#!/usr/bin/env python3
"""Build the designed RTL page for the LumeBook carousel playbook.

Input:  ../../docs/lumebook-instagram-carousel-playbook-he.md
Output: lumebook-carousel-playbook.html (next to this script)
Needs the `markdown` package (PYTHONPATH=<dir with markdown> python3 build_page.py).
Styled with the LumeBook design system (shared/design): design.head() is inlined, page.css adds the page rules.
"""
import html, json, os, re, sys
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # project root (research/<this folder>)
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
import design  # LumeBook design system: tokens, components, theme toggle, logo

SRC = os.path.join(ROOT, "docs/lumebook-instagram-carousel-playbook-he.md")
SRC_DIR = os.path.relpath(os.path.dirname(SRC), ROOT)  # local links in the markdown are relative to docs/
OUT = os.path.join(HERE, "lumebook-carousel-playbook.html")
HUB = "https://claude.ai/artifact/R5tEXfKkNKzVYg8CWFh4s6"  # LumeBook HQ

md_text = open(SRC, encoding="utf-8").read()
md_text = md_text.replace('<div dir="rtl">', "").replace("</div>", "").strip()

# ---------- split into sections ----------
parts = re.split(r"\n(?=## \d+\. )", md_text)
front = parts[0]
sections = {}
titles = {}
for p in parts[1:]:
    m = re.match(r"## (\d+)\. (.*)\n", p)
    n = int(m.group(1))
    titles[n] = m.group(2).strip()
    body = p[m.end():].strip()
    body = re.sub(r"\n---\s*$", "", body).strip()
    sections[n] = body

# ---------- markdown helpers ----------
LINK_RE = re.compile(r"\[[^\]\n]*\]\([^)\n]*\)")

def link_refs(text):
    """Turn 'סעיף 9.7' / 'קונספט 3' into in-page links, outside existing links and headings."""
    out_lines = []
    for line in text.split("\n"):
        if line.lstrip().startswith("#"):
            out_lines.append(line); continue
        keep = []
        def protect(m):
            keep.append(m.group(0)); return f"\u0000{len(keep)-1}\u0000"
        line = LINK_RE.sub(protect, line)
        line = re.sub(r"סעיף (\d+)((?:\.\d+)?)", lambda m: f"[סעיף {m.group(1)}{m.group(2)}](#s{m.group(1)})" if 1 <= int(m.group(1)) <= 19 else m.group(0), line)
        line = re.sub(r"קונספט (\d+)", lambda m: f"[קונספט {m.group(1)}](#c{m.group(1)})" if 1 <= int(m.group(1)) <= 12 else m.group(0), line)
        line = re.sub(r"\u0000(\d+)\u0000", lambda m: keep[int(m.group(1))], line)
        out_lines.append(line)
    return "\n".join(out_lines)

TAGS = [
    ("מבוסס היטב", "t-good"), ("נתמך חלקית", "t-part"), ("Best practice", "t-prac"),
    ("השערה לניסוי", "t-hypo"), ("השערה", "t-hypo"), ("מחקר/תקן", "t-good"),
    ("מקצועי", "t-prac"), ("מוסכמה", "t-conv"),
]
TAG_RE = re.compile(r"\[(" + "|".join(re.escape(t) for t, _ in TAGS) + r")([^\]\[]*)\]")
TAG_CLASS = dict(TAGS)
CHIP = {"t-good": "success", "t-part": "warning", "t-prac": "tint", "t-hypo": "outline", "t-conv": "", "t-bad": "danger"}

def tag(cls, text):
    classes = " ".join(c for c in ("tag", "lb-chip", CHIP[cls], cls) if c)
    return f'<span class="{classes}">{text}</span>'

def project_path(href):
    """A local link in the markdown (relative to docs/) as a path from the project root, keeping a folder's trailing /."""
    p = os.path.normpath(os.path.join(SRC_DIR, href))
    return p + "/" if href.endswith("/") else p

