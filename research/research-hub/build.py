#!/usr/bin/env python3
"""Build the research hub: every research LumeBook has made, on one Hebrew page (08 Nov 2026).

Yarin: "combine every research we ever made to one super organized page".

    python3 tools/lumebook.py build research-hub      # or: cd research/research-hub && python3 build.py

Source: research.json in this folder (topics, the bottom line, one entry per research). Output: research-hub.html.
The build fails on a broken entry (unknown topic, a link to a file that does not exist, an em or en dash, the brand
in the wrong spelling, a bad date) so the page never shows a dead link. Local only: the page holds internal sales
figures, so it has no Vercel address and is not published as an artifact. Standard library only.
"""
import html
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
import design  # noqa: E402

SRC = os.path.join(HERE, "research.json")
OUT = os.path.join(HERE, "research-hub.html")
PAGE = "research/research-hub/research-hub.html"
CAT_SET = "research-topics"

EVIDENCE = {
    "strong": ("success", "ראיות חזקות"),
    "medium": ("info", "ראיות בינוניות"),
    "early": ("warning", "ראיות ראשוניות"),
}
STATUS = {"active": None, "done": None, "superseded": "הוחלף", "stopped": "הופסק"}
DASHES = re.compile("[–—]")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def esc(s):
    return html.escape(str(s or ""), quote=True)


DATE_TXT = re.compile(r"(?<![\d/])(\d{2} / \d{2}(?: / \d{4})?)(?![\d/])")


HANDLE = re.compile(r"(?<![\w@])(@[A-Za-z0-9_.]*[A-Za-z0-9_])")


def ltr_dates(s):
    """dd / mm / yyyy and @handles stay one left-to-right piece inside Hebrew (the bidi algorithm would flip the
    date's spaced parts and move a handle's @ to its far end)."""
    s = DATE_TXT.sub(r'<span class="lb-ltr rh-d">\1</span>', s)
    return HANDLE.sub(r'<span class="lb-ltr rh-d">\1</span>', s)


def inline(s):
    """Escaped text with `code` spans (file names, commands) and dates kept left to right."""
    parts = re.split(r"`([^`]+)`", str(s or ""))
    return "".join(f'<code class="lb-ltr">{esc(p)}</code>' if i % 2 else ltr_dates(esc(p)) for i, p in enumerate(parts))


def fmt(iso):
    if not iso:
        return ""
    y, m, d = iso.split("-")
    return f'<span class="lb-ltr rh-d">{d} / {m} / {y}</span>'


def all_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from all_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from all_strings(v)


def validate(data):
    errs = []
    topics = {t["id"] for t in data["topics"]}
    cats = design.categories(CAT_SET)
    for t in data["topics"]:
        if t["id"] not in cats and not t.get("neutral"):
            errs.append(f"topic {t['id']}: no hue in shared/design/categories.json set {CAT_SET} (or mark it neutral)")
    seen = set()
    for e in data["entries"]:
        eid = e.get("id", "?")
        if eid in seen:
            errs.append(f"{eid}: duplicate id")
        seen.add(eid)
        if e.get("topic") not in topics:
            errs.append(f"{eid}: unknown topic {e.get('topic')!r}")
        if e.get("evidence") not in EVIDENCE:
            errs.append(f"{eid}: evidence must be one of {', '.join(EVIDENCE)}")
        if e.get("status") not in STATUS:
            errs.append(f"{eid}: status must be one of {', '.join(STATUS)}")
        for k in ("date", "updated"):
            if e.get(k) and not DATE.match(e[k]):
                errs.append(f"{eid}: {k} {e[k]!r} is not YYYY-MM-DD")
        if not e.get("date"):
            errs.append(f"{eid}: no date")
        for ln in e.get("links", []):
            if not os.path.exists(os.path.join(ROOT, ln["path"].split("#")[0])):   # a #fragment opens a view (HQ)
                errs.append(f"{eid}: link {ln['path']} does not exist")
        if not e.get("findings"):
            errs.append(f"{eid}: no findings")
    ids = {e["id"] for e in data["entries"]}
    for h in data.get("headlines", []):
        for r in h.get("refs", []):
            if r not in ids:
                errs.append(f"headline refers to unknown entry {r!r}")
    for s in all_strings(data):
        if DASHES.search(s):
            errs.append(f"em or en dash in: {s[:70]}")
        if "לומיבוק" in s:
            errs.append(f"brand spelt לומיבוק in: {s[:70]}")
    return errs


def link_button(ln, first, title=""):
    path, label = ln["path"], ln["label"]
    cls = "lb-btn sm" if first else "lb-btn secondary sm"
    ext = os.path.splitext(path.split("#")[0])[1].lower()
    if ext == ".md":   # read in the page (the server sends Markdown as a download-like text file)
        return (f'<a class="{cls}" href="/{esc(path)}" data-md="{esc(path)}" data-title="{esc(title + ": " + label if title else label)}">'
                f'{design.icon("file")}<span>{esc(label)}</span></a>')
    icon = "open-out" if ext in (".html", ".htm") or path.endswith("/") else "file"
    return (f'<a class="{cls}" href="/{esc(path)}" target="_blank" rel="noopener">'
            f'{design.icon(icon)}<span>{esc(label)}</span></a>')


