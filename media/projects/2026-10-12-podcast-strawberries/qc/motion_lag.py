"""Rough lip-sync lag for a face without a tracker: motion energy in a fixed mouth box vs the speech envelope.
usage: motion_lag.py VIDEO REF_WAV x0,y0,x1,y1 T0 T1   (1080p px; window in seconds)"""
import sys, subprocess, wave, tempfile, os, glob
import numpy as np
from PIL import Image
v, ref = sys.argv[1], sys.argv[2]; x0, y0, x1, y1 = [int(a) for a in sys.argv[3].split(',')]; t0, t1 = float(sys.argv[4]), float(sys.argv[5])
d = tempfile.mkdtemp(); fps = 30.0
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', v, '-vf', f'crop={x1-x0}:{y1-y0}:{x0}:{y0},format=gray', os.path.join(d, 'f_%04d.png')], check=True)
fr = [np.asarray(Image.open(f)).astype(np.float32) for f in sorted(glob.glob(os.path.join(d, 'f_*.png')))]
mot = np.array([0.0] + [np.abs(fr[i]-fr[i-1]).mean() for i in range(1, len(fr))])
dark = np.array([(f < 70).mean() for f in fr])
t = os.path.join(d, 'a.wav'); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', ref, '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', t], check=True)
w = wave.open(t); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float)/32768
hop = int(16000/fps); n = min(len(x)//hop, len(fr)); env = np.sqrt((x[:n*hop].reshape(n, hop)**2).mean(axis=1))
a, b = int(t0*fps), int(t1*fps)
def best(sig, name):
    res = []
    for lag in range(-8, 9):
        s = sig[a+lag:b+lag]; e = env[a:b]
        if len(s) != len(e): continue
        res.append((np.corrcoef(s, e)[0, 1], lag))
    c, l = max(res); print(f'  {name}: best corr {c:.2f} at lag {l/fps*1000:+.0f} ms (lag>0 = picture later than sound); corr at 0: {dict((l2, c2) for c2, l2 in res)[0]:.2f}')
best(mot, 'motion energy'); best(dark, 'dark-interior fraction')
