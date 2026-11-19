#!/usr/bin/env python3
"""Writes the story series and their sets into series.json (19 Nov 2026).

    python3 media/projects/2026-11-19-story-series/make_sets.py day1          # the first day of all three series (23 / 11 / 2026)
    python3 media/projects/2026-11-19-story-series/make_sets.py day1 --force  # overwrite a set that already exists

A set is data (see tools/stories.py): the editor in the content calendar changes it afterwards, so this file only seeds. It never
overwrites a set that is approved or already sent, even with --force. Review frames take their words from the social proof page's
data.json and check that every quoted piece is word for word in the review (a cut is marked with an ellipsis, never reworded).
"""
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import stories  # noqa: E402

ART = "media/projects/2026-11-19-story-series/art/"
PROOF = ROOT / "media" / "projects" / "2026-11-15-social-proof"
GOLD, INK, VIOLET = "#F5C26B", "#2B1A5C", "#5B2BD6"
STORE = "https://lumebook.com/IL/he"


def utm(path, campaign, day):
    return f"{STORE}{path}?utm_source=instagram&utm_medium=social&utm_campaign={campaign}&utm_content=story-{day.replace('-', '')}"


SERIES = {
    "bf": {"name": "בלאק פריידיי", "name_en": "Black Friday", "start": "2026-11-23", "end": "2026-11-30", "time": "19:30", "path": "/books",
           "about": "לפי רצף הסטוריז בבריף 5 של black-friday.md: ציפייה, הוכחה, ומ־25 / 11 המבצע (ספר ראשון 119, שני 99) רק באישור שלך למחיר מחוץ לרילס. עד סייבר מאנדיי."},
    "hanukkah": {"name": "חנוכה", "name_en": "Hanukkah", "start": "2026-11-23", "end": "2026-12-12", "time": "14:30", "path": "/holiday-cards",
                 "about": "כל סטורי מוביל למתנה החינמית בעמוד holiday-cards (כרטיס ברכה או חוברת צביעה), עד סוף חנוכה."},
    "reviews": {"name": "ביקורות", "name_en": "Reviews", "start": "2026-11-23", "end": "2026-12-12", "time": "10:30", "path": "",
                "about": "3 עד 5 ביקורות אמיתיות בכל יום, מעמוד ההוכחה החברתית, עד סוף חנוכה."},
}


def text(i, t, y, size=110, x=90, w=900, color="#FFFFFF", weight=900, align="center", lh=1.1, shadow=True, **kw):
    return {"id": i, "type": "text", "text": t, "x": x, "y": y, "w": w, "size": size, "color": color, "weight": weight, "align": align,
            "lh": lh, "shadow": shadow, **kw}


def sticker(i, kind, label, y, h=150, x=140, w=800, url=""):
    return {"id": i, "type": "sticker", "kind": kind, "label": label, "x": x, "y": y, "w": w, "h": h, "url": url}


def frame(i, art, layers, scrim=None, note="", fill="#2B0E6E"):
    return {"id": i, "bg": {"src": ART + art, "fill": fill, "x": 50, "y": 50, "zoom": 100}, "scrim": scrim or {"top": 0, "bottom": 0},
            "layers": layers, "note": note}


