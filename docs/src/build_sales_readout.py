#!/usr/bin/env python3
"""Build the sales readout page from the sales data Markdown.

    python3 docs/src/build_sales_readout.py

Input:  docs/lumebook-sales-data-decisions-2026-10-12.md (the only source; edit it, then rebuild, never edit the HTML)
Output: docs/lumebook-sales-readout.html, a full HTML document on the LumeBook design system (design.head() inlined, light only)
        that opens straight from disk.
        Local only, not published: it holds internal sales figures.

How the Markdown becomes the page: the # heading and the paragraphs under it are the hero, every ## heading is a
section (and a pill in the top bar), ### headings are sub-heads. The "At a glance" table becomes figure tiles,
numbered lists become numbered points with the bold lead as their first line, "- [ ]" items become
to-dos whose ticks are saved in the browser (localStorage, keyed by the bold lead), [text](url) becomes a link, the "Numbers not to use" section
sits in a caution panel, and other tables become lb-table tables with numeric columns aligned to the end.
Hebrew runs are wrapped in <bdi> so book titles and cities keep their order inside English text. Standard library only.
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

SRC = ROOT / "docs" / "lumebook-sales-data-decisions-2026-10-12.md"
OUT = ROOT / "docs" / "lumebook-sales-readout.html"
TITLE = "LumeBook Sales Readout"
GLANCE = "At a glance"
CAUTION = "Numbers not to use"

HEB = re.compile(r"[֐-׿][֐-׿׳״' ,.?\-]*[֐-׿׳״'?]|[֐-׿]")
NUM = re.compile(r"^(?:[≈+\-]?[₪$]?\d[\d,.]*%?(?: \(.*\))?|[₪$]\d[\d,.]* and [₪$]\d[\d,.]*|none)$")


def inline(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return HEB.sub(lambda m: f"<bdi>{m.group(0)}</bdi>", t)


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def parse(md):
    """Return (h1, intro blocks, [(h2, blocks)]). A block is (kind, payload)."""
    h1, intro, sections = "", [], []
    blocks = intro
    para, items, rows, kind = [], [], [], None

    def flush():
        nonlocal para, items, rows, kind
        if para:
            blocks.append(("p", " ".join(para)))
        if items:
            blocks.append((kind, items))
        if rows:
            blocks.append(("table", rows))
        para, items, rows, kind = [], [], [], None

    for line in md.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("# "):
            flush(); h1 = s[2:]
        elif s.startswith("## "):
            flush(); blocks = []; sections.append((s[3:], blocks))
        elif s.startswith("### "):
            flush(); blocks.append(("h3", s[4:]))
        elif s.startswith("|"):
            if para or items:
                flush()
            if not re.fullmatch(r"\|[\s:|-]+\|", s):
                rows.append([c.strip() for c in s.strip("|").split("|")])
        elif re.match(r"\d+\. ", s):
            if kind not in (None, "ol") or para or rows:
                flush()
            kind = "ol"; items.append(re.sub(r"^\d+\. ", "", s))
        elif s.startswith("- [ ] "):
            if kind not in (None, "check") or para or rows:
                flush()
            kind = "check"; items.append(s[6:])
        elif s.startswith("- "):
            if kind not in (None, "ul") or para or rows:
                flush()
            kind = "ul"; items.append(s[2:])
        else:
            if items or rows:
                flush()
            para.append(s)
    flush()
    return h1, intro, sections


def point(item):
    m = re.match(r"\*\*(.+?)\*\*\s*(.*)", item)
    if not m:
        return f"<li><div>{inline(item)}</div></li>"
    rest = f'<p>{inline(m.group(2))}</p>' if m.group(2) else ""
    return f'<li><div><h3>{inline(m.group(1))}</h3>{rest}</div></li>'


def table(rows):
    head, body = rows[0], rows[1:]
    numeric = [bool(body) and all(NUM.match(r[i]) for r in body if i < len(r)) for i in range(len(head))]
    cls = [' class="num"' if n else "" for n in numeric]
    th = "".join(f"<th{cls[i]}>{inline(c)}</th>" for i, c in enumerate(head))
    trs = "".join("<tr>" + "".join(f"<td{cls[i] if i < len(cls) else ''}>{inline(c)}</td>" for i, c in enumerate(r)) + "</tr>"
                  for r in body)
    return f'<div class="lb-table-wrap"><table class="lb-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def check(item):
    """A to-do with a stable id (from its bold lead) so a saved tick survives rebuilds."""
    m = re.match(r"\*\*(.+?)\*\*", item)
    cid = "do-" + slug(m.group(1) if m else item)[:48]
    return (f'<li><label class="lb-check" for="{cid}"><input type="checkbox" id="{cid}">'
            f"<span>{inline(item)}</span></label></li>")


def render(blocks):
    out = []
    for kind, val in blocks:
        if kind == "p":
            out.append(f"<p>{inline(val)}</p>")
        elif kind == "h3":
            out.append(f"<h3 class=\"sub\">{inline(val)}</h3>")
        elif kind == "ol":
            out.append('<ol class="points">' + "".join(point(i) for i in val) + "</ol>")
        elif kind == "ul":
            out.append('<ul class="list">' + "".join(f"<li>{inline(i)}</li>" for i in val) + "</ul>")
        elif kind == "table":
            out.append(table(val))
        elif kind == "check":
            out.append('<ul class="checks">' + "".join(check(i) for i in val) + "</ul>")
    return "\n".join(out)


def glance(blocks):
    rows = next((v for k, v in blocks if k == "table"), [])[1:]
    tiles = "".join(f'<div class="lb-card lb-stat"><span class="lb-stat-value">{inline(v)}</span>'
                    f'<span class="lb-stat-foot">{inline(l)}</span></div>' for v, l in rows)
    return f'<div class="glance">{tiles}</div>'


STYLE = """<style>
/* Layout: a one-column readout on the LumeBook design system. Hero with four figures, the plain-words
   sections as numbered points, then the numbers as tables. Light only; page rules use design tokens only. */
