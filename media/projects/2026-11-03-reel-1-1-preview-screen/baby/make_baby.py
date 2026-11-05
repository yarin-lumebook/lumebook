"""One OpenAI edit: Yarin as a funny baby for reel 1.1 (4 Nov 2026). Yarin approved one picture, budget $0.03.
One call only, no retry; it refuses to start if the estimate passes the budget. Run through zsh -ic for the key."""
import json, sys
from pathlib import Path
sys.path.insert(0, "/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts")
import openai_pictures as op

BUDGET = 0.03
here = Path(__file__).parent
cfg = op.config()
job = {"mode": "edit", "model": cfg["model"], "refs": ["reference-yarin.png"],
       "input": {**op.base_input(cfg), "prompt": (here / "prompt.txt").read_text().strip()}}
est = op.estimate_job(job, cfg)
print("estimate", est)
if est["usd"] > BUDGET:
    raise SystemExit(f"estimate ${est['usd']} is over the ${BUDGET} budget, nothing called")
out = here / "baby-yarin.png"
if out.exists():
    raise SystemExit("baby-yarin.png already exists, nothing called")
try:
    rid, png, usage = op.OpenAIImages().edit(job, [here / "reference-yarin.png"], cfg)
except op.ApiError as e:
    (here / "log.json").write_text(json.dumps({"error": str(e), "billed_unknown": e.billed, "estimate": est}, indent=1))
    raise SystemExit(f"call failed: {e}")
out.write_bytes(png)
cost = op.usage_cost(usage, cfg)
(here / "log.json").write_text(json.dumps({"request_id": rid, "usage": usage, "usd": cost, "estimate": est, "budget": BUDGET}, indent=1))
print("saved", out.name, "real cost $", cost, "usage", usage)
