#!/usr/bin/env python3
"""Overlay the frozen Hebrew copy on the approved images and export the final carousel.

    python3 carousel/carousel-pipeline/scripts/compose_slides.py RUN_DIR
    python3 carousel/carousel-pipeline/scripts/compose_slides.py RUN_DIR --placeholders      # no paid images needed
    python3 carousel/carousel-pipeline/scripts/compose_slides.py RUN_DIR --slides 3 5         # re-export only some slides

The image model never renders Hebrew. Every word is HTML text set in Heebo and Assistant
(SIL Open Font License, in carousel/carousel-pipeline/assets/fonts), right to left.

Writes to RUN_DIR/final/ (or RUN_DIR/final-placeholders/ with --placeholders):
    slides.html          editable source, one <section class="slide" data-n="N"> per slide
    01.png ... 08.png    exactly 1080 x 1350
    contact-sheet.png    numbered overview
    rtl-check.png        every line that mixes Hebrew with digits or Latin, large, for a visual check
    rtl-report.json      computed direction and alignment of every text block, plus overflow
    caption.txt, sources.md, alt-text.txt
    DATE-OPTION.zip      slides, caption, sources, alt text, contact sheet, generation log

Carousels do not name the brand: no logo and no product card by default. --brand-mark adds the logo,
--preview-card adds real-assets/preview.png as a card on the last slide (only if it shows no brand name).

Needs Google Chrome or Chromium (carousel_lib.find_chrome). Standard library only.
"""

import argparse
import json
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


def rel(target, base):
    return Path(os.path.relpath(target, base)).as_posix()


LATIN_RUN = re.compile(r"([A-Za-z][A-Za-z0-9 .'&-]*[A-Za-z0-9]|[A-Za-z])")
SPOKEN_RE = re.compile(r"([״\"“][^״\"“”]{6,}[״\"”])")
SAVE_LINE_RE = re.compile(r"\s*ת?שמר[וי](?![א-ת])")   # the save and share CTA's first line (24 Oct 2026)
SEND_LINE_RE = re.compile(r"\s*ו?ת?שלח[וי](?![א-ת])")  # and its second line
# Instagram's save (bookmark) and send (paper plane) glyphs, drawn as outlines like the app's own
SAVE_ICON = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 3h11a1.5 1.5 0 0 1 1.5 1.5V21l-7-6.2L5 21V4.5A1.5 1.5 0 0 1 6.5 3z"/></svg>'
SEND_ICON = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M22 2.5 10.6 13.4"/><path d="M22 2.5 15 21.5l-4.4-8.1L2.5 9z"/></svg>'
LOOKS = ("clean", "bold", "classic")
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
    (out_dir / "caption.txt").write_text(v["caption"].strip() + "\n", encoding="utf-8")
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
    alt = [f"{s['number']}: " + " ".join(lib.lines_of(s["headline"] + "\n" + s.get("body", ""))) for s in v["slides"]]
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
    m = re.search(r'<body[^>]*class="[^"]*look-(clean|bold|classic)', html_path.read_text(encoding="utf-8"))
    if not m:
        return None
    return "clean" if "look-clean" in html_path.read_text(encoding="utf-8")[:200000] else m.group(1)


def choose_look(forced, previous, v):
    """--look wins, then the look of the run's earlier export, then clean for a one-picture carousel (14 Oct 2026 on) or
    copy with highlights, else classic. Since the save for later CTA (24 Oct 2026) slide 10 has no highlight, which was the
    only one in many carousels: four re-exports that evening fell back to classic, so a one-picture run never keeps it."""
    if previous == "classic" and lib.one_picture(v):
        previous = None
    return forced or previous or ("clean" if lib.one_picture(v) or any(s.get("highlight") for s in v["slides"]) else "classic")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--placeholders", action="store_true", help="test the layout with generated placeholder images")
    ap.add_argument("--slides", nargs="*", type=int, help="only re-export these slide numbers")
    ap.add_argument("--preview-card", action="store_true", help="place real-assets/preview.png as a card on the last slide (must not show the brand)")
    ap.add_argument("--brand-mark", action="store_true", help="add the small logo to every slide (off: carousels do not name the brand)")
    ap.add_argument("--look", choices=LOOKS, help="clean (default for new runs since 14 Oct 2026): plain centred type, no highlight block or bubbles, the last slide as in bold. bold: large type, a highlighted phrase, bubbles and a comment button (default for copy written with highlights, "
                    "packs from 10 Oct 2026 18:30). classic: the 8 Oct layout (default for older copy, whose lines are too long for the large type)")
    ap.add_argument("--out", help="write to RUN_DIR/NAME instead of final/ (to compare looks without touching the export)")
    args = ap.parse_args()

    run_dir = Path(args.run_dir).resolve()
    frozen = lib.read_json(run_dir / "approved.json")
    v = frozen["option"]
    out_dir = run_dir / (args.out or ("final-placeholders" if args.placeholders else "final"))
    look = choose_look(args.look, previous_look(out_dir / "slides.html"), v)
    out_dir.mkdir(parents=True, exist_ok=True)

    images = {}
    if args.placeholders:
        ph = run_dir / "placeholders"
        for s in v["slides"]:
            images[s["number"]] = lib.write_placeholder_png(ph / f"slide-{s['number']:02d}.png", 1024, 1280, seed=s["number"])
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
    html_path.write_text(build_html(frozen, images, out_dir, preview, brand_mark=args.brand_mark, look=look), encoding="utf-8")
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
