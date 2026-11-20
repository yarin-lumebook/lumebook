#!/usr/bin/env python3
"""Builds the content calendar page (sites/content-calendar/index.html) from page.css and page.js with the design system inlined
(design.head(): tokens, lb- components, the project nav, the language switch). The data comes live from the project server
(GET /api/calendar, tools/content_calendar.py), so the page only needs a rebuild when its code or the design system changes.

    python3 sites/content-calendar/build.py      (or: python3 tools/lumebook.py build content-calendar)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

PAGE = "sites/content-calendar/index.html"
ICONS = ["slides", "flask", "clapper", "sparkle", "send", "bell", "film", "pencil", "bars", "check-circle", "target", "play", "sync", "wallet",
         "clock", "check", "info", "instagram", "facebook", "chat", "compass", "gift", "trend", "eye", "calendar", "arrow-left", "arrow-right",
         "plus", "search", "menu", "upload", "download", "folder", "layers", "open-out", "image", "close",
         "book", "copy", "audio", "file", "stack", "link", "undo", "arrow-up"]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def data_js():
    facts = json.loads((ROOT / "shared" / "facts.json").read_text(encoding="utf-8"))
    dates = {d["date"]: d["label"] for d in facts.get("key_dates", []) if d.get("date") and d.get("label")}
    reels = json.loads((ROOT / "research/israeli-product-reels/src/scripts/series-2026-11/reels.json").read_text(encoding="utf-8"))
    disclaimer = (reels.get("defaults") or {}).get("caption_disclaimer", "")
    icons = {n: design.icon(n) for n in ICONS}
    cats = {k: design.cat_class("content-types", k) for k in ("kid", "test", "reel", "post", "idea", "story", "season")}
    blob = {"CC_ICONS": icons, "CC_CAT": cats, "CC_DATES": dates, "CC_DISCLAIMER": disclaimer}
    return "".join(f"window.{k}={json.dumps(v, ensure_ascii=False)};" for k, v in blob.items()).replace("</", "<\\/")


def page():
    i = design.icon
    help_rows = [("T", "היום"), ("← →", "חודש, שבוע או יום קודם או הבא, לפי התצוגה"), ("↑ ↓", "שבוע קודם או הבא (בחודש)"), ("PageUp PageDown", "חודש"), ("1 2 3", "חודש, שבוע, יום"),
                 ("/", "חיפוש"), ("Enter", "פתיחת היום"), ("Esc", "סגירה"), ("?", "העזרה הזאת")]
    help_html = "".join(f'<span>{"".join(f"<kbd class=lb-kbd>{esc(k)}</kbd>" for k in keys.split(" ") if k not in ("+",))}</span><span>{esc(what)}</span>'
                        for keys, what in help_rows)
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>לוח תוכן</title>
{design.head(page=PAGE)}
<style>
{(HERE / "page.css").read_text(encoding="utf-8")}
</style>
</head>
<body dir="rtl">
<div class="lb-app cc-app" dir="rtl" lang="he">
<aside class="lb-sidebar cc-side" id="ccSide" aria-label="לוח תוכן">
  <a class="lb-brand" href="#"><img src="{design.logo_data_uri()}" alt=""><span><b>לוח תוכן</b><small>קרוסלות, רילס וסטוריז, חודש אחד</small></span></a>
  <section class="cc-sec" aria-labelledby="ccQh"><h2 id="ccQh">{i("bell")}צריך אותי השבוע<span class="lb-count" id="ccQn"></span></h2><div class="cc-q" id="ccQ"></div></section>
  <section class="cc-sec"><div class="cc-mini-head" id="ccMiniT"></div><div class="cc-mini" id="ccMini"></div></section>
  <section class="cc-sec" aria-labelledby="ccTh"><h2 id="ccTh">סוג</h2><div class="cc-ft" id="ccTypes"></div></section>
  <section class="cc-sec"><div class="cc-ft" id="ccDrafts"></div></section>
  <section class="cc-sec" aria-labelledby="ccSh"><h2 id="ccSh">סטטוס</h2><div class="cc-stf" id="ccSts"></div></section>
  <section class="cc-sec" aria-labelledby="ccLh"><h2 id="ccLh">מקרא</h2><div class="cc-legend" id="ccLegend"></div></section>
  <div class="cc-side-foot">
    <button class="lb-btn ghost sm" type="button" id="ccHelpBtn"><kbd class="lb-kbd">?</kbd>קיצורי מקלדת</button>
    <div class="cc-help" id="ccHelp" hidden>{help_html}</div>
    <span>הכלים הקודמים: <a href="/hook-studio/">מכונת הקרוסלות</a> · <a href="/research/israeli-product-reels/reels-explorer.html#calendar">מערכת הרילס</a></span>
  </div>
</aside>
<div class="lb-scrim" id="ccScrim" hidden></div>
<main class="lb-main" aria-label="לוח התוכן של החודש">
  <header class="lb-topbar lb-edge cc-top"><div class="lb-topbar-in">
    <button class="lb-btn ghost sm cc-side-btn" type="button" id="ccSideBtn" aria-controls="ccSide" aria-pressed="true" aria-label="הסרגל של הלוח">{i("menu")}</button>
    <button class="lb-btn secondary sm lb-menu-btn" type="button" id="ccMenu" aria-controls="ccSide">{i("bell")}תור וסינון <span class="lb-count" id="ccMenuN"></span></button>
    <h1>לוח תוכן <small id="ccMonth"></small></h1>
    <span class="cc-nav"><button class="lb-btn secondary sm" type="button" id="ccToday">היום</button></span>
    <span class="lb-segmented" id="ccViews" role="group" aria-label="תצוגה"><button type="button" data-v="month">חודש</button><button type="button" data-v="week">שבוע</button><button type="button" data-v="day">יום</button></span>
    <span class="lb-spacer"></span>
    <label class="lb-search cc-search"><span class="lb-sr">חיפוש</span>{i("search")}<input class="lb-input" id="ccQ2" type="search" dir="rtl" placeholder="חיפוש: הוק, נושא, כיתוב, מספר ריל" autocomplete="off"></label>
    <button class="lb-btn" type="button" id="ccNewBtn">{i("plus")}<span class="cc-new-lbl">חדש</span></button>
  </div></header>
  <div class="cc-body"><div class="cc-notice" id="ccNotice" role="status" hidden></div><section class="cc-qphone" id="ccQPhone" aria-label="צריך אותי"></section><div class="cc-stage"><div class="cc-rail cc-edge" data-dir="-1"><button class="lb-btn secondary" type="button" id="ccPrev" aria-label="החודש הקודם">{i("arrow-right")}</button></div><section id="ccView" aria-live="polite"></section><div class="cc-rail cc-edge" data-dir="1"><button class="lb-btn secondary" type="button" id="ccNext" aria-label="החודש הבא">{i("arrow-left")}</button></div></div></div>
</main>
</div>
<dialog class="lb-dialog cc-dlg" id="ccDlg" aria-labelledby="ccDlgT"><div class="lb-dialog-card">
  <div class="lb-dialog-head"><h2 id="ccDlgT"></h2><button class="lb-dialog-x" type="button" id="ccDlgX" aria-label="סגירה">✕</button></div>
  <div class="lb-dialog-body" id="ccDlgB"></div>
</div></dialog>
<dialog class="lb-dialog cc-new" id="ccNew" aria-labelledby="ccNewH"><div class="lb-dialog-card">
  <div class="lb-dialog-head"><h2 id="ccNewH" style="flex:1;margin:0;padding-inline:var(--sp-4);font-size:var(--fs-headline)">רעיון חדש</h2><button class="lb-dialog-x" type="button" id="ccNewX" aria-label="סגירה">✕</button></div>
  <form class="lb-dialog-body" id="ccNewForm" novalidate>
    <span class="lb-segmented" id="ccNewFor" role="group" aria-label="סוג"><button type="button" data-for="carousel" aria-pressed="true">קרוסלה</button></span>
    <div class="lb-row"><label class="lb-field">תאריך<input class="lb-input" type="date" id="ccNewDate" required></label><label class="lb-field">שעה (לא חובה)<input class="lb-input" type="time" id="ccNewTime"></label></div>
    <label class="lb-field">על מה הפוסט<textarea class="lb-textarea lb-editable" dir="rtl" id="ccNewBrief" rows="3" placeholder="למשל: סבתא שמחפשת מתנה לחנוכה לנכד שכבר יש לו הכול"></textarea></label>
    <p class="lb-form-error" id="ccNewErr" hidden></p>
    <div class="lb-row"><button class="lb-btn" type="submit">{i("sparkle")}לבקש רעיון ו-5 הוקים</button></div>
  </form>
</div></dialog>
<div class="cc-peek" id="ccPeek" hidden></div>
<div class="lb-toast" id="ccToast" role="status" hidden></div>
<script>{data_js()}</script>
<script>
{(HERE / "story-frame.js").read_text(encoding="utf-8")}
</script>
<script>
{(HERE / "story.js").read_text(encoding="utf-8")}
</script>
<script>
{(HERE / "season.js").read_text(encoding="utf-8")}
</script>
<script>
{(HERE / "page.js").read_text(encoding="utf-8")}
</script>
</body>
</html>
"""


def main():
    out = HERE / "index.html"
    out.write_text(page(), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
