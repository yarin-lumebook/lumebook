"""Evenly spaced full-frame contact sheet. usage: sheet.py VIDEO OUT.jpg N COLS [tile_w] [t0 t1]"""
import sys, subprocess, tempfile, os
from PIL import Image, ImageDraw
v, out, n, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); tw = int(sys.argv[5]) if len(sys.argv) > 5 else 480
r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames,avg_frame_rate', '-of', 'csv=p=0', v], capture_output=True, text=True).stdout.strip().split(',')
dur = int(r[1]) / eval(r[0])
t0 = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0; t1 = float(sys.argv[7]) if len(sys.argv) > 7 else dur - 0.08
d = tempfile.mkdtemp(); th = round(tw*9/16); rows = (n+cols-1)//cols
sh = Image.new('RGB', (cols*tw, rows*(th+14)), 'white'); dr = ImageDraw.Draw(sh)
for k in range(n):
    t = t0 + (t1-t0)*k/(n-1); f = os.path.join(d, f'{k}.jpg')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', v, '-frames:v', '1', '-vf', f'scale={tw}:{th}', '-q:v', '3', f], check=True)
    x, y = (k % cols)*tw, (k//cols)*(th+14); sh.paste(Image.open(f), (x, y)); dr.text((x+3, y+th+1), f'{t:.2f}s', fill='black')
sh.save(out, quality=88); print(out, sh.size, f'dur={dur:.2f}')
