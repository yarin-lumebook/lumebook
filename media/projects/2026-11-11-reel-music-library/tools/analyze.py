#!/usr/bin/env python3
"""Measures every track in the reel music library and finds its best 30 seconds.

Needs librosa (Python 3.9 to 3.12; llvmlite does not build on 3.14):
    /usr/bin/python3 -m venv ~/.venvs/reel-music && ~/.venvs/reel-music/bin/pip install librosa soundfile
    ~/.venvs/reel-music/bin/python media/projects/2026-11-11-reel-music-library/tools/analyze.py [--only ID ...]

Writes analysis/audio/<id>.json per track (cached; --force redoes it). Lyrics timing, when
analysis/lyrics/<id>.json exists (tools/transcribe.sh), is used by tools/finish.py, not here.

What "best 30 seconds" means here (11 Nov 2026):
  the 30 s window, starting on a bar line, that scores highest on
  0.40 loudness/fullness  +  0.40 repetition (the part the song keeps coming back to, usually the chorus)
  + 0.20 rhythmic drive, with a penalty for starting in the last quarter (outro) or in the first 6 s (intro).
"""
import argparse, json, sys, warnings
from pathlib import Path

import numpy as np
import librosa

warnings.filterwarnings("ignore")
D = Path(__file__).resolve().parent.parent
OUT = D / "analysis" / "audio"
SR = 22050
HOP = 512
CUT = 30.0

# Krumhansl-Schmuckler key profiles
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def key_of(chroma_mean):
    best = (-9, None, None)
    for i in range(12):
        for prof, mode in ((MAJ, "major"), (MIN, "minor")):
            r = np.corrcoef(np.roll(prof, i), chroma_mean)[0, 1]
            if r > best[0]:
                best = (r, NOTES[i], mode)
    return best[1], best[2], round(float(best[0]), 2)


def z(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    return (x - x.mean()) / s if s > 1e-9 else np.zeros_like(x)


def analyze(path):
    y, sr = librosa.load(str(path), sr=SR, mono=True)
    dur = len(y) / sr
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=1.0)
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=HOP)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_t = librosa.frames_to_time(beats, sr=sr, hop_length=HOP)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=HOP)[0]
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=HOP)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=HOP, n_mfcc=13)
    key, mode, key_conf = key_of(chroma.mean(axis=1))

    # pulse clarity: how much of the onset energy sits on the beat grid
    if len(beats) > 8:
        on_beat = onset[beats].mean()
        pulse = float(on_beat / (onset.mean() + 1e-9))
    else:
        pulse = 0.0

    # beat-synchronous features and repetition (chorus-ness)
    if len(beats) < 16:
        beats = np.arange(0, len(rms), int(sr / HOP / 2))
        beat_t = librosa.frames_to_time(beats, sr=sr, hop_length=HOP)
    feats = np.vstack([librosa.util.normalize(chroma, axis=0), librosa.util.normalize(mfcc[1:], axis=1)])
    bs = librosa.util.sync(feats, beats, aggregate=np.median)
    rec = librosa.segment.recurrence_matrix(bs, k=max(3, bs.shape[1] // 12), width=8, mode="affinity", sym=True)
    rep = np.asarray(rec.sum(axis=0)).ravel()
    rep = rep[: len(beat_t)] if len(rep) >= len(beat_t) else np.pad(rep, (0, len(beat_t) - len(rep)))
    b_rms = librosa.util.sync(rms[None, :], beats, aggregate=np.mean)[0][: len(beat_t)]
    b_on = librosa.util.sync(onset[None, :], beats, aggregate=np.mean)[0][: len(beat_t)]

    # per-second curves for the record (and for picking shorter windows later)
    sec = int(dur)
    fr = lambda t: min(len(rms) - 1, int(t * sr / HOP))
    loud_s = [round(float(rms_db[fr(t):fr(t + 1) + 1].mean()), 1) for t in range(sec)]

    # section boundaries (verse, chorus, bridge...) from the beat-synchronous features
    nseg = int(np.clip(dur / 12, 6, 24))
    try:
        bounds = sorted(set(int(b) for b in librosa.segment.agglomerative(bs, nseg)))
    except Exception:
        bounds = list(range(0, len(beat_t), 16))
    bounds = [b for b in bounds if b < len(beat_t)]

    # candidate starts: section boundaries, nudged to the nearest bar line (every 4th beat)
    zr, zp, zo = z(b_rms), z(rep), z(b_on)
    starts = sorted(set([b for b in bounds] + [4 * round(b / 4) for b in bounds]))
    cands = []
    for i in [s for s in starts if 0 <= s < len(beat_t)]:
        t0 = beat_t[i]
        if t0 + CUT > dur - 0.5:
            continue
        j = np.searchsorted(beat_t, t0 + CUT)
        if j - i < 8:
            continue
        s = 0.40 * zr[i:j].mean() + 0.40 * zp[i:j].mean() + 0.20 * zo[i:j].mean()
        if t0 < 6:
            s -= 0.35
        if t0 > 0.75 * dur:
            s -= 0.5
        # a strong first beat: the cut should land on something
        s += 0.10 * zr[i]
        cands.append((float(s), float(t0), i))
    if not cands:  # track shorter than 30 s plus margin
        cands = [(0.0, 0.0, 0)]
    cands.sort(reverse=True)
    best = cands[0]
    # a second, different option (at least 20 s away)
    alt = next((c for c in cands[1:] if abs(c[1] - best[1]) >= 20), None)

    return {
        "seconds": round(dur, 1),
        "bpm": round(tempo, 1),
        "key": f"{key} {mode}",
        "key_confidence": key_conf,
        "mode": mode,
        "loudness_db": round(float(np.percentile(rms_db, 90)), 1),
        "dynamic_range_db": round(float(np.percentile(rms_db, 95) - np.percentile(rms_db, 10)), 1),
        "brightness_hz": int(np.median(cent)),
        "onset_strength": round(float(onset.mean()), 2),
        "pulse_clarity": round(pulse, 2),
        "beats": [round(float(t), 2) for t in beat_t],
        "loud_per_second": loud_s,
        "loud_z_per_beat": [round(float(v), 2) for v in zr],
        "repetition_per_beat": [round(float(v), 2) for v in zp],
        "drive_z_per_beat": [round(float(v), 2) for v in zo],
        "section_starts": [round(float(beat_t[b]), 2) for b in bounds],
        "best30": {"start": round(best[1], 2), "score": round(best[0], 2)},
        "alt30": {"start": round(alt[1], 2), "score": round(alt[0], 2)} if alt else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in D.glob("0*/*.mp3"))
    total = len(files)
    for n, p in enumerate(files, 1):
        vid = p.stem[-12:-1]
        if a.only and vid not in a.only:
            continue
        o = OUT / f"{vid}.json"
        if o.exists() and not a.force:
            print(f"PROGRESS {n}/{total} {vid} cached", flush=True)
            continue
        try:
            r = analyze(p)
            r["id"] = vid
            o.write_text(json.dumps(r) + "\n")
            print(f"PROGRESS {n}/{total} {vid} bpm {r['bpm']} best {r['best30']['start']}s", flush=True)
        except Exception as e:  # keep going, report at the end
            print(f"ERROR {vid} {e}", flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
