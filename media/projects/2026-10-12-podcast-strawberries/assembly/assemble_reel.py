#!/usr/bin/env python3
"""Build the vertical fast-cut reel from assembly/reel-timeline.json (needs Pillow).

usage: assemble_reel.py [TIMELINE.json] [--no-text]   (default timeline: reel-timeline.json; `output`, `name` in the timeline set the file names)
       assemble_reel.py            -> final/strawberries-reel-v1-1080x1920.mp4 (hook + word captions)
       assemble_reel.py --no-text  -> final/strawberries-reel-v1-clean-1080x1920.mp4 (same cut and sound, no text)

Outputs: final/strawberries-reel-v1-1080x1920.mp4, audio/reel-mix-v1.wav, audio/reel-dialogue-track-v1.wav,
assembly/reel-resolved-timeline.json (every start, word cue and effect time actually used).
Hard cuts only; voices are placed untouched (gain only); no music.
"""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parent.parent
NO_TEXT = '--no-text' in sys.argv
TL = next((a for a in sys.argv[1:] if a.endswith('.json')), 'reel-timeline.json')
T = json.loads((ROOT / 'assembly' / Path(TL).name).read_text()); NAME = T.get('name', 'reel')
FPS = T['fps']; CW, CH = T['canvas']
OUT = T.get('output', 'final/strawberries-reel-v1-1080x1920.mp4')
if NO_TEXT: OUT = OUT.replace('-1080x1920', '-clean-1080x1920') if 'output' not in T else OUT.replace('-captions', '-clean')
def run(cmd): subprocess.run(cmd, check=True, cwd=ROOT)
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(ROOT / p)], capture_output=True, text=True).stdout)

# ---- picture timing, in whole frames
f = 0; seg = {}
for s in T['segments']:
    a = round(s['in'] * FPS); n_in = round((s['out'] - s['in']) * FPS); sp = s.get('speed', 1.0); n = round(n_in / sp)
    seg[s['id']] = {**s, 'in_frame': a, 'frames_in': n_in, 'frames': n, 'speed': sp, 'in': a / FPS, 'start': round(f / FPS, 4), 'end': round((f + n) / FPS, 4)}; f += n
TOTAL_FRAMES = f; TOTAL = f / FPS

lines = []
for l in T['lines']:
    s = seg[l['segment']]; start = s['start'] + (l['shot_time'] - s['in']) / s['speed']
    assert start >= -0.001, f"line {l['id']} would start before the reel ({start:.3f}s): start its segment earlier"
    lines.append({**l, 'start': round(start, 3)})
C = T['captions']; cues = []
for l in lines:
    w = l['words']
    for i, x in enumerate(w):
        a = l['start'] + x[1] - C['pre']
        b = (l['start'] + w[i+1][1] - C['pre']) if i + 1 < len(w) else (l['start'] + x[2] + C['last_word_hold'])
        cues.append({'text': x[0], 'start': round(a, 3), 'end': round(b, 3), 'y': l.get('caption_y', C['baseline_y'])})
for i in range(len(cues) - 1): cues[i]['end'] = round(min(cues[i]['end'], cues[i+1]['start'] - 0.02), 3)
sfx = []
for x in T['sfx']:
    sid, edge = x['anchor'].split('.'); start = seg[sid][edge] + x['offset']; tempo = x.get('tempo', 1.0)
    length = min(x.get('trim', 1e9), (dur(x['file']) - x.get('src_in', 0)) / tempo, TOTAL - start)
    sfx.append({**x, 'start': round(start, 3), 'len': round(length, 3), 'tempo': tempo})
(ROOT / f'assembly/{NAME}-resolved-timeline.json').write_text(json.dumps({'total': TOTAL, 'total_frames': TOTAL_FRAMES, 'segments': list(seg.values()), 'lines': lines, 'captions': cues, 'sfx': sfx}, indent=1, ensure_ascii=False))

