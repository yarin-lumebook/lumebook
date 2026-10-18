#!/usr/bin/env python3
"""Validate a nightly carousel pack before anyone sees it.

    python3 carousel/carousel-pipeline/scripts/validate_pack.py PATH/pack.json
    python3 carousel/carousel-pipeline/scripts/validate_pack.py PATH/pack.json --json
    python3 carousel/carousel-pipeline/scripts/validate_pack.py PATH/pack.json --no-history

Exit code 0 = valid (warnings may still be printed), 1 = invalid.
Every punctuation failure names the exact field, line, column and character.
Nothing is ever removed or rewritten here: fix the line by rewriting it, then validate again.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402


# ---------------------------------------------------------------------------
# A small JSON Schema subset (type, required, enum, const, pattern, min/max,
# additionalProperties false, $ref) so pack.schema.json stays the single
# source of the structure without needing the jsonschema package.
# ---------------------------------------------------------------------------

TYPES = {
    "object": dict, "array": list, "string": str, "integer": int, "boolean": bool, "number": (int, float),
}


def schema_issues(value, schema, root, path="pack"):
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return schema_issues(value, root["$defs"][ref], root, path)
    issues = []
    expected = schema.get("type")
    if expected:
        py = TYPES[expected]
        if not isinstance(value, py) or (expected == "integer" and isinstance(value, bool)):
            return [lib.Issue("ERROR", path, f"must be {expected}")]
    if "const" in schema and value != schema["const"]:
        issues.append(lib.Issue("ERROR", path, f"must be {schema['const']!r}"))
    if "enum" in schema and value not in schema["enum"]:
        issues.append(lib.Issue("ERROR", path, f"must be one of {', '.join(map(str, schema['enum']))}"))
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            issues.append(lib.Issue("ERROR", path, f"must have at least {schema['minLength']} characters"))
        if "pattern" in schema and not re.search(schema["pattern"], value):
            issues.append(lib.Issue("ERROR", path, f"does not match {schema['pattern']}"))
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            issues.append(lib.Issue("ERROR", path, f"must be at least {schema['minimum']}"))
        if "maximum" in schema and value > schema["maximum"]:
            issues.append(lib.Issue("ERROR", path, f"must be at most {schema['maximum']}"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            issues.append(lib.Issue("ERROR", path, f"needs at least {schema['minItems']} items (has {len(value)})"))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            issues.append(lib.Issue("ERROR", path, f"allows at most {schema['maxItems']} items (has {len(value)})"))
        if "items" in schema:
            for i, item in enumerate(value):
                issues.extend(schema_issues(item, schema["items"], root, f"{path}[{i}]"))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                issues.append(lib.Issue("ERROR", f"{path}/{key}", "is required"))
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    issues.append(lib.Issue("ERROR", f"{path}/{key}", "is not a known field"))
        for key, sub in props.items():
            if key in value:
                issues.extend(schema_issues(value[key], sub, root, f"{path}/{key}"))
    return issues


# ---------------------------------------------------------------------------
# Rules the schema cannot express
# ---------------------------------------------------------------------------

def person_issues(p, v, direction_id, names):
    """Who the carousel is about (a named Israeli girl or boy) and who it talks to (mom or both parents, never dad)."""
    issues = []
    name, gender, addressee = v.get("child_name", ""), v.get("child_gender"), v.get("addressee")
    if gender in names and name not in names[gender]:
        issues.append(lib.Issue("ERROR", f"{p}/child_name", f"{name!r} is not a {gender} name in names.md (add it there if it is a real Israeli name)"))
    slides = v.get("slides") or []
    before_last = "\n".join(s.get("headline", "") + "\n" + s.get("body", "") for s in slides[:lib.last_slide(v) - 1])
    if name and not re.search(rf"(?<![\u05D0-\u05EA])(?:ו|ש|ל|ה|כש)?{re.escape(name)}(?![\u05D0-\u05EA])", before_last):
        issues.append(lib.Issue("ERROR", f"{p}/child_name", f"the carousel is about {name}: use the name at least once before the last slide"))
    every = before_last + "\n" + "\n".join(s.get("headline", "") + "\n" + s.get("body", "") for s in slides[lib.last_slide(v) - 1:]) + "\n" + v.get("caption", "")
    m = lib.DAD_RE.search(lib.PARENT_PAIR_RE.sub(" ", every) if addressee == "parents" else every)
    if m:
        issues.append(lib.Issue("ERROR", f"{p}", f"never talk to dad: «{m.group(0)}». Talk to mom (feminine singular) or both parents (plural)"))
    form = lib.CTA_FORMS.get(addressee)
    cta = lib.collapse(v.get("cta", ""))
    if form:
        if not cta.startswith(form["verb"]) or form["get"] not in cta or form["owner"] not in cta:
            issues.append(lib.Issue("ERROR", f"{p}/cta", f"the CTA must talk to {'mom' if addressee == 'mom' else 'both parents'}: {form['verb']} \"X\" בתגובות {form['get']} קישור ליצירת ספר שבו {'הילד' if gender == 'boy' else 'הילדה'} {form['owner']} {'הוא הגיבור' if gender == 'boy' else 'היא הגיבורה'}"))
        address_re = lib.MOM_ADDRESS_RE if addressee == "mom" else lib.PARENTS_ADDRESS_RE
        other_re = lib.PARENTS_ADDRESS_RE if addressee == "mom" else lib.MOM_ADDRESS_RE
        text = before_last + "\n" + "\n".join(lib.lines_of(v.get("caption", ""))[:-1])
        if not address_re.search(text):
            issues.append(lib.Issue("WARN", f"{p}/addressee", f"no line talks to {'mom' if addressee == 'mom' else 'the parents'} directly"))
        if addressee == "mom" and lib.PARENTS_ADDRESS_RE.search(text):
            issues.append(lib.Issue("WARN", f"{p}/addressee", f"addressee is mom but a line talks to both parents: «{lib.PARENTS_ADDRESS_RE.search(text).group(0)}»"))
    anchor = (v.get("character_anchor") or {}).get("parent", "").lower()
    has_mom = any(w in anchor for w in ("mother", "mom", "mum"))
    has_dad = any(w in anchor for w in ("father", "dad"))
    if addressee == "mom" and (not has_mom or has_dad):
        issues.append(lib.Issue("ERROR", f"{p}/character_anchor/parent", "addressee is mom: the image anchor shows the mother only"))
    if addressee == "parents" and not has_mom:
        issues.append(lib.Issue("ERROR", f"{p}/character_anchor/parent", "addressee is both parents: the image anchor must include the mother"))
    return issues


def version_issues(direction_id, v, pack, product_ids, titles=frozenset(), hook_bank=None, names=None):
    hook_bank = hook_bank if hook_bank is not None else lib.load_hook_bank()
    names = names if names is not None else lib.load_names()
    issues = []
    vid = v.get("id", "?")
    p = f"{direction_id}/{vid}"
    if not str(vid).startswith(f"{direction_id}-"):
        issues.append(lib.Issue("ERROR", f"{p}/id", f"option id must start with {direction_id}-"))

    code_word = v.get("code_word", "")
    issues.extend(lib.code_word_issues(f"{p}/code_word", code_word))
    if lib.fixed_code_word_applies(pack) and code_word != lib.CTA_CODE_WORD:
        issues.append(lib.Issue("ERROR", f"{p}/code_word", f"the CTA word is always «{lib.CTA_CODE_WORD}» (Yarin, 10 Oct 2026); got «{code_word}». Write it in the CTA, on the last slide and in the caption's last line"))

    slides = v.get("slides") or []
    numbers = [s.get("number") for s in slides]
    CTA = lib.slide_count(pack)  # the last slide: 7 before 14 Oct 2026, 10 since
    hook_slides = (1,) if CTA == lib.TEN_SLIDE_COUNT else lib.HOOK_SLIDES
    if numbers != list(range(1, CTA + 1)):
        issues.append(lib.Issue("ERROR", f"{p}/slides", f"slides must be numbered 1 to {CTA} in order (got {numbers})"))
    if len(slides) != CTA:
        return issues  # structural error already reported by the schema
    first, last_insight = lib.INSIGHT_SLIDES[0], lib.INSIGHT_SLIDES[-1]
    middle = {s.get("role") for s in slides[first - 1:last_insight]}
    if len(lib.INSIGHT_SLIDES) > 1 and not {"recognition", "reframe"} <= middle:
        issues.append(lib.Issue("ERROR", f"{p}/slides[{first}-{last_insight}]", f"slides {first} to {last_insight} must touch the feeling or problem (recognition) and what is behind it (reframe), at least one of each"))
    issues.extend(person_issues(p, v, direction_id, names))
    issues.extend(lib.hook_issues(p, v, direction_id, hook_bank))
    for s in slides[:CTA - 1]:
        pull = s.get("pull")
        sp = f"{p}/slide-{s.get('number')}/pull"
        if not isinstance(pull, dict) or pull.get("type") not in lib.PULL_TYPES or len(str(pull.get("note", "")).strip()) < 5:
            issues.append(lib.Issue("ERROR", sp, "every slide before the CTA needs a pull: what makes the reader swipe to the next slide (type and note)"))
            continue
        text = s.get("headline", "") + "\n" + s.get("body", "")
        if pull["type"] == "question" and "?" not in text:
            issues.append(lib.Issue("ERROR", sp, "pull type question, but the slide has no question"))
        if pull["type"] == "numbered" and not re.search(r"\d|ראשון|שני|שלישי|אחרון", text):
            issues.append(lib.Issue("ERROR", sp, "pull type numbered, but the slide shows no number or order word"))
    for s in slides[:CTA - 1]:
        m = lib.SALE_PREP_RE.search(s.get("headline", "") + "\n" + s.get("body", ""))
        if m:
            issues.append(lib.Issue("ERROR", f"{p}/slide-{s.get('number')}", f"«{m.group(0)}» prepares a sale; the personalised story and the link belong only on the last slide"))
    last_text = slides[CTA - 1].get("headline", "") + "\n" + slides[CTA - 1].get("body", "")
    if not re.search(r"סיפור", last_text) or not re.search(r"אישי", last_text):
        issues.append(lib.Issue("ERROR", f"{p}/slide-{CTA}", "the last slide must suggest helping the child with a personalised story (say סיפור and אישי) before the CTA"))
    bold = lib.bold_rule_applies(pack)
    numbered = lib.numbered_examples_apply(pack)
    if lib.examples_rule_applies(pack):
        tgt = v.get("examples_target")
        low, high = (lib.NUMBERED_EXAMPLES_MIN, lib.NUMBERED_EXAMPLES_MAX) if numbered else (lib.EXAMPLES_MIN, lib.EXAMPLES_MAX)
        if not isinstance(tgt, int) or not low <= tgt <= high:
            issues.append(lib.Issue("ERROR", f"{p}/examples_target", f"copy this option's number ({low} to {high}) from `examples_per_option` in the start JSON into examples_target"))
    if numbered:
        issues.extend(lib.numbered_example_issues(p, v))
    roles = lib.slide_roles(pack)
    for s in slides:
        n = s.get("number")
        sp = f"{p}/slide-{n}"
        if n in roles and s.get("role") not in roles[n]:
            issues.append(lib.Issue("ERROR", f"{sp}/role", f"slide {n} must be {' or '.join(roles[n])}"))
        headline, body = s.get("headline", ""), s.get("body", "")
        is_cta = n == CTA
        issues.extend(lib.audience_text_issues(f"{sp}/headline", headline, allow_cta=is_cta))
        issues.extend(lib.brand_issues(f"{sp}/headline", headline, titles))
        if body.strip():
            issues.extend(lib.audience_text_issues(f"{sp}/body", body, allow_cta=is_cta))
            issues.extend(lib.brand_issues(f"{sp}/body", body, titles))
        hw = len(lib.words(headline))
        total = hw + len(lib.words(body))
        if n in hook_slides and hw > lib.HOOK_MAIN_MAX_WORDS:
            issues.append(lib.Issue("ERROR", f"{sp}/headline", f"hook main line has {hw} words (max {lib.HOOK_MAIN_MAX_WORDS})"))
        if n == 1 and total > lib.HOOK_TOTAL_MAX_WORDS:
            issues.append(lib.Issue("ERROR", sp, f"hook slide has {total} words (max {lib.HOOK_TOTAL_MAX_WORDS})"))
        elif n == CTA and total > lib.CTA_SLIDE_MAX_WORDS:
            issues.append(lib.Issue("ERROR", sp, f"CTA slide has {total} words (max {lib.CTA_SLIDE_MAX_WORDS})"))
        elif 1 < n < CTA and total > (lib.BOLD_SLIDE_MAX_WORDS if bold else lib.SLIDE_MAX_WORDS):
            issues.append(lib.Issue("ERROR", sp, f"slide has {total} words (max {lib.BOLD_SLIDE_MAX_WORDS if bold else lib.SLIDE_MAX_WORDS})"))
        head_lines = (3 if n == 1 else lib.BOLD_HEADLINE_MAX_LINES) if bold else 3
        if len(lib.lines_of(headline)) > head_lines:
            issues.append(lib.Issue("ERROR", f"{sp}/headline", f"headline is longer than {head_lines} lines"))
        head_chars, body_chars = lib.HEADLINE_LINE_MAX_CHARS, lib.BODY_LINE_MAX_CHARS
        if bold:
            head_chars = lib.COVER_HEADLINE_LINE_MAX_CHARS if n == 1 else lib.BOLD_HEADLINE_LINE_MAX_CHARS
            body_chars = lib.BOLD_BODY_LINE_MAX_CHARS
            if len(lib.lines_of(body)) > lib.BOLD_BODY_MAX_LINES:
                issues.append(lib.Issue("ERROR", f"{sp}/body", f"body has {len(lib.lines_of(body))} lines (max {lib.BOLD_BODY_MAX_LINES}); the type is large, cut to the lines that earn the swipe"))
            issues.extend(lib.highlight_issues(sp, s, last=CTA, required=not numbered))  # the clean look (14 Oct 2026) paints no highlight before the last slide
            if n == 1:
                soft = lib.SOFT_COVER_RE.search(headline + "\n" + body)
                if soft:
                    issues.append(lib.Issue("WARN", f"{sp}/headline", f"soft word on the cover: «{soft.group(0)}»; the cover states the tension flat out"))
        if lib.headline_story_applies(pack):
            issues.extend(lib.headline_story_issues(sp, s))
        if not numbered:
            issues.extend(lib.example_issues(sp, s, v, pack))
        for field, text, limit in (("headline", headline, head_chars), ("body", body, body_chars)):
            for i, line in enumerate(lib.lines_of(text), start=1):
                if len(line) > limit:
                    issues.append(lib.Issue("ERROR", f"{sp}/{field}", f"line {i} has {len(line)} characters and will not fit the slide at a readable size (max {limit}); break it into two lines", excerpt=line))
        if not numbered:
            image = s.get("image") or {}
            if not image:
                issues.append(lib.Issue("ERROR", f"{sp}/image", "every slide needs its image brief"))
            for field in lib.IMAGE_FIELDS:
                val = image.get(field, "")
                if lib.HEBREW_RE.search(str(val)):
                    issues.append(lib.Issue("ERROR", f"{sp}/image/{field}", "image briefs are written in English"))
            if n == 1 and lib.cover_rule_applies(pack):
                issues.extend(lib.cover_image_issues(sp, image))
        elif s.get("image"):
            issues.append(lib.Issue("ERROR", f"{sp}/image", "one picture for the whole carousel (Yarin, 14 Oct 2026): put the brief in the option's `image`, not on a slide"))
        if direction_id == "expert" and n < CTA and lib.AUTHORITY_TITLES.search(headline + " " + body):
            frame = (v.get("expert_frame") or {}).get("type")
            if frame != "named_expert":
                issues.append(lib.Issue("ERROR", sp, "academic title on a slide without a verified named expert (no authority theater)"))

    if numbered:
        image = v.get("image")
        if not isinstance(image, dict):
            issues.append(lib.Issue("ERROR", f"{p}/image", "one picture for the whole carousel (Yarin, 14 Oct 2026): the option needs `image`, the brief of the one picture that depicts the idea"))
        else:
            for field in lib.IMAGE_FIELDS:
                if not str(image.get(field, "")).strip():
                    issues.append(lib.Issue("ERROR", f"{p}/image/{field}", "the picture brief needs this field"))
                elif lib.HEBREW_RE.search(str(image.get(field, ""))):
                    issues.append(lib.Issue("ERROR", f"{p}/image/{field}", "image briefs are written in English"))
            issues.extend(lib.cover_image_issues(f"{p}/image", image))

    headlines = [lib.collapse(s.get("headline", "")) for s in slides]
    if len(set(headlines)) != len(headlines):
        issues.append(lib.Issue("ERROR", f"{p}/slides", "two slides share the same headline; headlines must tell the story on their own"))

    # Kid direction should be the child talking
    if direction_id == "kid":
        first_person = sum(1 for s in slides[:5] if lib.FIRST_PERSON_RE.search(s.get("headline", "") + " " + s.get("body", "")))
        if first_person < 3:
            issues.append(lib.Issue("WARN", f"{p}/slides", f"only {first_person} of slides 1 to 5 sound like the child in first person"))

    # Expert frame
    frame = v.get("expert_frame")
    if direction_id == "expert":
        if not frame:
            issues.append(lib.Issue("ERROR", f"{p}/expert_frame", "expert options need expert_frame (evidence_based_take or named_expert)"))
        elif frame.get("type") == "named_expert":
            src_ids = {s.get("id") for s in v.get("sources", [])}
            if not frame.get("name") or frame.get("source_id") not in src_ids:
                issues.append(lib.Issue("ERROR", f"{p}/expert_frame", "a named expert needs a real name and a source_id from this option's sources"))

    # CTA
    cta = v.get("cta", "")
    issues.extend(lib.cta_issues(f"{p}/cta", cta, code_word))
    last = slides[CTA - 1]
    if lib.collapse(cta) not in lib.collapse(last.get("headline", "") + "\n" + last.get("body", "")):
        issues.append(lib.Issue("ERROR", f"{p}/slide-{CTA}", f"slide {CTA} must contain the exact CTA text"))
    for s in slides[:CTA - 1]:
        if code_word and re.search(lib.CTA_WRITE_RE + rf"\s*[״\"]?{re.escape(code_word)}", s.get("headline", "") + " " + s.get("body", "")):
            issues.append(lib.Issue("ERROR", f"{p}/slide-{s.get('number')}", f"the CTA appears before slide {CTA}"))

    # Caption
    caption = v.get("caption", "")
    issues.extend(lib.audience_text_issues(f"{p}/caption", caption, allow_cta=True))  # second CTA lines checked below
    issues.extend(lib.brand_issues(f"{p}/caption", caption, titles))
    issues.extend(lib.brand_issues(f"{p}/cta", cta, titles))
    cap_lines = lib.lines_of(caption)
    if cap_lines and lib.collapse(cap_lines[-1]) != lib.collapse(cta):
        issues.append(lib.Issue("ERROR", f"{p}/caption", "the caption's final line must be exactly the CTA", excerpt=cap_lines[-1][:80]))
    if not (lib.CAPTION_MIN_LINES <= len(cap_lines) <= lib.CAPTION_MAX_LINES):
        issues.append(lib.Issue("ERROR", f"{p}/caption", f"caption has {len(cap_lines)} lines; the formula is hook line, 2 to 4 value lines, one bridge line, CTA ({lib.CAPTION_MIN_LINES} to {lib.CAPTION_MAX_LINES} lines)"))
    for i, line in enumerate(cap_lines[:-1], start=1):
        for pattern, why in lib.SECOND_CTA_PATTERNS:
            if re.search(pattern, line):
                issues.append(lib.Issue("ERROR", f"{p}/caption", f"caption line {i} adds a second CTA ({why})", excerpt=line[:80]))
        if code_word and re.search(lib.CTA_WRITE_RE + rf"\s*[״\"]?{re.escape(code_word)}", line):
            issues.append(lib.Issue("ERROR", f"{p}/caption", f"caption line {i} repeats the CTA; it belongs only on the final line"))
    if cap_lines and lib.collapse(cap_lines[0]) == lib.collapse(slides[0].get("headline", "")):
        issues.append(lib.Issue("ERROR", f"{p}/caption", "caption line 1 must restate the hook in different words, not copy it"))

    # Sources and claims
    sources = v.get("sources", [])
    src_ids = [s.get("id") for s in sources]
    if len(set(src_ids)) != len(src_ids):
        issues.append(lib.Issue("ERROR", f"{p}/sources", "duplicate source ids"))
    claims = v.get("claims", [])
    used = set()
    for i, c in enumerate(claims):
        cp = f"{p}/claims[{i}]"
        ids = c.get("source_ids", [])
        kind = c.get("kind")
        if kind == "sourced_fact":
            if not ids:
                issues.append(lib.Issue("ERROR", cp, "a sourced fact needs at least one source id"))
            for sid in ids:
                if sid not in src_ids:
                    issues.append(lib.Issue("ERROR", cp, f"unknown source id {sid}"))
                used.add(sid)
        elif kind == "product_fact":
            if not ids:
                issues.append(lib.Issue("ERROR", cp, "a product fact must cite a live-site fact id (site-...)"))
            for sid in ids:
                if sid not in product_ids:
                    issues.append(lib.Issue("ERROR", cp, f"unknown product fact id {sid}"))
        if not str(c.get("supports", "")).strip():
            issues.append(lib.Issue("ERROR", cp, "say what the source supports (or why this is LumeBook wording only)"))
    if direction_id == "expert":
        if not any(c.get("kind") == "sourced_fact" for c in claims):
            issues.append(lib.Issue("ERROR", f"{p}/claims", "expert options need at least one sourced fact"))
        for s in sources:
            if not str(s.get("quote", "")).strip():
                issues.append(lib.Issue("ERROR", f"{p}/sources/{s.get('id')}", "expert sources need a verbatim quote"))
    for sid in src_ids:
        if sid not in used and direction_id == "expert":
            issues.append(lib.Issue("WARN", f"{p}/sources/{sid}", "source is listed but no claim cites it"))
    sourced_slides = {c.get("slide") for c in claims if c.get("kind") == "sourced_fact"}
    if numbered:
        value = set(lib.NUMBERED_VALUE_SLIDES)
        value_label = f"{min(value)} to {max(value)}"
        if not sourced_slides & value:
            issues.append(lib.Issue("ERROR", f"{p}/claims", f"the examples and the whole idea (slides {value_label}) must give real value: map at least one of them to a sourced fact"))
        if direction_id == "expert" and len(sourced_slides & value) < 2:
            issues.append(lib.Issue("ERROR", f"{p}/claims", f"expert options need a sourced fact on at least two of slides {value_label}"))
    else:
        sol = set(lib.SOLUTION_SLIDES)
        sol_label = ", ".join(map(str, lib.SOLUTION_SLIDES))
        if not sourced_slides & sol:
            issues.append(lib.Issue("ERROR", f"{p}/claims", f"the solution slides ({sol_label}) must give real value: map at least one of them to a sourced fact"))
        if direction_id == "expert" and not sol <= sourced_slides:
            issues.append(lib.Issue("ERROR", f"{p}/claims", f"expert options need a sourced fact on every solution slide ({sol_label})"))
    if CTA not in sourced_slides:
        issues.append(lib.Issue("ERROR", f"{p}/claims", f"slide {CTA} suggests a story: map it to a source that supports reading stories about this"))
    if not any(c.get("kind") == "product_fact" and c.get("slide") == CTA for c in claims):
        issues.append(lib.Issue("ERROR", f"{p}/claims", f"slide {CTA} must map the personalised story (the child as the hero) to a live-site product fact"))

    # Character anchor sanity
    anchor = v.get("character_anchor") or {}
    if anchor and not re.search(r"\d", anchor.get("child", "")):
        issues.append(lib.Issue("WARN", f"{p}/character_anchor/child", "state the child's age so the model keeps it stable"))
    for field in lib.ANCHOR_FIELDS:
        if lib.HEBREW_RE.search(anchor.get(field, "")):
            issues.append(lib.Issue("ERROR", f"{p}/character_anchor/{field}", "write the anchor in English"))
    return issues


# ---------------------------------------------------------------------------
# Hook strategy (hook-bank.md and research/hook-strategy-2026-10-08.md)
# ---------------------------------------------------------------------------

def _slide_text(slide):
    return (slide.get("headline", "") + "\n" + slide.get("body", "")).strip()


def _first_line(text):
    lines = lib.lines_of(text)
    return lines[0] if lines else ""


def candidate_text_issues(p, c, titles):
    """Audience rules for a slate candidate's slide 1 and slide 2 text."""
    issues = []
    for field in ("hook", "slide2"):
        text = c.get(field, "")
        issues.extend(lib.audience_text_issues(f"{p}/{field}", text))
        issues.extend(lib.brand_issues(f"{p}/{field}", text, titles))
        m = lib.SALE_PREP_RE.search(text)
        if m:
            issues.append(lib.Issue("ERROR", f"{p}/{field}", f"«{m.group(0)}» sells or prepares a sale; hooks never sell"))
        for pattern, why in lib.HOOK_BANNED:
            if re.search(pattern, lib.collapse(text)):
                issues.append(lib.Issue("ERROR", f"{p}/{field}", f"banned hook wording ({why}): «{re.search(pattern, lib.collapse(text)).group(0)}»"))
        m = lib.DAD_RE.search(lib.PARENT_PAIR_RE.sub(" ", text))
        if m:
            issues.append(lib.Issue("ERROR", f"{p}/{field}", f"never talk to dad: «{m.group(0)}»"))
    hook = c.get("hook", "")
    if len(lib.words(_first_line(hook))) > lib.HOOK_MAIN_MAX_WORDS:
        issues.append(lib.Issue("ERROR", f"{p}/hook", f"hook main line has {len(lib.words(_first_line(hook)))} words (max {lib.HOOK_MAIN_MAX_WORDS})"))
    if len(lib.words(hook)) > lib.HOOK_TOTAL_MAX_WORDS:
        issues.append(lib.Issue("ERROR", f"{p}/hook", f"hook has {len(lib.words(hook))} words (max {lib.HOOK_TOTAL_MAX_WORDS})"))
    s2 = c.get("slide2", "")
    if len(lib.words(s2)) > lib.SLIDE_MAX_WORDS:
        issues.append(lib.Issue("ERROR", f"{p}/slide2", f"slide 2 has {len(lib.words(s2))} words (max {lib.SLIDE_MAX_WORDS})"))
    if lib.SLIDE2_LEANS_ON_SLIDE1_RE.search(lib.collapse(_first_line(s2))):
        issues.append(lib.Issue("ERROR", f"{p}/slide2", f"slide 2 opens with «{lib.SLIDE2_LEANS_ON_SLIDE1_RE.search(lib.collapse(_first_line(s2))).group(0)}» and leans on slide 1; it must work as a first slide on its own"))
    if lib.collapse(s2) == lib.collapse(hook):
        issues.append(lib.Issue("ERROR", f"{p}/slide2", "slide 2 repeats slide 1"))
    return issues


