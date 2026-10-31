#!/usr/bin/env python3
"""Overlay the frozen Hebrew copy on the approved images and export the final carousel.

    python3 carousel/carousel-pipeline/scripts/compose_slides.py RUN_DIR
    python3 carousel/carousel-pipeline/scripts/compose_slides.py RUN_DIR --placeholders      # no paid images needed
    python3 carousel/carousel-pipeline/scripts/compose_slides.py RUN_DIR --slides 3 5         # re-export only some slides

The image model never renders Hebrew. Every word is HTML text set in Heebo and Assistant
(SIL Open Font License, in carousel/carousel-pipeline/assets/fonts), right to left.

Writes to RUN_DIR/final/ (or RUN_DIR/final-placeholders/ with --placeholders):
    slides.html          editable source, one <section class="slide" data-n="N"> per slide
    01.png ... NN.png    exactly 1080 x 1350, one per slide (7, 10, or 9 to 12 in the story format)
    contact-sheet.png    numbered overview
    rtl-check.png        every line that mixes Hebrew with digits or Latin, large, for a visual check
    rtl-report.json      computed direction and alignment of every text block, plus overflow
    caption.txt, sources.md, alt-text.txt
    DATE-OPTION.zip      slides, caption, sources, alt text, contact sheet, generation log

Carousels do not name the brand: no logo and no product card by default. --brand-mark adds the logo,
--preview-card adds real-assets/preview.png as a card on the last slide (only if it shows no brand name).

Story packs (copy_style "story", story-format.md, 29 Oct 2026) get the story look: a picture per slide
(generated-assets/slide-NN.png, the cover slide-01.png), Varela Round on an ink veil, gold tags and labels, a cream card for
"> " lines, the letter structure on a cream sheet. --brand-mark and --preview-card do not apply to it.

Needs Google Chrome or Chromium (carousel_lib.find_chrome). Standard library only.
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
from carousel_lib import esc  # noqa: E402

W, H = 1080, 1350
FONTS = lib.PIPELINE / "assets" / "fonts"
LOGO = lib.PIPELINE / "assets" / "brand" / "logo_square.png"

CSS = """
@font-face{font-family:"Heebo";src:url("{heebo}") format("truetype");font-weight:900;font-display:block}
@font-face{font-family:"Assistant";src:url("{assistant}") format("truetype");font-weight:200 800;font-display:block}
*{box-sizing:border-box;margin:0;padding:0}
html,body{direction:rtl}
body{background:#d9d2c6;text-align:center}
body.single .slide:not(.on){display:none}
/* The layout of the approved fal trial carousel (media/projects/2026-10-06-fal-carousel-trial/source/flare_carousel.py, 7 Oct 2026):
   centred Heebo Black straight on the picture's plain wall, a soft veil, no boxes. The picture always fills the slide
   exactly as generated (Yarin, 24 Oct 2026: "i dont want you to distort the images anymore"); until then it was pushed
   down under the text and the gap filled by stretching its top rows. The copy is fitted to the plain wall instead (fitTop). */
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:#F3EADC;--ink:#1D1039;--veil:243,234,220;direction:rtl;text-align:center}
.slide.dark{--ink:#F8F0E1;--veil:11,5,24;background:#0B0518}
.art{position:absolute;left:0;top:0;width:1080px;height:1350px;object-fit:cover}
.veil{position:absolute;inset:0;pointer-events:none}
.veil.top{background:linear-gradient(180deg,rgba(var(--veil),.88) 0,rgba(var(--veil),.7) 20%,rgba(var(--veil),0) 40%)}
.veil.bottom{background:linear-gradient(0deg,rgba(var(--veil),.88) 0,rgba(var(--veil),.7) 20%,rgba(var(--veil),0) 40%)}
.copy{position:absolute;left:90px;right:90px;direction:rtl;text-align:center;color:var(--ink)}
.copy.top{top:150px}
.copy.bottom{bottom:180px}
.h{font-family:"Heebo",sans-serif;font-weight:900;line-height:1.08;letter-spacing:-.01em}
.b{font-family:"Heebo",sans-serif;font-weight:900;line-height:1.15;margin-top:22px;opacity:.82}
.ln{display:block;white-space:nowrap}
.mark{position:absolute;top:44px;left:48px;width:60px;height:60px;border-radius:14px}
/* Bottom centre (Yarin, 19 Oct 2026: "i want the arrow in the middle"); the art is pushed down only as far as the text needs, so it covers less */
.arrow{position:absolute;left:50%;transform:translateX(-50%);bottom:56px;width:88px;height:88px;border-radius:50%;background:#F8F0E1;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(11,5,24,.28)}
.arrow svg{width:44px;height:44px}.arrow path{fill:none;stroke:#1D1039;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}
.ai{position:absolute;right:48px;bottom:64px;font-family:"Assistant",sans-serif;font-weight:700;font-size:24px;color:#1D1039;background:rgba(248,240,225,.86);border-radius:999px;padding:6px 16px;direction:rtl}
.card{position:absolute;left:72px;bottom:150px;width:400px;height:500px;transform:rotate(-2deg);border-radius:18px;overflow:hidden;background:#fff;border:10px solid #fff;box-shadow:0 18px 40px rgba(11,5,24,.28)}
.card img{width:100%;height:100%;object-fit:cover;border-radius:8px}
pre#rtl-report{display:none}
/* The bold look (Carousel Machine, 10 Oct 2026): type first. Much larger headline on short lines, one highlighted
   phrase per slide in the pillar colour, body in Rubik for a clear step down, spoken sentences as bubbles,
   the comment line of the last slide as a button. --look classic keeps the layout above untouched. */
@font-face{font-family:"Rubik";src:url("{rubik}") format("truetype");font-weight:300 900;font-display:block}
.pillar-kid{--hl:#5B2BD6;--hl-ink:#FFF7E8}
.pillar-expert{--hl:#F6C445;--hl-ink:#1D1039}
.look-bold .copy{left:64px;right:64px}
.look-bold .copy.top{top:72px}
.look-bold .veil.top{background:linear-gradient(180deg,rgba(var(--veil),.94) 0,rgba(var(--veil),.8) 24%,rgba(var(--veil),0) 48%)}
.look-bold .h{line-height:1.13;letter-spacing:-.02em;text-shadow:0 0 26px rgba(var(--veil),.95),0 0 8px rgba(var(--veil),.85)}
.look-bold .b{font-family:"Rubik",sans-serif;font-weight:600;line-height:1.26;margin-top:28px;opacity:1;text-shadow:0 0 18px rgba(var(--veil),.95),0 0 6px rgba(var(--veil),.8)}
.look-bold .hl{display:inline-block;background:var(--hl);color:var(--hl-ink);padding:0 .2em .05em;border-radius:.15em;transform:rotate(-1.6deg);text-shadow:none;box-shadow:0 10px 24px rgba(11,5,24,.24)}
.look-bold .ln:has(.hl){margin:.07em 0}
.look-bold .q{display:inline-block;background:#FFFDF8;color:#1D1039;border-radius:.5em;padding:.04em .42em .08em;margin:.1em 0;text-shadow:none;box-shadow:0 6px 16px rgba(11,5,24,.2)}
.look-bold .btn{display:inline-block;background:#F6C445;color:#1D1039;border-radius:.4em;padding:.06em .5em .1em;margin-bottom:.16em;font-weight:800;text-shadow:none;box-shadow:0 10px 26px rgba(0,0,0,.4)}
/* Instagram's own save and send glyphs beside the save and share CTA (Yarin, 24 Oct 2026: "add default save and send icons") */
.ic{display:inline-block;width:.86em;height:.86em;vertical-align:-.13em;margin-inline-end:.3em;fill:none;stroke:currentColor;stroke-width:2.3;stroke-linecap:round;stroke-linejoin:round}
.look-bold .arrow{width:96px;height:96px;bottom:52px;background:var(--hl)}
.look-bold .arrow path{stroke:var(--hl-ink);stroke-width:6}
/* The clean look (Yarin, 14 Oct 2026: "from now on design the text of the carousels like these except the cta
   slide"): every slide but the last is plain centred type on the wall. Headline in Heebo Black, solid dark plum;
   the body a step down in a lighter plum; no highlight block, no bubbles, no veil or glow; a cream round arrow.
   The last slide keeps the bold look exactly (it also carries .look-bold). */
.look-clean .slide:not(.cta) .veil{display:none}
.look-clean .slide:not(.cta) .h{color:var(--ink);line-height:1.1;text-shadow:none}
.look-clean .slide:not(.cta) .b{font-family:"Heebo",sans-serif;font-weight:900;color:#43345F;line-height:1.22;margin-top:30px;text-shadow:none}
.look-clean .slide.dark:not(.cta) .b{color:var(--ink);opacity:.86}
.look-clean .slide:not(.cta) .arrow{width:88px;height:88px;bottom:56px;background:#F8F0E1}
.look-clean .slide:not(.cta) .arrow path{stroke:#1D1039;stroke-width:5}
/* Only when the contrast check (legible() below) still fails after darker ink and light-on-dark: a soft panel of the
   wall colour behind the copy (24 Oct 2026) */
.copy.panel{isolation:isolate}
.copy.panel::before{content:"";position:absolute;inset:-28px -36px;border-radius:44px;background:rgba(var(--veil),.84);z-index:-1}
"""

JS = """
const q = new URLSearchParams(location.search);
const one = q.get('s');
// layout notes per slide land in data-push / data-clear and in the check report
if (one) { document.body.classList.add('single'); document.querySelector('.slide[data-n="' + one + '"]').classList.add('on'); }
function fitSlide(s) {
  // Headline and body are fitted separately so a long headline never shrinks the body.
  // Floors: headline 56px, body 40px (Heebo Black is wider than the old Assistant body). Below that
  // the slide is reported as overflow and the copy has to be shortened instead of printed too small.
  const c = s.querySelector('.copy'); const h = c.querySelector('.h'); const b = c.querySelector('.b');
  const maxH = Number(c.dataset.maxh);
  const HMIN = Number(c.dataset.hmin || 56), BMIN = Number(c.dataset.bmin || 40);
  const wide = el => [...el.querySelectorAll('.ln')].some(l => l.scrollWidth > l.clientWidth + 1);
  let hs = Number(h.dataset.max); h.style.fontSize = hs + 'px';
  while (wide(h) && hs > HMIN) { hs -= 2; h.style.fontSize = hs + 'px'; }
  let bs = 0;
  if (b) { bs = Number(b.dataset.max); b.style.fontSize = bs + 'px'; while (wide(b) && bs > BMIN) { bs -= 1; b.style.fontSize = bs + 'px'; } }
  let guard = 0;
  while (c.scrollHeight > maxH + 1 && guard < 120) {
    const before = hs + bs;
    if (hs > HMIN) { hs -= 2; h.style.fontSize = hs + 'px'; }
    if (b && bs > BMIN) { bs -= 1; b.style.fontSize = bs + 'px'; }
    if (hs + bs === before) break;
    guard++;
  }
  const ok = !wide(h) && !(b && wide(b)) && c.scrollHeight <= maxH + 1;
  c.dataset.fit = ok ? 'ok' : 'overflow'; c.dataset.headSize = hs; c.dataset.bodySize = bs;
}
// Pixels of the picture as it is shown (object-fit: cover onto 1080x1350), at quarter resolution:
// downscaling averages 4x4 blocks, which stands in for the trial's 3px blur.
function pixels(img) {
  const w = 270, h = 338, cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const g = cv.getContext('2d'); const sc = Math.max(1080 / img.naturalWidth, 1350 / img.naturalHeight);
  const dw = img.naturalWidth * sc / 4, dh = img.naturalHeight * sc / 4;
  g.drawImage(img, (w - dw) / 2, (h - dh) / 2, dw, dh);
  return { w, h, d: g.getImageData(0, 0, w, h).data };
}
function topLuma(px, rows) {
  let sum = 0, n = 0;
  for (let y = 0; y < rows; y++) for (let x = 0; x < px.w; x++) { const i = (y * px.w + x) * 4; sum += .2126 * px.d[i] + .7152 * px.d[i + 1] + .0722 * px.d[i + 2]; n++; }
  return sum / n;
}
// First row (slide px) where the picture stops being plain wall or sky. Each row is compared with a smooth
// quadratic fitted across it (walls have soft left-right shading); a row where more than 2% of pixels
// deviate strongly from that fit is where hair, faces or furniture begin. Same test as the trial's subject_top.
function subjectTop(px, left, right) {
  const x0 = Math.max(10, Math.floor((left ?? 40) / 4)), x1 = Math.min(px.w - 10, Math.ceil((right ?? px.w * 4 - 40) / 4)), m = x1 - x0;
  const xs = Array.from({ length: m }, (_, k) => -1 + 2 * k / (m - 1));
  let S = [[0,0,0],[0,0,0],[0,0,0]];
  xs.forEach(x => { const v = [1, x, x * x]; for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) S[a][b] += v[a] * v[b]; });
  const inv = inv3(S);
  for (let y = 5; y < px.h; y++) {
    const coef = [0, 1, 2].map(ch => { const r = [0, 0, 0];
      xs.forEach((x, k) => { const val = px.d[(y * px.w + x0 + k) * 4 + ch]; r[0] += val; r[1] += val * x; r[2] += val * x * x; });
      return [0, 1, 2].map(a => inv[a][0] * r[0] + inv[a][1] * r[1] + inv[a][2] * r[2]); });
    let bad = 0;
    xs.forEach((x, k) => { let e = 0;
      for (let ch = 0; ch < 3; ch++) { const f = coef[ch][0] + coef[ch][1] * x + coef[ch][2] * x * x; const dv = px.d[(y * px.w + x0 + k) * 4 + ch] - f; e += dv * dv; }
      if (Math.sqrt(e) > 18) bad++; });
    if (bad / m > 0.02) return y * 4;
  }
  return 1350;
}
function inv3(m) {
  const [a, b, c] = m[0], [d, e, f] = m[1], [g, h, i] = m[2];
  const A = e * i - f * h, B = -(d * i - f * g), C = d * h - e * g, det = a * A + b * B + c * C;
  return [[A / det, -(b * i - c * h) / det, (b * f - c * e) / det],
          [B / det, (a * i - c * g) / det, -(a * f - c * d) / det],
          [C / det, -(a * h - b * g) / det, (a * e - b * d) / det]];
}
// Readable type on any picture (Yarin, 24 Oct 2026, "do it" on the carousel audit's contrast fix: the clock change and
// pacifier carousels set dark plum type on a blue wall). The WCAG contrast of each text block's ink against the picture
// behind its lines, read at the 15th percentile so a busy patch counts. Below MIN_CONTRAST the body first takes the
// headline's darker ink, then the slide turns light on dark if that reads better, and only then a soft panel of the
// wall colour goes behind the copy. The report records the contrast before and after, and the fix used.
const MIN_CONTRAST = 4.5;
function lum(r, g, b) { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); }
function behind(px, s, el, dy) {
  const sr = s.getBoundingClientRect(), out = [];
  el.querySelectorAll('.ln').forEach(l => { const r = document.createRange(); r.selectNodeContents(l); const b = r.getBoundingClientRect();
    if (!b.width) return;
    for (let y = Math.max(0, b.top - sr.top); y < Math.min(1350, b.bottom - sr.top); y += 8)
      for (let x = Math.max(0, b.left - sr.left - 12); x < Math.min(1080, b.right - sr.left + 12); x += 8) {
        const iy = Math.min(px.h - 1, Math.max(0, Math.floor((y < dy ? 0 : y - dy) / 4))), ix = Math.min(px.w - 1, Math.floor(x / 4)), i = (iy * px.w + ix) * 4;
        out.push(lum(px.d[i], px.d[i + 1], px.d[i + 2]));
      } });
  return out;
}
function contrastOf(px, s, el, dy) {
  const cs = getComputedStyle(el), m = cs.color.match(/[0-9.]+/g).map(Number), op = Number(cs.opacity) * (m.length > 3 ? m[3] : 1);
  const ink = lum(m[0], m[1], m[2]), bgs = behind(px, s, el, dy);
  if (!bgs.length) return 21;
  const ks = bgs.map(L => { const t = op * ink + (1 - op) * L; return (Math.max(L, t) + .05) / (Math.min(L, t) + .05); }).sort((a, b) => a - b);
  return ks[Math.floor(ks.length * .15)];
}
function legible(s, px, dy) {
  if (s.classList.contains('cta')) return;   // the last slide keeps its own dark veil
  const c = s.querySelector('.copy'), h = c.querySelector('.h'), b = c.querySelector('.b'), els = [h, b].filter(Boolean);
  const worst = () => Math.min(...els.map(e => contrastOf(px, s, e, dy)));
  const before = worst(); let k = before, fix = 'none';
  if (k < MIN_CONTRAST && b) { b.style.color = getComputedStyle(h).color; b.style.opacity = '1'; const k1 = worst(); if (k1 > k) { k = k1; fix = 'ink'; } else { b.style.color = ''; b.style.opacity = ''; } }
  if (k < MIN_CONTRAST) {
    const keep = b ? [b.style.color, b.style.opacity] : null;
    if (b) { b.style.color = ''; b.style.opacity = ''; }
    s.classList.toggle('dark'); const k2 = worst();
    if (k2 > k) { k = k2; fix = 'flip'; } else { s.classList.toggle('dark'); if (b) { b.style.color = keep[0]; b.style.opacity = keep[1]; } }
  }
  if (k < MIN_CONTRAST) { c.classList.add('panel'); fix = fix === 'none' ? 'panel' : fix + '+panel'; }
  s.dataset.contrast = before.toFixed(2); s.dataset.contrastAfter = (c.classList.contains('panel') ? Math.max(k, MIN_CONTRAST) : k).toFixed(2); s.dataset.fix = fix;
}
// Text on the picture's plain wall, the picture untouched (Yarin, 24 Oct 2026: "i dont want you to distort the images anymore,
// fit the text on the flat space in the generated picture even if it means to play a bit with the sizing of the text or make
// another line"). Every line must end GAP px above the row where the picture stops being plain under that line's own width
// (centred lines, so a short line can go lower between the furniture at the sides). The search tries each headline size from
// the largest down (the body keeps its proportion), first on the copy's own lines and then breaking the widest line that
// does not fit at its most even word gap, up to MAX_SPLITS more lines, and keeps the largest type; every extra line costs
// LINE_COST px of headline size. Under the usual floors it goes on to SMALL of them. If nothing fits even then, the layout
// that runs least into the picture is kept with the soft panel, and the report calls it tight.
const GAP = 28, SIDE = 36, MAX_SPLITS = 3, LINE_COST = 10, SMALL = .8, ARROW_TOP = 1350 - 170;
const clearMaps = {};
function clearTop(px, src, half) {
  // first row that is not plain wall under a centred span of this half width (+SIDE px each side), cached per picture
  const map = clearMaps[src] = clearMaps[src] || {}, k = Math.min(540, Math.max(20, Math.ceil(half / 20) * 20));
  if (!(k in map)) map[k] = subjectTop(px, 540 - k - SIDE, 540 + k + SIDE);
  return map[k];
}
function overlap(s, c, px, src) {
  // how far the copy runs into the picture (0 or less: it fits); a line wider than the copy box never fits
  const sr = s.getBoundingClientRect(); let worst = -1350;
  for (const l of c.querySelectorAll('.ln')) {
    if (l.scrollWidth > l.clientWidth + 1) return 5000 + l.scrollWidth - l.clientWidth;
    const r = document.createRange(); r.selectNodeContents(l); const b = r.getBoundingClientRect();
    if (!b.width) continue;
    const bottom = b.bottom - sr.top, half = Math.max(540 - (b.left - sr.left), b.right - sr.left - 540);
    worst = Math.max(worst, bottom + GAP - clearTop(px, src, half), bottom - ARROW_TOP);
  }
  return worst;
}
function groupsOf(l) {
  // the line's words as node groups: a top-level space separates them; a highlight, button, bubble or Latin run stays whole
  const out = [[]];
  l.childNodes.forEach(n => {
    if (n.nodeType !== 3) { out[out.length - 1].push(n.cloneNode(true)); return; }
    n.textContent.split(/(\\s+)/).forEach(p => { if (!p) return; if (/^\\s+$/.test(p)) out.push([]); else out[out.length - 1].push(document.createTextNode(p)); });
  });
  return out.filter(g => g.length);
}
function splitLine(l) {
  // one line into two at the word gap that makes them most even; a list number stays with its first word
  if (l.querySelector('.btn')) return false;
  const gs = groupsOf(l), len = g => g.reduce((t, n) => t + n.textContent.length, 0);
  const first = /^\\d+$/.test(gs.length ? gs[0].map(n => n.textContent).join('') : '') ? 2 : 1;
  let best = -1, diff = 1e9;
  for (let i = first; i < gs.length; i++) {
    const a = gs.slice(0, i).reduce((t, g) => t + len(g) + 1, 0), b = gs.slice(i).reduce((t, g) => t + len(g) + 1, 0);
    if (Math.abs(a - b) < diff) { diff = Math.abs(a - b); best = i; }
  }
  // the save for later CTA breaks after לפעם הבאה, so the moment about the child stays whole (24 Oct 2026)
  const words = gs.map(g => g.map(n => n.textContent).join(''));
  if (gs.length > 2 && words[0] === 'לפעם' && words[1] === 'הבאה') best = 2;
  if (best < 0) return false;
  const make = part => { const el = l.cloneNode(false); part.forEach((g, k) => { if (k) el.append(' '); el.append(...g); }); return el; };
  l.replaceWith(make(gs.slice(0, best)), make(gs.slice(best)));
  return true;
}
function splitWorst(s, c, px, src) {
  // break the widest line that does not fit on its own
  const sr = s.getBoundingClientRect(); let pick = null, wide = 0;
  for (const l of c.querySelectorAll('.ln')) {
    const r = document.createRange(); r.selectNodeContents(l); const b = r.getBoundingClientRect();
    if (!b.width || l.querySelector('.btn') || groupsOf(l).length < 2) continue;
    const half = Math.max(540 - (b.left - sr.left), b.right - sr.left - 540);
    const bad = l.scrollWidth > l.clientWidth + 1 || b.bottom - sr.top + GAP > clearTop(px, src, half);
    if (bad && b.width > wide) { wide = b.width; pick = l; }
  }
  return pick ? splitLine(pick) : false;
}
function fitTop(s, px, src) {
  const c = s.querySelector('.copy'), h = c.querySelector('.h'), b = c.querySelector('.b');
  const orig = [h.innerHTML, b ? b.innerHTML : ''];
  const hmax = Number(h.dataset.max), hmin = Number(c.dataset.hmin || 56), bmax = b ? Number(b.dataset.max) : 0, bmin = Number(c.dataset.bmin || 40);
  const set = (hs, splits) => {
    h.innerHTML = orig[0]; h.style.fontSize = hs + 'px';
    if (b) { b.innerHTML = orig[1]; b.style.fontSize = Math.max(Math.round(bmin * (hs < hmin ? SMALL : 1)), Math.min(bmax, Math.round(bmax * hs / hmax))) + 'px'; }
    for (let k = 0; k < splits; k++) if (!splitWorst(s, c, px, src)) return k;
    return splits;
  };
  let best = null, least = null;
  for (let hs = hmax; hs >= Math.round(hmin * SMALL); hs -= 4) {
    for (let k = 0; k <= MAX_SPLITS; k++) {
      if (set(hs, k) < k) break;                                  // nothing left to break
      const o = overlap(s, c, px, src);
      if (!least || o < least.o) least = { hs, k, o };
      if (o <= 0) { const score = hs - LINE_COST * k - (hs < hmin ? 30 : 0); if (!best || score > best.score) best = { hs, k, o, score }; break; }
    }
    if (best && hs - 4 <= best.score) break;                      // smaller type cannot win any more
  }
  const pick = best || least;
  set(pick.hs, pick.k);
  if (best && b) {                                                // then the body as large as the wall still allows
    let bs = parseInt(b.style.fontSize);
    while (bs < bmax) { b.style.fontSize = (bs + 2) + 'px'; if (overlap(s, c, px, src) > 0) { b.style.fontSize = bs + 'px'; break; } bs += 2; }
    pick.o = overlap(s, c, px, src);
  }
  c.dataset.fit = best ? 'ok' : 'tight'; c.dataset.headSize = pick.hs; c.dataset.bodySize = b ? parseInt(b.style.fontSize) : 0;
  c.dataset.splits = pick.k; c.dataset.clearance = Math.round(-pick.o);
  if (!best) c.classList.add('panel');
  if (s.classList.contains('cta')) {                              // the dark veil of the last slide ends just under its copy
    const end = c.offsetTop + c.scrollHeight + GAP + 50;
    s.querySelector('.veil').style.background = `linear-gradient(180deg,rgba(var(--veil),.94) 0,rgba(var(--veil),.8) ${Math.round(end * .62)}px,rgba(var(--veil),0) ${end}px)`;
  }
}
function layoutSlide(s) {
  const img = s.querySelector('.art'); const c = s.querySelector('.copy');
  if (!img || !img.naturalWidth) return;
  let px = null;
  try { px = pixels(img); } catch (e) { s.dataset.layout = 'no-pixels'; return; }
  // Dark ink or cream ink: the last slide is always dark; any other slide goes dark when the wall behind the text is dark.
  if (!s.classList.contains('dark') && c.classList.contains('top') && topLuma(px, Math.round(px.h * .3)) < 105) s.classList.add('dark');
  if (c.classList.contains('top')) fitTop(s, px, img.src); else fitSlide(s);
  s.dataset.push = 0; s.dataset.textBottom = c.offsetTop + c.scrollHeight;
  legible(s, px, 0);
}
async function ready() {
  try { await document.fonts.ready; } catch (e) {}
  await Promise.all([...document.querySelectorAll('img.art')].map(i => i.complete ? null : new Promise(r => { i.onload = r; i.onerror = r; })));
  try { document.querySelectorAll('.slide').forEach(s => { fitSlide(s); layoutSlide(s); }); }
  catch (e) { document.getElementById('rtl-report').textContent = 'JSERROR ' + e + ' ' + e.stack; document.body.dataset.ready = '1'; return; }
  if (q.get('check')) {
    const rep = [...document.querySelectorAll('.slide')].map(s => {
      const c = s.querySelector('.copy'); const cs = getComputedStyle(c);
      const blocks = [...s.querySelectorAll('.copy .ln, .ai')].map(el => ({
        text: el.textContent, direction: getComputedStyle(el).direction, textAlign: getComputedStyle(el).textAlign,
        mixed: /[A-Za-z0-9]/.test(el.textContent), overflow: el.scrollWidth > el.clientWidth + 1 }));
      return { n: Number(s.dataset.n), lang: document.documentElement.lang, htmlDir: document.documentElement.dir,
               direction: cs.direction, textAlign: cs.textAlign, fit: c.dataset.fit, push: Number(s.dataset.push || 0), clear: c.dataset.clear || 'ok', dark: s.classList.contains('dark'), headSize: Number(c.dataset.headSize), bodySize: Number(c.dataset.bodySize),
               splits: Number(c.dataset.splits || 0), clearance: Number(c.dataset.clearance || 0),
               contrast: Number(s.dataset.contrast || 0), contrastAfter: Number(s.dataset.contrastAfter || 0), contrastFix: s.dataset.fix || '', blocks };
    });
    document.getElementById('rtl-report').textContent = JSON.stringify(rep);
  }
  document.body.dataset.ready = '1';
}
ready();
"""

ARROW = '<div class="arrow"><svg viewBox="0 0 44 44"><path d="M36 22H8M19 10 7 22l12 12"/></svg></div>'

# ---------------------------------------------------------------------------------------------------------------------
# The story look (story-format.md section 6, Yarin 29 Oct 2026: "i like the new content, change the entire carousel
# machine and November batch to match it"). Ported from media/projects/2026-10-29-lotem-format-carousels/render.py
# (final-v4 is the reference): Lotem Lerner's text treatment in lumebook.com's palette and font. An ink #0B0518 veil over
# each slide's own picture, cream #F8F0E1 type in Varela Round (one weight, so a thin stroke in the type's own colour reads
# heavier), gold #E6B762 tags, labels, emphasis, cover pill and save button, soft gold #F3D9A1 for quoted speech, a cream
# card for "> " lines, the letter structure on a cream sheet in ink. No logo, handle or swipe arrow. Body lines are broken
# by hand (white-space nowrap) and the whole copy block shrinks in steps only when it does not fit.
# ---------------------------------------------------------------------------------------------------------------------
STORY_CSS = """
@font-face{font-family:"Varela Round";src:url("{he}") format("woff2");unicode-range:U+0307-0308,U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F;font-display:block}
@font-face{font-family:"Varela Round";src:url("{la}") format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD;font-display:block}
:root{--ink:#0B0518;--ink-2:#1D1039;--gold:#E6B762;--gold-soft:#F3D9A1;--cream:#F8F0E1}
*{box-sizing:border-box;margin:0;padding:0}
html,body{direction:rtl;background:#0B0518}
body.single .slide:not(.on){display:none}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:var(--ink);font-family:"Varela Round",sans-serif;color:var(--cream);text-align:center;direction:rtl}
.art{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover}
.veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,5,24,.88) 0,rgba(11,5,24,.8) 45%,rgba(11,5,24,.55) 66%,rgba(11,5,24,.22) 84%,rgba(11,5,24,.38) 100%)}
.cover .veil{background:linear-gradient(180deg,rgba(11,5,24,.88) 0,rgba(11,5,24,.66) 30%,rgba(11,5,24,0) 52%)}
.cta .veil{background:linear-gradient(180deg,rgba(11,5,24,.9) 0,rgba(11,5,24,.78) 40%,rgba(11,5,24,.45) 70%,rgba(11,5,24,.55) 100%)}
.copy{position:absolute;top:70px;left:70px;right:70px;direction:rtl;text-align:center}
.h,.t{text-wrap:balance;-webkit-text-stroke:.022em currentColor;paint-order:stroke fill;text-shadow:0 2px 22px rgba(11,5,24,.7)}
.h{line-height:1.16;letter-spacing:-.005em}
.h .ln{display:block}
.t{font-size:.74em;line-height:1.3;margin-top:.15em;-webkit-text-stroke-width:.014em}
.part{margin-top:.5em}
.lab{display:block;color:var(--gold);font-size:.56em;letter-spacing:.01em;margin-bottom:.15em;-webkit-text-stroke:.012em currentColor;text-shadow:0 2px 16px rgba(11,5,24,.8)}
.q{color:var(--gold-soft)}
.num{display:inline-flex;align-items:center;justify-content:center;width:84px;height:84px;border-radius:50%;background:var(--gold);color:var(--ink);font-size:46px;margin-bottom:26px;box-shadow:0 8px 24px rgba(11,5,24,.45)}
.pill{display:inline-block;margin-top:34px;background:var(--gold);color:var(--ink);border-radius:999px;padding:.22em .9em .3em;font-size:.5em;line-height:1.2;box-shadow:0 10px 28px rgba(11,5,24,.45)}
.btn{display:inline-flex;white-space:nowrap;align-items:center;gap:.35em;background:var(--gold);color:var(--ink);border-radius:999px;padding:.16em .8em .24em;-webkit-text-stroke:.02em currentColor;text-shadow:none;box-shadow:0 12px 30px rgba(0,0,0,.45)}
.btn svg{width:.8em;height:.8em;fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.tag{display:inline-flex;align-items:center;gap:.3em;color:var(--gold);font-size:.46em;margin-bottom:.45em;-webkit-text-stroke:.012em currentColor;text-shadow:0 2px 16px rgba(11,5,24,.8)}
.tag .num{width:1.55em;height:1.55em;margin:0;font-size:1em;box-shadow:0 6px 18px rgba(11,5,24,.45);-webkit-text-stroke:0}
.body{font-size:.6em;margin-top:.55em}
/*BOOKLET*/
.body .t{font-size:1em;margin-top:0}
.body .t .ln{display:block;white-space:nowrap}
.body .gap{height:.55em}
.body .lab{font-size:.8em;margin:.55em 0 .05em}
.body .lab:first-child{margin-top:0}
.em{color:var(--gold);-webkit-text-stroke:.03em currentColor}
.say{display:inline-block;margin-top:.15em;background:var(--cream);color:var(--ink);border-radius:.7em;padding:.28em .8em .36em;line-height:1.3;-webkit-text-stroke:.012em currentColor;text-shadow:none;box-shadow:0 10px 28px rgba(11,5,24,.5);white-space:nowrap}
.say .q{color:var(--ink)}
.tag.plain{font-size:.5em}
.letter .copy{background:var(--cream);color:var(--ink);border-radius:34px;padding:56px 58px 60px;transform:rotate(-1.2deg);box-shadow:0 24px 60px rgba(11,5,24,.55)}
.letter .h,.letter .t,.letter .lab{text-shadow:none}
.letter .h{font-size:.92em}
.letter .em,.letter .q{color:#8A5A14}
.letter .veil{background:linear-gradient(180deg,rgba(11,5,24,.55) 0,rgba(11,5,24,.3) 60%,rgba(11,5,24,.2) 100%)}
/* the medical disclaimer at the foot of every slide from slide 2 (Yarin, 31 Oct 2026: "only from the second slide") */
.disc-bg{position:absolute;left:0;right:0;bottom:0;height:190px;background:linear-gradient(180deg,rgba(11,5,24,0),rgba(11,5,24,.62))}
.disc{position:absolute;left:150px;right:150px;bottom:30px;font-size:20px;line-height:1.38;color:rgba(255,255,255,.82);text-align:center;direction:rtl;text-wrap:balance;text-shadow:0 1px 6px rgba(0,0,0,.75)}
pre#rtl-report{display:none}
"""

# The booklet under the book link CTA (30 Oct 2026, story-format.md section 7), drawn in 3D since 31 Oct 2026. Carousel
# Machine's preview uses the same rules and the same HTML (studio.py), so every class starts with bk3.
BOOKLET_CSS = """
.bk3-fade{position:absolute;left:0;top:500px;width:1080px;height:220px;background:linear-gradient(180deg,rgba(11,5,24,0),rgba(11,5,24,.9) 55%,rgba(11,5,24,0))}
.bk3{position:absolute;left:0;top:0;width:1080px;height:1350px;pointer-events:none}
.bk3 svg{position:absolute;left:0;top:0;overflow:visible}
.bk3-strip{position:absolute;left:0;top:0;transform-origin:0 0;background-repeat:no-repeat;backface-visibility:hidden}
.bk3-strip i{position:absolute;inset:0}
.bk3-page{position:absolute;left:0;top:0;transform-origin:0 0;display:flex;flex-direction:column;justify-content:center;align-items:center;font-size:38px;line-height:1.45;color:#2a2340;text-align:center;direction:rtl;font-family:inherit}
.bk3-page span{display:block;white-space:nowrap}
.bk3-kid{position:absolute;left:830px;top:505px;width:230px;height:230px;border-radius:50%;border:7px solid #fff;box-shadow:0 8px 22px rgba(0,0,0,.35);background-size:cover;background-position:50% 38%}
"""
STORY_CSS = STORY_CSS.replace("/*BOOKLET*/", BOOKLET_CSS.strip())

STORY_JS = """
const q = new URLSearchParams(location.search), one = q.get('s');
if (one) { document.body.classList.add('single'); document.querySelector('.slide[data-n="' + one + '"]').classList.add('on'); }
const WIDE = '.h,.t,.ln,.pill,.say,.tag,.btn';
function fit(s) {
  // the whole copy block shrinks in steps of 2px until it ends above data-maxh and no line runs past the sides
  const c = s.querySelector('.copy'), maxH = Number(c.dataset.maxh), min = Number(c.dataset.min);
  let k = Number(c.dataset.max);
  const over = () => c.scrollHeight > maxH || [...c.querySelectorAll(WIDE)].some(e => e.scrollWidth > e.clientWidth + 1);
  c.style.fontSize = k + 'px';
  while (over() && k > min) { k -= 2; c.style.fontSize = k + 'px'; }
  c.dataset.fit = over() ? 'overflow' : 'ok'; c.dataset.size = k;
}
(async () => {
  try { await document.fonts.ready; } catch (e) {}
  await Promise.all([...document.images].map(i => i.complete ? null : new Promise(r => { i.onload = r; i.onerror = r; })));
  try { document.querySelectorAll('.slide').forEach(fit); }
  catch (e) { document.getElementById('rtl-report').textContent = 'JSERROR ' + e + ' ' + e.stack; document.body.dataset.ready = '1'; return; }
  if (q.get('check')) {
    const font = document.fonts.check('40px "Varela Round"', 'אב');
    const rep = [...document.querySelectorAll('.slide')].map(s => {
      const c = s.querySelector('.copy'), cs = getComputedStyle(c), k = Number(c.dataset.size);
      const blocks = [...s.querySelectorAll('.copy .ln, .copy .lab, .copy .tag, .copy .say, .copy .pill, .copy .btn, .cta .t')].map(el => ({
        text: el.textContent, direction: getComputedStyle(el).direction, textAlign: getComputedStyle(el).textAlign,
        mixed: /[A-Za-z0-9]/.test(el.textContent), overflow: el.scrollWidth > el.clientWidth + 1 }));
      return { n: Number(s.dataset.n), lang: document.documentElement.lang, htmlDir: document.documentElement.dir,
               direction: cs.direction, textAlign: cs.textAlign, fit: c.dataset.fit, push: 0, clear: 'ok', dark: true,
               headSize: k, bodySize: Math.round(k * (s.classList.contains('cover') ? .5 : s.classList.contains('cta') ? .67 : .6)),
               splits: 0, clearance: Math.round(Number(c.dataset.maxh) - c.scrollHeight), height: c.scrollHeight, maxH: Number(c.dataset.maxh),
               contrast: 0, contrastAfter: 0, contrastFix: 'veil', font, blocks };
    });
    document.getElementById('rtl-report').textContent = JSON.stringify(rep);
  }
  document.body.dataset.ready = '1';
})();
"""

STORY_SAVE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 3h11a1.5 1.5 0 0 1 1.5 1.5V21l-7-6.2L5 21V4.5A1.5 1.5 0 0 1 6.5 3z"/></svg>'
STORY_QUOTE = re.compile(r"(״[^״]+״)")
STORY_NUMBERED_TAG = re.compile(r"(\d+):\s+(.*)")
# (headline max px, floor px, the height the copy block must end above) per slide kind, as in render.py
STORY_SIZES = {"cover": (104, 72, 560), "cta": (84, 60, 520), "slide": (84, 62, 900), "cta_booklet": (66, 50, 425)}
STORY_MARKUP = re.compile(r"\*\*|^\s*(?:##|>)\s+", re.M)


def is_story(frozen):
    """A run in the story format (story-format.md): the frozen pack's copy_style, or the option's own structure."""
    v = (frozen or {}).get("option") or {}
    return (frozen or {}).get("copy_style") == "story" or v.get("copy_style") == "story" or bool(v.get("structure"))


def plain_text(text):
    """Story copy without its markup (## label, > card, **emphasis**), for the alt text."""
    return STORY_MARKUP.sub("", text or "")


def _story_text(t):
    # spoken lines in gershayim in the soft gold
    return "".join(f'<span class="q">{_safe(p)}</span>' if i % 2 else _safe(p) for i, p in enumerate(STORY_QUOTE.split(t)))


def _story_rich(t):
    # **x** is gold emphasis, the stand-in for her heavy-bold words (Varela Round has one weight)
    return "".join(f'<span class="em">{_story_text(p)}</span>' if i % 2 else _story_text(p) for i, p in enumerate(t.split("**")))


def story_body_html(body):
    """'## ' a gold label, '> ' a cream card, an empty line a gap, every other line its own hand-broken line."""
    out, para = [], []

    def flush():
        if para:
            out.append('<div class="t">' + "".join(f'<span class="ln">{_story_rich(l)}</span>' for l in para) + "</div>")
            para.clear()
    for line in (body or "").split("\n"):
        line = line.strip()
        if not line:
            flush()
            out.append('<div class="gap"></div>')
        elif line.startswith("## "):
            flush()
            out.append(f'<div class="lab">{_story_rich(line[3:].strip())}</div>')
        elif line.startswith("> "):
            flush()
            out.append(f'<div><span class="say">{_story_rich(line[2:].strip())}</span></div>')
        else:
            para.append(line)
    flush()
    return '<div class="body">' + "".join(out) + "</div>"


BOOK_BOX = (65, 620, 950)          # left, top, width of the booklet's flat spread on the last slide
ARROW_YELLOW = "#FFC21A"           # Yarin, 30 Oct 2026: "straight short arrows", then "bigger, add a thin black outline"
# The booklet in 3D (Yarin, 31 Oct 2026: "the booklet in the last slides should look more 3D like but not like a book, its
# a booklet"): the flat spread (the crop of RUN_DIR/booklet/booklet.png) lies open, tilted back, thin and soft. Each page
# is cut into strips from the fold outwards (BOOK_STRIPS, parts of the page width) that bend down into the fold, the far
# edge is narrower than the near one, two sheet edges and the soft cover show under the pages, and a soft shadow sits
# under it all. Every strip is the flat picture mapped onto its corners (a CSS matrix3d), so no new picture is made.
BOOK_STRIPS = (0, 0.03, 0.07, 0.12, 0.2, 1)
BOOK_TILT = 0.9                    # the page height after the tilt
BOOK_FAR_INSET = 42                # the far edge is this much narrower at each side
BOOK_DIP = (28, 15)                # how deep the far and the near edge sink into the fold
BOOK_LIFT = (9, 5)                 # how much the far and the near edge rise across the page
BOOK_SHEETS = ((3, 2, "#F4F1F7"), (6, 4, "#E3DDEA"), (9, 6, "#CEC5DA"))   # down, out, colour: two sheets and the cover
BOOK_TEXT_SPAN = (0.08, 0.96)      # where the page text box sits across the white page (part of its width from the fold)


def _solve(a, b):
    """Gaussian elimination with partial pivoting (8 x 8, no numpy on the server's Python)."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[piv] = m[piv], m[c]
        for r in range(n):
            if r != c and m[r][c]:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


def homography(src, dst):
    """The 3 x 3 projective map that takes the four src points to the four dst points."""
    a, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    h = _solve(a, b)
    return [[h[0], h[1], h[2]], [h[3], h[4], h[5]], [h[6], h[7], 1.0]]


def hpoint(hm, x, y):
    w = hm[2][0] * x + hm[2][1] * y + hm[2][2]
    return ((hm[0][0] * x + hm[0][1] * y + hm[0][2]) / w, (hm[1][0] * x + hm[1][1] * y + hm[1][2]) / w)


def matrix3d(hm, x0=0.0, y0=0.0):
    """CSS matrix3d for an element whose own (0, 0) sits at flat (x0, y0), with transform-origin 0 0."""
    m = [[hm[r][0], hm[r][1], hm[r][0] * x0 + hm[r][1] * y0 + hm[r][2]] for r in range(3)]
    d = m[2][2]
    m = [[v / d for v in row] for row in m]
    vals = (m[0][0], m[1][0], 0, m[2][0], m[0][1], m[1][1], 0, m[2][1], 0, 0, 1, 0, m[0][2], m[1][2], 0, m[2][2])
    return "matrix3d(" + ",".join(f"{v:.8g}" for v in vals) + ")"


def _book_edge(side, u, far, box):
    """A point on the far (top) or near (bottom) edge of a page: side -1 the left page, 1 the right; u 0 at the fold,
    1 at the outer corner."""
    left, top, width, flat_h = box
    fold = left + width / 2
    reach = width / 2 - (BOOK_FAR_INSET if far else 0)
    e = 0 if far else 1
    y = (top if far else top + flat_h * BOOK_TILT) + BOOK_DIP[e] * max(0.0, 1 - u / 0.2) ** 2 - BOOK_LIFT[e] * math.sin(math.pi * u)
    return (fold + side * u * reach, y)


def booklet_geometry(booklet):
    """Where every strip of the two pages goes, as flat spread coordinates (0 .. 950 wide) mapped to slide pixels."""
    bx, by, bw = BOOK_BOX
    cx, cy, cw, ch = booklet["crop"]
    k = bw / cw
    flat_h = ch * k
    pw = bw / 2
    box = (bx, by, bw, flat_h)
    pages = {}
    for side in (-1, 1):   # -1 the picture page, 1 the white page
        strips = []
        for u0, u1 in zip(BOOK_STRIPS, BOOK_STRIPS[1:]):
            x0, x1 = (pw * (1 - u1), pw * (1 - u0)) if side < 0 else (pw * (1 + u0), pw * (1 + u1))
            ua, ub = (u1, u0) if side < 0 else (u0, u1)   # u at the strip's flat left and right edge
            dst = [_book_edge(side, ua, True, box), _book_edge(side, ub, True, box),
                   _book_edge(side, ub, False, box), _book_edge(side, ua, False, box)]
            strips.append({"u": (u0, u1), "x": (x0, x1), "h": homography([(x0, 0), (x1, 0), (x1, flat_h), (x0, flat_h)], dst)})
        pages[side] = strips
    steps = [1, .85, .7, .55, .4, .3, .22, .16, .11, .07, .04, .02, 0]
    outline = {"far": [_book_edge(-1, u, True, box) for u in steps] + [_book_edge(1, u, True, box) for u in reversed(steps)],
               "near": [_book_edge(1, u, False, box) for u in steps] + [_book_edge(-1, u, False, box) for u in reversed(steps)]}
    return {"k": k, "flat_h": flat_h, "pw": pw, "crop": (cx, cy), "pages": pages, "outline": outline, "box": box}


def booklet_face_tip(booklet, geo=None):
    """The arrow tip just under the face on the picture page, from the lower left (face [x, y] or [x, y, scale], parts
    of the flat spread's width and height), and the arrow's tail."""
    geo = geo or booklet_geometry(booklet)
    fx, fy = booklet["face"][:2]
    k_face = booklet["face"][2] if len(booklet["face"]) > 2 else 1   # a smaller face: the tip sits closer to it
    x, y = fx * BOOK_BOX[2], fy * geo["flat_h"]
    strip = min(geo["pages"][-1], key=lambda s: 0 if s["x"][0] <= x <= s["x"][1] else min(abs(x - s["x"][0]), abs(x - s["x"][1])))
    px, py = hpoint(strip["h"], x, y)
    tip = (px - 60 * k_face, py + 95 * k_face)
    tail = (tip[0] - 122, tip[1] + 145)
    if tail[0] < 30:                                           # a face near the left edge: from the lower right
        tail = (tip[0] + 122, tip[1] + 145)
    return tip, tail


def _pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def booklet_html(booklet, files, uid=""):
    """The booklet block of the last slide in 3D: the shadow and the thin edges, the two pages in strips with the page
    text set in Varela Round on the white page, the face photo in a circle over the top right corner, and an arrow at
    each face. files: {"booklet": src, "kid": src, "booklet_path": the local booklet.png}; uid keeps the SVG ids apart
    when several previews share a page (Carousel Machine)."""
    geo = booklet_geometry(booklet)
    k, flat_h = geo["k"], geo["flat_h"]
    cx, cy = geo["crop"]
    nat_w, nat_h = lib.png_size(files["booklet_path"])
    far, near = geo["outline"]["far"], geo["outline"]["near"]
    fold = BOOK_BOX[0] + BOOK_BOX[2] / 2

    def spread(points, down, out):   # the outline pushed down and out towards the outer corners
        return [(x + (out * (x - fold) / (BOOK_BOX[2] / 2)), y + down) for x, y in points]
    shadow = spread(far, 10, 6) + spread(near, 26, 14)
    under = (f'<svg viewBox="0 0 1080 1350" width="1080" height="1350"><defs>'
             f'<filter id="bks{uid}" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="16"/></filter>'
             f'<filter id="bkc{uid}" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="4"/></filter></defs>'
             f'<polygon points="{_pts(shadow)}" fill="rgba(4,0,12,.62)" filter="url(#bks{uid})"/>'
             f'<polygon points="{_pts(spread(far, 4, 4) + spread(near, 12, 8))}" fill="rgba(4,0,12,.45)" filter="url(#bkc{uid})"/>'
             + "".join(f'<polygon points="{_pts(spread(far, d, o) + spread(near, d, o))}" fill="{c}" stroke="rgba(60,40,80,.18)" stroke-width="1"/>'
                       for d, o, c in reversed(BOOK_SHEETS))
             + "</svg>")
    strips = []
    for side, page in geo["pages"].items():
        for s in page:
            x0, x1 = s["x"]
            u0, u1 = s["u"]
            a0, a1 = (.44 * max(0.0, 1 - u / 0.2) ** 1.7 + .03 for u in (u0, u1))
            shade = (f"linear-gradient(to right,rgba(24,12,44,{a1:.3f}),rgba(24,12,44,{a0:.3f}))" if side < 0
                     else f"linear-gradient(to right,rgba(24,12,44,{a0:.3f}),rgba(24,12,44,{a1:.3f}))")
            if u1 == 1:   # a soft light across the open part of the page, nothing at the edge next to the bent strips
                shade += (",linear-gradient(to right,rgba(255,255,255,.1),rgba(255,255,255,0) 60%)" if side < 0
                          else ",linear-gradient(to right,rgba(255,255,255,0),rgba(255,255,255,.08) 55%,rgba(255,255,255,0))")
                shade += ",linear-gradient(180deg,rgba(0,0,0,0) 55%,rgba(0,0,0,.07))"
            pad = 0.8   # strips overlap a hair, so no seam shows between them
            strips.append(f'<div class="bk3-strip" style="width:{x1 - x0 + 2 * pad:.2f}px;height:{flat_h:.2f}px;'
                          f'transform:{matrix3d(s["h"], x0 - pad, 0)};background-image:url(&quot;{files["booklet"]}&quot;);'
                          f'background-size:{nat_w * k:.1f}px {nat_h * k:.1f}px;background-position:{-(cx * k + x0 - pad):.2f}px {-cy * k:.2f}px">'
                          f'<i style="background:{shade}"></i></div>')
    outer = geo["pages"][1][-1]
    t0, t1 = (geo["pw"] * (1 + f) for f in BOOK_TEXT_SPAN)
    page = (f'<div class="bk3-page" style="width:{t1 - t0:.1f}px;height:{flat_h:.1f}px;transform:{matrix3d(outer["h"], t0, 0)}">'
            + "".join(f"<span>{esc(ln)}</span>" for ln in booklet["page_text"]) + "</div>")
    tip, tail = booklet_face_tip(booklet, geo)
    arrows = [(tail, tip), ((1040, 845), (978, 724))]          # the second points up at the photo's chin
    paths = "".join(f'<path d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="#000" stroke-width="19" marker-end="url(#ao{uid})"/>'
                    f'<path d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="{ARROW_YELLOW}" stroke-width="13" marker-end="url(#ah{uid})"/>'
                    for a, b in arrows)
    crease = f'<path d="M{far[len(far) // 2][0]:.1f} {far[len(far) // 2][1]:.1f} L{near[len(near) // 2][0]:.1f} {near[len(near) // 2][1]:.1f}" stroke="rgba(30,15,50,.35)" stroke-width="1.6"/>'
    top = (f'<svg viewBox="0 0 1080 1350" width="1080" height="1350"><defs>'
           f'<marker id="ah{uid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.4" markerHeight="4.4" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{ARROW_YELLOW}"/></marker>'
           f'<marker id="ao{uid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="3.6" markerHeight="3.6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#000"/></marker>'
           f'</defs>{crease}<g fill="none" stroke-linecap="round" stroke-linejoin="round">{paths}</g></svg>')
    return (f'<div class="bk3-fade"></div><div class="bk3">{under}{"".join(strips)}{page}</div>'
            f'<div class="bk3-kid" style="background-image:url(&quot;{files["kid"]}&quot;)"></div>'
            f'<div class="bk3">{top}</div>')


def story_slide_html(v, s, img_src, last, booklet_files=None):
    n = s["number"]
    head, body = s.get("headline", ""), (s.get("body") or "").strip()
    cls, inner = "", []
    if n == 1:
        cls, kind = "cover", "cover"
        inner.append('<div class="h">' + "".join(f'<span class="ln">{_story_text(l)}</span>' for l in lib.lines_of(head)) + "</div>")
        if body:
            inner.append(f'<div class="pill">{_story_rich(lib.collapse(body))}</div>')
    elif n == last:
        cls, kind = "cta", "cta"
        if SAVE_LINE_RE.match(head):   # the save line is the gold button; the book link CTA (30 Oct 2026) has a plain headline
            inner.append(f'<div class="h"><span class="btn">{STORY_SAVE_ICON}{_safe(lib.collapse(head))}</span></div>')
        else:
            inner.append('<div class="h">' + "".join(f'<span class="ln">{_story_text(l)}</span>' for l in lib.lines_of(head)) + "</div>")
        if not SAVE_LINE_RE.match(head):   # book link CTA: the comment word in gold, one line per thought
            body_html = "".join(f'<span class="ln" style="display:block">{_story_rich(re.sub(r"([\"״][^\"״]+[\"״])", r"**\1**", l))}</span>' for l in lib.lines_of(body))
            inner.append(f'<div class="part"><div class="t" style="font-size:.9em">{body_html}</div></div>')
        else:
            inner.append('<div class="part"><div class="t" style="font-size:.9em">' + _story_rich(lib.collapse(body)) + "</div></div>")
    else:
        kind = "slide"
        label = (s.get("label") or "").strip()
        m = STORY_NUMBERED_TAG.match(label)
        if m:
            inner.append(f'<div><span class="tag"><span class="num">{esc(m.group(1))}</span>{_safe(m.group(2))}</span></div>')
        elif label:
            inner.append(f'<div><span class="tag plain">{_safe(label)}</span></div>')
        if head.strip():
            inner.append('<div class="h">' + "".join(f'<span class="ln">{_story_rich(l)}</span>' for l in lib.lines_of(head)) + "</div>")
        if v.get("structure") == "letter":
            cls = "letter"
        inner.append(story_body_html(body))
    mx, mn, max_h = STORY_SIZES[kind]
    extra = ""
    if n == last and booklet_files and v.get("booklet"):   # the copy ends above the photo circle, the booklet below it
        mx, mn, max_h = STORY_SIZES["cta_booklet"]
        extra = booklet_html(v["booklet"], booklet_files)
    disc = (f'<div class="disc-bg"></div>', f'<div class="disc">{esc(lib.SLIDE_DISCLAIMER)}</div>') if n > 1 else ("", "")   # slide 1, the thumbnail, has none
    return (f'<section class="slide {cls}" data-n="{n}"><img class="art" src="{img_src}" alt=""><div class="veil"></div>'
            f'{disc[0]}<div class="copy" data-max="{mx}" data-min="{mn}" data-maxh="{max_h}" style="font-size:{mx}px">'
            + "".join(inner) + "</div>" + extra + f'{disc[1]}</section>')


def build_story_html(frozen, images, out_dir):
    v = frozen["option"]
    css = (STORY_CSS.replace("{he}", rel(FONTS / "VarelaRound-hebrew.woff2", out_dir))
                    .replace("{la}", rel(FONTS / "VarelaRound-latin.woff2", out_dir)))
    last = len(v["slides"])
    files = None
    if v.get("booklet"):   # RUN_DIR/booklet/ (scripts/booklet_cta.py)
        bdir = Path(images[last]).parent.parent / "booklet"
        if not (bdir / "booklet.png").exists() or not (bdir / "kid.png").exists():
            raise SystemExit(f"the option has a booklet but {bdir} lacks booklet.png or kid.png (scripts/booklet_cta.py)")
        files = {"booklet": rel(bdir / "booklet.png", out_dir), "kid": rel(bdir / "kid.png", out_dir), "booklet_path": bdir / "booklet.png"}
    sections = "".join(story_slide_html(v, s, rel(images[s["number"]], out_dir), last, files) for s in v["slides"])
    return ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{esc(frozen["date"])} {esc(v["id"])}</title><style>{css}</style></head>'
            f'<body dir="rtl" class="look-story structure-{esc(v.get("structure") or "story")}">{sections}'
            f'<pre id="rtl-report"></pre><script>{STORY_JS}</script></body></html>')


def rel(target, base):
    return Path(os.path.relpath(target, base)).as_posix()


LATIN_RUN = re.compile(r"([A-Za-z][A-Za-z0-9 .'&-]*[A-Za-z0-9]|[A-Za-z])")
SPOKEN_RE = re.compile(r"([״\"“][^״\"“”]{6,}[״\"”])")
SAVE_LINE_RE = re.compile(r"\s*ת?שמר[וי](?![א-ת])")   # the save and share CTA's first line (24 Oct 2026)
SEND_LINE_RE = re.compile(r"\s*ו?ת?שלח[וי](?![א-ת])")  # and its second line
# Instagram's save (bookmark) and send (paper plane) glyphs, drawn as outlines like the app's own
SAVE_ICON = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 3h11a1.5 1.5 0 0 1 1.5 1.5V21l-7-6.2L5 21V4.5A1.5 1.5 0 0 1 6.5 3z"/></svg>'
SEND_ICON = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M22 2.5 10.6 13.4"/><path d="M22 2.5 15 21.5l-4.4-8.1L2.5 9z"/></svg>'
LOOKS = ("clean", "bold", "classic", "story")
# Type sizes per look: (headline max, headline floor, body max, body floor) for the cover, a regular slide, the last slide
SIZES = {
    "classic": {"cover": (96, 56, 50, 40), "slide": (96, 56, 50, 40), "cta": (84, 56, 50, 40)},
    "bold": {"cover": (156, 84, 80, 52), "slide": (118, 72, 56, 42), "cta": (92, 64, 58, 42)},
    "clean": {"cover": (128, 80, 60, 44), "slide": (112, 72, 54, 42), "cta": (92, 64, 58, 42)},
}


def _safe(piece):
    # isolate Latin runs so bidi never moves neighbouring punctuation
    # split the raw text first, then escape each piece, so entities like &quot; are never split
    parts = LATIN_RUN.split(piece)
    return "".join(f'<bdi dir="ltr">{esc(p)}</bdi>' if i % 2 else esc(p) for i, p in enumerate(parts))


def lines_html(text, highlight=None, bubbles=False, button=None):
    """One <span class="ln"> per line. Bold look only: `highlight` (a phrase of the text) gets the colour block
    once, `bubbles` wraps spoken sentences in quotation marks, `button` is the line set as the comment button.
    A save line as the button gets the save icon, and the send line after it the send icon."""
    out = []
    highlight = (highlight or "").strip()
    saving = bool(button and SAVE_LINE_RE.match(button))
    for line in lib.lines_of(text):
        if button and line.strip() == button.strip():
            out.append(f'<span class="ln"><span class="btn">{SAVE_ICON if saving else ""}{_safe(line)}</span></span>')
            continue
        if saving and SEND_LINE_RE.match(line):
            out.append(f'<span class="ln">{SEND_ICON}{_safe(line)}</span>')
            continue
        if highlight and highlight in line:
            before, after = line.split(highlight, 1)
            safe = f'{_safe(before)}<span class="hl">{_safe(highlight)}</span>{_safe(after)}'
            highlight = ""
        elif bubbles:
            safe = "".join(f'<span class="q">{_safe(p)}</span>' if i % 2 else _safe(p) for i, p in enumerate(SPOKEN_RE.split(line)))
        else:
            safe = _safe(line)
        out.append(f'<span class="ln">{safe}</span>')
    return "".join(out)


def slide_highlight(slide):
    """The phrase that gets the colour block: the slide's own `highlight` when it is still in the headline,
    otherwise the last headline line on the cover and nothing elsewhere."""
    head = slide.get("headline", "")
    want = str(slide.get("highlight") or "").strip()
    if want and any(want in line for line in lib.lines_of(head)):
        return want
    if slide.get("number") == 1:
        lines = lib.lines_of(head)
        return lines[-1].strip() if lines else ""
    return ""


def build_html(frozen, images, out_dir, preview, brand_mark=False, look="bold"):
    v = frozen["option"]
    css = (CSS.replace("{heebo}", rel(FONTS / "Heebo-Black.ttf", out_dir))
              .replace("{assistant}", rel(FONTS / "Assistant-VariableFont_wght.ttf", out_dir))
              .replace("{rubik}", rel(FONTS / "Rubik-VariableFont_wght.ttf", out_dir)))
    bold = look in ("bold", "clean")
    clean = look == "clean"
    pillar = frozen.get("direction") if frozen.get("direction") in lib.PILLARS else "expert"
    sections = []
    for s in v["slides"]:
        n = s["number"]
        zone = lib.slide_image(v, s)["text_zone"]
        edge, pct = zone["edge"], zone["percent"]
        last = len(v["slides"])
        dark = n == last
        if dark:
            edge = "top"
        max_h = int(H * pct / 100) - ((72 if bold else 150) if edge == "top" else 180) + 60
        head_max, head_min, body_max, body_min = SIZES[look]["cta" if n == last else "cover" if n == 1 else "slide"]
        body = s.get("body", "").strip()
        # the comment line (code word in quotes), or since 24 Oct 2026 the save line of the save and share CTA, as the button
        button = next((ln for ln in lib.lines_of(body) if re.search(r"[\"״]", ln) or SAVE_LINE_RE.match(ln)), None) if bold and n == last else None
        # since the save for later CTA (24 Oct 2026 evening) the save line is slide 10's headline, drawn as the button
        head_lines = lib.lines_of(s["headline"])
        head_button = head_lines[0] if bold and n == last and len(head_lines) == 1 and SAVE_LINE_RE.match(head_lines[0]) else None
        src = rel(images[n], out_dir)
        parts = [f'<section class="slide{" dark" if dark else ""}{" cta" if n == last else ""}" data-n="{n}">',
                 f'<img class="art" src="{src}" alt="">',
                 f'<div class="veil {edge}"></div>',
                 f'<div class="copy {edge}" data-maxh="{max_h}" data-hmin="{head_min}" data-bmin="{body_min}">',
                 f'<div class="h" data-max="{head_max}">{lines_html(s["headline"], highlight=slide_highlight(s) if bold and (n == last or not clean) else None, button=head_button)}</div>']
        if body:
            parts.append(f'<div class="b" data-max="{body_max}">{lines_html(body, bubbles=bold and not button and (n == last or not clean), button=button)}</div>')
        parts.append('</div>')
        if brand_mark:
            parts.append(f'<img class="mark" src="{rel(LOGO, out_dir)}" alt="">')
        if n == last and preview:
            parts.append(f'<div class="card"><img src="{rel(preview, out_dir)}" alt=""></div>')
        if n < last:
            parts.append(ARROW)
        parts.append('</section>')
        sections.append("".join(parts))
    return ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{esc(frozen["date"])} {esc(v["id"])}</title><style>{css}</style></head>'
            f'<body dir="rtl" class="pillar-{pillar} look-{'bold look-clean' if clean else look}">{"".join(sections)}<pre id="rtl-report"></pre><script>{JS}</script></body></html>')


def chrome(args, timeout=60):
    if not lib.CHROME:
        if os.environ.get("CHROME_PATH", "").strip():
            raise SystemExit(f"CHROME_PATH={os.environ['CHROME_PATH']} is not an executable Chrome or Chromium")
        raise SystemExit(f"Google Chrome not found: looked for {lib.CHROME_MAC} and {', '.join(lib.CHROME_LINUX)} on PATH. "
                         "Install Chromium or set CHROME_PATH (README, Running in the cloud).")
    profile = tempfile.mkdtemp(prefix="lumebook-chrome-")
    base = [lib.CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio", "--no-first-run",
            f"--user-data-dir={profile}", "--force-device-scale-factor=1", "--allow-file-access-from-files",
            "--virtual-time-budget=8000"]
    if sys.platform != "darwin":  # for Linux containers that run as root or have a small /dev/shm
        base += ["--no-sandbox", "--disable-dev-shm-usage"]
    return base + args, profile


def screenshot(url, out, width, height, attempts=2):
    # Chrome now and then exits without writing the PNG (the known hiccup: a test failed that way on 24 Oct 2026 and
    # passed on the rerun), so a missing file gets one more try with a fresh profile before it is an error.
    for attempt in range(attempts):
        cmd, profile = chrome([f"--window-size={width},{height}", f"--screenshot={out}", url])
        if out.exists():
            out.unlink()
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(160):  # Chrome sometimes writes the PNG and never exits
            time.sleep(0.25)
            if proc.poll() is not None or (out.exists() and out.stat().st_size > 0):
                time.sleep(0.4)
                break
        if proc.poll() is None:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
        if out.exists() and out.stat().st_size > 0:
            return out
    raise SystemExit(f"Chrome did not write {out}")


def dump_dom(url, width, height):
    """Chrome prints the DOM and then often never exits, so read the output file and kill it."""
    cmd, profile = chrome([f"--window-size={width},{height}", "--dump-dom", url])
    out = Path(tempfile.mkstemp(suffix=".html")[1])
    with out.open("wb") as fh:
        proc = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.DEVNULL)
        for _ in range(240):
            time.sleep(0.25)
            if proc.poll() is not None or b"</html>" in out.read_bytes():
                break
        if proc.poll() is None:
            proc.kill()
    shutil.rmtree(profile, ignore_errors=True)
    text = out.read_text(encoding="utf-8", errors="replace")
    out.unlink()
    return text


def rtl_report(html_path):
    dom = dump_dom(html_path.as_uri() + "?check=1", W, H)
    m = re.search(r'<pre id="rtl-report">(.*?)</pre>', dom, re.S)
    if not m or not m.group(1).strip():
        raise SystemExit("RTL check could not read the rendered page")
    import html as htmlmod
    report = json.loads(htmlmod.unescape(m.group(1)))
    problems = []
    for s in report:
        if s["lang"] != "he" or s["htmlDir"] != "rtl":
            problems.append(f"slide {s['n']}: page must be lang he dir rtl")
        if s["direction"] != "rtl" or s["textAlign"] not in ("right", "start", "center"):  # centred lines, as in the trial
            problems.append(f"slide {s['n']}: copy block is {s['direction']} {s['textAlign']}")
        if s["fit"] == "tight":
            problems.append(f"slide {s['n']}: even at the smallest size the text runs {-s.get('clearance', 0)}px into the picture (it has a soft panel); shorten it")
        elif s["fit"] != "ok":
            problems.append(f"slide {s['n']}: text does not fit the reserved zone even at the smallest size")
        if s.get("font") is False:   # the story look's Varela Round (assets/fonts/VarelaRound-*.woff2) did not load
            problems.append(f"slide {s['n']}: Varela Round did not load (assets/fonts/VarelaRound-*.woff2, lumebook.py sync)")
        for b in s["blocks"]:
            if b["direction"] != "rtl":
                problems.append(f"slide {s['n']}: «{b['text']}» renders {b['direction']}")
            if b["overflow"]:
                problems.append(f"slide {s['n']}: «{b['text']}» overflows its line")
    return report, problems


def rtl_sheet(report, out_dir):
    rows = []
    for s in report:
        for b in s["blocks"]:
            if b["mixed"]:
                rows.append((s["n"], b["text"]))
    if not rows:
        rows = [(0, "אין שורות שמערבבות עברית עם ספרות או אותיות לטיניות")]
    css = (CSS.replace("{heebo}", rel(FONTS / "Heebo-Black.ttf", out_dir)).replace("{assistant}", rel(FONTS / "Assistant-VariableFont_wght.ttf", out_dir))
              .replace("{rubik}", rel(FONTS / "Rubik-VariableFont_wght.ttf", out_dir)))
    items = "".join(
        f'<div style="padding:22px 0;border-bottom:2px solid #E6DCCB"><div style="font:700 24px Assistant;color:#7A7090">שקופית {n}</div>'
        f'<div style="font:900 64px Heebo;color:#1D1039;direction:rtl;text-align:right">{lines_html(t)}</div>'
        f'<div dir="ltr" style="font:20px Menlo,monospace;color:#7A7090;text-align:left">logical order: {esc(t)}</div></div>'
        for n, t in rows)
    page = out_dir / "rtl-check.html"
    page.write_text(f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>{css}body{{background:#FBF7F0;padding:60px}}</style></head>'
                    f'<body dir="rtl"><div style="font:900 40px Heebo;color:#5B2BD6">בדיקת RTL לשורות מעורבות</div>{items}</body></html>', encoding="utf-8")
    screenshot(page.as_uri(), out_dir / "rtl-check.png", W, H)
    page.unlink()


def contact_sheet(out_dir, count):
    cols = 5 if count > 8 else 4
    rows = -(-count // cols)
    figs = "".join(
        f'<figure style="margin:0"><img src="{n:02d}.png" style="width:320px;height:400px;display:block;border-radius:10px;box-shadow:0 4px 14px rgba(0,0,0,.15)">'
        f'<figcaption style="font:700 24px Menlo,monospace;color:#4B4062;margin-top:8px;text-align:center">{n:02d}</figcaption></figure>'
        for n in range(1, count + 1))
    page = out_dir / "contact-sheet.html"
    page.write_text('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"></head>'
                    f'<body style="margin:0;background:#E9E2D6;direction:rtl"><div style="display:grid;grid-template-columns:repeat({cols},320px);gap:24px 28px;padding:44px">'
                    f'{figs}</div></body></html>', encoding="utf-8")
    screenshot(page.as_uri(), out_dir / "contact-sheet.png", cols * 320 + (cols - 1) * 28 + 88, rows * 444 + (rows - 1) * 24 + 88)
    page.unlink()


def write_texts(frozen, out_dir):
    v = frozen["option"]
    story = is_story(frozen)
    (out_dir / "caption.txt").write_text(lib.with_disclaimer(v["caption"].strip()) + "\n", encoding="utf-8")   # the disclaimer since 31 Oct 2026
    src = [f"# Sources · {v['id']} · {frozen['date']}", ""]
    for s in v["sources"]:
        src += [f"- [{s['title']}]({s['url']}) · {s['publisher']} · read {s['accessed']}", f"  - supports: {s['supports']}", f"  - quote: \"{s['quote']}\""]
    src += ["", "## Product facts (live site)", ""]
    for f in frozen.get("product_facts", []):
        src.append(f"- {f['fact']} · \"{f['quote']}\" · {f['url']} · checked {f['checked_at']}")
    src += ["", "## Claims", ""]
    for c in v["claims"]:
        src.append(f"- slide {c['slide']} · {c['kind']} · {c['wording_he']} · {c['supports']} · {', '.join(c['source_ids'])}")
    (out_dir / "sources.md").write_text("\n".join(src) + "\n", encoding="utf-8")
    words = (lambda t: plain_text(t)) if story else (lambda t: t)   # story copy carries ## > ** markup
    alt = [f"{s['number']}: " + " ".join(lib.lines_of(words(s["headline"] + "\n" + s.get("body", "")))) for s in v["slides"]]
    (out_dir / "alt-text.txt").write_text("\n".join(alt) + "\n", encoding="utf-8")


def find_preview(run_dir):
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = run_dir / "real-assets" / f"preview.{ext}"
        if p.exists():
            return p
    return None


def previous_look(html_path):
    """A run already exported keeps its look when it is re-exported (edit_final.py); new runs get the clean look."""
    if not html_path.exists():
        return None
    m = re.search(r'<body[^>]*class="[^"]*look-(clean|bold|classic|story)', html_path.read_text(encoding="utf-8"))
    if not m:
        return None
    return "clean" if "look-clean" in html_path.read_text(encoding="utf-8")[:200000] else m.group(1)


def choose_look(forced, previous, v, story=False):
    """--look wins, then the look of the run's earlier export, then clean for a one-picture carousel (14 Oct 2026 on) or
    copy with highlights, else classic. Since the save for later CTA (24 Oct 2026) slide 10 has no highlight, which was the
    only one in many carousels: four re-exports that evening fell back to classic, so a one-picture run never keeps it.
    A story run (story-format.md, 29 Oct 2026) always gets the story look unless --look says otherwise, and the story
    look is never carried over to a run whose copy is not in the story format."""
    if story:
        return forced or "story"
    if previous == "story":
        previous = None
    if previous == "classic" and lib.one_picture(v):
        previous = None
    return forced or previous or ("clean" if lib.one_picture(v) or any(s.get("highlight") for s in v["slides"]) else "classic")


def story_images(run_dir, v):
    """A story run has a picture per slide (story-format.md section 4): slide N is generated-assets/slide-NN.png, the cover
    slide-01.png, each job QA-passed in state.json. A slide with no job of its own shows the cover picture."""
    state = lib.read_json(run_dir / "state.json")["jobs"]
    cover = "slide-01" if "slide-01" in state else "picture"
    job_of = {s["number"]: (f"slide-{s['number']:02d}" if f"slide-{s['number']:02d}" in state else cover) for s in v["slides"]}
    missing = sorted({j for j in job_of.values() if state.get(j, {}).get("qa") != "pass"})
    if missing:
        raise SystemExit("These images have not passed visual QA yet: " + ", ".join(missing))
    return {n: run_dir / "generated-assets" / f"{j}.png" for n, j in job_of.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--placeholders", action="store_true", help="test the layout with generated placeholder images")
    ap.add_argument("--slides", nargs="*", type=int, help="only re-export these slide numbers")
    ap.add_argument("--preview-card", action="store_true", help="place real-assets/preview.png as a card on the last slide (must not show the brand)")
    ap.add_argument("--brand-mark", action="store_true", help="add the small logo to every slide (off: carousels do not name the brand)")
    ap.add_argument("--look", choices=LOOKS, help="story (default for story packs, story-format.md, 29 Oct 2026): Varela Round on an ink veil over a picture per slide. clean (default for new runs since 14 Oct 2026): plain centred type, no highlight block or bubbles, the last slide as in bold. bold: large type, a highlighted phrase, bubbles and a comment button (default for copy written with highlights, "
                    "packs from 10 Oct 2026 18:30). classic: the 8 Oct layout (default for older copy, whose lines are too long for the large type)")
    ap.add_argument("--out", help="write to RUN_DIR/NAME instead of final/ (to compare looks without touching the export)")
    args = ap.parse_args()

    run_dir = Path(args.run_dir).resolve()
    frozen = lib.read_json(run_dir / "approved.json")
    v = frozen["option"]
    out_dir = run_dir / (args.out or ("final-placeholders" if args.placeholders else "final"))
    story = is_story(frozen)
    look = choose_look(args.look, previous_look(out_dir / "slides.html"), v, story=story)
    out_dir.mkdir(parents=True, exist_ok=True)

    images = {}
    if args.placeholders:
        ph = run_dir / "placeholders"
        for s in v["slides"]:
            images[s["number"]] = lib.write_placeholder_png(ph / f"slide-{s['number']:02d}.png", 1024, 1280, seed=s["number"])
    elif story:
        images = story_images(run_dir, v)
    else:
        state = lib.read_json(run_dir / "state.json")["jobs"]
        # One picture behind every slide (packs from 14 Oct 2026), or one picture per slide before that
        job_of = {s["number"]: "picture" if lib.one_picture(v) else f"slide-{s['number']:02d}" for s in v["slides"]}
        missing = sorted({j for j in job_of.values() if state.get(j, {}).get("qa") != "pass"})
        if missing:
            raise SystemExit("These images have not passed visual QA yet: " + ", ".join(missing))
        for n, j in job_of.items():
            images[n] = run_dir / "generated-assets" / f"{j}.png"
    preview = None
    if args.preview_card:
        preview = find_preview(run_dir)
        if not preview:
            raise SystemExit(f"--preview-card needs an image at {run_dir / 'real-assets' / 'preview.png'}")

    html_path = out_dir / "slides.html"
    if look == "story":
        page = build_story_html(frozen, images, out_dir)
    else:
        page = build_html(frozen, images, out_dir, preview, brand_mark=args.brand_mark, look=look)
    html_path.write_text(page, encoding="utf-8")
    report, problems = rtl_report(html_path)
    (out_dir / "rtl-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    which = args.slides or [s["number"] for s in v["slides"]]
    for n in which:
        out = out_dir / f"{n:02d}.png"
        screenshot(html_path.as_uri() + f"?s={n}", out, W, H)
        size = lib.png_size(out)
        if size != (W, H):
            raise SystemExit(f"{out} is {size[0]}x{size[1]}, expected {W}x{H}")
    count = len(v["slides"])
    contact_sheet(out_dir, count)
    rtl_sheet(report, out_dir)
    write_texts(frozen, out_dir)

    zip_path = out_dir / f"{frozen['date']}-{v['id']}{'-PLACEHOLDER' if args.placeholders else ''}.zip"
    log = run_dir / "generated-assets" / "generation-log.jsonl"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for n in range(1, count + 1):
            z.write(out_dir / f"{n:02d}.png", f"slides/{n:02d}.png")
        for name in ("caption.txt", "sources.md", "alt-text.txt", "contact-sheet.png", "rtl-check.png", "slides.html"):
            z.write(out_dir / name, name)
        if log.exists():
            z.write(log, "generation-log.jsonl")
        else:
            z.writestr("generation-log.jsonl", "")
    result = {"out_dir": str(out_dir), "slides": [str(out_dir / f"{n:02d}.png") for n in range(1, count + 1)],
              "zip": str(zip_path), "look": look, "rtl_problems": problems, "placeholders": args.placeholders,
              "preview": str(preview) if preview else None}
    if out_dir.name == "final" and not args.placeholders:
        import drive_export  # Yarin's Drive content folder (18 Oct 2026); queued when Drive for desktop is not set up
        dest = drive_export.export(run_dir)
        result["drive"] = str(dest) if dest else "waiting"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
