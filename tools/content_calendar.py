#!/usr/bin/env python3
"""לוח תוכן, the content calendar (Yarin, 11 Nov 2026: "merge carousel machine, the new carousel ideas, and the reel calendar
all in one place ... a big monthly calendar, i can open each day ... the hours and the content").

A front end over three engines that stay the single sources:
  - Carousel Machine (carousel/carousel-pipeline, the login item on :8777): the child-voice carousels (packs, options, grades,
    productions, Postiz). Unproduced options come only from the batch Carousel Machine opens by default; produced ones from
    productions.json and each run's postiz.json (the real post date: November's posts were made from the 30.11 to 6.12 packs).
  - the test batch (carousel/carousel-pipeline/test-batch/2026-11): one day, two options (a, b).
  - the reels (research/israeli-product-reels/src/scripts/series-2026-11/reels.json + the hub's local-edits.json).
  - the stories (19 Nov 2026, tools/stories.py: media/projects/2026-11-19-story-series/series.json): one set = one day of one series.
This module reads them into one list of pieces (collect), keeps the calendar's own state (sites/content-calendar/
calendar-state.json: hooks, approvals, moves of carousels, trial reels, reminders, ideas) and does the few writes the old tools
have no path for (move, state docs). The project server (tools/lumebook.py) answers /api/calendar* with it. Every other write
goes through the existing endpoints (Carousel Machine's /api/save, /api/save-test, /api/grade, /api/production/*; the hub's
/api/reels-hub/doc then reels.py merge local).

    python3 tools/content_calendar.py month 2026-11            # the month as the page gets it, one line a piece
    python3 tools/content_calendar.py hours [export.csv ...]   # import Meta exports (carousel audit) and suggest posting hours
"""
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stories  # noqa: E402  (the story sets, 19 Nov 2026)
import seasonal  # noqa: E402  (the Black Friday and Hanukkah carousels, 20 Nov 2026)

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "sites" / "content-calendar"
PIPE = Path(os.environ.get("LUMEBOOK_PIPELINE") or ROOT / "carousel" / "carousel-pipeline")   # a scratch copy on a test server
REELS_DIR = ROOT / "research" / "israeli-product-reels" / "src" / "scripts" / "series-2026-11"


def _env_path(name, default):
    v = os.environ.get(name)
    return Path(v) if v else default


REELS_JSON = _env_path("LUMEBOOK_REELS_DATA", REELS_DIR / "reels.json")
HUB_FILE = _env_path("LUMEBOOK_REELS_HUB_FILE", REELS_DIR / "local-edits.json")
TEST_DIR = _env_path("LUMEBOOK_TEST_BATCH_DIR", PIPE / "test-batch" / "2026-11")
STATE = _env_path("LUMEBOOK_CALENDAR_STATE", SITE / "calendar-state.json")
HOURS = _env_path("LUMEBOOK_CALENDAR_HOURS", SITE / "posting-hours.json")
PRODUCTIONS = PIPE / "productions.json"
GRADES = PIPE / "grades.json"
APPROVED = PIPE / "approved"
CM_URL = os.environ.get("LUMEBOOK_CM_URL") or "http://127.0.0.1:8777"
TEST_BATCH = "test-2026-11"
# Yarin, 20 Nov 2026: "remove the trial carousels from the content board". The test batch (קרוסלות ניסוי) is no longer drawn on the
# calendar; its files and Carousel Machine's סבב ניסוי stay as they are. LUMEBOOK_CALENDAR_TEST=1 brings the pieces back.
SHOW_TEST = os.environ.get("LUMEBOOK_CALENDAR_TEST") == "1"
# Reel suggestions (20 Nov 2026, Yarin: "remove all reel suggestions everywhere"): reels without a final video and not posted or sent,
# reel ideas and shoot days are not drawn. LUMEBOOK_CALENDAR_REEL_IDEAS=1 brings them back.
SHOW_REEL_SUGGESTIONS = os.environ.get("LUMEBOOK_CALENDAR_REEL_IDEAS") == "1"
try:
    from zoneinfo import ZoneInfo
    IL = ZoneInfo("Asia/Jerusalem")
except Exception:  # noqa: BLE001
    IL = timezone(timedelta(hours=2))

# ---------------------------------------------------------------- the one status ladder (README has the table)
STATUSES = [
    ("idea", "רעיון"), ("draft", "טיוטה"), ("grade", "לדרג"), ("pick", "לבחור"), ("hook", "לבחור הוק"), ("film", "לצלם"),
    ("produce", "להפיק"), ("making", "בהפקה"), ("approve", "מחכה לאישור שלי"), ("ready", "מוכן"),
    ("scheduled", "מתוזמן בפוסטיז"), ("posted", "עלה"),
]
STATUS_HE = dict(STATUSES)
NEEDS_ME = {"grade": "לדרג", "pick": "לבחור", "hook": "לבחור הוק", "film": "לצלם", "approve": "לאשר", "produce": "להפיק"}
KIND_HE = {"kid": "קרוסלת ילד", "test": "קרוסלת ניסוי", "reel": "ריל", "idea": "רעיון", "story": "סטוריז", "season": "קרוסלת חג"}
TEST_TYPES = {"say": ("תגידו את זה", "chat"), "how": ("ככה זה עובד", "compass"), "gift": ("מתנה לחנוכה", "gift"),
              "age": ("מה קורה בגיל", "trend"), "reveal": ("הרגע שרואים", "eye")}
RUN_MAKING = {"queued", "fixing", "preparing", "generating", "composing", "exporting", "started", "running"}
LANE_OF = {"kid-1": "a", "kid-2": "a", "kid-3": "a", "kid-4": "b", "kid-5": "b", "kid-6": "b",
           "expert-1": "x", "expert-2": "x", "expert-3": "x"}

_lock = threading.RLock()
_cache = {}


def now():
    return datetime.now(IL)


def today():
    return now().date().isoformat()


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path, obj, indent=1):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def url_of(path):
    """A file of this folder as the project server serves it (a static path, so it works when Carousel Machine is down)."""
    try:
        rel = Path(path).resolve().relative_to(ROOT)
    except ValueError:
        return ""
    p = Path(path)
    v = int(p.stat().st_mtime) if p.exists() else 0
    return "/" + "/".join(urllib.request.quote(x) for x in rel.parts) + f"?v={v}"


