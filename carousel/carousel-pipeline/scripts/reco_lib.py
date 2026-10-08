#!/usr/bin/env python3
"""Rules, rotation and validation for the two daily recommendation carousels.

Every nightly run adds two complete 7-slide carousels next to the kid and expert pack:

    drafts/DATE/games-carousel.json    3 real games for one developmental stage
    drafts/DATE/books-carousel.json    3 real books for one developmental stage

Each product must be popular or clearly established in Israel (Israel-specific evidence, never inferred from
international popularity), each recommendation slide centres a real product image from an authoritative source,
and LumeBook is named once, on slide 6. No image generation, no paid API, nothing is posted.

    python3 carousel/carousel-pipeline/scripts/reco_lib.py PATH/games-carousel.json        # validate one file
    python3 carousel/carousel-pipeline/scripts/reco_lib.py PATH/books-carousel.json --json

The Hebrew hard rules (punctuation, jargon, guarantees, never dad, never AI) come from carousel_lib so there is
one definition of the voice rules. Format rules: carousel/carousel-pipeline/recommendations.md.
Standard library only.
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402

SCHEMA = lib.PIPELINE / "reco.schema.json"
HISTORY = lib.PIPELINE / "reco-history.json"
FORMATS = ("games", "books")
FILES = {"games": "games-carousel.json", "books": "books-carousel.json"}
ASSETS_DIR = "reco-assets"  # product and LumeBook images, inside drafts/DATE/
FORMAT_HE = {"games": "משחקים", "books": "ספרים"}
KIND_OF = {"games": "game", "books": "book"}

SLIDE_COUNT = 7
SLIDE_ROLES = {1: "hook", 2: "frame", 3: "recommendation", 4: "recommendation", 5: "recommendation", 6: "lumebook", 7: "close"}
REC_SLIDES = (3, 4, 5)
LUMEBOOK_SLIDE = 6
CLOSE_SLIDE = 7
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

# Slide 1 structures, rotated so the two daily carousels do not open the same way every day.
HOOK_STRUCTURES = {
    "age_need_list": "גיל + מה מתרגלים + כמה המלצות (3 משחקים לגיל 4 שמתרגלים תור)",
    "moment_question": "רגע מוכר + שאלה (הוא בוכה כשהוא מפסיד?)",
    "skill_reveal": "מה הילד באמת מתרגל כשהוא עושה X",
    "parent_quote": "משפט שהורים אומרים במירכאות",
    "shelf_check": "מה כדאי שיהיה על המדף בגיל הזה",
    "gift_list": "רשימה למתנה לגיל מסוים",
    "observation": "משהו קטן ששמים לב אליו בבית",
    "myth_vs_fact": "מה שחושבים לעומת מה שקורה",
}

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
    """{format: path} for the recommendation carousels that exist in a draft folder."""
    return {f: carousel_path(folder, f) for f in FORMATS if carousel_path(folder, f).exists()}


def load_history(path=HISTORY):
    path = Path(path)
    if not path.exists():
        return {"carousels": []}
    return json.loads(path.read_text(encoding="utf-8"))


def previous(history, date_str, fmt=None):
    """Earlier carousels, newest first. A rerun for the same date and format ignores its own earlier entry."""
    out = [c for c in history.get("carousels", []) if c.get("date") and c["date"] < date_str and (fmt is None or c.get("format") == fmt)]
    return sorted(out, key=lambda c: c["date"], reverse=True)


def history_entry(car):
    return {
        "date": car["date"], "format": car["format"], "generated_at": car.get("generated_at"),
        "stage_id": car["stage"]["id"], "skill": car["stage"]["skill"],
        "age_min": car["stage"]["age_min"], "age_max": car["stage"]["age_max"],
        "hook_structure": car["hook_structure"], "hook": lib.collapse(car["slides"][0]["headline"]),
        "products": [{k: p.get(k, "") for k in ("id", "title_he", "author", "publisher", "manufacturer", "type")} for p in car["products"]],
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


def rotation_context(history, date_str):
    """What tonight's games and books carousels should rotate away from."""
    day = lib.parse_date(date_str)
    out = {"product_cooldown_days": PRODUCT_COOLDOWN_DAYS}
    cutoff = (day - dt.timedelta(days=PRODUCT_COOLDOWN_DAYS)).isoformat()
    recent_all = [c for c in previous(history, date_str) if c["date"] >= cutoff]
    out["blocked_products"] = sorted({f"{p['id']} · {p['title_he']}" for c in recent_all for p in c.get("products", [])})
    for fmt in FORMATS:
        prev = previous(history, date_str, fmt)
        maker_cut = (day - dt.timedelta(days=MAKER_WARN_DAYS)).isoformat()
        stage_cut = (day - dt.timedelta(days=STAGE_COOLDOWN_DAYS)).isoformat()
        out[fmt] = {
            "blocked_skills": sorted({c["skill"] for c in prev[:SKILL_COOLDOWN_RUNS]}),
            "blocked_stage_ids": sorted({c["stage_id"] for c in prev if c["date"] >= stage_cut}),
            "last_age_range": [prev[0]["age_min"], prev[0]["age_max"]] if prev else None,
            "last_hook_structure": prev[0]["hook_structure"] if prev else None,
            "recent_hooks": [c.get("hook") for c in prev[:14]],
            "recent_makers_warn": sorted({x for c in prev if c["date"] >= maker_cut for p in c.get("products", [])
                                          for x in (p.get("author"), p.get("publisher"), p.get("manufacturer")) if x}),
        }
    return out


