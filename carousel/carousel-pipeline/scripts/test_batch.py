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
    "say": {"he": "במקום זה, תגידו את זה", "short_he": "במקום זה", "brand": False, "disclaimer": True,
            "about_he": "משפט שהורים אומרים, ומשפט שכדאי לנסות במקומו. בקול של ההורה, בלי מותג.",
            "why_he": "בנוי לשיתוף ולשמירה. במחקר הקרוסלות, קרוסלת ״במקום X תגידו Y״ הייתה מהחזקות בארץ."},
    "how": {"he": "ככה זה עובד", "short_he": "ככה זה עובד", "brand": True, "disclaimer": False,
            "about_he": "השאלות לפני שמזמינים: התצוגה המקדימה, ההקדשה, מה יש בפנים. מסכי האתר וילד אמיתי עם הספר.",
            "why_he": "עונה על החששות שלפני ההזמנה. הריל ששאל ״מפחדים שהספר לא ייראה כמו הילד?״ הגיע לפי 3 עד 8 אנשים."},
    "age": {"he": "מה קורה בגיל", "short_he": "מה קורה בגיל", "brand": False, "disclaimer": True,
            "about_he": "דף לשמירה על גיל אחד: דברים שנראים כמו בעיה וחלק מהגיל. כל נקודה על מקור.",
            "why_he": "בנוי לשמירה. חמש הקרוסלות החזקות של לוטם לרנר הן סדרות לפי גיל."},
    "gift": {"he": "מתנה לחנוכה", "short_he": "מתנה לחנוכה", "brand": True, "disclaimer": False,
             "about_he": "לסבים, לסבתות ולמי שקונה מתנה: למה זו מתנה ששומרים, מה כותבים בהקדשה, עד מתי מזמינים.",
             "why_he": "לפי מטא, 43 מתוך 102 רכישות היו של נשים בנות 45 ומעלה. יום ההזמנה האחרון לחנוכה: 05 / 12."},
    "reveal": {"he": "הרגע שהם רואים את הספר", "short_he": "הרגע שהם רואים", "brand": True, "disclaimer": False,
               "about_he": "ילד אמיתי עם הספר שלו, מהצילומים של היוצרת sapir_ivan_mugatz.",
               "why_he": "הוכחה אמיתית. בתוכנית של הרבעון זה הלב: רגעי פתיחה של ספר."},
}

# the look of each type on the slide (audience content: its own colours, never the page tokens)
THEMES = {
    "say": {"bg": "#FBF5EC", "ink": "#1D1039", "soft": "#5E5470", "accent": "#5B2BD6", "chip": "#ECE5FF",
            "no": "#B4283B", "no_soft": "#FBE4E6", "yes": "#17703F", "yes_soft": "#DFF2E6"},
    "how": {"bg": "#F2EDFF", "ink": "#1D1039", "soft": "#584E72", "accent": "#5B2BD6", "chip": "#FFFFFF"},
    "age": {"bg": "#E9F5F2", "ink": "#12302C", "soft": "#46625D", "accent": "#0D7A6E", "chip": "#FFFFFF"},
    "gift": {"bg": "#FFF6E4", "ink": "#16224D", "soft": "#4E5675", "accent": "#2448B8", "chip": "#FFFFFF", "gold": "#C9954A"},
    "reveal": {"bg": "#FFF0F3", "ink": "#2A1020", "soft": "#6B4A5C", "accent": "#C2306A", "chip": "#FFFFFF"},
}

