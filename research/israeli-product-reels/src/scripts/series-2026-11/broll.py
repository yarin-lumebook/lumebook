#!/usr/bin/python3
"""Drawn LumeBook books for the daily reels, made locally (no API, no cost) and kept in the reels' media library.

Yarin, 11 Nov 2026: "when i talk about something like the book with the name of the kid ... the object shown should match with
what i said ... taking a flat image and making it look like a book and adding the name on top", and the same evening:
"always make books look like lumebook books, always 3d and open unless im talking about the cover".

A LumeBook book is 22 x 22 cm, soft cover, 24 colour pages (docs/lumebook-product-brief.md). Inside, each spread is a full-bleed
picture of the child facing a white page with the story text; the title page has a round photo of the child, "הסיפור הקסום של",
the name and the LumeBook logo; the dedication page has a round photo, a printed line and the dedication. So:

  open        THE DEFAULT BOOK. An open book in 3D: the art page (the store cover art) and the story page with the child's name
              marked, pages that curve into the gutter, the page block and the soft cover under them, seen from the side of the
              text page. Spec: cover, name, lines (2 to 4 short story lines), optional art (another picture for the art page).
  title       the same open book at the title page (round photo, "הסיפור הקסום של", the name, the logo). Spec: cover, name.
  dedication  the same open book at the dedication page. Spec: cover, name, lines (printed) or hand (written in pen).
  cover       ONLY WHEN THE WORDS ARE ABOUT THE COVER: the closed book in 3D, the title with the child's name in white at the
              bottom like the printed covers. Spec: cover, title, optional sub, zoom (> 1 fills the frame with the title).
  overlay     the closed cover, cropped, for hook_overlay (the cover under Yarin's face while he says the hook).
  row         three closed books with one name (one child, every story: the covers are the subject). Spec: books [{cover, title}].
  ("book" is the old name of cover, "page" of open.)

Every kind but overlay is a 1080 x 1920 picture on a transparent ground: the reel builder puts it over the darkened child video
(reel_make.py). Text stays clear of the captions (y 1158 to 1248).

Each reel's edit.json lists its pictures under "mockups" ({"source/mk-...png": {"kind": ..., ...}}). render draws each one into
the library (media/projects/2026-11-11-reel-broll-pool/drawn/, named for what it shows, listed in library.json) unless the same
drawing is already there, and links it into the reel's source/:

    /usr/bin/python3 research/israeli-product-reels/src/scripts/series-2026-11/broll.py render 1.4      # one reel
    /usr/bin/python3 .../broll.py render all
    /usr/bin/python3 .../broll.py render-folder <reel folder> [id]       what the project server's reel jobs run
    /usr/bin/python3 .../broll.py sample open B41_boy נועם      # one drawing to the scratch folder given as 5th argument

Needs Pillow, numpy and python-bidi (all in /usr/bin/python3 on this Mac). Hebrew on the pictures is audience copy: no dashes,
the grammar rules in creators/creator-research/src/hebrew-rules.md, never AI wording.
"""
import json, math, shutil, sys
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from bidi.algorithm import get_display

sys.path.insert(0, str(Path(__file__).resolve().parent))
import library  # noqa: E402

ROOT = Path(__file__).resolve().parents[5]
FONTS = ROOT / "shared/brand/fonts"
LOGO = ROOT / "shared/brand/logo_wide.png"
W, H = 1080, 1920
INK, VIOLET, MARK, PAPER = (52, 44, 40), (91, 43, 214), (255, 226, 122), (252, 250, 246)
P = 1000                                   # one page, drawn at this size before the 3D view
DRAW_V = 3                                 # raise when the drawing changes: library drawings of the same spec are redrawn in place


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def body(size, weight=420):
    return font("Rubik-VariableFont_wght.ttf", size, weight)


def heb(s):
    return get_display(s)


def text_center(draw, cx, y, s, f, fill, shadow=None):
    s = heb(s)
    w = draw.textlength(s, font=f)
    if shadow:
        draw.text((cx - w / 2 + 3, y + 4), s, font=f, fill=shadow)
    draw.text((cx - w / 2, y), s, font=f, fill=fill)
    return w


