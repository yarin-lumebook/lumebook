"""Word-level Hebrew transcripts of the creators' own narration (ivrit-ai whisper-large-v3, faster-whisper).
Run: KMP_DUPLICATE_LIB_OK=TRUE /usr/bin/python3 moms/transcribe.py   (faster_whisper lives in that Python's user site)"""
import glob, json, os
from pathlib import Path
from faster_whisper import WhisperModel

HERE = Path(__file__).parent
RAW = HERE.parents[1] / "2026-10-15-israeli-product-reels" / "creator-examples" / "raw"
VIDEOS = {"natali": "Natali_Fridman_v2.mp4", "nofit": "Nofit_Hazut.mov", "moran": "Moran_arges_v3.mp4"}
snap = glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--ivrit-ai--whisper-large-v3-ct2/snapshots/*"))[0]
model = WhisperModel(snap, device="cpu", compute_type="int8")
for name, video in VIDEOS.items():
    segs, _ = model.transcribe(str(RAW / video), language="he", beam_size=5, word_timestamps=True)
    words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
    (HERE / f"{name}-words.json").write_text(json.dumps(words, ensure_ascii=False, indent=0))
    print(name, len(words), "words")
