#!/usr/bin/env python3
"""The test batch: a second kind of carousel every day, next to the child-voice carousels (Yarin, 10 Nov 2026).

Yarin, 10 Nov 2026: "i want to start uplaoding a different kind of carousels on the other days we dont", then on the five
suggestions: "lets do them all, everyday in addition to what we have, build it all and add it to the carousel machine as a
test batch section, give me different options for each day, you can use media from google drive, if you need to generate
images for a carousel just add a budget (lowest possible) and if i decide to produce it gives you permission for that
specific carousel". On the times: "try an evening hour on one of the new days and compare" and "we can upload in the
evening" (Saturday).

Five types (TYPES), one per day by a fixed rotation over 11 to 30 Nov 2026 (plan.json), two options a day (a and b):
    say      במקום זה, תגידו את זה   one sentence parents say and a better one to try instead, parent voice, no brand
    how      ככה זה עובד            the questions before ordering, real store screens and a real child's book, LumeBook named
    age      מה קורה בגיל            an age-stage cheat sheet, every point on a source, no brand
    gift     מתנה לחנוכה            for grandparents and gift givers, real covers, last order day for Hanukkah
    reveal   הרגע שהם רואים את הספר  a real child with his book (creator footage), LumeBook named

Files, all under test-batch/2026-11/:
    plan.json                    the days: date, type, morning or evening, post time
    assets.json                  every real picture a slide may use (key -> file, where it came from, rights note)
    carousels/DATE-OPT.json      one carousel (slides, caption, CTA, Facebook text, sources, pictures to make)
    slides/DATE-OPT/             the rendered draft slides (NN.png, contact sheet, render report)
    runs/DATE-OPT/               a production: jobs.json + generated-assets/ when it has pictures, approved.json, final/,
                                 facebook/facebook.txt, postiz.json (postiz_export.py reads it like an approved/ run)
    versions/DATE-OPT/vN.json    the carousel before each save in Carousel Machine

Pictures: real ones first (assets.json). A carousel that needs a made picture lists it under "pictures"; its budget is
the lowest the estimate allows (budget()). Pressing produce in Carousel Machine for that carousel is Yarin's permission
for that budget and that carousel only (his words above); the runner (openai_generate.py --max-usd) refuses anything past it.

    python3 carousel/carousel-pipeline/scripts/test_batch.py status
    python3 carousel/carousel-pipeline/scripts/test_batch.py lint [KEY ...]
    python3 carousel/carousel-pipeline/scripts/test_batch.py render [KEY ...]      # all when no key
    python3 carousel/carousel-pipeline/scripts/test_batch.py budget
Standard library only (the Carousel Machine server's Python has no Pillow); Chrome draws the slides.
"""

import argparse
import datetime as dt
import html
import json
import math
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel_lib as lib  # noqa: E402

ID = "test-2026-11"
HOME = lib.PIPELINE / "test-batch" / "2026-11"
PLAN = HOME / "plan.json"
ASSETS = HOME / "assets.json"
CARS = HOME / "carousels"
SLIDES = HOME / "slides"
RUNS = HOME / "runs"
VERSIONS = HOME / "versions"
W, H = 1080, 1350
KEY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[ab]$")
OPTION_HE = {"a": "אפשרות א", "b": "אפשרות ב"}
WEEKDAYS_HE = ("שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון")

TYPES = {
    "say": {"he": "במקום זה, תגידי את זה", "short_he": "במקום זה", "brand": False, "disclaimer": True,
            "about_he": "משפט שאמא או סבתא אומרת, ומשפט שכדאי לנסות במקומו. בלי מותג, תמונות אמיתיות ברקע.",
            "why_he": "בנוי לשיתוף ולשמירה. במחקר הקרוסלות, קרוסלת ״במקום X תגידו Y״ הייתה מהחזקות בארץ."},
    "how": {"he": "ככה זה עובד", "short_he": "ככה זה עובד", "brand": True, "disclaimer": False,
            "about_he": "השאלות של אמא או סבתא לפני שמזמינים: התצוגה המקדימה, ההקדשה, מה יש בפנים. מסכי האתר וספרים אמיתיים.",
            "why_he": "עונה על החששות שלפני ההזמנה. הריל ששאל ״מפחדים שהספר לא ייראה כמו הילד?״ הגיע לפי 3 עד 8 אנשים."},
    "age": {"he": "מה קורה בגיל", "short_he": "מה קורה בגיל", "brand": False, "disclaimer": True,
            "about_he": "דף לשמירה על גיל אחד, לאמא או לסבתא: דברים שנראים כמו בעיה וחלק מהגיל. כל נקודה על מקור.",
            "why_he": "בנוי לשמירה. חמש הקרוסלות החזקות של לוטם לרנר הן סדרות לפי גיל."},
    "gift": {"he": "מתנה לחנוכה", "short_he": "מתנה לחנוכה", "brand": True, "disclaimer": False,
             "about_he": "לסבתא, ולאמא שקונה מתנה: למה זו מתנה ששומרים, מה כותבים בהקדשה, עד מתי מזמינים.",
             "why_he": "לפי מטא, 43 מתוך 102 רכישות היו של נשים בנות 45 ומעלה. יום ההזמנה האחרון לחנוכה: 05 / 12."},
    "reveal": {"he": "הרגע שהם רואים את הספר", "short_he": "הרגע שהם רואים", "brand": True, "disclaimer": False,
               "about_he": "ילדים אמיתיים עם הספר שלהם: היוצרות של לומבוק, משפחות מתיקיית חומרי הגלם, ודברים שהאמהות אמרו באמת.",
               "why_he": "הוכחה אמיתית. בתוכנית של הרבעון זה הלב: רגעי פתיחה של ספר."},
}

# the look of each type over a photo (audience content: its own colours, never the page tokens): accent for chips and
# discs, hi for emphasised words on the dark fade
THEMES = {
    "say": {"accent": "#E2671B", "hi": "#FFB24A"},
    "how": {"accent": "#6B3CE6", "hi": "#CDBBFF"},
    "age": {"accent": "#0E8C7E", "hi": "#7FE6D4"},
    "gift": {"accent": "#2B55D6", "hi": "#F4CF7A"},
    "reveal": {"accent": "#D23A78", "hi": "#FF9EC4"},
}
ADDRESSEES = {"mom": "אמא", "grandma": "סבתא"}
# talking to one mom or one grandmother: no plural you (quotes of real people excepted)
PLURAL_RE = re.compile(r"(?<![\u05D0-\u05EA])(?:ו|ש|כש)?(תכתבו|תשמרו|תנסו|תגידו|תראו|אתם|לכם|שלכם|אתכם|בשבילכם|תזמינו|תבחרו|תעלו|תקראו|תשאלו|תנו|תדעו|תשלחו|תוסיפו|תחכו|תבדקו)(?![\u05D0-\u05EA])")
# the creators' own recorded words: a quote slide may only use words that are in one of these (no invented testimonials)
QUOTE_SOURCES = {
    "moran_arges": "media/projects/2026-10-24-grandma-baking-book-reel/moms/moran-words.json",
    "natali_fridman": "media/projects/2026-10-24-grandma-baking-book-reel/moms/natali-words.json",
    "nofit_hazut": "media/projects/2026-10-24-grandma-baking-book-reel/moms/nofit-words.json",
}

