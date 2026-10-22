#!/usr/bin/env python3
"""Build the Carousel Machine page (its front page) as one self-contained HTML file.

    python3 carousel/carousel-pipeline/scripts/build_hook_studio_page.py [--date 2026-10-11]

Reads the pack for the date (default: the newest pack that has a recommendation carousel), the validation state of the
games and books carousel (reco-carousel.json; games-carousel.json and books-carousel.json on nights up to 13 Oct 2026), the contact sheets, and any approved production run for the same date. Writes
carousel/carousel-pipeline/hook-studio.html using the LumeBook design system (shared/design). Standard library plus the
macOS `sips` tool for shrinking the contact sheets to JPEG.
"""
import argparse
import base64
import html
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PIPE = HERE.parent
ROOT = PIPE.parent.parent
sys.path.insert(0, str(ROOT / "shared" / "design"))
sys.path.insert(0, str(HERE))
import design  # noqa: E402
import reco_lib  # noqa: E402

OUT = PIPE / "hook-studio.html"
esc = html.escape


def newest_date():
    days = sorted(p.name for p in (PIPE / "drafts").iterdir() if (p / "pack.json").exists())
    with_reco = [d for d in days if reco_lib.present(PIPE / "drafts" / d)]
    return (with_reco or days)[-1]


def options(node):
    if isinstance(node, dict):
        if "slides" in node and "id" in node and "hook" in node:
            yield node
        for v in node.values():
            yield from options(v)
    elif isinstance(node, list):
        for v in node:
            yield from options(v)


def jpeg_uri(png, width=1100):
    if not png.exists():
        return ""
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td) / "x.jpg"
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72", "--resampleWidth", str(width),
                        str(png), "--out", str(out)], check=True, capture_output=True)
        return "data:image/jpeg;base64," + base64.b64encode(out.read_bytes()).decode()


def reco_state(day, fmt):
    path = reco_lib.carousel_path(PIPE / "drafts" / day, fmt)
    if not path.exists():
        return None
    car, issues, st = reco_lib.validate_file(str(path), history=reco_lib.load_history())
    return {"car": car, "errors": [i for i in issues if i.level == "ERROR"], "warns": [i for i in issues if i.level == "WARN"],
            "status": st, "n": len(car.get("slides", []))}


def chip(text, kind=""):
    return f'<span class="lb-chip {kind}">{esc(text)}</span>'


def card_reco(day, fmt, label, st):
    if not st:
        return ""
    if st["errors"]:
        status = chip(f'{len(st["errors"])} שגיאות בבדיקה', "danger")
    else:
        status = chip("עבר את הבדיקה", "success")
    rights = chip("זכויות תמונה לא אומתו", "warning") if not st["status"].get("rights_clear") else chip("זכויות תמונה אומתו", "success")
    img = jpeg_uri(PIPE / "drafts" / day / reco_lib.OUT_DIRS.get(fmt, fmt) / "contact-sheet.png")
    caption = esc(st["car"].get("caption", "")).replace("\n", "<br>")
    errs = "".join(f'<li>{esc(e.message)}</li>' for e in st["errors"])
    err_block = f'<details class="more"><summary>מה נכשל</summary><ul class="lim">{errs}</ul></details>' if errs else ""
    return f'''<article class="lb-card is-flush prod">
  <img class="sheet" src="{img}" alt="גיליון תמונות מוקטנות של {esc(label)}, {st["n"]} שקופיות">
  <div class="body">
    <div class="lb-row between"><h3>{esc(label)}</h3><span class="lb-meta">{st["n"]} שקופיות</span></div>
    <div class="lb-row">{status}{rights}</div>
    <p class="cap">{caption}</p>
    {err_block}
  </div>
</article>'''


def card_kid(day, run, opt):
    state = json.loads((run / "state.json").read_text(encoding="utf-8")) if (run / "state.json").exists() else {"jobs": {}}
    pending = [(k, n) for k, j in state["jobs"].items() for n in j.get("notes", []) if n.startswith("pass-pending")]
    img = jpeg_uri(run / "final" / "contact-sheet.png")
    notes = "".join(f'<li><b class="lb-ltr">{esc(k)}</b> {esc(n.split(":", 1)[1].strip())}</li>' for k, n in pending)
    block = f'<details class="more"><summary>{len(pending)} בעיות תמונה פתוחות</summary><ul class="lim">{notes}</ul></details>' if notes else ""
    return f'''<article class="lb-card is-flush prod">
  <img class="sheet" src="{img}" alt="גיליון תמונות מוקטנות של kid-2, 7 שקופיות">
  <div class="body">
    <div class="lb-row between"><h3>kid-2 · {esc(opt["child_name"])}</h3><span class="lb-meta">7 שקופיות</span></div>
    <div class="lb-row">{chip("הופק", "success")}{chip("kid", "kid")}{chip("כ-0.48$ מתוך 0.50$", "outline")}</div>
    <p class="cap">{esc(opt["title"])}</p>
    {block}
  </div>
</article>'''