def _cm_fetch(path):
    try:
        with urllib.request.urlopen(CM_URL + path, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:  # noqa: BLE001 - down, slow or not JSON: the calendar shows what it can without it
        return None


def cm_get(path, ttl=25):
    """Carousel Machine's JSON (read only). The first call waits for it; later ones get the last answer at once and refresh it
    in the background when it is older than ttl seconds, so a slow Carousel Machine never holds up the page. None when it is
    down."""
    key = "cm:" + path
    hit = _cache.get(key)
    if hit is None:
        data = _cm_fetch(path)
        _cache[key] = [time.time(), data, False]
        return data
    if time.time() - hit[0] > ttl and not hit[2]:
        hit[2] = True

        def refresh():
            data = _cm_fetch(path)
            _cache[key] = [time.time(), data, False]
        threading.Thread(target=refresh, daemon=True).start()
    return hit[1]


# ---------------------------------------------------------------- the calendar's own state

STATE_COLLECTIONS = ("hooks", "approvals", "moves", "trials", "reminders", "ideas", "gpt", "postiz")
KEY_RE = re.compile(r"^[\w.\-]{1,80}$")


def state():
    s = read_json(STATE, {}) or {}
    for c in STATE_COLLECTIONS:
        if not isinstance(s.get(c), dict):
            s[c] = {}
    return s


def put_doc(coll, key, doc):
    """One document of calendar-state.json (doc None deletes it). Returns (status, body)."""
    if coll not in STATE_COLLECTIONS or not KEY_RE.match(key or ""):
        return 400, {"error": "bad path"}
    if doc is not None and not isinstance(doc, dict):
        return 400, {"error": "a document is a JSON object"}
    with _lock:
        s = state()
        s.setdefault("_about", "The content calendar's own state (tools/content_calendar.py, sites/content-calendar/README.md).")
        if doc is None:
            s[coll].pop(key, None)
        else:
            s[coll][key] = {**doc, "at": now().isoformat(timespec="seconds")}
        write_json(STATE, s)
    _cache.pop("collect", None)
    return 200, {"ok": True}


def hours():
    return read_json(HOURS, {}) or {}


def plan_time(date_s, role):
    """The planned posting time of a role on a date from the weekly plan in posting-hours.json ("HH:MM"), or None. Weekdays there
    are 0 = Sunday ... 6 = Saturday; roles: kid, test, reel_a, reel_b (Yarin, 11 Nov 2026: four posting hours a day)."""
    try:
        d = date.fromisoformat(date_s)
    except (TypeError, ValueError):
        return None
    return ((hours().get("plan") or {}).get(str((d.weekday() + 1) % 7)) or {}).get(role)


# ---------------------------------------------------------------- reels

def rid(r):
    return "r" + r["id"].replace(".", "-")


def reel_texts(r, edits):
    """The reel's words with the hub's unsaved-to-json edits on top (local-edits.json "edits": {key: {key, text}})."""
    k = rid(r)

    def ed(field, default):
        doc = edits.get(f"{k}__{field}")
        t = (doc or {}).get("text")
        return t.strip() if isinstance(t, str) and t.strip() else default
    vo = [ed(f"vo__{i}", v) for i, v in enumerate(r.get("vo") or [])]
    sees = [ed(f"sees__{i}", v) for i, v in enumerate(r.get("sees") or [])]
    th = [ed(f"trialhooks__{i}", v) for i, v in enumerate((r.get("trial_hooks") or []) + [""] * (4 - len(r.get("trial_hooks") or [])))]
    return {"hook": ed("hook", r.get("hook", "")), "vo": vo, "sees": sees, "caption": ed("caption", r.get("caption", "")),
            "payoff": ed("payoff", r.get("payoff", "")), "shot": ed("shot", r.get("shot", "")), "trial_hooks": th[:4],
            "structure": r.get("structure", ""), "notes": r.get("notes", "")}


def reel_media(r):
    """The reel's made files: the newest final, its QC picture, the trial versions."""
    out = {"final": None, "qc": None, "trials": [], "files": 0}
    if not r.get("project"):
        return out
    folder = ROOT / r["project"]
    name = "reel-" + r["id"].replace(".", "-")
    fin = folder / "final" / f"{name}-1.mp4"
    if fin.exists():
        out["final"] = "/api/reel-files/raw?reel=" + rid(r) + "&f=" + urllib.request.quote(f"final/{name}-1.mp4")
        out["final_at"] = datetime.fromtimestamp(fin.stat().st_mtime, IL).isoformat(timespec="minutes")
    qc = folder / "final" / f"{name}-qc.jpg"
    if qc.exists():
        out["qc"] = url_of(qc)
    tdir = folder / "trial"
    if tdir.is_dir():
        out["trials"] = ["/api/reel-files/raw?reel=" + rid(r) + "&f=" + urllib.request.quote(f"trial/{f.name}")
                         for f in sorted(tdir.glob(f"{name}-trial-*.mp4"))]
    src = folder / "source"
    out["files"] = len([f for f in src.iterdir() if not f.name.startswith(".")]) if src.is_dir() else 0
    rep = read_json(folder / "work" / "make" / "report.json", {}) or {}
    try:
        out["seconds"] = round(float(rep["length"]), 1)   # the real length of the made reel, like reels.made_seconds
    except (KeyError, TypeError, ValueError):
        out["seconds"] = None
    return out


REEL_VOICE_HE = {"yarin": "הקריינות שלך", "text": "טקסט בלי קול", "trend": "טרנד מוכן"}   # the reel calendar's VOICE (build_page.py)


def reel_series_he():
    sets = (read_json(ROOT / "shared" / "design" / "categories.json", {}) or {}).get("sets") or {}
    return {k: v.get("label", "") for k, v in ((sets.get("reel-series") or {}).get("items") or {}).items()}


def reels_cfg(defaults):
    """What the reel panel needs from reels.json "defaults" to draw the reel calendar's card: the script timing (the same estimate as
    reels.seconds), the fixed closing line, the facts and the word limits its asks give Claude (build_page.py ask_cfg)."""
    L = defaults.get("length") or {}
    lead, wps = float(L.get("lead_seconds") or 1.0), float(L.get("words_per_second") or 2.8)
    lo, hi = float(L.get("min") or 10), float(L.get("max") or 30)
    cta_words = len((defaults.get("cta_voice") or "").split())
    return {"lead_seconds": lead, "words_per_second": wps, "min": lo, "max": hi,
            "vo_min": max(1, int((lo - lead) * wps) + 1 - cta_words), "vo_max": int((hi - lead) * wps) - cta_words,
            "cta_voice": defaults.get("cta_voice", ""), "cta_sees": defaults.get("cta_sees", ""), "cta_caption": defaults.get("cta_caption", ""),
            "disclaimer": defaults.get("caption_disclaimer", ""), "facts": defaults.get("facts", ""),
            "offer": (defaults.get("offer") or {}).get("text", "") if isinstance(defaults.get("offer"), dict) else ""}


def reel_pieces(month, st, jobs):
    d = read_json(REELS_JSON, {}) or {}
    hub = read_json(HUB_FILE, {}) or {}
    edits = hub.get("edits") or {}
    made_ticks = hub.get("made") or {}
    defaults = d.get("defaults") or {}
    pages = defaults.get("pages") or {}
    series_he = reel_series_he()
    hr = hours()
    times = ((hr.get("previous") or {}).get("reel") or ["21:30", None])
    making = {j.get("reel") for j in jobs if j.get("kind") == "make" and j.get("status") in ("queued", "running")}
    shoots = {s["date"]: s for s in d.get("shoots") or []}
    out = []
    for r in d.get("reels") or []:
        if not r.get("date") or r.get("status") == "spare":
            continue
        pid = "r-" + r["id"]
        mv = st["moves"].get(pid) or {}
        dt = r["date"]
        opt = r.get("option") or 1
        if r.get("status") == "posted":
            tm = mv.get("time") or defaults.get("post_time_posted") or "21:30"
        else:
            tm = mv.get("time") or plan_time(dt, "reel_a" if opt == 1 else "reel_b") or (times[opt - 1] if opt - 1 < len(times) else None)
        if not dt.startswith(month):
            continue
        tx = reel_texts(r, edits)
        media = reel_media(r)
        hk = st["hooks"].get(pid) or {}
        appr = st["approvals"].get(pid) or {}
        trials = st["trials"].get(r["id"]) or {}
        flags, needs, actions = [], [], []
        if r.get("status") == "posted":
            status = "posted"
        elif rid(r) in making:
            status = "making"
        elif media["final"]:
            status = "ready" if appr.get("main") else "approve"
            if not appr.get("main"):
                needs.append("approve")
        elif hk.get("picked") is None and r.get("status") != "ready":
            status = "hook"
            needs.append("hook")
        elif r.get("status") in ("needs-voice", "needs-footage", "blocked", "needs-edit"):
            status = "film"
            needs.append("film")
        else:
            status = "produce"
            needs.append("produce")
        if not SHOW_REEL_SUGGESTIONS and status in ("hook", "film", "produce"):
            continue
        if r.get("blockers"):
            flags.append({"code": "blocked", "he": "חסר: " + "; ".join(str(b) for b in r["blockers"])[:200]})
        gpt = r.get("gpt") or {}
        gst = st["gpt"].get(r["id"]) or {}
        if gpt.get("images") and not gst.get("done") and r.get("status") != "posted":
            flags.append({"code": "budget", "he": f"תמונות GPT: תקציב מוצע ${gpt.get('budget_usd', 0):.2f}"})
        if media["trials"] and not (st["postiz"].get(r["id"]) or {}).get("trials"):
            flags.append({"code": "trials", "he": f"{len(media['trials'])} גרסאות ניסיון"})
        if not tm:
            flags.append({"code": "no_time", "he": "שעה לא נקבעה"})
        sent = st["postiz"].get(r["id"]) or {}
        extra_ids, pz = [], None
        if sent.get("main"):
            pz = refine({"date": sent["main"]["date"], "status": "schedule", "sent_at": sent["main"].get("sent_at")}, sent["main"].get("ids") or [])
            if status not in ("posted",) and pz.get("status") in ("schedule", "published", "draft"):
                status = "posted" if pz["status"] == "published" else "scheduled"
                needs = []
            if pz.get("status") == "gone":
                flags.append({"code": "pz_gone", "he": "הריל הראשי לא נמצא בפוסטיז (נמחק שם)"})
        for tk, tv in (sent.get("trials") or {}).items():
            extra_ids += tv.get("ids") or []
        for tk, tv in (sent.get("fb_trials") or {}).items():
            extra_ids += tv.get("ids") or []
        if sent.get("trials"):
            flags.append({"code": "trials", "he": f"{len(sent['trials'])} גרסאות ניסיון בפוסטיז"})
        out.append({
            "postiz": pz, "postiz_extra_ids": extra_ids,
            "id": pid, "kind": "reel", "subtype": str(r.get("series", "")), "subtype_he": f"סדרה {r.get('series', '')}",
            "date": dt, "time": tm, "channels": ["ig", "fb"], "title": " ".join(tx["hook"].split()),
            "options": [], "picked": None, "status": status, "flags": flags, "needs": needs, "actions": actions,
            "thumb": media["qc"], "source": {"file": str(REELS_JSON.relative_to(ROOT)) if REELS_JSON.is_relative_to(ROOT) else REELS_JSON.name,
                                             "key": r["id"]},
            "moved": bool(mv),
            "detail": {"reel": r["id"], "rkey": rid(r), "option": opt, "series": r.get("series"), "status_src": r.get("status"),
                       "voice": r.get("voice"), "approach": r.get("approach"), "audience": r.get("audience"),
                       # the reel calendar's card header: series, length, voice, audience, the book page the DM link opens, עשיתי
                       "series_he": series_he.get(str(r.get("series")), ""), "voice_he": REEL_VOICE_HE.get(r.get("voice"), ""),
                       "page": r.get("page"), "book": pages.get(r.get("page"), r.get("page") or ""),
                       "book_url": ("https://lumebook.com/IL/he/" + r["page"]) if r.get("page") else None,
                       "made": bool((made_ticks.get(rid(r)) or {}).get("made")) if rid(r) in made_ticks else r.get("status") == "posted",
                       "own_cta": any("לומי" in l for l in tx["vo"][-2:]), "clip_seconds": r.get("clip_seconds"),
                       "texts": tx, "media": media, "project": r.get("project"), "blockers": r.get("blockers") or [],
                       "yarin_films": r.get("yarin_films") or [], "gpt": gpt, "gpt_state": gst,
                       "hooks": hk, "approval": appr, "trials": trials, "pz_sent": sent, "pz_text": reel_post_texts(tx, defaults),
                       "shoot": shoots.get(dt, {}).get("note") if r["id"] in (shoots.get(dt, {}).get("for") or []) else None},
        })
    # shoot days: a separate, non-posting row
    for dt, s in (shoots.items() if SHOW_REEL_SUGGESTIONS else []):
        if dt.startswith(month):
            out.append({"id": "s-" + dt, "kind": "shoot", "date": dt, "time": None, "title": "צילום", "status": None,
                        "detail": {"note": s.get("note", ""), "for": s.get("for") or []}, "flags": [], "needs": [], "channels": []})
    return out, d


# ---------------------------------------------------------------- carousels shared

def grades_all():
    return (read_json(GRADES, {}) or {}).get("grades") or {}


def runs_all():
    return (read_json(PRODUCTIONS, {}) or {}).get("runs") or {}


POSTIZ_CMD = os.environ.get("LUMEBOOK_POSTIZ_CMD") or str(Path.home() / ".local" / "bin" / "postiz")
_pz_live = {}


def postiz_live(month):
    """Postiz's own list of the month's posts (read only: `postiz posts:list`), refreshed in the background every 5 minutes so
    the page never waits on it. {post id: {state, date, url, channel, group, text}}; None until the first answer (or when the
    CLI is missing, off, or not signed in). The calendar trusts this over the postiz.json a run kept: on 30 Oct 2026 the
    1 and 3 Nov posts were deleted in Postiz while their records still said scheduled."""
    if POSTIZ_CMD == "off":
        return None
    ent = _pz_live.get(month)
    if not ent or (time.time() - ent["t"] > 300 and not ent.get("busy")):
        if ent:
            ent["busy"] = True
        else:
            _pz_live[month] = ent = {"t": 0, "data": None, "busy": True}

        def fetch():
            y, m = map(int, month.split("-"))
            start = date(y, m, 1) - timedelta(days=2)
            end = (date(y + (m == 12), m % 12 + 1, 1)) + timedelta(days=2)
            data = None
            try:
                p = subprocess.run([POSTIZ_CMD, "posts:list", "--startDate", start.isoformat() + "T00:00:00Z", "--endDate",
                                    end.isoformat() + "T00:00:00Z"], capture_output=True, text=True, timeout=60,
                                   env={**os.environ, "PATH": os.pathsep.join([str(Path(POSTIZ_CMD).parent), "/usr/local/bin",
                                                                               "/opt/homebrew/bin", "/usr/bin", "/bin"])})
                raw = p.stdout
                a = min([i for i in (raw.find("{"), raw.find("[")) if i >= 0] or [0])
                body = json.loads(raw[a:]) if raw.strip() else {}
                posts = body.get("posts", body) if isinstance(body, dict) else body
                data = {}
                for x in posts or []:
                    integ = x.get("integration")
                    if isinstance(integ, str):
                        prov = "instagram" if "instagram" in integ else "facebook" if "facebook" in integ else ""
                    else:
                        prov = (integ or {}).get("providerIdentifier", "")
                    data[x["id"]] = {"state": x.get("state"), "date": x.get("publishDate"), "url": x.get("releaseURL"),
                                     "channel": "ig" if "instagram" in prov else "fb" if "facebook" in prov else prov,
                                     "group": x.get("group"), "error": x.get("error"),
                                     "text": (x.get("content") or "").split("\n")[0][:120]}
            except Exception:  # noqa: BLE001 - Postiz unreachable: keep the last answer
                data = ent.get("data")
            ent.update(t=time.time(), data=data, busy=False)
            _cache.pop("collect", None)
        threading.Thread(target=fetch, daemon=True).start()
    return ent.get("data")


_LIVE = {"data": None}


def postiz_of(run, live=None):
    """The run's postiz.json (what was sent, when it goes out), checked against Postiz's own list when it is known."""
    if not run or not run.get("run_dir"):
        return None
    p = PIPE / run["run_dir"].lstrip("/") / "postiz.json"
    j = read_json(p)
    if not j or not j.get("date"):
        return run.get("postiz")
    out = {"date": j["date"], "status": j.get("status"), "sent_at": j.get("sent_at")}
    ids = [r.get("postId") for r in (j.get("result") or []) if isinstance(r, dict) and r.get("postId")]
    return refine(out, ids, live)


def refine(out, ids, live=None):
    """Check a send record (ids of its Postiz posts) against Postiz's own list: published, queued, draft, error, or gone."""
    out["ids"] = ids
    live = live if live is not None else _LIVE["data"]
    if live is not None and ids:
        found = [live[i] for i in ids if i in live]
        recent = False
        try:
            recent = bool(out.get("sent_at")) and now() - datetime.fromisoformat(out["sent_at"]) < timedelta(minutes=10)
        except ValueError:
            pass
        if not found and not recent:   # a send of the last 10 minutes may not be in the cached Postiz list yet
            out["status"] = "gone"     # not in Postiz any more (deleted there)
        elif not found:
            pass
        else:
            out["live"] = [{"channel": f["channel"], "state": f["state"], "url": f["url"], "error": f["error"]} for f in found]
            out["date"] = found[0]["date"] or out["date"]
            if all(f["state"] == "PUBLISHED" for f in found):
                out["status"] = "published"
            elif any(f["state"] == "ERROR" or f.get("error") for f in found):
                out["status"] = "error"
            elif all(f["state"] == "DRAFT" for f in found):
                out["status"] = "draft"
    return out


def run_status(run, pz):
    """(status, flags) of a production record."""
    flags = []
    s = (run or {}).get("status")
    if not run:
        return None, flags
    if s == "approval":
        return "approve", flags
    if s == "review":
        return "approve", flags
    if s in RUN_MAKING:
        return "making", flags
    if s == "failed":
        flags.append({"code": "failed", "he": "ההפקה נעצרה: " + str(run.get("error") or "")[:160]})
        return "produce", flags
    if s == "done":
        st_ = (pz or {}).get("status")
        if st_ == "published":
            return "posted", flags
        if st_ == "error":
            flags.append({"code": "pz_error", "he": "פוסטיז דיווח על שגיאה בפרסום"})
            return "scheduled", flags
        if st_ == "schedule":
            try:
                past = datetime.fromisoformat(pz["date"].replace("Z", "+00:00")) <= now()
            except ValueError:
                past = False
            if past and not pz.get("live"):
                flags.append({"code": "pz_unchecked", "he": "לפי הרישום עלה; פוסטיז עוד לא נבדק"})
            return ("posted" if past else "scheduled"), flags
        if st_ == "gone":
            flags.append({"code": "pz_gone", "he": "לא נמצא בפוסטיז (נמחק שם)"})
        if st_ == "draft":
            flags.append({"code": "pz_draft", "he": "טיוטה בפוסטיז"})
        return "ready", flags
    return "making", flags


def retime_flag(pz, posted_time, planned):
    """A carousel already queued in Postiz at another time than the weekly plan: said plainly, never moved from here."""
    if pz and pz.get("status") == "schedule" and posted_time and planned and posted_time != planned:
        return [{"code": "retime", "he": f"בפוסטיז ב־{posted_time}, לפי התכנית {planned} (לא משתנה בלי אישור שלך)"}]
    return []


def pz_split(pz):
    """'2026-11-11T06:00:00+02:00' -> ('2026-11-11', '06:00'); nothing for a post deleted in Postiz."""
    if not pz or pz.get("status") == "gone":
        return None, None
    try:
        t = datetime.fromisoformat(pz["date"].replace("Z", "+00:00")).astimezone(IL)
        return t.date().isoformat(), t.strftime("%H:%M")
    except (ValueError, KeyError, TypeError):
        return None, None


def run_slides(run):
    out = []
    for s in (run or {}).get("slides") or []:
        p = PIPE / s.split("?")[0].lstrip("/")
        out.append(url_of(p) if p.exists() else "")
    return [x for x in out if x]


# ---------------------------------------------------------------- kid carousels

def kid_pieces(month, st, notices, drafts=False, hidden=None):
    grades, runs = grades_all(), runs_all()
    hr = hours()
    kid_time = (hr.get("previous") or {}).get("kid") or "06:00"
    out, seen_runs = [], set()
    cur = cm_get("/api/state")
    lanes = {}
    if cur and cur.get("items"):
        for it in cur["items"]:
            lanes.setdefault((it["date"], it.get("lane") or LANE_OF.get(it["id"], "x")), []).append(it)
    elif cur is None:
        notices.append("מכונת הקרוסלות לא עונה כרגע: מוצגים הרילס, הקרוסלות שהופקו וקרוסלות הניסוי מהקבצים (בלי בדיקת ניסוח ותקציב)." + (" טיוטות של קרוסלות ילד יחזרו כשהיא תעלה." if drafts else ""))
    # 1) the current batch: one piece per day and topic (lane), its three options
    for (dt, lane), its in sorted(lanes.items()):
        its.sort(key=lambda i: i["id"])
        pid = f"k-{dt}-{lane}"
        run_key = next((i["key"] for i in its if i["key"] in runs), None)
        run = runs.get(run_key) if run_key else None
        pz = postiz_of(run)
        mv = st["moves"].get(pid) or {}
        pdate, ptime = pz_split(pz) if pz else (None, None)
        date_ = pdate or mv.get("date") or dt
        time_ = ptime or mv.get("time") or plan_time(date_, "kid") or kid_time
        if not date_.startswith(month):
            if run_key:
                seen_runs.add(run_key)
            continue
        if not run_key and not drafts:   # a pack nobody planned or produced: kept off the grid (the toggle shows it)
            if hidden is not None:
                hidden.append(pid)
            continue
        opts = []
        for i in its:
            g = grades.get(i["key"]) or {}
            opts.append({"key": i["key"], "id": i["id"], "label": i["id"].split("-")[-1], "title": i.get("title", ""),
                         "grade": g.get("score"), "produce": bool(g.get("produce")), "errors": len(i.get("errors") or []),
                         "child": i.get("child_name", ""), "structure_he": i.get("structure_he", "")})
        picked = run_key or next((o["key"] for o in opts if o["produce"]), None)
        status, flags = run_status(run, pz)
        flags += retime_flag(pz, ptime, plan_time(date_, "kid"))
        needs = []
        hk_key = f"{pid}.{(picked or '').split('/')[-1]}"
        if not status:
            if all(o["errors"] for o in opts):
                status = "draft"
            elif not picked:
                status = "pick" if any(o["grade"] for o in opts) else "grade"
            elif (st["hooks"].get(hk_key) or {}).get("picked") is None:
                status = "hook"
            else:
                status = "produce"
        if status in NEEDS_ME:
            needs.append(status)
        if run_key:
            seen_runs.add(run_key)
        out.append({
            "id": pid, "kind": "kid", "subtype": its[0].get("topic_id", ""), "subtype_he": its[0].get("topic_he", ""),
            "date": date_, "time": time_, "channels": ["ig", "fb"], "title": its[0].get("topic_he", ""),
            "options": opts, "picked": picked, "status": status, "flags": flags, "needs": needs, "actions": [],
            "thumb": (run_slides(run) or [None])[0], "postiz": pz, "moved": bool(mv) and not pz,
            "source": {"file": f"carousel/carousel-pipeline/drafts/{dt}/pack.json", "key": run_key or f"{dt}/{lane}"},
            "detail": {"batch": cur.get("batch") if cur else None, "pack_date": dt, "lane": lane, "hook_key": hk_key,
                       "items": [{k: i.get(k) for k in ("key", "id", "title", "child_name", "addressee", "structure_he", "slides",
                                                        "caption", "caption_body", "cta", "errors", "pictures")} for i in its],
                       "run": run, "slides": run_slides(run), "hooks": st["hooks"].get(hk_key) or {}},
        })
    # 2) produced runs of other batches (their date is the Postiz date): November's kid carousels
    for key, run in runs.items():
        if key in seen_runs or key.startswith(TEST_BATCH + "/") or run.get("kind") not in ("kid", "expert"):
            continue
        pz = postiz_of(run)
        dt, oid = key.split("/", 1)
        lane = LANE_OF.get(oid, "x")
        pid = f"k-{dt}-{lane}"
        mv = st["moves"].get(pid) or {}
        pdate, ptime = pz_split(pz) if pz else (None, None)
        date_ = pdate or mv.get("date") or run.get("date") or dt
        time_ = ptime or mv.get("time") or plan_time(date_, "kid") or kid_time
        if not date_.startswith(month):
            continue
        status, flags = run_status(run, pz)
        flags += retime_flag(pz, ptime, plan_time(date_, "kid"))
        out.append({
            "id": pid, "kind": "kid" if run.get("kind") == "kid" else "kid", "subtype": oid, "subtype_he": run.get("topic_he", ""),
            "date": date_, "time": time_, "channels": ["ig", "fb"], "title": run.get("topic_he", ""),
            "options": [{"key": key, "id": oid, "label": oid.split("-")[-1], "title": run.get("cover", ""), "grade": None,
                         "produce": True, "errors": 0}],
            "picked": key, "status": status, "flags": flags, "needs": ["approve"] if status == "approve" else [], "actions": [],
            "thumb": (run_slides(run) or [None])[0], "postiz": pz, "moved": bool(mv) and not pz,
            "source": {"file": f"carousel/carousel-pipeline/drafts/{dt}/pack.json", "key": key},
            "detail": {"batch": run.get("batch"), "pack_date": dt, "lane": lane, "hook_key": f"{pid}.{oid}", "items": [],
                       "run": run, "slides": run_slides(run), "hooks": {}, "caption": _read_text(run, "final/caption.txt")},
        })
    return out


def _read_text(run, rel):
    if not run or not run.get("run_dir"):
        return ""
    p = PIPE / run["run_dir"].lstrip("/") / rel
    try:
        return p.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


# ---------------------------------------------------------------- test carousels

def test_pieces(month, st, notices):
    plan = read_json(TEST_DIR / "plan.json", {}) or {}
    days = {d["date"]: d for d in plan.get("days") or []}
    cm = cm_get(f"/api/state?batch={TEST_BATCH}")
    by_key = {i["id"]: i for i in (cm or {}).get("items") or []}
    grades, runs = grades_all(), runs_all()
    if cm is None and days and not any("מכונת הקרוסלות" in n for n in notices):
        notices.append("מכונת הקרוסלות לא עונה כרגע: קרוסלות הניסוי מוצגות מהקבצים, בלי בדיקת ניסוח ותקציב.")
    out = []
    for dt, day in sorted(days.items()):
        pid = "t-" + dt
        mv = st["moves"].get(pid) or {}
        opts, runs_here = [], {}
        for o in ("a", "b"):
            key = f"{dt}-{o}"
            path = TEST_DIR / "carousels" / f"{key}.json"
            if not path.exists():
                continue
            it = by_key.get(key)
            car = None if it else read_json(path, {})
            gkey = f"{TEST_BATCH}/{key}"
            g = grades.get(gkey) or {}
            run = runs.get(gkey)
            if run:
                runs_here[gkey] = run
            if it is None:
                sdir = TEST_DIR / "slides" / key
                imgs = [u for u in (url_of(p) for p in sorted(sdir.glob("[0-9][0-9].png"))) if u]
                it = {"id": key, "key": gkey, "title": car.get("title", ""), "slides": car.get("slides", []), "images": imgs,
                      "caption": car.get("caption", ""), "cta": car.get("cta", ""), "fb_text": car.get("fb_text", ""),
                      "comment_word": car.get("comment_word", ""), "addressee_he": {"mom": "לאמא", "grandma": "לסבתא"}.get(car.get("addressee"), ""),
                      "lint": [], "budget": None, "type": car.get("type", day.get("type"))}
            else:
                it = dict(it)
                it["images"] = [u for u in (url_of(TEST_DIR / "slides" / key / f"{i:02d}.png") for i in range(1, len(it.get("slides") or []) + 1)
                                            if (TEST_DIR / "slides" / key / f"{i:02d}.png").exists()) if u]
            errors = [x for x in it.get("lint") or [] if x.get("level") == "ERROR"]
            opts.append({"key": gkey, "id": key, "label": "א" if o == "a" else "ב", "title": it.get("title", ""),
                         "grade": g.get("score"), "produce": bool(g.get("produce")), "errors": len(errors),
                         "addressee_he": it.get("addressee_he", ""), "thumb": (it.get("images") or [None])[0],
                         "budget": it.get("budget"), "item": it})
        if not opts:
            continue
        run_key = next(iter(runs_here), None)
        run = runs_here.get(run_key)
        pz = postiz_of(run)
        pdate, ptime = pz_split(pz) if pz else (None, None)
        date_ = pdate or mv.get("date") or dt
        time_ = ptime or mv.get("time") or plan_time(date_, "test") or day.get("time", "09:30")
        if not date_.startswith(month):
            continue
        picked = run_key or next((o["key"] for o in opts if o["produce"]), None)
        status, flags = run_status(run, pz)
        flags += retime_flag(pz, ptime, plan_time(date_, "test"))
        hk_key = f"{pid}.{(picked or '').split('-')[-1]}" if picked else ""
        if not status:
            if all(o["errors"] for o in opts):
                status = "draft"
            elif not picked:
                status = "pick" if any(o["grade"] for o in opts) else "grade"
            elif (st["hooks"].get(hk_key) or {}).get("picked") is None:
                status = "hook"
            else:
                status = "produce"
        if picked:
            po = next((o for o in opts if o["key"] == picked), None)
            b = (po or {}).get("budget") or {}
            if b and b.get("budget_usd") and status in ("produce", "hook"):
                flags.append({"code": "budget", "he": f"תמונות: עד ${float(b['budget_usd']):.2f} בלחיצה על להפיק"})
        t_he, t_icon = TEST_TYPES.get(day.get("type"), (day.get("type", ""), "flask"))
        out.append({
            "id": pid, "kind": "test", "subtype": day.get("type"), "subtype_he": t_he, "subtype_icon": t_icon,
            "date": date_, "time": time_, "channels": ["ig", "fb"],
            "title": next((o["title"] for o in opts if o["key"] == picked), None) or t_he,
            "options": [{k: v for k, v in o.items() if k != "item"} for o in opts], "picked": picked, "status": status,
            "flags": flags, "needs": [status] if status in NEEDS_ME else [], "actions": [],
            "thumb": next((o["thumb"] for o in opts if o["key"] == picked), None) or opts[0]["thumb"], "postiz": pz,
            "moved": bool(mv) and not pz,
            "source": {"file": str(Path("carousel/carousel-pipeline/test-batch/2026-11/carousels")), "key": dt},
            "detail": {"plan_date": dt, "slot": day.get("slot"), "items": [o["item"] for o in opts], "run": run,
                       "slides": run_slides(run), "hook_key": hk_key, "hooks": st["hooks"].get(hk_key) or {} if hk_key else {}},
        })
    return out


# ---------------------------------------------------------------- ideas and reminders

def idea_pieces(month, st):
    out = []
    for k, v in st["ideas"].items():
        if not str(v.get("date", "")).startswith(month) or (v.get("for") == "reel" and not SHOW_REEL_SUGGESTIONS):
            continue
        hk = st["hooks"].get("i-" + k) or {}
        status = "hook" if hk.get("options") and hk.get("picked") is None else "idea"
        out.append({"id": "i-" + k, "kind": "idea", "subtype": v.get("for", "carousel"), "subtype_he": "קרוסלה" if v.get("for") != "reel" else "ריל",
                    "date": v["date"], "time": v.get("time"), "channels": ["ig", "fb"], "title": v.get("title") or v.get("brief", "")[:60],
                    "options": [], "picked": None, "status": status, "flags": [], "needs": ["hook"] if status == "hook" else [],
                    "actions": [], "thumb": None, "postiz": None, "moved": False, "source": {"file": "sites/content-calendar/calendar-state.json", "key": k},
                    "detail": {"idea": v, "hooks": hk, "hook_key": "i-" + k}})
    return out


def reminder_pieces(month, st, reels):
    """The day after a reel's trial versions went up: share one to the main feed and post it on Facebook (Yarin, 11 Nov 2026)."""
    out = []
    for r in reels:
        if r.get("kind") != "reel":
            continue
        trials = r["detail"]["media"]["trials"]
        if not trials:
            continue
        nxt = (date.fromisoformat(r["date"]) + timedelta(days=1)).isoformat()
        if not nxt.startswith(month):
            continue
        done = (st["reminders"].get(r["detail"]["reel"]) or {}).get("done")
        out.append({"id": "m-" + r["detail"]["reel"], "kind": "remind", "date": nxt, "time": None,
                    "title": f"לשתף לראשי ולפייסבוק: ריל {r['detail']['reel']}", "status": "posted" if done else None,
                    "flags": [], "needs": [] if done else ["remind"], "channels": ["ig", "fb"],
                    "detail": {"reel": r["detail"]["reel"], "trials": trials, "done": done, "hook": r["title"],
                               "fb_text": r["detail"]["pz_text"]["fb"],
                               "fb_done": [i for i, u in enumerate(trials) if urllib.parse.unquote(u).rsplit("/", 1)[-1] in ((r["detail"]["pz_sent"] or {}).get("fb_trials") or {})]}})
    return out


def postiz_only(month, pieces):
    """Posts that are in Postiz but belong to no carousel run here (a reel sent by hand, a post made in Postiz): shown so the
    month matches what really goes out. IG and FB of one post (same Postiz group) are one item."""
    live = _LIVE["data"]
    if not live:
        return []
    known = {i for p in pieces for i in ((p.get("postiz") or {}).get("ids") or []) + (p.get("postiz_extra_ids") or [])}
    groups = {}
    for pid_, x in live.items():
        if pid_ in known or not x.get("date"):
            continue
        groups.setdefault(x.get("group") or pid_, []).append((pid_, x))
    out = []
    for g, xs in groups.items():
        x = xs[0][1]
        try:
            t = datetime.fromisoformat(x["date"].replace("Z", "+00:00")).astimezone(IL)
        except ValueError:
            continue
        if not t.date().isoformat().startswith(month):
            continue
        published = all(y["state"] == "PUBLISHED" for _, y in xs)
        pz = {"status": "published" if published else "schedule", "ids": [i for i, _ in xs], "date": x["date"],
              "live": [{"channel": y["channel"], "state": y["state"], "url": y["url"]} for _, y in xs]}
        # a reel that went up through Postiz: matched by day and the words of its caption or hook, so it is one item
        words = set(re.findall(r"[א-ת]{3,}", x["text"]))
        reel = None
        for p in pieces:
            if p["kind"] != "reel" or p["date"] != t.date().isoformat() or p.get("postiz"):
                continue
            tx = p["detail"]["texts"]
            mine = set(re.findall(r"[א-ת]{3,}", tx["caption"].split("\n")[0] + " " + tx["hook"]))
            if words and mine and len(words & mine) / max(1, min(len(words), len(mine))) >= .5:
                reel = p
                break
        if reel:
            reel["postiz"] = pz
            reel["status"] = "posted" if published else "scheduled"
            reel["needs"] = []
            reel["time"] = t.strftime("%H:%M")
            continue
        out.append({"id": "p-" + g[:36], "kind": "post", "subtype": "", "subtype_he": "", "date": t.date().isoformat(),
                    "time": t.strftime("%H:%M"), "channels": sorted({y["channel"] for _, y in xs}), "title": x["text"],
                    "options": [], "picked": None, "status": "posted" if published else "scheduled", "flags": [], "needs": [],
                    "actions": [], "thumb": None, "postiz": {"status": "published" if published else "schedule", "ids": [i for i, _ in xs],
                                                            "live": [{"channel": y["channel"], "state": y["state"], "url": y["url"]} for _, y in xs]},
                    "moved": False, "source": {"file": "Postiz", "key": g}, "detail": {"texts": [y["text"] for _, y in xs]}})
    return out


# ---------------------------------------------------------------- the month

_collect_lock = threading.Lock()


def collect(month, jobs=(), drafts=False):
    """Every piece of the month in one shape (the README lists the fields). One month at a time: the month's Postiz list sits in
    the shared _LIVE while it is built, so two months built at once (the page loads a month and its neighbours) mixed their posts
    (11 Nov 2026: reel 7.1 lost its real 11:12 time and a posted carousel vanished)."""
    with _collect_lock:
        return _collect(month, jobs, drafts)


def _collect(month, jobs=(), drafts=False):
    if not re.match(r"^\d{4}-\d{2}$", month or ""):
        month = today()[:7]
    st = state()
    notices = []
    pieces = []
    hidden = []
    _LIVE["data"] = postiz_live(month)
    for fn in (lambda: kid_pieces(month, st, notices, drafts, hidden), lambda: test_pieces(month, st, notices) if SHOW_TEST else []):
        try:
            pieces += fn()
        except Exception as exc:  # noqa: BLE001 - one source failing never blanks the page
            notices.append(f"שגיאה בקריאת אחד המקורות: {exc}")
    try:
        reels, _ = reel_pieces(month, st, list(jobs))
        pieces += reels
        pieces += reminder_pieces(month, st, reels)
    except Exception as exc:  # noqa: BLE001
        notices.append(f"שגיאה בקריאת הרילס: {exc}")
    pieces += idea_pieces(month, st)
    try:
        pieces += stories.pieces(month, st)   # before postiz_only, so a set's Postiz posts are its own and not strays
    except Exception as exc:  # noqa: BLE001
        notices.append(f"שגיאה בקריאת הסטוריז: {exc}")
    try:
        pieces += seasonal.pieces(month, st)   # Black Friday and Hanukkah, two options a day (tools/seasonal.py)
    except Exception as exc:  # noqa: BLE001
        notices.append(f"שגיאה בקריאת קרוסלות החג: {exc}")
    pieces += postiz_only(month, pieces)
    if _LIVE["data"] is None and POSTIZ_CMD != "off":
        notices.append("בודק מול פוסטיז, מתעדכן בעוד רגע.")
    for p in pieces:
        p["status_he"] = STATUS_HE.get(p.get("status") or "", "")
        p["kind_he"] = KIND_HE.get(p["kind"], "")
    gap = int(hours().get("min_gap_minutes") or 180)
    by_day = {}
    for p in pieces:
        if p["kind"] in ("kid", "test", "reel", "post", "season") and p.get("time"):
            by_day.setdefault(p["date"], []).append(p)
    for day_pieces in by_day.values():
        day_pieces.sort(key=lambda p: p["time"])
        for prev, cur in zip(day_pieces, day_pieces[1:]):
            m = lambda t: int(t[:2]) * 60 + int(t[3:5])  # noqa: E731
            if cur["status"] != "posted" and 0 < m(cur["time"]) - m(prev["time"]) < gap:
                cur["flags"].append({"code": "gap", "he": f"פחות מ־{gap // 60} שעות אחרי הפוסט של {prev['time']}"})
    pieces.sort(key=lambda p: (p["date"], p.get("time") or "99:99", p["kind"]))
    hr = hours()
    body = {"month": month, "today": today(), "pieces": pieces, "notices": notices,
            "statuses": [{"code": c, "he": h} for c, h in STATUSES], "hours": hr,
            "targets": hr.get("targets") or {"carousel": 2, "reel": 2}, "hidden_drafts": len(hidden), "drafts": bool(drafts),
            "reels_defaults": reels_cfg((read_json(REELS_JSON, {}) or {}).get("defaults") or {}), "story_lib": stories.library(), "season_lib": seasonal.library()}
    blob = json.dumps(body, ensure_ascii=False, sort_keys=True)
    body["rev"] = hashlib.sha1(blob.encode("utf-8")).hexdigest()[:12]
    return body


# ---------------------------------------------------------------- moves (drag to reschedule)

def move(piece_id, to_date, to_time="keep"):
    """Drag to reschedule. A reel's date goes into reels.json (its own source); a carousel keeps its pack and file names (they
    carry the date) and the move is kept in calendar-state.json "moves", which the calendar's Postiz button sends at. A piece
    already scheduled in Postiz is never moved here: (409, ...) and Yarin decides in the page. Returns (status, body) with the
    old place for the undo."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", to_date or "") or (to_time not in (None, "keep") and not re.match(r"^\d{2}:\d{2}$", str(to_time))):
        return 400, {"error": "bad date or time"}
    if piece_id.startswith("st-"):   # a story set: its date and time live in series.json (tools/stories.py)
        return stories.move(piece_id, to_date, to_time)
    if piece_id.startswith("se-"):  # a Black Friday or Hanukkah day: its move lives in the seasonal folder's state.json
        return seasonal.move(piece_id, to_date, to_time)
    month = to_date[:7]
    with _lock:
        st = state()
        if piece_id.startswith("r-"):
            d = read_json(REELS_JSON)
            r = next((x for x in (d or {}).get("reels", []) if x["id"] == piece_id[2:]), None)
            if not r:
                return 404, {"error": "no such reel"}
            if r.get("status") == "posted":
                return 409, {"error": "posted", "he": "הריל כבר עלה"}
            old = {"date": r["date"], "time": (st["moves"].get(piece_id) or {}).get("time")}
            backup = REELS_JSON.with_name(REELS_JSON.stem + ".before-move.json")
            backup.write_text(REELS_JSON.read_text(encoding="utf-8"), encoding="utf-8")
            r["date"] = to_date
            REELS_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if to_time is None:      # back to the reel's default slot time (an undo)
                st["moves"].pop(piece_id, None)
            elif to_time != "keep":
                st["moves"][piece_id] = {"time": to_time, "at": now().isoformat(timespec="seconds")}
            write_json(STATE, st)
            _cache.pop("collect", None)
            return 200, {"ok": True, "undo": {"id": piece_id, **old}}
        if not re.match(r"^[kt]-\d{4}-\d{2}-\d{2}(-[abx])?$", piece_id or ""):
            return 400, {"error": "only reels and carousels move"}
        pz = carousel_postiz(piece_id)
        if pz and pz.get("status") == "schedule":   # in Postiz already: never moved from here (Yarin decides in that moment)
            return 409, {"error": "in_postiz", "he": "מתוזמן בפוסטיז: לשנות שם?", "postiz": pz}
        mv = st["moves"].get(piece_id) or {}
        old = {"date": mv.get("date"), "time": mv.get("time")}
        st["moves"][piece_id] = {"date": to_date, "time": mv.get("time") if to_time == "keep" else to_time, "at": now().isoformat(timespec="seconds")}
        write_json(STATE, st)
    _cache.pop("collect", None)
    return 200, {"ok": True, "undo": {"id": piece_id, **old}}


def carousel_postiz(piece_id):
    """The Postiz record of a carousel piece's production, if any (k-DATE-LANE or t-DATE)."""
    runs = runs_all()
    if piece_id.startswith("t-"):
        dt = piece_id[2:]
        keys = [f"{TEST_BATCH}/{dt}-a", f"{TEST_BATCH}/{dt}-b"]
    else:
        dt, lane = piece_id[2:12], piece_id[13:]
        keys = [k for k in runs if k.startswith(dt + "/") and LANE_OF.get(k.split("/", 1)[1], "x") == lane]
    for k in keys:
        pz = postiz_of(runs.get(k))
        if pz:
            return pz
    return None


# ---------------------------------------------------------------- reel commands (background, fixed recipes)

REELS_PY = _env_path("LUMEBOOK_REELS_PY", REELS_DIR / "reels.py")
GPT_PY = REELS_DIR / "reel_gpt.py"
_tasks = {}


def reel_env():
    env = dict(os.environ)
    return env


def reel_merge(reel_id):
    """reels.py merge local <id>, then lint: the hub's edits of this reel into reels.json. Returns (status, body)."""
    if not re.match(r"^\d+\.\d+$", reel_id or ""):
        return 400, {"error": "bad reel id"}
    m = subprocess.run([sys.executable, str(REELS_PY), "merge", "local", reel_id], cwd=ROOT, env=reel_env(),
                       capture_output=True, text=True, timeout=120)
    lint = subprocess.run([sys.executable, str(REELS_PY), "lint"], cwd=ROOT, env=reel_env(), capture_output=True, text=True, timeout=180)
    mine = [l for l in (lint.stdout + lint.stderr).splitlines() if f" {reel_id}:" in l or f" {reel_id} " in l]
    _cache.pop("collect", None)
    return 200, {"ok": m.returncode == 0, "merge": (m.stdout + m.stderr).strip()[-600:], "lint_ok": lint.returncode == 0,
                 "lint": mine[:12]}


def task_list():
    with _lock:
        return [dict(v, id=k) for k, v in _tasks.items()]


def _run_task(tid, cmd, shell_wrap=False, on_done=None):
    def go():
        t0 = time.time()
        try:
            if shell_wrap:   # the OpenAI key comes from ~/.zshrc (Keychain): run through zsh -ic, never print it
                full = ["zsh", "-ic", " ".join(_q(x) for x in cmd)]
            else:
                full = cmd
            p = subprocess.run(full, cwd=ROOT, env=reel_env(), capture_output=True, text=True, timeout=3600)
            tail = "\n".join(l for l in (p.stdout + p.stderr).strip().splitlines()[-8:] if "sk-" not in l and "OPENAI_API_KEY" not in l)
            ok = p.returncode == 0
        except Exception as exc:  # noqa: BLE001
            ok, tail = False, str(exc)
        with _lock:
            _tasks[tid].update(status="done" if ok else "failed", tail=tail, seconds=round(time.time() - t0, 1),
                               ended=now().isoformat(timespec="seconds"))
        if on_done:
            try:
                on_done(ok)
            except Exception:  # noqa: BLE001
                pass
        _cache.pop("collect", None)
    threading.Thread(target=go, daemon=True).start()


def _q(s):
    import shlex
    return shlex.quote(str(s))


def start_gpt(reel_id, budget, confirmed):
    """Yarin's budget and explicit yes for one reel's GPT pictures (reel_gpt.py run --max-usd --yes). Never without both."""
    if not re.match(r"^\d+\.\d+$", reel_id or ""):
        return 400, {"error": "bad reel id"}
    try:
        b = float(budget)
    except (TypeError, ValueError):
        return 400, {"error": "budget"}
    if confirmed is not True or not (0 < b <= 5):
        return 400, {"error": "a budget between 0 and 5 dollars and an explicit yes are required"}
    tid = f"gpt-{reel_id}"
    with _lock:
        if (_tasks.get(tid) or {}).get("status") == "running":
            return 409, {"error": "already running"}
        _tasks[tid] = {"kind": "gpt", "reel": reel_id, "status": "running", "budget_usd": b, "started": now().isoformat(timespec="seconds")}
    test_cmd = os.environ.get("LUMEBOOK_REEL_GPT_CMD")
    cmd = test_cmd.split() + [reel_id, str(b)] if test_cmd else [sys.executable, str(GPT_PY), "run", reel_id, "--max-usd", f"{b:.2f}", "--yes"]

    def done(ok):
        if ok:
            put_doc("gpt", reel_id, {"done": now().isoformat(timespec="seconds"), "budget_usd": b})
    _run_task(tid, cmd, shell_wrap=not test_cmd, on_done=done)
    return 202, {"task": dict(_tasks[tid], id=tid)}


def start_trials(reel_id):
    """The trial versions of a reel, only after its main version and its trial hooks were approved in the calendar."""
    if not re.match(r"^\d+\.\d+$", reel_id or ""):
        return 400, {"error": "bad reel id"}
    st = state()
    pid = "r-" + reel_id
    if not (st["approvals"].get(pid) or {}).get("main"):
        return 409, {"error": "approve the main version first", "he": "קודם לאשר את הגרסה הראשית"}
    hk = st["hooks"].get(pid) or {}
    trial = [hk["options"][i] for i in hk.get("trial") or [] if 0 <= i < len(hk.get("options") or [])]
    if len(trial) != 4:   # reel_make.py builds five versions: the main hook, then four trial hooks, all different
        return 409, {"error": "four trial hooks are needed", "he": "לסמן 4 הוקים לגרסאות הניסיון (יחד עם ההוק הראשי, חמש גרסאות)"}
    # the approved hooks go into reels.json trial_hooks through the hub's own edit documents and merge local
    hub = read_json(HUB_FILE, {}) or {}
    for c in ("edits", "made", "requests", "picks"):
        hub.setdefault(c, {})
    key = "r" + reel_id.replace(".", "-")
    for i in range(4):
        hub["edits"][f"{key}__trialhooks__{i}"] = {"key": f"{key}__trialhooks__{i}", "text": trial[i], "at": now().isoformat(timespec="seconds")}
    write_json(HUB_FILE, hub)
    reel_merge(reel_id)
    tid = f"trials-{reel_id}"
    with _lock:
        if (_tasks.get(tid) or {}).get("status") == "running":
            return 409, {"error": "already running"}
        _tasks[tid] = {"kind": "trials", "reel": reel_id, "status": "running", "started": now().isoformat(timespec="seconds")}
    test_cmd = os.environ.get("LUMEBOOK_TRIAL_CMD")
    cmd = test_cmd.split() + [reel_id] if test_cmd else [sys.executable, str(REELS_PY), "make", reel_id, "--trial-only"]

    def done(ok):
        if ok:
            put_doc("trials", reel_id, {"made_at": now().isoformat(timespec="seconds"), "hooks": trial})
    _run_task(tid, cmd, on_done=done)
    return 202, {"task": dict(_tasks[tid], id=tid)}


# ---------------------------------------------------------------- reels to Postiz (Yarin, 11 Nov 2026: "so connect it")

FB_LINK = "https://lumebook.com/IL/he?utm_source=facebook&utm_medium=social"   # as test_batch.py: the store link with Yarin's UTM


def reel_post_texts(tx, defaults):
    """The texts a reel goes out with: Instagram gets the caption, Facebook the caption without the comment-word line (a comment
    word needs Instagram comments) and the store link with the UTM, both ending with the short disclaimer (31 Oct 2026 rule).
    Yarin can edit both on the page before sending."""
    disc = (defaults or {}).get("caption_disclaimer", "")
    cap = (tx.get("caption") or "").strip()
    ig = cap + ("\n\n" + disc if disc else "")
    lines = [l for l in cap.split("\n") if "לומי" not in l]
    fb = "\n".join(lines).rstrip() + "\n\nלהכנת הספר 👇\n" + FB_LINK + ("\n\n" + disc if disc else "")
    return {"ig": ig, "fb": fb}


def pz_config():
    f = read_json(ROOT / "shared" / "facts.json", {}) or {}
    z = f.get("postiz") or {}
    return z.get("instagram"), z.get("facebook")


def pz_cli(*args, timeout=300):
    """postiz CLI with JSON out (as postiz_export._cli). RuntimeError with a short reason when it fails."""
    if POSTIZ_CMD == "off":
        raise RuntimeError("Postiz כבוי בהגדרות השרת")
    env = {**os.environ, "PATH": os.pathsep.join([str(Path(POSTIZ_CMD).parent), "/usr/local/bin", "/opt/homebrew/bin", "/usr/bin", "/bin"])}
    p = subprocess.run([POSTIZ_CMD, *args], capture_output=True, text=True, timeout=timeout, env=env)
    out = p.stdout.strip()
    if p.returncode != 0:
        raise RuntimeError("Postiz: " + (p.stderr or out).strip()[-400:])
    a = min([i for i in (out.find("{"), out.find("[")) if i >= 0] or [-1])
    if a < 0:
        raise RuntimeError("Postiz: תשובה לא צפויה: " + out[-200:])
    return json.loads(out[a:])


def pz_upload(path, tries=4):
    for n in range(tries):
        try:
            return pz_cli("upload", str(path))["path"]
        except RuntimeError as exc:
            if n == tries - 1 or "502" not in str(exc):
                raise
            time.sleep(15 * (n + 1))


def reel_videos(reel_id):
    """(main final, [trial versions]) of a reel, files that exist inside the project."""
    d = read_json(REELS_JSON, {}) or {}
    r = next((x for x in d.get("reels", []) if x["id"] == reel_id), None)
    if not r or not r.get("project"):
        return None, []
    folder = (ROOT / r["project"]).resolve()
    name = "reel-" + reel_id.replace(".", "-")
    main = folder / "final" / f"{name}-1.mp4"
    trials = sorted((folder / "trial").glob(f"{name}-trial-*.mp4")) if (folder / "trial").is_dir() else []
    roots = [ROOT.resolve()] + ([Path(os.environ["LUMEBOOK_TEST_MEDIA_ROOT"]).resolve()] if os.environ.get("LUMEBOOK_TEST_MEDIA_ROOT") else [])
    ok = lambda f: f.exists() and any(x in f.resolve().parents for x in roots)  # noqa: E731
    return (main if ok(main) else None), [t for t in trials if ok(t)]


def _when(date_s, time_s, draft):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_s or "") or not re.match(r"^\d{2}:\d{2}$", time_s or ""):
        raise ValueError("בחרו תאריך ושעה")
    t = datetime.fromisoformat(f"{date_s}T{time_s}:00").replace(tzinfo=IL)
    if not draft and t < now() + timedelta(minutes=5):
        raise ValueError("השעה שנבחרה כבר עברה או קרובה מדי. בחרו שעה מאוחרת יותר")
    return t