LAYOUTS = ("cover", "swap", "point", "photo", "covers", "quote", "cta")
TEXT_FIELDS = ("tag", "big", "label", "headline", "body", "no", "yes", "why", "quote", "by")
SLIDE_KEYS = ("layout", "bg", "pos", "text_at", "quote_from", "covers", "cover", "spread_art", "spread_photo", "num") + TEXT_FIELDS
NUM_FIELD = "num"   # the number disc of a point or swap slide (1 to 9), not text
TOP_FIELDS = ("title", "caption", "cta", "fb_text", "comment_word")
MAX_SLIDES = 10          # Postiz sends at most 10 pictures to an Instagram carousel (30 Oct 2026)
MIN_SLIDES = 6
FB_LINK = "https://lumebook.com/IL/he?utm_source=facebook&utm_medium=social"
BANNED_EXTRA = [   # rules of this project that the carousel validator does not know (memory, 5 to 9 Nov 2026)
    (r"₪|\bשקל|\bמחיר|\bהנח[הת]|\bמבצע|\bדמי משלוח", "no price, discount, sale or delivery cost (the reels rule, kept here)"),
    (r"קוד הנחה|קוד אישי", "never קוד הנחה or קוד אישי"),
    (r"(?<![\u05D0-\u05EA])(?:ו|ש|ב|מ|ל|כ|ה)?הכל(?![\u05D0-\u05EA])", "spell it הכול (full spelling)"),
    (r"\bבשפות\b|\bאנגלית\b|\bערבית\b|\bרוסית\b|עותק דיגיטלי|\bדיגיטלי", "no language options and no digital copy (Hebrew audience)"),
    (r"הילד שלי|הילדה שלי|הבן שלי|הבת שלי", "Yarin is not a parent: never הילד שלי in LumeBook's own voice"),
    (r"(?<!אמא ו)(?<![\u05D0-\u05EA])אבא(?![\u05D0-\u05EA])(?!\s+ואמא)", "talk to mom or both parents, never dad alone"),
    # the voice skill's never-list (.claude/skills/lumebook-hebrew-voice/SKILL.md)
    (r"חשוב לזכור|בואו נדבר על|(?<![\u05D0-\u05EA])המסע(?![\u05D0-\u05EA])|(?<![\u05D0-\u05EA])קסם(?![\u05D0-\u05EA])|להעצים|(?<![\u05D0-\u05EA])חוסן|(?<![\u05D0-\u05EA])להכיל(?![\u05D0-\u05EA])|(?<![\u05D0-\u05EA])לתקף|מרחב בטוח|בסופו של יום|הנה הדבר|מה שאף אחד לא מספר לכם",
     "a phrase the Hebrew voice skill never uses"),
]


# ---------------------------------------------------------------- files

def read(path):
    return lib.read_json(path)


def plan():
    return read(PLAN)


def assets():
    return read(ASSETS)["assets"] if ASSETS.exists() else {}


def keys():
    return sorted(p.stem for p in CARS.glob("*.json")) if CARS.exists() else []


def car_path(key):
    if not KEY_RE.match(str(key)):
        raise ValueError(f"bad test carousel key {key!r}")
    return CARS / f"{key}.json"


def load(key):
    return read(car_path(key))


def day_of(date):
    return next((d for d in plan()["days"] if d["date"] == date), None)


def weekday_he(date):
    return WEEKDAYS_HE[dt.date.fromisoformat(date).weekday()]


def when_he(day):
    return f'{"בבוקר" if day["slot"] == "morning" else "בערב"} {day["time"]}'


# ---------------------------------------------------------------- pictures and budget

def picture_jobs(car):
    """The pictures this carousel needs made (car["pictures"]), as openai_generate.py jobs: text-to-image, quality low."""
    import openai_pictures as op
    cfg = op.config()
    base = op.base_input(cfg)
    jobs = {}
    for name, p in (car.get("pictures") or {}).items():
        look = car.get("character") if p.get("character", True) else ""   # the recurring child, described in words (no photo is sent)
        prompt = " ".join(x for x in (look, p["scene"], lib.STYLE, lib.PALETTE, lib.AVOID,
                                       "Keep the faces and the main action inside the middle of the frame; the picture is cropped to 4:5.",
                                       lib.NO_TEXT) if x)
        refs = []
        if p.get("ref"):   # the child in the picture is the real child of this photo (Yarin, 11 Nov 2026)
            refs = [f"ref-{p['ref']}"]
            prompt = ("The child in this picture is the toddler in the reference photo: keep his face shape, curly light-brown hair, "
                      "dark brown eyes and round cheeks recognisable, drawn as a 3D animated character. " + prompt)
        job = {"mode": "edit" if refs else "generate", "model": cfg["model"], "input": {**base, "prompt": prompt}, "refs": refs,
               "purpose": p.get("purpose", "")}
        job["estimated_cost_usd"] = op.estimate_job(job, cfg)["usd"]
        jobs[name] = job
    return jobs


def prepare_refs(key, jobs):
    """Copy each reference photo (an assets.json picture) into the run as generated-assets/ref-KEY.png and mark it done and
    QA-passed in state.json (a real photo needs no generation)."""
    import subprocess
    run = RUNS / key
    gen = run / "generated-assets"
    gen.mkdir(parents=True, exist_ok=True)
    state_path = run / "state.json"
    state = read(state_path) if state_path.exists() else {"jobs": {}}
    for job in jobs.values():
        for ref in job.get("refs") or []:
            src = lib.ROOT / assets()[ref[4:]]["file"]
            dst = gen / f"{ref}.png"
            if not dst.exists():
                subprocess.run(["sips", "-s", "format", "png", str(src), "--out", str(dst)], check=True, capture_output=True)
            state["jobs"][ref] = {"status": "done", "attempts": 0, "replacements": 0, "qa": "pass", "notes": ["real photo, no generation"]}
    lib.write_json(state_path, state)


def budget(car):
    """{images, usd, budget_usd, model, quality, tokens}: the estimate and the lowest budget that covers it (rounded up to
    the next cent). No pictures: zero, nothing is ever called."""
    jobs = picture_jobs(car)
    if not jobs:
        return {"images": 0, "usd": 0.0, "budget_usd": 0.0}
    import openai_pictures as op
    cfg = op.config()
    total = op.estimate_total({"jobs": jobs}, cfg=cfg)
    return {"images": total["images"], "usd": total["usd"], "budget_usd": math.ceil(total["usd"] * 100 - 1e-9) / 100,
            "tokens": total["total_tokens"], "model": cfg["model"], "quality": cfg["quality"]}


def made_picture(key, name):
    p = RUNS / key / "generated-assets" / f"{name}.png"
    return p if p.exists() else None


# ---------------------------------------------------------------- checks

def _issue(level, path, message, excerpt=""):
    return lib.Issue(level, path, message, excerpt=excerpt) if excerpt else lib.Issue(level, path, message)


