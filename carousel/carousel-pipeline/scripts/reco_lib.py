#!/usr/bin/env python3
"""Rules, rotation and validation for the daily recommendation carousel.

Every nightly run adds one complete games-and-books carousel next to the kid and expert pack (Yarin, 14 Oct 2026:
"combine the book and games to one carousel. 10-20 slides"):

    drafts/DATE/reco-carousel.json     format "mixed": 7 to 9 suggestions for one developmental stage, at least 3 real
                                       games and at least 3 real books (mixed in order since 16 Oct 2026) + the LumeBook book, 10 to 12 slides

Nights up to 13 Oct 2026 have two separate carousels instead, which stay valid and renderable:

    drafts/DATE/games-carousel.json    format "games": 3 to 7 suggestions (real games + the LumeBook book)
    drafts/DATE/books-carousel.json    format "books": 3 to 7 suggestions (real books + the LumeBook book)

Each product must be popular or clearly established in Israel (Israel-specific evidence, never inferred from
international popularity), each recommendation slide centres a real product image from an authoritative source,
and LumeBook is named once, as the second to last suggestion, in the same format as the others. No image generation, no paid API, nothing is posted.

    python3 carousel/carousel-pipeline/scripts/reco_lib.py PATH/reco-carousel.json         # validate one file
    python3 carousel/carousel-pipeline/scripts/reco_lib.py PATH/games-carousel.json --json

The Hebrew hard rules (punctuation, jargon, guarantees, never dad, never AI) come from carousel_lib so there is
one definition of the voice rules. Format rules: carousel/carousel-pipeline/recommendations.md.
Standard library only.
"""

import argparse
import datetime as dt
import itertools
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402

SCHEMA = lib.PIPELINE / "reco.schema.json"
HISTORY = lib.PIPELINE / "reco-history.json"
MIXED = "mixed"
MIXED2 = "mixed2"                        # the second games and books carousel of a weekly batch pack (16 Oct 2026), same rules
MIXED_FORMATS = (MIXED, MIXED2)
LEGACY_FORMATS = ("games", "books")      # the two separate carousels of the nights up to 13 Oct 2026
FORMATS = MIXED_FORMATS + LEGACY_FORMATS # every format the validator, the renderer and the review pages know
NIGHTLY_FORMATS = (MIXED,)               # what nightly.py start draws and finish-reco expects (from 14 Oct 2026)
BATCH_FORMATS = MIXED_FORMATS            # a pack of the weekly batch has two (Yarin, 16 Oct 2026: 14 a week for 7 packs)
# Yarin, 18 Oct 2026: "i dont want the games and books carousels anymore". No new ones are planned or drawn; the ones
# already made still validate, render, show in Carousel Machine and export. Set True to bring them back.
ACTIVE = False
FILES = {MIXED: "reco-carousel.json", MIXED2: "reco-carousel-2.json", "games": "games-carousel.json", "books": "books-carousel.json"}
OUT_DIRS = {MIXED: "reco", MIXED2: "reco-2", "games": "games", "books": "books"}  # drafts/DATE/<dir>/: slides.html, 01.png..., contact sheet
ASSETS_DIR = "reco-assets"  # product and LumeBook images, inside drafts/DATE/ (both mixed carousels share it)
FORMAT_HE = {MIXED: "משחקים וספרים", MIXED2: "משחקים וספרים 2", "games": "משחקים", "books": "ספרים"}
KIND_OF = {"games": "game", "books": "book"}
KIND_HE = {"game": "משחק", "book": "ספר"}

# Every night draws how many suggestions the carousel has, and the LumeBook book counts as one of them (Yarin, 8 Oct 2026).
# The carousel is hook, frame, N suggestions, close: N + 3 slides. Mixed (Yarin, 14 Oct 2026): 7 to 9, so 10 to 12 slides,
# with at least 3 games and at least 3 books. The old games and books carousels: 3 to 7, so 6 to 10 slides.
OPTIONS_MIN, OPTIONS_MAX = 3, 7                  # games and books (older nights)
MIXED_OPTIONS_MIN, MIXED_OPTIONS_MAX = 7, 9      # mixed (Yarin, 14 Oct 2026: "cap it to 7-9 books and games")
SIZES = {MIXED: (MIXED_OPTIONS_MIN, MIXED_OPTIONS_MAX), MIXED2: (MIXED_OPTIONS_MIN, MIXED_OPTIONS_MAX), "games": (OPTIONS_MIN, OPTIONS_MAX), "books": (OPTIONS_MIN, OPTIONS_MAX)}
MIXED_MIN_PER_KIND = 3                           # a mixed carousel has at least 3 games and at least 3 books
SLOTS_FILE = "reco-slots.json"  # drafts/DATE/: tonight's draw, kept so a rerun builds the same size


def size_range(fmt):
    return SIZES.get(fmt, (OPTIONS_MIN, OPTIONS_MAX))


def layout(n_options):
    """Slide roles for a carousel with n_options suggestions (the LumeBook book included). The LumeBook book is the
    second to last suggestion, offered casually like one of the options (Yarin, 8 Oct 2026)."""
    n_options = int(n_options)
    lumebook = n_options + 1
    roles = {1: "hook", 2: "frame"}
    for n in range(3, n_options + 3):
        roles[n] = "lumebook" if n == lumebook else "recommendation"
    close = n_options + 3
    roles[close] = "close"
    return {"options": n_options, "total": close, "roles": roles, "lumebook_slide": lumebook, "close_slide": close,
            "rec_slides": tuple(n for n, r in roles.items() if r == "recommendation")}


def draw_slots(folder, formats=NIGHTLY_FORMATS, rng=None):
    """Tonight's random sizes {format: n} (mixed: 7..9). The first call for a date draws and saves them to
    reco-slots.json, later calls (a rerun) read the same numbers back, so one night never changes size by itself."""
    import random
    path = Path(folder) / SLOTS_FILE
    saved = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    rng = rng or random.SystemRandom()
    changed = False
    for f in formats:
        lo, hi = size_range(f)
        if not isinstance(saved.get(f), int) or not lo <= saved[f] <= hi:
            saved[f] = rng.randint(lo, hi)
            changed = True
    if changed:
        saved["drawn_at"] = lib.now_local().isoformat(timespec="seconds")
        lib.write_json(path, saved)
    return {f: saved[f] for f in formats}
# The LumeBook slide (Yarin, 8 Oct 2026): "ספר של LumeBook" / "סיפור מותאם אישית עם תמונה של הילד שלכם שבו... X",
# next to a 3D book from lumebook.com with the real child photo in a small circle (the site's hero renders).
LUMEBOOK_BODY_RE = re.compile(r"מותאם\s+אישית")
LUMEBOOK_PHOTO_RE = re.compile(r"תמונה|תמונת|תמונות")
ROLE_LABELS_HE = {"hook": "פתיח", "frame": "מה מתרגלים בגיל הזה", "recommendation": "המלצה", "lumebook": "לומבוק", "close": "סיכום"}

PRODUCT_COOLDOWN_DAYS = 30      # the brief: no product twice within 30 days unless a seasonal reason is documented
SKILL_COOLDOWN_RUNS = 4         # same format: a skill may not return within its last 4 carousels
STAGE_COOLDOWN_DAYS = 14        # same format: the same stage id may not return within 14 days
MAKER_WARN_DAYS = 14            # same author, publisher or manufacturer within 14 days: a reviewer warning
FRESH_DAYS = 3                  # availability, popularity and product facts must be checked within 3 days of the run
SITE_FACT_DAYS = 2              # live-site LumeBook facts, same rule as the kid and expert pack

# Developmental areas (the brief's list). keywords_he: words that show a slide talks about this skill.
SKILLS = {
    "language_vocabulary": {"he": "שפה ואוצר מילים", "keywords_he": r"מיל(?:ה|ים|ות)|לדבר|מדבר|שפה|לספר|לתאר|שמות"},
    "fine_motor": {"he": "מוטוריקה עדינה", "keywords_he": r"אצבע|לגזור|להשחיל|לתפוס|לצבוט|ידיים|יד"},
    "gross_motor": {"he": "מוטוריקה גסה", "keywords_he": r"לקפוץ|לרוץ|לטפס|שיווי|גוף|לזרוק"},
    "imagination": {"he": "דמיון", "keywords_he": r"דמיון|לדמיין|להעמיד פנים|משחק תפקידים|ממציא"},
    "early_literacy": {"he": "אוריינות ראשונית", "keywords_he": r"לספר|מספר|לנחש|מה יקרה|סיפור|לקרוא|קוראים|מילים|לחזור|חוזר"},
    "problem_solving": {"he": "פתרון בעיות", "keywords_he": r"לפתור|פתרון|לתכנן|לנסות|דרך אחרת|לחשוב"},
    "memory": {"he": "זיכרון", "keywords_he": r"לזכור|זוכר|זיכרון|איפה היה"},
    "emotional_understanding": {"he": "הבנת רגשות", "keywords_he": r"רגש|מרגיש|כועס|עצוב|שמח|מפחד|לקרוא בשם"},
    "turn_taking": {"he": "לחכות לתור", "keywords_he": r"תור|לחכות|מחכ|לסירוגין|אחרי ש"},
    "cooperation": {"he": "שיתוף פעולה", "keywords_he": r"ביחד|יחד|צוות|לעזור|שיתוף|משותף"},
    "independence": {"he": "עצמאות", "keywords_he": r"לבד|בעצמו|בעצמה|עצמאי"},
    "attention_self_regulation": {"he": "קשב וויסות עצמי", "keywords_he": r"להתרכז|לחכות|לעצור|קשב|להקשיב|לשים לב"},
    "early_numeracy": {"he": "חשבון ראשוני", "keywords_he": r"לספור|סופר|מספר|כמה|יותר|פחות|\d"},
}

