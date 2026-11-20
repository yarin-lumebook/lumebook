#!/usr/bin/env python3
"""The full run of the three story series (20 Nov 2026), after day 1.

Yarin, 20 / 11 / 2026: "i need each day stories for black friday with a distinct design until the 27th, each day hanukkah stories
with a distinct design until the last day of the holiday and a reviews stories that runs until the end of the month", then
"can you add different music for each and url sticker with utm to the books?".

    python3 media/projects/2026-11-19-story-series/make_days.py            # seed every day that has no set yet, songs and link stickers on all
    python3 media/projects/2026-11-19-story-series/make_days.py --force    # also rewrite days that exist (never approved or sent ones)

Every day of a series has its own background (made in Yarin's ChatGPT through Claude in Chrome, art/), its own layout and its own
accent colour. Every frame carries a link sticker with the day's UTM link (books for Black Friday and reviews, the free gift page for
Hanukkah, which Yarin asked to promote on 19 / 11). Every set has its own song: Instagram's music sticker, added in the app with the
link sticker, since the reel music library's songs are commercial and its files are not a licence (its README).
"""
import json
import re
import sys
from datetime import date, timedelta

import make_sets as M
from make_sets import GOLD, SERIES, frame, sticker, stories, text, utm

ROOT = M.ROOT
LIB = ROOT / "media" / "projects" / "2026-11-11-reel-music-library"
ACCENTS = ["#F5C26B", "#FF9BD2", "#7FE3C4", "#9CCBFF", "#FFB37A", "#C9B2FF", "#FFE07A"]
END = {"bf": "2026-11-27", "hanukkah": "2026-12-12", "reviews": "2026-11-30"}


def days(a, b):
    d, e = date.fromisoformat(a), date.fromisoformat(b)
    while d <= e:
        yield d.isoformat()
        d += timedelta(days=1)


