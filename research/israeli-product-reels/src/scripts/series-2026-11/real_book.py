#!/usr/bin/python3
"""Realistic LumeBook books from the blank renders (book-templates/, 11 Nov 2026), drawn locally at no cost.

Yarin, 20 Nov 2026, choosing from every book look we have: "10-14 are the most accurate but i need you to add images (always on
the cover and the left side when open) and hebrew text on the right side". So each blank render gets, in its own perspective and
under its own light (the render's brightness multiplies the pasted page, which keeps the gutter shadow, the curl and the edges):

  real-cover     the closed book standing, the cover turned three quarters: the store cover art with the title
  real-open      the open book from the top: the picture on the left page, the Hebrew story page on the right
  real-standing  the open book standing towards the camera: picture left, Hebrew right
  real-turn      the open book with a page halfway through a turn: picture left, Hebrew right, the turning page a picture
  real-stack     three closed books stacked: the cover art with the title on the top one

Spec (as broll.py's): cover (a store cover), title (the cover kinds), name and lines (the open kinds), optional art (the left
page; default the cover art) and art2 (the turning page; default the art zoomed to another part). broll.py lists these kinds,
so they go in a reel's edit.json "mockups" and into the library like every drawing.

    /usr/bin/python3 real_book.py sample <kind> <out.png>      one drawing, for a look
    /usr/bin/python3 real_book.py cover <cover> <out.png> [title]   the closed book alone, cut out (no title: the art as it is)
"""
import math, sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import broll  # noqa: E402

TEMPLATES = broll.ROOT / "media/projects/2026-11-11-reel-broll-pool/book-templates"
SS = 4                                       # supersampling of the masks

# Surfaces in template pixels (1024 x 1536), read off the renders. "quad": TL, TR, BR, BL of the flat surface as it should be
# read (for a page: its outer top, gutter top, gutter bottom, outer bottom are mapped from the page's left/right as printed).
# "turn": a curled page as a Coons patch (four corners plus a control point on the top and bottom edges).
TPL = {
    "real-cover": {"file": "book-blank-closed-standing-cover-three-quarter.png",
                   "surfaces": [("cover", [(231, 355), (832, 302), (832, 1060), (231, 1165)])],
                   "outline": [(187, 356), (859, 297), (859, 1059), (858, 1060), (204, 1173), (188, 1162)]},
    "real-open": {"file": "book-blank-open-flat-top-view.png",
                  "surfaces": [("left", [(57, 463), (503, 459), (503, 1011), (57, 1014)]),
                               ("right", [(516, 459), (971, 463), (971, 1004), (516, 1010)])],
                  "outline": [(50, 459), (977, 459), (979, 1016), (51, 1018)]},
    "real-standing": {"file": "book-blank-open-standing-shown.png",
                      "surfaces": [("left", [(106, 479), (501, 447), (501, 988), (109, 1073)]),
                                   ("right", [(509, 447), (905, 471), (905, 1071), (509, 988)])],
                      "outline": [(88, 467), (488, 437), (527, 436), (938, 461), (934, 1075), (505, 993), (93, 1079)]},
    "real-turn": {"file": "book-blank-open-page-turning.png",
                  "surfaces": [("left2", [(198, 469), (588, 522), (466, 975), (45, 906)]),
                               ("right", [(592, 530), (982, 594), (906, 1060), (470, 976)]),
                               ("turn", {"tl": (366, 303), "tr": (590, 528), "br": (470, 973), "bl": (395, 790),
                                         "top": (548, 332), "bottom": (588, 852)})],
                  "outline": None},
    # three more renders measured on 20 Nov 2026 for the Black Friday offer posts ("using different book models as well")
    "real-cover-2": {"file": "book-blank-closed-standing-cover-three-quarter-2.png",
                     "surfaces": [("cover", [(228, 368), (822, 318), (822, 1066), (228, 1170)])],
                     "outline": [(186, 368), (851, 314), (849, 1068), (225, 1180), (188, 1167)]},
    "real-flat": {"file": "book-blank-closed-flat-above-angle.png",
                  "surfaces": [("cover", [(353, 402), (910, 532), (735, 1045), (110, 848)])],
                  "outline": [(353, 400), (938, 536), (757, 1067), (108, 852)]},
    "real-standing-2": {"file": "book-blank-open-standing-shown-2.png",
                        "surfaces": [("left", [(97, 483), (504, 453), (504, 949), (104, 1006)]),
                                     ("right", [(516, 453), (915, 480), (915, 1006), (516, 949)])],
                        "outline": [(81, 480), (500, 444), (525, 444), (944, 480), (935, 1012), (510, 955), (92, 1012)]},
    "real-stack": {"file": "book-blank-three-closed-stacked.png",
                   "surfaces": [("cover", [(250, 458), (761, 388), (905, 893), (305, 999)])],
                   "outline": [(200, 459), (763, 385), (926, 800), (921, 826), (902, 913), (702, 965), (550, 1173), (382, 1122),
                               (95, 872), (82, 845), (104, 622), (198, 577)]},
}