def card(e, topic, cat):
    ev_cls, ev_label = EVIDENCE[e["evidence"]]
    status = STATUS[e["status"]]
    chips = [f'<span class="lb-chip cat {cat} rh-topic-chip">{esc(topic["label"])}</span>',
             f'<span class="lb-chip rh-date">{design.icon("clock")}<span>{fmt(e["date"])}</span></span>']
    if e.get("updated") and e["updated"] != e["date"]:
        chips.append(f'<span class="lb-chip rh-date">עודכן {fmt(e["updated"])}</span>')
    chips.append(f'<span class="lb-chip {ev_cls}"><i class="lb-dot"></i>{ev_label}</span>')
    if status:
        chips.append(f'<span class="lb-chip outline">{status}</span>')
    if e.get("internal"):
        chips.append('<span class="lb-chip outline" title="מספרים פנימיים או מידע אישי, לא לדפים ציבוריים">פנימי</span>')
    findings = "".join(f"<li>{inline(f)}</li>" for f in e["findings"])
    actions = "".join(f"<li>{inline(a)}</li>" for a in e.get("actions", []))
    links = "".join(link_button(ln, i == 0, e["title"]) for i, ln in enumerate(e.get("links", [])))
    if not links:
        links = '<span class="lb-dim lb-xs">אין קובץ בפרויקט</span>'
    note = f'<p class="rh-status-note lb-xs">{inline(e["status_note"])}</p>' if e.get("status_note") else ""
    side = []
    if actions:
        side.append(f'<div class="rh-block"><h4 class="lb-eyebrow">מה עשינו עם זה</h4><ul class="rh-acts">{actions}</ul></div>')
    side.append(f'<div class="rh-block"><h4 class="lb-eyebrow">כמה זה חזק</h4><p class="rh-ev lb-xs">{inline(e.get("evidence_note"))}</p></div>')
    side.append(f'<div class="rh-links">{links}</div>')
    return f"""<article class="lb-card rh-card{' is-old' if status else ''}" id="r-{esc(e['id'])}" data-id="{esc(e['id'])}" data-topic="{esc(e['topic'])}" data-evidence="{esc(e['evidence'])}" data-date="{esc(e['date'])}">
  <header class="rh-head">
    <div class="rh-title"><span class="lb-tile {cat}">{design.icon(topic['icon'])}</span><h3 class="rh-h">{inline(e['title'])}</h3></div>
    <div class="rh-chips">{''.join(chips)}</div>
  </header>
  <p class="rh-scale lb-font-2">{inline(e.get('scale'))}</p>
  <p class="rh-summary">{inline(e['summary'])}</p>
  {note}
  <div class="rh-body">
    <div class="rh-findings"><h4 class="lb-eyebrow">מה מצאנו</h4><ul class="rh-list">{findings}</ul></div>
    <aside class="lb-sheet rh-side">{''.join(side)}</aside>
  </div>
</article>"""


