#!/usr/bin/env python3
"""Run, resume, QA and replace the fal.ai jobs of one approved carousel.

    python3 fal_generate.py RUN_DIR status
    python3 fal_generate.py RUN_DIR plan                                   # what would run and what it costs
    python3 fal_generate.py RUN_DIR run [JOB ...] --max-usd 1.60 [--dry-run] [--workers 7]
    python3 fal_generate.py RUN_DIR qa JOB pass|fail [--note "..."]
    python3 fal_generate.py RUN_DIR replace JOB --note "fix" --max-usd 1.60 [--dry-run]

Only call run or replace after Yarin approved APPROVAL.md in chat. --max-usd is that approved amount:
the runner stops before any call that would push the logged estimate past it.

Slides run in parallel (default 7 at a time, --workers 1 for one by one). fal queues anything above the
account's concurrency limit and never rejects it (fal.ai/docs/documentation/model-apis/concurrency-limits),
and the whole batch is checked against --max-usd before the first call.

Resumable: finished jobs are skipped, state.json records every attempt, and a failed call leaves the
other images untouched. Slides need a reference image that passed QA. Each job may be replaced twice;
after that the runner refuses and asks for direction.

Story runs (story-format.md, 29 Oct 2026; jobs.json "story": true): the reference is the cover, slide-01 (jobs.json
"reference_job"). It runs alone and waits for QA like the character reference; then slide-02 to slide-NN run in
parallel as edits of it. jobs.json "max_usd" (1.00) caps the whole carousel even when --max-usd is higher.

FAL_KEY is read from the environment and never written to disk or logs. The calls go to the official
fal.ai MCP server (https://mcp.fal.ai/mcp), the same server the fal-ai MCP connector uses, so this works
even when the MCP tools are not loaded into a Claude session.
"""

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402

MCP_URL = "https://mcp.fal.ai/mcp"


class Run:
    lock = threading.Lock()   # state.json and the log are written from parallel workers

    def __init__(self, run_dir):
        self.dir = Path(run_dir).resolve()
        self.jobs = lib.read_json(self.dir / "jobs.json")
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
        return round(total, 4)

    def log(self, record):
        self.gen.mkdir(parents=True, exist_ok=True)
        with self.lock, self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# fal MCP client (JSON-RPC over HTTP). Errors are scrubbed so the key never prints.
# ---------------------------------------------------------------------------