def black_friday(day):
    link = utm(SERIES["bf"]["path"], "bf-2026", day)   # the campaign's tag (shared/facts.json black_friday_2026.utm_campaign)
    return [
        frame("f1", "story-bf-cart-toys.png", [
            text("l1", "עוד 4 ימים לבלאק פריידיי", 262, size=58, weight=700, color=GOLD),
            text("l2", "העגלה כבר מלאה\n**בצעצועים**", 340, size=94),
            text("l3", "מה מכל זה הוא עוד יזכור בעוד שנה?", 1440, size=54, weight=700, w=860, x=110)],
            note="פתיח. מבוסס על כוונה 3 ב־black-friday.md: העגלה מלאה צעצועים ומתנה אחת שלא נזרקת."),
        frame("f2", "story-bf-gift-box.png", [
            text("l1", "אז מה כן קונים?", 285, size=62, weight=700, color=GOLD),
            text("l2", "מתנה אחת\nשהוא **ישמור**", 390, size=112),
            sticker("l3", "poll", "סקר: עוד צעצוע או מתנה אישית?", 1400, h=170)],
            note="שאלה לקהל. הסקר הוא מדבקה שמוסיפים באפליקציה (פוסטיז לא שולח מדבקות)."),
        frame("f3", "story-reviews-backdrop.png", [
            text("l1", "שאלות שאתם שואלים", 330, size=70, weight=700, color=GOLD),
            text("l2", "תוך כמה זמן\nזה **מגיע**?", 440, size=104),
            text("l3", "עד 7 ימי עסקים, עד הבית.", 690, size=58, weight=700),
            text("l4", "צריך לכתוב\nסיפור **בעצמנו**?", 840, size=104),
            text("l5", "לא. בוחרים סיפור, והילד בפנים.", 1090, size=58, weight=700),
            sticker("l6", "question", "תיבת שאלה: מה עוד תרצו לדעת?", 1250, h=200),
            sticker("l7", "link", "מדבקת קישור: הספרים באתר", 1470, h=100, url=link)],
            note="שאלות ותשובות, לפי בריף 5 ב־black-friday.md (שלב ההוכחה, 22 עד 24 / 11). מחיר רק מ־25 / 11 ורק באישור שלך. תשובות: store_facts.delivery ו־Q31."),
    ]


def hanukkah(day):
    """Every Hanukkah frame promotes the free gift page (Yarin, 19 Nov 2026: "i want to promote this https://lumebook.com/IL/he/holiday-cards
    for hanukkah"). Its words come from that page, read 19 / 11 / 2026: a personal greeting card or a colouring booklet "בכיכוב הילדים",
    "בלי תשלום · בלי כרטיס אשראי", one face photo, a first name, birth month and year, "יוצרים ומשתפים בוואטסאפ"."""
    link = utm(SERIES["hanukkah"]["path"], "story-hanukkah", day)
    return [
        frame("f1", "story-hanukkah-windowsill.png", [
            text("l1", "עוד 11 ימים לנר הראשון", 285, size=64, weight=700, color=GOLD),
            text("l2", "ברכה לחנוכה\nשהילדים **בתוכה**", 380, size=112),
            text("l3", "מתנה מאיתנו, בלי תשלום", 1340, size=58, weight=900),
            sticker("l4", "countdown", "ספירה לאחור: נר ראשון, 04 / 12", 1450, h=120)],
            note="ספירה לאחור (נר ראשון בערב שישי 04 / 12 / 2026) שמובילה למתנה החינמית בעמוד holiday-cards."),
        frame("f2", "story-hanukkah-table.png", [
            text("l1", "מתנה מאיתנו לחנוכה", 258, size=64, weight=700, color=GOLD),
            text("l2", "כרטיס ברכה או\n**חוברת צביעה**", 336, size=98),
            sticker("l3", "link", "מדבקת קישור: המתנה החינמית", 1290, h=130, url=link),
            text("l4", "בכיכוב הילדים, **בחינם**", 1450, size=58, w=900)],
            note="המתנה החינמית בעמוד holiday-cards: כרטיס ברכה אישי או חוברת צביעה (חמישה דפים להדפסה בבית)."),
        frame("f3", "story-reviews-backdrop.png", [
            text("l1", "איך מקבלים?", 470, size=76, weight=900, color=GOLD),
            text("l2", "1. תמונה אחת של הפנים\n2. שם וחודש לידה\n3. כרטיס או חוברת צביעה", 590, size=62, weight=700, lh=1.45),
            text("l3", "ומשתפים **בוואטסאפ**", 900, size=80),
            text("l4", "בלי תשלום ובלי כרטיס אשראי", 1040, size=54, weight=700),
            sticker("l5", "link", "מדבקת קישור: המתנה החינמית", 1230, h=150, url=link)],
            note="איך זה עובד, לפי עמוד המתנה (נקרא 19 / 11 / 2026). מוביל ל־holiday-cards."),
    ]


