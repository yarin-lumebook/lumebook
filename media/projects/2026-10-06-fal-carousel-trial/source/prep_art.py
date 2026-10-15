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

# Photo-real direction (chosen by the user after the style tests). slide -> original in generated-assets/.
# Slides 1-5 are daylight, 6-7 dim violet evening. Slide 3 reuses the style test image.
ART = {1: "p1.png", 2: "p2.png", 3: "style-2-nb2.png", 4: "p4.png", 5: "p5.png", 6: "p6.png", 7: "p7.png"}
# push the photo down by N px; the plain wall above is mirrored to fill the gap (keeps type off faces)
PUSH = {1: 80, 2: 90, 3: 170, 6: 90}
PARK_FADE = 170        # slide 4: px over which the treetops fade into cream


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


def cover(im, dy=0):
    """Scale to cover 1080x1350, centre-crop. No colour changes: the photographs keep their own grade."""
    sc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))
    if dy:
        canvas = Image.new("RGB", (W, H))
        canvas.paste(im.crop((0, 0, W, dy)).transpose(Image.FLIP_TOP_BOTTOM), (0, 0))
        canvas.paste(im.crop((0, 0, W, H - dy)), (0, dy))
        im = canvas
    return im


def park(im):
    """p4 came back with a flat wall-coloured slab pasted over the top third of the sky (hard seam).
    Find the seam, keep only the real photograph below it, and fade its top into cream."""
    a = np.asarray(im.convert("L"), dtype=np.float32)
    rows = np.abs(np.diff(a.mean(axis=1)))
    seam = int(np.argmax(rows[300:600])) + 301
    real = im.crop((0, seam + 2, im.width, im.height))
    sc = W / real.width
    real = real.resize((W, round(real.height * sc)), Image.LANCZOS)
    top_rgb = tuple(int(v) for v in np.asarray(im.crop((0, 10, im.width, 40)).convert("RGB")).reshape(-1, 3).mean(0))
    canvas = Image.new("RGB", (W, H), top_rgb)
    y0 = H - real.height
    canvas.paste(real, (0, y0))
    ramp = np.clip(np.arange(real.height) / PARK_FADE, 0, 1)[:, None]            # 0 = cream, 1 = photo
    mask = Image.fromarray((np.repeat(ramp, W, 1) * 255).astype(np.uint8))
    base = Image.new("RGB", real.size, top_rgb)
    canvas.paste(Image.composite(real, base, mask), (0, y0))
    print(f"  slide 4: seam at source row {seam}, photograph placed at y={y0}")
    return canvas


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    paper_grain()
    print("wrote images/paper-grain.png")
    for n, name in ART.items():
        im = Image.open(GEN / name).convert("RGB")
        out = park(im) if n == 4 else cover(im, PUSH.get(n, 0))
        out.save(IMG / f"slide-{n:02d}.jpg", quality=95)
        print(f"slide {n}: {name} -> images/slide-{n:02d}.jpg")