# Slide 1 is always one sentence (Yarin, 9 Oct 2026):
#   mixed: "X משחקים וספרים לגילאי A-B ש(במה הם עוזרים)" (14 Oct 2026; the ages since Yarin's "add what ages are
#          they suitable for", same day, as on his reference slide "4 משחקי קופסא לגילאי 5-6 שעוזרים לילדים לשים לב")
#   games: "X משחקי קופסא ש(במה הם עוזרים)"    books: "X ספרי ילדים ש(במה הם עוזרים)"   (older nights)
# The X is the number of suggestions, the LumeBook book included. Older nights: no ages in the hook (Yarin, 9 Oct 2026).
HOOK_STRUCTURES = {"count_ages_skill": "X משחקים וספרים לגילאי A-B ש(במה הם עוזרים); older nights X משחקי קופסא / X ספרי ילדים ש..."}
HOOK_TEMPLATE_RE = {
    MIXED: re.compile(r"^(\d+)\s+משחקים\s+וספרים\s+(?:לגילאי\s+(\d+)\s*-\s*(\d+)|לגיל\s+(\d+))\s+ש[א-ת]+(?:\s+\S+)*$"),
    "games": re.compile(r"^(\d+)\s+משחקי\s+קופסא\s+ש[א-ת]+(?:\s+\S+)*$"),
    "books": re.compile(r"^(\d+)\s+ספרי\s+ילדים\s+ש[א-ת]+(?:\s+\S+)*$"),
}
HOOK_TEMPLATE_RE[MIXED2] = HOOK_TEMPLATE_RE[MIXED]
HOOK_TEMPLATE_HE = {MIXED: "X משחקים וספרים לגילאי A-B ש...", "games": "X משחקי קופסא ש...", "books": "X ספרי ילדים ש..."}
HOOK_TEMPLATE_HE[MIXED2] = HOOK_TEMPLATE_HE[MIXED]
# Carousel Machine (Yarin, 10 Oct 2026: click baity hooks, content and slide design for every carousel). The sentence
# stays Yarin's; the ending and the type get louder. Carousels written from this moment name the phrase that gets the
# colour block (`highlight`) on the hook and the frame slide and record the wordings they weighed (`hook_alternatives`).
REQUIRE_HIGHLIGHT_ROLES = ("hook", "frame")


def bold_applies(car):
    return lib.bold_rule_applies(car)


HOOK_AGE_RE = re.compile(r"גיל|לגילאי|בני\s+\d|בנות\s+\d|\d+\s*-\s*\d+")  # Yarin, 9 Oct 2026: no ages in the hook
# Always plural (Yarin, 9 Oct 2026). Left out on purpose: ספרי (also 'books of', as in ספרי ילדים) and אותו/אותה
# (also 'the same'). Always plural (Yarin, 9 Oct 2026): talk to both parents and about children in the plural. Text inside quotes
# (a sentence a parent says to a child, a character's name or line) is exempt.
SINGULAR_CHILD_RE = re.compile(r"(?<![א-ת])(?:ו|ש|כש|ל|ה|ב|מ|כ)*(?:ילד|ילדה)(?![א-ת])")
SINGULAR_YOU_RE = re.compile(r"(?<![א-ת])(?:ו|ש|כש)?(?:שלך|לך|אותך|איתך|בשבילך|עלייך|אלייך)(?![א-ת])")
FEM_COMMAND_RE = re.compile(r"(?<![א-ת])(?:ו)?(?:שאלי|עצרי|תני|שמרי|נסי|בואי|תגידי|תקריאי|כתבי|חפשי|קראי|שימי|התחילי|אפשרי|בקשי|שלחי|תשמרי|תספרי|הזמיני|שחקי|הסבירי)(?![א-ת])")
SINGULAR_PRONOUN_RE = re.compile(r"(?<![א-ת])(?:ו|ש|כש)?(?:הוא|היא|לו|לה|שלו|שלה)(?![א-ת])")
QUOTED_RE = re.compile(r"״[^״]*״|\"[^\"]*\"|“[^”]*”")

# Israel-specific popularity evidence. One strong signal is enough for popular_in_israel; otherwise two
# independent signals (different `group`) are needed. Stocked locally only = available_in_israel.
STRONG_SIGNALS = {"bestseller_list", "retailer_ranking", "sifriyat_pijama"}
RANKING_STRONG_TOP = 20       # a retailer ranking is strong at position 20 or better ...
RANKING_STRONG_SHARE = 0.10   # ... or inside the top 10 percent of the ranked list (record rank and out_of)
SUPPORTING_SIGNALS = {"prominent_placement", "multi_retailer", "hebrew_edition_established_publisher", "credible_recommendation",
                      "review_volume", "social_attention", "award_israel", "library"}
SIGNAL_HE = {
    "bestseller_list": "רשימת רבי מכר ישראלית", "retailer_ranking": "דירוג אצל קמעונאי ישראלי",
    "sifriyat_pijama": "נבחר והופץ בספריית פיג'מה", "prominent_placement": "מיקום בולט ברשת ישראלית",
    "multi_retailer": "נמכר בכמה חנויות ישראליות עצמאיות", "hebrew_edition_established_publisher": "מהדורה עברית בהוצאה מבוססת",
    "credible_recommendation": "המלצה ממקור ישראלי אמין", "review_volume": "כמות ביקורות ישראליות", "social_attention": "תשומת לב ברשתות בישראל",
    "award_israel": "פרס ישראלי", "library": "ספריות ציבוריות בישראל",
}
POPULARITY_HE = {"popular_in_israel": "פופולרי בישראל", "available_in_israel": "זמין בישראל בלבד"}
RIGHTS_HE = {"owned": "שלנו", "cleared": "זכויות מאושרות", "rights_unverified": "rights_unverified · זכויות לא מאומתות"}
PUBLISHABLE_RIGHTS = {"owned", "cleared"}

# Where product and cover images may come from. Never a search engine, a pin board or an image generator.
PRODUCT_IMAGE_SOURCES = {"publisher", "manufacturer", "official", "israeli_retailer", "sifriyat_pijama"}
LUMEBOOK_IMAGE_SOURCES = {"lumebook_site", "lumebook_repo"}
# Yarin, 10 Oct 2026: "i want the lumebook image to depict the idea of the caption". The picture on the LumeBook slide is the
# cover of the catalogue book whose idea the slide's line states (lumebook.com/book_covers/<boy|girl>/B<id>_<boy|girl>.avif,
# LumeBook's own art), not a homepage hero render. Required in carousels generated from LUMEBOOK_COVER_FROM; older ones keep the hero.
LUMEBOOK_COVER_RE = re.compile(r"^https://lumebook\.com/book_covers/(boy|girl)/B(\d+)_(boy|girl)\.avif$")
LUMEBOOK_COVER_FROM = "2026-10-10T22:00"
# The games and the books are mixed on carousels generated from MIXED_ORDER_FROM (Yarin, 16 Oct 2026: "in the book and
# games i want it to mix their order instead of games and then books"); older ones keep every game first, then the books.
MIXED_ORDER_FROM = "2026-10-16T12:00"
MIXED_ORDER_MAX_RUN = 2


def mixed_order_applies(car):
    return str((car or {}).get("generated_at", ""))[:16] >= MIXED_ORDER_FROM


def cover_rule_applies(car):
    return str((car or {}).get("generated_at", ""))[:16] >= LUMEBOOK_COVER_FROM


def lumebook_cover_issues(P, car):
    lb = car.get("lumebook") or {}
    img = lb.get("image") or {}
    m = LUMEBOOK_COVER_RE.match(str(img.get("image_url", "")))
    if not m:
        if cover_rule_applies(car):
            return [issue("ERROR", f"{P}/lumebook/image/image_url", "the LumeBook picture is the cover of the catalogue book whose idea the slide's line states: https://lumebook.com/book_covers/boy/B<id>_boy.avif or .../girl/B<id>_girl.avif (Yarin, 10 Oct 2026), not a homepage render", "lumebook")]
        return []
    issues = []
    if m.group(1) != m.group(3):
        issues.append(issue("ERROR", f"{P}/lumebook/image/image_url", "the folder and the file name must agree (boy/B<id>_boy, girl/B<id>_girl)", "lumebook"))
    if lb.get("catalogue_book_id") != int(m.group(2)):
        issues.append(issue("ERROR", f"{P}/lumebook/catalogue_book_id", f"the cover is book {int(m.group(2))}; catalogue_book_id says {lb.get('catalogue_book_id')}", "lumebook"))
    if not str(lb.get("catalogue_book", "")).strip():
        issues.append(issue("ERROR", f"{P}/lumebook/catalogue_book", "name the catalogue book the cover belongs to", "lumebook"))
    if len(str(img.get("depicts", "")).strip()) < 20:
        issues.append(issue("ERROR", f"{P}/lumebook/image/depicts", "open the cover and say in `depicts` what it shows and how that is the idea of the slide's line (the picture must depict it)", "lumebook"))
    return issues