class Fal:
    def __init__(self):
        self.key = os.environ.get("FAL_KEY", "")
        if not self.key:
            raise SystemExit("FAL_KEY is not set in this shell. Run through zsh -ic so ~/.zshrc is loaded.")
        self.session = None
        self.n = 0
        self._post({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "lumebook-carousel", "version": "2"}}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"}, notification=True)

    def _post(self, payload, notification=False):
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   "Authorization": f"Bearer {self.key}", "MCP-Protocol-Version": "2025-06-18"}
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(MCP_URL, json.dumps(payload).encode(), headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=900) as resp:
                self.session = resp.headers.get("Mcp-Session-Id") or self.session
                body = resp.read().decode("utf-8", "replace")
                ctype = resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"fal MCP HTTP {exc.code}") from None
        except urllib.error.URLError as exc:
            raise RuntimeError(f"fal MCP unreachable: {exc.reason}") from None
        if notification:
            return None
        if "text/event-stream" in ctype:
            msgs = [json.loads(l[5:]) for l in body.splitlines() if l.startswith("data:") and l[5:].strip()]
            return next(m for m in reversed(msgs) if m.get("id") == payload["id"])
        return json.loads(body)

    def tool(self, name, arguments):
        self.n += 1
        res = self._post({"jsonrpc": "2.0", "id": self.n, "method": "tools/call", "params": {"name": name, "arguments": arguments}})
        if "error" in res:
            raise RuntimeError(f"{name}: {str(res['error'])[:500]}")
        text = "".join(i.get("text", "") for i in res["result"].get("content", []) if i.get("type") == "text")
        if res["result"].get("isError"):
            raise RuntimeError(f"{name}: {text[:800]}")
        return json.loads(text)

    def upload(self, path):
        prep = self.tool("upload_file", {"prepare_upload": True, "file_name": path.name, "file_size": path.stat().st_size})
        req = urllib.request.Request(prep["upload_url"], path.read_bytes(), method="PUT",
                                     headers={"Content-Type": prep.get("content_type", "image/png"), **prep.get("upload_headers", {})})
        urllib.request.urlopen(req, timeout=300).read()
        return prep["file_url"]

    def generate(self, endpoint, arguments):
        result = self.tool("run_model", {"endpoint_id": endpoint, "input": arguments})
        request_id = result.get("request_id") or result.get("requestId")
        if result.get("status") == "processing":
            while True:
                time.sleep(4)
                st = self.tool("check_job", {"endpoint_id": endpoint, "request_id": request_id, **({"status_url": result["status_url"]} if result.get("status_url") else {})})
                value = str(st.get("queue_status", st.get("status", ""))).upper()
                if value in ("COMPLETED", "OK"):
                    break
                if value in ("FAILED", "ERROR", "CANCELLED"):
                    raise RuntimeError(f"job {request_id} {value}")
            result = self.tool("get_job_result", {"endpoint_id": endpoint, "request_id": request_id, **({"response_url": result["response_url"]} if result.get("response_url") else {})})
        urls = list(_image_urls(result))
        if not urls:
            raise RuntimeError(f"no image returned for {request_id}")
        return request_id, urls[0]


def _image_urls(value):
    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str) and url.split("?")[0].lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            yield url
        for v in value.values():
            yield from _image_urls(v)
    elif isinstance(value, list):
        for v in value:
            yield from _image_urls(v)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def payload_for(run, name, note_lines):
    job = run.jobs["jobs"][name]
    arguments = dict(job["input"])
    if note_lines:
        arguments["prompt"] = arguments["prompt"] + "\n\nFix from visual QA: " + " ".join(note_lines)
    return job, arguments


def reference_job(run):
    """The job every other job is edited from: the character reference, or the cover of a story run (slide-01)."""
    return run.jobs.get("reference_job", "character-reference")


def check_budget(run, cost, max_usd):
    spent = run.spent()
    if max_usd is None:
        raise SystemExit("--max-usd is required: pass the amount Yarin approved in chat")
    if run.jobs.get("max_usd") is not None:   # a story run's own cap (1.00) is never exceeded, whatever was passed
        max_usd = min(max_usd, float(run.jobs["max_usd"]))
    if spent + cost > max_usd + 1e-9:
        raise SystemExit(f"stop: logged estimate ${spent:.3f} + this image ${cost:.3f} would pass the approved ${max_usd:.2f}. Ask before spending more.")


