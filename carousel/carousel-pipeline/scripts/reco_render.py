#!/usr/bin/env python3
"""Render the daily recommendation carousel (games and books together, or the older separate ones) and its review page.

    python3 carousel/carousel-pipeline/scripts/reco_render.py drafts/DATE/reco-carousel.json      # slides + review
    python3 carousel/carousel-pipeline/scripts/reco_render.py drafts/DATE/games-carousel.json --no-png   # an older night

Slides are HTML and CSS set in Heebo and Assistant, right to left, 1080 x 1350, exported with Google Chrome
(no image generation, no paid call). Recommendation slides put the real product or cover image in the centre,
whole and undistorted (object-fit: contain inside a white card), with the title above and the reason below.

Writes drafts/DATE/<dir>/slides.html (dir: reco for the mixed carousel, games or books on older nights), 01.png to
NN.png (up to 20), contact-sheet.png and render-report.json, writes the carousel's own page (reco.html, or games.html and
books.html), and puts the tab bar on drafts/DATE/review.html (create_review.write_review calls inject_review).
Standard library only.
"""

import argparse
import html as htmlmod
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import reco_lib as rl  # noqa: E402
from carousel_lib import esc  # noqa: E402

W, H = 1080, 1350
FONTS = lib.PIPELINE / "assets" / "fonts"
# Theme colours set by Yarin (11 Oct 2026): games #5141A5, books #D80B64. (accent, soft tint, deep shade)
# The slide background is a light pastel of the theme colour (base, a slightly deeper tone for the last slide), as r,g,b
BACKGROUNDS = {"games": ("241,236,255", "233,225,255"), "books": ("253,236,243", "251,222,234")}
# Then (same day) "the most saturated version" of each: same hue and lightness, saturation 100%: #2500E6 and #E30063
ACCENTS = {"games": ("#2500E6", "#E9E5FF", "#160087"), "books": ("#E30063", "#FFE0EE", "#85003A")}
# The combined carousel (14 Oct 2026) sits on the LumeBook purple pastel with the games violet; each product slide's
# small kind tag takes its own kind's colour (games violet, books pink).
BACKGROUNDS[rl.MIXED] = BACKGROUNDS["games"]
# Yarin, 14 Oct 2026: "go back to cream" (his reference slide): every slide of the combined carousel but the close
# slide, which stays exactly as it was.
CREAM = ("250,246,239", "244,237,226")
ACCENTS[rl.MIXED] = ACCENTS["games"]
BACKGROUNDS[rl.MIXED2], ACCENTS[rl.MIXED2] = BACKGROUNDS[rl.MIXED], ACCENTS[rl.MIXED]
KIND_ACCENT = {"game": ACCENTS["games"][0], "book": ACCENTS["books"][0]}

SLIDE_CSS = """
@font-face{font-family:"Heebo";src:url("{heebo}") format("truetype");font-weight:900;font-display:block}
@font-face{font-family:"Heebo";src:url("{heebo_bold}") format("truetype");font-weight:700;font-display:block}
@font-face{font-family:"Assistant";src:url("{assistant}") format("truetype");font-weight:200 800;font-display:block}
*{box-sizing:border-box;margin:0;padding:0}
html,body{direction:rtl}
body{background:#d9d2c6}
body.single .slide:not(.on){display:none}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:rgb(var(--bg,241,236,255));color:#1D1039;direction:rtl;text-align:center;--ink:#1D1039;--ink2:#4B4062}
.slide.dark{background:#1D1039;--ink:#F8F0E1;--ink2:#D9CFF0}
.glow{position:absolute;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.75) 0,rgba(255,255,255,0) 68%);left:90px;top:300px;pointer-events:none}
.dark .glow{opacity:.08}
.bignum{font-family:"Heebo",sans-serif;font-weight:900;font-size:300px;line-height:.86;color:var(--accent);letter-spacing:-.04em}
/* Last slide (Yarin, 9 Oct 2026): a background made of everything the carousel suggested, every product and the
   LumeBook book, whole on white tiles, under a purple layer; only the save and comment lines on top. */
.collage{position:absolute;inset:0;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(4,1fr);gap:16px;padding:16px;background:rgb(var(--bg,241,236,255))}
.collage .t{background:#fff;border-radius:24px;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:16px}
.collage .t img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain}
.purple{position:absolute;inset:0;background:linear-gradient(180deg,rgba(var(--bg,241,236,255),.90) 0%,rgba(var(--bg2,233,225,255),.86) 50%,rgba(var(--bg,241,236,255),.92) 100%)}
/* Text-only slides: one big line, quieter supporting lines, generous space between them */
.sub{font-family:"Assistant",sans-serif;font-weight:700;line-height:1.32;color:var(--ink2)}
.lead{font-family:"Assistant",sans-serif;font-weight:800;line-height:1.25;color:var(--ink2)}
.h.wrap .ln{white-space:normal;text-wrap:balance}
.icons{display:flex;justify-content:center;gap:48px;margin-top:84px}
.icons .i{display:flex;flex-direction:column;align-items:center;gap:14px;font-family:"Assistant",sans-serif;font-weight:800;font-size:30px;color:var(--ink2)}
.icons .c{width:124px;height:124px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 14px 30px rgba(59,29,120,.14)}
.icons svg{width:60px;height:60px}.icons path{fill:none;stroke:#1D1039;stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round}
.block{position:absolute;left:90px;right:90px;direction:rtl;text-align:center;color:var(--ink)}
.h{font-family:"Heebo",sans-serif;font-weight:900;line-height:1.08;letter-spacing:-.01em;color:var(--ink)}
.b{font-family:"Heebo",sans-serif;font-weight:900;line-height:1.16;color:var(--ink);opacity:.86}
.how{font-family:"Assistant",sans-serif;font-weight:700;line-height:1.2;color:var(--ink2);margin-top:18px}
.age{font-family:"Assistant",sans-serif;font-weight:700;line-height:1.2;color:var(--ink2);margin-top:12px}
.hero3d{display:block;width:auto;height:auto;filter:drop-shadow(0 26px 30px rgba(29,16,57,.18))}
/* The LumeBook slide shows the cover of the catalogue book whose idea the line states (10 Oct 2026), flat in the same
   white card as the other books (Yarin, 14 Oct 2026: "look flat like the rest of the book examples and not as a 3d object") */
.ln{display:block;white-space:nowrap}
.prod{position:absolute;left:0;right:0;display:flex;align-items:center;justify-content:center}
.card{background:#fff;border-radius:28px;padding:22px;box-shadow:0 22px 50px rgba(29,16,57,.16),0 2px 6px rgba(29,16,57,.08);display:flex;align-items:center;justify-content:center}
.card img{display:block;width:auto;height:auto;object-fit:contain;border-radius:10px}
.fan{position:absolute;left:0;right:0;top:600px;height:600px}
.fan .card{position:absolute;padding:14px;border-radius:22px}
.fan .card img{max-width:340px;max-height:440px}
.block.mid{top:50%;transform:translateY(-50%)}
.kind{position:absolute;left:50%;transform:translateX(-50%);top:44px;padding:6px 26px 8px;border-radius:999px;background:var(--kind,var(--accent));color:#fff;font-family:"Assistant",sans-serif;font-weight:800;font-size:30px;line-height:1.2;letter-spacing:.01em}
.collage.big{grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(5,1fr);gap:14px;padding:14px}
.collage.big .t{border-radius:20px;padding:12px}
.arrow{position:absolute;left:50%;transform:translateX(-50%);bottom:44px;width:72px;height:72px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center}
.arrow svg{width:36px;height:36px}.arrow path{fill:none;stroke:#fff;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}
pre#report{display:none}
/* The bold look (Carousel Machine, 10 Oct 2026): a much bigger number, the hook and frame lines set larger, one phrase in a
   colour block, the question of the last slide marked the same way. It applies when the carousel marks a highlight. */
.look-bold .slide{--hl:var(--accent);--hl-ink:#FFF7E8}
.look-bold .bignum{font-size:380px;line-height:.82}
.look-bold .h{line-height:1.12;letter-spacing:-.02em}
.look-bold .fan{top:760px;height:520px}
.look-bold .hl{display:inline-block;background:var(--hl);color:var(--hl-ink);padding:0 .2em .05em;border-radius:.15em;transform:rotate(-1.6deg);box-shadow:0 10px 24px rgba(11,5,24,.22)}
.look-bold .ln:has(.hl){margin:.07em 0}
.look-bold .arrow{width:84px;height:84px}
/* The plain look (Yarin, 14 Oct 2026: "from now on design the text of the carousels like these except the cta slide leave it
   as it is"): every slide but the close one has centred Heebo Black headlines in dark plum, the number inside the hook
   sentence, no colour block behind any word, and secondary lines in Heebo Bold in a lighter plum. The close slide keeps the
   look above. Used by the combined games and books carousel; older games and books carousels keep their own look. */
.look-plain .slide:not([data-role="close"]){--ink:#1C1233;--ink2:#3D2F5E}
.look-plain .slide:not([data-role="close"]) .h{font-family:"Heebo",sans-serif;font-weight:900;color:var(--ink);line-height:1.1;letter-spacing:-.015em}
.look-plain .slide:not([data-role="close"]) :is(.b,.sub,.how,.age){font-family:"Heebo",sans-serif;font-weight:700;color:var(--ink2);opacity:1}
.look-plain .slide:not([data-role="close"]) .hl{background:none;color:inherit;padding:0;box-shadow:none;transform:none}
.look-plain .fan{top:540px;height:600px}
.look-plain .kind{background:none;color:var(--ink2);font-family:"Heebo",sans-serif;font-weight:700;font-size:32px;padding:0;top:48px}
"""