BLOCKED_IMAGE_HOSTS = re.compile(r"(^|\.)(google\.|gstatic\.com|googleusercontent\.com|bing\.com|pinterest\.|pinimg\.com|fal\.media|fal\.ai|fal\.run|"
                                 r"oaiusercontent\.com|openai\.com|midjourney\.com|replicate\.delivery|stability\.ai|lexica\.art|ideogram\.ai)")
IMAGE_MAGIC = {b"\x89PNG": "png", b"\xff\xd8\xff": "jpg", b"RIFF": "webp", b"GIF8": "gif"}
MIN_IMAGE_SIDE = 500

# Credible developmental sources. Anything else must be peer reviewed research with a DOI or journal URL.
DEV_SOURCE_HOSTS = re.compile(r"(^|\.)(cdc\.gov|aap\.org|healthychildren\.org|zerotothree\.org|childmind\.org|kidshealth\.org|nemours\.org|"
                              r"nih\.gov|ed\.gov|aappublications\.org|who\.int|unicef\.org|harvard\.edu|apa\.org|nhs\.uk|raisingchildren\.net\.au|education\.gov\.il|gov\.il|"
                              r"doi\.org|sciencedirect\.com|springer\.com|wiley\.com|tandfonline\.com|sagepub\.com|frontiersin\.org|nature\.com|"
                              r"jstor\.org|cambridge\.org|oup\.com|plos\.org|mdpi\.com)$")

# Copy rules specific to recommendations, on top of carousel_lib's hard rules
ACTIVITY_RE = re.compile(r"(?<![א-ת])(?:ו|ש|כש|ל|ב|ה)?(?:לחכות|מחכ\w*|תור\w*|להתאים|מתאימ\w*|התאמה|לספר|מספר\w*|לנחש|מנחש\w*|לבנות|בונ\w*|למיין|ממיינ\w*|"
                         r"לתכנן|מתכננ\w*|לזכור|זוכר\w*|לספור|סופר\w*|לגלגל|מגלגל\w*|להטיל|מטיל\w*|לחפש|מחפש\w*|לקרוא|קורא\w*|לחזור|חוזר\w*|לשיר|"
                         r"לדמיין|להצביע|מצביע\w*|לאסוף|אוספ\w*|אוסף|להפסיד|מפסיד\w*|לנצח|מנצח\w*|לעזור|עוזר\w*|ביחד|יחד|לסדר|מסדר\w*|לזהות|מזה\w*|"
                         r"לשאול|שואל\w*|להשלים|משלימ\w*|לבחור|בוחר\w*|לשלוף|שולפ\w*|לסובב|מסובב\w*|להפוך|הופכ\w*|לגלות|מגל\w*|לענות|עונ\w*|"
                         r"לחקות|לתאר|מתאר\w*|לעצור|עוצר\w*|לקפוץ|לזרוק|להשחיל|לגזור|לצייר|לקרוא בשם|לדבר|מדבר\w*)(?![א-ת])")
VAGUE_RE = re.compile(r"מעולה להתפתחות|טוב להתפתחות|מפתח את הילד|מפתח חשיבה|משחק התפתחותי|ספר התפתחותי|מחכימ|חכם יותר|חכמה יותר|"
                      r"חכמים יותר|גאון|מוח|מושלם ל|הכי טוב|חובה בכל בית|כל הורה חייב")
RECO_CLAIM_ERRORS = [
    (r"מבטיח|מובטח|בטוח ש", "guarantee"),
    (r"(?<![א-ת])(?:ו)?(?:יפתח|ישפר|משפר|משפרת|מחזק|מחזקת|יחזק|יגרום|גורם ל)(?![א-ת])", "promises a developmental result (write מתרגלים, יכול לעזור, הזדמנות ל)"),
    (r"(?<![א-ת])(?:ו)?(?:מטפל|מטפלת|טיפול|לטיפול|טיפולית)(?![א-ת])", "treatment claim"),
    (r"קשיי|עיכוב|לקות|אבחון", "medical or diagnostic wording"),
    (r"מומלץ על ידי רופאים|רופאים ממליצים|מומחים ממליצים", "authority claim without a named source"),
]
POPULARITY_WORDS_RE = re.compile(r"רב[י]?\s*מכר|הכי נמכר|הנמכר|פופולרי|להיט|כולם משחקים|בכל גן|בכל בית|קלאסיקה|אהוב על|הכי אהוב|ספר הבית")
SALES_RE = re.compile(r"הנחה|מבצע|קוד(?![םמ])|קופון|עכשיו|מהרו|מהרי|רק היום|לזמן מוגבל|אחרונים|נגמר|₪|שקל|מחיר|לקנות|להזמין|הזמינו|קנו|בחינם|חינם")
GUARANTEE_RE = re.compile(r"יבטיח|מבטיח|תמיד יעבוד|בטוח יעזור|יפתור|ישפר|יפתח")
CLOSE_PROMPT_RE = re.compile(r"(?<![א-ת])(?:ו)?(?:שמרי|שמרו|תשמרי|תשמרו|שלחי|שלחו|תשלחי|תשלחו|כתבי|כתבו|ספרי|ספרו|תספרי|תספרו|תייגי|תייגו|שתפי|שתפו)(?![א-ת])|בתגובות|בתגובה")
CLOSE_SALE_RE = re.compile(r"קישור|הנחה|לקנות|להזמין|מבצע|ספר שבו|הגיבור|הגיבורה|בהתאמה אישית|אישי")
# Masculine singular commands talk to dad. Only forms that cannot be read another way (תגיד is also "she will say",
# so it is caught only with an object: תגיד לו / תגיד לה).
MALE_COMMAND_RE = re.compile(r"(?<![א-ת])(?:ו)?(?:תן|שאל|שחק|שמור|כתוב|עצור|נסה|בוא|תעשה|תקריא)(?![א-ת])|(?<![א-ת])(?:ו)?תגיד\s+(?:לו|לה|לילד|לילדה)(?![א-ת])")
AGE_HEDGE_RE = re.compile(r"בערך|בסביבות|פחות או יותר|יש ילדים|בקצב של|בקצב שלו|בקצב שלה|לא אצל כולם|מתישהו|לפעמים|יש שמגיעים|כל אחד בזמן")
AGE_IN_TEXT_RE = re.compile(r"\d|גיל|בני |בנות |פעוט|גן חובה|טרום חובה")

HOOK_MAX_WORDS = 12
HOOK_MAIN_MAX_WORDS = 8
FRAME_MAX_WORDS = 30
WHY_MAX_WORDS = 16
HOW_MAX_WORDS = 16
REC_LINES_MAX = 2
LUMEBOOK_MAX_WORDS = 30
CLOSE_MAX_WORDS = 25
CLOSE_LINE_MAX_CHARS = 40
CAPTION_MIN_LINES, CAPTION_MAX_LINES = 3, 8

FLAG_HE = {
    "popularity": "חסרות ראיות לפופולריות בישראל",
    "dev_source": "מקור התפתחותי חלש או חסר",
    "age_fit": "התאמת גיל לא נכונה",
    "availability": "מוצר לא זמין או זמינות לא נבדקה",
    "image": "תמונה חסרה או ממקור לא מאושר",
    "rights": "זכויות התמונה לא מאומתות",
    "repeat": "מוצר או נושא שחוזר על עצמו",
    "claim": "טענה בלי תמיכה",
    "voice": "הפרה של כללי הקול והעברית",
    "structure": "מבנה הקרוסלה",
    "lumebook": "האזכור של לומבוק",
    "process": "תשלום, יצירת תמונות או פרסום",
}


def issue(level, path, message, flag, **kw):
    i = lib.Issue(level, path, message, **kw)
    i.flag = flag
    return i


def _flag(issues, flag):
    for i in issues:
        if not hasattr(i, "flag"):
            i.flag = flag
    return issues


def host(url):
    return (urlparse(str(url)).hostname or "").lower()


def is_israeli_url(url):
    return host(url).endswith(".il")


def norm_title(text):
    """Compare titles across line breaks and quote styles: ״ vs ", ׳ vs ', any whitespace."""
    t = str(text).replace("״", '"').replace("“", '"').replace("”", '"').replace("׳", "'").replace("’", "'")
    return " ".join(t.split())


def _days(a, b):
    return (lib.parse_date(a) - lib.parse_date(b)).days


def image_kind(path):
    with open(path, "rb") as fh:
        head = fh.read(12)
    for magic, kind in IMAGE_MAGIC.items():
        if head.startswith(magic):
            if kind == "webp" and head[8:12] != b"WEBP":
                continue
            return kind
    return None


# ---------------------------------------------------------------------------
# Paths and history
# ---------------------------------------------------------------------------

def carousel_path(folder, fmt):
    return Path(folder) / FILES[fmt]


def present(folder):
    """{format: path} for the recommendation carousels that exist in a draft folder (mixed, or the older games and books)."""
    return {f: carousel_path(folder, f) for f in FORMATS if carousel_path(folder, f).exists()}


def load_history(path=HISTORY):
    path = Path(path)
    if not path.exists():
        return {"carousels": []}
    return json.loads(path.read_text(encoding="utf-8"))