def send_reel(reel_id, kind, date_s, time_s, ig_text=None, fb_text=None, draft=False, trial_index=None, confirmed=False):
    """A reel to Postiz, only on Yarin's click (the page asks twice and shows the date, time and channels):
       kind "main": the approved final, Instagram and Facebook;
       kind "trials": every trial version not sent yet, Instagram only as trial reels (is_trial_reel, graduation MANUAL), 5 minutes apart;
       kind "fb_trial": one trial version (trial_index) to Facebook only, for the day after (Yarin: "also share it to fb").
    Records every send in calendar-state.json "postiz" and refuses a second send of the same thing (a second send would make a
    second post). Returns (status, body)."""
    if confirmed is not True:
        return 400, {"error": "confirmation needed", "he": "צריך לאשר את השליחה"}
    if not re.match(r"^\d+\.\d+$", reel_id or "") or kind not in ("main", "trials", "fb_trial"):
        return 400, {"error": "bad request"}
    ig, fb = pz_config()
    if not ig or not fb:
        return 500, {"error": "no Postiz channels in shared/facts.json"}
    st = state()
    rec = (st["postiz"].get(reel_id) or {})
    pid = "r-" + reel_id
    main, trials = reel_videos(reel_id)
    d = read_json(REELS_JSON, {}) or {}
    r = next((x for x in d.get("reels", []) if x["id"] == reel_id), None)
    if not r:
        return 404, {"error": "no such reel"}
    texts = reel_post_texts(reel_texts(r, (read_json(HUB_FILE, {}) or {}).get("edits") or {}), d.get("defaults"))
    ig_text = (ig_text or texts["ig"]).strip()
    fb_text = (fb_text or texts["fb"]).strip()
    for t in (ig_text, fb_text):
        if re.search(r"—|–|לומבוק", t):
            return 400, {"error": "text rules", "he": "בטקסט יש מקף ארוך או איות לא נכון של לומיבוק"}
    try:
        base = _when(date_s, time_s, draft)
        post_type = "draft" if draft else "schedule"

        def create(posts, when):
            body = {"type": post_type, "date": when.isoformat(), "shortLink": False, "tags": [], "posts": posts}
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump(body, f, ensure_ascii=False)
            try:
                res = pz_cli("posts:create", "--json", f.name)
            finally:
                os.unlink(f.name)
            return [x.get("postId") for x in (res if isinstance(res, list) else [res]) if isinstance(x, dict) and x.get("postId")]

        def vpost(channel, provider, text, url, settings):
            return {"integration": {"id": channel}, "value": [{"content": text, "image": [{"id": "v01", "path": url}]}],
                    "settings": {"__type": provider, **settings}}

        if kind == "main":
            if (rec.get("main") or {}).get("ids"):
                return 409, {"error": "already sent", "he": "הריל הראשי כבר נשלח לפוסטיז. שינוי שם רק באישור שלך"}
            if not (st["approvals"].get(pid) or {}).get("main"):
                return 409, {"error": "approve first", "he": "קודם לאשר את הגרסה הראשית"}
            if not main:
                return 409, {"error": "no final", "he": "אין עדיין קובץ ריל מוכן"}
            url = pz_upload(main)
            ids = create([vpost(ig, "instagram", ig_text, url, {"post_type": "post"}),
                          vpost(fb, "facebook", fb_text, url, {"post_type": "post"})], base)
            rec["main"] = {"ids": ids, "date": base.isoformat(), "status": post_type, "media": url, "sent_at": now().isoformat(timespec="seconds")}
            out = {"sent": 1, "ids": ids}
        elif kind == "trials":
            if not (st["approvals"].get(pid) or {}).get("main"):
                return 409, {"error": "approve first", "he": "גרסאות ניסיון נשלחות רק אחרי שהגרסה הראשית אושרה"}
            done = rec.setdefault("trials", {})
            todo = [t for t in trials if t.name not in done]
            if not todo:
                return 409, {"error": "nothing to send", "he": "אין גרסאות ניסיון חדשות לשלוח"}
            n = 0
            for i, t in enumerate(todo):
                when = base + timedelta(minutes=5 * i)
                url = pz_upload(t)
                ids = create([vpost(ig, "instagram", ig_text, url, {"post_type": "post", "is_trial_reel": True, "graduation_strategy": "MANUAL"})], when)
                done[t.name] = {"ids": ids, "date": when.isoformat(), "status": post_type, "media": url, "sent_at": now().isoformat(timespec="seconds")}
                n += 1
                st["postiz"][reel_id] = rec
                write_json(STATE, {**state(), "postiz": {**state()["postiz"], reel_id: rec}})   # kept after each one: a failure midway loses none
            out = {"sent": n}
        else:   # fb_trial: one trial version to Facebook, a normal Facebook video post
            if trial_index is None or not (0 <= int(trial_index) < len(trials)):
                return 400, {"error": "which trial"}
            t = trials[int(trial_index)]
            fbd = rec.setdefault("fb_trials", {})
            if t.name in fbd:
                return 409, {"error": "already sent", "he": "הגרסה הזאת כבר נשלחה לפייסבוק"}
            url = pz_upload(t)
            ids = create([vpost(fb, "facebook", fb_text, url, {"post_type": "post"})], base)
            fbd[t.name] = {"ids": ids, "date": base.isoformat(), "status": post_type, "media": url, "sent_at": now().isoformat(timespec="seconds")}
            out = {"sent": 1, "ids": ids}
    except ValueError as exc:
        return 400, {"error": str(exc), "he": str(exc)}
    except RuntimeError as exc:
        return 502, {"error": str(exc), "he": str(exc)}
    with _lock:
        s2 = state()
        s2["postiz"][reel_id] = rec
        write_json(STATE, s2)
    _cache.pop("collect", None)
    _LIVE["data"] = None
    _pz_live.clear()
    return 200, out


