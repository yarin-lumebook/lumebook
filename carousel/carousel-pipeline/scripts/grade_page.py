#!/usr/bin/env python3
"""The grading page of a weekly batch: every carousel one at a time, a 1 to 5 grade, Yarin's reason, a produce toggle.

Served by review_server.py at /grade/<batch id>; it saves through /api/grade and sends picks with /api/produce-send
(grades.py holds the data and the rules). Design system tokens and lb- components; the slide cards use the two
pillar looks (pillars.md), the games and books carousels show their rendered PNGs.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import grades  # noqa: E402
from carousel_lib import esc  # noqa: E402

PAGE_CSS = """
@font-face{font-family:"Rubik Slide";src:url("/assets/fonts/Rubik-VariableFont_wght.ttf") format("truetype");font-weight:300 900}
@font-face{font-family:"Heebo Slide";src:url("/assets/fonts/Heebo-Black.ttf") format("truetype");font-weight:900}
.gv-wrap{display:grid;grid-template-columns:minmax(0,1fr) 18rem;gap:var(--sp-5);align-items:start}
.gv-head{display:flex;align-items:center;gap:var(--sp-2);flex-wrap:wrap;margin-bottom:var(--sp-3)}
.gv-head h2{font-size:1.375rem;font-weight:700;letter-spacing:-.015em;margin:0;margin-inline-end:var(--sp-2)}
.gv-pos{font-family:var(--font-mono);font-size:var(--fs-footnote);color:var(--text-3);direction:ltr}
.lb-chip.kid{background:var(--kid-soft);color:var(--kid)}
.lb-chip.expert{background:var(--expert-soft);color:var(--expert)}
.lb-chip.reco{background:var(--info-soft);color:var(--info)}
.gv-sub{color:var(--text-2);font-size:var(--fs-callout);margin:0 0 var(--sp-4)}
.gv-slides{display:grid;grid-template-columns:repeat(auto-fill,minmax(9rem,1fr));gap:var(--sp-3)}
.gv-card{aspect-ratio:4/5;border-radius:var(--r-lg);border:1px solid var(--line);padding:var(--sp-4);display:flex;flex-direction:column;gap:var(--sp-2);overflow:hidden;position:relative}
.gv-card .n{font-size:var(--fs-caption);font-weight:700;color:var(--text-3)}
.gv-card .h{font-weight:800;font-size:1.05rem;line-height:1.25;white-space:pre-line}
.gv-card .b{font-size:var(--fs-callout);line-height:1.4;white-space:pre-line;color:var(--text-2)}
.gv-card.first{outline:2px solid currentColor;outline-offset:-2px}
.p-kid .gv-card{background:#F8F4FF;border-color:#E3D8FB;color:#3B1D78;border-radius:var(--r-lg) var(--r-lg) var(--r-lg) var(--r-xs)}
.p-kid .gv-card .h{font-family:"Rubik Slide",var(--font)}
.p-expert .gv-card{background:#FCF7EE;border-color:#EBDCC0;color:#1D1039}
.p-expert .gv-card .h{font-family:"Heebo Slide",var(--font)}
.p-expert .gv-card .h::before{content:"";display:block;width:1.75rem;height:3px;border-radius:2px;background:#A8741F;margin-bottom:var(--sp-2)}
.gv-card.last{background:linear-gradient(160deg,#5B2BD6,#3B1D78);color:#F8F0E1;border-color:#3B1D78}
.p-expert .gv-card.last{background:#1D1039}
.gv-card.last .b,.gv-card.last .n{color:#E3D8FB}
.gv-img{display:block;padding:0;border:1px solid var(--line);border-radius:var(--r-md);overflow:hidden;background:var(--tint-soft);cursor:zoom-in;aspect-ratio:4/5}
.gv-img img{display:block;width:100%;height:100%;object-fit:cover}
.gv-story{font-size:var(--fs-footnote);color:var(--text-2);line-height:1.7;margin:var(--sp-4) 0 0}
.gv-story b{color:var(--text);margin-inline-end:var(--sp-1)}
.gv-more{margin-top:var(--sp-3)}
.gv-more summary{cursor:pointer;font-size:var(--fs-footnote);color:var(--tint)}
.gv-more pre{white-space:pre-wrap;font:inherit;font-size:var(--fs-callout);line-height:1.6;background:var(--surface-2);border-radius:var(--r-md);padding:var(--sp-3);margin:var(--sp-2) 0 0}
.gv-panel{position:sticky;top:4.25rem;display:grid;gap:var(--sp-4);box-shadow:var(--shadow-1)}
.gv-scores{display:grid;grid-template-columns:repeat(5,1fr);gap:var(--sp-1)}
.gv-scores button{border:1px solid var(--line-strong);background:var(--surface);border-radius:var(--r-md);padding:var(--sp-2) 0;font:inherit;cursor:pointer;display:grid;gap:2px;color:var(--text)}
.gv-scores button b{font-size:1.25rem;line-height:1}
.gv-scores button span{font-size:var(--fs-caption);color:var(--text-3)}
.gv-scores button[aria-pressed="true"]{background:var(--tint);border-color:var(--tint);color:var(--text-on-tint)}
.gv-scores button[aria-pressed="true"] span{color:var(--text-on-tint)}
.gv-produce{display:flex;align-items:center;gap:var(--sp-3);justify-content:space-between;padding:var(--sp-3);border-radius:var(--r-md);background:var(--surface-2)}
.gv-produce label{font-weight:600;cursor:pointer}
.gv-produce .lb-muted{font-size:var(--fs-caption)}
.gv-nav{display:grid;grid-template-columns:1fr 1fr;gap:var(--sp-2)}
.gv-nav .wide{grid-column:1/-1}
.gv-state{font-size:var(--fs-caption);color:var(--text-3);min-height:1em}
.gv-state.err{color:var(--danger)}
.gv-dots{display:flex;flex-wrap:wrap;gap:3px}
.gv-dots .sep{flex-basis:100%;height:0}
.gv-dots button{width:1.05rem;height:1.05rem;border-radius:4px;border:1px solid var(--line-strong);background:var(--surface);padding:0;cursor:pointer;font-size:9px;color:var(--text-on-tint);line-height:1}
.gv-dots button.graded{background:var(--tint);border-color:var(--tint)}
.gv-dots button.pick{box-shadow:0 0 0 2px var(--accent)}
.gv-dots button.cur{outline:2px solid var(--text);outline-offset:1px}
.gv-keys{font-size:var(--fs-caption);color:var(--text-3);line-height:1.6}
.gv-box{position:fixed;inset:0;background:var(--overlay);display:none;align-items:center;justify-content:center;z-index:70;padding:var(--sp-4)}
.gv-box.open{display:flex}
.gv-box img{max-width:min(100%,32rem);max-height:100%;border-radius:var(--r-md);box-shadow:var(--shadow-3)}
.gv-box .lb-btn{position:absolute;top:var(--sp-4);inset-inline-end:var(--sp-4)}
@media (max-width:1180px){.gv-wrap{grid-template-columns:minmax(0,1fr)}.gv-panel{position:static}.gv-slides{grid-auto-flow:column;grid-template-columns:none;grid-auto-columns:10.5rem;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:var(--sp-2)}.gv-slides>*{scroll-snap-align:start}}
"""

SCRIPT = r"""
const D = JSON.parse(document.getElementById('gv-data').textContent);
const items = D.items, G = D.grades, Q = D.queue;
let cur = 0, timer = null;
const $ = s => document.querySelector(s);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const KIND = {kid: 'הילד מספר', expert: 'גישה מקצועית', reco: 'משחקים וספרים'};

function g(key) { return G[key] || {}; }
function counts() {
  const graded = items.filter(i => g(i.key).score).length;
  const picks = items.filter(i => g(i.key).produce && !g(i.key).sent_at).length;
  $('#gv-count').textContent = `דורגו ${graded} מתוך ${items.length}`;
  const b = $('#gv-send'); b.textContent = picks ? `הפקת הנבחרים (${picks})` : 'הפקת הנבחרים'; b.disabled = !picks;
}
function dots() {
  const box = $('#gv-dots'); box.textContent = '';
  let slot = null;
  items.forEach((it, i) => {
    if (slot !== null && it.slot !== slot) box.append(el('span', 'sep'));
    slot = it.slot;
    const b = el('button');
    const s = g(it.key);
    b.className = (s.score ? 'graded' : '') + (s.produce ? ' pick' : '') + (i === cur ? ' cur' : '');
    b.textContent = s.score || '';
    b.title = `${i + 1} · ${it.topic_he} · ${it.id}${s.score ? ' · ' + s.score : ''}`;
    b.onclick = () => go(i);
    box.append(b);
  });
}
function show() {
  const it = items[cur], s = g(it.key);
  history.replaceState(null, '', '#' + it.key);
  const main = $('#gv-main'); main.textContent = '';
  main.className = 'p-' + it.kind;
  const head = el('div', 'gv-head');
  head.append(el('span', 'gv-pos', `${cur + 1}/${items.length}`), el('h2', null, it.topic_he));
  head.append(el('span', 'lb-chip ' + it.kind, KIND[it.kind]));
  head.append(el('span', 'lb-chip', it.kind === 'reco' ? (it.id === 'reco' ? 'קרוסלה 1' : 'קרוסלה 2') : it.id));
  if (it.child_name) head.append(el('span', 'lb-chip', it.child_name));
  if (it.skill_he) head.append(el('span', 'lb-chip', it.skill_he + (it.ages ? ' · ' + it.ages : '')));
  if (it.event) head.append(el('span', 'lb-chip warning', 'אירוע · ' + it.event));
  const q = Q[it.key];
  if (q) { const a = el('a', 'lb-chip ' + (q.status === 'done' ? 'success' : q.status === 'failed' ? 'danger' : 'accent'), q.status_he || q.status); a.href = '/productions#' + it.key; head.append(a); }
  main.append(head);
  main.append(el('p', 'gv-sub', it.title));
  const grid = el('div', 'gv-slides');
  if (it.images && it.images.length) {
    it.images.forEach((src, n) => {
      const b = el('button', 'gv-img'); b.type = 'button';
      const img = el('img'); img.src = src; img.alt = 'שקופית ' + (n + 1); img.loading = n < 4 ? 'eager' : 'lazy';
      b.append(img); b.onclick = () => zoom(n); grid.append(b);
    });
  } else {
    it.slides.forEach((sl, n) => {
      const c = el('div', 'gv-card' + (n === 0 ? ' first' : '') + (n === it.slides.length - 1 ? ' last' : ''));
      c.append(el('span', 'n', n === 0 ? '1 · שער' : String(sl.n)), el('div', 'h', sl.headline));
      if (sl.body) c.append(el('div', 'b', sl.body));
      grid.append(c);
    });
  }
  main.append(grid);
  if (it.kind !== 'reco') {
    const p = el('p', 'gv-story'); p.append(el('b', null, 'הכותרות בלבד'), document.createTextNode(it.headlines.join(' ← ')));
    main.append(p);
  } else if (it.products && it.products.length) {
    const p = el('p', 'gv-story'); p.append(el('b', null, 'מה בפנים'), document.createTextNode(it.products.join(' · ')));
    main.append(p);
  }
  if (it.caption) {
    const d = el('details', 'gv-more'); d.append(el('summary', null, 'כיתוב'), el('pre', null, it.caption)); main.append(d);
  }
  const page = it.kind === 'reco' ? `/drafts/${it.date}/${it.id === 'reco' ? 'reco.html' : 'reco-2.html'}` : `/drafts/${it.date}/review.html#${it.id}`;
  $('#gv-edit').href = page;
  document.querySelectorAll('.gv-scores button').forEach(b => b.setAttribute('aria-pressed', String(Number(b.dataset.s) === s.score)));
  $('#gv-why').value = s.why || '';
  $('#gv-pick').checked = !!s.produce;
  $('#gv-pick-note').textContent = s.sent_at ? 'נשלח להפקה' : (it.kind === 'reco' ? 'ייצוא השקופיות והכיתוב, בלי עלות' : 'תמונה אחת והפקה, עד $0.50');
  state('');
  dots(); counts();
  window.scrollTo({top: 0});
}
function state(msg, err) { const s = $('#gv-state'); s.textContent = msg; s.classList.toggle('err', !!err); }
async function save(fields) {
  const it = items[cur];
  state('שומר...');
  try {
    const r = await fetch('/api/grade', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({batch: D.batch, key: it.key, ...fields})});
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || r.status);
    G[it.key] = j.entry; state('נשמר'); dots(); counts();
  } catch (e) { state('לא נשמר: ' + e.message, true); }
}
function flushWhy() {
  if (!timer) return;
  clearTimeout(timer); timer = null;
  save({why: $('#gv-why').value});
}
function go(i) {
  flushWhy();
  if (i < 0 || i >= items.length) return;
  cur = i; show();
}
function nextOpen() {
  for (let k = 1; k <= items.length; k++) { const i = (cur + k) % items.length; if (!g(items[i].key).score) return go(i); }
  hsToast('הכול דורג');
}
function zoom(n) {
  const it = items[cur]; if (!it.images) return;
  zoom.n = (n + it.images.length) % it.images.length;
  $('#gv-box img').src = it.images[zoom.n]; $('#gv-box').classList.add('open');
}
function unzoom() { $('#gv-box').classList.remove('open'); }
async function send() {
  flushWhy();
  const b = $('#gv-send'); b.disabled = true;
  try {
    const j = await hsPost('/api/produce-send', {batch: D.batch});
    Object.assign(G, j.grades); j.started.forEach(r => Q[r.key] = r);
    hsToast(j.started.length ? `${j.started.length} נשלחו להפקה. ההתקדמות בדף ״הפקות״` : 'אין מה לשלוח');
    show();
  } catch (e) { hsToast('השליחה נכשלה: ' + e.message); counts(); }
}

document.querySelectorAll('.gv-scores button').forEach(b => b.onclick = () => {
  const s = Number(b.dataset.s);
  document.querySelectorAll('.gv-scores button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  save({score: s});
});
$('#gv-why').addEventListener('input', () => { clearTimeout(timer); state('...'); timer = setTimeout(() => { timer = null; save({why: $('#gv-why').value}); }, 700); });
$('#gv-why').addEventListener('blur', flushWhy);
$('#gv-pick').onchange = e => save({produce: e.target.checked});
$('#gv-prev').onclick = () => go(cur - 1);
$('#gv-next').onclick = () => go(cur + 1);
$('#gv-open').onclick = nextOpen;
$('#gv-send').onclick = send;
$('#gv-box').onclick = e => { if (e.target.id === 'gv-box' || e.target.dataset.close != null) unzoom(); else zoom(zoom.n + 1); };
document.addEventListener('keydown', e => {
  if ($('#gv-box').classList.contains('open')) {
    if (e.key === 'Escape') unzoom(); else if (e.key === 'ArrowLeft') zoom(zoom.n + 1); else if (e.key === 'ArrowRight') zoom(zoom.n - 1);
    return;
  }
  if (e.target.matches('textarea, input[type=text]') || e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === 'ArrowLeft') go(cur + 1);
  else if (e.key === 'ArrowRight') go(cur - 1);
  else if ('12345'.includes(e.key) && e.key.length === 1) document.querySelector(`.gv-scores button[data-s="${e.key}"]`).click();
  else if (e.key === 'p' || e.key === 'פ') $('#gv-pick').click();
  else if (e.key === 'w' || e.key === "'") { e.preventDefault(); $('#gv-why').focus(); }
});
window.addEventListener('beforeunload', flushWhy);
const start = items.findIndex(i => '#' + i.key === decodeURIComponent(location.hash));
cur = start >= 0 ? start : Math.max(0, items.findIndex(i => !g(i.key).score));
show();
"""


def page(plan, drafts=None, grades_path=None, productions_path=None):
    import producer
    import studio
    its = grades.items(plan, drafts)
    stored = grades.load(grades_path)["grades"]
    keys = {i["key"] for i in its}
    runs = producer.load(productions_path)["runs"]
    queue = {k: {"status": r.get("status"), "status_he": r.get("status_he")} for k, r in runs.items() if k in keys}
    data = {"batch": plan["id"], "items": its, "grades": {k: v for k, v in stored.items() if k in keys}, "queue": queue}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    scores = "".join(f'<button type="button" data-s="{s}" aria-pressed="false"><b>{s}</b><span>{esc(grades.SCORE_HE[s])}</span></button>' for s in grades.SCORES)
    if not its:
        return studio.page("דירוג", "grade", '<p class="lb-empty">אין עדיין קרוסלות בשבוע הזה.</p>')
    body = ('<div class="gv-wrap"><section id="gv-main"></section>'
            '<aside class="lb-card gv-panel" aria-label="דירוג">'
            f'<div class="lb-field">ציון<div class="gv-scores">{scores}</div></div>'
            '<label class="lb-field">למה? מה עובד, מה לא, מה היית משנה'
            '<textarea class="lb-textarea" id="gv-why" rows="5" dir="rtl" placeholder="הפתיח תופס כי... / הייתי מוריד את..."></textarea></label>'
            '<div class="gv-produce"><div><label for="gv-pick">להפקה</label><div class="lb-muted" id="gv-pick-note"></div></div>'
            '<input class="lb-switch" type="checkbox" id="gv-pick" aria-label="להפקה"></div>'
            '<div class="gv-state" id="gv-state" aria-live="polite"></div>'
            '<div class="gv-nav"><button class="lb-btn secondary" type="button" id="gv-prev">הקודם</button>'
            '<button class="lb-btn" type="button" id="gv-next">הבא</button>'
            '<button class="lb-btn ghost wide" type="button" id="gv-open">הבא שעוד לא דורג</button>'
            '<a class="lb-btn ghost wide" id="gv-edit" href="#">פתיחה לעריכה</a></div>'
            '<div class="gv-dots" id="gv-dots" aria-label="כל הקרוסלות"></div>'
            '<p class="gv-keys">מקשים: חצים לניווט, 1 עד 5 לציון, P להפקה, W לכתיבה</p>'
            '</aside></div>'
            '<div class="gv-box" id="gv-box"><button class="lb-btn secondary sm" type="button" data-close>סגירה</button><img alt=""></div>'
            f'<script type="application/json" id="gv-data">{blob}</script>')
    actions = ('<span class="lb-chip" id="gv-count"></span>'
               '<button class="lb-btn sm" type="button" id="gv-send" disabled>הפקת הנבחרים</button>')
    return studio.page("דירוג", "grade", body, actions=actions, css=PAGE_CSS, script=SCRIPT,
                       subtitle="קרוסלה אחת בכל פעם. ציון, הסבר קצר, ומה להפיק. הכול נשמר לבד.")
