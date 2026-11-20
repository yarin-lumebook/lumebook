#!/usr/bin/env python3
"""The Facebook community tracker, קהילות פייסבוק (15 Nov 2026): since the same day the third view of the creator map.

The groups come from the parent community research (research/parent-community/data.json, every row whose platform is
"Facebook group": the parent groups and the UGC creator groups) with the Hebrew of their rules from research-he.json. The code
is page.css + page.js; embed_parts() hands them, the group data and the markup to the creator map's build
(creators/creator-research/src/build2.py), which draws them as the communities view (#fb-home, #fb-parents ...). Yarin's work
(statuses, posts, leads, message texts) is not in the page: it comes live from the project server (GET /api/communities/state,
tools/communities.py), so the map needs a rebuild only when the research, this code or the design system changes.

    python3 creators/creator-research/src/build2.py   the map, with this view inside
    python3 creators/community-tracker/build.py        only the old address, community-tracker.html, as a forward to the map
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

PAGE = "creators/community-tracker/community-tracker.html"
OUT = ROOT / PAGE
RESEARCH = ROOT / "research/parent-community/data.json"
HEBREW = HERE / "research-he.json"
ICONS = ["people", "pin", "facebook", "chat", "bell", "calendar", "home", "info", "send", "target", "heart", "share", "link", "mail",
         "whatsapp", "instagram", "eye", "trend", "funnel", "signup", "brief", "bookmark", "clock", "bars", "globe", "sheet",
         "plus", "search", "menu", "close", "copy", "open-out", "pencil", "check", "check-circle", "user-plus", "sort", "chevron-down",
         "arrow-left", "undo", "sparkle", "group", "stack", "file"]

APPROACH = {"Post directly": "לפרסם ישירות", "Ask admin first": "לפנות קודם למנהלים",
            "Paid post or formal partnership": "פוסט בתשלום או שותפות", "Monitor": "מעקב בלבד", "Do not use": "לא להשתמש"}
APPROVAL = {"Yes": "כן", "Yes (posts reviewed)": "כן, כל פוסט נבדק", "No (per rules)": "לא, לפי הכללים", "Unknown": "לא ידוע", "n/a": ""}
PRIVACY = {"Public": "ציבורית", "Private": "פרטית"}
BANDS = {1: "באשקלון", 2: "עד 30 ק״מ", 3: "30 עד 55 ק״מ", 4: "55 עד 80 ק״מ", 5: "מעל 80 ק״מ", 6: "ארצית"}
LANG = {"Hebrew": "עברית", "English": "אנגלית", "Russian": "רוסית", "Arabic": "ערבית"}
CONF = {"High": "גבוהה", "Medium": "בינונית", "Low": "נמוכה"}
SEGMENTS = {"Mothers": "אמהות", "Local city or neighbourhood parents": "הורים מהעיר", "General parents": "הורים",
            "Preschool and primary-school parents": "הורים לגן ולבית ספר", "Babies and toddlers": "תינוקות ופעוטות",
            "Special education or child development": "חינוך מיוחד והתפתחות", "Content creators and UGC": "יוצרי תוכן ו-UGC",
            "Product testing, deals and recommendations": "המלצות ומבצעים", "Fathers": "אבות",
            "Children's books and reading": "ספרי ילדים וקריאה"}
PARENT_SEGMENTS = {"Mothers", "Local city or neighbourhood parents", "General parents", "Preschool and primary-school parents",
                   "Babies and toddlers", "Special education or child development", "Fathers"}
GEO = {"National": "ארצית", "Modiin": "מודיעין", "Ashkelon": "אשקלון", "Haifa and Krayot": "חיפה והקריות",
       "Ramat Gan, Givatayim": "רמת גן וגבעתיים", "Herzliya": "הרצליה", "Petah Tikva": "פתח תקווה", "Jerusalem": "ירושלים",
       "Rehovot": "רחובות", "Netanya": "נתניה", "Raanana": "רעננה", "Ashdod": "אשדוד", "Beit Shemesh": "בית שמש",
       "Tel Aviv": "תל אביב", "Kfar Saba": "כפר סבא", "Rishon LeZion": "ראשון לציון", "Holon, Bat Yam": "חולון ובת ים",
       "Nes Ziona": "נס ציונה", "Maale Adumim": "מעלה אדומים", "Beer Sheva": "באר שבע", "Sderot": "שדרות", "Sharon": "השרון",
       "Hod Hasharon": "הוד השרון", "Nahariya": "נהריה", "Tiberias": "טבריה", "Beer Yaakov": "באר יעקב", "Hadera": "חדרה",
       "Kiryat Gat": "קריית גת", "Kiryat Malachi": "קריית מלאכי", "Gedera": "גדרה", "Centre": "המרכז", "Kiryat Ono": "קריית אונו",
       "Kiryat Motzkin": "קריית מוצקין", "Kiryat Bialik": "קריית ביאליק", "Or Yehuda": "אור יהודה",
       "Ramat Hasharon": "רמת השרון", "Kfar Yona": "כפר יונה", "Atlit": "עתלית", "North": "הצפון", "Netivot": "נתיבות",
       "Dimona": "דימונה", "Ofakim": "אופקים", "Yavne": "יבנה", "Rosh HaAyin": "ראש העין"}


def track_of(row):
    seg = set(row.get("segments") or [])
    return "ugc" if "Content creators and UGC" in seg and not (seg & PARENT_SEGMENTS) else "parent"


def groups(data, he):
    tr = (he or {}).get("groups") or {}
    top_he = (he or {}).get("top") or {}
    top = {t["id"]: (i + 1, top_he.get(t["id"]) or t.get("why", "")) for i, t in enumerate(data.get("top") or [])}
    out, missing = [], []
    for r in data["rows"]:
        if r.get("platform") != "Facebook group":
            continue
        gid = str(r["id"])
        h = tr.get(gid) or {}
        if not h:
            missing.append(gid)
        geo = r.get("geo") or ""
        g = {
            "id": gid, "name": r["name"], "url": r.get("url") or "", "about": r.get("evidence") or "",
            "track": track_of(r), "pri": r.get("priority") or "", "band": r.get("band") or 6,
            "km": r.get("dist_km"), "geo": GEO.get(geo, geo), "mem": r.get("members_n"), "pm": r.get("posts_month"),
            "priv": PRIVACY.get(r.get("privacy"), r.get("privacy") or ""), "privKey": r.get("privacy") or "",
            "appr": APPROVAL.get(r.get("approval"), r.get("approval") or ""),
            "ap": r.get("approach") or "", "apHe": APPROACH.get(r.get("approach"), r.get("approach") or ""),
            "pol": h.get("policy") or r.get("policy") or "", "polEn": r.get("policy") or "",
            "notes": h.get("notes") or r.get("notes") or "", "contact": h.get("contact") or r.get("contact") or "",
            "seg": [SEGMENTS.get(s, s) for s in (r.get("segments") or [])],
            "lang": LANG.get(r.get("language"), r.get("language") or ""), "conf": CONF.get(r.get("confidence"), ""),
            "checked": r.get("checked") or data.get("checked") or "",
        }
        if gid in top:
            g["top"], g["why"] = top[gid]
        if not h:
            g["polIsEn"] = True
        out.append(g)
    return out, missing


def templates(data, facts):
    """The message texts a fresh tracker starts with. Once Yarin saves his own (settings/main), the page uses his."""
    d = data.get("drafts") or {}
    form = "https://forms.gle/eBLpHjAbRSnM8FQo7"
    pct = (facts.get("offer") or {}).get("allocation_pct", 25)
    link = (facts.get("offer") or {}).get("wording_he", "קישור אישי עם הנחה לקהל")
    parent = [
        {"id": "p-full", "kind": "post", "title": "פוסט מלא בקבוצה", "text": d.get("post_general", "")},
        {"id": "p-short", "kind": "post", "title": "פוסט קצר", "text": d.get("post_short", "")},
        {"id": "p-admin", "kind": "admin", "title": "הודעה למנהלי הקבוצה", "text": d.get("dm_admin", "")},
        {"id": "p-reply", "kind": "dm", "title": "תשובה למי שהגיבו", "text":
            "היי [שם] 🙏\nתודה שכתבת!\nכל הפרטים וההרשמה בטופס הקצר\n" + form + "\nואם יש שאלה אפשר לכתוב לי פה בפרטי"},
    ]
    ugc = [
        {"id": "u-post", "kind": "post", "title": "פוסט בקבוצת יוצרים", "text":
            "היי לכולם 👋\nאני ירין, מנהל הסושיאל של לומיבוק\nאנחנו מכינים ספרי ילדים מותאמים אישית, שבהם הילד הוא הגיבור של הסיפור\n\n"
            "מחפשים יוצרות ויוצרי תוכן שמצלמים עם ילדים\nאמהות, אבות ואנשי מקצוע בגיל הרך\n\n"
            "מה מקבלים\nספר מותאם אישית לילד שלכם\n" + link + "\n"
            f"{pct}% מכל מכירה דרך הקישור, לחלוקה בין הרווח שלכם להנחה לקהל\n\n"
            "מה מבקשים\nסרטון אחד שנסכם עליו מראש\nאין תשלום על הסרטון, רק עמלה ממכירות דרך הקישור\n\n"
            "מתאים לכם? כתבו לי בפרטי או בתגובה ואשלח את כל הפרטים 🙏"},
        {"id": "u-admin", "kind": "admin", "title": "הודעה למנהלי הקבוצה", "text":
            "היי [שם] 👋\nאני ירין, מנהל הסושיאל של לומיבוק\nאנחנו מכינים ספרי ילדים מותאמים אישית\n\n"
            "רציתי לשאול לפני שאני מפרסם משהו בקבוצה\nאנחנו מחפשים יוצרי תוכן שמצלמים עם ילדים\n"
            "ספר במתנה וקישור אישי עם עמלה על כל מכירה\n\nמותר לפרסם פוסט כזה בקבוצה?\n"
            "אם יש יום קבוע או מחיר לפוסט, אשמח לדעת\nתודה 🙏"},
        {"id": "u-reply", "kind": "dm", "title": "תשובה למי שהגיבו", "text":
            "היי [שם] 🙏\nתודה שכתבת!\nשולח לך את כל הפרטים פה בפרטי"},
    ]
    return {"parent": parent, "ugc": ugc}


def creator_handles():
    """Instagram handles already in the creator map, so a UGC lead can show that the creator is there."""
    try:
        rows = json.loads((ROOT / "creators/creator-research/src/C_all.json").read_text(encoding="utf-8"))
        return sorted({str(r.get("h", "")).lower() for r in rows if r.get("h")})
    except (OSError, ValueError):
        return []


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def embed_parts():
    """The communities view of the creator map (since 15 Nov 2026). creators/creator-research/src/build2.py puts these into
    lumebook-creator-map.html: css (page.css), data (window.CT_* and CT_EMBED), js (page.js), nav (the side bar group), top (the top
    bar's search, post and lead buttons and save state), overlays (drawer, dialog, menu, toast). Everything the communities script
    handles carries .ct-scope, so the map's own handlers and its handlers never meet."""
    data = json.loads(RESEARCH.read_text(encoding="utf-8"))
    facts = json.loads((ROOT / "shared/facts.json").read_text(encoding="utf-8"))
    try:
        he = json.loads(HEBREW.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        he = {}
    gs, missing = groups(data, he)
    n_parent = sum(1 for g in gs if g["track"] == "parent")
    blob = {
        "CT_EMBED": 1,
        "CT_GROUPS": gs,
        "CT_TEMPLATES": templates(data, facts),
        "CT_ICONS": {n: design.icon(n) for n in ICONS},
        "CT_CAT": {k: design.cat_class("community-metrics", k) for k in ("groups", "posts", "reactions", "comments", "leads")},
        "CT_CREATORS": creator_handles(),
        "CT_META": {"checked": data.get("checked", ""), "parent": n_parent, "ugc": len(gs) - n_parent,
                    "form": (facts.get("parent_shoot_offer") or {}).get("form_url", ""),
                    "creator_map": "#c-all",
                    "research": "/research/parent-community/lumebook-parent-communities.html"},
    }
    js_data = "".join(f"window.{k}={json.dumps(v, ensure_ascii=False, separators=(',', ':'))};" for k, v in blob.items()).replace("</", "<\\/")
    i = design.icon
    nav = [("home", "home", "בית", ""), ("parents", "people", "קהילות הורים", "parent"), ("ugc", "sparkle", "קהילות יוצרי UGC", "ugc"),
           ("posts", "send", "פוסטים", "posts"), ("leads", "user-plus", "לידים", "leads"), ("templates", "copy", "נוסחים להעתקה", ""),
           ("method", "info", "מאיפה הקבוצות", "")]
    nav_html = "".join(
        f'<a class="nav-i lb-nav-item lb-ws-communities" href="#fb-{key}" data-ctroute="{key}"><span class="lb-tile">{i(ic, "i")}</span>'
        f'<span class="t">{esc(label)}</span>' + (f'<b class="cnt lb-count" data-ctcnt="{cnt}"></b>' if cnt else "") + "</a>"
        for key, ic, label, cnt in nav)
    top = (f'<label class="lb-search ct-search"><span class="lb-sr">חיפוש</span>{i("search")}<input class="lb-input" id="ctQ" type="search" dir="rtl" '
           f'placeholder="חיפוש קבוצה, עיר או ליד" autocomplete="off"><span class="lb-kbd" aria-hidden="true">/</span></label>'
           f'<span class="lb-savestate is-wait" id="ctSave">טוען…</span>'
           f'<button class="lb-btn secondary sm" type="button" id="ctAddPost">{i("send")}<span class="ct-hide-sm">פוסט</span></button>'
           f'<button class="lb-btn sm" type="button" id="ctAddLead">{i("user-plus")}<span class="ct-hide-sm">ליד</span></button>')
    overlays = f"""<aside class="lb-drawer ct-drawer ct-scope" id="ctDrawer" role="dialog" aria-modal="true" aria-labelledby="ctDrawerT" hidden>
  <div class="lb-drawer-head"><h2 id="ctDrawerT" translate="no"></h2><button class="lb-btn ghost icon" type="button" id="ctDrawerX" aria-label="סגירה">{i("close")}</button></div>
  <div class="lb-drawer-body" id="ctDrawerB"></div>
</aside>
<div class="lb-scrim ct-dscrim ct-scope" id="ctDScrim" hidden></div>
<dialog class="lb-dialog ct-dlg ct-scope" id="ctDlg" aria-labelledby="ctDlgT"><div class="lb-dialog-card">
  <div class="lb-dialog-head"><h2 id="ctDlgT" class="ct-dlg-t"></h2><button class="lb-dialog-x" type="button" id="ctDlgX" aria-label="סגירה">✕</button></div>
  <div class="lb-dialog-body"><form class="lb-card lb-form ct-form" id="ctForm" novalidate></form></div>
</div></dialog>
<div class="lb-popover ct-pop ct-scope" id="ctPop" role="menu" hidden></div>
<div class="lb-toast ct-scope" id="ctToast" role="status" hidden></div>"""
    return {"css": (HERE / "page.css").read_text(encoding="utf-8"), "data": js_data, "js": (HERE / "page.js").read_text(encoding="utf-8"),
            "nav": nav_html, "top": top, "overlays": overlays, "groups": gs, "missing": missing}


def build():
    """The tracker has no page of its own since 15 Nov 2026: it is the creator map's third view. This writes the old address as a
    forward to it (#parents becomes #fb-parents), so a saved link still lands in the right place."""
    p = embed_parts()
    own = p["js"] + p["css"] + p["nav"] + p["top"] + p["overlays"]
    if "\u2014" in own or "\u2013" in own:
        raise SystemExit("an em or en dash slipped into the communities code; fix the source")
    OUT.write_text("""<!doctype html>
<html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>קהילות פייסבוק</title>
<script>location.replace("../creator-research/lumebook-creator-map.html#fb-"+(location.hash.length>1?location.hash.slice(1):"home"))</script>
</head><body><p><a href="../creator-research/lumebook-creator-map.html#fb-home">קהילות פייסבוק נמצאות עכשיו במפת היוצרים</a></p></body></html>
""", encoding="utf-8")
    n_ugc = sum(1 for g in p["groups"] if g["track"] == "ugc")
    print(f"communities view: {len(p['groups'])} Facebook groups ({len(p['groups']) - n_ugc} parents, {n_ugc} UGC creators), "
          f"{len(p['missing'])} without Hebrew rules; {PAGE} forwards to the creator map. Build the map: python3 creators/creator-research/src/build2.py")


if __name__ == "__main__":
    build()