# ---------------------------------------------------------------- Postiz per-post numbers (for the hours analysis)

def postiz_stats(days=60):
    """The numbers Postiz keeps for every post it published (postiz analytics:post, read only) into postiz-stats.json: per post its
    channel, publish time (Israel) and the totals. Works for what went out through Postiz (from late October), Facebook included;
    older posts need Meta's own export."""
    now_ = now()
    start = (now_ - timedelta(days=days)).date().isoformat() + "T00:00:00Z"
    end = (now_ + timedelta(days=1)).date().isoformat() + "T00:00:00Z"
    listed = pz_cli("posts:list", "--startDate", start, "--endDate", end)
    posts = listed.get("posts", listed) if isinstance(listed, dict) else listed
    out = []
    for x in posts:
        if x.get("state") != "PUBLISHED":
            continue
        integ = x.get("integration")
        prov = integ.get("providerIdentifier", "") if isinstance(integ, dict) else str(integ)
        try:
            res = pz_cli("analytics:post", x["id"], "-d", str(days))
        except RuntimeError as exc:
            res = []
            print("skip", x["id"], exc)
        tot = {}
        for m in res if isinstance(res, list) else []:
            vals = [float(d.get("total") or 0) for d in m.get("data", [])]
            tot[m.get("label")] = sum(vals)
        t = datetime.fromisoformat(x["publishDate"].replace("Z", "+00:00")).astimezone(IL)
        out.append({"id": x["id"], "channel": "ig" if "instagram" in prov else "fb" if "facebook" in prov else prov,
                    "posted_local": t.isoformat(timespec="minutes"), "text": (x.get("content") or "").split("\n")[0][:80], "totals": tot})
    write_json(SITE / "postiz-stats.json", {"as_of": now_.isoformat(timespec="minutes"), "days": days, "posts": out})
    for o in sorted(out, key=lambda o: o["posted_local"]):
        print(o["posted_local"][:16], o["channel"], o["totals"], o["text"][:40])
    print(len(out), "published posts ->", (SITE / "postiz-stats.json").relative_to(ROOT))