def lint(car, key=None):
    """Every rule a test carousel has to pass. Returns lib.Issue objects (ERROR blocks nothing, the page shows them)."""
    key = key or car.get("id", "?")
    out = []
    t = car.get("type")
    if t not in TYPES:
        return [_issue("ERROR", key, f"unknown type {t!r}")]
    slides = car.get("slides") or []
    if not MIN_SLIDES <= len(slides) <= MAX_SLIDES:
        out.append(_issue("ERROR", f"{key}/slides", f"{len(slides)} slides; {MIN_SLIDES} to {MAX_SLIDES} (Postiz sends at most 10)"))
    if slides and slides[0].get("layout") != "cover":
        out.append(_issue("ERROR", f"{key}/slide-1", "slide 1 is the cover"))
    if slides and slides[-1].get("layout") != "cta":
        out.append(_issue("ERROR", f"{key}/slide-{len(slides)}", "the last slide is the CTA"))
    known = assets()
    pics = car.get("pictures") or {}
    if car.get("addressee") not in ADDRESSEES:
        out.append(_issue("ERROR", f"{key}/addressee", "say who it talks to: mom or grandma (Yarin, 11 Nov 2026: \"talk to moms and grandmothers\")"))
    for i, s in enumerate(slides, start=1):
        p = f"{key}/slide-{i}"
        if s.get("layout") not in LAYOUTS:
            out.append(_issue("ERROR", p, f"layout {s.get('layout')!r} is not one of {LAYOUTS}"))
        if not s.get("bg"):
            out.append(_issue("ERROR", p, "every slide has a picture filling the background (bg); Yarin, 11 Nov 2026"))
        elif s["bg"] not in known and s["bg"] not in pics:
            out.append(_issue("ERROR", p, f"bg {s['bg']!r} is not in assets.json or the carousel's pictures"))
        if s.get("text_at") and s["text_at"] not in TEXT_AT:
            out.append(_issue("ERROR", p, f"text_at is one of {TEXT_AT}"))
        verified = False
        if s.get("layout") == "quote":
            ok, why = quote_check(s.get("quote", ""), s.get("quote_from", ""))
            verified = ok
            if not ok:
                out.append(_issue("ERROR", f"{p}/quote", why))
            if not s.get("by"):
                out.append(_issue("ERROR", f"{p}/by", "a quote says who said it"))
        if s.get("tag"):
            out.append(_issue("WARN", f"{p}/tag", "the tag chip is gone (Yarin, 11 Nov 2026): put its words in the headline; the cover's hook is `big`"))
        for f in TEXT_FIELDS:
            if f in s and s[f]:
                text = plain(s[f])
                if f == "label" and text.strip().isdigit():
                    continue
                if f == "quote" and verified:
                    out.extend(i for i in lib.audience_text_issues(f"{p}/{f}", text) if i.level == "ERROR" and "AI" in i.message)
                    continue
                out.extend(lib.audience_text_issues(f"{p}/{f}", text, allow_cta=s.get("layout") == "cta"))
                out.extend(extra_issues(f"{p}/{f}", text))
                out.extend(plural_issues(f"{p}/{f}", text))
                out.extend(tone_issues(f"{p}/{f}", text))
        if NUM_FIELD in s and not (isinstance(s[NUM_FIELD], int) and 1 <= s[NUM_FIELD] <= 9):
            out.append(_issue("ERROR", p, "num is a whole number from 1 to 9"))
        words = sum(len(lib.words(plain(s.get(f, "")))) for f in TEXT_FIELDS)
        limit = {"cover": 18, "cta": 26}.get(s.get("layout"), 30)   # text sits on the photo: short (11 Nov 2026, after the review)
        if words > limit:
            out.append(_issue("ERROR", p, f"{words} words on the slide (max {limit})"))
        for k in list(s.get("covers") or []) + [s[x] for x in ("cover", "spread_art", "spread_photo") if s.get(x)]:
            if k not in known and k not in pics:
                out.append(_issue("ERROR", p, f"picture {k!r} is not in assets.json"))
            elif k not in known:
                pass
            elif not (lib.ROOT / known[k]["file"]).exists():
                out.append(_issue("ERROR", p, f"picture file missing: {known[k]['file']}"))
        for old in ("photo", "picture"):
            if s.get(old):
                out.append(_issue("ERROR", p, f"{old} is gone since 11 Nov 2026: put the picture in bg"))
    word = car.get("comment_word", "")
    out.extend(lib.code_word_issues(f"{key}/comment_word", word))
    cta = car.get("cta", "")
    if not cta.strip():
        out.append(_issue("ERROR", f"{key}/cta", "missing"))
    else:
        out.extend(lib.audience_text_issues(f"{key}/cta", cta, allow_cta=True))
        if f'"{word}"' not in cta or "תכתבי" not in cta or "קישור" not in cta:
            out.append(_issue("ERROR", f"{key}/cta", f'the CTA asks her to comment "{word}" for the link: תכתבי "{word}" ... קישור'))
        out.extend(plural_issues(f"{key}/cta", cta))
        last = slides[-1] if slides else {}
        if lib.collapse(plain(last.get("body", "")) + " " + plain(last.get("headline", ""))).find(lib.collapse(cta.split("\n")[-1])) < 0:
            out.append(_issue("ERROR", f"{key}/slide-{len(slides)}", "the last slide carries the CTA's last line"))
    cap = car.get("caption", "")
    if not cap.strip():
        out.append(_issue("ERROR", f"{key}/caption", "missing"))
    else:
        out.extend(lib.audience_text_issues(f"{key}/caption", cap, allow_cta=True))
        out.extend(extra_issues(f"{key}/caption", cap))
        out.extend(plural_issues(f"{key}/caption", cap))
        if not lib.collapse(cap).endswith(lib.collapse(cta)):
            out.append(_issue("ERROR", f"{key}/caption", "the caption ends with the CTA"))
    fb = car.get("fb_text", "")
    if not fb.strip():
        out.append(_issue("ERROR", f"{key}/fb_text", "missing (Facebook gets its own text, 31 Oct 2026)"))
    else:
        out.extend(lib.audience_text_issues(f"{key}/fb_text", fb, allow_cta=True))
        out.extend(extra_issues(f"{key}/fb_text", fb))
        out.extend(plural_issues(f"{key}/fb_text", fb))
        if "http" in fb:
            out.append(_issue("ERROR", f"{key}/fb_text", "no link in the text; the export adds the site link at the end"))
        if f'"{word}"' in fb or "בתגובות" in fb:
            out.append(_issue("ERROR", f"{key}/fb_text", "no comment word on Facebook (31 Oct 2026): the post ends with the link"))
    if not TYPES[t]["brand"]:
        for i, s in enumerate(slides[:-1], start=1):
            for f in TEXT_FIELDS:
                if re.search(r"לומבוק|LumeBook", s.get(f, "") or ""):
                    out.append(_issue("ERROR", f"{key}/slide-{i}/{f}", "this type names no brand on the slides"))
    if t == "age" and not car.get("sources"):
        out.append(_issue("ERROR", f"{key}/sources", "every age point needs a source you read"))
    for name, p in pics.items():
        if len((p.get("scene") or "").strip()) < 40:
            out.append(_issue("ERROR", f"{key}/pictures/{name}", "describe the scene (in English, 40+ characters)"))
    return out


def tone_issues(path, text):
    """WARN: a line that opens with עוזר reads like a translated parenting guide (the review of 11 Nov 2026)."""
    return [_issue("WARN", path, "starts like a parenting guide (עוזר...): say it the way she would", excerpt=l[:40])
            for l in lib.lines_of(text) if re.match(r"^\s*(ו)?עוזר(ת|ים)?\s", l)]


def plural_issues(path, text):
    m = PLURAL_RE.search(lib.collapse(text))
    return [_issue("ERROR", path, "talk to one mom or one grandmother (את, תכתבי, לך), not to a plural you", excerpt=m.group(0))] if m else []


_TRANSCRIPTS = {}


def _norm_words(text):
    return re.findall(r"[\u05D0-\u05EA]+|\d+", str(text or ""))


def quote_check(quote, source):
    """(ok, why): the quote must be the creator's own recorded words, in order (QUOTE_SOURCES), so nothing is invented."""
    if source not in QUOTE_SOURCES:
        return False, f"quote_from is one of {sorted(QUOTE_SOURCES)} (their recorded words); never an invented quote"
    if source not in _TRANSCRIPTS:
        path = lib.ROOT / QUOTE_SOURCES[source]
        _TRANSCRIPTS[source] = _norm_words(" ".join(w["w"] for w in lib.read_json(path))) if path.exists() else []
    said, q = _TRANSCRIPTS[source], _norm_words(plain(quote))
    if len(q) < 3:
        return False, "a quote has at least 3 words"
    n = len(q)
    if any(said[i:i + n] == q for i in range(len(said) - n + 1)):
        return True, ""
    return False, f"these words are not in {source}'s recording, in this order"


def extra_issues(path, text):
    flat = lib.collapse(text)
    return [_issue("ERROR", path, why, excerpt=m.group(0)) for pattern, why in BANNED_EXTRA for m in [re.search(pattern, flat)] if m]


def issue_dicts(issues):
    return [{"level": i.level, "path": str(i.path), "message": i.message, "slide": _slide_no(i.path)} for i in issues]


def _slide_no(path):
    m = re.search(r"/slide-(\d+)", str(path))
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- slides

EMPH_RE = re.compile(r"\*\*(.+?)\*\*")
# A date as dd / mm (/ yyyy). In right-to-left text the spaces split it, so "05 / 12" shows as "12 / 05" (found by the gift
# writer, 10 Nov 2026): the slides draw it left to right, and the export puts a left-to-right mark before it in the texts.
DATE_RE = re.compile("\u200e?(\\d{1,2} / \\d{1,2}(?: / \\d{4})?)")


def ltr_dates(text):
    """The caption or Facebook text with a left-to-right mark (U+200E) before every dd / mm date, once."""
    return DATE_RE.sub(lambda m: "\u200e" + m.group(1), str(text or ""))


def plain(text):
    return EMPH_RE.sub(r"\1", str(text or ""))


def rich(text):
    """Hebrew text to HTML: **emphasis** in the accent colour, one line per line."""
    out = []
    for line in str(text or "").split("\n"):
        line = html.escape(line.strip())
        line = re.sub(r'(\S*(?:״|&quot;)\S*)', r'<span class="nw">\1</span>', line)   # a quote mark never wraps alone
        line = DATE_RE.sub(lambda m: f'<span dir="ltr" class="nw">{m.group(1)}</span>', line)   # 05 / 12 stays 05 / 12 in RTL
        out.append(EMPH_RE.sub(r'<em>\1</em>', line))
    return "<br>".join(x for x in out if x) if any(out) else ""


