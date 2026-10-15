"""Inspect a talking-shot candidate: stream facts, audio match vs the reference line, mouth motion vs audio,
background stability, and contact sheets for viewing.
usage: qc_shot.py VIDEO REF_WAV OUT_DIR CONFIG_JSON
CONFIG: {"mode": "lume"|"fixed", "words": [[label, start, end], ...], "shift": 0.0, "mouth": [cx, cy, half] (fixed mode, 1080p px), "window": [t0, t1], "book": [x0, y0, x1, y1] (1080p px, optional)}
"""
import sys, json, subprocess, wave, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

video, ref_wav, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
tag = video.stem
work = out / f'{tag}_frames'
if work.exists(): shutil.rmtree(work)
work.mkdir(parents=True)

import json as _json
CFG = _json.loads(Path(sys.argv[4]).read_text()) if len(sys.argv) > 4 else {}
SHIFT = float(CFG.get('shift', 0.0))
WORDS = [(w, a+SHIFT, b+SHIFT) for w, a, b in CFG.get('words', [])]
MODE = CFG.get('mode', 'lume'); T0, T1 = CFG.get('window', [0.3, 3.2])
def word_at(t):
    for w, a, b in WORDS:
        if a <= t <= b: return w
    return ''

def run(*a): return subprocess.run(a, capture_output=True, text=True)
info = json.loads(run('ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', str(video)).stdout)
vs = next(s for s in info['streams'] if s['codec_type'] == 'video')
aus = [s for s in info['streams'] if s['codec_type'] == 'audio']
num, den = map(int, vs['avg_frame_rate'].split('/')); fps = num/den
print(f"VIDEO {vs['width']}x{vs['height']} {vs['codec_name']} {fps:.3f} fps frames={vs.get('nb_frames')} dur={float(info['format']['duration']):.3f}s bitrate={int(info['format']['bit_rate'])//1000} kb/s")
print('AUDIO', [(a['codec_name'], a['sample_rate'], a['channels'], a.get('duration')) for a in aus] or 'none')

def load(path, sr=16000):
    tmp = work / (Path(path).stem + f'_{sr}.wav')
    run('ffmpeg', '-y', '-loglevel', 'error', '-i', str(path), '-vn', '-ac', '1', '-ar', str(sr), '-c:a', 'pcm_s16le', str(tmp))
    with wave.open(str(tmp)) as w: x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)/32768
    return x
def env(x, sr=16000, hop=160):
    n = len(x)//hop
    return np.sqrt((x[:n*hop].reshape(n, hop)**2).mean(axis=1) + 1e-12)
def xcorr_lag(a, b, maxlag):
    a = (a-a.mean())/(a.std()+1e-12); b = (b-b.mean())/(b.std()+1e-12)
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    best = (-9, 0)
    for lag in range(-maxlag, maxlag+1):
        if lag >= 0: c = (a[lag:]*b[:n-lag]).mean() if n-lag > 10 else -9
        else: c = (a[:n+lag]*b[-lag:]).mean() if n+lag > 10 else -9
        if c > best[0]: best = (c, lag)
    return best

ref = load(ref_wav); ref_env = env(ref)
if aus:
    va = load(video); va_env = env(va)
    n = min(len(ref), len(va))
    f = np.fft.rfft(va[:n], 2*n) * np.conj(np.fft.rfft(ref[:n], 2*n)); cc = np.fft.irfft(f)
    k = int(np.argmax(np.abs(cc))); lag = k if k < n else k-2*n
    peak = abs(cc[k]) / (np.linalg.norm(va[:n])*np.linalg.norm(ref[:n])+1e-12)
    c_env, l_env = xcorr_lag(va_env, ref_env, 100)
    print(f"AUDIO vs REF  waveform xcorr peak={peak:.3f} at lag={lag/16000*1000:+.0f} ms   envelope corr={c_env:.3f} at lag={l_env*10:+d} ms   (peak near 1.0 = same recording; lag>0 = video audio is later)")
    print(f"   video-audio speech span (env>-32dB): ", end='')
    thr = 10**(-32/20); idx = np.where(va_env > thr)[0]
    print(f"{idx[0]/100:.2f}-{idx[-1]/100:.2f}s" if len(idx) else 'silent', f"  ref span: {np.where(ref_env>thr)[0][0]/100:.2f}-{np.where(ref_env>thr)[0][-1]/100:.2f}s")

# frames
run('ffmpeg', '-y', '-loglevel', 'error', '-i', str(video), '-vf', 'scale=960:-2', '-q:v', '3', str(work/'f_%04d.jpg'))
files = sorted(work.glob('f_*.jpg')); N = len(files)
frames = [np.asarray(Image.open(f).convert('RGB')).astype(np.int16) for f in files]
H, W = frames[0].shape[:2]; t_of = lambda i: i/fps
print(f"frames extracted: {N} ({N/fps:.2f}s)")

# nose tracking: the nose is the topmost saturated-red blob near its previous position (the tongue has the
# same colour but sits below it; the ear interiors are also red but far away, so search locally frame to frame)
def red(fr):
    R, G, B = fr[..., 0], fr[..., 1], fr[..., 2]
    return (R > 120) & (G < 60) & (B < 110)
