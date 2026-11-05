#!/usr/bin/env python3
"""Shared rules and helpers for the LumeBook carousel pipeline.

Everything that more than one script needs lives here so there is exactly one
definition of the Hebrew hard rules, the slide structure, the image prompt
assembly, the topic rotation and the voice calibration status.

Standard library only, so the nightly run never depends on pip installs.
"""

import datetime as dt
import json
import os
import re
import shutil
import struct
import unicodedata
import zlib
from pathlib import Path

import story_lib  # the story copy format (story-format.md, 29 Oct 2026)

PIPELINE = Path(__file__).resolve().parents[1]
# Project root = the nearest folder up that holds lumebook.json (the component registry)
ROOT = next((p for p in PIPELINE.parents if (p / "lumebook.json").exists()), PIPELINE.parents[1])
DRAFTS = PIPELINE / "drafts"
APPROVED = PIPELINE / "approved"
HISTORY = PIPELINE / "history.json"
TOPIC_BANK = PIPELINE / "topic-bank.md"
HOOK_BANK = PIPELINE / "hook-bank.md"
NAMES = PIPELINE / "names.md"
SCHEMA = PIPELINE / "pack.schema.json"
VOICE_PROFILE = PIPELINE / "voice-profile.md"
VOICE_SKILL = ROOT / ".claude" / "skills" / "lumebook-hebrew-voice"
APPROVED_EXAMPLES = VOICE_SKILL / "examples" / "approved"
REJECTED_EXAMPLES = VOICE_SKILL / "examples" / "rejected"
VOICE_EDITS = VOICE_SKILL / "examples" / "edits.jsonl"
# Where production pictures come from: the OpenAI Images API only (Yarin, 03 Nov 2026: "disconnect carousel machine from any other
# image generation tool, i want it to use the gpt api from now on"). Model, size, quality and rates: scripts/openai_models.json.
# fal.ai (until 30 Oct 2026) and ChatGPT in Chrome (30 Oct to 03 Nov 2026) are retired, their files are in _to-delete/.
PICTURE_BACKEND = "openai"
OPENAI_MODELS = PIPELINE / "scripts" / "openai_models.json"


def picture_backend():
    """Always "openai". Kept as a function so producer.py, the page and the tests ask one place."""
    return PICTURE_BACKEND


CHROME_MAC = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_LINUX = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")


def find_chrome():
    """The Chrome or Chromium that renders the slides, or None.

    CHROME_PATH wins when it is set (a full path or a command name); then the Mac app; then the first
    Linux name on PATH, so Claude Code on the web renders too (README, Running in the cloud).
    """
    env = os.environ.get("CHROME_PATH", "").strip()
    if env:
        return shutil.which(env)
    if Path(CHROME_MAC).exists():
        return CHROME_MAC
    return next(filter(None, map(shutil.which, CHROME_LINUX)), None)


CHROME = find_chrome()

CALIBRATION_MIN_SAMPLES = 15
TOPIC_COOLDOWN_PACKS = 14
EVENT_TOPIC_PREFIX = "event-"   # an Israeli event pack's topic id (topic-bank.md "Israeli events", Yarin 16 Oct 2026)
EVENT_PAST_DAYS, EVENT_AHEAD_DAYS = 3, 21  # the event happens between 3 days before and 21 days after the pack date
CODE_WORD_COOLDOWN_DAYS = 14
HOOK_FAMILY_WINDOW_DAYS = 7
HOOK_FAMILY_MAX_IN_WINDOW = 2
NAME_COOLDOWN_PACKS = 7

# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

DIRECTIONS = ("kid", "expert")
SLIDE_COUNT = 7
# The arc (Yarin, 7 Oct 2026): every slide gives value and pulls to the next one. Hook, second hook, what is
# behind the feeling or problem, two solutions, the resolution, and only the last slide suggests a personalised
# story where the child is the hero, together with the comment CTA. Nothing before it prepares a sale.
SLIDE_ROLES = {
    1: ("hook",),
    2: ("second_hook",),
    3: ("recognition", "reframe"),
    4: ("solution",),
    5: ("solution",),
    6: ("resolution",),
    7: ("story_cta",),
}
HOOK_SLIDES = (1, 2)
INSIGHT_SLIDES = (3,)
SOLUTION_SLIDES = (4, 5)
RESOLUTION_SLIDE = 6
CTA_SLIDE = 7
ROLE_LABELS_HE = {
    "hook": "פתיח",
    "second_hook": "פתיח שני",
    "recognition": "הבעיה או הרגש",
    "reframe": "מה עומד מאחורי זה",
    "solution": "פתרון",
    "resolution": "הסגירה",
    "story_cta": "סיפור אישי וקריאה לפעולה",
    "explain": "ההסבר",
    "example": "דוגמאות ממוספרות",
    "recap": "סיכום",
}
# Words that prepare a sale. They belong only on the last slide.
SALE_PREP_RE = re.compile(r"ספר\s+שבו|סיפור\s+אישי|ספר\s+אישי|גיבור|קישור|תצוגה\s+מקדימה|בתגובות")
# What makes the reader swipe from this slide to the next (every slide before the last).
PULL_TYPES = {
    "question": "שאלה שהתשובה עליה בשקופית הבאה",
    "open_loop": "משהו שנפתח ונסגר בשקופית הבאה",
    "next_step": "הבטחה לצעד הבא",
    "contrast": "ניגוד שמבקש הסבר",
    "numbered": "רשימה שעוד לא נגמרה",
}
# Hook families follow section 7 of docs/lumebook-instagram-carousel-playbook-he.md
HOOK_FAMILIES = {
    "moment": "רגע מוכר",
    "child_quote": "ציטוט של ילד",
    "child_pov": "הילד מדבר בגוף ראשון",
    "practical_question": "שאלה מעשית",
    "reframe": "שינוי תפיסה",
    "sentences_we_say": "משפטים שכולנו אומרים",
    "parent_identity": "זהות הורית",
    "gentle_outcome": "תוצאה רצויה עדינה",
    "story": "סיפור",
    "surprising_statement": "אמירה מפתיעה",
    "milestone": "רגע התפתחותי",
    "gift": "מתנה לאירוע",
    "objection": "התנגדות",
    "demo": "הדגמה",
    # Added by the hook strategy research (carousel/carousel-pipeline/research/hook-strategy-2026-10-08.md)
    "normalising": "נרמול שמוריד בושה",
    "analogy": "משל מעולם המבוגרים",
}
AWARENESS_STAGES = ("unaware", "problem_aware", "solution_aware", "product_aware", "most_aware")
AWARENESS_LABELS_HE = {
    "unaware": "לא מודע",
    "problem_aware": "מכיר את הבעיה",
    "solution_aware": "מחפש פתרון",
    "product_aware": "מכיר את המוצר",
    "most_aware": "כמעט קונה",
}
CLAIM_KINDS = ("sourced_fact", "product_fact", "lumebook_wording")

# ---------------------------------------------------------------------------
# Hebrew hard rules
# ---------------------------------------------------------------------------

# Characters that must never appear in audience facing Hebrew (Yarin, 24 Oct 2026: "lets bring back punctuation marks
# except em dashes, semicolon and hyphens"): every dash, the semicolon and the hyphen, with their lookalikes so a model
# cannot slip past the rule with a near identical glyph. Periods, commas, question and exclamation marks, colons,
# quotation marks and the ellipsis are fine again. Packs written before PUNCTUATION_FROM (and the games and books
# carousels) keep LEGACY_FORBIDDEN_CHARS: no dash, period or comma, hyphens allowed.
FORBIDDEN_CHARS = {
    "—": "em dash",
    "―": "horizontal bar (em dash lookalike)",
    "⸺": "two-em dash",
    "⸻": "three-em dash",
    "–": "en dash (write עד for ranges)",
    "﹘": "small em dash",
    "-": "hyphen (write the number or word on its own: ועוד 8, בשעה 17:40, 3 עד 6)",
    "־": "maqaf (Hebrew hyphen)",
    "‐": "hyphen",
    "‑": "non-breaking hyphen",
    "‒": "figure dash",
    "−": "minus sign (hyphen lookalike)",
    "﹣": "small hyphen",
    "－": "fullwidth hyphen",
    ";": "semicolon",
    "；": "fullwidth semicolon",
    "\u037e": "Greek question mark (semicolon lookalike)",
}
PUNCTUATION_FROM = "2026-10-24T21:00"
LEGACY_FORBIDDEN_CHARS = {
    "—": "em dash",
    "―": "horizontal bar (em dash lookalike)",
    "⸺": "two-em dash",
    "⸻": "three-em dash",
    "–": "en dash (used as an em dash substitute; write עד for ranges)",
    "﹘": "small em dash",
    ".": "period",
    "．": "fullwidth period",
    "﹒": "small period",
    "…": "ellipsis (three periods)",
    ",": "comma",
    "，": "fullwidth comma",
    "﹐": "small comma",
    "،": "Arabic comma",
    "、": "ideographic comma",
}

HEBREW_RE = re.compile(r"[א-ת]")
LATIN_RE = re.compile(r"[A-Za-z]")
WORD_RE = re.compile(r"[\w֐-׿]", re.UNICODE)

# Lexicon checks. ERROR entries fail the build, WARN entries are shown to the
# reviewer. Matching is on whole Hebrew tokens or exact phrases so that normal
# words are not caught by accident.
LEXICON_ERRORS = [
    # diagnosis and clinical jargon
    (r"חרד(ה|ת|תי|תית|ות)\b", "diagnostic word חרדה (write חשש or קשה לו)"),
    (r"\bהפרע(ה|ת|ות)\b", "diagnostic word הפרעה"),
    (r"\bאבחנ|\bאבחון|\bמאובחנ", "diagnosis language"),
    (r"\bטראומ", "clinical word טראומה"),
    (r"\bויסות|\bרגולציה|\bדיסרגולציה", "jargon ויסות or רגולציה"),
    (r"\bסימפטומ|\bתסמינ", "clinical word תסמין"),
    (r"\bפתולוג", "clinical word פתולוגי"),
    (r"\bקוגניטיב|\bנוירולוג|\bמערכת העצבים", "jargon"),
    (r"\bטריגר", "jargon טריגר"),
    # fake certainty and guarantees
    (r"\bמוכח|\bהוכח", "fake certainty מוכח"),
    (r"\bמובטח", "guarantee מובטח"),
    (r"100\s*%|מאה אחוז", "fake certainty 100 percent"),
    (r"בלי דמעות", "outcome promise בלי דמעות"),
    (r"שבאמת עובד|תמיד עובד", "outcome promise"),
    (r"\bיפתור|\bפותר את|\bהפתרון ל", "the book or tip fixes the problem"),
    (r"\bייעלם|\bיעלים|\bיעלמו", "promise that a feeling will disappear"),
    (r"\bמרפא|\bירפא|\bטיפולי", "treatment claim"),
    # universality
    (r"\bכל הילדים\b(?!\s+שונים)|\bכל ילד\b(?!\s+(?:שונה|אחר))|\bכל ילדה\b(?!\s+(?:שונה|אחרת))|\bכל הפעוטות\b|\bכל הקטנים\b", "claim that every child feels the same"),
    # brand spelling
    (r"לומיבוק", "brand misspelled (write לומבוק)"),
]
LEXICON_WARNINGS = [
    (r"\bאשמ", "guilt word, check the line does not blame parents"),
    (r"\bאתם עושים את זה לא נכון|\bטעות שכל|\bטעויות שכל", "guilt framing"),
    (r"\bמסוכנ|\bסכנה|\bנזק|\bצלקת|\bיהרוס|\bהרסני", "scare word"),
    (r"\bכל ההורים\b|\bכולם מרגישים", "generalisation"),
    (r"\bמחקרים מוכיחים|\bמחקרים מראים|\bמומחים אומרים|\bמומחים ממליצים", "authority phrase, make sure a claim maps to a source"),
    (r"\bתמיד\b|\bאף פעם\b|\bבחיים לא\b", "absolute word, check it is not fake certainty"),
]
# Python's \b treats a Hebrew prefix letter (ו ש ה ב ל מ כש) as part of the word, so "שמוכח" would
# slip past \bמוכח. _heb() turns each leading \b into "no Hebrew letter before, optional prefix"
# and each trailing \b into "no Hebrew letter after".
_HEB_START = r"(?<![\u05D0-\u05EA])(?:וכש|כש|וה|שה|ו|ש|ה|ב|ל|מ)?"
_HEB_END = r"(?![\u05D0-\u05EA])"


def _heb(pattern):
    pattern = re.sub(r"(^|\||\()\\b", lambda m: m.group(1) + _HEB_START, pattern)
    return pattern.replace(r"\b", _HEB_END)


LEXICON_ERRORS = [(_heb(p), why) for p, why in LEXICON_ERRORS]
LEXICON_WARNINGS = [(_heb(p), why) for p, why in LEXICON_WARNINGS]

# Hebrew attaches ו/ש/כש/ה to the word, so patterns allow those prefixes instead of using \b
_P = r"(?<![\u05D0-\u05EA])(?:ו|ש|כש|וכש)?"
SECOND_CTA_PATTERNS = [
    (r"בביו|לינק|קישור בביו", "link in bio CTA"),
    (_P + r"(?:שמרו|תשמרו)(?:\s+(?:את|לפעם|לערב|לרגע|לאחר|לבוקר|לפוסט|אצלכם)|\s*$)", "save CTA"),
    (_P + r"(?:שתפו|תשתפו)\s+(?:את|עם)|" + _P + r"(?:שלחו|תשלחו)\s+(?:את זה|לחבר|לחברה|למישהו|לאמא|לאבא)", "share CTA"),
    (_P + r"(?:תייגו|תתייגו)(?![\u05D0-\u05EA])", "tag CTA"),
    (_P + r"(?:עקבו|תעקבו)(?![\u05D0-\u05EA])", "follow CTA"),
    (_P + r"(?:הזמינו\s+(?:עכשיו|היום)|לחצו(?![\u05D0-\u05EA]))", "purchase or click CTA"),
]
AUTHORITY_TITLES = re.compile(r"ד״ר|ד\"ר|דר׳|דוקטור|פרופ׳|פרופ'|פרופסור")
FIRST_PERSON_RE = re.compile(r"(?<![\u05D0-\u05EA])(ו|ש|כש|וכש)?(אני|לי|שלי|אותי|ממני|איתי|בשבילי|אליי|עליי|לנו|אנחנו)(?![\u05D0-\u05EA])")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

LINE_MAX_WORDS = 12
HOOK_MAIN_MAX_WORDS = 8
HOOK_TOTAL_MAX_WORDS = 12
SLIDE_MAX_WORDS = 25
CTA_SLIDE_MAX_WORDS = 18
CAPTION_MIN_LINES = 5
# Width limits measured with compose_slides.py at the readable floors (headline 56px Heebo Black,
# body 44px Assistant Bold, 888px text column): longer lines overflow the 1080px slide.
HEADLINE_LINE_MAX_CHARS = 30
BODY_LINE_MAX_CHARS = 42
# The bold look (compose_slides.py --look bold, the default since 10 Oct 2026): type first, so lines are short.
# Measured the same way at the bold floors (cover headline 84px, headline 72px, body 42px Rubik, 952px column).
# Applies to packs written from BOLD_RULE_FROM on; older packs keep the limits above.
BOLD_RULE_FROM = "2026-10-10T18:30"
COVER_HEADLINE_LINE_MAX_CHARS = 18
BOLD_HEADLINE_LINE_MAX_CHARS = 22
BOLD_BODY_LINE_MAX_CHARS = 34
BOLD_HEADLINE_MAX_LINES = 2   # the cover may use 3
BOLD_BODY_MAX_LINES = 3
BOLD_SLIDE_MAX_WORDS = 20
HIGHLIGHT_MAX_WORDS = 3
# Words that take the edge off a cover. A warning: a hedge a claim really needs moves to the payoff slide.
SOFT_COVER_RE = re.compile(r"(?<![א-ת])(?:קצת|אולי|לפעמים|בערך|כנראה|די)(?![א-ת])")


