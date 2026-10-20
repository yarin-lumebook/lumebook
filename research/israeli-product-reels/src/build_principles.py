#!/usr/bin/env python3
"""Build smm-research/principles.md, the compact principle list, from the four research notes.

    python3 research/israeli-product-reels/src/build_principles.py

Inputs:  smm-research/notes/{hooks-retention,cta-text,shown-filmed,edit-topic}.md (written 18 Oct 2026,
         one per research area; each principle has Rule, Evidence, Strength, Transfer to LumeBook and
         How to spot it), smm-research/overlaps.json (which principles say the same thing, optional).
Output:  smm-research/principles.md: per question, every principle's rule, strength, the sources it
         rests on (title, link, type), what it means for LumeBook and where the full evidence is.
         The coding agents (src/TABLE_BRIEF.md) cite these IDs; the page renders this file.

Standard library only. Edit the notes, then rebuild.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIR = HERE.parent
NOTES = DIR / "smm-research" / "notes"
OUT = DIR / "smm-research" / "principles.md"
INDEX = DIR / "smm-research" / "principles-index.md"   # the short version the coding agents read

AREAS = [
    ("H", 1, "The hook (first 3 seconds)", "hooks-retention.md"),
    ("R", 2, "Every few seconds: retention and interaction", "hooks-retention.md"),
    ("C", 3, "The call to action", "cta-text.md"),
    ("S", 4, "What is shown", "shown-filmed.md"),
    ("E", 5, "Editing", "edit-topic.md"),
    ("K", 6, "What the content is about", "edit-topic.md"),
    ("F", 7, "What is filmed and how", "shown-filmed.md"),
    ("T", 8, "Text on screen and the caption", "cta-text.md"),
]
TYPES = [("peer-reviewed", "peer-reviewed"), ("meta-analysis", "peer-reviewed"), ("official", "platform"), ("platform", "platform"),
         ("regulator", "regulator"), ("government", "regulator"), ("law", "regulator"), ("industry", "industry study"),
         ("survey", "industry study"), ("news", "news report"), ("practitioner", "practitioner"), ("conference", "conference paper")]


def field(block, name):
    m = re.search(r"^- \*\*" + re.escape(name) + r":\*\*\s*(.*?)(?=^- \*\*|\Z)", block, re.S | re.M)
    return m.group(1).strip() if m else ""


def sources(evidence):
    """One short line per evidence bullet: [title](url), with its evidence type."""
    out = []
    for line in re.split(r"\n\s*- ", "\n" + evidence):
        line = line.strip()
        if not line:
            continue
        m = re.search(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", line)
        low = line.lower()
        kind = next((v for k, v in TYPES if k in low), "")
        if m:
            out.append(f"[{m.group(1)}]({m.group(2)})" + (f" ({kind})" if kind else ""))
        else:
            ref = re.split(r"\(link in|\(sample above|,", line, maxsplit=1)[0].strip()
            out.append(f"{ref} (see above)" if ref else "")
    seen, uniq = set(), []
    for s in out:
        if s and s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def parse(prefix, path):
    text = path.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"^####\s+(" + prefix + r"\d{1,2})\.\s+(.+?)\n(.*?)(?=^#{2,4}\s|\Z)", text, re.S | re.M):
        pid, title, block = m.group(1), m.group(2).strip(), m.group(3)
        out.append({
            "id": pid, "title": title,
            "rule": field(block, "Rule"),
            "strength": field(block, "Strength"),
            "transfer": field(block, "Transfer to LumeBook"),
            "spot": field(block, "How to spot it in a Reel"),
            "sources": sources(field(block, "Evidence")),
            "file": path.name,
        })
    return out


def main():
    overlaps = {}
    ov = DIR / "smm-research" / "overlaps.json"
    if ov.exists():
        for group in json.loads(ov.read_text(encoding="utf-8"))["groups"]:
            for pid in group["ids"]:
                overlaps[pid] = [x for x in group["ids"] if x != pid]
    lines = [
        "# SMM research principles behind the playbook",
        "",
        "Research of 18 Oct 2026. Four research passes read platform documentation (Instagram, Meta, TikTok, YouTube), peer-reviewed studies, "
        "large industry datasets and regulators, and traced popular statistics back to their origin. Every source listed was opened during the research; "
        "for most paywalled journal papers only the abstract was read, and the full notes say which. The full evidence, with dates, sample sizes and what each "
        "source shows, is in `smm-research/notes/`.",
        "",
        "How to read a principle: the **rule** is what a Reel can be checked against; **strength** says how much the evidence carries (strong, moderate, weak "
        "or contested) and why; **sources** are the studies and platform pages it rests on; **for LumeBook** turns it into a filming choice. "
        "The table's whys cite these IDs. Most platform numbers come from paid ads, not organic Reels, and nothing found is specific to Hebrew or Israel unless the principle says so.",
        "",
    ]
    index = ["# Principle index for coders (built by src/build_principles.py; full version: principles.md)", "",
             "ID, rule, strength, and what to look for. Cite IDs in the table's whys.", ""]
    total = 0
    for prefix, q, title, fname in AREAS:
        path = NOTES / fname
        if not path.exists():
            lines += [f"## {q}. {title} ({prefix})", "", f"Not written yet: `notes/{fname}` is missing.", ""]
            continue
        ps = parse(prefix, path)
        total += len(ps)
        lines += [f"## {q}. {title} ({prefix})", ""]
        index += [f"## Q{q}. {title}", ""]
        for p in ps:
            strength = re.split(r"(?<=[a-z])[.;]", p["strength"], maxsplit=1)[0]
            index.append(f"- **{p['id']}. {p['title']}** Rule: {p['rule']} Strength: {strength}."
                         + (f" Look for: {p['spot']}" if p["spot"] else "")
                         + (f" (Overlaps {', '.join(overlaps[p['id']])}.)" if overlaps.get(p["id"]) else ""))

            lines.append(f"### {p['id']}. {p['title']}")
            lines.append("")
            lines.append(f"- **Rule:** {p['rule']}")
            lines.append(f"- **Strength:** {p['strength']}")
            if p["sources"]:
                lines.append(f"- **Sources:** {'; '.join(p['sources'])}")
            lines.append(f"- **For LumeBook:** {p['transfer']}")
            if overlaps.get(p["id"]):
                lines.append(f"- **Overlaps with:** {', '.join(overlaps[p['id']])}")
            lines.append(f"- **Full evidence:** `smm-research/notes/{p['file']}`")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    INDEX.write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(HERE.parents[2])}: {total} principles")


if __name__ == "__main__":
    main()
