"""november-calendar.html: the November reel calendar as a page (Yarin, 04 Nov 2026: "html").

Built from reels.json by `reels.py build` (which calls page()). Never edit the HTML; edit reels.json and build.
Design system: shared/design (design.head(), lb- components, white only). Series colours come from the
"reel-series" set in shared/design/categories.json; status has its own chips, never a category hue.

Editing (Yarin, 04 Nov 2026: "just make the text editable and auto save with full text editor options"): every text on
the page carries data-ek (a stable key such as r1-2__vo__3) and is contenteditable, with a formatting toolbar. Edits save
by themselves, on claude.ai to the artifact's db (collection "edits", one document per key: html, text, base, at); on the
project server to local-edits.json next to this file (through /api/reels-hub/*, since 06 Nov 2026; what the browser had
kept in localStorage moves there on the first visit); anywhere else (Vercel) only in that browser. An edit is shown only
while its base still equals the built text, so a later change to reels.json is never hidden under an old edit.
`reels.py merge FILE` copies saved edits back into reels.json (FILE = the "edits" collection read with ArtifactData;
`reels.py merge local` reads local-edits.json instead).
"""
import calendar, html, json, re, sys
from datetime import date
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "shared" / "design"))
sys.path.insert(0, str(HERE))
import design  # noqa: E402
import reels  # noqa: E402

OUT = HERE / "november-calendar.html"
OUT_WEB = HERE / "november-calendar-web.html"
WEEK = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]   # Israeli week, Sunday first
STATUS = {  # label, chip class
    "posted": ("פורסם", "success"),
    "ready": ("מוכן לפרסום", "success"),
    "needs-edit": ("מחכה לעריכה שלי", "info"),
    "needs-voice": ("מחכה לצילום וקריינות שלך", "warning"),
    "needs-footage": ("מחכה לחומר", "warning"),
    "blocked": ("חסום", "danger"),
    "spare": ("ספייר", ""),
}
VOICE = {"yarin": "הקריינות שלך", "text": "טקסט בלי קול", "trend": "טרנד מוכן"}
e = html.escape



def ddmm(iso, year=True):
    y, m, d = iso.split("-")
    return f"{d} / {m} / {y}" if year else f"{d} / {m}"


def wd(iso):
    return WEEK[(date.fromisoformat(iso).weekday() + 1) % 7]


def series_cls(n):
    return design.cat_class("reel-series", str(n))


def rid(r):
    return "r" + r["id"].replace(".", "-")


def ek(*parts):
    """Editable key: letters, digits, - and _ only, so it is also a valid db document id."""
    return "__".join(str(p) for p in parts).replace(".", "-").replace("/", "-")


def opt_link(r, day, pick):
    """One of a day's two options (10 Nov 2026): a small tinted card with the option letter, the id and the hook; the
    picked one gets a green border and נבחרה, the other fades (the page script repaints both from the saved picks)."""
    lab, cls = STATUS[r["status"]]
    letter = reels.OPT[r["option"]]
    state = " is-pick" if pick == r["id"] else " is-unpicked" if pick else ""
    aud_html = '<span class="aud" title="מדבר לסבתות">סבתא</span>' if r.get("audience") == "grandma" else ""
    return (f'<a class="lb-day lb-tinted is-opt {series_cls(r["series"])}{state}" href="#{rid(r)}" data-k="{rid(r)}" data-series="{r["series"]}" '
            f'data-aud="{r.get("audience", "parents")}" data-day="{r["date"]}" data-opt="{r["option"]}" '
            f'aria-label="{day.day} בנובמבר, אפשרות {letter}, ריל {e(r["id"])}, {e(lab)}">'
            f'<span class="lb-day-top"><span class="opt-l" title="אפשרות {letter}">{letter}</span><span class="lb-pid">{e(r["id"])}</span></span>'
            f'<span class="lb-day-text" data-hook-of="{ek(rid(r), "hook")}">{e(r["hook"].replace(chr(10), " "))}</span>'
            f'<span class="lb-day-foot"><span class="st {cls}" title="{e(lab)}"></span>{aud_html}<span class="pick-mark">נבחרה</span>'
            f'<span class="lb-day-tick" title="עשית">✓</span></span></a>')


def month_grid(rs, carousels, picks=None):
    picks = picks or {}
    by_date = {}
    for r in sorted((r for r in rs if r["date"]), key=lambda r: (r.get("option") or 1)):
        by_date.setdefault(r["date"], []).append(r)
    cal = calendar.Calendar(firstweekday=6)  # Sunday
    cells = [f'<div class="lb-month-dow" aria-hidden="true">{d}</div>' for d in WEEK]
    for day in cal.itermonthdates(2026, 11):
        iso = day.isoformat()
        if day.month != 11:
            cells.append('<div class="lb-day is-out" aria-hidden="true"></div>')
            continue
        day_rs = by_date.get(iso) or []
        car = carousels.get(iso)
        car_html = f'<span class="car" title="קרוסלה 06:00: {e(car)}">קרוסלה</span>' if car else ""
        if not day_rs:
            cells.append(f'<div class="lb-day is-empty"><span class="lb-day-num">{day.day}</span>{car_html}</div>')
            continue
        if len(day_rs) > 1:   # two options (Yarin, 10 Nov 2026: "i want 2 options for each day")
            p = picks.get(iso) if isinstance(picks.get(iso), str) else ""
            p_k = "r" + p.replace(".", "-") if p else ""
            cells.append(f'<div class="lb-day-pair{" is-picked" if p else ""}" data-day="{iso}" data-pick-def="{p_k}" role="group" '
                         f'aria-label="{day.day} בנובמבר, שתי אפשרויות">'
                         f'<span class="pair-top"><span class="lb-day-num">{day.day}</span>{car_html}</span>'
                         + "".join(opt_link(r, day, p) for r in day_rs) + '</div>')
            continue
        r = day_rs[0]
        lab, cls = STATUS[r["status"]]
        aud_html = '<span class="aud" title="מדבר לסבתות">סבתא</span>' if r.get("audience") == "grandma" else ""
        cells.append(
            f'<a class="lb-day lb-tinted {series_cls(r["series"])}" href="#{rid(r)}" data-k="{rid(r)}" data-series="{r["series"]}" data-aud="{r.get("audience", "parents")}" '
            f'aria-label="{day.day} בנובמבר, ריל {e(r["id"])}, {e(lab)}">'
            f'<span class="lb-day-top"><span class="lb-day-num">{day.day}</span><span class="lb-pid">{e(r["id"])}</span></span>'
            f'<span class="lb-day-text" data-hook-of="{ek(rid(r), "hook")}">{e(r["hook"].replace(chr(10), " "))}</span>'
            f'<span class="lb-day-foot"><span class="st {cls}" title="{e(lab)}"></span>{aud_html}{car_html}<span class="lb-day-tick" title="עשית">✓</span></span></a>')
    return f'<div class="lb-month">{"".join(cells)}</div>'



def ed(tag, key, inner, cls="", attrs=""):
    """An editable element."""
    c = f' class="lb-editable {cls}"' if cls else ' class="lb-editable"'
    return f'<{tag}{c} data-ek="{key}" dir="rtl"{attrs}>{inner}</{tag}>'


def card(r, d, web=False):
    lab, cls = STATUS[r["status"]]
    s = d["defaults"]
    k = rid(r)
    rows = []
    shot = ed("p", ek(k, "shot"), e(r["shot"])) if r.get("shot") else ""
    if r.get("yarin_films"):
        shot += '<span class="sub">אתה מצלם</span>' + ed("p", ek(k, "films"), e(", ".join(r["yarin_films"])))
    # the payoff and the structure (Yarin, 09 Nov 2026: the @matan.nistor study "implemented to all reels"): what the viewer
    # sees when the reel pays off, kept on screen until the לומי card (research/matan-nistor-reels/report.md)
    if r.get("payoff") or r.get("structure"):
        st = f'<span class="lb-chip outline" title="המבנה של הריל">{e(r["structure"])}</span>' if r.get("structure") else ""
        rows.append(("השיא על המסך", st + ed("p", ek(k, "payoff"), e(r.get("payoff", "")))))
    if shot:
        rows.append(("צילום", f'<details class="shot"><summary>הצגה</summary>{shot}</details>'))
    script = script_table(r, d) if r.get("vo") else ""
    if r["voice"] == "trend":
        # on-screen text is copy for parents: it stays Hebrew when the language switch shows English (8 Nov 2026)
        lis = f'<li><span data-hook-of="{ek(k, "hook")}" translate="no">{e(r["hook"].replace(chr(10), " "))}</span></li>'
        if r["status"] != "posted":
            lis += f'<li class="fixed" title="קבוע לכל הרילס" translate="no">{e(s["cta_screen"].replace(chr(10), " "))}</li>'
        rows.append((f"טקסט על המסך, טרנד {r['clip_seconds']:g} שניות", f'<ol class="vo">{lis}</ol>'))
    if r.get("cards"):
        rows.append(("כרטיסיות על המסך", '<ol class="vo">' + "".join(ed("li", ek(k, "cards", i), e(x)) for i, x in enumerate(r["cards"])) + "</ol>"))
    cap = reels.caption_of(r, d)
    rows.append(("כיתוב לאינסטגרם",
                 f'<div class="cap">{ed("div", ek(k, "caption"), e(cap), "capbox lb-textblock", f" id=cap-{k}")}'
                 f'<button class="lb-btn copy" type="button" data-copy="cap-{k}">העתקה</button></div>'))
    body = "".join(f'<div class="row"><dt class="sec-t">{design.icon(ROW_ICON.get(t, "info"), "i")}{t}</dt><dd>{v}</dd></div>' for t, v in rows if t != "כיתוב לאינסטגרם")
    cap_row = next(v for t, v in rows if t == "כיתוב לאינסטגרם")
    car = s["carousel_days"].get(r["date"]) if r["date"] else None
    car_html = f'<span class="lb-chip outline">באותו יום קרוסלה: {e(car)}</span>' if car else ""
    aud = "סבתות" if r.get("audience") == "grandma" else "הורים"
    aud_html = f'<span class="lb-chip {"accent" if r.get("audience") == "grandma" else ""}" title="למי הריל מדבר">מדבר ל{aud}</span>'
    pg = r.get("page")
    pg_html = (f'<a class="lb-chip tint" target="_blank" rel="noopener" href="https://lumebook.com/IL/he/{e(pg)}" title="הדף שהקישור ב DM פותח">'
               f'{e(d["defaults"].get("pages", {}).get(pg, pg))}</a>') if pg else ""
    when = (f'<span class="wd">{wd(r["date"])}</span><span class="dd">{ddmm(r["date"], False)}</span><span class="tm">{e(s["post_time"])}</span>'
            if r["date"] else '<span class="wd">ספייר</span>')
    sec = reels.seconds(r, d)
    return f"""
<article class="reel lb-card lb-tinted {series_cls(r['series'])}" id="{k}" data-series="{r['series']}" data-status="{r['status']}">
  <header class="reel-head">
    <div class="when">{when}</div>
    <button type="button" class="lb-chip check" data-made="{k}" data-def="{1 if r['status'] == 'posted' else 0}" aria-pressed="false">עשיתי</button>
    <div class="meta">
      <span class="lb-pid">{e(r['id'])}</span>
      <span class="lb-chip cat">{e(design.categories('reel-series')[str(r['series'])]['label'])}</span>
      <span class="lb-chip {cls}">{e(lab)}</span>
      <span class="lb-chip" title="אורך משוער">{sec:g} שניות</span>
      <span class="lb-chip">{VOICE[r['voice']]}</span>
      {aud_html}{pg_html}
      {car_html}
    </div>
  </header>
  {opt_bar(r, d)}
  {ed("h3", ek(k, "hook"), e(r['hook'].replace(chr(10), ' ')), "hook-big", f' title="{e(r["hook"].replace(chr(10), " "))}"')}
  {script}
  <dl class="rows lb-sheet">{body}</dl>
  {"" if web else make_sheet(k)}
  <section class="capwin lb-window" aria-label="כיתוב לאינסטגרם"><h4 class="sec-t">{design.icon("instagram", "i")}כיתוב לאינסטגרם</h4>{cap_row}</section>
</article>"""


ROW_ICON = {"צילום": "eye", "כרטיסיות על המסך": "layers", "השיא על המסך": "sparkle"}


def opt_bar(r, d):
    """The two options of the reel's day (10 Nov 2026): a segmented control that opens either one, and בוחר בזו, which saves
    this one as the day's pick (collection "picks"; a second click clears it). Nothing for a day with one reel."""
    rs = reels.options(d).get(r["date"], []) if r["date"] else []
    if len(rs) < 2:
        return ""
    seg = "".join(f'<button type="button" data-open="{rid(x)}" aria-pressed="{"true" if x is r else "false"}">'
                  f'אפשרות {reels.OPT[x["option"]]}<span class="optbar-id">{e(x["id"])}</span></button>' for x in rs)
    on = reels.pick_of(d, r["date"]) == r["id"]
    return (f'<div class="optbar" data-day="{r["date"]}"><div class="lb-segmented" role="group" aria-label="שתי האפשרויות ליום הזה">{seg}</div>'
            f'<button type="button" class="lb-chip check pick" data-pick="{rid(r)}" data-day="{r["date"]}" aria-pressed="{"true" if on else "false"}">'
            f'<span>{"נבחרה" if on else "בוחר בזו"}</span></button></div>')


def make_sheet(k):
    """Making the reel from the card (Yarin, 07 Nov 2026: "a full file dropping and a prompt text box to the reel cards so i could
    let you create the reel through there"): the finished reel, a drop zone, the dropped files and the prompt for Claude. The script
    fills it from the project server (/api/reel-files, /api/reel-make/jobs); elsewhere only make-off shows."""
    return (f'<section class="make lb-sheet" data-make="{k}" aria-label="יצירת הריל">'
            f'<div class="make-head"><h4 class="sec-t">{design.icon("film", "i")}יצירת הריל</h4><span class="make-sum"></span></div>'
            f'<div class="make-final" hidden></div>'
            f'<label class="lb-drop make-drop">{design.icon("upload")}<span class="lb-drop-t">גוררים לכאן סרטונים, הקלטות ותמונות</span>'
            f'<span class="lb-drop-s">או לוחצים לבחירה. הכול נשמר בתיקיית הריל</span>'
            f'<input type="file" multiple accept="video/*,audio/*,image/*,.heic,.pdf" aria-label="בחירת קבצים לריל"></label>'
            f'<ul class="lb-files make-files" aria-label="הקבצים של הריל"></ul>'
            f'<div class="lb-composer make-comp"><textarea rows="2" dir="rtl" aria-label="מה Claude עושה עם החומרים" '
            f'placeholder="מה לעשות עם החומרים? למשל: הטייק השני לפתיחה, לחתוך את השתיקות, הקלטת המסך באמצע"></textarea>'
            f'<div class="lb-composer-bar"><span class="lb-composer-note make-note"></span>'
            f'<button type="button" class="lb-btn sm make-go">{design.icon("play")}<span>ליצור את הריל</span></button></div></div>'
            f'<p class="make-msg" role="status" aria-live="polite"></p>'
            f'<p class="make-off">העלאת קבצים ויצירת הריל עובדות בעמוד המקומי, במחשב שלך (localhost:8780).</p></section>')


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def script_table(r, d):
    """The voiceover as a table (Yarin, 07 Nov 2026: "what i say, what they see, timestamps"). Times come from the word
    count, the same estimate as reels.seconds (lead_seconds on the first line, words_per_second after); the page
    recounts them while a line is edited."""
    s, L, k = d["defaults"], d["defaults"]["length"], rid(r)
    sees = r.get("sees", [])
    lines = [(ed("div", ek(k, "vo", i), e(x)), ed("div", ek(k, "sees", i), e(sees[i] if i < len(sees) else ""), "sees-ed"), len(x.split()), "")
             for i, x in enumerate(r["vo"])]
    if r["status"] != "posted":
        lines.append((f'<div>{e(s["cta_voice"])}</div>', f'<div>{e(s["cta_sees"])}</div>', len(s["cta_voice"].split()), ' class="fixed" title="קבוע לכל הרילס"'))
    t, trs = 0.0, []
    for i, (say, see, w, cls) in enumerate(lines):
        a = t
        t += (L["lead_seconds"] if i == 0 else 0) + w / L["words_per_second"]
        trs.append(f'<tr{cls}><td class="tc" data-label="זמן"><span class="t0">{mmss(a)}</span><span class="t1">{mmss(t)}</span></td>'
                   f'<td class="say" data-label="מה אני אומר">{say}</td><td class="see" data-label="מה רואים">{see}</td></tr>')
    words = sum(x[2] for x in lines)
    return (f'<section class="script lb-sheet" aria-label="תסריט">'
            f'<div class="script-head"><h4 class="sec-t">{design.icon("clapper", "i")}תסריט</h4><span class="script-sum"><b class="script-sec">{t:.0f}</b> שניות, <b class="script-w">{words}</b> מילים</span></div>'
            f'<table class="lb-table top is-stack script-t" data-lead="{L["lead_seconds"]}" data-wps="{L["words_per_second"]}">'
            f'<thead><tr><th class="tc">זמן</th><th>מה אני אומר</th><th>מה רואים</th></tr></thead><tbody>{"".join(trs)}</tbody></table></section>')


AUTOSCROLL = """<div class="autoscroll" role="group" aria-label="גלילה אוטומטית של התסריט">
    <button type="button" class="lb-chip check" id="as-go" aria-pressed="false" title="גלילה איטית של התסריט, כמו טלפרומפטר"><span id="as-lbl">▶ גלילה</span></button>
    <button type="button" class="lb-chip" id="as-slow" aria-label="לאט יותר">−</button>
    <span class="as-speed" id="as-speed" aria-live="polite">3</span>
    <button type="button" class="lb-chip" id="as-fast" aria-label="מהר יותר">+</button>
  </div>
  <style>
  .autoscroll { display: flex; align-items: center; gap: 4px; margin-inline-start: auto; padding-inline: 6px; flex: none; }
  .autoscroll .lb-chip { min-width: 2.25rem; justify-content: center; cursor: pointer; }
  .autoscroll .as-speed { min-width: 1.5rem; text-align: center; font-family: var(--font-2); font-weight: 700; font-variant-numeric: tabular-nums; }
  .lb-dialog-head > .lb-editbar:not([hidden]) ~ .autoscroll { margin-inline-start: 0; }
  </style>"""