SLIDE_JS = """
const q = new URLSearchParams(location.search);
const one = q.get('s');
if (one) { document.body.classList.add('single'); document.querySelector('.slide[data-n="' + one + '"]').classList.add('on'); }
function fit(block) {
  // shrink every .fit inside the block until no line is wider than the column and the block fits its height
  const parts = [...block.querySelectorAll('.fit')];
  const wide = el => [...el.querySelectorAll('.ln')].some(l => l.scrollWidth > l.clientWidth + 1);
  parts.forEach(p => { p.style.fontSize = p.dataset.max + 'px'; let s = Number(p.dataset.max);
    while (wide(p) && s > Number(p.dataset.min)) { s -= 2; p.style.fontSize = s + 'px'; } p.dataset.size = s; });
  const maxH = Number(block.dataset.maxh || 99999); let guard = 0;
  while (block.scrollHeight > maxH + 1 && guard < 80) {
    let moved = false;
    parts.forEach(p => { let s = Number(p.dataset.size); if (s > Number(p.dataset.min)) { s -= 2; p.style.fontSize = s + 'px'; p.dataset.size = s; moved = true; } });
    if (!moved) break; guard++;
  }
  block.dataset.fit = (!parts.some(wide) && block.scrollHeight <= maxH + 1) ? 'ok' : 'overflow';
}
// Retailer packshots often sit on a white band (e.g. a 1200x1600 canvas around a square cover). Hide only that uniform
// margin with object-view-box: the file is untouched, the product itself is never cropped, and the aspect check uses the
// trimmed box. Only images whose record says trim_padding (the source added the band) are trimmed: a cover with its own
// light background would otherwise lose part of the cover. Nothing is trimmed when the corners are not near white.
function trim(img) {
  if (!img.naturalWidth) return;
  const w = Math.min(400, img.naturalWidth), h = Math.max(1, Math.round(img.naturalHeight * w / img.naturalWidth));
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h; const g = cv.getContext('2d'); g.drawImage(img, 0, 0, w, h);
  let d; try { d = g.getImageData(0, 0, w, h).data; } catch (e) { return; }
  const white = i => d[i] > 238 && d[i + 1] > 238 && d[i + 2] > 238;
  if (![0, (w - 1) * 4, (h - 1) * w * 4, (h * w - 1) * 4].every(white)) return;
  const rowInk = y => { let n = 0; for (let x = 0; x < w; x++) if (!white((y * w + x) * 4)) n++; return n > w * 0.01; };
  const colInk = x => { let n = 0; for (let y = 0; y < h; y++) if (!white((y * w + x) * 4)) n++; return n > h * 0.01; };
  let t = 0, b = h - 1, l = 0, r = w - 1;
  while (t < b && !rowInk(t)) t++; while (b > t && !rowInk(b)) b--; while (l < r && !colInk(l)) l++; while (r > l && !colInk(r)) r--;
  const pad = 0.01, T = Math.max(0, t / h - pad), B = Math.max(0, (h - 1 - b) / h - pad), L = Math.max(0, l / w - pad), R = Math.max(0, (w - 1 - r) / w - pad);
  if (Math.max(T, B, L, R) < 0.02) return;
  img.style.objectViewBox = `inset(${(T * 100).toFixed(2)}% ${(R * 100).toFixed(2)}% ${(B * 100).toFixed(2)}% ${(L * 100).toFixed(2)}%)`;
  img.dataset.aspect = (img.naturalWidth * (1 - L - R)) / (img.naturalHeight * (1 - T - B));
}
async function ready() {
  try { await document.fonts.ready; } catch (e) {}
  await Promise.all([...document.images].map(i => i.complete ? null : new Promise(r => { i.onload = r; i.onerror = r; })));
  document.querySelectorAll('img.main[data-trim]').forEach(trim);
  document.querySelectorAll('.block').forEach(fit);
  if (q.get('check')) {
    const rep = [...document.querySelectorAll('.slide')].map(s => {
      const sr = s.getBoundingClientRect();
      const blocks = [...s.querySelectorAll('.ln')].map(el => ({ text: el.textContent, direction: getComputedStyle(el).direction,
        overflow: el.scrollWidth > el.clientWidth + 1 }));
      const imgs = [...s.querySelectorAll('img.main')].map(img => { const r = img.getBoundingClientRect();
        return { src: img.getAttribute('src'), loaded: img.naturalWidth > 0, natural: [img.naturalWidth, img.naturalHeight],
          shown: [Math.round(r.width), Math.round(r.height)],
          aspect_error: img.naturalWidth ? Math.abs((img.offsetWidth / img.offsetHeight) / Number(img.dataset.aspect || img.naturalWidth / img.naturalHeight) - 1) : 1, trimmed: img.style.objectViewBox || '',  // layout size: rotation does not change it
          center_dx: Math.round(r.left - sr.left + r.width / 2 - 540), share: Math.max(r.width / 1080, r.height / 1350),
          top: Math.round(r.top - sr.top), bottom: Math.round(r.bottom - sr.top) }; });
      const texts = [...s.querySelectorAll('.block')].map(b => { const r = b.getBoundingClientRect(); return { fit: b.dataset.fit, top: Math.round(r.top - sr.top), bottom: Math.round(r.bottom - sr.top), where: b.dataset.where }; });
      return { n: Number(s.dataset.n), role: s.dataset.role, lang: document.documentElement.lang, htmlDir: document.documentElement.dir,
               direction: getComputedStyle(s).direction, blocks, imgs, texts };
    });
    document.getElementById('report').textContent = JSON.stringify(rep);
  }
  document.body.dataset.ready = '1';
  if (q.get('edit')) editMode();
}
// Editing straight on the slide (Yarin, 11 Oct 2026): the editor page shows this file in a frame with ?edit=1. Every text
// block is typed into in place and each change is posted to the page, which keeps the field under the slide in step and saves.
function editMode() {
  const slide = document.querySelector('.slide.on') || document.querySelector('.slide'); if (!slide) return;
  const st = document.createElement('style');
  st.textContent = '[data-f]{outline:3px dashed rgba(29,16,57,.28);outline-offset:8px;border-radius:10px;cursor:text}[data-f]:focus{outline:4px solid var(--accent);background:rgba(255,255,255,.55)}.ln{white-space:pre-wrap}';
  document.head.appendChild(st);
  const lines = el => el.innerText.replace(/\\u00a0/g, ' ').split('\\n').map(x => x.trim()).filter(Boolean);
  const value = f => { let out = ''; slide.querySelectorAll('[data-f="' + f + '"]').forEach(el => { const t = lines(el).join('\\n'); if (!t) return;
    out += (out ? (out.endsWith('\\u0001') ? '' : '\\n') : '') + t + (el.dataset.join === 'space' ? ' \\u0001' : ''); }); return out.replace(/\\u0001/g, ''); };
  slide.querySelectorAll('[data-f]').forEach(el => {
    try { el.contentEditable = 'plaintext-only'; } catch (e) { el.contentEditable = 'true'; }
    if (el.contentEditable !== 'plaintext-only') el.contentEditable = 'true';
    el.addEventListener('input', () => parent.postMessage({ lumebookEdit: 1, slide: Number(slide.dataset.n), field: el.dataset.f, value: value(el.dataset.f) }, '*'));
    el.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); parent.postMessage({ lumebookEdit: 1, save: 1 }, '*'); } });
  });
}
ready();
"""

