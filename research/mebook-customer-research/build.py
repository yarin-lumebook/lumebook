#!/usr/bin/env python3
"""Build the MeBook customer study page (14 Nov 2026), in Hebrew.

Yarin: "super organized html" and "in hebrew".

    python3 tools/lumebook.py build mebook-customer-research     # or: cd research/mebook-customer-research && python3 build.py

Source: data.json (every quote, count and link; the English report is report.md). Output: mebook-customer-research.html.
Fails on a broken entry (unknown theme, a quote number that does not exist, an em or en dash, the brand misspelt).
Local only: no Vercel address, not an artifact. Standard library only.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
import design  # noqa: E402

SRC = os.path.join(HERE, "data.json")
HOOKS = os.path.join(ROOT, "research", "mebook-hooks", "hooks.json")   # built by research/mebook-hooks/assemble.py
OUT = os.path.join(HERE, "mebook-customer-research.html")
PAGE = "research/mebook-customer-research/mebook-customer-research.html"
CAT_SET = "mebook-themes"
DASHES = re.compile("[–—]")
STRENGTH = {"strong": "success", "medium": "info", "weak": "warning"}
KIND = {"motivation": ("success", "מניע"), "objection": ("warning", "התנגדות"), "both": ("info", "גם וגם")}

DATE_TXT = re.compile(r"(?<![\d/])(\d{2} / \d{2}(?: / \d{4})?|\d{2} / \d{4})(?![\d/])")
HANDLE = re.compile(r"(?<![\w@])(@[A-Za-z0-9_.]*[A-Za-z0-9_])")


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def ltr(s):
    s = DATE_TXT.sub(r'<span class="lb-ltr">\1</span>', s)
    return HANDLE.sub(r'<span class="lb-ltr">\1</span>', s)


def inline(s):
    """Escaped text: `code` spans, **bold**, dates and @handles kept left to right."""
    out = []
    for i, p in enumerate(re.split(r"`([^`]+)`", str(s or ""))):
        if i % 2:
            out.append(f'<code class="lb-ltr">{esc(p)}</code>')
        else:
            t = ltr(esc(p))
            out.append(re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t))
    return "".join(out)


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


def validate(d):
    errs = []
    themes = set(design.categories(CAT_SET))
    nums = {e["n"] for e in d["evidence"]}
    if len(nums) != len(d["evidence"]):
        errs.append("duplicate quote numbers")
    for e in d["evidence"]:
        for t in e["themes"]:
            if t not in themes:
                errs.append(f"#{e['n']}: unknown theme {t}")
        if e["kind"] not in KIND:
            errs.append(f"#{e['n']}: kind")
        if e["src"] not in d["src_labels"] or e["buyer"] not in d["buyer_labels"]:
            errs.append(f"#{e['n']}: src or buyer label")
    for h in d["hypotheses"]:
        for r in h["refs"]:
            if r not in nums:
                errs.append(f"{h['id']}: refers to unknown quote {r}")
    for g in d["language"]:
        for it in g["items"]:
            if it["ref"] is not None and it["ref"] not in nums:
                errs.append(f"language: unknown quote {it['ref']}")
    fids = [x.get("id") or "" for x in d["summary"] + d["patterns"]]
    if len(set(fids)) != len(fids) or not all(re.match(r"^[a-z0-9-]{1,40}$", f) for f in fids):
        errs.append("summary and patterns need unique ids (a-z, 0-9, -): experiments link to them as finding:<id>")
    for p in d["patterns"]:
        if p["theme"] and p["theme"] not in themes:
            errs.append(f"pattern theme {p['theme']}")
        if p["strength"] not in STRENGTH:
            errs.append(f"pattern strength {p['strength']}")
    # every review of the two source files is a card (15 Nov 2026, Yarin: "i dont want any missing pieces")
    covered = {c for e in d["evidence"] for c in e.get("codes", [])}
    for fn, pre in (("google-reviews.json", "G"), ("site-reviews.json", "S")):
        with open(os.path.join(HERE, "sources", fn), encoding="utf-8") as f:
            for x in json.load(f)["items"]:
                if x["id"] not in covered:
                    errs.append(f"{x['id']} ({pre}) is not a card in the evidence table: add it to data.json evidence, with its code in codes")
    # the cubes and the five themed patterns count the table, so they cannot drift from it
    def cnt(theme, **kw):
        return sum(e.get("count", 1) for e in d["evidence"] if theme in e["themes"] and all(e[k] == v for k, v in kw.items()))
    pro = sum(e.get("count", 1) for e in d["evidence"] if "likeness" in e["themes"] and e["kind"] == "motivation" and e["buyer"] != "prospect")
    con = sum(e.get("count", 1) for e in d["evidence"] if "likeness" in e["themes"] and e["kind"] != "motivation")
    want = {"recognition": str(cnt("recognition")), "gifters": str(cnt("gifters")), "repeat": str(cnt("repeat")),
            "likeness": f"{pro} מול {con}", "questions": str(cnt("questions"))}
    for m in d["metrics"]:
        if want.get(m["theme"]) != m["n"]:
            errs.append(f"cube {m['theme']} says {m['n']} but the evidence table counts {want.get(m['theme'])}")
    pn = {"p-recognition": cnt("recognition"), "p-gifters": cnt("gifters"), "p-repeat": cnt("repeat"), "p-likeness": pro, "p-questions": cnt("questions")}
    for p in d["patterns"]:
        if p["id"] in pn and p["n"] != pn[p["id"]]:
            errs.append(f"pattern {p['id']} says {p['n']} but the evidence table counts {pn[p['id']]}")
    for s in strings(d):
        if DASHES.search(s):
            errs.append(f"em or en dash in: {s[:70]}")
        if "לומבוק" in s:
            errs.append(f"brand spelt לומבוק in: {s[:70]}")
    return errs


def link(url, label):
    if not url:
        return ""
    return f'<a class="lb-btn secondary sm" href="{esc(url)}" target="_blank" rel="noopener">{design.icon("open-out")}<span>{esc(label)}</span></a>'


def theme_chip(d, key):
    it = design.categories(CAT_SET)[key]
    return (f'<button type="button" class="lb-chip cat lb-cat-{it["cat"]} mb-chip-btn" data-chip="{key}" aria-pressed="false" '
            f'title="הצגת כל האמירות בנושא הזה">{esc(d["themes"][key]["short"])}</button>')


def cat(key):
    return f"lb-cat-{design.categories(CAT_SET)[key]['cat']}" if key else "lb-cat-0"


# ---- the 100 purchase intents (purchase-intents.md is their only source; the page parses it) ----
INTENTS = os.path.join(HERE, "purchase-intents.md")
MB_REEL_INTENTS = os.path.join(HERE, "mebook-reel-intents.json")   # MeBook reel or ad id -> intent numbers, a topical match (15 Nov 2026)


def load_intent_reels(intent_ns):
    """{intent n: [hooks.json item, ...]}: MeBook's own reels and video ads (research/mebook-hooks/hooks.json) per purchase intent.
    Fails on an id that is not in hooks.json, an unknown intent, or a reel or ad with no link."""
    with open(MB_REEL_INTENTS, encoding="utf-8") as f:
        m = json.load(f)["reels"]
    with open(HOOKS, encoding="utf-8") as f:
        items = {i["key"]: i for i in json.load(f)["items"]}
    out, errs = {n: [] for n in intent_ns}, []
    for key, ns in m.items():
        if key not in items:
            errs.append(f"mebook-reel-intents.json: {key} is not in research/mebook-hooks/hooks.json")
            continue
        for n in ns:
            if n not in out:
                errs.append(f"mebook-reel-intents.json: {key} names unknown intent {n}")
            else:
                out[n].append(items[key])
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    for v in out.values():   # reels by views, then the ads by their library rank
        v.sort(key=lambda i: (i["kind"] == "ad", -(i.get("views") or 0), i.get("ad_rank") or 0))
    return out


def reel_chip(i):
    ad = i["kind"] == "ad"
    text = DASHES.sub("-", " ".join((i.get("on_screen") or i.get("spoken") or i.get("caption") or "").split()))
    short = text[:40] + ("..." if len(text) > 40 else "")
    who = f'מודעה {i["ad_rank"]}' if ad else i["account"]
    views = "" if ad else f' · <span class="lb-ltr">{i["views"]:,}</span>'
    title = esc(f'{text} ({ddmmyyyy(i["date"])}' + ("" if ad else f', {i["views"]:,} צפיות') + ")")
    return (f'<a class="lb-chip mb-reel {"outline" if ad else "info"}" href="{esc(i["url"])}" target="_blank" rel="noopener" title="{title}">'
            f'<span class="lb-ltr">{esc(who)}</span> · <span dir="rtl" translate="no">{esc(short)}</span>{views}</a>')


ILABELS = {"ישירה": ("direct", "success", "ראיה ישירה"), "הסקה": ("inference", "info", "הסקה"), "השערה": ("hypothesis", "warning", "השערה")}
CODE = re.compile(r"(?<![\w/.#-])([GSQL])(\d{1,2})(?![\w])")


def cat_label(name):
    """A category heading without its Hebrew letter prefix ("ז. התאמה ..." -> "התאמה ...")."""
    return re.sub(r"^[א-ת]{1,2}\. ", "", name)


def row_cells(line):
    return [x.strip() for x in line.strip().strip("|").split("|")]


def parse_intents():
    """Categories, the 100 rows, the limits list, the top 10 and their sales hypotheses, from purchase-intents.md."""
    with open(INTENTS, encoding="utf-8") as f:
        lines = f.read().split("\n")
    out = {"cats": [], "intents": [], "limits": [], "top": [], "hyps": {}}
    section = sub = cat_name = None
    for line in lines:
        if line.startswith("## "):
            section, cat_name, sub = line[3:].strip(), None, None
            continue
        if line.startswith("### "):
            cat_name = line[4:].strip()
            out["cats"].append(cat_name)
            continue
        if line.startswith("**") and line.endswith("**"):
            sub = line.strip("*")
            continue
        if section == "הערכת הכיסוי של המחקר" and sub == "המגבלות" and line.startswith("- "):
            out["limits"].append(line[2:])
        elif section == "הכוונות" and cat_name and re.match(r"^\| \d+ \| ", line):
            c = row_cells(line)
            lab, _, src = c[4].partition(" · ")
            out["intents"].append({"n": int(c[0]), "intent": c[1], "buyer": c[2], "hes": c[3], "label": lab, "src": src,
                                   "show": c[5], "cat": len(out["cats"]), "cat_name": cat_name, "flag": "⚑" in c[5]})
        elif section and section.startswith("10 הכוונות") and re.match(r"^\| \d+ \| ", line):
            c = row_cells(line)
            out["top"].append({"n": int(c[0]), "title": c[1], "why": c[2]})
        elif section and section.startswith("השערות מכירה"):
            m = re.match(r"^\d+\. \*\*#(\d+)\*\* (.*)$", line)
            if m:
                out["hyps"][int(m.group(1))] = m.group(2)
    return out


def validate_intents(it):
    errs = []
    if [x["n"] for x in it["intents"]] != list(range(1, len(it["intents"]) + 1)):
        errs.append("purchase-intents.md: intent numbers are not 1..N in order")
    for x in it["intents"]:
        if x["label"] not in ILABELS:
            errs.append(f"intent {x['n']}: unknown label {x['label']!r}")
    nums = {x["n"] for x in it["intents"]}
    for t in it["top"]:
        if t["n"] not in nums or t["n"] not in it["hyps"]:
            errs.append(f"top intent {t['n']}: missing row or sales hypothesis")
    for s in strings(it):
        if DASHES.search(s):
            errs.append(f"purchase-intents.md: em or en dash in: {s[:70]}")
        if "לומבוק" in s:
            errs.append(f"purchase-intents.md: brand spelt לומבוק in: {s[:70]}")
    return errs


def source_tips():
    """G, S and L codes -> the text behind them, for the hover title on each code."""
    tips = {}
    for fn in ("google-reviews.json", "site-reviews.json"):
        with open(os.path.join(HERE, "sources", fn), encoding="utf-8") as f:
            for item in json.load(f)["items"]:
                tips[item["id"]] = item["text"]
    with open(os.path.join(HERE, "sources", "live-pages.md"), encoding="utf-8") as f:
        for line in f:
            if re.match(r"^\| L\d+ \|", line):
                c = row_cells(line)
                tips[c[0]] = c[3]
    return tips


def codes(s, quote_nums, tips):
    """Inline text with Q codes linked to the quote card and G / S / L codes carrying their source text on hover."""
    def rep(m):
        code = m.group(0)
        if m.group(1) == "Q" and int(m.group(2)) in quote_nums:
            return f'<a class="mb-code" href="#e-{m.group(2)}" data-ref="{m.group(2)}">{code}</a>'
        if code in tips:
            return f'<abbr class="mb-code" title="{esc(tips[code][:400])}">{code}</abbr>'
        return code
    return CODE.sub(rep, inline(s))


CSS = """
.mb-hero h1 { font-size: clamp(1.8rem, 4vw, 2.6rem); }
.mb-top { gap: var(--sp-2); }
.mb-top .lb-search { flex: 1 1 18rem; max-width: 34rem; }
.mb-top .lb-search .lb-input { font-size: var(--fs-callout); padding-inline-end: 2.4rem; }
.mb-count { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); white-space: nowrap; }
.mb-section-head { display: flex; align-items: center; gap: var(--sp-3); margin-bottom: var(--sp-4); }
.mb-section-head h2 { margin: 0; }
.mb-section-head p { margin: .15rem 0 0; color: var(--text-2); }
.lb-section { scroll-margin-top: 5rem; }
/* one section at a time (15 Nov 2026, Yarin: each sidebar tab opens on its own, not as a long list) */
.lb-section[hidden] { display: none; }
.mb-lang .lb-card:last-child { grid-column: 1 / -1; }
.mb-hero { margin-bottom: var(--sp-4); }

