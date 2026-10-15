#!/usr/bin/env python3
"""Build the full research page (for Yarin) from the markdown files.

    python3 research/israeli-product-reels/src/build_research_page.py

Inputs:  research/israeli-product-reels/README.md, playbook.md, breakdowns.md, source-index.md
         media/projects/2026-10-15-israeli-product-reels/annotated/*.jpg (embedded as data: URIs;
         skipped with a note if the media folder is missing)
Output:  research/israeli-product-reels/reels-research.html, an artifact page (no doctype: the
         artifact host wraps it) styled with the LumeBook design system, one view per section,
         hash routes (#overview, #concept-1, #dive-3, ...).

Edit the markdown, then rebuild; never edit the HTML. Standard library only.
"""
import base64
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIR = HERE.parent
ROOT = HERE.parents[2]
MEDIA = ROOT / "media" / "projects" / "2026-10-15-israeli-product-reels" / "annotated"
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

OUT = DIR / "reels-research.html"
TITLE = "Product Reels Playbook"

# A Hebrew run; a straight or Hebrew quote on either side stays inside it so the quotes stay paired
HEB = re.compile(r"[\"״]?[\u0590-\u05FF](?:[\u0590-\u05FF0-9\s'״׳\-.,:?!·%₪]*[\u0590-\u05FF?!])?[\"״]?")


# ---------- markdown (the subset these files use) ----------

def bdi(text):
    """Wrap Hebrew runs in text (outside tags) so they keep their direction inside English lines."""
    parts = re.split(r"(<[^>]+>)", text)
    for i, p in enumerate(parts):
        if p and not p.startswith("<"):
            parts[i] = HEB.sub(lambda m: f'<bdi lang="he">{m.group(0)}</bdi>', p)
    return "".join(parts)


def inline(text, rtl=False):
    keep = []

    def stash(s):
        keep.append(s)
        return f"\x00{len(keep) - 1}\x00"

    text = re.sub(r"<br\s*/?>", lambda m: stash("<br>"), text)
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", lambda m: stash(f'<code dir="ltr">{m.group(1)}</code>'), text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                  lambda m: stash(f'<a href="{m.group(2)}" target="_blank" rel="noopener">') + m.group(1) + stash("</a>"), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r"\1", text)          # local file links: keep the label
    text = re.sub(r"(?<![\"'>])(https?://[^\s<)|]+)", lambda m: stash(f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>'), text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    if not rtl:
        text = bdi(text)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], text)


def img_tag(alt, path):
    name = Path(path).name
    f = MEDIA / name
    if not f.exists():
        return f'<p class="lb-note">Frame strip {html.escape(name)} is not on this machine (media folder missing).</p>'
    uri = "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()
    return (f'<figure class="rr-strip"><div class="rr-strip-scroll" tabindex="0" aria-label="{html.escape(alt)}">'
            f'<img src="{uri}" alt="{html.escape(alt)}" loading="lazy"></div>'
            f'<figcaption>Annotated frames with timestamps. Scroll sideways to see every frame.</figcaption></figure>')


