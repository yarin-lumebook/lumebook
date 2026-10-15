#!/usr/bin/env python3
"""Build the creator brief page from creator-brief.md.

    python3 research/israeli-product-reels/src/build_creator_brief.py

Input:  research/israeli-product-reels/creator-brief.md, only its Hebrew part (the <div dir="rtl"> blocks,
        read with the same parser as lint_creator_brief.py, so the page shows exactly the linted text)
Output: research/israeli-product-reels/creator-brief.html, an artifact page styled with the LumeBook design
        system (design.head() inlined, page rules below use tokens only)

How blocks become the page: the first ### heading is the hero, every other ### heading a section.
A block that starts with **name · A עד B שניות** is a shot step (the time strip is drawn from these),
a block that starts with למשל is an example for the step before it, a list item whose first line is a
quote (״...״) is a worry card, other list items are do-not rules, "- [ ]" items are the checklist, and the
data-lint="cta" / "caption" blocks get a copy button. Edit the brief, then rebuild; never edit the HTML.
Standard library only.
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402
from lint_creator_brief import BRIEF, DIV_RE, blocks  # noqa: E402

OUT = HERE.parent / "creator-brief.html"
TITLE = "בריף הרילס של לומבוק"

# Hebrew the page adds around the brief's own text (linted by lint_creator_brief.py too)
UI = {
    "brand": "לומבוק",
    "eyebrow": "בריף ליוצרים",
    "brand_sub": "בריף ליוצרים",
    "copy": "העתקה",
    "copied": "הועתק",
    "copy_fallback": "הטקסט מסומן\nאפשר להעתיק",
    "checked_of": "מתוך",
    "reset": "ניקוי הסימונים",
    "seconds": "שניות",
    "strip_label": "{n} חלקים לאורך {t} שניות",
    "frame_hook": "טקסט הפתיחה",
    "frame_book": "הספר",
    "frame_subs": "כתוביות",
    "frame_ui": "אינסטגרם מכסה כאן",
}

STEP_RE = re.compile(r"^\*\*(.+?) · (\d+) עד (\d+) שניות\*\*")


# ---------- inline markdown ----------

def inline(text):
    """Escape, then bold, `handles` and [links](url)."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`([^`]+)`", r'<bdi class="handle" dir="ltr">\1</bdi>', out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', out)
    return out


def lines_of(block):
    """A raw block as rendered lines (markdown list and quote markers removed, <br> = line break)."""
    text = []
    for line in block.splitlines():
        line = re.sub(r"^\s*(?:>\s?|#+\s+|-\s+\[ \]\s+|-\s+)", "", line).strip()
        if line:
            text.append(line)
    return [part.strip() for part in re.split(r"<br>", " ".join(text)) if part.strip()]


def plain(lines):
    return "\n".join(re.sub(r"`([^`]+)`", r"\1", l) for l in lines)


def br(lines):
    return "<br>".join(inline(l) for l in lines)


# ---------- parse ----------

def parse():
    md = BRIEF.read_text(encoding="utf-8")
    sections = []
    for kind, content in DIV_RE.findall(md):
        if kind in ("cta", "caption"):
            sections[-1]["items"].append({"type": "copy", "role": kind, "lines": lines_of(content)})
            continue
        for b in blocks(content):
            first = b.lstrip()
            if first.startswith("### "):
                sections.append({"title": first[4:].strip(), "items": []})
                continue
            if not sections:
                continue
            items = sections[-1]["items"]
            lines = lines_of(b)
            m = STEP_RE.match(first)
            if first.startswith("- [ ]"):
                items.append({"type": "check", "lines": lines})
            elif first.startswith("- "):
                items.append({"type": "worry" if lines[0].startswith("״") else "rule", "lines": lines})
            elif m:
                items.append({"type": "step", "name": m.group(1), "start": int(m.group(2)), "end": int(m.group(3)), "lines": lines[1:]})
            elif lines and lines[0] == "למשל":
                items.append({"type": "example", "lines": lines[1:]})
            elif lines:
                items.append({"type": "para", "lines": lines})
    return sections


