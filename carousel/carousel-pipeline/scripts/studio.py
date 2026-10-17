#!/usr/bin/env python3
"""Hook Studio's app shell and its own pages: home, packs, productions.

Yarin, 16 Oct 2026: "i want the entire carousel engine, editor and producer to be viewed in one place i can easily
access" and "design it better using heebo as the main font, better hierarchy and apple design principles, i want it to
look and behave like a professional tool".

One sidebar for every Hook Studio page (review_server.py serves them): בית (/), השבוע (/pool/ID), דירוג (/grade/ID),
הפקות (/productions), חבילות (/packs). The review editors (drafts/DATE/review.html, reco.html) keep their own layout
and get a back link from the server. Design system tokens and lb- components only; Heebo for every line, one tint,
large titles, inset grouped lists, quiet chrome. Light only.
"""

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch  # noqa: E402
import carousel_lib as lib  # noqa: E402
import grades  # noqa: E402
import producer  # noqa: E402
import reco_lib as rl  # noqa: E402
from carousel_lib import esc  # noqa: E402

WEEKDAYS_HE = ("שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון")   # datetime.weekday() order
CLOUD_RUN_UTC = (3, 19, 0)   # the weekly routine: Thursday 19:00 UTC (cron 0 19 * * 4)

ICONS = {
    "home": '<path d="M3.5 10.5 12 3.5l8.5 7V20a1 1 0 0 1-1 1H15v-6H9v6H4.5a1 1 0 0 1-1-1z"/>',
    "pool": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/>',
    "grade": '<path d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/>',
    "produce": '<path d="M12 3.5v11m0 0 4-4m-4 4-4-4"/><path d="M4.5 15.5v3a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-3"/>',
    "packs": '<path d="M7 3.5h7l4.5 4.5v12.5H7z"/><path d="M14 3.5V8h4.5"/><path d="M10 12.5h5M10 16h5"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
}

SHELL_CSS = """
:root{--font-display:var(--font)}
body{font-family:var(--font);background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;direction:rtl;text-align:right}
.lb-brand b{font-family:var(--font);font-weight:700;letter-spacing:-.01em}
.lb-sidebar{background:var(--bar);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px)}
.lb-nav-item{font-weight:500;min-height:2.25rem}
.lb-nav-item[aria-current="page"]{font-weight:600}
.lb-nav-item .lb-count{font-size:var(--fs-caption);font-weight:600;min-width:1.4rem;height:1.25rem;padding:0 .4rem;border-radius:var(--r-pill);background:var(--fill-2);color:var(--text-2);display:inline-flex;align-items:center;justify-content:center;font-variant-numeric:tabular-nums}
.lb-nav-item .lb-count.hot{background:var(--tint);color:var(--text-on-tint)}
.hs-bar{display:flex;align-items:center;gap:var(--sp-2);min-height:3.25rem}
.hs-bar-title{font-weight:600;font-size:var(--fs-callout);opacity:0;transition:opacity .15s}
.hs-bar-title.on{opacity:1}
.hs-bar-actions{margin-inline-start:auto;display:flex;align-items:center;gap:var(--sp-2)}
.hs-head{display:flex;align-items:flex-end;justify-content:space-between;gap:var(--sp-3) var(--sp-5);flex-wrap:wrap}
.hs-title{font-size:2rem;font-weight:700;letter-spacing:-.022em;line-height:1.15;margin:0}
.hs-sub{color:var(--text-2);font-size:var(--fs-body);margin:var(--sp-1) 0 0;max-width:46rem}
.hs-h2{font-size:1.25rem;font-weight:700;letter-spacing:-.012em;margin:0}
.hs-h3{font-size:var(--fs-headline);font-weight:600;margin:0}
.hs-foot{font-size:var(--fs-footnote);color:var(--text-3)}
.hs-row-main{display:grid;gap:2px;min-width:0;flex:1}
.hs-row-main b{font-weight:600;overflow:hidden;text-overflow:ellipsis}
.hs-row-main span{font-size:var(--fs-footnote);color:var(--text-3)}
.hs-chev{color:var(--text-3);flex:none}
.hs-badge{display:inline-flex;align-items:center;justify-content:center;min-width:1.6rem;height:1.6rem;border-radius:var(--r-sm);font-weight:700;font-size:var(--fs-footnote);background:var(--fill-2);color:var(--text-2);font-variant-numeric:tabular-nums;flex:none}
.hs-badge.on{background:var(--tint);color:var(--text-on-tint)}
.hs-id{font-family:var(--font-mono);font-size:var(--fs-caption);color:var(--text-3);direction:ltr;min-width:4.2rem;text-align:left;flex:none}
.hs-pill{display:inline-flex;align-items:center;gap:var(--sp-1);font-size:var(--fs-caption);font-weight:600;padding:.15rem .55rem;border-radius:var(--r-pill);background:var(--fill-2);color:var(--text-2);white-space:nowrap}
.hs-pill.kid{background:var(--kid-soft);color:var(--kid)}
.hs-pill.expert{background:var(--expert-soft);color:var(--expert)}
.hs-pill.reco{background:var(--info-soft);color:var(--info)}
.hs-pill.review{background:var(--accent-soft);color:var(--accent-ink)}
.hs-pill.done{background:var(--success-soft);color:var(--success)}
.hs-pill.failed{background:var(--danger-soft);color:var(--danger)}
.hs-pill.busy{background:var(--tint-soft);color:var(--tint)}
.hs-spin{width:.8rem;height:.8rem;border-radius:50%;border:2px solid currentColor;border-inline-end-color:transparent;animation:hs-spin .8s linear infinite;flex:none}
@keyframes hs-spin{to{transform:rotate(360deg)}}
.hs-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--sp-3)}
.hs-stats .lb-card{padding:var(--sp-4)}
.hs-progress{height:.375rem;border-radius:var(--r-pill);background:var(--fill-2);overflow:hidden}
.hs-progress i{display:block;height:100%;background:var(--tint);border-radius:inherit}
.hs-back{position:fixed;inset-block-end:var(--sp-4);inset-inline-start:var(--sp-4);z-index:80;box-shadow:var(--shadow-2)}
@media (max-width:900px){.hs-stats{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:640px){.hs-title{font-size:1.65rem}}
"""