TOOLBAR = """
<div class="lb-editbar" id="tb" role="toolbar" aria-label="עיצוב טקסט">
  <div class="lb-editbar-in">
    <button type="button" data-cmd="undo" title="ביטול (⌘Z)">↶</button>
    <button type="button" data-cmd="redo" title="ביצוע מחדש (⇧⌘Z)">↷</button>
    <span class="sep"></span>
    <select id="tb-block" title="סגנון">
      <option value="">סגנון</option><option value="p">פסקה</option><option value="h2">כותרת גדולה</option>
      <option value="h3">כותרת</option><option value="h4">כותרת קטנה</option><option value="blockquote">ציטוט</option>
    </select>
    <select id="tb-font" title="גופן">
      <option value="">גופן</option><option value="Heebo">ראשי</option><option value="Assistant">משני</option>
      <option value="Arial">אריאל</option><option value="ui-monospace">מונו</option>
    </select>
    <select id="tb-size" title="גודל">
      <option value="">גודל</option><option value="1">קטן מאוד</option><option value="2">קטן</option><option value="3">רגיל</option>
      <option value="4">בינוני</option><option value="5">גדול</option><option value="6">גדול מאוד</option><option value="7">ענק</option>
    </select>
    <span class="sep"></span>
    <button type="button" data-cmd="bold" title="מודגש (⌘B)"><b>B</b></button>
    <button type="button" data-cmd="italic" title="נטוי (⌘I)"><i>I</i></button>
    <button type="button" data-cmd="underline" title="קו תחתון (⌘U)"><u>U</u></button>
    <button type="button" data-cmd="strikeThrough" title="קו חוצה"><s>S</s></button>
    <label class="clr" title="צבע טקסט"><span class="a">A</span><input type="color" id="tb-color" value="#5b2bd6"></label>
    <label class="clr hl" title="הדגשת רקע"><span class="a">▇</span><input type="color" id="tb-hilite" value="#fbebc9"></label>
    <span class="sep"></span>
    <button type="button" data-cmd="justifyRight" title="יישור לימין">⇥</button>
    <button type="button" data-cmd="justifyCenter" title="מרכוז">≡</button>
    <button type="button" data-cmd="justifyLeft" title="יישור לשמאל">⇤</button>
    <button type="button" data-cmd="justifyFull" title="יישור לשני הצדדים">☰</button>
    <span class="sep"></span>
    <button type="button" data-cmd="insertUnorderedList" title="רשימת תבליטים">•</button>
    <button type="button" data-cmd="insertOrderedList" title="רשימה ממוספרת">1.</button>
    <button type="button" data-cmd="outdent" title="הקטנת הזחה">⇠</button>
    <button type="button" data-cmd="indent" title="הגדלת הזחה">⇢</button>
    <span class="sep"></span>
    <button type="button" data-cmd="link" title="קישור (⌘K)">🔗</button>
    <button type="button" data-cmd="unlink" title="הסרת קישור">⛓</button>
    <button type="button" data-cmd="superscript" title="כתב עילי">x²</button>
    <button type="button" data-cmd="subscript" title="כתב תחתי">x₂</button>
    <button type="button" data-cmd="dir" title="כיוון כתיבה ימין או שמאל">⇄</button>
    <button type="button" data-cmd="removeFormat" title="ניקוי עיצוב">⌫</button>
    <input id="tb-link" type="url" dir="ltr" hidden aria-label="כתובת הקישור, אנטר לאישור">
    <span class="hint">לוחצים על טקסט כדי לערוך</span>
  </div>
</div>"""

