#!/usr/bin/env python3
"""Turn the original fal.ai outputs into slide-ready art (no AI involved here).

    python3 source/prep_art.py

1. paper-grain.png: a seeded, tileable paper-fibre texture multiplied over every
   slide so all seven images sit on the same physical-looking paper.
2. For each entry in ART below: crop/scale the original from generated-assets/
   to 1080x1350, then pull its paper tone to the shared --paper colour so the
   seven generations (which drift slightly in white balance) read as one book.
Originals in generated-assets/ are never modified.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "generated-assets"
IMG = ROOT / "source" / "images"
W, H = 1080, 1350
PAPER = np.array([243, 234, 220], dtype=np.float32)   # --paper  #F3EADC

# slide -> (original file, horizontal focus 0..1, push-down in canvas px, fixes)
# push-down moves the art lower and mirrors the plain paper above it, freeing the top for type.
ART = {
    1: ("cover-A-nb2.png", 0.5, 0,   []),
    2: ("s2-fix.png",      0.5, 60,  ["warm_floor"]),   # the leg-removal edit cooled the floor to blue-grey
    3: ("s3.png",          0.5, 80,  []),
    4: ("s4.png",          0.5, 130, []),
    5: ("s5.png",          0.5, 40,  []),
    6: ("s6.png",          0.5, 180, []),
}
# slide 7 uses a square crop of s7.png as a "page" of the 22x22 cm book: (x, y, size) in source px
PAGE_7 = ("s7.png", (300, 452, 628))


def paper_grain(size=540, seed=7):
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 1, (size, size)).astype(np.float32)
    img = Image.fromarray(((base - base.min()) / (base.max() - base.min()) * 255).astype(np.uint8))
    fine = np.asarray(img.filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255
    coarse = np.asarray(img.filter(ImageFilter.GaussianBlur(6)), dtype=np.float32) / 255
    # long soft fibres: stretch noise horizontally and vertically
    fib = rng.normal(0, 1, (size // 8, size)).astype(np.float32)
    fib = np.asarray(Image.fromarray(((fib - fib.min()) / np.ptp(fib) * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC), dtype=np.float32) / 255
    g = 0.55 * fine + 0.30 * coarse + 0.15 * fib
    g = (g - g.mean()) / g.std()
    lum = 1.0 - np.clip(np.abs(g) * 0.022 + np.clip(g, 0, None) * 0.018, 0, 0.08)   # multiply layer: 0.92..1.0
    rgb = np.stack([lum, lum * 0.995, lum * 0.985], -1)
    Image.fromarray((rgb * 255).astype(np.uint8)).save(IMG / "paper-grain.png")


def fit(im: Image.Image, fx=0.5, dy=0) -> Image.Image:
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(round(im.width * fx - W / 2), 0), im.width - W)
    im = im.crop((x, 0, x + W, H))
    if dy:
        top = im.crop((0, 0, W, dy)).transpose(Image.FLIP_TOP_BOTTOM)   # mirrored blank paper, seamless
        canvas = Image.new("RGB", (W, H))
        canvas.paste(top, (0, 0))
        canvas.paste(im.crop((0, 0, W, H - dy)), (0, dy))
        im = canvas
    return im


def warm_floor(im: Image.Image, from_row=0.755, keep=(620, 900, 850, 1075)) -> Image.Image:
    """The leg-removal edit repainted the floor neutral grey; pull it back to the warm floor of the
    pre-edit image. Only pale, un-warm pixels below the baseboard change; `keep` (x0,y0,x1,y1 in
    source px) protects the lilac stack of baby clothes."""
    a = np.asarray(im, dtype=np.float32)
    h, w = a.shape[:2]
    lum = a.mean(-1)
    warmth = a[..., 0] - a[..., 2]
    m = np.clip((20 - warmth) / 14, 0, 1) * (lum > 120) * (np.arange(h)[:, None] > h * from_row)
    x0, y0, x1, y1 = keep
    m[y0:y1, x0:x1] = 0
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), dtype=np.float32)[..., None] / 255
    src = np.median(a[m[..., 0] > 0.7], axis=0)
    target = np.array([238, 227, 213], dtype=np.float32)            # floor of the same scene before the edit (s2.png)
    corrected = np.clip(a * (target / np.maximum(src, 1)), 0, 255)
    return Image.fromarray((a * (1 - m) + corrected * m).astype(np.uint8))


def match_paper(im: Image.Image) -> Image.Image:
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    lum = a.mean(-1)
    sat = a.max(-1) - a.min(-1)
    mask = (lum > np.percentile(lum, 70)) & (sat < np.percentile(sat, 60))   # bright, low-chroma = paper
    ref = np.median(a[mask], axis=0) if mask.sum() > 5000 else np.median(a.reshape(-1, 3), axis=0)
    gain = PAPER / np.maximum(ref, 1)
    gain = 1 + (gain - 1) * 0.85                     # don't over-correct
    out = np.clip(a * gain, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    paper_grain()
    print("wrote images/paper-grain.png")
    for n, (name, fx, dy, fixes) in ART.items():
        im = Image.open(GEN / name).convert("RGB")
        if "warm_floor" in fixes:
            im = warm_floor(im)
        out = match_paper(fit(im, fx, dy))
        out.save(IMG / f"slide-{n:02d}.jpg", quality=95)
        print(f"slide {n}: {name} -> images/slide-{n:02d}.jpg")
    name, (x, y, size) = PAGE_7
    page = match_paper(Image.open(GEN / name).convert("RGB").crop((x, y, x + size, y + size)))
    page.save(IMG / "slide-07-page.jpg", quality=95)
    print(f"slide 7: {name} square crop -> images/slide-07-page.jpg")
