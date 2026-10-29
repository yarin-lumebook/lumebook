#!/usr/bin/env python3
"""The story copy format (carousel/carousel-pipeline/story-format.md, Yarin 29 Oct 2026): constants and helpers that the
validator, nightly start, the renderer and the review pages share.

Yarin, 29 Oct 2026, after the five Lotem-format carousels (media/projects/2026-10-29-lotem-format-carousels/): "i like the
new content, change the entire carousel machine and November batch to match it", after "too little text so the slides are
not coherent enough and the format is too repetitive" and "why is it always 8 things? why always lists?".

A pack is in the story format when it has "copy_style": "story" at the top level (is_story). Everything here applies only
to those packs; older packs keep their rules in carousel_lib.

Body markup (story-format.md section 3), one marker per line:
    ## text        a small gold label (up to 26 characters)
    > ״...״        a cream card with a sentence the parent can say (at most one per slide)
    **word**       gold emphasis (at most 2 per slide)
    an empty line  a paragraph gap

Standard library only, and no import of carousel_lib, so carousel_lib can import this module.
"""

import hashlib
import itertools
import re

COPY_STYLE = "story"

# ---------------------------------------------------------------------------
# Structures (story-format.md section 1)
# ---------------------------------------------------------------------------

STRUCTURES = {
    "before_after": "פעם, ואז, ומאז: איך היה, מה השתנה, מה אני עושה עכשיו ולמה",
    "letter": "מכתב ממני אליכם, חתום בשם שלי",
    "thoughts_answers": "אתם חושבים, ואני עונה",
    "one_minute": "רגע קשה אחד, שנייה אחרי שנייה, ומה עוזר אחריו",
    "one_day": "יום אחד שלי לפי השעון, מהבוקר עד המיטה",
    "short_list": "רשימה קצרה, 3 עד 5 נקודות בלבד",
}
STRUCTURE_IDS = tuple(STRUCTURES)
STRUCTURES_EN = {
    "before_after": "before and after: 2 to 3 slides labelled פעם, one ואז (the change), 3 to 5 ומאז (what I do now and why), "
                    "one slide of what brings back פעם, then a turn back to the parents",
    "letter": "a letter from the child: slide 2 headline אמא שלי, (both parents: אמא ואבא שלי,), the following slides have no "
              "headline (body only), the last letter slide ends with the signature line **אוהב, NAME** / **אוהבת, NAME**; no labels",
    "thoughts_answers": "slide 2 sets up (אני רואה איך אתם מסתכלים עליי...), then each slide is labelled אתם חושבים: (mom: את חושבת:), "
                        "its headline is the parent's thought in ״...״ and its body the child's answer under ## אני עונה: and/or "
                        "## מה יעזור לי:, the last one labelled ואחרונה:",
    "one_minute": "one hard moment slowed down second by second (labels הדקה מתחילה, עשר שניות, עשרים שניות...), then what helps after (בערב)",
    "one_day": "one day of the child by the clock, morning to bed, every story slide labelled HH:MM, place (07:30, בבוקר ... 20:00, במיטה)",
    "short_list": "a short list of 3 to 5 points only, each point slide labelled N: short title with a monologue body, neighbouring "
                  "point slides in different shapes",
}
PACK_MIN_STRUCTURES = 4        # at least 4 different structures among the 6 options
STRUCTURE_MAX_PER_PACK = 2     # none more than twice
SHORT_LIST_MAX_PER_PACK = 1    # short_list at most once
RECENT_PACKS = 3               # nightly start rotates away from the structures of the previous 3 packs

# ---------------------------------------------------------------------------
# Slides (story-format.md section 2)
# ---------------------------------------------------------------------------

