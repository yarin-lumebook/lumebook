"""Hebrew word timestamps for word-by-word captions (ivrit-ai whisper-large-v3, faster-whisper).
Run: KMP_DUPLICATE_LIB_OK=TRUE /usr/bin/python3 transcribe.py VIDEO OUT.json   (faster_whisper lives in that Python's user site)
Writes [{"w": word, "s": start, "e": end}, ...] in source seconds. Read it and fix misheard words before building."""
import glob, json, os, sys
from faster_whisper import WhisperModel

video, out = sys.argv[1], sys.argv[2]
snap = glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--ivrit-ai--whisper-large-v3-ct2/snapshots/*"))[0]
model = WhisperModel(snap, device="cpu", compute_type="int8")
segs, _ = model.transcribe(video, language="he", beam_size=5, word_timestamps=True)
words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words if w.word.strip()]
with open(out, "w") as f:
    json.dump(words, f, ensure_ascii=False, indent=0)
print(len(words), "words ->", out)
