"""Rebuild Yarin's CapCut edit of the fal take (reel-1029/source/1029.mp4) from the original, at 30 fps, no speed change.

Measured from 1029.mp4 on 29 Oct 2026 (audio cross-correlation and frame matching against outputs/car-yap-v2-anush.mp4):
- one jump cut: fal 6.967 to 7.667 s ("זהו,") is removed; both ends sit in silence below -50 dB
- zoom about the frame centre, in edit time: 0 to 3.567 s a straight push-in 1.00 to 1.25; 3.567 to 5.80 s none;
  5.80 to 6.967 s held at 1.25 (the punch-in on "ותראו מה יצא"); 6.967 s to the end a straight push-in 1.00 to 1.25
All cut points fall on whole frames at 30 fps (107, 174, 209 in the edit; 209 and 230 in the source).
Each frame is zoomed with Pillow's bicubic affine (sub-pixel, so the push-ins do not shake), straight from 720x1280.
Text goes on afterwards with the reel editor (reel-capcut.json).
Usage: /usr/bin/python3 capcut_edit.py  ->  work/capcut/car-yap-capcut-zoomed.mp4
"""
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

SRC = "outputs/car-yap-v2-anush.mp4"
OUT = Path("work/capcut/car-yap-capcut-zoomed.mp4")
FPS, SW, SH, W, H = 30, 720, 1280, 1080, 1920
CUT = (209, 230)                    # source frames [209, 230) at 30 fps = 6.967 to 7.667 s
FADE = 0.01                         # audio fade at the cut so it does not click
ZOOM_TO = 1.25


def zoom(n):
    if n < 107: return 1 + (ZOOM_TO - 1) * n / 107
    if n < 174: return 1.0
    if n < 209: return ZOOM_TO
    return 1 + (ZOOM_TO - 1) * (n - 209) / 132      # same rate as 1029 (it reaches 1.25 at its frame 341)


OUT.parent.mkdir(parents=True, exist_ok=True)
a, b = CUT[0] / FPS, CUT[1] / FPS
wav = OUT.with_suffix(".wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex",
                f"[0:a]atrim=0:{a:.4f},asetpts=PTS-STARTPTS,afade=t=out:st={a - FADE:.4f}:d={FADE}[a0];"
                f"[0:a]atrim=start={b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d={FADE}[a1];[a0][a1]concat=n=2:v=0:a=1[a]",
                "-map", "[a]", "-c:a", "pcm_s16le", str(wav)], check=True)

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-filter_complex",
                        f"[0:v]fps={FPS},split[x][y];[x]trim=end_frame={CUT[0]},setpts=PTS-STARTPTS[v0];"
                        f"[y]trim=start_frame={CUT[1]},setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v]",
                        "-map", "[v]", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-i", str(wav), "-map", "0:v", "-map", "1:a",
                        "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", str(OUT)], stdin=subprocess.PIPE)
n = 0
while True:
    buf = dec.stdout.read(SW * SH * 3)
    if len(buf) < SW * SH * 3: break
    k = W / SW * zoom(n)                             # output px per source px
    frame = Image.frombuffer("RGB", (SW, SH), buf, "raw", "RGB", 0, 1)
    out = frame.transform((W, H), Image.AFFINE, (1 / k, 0, SW / 2 - W / 2 / k, 0, 1 / k, SH / 2 - H / 2 / k),
                          Image.BICUBIC)
    enc.stdin.write(out.tobytes())
    n += 1
    if n % 30 == 0: print(f"PROGRESS {n}/340 frame {n}", flush=True)
enc.stdin.close(); enc.wait(); dec.wait()
print(OUT, n, "frames", f"{n / FPS:.3f}s")