def previous(history, date_str, fmt=None, sibling_of=None):
    """Earlier carousels, newest first. A rerun for the same date and format ignores its own earlier entry.
    sibling_of: a mixed format; the other mixed carousel of the same date counts as earlier too (a batch pack has two)."""
    def earlier(c):
        if c["date"] < date_str:
            return True
        return sibling_of in MIXED_FORMATS and c["date"] == date_str and c.get("format") in MIXED_FORMATS and c.get("format") != sibling_of
    out = [c for c in history.get("carousels", []) if c.get("date") and earlier(c) and (fmt is None or c.get("format") == fmt)]
    return sorted(out, key=lambda c: c["date"], reverse=True)


def rotation_pool(history, date_str, fmt):
    """The earlier carousels a format rotates away from, newest first. The mixed carousel replaced both the games and the
    books carousel, so it rotates against every earlier entry (mixed, games and books); games and books keep their own."""
    return previous(history, date_str, None if fmt in MIXED_FORMATS else fmt, sibling_of=fmt)


def last_runs(prev, runs):
    """The entries of the last `runs` nights (two carousels on one older night count as one night)."""
    dates = sorted({c["date"] for c in prev}, reverse=True)[:runs]
    return [c for c in prev if c["date"] in dates]


def history_entry(car):
    return {
        "date": car["date"], "format": car["format"], "generated_at": car.get("generated_at"),
        "stage_id": car["stage"]["id"], "skill": car["stage"]["skill"],
        "age_min": car["stage"]["age_min"], "age_max": car["stage"]["age_max"],
        "hook_structure": car["hook_structure"], "hook": lib.collapse(car["slides"][0]["headline"]),
        "products": [{k: p.get(k, "") for k in ("id", "kind", "title_he", "author", "publisher", "manufacturer", "type")} for p in car["products"]],
        "popularity": {p["id"]: p["popularity_label"] for p in car["products"]},
    }


def record_history(car, path=HISTORY):
    """Insert or replace this date and format's entry (reruns are idempotent)."""
    history = load_history(path)
    entry = history_entry(car)
    kept = [c for c in history.get("carousels", []) if not (c.get("date") == car["date"] and c.get("format") == car["format"])]
    kept.append(entry)
    kept.sort(key=lambda c: (c["date"], c["format"]))
    history["carousels"] = kept
    lib.write_json(path, history)
    return entry


def rotation_context(history, date_str, formats=FORMATS):
    """What tonight's carousel should rotate away from. Products: every format within 30 days. Skills, stages, ages, hooks
    and makers: per format, where mixed looks at mixed, games and books entries alike (rotation_pool)."""
    day = lib.parse_date(date_str)
    out = {"product_cooldown_days": PRODUCT_COOLDOWN_DAYS}
    cutoff = (day - dt.timedelta(days=PRODUCT_COOLDOWN_DAYS)).isoformat()
    recent_all = [c for c in previous(history, date_str) if c["date"] >= cutoff]
    out["blocked_products"] = sorted({f"{p['id']} · {p['title_he']}" for c in recent_all for p in c.get("products", [])})
    for fmt in formats:
        prev = rotation_pool(history, date_str, fmt)
        maker_cut = (day - dt.timedelta(days=MAKER_WARN_DAYS)).isoformat()
        stage_cut = (day - dt.timedelta(days=STAGE_COOLDOWN_DAYS)).isoformat()
        out[fmt] = {
            "blocked_skills": sorted({c["skill"] for c in last_runs(prev, SKILL_COOLDOWN_RUNS)}),
            "blocked_stage_ids": sorted({c["stage_id"] for c in prev if c["date"] >= stage_cut}),
            "last_age_range": [prev[0]["age_min"], prev[0]["age_max"]] if prev else None,
            "last_hook_structure": prev[0]["hook_structure"] if prev else None,
            "recent_hooks": [c.get("hook") for c in prev[:14]],
            "recent_titles": sorted({p.get("title_he", "") for c in prev[:30] for p in c.get("products", []) if p.get("title_he")}),
            "recent_makers_warn": sorted({x for c in prev if c["date"] >= maker_cut for p in c.get("products", [])
                                          for x in (p.get("author"), p.get("publisher"), p.get("manufacturer")) if x}),
        }
    return out


def backup_existing(folder, target=None):
    """Move earlier recommendation files for this date into versions/vN (the same vN as the pack backup when given)."""
    folder = Path(folder)
    names = [FILES[f] for f in FORMATS] + sorted(set(OUT_DIRS.values()))
    there = [folder / n for n in names if (folder / n).exists()]
    if not there:
        return None
    if target is None:
        versions = folder / "versions"
        versions.mkdir(parents=True, exist_ok=True)
        n = 1
        while (versions / f"v{n}").exists():
            n += 1
        target = versions / f"v{n}"
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    for p in there:
        p.replace(target / p.name)
    return target


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _mask_title(text, title):
    """Replace the exact product title with a neutral word so a title's own punctuation never fails the copy rules."""
    flat = norm_title(text)
    t = norm_title(title)
    return flat.replace(t, "שם") if t and t in flat else text


def text_issues(path, text, allow_cta=False, title=None):
    issues = []
    checked = _mask_title(text, title) if title else text
    brand_only_latin = not lib.LATIN_RE.search(lib.BRAND_RE.sub("", checked))
    for i in lib.audience_text_issues(path, checked, allow_cta=allow_cta):
        if brand_only_latin and i.message.startswith("contains Latin letters"):
            continue  # "ספר של LumeBook" is Yarin's own wording; the renderer isolates the Latin run
        issues.append(i)
    for pattern, why in RECO_CLAIM_ERRORS:
        m = re.search(pattern, lib.collapse(checked))
        if m:
            issues.append(issue("ERROR", path, f"{why}: «{m.group(0)}»", "claim"))
    m = VAGUE_RE.search(lib.collapse(checked))
    if m:
        issues.append(issue("ERROR", path, f"vague or inflated line «{m.group(0)}»: say the actual activity (matching, retelling, waiting for a turn)", "claim"))
    return _flag(issues, "voice")


def image_issues(path, img, folder, allowed_sources, product=True):
    issues = []
    if not isinstance(img, dict):
        return [issue("ERROR", path, "missing image", "image")]
    f = Path(folder) / str(img.get("file", ""))
    if not img.get("file") or not f.exists():
        issues.append(issue("ERROR", f"{path}/file", f"image file not found: {img.get('file')!r} (relative to the draft folder)", "image"))
    else:
        kind = image_kind(f)
        if kind not in ("png", "jpg", "webp"):
            issues.append(issue("ERROR", f"{path}/file", "not a PNG, JPEG or WebP image", "image"))
    for key in ("image_url", "page_url"):
        h = host(img.get(key, ""))
        if not h:
            issues.append(issue("ERROR", f"{path}/{key}", "needs the original source URL", "image"))
        elif BLOCKED_IMAGE_HOSTS.search(h):
            issues.append(issue("ERROR", f"{path}/{key}", f"{h} is a search engine, pin board or image generator; take the image from the publisher, manufacturer, an official page or an established Israeli retailer", "image"))
    if img.get("source_type") not in allowed_sources:
        issues.append(issue("ERROR", f"{path}/source_type", f"source must be one of {', '.join(sorted(allowed_sources))}", "image"))
    if product and img.get("source_type") == "israeli_retailer" and not is_israeli_url(img.get("page_url", "")):
        issues.append(issue("WARN", f"{path}/page_url", "source_type is israeli_retailer but the page is not on an .il domain", "image"))
    if img.get("rights_status") not in RIGHTS_HE:
        issues.append(issue("ERROR", f"{path}/rights_status", "record the image rights status (owned, cleared or rights_unverified)", "rights"))
    elif img.get("rights_status") == "rights_unverified":
        issues.append(issue("WARN", f"{path}/rights_status", "rights_unverified: an image being online does not make it cleared; the carousel is not publish-ready until someone confirms the right to use it", "rights"))
    w, h_ = img.get("width", 0), img.get("height", 0)
    if isinstance(w, int) and isinstance(h_, int) and min(w, h_) < MIN_IMAGE_SIDE:
        issues.append(issue("WARN", f"{path}", f"image is {w}x{h_}; look for a larger version (at least {MIN_IMAGE_SIDE}px on the short side)", "image"))
    return issues


def is_strong(signal):
    """A ranking is strong only near the top (top 20 or top 10 percent); a lower position is supporting evidence."""
    if signal.get("type") not in STRONG_SIGNALS:
        return False
    if signal.get("type") == "retailer_ranking":
        rank, out_of = signal.get("rank"), signal.get("out_of")
        if not isinstance(rank, int):
            return False
        return rank <= RANKING_STRONG_TOP or (isinstance(out_of, int) and rank / out_of <= RANKING_STRONG_SHARE)
    return True