SCRIPT = r"""
<script>
(function () {
  "use strict";
  var KEY_F = "lb-reels-nov-filter", KEY_L = "lb-reels-nov-edits";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* filter */
  var btns = $$(".filters [data-f]");
  function applyFilter(f) {
    btns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.f === f)); });
    $$(".lb-day[data-series]").forEach(function (el) {
      var hit = f === "all" || (f === "grandma" ? el.dataset.aud === "grandma" : el.dataset.series === f);
      el.classList.toggle("is-dim", !hit);
    });
    try { localStorage.setItem(KEY_F, f); } catch (x) {}
  }
  btns.forEach(function (b) { b.addEventListener("click", function () { applyFilter(b.dataset.f); }); });
  var savedF = "all";
  try { savedF = localStorage.getItem(KEY_F) || "all"; } catch (x) {}
  if ($('.filters [data-f="' + savedF + '"]')) applyFilter(savedF);

  /* copy */
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var el = document.getElementById(b.dataset.copy);
      var done = function () { b.textContent = "הועתק"; setTimeout(function () { b.textContent = "העתקה"; }, 1600); };
      var select = function () { var r = document.createRange(); r.selectNodeContents(el); var s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = "מסומן, להעתיק"; };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(el.innerText).then(done, select); else select();
    });
  });

  /* sanitizer: keep formatting, drop scripts, handlers and unknown tags */
  var OK = { B:1, STRONG:1, I:1, EM:1, U:1, S:1, STRIKE:1, SPAN:1, FONT:1, A:1, UL:1, OL:1, LI:1, BR:1, DIV:1, P:1, H2:1, H3:1, H4:1, BLOCKQUOTE:1, SUB:1, SUP:1, MARK:1 };
  var ATTR = { style:1, href:1, color:1, size:1, face:1, dir:1 };
  function clean(html) {
    var t = document.createElement("template"); t.innerHTML = html;
    (function walk(node) {
      $$("*", node).reverse().forEach(function (el) {
        if (!OK[el.tagName]) {
          if (/^(SCRIPT|STYLE|IFRAME|OBJECT|EMBED|TEMPLATE|META|LINK)$/.test(el.tagName)) { el.remove(); return; }
          while (el.firstChild) el.parentNode.insertBefore(el.firstChild, el);
          el.remove(); return;
        }
        Array.prototype.slice.call(el.attributes).forEach(function (a) {
          var n = a.name.toLowerCase();
          if (!ATTR[n]) el.removeAttribute(a.name);
          else if (n === "href" && !/^(https?:|mailto:)/i.test(a.value.trim())) el.removeAttribute(a.name);
          else if (n === "style" && /url\(|expression|javascript:/i.test(a.value)) el.removeAttribute(a.name);
        });
        if (el.tagName === "A") { el.setAttribute("target", "_blank"); el.setAttribute("rel", "noopener"); }
      });
    })(t.content);
    return t.innerHTML;
  }

  /* editable fields */
  var fields = {};   // key -> {el, base, baseHtml}
  $$("[data-ek]").forEach(function (el) {
    fields[el.dataset.ek] = { el: el, base: el.innerText.trim(), baseHtml: el.innerHTML };
    el.setAttribute("contenteditable", "true");
    el.setAttribute("spellcheck", "true");
  });
  function syncHook(key) {
    var f = fields[key]; if (!f) return;
    $$('[data-hook-of="' + key + '"]').forEach(function (s) { s.textContent = f.el.innerText.replace(/\s*\n\s*/g, " ").trim(); });
  }

  /* status pill */
  var pill = $("#save-state");
  function state(t, kind) { pill.textContent = t; pill.className = "lb-chip " + (kind || ""); }

  /* store: artifact db when the viewer serves it, else this browser */
  var store = null, local = {}, readOnly = false;
  try { local = JSON.parse(localStorage.getItem(KEY_L) || "{}"); } catch (x) { local = {}; }
  function applyDoc(key, doc) {
    var f = fields[key]; if (!f || !doc || typeof doc.html !== "string") return;
    if (document.activeElement === f.el) return;
    var text = typeof doc.text === "string" ? doc.text.trim() : "";
    if (doc.base !== f.base && text !== f.base) { f.el.classList.add("is-stale"); f.el.title = "הטקסט השתנה במקור אחרי העריכה, מוצג הטקסט החדש"; return; }
    f.el.innerHTML = clean(doc.html);
    f.el.classList.add("is-edited");
    syncHook(key);
  }
  Object.keys(local).forEach(function (k) { applyDoc(k, local[k]); });

  var timers = {}, pending = 0;
  function save(key) {
    var f = fields[key]; if (!f || readOnly) return;
    var doc = { key: key, html: clean(f.el.innerHTML), text: f.el.innerText.trim(), base: f.base, at: new Date().toISOString() };
    pending++; state("שומר...", "info");
    var done = function () { pending--; if (!pending) state(store ? "נשמר" : "נשמר בדפדפן הזה", "success"); f.el.classList.add("is-edited"); };
    var fail = function (err) {
      pending--;
      if (err && err.code === "invalid_argument") { readOnly = true; lockAll(); state("קריאה בלבד", ""); return; }
      state("לא נשמר, אנסה שוב", "danger"); setTimeout(function () { save(key); }, 5000);
    };
    if (store) store.doc(key).set(doc).then(done, fail);
    else { try { local[key] = doc; localStorage.setItem(KEY_L, JSON.stringify(local)); done(); } catch (x) { fail(x); } }
  }
  function lockAll() { Object.keys(fields).forEach(function (k) { fields[k].el.setAttribute("contenteditable", "false"); }); $("#tb").hidden = true; }
  document.addEventListener("input", function (ev) {
    var el = ev.target.closest && ev.target.closest("[data-ek]"); if (!el) return;
    var key = el.dataset.ek; syncHook(key); state("לא נשמר עדיין", "warning");
    clearTimeout(timers[key]); timers[key] = setTimeout(function () { save(key); }, 700);
  });
  document.addEventListener("focusout", function (ev) {
    var el = ev.target.closest && ev.target.closest("[data-ek]"); if (!el || !timers[el.dataset.ek]) return;
    clearTimeout(timers[el.dataset.ek]); timers[el.dataset.ek] = null; save(el.dataset.ek);
  });
  /* paste keeps formatting, cleaned */
  document.addEventListener("paste", function (ev) {
    var el = ev.target.closest && ev.target.closest("[data-ek]"); if (!el) return;
    var h = ev.clipboardData && ev.clipboardData.getData("text/html");
    if (!h) return;
    ev.preventDefault(); document.execCommand("insertHTML", false, clean(h));
  });
  /* links inside edited text still open with ⌘ or Ctrl click */
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("[data-ek] a[href]");
    if (a && (ev.metaKey || ev.ctrlKey)) window.open(a.href, "_blank", "noopener");
  });

  /* Where edits live (6 Nov 2026): on claude.ai the artifact's db (collections edits, made, requests); on the project server
     its own file, research/.../series-2026-11/local-edits.json, through /api/reels-hub/* (reels.py merge local reads it);
     anywhere else (Vercel, a file) only this browser. The server twin below has the few db calls this page makes. */
  var onServer = null;   // promise: true when this page is served by the project server
  function projectServer() {
    if (!onServer) onServer = fetch("/api/board/env").then(function (r) { return r.ok ? r.json() : null; }, function () { return null; })
      .then(function (j) { return !!(j && j.server === "lumebook"); });
    return onServer;
  }
  function serverDb() {
    var HEAD = { "Content-Type": "application/json", "X-LumeBook-Board": "1" };
    return fetch("/api/reels-hub/state").then(function (r) { if (!r.ok) throw new Error("state"); return r.json(); }).then(function (st) {
      var docs = { edits: (st && st.edits) || {}, made: (st && st.made) || {}, requests: (st && st.requests) || {}, picks: (st && st.picks) || {} };
      function put(name, id, doc) {
        return fetch("/api/reels-hub/doc?path=" + encodeURIComponent(name + "/" + id), { method: "PUT", headers: HEAD, body: JSON.stringify(doc) })
          .then(function (r) { if (!r.ok) { var e = new Error("put"); e.code = "unavailable"; throw e; } docs[name][id] = doc; });
      }
      /* what this browser kept before the server did: send edits and ticks the server lacks (or has older), then forget them here */
      var moved = [];
      Object.keys(local).forEach(function (k) {
        var l = local[k], s = docs.edits[k];
        if (l && typeof l.html === "string" && (!s || String(l.at) > String(s.at))) {
          docs.edits[k] = l; moved.push(put("edits", k, l).then(function () { delete local[k]; }));
        } else delete local[k];
      });
      Promise.all(moved).then(function () { try { localStorage.setItem(KEY_L, JSON.stringify(local)); } catch (x) {} }, function () {});
      var ticks = [];
      Object.keys(made).forEach(function (k) {
        if (!docs.made[k]) { var d = { key: k, made: !!made[k], at: new Date().toISOString() }; docs.made[k] = d; ticks.push(put("made", k, d)); }
      });
      Promise.all(ticks).then(function () { try { localStorage.removeItem(KEY_M); } catch (x) {} }, function () {});
      var pk = [];
      Object.keys(picks).forEach(function (day) {
        if (!docs.picks[day]) { var d = { day: day, reel: picks[day] || "", at: new Date().toISOString() }; docs.picks[day] = d; pk.push(put("picks", day, d)); }
      });
      Promise.all(pk).then(function () { try { localStorage.removeItem(KEY_P); } catch (x) {} }, function () {});
      function collection(name) {
        return {
          doc: function (id) { return { set: function (doc) { return put(name, id, doc); } }; },
          add: function (doc) { return put(name, Date.now().toString(36) + Math.random().toString(36).slice(2, 7), doc); },
          onSnapshot: function (cb) {
            var ch = Object.keys(docs[name]).map(function (id) { return { type: "added", doc: { id: id, data: function () { return docs[name][id]; } } }; });
            setTimeout(function () { cb({ docChanges: function () { return ch; } }); }, 0);
          }
        };
      }
      return { collection: collection };
    });
  }
  function useDb(db) {
    store = db.collection("edits");
    madeStore = db.collection("made");
    reqStore = db.collection("requests");
    pickStore = db.collection("picks");
    madeStore.onSnapshot(function (snap) {
      snap.docChanges().forEach(function (c) { if (c.type === "removed") return; var v = c.doc.data(); made[c.doc.id] = !!(v && v.made); paintMade(c.doc.id); });
    }, function () {});
    pickStore.onSnapshot(function (snap) {
      snap.docChanges().forEach(function (c) { if (c.type === "removed") return; var v = c.doc.data(); picks[c.doc.id] = (v && v.reel) || ""; paintPick(c.doc.id); });
    }, function () {});
    var timer = setTimeout(function () { state("השמירה לא עונה", "warning"); }, 10000);
    store.onSnapshot(function (snap) {
      clearTimeout(timer);
      snap.docChanges().forEach(function (c) { if (c.type !== "removed") applyDoc(c.doc.id, c.doc.data()); });
      if (!pending) state("נשמר", "success");
    }, function () { clearTimeout(timer); state("השמירה לא זמינה", "danger"); });
  }
  if (window.claude && claude.use) {
    claude.use("db").then(function (db) {
      if (!db) { state("נשמר בדפדפן הזה", ""); return; }
      useDb(db);
      return claude.use("user").then(function (u) {
        if (!u) return;
        return u.can("data.write").then(function (w) { if (w === false) { readOnly = true; lockAll(); state("קריאה בלבד", ""); } });
      });
    }, function () { state("נשמר בדפדפן הזה", ""); });
  } else {
    projectServer().then(function (ok) { return ok ? serverDb().then(useDb) : null; })
      .then(function () { if (!store) state("נשמר בדפדפן הזה", ""); }, function () { state("נשמר בדפדפן הזה", ""); });
  }

  /* popup: a day opens its reel */
  var dlg = $("#dlg"), dbody = $("#dlg-body"), holder = $("#cards"), cur = null;
  function flush() { Object.keys(timers).forEach(function (k) { if (timers[k]) { clearTimeout(timers[k]); timers[k] = null; save(k); } }); }
  /* script table: times follow the word count while a line is edited (same estimate as reels.py seconds) */
  function mmss(t) { t = Math.round(t); return Math.floor(t / 60) + ":" + String(t % 60).padStart(2, "0"); }
  function retime(tb) {
    var lead = Number(tb.dataset.lead) || 0, wps = Number(tb.dataset.wps) || 2.8, t = 0, words = 0;
    $$("tbody tr", tb).forEach(function (tr, i) {
      var say = $(".say > div", tr), w = say ? say.innerText.trim().split(/\s+/).filter(Boolean).length : 0;
      var a = t; t += (i === 0 ? lead : 0) + w / wps; words += w;
      $(".t0", tr).textContent = mmss(a); $(".t1", tr).textContent = mmss(t);
    });
    var box = tb.closest(".script"); if (!box) return;
    $(".script-sec", box).textContent = Math.round(t); $(".script-w", box).textContent = words;
  }
  document.addEventListener("input", function (ev) {
    var tb = ev.target.closest && ev.target.closest(".script-t"); if (tb) retime(tb);
  });
  /* a wide screen docks the reel on the left as a drawer and the page narrows to the right, so the month stays in use next
     to it (Yarin, 07 Nov 2026: "open from the calendar like a drawer (from right to left) and minimize the calendar to the
     right"); a narrow one opens the popup. Design system: lb-dialog is-docked and html.lb-docked. */
  var DOCK_MIN = 1100, DOCK_MAX = 860, docked = false, dockTick = 0;
  function dockRoom() {   /* the width the page and the drawer share: the window left of the project nav (a page sidebar steps aside) */
    var h = document.documentElement;
    return h.clientWidth - (parseFloat(getComputedStyle(h).paddingRight) || 0);
  }
  function setDock(on) {
    var h = document.documentElement;
    if (on) h.style.setProperty("--lb-dock-w", Math.round(Math.min(dockRoom() / 2, DOCK_MAX)) + "px");
    docked = on; dlg.classList.toggle("is-docked", on); h.classList.toggle("lb-docked", on);
  }
  function showReel() {
    var want = dockRoom() >= DOCK_MIN;
    if (dlg.open && want === docked) { if (docked) setDock(true); return; }
    if (dlg.open) dlg.close();   /* popup to drawer or back: the close event finds it open again and leaves the card where it is */
    setDock(want);
    if (want) dlg.show(); else dlg.showModal();
  }
  function markDay(id) {
    $$(".lb-day[aria-current]").forEach(function (x) { x.removeAttribute("aria-current"); });
    var c = id && $('.lb-day[data-k="' + id + '"]'); if (c) c.setAttribute("aria-current", "true");
  }
  function redock() { dockTick = 0; if (dlg.open) showReel(); }
  if (window.ResizeObserver) new ResizeObserver(function () { if (dlg.open && !dockTick) dockTick = requestAnimationFrame(redock); }).observe(document.documentElement);
  else addEventListener("resize", function () { if (dlg.open && !dockTick) dockTick = requestAnimationFrame(redock); });
  document.addEventListener("keydown", function (ev) {   /* a docked drawer is not modal, so Escape is ours to handle */
    if (ev.key === "Escape" && docked && dlg.open && !ev.defaultPrevented) { ev.preventDefault(); dlg.close(); }
  });
  /* arrow keys jump between the days (Yarin, 08 Nov 2026): the month reads right to left, so Left is the next day and Right the
     one before; Up and Down move a week. With a reel open the next reel opens; otherwise the focus moves from day to day.
     A day with two options (10 Nov 2026) is one grid cell: the move keeps the option (א or ב) where the next day has it. */
  document.addEventListener("keydown", function (ev) {
    var k = ev.key, step = k === "ArrowLeft" ? 1 : k === "ArrowRight" ? -1 : k === "ArrowDown" ? 7 : k === "ArrowUp" ? -7 : 0;
    if (!step || ev.defaultPrevented || ev.metaKey || ev.ctrlKey || ev.altKey || ev.shiftKey) return;
    var t = ev.target, tag = t && t.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable)) return;
    var cells = $$("#calRoot .lb-month > :not(.lb-month-dow)"); if (!cells.length) cells = $$(".lb-month > :not(.lb-month-dow)");
    var here = cur && dlg.open ? $('.lb-day[data-k="' + cur.id + '"]') : (t && t.closest && t.closest("a.lb-day[data-k]"));
    if (!here) return;
    var i = cells.indexOf(here.closest(".lb-day-pair") || here); if (i < 0) return;
    var slot = here.dataset.opt || "1";
    ev.preventDefault();
    for (var j = i + step; j >= 0 && j < cells.length; j += step) {
      var c = cells[j], links = (c.matches("a.lb-day[data-k]") ? [c] : $$("a.lb-day[data-k]", c)).filter(function (x) { return x.getClientRects().length; });
      if (links.length) {
        var d = links.filter(function (x) { return (x.dataset.opt || "1") === slot; })[0] || links[0];
        if (cur && dlg.open) openReel(d.dataset.k); else d.focus();
        d.scrollIntoView({ block: "nearest", inline: "nearest" });
        return;
      }
    }
  });
  function openReel(id) {
    var a = document.getElementById(id); if (!a || !a.classList.contains("reel")) return;
    if (cur === a && dlg.open) { dlg.close(); return; }   /* its day clicked again while it is open: close the drawer (Yarin, 08 Nov 2026) */
    flush(); if (cur) holder.appendChild(cur);
    cur = a; dbody.appendChild(a);
    $$(".script-t", a).forEach(retime);
    makeOpen(a);
    showReel(); markDay(id);
    if (typeof asStop === "function") asStop();
    dlg.scrollTop = 0; $("#dlg-x").focus({ preventScroll: true });
    if (typeof paintAsk === "function" && askMsg) { msg(""); setBusy(false); paintAsk(); }   /* askMsg is still unset when a #reel link opens the page */
    try { history.replaceState(null, "", "#" + id); } catch (x) {}
  }
  dlg.addEventListener("close", function () {
    if (dlg.open) return;  /* a late close event after the popup was opened again */
    setDock(false); markDay(null);
    flush(); if (!cur) return;
    var c = $('.lb-day[data-k="' + cur.id + '"]'); holder.appendChild(cur); cur = null;
    try { history.replaceState(null, "", location.pathname + location.search); } catch (x) {}
    if (c) c.focus();
  });
  $("#dlg-x").addEventListener("click", function () { dlg.close(); });
  /* Slow auto-scroll of the open reel (10 Nov 2026, Yarin: "add an option to slowly scroll when the script is open ... and control the speed"):
     like a teleprompter. Nine speeds in pixels a second; the position is kept as a fraction so the slowest speed still moves; any touch,
     wheel, key or scrollbar drag stops it, and so does the end of the card, closing and opening another reel. */
  var AS = [8, 14, 20, 28, 38, 50, 66, 88, 120], asI = 2, asOn = false, asPos = 0, asLast = 0, asRaf = 0, asSet = 0;
  try { var sv = parseInt(localStorage.getItem("lb-reel-scroll-speed"), 10); if (sv >= 0 && sv < AS.length) asI = sv; } catch (x) {}
  var asGo = $("#as-go"), asLbl = $("#as-lbl"), asSpd = $("#as-speed");
  function asPaint() {
    asSpd.textContent = String(asI + 1);
    asLbl.textContent = asOn ? "⏸ עצירה" : "▶ גלילה";
    asGo.setAttribute("aria-pressed", asOn ? "true" : "false");
    $("#as-slow").disabled = asI === 0; $("#as-fast").disabled = asI === AS.length - 1;
  }
  function asStep(now) {
    if (!asOn) return;
    if (Math.abs(dlg.scrollTop - asSet) > 3) { asStop(); return; }   /* the reader moved it */
    asPos += AS[asI] * Math.min(now - asLast, 250) / 1000; asLast = now;
    var max = dlg.scrollHeight - dlg.clientHeight;
    if (asPos >= max) { dlg.scrollTop = max; asStop(); return; }
    dlg.scrollTop = asPos; asSet = dlg.scrollTop;
    asRaf = requestAnimationFrame(asStep);
  }
  function asStart() {
    if (!dlg.open) return;
    if (dlg.scrollHeight - dlg.clientHeight - dlg.scrollTop < 4) dlg.scrollTop = 0;   /* at the end: start again from the top */
    asOn = true; asPos = dlg.scrollTop; asSet = dlg.scrollTop; asLast = performance.now();
    asPaint(); asRaf = requestAnimationFrame(asStep);
  }
  function asStop() { asOn = false; cancelAnimationFrame(asRaf); asPaint(); }
  function asSpeed(d) {
    asI = Math.max(0, Math.min(AS.length - 1, asI + d));
    try { localStorage.setItem("lb-reel-scroll-speed", String(asI)); } catch (x) {}
    asPaint();
  }
  asGo.addEventListener("click", function () { if (asOn) asStop(); else asStart(); });
  $("#as-slow").addEventListener("click", function () { asSpeed(-1); });
  $("#as-fast").addEventListener("click", function () { asSpeed(1); });
  ["wheel", "touchstart", "pointerdown"].forEach(function (t) {
    dlg.addEventListener(t, function (ev) { if (asOn && !ev.target.closest(".autoscroll")) asStop(); }, { passive: true });
  });
  document.addEventListener("keydown", function (ev) {
    if (!asOn) return;
    if (ev.key === " " && !ev.target.closest("input, textarea, [contenteditable=true]")) { ev.preventDefault(); asStop(); }
    else if (["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End"].indexOf(ev.key) >= 0) asStop();
  });
  dlg.addEventListener("close", asStop);
  asPaint();
  dlg.addEventListener("click", function (ev) { if (ev.target === dlg && !docked) dlg.close(); });   /* the backdrop; a drawer has none */
  $$("a.lb-day[data-k]").forEach(function (c) { c.addEventListener("click", function (ev) { ev.preventDefault(); openReel(c.dataset.k); }); });
  if (location.hash.length > 1) openReel(decodeURIComponent(location.hash.slice(1)));

  /* "עשיתי": tick the reels you made */
  var KEY_M = "lb-reels-nov-made", made = {}, madeStore = null;
  try { made = JSON.parse(localStorage.getItem(KEY_M) || "{}"); } catch (x) { made = {}; }
  function isMade(k) { if (k in made) return !!made[k]; var b = $('[data-made="' + k + '"]'); return !!(b && b.dataset.def === "1"); }
  function paintMade(k) {
    var on = isMade(k);
    $$('[data-made="' + k + '"]').forEach(function (b) { b.setAttribute("aria-pressed", String(on)); });
    var c = $('.lb-day[data-k="' + k + '"]'); if (c) c.classList.toggle("is-done", on);
  }
  $$("[data-made]").forEach(function (b) {
    paintMade(b.dataset.made);
    b.addEventListener("click", function () {
      if (readOnly) return;
      var k = b.dataset.made; made[k] = !isMade(k); paintMade(k);
      if (madeStore) {
        pending++; state("שומר...", "info");
        madeStore.doc(k).set({ key: k, made: made[k], at: new Date().toISOString() }).then(
          function () { pending--; if (!pending) state("נשמר", "success"); },
          function () { pending--; state("לא נשמר", "danger"); });
      } else { try { localStorage.setItem(KEY_M, JSON.stringify(made)); state("נשמר בדפדפן הזה", "success"); } catch (x) {} }
    });
  });

  /* two options a day (Yarin, 10 Nov 2026: "i want 2 options for each day"): בוחר בזו saves which option goes up (collection
     "picks", one document per day: {day, reel, at}; reel "" clears it) and the month fades the other one. The built page starts
     from reels.json "picks" (data-pick-def); reels.py merge local copies the clicks back. The segmented control opens the other. */
  var KEY_P = "lb-reels-nov-picks", picks = {}, pickStore = null;
  try { picks = JSON.parse(localStorage.getItem(KEY_P) || "{}"); } catch (x) { picks = {}; }
  function pickOf(day) {
    if (day in picks) return picks[day] || "";
    var c = $('.lb-day-pair[data-day="' + day + '"]'); return (c && c.dataset.pickDef) || "";
  }
  function paintPick(day) {
    var p = pickOf(day);
    $$('.lb-day-pair[data-day="' + day + '"]').forEach(function (c) {
      c.classList.toggle("is-picked", !!p);
      $$("a.lb-day[data-k]", c).forEach(function (a) { a.classList.toggle("is-pick", a.dataset.k === p); a.classList.toggle("is-unpicked", !!p && a.dataset.k !== p); });
    });
    $$('.pick[data-pick][data-day="' + day + '"]').forEach(function (b) {
      var on = b.dataset.pick === p; b.setAttribute("aria-pressed", String(on));
      var s = $("span", b); if (s) s.textContent = on ? "נבחרה" : p ? "לבחור בזו במקום" : "בוחר בזו";
    });
  }
  function paintPicks() {
    var days = {}; $$(".lb-day-pair[data-day], .pick[data-day]").forEach(function (el) { days[el.dataset.day] = 1; });
    Object.keys(days).forEach(paintPick);
  }
  paintPicks();
  window.CalPicksPaint = paintPicks;
  document.addEventListener("click", function (ev) {
    var o = ev.target.closest && ev.target.closest(".optbar [data-open]");
    if (o) { if (!cur || cur.id !== o.dataset.open) openReel(o.dataset.open); return; }
    var b = ev.target.closest && ev.target.closest(".pick[data-pick][data-day]");
    if (!b || readOnly) return;
    var day = b.dataset.day, k = pickOf(day) === b.dataset.pick ? "" : b.dataset.pick;
    picks[day] = k; paintPick(day);
    if (pickStore) {
      pending++; state("שומר...", "info");
      pickStore.doc(day).set({ day: day, reel: k, at: new Date().toISOString() }).then(
        function () { pending--; if (!pending) state("נשמר", "success"); },
        function () { pending--; state("לא נשמר", "danger"); });
    } else { try { localStorage.setItem(KEY_P, JSON.stringify(picks)); state("נשמר בדפדפן הזה", "success"); } catch (x) {} }
  });

  /* comment box: Claude rewrites the open reel from a comment */
  var CFG = {}; try { CFG = JSON.parse($("#ask-cfg").textContent); } catch (x) {}
  var ask = $("#ask"), askT = $("#ask-t"), askGo = $("#ask-go"), askMsg = $("#ask-msg"), sampleFn = null, askCtl = null, reqStore = null;
  function msg(t, err) { askMsg.textContent = t; askMsg.classList.toggle("is-error", !!err); }
  function label(key) {
    var m = key.split("__"), f = m[1], i = m[2] ? Number(m[2]) + 1 : 0;
    return { hook: "כותרת (על המסך ובראש הכרטיס)", vo: "קריינות, שורה " + i, sees: "מה רואים על המסך בזמן קריינות שורה " + i + " (פנימי, לירין)", cards: "כרטיסייה על המסך " + i, caption: "כיתוב לאינסטגרם",
             shot: "הוראות צילום (פנימי, לירין)", films: "מה ירין מצלם (פנימי, רשימה מופרדת בפסיקים)",
             payoff: "השיא על המסך: מה רואים כשהריל נותן את מה שהבטיח (פנימי, לירין)" }[f] || f;
  }
  function tidy(t) {
    return String(t).replace(/\s*[\u2014\u2013]\s*/g, ", ").replace(/\u05BE/g, " ").replace(/(\S)\s+-\s+(\S)/g, "$1, $2")
      .replace(/;/g, ",").replace(/לומיבוק/g, "לומבוק").replace(/,\s*,/g, ",").trim();
  }
  function prompt(reel, comment) {
    var flds = {};
    $$("[data-ek]", reel).forEach(function (el) { flds[el.dataset.ek] = { role: label(el.dataset.ek), text: el.innerText.trim() }; });
    return [
      "אתה עורך את התסריט של ריל אחד לאינסטגרם של לומבוק (ספרי ילדים מותאמים אישית, ישראל). ירין, מנהל הסושיאל, כתב הערה. שנה את הטקסטים לפי ההערה בלבד.",
      "",
      "חוקים לכל טקסט שהורים רואים או שומעים (כותרת, קריינות, כרטיסיות, כיתוב):",
      "- עברית ישראלית יומיומית, כמו שירין מדבר עם הורה אחר. משפטים קצרים, פעלים לפני שמות עצם, בלי שפה של מותג או של מטפל.",
      "- בלי מקף מכל סוג (גם לא מקף עברי), בלי קו מפריד ארוך, בלי נקודה ופסיק. פסיק, נקודה, סימן שאלה וקריאה ומרכאות מותרים.",
      "- השם לומבוק בלבד, אף פעם לא לומיבוק. אף פעם לא להזכיר בינה מלאכותית. אף פעם לא \"קוד הנחה\" או \"קוד אישי\".",
      "- בלי עובדות חדשות. אף פעם לא להזכיר מחיר, סכום כסף, הנחה או מבצע. זמנים ותכונות רק מהעובדות כאן: " + CFG.facts + ". המבצע: " + CFG.offer + ".",
      "- כותרת: עד 8 מילים. קריינות: כל השורות יחד בין " + CFG.vo_min + " ל " + CFG.vo_max + " מילים, שורה אחת לכל מחשבה, עד 12 מילים בשורה.",
      "- שורת הסיום של הקריינות קבועה ומתווספת לבד: \"" + CFG.cta_voice + "\". לא לכתוב אותה בשורות.",
      "- הכיתוב מסתיים תמיד בשורה הזאת, מילה במילה: " + CFG.cta_caption,
      "- אם בסוף הכיתוב יש הסתייגות רפואית, להשאיר אותה בדיוק כמו שהיא.",
      "- הוראות הצילום, רשימת הצילום ו\"מה רואים\" הן הערות פנימיות לירין, בעברית פשוטה, בגוף שני. \"מה רואים\" נשאר מתאים לשורת הקריינות שלו.",
      "",
      "אפשר לשנות רק את המפתחות שכבר קיימים. אי אפשר להוסיף או למחוק שורות. כל ערך חייב להיות לא ריק. לשנות רק מה שההערה מבקשת, ומה שחייב להשתנות בעקבותיה כדי שהריל יישאר עקבי.",
      "",
      "הריל עכשיו (מפתח, תפקיד, טקסט):",
      JSON.stringify(flds, null, 1),
      "",
      "ההערה של ירין:",
      comment,
      "",
      "תחזיר רק JSON בצורה הזאת, בלי שום טקסט אחר:",
      "{\"changes\": {\"<מפתח>\": \"<הטקסט החדש>\"}, \"summary\": \"משפט קצר בעברית: מה שינית\"}",
      "אם אי אפשר לעשות את מה שההערה מבקשת בלי לשבור את החוקים, תחזיר changes ריק ותסביר ב summary."
    ].join("\n");
  }
  function ideaPrompt(reel) {
    var flds = {};
    $$("[data-ek]", reel).forEach(function (el) { flds[el.dataset.ek] = { role: label(el.dataset.ek), text: el.innerText.trim() }; });
    var chip = $(".reel-head .lb-chip.cat", reel), when = $(".when", reel);
    var others = $$("article.reel").filter(function (a) { return a !== reel; })
      .map(function (a) { var h = $(".hook-big", a); return h ? h.innerText.replace(/\s+/g, " ").trim() : ""; }).filter(Boolean);
    return [
      "אתה כותב ריל חדש לאינסטגרם של לומבוק (ספרי ילדים מותאמים אישית, ישראל). ירין, מנהל הסושיאל, לא אהב את הרעיון של הריל הזה ורוצה רעיון אחר לגמרי לאותו יום.",
      "",
      "הסדרה של הריל: " + (chip ? chip.innerText.trim() : "") + ". היום: " + (when ? when.innerText.replace(/\s+/g, " ").trim() : "") + ". הרעיון החדש נשאר בסדרה הזאת אבל עם זווית, פתיחה ומבנה אחרים. לא לנסח מחדש את הרעיון הישן.",
      "רעיונות של רילס אחרים בחודש, לא לחזור עליהם: " + others.join(" | "),
      "",
      "חוקים לכל טקסט שהורים רואים או שומעים (כותרת, קריינות, כרטיסיות, כיתוב):",
      "- עברית ישראלית יומיומית, כמו שירין מדבר עם הורה אחר. משפטים קצרים, פעלים לפני שמות עצם, בלי שפה של מותג או של מטפל.",
      "- בלי מקף מכל סוג (גם לא מקף עברי), בלי קו מפריד ארוך, בלי נקודה ופסיק. פסיק, נקודה, סימן שאלה וקריאה ומרכאות מותרים.",
      "- השם לומבוק בלבד, אף פעם לא לומיבוק. אף פעם לא להזכיר בינה מלאכותית. אף פעם לא \"קוד הנחה\" או \"קוד אישי\".",
      "- בלי עובדות חדשות. אף פעם לא להזכיר מחיר, סכום כסף, הנחה או מבצע. זמנים ותכונות רק מהעובדות כאן: " + CFG.facts + ". המבצע: " + CFG.offer + ".",
      "- לא לדבר על השפות של הספר ולא על העותק הדיגיטלי: הקהל ישראלי ודובר עברית.",
      "- כותרת: עד 8 מילים, שואלת או מסקרנת, ומתאימה לשנייה הראשונה. קריינות: כל השורות יחד בין " + CFG.vo_min + " ל " + CFG.vo_max + " מילים, שורה אחת לכל מחשבה, עד 12 מילים בשורה. הריל כולו בין 10 ל 30 שניות.",
      "- שורת הסיום של הקריינות קבועה ומתווספת לבד: \"" + CFG.cta_voice + "\". לא לכתוב אותה בשורות.",
      "- הכיתוב מסתיים תמיד בשורה הזאת, מילה במילה: " + CFG.cta_caption,
      "- אם בסוף הכיתוב יש הסתייגות רפואית, להשאיר אותה בדיוק כמו שהיא.",
      "- ירין חייב להופיע בריל: קטע פתיחה שלו למצלמה ו/או הקול שלו בקריינות. בלי שחקנים, בלי ילדים זרים, בלי טרנדים של אפליקציות.",
      "- מה שאפשר לצלם לבד ובזול: ירין מדבר למצלמה, הקלטת מסך של האתר וההזמנה, הספר המודפס, תצוגה מקדימה של ספר, צילום מלמעלה, הקלטה בטלפון.",
      "- הוראות הצילום ורשימת הצילום הן הערות פנימיות לירין, בעברית פשוטה, בגוף שני (\"אתה\"), ו\"אני\" זה Claude. ברשימת הצילום פריטים מופרדים בפסיקים, בלי פסיק בתוך פריט.",
      "",
      "צריך להחזיר ערך חדש לכל אחד מהמפתחות שכאן, ורק להם. אי אפשר להוסיף או למחוק מפתחות, וכל ערך חייב להיות לא ריק:",
      JSON.stringify(flds, null, 1),
      "",
      "תחזיר רק JSON בצורה הזאת, בלי שום טקסט אחר:",
      "{\"changes\": {\"<מפתח>\": \"<הטקסט החדש>\"}, \"summary\": \"משפט קצר בעברית: מה הרעיון החדש\"}"
    ].join("\n");
  }
  var askNew = $("#ask-new");
  function btnText(b, t) { var s = $("span", b); (s || b).textContent = t; }
  function setBusy(on, which) {
    /* which: "new" (רעיון חדש runs), "comment" (שליחה runs) or "make" (the reel is being made: both wait, the make sheet stops it) */
    var mk = on && which === "make";
    btnText(askGo, on && which !== "new" && !mk ? "עצירה" : "שליחה"); askGo.dataset.busy = on && !mk && which !== "new" ? "1" : ""; askT.disabled = on;
    btnText(askNew, on && which === "new" ? "עצירה" : "רעיון חדש"); askNew.dataset.busy = on && which === "new" ? "1" : "";
    askGo.disabled = mk || (on && which === "new"); askNew.disabled = mk || (on && which !== "new");
  }
  function apply(reel, changes) {
    var before = {}, keys = [];
    Object.keys(changes || {}).forEach(function (key) {
      var f = fields[key]; if (!f || !reel.contains(f.el)) return;
      var t = tidy(changes[key]); if (!t || t === f.el.innerText.trim()) return;
      before[key] = f.el.innerHTML; f.el.innerText = t;
      if (f.el.classList.contains("hook-big")) f.el.title = t;
      f.el.classList.add("is-changed"); (function (el) { setTimeout(function () { el.classList.remove("is-changed"); }, 2400); })(f.el);
      syncHook(key); save(key); keys.push(key);
    });
    return { before: before, keys: keys };
  }
  function undo(before) {
    Object.keys(before).forEach(function (key) { var f = fields[key]; if (!f) return; f.el.innerHTML = before[key]; syncHook(key); save(key); });
    msg("ביטלתי את השינוי.");
  }
  /* Background answers (Yarin, 07 Nov 2026: "if i click רעיון חדש and exit the tab i want it to continue in the bg and show
     me the process and let me do it for a couple of reels simultaneously"). Every ask (רעיון חדש and שליחה) is a job, one per
     reel, several reels at once. On the project server the job runs on the server (POST /api/sample/jobs, tools/lumebook.py
     SampleJobs): it goes on when the popup or the tab is closed, and its answer waits there until a page takes it and puts it
     into the reel, so it is applied the next time the page is open. On claude.ai the artifact's sample capability answers
     inside the page: several at once and the popup can close, but closing the tab stops them. The tray in the corner shows
     every job: queued, thinking, writing which field, done (open it, undo), failed. */
  var JOBS = {}, jobMode = null, jobTimer = null, ctlBy = {}, undoBy = {}, HEADJ = { "Content-Type": "application/json", "X-LumeBook-Board": "1" };
  function errText(c, which) {
    if (c === "cancelled") return which === "new" ? "עצרתי. הריל נשאר כמו שהיה." : "עצרתי. ההערה לא בוצעה.";
    if (c === "not_granted" || c === "sampling_disabled" || c === "not_declared" || c === "capability_disabled" || c === "capability_removed")
      return "אין אישור לשנות טקסט מכאן. אפשר לאשר בתפריט ההרשאות של העמוד.";
    if (c === "rate_limited") return "יותר מדי בקשות כרגע. נסה שוב עוד קצת.";
    if (c === "not_logged_in") return "Claude לא מחובר במחשב הזה. צריך להריץ פעם אחת במסוף: claude auth login";
    if (c === "no_cli") return "אין פקודת claude במחשב הזה, אז העמוד המקומי לא יכול לשאול את Claude.";
    if (c === "timeout") return "Claude לקח יותר מדי זמן. אפשר לשלוח שוב.";
    if (c === "invalid_json" || c === "empty_completion") return "לא הבנתי את התשובה. אפשר לנסות שוב.";
    if (c === "refused") return "את ההערה הזאת לא יכולתי לבצע. נסה לנסח אחרת.";
    if (c === "restarted") return "השרת המקומי הופעל מחדש באמצע. אפשר לנסות שוב.";
    if (c === "busy_reel") return "כבר יש בקשה שרצה לריל הזה.";
    if (c === "gone") return "הבקשה כבר לא קיימת.";
    if (c === "timeout" && which === "make") return "הבנייה לקחה יותר מ 30 דקות ונעצרה. מה שנוצר עד עכשיו נשאר בתיקייה.";
    if (c === "no_folder") return "לא הצלחתי לפתוח תיקייה לריל הזה.";
    if (c === "no_files") return "צריך לגרור לכאן את הקבצים של הריל קודם.";
    if (c === "bad_plan") return "התוכנית ש Claude כתב לא עברה בדיקה, אז לא בניתי כלום. אפשר לנסות שוב או לכתוב יותר מה הולך לאן.";
    if (c === "build_failed") return "הבנייה נעצרה.";
    return "משהו נכשל בדרך. אפשר לנסות שוב.";
  }
  function parseAnswer(t) {
    t = String(t || "").replace(/^\s*```(?:json)?\s*|\s*```\s*$/g, "").trim();
    var a = t.indexOf("{"), b = t.lastIndexOf("}");
    if (!t) { var e = new Error("empty"); e.code = "empty_completion"; throw e; }
    try { return JSON.parse(a >= 0 && b > a ? t.slice(a, b + 1) : t); } catch (x) { var e2 = new Error("json"); e2.code = "invalid_json"; throw e2; }
  }
  function running(j) { return j && (j.status === "queued" || j.status === "running"); }
  function jobFor(reelId) { var id = Object.keys(JOBS).filter(function (k) { return JOBS[k].reel === reelId && running(JOBS[k]); })[0]; return id ? JOBS[id] : null; }
  function clock(j) {
    var t0 = Date.parse(j.ran || j.started), t1 = j.ended ? Date.parse(j.ended) : Date.now(), s = Math.max(0, Math.round((t1 - t0) / 1000));
    return Math.floor(s / 60) + ":" + ("0" + (s % 60)).slice(-2);
  }
  function stepOf(j) {   // which field the answer is writing now, and how many of the reel's fields it has written
    var reel = document.getElementById(j.reel), total = reel ? $$("[data-ek]", reel).length : 0;
    var keys = [], m, re = /"(r[\w-]+__[a-z]+(?:__\d+)?)"\s*:/g, out = j.out || "";
    while ((m = re.exec(out))) if (keys.indexOf(m[1]) < 0) keys.push(m[1]);
    return { field: keys.length ? label(keys[keys.length - 1]) : "", done: keys.length, total: total };
  }
  function stateText(j) {
    if (j.status === "queued") return j.kind === "make" ? "מחכה בתור, ריל אחר נוצר עכשיו" : "מחכה בתור";
    if (running(j) && j.kind === "make") return (j.steps ? "שלב " + j.steps + ": " : "") + (j.step || "מתחיל לעבוד");
    if (running(j)) { var st = stepOf(j); return j.stage === "writing" ? (st.field ? "כותב: " + st.field : "מתחיל לכתוב") : "חושב"; }
    if (j.status === "done") return j.applied ? (j.summary || "הוכנס לריל") : "מוכן";
    if (j.status === "cancelled") return "נעצר";
    return errText(j.code, j.kind);
  }
  function hookOf(reelId) { var r = document.getElementById(reelId), h = r && $(".hook-big", r); return h ? h.innerText.replace(/\s+/g, " ").trim() : reelId; }
  function pidOf(reelId) { var c = $('.lb-day[data-k="' + reelId + '"] .lb-pid'); return c ? c.textContent : reelId.slice(1).replace("-", "."); }

  /* the tray */
  var tray = document.createElement("aside");
  tray.className = "jobs lb-glass is-thick"; tray.id = "jobs"; tray.hidden = true; tray.setAttribute("aria-label", "בקשות ל Claude");
  tray.innerHTML = '<div class="jobs-head"><span class="jobs-title" role="status" aria-live="polite"></span>' +
    '<button type="button" class="lb-btn secondary sm" data-jobs-fold aria-expanded="true">הסתרה</button></div><div class="jobs-list"></div><p class="jobs-note"></p>';
  document.body.appendChild(tray);
  var trayFolded = false;
  $("[data-jobs-fold]", tray).addEventListener("click", function () {
    trayFolded = !trayFolded; tray.classList.toggle("is-folded", trayFolded);
    this.textContent = trayFolded ? "הצגה" : "הסתרה"; this.setAttribute("aria-expanded", String(!trayFolded));
  });
  function render() {
    var list = Object.keys(JOBS).map(function (k) { return JOBS[k]; }).sort(function (a, b) { return String(a.started).localeCompare(String(b.started)); });
    tray.hidden = !list.length;
    var live = list.filter(running).length;
    $(".jobs-title", tray).textContent = live ? "Claude עובד על " + live + (live === 1 ? " ריל" : " רילס") : "בקשות ל Claude";
    $(".jobs-note", tray).textContent = live && jobMode === "page" ? "ב claude.ai זה ממשיך כל עוד הלשונית פתוחה." : live ? "אפשר לסגור את הלשונית, זה ממשיך ברקע." : "";
    $(".jobs-list", tray).innerHTML = list.map(function (j) {
      var st = stepOf(j), pct = j.status === "done" ? 100 : running(j) && j.kind === "new" && st.total ? Math.min(95, Math.round(100 * st.done / st.total)) : 0;
      var bad = j.status === "failed", btns = '<button type="button" class="lb-btn secondary sm" data-job-open="' + j.reel + '">פתיחה</button>';
      if (running(j)) btns += '<button type="button" class="lb-btn secondary sm" data-job-stop="' + j.id + '">עצירה</button>';
      else {
        if (undoBy[j.id]) btns += '<button type="button" class="lb-btn secondary sm" data-job-undo="' + j.id + '">ביטול השינוי</button>';
        btns += '<button type="button" class="lb-btn secondary sm" data-job-x="' + j.id + '" aria-label="הסרה מהרשימה">✕</button>';
      }
      return '<div class="job' + (bad ? " is-bad" : "") + '"><div class="job-top"><span class="lb-pid">' + esc(pidOf(j.reel)) + '</span><span class="job-hook">' + esc(j.label || hookOf(j.reel)) + '</span>' +
        '<span class="job-kind">' + (j.kind === "new" ? "רעיון חדש" : j.kind === "make" ? "יצירת ריל" : "הערה") + '</span></div>' +
        '<div class="job-st">' + (running(j) ? '<span class="lb-spinner" aria-hidden="true"></span>' : "") + '<span>' + esc(stateText(j)) + '</span><span class="job-t">' + clock(j) + '</span></div>' +
        (running(j) || j.status === "done" ? '<div class="job-bar' + (running(j) && !pct ? " is-wait" : "") + '"><i style="width:' + pct + '%"></i></div>' : "") +
        '<div class="job-act">' + btns + '</div></div>';
    }).join("");
    paintCells(); paintAsk(); if (cur) paintMake(cur);
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function paintCells() {
    $$(".lb-day[data-k]").forEach(function (c) {
      var j = jobFor(c.dataset.k); c.classList.toggle("is-busy", !!j);
      var dot = $(".job-dot", c);
      if (j && !dot) { dot = document.createElement("span"); dot.className = "job-dot lb-spinner"; dot.title = "Claude עובד על הריל הזה"; var top = $(".lb-day-top", c); if (top) top.insertBefore(dot, $(".lb-pid", top)); else c.appendChild(dot); }
      if (!j && dot) dot.remove();
    });
  }
  window.CalJobsPaint = paintCells;
  function paintAsk() {
    if (!cur) return;
    var j = jobFor(cur.id);
    if (j && j.kind === "make") { setBusy(true, "make"); msg("Claude יוצר עכשיו את הריל הזה. אפשר לשנות את הטקסט כשהוא יסיים."); }
    else if (j) { setBusy(true, j.kind); msg((j.kind === "new" ? "רעיון חדש: " : "") + stateText(j) + " (" + clock(j) + "). אפשר לסגור, זה ממשיך ברקע."); }
    else if (askGo.dataset.busy || askNew.dataset.busy) setBusy(false);
  }
  tray.addEventListener("click", function (ev) {
    var t = ev.target.closest("button"); if (!t) return;
    if (t.dataset.jobOpen) openReel(t.dataset.jobOpen);
    else if (t.dataset.jobStop) stopJob(t.dataset.jobStop);
    else if (t.dataset.jobUndo) { undo(undoBy[t.dataset.jobUndo]); delete undoBy[t.dataset.jobUndo]; JOBS[t.dataset.jobUndo].summary = "השינוי בוטל"; render(); }
    else if (t.dataset.jobX) dismissJob(t.dataset.jobX);
  });

  /* finishing: put the answer into its reel (also when the popup is closed or another reel is open) */
  function finish(j, res) {
    var reel = document.getElementById(j.reel);
    if (!reel) { j.summary = "הריל לא נמצא בעמוד"; return; }
    var r = apply(reel, res && res.changes), sum = res && res.summary ? String(res.summary).replace(/[.\s]+$/, "") : "";
    j.applied = true;
    if (!r.keys.length) { j.summary = sum || "לא היה מה לשנות"; return; }
    j.summary = (sum || "שיניתי " + r.keys.length + " טקסטים") + ".";
    undoBy[j.id] = r.before;
    if (cur === reel) {
      setBusy(false); if (j.kind !== "new" && askT.value.trim() === (j.comment || "").trim()) askT.value = "";
      askMsg.classList.remove("is-error"); askMsg.textContent = j.summary;
      var u = document.createElement("button"); u.type = "button"; u.textContent = "ביטול";
      u.addEventListener("click", function () { undo(r.before); delete undoBy[j.id]; j.summary = "השינוי בוטל"; render(); }); askMsg.appendChild(u);
    }
    if (reqStore) reqStore.add({ reel: reel.id, comment: j.comment || "רעיון חדש", kind: j.kind, summary: sum, keys: r.keys, at: new Date().toISOString() }).catch(function () {});
  }
  function startJob(reel, text, which, comment) {
    if (jobFor(reel.id)) { msg(errText("busy_reel"), true); return; }
    var meta = { reel: reel.id, kind: which, label: hookOf(reel.id), comment: comment };
    if (jobMode === "server") {
      setBusy(true, which); msg("שולח...");
      fetch("/api/sample/jobs", { method: "POST", headers: HEADJ, body: JSON.stringify(Object.assign({ prompt: text }, meta)) })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (b) { if (!r.ok) { var x = new Error(b.error); x.code = b.code || "failed"; throw x; } return b.job; }); })
        .then(function (job) { JOBS[job.id] = job; render(); poll(); }, function (x) { setBusy(false); msg(errText(x.code, which), true); });
      return;
    }
    var id = "p" + Date.now().toString(36), ctl = new AbortController();
    var j = JOBS[id] = Object.assign({ id: id, status: "running", stage: "thinking", started: new Date().toISOString() }, meta);
    ctlBy[id] = ctl; render(); tick();
    sampleFn.json(text, { signal: ctl.signal, cache: false }).then(function (res) {
      j.status = "done"; j.ended = new Date().toISOString(); finish(j, res);
    }, function (x) {
      var c = x && x.code; j.status = c === "cancelled" ? "cancelled" : "failed"; j.code = c; j.ended = new Date().toISOString();
      if (c === "not_granted" || c === "sampling_disabled" || c === "not_declared" || c === "capability_disabled" || c === "capability_removed") sampleFn = null;
      if (cur && cur.id === j.reel) { setBusy(false); msg(errText(c, j.kind), c !== "cancelled"); }
    }).then(function () { delete ctlBy[id]; render(); });
  }
  function stopJob(id) {
    if (ctlBy[id]) { ctlBy[id].abort(); return; }
    fetch("/api/sample/jobs/" + id + "/cancel", { method: "POST", headers: HEADJ }).then(function () { poll(); }, function () {});
  }
  function dismissJob(id) {
    delete undoBy[id];
    if (jobMode === "server" && id.charAt(0) !== "p") fetch("/api/sample/jobs/" + id + "/dismiss", { method: "POST", headers: HEADJ }).catch(function () {});
    delete JOBS[id]; render();
  }
  /* server jobs: read the list, take every finished answer nobody took yet */
  var polling = false;
  function poll() {
    if (jobMode !== "server" || polling) return;
    polling = true; clearTimeout(jobTimer);
    fetch("/api/sample/jobs", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : { jobs: [] }; }).then(function (b) {
      var seen = {};
      (b.jobs || []).forEach(function (sj) {
        seen[sj.id] = 1;
        var j = JOBS[sj.id];
        if (j && j.applied) return;   // ours, already in the reel
        if (sj.claimed && !j) return; // another tab or an earlier visit put it in; nothing left to show
        JOBS[sj.id] = j = Object.assign(j || {}, sj);
        if (j.status === "done" && !j.claimed && !j.taking) {
          j.taking = true;
          fetch("/api/sample/jobs/" + j.id + "/claim", { method: "POST", headers: HEADJ }).then(function (r) {
            if (!r.ok) { delete JOBS[j.id]; return; }
            if (j.kind === "make") { finishMake(j); return; }
            try { finish(j, parseAnswer(j.text)); } catch (x) { j.status = "failed"; j.code = x.code || "invalid_json"; if (cur && cur.id === j.reel) setBusy(false); }
          }).then(render, render);
        } else if (j.kind === "make" && j.status !== "done" && !running(j) && !j.told) {
          j.told = true;
          mkNote[j.reel] = { text: errText(j.code, "make") + (j.error && (j.code === "build_failed" || j.code === "bad_plan") ? " (" + j.error + ")" : ""), err: j.status !== "cancelled" };
          var mr = document.getElementById(j.reel); if (mr) loadFiles(mr);
        } else if (j.status !== "done" && !running(j) && cur && cur.id === j.reel && !j.told) { j.told = true; setBusy(false); msg(errText(j.code, j.kind), j.status !== "cancelled"); }
      });
      Object.keys(JOBS).forEach(function (k) { if (!seen[k] && k.charAt(0) !== "p" && !JOBS[k].applied) delete JOBS[k]; });
      render();
    }, function () {}).then(function () {
      polling = false;
      var live = Object.keys(JOBS).some(function (k) { return running(JOBS[k]); });
      if (live) jobTimer = setTimeout(poll, 1200);
    });
  }
  function tick() {   // the clock of in-page jobs (claude.ai)
    if (Object.keys(JOBS).some(function (k) { return running(JOBS[k]); })) { render(); setTimeout(tick, 1000); }
  }
  document.addEventListener("visibilitychange", function () { if (!document.hidden) poll(); });

  function canRun(what) {
    if (!sampleFn && jobMode !== "server") {
      msg(what + " עובד רק כשהעמוד פתוח ב claude.ai. ", true);
      if (CFG.artifact && !window.claude) {   /* opened somewhere without the project server: link to the claude.ai copy */
        var a = document.createElement("a"); a.href = CFG.artifact; a.target = "_blank"; a.rel = "noopener"; a.textContent = "לפתיחה שם";
        askMsg.appendChild(a);
      }
      return false;
    }
    if (readOnly) { msg("העמוד פתוח לקריאה בלבד.", true); return false; }
    return true;
  }
  ask.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var reel = cur, j = reel && jobFor(reel.id);
    if (j) { if (j.kind !== "make") stopJob(j.id); return; }
    var comment = askT.value.trim();
    if (!comment || !reel || !canRun("השינוי לפי הערה")) return;
    startJob(reel, prompt(reel, comment), "comment", comment);
  });
  askNew.addEventListener("click", function () {
    var reel = cur, j = reel && jobFor(reel.id);
    if (j) { if (j.kind !== "make") stopJob(j.id); return; }
    if (!reel || !canRun("רעיון חדש")) return;
    startJob(reel, ideaPrompt(reel), "new", "רעיון חדש");
  });
  askT.addEventListener("keydown", function (ev) { if (ev.key === "Enter" && (ev.metaKey || ev.ctrlKey)) { ev.preventDefault(); ask.requestSubmit(); } });
  dlg.addEventListener("close", function () { msg(""); setBusy(false); });   // a running job goes on; the tray shows it
  /* On claude.ai the ask buttons use the artifact's sample capability. On the project server there is no claude.ai, so
     POST /api/sample (tools/lumebook.py, the claude command of this Mac) answers instead; this wrapper looks like the
     artifact's sample function: a call, call.json, and errors with a .code the handlers below already know. */
  function localSample() {
    function fail(code, text) { var e = new Error(text || code); e.code = code; return e; }
    function call(input, opts) {
      var text = typeof input === "string" ? input : (input || []).map(function (m) { return m.content; }).join("\n\n");
      return fetch("/api/sample", { method: "POST", headers: { "Content-Type": "application/json", "X-LumeBook-Board": "1" },
        body: JSON.stringify({ prompt: text }), signal: opts && opts.signal }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) {
          if (!r.ok) throw fail(j.code || "failed", j.error);
          return { text: j.text || "", truncated: false };
        });
      }, function (x) { throw x && x.name === "AbortError" ? fail("cancelled") : fail("failed", x && x.message); });
    }
    call.json = function (input, opts) {
      return call(input, opts).then(function (r) {
        var t = r.text.replace(/^\s*```(?:json)?\s*|\s*```\s*$/g, "").trim(), a = t.indexOf("{"), b = t.lastIndexOf("}");
        if (!t) throw fail("empty_completion");
        try { return JSON.parse(a >= 0 && b > a ? t.slice(a, b + 1) : t); } catch (x) { throw fail("invalid_json"); }
      });
    };
    return call;
  }
  if (window.claude && claude.use) claude.use("sample").then(function (fn) { sampleFn = fn || null; if (fn) jobMode = "page"; }, function () {});
  else projectServer().then(function (ok) { if (ok) { sampleFn = localSample(); jobMode = "server"; poll(); } });

  /* Making the reel (Yarin, 07 Nov 2026: "a full file dropping and a prompt text box to the reel cards so i could let you create
     the reel through there"). On the project server every reel card has a make sheet. Files dropped anywhere on the open card, on a
     day of the month, or picked in the drop zone upload into the reel's media folder (POST /api/reel-files; the first one opens the
     folder with reels.py new) and show as tiles (✕ moves one to _to-delete). The prompt and ליצור את הריל start a reel job (POST
     /api/reel-make/jobs, tools/lumebook.py): Claude Code with tools, in the project folder, makes the video the reel_make.py way, in
     the background, one reel at a time. The tray and the sheet show each step; the newest file in final/ plays on the card. On
     claude.ai and Vercel the sheet only says where it works. */
  var MK = null, mkFiles = {}, mkUp = {}, mkNote = {}, mkSel = {}, upSeq = 0, upActive = 0, ICO = CFG.icons || {};
  var OKX = /\.(mp4|mov|m4v|webm|mkv|png|jpe?g|webp|gif|heic|mp3|m4a|wav|ogg|opus|aac|pdf)$/i, KIND_HE = { video: "סרטון", image: "תמונה", audio: "הקלטה", file: "קובץ" };
  function mkSec(reel) { return reel ? $(".make", reel) : null; }
  function kindOf(n) {
    var x = String(n).split(".").pop().toLowerCase();
    return /^(mp4|mov|m4v|webm|mkv)$/.test(x) ? "video" : /^(png|jpe?g|webp|gif|heic)$/.test(x) ? "image" : /^(mp3|m4a|wav|ogg|opus|aac)$/.test(x) ? "audio" : "file";
  }
  function mkSize(b) { return b >= 1e9 ? (b / 1e9).toFixed(1) + " GB" : b >= 1e6 ? Math.round(b / 1e6) + " MB" : Math.max(1, Math.round(b / 1e3)) + " KB"; }
  function mkWhen(t) { var d = new Date(t * 1000), p = function (n) { return ("0" + n).slice(-2); }; return p(d.getDate()) + " / " + p(d.getMonth() + 1) + ", " + p(d.getHours()) + ":" + p(d.getMinutes()); }
  function tileHtml(f) {
    var k = f.kind || kindOf(f.name), src = f.src || f.url || "", th;
    if (src && k === "image") th = '<a class="lb-file-th" href="' + esc(src) + '" target="_blank" rel="noopener" tabindex="-1"><img src="' + esc(src) + '" alt="" loading="lazy"></a>';
    else if (src && k === "video") th = '<a class="lb-file-th" href="' + esc(src) + '" target="_blank" rel="noopener" tabindex="-1"><video src="' + esc(src) + '#t=0.3" muted playsinline preload="metadata"></video><span class="lb-file-dur"></span></a>';
    else th = '<span class="lb-file-th">' + (ICO[k] || ICO.file || "") + '</span>';
    var sub = f.bad || (f.up ? "מעלה, " + mkSize(f.size) : KIND_HE[k] + ", " + mkSize(f.size));
    return '<li class="lb-file' + (f.up ? " is-up" : "") + (f.bad ? " is-bad" : "") + '" ' + (f.id ? 'data-up="' + f.id + '"' : 'data-rf="' + esc(f.path) + '"') + ' style="--p:' + (f.p || 0).toFixed(3) + '">' + th +
      '<button type="button" class="lb-file-x" aria-label="' + (f.up ? "ביטול ההעלאה של " : "הסרה של ") + esc(f.name) + '">' + (ICO.close || "✕") + '</button>' +
      '<span class="lb-file-meta"><span class="lb-file-n" title="' + esc(f.name) + '">' + esc(f.name) + '</span><span class="lb-file-s">' + esc(sub) + '</span></span>' +
      '<span class="lb-file-bar"><i></i></span></li>';
  }
  function paintFiles(reel) {
    var s = mkSec(reel); if (!s) return;
    var b = mkFiles[reel.id] || { files: [], finals: [] }, ups = mkUp[reel.id] || {}, ul = $(".make-files", s);
    ul.innerHTML = b.files.concat(Object.keys(ups).map(function (k) { return ups[k]; })).map(tileHtml).join("");
    $$("video", ul).forEach(function (v) {
      var li = v.closest(".lb-file");
      v.addEventListener("loadedmetadata", function () { var d = $(".lb-file-dur", li); if (d && isFinite(v.duration)) d.textContent = mmss(v.duration); });
      li.addEventListener("mouseenter", function () { var p = v.play(); if (p && p.catch) p.catch(function () {}); });
      li.addEventListener("mouseleave", function () { v.pause(); try { v.currentTime = 0.3; } catch (x) {} });
    });
    $$("img", ul).forEach(function (im) { im.addEventListener("error", function () { var a = im.parentNode; a.outerHTML = '<span class="lb-file-th">' + (ICO.image || "") + '</span>'; }); });
    paintFinal(reel); paintMake(reel);
  }
  function paintFinal(reel) {
    var s = mkSec(reel), box = s && $(".make-final", s), fin = ((mkFiles[reel.id] || {}).finals) || []; if (!box) return;
    if (!fin.length) { box.hidden = true; box.innerHTML = ""; box.dataset.src = ""; return; }
    var pick = fin.filter(function (f) { return f.path === mkSel[reel.id]; })[0] || fin[0], key = pick.url + "|" + pick.mtime + "|" + fin.length;
    box.hidden = false;
    if (box.dataset.src === key) return;   // the same file: leave the player alone (it may be playing)
    box.dataset.src = key;
    var vers = fin.length > 1 ? '<div class="make-vers">' + fin.map(function (f) {
      return '<button type="button" class="lb-chip" data-ver="' + esc(f.path) + '" aria-pressed="' + (f === pick) + '">' + esc(f.name.replace(/\.mp4$/i, "")) + '</button>'; }).join("") + '</div>' : "";
    box.innerHTML = '<video controls playsinline preload="metadata" src="' + esc(pick.url) + '"></video><div class="make-final-info"><b>הריל המוכן</b>' +
      '<span class="n">' + esc(pick.name) + ', ' + mkWhen(pick.mtime) + ', ' + mkSize(pick.size) + '</span><div class="make-final-acts">' +
      '<a class="lb-btn secondary sm" href="' + esc(pick.url) + '" download="' + esc(pick.name) + '">' + (ICO.download || "") + '<span>הורדה</span></a>' +
      '<a class="lb-btn secondary sm" href="' + esc(pick.url) + '" target="_blank" rel="noopener">' + (ICO.open || "") + '<span>פתיחה בלשונית</span></a></div>' + vers + '</div>';
  }
  function mkMsg(s, html, err) { var m = $(".make-msg", s); if (m.innerHTML !== html) m.innerHTML = html; m.classList.toggle("is-error", !!err); }
  function paintMake(reel) {
    var s = mkSec(reel); if (!s || MK !== "server") return;
    var j = jobFor(reel.id), go = $(".make-go", s), ta = $("textarea", s), b = mkFiles[reel.id] || { files: [], finals: [] }, ups = mkUp[reel.id] || {};
    var nUp = Object.keys(ups).filter(function (k) { return ups[k].up; }).length, nf = b.files.length, nr = b.finals.length;
    $(".make-sum", s).textContent = nf || nr ? (nf ? nf + (nf === 1 ? " קובץ" : " קבצים") : "") + (nf && nr ? ", " : "") + (nr ? nr + (nr === 1 ? " ריל מוכן" : " רילס מוכנים") : "") : "";
    var note = nUp ? esc("מעלה " + (nUp === 1 ? "קובץ אחד" : nUp + " קבצים") + "...") : b.project ? "<bdi>" + esc(b.project.split("/").pop()) + "</bdi>" : "";
    if ($(".make-note", s).innerHTML !== note) $(".make-note", s).innerHTML = note;   // bdi: the folder name keeps its order inside the Hebrew bar
    if (j && j.kind === "make") {
      btnText(go, "עצירה"); go.dataset.busy = "1"; go.disabled = false; ta.disabled = true;
      mkMsg(s, '<span class="lb-spinner" aria-hidden="true"></span><span>' + esc(stateText(j)) + '</span><span class="t">' + clock(j) + '</span>');
      return;
    }
    btnText(go, nr ? "ליצור שוב" : "ליצור את הריל"); go.dataset.busy = ""; ta.disabled = false; go.disabled = !!j || readOnly;
    var n = j ? { text: "מחכה שהשינוי בטקסט של הריל יסתיים." } : mkNote[reel.id];
    mkMsg(s, n ? '<span>' + esc(n.text) + '</span>' : "", n && n.err);
  }
  function loadFiles(reel) {
    if (MK !== "server" || !reel) return;
    fetch("/api/reel-files?reel=" + encodeURIComponent(reel.id), { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (b) { if (b) { mkFiles[reel.id] = b; paintFiles(reel); } }, function () {});
  }
  function upload(reel, list) {
    if (MK !== "server" || !reel || readOnly) return;
    var all = Array.prototype.slice.call(list || []), ok = all.filter(function (f) { return f.size > 0 && OKX.test(f.name); }), skip = all.length - ok.length;
    var q = mkUp[reel.id] || (mkUp[reel.id] = {});
    ok.forEach(function (f) {
      var id = "u" + (++upSeq), k = kindOf(f.name);
      q[id] = { id: id, name: f.name, size: f.size, kind: k, src: k === "video" || k === "image" ? URL.createObjectURL(f) : "", p: 0, up: true, file: f, reel: reel.id };
    });
    if (skip) mkNote[reel.id] = { text: (skip === 1 ? "קובץ אחד לא נכנס" : skip + " קבצים לא נכנסו") + ": רק סרטונים, הקלטות, תמונות ו PDF.", err: true };
    else if (ok.length) mkNote[reel.id] = null;
    paintFiles(reel); pump();
  }
  function pump() {   // two uploads at a time, in the order they were dropped
    while (upActive < 2) {
      var next = null;
      Object.keys(mkUp).some(function (r) { return Object.keys(mkUp[r]).some(function (k) { var u = mkUp[r][k]; if (u.up && !u.xhr) { next = u; return true; } return false; }); });
      if (!next) return;
      send(next);
    }
  }
  function send(u) {
    var x = new XMLHttpRequest(); u.xhr = x; upActive++;
    x.open("POST", "/api/reel-files?reel=" + encodeURIComponent(u.reel) + "&name=" + encodeURIComponent(u.name));
    x.setRequestHeader("X-LumeBook-Board", "1"); x.setRequestHeader("Content-Type", "application/octet-stream");
    x.upload.onprogress = function (e) {
      if (!e.lengthComputable) return; u.p = e.loaded / e.total;
      var el = $('[data-up="' + u.id + '"]'); if (el) el.style.setProperty("--p", u.p.toFixed(3));
    };
    x.onloadend = function () {
      upActive--;
      var body = {}; try { body = JSON.parse(x.responseText || "{}"); } catch (e) {}
      if (x.status >= 200 && x.status < 300 && body.file) {
        delete mkUp[u.reel][u.id]; if (u.src) URL.revokeObjectURL(u.src);
        var b = mkFiles[u.reel] || (mkFiles[u.reel] = { files: [], finals: [] });
        b.files = b.files.filter(function (f) { return f.path !== body.file.path; }).concat([body.file]); if (body.project) b.project = body.project;
      } else if (u.cancelled) { delete mkUp[u.reel][u.id]; if (u.src) URL.revokeObjectURL(u.src); }
      else { u.up = false; u.bad = x.status === 413 ? "גדול מדי" : x.status === 415 ? "סוג קובץ שלא נתמך" : x.status === 0 ? "ההעלאה נקטעה" : "ההעלאה נכשלה"; }
      var r = document.getElementById(u.reel); if (r) paintFiles(r);
      pump();
    };
    x.send(u.file);
  }
  function removeFile(reel, path) {
    fetch("/api/reel-files/remove?reel=" + encodeURIComponent(reel.id) + "&f=" + encodeURIComponent(path), { method: "POST", headers: HEADJ })
      .then(function (r) { if (!r.ok) throw new Error("remove"); })
      .then(function () {
        var b = mkFiles[reel.id]; if (b) b.files = b.files.filter(function (f) { return f.path !== path; });
        mkNote[reel.id] = { text: "הקובץ עבר ל _to-delete, אפשר להחזיר אותו משם." }; paintFiles(reel);
      }, function () { mkNote[reel.id] = { text: "לא הצלחתי להסיר את הקובץ.", err: true }; paintMake(reel); });
  }
  function makeGo(reel) {
    if (!reel || MK !== "server") return;
    var j = jobFor(reel.id), s = mkSec(reel);
    if (j) { if (j.kind === "make") stopJob(j.id); return; }
    if (readOnly) { mkNote[reel.id] = { text: "העמוד פתוח לקריאה בלבד.", err: true }; paintMake(reel); return; }
    var text = $("textarea", s).value.trim(), b = mkFiles[reel.id] || { files: [] }, ups = mkUp[reel.id] || {};
    if (Object.keys(ups).some(function (k) { return ups[k].up; })) { mkNote[reel.id] = { text: "רגע, הקבצים עוד עולים. אפשר ללחוץ שוב כשהם יסיימו." }; paintMake(reel); return; }
    if (!b.files.length) { mkNote[reel.id] = { text: "צריך לגרור לכאן את הקבצים של הריל קודם.", err: true }; paintMake(reel); return; }
    flush();   // the script Claude gets is the one on the screen, edits included
    var script = {};
    $$("[data-ek]", reel).forEach(function (el) {
      var m = el.dataset.ek.split("__"), t = el.innerText.trim();
      if (m.length > 2) (script[m[1]] = script[m[1]] || [])[Number(m[2])] = t; else script[m[1]] = t;
    });
    mkNote[reel.id] = null; $(".make-go", s).disabled = true;
    fetch("/api/reel-make/jobs", { method: "POST", headers: HEADJ, body: JSON.stringify({ reel: reel.id, prompt: text, script: script, label: hookOf(reel.id) }) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (x) { if (!r.ok) { var e = new Error(x.error); e.code = x.code || "failed"; throw e; } return x.job; }); })
      .then(function (job) { JOBS[job.id] = job; render(); poll(); }, function (x) { mkNote[reel.id] = { text: errText(x.code, "make"), err: true }; paintMake(reel); });
  }
  function finishMake(j) {
    j.applied = true;
    var t = String(j.text || "").trim().split(/\n\s*\n/).pop().replace(/\s+/g, " ").trim();
    j.summary = t ? t.slice(0, 400) : "הריל מוכן.";
    mkNote[j.reel] = { text: j.summary + (j.checks && j.checks.length ? " לבדוק: " + j.checks.join(" | ") : "") };
    var reel = document.getElementById(j.reel); if (reel) loadFiles(reel);
    if (reqStore) reqStore.add({ reel: j.reel, comment: j.comment || "", kind: "make", summary: j.summary, keys: [], at: new Date().toISOString() }).catch(function () {});
  }
  function makeOpen(reel) {
    var s = mkSec(reel); if (!s || !MK) return;
    s.classList.toggle("is-off", MK !== "server");
    if (MK === "server") { paintMake(reel); loadFiles(reel); }
  }
  document.addEventListener("change", function (ev) {
    var inp = ev.target.closest && ev.target.closest(".make-drop input[type=file]"); if (!inp) return;
    upload(inp.closest(".reel"), inp.files); inp.value = "";
  });
  document.addEventListener("click", function (ev) {
    var t = ev.target.closest && ev.target.closest(".make .lb-file-x, .make-go, .make-vers [data-ver]"), reel = t && t.closest(".reel"); if (!reel) return;
    if (t.classList.contains("make-go")) { makeGo(reel); return; }
    if (t.dataset.ver) { mkSel[reel.id] = t.dataset.ver; paintFinal(reel); return; }
    var li = t.closest(".lb-file");
    if (li.dataset.up) {
      var u = (mkUp[reel.id] || {})[li.dataset.up]; if (!u) return;
      if (u.xhr && u.up) { u.cancelled = true; u.xhr.abort(); } else { delete mkUp[reel.id][u.id]; if (u.src) URL.revokeObjectURL(u.src); paintFiles(reel); }
      return;
    }
    removeFile(reel, li.dataset.rf);   // data-rf, not data-f: the hub's filter chips own [data-f]
  });
  document.addEventListener("keydown", function (ev) {
    var ta = ev.key === "Enter" && (ev.metaKey || ev.ctrlKey) && ev.target.closest && ev.target.closest(".make-comp textarea");
    if (ta) { ev.preventDefault(); makeGo(ta.closest(".reel")); }
  });
  /* dropping: anywhere on the open card (a veil over its visible part says which reel), or on a day of the month (it opens) */
  var veil = document.createElement("div"), dragN = 0;
  veil.className = "lb-drop-veil"; veil.setAttribute("aria-hidden", "true");
  veil.innerHTML = (ICO.upload || "") + "<span>משחררים, והקבצים נכנסים לריל</span><small></small>";
  dlg.appendChild(veil);
  function hasFiles(ev) { var t = ev.dataTransfer && ev.dataTransfer.types; return !!t && Array.prototype.indexOf.call(t, "Files") >= 0; }
  function veilOn(on) {
    var s = mkSec(cur), dz = s && $(".make-drop", s); if (dz) dz.classList.toggle("is-over", on);
    if (!on || !cur) { veil.classList.remove("is-on"); return; }
    var r = $(".lb-dialog-card", dlg).getBoundingClientRect(), top = Math.max(r.top, 0) + 8, bot = Math.min(r.bottom, innerHeight) - 8;
    veil.style.left = (r.left + 8) + "px"; veil.style.width = (r.width - 16) + "px"; veil.style.top = top + "px"; veil.style.height = Math.max(96, bot - top) + "px";
    $("small", veil).textContent = "ריל " + pidOf(cur.id) + ": " + hookOf(cur.id);
    veil.classList.add("is-on");
  }
  dlg.addEventListener("dragenter", function (ev) { if (!hasFiles(ev) || !cur || MK !== "server") return; ev.preventDefault(); if (dragN++ === 0) veilOn(true); });
  dlg.addEventListener("dragover", function (ev) { if (!hasFiles(ev)) return; ev.preventDefault(); ev.dataTransfer.dropEffect = cur && MK === "server" ? "copy" : "none"; });
  dlg.addEventListener("dragleave", function (ev) { if (!hasFiles(ev) || !dragN) return; if (--dragN === 0) veilOn(false); });
  dlg.addEventListener("drop", function (ev) { if (!hasFiles(ev)) return; ev.preventDefault(); dragN = 0; veilOn(false); if (cur && MK === "server") upload(cur, ev.dataTransfer.files); });
  document.addEventListener("dragover", function (ev) {   /* next to a docked drawer the days take drops too; the drawer keeps its own */
    if (!hasFiles(ev) || (dlg.open && !docked) || dlg.contains(ev.target)) return;
    var c = ev.target.closest && ev.target.closest("a.lb-day[data-k]");
    $$(".lb-day.is-drop").forEach(function (x) { if (x !== c) x.classList.remove("is-drop"); });
    ev.preventDefault();   // a file let go off a day never opens in the tab instead of the page
    ev.dataTransfer.dropEffect = c && MK === "server" ? "copy" : "none";
    if (c && MK === "server") c.classList.add("is-drop");
  });
  document.addEventListener("dragleave", function (ev) { var c = ev.target.closest && ev.target.closest(".lb-day.is-drop"); if (c && !c.contains(ev.relatedTarget)) c.classList.remove("is-drop"); });
  document.addEventListener("drop", function (ev) {
    if (!hasFiles(ev) || (dlg.open && !docked) || dlg.contains(ev.target)) return;
    ev.preventDefault();
    var c = ev.target.closest && ev.target.closest("a.lb-day[data-k]"), files = ev.dataTransfer.files;
    $$(".lb-day.is-drop").forEach(function (x) { x.classList.remove("is-drop"); });
    if (!c || MK !== "server") return;
    openReel(c.dataset.k); upload(document.getElementById(c.dataset.k), files);
  });
  if (window.claude && claude.use) { MK = "off"; if (cur) makeOpen(cur); }
  else projectServer().then(function (ok) { MK = ok ? "server" : "off"; if (cur) makeOpen(cur); });

  /* toolbar */
  var tb = $("#tb"), lastRange = null, lastEl = null;
  document.addEventListener("selectionchange", function () {
    var s = getSelection(); if (!s.rangeCount) return;
    var n = s.anchorNode; var el = n && (n.nodeType === 1 ? n : n.parentElement); el = el && el.closest("[data-ek]");
    if (el) { lastRange = s.getRangeAt(0).cloneRange(); lastEl = el; tb.classList.add("is-on"); }
    else if (!tb.contains(document.activeElement)) tb.classList.remove("is-on");
  });
  function restore() {
    if (!lastRange || !lastEl) return false;
    lastEl.focus({ preventScroll: true }); var s = getSelection(); s.removeAllRanges(); s.addRange(lastRange); return true;
  }
  function touched() { if (lastEl) lastEl.dispatchEvent(new Event("input", { bubbles: true })); }
  try { document.execCommand("styleWithCSS", false, true); } catch (x) {}
  $$("button[data-cmd]", tb).forEach(function (b) {
    b.addEventListener("mousedown", function (ev) { ev.preventDefault(); });
    b.addEventListener("click", function () {
      if (!restore()) return;
      var c = b.dataset.cmd;
      if (c === "link") {
        var inp = $("#tb-link"); inp.hidden = false; inp.value = "https://"; inp.focus(); inp.select(); return;
      }
      if (c === "dir") { var cur = lastEl.getAttribute("dir"); lastEl.setAttribute("dir", cur === "ltr" ? "rtl" : "ltr"); touched(); return; }
      document.execCommand(c, false, null); touched();
    });
  });
  var linkIn = $("#tb-link");
  linkIn.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") { linkIn.hidden = true; restore(); return; }
    if (ev.key !== "Enter") return;
    ev.preventDefault(); var v = linkIn.value.trim(); linkIn.hidden = true;
    if (restore() && /^(https?:|mailto:)/i.test(v)) { document.execCommand("createLink", false, v); touched(); }
  });
  $("#tb-block").addEventListener("change", function (ev) {
    if (ev.target.value && restore()) { document.execCommand("formatBlock", false, "<" + ev.target.value + ">"); touched(); } ev.target.value = "";
  });
  $("#tb-font").addEventListener("change", function (ev) {
    if (ev.target.value && restore()) { document.execCommand("fontName", false, ev.target.value); touched(); } ev.target.value = "";
  });
  $("#tb-size").addEventListener("change", function (ev) {
    if (ev.target.value && restore()) { document.execCommand("fontSize", false, ev.target.value); touched(); } ev.target.value = "";
  });
  $("#tb-color").addEventListener("input", function (ev) { if (restore()) { document.execCommand("foreColor", false, ev.target.value); touched(); } });
  $("#tb-hilite").addEventListener("input", function (ev) { if (restore()) { document.execCommand("hiliteColor", false, ev.target.value); touched(); } });
  document.addEventListener("keydown", function (ev) {
    if ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === "k" && ev.target.closest && ev.target.closest("[data-ek]")) {
      ev.preventDefault(); $('button[data-cmd="link"]', tb).click();
    }
  });
})();
</script>"""


