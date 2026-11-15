"""MeBook hooks: for each downloaded video, a frame strip of the opening (on-screen hook) and a Whisper
transcript of the first 10 seconds (spoken hook). Usage: python3 process.py strips | whisper"""
import glob, os, subprocess, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, '..', '..', 'media', 'projects', '2026-11-15-mebook-hooks')
MODEL = os.path.expanduser('~/Library/Application Support/MacWhisper/models/ggml-model-whisper-turbo.bin')
TIMES = [0.2, 0.8, 1.5, 2.3, 3.2, 4.5]

def videos():
    return sorted(glob.glob(f'{MEDIA}/reels/*.mp4') + glob.glob(f'{MEDIA}/ads/*.mp4'))

def key(v):
    return os.path.basename(v)[:-4]

def strips():
    os.makedirs(f'{MEDIA}/strips', exist_ok=True)
    vs = videos()
    for n, v in enumerate(vs, 1):
        out = f'{MEDIA}/strips/{key(v)}.jpg'
        if not os.path.exists(out):
            tiles = []
            for t in TIMES:
                f = f'{HERE}/work/_f.jpg'
                r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', v, '-frames:v', '1', '-vf', 'scale=-2:560', f])
                if r.returncode == 0 and os.path.exists(f):
                    im = Image.open(f).convert('RGB'); tiles.append((t, im.copy())); os.remove(f)
            if tiles:
                w = sum(im.width for _, im in tiles) + 6 * (len(tiles) - 1)
                h = max(im.height for _, im in tiles) + 26
                sheet = Image.new('RGB', (w, h), 'white'); d = ImageDraw.Draw(sheet); x = 0
                for t, im in tiles:
                    sheet.paste(im, (x, 26)); d.text((x + 4, 6), f'{t:.1f}s', fill='black'); x += im.width + 6
                sheet.save(out, quality=85)
        print(f'PROGRESS {n}/{len(vs)} strip {key(v)}', flush=True)

def whisper():
    os.makedirs(f'{HERE}/work/whisper', exist_ok=True)
    vs = videos()
    if os.environ.get('REVERSE'): vs = vs[::-1]
    for n, v in enumerate(vs, 1):
        base = f'{HERE}/work/whisper/{key(v)}'
        if not os.path.exists(base + '.txt') and not os.path.exists(base + '.wav'):
            wav = base + '.wav'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-t', '12', '-ar', '16000', '-ac', '1', wav])
            if os.path.exists(wav):
                subprocess.run(['whisper-cli', '-m', MODEL, '-l', 'he', '-t', '5', '-bs', '1', '-bo', '1', '-osrt', '-otxt',
                                '-of', base, '-f', wav], capture_output=True)
                os.remove(wav)
            else:
                open(base + '.txt', 'w').write('[no audio]\n')
        print(f'PROGRESS {n}/{len(vs)} whisper {key(v)}', flush=True)

if __name__ == '__main__':
    {'strips': strips, 'whisper': whisper}[sys.argv[1]]()
