#!/usr/bin/env python3
"""Option 2 (11 Nov 2026): transcribe only ~60 s around each song's current cut (15 s before, 45 s after)
instead of the whole song. Writes analysis/lyrics/<id>.json with absolute timestamps and "window": [a, b].
Skips songs that already have a full transcript. Run from the project root."""
import json, subprocess, os, tempfile
from pathlib import Path
D = Path(__file__).resolve().parent.parent
OUT = D / "analysis" / "lyrics"
lib = json.loads((D / "library.json").read_text())["tracks"]
def fmt(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
def ts(s):
    h, m, r = s.split(":"); sec, ms = r.split(","); return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
tmp = Path(tempfile.mkdtemp())
BYID = {f.stem[-12:-1]: f for f in D.glob("0*/*.mp3")}  # library.json paths can be stale after a re-sort
for n, r in enumerate(lib, 1):
    o = OUT / f"{r['id']}.json"
    if o.exists():
        print(f"PROGRESS {n}/{len(lib)} {r['id']} kept", flush=True); continue
    a = max(0.0, r["cut"]["start"] - 15); b = min(r["seconds"], r["cut"]["start"] + 45)
    w = tmp / "w.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.2f}", "-t", f"{b-a:.2f}", "-i", str(BYID.get(r["id"], D / r["file"])), "-ar", "16000", "-ac", "1", str(w)], check=True)
    subprocess.run(["whisper-cli", "-m", os.path.expanduser("~/.cache/whisper/ggml-small.en.bin"), "-f", str(w), "-t", "6", "-bs", "1", "-bo", "1",
                    "-sns", "--prompt", "Song lyrics:", "-oj", "-of", str(tmp / "w"), "-np"], capture_output=True)
    d = json.loads((tmp / "w.json").read_text(errors="replace"))
    for s in d.get("transcription", []):
        s["timestamps"] = {"from": fmt(ts(s["timestamps"]["from"]) + a), "to": fmt(ts(s["timestamps"]["to"]) + a)}
    d["window"] = [round(a, 2), round(b, 2)]
    o.write_text(json.dumps(d))
    print(f"PROGRESS {n}/{len(lib)} {r['id']}", flush=True)
print("DONE")