def _src(path, base):
    return Path(os.path.relpath(Path(path).resolve(), Path(base).resolve())).as_posix()


def _tile(key, base, cls):
    """A small picture tile over the photo: a book cover in a covers row or on the CTA."""
    a = assets().get(key)
    if not a:
        return f'<div class="{cls} missing">חסרה תמונה: {html.escape(str(key))}</div>'
    return f'<div class="{cls}"><img src="{_src(lib.ROOT / a["file"], base)}" alt="" style="object-position:{a.get("position", "50% 50%")}"></div>'


def _book3d(key, base):
    """A real-looking book for the CTA (Yarin, 11 Nov 2026: "the book is flat, it should look like a book"): the store cover on a
    front face with a hinge groove, a spine, a stack of pages and a top edge, tilted in 3D, with a soft shadow on the ground."""
    a = assets().get(key)
    if not a:
        return f'<div class="book3d missing">חסרה תמונה: {html.escape(str(key))}</div>'
    img = f'<img src="{_src(lib.ROOT / a["file"], base)}" alt="" style="object-position:{a.get("position", "50% 50%")}">'
    return ('<div class="book3d"><div class="bk">'
            f'<div class="face front">{img}<i class="sheen"></i></div><div class="face back"></div>'
            '<div class="face spine"></div><div class="face pages"></div><div class="face top"></div><div class="face bottom"></div>'
            '</div><div class="bk-shadow"></div></div>')


def _open_book(car, art_key, photo_key, base, key):
    """An open LumeBook book for the CTA (Yarin, 11 Nov 2026: "the book should be open and look like a real lumebook book"): a Hebrew
    spread, so the dedication page is on the right (the real one: the line about the one book in the world, the child's round
    photo with a teal ring, the dedication line, the LumeBook logo) and the first illustration page on the left, tilted on
    a cover board with a stack of page edges under it and a shadow."""
    photo = assets().get(photo_key) if photo_key else None
    if art_key in (car.get("pictures") or {}):   # a picture made for this carousel fills the illustration page
        made = made_picture(key, art_key)
        art_src, art_pos = (_src(made, base), "50% 50%") if made else (None, "")
    else:
        art = assets().get(art_key)
        art_src, art_pos = (_src(lib.ROOT / art["file"], base), art.get("position", "50% 50%")) if art else (None, "")
    if not art_src:
        return f'<div class="obook missing">חסרה תמונה: {html.escape(str(art_key))}</div>'
    logo = _src(lib.ROOT / "shared" / "brand" / "logo_wide.png", base)
    ph = (f'<div class="ph"><img src="{_src(lib.ROOT / photo["file"], base)}" alt="" style="object-position:{photo.get("position", "50% 30%")}"></div>'
          if photo else "")
    return ('<div class="obook"><div class="spread"><div class="base"></div>'
            f'<div class="pg left"><img src="{art_src}" alt="" style="object-position:{art_pos}"><i class="gut"></i></div>'
            '<div class="pg right"><p class="t1">את הספר הזה לא תוכלו למצוא בשום מקום,<br>יש אחד כזה בכל העולם!</p>'
            f'{ph}<p class="t2">הספר הזה מוקדש מכל הלב</p><i class="ln"></i><img class="lg" src="{logo}" alt=""><i class="gut"></i></div>'
            '<div class="stack"></div></div><div class="ob-shadow"></div></div>')


def _bg(car, s, base, key):
    """The slide's background, filling it edge to edge (Yarin, 11 Nov 2026: "i need the media to fill most of the bg"):
    a real picture from assets.json, or a picture the carousel makes when produced."""
    k = s.get("bg")
    if not k:
        return '<div class="bg none"></div>'
    pics = car.get("pictures") or {}
    if k in pics:
        made = made_picture(key, k)
        if made:
            return f'<img class="bg" src="{_src(made, base)}" alt="" style="object-position:{s.get("pos", "50% 40%")}">'
        return f'<div class="bg todo"><span>תמונה שתיווצר בהפקה</span><small>{html.escape(pics[k].get("purpose", ""))}</small></div>'
    a = assets().get(k)
    if not a:
        return f'<div class="bg none missing">חסרה תמונה: {html.escape(str(k))}</div>'
    return f'<img class="bg" src="{_src(lib.ROOT / a["file"], base)}" alt="" style="object-position:{s.get("pos") or a.get("position", "50% 40%")}">'


ARROW = ('<div class="arrow"><svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="2.6" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M11 18l-6-6 6-6"/></svg></div>')
SAVE_ICON = ('<svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round">'
             '<path d="M6 3h12v18l-6-4.5L6 21z"/></svg>')
BUBBLE_ICON = ('<svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round">'
               '<path d="M4 5h16v11H9l-5 4z"/></svg>')
TEXT_AT = ("bottom", "top", "full")


def slide_html(car, s, n, total, base, key):
    """One slide: the picture fills the background, a dark fade on the text side, the words in white on it."""
    t = car["type"]
    lay = s.get("layout", "point")
    at = s.get("text_at", "bottom") if s.get("text_at") in TEXT_AT else "bottom"
    parts = [f'<section class="slide l-{lay} at-{at}" data-n="{n}">', _bg(car, s, base, key), '<div class="scrim"></div>']
    if TYPES[t]["brand"] and n == 1:
        parts.append('<div class="brand">לומבוק</div>')
    z = []
    if s.get(NUM_FIELD):
        z.append(f'<div class="num">{int(s[NUM_FIELD])}</div>')
    if s.get("label"):
        z.append(f'<div class="label">{rich(s["label"])}</div>')
    cover_hook = lay == "cover" and s.get("big")
    if cover_hook and s.get("headline"):   # the context line sits above the hook (Yarin, 11 Nov 2026: the hook is the big text)
        z.append(f'<h1 class="h">{rich(s["headline"])}</h1>')
    if cover_hook:
        z.append(f'<div class="big">{rich(s["big"])}</div>')
    if lay == "quote":
        z.append(f'<blockquote class="q">{rich(s.get("quote", ""))}</blockquote>')
        if s.get("by"):
            z.append(f'<div class="by">{rich(s["by"])}</div>')
    elif s.get("headline") and not cover_hook:
        tag = "h1" if lay == "cover" else "h2"
        z.append(f'<{tag} class="h">{rich(s["headline"])}</{tag}>')
    if (lay == "swap" or lay == "cover") and (s.get("no") or s.get("yes")):
        z.append('<div class="pair">' + (f'<div class="card no"><span class="k">במקום</span><p>{rich(s["no"])}</p></div>' if s.get("no") else "")
                 + (f'<div class="card yes"><span class="k">לנסות</span><p>{rich(s["yes"])}</p></div>' if s.get("yes") else "") + '</div>')
    if s.get("body"):
        body = rich(s["body"])
        word = car.get("comment_word", "")
        if lay == "cta" and word:
            body = body.replace(f'&quot;{html.escape(word)}&quot;', f'<b class="word">״{html.escape(word)}״</b>')
        z.append(f'<p class="b">{body}</p>')
    if lay == "swap" and s.get("why"):
        z.append(f'<p class="b why">{rich(s["why"])}</p>')
    if lay == "covers" and s.get("covers"):
        cv = s["covers"][:4]
        z.append(f'<div class="covers n{len(cv)}">' + "".join(_tile(c, base, "cv") for c in cv) + '</div>')
    if lay == "cta":
        if s.get("spread_art"):
            z.append(_open_book(car, s["spread_art"], s.get("spread_photo"), base, key))
        elif s.get("cover"):
            z.append(_book3d(s["cover"], base))
        z.append(f'<div class="icons"><span>{BUBBLE_ICON}</span><span>{SAVE_ICON}</span></div>')
    parts.append('<div class="zone">' + "".join(z) + '</div>')
    if n < total:
        parts.append(ARROW)
    parts.append('</section>')
    return "".join(parts)


