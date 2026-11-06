"""Cut the wizard quokka out of the flat dark-purple closeup (shared/brand).

Flood-fills from the border through pixels close to the flat background colour,
then softens the edge. Output: src/mascot_cut.png (RGBA, 1254x1254).
"""
import sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

SRC = sys.argv[1]
OUT = sys.argv[2]
TOL = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0

im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
bg = np.median(np.concatenate([a[:6].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)]), axis=0)
dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
near = dist < TOL

seen = np.zeros((h, w), bool)
dq = deque()
for x in range(w):
    for y in (0, h - 1):
        if near[y, x] and not seen[y, x]:
            seen[y, x] = True; dq.append((y, x))
for y in range(h):
    for x in (0, w - 1):
        if near[y, x] and not seen[y, x]:
            seen[y, x] = True; dq.append((y, x))
while dq:
    y, x = dq.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not seen[ny, nx]:
            seen[ny, nx] = True; dq.append((ny, nx))

alpha = np.where(seen, 0, 255).astype(np.uint8)
m = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
out = im.convert("RGBA"); out.putalpha(m)
out.save(OUT)
print("bg", bg, "transparent %.1f%%" % (seen.mean() * 100))
