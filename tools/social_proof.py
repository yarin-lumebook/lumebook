"""Removed cards of the social proof page (15 Nov 2026).

Yarin: "i need a way to delete irrelevant cards so you wont use them in the future when i ask you to use media from there".
A card removed on media/projects/2026-11-15-social-proof/social-proof.html is recorded here, never deleted from disk
(project rule: nothing is deleted). Whoever picks media from that page, folder or data.json for a reel, carousel or post must
skip every key listed in removed.json.

Storage: media/projects/2026-11-15-social-proof/removed.json, {"removed": {key: {"at": ISO time, "label": text}}}.
Keys: "review:<id>" for a review or comment, "kid:<file name>" for a photo or video of a child.

    GET /api/social-proof/removed             {"removed": {...}}
    PUT /api/social-proof/removed             body {"key": ..., "removed": true|false, "label": ...} (same-origin only)

LUMEBOOK_SOCIAL_PROOF_REMOVED points a test server on a spare port at a scratch file.
"""
import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = Path(os.environ.get("LUMEBOOK_SOCIAL_PROOF_REMOVED") or ROOT / "media/projects/2026-11-15-social-proof/removed.json")
KEY_RE = re.compile(r"^(review|kid):[^\s/\\][^/\\]{0,200}$")
_lock = threading.Lock()


def load(path=None):
    try:
        data = json.loads(Path(path or FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict) or not isinstance(data.get("removed"), dict):
        data = {"removed": {}}
    return data


def put(doc, path=None):
    """Mark a card removed or bring it back. Returns (status, body)."""
    if not isinstance(doc, dict):
        return 400, {"error": "a JSON object"}
    key, gone = doc.get("key"), doc.get("removed")
    if not isinstance(key, str) or not KEY_RE.match(key) or not isinstance(gone, bool):
        return 400, {"error": "key (review:ID or kid:FILE) and removed (true or false) are required"}
    label = doc.get("label") if isinstance(doc.get("label"), str) else ""
    path = Path(path or FILE)
    with _lock:
        data = load(path)
        if gone:
            data["removed"][key] = {"at": datetime.now().astimezone().isoformat(timespec="seconds"), "label": label[:200]}
        else:
            data["removed"].pop(key, None)
        data["_about"] = ("Cards removed on the social proof page by Yarin (tools/social_proof.py). Never use these when picking "
                          "media from that page, its folders or data.json. Nothing is deleted from disk.")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    return 200, {"ok": True, "removed": data["removed"]}