def css(t, base):
    th = THEMES[t]
    fonts = _src(lib.PIPELINE / "assets" / "fonts", base)
    v = "".join(f"--{k.replace('_', '-')}:{c};" for k, c in th.items())
    return f"""
@font-face{{font-family:"Heebo LB";src:url("{fonts}/Heebo-Black.ttf") format("truetype");font-weight:900}}
@font-face{{font-family:"Heebo LB";src:url("{fonts}/Heebo-Bold.ttf") format("truetype");font-weight:700}}
@font-face{{font-family:"Assistant LB";src:url("{fonts}/Assistant-VariableFont_wght.ttf") format("truetype");font-weight:200 800}}
:root{{{v}--shade:10,6,22}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:#111}}
body{{width:{W}px;direction:rtl;font-family:"Assistant LB",sans-serif;-webkit-font-smoothing:antialiased}}
.slide{{--k:1;width:{W}px;height:{H}px;position:relative;overflow:hidden;background:#1a1426;color:#fff;text-align:center}}
body.one .slide{{display:none}} body.one .slide.on{{display:block}}
.bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}}
.bg.none{{background:radial-gradient(120% 90% at 50% 20%, var(--accent), #1a1426 70%)}}
.bg.todo{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;background:#2a2340;border:6px dashed var(--hi);color:var(--hi);font:700 44px "Heebo LB"}}
.bg.todo small{{font:500 28px "Assistant LB";color:#fff;opacity:.8;max-width:80%;direction:rtl}}
.missing{{color:#ff8a8a;font:700 30px "Heebo LB";display:flex;align-items:center;justify-content:center}}
.scrim{{position:absolute;inset:0;pointer-events:none}}
.at-bottom .scrim{{background:linear-gradient(to top, rgba(var(--shade),.93) 0%, rgba(var(--shade),.84) 34%, rgba(var(--shade),.45) 56%, rgba(var(--shade),0) 74%)}}
.at-top .scrim{{background:linear-gradient(to bottom, rgba(var(--shade),.93) 0%, rgba(var(--shade),.82) 32%, rgba(var(--shade),.4) 54%, rgba(var(--shade),0) 70%),
  linear-gradient(to top, rgba(var(--shade),.6) 0%, rgba(var(--shade),0) 14%)}}
.at-full .scrim{{background:rgba(var(--shade),.58)}}
.zone{{position:absolute;left:72px;right:72px;display:flex;flex-direction:column;align-items:center;gap:calc(var(--k)*22px);text-shadow:0 2px 16px rgba(0,0,0,.35)}}
.at-bottom .zone{{bottom:126px;max-height:60%;justify-content:flex-end}}
.at-top .zone{{top:80px;max-height:60%;justify-content:flex-start}}
.at-full .zone{{top:96px;bottom:126px;justify-content:center}}
.brand{{position:absolute;top:40px;left:52px;font:900 36px "Heebo LB";color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.45);z-index:2}}
.at-top .brand{{top:auto;bottom:46px;left:auto;right:56px}}
.tag{{background:var(--accent);color:#fff;font:700 calc(var(--k)*38px) "Heebo LB";padding:12px 34px;border-radius:999px;text-shadow:none;box-shadow:0 8px 20px rgba(0,0,0,.25)}}
.label{{background:rgba(255,255,255,.16);border:1.5px solid rgba(255,255,255,.4);color:#fff;font:700 calc(var(--k)*38px) "Heebo LB";padding:8px 30px;border-radius:999px;text-shadow:none}}
.num{{width:calc(var(--k)*112px);height:calc(var(--k)*112px);flex:none;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font:900 calc(var(--k)*64px) "Heebo LB";text-shadow:none;box-shadow:0 10px 24px rgba(0,0,0,.3)}}
.big{{font:900 calc(var(--k)*230px)/.92 "Heebo LB";color:var(--hi)}}
.h{{margin:0;font:900 calc(var(--k)*96px)/1.07 "Heebo LB";letter-spacing:-.005em;text-wrap:balance}}
.l-cover .h{{font-size:calc(var(--k)*124px);line-height:1.02}}
.l-cover .h:has(+ .big){{font-size:calc(var(--k)*72px);line-height:1.1;font-weight:700}}
.l-cover .big{{font-size:calc(var(--k)*158px);line-height:1.0;text-wrap:balance;letter-spacing:-.01em}}
.zone > .h:last-child{{padding-bottom:.16em}}
.l-cta .h{{font-size:calc(var(--k)*104px);line-height:1.04}}
.l-cta .zone{{max-height:80%;gap:calc(var(--k)*20px)}}
.l-cta .b{{font-size:calc(var(--k)*64px);line-height:1.28;font-weight:700}}
.l-cta .scrim{{background:linear-gradient(to bottom, rgba(var(--shade),.92) 0%, rgba(var(--shade),.82) 50%, rgba(var(--shade),.6) 100%)}}
.l-cta.at-bottom .scrim{{background:linear-gradient(to top, rgba(var(--shade),.92) 0%, rgba(var(--shade),.82) 50%, rgba(var(--shade),.6) 100%)}}
.b{{margin:0;font:600 calc(var(--k)*48px)/1.3 "Assistant LB";color:rgba(255,255,255,.94);text-wrap:pretty}}
.l-cover .b{{font-size:calc(var(--k)*58px)}}
em{{font-style:normal;color:var(--hi)}}
.pair{{display:flex;flex-direction:column;gap:calc(var(--k)*18px);width:100%}}
.card{{border-radius:30px;padding:calc(var(--k)*20px) 38px calc(var(--k)*24px);text-align:right;text-shadow:none}}
.card .k{{display:inline-block;font:900 calc(var(--k)*30px) "Heebo LB";margin-bottom:calc(var(--k)*6px);padding:2px 16px;border-radius:999px}}
.card p{{margin:0;font:800 calc(var(--k)*54px)/1.14 "Heebo LB"}}
.card.no p{{font-size:calc(var(--k)*40px)}}
.card.no{{background:rgba(255,255,255,.14);border:1.5px solid rgba(255,255,255,.34);color:#fff;backdrop-filter:blur(6px)}}
.card.no .k{{background:rgba(255,120,130,.9);color:#fff}}
.card.no p{{opacity:.9;text-decoration:line-through;text-decoration-thickness:5px;text-decoration-color:rgba(255,120,130,.85)}}
.card.yes{{background:#fff;color:#14592f;box-shadow:0 16px 36px rgba(0,0,0,.3)}}
.card.yes .k{{background:#1f8a4c;color:#fff}}
.l-cover .card p{{font-size:calc(var(--k)*56px)}}
.why{{font-size:calc(var(--k)*40px)}}
.l-swap .zone{{max-height:52%}}
.l-swap .num{{width:calc(var(--k)*92px);height:calc(var(--k)*92px);font-size:calc(var(--k)*52px)}}
.covers{{display:flex;justify-content:center;align-items:center;gap:26px;width:100%;height:calc(var(--k)*330px);flex:none}}
.cv{{position:relative;height:100%;aspect-ratio:1/1;max-width:46%;border-radius:16px;overflow:hidden;background:#fff;box-shadow:0 18px 40px rgba(0,0,0,.45),0 0 0 7px #fff}}
.covers.n3 .cv{{height:80%;max-width:31%}} .covers.n4 .cv{{height:64%;max-width:23%}}
.covers .cv:nth-child(odd){{transform:rotate(-3deg)}} .covers .cv:nth-child(even){{transform:rotate(3deg)}}
.cv img,.book img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.q{{margin:0;font:900 calc(var(--k)*80px)/1.16 "Heebo LB";color:#fff}}
.q::before{{content:"״";display:block;font-size:1.5em;line-height:.6;color:var(--hi)}}
.by{{font:700 calc(var(--k)*40px) "Heebo LB";color:var(--hi)}}
.word{{display:inline-block;background:var(--accent);color:#fff;border-radius:18px;padding:0 22px;margin:6px 0;font-weight:900;text-shadow:none}}
.book3d{{position:relative;width:calc(var(--k)*440px);height:calc(var(--k)*420px);flex:none;perspective:1800px}}
.bk{{--s:calc(var(--k)*340px);--t:calc(var(--k)*56px);position:absolute;left:50%;top:calc(var(--k)*28px);width:var(--s);height:var(--s);margin-left:calc(var(--s)/-2);transform-style:preserve-3d;transform:rotateX(-13deg) rotateY(34deg) rotateZ(-2deg)}}
.bk .face{{position:absolute;backface-visibility:hidden}}
.bk .front{{inset:0;transform:translateZ(calc(var(--t)/2));border-radius:3px 9px 9px 3px;overflow:hidden;background:#fff}}
.bk .front img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.bk .sheen{{position:absolute;inset:0;background:linear-gradient(100deg, rgba(0,0,0,.28) 0, rgba(0,0,0,0) 7%, rgba(255,255,255,.14) 9%, rgba(255,255,255,0) 14%, rgba(255,255,255,0) 60%, rgba(255,255,255,.2) 100%)}}
.bk .back{{inset:0;transform:translateZ(calc(var(--t)/-2)) rotateY(180deg);background:#2a2340;border-radius:9px 3px 3px 9px}}
.bk .spine{{width:var(--t);height:100%;top:0;right:calc(var(--t)/-2);transform:rotateY(90deg);background:linear-gradient(90deg,#241c38,#3b2f5c 50%,#241c38);border-radius:3px}}
.bk .pages{{width:var(--t);height:calc(100% - 8px);top:4px;left:calc(var(--t)/-2);transform:rotateY(-90deg);background:repeating-linear-gradient(90deg,#fffdf8 0 1.5px,#e6e0d2 1.5px 3px)}}
.bk .top{{width:calc(100% - 8px);height:var(--t);left:4px;top:calc(var(--t)/-2);transform:rotateX(90deg);background:repeating-linear-gradient(180deg,#fffdf8 0 1.5px,#e6e0d2 1.5px 3px)}}
.bk .bottom{{width:calc(100% - 8px);height:var(--t);left:4px;bottom:calc(var(--t)/-2);transform:rotateX(-90deg);background:#cfc8b8}}
.obook{{position:relative;width:calc(var(--k)*820px);height:calc(var(--k)*420px);flex:none;perspective:1700px}}
.spread{{--p:calc(var(--k)*390px);position:absolute;left:50%;top:calc(var(--k)*34px);width:calc(var(--p)*2);height:var(--p);margin-left:calc(var(--p)*-1);transform-style:preserve-3d;transform:rotateX(36deg) rotateZ(-2.5deg)}}
.spread .base{{position:absolute;inset:calc(var(--k)*-9px);transform:translateZ(calc(var(--k)*-10px));background:#33285a;border-radius:12px;box-shadow:0 0 0 2px rgba(255,255,255,.08)}}
.spread .pg{{position:absolute;top:0;width:var(--p);height:var(--p);overflow:hidden;background:#eeecf8;backface-visibility:hidden}}
.spread .left{{left:0;transform-origin:100% 50%;transform:rotateY(6deg);border-radius:6px 0 0 6px}}
.spread .right{{left:var(--p);transform-origin:0 50%;transform:rotateY(-6deg);border-radius:0 6px 6px 0;display:flex;flex-direction:column;align-items:center;padding:calc(var(--k)*34px) calc(var(--k)*26px) calc(var(--k)*20px);text-align:center;color:#2a2740;text-shadow:none;font-family:"Assistant LB",sans-serif}}
.spread .pg img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.spread .right img.lg{{position:static;width:calc(var(--k)*190px);height:auto;margin-top:auto;object-fit:contain}}
.spread .t1{{margin:0;font:600 calc(var(--k)*20px)/1.35 "Assistant LB";color:#2a2740}}
.spread .t2{{margin:calc(var(--k)*10px) 0 0;font:600 calc(var(--k)*21px)/1.3 "Assistant LB";color:#2a2740}}
.spread .ph{{position:relative;width:calc(var(--k)*118px);height:calc(var(--k)*118px);flex:none;margin-top:calc(var(--k)*16px);border-radius:50%;overflow:hidden;box-shadow:0 0 0 calc(var(--k)*5px) #8fd6d8,0 0 18px rgba(143,214,216,.8)}}
.spread .ph img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.spread .ln{{display:block;width:62%;height:2px;background:#9a97b3;margin:calc(var(--k)*14px) 0}}
.spread .gut{{position:absolute;top:0;bottom:0;width:26%;pointer-events:none}}
.spread .left .gut{{right:0;background:linear-gradient(to left,rgba(0,0,0,.34),rgba(0,0,0,0))}}
.spread .right .gut{{left:0;background:linear-gradient(to right,rgba(0,0,0,.34),rgba(0,0,0,0))}}
.spread .stack{{position:absolute;left:0;top:100%;width:100%;height:calc(var(--k)*20px);transform-origin:top;transform:rotateX(-90deg);background:repeating-linear-gradient(180deg,#fffdf8 0 2px,#d8d2c2 2px 3.5px);border-bottom:calc(var(--k)*5px) solid #33285a}}
.ob-shadow{{position:absolute;left:50%;bottom:calc(var(--k)*2px);width:calc(var(--k)*760px);height:calc(var(--k)*50px);margin-left:calc(var(--k)*-380px);background:radial-gradient(ellipse at center,rgba(0,0,0,.6),rgba(0,0,0,0) 70%);filter:blur(7px)}}
.bk-shadow{{position:absolute;left:50%;bottom:calc(var(--k)*6px);width:calc(var(--k)*330px);height:calc(var(--k)*46px);margin-left:calc(var(--k)*-165px);background:radial-gradient(ellipse at center,rgba(0,0,0,.6),rgba(0,0,0,0) 70%);filter:blur(5px)}}
.book{{position:relative;width:calc(var(--k)*240px);aspect-ratio:1/1;flex:none;border-radius:14px;overflow:hidden;transform:rotate(-4deg);box-shadow:0 22px 46px rgba(0,0,0,.5),0 0 0 9px #fff}}
.icons{{display:flex;justify-content:center;gap:24px;color:#fff}}
.icons span{{width:60px;height:60px;border-radius:50%;background:rgba(255,255,255,.18);border:1.5px solid rgba(255,255,255,.4);display:flex;align-items:center;justify-content:center}}
.arrow{{position:absolute;left:50%;margin-left:-36px;bottom:38px;width:72px;height:72px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 18px rgba(0,0,0,.3)}}
.nw{{white-space:nowrap}}
#report{{display:none}}
"""