SHELL_JS = r"""
(() => {
  const sb = document.querySelector('.lb-sidebar'), btn = document.querySelector('.lb-menu-btn');
  let scrim = null;
  const close = () => { sb.classList.remove('is-open'); if (scrim) { scrim.remove(); scrim = null; } };
  if (btn) btn.onclick = () => { if (sb.classList.contains('is-open')) return close(); sb.classList.add('is-open');
    scrim = document.createElement('div'); scrim.className = 'lb-scrim'; scrim.onclick = close; document.body.append(scrim); };
  const t = document.querySelector('.hs-bar-title'), h = document.querySelector('.hs-title');
  if (t && h) new IntersectionObserver(([e]) => t.classList.toggle('on', !e.isIntersecting), {rootMargin: '-56px 0px 0px 0px'}).observe(h);
})();
window.hsToast = (msg) => { let t = document.getElementById('hs-toast'); if (!t) { t = document.createElement('div'); t.id = 'hs-toast'; t.className = 'lb-toast'; t.setAttribute('role', 'status'); document.body.append(t); }
  t.textContent = msg; t.hidden = false; clearTimeout(window.hsToast.t); window.hsToast.t = setTimeout(() => t.hidden = true, 4000); };
window.hsPost = async (url, body) => { const r = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body || {})});
  const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.error || ('HTTP ' + r.status)); return j; };
"""


def icon(name, size=18):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


CHEVRON = ('<svg class="hs-chev" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" aria-hidden="true"><path d="m14.5 6-6 6 6 6"/></svg>')


# ---------------------------------------------------------------- what the sidebar and home need

def current_plan():
    return batch.newest_batch_with_content()


def batch_numbers(plan):
    its = grades.items(plan) if plan else []
    keys = {i["key"] for i in its}
    stored = {k: v for k, v in grades.load()["grades"].items() if k in keys}
    runs = producer.load()["runs"]
    return {
        "items": its,
        "total": len(its),
        "graded": sum(1 for g in stored.values() if g.get("score")),
        "reasons": sum(1 for g in stored.values() if g.get("why")),
        "picked": sum(1 for g in stored.values() if g.get("produce") and not g.get("sent_at")),
        "review": sum(1 for r in runs.values() if r.get("status") == "review"),
        "busy": sum(1 for r in runs.values() if r.get("status") in producer.BUSY),
        "done": sum(1 for r in runs.values() if r.get("status") == "done"),
        "grades": stored,
        "runs": runs,
    }


