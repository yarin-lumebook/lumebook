#!/usr/bin/env python3
"""Build the Hanukkah and Black Friday 2026 content page (18 Nov 2026), in Hebrew.

Yarin: "can i have an html for it?"

    python3 tools/lumebook.py build hanukkah-black-friday-2026     # or: cd research/hanukkah-black-friday-2026 && python3 build.py

Source: content.md, the only source. The page parses it, so edit the md and rebuild, never the html.
Output: hanukkah-black-friday.html, one section at a time from the page sidebar (overview, then the seven ## sections).
Tables whose first column is "#" become cards (the purchase intents and the hooks); a hook's "כוונה" links to its intent card.
Fails on an em or en dash, the brand spelt לומיבוק, intent numbers that are not 1..N, or a hook that names an unknown intent.
Local only: it repeats an internal figure from shared/facts.json (buyers). Standard library only.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
import design  # noqa: E402

# two pages (18 Nov 2026, Yarin: "separete hanukkah and black friday"): name -> source, output, page title, sidebar title
PAGES = {
    "hanukkah": ("hanukkah.md", "hanukkah.html", "חנוכה 2026", "חנוכה"),
    "black-friday": ("black-friday.md", "black-friday.html", "בלאק פריידיי 2026", "בלאק פריידיי"),
}
SRC = OUT = PAGE = PAGE_TITLE = BRAND = None
DASHES = re.compile("[–—]")

# the number of a "## N." heading -> section id, sidebar label, icon
SECTIONS_BASE = {
    "1": ("offers", "מה מציעים, ומתי", "gift"),
    "2": ("planned", "מה כבר מתוכנן", "calendar"),
    "3": ("search", "מה מחפשים בגוגל", "search"),
    "4": ("intents", "כוונות קנייה", "target"),
    "5": ("questions", "שאלות קשורות", "chat"),
    "6": ("hooks", "הוקים", "sparkle"),
    "7": ("open", "מה פתוח", "bell"),
}
# Black Friday became a campaign on 19 Nov 2026 (Yarin: "119 for the first book 99 for the second"; the campaign prompt asked
# for phases, five briefs, distribution, measurement and tasks inside the existing page, not a new one)
SECTIONS_BF = {
    "1": ("offers", "מה מציעים, ומתי", "gift"),
    "2": ("planned", "לוח הקמפיין", "calendar"),
    "3": ("search", "מה מחפשים בגוגל", "search"),
    "4": ("intents", "כוונות קנייה", "target"),
    "5": ("questions", "שאלות קשורות", "chat"),
    "6": ("hooks", "הוקים", "sparkle"),
    "7": ("briefs", "חמישה בריפים", "image"),
    "8": ("funnel", "הפצה והמרה", "share"),
    "9": ("measure", "מדידה ורווחיות", "chart"),
    "10": ("tasks", "משימות", "check"),
    "11": ("open", "מה פתוח", "bell"),
}
SECTIONS_BY_PAGE = {"hanukkah": SECTIONS_BASE, "black-friday": SECTIONS_BF}
SECTIONS = SECTIONS_BASE
COPY_SECTIONS = {"hooks", "briefs"}   # sections whose card headlines are audience copy (Hebrew in both languages)
# table columns that hold audience copy: kept Hebrew when the page is switched to English
COPY_COLS = {"הטקסט על המסך", "בדיבור", "על השקופית", "על הפריים", "ההוק", "הכיתוב", "טקסט לפייסבוק", "ההודעה"}
# "### " headings in the hooks section that the overview cubes point at
SUB_IDS = {"רילס": "reels", "קרוסלות ניסוי": "test", "קרוסלות ילד": "kid", "פוסטים בפייסבוק": "facebook", "סטוריז": "stories"}
HEADLINE = {"הכוונה", "ההוק על המסך", "כותרת (המילה המודגשת בכוכביות)", "שער"}
BR_COLS = {"כותרת (המילה המודגשת בכוכביות)", "גוף השער", "שער", "הנעה לשמירה", "ההוק על המסך"}   # " / " marks a line break on the slide
LABELS = {"ישירה": ("success", "ראיה ישירה"), "הסקה": ("info", "הסקה"), "השערה": ("warning", "השערה")}
KV_NAMES = {"כותרת (המילה המודגשת בכוכביות)": "כותרת"}

DATE_TXT = re.compile(r"(?<![\d/])(\d{1,2} / \d{2}(?: / \d{4})?)(?![\d/])")
SITE = re.compile(r"(?<![\w/.])((?:https?://)?lumebook\.com/[A-Za-z0-9/_\-]+)")


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def inline(s, br=False):
    """Escaped text: `code` spans, **bold**, store links, dates kept left to right, ⚑ marked."""
    out = []
    for i, p in enumerate(re.split(r"`([^`]+)`", str(s or ""))):
        if i % 2:
            out.append(f'<code class="lb-ltr">{esc(p)}</code>')
            continue
        t = esc(p)
        if br:
            t = t.replace(" / ", "<br>")
        t = SITE.sub(lambda m: f'<a class="lb-ltr" href="{m.group(1) if m.group(1).startswith("http") else "https://" + m.group(1)}" '
                               f'target="_blank" rel="noopener">{m.group(1)}</a>', t)
        t = DATE_TXT.sub(r'<span class="lb-ltr">\1</span>', t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = t.replace("⚑", '<span class="hb-flag" title="תלוי במשהו שלא אומת">⚑</span>')
        out.append(t)
    return "".join(out)


def cells(line):
    return [x.strip() for x in line.strip().strip("|").split("|")]


# ---- parse content.md into the intro and the ## sections, each a list of blocks ----
def parse():
    with open(os.path.join(HERE, SRC), encoding="utf-8") as f:
        lines = f.read().split("\n")
    doc = {"title": "", "intro": [], "sections": []}
    blocks = doc["intro"]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            doc["title"] = line[2:].strip()
        elif line.startswith("## "):
            m = re.match(r"^## (\d+)\. (.+)$", line)
            if not m or m.group(1) not in SECTIONS:
                sys.exit(f"content.md: unexpected section heading {line!r} (SECTIONS in build.py knows 1 to {len(SECTIONS)})")
            blocks = []
            doc["sections"].append({"num": m.group(1), "title": m.group(2).strip(), "blocks": blocks})
        elif line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s:|-]+\|$", lines[i]):
                    rows.append(cells(lines[i]))
                i += 1
            blocks.append(("table", rows))
            continue
        elif re.match(r"^(- |\d+\. )", line):
            ordered = not line.startswith("- ")
            items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i]))
                i += 1
            blocks.append(("ol" if ordered else "ul", items))
            continue
        elif line.strip():
            para = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|\||- |\d+\. )", lines[i + 1]):
                i += 1
                para.append(lines[i])
            blocks.append(("p", " ".join(para)))
        i += 1
    return doc


def all_text(doc):
    yield doc["title"]
    for b in doc["intro"] + [b for s in doc["sections"] for b in s["blocks"]]:
        if b[0] == "table":
            for r in b[1]:
                yield from r
        elif b[0] in ("ul", "ol"):
            yield from b[1]
        else:
            yield b[1]
    for s in doc["sections"]:
        yield s["title"]


def section(doc, sid):
    return next(s for s in doc["sections"] if SECTIONS[s["num"]][0] == sid)


def card_tables(sec):
    return [b[1] for b in sec["blocks"] if b[0] == "table" and b[1][0][0] == "#"]


def validate(doc):
    errs = []
    for s in all_text(doc):
        if DASHES.search(s):
            errs.append(f"em or en dash in: {s[:70]}")
        if "לומיבוק" in s:
            errs.append(f"brand spelt לומיבוק in: {s[:70]}")
    nums = [int(r[0]) for t in card_tables(section(doc, "intents")) for r in t[1:]]
    if nums != list(range(1, len(nums) + 1)):
        errs.append(f"intent numbers are not 1..{len(nums)} in order: {nums}")
    for t in card_tables(section(doc, "hooks")):
        if "כוונה" in t[0]:
            k = t[0].index("כוונה")
            for r in t[1:]:
                for n in re.findall(r"\d+", r[k]):
                    if int(n) not in nums:
                        errs.append(f"hook #{r[0]} names unknown intent {n}")
    return errs


# ---- rendering ----
def chip(cls, text, title=""):
    t = f' title="{esc(title)}"' if title else ""
    return f'<span class="lb-chip {cls}"{t}>{text}</span>'


def cards(rows, sid, sub, copy):
    """A "#" table as cards: the headline column on top, chips for the label, intent, plan and child, the rest as key and value."""
    head = rows[0]
    hcol = next((k for k, h in enumerate(head) if h in HEADLINE), 1)
    out = []
    for r in rows[1:]:
        chips, kv = [], []
        for k, (h, v) in enumerate(zip(head, r)):
            if k in (0, hcol) or not v:
                continue
            if h == "תווית ומקור":
                lab, _, src = v.partition(" · ")
                cls, name = LABELS.get(lab.strip(), ("outline", lab))
                chips.append(chip(cls, esc(name)))
                if src:
                    kv.append(("מקור", inline(src)))
            elif h == "כוונה":
                for n in re.findall(r"\d+", v):
                    chips.append(f'<a class="lb-chip outline hb-ilink" href="#i-{n}" data-int="{n}">כוונה {n}</a>')
            elif h == "מתוכנן":
                chips.append(chip("success", "חדש") if v == "לא" else chip("info", f"כבר מתוכנן: {inline(v)}"))
            elif h == "הילד":
                chips.append(chip("outline", esc(v)))
            else:
                tn = ' translate="no"' if copy and h in BR_COLS | {"השורה השנייה בדיבור"} else ""
                kv.append((KV_NAMES.get(h, h), f'<span{tn}>{inline(v, br=h in BR_COLS)}</span>'))
        cid = f"i-{r[0]}" if sid == "intents" else f"{sub or sid}-{r[0]}"
        tn = ' translate="no"' if copy else ""
        dl = "".join(f"<dt>{esc(a)}</dt><dd>{b}</dd>" for a, b in kv)
        out.append(f'<article class="lb-card hb-card" id="{cid}"><div class="hb-card-head"><span class="hb-n">#{esc(r[0])}</span>{"".join(chips)}</div>'
                   f'<p class="hb-headline" dir="rtl"{tn}>{inline(r[hcol], br=head[hcol] in BR_COLS)}</p>'
                   f'<dl class="lb-kv">{dl}</dl></article>')
    return f'<div class="hb-cards">{"".join(out)}</div>'


def table(rows):
    head = rows[0]
    th = "".join(f"<th>{esc(h)}</th>" for h in head)
    tn = [' translate="no" dir="rtl"' if h in COPY_COLS else "" for h in head]
    # in a copy column " // " is a line break (" / " cannot be: dates are written 27 / 11)
    body = "".join("<tr>" + "".join(f'<td data-label="{esc(head[k])}"{tn[k]}>{inline(v).replace(" // ", "<br>")}</td>'
                                    for k, v in enumerate(r)) + "</tr>" for r in rows[1:])
    return f'<div class="lb-table-wrap"><table class="lb-table hb-table"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def blocks_html(blocks, sid):
    out, sub, k = [], None, 0
    copy = sid in COPY_SECTIONS   # audience copy stays Hebrew in both languages
    tn = ' translate="no"' if copy else ""
    for kind, data in blocks:
        if kind == "h3":
            k += 1
            sub = next((f"{sid}-{v}" for key, v in SUB_IDS.items() if data.startswith(key)), f"{sid}-{k}") if sid == "hooks" else f"{sid}-{k}"
            out.append(f'<h3 class="hb-h3" id="{sub}">{inline(data)}</h3>')
        elif kind == "p":
            out.append(f"<p>{inline(data)}</p>")
        elif kind == "ul":
            out.append('<ul class="hb-list">' + "".join(f"<li>{inline(x)}</li>" for x in data) + "</ul>")
        elif kind == "ol":
            out.append(f'<ol class="lb-steps hb-steps"{tn}>' + "".join(f"<li><div>{inline(x)}</div></li>" for x in data) + "</ol>")
        elif kind == "table":
            out.append(cards(data, sid, sub, copy) if data[0][0] == "#" else table(data))
    return "".join(out)


def count_after(blocks, h3_start, kind):
    """Rows (table) or items (list) under the ### heading that starts with h3_start."""
    on = False
    for b in blocks:
        if b[0] == "h3":
            on = b[1].startswith(h3_start)
        elif on and b[0] == kind:
            return len(b[1]) - (1 if kind == "table" else 0)
    return 0