def candidate_fails(c):
    """Why a candidate may not be used: a failed honesty check, a zero on a must-have, or a low total."""
    why = [k for k in lib.SLATE_FAIL_CHECKS if (c.get("fail_checks") or {}).get(k) is True]
    score = c.get("score") or {}
    values = [score.get(k) for k in lib.SLATE_SCORE_KEYS]
    if all(isinstance(v, int) for v in values):
        zeros = [k for k in lib.SLATE_NO_ZERO if score.get(k) == 0]
        if zeros:
            why.append("0 on " + ", ".join(zeros))
        if sum(values) < lib.SLATE_MIN_SCORE:
            why.append(f"scores {sum(values)} of 20 (needs {lib.SLATE_MIN_SCORE})")
    return why


def slate_issues(slate, bank, titles):
    issues = []
    for direction in lib.DIRECTIONS:
        cands = slate.get(direction) or []
        prefix = "k" if direction == "kid" else "e"
        p0 = f"hook_slate/{direction}"
        ids = [c.get("id") for c in cands]
        if len(set(ids)) != len(ids):
            issues.append(lib.Issue("ERROR", p0, "duplicate candidate ids"))
        fams, mechs, used = {}, set(), []
        for c in cands:
            p = f"{p0}/{c.get('id')}"
            if not str(c.get("id", "")).startswith(prefix):
                issues.append(lib.Issue("ERROR", f"{p}/id", f"{direction} candidates are numbered {prefix}1 to {prefix}{lib.SLATE_SIZE}"))
            f = bank.get(c.get("formula"))
            if not f:
                issues.append(lib.Issue("ERROR", f"{p}/formula", f"{c.get('formula')!r} is not in hook-bank.md"))
                continue
            if f["direction"] not in ("both", direction):
                issues.append(lib.Issue("ERROR", f"{p}/formula", f"{f['id']} is a {f['direction']} formula"))
            if c.get("family") != f["family"]:
                issues.append(lib.Issue("ERROR", f"{p}/family", f"formula {f['id']} belongs to family {f['family']}"))
            if f.get("mechanisms") and c.get("mechanism") not in f["mechanisms"]:
                issues.append(lib.Issue("ERROR", f"{p}/mechanism", f"{f['id']} works through {' or '.join(f['mechanisms'])}"))
            fams[f["family"]] = fams.get(f["family"], 0) + 1
            mechs.add(c.get("mechanism"))
            issues.extend(candidate_text_issues(p, c, titles))
            if len(str(c.get("answer", "")).strip()) < 8:
                issues.append(lib.Issue("ERROR", f"{p}/answer", "say how the payoff slide closes the question"))
            if c.get("used_by"):
                used.append(c["used_by"])
                if not c["used_by"].startswith(direction + "-"):
                    issues.append(lib.Issue("ERROR", f"{p}/used_by", f"a {direction} candidate can only become a {direction} option"))
                why = candidate_fails(c)
                if why:
                    issues.append(lib.Issue("ERROR", f"{p}/used_by", f"this candidate fails ({'; '.join(why)}) and cannot become an option"))
        formulas = [c.get("formula") for c in cands]
        for fid in sorted({x for x in formulas if formulas.count(x) > 1}):
            issues.append(lib.Issue("ERROR", p0, f"formula {fid} appears twice; the slate needs structurally different candidates"))
        for fam, n in fams.items():
            if n > lib.HOOK_FAMILY_MAX_IN_WINDOW:
                issues.append(lib.Issue("ERROR", p0, f"family {fam} has {n} candidates (max {lib.HOOK_FAMILY_MAX_IN_WINDOW})"))
        if len(fams) < lib.SLATE_MIN_FAMILIES:
            issues.append(lib.Issue("ERROR", p0, f"only {len(fams)} hook families among the candidates (needs {lib.SLATE_MIN_FAMILIES})"))
        if len(mechs) < lib.SLATE_MIN_MECHANISMS:
            issues.append(lib.Issue("ERROR", p0, f"only {len(mechs)} mechanisms among the candidates (needs {lib.SLATE_MIN_MECHANISMS})"))
        for i, a in enumerate(cands):
            for b in cands[i + 1:]:
                if lib.overlap(a.get("hook", ""), b.get("hook", "")) >= lib.NEAR_DUPLICATE:
                    issues.append(lib.Issue("ERROR", p0, f"{a.get('id')} and {b.get('id')} are near rewrites of each other"))
        expected = [f"{direction}-{i}" for i in range(1, 4)]
        if sorted(used) != expected:
            issues.append(lib.Issue("ERROR", f"{p0}/used_by", f"exactly one candidate per option: {', '.join(expected)} (got {', '.join(sorted(used)) or 'none'})"))
    return issues


