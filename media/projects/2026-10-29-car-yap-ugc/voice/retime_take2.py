"""Fit the full Anush recording to take 2's lip timing without touching any word.

Seedance 2.5 (take 2) re-voiced the reference and stretched two pauses: sentence 3 starts
about 0.50 s later than in the recording and sentence 4 about 0.76 s later (ivrit-ai Whisper
word timings, 29 Oct 2026). This only lengthens silences, split inside measured quiet runs.
Usage: python3 retime_take2.py  ->  voice-final-anush-take2.wav
"""
import subprocess

SRC = "voice-final-anush.mp3"
OUT = "voice-final-anush-take2.wav"
TARGET = 14.08  # take 2 length
# (cut point in the recording, seconds of silence inserted there)
INSERTS = [(7.30, 0.50), (9.30, 0.06), (11.00, 0.20)]

cuts = [0.0] + [t for t, _ in INSERTS] + [None]
parts, labels = [], []
for i in range(len(cuts) - 1):
    a, b = cuts[i], cuts[i + 1]
    trim = f"atrim=start={a}" + (f":end={b}" if b is not None else "")
    parts.append(f"[0:a]{trim},asetpts=PTS-STARTPTS[s{i}]")
    labels.append(f"[s{i}]")
    if i < len(INSERTS):
        parts.append(f"anullsrc=r=44100:cl=mono,atrim=duration={INSERTS[i][1]}[g{i}]")
        labels.append(f"[g{i}]")
graph = ";".join(parts) + ";" + "".join(labels) + \
    f"concat=n={len(labels)}:v=0:a=1,apad=whole_dur={TARGET}[out]"

subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", graph,
     "-map", "[out]", "-ac", "1", "-ar", "44100", OUT],
    check=True,
)
print(OUT, f"+{sum(d for _, d in INSERTS):.2f}s of pauses, padded to {TARGET}s")
