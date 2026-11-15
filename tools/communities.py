"""The Facebook community tracker's saved work (15 Nov 2026, creators/community-tracker).

Yarin asked for "a combined tool like the ugc creator map to track the parent facebook communities and ugc creators facebook
communities posts and leads (take the groups from the researches we made)". The groups themselves come from
research/parent-community/data.json and are built into the page; this file keeps only what Yarin does with them:

    groups/<gid>    a group's tracking: status, dates, next step, notes (and the fields of a group added by hand, `custom`)
    posts/<pid>     a post in a group: date, link, which text, state, reactions, comments, shares
    leads/<lid>     a person who answered: a family (parents track) or a creator (UGC track), contact, status, next step
    settings/main   the message texts to copy, per track

Storage: one JSON file, creators/community-tracker/state/tracker.json ({"groups": {}, "posts": {}, "leads": {}, "settings": {}}).
It holds names and phone numbers of parents, so it is private and not in git (.gitignore); the first save of every day also
keeps a copy in state/backup/ (the last 21 days). The project server reads and writes it (tools/lumebook.py serve):

    GET /api/communities/state                 the whole file
    PUT /api/communities/doc?path=<kind>/<id>  one document, checked by clean() (same-origin only); the body null removes it

LUMEBOOK_COMMUNITIES_FILE points a test server on a spare port at a scratch file. Numbers are a number or null (not counted);
null never turns into 0.
"""
import json
import os
import re
import shutil
import threading
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = Path(os.environ.get("LUMEBOOK_COMMUNITIES_FILE") or ROOT / "creators/community-tracker/state/tracker.json")

KINDS = ("groups", "posts", "leads", "settings")
GROUP_STATUS = ("new", "join", "member", "admin", "ok", "active", "later", "no")
LEAD_STATUS = ("new", "contacted", "replied", "qualified", "booked", "done", "no")
POST_STATE = ("pending", "live", "declined", "removed")
CHANNELS = ("comment", "dm", "whatsapp", "form", "email", "other")
TRACKS = ("parent", "ugc")
PRIVACY = ("", "Public", "Private")
ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_FILE = 8 * 1024 * 1024
BACKUP_DAYS = 21
_lock = threading.Lock()


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def empty():
    return {"groups": {}, "posts": {}, "leads": {}, "settings": {}}