FIT_JS = """
(function(){
  const q = new URLSearchParams(location.search), one = q.get('s');
  const slides = [...document.querySelectorAll('.slide')];
  if (one) { document.body.classList.add('one'); slides.forEach(s => s.classList.toggle('on', s.dataset.n === one)); }
  const over = s => { const z = s.querySelector('.zone'); if (!z) return false;
    const r = z.getBoundingClientRect(), sr = s.getBoundingClientRect();
    const cv = s.querySelector('.covers'); const small = cv && cv.getBoundingClientRect().height < 220;
    return z.scrollHeight > z.clientHeight + 22 || r.top - sr.top < 36 || sr.bottom - r.bottom < 110 || small; };   // Heebo Black's letters reach past a tight line box: a few px is not overflow
  const report = [];
  const fit = () => slides.forEach(s => { if (one && s.dataset.n !== one) return; let k = 1; s.style.setProperty('--k', k);
    while (over(s) && k > 0.56) { k = Math.round((k - 0.03) * 100) / 100; s.style.setProperty('--k', k); }
    const z = s.querySelector('.zone');
    report.push({n: Number(s.dataset.n), k, fits: !over(s), dir: getComputedStyle(s).direction, zone: z ? Math.round(z.getBoundingClientRect().height) : 0}); });
  const done = () => { fit(); if (q.get('check')) document.getElementById('report').textContent = JSON.stringify(report); };
  let ran = false; const once = () => { if (!ran) { ran = true; done(); } };   // the boxes have fixed sizes: only the fonts change the layout
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(once); setTimeout(once, 2500);
})();
"""


def slides_html(car, key, out_dir):
    total = len(car["slides"])
    body = "".join(slide_html(car, s, n, total, out_dir, key) for n, s in enumerate(car["slides"], start=1))
    return ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{html.escape(key)}</title><style>{css(car["type"], out_dir)}</style></head>'
            f'<body dir="rtl" class="t-{car["type"]}">{body}<pre id="report"></pre><script>{FIT_JS}</script></body></html>')