def popularity_issues(path, p, gen_date):
    issues = []
    signals = p.get("popularity_signals") or []
    ids = [s.get("id") for s in signals]
    if len(set(ids)) != len(ids):
        issues.append(issue("ERROR", f"{path}/popularity_signals", "duplicate signal ids", "popularity"))
    good = []
    for i, s in enumerate(signals):
        sp = f"{path}/popularity_signals[{i}]"
        israeli = s.get("israel_specific", is_israeli_url(s.get("url", "")))
        if not israeli:
            issues.append(issue("ERROR", sp, "not Israel-specific: international popularity never counts (set israel_specific only for an Israeli source on another domain)", "popularity"))
            continue
        try:
            if _days(gen_date, s.get("accessed", "")) > FRESH_DAYS and s.get("type") in ("bestseller_list", "retailer_ranking", "prominent_placement", "review_volume"):
                issues.append(issue("ERROR", sp, f"a ranking or placement read {_days(gen_date, s['accessed'])} days before the run; re-check it", "popularity"))
        except ValueError:
            issues.append(issue("ERROR", f"{sp}/accessed", "invalid date", "popularity"))
        good.append(s)
    strong = [s for s in good if is_strong(s)]
    groups = {s.get("group") for s in good}
    label = p.get("popularity_label")
    if label == "popular_in_israel" and not strong and len(groups) < 2:
        issues.append(issue("ERROR", f"{path}/popularity_label", "popular_in_israel needs one strong Israeli ranking or sales signal, or two independent Israel-specific signals; otherwise label it available_in_israel", "popularity"))
    if label == "available_in_israel":
        issues.append(issue("WARN", f"{path}/popularity_label", "only available_in_israel: no sufficient Israeli popularity evidence; replace it if a popular product fits", "popularity"))
    return issues


def availability_issues(path, p, gen_date):
    issues = []
    rows = p.get("availability") or []
    israeli = [a for a in rows if a.get("israeli", is_israeli_url(a.get("url", "")))]
    if not israeli:
        issues.append(issue("ERROR", f"{path}/availability", "needs Israel-specific availability evidence (an Israeli retailer or publisher page)", "availability"))
    live = [a for a in israeli if a.get("status") in ("in_stock", "listed")]
    if israeli and not live:
        issues.append(issue("ERROR", f"{path}/availability", "no Israeli retailer lists it as available now; recommend something parents can buy", "availability"))
    for i, a in enumerate(rows):
        try:
            age = _days(gen_date, a.get("accessed", ""))
            if age > FRESH_DAYS:
                issues.append(issue("ERROR", f"{path}/availability[{i}]", f"checked {age} days before the run; re-check that it is still sold", "availability"))
        except ValueError:
            issues.append(issue("ERROR", f"{path}/availability[{i}]/accessed", "invalid date", "availability"))
        if a.get("status") == "discontinued":
            issues.append(issue("ERROR", f"{path}/availability[{i}]", "discontinued products are excluded", "availability"))
    return issues


def age_issues(path, p, stage):
    issues = []
    oa = p.get("official_age") or {}
    lo, hi = oa.get("min"), oa.get("max")
    if not isinstance(lo, int):
        return [issue("ERROR", f"{path}/official_age", "record the official minimum age from the manufacturer or publisher", "age_fit")]
    if lo > stage.get("age_max", 99):
        issues.append(issue("ERROR", f"{path}/official_age", f"officially {oa.get('text')} but the carousel is for {stage.get('age_label_he')}; the age recommendation conflicts", "age_fit"))
    if isinstance(hi, int) and hi < stage.get("age_min", 0):
        issues.append(issue("ERROR", f"{path}/official_age", f"officially up to {hi}, younger than the carousel's stage", "age_fit"))
    if lo < stage.get("age_min", 0) - 3:
        issues.append(issue("WARN", f"{path}/official_age", f"officially from {lo}: check it still interests a child of {stage.get('age_label_he')}", "age_fit"))
    if not host(oa.get("url", "")):
        issues.append(issue("ERROR", f"{path}/official_age/url", "the age must come from the official product source", "age_fit"))
    return issues


