"""Loudness over time of an audio or video file, in 0.25 s steps (dBFS RMS). usage: audio_profile.py FILE [FILE...]"""
import sys, subprocess, wave, tempfile, os
import numpy as np
for p in sys.argv[1:]:
    t = os.path.join(tempfile.mkdtemp(), 'a.wav'); subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', t], check=True)
    w = wave.open(t); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    n = len(x) // 4000; e = 20 * np.log10(np.sqrt((x[:n*4000].reshape(n, 4000) ** 2).mean(axis=1)) + 1e-6)
    print(f'{os.path.basename(p)}  ({len(x)/16000:.2f}s)')
    for i in range(0, n, 8): print(f'  {i/4:5.2f}s ' + ' '.join(f'{v:5.0f}' for v in e[i:i+8]))