def load(path=None):
    """The whole file; an empty tracker when it is missing or broken (never raises)."""
    try:
        data = json.loads(Path(path or FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    out = empty()
    for k in KINDS:
        if isinstance(data.get(k), dict):
            out[k] = data[k]
    return out


def _backup(path):
    """The first save of the day keeps yesterday's file in state/backup/ (21 days kept)."""
    path = Path(path)
    if not path.exists():
        return
    folder = path.parent / "backup"
    day = datetime.now().date().isoformat()
    target = folder / f"{path.stem}-{day}.json"
    if target.exists():
        return
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    for old in sorted(folder.glob(f"{path.stem}-*.json"))[:-BACKUP_DAYS]:
        old.unlink()


def _write(path, data):
    path = Path(path)
    out = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if len(out.encode("utf-8")) > MAX_FILE:
        raise ValueError("the tracker file would be over 8 MB")
    path.parent.mkdir(parents=True, exist_ok=True)
    _backup(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(out, encoding="utf-8")
    os.replace(tmp, path)


# ---- field checks -------------------------------------------------------------------------------------------------------

def _text(doc, key, n, required=False):
    v = doc.get(key, "")
    if v is None:
        v = ""
    if not isinstance(v, str):
        raise ValueError(f"{key}: text expected")
    v = v.strip()
    if len(v) > n:
        raise ValueError(f"{key}: longer than {n} characters")
    if required and not v:
        raise ValueError(f"{key} is required")
    return v


def _date(doc, key, required=False):
    v = doc.get(key) or ""
    if not isinstance(v, str) or (v and not DATE_RE.match(v)):
        raise ValueError(f"{key}: a date YYYY-MM-DD")
    if required and not v:
        raise ValueError(f"{key} is required")
    return v


def _choice(doc, key, allowed, default):
    v = doc.get(key) or default
    if v not in allowed:
        raise ValueError(f"{key}: one of " + ", ".join(a for a in allowed if a))
    return v


def _number(doc, key):
    """A non-negative whole number, or None for 'not counted'. '' and None stay None; 0 stays 0."""
    v = doc.get(key)
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        raise ValueError(f"{key}: a number")
    if isinstance(v, str):
        v = v.strip().replace(",", "")
        if v == "":
            return None
        try:
            v = float(v)
        except ValueError:
            raise ValueError(f"{key}: a number")
    if not isinstance(v, (int, float)) or v != v or v < 0 or v > 10_000_000:
        raise ValueError(f"{key}: a number from 0")
    return int(v)


def _url(doc, key):
    v = _text(doc, key, 600)
    if v and not re.match(r"^https?://", v):
        raise ValueError(f"{key}: a link that starts with https://")
    return v


def _log(doc, key="notes", max_items=400):
    items = doc.get(key) or []
    if not isinstance(items, list) or len(items) > max_items:
        raise ValueError(f"{key}: a list of up to {max_items}")
    out = []
    for it in items:
        if not isinstance(it, dict):
            raise ValueError(f"{key}: each item is an object")
        t = it.get("t")
        at = it.get("at") or ""
        if not isinstance(t, str) or not t.strip() or len(t) > 2000:
            raise ValueError(f"{key}: text of up to 2000 characters")
        if not isinstance(at, str) or len(at) > 40:
            raise ValueError(f"{key}: bad time")
        out.append({"at": at, "t": t.strip()})
    return out


def _ref(doc, key, required=False):
    v = doc.get(key) or ""
    if not isinstance(v, str) or (v and not ID_RE.match(v)):
        raise ValueError(f"{key}: an id")
    if required and not v:
        raise ValueError(f"{key} is required")
    return v


# ---- one document per kind ----------------------------------------------------------------------------------------------

def clean_group(doc):
    out = {
        "status": _choice(doc, "status", GROUP_STATUS, "new"),
        "next_on": _date(doc, "next_on"),
        "next_note": _text(doc, "next_note", 300),
        "joined_on": _date(doc, "joined_on"),
        "asked_on": _date(doc, "asked_on"),
        "ok_on": _date(doc, "ok_on"),
        "post_day": _text(doc, "post_day", 120),
        "notes": _log(doc),
    }
    custom = doc.get("custom")
    if custom is not None:
        if not isinstance(custom, dict):
            raise ValueError("custom: an object")
        out["custom"] = {
            "name": _text(custom, "name", 200, required=True),
            "url": _url(custom, "url"),
            "track": _choice(custom, "track", TRACKS, "parent"),
            "geo": _text(custom, "geo", 80),
            "members_n": _number(custom, "members_n"),
            "privacy": _choice(custom, "privacy", PRIVACY, ""),
            "policy": _text(custom, "policy", 1000),
        }
    return out


def clean_post(doc):
    out = {
        "gid": _ref(doc, "gid", required=True),
        "on": _date(doc, "on", required=True),
        "url": _url(doc, "url"),
        "template": _text(doc, "template", 120),
        "text": _text(doc, "text", 8000),
        "state": _choice(doc, "state", POST_STATE, "live"),
        "reactions": _number(doc, "reactions"),
        "comments": _number(doc, "comments"),
        "shares": _number(doc, "shares"),
        "checked_on": _date(doc, "checked_on"),
        "note": _text(doc, "note", 2000),
    }
    return out


def clean_lead(doc):
    out = {
        "gid": _ref(doc, "gid", required=True),
        "pid": _ref(doc, "pid"),
        "track": _choice(doc, "track", TRACKS, "parent"),
        "name": _text(doc, "name", 120, required=True),
        "channel": _choice(doc, "channel", CHANNELS, "comment"),
        "status": _choice(doc, "status", LEAD_STATUS, "new"),
        "fb": _url(doc, "fb"),
        "ig": _text(doc, "ig", 60).lstrip("@"),
        "phone": _text(doc, "phone", 40),
        "email": _text(doc, "email", 160),
        "city": _text(doc, "city", 80),
        "kids": _text(doc, "kids", 300),
        "next_on": _date(doc, "next_on"),
        "next_note": _text(doc, "next_note", 300),
        "note": _text(doc, "note", 4000),
        "on": _date(doc, "on"),
        "log": _log(doc, "log"),
    }
    if out["ig"] and not re.match(r"^[A-Za-z0-9._]{1,30}$", out["ig"]):
        raise ValueError("ig: an Instagram handle (letters, numbers, dot, underscore)")
    if out["phone"] and not re.match(r"^[0-9+\-() ]{6,40}$", out["phone"]):
        raise ValueError("phone: digits, spaces, + - ( ) only")
    return out


def clean_settings(doc):
    tpl = doc.get("templates") or {}
    if not isinstance(tpl, dict):
        raise ValueError("templates: an object")
    out = {"templates": {}}
    for track in TRACKS:
        items = tpl.get(track) or []
        if not isinstance(items, list) or len(items) > 40:
            raise ValueError(f"templates.{track}: a list of up to 40")
        clean = []
        for it in items:
            if not isinstance(it, dict):
                raise ValueError("a template is an object")
            tid = _ref(it, "id", required=True)
            clean.append({"id": tid, "title": _text(it, "title", 120, required=True), "text": _text(it, "text", 8000),
                          "kind": _choice(it, "kind", ("post", "admin", "dm", "other"), "post")})
        out["templates"][track] = clean
    return out


CLEAN = {"groups": clean_group, "posts": clean_post, "leads": clean_lead, "settings": clean_settings}
RESEARCH = ROOT / "research/parent-community/data.json"
_research = {"mtime": None, "ids": frozenset()}


def research_ids():
    """The ids of the research's Facebook groups (re-read when data.json changes)."""
    try:
        mt = RESEARCH.stat().st_mtime
    except OSError:
        return _research["ids"]
    if _research["mtime"] != mt:
        try:
            rows = json.loads(RESEARCH.read_text(encoding="utf-8")).get("rows") or []
            _research["ids"] = frozenset(str(r.get("id")) for r in rows if r.get("platform") == "Facebook group" and r.get("id"))
            _research["mtime"] = mt
        except (OSError, ValueError):
            pass
    return _research["ids"]


def known_group(gid, data):
    return gid in research_ids() or "custom" in (data["groups"].get(gid) or {})


def put(path_str, doc, path=None):
    """Save (or, with doc None, remove) one document. Returns (status, body) like the project server's other stores."""
    m = re.match(r"^(groups|posts|leads|settings)/([A-Za-z0-9._-]{1,80})$", path_str or "")
    if not m:
        return 400, {"error": "bad path"}
    kind, doc_id = m.groups()
    if kind == "settings" and doc_id != "main":
        return 400, {"error": "settings/main only"}
    path = path or FILE
    with _lock:
        data = load(path)
        if doc is None:
            data[kind].pop(doc_id, None)
            new = None
        else:
            if not isinstance(doc, dict):
                return 400, {"error": "a document is a JSON object"}
            try:
                new = CLEAN[kind](doc)
            except (ValueError, TypeError) as e:
                return 400, {"error": str(e)}
            old = data[kind].get(doc_id) or {}
            if kind in ("posts", "leads") and not known_group(new["gid"], data):
                return 400, {"error": "no such group"}
            if kind == "groups" and doc_id not in research_ids() and "custom" not in new:
                return 400, {"error": "a group that is not in the research needs its own details (custom)"}
            if kind == "leads" and new["pid"] and new["pid"] not in data["posts"]:
                return 400, {"error": "no such post"}
            new["created"] = old.get("created") or now()
            new["updated"] = now()
            data[kind][doc_id] = new
        data["_about"] = ("The Facebook community tracker's saved work (tools/communities.py, creators/community-tracker/README.md). "
                          "Private: names and phone numbers of parents. Not in git.")
        try:
            _write(path, data)
        except ValueError as e:
            return 413, {"error": str(e)}
    return 200, {"ok": True, "doc": new}
