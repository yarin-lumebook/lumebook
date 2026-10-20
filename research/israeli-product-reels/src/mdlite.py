"""Small markdown-to-HTML helpers for the Product Reels Playbook page (the subset our markdown files use).

Hebrew runs inside English lines are wrapped in <bdi lang="he"> so they keep their direction; blocks
inside <div dir="rtl"> render right to left. Images named in markdown are embedded from the annotated
frame strips in media/ as data: URIs. Standard library only.
"""
import base64
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MEDIA = ROOT / "media" / "projects" / "2026-10-15-israeli-product-reels" / "annotated"

# A Hebrew run; a straight or Hebrew quote on either side stays inside it so the quotes stay paired
HEB = re.compile(r"[\"״]?[֐-׿](?:[֐-׿0-9\s'״׳\-.,:?!·%₪]*[֐-׿0-9?!])?[\"״]?")


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

    text = re.sub(r"<br\s*/?>", lambda m: stash("<br>"), str(text or ""))
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


def strip_md(text):
    """Plain text: drop markdown links, bold and code marks."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", str(text or ""))
    return re.sub(r"\*\*|`", "", text).strip()


def img_tag(alt, path):
    name = Path(path).name
    f = MEDIA / name
    if not f.exists():
        return f'<p class="pb-note">Frame strip {html.escape(name)} is not on this machine (media folder missing).</p>'
    uri = "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()
    return (f'<figure class="pb-strip"><div class="pb-strip-scroll" tabindex="0" aria-label="{html.escape(alt)}">'
            f'<img src="{uri}" alt="{html.escape(alt)}" loading="lazy"></div>'
            f'<figcaption>Annotated frames with timestamps. Scroll sideways to see every frame.</figcaption></figure>')


def table_rows(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    return cells[0], cells[2:]


def table(rows):
    head, body = table_rows(rows)
    out = ['<div class="pb-table-wrap"><table class="pb-table"><thead><tr>']
    out += [f"<th>{inline(h)}</th>" for h in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def render(md, rtl=False):
    """Markdown blocks to HTML: headings, paragraphs, lists, tables, code fences, images and <div dir="rtl"> blocks."""
    lines = str(md or "").splitlines()
    out, i = [], 0
    while i < len(lines):
        s = lines[i].strip()
        if not s or s == "---":
            i += 1
            continue
        if s.startswith('<div dir="rtl"'):
            j = i + 1
            while j < len(lines) and lines[j].strip() != "</div>":
                j += 1
            out.append(f'<div class="pb-he" dir="rtl" lang="he">{render(chr(10).join(lines[i + 1:j]), rtl=True)}</div>')
            i = j + 1
            continue
        if s.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            out.append(f'<pre class="pb-pre" dir="ltr"><code>{html.escape(chr(10).join(lines[i + 1:j]))}</code></pre>')
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
        if not para:
            para, j = [s], i + 1
        out.append(f"<p>{inline(' '.join(para), rtl)}</p>")
        i = j
    return "\n".join(out)


def sections(md, level):
    """Split markdown at headings of one level: [(title, body)], with the text before the first heading as ('', body)."""
    marker = "#" * level + " "
    out, title, buf = [], "", []
    for line in str(md).splitlines():
        if line.startswith(marker):
            out.append((title, "\n".join(buf)))
            title, buf = line[len(marker):].strip(), []
        else:
            buf.append(line)
    out.append((title, "\n".join(buf)))
    return out


def bullets_by_label(md):
    """'- **Label:** text' bullets as {label: text}, keeping wrapped continuation lines."""
    out, cur = {}, None
    for line in str(md).splitlines():
        m = re.match(r"^- \*\*([^*]+?):?\*\*:?\s*(.*)$", line.strip()) if line.startswith("- ") else None
        if m:
            cur = m.group(1).strip().rstrip(":")
            out[cur] = m.group(2).strip()
        elif cur and line.startswith("  ") and line.strip():
            out[cur] += " " + line.strip()
        elif not line.strip():
            continue
        else:
            cur = None
    return out
