#!/usr/bin/env python3
"""Turn a pack.json into review.html (main) and review.md (portable fallback).

    python3 carousel/carousel-pipeline/scripts/create_review.py PATH/pack.json

Right to left: lang="he" dir="rtl", direction rtl, right aligned. The page chrome uses the LumeBook design system
(shared/design: tokens, lb- components, light by default with a dark toggle), inlined so the file stands alone.
Each option is one card: who it is about, the strategy in one row, the slide previews as editable cards, caption
and CTA, and two dropdowns (claims and sources, image descriptions). The page never picks a winner.

The slide previews keep the carousel's own look (PILLARS: kid violet and Rubik, expert gold and Heebo Black) in
both themes; only the chrome around them follows the design system.

Served by review_server.py the copy is editable and saved back to pack.json; opened as a file it is read only.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
from carousel_lib import esc  # noqa: E402


def _project_root():
    for folder in Path(__file__).resolve().parents:
        if (folder / "lumebook.json").exists():
            return folder
    raise SystemExit("create_review.py: no lumebook.json above this script, so the LumeBook project root is unknown")


ROOT = _project_root()
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402


def hub_url():
    """The HQ dashboard artifact (shared/facts.json links.hq_artifact)."""
    try:
        return json.loads((ROOT / "shared" / "facts.json").read_text(encoding="utf-8"))["links"]["hq_artifact"]
    except (OSError, ValueError, KeyError):
        return "https://claude.ai/artifact/3y8LwbxtTNQW2HAL479aSQ"


# The slide previews: the carousel's audience-facing look, fixed in both themes and kept exactly as it was.
# Everything they read is pinned on .deck (colours, the inherited font, size and line height), so neither the
# design system's tokens nor the theme reach them. The local Heebo Black file is registered as "Heebo Slide":
# the design system loads Heebo 400 to 800 from Google Fonts, and the previews must keep rendering every Heebo
# weight in the Black cut, as they always have.
SLIDE_CSS = """
@font-face{font-family:"Rubik";src:url("../../assets/fonts/Rubik-VariableFont_wght.ttf") format("truetype");font-weight:300 900}
@font-face{font-family:"Heebo Slide";src:url("../../assets/fonts/Heebo-Black.ttf") format("truetype");font-weight:900}
.p-kid{--p:#5B2BD6;--p-soft:#F1EBFF;--p-card:#F8F4FF;--p-deep:#3B1D78;--p-font:"Rubik";--p-cta:#3B1D78;--p-cta2:#5B2BD6}
.p-expert{--p:#A8741F;--p-soft:#F8EEDC;--p-card:#FCF7EE;--p-deep:#1D1039;--p-font:"Heebo Slide";--p-cta:#1D1039;--p-cta2:#1D1039}
.deck{--ink:#1D1039;--ink2:#4B4062;--muted:#7D7491;--line:#E7DFD2;--violet:#5B2BD6;--violet-soft:#F0EAFF;--cream:#FBF6EE;color-scheme:light;color:#1D1039;font-family:"Heebo Slide","Assistant",-apple-system,"SF Hebrew","Arial Hebrew",sans-serif;font-size:16px;line-height:1.55;font-weight:400;-webkit-font-smoothing:auto}
.hstory{font-size:13px;line-height:1.7;color:#4B4062;margin:8px 2px 0}.hstory b{color:#1D1039;margin-inline-end:6px}
.deck{display:grid;grid-template-columns:repeat(7,minmax(150px,1fr));gap:10px;overflow-x:auto;padding-bottom:4px;scroll-snap-type:x proximity}
.deck .card{scroll-snap-align:start}
.card{background:var(--p-card,var(--cream));border:1px solid var(--line);border-radius:14px;padding:12px 12px 10px;display:flex;flex-direction:column;gap:6px;min-height:200px;direction:rtl;text-align:right}
.card.cta{background:linear-gradient(160deg,var(--p-cta2),var(--p-cta));color:#F8F0E1;border-color:var(--p-cta)}
.p-kid .card:not(.cta){border-radius:18px 18px 18px 4px;border-color:#E3D8FB}
.p-expert .card:not(.cta) .h::before{content:"";display:block;width:28px;height:3px;border-radius:2px;background:var(--p);margin-bottom:6px}
.card .n{font-size:11px;font-weight:700;color:var(--muted);display:flex;justify-content:space-between;gap:6px}
.card.cta .n{color:#C9BFE0}
.card .h{font-family:var(--p-font),"Heebo Slide",sans-serif;font-weight:800;font-size:17px;line-height:1.2;white-space:pre-line;color:var(--p-deep,var(--ink))}
.card.cta .h{color:#F8F0E1}
.card .b{font-size:14px;line-height:1.4;white-space:pre-line;color:var(--ink2)}
.card .hlrow{margin-top:auto;display:flex;align-items:center;gap:6px;font-size:11px;color:var(--muted)}
.card .hlrow .hl{background:var(--p,var(--violet));color:#fff;border-radius:6px;padding:1px 7px;font-size:12px;font-weight:700;min-width:2em}
.card.cta .b{color:#F8F0E1}
.card .pull{margin-top:auto;font-size:11px;color:var(--p-deep,var(--violet));background:var(--p-soft,var(--violet-soft));border-radius:8px;padding:4px 7px;line-height:1.35}
.card .wc{font-size:11px;color:var(--muted)}
.b:empty{display:none}
body.editing .deck [data-edit]{outline:1.5px dashed rgba(91,43,214,.45);outline-offset:3px;border-radius:6px}
body.editing .deck [data-edit]:focus{outline:2px solid var(--violet);background:rgba(240,234,255,.6)}
body.editing .deck .card.cta [data-edit]:focus{background:rgba(255,255,255,.08)}
body.editing .card .b:empty{display:block}
body.editing .card .b[data-edit]:empty::before{content:"שורות גוף (לא חובה)";opacity:.45}
@media (max-width:760px){.deck{grid-template-columns:repeat(7,150px)}}
"""

# The chrome: design system tokens only. The old variable names stay as aliases because reco_render.py injects
# the games and books section into this page and styles it with them (and with .chip, .opt-head, .strategy,
# .post, .caption, details.more, .direction-head, .sym, .oid, h4 and plain tables).
PAGE_CSS = """
:root{--card:var(--surface);--soft:var(--surface-2);--ink:var(--text);--ink2:var(--text-2);--muted:var(--text-3);--violet:var(--tint);--violet-soft:var(--tint-soft);--gold:var(--accent);--gold-soft:var(--accent-soft);--cream:var(--surface-2);--ok:var(--success);--bad:var(--danger);--content-w:79.25rem;--rv-sticky:4.75rem}
[hidden]{display:none !important}
body{direction:rtl;text-align:right}
body.editing{--rv-sticky:7.75rem}
[id]{scroll-margin-top:var(--rv-sticky)}
.wrap{width:100%;max-width:var(--content-w);margin-inline:auto;padding:var(--sp-5) var(--sp-5) var(--sp-7);display:grid;gap:var(--sp-6)}
.lb-page,.wrap{grid-template-columns:minmax(0,1fr)}
.rv-topbar .lb-topbar-in{gap:var(--sp-3)}
.rv-logo{width:28px;height:28px;border-radius:var(--r-xs);flex:none;display:block}
.rv-name{font-weight:800;font-size:1.0625rem;letter-spacing:-.01em;white-space:nowrap;color:var(--text)}
nav.jump{display:flex;align-items:center;gap:var(--sp-1);overflow-x:auto;scrollbar-width:none;min-width:0;flex:0 1 auto;padding-block:var(--sp-2)}
nav.jump::-webkit-scrollbar{display:none}
.drops{display:grid;gap:var(--sp-2)}
.drops>details.more{margin-top:0}
.rp-list{margin:0;padding-inline-start:1.1rem;display:grid;gap:var(--sp-1)}
.top>.row h1{margin-inline-end:auto}
.direction-head{padding:var(--sp-2) var(--sp-4)}
.rv-tabs{margin-bottom:calc(-1 * var(--sp-3));flex-wrap:wrap;row-gap:var(--sp-1)}
.rv-days{margin-inline-start:auto;display:flex;gap:var(--sp-2);align-items:center;font-size:var(--fs-footnote)}
.rv-days a{color:var(--text-3);text-decoration:none;padding:2px 8px;border-radius:999px}
.rv-days a[aria-current]{background:var(--surface-2);color:var(--text);font-weight:700}
.post .cta-box{align-self:start}
nav.jump .label{flex:none;font-size:var(--fs-caption);font-weight:600;color:var(--text-3);margin-inline-end:var(--sp-1)}
nav.jump a{flex:none;padding:.3rem .7rem;border-radius:var(--r-pill);color:var(--text);font-size:var(--fs-footnote);font-weight:600;white-space:nowrap}
nav.jump a:hover{background:var(--fill-2);color:var(--text);text-decoration:none}
nav.jump a span{color:var(--text-3);font-weight:400}
nav.jump .grp{flex:none;display:flex;align-items:center;gap:2px;padding:2px;border-radius:var(--r-pill);background:var(--pill-soft,var(--fill))}
nav.jump .grp a:hover{background:var(--surface)}
nav.jump .grp .dot{width:.5rem;height:.5rem;border-radius:50%;background:var(--pill,var(--text-3));margin-inline:var(--sp-2) var(--sp-1);flex:none}
.editbar{max-width:var(--content-w);margin-inline:auto;padding:var(--sp-2) var(--sp-5);display:flex;flex-wrap:wrap;align-items:center;gap:var(--sp-2) var(--sp-3);border-top:1px solid var(--line)}
.editbar .msg{flex:1 1 12rem;min-width:0;font-size:var(--fs-footnote);color:var(--text-2)}
@media (max-width:860px){
  :root{--rv-sticky:6rem}
  body.editing{--rv-sticky:11rem}
  .rv-topbar .lb-topbar-in{flex-wrap:wrap;row-gap:0;padding-top:var(--sp-2)}
  .rv-topbar nav.jump{order:5;flex-basis:100%;padding-block:0 var(--sp-2)}
  .editbar{padding-inline:var(--sp-4)}
}
@media (max-width:420px){.rv-topbar .lb-theme-label{display:none}}
.p-kid{--pill:var(--kid);--pill-soft:var(--kid-soft)}
.p-expert{--pill:var(--expert);--pill-soft:var(--expert-soft)}
.top{display:grid;gap:var(--sp-3);min-width:0}
.lead{color:var(--text-2);max-width:80ch;font-size:var(--fs-callout)}
.row{display:flex;flex-wrap:wrap;gap:var(--sp-2);align-items:center}
.chip{display:inline-flex;align-items:center;gap:.375rem;padding:.15rem .6rem;border-radius:var(--r-pill);font-size:var(--fs-footnote);font-weight:500;line-height:1.5;white-space:nowrap;background:var(--fill);color:var(--text-2)}
.chip.violet{background:var(--tint-soft);color:var(--tint)}
.chip.gold{background:var(--accent-soft);color:var(--accent-ink)}
.chip.warn{background:var(--warning-soft);color:var(--warning)}
.chip.ok{background:var(--success-soft);color:var(--success)}
.oid{font-family:var(--font-mono);direction:ltr;unicode-bidi:isolate;font-weight:700;background:var(--p,var(--text));color:var(--lb-cream);border-radius:var(--r-xs);padding:.1rem .55rem;font-size:var(--fs-footnote)}
.rv-id{font-family:var(--font-mono);font-weight:700;direction:ltr;unicode-bidi:isolate}
.steps{display:flex;flex-wrap:wrap;gap:var(--sp-2);margin:0;padding:0;list-style:none}
.steps li{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-sm);padding:var(--sp-1) var(--sp-3);font-size:var(--fs-footnote);color:var(--text-2)}
.legend{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr));gap:var(--sp-3)}
.legend a{display:flex;align-items:center;gap:var(--sp-3);padding:var(--sp-3) var(--sp-4);border-radius:var(--r-md);background:var(--pill-soft,var(--surface-2));color:var(--text);font-size:var(--fs-callout);text-decoration:none}
.legend a:hover{color:var(--text);text-decoration:none;box-shadow:inset 0 0 0 1px var(--pill,var(--line-strong))}
.legend a b{color:var(--pill,var(--text));font-weight:700;white-space:nowrap}
.legend a>span:not(.sym){color:var(--text-2)}
.sym{display:inline-grid;place-items:center;width:1.75rem;height:1.75rem;border-radius:50%;background:var(--p,var(--text));color:var(--lb-cream);font-weight:800;font-size:1rem;line-height:1;flex:none}
.p-kid .sym,.p-expert .sym{background:var(--pill);color:var(--text-on-tint)}
.direction{gap:var(--sp-5)}
.direction-head{display:flex;flex-wrap:wrap;align-items:center;gap:var(--sp-2) var(--sp-3);padding:var(--sp-3) var(--sp-4);border-radius:var(--r-lg);background:var(--pill-soft,var(--surface-2));border-inline-start:4px solid var(--pill,var(--text))}
.direction-head>div{flex:1 1 14rem;min-width:0}
.direction-head .sym{width:2.25rem;height:2.25rem;font-size:1.25rem}
.direction-head h2{color:var(--text)}
.direction-head p{color:var(--text-2);font-size:var(--fs-callout)}
.direction-head .count{flex:none}
.option{background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--pill,var(--line-strong));border-radius:var(--r-lg);padding:var(--sp-4) var(--sp-5);display:grid;grid-template-columns:minmax(0,1fr);gap:var(--sp-3);min-width:0;box-shadow:var(--shadow-1)}
.option>*{margin:0}
.opt-head{display:flex;flex-wrap:wrap;gap:var(--sp-2);align-items:center}
.opt-head h3{margin-inline-end:auto;color:var(--text)}
.strategy{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,14.5rem),1fr));gap:var(--sp-3)}
.strategy>div{background:var(--surface-2);border-radius:var(--r-md);padding:var(--sp-2) var(--sp-3);font-size:var(--fs-callout);color:var(--text-2)}
.strategy b{display:block;font-size:var(--fs-footnote);font-weight:600;color:var(--text-3);margin-bottom:2px}
h4{margin:0 0 var(--sp-1);font-size:var(--fs-footnote);font-weight:600;color:var(--text-3)}
.post{display:grid;grid-template-columns:2fr 1fr;gap:var(--sp-3)}
.caption{background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);white-space:pre-line;font-size:var(--fs-callout)}
.cap-cta{margin-top:var(--sp-2);color:var(--text-3)}
.cta-box{background:var(--pill-soft,var(--surface-2));color:var(--text);border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);font-weight:600;font-size:var(--fs-callout);display:flex;flex-direction:column;gap:var(--sp-2)}
.cta-box .code{align-self:flex-start}
details.more{margin-top:var(--sp-3);border:1px solid var(--line);border-radius:var(--r-md);background:var(--surface);min-width:0}
details.more>summary{cursor:pointer;min-height:2.75rem;padding:var(--sp-2) var(--sp-4);font-weight:600;font-size:var(--fs-callout);color:var(--text);list-style:none;display:flex;justify-content:space-between;align-items:center;gap:var(--sp-3)}
details.more>summary:hover{color:var(--tint)}
details.more>summary::-webkit-details-marker{display:none}
details.more>summary::after{content:"";flex:none;width:.5rem;height:.5rem;border-right:2px solid var(--text-3);border-bottom:2px solid var(--text-3);transform:translateY(-2px) rotate(45deg);transition:transform .15s}
details.more[open]>summary::after{transform:translateY(2px) rotate(-135deg)}
details.more>.inner{padding:0 var(--sp-4) var(--sp-4);overflow-wrap:anywhere}
.wrap>details.more,.lb-page>details.more,.top>details.more{margin-top:0}
table{width:100%;border-collapse:collapse;font-size:var(--fs-footnote)}
th,td{border-bottom:1px solid var(--line);padding:var(--sp-2);vertical-align:top;text-align:right;overflow-wrap:anywhere}
th{color:var(--text-3);font-size:var(--fs-caption);font-weight:500;background:var(--surface-2);overflow-wrap:normal}
tbody tr:last-child td{border-bottom:0}
td.en,.en{direction:ltr;text-align:left}
.kind{font-size:var(--fs-caption);font-weight:600;white-space:nowrap}
.kind.sourced_fact{color:var(--success)}.kind.product_fact{color:var(--tint)}.kind.lumebook_wording{color:var(--text-3)}
blockquote{overflow-wrap:anywhere;margin:var(--sp-1) 0 var(--sp-2);padding:var(--sp-2) var(--sp-3);border-inline-start:3px solid var(--accent);border-radius:var(--r-xs);background:var(--surface-2);color:var(--text-2);direction:ltr;text-align:left;font-size:var(--fs-caption)}
.src{font-size:var(--fs-footnote);margin:var(--sp-2) 0 0}
.anchor{direction:ltr;text-align:left;white-space:pre-wrap;font-family:var(--font-mono);font-size:var(--fs-caption);background:var(--surface-sunk);border-radius:var(--r-sm);padding:var(--sp-2) var(--sp-3);margin:0 0 var(--sp-2)}
.prompt{direction:ltr;text-align:left;white-space:pre-wrap;font-family:var(--font-mono);font-size:.6875rem;line-height:1.45;color:var(--text-2)}
.result{border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);border:1px solid var(--line);background:var(--surface);font-size:var(--fs-callout)}
.result.ok{background:var(--success-soft);border-color:transparent}
.result.bad{background:var(--danger-soft);border-color:transparent}
.result ul{margin:var(--sp-2) 0 0;padding-inline-start:1.25rem;display:grid;gap:var(--sp-1)}
.result a{cursor:pointer}
.edit-note{font-size:var(--fs-footnote);color:var(--text-3);line-height:1.5;margin:0}
.edit-note code{direction:ltr;unicode-bidi:isolate}
body.editing [data-edit]{outline:1.5px dashed var(--focus);outline-offset:3px;border-radius:var(--r-xs);cursor:text;min-height:1.2em}
body.editing [data-edit]:focus{outline:2px solid var(--tint);background:var(--tint-soft)}
.has-error{outline:2.5px solid var(--danger) !important;outline-offset:3px}
.lb-page>.reco-wrap{margin-top:0}
.reco .opt-head h3{color:var(--text)}
body .reco .oid{background:var(--p-deep,var(--lb-ink)) !important}
body .reco .chip.bad{background:var(--danger-soft);color:var(--danger)}
body .reco .flags li.w{color:var(--warning)}
body.editing .reco [data-reco]{outline-color:var(--focus)}
body.editing .reco [data-reco]:focus{outline-color:var(--tint);background:var(--tint-soft)}
@media (max-width:760px){.post{grid-template-columns:1fr}table{table-layout:fixed}th{overflow-wrap:anywhere}.kind{white-space:normal}}
@media (max-width:640px){.option{padding:var(--sp-3) var(--sp-4)}.wrap{padding-inline:var(--sp-4)}}
"""

# reco_render.standalone_page() inlines CSS on its own (no design.head()), so CSS carries the design system too.
CSS = design.css() + SLIDE_CSS + PAGE_CSS

SCRIPT = r"""
// ---- Editing: enabled only when the page is served by review_server.py ----
const CHAR_HE = {',': 'פסיק', '.': 'נקודה', '—': 'מקף ארוך', '–': 'מקף', '…': 'שלוש נקודות', '，': 'פסיק', '―': 'מקף ארוך'};
const FIELD_HE = {headline: 'כותרת', body: 'גוף', caption: 'כיתוב', cta: 'קריאה לפעולה', title: 'שם', code_word: 'מילת קוד', child_name: 'שם הילד', claims: 'מקורות', hook: 'פתיח', highlight: 'הדגשה'};
const EDIT = {orig: new Map()};
function textOf(el) { return el.innerText.replace(/ /g, ' ').split('\n').map(x => x.trim()).filter(Boolean).join('\n'); }
function changed() { const out = []; EDIT.orig.forEach((o, el) => { const now = textOf(el); if (now !== o) out.push({el, now}); }); return out; }
function setMsg(t) { document.getElementById('edit-msg').textContent = t; }
function labelFor(path) {
  const parts = path.split('/'); let where = parts[1] || '';
  const slide = (path.match(/slide-(\d+)/) || [])[1]; if (slide) where += ' · שקופית ' + slide;
  const field = parts[parts.length - 1]; if (FIELD_HE[field]) where += ' · ' + FIELD_HE[field];
  return where;
}
function heMessage(i) {
  if (i.char) return (CHAR_HE[i.char] || 'סימן אסור') + ' בשורה ' + i.line + ' (צריך לשכתב את השורה, לא רק למחוק)';
  return i.message;
}
function targetFor(path) {
  return document.querySelector('[data-path="' + path + '"]') || document.querySelector('[data-path="' + path.split('/').slice(0, 3).join('/') + '"]') || document.getElementById(path.split('/')[1]);
}
function showResult(res) {
  const box = document.getElementById('save-result'); box.hidden = false;
  if (res.error) { box.className = 'result bad'; box.textContent = 'השמירה נכשלה: ' + res.error; return; }
  const errs = res.errors || [];
  box.className = 'result ' + (errs.length ? 'bad' : 'ok');
  let html = res.changed ? ('נשמר (' + res.changed + ' שדות). ') : '';
  html += errs.length ? ('יש ' + errs.length + ' דברים לתקן לפני שאפשר להפיק:') : 'הכול תקין ומוכן להפקה.';
  if (res.voice_logged) html += ' <span class="edit-note">השינויים נשמרו ללמידת הקול (' + res.voice_samples + ' מתוך ' + res.voice_required + ' דוגמאות לכיול).</span>';
  const ul = document.createElement('ul');
  errs.forEach(i => {
    const li = document.createElement('li'); const a = document.createElement('a');
    a.textContent = labelFor(i.path) + ': ' + heMessage(i);
    const t = targetFor(i.path);
    if (t) {
      t.classList.add('has-error');
      a.onclick = () => { const d = t.closest('details'); if (d) d.open = true; t.scrollIntoView({behavior: 'smooth', block: 'center'}); };
    }
    li.appendChild(a); ul.appendChild(li);
  });
  box.innerHTML = html; if (errs.length) box.appendChild(ul);
}
async function saveEdits() {
  const ch = changed();
  if (!ch.length) { setMsg('אין שינויים לשמור'); return; }
  setMsg('שומר...');
  const edits = ch.map(({el, now}) => ({option: el.dataset.opt, field: el.dataset.edit, slide: el.dataset.slide ? Number(el.dataset.slide) : null, value: now}));
  let res;
  try {
    const r = await fetch('/api/save', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({date: document.body.dataset.date, edits})});
    res = await r.json();
  } catch (e) { setMsg('השמירה נכשלה: העורך לא רץ?'); return; }
  try { sessionStorage.setItem('lumebook-save-result', JSON.stringify(res)); } catch (e) {}
  EDIT.orig.clear();
  location.reload();
}
async function enableEditing() {
  try { const r = await fetch('/api/ping', {cache: 'no-store'}); if (!r.ok) throw new Error(); }
  catch (e) { return; }  // read only when opened as a file; no hint text (Yarin wants the page minimal)
  document.body.classList.add('editing');
  document.querySelectorAll('[data-edit]').forEach(el => {
    try { el.contentEditable = 'plaintext-only'; } catch (e) { el.contentEditable = 'true'; }
    if (el.contentEditable !== 'plaintext-only') el.contentEditable = 'true';
    EDIT.orig.set(el, textOf(el));
  });
  document.getElementById('editbar').hidden = false;
  document.querySelector('#editbar .save').onclick = saveEdits;
  document.querySelector('#editbar .undo').onclick = () => { if (!changed().length || confirm('לבטל את השינויים שלא נשמרו?')) { EDIT.orig.clear(); location.reload(); } };
  document.addEventListener('input', e => { if (e.target.closest('[data-edit]')) setMsg(changed().length + ' שדות שונו, עוד לא נשמרו'); });
  document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); saveEdits(); } });
  window.addEventListener('beforeunload', e => { if (changed().length) { e.preventDefault(); e.returnValue = ''; } });
  let stored = null; try { stored = sessionStorage.getItem('lumebook-save-result'); sessionStorage.removeItem('lumebook-save-result'); } catch (e) {}
  if (stored) showResult(JSON.parse(stored));
}
enableEditing();
"""


def word_count(slide):
    return len(lib.words(slide["headline"])) + len(lib.words(slide.get("body", "")))


def source_lookup(pack, version):
    table = {s["id"]: s for s in version.get("sources", [])}
    for f in pack.get("product_facts", []):
        table[f["id"]] = {"id": f["id"], "title": "lumebook.com", "publisher": "LumeBook (live site)", "url": f["url"], "quote": f["quote"], "supports": f["fact"], "accessed": f["checked_at"]}
    return table


def person_line(v):
    gender = v.get("child_gender")
    talks = "מדברת" if gender == "girl" else "מדבר"
    return f'{esc(v.get("child_name", ""))} · {"בת" if gender == "girl" else "בן"} · {talks} {esc(lib.ADDRESSEES.get(v.get("addressee"), ""))}'


def html_card(direction, v, s):
    n = s["number"]
    sp = f'{direction}/{esc(v["id"])}/slide-{n}'
    edit = f'data-opt="{esc(v["id"])}" data-slide="{n}"'
    is_last = n == len(v["slides"])
    if is_last:
        body = f'<div class="b" data-path="{sp}/body" title="נגזר אוטומטית מהקריאה לפעולה">{esc(s.get("body", ""))}</div>'
    else:
        body = f'<div class="b" data-edit="body" {edit} data-path="{sp}/body">{esc(s.get("body", ""))}</div>'
    mark = ""
    if "highlight" in s:   # bold look: the words that get the colour block on the slide
        mark = (f'<div class="hlrow"><span>הדגשה</span><b class="hl" data-edit="highlight" {edit} '
                f'data-path="{sp}/highlight">{esc(s.get("highlight", ""))}</b></div>')
    return (f'<div class="card{" cta" if is_last else ""}" lang="he" dir="rtl" data-path="{sp}">'
            f'<div class="n"><span>{n}</span></div>'
            f'<div class="h" data-edit="headline" {edit} data-path="{sp}/headline">{esc(s["headline"])}</div>'
            f'{body}{mark}</div>')


def html_option(pack, direction, v):
    vid = esc(v["id"])
    p = f"{direction}/{vid}"
    hook = v.get("hook") or {}
    total = sum((hook.get("score") or {}).get(k, 0) for k in lib.HOOK_SCORE_KEYS)
    out = [f'<article class="option p-{esc(direction)}" id="{vid}">']
    out.append('<header class="opt-head">'
               f'<span class="lb-chip {esc(direction)} rv-id">{vid}</span>'
               f'<h3 data-edit="title" data-opt="{vid}" data-path="{p}/title">{esc(v["title"])}</h3>'
               f'<span class="lb-chip">{esc(v.get("child_name", ""))}</span>'
               f'<span class="lb-chip accent">"{esc(v["code_word"])}"</span>'
               '</header>')
    out.append('<div class="deck">' + "".join(html_card(direction, v, s) for s in v["slides"]) + '</div>')
    # What someone who reads only the headlines gets (Yarin, 10 Oct 2026): the story must survive without the bodies
    out.append('<p class="hstory" dir="rtl"><b>הכותרות בלבד</b> ' + " ← ".join(esc(" ".join(lib.lines_of(s["headline"]))) for s in v["slides"]) + '</p>')
    out.append('<div class="drops">')
    cap_lines = lib.lines_of(v["caption"])
    cap_body = cap_lines[:-1] if cap_lines and lib.collapse(cap_lines[-1]) == lib.collapse(v["cta"]) else cap_lines
    out.append('<details class="more"><summary>כיתוב וקריאה לפעולה</summary><div class="inner"><div class="post">'
               f'<div class="caption" dir="rtl" data-path="{p}/caption">'
               f'<div data-edit="caption" data-opt="{vid}">{esc(chr(10).join(cap_body))}</div>'
               f'<div class="cap-cta">{esc(v["cta"])}</div></div>'
               f'<div class="cta-box" data-path="{p}/code_word"><div data-edit="cta" data-opt="{vid}" data-path="{p}/cta">{esc(v["cta"])}</div></div>'
               '</div></div></details>')
    awareness = esc(lib.AWARENESS_LABELS_HE.get(v["awareness_stage"], v["awareness_stage"]))
    pulls = "".join(f'<li>{s["number"]} · {esc((s.get("pull") or {}).get("note", ""))}</li>' for s in v["slides"] if s.get("pull"))
    out.append('<details class="more"><summary>אסטרטגיה</summary><div class="inner"><dl class="lb-kv">'
               f'<dt>על מי</dt><dd>{person_line(v)}</dd>'
               f'<dt>זווית</dt><dd dir="auto">{esc(v["angle"])}</dd>'
               f'<dt>למי</dt><dd dir="auto">{esc(v["target_parent"])} · {awareness}</dd>'
               f'<dt>למה זה עשוי להמיר</dt><dd dir="auto">{esc(v["conversion_rationale"])}</dd>'
               f'<dt>פתיח</dt><dd>{esc(hook.get("formula", ""))} · {total}/12 · {esc(hook.get("gap", ""))}</dd>'
               f'<dt>משיכה לשקופית הבאה</dt><dd><ul class="rp-list">{pulls}</ul></dd>'
               '</dl></div></details>')
    # Claims and sources: dropdown
    lookup = source_lookup(pack, v)
    kind_he = {"sourced_fact": "עובדה עם מקור", "product_fact": "עובדת מוצר מהאתר", "lumebook_wording": "ניסוח שלנו"}
    rows = []
    for c in v["claims"]:
        refs = [f'<a href="{esc(lookup[sid]["url"])}" target="_blank" rel="noopener">{esc(lookup[sid]["title"])}</a>' for sid in c.get("source_ids", []) if sid in lookup]
        rows.append(f'<tr><td>{c["slide"]}</td><td>{esc(c["wording_he"])}</td><td class="kind {esc(c["kind"])}">{kind_he.get(c["kind"], c["kind"])}</td>'
                    f'<td dir="auto">{esc(c["supports"])}{"<br>" + " · ".join(refs) if refs else ""}</td></tr>')
    srcs = "".join(f'<p class="src"><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a> · {esc(s["publisher"])} · נקרא {esc(s["accessed"])}'
                   f'<blockquote dir="ltr" lang="en">{esc(s["quote"])}</blockquote></p>' for s in v["sources"])
    out.append(f'<details class="more" data-path="{p}/claims"><summary>טענות ומקורות</summary><div class="inner">'
               '<table><thead><tr><th>שקופית</th><th>ניסוח</th><th>סוג</th><th>מה המקור תומך</th></tr></thead><tbody>'
               + "".join(rows) + '</tbody></table>' + srcs + '</div></details>')
    # Image descriptions: dropdown, each slide's copy next to its prompt
    anchor = v["character_anchor"]
    img_rows = []
    if lib.one_picture(v):   # one picture behind every slide (Yarin, 14 Oct 2026)
        im = v["image"]
        prompt = lib.compose_image_prompt(anchor, im, 1, pillar=direction, one_picture_prompt=True)
        img_rows.append(f'<tr><td>1 עד {len(v["slides"])}</td><td>תמונה אחת לכל הקרוסלה</td>'
                        f'<td class="en" dir="ltr" lang="en"><b>{esc(im["beat"])}</b><br>{esc(im["action"])}'
                        f'<details><summary>Full prompt</summary><div class="prompt" dir="ltr">{esc(prompt)}</div></details></td></tr>')
    for s in ([] if lib.one_picture(v) else v["slides"]):
        prompt = lib.compose_image_prompt(anchor, s["image"], s["number"], pillar=direction)
        img_rows.append(f'<tr><td>{s["number"]}</td><td style="white-space:pre-line">{esc(s["headline"])}</td>'
                        f'<td class="en" dir="ltr" lang="en"><b>{esc(s["image"]["beat"])}</b><br>{esc(s["image"]["action"])}'
                        f'<details><summary>Full prompt</summary><div class="prompt" dir="ltr">{esc(prompt)}</div></details></td></tr>')
    out.append('<details class="more"><summary>תמונות</summary><div class="inner">'
               f'<div class="anchor" dir="ltr" lang="en">Child: {esc(anchor["child"])}\nParent: {esc(anchor["parent"])}\nWardrobe: {esc(anchor["wardrobe"])}</div>'
               '<table><thead><tr><th>שקופית</th><th>טקסט</th><th>תמונה</th></tr></thead><tbody>' + "".join(img_rows) + '</tbody></table></div></details>')
    out.append('</div></article>')
    return "\n".join(out)


def build_html(pack):
    current = lib.voice_status()
    if current["status"] == "calibrated":
        vchip = '<span class="lb-chip success">קול מכויל</span>'
    else:
        vchip = f'<span class="lb-chip warning" title="קול ברירת מחדל">קול {current["approved_samples"]}/{lib.CALIBRATION_MIN_SAMPLES}</span>'
    nav = []
    legend = []
    for d in pack["directions"]:
        pil = lib.PILLARS.get(d["id"], {})
        links = "".join(f'<a href="#{esc(v["id"])}">{esc(v["id"])} <span>{esc(v.get("child_name", ""))}</span></a>' for v in d["versions"])
        nav.append(f'<span class="grp p-{esc(d["id"])}" title="{esc(pil.get("name_he", ""))}"><span class="dot"></span>{links}</span>')
        legend.append(f'<a class="p-{esc(d["id"])}" href="#dir-{esc(d["id"])}"><span class="sym">{esc(pil.get("symbol", ""))}</span>'
                      f'<b>{esc(pil.get("name_he", d["label_he"]))}</b><span>{esc(pil.get("tagline_he", ""))}</span></a>')
    count = max((len(v["slides"]) for d in pack["directions"] for v in d["versions"]), default=lib.SLIDE_COUNT)
    styles = (SLIDE_CSS + PAGE_CSS).replace("repeat(7,", "repeat(%d," % count)
    # reco_render.inject_review adds its jump link to the first </nav> (keep nav.jump the only <nav>) and inserts its
    # section before the last "</div><script>" (the end of the page body below).
    parts = [
        '<!doctype html>',
        '<html lang="he" dir="rtl">',
        '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark">',
        f'<title>קרוסלות לבוקר {esc(pack["date"])}</title>',
        design.head(),
        f'<style>{styles}</style></head>',
        f'<body dir="rtl" data-date="{esc(pack["date"])}">',
        '<header class="lb-topbar rv-topbar"><div class="lb-topbar-in">',
        f'<img class="rv-logo" src="{design.logo_data_uri()}" alt="LumeBook" width="28" height="28">',
        f'<b class="rv-name">{esc(pack["date"])}</b>',
        f'<nav class="jump">{"".join(nav)}</nav>',
        '<span class="lb-spacer"></span>',
        f'<a class="lb-btn ghost sm" href="{esc(hub_url())}" target="_blank" rel="noopener">ללוח</a>',
        design.theme_toggle(),
        '</div>',
        '<div class="editbar" id="editbar" hidden><span class="lb-chip tint"><span class="lb-dot"></span><b>מצב עריכה</b></span>'
        '<span class="msg" id="edit-msg">לוחצים על טקסט ומשנים. אנטר מוסיף שורה.</span>'
        '<button class="save lb-btn sm" type="button">שמירה (⌘S)</button><button class="undo lb-btn secondary sm" type="button">ביטול</button></div>',
        '</header>',
        '<div class="lb-page">',
        '<header class="top">',
        f'<div class="row"><h1>{esc(pack["topic"]["title_he"])}</h1>{vchip}</div>',
        f'<details class="more"><summary>על הנושא</summary><div class="inner"><p class="lead" dir="auto">{esc(pack["topic"]["reason"])}</p>'
        f'<div class="legend">{"".join(legend)}</div></div></details>',
        '<p class="edit-note" id="edit-note" hidden>לעריכה: <code>python3 carousel/carousel-pipeline/scripts/review_server.py</code></p>',
        '</header>',
        '<div class="result" id="save-result" hidden></div>',
    ]
    for d in pack["directions"]:
        pil = lib.PILLARS.get(d["id"], {})
        parts.append(f'<section class="direction p-{esc(d["id"])} lb-section" id="dir-{esc(d["id"])}"><div class="direction-head">'
                     f'<span class="sym">{esc(pil.get("symbol", ""))}</span><div><h2>{esc(pil.get("name_he", d["label_he"]))}</h2></div></div>')
        for v in d["versions"]:
            parts.append(html_option(pack, d["id"], v))
        parts.append('</section>')
    facts = "".join(f'<tr><td class="en" dir="ltr">{esc(f["id"])}</td><td dir="auto">{esc(f["fact"])}</td><td><a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f["quote"])}</a> · {esc(f["checked_at"])}</td></tr>' for f in pack["product_facts"])
    parts.append(f'<details class="more facts"><summary>עובדות מהאתר</summary><div class="inner">'
                 f'<table><thead><tr><th>מזהה</th><th>עובדה</th><th>ציטוט מהאתר</th></tr></thead><tbody>{facts}</tbody></table></div></details>')
    parts.append(f'</div><script>{SCRIPT}</script></body></html>')
    return "\n".join(parts)


def build_md(pack):
    voice = pack["voice"]
    vline = ("קול מכויל" if voice["status"] == "calibrated"
             else f"קול ברירת מחדל ({voice['approved_samples']} מתוך {lib.CALIBRATION_MIN_SAMPLES} דוגמאות מאושרות)")
    md = [
        f"# קרוסלות לבוקר {pack['date']} · {pack['topic']['title_he']}",
        "",
        '<div dir="rtl" lang="he" style="direction:rtl;text-align:right">',
        "",
        f"**למה הנושא הזה:** {pack['topic']['reason']}",
        "",
        f"**סטטוס קול:** {vline}. {voice['note']}",
        "",
        "בוחרים אפשרות ואומרים לקלוד למשל `produce kid-2`. אין יצירת תמונות בתשלום לפני בחירה ואישור.",
        "",
    ]
    for d in pack["directions"]:
        md += [f"## {d['label_he']}", ""]
        for v in d["versions"]:
            md += [
                f"### {v['id']} · {v['title']}",
                "",
                f"- **על מי:** {v.get('child_name', '')} ({'בת' if v.get('child_gender') == 'girl' else 'בן'}), {lib.ADDRESSEES.get(v.get('addressee'), '')}",
                f"- **זווית:** {v['angle']}",
                f"- **למי:** {v['target_parent']}",
                f"- **שלב מודעות:** {lib.AWARENESS_LABELS_HE.get(v['awareness_stage'], v['awareness_stage'])}",
                f"- **פתיח:** {(v.get('hook') or {}).get('formula', '')}",
                f"- **מילת קוד:** {v['code_word']}",
                f"- **למה זה עשוי להמיר:** {v['conversion_rationale']}",
                "",
            ]
            for s in v["slides"]:
                md += [f"#### שקופית {s['number']} · {lib.ROLE_LABELS_HE.get(s['role'], s['role'])}", ""]
                md += [f"**{line}**  " for line in lib.lines_of(s["headline"])]
                md += [f"{line}  " for line in lib.lines_of(s.get("body", ""))]
                if not lib.one_picture(v):
                    md += ["", '<div dir="ltr" lang="en" style="direction:ltr;text-align:left">', "",
                           f"*Image:* {s['image']['beat']}. {s['image']['action']}", "", "</div>", ""]
                else:
                    md += [""]
            md += ["**הכותרות בלבד:** " + " ← ".join(" ".join(lib.lines_of(s["headline"])) for s in v["slides"]), ""]
            md += ["**כיתוב לפוסט**", ""] + [f"{line}  " for line in lib.lines_of(v["caption"])] + [""]
            md += [f"**CTA:** {v['cta']}", "", "<details><summary>טענות ומקורות</summary>", "", "**מקורות**", ""]
            for src in v["sources"]:
                md.append(f"- [{src['title']}]({src['url']}) · {src['publisher']}: {src['supports']}")
            md += ["", "**טענות**", ""]
            for c in v["claims"]:
                md.append(f"- שקופית {c['slide']} · {c['wording_he']} · {c['kind']} · {c['supports']}")
            md += ["", "</details>", ""]
    md += ["## עובדות מוצר שנבדקו", ""]
    for f in pack["product_facts"]:
        md.append(f"- {f['fact']} · [{f['quote']}]({f['url']}) · {f['checked_at']}")
    md += ["", "</div>", ""]
    return "\n".join(md)


def write_review(pack_path):
    pack_path = Path(pack_path)
    pack = lib.read_json(pack_path)
    html_path = pack_path.with_name("review.html")
    md_path = pack_path.with_name("review.md")
    import reco_render  # the daily games and books carousels, when the night has them
    html_path.write_text(reco_render.inject_review(build_html(pack), pack_path.parent), encoding="utf-8")
    md_path.write_text(build_md(pack), encoding="utf-8")
    return html_path, md_path


def rtl_issues(html):
    """Static RTL checks on a generated page. Used by tests and nightly finish."""
    issues = []
    for needle, why in [('<html lang="he" dir="rtl">', 'html element needs lang="he" dir="rtl"'),
                        ("direction:rtl", "CSS direction:rtl"), ("text-align:right", "CSS text-align:right")]:
        if needle not in html:
            issues.append(why)
    return issues


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: create_review.py PATH_TO_PACK_JSON")
    html_path, md_path = write_review(sys.argv[1])
    problems = rtl_issues(html_path.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("RTL check failed: " + "; ".join(problems))
    print(html_path)
    print(md_path)


if __name__ == "__main__":
    main()
