#!/usr/bin/env python3
"""Render the carousel to PNGs and build the review sheets.

Usage (from carousel/fal-carousel-trial/):
    python3 source/render.py            # all 7 slides + contact sheet + 25% sheet
    python3 source/render.py 3 5        # only slides 3 and 5 (sheets are rebuilt too)

Needs Google Chrome (headless) and Pillow (pip install pillow).
Every slide is a <section class="slide" data-n="N"> in source/carousel.html;
carousel.html?s=N shows only that slide at 1080x1350.
"""
import subprocess, sys, tempfile, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent          # carousel/fal-carousel-trial/
SRC = ROOT / "source"
OUT = ROOT / "slides"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H, N = 1080, 1350, 7
PROFILE = tempfile.mkdtemp(prefix="lumebook-chrome-")   # own profile, so it works while regular Chrome is open


def render(n: int, page: str = "carousel.html", out: Path = None) -> Path:
    out = out or OUT / f"{n:02d}.png"
    url = (SRC / page).as_uri() + f"?s={n}"
    args = [
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio",
        f"--user-data-dir={PROFILE}", "--force-device-scale-factor=1", f"--window-size={W},{H}",
        "--virtual-time-budget=6000", "--allow-file-access-from-files",
        f"--screenshot={out}", url,
    ]
    if out.exists():
        out.unlink()
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):                       # Chrome sometimes writes the PNG but never exits
        time.sleep(0.5)
        if proc.poll() is not None or (out.exists() and out.stat().st_size > 0):
            time.sleep(0.5)
            break
    if proc.poll() is None:
        proc.kill()
    im = Image.open(out)
    if im.size != (W, H):
        im = im.crop((0, 0, W, H))   # guard: never ship a wrong-size PNG
        im.save(out)
    assert Image.open(out).size == (W, H), f"{out} is {Image.open(out).size}"
    return out


def contact_sheet():
    font = ImageFont.truetype(str(SRC / "fonts/Assistant-VariableFont_wght.ttf"), 26)
    scale, gap, pad = 0.34, 28, 48
    tw, th = int(W * scale), int(H * scale)
    cols = 4
    rows = 2
    sheet = Image.new("RGB", (pad * 2 + cols * tw + (cols - 1) * gap, pad * 2 + rows * (th + 44) + (rows - 1) * gap), "#E9E2D6")
    d = ImageDraw.Draw(sheet)
    for i in range(N):
        r, c = divmod(i, cols)
        x = pad + c * (tw + gap)
        y = pad + r * (th + 44 + gap)
        sheet.paste(Image.open(OUT / f"{i+1:02d}.png").convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y + th + 10), f"{i+1:02d}", fill="#4B4062", font=font)
    sheet.save(ROOT / "contact-sheet.png")

    # Phone-scale check: every slide at 25% (270x337), the size of a thumbnail in a busy feed
    q = 0.25
    qw, qh = int(W * q), int(H * q)
    strip = Image.new("RGB", (N * qw + (N + 1) * 16, qh + 32), "#E9E2D6")
    for i in range(N):
        strip.paste(Image.open(OUT / f"{i+1:02d}.png").convert("RGB").resize((qw, qh), Image.LANCZOS), (16 + i * (qw + 16), 16))
    strip.save(SRC / "qa-25pct.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    which = [int(a) for a in sys.argv[1:]] or list(range(1, N + 1))
    for n in which:
        print("rendered", render(n).relative_to(ROOT))
    if all((OUT / f"{i:02d}.png").exists() for i in range(1, N + 1)):
        contact_sheet()
        print("built contact-sheet.png and source/qa-25pct.png")
