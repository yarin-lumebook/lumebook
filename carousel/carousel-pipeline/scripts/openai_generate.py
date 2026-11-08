#!/usr/bin/env python3
"""Run, resume, QA and replace the OpenAI picture jobs of one approved carousel (03 Nov 2026).

    python3 openai_generate.py RUN_DIR status
    python3 openai_generate.py RUN_DIR plan                                  # what would run, estimated tokens and dollars
    python3 openai_generate.py RUN_DIR run [JOB ...] --max-usd 0.30 [--dry-run] [--workers 4]
    python3 openai_generate.py RUN_DIR qa JOB pass|fail [--note "..."]
    python3 openai_generate.py RUN_DIR replace JOB --note "fix" --max-usd 0.30 [--dry-run]

Yarin's rules for the OpenAI key (03 Nov 2026, memory feedback-openai-api-key-rules): always ask for a budget, never exceed it,
tell the estimated tokens and cost before generating, create nothing without his explicit permission. So:
- run and replace need --max-usd, the amount Yarin approved for this carousel; there is no default;
- no call starts when the logged spend, the calls in flight and this call's estimate would pass it (the whole batch is
  checked once before the first call, then every call again at the moment it starts);
- the logged spend is the real cost of each finished call, from the usage OpenAI returns; a call whose outcome is unknown
  (a timeout) counts at its estimate, so the budget is never understated;
- --dry-run prints the prompts and the estimate and calls nothing.
Carousel Machine asks for the budget and shows the estimate before it runs this (producer.py).

Resumable: finished jobs are skipped, state.json records every attempt, and a failed call leaves the other pictures
untouched. Slides need a reference picture that passed QA. Each job may be replaced twice; after that the runner refuses.

Story runs (story-format.md, jobs.json "story": true): the reference is the cover, slide-01 (jobs.json "reference_job"). It
runs alone and waits for QA; then slide-02 to slide-NN run in parallel as edits of it.

OPENAI_API_KEY comes from the environment only (run through `zsh -ic`), never written to disk or logs. Every picture is
saved as generated-assets/<job>.png, cropped to the centred 4:5 at 1024 x 1280; the 2:3 original from OpenAI is kept in
generated-assets/openai-originals/.
"""

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import openai_pictures as op  # noqa: E402


class Run:
    lock = threading.Lock()   # state.json, the log and the in-flight total are used from parallel workers
    reserved = 0.0            # estimated dollars of calls that started and have not finished

    def __init__(self, run_dir):
        self.dir = Path(run_dir).resolve()
        self.jobs = lib.read_json(self.dir / "jobs.json")
        if any("mode" not in j for j in self.jobs.get("jobs", {}).values()):
            raise SystemExit(f"{self.dir.name} was frozen before 03 Nov 2026 (fal or ChatGPT jobs). Freeze it again first, which is free and keeps "
                             "the pictures already made: python3 carousel/carousel-pipeline/scripts/prepare_picture_jobs.py PATH/pack.json OPTION")
        self.state_path = self.dir / "state.json"
        self.state = lib.read_json(self.state_path)
        self.gen = self.dir / "generated-assets"
        self.log_path = self.gen / "generation-log.jsonl"

    def save(self):
        with self.lock:
            lib.write_json(self.state_path, self.state)

    def spent(self):
        if not self.log_path.exists():
            return 0.0
        total = 0.0
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get("billed", True):
                    total += float(rec.get("estimated_cost_usd", 0))
        return round(total, 5)

    def log(self, record):
        self.gen.mkdir(parents=True, exist_ok=True)
        with self.lock, self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def reference_job(run):
    """The job every other job is edited from: the cover of a story run (slide-01)."""
    return run.jobs.get("reference_job", "character-reference")


def job_estimate(run, name, cfg=None):
    return op.estimate_job(run.jobs["jobs"][name], cfg)["usd"]


def check_budget(run, cost, max_usd):
    """Stop, before anything is called, when this much more would pass the approved amount."""
    if max_usd is None:
        raise SystemExit("--max-usd is required: pass the amount Yarin approved as the budget for this carousel")
    spent = run.spent()
    if spent + Run.reserved + cost > max_usd + 1e-9:
        raise SystemExit(f"stop: logged spend ${spent:.4f} + in flight ${Run.reserved:.4f} + this estimate ${cost:.4f} would pass the "
                         f"approved ${max_usd:.4f}. Ask Yarin for a bigger budget before generating more.")


def reserve(run, cost, max_usd):
    with Run.lock:
        check_budget(run, cost, max_usd)
        Run.reserved += cost


def release(cost):
    with Run.lock:
        Run.reserved = max(0.0, Run.reserved - cost)


