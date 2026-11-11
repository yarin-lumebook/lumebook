#!/usr/bin/env python3
"""Checks where each 30 s cut lands: transcribes its first 10 s (whisper small.en, like transcribe.sh)
and reports when the singing starts and whether that first line is one the song repeats (a chorus line).

  python3 media/projects/2026-11-11-reel-music-library/tools/check_cuts.py [--only ID ...]

Writes analysis/cut-check.json (no lyrics text in it, only times and verdicts). Made 11 Nov 2026.
"""
import argparse, difflib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import library as L

D = L.D
MODEL = os.path.expanduser("~/.cache/whisper/ggml-small.en.bin")


def norm(t):
    return re.sub(r"[^a-z' ]", "", t.lower()).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    lib = json.loads((D / "library.json").read_text())["tracks"]
    out = {}
    tmp = Path(tempfile.mkdtemp())
    for k, r in enumerate(lib, 1):
        if a.only and r["id"] not in a.only or "cut" not in r:
            continue
        w = tmp / "c.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-t", "10", "-i", str(D / r["cut"]["file"]), "-ar", "16000", "-ac", "1", str(w)], check=True)
        subprocess.run(["whisper-cli", "-m", MODEL, "-f", str(w), "-t", "6", "-bs", "1", "-bo", "1", "-sns",
                        "--prompt", "Song lyrics:", "-oj", "-of", str(tmp / "c"), "-np"], capture_output=True)
        segs = []
        try:
            for s in json.loads((tmp / "c.json").read_text(errors="replace"))["transcription"]:
                t = re.sub(r"\[.*?\]|\(.*?\)|♪", "", s["text"]).strip()
                if t and not L.HALLU.match(t):
                    segs.append((L.ts(s["timestamps"]["from"]), t))
        except Exception:
            pass
        full = L.lyrics(r["id"]) or []
        rep = [norm(s["text"]) for s in full if s["repeats"] >= 2]
        first = segs[0] if segs else None
        chorus = bool(first) and any(difflib.SequenceMatcher(None, norm(first[1]), x).ratio() > 0.7 for x in rep)
        if not first:
            verdict = "no singing in the first 10 s"
        elif first[0] <= 1.5:
            verdict = "opens on a chorus line" if chorus else "opens on a sung line"
        else:
            verdict = f"singing starts at {first[0]:.1f} s" + (" (chorus line)" if chorus else "")
        out[r["id"]] = {"n": r["n"], "title": r["title"], "start": r["cut"]["start"], "first_sung_s": round(first[0], 1) if first else None,
                        "chorus_line": chorus, "verdict": verdict}
        print(f"PROGRESS {k}/{len(lib)} {r['n']:02d} {verdict}", flush=True)
    p = D / "analysis" / "cut-check.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old.update(out)
    p.write_text(json.dumps(old, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
