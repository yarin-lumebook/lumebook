"""Track the book cover through the 10 s edit and write where the kid's name is in every frame.

Template matching (normalised cross-correlation, numpy only) at quarter size on the un-zoomed edit, using the
cover's upper art (crown, baby, balloons: rarely under her hand). The name sits at a fixed spot under it,
measured in the variant's reference frame (variants.py: ref_t, tpl, name). Run with /usr/bin/python3 (it has numpy).
Usage: /usr/bin/python3 track_name.py [higgsfield|fal]  ->  the variant's track json  (1080x1920, un-zoomed)
"""
import json, subprocess
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from variants import V

SRC, OUT = V["edit"], V["track"]
Q = 4                          # work at 270x480
W, H, FPS = 1080, 1920, 30
REF_T = V["ref_t"]
TPL = V["tpl"]                 # template box in the reference frame (x0, y0, x1, y1), full size
NAME = V["name"]               # "סהר דויד" in the same frame
CUTS = V["jumps_s"]            # jump cuts: the book jumps, so search wider there
SCALES = [0.94, 0.97, 1.0, 1.03, 1.06]

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"scale={W // Q}:{H // Q},format=gray",
                      "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H // Q, W // Q).astype(np.float32)

x0, y0, x1, y1 = (v // Q for v in TPL)
ref = frames[round(REF_T * FPS)]
base_tpl = ref[y0:y1, x0:x1]
tcx, tcy = (TPL[0] + TPL[2]) / 2, (TPL[1] + TPL[3]) / 2


def scaled(tpl, s):
    from PIL import Image
    h, w = tpl.shape
    im = Image.fromarray(tpl).resize((max(8, round(w * s)), max(8, round(h * s))), Image.BILINEAR)
    return np.asarray(im, np.float32)


def ncc(img, tpl, cx, cy, r):
    """Best match of tpl centred within r px of (cx, cy) in quarter-size img: (score, centre x, centre y)."""
    th, tw = tpl.shape
    xa, ya = int(max(cx - r - tw / 2, 0)), int(max(cy - r - th / 2, 0))
    xb, yb = int(min(cx + r + tw / 2, img.shape[1])), int(min(cy + r + th / 2, img.shape[0]))
    win = img[ya:yb, xa:xb]
    if win.shape[0] < th or win.shape[1] < tw:
        return -1, cx, cy
    patches = sliding_window_view(win, (th, tw))
    t = (tpl - tpl.mean()) / (tpl.std() + 1e-6)
    pm = patches.mean(axis=(2, 3), keepdims=True)
    ps = patches.std(axis=(2, 3), keepdims=True) + 1e-6
    score = ((patches - pm) / ps * t).mean(axis=(2, 3))
    iy, ix = np.unravel_index(np.argmax(score), score.shape)
    return float(score[iy, ix]), xa + ix + tw / 2, ya + iy + th / 2


cut_frames = {round(c * FPS) for c in CUTS} | {round(c * FPS) + 1 for c in CUTS}
tpls = {s: scaled(base_tpl, s) for s in SCALES}
cx, cy = tcx / Q, tcy / Q
track = []
for i, img in enumerate(frames):
    r = 45 if i == 0 else (30 if i in cut_frames else 10)
    best = max((ncc(img, tpls[s], cx, cy, r) + (s,) for s in SCALES), key=lambda b: b[0])
    score, cx, cy, s = best
    mx, my = cx * Q, cy * Q   # template centre, full size
    nx0, ny0 = mx + (NAME[0] - tcx) * s, my + (NAME[1] - tcy) * s
    nx1, ny1 = mx + (NAME[2] - tcx) * s, my + (NAME[3] - tcy) * s
    track.append(dict(t=round(i / FPS, 3), score=round(score, 3), scale=s,
                      name=[round(nx0), round(ny0), round(nx1), round(ny1)]))

json.dump(track, open(OUT, "w"), indent=0)
scores = [f["score"] for f in track]
print(OUT, len(track), "frames; match score min %.2f median %.2f" % (min(scores), float(np.median(scores))))
for f in track[::30]:
    print(f["t"], f["score"], f["scale"], f["name"])
