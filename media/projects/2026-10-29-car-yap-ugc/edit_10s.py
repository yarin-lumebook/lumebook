"""Cut a take to a 10 s yap edit: jump-cut the gaps between sentences, then speed up evenly.

Keep ranges (variants.py) come from the voice's quiet runs: below -38 dB for take 2
(voice/voice-final-anush-take2.wav), and from ivrit-ai word timings for the fal take
(voice/voice-final-anush-12s.wav, work/fal/words-12s.json), with about 0.07 s kept around each sentence.
Picture and sound are cut at the same points, so the lip sync holds.
Usage: python3 edit_10s.py [higgsfield|fal]  ->  the variant's edit (outputs/)
"""
import subprocess
from variants import V

SRC, OUT, KEEP, FLIP = V["take"], V["edit"], V["keep"], V["flip"]
TARGET = 10.0
FADE = 0.01  # audio fade at each cut so the hum does not click

speed = sum(b - a for a, b in KEEP) / TARGET
parts, v_labels, a_labels = [], "", ""
for i, (a, b) in enumerate(KEEP):
    parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
    parts.append(
        f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
        f"afade=t=in:d={FADE},afade=t=out:st={b - a - FADE:.3f}:d={FADE}[a{i}]"
    )
    v_labels += f"[v{i}]"
    a_labels += f"[a{i}]"
n = len(KEEP)
graph = ";".join(parts) + (
    f";{v_labels}concat=n={n}:v=1:a=0,setpts=PTS/{speed:.4f},fps=30{',hflip' if FLIP else ''}[v]"
    f";{a_labels}concat=n={n}:v=0:a=1,atempo={speed:.4f}[a]"
)

subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", graph,
     "-map", "[v]", "-map", "[a]", "-t", str(TARGET),
     "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT],
    check=True,
)
print(OUT, f"speed x{speed:.3f}")