def open_img(path):
    p = Path(path)
    return Image.open(p if p.is_absolute() else ROOT / p).convert("RGB")


def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


# ---------- the closed book (only when the cover is what is said) ----------

def cover_with_title(path, title, sub=None, size=860):
    c = open_img(path).resize((size, size), Image.LANCZOS)
    # darken the bottom a little so the white title reads, as on the printed covers
    shade = Image.new("L", (size, size), 0)
    sd = ImageDraw.Draw(shade)
    for y in range(int(size * 0.62), size):
        sd.line([(0, y), (size, y)], fill=int(150 * max(0.0, (y - size * 0.62) / (size * 0.38)) ** 1.4))
    c = Image.composite(Image.new("RGB", (size, size), (20, 12, 30)), c, shade)
    d = ImageDraw.Draw(c)
    ft = font("Heebo-Black.ttf", int(size * 0.085))
    while d.textlength(heb(title), font=ft) > size * 0.86:
        ft = font("Heebo-Black.ttf", ft.size - 2)
    y = size * (0.80 if sub else 0.84)
    text_center(d, size / 2, y - ft.size / 2, title, ft, (255, 255, 255), shadow=(0, 0, 0))
    if sub:
        fs = font("Heebo-Bold.ttf", int(size * 0.06))
        text_center(d, size / 2, y + ft.size * 0.75, sub, fs, (255, 236, 190), shadow=(0, 0, 0))
    return c


def persp(pa, pb):
    """Coefficients for Image.PERSPECTIVE mapping output points pa to input points pb."""
    import numpy as np
    A, B = [], []
    for (x, y), (u, v) in zip(pa, pb):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def shadowed(obj, dy=40, blur=26, alpha=0.5):
    a = obj.split()[3]
    sh = Image.new("RGBA", obj.size, (10, 6, 16, 0))
    sh.putalpha(a.point(lambda v: v * alpha).filter(ImageFilter.GaussianBlur(blur)))
    out = Image.new("RGBA", (obj.size[0] + 60, obj.size[1] + dy + 60), (0, 0, 0, 0))
    out.alpha_composite(sh, (30, 30 + dy))
    out.alpha_composite(obj, (30, 30))
    return out.crop(out.getbbox())


