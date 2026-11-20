"""The Black Friday and Hanukkah carousels in the content calendar, with their editor (20 Nov 2026).

Yarin, 20 Nov 2026: "create 2 options for each for everyday of uploading / i want full editing capabilities".
The pieces live in carousel/carousel-pipeline/seasonal/2026-bf-hanukkah/ (README there; renderer and lint in
carousel/carousel-pipeline/scripts/seasonal_batch.py). Every posting day is one calendar piece of kind "season"
(`se-<bf|hn>-<date>`) with two options, a and b; each option is a carousel or a single picture.

The editor (sites/content-calendar/season.js) edits the option's JSON as a whole: every field of every slide, the layout,
the pictures and their position, slides added, copied, moved and removed, the format, the addressee, the caption, the CTA,
the Facebook text, the comment word and the links. It saves by itself (op save, a backup in versions/KEY/ at most every 10
minutes, Yarin's text changes logged to the voice skill's edits.jsonl once a field rests for 90 seconds), previews with the same
renderer as the PNGs (op preview), lints on every change, draws the PNGs on request (op render) and keeps the day's pick and
approval in state.json beside the carousels. Nothing here talks to Postiz: scheduling waits for Yarin.

    POST /api/calendar/season {op: save|preview|render|pick|approve|unapprove|reset, ...}   (tools/lumebook.py, same-origin)

Test on a spare port with LUMEBOOK_SEASONAL_DIR at a scratch copy of the seasonal folder.
"""

import copy
import hashlib
import json
import os
import re
import shutil
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "carousel" / "carousel-pipeline" / "scripts"))
import seasonal_batch as sb  # noqa: E402
import test_batch as tb  # noqa: E402
import carousel_lib as lib  # noqa: E402

if os.environ.get("LUMEBOOK_SEASONAL_DIR"):
    _h = Path(os.environ["LUMEBOOK_SEASONAL_DIR"]).resolve()
    sb.HOME = tb.HOME = _h
    tb.CARS, tb.SLIDES, tb.RUNS, tb.VERSIONS = _h / "carousels", _h / "slides", _h / "runs", _h / "versions"


def home():
    return tb.HOME


