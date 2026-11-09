"""Verification strip: frames at chosen timestamps of one Reel, tiled left to right with time labels.
Usage: strip.py CODE t1 t2 ... (seconds)  ->  media/.../analysis/CODE/check_strip.jpg"""
import sys, subprocess, os
from PIL import Image, ImageDraw, ImageFont
M = '/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-11-09-matan-nistor-reels'
code, ts = sys.argv[1], [float(t) for t in sys.argv[2:]]
v = f'{M}/videos/{code}.mp4'
tmp = f'{M}/analysis/{code}/_strip'
os.makedirs(tmp, exist_ok=True)
ims = []
for i, t in enumerate(ts):
    p = f'{tmp}/{i:02d}.jpg'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t), '-i', v, '-frames:v', '1', '-vf', 'scale=-2:420', '-q:v', '3', p])
    if os.path.exists(p): ims.append((t, Image.open(p)))
font = ImageFont.load_default(size=24)
w = sum(im.width for _, im in ims) + 6 * (len(ims) - 1)
sh = Image.new('RGB', (w, 450), (17, 17, 20)); d = ImageDraw.Draw(sh); x = 0
for t, im in ims:
    sh.paste(im, (x, 30)); d.text((x + 4, 2), f'{int(t // 60):02d}:{t % 60:05.2f}', fill=(255, 230, 120), font=font); x += im.width + 6
out = f'{M}/analysis/{code}/check_strip.jpg'
sh.save(out, quality=85); print(out, len(ims))
