"""Download each sampled/breakout post's media from the Instagram CDN URLs captured on 14 Oct
and build contact sheets for coding. Reels: 6 frames (0.3 s, 1.5 s, 3 s, 35%, 65%, 92%).
Carousels: every slide (up to 12), 6 per sheet. Images: the image.
Usage: python3 media.py [sets=sample,breakout]
"""
import json, os, sys, subprocess, urllib.request, concurrent.futures as cf
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'media')
SETS = set((sys.argv[1] if len(sys.argv) > 1 else 'sample,breakout').split(','))
H = 640
FONT = ImageFont.load_default(size=26)

def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, 'wb') as f:
            f.write(r.read())
        return True
    except Exception as e:
        print('dl fail', path, e)
        return False

def sheet(items, path):
    ims = []
    for label, p in items:
        try:
            im = Image.open(p).convert('RGB')
        except Exception:
            continue
        im = im.resize((max(1, int(im.width * H / im.height)), H))
        ims.append((label, im))
    if not ims:
        return None
    w = sum(im.width for _, im in ims) + 8 * (len(ims) - 1)
    sh = Image.new('RGB', (w, H + 40), (17, 17, 20)); dr = ImageDraw.Draw(sh); x = 0
    for label, im in ims:
        sh.paste(im, (x, 40)); dr.text((x + 6, 6), label, fill=(255, 230, 120), font=FONT); x += im.width + 8
    sh.save(path, quality=85)
    return path

def dur(v):
    try:
        return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v]).strip())
    except Exception:
        return None

def do(u, q):
    d = os.path.join(OUT, u, q['code']); os.makedirs(d, exist_ok=True)
    meta = {'code': q['code'], 'format': q['format']}
    if q['format'] == 'reel' and q.get('vid'):
        v = os.path.join(d, 'video.mp4')
        if get(q['vid'], v):
            D = dur(v); meta['duration_s'] = D
            if D:
                ts = [0.3, 1.5, 3.0, D * 0.35, D * 0.65, D * 0.92]
                ts = sorted(set(round(min(t, max(D - 0.2, 0)), 2) for t in ts))
                fr = []
                for i, t in enumerate(ts):
                    o = os.path.join(d, f'f{i}_{t:06.2f}s.jpg')
                    if not os.path.exists(o):
                        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t), '-i', v, '-frames:v', '1', '-vf', f'scale=-2:{H}', o])
                    if os.path.exists(o):
                        fr.append((f'{t:.1f}s', o))
                meta['sheets'] = [sheet(fr, os.path.join(d, 'sheet_1.jpg'))]
    elif q['format'] == 'carousel' and q.get('slides'):
        fr = []
        for i, s in enumerate(q['slides'][:12]):
            url = s.get('img')
            if not url:
                continue
            o = os.path.join(d, f's{i+1:02d}.jpg')
            if get(url, o):
                fr.append((f'slide {i+1}' + (' (video)' if s.get('vid') else ''), o))
        meta['n_slides_fetched'] = len(fr)
        meta['sheets'] = [sheet(fr[i:i + 6], os.path.join(d, f'sheet_{i//6+1}.jpg')) for i in range(0, len(fr), 6)]
    elif q.get('img'):
        o = os.path.join(d, 'image.jpg')
        if get(q['img'], o):
            meta['sheets'] = [sheet([('image', o)], os.path.join(d, 'sheet_1.jpg'))]
    json.dump(meta, open(os.path.join(d, 'meta.json'), 'w'))
    return u, q['code'], bool(meta.get('sheets'))

if __name__ == '__main__':
    S = json.load(open(os.path.join(BASE, 'sample.json')))
    jobs = [(u, q) for u, r in S.items() for q in r['posts'] if q['set'] in SETS]
    print(len(jobs), 'posts')
    ok = 0
    with cf.ThreadPoolExecutor(6) as ex:
        for u, c, good in ex.map(lambda a: do(*a), jobs):
            ok += good
    print('done', ok, 'of', len(jobs))