# ---- audio
def track(items, out, ch, t_total=TOTAL):
    # Two passes. Pass 1 renders each item by itself (source offset, speed, trim, fade, gain) to a plain WAV.
    # Pass 2 only delays and sums those WAVs. Doing speed changes and delays in one filter chain shifted the
    # whole effects track to time zero when the first item was speed-changed (found on reel v2, 12 Oct 2026).
    tmp = ROOT / f'assembly/{NAME}-audio-tmp'; tmp.mkdir(exist_ok=True); lay = 'mono' if ch == 1 else 'stereo'
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']; fc = []
    for i, it in enumerate(items):
        fl = f"aresample=48000,aformat=channel_layouts={lay}"
        if it.get('src_in'): fl += f",atrim=start={it['src_in']},asetpts=PTS-STARTPTS"
        if it.get('tempo', 1.0) != 1.0: fl += f",atempo={it['tempo']}"
        if 'len' in it: fl += f",atrim=0:{it['len']},afade=t=out:st={max(it['len'] - it.get('fade_out', 0.3), 0):.3f}:d={it.get('fade_out', 0.3)}"
        fl += f",volume={it.get('gain_db', 0)}dB"
        part = tmp / f"{Path(out).stem}-{i:02d}-{it['id']}.wav"
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', it['file'], '-af', fl, '-ar', '48000', '-ac', str(ch), '-c:a', 'pcm_s16le', str(part)])
        cmd += ['-i', str(part.relative_to(ROOT))]; fc.append(f"[{i}:a]adelay={max(int(round(it['start'] * 1000)), 0)}:all=1[a{i}]")
    fc.append(''.join(f'[a{i}]' for i in range(len(items))) + f"amix=inputs={len(items)}:normalize=0:dropout_transition=0,apad=whole_dur={t_total},atrim=0:{t_total}[out]")
    run(cmd + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-ar', '48000', '-ac', str(ch), '-c:a', 'pcm_s16le', out])
track(lines, f'audio/{NAME}-dialogue-track-v1.wav', 1)
track(sfx, f'audio/{NAME}-sfx-track-v1.wav', 2)
def first_sound(p):          # guard: every track must be full length and start where the plan says
    import wave, array
    w = wave.open(str(ROOT / p)); x = array.array('h'); x.frombytes(w.readframes(w.getnframes())); ch = w.getnchannels(); sr = w.getframerate()
    i = next((k for k in range(0, len(x), ch) if abs(x[k]) > 60), None)
    return (i / ch / sr if i is not None else None), len(x) / ch / sr
for p, items in ((f'audio/{NAME}-dialogue-track-v1.wav', lines), (f'audio/{NAME}-sfx-track-v1.wav', sfx)):
    t0, length = first_sound(p); plan = min(it['start'] for it in items)
    assert abs(length - TOTAL) < 0.01, f'{p} is {length:.2f}s, expected {TOTAL:.2f}s'
    assert t0 is not None and plan - 0.05 <= t0 <= plan + 0.6, f'{p}: first sound at {t0}, planned {plan:.2f}s'
run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', f'audio/{NAME}-dialogue-track-v1.wav', '-i', f'audio/{NAME}-sfx-track-v1.wav', '-filter_complex',
     f"[0:a]aformat=channel_layouts=stereo[d];[d][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=0,afade=t=out:st={TOTAL - 0.3:.3f}:d=0.3[out]",
     '-map', '[out]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', f'audio/{NAME}-mix-v1.wav'])

# ---- text layers (Pillow here has no bidi library: draw Hebrew in visual order, keeping digit runs readable)
from PIL import ImageFilter
RAQM = features.check('raqm')
def visual(t): return t if RAQM else re.sub(r'\d+', lambda m: m.group(0)[::-1], t[::-1])
def font(path, size, weight='Regular'):
    f = ImageFont.truetype(path if path.startswith('/') else str((ROOT / 'assembly' / path).resolve()), size)
    try: f.set_variation_by_name(weight)
    except Exception: pass
    return f
SH = T.get('text_shadow')
def runs(vis, f, fb):       # the Hebrew face has no digits or punctuation: those runs use the fallback face
    out = []
    for ch in vis:
        use = f if ('\u0590' <= ch <= '\u05ff' or ch == ' ') else fb
        if out and out[-1][1] is use: out[-1][0] += ch
        else: out.append([ch, use])
    return out