def nose(fr, px, py, rad):
    x0, x1, y0, y1 = max(int(px-rad), 0), min(int(px+rad), W), max(int(py-rad), 0), min(int(py+rad*1.2), H)
    m = red(fr)[y0:y1, x0:x1]
    rc = m.sum(axis=1); rows = np.nonzero(rc >= 3)[0]
    if len(rows) < 6: return None
    top = rows[0]; bot = top
    for r in rows[1:]:
        if r - bot <= 2: bot = r
        else: break
    if bot - top < 6: return None
    ys, xs = np.nonzero(m[top:bot+1])
    k = np.abs(xs - np.median(xs)) < W*0.035
    xs = xs[k]
    return float(xs.mean()+x0), float(top+y0), float(bot+y0), float(xs.max()-xs.min()+1), int(len(xs))
if MODE == 'lume':
    first = nose(frames[0], W*0.52, H*0.40, H*0.13)   # start: nose position in the master still (500, 199 of 960x540)
    assert first, 'nose not found in frame 0'
    track = [first]; prev = first; lost = 0
    for fr in frames[1:]:
        t = nose(fr, prev[0], (prev[1]+prev[2])/2, prev[3]*1.35)
        if t and 0.6*first[3] < t[3] < 1.7*first[3]: prev = t; track.append(t)
        else: lost += 1; track.append(None)
    valid = [t for t in track if t]
    print(f"nose tracked in {len(valid)}/{N} frames; x range {min(t[0] for t in valid):.0f}-{max(t[0] for t in valid):.0f}, top-y range {min(t[1] for t in valid):.0f}-{max(t[1] for t in valid):.0f} (frame {W}x{H}); nose width {min(t[3] for t in valid):.0f}-{max(t[3] for t in valid):.0f} px")
    hx = np.array([t[0] if t else np.nan for t in track]); hy = np.array([t[1] if t else np.nan for t in track])
    print(f"HEAD travel (nose, in 1080p px): horizontal {2*(np.nanmax(hx)-np.nanmin(hx)):.0f}, vertical {2*(np.nanmax(hy)-np.nanmin(hy)):.0f}; start->end shift {2*(hx[~np.isnan(hx)][-1]-hx[0]):+.0f}, {2*(hy[~np.isnan(hy)][-1]-hy[0]):+.0f}")
    nw = float(np.median([t[3] for t in valid]))
    last = valid[0]; mouth = []; boxes = []
    for fr, tr in zip(frames, track):
        if tr: last = tr
        cx, nb = last[0], last[2]
        l, r, tp, bt = int(cx-nw*1.5), int(cx+nw*1.5), int(nb+3), int(nb+nw*2.3)
        roi = fr[max(tp, 0):bt, max(l, 0):r]
        R, G, B = roi[..., 0], roi[..., 1], roi[..., 2]
        interior = ((R < 80) & (G < 40) & (B < 40)) | ((R > 60) & (G < 60) & (B < 110))   # dark cavity or red tongue
        mouth.append(interior.sum()/(nw*nw)); boxes.append((l, tp, r, bt))
else:
    cx, cy, half = [v/2 for v in CFG['mouth']]   # config is in 1080p px, frames are 960x540
    nw = half/1.5; mouth = []; boxes = []
    for fr in frames:
        l, r, tp, bt = int(cx-half), int(cx+half), int(cy-half*0.7), int(cy+half*0.7)
        roi = fr[tp:bt, l:r]; lum = 0.299*roi[..., 0] + 0.587*roi[..., 1] + 0.114*roi[..., 2]
        mouth.append(float((lum < 75).mean())*10); boxes.append((int(cx-nw*1.5), int(cy-nw*0.3)+0, int(cx+nw*1.5), int(cy+nw*2)))
    hd = [np.abs(frames[i][int(cy-half*3):int(cy+half*2), int(cx-half*3):int(cx+half*3)] - frames[0][int(cy-half*3):int(cy+half*2), int(cx-half*3):int(cx+half*3)]).mean() for i in range(N)]
    print(f"HEAD-region change vs frame 0 (0-255): max {max(hd):.1f}, end {hd[-1]:.1f}")
mouth = np.array(mouth)
aenv_f = np.array([ref_env[min(int(t_of(i)*100), len(ref_env)-1)] for i in range(N)])
c_m, l_m = xcorr_lag(mouth, aenv_f, int(fps*0.5))
print(f"MOUTH-OPEN vs REF AUDIO envelope: corr={c_m:.3f} at lag={l_m/fps*1000:+.0f} ms (lag>0 = mouth moves later than audio)")
sp = (np.arange(N)/fps > (WORDS[0][1] if WORDS else 0)) & (np.arange(N)/fps < (WORDS[-1][2] if WORDS else 0))
print(f"   mouth-open mean during speech {mouth[sp].mean() if sp.any() else 0:.3f} / outside speech {mouth[~sp].mean():.3f}")
print('   per-frame (t, audio dB, mouth, word):')
for i in range(N):
    if i % 3 == 0 and (T0-0.2) <= t_of(i) <= (T1+0.2): print(f"    {t_of(i):5.2f}  {20*np.log10(aenv_f[i]+1e-6):6.1f}  {mouth[i]:.3f}  {'#'*int(mouth[i]*40):<24} {word_at(t_of(i))}")