def poly_mask(size, pts, grow=0):
    m = Image.new("L", (size[0] * SS, size[1] * SS), 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    m = m.resize(size, Image.LANCZOS)
    if grow > 0:
        m = m.filter(ImageFilter.MaxFilter(2 * grow + 1))
    elif grow < 0:
        m = m.filter(ImageFilter.MinFilter(-2 * grow + 1))
    return m


def bezier(p0, c, p1, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])


def coons(s, u, v):
    top, bot = bezier(s["tl"], s["top"], s["tr"], u), bezier(s["bl"], s["bottom"], s["br"], u)
    lef = (s["tl"][0] + (s["bl"][0] - s["tl"][0]) * v, s["tl"][1] + (s["bl"][1] - s["tl"][1]) * v)
    rig = (s["tr"][0] + (s["br"][0] - s["tr"][0]) * v, s["tr"][1] + (s["br"][1] - s["tr"][1]) * v)
    bil = [(1 - u) * (1 - v) * s["tl"][k] + u * (1 - v) * s["tr"][k] + (1 - u) * v * s["bl"][k] + u * v * s["br"][k] for k in (0, 1)]
    return tuple((1 - v) * top[k] + v * bot[k] + (1 - u) * lef[k] + u * rig[k] - bil[k] for k in (0, 1))


def warp_quad(img, quad, size):
    w, h = img.size
    coeffs = broll.persp(quad, [(0, 0), (w, 0), (w, h), (0, h)])
    return img.convert("RGB").transform(size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)


