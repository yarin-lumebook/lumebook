#!/usr/bin/env python3
"""Same CGI slide 5 prompt on every model, in the clean Heebo layout, sorted by price.

    python3 source/model_compare.py

Writes model-compare/<job>.png and model-compare/sheet.png.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC, GEN, OUT = ROOT / "source", ROOT / "generated-assets", ROOT / "model-compare"
sys.path.insert(0, str(SRC))
import prep_art as pa
import render
from clean_text import CSS, COPY

# job -> (label, price per image in USD, seconds)
JOBS = [
    ("cmp-recraft", "Recraft 4.1 Flash"),
    ("cmp-flux3", "Flux 3"),
    ("cmp-sd5flash", "Seedream 5.0 Flash"),
    ("cmp-gpt25", "GPT Image 2.5 Flare (high)"),
    ("cmp-gpt25sun", "GPT Image 2.5 Sunburst (high)"),
    ("cmp-gpt2", "GPT Image 2 (medium)"),
    ("cmp-ideogram", "Ideogram 4.5 (medium)"),
    ("cmp-sd5", "Seedream 5.0 Pro"),
    ("cgi-5-nb2", "Nano Banana 2"),
    ("cgi-5-cute", "Nano Banana 2 + cuter edit (2 calls)"),
    ("cmp-nbpro", "Nano Banana Pro"),
]


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "art").mkdir(exist_ok=True)
    log = {}
    for l in open(GEN / "generation-log.jsonl", encoding="utf-8"):
        r = json.loads(l); log[r["job"]] = r
    cost = {j: log[j]["est_cost_usd"] for j, _ in JOBS}
    cost["cgi-5-cute"] += log["cgi-5-nb2"]["est_cost_usd"]           # the edit was built on cgi-5-nb2
    jobs = sorted(JOBS, key=lambda t: cost[t[0]])
    l1, l2 = COPY[5]
    secs = []
    for i, (job, _) in enumerate(jobs, 1):
        im = Image.open(GEN / f"{job}.png").convert("RGB")
        pa.cover(im, 60 if job == "cgi-5-cute" else 0).save(OUT / "art" / f"{i:02d}.jpg", quality=92)
        secs.append(f'<section class="slide" data-n="{i}"><img class="art" src="../model-compare/art/{i:02d}.jpg" alt="">'
                    f'<div class="veil"></div><div class="copy"><h2 style="font-size:96px">{l1}<br>{l2}</h2></div></section>')
    js = "<script>const s=new URLSearchParams(location.search).get('s');if(s){document.body.classList.add('single');document.querySelector('.slide[data-n=\"'+s+'\"]').classList.add('on');}</script>"
    (SRC / "model-compare.html").write_text(f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>Model comparison</title><style>{CSS}</style></head><body>{"".join(secs)}{js}</body></html>', encoding="utf-8")
    files = []
    for i, (job, _) in enumerate(jobs, 1):
        out = OUT / f"{i:02d}-{job}.png"
        render.render(i, "model-compare.html", out)
        files.append(out)
    def font(p, s, w):
        f = ImageFont.truetype(str(SRC / "fonts" / p), s); f.set_variation_by_axes([w]); return f
    tw, th, cols = 340, 425, 6
    rows = (len(files) + cols - 1) // cols
    W = 64 * 2 + cols * tw + (cols - 1) * 22
    sheet = Image.new("RGB", (W, 150 + rows * (th + 110)), "#F3EADC")
    d = ImageDraw.Draw(sheet)
    d.text((64, 40), "Same prompt, every model, cheapest to most expensive", font=font("Rubik-VariableFont_wght.ttf", 44, 600), fill="#1D1039")
    d.text((64, 98), "CGI slide 5, cute faces, empty top for type. One image per model, no cherry-picking. Prices from fal.ai pricing tool / model pages, 6 to 7 Oct 2026.", font=font("Assistant-VariableFont_wght.ttf", 22, 500), fill="#4B4062")
    for k, ((job, label), p) in enumerate(zip(jobs, files)):
        x, y = 64 + (k % cols) * (tw + 22), 150 + (k // cols) * (th + 110)
        sheet.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
        r = log[job]
        d.text((x, y + th + 10), label, font=font("Assistant-VariableFont_wght.ttf", 22, 800), fill="#1D1039")
        d.text((x, y + th + 40), f"${cost[job]:.3f} · {r['wall_seconds']:.0f} s", font=font("Assistant-VariableFont_wght.ttf", 21, 600), fill="#4B4062")
    sheet.save(OUT / "sheet.png")
    print("built model-compare/sheet.png")


if __name__ == "__main__":
    main()