def hook_strategy_issues(pack, bank, titles, today=None):
    """Formula evidence status, slide 2 independence, and (schema_version 3) the slate and the diversity of the six."""
    issues = [lib.Issue("ERROR", i.path, i.message) for i in lib.bank_issues(bank)]
    v3 = pack.get("schema_version", 2) >= 3
    try:
        today = today or lib.parse_date(pack.get("date", ""))
    except ValueError:
        today = lib.now_local().date()
    options = [(d.get("id"), v) for d in pack.get("directions", []) for v in d.get("versions", [])]
    slate = pack.get("hook_slate") or {}
    by_id = {c.get("id"): (direction, c) for direction in lib.DIRECTIONS for c in (slate.get(direction) or [])}
    for did, v in options:
        p = f"{did}/{v.get('id')}"
        hook = v.get("hook") or {}
        f = bank.get(hook.get("formula"))
        if f and f.get("has_meta"):
            status = lib.formula_status(f, today)
            if status == "expired":
                issues.append(lib.Issue("ERROR" if v3 else "WARN", f"{p}/hook/formula", f"{f['id']} is a current_trend whose review date {f['review_by']} has passed; revalidate it in hook-bank.md before using it"))
            elif status == "review_due":
                issues.append(lib.Issue("WARN", f"{p}/hook/formula", f"{f['id']} was due for an evidence review on {f['review_by']}"))
        slides = v.get("slides") or []
        if len(slides) > 1:
            m = lib.SLIDE2_LEANS_ON_SLIDE1_RE.search(lib.collapse(_first_line(slides[1].get("headline", ""))))
            if m:
                issues.append(lib.Issue("ERROR" if v3 else "WARN", f"{p}/slide-2/headline", f"slide 2 opens with «{m.group(0)}» and leans on slide 1; it must work as a first slide on its own"))
        if not v3:
            continue
        for key in ("slate_id", "mechanism", "slide2_move"):
            if not hook.get(key):
                issues.append(lib.Issue("ERROR", f"{p}/hook/{key}", "is required from schema_version 3"))
        if f and hook.get("mechanism") and f.get("mechanisms") and hook["mechanism"] not in f["mechanisms"]:
            issues.append(lib.Issue("ERROR", f"{p}/hook/mechanism", f"{f['id']} works through {' or '.join(f['mechanisms'])}"))
        found = by_id.get(hook.get("slate_id"))
        if hook.get("slate_id") and not found:
            issues.append(lib.Issue("ERROR", f"{p}/hook/slate_id", f"{hook['slate_id']} is not in hook_slate"))
        elif found:
            direction, c = found
            if direction != did or c.get("used_by") != v.get("id"):
                issues.append(lib.Issue("ERROR", f"{p}/hook/slate_id", f"candidate {c.get('id')} is not marked used_by {v.get('id')}"))
            for key in ("formula", "mechanism", "slide2_move"):
                ours = hook.get(key)
                if ours and c.get(key) != ours:
                    issues.append(lib.Issue("ERROR", f"{p}/hook/{key}", f"differs from slate candidate {c.get('id')} ({c.get(key)})"))
            if lib.value_hook_applies(pack):
                low = [k for k in lib.COVER_VALUE_MUST_BE_2 if (c.get("score") or {}).get(k) != 2]
                if low:
                    issues.append(lib.Issue("ERROR", f"{p}/hook/slate_id", f"the cover must say what the viewer gets (Yarin, 11 Oct 2026): candidate {c.get('id')} scores under 2 on {', '.join(low)}. Name the value on slide 1 (a number of things, a sentence to say, a result)"))
                if slides and not lib.VALUE_MARKER_RE.search(lib.collapse(_slide_text(slides[0]))):
                    issues.append(lib.Issue("WARN", f"{p}/slide-1", "the cover does not say what the viewer gets: add the number of things, the sentence or the result it promises"))
            if lib.cover_rule_applies(pack):
                weak = [k for k in lib.COVER_HOOK_MUST_BE_2 if (c.get("score") or {}).get(k) != 2]
                if weak:
                    issues.append(lib.Issue("ERROR", f"{p}/hook/slate_id", f"slide 1 is the thumbnail: candidate {c.get('id')} scores under 2 on {', '.join(weak)}. Use or write a stronger one"))
            if slides and lib.collapse(_slide_text(slides[0])) != lib.collapse(c.get("hook", "")):
                issues.append(lib.Issue("WARN", f"{p}/slide-1", f"slide 1 no longer matches slate candidate {c.get('id')} (edited after the slate?)"))
            if c.get("factual_claim") and not any(cl.get("kind") == "sourced_fact" and cl.get("slide") in (1, 2) for cl in v.get("claims", [])):
                issues.append(lib.Issue("ERROR", f"{p}/claims", "the hook states a fact about children: map a sourced_fact claim to slide 1 or 2"))
    if not v3:
        return issues
    if not slate:
        issues.append(lib.Issue("ERROR", "pack/hook_slate", "schema_version 3 packs need the hook slate (6 kid and 6 expert candidates)"))
    else:
        issues.extend(slate_issues(slate, bank, titles))
    # The six final options must not be cosmetic rewrites of one another
    mechs = {did: set() for did in lib.DIRECTIONS}
    shapes, moves, stages = set(), set(), set()
    for did, v in options:
        hook = v.get("hook") or {}
        if did in mechs and hook.get("mechanism"):
            mechs[did].add(hook["mechanism"])
        f = bank.get(hook.get("formula"))
        if f and f.get("shape"):
            shapes.add(f["shape"])
        if hook.get("slide2_move"):
            moves.add(hook["slide2_move"])
        stages.add(v.get("awareness_stage"))
    all_mechs = set().union(*mechs.values())
    if len(all_mechs) < lib.PACK_MIN_MECHANISMS:
        issues.append(lib.Issue("ERROR", "pack/directions", f"the six hooks use {len(all_mechs)} mechanisms (needs {lib.PACK_MIN_MECHANISMS})"))
    for did, ms in mechs.items():
        if len(ms) < 2:
            issues.append(lib.Issue("ERROR", f"{did}", "the three options in a direction need at least 2 different mechanisms"))
    if len(shapes) < lib.PACK_MIN_SHAPES:
        issues.append(lib.Issue("ERROR", "pack/directions", f"the six hooks use {len(shapes)} sentence shapes (needs {lib.PACK_MIN_SHAPES})"))
    if len(moves) < lib.PACK_MIN_SLIDE2_MOVES:
        issues.append(lib.Issue("ERROR", "pack/directions", f"the six slide 2 hooks use {len(moves)} moves (needs {lib.PACK_MIN_SLIDE2_MOVES})"))
    if len(stages) < lib.PACK_MIN_AWARENESS:
        issues.append(lib.Issue("ERROR", "pack/directions", f"all six options target one awareness stage (needs {lib.PACK_MIN_AWARENESS})"))
    for i, (da, a) in enumerate(options):
        for db, b in options[i + 1:]:
            sa, sb = a.get("slides") or [{}], b.get("slides") or [{}]
            if lib.overlap(_slide_text(sa[0]), _slide_text(sb[0])) >= lib.NEAR_DUPLICATE:
                issues.append(lib.Issue("ERROR", "pack/directions", f"{a.get('id')} and {b.get('id')} open with near rewrites of the same hook"))
    return issues


