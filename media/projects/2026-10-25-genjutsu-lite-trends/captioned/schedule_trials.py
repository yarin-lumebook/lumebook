"""Schedule the 26 Oct captioned reels as Instagram trial reels, Tue 27 to Thu 29 Oct 2026, 15:00 Israel, 5 min apart."""
import datetime as dt, json, sys, tempfile, os
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, "/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts")
import postiz_export as px  # _cli, _upload with 502 retry

CAP = Path("/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-25-genjutsu-lite-trends/captioned")
IG = json.load(open("/Users/yarinbruner/Claude/Projects/Lumebook/shared/facts.json"))["postiz"]["instagram"]
TZ = ZoneInfo("Asia/Jerusalem")
DAYS = [("03-mom-fridge", 3, dt.date(2026, 10, 27)), ("04-lume-books-dance", 3, dt.date(2026, 10, 28)),
        ("05-ben-lume-dance", 5, dt.date(2026, 10, 29))]
DRY = "--dry-run" in sys.argv
REC = CAP / "postiz-trial.json"

jobs = []
for reel, n, day in DAYS:
    text = (CAP / f"{reel}-description.txt").read_text(encoding="utf-8").strip()
    for i in range(1, n + 1):
        when = dt.datetime.combine(day, dt.time(15, 0), TZ) + dt.timedelta(minutes=5 * (i - 1))
        jobs.append((CAP / f"{reel}-caption-{i}.mp4", text, when))

record = json.loads(REC.read_text()) if REC.exists() else {}
for k, (video, text, when) in enumerate(jobs, 1):
    if video.name in record and record[video.name].get("result"):
        print(f"PROGRESS {k}/{len(jobs)} {video.name} already scheduled", flush=True)
        continue
    path = "<upload>" if DRY else px._upload(video)
    body = {"type": "schedule", "date": when.isoformat(), "shortLink": False, "tags": [],
            "posts": [{"integration": {"id": IG},
                       "value": [{"content": text, "image": [{"id": "v01", "path": path}]}],
                       "settings": {"__type": "instagram", "post_type": "post",
                                    "is_trial_reel": True, "graduation_strategy": "MANUAL"}}]}
    if DRY:
        print(json.dumps(body, ensure_ascii=False)[:400] if k == 1 else f"{video.name} {when.isoformat()}")
        continue
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False)
    try:
        created = px._cli("posts:create", "--json", f.name)
    finally:
        os.unlink(f.name)
    record[video.name] = {"date": body["date"], "media": path, "trial": True, "result": created}
    REC.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PROGRESS {k}/{len(jobs)} scheduled {video.name} {when:%a %H:%M}", flush=True)
