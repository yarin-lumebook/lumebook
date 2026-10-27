"""Swap the text of the scheduled trial reels (postiz-trial.json) for the current <reel>-description.txt.

The postiz CLI cannot edit a post's text, so each post is created again with the same video, date and settings,
and the old one is deleted only after the new one exists. 26 Oct 2026: the link in bio CTA was added this way.
"""
import json, os, sys, tempfile
from pathlib import Path

sys.path.insert(0, "/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts")
import postiz_export as px  # _cli

CAP = Path(__file__).resolve().parent
IG = json.load(open(CAP.parents[3] / "shared/facts.json"))["postiz"]["instagram"]
REC = CAP / "postiz-trial.json"

record = json.loads(REC.read_text())
for k, (name, r) in enumerate(record.items(), 1):
    text = (CAP / f"{name.rsplit('-caption-', 1)[0]}-description.txt").read_text(encoding="utf-8").strip()
    if r.get("text") == text:
        print(f"PROGRESS {k}/{len(record)} {name} already has this text", flush=True)
        continue
    old = r["result"][0]["postId"]
    body = {"type": "schedule", "date": r["date"], "shortLink": False, "tags": [],
            "posts": [{"integration": {"id": IG},
                       "value": [{"content": text, "image": [{"id": "v01", "path": r["media"]}]}],
                       "settings": {"__type": "instagram", "post_type": "post",
                                    "is_trial_reel": True, "graduation_strategy": "MANUAL"}}]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False)
    try:
        created = px._cli("posts:create", "--json", f.name)
    finally:
        os.unlink(f.name)
    r.update(result=created, text=text, replaced=r.get("replaced", []) + [old])
    REC.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        px._cli("posts:delete", old)
    except RuntimeError as exc:  # posts:delete answers in plain text, not JSON
        if "deleted successfully" not in str(exc):
            raise
    print(f"PROGRESS {k}/{len(record)} {name} replaced ({old} deleted)", flush=True)
