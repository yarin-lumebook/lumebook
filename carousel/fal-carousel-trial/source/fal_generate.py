#!/usr/bin/env python3
"""Run the image jobs in source/jobs.json through the official fal.ai MCP server.

    export FAL_KEY=...            # never commit it; read from the environment only
    python3 source/fal_generate.py cover-A-nb2 cover-B-nb2      # run named jobs
    python3 source/fal_generate.py --list                       # show jobs + est. cost

Talks JSON-RPC to https://mcp.fal.ai/mcp (the same server `claude mcp add fal-ai` connects),
using its run_model / check_job / get_job_result / upload_file tools.
Outputs land in generated-assets/<job>.png, untouched. Every call is appended to
generated-assets/generation-log.jsonl (model, full input incl. seed, request id,
wall time, estimated cost). Media URLs are deliberately NOT logged.

A job may list "refs": ["<other job>", ...]. Those local PNGs are uploaded to fal's CDN
(upload_file, prepare_upload + PUT) and passed as image_urls: the reference-image workflow.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "generated-assets"
JOBS = json.loads((ROOT / "source" / "jobs.json").read_text(encoding="utf-8"))
URL = "https://mcp.fal.ai/mcp"
KEY = os.environ.get("FAL_KEY", "")

_sid, _id = None, 0


def _post(payload, notify=False):
    global _sid
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
         "Authorization": f"Bearer {KEY}", "MCP-Protocol-Version": "2025-06-18"}
    if _sid:
        h["Mcp-Session-Id"] = _sid
    req = urllib.request.Request(URL, json.dumps(payload).encode(), h, method="POST")
    with urllib.request.urlopen(req, timeout=900) as r:
        _sid = r.headers.get("Mcp-Session-Id") or _sid
        body, ctype = r.read().decode("utf-8", "replace"), r.headers.get("Content-Type", "")
    if notify:
        return None
    if "text/event-stream" in ctype:
        msgs = [json.loads(l[5:]) for l in body.splitlines() if l.startswith("data:") and l[5:].strip()]
        return next(m for m in reversed(msgs) if m.get("id") == payload["id"])
    return json.loads(body)


def tool(name, args):
    global _id
    _id += 1
    res = _post({"jsonrpc": "2.0", "id": _id, "method": "tools/call", "params": {"name": name, "arguments": args}})
    if "error" in res:
        raise RuntimeError(f"{name}: {res['error']}")
    text = "".join(c.get("text", "") for c in res["result"].get("content", []) if c.get("type") == "text")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"raw": text}
    if res["result"].get("isError"):
        raise RuntimeError(f"{name} failed: {text[:1500]}")
    return data


def connect():
    if not KEY:
        sys.exit("FAL_KEY is not set in this environment.")
    _post({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "lumebook-carousel", "version": "1"}}})
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, notify=True)


def upload(path: Path) -> str:
    prep = tool("upload_file", {"prepare_upload": True, "file_name": path.name, "file_size": path.stat().st_size})
    put = urllib.request.Request(prep["upload_url"], path.read_bytes(), method="PUT",
                                 headers={"Content-Type": prep.get("content_type", "image/png"), **prep.get("upload_headers", {})})
    urllib.request.urlopen(put, timeout=300).read()
    return prep["file_url"]


def find_images(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("url"), str) and (str(obj.get("content_type", "")).startswith("image") or obj["url"].split("?")[0].endswith((".png", ".jpg", ".jpeg", ".webp"))):
            yield obj
        for v in obj.values():
            yield from find_images(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from find_images(v)


def run(job_name):
    job = JOBS["jobs"][job_name]
    model = JOBS["models"][job["model"]]
    inp = {**model.get("defaults", {}), **job.get("params", {})}
    inp["prompt"] = "\n\n".join(JOBS["blocks"][b] if b in JOBS["blocks"] else b for b in job["prompt"])
    if job.get("refs"):
        inp["image_urls"] = [upload(GEN / f"{r}.png") for r in job["refs"]]
    t0 = time.time()
    res = tool("run_model", {"endpoint_id": model["endpoint"], "input": inp})
    if res.get("status") == "processing":
        rid = res["request_id"]
        while True:
            time.sleep(4)
            st = tool("check_job", {"endpoint_id": model["endpoint"], "request_id": rid, **({"status_url": res["status_url"]} if res.get("status_url") else {})})
            if str(st.get("queue_status", st.get("status", ""))).upper() in ("COMPLETED", "OK"):
                break
            if str(st.get("queue_status", st.get("status", ""))).upper() in ("FAILED", "ERROR", "CANCELLED"):
                raise RuntimeError(f"job failed: {st}")
        res = tool("get_job_result", {"endpoint_id": model["endpoint"], "request_id": rid, **({"response_url": res["response_url"]} if res.get("response_url") else {})})
    secs = round(time.time() - t0, 1)
    imgs = list(find_images(res))
    if not imgs:
        raise RuntimeError(f"no image in result: {json.dumps(res)[:1500]}")
    out = GEN / f"{job_name}.png"
    with urllib.request.urlopen(imgs[0]["url"], timeout=300) as r:
        out.write_bytes(r.read())
    rec = {"job": job_name, "endpoint": model["endpoint"], "input": {k: v for k, v in inp.items() if k != "image_urls"},
           "refs": job.get("refs", []), "request_id": res.get("request_id") or res.get("requestId"),
           "seed": res.get("seed", (res.get("result") or {}).get("seed") if isinstance(res.get("result"), dict) else None),
           "wall_seconds": secs, "est_cost_usd": model["est_cost_usd"],
           "width": imgs[0].get("width"), "height": imgs[0].get("height"),
           "model_description": (res.get("description") or (res.get("result") or {}).get("description") if isinstance(res.get("result"), dict) else res.get("description")),
           "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with open(GEN / "generation-log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{job_name}: {out.name} {rec['width']}x{rec['height']} in {secs}s, est ${model['est_cost_usd']}")
    return rec


if __name__ == "__main__":
    if "--list" in sys.argv:
        for k, j in JOBS["jobs"].items():
            print(f"{k:28s} {JOBS['models'][j['model']]['endpoint']:45s} ${JOBS['models'][j['model']]['est_cost_usd']}")
        sys.exit()
    connect()
    for name in sys.argv[1:]:
        run(name)