# ---------- render ----------

def strip(steps):
    total = steps[-1]["end"]
    segs = "".join(
        f'<span class="seg" style="flex-grow:{s["end"] - s["start"]}" title="{html.escape(s["name"])}">{i}</span>'
        for i, s in enumerate(steps, 1))
    label = UI["strip_label"].format(n=len(steps), t=total)
    return (f'<div class="strip" role="img" aria-label="{label}">'
            f'<div class="segs">{segs}</div>'
            f'<div class="ticks"><span>0</span><span>{total} {UI["seconds"]}</span></div></div>')


def frame():
    return (f'<figure class="frame" aria-hidden="true"><div class="screen">'
            f'<span class="z hook">{UI["frame_hook"]}</span><span class="z book">{UI["frame_book"]}</span>'
            f'<span class="z subs">{UI["frame_subs"]}</span><span class="z ui">{UI["frame_ui"]}</span>'
            f'</div></figure>')


def copy_box(item, n):
    cls = "cta" if item["role"] == "cta" else "caption"
    return (f'<div class="copybox lb-card is-accent {cls}">'
            f'<p class="copytext" id="copy-{n}">{br(item["lines"])}</p>'
            f'<div class="lb-row"><button class="lb-btn sm" type="button" data-copy="copy-{n}" '
            f'data-text="{html.escape(plain(item["lines"]))}">{UI["copy"]}</button></div></div>')


def render_items(items, sec_id):
    out, i, n_copy, n_check = [], 0, 0, 0
    while i < len(items):
        it = items[i]
        t = it["type"]
        if t == "step":
            run = []
            while i < len(items) and items[i]["type"] in ("step", "example", "para") and (items[i]["type"] == "step" or run):
                run.append(items[i]); i += 1
            steps = [s for s in run if s["type"] == "step"]
            out.append(strip(steps))
            lis, num = [], 0
            for s in run:
                if s["type"] == "step":
                    num += 1
                    lis.append([f'<span class="num">{num}</span><div class="body"><div class="lb-row head"><h3>{inline(s["name"])}</h3>'
                                f'<span class="lb-chip outline time">{s["start"]} עד {s["end"]} {UI["seconds"]}</span></div>'
                                f'<p>{br(s["lines"])}</p>'])
                elif s["type"] == "example":
                    lis[-1].append(f'<div class="example">{"".join(f"<p>{inline(l)}</p>" for l in s["lines"])}</div>')
                else:
                    lis[-1].append(f'<p class="lb-muted">{br(s["lines"])}</p>')
            out.append('<ol class="steps">' + "".join(f'<li>{li[0]}{"".join(li[1:])}</div></li>' for li in lis) + "</ol>")
            continue
        if t in ("worry", "rule", "check"):
            run = []
            while i < len(items) and items[i]["type"] == t:
                run.append(items[i]); i += 1
            if t == "worry":
                out.append('<div class="worries">' + "".join(
                    f'<div class="lb-card worry"><h3>{inline(w["lines"][0])}</h3><p>{br(w["lines"][1:])}</p></div>' for w in run) + "</div>")
            elif t == "rule":
                body = []
                for r in run:
                    extra = frame() if any("כתוביות" in l for l in r["lines"][:1]) else ""
                    body.append(f'<li><span class="mark" aria-hidden="true"></span><div><strong>{inline(r["lines"][0])}</strong>'
                                f'<p>{br(r["lines"][1:])}</p>{extra}</div></li>')
                out.append('<ul class="rules">' + "".join(body) + "</ul>")
            else:
                boxes = []
                for c in run:
                    n_check += 1
                    boxes.append(f'<li><label class="lb-check"><input type="checkbox" id="chk-{n_check}"><span>{br(c["lines"])}</span></label></li>')
                out.append(f'<div class="lb-card checklist"><div class="lb-row between"><span class="lb-count is-tint" id="chk-count">0 {UI["checked_of"]} {n_check}</span>'
                           f'<button class="lb-btn ghost sm" type="button" id="chk-reset">{UI["reset"]}</button></div>'
                           f'<ul>{"".join(boxes)}</ul></div>')
            continue
        if t == "copy":
            n_copy += 1
            out.append(copy_box(it, f"{sec_id}-{n_copy}"))
        elif t == "example":
            out.append(f'<div class="example">{"".join(f"<p>{inline(l)}</p>" for l in it["lines"])}</div>')
        else:
            out.append(f'<p>{br(it["lines"])}</p>')
        i += 1
    return "\n".join(out)


