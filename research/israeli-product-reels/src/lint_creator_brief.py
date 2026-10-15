#!/usr/bin/env python3
"""Lint the Hebrew in creator-brief.md with the LumeBook voice lint.

    python3 research/israeli-product-reels/src/lint_creator_brief.py          # lint, exit 1 on any error
    python3 research/israeli-product-reels/src/lint_creator_brief.py --text   # also print the Hebrew as plain lines

Every <div dir="rtl"> block in the brief is split into fields the way it renders: one field per
paragraph, list item or heading, <br> as a line break. The div marked data-lint="cta" is the CTA and
data-lint="caption" the caption template (its last line must equal the CTA). Markdown syntax is
removed first, render hints (<!--icon:...--> and the like) too. Handles and URLs in backticks or links are swapped for a Hebrew placeholder, because
the dot in @lumebook.il is not punctuation. The page's own Hebrew (UI in build_creator_brief.py) is
linted too. The fields are written to src/scripts/creator-brief.json
and linted with carousel/carousel-pipeline/scripts/voice_lint.py. Nothing in the brief is edited.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BRIEF = HERE.parent / "creator-brief.md"
OUT = HERE / "scripts" / "creator-brief.json"
LINT = ROOT / "carousel/carousel-pipeline/scripts/voice_lint.py"
CODE_WORD = "לומי"
PLACEHOLDER = "הכתובת"

DIV_RE = re.compile(r'<div dir="rtl" lang="he"(?: data-lint="(\w+)")?>(.*?)</div>', re.S)


def clean(block, for_lint=True):
    block = re.sub(r"<!--.*?-->", "", block)                    # render hints (icon, as, visual)
    if for_lint:
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", block)   # [text](url) -> text
        text = re.sub(r"`[^`]+`", PLACEHOLDER, text)              # `@handle` -> placeholder
    else:
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1<br>\2", block)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"^-\s+\[ \]\s+", "☐ ", text)
    text = text.replace("**", "")
    lines = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:>\s?|#+\s+|-\s+\[ \]\s+|-\s+)", "", line)
        lines.append(line.strip())
    text = " ".join(l for l in lines if l)
    return "\n".join(part.strip() for part in re.split(r"<br>", text) if part.strip())


def blocks(content):
    """Paragraphs, headings and list items, in order."""
    out, current = [], []
    for line in content.splitlines():
        starts_item = re.match(r"^(#+\s|-\s)", line)
        if not line.strip() or starts_item:
            if current:
                out.append("\n".join(current))
            current = [line] if line.strip() else []
        else:
            current.append(line)
    if current:
        out.append("\n".join(current))
    return out


def fields(for_lint=True):
    md = BRIEF.read_text(encoding="utf-8")
    result, n = {}, 0
    for kind, content in DIV_RE.findall(md):
        if kind in ("cta", "caption"):
            result[kind] = clean(content, for_lint)
            continue
        for b in blocks(content):
            text = clean(b, for_lint)
            if text:
                n += 1
                result[f"b{n:02d}"] = text
    return result


def main():
    f = fields()
    from build_creator_brief import UI  # the Hebrew the page adds around the brief
    f.update({f"ui_{k}": v.format(n=7, t=36) for k, v in UI.items()})  # templates linted with sample numbers
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if "--text" in sys.argv:
        print("\n\n".join(fields(for_lint=False).values()))
        print()
    cmd = [sys.executable, str(LINT), str(OUT), "--cta", "cta", "--caption", "caption", "--code-word", CODE_WORD]
    print(f"{len(f)} Hebrew fields from {BRIEF.relative_to(ROOT)} -> {OUT.relative_to(ROOT)}")
    sys.exit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