CSS = """
.lb-section { scroll-margin-top: 5rem; display: grid; gap: var(--sp-3); align-content: start; }
.lb-section[hidden] { display: none; }
.lb-main, .lb-page, .lb-section { min-width: 0; }
.lb-section > h2 { margin: 0 0 var(--sp-2); }
.lb-section > p, .hb-list, .hb-steps { margin: 0; max-width: 60rem; line-height: 1.65; }
.hb-h3 { margin: var(--sp-4) 0 0; scroll-margin-top: 6rem; }
.hb-list { padding-inline-start: 1.2rem; display: grid; gap: .45rem; }
.hb-steps > li > div { line-height: 1.6; }
.hb-top { gap: var(--sp-3); }
.hb-top-title { font-weight: 700; }
.hb-flag { color: var(--warning); font-weight: 700; }
.hb-hero h1 { font-size: clamp(1.7rem, 4vw, 2.5rem); }
.hb-rules { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 20rem), 1fr)); }
.hb-rules .lb-card { display: grid; gap: .4rem; align-content: start; }
.hb-rules p { margin: 0; line-height: 1.6; }
.hb-cubes.lb-metrics { grid-template-columns: repeat(auto-fill, minmax(min(100%, 10.5rem), 1fr)); }
a.lb-metric { text-decoration: none; color: inherit; transition: transform var(--dur-2) var(--ease-spring); }
a.lb-metric:active { transform: scale(var(--press)); }
.hb-cards { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fill, minmax(min(100%, 21rem), 1fr)); align-items: start; }
.hb-card { display: grid; gap: .55rem; scroll-margin-top: 6rem; }
.hb-card.is-flash { animation: hb-flash 1.8s var(--ease); }
@keyframes hb-flash { 0%, 45% { box-shadow: 0 0 0 3px var(--accent), var(--glass-card-lift, none); } 100% { box-shadow: 0 0 0 0 transparent, var(--glass-card-lift, none); } }
.hb-card-head { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem; }
.hb-n { font-family: var(--font-2); font-weight: 800; color: var(--text-3); margin-inline-end: .2rem; }
.hb-headline { margin: 0; font-size: var(--fs-callout); line-height: 1.55; font-weight: 700; }
.hb-card .lb-kv { font-size: var(--fs-footnote); }
.hb-card .lb-kv dd { line-height: 1.5; }
a.hb-ilink { text-decoration: none; }
a.hb-ilink:hover { text-decoration: underline; }
.hb-table td, .hb-table th { vertical-align: top; }
.hb-table td { line-height: 1.55; min-width: 7rem; }
.hb-table td:first-child { font-weight: 600; }
.lb-table-wrap { max-width: 100%; overflow-x: auto; }
@media (max-width: 44rem) {
  .hb-table, .hb-table tbody, .hb-table tr, .hb-table td { display: block; width: auto; }
  .hb-table thead { display: none; }
  .hb-table tr { padding: var(--sp-3) var(--sp-3) var(--sp-2); border-bottom: 1px solid var(--line); }
  .hb-table td { padding: .2rem 0; border: 0; min-width: 0; }
  .hb-table td[data-label]::before { content: attr(data-label); display: block; font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; color: var(--text-3); }
}
@media print { .lb-sidebar, .lb-topbar { display: none; } .lb-app { display: block; } .lb-section[hidden] { display: grid; } }
"""

