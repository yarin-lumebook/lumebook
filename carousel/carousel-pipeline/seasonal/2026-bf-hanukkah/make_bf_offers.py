"""One-off (20 Nov 2026), kept as a record: wrote the 14 Black Friday offer posts. Do not run it again: it overwrites edits made in the content calendar.
import json
from pathlib import Path

ROOT = Path("/Users/yarinbruner/Claude/Projects/Lumebook")
CARS = ROOT / "carousel/carousel-pipeline/seasonal/2026-bf-hanukkah/carousels"

# day, option, icp (internal), book id, cover key, gender, label, headline, book line for the caption, comment word, tagline noun
POSTS = [
    ("2026-11-21", "a", "הורים לילד עם יום הולדת קרוב", 15, "cover-b15-birthday-boy", "boy",
     "יום הולדת בחודש הבא?", "דמיינו אותו\n**מלך ליום אחד**",
     "בספר הוא מלך ליום אחד: בלונים, עוגה ומשחקים עם חברים.", "מלך", "הילד"),
    ("2026-11-21", "b", "הורים לילדה שחולמת על במה, יום הולדת קרוב", 64, "cover-b64-kpop-star-girl", "girl",
     "יום הולדת בקרוב,\nוהיא חולמת על במה?", "דמיינו אותה\n**כוכבת קיי פופ**",
     "בספר היא מתאמנת מול המראה, נרשמת לתחרות ועולה לבמה.", "במה", "הילד"),
    ("2026-11-22", "a", "הורים לשני ילדים ומעלה", 49, "cover-b49-solar-system-journey-girl", "girl",
     "שני ילדים בבית?", "דמיינו את הגדולה\n**טסה למאדים**",
     "בספר היא חוקרת את מאדים, צדק וכל כוכבי הלכת.", "מאדים", "הילד"),
    ("2026-11-22", "b", "הורים לשני ילדים ומעלה", 67, "cover-b67-dinosaur-park-boy", "boy",
     "שני ילדים בבית?", "דמיינו את הקטן\n**בפארק הדינוזאורים**",
     "בספר הוא נכנס בשער ענק ופוגש דינוזאורים אמיתיים.", "דינוזאור", "הילד"),
    ("2026-11-23", "a", "הורים לילד שאוהב כדורגל", 23, "cover-b23-nois-big-tournament-boy", "boy",
     "כל היום עם כדור ברגליים?", "דמיינו אותו\n**בטורניר הגדול**",
     "בספר הוא משחק עם הקבוצה ולומד לא לוותר עד המשחק הגדול.", "גול", "הילד"),
    ("2026-11-23", "b", "הורים לילדה שאוהבת חיות", 22, "cover-b22-amits-stable-journey-girl", "girl",
     "מתה על סוסים?", "דמיינו אותה\n**באורווה עם הסוסים**",
     "בספר היא לומדת מהסוסים לצחוק, לנסות דברים חדשים ולא לוותר.", "סוס", "הילד"),
    ("2026-11-24", "a", "הורים שמחכים לתינוק, הגדול הופך לאח גדול", 2, "cover-b2-new-sibling-boy", "boy",
     "התינוק כבר בדרך?", "דמיינו אותו\n**אח גדול וגאה**",
     "בספר הוא מתכונן לתינוק, עוזר, ומרגיש כמה הוא חשוב.", "אח", "הילד"),
    ("2026-11-24", "b", "הורים שמחכים לתינוק, הגדולה הופכת לאחות גדולה", 2, "cover-b2-new-sibling-girl", "girl",
     "עוד מעט היא כבר לא הקטנה?", "דמיינו אותה\n**אחות גדולה וגאה**",
     "בספר היא מתכוננת לתינוק, עוזרת, ומרגישה כמה היא חשובה.", "אחות", "הילד"),
    ("2026-11-25", "a", "סבא וסבתא שמחפשים מתנה לנכד", 18, "cover-b18-what-will-i-be-tomorrow-boy", "boy",
     "סבא וסבתא,\nמה הוא יהיה כשיגדל?", "דמיינו את הנכד\n**רופא, טייס, צייר**",
     "בספר הוא יוצא למסע ומנסה מקצוע אחרי מקצוע.", "נכד", "הנכד"),
    ("2026-11-25", "b", "סבא וסבתא שמחפשים מתנה לנכד", 49, "cover-b49-solar-system-journey-boy", "boy",
     "סבא וסבתא,\nהנכד שואל על הכוכבים?", "דמיינו אותו\n**טס בין כוכבי הלכת**",
     "בספר הוא חוקר את מאדים, צדק וכל כוכבי הלכת.", "כוכבים", "הנכד"),
    ("2026-11-26", "a", "הורים לילד רגיש עם לב גדול", 13, "cover-b13-heart-of-courage-boy", "boy",
     "ילד עם לב ענק?", "דמיינו אותו\n**גיבור על של טוב לב**",
     "בספר הוא מגלה שכל מעשה טוב קטן הופך אותו לגיבור.", "לב", "הילד"),
    ("2026-11-26", "b", "הורים לילדה לפני התחלה חדשה", 47, "cover-b47-superhero-academy-first-day-girl", "girl",
     "יום ראשון במקום חדש?", "דמיינו אותה\n**באקדמיה לגיבורות על**",
     "בספר היא מגלה שהכוח הכי גדול הוא טוב לב.", "גיבורה", "הילד"),
    ("2026-11-27", "a", "הורים שמחפשים מתנת חנוכה", 86, "cover-b86-my-hanukkah-boy", "boy",
     "היום בלאק פריידיי,\nועוד שבוע חנוכה", "דמיינו אותו\n**מדליק את הנר הראשון**",
     "בספר הוא מכין חנוכייה, מדליק נר ועוד נר ומסובב סביבון.", "נר", "הילד"),
    ("2026-11-27", "b", "הורים שמחפשים מתנת חנוכה", 86, "cover-b86-my-hanukkah-girl", "girl",
     "מתנה לחנוכה?\nמזמינים עד 05 / 12", "דמיינו אותה\n**הגיבורה של חנוכה**",
     "בספר היא בתפקיד הראשי: חנוכייה, סביבון וסופגנייה.", "סביבון", "הילד"),
]


def plain(t):
    return t.replace("**", "").replace("\n", " ")


for d, o, icp, book, cover, g, label, head, bookline, word, noun in POSTS:
    key = f"bf-{d}-{o}"
    him = "אותו" if g == "boy" else "אותה"
    his = "שלו" if g == "boy" else "שלה"
    tagline = f"ספר מותאם אישית\nבכיכוב {noun} שלכם"
    cta = f"רוצים לראות {him} בספר, בחינם?\nתכתבו \"{word}\" ואשלח לכם את הקישור"
    hook = plain(label) + "\n" + plain(head) + "."
    car = {
        "id": key, "date": d, "option": o, "type": "bf", "format": "single", "addressee": "parents",
        "title": f"בלאק פריידיי: {plain(head)}",
        "angle_he": f"ICP: {icp}. סיפור מומצא על הילד ({plain(head)}), ספר אחד מהקטלוג (ספר {book}), ההצעה: ספר ראשון 119, ספר שני 99.",
        "icp_he": icp, "topic_id": "", "book": book, "comment_word": word, "emoji": "",
        "slides": [{"layout": "offer", "cover": cover, "label": label, "headline": head, "yes": tagline,
                    "p1": "ספר ראשון\n119 ₪", "p2": "ספר שני\n99 ₪",
                    "body": f"התצוגה המקדימה בחינם.\nתכתבו \"{word}\" ואשלח לכם את הקישור"}],
        "caption": "\n".join([hook, bookline, f"ספר מותאם אישית בכיכוב {noun} שלכם,", f"עם השם {his} והפנים {his}.",
                              "בבלאק פריידיי: ספר ראשון 119 ₪, ספר שני 99 ₪.", "התצוגה המקדימה בחינם, ומשלמים רק אם אהבתם.", cta]),
        "cta": cta,
        "fb_text": "\n".join([hook, "", bookline, f"ספר מותאם אישית בכיכוב {noun} שלכם, עם השם {his} והפנים {his}.", "",
                              "בבלאק פריידיי: ספר ראשון 119 ₪, ספר שני 99 ₪.", "התצוגה המקדימה בחינם, ומשלמים רק אם אהבתם.", "", "להכנת הספר 👇"]),
        "sources": [
            {"title": f"Book {book} page", "publisher": f"lumebook.com/IL/he/books/{book} (the page's description, read 20 Nov 2026)",
             "url": f"https://lumebook.com/IL/he/books/{book}", "accessed": "2026-11-20", "supports": "what happens in the book, as the story line says"},
            {"title": "Black Friday 2026 offer", "publisher": "shared/facts.json black_friday_2026 (Yarin, 19 Nov 2026; price on the posts approved 20 Nov 2026)",
             "url": "shared/facts.json", "accessed": "2026-11-20", "supports": "first book 119, second book 99"},
            {"title": "Who buys", "publisher": "research/hanukkah-black-friday-2026/black-friday.md (section 1) and research/mebook-customer-research/purchase-intents.md",
             "url": "research/hanukkah-black-friday-2026/black-friday.md", "accessed": "2026-11-20", "supports": "the ICP of the post"},
        ],
        "pictures": {},
        "_note": "The story is made up (Yarin, 20 Nov 2026: \"everyday invents a different story\"); what happens in the book is from its page. Check the store shows the 99 second book before posting.",
        "links": {
            "dm": f"https://lumebook.com/IL/he/books/{book}?utm_source=instagram&utm_medium=social&utm_campaign=bf-2026&utm_content=dm-{d.replace('-', '')}-{o}",
            "facebook": f"https://lumebook.com/IL/he/books/{book}?utm_source=facebook&utm_medium=social&utm_campaign=bf-2026&utm_content=post-{d.replace('-', '')}-{o}",
        },
    }
    (CARS / f"{key}.json").write_text(json.dumps(car, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(key)