def table_options(opts):
    rows = []
    for o in opts:
        kind = "kid" if o["id"].startswith("kid") else "expert"
        heads = " · ".join(esc(s["headline"].replace("\n", " ")) for s in o["slides"])
        who = "אמא" if o["addressee"] == "mom" else "הורים"
        done = chip("הופק", "success") if o["id"] == "kid-2" else ""
        rows.append(f'<tr><td><span class="lb-chip {kind}">{o["id"]}</span> {done}</td>'
                    f'<td>{esc(o["child_name"])}<div class="lb-meta">{who}</div></td>'
                    f'<td class="heads">{heads}</td></tr>')
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    day = (ap.parse_args().date or newest_date())
    pack = json.loads((PIPE / "drafts" / day / "pack.json").read_text(encoding="utf-8"))
    opts = list(options(pack["directions"]))
    topic = pack["topic"]
    history = json.loads((PIPE / "history.json").read_text(encoding="utf-8"))["packs"]
    mixed, games, books = reco_state(day, reco_lib.MIXED), reco_state(day, "games"), reco_state(day, "books")
    run = PIPE / "approved" / f"{day}-kid-2"
    kid2 = next((o for o in opts if o["id"] == "kid-2"), None)
    cards = []
    if kid2 and run.exists():
        cards.append(card_kid(day, run, kid2))
    cards += [card_reco(day, reco_lib.MIXED, "קרוסלת משחקים וספרים", mixed),
              card_reco(day, "games", "קרוסלת משחקים", games), card_reco(day, "books", "קרוסלת ספרים", books)]
    day_he = f'{int(day[8:])}.{int(day[5:7])}.{day[:4]}'

    page = TEMPLATE
    for k, v in {
        "__HEAD__": design.head(), "__TOGGLE__": design.theme_toggle(), "__LOGO__": design.logo_data_uri(),
        "__DAY__": day_he, "__TOPIC__": esc(topic["title_he"]), "__REASON__": esc(topic["reason"]),
        "__CARDS__": "\n".join(cards), "__ROWS__": table_options(opts), "__PACKS__": str(len(history)),
    }.items():
        page = page.replace(k, v)
    assert "__" not in page.replace("__init__", ""), "unfilled placeholder"
    OUT.write_text(page, encoding="utf-8")
    print(OUT, f"{OUT.stat().st_size // 1024} KB", "date", day)


TEMPLATE = r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Carousel Machine</title>
__HEAD__
<style>
/* Carousel Machine page: page rules on top of the LumeBook design system (shared/design/lumebook.css, inlined above). Tokens only. */
:root{--content-w:64rem}
.lb-topbar .lb-brand{padding-inline:0;min-width:0;flex:none}
.lb-topbar .lb-brand img{width:1.75rem;height:1.75rem;border-radius:var(--r-xs);flex:none}
.lb-topbar .lb-brand b{white-space:nowrap}
.lb-section{scroll-margin-top:4.5rem}
.intro{gap:var(--sp-4)}
.stats{--min:9.5rem;gap:var(--sp-3)}
.lb-section > p,.intro > .lb-callout{max-width:42rem}
.prods{--min:19rem}
.prod .sheet{display:block;width:100%;height:auto;background:var(--surface-sunk);border-bottom:1px solid var(--line)}
.prod .body{padding:var(--sp-4) var(--sp-5) var(--sp-5);display:grid;gap:var(--sp-3);min-width:0}
.prod .cap{color:var(--text-2);font-size:var(--fs-callout);line-height:1.5}
.more summary{cursor:pointer;color:var(--tint);font-size:var(--fs-callout);font-weight:600}
.more summary:focus-visible{outline:2px solid var(--focus);outline-offset:2px;border-radius:var(--r-xs)}
ul.lim{margin:var(--sp-2) 0 0;padding-inline-start:1.2rem;color:var(--text-2);font-size:var(--fs-callout);display:grid;gap:var(--sp-1)}
.lb-table{min-width:44rem;font-size:var(--fs-callout)}
.lb-table td{vertical-align:top}
.lb-table td.heads{color:var(--text-2);line-height:1.6}
.lb-table td:first-child{white-space:nowrap}
.flow{--min:20rem}
.flow ol{margin:0;padding-inline-start:1.3rem;display:grid;gap:var(--sp-2);color:var(--text-2);font-size:var(--fs-callout)}
.flow ol b{color:var(--text)}
.rules{margin:0;padding-inline-start:1.2rem;display:grid;gap:var(--sp-2);color:var(--text-2);max-width:42rem}
.rules strong{color:var(--text)}
.cmd{display:grid;gap:var(--sp-1)}
.cmd .lb-row{flex-wrap:nowrap;align-items:stretch}
.cmd pre{margin:0;flex:1 1 auto;min-width:0;overflow-x:auto;direction:ltr;text-align:left;background:var(--surface-sunk);border-radius:var(--r-sm);padding:var(--sp-2) var(--sp-3);font:var(--fs-footnote)/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--text)}
.cmd .lb-btn{flex:none}
.cmd small{color:var(--text-3)}
.kv-wrap{overflow-wrap:anywhere}
@media (max-width:860px){
  .lb-topbar-in{flex-wrap:wrap;row-gap:var(--sp-1);padding-top:var(--sp-2)}
  .lb-topbar .lb-brand{flex:1 1 0}
  .lb-topbar .lb-spacer{display:none}
  .lb-topbar .lb-toc{order:10;flex-basis:100%;margin-inline:calc(-1 * var(--sp-3));padding-bottom:var(--sp-2)}
  .lb-section{scroll-margin-top:7rem}
}
</style>