STATE = lambda: home() / "state.json"  # noqa: E731
SERIES = {"bf": {"he": "בלאק פריידיי", "type": "bf"}, "hn": {"he": "חנוכה", "type": "hanukkah"}}
KEY = re.compile(r"^(bf|hn)-(\d{4}-\d{2}-\d{2})-([ab])$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME = re.compile(r"^\d{2}:\d{2}$")
LAYOUTS = ("cover", "point", "quote", "covers", "cta", "offer")
# the offer post's book model and design (Yarin, 20 Nov 2026: "design each one differently, but not drastically ... using different book models")
BOOK_MODELS = ("real-cover", "real-cover-2", "real-flat", "real-stack", "real-open", "real-standing", "real-standing-2")
STYLES = ("s1", "s2", "s3", "s4", "s5", "s6", "s7")
SLIDE_TEXT = ("label", "headline", "body", "quote", "by", "no", "yes", "p1", "p2", "page", "badge")   # page: the open book's right page
SLIDE_KEYS = SLIDE_TEXT + ("layout", "bg", "pos", "text_at", "pics", "covers", "cover", "num", "quote_from")
TOP_TEXT = ("title", "caption", "cta", "fb_text", "comment_word", "angle_he")
TOP_KEYS = TOP_TEXT + ("format", "addressee", "emoji", "book", "links", "_note", "style")
ADDRESSEE_HE = {"grandma": "לסבתא", "mom": "לאמא", "parents": "להורים"}
MAX_TEXT = 4000

_lock = threading.RLock()
_renders = {}      # key -> {"status": "running"|"done"|"failed", "problems": [...], "at": ts}
_pending = {}      # (key, path) -> {"before", "after", "at", "car_date", "type", "addressee"}: voice edits waiting to rest
_lint_cache = {}   # key -> (mtime, issues)


def cc():
    import content_calendar   # imported late: content_calendar imports this module
    return content_calendar


def read_state():
    try:
        d = json.loads(STATE().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    for k in ("picks", "approved", "rendered", "moves"):
        d.setdefault(k, {})
    return d


def write_state(d):
    tmp = STATE().with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(STATE())


def keys():
    return sorted(p.stem for p in tb.CARS.glob("*.json") if KEY.match(p.stem))


def day_of(key):
    m = KEY.match(key)
    return m.group(1), m.group(2), m.group(3)


def slide_hash(car):
    """What the PNGs are drawn from: the slides, the look and the comment word (it is drawn on the CTA)."""
    blob = json.dumps([car.get("slides"), car.get("type"), car.get("format"), car.get("comment_word"), car.get("pictures")], ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


def content_hash(car):
    blob = json.dumps({k: v for k, v in car.items() if not k.startswith("_")}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


def issues_of(car, key):
    try:
        out = sb.lint_car(copy.deepcopy(car), key)
    except Exception as exc:  # noqa: BLE001 - a half-typed carousel must not break the page
        return [{"level": "ERROR", "slide": None, "message": f"הבדיקה נכשלה: {exc}"}]
    return [{"level": i.level, "slide": tb._slide_no(i.path), "message": i.message} for i in out]


def lint_key(key):
    p = tb.CARS / f"{key}.json"
    m = p.stat().st_mtime
    hit = _lint_cache.get(key)
    if hit and hit[0] == m:
        return hit[1]
    res = issues_of(tb.read(p), key)
    _lint_cache[key] = (m, res)
    return res


# ---------------------------------------------------------------- the picture library for the editor

def library():
    """Every real picture the batch may use, for the editor's picker: key, address, what it shows, kind, who."""
    c = cc()
    out = []
    for k, a in sorted(tb.assets().items()):
        url = c.url_of(ROOT / a["file"])
        if not url:
            continue
        out.append({"k": k, "url": url, "what": a.get("what_he", ""), "kind": a.get("kind", ""), "who": a.get("who_he", ""),
                    "gender": a.get("gender", ""), "pos": a.get("position", "50% 40%"), "cover": k.startswith("cover-")})
    return out


# ---------------------------------------------------------------- the calendar's pieces

def option_item(key, st):
    c = cc()
    car = tb.read(tb.CARS / f"{key}.json")
    sdir = tb.SLIDES / key
    n = len(car.get("slides") or [])
    imgs = []
    for i in range(1, n + 1):
        p = sdir / f"{i:02d}.png"
        if p.exists():
            u = c.url_of(p)
            if u:
                imgs.append(u)
    jm = (tb.CARS / f"{key}.json").stat().st_mtime
    if key in st["rendered"]:
        fresh = st["rendered"][key] == slide_hash(car) and len(imgs) == n
    else:   # drawn from the command line (seasonal_batch.py render): fresh when every PNG is newer than the file
        fresh = len(imgs) == n and all((sdir / f"{i:02d}.png").stat().st_mtime >= jm - 1 for i in range(1, n + 1))
    rep = tb.read(sdir / "render-report.json") if (sdir / "render-report.json").exists() else {}
    r = _renders.get(key) or {}
    return {"key": key, "car": car, "images": imgs, "fresh": fresh, "issues": lint_key(key),
            "render": {"status": r.get("status") or ("done" if imgs else None), "problems": (r.get("problems") if r else None) or rep.get("problems") or []},
            "approved": st["approved"].get(key) == content_hash(car)}


def pieces(month, st_cal=None):
    c = cc()
    st = read_state()
    days = {}
    for k in keys():
        ser, d, o = day_of(k)
        days.setdefault((ser, d), []).append(k)
    out = []
    for (ser, d), ks in sorted(days.items(), key=lambda x: x[0][1]):
        pid = f"se-{ser}-{d}"
        mv = st["moves"].get(pid) or {}
        date_ = mv.get("date") or d
        if not date_.startswith(month):
            continue
        time_ = mv.get("time") or c.plan_time(date_, "test") or "09:30"
        items = [option_item(k, st) for k in sorted(ks)]
        picked = st["picks"].get(pid)
        if picked not in ks:
            picked = None
        pit = next((i for i in items if i["key"] == picked), None)
        flags, needs = [], []
        if not picked:
            status = "pick"
            needs = ["pick"]
        elif any(x["level"] == "ERROR" for x in pit["issues"]):
            status = "draft"
            flags.append({"code": "lint", "he": "באפשרות שנבחרה יש מה לתקן בטקסט"})
        elif pit["approved"] and pit["fresh"]:
            status = "ready"
        else:
            status = "approve"
            needs = ["approve"]
        if pit and not pit["fresh"]:
            flags.append({"code": "stale", "he": "התמונות לא מעודכנות לטקסט: ליצור מחדש"})
        if pit and (pit["car"].get("_note") or "").strip():
            flags.append({"code": "note", "he": pit["car"]["_note"][:140]})
        if date_ < c.today():
            flags.append({"code": "past", "he": "התאריך כבר עבר"})
        thumb_of = lambda it: (it["images"] or [None])[0]  # noqa: E731
        opts = [{"key": it["key"], "label": "א" if it["key"].endswith("-a") else "ב", "title": it["car"].get("title", ""),
                 "format": it["car"].get("format") or "carousel", "addressee_he": ADDRESSEE_HE.get(it["car"].get("addressee"), ""),
                 "thumb": thumb_of(it), "errors": len([x for x in it["issues"] if x["level"] == "ERROR"]), "grade": None} for it in items]
        out.append({
            "id": pid, "kind": "season", "subtype": ser, "subtype_he": SERIES[ser]["he"], "subtype_icon": "gift",
            "date": date_, "time": time_, "channels": ["ig", "fb"],
            "title": (pit["car"].get("title") if pit else None) or SERIES[ser]["he"],
            "options": opts, "picked": picked, "status": status, "flags": flags, "needs": needs, "actions": [],
            "thumb": (thumb_of(pit) if pit else None) or next((o["thumb"] for o in opts if o["thumb"]), None),
            "postiz": None, "moved": bool(mv),
            "source": {"file": str(tb.CARS.relative_to(ROOT)) if tb.CARS.is_relative_to(ROOT) else str(tb.CARS), "key": d},
            "detail": {"series": ser, "plan_date": d, "items": items},
        })
    return out


def move(piece_id, to_date, to_time="keep"):
    if not DATE.match(to_date or "") or (to_time not in (None, "keep") and not TIME.match(str(to_time))):
        return 400, {"error": "bad date or time"}
    with _lock:
        st = read_state()
        mv = st["moves"].get(piece_id) or {}
        old = {"date": mv.get("date"), "time": mv.get("time")}
        st["moves"][piece_id] = {"date": to_date, "time": mv.get("time") if to_time == "keep" else to_time}
        if to_time is None:
            st["moves"][piece_id].pop("time", None)
        write_state(st)
    cc()._cache.pop("collect", None)
    return 200, {"ok": True, "undo": {"id": piece_id, **old}}


# ---------------------------------------------------------------- editing

def _text(v):
    return str(v if v is not None else "").replace("\r", "")[:MAX_TEXT]


def clean(car_in, key, old):
    """Keep what the renderer and lint know, with the key's own id, date and type. Raises ValueError on a bad shape."""
    if not isinstance(car_in, dict) or not isinstance(car_in.get("slides"), list) or not car_in["slides"]:
        raise ValueError("a carousel needs at least one slide")
    if len(car_in["slides"]) > 10:
        raise ValueError("Instagram takes at most 10 slides")
    ser, d, o = day_of(key)
    car = {k: v for k, v in old.items() if k not in TOP_KEYS and k != "slides"}   # sources, pictures, topic...: kept as they were
    car.update({"id": key, "date": d, "option": o, "type": SERIES[ser]["type"]})
    for k in TOP_TEXT:
        if k in car_in:
            car[k] = _text(car_in[k]).strip() if k == "comment_word" else _text(car_in[k])
    fmt = car_in.get("format")
    if fmt == "single":
        car["format"] = "single"
    if car_in.get("addressee") in ADDRESSEE_HE:
        car["addressee"] = car_in["addressee"]
    if car_in.get("style") in STYLES:
        car["style"] = car_in["style"]
    for k in ("emoji", "_note"):
        if car_in.get(k):
            car[k] = _text(car_in[k])
    if isinstance(car_in.get("book"), int):
        car["book"] = car_in["book"]
    if isinstance(car_in.get("links"), dict):
        car["links"] = {str(k)[:20]: _text(v)[:600] for k, v in car_in["links"].items() if str(v).startswith("https://")}
    known = set(tb.assets()) | set((car.get("pictures") or {}))
    slides = []
    for s in car_in["slides"]:
        if not isinstance(s, dict):
            raise ValueError("a slide is an object")
        t = {}
        lay = s.get("layout") if s.get("layout") in LAYOUTS else "point"
        t["layout"] = lay
        for k in SLIDE_TEXT + ("text_at", "pos", "quote_from"):
            if s.get(k) not in (None, ""):
                t[k] = _text(s[k])
        for k in ("bg", "cover"):
            if s.get(k):
                if s[k] not in known:
                    raise ValueError(f"no picture named {s[k]}")
                t[k] = s[k]
        for k in ("pics", "covers"):
            if isinstance(s.get(k), list) and s[k]:
                bad = [x for x in s[k] if x not in known]
                if bad:
                    raise ValueError(f"no picture named {bad[0]}")
                t[k] = list(s[k])[:3]
        if s.get("num") not in (None, ""):
            try:
                t["num"] = max(1, min(9, int(s["num"])))
            except (TypeError, ValueError):
                pass
        if t.get("pos") and not re.match(r"^\d{1,3}(\.\d+)?% \d{1,3}(\.\d+)?%$", t["pos"]):
            t.pop("pos")
        if s.get("model") in BOOK_MODELS:
            t["model"] = s["model"]
        if t.get("text_at") not in (None, "top", "bottom"):
            t.pop("text_at")
        slides.append(t)
    car["slides"] = slides
    return car


def _walk_text(car):
    out = {}
    for k in TOP_TEXT:
        if k not in ("comment_word", "title", "angle_he"):
            out[k] = car.get(k, "")
    for i, s in enumerate(car.get("slides") or [], start=1):
        for k in SLIDE_TEXT:
            if s.get(k):
                out[f"{i}.{k}"] = s[k]
    return out


def _note_voice(key, old, new):
    """Hold Yarin's text changes until the field rests, then log before/after once (the voice skill learns from them)."""
    before, after = _walk_text(old), _walk_text(new)
    now = time.time()
    for path in set(before) | set(after):
        b, a = before.get(path, ""), after.get(path, "")
        pk = (key, path)
        if pk in _pending:
            _pending[pk].update(after=a, at=now)
        elif a != b:
            _pending[pk] = {"before": b, "after": a, "at": now, "date": new.get("date"), "type": new.get("type"), "addressee": new.get("addressee")}


def flush_voice(force=False):
    now = time.time()
    recs = []
    with _lock:
        for pk, v in list(_pending.items()):
            if force or now - v["at"] > 90:
                _pending.pop(pk)
                if v["before"] != v["after"] and v["before"] and v["after"]:
                    key, path = pk
                    sl, _, field = path.rpartition(".")
                    recs.append({"at": lib.now_local().isoformat(timespec="seconds"), "pack_date": v["date"], "direction": f"seasonal-{v['type']}",
                                 "option": key, "field": field or path, "slide": int(sl) if sl.isdigit() else None, "role": "", "child_gender": None,
                                 "addressee": v["addressee"] or "", "kind": lib.edit_kind(v["before"], v["after"]),
                                 "before": v["before"], "after": v["after"]})
    if recs:
        try:
            lib.log_voice_edits(recs)
        except Exception:  # noqa: BLE001 - the text is saved; the voice log is a bonus
            pass


def _flusher():
    while True:
        time.sleep(30)
        try:
            flush_voice()
        except Exception:  # noqa: BLE001
            pass


threading.Thread(target=_flusher, daemon=True, name="season-voice").start()


def _backup(key, path):
    vdir = tb.VERSIONS / key
    vdir.mkdir(parents=True, exist_ok=True)
    olds = sorted(vdir.glob("v*.json"), key=lambda p: p.stat().st_mtime)
    if olds and time.time() - olds[-1].stat().st_mtime < 600:
        return None
    k = 1
    while (vdir / f"v{k}.json").exists():
        k += 1
    shutil.copy2(path, vdir / f"v{k}.json")
    return f"versions/{key}/v{k}.json"


def save(key, car_in):
    path = tb.CARS / f"{key}.json"
    with _lock:
        old = tb.read(path)
        car = clean(car_in, key, old)
        if car == old:
            return {"ok": True, "changed": False, "issues": lint_key(key)}
        bk = _backup(key, path)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(car, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(path)
        _note_voice(key, old, car)
        st = read_state()
        if key in st["approved"] and st["approved"][key] != content_hash(car):
            st["approved"].pop(key)       # an edit after an approval clears it
            write_state(st)
    cc()._cache.pop("collect", None)
    return {"ok": True, "changed": True, "issues": lint_key(key), "backup": bk,
            "fresh": fresh_for(key, car)}


def fresh_for(key, car):
    """Do the PNGs show this car? By the recorded hash, or (drawn from the command line) when it is the saved file and its PNGs are newer."""
    st = read_state()
    if key in st["rendered"]:
        return st["rendered"][key] == slide_hash(car)
    return slide_hash(car) == slide_hash(tb.read(tb.CARS / f"{key}.json")) and option_item(key, st)["fresh"]


def render_bg(key):
    with _lock:
        if (_renders.get(key) or {}).get("status") == "running":
            return {"status": "running"}
        _renders[key] = {"status": "running", "problems": [], "at": time.time()}

    def go():
        try:
            car = tb.read(tb.CARS / f"{key}.json")
            problems = sb.render(key)
            with _lock:
                st = read_state()
                st["rendered"][key] = slide_hash(car)
                write_state(st)
                _renders[key] = {"status": "done", "problems": problems, "at": time.time()}
        except Exception as exc:  # noqa: BLE001
            _renders[key] = {"status": "failed", "problems": [str(exc)[:300]], "at": time.time()}
        cc()._cache.pop("collect", None)

    threading.Thread(target=go, daemon=True, name="season-render-" + key).start()
    return {"status": "running"}


def handle(doc):
    """POST /api/calendar/season. Returns (status, body)."""
    op = str(doc.get("op") or "")
    key = str(doc.get("key") or "")
    if op in ("save", "preview", "render", "approve", "unapprove", "reset"):
        if not KEY.match(key) or not (tb.CARS / f"{key}.json").exists():
            return 404, {"error": "no such option"}
    try:
        if op == "save":
            return 200, save(key, doc.get("car"))
        if op == "preview":
            old = tb.read(tb.CARS / f"{key}.json")
            car = clean(doc.get("car"), key, old) if doc.get("car") is not None else old
            n = doc.get("n")
            return 200, {"html": sb.preview_html(car, key, int(n) if n else None), "issues": issues_of(car, key),
                         "fresh": fresh_for(key, car)}
        if op == "render":
            flush_voice(force=True)
            return 200, render_bg(key)
        if op in ("approve", "unapprove"):
            car = tb.read(tb.CARS / f"{key}.json")
            with _lock:
                st = read_state()
                if op == "approve":
                    if any(x["level"] == "ERROR" for x in lint_key(key)):
                        return 409, {"error": "lint", "he": "יש בטקסט מה לתקן לפני אישור"}
                    if not option_item(key, st)["fresh"]:
                        return 409, {"error": "stale", "he": "קודם ליצור את התמונות מהטקסט הנוכחי"}
                    st["approved"][key] = content_hash(car)
                else:
                    st["approved"].pop(key, None)
                write_state(st)
            cc()._cache.pop("collect", None)
            return 200, {"ok": True}
        if op == "reset":   # back to the last backup (an undo across sessions)
            vdir = tb.VERSIONS / key
            olds = sorted(vdir.glob("v*.json"), key=lambda p: p.stat().st_mtime) if vdir.exists() else []
            if not olds:
                return 404, {"error": "no backup", "he": "אין גרסה קודמת"}
            return 200, {"car": tb.read(olds[-1]), "from": olds[-1].name}
        if op == "pick":
            pid = str(doc.get("id") or "")
            if not re.match(r"^se-(bf|hn)-\d{4}-\d{2}-\d{2}$", pid):
                return 400, {"error": "bad piece"}
            with _lock:
                st = read_state()
                if doc.get("key"):
                    if not KEY.match(key) or f"se-{day_of(key)[0]}-{day_of(key)[1]}" != pid:
                        return 400, {"error": "that option is not of this day"}
                    st["picks"][pid] = key
                else:
                    st["picks"].pop(pid, None)
                write_state(st)
            cc()._cache.pop("collect", None)
            return 200, {"ok": True}
    except ValueError as exc:
        return 400, {"error": str(exc), "he": str(exc)}
    return 400, {"error": "unknown op"}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["pieces", "flush"])
    ap.add_argument("--month", default=time.strftime("%Y-%m"))
    a = ap.parse_args()
    if a.cmd == "pieces":
        for p in pieces(a.month):
            print(p["date"], p["time"], p["id"], p["status"], [o["key"] + ("*" if o["key"] == p["picked"] else "") for o in p["options"]])
    else:
        flush_voice(force=True)
