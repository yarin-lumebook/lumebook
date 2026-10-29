#!/usr/bin/env python3
"""Lint loose LumeBook Hebrew copy with the same hard rules as the nightly validator.

    python3 carousel/carousel-pipeline/scripts/voice_lint.py copy.json
    python3 carousel/carousel-pipeline/scripts/voice_lint.py copy.json --cta cta --code-word גן --caption caption --hook hook
    python3 carousel/carousel-pipeline/scripts/voice_lint.py copy.json --cta cta --addressee mom --caption caption   # save for later CTA
    python3 carousel/carousel-pipeline/scripts/voice_lint.py copy.txt

copy.json is a flat object {"field name": "Hebrew text"}. A .txt file is linted as one field.
--cta names the field holding the CTA, --caption the caption field (its last line must equal the CTA),
--hook a field held to the hook limits. Without --code-word the CTA is the save for later CTA of packs from the evening of
24 Oct 2026 (Yarin: "i want the cta to change, 'תשמרו את הפוסט לפעם הבאה שX'"), checked for --addressee (mom or parents).
Punctuation follows the rule of the same evening: everything but dashes, semicolons and hyphens.

--story (or "copy_style": "story" in copy.json) lints story copy (story-format.md, 29 Oct 2026): a slide field carries up to
50 words with the markup not counted (## labels, > cards, **emphasis**) instead of 25, every line at most 38 characters and
12 words, the markup within its limits, and a --hook field is the cover headline (up to 3 lines of 18 characters).
Exit 1 on any error. Nothing is ever edited.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import story_lib  # noqa: E402


def story_field_issues(name, text, hook=False):
    """Story copy limits for one loose field (story-format.md sections 2 and 3)."""
    issues = []
    if hook:
        lines = story_lib.plain_lines(text)
        if len(lines) > story_lib.COVER_HEADLINE_MAX_LINES:
            issues.append(lib.Issue("ERROR", name, f"the cover headline has {len(lines)} lines (max {story_lib.COVER_HEADLINE_MAX_LINES})"))
        for i, line in enumerate(lines, start=1):
            if len(line) > story_lib.COVER_HEADLINE_LINE_MAX_CHARS:
                issues.append(lib.Issue("ERROR", name, f"cover line {i} has {len(line)} characters (max {story_lib.COVER_HEADLINE_LINE_MAX_CHARS})", excerpt=line))
        return issues
    n = story_lib.word_count(text)
    if n > story_lib.SLIDE_MAX_WORDS:
        issues.append(lib.Issue("ERROR", name, f"{n} words (max {story_lib.SLIDE_MAX_WORDS} per story slide, markup not counted)"))
    for i, line in enumerate(story_lib.plain_lines(text), start=1):
        if len(line) > story_lib.BODY_LINE_MAX_CHARS:
            issues.append(lib.Issue("ERROR", name, f"line {i} has {len(line)} characters (max {story_lib.BODY_LINE_MAX_CHARS}); break it by hand", excerpt=line))
        if len(story_lib.words(line)) > story_lib.BODY_LINE_MAX_WORDS:
            issues.append(lib.Issue("ERROR", name, f"line {i} has {len(story_lib.words(line))} words (max {story_lib.BODY_LINE_MAX_WORDS})", excerpt=line))
    for problem in story_lib.markup_problems(text):
        issues.append(lib.Issue("ERROR", name, problem))
    return issues


def lint(fields, cta=None, code_word=None, caption=None, hooks=(), addressee=None, story=False):
    issues = []
    for name, text in fields.items():
        if name == cta:
            issues.extend(lib.cta_issues(name, text, code_word) if code_word else lib.save_later_cta_issues(name, text, addressee))
        else:
            issues.extend(lib.audience_text_issues(name, text, allow_cta=(name == caption)))
        if story and name not in (cta, caption):
            issues.extend(story_field_issues(name, text, hook=name in hooks))
            continue
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
            for pattern, why in lib.SECOND_CTA_PATTERNS + ([] if code_word else lib.COMMENT_CTA_PATTERNS):
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
    ap.add_argument("--addressee", choices=sorted(lib.SAVE_LATER_FORMS), help="who the save for later CTA talks to")
    ap.add_argument("--story", action="store_true", help="story copy (story-format.md): up to 50 words a slide, markup, 38 character lines")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    path = Path(args.file)
    story = args.story
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        story = story or data.pop("copy_style", None) == story_lib.COPY_STYLE
        fields = {k: v for k, v in data.items() if isinstance(v, str)}
    else:
        fields = {path.name: path.read_text(encoding="utf-8")}
    issues = lint(fields, args.cta, args.code_word, args.caption, tuple(args.hook), args.addressee, story=story)
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