<div dir="rtl" lang="he">
<header class="lb-topbar"><div class="lb-topbar-in">
  <a class="lb-brand" href="#top"><img src="__LOGO__" alt="" width="28" height="28"><b>Carousel Machine</b></a>
  <nav class="lb-toc" aria-label="פרקים">
    <a href="#today">הלילה האחרון</a><a href="#how">איך זה עובד</a><a href="#slides">שבע השקופיות</a><a href="#rules">כללים</a><a href="#commands">פקודות</a>
  </nav>
  <span class="lb-spacer"></span>
  <a class="lb-btn ghost sm" href="https://claude.ai/artifact/3y8LwbxtTNQW2HAL479aSQ" target="_blank" rel="noopener">לוח לומבוק</a>
  __TOGGLE__
</div></header>

<main class="lb-page" id="top">
<header class="lb-section intro">
  <span class="lb-eyebrow">LumeBook · מכונת הקרוסלות</span>
  <h1>Carousel Machine</h1>
  <p class="lb-lede">כל לילה ב-22:00 המכונה מכינה חבילה אחת: שש אפשרויות לקרוסלה על נושא אחד, וגם קרוסלה אחת של משחקים וספרים. בבוקר בוחרים אפשרות אחת, והיא עוברת הפקה מלאה עם תמונות ועיצוב.</p>
  <div class="stats lb-grid">
    <div class="lb-card lb-stat"><span class="lb-stat-value">6</span><span class="lb-stat-label">אפשרויות בכל חבילה, 3 kid ו-3 expert</span></div>
    <div class="lb-card lb-stat"><span class="lb-stat-value">7</span><span class="lb-stat-label">שקופיות בכל קרוסלה</span></div>
    <div class="lb-card lb-stat"><span class="lb-stat-value">__PACKS__</span><span class="lb-stat-label">חבילות ברישום ההיסטוריה</span></div>
    <div class="lb-card lb-stat"><span class="lb-stat-value">0.50$</span><span class="lb-stat-label">תקרת הוצאה להפקת קרוסלה</span></div>
  </div>
</header>

<section class="lb-section" id="today">
  <div class="lb-section-head"><h2>החבילה של __DAY__</h2><span class="lb-meta">נבנה מהקבצים בתיקיית drafts</span></div>
  <div class="lb-callout"><p><strong>__TOPIC__.</strong> __REASON__</p></div>
  <div class="prods lb-grid">
__CARDS__
  </div>
  <h3>שש האפשרויות, כותרות בלבד</h3>
  <p>הכותרות לבדן מספרות את הסיפור: הרגע, הרגש, מה עומד מאחוריו, שני דברים לנסות, איך זה נגמר וההצעה.</p>
  <div class="lb-table-wrap"><table class="lb-table">
    <thead><tr><th>אפשרות</th><th>ילד או ילדה</th><th>שבע הכותרות לפי הסדר</th></tr></thead>
    <tbody>