def carousel_issues(car, folder, history=None, today=None):
    """Every rule. Issues carry .flag (see FLAG_HE) so the review page can group them."""
    import validate_pack  # the shared schema checker
    root = lib.read_json(SCHEMA)
    issues = _flag(validate_pack.schema_issues(car, root, root, path=car.get("format", "reco") if isinstance(car, dict) else "reco"), "structure")
    if not isinstance(car, dict) or not isinstance(car.get("slides"), list) or not isinstance(car.get("products"), list):
        return issues
    fmt = car.get("format")
    P = fmt or "reco"
    folder = Path(folder)
    gen_date = str(car.get("generated_at", ""))[:10] or car.get("date", "")
    stage = car.get("stage") or {}

    # Process: never paid, never generated, never posted
    checks = car.get("checks") or {}
    if checks.get("paid_api_calls", 1) != 0:
        issues.append(issue("ERROR", f"{P}/checks/paid_api_calls", "recommendation carousels never call a paid API", "process"))
    if checks.get("images_generated", 1) != 0:
        issues.append(issue("ERROR", f"{P}/checks/images_generated", "recommendation carousels never generate images", "process"))
    if checks.get("posted", True) is not False:
        issues.append(issue("ERROR", f"{P}/checks/posted", "nothing is posted automatically", "process"))

    # Stage
    if stage.get("skill") not in SKILLS:
        issues.append(issue("ERROR", f"{P}/stage/skill", f"skill must be one of {', '.join(SKILLS)}", "structure"))
    if isinstance(stage.get("age_min"), int) and isinstance(stage.get("age_max"), int) and stage["age_min"] > stage["age_max"]:
        issues.append(issue("ERROR", f"{P}/stage", "age_min is above age_max", "age_fit"))
    if car.get("hook_structure") not in HOOK_STRUCTURES:
        issues.append(issue("ERROR", f"{P}/hook_structure", f"must be one of {', '.join(HOOK_STRUCTURES)}", "structure"))

    # Developmental sources
    dev = {s.get("id"): s for s in car.get("dev_sources", [])}
    for s in car.get("dev_sources", []):
        sp = f"{P}/dev_sources/{s.get('id')}"
        h = host(s.get("url", ""))
        if not DEV_SOURCE_HOSTS.search(h) and s.get("kind") != "peer_reviewed":
            issues.append(issue("ERROR", sp, f"{h} is not on the credible source list (CDC, AAP, ZERO TO THREE, Child Mind Institute, KidsHealth, government or a journal); use one of them or cite peer reviewed research", "dev_source"))

    # Live-site LumeBook facts
    site_ids = set()
    for i, f in enumerate(car.get("product_facts", [])):
        site_ids.add(f.get("id"))
        try:
            age = _days(gen_date, f.get("checked_at", ""))
            if age > SITE_FACT_DAYS:
                issues.append(issue("ERROR", f"{P}/product_facts[{i}]", f"checked {age} days before the run; re-check the live site", "lumebook"))
        except ValueError:
            issues.append(issue("ERROR", f"{P}/product_facts[{i}]/checked_at", "invalid date", "lumebook"))

    # Products
    products = {p.get("id"): p for p in car.get("products", [])}
    kinds = {p.get("kind") for p in products.values()}
    if fmt in KIND_OF and kinds != {KIND_OF[fmt]}:
        issues.append(issue("ERROR", f"{P}/products", f"a {fmt} carousel recommends only {KIND_OF[fmt]}s", "structure"))
    if fmt in MIXED_FORMATS:
        kind_list = [p.get("kind") for p in car.get("products", [])]
        for kind in ("game", "book"):
            if kind_list.count(kind) < MIXED_MIN_PER_KIND:
                issues.append(issue("ERROR", f"{P}/products", f"a games and books carousel has at least {MIXED_MIN_PER_KIND} {kind}s (it has {kind_list.count(kind)})", "structure"))
    types = [p.get("type") for p in products.values()]
    if len(set(types)) != len(types):
        issues.append(issue("ERROR", f"{P}/products", "two products share a type; rotate across different kinds of play or reading", "repeat"))
    for key in ("author", "publisher", "manufacturer"):
        vals = [p.get(key) for p in products.values() if p.get(key)]
        for v in sorted({v for v in vals if vals.count(v) > 1}):
            issues.append(issue("WARN", f"{P}/products", f"{key} {v} appears twice in one carousel; prefer a different {key}", "repeat"))
    if len(products) != len(car.get("products", [])):
        issues.append(issue("ERROR", f"{P}/products", "duplicate product ids", "repeat"))
    for pid, p in products.items():
        pp = f"{P}/products/{pid}"
        if p.get("kind") == "book" and not (p.get("author") and p.get("publisher")):
            issues.append(issue("ERROR", pp, "books need the author and the Hebrew edition's publisher", "structure"))
        if p.get("kind") == "game" and not p.get("manufacturer"):
            issues.append(issue("ERROR", pp, "games need the manufacturer", "structure"))
        issues.extend(age_issues(pp, p, stage))
        issues.extend(availability_issues(pp, p, gen_date))
        issues.extend(popularity_issues(pp, p, gen_date))
        issues.extend(image_issues(f"{pp}/image", p.get("image"), folder, PRODUCT_IMAGE_SOURCES))
        for sid in p.get("dev_source_ids", []):
            if sid not in dev:
                issues.append(issue("ERROR", f"{pp}/dev_source_ids", f"unknown developmental source {sid}", "dev_source"))
        if p.get("confidence") == "low":
            issues.append(issue("WARN", pp, "low confidence: say why in limitations or replace it", "claim"))

    # Size: mixed 7 to 9 suggestions, games and books 3 to 7, the LumeBook book counted as one, and tonight's draw when there is one
    n_options = len(car.get("products", [])) + 1
    lo_n, hi_n = size_range(fmt)
    if not lo_n <= n_options <= hi_n:
        issues.append(issue("ERROR", f"{P}/products", f"{n_options} suggestions including the LumeBook book; the carousel has {lo_n} to {hi_n} ({lo_n + 3} to {hi_n + 3} slides)", "structure"))
        return issues
    L = layout(n_options)
    REC_SLIDES, LUMEBOOK_SLIDE, CLOSE_SLIDE = L["rec_slides"], L["lumebook_slide"], L["close_slide"]
    slots_path = folder / SLOTS_FILE
    if slots_path.exists():
        drawn = json.loads(slots_path.read_text(encoding="utf-8")).get(fmt)
        if isinstance(drawn, int) and drawn != n_options:
            issues.append(issue("ERROR", f"{P}/products", f"tonight's random draw for {fmt} is {drawn} suggestions (the LumeBook book counts as one); this carousel has {n_options}", "structure"))

    # Slides
    slides = car.get("slides", [])
    numbers = [s.get("number") for s in slides]
    if numbers != list(range(1, L["total"] + 1)):
        issues.append(issue("ERROR", f"{P}/slides", f"{n_options} suggestions need exactly {L['total']} slides numbered 1 to {L['total']} (hook, frame, {n_options} suggestions, close; got {numbers})", "structure"))
        return issues
    for s in slides:
        n = s["number"]
        if s.get("role") != L["roles"][n]:
            issues.append(issue("ERROR", f"{P}/slide-{n}/role", f"slide {n} must be {L['roles'][n]}", "structure"))
    addressee = car.get("addressee")
    every = []
    brand_hits = {}
    titles = {pid: p.get("title_he", "") for pid, p in products.items()}
    used_products = []
    for s in slides:
        n = s["number"]
        sp = f"{P}/slide-{n}"
        title = titles.get(s.get("product_id")) if n in REC_SLIDES else None
        fields = [("headline", s.get("headline", ""))]
        if n in REC_SLIDES:
            fields += [("age", s.get("age", "")), ("why", s.get("why", "")), ("how", s.get("how", ""))]
            if s.get("body", "").strip():
                issues.append(issue("ERROR", f"{sp}/body", "suggestion slides use headline, age, why and how (no body)", "structure"))
        else:
            fields.append(("body", s.get("body", "")))
            for extra in ("product_id", "age", "why", "how"):
                if s.get(extra):
                    issues.append(issue("ERROR", f"{sp}/{extra}", f"only the suggestion slides have {extra}", "structure"))
        for field, text in fields:
            if field == "body" and not text.strip():
                continue
            every.append(text)
            hits = lib.BRAND_RE.findall(text)
            if hits:
                brand_hits[n] = brand_hits.get(n, 0) + len(hits)
            if field == "age":
                if not text.strip():
                    issues.append(issue("ERROR", f"{sp}/age", "state the age range on the slide", "age_fit"))
                continue
            issues.extend(text_issues(f"{sp}/{field}", text, allow_cta=(n == CLOSE_SLIDE), title=title if field == "headline" else None))
            limit = lib.BODY_LINE_MAX_CHARS if field != "headline" else lib.HEADLINE_LINE_MAX_CHARS
            if field == "headline" and s["role"] == "close":
                limit = CLOSE_LINE_MAX_CHARS  # the close slide shrinks its headline to 44px, so a longer line still fits
            for li, line in enumerate(lib.lines_of(text), start=1):
                if field == "headline" and title and norm_title(line) in norm_title(title):
                    continue  # the product name itself is fitted by the renderer
                if len(line) > limit:
                    issues.append(issue("ERROR", f"{sp}/{field}", f"line {li} has {len(line)} characters (max {limit}); break it", "voice", excerpt=line))
        hl = str(s.get("highlight") or "").strip()
        if hl and s["role"] not in ("hook", "frame", "close"):
            issues.append(issue("ERROR", f"{sp}/highlight", "only the hook, the frame and the close slide have a highlight (a product title is never marked)", "structure"))
        elif hl or (bold_applies(car) and s["role"] in REQUIRE_HIGHLIGHT_ROLES):
            head = re.sub(r"^\s*\d+\s+", "", s.get("headline", "")) if s["role"] == "hook" else s.get("headline", "")
            for i in lib.highlight_issues(sp, {"number": n, "headline": head, "highlight": hl}):
                issues.append(issue(i.level, i.path, i.message, "voice"))
        words = sum(len(lib.words(t)) for _, t in fields if _ != "age")
        if n == 1:
            hw = len(lib.words(lib.lines_of(s.get("headline", ""))[0] if lib.lines_of(s.get("headline", "")) else ""))
            if hw > HOOK_MAIN_MAX_WORDS:
                issues.append(issue("ERROR", f"{sp}/headline", f"hook main line has {hw} words (max {HOOK_MAIN_MAX_WORDS})", "voice"))
            if words > HOOK_MAX_WORDS:
                issues.append(issue("ERROR", sp, f"hook slide has {words} words (max {HOOK_MAX_WORDS})", "voice"))
            text = lib.collapse(s.get("headline", "") + " " + s.get("body", ""))
            for pattern, why in lib.HOOK_BANNED:
                if re.search(pattern, text):
                    issues.append(issue("ERROR", sp, f"banned hook opener ({why})", "voice"))
            m = HOOK_TEMPLATE_RE.get(fmt, re.compile("$^")).match(text)
            if s.get("body", "").strip():
                issues.append(issue("ERROR", f"{sp}/body", "the hook is one sentence in the headline (break it into lines there); no body", "structure"))
            if fmt not in MIXED_FORMATS and HOOK_AGE_RE.search(text):
                issues.append(issue("ERROR", sp, f"no ages in the hook (Yarin, 9 Oct 2026): «{HOOK_AGE_RE.search(text).group(0)}»", "structure"))
            if not m:
                issues.append(issue("ERROR", sp, f"the hook is always «{HOOK_TEMPLATE_HE.get(fmt)}» (Yarin, 9 Oct 2026{'; the ages since 14 Oct 2026' if fmt in MIXED_FORMATS else ''})", "structure"))
            else:
                if fmt in MIXED_FORMATS:
                    lo, hi = (int(m.group(2)), int(m.group(3))) if m.group(2) else (int(m.group(4)), int(m.group(4)))
                    want = (stage.get("age_min"), stage.get("age_max"))
                    if (lo, hi) != want:
                        say = f"לגיל {want[0]}" if want[0] == want[1] else f"לגילאי {want[0]}-{want[1]}"
                        issues.append(issue("ERROR", sp, f"the hook says the ages {lo}-{hi}; the carousel's stage is {want[0]} to {want[1]}: write «{say}» (Yarin, 14 Oct 2026: \"add what ages are they suitable for\")", "structure"))
                if int(m.group(1)) != n_options:
                    issues.append(issue("ERROR", sp, f"the hook says {m.group(1)}; this carousel has {n_options} suggestions (the LumeBook book counts as one)", "structure"))
            skill_re = SKILLS.get(stage.get("skill"), {}).get("keywords_he")
            if lib.value_hook_applies(car) and not re.search(r"שיעזר|שעוזר|עוזרים|מתרגלים|לתרגל|שמלמד|מלמדים|שמאפשר", text):
                issues.append(issue("WARN", sp, "the hook says what the value is: end with שיעזרו להם ... or שמתרגלים ... and the concrete thing (Yarin, 11 Oct 2026)", "voice"))
            if bold_applies(car):
                alts = car.get("hook_alternatives") or []
                if len(alts) < 2:
                    issues.append(issue("WARN", f"{P}/hook_alternatives", "write 3 wordings of the hook, calm to loud, keep the loudest one the developmental source supports, and list them in hook_alternatives", "voice"))
                for ai, alt in enumerate(alts):
                    issues.extend(text_issues(f"{P}/hook_alternatives[{ai}]", alt))
            if not AGE_IN_TEXT_RE.search(text) and not (skill_re and re.search(skill_re, text)):
                issues.append(issue("ERROR", sp, "the hook names the age range, the stage or the need", "structure"))
        elif n == 2 and words > FRAME_MAX_WORDS:
            issues.append(issue("ERROR", sp, f"slide has {words} words (max {FRAME_MAX_WORDS})", "voice"))
        if n in REC_SLIDES:
            for field, limit in (("why", WHY_MAX_WORDS), ("how", HOW_MAX_WORDS)):
                text = s.get(field, "")
                if not text.strip():
                    issues.append(issue("ERROR", f"{sp}/{field}", "say why it is valuable (why) and how a parent and child can use it (how)", "structure"))
                    continue
                if len(lib.words(text)) > limit:
                    issues.append(issue("ERROR", f"{sp}/{field}", f"{len(lib.words(text))} words (max {limit})", "voice"))
                if len(lib.lines_of(text)) > REC_LINES_MAX:
                    issues.append(issue("ERROR", f"{sp}/{field}", f"at most {REC_LINES_MAX} lines", "voice"))
            if s.get("why", "").strip() and not ACTIVITY_RE.search(s["why"]):
                issues.append(issue("ERROR", f"{sp}/why", "name the actual activity the child does (waits for a turn, matches, retells, predicts, builds, sorts, plans)", "claim"))
        if n in REC_SLIDES:
            pid = s.get("product_id")
            p = products.get(pid)
            if not p:
                issues.append(issue("ERROR", f"{sp}/product_id", f"{pid!r} is not one of this carousel's products", "structure"))
            else:
                used_products.append(pid)
                if norm_title(p.get("title_he", "")) not in norm_title(s.get("headline", "")):
                    issues.append(issue("ERROR", f"{sp}/headline", f"must contain the exact product name «{p.get('title_he')}»", "structure"))
                lo = (p.get("official_age") or {}).get("min")
                if isinstance(lo, int) and str(lo) not in s.get("age", ""):
                    issues.append(issue("ERROR", f"{sp}/age", f"the slide's age must follow the official age ({(p.get('official_age') or {}).get('text')})", "age_fit"))
                if POPULARITY_WORDS_RE.search(lib.collapse(" ".join(t for _, t in fields))):
                    if p.get("popularity_label") != "popular_in_israel":
                        issues.append(issue("ERROR", sp, "the slide says it is popular but the evidence only supports available_in_israel", "popularity"))
                    elif not any(c.get("kind") == "popularity" and c.get("slide") == n for c in car.get("claims", [])):
                        issues.append(issue("ERROR", sp, "a popularity wording needs a popularity claim citing the product's Israeli signals", "popularity"))
        elif n == LUMEBOOK_SLIDE:
            text = lib.collapse(" ".join(t for _, t in fields))
            if words > LUMEBOOK_MAX_WORDS:
                issues.append(issue("ERROR", sp, f"slide has {words} words (max {LUMEBOOK_MAX_WORDS})", "voice"))
            if not LUMEBOOK_BODY_RE.search(s.get("body", "")) or not LUMEBOOK_PHOTO_RE.search(s.get("body", "")):
                issues.append(issue("ERROR", f"{sp}/body", "the LumeBook line reads סיפור מותאם אישית עם תמונה של הילד שלכם שבו... (Yarin's format)", "lumebook"))
            m = SALES_RE.search(text)
            if m:
                issues.append(issue("ERROR", sp, f"«{m.group(0)}» is sales talk; the LumeBook slide stays editorial and relaxed (no urgency, discounts, prices or free offers)", "lumebook"))
            m = GUARANTEE_RE.search(text)
            if m:
                issues.append(issue("ERROR", sp, f"«{m.group(0)}» promises a result; personalisation never guarantees development", "lumebook"))
            if not any(c.get("kind") == "product_fact" and c.get("slide") == n for c in car.get("claims", [])):
                issues.append(issue("ERROR", sp, "map what the LumeBook slide says to a live-site product fact (site-...)", "lumebook"))
        elif n == CLOSE_SLIDE:
            if s.get("body", "").strip():
                issues.append(issue("ERROR", f"{sp}/body", "the last slide is only the save and comment lines, in the headline (Yarin, 9 Oct 2026); no summary or body", "structure"))
            if words > CLOSE_MAX_WORDS:
                issues.append(issue("ERROR", sp, f"slide has {words} words (max {CLOSE_MAX_WORDS})", "voice"))
            text = lib.collapse(s.get("headline", "") + " " + s.get("body", ""))
            m = CLOSE_SALE_RE.search(text)
            if m:
                issues.append(issue("ERROR", sp, f"«{m.group(0)}» turns the close into a sales slide; keep it a useful summary", "lumebook"))
            if not CLOSE_PROMPT_RE.search(text):
                issues.append(issue("ERROR", sp, "end with a light save, share or comment prompt", "structure"))
    if fmt in MIXED_FORMATS:
        order = [products[pid].get("kind") for pid in used_products if pid in products]
        if mixed_order_applies(car):
            runs = [len(list(g)) for _, g in itertools.groupby(order)]
            if runs and max(runs) > MIXED_ORDER_MAX_RUN:
                issues.append(issue("ERROR", f"{P}/slides", f"mix the games and the books (Yarin, 16 Oct 2026: \"mix their order instead of games and then books\"): never {MIXED_ORDER_MAX_RUN + 1} of the same kind in a row; alternate where the counts allow (the LumeBook book stays second to last)", "structure"))
        elif "book" in order and "game" in order[order.index("book"):]:
            issues.append(issue("ERROR", f"{P}/slides", "group the suggestions: every game first, then the books (the LumeBook book stays second to last)", "structure"))
    if sorted(used_products) != sorted(products):
        issues.append(issue("ERROR", f"{P}/slides", f"the product slides ({', '.join(map(str, REC_SLIDES))}) must show each of the {len(products)} products exactly once", "structure"))
    if len(set(used_products)) != len(used_products):
        issues.append(issue("ERROR", f"{P}/slides", "a product appears on two slides", "repeat"))

    # LumeBook: once, on its slide, with an approved asset
    if brand_hits.get(LUMEBOOK_SLIDE, 0) != 1:
        issues.append(issue("ERROR", f"{P}/slide-{LUMEBOOK_SLIDE}", f"slide {LUMEBOOK_SLIDE} names LumeBook (לומבוק) exactly once", "lumebook"))
    for n in brand_hits:
        if n != LUMEBOOK_SLIDE:
            issues.append(issue("ERROR", f"{P}/slide-{n}", f"LumeBook appears only on slide {LUMEBOOK_SLIDE}", "lumebook"))
    if lib.BRAND_RE.search(car.get("caption", "")):
        issues.append(issue("ERROR", f"{P}/caption", f"LumeBook is mentioned once, on slide {LUMEBOOK_SLIDE}, not in the caption", "lumebook"))
    issues.extend(image_issues(f"{P}/lumebook/image", (car.get("lumebook") or {}).get("image"), folder, LUMEBOOK_IMAGE_SOURCES, product=False))
    issues.extend(lumebook_cover_issues(P, car))

    # Who it talks to: mom or both parents, never dad
    caption = car.get("caption", "")
    all_text = "\n".join(every + [caption])
    m = lib.DAD_RE.search(lib.PARENT_PAIR_RE.sub(" ", all_text) if addressee == "parents" else all_text)
    if m:
        issues.append(issue("ERROR", P, f"never talk to dad: «{m.group(0)}». Talk to mom or both parents", "voice"))
    m = MALE_COMMAND_RE.search(all_text)
    if m:
        issues.append(issue("ERROR", P, f"«{m.group(0)}» talks to a father (masculine singular); write to mom (תני, שאלי) or both parents (תנו, שאלו)", "voice"))
    if addressee != "parents":
        issues.append(issue("ERROR", f"{P}/addressee", "these carousels always talk to both parents, in the plural (Yarin, 9 Oct 2026)", "voice"))
    unquoted = QUOTED_RE.sub(" ", all_text)
    for title in titles.values():
        unquoted = unquoted.replace(title, " ")
    for rx, why, level in ((SINGULAR_CHILD_RE, "talks about one child; write about children in the plural (הילדים, ילדים)", "ERROR"),
                           (SINGULAR_YOU_RE, "talks to one parent; write to both parents in the plural (לכם, שלכם)", "ERROR"),
                           (FEM_COMMAND_RE, "a feminine singular command; write to both parents in the plural (שאלו, עצרו, תנו)", "ERROR"),
                           (SINGULAR_PRONOUN_RE, "a singular pronoun; if it means the child, write in the plural (הם, להם, שלהם)", "WARN")):
        m = rx.search(unquoted)
        if m:
            issues.append(issue(level, P, f"«{m.group(0)}» {why}", "voice"))
    m = re.search(r"יש שמגיעים לזה קודם", all_text)
    if m:  # Yarin, 9 Oct 2026: never use this line again
        issues.append(issue("ERROR", P, "drop «יש שמגיעים לזה קודם ויש שאחר כך» (Yarin, 9 Oct 2026); say ages are approximate another way (בסביבות גיל X)", "voice"))
    opening = "\n".join(s.get("headline", "") + "\n" + s.get("body", "") for s in slides[:2])
    if not AGE_HEDGE_RE.search(opening + "\n" + caption):
        issues.append(issue("ERROR", f"{P}/slide-2", "say that ages are approximate (בערך, יש ילדים ש..., בקצב של כל ילד): never treat an age boundary as exact", "claim"))

    # Caption
    issues.extend(text_issues(f"{P}/caption", caption, allow_cta=True))
    cap = lib.lines_of(caption)
    if not CAPTION_MIN_LINES <= len(cap) <= CAPTION_MAX_LINES:
        issues.append(issue("ERROR", f"{P}/caption", f"caption has {len(cap)} lines ({CAPTION_MIN_LINES} to {CAPTION_MAX_LINES})", "voice"))
    m = SALES_RE.search(caption)
    if m:
        issues.append(issue("ERROR", f"{P}/caption", f"«{m.group(0)}» is sales talk", "lumebook"))

    # Claims
    claims = car.get("claims", [])
    sig_ids = {s.get("id"): pid for pid, p in products.items() for s in p.get("popularity_signals", [])}
    for i, c in enumerate(claims):
        cp = f"{P}/claims[{i}]"
        ids, kind = c.get("source_ids", []), c.get("kind")
        if kind == "developmental":
            if not ids:
                issues.append(issue("ERROR", cp, "every developmental claim needs a credible source", "dev_source"))
            for sid in ids:
                if sid not in dev:
                    issues.append(issue("ERROR", cp, f"unknown developmental source {sid}", "dev_source"))
        elif kind == "popularity":
            if not ids:
                issues.append(issue("ERROR", cp, "a popularity claim cites the product's Israeli signals (pop-...)", "popularity"))
            for sid in ids:
                if sid not in sig_ids:
                    issues.append(issue("ERROR", cp, f"unknown popularity signal {sid}", "popularity"))
                elif products[sig_ids[sid]].get("popularity_label") != "popular_in_israel":
                    issues.append(issue("ERROR", cp, "claims popularity for a product labelled available_in_israel", "popularity"))
        elif kind == "product_fact":
            if not ids:
                issues.append(issue("ERROR", cp, "a LumeBook fact cites a live-site fact (site-...)", "lumebook"))
            for sid in ids:
                if sid not in site_ids:
                    issues.append(issue("ERROR", cp, f"unknown product fact {sid}", "lumebook"))
        elif kind in ("availability", "age") and not ids:
            issues.append(issue("ERROR", cp, f"an {kind} claim cites the product id it is about", "claim"))
    claimed = {(c.get("slide"), c.get("kind")) for c in claims}
    if (1, "developmental") not in claimed:
        issues.append(issue("ERROR", f"{P}/claims", "the hook says what the products help with: map slide 1 to a developmental source", "dev_source"))
    if (2, "developmental") not in claimed:
        issues.append(issue("ERROR", f"{P}/claims", "slide 2 explains what children practise at this stage: map it to a developmental source", "dev_source"))
    for n in REC_SLIDES:
        if (n, "developmental") not in claimed:
            issues.append(issue("ERROR", f"{P}/claims", f"slide {n} says why the product is valuable: map it to a developmental source", "dev_source"))

    # Rotation against history
    if history is not None and car.get("date"):
        issues.extend(rotation_issues(car, history))
    return issues