def render(key, out_dir=None, png=True):
    """Draw the carousel's slides as 1080 x 1350 PNGs (drafts in slides/KEY, or out_dir for a production). Returns problems."""
    import compose_slides as cs
    car = load(key)
    out_dir = Path(out_dir or SLIDES / key)
    out_dir.mkdir(parents=True, exist_ok=True)
    page = out_dir / "slides.html"
    page.write_text(slides_html(car, key, out_dir), encoding="utf-8")
    for old in out_dir.glob("[0-9][0-9].png"):
        if int(old.stem) > len(car["slides"]):
            old.unlink()
    if not png:
        return []
    dom = cs.dump_dom(page.as_uri() + "?check=1", W, H)
    m = re.search(r'<pre id="report">(.*?)</pre>', dom, re.S)
    report = json.loads(html.unescape(m.group(1))) if m and m.group(1).strip() else []
    problems = [f"slide {r['n']}: the text does not fit even at the smallest size; shorten it" for r in report if not r.get("fits")]
    problems += [f"slide {r['n']}: direction {r['dir']}" for r in report if r.get("dir") != "rtl"]
    if not report:
        problems.append("the slide check could not read the page")
    for n in range(1, len(car["slides"]) + 1):
        cs.screenshot(page.as_uri() + f"?s={n}", out_dir / f"{n:02d}.png", W, H)
    cs.contact_sheet(out_dir, len(car["slides"]))
    lib.write_json(out_dir / "render-report.json", {"problems": problems, "slides": report})
    return problems


# ---------------------------------------------------------------- Carousel Machine

def _url(path):
    return "/" + Path(path).resolve().relative_to(lib.PIPELINE.resolve()).as_posix()


def items():
    """Every test carousel as a Carousel Machine item (kind "test"), in day order, a before b."""
    days = {d["date"]: (i, d) for i, d in enumerate(plan()["days"], start=1)}
    known = assets()
    out = []
    for key in keys():
        car = load(key)
        date = car["date"]
        n, day = days.get(date, (99, {"slot": "evening", "time": "20:30", "type": car["type"]}))
        t = TYPES[car["type"]]
        out_dir = SLIDES / key
        pngs = [out_dir / f"{i:02d}.png" for i in range(1, len(car["slides"]) + 1)]
        images = [f"{_url(p)}?v={int(p.stat().st_mtime)}" for p in pngs if p.exists()]
        issues = lint(car, key)
        rep = out_dir / "render-report.json"
        render_problems = read(rep).get("problems", []) if rep.exists() else ["עוד לא צוירו שקופיות"]
        used = sorted({k for s in car["slides"] for k in ([s.get("bg")] + list(s.get("covers") or []) + [s.get("cover")]) if k})
        out.append({
            "batch": ID, "key": f"{ID}/{key}", "kind": "test", "id": key, "date": date, "slot": n, "type": car["type"],
            "type_he": t["he"], "topic_he": t["he"], "topic_id": car["type"], "option": car["option"],
            "option_he": OPTION_HE[car["option"]], "title": car.get("title", ""), "angle_he": car.get("angle_he", ""),
            "when_he": when_he(day), "post_time": day["time"], "slot_kind": day["slot"], "weekday_he": weekday_he(date),
            "about_he": t["about_he"], "why_he": t["why_he"], "brand": t["brand"],
            "cover": lib.collapse(plain(car["slides"][0].get("headline", ""))) if car["slides"] else "",
            "headlines": [lib.collapse(plain(s.get("headline") or s.get("yes") or s.get("quote") or "")) for s in car["slides"]],
            "slides": [{"n": i, "layout": s.get("layout"), **{f: s[f] for f in TEXT_FIELDS + (NUM_FIELD,) if f in s},
                        **{f: s[f] for f in ("bg", "text_at") if s.get(f)}, "bg_he": known.get(s.get("bg"), {}).get("what_he", "")}
                       for i, s in enumerate(car["slides"], start=1)],
            "images": images, "caption": car.get("caption", ""), "cta": car.get("cta", ""), "fb_text": car.get("fb_text", ""),
            "comment_word": car.get("comment_word", ""), "budget": budget(car), "addressee": car.get("addressee", ""),
            "addressee_he": ADDRESSEES.get(car.get("addressee", ""), ""),
            "pictures": {k: v.get("purpose", "") for k, v in (car.get("pictures") or {}).items()},
            "sources": car.get("sources", []), "rights": sorted({known[k].get("rights_he", "") for k in used if k in known and known[k].get("rights_he")}),
            "lint": issue_dicts([i for i in issues if i.level in ("ERROR", "WARN")]), "render_problems": render_problems,
        })
    out.sort(key=lambda x: (x["slot"], x["option"]))
    return out


def item(key):
    """The item behind a production key "test-2026-11/DATE-OPT"."""
    k = str(key).split("/", 1)[-1]
    return next((i for i in items() if i["id"] == k), None)


def apply_edits(car, edits):
    changes = []
    for e in edits:
        field, value = e.get("field"), str(e.get("value", "")).replace("\r", "")
        n = e.get("slide")
        if n:
            if field not in TEXT_FIELDS:
                raise ValueError(f"field {field} cannot be edited")
            s = car["slides"][int(n) - 1]
            before = s.get(field, "")
            if before != value:
                s[field] = value
                changes.append({"field": field, "slide": int(n), "before": before, "after": value})
        else:
            if field not in TOP_FIELDS:
                raise ValueError(f"field {field} cannot be edited")
            before = car.get(field, "")
            if before != value:
                car[field] = value.strip() if field == "comment_word" else value
                changes.append({"field": field, "slide": None, "before": before, "after": value})
    # the CTA lives on the last slide's body and at the caption's end: keep them in step when only the CTA changed
    if any(c["field"] == "cta" for c in changes):
        old = next(c["before"] for c in changes if c["field"] == "cta")
        cap = car.get("caption", "")
        if old and cap.rstrip().endswith(old.strip()) and not any(c["field"] == "caption" for c in changes):
            car["caption"] = cap.rstrip()[: -len(old.strip())] + car["cta"].strip()
    return changes


def save(key, edits, render_png=True):
    """Edits from Carousel Machine: back up, apply, log the voice edits, lint, re-render the draft slides."""
    path = car_path(key)
    car = read(path)
    try:
        changes = apply_edits(car, edits)
    except (ValueError, IndexError) as exc:
        return {"error": str(exc)}
    if not changes:
        return {"changed": 0, "errors": [], "warnings": []}
    vdir = VERSIONS / key
    vdir.mkdir(parents=True, exist_ok=True)
    k = 1
    while (vdir / f"v{k}.json").exists():
        k += 1
    shutil.copy2(path, vdir / f"v{k}.json")
    lib.write_json(path, car)
    records = [{"at": lib.now_local().isoformat(timespec="seconds"), "pack_date": car["date"], "direction": f"test-{car['type']}",
                "option": key, "field": c["field"], "slide": c["slide"], "role": "", "child_gender": None, "addressee": "parents",
                "kind": lib.edit_kind(c["before"], c["after"]), "before": c["before"], "after": c["after"]}
               for c in changes if c["field"] not in ("title", "comment_word")]
    try:
        lib.log_voice_edits(records)
    except Exception:  # noqa: BLE001 - the edit is saved; the voice log is a bonus
        pass
    issues = lint(car, key)
    problems = render(key) if render_png else []
    return {"changed": len(changes), "valid": not any(i.level == "ERROR" for i in issues),
            "errors": [{"path": str(i.path), "message": i.message} for i in issues if i.level == "ERROR"],
            "warnings": [{"path": str(i.path), "message": i.message} for i in issues if i.level == "WARN"],
            "render_problems": problems, "backup": f"versions/{key}/v{k}.json"}


# ---------------------------------------------------------------- production