# ---------------------------------------------------------------- posting hours from the stats

def hours_cmd(exports):
    """Import the given Meta exports into the carousel audit (its importer converts US Pacific to Israel time and takes Yarin's own
    like and save off each post), then compare posts by hour block and weekday, per kind. Writes the suggestion and the evidence
    into posting-hours.json (approved stays false until Yarin says so); prints the result in plain words."""
    audit = ROOT / "research" / "carousel-audit" / "src" / "audit.py"
    for e in exports:
        r = subprocess.run([sys.executable, str(audit), "import", e], cwd=ROOT, capture_output=True, text=True)
        print((r.stdout + r.stderr).strip()[-400:])
    posts = (read_json(ROOT / "research" / "carousel-audit" / "data" / "posts.json", {}) or {}).get("posts", {})
    rows = [p for p in posts.values() if p.get("username") in (None, "lumebook.il") and p.get("posted_local") and p.get("latest")]
    blocks = [(5, 9), (9, 12), (12, 15), (15, 18), (18, 20), (20, 22), (22, 24)]
    days_he = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]
    result = {}
    lines = []
    for kind in ("carousel", "reel"):
        ps = [p for p in rows if p.get("type") == kind]
        by = {}
        for p in ps:
            h = int(p["posted_local"][11:13])
            b = next((f"{a:02d}-{z:02d}" for a, z in blocks if a <= h < z), "00-05")
            by.setdefault(b, []).append(p)
        stats = []
        for b, group in sorted(by.items()):
            def med(k):
                vals = [x["latest"].get(k) or 0 for x in group]
                return round(statistics.median(vals), 1) if vals else 0
            times = sorted(x["posted_local"][11:16] for x in group)
            stats.append({"block": b, "n": len(group), "reach": med("reach"), "views": med("views"), "saves": med("saves"),
                          "shares": med("shares"), "comments": med("comments"), "follows": med("follows"),
                          "typical_time": times[len(times) // 2], "few": len(group) < 4})
        trusted = [s for s in stats if not s["few"]]
        best = sorted(trusted, key=lambda s: (s["reach"], s["saves"] + s["shares"]), reverse=True)[:3]
        wd = {}
        for p in ps:
            wd.setdefault(days_he[datetime.fromisoformat(p["posted_local"]).weekday()], []).append(p["latest"].get("reach") or 0)
        result[kind] = {"n": len(ps), "blocks": stats, "best": best,
                        "weekdays": {k: {"n": len(v), "reach": round(statistics.median(v), 1)} for k, v in wd.items()}}
        lines.append(f"{kind}: {len(ps)} posts")
        for s in stats:
            lines.append(f"  {s['block']}: {s['n']} posts, median reach {s['reach']}, saves {s['saves']}, shares {s['shares']}"
                         + ("  (too few to trust)" if s["few"] else ""))
        lines.append("  best: " + (", ".join(f"{s['block']} (n={s['n']})" for s in best) or "no block has 4 or more posts yet"))
    hr = hours()
    span = sorted(p["posted_local"][:10] for p in rows)
    hr["suggested"] = {k: [{"time": s["typical_time"], "block": s["block"], "n": s["n"],
                            "why": f"חציון תפוצה {s['reach']:g} ב-{s['block'].replace('-', ':00 עד ')}:00, {s['n']} פוסטים"} for s in v["best"]]
                       for k, v in result.items()}
    hr["stats"] = {"as_of": now().isoformat(timespec="minutes"), "posts": len(rows), "from": span[0] if span else None,
                   "to": span[-1] if span else None, "source": "research/carousel-audit/data/posts.json", "by_kind": result}
    hours_seen = sorted({p["posted_local"][11:13] for p in rows})
    hr["stats"]["hours_seen"] = hours_seen
    hr["stats"]["note"] = ("Only hour blocks with 4 or more posts are suggested. Hours with no post in the data cannot be judged: "
                           + ", ".join(h for h in ("06", "20", "21") if h not in hours_seen) + " (the current slots) have none." if any(
                               h not in hours_seen for h in ("06", "20", "21")) else "")
    hr.setdefault("approved", False)
    write_json(HOURS, hr)
    print("\n".join(lines))
    print(f"\nwritten to {HOURS.relative_to(ROOT)} (suggested; approved: {hr['approved']})")


def main():
    cmd, *args = sys.argv[1:] or ["month"]
    if cmd == "month":
        body = collect(args[0] if args else today()[:7])
        for n in body["notices"]:
            print("!", n)
        for p in body["pieces"]:
            print(p["date"], p.get("time") or "--:--", p["kind"].ljust(6), (p.get("status") or "").ljust(9), p["id"].ljust(20), (p.get("title") or "")[:40])
        print(len(body["pieces"]), "pieces, rev", body["rev"])
    elif cmd == "hours":
        hours_cmd(args)
    elif cmd == "postiz-stats":
        postiz_stats(int(args[0]) if args else 60)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