# Instagram's save, share and comment actions, drawn as plain outline icons
ICONS = ('<div class="icons">'
         '<div class="i"><div class="c"><svg viewBox="0 0 48 48"><path d="M13 7h22v34l-11-9-11 9z"/></svg></div></div>'
         '<div class="i"><div class="c"><svg viewBox="0 0 48 48"><path d="M43 6 5 20l15 7 7 15z M43 6 20 27"/></svg></div></div>'
         '<div class="i"><div class="c"><svg viewBox="0 0 48 48"><path d="M24 6c10 0 18 7.6 18 17s-8 17-18 17c-2.6 0-5-.5-7.2-1.4L7 41l2.6-8.6C7.6 29.7 6 26.5 6 23 6 13.6 14 6 24 6z"/></svg></div></div>'
         '</div>')

ARROW = '<div class="arrow"><svg viewBox="0 0 36 36"><path d="M30 18H7M16 8 6 18l10 10"/></svg></div>'


def rel(target, base):
    return Path(os.path.relpath(target, base)).as_posix()


def _safe(piece):
    parts = re.split(r"([A-Za-z][A-Za-z0-9 .'&-]*[A-Za-z0-9]|[A-Za-z])", piece)
    return "".join(f'<bdi dir="ltr">{esc(p)}</bdi>' if i % 2 else esc(p) for i, p in enumerate(parts))


def lines_html(text, highlight=None):
    """One <span class="ln"> per line; `highlight` (a phrase of one line) gets the colour block once."""
    out = []
    highlight = (highlight or "").strip()
    for line in lib.lines_of(text):
        if highlight and highlight in line:
            before, after = line.split(highlight, 1)
            out.append(f'<span class="ln">{_safe(before)}<span class="hl">{_safe(highlight)}</span>{_safe(after)}</span>')
            highlight = ""
        else:
            out.append(f'<span class="ln">{_safe(line)}</span>')
    return "".join(out)


def is_plain(car):
    """The plain text look (14 Oct 2026) is the look of the combined games and books carousel, the nightly format from then on."""
    return car.get("format") in rl.MIXED_FORMATS


def is_bold(car):
    return any(str(s.get("highlight") or "").strip() for s in car.get("slides", []))


def trim_attr(product):
    return ' data-trim="1"' if product["image"].get("trim_padding") else ""


