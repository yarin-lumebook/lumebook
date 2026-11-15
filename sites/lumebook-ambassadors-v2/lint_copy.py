#!/usr/bin/env python3
"""Copy and page lint for the redesigned ambassador page.

Run:  python3 sites/lumebook-ambassadors-v2/lint_copy.py      (after src/build.py)
Exit code 1 if anything fails. Standard library only.

Checks every visitor string in src/content/he.json and the built index.html:
- house rules: no em or en dash; audience Hebrew has no hyphen, maqaf or semicolon (24 Oct 2026 rule); no space before punctuation;
  brand LumeBook / לומבוק, never לומיבוק; no AI wording; never "קוד הנחה" or "קוד אישי" (shared/facts.json offer)
- this page's clarity rules: no unexplained jargon (UGC, אפיליאייט, המרות, Collaborator), no "חינם" and no "מתנה" (the book is payment for
  content and may count as income, terms 7.4 and 8.1), no income projections, no guarantee words, no shekel amount or percentage typed
  into the copy except ₪0 (numbers come from shared/facts.json and the live program API)
- the reward is 25% of the book price, never ₪30 (Yarin, 15 Nov 2026: "זה 25% לא 30 שקלים"): no {budget} or {step} token in the copy,
  and no ₪30 anywhere on the built page
- the built page: Hebrew RTL, one h1, canonical to the store route, the form posts the same fields as the store's signup,
  the form is in mock mode, the terms version matches shared/facts.json
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
COPY = json.load(open(os.path.join(HERE, "src", "content", "he.json"), encoding="utf-8"))
FACTS = json.load(open(os.path.join(ROOT, "shared", "facts.json"), encoding="utf-8"))
PAGE = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()

DASH = re.compile("[" + "".join(chr(c) for c in (0x2012, 0x2013, 0x2014, 0x2015, 0x2212)) + "]")
RULES = [
    ("em or en dash", DASH),
    ("hyphen (audience Hebrew)", re.compile(r"-")),
    ("maqaf", re.compile("־")),
    ("semicolon", re.compile("[;;]")),
    ("space before punctuation", re.compile(r"\s[,.!?:](?!\S*\})")),
    ("brand spelled with yod", re.compile("לומיבוק")),
    ("brand in wrong Latin form", re.compile(r"Lumebook|Lume Book|LUMEBOOK")),
    ("AI wording", re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])|בינה מלאכותית")),
    ("banned offer wording", re.compile("|".join(map(re.escape, FACTS["offer"]["banned_wording_he"])))),
    ("jargon", re.compile(r"UGC|אפיליאייט|אפילייט|המרות|Collaborator|קולבורייטור")),
    ("'free' or 'gift' wording", re.compile(r"חינם|(?<!ה)מתנה|מתנות")),  # המתנה (waiting) is fine
    ("typed percentage (use a {token})", re.compile(r"\d\s*%")),
    ("reward written in shekels (it is 25%, Yarin 15 Nov 2026)", re.compile(r"\{budget\}|\{step\}")),
    ("guarantee wording", re.compile(r"מובטח|מבטיחים|מבטיחה לכם|בטוח תרוויחו|הכנסה קבועה|פסיבית")),
    ("typed shekel amount (use a {token})", re.compile(r"₪\s?(?!0(?![\d,]))\d")),
]


def strings(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("_"):
                continue
            yield from strings(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


fails = []
for path, s in strings(COPY):
    for name, rx in RULES:
        if name == "hyphen (audience Hebrew)" and path.endswith(("_ph",)):
            continue
        m = rx.search(s)
        if m:
            fails.append(f"{path}: {name}: …{s[max(0, m.start() - 20):m.end() + 20]}…")

# the built page
if '<html lang="he" dir="rtl">' not in PAGE:
    fails.append("index.html: not lang=he dir=rtl")
if len(re.findall(r"<h1[\s>]", PAGE)) != 1:
    fails.append("index.html: needs exactly one h1")
if f'<link rel="canonical" href="https://lumebook.com{FACTS["ambassador_program"]["routes"]["page"]}">' not in PAGE:
    fails.append("index.html: canonical does not point at the store route")
if 'data-api="mock"' not in PAGE:
    fails.append("index.html: the form must ship in mock mode (live only on lumebook.com, set by the store)")
if FACTS["ambassador_program"]["terms_version"] not in PAGE:
    fails.append("index.html: terms version missing or not the one in shared/facts.json")
for field in ["followersBand", "socialHandle", "fullName", "phone", "email", "discountMinor", "termsAccepted"]:
    if f'name="{field}"' not in PAGE:
        fails.append(f"index.html: store signup field {field} missing from the form")
if DASH.search(re.sub(r"<script.*?</script>", "", PAGE, flags=re.S)):
    fails.append("index.html: em or en dash in the page")
visible = re.sub(r"<script.*?</script>", "", PAGE, flags=re.S)
if re.search(r"₪\s?30(?![\d,])", visible):
    fails.append("index.html: ₪30 on the page (the reward is presented as 25%)")
if "לומיבוק" in PAGE:
    fails.append("index.html: לומיבוק")

if fails:
    print(f"lint_copy: {len(fails)} problem(s)")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("lint_copy: ok (copy and built page)")