def next_cloud_run(now=None):
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    wd, hh, mm = CLOUD_RUN_UTC
    days = (wd - now.weekday()) % 7
    at = (now + dt.timedelta(days=days)).replace(hour=hh, minute=mm, second=0, microsecond=0)
    if at <= now:
        at += dt.timedelta(days=7)
    return at.astimezone()


def when_he(moment):
    return f"יום {WEEKDAYS_HE[moment.weekday()]} {moment.day}.{moment.month} · {moment:%H:%M}"


def grades_unsent():
    """True when grades.json has changes main on GitHub does not have yet (the cloud batch reads main)."""
    if not any(g.get("score") for g in grades.load()["grades"].values()):
        return False
    rel_path = str(grades.GRADES.relative_to(lib.PIPELINE.parents[1]))
    root = str(lib.PIPELINE.parents[1])
    try:
        st = subprocess.run(["git", "status", "--porcelain", "--", rel_path], capture_output=True, text=True, cwd=root, timeout=10).stdout.strip()
        ahead = subprocess.run(["git", "log", "--oneline", "origin/main..HEAD", "--", rel_path], capture_output=True, text=True, cwd=root, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return bool(st or ahead) if grades.GRADES.exists() else False


def push_grades():
    """Commit grades.json alone and push main, so next Thursday's cloud batch reads them. Only from the button."""
    root = str(lib.PIPELINE.parents[1])
    rel_path = str(grades.GRADES.relative_to(lib.PIPELINE.parents[1]))

    def git(*args, timeout=60):
        p = subprocess.run(["git", *args], capture_output=True, text=True, cwd=root, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()

    code, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if code or branch != "main":
        return {"ok": False, "error": f"הענף הנוכחי הוא {branch}, לא main. שלחו מקלוד."}
    if not grades.GRADES.exists():
        return {"ok": False, "error": "אין עדיין דירוגים"}
    git("add", "--", rel_path)
    code, out = git("commit", "--only", "-m", "Hook Studio grades for the next weekly batch", "--", rel_path)
    if code and "nothing to commit" not in out and "no changes added" not in out:
        return {"ok": False, "error": out[-600:]}
    code, out = git("push", "origin", "main", timeout=90)
    if code:
        return {"ok": False, "error": out[-600:]}
    return {"ok": True}


# ---------------------------------------------------------------- the shell

def page(title, active, body, *, subtitle="", actions="", css="", script="", head_extra=""):
    import create_review
    design = create_review.design
    plan = current_plan()
    n = batch_numbers(plan) if plan else {"total": 0, "graded": 0, "review": 0, "busy": 0}
    bid = plan["id"] if plan else ""
    left = n["total"] - n["graded"]
    nav = [("home", "/", "בית", ""),
           ("pool", f"/pool/{bid}" if bid else "/packs", "השבוע", ""),
           ("grade", f"/grade/{bid}" if bid else "/packs", "דירוג", f'<span class="lb-count">{left}</span>' if left else ""),
           ("produce", "/productions", "הפקות", f'<span class="lb-count hot">{n["review"]}</span>' if n["review"] else (f'<span class="lb-count">{n["busy"]}</span>' if n["busy"] else "")),
           ("packs", "/packs", "חבילות ועריכה", "")]
    current = ' aria-current="page"'
    items = "".join(f'<a class="lb-nav-item" href="{href}"{current if key == active else ""}>{icon(key)}<span>{label}</span>{count}</a>'
                    for key, href, label, count in nav)
    week = ""
    if plan:
        dates = [s["date"] for s in plan["slots"]]
        week = f'השבוע: {dates[0][8:]}.{int(dates[0][5:7])} עד {dates[-1][8:]}.{int(dates[-1][5:7])}'
    nxt = next_cloud_run()
    sub = f'<p class="hs-sub">{subtitle}</p>' if subtitle else ""
    return ('<!doctype html>\n<html lang="he" dir="rtl">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title if title == "Hook Studio" else title + " · Hook Studio")}</title>{design.head()}<style>{SHELL_CSS}{css}</style>{head_extra}</head>\n'
            '<body dir="rtl"><div class="lb-app">'
            '<aside class="lb-sidebar" aria-label="ניווט">'
            f'<a class="lb-brand" href="/"><img src="{design.logo_data_uri()}" alt="" width="32" height="32"><span><b>Hook Studio</b><small>LumeBook</small></span></a>'
            f'<nav class="lb-nav">{items}</nav>'
            f'<div class="lb-sidebar-foot"><span>{esc(week)}</span><span>הבאץ\' הבא: {esc(when_he(nxt))}</span></div></aside>'
            '<div class="lb-main"><header class="lb-topbar"><div class="lb-topbar-in hs-bar">'
            f'<button class="lb-btn ghost icon lb-menu-btn" type="button" aria-label="תפריט">{icon("menu")}</button>'
            f'<span class="hs-bar-title">{esc(title)}</span><div class="hs-bar-actions">{actions}</div></div></header>'
            f'<main class="lb-page"><div class="hs-head"><div><h1 class="hs-title">{esc(title)}</h1>{sub}</div></div>{body}</main></div></div>'
            f'<script>{SHELL_JS}</script>{f"<script>{script}</script>" if script else ""}</body></html>')


BACK_LINK = '<a class="lb-btn secondary sm hs-back" href="/" style="position:fixed;bottom:16px;left:16px;z-index:80">Hook Studio</a>'


# ---------------------------------------------------------------- home

def home_page():
    plan = current_plan()
    if not plan:
        return page("בית", "home", '<p class="lb-empty">אין עדיין באץ\' שבועי. החבילות הישנות נמצאות ב<a href="/packs">חבילות ועריכה</a>.</p>')
    n = batch_numbers(plan)
    bid = plan["id"]
    pct = round(100 * n["graded"] / n["total"]) if n["total"] else 0
    stats = [("דורגו", f'{n["graded"]}<small>מתוך {n["total"]}</small>', f'<div class="hs-progress" aria-hidden="true"><i style="width:{pct}%"></i></div>'),
             ("עם הסבר", str(n["reasons"]), '<span class="lb-stat-foot">ייכנסו לבאץ\' הבא</span>'),
             ("מחכות לאישור שלך", str(n["review"]), '<span class="lb-stat-foot">תמונות להפקה</span>'),
             ("מוכנות לפרסום", str(n["done"]), '<span class="lb-stat-foot">ZIP מוכן להורדה</span>')]
    stat_html = '<div class="hs-stats">' + "".join(
        f'<div class="lb-card lb-stat"><span class="lb-stat-label">{label}</span><span class="lb-stat-value">{value}</span>{foot}</div>' for label, value, foot in stats) + '</div>'

    todo = []
    if n["review"]:
        todo.append(('/productions', "produce", f'מחכות לאישור שלך: {n["review"]}', "לאשר את התמונה או לבקש אחרת, ואז הייצוא רץ לבד"))
    left = n["total"] - n["graded"]
    if left:
        todo.append((f'/grade/{bid}', "grade", f'להמשיך לדרג ({left} נשארו)', "ציון, הסבר קצר, ובחירה להפקה"))
    if n["picked"]:
        todo.append((f'/grade/{bid}', "produce", f'נבחרו להפקה ועוד לא נשלחו: {n["picked"]}', "כפתור ״הפקת הנבחרים״ בדף הדירוג"))
    if n["busy"]:
        todo.append(('/productions', "produce", f'בהפקה עכשיו: {n["busy"]}', "אפשר להמשיך לעבוד, זה רץ ברקע"))
    todo_html = ""
    if todo:
        todo_html = ('<section class="lb-section"><h2 class="hs-h2">מה עכשיו</h2><div class="lb-group">' + "".join(
            f'<a class="lb-group-row" href="{href}">{icon(ic, 20)}<span class="hs-row-main"><b>{esc(t)}</b><span>{esc(s)}</span></span>{CHEVRON}</a>'
            for href, ic, t, s in todo) + '</div></section>')

    rows = []
    for slot in plan["slots"]:
        folder = lib.DRAFTS / slot["date"]
        pack = lib.read_json(folder / "pack.json") if (folder / "pack.json").exists() else None
        topic = (pack or {}).get("topic", {})
        title = topic.get("title_he") or slot.get("topic_he") or "משבצת אירוע"
        mine = [i for i in n["items"] if i["date"] == slot["date"]]
        done = sum(1 for i in mine if n["grades"].get(i["key"], {}).get("score"))
        d = dt.date.fromisoformat(slot["date"])
        event = (topic.get("event") or {}).get("name_he")
        tag = f'<span class="hs-pill review">אירוע</span>' if event else ""
        state = f'<span class="hs-foot">{done}/{len(mine)} דורגו</span>' if mine else '<span class="hs-foot">עוד לא הגיע</span>'
        rows.append(f'<a class="lb-group-row" href="/pool/{bid}#slot-{slot["n"]}"><span class="hs-badge">{slot["n"]}</span>'
                    f'<span class="hs-row-main"><b>{esc(title)}</b><span>יום {WEEKDAYS_HE[d.weekday()]} {d.day}.{d.month}</span></span>{tag}{state}{CHEVRON}</a>')
    week_html = f'<section class="lb-section"><div class="lb-section-head"><h2 class="hs-h2">השבוע</h2><a class="lb-btn ghost sm" href="/pool/{bid}">כל המאגר</a></div><div class="lb-group">{"".join(rows)}</div></section>'

    unsent = grades_unsent()
    learn = ('<section class="lb-section"><h2 class="hs-h2">הבאץ\' הבא לומד ממך</h2><div class="lb-card">'
             f'<p style="margin:0">ביום חמישי ({esc(when_he(next_cloud_run()))}) הענן כותב את השבוע הבא, וקורא קודם את הציונים וההסברים שלך. '
             'ציון 4 עד 5 עם הסבר מלמד אותו מה לעשות יותר, 1 עד 2 מה להפסיק.</p>'
             '<div class="lb-toolbar">'
             + ('<button class="lb-btn" type="button" id="hs-push">שליחת הדירוגים לענן</button><span class="hs-foot" id="hs-push-state">יש דירוגים שהענן עוד לא ראה</span>' if unsent
                else '<span class="hs-pill done">הענן מעודכן</span>' if unsent is False and n["graded"] else '<span class="hs-foot">עוד אין דירוגים לשלוח</span>')
             + '<button class="lb-btn secondary" type="button" id="hs-sync">בדיקת חבילות חדשות מהענן</button></div></div></section>')
    script = r"""
const push = document.getElementById('hs-push');
if (push) push.onclick = async () => { push.disabled = true; push.textContent = 'שולח...';
  try { await hsPost('/api/push-grades'); hsToast('הדירוגים נשלחו. הבאץ\' הבא יקרא אותם'); setTimeout(() => location.reload(), 900); }
  catch (e) { hsToast('השליחה נכשלה: ' + e.message); push.disabled = false; push.textContent = 'שליחת הדירוגים לענן'; } };
const sync = document.getElementById('hs-sync');
sync.onclick = async () => { sync.disabled = true; sync.textContent = 'בודק...';
  try { const j = await hsPost('/api/sync'); hsToast(j.new ? `הגיעו ${j.new} חבילות חדשות` : 'אין חדש בענן'); if (j.new) setTimeout(() => location.reload(), 900); }
  catch (e) { hsToast('הבדיקה נכשלה: ' + e.message); }
  sync.disabled = false; sync.textContent = 'בדיקת חבילות חדשות מהענן'; };
"""
    actions = f'<a class="lb-btn sm" href="/grade/{bid}">{icon("grade", 16)}<span>לדרג</span></a>'
    sub = f'{n["total"]} קרוסלות בשבעה נושאים. מדרגים, מסמנים להפקה, ומורידים ZIP מוכן, הכול מכאן.'
    return page("Hook Studio", "home", stat_html + todo_html + week_html + learn, subtitle=sub, actions=actions, script=script)


# ---------------------------------------------------------------- packs: every draft with its editors

def packs_page():
    plans = {s["date"]: p["id"] for p in batch.plans() for s in p.get("slots", [])}
    dates = sorted((p.name for p in lib.DRAFTS.iterdir() if p.is_dir() and len(p.name) == 10 and (p / "review.html").exists()), reverse=True) if lib.DRAFTS.exists() else []
    groups = {}
    for date in dates:
        groups.setdefault(plans.get(date, ""), []).append(date)
    parts = []
    for bid, ds in groups.items():
        rows = []
        for date in ds:
            folder = lib.DRAFTS / date
            try:
                topic = lib.read_json(folder / "pack.json").get("topic", {})
            except (OSError, ValueError):
                topic = {}
            d = dt.date.fromisoformat(date)
            links = [f'<a class="lb-btn secondary sm" href="/drafts/{date}/review.html">ילד ומומחה</a>']
            for fmt in rl.FORMATS:
                if rl.carousel_path(folder, fmt).exists():
                    page_name = {rl.MIXED: "reco.html", rl.MIXED2: "reco-2.html", "games": "games.html", "books": "books.html"}[fmt]
                    if (folder / page_name).exists():
                        links.append(f'<a class="lb-btn secondary sm" href="/drafts/{date}/{page_name}">{esc(rl.FORMAT_HE[fmt])}</a>')
            rows.append(f'<div class="lb-group-row"><span class="hs-row-main"><b>{esc(topic.get("title_he", date))}</b>'
                        f'<span>יום {WEEKDAYS_HE[d.weekday()]} {d.day}.{d.month}.{d.year}</span></span><span class="lb-toolbar">{"".join(links)}</span></div>')
        head = f'באץ\' {esc(bid)}' if bid else 'חבילות לילה (לפני הבאץ\' השבועי)'
        tools = f'<a class="lb-btn ghost sm" href="/pool/{esc(bid)}">מאגר</a><a class="lb-btn ghost sm" href="/grade/{esc(bid)}">דירוג</a>' if bid else ""
        parts.append(f'<section class="lb-section"><div class="lb-section-head"><h2 class="hs-h2">{head}</h2><span class="lb-toolbar">{tools}</span></div><div class="lb-group">{"".join(rows)}</div></section>')
    body = "".join(parts) or '<p class="lb-empty">אין עדיין חבילות.</p>'
    return page("חבילות ועריכה", "packs", body, subtitle="כל חבילה עם עמודי העריכה שלה. לוחצים על טקסט ומקלידים, ״שמירה״ או Cmd+S שומר עם גיבוי.")


# ---------------------------------------------------------------- productions

PROD_CSS = """
.pr-list{display:grid;gap:var(--sp-4)}
.pr-card{display:grid;grid-template-columns:13rem minmax(0,1fr);gap:var(--sp-5);align-items:start}
.pr-media{display:block;border-radius:var(--r-md);overflow:hidden;background:var(--surface-2);aspect-ratio:4/5;border:1px solid var(--line)}
.pr-media img{display:block;width:100%;height:100%;object-fit:cover}
.pr-media.wide{aspect-ratio:auto}
.pr-media.wide img{height:auto}
.pr-media .ph{display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-3);font-size:var(--fs-footnote);gap:var(--sp-2)}
.pr-media.empty{aspect-ratio:auto;min-height:6rem}
.pr-body{display:grid;gap:var(--sp-3);min-width:0}
.pr-top{display:flex;align-items:center;gap:var(--sp-2);flex-wrap:wrap}
.pr-cover{font-size:var(--fs-headline);font-weight:600;line-height:1.35;margin:0}
.pr-meta{font-size:var(--fs-footnote);color:var(--text-3)}
.pr-checks{margin:0;padding:0;list-style:none;display:grid;gap:var(--sp-1);font-size:var(--fs-callout);color:var(--text-2)}
.pr-checks li::before{content:"";display:inline-block;width:.4rem;height:.4rem;border-radius:50%;background:var(--accent);margin-inline-end:var(--sp-2);vertical-align:middle}
.pr-err{white-space:pre-wrap;font-family:var(--font);direction:auto;font-size:var(--fs-footnote);color:var(--danger);background:var(--danger-soft);border-radius:var(--r-sm);padding:var(--sp-2) var(--sp-3);margin:0}
.pr-warn{font-size:var(--fs-footnote);color:var(--warning);background:var(--warning-soft);border-radius:var(--r-sm);padding:var(--sp-2) var(--sp-3);margin:0}
.pr-redo{display:grid;gap:var(--sp-2)}
.pr-redo[hidden]{display:none}
.pr-filter{margin-inline-start:auto}
@media (max-width:700px){.pr-card{grid-template-columns:minmax(0,1fr)}.pr-media{max-width:16rem}}
"""

PROD_JS = r"""
const QA = __QA__;
let runs = __RUNS__;
let filter = 'all';
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const KIND = {kid: 'הילד מספר', expert: 'גישה מקצועית', reco: 'משחקים וספרים'};
const ORDER = {review: 0, failed: 1, queued: 2, preparing: 2, generating: 2, composing: 2, exporting: 2, done: 3};
const BUSY = ['queued', 'preparing', 'generating', 'composing', 'exporting'];
function pill(r) {
  const cls = r.status === 'review' ? 'review' : r.status === 'done' ? 'done' : r.status === 'failed' ? 'failed' : 'busy';
  const p = el('span', 'hs-pill ' + cls);
  if (BUSY.includes(r.status)) p.append(el('span', 'hs-spin'));
  p.append(document.createTextNode(r.status_he || r.status)); return p;
}
async function act(url, body, msg) {
  try { const j = await hsPost(url, body); runs[j.run.key] = j.run; render(); if (msg) hsToast(msg); poll(); }
  catch (e) { hsToast(e.message); }
}
function card(r) {
  const c = el('article', 'lb-card pr-card'); c.id = r.key;
  const media = el(r.status === 'done' && r.contact_sheet ? 'a' : 'div', 'pr-media' + (r.status === 'done' && r.contact_sheet ? ' wide' : ''));
  const src = r.status === 'done' ? (r.contact_sheet || (r.slides || [])[0]) : r.picture;
  if (src) { const img = el('img'); img.src = src; img.alt = ''; media.append(img); if (media.tagName === 'A') { media.href = src; media.target = '_blank'; } }
  else { media.classList.add('empty'); const ph = el('div', 'ph'); if (BUSY.includes(r.status)) ph.append(el('span', 'hs-spin')); ph.append(document.createTextNode(r.kind === 'reco' ? 'שקופיות מוכנות' : 'עוד אין תמונה')); media.append(ph); }
  const b = el('div', 'pr-body');
  const top = el('div', 'pr-top');
  top.append(pill(r), el('span', 'hs-pill ' + r.kind, KIND[r.kind] || r.kind), el('span', 'hs-id', r.date + ' · ' + r.id));
  b.append(top, el('p', 'pr-cover', r.cover || ''));
  const meta = [r.topic_he, r.child_name, r.skill_he, r.spent_usd != null && r.kind !== 'reco' ? `$${Number(r.spent_usd).toFixed(2)} מתוך $0.50` : null].filter(Boolean).join(' · ');
  b.append(el('div', 'pr-meta', meta));
  if (r.error) b.append(el('pre', 'pr-err', r.error));
  if (r.warning) b.append(el('p', 'pr-warn', r.warning));
  const tools = el('div', 'lb-toolbar');
  if (r.status === 'review') {
    const ul = el('ul', 'pr-checks'); QA.forEach(q => ul.append(el('li', null, q))); b.append(ul);
    const ok = el('button', 'lb-btn', 'מאשר, להרכיב את השקופיות'); ok.type = 'button';
    ok.onclick = () => act('/api/production/approve', {key: r.key}, 'מרכיב את השקופיות');
    const again = el('button', 'lb-btn secondary', 'תמונה אחרת'); again.type = 'button';
    const left = 2 - (r.replacements || 0);
    if (left <= 0) { again.disabled = true; again.title = 'נוצרו כבר 3 תמונות'; }
    const box = el('div', 'pr-redo'); box.hidden = true;
    const ta = el('textarea', 'lb-textarea'); ta.rows = 2; ta.placeholder = 'מה לשנות? למשל: הפנים לא למצלמה, יותר מדי אנשים, אותיות על החולצה';
    const go = el('button', 'lb-btn sm', 'לייצר שוב'); go.type = 'button';
    go.onclick = () => { if (!ta.value.trim()) { ta.focus(); return; } act('/api/production/redo', {key: r.key, note: ta.value.trim()}, 'מייצר תמונה חדשה'); };
    box.append(ta, go);
    again.onclick = () => { box.hidden = !box.hidden; if (!box.hidden) ta.focus(); };
    tools.append(ok, again, el('span', 'hs-foot', left > 0 ? `עוד ${left} ניסיונות` : 'אין עוד ניסיונות'));
    b.append(tools, box);
  } else if (r.status === 'done') {
    if (r.zip) { const a = el('a', 'lb-btn', 'הורדת ZIP'); a.href = r.zip; a.download = ''; tools.append(a); }
    const f = el('button', 'lb-btn secondary', 'הצגה ב-Finder'); f.type = 'button'; f.onclick = () => act('/api/production/reveal', {key: r.key}); tools.append(f);
    if (r.rtl_check) { const a = el('a', 'lb-btn ghost', 'בדיקת כיוון'); a.href = r.rtl_check; a.target = '_blank'; tools.append(a); }
    if (r.caption_file) { const a = el('a', 'lb-btn ghost', 'כיתוב'); a.href = r.caption_file; a.target = '_blank'; tools.append(a); }
    const again = el('button', 'lb-btn ghost', 'ייצוא מחדש'); again.type = 'button'; again.title = 'אחרי עריכת טקסט: בלי תמונה חדשה ובלי עלות';
    again.onclick = () => act('/api/production/start', {key: r.key}, 'מייצא מחדש'); tools.append(again);
    b.append(tools);
  } else if (r.status === 'failed') {
    const again = el('button', 'lb-btn', 'להמשיך'); again.type = 'button';
    again.onclick = () => act('/api/production/start', {key: r.key}, 'ממשיך'); tools.append(again); b.append(tools);
  }
  c.append(media, b); return c;
}
function render() {
  const box = document.getElementById('pr-list'); box.textContent = '';
  const list = Object.values(runs).filter(r => filter === 'all' || (filter === 'review' ? r.status === 'review' : filter === 'done' ? r.status === 'done' : BUSY.includes(r.status) || r.status === 'failed'))
    .sort((a, b) => (ORDER[a.status] ?? 9) - (ORDER[b.status] ?? 9) || (b.updated_at || '').localeCompare(a.updated_at || ''));
  if (!list.length) { box.append(el('p', 'lb-empty', Object.keys(runs).length ? 'אין כאן כלום בסינון הזה' : 'עוד לא הופק כלום. בדף הדירוג מסמנים ״להפקה״ ולוחצים ״הפקת הנבחרים״.')); }
  list.forEach(r => box.append(card(r)));
  document.querySelectorAll('.pr-filter button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.f === filter)));
}
let timer = null;
function poll() {
  clearTimeout(timer);
  if (!Object.values(runs).some(r => BUSY.includes(r.status))) return;
  timer = setTimeout(async () => { try { const j = await (await fetch('/api/productions')).json(); runs = j.runs; render(); } catch (e) {} poll(); }, 3000);
}
document.querySelectorAll('.pr-filter button').forEach(b => b.onclick = () => { filter = b.dataset.f; render(); });
render(); poll();
if (location.hash) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) t.scrollIntoView({block: 'center'}); }
"""


def productions_page():
    runs = producer.load()["runs"]
    filt = ('<div class="lb-segmented pr-filter" role="group" aria-label="סינון">'
            '<button type="button" data-f="all">הכול</button><button type="button" data-f="review">לאישור</button>'
            '<button type="button" data-f="busy">בתהליך</button><button type="button" data-f="done">מוכנות</button></div>')
    body = f'<section class="lb-section"><div class="lb-section-head"><span></span>{filt}</div><div class="pr-list" id="pr-list"></div></section>'
    script = PROD_JS.replace("__QA__", json.dumps(producer.QA_CHECKS_HE, ensure_ascii=False)).replace("__RUNS__", json.dumps(runs, ensure_ascii=False).replace("</", "<\\/"))
    sub = "קרוסלת ילד או מומחה: תמונה אחת (עד $0.50), מאשרים אותה או מבקשים אחרת, והשקופיות וה-ZIP נבנים לבד. משחקים וספרים: ייצוא מיידי בלי עלות."
    return page("הפקות", "produce", body, subtitle=sub, css=PROD_CSS, script=script)