/* number cubes: also the theme filters of the quote table */
.mb-cubes.lb-metrics { grid-template-columns: repeat(auto-fill, minmax(11.5rem, 1fr)); }
button.lb-metric { font: inherit; text-align: start; color: inherit; border: 1px solid transparent; border-radius: var(--r-lg); padding: var(--sp-3) var(--sp-4); cursor: pointer;
  transition: transform var(--dur-2) var(--ease-spring), box-shadow var(--dur-2) var(--ease); }
button.lb-metric:active { transform: scale(var(--press)); }
button.lb-metric[aria-pressed="true"] { border-color: var(--tc); }
.mb-cubes.is-filtering button.lb-metric[aria-pressed="false"] { opacity: .5; }
.mb-cubes .lb-metric-value small { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); }

/* identity */
.mb-id { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr)); }
.mb-id .lb-card { display: grid; gap: .35rem; align-content: start; }
.mb-id h3 { margin: 0; font-size: var(--fs-callout); }
.mb-id p { margin: 0; color: var(--text-2); }

/* summary findings */
.mb-sum { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(19rem, 1fr)); }
.mb-sum .lb-card { display: grid; gap: .5rem; align-content: start; }
.mb-sum h3 { margin: 0; font-size: var(--fs-headline); display: flex; align-items: center; gap: .5rem; }
.mb-sum p { margin: 0; }

/* tables */
.mb-table td, .mb-table th { vertical-align: top; }
.mb-table .q { min-width: 22rem; max-width: 36rem; line-height: 1.55; }
.mb-table .n { width: 2.4rem; text-align: center; color: var(--text-3); font-family: var(--font-2); font-weight: 700; }
.mb-table .meta { color: var(--text-2); font-size: var(--fs-footnote); }
.mb-table .meta { margin-top: .2rem; }
.mb-ncell { text-align: center; }
.lb-table-wrap { max-width: 100%; overflow-x: auto; }
@media (max-width: 44rem) {
  .mb-table, .mb-table tbody, .mb-table tr, .mb-table td { display: block; width: auto; }
  .mb-table thead { display: none; }
  .mb-table tr { padding: var(--sp-3) var(--sp-3) var(--sp-2); border-bottom: 1px solid var(--line); }
  .mb-table td { padding: .2rem 0; border: 0; }
  .mb-table td[data-label]::before { content: attr(data-label); display: block; font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; color: var(--text-3); }
  .mb-ncell { text-align: start; }
}

/* quote cards */
.mb-quotes { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fill, minmax(min(100%, 24rem), 1fr)); align-items: start; }
.mb-q { display: grid; gap: .6rem; scroll-margin-top: 6rem; }
.mb-q[hidden] { display: none; }
.mb-q.is-flash { animation: mb-flash 1.8s var(--ease); }
@keyframes mb-flash { 0%, 45% { box-shadow: 0 0 0 3px var(--accent), var(--glass-card-lift, none); } 100% { box-shadow: 0 0 0 0 transparent, var(--glass-card-lift, none); } }
.mb-q-head { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem; }
.mb-qn { font-family: var(--font-2); font-weight: 800; color: var(--text-3); margin-inline-end: .2rem; }
.mb-src { margin-inline-start: auto; }
.mb-quote { margin: 0; font-size: var(--fs-callout); line-height: 1.6; font-weight: 500; }
.mb-q-meta { display: flex; flex-wrap: wrap; align-items: center; gap: .3rem .5rem; font-size: var(--fs-footnote); color: var(--text-2); }
.mb-when { font-family: var(--font-2); }
.mb-sep { color: var(--text-3); }
.mb-q-note { margin: 0; font-size: var(--fs-footnote); color: var(--text-3); }
.mb-chip-btn { font: inherit; border: 0; cursor: pointer; transition: transform var(--dur-2) var(--ease-spring), box-shadow var(--dur-2) var(--ease); }
.mb-chip-btn:active { transform: scale(var(--press)); }
.mb-chip-btn[aria-pressed="true"] { box-shadow: 0 0 0 2px var(--tc, var(--accent)); }
.mb-chips { display: flex; flex-wrap: wrap; gap: .3rem; }
.mb-links a { text-decoration: none; }
.mb-filterrow { display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-2) var(--sp-3); margin-block: var(--sp-3); }
.mb-filterrow .lb-dim { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; }
.lb-main, .lb-page, .lb-section { min-width: 0; }
.mb-filterrow .lb-filters { flex-wrap: wrap; }

/* language bank */
.mb-lang { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(19rem, 1fr)); }
.mb-lang .lb-card { display: grid; gap: .6rem; align-content: start; }
.mb-lang h3 { margin: 0; font-size: var(--fs-callout); }
.mb-lang ul { list-style: none; margin: 0; padding: 0; display: grid; gap: .4rem; }
.mb-lang li { display: flex; align-items: baseline; justify-content: space-between; gap: .6rem; }
.mb-lang li span.t { line-height: 1.5; }
.mb-lang a.ref { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; color: var(--text-3); text-decoration: none; white-space: nowrap; }