def produce(key, update, sh):
    """Make the carousel ready to post: its pictures (only those not made yet, inside the budget Yarin approved by pressing
    produce), the final slides, the texts and the ZIP, in runs/KEY. update(**fields) writes productions.json; sh() runs a
    script (producer._sh). Returns the run folder."""
    car = load(key)
    run = RUNS / key
    run.mkdir(parents=True, exist_ok=True)
    jobs = picture_jobs(car)
    b = budget(car)
    if jobs:
        lib.write_json(run / "jobs.json", {"order": list(jobs), "backend": "openai", "max_replacements_per_job": 0, "jobs": jobs,
                                           "about": "Test batch pictures (test_batch.py). Approved by Yarin pressing produce for this carousel, budget below."})
        state_path = run / "state.json"
        state = read(state_path) if state_path.exists() else {"jobs": {}}
        for n in jobs:
            state["jobs"].setdefault(n, {"status": "pending", "attempts": 0, "replacements": 0, "qa": None, "notes": []})
        lib.write_json(state_path, state)
        prepare_refs(key, jobs)
        todo = [n for n in jobs if state["jobs"][n]["status"] != "done" or not made_picture(key, n)]
        if todo:
            update(status="generating", budget_usd=b["budget_usd"], grant={"by": "produce button", "budget_usd": b["budget_usd"],
                                                                            "at": lib.now_local().isoformat(timespec="seconds")})
            code, out = sh([sys.executable, HERE / "openai_generate.py", run, "run", *todo, "--max-usd", b["budget_usd"]], 900, env_shell=True)
            missing = [n for n in jobs if not made_picture(key, n)]
            if missing:
                tail = "\n".join(l for l in out.strip().splitlines()[-6:] if "sk-" not in l and "OPENAI_API_KEY" not in l)
                raise RuntimeError("התמונות לא נוצרו: " + ", ".join(missing) + "\n" + tail)
    update(status="composing")
    final = run / "final"
    if final.exists():
        old = run / "versions" / lib.now_local().strftime("%Y%m%d-%H%M%S")
        old.mkdir(parents=True, exist_ok=True)
        shutil.move(str(final), str(old / "final"))
    final.mkdir(parents=True)
    problems = render(key, out_dir=final)
    (SLIDES / key).mkdir(parents=True, exist_ok=True)   # the drafts show the made pictures too (the PNGs only)
    for png in list(final.glob("[0-9][0-9].png")) + [final / "contact-sheet.png"]:
        if png.exists():
            shutil.copy2(png, SLIDES / key / png.name)
    update(status="exporting")
    day = day_of(car["date"]) or {"time": "20:30"}
    slides = [{"number": i, "headline": plain(s.get("headline") or s.get("yes") or s.get("quote") or ""),
               "body": plain("\n".join(x for x in (s.get("no") and "במקום: " + s["no"], s.get("body"), s.get("why")) if x))}
              for i, s in enumerate(car["slides"], start=1)]
    option = {"id": key, "title": car.get("title", ""), "slides": slides, "caption": car["caption"], "cta": car["cta"],
              "test_type": car["type"]}
    lib.write_json(run / "approved.json", {"date": car["date"], "test_batch": ID, "type": car["type"], "post_time": day["time"],
                                           "option": option, "frozen_at": lib.now_local().isoformat(timespec="seconds")})
    caption = ltr_dates(car["caption"].strip())
    option["caption"] = caption
    lib.write_json(run / "approved.json", {**read(run / "approved.json"), "option": option})
    (final / "caption.txt").write_text(lib.with_disclaimer(caption) + "\n", encoding="utf-8")
    emoji = car.get("emoji") or ""
    lines = caption.split("\n")
    if emoji:
        lines[0] = lines[0] + " " + emoji
    lib.write_json(final / "postiz-text.json", {"caption": "\n".join(lines)})
    fb = run / "facebook"
    fb.mkdir(exist_ok=True)
    (fb / "facebook.txt").write_text(ltr_dates(car["fb_text"].strip()) + "\n\n" + FB_LINK + "\n", encoding="utf-8")
    (final / "alt-text.txt").write_text("\n".join(f'{s["number"]}: {lib.collapse(s["headline"] + " " + s["body"])}' for s in slides) + "\n", encoding="utf-8")
    src = [f"# Sources · {key} · {TYPES[car['type']]['he']}", ""]
    for s in car.get("sources", []):
        src.append(f'- [{s.get("title", "")}]({s.get("url", "")}) · {s.get("publisher", "")} · read {s.get("accessed", "")} · {s.get("supports", "")}')
    known = assets()
    src += ["", "## Pictures", ""]
    for k in sorted({k for s in car["slides"] for k in ([s.get("bg")] + list(s.get("covers") or []) + [s.get("cover")]) if k}):
        a = known.get(k, {})
        src.append(f'- {k}: {a.get("file", "")} · {a.get("from", "")} · {a.get("rights_he", "")}')
    for n in jobs:
        src.append(f"- {n}: made with the OpenAI Images API ({jobs[n]['model']}, low) for this carousel")
    (final / "sources.md").write_text("\n".join(src) + "\n", encoding="utf-8")
    zip_path = final / f"{key}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(final.glob("[0-9][0-9].png")):
            z.write(p, f"slides/{p.name}")
        for name in ("caption.txt", "alt-text.txt", "sources.md", "contact-sheet.png"):
            if (final / name).exists():
                z.write(final / name, name)
        z.write(fb / "facebook.txt", "facebook.txt")
    if problems:
        update(warning="בדיקת השקופיות: " + "; ".join(problems[:3]))
    return run


# ---------------------------------------------------------------- command line

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    for name in ("lint", "render"):
        p = sub.add_parser(name)
        p.add_argument("keys", nargs="*")
    sub.add_parser("budget")
    sub.add_parser("batch")
    args = ap.parse_args()
    if args.cmd == "status":
        days = {d["date"]: d for d in plan()["days"]}
        for key in keys():
            car = load(key)
            d = days.get(car["date"], {})
            errs = [i for i in lint(car, key) if i.level == "ERROR"]
            rendered = (SLIDES / key / "01.png").exists()
            print(f'{key}  {car["type"]:6}  {d.get("time", "?"):5}  {len(car["slides"])} slides  '
                  f'{"rendered" if rendered else "not rendered"}  {len(errs)} errors  ${budget(car)["budget_usd"]:.2f}')
    elif args.cmd == "lint":
        bad = 0
        for key in args.keys or keys():
            issues = lint(load(key), key)
            for i in issues:
                print(f"{i.level:5} {i.path}: {i.message}" + (f" «{i.excerpt}»" if getattr(i, "excerpt", "") else ""))
            bad += sum(1 for i in issues if i.level == "ERROR")
        print(f"{bad} errors")
        sys.exit(1 if bad else 0)
    elif args.cmd == "render":
        todo = args.keys or keys()
        for n, key in enumerate(todo, start=1):
            problems = render(key)
            print(f"PROGRESS {n}/{len(todo)} {key}" + (f"  {'; '.join(problems)}" if problems else ""), flush=True)
    elif args.cmd == "batch":
        # the whole batch at once (after the review of 11 Nov 2026): openers used twice, families over 3 slides in a
        # carousel, Nofit's son over 2, adults on a cover
        from collections import Counter, defaultdict
        known = assets()
        openers = defaultdict(list)
        total = Counter()
        bad = 0
        for key in keys():
            car = load(key)
            bgs = [s.get("bg") for s in car["slides"] if s.get("bg")]
            if bgs:
                openers[bgs[0]].append(key)
            fam = Counter(known.get(b, {}).get("family", "?") for b in bgs)
            total.update(fam)
            over = {f: n for f, n in fam.items() if n > 3 and f not in ("store", "?")}
            nofit = fam.get("nofit", 0)
            dup = [b for b, n in Counter(bgs).items() if n > 1]
            adult_cover = bgs and known.get(bgs[0], {}).get("gender") == "adult"
            if over or nofit > 2 or dup or adult_cover:
                bad += 1
                print(f"{key}: " + "; ".join(x for x in (f"over 3: {over}" if over else "", f"nofit {nofit}" if nofit > 2 else "",
                                                          f"repeated {dup}" if dup else "", "adult on the cover" if adult_cover else "") if x))
        for b, ks in openers.items():
            if len(ks) > 1:
                bad += 1
                print(f"opener {b} opens {', '.join(ks)}")
        print("families across the batch:", dict(total.most_common()))
        print(f"{bad} problems")
    elif args.cmd == "budget":
        total = 0.0
        for key in keys():
            b = budget(load(key))
            if b["images"]:
                total += b["budget_usd"]
                print(f'{key}: {b["images"]} pictures, estimate ${b["usd"]:.4f}, budget ${b["budget_usd"]:.2f}')
        print(f"all pictures of the batch together: ${total:.2f} (each carousel only when Yarin produces it)")


if __name__ == "__main__":
    main()