def post_html(h):
    # evidence chips
    h = TAG_RE.sub(lambda m: tag(TAG_CLASS[m.group(1)], m.group(1) + m.group(2)), h)
    for word, cls in [("מבוסס היטב", "t-good"), ("נתמך חלקית", "t-part"), ("שנוי במחלוקת", "t-bad"), ("חלש מאוד", "t-bad"), ("חלש", "t-bad")]:
        h = h.replace(f"<strong>{word}</strong>", tag(cls, word))
    # local file links become non-clickable file chips; the title gives the path from the project root
    h = re.sub(r'<a href="(?!https?:|#)([^"]+)">(.*?)</a>', lambda m: f'<span class="file" dir="auto" title="בתיקיית הפרויקט: {html.escape(project_path(html.unescape(m.group(1))))}">{m.group(2)}</span>', h)
    # external links open in a new tab
    h = re.sub(r'<a href="(https?:[^"]+)">', r'<a href="\1" target="_blank" rel="noopener">', h)
    # tables scroll inside their own box
    def wrap_table(m):
        t = m.group(0)
        cols = len(re.findall(r"<th", t.split("</tr>")[0]))
        cls = "wide" if cols >= 5 else ("mid" if cols == 4 else "")
        t = t.replace("<table>", f'<table class="{" ".join(c for c in ("lb-table", "top", cls) if c)}">', 1)
        return f'<div class="tbl lb-table-wrap">{t}</div>'
    h = re.sub(r"<table>.*?</table>", wrap_table, h, flags=re.S)
    # checklists (the whole line is the label, so tapping the text ticks the box)
    h = re.sub(r"<li>\[ \] (.*?)</li>", lambda m: f'<li class="check"><label class="lb-check"><input type="checkbox"><span>{m.group(1)}</span></label></li>', h, flags=re.S)
    # blockquotes are captions / formulas
    h = h.replace("<blockquote>", '<blockquote class="quote lb-callout">')
    return h

def md(text):
    text = link_refs(text)
    text = re.sub(r"^(   )(?=[-\d])", "    ", text, flags=re.M)  # 3-space nesting -> 4
    # a list straight after a paragraph line needs a blank line for Python-Markdown
    text = re.sub(r"(\n(?![ \t]*(?:- |\d+\. |\||>|#))[^\n]+)\n(?=- |\d+\. )", r"\1\n\n", "\n" + text)[1:]
    h = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    return post_html(h)

def inline(text):
    h = markdown.markdown(text.strip())
    h = re.sub(r"^<p>|</p>$", "", h.strip())
    return post_html(h)

# ---------- concepts ----------
c_body = sections[19]
c_parts = re.split(r"\n(?=### קונספט \d+ )", c_body)
concept_intro = c_parts[0].rstrip("-").strip()
concepts = []
for cp in c_parts[1:]:
    cp = re.sub(r"\n---\s*$", "", cp.strip()).strip()
    hm = re.match(r"### קונספט (\d+) · ([^·\n]*?)(?: · ([^\n]*))?\n", cp)
    num, topic = int(hm.group(1)), hm.group(2).strip()
    name = (hm.group(3) or "").strip().strip('"')
    if not name:
        name, topic = topic, "התצוגה המקדימה"
    rest = cp[hm.end():]
    # meta table
    tm = re.search(r"\| \| \|\n\|---\|---\|\n((?:\|[^\n]*\n)+)", rest + "\n")
    meta = {}
    for row in tm.group(1).strip().split("\n"):
        cells = [c.strip() for c in row.strip("|").split("|")]
        meta[re.sub(r"\*", "", cells[0])] = cells[1]
    # slides block
    sm = re.search(r"\*\*השקופיות\*\*\n\n(.*?)(?=\n\n\*\*הגשר למוצר)", rest, flags=re.S)
    slides_md = sm.group(1)
    pre_slides = rest[tm.end():sm.start()].strip()
    after = rest[sm.end():].strip()
    slides = []
    for block in re.split(r"\n(?=\d+\. )", "\n" + slides_md.strip()):
        block = block.strip()
        if not block: continue
        first, *subs = block.split("\n")
        fm = re.match(r"(\d+)\. (?:\*\*(.*?)\*\*)?\s*(?:· (?:פריסה )?(P\d)(?: \((.*?)\))?)?", first)
        s = {"n": int(fm.group(1)), "role": fm.group(2) or "המשך הסיפור", "layout": fm.group(3) or "P2", "items": []}
        for sub in subs:
            sub = sub.strip()
            if not sub.startswith("- "): continue
            sub = sub[2:]
            km = re.match(r'(טקסט|שורה קטנה|שורה שנייה|שורה גדולה שנייה|עיצוב|מקור קטן על השקופית|מקור קטן בתחתית|מקור קטן|מקור|"במקום"|"אפשר לנסות"|למה, בשורה קטנה):\s*(.*)', sub)
            if km:
                s["items"].append((km.group(1).strip('"'), km.group(2)))
            else:
                s["items"].append(("plain", sub))
        slides.append(s)
    concepts.append({"n": num, "topic": topic, "name": name, "meta": meta, "pre": pre_slides, "slides": slides, "after": after})

