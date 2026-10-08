#!/usr/bin/env python3
"""Lint loose LumeBook Hebrew copy with the same hard rules as the nightly validator.

    python3 carousel/carousel-pipeline/scripts/voice_lint.py copy.json
    python3 carousel/carousel-pipeline/scripts/voice_lint.py copy.json --cta cta --code-word גן --caption caption --hook hook
    python3 carousel/carousel-pipeline/scripts/voice_lint.py copy.txt

copy.json is a flat object {"field name": "Hebrew text"}. A .txt file is linted as one field.
--cta names the field holding the CTA, --caption the caption field (its last line must equal the CTA),
--hook a field held to the hook limits. Exit 1 on any error. Nothing is ever edited.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402


def lint(fields, cta=None, code_word=None, caption=None, hooks=()):
    issues = []
    for name, text in fields.items():
        if name == cta:
            issues.extend(lib.cta_issues(name, text, code_word))
        else:
            issues.extend(lib.audience_text_issues(name, text, allow_cta=(name == caption)))
        if name in hooks:
            first = lib.lines_of(text)[0] if lib.lines_of(text) else ""
            if len(lib.words(first)) > lib.HOOK_MAIN_MAX_WORDS:
                issues.append(lib.Issue("ERROR", name, f"hook main line has {len(lib.words(first))} words (max {lib.HOOK_MAIN_MAX_WORDS})"))
            if len(lib.words(text)) > lib.HOOK_TOTAL_MAX_WORDS:
                issues.append(lib.Issue("ERROR", name, f"hook has {len(lib.words(text))} words (max {lib.HOOK_TOTAL_MAX_WORDS})"))
        elif name not in (cta, caption) and len(lib.words(text)) > lib.SLIDE_MAX_WORDS:
            issues.append(lib.Issue("ERROR", name, f"{len(lib.words(text))} words (max {lib.SLIDE_MAX_WORDS} per slide)"))
    if code_word:
        issues.extend(lib.code_word_issues("code_word", code_word))
    if caption and cta and caption in fields and cta in fields:
        cap = lib.lines_of(fields[caption])
        if not cap or lib.collapse(cap[-1]) != lib.collapse(fields[cta]):
            issues.append(lib.Issue("ERROR", caption, "the caption's final line must be exactly the CTA"))
        for i, line in enumerate(cap[:-1], start=1):
            for pattern, why in lib.SECOND_CTA_PATTERNS:
                if re.search(pattern, line):
                    issues.append(lib.Issue("ERROR", caption, f"line {i} adds a second CTA ({why})"))
    return issues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--cta")
    ap.add_argument("--code-word")
    ap.add_argument("--caption")
    ap.add_argument("--hook", action="append", default=[])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    path = Path(args.file)
    if path.suffix == ".json":
        fields = {k: v for k, v in json.loads(path.read_text(encoding="utf-8")).items() if isinstance(v, str)}
    else:
        fields = {path.name: path.read_text(encoding="utf-8")}
    issues = lint(fields, args.cta, args.code_word, args.caption, tuple(args.hook))
    errors = [i for i in issues if i.level == "ERROR"]
    if args.json:
        print(json.dumps({"valid": not errors, "issues": [i.as_dict() for i in issues]}, ensure_ascii=False, indent=2))
    else:
        for i in issues:
            print(f"- {i}")
        print("PASS" if not errors else f"FAIL {len(errors)} errors")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
