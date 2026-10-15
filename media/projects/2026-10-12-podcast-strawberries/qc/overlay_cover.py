"""Replace the model-drawn book cover in a still with the genuine supplied cover.
usage: overlay_cover.py STILL OUT x0,y0,x1,y1 [--corners TLx,TLy,TRx,TRy,BRx,BRy,BLx,BLy] [--keep x0,y0,x1,y1 ...] [--preview P]
The box is a search window (native px) around the book. Corners are found from the red cover field unless given.
Lighting is carried over from the model's own render (low-frequency luminance ratio + per-channel gain).
--keep boxes are left untouched (fingers in front of the cover)."""
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

args = sys.argv[1:]
still, out = args[0], args[1]
box = [int(float(v)) for v in args[2].split(',')]
corners = None; keeps = []; preview = None
i = 3
while i < len(args):
    if args[i] == '--corners': corners = [float(v) for v in args[i+1].split(',')]; i += 2
    elif args[i] == '--keep': keeps.append([int(float(v)) for v in args[i+1].split(',')]); i += 2
    elif args[i] == '--preview': preview = args[i+1]; i += 2
    else: raise SystemExit('bad arg ' + args[i])
COVER = '/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-12-podcast-strawberries/references/book-cover-clean.png'
im = Image.open(still).convert('RGB'); A = np.asarray(im).astype(np.float32)
cov = Image.open(COVER).convert('RGB'); cw, ch = cov.size
x0, y0, x1, y1 = box
if corners is None:
    sub = A[y0:y1, x0:x1]; R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
    red = (R > 120) & (G < 0.55*R) & (B < 0.55*R)
    m = Image.fromarray((red*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5))
    ys, xs = np.nonzero(np.asarray(m) > 0)
    s, d = xs + ys, xs - ys
    pts = [(xs[s.argmin()], ys[s.argmin()]), (xs[d.argmax()], ys[d.argmax()]), (xs[s.argmax()], ys[s.argmax()]), (xs[d.argmin()], ys[d.argmin()])]
    corners = [c for (px, py) in pts for c in (px + x0, py + y0)]
TL, TR, BR, BL = [(corners[k], corners[k+1]) for k in (0, 2, 4, 6)]
print('corners TL,TR,BR,BL:', ','.join(f'{v:.0f}' for v in corners))
def coeffs(dst, src):  # maps output (dst) coords to source coords
    M = []; b = []
    for (x, y), (u, v) in zip(dst, src):
        M.append([x, y, 1, 0, 0, 0, -u*x, -u*y]); M.append([0, 0, 0, x, y, 1, -v*x, -v*y]); b += [u, v]
    return np.linalg.solve(np.array(M, float), np.array(b, float))
c = coeffs([TL, TR, BR, BL], [(0, 0), (cw, 0), (cw, ch), (0, ch)])
warped = cov.transform(im.size, Image.PERSPECTIVE, tuple(c), Image.BICUBIC)
mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).polygon([TL, TR, BR, BL], fill=255)
for k in keeps: ImageDraw.Draw(mask).rectangle(k, fill=0)
Wm = np.asarray(mask).astype(np.float32)/255
Wn = np.asarray(warped).astype(np.float32)
# lighting: per-channel gain + low-frequency luminance ratio taken from the model's render of the cover
sel = Wm > 0.5
gain = np.clip(A[sel].mean(axis=0) / (Wn[sel].mean(axis=0) + 1e-6), 0.6, 1.5)
Wn = Wn * gain
rad = max(8, int(0.18 * max(abs(TR[0]-TL[0]), abs(BL[1]-TL[1]))))
def lowlum(X):
    L = (0.299*X[..., 0] + 0.587*X[..., 1] + 0.114*X[..., 2]) * Wm
    Lb = np.asarray(Image.fromarray(np.clip(L, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rad))).astype(np.float32)
    Wb = np.asarray(Image.fromarray((Wm*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rad))).astype(np.float32)/255
    return Lb / (Wb + 1e-3)
shade = np.clip(lowlum(A) / (lowlum(Wn) + 1e-3), 0.7, 1.4)[..., None]
Wn = np.clip(Wn * shade, 0, 255)
soft = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)[..., None]/255
res = A*(1-soft) + Wn*soft
Image.fromarray(res.astype(np.uint8)).save(out)
print('gain', gain.round(2), 'saved', out)
if preview:
    pad = 40; bx = (max(int(min(TL[0], BL[0]))-pad, 0), max(int(min(TL[1], TR[1]))-pad, 0), min(int(max(TR[0], BR[0]))+pad, im.width), min(int(max(BL[1], BR[1]))+pad, im.height))
    a, b = im.crop(bx), Image.open(out).crop(bx)
    h = 620; a = a.resize((round(a.width*h/a.height), h), Image.LANCZOS); b = b.resize(a.size, Image.LANCZOS)
    sh = Image.new('RGB', (a.width*2+10, h), 'white'); sh.paste(a, (0, 0)); sh.paste(b, (a.width+10, 0)); sh.save(preview, quality=92)