/* hypotheses */
.mb-hyps { display: grid; gap: var(--sp-4); }
.mb-hyp { display: grid; gap: var(--sp-3); }
.mb-hyp-head { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; }
.mb-hyp-head h3 { margin: 0; font-size: var(--fs-title-3, 1.2rem); flex: 1 1 14rem; }
.mb-hid { font-family: var(--font-2); font-weight: 800; }
.mb-statement { margin: 0; font-size: var(--fs-callout); line-height: 1.65; }
.mb-hyp-grid { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
.mb-hyp-grid .lb-sheet { display: grid; gap: .35rem; align-content: start; }
.mb-hyp-grid h4 { margin: 0; }
.mb-hyp-grid p { margin: 0; line-height: 1.55; }
.mb-hook { font-size: var(--fs-callout); font-weight: 700; }
.mb-refs { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem; }
.mb-refs a { text-decoration: none; }

/* experiments */
.mb-exp { display: grid; gap: var(--sp-3); }
.mb-exp .lb-card { display: grid; grid-template-columns: auto 1fr; gap: var(--sp-3); align-items: start; }
.mb-exp .lb-disc { align-self: start; }
.mb-exp b.t { display: block; margin-bottom: .2rem; }
.mb-exp p { margin: 0; color: var(--text-2); }

.mb-qs { counter-reset: q; display: grid; gap: var(--sp-2); list-style: none; padding: 0; margin: 0; }
.mb-qs li { counter-increment: q; display: flex; gap: .75rem; align-items: baseline; }
.mb-qs li::before { content: counter(q); font-family: var(--font-2); font-weight: 800; color: var(--accent); min-width: 1.4rem; }

.mb-claims li { margin-bottom: .5rem; }
.mb-sugg { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
/* purchase intents */
.mb-ints { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fill, minmax(min(100%, 22rem), 1fr)); align-items: start; }
.mb-int { display: grid; gap: .55rem; scroll-margin-top: 6rem; }
.mb-int[hidden] { display: none; }
.mb-int.is-flash, .mb-top10 .lb-card.is-flash { animation: mb-flash 1.8s var(--ease); }
.mb-int-text { margin: 0; font-size: var(--fs-callout); line-height: 1.55; font-weight: 600; }
.mb-int .lb-kv { margin: 0; font-size: var(--fs-footnote); }
.mb-int .lb-kv dd { line-height: 1.5; }
.mb-code { font-family: var(--font-2); font-weight: 700; text-decoration: none; direction: ltr; unicode-bidi: isolate; }
abbr.mb-code { text-decoration: underline dotted; cursor: help; }
.mb-top10 { display: grid; gap: var(--sp-3); }
.mb-top10 .lb-card { display: grid; grid-template-columns: auto 1fr; gap: var(--sp-3); align-items: start; }
.mb-top10 .t { display: block; margin-bottom: .2rem; }
.mb-top10 p { margin: 0; color: var(--text-2); }
.mb-top10 .lb-sheet { margin-top: .5rem; }
.mb-top10 .lb-sheet p { color: var(--text); line-height: 1.6; }
.mb-icounts { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
.mb-reels { display: grid; gap: .35rem; margin-top: .25rem; }
.mb-reels > summary { cursor: pointer; list-style: none; }
.mb-reels > summary::-webkit-details-marker { display: none; }
.mb-reels[open] > summary { margin-bottom: .2rem; }
.mb-reel { text-decoration: none; white-space: normal; height: auto; max-width: 100%; text-align: start; line-height: 1.35; padding-block: .25rem; }
a.mb-reel:hover { filter: brightness(.96); text-decoration: underline; }
/* experiment log */
.mbx-list { display: grid; gap: var(--sp-2); }
.mbx-row { display: grid; gap: .35rem; text-align: start; font: inherit; color: inherit; cursor: pointer; width: 100%; }
.mbx-row:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
.mbx-row-title { font-weight: 700; }
.mbx-row-meta { font-size: var(--fs-footnote); color: var(--text-2); }
.mbx-inline { display: inline-grid; min-width: 11rem; }
.mbx-src { display: grid; gap: .4rem; justify-items: start; margin-top: .4rem; }
.mbx-src:empty { display: none; }
.mbx-src ul { list-style: none; margin: 0; padding: 0; display: grid; gap: .35rem; width: 100%; }
.mbx-srclink { font: inherit; font-weight: 700; color: var(--accent); background: none; border: 0; padding: 0; cursor: pointer; text-align: start; }
.mbx-learn { font-size: var(--fs-footnote); color: var(--text-2); margin-top: .15rem; }
dialog.mbx-dlg { width: min(52rem, calc(100vw - 32px)); }
.mbx-dlg .lb-dialog-body { overflow: auto; max-height: calc(100dvh - 7rem); }
.mbx-dlg-title { flex: 1; padding-inline-start: var(--sp-4); }
.mbx-form { display: grid; gap: var(--sp-4); padding: var(--sp-4); }
.mbx-fs { border: 0; margin: 0; padding: 0; display: grid; gap: var(--sp-3); min-width: 0; }
.mbx-form, .mbx-form .lb-field, .mbx-grid > * { min-width: 0; }
.mbx-fs legend { font-weight: 800; font-size: var(--fs-headline); margin-bottom: var(--sp-2); }
.mbx-grid { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr)); }
.mbx-hint { font-weight: 500; color: var(--text-3); }
.mbx-req { color: var(--danger, var(--accent)); font-weight: 700; margin-inline-start: .4rem; }
.mbx-radios { display: flex; flex-wrap: wrap; gap: var(--sp-3); }
.mbx-linkchip { gap: .35rem; white-space: normal; max-width: 100%; height: auto; text-align: start; }
.mbx-linkchip button { border: 0; background: none; cursor: pointer; color: inherit; padding: 0 .1rem; }
.mbx-metrics.lb-metrics { grid-template-columns: repeat(auto-fit, minmax(min(100%, 11rem), 1fr)); }
.mbx-metrics .lb-metric-value small { display: block; font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); }
.mbx-na { color: var(--text-3); }
.mbx-prompts { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); }
.mbx-prompts li { padding: var(--sp-2) var(--sp-3); border-radius: var(--r-md, 12px); background: var(--fill); color: var(--text-3); line-height: 1.55; }
.mbx-prompts li.is-on { background: var(--tint-soft); color: var(--text); }
.mbx-prompt-nums { font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }
.mbx-chain p { margin: 0; }
/* 50 hooks (15 Nov 2026) */
.mbh-cubes.lb-metrics { grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr)); }
.mbh-cubes .lb-metric-value small { font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); }
.mbh-list { list-style: none; margin: 0; padding: 0; }
.mbh-list[hidden], .mbh-row[hidden] { display: none; }
.mbh-row { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: start; gap: var(--sp-2) var(--sp-3); padding: var(--sp-3) var(--sp-4); }
.mbh-main { display: grid; gap: .35rem; min-width: 0; }
.mbh-text { margin: 0; font-size: var(--fs-callout); line-height: 1.55; font-weight: 600; overflow-wrap: anywhere; }
.mbh-tags { display: flex; flex-wrap: wrap; gap: .3rem; }
.mbh-meta { display: grid; justify-items: end; gap: .15rem; font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); white-space: nowrap; }
.mbh-who .lb-ltr, .mbh-views { white-space: nowrap; }
.mbh-views b { font-size: var(--fs-callout); color: var(--text); font-variant-numeric: tabular-nums; }
.mbh-open { display: inline-flex; align-items: center; gap: .3rem; color: var(--tint); font-weight: 600; text-decoration: none; }
.mbh-open svg { width: .95rem; height: .95rem; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.mbh-open:hover { text-decoration: underline; }
@media (max-width: 44rem) {
  .mbh-row { grid-template-columns: auto minmax(0, 1fr); }
  .mbh-meta { grid-column: 2; display: flex; flex-wrap: wrap; align-items: baseline; gap: .2rem .7rem; white-space: normal; }
}
@media print { .lb-sidebar, .lb-topbar, .mb-filterrow, .mb-cubes { display: none; } .lb-app { display: block; } .lb-section[hidden] { display: grid; } }
"""

JS = r"""<script>
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  // tabs: the sidebar shows one section at a time
  var sections = $$('.lb-section'), items = $$('.lb-sidebar .lb-nav-item'), side = $('.lb-sidebar'), scrim = $('.lb-scrim'), curTab = '';
  function closeNav() { side.classList.remove('is-open'); scrim.hidden = true; }
  function showTab(id, keepScroll) {
    if (!sections.some(function (s) { return s.id === id; })) id = sections[0].id;
    curTab = id;
    sections.forEach(function (s) { s.hidden = s.id !== id; });
    items.forEach(function (a) { if (a.getAttribute('href') === '#' + id) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    var c = document.getElementById('mb-count'); if (c) c.hidden = id !== 'evidence';
    if (!keepScroll) window.scrollTo(0, 0);
  }
  // the tab that holds an element (a quote, an intent), opened before the page scrolls to it
  function openFor(el) { var s = el && el.closest && el.closest('.lb-section'); if (s && s.hidden) showTab(s.id, true); }
  var rows = $$('#mb-evidence .mb-q'), input = $('#mb-q'), count = $('#mb-count'), cubes = $('.mb-cubes'), clear = $('#mb-clear'), empty = $('#mb-empty');
  var state = { q: '', themes: [], kind: '', buyer: '' };
  function norm(s) {
    return (s || '').toLowerCase().replace(/[֑-ׇ]/g, '').replace(/[׳']/g, "'").replace(/[״"“”]/g, '"')
      .replace(/ם/g, 'מ').replace(/ן/g, 'נ').replace(/ץ/g, 'צ').replace(/ף/g, 'פ').replace(/ך/g, 'כ');
  }
  rows.forEach(function (r) { r._t = norm(r.textContent); });
  function apply() {
    var terms = norm(state.q).split(/\s+/).filter(Boolean), shown = 0;
    rows.forEach(function (r) {
      var th = (r.dataset.themes || '').split(' ');
      var ok = (!state.themes.length || state.themes.some(function (t) { return th.indexOf(t) >= 0; })) &&
        (!state.kind || r.dataset.kind === state.kind) && (!state.buyer || r.dataset.buyer === state.buyer) &&
        terms.every(function (t) { return r._t.indexOf(t) >= 0; });
      r.hidden = !ok; if (ok) shown++;
    });
    count.textContent = shown === rows.length ? rows.length + ' אמירות' : shown + ' מתוך ' + rows.length;
    empty.hidden = shown > 0;
    var f = !!(state.q || state.themes.length || state.kind || state.buyer);
    clear.hidden = !f; cubes.classList.toggle('is-filtering', state.themes.length > 0);
    $$('[data-chip]').forEach(function (c) { c.setAttribute('aria-pressed', state.themes.indexOf(c.dataset.chip) >= 0 ? 'true' : 'false'); });
  }
  input.addEventListener('input', function () {
    state.q = input.value; apply();
    if (state.q && ['evidence', 'intents', 'hooks'].indexOf(curTab) < 0) showTab('evidence');
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === '/' && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) { ev.preventDefault(); input.focus(); }
  });
  $$('.mb-cubes [data-theme]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.dataset.theme, i = state.themes.indexOf(t);
      if (i >= 0) state.themes.splice(i, 1); else state.themes.push(t);
      b.setAttribute('aria-pressed', i >= 0 ? 'false' : 'true'); apply();
      if (state.themes.length) showTab('evidence');
    });
  });
  // a theme chip on a card or in the patterns table: show every quote of that theme (press again: show all)
  $$('[data-chip]').forEach(function (c) {
    c.addEventListener('click', function () {
      var t = c.dataset.chip;
      state.themes = (state.themes.length === 1 && state.themes[0] === t) ? [] : [t];
      $$('.mb-cubes [data-theme]').forEach(function (b) { b.setAttribute('aria-pressed', state.themes.indexOf(b.dataset.theme) >= 0 ? 'true' : 'false'); });
      apply(); showTab('evidence');
    });
  });
  $$('.lb-filters [data-kind]').forEach(function (b) { b.addEventListener('click', function () {
    state.kind = b.dataset.kind; $$('.lb-filters [data-kind]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); apply(); }); });
  $$('.lb-filters [data-buyer]').forEach(function (b) { b.addEventListener('click', function () {
    state.buyer = b.dataset.buyer; $$('.lb-filters [data-buyer]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); apply(); }); });
  clear.addEventListener('click', function () {
    state = { q: '', themes: [], kind: '', buyer: '' }; input.value = '';
    $$('.mb-cubes [data-theme]').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
    $$('.lb-filters [data-kind]').forEach(function (x) { x.setAttribute('aria-pressed', x.dataset.kind === '' ? 'true' : 'false'); });
    $$('.lb-filters [data-buyer]').forEach(function (x) { x.setAttribute('aria-pressed', x.dataset.buyer === '' ? 'true' : 'false'); });
    apply();
  });

  // a quote number jumps to its row (and clears the filter if the row is hidden)
  $$('a[data-ref]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      var r = $('#e-' + a.dataset.ref); if (!r) return;
      openFor(r);
      if (r.hidden) clear.click();
      r.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
      r.classList.remove('is-flash'); void r.offsetWidth; r.classList.add('is-flash');
    });
  });

  // sidebar: drawer on phones, a tab per section
  $('#mb-menu').addEventListener('click', function () { side.classList.add('is-open'); scrim.hidden = false; });
  scrim.addEventListener('click', closeNav);
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') closeNav(); });
  items.forEach(function (a) { a.addEventListener('click', function (ev) {
    ev.preventDefault(); closeNav();
    showTab(a.getAttribute('href').slice(1));
    history.replaceState(null, '', location.pathname + location.search + a.getAttribute('href'));
  }); });
  function fromHash() {
    var h = decodeURIComponent(location.hash.slice(1)), el = h && document.getElementById(h);
    var sec = el && (el.classList.contains('lb-section') ? el : el.closest('.lb-section'));
    showTab(sec ? sec.id : '', !!sec && sec !== el);
    if (sec && sec !== el) el.scrollIntoView({ block: 'center' });
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();

  // purchase intents: filter by label and category, the top search applies here too
  var icards = $$('#mb-intents .mb-int'), istate = { label: '', cat: '', reel: '' }, icount = $('#mb-icount'), iempty = $('#mb-iempty'), iclear = $('#mb-iclear');
  icards.forEach(function (c) { c._t = norm(c.textContent); });
  function iapply() {
    var terms = norm(state.q).split(/\s+/).filter(Boolean), n = 0;
    icards.forEach(function (c) {
      var ok = (!istate.label || c.dataset.label === istate.label) && (!istate.cat || c.dataset.cat === istate.cat) && (!istate.reel || c.dataset.reels === istate.reel) &&
        terms.every(function (t) { return c._t.indexOf(t) >= 0; });
      c.hidden = !ok; if (ok) n++;
    });
    if (icount) icount.textContent = n === icards.length ? icards.length + ' כוונות' : n + ' מתוך ' + icards.length;
    if (iempty) iempty.hidden = n > 0;
    if (iclear) iclear.hidden = !(istate.label || istate.cat || istate.reel);
  }
  function group(attr, key) {
    $$('[' + attr + ']').forEach(function (b) { b.addEventListener('click', function () {
      istate[key] = b.getAttribute(attr);
      $$('[' + attr + ']').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      iapply();
    }); });
  }
  group('data-ilabel', 'label'); group('data-icat', 'cat'); group('data-ireel', 'reel');
  function iclearAll() {
    istate = { label: '', cat: '', reel: '' };
    $$('[data-ireel]').forEach(function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-ireel') === '' ? 'true' : 'false'); });
    $$('[data-ilabel]').forEach(function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-ilabel') === '' ? 'true' : 'false'); });
    $$('[data-icat]').forEach(function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-icat') === '' ? 'true' : 'false'); });
    iapply();
  }
  if (iclear) iclear.addEventListener('click', iclearAll);
  input.addEventListener('input', iapply);
  clear.addEventListener('click', iapply);
  $$('a[data-int]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      var c = $('#i-' + a.dataset.int); if (!c) return;
      openFor(c);
      if (c.hidden) { input.value = ''; state.q = ''; apply(); iclearAll(); }
      c.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
      c.classList.remove('is-flash'); void c.offsetWidth; c.classList.add('is-flash');
    });
  });
  iapply();
  apply();
})();
</script>"""


def xbox(key):
    """The box on a source record where the experiment log shows its experiments and the button to start one (filled by
    experiments.src.js once the log has loaded)."""
    return f'<div class="mbx-src" data-for="{esc(key)}"></div>'


EXP_JS = os.path.join(HERE, "experiments-metrics.js"), os.path.join(HERE, "experiments.src.js")


def mb_src(d, it):
    """The records experiments link to, for the log's prefill and labels (window.MB_SRC)."""
    tops = it["hyps"]
    return {
        "intents": {str(x["n"]): {"intent": x["intent"], "buyer": x["buyer"], "hes": x["hes"], "show": x["show"],
                                  "label": x["label"], "sales": tops.get(x["n"], "")} for x in it["intents"]},
        "findings": {**{s["id"]: {"title": s["title"], "text": s["text"]} for s in d["summary"]},
                     **{p["id"]: {"title": p["finding"], "text": p["limits"]} for p in d["patterns"]}},
        "hyps": {h["id"]: {"title": h["title"], "statement": h["statement"], "hook": h["hook"], "footage": h["footage"],
                           "test": h["test"]} for h in d["hypotheses"]},
    }


def exp_scripts():
    out = []
    for fn in EXP_JS:
        with open(fn, encoding="utf-8") as f:
            out.append(re.sub(r"</(script)", r"<\\/\1", f.read(), flags=re.I))   # only a closing script tag needs escaping
    return "\n".join(out)


def log_html():
    status = "".join(f'<button type="button" data-xstatus="{k}" aria-pressed="false">{v}</button>' for k, v in
                      (("idea", "רעיון"), ("ready", "מוכן"), ("running", "רץ"), ("completed", "הושלם"), ("archived", "בארכיון")))
    return (
        '<p class="lb-callout warning" id="mbx-note" hidden></p>'
        '<div class="mb-filterrow"><button class="lb-btn" id="mbx-new" type="button">+ ניסוי חדש</button><span class="mb-count" id="mbx-count"></span></div>'
        f'<div class="mb-filterrow"><span class="lb-dim">סטטוס</span><div class="lb-filters" role="group" aria-label="סטטוס">'
        f'<button type="button" data-xstatus="" aria-pressed="true">הכול</button>{status}</div></div>'
        '<div class="mb-filterrow"><span class="lb-dim">סוג</span><div class="lb-segmented" role="group" aria-label="אורגני או ממומן">'
        '<button type="button" data-xmode="" aria-pressed="true">הכול</button><button type="button" data-xmode="organic" aria-pressed="false">אורגני</button>'
        '<button type="button" data-xmode="paid" aria-pressed="false">ממומן</button></div>'
        '<label class="lb-field mbx-inline">ערוץ<select class="lb-select" id="mbx-f-channel"></select></label>'
        '<label class="lb-field mbx-inline">כוונת קנייה<select class="lb-select" id="mbx-f-intent"></select></label></div>'
        '<div class="mbx-list" id="mbx-list"></div>')


def exp_dialog():
    def f(name, label, kind="input", hint="", req=False, extra=""):
        star = ' <span class="mbx-req">חובה</span>' if req else ""
        hint_html = f'<small class="mbx-hint">{hint}</small>' if hint else ""
        if kind == "textarea":
            ctl = f'<textarea class="lb-textarea" name="{name}" dir="rtl" rows="3"{extra}></textarea>'
        else:
            ctl = f'<input class="lb-input" name="{name}"{"" if "dir=" in extra else ' dir="rtl"'}{extra}>'
        return f'<label class="lb-field"><span>{label}{star}</span>{ctl}{hint_html}</label>'

    def n(name, label, hint="", cls=""):
        return (f'<label class="lb-field{cls}">{label}<input class="lb-input" name="r_{name}" data-label="{label}" inputmode="decimal" '
                f'dir="ltr" placeholder="לא נמדד">{f"<small class=mbx-hint>{hint}</small>" if hint else ""}</label>')

    def t(name, label):
        return f'<label class="lb-field">{label}<input class="lb-input" name="t_{name}" dir="ltr"></label>'

    status = "".join(f'<option value="{k}">{v}</option>' for k, v in
                     (("idea", "רעיון"), ("ready", "מוכן"), ("running", "רץ"), ("completed", "הושלם"), ("archived", "בארכיון")))
    return f"""<dialog class="lb-dialog mbx-dlg" id="mbx-dlg" aria-labelledby="mbx-dlg-title">
  <div class="lb-dialog-card">
    <div class="lb-dialog-head"><b class="mbx-dlg-title" id="mbx-dlg-title">ניסוי</b><span class="lb-chip success" id="mbx-saved" hidden></span>
      <button class="lb-dialog-x" id="mbx-close" type="button" aria-label="סגירה">✕</button></div>
    <div class="lb-dialog-body">
      <form class="lb-form mbx-form" id="mbx-form" novalidate>
        <div class="mbx-chain" id="mbx-chain" hidden></div>
        <fieldset class="mbx-fs"><legend>הניסוי</legend>
          {f("title", "כותרת", req=True)}
          {f("hypothesis", "השערה", "textarea", "התבנית: אני מאמין ש[קהל] יקנו אם נראה [מסר או הוכחה], כי המניע או ההיסוס שלהם עכשיו הוא [תובנה].", req=True)}
          <button class="lb-btn secondary sm" type="button" id="mbx-tpl">מילוי ההשערה לפי התבנית מהשדות למטה</button>
          <div class="lb-field">מקושר אל<div class="mb-chips" id="mbx-links"></div>
            <select class="lb-select" id="mbx-addlink"><option value="">+ קישור לכוונה, ממצא או השערה</option></select></div>
          <div class="mbx-grid">
            {f("audience", "קהל")}
            {f("motivation", "המניע או ההיסוס שנבדק", "textarea")}
            {f("hook", "הוק")}
            {f("proof", "ההוכחה שמראים", "textarea")}
            {f("cta", "קריאה לפעולה")}
            {f("format", "פורמט", extra=' list="mbx-formats"')}
            {f("channel", "ערוץ", extra=' list="mbx-channels"')}
            {f("content_url", "קישור לתוכן או לקובץ", extra=' dir="ltr"')}
          </div>
          <div class="lb-field">אורגני או ממומן<div class="mbx-radios">
            <label class="lb-check"><input type="radio" name="mode" value="organic"><span>אורגני</span></label>
            <label class="lb-check"><input type="radio" name="mode" value="paid"><span>ממומן</span></label></div></div>
          <div class="mbx-grid">
            <label class="lb-field">סטטוס<select class="lb-select" name="status">{status}</select></label>
            <label class="lb-field">התחלה<input class="lb-input" type="date" name="start"></label>
            <label class="lb-field">סיום<input class="lb-input" type="date" name="end"></label>
          </div>
        </fieldset>
        <fieldset class="mbx-fs"><legend>תוצאות</legend>
          <p class="lb-note">ממלאים ידנית, רק מה שנמדד. שדה ריק הוא ״לא נמדד״, ו 0 הוא ״נמדד, אין״.</p>
          <p class="lb-callout warning" id="mbx-organic-note" hidden>בתוכן אורגני הייחוס חלקי. רכישה מיוחסת היא רכישה שהגיעה דרך הקישור המתויג, או שתועדה ידנית. היא לא מוכיחה שהתוכן גרם למכירה נוספת, ומכירות שלא עברו דרך הקישור לא נספרות.</p>
          <div class="mbx-grid">
            {n("impressions", "חשיפות (impressions)", "כמה פעמים התוכן הוצג, לפי הפלטפורמה")}
            {n("views", "צפיות (views)", "כמה צפיות הפלטפורמה ספרה. לא אותו דבר כמו חשיפות")}
            {n("clicks", "לחיצות יוצאות", "לחיצות על קישור שיוצא מהפלטפורמה")}
            {n("visits", "ביקורים בדף הנחיתה", "לפי האתר או כלי האנליטיקה")}
            {n("purchases", "רכישות מיוחסות", "ריק: לא נמדד. 0: נמדד, אין רכישות")}
            {n("revenue", "הכנסה מיוחסת (₪)")}
            {n("spend", "הוצאה על מודעות (₪)", "רק בניסוי ממומן", " mbx-paid")}
          </div>
          <div class="mbx-grid">
            {t("url", "קישור מעקב")}{t("utm_source", "utm_source")}{t("utm_medium", "utm_medium")}
            {t("utm_campaign", "utm_campaign")}{t("utm_content", "utm_content")}{t("utm_term", "utm_term")}
          </div>
          <div class="mbx-grid">
            {f("data_source", "מקור הנתונים")}
            {f("period", "תקופת הדיווח")}
          </div>
          {f("attribution_notes", "הערות על הייחוס", "textarea")}
          <div class="lb-metrics mbx-metrics" id="mbx-metrics"></div>
          <p class="lb-note">CPA כאן הוא הוצאה על מודעות חלקי רכישות מיוחסות, לא CAC כולל (בלי זמן, מוצר, יוצרים ועלויות אחרות).</p>
        </fieldset>
        <fieldset class="mbx-fs"><legend>למידה</legend>
          <p class="lb-note">שאלות לבדיקה, לא אבחנה. אין כאן סף אוניברסלי: אתם מחליטים מה נחשב הרבה ומה מעט. שאלה נדלקת כשיש את המספרים שהיא מדברת עליהם.</p>
          <ul class="mbx-prompts">
            <li data-prompt="reach_vs_visits"><b>הרבה צפיות ומעט ביקורים?</b> האם התוכן יוצר עניין במוצר עצמו, ולא רק בסיפור? האם הקריאה לפעולה ברורה ונראית? <span class="mbx-prompt-nums"></span></li>
            <li data-prompt="visits_vs_purchases"><b>הרבה ביקורים ומעט רכישות?</b> האם דף הנחיתה ממשיך את מה שהתוכן הראה? מה עם ההצעה, המחיר, המשלוח, האמון ותהליך התשלום? <span class="mbx-prompt-nums"></span></li>
            <li data-prompt="single_purchase"><b>רכישה אחת, גם זולה:</b> סימן מבטיח, אבל לא מספיק כדי להכריז על מנצח. כדאי לחזור על הניסוי לפני מסקנה. <span class="mbx-prompt-nums"></span></li>
          </ul>
          <div class="lb-field">מסקנה<div class="mbx-radios">
            <label class="lb-check"><input type="radio" name="conclusion" value="promising"><span>מבטיח</span></label>
            <label class="lb-check"><input type="radio" name="conclusion" value="inconclusive"><span>לא חד משמעי</span></label>
            <label class="lb-check"><input type="radio" name="conclusion" value="not_supported"><span>לא נתמך</span></label></div></div>
          {f("explanation", "הסבר", "textarea", "חובה לפני שמסמנים ״הושלם״: מה ראינו, ומה זה אומר ומה לא")}
          {f("next", "הניסוי הבא", "textarea", "ממלא את ההשערה של ניסוי ההמשך")}
        </fieldset>
        <p class="lb-form-error" id="mbx-err" role="alert" hidden></p>
        <div class="lb-form-actions">
          <button type="submit" class="lb-btn">שמירה</button>
          <button type="button" class="lb-btn ok" id="mbx-complete">שמירה וסימון ״הושלם״</button>
          <span class="lb-spacer"></span>
          <button type="button" class="lb-btn secondary" id="mbx-follow">ניסוי המשך</button>
        </div>
      </form>
    </div>
  </div>
  <datalist id="mbx-formats"><option value="ריל"><option value="קרוסלה"><option value="סטורי"><option value="פוסט"><option value="מודעה"></datalist>
  <datalist id="mbx-channels"><option value="אינסטגרם"><option value="פייסבוק"><option value="טיקטוק"><option value="וואטסאפ"></datalist>
</dialog>"""


HOOK_LISTS = (("on_screen", "על המסך"), ("spoken", "מה נאמר"), ("caption", "כיתוב"))
MONTHS = {m: i for i, m in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}


def ddmmyyyy(s):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})$", s or "")
    if m:
        return f"{m.group(3)} / {m.group(2)} / {m.group(1)}"
    m = re.match(r"([A-Z][a-z]{2}) (\d{1,2}), (\d{4})$", s or "")
    if m:
        return f"{int(m.group(2)):02d} / {MONTHS[m.group(1)]:02d} / {m.group(3)}"
    return s or ""


def hooks_html():
    """The 50 best performing on-screen, spoken and caption hooks of MeBook's Reels (15 Nov 2026), from
    research/mebook-hooks/hooks.json. Hooks are quotes: copied as written, translate="no", never corrected here."""
    if not os.path.exists(HOOKS):
        return '<p class="lb-empty">אין עדיין נתונים: <code class="lb-ltr">research/mebook-hooks/hooks.json</code> חסר.</p>'
    with open(HOOKS, encoding="utf-8") as f:
        h = json.load(f)
    for i in h["items"]:
        for f in ("on_screen", "spoken", "caption"):
            if i.get(f):
                i[f] = DASHES.sub("-", i[f])
    items = {i["key"]: i for i in h["items"]}
    reels = [i for i in h["items"] if i["kind"] == "reel"]
    ads = [i for i in h["items"] if i["kind"] == "ad"]
    views = sorted(i["views"] for i in reels)
    mid = len(views) // 2
    median = views[mid] if len(views) % 2 else (views[mid - 1] + views[mid]) / 2
    by_creator = sum(1 for i in reels if i["account"] != "@mebook.ai")
    top = max(reels, key=lambda i: i["views"])

    def metric(label, value, small=""):
        extra = f'<small class="lb-ltr">{esc(small)}</small>' if small else ""
        return (f'<div class="lb-metric"><p class="lb-metric-label">{esc(label)}</p>'
                f'<p class="lb-metric-value"><span class="lb-ltr">{value}</span>{extra}</p></div>')

    cubes = (metric("רילס שנבדקו", len(reels)) + metric("חציון צפיות", f"{median:,.0f}") +
             metric("עלו אצל יוצרים", f"{by_creator} / {len(reels)}") + metric("הריל המוביל", f'{top["views"]:,}', top["account"]))

    def row(n, it, f):
        tags = ""
        if f == "on_screen" and it.get("on_screen_kind") == "subtitles":
            tags += '<span class="lb-chip outline" title="הטקסט על המסך הוא המשפט שנאמר">כתוביות</span>'
        if f == "spoken" and it.get("spoken_basis") in ("auto", "auto+edit"):
            tags += '<span class="lb-chip warning" title="מתמלול מקומי, לא אומת מול כתוביות">תמלול</span>'
        tagbox = f'<div class="mbh-tags">{tags}</div>' if tags else ""
        return (f'<li class="mbh-row"><span class="lb-disc sm quiet">{n}</span>'
                f'<div class="mbh-main"><p class="mbh-text" dir="rtl" translate="no">{esc(it[f])}</p>{tagbox}</div>'
                f'<div class="mbh-meta"><span class="mbh-views"><b class="lb-ltr">{it["views"]:,}</b> צפיות</span>'
                f'<span class="mbh-who"><span class="lb-ltr">{esc(it["account"])}</span> · <span class="lb-ltr">{ddmmyyyy(it["date"])}</span></span>'
                f'<a class="mbh-open" href="{esc(it["url"])}" target="_blank" rel="noopener" aria-label="פתיחת הריל באינסטגרם">{design.icon("open-out")}<span>פתיחה</span></a></div></li>')

    lists, seg = [], []
    for k, (f, label) in enumerate(HOOK_LISTS):
        keys = h["top"][f]
        hid = "" if k == 0 else " hidden"
        lists.append(f'<ol class="lb-rowlist mbh-list" data-hlist="{f}"{hid}>' +
                     "".join(row(n, items[key], f) for n, key in enumerate(keys, 1)) + "</ol>")
        pressed = "true" if k == 0 else "false"
        seg.append(f'<button type="button" data-hl="{f}" aria-pressed="{pressed}">{label} · {len(keys)}</button>')

    def cell(t):
        return f'<span dir="rtl" translate="no">{esc(t)}</span>' if t else '<span class="lb-dim">אין</span>'
    ad_rows = "".join(
        f'<tr><td class="lb-ltr">{a["ad_rank"]}</td><td>{cell(a["on_screen"])}</td><td>{cell(a["spoken"])}</td><td>{cell(a["caption"])}</td>'
        f'<td><span class="lb-ltr">{ddmmyyyy(a["date"])}</span></td><td><a href="{esc(a["url"])}" target="_blank" rel="noopener">מודעה</a></td></tr>' for a in ads)
    subs = sum(1 for k in h["top"]["on_screen"] if items[k].get("on_screen_kind") == "subtitles")
    checked = sum(1 for k in h["top"]["spoken"] if items[k].get("spoken_basis") == "subtitles")
    return (
        f'<div class="lb-metrics mbh-cubes">{cubes}</div>'
        f'<div class="lb-callout info" style="margin-top:var(--sp-4)"><b>איך לקרוא</b><span>'
        f'הדירוג לפי הצפיות שאינסטגרם מציג בלשונית הרילס של <span class="lb-ltr">@mebook.ai</span> ב <span class="lb-ltr">15 / 11 / 2026</span>. '
        f'{by_creator} מתוך {len(reels)} הרילס עלו אצל יוצרות ויוצרים, אז מספר גבוה מעיד גם על הקהל שלהם ולא רק על ההוק. '
        f'<b>על המסך</b>: הטקסט ב 3 השניות הראשונות; {subs} מתוך 50 הם כתוביות של המשפט שנאמר. '
        f'<b>מה נאמר</b>: המשפט הראשון, מתמלול מקומי שתוקן מול הכתוביות של הריל ב {checked} מתוך 50; השאר מסומנים ״תמלול״. '
        f'<b>כיתוב</b>: השורה הראשונה של הכיתוב. הכול כפי שנכתב ונאמר, בלי תיקון; [?] היא מילה שלא ברורה.</span></div>'
        f'<div class="mb-filterrow"><span class="lb-dim">רשימה</span><div class="lb-segmented" role="group" aria-label="סוג ההוק">{"".join(seg)}</div>'
        f'<span class="mb-count" id="mbh-count"></span></div>'
        f'{"".join(lists)}<p class="lb-empty" id="mbh-empty" hidden>אין הוק שמתאים לחיפוש.</p>'
        f'<details class="lb-disclosure" style="margin-top:var(--sp-4)"><summary><span class="lb-sum">{len(ads)} מודעות הווידאו של מיבוק'
        f'<small>מספריית המודעות של Meta, בלי מספרים ציבוריים</small></span></summary><div class="lb-disclosure-body">'
        f'<div class="lb-table-wrap"><table class="lb-table mb-table"><thead><tr><th>#</th><th>על המסך</th><th>מה נאמר</th><th>טקסט המודעה</th><th>עלתה</th><th></th></tr></thead>'
        f'<tbody>{ad_rows}</tbody></table></div><p class="lb-note">אותו סרטון רץ לפעמים עם כמה טקסטים. הסדר הוא המיון של ספריית המודעות לפי חשיפות, בלי מספרים.</p></div></details>'
        )


HOOKS_JS = r"""<script>
(function () {
  function $$(s) { return Array.prototype.slice.call(document.querySelectorAll(s)); }
  var lists = $$('[data-hlist]'), btns = $$('[data-hl]'), count = document.getElementById('mbh-count'),
      empty = document.getElementById('mbh-empty'), q = document.getElementById('mb-q'), cur = btns.length ? btns[0].dataset.hl : '';
  if (!lists.length) return;
  function norm(t) { return (t || '').toLowerCase().replace(/[֑-ׇ]/g, ''); }
  $$('.mbh-row').forEach(function (r) { r._t = norm(r.textContent); });
  function apply() {
    var terms = norm(q ? q.value : '').split(/\s+/).filter(Boolean), n = 0, total = 0;
    lists.forEach(function (l) {
      var on = l.dataset.hlist === cur; l.hidden = !on;
      if (!on) return;
      Array.prototype.forEach.call(l.children, function (r) {
        var ok = terms.every(function (t) { return r._t.indexOf(t) >= 0; });
        r.hidden = !ok; total++; if (ok) n++;
      });
    });
    if (count) count.textContent = n === total ? total + ' הוקים' : n + ' מתוך ' + total;
    if (empty) empty.hidden = n > 0;
  }
  btns.forEach(function (b) { b.addEventListener('click', function () {
    cur = b.dataset.hl; btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); apply();
  }); });
  if (q) q.addEventListener('input', apply);
  apply();
})();
</script>"""


def build():
    with open(SRC, encoding="utf-8") as f:
        d = json.load(f)
    it = parse_intents()
    errs = validate(d) + validate_intents(it)
    if errs:
        print("\n".join(errs))
        sys.exit(1)

    ev = {e["n"]: e for e in d["evidence"]}
    sections = [  # id, nav label, icon, heading, sub
        ("sources", "מקורות ומגבלות", "search", "מקורות ומגבלות", "מה נקרא, ומה לא הצלחתי לקרוא."),
        ("summary", "סיכום המחקר", "sparkle", "סיכום המחקר", "הממצאים החזקים ביותר, ומה עדיין לא ידוע."),
        ("evidence", "טבלת הראיות", "file", "טבלת הראיות", f"{len(d['evidence'])} אמירות במילים של הלקוחות, כל מה שבמדגם. אפשר לסנן לפי נושא, סוג ומי הקונה, ולחפש."),
        ("patterns", "דפוסים", "chart", "דפוסים עיקריים", "כמה אמירות תומכות בכל ממצא, כמה חזק, ומה מגביל אותו."),
        ("language", "בנק שפה", "chat", "בנק שפת הלקוחות", "ביטויים אמיתיים מהלקוחות."),
        ("hypotheses", "שש השערות", "sparkle", "שש השערות תוכן ללומיבוק", "כל השערה עם הראיות, הוק, הצילום הנדרש, דרך לבדוק, והנחה שעוד צריך לאמת."),
        ("intents", "100 כוונות קנייה", "chart", "100 כוונות קנייה", "למה מישהו מחליט לקנות ספר אישי במצב מסוים. לכל כוונה: תווית ראיה, מקור, ההיסוס, ומה לומיבוק צריכה להראות. ו 10 לבדוק קודם."),
        ("hooks", "50 ההוקים", "chat", "50 ההוקים הכי חזקים של מיבוק", "מה כתוב על המסך, מה נאמר ראשון ומה השורה הראשונה בכיתוב, ברילס של מיבוק לפי מספר הצפיות."),
        ("log", "יומן ניסויים", "chart", "יומן ניסויים", "ניסוי תוכן לכל רעיון מהמחקר: השערה, מה הראינו, תוצאות שמזינים ידנית, ומה למדנו. נשמר בשרת הפרויקט."),
    ]
    # icons: fall back to a known icon if a name is missing
    known = set(design.icons("icons")) | set(design.icons("ui"))

    def ic(name, fallback="file"):
        return design.icon(name if name in known else fallback)

    nav = ['<div class="lb-nav-label">חלקים</div>']
    for sid, label, icon, *_ in sections:
        nav.append(f'<a class="lb-nav-item" href="#{sid}"><span class="lb-tile lb-cat-0">{ic(icon)}</span><span class="lb-nav-text">{esc(label)}</span></a>')

    # cubes (also the theme filters)
    cubes = []
    for m in d["metrics"]:
        t = d["themes"][m["theme"]]
        cubes.append(f'<button type="button" class="lb-metric {cat(m["theme"])}" data-theme="{m["theme"]}" aria-pressed="false">'
                     f'<span class="lb-metric-label">{esc(t["label"])}</span>'
                     f'<span class="lb-metric-value"><b>{esc(m["n"])}</b> <small>{esc(m["unit"])}</small></span>'
                     f'<span class="lb-metric-foot">{inline(m["foot"])}</span></button>')

    def head(sid):
        s = next(x for x in sections if x[0] == sid)
        return f'<div class="mb-section-head"><div><h2>{esc(s[3])}</h2><p>{esc(s[4])}</p></div></div>'

    # sources
    def src_cell(x):
        if x.get("url"):
            return link(x["url"], "פתיחה")
        return f'<code class="lb-ltr">{esc(x.get("path", ""))}</code>' if x.get("path") else ""

    src_rows = "".join(
        f'<tr><td data-label="מקור"><b>{esc(s["name"])}</b></td><td data-label="מה זה">{inline(s["what"])}</td><td data-label="כמה נקרא">{esc(s["read"])}</td><td data-label="הטיה שצריך לזכור">{inline(s["bias"])}</td>'
        f'<td class="mb-links">{src_cell(s)}</td></tr>'
        for s in d["sources"])
    not_read = "".join(f"<li>{inline(x)}</li>" for x in d["not_read"])

    # summary
    summ = "".join(
        f'<article class="lb-card {cat(s["theme"])}"><h3><span class="lb-tile {cat(s["theme"])}">{ic("sparkle")}</span>{esc(s["title"])}</h3><p>{inline(s["text"])}</p>{xbox("finding:" + s["id"])}</article>'
        for s in d["summary"])
    unknowns = "".join(f"<li>{inline(x)}</li>" for x in d["unknowns"])

    # evidence table
    rows = []
    for e in d["evidence"]:
        kcls, klabel = KIND[e["kind"]]
        chips = "".join(theme_chip(d, t) for t in e["themes"])
        when = "".join(f'<span class="mb-when"><bdi>{inline(p)}</bdi></span>' for p in e["date"].split(", "))
        rows.append(
            f'<article class="lb-card mb-q" id="e-{e["n"]}" data-themes="{" ".join(e["themes"])}" data-kind="{e["kind"]}" data-buyer="{e["buyer"]}">'
            f'<div class="mb-q-head"><span class="mb-qn">#{e["n"]}</span><span class="lb-chip {kcls}">{klabel}</span>{chips}'
            f'<a class="lb-btn secondary sm mb-src" href="{esc(e["url"])}" target="_blank" rel="noopener">{design.icon("open-out")}<span>מקור</span></a></div>'
            f'<blockquote class="mb-quote" dir="rtl" lang="he" translate="no">״{esc(e["quote"])}״</blockquote>'
            f'<div class="mb-q-meta"><span class="lb-chip outline">{esc(d["src_labels"][e["src"]])}</span>{when}'
            f'<span class="mb-sep">·</span><span>{esc(e["context"])}</span></div>'
            f'<p class="mb-q-note">{esc(e["note"])}</p></article>')
    kinds = ('<div class="lb-filters" role="group" aria-label="סוג">'
             '<button type="button" data-kind="" aria-pressed="true">הכול</button>'
             '<button type="button" data-kind="motivation" aria-pressed="false">מניע</button>'
             '<button type="button" data-kind="objection" aria-pressed="false">התנגדות</button>'
             '<button type="button" data-kind="both" aria-pressed="false">גם וגם</button></div>')
    buyers = ('<div class="lb-filters" role="group" aria-label="מי הקונה"><button type="button" data-buyer="" aria-pressed="true">כל הקונים</button>' +
              "".join(f'<button type="button" data-buyer="{k}" aria-pressed="false">{esc(v)}</button>' for k, v in d["buyer_labels"].items() if k not in ("unknown",)) + "</div>")

    # patterns
    prow = []
    for p in d["patterns"]:
        chip = theme_chip(d, p["theme"]) if p["theme"] else ""
        prow.append(f'<tr><td data-label="ממצא"><b>{inline(p["finding"])}</b><div class="mb-chips" style="margin-top:.35rem">{chip}</div></td>'
                    f'<td class="lb-num mb-ncell" data-label="אמירות"><b>{p["n"]}</b><div class="meta">{inline(p["breakdown"])}</div></td>'
                    f'<td data-label="עוצמה"><span class="lb-chip {STRENGTH[p["strength"]]}"><i class="lb-dot"></i>{esc(d["strength_labels"][p["strength"]])}</span></td>'
                    f'<td data-label="מגבלות או סתירות">{inline(p["limits"])}{xbox("finding:" + p["id"])}</td></tr>')

    # language bank
    lang = []
    for g in d["language"]:
        li = "".join(
            f'<li><span class="t" dir="rtl" lang="he">״{esc(i["t"])}״</span>' +
            (f'<a class="ref" href="#e-{i["ref"]}" data-ref="{i["ref"]}">#{i["ref"]}</a>' if i["ref"] is not None else '<span></span>') + "</li>"
            for i in g["items"])
        lang.append(f'<article class="lb-card"><h3>{esc(g["title"])}</h3><ul>{li}</ul></article>')

    # hypotheses
    hyps = []
    for h in d["hypotheses"]:
        refs = "".join(f'<a class="lb-chip" href="#e-{r}" data-ref="{r}">#{r}</a>' for r in h["refs"])
        first = f'<span class="lb-chip success">בדיקה ראשונה מספר {h["first"]}</span>' if h["first"] else ""
        hook_alt = f'<p class="lb-dim lb-xs">{esc(h["hook_alt"])}</p>' if h.get("hook_alt") else ""
        hyps.append(f"""<article class="lb-card mb-hyp" id="{h['id']}">
  <div class="mb-hyp-head"><span class="lb-chip outline mb-hid">{h['id']}</span><h3>{esc(h['title'])}</h3>{first}<span class="lb-chip {STRENGTH[h['strength']]}"><i class="lb-dot"></i>ראיות {esc(d['strength_labels'][h['strength']])}</span></div>
  <p class="mb-statement">{inline(h['statement'])}</p>
  <div class="mb-refs"><span class="lb-dim lb-xs">הראיות:</span>{refs}<span class="lb-dim lb-xs">{esc(h['evidence_note'])}</span></div>
  <div class="mb-hyp-grid">
    <div class="lb-sheet"><h4 class="lb-eyebrow">הוק מוצע</h4><p class="mb-hook">״{esc(h['hook'])}״</p>{hook_alt}</div>
    <div class="lb-sheet"><h4 class="lb-eyebrow">הצילום וההוכחה שצריך לאסוף</h4><p>{inline(h['footage'])}</p></div>
    <div class="lb-sheet"><h4 class="lb-eyebrow">איך בודקים</h4><p>{inline(h['test'])}</p></div>
    <div class="lb-sheet"><h4 class="lb-eyebrow">ההנחה שעוד צריך לאמת מול לקוחות לומיבוק</h4><p>{inline(h['assumption'])}</p></div>
  </div>
  {xbox("hyp:" + h["id"])}
</article>""")
    risks = "".join(f'<div class="lb-callout warning"><b>{esc(r["title"])}</b><span>{inline(r["text"])}' +
                    (f' {link(r["url"], "המקור")}' if r.get("url") else (f' <a href="#e-{r["ref"]}" data-ref="{r["ref"]}">#{r["ref"]}</a>' if r.get("ref") else "")) + "</span></div>"
                    for r in d["risks"])

    # (identity, brand claims, our suggested phrases, the three first experiments, the five questions and the method stay in
    # data.json and report.md; Yarin took them off the page with the edit button on 15 Nov 2026)

    # purchase intents
    qnums = set(ev)
    tips = source_tips()
    top_ns = {t["n"]: i for i, t in enumerate(it["top"], 1)}
    lab_count = {k: sum(1 for x in it["intents"] if x["label"] == k) for k in ILABELS}
    ireels = load_intent_reels([x["n"] for x in it["intents"]])
    n_with = sum(1 for v in ireels.values() if v)

    def reel_row(n):
        rs = ireels[n]
        if not rs:
            return '<div class="mb-reels"><span class="lb-eyebrow">רילס של מיבוק</span><span class="lb-dim">אין רילס במחקר שמתאימים</span></div>'
        return (f'<details class="mb-reels"><summary><span class="lb-eyebrow">רילס של מיבוק · {len(rs)}</span></summary>'
                f'<div class="mb-chips">{"".join(reel_chip(r) for r in rs)}</div></details>')
    icards = []
    for x in it["intents"]:
        key, cls, word = ILABELS[x["label"]]
        chips = f'<span class="lb-chip {cls}"><i class="lb-dot"></i>{word}</span><span class="lb-chip outline">{esc(cat_label(x["cat_name"]))}</span>'
        if x["n"] in top_ns:
            chips += f'<span class="lb-chip success">לבדוק קודם, מספר {top_ns[x["n"]]}</span>'
        if x["flag"]:
            chips += '<span class="lb-chip warning" title="תלוי ביכולת של לומיבוק שלא אומתה באתר החי">⚑ לאמת בלומיבוק</span>'
        icards.append(
            f'<article class="lb-card mb-int" id="i-{x["n"]}" data-label="{key}" data-cat="{x["cat"]}" data-reels="{1 if ireels[x["n"]] else 0}">'
            f'<div class="mb-q-head"><span class="mb-qn">#{x["n"]}</span>{chips}</div>'
            f'<p class="mb-int-text" dir="rtl">{inline(x["intent"])}</p>'
            f'<dl class="lb-kv"><dt>מי ומתי</dt><dd>{inline(x["buyer"])}</dd><dt>מה מעכב</dt><dd>{codes(x["hes"], qnums, tips)}</dd>'
            f'<dt>מקור</dt><dd>{codes(x["src"], qnums, tips)}</dd><dt>מה להראות</dt><dd>{codes(x["show"], qnums, tips)}</dd></dl>'
            f'{reel_row(x["n"])}{xbox("intent:" + str(x["n"]))}</article>')
    ilabel_btns = (f'<div class="lb-filters" role="group" aria-label="תווית ראיה"><button type="button" data-ilabel="" aria-pressed="true">הכול · {len(it["intents"])}</button>' +
                   "".join(f'<button type="button" data-ilabel="{ILABELS[k][0]}" aria-pressed="false">{ILABELS[k][2]} · {lab_count[k]}</button>' for k in ILABELS) + "</div>")
    icat_btns = ('<div class="lb-filters" role="group" aria-label="קטגוריה"><button type="button" data-icat="" aria-pressed="true">כל הקטגוריות</button>' +
                 "".join(f'<button type="button" data-icat="{i}" aria-pressed="false">{esc(cat_label(c))}</button>' for i, c in enumerate(it["cats"], 1)) + "</div>")
    ireel_btns = ('<div class="lb-filters" role="group" aria-label="רילס של מיבוק"><button type="button" data-ireel="" aria-pressed="true">הכול</button>'
                  f'<button type="button" data-ireel="1" aria-pressed="false">יש רילס של מיבוק · {n_with}</button>'
                  f'<button type="button" data-ireel="0" aria-pressed="false">אין רילס שמתאימים · {len(ireels) - n_with}</button></div>')
    intent_by_n = {x["n"]: x for x in it["intents"]}
    top_cards = "".join(
        f'<article class="lb-card"><span class="lb-disc lb-cat-0">{i}</span><div>'
        f'<b class="t"><a href="#i-{t["n"]}" data-int="{t["n"]}">#{t["n"]}</a> {inline(intent_by_n[t["n"]]["intent"])}</b>'
        f'<p>{inline(t["why"])}</p><div class="lb-sheet"><span class="lb-eyebrow">השערת מכירה</span><p>{codes(it["hyps"][t["n"]], qnums, tips)}</p></div>'
        f'{reel_row(t["n"])}</div></article>'
        for i, t in enumerate(it["top"], 1))
    limits = "".join(f"<li>{inline(x)}</li>" for x in it["limits"])
    intents_html = (
        f'<div class="lb-callout info"><b>איך לקרוא</b><span>כוונת קנייה היא הסיבה הספציפית שבגללה מישהו מחליט לקנות ספר אישי במצב מסוים. '
        f'<b>ראיה ישירה</b>: לקוח או מתעניין אמר את זה במפורש. <b>הסקה</b>: נגזרת מאמירות ספציפיות. <b>השערה</b>: סבירה אבל לא מבוססת במחקר. '
        f'כיתוב ממומן של יוצרת או טענה של מיבוק לא נחשבים ראיה ישירה. עמודת "מה מעכב" היא ההערכה שלנו, אלא אם יש בה מקור. '
        f'⚑ מסמן תלות ביכולת של לומיבוק שלא אומתה באתר החי. קוד מקור (G, S, L) מראה את הטקסט המקורי במעבר עכבר, ו Q קופץ לציטוט.</span></div>'
        f'<details class="lb-disclosure" style="margin-top:var(--sp-3)"><summary><span class="lb-sum">המגבלות של הכיסוי<small>{len(it["limits"])} נקודות</small></span></summary>'
        f'<div class="lb-disclosure-body"><ul>{limits}</ul></div></details>'
        f'<h3 style="margin-top:var(--sp-5)">10 הכוונות לבדוק קודם, עם השערת מכירה</h3>'
        f'<div class="mb-top10">{top_cards}</div>'
        f'<h3 style="margin-top:var(--sp-5)">כל 100 הכוונות</h3>'
        f'<div class="mb-filterrow"><span class="lb-dim">תווית</span>{ilabel_btns}<span class="mb-count" id="mb-icount"></span>'
        f'<button class="lb-btn ghost sm" id="mb-iclear" type="button" hidden>{design.icon("close")}<span>ניקוי הסינון</span></button></div>'
        f'<div class="mb-filterrow"><span class="lb-dim">קטגוריה</span>{icat_btns}</div>'
        f'<div class="mb-filterrow"><span class="lb-dim">רילס של מיבוק</span>{ireel_btns}</div>'
        f'<div class="mb-ints" id="mb-intents">{"".join(icards)}</div>'
        f'<p class="lb-empty" id="mb-iempty" hidden>אין כוונה שמתאימה. אפשר לנסות מילה אחרת או לנקות את הסינון.</p>'
        f'<p class="lb-note" style="margin-top:var(--sp-3)">המקור: <code class="lb-ltr">purchase-intents.md</code>, והמקורות הממוספרים ב <code class="lb-ltr">sources/</code>.</p>')

    def sec(sid, body):
        return f'<section class="lb-section" id="{sid}">{head(sid)}{body}</section>'

    body = "".join([
        sec("sources", f'<div class="lb-table-wrap"><table class="lb-table mb-table"><thead><tr><th>מקור</th><th>מה זה</th><th>כמה נקרא</th><th>הטיה שצריך לזכור</th><th></th></tr></thead><tbody>{src_rows}</tbody></table></div>'
            f'<div class="lb-callout warning" style="margin-top:var(--sp-3)"><b>לא נקרא</b><span><ul>{not_read}</ul></span></div>'
            f'<p class="lb-note" style="margin-top:var(--sp-3)">{inline(d["sample_note"])}</p>'),
        sec("summary", f'<div class="mb-sum">{summ}</div><div class="lb-callout info" style="margin-top:var(--sp-4)"><b>מה עדיין לא ידוע</b><span><ul>{unknowns}</ul></span></div>'),
        sec("evidence", f'<div class="lb-metrics mb-cubes" aria-label="סינון לפי נושא">{"".join(cubes)}</div><div class="mb-filterrow"><span class="lb-dim">סוג</span>{kinds}<span class="lb-dim">קונה</span>{buyers}'
            f'<button class="lb-btn ghost sm" id="mb-clear" type="button" hidden>{design.icon("close")}<span>ניקוי הסינון</span></button></div>'
            f'<div class="mb-quotes" id="mb-evidence">{"".join(rows)}</div>'
            f'<p class="lb-empty" id="mb-empty" hidden>אין אמירה שמתאימה. אפשר לנסות מילה אחרת או לנקות את הסינון.</p>'
            ),
        sec("patterns", f'<div class="lb-table-wrap"><table class="lb-table mb-table"><thead><tr><th>ממצא</th><th>אמירות</th><th>עוצמה</th><th>מגבלות או סתירות</th></tr></thead><tbody>{"".join(prow)}</tbody></table></div>'
            ),
        sec("language", f'<div class="mb-lang">{"".join(lang)}</div>'),
        sec("hypotheses", f'<div class="mb-hyps">{"".join(hyps)}</div>'
            f'<h3 style="margin-top:var(--sp-5)">שני סיכונים שהמחקר מעלה ללומיבוק</h3><div class="lb-stack" style="display:grid;gap:var(--sp-3)">{risks}</div>'),
        sec("intents", intents_html),
        sec("hooks", hooks_html()),
        sec("log", log_html()),
    ])

    page = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>מה לקוחות מיבוק אומרים · לומיבוק</title>
{design.head(page=PAGE)}
<style>{CSS}</style>
</head>
<body>
<div class="lb-app">
  <aside class="lb-sidebar" aria-label="חלקי המחקר">
    <a class="lb-brand" href="#top"><span><b>Mebook: מחקר</b></span></a>
    <nav class="lb-nav">{"".join(nav)}</nav>
  </aside>
  <div class="lb-scrim" hidden></div>
  <main class="lb-main" id="top">
    <div class="lb-topbar lb-edge"><div class="lb-topbar-in mb-top">
      <button class="lb-btn secondary icon lb-menu-btn" id="mb-menu" type="button" aria-label="פתיחת החלקים">{design.icon("menu")}</button>
      <label class="lb-search">{design.icon("search")}<span class="lb-sr">חיפוש באמירות</span><input class="lb-input" id="mb-q" type="search" dir="rtl" placeholder="חיפוש באמירות ובכוונות" autocomplete="off"><span class="lb-kbd" aria-hidden="true">/</span></label>
      <span class="mb-count" id="mb-count"></span>
    </div></div>
    <div class="lb-page">
      <header class="lb-hero mb-hero">
        <h1>Mebook: מחקר</h1>
      </header>
      {body}
    </div>
  </main>
</div>
{exp_dialog()}
{JS}
<script>window.MB_SRC = {json.dumps(mb_src(d, it), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")};</script>
<script>{exp_scripts()}</script>
{HOOKS_JS}
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(d['evidence'])} quotes, {len(d['hypotheses'])} hypotheses, {len(page):,} bytes")


if __name__ == "__main__":
    build()
