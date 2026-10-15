"""10 evenly spaced frames per Reel in one row, for my own check of the agents' coding.
Writes media/projects/2026-10-15-israeli-product-reels/analysis/CODE/review.jpg"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
MEDIA = '/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-15-israeli-product-reels/analysis'
font = ImageFont.load_default(size=22)
for code in sys.argv[1:]:
    d = f'{MEDIA}/{code}/frames'
    files = sorted((float(f[1:-4]), f) for f in os.listdir(d) if f.startswith('t'))
    n = 10
    pick = [files[round(i * (len(files) - 1) / (n - 1))] for i in range(n)]
    ims = [Image.open(f'{d}/{f}') for _, f in pick]
    ims = [im.resize((int(im.width * 420 / im.height), 420)) for im in ims]
    w = sum(im.width for im in ims) + 6 * (n - 1)
    sh = Image.new('RGB', (w, 452), (20, 20, 20))
    dr = ImageDraw.Draw(sh)
    x = 0
    for (t, _), im in zip(pick, ims):
        sh.paste(im, (x, 32)); dr.text((x + 4, 4), f'{int(t // 60)}:{t % 60:04.1f}', fill=(255, 230, 120), font=font); x += im.width + 6
    sh.save(f'{MEDIA}/{code}/review.jpg', quality=82)
    print(code, sh.size)
