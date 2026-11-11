"""Download the 34 selected adar.motherhood Reels from their CDN links (info json), then per Reel:
a hook sheet (0-6 s at 3 fps, 6 per row) + 1 fps strip, and a Hebrew Whisper transcript (greedy).
Run: python3 pipeline.py   (watch-video venv python for Pillow)"""
import json, os, subprocess, sys, time, urllib.request
R = '/Users/yarinbruner/Claude/Projects/Lumebook/research/adar-motherhood'
M = '/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-11-11-adar-motherhood-reels'
MODEL = os.path.expanduser('~/Library/Application Support/MacWhisper/models/ggml-model-whisper-turbo.bin')
info = json.load(open(f'{R}/data/info_2026-11-11.json'))
sel = json.load(open(f'{R}/data/selected.json'))
codes = [r['code'] for r in sel]
for i, c in list(enumerate(codes, 1))[::-1]:
    v = f'{M}/videos/{c}.mp4'; a = f'{M}/analysis/{c}'
    os.makedirs(a, exist_ok=True)
    if not os.path.exists(v):
        try:
            req = urllib.request.Request(info[c]['url'], headers={'User-Agent': 'Mozilla/5.0'})
            open(v, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:
            print('FAIL download', c, e); continue
    if not os.path.exists(f'{a}/hook.jpg'):
        subprocess.run(['ffmpeg','-loglevel','error','-y','-t','6','-i',v,'-vf','fps=3,scale=-2:420,tile=6x3','-frames:v','1','-q:v','3',f'{a}/hook.jpg'])
    if not os.path.exists(f'{a}/strip.jpg'):
        subprocess.run(['ffmpeg','-loglevel','error','-y','-i',v,'-vf','fps=1/2,scale=-2:300,tile=8x4','-frames:v','1','-q:v','3',f'{a}/strip.jpg'])
    print(f'PROGRESS {i}/{len(codes)} {c}', flush=True)
print('DONE')