SLIDES_MIN, SLIDES_MAX = 9, 12           # the cover, 7 to 10 story slides, the CTA
ROLE_HOOK, ROLE_BEAT, ROLE_TURN, ROLE_CTA = "hook", "beat", "turn", "story_cta"
ROLES = (ROLE_HOOK, ROLE_BEAT, ROLE_TURN, ROLE_CTA)
ROLE_LABELS_HE = {ROLE_HOOK: "כריכה", ROLE_BEAT: "שקופית סיפור", ROLE_TURN: "פנייה להורים", ROLE_CTA: "שמירה"}
LABEL_MAX_CHARS = 28                     # the slide's `label`
COVER_PILL_MAX_CHARS = 34                # slide 1 body
COVER_HEADLINE_MAX_LINES, COVER_HEADLINE_LINE_MAX_CHARS = 3, 18
HEADLINE_MAX_LINES, HEADLINE_LINE_MAX_CHARS = 2, 26
BODY_LINE_MAX_CHARS, BODY_LINE_MAX_WORDS = 38, 12
SLIDE_MIN_WORDS, SLIDE_MAX_WORDS = 15, 50   # story slides, headline + body, markup not counted

# ---------------------------------------------------------------------------
# Markup (story-format.md section 3)
# ---------------------------------------------------------------------------

MARK_LABEL_MAX_CHARS = 26
CARDS_MAX = 1
EMPHASIS_MAX = 2
LABEL_LINE_RE = re.compile(r"^##\s+(\S.*)$")
CARD_LINE_RE = re.compile(r"^>\s*(\S.*)$")
EMPHASIS_RE = re.compile(r"\*\*(.+?)\*\*")
WORD_RE = re.compile(r"[\w֐-׿]", re.UNICODE)
HELP_LABEL_RE = re.compile(r"^(?:מה\s+יעזור\s+ל|אני\s+עונה)")   # ## מה יעזור לי:, ## מה יעזור לי לשמוע:, ## אני עונה:
SEE_LABEL_RE = re.compile(r"^מה\s+(?:אתם\s+רואים|את\s+רואה)")
INSIDE_LABEL_RE = re.compile(r"^מה\s+קורה\s+לי")

# ---------------------------------------------------------------------------
# Per-structure labels and lines
# ---------------------------------------------------------------------------

BEFORE, THEN, SINCE = "פעם", "ואז", "ומאז"
BEFORE_SLIDES = (2, 3)
SINCE_SLIDES = (3, 5)
LETTER_OPENINGS = {"mom": "אמא שלי,", "parents": "אמא ואבא שלי,"}
LETTER_SIGN_WORD = {"boy": "אוהב", "girl": "אוהבת"}
THOUGHT_LABELS = {"mom": "את חושבת:", "parents": "אתם חושבים:"}
THOUGHT_LAST_LABEL = "ואחרונה:"
MINUTE_START = "הדקה מתחילה"
MINUTE_TICK_RE = re.compile(r"שני(?:ות|יה|ה)|דקה|דקות")
MINUTE_MIN_TICKS = 3
TIME_LABEL_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d),\s*\S")
DAY_FIRST_BEFORE = 12 * 60     # the day starts in the morning
DAY_LAST_FROM = 18 * 60        # and ends in the evening or in bed
DAY_MIN_TIMES = 5
POINT_LABEL_RE = re.compile(r"^(\d):\s*(\S.*)$")
SHORT_LIST_MIN_POINTS, SHORT_LIST_MAX_POINTS = 3, 5
HELP_ACTIONS_MIN = 3           # sourced claims behind the help actions of one option (story-format.md section 5)
BRIDGE_LINES = {"boy": "ובערב אפשר להמשיך עם סיפור שבו אני הגיבור", "girl": "ובערב אפשר להמשיך עם סיפור שבו אני הגיבורה"}

# A cover that promises a number of things («6 דברים», «שלושה משפטים»): only a short_list may do that.
_NUMBER_WORDS = r"שלוש(?:ה)?|ארבע(?:ה)?|חמש(?:ה)?|שש(?:ה)?|שבע(?:ה)?|שמונה|תשע(?:ה)?|עשר(?:ה)?|שני|שתי"
_NUMBER_VALUES = {"שני": 2, "שתי": 2, "שלוש": 3, "שלושה": 3, "ארבע": 4, "ארבעה": 4, "חמש": 5, "חמישה": 5, "חמשה": 5, "שש": 6, "שישה": 6,
                  "ששה": 6, "שבע": 7, "שבעה": 7, "שמונה": 8, "תשע": 9, "תשעה": 9, "עשר": 10, "עשרה": 10}