:root { --read-w: 72ch; }
.plan-logo { width: 1.75rem; height: 1.75rem; flex: none; display: block; }
.brand { display: grid; line-height: 1.15; flex: none; }
.brand b { font-weight: 800; font-size: var(--fs-headline); letter-spacing: -.01em; }
.brand span { font-size: var(--fs-caption); font-weight: 600; letter-spacing: .02em; color: var(--accent-ink); }
.lb-topbar .lb-toc { flex: 1 1 0; margin-inline-start: var(--sp-3); }
@media (max-width: 860px) {
  .lb-topbar-in { flex-wrap: wrap; row-gap: 0; padding-top: var(--sp-2); }
  .lb-topbar .lb-toc { order: 9; flex-basis: 100%; margin: var(--sp-2) 0 0; padding-bottom: var(--sp-2); }
}
main > section { display: grid; gap: var(--sp-4); min-width: 0; scroll-margin-top: calc(6rem + var(--sp-4)); }
.hero { display: grid; gap: var(--sp-3); padding-top: var(--sp-3); }
.hero h1 { max-width: 24ch; }
.hero p, main > section > p { max-width: var(--read-w); color: var(--text-2); text-wrap: pretty; }
.hero .lb-chip { justify-self: start; }
.glance { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr)); }
.glance .lb-stat-value { color: var(--tint); unicode-bidi: plaintext; }
h3.sub { margin-top: var(--sp-3); }
ol.points { list-style: none; counter-reset: pt; margin: 0; padding: 0; display: grid; gap: var(--sp-3); max-width: 60rem; }
ol.points > li { counter-increment: pt; display: grid; grid-template-columns: 2rem minmax(0, 1fr); gap: var(--sp-3);
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-4); }
ol.points > li::before { content: counter(pt); display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: 50%;
  background: var(--tint-soft); color: var(--tint); font-weight: 700; font-variant-numeric: tabular-nums; }