PAGE_CSS = """
/* Creator brief: one reading column for a phone, the shot list as a time strip and numbered steps,
   gold copy boxes for the two lines creators paste, a checklist they tick. Tokens only. */
.brief { max-width: 46rem; }
.brief h2 { font-size: var(--fs-title); }
.hero { display: grid; gap: var(--sp-3); padding-block: var(--sp-3) 0; }
.hero p { font-size: 1.125rem; line-height: 1.55; color: var(--text-2); }
.lb-section > p { color: var(--text-2); }
.handle { font-family: var(--font); font-weight: 600; color: var(--text); unicode-bidi: isolate; }

.strip { display: grid; gap: var(--sp-1); }
.segs { display: flex; gap: 3px; height: 2.25rem; direction: rtl; }
.seg { display: grid; place-items: center; min-width: 0; border-radius: var(--r-xs); background: var(--tint-soft); color: var(--tint);
  font-size: var(--fs-footnote); font-weight: 700; font-variant-numeric: tabular-nums; }
.seg:nth-child(even) { background: var(--accent-soft); color: var(--accent-ink); }
.ticks { display: flex; justify-content: space-between; font-size: var(--fs-caption); color: var(--text-3); font-variant-numeric: tabular-nums; }

.steps { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-3); }
.steps > li { display: grid; grid-template-columns: 2rem minmax(0, 1fr); gap: var(--sp-3); align-items: start;
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-4); }
.steps .num { display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: 50%; background: var(--lb-ink); color: var(--text-on-tint);
  font-weight: 700; font-variant-numeric: tabular-nums; }
.steps .body { display: grid; gap: var(--sp-2); min-width: 0; }
.steps .head { gap: var(--sp-2) var(--sp-3); }
.steps .time { font-variant-numeric: tabular-nums; color: var(--text-2); }
.steps p { color: var(--text-2); }
.steps .body > p:first-of-type { color: var(--text); }

.example { display: grid; gap: var(--sp-1); background: var(--surface-2); border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); }
.example p { font-family: var(--font-display); font-size: 1.0625rem; color: var(--text); }

.worries { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); }
.worry { gap: var(--sp-2); }
.worry h3 { font-family: var(--font-display); font-weight: 400; font-size: 1.1875rem; }
.worry p { color: var(--text-2); }

.copybox { gap: var(--sp-3); }
.copytext { font-size: 1.0625rem; font-weight: 500; line-height: 1.6; }
.cta .copytext { font-family: var(--font-display); font-weight: 400; font-size: 1.25rem; line-height: 1.45; }

.rules { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-4); }
.rules > li { display: grid; grid-template-columns: 1.25rem minmax(0, 1fr); gap: var(--sp-3); align-items: start; }
.rules .mark { width: 1.25rem; height: 1.25rem; margin-top: .2rem; border-radius: 50%; background: var(--danger-soft); position: relative; }
.rules .mark::before, .rules .mark::after { content: ""; position: absolute; left: 50%; top: 50%; width: .6rem; height: 2px;
  background: var(--danger); border-radius: 1px; transform: translate(-50%, -50%) rotate(45deg); }
.rules .mark::after { transform: translate(-50%, -50%) rotate(-45deg); }
.rules li > div { display: grid; gap: var(--sp-1); min-width: 0; }
.rules p { color: var(--text-2); }

.frame { margin: var(--sp-2) 0 0; }
.frame .screen { position: relative; width: 9.5rem; max-width: 100%; aspect-ratio: 9 / 16; border: 2px solid var(--lb-ink); border-radius: var(--r-md);
  background: var(--surface); overflow: hidden; font-size: var(--fs-caption); font-weight: 600; }
.frame .z { position: absolute; inset-inline: 6px; display: grid; place-items: center; text-align: center; border-radius: var(--r-xs); padding: 2px; }
.frame .hook { top: 6px; height: calc(33.3% - 9px); background: var(--tint-soft); color: var(--tint); }
.frame .book { top: 33.3%; height: 30%; background: var(--accent-soft); color: var(--accent-ink); }
.frame .subs { top: 66%; height: calc(14% - 6px); background: var(--fill-2); color: var(--text); }
.frame .ui { inset-inline: 0; bottom: 0; height: 20%; border-radius: 0; color: var(--danger);
  background: repeating-linear-gradient(135deg, var(--danger-soft) 0 6px, transparent 6px 12px); }

.checklist ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); }
.checklist .lb-check { font-size: var(--fs-body); }
.foot { font-size: var(--fs-footnote); color: var(--text-3); }
"""

