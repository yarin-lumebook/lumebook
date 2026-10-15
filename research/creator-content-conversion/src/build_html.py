"""Markdown helpers (convert, inline) for build_page.py, which builds report.html.

Running this file builds the page through build_page.py. Standard library only.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(OUT_DIR, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
import design  # noqa: E402

HEB = re.compile(r"[֐-׿]")


def slug(text, seen):
    s = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-") or "section"
    n, base = 2, s
    while s in seen:
        s, n = f"{base}-{n}", n + 1
    seen.add(s)
    return s


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    # Hebrew runs get their own direction so punctuation lands correctly in an LTR page
    t = re.sub(r"((?:[֐-׿][֐-׿\s'\"״׳\-!?.,:;()/+0-9]*[֐-׿!?\"״'׳])|[֐-׿])",
               r'<bdi class="he" dir="rtl">\1</bdi>', t)
    return t


def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def convert(md):
    lines = md.splitlines()
    out, toc, seen = [], [], set()
    i, n = 0, len(lines)
    section_open = False
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            lvl, text = len(m.group(1)), m.group(2)
            if lvl == 1:
                out.append(f'<h1 class="rp-title">{inline(text)}</h1>')
            elif lvl == 2:
                if section_open:
                    out.append("</section>")
                sid = slug(text, seen)
                toc.append((sid, re.sub(r"^\d+\.\s*", "", text)))
                out.append(f'<section class="rp-section" id="{sid}"><h2>{inline(text)}</h2>')
                section_open = True
            else:
                sid = slug(text, seen)
                out.append(f'<h3 id="{sid}">{inline(text)}</h3>')
            i += 1
            continue
        if line.strip() == "---":
            i += 1
            continue
        if line.startswith("|") and i + 1 < n and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip()):
            head = split_row(line)
            i += 2
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            tb = ['<div class="lb-table-wrap"><table class="lb-table rp-table"><thead><tr>']
            tb += [f"<th>{inline(c)}</th>" for c in head]
            tb.append("</tr></thead><tbody>")
            for r in rows:
                tb.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            tb.append("</tbody></table></div>")
            out.append("".join(tb))
            continue
        if re.match(r"^\s*(?:[-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n:
                cur = lines[i]
                mm = re.match(r"^(\s*)(?:[-*]|\d+\.)\s+(.*)", cur)
                if mm and len(mm.group(1)) == 0:
                    items.append([mm.group(2)])
                    i += 1
                elif mm and len(mm.group(1)) > 0 and items:
                    items[-1].append("  - " + mm.group(2))
                    i += 1
                elif cur.startswith("  ") and cur.strip() and items:
                    items[-1].append(cur.strip())
                    i += 1
                else:
                    break
            body = [f"<{tag} class=\"rp-list\">"]
            for it in items:
                parts, quote = [inline(it[0])], []
                for extra in it[1:]:
                    if extra.startswith(">"):
                        quote.append(inline(extra.lstrip("> ").strip()))
                    elif extra.startswith("  - "):
                        parts.append("<br>" + inline(extra[4:]))
                    else:
                        parts.append(" " + inline(extra))
                li = "".join(parts)
                if quote:
                    li += '<span class="rp-quote">' + "<br>".join(quote) + "</span>"
                body.append(f"<li>{li}</li>")
            body.append(f"</{tag}>")
            out.append("".join(body))
            continue
        if line.startswith(">"):
            q = []
            while i < n and lines[i].startswith(">"):
                q.append(inline(lines[i].lstrip("> ").strip()))
                i += 1
            out.append('<blockquote class="rp-quote">' + "<br>".join(q) + "</blockquote>")
            continue
        para = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,3}\s|\||>|\s*(?:[-*]|\d+\.)\s|---)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    if section_open:
        out.append("</section>")
    return "\n".join(out), toc


CSS = """
:root { --rp-measure: 1040px; }
body { background: var(--bg); }
.rp-wrap { max-width: var(--rp-measure); margin: 0 auto; padding: 24px 16px 80px; direction: ltr; text-align: left; }
.rp-badge { display: inline-block; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px;
  background: var(--tint-soft); color: var(--tint); margin-bottom: 10px; }
.rp-title { font-size: clamp(26px, 5vw, 38px); line-height: 1.15; margin: 0 0 12px; }
.rp-toc { margin: 18px 0 8px; display: flex; flex-wrap: wrap; gap: 6px; }
.rp-toc a { font-size: 13px; padding: 4px 10px; border-radius: 999px; background: var(--surface); border: 1px solid var(--line);
  color: var(--text); text-decoration: none; }
.rp-toc a:hover { background: var(--tint-soft); color: var(--tint); }
.rp-section { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px 18px 8px; margin: 18px 0; }
.rp-section h2 { margin: 0 0 10px; font-size: 22px; }
.rp-section h3 { margin: 22px 0 8px; font-size: 17px; }
.rp-wrap p, .rp-wrap li { line-height: 1.6; }
.rp-list { padding-inline-start: 22px; margin: 8px 0 14px; }
.rp-list li { margin: 5px 0; }
.rp-table { font-size: 13px; }
.rp-table th, .rp-table td { vertical-align: top; text-align: left; }
.lb-table-wrap { overflow-x: auto; margin: 10px 0 16px; border-radius: 10px; }
bdi.he { font-family: 'Heebo', sans-serif; }
.rp-quote { display: block; margin: 6px 0 8px; padding: 8px 12px; background: var(--surface-2); border-radius: 10px;
  border-inline-start: 3px solid var(--lb-gold-deep); direction: rtl; text-align: right; font-size: 17px; font-weight: 600; line-height: 1.5; }
.rp-quote bdi.he { font-weight: 600; }
code { font-size: 12.5px; direction: ltr; unicode-bidi: isolate; word-break: break-word; }
.rp-foot { margin-top: 28px; font-size: 12.5px; color: var(--text-3); }
@media (max-width: 480px) { .rp-section { padding: 14px 12px 4px; } .rp-table { font-size: 12px; } }
@media print { .rp-toc { display: none; } .rp-section { break-inside: avoid-page; border: none; padding: 0; } }
"""


def main():
    md = open(os.path.join(OUT_DIR, "report.md"), encoding="utf-8").read()
    body, toc = convert(md)
    # put the title block and a contents strip before the first section
    first = body.index('<section class="rp-section"')
    head_html, rest = body[:first], body[first:]
    toc_html = '<nav class="rp-toc" aria-label="Contents">' + "".join(
        f'<a href="#{sid}">{html.escape(t)}</a>' for sid, t in toc) + "</nav>"
    page = f"""<!doctype html>
<html lang="en" dir="ltr" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Creator content and purchase intent</title>
{design.head()}
<style>{CSS}</style>
</head>
<body>
<main class="rp-wrap">
<span class="rp-badge">Internal · holds sales figures · 14 Oct 2026</span>
{head_html}
{toc_html}
{rest}
<p class="rp-foot">Built from <code>report.md</code> by <code>src/build_html.py</code>. Evidence, method and data: <code>evidence.md</code>, <code>methodology.md</code>, <code>posts.csv</code>, <code>creators.csv</code>.</p>
</main>
</body>
</html>
"""
    with open(os.path.join(OUT_DIR, "report.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote report.html", len(page), "bytes,", len(toc), "sections")


if __name__ == "__main__":
    import runpy
    runpy.run_path(os.path.join(HERE, "build_page.py"), run_name="__main__")