CSS = r"""
/* research hub: page-specific rules, tokens and lb- pieces only (white only, no side stripes, no scrollbar styles) */
.rh-top { gap: var(--sp-2); }
.rh-top .lb-search { flex: 1 1 18rem; max-width: 34rem; }
.rh-top .lb-search .lb-input { font-size: var(--fs-callout); }
.rh-count { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); white-space: nowrap; }
.rh-top .lb-search .lb-input { padding-inline-end: 2.4rem; }
.rh-top .lb-search .lb-kbd { position: absolute; inset-inline-end: .6rem; pointer-events: none; }
.rh-hero h1 { font-size: clamp(1.8rem, 4vw, 2.6rem); }

/* topic cubes: the colour-coded counts are also the topic filters */
.rh-topics.lb-metrics { grid-template-columns: repeat(auto-fill, minmax(10.5rem, 1fr)); }
button.lb-metric { font: inherit; text-align: start; color: inherit; border: 1px solid transparent; border-radius: var(--r-lg); padding: var(--sp-3) var(--sp-4); cursor: pointer;
  transition: transform var(--dur-2) var(--ease-spring), box-shadow var(--dur-2) var(--ease); }
button.lb-metric:active { transform: scale(var(--press)); }
button.lb-metric[aria-pressed="true"] { border-color: var(--tc); }
.rh-topics.is-filtering button.lb-metric[aria-pressed="false"], .rh-topics button.lb-metric.is-zero { opacity: .5; }
.rh-topics .rh-n { font-weight: inherit; }
.rh-topics .lb-metric-value small { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); }

.rh-tools { display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-2) var(--sp-3); }
.rh-tools .lb-dim { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; }

/* the bottom line */
.rh-lines { display: grid; gap: var(--sp-3); }
.rh-lines li > p { margin: 0; }
.rh-lines .rh-refs { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .35rem; }
.rh-lines .rh-refs a { text-decoration: none; }

/* topic sections */
.rh-section-head { display: flex; align-items: center; gap: var(--sp-3); }
.rh-section-head h2 { font-size: var(--fs-title, 1.5rem); line-height: 1.15; }
.rh-section-head p { margin: .15rem 0 0; color: var(--text-2); font-size: var(--fs-callout); }
.rh-section-head .lb-count { margin-inline-start: auto; }
.rh-cards { display: grid; gap: var(--sp-4); container-type: inline-size; }

/* research card */
.rh-card { gap: var(--sp-3); padding: var(--sp-5); scroll-margin-top: 5rem; }
.rh-card.is-old .rh-h { color: var(--text-2); }
.rh-head { display: grid; gap: var(--sp-2); }
.rh-title { display: flex; align-items: center; gap: var(--sp-3); min-width: 0; }
.rh-h { font-size: 1.25rem; line-height: 1.25; letter-spacing: -.01em; margin: 0; min-width: 0; }
.rh-chips { display: flex; flex-wrap: wrap; gap: .35rem; }
.rh-chips .lb-chip svg { width: .85rem; height: .85rem; }
.rh-by-topic .rh-topic-chip { display: none; }
.rh-scale { margin: 0; font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); }
.rh-summary { margin: 0; font-size: 1.0625rem; line-height: 1.55; max-width: 52rem; }
.rh-status-note { margin: 0; color: var(--text-2); font-weight: 600; }
.rh-card.is-old .rh-status-note { color: var(--warning); }
.rh-d { white-space: nowrap; }
.rh-body { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 17rem); gap: var(--sp-4); align-items: start; }
.rh-findings { display: grid; gap: var(--sp-2); min-width: 0; }
.rh-list, .rh-acts { margin: 0; padding-inline-start: 1.15rem; display: grid; gap: .45rem; }
.rh-list li { line-height: 1.55; }
.rh-list li::marker { color: var(--text-3); }
.rh-acts { font-size: var(--fs-callout); gap: .35rem; }
.rh-side { display: grid; gap: var(--sp-3); padding: var(--sp-3) var(--sp-4); min-width: 0; }
.rh-block { display: grid; gap: .3rem; }
.rh-ev { margin: 0; color: var(--text-2); line-height: 1.5; }
.rh-links { display: flex; flex-wrap: wrap; gap: .4rem; }
.rh-links .lb-btn { max-width: 100%; }
.rh-links .lb-btn span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rh-card code { font-size: .9em; }
mark.rh-hit { background: var(--accent-soft); color: inherit; border-radius: 3px; padding-inline: 1px; }
.rh-list li.is-hit { font-weight: 600; }
.rh-card.is-flash { animation: rh-flash 1.6s var(--ease); }
@keyframes rh-flash { 0%, 40% { box-shadow: var(--glass-card-rim), 0 0 0 3px var(--tint-soft), var(--glass-card-lift); } 100% { box-shadow: var(--glass-card-rim), var(--glass-card-lift); } }

/* short view: the summary only, unless a search hits a finding */
.rh-short .rh-body, .rh-short .rh-scale { display: none; }
.rh-short .rh-card { padding: var(--sp-4) var(--sp-5); }
.rh-short.is-searching .rh-card .rh-body { display: grid; grid-template-columns: minmax(0, 1fr); }
.rh-short.is-searching .rh-side, .rh-short.is-searching .rh-list li:not(.is-hit) { display: none; }

/* in-page reader for the Markdown studies */
dialog.rh-reader { width: min(58rem, calc(100vw - 32px)); }
.rh-reader .lb-dialog-head { padding-inline: var(--sp-4) 8px; gap: var(--sp-2); min-height: 3.5rem; }
.rh-reader-title { flex: 1; min-width: 0; display: grid; }
.rh-reader-title b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rh-reader-title small { font-family: var(--font-2); font-size: var(--fs-caption); color: var(--text-3); direction: ltr; text-align: end; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rh-doc { padding: var(--sp-5); display: grid; gap: var(--sp-3); font-size: var(--fs-callout); line-height: 1.6; overflow-wrap: anywhere; }
.rh-doc h2, .rh-doc h3, .rh-doc h4, .rh-doc h5 { margin: var(--sp-3) 0 0; line-height: 1.25; }
.rh-doc h2 { font-size: 1.5rem; } .rh-doc h3 { font-size: 1.2rem; } .rh-doc h4 { font-size: 1.05rem; } .rh-doc h5 { font-size: 1rem; }
.rh-doc p, .rh-doc ul, .rh-doc ol, .rh-doc blockquote, .rh-doc pre { margin: 0; }
.rh-doc ul, .rh-doc ol { padding-inline-start: 1.3rem; display: grid; gap: .25rem; }
.rh-doc blockquote { padding: var(--sp-2) var(--sp-3); border-radius: var(--r-md); background: var(--fill); color: var(--text-2); }
.rh-doc hr { border: 0; border-top: 1px solid var(--line); margin: var(--sp-2) 0; width: 100%; }
.rh-doc .lb-table-wrap { overflow-x: auto; }
.rh-doc td, .rh-doc th { vertical-align: top; }
.rh-doc [dir="ltr"] { text-align: left; }

@container (max-width: 50rem) { .rh-body { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 640px) {
  .rh-card { padding: var(--sp-4); }
  .rh-h { font-size: 1.125rem; }
  .rh-summary { font-size: 1rem; }
  .rh-count, .rh-top .lb-kbd { display: none; }
  .rh-topics.lb-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .5rem; }
  .rh-topics button.lb-metric { padding: .55rem .7rem .6rem; gap: .2rem; border-radius: var(--r-md); }
  .rh-topics .lb-metric-label { font-size: var(--fs-footnote); gap: .4rem; line-height: 1.2; }
  .rh-topics .lb-metric-label > .lb-tile { width: 1.6rem; height: 1.6rem; border-radius: .45rem; }
  .rh-topics .lb-metric-label > .lb-tile svg { width: .95rem; height: .95rem; }
  .rh-topics .lb-metric-value { font-size: var(--fs-title, 1.5rem); }
  .rh-topics .lb-metric-foot { display: none; }
  .rh-tools .lb-segmented { flex-wrap: wrap; }
  .rh-doc { padding: var(--sp-4); }
}
@media print { .lb-sidebar, .lb-topbar, .rh-tools, .rh-topics { display: none; } .lb-app { display: block; } }
"""