__ROWS__
    </tbody>
  </table></div>
</section>

<section class="lb-section" id="how">
  <h2>איך זה עובד</h2>
  <div class="flow lb-grid">
    <div class="lb-card">
      <div class="lb-card-head"><span class="lb-card-title">מצב ראשון · חבילה לילית</span>__NOCOST__</div>
      <ol>
        <li><b>בוחרים נושא</b> מבנק הנושאים לפי עונה ולוח שנה.</li>
        <li><b>בודקים עובדות מוצר</b> באתר החי ושומרים ציטוט מילה במילה.</li>
        <li><b>קוראים מקורות</b> רפואיים או חינוכיים ושומרים ציטוט לכל טענה.</li>
        <li><b>בונים סלייט פתיחים:</b> שישה ל-kid ושישה ל-expert, ומהם שש האפשרויות.</li>
        <li><b>הבדיקה האוטומטית</b> מאשרת את החבילה, ואם יש שגיאה כותבים מחדש את השורה.</li>
        <li><b>קרוסלת משחקים וספרים:</b> בין 7 ל-17 המלצות, 10 עד 20 שקופיות, לפחות 3 משחקים ולפחות 3 ספרים.</li>
      </ol>
    </div>
    <div class="lb-card">
      <div class="lb-card-head"><span class="lb-card-title">מצב שני · הפקה</span><span class="lb-chip accent">עד 0.50$</span></div>
      <ol>
        <li><b>בוחרים אפשרות,</b> למשל kid-2. הבחירה היא גם האישור להוצאה.</li>
        <li><b>מקפיאים טקסט ותמונות</b> לתיקיית approved, בלי עלות.</li>
        <li><b>תמונת ייחוס,</b> בדיקה שלה, ואז שבע התמונות במקביל.</li>
        <li><b>בודקים כל תמונה:</b> פנים, ידיים, אותיות לא רצויות, מי נמצא בסצנה.</li>
        <li><b>העברית עולה כטקסט</b> על התמונה, ומיוצאים קבצי 1080 על 1350.</li>
        <li><b>הודעה אחת:</b> גיליון תמונות, ZIP, ההוצאה וכל בעיה פתוחה.</li>
      </ol>
    </div>
  </div>
</section>

<section class="lb-section" id="slides">
  <h2>שבע השקופיות</h2>
  <p>סדר העבודה: קודם הפתיח, אחר כך התוכן, ובסוף העיצוב. כל שקופית אמורה להצדיק את החלקה בפני עצמה.</p>
  <div class="lb-table-wrap"><table class="lb-table" style="min-width:34rem">
    <thead><tr><th class="num">#</th><th>תפקיד</th><th>המשימה</th></tr></thead>
    <tbody>
      <tr><td class="num">1</td><td>פתיח</td><td>התמונה הממוזערת: מילים שאומרות מה מקבלים, ופנים של הילד מול הצופה בהבעה מוגזמת</td></tr>
      <tr><td class="num">2</td><td>פתיח שני</td><td>עומד בפני עצמו, כי אינסטגרם עשויה להציג את הקרוסלה משקופית 2</td></tr>
      <tr><td class="num">3</td><td>זיהוי או מסגור מחדש</td><td>מה עשוי לעמוד מאחורי הרגש או ההתנהגות</td></tr>
      <tr><td class="num">4, 5</td><td>פתרון</td><td>שני דברים מעשיים, לפחות אחד ממופה למקור</td></tr>
      <tr><td class="num">6</td><td>סגירה</td><td>הסיפור נסגר. בלי ספר, הצעה, קישור או תגובות</td></tr>
      <tr><td class="num">7</td><td>הצעה וקריאה לפעולה</td><td>שורה אחת על סיפור אישי, ואז כתבו "לומי" בתגובות</td></tr>
    </tbody>
  </table></div>
</section>

