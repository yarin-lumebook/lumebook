#!/usr/bin/env python3
"""Put every fal.ai generation into the clean layout: centred Heebo Black, two lines,
no quote marks or full stops, no numbering, wordmark or thread.

    python3 source/clean_text.py

Writes clean-text/art/*.jpg, source/clean-text.html, clean-text/NN-<job>.png and clean-text/overview.png.
Edit COPY to change the words; edit ITEMS to change placement (push-down) or light/dark.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC, GEN, OUT = ROOT / "source", ROOT / "generated-assets", ROOT / "clean-text"
sys.path.insert(0, str(SRC))
import prep_art as pa                      # cover(), park()
import render

# Two lines per slide (tightened from the brief so each fits two lines)
COPY = {
    1: ("עוד מעט נולד תינוק", "וגם הגדול נולד מחדש"),
    2: ("לפני שמבקשים ממנו לשמוח", "תנו מקום לכל מה שהוא מרגיש"),
    3: ("מותר לך לאהוב אותו", "וגם להתגעגע למה שהיה"),
    4: ("יש דברים שיישארו", "רק שלנו"),
    5: ("אתה לא צריך להיות", "גדול כל הזמן"),
    6: ("בסיפור הוא מתאמן על הרגע", "לפני שהוא מגיע"),
    7: ("הוא לא מאבד את המקום שלו", "הוא מגלה תפקיד חדש"),
}
CTA = "צרו תצוגה מקדימה בחינם · הקישור בביו"

# job -> (slide, dark?, push-down px). Order = generation order in generation-log.jsonl.
ITEMS = {
    "cover-B-nb2": (1, True, 0), "cover-A-nb2": (1, False, 0),
    "s5": (5, False, 40), "s6": (6, False, 180), "s4": (4, False, 130), "s7": (7, False, 0),
    "s3": (3, False, 80), "s2": (2, False, 60), "s2-fix": (2, False, 60),
    "style-4-mixed": (3, False, 0), "style-3-painted-lumebook": (3, False, 0),
    "style-1-3d-cartoon": (3, False, 0), "style-2-photoreal": (3, False, 0),
    "style-3-nb2": (3, False, 0), "style-2-nb2": (3, False, 170),
    "p1": (1, False, 80), "p7": (7, True, 0), "p4": (4, False, 0), "p2": (2, False, 90),
    "p5": (5, False, 0), "p6": (6, True, 90),
    "cgi-5-schnell": (5, False, 0), "cgi-5-nb2": (5, False, 0), "cgi-5-cute": (5, False, 60),
}

CSS = """
@font-face{font-family:"Heebo";src:url("fonts/Heebo-Black.ttf") format("truetype");font-weight:900;font-display:block}
@font-face{font-family:"Assistant";src:url("fonts/Assistant-VariableFont_wght.ttf") format("truetype");font-weight:200 800;font-display:block}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#d9d2c6}
body.single .slide:not(.on){display:none}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:#F3EADC;--ink:#1D1039;--veil:243,234,220}
.slide.dark{--ink:#F8F0E1;--veil:11,5,24;background:#0B0518}
.art{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
/* soft top veil: invisible on clean walls, keeps type readable on busy drafts */
.veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(var(--veil),.88) 0,rgba(var(--veil),.7) 20%,rgba(var(--veil),0) 40%)}
.copy{position:absolute;top:150px;left:90px;right:90px;text-align:center;direction:rtl}
h2{font-family:"Heebo",sans-serif;font-weight:900;font-size:96px;line-height:1.08;letter-spacing:-.01em;color:var(--ink);white-space:nowrap}
.cta{margin-top:26px;font-family:"Assistant",sans-serif;font-weight:800;font-size:36px;color:var(--ink)}
"""
FIT = """<script>
const s=new URLSearchParams(location.search).get('s');
if(s){document.body.classList.add('single');document.querySelector('.slide[data-n="'+s+'"]').classList.add('on');}
</script>"""


def main():
    (OUT / "art").mkdir(parents=True, exist_ok=True)
    order = [json.loads(l)["job"] for l in open(GEN / "generation-log.jsonl", encoding="utf-8")]
    order = [j for j in order if j in ITEMS]
    heebo = ImageFont.truetype(str(SRC / "fonts/Heebo-Black.ttf"), 96)
    size = {n: min(96, int(900 / max(heebo.getlength(a), heebo.getlength(b)) * 96)) for n, (a, b) in COPY.items()}
    sections = []
    for i, job in enumerate(order, 1):
        slide, dark, dy = ITEMS[job]
        im = Image.open(GEN / f"{job}.png").convert("RGB")
        art = pa.park(im) if job == "p4" else pa.cover(im, dy)
        art.save(OUT / "art" / f"{i:02d}.jpg", quality=92)
        l1, l2 = COPY[slide]
        cta = f'<div class="cta">{CTA}</div>' if slide == 7 else ""
        sections.append(f'<section class="slide{" dark" if dark else ""}" data-n="{i}"><img class="art" src="../clean-text/art/{i:02d}.jpg" alt="">'
                        f'<div class="veil"></div><div class="copy"><h2 style="font-size:{size[slide]}px">{l1}<br>{l2}</h2>{cta}</div></section>')
    html = f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>Clean text versions</title><style>{CSS}</style></head><body>{"".join(sections)}{FIT}</body></html>'
    (SRC / "clean-text.html").write_text(html, encoding="utf-8")
    files = []
    for i, job in enumerate(order, 1):
        out = OUT / f"{i:02d}-{job}.png"
        render.render(i, "clean-text.html", out)
        files.append(out)
        print("rendered", out.name)
    # overview sheet
    f = ImageFont.truetype(str(SRC / "fonts/Assistant-VariableFont_wght.ttf"), 22); f.set_variation_by_axes([700])
    tw, th, cols = 300, 375, 6
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (64 * 2 + cols * tw + (cols - 1) * 20, 64 + rows * (th + 56)), "#F3EADC")
    d = ImageDraw.Draw(sheet)
    for k, p in enumerate(files):
        x, y = 64 + (k % cols) * (tw + 20), 40 + (k // cols) * (th + 56)
        sheet.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y + th + 8), p.stem, font=f, fill="#1D1039")
    sheet.save(OUT / "overview.png")
    print("built clean-text/overview.png")


if __name__ == "__main__":
    main()