def bold_rule_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= BOLD_RULE_FROM


# Yarin, 10 Oct 2026: "i need the headlines of each slide to tell a story even if the viewer doesnt read the rest in each
# slide". Someone who reads only the seven headlines, in order, must get the whole carousel: the moment, the feeling,
# what is behind it, the two things to try (each headline NAMES the thing), how it ends, the offer. The body adds detail,
# proof and the sentence to say, never the thing itself. Applies to packs generated from HEADLINE_STORY_FROM on.
HEADLINE_STORY_FROM = "2026-10-10T22:00"
HEADLINE_MIN_WORDS = 3
HEADLINE_ORDER_ONLY_RE = re.compile(r"^(?:ו)?(?:דבר\s+(?:ראשון|שני|שלישי)|עוד\s+דבר(?:\s+קטן)?|קודם|אחר\s+כך|ואז|ועכשיו|בסוף)$")


def headline_story_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= HEADLINE_STORY_FROM


def headline_story_issues(path, slide):
    head = collapse(slide.get("headline", ""))
    if HEADLINE_ORDER_ONLY_RE.match(head):
        return [Issue("ERROR", f"{path}/headline", f"«{head}» is only an order word: the headline must name the thing itself, because some people read only the headlines (Yarin, 10 Oct 2026)")]
    n = len(words(head))
    if n < HEADLINE_MIN_WORDS:
        return [Issue("ERROR", f"{path}/headline", f"headline has {n} words: it must be a full thought that carries the story on its own (at least {HEADLINE_MIN_WORDS}), because some people read only the headlines (Yarin, 10 Oct 2026)")]
    return []


# Yarin, 10 Oct 2026: "in the kid stories and expert carousels when you give examples i want them to be between 3-7".
# The slide count stays 7. Wherever a slide lists examples (a story or music or a bath), the slide records them in
# `examples` and the list has 3 to 7 items; each option gets its own random number from the nightly draw
# (`examples_target`, saved in drafts/DATE/example-slots.json, like the games and books suggestion counts).
EXAMPLES_MIN, EXAMPLES_MAX = 3, 7
EXAMPLES_FROM = "2026-10-10T23:00"
EXAMPLE_SLOTS_FILE = "example-slots.json"
OPTION_IDS = ("kid-1", "kid-2", "kid-3", "expert-1", "expert-2", "expert-3")


def examples_rule_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= EXAMPLES_FROM


def draw_example_slots(folder, rng=None):
    """{option id: 6..9} (since the 10 slide layout, 14 Oct 2026; 3..7 before). The first call for a date draws and saves them, so a rerun keeps the same numbers."""
    import random
    path = Path(folder) / EXAMPLE_SLOTS_FILE
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["slots"]
    rng = rng or random.SystemRandom()
    # kid-4 to kid-6 are the second topic of a two-topic pack (24 Oct 2026); the expert ids stay for older dates
    slots = {oid: rng.randint(NUMBERED_EXAMPLES_MIN, NUMBERED_EXAMPLES_MAX) for oid in dict.fromkeys(OPTION_IDS + PAIR_OPTION_IDS)}
    path.write_text(json.dumps({"drawn_at": now_local().isoformat(timespec="seconds"), "slots": slots}, indent=2) + "\n", encoding="utf-8")
    return slots


def example_issues(path, slide, version, pack):
    """The `examples` list of one slide: 3 to 7 distinct items that really appear on the slide, matching the option's draw."""
    items = slide.get("examples")
    if items is None:
        return []
    issues = []
    n = len(items)
    if not EXAMPLES_MIN <= n <= EXAMPLES_MAX:
        issues.append(Issue("ERROR", f"{path}/examples", f"a list of examples has {EXAMPLES_MIN} to {EXAMPLES_MAX} items (Yarin, 10 Oct 2026); this one has {n}"))
    if len({collapse(x) for x in items}) != n:
        issues.append(Issue("ERROR", f"{path}/examples", "the examples must be different from each other"))
    shown = collapse(slide.get("headline", "") + " " + slide.get("body", ""))
    for x in items:
        if collapse(x) not in shown:
            issues.append(Issue("ERROR", f"{path}/examples", f"«{x}» is listed as an example but does not appear on the slide; list only what the slide shows"))
    target = (version or {}).get("examples_target")
    if target is not None and n != target:
        issues.append(Issue("ERROR", f"{path}/examples", f"tonight's draw for this option is {target} examples; this list has {n}"))
    return issues


# Yarin, 14 Oct 2026, two messages: "every slide from the second one should show one-two examples, numbering them,
# and second to last explain the idea as a whole", then "one picture that depicts the idea for the entire carousel,
# also make them 10 slides, 2nd slide explaining, second to last recap". Packs from TEN_SLIDE_FROM have 10 slides:
# 1 hook, 2 explains the idea, 3 to 8 show 1 or 2 examples each, numbered 1, 2, 3... across the carousel (the digit
# written right before the example), 9 recaps, 10 the personalised story and CTA. Six slides of 1 or 2, 6 to 9 examples in all
# (Yarin: "lets do 6-9"). Each option has ONE picture (`image` on the option) used behind every slide.
TEN_SLIDE_FROM = "2026-10-14T10:00"
NUMBERED_EXAMPLES_FROM = TEN_SLIDE_FROM
TEN_SLIDE_COUNT = 10
NUMBERED_EXAMPLE_SLIDES = (3, 4, 5, 6, 7, 8)
EXAMPLES_PER_SLIDE_MIN, EXAMPLES_PER_SLIDE_MAX = 1, 2
NUMBERED_EXAMPLES_MIN, NUMBERED_EXAMPLES_MAX = 6, 9  # Yarin, 14 Oct 2026: "lets do 6-9"
EXPLAIN_SLIDE = 2
RECAP_SLIDE = 9
NUMBERED_SLIDE_ROLES = {
    1: ("hook",),
    2: ("explain",),
    **{n: ("example",) for n in NUMBERED_EXAMPLE_SLIDES},
    9: ("recap",),
    10: ("story_cta",),
}
# Slides that give the value and so need a sourced fact (kid: one of them, expert: two of them).
NUMBERED_VALUE_SLIDES = (2, 3, 4, 5, 6, 7, 8, 9)


def ten_slide_era(pack):
    """Packs written from TEN_SLIDE_FROM on (10 slides, one picture), the story packs included."""
    return str((pack or {}).get("generated_at", ""))[:16] >= TEN_SLIDE_FROM


def numbered_examples_apply(pack):
    """10 slides with numbered examples: packs from TEN_SLIDE_FROM, except story packs (story-format.md, 29 Oct 2026),
    which have no numbered examples."""
    return ten_slide_era(pack) and not story_lib.is_story(pack)


def slide_roles(pack):
    """Roles by slide number for the fixed layouts. Story packs have 9 to 12 slides: story_lib.ROLES, checked by the validator."""
    return NUMBERED_SLIDE_ROLES if ten_slide_era(pack) else SLIDE_ROLES


def slide_count(pack):
    """The fixed slide count of a pack's era. A story option has 9 to 12 slides: use last_slide(version) for it."""
    return TEN_SLIDE_COUNT if ten_slide_era(pack) else SLIDE_COUNT


def last_slide(version):
    """The CTA slide: the last one (7 in older packs, 10 since 14 Oct 2026)."""
    return len((version or {}).get("slides") or []) or SLIDE_COUNT


def one_picture(version):
    """True when the option has one picture for the whole carousel (packs from 14 Oct 2026)."""
    return isinstance((version or {}).get("image"), dict)


def slide_image(version, slide):
    """The image brief behind a slide: the option's one picture, or the slide's own brief in older packs."""
    return version["image"] if one_picture(version) else slide["image"]


NUMBERED_LINE_RE = re.compile(r"^\s*(\d{1,2})\s+(\S.*)$")


def sync_numbered_examples(version):
    """Make the hidden `examples` lists and `examples_target` follow what the slides say (Yarin, 18 Oct 2026: the editor
    saved his reworded and removed examples, the lists stayed old and the production stopped on errors he could not
    fix from the page). On slides 3 to 8 each headline line that starts with a number is an example (that line's
    words; a line after it without a number stays on the slide but is not part of the example, as the packs write it); the numbers are rewritten 1, 2, 3... in order, and when the count changes, a cover or caption
    number that stated the old count is updated. A slide with no numbered line keeps its list (the validator names it).
    Returns {"examples": old->new count or None, "renumbered": bool, "changed": [slide numbers]}."""
    slides = {s.get("number"): s for s in version.get("slides") or []}
    old_target = version.get("examples_target")
    k, changed, renumbered = 0, [], False
    for n in NUMBERED_EXAMPLE_SLIDES:
        s = slides.get(n)
        if not s:
            continue
        lines = str(s.get("headline", "")).split("\n")
        if not any(NUMBERED_LINE_RE.match(l) for l in lines):
            k += len(s.get("examples") or [])
            continue
        items, out = [], []
        for line in lines:
            m = NUMBERED_LINE_RE.match(line)
            if m:
                k += 1
                if int(m.group(1)) != k:
                    renumbered = True
                items.append(m.group(2).strip())
                out.append(f"{k} {m.group(2).strip()}")
            else:
                out.append(line)
        new_head = "\n".join(out)
        old = s.get("examples") or []
        shown, first = collapse(new_head + " " + s.get("body", "")), k - len(items) + 1
        if len(old) == len(items) and all(re.search(rf"(?<!\d){first + i}\s+{re.escape(collapse(x))}", shown) for i, x in enumerate(old)):
            items = old  # the list still matches the slide (some packs list both lines of an example): keep it
        if items != s.get("examples") or new_head != s.get("headline"):
            changed.append(n)
        s["examples"], s["headline"] = items, new_head
    count = None
    if isinstance(old_target, int) and k and k != old_target:
        count = (old_target, k)
        version["examples_target"] = k
        num = re.compile(rf"(?<!\d){old_target}(?!\d)")
        cover = slides.get(1) or {}
        for field in ("headline", "body"):
            if len(num.findall(cover.get(field, ""))) == 1:
                cover[field] = num.sub(str(k), cover[field])
        cap = str(version.get("caption", "")).split("\n")
        hits = [i for i, l in enumerate(cap) if num.search(l)]
        if len(hits) == 1 and len(num.findall(cap[hits[0]])) == 1:
            cap[hits[0]] = num.sub(str(k), cap[hits[0]])
            version["caption"] = "\n".join(cap)
    return {"examples": count, "renumbered": renumbered, "changed": changed}


def numbered_example_issues(path, version):
    """Slides 3 to 8: 1 or 2 examples each, numbered in one run from 1, each number written right before its example
    on the slide; the other slides list none; the total is the option's draw."""
    issues = []
    slides = {s.get("number"): s for s in version.get("slides") or []}
    k = 0
    for n in sorted(slides):
        s = slides[n]
        sp = f"{path}/slide-{n}/examples"
        items = s.get("examples")
        if n not in NUMBERED_EXAMPLE_SLIDES:
            if items:
                issues.append(Issue("ERROR", sp, "only slides 3 to 8 show numbered examples (slide 2 explains, slide 9 recaps)"))
            continue
        items = items or []
        if not EXAMPLES_PER_SLIDE_MIN <= len(items) <= EXAMPLES_PER_SLIDE_MAX:
            issues.append(Issue("ERROR", sp, f"every slide from 3 to 8 shows 1 or 2 numbered examples (Yarin, 14 Oct 2026); this one lists {len(items)}"))
        shown = collapse(s.get("headline", "") + " " + s.get("body", ""))
        for x in items:
            k += 1
            if not re.search(rf"(?<!\d){k}\s+{re.escape(collapse(x))}", shown):
                issues.append(Issue("ERROR", sp, f"example {k} «{x}» must appear on the slide with its number right before it: «{k} {collapse(x)}»"))
    all_items = [collapse(x) for n in NUMBERED_EXAMPLE_SLIDES for x in (slides.get(n) or {}).get("examples") or []]
    if len(set(all_items)) != len(all_items):
        issues.append(Issue("ERROR", f"{path}/examples", "the examples must be different from each other"))
    target = version.get("examples_target")
    if isinstance(target, int) and k != target:
        issues.append(Issue("ERROR", f"{path}/examples", f"tonight's draw for this option is {target} examples across slides 3 to 8; the slides number {k}"))
    cover = slides.get(1) or {}
    promised = re.findall(r"(?<!\d)([1-9]|1[0-2])(?!\d)", cover.get("headline", ""))
    if k and promised and str(k) not in promised:
        issues.append(Issue("WARN", f"{path}/slide-1", f"the cover promises {', '.join(promised)} but the slides number {k} examples"))
    return issues


def example_target_issues(pack, folder):
    """Cross-check the options' examples_target against the saved draw (only when the pack applies the rule; story packs
    have no examples)."""
    if not examples_rule_applies(pack) or story_lib.is_story(pack):
        return []
    f = Path(folder) / EXAMPLE_SLOTS_FILE
    if not f.exists():
        return []
    slots = json.loads(f.read_text(encoding="utf-8"))["slots"]
    out = []
    for d in pack.get("directions", []):
        for v in d.get("versions", []):
            if v.get("id") in slots and v.get("examples_target") != slots[v["id"]]:
                out.append(Issue("ERROR", f"{d.get('id')}/{v.get('id')}/examples_target", f"tonight's draw for {v['id']} is {slots[v['id']]}; the pack says {v.get('examples_target')}"))
    return out


def highlight_issues(path, slide, last=CTA_SLIDE, required=True):
    """Every slide but the last names the one phrase that gets the colour block: whole words taken from the headline."""
    head = slide.get("headline", "")
    hl = str(slide.get("highlight") or "").strip()
    if not hl:
        if slide.get("number") == last or not required:
            return []
        return [Issue("ERROR", f"{path}/highlight", "name the 1 to 3 words of the headline that get the colour block (highlight)")]
    line = next((ln for ln in lines_of(head) if hl in ln), None)
    if line is None:
        return [Issue("ERROR", f"{path}/highlight", f"«{hl}» is not in the headline (it must sit on one line, word for word)")]
    issues = []
    i = line.index(hl)
    before, after = line[:i], line[i + len(hl):]
    if (before and HEBREW_RE.match(before[-1])) or (after and HEBREW_RE.match(after[0])):
        issues.append(Issue("ERROR", f"{path}/highlight", f"«{hl}» cuts a word in the middle; highlight whole words (with their prefix letter)"))
    if len(words(hl)) > HIGHLIGHT_MAX_WORDS:
        issues.append(Issue("ERROR", f"{path}/highlight", f"highlight has {len(words(hl))} words (max {HIGHLIGHT_MAX_WORDS}); the block marks the punch, not the line"))
    return issues
CAPTION_MAX_LINES = 8


class Issue:
    """One validation finding. level is ERROR or WARN."""

    def __init__(self, level, path, message, char=None, line=None, col=None, excerpt=None):
        self.level = level
        self.path = path
        self.message = message
        self.char = char
        self.line = line
        self.col = col
        self.excerpt = excerpt

    def as_dict(self):
        out = {"level": self.level, "path": self.path, "message": self.message}
        if self.char is not None:
            out["char"] = self.char
            out["codepoint"] = f"U+{ord(self.char):04X}"
        if self.line is not None:
            out["line"] = self.line
            out["col"] = self.col
        if self.excerpt is not None:
            out["excerpt"] = self.excerpt
        return out

    def __str__(self):
        where = self.path
        if self.line is not None:
            where += f" line {self.line} col {self.col}"
        text = f"{self.level} {where}: {self.message}"
        if self.char is not None:
            text += f" {self.char!r} (U+{ord(self.char):04X})"
        if self.excerpt:
            text += f" in «{self.excerpt}»"
        return text


def words(text):
    """Count spoken words: whitespace separated tokens that contain a letter or digit."""
    return [t for t in text.split() if WORD_RE.search(t)]