def brief(dated, d):
    """The month in one block: who the reels talk to and which best sellers they sell (shared/facts.json top_books, buyers)."""
    facts = json.loads((HERE.parents[4] / "shared/facts.json").read_text())
    books = facts["top_books"]["books"]
    g = sum(1 for r in dated if r.get("audience") == "grandma")
    cards = []
    for b in books:
        if not b["id"]:
            continue
        page = f"books/{b['id']}"
        n = sum(1 for r in dated if r.get("page") == page)
        cards.append(f'<a href="https://lumebook.com/IL/he/{page}" target="_blank" rel="noopener"><b>{e(b["title"].split(" - ")[0])}</b>'
                     f'<span>{b["orders"]} הזמנות בכל התקופה, {n} רילס בלוח</span></a>')
    return (f'<section class="brief" aria-label="למי ועל מה"><h3>למי ועל מה החודש</h3>'
            f'<p>נשים בנות 55 עד 64 הן קבוצת הקונות הגדולה ביותר בנתוני מטא של 05 / 11 / 2026, ונשים מגיל 45 ומעלה הן 58% מהרכישות של נשים. '
            f'לכן {g} מתוך {len(dated)} הרילס בלוח מדברים לסבתות, והשאר להורים. מ {reels.ddmm(d["defaults"]["options"]["from"])} יש לכל יום שתי אפשרויות, ואת זו שתבחר מצלמים. '
            f'כל ריל מכוון לספר או לעמוד המתנות באתר, והקישור ב DM פותח אותו.</p>'
            f'<div class="books">{"".join(cards)}</div></section>')