PAGE_JS = """
<div class="lb-toast" id="toast" role="status" aria-live="polite" hidden></div>
<script>
(function () {
  var toast = document.getElementById("toast"), timer;
  function say(text) { toast.textContent = text; toast.hidden = false; clearTimeout(timer); timer = setTimeout(function () { toast.hidden = true; }, 2200); }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    var text = btn.getAttribute("data-text"), el = document.getElementById(btn.getAttribute("data-copy"));
    function fallback() {
      var r = document.createRange(); r.selectNodeContents(el);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      say(__FALLBACK__);
    }
    try { navigator.clipboard.writeText(text).then(function () { say(__COPIED__); }, fallback); } catch (err) { fallback(); }
  });
  var KEY = "lb-creator-brief-checks", boxes = Array.prototype.slice.call(document.querySelectorAll(".checklist input[type=checkbox]"));
  var count = document.getElementById("chk-count");
  function update() {
    var n = boxes.filter(function (b) { return b.checked; }).length;
    if (count) count.textContent = n + " " + __OF__ + " " + boxes.length;
    try { localStorage.setItem(KEY, JSON.stringify(boxes.map(function (b) { return b.checked; }))); } catch (err) {}
  }
  try { var saved = JSON.parse(localStorage.getItem(KEY) || "[]"); boxes.forEach(function (b, i) { b.checked = !!saved[i]; }); } catch (err) {}
  boxes.forEach(function (b) { b.addEventListener("change", update); });
  var reset = document.getElementById("chk-reset");
  if (reset) reset.addEventListener("click", function () { boxes.forEach(function (b) { b.checked = false; }); update(); });
  update();
})();
</script>
"""


def build():
    sections = parse()
    hero, rest = sections[0], sections[1:]
    hero_html = (f'<section class="hero"><span class="lb-eyebrow">{UI["eyebrow"]}</span><h1>{inline(hero["title"])}</h1>'
                 + "".join(f'<p>{br(it["lines"])}</p>' for it in hero["items"]) + "</section>")
    body = []
    for n, s in enumerate(rest, 1):
        body.append(f'<section class="lb-section" id="s{n}"><h2>{inline(s["title"])}</h2>\n{render_items(s["items"], n)}\n</section>')
    js = (PAGE_JS.replace("__COPIED__", repr(UI["copied"])).replace("__OF__", repr(UI["checked_of"]))
          .replace("__FALLBACK__", repr(UI["copy_fallback"].replace("\n", " "))))
    page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
{design.head()}
<script>document.documentElement.setAttribute("dir","rtl");document.documentElement.setAttribute("lang","he");</script>
<style>{PAGE_CSS}</style>

<header class="lb-topbar" dir="rtl" lang="he">
  <div class="lb-topbar-in">
    <span class="lb-brand"><img src="{design.logo_data_uri()}" alt=""><span><b>{UI["brand"]}</b><small>{UI["brand_sub"]}</small></span></span>
  </div>
</header>

<main class="lb-page brief" dir="rtl" lang="he">
{hero_html}
{chr(10).join(body)}
</main>
{js}"""
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page) // 1024} KB, {len(rest)} sections)")


if __name__ == "__main__":
    build()