def lines_of(text):
    return [line.strip() for line in str(text).splitlines() if line.strip()]


def collapse(text):
    return " ".join(str(text).split())


def punctuation_rule_applies(pack):
    """Dashes, semicolons and hyphens out, the rest of punctuation back: packs from PUNCTUATION_FROM and packs moved to the save for later CTA."""
    return str((pack or {}).get("generated_at", ""))[:16] >= PUNCTUATION_FROM or (pack or {}).get("cta_style") == SAVE_LATER_STYLE


def forbidden_char_issues(path, text, legacy=False):
    """Report every forbidden character with its exact line and column. Never edits the text."""
    issues = []
    chars = LEGACY_FORBIDDEN_CHARS if legacy else FORBIDDEN_CHARS
    for line_no, line in enumerate(str(text).splitlines() or [str(text)], start=1):
        for col, ch in enumerate(line, start=1):
            if ch in chars:
                issues.append(Issue(
                    "ERROR", path, f"forbidden {chars[ch]}",
                    char=ch, line=line_no, col=col, excerpt=line.strip()[:80],
                ))
    return issues


def lexicon_issues(path, text, allow_cta=False):
    issues = []
    flat = collapse(text)
    for pattern, why in LEXICON_ERRORS:
        m = re.search(pattern, flat)
        if m:
            issues.append(Issue("ERROR", path, f"{why}: «{m.group(0)}»"))
    for pattern, why in LEXICON_WARNINGS:
        m = re.search(pattern, flat)
        if m:
            issues.append(Issue("WARN", path, f"{why}: «{m.group(0)}»"))
    if not allow_cta:
        for line in lines_of(text):
            for pattern, why in SECOND_CTA_PATTERNS:
                m = re.search(pattern, line)
                if m:
                    issues.append(Issue("ERROR", path, f"second CTA ({why}): «{m.group(0)}»", excerpt=line[:80]))
    return issues


# Yarin, 8 Oct 2026: "never say its made with ai ever again, its super clear and ruins trust and engagement"
AI_MENTION_RE = re.compile(r"(?<![A-Za-z])A\.?I(?![A-Za-z])|בינה\s+מלאכותית|נוצר[הו]?\s+(?:ב|על\s+ידי|בעזרת)\s*(?:AI|בינה)|\bai\b", re.I)


def audience_text_issues(path, text, require_hebrew=True, allow_cta=False, legacy=False):
    """All hard rules for one piece of audience facing Hebrew (legacy: the punctuation rule before PUNCTUATION_FROM)."""
    issues = []
    if not isinstance(text, str) or not text.strip():
        return [Issue("ERROR", path, "must be a non empty string")]
    if require_hebrew and not HEBREW_RE.search(text):
        issues.append(Issue("ERROR", path, "must contain Hebrew"))
    issues.extend(forbidden_char_issues(path, text, legacy=legacy))
    issues.extend(lexicon_issues(path, text, allow_cta=allow_cta))
    if AI_MENTION_RE.search(text):
        issues.append(Issue("ERROR", path, "mentions AI; carousels never say the images or copy are AI made (Yarin, 8 Oct 2026)", excerpt=AI_MENTION_RE.search(text).group(0)))
    for i, line in enumerate(lines_of(text), start=1):
        n = len(words(line))
        if n > LINE_MAX_WORDS:
            issues.append(Issue("ERROR", path, f"line {i} has {n} words; keep one short thought per line (max {LINE_MAX_WORDS})", excerpt=line[:80]))
        first_strong = next((c for c in line if unicodedata.bidirectional(c) in ("L", "R", "AL")), None)
        if first_strong is not None and unicodedata.bidirectional(first_strong) == "L":
            issues.append(Issue("WARN", path, f"line {i} starts with a Latin word; start lines with Hebrew so RTL punctuation stays in place", excerpt=line[:80]))
    if LATIN_RE.search(text):
        issues.append(Issue("WARN", path, "contains Latin letters; prefer Hebrew on slides and check RTL in the render"))
    if len(EMOJI_RE.findall(text)) > 1:
        issues.append(Issue("WARN", path, "more than one emoji"))
    return issues


CTA_REQUIRED = [
    (r"כתב[וי]", "כתבו or כתבי"),
    (r"בתגובות", "בתגובות"),
    (r"קישור", "קישור"),
    (r"ספר", "ספר"),
    (r"גיבור", "הגיבור or הגיבורה"),
]
CTA_WRITE_RE = r"כתב[וי]"
CTA_CODE_QUOTE = '"'   # the code word is always written inside these: כתבו "גן" בתגובות


def quote_code_word(cta):
    """כתבו גן / כתבו ״גן״ / כתבו 'גן' -> כתבו "גן". Used by the editor so a typed CTA always comes out right."""
    return re.sub(CTA_WRITE_RE.join(["(", ")"]) + r"\s*[״\"׳'“”]?([\u05D0-\u05EA]{2,10})[״\"׳'“”]?(?=\s|$)",
                  lambda m: f'{m.group(1)} "{m.group(2)}"', cta, count=1)
# Who the copy talks to (Yarin, 7 Oct 2026): mom (feminine singular) or both parents (plural), never dad.
ADDRESSEES = {"mom": "לאמא", "parents": "לשני ההורים"}
CTA_FORMS = {
    "mom": {"verb": "כתבי", "get": "וקבלי", "owner": "שלך"},
    "parents": {"verb": "כתבו", "get": "וקבלו", "owner": "שלכם"},
}
# "אמא ואבא" is talking to both parents, which is allowed; only dad on his own is not (Yarin, 8 Oct 2026)
PARENT_PAIR_RE = re.compile(r"(?<![\u05D0-\u05EA])(?:ו|ש|ל|כש)?(?:אמא\s+ואבא|אבא\s+ואמא)(?![\u05D0-\u05EA])")
DAD_RE = re.compile(r"(?<![\u05D0-\u05EA])(?:ו|ש|ה|ל|ב|מ|כש)?(?:אבא|אבאל'ה)(?![\u05D0-\u05EA])|(?<![\u05D0-\u05EA])(?:ו)?אתה(?![\u05D0-\u05EA])|(?<![\u05D0-\u05EA])בוא\s+נ")
MOM_ADDRESS_RE = re.compile(r"(?<![\u05D0-\u05EA])(?:ו|ש|כש)?(?:את|לך|שלך|אותך|איתך|עלייך|אלייך|בואי|תגידי|תקריאי|תני|כתבי)(?![\u05D0-\u05EA])")
PARENTS_ADDRESS_RE = re.compile(r"(?<![\u05D0-\u05EA])(?:ו|ש|כש)?(?:אתם|לכם|שלכם|אתכם|איתכם|עליכם|לפניכם|אצלכם|בשבילכם|תגידו|תבואו|כתבו|בואו|נסו|תנו)(?![\u05D0-\u05EA])")


def cta_issues(path, cta, code_word, legacy=False):
    issues = audience_text_issues(path, cta, allow_cta=True, legacy=legacy)
    flat = collapse(cta)
    for pattern, label in CTA_REQUIRED:
        if not re.search(pattern, flat):
            issues.append(Issue("ERROR", path, f"CTA must keep the brief's idea and include «{label}»"))
    # Yarin, 8 Oct 2026: the code word always sits inside quotation marks, כתבו "גן" בתגובות
    if code_word and not re.search(CTA_WRITE_RE + r'\s*"' + re.escape(code_word) + r'"(\s|$)', flat):
        issues.append(Issue("ERROR", path, f'CTA must read כתבו or כתבי "{code_word}" with the code word inside straight quotation marks, right after the verb'))
    n = len(words(flat))
    if n > CTA_SLIDE_MAX_WORDS:
        issues.append(Issue("ERROR", path, f"CTA has {n} words (max {CTA_SLIDE_MAX_WORDS})"))
    for pattern, why in SECOND_CTA_PATTERNS:
        if re.search(pattern, flat):
            issues.append(Issue("ERROR", path, f"CTA contains a second CTA ({why})"))
    return issues


# ---------------------------------------------------------------------------
# Child names (carousel/carousel-pipeline/names.md)
# ---------------------------------------------------------------------------

def load_names(path=NAMES):
    """{'boy': [...], 'girl': [...]} from the two tables in names.md."""
    names = {"boy": [], "girl": []}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] in names:
            names[cells[0]].extend(n.strip() for n in cells[1].split("·") if n.strip())
    return names


def audience_lines(version):
    """All audience text of one option except the CTA slide body and caption's last line (fixed CTA wording)."""
    out = []
    for s in version.get("slides", []):
        out.append(("slide", s.get("number"), "headline", s.get("headline", "")))
        out.append(("slide", s.get("number"), "body", s.get("body", "")))
    return out


# ---------------------------------------------------------------------------
# Hook bank (carousel/carousel-pipeline/hook-bank.md)
# ---------------------------------------------------------------------------

HOOK_SCORE_KEYS = ("specific", "feeling", "honest_gap", "short_spoken", "filters", "not_an_ad")
HOOK_MIN_SCORE = 9
HOOK_RECENT_PACKS = 3
# Carousel Machine (Yarin, 10 Oct 2026: "focus heavily on clickbaity hooks"): curiosity openers are wanted when the
# carousel pays them off, so «לא תאמינו», «הסוד ש», «חייבת לדעת», «מה שאף אחד לא מספר» and «תפסיקי» (about an
# action, with the replacement in the carousel) are no longer banned. What stays banned is what is weak (lecture
# and generic openers, hype with no gap) or what hurts the parent (shame, guilt, fear, threats).
HOOK_BANNED = [
    (r"חובה לראות", "hype with no gap"),
    (r"האם ידעתם", "trivia opener"), (r"בואו נדבר על", "lecture opener"), (r"היום נדבר", "lecture opener"),
    (r"כל מה שצריך לדעת", "generic opener"), (r"המדריך המלא", "generic opener"),
    (r"אתם עושים את זה לא נכון", "guilt opener"), (r"הטעות שכל ההורים", "guilt opener"),
    # Added 8 Oct 2026 (hook strategy research): shame, fear, fake urgency and "you are doing it wrong" openers
    (r"לפני שיהיה מאוחר", "fear and urgency"),
    (r"את עושה את זה לא נכון", "guilt opener"), (r"הורים טובים (?:לא|תמיד)", "shame opener"),
    (r"(?<![א-ת])אם (?:את|אתם) לא(?![א-ת])", "conditional threat"),
]
HOOK_SPECIFIC_RE = re.compile(r"\d|[״\"?]|בוקר|צהריים|ערב|לילה|שער|גן|כיתה|בית|שינה|מים|סיפור|מיטה|אמבטיה|ארוחה|מדרגות|אוטו|שבוע|חגים|גיל|אמא|אבא")

# Evidence labels for hook formulas (hook strategy research, 8 Oct 2026). Kept separate on purpose:
# "trendy", "frequently observed", "high performing" and "caused better performance" are different things.
EVIDENCE_LABELS = {
    "platform_supported": "current first-party Instagram or Meta guidance",
    "external_performance_pattern": "repeated in several relevant posts with visible performance evidence",
    "current_trend": "appearing repeatedly in recent content, not shown to cause performance",
    "research_supported_mechanism": "credible behavioural, attention or communication research",
    "lumebook_hypothesis": "a promising adaptation that still needs LumeBook testing",
    "lumebook_validated": "supported by LumeBook's own results (hook-results.json)",
}
# The psychological job a hook does. Rotation spreads these across the six options.
MECHANISMS = {
    "recognition": "ההורה מזהה רגע מדויק מהבית שלו",
    "perspective_shift": "רואים את הרגע מהצד של הילד",
    "honest_curiosity": "שאלה אמיתית שהקרוסלה עונה עליה",
    "reassurance": "נרמול שמוריד בושה או דאגה",
    "practical_utility": "משהו לעשות מחר",
    "reframe": "פירוש אחר להתנהגות מוכרת",
    "narrative_tension": "סיפור שנעצר ברגע לא פתור",
    "anticipation": "רגע התפתחותי או עונתי שמתקרב",
    "identity_filter": "פונה בדיוק למי שנמצאת במצב הזה",
}
# The surface form of slide 1. Two options with the same shape read like rewrites of each other.
SENTENCE_SHAPES = {
    "address": "פנייה (אמא / אמא ואבא)",
    "quote": "משפט במירכאות",
    "time_place": "שעה או מקום ואז מה קורה",
    "question": "שאלה",
    "contrast_pair": "במקום X / Y",
    "negation": "לא X / אלא Y",
    "numbered": "מספר",
    "identity_label": "לאמא של",
    "statement": "אמירה",
    "story_open": "פתיחה של סיפור",
    "ages_sequence": "גיל אחרי גיל",
    "just_so_you_know": "רק שתדעי",
    "imagine": "דמייני ש",
    "command": "ציווי על פעולה אחת (אל / תפסיקי)",
    "secret": "סוד או משהו שלא מספרים",
}
# Slide 2 moves. Slide 2 must work as a first slide on its own (Instagram may re-show a carousel from slide 2).
SLIDE2_MOVES = {
    "zoom_in": "אותו רגע מקרוב יותר",
    "other_side": "מעבר בין הצד של הילד לצד של ההורה",
    "name_trigger": "מה הפעיל את זה עכשיו",
    "contrast": "ניגוד שמבקש הסבר",
    "promise": "מה מקבלים בהמשך",
    "first_answer": "חצי תשובה שעומדת לבד",
    "scene_restart": "הסצנה מסופרת מחדש במשפט אחד",
    "same_template": "עוד מופע של אותה תבנית",
}
# Words that make slide 2 lean on slide 1. A slide 2 headline must not open with them.
SLIDE2_LEANS_ON_SLIDE1_RE = re.compile(r"^(?:ואז|אז|אבל|כי|וגם|גם|ולכן|לכן|ואם|זה|זאת|ככה|הנה|ובגלל|ועוד|וזה|וזאת)(?![א-ת])")
HOOK_RESULTS = PIPELINE / "hook-results.json"
TREND_REVIEW_MAX_DAYS = 120  # a current_trend formula must be re-checked at least this often
# Hypotheses, not findings: how many comparable LumeBook posts a formula needs before it may be called validated.
VALIDATE_MIN_POSTS = 6
VALIDATE_MIN_TOPICS = 3
VALIDATE_MIN_REACH_PER_POST = 300

# The nightly hook slate (hook-bank.md, "Nightly hook slate"): 6 kid and 6 expert candidates, scored 0-2.
SLATE_SIZE = 6
SLATE_SCORE_KEYS = (
    "stopping_power", "specificity", "parent_relevance", "honest_curiosity", "emotional_truth",
    "swipe_promise", "usefulness", "topic_fit", "lumebook_fit", "freshness",
)
SLATE_NO_ZERO = ("honest_curiosity", "emotional_truth", "topic_fit", "lumebook_fit")
SLATE_MIN_SCORE = 14  # of 20; a LumeBook hypothesis, revisit when hook-results.json has data
SLATE_FAIL_CHECKS = ("clickbait", "unsupported_claim", "unfulfilled_promise", "blames_parent")
SLATE_MIN_FAMILIES = 3     # per direction, among the 6 candidates
SLATE_MIN_MECHANISMS = 3   # per direction, among the 6 candidates
PACK_MIN_MECHANISMS = 4    # across the 6 final options
PACK_MIN_SHAPES = 4        # across the 6 final options
PACK_MIN_SLIDE2_MOVES = 3  # across the 6 final options
PACK_MIN_AWARENESS = 2     # across the 6 final options
NEAR_DUPLICATE = 0.6       # word overlap (Jaccard) at which two hooks count as rewrites of each other
_STOP_WORDS = {"את", "של", "על", "עם", "לא", "זה", "זאת", "אני", "הוא", "היא", "אתם", "לי", "לך", "כל", "גם", "רק", "עוד", "אז", "כי", "אבל", "מה", "איך"}