def tile_html(s):
    lay = s["layout"]
    on, notes, copy = [], [], []
    for key, val in s["items"]:
        if key in ("עיצוב", "מקור"):
            notes.append((key, val)); continue
        plain = re.sub(r"\*\*|\[|\]", "", re.sub(r"\]\([^)]*\)", "]", val))
        if key == "טקסט":
            on.append(f'<div class="t-main">{inline(val)}</div>'); copy.append(plain)
        elif key in ("שורה שנייה", "שורה גדולה שנייה"):
            on.append(f'<div class="t-second">{inline(val)}</div>'); copy.append(plain)
        elif key in ("שורה קטנה", "למה, בשורה קטנה"):
            on.append(f'<div class="t-small">{inline(val)}</div>'); copy.append(plain)
        elif key in ("מקור קטן", "מקור קטן על השקופית", "מקור קטן בתחתית"):
            on.append(f'<div class="t-src">{inline(val)}</div>')
        elif key == "במקום":
            on.append(f'<div class="swap swap-a"><span>במקום</span>{inline(val)}</div>'); copy.append("במקום: " + plain)
        elif key == "אפשר לנסות":
            on.append(f'<div class="swap swap-b"><span>אפשר לנסות</span>{inline(val)}</div>'); copy.append("אפשר לנסות: " + plain)
        elif key == "plain":
            if re.match(r"\d+\.", val) or not val.startswith("("):
                on.append(f'<div class="t-item">{inline(val)}</div>'); copy.append(plain)
            else:
                notes.append(("הערה", val))
    # asset placeholders
    asset = ""
    for key, val in notes:
        am = re.search(r"\[([^\]]+)\]", val)
        if key == "עיצוב" and am and lay in ("P5", "P6"):
            asset = f'<div class="asset">{html.escape(am.group(1))}</div>'
            break
    num_badge = f'<div class="t-num">{s["n"]}</div>' if lay == "P3" else ""
    tile = f'<div class="slide L{lay[1:]}"><div class="slide-in">{num_badge}{"".join(on)}{asset}<div class="brandmark">לומבוק</div></div></div>'
    note_html = "".join(f'<p><b>{html.escape(k)}:</b> {inline(v)}</p>' for k, v in notes)
    return tile, note_html, copy

def concept_page(c):
    meta_rows = "".join(f"<tr><th>{html.escape(k)}</th><td>{inline(v)}</td></tr>" for k, v in c["meta"].items())
    strip, copy_lines = [], []
    for s in c["slides"]:
        tile, notes, copy = tile_html(s)
        copy_lines.append(f'שקופית {s["n"]} ({s["role"]}): ' + " / ".join(copy))
        strip.append(f'<figure class="slot"><figcaption><span class="snum lb-count is-tint">{s["n"]}</span> {html.escape(s["role"])} <span class="lay">{s["layout"]}</span></figcaption>{tile}<div class="snotes">{notes}</div></figure>')
    copy_text = "\n".join(copy_lines)
    return f'''
<header class="sec-head"><p class="eyebrow lb-eyebrow">קונספט {c["n"]} מתוך 12 · {html.escape(c["topic"])}</p><h1>{html.escape(c["name"])}</h1></header>
<div class="tbl lb-table-wrap meta"><table class="lb-table top"><tbody>{meta_rows}</tbody></table></div>
{f'<div class="pre lb-prose">{md(c["pre"])}</div>' if c["pre"] else ""}
<div class="strip-head"><h2>השקופיות</h2><button class="lb-btn secondary sm copy" type="button" data-copy="{html.escape(copy_text)}">העתקת הטקסט לכל השקופיות</button></div>
<p class="hint lb-note">התצוגה היא סקיצה של הטקסט והפריסה, לא עיצוב סופי. החליקו כדי לראות את כל השקופיות. מתחת לכל שקופית: הוראות העיצוב והמקור.</p>
<div class="lb-scroller snap" tabindex="0" aria-label="שקופיות קונספט {c["n"]}">{"".join(strip)}</div>
<div class="after lb-prose">{md(c["after"])}</div>
'''

