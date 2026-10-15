#!/usr/bin/env python3
"""Run one Higgsfield job for the Lume podcast pilot and record it.

usage: run.py OUT MODEL PROMPT_FILE [higgsfield flags ...]
OUT is the result path without extension, relative to this folder
(e.g. still/candidates/still-a). Everything after PROMPT_FILE is passed to
`higgsfield generate create` unchanged. Saves the result (never overwrites:
adds _v2, _v3 ...), the raw job JSON in raw/, and appends prompt, model,
flags and job id to manifest.json.
"""
import json, subprocess, sys, urllib.request, datetime, fcntl
from pathlib import Path

HERE = Path(__file__).parent
EXTS = (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".webm", ".mp3", ".wav", ".m4a")

def find_url(o):
    if isinstance(o, str):
        return o if o.startswith("http") and o.split("?")[0].lower().endswith(EXTS) else None
    if isinstance(o, dict):
        for k in ("result_url", "url", "results", "result", "outputs", "output"):
            if k in o:
                u = find_url(o[k])
                if u: return u
        for k, v in o.items():
            if k == "params": continue  # inputs, not the result
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

name, model, prompt_file, flags = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
prompt = Path(prompt_file).read_text().strip()
cmd = ["higgsfield", "generate", "create", model, "--prompt", prompt, *flags,
       "--wait", "--wait-timeout", "30m", "--json"]
p = subprocess.run(cmd, capture_output=True, text=True)
if p.returncode != 0:
    sys.exit(f"{name}: FAILED\n{p.stdout}\n{p.stderr}")
data = json.loads(p.stdout)
url = find_url(data)
if not url: sys.exit(f"{name}: no result url\n{p.stdout[:3000]}")
ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
out, v = HERE / f"{name}.{ext}", 1
while out.exists():
    v += 1
    out = HERE / f"{name}_v{v}.{ext}"
out.parent.mkdir(parents=True, exist_ok=True)
urllib.request.urlretrieve(url, out)
raw = HERE / "raw" / f"{out.stem}.json"
raw.write_text(json.dumps(data, indent=2, ensure_ascii=False))
entry = {"file": str(out.relative_to(HERE)), "model": model, "job_id": find_id(data),
         "flags": flags, "prompt_file": str(Path(prompt_file)), "prompt": prompt,
         "result_url": url, "created": datetime.datetime.now().isoformat(timespec="seconds")}
mf = HERE / "manifest.json"
with open(HERE / ".manifest.lock", "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    m = json.loads(mf.read_text()) if mf.exists() else {"generations": []}
    m.setdefault("generations", []).append(entry)
    mf.write_text(json.dumps(m, indent=2, ensure_ascii=False))
print(f"{out.relative_to(HERE)}  job {entry['job_id']}")
