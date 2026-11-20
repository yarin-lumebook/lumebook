#!/usr/bin/env python3
"""Instagram and Facebook stories for the content calendar (19 Nov 2026).

Yarin: "use my chatgpt through chrome to create a daily story series we can schedule in postiz ... add it to our content-calendar
with full story editing capabilities". The data lives next to the pictures in media/projects/2026-11-19-story-series/:

    series.json     the series (Black Friday, Hanukkah, reviews: dates, default hour, link) and the sets, one set = one day of one
                    series = a few frames; a frame is data (background picture, layers of text, pictures, shapes, sticker
                    placeholders), never a flat picture, so every word and every position stays editable
    art/            the backgrounds made in ChatGPT (Claude in Chrome); uploads/ what Yarin dropped in the editor
    frames/<set>/   the PNGs (1080 x 1920) drawn from the frames by the same renderer the editor uses (sites/content-calendar/
                    story-frame.js in headless Chrome), one file per frame id; what goes to Postiz

The calendar (tools/content_calendar.py) shows every set as a piece of kind "story" and sends its writes here through one endpoint,
POST /api/calendar/story {op: save|new|dup|delete|approve|unapprove|render|send}, same-origin only. Nothing is sent to Postiz
without confirmed:true, an approval of exactly this content, and fresh PNGs. Instagram stories take one picture per post and
Facebook publishes each picture as its own story, so a set is one Postiz post per frame, both channels in it.
Restart the project server after editing this file.

    python3 tools/stories.py status         # the sets, their approval and render state
    python3 tools/stories.py render KEY     # draw a set's PNGs now
"""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "sites" / "content-calendar"
DIR = Path(os.environ.get("LUMEBOOK_STORIES_DIR") or ROOT / "media" / "projects" / "2026-11-19-story-series")
DATA = DIR / "series.json"
RENDER_JS = SITE / "story-frame.js"
CHROME = os.environ.get("CHROME_PATH") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
RENDER_VERSION = 2            # 2: dates kept left to right (19 Nov 2026). Bump when story-frame.js changes how a frame looks, so every PNG is drawn again
W, H = 1080, 1920
GAP_SECONDS = 60              # frames of a set go out one minute apart, in order
MAX_FRAMES, MAX_LAYERS = 12, 24
UPLOAD_EXT = {".png", ".jpg", ".jpeg", ".webp"}
UPLOAD_MAX = 15 * 1024 * 1024

_lock = threading.RLock()
_render_lock = threading.Lock()


def rel(p):
    """A path as the project names it (relative to the project folder), or absolute when it is outside (a test server's scratch copy)."""
    p = Path(p).resolve()
    try:
        return str(p.relative_to(ROOT.resolve()))
    except ValueError:
        return str(p)


def cc():
    import content_calendar   # imported late: content_calendar imports this module
    return content_calendar


# ---------------------------------------------------------------- the data

def data():
    d = cc().read_json(DATA, None)
    if not isinstance(d, dict):
        d = {}
    d.setdefault("series", {})
    d.setdefault("sets", {})
    d.setdefault("removed", {})
    return d


def save(d):
    cc().write_json(DATA, d, indent=1)
    cc()._cache.pop("collect", None)