def execute(run, name, max_usd, dry_run, replacement=False, client=None, cfg=None):
    cfg = cfg or op.config()
    st = run.state["jobs"][name]
    job = run.jobs["jobs"][name]
    prompt = job["input"]["prompt"]
    if replacement and st["notes"]:
        prompt = prompt + "\n\nFix from visual QA: " + " ".join(st["notes"])
    job = {**job, "input": {**job["input"], "prompt": prompt}}
    for ref in job.get("refs") or []:
        ref_state = run.state["jobs"][ref]
        if ref_state["status"] != "done" or ref_state["qa"] != "pass":
            raise SystemExit(f"{name} needs {ref} generated and QA-passed first (qa {ref} pass)")
    est = op.estimate_job(job, cfg)
    if dry_run:
        print(json.dumps({"job": name, "model": job["model"], "mode": job["mode"], "estimate": est, "input": job["input"],
                          "refs": [f"generated-assets/{r}.png" for r in job.get("refs") or []]}, ensure_ascii=False, indent=2))
        return
    reserve(run, est["usd"], max_usd)
    try:
        client = client or op.OpenAIImages()
        st["attempts"] += 1
        st["status"] = "running"
        run.save()
        start = time.time()
        record = {"job": name, "model": job["model"], "mode": job["mode"], "attempt": st["attempts"], "replacement": replacement,
                  "pre_estimate_usd": est["usd"], "at": lib.now_local().isoformat(timespec="seconds")}
        try:
            if job["mode"] == "edit":
                request_id, png, usage = client.edit(job, [run.gen / f"{r}.png" for r in job["refs"]], cfg)
            else:
                request_id, png, usage = client.generate(job, cfg)
        except op.ApiError as exc:
            st["status"] = "failed"
            run.save()
            run.log({**record, "status": "error", "error": str(exc)[:300], "http": exc.status, "code": exc.code, "billed": exc.billed,
                     "estimated_cost_usd": est["usd"] if exc.billed else 0, "seconds": round(time.time() - start, 1)})
            raise RuntimeError(f"{name} failed: {exc}. Other jobs are untouched; rerun the same command to resume.")
        except Exception as exc:
            # anything else once the request was on its way (an answer cut off or unreadable after a 200, a bad picture
            # payload): the outcome is unknown, so it counts as spent at the estimate, like a dropped connection
            # (audit of 08 Nov 2026: these left the job "running" with nothing in the spend log)
            st["status"] = "failed"
            run.save()
            run.log({**record, "status": "error", "error": f"{type(exc).__name__}: {exc}"[:300], "billed": True,
                     "estimated_cost_usd": est["usd"], "cost_basis": "estimate", "seconds": round(time.time() - start, 1)})
            raise RuntimeError(f"{name} failed ({type(exc).__name__}); counted as spent because the outcome is unknown. "
                               "Other jobs are untouched; rerun the same command to resume.")
        cost = op.usage_cost(usage, cfg)
        originals = run.gen / "openai-originals"
        originals.mkdir(parents=True, exist_ok=True)
        raw = originals / f"{name}-attempt{st['attempts']}.png"
        raw.write_bytes(png)
        out = run.gen / f"{name}.png"
        try:
            op.normalize(raw, out)
        except Exception as exc:   # the picture is made and paid: log it before anything else
            st["status"] = "failed"
            run.save()
            run.log({**record, "status": "error", "error": f"crop: {type(exc).__name__}: {exc}"[:300], "request_id": request_id,
                     "usage": usage, "estimated_cost_usd": cost, "billed": True, "cost_basis": "usage",
                     "seconds": round(time.time() - start, 1), "file": raw.name})
            raise RuntimeError(f"{name}: the picture was made and paid (${cost:.4f}) but could not be cropped ({exc}); "
                               f"the original is {raw}. A rerun makes and pays for a new one.")
        st.update({"status": "done", "qa": None, "request_id": request_id})
        run.save()
        run.log({**record, "status": "ok", "request_id": request_id, "usage": usage, "estimated_cost_usd": cost, "billed": True,
                 "cost_basis": "usage", "seconds": round(time.time() - start, 1), "file": out.name})
        print(f"{name} -> {out} (${cost:.4f}, {usage.get('input_tokens', 0)} in / {usage.get('output_tokens', 0)} out tokens, request {request_id})")
    finally:
        release(est["usd"])


def cmd_status(run, _args):
    print(f"{run.dir}\nlogged spend so far: ${run.spent():.4f}")
    for name in run.jobs["order"]:
        s = run.state["jobs"][name]
        print(f"{name:20} {s['status']:8} qa {str(s['qa']):5} attempts {s['attempts']} replacements {s['replacements']}")


def cmd_plan(run, _args):
    cfg = op.config()
    pending = [n for n in run.jobs["order"] if run.state["jobs"][n]["status"] != "done"]
    print(json.dumps({"model": cfg["model"], "size": cfg["size"], "quality": cfg["quality"], "pending": pending,
                      "estimate": op.estimate_total(run.jobs, pending, cfg), "spent_so_far_usd": run.spent()}, indent=2))