# ---------- navigation ----------
NAV = [
    ("התחלה", [1, 2, 3]),
    ("למה זה עובד", [4]),
    ("איך בונים קרוסלה", [5, 6, 7, 8, 9, 10, 11, 12]),
    ("שוק ולקחים", [13, 14]),
    ("עבודה שוטפת", [15, 16, 17]),
    ("קונספטים מוכנים", [19]),
    ("מקורות", [18]),
]
SHORT = {1: "תקציר מנהלים", 2: "מה נחשב המרה", 3: "הממצאים החשובים", 4: "פסיכולוגיה", 5: "אנטומיה של קרוסלה", 6: "מבנים ו-6 תבניות", 7: "ספריית Hooks", 8: "קופירייטינג בעברית", 9: "מערכת עיצוב", 10: "שילוב המוצר", 11: "אמון והתנגדויות", 12: "ספריית CTA", 13: "דוגמאות מהשוק", 14: "טעויות נפוצות", 15: "Checklist לפני פרסום", 16: "תוכנית ניסויים", 17: "מערכת מדידה", 18: "מקורות", 19: "12 קונספטים"}

nav_html = []
for group, nums in NAV:
    items = []
    for n in nums:
        items.append(f'<a class="lb-nav-item" href="#s{n}" data-route="s{n}"><span class="nn">{n}</span>{SHORT[n]}</a>')
        if n == 19:
            sub = "".join(f'<a class="lb-nav-item sub" href="#c{c["n"]}" data-route="c{c["n"]}"><span class="nn">{c["n"]}</span>{html.escape(c["topic"])}</a>' for c in concepts)
            items.append(f'<div class="subs">{sub}</div>')
    nav_html.append(f'<div class="nav-group lb-nav"><p class="nav-label lb-nav-label">{group}</p>{"".join(items)}</div>')
nav_html = "".join(nav_html)

# top bar section nav: one pill per group, lit while any of its routes is open
def group_routes(nums):
    routes = [f"s{n}" for n in nums]
    if 19 in nums:
        routes += [f"c{c['n']}" for c in concepts]
    return " ".join(routes)
toc_html = "".join(f'<a href="#s{nums[0]}" data-routes="{group_routes(nums)}">{group}</a>' for group, nums in NAV)

order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19] + [f"c{c['n']}" for c in concepts] + [18]

def pager(route):
    i = order.index(route)
    def label(r):
        return SHORT[r] if isinstance(r, int) else f"קונספט {r[1:]}"
    def rid(r):
        return f"s{r}" if isinstance(r, int) else r
    prev = f'<a class="prev" href="#{rid(order[i-1])}"><small>הקודם</small><b>{label(order[i-1])}</b></a>' if i > 0 else ""
    nxt = f'<a class="next" href="#{rid(order[i+1])}"><small>הבא</small><b>{label(order[i+1])}</b></a>' if i < len(order) - 1 else ""
    return f'<nav class="lb-pager" aria-label="ניווט בין סעיפים">{prev}{nxt}</nav>'

# ---------- home extras ----------
FLOW = ["רגע ספציפי + גיל", "הזדהות", "2 עד 3 כלים עם מקור", "סיפור ככלי", "עמוד אמיתי מהספר", "משלמים רק אם אהבתם", "צרו תצוגה מקדימה בחינם"]
flow_html = '<ol class="flow" aria-label="הנוסחה">' + "".join(f'<li{" class=cta" if i == len(FLOW)-1 else ""}><span>{i+1}</span>{t}</li>' for i, t in enumerate(FLOW)) + "</ol>"
home_head = f'''
<header class="lb-hero">
  <p class="eyebrow lb-eyebrow">פלייבוק · גרסה 1 · 6.10.2026</p>
  <h1>קרוסלות שמובילות מהרגע האמיתי של הילד <em>לתצוגה מקדימה בחינם</em></h1>
  <p class="lede lb-lede">איך לכתוב, לבנות, לעצב ולמדוד קרוסלות Instagram של לומבוק, על בסיס מחקר: תיעוד של Meta, כ-110 מאמרים, ניתוח של כ-108 קרוסלות מהשוק, ו-12 קונספטים מוכנים ל-Canva.</p>
  {flow_html}
  <p class="flow-note lb-note">ברירת המחדל, עד שהניסויים יגידו אחרת: 8 עד 9 שקופיות · 1080x1440 · רעיון אחד בשקופית · המוצר אחרי הערך לקהל קר</p>
  <div class="quick lb-row">
    <a class="lb-btn" href="#s19">12 הקונספטים</a>
    <a class="lb-btn secondary" href="#s15">Checklist לפני פרסום</a>
    <a class="lb-btn secondary" href="#s16">תוכנית 12 שבועות</a>
  </div>
</header>
<div class="legend lb-row">{tag("t-good", "מבוסס היטב")}{tag("t-part", "נתמך חלקית")}{tag("t-prac", "Best practice")}{tag("t-hypo", "השערה לניסוי")}{tag("t-bad", "שנוי במחלוקת / חלש")}</div>
'''