def book_object(cov, turn=0.10):
    """A closed soft-cover square book in 3D: the cover face, the page block along the opening edge (left: Hebrew books open
    to the left) and the bottom, the spine shading on the right; turned by `turn` so the opening edge leans away."""
    s = cov.size[0]
    pad, th = 70, max(14, s // 34)
    obj = Image.new("RGBA", (s + 2 * pad, s + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    for k in range(th, 0, -1):               # the page block: cream sheets down and to the left, a darker line every third
        tone = 238 - (8 if k % 3 == 0 else 0)
        d.rounded_rectangle([pad - k, pad + k, pad + s - k, pad + s + k], 12, fill=(tone, tone - 5, tone - 14, 255))
    d.rounded_rectangle([pad - th - 2, pad + th + 2, pad + s - th - 2, pad + s + th + 2], 12, outline=(150, 130, 110, 255), width=2)
    face = cov.convert("RGBA")
    hinge = Image.new("L", (s, s), 0)
    hd = ImageDraw.Draw(hinge)
    for x in range(int(s * 0.06)):
        hd.line([(s - 1 - x, 0), (s - 1 - x, s)], fill=int(95 * (1 - x / (s * 0.06))))
    hd.line([(s - int(s * 0.04), 0), (s - int(s * 0.04), s)], fill=120)
    face = Image.composite(Image.new("RGBA", (s, s), (0, 0, 0, 255)), face, hinge)
    gloss = Image.new("L", (s, s), 0)
    gd = ImageDraw.Draw(gloss)
    for x in range(s):
        gd.line([(x, 0), (x, s)], fill=int(30 * max(0, 1 - abs(x - s * 0.3) / (s * 0.35))))
    face = Image.composite(Image.new("RGBA", (s, s), (255, 255, 255, 255)), face, gloss)
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], 12, fill=255)
    obj.paste(face, (pad, pad), mask)
    if turn:
        w, h = obj.size
        dy = h * turn
        src = [(0, 0), (w, 0), (w, h), (0, h)]
        dst = [(w * turn * 0.7, dy), (w, 0), (w, h), (w * turn * 0.7, h - dy)]
        obj = obj.transform(obj.size, Image.PERSPECTIVE, persp(dst, src), Image.BICUBIC)
    return shadowed(obj.crop(obj.getbbox()))


def mk_cover(spec):
    zoom = float(spec.get("zoom", 1))
    obj = book_object(cover_with_title(spec["cover"], spec["title"], spec.get("sub"), int(740 * zoom)), 0.10 if zoom == 1 else 0.05)
    c = canvas()
    if zoom <= 1:
        # below the top numbers and hook text (to y 444), the title above the captions (y 1158)
        cy = spec.get("cy", 830)
        c.alpha_composite(obj, (int(W / 2 - obj.size[0] / 2), int(cy - obj.size[1] / 2)))
    else:                                    # the title fills the frame: the cover's lower part in the middle
        c.alpha_composite(obj, (int(W / 2 - obj.size[0] / 2), int(860 - obj.size[1] * 0.80)))
    return c


def mk_overlay(spec):
    return book_object(cover_with_title(spec["cover"], spec["title"], spec.get("sub"), 700), 0.06)


def mk_row(spec):
    c = canvas()
    objs = [book_object(cover_with_title(b["cover"], b["title"], b.get("sub"), 600), 0.06) for b in spec["books"]]
    xs, ys, rots = [W * 0.38, W * 0.62, W * 0.40], [470, 850, 1460], [4, -4, 3]   # titles clear of the captions
    for i in (2, 1, 0):
        o = objs[i].rotate(rots[i], Image.BICUBIC, expand=True)
        c.alpha_composite(o, (int(xs[i] - o.size[0] / 2), int(ys[i] - o.size[1] / 2)))
    return c


# ---------- the open book (the default) ----------

def round_photo(art, d):
    """The child's face from the cover art in a circle with a thin ring, as on the title and dedication pages."""
    a = art.copy()
    w, h = a.size
    r = int(min(w, h) * 0.24)
    cx, cy = w // 2, int(h * 0.40)
    face = a.crop((cx - r, cy - r, cx + r, cy + r)).resize((d, d), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    face.putalpha(m)
    ring = Image.new("RGBA", (d + 16, d + 16), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, d + 15, d + 15), fill=(225, 222, 228, 255))
    ring.alpha_composite(face, (8, 8))
    return ring


def logo(width):
    lg = Image.open(LOGO).convert("RGBA")
    return lg.resize((width, int(lg.size[1] * width / lg.size[0])), Image.LANCZOS)


def lines_block(pg, lines, name, top, size, mark=True, color=INK, weight=420, gap=0.62):
    d = ImageDraw.Draw(pg)
    f = body(size, weight)
    fb = font("Heebo-Bold.ttf", size)
    y = top
    for line in lines:
        vis = heb(line)
        vn = heb(name) if name else ""
        i = vis.find(vn) if vn and name in line else -1
        if i < 0:
            lw = d.textlength(vis, font=f)
            d.text(((P - lw) / 2, y), vis, font=f, fill=color)
        else:
            a, b = vis[:i], vis[i + len(vn):]
            wa, wn, wb = d.textlength(a, font=f), d.textlength(vn, font=fb), d.textlength(b, font=f)
            x0 = (P - wa - wn - wb) / 2
            if mark:
                d.rounded_rectangle([x0 + wa - 12, y + size * 0.10, x0 + wa + wn + 12, y + size * 1.22], 14, fill=MARK)
            d.text((x0, y), a, font=f, fill=color)
            d.text((x0 + wa, y - size * 0.02), vn, font=fb, fill=VIOLET if mark else color)
            d.text((x0 + wa + wn, y), b, font=f, fill=color)
        y += size * (1 + gap)
    return y


def page_story(spec):
    pg = Image.new("RGB", (P, P), PAPER)
    lines = spec.get("lines") or [f"{spec['name']} יצא להרפתקה"]
    size = 84 if max(len(x) for x in lines) <= 18 else (72 if max(len(x) for x in lines) <= 24 else 60)
    h = len(lines) * size * 1.62
    lines_block(pg, lines, spec.get("name"), (P - h) / 2 - 40, size, mark=spec.get("mark", True))
    ImageDraw.Draw(pg).text((P / 2 - 10, P - 70), "7", font=body(28), fill=(150, 140, 130))
    return pg


def page_title(spec, art):
    pg = Image.new("RGB", (P, P), PAPER)
    ph = round_photo(art, 250)
    pg.paste(ph, ((P - ph.size[0]) // 2, 150), ph)
    d = ImageDraw.Draw(pg)
    text_center(d, P / 2, 470, "הסיפור הקסום של", body(60, 450), (70, 64, 72))
    fn = font("Heebo-Bold.ttf", 120)
    while d.textlength(heb(spec["name"]), font=fn) > P * 0.8:
        fn = font("Heebo-Bold.ttf", fn.size - 4)
    text_center(d, P / 2, 560, spec["name"], fn, (34, 30, 34))
    lg = logo(330)
    pg.paste(lg, ((P - lg.size[0]) // 2, P - lg.size[1] - 60), lg)
    return pg


def page_dedication(spec, art):
    pg = Image.new("RGB", (P, P), PAPER)
    d = ImageDraw.Draw(pg)
    text_center(d, P / 2, 90, spec.get("printed", "הספר הזה מוקדש באהבה"), body(44, 450), (110, 100, 112))
    ph = round_photo(art, 190)
    pg.paste(ph, ((P - ph.size[0]) // 2, 180), ph)
    if spec.get("hand"):                     # written in pen on the ruled lines of the blank dedication page
        for k in range(4):
            d.line([(150, 560 + k * 92), (P - 150, 560 + k * 92)], fill=(214, 208, 214), width=3)
        hand = Image.new("RGBA", (P, P), (0, 0, 0, 0))
        hd = ImageDraw.Draw(hand)
        fh = font("Assistant-VariableFont_wght.ttf", 62, weight=300)
        y = 482
        for line in spec["hand"][:4]:
            vis = heb(line)
            hd.text(((P - hd.textlength(vis, font=fh)) / 2, y), vis, font=fh, fill=(38, 66, 150, 255))
            y += 92
        pg = pg.convert("RGBA")
        pg.alpha_composite(hand.rotate(-2, Image.BICUBIC))
        pg = pg.convert("RGB")
    else:
        lines_block(pg, spec.get("lines") or [f"ל{spec['name']} שלנו", "שתמיד תדע כמה אוהבים אותך"], spec.get("name"), 470, 54,
                    mark=spec.get("mark", False))
    lg = logo(260)
    pg.paste(lg, ((P - lg.size[0]) // 2, P - lg.size[1] - 50), lg)
    return pg


def page_art(art):
    return ImageOps.fit(art, (P, P), Image.LANCZOS, centering=(0.5, 0.45))


def shade_page(pg, gutter_right):
    """The fold: darker into the gutter, a soft light on the curve of the page."""
    import numpy as np
    a = np.asarray(pg.convert("RGB"), float)
    d = np.linspace(1, 0, P) if gutter_right else np.linspace(0, 1, P)   # 0 at the gutter
    f = 1 - 0.42 * (1 - d) ** 6 + 0.05 * np.exp(-((d - 0.22) / 0.12) ** 2) - 0.04 * d
    a = np.clip(a * f[None, :, None], 0, 255).astype("uint8")
    return Image.fromarray(a)


def curve(pg, gutter_right, sink=60, n=48):
    """The page curving into the gutter: near the binding it is foreshortened and sinks (Pillow mesh warp)."""
    mesh = []
    out_h = P + sink
    for i in range(n):
        d0, d1 = i / n, (i + 1) / n                 # distance from the gutter
        g = lambda d: 0.55 * d + 0.45 * d * d       # foreshortened near the gutter, flat at the outer edge
        dy = lambda d: sink * (1 - d) ** 2.6
        if gutter_right:
            X0, X1 = P - g(d1) * P, P - g(d0) * P
            s0, s1 = P - d1 * P, P - d0 * P
            y0, y1 = dy(d1), dy(d0)
        else:
            X0, X1 = g(d0) * P, g(d1) * P
            s0, s1 = d0 * P, d1 * P
            y0, y1 = dy(d0), dy(d1)
        box = (int(round(X0)), 0, int(round(X1)), out_h)
        if box[2] <= box[0]:
            continue
        mesh.append((box, (s0, -y0, s0, out_h - y0, s1, out_h - y1, s1, -y1)))
    src = pg.convert("RGBA")
    return src.transform((P, out_h), Image.MESH, mesh, Image.BICUBIC)


def open_book(left, right, cover_tone):
    """Two flat pages (art on the left, text on the right) as an open soft-cover book in 3D, on a transparent ground."""
    lw = curve(shade_page(left, True), True)
    rw = curve(shade_page(right, False), False)
    gap_x, top = 40, 40
    Wt, Ht = 2 * P + 2 * gap_x, P + 160
    book = Image.new("RGBA", (Wt, Ht), (0, 0, 0, 0))
    sil = Image.new("L", (Wt, Ht), 0)
    sil.paste(lw.split()[3], (gap_x, top), lw.split()[3])
    sil.paste(rw.split()[3], (gap_x + P, top), rw.split()[3])
    # the soft cover just under the pages, then the page block: cream sheets down and outward
    th = 12
    cov = Image.new("RGBA", (Wt, Ht), cover_tone + (255,))
    for k in range(th + 3, 0, -1):
        off = Image.new("L", (Wt, Ht), 0)
        sx = int(k * 0.9)
        off.paste(sil.crop((0, 0, Wt // 2, Ht)), (-sx, int(k * 2.3)))
        off.paste(sil.crop((Wt // 2, 0, Wt, Ht)), (Wt // 2 + sx, int(k * 2.3)))
        if k > th:
            book.paste(cov, (0, 0), off)
        else:
            tone = 236 - (12 if k % 3 == 0 else 0)
            book.paste(Image.new("RGBA", (Wt, Ht), (tone, tone - 6, tone - 16, 255)), (0, 0), off)
    book.alpha_composite(lw, (gap_x, top))
    book.alpha_composite(rw, (gap_x + P, top))
    gd = ImageDraw.Draw(book)                  # the gutter line
    gd.line([(gap_x + P, top + 50), (gap_x + P, top + P + 50)], fill=(120, 105, 95, 160), width=3)
    book = book.crop(book.getbbox())
    # the 3D view: seen a little from above and from the side of the text page (it comes closer, the art page leans away)
    w, h = book.size
    h2 = int(h * 0.86)                     # lying on a table, seen from above at an angle: shorter, the far edge narrower
    dst = [(w * 0.13, h2 * 0.17), (w * 0.95, 0), (w, h2), (0, h2 * 0.90)]
    book = book.transform((w, h2), Image.PERSPECTIVE, persp(dst, [(0, 0), (w, 0), (w, h), (0, h)]), Image.BICUBIC)
    book = book.crop(book.getbbox())
    return shadowed(book, dy=50, blur=34, alpha=0.6)


def tone_of(art):
    c = art.resize((1, 1), Image.LANCZOS).getpixel((0, 0))
    return tuple(int(v * 0.55) for v in c[:3])


def place_open(obj, spec, width=1200, cy=800):
    """The open book on the frame: wider than the frame so the text page is big enough to read on a phone; the art page runs a
    little off the left edge. The text page ends above the captions (y 1158)."""
    s = width / obj.size[0]
    obj = obj.resize((width, int(obj.size[1] * s)), Image.LANCZOS)
    c = canvas()
    x, y = W - obj.size[0] + int(spec.get("dx", -24)), int(spec.get("cy", cy) - obj.size[1] / 2)
    obj = obj.crop((max(0, -x), max(0, -y), obj.size[0], obj.size[1]))
    c.alpha_composite(obj.crop((0, 0, min(obj.size[0], W - max(0, x)), min(obj.size[1], H - max(0, y)))), (max(0, x), max(0, y)))
    return c


def mk_open(spec):
    art = open_img(spec.get("art") or spec["cover"])
    return place_open(open_book(page_art(art), page_story(spec), tone_of(art)), spec)


def mk_title(spec):
    art = open_img(spec.get("art") or spec["cover"])
    return place_open(open_book(page_art(art), page_title(spec, art), tone_of(art)), spec)


def mk_dedication(spec):
    art = open_img(spec.get("art") or spec["cover"])
    return place_open(open_book(page_art(art), page_dedication(spec, art), tone_of(art)), spec)


KINDS = {"open": mk_open, "title": mk_title, "dedication": mk_dedication, "cover": mk_cover, "overlay": mk_overlay, "row": mk_row,
         "book": mk_cover, "page": mk_open}
OPEN_KINDS = {"open", "title", "dedication", "page"}


# ---------- the library ----------

def describe(spec):
    """A file name and an English line that say what the drawing shows."""
    k = {"book": "cover", "page": "open"}.get(spec["kind"], spec["kind"])
    covers = [spec.get("cover")] + [b.get("cover") for b in spec.get("books", [])]
    code = next((Path(c).stem for c in covers if c), "art")
    what = {"open": "open-book-story-page-with-the-name", "title": "open-book-title-page-with-the-name",
            "dedication": "open-book-dedication-page", "cover": "closed-book-cover-with-the-name-in-the-title",
            "overlay": "closed-book-cover-small-for-the-hook", "row": "three-closed-books-with-one-name"}[k]
    name = spec.get("name") or spec.get("title") or ""
    about = {"open": "Open 3D LumeBook book: art page and the story page with the child's name marked",
             "title": "Open 3D LumeBook book at the title page: round photo, the child's name, the logo",
             "dedication": "Open 3D LumeBook book at the dedication page", "cover": "Closed 3D LumeBook book, the cover with the title",
             "overlay": "Closed LumeBook cover, small, transparent, for under the face during the hook",
             "row": "Three closed LumeBook books with the same child's name"}[k]
    text = " / ".join(spec.get("lines") or spec.get("hand") or ([spec["title"]] if spec.get("title") else [])
                      or [b.get("title", "") for b in spec.get("books", [])])
    words = [w for w in ([name] if name else []) + {"open": ["השם", "בסיפור", "בתוך הספר"], "title": ["השם", "העמוד הראשון"],
             "dedication": ["הקדשה", "מוקדש"], "cover": ["הכריכה", "על הכריכה"], "overlay": ["הכריכה"],
             "row": ["כל סיפור", "ספרים"]}[k]]
    return f"{what}-{code}", f"{about} ({code}; {name}{': ' + text if text else ''})", words


def draw_into_library(spec, rid=None):
    """The drawing for spec from the library, drawn first when it is not there. Returns its path."""
    key = library.key_of({"spec": spec, "v": DRAW_V})
    e = library.find("drawn", key)
    if e:
        return library.path_of(e), False
    img = KINDS[spec["kind"]](spec)
    base, about, words = describe(spec)
    old = next((x for x in library.load() if x.get("kind") == "drawn" and x.get("spec") == spec and library.path_of(x).exists()), None)
    # the same drawing made by an earlier version of this file is redrawn under its name (it costs nothing and nothing else
    # points at its pixels); a new drawing gets a new name
    out = library.path_of(old) if old else library.free_name(library.POOL / "drawn", base + "-" + key[:4], ".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    library.put({"file": str(out.relative_to(library.POOL)), "kind": "drawn", "about": about, "words": words, "key": key,
                 "spec": spec, "cost_usd": 0, "made": date.today().isoformat(),
                 "reels": sorted(set((old or {}).get("reels", []) + ([rid] if rid else [])))})
    return out, True


def retire(p, why):
    """Move a real file out of a reel folder into _to-delete/ under its original path, with a line in its README."""
    dest = ROOT / "_to-delete" / p.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest = dest.with_name(dest.stem + "-" + date.today().strftime("%Y%m%d") + dest.suffix)
    shutil.move(str(p), dest)
    with open(ROOT / "_to-delete/README.md", "a", encoding="utf-8") as fh:
        fh.write(f"- `{p.relative_to(ROOT)}` ({date.today().isoformat()}): {why}\n")


def render(folder, rid=None):
    e = json.loads((folder / "edit.json").read_text())
    for out, spec in (e.get("mockups") or {}).items():
        path, new = draw_into_library(spec, rid)
        dst = folder / out
        if dst.exists() and not dst.is_symlink():
            retire(dst, "an earlier flat drawing of broll.py, replaced by the 3D LumeBook book in the reels' media library")
        library.link(path, folder, out)
        if rid:
            library.used_in(str(path.relative_to(library.POOL)), rid)
        print(f"  {out} -> {path.relative_to(ROOT)}  {spec['kind']}{'  (drawn)' if new else '  (from the library)'}")


def whole_book(spec):
    """The whole book of a spec, not placed on the reel frame (nothing cut off), on a transparent ground."""
    k = {"book": "cover", "page": "open"}.get(spec["kind"], spec["kind"])
    if k in ("open", "title", "dedication"):
        art = open_img(spec.get("art") or spec["cover"])
        page = {"open": lambda: page_story(spec), "title": lambda: page_title(spec, art),
                "dedication": lambda: page_dedication(spec, art)}[k]()
        return open_book(page_art(art), page, tone_of(art))
    if k == "cover":
        return book_object(cover_with_title(spec["cover"], spec["title"], spec.get("sub"), 740), 0.10)
    return KINDS[spec["kind"]](spec)


def ref_on_white(drawn, out):
    """A library drawing's whole book on white, as a reference picture for a GPT edit (reel_gpt.py fixbooks)."""
    e = next(x for x in library.load() if x.get("kind") == "drawn" and library.path_of(x).resolve() == Path(drawn).resolve())
    obj = whole_book(e["spec"])
    bg = Image.new("RGBA", (obj.size[0] + 80, obj.size[1] + 80), (255, 255, 255, 255))
    bg.alpha_composite(obj, (40, 40))
    bg = bg.convert("RGB")
    bg.thumbnail((1536, 1536))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    bg.save(out)


def main():
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "ref":   # reel_gpt.py fixbooks: a drawing's whole book on white
        ref_on_white(a[1], a[2])
        return
    if len(a) >= 5 and a[0] == "sample":
        kind, cov, name, out = a[1], a[2], a[3], Path(a[4])
        spec = {"kind": kind, "cover": f"media/projects/2026-11-10-store-covers/{cov}.webp", "name": name, "title": f"הספר של {name}",
                "lines": [f"{name} קם בבוקר", "והבין שהיום הוא יום מיוחד"]}
        KINDS[kind](spec).save(out)
        print(out)
        return
    if len(a) >= 2 and a[0] == "render-folder":   # the project server's reel jobs: a reel folder (and its id)
        render(Path(a[1]), a[2] if len(a) > 2 else None)
        return
    if len(a) < 2 or a[0] != "render":
        sys.exit(__doc__)
    reels = json.loads((Path(__file__).resolve().parent / "reels.json").read_text())["reels"]
    want = None if a[1] == "all" else set(a[1:])
    for r in reels:
        if r.get("project") and (want is None or r["id"] in want):
            f = ROOT / r["project"]
            if (f / "edit.json").exists() and json.loads((f / "edit.json").read_text()).get("mockups"):
                print(r["id"])
                render(f, r["id"])


if __name__ == "__main__":
    main()