def cmd_run(run, args):
    cfg = op.config()
    names = args.jobs or [n for n in run.jobs["order"] if run.state["jobs"][n]["status"] != "done"]
    todo = []
    for name in names:
        if name not in run.jobs["jobs"]:
            raise SystemExit(f"unknown job {name}")
        if run.state["jobs"][name]["status"] == "done" and not args.dry_run:
            print(f"{name} already done, skipped")
            continue
        todo.append(name)
    if args.dry_run:
        for name in todo:
            execute(run, name, args.max_usd, True, cfg=cfg)
        print(json.dumps({"estimate": op.estimate_total(run.jobs, todo, cfg)}, indent=2))
        return
    if args.max_usd is None:
        raise SystemExit("--max-usd is required: pass the amount Yarin approved as the budget for this carousel")
    ref = reference_job(run)
    if ref in todo and ref in run.jobs["jobs"]:   # the cover always runs alone and stops for visual QA
        try:
            execute(run, ref, args.max_usd, False, cfg=cfg)
        except RuntimeError as exc:
            raise SystemExit(str(exc))
        print(f"Inspect the reference at full size, then: qa {ref} pass")
        return
    if not todo:
        return
    for name in todo:   # fail before spending anything if a slide's reference has not passed QA
        for r in run.jobs["jobs"][name].get("refs", []):
            if run.state["jobs"][r]["status"] != "done" or run.state["jobs"][r]["qa"] != "pass":
                raise SystemExit(f"{name} needs {r} generated and QA-passed first (qa {r} pass)")
    check_budget(run, op.estimate_total(run.jobs, todo, cfg)["usd"], args.max_usd)   # the whole batch, before the first call
    client = op.OpenAIImages()
    workers = max(1, min(args.workers, len(todo)))
    errors = []

    def one(name):
        try:
            execute(run, name, args.max_usd, False, client=client, cfg=cfg)
        except (RuntimeError, SystemExit) as exc:   # one failed or refused slide never stops the others
            errors.append(str(exc))

    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, todo))
    print(f"{len(todo) - len(errors)} of {len(todo)} images in {time.time() - start:.0f}s ({workers} at a time), logged spend ${run.spent():.4f} of ${args.max_usd:.4f}")
    if errors:
        raise SystemExit("\n".join(errors))


def cmd_qa(run, args):
    st = run.state["jobs"][args.job]
    if st["status"] != "done":
        raise SystemExit(f"{args.job} has no finished image to QA")
    st["qa"] = args.result
    if args.note:
        st["notes"].append(args.note)
    run.save()
    print(f"{args.job} qa {args.result}")


def cmd_replace(run, args):
    st = run.state["jobs"][args.job]
    if st["qa"] != "fail":
        raise SystemExit(f"{args.job} is not marked as failed QA; only failed images are replaced")
    if st["replacements"] >= run.jobs["max_replacements_per_job"]:
        raise SystemExit(f"stop: {args.job} already failed {st['replacements']} replacements. Ask Yarin for direction before trying again.")
    if args.note:
        st["notes"].append(args.note)
    if args.dry_run:
        execute(run, args.job, args.max_usd, True, replacement=True)
        return
    if args.max_usd is None:
        raise SystemExit("--max-usd is required: pass the amount Yarin approved as the budget for this carousel")
    check_budget(run, job_estimate(run, args.job), args.max_usd)   # refuse before the old picture is moved away
    old = run.gen / f"{args.job}.png"
    if old.exists():
        (run.gen / "rejected").mkdir(parents=True, exist_ok=True)
        old.replace(run.gen / "rejected" / f"{args.job}-attempt{st['attempts']}.png")
    st["replacements"] += 1
    st["status"] = "pending"
    run.save()
    try:
        execute(run, args.job, args.max_usd, False, replacement=True)
    except RuntimeError as exc:
        raise SystemExit(str(exc))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("plan").set_defaults(func=cmd_plan)
    r = sub.add_parser("run")
    r.add_argument("jobs", nargs="*")
    r.add_argument("--max-usd", type=float)
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--workers", type=int, default=4, help="images generated at the same time")
    r.set_defaults(func=cmd_run)
    q = sub.add_parser("qa")
    q.add_argument("job")
    q.add_argument("result", choices=["pass", "fail"])
    q.add_argument("--note")
    q.set_defaults(func=cmd_qa)
    rp = sub.add_parser("replace")
    rp.add_argument("job")
    rp.add_argument("--note")
    rp.add_argument("--max-usd", type=float)
    rp.add_argument("--dry-run", action="store_true")
    rp.set_defaults(func=cmd_replace)
    args = ap.parse_args()
    run = Run(args.run_dir)
    args.func(run, args)


if __name__ == "__main__":
    main()