def execute(run, name, max_usd, dry_run, replacement=False, fal=None, ref_urls=None, budget_checked=False):
    st = run.state["jobs"][name]
    job, arguments = payload_for(run, name, st["notes"] if replacement else [])
    if job.get("refs"):
        for ref in job["refs"]:
            ref_state = run.state["jobs"][ref]
            if ref_state["status"] != "done" or ref_state["qa"] != "pass":
                raise SystemExit(f"{name} needs {ref} generated and QA-passed first (qa {ref} pass)")
    cost = job["estimated_cost_usd"]
    if dry_run:
        shown = dict(arguments)
        if job.get("refs"):
            shown["image_urls"] = [f"<upload of generated-assets/{r}.png>" for r in job["refs"]]
        print(json.dumps({"job": name, "endpoint": job["endpoint"], "estimated_cost_usd": cost, "input": shown}, ensure_ascii=False, indent=2))
        return
    if not budget_checked:
        check_budget(run, cost, max_usd)
    fal = fal or Fal()
    if job.get("refs"):
        arguments["image_urls"] = [(ref_urls or {}).get(r) or fal.upload(run.gen / f"{r}.png") for r in job["refs"]]
    st["attempts"] += 1
    st["status"] = "running"
    run.save()
    start = time.time()
    record = {"job": name, "endpoint": job["endpoint"], "attempt": st["attempts"], "replacement": replacement,
              "estimated_cost_usd": cost, "at": lib.now_local().isoformat(timespec="seconds")}
    try:
        request_id, url = fal.generate(job["endpoint"], arguments)
    except Exception as exc:  # noqa: BLE001 - record and stop this job only
        st["status"] = "failed"
        run.save()
        run.log({**record, "status": "error", "error": str(exc)[:300], "seconds": round(time.time() - start, 1)})
        raise RuntimeError(f"{name} failed: {exc}. Other jobs are untouched; rerun the same command to resume.")
    out = run.gen / f"{name}.png"
    with urllib.request.urlopen(url, timeout=300) as resp:
        out.write_bytes(resp.read())
    st.update({"status": "done", "qa": None, "request_id": request_id})
    run.save()
    run.log({**record, "status": "ok", "request_id": request_id, "seconds": round(time.time() - start, 1), "file": out.name})
    print(f"{name} -> {out} (~${cost:.3f}, request {request_id})")


def cmd_status(run, _args):
    print(f"{run.dir}\nlogged estimate so far: ${run.spent():.3f}")
    for name in run.jobs["order"]:
        s = run.state["jobs"][name]
        print(f"{name:20} {s['status']:8} qa {str(s['qa']):5} attempts {s['attempts']} replacements {s['replacements']}")


def cmd_plan(run, _args):
    pending = [n for n in run.jobs["order"] if run.state["jobs"][n]["status"] != "done"]
    cost = sum(run.jobs["jobs"][n]["estimated_cost_usd"] for n in pending)
    print(json.dumps({"pending": pending, "estimated_usd": round(cost, 3), "spent_so_far_usd": run.spent(),
                      "endpoints": sorted({run.jobs['jobs'][n]['endpoint'] for n in pending})}, indent=2))


def cmd_run(run, args):
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
            execute(run, name, args.max_usd, True)
        return
    ref = reference_job(run)
    if ref in todo and ref in run.jobs["jobs"]:   # the reference (or a story cover) always runs alone and stops for visual QA
        try:
            execute(run, ref, args.max_usd, False)
        except RuntimeError as exc:
            raise SystemExit(str(exc))
        print(f"Inspect the reference at full size, then: qa {ref} pass")
        return
    if not todo:
        return
    for name in todo:   # fail before spending anything if a slide's reference has not passed QA
        for ref in run.jobs["jobs"][name].get("refs", []):
            if run.state["jobs"][ref]["status"] != "done" or run.state["jobs"][ref]["qa"] != "pass":
                raise SystemExit(f"{name} needs {ref} generated and QA-passed first (qa {ref} pass)")
    check_budget(run, sum(run.jobs["jobs"][n]["estimated_cost_usd"] for n in todo), args.max_usd)
    first = Fal()
    refs = sorted({r for n in todo for r in run.jobs["jobs"][n].get("refs", [])})
    ref_urls = {r: first.upload(run.gen / f"{r}.png") for r in refs}   # uploaded once, shared by every worker
    workers = max(1, min(args.workers, len(todo)))
    errors = []

    def one(name):
        try:
            execute(run, name, args.max_usd, False, fal=first if workers == 1 else Fal(), ref_urls=ref_urls, budget_checked=True)
        except Exception as exc:  # noqa: BLE001 - one failed slide never stops the others
            errors.append(str(exc))

    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, todo))
    print(f"{len(todo) - len(errors)} of {len(todo)} images in {time.time() - start:.0f}s ({workers} at a time)")
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
    old = run.gen / f"{args.job}.png"
    if old.exists():
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
    r.add_argument("--workers", type=int, default=7, help="images generated at the same time (fal queues the rest)")
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
