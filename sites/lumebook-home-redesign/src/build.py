#!/usr/bin/env python3
"""LumeBook home redesign (demo, 17 / 11 / 2026).

Writes index.html (the unified home), kids.html, gift-books.html, albums.html and the
dev-only compare.html from one set of components. Run:

    python3 tools/lumebook.py build home-redesign      (or: python3 src/build.py)

Facts (prices, formats, delivery, flows) were read from lumebook.com on 17 / 11 / 2026:
/IL/he (and its FAQPage data), /IL/he/gift-books, /IL/he/albums, /IL/he/books/15 and the
gift sample's input page. Re-read the store before changing any of them.
Store pictures are referenced at their lumebook.com address (one copy, the store's own);
pictures made for this demo live in img/ (README lists their sources).
"""
import html
import json
import pathlib
import re
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent
ROOT = SITE.parent.parent
STORE = "https://lumebook.com"

# ---------------------------------------------------------------- routes (live store)
FLOW = {
    "kids": STORE + "/IL/he/wizard",
    "gift": STORE + "/IL/he/gift-books/create",
    "albums": STORE + "/IL/he/albums/create",
}
PAGE = {"home": "index.html", "kids": "kids.html", "gift": "gift-books.html", "albums": "albums.html"}
LIVE = {  # the live page each demo page stands for
    "home": STORE + "/IL/he", "kids": STORE + "/IL/he", "gift": STORE + "/IL/he/gift-books", "albums": STORE + "/IL/he/albums",
}
LINK = {
    "books_all": STORE + "/IL/he/books/category/bestsellers",
    "book": STORE + "/IL/he/books/{}",
    "gift_sample": STORE + "/adult-books/sample/sample-book.pdf?v=lumebook-brand-v2",
    "gift_input": STORE + "/adult-books/sample/input.html?v=lumebook-brand-v2",
    "contact": STORE + "/adult-books/contact/",
    "tutorials": STORE + "/IL/he/tutorials",
    "privacy": STORE + "/IL/he/privacy-policy",
    "terms": STORE + "/IL/he/terms-of-service",
    "access": STORE + "/IL/he/accessibility",
    "google": "https://www.google.com/search?q=LumeBook+-+%D7%9C%D7%95%D7%9E%D7%99%D7%91%D7%95%D7%A7+Reviews",
    "mail": "mailto:support@LumeBook.com",
}
KIDS_CATEGORIES = [  # slugs read from the store home page links
    ("רבי מכר", "bestsellers"), ("ימי הולדת וחגים", "holidays"), ("גמילה ממוצץ ומחיתולים", "habits"),
    ("אומץ ועצמאות", "courage"), ("למידה ראשונה", "learning"), ("חברות ועבודת צוות", "social"),
]

# ---------------------------------------------------------------- pictures
# key: (src, width, height, alt). Store pictures by address, demo pictures in img/.
A = {
    # kids: the store's own photo-to-cover examples (its home hero), transparent
    "k2": ("/hero/series2-transparent-768.avif", 768, 768, "תמונה של ילד והכריכה שנוצרה ממנה: נווה בארץ הדינוזאורים"),
    "k3": ("/hero/series3-transparent-768.avif", 768, 768, "תמונה של ילד והכריכה שנוצרה ממנה: לביא והמחלצים"),
    "k4": ("/hero/series4-transparent-768.avif", 768, 768, "תמונה של ילדה והכריכה שנוצרה ממנה: נועה והחתלתולים"),
    "k5": ("/hero/series5-transparent-768.avif", 768, 768, "תמונה של ילדה והכריכה שנוצרה ממנה: מיה והחיות"),
    # kids: the store's default covers
    "c15": ("/book_covers/girl/B15_girl.webp", 800, 800, "איור הכריכה של יום הולדת"),
    "c13": ("/book_covers/boy/B13_boy.webp", 800, 800, "איור הכריכה של הלב של יובל"),
    "c29": ("/book_covers/girl/B29_girl.webp", 640, 640, "איור הכריכה של חברים צבעוניים"),
    "c41": ("/book_covers/boy/B41_boy.webp", 640, 640, "איור הכריכה של ביי ביי מוצץ"),
    "c43": ("/book_covers/boy/B43_boy.webp", 640, 640, "איור הכריכה של עדן והחיות החופשיות"),
    "c18": ("/book_covers/girl/B18_girl.webp", 800, 800, "איור הכריכה של מה אהיה מחר?"),
    "c10": ("/book_covers/boy/B10_boy.webp", 800, 800, "איור הכריכה של שלום כיתה א׳"),
    "c23": ("/book_covers/girl/B23_girl.webp", 800, 800, "איור הכריכה של הטורניר הגדול של נוי"),
    "c22": ("/book_covers/boy/B22_boy.webp", 800, 800, "איור הכריכה של המסע של עמית באורווה"),
    "c27": ("/book_covers/girl/B27_girl.webp", 800, 800, "איור הכריכה של לב האומץ של אלי"),
    "c5": ("/book_covers/boy/B5_boy.webp", 800, 800, "איור הכריכה של הגן הקסום של הגדולים"),
    # kids: open-book drawings (illustration of a page, not the store's own interior)
    "k-open": ("../lumebook-partners/img/book-open.webp", 900, 684, "ספר ילדים פתוח: איור של יום הולדת משני הצדדים"),
    "k-story": ("img/kids-open-story-page.webp", 1068, 601, "המחשה של עמוד בספר ילדים: השם של הילדה מודגש בתוך הטקסט"),
    "k-title": ("img/kids-open-title-page.webp", 1068, 601, "המחשה של עמוד השער בספר ילדים, עם השם של הילד"),
    "k-ded": ("img/kids-open-dedication.webp", 1068, 601, "המחשה של עמוד ההקדשה בספר ילדים"),
    # gift books: store photo and the store's sample book (pages rendered from its PDF)
    "g-three": ("/adult-books/three-adult-books-1280.webp", 1280, 853, "שלושה ספרי מתנה לדוגמה על שולחן: אני מכיר קיצור, לא הכנתי כלום, מה אוכלים?"),
    "g-cover": ("img/gift-cover.webp", 640, 895, "הכריכה של ספר הדוגמה רק נעצור לרגע"),
    "g-ded": ("img/gift-dedication.webp", 640, 895, "עמוד ההקדשה בספר הדוגמה: לתמר, לעוד הרבה עצירות בדרך. באהבה, מיכל."),
    "g-contents": ("img/gift-spread-contents.webp", 1200, 839, "שני עמודים מספר הדוגמה: תוכן העניינים ואיור של הגיבורה"),
    "g-chapter": ("img/gift-spread-chapter.webp", 1200, 839, "שני עמודים מספר הדוגמה: פתיחת הפרק רשימות של בוקר בחיפה"),
    "g-photo": ("img/gift-spread-photo.webp", 1200, 839, "שני עמודים מספר הדוגמה: פרק עם תמונה של לחם ועגבניות שנשמרה כמו שהיא"),
    "g-back": ("img/gift-back.webp", 640, 895, "הכריכה האחורית של ספר הדוגמה: יש סיפורים שרק אתם מבינים"),
    # albums: the store's own pictures (illustrative people, see README)
    "a-hands": ("/albums/marketing/hero-album-in-hands.webp", 1254, 1254, "ידיים מחזיקות אלבום פתוח עם תמונות של משפחה בים"),
    "a-hands-800": ("/albums/marketing/hero-album-in-hands-800w.webp", 800, 800, "ידיים מחזיקות אלבום פתוח עם תמונות של משפחה בים"),
    "a-table": ("/albums/marketing/price-album-on-table.webp", 1448, 1086, "אלבום מודפס סגור על שולחן בסלון, ליד כוס קפה"),
    "a-unbox": ("/albums/marketing/delivery-unboxing-800w.webp", 800, 800, "אמא ובת פותחות את הקרטון ומוציאות את האלבום המודפס"),
    "a-sofa": ("/albums/marketing/closing-family-sofa.webp", 1448, 1086, "משפחה יושבת על הספה ומדפדפת יחד באלבום"),
    "a-walk": ("/albums/marketing/example-beach-walk-800w.webp", 800, 533, "תמונה מהטלפון: משפחה הולכת על החוף בשקיעה"),
    "a-sand": ("/albums/marketing/example-beach-sandcastle-800w.webp", 800, 800, "תמונה מהטלפון: ילדים בונים ארמון חול"),
    "a-shoulders": ("/albums/marketing/example-beach-shoulders-800w.webp", 800, 1000, "תמונה מהטלפון: ילד על הכתפיים של אבא בים"),
    "a-hug": ("/albums/marketing/example-grandparents-hug-800w.webp", 800, 800, "סבתא מחבקת את הנכדים"),
    "a-crawl": ("/albums/marketing/example-baby-crawling-800w.webp", 800, 533, "תינוקת זוחלת על השטיח"),
    "a-school": ("/albums/marketing/example-year-first-school-day.webp", 1122, 1402, "ילדה עם תיק ביום הראשון ללימודים"),
    "a-present": ("/albums/marketing/example-birthday-present-800w.webp", 800, 800, "ילד פותח מתנת יום הולדת"),
    "a-candles": ("/albums/marketing/example-birthday-candles.webp", 1122, 1402, "עוגת יום הולדת עם נרות"),
    # customers: photos the store already shows on its home page, with its own captions
    "u-sagi": ("/ugc/ugc-sagi-384.webp", 384, 512, "ילדה מחזיקה את הספר שלה", "הספר של שגיא"),
    "u-shaili": ("/ugc/ugc-shaili-rom-384.webp", 384, 683, "ילד במשקפיים מחזיק את הספר שלו", "שי לי ורום דוד"),
    "u-ella": ("/ugc/ugc-ella-story-384.webp", 384, 689, "ילדה מדפדפת בספר שלה", "הסיפור של אלה"),
    "u-lavi": ("/ugc/ugc-lavi-384.webp", 384, 549, "ילד פותח את הקרטון עם הספר", "הספר של לביא"),
    "u-review": ("/ugc/ugc-video-review-384.webp", 384, 683, "אמא וילדה מדפדפות יחד בספר", "יומולדת שנתיים לטרה"),
    "u-ariel": ("/ugc/ugc-ariel-story-384.webp", 384, 683, "הספר של אריאל בידיים", "הסיפור של אריאל"),
    "u-couch": ("/ugc/ugc-couch.webp", 900, 1200, "שני ילדים על הספה מחזיקים ספר פתוח", "אמילי ודויד"),
}