def rotation_issues(car, history):
    issues = []
    fmt, date_str = car["format"], car["date"]
    day = lib.parse_date(date_str)
    P = fmt
    cutoff = (day - dt.timedelta(days=PRODUCT_COOLDOWN_DAYS)).isoformat()
    recent = [c for c in previous(history, date_str, sibling_of=fmt) if c["date"] >= cutoff]
    for p in car.get("products", []):
        for c in recent:
            for q in c.get("products", []):
                if q.get("id") == p.get("id") or norm_title(q.get("title_he", "")) == norm_title(p.get("title_he", "")):
                    level = "WARN" if p.get("seasonal_reason") else "ERROR"
                    issues.append(issue(level, f"{P}/products/{p.get('id')}", f"recommended on {c['date']}; no product twice within {PRODUCT_COOLDOWN_DAYS} days{' (seasonal reason given)' if level == 'WARN' else ' unless a seasonal reason is documented'}", "repeat"))
    prev = rotation_pool(history, date_str, fmt)
    stage = car.get("stage", {})
    if stage.get("skill") in {c["skill"] for c in last_runs(prev, SKILL_COOLDOWN_RUNS)}:
        issues.append(issue("ERROR", f"{P}/stage/skill", f"{stage.get('skill')} was one of the last {SKILL_COOLDOWN_RUNS} {'recommendation' if fmt in MIXED_FORMATS else fmt} carousels; rotate the skill", "repeat"))
    stage_cut = (day - dt.timedelta(days=STAGE_COOLDOWN_DAYS)).isoformat()
    if stage.get("id") in {c["stage_id"] for c in prev if c["date"] >= stage_cut}:
        issues.append(issue("ERROR", f"{P}/stage/id", f"stage {stage.get('id')} ran in the last {STAGE_COOLDOWN_DAYS} days", "repeat"))
    if prev and [prev[0]["age_min"], prev[0]["age_max"]] == [stage.get("age_min"), stage.get("age_max")]:
        issues.append(issue("WARN", f"{P}/stage", "same age range as the previous carousel of this format; rotate ages when another fits", "repeat"))
    hook = lib.collapse(car["slides"][0].get("headline", "")) if car.get("slides") else ""
    if hook and any(hook == c.get("hook") for c in prev[:30]):
        issues.append(issue("ERROR", f"{P}/slide-1", "this hook was used before", "repeat"))
    maker_cut = (day - dt.timedelta(days=MAKER_WARN_DAYS)).isoformat()
    makers = {x for c in prev if c["date"] >= maker_cut for q in c.get("products", []) for x in (q.get("author"), q.get("publisher"), q.get("manufacturer")) if x}
    for p in car.get("products", []):
        for key in ("author", "publisher", "manufacturer"):
            if p.get(key) and p[key] in makers:
                issues.append(issue("WARN", f"{P}/products/{p.get('id')}/{key}", f"{p[key]} was in a {fmt} carousel in the last {MAKER_WARN_DAYS} days", "repeat"))
    return issues