def slide_html(car, s, out_dir, folder, index):
    n, role = s["number"], s["role"]
    products = {p["id"]: p for p in car["products"]}
    accent, soft, deep = ACCENTS[car["format"]]
    dark = False  # every slide sits on the pastel purple, the close one included
    bold = is_bold(car)
    plain = is_plain(car) and role != "close"  # the close slide keeps today's look
    hl = (s.get("highlight") or "").strip() if bold and not plain else None
    bg = CREAM if car["format"] in rl.MIXED_FORMATS and role != "close" else BACKGROUNDS[car["format"]]
    parts = [f'<section class="slide{" dark" if dark else ""}" data-n="{n}" data-role="{role}" data-format="{car["format"]}" style="--accent:{accent};--soft:{soft};--deep:{deep};--bg:{bg[0]};--bg2:{bg[1]}"><div class="glow"></div>']
    if role == "hook" and plain:
        # The number inside the sentence, one big Heebo Black headline (Yarin, 14 Oct 2026)
        parts.append('<div class="block" data-where="top" style="top:96px" data-maxh="430">'
                     f'<div data-f="headline" class="h fit" data-max="120" data-min="72">{lines_html(s["headline"])}</div></div>')
        cards = []
        shown = fan_products(car)
        spots = {2: [(560, 5, 1, 60), (150, -5, 2, 60)], 3: [(640, 6, 1, 90), (356, 0, 3, 20), (72, -6, 2, 90)]}[len(shown)]
        for p, (x, rot, z, top) in zip(shown, spots):
            src = rel(Path(folder) / p["image"]["file"], out_dir)
            cards.append(f'<div class="card" style="left:{x}px;top:{top}px;transform:rotate({rot}deg);z-index:{z}"><img class="main"{trim_attr(p)} src="{esc(src)}" alt=""></div>')
        parts.append('<div class="fan">' + "".join(cards) + '</div>')
    elif role == "hook":
        # The number of suggestions on its own line, much bigger than the words (Yarin, 9 Oct 2026)
        m = re.match(r"\s*(\d+)\s+", s["headline"])
        num, rest = (m.group(1), s["headline"][m.end():]) if m else ("", s["headline"])
        parts.append(f'<div class="block" data-where="top" style="top:{70 if bold else 90}px" data-maxh="{640 if bold else 500}">'
                     + (f'<div class="bignum" data-f="headline" data-join="space">{esc(num)}</div>' if num else "")
                     + f'<div data-f="headline" class="h fit" data-max="{124 if bold else 96}" data-min="{72 if bold else 60}">{lines_html(rest, hl)}</div>'
                     + (f'<div data-f="body" class="b fit" data-max="52" data-min="38" style="margin-top:26px">{lines_html(s["body"])}</div>' if s.get("body", "").strip() else "") + '</div>')
        cards = []
        shown = fan_products(car)  # the fan shows up to three of the products, however many suggestions there are
        spots = {2: [(560, 5, 1, 60), (150, -5, 2, 60)], 3: [(640, 6, 1, 90), (356, 0, 3, 20), (72, -6, 2, 90)]}[len(shown)]
        for p, (x, rot, z, top) in zip(shown, spots):
            src = rel(Path(folder) / p["image"]["file"], out_dir)
            cards.append(f'<div class="card" style="left:{x}px;top:{top}px;transform:rotate({rot}deg);z-index:{z}"><img class="main"{trim_attr(p)} src="{esc(src)}" alt=""></div>')
        parts.append('<div class="fan">' + "".join(cards) + '</div>')
    elif role == "frame":
        parts.append(f'<div class="block mid" data-where="middle" data-maxh="980"><div data-f="headline" class="h fit" data-max="{112 if bold else 88}" data-min="{70 if bold else 58}">{lines_html(s["headline"], hl)}</div>'
                     + (f'<div data-f="body" class="sub fit" data-max="52" data-min="38" style="margin-top:64px">{lines_html(s["body"])}</div>' if s.get("body", "").strip() else "") + '</div>')
    elif role == "recommendation":
        kind = products[s["product_id"]].get("kind")
        if car["format"] in rl.MIXED_FORMATS and kind in rl.KIND_HE:
            # a small tag above the title in the empty top band: games and books share one carousel (14 Oct 2026)
            parts.append(f'<div class="kind" data-kind="{kind}" style="--kind:{KIND_ACCENT[kind]}">{esc(rl.KIND_HE[kind])}</div>')
        parts.append(f'<div class="block" data-where="title" style="top:110px" data-maxh="220"><div data-f="headline" class="h fit" data-max="84" data-min="52">{lines_html(s["headline"])}</div>'
                     f'<div data-f="age" class="age fit" data-max="36" data-min="28">{lines_html(s.get("age", ""))}</div></div>')
        p = products[s["product_id"]]
        src = rel(Path(folder) / p["image"]["file"], out_dir)
        parts.append(f'<div class="prod" style="top:360px;height:590px"><div class="card"><img class="main"{trim_attr(p)} src="{esc(src)}" alt="" style="max-width:820px;max-height:546px"></div></div>')
        parts.append(f'<div class="block" data-where="reason" style="top:975px" data-maxh="215"><div data-f="why" class="b fit" data-max="46" data-min="34">{lines_html(s.get("why", ""))}</div>'
                     f'<div data-f="how" class="how fit" data-max="38" data-min="28">{lines_html(s.get("how", ""))}</div></div>')
    elif role == "lumebook":
        # "ספר של LumeBook", the catalogue cover flat in a white card where the other books show theirs (Yarin, 14 Oct
        # 2026), the one line under it. Carousels before 10 Oct 2026 22:00 keep the site's own 3D hero render.
        src = rel(Path(folder) / car["lumebook"]["image"]["file"], out_dir)
        flat = "/book_covers/" in car["lumebook"]["image"].get("image_url", "")
        if flat:
            parts.append(f'<div class="block" data-where="title" style="top:110px" data-maxh="220"><div data-f="headline" class="h fit" data-max="84" data-min="52">{lines_html(s["headline"])}</div></div>')
            parts.append(f'<div class="prod" style="top:360px;height:590px"><div class="card"><img class="main" src="{esc(src)}" alt="" style="max-width:820px;max-height:546px"></div></div>')
        else:
            parts.append(f'<div class="block" data-where="title" style="top:120px" data-maxh="170"><div data-f="headline" class="h fit" data-max="88" data-min="56">{lines_html(s["headline"])}</div></div>')
            parts.append(f'<div class="prod" style="top:280px;height:680px"><img class="main hero3d" src="{esc(src)}" alt="" style="max-width:720px;max-height:680px"></div>')
        parts.append(f'<div class="block" data-where="reason" style="top:{975 if flat else 985}px" data-maxh="{215 if flat else 205}"><div data-f="body" class="b fit" data-max="46" data-min="34">{lines_html(s.get("body", ""))}</div></div>')
    else:  # close: the collage of every suggestion under a purple layer, then the save and comment lines
        files = [p["image"]["file"] for p in car["products"]] + [car["lumebook"]["image"]["file"]]
        tiles = []
        big = len(files) > 12  # up to 17 suggestions in the combined carousel: a 4 x 5 grid so every one of them shows
        cols, count = (4, 20) if big else (3, 12)
        for k in range(count):  # 3 x 4: each row shifts by 2 so no image sits next to or under itself; 4 x 5: in order
            row, col = divmod(k, cols)
            src = rel(Path(folder) / files[(k if big else col + 2 * row) % len(files)], out_dir)
            tiles.append(f'<div class="t"><img class="bg" src="{esc(src)}" alt=""></div>')
        parts.append(f'<div class="collage{" big" if big else ""}">' + "".join(tiles) + '</div><div class="purple"></div>')
        lines = lib.lines_of(s["headline"])
        main = next((k for k, x in enumerate(lines) if x.rstrip().endswith("?")), 0)
        before, after = "\n".join(lines[:main]), "\n".join(lines[main + 1:])
        parts.append('<div class="block mid" data-where="middle" data-maxh="1100">'
                     + (f'<div data-f="headline" class="lead fit" data-max="44" data-min="34" style="margin-bottom:44px">{lines_html(before)}</div>' if before else "")
                     + f'<div data-f="headline" class="h fit wrap" data-max="{100 if bold else 84}" data-min="{66 if bold else 60}">{lines_html(lines[main], hl)}</div>'
                     + (f'<div data-f="headline" class="lead fit" data-max="44" data-min="34" style="margin-top:44px">{lines_html(after)}</div>' if after else "")
                     + (f'<div data-f="body" class="sub fit" data-max="44" data-min="34" style="margin-top:30px">{lines_html(s["body"])}</div>' if s.get("body", "").strip() else "")
                     + ICONS + '</div>')
    if n < len(car["slides"]):
        parts.append(ARROW)
    parts.append('</section>')
    return "".join(parts)


def fan_products(car):
    """The up to three covers fanned out on the hook. A mixed carousel shows both kinds: a game, a book, a game."""
    products = car["products"]
    if car.get("format") not in rl.MIXED_FORMATS:
        return products[:3]
    games = [p for p in products if p.get("kind") == "game"]
    books = [p for p in products if p.get("kind") == "book"]
    picked = [x for x in (games[:1] + books[:1] + games[1:2]) if x]
    return picked + [p for p in products if p not in picked][:3 - len(picked)]


def out_dir_for(folder, fmt):
    return Path(folder) / rl.OUT_DIRS.get(fmt, fmt)


def build_slides_html(car, out_dir, folder):
    css = SLIDE_CSS.replace("{heebo}", rel(FONTS / "Heebo-Black.ttf", out_dir)).replace("{heebo_bold}", rel(FONTS / "Heebo-Bold.ttf", out_dir)).replace("{assistant}", rel(FONTS / "Assistant-VariableFont_wght.ttf", out_dir))
    index, sections = 0, []
    for s in car["slides"]:
        if s["role"] == "recommendation":
            index += 1
        sections.append(slide_html(car, s, out_dir, folder, index))
    return ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{esc(car["date"])} {esc(car["format"])}</title><style>{css}</style></head>'
            f'<body dir="rtl" class="look-{"bold" if is_bold(car) else "classic"}{" look-plain" if is_plain(car) else ""}">{"".join(sections)}<pre id="report"></pre><script>{SLIDE_JS}</script></body></html>')