# Public reviews, word for word, from media/projects/2026-11-15-social-proof/data.json (read 17 / 11 / 2026).
# (id, shown name, source label, source link, context in the reviewer's own terms or "", pull quote = an exact part of the text, full text)
GOOGLE_NOTE = "ביקורת בגוגל"
REVIEWS = [
    ("instagram-instagram-DI86Va_i9mS-1", "Miri O.", "תגובה באינסטגרם", "https://www.instagram.com/p/DI86Va_i9mS/", "ספר לנכד",
     "כשנכדי ראה את עצמו באיור בספר, עיניו נצצו מהתרגשות.",
     "כשנכדי ראה את עצמו באיור בספר, עיניו נצצו מהתרגשות. הדמיון היה כל כך מדוייק, שלרגע חשבנו שזו תמונה מצולמת ולא איור."),
    ("google-00", "Hila E.", GOOGLE_NOTE, None, "מתנות יום הולדת לגן",
     "הספרים הגיעו באיכות מאוד טובה, יפה ונעימה לעין!",
     "ביצעתי הזמנה עבור מתנת ימי הולדת לגן שלנו, הספרים הגיעו באיכות מאוד טובה, יפה ונעימה לעין! מתמונה אחת שנשלחההעבור כל ילד הפיקו ספר שלם עם וריאציות שונות של אותה התמונה!! תמורה טובה מעל ומעבר למחיר"),
    ("facebook-rec-2025-11-23", "Hanna L.", "המלצה בפייסבוק", "https://www.facebook.com/profile.php?id=61575235094083&sk=mentions", "שני ספרים לנכדים",
     "איכות הספרים, התמונות, הצבעים וההדפסה ברמה גבוהה מאוד",
     "ממליצה מכל הלב. הזמנתי שני ספרים לשני נכדיי, איכות הספרים, התמונות, הצבעים וההדפסה ברמה גבוהה מאוד, מתנה נפלאה וזיכרון לעולם. שירות מעל ומעבר, משלוח מהיר."),
    ("google-21", "Noa H.", GOOGLE_NOTE, None, "",
     "האפשרות הזו לשלב את תמונות הילד בסיפור כל כך מעודד את הילדים לקרוא",
     "חייבת להרים לחבר׳ה האלה!! שירותיים ברמה גבוהה מאוד, האתר עם ממשק נוח לשימוש במהירות ויעילות! האפשרות הזו לשלב את תמונות הילד בסיפור כל כך מעודד את הילדים לקרוא וזה מדהים, גם מבחר הסיפורים מדהים וכתוב בצורה כל כך נגישה. לגמרי אזמין שוב, תודה"),
    ("google-13", "Tamar B.", GOOGLE_NOTE, None, "",
     "שקל מאוד לעצב וכיף מאוד להתעסק בעריכה שלו.",
     "אפילו עוד לפני שקיבלתי את הספר, שקל מאוד לעצב וכיף מאוד להתעסק בעריכה שלו. אני ממליצה מכל הלב. השירות כאן הוא יוצא דופן. אני בהחלט אחזור לרכישות נוספות וגם אמליץ לחברותיי הסבתות והאמהות על הספרים הנפלאים האלה."),
    ("facebook-rec-2026-02-26", "Daniel B.", "המלצה בפייסבוק", "https://www.facebook.com/profile.php?id=61575235094083&sk=mentions", "",
     "מתנה אדירה לילדים",
     "מתנה אדירה לילדים, קל ופשוט לביצוע... ממליצה בחום"),
    ("google-14", "Lea G.", GOOGLE_NOTE, None, "2 ספרים לנכדים",
     "שאפו לכם ותודה על הכל.",
     "הזמנתי 2 ספרים לנכדים שלי, השרות היה מעולה למרות שלא הפסקתי לנדנד להם בגלל שלא ידעתי איך לפעול בקישור ששלחו לי ועם המון סבלנות מצידם הצלחתי לבצע את ההזמנה. שאפו לכם ותודה על הכל."),
    ("google-15", "Micha N.", GOOGLE_NOTE, None, "",
     "אחלה אתר, נוח לשימוש, ברור וידידותי למשתמש",
     "אחלה אתר, נוח לשימוש, ברור וידידותי למשתמש והכי חשוב שירות לקוחות ברמה של vip. עזרו לי (עמית) גם בשעה 22:00 בלילה ולא איזה בוט מעצבן. הקשיבו לבקשות שלי ועשו הכל כדי לעזור לי. תודה רבה!!"),
    ("google-06", "Noa L.", GOOGLE_NOTE, None, "",
     "שירות כזה ממש לא מובן מאליו!",
     "שירות מדהים ואכפתי! באמת מרגישים שאכפת להם מהלקוחות ושהמטרה שלהם היא לעשות הכול כדי שנצא מרוצים. גם כשנוצרה אצלי טעות בהזמנה והייתה סיטואציה קצת מורכבת, הם באו לקראתי, התגמשו ועשו מעל ומעבר כדי למצוא פתרון. שירות כזה ממש לא מובן מאליו! תודה רבה על היחס, הסבלנות והאכפתיות. בהחלט אחזור להזמין שוב! ותודה לעמית על הטיפול ומענה תוך שניות. כייף גדול להיות לקוחות שלכם ואף אמליץ"),
]
for _r in REVIEWS:  # a pull quote must be an exact part of the review
    assert _r[5].rstrip(".!") in _r[6], _r[0]

# ---------------------------------------------------------------- icons (24px, stroke)
# arrow, book, gift, album, truck, eye, upload, sun, moon, star and pen are the identity kit's icons
# (shared/brand/identity-v1/web/icons); the rest are drawn to match (1.65 stroke, round joins).
ICON = {
    "arrow": '<path d="M20 12H4 M10 6l-6 6 6 6"/>',
    "chev": '<path d="M6 9l6 6 6-6"/>',
    "chev-r": '<path d="M9 6l6 6-6 6"/>',
    "chev-l": '<path d="M15 6l-6 6 6 6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "sun": '<path d="M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z M12 1v2 M12 21v2 M1 12h2 M21 12h2 M4 4l2 2 M18 18l2 2 M4 20l2-2 M18 6l2-2"/>',
    "moon": '<path d="M20 15A9 9 0 0 1 9 4 9 9 0 1 0 20 15Z"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>',
    "truck": '<path d="M2 6h12v12H2z M14 10h4l4 5v3h-8 M7 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM21 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0Z"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 018 0v2.5"/>',
    "star": '<polygon points="12.00,2.00 14.65,8.36 21.51,8.91 16.28,13.39 17.88,20.09 12.00,16.50 6.12,20.09 7.72,13.39 2.49,8.91 9.35,8.36"/>',
    "book": '<path d="M3 5q5-2 9 1q4-3 9-1v14q-5-2-9 1q-4-3-9-1V5Zm9 1v14"/>',
    "gift": '<path d="M3 9h18v4H3z M5 13v8h14v-8 M12 9v12 M12 9C4 9 5 2 8 3q4 0 4 6Zm0 0c8 0 7-7 4-6q-4 0-4 6Z"/>',
    "album": '<path d="M5 3h15v18H5z M3 3v18 M8 16l3-4 3 3 2-2 2 3 M15 7h.01"/>',
    "photo": '<rect x="6" y="2.5" width="12" height="19" rx="2.5"/><path d="M10.5 18.5h3"/>',
    "pen": '<path d="M4 16 16 4l4 4L8 20H4v-4ZM14 6l4 4"/>',
    "home": '<path d="M4 11l8-7 8 7v9h-5v-6H9v6H4z"/>',
    "user": '<circle cx="12" cy="8.5" r="3.8"/><path d="M4.5 20c1.2-3.6 4-5.4 7.5-5.4s6.3 1.8 7.5 5.4"/>',
    "logout": '<path d="M14 4h4a2 2 0 012 2v12a2 2 0 01-2 2h-4M10 16l-4-4 4-4M6 12h10"/>',
    "upload": '<path d="M12 16V3 M7 8l5-5 5 5 M4 15v6h16v-6"/>',
}


def icon(name, cls=""):
    filled = name == "star"
    attrs = 'fill="currentColor" stroke="none"' if filled else 'fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round"'
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" {attrs} aria-hidden="true" focusable="false">{ICON[name]}</svg>'


def esc(s):
    return html.escape(s, quote=True)


def src_of(key):
    s = A[key][0]
    return STORE + s if s.startswith("/") else s


def img(key, cls="", lazy=True, alt=None, sizes=None, fetch=None):
    s, w, h, a = A[key][:4]
    alt = a if alt is None else alt
    bits = [f'src="{esc(src_of(key))}"', f'width="{w}"', f'height="{h}"', f'alt="{esc(alt)}"', 'decoding="async"']
    if lazy:
        bits.append('loading="lazy"')
    if fetch:
        bits.append(f'fetchpriority="{fetch}"')
    if sizes:
        bits.append(f'sizes="{sizes}"')
    if cls:
        bits.append(f'class="{cls}"')
    return "<img " + " ".join(bits) + ">"


def flow(cat, label, cls="btn btn-primary", place="", arrow=True):
    a = icon("arrow") if arrow else ""
    return f'<a class="{cls}" href="{FLOW[cat]}" data-flow="{cat}" data-place="{place}"><span class="lbl">{label}</span>{a}</a>'


