"""One slow, subtle push-in across the whole 10 s edit, at 1080x1920 (Yarin, 29 Oct 2026: replaced the punch-ins).

The zoom grows evenly from 1.00 to ZOOM_END around a fixed point between her face and the book (variants.py
anchor; the same for both takes), low enough that on take 2 the kid's name stays above Instagram's safe line
(65% of the height), where the caption box that hides it has to sit. zoompan runs on a 2x upscale so the window
moves in half-pixel steps and does not shake.
Usage: python3 zoom_cuts.py [higgsfield|fal]  ->  the variant's zoomed edit   (to_zoomed() is used by captions_box.py)
"""
import subprocess
from pathlib import Path
from variants import V

SRC, OUT = V["edit"], V["zoomed"]
W, H, FPS, FRAMES = 1080, 1920, 30, 300
ZOOM_END = 1.08
ANCHOR = V["anchor"]                # the point that stays still, full size


def zoom(n):
    return 1 + (ZOOM_END - 1) * n / (FRAMES - 1)


def to_zoomed(x, y, n):
    """Where an un-zoomed point (full size) lands in frame n of the zoomed video."""
    z = zoom(n)
    return (x - ANCHOR[0]) * z + ANCHOR[0], (y - ANCHOR[1]) * z + ANCHOR[1]


if __name__ == "__main__":
    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    px, py = 2 * ANCHOR[0], 2 * ANCHOR[1]
    vf = (f"scale={2 * W}:{2 * H}:flags=lanczos,"
          f"zoompan=z='1+{ZOOM_END - 1}*on/{FRAMES - 1}':x='{px}*(1-1/zoom)':y='{py}*(1-1/zoom)'"
          f":d=1:s={W}x{H}:fps={FPS},setsar=1")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vf", vf, "-c:v", "libx264", "-crf", "15",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", OUT], check=True)
    print(OUT)