def warp_patch(img, s, size, n=28):
    """The picture laid over a curled page: n x n small perspective cells, each drawn into its own box."""
    src = img.convert("RGB")
    w, h = src.size
    out = Image.new("RGB", size)
    mask = Image.new("L", size, 0)
    for i in range(n):
        for j in range(n):
            u0, u1, v0, v1 = i / n, (i + 1) / n, j / n, (j + 1) / n
            q = [coons(s, u0, v0), coons(s, u1, v0), coons(s, u1, v1), coons(s, u0, v1)]
            x0, y0 = int(math.floor(min(p[0] for p in q))) - 1, int(math.floor(min(p[1] for p in q))) - 1
            x1, y1 = int(math.ceil(max(p[0] for p in q))) + 1, int(math.ceil(max(p[1] for p in q))) + 1
            rel = [(x - x0, y - y0) for x, y in q]
            cell = src.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE,
                                 broll.persp(rel, [(u0 * w, v0 * h), (u1 * w, v0 * h), (u1 * w, v1 * h), (u0 * w, v1 * h)]),
                                 Image.BICUBIC)
            cm = Image.new("L", (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(cm).polygon(rel, fill=255)
            cm = cm.filter(ImageFilter.MaxFilter(3))
            out.paste(cell, (x0, y0), cm)
            mask.paste(255, (x0, y0), cm)
    outline = [coons(s, k / 40, 0) for k in range(41)] + [coons(s, 1, k / 40) for k in range(41)] + \
              [coons(s, 1 - k / 40, 1) for k in range(41)] + [coons(s, 0, 1 - k / 40) for k in range(41)]
    return out, ImageChops.multiply(mask, poly_mask(size, outline)), outline


def shade(content, tpl_l, mask):
    """The render's light on the pasted page: its brightness over the page's own white, a little brighter allowed."""
    L = np.asarray(tpl_l, float)
    m = np.asarray(mask) > 128
    ref = np.percentile(L[m], 96) if m.any() else 255.0
    f = np.clip(L / ref, 0, 1.06)
    a = np.asarray(content, float) * f[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def pages_for(kind, spec):
    art = broll.open_img(spec.get("art") or spec["cover"])
    if kind in ("real-cover", "real-cover-2", "real-flat", "real-stack"):
        if not spec.get("title"):           # the store cover art as it is (the seasonal offer posts, 20 Nov 2026)
            art = broll.open_img(spec["cover"])   # a store cover with white bars (B22) loses them, then fills the square
            box = ImageChops.difference(art, Image.new("RGB", art.size, (255, 255, 255))).convert("L").point(lambda v: 255 if v > 18 else 0).getbbox()
            return {"cover": ImageOps.fit(art.crop(box) if box else art, (1000, 1000), Image.LANCZOS)}
        return {"cover": broll.cover_with_title(spec["cover"], spec["title"], spec.get("sub"), 1000)}
    left = broll.page_art(art)
    right = broll.page_story(spec)
    out = {"left": left, "right": right}
    if kind == "real-turn":
        w, h = art.size                      # another part of the same picture, so the two lower pages differ
        out["left2"] = broll.page_art(art.crop((int(w * 0.18), int(h * 0.05), int(w * 0.92), int(h * 0.79))))
        out["turn"] = broll.page_art(broll.open_img(spec["art2"])) if spec.get("art2") else left
    return out


def render_book(kind, spec):
    """The book of spec on a transparent ground, cut to its size, with a soft shadow."""
    t = TPL[kind]
    tpl = Image.open(TEMPLATES / t["file"]).convert("RGB")
    size = tpl.size
    tl = tpl.convert("L")
    pages = pages_for(kind, spec)
    out = tpl.copy()
    union = Image.new("L", size, 0)
    outline_pts = []
    for role, geo in t["surfaces"]:
        if role == "turn":
            warped, m, outline_pts = warp_patch(pages["turn"], geo, size)
        else:
            warped = warp_quad(pages[role], geo, size)
            m = poly_mask(size, geo, grow=-1)
        out.paste(shade(warped, tl, m), (0, 0), m)
        union = ImageChops.lighter(union, m)
    # what is book and what is the grey ground: the outline (or the surfaces) with a soft edge, and at the rim only what is
    # lighter than the ground (the edges of the page block), never the shadow
    if t["outline"]:
        sil = poly_mask(size, t["outline"])
    else:
        sil = ImageChops.lighter(union.filter(ImageFilter.MaxFilter(9)), poly_mask(size, outline_pts, grow=3) if outline_pts else union)
        L = np.asarray(tl, float)
        ground = np.percentile(np.concatenate([L[:20].ravel(), L[-20:].ravel()]), 60)
        lit = Image.fromarray(((L > ground + 6) * 255).astype("uint8")).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
        sil = ImageChops.lighter(union.filter(ImageFilter.MaxFilter(3)), ImageChops.multiply(sil, lit))
    sil = sil.filter(ImageFilter.GaussianBlur(0.8))
    book = out.convert("RGBA")
    book.putalpha(sil)
    book = book.crop(sil.getbbox())
    return broll.shadowed(book, dy=34, blur=30, alpha=0.55)


def place(obj, spec):
    """On the reel frame (1080 x 1920, transparent): as large as fits 1000 x 880, centred at y 830 (between the hook and the
    captions; reel_make's "box" can move it)."""
    s = min(1000 / obj.width, 880 / obj.height)
    obj = obj.resize((round(obj.width * s), round(obj.height * s)), Image.LANCZOS)
    c = broll.canvas()
    c.alpha_composite(obj, ((broll.W - obj.width) // 2, int(spec.get("cy", 830) - obj.height / 2)))
    return c


def make(kind):
    return lambda spec: place(render_book(kind, spec), spec)


def pair(spec):
    """Two closed books standing side by side, each its own cover and title (one per child: "the name of each one is on the
    cover"). Spec: books [{cover, title}, {cover, title}], the first on the right (Hebrew reads from the right)."""
    a, b = (render_book("real-cover", x) for x in spec["books"][:2])
    h = max(a.height, b.height)
    a, b = (o.resize((round(o.width * h / o.height), h), Image.LANCZOS) for o in (a, b))
    ov = int(a.width * 0.10)
    both = Image.new("RGBA", (a.width + b.width - ov, h + 40), (0, 0, 0, 0))
    both.alpha_composite(b, (0, 40))             # the second book a little behind and lower, on the left
    both.alpha_composite(a, (b.width - ov, 0))
    return place(both, spec)


KINDS = {k: make(k) for k in TPL}
KINDS["real-pair"] = pair

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "sample":
        demo = {"cover": "media/projects/2026-11-10-store-covers/B15_girl.webp", "title": "יום ההולדת של נויה", "name": "נויה",
                "lines": ["בבוקר יום ההולדת", "נויה פקחה את העיניים,", "והבית כולו היה מלא בלונים.", "״זה בשבילי?״ שאלה נויה."]}
        KINDS[a[1]](demo).save(a[2])
        print(a[2])
    elif len(a) >= 4 and a[0] == "book":
        # any kind, cut out: real_book.py book <kind> <cover> <out.png> [story line ...] (open kinds: the lines on the right page)
        spec = {"cover": a[2], "title": "", "name": None, "lines": a[4:] or ["ספר מותאם אישית"]}
        render_book(a[1], spec).save(a[3])
        print(a[3])
    elif len(a) in (3, 4) and a[0] == "cover":
        # the closed book alone, cut out with its shadow on a transparent ground: real_book.py cover <cover> <out.png> [title]
        render_book("real-cover", {"cover": a[1], "title": a[3] if len(a) == 4 else ""}).save(a[2])
        print(a[2])
    else:
        sys.exit(__doc__)