HEX = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")
KEY = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*-\d{4}-\d{2}-\d{2}(-[a-z0-9]+)?$")
ID = re.compile(r"^[\w\-]{1,24}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME = re.compile(r"^\d{2}:\d{2}$")
STICKERS = ("link", "poll", "question", "countdown", "mention", "emoji")


def _n(v, lo, hi, dflt):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return dflt
    if v != v:
        return dflt
    v = max(lo, min(hi, v))
    return int(v) if v == int(v) else round(v, 3)


def _color(v, dflt):
    return v if isinstance(v, str) and HEX.match(v) else dflt


def _text(v, limit):
    v = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", str(v or ""))
    return v[:limit]


def _src(v):
    """A picture inside the project's media or brand folders that exists; ValueError otherwise."""
    v = str(v or "")
    p = Path(v).resolve() if Path(v).is_absolute() else (ROOT / v).resolve()   # absolute only inside the folders below (a test copy)
    ok = [(ROOT / "media").resolve(), (ROOT / "shared" / "brand").resolve()] + ([DIR.resolve()] if DIR.exists() else [])
    if not v or ".." in Path(v).parts or p.suffix.lower() not in UPLOAD_EXT or not p.is_file() or not any(r in p.parents for r in ok):
        raise ValueError("תמונה לא נמצאה: " + v[:80])
    return rel(p)


def clean_layer(l, n):
    if not isinstance(l, dict):
        raise ValueError("שכבה לא תקינה")
    t = l.get("type")
    out = {"id": l.get("id") if isinstance(l.get("id"), str) and ID.match(l["id"]) else f"l{n}", "type": t,
           "x": _n(l.get("x"), -1080, 2160, 90), "y": _n(l.get("y"), -1920, 3840, 400), "w": _n(l.get("w"), 20, 2160, 900),
           "op": _n(l.get("op", 100), 0, 100, 100)}
    if l.get("rot"):
        out["rot"] = _n(l.get("rot"), -180, 180, 0)
    if isinstance(l.get("group"), str) and ID.match(l["group"]):
        out["group"] = l["group"]       # layers made together (a review's header, quote, screenshot, label) are replaced together
    if t == "text":
        out.update(text=_text(l.get("text"), 600), size=_n(l.get("size"), 16, 400, 80), weight=700 if str(l.get("weight")) == "700" else 900,
                   color=_color(l.get("color"), "#FFFFFF"), accent=_color(l.get("accent"), "#F5C26B"),
                   align=l.get("align") if l.get("align") in ("left", "center", "right") else "center",
                   lh=_n(l.get("lh"), .8, 2, 1.12), shadow=bool(l.get("shadow")), font="assistant" if l.get("font") == "assistant" else "heebo")
        if l.get("pill"):
            out.update(pill=_color(l.get("pill"), "#2B0E6E"), pad=_n(l.get("pad"), 0, 120, 28), pillr=_n(l.get("pillr"), 0, 200, 40))
    elif t == "image":
        out.update(src=_src(l.get("src")), radius=_n(l.get("radius"), 0, 400, 0), shadow=bool(l.get("shadow")))
        blurs = [b for b in (l.get("blurs") or []) if isinstance(b, dict)][:16]   # names and faces hidden on a screenshot, % of the picture
        if blurs:
            out["blurs"] = [{"x": _n(b.get("x"), 0, 100, 0), "y": _n(b.get("y"), 0, 100, 0), "w": _n(b.get("w"), .5, 100, 10), "h": _n(b.get("h"), .5, 100, 10)} for b in blurs]
            out["blur"] = _n(l.get("blur"), 4, 60, 16)
        if l.get("bg"):
            out["bg"] = _color(l.get("bg"), "#FFFFFF")
    elif t == "shape":
        out.update(h=_n(l.get("h"), 4, 3840, 200), fill=_color(l.get("fill"), "#FFFFFF"), radius=_n(l.get("radius"), 0, 800, 0))
        if l.get("border"):
            out.update(border=_color(l.get("border"), "#FFFFFF"), bw=_n(l.get("bw"), 1, 40, 4))
    elif t == "sticker":
        out.update(kind=l.get("kind") if l.get("kind") in STICKERS else "link", label=_text(l.get("label"), 80), h=_n(l.get("h"), 40, 800, 150),
                   url=_text(l.get("url"), 300))
    else:
        raise ValueError("סוג שכבה לא מוכר")
    return out


def clean_frame(f, n):
    if not isinstance(f, dict):
        raise ValueError("פריים לא תקין")
    bg = f.get("bg") if isinstance(f.get("bg"), dict) else {}
    nb = {"fill": _color(bg.get("fill"), "#2B0E6E")}
    if bg.get("src"):
        nb.update(src=_src(bg.get("src")), x=_n(bg.get("x"), 0, 100, 50), y=_n(bg.get("y"), 0, 100, 50), zoom=_n(bg.get("zoom"), 100, 300, 100))
    sc = f.get("scrim") if isinstance(f.get("scrim"), dict) else {}
    layers = f.get("layers") if isinstance(f.get("layers"), list) else []
    if len(layers) > MAX_LAYERS:
        raise ValueError(f"יותר מ־{MAX_LAYERS} שכבות בפריים")
    seen, out_layers = set(), []
    for i, l in enumerate(layers, 1):
        cl = clean_layer(l, i)
        while cl["id"] in seen:
            cl["id"] += "x"
        seen.add(cl["id"])
        out_layers.append(cl)
    return {"id": f.get("id") if isinstance(f.get("id"), str) and ID.match(f["id"]) else f"f{n}", "bg": nb,
            "scrim": {"top": _n(sc.get("top"), 0, 1, 0), "bottom": _n(sc.get("bottom"), 0, 1, 0)}, "layers": out_layers,
            "note": _text(f.get("note"), 300), "ask": _text(f.get("ask"), 500), "manual": bool(f.get("manual"))}


def clean_set(doc, old=None):
    """A set as the editor sends it, checked and cut to what is allowed. ValueError (Hebrew) when it cannot be saved."""
    d = data()
    old = old or {}
    ser = doc.get("series") or old.get("series")
    if ser not in d["series"]:
        raise ValueError("סדרה לא מוכרת")
    dt = doc.get("date") or old.get("date")
    tm = doc.get("time") or old.get("time") or d["series"][ser].get("time") or "17:00"
    if not DATE.match(str(dt or "")) or not TIME.match(str(tm)):
        raise ValueError("תאריך או שעה לא תקינים")
    frames = doc.get("frames") if isinstance(doc.get("frames"), list) else old.get("frames") or []
    if not 1 <= len(frames) <= MAX_FRAMES:
        raise ValueError(f"סט הוא בין 1 ל־{MAX_FRAMES} פריימים")
    fr, ids = [], set()
    for i, f in enumerate(frames, 1):
        cf = clean_frame(f, i)
        while cf["id"] in ids:
            cf["id"] += "x"
        ids.add(cf["id"])
        fr.append(cf)
    new = {"series": ser, "date": dt, "time": tm, "title": _text(doc.get("title", old.get("title", "")), 80), "frames": fr,
           "channels": [c for c in ("ig", "fb") if c in (doc.get("channels") or old.get("channels") or ["ig", "fb"])] or ["ig", "fb"],
           "notes": _text(doc.get("notes", old.get("notes", "")), 600)}
    # the set's song (Yarin, 20 Nov 2026: "add different music for each"): chosen from the reel music library and added in Instagram
    # with its music sticker, since the library's songs are commercial and a file there is not a licence (its README)
    mu = doc.get("music") if isinstance(doc.get("music"), dict) else old.get("music")
    if isinstance(mu, dict) and mu.get("title"):
        new["music"] = {"id": _text(mu.get("id", ""), 20), "title": _text(mu.get("title", ""), 120),
                        "start": _text(mu.get("start", ""), 8), "why": _text(mu.get("why", ""), 200)}
    for k in ("approved", "rendered", "postiz"):
        if old.get(k):
            new[k] = old[k]
    if new.get("approved") and new["approved"].get("hash") != content_hash(new):
        new.pop("approved")      # edited after the approval: the approval was for other content
    return new


def frame_hash(fr):
    body = {k: v for k, v in fr.items() if k not in ("note", "ask", "manual")}
    return hashlib.sha1((json.dumps(body, ensure_ascii=False, sort_keys=True) + f"|v{RENDER_VERSION}").encode("utf-8")).hexdigest()[:12]


def content_hash(s):
    """What an approval is for: every frame, in order (date and time may still move)."""
    return hashlib.sha1("|".join(frame_hash(f) for f in s.get("frames", [])).encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------- the copy rules (Yarin's, from the project's CLAUDE.md)

def lint(s, series_key):
    """Problems in a set's words: [{frame, layer, level, he}]. Errors are rules the project never breaks; warnings need a look."""
    out = []
    for i, f in enumerate(s.get("frames", []), 1):
        for l in f.get("layers", []):
            if l.get("type") != "text":
                continue
            t = l.get("text") or ""
            at = {"frame": i, "layer": l["id"]}
            if re.search(r"[—–]", t):
                out.append({**at, "level": "error", "he": "מקף ארוך בטקסט"})
            if "לומבוק" in t:
                out.append({**at, "level": "error", "he": "כותבים לומיבוק, לא לומבוק"})
            if "תצוגה מקדימה" in t or "תצוגה המקדימה" in t:   # Yarin, 20 Nov 2026: "its unnatural and people dont care about it"
                out.append({**at, "level": "error", "he": "בלי \"תצוגה מקדימה\": לדבר על כמה זה פשוט (בוחרים סיפור, מוסיפים תמונה, ובום, יש ספר)"})
            if "אמיתי" in t:     # Yarin, 20 Nov 2026: "dont write "ביקורת אמיתית" on the stories, it sounds sketchy"
                out.append({**at, "level": "error", "he": "בלי \"אמיתי\" על הסטורי: נשמע חשוד"})
            if re.search(r"(?<![א-ת])[בלהשמו]{0,2}ביו(?![א-ת])", t):   # Yarin, 20 Nov 2026: "instead of ביו write בפרופיל שלנו"
                out.append({**at, "level": "error", "he": "כותבים \"בפרופיל שלנו\", לא \"ביו\""})
            if re.search(r"\bAI\b|בינה מלאכותית", t, re.I):
                out.append({**at, "level": "error", "he": "בלי אזכור של בינה מלאכותית בטקסט לקהל"})
            if re.search(r"[־;]|\s-\s", t):
                out.append({**at, "level": "warn", "he": "מקף, מקף עליון או נקודה פסיק (הכלל: בלי)"})
            if series_key == "bf" and re.search(r"₪|\d\s?שקל|\b\d{2,3}\s?ש\"ח", t):
                out.append({**at, "level": "warn", "he": "מחיר בסטורי של בלאק פריידיי מחכה לאישור שלך"})
            if re.search(r"קוד הנחה|קוד אישי", t):
                out.append({**at, "level": "error", "he": "הכלל: קישור אישי עם הנחה לקהל, בלי \"קוד\""})
    return out


# ---------------------------------------------------------------- the PNGs (the editor's renderer in headless Chrome)

def _chrome_run(html_path, out, tries=2, scale=1):
    if not Path(CHROME).exists():
        raise RuntimeError("Google Chrome לא נמצא (CHROME_PATH)")
    for _ in range(tries):
        profile = tempfile.mkdtemp(prefix="lumebook-story-")
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio", "--no-first-run", f"--user-data-dir={profile}",
               f"--force-device-scale-factor={scale}", "--allow-file-access-from-files", "--virtual-time-budget=9000",
               f"--window-size={W},{H}", f"--screenshot={out}", Path(html_path).as_uri()]
        if out.exists():
            out.unlink()
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _i in range(200):    # Chrome sometimes writes the PNG and never exits (as compose_slides.py found)
            time.sleep(0.25)
            if proc.poll() is not None or (out.exists() and out.stat().st_size > 0):
                time.sleep(0.4)
                break
        if proc.poll() is None:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
        if out.exists() and out.stat().st_size > 0:
            return out
    raise RuntimeError(f"Chrome לא יצר את {out.name}")


def png_size(path):
    with open(path, "rb") as f:
        h = f.read(24)
    return (int.from_bytes(h[16:20], "big"), int.from_bytes(h[20:24], "big")) if h[:8] == b"\x89PNG\r\n\x1a\n" else (0, 0)


def export_html(fr):
    js = RENDER_JS.read_text(encoding="utf-8")
    blob = json.dumps(fr, ensure_ascii=False).replace("</", "<\\/")
    base = json.dumps(ROOT.resolve().as_uri() + "/")
    return ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>html,body{margin:0;background:#000;overflow:hidden}</style></head><body>'
            '<div id="r"></div><script>' + js.replace("</", "<\\/") + '</script><script>var FR=' + blob + ',B=' + base + ';'
            'var s=document.createElement("style");s.textContent=LBStory.css(B);document.head.appendChild(s);'
            'document.getElementById("r").innerHTML=LBStory.frameHtml(FR,{base:B,editor:false});</script></body></html>')


def render_set(key, force=False):
    """Draw the PNGs of a set that are missing or out of date (a frame's hash decides). Returns (status, body)."""
    with _render_lock:
        d = data()
        s = d["sets"].get(key)
        if not s:
            return 404, {"error": "no such set"}
        out_dir = DIR / "frames" / key
        out_dir.mkdir(parents=True, exist_ok=True)
        done = dict((s.get("rendered") or {}).get("frames") or {})
        drawn = 0
        try:
            for fr in s["frames"]:
                h = frame_hash(fr)
                png = out_dir / f"{fr['id']}.png"
                if not force and png.exists() and done.get(fr["id"]) == h:
                    continue
                with tempfile.TemporaryDirectory(prefix="lumebook-storyhtml-") as tmp:
                    page = Path(tmp) / "frame.html"
                    page.write_text(export_html(fr), encoding="utf-8")
                    _chrome_run(page, png)
                if png_size(png) != (W, H):
                    raise RuntimeError(f"{png.name}: הגודל {png_size(png)} במקום {W}x{H}")
                done[fr["id"]] = h
                drawn += 1
                if fr is s["frames"][0] or not (out_dir / "thumb.png").exists():
                    with tempfile.TemporaryDirectory(prefix="lumebook-storyhtml-") as tmp:   # the calendar's small picture of the set
                        page = Path(tmp) / "frame.html"
                        page.write_text(export_html(s["frames"][0]), encoding="utf-8")
                        _chrome_run(page, out_dir / "thumb.png", scale=0.2)
        except (RuntimeError, OSError) as exc:
            return 500, {"error": str(exc), "he": str(exc)}
        s["rendered"] = {"at": cc().now().isoformat(timespec="seconds"), "frames": {f["id"]: done[f["id"]] for f in s["frames"] if f["id"] in done}}
        d["sets"][key] = s
        with _lock:
            save(d)
        return 200, {"ok": True, "drawn": drawn, "files": [rel(out_dir / f"{f['id']}.png") for f in s["frames"]]}


def fresh(key, s):
    """True when every frame has a PNG drawn from exactly its current content."""
    done = (s.get("rendered") or {}).get("frames") or {}
    return bool(s.get("frames")) and all(done.get(f["id"]) == frame_hash(f) and (DIR / "frames" / key / f"{f['id']}.png").exists() for f in s["frames"])


# ---------------------------------------------------------------- the calendar's pieces

def series_days(d, ser_key):
    ser = d["series"].get(ser_key) or {}
    try:
        a, b = date.fromisoformat(ser["start"]), date.fromisoformat(ser["end"])
    except (KeyError, ValueError):
        return None, None
    return a, (b - a).days + 1


def pieces(month, st):
    """Every story set of the month as a calendar piece (kind "story"): one set is one day of one series."""
    c = cc()
    d = data()
    out = []
    for key, s in d["sets"].items():
        if not str(s.get("date", "")).startswith(month):
            continue
        ser = d["series"].get(s["series"], {})
        a, total = series_days(d, s["series"])
        day = (date.fromisoformat(s["date"]) - a).days + 1 if a else None
        flags = []
        needs = []
        pz = None
        status = "approve"
        problems = lint(s, s["series"])
        approved = bool(s.get("approved")) and s["approved"].get("hash") == content_hash(s)
        sent = s.get("postiz") or {}
        if sent.get("ids"):
            pz = c.refine({"date": sent.get("date"), "status": sent.get("status") or "schedule", "sent_at": sent.get("sent_at")}, list(sent["ids"]), c._LIVE["data"])
            ps = pz.get("status")
            if ps == "published":
                status = "posted"
            elif ps == "error":
                status = "scheduled"
                flags.append({"code": "pz_error", "he": "פוסטיז דיווח על שגיאה בפרסום"})
            elif ps in ("schedule", None):
                try:
                    past = datetime.fromisoformat(str(pz["date"]).replace("Z", "+00:00")) <= c.now()
                except (ValueError, TypeError):
                    past = False
                status = "posted" if past and not pz.get("live") else "scheduled"
            else:
                status = "ready"
                flags.append({"code": "pz_" + ps, "he": "בפוסטיז: " + {"gone": "לא נמצא (נמחק שם)", "draft": "טיוטה"}.get(ps, ps)})
            n_sent, n_auto = len(sent.get("frames") or {}), len([f for f in s["frames"] if not f.get("manual")])
            if n_sent < n_auto:
                flags.append({"code": "partial", "he": f"נשלחו {n_sent} מתוך {n_auto} פריימים לפוסטיז"})
        elif approved:
            status = "ready"
        else:
            needs = ["approve"]
        if any(f.get("ask") for f in s["frames"]) and status in ("approve", "ready") and not sent.get("ids"):
            flags.append({"code": "art", "he": "יש בקשה לתמונה חדשה שמחכה לתיקון"})
        for p_ in problems:
            if p_["level"] == "error":
                flags.append({"code": "lint", "he": f"פריים {p_['frame']}: {p_['he']}"})
        n_manual = len([f for f in s["frames"] if f.get("manual")])
        if n_manual:
            flags.append({"code": "manual", "he": f"{n_manual} פריימים עולים ידנית מהטלפון (בשביל מדבקה)"})
        if not sent.get("ids") and s["date"] < c.today():
            flags.append({"code": "past", "he": "התאריך כבר עבר"})
        if not sent.get("ids") and not fresh(key, s):
            flags.append({"code": "stale", "he": "התמונות לא מעודכנות: ליצור מחדש לפני התזמון"})
        first = DIR / "frames" / key / f"{s['frames'][0]['id']}.png" if s["frames"] else None
        small = DIR / "frames" / key / "thumb.png"
        ok1 = first and first.exists() and (s.get("rendered") or {}).get("frames", {}).get(s["frames"][0]["id"]) == frame_hash(s["frames"][0])
        thumb = (c.url_of(small) if small.exists() and small.stat().st_mtime >= first.stat().st_mtime - 5 else c.url_of(first)) if ok1 else None
        out.append({"id": "st-" + key, "kind": "story", "subtype": s["series"], "subtype_he": ser.get("name", s["series"]), "date": s["date"],
                    "time": s["time"], "channels": s.get("channels") or ["ig", "fb"],
                    "title": (s.get("title") or ser.get("name", "")) + (f" · יום {day} מתוך {total}" if day and total and 1 <= day <= total else ""),
                    "options": [], "picked": None, "status": status, "flags": flags, "needs": needs, "actions": [], "thumb": thumb,
                    "postiz": pz, "moved": False, "source": {"file": str(DATA.relative_to(ROOT)) if DATA.is_relative_to(ROOT) else "series.json", "key": key},
                    "detail": {"key": key, "set": s, "series": ser, "day": day, "days": total,
                               "approved": approved, "fresh": fresh(key, s), "lint": problems, "sent": sent,
                               "png": [c.url_of(DIR / "frames" / key / f"{f['id']}.png") if (DIR / "frames" / key / f"{f['id']}.png").exists() else None for f in s["frames"]],
                               "base": "/", "dir": str(DIR.relative_to(ROOT)) if DIR.is_relative_to(ROOT) else ""}})
    return out


def library():
    """What the editor offers once per month response: the series and the pictures to pick a background from."""
    d = data()
    art = []
    for folder, label in ((DIR / "art", "תמונות הסדרה"), (DIR / "uploads", "הועלו"), (ROOT / "shared" / "brand" / "social-backgrounds", "רקעים של המותג")):
        if folder.is_dir():
            for p in sorted(folder.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
                if p.suffix.lower() in UPLOAD_EXT and p.is_file():
                    art.append({"src": rel(p), "name": p.stem, "group": label})
    return {"series": d["series"], "art": art, "canvas": {"w": W, "h": H}}


def reviews():
    """The social proof page's reviews as pictures to put on a frame (read only; cards Yarin removed there are left out)."""
    base = ROOT / "media" / "projects" / "2026-11-15-social-proof"
    dj = cc().read_json(base / "data.json", {}) or {}
    removed = set((cc().read_json(base / "removed.json", {}) or {}).get("removed") or [])
    out = []
    for r in dj.get("reviews", []):
        if ("review:" + str(r.get("id"))) in removed or not r.get("file") or not (base / r["file"]).is_file():
            continue
        if r.get("platform") == "whatsapp" or r.get("kind") == "caption" or "@" in (r.get("text") or ""):
            continue    # private chats, our own captions, and words that tag someone else (a name the blur would miss)
        w, h = png_size(base / r["file"])
        out.append({"id": r["id"], "src": str((base / r["file"]).relative_to(ROOT)), "platform": r.get("platform"), "kind": r.get("kind"),
                    "author": r.get("author"), "stars": r.get("stars"), "text": r.get("text"), "intent": r.get("intent"), "themes": r.get("themes") or [],
                    "w": w, "h": h})
    return out


# ---------------------------------------------------------------- review frames: the real screenshots, names and faces blurred
# Yarin, 19 Nov 2026: "use the real comments and reviews screenshots just blur the names". The blur boxes belong to the picture layer
# (story-frame.js draws them into the PNG) and move in the editor. A Google screenshot gets a large pull quote of its own words above it:
# its text is about 22 pixels on a 1140 pixel image, too small to read in a story; Instagram comments are large enough on their own.

PROOF = ROOT / "media" / "projects" / "2026-11-15-social-proof"
FIND_NAMES = DIR / "find_names.swift"
PLATFORM_HE = {"google": "ביקורת בגוגל", "instagram": "תגובה באינסטגרם", "facebook": "תגובה בפייסבוק"}   # never "אמיתית" (Yarin, 20 Nov 2026: "it sounds sketchy")
GOLD = "#F5C26B"


def find_names(paths):
    """Text lines of screenshots with their boxes (find_names.swift, macOS Vision; Latin only, so it finds Instagram usernames)."""
    exe = Path(tempfile.gettempdir()) / "lumebook-find-names"
    if not exe.exists() or exe.stat().st_mtime < FIND_NAMES.stat().st_mtime:
        subprocess.run(["swiftc", "-O", str(FIND_NAMES), "-o", str(exe)], check=True, capture_output=True, timeout=300)
    out = subprocess.run([str(exe), *map(str, paths)], check=True, capture_output=True, text=True, timeout=120).stdout
    return {Path(x["file"]).name: x for x in json.loads(out)}


def blur_boxes(rv, found=None):
    """Boxes (% of the picture) over the name and the profile picture of one screenshot, and how they were found."""
    path = PROOF / rv["file"]
    w, h = png_size(path)

    def pct(x0, y0, x1, y1):
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
        return {"x": round(x0 / w * 100, 2), "y": round(y0 / h * 100, 2), "w": round((x1 - x0) / w * 100, 2), "h": round((y1 - y0) / h * 100, 2)}
    if rv.get("platform") == "google":   # the same on every Google screenshot: photo and name at the top right, the review count under it
        return [pct(w * 0.45, 8, w, min(106, h * 0.34))], "google: the header strip"
    if rv.get("platform") == "instagram":
        if found is None:
            try:
                found = find_names([path])
            except (OSError, subprocess.SubprocessError, ValueError):
                found = {}
        ls = sorted((found.get(path.name) or {}).get("lines") or [], key=lambda l: l["y"])
        # the username starts at the left, right after the photo (20 Nov 2026: a "1w" further right was taken for it once)
        u = next((l for l in ls if re.match(r"^[A-Za-z0-9._]{3,}", l["t"]) and l["x"] < w * 0.3 and not re.match(r"^\d+[wdh]$", l["t"].strip())), None)
        if u:   # the username line, and the round profile picture left of it (about twice the line's height)
            return [pct(u["x"] - 10, u["y"] - 8, u["x"] + u["w"] + 12, u["y"] + u["h"] + 8),
                    pct(u["x"] - 3.1 * u["h"], u["y"] - 0.5 * u["h"], u["x"] - 0.1 * u["h"], u["y"] + 2.0 * u["h"])], "instagram: the username line and the photo"
        return [pct(0, 0, w * 0.75, h * 0.3)], "instagram: no username found, the top strip"
    return [pct(0, 0, w, h * 0.3)], "the top strip"


def review_layers(rv, parts=None, cta=False, found=None):
    """The layers of one review frame: header, (Google: stars and a pull quote), the screenshot with its blurs, the platform label.
    parts are word for word pieces of the review joined by an ellipsis (None: the whole text for Google, nothing for comments).
    Returns (layers, note). All layers are in the group "review", so the editor replaces them together."""
    google = rv.get("platform") == "google"
    if google and parts is None:
        parts = [rv.get("text", "").strip()]
    for p in parts or []:
        if p.strip("… ") not in rv.get("text", ""):
            raise ValueError(f"not word for word in {rv['id']}: {p[:40]}")
    sw, sh = png_size(PROOF / rv["file"])
    W = 1040 if google else 1000
    img_h = sh * W / sw if sw else 400
    qsize = 62
    q = ('"' + " … ".join(parts) + '"') if (google and parts) else ""
    q_h = sum(max(1, -(-len(ln) // int(920 / (qsize * 0.52)))) for ln in q.split("\n")) * qsize * 1.15 if q else 0
    block = 100 + (120 if google else 0) + (q_h + 44 if q else 0) + img_h + 30 + 50
    bottom = 1260 if cta else 1560
    y = max(280, int((280 + bottom) / 2 - block / 2))
    t = lambda i, txt, yy, **kw: {"id": i, "type": "text", "text": txt, "x": 90, "y": int(yy), "w": 900, "size": 72, "weight": 900, "color": "#FFFFFF",
                                  "align": "center", "lh": 1.1, "shadow": True, "group": "review", **kw}
    layers = [t("r1", "מה אומרים עלינו", y)]
    y += 100
    if google:
        layers.append(t("r2", "★" * int(rv.get("stars") or 5), y, size=90, color=GOLD, shadow=False))
        y += 120
    if q:
        layers.append(t("r3", q, y, size=qsize, lh=1.15))
        y += q_h + 44
    boxes, how = blur_boxes(rv, found)
    layers.append({"id": "r4", "type": "image", "src": str((PROOF / rv["file"]).relative_to(ROOT)), "x": (1080 - W) // 2, "y": int(y), "w": W,
                   "radius": 28, "shadow": True, "bg": "#FFFFFF", "blurs": boxes, "blur": 18, "group": "review"})
    y += img_h + 30
    layers.append(t("r5", PLATFORM_HE.get(rv.get("platform"), ""), y, size=42, weight=700, color=GOLD))
    note = f"ביקורת {rv['id']}: {rv.get('platform')}. השם והתמונה מטושטשים ({how}). צילום המסך: {PROOF.relative_to(ROOT)}/{rv['file']}"
    return layers, note


def review_by_id(rid):
    for r in (cc().read_json(PROOF / "data.json", {}) or {}).get("reviews", []):
        if r.get("id") == rid:
            return r
    return None


# ---------------------------------------------------------------- writes

def new_set(series, dt):
    d = data()
    if series not in d["series"] or not DATE.match(dt or ""):
        return 400, {"error": "bad request"}
    key = f"{series}-{dt}"
    if key in d["sets"]:
        return 409, {"error": "exists", "he": "יש כבר סט של הסדרה הזאת ביום הזה"}
    d["sets"][key] = {"series": series, "date": dt, "time": d["series"][series].get("time") or "17:00", "title": "", "channels": ["ig", "fb"], "notes": "",
                      "frames": [clean_frame({"id": "f1", "bg": {"fill": "#2B0E6E"}, "layers": []}, 1)]}
    with _lock:
        save(d)
    return 200, {"ok": True, "key": key}


def put_set(key, doc):
    if not KEY.match(key or ""):
        return 400, {"error": "bad key"}
    with _lock:
        d = data()
        old = d["sets"].get(key)
        if not old:
            return 404, {"error": "no such set"}
        if (old.get("postiz") or {}).get("ids") and _content_changed(old, doc):
            return 409, {"error": "sent", "he": "הסט כבר בפוסטיז: שינוי תוכן כאן לא ישנה את מה שנשלח. שנו בפוסטיז או שכפלו ליום אחר"}
        try:
            d["sets"][key] = clean_set(doc, old)
        except ValueError as exc:
            return 400, {"error": str(exc), "he": str(exc)}
        save(d)
    return 200, {"ok": True, "approved": bool(d["sets"][key].get("approved"))}


def _content_changed(old, doc):
    if not isinstance(doc.get("frames"), list):
        return False
    try:
        new = clean_set(doc, old)
    except ValueError:
        return True
    return content_hash(new) != content_hash(old)


def dup_set(key, to_date, series=None):
    with _lock:
        d = data()
        s = d["sets"].get(key)
        if not s or not DATE.match(to_date or ""):
            return 400, {"error": "bad request"}
        ser = series or s["series"]
        nk = f"{ser}-{to_date}"
        if nk in d["sets"]:
            return 409, {"error": "exists", "he": "יש כבר סט של הסדרה הזאת ביום הזה"}
        c = json.loads(json.dumps(s))
        for k in ("approved", "rendered", "postiz"):
            c.pop(k, None)
        c["date"], c["series"] = to_date, ser
        d["sets"][nk] = c
        save(d)
    return 200, {"ok": True, "key": nk}


def delete_set(key):
    """Never destroys: the set moves to "removed" in series.json (its PNGs stay in frames/)."""
    with _lock:
        d = data()
        s = d["sets"].get(key)
        if not s:
            return 404, {"error": "no such set"}
        if (s.get("postiz") or {}).get("ids"):
            return 409, {"error": "sent", "he": "הסט נשלח לפוסטיז. מוחקים אותו שם"}
        d["removed"][key + "@" + cc().now().strftime("%Y%m%d%H%M%S")] = s
        d["sets"].pop(key)
        save(d)
    return 200, {"ok": True}


def approve(key, on):
    with _lock:
        d = data()
        s = d["sets"].get(key)
        if not s:
            return 404, {"error": "no such set"}
        if on:
            bad = [p for p in lint(s, s["series"]) if p["level"] == "error"]
            if bad:
                return 409, {"error": "lint", "he": f"פריים {bad[0]['frame']}: {bad[0]['he']}"}
            s["approved"] = {"at": cc().now().isoformat(timespec="seconds"), "hash": content_hash(s)}
        else:
            s.pop("approved", None)
        save(d)
    return 200, {"ok": True}


def move(piece_id, to_date, to_time="keep"):
    key = piece_id[3:]
    if not DATE.match(to_date or "") or (to_time not in (None, "keep") and not TIME.match(str(to_time))):
        return 400, {"error": "bad date or time"}
    with _lock:
        d = data()
        s = d["sets"].get(key)
        if not s:
            return 404, {"error": "no such set"}
        if (s.get("postiz") or {}).get("ids"):
            return 409, {"error": "in_postiz", "he": "מתוזמן בפוסטיז: לשנות שם?"}
        nk = f"{s['series']}-{to_date}"
        if nk != key and nk in d["sets"]:
            return 409, {"error": "exists", "he": "יש כבר סט של הסדרה הזאת ביום הזה"}
        old = {"date": s["date"], "time": s["time"]}
        s["date"] = to_date
        if to_time == "keep":
            pass
        elif to_time is None:
            s["time"] = (d["series"].get(s["series"]) or {}).get("time") or s["time"]
        else:
            s["time"] = to_time
        if nk != key:
            d["sets"][nk] = d["sets"].pop(key)
            fr = DIR / "frames" / key
            if fr.is_dir() and not (DIR / "frames" / nk).exists():
                fr.rename(DIR / "frames" / nk)     # the PNGs follow the key; nothing is lost
        save(d)
    return 200, {"ok": True, "undo": {"id": "st-" + (nk if nk != key else key), **old}, "id": "st-" + nk}


def upload(name, body):
    base, ext = os.path.splitext(os.path.basename(name or ""))
    if ext.lower() not in UPLOAD_EXT:
        return 415, {"error": "png, jpg or webp"}
    if not body or len(body) > UPLOAD_MAX:
        return 413, {"error": "too big"}
    (DIR / "uploads").mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w.\-]+", "-", base).strip("-.")[:60] or "picture"
    p = DIR / "uploads" / f"{cc().now().strftime('%Y%m%d-%H%M%S')}-{safe}{ext.lower()}"
    p.write_bytes(body)
    return 200, {"ok": True, "src": rel(p)}


# ---------------------------------------------------------------- Postiz (Yarin's click only)

def frame_label(fr):
    for l in fr.get("layers", []):
        if l.get("type") == "text" and (l.get("text") or "").strip():
            return re.sub(r"\*\*|\n", " ", l["text"]).strip()[:100]
    return "סטורי"


def send(key, date_s, time_s, draft=False, confirmed=False):
    """A set to Postiz as stories: one post per frame (Instagram takes one picture per story post, Facebook publishes every picture as
    its own story), both channels in each post, one minute apart in the order of the frames. Only after Yarin approved exactly this
    content and the PNGs match it. Frames already sent are skipped, so a failure midway can be finished; a set that is all sent is
    refused (a second send would make second posts). Returns (status, body)."""
    c = cc()
    if confirmed is not True:
        return 400, {"error": "confirmation needed", "he": "צריך לאשר את השליחה"}
    ig, fb = c.pz_config()
    if not ig or not fb:
        return 500, {"error": "no Postiz channels in shared/facts.json"}
    d = data()
    s = d["sets"].get(key)
    if not s:
        return 404, {"error": "no such set"}
    if not s.get("approved") or s["approved"].get("hash") != content_hash(s):
        return 409, {"error": "approve first", "he": "קודם לאשר את הסט (האישור נמחק כשמשנים תוכן)"}
    bad = [p for p in lint(s, s["series"]) if p["level"] == "error"]
    if bad:
        return 409, {"error": "lint", "he": f"פריים {bad[0]['frame']}: {bad[0]['he']}"}
    rec = s.get("postiz") or {}
    sent = rec.get("frames") or {}
    todo = [f for f in s["frames"] if f["id"] not in sent and not f.get("manual")]
    if not todo:
        return 409, {"error": "already sent", "he": "כל הפריימים כבר בפוסטיז (או מסומנים להעלאה ידנית). שינוי שם רק באישור שלך"}
    try:
        base = c._when(date_s, time_s, draft)
    except ValueError as exc:
        return 400, {"error": str(exc), "he": str(exc)}
    code, body = render_set(key)
    if code != 200:
        return code, body
    d = data()
    s = d["sets"][key]
    post_type = "draft" if draft else "schedule"
    chans = [(ig, "instagram"), (fb, "facebook")]
    chans = [x for x in chans if {"instagram": "ig", "facebook": "fb"}[x[1]] in (s.get("channels") or ["ig", "fb"])]
    rec = s.get("postiz") or {"ids": [], "frames": {}, "date": base.isoformat(), "status": post_type}
    n = 0
    try:
        for idx, fr in enumerate(s["frames"]):
            if fr["id"] in rec["frames"] or fr.get("manual"):
                continue
            when = base + timedelta(seconds=GAP_SECONDS * idx)
            url = c.pz_upload(DIR / "frames" / key / f"{fr['id']}.png")
            posts = [{"integration": {"id": ch}, "value": [{"content": frame_label(fr), "image": [{"id": "s" + fr["id"], "path": url}]}],
                      "settings": {"__type": prov, "post_type": "story"}} for ch, prov in chans]
            req = {"type": post_type, "date": when.isoformat(), "shortLink": False, "tags": [], "posts": posts}
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump(req, f, ensure_ascii=False)
            try:
                res = c.pz_cli("posts:create", "--json", f.name)
            finally:
                os.unlink(f.name)
            ids = [x.get("postId") for x in (res if isinstance(res, list) else [res]) if isinstance(x, dict) and x.get("postId")]
            rec["frames"][fr["id"]] = {"ids": ids, "date": when.isoformat(), "media": url}
            rec["ids"] = [i for v in rec["frames"].values() for i in v["ids"]]
            rec["sent_at"] = c.now().isoformat(timespec="seconds")
            rec["status"] = post_type
            d["sets"][key]["postiz"] = rec
            with _lock:
                save(d)     # kept after each frame: a failure midway loses none
            n += 1
    except RuntimeError as exc:
        return 502, {"error": str(exc), "he": str(exc), "sent": n}
    c._cache.pop("collect", None)
    c._LIVE["data"] = None
    c._pz_live.clear()
    return 200, {"sent": n}


# ---------------------------------------------------------------- the one endpoint

def handle(doc):
    op = doc.get("op")
    key = str(doc.get("key") or "")
    if op == "save":
        return put_set(key, doc.get("set") or {})
    if op == "new":
        return new_set(str(doc.get("series") or ""), str(doc.get("date") or ""))
    if op == "dup":
        return dup_set(key, str(doc.get("date") or ""), doc.get("series"))
    if op == "delete":
        return delete_set(key)
    if op in ("approve", "unapprove"):
        return approve(key, op == "approve")
    if op == "review-layers":   # the editor's review picker: a review frame's layers for one review (blur boxes found on the server)
        rv = review_by_id(str(doc.get("review") or ""))
        if not rv:
            return 404, {"error": "no such review"}
        try:
            layers, note = review_layers(rv, None, bool(doc.get("cta")))
        except (ValueError, OSError) as exc:
            return 400, {"error": str(exc), "he": str(exc)}
        return 200, {"layers": layers, "note": note}
    if op == "render":
        return render_set(key, bool(doc.get("force")))
    if op == "send":
        return send(key, str(doc.get("date") or ""), str(doc.get("time") or ""), bool(doc.get("draft")), doc.get("confirmed"))
    return 404, {"error": "unknown story action"}


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    a = sys.argv[1:]
    if a[:1] == ["status"]:
        d = data()
        for k, s in d["sets"].items():
            print(k, s["date"], s["time"], f"{len(s['frames'])} frames", "approved" if s.get("approved") else "-", "fresh" if fresh(k, s) else "stale",
                  "sent" if (s.get("postiz") or {}).get("ids") else "")
        return 0
    if a[:1] == ["render"] and len(a) > 1:
        code, body = render_set(a[1], force="--force" in a)
        print(code, json.dumps(body, ensure_ascii=False))
        return 0 if code == 200 else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