<section class="lb-section" id="rules">
  <h2>כללים שלא זזים</h2>
  <ul class="rules">
    <li><strong>שלושה קווים קבועים:</strong> הקרוסלה עונה על מה שהפתיח פותח, אין בה דבר לא נכון על ילדים, וההורה לא מושפל ולא מפוחד.</li>
    <li><strong>הילד:</strong> שם ישראלי אחד לכל אפשרות. הפנייה לאמא, או לשני ההורים. אף פעם לא לאבא לבד.</li>
    <li><strong>מילת הקריאה לפעולה</strong> היא תמיד "לומי", בתוך מרכאות, והיא חוזרת בדיוק כך בשקופית 7 ובשורה האחרונה של הכיתוב.</li>
    <li><strong>בלי מותג:</strong> לא כותבים לומבוק ולא שם ספר בשום מקום שהורה קורא. הקישור בתגובה הוא שמוכר.</li>
    <li><strong>בלי אזכור של בינה מלאכותית</strong> בשקופיות, בכיתוב, בטקסט החלופי ובתגובות.</li>
    <li><strong>דוגמאות:</strong> כשרשימה מופיעה על שקופית, היא בת 3 עד 7 פריטים.</li>
    <li><strong>טענות עובדתיות</strong> נרשמות עם המקור והציטוט. כל פתיח הוא השערה של LumeBook עד שיש תוצאות משלה.</li>
    <li><strong>סגנון:</strong> תלת ממד מונפש, אף פעם לא צילום. בלי מקף ארוך בטקסט.</li>
  </ul>
</section>

<section class="lb-section" id="commands">
  <h2>פקודות</h2>
  <p>מריצים מתיקיית הפרויקט. כל פקודה ניתנת להעתקה.</p>
  <div class="lb-grid" style="--min:24rem">
    __CMDS__
  </div>
  <h3>איפה הכול נמצא</h3>
  <dl class="lb-kv kv-wrap">
    <dt>החבילות</dt><dd class="lb-ltr">carousel/carousel-pipeline/drafts/DATE/</dd>
    <dt>ההפקות</dt><dd class="lb-ltr">carousel/carousel-pipeline/approved/DATE-OPTION/final/</dd>
    <dt>בנק הפתיחים</dt><dd class="lb-ltr">carousel/carousel-pipeline/hook-bank.md</dd>
    <dt>בנק הנושאים</dt><dd class="lb-ltr">carousel/carousel-pipeline/topic-bank.md</dd>
    <dt>מדריך מלא</dt><dd class="lb-ltr">carousel/carousel-pipeline/README.md</dd>
  </dl>
</section>
</main>
</div>
<script>
document.addEventListener("click", function (e) {
  var b = e.target.closest("[data-copy]");
  if (!b) return;
  var t = b.getAttribute("data-copy"), done = function () { var o = b.textContent; b.textContent = "הועתק"; setTimeout(function () { b.textContent = o; }, 1400); };
  try { navigator.clipboard.writeText(t).then(done, function () { sel(b); }); } catch (err) { sel(b); }
  function sel(btn) { var pre = btn.parentNode.querySelector("pre"), r = document.createRange(); r.selectNodeContents(pre); var s = getSelection(); s.removeAllRanges(); s.addRange(r); }
});
</script>
'''

CMDS = [
    ("מתחילים לילה: יוצרים תיקייה ומדפיסים הקשר", "python3 carousel/carousel-pipeline/scripts/nightly.py start"),
    ("בודקים ושומרים חבילה", "python3 carousel/carousel-pipeline/scripts/nightly.py finish carousel/carousel-pipeline/drafts/DATE/pack.json"),
    ("בודקים ומרנדרים את קרוסלת המשחקים והספרים", "python3 carousel/carousel-pipeline/scripts/nightly.py finish-reco carousel/carousel-pipeline/drafts/DATE"),
    ("עורכים טקסט בדף הסקירה", "python3 carousel/carousel-pipeline/scripts/review_server.py"),
    ("מקפיאים אפשרות להפקה, בלי עלות", "python3 carousel/carousel-pipeline/scripts/prepare_fal_jobs.py carousel/carousel-pipeline/drafts/DATE/pack.json kid-2"),
    ("מרכיבים את השקופיות וה-ZIP", "python3 carousel/carousel-pipeline/scripts/compose_slides.py carousel/carousel-pipeline/approved/DATE-kid-2"),
    ("תיקון טקסט אחרי יצוא, בלי עלות", 'python3 carousel/carousel-pipeline/scripts/edit_final.py RUN_DIR --slide 2 --body "..."'),
]


def cmd_html():
    out = []
    for label, cmd in CMDS:
        out.append(f'<div class="cmd lb-card"><small>{esc(label)}</small><div class="lb-row"><pre><code>{esc(cmd)}</code></pre>'
                   f'<button class="lb-btn secondary sm" type="button" data-copy="{esc(cmd, quote=True)}">העתקה</button></div></div>')
    return "\n    ".join(out)


TEMPLATE = TEMPLATE.replace("__CMDS__", cmd_html()).replace("__NOCOST__", '<span class="lb-chip success">בלי עלות</span>')

if __name__ == "__main__":
    main()