def _bank_rows(path):
    """(section heading, cells) for every table row whose first cell is a backticked id."""
    section = ""
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = re.fullmatch(r"`([a-z0-9_-]+)`", cells[0]) if cells else None
        if m:
            yield section, m.group(1), cells


def _plus_list(cell):
    return [x.strip().strip("`") for x in cell.split("+") if x.strip()]


def load_hook_bank(path=HOOK_BANK):
    """Formulas table (| `id` | family | direction | formula | example | source |) merged with the
    Evidence and rotation table (| `id` | evidence | mechanism | shape | slide2 | payoff | researched | review_by |)."""
    rows, meta = {}, {}
    for section, fid, cells in _bank_rows(path):
        if section.startswith("formulas") and len(cells) >= 6:
            rows[fid] = {"id": fid, "family": cells[1], "direction": cells[2], "formula": cells[3], "example": cells[4], "source": cells[5]}
        elif section.startswith("evidence and rotation") and len(cells) >= 8:
            meta[fid] = {
                "evidence": _plus_list(cells[1]), "mechanisms": _plus_list(cells[2]), "shape": cells[3].strip("`"),
                "slide2_moves": _plus_list(cells[4]), "payoff": cells[5], "researched": cells[6], "review_by": cells[7],
            }
    for fid, row in rows.items():
        row.update(meta.get(fid, {"evidence": [], "mechanisms": [], "shape": "", "slide2_moves": [], "payoff": "", "researched": "", "review_by": ""}))
        row["has_meta"] = fid in meta
    return rows


def bank_orphans(path=HOOK_BANK):
    """Ids in the Evidence and rotation table that have no formula row."""
    formulas = {fid for section, fid, cells in _bank_rows(path) if section.startswith("formulas")}
    return sorted({fid for section, fid, cells in _bank_rows(path) if section.startswith("evidence and rotation")} - formulas)


def formula_status(formula, today=None):
    """current, review_due (past review_by) or expired (a current_trend past review_by: needs revalidation)."""
    today = today or now_local().date()
    try:
        review_by = parse_date(formula.get("review_by", ""))
    except ValueError:
        return "review_due"
    if today <= review_by:
        return "current"
    return "expired" if "current_trend" in formula.get("evidence", []) else "review_due"


def load_hook_results(path=HOOK_RESULTS):
    path = Path(path)
    if not path.exists():
        return {"posts": []}
    return json.loads(path.read_text(encoding="utf-8"))


def formula_observations(formula_id, results):
    """LumeBook's own published posts that used this formula and have a 7-day read."""
    posts = [p for p in results.get("posts", []) if p.get("hook_formula") == formula_id and isinstance(p.get("reach"), int)]
    return {
        "posts": len(posts),
        "topics": len({p.get("topic_id") for p in posts}),
        "enough_reach": sum(1 for p in posts if p["reach"] >= VALIDATE_MIN_REACH_PER_POST),
        "promotion_note": next((p.get("promotion_note") for p in posts if p.get("promotion_note")), ""),
    }


def bank_issues(bank, results=None, orphans=None):
    """Problems with hook-bank.md itself: missing evidence rows, unknown labels, a 'validated' label without data."""
    issues = []
    results = results if results is not None else load_hook_results()
    for fid in (orphans if orphans is not None else bank_orphans()):
        issues.append(Issue("ERROR", f"hook-bank/{fid}", "has an evidence row but no formula row"))
    for fid, f in bank.items():
        p = f"hook-bank/{fid}"
        if f["family"] not in HOOK_FAMILIES:
            issues.append(Issue("ERROR", p, f"unknown family {f['family']}"))
        if f["direction"] not in ("kid", "expert", "both"):
            issues.append(Issue("ERROR", p, f"direction must be kid, expert or both (got {f['direction']})"))
        if not f.get("has_meta"):
            issues.append(Issue("ERROR", p, "needs a row in the Evidence and rotation table"))
            continue
        for label in f["evidence"] or ["(none)"]:
            if label not in EVIDENCE_LABELS:
                issues.append(Issue("ERROR", p, f"unknown evidence label {label}"))
        for m in f["mechanisms"] or ["(none)"]:
            if m not in MECHANISMS:
                issues.append(Issue("ERROR", p, f"unknown mechanism {m}"))
        if f["shape"] not in SENTENCE_SHAPES:
            issues.append(Issue("ERROR", p, f"unknown sentence shape {f['shape']}"))
        for mv in f["slide2_moves"] or ["(none)"]:
            if mv not in SLIDE2_MOVES:
                issues.append(Issue("ERROR", p, f"unknown slide 2 move {mv}"))
        try:
            researched, review_by = parse_date(f["researched"]), parse_date(f["review_by"])
            if "current_trend" in f["evidence"] and (review_by - researched).days > TREND_REVIEW_MAX_DAYS:
                issues.append(Issue("ERROR", p, f"a current_trend formula must be re-checked within {TREND_REVIEW_MAX_DAYS} days of research"))
        except ValueError:
            issues.append(Issue("ERROR", p, "researched and review_by must be YYYY-MM-DD dates"))
        if "lumebook_validated" in f["evidence"]:
            obs = formula_observations(fid, results)
            if obs["posts"] < VALIDATE_MIN_POSTS or obs["topics"] < VALIDATE_MIN_TOPICS or obs["enough_reach"] < VALIDATE_MIN_POSTS or not obs["promotion_note"]:
                issues.append(Issue("ERROR", p, f"lumebook_validated needs LumeBook's own results in hook-results.json: at least {VALIDATE_MIN_POSTS} posts with {VALIDATE_MIN_REACH_PER_POST}+ reach across {VALIDATE_MIN_TOPICS} topics and a written promotion_note (has {obs['posts']} posts, {obs['topics']} topics)"))
    return issues


_NAME_SET = None


def hook_words(text):
    """Content words of a hook, for near-duplicate checks (names and small function words removed)."""
    global _NAME_SET
    if _NAME_SET is None:
        _NAME_SET = {n for ns in load_names().values() for n in ns}
    names = _NAME_SET
    out = set()
    for w in words(collapse(text).replace("״", " ").replace('"', " ").replace("?", " ")):
        w = w.strip()
        if not w or w in _STOP_WORDS or w in names:
            continue
        out.add(w)
    return out


