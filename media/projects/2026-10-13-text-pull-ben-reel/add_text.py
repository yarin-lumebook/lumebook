"""Cut take1 before the step back and add the growing text block (the "pulled out of the screen" trend).

Run with a Python that has Pillow:
  python add_text.py take1.mp4 final-v1.mp4
Pillow here has no raqm, so each Hebrew line is drawn reversed.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

LINES = ["את אמא", "מהממת.", "ואת", "עושה", "הכי טוב", "בשביל", "התינוק", "שלך."]
FONT = "/System/Library/Fonts/SFHebrew.ttf"
COLOR = (250, 238, 190, 255)
FPS = 30
CUT = 5.40          # seconds kept (the step back starts right after)
GROW_START = 1.70   # hand reaches the lens
GROW_END = 3.70     # palm fully open
START_SCALE = 0.06
START_POS = (0.50, 0.42)  # where the hand is, as a fraction of the frame
END_POS = (0.50, 0.50)
BLOCK_HEIGHT = 0.80       # final text block height as a fraction of the frame


def text_block(frame_h):
    size = 150
    font = ImageFont.truetype(FONT, size)
    gap = int(size * 1.42)
    widths = [font.getlength(line[::-1]) for line in LINES]
    w, h = int(max(widths)) + 80, gap * len(LINES) + 40
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i, line in enumerate(LINES):
        x, y = (w - widths[i]) / 2, 20 + i * gap
        ImageDraw.Draw(shadow).text((x, y + 4), line[::-1], font=font, fill=(0, 0, 0, 110))
        ImageDraw.Draw(img).text((x, y), line[::-1], font=font, fill=COLOR)
    block = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)), img)
    scale = frame_h * BLOCK_HEIGHT / h
    return block.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


def main(src, dst):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-t", str(CUT), "-vf", "scale=1080:1920",
                        str(tmp / "f_%04d.png")], check=True, stdin=subprocess.DEVNULL)
        frames = sorted(tmp.glob("f_*.png"))
        block = text_block(1920)
        for n, path in enumerate(frames):
            t = n / FPS
            if t < GROW_START:
                continue
            p = min(1.0, (t - GROW_START) / (GROW_END - GROW_START))
            e = 1 - (1 - p) ** 3
            s = START_SCALE + (1 - START_SCALE) * e
            cx = (START_POS[0] + (END_POS[0] - START_POS[0]) * e) * 1080
            cy = (START_POS[1] + (END_POS[1] - START_POS[1]) * e) * 1920
            layer = block.resize((max(1, int(block.width * s)), max(1, int(block.height * s))), Image.LANCZOS)
            frame = Image.open(path).convert("RGBA")
            frame.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))
            frame.convert("RGB").save(path)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f_%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-movflags", "+faststart", dst],
                       check=True, stdin=subprocess.DEVNULL)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