_LIST_NOUNS = r"דברים|סיבות|טיפים|דרכים|משפטים|שאלות|סימנים|צעדים|רגעים|כללים|טעויות|נקודות|רעיונות|מילים"
COVER_COUNT_RE = re.compile(rf"(?<![\dא-ת])(\d{{1,2}}|{_NUMBER_WORDS})\s+(?:{_LIST_NOUNS})(?![א-ת])")

# Scenes are pictures without writing (story-format.md section 4)
SCENE_FIELDS = ("action", "setting")
SCENE_TEXT_RE = re.compile(r"\b(?:text|words?|letters?|lettering|writing|written|captions?|subtitles?|numerals?|digits?|logos?|"
                           r"signs?\s+(?:that\s+says|saying|reading))\b|\d{1,2}:\d{2}", re.I)


def is_story(pack):
    """True for a pack in the story format ("copy_style": "story")."""
    return isinstance(pack, dict) and pack.get("copy_style") == COPY_STYLE


# ---------------------------------------------------------------------------
# Markup parsing
# ---------------------------------------------------------------------------

def strip_markup(text):
    """The text as read: `## ` and `> ` line markers and `**` removed, line breaks (and blank lines) kept."""
    out = []
    for line in str(text or "").split("\n"):
        s = line.strip()
        m = LABEL_LINE_RE.match(s) or CARD_LINE_RE.match(s)
        if m:
            s = m.group(1)
        out.append(s.replace("**", ""))
    return "\n".join(out)


def plain_lines(text):
    """Non-empty lines without markup."""
    return [ln.strip() for ln in strip_markup(text).split("\n") if ln.strip()]


def words(text):
    """Words without markup: whitespace tokens that contain a letter or digit."""
    return [t for t in strip_markup(text).split() if WORD_RE.search(t)]


def word_count(*texts):
    return sum(len(words(t)) for t in texts)


def emphasis(text):
    """The **emphasised** phrases of a text, in order."""
    return EMPHASIS_RE.findall(str(text or ""))


def parse_body(text):
    """The body as blocks, in order: {"kind": "label" | "card" | "line" | "gap", "text": the words without markup,
    "raw": the line as written, "emphasis": [phrases]}. Consecutive blank lines make one gap; leading and trailing gaps
    are dropped. This is what the renderer draws and what the validator measures."""
    blocks = []
    for line in str(text or "").split("\n"):
        s = line.strip()
        if not s:
            if blocks and blocks[-1]["kind"] != "gap":
                blocks.append({"kind": "gap", "text": "", "raw": "", "emphasis": []})
            continue
        m = LABEL_LINE_RE.match(s)
        kind = "label" if m else None
        if not m:
            m = CARD_LINE_RE.match(s)
            kind = "card" if m else "line"
        inner = m.group(1) if m else s
        blocks.append({"kind": kind, "text": inner.replace("**", ""), "raw": s, "emphasis": EMPHASIS_RE.findall(inner)})
    while blocks and blocks[-1]["kind"] == "gap":
        blocks.pop()
    return blocks


def labels_in(text):
    """The `## ` labels of a body, without the marker."""
    return [b["text"] for b in parse_body(text) if b["kind"] == "label"]


def has_help(text):
    """True when the body has a help label (## מה יעזור לי: ... or ## אני עונה:)."""
    return any(HELP_LABEL_RE.match(lbl) for lbl in labels_in(text))


def markup_problems(text):
    """What is wrong with the markup of one body, as plain sentences (the validator turns them into issues)."""
    out = []
    raw = str(text or "")
    if raw.count("**") % 2:
        out.append("an emphasis marker ** is not closed: write **word** around the word")
    for b in parse_body(raw):
        if b["kind"] == "label":
            if len(b["text"]) > MARK_LABEL_MAX_CHARS:
                out.append(f"the label «{b['text']}» has {len(b['text'])} characters (max {MARK_LABEL_MAX_CHARS})")
            if b["emphasis"]:
                out.append(f"no emphasis inside a label: «{b['raw']}»")
        if "#" in b["text"] or (b["kind"] != "card" and b["raw"].startswith(">")):
            out.append(f"a stray markup character: «{b['raw']}» (## and > start a line, followed by a space)")
    cards = sum(1 for b in parse_body(raw) if b["kind"] == "card")
    if cards > CARDS_MAX:
        out.append(f"{cards} card lines (> ...); at most {CARDS_MAX} sentence to say per slide")
    n = len(emphasis(raw))
    if n > EMPHASIS_MAX:
        out.append(f"{n} emphasised phrases (**...**); at most {EMPHASIS_MAX} per slide")
    return out