def draw_line(d, vis, by, f, fb, fill, dy=0, stroke=0, stroke_fill=None):
    rs = runs(vis, f, fb); x = (CW - sum(u.getlength(t) for t, u in rs)) / 2
    for t, u in rs: d.text((x, by + dy), t, font=u, anchor='ls', fill=fill, stroke_width=stroke, stroke_fill=stroke_fill); x += u.getlength(t)
def text_layer(items, f, fb, stroke=0, stroke_fill=None):   # items: [(text, baseline_y, colour)]
    im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    if SH:
        sh = Image.new('L', (CW, CH), 0); d = ImageDraw.Draw(sh)
        for txt, by, col in items: draw_line(d, visual(txt), by, f, fb, int(255 * SH['opacity']), SH['offset_y'])
        im.putalpha(sh.filter(ImageFilter.GaussianBlur(SH['blur'])))
    d = ImageDraw.Draw(im)
    for txt, by, col in items: draw_line(d, visual(txt), by, f, fb, col, 0, stroke, stroke_fill)
    return im
pngdir = ROOT / f'assembly/{NAME}-text-png'; pngdir.mkdir(exist_ok=True)
for old in pngdir.glob('*.png'): old.unlink()
H = T.get('hook')
if H: text_layer([(t, by, H['color']) for t, by in zip(H['lines'], H['baselines'])], font(H['font'], H['size'], H.get('weight_name', 'Regular')), font(H['fallback_font'], H['size'], H.get('weight_name', 'Regular'))).save(pngdir / 'hook.png')
W8 = C['weight'] if isinstance(C.get('weight'), str) else 'Regular'
cf = font(C['font'], C['size'], W8); cfb = font(C['fallback_font'], C['size'], W8)
for i, c in enumerate(cues): text_layer([(c['text'], c['y'], C['color'])], cf, cfb, C.get('stroke', 0), C.get('stroke_color')).save(pngdir / f'word-{i+1:02d}.png')

# ---- picture
cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']; fc = []
for i, s in enumerate(seg.values()):
    cmd += ['-i', s['file']]; x, y, w = s['crop']
    fc.append(f"[{i}:v]fps={FPS},trim=start_frame={s['in_frame']}:end_frame={s['in_frame'] + s['frames_in']},setpts=(PTS-STARTPTS)/{s['speed']},fps={FPS},"
              f"tpad=stop_mode=clone:stop_duration=0.2,trim=end_frame={s['frames']},setpts=PTS-STARTPTS,crop={w}:{round(w * 16 / 9)}:{x}:{y},scale={CW}:{CH}:flags=lanczos,setsar=1,format=yuv420p[v{i}]")
n = len(seg)
fc.append(''.join(f'[v{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=0[vid]')
if NO_TEXT:
    last = 'vid'; n_text = 0
else:
    last = 'vid'; k = n
    if H: cmd += ['-i', f'assembly/{NAME}-text-png/hook.png']; fc.append(f'[vid][{k}:v]overlay=0:0[c1]'); last = 'c1'; k += 1
    for i, c in enumerate(cues):
        cmd += ['-i', f'assembly/{NAME}-text-png/word-{i+1:02d}.png']
        fc.append(f"[{last}][{k + i}:v]overlay=0:0:enable='between(t,{c['start']},{c['end']})'[w{i}]"); last = f'w{i}'
    n_text = (1 if H else 0) + len(cues)
cmd += ['-i', f'audio/{NAME}-mix-v1.wav']
run(cmd + ['-filter_complex', ';'.join(fc), '-map', f'[{last}]', '-map', f'{n + n_text}:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS),
           '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-ac', '2', '-frames:v', str(TOTAL_FRAMES), '-t', f'{TOTAL:.4f}', OUT])
print(f'{OUT}: reel total {TOTAL:.3f}s = {TOTAL_FRAMES} frames; raqm={RAQM}')
for s in seg.values(): print(f"  {s['id']:<4} {s['start']:6.2f}-{s['end']:6.2f}  x{s['speed']}")
for l in lines: print(f"  {l['id']:<4} at {l['start']:6.2f}")
for x in sfx: print(f"  sfx {x['id']} at {x['start']:6.2f} len {x['len']}")
