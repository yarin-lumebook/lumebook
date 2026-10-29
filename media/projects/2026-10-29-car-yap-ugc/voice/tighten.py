"""Trim the silent part of each pause in the Anush take so it fits take 1 (12.064 s).

Breaths before each sentence are kept; only stretches measured below -47 dB are cut.
Usage: python3 tighten.py  ->  voice-final-anush-12s.wav
"""
import subprocess

SRC = "voice-final-anush.mp3"
OUT = "voice-final-anush-12s.wav"
TARGET = 12.064  # take 1 length
# (start, end) seconds to keep; the gaps between them are the trimmed silences
KEEP = [(0, 3.46), (3.58, 7.06), (7.46, 8.12), (8.20, 9.24), (9.32, 10.72), (11.16, 13.12)]
FADE = 0.005  # short fades at every cut so there are no clicks

parts = []
for i, (a, b) in enumerate(KEEP):
    parts.append(
        f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
        f"afade=t=in:d={FADE},afade=t=out:st={b - a - FADE:.3f}:d={FADE}[p{i}]"
    )
joined = "".join(f"[p{i}]" for i in range(len(KEEP)))
graph = ";".join(parts) + f";{joined}concat=n={len(KEEP)}:v=0:a=1,apad=whole_dur={TARGET}[out]"

subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", graph,
     "-map", "[out]", "-ac", "1", "-ar", "44100", OUT],
    check=True,
)
print(OUT, f"kept {sum(b - a for a, b in KEEP):.2f}s, padded to {TARGET}s")