def shape(slide):
    """How a story slide looks: card (a sentence to say), see_inside (מה אתם רואים / מה קורה לי בפנים), question (the parents'
    question as the headline), beats (short lines on their own) or monologue."""
    blocks = parse_body(slide.get("body", ""))
    labels = [b["text"] for b in blocks if b["kind"] == "label"]
    if any(b["kind"] == "card" for b in blocks):
        return "card"
    if any(SEE_LABEL_RE.match(x) for x in labels) and any(INSIDE_LABEL_RE.match(x) for x in labels):
        return "see_inside"
    if strip_markup(slide.get("headline", "")).strip().rstrip("״\"").endswith("?"):
        return "question"
    lines = [b["text"] for b in blocks if b["kind"] == "line"]
    if len(lines) >= 3 and all(len(x.split()) <= 5 for x in lines):
        return "beats"
    return "monologue"


def cover_promise(text):
    """The number of things a cover promises («6 דברים» -> 6), or None."""
    m = COVER_COUNT_RE.search(strip_markup(text))
    if not m:
        return None
    n = m.group(1)
    return int(n) if n.isdigit() else _NUMBER_VALUES.get(n)


def time_minutes(label):
    """Minutes since midnight of a one_day label (07:30, בבוקר -> 450), or None."""
    m = TIME_LABEL_RE.match(str(label or "").strip())
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def signature_line(gender, name):
    return f"**{LETTER_SIGN_WORD.get(gender, 'אוהבת')}, {name}**"


def story_slides(version):
    """The slides between the cover and the CTA."""
    return (version.get("slides") or [])[1:-1]


# ---------------------------------------------------------------------------
# Structure assignment for nightly start
# ---------------------------------------------------------------------------

def distribution_problems(structures_by_option, lanes):
    """Why an assignment {option id: structure} breaks the per-pack rules (empty list = fine)."""
    out = []
    got = [s for s in structures_by_option.values() if s]
    counts = {s: got.count(s) for s in set(got)}
    if len(counts) < PACK_MIN_STRUCTURES:
        out.append(f"the six options use {len(counts)} structures (needs at least {PACK_MIN_STRUCTURES} different ones)")
    for s, n in sorted(counts.items()):
        cap = SHORT_LIST_MAX_PER_PACK if s == "short_list" else STRUCTURE_MAX_PER_PACK
        if n > cap:
            out.append(f"{s} is used {n} times (max {cap})")
    for lane, ids in lanes:
        mine = [structures_by_option.get(i) for i in ids if structures_by_option.get(i)]
        if len(set(mine)) != len(mine):
            out.append(f"the options of topic {lane} ({', '.join(ids)}) need three different structures")
    return out


def assign_structures(lanes, recent_counts=None, seed=""):
    """{option id: structure} that satisfies the per-pack rules and uses the structures of the previous packs as little as
    possible (recent_counts {structure: times used}). The seed (the date) breaks ties, so a rerun for the same date gets the
    same assignment and different dates differ."""
    recent_counts = recent_counts or {}
    ids = [i for _, lane_ids in lanes for i in lane_ids]
    rank = {s: int(hashlib.sha256(f"{seed}:{s}".encode()).hexdigest(), 16) % 1000 for s in STRUCTURE_IDS}
    best, best_key = None, None
    lane_perms = [list(itertools.permutations(STRUCTURE_IDS, len(lane_ids))) for _, lane_ids in lanes]
    for combo in itertools.product(*lane_perms):
        chosen = [s for lane in combo for s in lane]
        assignment = dict(zip(ids, chosen))
        if distribution_problems(assignment, lanes):
            continue
        key = (sum(recent_counts.get(s, 0) for s in chosen),          # rotate away from recent structures
               -len(set(chosen)),                                     # prefer more variety
               sum(rank[s] * (k + 1) for k, s in enumerate(chosen)))  # stable, date-seeded tie break
        if best_key is None or key < best_key:
            best, best_key = assignment, key
    return best
