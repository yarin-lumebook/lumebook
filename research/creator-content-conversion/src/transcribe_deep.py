"""Transcribe the first 30 s of each deep-dive reel with local Whisper (Hebrew turbo model).
Two parallel queues (more starves this Mac). Writes media/<user>/<code>/whisper.txt/.srt."""
import json, os, subprocess, concurrent.futures as cf
BASE = os.path.dirname(os.path.abspath(__file__))
M = os.path.expanduser('~/Library/Application Support/MacWhisper/models/ggml-model-whisper-turbo.bin')
deep = json.load(open(os.path.join(BASE, 'deep.json')))
jobs = [(u, p['code']) for u, ps in deep.items() for p in ps if p['format'] == 'reel']
order = {'strong': 0, 'ordinary': 1, 'relevant_kw': 2}
role = {p['code']: p['role'] for ps in deep.values() for p in ps}
jobs.sort(key=lambda j: order[role[j[1]]])

def run(u, c):
    d = os.path.join(BASE, 'media', u, c)
    v = os.path.join(d, 'video.mp4')
    if not os.path.exists(v) or os.path.exists(os.path.join(d, 'whisper.txt')):
        return c, 'skip'
    wav = os.path.join(d, 'audio.wav')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', v, '-t', '30', '-ar', '16000', '-ac', '1', wav])
    subprocess.run(['whisper-cli', '-m', M, '-l', 'he', '-t', '5', '-osrt', '-otxt', '-of', os.path.join(d, 'whisper'), '-f', wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        os.remove(wav)
    except OSError:
        pass
    return c, 'ok'

print(len(jobs), 'reels to transcribe', flush=True)
with cf.ThreadPoolExecutor(2) as ex:
    for c, s in ex.map(lambda a: run(*a), jobs):
        print(c, s, flush=True)
print('ALL DONE', flush=True)
