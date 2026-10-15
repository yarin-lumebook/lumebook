"""Sheet of the frame just before and just after every cut of a finished export.
usage: final_cut_frames.py VIDEO RESOLVED_TIMELINE.json OUT.jpg"""
import json, subprocess, sys, tempfile, os
from PIL import Image, ImageDraw
video, R, out = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]; d = tempfile.mkdtemp()
def grab(t, name):
    f = os.path.join(d, name + '.png'); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-vf', f"select='gte(t,{t:.4f})'", '-frames:v', '1', f], check=True); return Image.open(f).convert('RGB')
cuts = [s['start'] for s in R['segments'][1:]]
sh = Image.new('RGB', (1920, ((len(cuts)*2+3)//4)*(270+14)), 'white'); dr = ImageDraw.Draw(sh)
for k, c in enumerate(cuts):
    for j, t in enumerate((c - 0.05, c + 0.005)):
        idx = k*2 + j; x, y = (idx % 4)*480, (idx//4)*284
        sh.paste(grab(t, f'{k}_{j}').resize((480, 270), Image.LANCZOS), (x, y)); dr.text((x+3, y+271), f"{'before' if j == 0 else 'after'} the cut at {c:.2f}s", fill='black')
sh.save(out, quality=88)