JS = r"""<script>
(function () {
  var DATA = window.RH_DATA, $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var main = $('.lb-main'), side = $('.lb-sidebar'), scrim = $('.lb-scrim'), input = $('#rh-q'), count = $('#rh-count'), empty = $('#rh-empty'), lines = $('#rh-lines-sec'), hero = $('.rh-hero');
  var cards = $$('.rh-card'), byId = {}, home = {}, flat = $('#rh-flat');
  cards.forEach(function (c) { byId[c.dataset.id] = c; home[c.dataset.id] = c.parentNode; });
  var state = { q: '', topics: [], ev: '', order: 'topic', view: 'full' };

  // ---- text search (Hebrew without points, final letters folded, Latin lower case) ----
  function norm(s) {
    return (s || '').toLowerCase().replace(/[֑-ׇ]/g, '').replace(/[׳']/g, "'").replace(/[״"“”]/g, '"')
      .replace(/ם/g, 'מ').replace(/ן/g, 'נ').replace(/ץ/g, 'צ').replace(/ף/g, 'פ').replace(/ך/g, 'כ');
  }
  // a light Hebrew stem: סבתא also finds סבתות, ילדים finds ילד (4+ letters, one ending dropped)
  function variants(t) {
    var v = [t];
    if (/[\u05D0-\u05EA]/.test(t) && t.length >= 4) {
      if (/(\u05D9\u05DE|\u05D5\u05EA)$/.test(t)) v.push(t.slice(0, -2));
      else if (/[\u05D4\u05EA\u05D0]$/.test(t)) v.push(t.slice(0, -1));
    }
    return v;
  }
  var hay = {};
  DATA.forEach(function (e) { hay[e.id] = norm([e.title, e.summary, e.scale, e.status_note, e.evidence_note, e.topic_label].concat(e.findings, e.actions || [], e.tags || [], (e.links || []).map(function (l) { return l.path + ' ' + l.label; })).join(' \n ')); });

  // highlight: restore each card's original text, then wrap the hits
  var orig = new Map();
  function marks(card, terms) {
    $$('.rh-h, .rh-summary, .rh-scale, .rh-list li, .rh-acts li, .rh-ev, .rh-status-note', card).forEach(function (el) {
      if (!orig.has(el)) orig.set(el, el.innerHTML); else el.innerHTML = orig.get(el);
      el.classList.remove('is-hit');
      if (!terms.length) return;
      var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), nodes = [], n, hit = false;
      while ((n = walker.nextNode())) nodes.push(n);
      nodes.forEach(function (node) {
        var text = node.nodeValue, low = norm(text), ranges = [];
        terms.forEach(function (t) { var i = 0; while (t && (i = low.indexOf(t, i)) > -1) { ranges.push([i, i + t.length]); i += t.length; } });
        ranges.sort(function (a, b) { return a[0] - b[0] || b[1] - a[1]; });
        if (!ranges.length) return;
        hit = true;
        var frag = document.createDocumentFragment(), at = 0;
        ranges.forEach(function (r) {
          if (r[0] < at) return;
          frag.appendChild(document.createTextNode(text.slice(at, r[0])));
          var m = document.createElement('mark'); m.className = 'rh-hit'; m.textContent = text.slice(r[0], r[1]); frag.appendChild(m);
          at = r[1];
        });
        frag.appendChild(document.createTextNode(text.slice(at)));
        node.parentNode.replaceChild(frag, node);
      });
      if (hit && el.tagName === 'LI') el.classList.add('is-hit');
    });
  }

  function apply() {
    var terms = norm(state.q).split(/\s+/).filter(Boolean), groups = terms.map(variants), shown = 0, hits = 0, perTopic = {}, anyTopic = {};
    var markTerms = [].concat.apply([], groups);
    DATA.forEach(function (e) {
      var c = byId[e.id];
      var match = (!state.ev || e.evidence === state.ev) && groups.every(function (g) { return g.some(function (t) { return hay[e.id].indexOf(t) > -1; }); });
      if (match) anyTopic[e.topic] = (anyTopic[e.topic] || 0) + 1;
      var ok = match && (!state.topics.length || state.topics.indexOf(e.topic) > -1);
      c.hidden = !ok;
      marks(c, ok ? markTerms : []);
      if (ok) { shown++; perTopic[e.topic] = (perTopic[e.topic] || 0) + 1; if (terms.length) hits += $$('.rh-list li.is-hit', c).length; }
    });
    $$('.rh-topic-sec').forEach(function (s) {
      s.hidden = state.order !== 'topic' || !perTopic[s.dataset.topic];
      s.querySelector('.rh-section-head .lb-count').textContent = perTopic[s.dataset.topic] || 0;
    });
    flat.hidden = state.order !== 'date' || !shown;
    $$('.lb-sidebar [data-topic]').forEach(function (a) { var n = a.querySelector('.lb-nav-n'); if (n) n.textContent = perTopic[a.dataset.topic] || 0; });
    var filtering = !!(terms.length || state.topics.length || state.ev), narrowed = !!(terms.length || state.ev);
    lines.hidden = filtering;
    hero.hidden = !!terms.length;
    $$('.rh-topics [data-topic]').forEach(function (b) {
      var n = narrowed ? (anyTopic[b.dataset.topic] || 0) : +b.dataset.total;
      b.querySelector('.rh-n').textContent = n;
      b.classList.toggle('is-zero', narrowed && !n);
    });
    main.classList.toggle('is-searching', !!terms.length);
    $('.rh-topics').classList.toggle('is-filtering', state.topics.length > 0);
    $('#rh-clear').hidden = !filtering;
    empty.hidden = shown > 0;
    count.textContent = filtering ? (shown + ' מתוך ' + DATA.length + ' מחקרים' + (terms.length ? ' · ' + hits + ' ממצאים' : '')) : DATA.length + ' מחקרים';
    var u = new URL(location.href);
    if (state.q) u.searchParams.set('q', state.q); else u.searchParams.delete('q');
    if (state.topics.length) u.searchParams.set('t', state.topics.join(',')); else u.searchParams.delete('t');
    history.replaceState(null, '', u.pathname + u.search + u.hash);
  }

  function setOrder(o) {
    state.order = o;
    main.classList.toggle('rh-by-topic', o === 'topic');
    if (o === 'date') {
      DATA.slice().sort(function (a, b) { return (b.date + b.id).localeCompare(a.date + a.id); }).forEach(function (e) { flat.appendChild(byId[e.id]); });
    } else {
      DATA.forEach(function (e) { home[e.id].appendChild(byId[e.id]); });
    }
    $$('[data-order]').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.order === o ? 'true' : 'false'); });
    apply();
  }

  var timer;
  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(function () { state.q = input.value.trim(); apply(); }, 110); });
  input.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') { input.value = ''; state.q = ''; apply(); } });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === '/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) { ev.preventDefault(); input.focus(); input.select(); }
  });
  $$('.rh-topics [data-topic]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.dataset.topic, i = state.topics.indexOf(t);
      if (i > -1) state.topics.splice(i, 1); else state.topics.push(t);
      b.setAttribute('aria-pressed', i > -1 ? 'false' : 'true');
      apply();
    });
  });
  $$('[data-ev]').forEach(function (b) {
    b.addEventListener('click', function () { state.ev = b.dataset.ev; $$('[data-ev]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); apply(); });
  });
  $$('[data-order]').forEach(function (b) { b.addEventListener('click', function () { setOrder(b.dataset.order); }); });
  $$('[data-view]').forEach(function (b) {
    b.addEventListener('click', function () {
      state.view = b.dataset.view; main.classList.toggle('rh-short', state.view === 'short');
      $$('[data-view]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    });
  });
  $('#rh-clear').addEventListener('click', function () {
    state.q = ''; input.value = ''; state.topics = []; state.ev = '';
    $$('.rh-topics [data-topic]').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
    $$('[data-ev]').forEach(function (x) { x.setAttribute('aria-pressed', x.dataset.ev === '' ? 'true' : 'false'); });
    apply();
  });

  // ---- sidebar: drawer on phones, jump to a topic, mark the topic in view ----
  function closeNav() { side.classList.remove('is-open'); scrim.hidden = true; }
  $('#rh-menu').addEventListener('click', function () { side.classList.add('is-open'); scrim.hidden = false; });
  scrim.addEventListener('click', closeNav);
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') closeNav(); });
  function go(el) { if (el) { el.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' }); } }
  $$('.lb-sidebar .lb-nav-item').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      var t = a.dataset.topic, target = $(a.getAttribute('href'));
      ev.preventDefault(); closeNav();
      if (t) {
        if (state.order !== 'topic') setOrder('topic');
        if (state.topics.length && state.topics.indexOf(t) < 0) { state.topics.push(t); $('.rh-topics [data-topic="' + t + '"]').setAttribute('aria-pressed', 'true'); }
        apply();
      }
      go(target);
      history.replaceState(null, '', location.pathname + location.search + a.getAttribute('href'));
    });
  });
  var navItems = $$('.lb-sidebar .lb-nav-item[data-topic]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (list) {
      list.forEach(function (en) {
        if (!en.isIntersecting) return;
        navItems.forEach(function (a) { if (a.dataset.topic === en.target.dataset.topic) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    $$('.rh-topic-sec').forEach(function (s) { io.observe(s); });
  }
  function flash(id) {
    var c = byId[id]; if (!c) return;
    if (c.hidden) { $('#rh-clear').click(); }
    go(c); c.classList.remove('is-flash'); void c.offsetWidth; c.classList.add('is-flash');
  }
  $$('a[data-ref]').forEach(function (a) { a.addEventListener('click', function (ev) { ev.preventDefault(); flash(a.dataset.ref); }); });

  // ---- reader: the Markdown studies open inside the page ----
  var dlg = $('#rh-reader'), doc = $('#rh-doc'), rTitle = $('#rh-r-title'), rPath = $('#rh-r-path'), rRaw = $('#rh-r-raw');
  function escH(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function resolve(base, href) {
    if (/^(https?:|mailto:|#)/.test(href)) return null;
    var parts = base.split('/'); parts.pop();
    href.split('#')[0].split('/').forEach(function (p) { if (p === '..') parts.pop(); else if (p && p !== '.') parts.push(p); });
    return parts.join('/');
  }
  function inl(s, base) {
    var codes = [];
    s = s.replace(/`([^`]+)`/g, function (_, c) { codes.push(c); return '\u0000' + (codes.length - 1) + '\u0000'; });
    s = escH(s);
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;[^&]*&quot;)?\)/g, function (_, t, h) {
      var hr = h.replace(/&amp;/g, '&'), r = resolve(base, hr);
      if (r === null) return '<a href="' + escH(hr) + '" target="_blank" rel="noopener">' + t + '</a>';
      if (/\.md$/i.test(r)) return '<a href="/' + escH(r) + '" data-md="' + escH(r) + '">' + t + '</a>';
      return '<a href="/' + escH(r) + '" target="_blank" rel="noopener">' + t + '</a>';
    });
    s = s.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
    s = s.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/(^|[\s(])\*([^*\s][^*]*)\*/g, '$1<i>$2</i>').replace(/(^|[\s(])_([^_\s][^_]*)_(?=[\s.,;:)]|$)/g, '$1<i>$2</i>');
    return s.replace(/\u0000(\d+)\u0000/g, function (_, i) { return '<code dir="ltr">' + escH(codes[+i]) + '</code>'; });
  }
  function md(text, base) {
    var L = text.replace(/\r/g, '').split('\n'), out = [], i = 0, para = [];
    if (L[0] === '---') { i = 1; while (i < L.length && L[i] !== '---') i++; i++; }
    function flush() { if (para.length) { out.push('<p dir="auto">' + inl(para.join(' '), base) + '</p>'); para = []; } }
    function cells(row) { return row.replace(/^\s*\|/, '').replace(/\|\s*$/, '').split('|').map(function (c) { return c.trim(); }); }
    while (i < L.length) {
      var l = L[i], m;
      if (/^\s*```/.test(l)) { flush(); var code = []; i++; while (i < L.length && !/^\s*```/.test(L[i])) code.push(L[i++]); i++; out.push('<pre class="lb-textblock is-code">' + escH(code.join('\n')) + '</pre>'); continue; }
      if ((m = l.match(/^(#{1,6})\s+(.*)$/))) { flush(); var lv = Math.min(5, m[1].length + 1); out.push('<h' + lv + ' dir="auto">' + inl(m[2].replace(/\s+#+\s*$/, ''), base) + '</h' + lv + '>'); i++; continue; }
      if (/^\s*([-*_])\s*\1\s*\1[\s\1]*$/.test(l)) { flush(); out.push('<hr>'); i++; continue; }
      if (/^\s*\|/.test(l) && i + 1 < L.length && /^\s*\|?\s*:?-{2,}/.test(L[i + 1])) {
        flush(); var head = cells(l), rows = []; i += 2;
        while (i < L.length && /^\s*\|/.test(L[i])) rows.push(cells(L[i++]));
        out.push('<div class="lb-table-wrap"><table class="lb-table" dir="auto"><thead><tr>' + head.map(function (c) { return '<th>' + inl(c, base) + '</th>'; }).join('') + '</tr></thead><tbody>' +
          rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + inl(c, base) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>');
        continue;
      }
      if (/^\s*>/.test(l)) { flush(); var q = []; while (i < L.length && /^\s*>/.test(L[i])) q.push(L[i++].replace(/^\s*>\s?/, '')); out.push('<blockquote dir="auto">' + inl(q.join(' '), base) + '</blockquote>'); continue; }
      if (/^\s*([-*+]|\d+[.)])\s+/.test(l)) {
        flush(); var stack = [];
        while (i < L.length && (/^\s*([-*+]|\d+[.)])\s+/.test(L[i]) || (/^\s{2,}\S/.test(L[i]) && stack.length))) {
          var li = L[i], mm = li.match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/);
          if (!mm) { out.push(' ' + inl(li.trim(), base)); i++; continue; }
          var ind = mm[1].replace(/\t/g, '    ').length, tag = /\d/.test(mm[2]) ? 'ol' : 'ul';
          while (stack.length && ind < stack[stack.length - 1].ind) { out.push('</li></' + stack.pop().tag + '>'); }
          if (!stack.length || ind > stack[stack.length - 1].ind) { out.push('<' + tag + ' dir="auto">'); stack.push({ ind: ind, tag: tag }); }
          else out.push('</li>');
          out.push('<li>' + inl(mm[3], base)); i++;
        }
        while (stack.length) out.push('</li></' + stack.pop().tag + '>');
        continue;
      }
      if (!l.trim()) { flush(); i++; continue; }
      para.push(l.trim()); i++;
    }
    flush();
    return out.join('');
  }
  function openDoc(path, title) {
    rTitle.textContent = title || path.split('/').pop(); rPath.textContent = path; rRaw.href = '/' + path;
    doc.innerHTML = '<div class="lb-row"><span class="lb-spinner"></span><span class="lb-dim">טוען...</span></div>';
    if (!dlg.open) dlg.showModal();
    dlg.scrollTop = 0;
    fetch('/' + path).then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); }).then(function (t) {
      doc.innerHTML = md(t, path);
      $$('a[data-md]', doc).forEach(function (a) { a.addEventListener('click', function (ev) { ev.preventDefault(); openDoc(a.dataset.md, a.textContent); }); });
    }).catch(function () {
      doc.innerHTML = '<p class="lb-empty">אי אפשר לקרוא את הקובץ כאן. הדף עובד מהשרת של הפרויקט (localhost:8780). אפשר לפתוח את הקובץ בלשונית.</p>';
    });
  }
  $$('a[data-md]').forEach(function (a) { a.addEventListener('click', function (ev) { if (ev.metaKey || ev.ctrlKey) return; ev.preventDefault(); openDoc(a.dataset.md, a.dataset.title); }); });
  $('#rh-r-x').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (ev) { if (ev.target === dlg) dlg.close(); });

  // ---- start: read ?q= and ?t= ----
  var sp = new URLSearchParams(location.search);
  if (sp.get('q')) { state.q = sp.get('q'); input.value = state.q; }
  (sp.get('t') || '').split(',').filter(function (t) { return $('.rh-topics [data-topic="' + t + '"]'); }).forEach(function (t) { state.topics.push(t); $('.rh-topics [data-topic="' + t + '"]').setAttribute('aria-pressed', 'true'); });
  setOrder('topic');
  if (location.hash && location.hash.indexOf('#r-') === 0) setTimeout(function () { flash(location.hash.slice(3)); }, 60);
})();
</script>"""