def table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    head, body = cells[0], cells[2:]
    out = ['<div class="lb-table-wrap"><table class="lb-table"><thead><tr>']
    out += [f"<th>{inline(h)}</th>" for h in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def render(md, rtl=False):
    """Markdown blocks to HTML. Handles headings, paragraphs, lists, tables, code fences, images,
    rules and <div dir="rtl"> Hebrew blocks."""
    lines = md.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s or s == "---":
            i += 1
            continue
        if s.startswith("<div dir=\"rtl\""):
            j = i + 1
            while j < len(lines) and lines[j].strip() != "</div>":
                j += 1
            out.append(f'<div class="rr-he" dir="rtl" lang="he">{render(chr(10).join(lines[i + 1:j]), rtl=True)}</div>')
            i = j + 1
            continue
        if s.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            out.append(f'<pre class="rr-pre" dir="ltr"><code>{html.escape(chr(10).join(lines[i + 1:j]))}</code></pre>')
            i = j + 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{inline(m.group(2), rtl)}</h{lvl}>")
            i += 1
            continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", s)
        if m:
            out.append(img_tag(m.group(1), m.group(2)))
            i += 1
            continue
        if s.startswith("|"):
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            out.append(table(lines[i:j]))
            i = j
            continue
        if re.match(r"^(-|\d+\.)\s+", s):
            ordered = bool(re.match(r"^\d+\.", s))
            items, j = [], i
            while j < len(lines) and re.match(r"^\s*(-|\d+\.)\s+", lines[j]):
                item = re.sub(r"^\s*(-|\d+\.)\s+", "", lines[j])
                j += 1
                while j < len(lines) and lines[j].startswith("  ") and lines[j].strip() and not re.match(r"^\s*(-|\d+\.)\s+", lines[j]):
                    item += " " + lines[j].strip()
                    j += 1
                items.append(f"<li>{inline(item, rtl)}</li>")
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            i = j
            continue
        para, j = [], i
        while j < len(lines) and lines[j].strip() and not re.match(r"^(#{1,4}\s|\||<div|```|!\[|-\s|\d+\.\s)", lines[j].strip()):
            para.append(lines[j].strip())
            j += 1
        if not para:          # a line no rule above took: show it as text rather than loop
            para, j = [s], i + 1
        out.append(f"<p>{inline(' '.join(para), rtl)}</p>")
        i = j
    return "\n".join(out)


def sections(md, level):
    """Split markdown at headings of one level: [(title, body)], with the text before the first heading as ('', body)."""
    marker = "#" * level + " "
    out, title, buf = [], "", []
    for line in md.splitlines():
        if line.startswith(marker):
            out.append((title, "\n".join(buf)))
            title, buf = line[len(marker):].strip(), []
        else:
            buf.append(line)
    out.append((title, "\n".join(buf)))
    return out


def read(name):
    return (DIR / name).read_text(encoding="utf-8")


# ---------- content ----------

readme = dict(sections(read("README.md"), 2))
play = sections(read("playbook.md"), 2)
play_intro = play[0][1].split("\n", 2)[-1]           # drop the H1 line
P = {t.split(". ", 1)[0]: (t, b) for t, b in play[1:]}
dives = sections(read("breakdowns.md"), 2)
dives_intro = dives[0][1].split("\n", 2)[-1]
D = [(t, b) for t, b in dives[1:] if re.match(r"^\d\.", t)]
dive_howto = next(b for t, b in dives[1:] if t.startswith("How to read"))
sources = read("source-index.md").split("\n", 2)[-1]


def head(title, eyebrow, lede=""):
    led = f'<p class="lb-lede">{inline(lede)}</p>' if lede else ""
    return f'<header class="rr-head"><span class="lb-eyebrow">{eyebrow}</span><h2>{inline(title)}</h2>{led}</header>'


def prose(md):
    return f'<div class="lb-prose rr-md">{render(md)}</div>'


V = {}

# Overview: the README's answer, the five Reels, what to film first
V["overview"] = (
    head("What to film for LumeBook, and how", "Overview · 15 Oct 2026",
         "41 Israeli creator Reels from 34 creators, watched frame by frame, turned into a filming plan for one phone, one home and no child on camera.")
    + '<div class="lb-grid cols-4 rr-stats">'
    + "".join(f'<div class="lb-stat"><span class="lb-stat-label">{a}</span><span class="lb-stat-value">{b}</span><span class="lb-stat-foot">{c}</span></div>'
              for a, b, c in [("Reels watched", "47", "41 verified, 6 excluded"), ("Creators", "34", "458 to about 54K followers"),
                              ("Deep dives", "8", "second by second"), ("LumeBook concepts", "5", "Hebrew scripts, linted")])
    + "</div>"
    + '<section class="lb-card rr-card"><h3>Bottom line</h3>' + prose(readme["Bottom line"]) + "</section>"
    + '<section class="lb-card rr-card"><h3>Watch these five first</h3>' + prose(readme["Watch these five first"]) + "</section>"
    + '<section class="lb-card rr-card rr-film"><h3>Film this first</h3>' + prose(readme["Film this first"])
    + '<p><a class="lb-btn" href="#shoot">Open the 60-90 minute shoot plan</a> <a class="lb-btn secondary" href="#concept-1">Concept 1 script</a></p></section>'
)

V["findings"] = head(P["1"][0].split(". ", 1)[1], "Findings", "Observed counts first, my reading after each.") + prose(play_intro + "\n\n" + P["1"][1])
V["approaches"] = head(P["2"][0].split(". ", 1)[1], "Findings") + prose(P["2"][1])
V["fixes"] = head(P["3"][0].split(". ", 1)[1], "Findings") + prose(P["3"][1])

concepts = sections(P["4"][1], 3)
V["concepts"] = head("Five LumeBook Reel concepts", "Concepts") + prose(concepts[0][1]) + \
    '<div class="lb-grid cols-2 rr-concepts">' + "".join(
        f'<a class="lb-card rr-concept-link" href="#concept-{n}"><span class="rr-n">{n}</span><span>{inline(t.split(":", 1)[1].strip())}</span></a>'
        for n, (t, _) in enumerate(concepts[1:], 1)) + "</div>"
for n, (t, b) in enumerate(concepts[1:], 1):
    V[f"concept-{n}"] = head(t.split(":", 1)[1].strip(), f"Concept {n} of 5") + prose(b)

V["shoot"] = head(P["5"][0].split(". ", 1)[1], "Filming") + prose(P["5"][1])
V["setup"] = head(P["6"][0].split(". ", 1)[1], "Filming") + prose(P["6"][1])
V["log"] = head(P["7"][0].split(". ", 1)[1], "Filming") + prose(P["7"][1])

V["dives"] = head("Eight Reels, broken down", "Deep dives") + prose(dives_intro) + prose("## How to read the breakdowns\n" + dive_howto)
for n, (t, b) in enumerate(D, 1):
    V[f"dive-{n}"] = head(t.split(". ", 1)[1], f"Deep dive {n} of 8") + prose(b) + \
        (f'<p class="rr-next"><a class="lb-btn secondary" href="#dive-{n + 1}">Next deep dive</a></p>' if n < len(D) else "")

V["sources"] = head("Sources", "Reference", "Every Reel watched, with link, date, relationship, disclosure and public counts on 15 Oct 2026.") + prose(sources)
V["limits"] = head("Method and limits", "Reference") + prose(readme["Evidence limits"]) + prose("## Rebuild\n" + readme["Rebuild"]) + \
    prose("## Files\nThe page is built from `README.md`, `playbook.md`, `breakdowns.md` and `source-index.md` in `research/israeli-product-reels/` by `src/build_research_page.py`. The creator brief is a separate page.")

# ---------- navigation ----------

ICON = {
    "overview": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    "findings": '<path d="M4 19V5M4 19h16"/><path d="M8 15l3-4 3 2 4-6"/>',
    "approaches": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "fixes": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    "concepts": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "concept": '<rect x="6" y="3" width="12" height="18" rx="2"/><path d="M10 7h4"/>',
    "shoot": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "setup": '<rect x="7" y="2" width="10" height="16" rx="2"/><path d="M12 18v4M8 22h8"/>',
    "log": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
    "dives": '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    "dive": '<path d="M5 4l14 8-14 8z"/>',
    "sources": '<path d="M4 6h16M4 12h16M4 18h10"/>',
    "limits": '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>',
}
short_concepts = ["What you actually get", "Book from my photo at 4", "Last night with the pacifier", "3 facts to camera", "Gift with a dedication"]
short_dives = [re.sub(r"[:].*$", "", t.split(". ", 1)[1]).strip() for t, _ in D]
NAV = [
    ("Start", [("overview", "Overview", "overview")]),
    ("What the Reels show", [("findings", "41 Reels in numbers", "findings"), ("approaches", "Seven approaches", "approaches"), ("fixes", "Weak choices and fixes", "fixes")]),
    ("Concepts", [("concepts", "All five", "concepts")] + [(f"concept-{n}", s, "concept") for n, s in enumerate(short_concepts, 1)]),
    ("Filming", [("shoot", "First shoot, 60-90 min", "shoot"), ("setup", "Phone set-up", "setup"), ("log", "After posting", "log")]),
    ("Deep dives", [("dives", "How to read them", "dives")] + [(f"dive-{n}", s, "dive") for n, s in enumerate(short_dives, 1)]),
    ("Reference", [("sources", "Sources (41 Reels)", "sources"), ("limits", "Method and limits", "limits")]),
]
nav = ""
for label, items in NAV:
    nav += f'<div class="lb-nav-label">{label}</div>'
    for k, t, ic in items:
        nav += (f'<a class="lb-nav-item" href="#{k}" data-view="{k}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
                f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[ic]}</svg><span>{inline(t)}</span></a>')
TITLES = {k: re.sub(r"<[^>]+>", "", inline(t)) for _, items in NAV for k, t, _ in items}
views = "\n".join(f'<section class="lb-page rr-view" data-view="{k}" id="v-{k}"{"" if k == "overview" else " hidden"}>{v}</section>' for k, v in V.items())

CSS = """
html { direction: ltr; }
body { text-align: start; background: var(--bg); color: var(--text); }
.rr-head { display: grid; gap: var(--sp-2); }
.rr-head h2 { font-size: clamp(1.5rem, 3vw, 2.15rem); text-wrap: balance; }
.rr-md { display: grid; gap: var(--sp-3); max-width: 72ch; }
.rr-md > .lb-table-wrap, .rr-md > .rr-strip, .rr-md > .rr-he { max-width: none; }
.rr-md h2 { font-size: var(--fs-title3, 1.35rem); margin-top: var(--sp-4); }
.rr-md h3 { font-size: var(--fs-headline, 1.12rem); margin-top: var(--sp-3); }
.rr-md h4 { font-size: var(--fs-callout, 1rem); }
.rr-md ul, .rr-md ol { margin: 0; padding-inline-start: 1.3rem; display: grid; gap: var(--sp-1); }
.rr-md p { margin: 0; }
.rr-md code { font-size: .88em; background: var(--surface-sunk); padding: .05rem .3rem; border-radius: 4px; }
.rr-md .lb-table-wrap { margin: 0; }
.lb-table td { vertical-align: top; }
.lb-table td, .lb-table th { font-size: var(--fs-footnote, .9rem); }
.rr-pre { margin: 0; padding: var(--sp-3); background: var(--surface-sunk); border-radius: var(--r-sm); overflow-x: auto; font-size: .85rem; }
.rr-he { direction: rtl; text-align: right; background: var(--surface); border: 1px solid var(--line); border-inline-start: 4px solid var(--lb-gold); border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); display: grid; gap: var(--sp-2); font-size: 1.08rem; line-height: 1.65; }
.rr-he p { margin: 0; }
.rr-he strong { color: var(--accent-ink); }
bdi[lang="he"] { font-family: var(--font); }
.rr-strip { margin: 0; display: grid; gap: var(--sp-2); }
.rr-strip-scroll { overflow-x: auto; border-radius: var(--r-md); border: 1px solid var(--line); background: var(--surface); }
.rr-strip-scroll img { display: block; height: min(55vh, 440px); width: auto; max-width: none; }
.rr-strip figcaption { font-size: var(--fs-caption, .8rem); color: var(--text-3); }
.rr-card { display: grid; gap: var(--sp-3); }
.rr-card h3 { font-size: var(--fs-headline, 1.12rem); }
.rr-film { border: 1px solid var(--accent); background: var(--accent-soft); }
.rr-stats .lb-stat-value { font-variant-numeric: tabular-nums; }
.rr-concepts { gap: var(--sp-3); }
.rr-concept-link { display: flex; gap: var(--sp-3); align-items: center; text-decoration: none; color: var(--text); font-weight: 600; }
.rr-concept-link:hover { border-color: var(--tint); }
.rr-n { display: inline-grid; place-items: center; width: 2rem; height: 2rem; border-radius: 50%; background: var(--tint-soft); color: var(--tint); font-weight: 700; flex: none; }
.rr-next { margin: 0; }
.rr-crumb { font-weight: 600; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lb-nav-item span { min-width: 0; }
@media (max-width: 640px) { .rr-he { font-size: 1rem; padding: var(--sp-3); } .rr-strip-scroll img { height: 46vh; } .lb-topbar .lb-dim { display: none; } }
"""

JS = """<script>
(function () {
  var views = document.querySelectorAll('.rr-view'), items = document.querySelectorAll('.lb-nav-item');
  var crumb = document.getElementById('rr-crumb'), side = document.querySelector('.lb-sidebar'), scrim = document.querySelector('.lb-scrim');
  var titles = TITLES;
  function route() {
    var h = (location.hash || '#overview').slice(1);
    if (!titles[h]) h = 'overview';
    views.forEach(function (v) { v.hidden = v.dataset.view !== h; });
    items.forEach(function (a) { if (a.dataset.view === h) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    crumb.textContent = titles[h];
    closeNav();
    window.scrollTo(0, 0);
  }
  function closeNav() { side.classList.remove('is-open'); scrim.hidden = true; }
  document.getElementById('rr-menu').addEventListener('click', function () { side.classList.add('is-open'); scrim.hidden = false; });
  scrim.addEventListener('click', closeNav);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeNav(); });
  window.addEventListener('hashchange', route);
  route();
})();
</script>"""

page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
{design.head()}
<style>{CSS}</style>
<div dir="ltr" lang="en">
<div class="lb-app">
  <aside class="lb-sidebar" aria-label="Sections">
    <a class="lb-brand" href="#overview"><img src="{design.logo_data_uri()}" alt=""><span><b>Product Reels Playbook</b><small>LumeBook · 15 Oct 2026</small></span></a>
    <nav class="lb-nav">{nav}</nav>
    <div class="lb-sidebar-foot"><span class="lb-chip">Internal</span><span>41 Reels · 34 creators · 8 deep dives</span><span>Public counts read 15 Oct 2026. None is tied to a sale.</span></div>
  </aside>
  <div class="lb-scrim" hidden></div>
  <main class="lb-main">
    <div class="lb-topbar"><div class="lb-topbar-in">
      <button class="lb-btn secondary icon lb-menu-btn" id="rr-menu" type="button" aria-label="Open sections"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
      <span class="rr-crumb" id="rr-crumb">Overview</span><span class="lb-spacer"></span><span class="lb-dim">Israeli creator product Reels</span>
    </div></div>
    {views}
  </main>
</div>
</div>
{JS.replace("TITLES", json.dumps(TITLES, ensure_ascii=False))}
"""
OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)}: {len(page):,} bytes, {len(V)} views")