def overlap(a, b):
    wa, wb = hook_words(a), hook_words(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def hook_issues(path, version, direction_id, bank, story=False):
    """The option's declared hook formula, gap, payoff slide and score, plus clickbait checks on slide 1.
    story: a story pack, whose payoff can be any slide from 2 to the one before the CTA."""
    issues = []
    hook = version.get("hook") or {}
    formula = bank.get(hook.get("formula"))
    if not formula:
        return [Issue("ERROR", f"{path}/hook/formula", f"{hook.get('formula')!r} is not in hook-bank.md")]
    if formula["family"] != version.get("hook_family"):
        issues.append(Issue("ERROR", f"{path}/hook_family", f"formula {formula['id']} belongs to family {formula['family']}"))
    if formula["direction"] not in ("both", direction_id):
        issues.append(Issue("ERROR", f"{path}/hook/formula", f"{formula['id']} is a {formula['direction']} formula"))
    score = hook.get("score") or {}
    values = [score.get(k) for k in HOOK_SCORE_KEYS]
    if any(not isinstance(v, int) or not 0 <= v <= 2 for v in values):
        issues.append(Issue("ERROR", f"{path}/hook/score", f"score each of {', '.join(HOOK_SCORE_KEYS)} from 0 to 2"))
    else:
        total = sum(values)
        if total < HOOK_MIN_SCORE or 0 in values:
            weak = [k for k in HOOK_SCORE_KEYS if score.get(k) == 0]
            issues.append(Issue("ERROR", f"{path}/hook/score", f"hook scores {total} of 12{' with 0 on ' + ', '.join(weak) if weak else ''}; rewrite it (needs {HOOK_MIN_SCORE}+ and no zero)"))
    payoff = hook.get("payoff_slide")
    n_slides = len(version.get("slides") or [])
    if story:
        low, high = 2, max(2, n_slides - 1)
    else:
        low, high = (EXPLAIN_SLIDE, RECAP_SLIDE) if n_slides == TEN_SLIDE_COUNT else (INSIGHT_SLIDES[0], RESOLUTION_SLIDE)
    if not isinstance(payoff, int) or not low <= payoff <= high:
        issues.append(Issue("ERROR", f"{path}/hook/payoff_slide", f"say which slide ({low} to {high}) answers the hook"))
    if len(str(hook.get("gap", "")).strip()) < 8:
        issues.append(Issue("ERROR", f"{path}/hook/gap", "state the question the hook opens"))
    slides = version.get("slides") or []
    if slides:
        text = collapse(slides[0].get("headline", "") + " " + slides[0].get("body", ""))
        for pattern, why in HOOK_BANNED:
            if re.search(pattern, text):
                issues.append(Issue("ERROR", f"{path}/slide-1", f"banned hook opener ({why}): «{re.search(pattern, text).group(0)}»"))
        if not HOOK_SPECIFIC_RE.search(text):
            issues.append(Issue("WARN", f"{path}/slide-1", "hook has no specific moment, time, age, place or quote"))
    return issues


# Carousels never name the brand or a catalogue book (Yarin, 7 Oct 2026): slide 7 only hints that a book
# where the child is the hero is one possible tool, and the comment CTA does the rest.
BRAND_RE = re.compile(r"לומי?בוק|lume\s*-?\s*book", re.IGNORECASE)
QUOTED_RE = re.compile(r"[״\"“”]([^״\"“”]{2,40})[״\"“”]")


def catalogue_titles(bank=None):
    """Book titles listed in topic-bank.md, plus their short form before ' של ' (the personalised cover drops the name)."""
    bank = bank if bank is not None else load_topic_bank()
    titles = set()
    for t in bank:
        for title in t.get("books", "").split("·"):
            title = title.strip()
            if not title or title.lower().startswith("check") or "(" in title:
                continue
            titles.add(title)
            if " של " in title:
                titles.add(title.split(" של ")[0].strip())
    return titles


def brand_issues(path, text, titles):
    issues = []
    m = BRAND_RE.search(text)
    if m:
        issues.append(Issue("ERROR", path, f"carousels never name the brand: «{m.group(0)}». Hint at a book where the child is the hero instead"))
    for q in QUOTED_RE.findall(text):
        if q.strip() in titles:
            issues.append(Issue("ERROR", path, f"carousels never name a catalogue book: «{q.strip()}»"))
    for title in titles:
        msg = f"carousels never name a catalogue book: «{title}»"
        if " של " in title and title in text and not any(i.message == msg for i in issues):
            issues.append(Issue("ERROR", path, msg))
    return issues


# Code words taken by competitors. Source: research/carousel-research/lumebook-carousel-research.html
# (artifact Rkt3DeuC86z23WcAbR7VHW, 6 Oct 2026): MeBook creator reels already say "comment ספר for my discount code".
# Yarin, 10 Oct 2026: "i want the cta word to always be לומי". One fixed comment word for every kid and expert option, so
# the 14 day rotation of code words ends for packs generated from FIXED_CODE_WORD_FROM on (older packs keep the old rule).
CTA_CODE_WORD = "לומי"
FIXED_CODE_WORD_FROM = "2026-10-10T22:00"


def fixed_code_word_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= FIXED_CODE_WORD_FROM


BLOCKED_CODE_WORDS = {"ספר": "MeBook creators already use the comment word ספר; pick a milestone word instead"}


def code_word_issues(path, code_word):
    if not isinstance(code_word, str) or not re.fullmatch(r"[א-ת]{2,10}", code_word or ""):
        return [Issue("ERROR", path, "code word must be one short Hebrew word, 2 to 10 letters, no spaces or marks")]
    if code_word in BLOCKED_CODE_WORDS:
        return [Issue("ERROR", path, BLOCKED_CODE_WORDS[code_word])]
    return []


# ---------------------------------------------------------------------------
# Two topics a day and the save and share CTA (Yarin, 24 Oct 2026, after the carousel audit in research/carousel-audit/):
# "Keep the child-voice numbered lists, on 2 topics that have a best-selling book (6 versions for each day (3 options for
# each) so i can choose the strongest one)" and "change the cta to save the post and share to a parent who would agree".
# Packs generated from DAILY_PAIR_FROM on have format two_topics: `topics` holds the day's two topics (each tied to a
# best-selling book, topic-bank.md "Best-selling books"), `topic` repeats the first for older readers, and one kid
# direction holds six options, kid-1 to kid-3 on topics[0] and kid-4 to kid-6 on topics[1] (each records `topic_id`).
# The CTA asks to save the post and send it to a mom who will relate; there is no comment word any more.
# Older packs keep their rules.
# ---------------------------------------------------------------------------
DAILY_PAIR_FROM = "2026-10-24T18:00"
PAIR_FORMAT = "two_topics"
PAIR_LANES = (("a", ("kid-1", "kid-2", "kid-3")), ("b", ("kid-4", "kid-5", "kid-6")))   # slate key and options per topic
PAIR_OPTION_IDS = tuple(o for _, ids in PAIR_LANES for o in ids)
PAIR_TOPIC_COOLDOWN_PACKS = 3      # a topic of a two-topic pack is not used again in the next 3 packs (days)
PAIR_BOOK_MAX_IN_BATCH = 2         # one best-selling book feeds at most two of a week's 14 topics


def daily_pair_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= DAILY_PAIR_FROM


def is_pair_pack(pack):
    return (pack or {}).get("format") == PAIR_FORMAT


# Older packs switched to the new last slide (Yarin, 24 Oct 2026: "switch this week's 42 carousels to the new last slide:
# אפשר לעזור להם גם בסיפור אישי plus the save and share CTA, and let the validator accept it") carry cta_style save_share.
# They keep their one topic and kid and expert directions; only the CTA rules change.
SAVE_SHARE_STYLE = "save_share"


def save_share_applies(pack):
    if book_link_applies(pack):
        return False
    """No comment word: the save and share CTA and the save for later CTA that replaced it."""
    return daily_pair_applies(pack) or (pack or {}).get("cta_style") in (SAVE_SHARE_STYLE, SAVE_LATER_STYLE) or save_later_applies(pack)


# Yarin, 24 Oct 2026 (evening): "remove אפשר לעזור להם גם בסיפור אישי from the cta" and "i want the cta to change,
# 'תשמרו את הפוסט לפעם הבאה שX'". Slide 10 is only the CTA: its headline is the save line (drawn as the yellow button with
# the save icon) and its body says when the post will be needed again, X being the moment the carousel is about
# (לפעם הבאה שהיא מפחדת מרעמים). Mom: תשמרי, both parents: תשמרו. Packs from SAVE_LATER_FROM have it; the week of
# 25 to 31 Oct 2026 was moved to it the same evening (cta_style save_for_later).

# Yarin, 28 Oct 2026: "make this carousels about the kids sound like the kid is telling his parents". In a kid option
# everything a parent reads is the child talking to them: slides 1 to 9, the caption and its bridge line. No narrator
# who speaks about the child in the third person ("גם את רוצה לעזור לרוני", "מה נדב מבקש מכם", "ילדה שאומרת"). The CTA
# slide keeps the save for later wording, which refers to the child (הוא/היא). Packs from TO_PARENTS_FROM, or with
# voice_style "to_parents" (the week of 28 to 31 Oct 2026 was moved to it the same day).
TO_PARENTS_STYLE = "to_parents"
TO_PARENTS_FROM = "2026-10-28T12:00"
NARRATOR_RE = re.compile(r"(?:רוצ(?:ה|ים) לעזור ל|מבקש(?:ת)? מ(?:כם|ך|את)|עוזר(?:ת)? ל(?:ילד|ילדה|הוא|היא)|ילד(?:ה)? ש(?:אומר|צריך|מבקש|רוצה))")


def to_parents_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= TO_PARENTS_FROM or (pack or {}).get("voice_style") == TO_PARENTS_STYLE


def to_parents_issues(p, v):
    """Narrator leaks in a kid option: third person about the child on slides 1 to 9 or in the caption (before the CTA
    line), a caption with no first person in it, or the child's own name outside a quoted sentence."""
    issues = []
    name = v.get("child_name", "")
    slides = v.get("slides") or []
    # slides 1 to 9 of a 10 slide pack; every slide before the CTA of a story option (9 to 12 slides)
    for n, s in enumerate(slides[:max(9, len(slides) - 1)], 1):
        text = (s.get("headline", "") + " " + s.get("body", ""))
        if NARRATOR_RE.search(text):
            issues.append(Issue("ERROR", f"{p}/slide-{n}", "the child is talking to the parents (Yarin, 28 Oct 2026): no narrator speaking about the child in the third person, say it as the child (תעזרי לי, תעזרו לי)"))
    cta = str(v.get("cta", "")).replace("\n", " ").strip()
    body = [ln for ln in str(v.get("caption", "")).strip().split("\n") if ln.strip()]
    tail = cta_tail_lines(v)   # the book link CTA is the caption's last two lines
    if body and cta and " ".join(" ".join(body[-tail:]).split()) == " ".join(cta.split()):
        body = body[:-tail]
    caption = "\n".join(body)
    if NARRATOR_RE.search(caption) or (name and re.search(r"(?<![\u05D0-\u05EA״])" + re.escape(name) + r"(?![\u05D0-\u05EA])", caption.replace("״", "\""))):
        issues.append(Issue("ERROR", f"{p}/caption", "the caption is the child talking to the parents (Yarin, 28 Oct 2026): first person, no narrator and no third person name"))
    elif sum(1 for ln in body if FIRST_PERSON_RE.search(ln) or re.search(r"(?:^|\s)ת[\u05D0-\u05EA]{2,}|(?:^|\s)(?:תני|תנו|תעזר)", ln)) < 3:
        issues.append(Issue("ERROR", f"{p}/caption", "the caption is the child talking to the parents (Yarin, 28 Oct 2026): at least 3 of its lines say I or ask the parents for something (תשבי איתי, תנו לי)"))
    return issues

SAVE_LATER_STYLE = "save_for_later"
SAVE_LATER_FROM = "2026-10-24T21:00"
SAVE_LATER_FORMS = {
    "mom": {"save": "תשמרי את הפוסט", "text": "תשמרי את הפוסט\nלפעם הבאה ש..."},
    "parents": {"save": "תשמרו את הפוסט", "text": "תשמרו את הפוסט\nלפעם הבאה ש..."},
}
SAVE_LATER_RE = re.compile(r"^(?:ת?שמר[וי])\s+את\s+הפוסט\s+לפעם\s+הבאה\s+ש[\u05D0-\u05EA״\"]")


def save_later_applies(pack):
    if book_link_applies(pack):
        return False
    return str((pack or {}).get("generated_at", ""))[:16] >= SAVE_LATER_FROM or (pack or {}).get("cta_style") == SAVE_LATER_STYLE


def save_later_slide(cta):
    """(headline, body) of slide 10 for a save for later CTA: the save line, then the rest on one line, or broken after
    לפעם הבאה so the moment (ש...) stays whole, or in two even lines when even that is too long."""
    w = collapse(cta).split()
    head, rest = " ".join(w[:3]), w[3:]
    if len(" ".join(rest)) <= 32 or len(rest) < 4:
        return head, " ".join(rest)
    clause = rest[2:]
    if rest[:2] == ["לפעם", "הבאה"] and len(" ".join(clause)) <= 30:
        return head, "לפעם הבאה\n" + " ".join(clause)
    cut = min(range(2, len(rest) - 1), key=lambda i: abs(len(" ".join(rest[:i])) - len(" ".join(rest[i:]))))
    return head, " ".join(rest[:cut]) + "\n" + " ".join(rest[cut:])


# The moment after לפעם הבאה ש is the topic's everyday situation, never one scene of the carousel ("too specific", "doesnt
# sound natural"), and it is always about the child (Yarin, 24 Oct 2026: "always refer to the kid"): הוא or היא, לו or לה,
# אותו or אותה as the option's child, or the child's name. The same situation for every option on a topic.
SAVE_LATER_MOMENT_MAX_WORDS = 5
KID_REF = {
    "boy": re.compile(r"(?<![\u05D0-\u05EA])(?:ש|כש|ו)?(?:הוא|לו|אותו|שלו|ממנו|איתו|אליו|עליו|בשבילו)(?![\u05D0-\u05EA])"),
    "girl": re.compile(r"(?<![\u05D0-\u05EA])(?:ש|כש|ו)?(?:היא|לה|אותה|שלה|ממנה|איתה|אליה|עליה|בשבילה)(?![\u05D0-\u05EA])"),
}



# ---------------------------------------------------------------------------
# The book link CTA (Yarin, 30 Oct 2026, after learning @lotem_lerner's CTAs and captions: "i want the cta to point to a
# book that might help them with x problem and then theyll get a link to the website"; the wording and the booklet the
# same afternoon: "אפשר גם לעזור להם עם X בעזרת ספר מותאם אישית / תכתבו X ואשלח לכם קישור להכנת הספר", then "great
# implement in novembers batch"). An option (or a whole pack) with cta_style "book_link" ends on two sentences: the
# problem of the carousel and a personalised book, then one topic word in the comments for the link in the DM. Never the
# brand or a catalogue title. The word is the topic's own (מוצץ, אח), the same on every book link option of a topic, in
# the option's `code_word`. Slide 10 is only the CTA over the open booklet (`booklet`, story-format.md section 7).
# ---------------------------------------------------------------------------
BOOK_LINK_STYLE = "book_link"
BOOK_LINK_FORMS = {
    "mom": {"ask": "תכתבי", "send": "ואשלח לך", "text": "אפשר גם לעזור להם עם ... בעזרת ספר מותאם אישית.\nתכתבי \"X\" ואשלח לך קישור להכנת הספר"},
    "parents": {"ask": "תכתבו", "send": "ואשלח לכם", "text": "אפשר גם לעזור להם עם ... בעזרת ספר מותאם אישית.\nתכתבו \"X\" ואשלח לכם קישור להכנת הספר"},
}
BOOK_LINK_RE = re.compile(r"^אפשר\s+גם\s+לעזור\s+להם\s+עם\s")
BOOK_LINK_PROBLEM_MAX_WORDS = 3     # the first sentence is one caption line of at most LINE_MAX_WORDS words
BOOK_LINK_CTA_MAX_WORDS = 20
BOOK_LINK_EARLY_RE = re.compile(r"תכתב[וי]\s*[\"״]|הגיב[וי]\s*[\"״]|כתב[וי]\s*[\"״]|בתגובות|ואשלח|קישור|לינק|ספר מותאם אישית")
_BOOK_LINK_PARTS = re.compile(r"^(אפשר גם לעזור להם עם (.+?) בעזרת ספר מותאם אישית)[.]\s*(תכתב[וי])\s+[\"״]([^\"״]+)[\"״]\s+(ואשלח\s+\S+)\s+קישור להכנת הספר[.]?$")


def book_link_applies(pack, version=None):
    """The pack's cta_style, or one option's own (the 14 produced November carousels were moved one by one)."""
    return (pack or {}).get("cta_style") == BOOK_LINK_STYLE or (version or {}).get("cta_style") == BOOK_LINK_STYLE


def book_link_parts(cta):
    """{problem, ask, word, send} of a book link CTA, or {} when the text has another shape."""
    m = _BOOK_LINK_PARTS.match(collapse(cta))
    return {"sentence": m.group(1), "problem": m.group(2), "ask": m.group(3), "word": m.group(4), "send": m.group(5)} if m else {}


def book_link_cta(problem, word, addressee):
    """The CTA text: two sentences on two lines (the caption ends with both)."""
    f = BOOK_LINK_FORMS["mom" if addressee == "mom" else "parents"]
    return f"אפשר גם לעזור להם עם {problem} בעזרת ספר מותאם אישית.\n{f['ask']} \"{word}\" {f['send']} קישור להכנת הספר"


def book_link_slide(cta):
    """(headline, body) of the last slide: the first sentence on three lines, then the ask and the link promise."""
    p = book_link_parts(cta)
    if not p:
        return collapse(cta), ""
    return (f"אפשר גם לעזור להם\nעם {p['problem']}\nבעזרת ספר מותאם אישית.",
            f"{p['ask']} \"{p['word']}\"\n{p['send']} קישור להכנת הספר")


def book_link_keyword(cta):
    return book_link_parts(cta).get("word", "")


def book_link_early_issues(path, text):
    """The book line, the word and the link promise belong to the last slide and the caption's last two lines only."""
    out = []
    for line in lines_of(text):
        m = BOOK_LINK_EARLY_RE.search(line)
        if m:
            out.append(Issue("ERROR", path, f"the book link CTA appears only on the last slide and as the caption's last two lines: «{m.group(0)}»", excerpt=line[:80]))
    return out


def book_link_cta_issues(path, cta, addressee, code_word="", legacy=False):
    """«אפשר גם לעזור להם עם <problem> בעזרת ספר מותאם אישית. תכתבו "<word>" ואשלח לכם קישור להכנת הספר» in the
    addressee's form (mom: תכתבי, ואשלח לך). No brand and no catalogue title (brand_issues), nothing else."""
    p = book_link_parts(cta)
    issues = audience_text_issues(path, "\n".join(book_link_slide(cta)), allow_cta=True, legacy=legacy)
    if not p:
        issues.append(Issue("ERROR", path, "the CTA is «אפשר גם לעזור להם עם <the problem> בעזרת ספר מותאם אישית. תכתבו \"<מילה>\" ואשלח לכם קישור להכנת הספר» (mom: תכתבי ... ואשלח לך), Yarin 30 Oct 2026"))
        return issues
    n_problem = len(words(p["problem"]))
    if not 1 <= n_problem <= BOOK_LINK_PROBLEM_MAX_WORDS:
        issues.append(Issue("ERROR", path, f"name the problem in 1 to {BOOK_LINK_PROBLEM_MAX_WORDS} words after «עם» (has {n_problem}): the topic's everyday problem (הגמילה מהמוצץ, הקנאה באח החדש)"))
    if len("עם " + p["problem"]) > 26:
        issues.append(Issue("ERROR", path, f"«עם {p['problem']}» is one headline line: 26 characters at most"))
    if not re.fullmatch(r"[א-ת]{2,10}", p["word"]):
        issues.append(Issue("ERROR", path, "the comment word is one Hebrew word, 2 to 10 letters"))
    elif p["word"] in BLOCKED_CODE_WORDS:
        issues.append(Issue("ERROR", path, BLOCKED_CODE_WORDS[p["word"]]))
    if code_word and p["word"] != code_word:
        issues.append(Issue("ERROR", path, f"the comment word in the CTA («{p['word']}») must be the option's code_word («{code_word}»)"))
    form = BOOK_LINK_FORMS.get(addressee)
    if form and (p["ask"] != form["ask"] or p["send"] != form["send"]):
        who = "mom (feminine singular)" if addressee == "mom" else "both parents (plural)"
        issues.append(Issue("ERROR", path, f"the CTA talks to {who}: {collapse(form['text'])}"))
    n = len(words(collapse(cta)))
    if n > BOOK_LINK_CTA_MAX_WORDS:
        issues.append(Issue("ERROR", path, f"CTA has {n} words (max {BOOK_LINK_CTA_MAX_WORDS})"))
    for pattern, why in SECOND_CTA_PATTERNS:
        m = re.search(pattern, collapse(cta))
        if m and why != "link in bio CTA":
            issues.append(Issue("ERROR", path, f"CTA contains a second CTA ({why}): «{m.group(0)}»"))
    return issues


def book_link_topic_issues(pack):
    """Every book link option on one topic uses the same comment word (one word per topic, as in Lotem's posts)."""
    out = []
    groups = {}
    for d in pack.get("directions", []):
        for v in d.get("versions", []):
            if book_link_applies(pack, v):
                groups.setdefault(v.get("topic_id") if is_pair_pack(pack) else "topic", []).append(v)
    for topic, vs in groups.items():
        words_ = {v.get("code_word", "") for v in vs}
        if len(words_) > 1:
            out.append(Issue("ERROR", f"directions/{topic}/code_word", f"every book link option on this topic uses the same comment word: {' / '.join(sorted(words_))}"))
    return out


# The open booklet under the CTA (Yarin, 30 Oct 2026: "an image of a physical open booklet example under the cta (in the
# same topic of the carousel), with a realistic image of the kid inside a small circle in the corner of the booklet",
# made with fal). `option.booklet`: {"page_text": [up to 3 lines], "crop": [x, y, w, h] of the spread inside
# booklet/booklet.png, "face": [x, y] of the child's face inside that crop, 0 to 1, and an optional arrow scale for a small face}. Files in RUN_DIR/booklet/:
# booklet.png (the spread, right page blank) and kid.png (a realistic face photo). scripts/booklet_cta.py.
BOOKLET_PAGE_MAX_LINES, BOOKLET_PAGE_LINE_MAX_CHARS = 3, 21


def booklet_issues(path, booklet):
    issues = []
    if not isinstance(booklet, dict):
        return [Issue("ERROR", path, "a book link option needs `booklet` (story-format.md section 7)")]
    lines = booklet.get("page_text") or []
    if not 1 <= len(lines) <= BOOKLET_PAGE_MAX_LINES:
        issues.append(Issue("ERROR", f"{path}/page_text", f"1 to {BOOKLET_PAGE_MAX_LINES} lines on the booklet page"))
    for ln in lines:
        if len(ln) > BOOKLET_PAGE_LINE_MAX_CHARS:
            issues.append(Issue("ERROR", f"{path}/page_text", f"a booklet line is {BOOKLET_PAGE_LINE_MAX_CHARS} characters at most", excerpt=ln))
    issues.extend(audience_text_issues(f"{path}/page_text", "\n".join(lines)))
    crop, face = booklet.get("crop"), booklet.get("face")
    if not (isinstance(crop, list) and len(crop) == 4):
        issues.append(Issue("ERROR", f"{path}/crop", "crop is [x, y, w, h] in booklet.png pixels"))
    if not (isinstance(face, list) and len(face) in (2, 3) and all(0 <= f <= 1 for f in face[:2]) and (len(face) == 2 or 0.3 <= face[2] <= 1.5)):
        issues.append(Issue("ERROR", f"{path}/face", "face is [x, y] inside the crop, 0 to 1, and an optional arrow scale (0.3 to 1.5; smaller for a small face)"))
    return issues


# ---------------------------------------------------------------------------
# Post texts: the written Instagram caption and Facebook text (Yarin, 26 Oct 2026: "in the written captions add
# punctuation marks and emojis (dont overdo it only at cta and hooks)")
# ---------------------------------------------------------------------------

POST_TEXT_FROM = "2026-10-26T21:00"
POST_CTA_EMOJI = "🔖"
BOOK_CTA_EMOJI = "📖"   # the CTA line of a book link post (30 Oct 2026) ends with a book, not the save bookmark


def post_cta_emoji(version):
    return BOOK_CTA_EMOJI if BOOK_LINK_RE.search(collapse((version or {}).get("cta", ""))) else POST_CTA_EMOJI


def cta_tail_lines(version):
    """How many caption lines the CTA takes: two for a book link CTA, one otherwise."""
    return 2 if BOOK_LINK_RE.search(collapse((version or {}).get("cta", ""))) else 1
_BARE_RE = re.compile(r"[^א-ת0-9A-Za-z]")
_POST_EMOJI_RE = re.compile("(?:" + EMOJI_RE.pattern + ")[\ufe0e\ufe0f\u200d]*")   # ☀️ = ☀ + a variation selector


def post_text_applies(pack):
    """Packs generated from POST_TEXT_FROM need post_text on every option."""
    return str((pack or {}).get("generated_at", ""))[:16] >= POST_TEXT_FROM


def fb_source(version):
    """Slides 2 to the last as written text, the Facebook post above slide 1: headline and body, a blank line between slides.
    A story option (it has a `structure`) is written without its markup (## labels, > cards, **emphasis**)."""
    clean = story_lib.strip_markup if version.get("structure") else (lambda t: t)
    blocks = ["\n".join(lines_of(clean(s.get("headline", ""))) + lines_of(clean(s.get("body", "")))) for s in version.get("slides", [])[1:]]
    return "\n\n".join(b for b in blocks if b)


def _bare(token):
    return _BARE_RE.sub("", token)


def _no_emoji(text):
    return "\n".join(" ".join(_POST_EMOJI_RE.sub("", line).split()) for line in str(text).split("\n"))


def post_words(text):
    """The words of a text without punctuation or emojis, to compare a post text with its source."""
    return [b for b in (_bare(t) for t in str(text).split()) if b]


def carry_punctuation(source, template):
    """The source text with its own words and line breaks, each word written as in the template where the two agree
    (difflib on the bare words), so a review edit keeps the punctuation of every unchanged word."""
    import difflib
    toks = _no_emoji(template).split()   # a mark standing alone (the · between words) stays its own token
    src_lines = [line.split() for line in str(source).split("\n")]
    flat = [w for line in src_lines for w in line]
    use = list(flat)
    sm = difflib.SequenceMatcher(None, [_bare(w) for w in flat], [_bare(t) for t in toks], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                use[i1 + k] = toks[j1 + k]
        elif tag == "replace" and i2 - i1 == j2 - j1:   # a word swapped for another keeps the marks around it
            for k in range(i2 - i1):
                t = toks[j1 + k]
                core = re.search(r"[א-ת0-9A-Za-z].*[א-ת0-9A-Za-z]|[א-ת0-9A-Za-z]", t)
                if core and _bare(flat[i1 + k]) == flat[i1 + k]:
                    use[i1 + k] = t[:core.start()] + flat[i1 + k] + t[core.end():]
    out, n = [], 0
    for line in src_lines:
        out.append(" ".join(use[n:n + len(line)]))
        n += len(line)
    return "\n".join(out)


def _hook_emoji(text):
    """(emoji, line) of the hook: the emoji ending line 1 or 2 (the hook sentence may run over two lines)."""
    filled = [line for line in str(text).split("\n") if line.strip()]
    for n, line in enumerate(filled[:2]):
        found = [e for e in _POST_EMOJI_RE.findall(line) if e != POST_CTA_EMOJI]   # 📖 stays a hook emoji (the same-story topic uses it)
        if found:
            return found[0], n
    return "", 0


def post_texts(version, template=None):
    """{"caption", "fb_text"} ready to post: the current caption and slides, punctuated as in the template
    (version["post_text"] or a hand written postiz-text.json), the hook emoji at the end of the first line and the
    save emoji at the end of the last. Without a template: the plain texts with only the save emoji."""
    tpl = template if template is not None else (version.get("post_text") or {})
    out = {}
    for key, src in (("caption", version.get("caption", "").strip()), ("fb_text", fb_source(version))):
        t = tpl.get(key) or ""
        text = carry_punctuation(src, t) if t else src
        lines = text.split("\n")
        filled = [i for i, line in enumerate(lines) if line.strip()]
        emoji, at = _hook_emoji(t)
        if not emoji:
            emoji, at = _hook_emoji(tpl.get("caption", ""))[0], 0
        if filled and emoji:
            lines[filled[min(at, len(filled) - 1)]] += " " + emoji
        if filled:
            lines[filled[-1]] += " " + post_cta_emoji(version)
        out[key] = "\n".join(lines)
    return out


def post_text_issues(path, version):
    """post_text must hold both texts, word for word the caption and slides 2 to 10, punctuated (no dash, semicolon or
    hyphen), with one emoji at the end of the first line, 🔖 at the end of the last and no other emoji."""
    pt = version.get("post_text")
    if not isinstance(pt, dict):
        return [Issue("ERROR", path, "post_text is missing: the written Instagram caption and Facebook text, punctuated, one emoji on the hook line and 🔖 on the CTA (Yarin, 26 Oct 2026)")]
    issues = []
    for key, src in (("caption", version.get("caption", "")), ("fb_text", fb_source(version))):
        p, text = f"{path}/{key}", str(pt.get(key) or "")
        if not text.strip():
            issues.append(Issue("ERROR", p, "empty"))
            continue
        a, b = post_words(src), post_words(text)
        if a != b:
            k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
            issues.append(Issue("ERROR", p, f"the words must be exactly the {'caption' if key == 'caption' else 'slides 2 to 10'}, only punctuation and emojis added; first difference at word {k + 1}",
                                excerpt=" ".join(b[max(0, k - 2):k + 3])))
        issues.extend(forbidden_char_issues(p, _POST_EMOJI_RE.sub("", text)))
        lines = [line for line in text.split("\n") if line.strip()]
        last = lines[-1] if lines else ""
        emoji, at = _hook_emoji(text)
        hook_line = lines[at] if lines else ""
        if not emoji or len(_POST_EMOJI_RE.findall(hook_line)) != 1 or not hook_line.rstrip().endswith(emoji):
            issues.append(Issue("ERROR", p, "the hook (line 1, or line 2 when the sentence runs over) ends with exactly one emoji that fits the topic", excerpt=(lines[0] if lines else "")[:80]))
        cta_emoji = post_cta_emoji(version)
        if not last.rstrip().endswith(cta_emoji) or len(_POST_EMOJI_RE.findall(last)) != 1:
            issues.append(Issue("ERROR", p, f"the last line (the CTA) ends with {cta_emoji} and nothing else", excerpt=last[:80]))
        if sum(len(_POST_EMOJI_RE.findall(line)) for line in lines) != 2:
            issues.append(Issue("ERROR", p, "two emojis in all: one on the hook and the CTA's, never in between"))
        if not re.search(r"[.,?!:]", _POST_EMOJI_RE.sub("", text)):
            issues.append(Issue("WARN", p, "no punctuation at all: add the periods, commas and question marks a person would type"))
    return issues


# ---------------------------------------------------------------------------
# Disclaimers (Yarin, 31 Oct 2026): a small block at the foot of every slide from slide 2 ("i want the disclaimer only
# from the second slide"; slide 1 is the thumbnail), and a line after the written caption of
# the Instagram post and the Facebook post. Both are fixed wording, added at export (compose_slides, caption.txt,
# postiz_export), never written into a pack.
# ---------------------------------------------------------------------------

SLIDE_DISCLAIMER = ("אין במוצג או באמור כדי להוות תחליף לייעוץ רפואי או המלצה לפעולה. בכל ספק יש לפנות לגורם רפואי "
                    "מוסמך כדי לשלול בעיה רפואית. ניתן למטרת ידע כללי ועל דעתי האישית בלבד.")
CAPTION_DISCLAIMER = "*לא מהווה ייעוץ רפואי/תחליף לייעוץ רפואי ולא מהווה המלצה לפעולה כלשהי. בכל ספק יש לפנות לגורם רפואי מוסמך"


def strip_disclaimer(text):
    """The text without its trailing caption disclaimer."""
    t = str(text or "").rstrip()
    if t.endswith(CAPTION_DISCLAIMER):
        t = t[:-len(CAPTION_DISCLAIMER)].rstrip()
    return t


def with_disclaimer(text):
    """The written text with the caption disclaimer after a blank line, once."""
    body = strip_disclaimer(text)
    return f"{body}\n\n{CAPTION_DISCLAIMER}" if body else CAPTION_DISCLAIMER


# ---------------------------------------------------------------------------
# The Facebook post (Yarin, 31 Oct 2026: "i need the facebook posts to be written more like engaging and converting
# facebook posts, their image without text on them and the right aspect ratio. also the cta should just refer people to
# the link"). Since then a finished carousel's Facebook post is its own text, RUN_DIR/facebook/facebook.txt, written at
# production: a hook, the moment, what helps, the book as one more way, a CTA line and the site link alone on the last
# line. Its picture is slide 1 as exported, with its text (1080 x 1350; the same day Yarin took back the picture without
# text: "add the text back to the facebook images"). The folder sits beside final/, so a re-export (which moves final/
# into versions/) keeps it, like booklet/. A run without facebook.txt keeps the old post (slide 1 with the slides
# written out).
# ---------------------------------------------------------------------------

FB_DIR = "facebook"
FB_POST_FILE = "facebook.txt"


def fb_post_path(run_dir):
    """The Facebook text of a run."""
    return Path(run_dir) / FB_DIR / FB_POST_FILE


FB_POST_MIN_WORDS = 45
FB_POST_MAX_WORDS = 160
_FB_COMMENT_CTA_RE = re.compile(r"(?<![א-ת])ת?כתב[וי]\s+[\"״]|ואשלח\s+(?:לך|לכם)")


def fb_link():
    """The site link every Facebook post ends with (shared/facts.json postiz.facebook_link)."""
    return (read_json(ROOT / "shared" / "facts.json").get("postiz") or {}).get("facebook_link", "")


def fb_post_issues(path, text):
    """facebook.txt: Hebrew that passes the audience rules, 45 to 160 words, the link alone on the last line and nowhere
    else, no comment word CTA, one emoji at the end of the hook line and one at the end of the CTA line above the link."""
    text = strip_disclaimer(text)
    lines = [line.strip() for line in str(text).split("\n") if line.strip()]
    if not lines:
        return [Issue("ERROR", path, "empty")]
    link = fb_link()
    issues = []
    if lines[-1] != link:
        issues.append(Issue("ERROR", path, f"the last line is the link alone: {link}", excerpt=lines[-1][:80]))
    body_lines = lines[:-1] if lines[-1] == link else lines
    body = "\n".join(body_lines)
    if re.search(r"https?://|lumebook\.com", body, re.I):
        issues.append(Issue("ERROR", path, "the link appears once, alone on the last line"))
    issues.extend(audience_text_issues(path, _POST_EMOJI_RE.sub("", body), allow_cta=True))
    m = _FB_COMMENT_CTA_RE.search(body)
    if m:
        issues.append(Issue("ERROR", path, "Facebook sends people to the link, not to a comment word", excerpt=m.group(0)))
    if re.search(r"לומבוק|לומיבוק|lumebook", body, re.I):
        issues.append(Issue("WARN", path, "names the brand: hint at a book where the child is the hero, the page name is on the post already"))
    n = len(words(_POST_EMOJI_RE.sub("", body)))
    if not FB_POST_MIN_WORDS <= n <= FB_POST_MAX_WORDS:
        issues.append(Issue("ERROR", path, f"{n} words; a Facebook post here is {FB_POST_MIN_WORDS} to {FB_POST_MAX_WORDS} words"))
    if body_lines:
        hook, cta = body_lines[0], body_lines[-1]
        if len(_POST_EMOJI_RE.findall(hook)) != 1 or not _POST_EMOJI_RE.search(hook.rstrip()[-3:]):
            issues.append(Issue("ERROR", path, "the hook (first line) ends with exactly one emoji", excerpt=hook[:80]))
        if len(body_lines) < 2 or len(_POST_EMOJI_RE.findall(cta)) != 1 or not _POST_EMOJI_RE.search(cta.rstrip()[-3:]):
            issues.append(Issue("ERROR", path, "the CTA line above the link ends with exactly one emoji", excerpt=cta[:80]))
        if sum(len(_POST_EMOJI_RE.findall(line)) for line in body_lines) != 2:
            issues.append(Issue("ERROR", path, "two emojis in all: one on the hook and one on the CTA line (Yarin, 26 Oct 2026)"))
    return issues


def save_later_moment(cta):
    """The words after לפעם הבאה in a save for later CTA ('' when it has none)."""
    flat = collapse(cta)
    return flat.split("לפעם הבאה", 1)[1].strip() if "לפעם הבאה" in flat else ""


def save_later_topic_issues(pack):
    """Every option on one topic says the same situation: options about a boy share one line and options about a girl
    share one line (the CTA is the topic's moment, not a scene of one carousel; Yarin, 24 Oct 2026)."""
    out = []
    groups = {}
    for d in pack.get("directions", []):
        for v in d.get("versions", []):
            if book_link_applies(None, v):
                continue
            topic = v.get("topic_id") if is_pair_pack(pack) else "topic"
            groups.setdefault((topic, v.get("child_gender")), []).append(v)
    for (topic, gender), vs in groups.items():
        moments = {save_later_moment(v.get("cta", "")) for v in vs}
        if len(moments) > 1:
            out.append(Issue("ERROR", f"directions/{topic}/cta", f"every option on this topic about a {gender} ends the CTA the same way, "
                                                                    f"with the topic's situation, not its own scene: {' / '.join(sorted(moments))}"))
    return out


def save_later_cta_issues(path, cta, addressee, legacy=False, gender=None, child_name=None):
    """The save for later CTA: תשמרי (or תשמרו) את הפוסט לפעם הבאה ש... in the addressee's form, about the child, and nothing else."""
    issues = audience_text_issues(path, cta, allow_cta=True, legacy=legacy)
    flat = collapse(cta)
    if not SAVE_LATER_RE.search(flat):
        issues.append(Issue("ERROR", path, "the CTA is «תשמרי את הפוסט לפעם הבאה ש...» (both parents: תשמרו), ending with the moment the post will be needed again (Yarin, 24 Oct 2026)"))
    elif len(words(flat)) < 7:
        issues.append(Issue("ERROR", path, "say when the post will be needed again: לפעם הבאה ש + the moment (לפעם הבאה שהיא מפחדת מרעמים)"))
    else:
        moment = save_later_moment(flat)
        if len(words(moment)) > SAVE_LATER_MOMENT_MAX_WORDS:
            issues.append(Issue("ERROR", path, f"the moment has {len(words(moment))} words: keep it to the topic's everyday situation in up to {SAVE_LATER_MOMENT_MAX_WORDS} words (שהיא מפחדת מרעמים, שיש לו יום הולדת), not a scene"))
        ref = KID_REF.get(gender)
        if ref and not ref.search(moment) and not (child_name and child_name in moment):
            pron = "הוא, לו, אותו" if gender == "boy" else "היא, לה, אותה"
            issues.append(Issue("ERROR", path, f"the moment is always about the child (Yarin, 24 Oct 2026: \"always refer to the kid\"): {pron}"))
    form = SAVE_LATER_FORMS.get(addressee)
    if form and not flat.startswith(form["save"]):
        who = "mom (feminine singular)" if addressee == "mom" else "both parents (plural)"
        issues.append(Issue("ERROR", path, f"the CTA talks to {who}: {form['save']} לפעם הבאה ש..."))
    n = len(words(flat))
    if n > CTA_SLIDE_MAX_WORDS:
        issues.append(Issue("ERROR", path, f"CTA has {n} words (max {CTA_SLIDE_MAX_WORDS})"))
    for pattern, why in COMMENT_CTA_PATTERNS + [p for p in SECOND_CTA_PATTERNS if p[1] not in ("save CTA", "link in bio CTA")]:
        m = re.search(pattern, flat)
        if m:
            issues.append(Issue("ERROR", path, f"CTA contains a second CTA ({why}): «{m.group(0)}»"))
    return issues


def pack_topics(pack):
    """The pack's topics in lane order: two for a two-topic pack, otherwise the one topic."""
    if is_pair_pack(pack):
        return [t for t in pack.get("topics") or [] if isinstance(t, dict)]
    return [pack["topic"]] if isinstance((pack or {}).get("topic"), dict) else []


def option_topic(pack, version):
    """The topic one option is about: its topic_id in a two-topic pack, otherwise the pack's topic."""
    if is_pair_pack(pack):
        for t in pack_topics(pack):
            if t.get("id") == (version or {}).get("topic_id"):
                return t
    return (pack or {}).get("topic") or {}


def pair_lane_of(option_id):
    """'a' or 'b' for a two-topic pack option id, else None."""
    return next((lane for lane, ids in PAIR_LANES if option_id in ids), None)


# Yarin, 24 Oct 2026: "make sure the carousel machine do 50/50 boys and girls". Packs generated from GENDER_BALANCE_FROM
# have as many girls as boys, and in a two-topic pack each topic has at least one of each. `nightly.py start` hands the
# writer a gender per option, alternating, and the first option's gender flips from day to day so kid-1 is not always a girl.
GENDER_BALANCE_FROM = "2026-10-24T21:00"


def gender_balance_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= GENDER_BALANCE_FROM


def gender_slots(date_str):
    """{option id: girl or boy} for one date: kid-1 girl, kid-2 boy, kid-3 girl... on even days, the other way round on odd ones."""
    first, second = ("girl", "boy") if dt.date.fromisoformat(date_str).toordinal() % 2 == 0 else ("boy", "girl")
    return {oid: first if i % 2 == 0 else second for i, oid in enumerate(PAIR_OPTION_IDS)}


def gender_balance_issues(pack):
    """Half girls and half boys across the options, and both in each topic of a two-topic pack (checked when the pack is written)."""
    if not gender_balance_applies(pack):
        return []
    versions = [v for d in pack.get("directions", []) for v in d.get("versions", [])]
    genders = [v.get("child_gender") for v in versions]
    out = []
    if genders.count("girl") != genders.count("boy"):
        out.append(Issue("ERROR", "directions/child_gender", f"the options must be half girls and half boys (Yarin, 24 Oct 2026: \"50/50 boys and girls\"): "
                                                             f"{genders.count('girl')} girls and {genders.count('boy')} boys; follow child_gender_per_option from nightly.py start"))
    if is_pair_pack(pack):
        for lane, ids in PAIR_LANES:
            have = {v.get("child_gender") for v in versions if v.get("id") in ids}
            if not {"girl", "boy"} <= have:
                out.append(Issue("ERROR", f"directions/topic-{lane}/child_gender", f"topic {lane} ({', '.join(ids)}) needs at least one girl and one boy"))
    return out


# The save and share CTA. Written in Yarin's own caption voice ("תשמרי כדי לזכור ותשלחי לאמא שצריכה לשמוע את זה גם",
# the reel of 14 Oct 2026); the default forms below are what `nightly.py start` hands the writer.
SAVE_SHARE_FORMS = {
    # Yarin, 24 Oct 2026: "i want the cta to be 'אפשר לעזור להם גם בסיפור אישי, תשמרי את הפוסט ותשלחי לאמא שתתחבר'"
    # (slide 10's headline is STORY_LINE; this is its body and the caption's last line). Both parents: the same in plural.
    "mom": {"save": r"ת?שמרי", "send": r"ו?ת?שלחי", "text": "תשמרי את הפוסט\nותשלחי לאמא שתתחבר"},
    "parents": {"save": r"ת?שמרו", "send": r"ו?ת?שלחו", "text": "תשמרו את הפוסט\nותשלחו לאמא שתתחבר"},
}
# Slide 10's headline above the save and share CTA, the same in every option (Yarin, 24 Oct 2026: "change the cta to
# אפשר לעזור להם גם בסיפור אישי"), with בסיפור אישי as the highlighted phrase
STORY_LINE = "אפשר לעזור להם גם\nבסיפור אישי"
STORY_LINE_HIGHLIGHT = "בסיפור אישי"
SAVE_SHARE_REQUIRED = [
    (r"(?<![א-ת])ת?שמר[וי](?![א-ת])", "a save verb (תשמרו / תשמרי)"),
    (r"(?<![א-ת])ו?ת?שלח[וי](?![א-ת])", "a send verb (ותשלחו / ותשלחי)"),
    (r"(?<![א-ת])ל(?:אמא|הורה|הורים|אמהות|חברה)(?![א-ת])", "who to send it to (לאמא, להורה)"),
    (r"(?<![\u05D0-\u05EA])ש(?:ת|י)תחבר(?:ו|י)?(?![\u05D0-\u05EA])", "a mom who will relate (שתתחבר)"),
]
# Since the save and share CTA, asking for a comment or a link is a second CTA anywhere in the option
COMMENT_CTA_PATTERNS = [
    (r"(?<![א-ת])(?:ו)?(?:ת)?כתב[וי]\s*[\"״]|בתגובות", "comment CTA (no comment word since 24 Oct 2026)"),
    (r"קישור|לינק|בביו", "link CTA"),
]


def save_share_cta_issues(path, cta, addressee, legacy=False):
    """The CTA of a pack from DAILY_PAIR_FROM: save the post and send it to a mom who will relate, in the addressee's form."""
    issues = audience_text_issues(path, cta, allow_cta=True, legacy=legacy)
    flat = collapse(cta)
    for pattern, label in SAVE_SHARE_REQUIRED:
        if not re.search(pattern, flat):
            issues.append(Issue("ERROR", path, f"the CTA asks to save the post and send it to a mom who will relate (Yarin, 24 Oct 2026); it needs {label}"))
    form = SAVE_SHARE_FORMS.get(addressee)
    if form:
        verbs_ok = re.search(rf"(?<![א-ת]){form['save']}(?![א-ת])", flat) and \
            re.search(rf"(?<![א-ת]){form['send']}(?![א-ת])", flat)
        if not verbs_ok:
            who = "mom (feminine singular)" if addressee == "mom" else "both parents (plural)"
            issues.append(Issue("ERROR", path, f"the CTA talks to {who}: {collapse(form['text'])}"))
    n = len(words(flat))
    if n > CTA_SLIDE_MAX_WORDS:
        issues.append(Issue("ERROR", path, f"CTA has {n} words (max {CTA_SLIDE_MAX_WORDS})"))
    for pattern, why in COMMENT_CTA_PATTERNS + [p for p in SECOND_CTA_PATTERNS if p[1] not in ("save CTA", "share CTA", "link in bio CTA")]:
        m = re.search(pattern, flat)
        if m:
            issues.append(Issue("ERROR", path, f"CTA contains a second CTA ({why}): «{m.group(0)}»"))
    return issues


def comment_cta_issues(path, text):
    """A comment or link request in a two-topic pack's slides or caption: the save and share CTA is the only one."""
    out = []
    for line in lines_of(text):
        for pattern, why in COMMENT_CTA_PATTERNS:
            m = re.search(pattern, line)
            if m:
                out.append(Issue("ERROR", path, f"second CTA ({why}): «{m.group(0)}»", excerpt=line[:80]))
    return out


def load_bestsellers(path=None):
    """{topic id: {"book", "title_he", "orders", "about"}} from topic-bank.md "Best-selling books" (Yarin, 24 Oct 2026)."""
    out, on = {}, False
    for line in Path(path or TOPIC_BANK).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            on = line.startswith("## Best-selling books")
            continue
        if not on or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        book = {"book": int(cells[0]), "title_he": cells[1], "orders": int(cells[2]) if cells[2].isdigit() else None, "about": cells[3]}
        for tid in re.findall(r"`([a-z0-9-]+)`", cells[4]):
            out[tid] = book
    return out


# ---------------------------------------------------------------------------
# Image prompts
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# The two content pillars (the two directions of every pack). One identity each, used by the review
# page, the final slide design and the photo direction. Full description: carousel/carousel-pipeline/pillars.md
# ---------------------------------------------------------------------------

PILLARS = {
    "kid": {
        "name_he": "הילד מספר",
        "tagline_he": "הילד מדבר בגוף ראשון ומספר מה מרגיש לו",
        "color": "#5B2BD6", "soft": "#F1EBFF", "card": "#F8F4FF", "deep": "#3B1D78",
        "font": "Rubik", "symbol": "״",
        "photo": ("Point of view: the child's world. Camera at the child's eye level or lower, close and intimate, "
                  "the parent often partly in frame (a hand, a knee, a shoulder), warm light with a soft violet cast."),
    },
    "expert": {
        "name_he": "גישה מקצועית",
        "tagline_he": "עצה ברורה שאפשר לנסות מחר, וכל עצה נשענת על מקור",
        "color": "#A8741F", "soft": "#F8EEDC", "card": "#FCF7EE", "deep": "#1D1039",
        "font": "Heebo", "symbol": "✦",
        "photo": ("Point of view: a calm observer. Camera at adult eye level, medium to wide, clean uncluttered composition "
                  "with generous negative space, mother and child both in frame, natural daylight with a muted gold warmth."),
    },
}


STYLE = (
    # Yarin's chosen look (fal trial, 7 Oct 2026; a photo-real reference was rejected on 8 Oct): feature-film 3D animation
    "Feature-film 3D animated style: smooth soft-shaded stylised characters with large expressive eyes, rounded features, "
    "gentle subsurface skin glow, detailed knit and linen fabric textures, warm cinematic lighting, soft depth of field, "
    "rich but tender colour. Cute faces: large round eyes with soft sparkly catch-lights, chubby rosy cheeks, small soft "
    "noses and chins; the child has a slightly bigger head relative to the body. Clearly an animated film still, never "
    "a photograph. Lived-in Israeli apartment details."
)
PALETTE = (
    "Palette: warm cream (#F8F0E1) walls and textiles, plum and violet accents (#5B2BD6, #291852), muted gold "
    "highlights (#C9954A). Low saturation, warm white balance."
)
AVOID = (
    "Avoid photorealism, glossy advertising smiles, exaggerated sadness or tears, staged stock-photo poses "
    "and any uncanny or distorted hands or faces."
)
NO_TEXT = (
    "No generated words, letters, numbers, logos, watermarks, signatures, frames, borders or user interface anywhere in "
    "the image, including on books, screens, clothing, toys and signs."
)
PRODUCT_CARD_ZONE = (
    "If a book, tablet or phone appears, it shows only a soft storybook illustration of this same child as the hero, "
    "with no words, letters, logos or interface. Nothing in the scene identifies a brand."
)
REFERENCE_LOCK = (
    "Use the reference image as the exact character and style reference. Keep the same child and parent: same faces, "
    "ages, hair, skin tone, body proportions, clothing and the same feature-film 3D animated style, lighting and textures. Create a new scene and camera angle; "
    "do not copy the reference layout."
)
# Slide 1 is the thumbnail (Yarin, 10 Oct 2026): "clickbaity and always have the child's face facing the viewer
# with an exaggerated expression". Applies to packs written from COVER_RULE_FROM on; older packs still validate.
COVER_RULE_FROM = "2026-10-10T17:00"
COVER_FACE = (
    "Cover image, composed like an animated film poster: the child is the subject and FACES THE VIEWER, head and "
    "shoulders or waist up, the face large in the frame, eyes looking straight into the camera. One big, exaggerated, "
    "instantly readable expression that fits the emotional beat (for example huge wide eyes with raised eyebrows, a "
    "dramatic pout with puffed cheeks, an open-mouthed gasp, a jaw-dropped stare, a giant grin). The whole face is "
    "visible: never from behind, never in profile, never hidden by hair, hands or objects. A parent may appear only "
    "small or soft in the background. This cover framing overrides any wider framing asked for elsewhere in this prompt."
)
COVER_AVOID = (
    "Avoid photorealism, staged stock-photo poses and any uncanny or distorted hands or faces. The exaggeration is in "
    "the expression, the way an animated film exaggerates, never in broken anatomy."
)
COVER_FACE_RE = re.compile(
    r"fac(?:es|ing)\s+(?:the\s+)?(?:viewer|camera|lens)"
    r"|look(?:s|ing)?\s+(?:straight\s+|directly\s+|right\s+)?(?:at|into|to)\s+(?:the\s+)?(?:viewer|camera|lens)"
    r"|eyes?\s+(?:straight\s+)?(?:to|on|into|at)\s+(?:the\s+)?(?:camera|viewer|lens)", re.I)
COVER_EXPRESSION_RE = re.compile(
    r"exaggerat|wide[- ]eyed|wide eyes|huge eyes|raised eyebrows|open[- ]mouth|gasp|jaw|pout|puffed cheeks|giant grin|"
    r"big grin|scrunched|shock|stunned|dramatic", re.I)
COVER_BLOCK_RE = re.compile(
    r"from behind|behind (?:the|her|his) (?:shoulder|back|head)|back to (?:the )?(?:camera|viewer)|back view|"
    r"over[- ]the[- ]shoulder|silhouette|in profile|profile (?:view|shot)|side view|from the side|face down|"
    r"face (?:hidden|covered|buried)|hides? (?:her|his) face", re.I)


def cover_rule_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= COVER_RULE_FROM


def cover_image_issues(path, image):
    """Slide 1's picture: the child's face to the viewer with a big readable expression."""
    issues = []
    where = " ".join(str(image.get(k, "")) for k in ("action", "camera"))
    if not COVER_FACE_RE.search(where):
        issues.append(Issue("ERROR", f"{path}/image/action", "slide 1 is the thumbnail: say that the child faces the viewer and looks straight into the camera"))
    m = COVER_BLOCK_RE.search(where)
    if m:
        issues.append(Issue("ERROR", f"{path}/image/camera", f"slide 1 shows the child's whole face to the viewer, not «{m.group(0)}»"))
    if not COVER_EXPRESSION_RE.search(where + " " + str(image.get("beat", ""))):
        issues.append(Issue("ERROR", f"{path}/image/action", "slide 1 needs one big exaggerated expression: name it (wide eyes and raised eyebrows, dramatic pout, open-mouthed gasp...)"))
    return issues


# Slide 1's words: only the strongest candidates. Used slate candidates must score 2 on each of these.
COVER_HOOK_MUST_BE_2 = ("stopping_power", "honest_curiosity", "swipe_promise")

# Yarin, 11 Oct 2026: "i want the hooks to focus on what value is it going to provide". The cover says what the viewer gets
# (a number of things to try, a sentence to say, a result, an answer), not only a tease. Used slate candidates score 2 on
# `usefulness` (the cover itself promises something to do or understand tomorrow), and a cover with no value marker is flagged.
VALUE_HOOK_FROM = "2026-10-11T00:00"
COVER_VALUE_MUST_BE_2 = ("usefulness",)
VALUE_MARKER_RE = re.compile(r"\d|שיעזר|עוזר|מעזר|איך\b|משפט|שאלה אחת|במקום|מה (?:עושים|אומרים|כן)|דבר(?:ים)?\b|טיפ|דרך|סדר|צעד|רעיון|כלי|מתי כן|סוגר|מרגיע|מרדים")


def value_hook_applies(pack):
    return str((pack or {}).get("generated_at", ""))[:16] >= VALUE_HOOK_FROM


IMAGE_FIELDS = ("beat", "action", "setting", "camera", "lighting", "wardrobe_objects")
ANCHOR_FIELDS = ("child", "parent", "wardrobe")


def text_zone_sentence(zone):
    edge = zone.get("edge", "top")
    percent = zone.get("percent", 40)
    surface = zone.get("surface") or "plain evenly lit cream wall"
    return (
        f"Composition: vertical 4:5. Reserve the {edge} {percent}% of the frame as clean, quiet negative space "
        f"({surface}) for editable Hebrew typography, and keep every face, hand and important object out of that zone. "
        # Yarin, 24 Oct 2026 ("do it" on the audit's contrast fix): dark plum type was hard to read on the blue night
        # walls of the clock change and pacifier carousels. The renderer also checks the contrast (compose_slides.py).
        "That zone is light and warm (cream, soft beige or a pale sky), never dark, blue, grey or saturated, so dark "
        "type reads at high contrast; in an evening or night scene a warm lamp lights that wall."
    )


def compose_image_prompt(anchor, image, slide_number, for_edit=False, pillar=None, one_picture_prompt=False):
    """The exact English prompt the image model receives. Review pages show this same string.
    pillar is 'kid' or 'expert' and adds that pillar's photo direction. one_picture_prompt: the option's single
    picture (packs from 14 Oct 2026), written as the cover (slide_number 1) and shown behind every slide."""
    parts = []
    if for_edit:
        parts.append(REFERENCE_LOCK)
    parts.append(
        "Characters, identical on every slide: "
        f"{anchor['child'].strip()} {anchor['parent'].strip()} Wardrobe: {anchor['wardrobe'].strip()}"
    )
    parts.append(f"Scene: {image['action'].strip()} Setting: {image['setting'].strip()}")
    if slide_number == 1:
        parts.append(COVER_FACE)
    parts.append(f"Emotional beat: {image['beat'].strip()}")
    parts.append(f"Camera: {image['camera'].strip()} Lighting: {image['lighting'].strip()}")
    parts.append(f"Wardrobe and objects in this scene: {image['wardrobe_objects'].strip()}")
    parts.extend([STYLE, PALETTE, COVER_AVOID if slide_number == 1 else AVOID])
    if pillar in PILLARS and slide_number != 1:   # the cover has its own framing
        parts.append(PILLARS[pillar]["photo"])
    parts.append(text_zone_sentence(image.get("text_zone", {})))
    if slide_number == CTA_SLIDE and not one_picture_prompt:
        parts.append(PRODUCT_CARD_ZONE)
    parts.append(NO_TEXT)
    return "\n\n".join(parts)


def reference_prompt(anchor, pillar=None):
    return "\n\n".join([
        "Characters, identical on every slide: "
        f"{anchor['child'].strip()} {anchor['parent'].strip()} Wardrobe: {anchor['wardrobe'].strip()}",
        "Scene: a neutral character and style reference. The child and the parent sit together on a cream sofa in a "
        "quiet living room, both faces and all four hands clearly visible, relaxed and natural, full enough framing "
        "to establish clothing, proportions and hair.",
        "Camera: eye level, medium-wide shot, 50mm look. Lighting: soft window daylight from the right.",
        STYLE, PALETTE, AVOID,
        PILLARS[pillar]["photo"] if pillar in PILLARS else "",
        text_zone_sentence({"edge": "top", "percent": 35, "surface": "plain cream wall"}),
        NO_TEXT,
    ])


# ---------------------------------------------------------------------------
# Voice calibration status
# ---------------------------------------------------------------------------

def _profile_samples(text):
    """Fenced ```text blocks under '## Writing samples' that are not the template."""
    if "## Writing samples" not in text:
        return []
    section = text.split("## Writing samples", 1)[1]
    blocks = re.findall(r"```text\n(.*?)```", section, re.S)
    return [b for b in blocks if b.strip() and "Paste the exact message here" not in b]


# Yarin's edits in the review page are Yarin's own writing. A rewrite where at least half of the words are new and
# the result has at least 3 words counts as one calibration sample; small tweaks and line-break changes are kept
# as style signals but do not count.
EDIT_SAMPLE_MIN_WORDS = 3
EDIT_SAMPLE_MIN_NEW_SHARE = 0.5


def _bare_words(text):
    return [re.sub(r"[^\w\u0590-\u05FF]", "", w) for w in words(collapse(text)) if re.sub(r"[^\w\u0590-\u05FF]", "", w)]


def edit_kind(before, after):
    """'rewrite' (counts as a voice sample), 'tweak', 'line_breaks' or 'none'."""
    bw, aw = _bare_words(before), _bare_words(after)
    if bw == aw:
        return "line_breaks" if lines_of(before) != lines_of(after) else "none"
    if not aw:
        return "tweak"
    seen = set(bw)
    share = sum(1 for w in aw if w not in seen) / len(aw)
    return "rewrite" if len(aw) >= EDIT_SAMPLE_MIN_WORDS and share >= EDIT_SAMPLE_MIN_NEW_SHARE else "tweak"


def load_voice_edits(path=VOICE_EDITS):
    path = Path(path)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def log_voice_edits(records, path=VOICE_EDITS):
    if not records:
        return 0
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(records)


def recent_voice_edits(n=20, path=VOICE_EDITS):
    """The latest edits worth learning from, newest last: rewrites, tweaks and line-break changes."""
    keep = [e for e in load_voice_edits(path) if e.get("kind") in ("rewrite", "tweak", "line_breaks")]
    return [{k: e.get(k) for k in ("at", "direction", "kind", "field", "role", "addressee", "before", "after")} for e in keep[-n:]]


def voice_status(profile_path=VOICE_PROFILE, approved_dir=APPROVED_EXAMPLES, edits_path=VOICE_EDITS):
    profile_samples = _profile_samples(Path(profile_path).read_text(encoding="utf-8")) if Path(profile_path).exists() else []
    files = []
    if Path(approved_dir).exists():
        for p in sorted(Path(approved_dir).glob("*.md")):
            if p.name.lower() == "readme.md":
                continue
            body = p.read_text(encoding="utf-8")
            if HEBREW_RE.search(body):
                files.append(p.name)
    edits = load_voice_edits(edits_path)
    rewrites = {collapse(e.get("after", "")) for e in edits if e.get("kind") == "rewrite"}
    total = len(profile_samples) + len(files) + len(rewrites)
    status = "calibrated" if total >= CALIBRATION_MIN_SAMPLES else "fallback"
    return {
        "status": status,
        "approved_samples": total,
        "required": CALIBRATION_MIN_SAMPLES,
        "from_profile": len(profile_samples),
        "from_examples_folder": len(files),
        "from_review_edits": len(rewrites),
        "review_edits_logged": len(edits),
    }


# ---------------------------------------------------------------------------
# Dates, topics and history
# ---------------------------------------------------------------------------

def now_local():
    return dt.datetime.now().astimezone()


def review_date_for(moment=None):
    """The morning the pack is for. Runs from 06:00 onward prepare the next morning;
    a late run after midnight (the computer was asleep at 22:00) still targets the same morning."""
    moment = moment or now_local()
    day = moment.date()
    return day if moment.hour < 6 else day + dt.timedelta(days=1)


def parse_date(value):
    return dt.date.fromisoformat(value)


def is_event_topic(topic_id):
    return str(topic_id or "").startswith(EVENT_TOPIC_PREFIX)


def load_topic_bank(path=TOPIC_BANK):
    """Rows of the markdown table whose first cell is a backticked id. A row tied to a best-selling book (topic-bank.md
    "Best-selling books", 24 Oct 2026) carries it as `bestseller`."""
    best = load_bestsellers(path)
    topics = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = re.fullmatch(r"`([a-z0-9-]+)`", cells[0]) if cells else None
        if not m or len(cells) < 5:
            continue
        months = [int(x) for x in re.findall(r"\d+", cells[3])] if cells[3] not in ("any", "") else []
        topics.append({
            "id": m.group(1),
            "title_he": cells[1],
            "title_en": cells[2],
            "months": months,
            "code_words": [w.strip() for w in cells[4].split("/") if w.strip()],
            "books": cells[5] if len(cells) > 5 else "",
            "bestseller": best.get(m.group(1)),
        })
    return topics


def load_history(path=HISTORY):
    path = Path(path)
    if not path.exists():
        return {"packs": []}
    return json.loads(path.read_text(encoding="utf-8"))


def previous_packs(history, date_str):
    """Packs before date_str, newest first. A rerun for the same date ignores its own earlier entry."""
    packs = [p for p in history.get("packs", []) if p.get("date") and p["date"] < date_str]
    return sorted(packs, key=lambda p: p["date"], reverse=True)


def rotation_context(history, date_str, bank=None):
    bank = bank if bank is not None else load_topic_bank()
    day = parse_date(date_str)
    prev = previous_packs(history, date_str)
    topic_ids_of = lambda p: p.get("topic_ids") or [p["topic_id"]]  # noqa: E731  (two per pack since 24 Oct 2026)
    recent_topics = [t for p in prev[:TOPIC_COOLDOWN_PACKS] for t in topic_ids_of(p)]
    recent_pair_topics = [t for p in prev[:PAIR_TOPIC_COOLDOWN_PACKS] for t in topic_ids_of(p)]
    code_cutoff = (day - dt.timedelta(days=CODE_WORD_COOLDOWN_DAYS)).isoformat()
    recent_code_words = sorted({w for p in prev if p["date"] >= code_cutoff for w in p.get("code_words", [])})
    fam_cutoff = (day - dt.timedelta(days=HOOK_FAMILY_WINDOW_DAYS)).isoformat()
    window = [p for p in prev if p["date"] >= fam_cutoff]
    selected_counts, candidate_counts = {}, {}
    for p in window:
        for o in p.get("options", []):
            candidate_counts[o["hook_family"]] = candidate_counts.get(o["hook_family"], 0) + 1
        for sel in p.get("selected", []):
            fam = next((o["hook_family"] for o in p.get("options", []) if o["id"] == sel), None)
            if fam:
                selected_counts[fam] = selected_counts.get(fam, 0) + 1
    blocked = sorted(f for f, n in selected_counts.items() if n >= HOOK_FAMILY_MAX_IN_WINDOW)
    recent_hooks = [h for p in prev[:30] for h in p.get("hooks", [])]
    recent_formulas = sorted({o.get("hook_formula") for p in prev[:HOOK_RECENT_PACKS] for o in p.get("options", []) if o.get("hook_formula")})
    recent_window = [o for p in prev[:HOOK_RECENT_PACKS] for o in p.get("options", [])]

    def _count(key):
        out = {}
        for o in recent_window:
            if o.get(key):
                out[o[key]] = out.get(o[key], 0) + 1
        return out
    recent_slide2 = [h for p in prev[:30] for h in p.get("slide2_hooks", [])]
    selected_formulas_14 = sorted({o.get("hook_formula") for p in prev if p["date"] >= (day - dt.timedelta(days=14)).isoformat()
                                   for o in p.get("options", []) if o["id"] in p.get("selected", []) and o.get("hook_formula")})
    recent_names = sorted({o.get("child_name") for p in prev[:NAME_COOLDOWN_PACKS] for o in p.get("options", []) if o.get("child_name")})
    last_used = {}
    for p in prev:
        for t in topic_ids_of(p):
            last_used.setdefault(t, p["date"])
    ranked = []
    for t in bank:
        eligible = t["id"] not in recent_topics
        in_season = (not t["months"]) or (day.month in t["months"])
        days_since = (day - parse_date(last_used[t["id"]])).days if t["id"] in last_used else None
        ranked.append({
            **t,
            "eligible": eligible,
            "in_season": in_season,
            "last_used": last_used.get(t["id"]),
            "days_since": days_since,
            "free_code_words": [w for w in t["code_words"] if w not in recent_code_words],
        })
    ranked.sort(key=lambda t: (not t["eligible"], not (t["in_season"] and t["months"]), not t["in_season"], -(t["days_since"] or 10_000)))
    return {
        "date": date_str,
        "recent_topic_ids": recent_topics,
        "recent_pair_topic_ids": recent_pair_topics,
        "recent_code_words": recent_code_words,
        "blocked_hook_families": blocked,
        "hook_family_candidates_last_7_days": candidate_counts,
        "hook_family_selected_last_7_days": selected_counts,
        "recent_hooks": recent_hooks,
        "recent_hook_formulas": recent_formulas,
        "recent_mechanisms": _count("mechanism"),
        "recent_shapes": _count("shape"),
        "recent_slide2_moves": _count("slide2_move"),
        "recent_awareness": _count("awareness_stage"),
        "recent_slide2_hooks": recent_slide2,
        "selected_formulas_last_14_days": selected_formulas_14,
        "recent_child_names": recent_names,
        # story packs (29 Oct 2026): how often each structure was used in the previous packs, to rotate away from them
        "recent_structures": {st: n for st, n in sorted(_story_counts(prev[:story_lib.RECENT_PACKS]).items())},
        "topics": ranked,
    }


def _story_counts(packs):
    out = {}
    for p in packs:
        for o in p.get("options", []):
            if o.get("structure"):
                out[o["structure"]] = out.get(o["structure"], 0) + 1
    return out


def history_entry(pack, bank=None):
    bank = bank if bank is not None else load_hook_bank()
    options, code_words, hooks, slide2 = [], set(), [], []
    for d in pack["directions"]:
        for v in d["versions"]:
            hook = v.get("hook") or {}
            formula = bank.get(hook.get("formula"), {})
            options.append({
                "id": v["id"], "hook_family": v["hook_family"], "hook_formula": hook.get("formula"), "code_word": v.get("code_word"),
                "child_name": v.get("child_name"), "title": v["title"],
                **({"topic_id": v.get("topic_id")} if is_pair_pack(pack) else {}),
                **({"structure": v["structure"]} if v.get("structure") else {}),   # story packs rotate structures (29 Oct 2026)
                # rotation fields (hook strategy research, 8 Oct 2026)
                "mechanism": hook.get("mechanism") or (formula.get("mechanisms") or [None])[0],
                "shape": formula.get("shape") or None,
                "slide2_move": hook.get("slide2_move"),
                "awareness_stage": v.get("awareness_stage"),
            })
            if v.get("code_word"):
                code_words.add(v["code_word"])
            hooks.append(collapse(v["slides"][0]["headline"]))
            if len(v["slides"]) > 1 and collapse(v["slides"][1]["headline"]):
                slide2.append(collapse(v["slides"][1]["headline"]))
    return {
        "date": pack["date"],
        "generated_at": pack.get("generated_at"),
        "topic_id": pack["topic"]["id"],
        "topic": pack["topic"]["title_he"],
        **({"topic_ids": [t.get("id") for t in pack_topics(pack)], "topics": [t.get("title_he") for t in pack_topics(pack)]}
           if is_pair_pack(pack) else {}),
        "hook_families": sorted({o["hook_family"] for o in options}),
        "code_words": sorted(code_words),
        "hooks": hooks,
        "slide2_hooks": slide2,
        "options": options,
        "selected": [],
    }


def record_history(pack, path=HISTORY):
    """Insert or replace this date's entry. Keeps an earlier selection if the pack is unchanged in options."""
    history = load_history(path)
    entry = history_entry(pack)
    kept = [p for p in history.get("packs", []) if p.get("date") != pack["date"]]
    old = next((p for p in history.get("packs", []) if p.get("date") == pack["date"]), None)
    if old:
        ids = {o["id"] for o in entry["options"]}
        entry["selected"] = [s for s in old.get("selected", []) if s in ids and old.get("topic_id") == entry["topic_id"]]
    kept.append(entry)
    kept.sort(key=lambda p: p["date"])
    history["packs"] = kept
    write_json(path, history)
    return entry


def mark_selected(date_str, option_id, path=HISTORY):
    history = load_history(path)
    for p in history.get("packs", []):
        if p.get("date") == date_str:
            if option_id not in p.setdefault("selected", []):
                p["selected"].append(option_id)
            write_json(path, history)
            return True
    return False


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # a temp name of its own per process, so two exports writing drive-pending.json at once never take each other's file
    # (24 Oct 2026: one of seven parallel re-exports failed with FileNotFoundError on the shared .tmp)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{id(data)}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def backup_existing(folder, names=("pack.json", "review.html", "review.md")):
    """Move an existing pack into versions/vN before a rerun overwrites it. Returns the backup folder or None."""
    folder = Path(folder)
    present = [folder / n for n in names if (folder / n).exists()]
    if not present:
        return None
    versions = folder / "versions"
    versions.mkdir(parents=True, exist_ok=True)
    n = 1
    while (versions / f"v{n}").exists():
        n += 1
    target = versions / f"v{n}"
    target.mkdir()
    for p in present:
        p.replace(target / p.name)
    return target


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def write_placeholder_png(path, width, height, label_rgb=(91, 43, 214), seed=0):
    """A plain cream image with a soft violet block in the lower half, stdlib only.
    Used to test the final renderer without paid images."""
    cream = (243, 234, 220)
    rows = []
    block_top = int(height * 0.55)
    left = int(width * (0.18 + 0.1 * (seed % 3)))
    right = left + int(width * 0.45)
    for y in range(height):
        if y < block_top:
            shade = int(8 * y / height)
            row = bytes((cream[0] - shade, cream[1] - shade, cream[2] - shade)) * width
        else:
            row = bytearray(bytes(cream) * width)
            row[left * 3:right * 3] = bytes(label_rgb) * (right - left)
            row = bytes(row)
        rows.append(b"\x00" + row)
    raw = b"".join(rows)

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)
    return Path(path)


def esc(value):
    return (str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))