# plot
PW, PH = 1600, 420; plot = Image.new('RGB', (PW, PH), 'white'); d = ImageDraw.Draw(plot)
dur = N/fps; X = lambda t: 40 + t/dur*(PW-60)
for w, a, b in WORDS:
    d.rectangle([X(a), 20, X(b), PH-30], fill=(235, 240, 255)); d.text((X(a)+3, 22), w, fill='navy')
for s in np.arange(0, dur+.001, .5): d.line([X(s), 20, X(s), PH-30], fill=(210, 210, 210)); d.text((X(s)-8, PH-26), f'{s:.1f}', fill='black')
ae = ref_env/ref_env.max(); mo = mouth/(mouth.max()+1e-9)
d.line([(X(i/100), PH-30-ae[i]*170) for i in range(min(len(ae), int(dur*100)))], fill=(30, 120, 30), width=2)
d.line([(X(t_of(i)), 200-mo[i]*170) for i in range(N)], fill=(200, 30, 30), width=2)
d.text((44, 4), 'red = mouth-open metric (top half), green = reference audio envelope (bottom half)', fill='black')
plot.save(out/f'{tag}__mouth_vs_audio.png')

# mouth contact sheet (every frame 0.40-3.10 s)
sel = [i for i in range(N) if T0 <= t_of(i) <= T1]
cw = 150; cols = 12; rows = (len(sel)+cols-1)//cols
sheet = Image.new('RGB', (cols*cw, rows*(cw+16)), 'white'); d = ImageDraw.Draw(sheet)
for k, i in enumerate(sel):
    l, tp, r, bt = boxes[i]; cx, cy = (l+r)/2, tp - nw*0.3
    if MODE != 'lume': cy = tp + nw*0.3
    s = nw*2.2
    crop = Image.fromarray(frames[i].astype(np.uint8)).crop((int(cx-s), int(cy-s*0.6), int(cx+s), int(cy+s*1.4))).resize((cw, cw), Image.LANCZOS)
    x, y = (k % cols)*cw, (k//cols)*(cw+16)
    sheet.paste(crop, (x, y)); d.text((x+3, y+cw+2), f'{t_of(i):.2f} {word_at(t_of(i))}', fill='black')
sheet.save(out/f'{tag}__mouth_sheet.jpg', quality=90)

# full-frame sheet (12 frames evenly) + background stability
idx = [round(k*(N-1)/11) for k in range(12)]
fs = Image.new('RGB', (4*480, 3*(270+16)), 'white'); d = ImageDraw.Draw(fs)
for k, i in enumerate(idx):
    im = Image.fromarray(frames[i].astype(np.uint8)).resize((480, 270), Image.LANCZOS); x, y = (k % 4)*480, (k//4)*286
    fs.paste(im, (x, y)); d.text((x+4, y+272), f'{t_of(i):.2f}s {word_at(t_of(i))}', fill='black')
fs.save(out/f'{tag}__frames_sheet.jpg', quality=88)
regions = {'shelf_left': (.02, .02, .30, .55), 'mic': (.16, .42, .40, .82), 'wall_right': (.80, .05, .99, .60), 'table_front': (.20, .86, .95, .99)}
f0 = frames[0]
print('BACKGROUND drift vs frame 0 (mean abs diff, 0-255):')
for name, (l, t, r, b) in regions.items():
    sl = (slice(int(t*H), int(b*H)), slice(int(l*W), int(r*W)))
    dd = [np.abs(fr[sl]-f0[sl]).mean() for fr in frames]
    print(f"   {name:<11} max={max(dd):5.2f} end={dd[-1]:5.2f} mean={np.mean(dd):5.2f}")
if CFG.get('book'):
    x0, y0, x1, y1 = [int(v/2) for v in CFG['book']]; dd = [np.abs(fr[y0:y1, x0:x1]-frames[1][y0:y1, x0:x1]).mean() for fr in frames[1:]]
    print(f"BOOK region change vs frame 1: max={max(dd):.2f} mean={np.mean(dd):.2f} (low = cover static and unobstructed)")
a, b = Image.fromarray(f0.astype(np.uint8)), Image.fromarray(frames[-1].astype(np.uint8))
diff = np.clip(np.abs(frames[-1]-f0).mean(axis=2)*4, 0, 255).astype(np.uint8)
st = Image.new('RGB', (W*3, H)); st.paste(a, (0, 0)); st.paste(b, (W, 0)); st.paste(Image.fromarray(diff).convert('RGB'), (2*W, 0))
st.resize((W*3//2, H//2), Image.LANCZOS).save(out/f'{tag}__first_last_diff.jpg', quality=88)
print('sheets saved to', out)