def status(issues, car):
    """valid = no errors. publish_ready = valid, every image owned or cleared, every product popular_in_israel."""
    errors = [i for i in issues if i.level == "ERROR"]
    rights = all((p.get("image") or {}).get("rights_status") in PUBLISHABLE_RIGHTS for p in car.get("products", [])) and \
        ((car.get("lumebook") or {}).get("image") or {}).get("rights_status") in PUBLISHABLE_RIGHTS
    popular = all(p.get("popularity_label") == "popular_in_israel" for p in car.get("products", []))
    return {"valid": not errors, "publish_ready": not errors and rights and popular, "rights_clear": rights, "all_popular": popular,
            "errors": len(errors), "warnings": len(issues) - len(errors),
            "flags": sorted({getattr(i, "flag", "structure") for i in issues})}


def validate_file(path, history=None):
    path = Path(path)
    car = lib.read_json(path)
    issues = carousel_issues(car, path.parent, history=history)
    return car, issues, status(issues, car)


def recent_edits(n=40, path=None):
    """Yarin's edits to the recommendation carousels (mixed, games, books) on the review page, newest last. The nightly run reads them
    before writing and writes the way the "after" lines sound (what was cut, added, shortened, how lines split)."""
    edits = lib.load_voice_edits(path) if path else lib.load_voice_edits()
    keep = [e for e in edits if e.get("direction") in FORMATS and e.get("before") != e.get("after")]
    return [{k: e.get(k) for k in ("at", "direction", "slide", "role", "field", "kind", "before", "after")} for e in keep[-n:]]


def start_context(date_str, folder, history=None, fmt=MIXED, formats=NIGHTLY_FORMATS, assigned=None):
    """Printed by nightly.py start under "recommendations": one combined games and books carousel (14 Oct 2026).
    A weekly batch pack has two (formats BATCH_FORMATS): the second is printed under "recommendations_2" with fmt MIXED2,
    and `assigned` carries the plan's skill and event flag for it."""
    history = history if history is not None else load_history()
    slots = draw_slots(folder, formats)
    n = slots[fmt]
    extra = {}
    if assigned:
        extra["assigned"] = {**assigned, "rule": "use this skill (the weekly plan spreads the 14 carousels so none repeats within four packs); "
                             "the two carousels of one pack use different age ranges and never share a product"
                             + ("; this carousel belongs to the Israeli event pack: pick games and books that fit the event and record the pack's `event`" if assigned.get("event") else "")}
    return {
        **extra,
        "write_to": str(Path(folder) / FILES[fmt]),
        "format": fmt,
        "images_go_to": str(Path(folder) / ASSETS_DIR),
        "rules": "carousel/carousel-pipeline/recommendations.md",
        "example": "carousel/carousel-pipeline/tests/fixtures/reco/reco-carousel.json",
        "skills": {k: v["he"] for k, v in SKILLS.items()},
        "hook_structures": HOOK_STRUCTURES,
        "hook_template": HOOK_TEMPLATE_HE[fmt],
        "recent_edits_learn_from_these": recent_edits(),
        "learn_rule": "Yarin edited these lines on the review pages (reco.html, and games.html and books.html on older nights). Read every pair before writing and write tonight's copy the way the after lines sound, per role and field. Never bring back what Yarin removed and do not copy the lines.",
        "rotation": rotation_context(history, date_str, (fmt,)),
        "suggestions": {
            "rule": (f"one carousel of games and books for one developmental stage and theme, with a random number of suggestions from {MIXED_OPTIONS_MIN} to {MIXED_OPTIONS_MAX}; "
                     f"the LumeBook book counts as one of them, so products = suggestions - 1, with at least {MIXED_MIN_PER_KIND} games and at least {MIXED_MIN_PER_KIND} books "
                     "(each product records kind game or book; games need manufacturer, books need author and the Hebrew edition's publisher). "
                     "Slides = suggestions + 3: hook, frame, the games and the books MIXED (never 3 of the same kind in a row, alternate where the counts allow; Yarin 16 Oct 2026), with the LumeBook book as the second to last suggestion, close. "
                     f"The hook is «{HOOK_TEMPLATE_HE[MIXED]}»: X is the number of suggestions, the LumeBook book included, and A-B the stage's ages (age_min-age_max; «לגיל A» when they are equal), as on Yarin's reference «4 משחקי קופסא לגילאי 5-6 שעוזרים לילדים לשים לב»."),
            "tonight": n,
            "products_tonight": n - 1,
            "slides_tonight": {str(k): v for k, v in layout(n)["roles"].items()},
        },
        "finish_with": f"python3 {lib.PIPELINE / 'scripts' / 'nightly.py'} finish-reco {folder}",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carousel")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-history", action="store_true")
    args = ap.parse_args()
    car, issues, st = validate_file(args.carousel, history=None if args.no_history else load_history())
    errors = [i for i in issues if i.level == "ERROR"]
    if args.json:
        print(json.dumps({**st, "issues": [{**i.as_dict(), "flag": getattr(i, "flag", "")} for i in issues]}, ensure_ascii=False, indent=2))
    else:
        for i in issues:
            print(f"- [{getattr(i, 'flag', '')}] {i}")
        print(("VALID" if st["valid"] else "INVALID") + f" {args.carousel} · publish-ready: {'yes' if st['publish_ready'] else 'no'}")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
