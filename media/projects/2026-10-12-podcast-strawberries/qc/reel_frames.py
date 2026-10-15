"""Sheet of the reel: one frame at the middle of every word caption plus a few uncaptioned moments.
usage: reel_frames.py REEL.mp4 REEL_RESOLVED.json OUT.jpg [extra times...]"""
import json, subprocess, sys, tempfile, os
from PIL import Image, ImageDraw
video, R, out = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]; extra = [float(x) for x in sys.argv[4:]]
pts = sorted([((c['start'] + c['end']) / 2, 'word') for c in R['captions']] + [(t, '') for t in extra]); d = tempfile.mkdtemp()
tw, th, cols = 213, 379, 9; rows = (len(pts) + cols - 1) // cols
sh = Image.new('RGB', (cols * tw, rows * (th + 14)), 'white'); dr = ImageDraw.Draw(sh)
for k, (t, kind) in enumerate(pts):
    f = os.path.join(d, f'{k}.png'); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-vf', f"select='gte(t,{t:.4f})',scale={tw}:{th}", '-frames:v', '1', f], check=True)
    x, y = (k % cols) * tw, (k // cols) * (th + 14); sh.paste(Image.open(f), (x, y)); dr.text((x + 3, y + th + 1), f'{t:.2f}s {kind}', fill='black')
sh.save(out, quality=90); print(out, sh.size)
