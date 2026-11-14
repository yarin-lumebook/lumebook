"""The content experiment log of the MeBook customer study (14 Nov 2026).

Yarin asked for "a practical content experiment log ... integrated with the existing Research and Purchase Intents sections":
every experiment starts from a research finding, a content hypothesis or a purchase intent of
research/mebook-customer-research, carries a hypothesis, the content it tested, manually entered results and a learning.

Storage: one JSON file, research/mebook-customer-research/experiments.json ({"experiments": {id: doc}}), in git so the
nightly commit keeps it. The project server reads and writes it (tools/lumebook.py serve):

    GET /api/experiments                 {"experiments": {...}}
    PUT /api/experiments/doc?id=<id>     one experiment (same-origin only); answers {"ok": true, "doc": <as saved>}

LUMEBOOK_EXPERIMENTS_FILE points a test server on a spare port at a scratch file. No external service, no API call: results
are typed in by hand. Every number is either a number or null (not measured); null is never turned into 0.
"""
import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = Path(os.environ.get("LUMEBOOK_EXPERIMENTS_FILE") or ROOT / "research/mebook-customer-research/experiments.json")

STATUSES = ("idea", "ready", "running", "completed", "archived")
CONCLUSIONS = ("promising", "inconclusive", "not_supported")
MODES = ("organic", "paid")
ID_RE = re.compile(r"^[a-z0-9]{6,24}$")
LINK_RE = re.compile(r"^(intent:\d{1,3}|finding:[a-z0-9-]{1,40}|hyp:H\d{1,2})$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TEXT = {   # field: max length
    "title": 200, "hypothesis": 2000, "audience": 600, "motivation": 1000, "hook": 600, "proof": 1000, "cta": 400,
    "format": 120, "channel": 120, "content_url": 600, "data_source": 300, "period": 200, "attribution_notes": 2000,
    "explanation": 4000, "next": 2000,
}
NUMBERS = ("impressions", "views", "clicks", "visits", "purchases", "revenue", "spend")
TRACKING = ("url", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
MAX_FILE = 4 * 1024 * 1024
_lock = threading.Lock()


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load(path=None):
    """{"experiments": {id: doc}}; an empty log when the file is missing or broken (never raises)."""
    try:
        data = json.loads(Path(path or FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict) or not isinstance(data.get("experiments"), dict):
        data = {"experiments": {}}
    return data


def _write(path, data):
    path = Path(path)
    out = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if len(out.encode("utf-8")) > MAX_FILE:
        raise ValueError("the experiments file would be over 4 MB")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(out, encoding="utf-8")
    os.replace(tmp, path)


def _number(v):
    """A non-negative number, or None for 'not measured'. '' and None stay None; 0 stays 0."""
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        raise ValueError("a number, not true or false")
    if isinstance(v, str):
        v = v.strip().replace(",", "")
        if v == "":
            return None
        v = float(v)
    if not isinstance(v, (int, float)) or v != v or v in (float("inf"), float("-inf")):
        raise ValueError("not a number")
    if v < 0:
        raise ValueError("negative")
    return int(v) if float(v).is_integer() else float(v)


def clean(doc, exp_id):
    """The experiment as it will be stored, or raises ValueError with a message the page can show."""
    if not isinstance(doc, dict):
        raise ValueError("an experiment is a JSON object")
    out = {"id": exp_id}
    for k, n in TEXT.items():
        v = doc.get(k, "")
        if v is None:
            v = ""
        if not isinstance(v, str):
            raise ValueError(f"{k}: text expected")
        v = v.strip()
        if len(v) > n:
            raise ValueError(f"{k}: longer than {n} characters")
        out[k] = v
    if not out["title"]:
        raise ValueError("title is required")
    if not out["hypothesis"]:
        raise ValueError("hypothesis is required")
    links = doc.get("links") or []
    if not isinstance(links, list) or len(links) > 50 or not all(isinstance(x, str) and LINK_RE.match(x) for x in links):
        raise ValueError("links: a list of intent:N, finding:id or hyp:HN")
    out["links"] = list(dict.fromkeys(links))
    mode = doc.get("mode") or ""
    if mode not in MODES + ("",):
        raise ValueError("mode: organic or paid")
    out["mode"] = mode
    status = doc.get("status") or "idea"
    if status not in STATUSES:
        raise ValueError("status: " + ", ".join(STATUSES))
    out["status"] = status
    for k in ("start", "end"):
        v = doc.get(k) or ""
        if v and not DATE_RE.match(v):
            raise ValueError(f"{k}: a date YYYY-MM-DD")
        out[k] = v
    if out["start"] and out["end"] and out["end"] < out["start"]:
        raise ValueError("end is before start")
    res = doc.get("results") or {}
    if not isinstance(res, dict):
        raise ValueError("results: an object")
    out["results"] = {}
    for k in NUMBERS:
        try:
            out["results"][k] = _number(res.get(k))
        except (ValueError, TypeError) as e:
            raise ValueError(f"results.{k}: {e}")
    if out["mode"] != "paid" and out["results"]["spend"] not in (None, 0):
        raise ValueError("ad spend belongs to a paid experiment")
    tr = doc.get("tracking") or {}
    if not isinstance(tr, dict):
        raise ValueError("tracking: an object")
    out["tracking"] = {}
    for k in TRACKING:
        v = tr.get(k) or ""
        if not isinstance(v, str) or len(v) > 600:
            raise ValueError(f"tracking.{k}: text up to 600 characters")
        out["tracking"][k] = v.strip()
    concl = doc.get("conclusion") or ""
    if concl not in CONCLUSIONS + ("",):
        raise ValueError("conclusion: " + ", ".join(CONCLUSIONS))
    out["conclusion"] = concl
    if out["status"] == "completed" and not (out["conclusion"] and out["explanation"]):
        raise ValueError("a completed experiment needs a conclusion and an explanation")
    prev = doc.get("prev") or ""
    if prev and not ID_RE.match(prev):
        raise ValueError("prev: an experiment id")
    if prev == exp_id:
        raise ValueError("an experiment cannot follow itself")
    out["prev"] = prev
    return out


def put(exp_id, doc, path=None):
    """Save one experiment. Returns (status, body) like the other stores of the project server."""
    if not ID_RE.match(exp_id or ""):
        return 400, {"error": "bad id"}
    try:
        new = clean(doc, exp_id)
    except (ValueError, TypeError) as e:
        return 400, {"error": str(e)}
    path = path or FILE
    with _lock:
        data = load(path)
        old = data["experiments"].get(exp_id) or {}
        if new["prev"] and new["prev"] not in data["experiments"]:
            return 400, {"error": "prev: no such experiment"}
        new["created"] = old.get("created") or now()
        new["updated"] = now()
        data["experiments"][exp_id] = new
        data["_about"] = ("Content experiments of the MeBook customer study (tools/experiments.py, "
                          "research/mebook-customer-research/README.md). Results are typed in by hand; null means not measured.")
        try:
            _write(path, data)
        except ValueError as e:
            return 413, {"error": str(e)}
    return 200, {"ok": True, "doc": new}