def render_problems(report):
    problems = []
    for s in report:
        if s["lang"] != "he" or s["htmlDir"] != "rtl" or s["direction"] != "rtl":
            problems.append(f"slide {s['n']}: page must be lang he dir rtl")
        for b in s["blocks"]:
            if b["direction"] != "rtl":
                problems.append(f"slide {s['n']}: «{b['text']}» renders {b['direction']}")
            if b["overflow"]:
                problems.append(f"slide {s['n']}: «{b['text']}» overflows its line")
        for t in s["texts"]:
            if t["fit"] != "ok":
                problems.append(f"slide {s['n']}: the {t['where']} text does not fit at the smallest size; shorten it")
        for im in s["imgs"]:
            if not im["loaded"]:
                problems.append(f"slide {s['n']}: image {im['src']} did not load")
                continue
            if im["aspect_error"] > 0.01:
                problems.append(f"slide {s['n']}: image is distorted ({im['aspect_error']:.1%} off its aspect ratio)")
            if s["role"] in ("recommendation", "lumebook"):
                if abs(im["center_dx"]) > 4:
                    problems.append(f"slide {s['n']}: product image is {im['center_dx']}px off centre")
                if im["share"] < 0.4:
                    problems.append(f"slide {s['n']}: product image is too small to read as the centre of the slide")
                tops = [t for t in s["texts"] if t["where"] in ("title", "top")]
                bottoms = [t for t in s["texts"] if t["where"] == "reason"]
                if any(t["bottom"] > im["top"] for t in tops) or any(t["top"] < im["bottom"] for t in bottoms):
                    problems.append(f"slide {s['n']}: text overlaps the product image")
    return problems