def page(d, web=False):
    """web=True is the read-only copy for the public Vercel site (10 Nov 2026, Yarin: "i need the scripts" on the phone): no project nav,
    no summary (it carries book order counts and Meta audience figures), no make sheets, no editing, no link to the claude.ai copy."""
    rs = sorted(d["reels"], key=reels.when)
    s = d["defaults"]
    L = s["length"]
    cats = design.categories("reel-series")
    dated = [r for r in rs if r["date"]]
    filt = '<button class="lb-chip cat no-swatch lb-cat-0" type="button" aria-pressed="true" data-f="all">הכול</button>' + "".join(
        f'<button class="lb-chip cat {design.cat_class("reel-series", k)}" type="button" aria-pressed="false" data-f="{k}">{e(v["label"])}</button>'
        for k, v in cats.items() if any(str(r["series"]) == k for r in rs))
    filt += '<button class="lb-chip cat lb-cat-3" type="button" aria-pressed="false" data-f="grandma">מדברים לסבתות</button>'
    cards = "".join(card(r, d, web) for r in dated)
    summary = "" if web else brief(dated, d)
    cta_words = len(s["cta_voice"].split())
    ask_cfg = json.dumps({
        "facts": s["facts"], "offer": s.get("offer", {}).get("text", ""),
        "cta_voice": s["cta_voice"], "cta_caption": s["cta_caption"], "disclaimer": s["caption_disclaimer"],
        "vo_min": max(1, int((L["min"] - L["lead_seconds"]) * L["words_per_second"]) + 1 - cta_words),
        "vo_max": int((L["max"] - L["lead_seconds"]) * L["words_per_second"]) - cta_words,
        # the claude.ai copy of the hub: the ask buttons need claude.ai's sample capability, so the project server links there
        "artifact": json.loads((ROOT / "lumebook.json").read_text())["components"]["reels-hub"]["publish"]["url"],
        # glyphs the make sheet draws in the page (file tiles, the finished reel, the drop veil)
        "icons": {k: design.icon(v) for k, v in {"video": "film", "image": "image", "audio": "audio", "file": "file", "upload": "upload",
                                                  "close": "close", "download": "download", "open": "open-out"}.items()},
    }, ensure_ascii=False).replace("</", "<\\/")
    if web:
        ask_cfg = "{}"
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>רילס נובמבר</title>
<meta name="claude:viewport-fit-sides" content="cover">
{design.head(nav=not web)}
{WEB_CSS if web else ""}
<style>
/* Layout: a sticky bar with the save state, a formatting toolbar under it while text is being edited, a summary,
   the month as a 7-day grid (Sunday first), then one card per reel in date order, then the spares. */