ol.points > li > div { display: grid; gap: var(--sp-1); min-width: 0; }
ol.points p { margin: 0; color: var(--text-2); text-wrap: pretty; }
ul.list { margin: 0; padding-inline-start: 1.2rem; display: grid; gap: var(--sp-2); max-width: var(--read-w); }
ul.list li::marker { color: var(--accent); }
.lb-table td.num, .lb-table th.num { unicode-bidi: plaintext; }
.lb-table-wrap { max-width: 60rem; }
.checks { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); max-width: 60rem; }
.checks li { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); }
.checks .lb-check { font-size: var(--fs-body); line-height: 1.5; }
.checks .lb-check span { color: var(--text-2); text-wrap: pretty; }
.checks .lb-check b { color: var(--text); }
.checks .lb-check input:checked + span b { color: var(--text-3); }
.done { font-size: var(--fs-footnote); color: var(--text-3); font-variant-numeric: tabular-nums; }
main a { color: var(--tint); }
.caution { display: grid; gap: var(--sp-3); padding: var(--sp-4) var(--sp-5); border-radius: var(--r-lg);
  background: var(--warning-soft); border: 1px solid var(--line); max-width: 60rem; }
.caution ul.list li::marker { color: var(--warning); }
code { font-size: .9em; background: var(--fill); border-radius: var(--r-xs); padding: .05em .35em; overflow-wrap: anywhere; }
bdi { unicode-bidi: isolate; }
main p, main li, .lb-table td { overflow-wrap: anywhere; } /* long URLs and file paths wrap at phone width */
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
html { scroll-behavior: smooth; }
</style>"""


CHECK_JS = """<script>
(function () {
  var KEY = "lumebook-sales-readout-done", saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) {}
  var boxes = [].slice.call(document.querySelectorAll(".checks input[type=checkbox]"));
  function count() {
    var n = boxes.filter(function (b) { return b.checked; }).length;
    document.querySelectorAll("[data-done]").forEach(function (el) { el.textContent = n + " of " + boxes.length + " done"; });
  }
  boxes.forEach(function (b) {
    if (saved[b.id]) b.checked = true;
    b.addEventListener("change", function () {
      saved[b.id] = b.checked ? 1 : 0;
      try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
      count();
    });
  });
  count();
})();
</script>"""


def build():
    h1, intro, sections = parse(SRC.read_text(encoding="utf-8"))
    pills, body = [], []
    for title, blocks in sections:
        sid = slug(title)
        if title == GLANCE:
            continue
        pills.append(f'<a href="#{sid}">{inline(title)}</a>')
        inner = render(blocks)
        if title == CAUTION:
            inner = f'<div class="caution">{inner}</div>'
        head = f'<h2>{inline(title)}</h2>'
        if '<ul class="checks">' in inner:
            head = f'<div class="lb-section-head">{head}<span class="done" data-done></span></div>'
        body.append(f'<section id="{sid}">\n{head}\n{inner}\n</section>')
    glance_blocks = next((b for t, b in sections if t == GLANCE), [])
    hero = (f'<section class="hero" id="top">\n<span class="lb-chip warning">Internal: holds sales figures</span>\n'
            f'<h1>{inline(h1)}</h1>\n{render(intro)}\n{glance(glance_blocks) if glance_blocks else ""}\n</section>')
    page = f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="robots" content="noindex, nofollow">
{design.head()}
{STYLE}
</head>
<body>
<header class="lb-topbar">
  <div class="lb-topbar-in">
    <img class="plan-logo" src="{design.logo_data_uri()}" alt="" width="28" height="28">
    <div class="brand"><span>LumeBook</span><b>Sales readout</b></div>
    <nav class="lb-toc" aria-label="Sections">{"".join(pills)}</nav>
  </div>
</header>
<main class="lb-page" dir="ltr" lang="en">
{hero}
{chr(10).join(body)}
<p class="lb-note">Built from <code>docs/lumebook-sales-data-decisions-2026-10-12.md</code> by <code>docs/src/build_sales_readout.py</code>. Edit the Markdown, then rebuild.</p>
</main>
{CHECK_JS}
</body>
</html>
"""
    if "—" in page:
        raise SystemExit("em dash in the page; fix the Markdown")
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page) // 1024} KB, {len(sections)} sections)")


if __name__ == "__main__":
    build()