LAYOUTS = ("cover", "swap", "point", "photo", "covers", "quote", "cta")
TEXT_FIELDS = ("tag", "big", "label", "headline", "body", "no", "yes", "why", "quote", "by")
NUM_FIELD = "num"   # the number disc of a point or swap slide (1 to 9), not text
TOP_FIELDS = ("title", "caption", "cta", "fb_text", "comment_word")
MAX_SLIDES = 10          # Postiz sends at most 10 pictures to an Instagram carousel (30 Oct 2026)
MIN_SLIDES = 6
FB_LINK = "https://lumebook.com/IL/he?utm_source=facebook&utm_medium=social"
BANNED_EXTRA = [   # rules of this project that the carousel validator does not know (memory, 5 to 9 Nov 2026)
    (r"₪|\bשקל|\bמחיר|\bהנח[הת]|\bמבצע|\bדמי משלוח", "no price, discount, sale or delivery cost (the reels rule, kept here)"),
    (r"קוד הנחה|קוד אישי", "never קוד הנחה or קוד אישי"),
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
        prompt = " ".join(x for x in (p["scene"], lib.STYLE, lib.PALETTE, lib.AVOID,
                                       "Keep the faces and the main action inside the middle of the frame; the picture is cropped to 4:5.",
                                       lib.NO_TEXT) if x)
        job = {"mode": "generate", "model": cfg["model"], "input": {**base, "prompt": prompt}, "refs": [],
               "purpose": p.get("purpose", "")}
        job["estimated_cost_usd"] = op.estimate_job(job, cfg)["usd"]
        jobs[name] = job
    return jobs


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
    for i, s in enumerate(slides, start=1):
        p = f"{key}/slide-{i}"
        if s.get("layout") not in LAYOUTS:
            out.append(_issue("ERROR", p, f"layout {s.get('layout')!r} is not one of {LAYOUTS}"))
        for f in TEXT_FIELDS:
            if f in s and s[f]:
                text = plain(s[f])
                if f == "label" and text.strip().isdigit():
                    continue
                out.extend(lib.audience_text_issues(f"{p}/{f}", text, allow_cta=s.get("layout") == "cta"))
                out.extend(extra_issues(f"{p}/{f}", text))
        if NUM_FIELD in s and not (isinstance(s[NUM_FIELD], int) and 1 <= s[NUM_FIELD] <= 9):
            out.append(_issue("ERROR", p, "num is a whole number from 1 to 9"))
        words = sum(len(lib.words(plain(s.get(f, "")))) for f in TEXT_FIELDS)
        limit = 22 if s.get("layout") == "cover" else 48
        if words > limit:
            out.append(_issue("ERROR", p, f"{words} words on the slide (max {limit})"))
        for k in ([s["photo"]] if s.get("photo") else []) + list(s.get("covers") or []) + ([s["cover"]] if s.get("cover") else []):
            if k not in known:
                out.append(_issue("ERROR", p, f"picture {k!r} is not in assets.json"))
            elif not (lib.ROOT / known[k]["file"]).exists():
                out.append(_issue("ERROR", p, f"picture file missing: {known[k]['file']}"))
        if s.get("picture") and s["picture"] not in pics:
            out.append(_issue("ERROR", p, f"picture {s['picture']!r} is not under pictures"))
    word = car.get("comment_word", "")
    out.extend(lib.code_word_issues(f"{key}/comment_word", word))
    cta = car.get("cta", "")
    if not cta.strip():
        out.append(_issue("ERROR", f"{key}/cta", "missing"))
    else:
        out.extend(lib.audience_text_issues(f"{key}/cta", cta, allow_cta=True))
        if f'"{word}"' not in cta or "תכתבו" not in cta and "תכתבי" not in cta or "קישור" not in cta:
            out.append(_issue("ERROR", f"{key}/cta", f'the CTA asks to comment "{word}" for the link: תכתבו "{word}" ... קישור'))
        last = slides[-1] if slides else {}
        if lib.collapse(plain(last.get("body", "")) + " " + plain(last.get("headline", ""))).find(lib.collapse(cta.split("\n")[-1])) < 0:
            out.append(_issue("ERROR", f"{key}/slide-{len(slides)}", "the last slide carries the CTA's last line"))
    cap = car.get("caption", "")
    if not cap.strip():
        out.append(_issue("ERROR", f"{key}/caption", "missing"))
    else:
        out.extend(lib.audience_text_issues(f"{key}/caption", cap, allow_cta=True))
        out.extend(extra_issues(f"{key}/caption", cap))
        if not lib.collapse(cap).endswith(lib.collapse(cta)):
            out.append(_issue("ERROR", f"{key}/caption", "the caption ends with the CTA"))
    fb = car.get("fb_text", "")
    if not fb.strip():
        out.append(_issue("ERROR", f"{key}/fb_text", "missing (Facebook gets its own text, 31 Oct 2026)"))
    else:
        out.extend(lib.audience_text_issues(f"{key}/fb_text", fb, allow_cta=True))
        out.extend(extra_issues(f"{key}/fb_text", fb))
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


def _img(key, base, cls="ph", style=""):
    a = assets().get(key)
    if not a:
        return f'<div class="{cls} missing">חסרה תמונה: {html.escape(str(key))}</div>'
    pos = a.get("position", "50% 30%")
    return f'<div class="{cls}"><img src="{_src(lib.ROOT / a["file"], base)}" alt="" style="object-position:{pos};{style}"></div>'


def _pic(car, name, base, key):
    made = made_picture(key, name)
    if made:
        return f'<div class="ph"><img src="{_src(made, base)}" alt="" style="object-position:50% 40%"></div>'
    p = (car.get("pictures") or {}).get(name, {})
    return f'<div class="ph todo"><span>תמונה שתיווצר בהפקה</span><small>{html.escape(p.get("purpose", ""))}</small></div>'


ARROW = ('<div class="arrow"><svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="2.6" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M11 18l-6-6 6-6"/></svg></div>')
SAVE_ICON = ('<svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round">'
             '<path d="M6 3h12v18l-6-4.5L6 21z"/></svg>')
BUBBLE_ICON = ('<svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round">'
               '<path d="M4 5h16v11H9l-5 4z"/></svg>')


def slide_html(car, s, n, total, base, key):
    t = car["type"]
    lay = s.get("layout", "point")
    parts = [f'<section class="slide l-{lay}" data-n="{n}">']
    if TYPES[t]["brand"] and n == 1:
        parts.append('<div class="brand">לומבוק</div>')
    if s.get("tag"):
        parts.append(f'<div class="tag">{rich(s["tag"])}</div>')
    if lay == "cover":
        if s.get("big"):
            parts.append(f'<div class="big">{rich(s["big"])}</div>')
        parts.append(f'<h1 class="h">{rich(s.get("headline", ""))}</h1>')
        if s.get("body"):
            parts.append(f'<p class="b">{rich(s["body"])}</p>')
        if s.get("no") or s.get("yes"):
            parts.append('<div class="pair">' + (f'<div class="card no"><span class="k">במקום</span><p>{rich(s["no"])}</p></div>' if s.get("no") else "")
                         + (f'<div class="card yes"><span class="k">תנסו</span><p>{rich(s["yes"])}</p></div>' if s.get("yes") else "") + '</div>')
        if s.get("photo"):
            parts.append(_img(s["photo"], base))
        elif s.get("picture"):
            parts.append(_pic(car, s["picture"], base, key))
        elif s.get("covers"):
            parts.append('<div class="covers">' + "".join(_img(c, base, "cv") for c in s["covers"][:3]) + '</div>')
    elif lay == "swap":
        if s.get(NUM_FIELD):
            parts.append(f'<div class="num">{int(s[NUM_FIELD])}</div>')
        if s.get("label"):
            parts.append(f'<div class="label">{rich(s["label"])}</div>')
        parts.append(f'<div class="card no"><span class="k">במקום</span><p>{rich(s.get("no", ""))}</p></div>')
        parts.append(f'<div class="card yes"><span class="k">תנסו</span><p>{rich(s.get("yes", ""))}</p></div>')
        if s.get("why"):
            parts.append(f'<p class="b why">{rich(s["why"])}</p>')
    elif lay == "point":
        if s.get(NUM_FIELD):
            parts.append(f'<div class="num">{int(s[NUM_FIELD])}</div>')
        if s.get("label"):
            parts.append(f'<div class="label">{rich(s["label"])}</div>')
        parts.append(f'<h2 class="h">{rich(s.get("headline", ""))}</h2>')
        if s.get("body"):
            parts.append(f'<p class="b">{rich(s["body"])}</p>')
        if s.get("photo"):
            parts.append(_img(s["photo"], base))
        elif s.get("picture"):
            parts.append(_pic(car, s["picture"], base, key))
    elif lay == "photo":
        if s.get("photo"):
            parts.append(_img(s["photo"], base))
        elif s.get("picture"):
            parts.append(_pic(car, s["picture"], base, key))
        if s.get("label"):
            parts.append(f'<div class="label">{rich(s["label"])}</div>')
        parts.append(f'<h2 class="h">{rich(s.get("headline", ""))}</h2>')
        if s.get("body"):
            parts.append(f'<p class="b">{rich(s["body"])}</p>')
    elif lay == "covers":
        if s.get("label"):
            parts.append(f'<div class="label">{rich(s["label"])}</div>')
        parts.append(f'<h2 class="h">{rich(s.get("headline", ""))}</h2>')
        if s.get("body"):
            parts.append(f'<p class="b">{rich(s["body"])}</p>')
        cv = s.get("covers") or []
        parts.append(f'<div class="covers n{min(len(cv), 4)}">' + "".join(_img(c, base, "cv") for c in cv[:4]) + '</div>')
    elif lay == "quote":
        if s.get("label"):
            parts.append(f'<div class="label">{rich(s["label"])}</div>')
        parts.append(f'<blockquote class="q">{rich(s.get("quote", ""))}</blockquote>')
        if s.get("by"):
            parts.append(f'<div class="by">{rich(s["by"])}</div>')
        if s.get("body"):
            parts.append(f'<p class="b">{rich(s["body"])}</p>')
        if s.get("photo"):
            parts.append(_img(s["photo"], base))
    elif lay == "cta":
        parts.append(f'<h2 class="h">{rich(s.get("headline", ""))}</h2>')
        body = rich(s.get("body", ""))
        word = car.get("comment_word", "")
        if word:
            body = body.replace(html.escape(f'"{word}"'), f'<b class="word">״{html.escape(word)}״</b>').replace(f'&quot;{html.escape(word)}&quot;', f'<b class="word">״{html.escape(word)}״</b>')
        parts.append(f'<p class="b">{body}</p>')
        if s.get("cover"):
            parts.append(_img(s["cover"], base, "book"))
        elif s.get("photo"):
            parts.append(_img(s["photo"], base))
        parts.append(f'<div class="icons"><span>{BUBBLE_ICON}</span><span>{SAVE_ICON}</span></div>')
    if TYPES[t]["disclaimer"] and n > 1:
        parts.append(f'<div class="disc">{html.escape(lib.SLIDE_DISCLAIMER)}</div>')
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
:root{{{v}}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:#ddd}}
body{{width:{W}px;direction:rtl;font-family:"Assistant LB",sans-serif;-webkit-font-smoothing:antialiased}}
.slide{{--k:1;width:{W}px;height:{H}px;position:relative;overflow:hidden;background:var(--bg);color:var(--ink);
  padding:calc(var(--k)*92px) 88px 132px;display:flex;flex-direction:column;align-items:stretch;gap:calc(var(--k)*30px);text-align:center}}
body.one .slide{{display:none}} body.one .slide.on{{display:flex}}
.brand{{position:absolute;top:44px;left:56px;font:900 34px "Heebo LB";color:var(--accent);letter-spacing:.01em}}
.tag{{align-self:center;background:var(--accent);color:#fff;font:700 calc(var(--k)*40px) "Heebo LB";padding:14px 36px;border-radius:999px}}
.label{{align-self:center;background:var(--chip);color:var(--accent);font:700 calc(var(--k)*42px) "Heebo LB";padding:12px 34px;border-radius:999px;
  box-shadow:0 2px 0 rgba(0,0,0,.04)}}
.big{{font:900 calc(var(--k)*260px)/.9 "Heebo LB";color:var(--accent)}}
.h{{margin:0;font:900 calc(var(--k)*104px)/1.08 "Heebo LB";letter-spacing:-.005em;text-wrap:balance}}
.l-cover .h{{font-size:calc(var(--k)*136px);line-height:1.02}}
.l-cta .h{{font-size:calc(var(--k)*88px)}}
.b{{margin:0;font:600 calc(var(--k)*56px)/1.3 "Assistant LB";color:var(--soft);text-wrap:pretty}}
.l-cover .b{{font-size:calc(var(--k)*60px);color:var(--ink)}}
em{{font-style:normal;color:var(--accent)}}
.ph{{flex:1 1 auto;min-height:calc(var(--k)*360px);border-radius:40px;overflow:hidden;position:relative;background:var(--chip);
  box-shadow:0 18px 40px rgba(20,10,40,.16)}}
.ph img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.ph.todo{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;border:4px dashed var(--accent);
  background:var(--chip);box-shadow:none;color:var(--accent);font:700 40px "Heebo LB"}}
.ph.todo small{{font:500 28px "Assistant LB";color:var(--soft);direction:ltr;max-width:80%}}
.missing{{display:flex;align-items:center;justify-content:center;color:#b00;font:700 30px "Heebo LB"}}
.card{{border-radius:40px;padding:calc(var(--k)*40px) 52px calc(var(--k)*48px);text-align:right;position:relative}}
.card .k{{display:inline-block;font:900 calc(var(--k)*40px) "Heebo LB";margin-bottom:calc(var(--k)*12px);padding:4px 20px;border-radius:999px;background:rgba(255,255,255,.7)}}
.card p{{margin:0;font:800 calc(var(--k)*80px)/1.16 "Heebo LB"}}
.card.no{{background:var(--no-soft);color:var(--no)}}
.card.no p{{font-weight:700;opacity:.92;text-decoration:line-through;text-decoration-thickness:4px;text-decoration-color:rgba(180,40,59,.45)}}
.card.yes{{background:var(--yes-soft);color:var(--yes);flex:0 0 auto}}
.l-swap{{justify-content:safe center}}
.why{{font-size:calc(var(--k)*52px);color:var(--ink)}}
.num{{align-self:center;width:calc(var(--k)*120px);height:calc(var(--k)*120px);border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font:900 calc(var(--k)*70px) "Heebo LB";box-shadow:0 10px 24px rgba(20,10,40,.18)}}
.pair{{display:flex;flex-direction:column;gap:calc(var(--k)*22px);margin-top:calc(var(--k)*20px)}}
.pair .card p{{font-size:calc(var(--k)*66px)}}
.l-cover{{justify-content:safe center}}
.l-point{{justify-content:safe center}}
.l-point .ph,.l-quote .ph{{max-height:560px}}
.covers{{display:flex;justify-content:center;align-items:center;gap:30px;flex:1 1 auto;min-height:calc(var(--k)*360px);padding:18px 0}}
.cv{{position:relative;flex:0 0 auto;height:min(100%, 440px);max-width:46%;aspect-ratio:1/1;border-radius:18px;overflow:hidden;background:#fff;
  box-shadow:0 20px 40px rgba(20,10,40,.22),0 0 0 8px #fff}}
.covers.n3 .cv{{height:min(100%, 300px);max-width:31%}} .covers.n4 .cv{{height:min(100%, 230px);max-width:23%}}
.l-covers{{justify-content:safe center}}
.l-covers .covers{{flex:0 0 auto;height:calc(var(--k)*560px)}}
.l-photo .ph{{min-height:calc(var(--k)*640px)}}
.l-cover .ph{{min-height:calc(var(--k)*520px)}}
.covers .cv:nth-child(odd){{transform:rotate(-3deg)}} .covers .cv:nth-child(even){{transform:rotate(3deg)}}
.cv img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.q{{margin:0;font:900 calc(var(--k)*88px)/1.16 "Heebo LB";color:var(--accent)}}
.q::before{{content:"״";display:block;font-size:1.6em;line-height:.6;opacity:.35}}
.by{{font:700 calc(var(--k)*44px) "Heebo LB";color:var(--soft)}}
.l-cta{{justify-content:safe center}}
.word{{display:inline-block;background:var(--accent);color:#fff;border-radius:16px;padding:0 18px;margin:4px 0;font-weight:800}}
.book{{align-self:center;width:calc(var(--k)*520px);aspect-ratio:1/1;position:relative;border-radius:14px;overflow:hidden;transform:rotate(-4deg);
  box-shadow:0 26px 50px rgba(20,10,40,.28),0 0 0 10px #fff}}
.book img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.icons{{display:flex;justify-content:center;gap:26px;color:var(--accent)}}
.icons span{{width:74px;height:74px;border-radius:50%;background:var(--chip);display:flex;align-items:center;justify-content:center}}
.disc{{position:absolute;left:150px;right:88px;bottom:30px;font:500 17px/1.35 "Assistant LB";color:var(--soft);opacity:.75;text-align:right}}
.arrow{{position:absolute;left:52px;bottom:40px;width:72px;height:72px;border-radius:50%;background:var(--accent);color:#fff;display:flex;
  align-items:center;justify-content:center;box-shadow:0 8px 18px rgba(20,10,40,.2)}}
.nw{{white-space:nowrap}}
#report{{display:none}}
"""


FIT_JS = """
(function(){
  const q = new URLSearchParams(location.search), one = q.get('s');
  const slides = [...document.querySelectorAll('.slide')];
  if (one) { document.body.classList.add('one'); slides.forEach(s => s.classList.toggle('on', s.dataset.n === one)); }
  const over = s => { const kids = [...s.children].filter(e => !e.classList.contains('arrow') && !e.classList.contains('disc') && !e.classList.contains('brand'));
    if (!kids.length) return false; const bottom = Math.max(...kids.map(e => e.getBoundingClientRect().bottom)) - s.getBoundingClientRect().top;
    const ph = s.querySelector('.ph,.covers,.book'); const small = ph && ph.getBoundingClientRect().height < (ph.classList.contains('book') ? 200 : ph.classList.contains('covers') ? 260 : 300);
    const top = Math.min(...kids.map(e => e.getBoundingClientRect().top)) - s.getBoundingClientRect().top;
    return bottom > s.clientHeight - 118 || top < 40 || s.scrollHeight > s.clientHeight + 1 || small; };
  const report = [];
  const fit = () => slides.forEach(s => { if (one && s.dataset.n !== one) return; let k = 1; s.style.setProperty('--k', k);
    while (over(s) && k > 0.56) { k = Math.round((k - 0.03) * 100) / 100; s.style.setProperty('--k', k); }
    report.push({n: Number(s.dataset.n), k, fits: !over(s), dir: getComputedStyle(s).direction}); });
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
        used = sorted({k for s in car["slides"] for k in ([s.get("photo")] + list(s.get("covers") or []) + [s.get("cover")]) if k})
        out.append({
            "batch": ID, "key": f"{ID}/{key}", "kind": "test", "id": key, "date": date, "slot": n, "type": car["type"],
            "type_he": t["he"], "topic_he": t["he"], "topic_id": car["type"], "option": car["option"],
            "option_he": OPTION_HE[car["option"]], "title": car.get("title", ""), "angle_he": car.get("angle_he", ""),
            "when_he": when_he(day), "post_time": day["time"], "slot_kind": day["slot"], "weekday_he": weekday_he(date),
            "about_he": t["about_he"], "why_he": t["why_he"], "brand": t["brand"],
            "cover": lib.collapse(plain(car["slides"][0].get("headline", ""))) if car["slides"] else "",
            "headlines": [lib.collapse(plain(s.get("headline") or s.get("yes") or s.get("quote") or "")) for s in car["slides"]],
            "slides": [{"n": i, "layout": s.get("layout"), **{f: s[f] for f in TEXT_FIELDS + (NUM_FIELD,) if f in s},
                        **({"photo": s["photo"]} if s.get("photo") else {}), **({"picture": s["picture"]} if s.get("picture") else {})}
                       for i, s in enumerate(car["slides"], start=1)],
            "images": images, "caption": car.get("caption", ""), "cta": car.get("cta", ""), "fb_text": car.get("fb_text", ""),
            "comment_word": car.get("comment_word", ""), "budget": budget(car),
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
    for k in sorted({k for s in car["slides"] for k in ([s.get("photo")] + list(s.get("covers") or []) + [s.get("cover")]) if k}):
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