JS = r"""<script>
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var sections = $$('.lb-section'), items = $$('.lb-sidebar .lb-nav-item'), side = $('.lb-sidebar'), scrim = $('.lb-scrim'), title = $('#hb-title');
  var smooth = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
  function closeNav() { side.classList.remove('is-open'); scrim.hidden = true; }
  function showTab(id, keepScroll) {
    if (!sections.some(function (s) { return s.id === id; })) id = sections[0].id;
    sections.forEach(function (s) { s.hidden = s.id !== id; });
    items.forEach(function (a) {
      if (a.getAttribute('href') === '#' + id) { a.setAttribute('aria-current', 'page'); title.textContent = a.textContent; }
      else a.removeAttribute('aria-current');
    });
    if (!keepScroll) window.scrollTo(0, 0);
  }
  function flash(el) { el.classList.remove('is-flash'); void el.offsetWidth; el.classList.add('is-flash'); }
  function goTo(el) {
    var sec = el.classList.contains('lb-section') ? el : el.closest('.lb-section');
    showTab(sec.id, sec !== el);
    if (sec !== el) { el.scrollIntoView({ behavior: smooth, block: el.tagName === 'H3' ? 'start' : 'center' }); if (el.classList.contains('hb-card')) flash(el); }
  }
  function fromHash() {
    var h = decodeURIComponent(location.hash.slice(1)), el = h && document.getElementById(h);
    if (el && (el.classList.contains('lb-section') || el.closest('.lb-section'))) goTo(el); else showTab('');
  }
  $('#hb-menu').addEventListener('click', function () { side.classList.add('is-open'); scrim.hidden = false; });
  scrim.addEventListener('click', closeNav);
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') closeNav(); });
  items.forEach(function (a) { a.addEventListener('click', function (ev) {
    ev.preventDefault(); closeNav(); showTab(a.getAttribute('href').slice(1));
    history.replaceState(null, '', location.pathname + location.search + a.getAttribute('href'));
  }); });
  // a hook's intent chip and the overview cubes jump to their target in its own section
  $$('a[href^="#"]:not(.lb-nav-item)').forEach(function (a) { a.addEventListener('click', function (ev) {
    var el = document.getElementById(a.getAttribute('href').slice(1));
    if (!el || !el.closest('.lb-section')) return;
    ev.preventDefault(); goTo(el);
    history.replaceState(null, '', location.pathname + location.search + a.getAttribute('href'));
  }); });
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
</script>"""