body {{ background: var(--bg); color: var(--text); font-family: var(--font); }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 21; background: var(--bar); }}
.lb-topbar-in, .lb-page {{ padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
.lb-topbar-in .sp {{ flex: 1; }}
.lb-topbar-in .sub {{ font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }}
#save-state {{ min-width: 6.5rem; justify-content: center; }}
.intro {{ display: grid; gap: var(--sp-3); }}
.intro h2 {{ font-size: var(--fs-display); font-weight: 800; letter-spacing: -.02em; line-height: 1.15; text-wrap: balance; }}
.intro p {{ color: var(--text-2); max-width: 62ch; }}
.filters {{ display: flex; flex-wrap: wrap; gap: var(--sp-2); }}
.aud {{ font-family: var(--font-2); font-size: .6875rem; font-weight: 700; padding: 0 5px; border-radius: 999px; background: var(--accent-soft); color: var(--accent-ink); }}
.brief {{ display: grid; gap: var(--sp-3); padding: var(--sp-4) var(--sp-5); border-radius: var(--r-lg); background: var(--glass-sheen), var(--glass-grey); box-shadow: var(--glass-card-rim), var(--glass-card-lift); }}
.brief h3 {{ font-size: var(--fs-headline); }}
.brief p {{ color: var(--text-2); max-width: 70ch; font-size: var(--fs-callout); }}
.books {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: var(--sp-2); }}
.books a {{ display: grid; gap: 2px; padding: .6rem .8rem; border-radius: var(--r-md); background: var(--glass-sheen), var(--glass-card); border: 1px solid transparent; box-shadow: var(--glass-card-rim-sm), 0 10px 20px -16px rgba(41, 30, 22, .3); color: var(--text); text-decoration: none; }}
.books a:hover {{ border-color: var(--tint); }}
.books b {{ font-size: var(--fs-callout); }}
.books span {{ font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }}
.st {{ width: .55rem; height: .55rem; border-radius: 50%; flex: none; }}
.st.success {{ background: var(--success); }} .st.info {{ background: var(--info); }} .st.warning {{ background: var(--warning); }} .st.danger {{ background: var(--danger); }}
.car {{ font-family: var(--font-2); font-size: .6875rem; color: var(--text-3); white-space: nowrap; }}
.legend {{ display: flex; flex-wrap: wrap; gap: var(--sp-2) var(--sp-4); font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-2); }}
.legend span {{ display: inline-flex; align-items: center; gap: 6px; }}
.reel {{ scroll-margin-top: 6rem; }}  /* the card itself is lb-card lb-tinted lb-cat-N */
.reel:target {{ box-shadow: 0 0 0 2px var(--tc); }}
.reel-head {{ display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-3); }}
.when {{ display: flex; align-items: baseline; gap: 8px; font-family: var(--font-2); }}
.when .wd {{ font-weight: 700; }} .when .dd {{ font-variant-numeric: tabular-nums; color: var(--text-2); }} .when .tm {{ color: var(--text-3); font-variant-numeric: tabular-nums; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }}
.hook-big {{ font-size: var(--fs-title); font-weight: 800; line-height: 1.25; letter-spacing: -.01em;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.hook-big:focus {{ white-space: normal; overflow: visible; }}
/* the reel card as stacked glass (Yarin, 07 Nov 2026: "a similar treatment like the creators map cards"): the card is the base
   sheet; the script table and the shooting notes are lb-sheets on it; the Instagram caption is the lb-window, the last and lowest
   part, a little wider than the card. It sits inside the dialog's thick glass, so it does not blur again (never glass on glass). */
.reel {{ gap: var(--sp-4); }}
.sec-t {{ margin: 0; display: flex; align-items: center; gap: .4rem; font-family: var(--font-2); font-size: var(--fs-caption); font-weight: 700;
  line-height: 1.2; letter-spacing: .02em; color: var(--text-3); }}
.sec-t .i {{ width: .95rem; height: .95rem; flex: none; }}
.script {{ padding: var(--sp-3) var(--sp-4) var(--sp-2); display: grid; gap: var(--sp-2); min-width: 0; }}
.script-head {{ display: flex; align-items: center; justify-content: space-between; gap: var(--sp-3); }}
.script-sum {{ font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }}
.script-sum b {{ font-weight: 700; color: var(--text-2); font-variant-numeric: tabular-nums; }}
.script-t {{ table-layout: fixed; }}
.script-t th {{ position: static; background: none; -webkit-backdrop-filter: none; backdrop-filter: none; padding: 0 var(--sp-2) 6px; border-bottom: 1px solid var(--line); }}
.script-t th.tc {{ width: 4.25rem; }}
.script-t th:nth-child(2) {{ width: 54%; }}
.script-t td {{ padding: .55rem var(--sp-2); border-bottom: 1px solid var(--line); }}
.script-t tbody tr:hover td {{ background: none; }}
.script-t tr:last-child td {{ border-bottom: 0; }}
.script-t .tc {{ font-family: var(--font-2); font-variant-numeric: tabular-nums; white-space: nowrap; }}
.script-t td.tc span {{ display: block; line-height: 1.3; }}
.script-t .t0 {{ font-weight: 700; color: var(--text); font-size: var(--fs-callout); }}
.script-t .t1 {{ font-size: var(--fs-caption); color: var(--text-3); }}
.script-t .say > div {{ font-size: var(--fs-callout); font-weight: 500; line-height: 1.45; }}
.script-t .see > div {{ font-size: var(--fs-footnote); color: var(--text-2); line-height: 1.45; }}
.script-t tr.fixed td, .script-t tr.fixed .say > div, .script-t tr.fixed .see > div {{ color: var(--text-3); }}
.rows.lb-sheet {{ margin: 0; padding: var(--sp-3) var(--sp-4); }}
.rows:empty {{ display: none; }}
.rows {{ display: grid; gap: var(--sp-3); }}
.rows .row {{ display: grid; grid-template-columns: 9rem minmax(0, 1fr); gap: var(--sp-3); align-items: start; }}
.rows dt {{ padding-top: 2px; }}
.rows dd {{ margin: 0; min-width: 0; }}
.shot summary {{ cursor: pointer; width: fit-content; font-family: var(--font-2); font-weight: 600; font-size: var(--fs-footnote); color: var(--tint); }}
.shot summary:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 2px; border-radius: 4px; }}
.shot[open] summary {{ margin-bottom: 4px; }}
.shot .sub {{ display: block; margin-top: var(--sp-2); font-family: var(--font-2); font-weight: 600; font-size: var(--fs-footnote); color: var(--text-3); }}
.rows p, .rows li {{ font-size: var(--fs-callout); }}
.vo {{ margin: 0; padding-inline-start: 1.4rem; display: grid; gap: 3px; }}
.vo li::marker {{ color: var(--text-3); font-family: var(--font-2); font-size: var(--fs-footnote); }}
.vo li.fixed {{ color: var(--text-3); }}
.capwin {{ padding: var(--sp-3) var(--sp-4) var(--sp-4); display: grid; gap: var(--sp-2); }}
.lb-dialog .capwin {{ -webkit-backdrop-filter: none; backdrop-filter: none; }}
.cap {{ display: grid; gap: var(--sp-2); justify-items: start; }}
.capbox {{ width: 100%; line-height: 1.55; }}
/* making the reel (07 Nov 2026): a sheet under the shooting notes with the finished reel, the drop zone (lb-drop), the dropped files
   (lb-files) and the prompt (lb-composer). The composer sits 6px from the sheet's sides and bottom, so its corners nest in the
   sheet's 20px; the rest keeps the sheet's 16px. */
.make {{ padding: var(--sp-3) 6px 6px; display: grid; gap: var(--sp-3); min-width: 0; }}
.make > :not(.make-comp) {{ margin-inline: 10px; }}
.make-comp {{ --lb-composer-r: calc(var(--r-lg) - 6px); }}
.make-head {{ display: flex; align-items: center; justify-content: space-between; gap: var(--sp-3); }}
.make-sum {{ font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }}
.make-note {{ text-align: start; padding-inline: 8px; }}
.make-msg {{ display: flex; align-items: center; gap: var(--sp-2); margin-block: -4px 4px; font-size: var(--fs-footnote); color: var(--text-2); }}
.make-msg:empty {{ display: none; }}
.make-msg.is-error {{ color: var(--danger); }}
.make-msg > span:not(.lb-spinner):not(.t) {{ min-width: 0; flex: 1; }}
.make-msg .lb-spinner {{ flex: none; }}
.make-msg .t {{ flex: none; font-family: var(--font-2); font-variant-numeric: tabular-nums; color: var(--text-3); }}
.make-msg button {{ flex: none; border: 0; background: none; padding: 0; color: var(--tint); font: 600 var(--fs-footnote) var(--font-2); cursor: pointer; text-decoration: underline; }}
.make-off {{ display: none; font-size: var(--fs-footnote); color: var(--text-3); }}
.make.is-off > :is(.make-drop, .make-files, .make-comp, .make-msg, .make-final) {{ display: none; }}
.make.is-off > .make-off {{ display: block; margin-block-end: 6px; }}
.make-final {{ display: grid; grid-template-columns: 8.5rem minmax(0, 1fr); gap: var(--sp-3); align-items: start; }}
.make-final[hidden] {{ display: none; }}
.make-final video {{ display: block; width: 100%; aspect-ratio: 9 / 16; border-radius: var(--r-md); background: #000; object-fit: contain;
  box-shadow: 0 10px 22px -14px rgba(41, 30, 22, .55); }}
