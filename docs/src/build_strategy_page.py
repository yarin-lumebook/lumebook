#!/usr/bin/env python3
"""Build the Q4 social strategy page from its template.

    python3 docs/src/build_strategy_page.py        (or: python3 tools/lumebook.py build strategy)

Input:  docs/src/strategy.template.html (the only source: edit it, then rebuild, never edit the HTML)
Output: docs/lumebook-social-strategy.html, a full HTML document on the LumeBook design system that opens straight
        from disk; it is published as an artifact from that path (lumebook.json component "strategy").

What the build does: <!--LB:HEAD--> becomes design.head() (fonts + the whole stylesheet, white only), <!--LB:LOGO-->
becomes the brand mark as a data: URI, and every cell of a table marked "is-stack" gets a data-label from its column
header, so the table can turn into one card per row on phones. It stops on an em dash. Standard library only.
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

SRC = HERE / "strategy.template.html"
OUT = ROOT / "docs" / "lumebook-social-strategy.html"

TABLE = re.compile(r'<table class="[^"]*\bis-stack\b[^"]*">.*?</table>', re.S)
TAGS = re.compile(r"<[^>]+>")


def label_cells(table):
    """Give each <td> of a stacking table the text of its column header as data-label."""
    heads = [html.escape(html.unescape(TAGS.sub("", h)).strip(), quote=True)
             for h in re.findall(r"<th\b[^>]*>(.*?)</th>", table.split("</thead>")[0], re.S)]

    def row(m):
        cells = iter(heads)
        return re.sub(r"<td\b", lambda _: f'<td data-label="{next(cells, "")}"', m.group(0))

    head, body = table.split("</thead>", 1)
    return head + "</thead>" + re.sub(r"<tr>.*?</tr>", row, body, flags=re.S)


def build():
    page = SRC.read_text(encoding="utf-8")
    page = TABLE.sub(lambda m: label_cells(m.group(0)), page)
    page = page.replace("<!--LB:HEAD-->", design.head()).replace("<!--LB:LOGO-->", design.logo_data_uri())
    if "—" in page:
        raise SystemExit("em dash in the page; fix docs/src/strategy.template.html")
    if "<!--LB:" in page:
        raise SystemExit("unreplaced <!--LB:...--> placeholder in the template")
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    build()
