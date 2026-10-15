"""Per-reel analysis prep: duration, scene cuts, timestamped frame sheets, Hebrew Whisper transcript.

Usage: python3 process.py frames CODE...   (cuts + sheets)
       python3 process.py whisper CODE...  (local whisper-cli turbo, Hebrew)
Inputs: media/projects/2026-10-15-israeli-product-reels/videos/CODE.mp4
Outputs: media/projects/2026-10-15-israeli-product-reels/analysis/CODE/
"""
import sys, os, subprocess, json, re
from PIL import Image, ImageDraw, ImageFont

ROOT = '/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-15-israeli-product-reels'
MODEL = os.path.expanduser('~/Library/Application Support/MacWhisper/models/ggml-model-whisper-turbo.bin')


def dur_of(v):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v]).strip())


def cuts(v):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', v, '-vf', "select='gt(scene,0.28)',showinfo", '-an', '-f', 'null', '-'],
                       capture_output=True, text=True)
    return [round(float(m), 2) for m in re.findall(r'pts_time:([0-9.]+)', r.stderr)]


def frames(code):
    v = f'{ROOT}/videos/{code}.mp4'
    d = f'{ROOT}/analysis/{code}'
    os.makedirs(f'{d}/frames', exist_ok=True)
    dur = dur_of(v)
    step = 1.0 if dur <= 75 else 1.5 if dur <= 120 else dur / 80
    if not os.listdir(f'{d}/frames'):
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', v, '-vf', f'fps=1/{step},scale=-2:640',
                        '-q:v', '3', f'{d}/frames/n%04d.jpg'])
        for f in sorted(os.listdir(f'{d}/frames')):
            t = (int(f[1:5]) - 1) * step
            os.rename(f'{d}/frames/{f}', f'{d}/frames/t{t:06.2f}.jpg')
    files = sorted((float(f[1:-4]), f'{d}/frames/{f}') for f in os.listdir(f'{d}/frames') if f.startswith('t'))
    font = ImageFont.load_default(size=30)
    sheets = []
    for s in range(0, len(files), 6):
        chunk = files[s:s + 6]
        ims = [Image.open(f) for _, f in chunk]
        w = sum(im.width for im in ims) + 8 * (len(ims) - 1)
        sh = Image.new('RGB', (w, 680), (17, 17, 20))
        dr = ImageDraw.Draw(sh)
        x = 0
        for (t, _), im in zip(chunk, ims):
            sh.paste(im, (x, 40))
            dr.text((x + 6, 4), f'{int(t // 60):02d}:{t % 60:05.2f}', fill=(255, 230, 120), font=font)
            x += im.width + 8
        p = f'{d}/sheet_{s // 6 + 1:02d}.jpg'
        sh.save(p, quality=85)
        sheets.append({'sheet': p, 'from': chunk[0][0], 'to': chunk[-1][0]})
    c = cuts(v)
    info = {'code': code, 'duration': round(dur, 2), 'step_s': step, 'cuts': c, 'n_shots': len(c) + 1,
            'avg_shot_s': round(dur / (len(c) + 1), 2), 'sheets': sheets}
    json.dump(info, open(f'{d}/index.json', 'w'), indent=1)
    print(code, round(dur, 1), 's', len(c) + 1, 'shots', len(sheets), 'sheets')


def whisper(code):
    v = f'{ROOT}/videos/{code}.mp4'
    d = f'{ROOT}/analysis/{code}'
    os.makedirs(d, exist_ok=True)
    if os.path.exists(f'{d}/whisper.srt') or os.path.exists(f'{d}/whisper.lock'):
        return
    open(f'{d}/whisper.lock', 'w').close()
    wav = f'{d}/audio.wav'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', v, '-t', '90', '-ar', '16000', '-ac', '1', wav])  # first 90 s only
    subprocess.run(['whisper-cli', '-m', MODEL, '-l', 'he', '-t', '5', '-bs', '1', '-bo', '1', '-osrt', '-otxt', '-of', f'{d}/whisper', '-f', wav],
                   capture_output=True)
    os.remove(wav)
    os.remove(f'{d}/whisper.lock')
    print(code, 'whisper done', flush=True)


if __name__ == '__main__':
    fn = {'frames': frames, 'whisper': whisper}[sys.argv[1]]
    for code in sys.argv[2:]:
        try:
            fn(code)
        except Exception as e:
            print(code, 'ERROR', e, flush=True)