# ---------------------------------------------------------------- reviews: the real screenshots, names and faces blurred
# The layout and the blur boxes live in tools/stories.py (review_layers, blur_boxes), shared with the editor's review picker.

BLUR_LOG = HERE / "blur-boxes.json"


def review_frame(i, rv, parts, found, cta=False, link=""):
    layers, note = stories.review_layers(rv, parts, cta, found)
    if cta:
        layers += [text("l6", "רואים תצוגה מקדימה\nעם הילד שלכם, בחינם", 1300, size=56, weight=700, w=860, x=110),
                   sticker("l7", "link", "מדבקת קישור: לתצוגה מקדימה", 1460, h=120, url=link)]
    return frame(i, "story-reviews-backdrop.png", layers, note=note)


def reviews(day):
    data = json.loads((PROOF / "data.json").read_text(encoding="utf-8"))
    by = {r["id"]: r for r in data["reviews"]}
    removed = set((json.loads((PROOF / "removed.json").read_text(encoding="utf-8")).get("removed") or {}))
    pick = [("google-00", ["הספרים הגיעו באיכות מאוד טובה, יפה ונעימה לעין!", "תמורה טובה מעל ומעבר למחיר"]),
            ("instagram-instagram-DI86Va_i9mS-1", None),
            ("instagram-instagram-DMmNcIZCnq1-1", None),
            ("instagram-instagram-DI82xDBipBK-1", None)]
    for rid, _ in pick:
        assert "review:" + rid not in removed and rid in by, rid
        assert "@" not in by[rid]["text"], f"{rid} tags someone in its words: pick another"
    found = stories.find_names([PROOF / by[rid]["file"] for rid, _ in pick if by[rid]["platform"] == "instagram"])
    log = json.loads(BLUR_LOG.read_text(encoding="utf-8")) if BLUR_LOG.exists() else {}
    link = utm("", "story-reviews", day)
    out = []
    for n, (rid, parts) in enumerate(pick, 1):
        log[by[rid]["file"]] = dict(zip(("boxes", "how"), stories.blur_boxes(by[rid], found)), day=day)
        out.append(review_frame(f"f{n}", by[rid], parts, found, cta=(n == len(pick)), link=link))
    BLUR_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


DAYS = {
    "day1": {"2026-11-23": {"bf": black_friday, "hanukkah": hanukkah, "reviews": reviews}},
}


def main():
    a = sys.argv[1:]
    if not a or a[0] not in DAYS:
        print(__doc__)
        return 2
    force = "--force" in a
    d = stories.data()
    for ser, meta in SERIES.items():
        link_ok = {**meta}
        link_ok.pop("path", None)
        camp = {"bf": "bf-2026"}.get(ser, f"story-{ser}")
        d["series"][ser] = {**d["series"].get(ser, {}), **link_ok, "link": utm(meta["path"], camp, meta["start"])}
    stories.save(d)          # the series first: clean_set checks a set's series against the file
    wrote = []
    for day, makers in DAYS[a[0]].items():
        for ser, fn in makers.items():
            key = f"{ser}-{day}"
            old = d["sets"].get(key)
            if old and (old.get("approved") or (old.get("postiz") or {}).get("ids")):
                print("skipped (approved or sent):", key)
                continue
            if old and not force:
                print("exists, use --force:", key)
                continue
            doc = {"series": ser, "date": day, "time": SERIES[ser]["time"], "title": "", "channels": ["ig", "fb"], "frames": fn(day), "notes": ""}
            d["sets"][key] = stories.clean_set(doc, old)
            wrote.append(key)
    stories.save(d)
    print("wrote", ", ".join(wrote) or "nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
