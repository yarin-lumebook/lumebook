#!/usr/bin/env python3
"""Assemble the strawberries episode from assembly/timeline.json.

usage: assemble.py PYTHON_WITH_PILLOW? no: run with a Python that has Pillow (only needed for subtitles).
Outputs (under the episode folder):
  audio/dialogue-track-v1.wav      all spoken lines, timed, nothing else (48 kHz mono)
  audio/sfx-track-v1.wav           doorbell, truck, strawberries (48 kHz stereo)
  audio/mix-v1.wav                 dialogue + effects, limited
  final/strawberries-episode-v1-clean-1920x1080.mp4
  final/strawberries-episode-v1-subtitled-he-1920x1080.mp4
  final/strawberries-episode-v1-he.srt
  assembly/resolved-timeline.json  every start/end actually used
Hard cuts only. Voices are placed untouched (gain only); no music, no titles.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = json.loads((ROOT / 'assembly/timeline.json').read_text())
FPS = T['fps']; W, H = T['size']
def q(t): return round(t * FPS) / FPS          # snap to frame
def run(cmd): subprocess.run(cmd, check=True, cwd=ROOT)
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(ROOT / p)], capture_output=True, text=True).stdout)

# ---- resolve times
f = 0; seg = {}          # everything is counted in whole frames so the cuts land exactly where the sound expects them
for s in T['segments']:
    in_f = round(s['in'] * FPS); n = round((s['out'] - s['in']) * FPS)
    seg[s['id']] = {**s, 'in_frame': in_f, 'frames': n, 'in': in_f / FPS, 'start': round(f / FPS, 4), 'end': round((f + n) / FPS, 4), 'dur': n / FPS}; f += n
TOTAL = f / FPS; TOTAL_FRAMES = f
lines = []
for l in T['lines']:
    s = seg[l['segment']]
    start = s['start'] + l['lead_in'] - l['sync_comp'] - s['in']
    lines.append({**l, 'start': round(start, 3), 'spans': [[round(start + a, 3), round(start + b, 3)] for a, b in l['speech']]})
sfx = []
for x in T['sfx']:
    sid, edge = x['anchor'].split('.'); start = seg[sid][edge] + x['offset']
    length = min(x.get('trim', 1e9), dur(x['file']), TOTAL - start)
    sfx.append({**x, 'start': round(start, 3), 'len': round(length, 3)})
cues = []
for l in lines:
    texts = l['text'] if isinstance(l['text'], list) else [l['text']]
    for txt, (a, b) in zip(texts, l['spans']):
        cues.append({'text': txt, 'start': a - T['subtitles']['pre'], 'end': min(b + T['subtitles']['post'], seg[l['segment']]['end'] - 0.04)})
for i in range(len(cues) - 1): cues[i]['end'] = round(min(cues[i]['end'], cues[i+1]['start'] - 0.06), 3)
for c in cues: c['start'] = round(c['start'], 3)
(ROOT / 'assembly/resolved-timeline.json').write_text(json.dumps({'total': TOTAL, 'total_frames': TOTAL_FRAMES, 'segments': list(seg.values()), 'lines': lines, 'sfx': sfx, 'subtitles': cues}, indent=1, ensure_ascii=False))

# ---- audio
def track(items, out, ch, limit=False):
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']; fc = []
    for i, it in enumerate(items):
        cmd += ['-i', it['file']]
        f = f"[{i}:a]aresample=48000,aformat=channel_layouts={'mono' if ch == 1 else 'stereo'}"
        if 'len' in it: f += f",atrim=0:{it['len']},afade=t=out:st={max(it['len'] - it.get('fade_out', 0.3), 0):.3f}:d={it.get('fade_out', 0.3)}"
        f += f",volume={it.get('gain_db', 0)}dB,adelay={int(round(it['start'] * 1000))}:all=1[a{i}]"; fc.append(f)
    mix = ''.join(f'[a{i}]' for i in range(len(items))) + f"amix=inputs={len(items)}:normalize=0:dropout_transition=0,apad=whole_dur={TOTAL},atrim=0:{TOTAL}"
    if limit: mix += ",alimiter=limit=0.89:level=0"
    fc.append(mix + '[out]')
    run(cmd + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-ar', '48000', '-ac', str(ch), '-c:a', 'pcm_s16le', out])
track(lines, 'audio/dialogue-track-v1.wav', 1)
track(sfx, 'audio/sfx-track-v1.wav', 2)
run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'audio/dialogue-track-v1.wav', '-i', 'audio/sfx-track-v1.wav', '-filter_complex',
     f"[0:a]aformat=channel_layouts=stereo[d];[d][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=0,afade=t=out:st={TOTAL - 0.35:.3f}:d=0.35[out]",
     '-map', '[out]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', 'audio/mix-v1.wav'])

# ---- picture
cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']; fc = []
for i, s in enumerate(seg.values()):
    cmd += ['-i', s['file']]
    fc.append(f"[{i}:v]fps={FPS},trim=start_frame={s['in_frame']}:end_frame={s['in_frame'] + s['frames']},setpts=PTS-STARTPTS,scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[v{i}]")
fc.append(''.join(f'[v{i}]' for i in range(len(seg))) + f'concat=n={len(seg)}:v=1:a=0[v]')
ENC = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-movflags', '+faststart']
AENC = ['-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-ac', '2']
clean = 'final/strawberries-episode-v1-clean-1920x1080.mp4'
run(cmd + ['-i', 'audio/mix-v1.wav', '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', f'{len(seg)}:a', *ENC, *AENC, '-frames:v', str(TOTAL_FRAMES), '-t', f'{TOTAL:.4f}', clean])

# ---- subtitles: sidecar .srt (logical order) + burned-in version (PNG overlays)
def ts(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}'
(ROOT / 'final/strawberries-episode-v1-he.srt').write_text(''.join(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n" for i, c in enumerate(cues, 1)), encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont, features
SUB = T['subtitles']; font = ImageFont.truetype(str((ROOT / 'assembly' / SUB['font']).resolve()), SUB['size'])
try: font.set_variation_by_axes([SUB['weight']])
except Exception: pass
RAQM = features.check('raqm')
subdir = ROOT / 'assembly/subtitle-png'; subdir.mkdir(exist_ok=True)
cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', clean]; fc = []; last = '0:v'
for i, c in enumerate(cues):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # Without libraqm Pillow lays glyphs out left to right, so pure-Hebrew text is drawn in visual order (reversed).
    kw = {'direction': 'rtl', 'language': 'he'} if RAQM else {}
    txt = c['text'] if RAQM else c['text'][::-1]
    d.text((W // 2, SUB['baseline_y']), txt, font=font, anchor='ms', fill=(255, 255, 255, 255), stroke_width=6, stroke_fill=(20, 12, 28, 255), **kw)
    p = subdir / f'cue-{i+1:02d}.png'; im.save(p); cmd += ['-i', str(p.relative_to(ROOT))]
    fc.append(f"[{last}][{i+1}:v]overlay=0:0:enable='between(t,{c['start']},{c['end']})'[s{i}]"); last = f's{i}'
run(cmd + ['-filter_complex', ';'.join(fc), '-map', f'[{last}]', '-map', '0:a', *ENC, '-c:a', 'copy', 'final/strawberries-episode-v1-subtitled-he-1920x1080.mp4'])
print(f'total {TOTAL:.3f}s = {TOTAL_FRAMES} frames; raqm={RAQM}')
for s in seg.values(): print(f"  {s['id']} {s['start']:6.2f}-{s['end']:6.2f}  {s['what']}")
for l in lines: print(f"  {l['id']} at {l['start']:6.2f}  speech {l['spans']}")
for x in sfx: print(f"  sfx {x['id']} at {x['start']:6.2f} len {x['len']}")
for c in cues: print(f"  sub {c['start']:6.2f}-{c['end']:6.2f}  {c['text']}")
