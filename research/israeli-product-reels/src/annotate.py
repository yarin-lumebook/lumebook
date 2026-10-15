"""Annotated frame strips for the deep-dive breakdowns.

python annotate.py   (uses the watch-video venv for Pillow)
Reads annotations.json: {CODE: {"handle": "...", "frames": [[seconds, "label"], ...]}}
Writes media/projects/2026-10-15-israeli-product-reels/annotated/CODE.jpg
Frames come from analysis/CODE/frames (one per second, file name = timestamp).
"""
import json
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.normpath(os.path.join(HERE, '../../../media/projects/2026-10-15-israeli-product-reels'))
H = 520            # frame height in the strip
LABEL_H = 150
GAP = 10

font = ImageFont.load_default(size=19)
small = ImageFont.load_default(size=17)
bold = ImageFont.load_default(size=24)


def nearest(code, t):
    d = os.path.join(MEDIA, 'analysis', code, 'frames')
    files = [f for f in os.listdir(d) if f.startswith('t') and f.endswith('.jpg')]
    best = min(files, key=lambda f: abs(float(f[1:-4]) - t))
    return os.path.join(d, best), float(best[1:-4])


def strip(code, spec):
    tiles = []
    for t, label in spec['frames']:
        path, real_t = nearest(code, t)
        im = Image.open(path)
        im = im.resize((int(im.width * H / im.height), H))
        tiles.append((im, real_t, label))
    w = sum(im.width for im, _, _ in tiles) + GAP * (len(tiles) - 1)
    total_h = 40 + H + LABEL_H + 34
    sheet = Image.new('RGB', (w, total_h), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    x = 0
    for im, t, label in tiles:
        dr.text((x + 4, 8), f'{int(t // 60)}:{t % 60:04.1f}', fill=(20, 20, 20), font=bold)
        sheet.paste(im, (x, 40))
        chars = max(14, int(im.width / 9.6))
        y = 40 + H + 8
        for line in textwrap.wrap(label, chars)[:7]:
            dr.text((x + 4, y), line, fill=(30, 30, 30), font=font)
            y += 21
        x += im.width + GAP
    src = f"Source: @{spec['handle']} · instagram.com/reel/{code}/ · frames sampled 15 Oct 2026 for internal research, timestamps ±0.5 s"
    dr.text((4, total_h - 28), src, fill=(90, 90, 90), font=small)
    os.makedirs(os.path.join(MEDIA, 'annotated'), exist_ok=True)
    out = os.path.join(MEDIA, 'annotated', f'{code}.jpg')
    sheet.save(out, quality=86)
    print(out, sheet.size)


if __name__ == '__main__':
    specs = json.load(open(os.path.join(HERE, 'annotations.json'), encoding='utf-8'))
    for code, spec in specs.items():
        strip(code, spec)
