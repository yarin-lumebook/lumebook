#!/usr/bin/env python3
"""The GPT Image 2.5 Flare (high) carousel in the clean layout: centred Heebo Black, two lines.

    python3 source/flare_carousel.py

Writes flare-carousel/01.png … 07.png and flare-carousel/contact-sheet.png.
Slide 5 (cmp-gpt25) is the character reference; the other six are Flare edits of it (jobs f1 … f7).
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC, GEN, OUT = ROOT / "source", ROOT / "generated-assets", ROOT / "flare-carousel"
sys.path.insert(0, str(SRC))
import prep_art as pa
import render
from clean_text import CSS

# Copy from the user (7 Oct 2026). head = big Heebo Black lines; sub = smaller lines under it.
COPY = {
    1: {"head": ["אח חדש בדרך?"], "sub": ["5 דברים שכדאי לשים לב אליהם", "אצל הילד הגדול"]},
    2: {"head": ["לפני שמבקשים ממנו לשמוח,", "תנו מקום לכל מה שהוא מרגיש"]},
    3: {"head": ["מותר לו לאהוב את התינוק", "וגם להתגעגע לחיים שהיו קודם"]},
    4: {"head": ["הוא לא מאבד", "את המקום שלו במשפחה", "הוא לומד איך", "המקום שלו משתנה"]},
    5: {"head": ["גם אם הוא עכשיו ״הגדול״,", "הוא עדיין יכול להרגיש", "שמותר לו להיות קטן"]},
    6: {"head": ["תנו לשינוי לקרות", "בקצב שלו"]},
    7: {"head": ["אל תחכו לרגע", "שבו הכול משתנה"], "sub": ["הכינו אותו כבר עכשיו עם סיפור אישי", "שבו הוא הגיבור · הקישור בביו"]},
}
EXTRA_CSS = """
.sub{margin-top:22px;font-family:"Heebo",sans-serif;font-weight:900;font-size:50px;line-height:1.15;color:var(--ink);opacity:.82}
.arrow{position:absolute;left:50%;transform:translateX(-50%);bottom:56px;width:88px;height:88px;border-radius:50%;background:#F8F0E1;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(11,5,24,.28)}
.arrow svg{width:44px;height:44px}
.arrow path{fill:none;stroke:#1D1039;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}
"""
ARROW = '<div class="arrow"><svg viewBox="0 0 44 44"><path d="M36 22H8M19 10 7 22l12 12"/></svg></div>'

# slide -> (generated image, dark evening slide?, push-down px so the headline clears heads)
SLIDES = {1: ("f1", False, 0), 2: ("f2", False, 90), 3: ("f3", False, 150), 4: ("f4", False, 240),
          5: ("cmp-gpt25", False, 130), 6: ("f6", True, 170), 7: ("f7", True, 170)}


TEXT_TOP, GAP = 150, 60          # headline starts at y=150; keep at least 60px of clear wall under the text


def text_bottom(c, size):
    h = len(c["head"]) * size * 1.08
    if c.get("sub"):
        h += 22 + len(c["sub"]) * 50 * 1.15
    return TEXT_TOP + h + 12      # +12: descenders


def subject_top(im):
    """First row (canvas px) where the picture stops being plain wall/sky.
    Each row is compared with a smooth quadratic 'wall' fitted across it (walls have soft left-right shading);
    a row where more than 2% of pixels deviate strongly from that fit is where hair, faces or furniture begin.
    Checked against the visible head positions of all seven Flare images (7 Oct 2026)."""
    a = np.asarray(im.convert("RGB").filter(ImageFilter.GaussianBlur(3)), dtype=np.float32)[:, 40:1040]
    x = np.linspace(-1, 1, a.shape[1])
    X = np.stack([np.ones_like(x), x, x ** 2], 1)
    P = np.linalg.pinv(X)
    for r in range(20, a.shape[0]):
        fit = X @ (P @ a[r])
        if (np.sqrt(((a[r] - fit) ** 2).sum(-1)) > 18).mean() > 0.02:
            return r
    return a.shape[0]


def place(job, c, size):
    """Smallest push-down (in 10px steps) that leaves GAP px between the text and the first character pixel."""
    src = Image.open(GEN / f"{job}.png").convert("RGB")
    need = text_bottom(c, size) + GAP
    for dy in range(0, 320, 10):      # beyond ~300px the mirrored wall would start copying heads
        art = pa.cover(src, dy)
        top = subject_top(art)
        if top >= need:
            return art, dy, top, need
    return art, dy, top, need


def main():
    (OUT / "art").mkdir(parents=True, exist_ok=True)
    heebo = ImageFont.truetype(str(SRC / "fonts/Heebo-Black.ttf"), 96)
    secs = []
    for n, (job, dark, dy) in SLIDES.items():
        c = COPY[n]
        size = min(96, int(900 / max(heebo.getlength(l) for l in c["head"]) * 96))
        art, dy, top, need = place(job, c, size)
        art.save(OUT / "art" / f"{n:02d}.jpg", quality=95)
        print(f"slide {n}: text ends ~{need - GAP:.0f}px, characters start {top}px, art pushed down {dy}px")
        sub = f'<div class="sub">{"<br>".join(c["sub"])}</div>' if c.get("sub") else ""
        arrow = ARROW if n < 7 else ""
        secs.append(f'<section class="slide{" dark" if dark else ""}" data-n="{n}"><img class="art" src="../flare-carousel/art/{n:02d}.jpg" alt="">'
                    f'<div class="veil"></div><div class="copy"><h2 style="font-size:{size}px">{"<br>".join(c["head"])}</h2>{sub}</div>{arrow}</section>')
    js = "<script>const s=new URLSearchParams(location.search).get('s');if(s){document.body.classList.add('single');document.querySelector('.slide[data-n=\"'+s+'\"]').classList.add('on');}</script>"
    (SRC / "flare-carousel.html").write_text(f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>Flare carousel</title><style>{CSS}{EXTRA_CSS}</style></head><body>{"".join(secs)}{js}</body></html>', encoding="utf-8")
    files = []
    for n in SLIDES:
        out = OUT / f"{n:02d}.png"
        render.render(n, "flare-carousel.html", out)
        assert Image.open(out).size == (1080, 1350)
        files.append(out)
    tw, th = 360, 450
    sheet = Image.new("RGB", (64 * 2 + 4 * tw + 3 * 24, 64 * 2 + 2 * th + 24), "#E9E2D6")
    for k, p in enumerate(files):
        sheet.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (64 + (k % 4) * (tw + 24), 64 + (k // 4) * (th + 24)))
    sheet.save(OUT / "contact-sheet.png")
    print("built flare-carousel/ (7 slides + contact sheet)")


if __name__ == "__main__":
    main()