.make-final-info {{ display: grid; gap: 6px; align-content: start; min-width: 0; }}
.make-final-info b {{ font-size: var(--fs-callout); }}
.make-final-info .n {{ font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); unicode-bidi: plaintext; text-align: start; overflow-wrap: anywhere; }}
.make-final-info p {{ margin: 0; font-size: var(--fs-footnote); color: var(--text-2); line-height: 1.5; }}
.make-final-acts {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.make-final-acts svg {{ width: .95rem; height: .95rem; }}
.make-vers {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.make-vers button[aria-pressed="true"] {{ color: var(--tint); }}
.lb-composer-bar > .lb-btn[data-busy="1"] svg {{ display: none; }}
code {{ font-family: var(--font-mono); font-size: var(--fs-footnote); overflow-wrap: anywhere; }}
/* two options a day (Yarin, 10 Nov 2026: "i want 2 options for each day"): the grid cell holds the day number and the two options as
   small tinted day cards, א on top; once one is picked it gets a green border and נבחרה, the other fades until hovered */
.lb-day-pair {{ display: grid; grid-template-rows: auto 1fr 1fr; gap: 4px; min-width: 0; min-height: 7.2rem; }}
.lb-day-pair .pair-top {{ display: flex; align-items: center; justify-content: space-between; gap: 4px; padding-inline: 4px; min-height: 1.1rem; }}
.lb-day.is-opt {{ min-height: 0; padding: 4px 6px; gap: 2px; }}
.lb-day.is-opt .lb-day-text {{ font-size: var(--fs-caption, .75rem); line-height: 1.3; -webkit-line-clamp: 2; align-self: start; max-height: 2.6em; }}
.lb-day.is-opt .lb-day-foot {{ min-height: 0; }}
.opt-l {{ font-family: var(--font-2); font-weight: 800; font-size: var(--fs-caption, .75rem); color: var(--text-2); }}
.legend .opt-l {{ letter-spacing: .1em; }}
.pick-mark {{ display: none; font-family: var(--font-2); font-size: .6875rem; font-weight: 700; color: var(--success); }}
.lb-day.is-pick {{ border-color: var(--success); }}
.lb-day.is-pick .pick-mark {{ display: inline; }}
.lb-day.is-unpicked {{ opacity: .45; }}
.lb-day.is-unpicked.is-dim {{ opacity: .2; }}
.lb-day.is-unpicked:is(:hover, :focus-visible, [aria-current="true"]) {{ opacity: 1; }}
.optbar {{ display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-2) var(--sp-3); }}
.optbar .lb-segmented button {{ display: inline-flex; align-items: baseline; gap: .4rem; }}
.optbar-id {{ font-family: var(--font-2); font-size: var(--fs-caption, .75rem); color: var(--text-3); font-variant-numeric: tabular-nums; }}
@media (max-width: 640px) {{
  .lb-day-pair {{ min-height: 3.6rem; gap: 2px; }}
  .lb-day-pair .pair-top {{ padding-inline: 2px; }}
  .lb-day.is-opt {{ padding: 2px 4px; }}
  .lb-day.is-opt .lb-day-top {{ flex-direction: row; align-items: center; gap: 2px; }}
  .lb-day.is-opt .lb-day-foot {{ display: none; }}
}}
@media (max-width: 640px) {{
  .hook-big {{ font-size: var(--fs-headline); }}
  .car {{ display: none; }}
  .rows .row {{ grid-template-columns: minmax(0, 1fr); gap: 2px; }}
  .reel {{ padding: var(--sp-3) var(--sp-4); }}
  .lb-dialog-body > .reel {{ --lb-rec-pad-x: var(--sp-4); --lb-rec-pad-b: var(--sp-3); }}
  .script {{ padding: var(--sp-2) var(--sp-3); }}
  .make-final {{ grid-template-columns: 7rem minmax(0, 1fr); }}
  .script-t td.tc span {{ display: inline; }}
  .script-t td.tc .t1::before {{ content: " עד "; }}
  .script-t td.tc::before {{ display: none !important; }}
  .lb-topbar-in .sub {{ display: none; }}
}}
/* the tray of background asks (07 Nov 2026): floating glass at the bottom left corner (Yarin, 07 Nov 2026: "move it to the left side"), above the edit button, clear of the project nav on the right; physical left so the page direction never flips it */
.jobs {{ position: fixed; z-index: 55; left: max(var(--sp-4), env(safe-area-inset-left, 0px)); right: auto; inset-block-end: calc(4.75rem + var(--lb-gnav-pad, 0px) + env(safe-area-inset-bottom, 0px));
  width: min(23rem, calc(100vw - 2 * var(--sp-4))); max-height: min(60vh, 32rem); overflow: auto; border-radius: var(--r-xl); padding: var(--sp-3) var(--sp-4); display: grid; gap: var(--sp-2); }}
.jobs[hidden] {{ display: none; }}
html.lb-docked .jobs {{ left: calc(var(--lb-dock-w) + var(--sp-4)); }}   /* beside the reel drawer, not over it */
.jobs-head {{ display: flex; align-items: center; justify-content: space-between; gap: var(--sp-2); }}
.jobs-title {{ font-weight: 700; font-size: var(--fs-callout); }}
.jobs.is-folded .jobs-list, .jobs.is-folded .jobs-note {{ display: none; }}
.jobs-list {{ display: grid; gap: var(--sp-2); }}
.jobs-note {{ margin: 0; font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }}
.jobs-note:empty {{ display: none; }}
.job {{ background: var(--surface); border-radius: var(--r-md); padding: var(--sp-2) var(--sp-3); display: grid; gap: 6px; box-shadow: var(--shadow-1); }}
.job.is-bad {{ background: var(--danger-soft, var(--surface)); }}
.job-top {{ display: flex; align-items: baseline; gap: var(--sp-2); min-width: 0; }}
.job-hook {{ flex: 1; min-width: 0; font-weight: 600; font-size: var(--fs-callout); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.job-kind {{ font-family: var(--font-2); font-size: var(--fs-caption, var(--fs-footnote)); color: var(--text-3); white-space: nowrap; }}
.job-st {{ display: flex; align-items: center; gap: var(--sp-2); font-size: var(--fs-footnote); color: var(--text-2); }}
.job-st span:nth-last-child(2) {{ flex: 1; min-width: 0; }}
.job-t {{ font-family: var(--font-2); font-variant-numeric: tabular-nums; color: var(--text-3); }}
.job-bar {{ height: 4px; border-radius: var(--r-pill); background: var(--fill-3); overflow: hidden; }}
.job-bar i {{ display: block; height: 100%; background: var(--tint); border-radius: inherit; transition: width .4s var(--ease, ease); }}
.job-bar.is-wait i {{ width: 30% !important; animation: lb-jobs-wait 1.4s ease-in-out infinite; }}
@keyframes lb-jobs-wait {{ from {{ transform: translateX(110%); }} to {{ transform: translateX(-340%); }} }}
.job-act {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.lb-day.is-busy {{ position: relative; }}
.lb-day .job-dot {{ width: .75rem; height: .75rem; margin-inline: auto; }}
.lb-day.is-drop {{ outline: 2px solid var(--tint); outline-offset: 2px; transform: scale(1.03); }}
@media (prefers-reduced-motion: reduce) {{ .job-bar.is-wait i {{ animation: none; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
</head>
<body>
<header class="lb-topbar"><div class="lb-topbar-in">
  <h1>רילס נובמבר</h1><span class="sub">ריל ביום מתוך שתי אפשרויות, {e(s['post_time'])}, {L['min']} עד {L['max']} שניות</span><span class="sp"></span>
  <span id="save-state" class="lb-chip" role="status" aria-live="polite">טוען...</span>
</div></header>
<main class="lb-page">
  <section class="intro">
    <span class="lb-eyebrow">05 עד 30 / 11 / 2026</span>
    {ed("h2", "page__title", "מערכת תוכן")}
  </section>

  {summary}

  <section class="lb-section" aria-labelledby="h-month">
    <div class="lb-section-head"><h2 id="h-month" class="lb-card-title">החודש</h2>
      <div class="legend"><span><b class="opt-l">א ב</b>שתי אפשרויות ליום</span><span><i class="st success"></i>מוכן או פורסם</span><span><i class="st info"></i>מחכה לעריכה שלי</span><span><i class="st warning"></i>מחכה לך</span><span><i class="st danger"></i>חסום</span></div>
    </div>
    <div class="filters" role="group" aria-label="סינון לפי סדרה">{filt}</div>
    {month_grid(dated, s['carousel_days'], d.get('picks'))}
  </section>

</main>
<div id="cards" hidden>{cards}</div>
<dialog id="dlg" class="lb-dialog" aria-label="ריל">
  <div class="lb-dialog-card">
    <div class="lb-dialog-head">{TOOLBAR}{AUTOSCROLL}<button type="button" class="lb-dialog-x" id="dlg-x" aria-label="סגירה">✕</button></div>
    <div class="lb-dialog-body" id="dlg-body"></div>
  </div>
  <form class="lb-ask" id="ask" autocomplete="off">
    <div class="lb-composer">
      <label class="lb-composer-label lb-ask-label" for="ask-t">הערה לשינוי הריל</label>
      <textarea id="ask-t" rows="2" dir="rtl" placeholder="מה לשנות? למשל: כותרת יותר קצרה, פתיחה אחרת"></textarea>
      <div class="lb-composer-bar">
        <button type="button" class="lb-btn secondary sm" id="ask-new" title="מחליף את כל הריל ברעיון אחר לאותו יום ולאותה סדרה">{design.icon("sparkle")}<span>רעיון חדש</span></button>
        <span class="lb-composer-note" id="ask-note">⌘ Enter לשליחה</span>
        <button type="submit" class="lb-btn sm" id="ask-go">{design.icon("arrow-up")}<span>שליחה</span></button>
      </div>
    </div>
    <p class="lb-ask-msg" id="ask-msg" role="status" aria-live="polite"></p>
  </form>
</dialog>
<script type="application/json" id="ask-cfg">{ask_cfg}</script>
{SCRIPT}
{WEB_JS if web else ""}
</body>
</html>
"""


WEB_CSS = """<meta name="robots" content="noindex, nofollow">
<style>
/* public copy: text can be edited (10 Nov 2026, Yarin: "let me edit the text"), saved in that browser only; nothing uploads or asks Claude */
.make, #ask, .optbar .pick, [data-made], .lb-ask { display: none !important; }
/* only the script itself: no "what they see" column, no times and no "what I say" label on a phone-width screen of the Vercel copy (10 Nov 2026, Yarin) */
@media (max-width: 700px) { .script-t td.see, .script-t th:nth-child(3), .script-t td.tc, .script-t td.say::before { display: none !important; } }
/* teleprompter with the camera (10 Nov 2026, Yarin: "make it a teleprompter with camera abilities"): the web copy only */
dialog#tp { position: fixed; inset: 0; width: 100vw; height: 100dvh; max-width: none; max-height: none; margin: 0; padding: 0; border: 0; background: #000; color: #fff; overflow: hidden; }
dialog#tp::backdrop { background: #000; }
#tp video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; background: #000; }
#tp video.mirror { transform: scaleX(-1); }
#tp > video.fit { object-fit: contain; }
#tp .tp-shade { position: absolute; inset: 0; background: linear-gradient(rgba(0,0,0,.55), rgba(0,0,0,.35) 45%, rgba(0,0,0,.55)); pointer-events: none; }
#tp .tp-text { position: absolute; inset: 0 0 9.5rem; overflow-y: auto; padding: 38dvh 22px 55dvh; text-align: center; direction: rtl; font-family: var(--font); font-weight: 700; line-height: 1.45; text-shadow: 0 1px 6px rgba(0,0,0,.9); scrollbar-width: none; -webkit-overflow-scrolling: touch; }
#tp .tp-text::-webkit-scrollbar { display: none; }
#tp .tp-text p { margin: 0 0 1.1em; }
#tp .tp-text p.fixed { opacity: .75; }
#tp .tp-line { position: absolute; inset-inline: 0; top: 38dvh; height: 0; border-top: 2px solid rgba(255,214,102,.8); pointer-events: none; }
#tp .tp-bar { position: absolute; inset-inline: 0; bottom: 0; display: grid; gap: 8px; padding: 10px 12px calc(10px + env(safe-area-inset-bottom, 0px)); background: rgba(0,0,0,.6); }
#tp .tp-r { display: flex; align-items: center; justify-content: center; gap: 8px; }
#tp button { font: inherit; color: #fff; background: rgba(255,255,255,.18); border: 0; border-radius: 999px; min-width: 44px; height: 44px; padding: 0 14px; cursor: pointer; }
#tp button:disabled { opacity: .35; }
#tp .tp-rec { width: 64px; height: 64px; background: #fff; border: 4px solid rgba(255,255,255,.5); position: relative; padding: 0; }
#tp .tp-rec::after { content: ""; position: absolute; inset: 8px; border-radius: 50%; background: #e5252a; transition: inset .15s, border-radius .15s; }
#tp .tp-rec.on::after { inset: 18px; border-radius: 6px; }
#tp .tp-top { position: absolute; inset-inline: 0; top: 0; display: flex; justify-content: space-between; align-items: center; padding: calc(10px + env(safe-area-inset-top, 0px)) 12px 10px; z-index: 2; }
#tp .tp-time { font-family: var(--font-2); font-variant-numeric: tabular-nums; font-weight: 700; background: rgba(0,0,0,.5); border-radius: 999px; padding: 6px 12px; }
#tp .tp-time.rec::before { content: "● "; color: #ff4d4f; }
#tp .tp-count { position: absolute; inset: 0; display: none; align-items: center; justify-content: center; font-size: 30vmin; font-weight: 800; text-shadow: 0 2px 16px rgba(0,0,0,.8); pointer-events: none; z-index: 3; }
#tp .tp-msg { position: absolute; inset-inline: 16px; top: 30%; text-align: center; background: rgba(0,0,0,.7); border-radius: 16px; padding: 16px; z-index: 3; direction: rtl; }
#tp .tp-done { position: absolute; inset: 0; z-index: 4; background: #000; display: none; flex-direction: column; align-items: center; justify-content: center; gap: 12px; padding: 16px; }
#tp .tp-done video { position: static; width: min(100%, 420px); height: auto; max-height: 68dvh; border-radius: 16px; object-fit: contain; }
#tp .tp-row { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
#tp .tp-save { background: #5B2BD6; }
#tp .tp-set { position: absolute; inset-inline: 12px; top: calc(62px + env(safe-area-inset-top, 0px)); z-index: 5; background: rgba(20,20,24,.94); border-radius: 18px; padding: 14px; display: none; gap: 12px; direction: rtl; max-height: 62dvh; overflow-y: auto; }
#tp .tp-set.on { display: grid; }
#tp .tp-set h4 { margin: 0 0 6px; font-size: .8rem; font-weight: 700; color: #fff; opacity: .85; }
#tp .tp-seg { display: flex; gap: 6px; flex-wrap: wrap; }
#tp .tp-seg button { height: 40px; }
#tp .tp-seg button[aria-pressed="true"] { background: #5B2BD6; }
#tp .tp-info { font-size: .75rem; opacity: .8; text-align: center; }
#tp .tp-note { font-size: .8rem; opacity: .8; text-align: center; max-width: 36ch; }
.autoscroll #tp-open { font-weight: 700; }
</style>"""
WEB_JS = r"""<script>
/* Sending to the Mac (10 Nov 2026, Yarin: "pack both the change in the script and the videos altogether"): the takes recorded in the
   teleprompter are kept in this browser (IndexedDB) until sent; שליחה למחשב packs them with the script edits into one zip (stored, not
   compressed: videos are already compressed) and opens the share sheet (AirDrop). On the Mac: reels.py merge phone. */
(function () {
  var DBN = "lb-reel-takes", ST = "takes", db = null;
  function open() {
    if (db) return Promise.resolve(db);
    return new Promise(function (ok, no) {
      if (!window.indexedDB) { no(new Error("no idb")); return; }
      var q = indexedDB.open(DBN, 1);
      q.onupgradeneeded = function () { q.result.createObjectStore(ST, { keyPath: "id", autoIncrement: true }); };
      q.onsuccess = function () { db = q.result; ok(db); }; q.onerror = function () { no(q.error); };
    });
  }
  function tx(mode, fn) {
    return open().then(function (d) { return new Promise(function (ok, no) {
      var t = d.transaction(ST, mode), r = fn(t.objectStore(ST)); t.oncomplete = function () { ok(r && r.result); }; t.onerror = t.onabort = function () { no(t.error); };
    }); });
  }
  var takes = {
    all: function () { return tx("readonly", function (s) { return s.getAll(); }).then(function (a) { return a || []; }, function () { return []; }); },
    add: function (t) { return tx("readwrite", function (s) { return s.add(t); }); },
    put: function (t) { return tx("readwrite", function (s) { return s.put(t); }); },
    del: function (id) { return tx("readwrite", function (s) { return s.delete(id); }); }
  };
  window.lbTakes = takes;
  try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist(); } catch (x) {}

  var T = null;
  function crcTable() { T = new Uint32Array(256); for (var n = 0; n < 256; n++) { var c = n; for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; T[n] = c >>> 0; } }
  async function crcOf(blob) {
    if (!T) crcTable();
    var c = 0xFFFFFFFF;
    for (var o = 0; o < blob.size; o += 4194304) {
      var u = new Uint8Array(await blob.slice(o, o + 4194304).arrayBuffer());
      for (var i = 0; i < u.length; i++) c = T[(c ^ u[i]) & 255] ^ (c >>> 8);
    }
    return (c ^ 0xFFFFFFFF) >>> 0;
  }
  function le(n, v) { var a = new Uint8Array(n); for (var i = 0; i < n; i++) a[i] = (v >>> (8 * i)) & 255; return a; }
  async function zip(entries, progress) {   /* entries: [{name, blob}] -> Blob (store only, no zip64) */
    var enc = new TextEncoder(), parts = [], cd = [], off = 0, now = new Date();
    var dt = ((now.getHours() << 11) | (now.getMinutes() << 5) | (now.getSeconds() >> 1)) & 0xFFFF;
    var dd = (((now.getFullYear() - 1980) << 9) | ((now.getMonth() + 1) << 5) | now.getDate()) & 0xFFFF;
    for (var e = 0; e < entries.length; e++) {
      var en = entries[e], nm = enc.encode(en.name), crc = await crcOf(en.blob), sz = en.blob.size;
      if (progress) progress(e + 1, entries.length);
      var lh = [le(4, 0x04034b50), le(2, 20), le(2, 0x0800), le(2, 0), le(2, dt), le(2, dd), le(4, crc), le(4, sz), le(4, sz), le(2, nm.length), le(2, 0), nm];
      lh.forEach(function (p) { parts.push(p); }); parts.push(en.blob);
      var hl = 30 + nm.length;
      cd.push([le(4, 0x02014b50), le(2, 20), le(2, 20), le(2, 0x0800), le(2, 0), le(2, dt), le(2, dd), le(4, crc), le(4, sz), le(4, sz), le(2, nm.length), le(2, 0), le(2, 0), le(2, 0), le(2, 0), le(4, 0), le(4, off), nm]);
      off += hl + sz;
    }
    var cdSize = 0; cd.forEach(function (a) { a.forEach(function (p) { parts.push(p); cdSize += p.length; }); });
    [le(4, 0x06054b50), le(2, 0), le(2, 0), le(2, entries.length), le(2, entries.length), le(4, cdSize), le(4, off), le(2, 0)].forEach(function (p) { parts.push(p); });
    return new Blob(parts, { type: "application/zip" });
  }

  var bar = document.querySelector(".lb-topbar-in"), st = document.getElementById("save-state"); if (!bar) return;
  var b = document.createElement("button"); b.type = "button"; b.className = "lb-btn sm"; b.id = "exp"; b.textContent = "שליחה למחשב";
  b.title = "השינויים בתסריטים והסרטונים שצילמת, חבילה אחת לשליחה למחשב (AirDrop)";
  var clr = document.createElement("button"); clr.type = "button"; clr.className = "lb-btn secondary sm"; clr.id = "exp-clear"; clr.hidden = true; clr.textContent = "מחיקת הסרטונים ששלחתי";
  var note = document.createElement("span"); note.className = "sub"; note.id = "exp-note";
  bar.insertBefore(b, st); bar.insertBefore(clr, st); bar.insertBefore(note, st);
  var timer = 0;
  function say(t, keep) { note.textContent = t; clearTimeout(timer); if (!keep) timer = setTimeout(count, 9000); }
  function edits() {
    var local = {}; try { local = JSON.parse(localStorage.getItem("lb-reels-nov-edits") || "{}"); } catch (x) {}
    return Object.keys(local).map(function (k) { return local[k]; }).filter(function (d) { return d && d.key && (d.text || d.html); });
  }
  function count() {
    return takes.all().then(function (all) {
      var un = all.filter(function (t) { return !t.sent; }), sent = all.length - un.length, ed = edits().length, bits = [];
      if (un.length) bits.push(un.length === 1 ? "סרטון אחד" : un.length + " סרטונים");
      if (ed) bits.push(ed === 1 ? "שינוי אחד" : ed + " שינויים");
      note.textContent = bits.length ? "מחכים לשליחה: " + bits.join(" ו") : "";
      clr.hidden = !sent; return { un: un, ed: ed };
    });
  }
  window.addEventListener("lb-takes", count); count();
  clr.addEventListener("click", function () {
    takes.all().then(function (all) {
      var sent = all.filter(function (t) { return t.sent; });
      if (!sent.length || !confirm("למחוק מהטלפון " + sent.length + " סרטונים ששלחת? לוודא קודם שהם הגיעו למחשב.")) return;
      return Promise.all(sent.map(function (t) { return takes.del(t.id); })).then(count);
    });
  });
  b.addEventListener("click", async function () {
    var docs = edits(), un = (await takes.all()).filter(function (t) { return !t.sent; });
    if (!docs.length && !un.length) { say("אין מה לשלוח"); return; }
    var d = new Date(), pad = function (n) { return String(n).padStart(2, "0"); }, stamp = d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + "-" + pad(d.getHours()) + pad(d.getMinutes());
    var json = new Blob([JSON.stringify({ docs: docs, exported: d.toISOString(), from: "phone" }, null, 1)], { type: "application/json" });
    var file, label = (docs.length ? (docs.length === 1 ? "שינוי אחד" : docs.length + " שינויים") : "") + (docs.length && un.length ? " ו" : "") + (un.length ? (un.length === 1 ? "סרטון אחד" : un.length + " סרטונים") : "");
    if (!un.length) { file = new File([json], "reels-edits-" + stamp + ".json", { type: "application/json" }); }
    else {
      var total = un.reduce(function (a, t) { return a + t.blob.size; }, 0);
      if (total > 3.8e9) { say("הסרטונים גדולים מדי לחבילה אחת (מעל 3.8 GB). שולחים בנפרד מ שמירה לגלריה", true); return; }
      b.disabled = true;
      try {
        var ent = un.map(function (t) { return { name: "videos/" + t.name, blob: t.blob }; });
        if (docs.length) ent.unshift({ name: "edits.json", blob: json });
        var zb = await zip(ent, function (i, n) { say("אורז " + i + " מתוך " + n + "...", true); });
        file = new File([zb], "reels-from-phone-" + stamp + ".zip", { type: "application/zip" });
      } catch (x) { say("האריזה נכשלה: " + (x && x.message || x), true); b.disabled = false; return; }
      b.disabled = false;
    }
    function sentOk() {
      say(label + " נשלחו. במחשב: reels.py merge phone", true);
      return Promise.all(un.map(function (t) { t.sent = true; return takes.put(t); })).then(function () { return count().then(function () { note.textContent = label + " נשלחו. במחשב: reels.py merge phone"; }); });
    }
    if (navigator.canShare && navigator.canShare({ files: [file] })) { navigator.share({ files: [file], title: file.name }).then(sentOk, function () { count(); }); return; }
    var a = document.createElement("a"); a.href = URL.createObjectURL(file); a.download = file.name; document.body.appendChild(a); a.click(); a.remove();
    sentOk();
  });
})();
</script>
<script>
/* Teleprompter with the camera (10 Nov 2026, Yarin): the open reel's script on the phone camera, scrolling slowly; record, then save or share.
   The text is not part of the recording (only camera and microphone are recorded). Nothing leaves the phone. */
(function () {
  var dlg = document.getElementById("dlg"), grp = dlg && dlg.querySelector(".autoscroll");
  if (!grp || !window.HTMLDialogElement) return;
  var SPEEDS = [8, 14, 20, 28, 38, 50, 66, 88, 120], spI = 2, fs = 30, facing = "user";
  var cfg = { q: 1080, fps: 30, orient: "portrait", mv: 1, mf: 0 };
  try { var sc = JSON.parse(localStorage.getItem("lb-tp-cfg") || "{}"); Object.keys(cfg).forEach(function (k) { if (sc[k] !== undefined) cfg[k] = sc[k]; }); } catch (x) {}
  try { var sv = parseInt(localStorage.getItem("lb-reel-scroll-speed"), 10); if (sv >= 0 && sv < SPEEDS.length) spI = sv;
        var fz = parseInt(localStorage.getItem("lb-tp-size"), 10); if (fz >= 20 && fz <= 56) fs = fz; } catch (x) {}
  var open = document.createElement("button"); open.type = "button"; open.className = "lb-chip"; open.id = "tp-open";
  open.textContent = "🎬 טלפרומפטר"; open.title = "התסריט על מצלמת הטלפון, גולל לאט, עם הקלטה";
  grp.insertBefore(open, grp.firstChild);

  var tp = document.createElement("dialog"); tp.id = "tp"; tp.setAttribute("aria-label", "טלפרומפטר");
  tp.innerHTML = '<video id="tp-v" class="mirror" playsinline muted autoplay></video><div class="tp-shade"></div>' +
    '<div class="tp-text" id="tp-t" dir="rtl"></div><div class="tp-line"></div>' +
    '<div class="tp-top"><span class="tp-time" id="tp-time">0:00</span><span class="tp-info" id="tp-info"></span><span><button type="button" id="tp-cfg" aria-label="הגדרות">⚙</button> <button type="button" id="tp-x" aria-label="סגירה">✕</button></span></div>' +
    '<div class="tp-set" id="tp-set"><div><h4>איכות</h4><div class="tp-seg" data-k="q"><button type="button" data-v="720">HD 720</button><button type="button" data-v="1080">Full HD 1080</button><button type="button" data-v="2160">4K</button></div></div>' +
    '<div><h4>קצב תמונות</h4><div class="tp-seg" data-k="fps"><button type="button" data-v="30">30</button><button type="button" data-v="60">60</button></div></div>' +
    '<div><h4>כיוון הסרטון</h4><div class="tp-seg" data-k="orient"><button type="button" data-v="portrait">לאורך</button><button type="button" data-v="landscape">לרוחב</button></div></div>' +
    '<div><h4>מראה בתצוגה (כמו מראה)</h4><div class="tp-seg" data-k="mv"><button type="button" data-v="1">כן</button><button type="button" data-v="0">לא</button></div></div>' +
    '<div><h4>מראה גם בסרטון השמור</h4><div class="tp-seg" data-k="mf"><button type="button" data-v="0">לא</button><button type="button" data-v="1">כן</button></div></div>' +
    '<div class="tp-note" id="tp-setnote">הטלפון נותן את האיכות הכי קרובה למה שבחרת, מה שקיבלת מוצג למעלה. 4K ו 60 מקבלים קבצים גדולים. לסרטון לרוחב מסובבים את הטלפון. מראה בסרטון השמור מכבידה על הטלפון.</div></div>' +
    '<div class="tp-count" id="tp-c"></div><div class="tp-msg" id="tp-m" hidden></div>' +
    '<div class="tp-bar"><div class="tp-r"><span style="font-size:.8em;opacity:.8">מהירות</span><button type="button" id="tp-sl" aria-label="לאט יותר">−</button><span id="tp-sp" style="min-width:1.4em;text-align:center;font-weight:700"></span><button type="button" id="tp-sf" aria-label="מהר יותר">+</button>' +
    '<span style="width:10px"></span><span style="font-size:.8em;opacity:.8">טקסט</span><button type="button" id="tp-fm" aria-label="טקסט קטן יותר">A−</button><button type="button" id="tp-fp" aria-label="טקסט גדול יותר">A+</button></div>' +
    '<div class="tp-r"><button type="button" id="tp-go" aria-label="גלילה">⏸</button>' +
    '<button type="button" class="tp-rec" id="tp-rec" aria-label="הקלטה"></button>' +
    '<button type="button" id="tp-fl" aria-label="החלפת מצלמה">⟲</button></div></div>' +
    '<div class="tp-done" id="tp-d"><video id="tp-dv" controls playsinline></video><div class="tp-row"><button type="button" class="tp-save" id="tp-save">שמירה לגלריה</button><button type="button" id="tp-dl">שמירה לקבצים</button></div><div class="tp-row"><button type="button" id="tp-again">צילום מחדש</button><button type="button" id="tp-dx">סגירה</button></div><div class="tp-note" id="tp-sinfo"></div></div>';
  document.body.appendChild(tp);
  var $ = function (i) { return document.getElementById(i); };
  var v = $("tp-v"), t = $("tp-t"), stream = null, rec = null, chunks = [], recT0 = 0, recTick = 0, cv = null, cvRaf = 0, saved = false, going = false, raf = 0, pos = 0, last = 0, setTop = 0, lock = null, blob = null, fname = "reel";

  function lines() {
    var out = [], card = dlg.querySelector(".reel"); if (!card) return out;
    card.querySelectorAll(".script-t tbody tr").forEach(function (tr) {
      var d = tr.querySelector(".say > div"), s = d ? d.innerText.trim() : ""; if (s) out.push({ s: s, fixed: tr.classList.contains("fixed") });
    });
    if (!out.length) {   /* a reel without a voiceover: the text on the screen */
      var h = card.querySelector(".hook-big"); if (h) out.push({ s: h.innerText.trim(), fixed: false });
      card.querySelectorAll("ol.vo li").forEach(function (li) { var s = li.innerText.trim(); if (s) out.push({ s: s, fixed: li.classList.contains("fixed") }); });
    }
    return out;
  }
  function paintText() {
    t.innerHTML = ""; lines().forEach(function (l) { var p = document.createElement("p"); p.textContent = l.s; if (l.fixed) p.className = "fixed"; t.appendChild(p); });
    t.style.fontSize = fs + "px"; $("tp-sp").textContent = String(spI + 1);
    $("tp-sl").disabled = spI === 0; $("tp-sf").disabled = spI === SPEEDS.length - 1;
  }
  function msg(s) { var m = $("tp-m"); m.hidden = !s; m.textContent = s || ""; }
  function step(now) {
    if (!going) return;
    if (Math.abs(t.scrollTop - setTop) > 3) { stopScroll(); return; }
    pos += SPEEDS[spI] * Math.min(now - last, 250) / 1000; last = now;
    var max = t.scrollHeight - t.clientHeight;
    if (pos >= max) { t.scrollTop = max; stopScroll(); return; }
    t.scrollTop = pos; setTop = t.scrollTop; raf = requestAnimationFrame(step);
  }
  function startScroll() { going = true; pos = t.scrollTop; setTop = pos; last = performance.now(); $("tp-go").textContent = "⏸"; raf = requestAnimationFrame(step); }
  function stopScroll() { going = false; cancelAnimationFrame(raf); $("tp-go").textContent = "▶"; }
  ["wheel", "touchstart"].forEach(function (e) { t.addEventListener(e, function () { if (going) stopScroll(); }, { passive: true }); });

  function camera() {
    if (stream) stream.getTracks().forEach(function (k) { k.stop(); });
    msg(""); 
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { msg("הדפדפן הזה לא נותן גישה למצלמה. אפשר להשתמש בטלפרומפטר בלי הקלטה, או לפתוח את העמוד ב Safari או Chrome."); return Promise.resolve(); }
    var long = Math.round(cfg.q * 16 / 9), land = cfg.orient === "landscape";
    var vc = { facingMode: facing, width: { ideal: land ? long : cfg.q }, height: { ideal: land ? cfg.q : long }, frameRate: { ideal: cfg.fps } };
    return navigator.mediaDevices.getUserMedia({ video: vc, audio: { echoCancellation: true, noiseSuppression: true } })
      .catch(function () { return navigator.mediaDevices.getUserMedia({ video: { facingMode: facing }, audio: false }); })
      .then(function (s) { stream = s; v.srcObject = s; v.classList.toggle("mirror", !!cfg.mv); v.classList.toggle("fit", land); v.play().catch(function () {}); readout(); },
            function () { msg("אין גישה למצלמה. צריך לאשר אותה בהגדרות הדפדפן. הטלפרומפטר עובד גם בלעדיה."); });
  }
  function readout() {
    var tr = stream && stream.getVideoTracks()[0], st = tr && tr.getSettings ? tr.getSettings() : null;
    $("tp-info").textContent = st && st.width ? st.width + "×" + st.height + " · " + Math.round(st.frameRate || 0) + " fps" : "";
  }
  function paintCfg() {
    tp.querySelectorAll(".tp-seg").forEach(function (g) {
      g.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", String(cfg[g.dataset.k]) === b.dataset.v ? "true" : "false"); });
    });
    v.classList.toggle("mirror", !!cfg.mv); v.classList.toggle("fit", cfg.orient === "landscape");
  }
  function fmt(ms) { var s = Math.floor(ms / 1000); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); }
  function mime() {
    var c = ["video/mp4;codecs=avc1,mp4a.40.2", "video/mp4", "video/webm;codecs=vp9,opus", "video/webm;codecs=vp8,opus", "video/webm"];
    for (var i = 0; i < c.length; i++) if (window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(c[i])) return c[i];
    return "";
  }
  function startRec() {
    if (!stream || !window.MediaRecorder) { msg("ההקלטה לא נתמכת בדפדפן הזה. הטלפרומפטר ממשיך לעבוד."); return; }
    var n = 3, c = $("tp-c"); c.style.display = "flex"; c.textContent = n; $("tp-rec").disabled = true;
    var iv = setInterval(function () {
      n--; if (n > 0) { c.textContent = n; return; }
      clearInterval(iv); c.style.display = "none"; $("tp-rec").disabled = false;
      chunks = []; var m = mime(), src = stream, st = stream.getVideoTracks()[0].getSettings(), fps = Math.round(st.frameRate || cfg.fps) || 30;
      if (cfg.mf) {   /* a mirrored file: the picture goes through a canvas flipped left to right, the sound is added to it */
        cv = document.createElement("canvas"); cv.width = st.width || v.videoWidth; cv.height = st.height || v.videoHeight;
        var cx = cv.getContext("2d"); cx.translate(cv.width, 0); cx.scale(-1, 1);
        (function draw() { if (!cv) return; cx.drawImage(v, 0, 0, cv.width, cv.height); cvRaf = requestAnimationFrame(draw); })();
        src = cv.captureStream(fps); stream.getAudioTracks().forEach(function (a) { src.addTrack(a); });
      }
      var px = (st.width || 1080) * (st.height || 1920), bps = Math.round(Math.min(60e6, Math.max(6e6, px * fps * 0.08)));
      try { rec = new MediaRecorder(src, Object.assign({ videoBitsPerSecond: bps }, m ? { mimeType: m } : {})); } catch (x) { msg("ההקלטה לא התחילה."); return; }
      $("tp-set").classList.remove("on");
      rec.ondataavailable = function (e) { if (e.data && e.data.size) chunks.push(e.data); };
      rec.onstop = done; rec.start(1000); recT0 = Date.now(); $("tp-rec").classList.add("on"); $("tp-time").classList.add("rec");
      recTick = setInterval(function () { $("tp-time").textContent = fmt(Date.now() - recT0); }, 250);
      t.scrollTop = 0; startScroll();
    }, 1000);
  }
  function stopRec() { cancelAnimationFrame(cvRaf); if (rec && rec.state !== "inactive") rec.stop(); clearInterval(recTick); $("tp-rec").classList.remove("on"); $("tp-time").classList.remove("rec"); stopScroll(); }
  function done() {
    var type = (rec && rec.mimeType) || (chunks[0] && chunks[0].type) || "video/mp4";
    blob = new Blob(chunks, { type: type }); var ext = /mp4/.test(type) ? "mp4" : "webm"; fname = "reel-" + (location.hash.slice(1) || "take") + "." + ext;
    var dv = $("tp-dv"); dv.src = URL.createObjectURL(blob); $("tp-d").style.display = "flex"; saved = false; cv = null;
    var card = dlg.querySelector(".reel"), key = card ? card.id : (location.hash.slice(1) || "take"), nm;
    if (window.lbTakes) lbTakes.all().then(function (all) {
      var n = all.filter(function (t) { return t.reel === key; }).length + 1, d = new Date(), pad = function (x) { return String(x).padStart(2, "0"); };
      nm = key + "__take" + n + "__" + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + "-" + pad(d.getHours()) + pad(d.getMinutes()) + "." + ext;
      return lbTakes.add({ reel: key, name: nm, type: blob.type, blob: blob, size: blob.size, at: d.toISOString(), sent: false });
    }).then(function () { saved = true; window.dispatchEvent(new Event("lb-takes")); $("tp-sinfo").textContent = "נשמר בטלפון, בתוך הדף (" + Math.round(blob.size / 1048576) + " MB). לשליחה למחשב, יחד עם השינויים בתסריטים: הכפתור שליחה למחשב בראש הדף."; }, function () {});
    var st = stream && stream.getVideoTracks()[0] && stream.getVideoTracks()[0].getSettings();
    $("tp-sinfo").textContent = "שומר בטלפון... אם זה נכשל, הסרטון רק בזיכרון של הדף ויימחק בסגירה. " + Math.round(blob.size / 1048576) + " MB" + (st && st.width ? ", " + st.width + "×" + st.height : "") + ".";
  }
  function save() {
    if (!blob) return;
    var f = new File([blob], fname, { type: blob.type });
    if (navigator.canShare && navigator.canShare({ files: [f] })) { navigator.share({ files: [f], title: fname }).then(function () { saved = true; $("tp-sinfo").textContent = "נשלח לתפריט השיתוף. בוחרים שם שמירת וידאו כדי שיגיע לגלריה."; }, function () {}); return; }
    download();
  }
  function download() {
    if (!blob) return;
    var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = fname; document.body.appendChild(a); a.click(); a.remove();
    saved = true; $("tp-sinfo").textContent = "ירד כקובץ " + fname + ". בטלפון הוא נמצא בקבצים, בתיקיית ההורדות.";
  }
  function closeAll() {
    if (blob && !saved && !confirm("הסרטון עוד לא נשמר. לסגור ולמחוק אותו?")) return;
    stopRec(); stopScroll(); if (stream) { stream.getTracks().forEach(function (k) { k.stop(); }); stream = null; } v.srcObject = null;
    if (lock) { try { lock.release(); } catch (x) {} lock = null; }
    var dv = $("tp-dv"); if (dv.src) { try { URL.revokeObjectURL(dv.src); } catch (x) {} dv.removeAttribute("src"); } blob = null; $("tp-d").style.display = "none";
    if (tp.open) tp.close();
  }
  open.addEventListener("click", function () {
    paintText(); paintCfg(); $("tp-time").textContent = "0:00"; $("tp-d").style.display = "none"; tp.showModal(); t.scrollTop = 0; stopScroll(); $("tp-go").textContent = "▶";
    if (navigator.wakeLock) navigator.wakeLock.request("screen").then(function (l) { lock = l; }, function () {});
    camera();
  });
  tp.addEventListener("cancel", function (ev) { ev.preventDefault(); closeAll(); });
  $("tp-x").addEventListener("click", closeAll); $("tp-dx").addEventListener("click", closeAll);
  $("tp-rec").addEventListener("click", function () { if (rec && rec.state === "recording") stopRec(); else startRec(); });
  $("tp-go").addEventListener("click", function () { if (going) stopScroll(); else startScroll(); });
  $("tp-sl").addEventListener("click", function () { spI = Math.max(0, spI - 1); try { localStorage.setItem("lb-reel-scroll-speed", String(spI)); } catch (x) {} paintText(); });
  $("tp-sf").addEventListener("click", function () { spI = Math.min(SPEEDS.length - 1, spI + 1); try { localStorage.setItem("lb-reel-scroll-speed", String(spI)); } catch (x) {} paintText(); });
  function size(d) { fs = Math.max(20, Math.min(56, fs + d)); try { localStorage.setItem("lb-tp-size", String(fs)); } catch (x) {} t.style.fontSize = fs + "px"; }
  $("tp-fm").addEventListener("click", function () { size(-3); }); $("tp-fp").addEventListener("click", function () { size(3); });
  $("tp-fl").addEventListener("click", function () { if (rec && rec.state === "recording") return; facing = facing === "user" ? "environment" : "user"; cfg.mv = facing === "user" ? 1 : 0; paintCfg(); camera(); });
  $("tp-save").addEventListener("click", save); $("tp-dl").addEventListener("click", download);
  $("tp-cfg").addEventListener("click", function () { $("tp-set").classList.toggle("on"); });
  tp.querySelectorAll(".tp-seg").forEach(function (g) {
    g.addEventListener("click", function (ev) {
      var b = ev.target.closest("button"); if (!b || (rec && rec.state === "recording")) return;
      var k = g.dataset.k, val = b.dataset.v; cfg[k] = (k === "q" || k === "fps" || k === "mv" || k === "mf") ? parseInt(val, 10) : val;
      try { localStorage.setItem("lb-tp-cfg", JSON.stringify(cfg)); } catch (x) {}
      paintCfg(); if (k === "q" || k === "fps" || k === "orient") camera();
    });
  });
  $("tp-again").addEventListener("click", function () { $("tp-d").style.display = "none"; blob = null; $("tp-time").textContent = "0:00"; t.scrollTop = 0; stopScroll(); });
})();
</script>
"""

# words that must never reach the public copy: internal figures, the pay line, private links (checked after every web build)
WEB_BANNED = ["הזמנות בכל התקופה", "58% מהרכישות", "המכירות שלי", "לחישוב ה-25%", "claude.ai/artifact", "localhost:8780", "lumebook.json"]


def build_web(d=None):
    d = d or json.loads((HERE / "reels.json").read_text())
    html = page(d, web=True)
    # design.head() adds a script that points claude.ai links at the local pages; it only runs on localhost:8780 and holds the private links
    html = re.sub(r'<script>document\.addEventListener\("DOMContentLoaded",function\(\)\{if\(!/\^\(localhost.*?</script>', "", html, count=1, flags=re.S)
    bad = [w for w in WEB_BANNED if w in html]
    if bad:
        raise SystemExit(f"web calendar not written, internal text found: {bad}")
    OUT_WEB.write_text(html)
    return OUT_WEB


def build(d=None):
    d = d or json.loads((HERE / "reels.json").read_text())
    OUT.write_text(page(d))
    build_web(d)
    return OUT


if __name__ == "__main__":
    print(build())