def render(car_path, png=True):
    """Write <format>/slides.html (+ PNGs, contact sheet, render-report.json). Returns (out_dir, problems)."""
    import compose_slides as cs  # Chrome helpers shared with the production renderer
    car_path = Path(car_path).resolve()
    car = lib.read_json(car_path)
    folder = car_path.parent
    out_dir = out_dir_for(folder, car["format"])
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "slides.html"
    html_path.write_text(build_slides_html(car, out_dir, folder), encoding="utf-8")
    for old in out_dir.glob("[0-9][0-9].png"):  # a carousel that got shorter must not keep its old extra slides
        if int(old.stem) > len(car["slides"]):
            old.unlink()
    if not png:
        return out_dir, []
    dom = cs.dump_dom(html_path.as_uri() + "?check=1", W, H)
    m = re.search(r'<pre id="report">(.*?)</pre>', dom, re.S)
    if not m or not m.group(1).strip():
        return out_dir, ["the slide check could not read the rendered page"]
    report = json.loads(htmlmod.unescape(m.group(1)))
    problems = render_problems(report)
    (out_dir / "render-report.json").write_text(json.dumps({"problems": problems, "slides": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for s in car["slides"]:
        out = out_dir / f"{s['number']:02d}.png"
        cs.screenshot(html_path.as_uri() + f"?s={s['number']}", out, W, H)
        if lib.png_size(out) != (W, H):
            problems.append(f"{out.name} is not {W}x{H}")
    cs.contact_sheet(out_dir, len(car["slides"]))
    return out_dir, problems


# ---------------------------------------------------------------------------
# Review pages: reco.html (and games.html, books.html on older nights) next to review.html, one tab bar across them
# ---------------------------------------------------------------------------

PAGES = {rl.MIXED: "reco.html", rl.MIXED2: "reco-2.html", "games": "games.html", "books": "books.html"}
TAB_LABELS = {"pack": "קרוסלות", rl.MIXED: "משחקים וספרים", rl.MIXED2: "משחקים וספרים 2", "games": "משחקים", "books": "ספרים"}

REVIEW_CSS = """
.rv-tabs{margin-bottom:calc(-1 * var(--sp-3))}
.rp-head{display:flex;flex-wrap:wrap;align-items:center;gap:var(--sp-2) var(--sp-3)}
.rp-head h1{margin-inline-end:auto}
.rp-slide{display:grid;gap:var(--sp-2);align-content:start}
.rp-live{position:relative;width:100%;aspect-ratio:4/5;overflow:hidden;border-radius:var(--r-md);border:1px solid var(--line);background:#fff}
.rp-live iframe{position:absolute;top:0;left:0;width:1080px;height:1350px;border:0;transform-origin:0 0}
.rp-hint{font-size:var(--fs-footnote);color:var(--text-3);margin:0}
.rp-slide img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:var(--r-md);border:1px solid var(--line);display:block;background:#fff}
.rp-off{font-size:var(--fs-footnote);color:var(--text-3)}
body.editing .rp-off{display:none}
.rp-copy{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr));gap:var(--sp-3)}
.rp-copy .rs{background:var(--surface-2);border-radius:var(--r-md);padding:var(--sp-3);display:grid;gap:var(--sp-1);align-content:start}
.rp-copy .lbl{font-size:var(--fs-caption);color:var(--text-3)}
.rp-copy .val{white-space:pre-line;font-size:var(--fs-callout);line-height:1.45}
.rp-hl{display:flex;align-items:center;gap:var(--sp-2);font-size:var(--fs-caption);color:var(--text-3);margin-top:var(--sp-1)}
.rp-hl .hl{background:var(--tint-solid);color:var(--text-on-tint);border-radius:var(--r-xs);padding:1px 8px;font-weight:700;min-width:2em}
.rp-copy .val.t{font-weight:700}
.rp-caption{white-space:pre-line;font-size:var(--fs-callout);background:var(--surface-2);border-radius:var(--r-md);padding:var(--sp-3);margin-top:var(--sp-3)}
details.prod{border-top:1px solid var(--line)}
details.prod:first-child{border-top:0}
details.prod>summary{cursor:pointer;list-style:none;display:flex;flex-wrap:wrap;align-items:center;gap:var(--sp-2);padding:var(--sp-3) 0}
details.prod>summary::-webkit-details-marker{display:none}
details.prod>summary img{width:2.75rem;height:2.75rem;object-fit:contain;border-radius:var(--r-xs);background:#fff;border:1px solid var(--line)}
details.prod>summary b{margin-inline-end:auto}
details.prod .lb-kv{padding-bottom:var(--sp-4)}
.rp-list{margin:0;padding-inline-start:1.1rem;display:grid;gap:var(--sp-1);font-size:var(--fs-footnote)}
.rp-q{color:var(--text-3)}
.rp-flags li.e{color:var(--danger)}
.rp-flags li.w{color:var(--text-2)}
.rp-flags li{direction:ltr;text-align:left}
body.editing [data-reco]{outline:1.5px dashed var(--focus);outline-offset:3px;border-radius:var(--r-xs);cursor:text;min-height:1.2em}
body.editing [data-reco]:focus{outline:2px solid var(--tint);background:var(--tint-soft)}
.rp-save{display:none;align-items:center;gap:var(--sp-3)}
body.editing .rp-save{display:flex}
.rp-copy.rp-slides{grid-template-columns:repeat(auto-fill,minmax(min(100%,15rem),1fr));gap:var(--sp-4)}
/* Phones: the slides sit in one row that scrolls sideways (up to 20 in the combined carousel), each card most of the width */
@media (max-width:640px){
.rp-copy.rp-slides{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:82%;overflow-x:auto;overscroll-behavior-x:contain;scroll-snap-type:x mandatory;padding-bottom:var(--sp-2);-webkit-overflow-scrolling:touch}
.rp-copy.rp-slides>.rp-slide{scroll-snap-align:start}
}
.rp-count{font-size:var(--fs-footnote);color:var(--text-3)}
"""

REVIEW_JS = r"""
(function () {
  const RECO = {orig: new Map()};
  const txt = el => el.innerText.replace(/ /g, ' ').split('\n').map(x => x.trim()).filter(Boolean).join('\n');
  const fmt = document.body.dataset.format;
  const msg = t => { const m = document.querySelector('.rp-save .savemsg'); if (m) m.textContent = t; };
  async function save() {
    const edits = [];
    RECO.orig.forEach((o, el) => { if (txt(el) !== o) edits.push({slide: el.dataset.slide ? Number(el.dataset.slide) : null, field: el.dataset.field, value: txt(el)}); });
    if (!edits.length) { msg('אין שינויים'); return; }
    msg('שומר...');
    try {
      const r = await fetch('/api/save-reco', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({date: document.body.dataset.date, format: fmt, edits})});
      sessionStorage.setItem('lumebook-reco-result', JSON.stringify(await r.json()));
    } catch (e) { msg('השמירה נכשלה'); return; }
    RECO.orig.clear(); location.reload();
  }
  async function init() {
    try { const r = await fetch('/api/ping', {cache: 'no-store'}); if (!r.ok) return; } catch (e) { return; }
    document.body.classList.add('editing');
    document.querySelectorAll('[data-reco]').forEach(el => { try { el.contentEditable = 'plaintext-only'; } catch (e) { el.contentEditable = 'true'; }
      if (el.contentEditable !== 'plaintext-only') el.contentEditable = 'true'; RECO.orig.set(el, txt(el)); });
    document.querySelector('.rp-save button').onclick = save;
    // The slide itself is the editing surface: the live slide replaces its picture, and typing on it fills the field below
    document.querySelectorAll('.rp-slide[data-n]').forEach(card => { const a = card.querySelector('a'); if (!a) return;
      const box = document.createElement('div'); box.className = 'rp-live'; const f = document.createElement('iframe');
      f.src = (document.body.dataset.dir || fmt) + '/slides.html?s=' + card.dataset.n + '&edit=1'; f.title = 'שקופית ' + card.dataset.n; box.appendChild(f); a.replaceWith(box);
      const fit = () => { f.style.transform = 'scale(' + (box.clientWidth / 1080) + ')'; }; fit(); new ResizeObserver(fit).observe(box); });
    window.addEventListener('message', e => { const d = e.data; if (!d || d.lumebookEdit !== 1) return; if (d.save) { save(); return; }
      const el = document.querySelector('[data-reco][data-slide="' + d.slide + '"][data-field="' + d.field + '"]'); if (!el) return;
      el.textContent = d.value; msg('יש שינויים שלא נשמרו'); });
    const hint = document.querySelector('.rp-off'); if (hint) { hint.className = 'rp-hint'; hint.textContent = 'לוחצים על הטקסט בשקופית ומקלידים · שמירה ב-⌘S'; }
    document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); save(); } });
    window.addEventListener('beforeunload', e => { for (const [el, o] of RECO.orig) if (txt(el) !== o) { e.preventDefault(); e.returnValue = ''; return; } });
    let stored = null; try { stored = sessionStorage.getItem('lumebook-reco-result'); sessionStorage.removeItem('lumebook-reco-result'); } catch (e) {}
    if (stored) { const res = JSON.parse(stored); msg(res.error ? 'השמירה נכשלה: ' + res.error : (res.valid ? 'נשמר' : 'נשמר · ' + res.errors.length + ' לתיקון, ברשימת הבדיקות'));
      if (!res.valid) { const d = document.getElementById('checks'); if (d) d.open = true; } }
  }
  init();
})();
"""


def _link(url, text):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'


def _field(fmt, n, field, text, cls="val"):
    slide = f' data-slide="{n}"' if n else ""
    return f'<div class="{cls}" data-reco="{fmt}"{slide} data-field="{field}">{esc(text)}</div>'


def _short(text, n=90):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[:n - 1].rstrip() + "…"


def tabs_html(folder, active):
    """The tab bar shared by review.html and the recommendation pages (reco.html; games.html and books.html on older nights)."""
    folder = Path(folder)
    # The recommendation carousel is always one tab away (Yarin, 11 Oct 2026): when this date has none (a batch on a topic,
    # for example), the tab opens the newest date that does, and says which date that is. The older games and books tabs
    # show only on the nights that have them. A row of dates follows.
    dates = sorted((d.name for d in folder.parent.iterdir() if d.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", d.name)), reverse=True)
    short = lambda d: f"{int(d[8:10])}.{int(d[5:7])}"
    items = [("pack", "review.html", TAB_LABELS["pack"])]
    has_legacy = any(rl.carousel_path(folder, f).exists() for f in rl.LEGACY_FORMATS)
    for f in rl.FORMATS:
        if rl.carousel_path(folder, f).exists():
            items.append((f, PAGES[f], TAB_LABELS[f]))
            continue
        if f in rl.LEGACY_FORMATS or f == rl.MIXED2 or (f == rl.MIXED and has_legacy):
            continue
        other = next((d for d in dates if d != folder.name and rl.carousel_path(folder.parent / d, f).exists()), None)
        if other:
            items.append((f, f"../{other}/{PAGES[f]}", f"{TAB_LABELS[f]} · {short(other)}"))
    selected = ' aria-selected="true"'   # not inside the f-string: a backslash there needs Python 3.12 (the cloud box has 3.11)
    links = "".join(f'<a href="{href}"{selected if key == active else ""}>{esc(label)}</a>' for key, href, label in items)
    return f'<nav class="lb-tabs rv-tabs" aria-label="עמודים">{links}{days_html(folder)}</nav>'


def days_html(folder):
    """The row of dates in the tab bar. review_server.py redraws it on every page load, so a night brought down from
    the cloud shows on the older pages too."""
    folder = Path(folder)
    dates = sorted((d.name for d in folder.parent.iterdir() if d.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", d.name)), reverse=True)
    short = lambda d: f"{int(d[8:10])}.{int(d[5:7])}"
    days = "".join(f'<a href="../{d}/review.html"{" aria-current=\"page\"" if d == folder.name else ""}>{short(d)}</a>'
                   for d in dates if (folder.parent / d / "review.html").exists() or d == folder.name)
    import batch  # a pack of a weekly batch links back to the pool page (served by review_server.py)
    plan, slot = batch.plan_for_date(folder.name)
    pool = f'<a href="/pool/{plan["id"]}">מאגר השבוע · {slot["n"]}</a>' if plan else ""
    return f'<span class="rv-days" aria-label="תאריכים">{pool}{days}</span>'


def _status_chips(st, car):
    chips = [f'<span class="lb-chip">{esc(car["stage"]["age_label_he"])} · {esc(rl.SKILLS.get(car["stage"]["skill"], {}).get("he", car["stage"]["skill"]))}</span>']
    chips.append('<span class="lb-chip success">תקין</span>' if st["valid"] else f'<span class="lb-chip danger">{st["errors"]} לתיקון</span>')
    if st["valid"] and not st["publish_ready"]:
        chips.append('<span class="lb-chip warning">לא לפרסום עדיין</span>')
    return "".join(chips)


def _product(p, s):
    img, oa = p["image"], p["official_age"]
    kind = rl.KIND_HE.get(p.get("kind"), "")
    maker = " · ".join(x for x in (p.get("author"), p.get("publisher"), p.get("manufacturer")) if x)
    pop_ok = p["popularity_label"] == "popular_in_israel"
    rights_ok = img["rights_status"] in rl.PUBLISHABLE_RIGHTS
    avail = "".join(f'<li>{_link(a["url"], a["retailer"])} · {esc({"in_stock": "במלאי", "listed": "למכירה", "out_of_stock": "אזל", "discontinued": "הופסק"}[a["status"]])}</li>' for a in p["availability"])
    sig = "".join(f'<li>{_link(x["url"], rl.SIGNAL_HE.get(x["type"], x["type"]))}{" · " + str(x["rank"]) + " מתוך " + str(x["out_of"]) if x.get("rank") else ""} <span class="rp-q">«{esc(_short(x["quote"], 70))}»</span></li>' for x in p["popularity_signals"]) or "<li>אין</li>"
    return (f'<details class="prod"><summary><img src="{esc(img["file"])}" alt=""><b>{esc(p["title_he"])}</b>'
            f'<span class="lb-chip {"success" if pop_ok else "warning"}">{"פופולרי בישראל" if pop_ok else "זמין בלבד"}</span>'
            f'<span class="lb-chip {"success" if rights_ok else "warning"}">{"זכויות תמונה מאושרות" if rights_ok else "זכויות תמונה לא מאומתות"}</span></summary>'
            '<dl class="lb-kv">'
            + (f'<dt>סוג</dt><dd>{esc(kind)}</dd>' if kind else "") +
            f'<dt>יוצר</dt><dd>{esc(maker)}</dd>'
            f'<dt>גיל</dt><dd>{esc(s.get("age", ""))} · רשמי {_link(oa["url"], oa["text"])}</dd>'
            f'<dt>פופולריות</dt><dd><ul class="rp-list">{sig}</ul></dd>'
            f'<dt>זמינות</dt><dd><ul class="rp-list">{avail}</ul></dd>'
            f'<dt>תמונה</dt><dd>{_link(img["page_url"], rl.host(img["page_url"]))} · {img["width"]}x{img["height"]}</dd>'
            f'<dt>מגבלות</dt><dd dir="ltr" style="text-align:left">{esc(_short(p["limitations"], 160))}</dd>'
            '</dl></details>')


def reco_page(folder, fmt, history=None):
    """reco.html (or games.html, books.html on older nights): header, the slides, and everything else in dropdowns."""
    import create_review  # the design system and the shared page chrome styles
    design = create_review.design
    folder = Path(folder)
    car = lib.read_json(rl.carousel_path(folder, fmt))
    issues = rl.carousel_issues(car, folder, history=history if history is not None else rl.load_history())
    st = rl.status(issues, car)
    out_dir = out_dir_for(folder, fmt)
    sub = rl.OUT_DIRS.get(fmt, fmt)
    # one card per slide: the rendered slide, and under it its text, editable in place when served by review_server.py
    cards = []
    for s in car["slides"]:
        n = s["number"]
        png = out_dir / f"{n:02d}.png"
        img = ""
        if png.exists():
            src = f'{sub}/{n:02d}.png?v={int(png.stat().st_mtime)}'
            img = f'<a href="{src}" target="_blank" rel="noopener"><img src="{src}" alt="שקופית {n}"></a>'
        cell = [_field(fmt, n, "headline", s["headline"], "val t")]
        if s["role"] == "recommendation":
            cell += [_field(fmt, n, "age", s.get("age", "")), _field(fmt, n, "why", s.get("why", "")), _field(fmt, n, "how", s.get("how", ""))]
        elif s["role"] != "close" or s.get("body"):
            cell.append(_field(fmt, n, "body", s.get("body", "")))
        if s["role"] in ("hook", "frame", "close") and (s.get("highlight") or rl.bold_applies(car)):
            cell.append(f'<div class="rp-hl"><span>הדגשה</span>{_field(fmt, n, "highlight", s.get("highlight", ""), "val hl")}</div>')
        cards.append(f'<div class="rp-slide" data-n="{n}">{img}<div class="rs" lang="he" dir="rtl">' + "".join(cell) + '</div></div>')
    recs = {s.get("product_id"): s for s in car["slides"] if s["role"] == "recommendation"}
    products = "".join(_product(p, recs.get(p["id"], {})) for p in sorted(car["products"], key=lambda p: recs.get(p["id"], {}).get("number", 9)))
    dev = "".join(f'<li>{_link(s["url"], s["publisher"])} · {esc(_short(s["title"], 80))}</li>' for s in car["dev_sources"])
    claims = "".join(f'<tr><td>{c["slide"]}</td><td>{esc(c["wording_he"])}</td><td dir="ltr" style="text-align:left">{esc(", ".join(c["source_ids"]) or "ניסוח שלנו")}</td></tr>' for c in car["claims"])
    lb = car["lumebook"]
    facts = "".join(f'<li>«{esc(f["quote"])}» · {_link(f["url"], rl.host(f["url"]))}</li>' for f in car["product_facts"])
    errs = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level != "ERROR"]
    flag_items = "".join(f'<li class="{"e" if i.level == "ERROR" else "w"}">{esc(str(i))}</li>' for i in errs + warns)
    report = out_dir / "render-report.json"
    render_probs = lib.read_json(report).get("problems", []) if report.exists() else []
    flag_items += "".join(f'<li class="e">{esc(p)}</li>' for p in render_probs)
    n_checks = len(errs) + len(render_probs)
    body = [
        f'<nav class="lb-tabs rv-tabs" aria-label="עמודים"></nav>',
        f'<header class="rp-head"><h1 data-reco="{fmt}" data-field="title">{esc(car["title"])}</h1>{_status_chips(st, car)}'
        f'<span class="rp-count">{len(car["slides"])} שקופיות{_kind_counts(car)}</span></header>',
        '<div class="rp-save"><button class="lb-btn sm" type="button">שמירה (⌘S)</button><span class="savemsg edit-note"></span></div>',
        '<p class="rp-off">לעריכה: python3 carousel/carousel-pipeline/scripts/review_server.py</p>',
        '<div class="rp-slides rp-copy">' + "".join(cards) + '</div>',
        f'<div class="rp-caption" dir="rtl">{_field(fmt, None, "caption", car["caption"], "")}</div>',
        (f'<details class="more"><summary>ניסוחי פתיח שנשקלו (מהשקט לחזק)</summary><div class="inner"><ul class="rp-list">'
         + "".join(f'<li>{esc(a).replace(chr(10), " / ")}</li>' for a in car["hook_alternatives"]) + '</ul></div></details>') if car.get("hook_alternatives") else "",
        '<div>',
        f'<details class="more"><summary>המוצרים</summary><div class="inner">{products}</div></details>',
        f'<details class="more"><summary>מקורות</summary><div class="inner"><ul class="rp-list">{dev}</ul>'
        f'<table style="margin-top:var(--sp-3)"><thead><tr><th>שקופית</th><th>טענה</th><th>מקור</th></tr></thead><tbody>{claims}</tbody></table></div></details>',
        f'<details class="more"><summary>לומבוק</summary><div class="inner"><dl class="lb-kv"><dt>תמונה</dt><dd>{_link(lb["image"]["page_url"], lb.get("catalogue_book") or "lumebook.com")}</dd>'
        f'<dt>עובדות מהאתר</dt><dd><ul class="rp-list">{facts}</ul></dd><dt>החיבור</dt><dd dir="auto">{esc(lb["connection"])}</dd></dl></div></details>',
        f'<details class="more" id="checks"{" open" if n_checks else ""}><summary>בדיקות{" · " + str(n_checks) + " לתיקון" if n_checks else ""}{" · " + str(len(warns)) + " הערות" if warns else ""}</summary>'
        f'<div class="inner"><ul class="rp-list rp-flags">{flag_items or "<li>הכול תקין</li>"}</ul></div></details>',
        '</div>',
    ]
    page = "\n".join(body).replace('<nav class="lb-tabs rv-tabs" aria-label="עמודים"></nav>', tabs_html(folder, fmt), 1)
    return ('<!doctype html>\n<html lang="he" dir="rtl">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(TAB_LABELS[fmt])} · {esc(car["date"])}</title>{design.head()}'
            f'<style>body{{direction:rtl;text-align:right}}{create_review.PAGE_CSS}{REVIEW_CSS}</style></head>\n'
            f'<body dir="rtl" data-date="{esc(car["date"])}" data-format="{fmt}" data-dir="{esc(sub)}">'
            '<header class="lb-topbar rv-topbar"><div class="lb-topbar-in">'
            f'<img class="rv-logo" src="{design.logo_data_uri()}" alt="LumeBook" width="28" height="28"><b class="rv-name">{esc(car["date"])}</b>'
            f'<span class="lb-spacer"></span></div></header>'
            f'<main class="lb-page">{page}</main><script>{REVIEW_JS}</script></body></html>')


def _kind_counts(car):
    if car.get("format") not in rl.MIXED_FORMATS:
        return ""
    kinds = [p.get("kind") for p in car["products"]]
    return f' · {kinds.count("game")} משחקים · {kinds.count("book")} ספרים'


def write_pages(folder, history=None):
    """Write reco.html (and games.html, books.html on older nights) for the carousels present. Returns their paths."""
    folder = Path(folder)
    out = []
    for fmt in rl.FORMATS:
        if rl.carousel_path(folder, fmt).exists():
            page = folder / PAGES[fmt]
            page.write_text(reco_page(folder, fmt, history), encoding="utf-8")
            out.append(page)
    return out


def inject_review(html, folder, history=None):
    """Called by create_review.write_review: put the tab bar on review.html and (re)write the recommendation pages."""
    if rl.present(folder):
        write_pages(folder, history)
    tabs = tabs_html(folder, "pack")
    for marker in ('<div class="lb-page">', '<div class="wrap">'):
        if marker in html:
            return html.replace(marker, marker + tabs, 1)
    return re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + tabs, html, count=1)


def standalone_page(folder, date):
    """review.html when the night has a recommendation carousel but no kid and expert pack."""
    import create_review
    design = create_review.design
    return ('<!doctype html>\n<html lang="he" dir="rtl">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(date)}</title>{design.head()}<style>body{{direction:rtl;text-align:right}}{create_review.PAGE_CSS}{REVIEW_CSS}</style></head>\n'
            f'<body dir="rtl" data-date="{esc(date)}"><main class="lb-page">{tabs_html(folder, "pack")}<p class="edit-note">אין קרוסלות ילד ומומחה הלילה</p></main></body></html>')


def write_review(folder):
    """Rebuild review.html (with the tab bar) and the recommendation pages."""
    import create_review
    folder = Path(folder)
    pack = folder / "pack.json"
    if pack.exists():
        return create_review.write_review(pack)[0]
    page = folder / "review.html"
    page.write_text(standalone_page(folder, folder.name), encoding="utf-8")
    write_pages(folder)
    return page


# ---------------------------------------------------------------------------
# Edits from the review page
# ---------------------------------------------------------------------------

EDIT_FIELDS = {"headline", "body", "highlight", "age", "why", "how", "caption", "title"}


def apply_edits(car, edits):
    changes = []
    for e in edits:
        field = e.get("field")
        if field not in EDIT_FIELDS:
            raise ValueError(f"unknown field {field}")
        value = "\n".join(line.strip() for line in str(e.get("value", "")).replace(" ", " ").splitlines() if line.strip())
        if field in ("caption", "title"):
            if car[field] != value:
                changes.append({"field": field, "slide": None, "role": None, "before": car[field], "after": value})
                car[field] = value
            continue
        n = e.get("slide")
        if not isinstance(n, int) or not 1 <= n <= len(car["slides"]):
            raise ValueError(f"bad slide number {n}")
        s = car["slides"][n - 1]
        if field in ("age", "why", "how") and s["role"] != "recommendation":
            raise ValueError(f"slide {n} has no {field}")
        if field == "body" and s["role"] == "recommendation":
            raise ValueError("suggestion slides use why and how")
        before = s.get(field, "")
        if before != value:
            s[field] = value
            changes.append({"field": field, "slide": n, "role": s["role"], "before": before, "after": value})
    return changes


def save(date, fmt, edits, drafts=lib.DRAFTS, history_path=rl.HISTORY, edits_log=lib.VOICE_EDITS, render_png=True):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(date)) or fmt not in rl.FORMATS:
        return {"error": "bad date or format"}
    folder = Path(drafts) / date
    path = rl.carousel_path(folder, fmt)
    if not path.exists():
        return {"error": f"no {fmt} carousel for {date}"}
    car = lib.read_json(path)
    try:
        changes = apply_edits(car, edits)
    except ValueError as exc:
        return {"error": str(exc)}
    if not changes:
        return {"changed": 0, "errors": [], "warnings": []}
    versions = folder / "versions"
    versions.mkdir(exist_ok=True)
    k = 1
    while (versions / f"v{k}").exists():
        k += 1
    (versions / f"v{k}").mkdir()
    shutil.copy2(path, versions / f"v{k}" / path.name)
    lib.write_json(path, car)
    records = [{"at": lib.now_local().isoformat(timespec="seconds"), "pack_date": date, "direction": fmt, "option": fmt,
                "field": c["field"], "slide": c["slide"], "role": c["role"], "child_gender": None, "addressee": car.get("addressee"),
                "kind": lib.edit_kind(c["before"], c["after"]), "before": c["before"], "after": c["after"]}
               for c in changes if c["field"] not in ("title", "highlight")]
    logged = lib.log_voice_edits(records, edits_log)
    history = rl.load_history(history_path)
    issues = rl.carousel_issues(car, folder, history=history)
    errors = [{**i.as_dict(), "flag": getattr(i, "flag", "")} for i in issues if i.level == "ERROR"]
    warnings = [{**i.as_dict(), "flag": getattr(i, "flag", "")} for i in issues if i.level == "WARN"]
    problems = []
    if render_png:
        _, problems = render(path)
    write_review(folder)
    if not errors:
        rl.record_history(car, history_path)
    return {"changed": len(changes), "valid": not errors, "errors": errors, "warnings": warnings, "render_problems": problems,
            "backup": f"versions/v{k}", "voice_logged": logged}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carousel")
    ap.add_argument("--no-png", action="store_true", help="write slides.html only")
    args = ap.parse_args()
    out_dir, problems = render(args.carousel, png=not args.no_png)
    page = write_review(Path(args.carousel).resolve().parent)
    print(json.dumps({"out_dir": str(out_dir), "review": str(page), "render_problems": problems}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()
