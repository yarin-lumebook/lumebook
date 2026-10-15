"""Automated audio checks on a finished export (no listening involved).
1. Each line in the export's own audio is compared with its source line file (normalised cross-correlation; 1.0 = same recording) and its position.
2. Levels of the export's audio.
usage: final_audio_checks.py EXPORT.mp4 RESOLVED_TIMELINE.json"""
import sys, json, subprocess, wave, tempfile, os
import numpy as np
exp, R = sys.argv[1], json.load(open(sys.argv[2])); d = tempfile.mkdtemp(); SR = 16000
def load(p):
    t = os.path.join(d, 'x.wav'); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p, '-vn', '-ac', '1', '-ar', str(SR), '-c:a', 'pcm_s16le', t], check=True)
    w = wave.open(t); return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)/32768
mix = load(exp)
for l in R['lines']:
    src = load(l['file']); a = int((l['start'] - 0.3) * SR); seg = mix[max(a, 0):a + len(src) + int(0.6*SR)]
    n = len(seg) + len(src); c = np.fft.irfft(np.fft.rfft(seg, n) * np.conj(np.fft.rfft(src, n))); k = int(np.argmax(np.abs(c[:len(seg)])))
    win = seg[k:k+len(src)]; peak = abs(c[k]) / (np.linalg.norm(win) * np.linalg.norm(src[:len(win)]) + 1e-12)
    found = (max(a, 0) + k) / SR
    print(f"{l['id']} {l.get('speaker', ''):<7} same-recording score {peak:.3f}  found at {found:7.3f}s  planned {l['start']:7.3f}s  diff {1000*(found - l['start']):+.0f} ms")
pk = np.abs(mix).max(); print(f"export audio peak {20*np.log10(pk):.1f} dBFS; samples at/above -0.1 dBFS: {int((np.abs(mix) > 0.989).sum())}")