def event_issues(pack, event):
    """An Israeli event pack (topic-bank.md "Israeli events", Yarin 16 Oct 2026): the event is sourced and timely."""
    issues = []
    if not event:
        return [lib.Issue("ERROR", "pack/topic/event", "an event- topic records topic.event (name, date, kind, tone and a source read today)")]
    run = str(pack.get("generated_at", ""))[:10]
    try:
        gap = (lib.parse_date(event["date"]) - lib.parse_date(pack["date"])).days
        if not -lib.EVENT_PAST_DAYS <= gap <= lib.EVENT_AHEAD_DAYS:
            issues.append(lib.Issue("ERROR", "pack/topic/event/date", f"the event is {gap} days from the pack date; an event pack covers something {lib.EVENT_PAST_DAYS} days back to {lib.EVENT_AHEAD_DAYS} days ahead"))
    except (KeyError, ValueError):
        pass
    for key in ("source", "talk_source"):
        src = event.get(key)
        try:
            stale = src and run and abs((lib.parse_date(run) - lib.parse_date(src["accessed"])).days) > 3
        except (KeyError, ValueError):
            stale = False
        if stale:
            issues.append(lib.Issue("ERROR", f"pack/topic/event/{key}/accessed", "read the source again: it must be read within 3 days of the run"))
    if event.get("tone") == "hard" and not event.get("talk_source"):
        issues.append(lib.Issue("ERROR", "pack/topic/event/talk_source", "a hard moment follows official guidance on talking with children (Ministry of Education psychological service, Ministry of Health, NATAL, ERAN): record it in talk_source"))
    return issues