concept_cards = "".join(
    f'''<a class="ccard lb-card" href="#c{c["n"]}"><span class="cnum">{c["n"]}</span><span class="ctopic lb-chip tint">{html.escape(c["topic"])}</span><span class="cname">{html.escape(c["name"])}</span><span class="cmeta">{html.escape(re.sub(r"[*`]", "", c["meta"].get("תבנית", "")))}</span><span class="ccta">{html.escape(re.sub(r"[*`]", "", c["meta"].get("CTA", "")))}</span></a>'''
    for c in concepts)

# ---------- pages ----------
pages = []
for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:
    if n == 19:
        body = md(concept_intro) + f'<div class="cgrid lb-grid">{concept_cards}</div>'
    elif n == 1:
        # the formula is drawn in the hero, so drop its text version here
        body = md(re.sub(r"\*\*הנוסחה ללומבוק.*?\n\n(?=\*\*מה לעשות)", "", sections[1], flags=re.S))
    else:
        body = md(sections[n])
    head = home_head if n == 1 else f'<header class="sec-head"><p class="eyebrow lb-eyebrow">סעיף {n}</p><h1>{html.escape(titles[n])}</h1></header>'
    pages.append(f'<section class="page" id="s{n}" data-page="s{n}" hidden>{head}<div class="prose lb-prose">{body}</div>{pager(n)}</section>')
for c in concepts:
    r = f"c{c['n']}"
    pages.append(f'<section class="page" id="{r}" data-page="{r}" hidden>{concept_page(c)}{pager(r)}</section>')

logo_uri = design.logo_data_uri()

CSS = open(os.path.join(HERE, "page.css"), encoding="utf-8").read()
JS = open(os.path.join(HERE, "page.js"), encoding="utf-8").read()

page = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>פלייבוק קרוסלות לומבוק</title>
<meta name="description" content="פלייבוק קרוסלות Instagram ללומבוק: מחקר, תבניות, עיצוב, מדידה ו-12 קונספטים.">
{design.head()}
<style>{CSS}</style>
<div class="pb-root" dir="rtl" lang="he">
  <header class="lb-topbar has-toc"><div class="lb-topbar-in">
    <button class="menu lb-btn secondary sm lb-menu-btn" type="button" aria-expanded="false" aria-controls="nav">תוכן</button>
    <a class="lb-brand" href="#s1"><img src="{logo_uri}" alt="" width="28" height="28"><span><b>פלייבוק קרוסלות</b></span></a>
    <nav class="lb-toc" aria-label="חלקי הפלייבוק">{toc_html}</nav>
    <span class="lb-spacer"></span>
    <span class="bar-meta">לומבוק · 6.10.2026</span>
    <a class="lb-btn ghost sm" href="{HUB}" target="_blank" rel="noopener">ללוח</a>
  </div></header>
  <div class="app lb-app">
    <aside class="nav lb-sidebar" id="nav" aria-label="תוכן הפלייבוק">
      <a class="nav-brand lb-brand" href="#s1"><span><b>פלייבוק קרוסלות</b><small>לומבוק · Instagram</small></span></a>
      {nav_html}
    </aside>
    <div class="scrim lb-scrim" hidden></div>
    <main class="main lb-main" id="main"><div class="lb-page">
      {"".join(pages)}
    </div></main>
  </div>
  <div class="toast lb-toast" role="status" aria-live="polite" hidden></div>
</div>
<script>{JS}</script>
'''
open(OUT, "w", encoding="utf-8").write(page)
print("wrote", OUT, len(page), "bytes;", len(concepts), "concepts;", sum(len(c["slides"]) for c in concepts), "slides")
