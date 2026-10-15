"""Tile a fixed crop of a video over a time window, labelled with time and the word being spoken.
usage: facestrip.py VIDEO OUT.jpg x0,y0,x1,y1 T0 T1 STEP_FRAMES CONFIG_JSON [tile_w] [cols]"""
import sys, json, subprocess, tempfile, glob, os
from pathlib import Path
from PIL import Image, ImageDraw
video, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = [int(v) for v in sys.argv[3].split(',')]
t0, t1, step = float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
cfg = json.loads(Path(sys.argv[7]).read_text()); words = [(w, a+cfg.get('shift', 0), b+cfg.get('shift', 0)) for w, a, b in cfg.get('words', [])]
tw = int(sys.argv[8]) if len(sys.argv) > 8 else 160; cols = int(sys.argv[9]) if len(sys.argv) > 9 else 12
fps = eval(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=avg_frame_rate', '-of', 'csv=p=0', video], capture_output=True, text=True).stdout.strip())
d = tempfile.mkdtemp()
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(t0), '-to', str(t1), '-i', video, '-vf', f'crop={x1-x0}:{y1-y0}:{x0}:{y0},select=not(mod(n\\,{step})),setpts=N/FRAME_RATE/TB', '-q:v', '3', os.path.join(d, 'f_%04d.jpg')], check=True)
fs = sorted(glob.glob(os.path.join(d, 'f_*.jpg'))); th = round(tw*(y1-y0)/(x1-x0)); rows = (len(fs)+cols-1)//cols
sh = Image.new('RGB', (cols*tw, rows*(th+14)), 'white'); dr = ImageDraw.Draw(sh)
for k, f in enumerate(fs):
    t = t0 + k*step/fps; w = next((n for n, a, b in words if a <= t <= b), '')
    x, y = (k % cols)*tw, (k//cols)*(th+14); sh.paste(Image.open(f).resize((tw, th), Image.LANCZOS), (x, y)); dr.text((x+2, y+th+1), f'{t:.2f} {w}', fill='black')
sh.save(out, quality=88); print(out, sh.size, len(fs), 'tiles')
