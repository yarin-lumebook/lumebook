# Re-transcribe each finished file and measure, word by word, whether the caption on screen is the word being said.
import glob, json, os, statistics
from faster_whisper import WhisperModel
snap = glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--ivrit-ai--whisper-large-v3-ct2/snapshots/*"))[0]
m = WhisperModel(snap, device="cpu", compute_type="int8")
norm = lambda s: s.strip(" ,.?!-").replace("לומי", "לומבוק")
for n in ["natali", "nofit", "moran"]:
    ev = json.load(open(f"work/moms/{n}_captions.json"))
    segs, _ = m.transcribe(f"final/mom-voice-{n}.mp4", language="he", beam_size=5, word_timestamps=True)
    heard = [(w.start, norm(w.word)) for s in segs for w in s.words if norm(w.word) not in ("", "בוק")]
    hits, lags = 0, []
    for t, w in heard:
        shown = next((e[2] for e in ev if e[0] <= t + 0.10 < e[1]), None)
        hits += shown == w
        same = [e[0] for e in ev if e[2] == w]
        if same: lags.append(min(same, key=lambda x: abs(x - t)) - t)
    print(n, f"{hits}/{len(heard)} words: caption matches the word being said 0.1 s in;",
          f"median caption lead/lag {statistics.median(lags):+.2f}s, worst {max(lags, key=abs):+.2f}s")
