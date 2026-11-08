#!/usr/bin/env python3
"""Profile pictures for the creator cards (8 Nov 2026).
pics.js (in the built-in browser) collects {handle: picture url}; this downloads each one, shrinks it to a 120px square
JPEG and saves it as creators/creator-research/avatars/<handle>.jpg. Instagram's picture links expire, so the files are
kept locally; the map page links avatars/<handle>.jpg and falls back to the initial when a file is missing.
  python3 pics.py FILE.json      # FILE = the browser's __pic_out
  python3 pics.py FILE.json --missing   # only handles without a file
"""
import json, os, sys, io, urllib.request
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.normpath(os.path.join(HERE, "..", "..", "avatars"))
os.makedirs(OUT, exist_ok=True)
src = json.load(open(sys.argv[1], encoding="utf-8")); only_missing = "--missing" in sys.argv
ok = bad = skip = 0; failed = []
for h, url in src.items():
    f = os.path.join(OUT, h + ".jpg")
    if only_missing and os.path.exists(f): skip += 1; continue
    if not url: failed.append(h); bad += 1; continue
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read()
        im = Image.open(io.BytesIO(data)).convert("RGB"); w, hh = im.size; s = min(w, hh)
        im = im.crop(((w - s) // 2, (hh - s) // 2, (w - s) // 2 + s, (hh - s) // 2 + s)).resize((120, 120), Image.LANCZOS)
        im.save(f, "JPEG", quality=82, optimize=True); ok += 1
    except Exception as e:
        failed.append(h); bad += 1; print("fail", h, e)
print(f"saved {ok}, skipped {skip}, failed {bad}", ("-> " + ", ".join(failed)) if failed else "")