def build():
    data = json.load(open(SRC, encoding="utf-8"))
    errs = validate(data)
    if errs:
        print("research.json has problems:\n  " + "\n  ".join(errs), file=sys.stderr)
        sys.exit(1)
    cats = design.categories(CAT_SET)
    topics = data["topics"]
    tmap = {t["id"]: t for t in topics}
    cat = {t["id"]: f"lb-cat-{cats[t['id']]['cat']}" if t["id"] in cats else "lb-cat-0" for t in topics}
    entries = sorted(data["entries"], key=lambda e: (e["date"], e["id"]), reverse=True)
    by_topic = {t["id"]: [e for e in entries if e["topic"] == t["id"]] for t in topics}
    n_find = sum(len(e["findings"]) for e in entries)
    first, last = min(e["date"] for e in entries), max(e.get("updated") or e["date"] for e in entries)

    nav = [f'<a class="lb-nav-item" href="#rh-lines-sec"><span class="lb-tile lb-cat-0">{design.icon("sparkle")}</span>'
           f'<span class="lb-nav-text">השורה התחתונה</span></a>', '<div class="lb-nav-label">נושאים</div>']
    for t in topics:
        if not by_topic[t["id"]]:
            continue
        nav.append(f'<a class="lb-nav-item {cat[t["id"]]}" href="#t-{t["id"]}" data-topic="{t["id"]}"><span class="lb-tile {cat[t["id"]]}">{design.icon(t["icon"])}</span>'
                   f'<span class="lb-nav-text">{esc(t["label"])}</span><span class="lb-nav-n">{len(by_topic[t["id"]])}</span></a>')

    cubes = []
    for t in topics:
        es = by_topic[t["id"]]
        if not es:
            continue
        nf = sum(len(e["findings"]) for e in es)
        cubes.append(f'<button type="button" class="lb-metric {cat[t["id"]]}" data-topic="{t["id"]}" data-total="{len(es)}" aria-pressed="false">'
                     f'<span class="lb-metric-label"><span class="lb-tile">{design.icon(t["icon"])}</span>{esc(t["label"])}</span>'
                     f'<span class="lb-metric-value"><b class="rh-n">{len(es)}</b> <small>מחקרים</small></span>'
                     f'<span class="lb-metric-foot">{nf} ממצאים</span></button>')

    eid = {e["id"]: e for e in entries}
    heads = []
    for h in data.get("headlines", []):
        refs = "".join(f'<a class="lb-chip cat {cat[eid[r]["topic"]]}" href="#r-{r}" data-ref="{r}">{esc(eid[r]["title"])}</a>' for r in h.get("refs", []))
        heads.append(f'<li><p>{inline(h["text"])}</p><div class="rh-refs">{refs}</div></li>')

    sections = []
    for t in topics:
        es = by_topic[t["id"]]
        if not es:
            continue
        sections.append(f"""<section class="lb-section rh-topic-sec" id="t-{t['id']}" data-topic="{t['id']}">
  <div class="rh-section-head"><span class="lb-tile lg {cat[t['id']]}">{design.icon(t['icon'])}</span><div><h2>{esc(t['label'])}</h2><p>{esc(t['desc'])}</p></div><span class="lb-count">{len(es)}</span></div>
  <div class="rh-cards">{''.join(card(e, t, cat[t['id']]) for e in es)}</div>
</section>""")

    client = [{"id": e["id"], "topic": e["topic"], "topic_label": tmap[e["topic"]]["label"], "title": e["title"], "date": e["date"],
               "summary": e["summary"], "scale": e.get("scale", ""), "findings": e["findings"], "actions": e.get("actions", []),
               "tags": e.get("tags", []), "evidence": e["evidence"], "evidence_note": e.get("evidence_note", ""),
               "status_note": e.get("status_note") or "", "links": e.get("links", [])} for e in entries]

    page = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>ספריית המחקר · לומבוק</title>
{design.head(page=PAGE)}
<style>{CSS}</style>
</head>
<body>
<div class="lb-app">
  <aside class="lb-sidebar" aria-label="נושאי המחקר">
    <a class="lb-brand" href="#top"><img src="{design.logo_data_uri()}" alt=""><span><b>ספריית המחקר</b><small>לומבוק · {len(entries)} מחקרים</small></span></a>
    <nav class="lb-nav">{''.join(nav)}</nav>
    <div class="lb-sidebar-foot"><span class="lb-chip outline">פנימי: מספרי מכירות, מקומי בלבד</span><span>עודכן {fmt(data.get('updated') or date.today().isoformat())}</span><span>המקור: <code class="lb-ltr">research/research-hub/research.json</code></span></div>
  </aside>
  <div class="lb-scrim" hidden></div>
  <main class="lb-main rh-by-topic" id="top">
    <div class="lb-topbar lb-edge"><div class="lb-topbar-in rh-top">
      <button class="lb-btn secondary icon lb-menu-btn" id="rh-menu" type="button" aria-label="פתיחת הנושאים">{design.icon("menu")}</button>
      <label class="lb-search">{design.icon("search")}<span class="lb-sr">חיפוש בכל המחקרים</span><input class="lb-input" id="rh-q" type="search" dir="rtl" placeholder="חיפוש בכל המחקרים והממצאים" autocomplete="off"><span class="lb-kbd" aria-hidden="true">/</span></label>
      <span class="rh-count" id="rh-count" aria-live="polite">{len(entries)} מחקרים</span>
    </div></div>
    <div class="lb-page">
      <header class="lb-hero rh-hero">
        <span class="lb-eyebrow">לומבוק · מחקר</span>
        <h1>כל המחקרים במקום אחד</h1>
        <p class="lb-lede">{inline(data.get('lede', ''))}</p>
        <div class="lb-hero-meta"><span>{len(entries)} מחקרים</span><span>{n_find} ממצאים</span><span>{fmt(first)} עד {fmt(last)}</span></div>
      </header>
      <div class="lb-metrics rh-topics" aria-label="סינון לפי נושא">{''.join(cubes)}</div>
      <div class="rh-tools">
        <div class="lb-segmented" role="group" aria-label="כמה חזקות הראיות"><button type="button" data-ev="" aria-pressed="true">כל הראיות</button><button type="button" data-ev="strong" aria-pressed="false">חזקות</button><button type="button" data-ev="medium" aria-pressed="false">בינוניות</button><button type="button" data-ev="early" aria-pressed="false">ראשוניות</button></div>
        <div class="lb-segmented" role="group" aria-label="סדר"><button type="button" data-order="topic" aria-pressed="true">לפי נושא</button><button type="button" data-order="date" aria-pressed="false">לפי תאריך</button></div>
        <div class="lb-segmented" role="group" aria-label="תצוגה"><button type="button" data-view="full" aria-pressed="true">מלא</button><button type="button" data-view="short" aria-pressed="false">תקציר</button></div>
        <button class="lb-btn ghost sm" id="rh-clear" type="button" hidden>{design.icon("close")}<span>ניקוי הסינון</span></button>
      </div>
      <section class="lb-section" id="rh-lines-sec"><div id="rh-lines">
        <div class="lb-section-head"><h2>השורה התחתונה</h2><span class="lb-meta">מה כמה מחקרים אומרים יחד</span></div>
        <div class="lb-card"><ol class="lb-steps tint rh-lines">{''.join(heads)}</ol></div>
      </div></section>
      {''.join(sections)}
      <div class="rh-cards" id="rh-flat" hidden></div>
      <p class="lb-empty" id="rh-empty" hidden>לא נמצא מחקר שמתאים. אפשר לנסות מילה אחרת או לנקות את הסינון.</p>
      <footer class="lb-footer lb-xs lb-dim">נבנה מ-<code class="lb-ltr">research/research-hub/research.json</code> ב-<code class="lb-ltr">python3 tools/lumebook.py build research-hub</code>. מחקר חדש: רשומה חדשה בקובץ, ואז build.</footer>
    </div>
  </main>
</div>
<dialog class="lb-dialog rh-reader" id="rh-reader" aria-label="קריאת המסמך">
  <div class="lb-dialog-card">
    <div class="lb-dialog-head"><div class="rh-reader-title"><b id="rh-r-title"></b><small id="rh-r-path"></small></div>
      <a class="lb-btn secondary sm" id="rh-r-raw" href="#" target="_blank" rel="noopener">{design.icon("open-out")}<span>בלשונית</span></a>
      <button class="lb-dialog-x" id="rh-r-x" type="button" aria-label="סגירה">✕</button></div>
    <div class="lb-dialog-body"><div class="rh-doc" id="rh-doc"></div></div>
  </div>
</dialog>
<script>window.RH_DATA = {json.dumps(client, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")};</script>
{JS}
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(entries)} research entries, {n_find} findings, {len(page):,} bytes")


if __name__ == "__main__":
    build()