def other_option_issue(issue, pack, option_id):
    """True when the issue belongs to another option of the pack (its own path or its schema path)."""
    path = str(issue.path)
    for di, d in enumerate(pack.get("directions") or []):
        for vi, v in enumerate(d.get("versions") or []):
            if v.get("id") == option_id:
                continue
            if path.startswith(f"{d.get('id')}/{v.get('id')}/") or path == f"{d.get('id')}/{v.get('id')}" \
                    or path.startswith(f"pack/directions[{di}]/versions[{vi}]/") or path == f"pack/directions[{di}]/versions[{vi}]":
                return True
    return False


def option_errors(pack, option_id, **kw):
    """ERRORs that block producing one option: its own and the pack's, never another option's half-done edits
    (Yarin, 18 Oct 2026: Produce on kid-2 failed because expert-1 was mid-edit)."""
    return [i for i in pack_issues(pack, **kw) if i.level == "ERROR" and not other_option_issue(i, pack, option_id)]


def pack_issues(pack, history=None, bank=None, voice=None, today=None):
    root = lib.read_json(lib.SCHEMA)
    issues = schema_issues(pack, root, root)
    if not isinstance(pack, dict) or not isinstance(pack.get("directions"), list):
        return issues

    # Voice honesty
    voice = voice or lib.voice_status()
    pv = pack.get("voice", {})
    if pv.get("status") == "calibrated" and voice["approved_samples"] < lib.CALIBRATION_MIN_SAMPLES:
        issues.append(lib.Issue("ERROR", "pack/voice/status", f"claims calibrated but only {voice['approved_samples']} approved samples exist (needs {lib.CALIBRATION_MIN_SAMPLES})"))
    if isinstance(pv.get("approved_samples"), int) and pv["approved_samples"] > voice["approved_samples"]:
        issues.append(lib.Issue("ERROR", "pack/voice/approved_samples", f"claims {pv['approved_samples']} samples but only {voice['approved_samples']} exist (counted by voice_status)"))
    if pv.get("status") == "fallback" and voice["status"] == "calibrated":
        issues.append(lib.Issue("WARN", "pack/voice/status", "enough samples exist; use the calibrated voice"))

    # Topic
    bank = bank if bank is not None else lib.load_topic_bank()
    topic_id = pack.get("topic", {}).get("id")
    event = pack.get("topic", {}).get("event")
    if lib.is_event_topic(topic_id):
        issues.extend(event_issues(pack, event))
    elif topic_id not in {t["id"] for t in bank}:
        issues.append(lib.Issue("ERROR", "pack/topic/id", f"{topic_id} is not in topic-bank.md"))
    elif event:
        issues.append(lib.Issue("ERROR", "pack/topic/event", "only an Israeli event pack (topic id event-...) records an event"))

    # Product facts must be fresh
    product_ids = set()
    gen_date = str(pack.get("generated_at", ""))[:10]
    for i, f in enumerate(pack.get("product_facts", [])):
        product_ids.add(f.get("id"))
        try:
            age = (lib.parse_date(gen_date) - lib.parse_date(f.get("checked_at", ""))).days
            if age > 2:
                issues.append(lib.Issue("ERROR", f"pack/product_facts[{i}]", f"checked {age} days before the run; re-check the live site"))
        except ValueError:
            issues.append(lib.Issue("ERROR", f"pack/product_facts[{i}]/checked_at", "invalid date"))

    # Directions and versions
    directions = pack.get("directions", [])
    dids = [d.get("id") for d in directions]
    if sorted(dids) != sorted(lib.DIRECTIONS):
        issues.append(lib.Issue("ERROR", "pack/directions", "must be exactly one kid and one expert direction"))
    titles = lib.catalogue_titles(bank)
    hook_bank = lib.load_hook_bank()
    names = lib.load_names()
    option_ids, families, formulas, child_names = [], {}, {}, {}
    for d in directions:
        for v in d.get("versions", []):
            option_ids.append(v.get("id"))
            families[v.get("hook_family")] = families.get(v.get("hook_family"), 0) + 1
            f = (v.get("hook") or {}).get("formula")
            formulas[f] = formulas.get(f, 0) + 1
            child_names[v.get("child_name")] = child_names.get(v.get("child_name"), 0) + 1
            issues.extend(version_issues(d.get("id"), v, pack, product_ids, titles, hook_bank, names))
    dupes = sorted({o for o in option_ids if option_ids.count(o) > 1})
    for o in dupes:
        issues.append(lib.Issue("ERROR", "pack/directions", f"duplicate option id {o}"))
    for nm, n in child_names.items():
        if nm and n > 1:
            issues.append(lib.Issue("ERROR", "pack/directions", f"the name {nm} is used {n} times; give each option its own child"))
    for f, n in formulas.items():
        if f and n > 1:
            issues.append(lib.Issue("ERROR", "pack/directions", f"hook formula {f} is used {n} times; each option needs its own formula"))
    for fam, n in families.items():
        if n > lib.HOOK_FAMILY_MAX_IN_WINDOW:
            issues.append(lib.Issue("ERROR", "pack/directions", f"hook family {fam} is used {n} times in this pack (max {lib.HOOK_FAMILY_MAX_IN_WINDOW})"))
    issues.extend(hook_strategy_issues(pack, hook_bank, titles, today))

    # Rotation against history
    if history is not None and pack.get("date"):
        ctx = lib.rotation_context(history, pack["date"], bank)
        if topic_id in ctx["recent_topic_ids"]:
            issues.append(lib.Issue("ERROR", "pack/topic/id", f"{topic_id} was used in the previous {lib.TOPIC_COOLDOWN_PACKS} packs"))
        for d in directions:
            for v in d.get("versions", []):
                if v.get("code_word") in ctx["recent_code_words"] and v.get("code_word") != lib.CTA_CODE_WORD and not lib.fixed_code_word_applies(pack):
                    issues.append(lib.Issue("ERROR", f"{d.get('id')}/{v.get('id')}/code_word", f"{v.get('code_word')} was used in the last {lib.CODE_WORD_COOLDOWN_DAYS} days"))
                if v.get("hook_family") in ctx["blocked_hook_families"]:
                    issues.append(lib.Issue("ERROR", f"{d.get('id')}/{v.get('id')}/hook_family", f"{v.get('hook_family')} was already published twice in the last {lib.HOOK_FAMILY_WINDOW_DAYS} days"))
                if v.get("child_name") in ctx["recent_child_names"]:
                    issues.append(lib.Issue("WARN", f"{d.get('id')}/{v.get('id')}/child_name", f"{v.get('child_name')} was used in the last {lib.NAME_COOLDOWN_PACKS} packs; pick another name if one fits"))
                f = (v.get("hook") or {}).get("formula")
                if f and f in ctx["recent_hook_formulas"]:
                    issues.append(lib.Issue("WARN", f"{d.get('id')}/{v.get('id')}/hook/formula", f"{f} was used in the last {lib.HOOK_RECENT_PACKS} packs; rotate if another formula fits"))
                hook = lib.collapse(v.get("slides", [{}])[0].get("headline", "")) if v.get("slides") else ""
                if hook and hook in ctx["recent_hooks"]:
                    issues.append(lib.Issue("ERROR", f"{d.get('id')}/{v.get('id')}/slide-1", "this hook was used in a recent pack"))
                elif hook and any(lib.overlap(hook, h) >= lib.NEAR_DUPLICATE for h in ctx["recent_hooks"]):
                    issues.append(lib.Issue("WARN", f"{d.get('id')}/{v.get('id')}/slide-1", "this hook reuses most of the wording of a recent hook"))
                s2 = lib.collapse(v["slides"][1].get("headline", "")) if len(v.get("slides", [])) > 1 else ""
                if s2 and s2 in ctx["recent_slide2_hooks"]:
                    issues.append(lib.Issue("WARN", f"{d.get('id')}/{v.get('id')}/slide-2", "this slide 2 headline was used in a recent pack"))
                if f and f in ctx["selected_formulas_last_14_days"]:
                    issues.append(lib.Issue("WARN", f"{d.get('id')}/{v.get('id')}/hook/formula", f"{f} was published in the last 14 days; only keep it if no fresher formula is as strong"))
    return issues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    ap.add_argument("--json", action="store_true", help="print machine readable results")
    ap.add_argument("--no-history", action="store_true", help="skip the rotation checks against history.json")
    ap.add_argument("--history", default=str(lib.HISTORY))
    args = ap.parse_args()
    path = Path(args.pack)
    try:
        pack = lib.read_json(path)
    except json.JSONDecodeError as exc:
        print(f"INVALID {path}\n- ERROR pack: not valid JSON ({exc})")
        raise SystemExit(1)
    history = None if args.no_history else lib.load_history(args.history)
    issues = pack_issues(pack, history=history) + lib.example_target_issues(pack, path.resolve().parent)
    errors = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level == "WARN"]
    if args.json:
        print(json.dumps({"valid": not errors, "errors": [i.as_dict() for i in errors], "warnings": [i.as_dict() for i in warns]}, ensure_ascii=False, indent=2))
    else:
        if errors:
            print(f"INVALID {path}")
            for i in errors:
                print(f"- {i}")
        if warns:
            print("Warnings for the reviewer:")
            for i in warns:
                print(f"- {i}")
        if not errors:
            n = sum(len(v.get("slides", [])) for d in pack["directions"] for v in d["versions"])
            print(f"VALID {path}: 2 directions, 6 options, {n} slides")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