def store_link(href, label, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{esc(href)}" data-store>{label}</a>'


def price(n):
    return f"{n}&nbsp;₪"


# ---------------------------------------------------------------- categories
CAT = {
    "kids": {
        "label": "ספרי ילדים", "one": "ספר ילדים", "tag": "הילד או הילדה בתפקיד הראשי",
        "thumb": "c15", "icon": "book",
        "cta": "להתחיל ספר ילדים", "more": "עוד על ספרי הילדים",
        "note": f"<b>{price(119)}</b> לספר מודפס, במקום {price(149)}. היצירה והתצוגה המקדימה בחינם, ועותק דיגיטלי במתנה.",
    },
    "gift": {
        "label": "ספרי מתנה", "one": "ספר מתנה", "tag": "סיפור שנכתב על מי שאתם אוהבים",
        "thumb": "g-three", "icon": "gift",
        "cta": "להתחיל ספר מתנה", "more": "עוד על ספרי המתנה",
        "note": f"<b>{price(199)}</b> מחיר השקה, במקום {price(299)}. מספרים עליהם בכמה מילים, ורואים כריכה ופרק ראשון לפני שמשלמים.",
    },
    "albums": {
        "label": "אלבומי תמונות", "one": "אלבום תמונות", "tag": "התמונות שלכם, מעוצבות ומודפסות",
        "thumb": "a-present", "icon": "album",
        "cta": "להכין אלבום", "more": "עוד על האלבומים",
        "note": f"<b>{price(149)}</b> לאלבום של עד 40 עמודים. רואים את האלבום המוכן, ומשלמים רק אחרי שמאשרים.",
    },
}
ORDER = ["gift", "kids", "albums"]  # Yarin, 17 / 11 / 2026: gift books first, then kids books, then albums

# ---------------------------------------------------------------- shared chrome
FONT = "https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;800&display=swap"  # 300 hero intro, 400 body, 500 hero button, 700 headings and buttons, 800 hero headline

BOOT = """document.documentElement.dataset.theme='light';document.documentElement.dataset.dir='both';"""  # Yarin, 17 / 11 / 2026: "only the combined version in light mode"


def logo_symbol():
    """The identity v1 wordmark (outlined Heebo 900) as a symbol, drawn in the theme's text colour."""
    raw = (ROOT / "shared/brand/identity-v1/logos/wordmark-en-primary.svg").read_text(encoding="utf-8")
    inner = re.sub(r"^.*?<svg[^>]*>", "", raw, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner.strip())
    inner = inner.replace('fill="#19151F"', 'fill="currentColor"')
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="lb-logo" viewBox="40 34 876 149">{inner}</symbol></svg>'


def logo(href="index.html", label="לומבוק, לדף הבית"):
    return (f'<a class="logo" href="{href}" aria-label="{label}"><img class="hat" src="img/hat-3d-96.webp" width="110" height="96" alt="">'
            '<svg viewBox="0 0 876 149" aria-hidden="true"><use href="#lb-logo"/></svg></a>')


def head(title, desc, page):
    return f"""<!doctype html>
<html lang="he" dir="rtl" data-dir="both" data-theme="light" translate="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#FBF8F2">
<link rel="canonical" href="{LIVE[page]}">
<script>{BOOT}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONT}">
<link rel="preconnect" href="{STORE}">
<link rel="icon" href="../../shared/brand/identity-v1/web/favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../shared/brand/identity-v1/web/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="../../shared/brand/identity-v1/web/favicon-180.png">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
{logo_symbol()}
<a class="skip" href="#main">דילוג לתוכן</a>
"""


def start_menu():
    items = []
    for c in ORDER:
        d = CAT[c]
        items.append(
            f'<a href="{FLOW[c]}" data-flow="{c}" data-place="header" role="menuitem">{img(d["thumb"], alt="")}'
            f'<div><b>{d["one"]}</b><span>{d["tag"]}</span></div><span class="go">{icon("arrow")}</span></a>'
        )
    return (
        '<div class="start"><button class="btn btn-primary btn-sm" type="button" data-start-toggle aria-haspopup="true" aria-expanded="false" aria-controls="start-pop">'
        '<span>להתחיל<span class="long"> ליצור</span></span>' + icon("chev") + '</button>'
        '<div class="start-pop" id="start-pop" role="menu" aria-label="מה תרצו ליצור?">' + "".join(items) + "</div></div>"
    )


def account_menu():
    return (
        '<div class="acct"><button class="icon-btn acct-btn" type="button" aria-haspopup="true" aria-expanded="false" aria-label="התחברות או הרשמה">'
        + icon("user", "i-user") + '<span class="av" aria-hidden="true"></span></button>'
        '<div class="acct-pop" role="menu" aria-label="החשבון"><div class="who"></div>'
        f'<button type="button" role="menuitem" data-mybooks>{icon("book")}הספרים שלי</button>'
        f'<button type="button" role="menuitem" data-logout>{icon("logout")}התנתקות</button></div></div>'
    )


def header(active):
    nav = []
    for c in ORDER:
        cur = ' aria-current="page"' if active == c else ""
        nav.append(f'<a href="{PAGE[c]}"{cur}>{CAT[c]["label"]}</a>')
    nav.append(f'<a href="{PAGE["home"]}#how">איך זה עובד</a>')
    nav.append(f'<a href="{PAGE["home"] if active == "home" else PAGE[active]}#faq">שאלות</a>')
    return f"""<header class="site-header">
  <div class="wrap hdr">
    {logo()}
    <nav class="nav" aria-label="ראשי">{''.join(nav)}</nav>
    <div class="hdr-end">
      {account_menu()}
      {start_menu()}
      <button class="icon-btn menu-btn" type="button" data-drawer-open aria-controls="drawer" aria-expanded="false" aria-label="תפריט">{icon("menu")}</button>
    </div>
  </div>
</header>
{drawer(active)}
"""


def appearance_seg(label_id):
    return (
        f'<div class="seg" role="group" aria-labelledby="{label_id}">'
        '<button type="button" data-appearance="light" aria-pressed="false">בהיר</button>'
        '<button type="button" data-appearance="dark" aria-pressed="false">כהה</button>'
        '<button type="button" data-appearance="system" aria-pressed="false">לפי המכשיר</button></div>'
    )


def drawer(active):
    cats = "".join(
        f'<a class="cat" href="{PAGE[c]}"{" aria-current=page" if active == c else ""}>{img(CAT[c]["thumb"], alt="")}<div><b>{CAT[c]["label"]}</b><span>{CAT[c]["tag"]}</span></div></a>'
        for c in ORDER
    )
    return f"""<dialog class="drawer" id="drawer" aria-label="תפריט">
  <div class="drawer-in">
    <div class="drawer-top">{logo()}<button class="icon-btn" type="button" data-drawer-close aria-label="סגירת התפריט">{icon("close")}</button></div>
    {cats}
    <div class="links">
      <a href="{PAGE['home']}#how">איך זה עובד</a>
      <a href="{PAGE['home']}#examples">דוגמאות</a>
      <a href="{PAGE['home'] if active == 'home' else PAGE[active]}#faq">שאלות נפוצות</a>
      {store_link(LINK['contact'], 'יצירת קשר')}
    </div>
    <div class="links" id="drawer-acct"></div>
  </div>
</dialog>"""


def footer():
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="ft">
      <div>{logo()}<p class="ft-about">לומבוק מדפיסה ספרי מתנה, ספרי ילדים אישיים ואלבומי תמונות, ושולחת אותם עד הבית.</p></div>
      <div><h4>ספרים</h4><ul>
        <li><a href="{PAGE['gift']}">ספרי מתנה</a></li>
        <li><a href="{PAGE['kids']}">ספרי ילדים</a></li>
        <li><a href="{PAGE['albums']}">אלבומי תמונות</a></li>
        <li>{store_link(LINK['books_all'], 'כל ספרי הילדים')}</li>
      </ul></div>
      <div><h4>עזרה</h4><ul>
        <li><a href="{PAGE['home']}#faq">שאלות נפוצות</a></li>
        <li>{store_link(LINK['tutorials'], 'הדרכות')}</li>
        <li>{store_link(LINK['contact'], 'יצירת קשר')}</li>
        <li><a href="{LINK['mail']}"><span class="ltr">support@LumeBook.com</span></a></li>
      </ul></div>
      <div><h4>מידע</h4><ul>
        <li>{store_link(LINK['privacy'], 'פרטיות')}</li>
        <li>{store_link(LINK['terms'], 'תנאי השירות')}</li>
        <li>{store_link(LINK['access'], 'נגישות')}</li>
      </ul></div>
    </div>
    <div class="ft-bottom">
      <span>© 2026 LumeBook · עיצוב לבדיקה. הכפתורים מובילים לאתר של לומבוק.</span>
    </div>
  </div>
</footer>
{dialogs()}
<script src="assets/site.js" defer></script>
<script src="assets/studio.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- sections
def facts_list(items):
    return '<ul class="facts">' + "".join(f"<li>{icon('check')}<span>{t}</span></li>" for t in items) + "</ul>"


def kids_fan():
    covers = [("c29", -8, "inset-inline-start:6%;top:24%"), ("c41", 7, "inset-inline-end:6%;top:24%"), ("c13", -1, "inset-inline-start:28%;top:12%;z-index:3")]
    return "".join(f'<span class="book" style="--rot:{rot}deg;{pos}">{img(k)}</span>' for k, rot, pos in covers)


def category_rows():
    kids = f"""<article class="cat-row reveal" id="cat-kids" aria-labelledby="cat-kids-h">
  <div class="cat-media fan">{kids_fan()}</div>
  <div class="cat-body">
    <span class="chip brand">{icon('book')} ספרי ילדים</span>
    <h3 id="cat-kids-h">הילד בתפקיד הראשי</h3>
    <p class="who">לילדים בגילאי 1 עד 10. בוחרים סיפור ומעלים תמונה אחת, והילד מופיע בכל האיורים, עם השם שלו בתוך הטקסט.</p>
    {facts_list([
        'סיפורים לרגעים של הילדות: יום הולדת, אח חדש, פרידה מהמוצץ, כיתה א׳ ועוד',
        '22×22 ס״מ, כריכה רכה, 24 עמודים צבעוניים ועמוד הקדשה',
        'בעברית, באנגלית, בערבית או ברוסית',
        'עותק דיגיטלי במתנה בכל הזמנה',
    ])}
    <div class="price-line"><span class="p">{price(119)}</span><s>{price(149)}</s><span class="pn">מחיר לזמן מוגבל. שלושה ספרים עולים {price(347)} וחמישה ספרים {price(545)}, כולל משלוח עד הבית.</span></div>
    <div class="cat-actions">{flow('kids', 'להתחיל ספר ילדים', place='home-row')}<a class="btn-text" href="{PAGE['kids']}">עוד על ספרי הילדים</a></div>
  </div>
</article>"""
    gift = f"""<article class="cat-row reveal" id="cat-gift" aria-labelledby="cat-gift-h">
  <div class="cat-media contain">{img('g-contents')}</div>
  <div class="cat-body">
    <span class="chip brand">{icon('gift')} ספרי מתנה</span>
    <h3 id="cat-gift-h">ספר שנכתב על מישהו שאתם אוהבים</h3>
    <p class="who">ליום הולדת של אמא, לפרישה של אבא, ליום הנישואין של סבא וסבתא, לבני זוג ולחברים. מספרים עליהם בכמה מילים, והסיפור נכתב מהפרטים שלכם.</p>
    {facts_list([
        'לא צריך לדעת לכתוב: עונים במילים פשוטות, ואפשר לדלג על שאלות',
        'כריכה אישית, שם לספר והקדשה בתחילתו',
        'לפני התשלום רואים כריכה, כיוון לפרקים ופרק ראשון',
        'תוספות לבחירה: תמונות ואיורים, עריכת הטקסט, עותק דיגיטלי',
    ])}
    <div class="price-line"><span class="p">{price(199)}</span><s>{price(299)}</s><span class="pn">מחיר השקה לספר המודפס. כל המחירים מוצגים לפני התשלום.</span></div>
    <div class="cat-actions">{flow('gift', 'להתחיל ספר מתנה', place='home-row')}<a class="btn-text" href="{PAGE['gift']}">עוד על ספרי המתנה</a></div>
  </div>
</article>"""
    albums = f"""<article class="cat-row reveal" id="cat-albums" aria-labelledby="cat-albums-h">
  <div class="cat-media">{img('a-sofa')}</div>
  <div class="cat-body">
    <span class="chip brand">{icon('album')} אלבומי תמונות</span>
    <h3 id="cat-albums-h">אלבום מהתמונות שבטלפון</h3>
    <p class="who">מעלים תמונות או קישור לאלבום. אנחנו בוחרים את הטובות, מסדרים ומעצבים כל עמוד, ואתם רק רואים ומאשרים.</p>
    {facts_list([
        'התמונות המקוריות, בלי שינוי באנשים',
        'עד 40 עמודים, 22×22 ס״מ, כריכה רכה, נייר כרומו 170 גרם',
        'מהטלפון, מהמחשב או מקישור לאלבום בגוגל פוטוס',
        'משלמים רק אחרי שמאשרים את האלבום המוכן',
    ])}
    <div class="price-line"><span class="p">{price(149)}</span><span class="pn">לאלבום, העיצוב כלול. משלוח {price(30)} פעם אחת לכל ההזמנה.</span></div>
    <div class="cat-actions">{flow('albums', 'להכין אלבום', place='home-row')}<a class="btn-text" href="{PAGE['albums']}">עוד על האלבומים</a></div>
  </div>
</article>"""
    return kids, gift, albums


def panel_kids(pid, default="k3", pairs=("k2", "k3", "k4")):
    btns = "".join(
        f'<button class="pair-btn" type="button" aria-pressed="{"true" if k == default else "false"}" data-src="{esc(src_of(k))}" data-alt="{esc(A[k][3])}" data-title="{esc(A[k][3].split(": ")[-1])}" aria-label="{esc(A[k][3].split(": ")[-1])}">{img(k, alt="")}</button>'
        for k in pairs
    )
    return f"""<div class="two" data-pairs>
  <div class="demo-in">
    <h4>מה נותנים</h4>
    <ul class="inputs">
      <li><b>תמונה אחת</b>תמונה ברורה ומוארת של הפנים. תמיד אפשר לנסות תמונה אחרת.</li>
      <li><b>שם, גיל, בן או בת</b>השם מופיע בטקסט, והילד מככב בכל האיורים.</li>
      <li><b>שפת הספר</b>עברית, אנגלית, ערבית או רוסית.</li>
    </ul>
    <p class="small" style="margin:16px 0 8px">עוד דוגמאות</p>
    <div class="pairs" style="grid-template-columns:repeat({len(pairs)},minmax(0,1fr))">{btns}</div>
  </div>
  <div class="demo-out">
    <h4>מהתמונה לכריכה</h4>
    <div class="pair-main">{img(default)}</div>
    <p class="out-note">הכריכה של <b data-pair-caption>{A[default][3].split(': ')[-1]}</b>, מתוך הדוגמאות באתר של לומבוק.</p>
    <figure style="margin:16px 0 0">
      <div class="out-media" style="background:transparent">{img('k-story')}</div>
      <figcaption class="small" style="margin-top:8px">המחשה של עמוד: השם של הילד בתוך הסיפור.</figcaption>
    </figure>
  </div>
</div>"""


def panel_gift():
    return f"""<div class="demo">
  <div class="demo-in">
    <h4>מה סיפרו</h4>
    <ul class="inputs">
      <li><b>על מי הספר</b>תמר, בת 55. חברה טובה כבר שלושים שנה.</li>
      <li><b>כמה מילים עליה</b>״תמר גרה בחיפה ועובדת כספרנית. היא אוהבת הליכות ליד הים, קפה שחור וצילום של דלתות ישנות.״</li>
      <li><b>הקדשה</b>״לתמר, לעוד הרבה עצירות בדרך. באהבה, מיכל.״</li>
    </ul>
    <p class="out-note">מתוך ספר הדוגמה של לומבוק. הדמויות והפרטים בדויים. {store_link(LINK['gift_input'], 'מה בדיוק הוזן')}</p>
  </div>
  <div class="demo-arrow" aria-hidden="true">{icon('arrow')}</div>
  <div class="demo-out">
    <h4>מה יצא</h4>
    <div class="out-media" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;background:transparent">{img('g-cover')}{img('g-ded')}</div>
    <p class="out-note">הכריכה ועמוד ההקדשה של ״רק נעצור לרגע״: עשרה פרקים ו 52 עמודי פנים. {store_link(LINK['gift_sample'], 'לקריאת הספר המלא')}</p>
  </div>
</div>"""


def panel_albums():
    return f"""<div class="demo">
  <div class="demo-in">
    <h4>התמונות מהטלפון</h4>
    <div class="photo-stack">{img('a-walk')}{img('a-sand')}{img('a-shoulders')}</div>
    <p class="out-note" style="margin-top:12px">מעלים הכול, גם תמונות דומות. אנחנו בוחרים את הרגעים החזקים, ותמונות שלא נכנסו נשמרות בצד.</p>
  </div>
  <div class="demo-arrow" aria-hidden="true">{icon('arrow')}</div>
  <div class="demo-out">
    <h4>העמוד באלבום</h4>
    <div class="out-media">{img('a-hands-800')}</div>
    <p class="out-note">תמונות להמחשה מהאתר של לומבוק. האנשים בהן אינם לקוחות.</p>
  </div>
</div>"""


def personal_section(only=None):
    panels = [("gift", "ספר מתנה", panel_gift()), ("kids", "ספר ילדים", panel_kids("pk")), ("albums", "אלבום תמונות", panel_albums())]
    if only:
        p = [x for x in panels if x[0] == only][0]
        return p[2]
    tabs = "".join(
        f'<button class="tab" role="tab" id="tab-{k}" aria-controls="panel-{k}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}" type="button">{lbl}</button>'
        for i, (k, lbl, _) in enumerate(panels)
    )
    bodies = "".join(
        f'<div class="panel" role="tabpanel" id="panel-{k}" aria-labelledby="tab-{k}" tabindex="0"{"" if i == 0 else " hidden"}>{body}</div>'
        for i, (k, lbl, body) in enumerate(panels)
    )
    return f"""<section class="section alt" id="personal" aria-labelledby="personal-h">
  <div class="wrap">
    <div class="head reveal"><div><span class="eyebrow">מה הופך אותם לאישיים</span><h2 class="h2" id="personal-h">מה שאתם נותנים, ומה שיוצא</h2>
      <p class="lead">דוגמה אחת מכל סוג ספר, מתוך האתר של לומבוק.</p></div>
      <div class="tabs" role="tablist" aria-label="סוג הספר">{tabs}</div></div>
    {bodies}
  </div>
</section>"""


def gallery_items(cats=("kids", "gift", "albums")):
    kids = [("c23", "הטורניר הגדול של נוי", 23), ("c22", "המסע של עמית באורווה", 22), ("c27", "לב האומץ של אלי", 27),
            ("c43", "עדן והחיות החופשיות: נפרדים מהטיטולים", 43), ("c18", "מה אהיה מחר?", 18), ("c10", "שלום כיתה א׳", 10)]
    out = []
    if "gift" in cats:
        out.append(("gift", f'<a href="{LINK["gift_sample"]}" data-store><div class="g-media contain">{img("g-back")}</div></a>',
                    f'<span class="chip">ספר מתנה</span><b>{store_link(LINK["gift_sample"], "רק נעצור לרגע: הכריכה האחורית")}</b>'))
        out.append(("gift", f'<a href="{LINK["gift_sample"]}" data-store><div class="g-media contain">{img("g-photo")}</div></a>',
                    f'<span class="chip">ספר מתנה</span><b>{store_link(LINK["gift_sample"], "פרק עם תמונה שלכם, כמו שהיא")}</b>'))
    if "kids" in cats:
        for k, t, bid in kids:
            out.append(("kids", f'<a href="{LINK["book"].format(bid)}" data-store><div class="g-media shelf"><span class="book">{img(k)}</span></div></a>',
                        f'<span class="chip">ספר ילדים</span><b><a href="{LINK["book"].format(bid)}" data-store>{t}</a></b>'))
    if "albums" in cats:
        for k, t in [("a-hug", "עם סבא וסבתא"), ("a-crawl", "אלמה, שנה ראשונה"), ("a-school", "השנה שלנו"), ("a-candles", "יונתן בן 6")]:
            out.append(("albums", f'<div class="g-media">{img(k)}</div>', f'<span class="chip">אלבום תמונות</span><b>{t}</b>'))
    return "".join(f'<figure class="g-item" data-cat="{c}">{m}<figcaption>{cap}</figcaption></figure>' for c, m, cap in out)


def gallery_section():
    filt = "".join(
        f'<button class="filter" type="button" data-cat="{k}" aria-pressed="{"true" if k == "all" else "false"}">{lbl}</button>'
        for k, lbl in [("all", "הכול"), ("gift", "ספרי מתנה"), ("kids", "ספרי ילדים"), ("albums", "אלבומי תמונות")]
    )
    return f"""<section class="section" id="examples" aria-labelledby="examples-h">
  <div class="wrap">
    <div class="head reveal"><div><span class="eyebrow">דוגמאות</span><h2 class="h2" id="examples-h">מכל סוג ספר</h2></div>
      <div class="filters" role="group" aria-label="סינון לפי סוג" data-filter-for="gallery">{filt}</div></div>
    <p id="gallery-status" class="sr-only" aria-live="polite"></p>
    <div class="gallery" id="gallery">{gallery_items()}</div>
    <p class="small illus-note">תמונות האלבומים להמחשה. האנשים בהן אינם לקוחות.</p>
    <div class="g-more">{store_link(LINK['books_all'], 'לכל ספרי הילדים בחנות', 'btn btn-quiet')}{store_link(LINK['gift_sample'], 'לקריאת ספר המתנה לדוגמה', 'btn btn-quiet')}</div>
  </div>
</section>"""


def how_section():
    rows = [  # values in the order kids, gift, albums; shown in ORDER
        ("מה נותנים", ["שם, גיל, בן או בת, שפה, ותמונה ברורה של הפנים", "כמה מילים עליהם, זיכרונות או בדיחות שרק אתם מכירים, ותמונה", "תמונות מהטלפון או קישור לאלבום"]),
        ("מה רואים לפני התשלום", ["תצוגה מקדימה של הספר, בחינם", "כריכה, כיוון לפרקים ופרק ראשון. הספר המלא נכתב אחרי התשלום", "את כל האלבום, עמוד אחרי עמוד. אפשר להחליף תמונות ולערוך כיתובים"]),
        ("הספר", ["22×22 ס״מ, כריכה רכה, 24 עמודים", "ספר מודפס. מספר העמודים לפי אורך הסיפור", "22×22 ס״מ, כריכה רכה, עד 40 עמודים"]),
        ("מחיר", [f"<b>{price(119)}</b> במקום {price(149)}, עותק דיגיטלי במתנה", f"<b>{price(199)}</b> מחיר השקה במקום {price(299)}, ותוספות לבחירה", f"<b>{price(149)}</b>, העיצוב כלול"]),
        ("משלוח", [f"{price(30)} עד הבית, עד 7 ימי עסקים", "לפי ההזמנה, ומוצג לפני התשלום", f"{price(30)} עד הבית, בערך 7 ימי עסקים"]),
    ]
    body = "".join(
        f'<tr><th scope="row">{h}</th>' + "".join(f'<td data-cat="{CAT[c]["label"]}">{dict(zip(("kids", "gift", "albums"), vals))[c]}</td>' for c in ORDER) + "</tr>"
        for h, vals in rows
    )
    return f"""<section class="section alt" id="how" aria-labelledby="how-h">
  <div class="wrap">
    <div class="head reveal"><div><span class="eyebrow">איך מזמינים</span><h2 class="h2" id="how-h">ארבעה צעדים, בכל אחד מהספרים</h2></div></div>
    <ol class="steps reveal">
      <li><b>בוחרים ומספרים</b><p>בוחרים סיפור ומעלים תמונה, מספרים על מי שהספר בשבילו, או מעלים תמונות לאלבום.</p></li>
      <li><b>רואים תצוגה מקדימה</b><p>לפני כל תשלום רואים איך הספר נראה.</p></li>
      <li><b>מאשרים ומשלמים</b><p>בתשלום מאובטח, וכל המחירים מוצגים מראש.</p></li>
      <li><b>מקבלים הביתה</b><p>ספר מודפס עד הבית, ומשלוח אחד לכל מה שמזמינים באותו יום.</p></li>
    </ol>
    <div class="compare-wrap reveal">
      <table class="compare">
        <caption>במה הם שונים</caption>
        <thead><tr><td></td>{''.join(f'<th scope="col">{CAT[c]["label"]}</th>' for c in ORDER)}</tr></thead>
        <tbody>{body}</tbody>
      </table>
    </div>
    <p class="ship-note">מזמינים כמה דברים באותו יום? משלמים משלוח עד הבית פעם אחת, ובהזמנות הבאות של אותו יום בוחרים בדף התשלום ״צירוף למשלוח קודם מהיום״. אפשר גם איסוף עצמי בחינם בירושלים, או נקודת איסוף בראשון לציון בתוספת {price(20)}.</p>
  </div>
</section>"""


def closeup_section():
    def m(cls, key, chips, contain=False):
        ch = "".join(f'<span class="chip">{c}</span>' for c in chips)
        return f'<figure class="m {cls}{" contain" if contain else ""}">{img(key)}<figcaption>{ch}</figcaption></figure>'
    return f"""<section class="section" id="closeup" aria-labelledby="closeup-h">
  <div class="wrap">
    <div class="head reveal"><div><span class="eyebrow">מקרוב</span><h2 class="h2" id="closeup-h">כך הם נראים בידיים</h2>
      <p class="lead">עמודים מבפנים, כריכות, וספרים שכבר הגיעו הביתה.</p></div></div>
    <div class="mosaic reveal">
      {m('m1', 'k-open', ['ספר ילדים', 'המחשה של עמודים'])}
      {m('m2', 'g-chapter', ['ספר מתנה', 'פרק מספר הדוגמה'], True)}
      {m('m3', 'k-title', ['ספר ילדים', 'עמוד השער עם השם'], True)}
      {m('m4', 'u-couch', ['ספר ילדים', 'אצל לקוחות'])}
      {m('m5', 'a-unbox', ['אלבום תמונות', 'להמחשה'])}
      {m('m6', 'k-ded', ['ספר ילדים', 'עמוד ההקדשה'], True)}
    </div>
  </div>
</section>"""


def customers_section(title="ספרים שכבר הגיעו הביתה"):
    tiles = "".join(
        f'<figure><div class="u-media">{img(k)}</div><figcaption>{A[k][4]}</figcaption></figure>'
        for k in ["u-sagi", "u-shaili", "u-ella", "u-lavi", "u-review", "u-ariel"]
    )
    return f"""<section class="section alt" id="customers" aria-labelledby="customers-h">
  <div class="wrap">
    <div class="head reveal"><div><span class="eyebrow">אצל הלקוחות</span><h2 class="h2" id="customers-h">{title}</h2>
      <p class="lead">תמונות של ספרי ילדים ששיתפו משפחות, מתוך האתר של לומבוק.</p></div></div>
    <div class="ugc reveal">{tiles}</div>
  </div>
</section>"""


def reviews_section():
    stars = '<span class="stars" role="img" aria-label="5 כוכבים">' + icon("star") * 5 + "</span>"
    cards = []
    for i, (rid, name, source, url, ctx, pull, text) in enumerate(REVIEWS):
        href = url or LINK["google"]
        meta = f'{esc(ctx)} · ' if ctx else ""
        cards.append(
            f'<li class="rv-card" aria-roledescription="ביקורת" aria-label="{i + 1} מתוך {len(REVIEWS)}"><figure>'
            f'<p class="rv-pull">״{esc(pull)}״</p>{stars}'
            f'<blockquote class="rv-text" id="rv-t-{i}">{esc(text)}</blockquote>'
            f'<button class="rv-more" type="button" aria-expanded="false" aria-controls="rv-t-{i}" hidden>לקריאת כל הביקורת</button>'
            f'<figcaption class="rv-who"><span class="rv-av ltr" aria-hidden="true">{esc(name[0])}</span>'
            f'<div><b class="ltr">{esc(name)}</b><span>{meta}{store_link(href, source)}</span></div></figcaption>'
            f"</figure></li>"
        )
    return f"""<section class="section" id="reviews" aria-labelledby="reviews-h">
  <div class="wrap">
    <div class="rv-head reveal"><span class="eyebrow">ממליצים</span><h2 class="h2" id="reviews-h">מה מספרים עלינו</h2>
      <p class="lead">ביקורות מגוגל, מפייסבוק ומאינסטגרם, מילה במילה.</p></div>
    <div class="rv reveal" data-carousel role="region" aria-roledescription="קרוסלה" aria-labelledby="reviews-h">
      <button class="rv-nav prev" type="button" aria-label="הביקורת הקודמת" aria-controls="rv-track">{icon('chev-r')}</button>
      <ul class="rv-track" id="rv-track" tabindex="0" aria-label="ביקורות">{''.join(cards)}</ul>
      <button class="rv-nav next" type="button" aria-label="הביקורת הבאה" aria-controls="rv-track">{icon('chev-l')}</button>
      <div class="rv-dots" role="group" aria-label="מעבר בין הביקורות"></div>
    </div>
    <p class="rv-all">{store_link(LINK['google'], '4.9 בגוגל: לכל הביקורות')}</p>
  </div>
</section>"""


FAQ = {
    "general": ("כללי", [
        ("מתי משלמים?", "בכל הספרים משלמים אחרי שרואים תצוגה מקדימה. בספרי הילדים היצירה והתצוגה המקדימה בחינם. בספר המתנה רואים כריכה, כיוון לפרקים ופרק ראשון, והספר המלא נכתב אחרי התשלום. באלבום עוברים על כל העמודים ומאשרים להדפסה, ורק אז משלמים."),
        ("כמה עולה המשלוח וכמה זמן הוא לוקח?", f"משלוח עד הבית ברחבי ישראל עולה {price(30)}, פעם אחת לכל מה שמזמינים באותו יום. ספרי ילדים מגיעים עד 7 ימי עסקים, ואלבומים בערך 7 ימי עסקים. אפשר גם איסוף עצמי בחינם בירושלים, או נקודת איסוף בראשון לציון בתוספת {price(20)} (עד 14 ימי עסקים)."),
        ("התשלום מאובטח?", "כן. התשלומים מוצפנים ופרטי הכרטיס לא נשמרים."),
        ("מה קורה עם התמונות שלי?", "משתמשים בהן רק כדי ליצור את הספר או האלבום שלכם, ולא משתפים אותן. באלבומים לא משנים את האנשים בתמונות, ואפשר למחוק את האלבום כל עוד לא הזמנתם."),
    ]),
    "kids": ("ספרי ילדים", [
        ("לאילו גילאים הספרים מתאימים?", "לגילאי 1 עד 10. בדף של כל ספר כתוב לאיזה גיל הוא מתאים."),
        ("השם של הילד מופיע בספר?", "כן. השם מופיע בטקסט, והילד או הילדה מככבים בכל האיורים."),
        ("התמונה לא נראית כמו הילד, מה עושים?", "מעלים תמונה ברורה ומוארת של הפנים. תמיד אפשר לנסות תמונה אחרת."),
        ("יש מחיר מיוחד לכמה ספרים?", f"כן. שלושה ספרים עולים {price(347)} וחמישה ספרים {price(545)}, כולל משלוח מהיר עד הבית. לגנים ולחברות יש מחירים מיוחדים להזמנות קבוצתיות."),
    ]),
    "gift": ("ספרי מתנה", [
        ("הסיפור נכתב במיוחד בשבילנו?", "כן. הסיפור נוצר מהפרטים, הזיכרונות וההנחיות שתשתפו. ככל שתוסיפו פרטים אמיתיים, הספר ירגיש אישי יותר."),
        ("צריך לדעת לכתוב?", "ממש לא. אפשר לענות במילים פשוטות על השאלות, או לתאר רעיון אחד משלכם. שאלות הסיפור גמישות ואפשר לדלג."),
        ("אפשר לערוך ולקבל קובץ דיגיטלי?", f"כן, כתוספות: עריכת כל הפרקים ({price(45)}) ועותק דיגיטלי ({price(25)}). הגישה אליהם נפתחת אחרי אישור התשלום."),
    ]),
    "albums": ("אלבומי תמונות", [
        ("כמה תמונות צריך?", "באלבום עד 40 עמודים, ובכל עמוד תמונה גדולה אחת או כמה תמונות. אפשר לשתף גם אלבום גדול: אנחנו בוחרים את הרגעים החזקים, ושאר התמונות נשמרות בצד. אם יש מעט תמונות, האלבום יהיה קצר יותר, באותו מחיר."),
        ("אפשר לשנות את מה שנבחר?", "כן. מחליפים ומזיזים תמונות, מדייקים חיתוך, עורכים כותרות, תאריכים, מקומות וכיתובים, ובוחרים תמונת כריכה ושם לאלבום."),
        ("אין לי גוגל פוטוס. אפשר להעלות מהאייפון?", "כן. בוחרים תמונות ישירות מהטלפון או מהמחשב, גם תמונות HEIC מאייפון. תמונות שכבר עלו נשמרות גם אם ההעלאה נעצרת."),
    ]),
}


def faq_section(groups=("general", "gift", "kids", "albums"), alt=False):
    plus = icon("plus")
    gs = []
    for g in groups:
        name, items = FAQ[g]
        qs = "".join(f'<details><summary>{q}<span class="plus" aria-hidden="true">{plus}</span></summary><div class="ans"><p>{a}</p></div></details>' for q, a in items)
        gs.append(f'<div class="faq-group"><h3>{name}</h3>{qs}</div>')
    return f"""<section class="section{' alt' if alt else ''}" id="faq" aria-labelledby="faq-h">
  <div class="wrap faq-grid">
    <div class="faq-side"><span class="eyebrow">שאלות</span><h2 class="h2" id="faq-h">שאלות נפוצות</h2>
      <p class="lead" style="margin-top:12px">לא מצאתם תשובה? {store_link(LINK['contact'], 'כתבו לנו')} או במייל <a class="ltr" href="{LINK['mail']}">support@LumeBook.com</a></p></div>
    <div class="faq faq-groups">{''.join(gs)}</div>
  </div>
</section>"""


def final_section(skip=None, title="בוחרים ספר ומתחילים"):
    cards = "".join(
        f'<a class="final-card" href="{FLOW[c]}" data-flow="{c}" data-place="final">{img(CAT[c]["thumb"], alt="")}'
        f'<div><b>{CAT[c]["one"]}</b><span>{CAT[c]["tag"]}</span><span class="go">{CAT[c]["cta"]} {icon("arrow")}</span></div></a>'
        for c in ORDER if c != skip
    )
    return f"""<section class="section final" aria-labelledby="final-h">
  <div class="wrap">
    <h2 class="h2" id="final-h">{title}</h2>
    <p class="lead">רואים תצוגה מקדימה בלי לשלם, ומשלמים רק אחרי שאוהבים את מה שרואים.</p>
    <div class="final-row{' cols-2' if skip else ''}">{cards}</div>
  </div>
</section>"""



# ---------------------------------------------------------------- creation demo and pretend account
STORE_BOOKS = json.loads((SITE / "src/store-books.json").read_text(encoding="utf-8"))["books"]
KIDS_STUDIO = [  # (id, catalogue title, ages as the store lists them, "" when not read)
    (15, "יום הולדת", "3 עד 8"), (13, "הלב של יובל", "4 עד 8"), (29, "חברים צבעוניים", "1 עד 2"), (41, "ביי ביי מוצץ", "2 עד 5"),
    (43, "עדן והחיות החופשיות: נפרדים מהטיטולים", "2 עד 4"), (10, "שלום כיתה א׳", ""), (18, "מה אהיה מחר?", ""),
    (23, "הטורניר הגדול של נוי", ""), (27, "לב האומץ של אלי", ""), (22, "המסע של עמית באורווה", ""), (5, "הגן הקסום של הגדולים", ""),
]


def clean_line(t):
    """Store story text with our punctuation rules: no dash, no hyphen between Hebrew words."""
    t = re.sub(r"\s[-\u2013\u2014]\s", ", ", t)
    t = re.sub(r"(?<=[\u0590-\u05FF])-(?=[\u0590-\u05FF])", " ", t)
    return t


def studio_data():
    books = []
    for bid, title, ages in KIDS_STUDIO:
        pg = STORE_BOOKS[str(bid)]
        books.append({
            "id": bid, "title": title, "ages": ages,
            "cover": {g: f"{STORE}/book_covers/{g}/B{bid}_{g}.webp" for g in ("boy", "girl")},
            "pages": {g: [[clean_line(x) for x in page] for page in pg[g]] for g in ("boy", "girl")},
        })
    am = STORE + "/albums/marketing/"
    data = {
        "flows": FLOW,
        "delivery": [
            {"k": "home", "name": "משלוח מהיר עד הבית", "price": 30, "time": "עד 7 ימי עסקים"},
            {"k": "jlm", "name": "איסוף עצמי בירושלים", "price": 0, "time": "בתיאום מראש, אחרי הודעה שהספר מוכן"},
            {"k": "rishon", "name": "נקודת איסוף בראשון לציון", "price": 20, "time": "עד 14 ימי עסקים"},
        ],
        "kids": {
            "books": books, "ages": list(range(1, 11)), "langs": ["עברית", "אנגלית", "ערבית", "רוסית"],
            "heroImg": src_of("k3"),
            "tiers": [{"n": 1, "price": 119}, {"n": 3, "price": 347, "was": 447}, {"n": 5, "price": 545, "was": 745}],
        },
        "gift": {
            "price": 199, "list": 299, "sample": LINK["gift_sample"], "heroImg": src_of("g-three"), "thumb": src_of("g-cover"),
            "addons": [
                {"k": "pics", "name": "תמונות ואיורים בספר", "price": 49, "desc": "איור אישי לכל פרק, עד עשר תמונות שלכם כתמונות או כאיורים, ועוד 5 איורים חדשים לבחירתכם"},
                {"k": "edit", "name": "עריכת כל הפרקים", "price": 45, "desc": "קריאה ותיקון של הטקסט המלא לפני אישור הספר"},
                {"k": "digital", "name": "עותק דיגיטלי", "price": 25, "desc": "קובץ לקריאה ולהורדה אחרי אישור הספר"},
            ],
            "reasons": ["יום הולדת", "פרישה", "יום נישואין", "אחר"],
            "rels": ["הורה", "סבא או סבתא", "בן או בת זוג", "חבר או חברה", "מהעבודה", "אחר"],
            "traits": ["עם לב גדול", "סקרנים", "מצחיקים", "הרפתקנים", "רגועים", "יצירתיים"],
            "aboutHint": "גרה בחיפה ועובדת כספרנית. אוהבת הליכות ליד הים וקפה שחור.",
            "memoryHint": "פעם יצאנו לטיול בגליל ופספסנו את הפנייה…",
            "dedHint": "לתמר, לעוד הרבה עצירות בדרך. באהבה, מיכל.",
            "chapterHints": ["איך הכול התחיל", "יום רגיל עם {who}", "הרגע שאף אחד לא שכח", "מה שרק אנחנו יודעים", "לעוד הרבה שנים"],
        },
        "albums": {
            "price": 149, "maxPages": 40, "noteHint": "הקיץ שלנו בים. הרבה מהילדים, והשקיעה ביום האחרון",
            "samples": [am + f for f in [
                "example-beach-walk-800w.webp", "example-beach-sandcastle-800w.webp", "example-beach-shoulders-800w.webp",
                "example-grandparents-hug-800w.webp", "example-baby-crawling-800w.webp", "example-year-first-school-day.webp",
                "example-birthday-present-800w.webp", "example-birthday-candles.webp", "example-baby-first-birthday.webp",
                "example-grandparents-reading.webp", "example-grandparents-garden.webp", "example-baby-newborn.webp", "example-birthday-party.webp"]],
        },
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def dialogs():
    x = icon("close")
    tmpl = "".join(f'<template id="ic-{n}">{icon(k)}</template>' for n, k in [("photo", "upload"), ("check", "check"), ("close", "close"), ("chev-r", "chev-r"), ("chev-l", "chev-l")])

    def fld(fid, label, typ, ac, extra=""):
        return (f'<div class="field"><label for="{fid}">{label}</label><input class="inp" id="{fid}" type="{typ}" autocomplete="{ac}" '
                f'aria-describedby="{fid}-err" {extra}><span class="err" id="{fid}-err" aria-live="polite"></span></div>')
    return f"""<dialog class="sheet auth" id="auth" aria-labelledby="auth-h">
  <div class="sheet-top"><h2 id="auth-h">החשבון שלכם</h2><span class="demo-note">דמו</span><button class="icon-btn x" type="button" data-close aria-label="סגירה">{x}</button></div>
  <div class="sheet-body">
    <p class="lead" id="auth-why"></p>
    <div class="tabs" role="tablist" aria-label="הרשמה או התחברות"><button class="tab" type="button" role="tab" data-mode="up" aria-selected="true">הרשמה</button><button class="tab" type="button" role="tab" data-mode="in" aria-selected="false" tabindex="-1">התחברות</button></div>
    <form id="auth-up" novalidate>
      {fld('up-name', 'שם', 'text', 'name', 'dir="rtl" maxlength="40"')}
      {fld('up-email', 'מייל', 'email', 'email', 'dir="ltr" inputmode="email"')}
      {fld('up-pw', 'סיסמה <span class="hint">לפחות 8 תווים</span>', 'password', 'new-password', 'dir="ltr" minlength="8"')}
      <button class="btn btn-primary btn-block" type="submit">יצירת חשבון</button>
    </form>
    <form id="auth-in" novalidate hidden>
      {fld('in-email', 'מייל', 'email', 'email', 'dir="ltr" inputmode="email"')}
      {fld('in-pw', 'סיסמה', 'password', 'current-password', 'dir="ltr"')}
      <button class="btn btn-primary btn-block" type="submit">התחברות</button>
      <button class="btn-text" type="button" id="auth-forgot" style="margin-top:8px">שכחתי סיסמה</button>
    </form>
    <p class="fine">דמו: החשבון נשמר רק בדפדפן הזה ולא נשלח לשום מקום. לא להשתמש כאן בסיסמה אמיתית.</p>
  </div>
</dialog>
<dialog class="sheet mybooks" id="mybooks" aria-labelledby="mb-h">
  <div class="sheet-top"><h2 id="mb-h">הספרים שלי</h2><span class="demo-note">נשמר בדפדפן הזה</span><button class="icon-btn x" type="button" data-close aria-label="סגירה">{x}</button></div>
  <div class="sheet-body" id="mb-list"></div>
</dialog>
<dialog class="sheet studio" id="studio" aria-labelledby="st-title">
  <div class="st-top"><b class="st-title" id="st-title">יצירת ספר</b><div class="st-progress" id="st-progress" aria-hidden="true"></div>
    <span class="st-steplbl" id="st-steplbl" aria-live="polite"></span><span class="demo-note">דמו</span>
    <a class="btn-text" id="st-real" href="{FLOW['kids']}" data-store target="_blank" rel="noopener">באתר האמיתי</a>
    <button class="icon-btn" type="button" data-close aria-label="סגירה">{x}</button></div>
  <div class="st-body" id="st-body"></div>
  <div class="st-foot"><button class="btn btn-quiet" type="button" id="st-back">חזרה</button><span class="sum" id="st-hint" aria-live="polite"></span><span class="grow"></span>
    <button class="btn btn-primary" type="button" id="st-next"><span class="lbl">להמשיך</span>{icon('arrow')}</button></div>
</dialog>
{tmpl}
<script type="application/json" id="studio-data">{studio_data()}</script>"""


# ---------------------------------------------------------------- pages
def home():
    picks = []
    for i, c in enumerate(ORDER):
        d = CAT[c]
        picks.append(
            f'<button class="pick" type="button" role="radio" aria-checked="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}" '
            f'data-cat="{c}" data-href="{FLOW[c]}" data-cta="{d["cta"]}" data-page="{PAGE[c]}" data-more="{d["more"]}">'
            f'<span class="tick">{icon("check")}</span>{img(d["thumb"], alt="", lazy=False)}<b>{d["one"]}</b><span>{d["tag"]}</span>'
            f'<template>{d["note"]}</template></button>'
        )
    kids_row, gift_row, albums_row = category_rows()
    first = CAT["gift"]
    stage = ""  # the product collage was removed (Yarin, 17 / 11 / 2026: "i hate it"); the picker is the hero object
    body = f"""{head('לומבוק: ספרי מתנה, ספרי ילדים ואלבומי תמונות בהתאמה אישית', 'ספר מתנה שנכתב על מי שאתם אוהבים, ספר ילדים שבו הילד הוא הגיבור, או אלבום מהתמונות שבטלפון. רואים תצוגה מקדימה לפני שמשלמים.', 'home')}
{header('home')}
<main id="main">
<section class="hero hero-solo" aria-labelledby="hero-h">
  <div class="wrap hero-grid">
    <div>
      <h1 class="h1" id="hero-h">האנשים שאתם אוהבים,<br class="br-wide"> <em class="mark">בספר מודפס</em></h1>
      <p class="lead">ספר מתנה שנכתב על מי שאתם אוהבים, ספר ילדים שבו הילד הוא הגיבור, או אלבום מהתמונות שבטלפון. בכל אחד רואים תצוגה מקדימה לפני שמשלמים.</p>
      <p class="picker-label" id="picker-h">מה תרצו ליצור?</p>
      <div class="picker" role="radiogroup" aria-labelledby="picker-h">{''.join(picks)}</div>
      <div class="hero-cta">
        <a class="btn btn-primary" id="hero-cta" href="{FLOW['gift']}" data-flow="gift" data-place="hero"><span class="lbl">{first['cta']}</span>{icon('arrow')}</a>
      </div>
      <p class="hero-note" id="hero-note" aria-live="polite">{first['note']}</p>
    </div>
    {stage}
  </div>
</section>

<section class="section tight" id="products" aria-labelledby="products-h">
  <div class="wrap">
    <div class="head reveal"><div><span class="eyebrow">שלושה סוגי ספרים</span><h2 class="h2" id="products-h">לכל אחד, הספר שמתאים לו</h2>
      <p class="lead">לכל ספר דרך יצירה משלו, מחיר משלו ופורמט משלו. הנה במה הם שונים.</p></div></div>
    <div class="cats">{gift_row}{kids_row}{albums_row}</div>
  </div>
</section>

{personal_section()}
{gallery_section()}
{how_section()}
{closeup_section()}
{customers_section()}
{reviews_section()}
{faq_section(alt=True)}
{final_section()}
</main>
{footer()}"""
    return body


def page_hero(cat, eyebrow, h1, lead, media, price_card, media_contain=False):
    d = CAT[cat]
    return f"""<section class="page-hero" aria-labelledby="ph-h">
  <div class="wrap hero-grid">
    <div>
      <p class="crumbs"><a href="{PAGE['home']}">דף הבית</a> ‹ {d['label']}</p>
      <span class="eyebrow">{eyebrow}</span>
      <h1 class="h1" id="ph-h">{h1}</h1>
      <p class="lead" style="margin-top:16px">{lead}</p>
      {price_card}
    </div>
    <div class="ph-media{' contain' if media_contain else ''}">{media}</div>
  </div>
</section>"""


def kids_page():
    pc = f"""<div class="price-card">
  <div class="row"><span><s>{price(149)}</s><span class="p">{price(119)}</span></span><span class="small">ספר מודפס, מחיר לזמן מוגבל</span></div>
  <table class="tiers"><tbody>
    <tr><td>ספר אחד</td><td>{price(119)} ומשלוח {price(30)}</td></tr>
    <tr><td>שלושה ספרים, משלוח כלול</td><td><s>{price(447)}</s> {price(347)}</td></tr>
    <tr><td>חמישה ספרים, משלוח כלול</td><td><s>{price(745)}</s> {price(545)}</td></tr>
  </tbody></table>
  <p class="small">מבצע חנוכה לזמן מוגבל: כל ספר נוסף {price(99)}.</p>
  <div class="hero-cta">{flow('kids', 'להתחיל ספר ילדים', place='kids-hero')}<span class="small">היצירה והתצוגה המקדימה בחינם</span></div>
</div>"""
    cats = "".join(f'<li>{store_link(STORE + "/IL/he/books/category/" + s, n, "chip")}</li>' for n, s in KIDS_CATEGORIES)
    covers = "".join(
        f'<figure class="g-item"><a href="{LINK["book"].format(b)}" data-store><div class="g-media shelf"><span class="book">{img(k)}</span></div></a><figcaption><b>{store_link(LINK["book"].format(b), t)}</b><span class="small">{age}</span></figcaption></figure>'
        for k, t, b, age in [("c15", "יום הולדת", 15, "לגילאי 3 עד 8"), ("c13", "הלב של יובל", 13, "לגילאי 4 עד 8"), ("c29", "חברים צבעוניים", 29, "לגילאי 1 עד 2"),
                             ("c41", "ביי ביי מוצץ", 41, "לגילאי 2 עד 5"), ("c43", "עדן והחיות החופשיות: נפרדים מהטיטולים", 43, "לגילאי 2 עד 4"), ("c23", "הטורניר הגדול של נוי", 23, ""),
                             ("c22", "המסע של עמית באורווה", 22, ""), ("c5", "הגן הקסום של הגדולים", 5, "")]
    )
    return f"""{head('ספרי ילדים בהתאמה אישית | לומבוק', 'ספר מותאם אישית שבו הילד הוא הגיבור: בוחרים סיפור, מעלים תמונה ורואים תצוגה מקדימה בחינם.', 'kids')}
{header('kids')}
<main id="main">
{page_hero('kids', 'ספרי ילדים · לגילאי 1 עד 10', 'הילד שלכם, <em class="mark">גיבור הסיפור</em>',
           'בוחרים סיפור, מעלים תמונה אחת, ורואים תצוגה מקדימה בחינם. אהבתם? מזמינים ספר מודפס, עם עותק דיגיטלי במתנה.',
           img('k4', lazy=False, fetch='high'), pc, media_contain=True)}
<section class="section alt" aria-labelledby="kp-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">מה הופך אותו לאישי</span><h2 class="h2" id="kp-h">תמונה אחת, ספר שלם</h2></div></div>
  {panel_kids('kp', default='k2', pairs=('k2', 'k3', 'k5'))}
</div></section>
<section class="section" aria-labelledby="kb-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">הספרים</span><h2 class="h2" id="kb-h">סיפורים לרגעים של הילדות</h2></div>
    <ul class="filters" style="list-style:none">{cats}</ul></div>
  <div class="gallery">{covers}</div>
  <div class="g-more">{store_link(LINK['books_all'], 'לכל הספרים בחנות', 'btn btn-quiet')}</div>
</div></section>
<section class="section alt" id="how" aria-labelledby="kh-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">איך זה עובד</span><h2 class="h2" id="kh-h">חמש דקות, ארבעה צעדים</h2></div></div>
  <ol class="steps">
    <li><b>בוחרים ספר</b><p>לפי הגיל והרגע: יום הולדת, אח חדש, פרידה מהמוצץ ועוד.</p></li>
    <li><b>מעלים תמונה</b><p>תמונה ברורה ומוארת של הפנים, עם השם, הגיל ושפת הספר.</p></li>
    <li><b>רואים תצוגה מקדימה</b><p>בחינם, לפני שמזמינים.</p></li>
    <li><b>אהבתם? מזמינים</b><p>ספר מודפס עד הבית תוך 7 ימי עסקים, ועותק דיגיטלי במייל תוך דקות.</p></li>
  </ol>
</div></section>
{customers_section('הם כבר קיבלו את הספר שלהם')}
{reviews_section()}
{faq_section(('kids', 'general'), alt=True)}
{final_section(skip='kids', title='יש עוד מישהו ברשימה?')}
</main>
{footer()}"""


def gift_page():
    addons = [("תמונות ואיורים בספר", 49, "איור אישי לכל פרק, עד עשר תמונות שלכם כתמונות או כאיורים, ועוד 5 איורים חדשים לבחירתכם"),
              ("עריכת כל הפרקים", 45, "קריאה ותיקון של הטקסט המלא לפני אישור הספר"),
              ("עותק דיגיטלי", 25, "קובץ לקריאה ולהורדה אחרי אישור הספר")]
    pc = f"""<div class="price-card">
  <div class="row"><span><s>{price(299)}</s><span class="p">{price(199)}</span></span><span class="small">הספר המודפס, מחיר השקה</span></div>
  <ul class="addons">{''.join(f'<li><div><b>{n}</b><br><span>{t}</span></div><b>{price(p)}+</b></li>' for n, p, t in addons)}</ul>
  <div class="hero-cta">{flow('gift', 'להתחיל ספר מתנה', place='gift-hero')}<span class="small">תצוגה מקדימה בחינם, לפני התשלום</span></div>
</div>"""
    return f"""{head('ספרי מתנה אישיים | לומבוק', 'ספר מתנה שנכתב על מי שאתם אוהבים: מספרים עליהם בכמה מילים, ורואים כריכה ופרק ראשון לפני שמזמינים.', 'gift')}
{header('gift')}
<main id="main">
{page_hero('gift', 'ספרי מתנה למבוגרים', 'ספר שנכתב על <em class="mark">מי שאתם אוהבים</em>',
           'ליום הולדת של אמא, לפרישה של אבא או ליום הנישואין של סבא וסבתא. ספר עם הסיפורים והבדיחות שרק אתם מכירים, גם לבני זוג, לחברים ולאנשים מהעבודה.',
           img('g-three', lazy=False, fetch='high'), pc)}
<section class="section alt" aria-labelledby="gp-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">מה הופך אותו לאישי</span><h2 class="h2" id="gp-h">מכמה מילים לספר שלם</h2></div></div>
  {panel_gift()}
</div></section>
<section class="section" aria-labelledby="gi-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">מבפנים</span><h2 class="h2" id="gi-h">עמודים מתוך ספר הדוגמה</h2>
    <p class="lead">הדוגמה מציגה סגנון כתיבה ועיצוב. הספר שלכם ייכתב לפי הפרטים שתשתפו, ומספר העמודים תלוי באורך הסיפור.</p></div>
    {store_link(LINK['gift_sample'], 'לקריאת הספר המלא', 'btn btn-quiet btn-sm')}</div>
  <div class="mosaic">
    <figure class="m m1 contain">{img('g-contents')}<figcaption><span class="chip">תוכן העניינים</span></figcaption></figure>
    <figure class="m m2 contain">{img('g-chapter')}<figcaption><span class="chip">פתיחת פרק</span></figcaption></figure>
    <figure class="m m3 contain">{img('g-photo')}<figcaption><span class="chip">תמונה שלכם, כמו שהיא</span></figcaption></figure>
  </div>
</div></section>
<section class="section alt" id="how" aria-labelledby="gh-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">איך זה עובד</span><h2 class="h2" id="gh-h">שלושה צעדים</h2></div></div>
  <ol class="steps three">
    <li><b>מספרים עליהם</b><p>מספרים למי הספר ומשתפים זיכרונות, הרגלים או בדיחות שרק אתם מכירים.</p></li>
    <li><b>רואים לאן הסיפור הולך</b><p>מקבלים כריכה, כיוון לפרקים ופרק ראשון. בודקים שהסיפור מרגיש נכון לפני שמזמינים.</p></li>
    <li><b>הופכים את זה לספר</b><p>בוחרים את החבילה, משלימים פרטי משלוח ומשלמים. הספר המלא נוצר אחרי אישור התשלום.</p></li>
  </ol>
</div></section>
{faq_section(('gift', 'general'))}
{final_section(skip='gift', title='ואולי גם משהו לילדים?')}
</main>
{footer()}"""


def albums_page():
    pc = f"""<div class="price-card">
  <div class="row"><span class="p">{price(149)}</span><span class="small">לאלבום של עד 40 עמודים, העיצוב כלול</span></div>
  <table class="tiers"><tbody>
    <tr><td>משלוח מהיר עד הבית, בערך 7 ימי עסקים</td><td>{price(30)}</td></tr>
    <tr><td>איסוף עצמי בירושלים</td><td>חינם</td></tr>
    <tr><td>נקודת איסוף בראשון לציון, בערך 14 ימי עסקים</td><td>{price(20)}</td></tr>
  </tbody></table>
  <div class="hero-cta">{flow('albums', 'להכין את האלבום שלי', place='albums-hero')}<span class="small">משלמים רק אחרי שמאשרים</span></div>
</div>"""
    themes = "".join(
        f'<figure class="g-item"><div class="g-media">{img(k)}</div><figcaption><span class="chip ltr">{en}</span><b>{he}</b><span class="small">{sub}</span></figcaption></figure>'
        for k, en, he, sub in [("a-sand", "THE GOOD DAYS", "ימים של חופש", "הטיול שלא רוצים לשכוח"),
                               ("a-school", "OUR YEAR", "השנה שלנו", "שנים עשר חודשים, אלבום אחד"),
                               ("a-crawl", "FIRST YEAR", "אלמה, שנה ראשונה", "מהלידה ועד יום ההולדת הראשון"),
                               ("a-candles", "MAKE A WISH", "יונתן בן 6", "העוגה, החברים וכל מה שביניהם"),
                               ("a-hug", "WITH LOVE", "עם סבא וסבתא", "הנכדים, בעמודים שאפשר לדפדף")]
    )
    keep = [("התמונות המקוריות", "לא מייצרים ולא משנים אנשים. כל תמונה מודפסת כמו שצילמתם, בחיתוך שבחרתם."),
            ("רק מה שבחרתם", "משתמשים רק בתמונות שהעליתם או שבקישור, בלי גישה לשאר הגלריה."),
            ("שום תמונה לא הולכת לאיבוד", "תמונות דומות או כאלה שהסרתם נשמרות בצד, ואפשר להחזיר כל אחת לאלבום."),
            ("נשמר בפרטיות", "האלבום נשמר באופן פרטי, ואפשר למחוק אותו מתי שרוצים, כל עוד לא הזמנתם.")]
    return f"""{head('אלבום תמונות מודפס מהטלפון | לומבוק', 'מעלים תמונות או קישור לאלבום, ואנחנו בוחרים, מסדרים ומעצבים. רואים ומאשרים, ומשלמים רק אחרי האישור.', 'albums')}
{header('albums')}
<main id="main">
{page_hero('albums', 'אלבום תמונות מודפס · 22×22 ס״מ', 'אלבום מודפס <em class="mark">מהתמונות שבטלפון</em>',
           'מעלים תמונות או קישור לאלבום, ואנחנו עושים את השאר: בוחרים את התמונות הטובות ומעצבים כל עמוד. אתם רק רואים ומאשרים.',
           img('a-hands', lazy=False, fetch='high'), pc)}
<section class="section alt" aria-labelledby="ap-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">איך זה נעשה אישי</span><h2 class="h2" id="ap-h">מהגלריה לעמוד מעוצב</h2></div></div>
  {panel_albums()}
</div></section>
<section class="section" aria-labelledby="at-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">אלבומים לדוגמה</span><h2 class="h2" id="at-h">לכל סיפור, עיצוב משלו</h2>
    <p class="lead">400 עיצובים לעמודים, שנבחרים לפי מה שקורה בתמונות.</p></div></div>
  <div class="gallery five">{themes}</div>
  <p class="small illus-note">דוגמאות להמחשה. האנשים בתמונות אינם לקוחות.</p>
</div></section>
<section class="section alt" id="how" aria-labelledby="ah-h"><div class="wrap">
  <div class="head reveal"><div><span class="eyebrow">איך זה עובד</span><h2 class="h2" id="ah-h">שלושה צעדים, וזהו</h2></div></div>
  <ol class="steps three">
    <li><b>מעלים תמונות או קישור</b><p>מהטלפון, מהמחשב או מגוגל פוטוס. לא צריך למיין, אנחנו בוחרים את הטובות.</p></li>
    <li><b>רואים ומאשרים</b><p>האלבום מגיע מוכן ומעוצב. רוצים לשנות משהו? אפשר. משלמים רק אחרי שמאשרים.</p></li>
    <li><b>מקבלים הביתה</b><p>אנחנו מדפיסים ושולחים, בערך 7 ימי עסקים.</p></li>
  </ol>
  <div class="two" style="margin-top:40px">
    <figure class="ph-media" style="margin:0">{img('a-unbox')}</figure>
    <div><h3 class="h3" style="margin-bottom:16px">התמונות שלכם נשארות שלכם</h3>{facts_list([f'<b>{h}.</b> {t}' for h, t in keep])}</div>
  </div>
</div></section>
{faq_section(('albums', 'general'))}
{final_section(skip='albums', title='מזמינים גם ספר? הוא מצטרף לאותו משלוח')}
</main>
{footer()}"""


def compare_page():
    return """<!doctype html>
<html lang="en" dir="ltr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>Compare directions</title>
<style>
:root{color-scheme:light dark}
body{margin:0;font:14px/1.4 ui-sans-serif,system-ui,sans-serif;background:#111;color:#eee}
header{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;gap:12px;align-items:center;padding:10px 14px;background:#000;border-bottom:1px solid #333}
header b{margin-right:8px} select,button{font:inherit;padding:6px 10px;border-radius:8px;border:1px solid #444;background:#1c1c1c;color:#eee}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;padding:14px}
.cell{background:#000;border:1px solid #333;border-radius:10px;overflow:hidden}
.cell h2{margin:0;padding:8px 12px;font-size:13px;font-weight:600;border-bottom:1px solid #333}
.vp{position:relative;overflow:hidden}
iframe{border:0;transform-origin:0 0;display:block;background:#fff}
</style></head>
<body>
<header><b>LumeBook home redesign: versions in light and dark (dev only)</b>
<label>Page <select id="pg"><option value="index.html">Home</option><option value="kids.html">Kids</option><option value="gift-books.html">Gift books</option><option value="albums.html">Albums</option></select></label>
<label>Width <select id="w"><option value="1280">Desktop 1280</option><option value="390">Phone 390</option><option value="768">Tablet 768</option></select></label>
<label>Height <select id="h"><option value="900">900</option><option value="1600">1600</option><option value="3000">3000</option></select></label>
<a href="index.html" style="color:#9cf">open the page</a></header>
<div class="grid" id="g"></div>
<script>
var combos=[['purple','light','Purple tint · light'],['purple','dark','Purple tint · dark'],['yellow','light','Yellow tint · light'],['yellow','dark','Yellow tint · dark'],['both','light','Purple + yellow · light'],['both','dark','Purple + yellow · dark']];
function draw(){var pg=document.getElementById('pg').value,w=+document.getElementById('w').value,h=+document.getElementById('h').value,g=document.getElementById('g');g.innerHTML='';
combos.forEach(function(c){var cell=document.createElement('div');cell.className='cell';cell.innerHTML='<h2>'+c[2]+'</h2><div class="vp"></div>';g.appendChild(cell);
var vp=cell.querySelector('.vp'),f=document.createElement('iframe');f.src=pg+'?dir='+c[0]+'&theme='+c[1];f.width=w;f.height=h;f.title=c[2];f.loading='lazy';vp.appendChild(f);
var s=Math.min(1,vp.clientWidth/w);f.style.transform='scale('+s+')';vp.style.height=(h*s)+'px';});}
['pg','w','h'].forEach(function(id){document.getElementById(id).addEventListener('change',draw)});window.addEventListener('resize',draw);draw();
</script>
</body></html>
"""


# ---------------------------------------------------------------- checks
BANNED = [("—", "em dash"), ("–", "en dash"), ("לומיבוק", "brand spelling"), ("בינה מלאכותית", "AI wording"), ("קוד הנחה", "offer wording")]


def visible_text(doc):
    doc = re.sub(r"<script.*?</script>|<style.*?</style>|<svg.*?</svg>", " ", doc, flags=re.S)
    doc = re.sub(r"<[^>]+>", " ", doc)
    return html.unescape(doc)


def check(name, doc):
    errs = []
    txt = visible_text(doc)
    for s, why in BANNED:
        if s in txt:
            errs.append(f"{name}: {why} ({s!r})")
    if re.search(r"\bAI\b", txt):
        errs.append(f"{name}: mentions AI")
    if re.search(r"[֐-׿][\-־][֐-׿]", txt):
        errs.append(f"{name}: hyphen or maqaf between Hebrew words")
    if re.search(r"[֐-׿][^;\n]{0,3};", txt):
        errs.append(f"{name}: semicolon in Hebrew text")
    for m in re.finditer(r'href="([^"]*)"', doc):
        h = m.group(1)
        if not h or h == "#":
            errs.append(f"{name}: empty link")
    return errs


def main():
    pages = {"index.html": home(), "kids.html": kids_page(), "gift-books.html": gift_page(), "albums.html": albums_page()}
    errs = []
    for n, d in pages.items():
        errs += check(n, d)
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    for n, d in pages.items():
        (SITE / n).write_text(d, encoding="utf-8")
    (SITE / "compare.html").write_text(compare_page(), encoding="utf-8")
    print("wrote", ", ".join(list(pages) + ["compare.html"]))


if __name__ == "__main__":
    main()