def build(name):
    global SRC, OUT, PAGE, PAGE_TITLE, BRAND, SECTIONS
    SRC, fn, PAGE_TITLE, BRAND = PAGES[name]
    SECTIONS = SECTIONS_BY_PAGE[name]
    OUT = os.path.join(HERE, fn)
    PAGE = f"research/hanukkah-black-friday-2026/{fn}"
    doc = parse()
    errs = validate(doc)
    if errs:
        print("\n".join(errs))
        sys.exit(1)

    ct = design.categories("content-types")
    hooks = section(doc, "hooks")["blocks"]
    n_int = sum(len(t) - 1 for t in card_tables(section(doc, "intents")))
    n_open = next(len(b[1]) for b in section(doc, "open")["blocks"] if b[0] == "ol")
    cubes = [  # label, number, foot, href, colour class
        ("כוונות קנייה", n_int, "בקצרה: למי ולמה", "#intents", "lb-cat-0"),
        ("רילס", count_after(hooks, "רילס", "table"), "ירין מדבר, בלי מחיר", "#hooks-reels", f'lb-cat-{ct["reel"]["cat"]}'),
        ("קרוסלות ניסוי", count_after(hooks, "קרוסלות ניסוי", "table"), "לאמא או לסבתא", "#hooks-test", f'lb-cat-{ct["test"]["cat"]}'),
        ("קרוסלות ילד", count_after(hooks, "קרוסלות ילד", "table"), "בקול הילד, הנעה לשמירה", "#hooks-kid", f'lb-cat-{ct["kid"]["cat"]}'),
        ("פייסבוק וסטוריז", count_after(hooks, "פוסטים בפייסבוק", "ol") + count_after(hooks, "סטוריז", "ol"), "שורות פתיחה ורעיונות", "#hooks-facebook", f'lb-cat-{ct["post"]["cat"]}'),
        ("מה פתוח", n_open, "החלטות שמחכות לירין", "#open", "is-warn"),
    ]
    ids = {SECTIONS[s["num"]][0] for s in doc["sections"]}
    if "briefs" in ids:   # the campaign sections of the Black Friday page (19 Nov 2026)
        n_briefs = sum(1 for b in section(doc, "briefs")["blocks"] if b[0] == "h3")
        n_must = count_after(section(doc, "tasks")["blocks"], "לפני ההשקה", "table")
        cubes[1:1] = [("בריפים", n_briefs, "ריל, יוצרת, קרוסלה, הדגמה, סטוריז", "#briefs", "lb-cat-0"),
                      ("לפני ההשקה", n_must, "משימות עם בעלים ותאריך", "#tasks", "is-warn")]
    cubes = [c for c in cubes if c[1]]   # a cube for something this page does not have is left out
    cube_html = "".join(f'<a class="lb-metric {cls}" href="{href}"><span class="lb-metric-label">{esc(lab)}</span>'
                        f'<span class="lb-metric-value"><b>{n}</b></span><span class="lb-metric-foot">{esc(foot)}</span></a>'
                        for lab, n, foot, href, cls in cubes)

    # overview: the first intro paragraph, the two rules as cards, the cubes, the rest of the intro folded away
    intro = doc["intro"]
    paras = [b[1] for b in intro if b[0] == "p"]
    rules = next((b[1] for b in intro if b[0] == "ul"), [])
    rule_cards = "".join(f'<div class="lb-card"><p>{inline(x)}</p></div>' for x in rules)
    more = "".join(f"<p>{inline(p)}</p>" for p in paras[1:])
    overview = (
        f'<section class="lb-section" id="overview"><header class="lb-hero hb-hero"><h1>{inline(doc["title"])}</h1>'
        f'<p class="lb-lede">{inline(paras[0]) if paras else ""}</p></header>'
        f'<div class="hb-rules">{rule_cards}</div>'
        f'<div class="lb-metrics hb-cubes">{cube_html}</div>'
        f'<details class="lb-disclosure"><summary><span class="lb-sum">איך לקרוא<small>תוויות, קודי מקור ומה כבר מתוכנן</small></span></summary>'
        f'<div class="lb-disclosure-body">{more}</div></details>'
        f'<p class="lb-note">המקור: <code class="lb-ltr">research/hanukkah-black-friday-2026/{SRC}</code>. הדף נבנה ממנו, '
        f'והחיפושים בגוגל ב <code class="lb-ltr">sources/</code>.</p></section>')

    known = set(design.icons("icons")) | set(design.icons("ui"))
    nav = ['<div class="lb-nav-label">חלקים</div>',
           f'<a class="lb-nav-item" href="#overview"><span class="lb-tile lb-cat-0">{design.icon("home")}</span><span class="lb-nav-text">סקירה</span></a>']
    body = [overview]
    for s in doc["sections"]:
        sid, label, icon = SECTIONS[s["num"]]
        nav.append(f'<a class="lb-nav-item" href="#{sid}"><span class="lb-tile lb-cat-0">{design.icon(icon if icon in known else "file")}</span>'
                   f'<span class="lb-nav-text">{esc(label)}</span></a>')
        body.append(f'<section class="lb-section" id="{sid}" hidden><h2>{inline(s["title"])}</h2>{blocks_html(s["blocks"], sid)}</section>')

    page = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{PAGE_TITLE} · לומבוק</title>
{design.head(page=PAGE)}
<style>{CSS}</style>
</head>
<body>
<div class="lb-app">
  <aside class="lb-sidebar" aria-label="חלקי התוכן">
    <a class="lb-brand" href="#overview"><span><b>{BRAND}</b></span></a>
    <nav class="lb-nav">{"".join(nav)}</nav>
  </aside>
  <div class="lb-scrim" hidden></div>
  <main class="lb-main" id="top">
    <div class="lb-topbar lb-edge"><div class="lb-topbar-in hb-top">
      <button class="lb-btn secondary icon lb-menu-btn" id="hb-menu" type="button" aria-label="פתיחת החלקים">{design.icon("menu")}</button>
      <b class="hb-top-title" id="hb-title">סקירה</b>
    </div></div>
    <div class="lb-page">
      {"".join(body)}
    </div>
  </main>
</div>
{JS}
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {n_int} intents, {len(doc['sections'])} sections, {len(page):,} bytes")


if __name__ == "__main__":
    for n in PAGES:
        build(n)