def bottom_of(l):
    if l.get("type") == "text":
        lines = str(l.get("text", "")).count("\n") + 1
        per = max(1, int(l.get("w", 900) / (l.get("size", 80) * 0.52)))
        lines = sum(max(1, -(-len(x) // per)) for x in str(l.get("text", "")).split("\n"))
        return l.get("y", 0) + lines * l.get("size", 80) * l.get("lh", 1.1)
    return l.get("y", 0) + l.get("h", 0) if l.get("type") in ("sticker", "shape") else l.get("y", 0) + 300


def ensure_link(fr, link, label):
    """Yarin, 20 / 11 / 2026: a link sticker with the UTM link on every frame."""
    for l in fr["layers"]:
        if l.get("type") == "sticker" and l.get("kind") == "link":
            l["url"], l["label"] = link, label
            return fr
    low = max([bottom_of(l) for l in fr["layers"]] + [1100])
    y = int(min(max(low + 30, 1150), 1490))
    fr["layers"].append(sticker("lk", "link", label, y, h=90, url=link))
    return fr


# ---------------------------------------------------------------- layouts: one per day, so no two days look alike

def lay(kind, kicker, head, foot, acc, foot_size=56):
    hl = dict(accent=acc)
    if kind == "top":
        return [text("l1", kicker, 262, size=60, weight=700, color=acc), text("l2", head, 350, size=108, **hl),
                text("l3", foot, 1330, size=foot_size, weight=700, w=860, x=110)]
    if kind == "low":
        return [text("l1", kicker, 980, size=60, weight=700, color=acc), text("l2", head, 1065, size=104, **hl),
                text("l3", foot, 1330, size=foot_size, weight=700, w=860, x=110)]
    if kind == "card":
        return [{"id": "c0", "type": "shape", "x": 90, "y": 270, "w": 900, "h": 520, "fill": "#FFFFFF", "op": 95, "radius": 48},
                text("l1", kicker, 320, size=56, weight=700, color="#5B2BD6", shadow=False),
                text("l2", head, 410, size=96, color="#2B1A5C", shadow=False, accent="#5B2BD6"),
                text("l3", foot, 1330, size=foot_size, weight=700, w=860, x=110)]
    if kind == "pill":
        return [text("l1", kicker, 290, size=58, weight=700, color="#2B1A5C", pill=acc, pillr=60, pad=22, w=700, x=190, shadow=False),
                text("l2", head, 420, size=96 if "₪" in head else 110, **hl),
                text("l3", foot, 1330, size=foot_size, weight=700, w=860, x=110)]
    if kind == "split":
        return [text("l1", kicker, 262, size=64, weight=900, color=acc), text("l2", head, 1020, size=104, **hl),
                text("l3", foot, 1330, size=foot_size, weight=700, w=860, x=110)]
    raise ValueError(kind)


SCRIM = {"top": {"top": .55, "bottom": .35}, "low": {"top": .2, "bottom": .8}, "card": {"top": 0, "bottom": .5},
         "pill": {"top": .45, "bottom": .4}, "split": {"top": .5, "bottom": .75}}
KINDS = ["top", "low", "card", "pill", "split"]


def hero(fid, art, kind, kicker, head, foot, acc, note, extra=(), under=()):
    return frame(fid, art, list(under) + lay(kind, kicker, head, foot, acc) + list(extra), scrim=SCRIM[kind], note=note)


# ---------------------------------------------------------------- our own media (Yarin, 20 / 11 / 2026: "use our own media as well")
# The reel media library (media/projects/2026-11-11-reel-broll-pool, library.json): LumeBook books drawn by broll.py on a transparent
# 1080 x 1920 ground (the book sits around y 430 to 1230 of the file), the library's pictures, and the mascot from shared/brand.
POOL = "media/projects/2026-11-11-reel-broll-pool/"


def book(name, y=262, w=900):
    return {"id": "m1", "type": "image", "src": POOL + "drawn/" + name, "x": (1080 - w) // 2, "y": y, "w": w}


def pic(name, y=610, w=470):
    return {"id": "m1", "type": "image", "src": POOL + "gpt/" + name, "x": (1080 - w) // 2, "y": y, "w": w, "radius": 40, "shadow": True}


def mascot(y=640, w=420):
    return {"id": "m1", "type": "image", "src": "shared/brand/mascot_3d_transparent.png", "x": (1080 - w) // 2, "y": y, "w": w}


# ---------------------------------------------------------------- Black Friday, by the stages of brief 5 (black-friday.md section 7)

QA = {
    "look": ("זה **מסובך**?", "לא. בוחרים סיפור, מוסיפים\nתמונה של הילד, ובום, יש ספר."),   # Yarin, 20 Nov 2026: the simplicity, never the preview
    "dedic": ("אפשר להוסיף\n**הקדשה**?", "כן, יש עמוד הקדשה."),
    "ship": ("תוך כמה זמן\nזה **מגיע**?", "עד 7 ימי עסקים, עד הבית."),
    "hanuk": ("עד מתי מזמינים\n**לחנוכה**?", "עד 05 / 12."),
}


def qa_frame(fid, art, keys, acc, note):
    ly, y = [{"id": "c0", "type": "shape", "x": 60, "y": 250, "w": 960, "h": 940, "fill": "#000000", "op": 72, "radius": 48},
             text("l1", "שאלות שאתם שואלים", 300, size=66, weight=700, color=acc)], 410
    for i, k in enumerate(keys):
        q, a = QA[k]
        ly += [text(f"q{i}", q, y, size=96, accent=acc), text(f"a{i}", a, y + 230, size=54, weight=700)]
        y += 420
    ly.append(sticker("l9", "question", "תיבת שאלה: מה עוד תרצו לדעת?", 1250, h=170))
    fr = frame(fid, art, ly, scrim={"top": .85, "bottom": .7}, note=note)
    fr["bg"]["fill"] = "#000000"
    return fr


_OCR = {}


def has_thread(rv):
    """An Instagram screenshot that shows replies or an @tag carries other people's names the blur does not cover (seen 20 / 11 / 2026:
    the repliers' usernames and the tagged handles stayed readable). Those are skipped."""
    row = stories.review_by_id(rv["id"]) or {}
    f = M.PROOF / row.get("file", "")
    if f.name not in _OCR:
        _OCR.update(stories.find_names([f]))
    ls = (_OCR.get(f.name) or {}).get("lines") or []
    return any("replies" in l["t"].lower() or "@" in l["t"] for l in ls) or "@" in rv.get("text", "")


def quote_of(t):
    """A long Google review: its first sentence, word for word, when it is 30 to 150 characters (the pull quote has to be readable)."""
    m = re.match(r"\s*(.{30,110}?[.!])(\s|$)", t)
    return m.group(1).strip() if m else ""


def review_pick(used, n, prefer=None):
    out = []
    for rv in sorted(stories.reviews(), key=lambda r: (r["platform"] != (prefer or r["platform"]), -len(r.get("text", "")) if r["platform"] == "google" else 0)):
        if rv["id"] in used or rv.get("platform") == "facebook":
            continue
        t = rv.get("text", "")
        if rv["platform"] == "google" and (len(t) < 40 or int(rv.get("stars") or 0) < 5 or (len(t) > 120 and not quote_of(t))):
            continue
        if rv["platform"] == "instagram" and (not (12 <= len(t) <= 160) or has_thread(rv)):
            continue
        out.append(rv)
        used.add(rv["id"])
        if len(out) == n:
            break
    return out


def review_frames(day, rvs, link, acc, cta_label, first_id=1, header=None):
    rvs = [stories.review_by_id(r["id"]) for r in rvs]          # the data.json rows (with their file)
    found = stories.find_names([M.PROOF / r["file"] for r in rvs if r["platform"] == "instagram"])
    frs = []
    for n, rv in enumerate(rvs, first_id):
        last = n == first_id + len(rvs) - 1
        long = rv["platform"] == "google" and len(rv.get("text", "")) > 120
        fr = M.review_frame(f"f{n}", rv, [quote_of(rv["text"]) + " …"] if long else None, found, cta=last, link=link)
        for l in fr["layers"]:
            if l["id"] == "r1":
                l["color"] = acc
                if header:
                    l["text"] = header
        fr["bg"]["fill"] = ["#2B0E6E", "#1E1050", "#3A0F5E", "#22124A"][n % 4]
        frs.append(fr)
    return frs


# Yarin, 20 / 11 / 2026: "make the black friday ones with a clearly black themes images, utilize real pictures of the product".
# Black and gold backgrounds made in ChatGPT, and the real photos of the books from the test carousels' library
# (carousel/carousel-pipeline/test-batch/2026-11/assets.json; approved by Yarin 11 / 11 / 2026: "we have their approval, use it freely").
# Not the grandma baking book (a real family's names) and not Sapir's clips (reel 1.1 only), per CLAUDE.md.
PHOTOS = "media/projects/2026-11-10-test-carousel-batch/frames/"


def photo_frame(fid, photo, kicker, head, foot, acc, note, extra=(), y=None, head_size=100):
    """A real photo filling the story, the words on a dark fade at the top (the faces stay clear below)."""
    ly = [text("l1", kicker, 262, size=60, weight=700, color=acc), text("l2", head, 345, size=head_size, accent=acc)]
    if foot:
        ly.append(text("l3", foot, 1360, size=54, weight=700, w=860, x=110))
    return {"id": fid, "bg": {"src": PHOTOS + photo, "fill": "#000000", "x": 50, "y": 50 if y is None else y, "zoom": 100},
            "scrim": {"top": .9, "bottom": .75 if foot else .2}, "layers": ly + list(extra), "note": note}


def black(fid, art, kind, kicker, head, foot, acc, note, extra=(), under=()):
    fr = hero(fid, art, kind, kicker, head, foot, acc, note, extra, under)
    fr["bg"]["fill"] = "#000000"
    return fr


def bf_reviews(day, rv, link, acc, first_id, header):
    frs = review_frames(day, rv, link, acc, "", first_id, header)
    for fr in frs:
        fr["bg"].update(src=ART_DIR + "story-bf-black-bags.png", zoom=120, y=80, fill="#000000")
        fr["scrim"] = {"top": .85, "bottom": .6}
    return frs


ART_DIR = "media/projects/2026-11-19-story-series/art/"


def bf_day(day, used):
    link = utm("/books", "bf-2026", day)
    i = list(days("2026-11-20", "2026-11-27")).index(day)
    acc = GOLD if i % 2 == 0 else "#FFE07A"
    price_note = " ⚑ מחיר: רק אם ירין אישר מחיר מחוץ לרילס ורק אם המבצע פעיל בחנות (בריף 5)."
    if day == "2026-11-20":
        return [black("f1", "story-bf-black-cart.png", "top", "עוד שבוע לבלאק פריידיי", "העגלה כבר מלאה\n**בצעצועים**", "מה מכל זה הוא עוד יזכור בעוד שנה?", acc,
                      "פתיח, כוונה 3 ב־black-friday.md."),
                photo_frame("f2", "boy-on-bed-serious-hugging-courage-book-to-chest-1.jpg", "אז מה כן קונים?", "מתנה אחת\nשהוא **ישמור**", "", acc,
                            "תמונה אמיתית של הספר.", [sticker("l4", "poll", "סקר: עוד צעצוע או מתנה אישית?", 1420, h=160)]),
                qa_frame("f3", "story-bf-black-bubbles.png", ["ship", "look"], acc, "שאלות, פריים 5 בבריף 5.")]
    if day == "2026-11-21":
        return [black("f1", "story-bf-black-calendar.png", "top", "עוד 6 ימים", "בלאק פריידיי\nב**לומיבוק**", "כבר קונים מתנות לחנוכה?", acc,
                      "ציפייה, פריים 1 בבריף 5.", [sticker("l4", "poll", "סקר: כבר התחלתי / עוד לא", 1430, h=150)]),
                photo_frame("f2", "girl-on-blue-chair-holding-her-book-cover-up.jpg", "ספר אחד,", "עם **השם שלה**\nעל הכריכה",
                            "בוחרים סיפור, מוסיפים תמונה של הילד", acc, "ציפייה, פריים 2 בבריף 5. תמונה אמיתית.")]
    if day == "2026-11-22":
        rv = review_pick(used, 2, "google")
        return [photo_frame("f1", "covers-fanned-out-different-kids.jpg", "לפני שממלאים עגלה", "כל ספר\n**עם ילד אחר**", "הילד שלכם על הכריכה", acc,
                            "הוכחה. תמונה אמיתית של כריכות.")] + bf_reviews(day, rv, link, acc, 2, "מה כתבו לנו")
    if day == "2026-11-23":
        return [photo_frame("f1", "siblings-on-gray-sofa-reading-own-books-1.jpg", "ככה זה נראה בבית", "כל אחד\n**עם הספר שלו**", "ערב רגיל, והם מבקשים אותו שוב", acc,
                            "הוכחה, פריים 3 בבריף 5. תמונה אמיתית."),
                qa_frame("f2", "story-bf-black-sofa.png", ["look", "dedic"], acc, "שאלות, פריים 5 בבריף 5.")]
    if day == "2026-11-24":
        rv = review_pick(used, 1, "instagram")
        return [qa_frame("f1", "story-bf-black-bubbles.png", ["ship", "hanuk"], acc, "שאלות, פריים 5 בבריף 5. משלוח: store_facts.delivery.")] + \
            bf_reviews(day, rv, link, acc, 2, "מה כתבו לנו השבוע") + \
            [photo_frame("f3", "delivery-bookpod-green-bag-with-book-inside.jpg", "משלוח", "עד **הבית**", "עד 7 ימי עסקים", acc, "תמונה אמיתית של המשלוח.")]
    if day == "2026-11-25":
        row = {"id": "m1", "type": "image", "src": PHOTOS + "print-run-row-of-covers-on-marble.jpg", "x": 110, "y": 720, "w": 860, "radius": 36, "shadow": True}
        return [black("f1", "story-bf-black-tag.png", "pill", "בלאק פריידיי בלומיבוק", "הספר הראשון **119 ₪**\nהספר השני **99 ₪**", "ספר ילדים עם השם והתמונה שלו", acc,
                      "המבצע, פריים 6 בבריף 5." + price_note, under=[row]),
                photo_frame("f2", "print-run-tall-stack-of-books-on-chair.jpg", "מזמינים כמה ספרים באותו יום?", "משלוח עד הבית\nמשלמים **פעם אחת**",
                            "לכל הספרים של אותו יום", acc, "המבצע, פריים 7 בבריף 5. תמונה אמיתית.")]
    if day == "2026-11-26":
        rv = review_pick(used, 1, "google")
        return [photo_frame("f1", "two-girls-on-turf-holding-their-books-up-smiling.jpg", "שני ילדים בבית?", "ספר **לכל אחד**", "הראשון 119 ₪, השני 99 ₪", acc,
                            "המבצע, כוונה 6 בבריף. תמונה אמיתית." + price_note)] + bf_reviews(day, rv, link, acc, 2, "מה כתבו לנו")
    if day == "2026-11-27":
        return [black("f1", "story-bf-black-confetti.png", "pill", "היום בלאק פריידיי", "הספר הראשון **119 ₪**\nהשני **99 ₪**", "רק בלומיבוק, עם השם שלו על הכריכה", acc,
                      "קנייה, פריים 8 בבריף 5." + price_note),
                black("f2", "story-bf-black-calendar.png", "low", "לחנוכה מזמינים", "עד **05 / 12**", "משלוח עד הבית עד 7 ימי עסקים", acc,
                      "קנייה, פריים 9 בבריף 5. ספירה לאחור ל 05 / 12 (תאריך ההזמנה לחנוכה, לא סוף המבצע).",
                      [sticker("l4", "countdown", "ספירה לאחור: 05 / 12, הזמנות לחנוכה", 1430, h=130)]),
                photo_frame("f3", "covers-on-grass-six-different-kids.jpg", "כמה זה פשוט?", "בוחרים סיפור\nמוסיפים תמונה של הילד\nו**בום**, יש ספר", "", acc,
                            "קנייה, פריים 10 בבריף 5. תמונה אמיתית.", head_size=80)]
    raise KeyError(day)


# ---------------------------------------------------------------- Hanukkah: the free gift of https://lumebook.com/IL/he/holiday-cards
# First candle Friday evening 04 / 12 / 2026, last day 12 / 12 (shared/facts.json key dates).
# Yarin, 20 / 11 / 2026: no link sticker (the link is in the bio); say what the gift is and show examples; no candles on a hanukkiah
# before the first night; the steps clear. Every day: f1 the day's hook, f2 what the gift is with an example, f3 how to make it.
# The gift, from the page (read 20 / 11 / 2026): one free gift, either a personal greeting card ("תמונה חגיגית לשמירה ולשיתוף") or a
# personal colouring booklet (five colouring pages as PNG files to print at home) starring the children; one face photo, first name,
# birth month and year; share on WhatsApp; no payment, no credit card.

H = {
    "2026-11-20": ("story-hanukkah-windowsill.png", "עוד שבועיים לנר הראשון", "ברכה לחנוכה\nשהילדים **בתוכה**", "מתנה מאיתנו, בלי תשלום"),
    "2026-11-21": ("story-hanukkah-armchair-phone.png", "לסבא ולסבתא", "ברכה לחנוכה\nעם **הנכדים** בתוכה", "שולחים בוואטסאפ, בחינם"),
    "2026-11-22": ("story-hanukkah-crayons-table.png", "לחופשת חנוכה", "חוברת צביעה\nשהוא **הגיבור** שלה", "חמישה דפים להדפסה בבית"),
    "2026-11-23": ("story-hanukkah-rainy-window.png", "יורד גשם בחוץ?", "דפי צביעה\n**עם הפנים שלו**", "מדפיסים בבית, בחינם"),
    "2026-11-24": ("story-hanukkah-kindergarten-cubbies.png", "לקבוצה של הגן", "ברכה לחנוכה\n**בכיכוב הילדים**", "יוצרים ומשתפים בוואטסאפ"),
    "2026-11-25": ("story-hanukkah-vintage-camera.png", "צריך רק", "**תמונה אחת**\nשל הפנים", "שם, חודש ושנת לידה, וזהו"),
    "2026-11-26": ("story-hanukkah-phone-hearts.png", "ברכה שכולם יענו לה", "שולחים לכל\n**המשפחה**", "כרטיס ברכה אישי, בחינם"),
    "2026-11-27": ("story-hanukkah-candle-calendar.png", "עוד שבוע", "לנר **הראשון**", "ברכה מוכנה מראש, בחינם"),
    "2026-11-28": ("story-hanukkah-home-printer.png", "שבת בבית?", "מדפיסים\n**ומציירים**", "חוברת צביעה אישית, בחינם"),
    "2026-11-29": ("story-hanukkah-paper-plane-city.png", "המשפחה רחוקה?", "ברכה שמגיעה\n**תוך שנייה**", "שולחים בוואטסאפ"),
    "2026-11-30": ("story-hanukkah-gold-envelope.png", "במקום עוד סטיקר", "ברכה עם\n**הפנים שלו**", "מתנה מאיתנו לחנוכה"),
    "2026-12-01": ("story-hanukkah-three-dreidels.png", "עוד 3 ימים", "לנר **הראשון**", "הספקתם להכין ברכה?"),
    "2026-12-02": ("story-hanukkah-craft-box.png", "פעילות לחנוכה", "חמישה דפים\n**רק שלו**", "חוברת צביעה, בחינם"),
    "2026-12-03": ("story-hanukkah-menorah-dusk.png", "מחר בערב", "נר **ראשון**", "הברכה מוכנה? יוצרים עכשיו, בחינם"),
    "2026-12-04": ("story-hanukkah-night-window.png", "הערב", "נר **ראשון**\nחג שמח", "שולחים ברכה עם הפנים שלו"),
    "2026-12-05": ("story-hanukkah-night-sufganiyot.png", "נר שני", "ברכה שעוד\n**לא שלחתם**", "יוצרים בדקה, בחינם"),
    "2026-12-06": ("story-hanukkah-night-latkes.png", "נר שלישי", "לביבות\n**וצביעה**", "חוברת צביעה אישית להדפסה"),
    "2026-12-07": ("story-hanukkah-night-gelt.png", "נר רביעי", "דמי חנוכה?\n**גם ברכה**", "כרטיס אישי, בחינם"),
    "2026-12-08": ("story-hanukkah-night-dreidel-spin.png", "נר חמישי", "חצי חנוכה\n**עבר**", "עוד אפשר לשלוח ברכה"),
    "2026-12-09": ("story-hanukkah-night-balcony.png", "נר שישי", "ברכה לכל\n**הקבוצות**", "גן, משפחה, חברים"),
    "2026-12-10": ("story-hanukkah-night-gift-pile.png", "נר שביעי", "מתנה קטנה\n**שלא עולה כלום**", "כרטיס ברכה או חוברת צביעה"),
    "2026-12-11": ("story-hanukkah-night-all-lights.png", "נר שמיני", "כל **האורות**\nדולקים", "ברכה אחרונה לחג, בחינם"),
    "2026-12-12": ("story-hanukkah-morning-after.png", "היום האחרון של חנוכה", "תודה שחגגתם\n**איתנו**", "חוברת הצביעה נשארת לכל השנה"),
}
EX = "media/projects/2026-11-19-story-series/examples/"
CARDS_EARLY = ["watercolor", "storybook"]                    # no candles behind the child: before the first night
CARDS_ALL = ["hero", "donuts", "miracle", "watercolor", "storybook"]
# Yarin, 20 / 11 / 2026 evening: "instead of ביו write בפרופיל שלנו", "write ללא תשלום או פרטי כרטיס אשראי", and the steps frame
# "clearer with a מתנה חינמית badge and clear step by step": one numbered row per step under a badge.
STEPS = ["נכנסים לקישור בפרופיל שלנו", "בוחרים כרטיס ברכה או חוברת צביעה", "מעלים תמונה אחת של הפנים",
         "כותבים שם, חודש ושנת לידה", "משתפים בוואטסאפ או מדפיסים"]
NO_PAY = "ללא תשלום או פרטי **כרטיס אשראי**"


def gift_frame(day, i, acc, art):
    """What the gift is, with an example: a card from the gift page, or a colouring page made as an example."""
    card = i % 2 == 0
    lit = day >= "2026-12-04"
    if card:
        names = CARDS_ALL if lit else CARDS_EARLY
        n = names[(i // 2) % len(names)]
        src, h = (EX + f"card-{n}-screen.png", 715) if lit else (EX + f"card-{n}-top.png", 455)
        w = 560 if not lit else 360       # the phone (340 x 715) ends above the line under it
        ex = {"id": "m1", "type": "image", "src": src, "x": (1080 - w) // 2, "y": 590, "w": w, "radius": 36, "shadow": True}
        ly = [text("l1", "מה זו המתנה?", 300, size=60, weight=700, color=acc),
              text("l2", "כרטיס ברכה לחנוכה\n**עם הפנים של הילד**", 380, size=84, accent=acc),
              text("l3", "שולחים לסבא, לסבתא ולכל המשפחה", 1380, size=52, weight=700, w=860, x=110)]
        note = "דוגמה מעמוד המתנה (holiday-cards). הדמויות בדוגמה נוצרו להמחשה."
    else:
        k = (i // 2) % 5 + 1      # the real booklet's five pages (Yarin's PDF, 20 / 11 / 2026), cropped above the hanukkiah row and the name
        ex = {"id": "m1", "type": "image", "src": EX + f"coloring-page-{k}.png", "x": 230, "y": 590, "w": 620, "radius": 24, "shadow": True, "bg": "#FFFFFF"}
        ly = [text("l1", "מה זו המתנה?", 300, size=60, weight=700, color=acc),
              text("l2", "חוברת צביעה\n**שהילד הגיבור שלה**", 380, size=84, accent=acc),
              text("l3", "חמישה דפים להדפסה בבית", 1380, size=52, weight=700, w=860, x=110)]
        note = "דף מחוברת צביעה אמיתית שהמתנה מייצרת (ה־PDF של ירין, 20 / 11), חתוך מעל שורת החנוכייה והשם."
    fr = frame("f2", art, [ex] + ly, scrim={"top": .7, "bottom": .7}, note=note)
    fr["bg"].update(zoom=125, y=30)
    return fr


def shape(i, x, y, w, h, fill, op=100, radius=0, **kw):
    return {"id": i, "type": "shape", "x": x, "y": y, "w": w, "h": h, "fill": fill, "op": op, "radius": radius, **kw}


def steps_frame(art, acc):
    """The five steps: a dark panel, a gold-style "מתנה חינמית" badge on its top edge, one row per step with a numbered disc on the
    right (Hebrew reads from the right), and the no payment line under the rows. 23 layers (the editor allows 24)."""
    top, row_h, gap = 560, 108, 18
    ly = [shape("c0", 60, 340, 960, 1000, "#14083C", op=94, radius=56, border=acc, bw=3),
          text("b0", "🎁 מתנה חינמית", 280, size=58, weight=900, color="#1E0B4F", pill=acc, pillr=70, pad=20, w=540, x=270, shadow=False),
          text("l1", "איך יוצרים את המתנה?", 430, size=74, color="#FFFFFF")]
    for n, step in enumerate(STEPS, 1):
        y = top + (n - 1) * (row_h + gap)
        ly += [shape(f"r{n}", 100, y, 880, row_h, "#FFFFFF", op=10, radius=32),
               shape(f"d{n}", 884, y + 16, 76, 76, acc, radius=38),
               text(f"n{n}", str(n), y + 26, size=48, x=884, w=76, color="#1E0B4F", lh=1.15, shadow=False),
               text(f"s{n}", step, y + 27, size=46, weight=700, align="right", lh=1.15, x=130, w=740)]
    ly.append(text("l3", NO_PAY, top + 5 * (row_h + gap) + 40, size=54, accent=acc))
    fr = frame("f3", art, ly, scrim={"top": .3, "bottom": .5},
               note="השלבים לפי עמוד המתנה (נקרא 20 / 11 / 2026). הקישור בפרופיל, בלי מדבקת קישור.")
    fr["bg"].update(zoom=140, y=75)
    return fr


# Yarin, 20 / 11 / 2026 evening: "the image should always refer to the slides text ... where are the kids?". From 21 / 11 every day's
# picture shows what its hook says, children included (made in his ChatGPT through Chrome, 3D animated, faces in the middle band).
# Day 1 (20 / 11) was already up. A day whose picture is not in art/ yet keeps its old one until it arrives.
KIDS = {
    "2026-11-21": "story-hanukkah-kids-grandparents-phone.png", "2026-11-22": "story-hanukkah-kids-hero-coloring.png",
    "2026-11-23": "story-hanukkah-kids-rainy-coloring.png", "2026-11-24": "story-hanukkah-kids-kindergarten.png",
    "2026-11-25": "story-hanukkah-kids-one-photo.png", "2026-11-26": "story-hanukkah-kids-family-hearts.png",
    "2026-11-27": "story-hanukkah-kids-calendar-star.png", "2026-11-28": "story-hanukkah-kids-printer.png",
    "2026-11-29": "story-hanukkah-kids-far-grandparents.png", "2026-11-30": "story-hanukkah-kids-chat-card.png",
    "2026-12-01": "story-hanukkah-kids-three-dreidels.png", "2026-12-02": "story-hanukkah-kids-five-pages.png",
    "2026-12-03": "story-hanukkah-kids-candles-ready.png", "2026-12-04": "story-hanukkah-kids-first-candle.png",
    "2026-12-05": "story-hanukkah-kids-sufganiya-photo.png", "2026-12-06": "story-hanukkah-kids-latkes-coloring.png",
    "2026-12-07": "story-hanukkah-kids-gelt-grandpa.png", "2026-12-08": "story-hanukkah-kids-dreidel-spin.png",
    "2026-12-09": "story-hanukkah-kids-balcony-bubbles.png", "2026-12-10": "story-hanukkah-kids-gift-box-card.png",
    "2026-12-11": "story-hanukkah-kids-all-lights.png", "2026-12-12": "story-hanukkah-kids-pages-on-wall.png",
}
KIDS_KINDS = ["top", "pill"]      # the headline above the children, never across their faces (the white card layout covered heads)
# per picture, after looking at it: 09 / 12 has face bubbles high up, so the picture is pushed down a little under a shorter headline
KIDS_BG = {"2026-12-09": {"zoom": 112, "y": 0}}
KIDS_KIND = {"2026-12-09": "top"}


def hanukkah_day(day, used):
    art, kicker, head, foot = H[day]
    i = list(days("2026-11-20", "2026-12-12")).index(day)
    acc, kind = ACCENTS[i % len(ACCENTS)], KINDS[i % len(KINDS)]
    under = {"2026-12-05": [pic("gpt-sufganiyah-donut-in-sunglasses-reads-a-book-lumebook-book.png", y=620, w=460)],
             "2026-11-21": [mascot()], "2026-12-12": [mascot()]}.get(day, [])
    if under and kind in ("low", "split"):
        kind = "top"                  # the picture needs the middle free
    if day in ("2026-12-01", "2026-12-09", "2026-12-11"):
        kind = "top"                  # the subject fills the middle (dreidels, mug, lit candles): headline above it
    kids = day in KIDS and (M.ROOT / "media/projects/2026-11-19-story-series/art" / KIDS[day]).is_file()
    if kids:
        under, kind = [], KIDS_KIND.get(day, KIDS_KINDS[i % len(KIDS_KINDS)])     # nothing laid over the children
    f1 = hero("f1", KIDS[day] if kids else art, kind, kicker, head, foot, acc,
              "פתיח של היום: התמונה מראה את מה שכתוב. המתנה החינמית בעמוד holiday-cards, הקישור בפרופיל.", under=under)
    countdown = day < "2026-12-04" and day in ("2026-11-20", "2026-11-27", "2026-12-01")
    if kids:
        # the line under the picture goes low, below the children's faces, with a stronger fall-off behind it
        for l in f1["layers"]:
            if l["id"] == "l3":
                l["y"] = FOOT_Y.get(day, 1440 if countdown else 1490)
        f1["scrim"]["bottom"] = max(f1["scrim"]["bottom"], .7)
        f1["bg"].update(KIDS_BG.get(day, {}))
    if countdown:
        f1["layers"].append(sticker("l9", "countdown", "ספירה לאחור: נר ראשון, 04 / 12", 1540 if kids else 1450, h=110 if kids else 120))
    # frames 2 and 3 lay the example and the steps panel over the middle, so they keep the day's people-free picture behind them
    return [f1, gift_frame(day, i, acc, art), steps_frame(art, acc)]


FOOT_Y = {"2026-11-21": 1560, "2026-12-11": 1575}      # per day, after looking at its picture: where the line under the picture sits


def reviews_day(day, used):
    i = list(days("2026-11-21", "2026-11-30")).index(day)
    acc = ACCENTS[i % len(ACCENTS)]
    rvs = review_pick(used, 2, "google") + review_pick(used, 2, "instagram")
    return review_frames(day, rvs, utm("/books", "story-reviews", day), acc, "")


# ---------------------------------------------------------------- songs: a different one for every set

LIB_PICKS = {
    "bf": ["02", "29", "80", "42", "44", "01", "15", "33"],
    "reviews": ["28", "10", "30", "66", "67", "50", "08", "06", "49", "21", "48"],
    "hanukkah": ["09", "26", "54", "83", "47", "87", "79", "23", "94", "27", "75", "05", "78", "88"],
}
WHY = {"bf": "קצבי ושמח, ליום של קניות", "reviews": "חם ורך, מתאים לביקורות", "hanukkah": "רגוע וחמים, ערב חורף בבית"}
# the eight nights: Hanukkah songs every child in Israel knows, to find in Instagram's music library (not checked that each is there)
NIGHT_SONGS = ["באנו חושך לגרש", "סביבון סוב סוב סוב", "נר לי דקיק", "חנוכה חנוכה חג יפה כל כך", "ימי החנוכה", "כד קטן", "מי ימלל", "אנו נושאים לפידים"]


def library_rows():
    rows, sec = {}, None
    for line in (LIB / "README.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"## (\d\d-[\w-]+)", line)
        if m:
            sec = m.group(1)
            continue
        c = [x.strip() for x in line.split("|")]
        if sec and len(c) > 8 and c[1].isdigit():
            rows[c[1]] = {"title": re.sub(r"\s*\((Lyrics|Official[^)]*)\)", "", c[2]).split(" / ")[0].strip(), "start": c[7]}
    return rows


def song_for(ser, n, day):
    if ser == "hanukkah" and "2026-12-04" <= day <= "2026-12-11":
        k = (date.fromisoformat(day) - date(2026, 12, 4)).days
        return {"id": "", "title": NIGHT_SONGS[k], "start": "", "why": f"שיר חנוכה לנר ה{k + 1}. לחפש בספריית המוזיקה של אינסטגרם"}
    picks = LIB_PICKS[ser]
    row = library_rows()[picks[n % len(picks)]]
    return {"id": picks[n % len(picks)], "title": row["title"], "start": row["start"], "why": WHY[ser] + f". לבחור באינסטגרם מ {row['start']}"}


def main():
    force = "--force" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    d = stories.data()
    for ser, end in END.items():
        d["series"][ser]["end"] = end
    stories.save(d)
    used = set()
    for s in d["sets"].values():          # reviews already in a set are never shown again (with --force only day 1 counts)
        if force and s["date"] != d["series"][s["series"]]["start"]:
            continue
        for f in s["frames"]:
            for l in f["layers"]:
                if l.get("type") == "image" and "2026-11-15-social-proof" in str(l.get("src", "")):
                    for rv in stories.reviews():
                        if l["src"].endswith(rv["src"].split("/")[-1]):
                            used.add(rv["id"])
    makers = {"bf": bf_day, "hanukkah": hanukkah_day, "reviews": reviews_day}
    links = {"bf": (lambda day: utm("/books", "bf-2026", day), "מדבקת קישור: הספרים"),
             "hanukkah": None,     # Yarin, 20 / 11 / 2026: "the hannukah free gift does not need a url sticker, ill just add the link in the bio"
             "reviews": (lambda day: utm("/books", "story-reviews", day), "מדבקת קישור: הספרים")}
    wrote, waiting = [], []
    for ser, end in END.items():
        start = d["series"][ser]["start"]
        for n, day in enumerate(days(start, end)):
            key = f"{ser}-{day}"
            old = d["sets"].get(key)
            locked = old and (old.get("approved") or (old.get("postiz") or {}).get("ids"))
            if only and ser not in only:
                continue
            if old and (locked or not force or (day == start and ser == "reviews")):
                frames = old["frames"]          # day 1 stays as it was reviewed; it only gets the link stickers and the song
            else:
                frames = makers[ser](day, used)
            if locked:
                continue
            if links[ser]:
                mk, label = links[ser]
                for fr in frames:
                    ensure_link(fr, mk(day), label)
            else:
                for fr in frames:
                    fr["layers"] = [l for l in fr["layers"] if not (l.get("type") == "sticker" and l.get("kind") == "link")]
            doc = {"series": ser, "date": day, "time": (old or {}).get("time") or SERIES[ser]["time"], "title": "", "channels": ["ig", "fb"],
                   "frames": frames, "notes": (old or {}).get("notes", ""), "music": song_for(ser, n, day)}
            try:
                d["sets"][key] = stories.clean_set(doc, old)
            except ValueError as e:          # its background is not made yet: run again when it is
                waiting.append(f"{key} ({e})")
                continue
            wrote.append(key)
    stories.save(d)
    print(len(wrote), "sets:", ", ".join(wrote))
    if waiting:
        print(len(waiting), "waiting:", "; ".join(waiting))


if __name__ == "__main__":
    sys.exit(main())
