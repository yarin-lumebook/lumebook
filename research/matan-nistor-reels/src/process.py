"""Per-Reel evidence for @matan.nistor analysis: frames, hook frames, cuts, loudness, Hebrew transcript.

Usage: python3 process.py frames CODE...   (1 fps sheets + 4 fps hook sheet for 0-5 s + scene cuts + loudness)
       python3 process.py whisper CODE...  (local whisper-cli turbo, Hebrew, greedy, whole Reel up to 180 s)
Inputs:  media/projects/2026-11-09-matan-nistor-reels/videos/CODE.mp4
Outputs: media/projects/2026-11-09-matan-nistor-reels/analysis/CODE/
Run with the watch-video venv python (Pillow).
"""
import sys, os, subprocess, json, re
from PIL import Image, ImageDraw, ImageFont

ROOT = '/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-11-09-matan-nistor-reels'
MODEL = os.path.expanduser('~/Library/Application Support/MacWhisper/models/ggml-model-whisper-turbo.bin')


def dur_of(v):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v]).strip())


def cuts(v):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-threads', '2', '-i', v, '-vf', "scale=270:-2,select='gt(scene,0.28)',showinfo", '-an', '-f', 'null', '-'],
                       capture_output=True, text=True)
    return [round(float(m), 2) for m in re.findall(r'pts_time:([0-9.]+)', r.stderr)]


def loudness(v):
    """Mean RMS level (dB) per 0.5 s window, from ffmpeg astats; -inf mapped to -90."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-threads', '2', '-i', v, '-vn', '-af',
                        'aresample=16000,asetnsamples=8000,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level',
                        '-f', 'null', '-'], capture_output=True, text=True)
    vals = []
    for m in re.findall(r'RMS_level=([-0-9.inf]+)', r.stderr):
        try:
            x = float(m)
        except ValueError:
            x = -90.0
        vals.append(round(max(x, -90.0), 1))
    return vals


def sheet(files, path, label_font, tall=640, per=6):
    out = []
    for s in range(0, len(files), per):
        chunk = files[s:s + per]
        ims = [Image.open(f) for _, f in chunk]
        w = sum(im.width for im in ims) + 8 * (len(ims) - 1)
        sh = Image.new('RGB', (w, tall + 40), (17, 17, 20))
        dr = ImageDraw.Draw(sh)
        x = 0
        for (t, _), im in zip(chunk, ims):
            sh.paste(im, (x, 40))
            dr.text((x + 6, 4), f'{int(t // 60):02d}:{t % 60:05.2f}', fill=(255, 230, 120), font=label_font)
            x += im.width + 8
        p = path.format(n=s // per + 1)
        sh.save(p, quality=85)
        out.append({'sheet': p, 'from': chunk[0][0], 'to': chunk[-1][0]})
    return out


def frames(code):
    v = f'{ROOT}/videos/{code}.mp4'
    d = f'{ROOT}/analysis/{code}'
    if os.path.exists(f'{d}/index.json'):
        return
    os.makedirs(f'{d}/frames', exist_ok=True)
    os.makedirs(f'{d}/hook', exist_ok=True)
    dur = dur_of(v)
    step = 1.0 if dur <= 90 else 1.5 if dur <= 150 else dur / 100
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-threads', '2', '-y', '-i', v, '-vf', f'fps=1/{step},scale=-2:640', '-q:v', '3', f'{d}/frames/n%04d.jpg'])
    for f in sorted(os.listdir(f'{d}/frames')):
        if f.startswith('n'):
            t = (int(f[1:5]) - 1) * step
            os.rename(f'{d}/frames/{f}', f'{d}/frames/t{t:07.2f}.jpg')
    # hook: 4 fps over the first 5 s (20 frames), 0.25 s apart
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-threads', '2', '-y', '-t', '5', '-i', v, '-vf', 'fps=4,scale=-2:640', '-q:v', '3', f'{d}/hook/h%03d.jpg'])
    for f in sorted(os.listdir(f'{d}/hook')):
        if f.startswith('h') and f[1:4].isdigit():
            t = (int(f[1:4]) - 1) * 0.25
            os.rename(f'{d}/hook/{f}', f'{d}/hook/t{t:05.2f}.jpg')
    font = ImageFont.load_default(size=30)
    files = sorted((float(f[1:-4]), f'{d}/frames/{f}') for f in os.listdir(f'{d}/frames') if f.startswith('t'))
    sheets = sheet(files, f'{d}/sheet_{{n:02d}}.jpg', font)
    hfiles = sorted((float(f[1:-4]), f'{d}/hook/{f}') for f in os.listdir(f'{d}/hook') if f.startswith('t'))
    hsheets = sheet(hfiles, f'{d}/hook_{{n:02d}}.jpg', font, per=5)
    c = cuts(v)
    lv = loudness(v)
    info = {'code': code, 'duration': round(dur, 2), 'step_s': step, 'cuts': c, 'n_shots': len(c) + 1,
            'avg_shot_s': round(dur / (len(c) + 1), 2), 'sheets': sheets, 'hook_sheets': hsheets,
            'rms_db_per_0_5s': lv}
    json.dump(info, open(f'{d}/index.json', 'w'), indent=1)
    print(code, round(dur, 1), 's', len(c) + 1, 'shots', len(sheets), 'sheets', flush=True)


def whisper(code):
    v = f'{ROOT}/videos/{code}.mp4'
    d = f'{ROOT}/analysis/{code}'
    os.makedirs(d, exist_ok=True)
    if os.path.exists(f'{d}/whisper.srt') or os.path.exists(f'{d}/whisper.lock'):
        return
    open(f'{d}/whisper.lock', 'w').close()
    wav = f'{d}/audio.wav'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', v, '-t', '120', '-ar', '16000', '-ac', '1', wav])
    subprocess.run(['whisper-cli', '-m', MODEL, '-l', 'he', '-t', '5', '-bs', '1', '-bo', '1', '-osrt', '-otxt', '-of', f'{d}/whisper', '-f', wav],
                   capture_output=True)
    os.remove(wav)
    os.remove(f'{d}/whisper.lock')
    print(code, 'whisper done', flush=True)


if __name__ == '__main__':
    fn = {'frames': frames, 'whisper': whisper}[sys.argv[1]]
    codes = sys.argv[2:]
    for i, code in enumerate(codes, 1):
        if not os.path.exists(f'{ROOT}/videos/{code}.mp4'):
            print(code, 'MISSING VIDEO', flush=True)
            continue
        try:
            fn(code)
        except Exception as e:
            print(code, 'ERROR', e, flush=True)
        print(f'PROGRESS {i}/{len(codes)} {sys.argv[1]} {code}', flush=True)
