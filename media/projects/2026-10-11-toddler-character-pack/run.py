#!/usr/bin/env python3
"""Run one Higgsfield job for the reel-character reference pack and record it.

usage: run.py NAME ASPECT PROMPT_FILE REF [REF...]
Saves NAME.png (or NAME_v2.png, ... if it exists), the raw job JSON in raw/,
and appends prompt, model, settings and job id to manifest.json.
"""
import json, subprocess, sys, urllib.request, datetime, fcntl
from pathlib import Path

HERE = Path(__file__).parent
MODEL = "seedream_v5_pro"
RESOLUTION = "2k"

def find_url(o):
    if isinstance(o, str):
        return o if o.startswith("http") and o.split("?")[0].lower().endswith((".png", ".jpg", ".jpeg", ".webp")) else None
    if isinstance(o, dict):
        for k in ("result_url", "url", "results", "result", "outputs", "output"):
            if k in o:
                u = find_url(o[k])
                if u: return u
        for v in o.values():
            u = find_url(v)
            if u: return u
    if isinstance(o, list):
        for v in o:
            u = find_url(v)
            if u: return u
    return None

def find_id(o):
    if isinstance(o, list) and o: return find_id(o[0])
    if isinstance(o, dict): return o.get("id") or o.get("job_id")
    return None

name, aspect, prompt_file, refs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
prompt = Path(prompt_file).read_text().strip()
cmd = ["higgsfield", "generate", "create", MODEL, "--prompt", prompt,
       "--aspect_ratio", aspect, "--resolution", RESOLUTION]
for r in refs: cmd += ["--image-references", r]
cmd += ["--wait", "--wait-timeout", "15m", "--json"]
p = subprocess.run(cmd, capture_output=True, text=True)
if p.returncode != 0:
    sys.exit(f"{name}: FAILED\n{p.stdout}\n{p.stderr}")
data = json.loads(p.stdout)
url = find_url(data)
if not url: sys.exit(f"{name}: no result url\n{p.stdout[:2000]}")
ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
out, v = HERE / f"{name}.{ext}", 1
while out.exists():
    v += 1
    out = HERE / f"{name}_v{v}.{ext}"
urllib.request.urlretrieve(url, out)
(HERE / "raw" / f"{out.stem}.json").write_text(json.dumps(data, indent=2))
entry = {"file": out.name, "version": v, "model": MODEL, "job_id": find_id(data),
         "settings": {"aspect_ratio": aspect, "resolution": RESOLUTION},
         "image_references": refs, "prompt": prompt, "result_url": url,
         "created": datetime.datetime.now().isoformat(timespec="seconds")}
mf = HERE / "manifest.json"
with open(HERE / ".manifest.lock", "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    m = json.loads(mf.read_text()) if mf.exists() else {"generations": []}
    m["generations"].append(entry)
    mf.write_text(json.dumps(m, indent=2, ensure_ascii=False))
print(f"{name}: {out.name}  job {entry['job_id']}")