def backup_existing(folder, target=None):
    """Move earlier recommendation files for this date into versions/vN (the same vN as the pack backup when given)."""
    folder = Path(folder)
    names = [FILES[f] for f in FORMATS] + list(FORMATS)
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
    for i in lib.audience_text_issues(path, checked, allow_cta=allow_cta):
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
        if fmt == "books" and not (p.get("author") and p.get("publisher")):
            issues.append(issue("ERROR", pp, "books need the author and the Hebrew edition's publisher", "structure"))
        if fmt == "games" and not p.get("manufacturer"):
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

    # Slides
    slides = car.get("slides", [])
    numbers = [s.get("number") for s in slides]
    if numbers != list(range(1, SLIDE_COUNT + 1)):
        issues.append(issue("ERROR", f"{P}/slides", f"exactly {SLIDE_COUNT} slides numbered 1 to {SLIDE_COUNT} (got {numbers})", "structure"))
        return issues
    for s in slides:
        n = s["number"]
        if s.get("role") != SLIDE_ROLES[n]:
            issues.append(issue("ERROR", f"{P}/slide-{n}/role", f"slide {n} must be {SLIDE_ROLES[n]}", "structure"))
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
                issues.append(issue("ERROR", f"{sp}/body", "recommendation slides use headline, age, why and how (no body)", "structure"))
        else:
            fields.append(("body", s.get("body", "")))
            for extra in ("product_id", "age", "why", "how"):
                if s.get(extra):
                    issues.append(issue("ERROR", f"{sp}/{extra}", f"only slides 3 to 5 have {extra}", "structure"))
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
            for li, line in enumerate(lib.lines_of(text), start=1):
                if field == "headline" and title and norm_title(line) in norm_title(title):
                    continue  # the product name itself is fitted by the renderer
                if len(line) > limit:
                    issues.append(issue("ERROR", f"{sp}/{field}", f"line {li} has {len(line)} characters (max {limit}); break it", "voice", excerpt=line))
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
            skill_re = SKILLS.get(stage.get("skill"), {}).get("keywords_he")
            if not AGE_IN_TEXT_RE.search(text) and not (skill_re and re.search(skill_re, text)):
                issues.append(issue("ERROR", sp, "the hook names the age range, the stage or the need", "structure"))
        elif n == 2 and words > FRAME_MAX_WORDS:
            issues.append(issue("ERROR", sp, f"slide has {words} words (max {FRAME_MAX_WORDS})", "voice"))
        elif n in REC_SLIDES:
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
            if words > LUMEBOOK_MAX_WORDS:
                issues.append(issue("ERROR", sp, f"slide has {words} words (max {LUMEBOOK_MAX_WORDS})", "voice"))
            text = lib.collapse(s.get("headline", "") + " " + s.get("body", ""))
            m = SALES_RE.search(text)
            if m:
                issues.append(issue("ERROR", sp, f"«{m.group(0)}» is sales talk; slide 6 stays editorial and relaxed (no urgency, discounts, prices or free offers)", "lumebook"))
            m = GUARANTEE_RE.search(text)
            if m:
                issues.append(issue("ERROR", sp, f"«{m.group(0)}» promises a result; personalisation never guarantees development", "lumebook"))
            skill_re = SKILLS.get(stage.get("skill"), {}).get("keywords_he")
            if skill_re and not re.search(skill_re, text):
                issues.append(issue("WARN", sp, "slide 6 should connect LumeBook to the same developmental need as the carousel", "lumebook"))
            if not any(c.get("kind") == "product_fact" and c.get("slide") == n for c in car.get("claims", [])):
                issues.append(issue("ERROR", sp, "map what slide 6 says about LumeBook to a live-site product fact (site-...)", "lumebook"))
        elif n == CLOSE_SLIDE:
            if words > CLOSE_MAX_WORDS:
                issues.append(issue("ERROR", sp, f"slide has {words} words (max {CLOSE_MAX_WORDS})", "voice"))
            text = lib.collapse(s.get("headline", "") + " " + s.get("body", ""))
            m = CLOSE_SALE_RE.search(text)
            if m:
                issues.append(issue("ERROR", sp, f"«{m.group(0)}» turns the close into a sales slide; keep it a useful summary", "lumebook"))
            if not CLOSE_PROMPT_RE.search(text):
                issues.append(issue("ERROR", sp, "end with a light save, share or comment prompt", "structure"))
    if sorted(used_products) != sorted(products):
        issues.append(issue("ERROR", f"{P}/slides", "slides 3 to 5 must show each of the 3 products exactly once", "structure"))
    if len(set(used_products)) != len(used_products):
        issues.append(issue("ERROR", f"{P}/slides", "a product appears on two slides", "repeat"))

    # LumeBook: once, on slide 6, with an approved asset
    if brand_hits.get(LUMEBOOK_SLIDE, 0) != 1:
        issues.append(issue("ERROR", f"{P}/slide-{LUMEBOOK_SLIDE}", "slide 6 names LumeBook (לומבוק) exactly once", "lumebook"))
    for n in brand_hits:
        if n != LUMEBOOK_SLIDE:
            issues.append(issue("ERROR", f"{P}/slide-{n}", "LumeBook appears only on slide 6", "lumebook"))
    if lib.BRAND_RE.search(car.get("caption", "")):
        issues.append(issue("ERROR", f"{P}/caption", "LumeBook is mentioned once, on slide 6, not in the caption", "lumebook"))
    issues.extend(image_issues(f"{P}/lumebook/image", (car.get("lumebook") or {}).get("image"), folder, LUMEBOOK_IMAGE_SOURCES, product=False))

    # Who it talks to: mom or both parents, never dad
    caption = car.get("caption", "")
    all_text = "\n".join(every + [caption])
    m = lib.DAD_RE.search(lib.PARENT_PAIR_RE.sub(" ", all_text) if addressee == "parents" else all_text)
    if m:
        issues.append(issue("ERROR", P, f"never talk to dad: «{m.group(0)}». Talk to mom or both parents", "voice"))
    m = MALE_COMMAND_RE.search(all_text)
    if m:
        issues.append(issue("ERROR", P, f"«{m.group(0)}» talks to a father (masculine singular); write to mom (תני, שאלי) or both parents (תנו, שאלו)", "voice"))
    if addressee == "mom" and lib.PARENTS_ADDRESS_RE.search(all_text):
        issues.append(issue("WARN", f"{P}/addressee", f"addressee is mom but a line talks to both parents: «{lib.PARENTS_ADDRESS_RE.search(all_text).group(0)}»", "voice"))
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
    recent = [c for c in previous(history, date_str) if c["date"] >= cutoff]
    for p in car.get("products", []):
        for c in recent:
            for q in c.get("products", []):
                if q.get("id") == p.get("id") or norm_title(q.get("title_he", "")) == norm_title(p.get("title_he", "")):
                    level = "WARN" if p.get("seasonal_reason") else "ERROR"
                    issues.append(issue(level, f"{P}/products/{p.get('id')}", f"recommended on {c['date']}; no product twice within {PRODUCT_COOLDOWN_DAYS} days{' (seasonal reason given)' if level == 'WARN' else ' unless a seasonal reason is documented'}", "repeat"))
    prev = previous(history, date_str, fmt)
    stage = car.get("stage", {})
    if stage.get("skill") in {c["skill"] for c in prev[:SKILL_COOLDOWN_RUNS]}:
        issues.append(issue("ERROR", f"{P}/stage/skill", f"{stage.get('skill')} was one of the last {SKILL_COOLDOWN_RUNS} {fmt} carousels; rotate the skill", "repeat"))
    stage_cut = (day - dt.timedelta(days=STAGE_COOLDOWN_DAYS)).isoformat()
    if stage.get("id") in {c["stage_id"] for c in prev if c["date"] >= stage_cut}:
        issues.append(issue("ERROR", f"{P}/stage/id", f"stage {stage.get('id')} ran in the last {STAGE_COOLDOWN_DAYS} days", "repeat"))
    if prev and [prev[0]["age_min"], prev[0]["age_max"]] == [stage.get("age_min"), stage.get("age_max")]:
        issues.append(issue("WARN", f"{P}/stage", "same age range as the previous carousel of this format; rotate ages when another fits", "repeat"))
    if prev and prev[0].get("hook_structure") == car.get("hook_structure"):
        issues.append(issue("ERROR", f"{P}/hook_structure", f"{car.get('hook_structure')} opened the previous {fmt} carousel; use another structure", "repeat"))
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


def start_context(date_str, folder, history=None):
    """Printed by nightly.py start under "recommendations"."""
    history = history if history is not None else load_history()
    return {
        "write_games_to": str(Path(folder) / FILES["games"]),
        "write_books_to": str(Path(folder) / FILES["books"]),
        "images_go_to": str(Path(folder) / ASSETS_DIR),
        "rules": "carousel/carousel-pipeline/recommendations.md",
        "example": "carousel/carousel-pipeline/tests/fixtures/reco/games-carousel.json",
        "skills": {k: v["he"] for k, v in SKILLS.items()},
        "hook_structures": HOOK_STRUCTURES,
        "rotation": rotation_context(history, date_str),
        "slides": {str(k): v for k, v in SLIDE_ROLES.items()},
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
