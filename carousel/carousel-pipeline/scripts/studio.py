#!/usr/bin/env python3
"""Carousel Machine: the whole carousel engine on one page, http://localhost:8777/ (review_server.py serves it).

Yarin, 16 and 17 Oct 2026: "i want the entire carousel engine, editor and producer to be viewed in one place i can
easily access", "design it better using heebo as the main font, better hierarchy and apple design principles",
"why cant i edit them directly from the local host?" and "i want one page for everything without any subpages".

Yarin, 24 Oct 2026: "instead of the current layout i want a grid that shows the first slide of each carousel and only
when i click on it the carousel exapnds so i can view it all with all the necessary controls. i want the side panel to
view what carousels i chose to produce with a button to batch produce them".

One screen (RTL): a grid of slide 1 of every carousel of the week, grouped by topic (filter: all, to grade,
production, waiting for approval; "+ להפקה" on each card picks it). A click opens the carousel in a sheet: every
headline, body, highlight, caption and CTA editable in place (saved through the editors' own save: backup, voice log,
validation, rebuilt pages; games and books slides are re-rendered), and beside it the grade, the reason, the produce
switch and its production (picture to approve or redo, ZIP, Finder). The side panel lists the picked carousels with
one button that produces them all, then the ones in production or done. The top bar has the week, progress, what
waits for approval and the cloud buttons. Everything loads from /api/state; old addresses (/pool, /grade,
/productions, /packs) open this page.
Design system tokens and lb- components; Heebo for the interface, the pillar fonts only on the slide cards. Light only.
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
from carousel_lib import esc  # noqa: E402

WEEKDAYS_HE = ("שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון")   # datetime.weekday() order
CLOUD_RUN_UTC = (3, 19, 0)   # the weekly routine: Thursday 19:00 UTC (cron 0 19 * * 4)

ICONS = {
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "sync": '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20v-4h-4"/>',
}


def icon(name, size=18):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def current_plan():
    return batch.newest_batch_with_content()


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
    code, out = git("commit", "--only", "-m", "Carousel Machine grades for the next weekly batch", "--", rel_path)
    if code and "nothing to commit" not in out and "no changes added" not in out:
        return {"ok": False, "error": out[-600:]}
    code, out = git("push", "origin", "main", timeout=90)
    if code:
        return {"ok": False, "error": out[-600:]}
    return {"ok": True}


BACK_LINK = '<a class="lb-btn secondary sm" href="/" style="position:fixed;bottom:16px;left:16px;z-index:80">Carousel Machine</a>'

# ---------------------------------------------------------------- the one page

def batches():
    """Every weekly plan that has packs here, newest first."""
    return [p["id"] for p in reversed(batch.plans()) if any((lib.DRAFTS / s["date"] / "pack.json").exists() for s in p.get("slots", []))]


def state(batch_id=None):
    """Everything the page shows, as JSON: the carousels, the grades, the productions, the cloud status."""
    plan = batch.load(batch_id) if batch_id else current_plan()
    if not plan:
        return {"batch": None, "batches": batches(), "items": [], "grades": {}, "runs": {}}
    its = grades.items(plan)
    for it in its:
        it["errors"] = producer.blocking_errors(it)
    keys = {i["key"] for i in its}
    nxt = next_cloud_run()
    dates = [s["date"] for s in plan["slots"]]
    weeks = batches()
    if plan["id"] not in weeks:   # a plan whose packs are still on their way from the cloud
        weeks.insert(0, plan["id"])
    return {"batch": plan["id"], "batches": weeks, "items": its,
            "week_he": f"{int(dates[0][8:])}.{int(dates[0][5:7])} עד {int(dates[-1][8:])}.{int(dates[-1][5:7])}",
            "grades": {k: v for k, v in grades.load()["grades"].items() if k in keys},
            "runs": {k: v for k, v in producer.load()["runs"].items() if k in keys},
            "unsent": bool(grades_unsent()), "next_run_he": when_he(nxt), "qa": list(producer.QA_CHECKS_HE)}


APP_CSS = """
:root{--font-display:var(--font);--hs-top:3.5rem}
html,body{height:100%}
body{margin:0;font-family:var(--font);background:var(--bg);color:var(--text);direction:rtl;text-align:right;-webkit-font-smoothing:antialiased;overflow:hidden}
button{font-family:inherit}
.hs-top{position:relative;z-index:30;height:var(--hs-top);display:flex;align-items:center;gap:var(--sp-3);padding-inline:var(--sp-4);background:var(--bar);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid var(--line)}
.hs-brand{display:flex;align-items:center;gap:var(--sp-2);font-weight:700;letter-spacing:-.01em;white-space:nowrap;font-size:var(--fs-headline)}
.hs-brand img{width:1.75rem;height:1.75rem;border-radius:var(--r-xs)}
.hs-week{font:inherit;font-size:var(--fs-footnote);color:var(--text-2);background:var(--fill);border:0;border-radius:var(--r-sm);padding:.3rem .6rem}
.hs-meter{display:flex;align-items:center;gap:var(--sp-2);font-size:var(--fs-footnote);color:var(--text-2);white-space:nowrap;font-variant-numeric:tabular-nums}
.hs-meter .bar{width:8rem;height:.375rem;border-radius:var(--r-pill);background:var(--fill-2);overflow:hidden}
.hs-meter .bar i{display:block;height:100%;background:var(--tint);border-radius:inherit;transition:width .3s}
.hs-sp{flex:1}
.hs-top .lb-btn{white-space:nowrap}
.hs-pickbtn{display:none}
.hs-app{display:grid;grid-template-columns:minmax(0,1fr) 21rem;height:calc(100vh - var(--hs-top))}
.hs-main{overflow-y:auto;min-width:0;padding:0 var(--sp-6) var(--sp-7);container-type:inline-size}
.hs-filter{position:sticky;top:0;z-index:3;background:var(--bg);padding:var(--sp-4) 0 var(--sp-3)}
.hs-filter .lb-segmented{display:flex;max-width:30rem}
.hs-filter .lb-segmented button{flex:1;padding-inline:.3rem}
.hs-group{margin-top:var(--sp-4)}
.hs-group>h2{display:flex;align-items:center;gap:var(--sp-2);font-size:var(--fs-headline);font-weight:600;letter-spacing:-.01em;margin:0 0 var(--sp-3)}
.hs-group>h2 .n{font-family:var(--font-2);color:var(--text-3);font-variant-numeric:tabular-nums}
.hs-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--sp-5) var(--sp-4)} /* a topic's 3 kid and 3 expert options: one row each, or all six on one row */
@container (min-width:60rem){.hs-cards{grid-template-columns:repeat(6,minmax(0,1fr))}}
/* A day since 24 Oct 2026: two topics side by side, each with its three child-voice options */
.hs-day{display:grid;grid-template-columns:minmax(0,1fr);gap:var(--sp-5)}
.hs-lane>h3{font-size:var(--fs-callout);font-weight:600;color:var(--text-2);margin:0 0 var(--sp-2)}
@container (min-width:60rem){.hs-day{grid-template-columns:repeat(2,minmax(0,1fr))}.hs-day .hs-cards{grid-template-columns:repeat(3,minmax(0,1fr))}}
.gc{position:relative;display:grid;gap:var(--sp-2);align-content:start;min-width:0}
.gc-thumb{display:block;width:100%;padding:0;border:0;background:none;cursor:pointer;border-radius:var(--r-lg);transition:transform .15s ease;container-type:inline-size}
.gc-thumb:hover{transform:translateY(-2px)}
.gc-thumb:focus-visible{outline:none}
.gc-thumb:focus-visible>*{box-shadow:0 0 0 3px var(--tint)}
.gc-thumb img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:var(--r-lg);border:1px solid var(--line);box-shadow:var(--shadow-1)}
.gc-thumb .st-card{overflow:hidden;box-shadow:var(--shadow-1);text-align:right}
.gc-thumb .st-card .h{font-size:clamp(.9rem,8.5cqi,1.4rem);line-height:1.22;display:-webkit-box;-webkit-line-clamp:7;-webkit-box-orient:vertical;overflow:hidden}
.gc-thumb .st-card .b{display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.gc.picked .gc-thumb>*{box-shadow:0 0 0 3px var(--tint)}
.gc-frame{position:relative}
.gc-pick{position:absolute;bottom:var(--sp-2);inset-inline-end:var(--sp-2);z-index:1;display:inline-flex;align-items:center;height:1.75rem;padding:0 .65rem;border:0;border-radius:var(--r-pill);background:var(--surface);color:var(--text);font-family:var(--font-2);font-size:var(--fs-caption);font-weight:700;box-shadow:var(--shadow-2);cursor:pointer}
.gc-pick[aria-pressed="true"]{background:var(--tint);color:var(--text-on-tint)}
.gc-meta{display:flex;align-items:center;gap:var(--sp-2);font-family:var(--font-2);font-size:var(--fs-caption);color:var(--text-3);min-width:0}
.gc-meta .who{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gc-meta .hs-pill{flex:none}
.hs-picks{overflow-y:auto;background:var(--surface);border-inline-start:1px solid var(--line);padding:var(--sp-5) var(--sp-4) var(--sp-6);display:flex;flex-direction:column;gap:var(--sp-3)}
.pk-head{display:flex;align-items:baseline;gap:var(--sp-2)}
.pk-head h2{margin:0;font-size:var(--fs-headline);font-weight:700}
.pk-head .c{font-family:var(--font-2);color:var(--text-3);font-variant-numeric:tabular-nums}
.pk-send{display:grid;gap:var(--sp-2)}
.pk-send .lb-btn{width:100%;justify-content:center}
.pk-send .in-keys:empty{display:none}
.pk-list{display:grid;gap:2px}
.pk-sub{font-family:var(--font-2);font-size:var(--fs-caption);font-weight:600;color:var(--text-3);margin:var(--sp-3) 0 0}
.pk-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:var(--sp-2);align-items:center;padding:var(--sp-2);border-radius:var(--r-md)}
.pk-row:hover{background:var(--fill)}
.pk-open{display:grid;grid-template-columns:2.6rem minmax(0,1fr);gap:var(--sp-3);align-items:center;padding:0;border:0;background:none;color:var(--text);text-align:right;cursor:pointer;min-width:0}
.pk-mini{display:block;width:2.6rem;aspect-ratio:4/5;border-radius:var(--r-xs);overflow:hidden;border:1px solid var(--line)}
.pk-mini.kid{background:#F8F4FF}.pk-mini.expert{background:#FCF7EE}.pk-mini.reco{background:var(--info-soft)}
.pk-mini img{display:block;width:100%;height:100%;object-fit:cover}
.pk-open .t{font-size:var(--fs-footnote);font-weight:500;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pk-open .m{display:block;font-family:var(--font-2);font-size:var(--fs-caption);color:var(--text-3);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pk-x{width:1.75rem;height:1.75rem;border:0;border-radius:50%;background:none;color:var(--text-3);cursor:pointer;font-size:1.15rem;line-height:1}
.pk-x:hover{background:var(--fill-2);color:var(--text)}
.pk-empty{font-size:var(--fs-footnote);color:var(--text-3);margin:0;line-height:1.6}
.hs-picks .hs-foot{margin-top:auto;padding:var(--sp-4) 0 0}
.hs-open{position:fixed;inset:0;z-index:50;background:var(--overlay);display:flex;justify-content:center;padding:var(--sp-5)}
.hs-open[hidden]{display:none}
.op-sheet{width:min(100%,88rem);display:flex;flex-direction:column;background:var(--bg);border-radius:var(--r-lg);box-shadow:var(--shadow-3);overflow:hidden;animation:op-in .18s ease}
@keyframes op-in{from{opacity:0;transform:scale(.985)}}
.op-bar{display:flex;align-items:center;gap:var(--sp-2);padding:var(--sp-3) var(--sp-4);border-bottom:1px solid var(--line);background:var(--surface)}
.op-bar .pos{font-family:var(--font-2);font-size:var(--fs-footnote);color:var(--text-3);font-variant-numeric:tabular-nums;min-width:5.5rem;text-align:center}
.op-body{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 20rem}
.hs-stage{overflow-y:auto;padding:var(--sp-5) var(--sp-6) var(--sp-7);min-width:0;position:relative}
.hs-insp{overflow-y:auto;background:var(--surface);border-inline-start:1px solid var(--line);padding:var(--sp-4) var(--sp-4) var(--sp-7);display:grid;gap:var(--sp-5);align-content:start}
.hs-kind{width:.5rem;height:.5rem;border-radius:50%;flex:none}
.hs-kind.kid{background:var(--kid)}.hs-kind.expert{background:var(--accent)}.hs-kind.reco{background:var(--info)}
.hs-badge{display:inline-flex;align-items:center;justify-content:center;width:1.5rem;height:1.5rem;border-radius:var(--r-xs);font-weight:700;font-size:var(--fs-caption);background:var(--fill-2);color:var(--text-3);font-variant-numeric:tabular-nums}
.hs-badge.on{background:var(--surface);color:var(--tint);box-shadow:var(--shadow-1)}
.hs-pill{display:inline-flex;align-items:center;gap:var(--sp-1);font-size:var(--fs-caption);font-weight:600;padding:.12rem .5rem;border-radius:var(--r-pill);background:var(--fill-2);color:var(--text-2);white-space:nowrap}
.hs-pill.kid{background:var(--kid-soft);color:var(--kid)}.hs-pill.expert{background:var(--expert-soft);color:var(--expert)}.hs-pill.reco{background:var(--info-soft);color:var(--info)}
.hs-pill.review{background:var(--accent-soft);color:var(--accent-ink)}.hs-pill.done{background:var(--success-soft);color:var(--success)}
.hs-pill.failed{background:var(--danger-soft);color:var(--danger)}.hs-pill.busy{background:var(--tint-soft);color:var(--tint)}
.hs-spin{width:.75rem;height:.75rem;border-radius:50%;border:2px solid currentColor;border-inline-end-color:transparent;animation:hs-spin .8s linear infinite;flex:none}
@keyframes hs-spin{to{transform:rotate(360deg)}}
.hs-foot{font-size:var(--fs-caption);color:var(--text-3);padding:var(--sp-4);line-height:1.6}
.hs-empty{color:var(--text-3);font-size:var(--fs-callout);padding:var(--sp-5) var(--sp-4);text-align:center}
.st-eyebrow{font-size:var(--fs-footnote);font-weight:600;color:var(--text-3)}
.st-h1{font-size:1.75rem;font-weight:700;letter-spacing:-.022em;line-height:1.2;margin:var(--sp-1) 0 var(--sp-2)}
.st-chips{display:flex;flex-wrap:wrap;gap:var(--sp-2);align-items:center;margin-bottom:var(--sp-4)}
.st-title{font-size:var(--fs-body);color:var(--text-2);margin:0 0 var(--sp-4)}
.st-slides{display:grid;grid-template-columns:repeat(auto-fill,minmax(10rem,1fr));gap:var(--sp-3)}
.st-card{aspect-ratio:4/5;border-radius:var(--r-lg);border:1px solid var(--line);padding:var(--sp-3) var(--sp-4);display:flex;flex-direction:column;gap:var(--sp-2);overflow:auto;position:relative}
.st-card .n{font-size:var(--fs-caption);font-weight:700;opacity:.6}
.st-card .h{font-weight:800;font-size:1.05rem;line-height:1.25;white-space:pre-line}
.st-card .b{font-size:var(--fs-footnote);line-height:1.45;white-space:pre-line;opacity:.85}
.st-card .hl{margin-top:auto;font-size:var(--fs-caption);display:flex;gap:var(--sp-1);align-items:center;opacity:.8}
.st-card .hl b{font-weight:700}
.p-kid .st-card{background:#F8F4FF;border-color:#E3D8FB;color:#3B1D78;border-radius:var(--r-lg) var(--r-lg) var(--r-lg) var(--r-xs)}
.p-kid .st-card .h{font-family:"Rubik Slide",var(--font)}
.p-expert .st-card{background:#FCF7EE;border-color:#EBDCC0;color:#1D1039}
.p-expert .st-card .h{font-family:"Heebo Slide",var(--font)}
.p-expert .st-card .h::before{content:"";display:block;width:1.75rem;height:3px;border-radius:2px;background:#A8741F;margin-bottom:var(--sp-2)}
.st-card.cta{background:linear-gradient(160deg,#5B2BD6,#3B1D78);color:#F8F0E1;border-color:#3B1D78}
.p-expert .st-card.cta{background:#1D1039}
.st-card.first{box-shadow:0 0 0 2px var(--tint)}
[contenteditable]{outline:none;border-radius:var(--r-xs);transition:background .12s,box-shadow .12s;cursor:text}
[contenteditable]:hover{box-shadow:0 0 0 1px var(--line-strong)}
[contenteditable]:focus{box-shadow:0 0 0 2px var(--tint);background:var(--surface)}
.st-card.cta [contenteditable]:focus{background:rgba(255,255,255,.12)}
.st-card:not(.cta) [contenteditable]:focus{background:#fff} /* slide cards keep their light pillar look in black mode too */
[contenteditable].dirty{box-shadow:0 0 0 2px var(--accent)}
[contenteditable]:empty::before{content:attr(data-ph);opacity:.45}
.st-imgs{display:grid;grid-template-columns:repeat(auto-fill,minmax(9.5rem,1fr));gap:var(--sp-3)}
.st-img{display:block;padding:0;border:1px solid var(--line);border-radius:var(--r-md);overflow:hidden;background:var(--tint-soft);cursor:zoom-in;aspect-ratio:4/5}
.st-img img{display:block;width:100%;height:100%;object-fit:cover}
.st-sec{margin-top:var(--sp-6)}
.st-sec h2{font-size:var(--fs-headline);font-weight:600;margin:0 0 var(--sp-2)}
.st-sec .hint{font-size:var(--fs-caption);color:var(--text-3);font-weight:400;margin-inline-start:var(--sp-2)}
.st-box{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--sp-3) var(--sp-4);white-space:pre-line;line-height:1.6;font-size:var(--fs-callout)}
.st-box+.st-box{margin-top:var(--sp-2)}
.st-story{font-size:var(--fs-footnote);color:var(--text-2);line-height:1.7;margin:var(--sp-4) 0 0}
.st-story b{color:var(--text);margin-inline-end:var(--sp-1)}
.st-rows{display:grid;gap:var(--sp-2)}
.st-r{display:grid;grid-template-columns:2rem minmax(0,1fr);gap:var(--sp-3);background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--sp-3)}
.st-r>.num{font-weight:700;color:var(--text-3);font-size:var(--fs-footnote);padding-top:2px}
.st-r .fs{display:grid;gap:var(--sp-1)}
.st-r .f{display:grid;grid-template-columns:4.5rem minmax(0,1fr);gap:var(--sp-2);align-items:baseline;font-size:var(--fs-callout)}
.st-r .f>span{font-size:var(--fs-caption);color:var(--text-3)}
.st-r .f>div{white-space:pre-line;line-height:1.5;padding:1px 4px}
.st-save{position:sticky;bottom:0;margin:var(--sp-5) calc(-1 * var(--sp-6)) calc(-1 * var(--sp-7));padding:var(--sp-3) var(--sp-6);background:var(--bar);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);border-top:1px solid var(--line);display:flex;align-items:center;gap:var(--sp-3);flex-wrap:wrap}
.st-save[hidden]{display:none}
.st-save .msg{font-size:var(--fs-footnote);color:var(--text-2);flex:1}
.st-errs{margin:var(--sp-3) 0 0;padding:0;list-style:none;display:grid;gap:var(--sp-1)}
.st-errs li{font-size:var(--fs-footnote);color:var(--danger);background:var(--danger-soft);border-radius:var(--r-sm);padding:var(--sp-2) var(--sp-3)}
.st-errs li.warn{color:var(--warning);background:var(--warning-soft)}
.in-sec{display:grid;gap:var(--sp-3)}
.in-sec h2{font-size:var(--fs-footnote);font-weight:600;color:var(--text-3);margin:0;letter-spacing:.01em}
.in-scores{display:grid;grid-template-columns:repeat(5,1fr);gap:var(--sp-1)}
.in-scores button{border:1px solid var(--line-strong);background:var(--surface);border-radius:var(--r-md);padding:var(--sp-2) 0;cursor:pointer;display:grid;gap:2px;color:var(--text)}
.in-scores button b{font-size:1.2rem;line-height:1}
.in-scores button span{font-size:var(--fs-caption);color:var(--text-3)}
.in-scores button[aria-pressed="true"]{background:var(--tint);border-color:var(--tint);color:var(--text-on-tint)}
.in-scores button[aria-pressed="true"] span{color:var(--text-on-tint)}
.in-switch{display:flex;align-items:center;justify-content:space-between;gap:var(--sp-3);padding:var(--sp-3);border-radius:var(--r-md);background:var(--surface-2)}
.in-switch label{font-weight:600;cursor:pointer}
.in-switch small{display:block;font-size:var(--fs-caption);color:var(--text-3)}
.in-state{font-size:var(--fs-caption);color:var(--text-3);min-height:1em}
.in-state.err{color:var(--danger)}
.in-pic{display:block;width:100%;border-radius:var(--r-md);border:1px solid var(--line);background:var(--surface-2)}
.in-checks{margin:0;padding:0;list-style:none;display:grid;gap:var(--sp-1);font-size:var(--fs-footnote);color:var(--text-2)}
.in-checks li::before{content:"";display:inline-block;width:.35rem;height:.35rem;border-radius:50%;background:var(--accent);margin-inline-end:var(--sp-2);vertical-align:middle}
.in-block{display:flex;flex-direction:column;gap:var(--sp-2);background:var(--danger-soft);border-radius:var(--r-sm);padding:var(--sp-3);margin:0}
.in-block-h{margin:0;font-weight:700;color:var(--danger)}
.in-block .st-errs{margin:0}
.in-err{white-space:pre-wrap;font-size:var(--fs-caption);color:var(--danger);background:var(--danger-soft);border-radius:var(--r-sm);padding:var(--sp-2) var(--sp-3);margin:0}
.in-warn{font-size:var(--fs-caption);color:var(--warning);background:var(--warning-soft);border-radius:var(--r-sm);padding:var(--sp-2) var(--sp-3);margin:0}
.in-btns{display:grid;gap:var(--sp-2)}
.in-btns .lb-btn{width:100%;justify-content:center}
.in-keys{font-size:var(--fs-caption);color:var(--text-3);line-height:1.7;margin:0}
.in-keys kbd{font-family:var(--font);font-size:var(--fs-caption);background:var(--fill-2);border-radius:4px;padding:0 .3rem}
.hs-box{position:fixed;inset:0;background:var(--overlay);display:none;align-items:center;justify-content:center;z-index:70;padding:var(--sp-4)}
.hs-box.open{display:flex}
.hs-box img{max-width:min(100%,34rem);max-height:100%;border-radius:var(--r-md);box-shadow:var(--shadow-3)}
.hs-box .lb-btn{position:absolute;top:var(--sp-4);inset-inline-end:var(--sp-4)}
@media (max-width:1200px){.hs-app{grid-template-columns:minmax(0,1fr) 18rem}.op-body{grid-template-columns:minmax(0,1fr) 18rem}.hs-main{padding-inline:var(--sp-5)}.hs-stage{padding-inline:var(--sp-5)}.st-save{margin-inline:calc(-1 * var(--sp-5))}.hs-meter .bar{display:none}}
@media (max-width:900px){
  body{overflow:auto}
  .hs-top{position:sticky;top:0;padding-inline:var(--sp-3);gap:var(--sp-2)}
  .hs-pickbtn{display:inline-flex}
  .hs-week,.hs-meter span,.hs-top .opt{display:none}
  .hs-app{display:block;height:auto}
  .hs-main{overflow:visible;padding:0 var(--sp-4) var(--sp-6)}
  .hs-filter{top:var(--hs-top)}
  .hs-cards{grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--sp-4) var(--sp-3)}
  .hs-picks{position:fixed;top:var(--hs-top);bottom:0;inset-inline-end:0;width:min(88vw,22rem);z-index:40;transform:translateX(-100%);transition:transform .2s ease;box-shadow:var(--shadow-3)}
  .hs-picks.open{transform:none}
  .hs-open{padding:0}
  .op-sheet{border-radius:0}
  .op-body{display:block;overflow-y:auto}
  .hs-stage{overflow:visible;padding:var(--sp-4)}
  .hs-insp{overflow:visible;border:0;border-top:1px solid var(--line);padding:var(--sp-4)}
  .st-slides{grid-auto-flow:column;grid-template-columns:none;grid-auto-columns:11rem;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:var(--sp-2)}
  .st-slides>*{scroll-snap-align:start}
  .st-save{margin:var(--sp-4) calc(-1 * var(--sp-4)) 0;padding-inline:var(--sp-4)}
}
"""

APP_JS = r"""
const S = JSON.parse(document.getElementById('hs-state').textContent);
const KIND = {kid: 'הילד מספר', expert: 'גישה מקצועית', reco: 'משחקים וספרים'};
const SCORE = {1: 'לא', 2: 'חלש', 3: 'בסדר', 4: 'טוב', 5: 'מעולה'};
const ROLE = {hook: 'פתיח', frame: 'מה מתרגלים', recommendation: 'המלצה', lumebook: 'לומבוק', close: 'סיכום'};
const DAYS = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת'];
const BUSY = ['queued', 'fixing', 'preparing', 'generating', 'composing', 'exporting'];
let cur = null, filter = 'all', whyTimer = null, poller = null, zoomN = 0, saving = false;
const orig = new Map();
const lastSave = {};
const $ = s => document.querySelector(s);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const g = k => S.grades[k] || {};
const run = k => S.runs[k];
const item = k => S.items.find(i => i.key === k);
const txt = e => e.innerText.replace(/ /g, ' ').split('\n').map(l => l.trim()).filter(Boolean).join('\n');
const day = d => { const x = new Date(d + 'T12:00:00'); return `יום ${DAYS[x.getDay()]} ${x.getDate()}.${x.getMonth() + 1}`; };
function toast(msg) { let t = $('#hs-toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => t.hidden = true, 4200); }
async function post(url, body) {
  const r = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body || {})});
  const j = await r.json().catch(() => ({})); if (!r.ok) { const e = new Error(j.error || ('HTTP ' + r.status)); e.data = j; throw e; } return j;
}
async function refresh() {
  const j = await (await fetch('/api/state?batch=' + encodeURIComponent(S.batch))).json();
  Object.assign(S, j);
}
function statusPill(r) {
  const cls = r.status === 'review' ? 'review' : r.status === 'done' ? 'done' : r.status === 'failed' ? 'failed' : 'busy';
  const p = el('span', 'hs-pill ' + cls); if (BUSY.includes(r.status)) p.append(el('span', 'hs-spin'));
  p.append(document.createTextNode(r.status_he || r.status)); return p;
}

/* ---------- the grid: slide 1 of every carousel ---------- */
function visible() {
  return S.items.filter(it => { const s = g(it.key), r = run(it.key);
    if (filter === 'open') return !s.score; if (filter === 'pick') return !!s.produce || !!r; if (filter === 'review') return r && r.status === 'review'; return true; });
}
const who = it => it.kind === 'reco' ? `${it.id === 'reco' ? 'משחקים וספרים 1' : 'משחקים וספרים 2'} · ${it.skill_he}` : `${it.id}${it.child_name ? ' · ' + it.child_name : ''}`;
function firstImage(it) { const r = run(it.key); return (r && r.status === 'done' && (r.slides || [])[0]) || (it.images || [])[0] || ''; }
function card(it) {
  const s = g(it.key), r = run(it.key);
  const a = el('article', 'gc' + (s.produce && !r ? ' picked' : '')); a.dataset.key = it.key;
  const b = el('button', 'gc-thumb p-' + it.kind); b.type = 'button'; b.setAttribute('aria-label', 'פתיחה: ' + it.cover);
  const src = firstImage(it);
  const coverCard = () => { const c = el('div', 'st-card'), f = it.slides[0] || {}; c.append(el('div', 'h', f.headline || it.cover)); if (f.body) c.append(el('div', 'b', f.body)); return c; };
  if (src) { const img = el('img'); img.src = src; img.alt = ''; img.loading = 'lazy'; img.decoding = 'async'; img.onerror = () => img.replaceWith(coverCard()); b.append(img); }
  else b.append(coverCard());
  b.onclick = () => openCar(it.key); const fr = el('div', 'gc-frame'); fr.append(b); a.append(fr);
  if (!r) { const p = el('button', 'gc-pick', s.produce ? '✓ להפקה' : '+ להפקה'); p.type = 'button'; p.setAttribute('aria-pressed', String(!!s.produce));
    p.onclick = () => grade({produce: !s.produce}, it.key); fr.append(p); }
  const m = el('div', 'gc-meta'); m.append(el('span', 'hs-kind ' + it.kind), el('span', 'who', who(it)));
  if (r) m.append(statusPill(r));
  if (s.score) { const sc = el('span', 'hs-badge on', String(s.score)); sc.title = 'ציון: ' + SCORE[s.score]; m.append(sc); }
  a.append(m);
  return a;
}
function renderGrid() {
  const box = $('#hs-groups'); box.textContent = '';
  let slot = null, cards = null, dayBox = null, lane = null;
  visible().forEach(it => {
    if (it.slot !== slot) {
      slot = it.slot; lane = null; const sec = el('section', 'hs-group'), h = el('h2');
      h.append(el('span', 'n', String(it.slot)), el('span', null, it.day_topics ? it.day_topics.join(' · ') : it.topic_he)); if (it.event) h.append(el('span', 'hs-pill review', 'אירוע'));
      if (it.day_topics) { dayBox = el('div', 'hs-day'); cards = null; sec.append(h, dayBox); }   // two topics a day (24 Oct 2026)
      else { dayBox = null; cards = el('div', 'hs-cards'); sec.append(h, cards); }
      box.append(sec);
    }
    if (dayBox && it.lane !== lane) {
      lane = it.lane; const ln = el('div', 'hs-lane'); cards = el('div', 'hs-cards');
      ln.append(el('h3', null, it.topic_he), cards); dayBox.append(ln);
    }
    cards.append(card(it));
  });
  if (!box.children.length) box.append(el('p', 'hs-empty', 'אין כאן קרוסלות בסינון הזה'));
  document.querySelectorAll('.hs-filter button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.f === filter)));
  meter();
}

/* ---------- the side panel: what is picked to produce ---------- */
const RUN_ORDER = s => s === 'review' ? 0 : BUSY.includes(s) ? 1 : s === 'failed' ? 2 : 3;
function pickRow(it, removable) {
  const row = el('div', 'pk-row');
  const o = el('button', 'pk-open'); o.type = 'button'; o.onclick = () => { closePicks(); openCar(it.key); };
  const mini = el('span', 'pk-mini ' + it.kind), src = firstImage(it);
  if (src) { const img = el('img'); img.src = src; img.alt = ''; img.loading = 'lazy'; img.onerror = () => img.remove(); mini.append(img); }
  const tx = el('span'); tx.append(el('span', 't', it.cover), el('span', 'm', `${it.slot} · ${it.topic_he} · ${it.id}`));
  o.append(mini, tx); row.append(o);
  if (removable) { const x = el('button', 'pk-x', '×'); x.type = 'button'; x.title = 'להוריד מההפקה'; x.setAttribute('aria-label', 'להוריד מההפקה'); x.onclick = () => grade({produce: false}, it.key); row.append(x); }
  else row.append(statusPill(run(it.key)));
  return row;
}
function renderPicks() {
  const wait = S.items.filter(i => g(i.key).produce && !run(i.key));
  const going = S.items.filter(i => run(i.key)).sort((a, b) => RUN_ORDER(run(a.key).status) - RUN_ORDER(run(b.key).status));
  $('#pk-count').textContent = wait.length ? String(wait.length) : '';
  $('#hs-pickbtn-n').textContent = wait.length ? String(wait.length) : '';
  const lw = $('#pk-wait'); lw.textContent = '';
  if (!wait.length) lw.append(el('p', 'pk-empty', 'עוד לא נבחרה קרוסלה. ״+ להפקה״ על קרוסלה ברשת מוסיף אותה לכאן.'));
  wait.forEach(it => lw.append(pickRow(it, true)));
  const usd = wait.reduce((n, i) => n + (i.kind === 'reco' ? 0 : 0.5), 0);
  const b = $('#hs-send'); b.disabled = !wait.length; b.textContent = wait.length > 1 ? `להפיק את כולן (${wait.length})` : 'להפיק';
  $('#pk-cost').textContent = !wait.length ? '' : usd ? `עד $0.50 לקרוסלה, עד $${usd.toFixed(2)} בסך הכול. כל תמונה מחכה לאישור שלך לפני שהשקופיות נבנות.` : 'ייצוא בלי עלות.';
  const lg = $('#pk-going'); lg.textContent = ''; $('#pk-going-h').hidden = !going.length;
  going.forEach(it => lg.append(pickRow(it, false)));
}
function closePicks() { $('#hs-picks').classList.remove('open'); }
function meter() {
  const graded = S.items.filter(i => g(i.key).score).length, total = S.items.length;
  $('#hs-meter-n').textContent = `דורגו ${graded} מתוך ${total}`;
  $('#hs-meter-bar').style.width = (total ? Math.round(100 * graded / total) : 0) + '%';
  const rv = Object.values(S.runs).filter(r => r.status === 'review').length;
  const c = $('#hs-review'); c.hidden = !rv; c.textContent = `מחכות לאישור: ${rv}`;
  $('#hs-push').hidden = !S.unsent;
}

/* ---------- the carousel ---------- */
function editable(tag, cls, value, field, slide, ph) {
  const e = el(tag, cls, value || '');
  try { e.contentEditable = 'plaintext-only'; } catch (x) {} if (e.contentEditable !== 'plaintext-only') e.contentEditable = 'true';
  e.dataset.f = field; if (slide != null) e.dataset.s = slide; if (ph) e.dataset.ph = ph;
  e.spellcheck = false; e.dir = 'rtl'; orig.set(e, txt(e) || '');
  e.addEventListener('input', () => { e.classList.toggle('dirty', txt(e) !== orig.get(e)); dirtyBar(); });
  return e;
}
function edits() { const out = []; orig.forEach((o, e) => { if (document.contains(e) && txt(e) !== o) out.push({field: e.dataset.f, slide: e.dataset.s ? Number(e.dataset.s) : null, value: txt(e)}); }); return out; }
function dirtyBar() {
  const n = edits().length, bar = $('#st-save'); if (!bar) return;
  const res = lastSave[cur];
  bar.hidden = !n && !res;
  $('#st-save-msg').textContent = n ? (n === 1 ? 'שינוי אחד שלא נשמר' : `${n} שינויים שלא נשמרו`) : (res ? res.msg : '');
  $('#st-save-btn').hidden = !n; $('#st-undo').hidden = !n;
}
function renderStage() {
  const it = item(cur), st = $('#hs-stage'); st.textContent = ''; orig.clear();
  st.className = 'hs-stage p-' + it.kind;
  st.append(el('div', 'st-eyebrow', it.day_topics ? `${day(it.date)} · יום ${it.slot} מתוך 7 · נושא ${it.lane === 'b' ? 2 : 1} מתוך 2` : `${day(it.date)} · נושא ${it.slot} מתוך 7`), el('h1', 'st-h1', it.topic_he));
  const chips = el('div', 'st-chips');
  chips.append(el('span', 'hs-pill ' + it.kind, KIND[it.kind]));
  chips.append(el('span', 'hs-pill', it.kind === 'reco' ? (it.id === 'reco' ? 'קרוסלה 1' : 'קרוסלה 2') : it.id));
  if (it.child_name) chips.append(el('span', 'hs-pill', it.child_name));
  if (it.skill_he) chips.append(el('span', 'hs-pill', it.skill_he + (it.ages ? ' · ' + it.ages : '')));
  if (it.event) chips.append(el('span', 'hs-pill review', 'אירוע · ' + it.event));
  st.append(chips);
  st.append(editable('p', 'st-title', it.title, 'title', null, 'כותרת פנימית'));
  if (it.kind === 'reco') {
    const grid = el('div', 'st-imgs');
    (it.images || []).forEach((src, n) => { const b = el('button', 'st-img'); b.type = 'button'; const img = el('img'); img.src = src; img.alt = 'שקופית ' + (n + 1); img.loading = n < 6 ? 'eager' : 'lazy'; b.append(img); b.onclick = () => zoom(n); grid.append(b); });
    st.append(grid);
    if (it.products && it.products.length) { const p = el('p', 'st-story'); p.append(el('b', null, 'מה בפנים'), document.createTextNode(it.products.join(' · '))); st.append(p); }
    const sec = el('section', 'st-sec'); const h = el('h2', null, 'טקסט השקופיות'); h.append(el('span', 'hint', 'לוחצים ומקלידים. בשמירה השקופיות נבנות מחדש')); sec.append(h);
    const rows = el('div', 'st-rows');
    it.slides.forEach(s => {
      const r = el('div', 'st-r'); r.append(el('span', 'num', String(s.n)));
      const fs = el('div', 'fs');
      const fields = s.role === 'recommendation' ? [['headline', 'שם'], ['age', 'גיל'], ['why', 'למה'], ['how', 'איך']] : [['headline', ROLE[s.role] || 'כותרת'], ['body', 'גוף']];
      if ('highlight' in s) fields.push(['highlight', 'הדגשה']);
      fields.forEach(([f, label]) => { const row = el('div', 'f'); row.append(el('span', null, label), editable('div', null, s[f] || '', f, s.n, '')); fs.append(row); });
      r.append(fs); rows.append(r);
    });
    sec.append(rows); st.append(sec);
    const cap = el('section', 'st-sec'); cap.append(el('h2', null, 'כיתוב'), editable('div', 'st-box', it.caption, 'caption', null, 'כיתוב')); st.append(cap);
  } else {
    const grid = el('div', 'st-slides'); const last = it.slides.length;
    it.slides.forEach((s, i) => {
      const c = el('div', 'st-card' + (i === 0 ? ' first' : '') + (s.n === last ? ' cta' : ''));
      c.append(el('span', 'n', i === 0 ? '1 · שער' : String(s.n)));
      c.append(editable('div', 'h', s.headline, 'headline', s.n, 'כותרת'));
      if (s.n === last) c.append(el('div', 'b', s.body)); else c.append(editable('div', 'b', s.body, 'body', s.n, 'גוף (לא חובה)'));
      if ('highlight' in s) { const hl = el('div', 'hl'); hl.append(el('span', null, 'הדגשה'), editable('b', null, s.highlight, 'highlight', s.n, '')); c.append(hl); }
      grid.append(c);
    });
    st.append(grid);
    const p = el('p', 'st-story'); p.append(el('b', null, 'הכותרות בלבד'), document.createTextNode(it.headlines.join(' ← '))); st.append(p);
    const cap = el('section', 'st-sec'); const h = el('h2', null, 'כיתוב וקריאה לפעולה'); h.append(el('span', 'hint', 'הקריאה לפעולה מעדכנת גם את השקופית האחרונה')); cap.append(h);
    cap.append(editable('div', 'st-box', it.caption_body, 'caption', null, 'כיתוב'), editable('div', 'st-box', it.cta, 'cta', null, 'קריאה לפעולה'));
    st.append(cap);
  }
  const bar = el('div', 'st-save'); bar.id = 'st-save'; bar.hidden = true;
  const msg = el('span', 'msg'); msg.id = 'st-save-msg';
  const undo = el('button', 'lb-btn ghost sm', 'ביטול'); undo.id = 'st-undo'; undo.type = 'button'; undo.onclick = () => { delete lastSave[cur]; renderStage(); };
  const save = el('button', 'lb-btn sm', 'שמירה'); save.id = 'st-save-btn'; save.type = 'button'; save.onclick = () => saveEdits();
  bar.append(msg, undo, save);
  const res = lastSave[cur];
  if (res && res.list && res.list.length) { const ul = el('ul', 'st-errs'); res.list.forEach(x => ul.append(el('li', x.warn ? 'warn' : null, x.text))); bar.append(ul); bar.style.flexDirection = 'row'; ul.style.flexBasis = '100%'; }
  st.append(bar); dirtyBar();
}
async function saveEdits() {
  const it = item(cur), ch = edits();
  if (!ch.length || saving) return true;
  saving = true; $('#st-save-msg').textContent = it.kind === 'reco' ? 'שומר ובונה את השקופיות מחדש...' : 'שומר...'; $('#st-save-btn').disabled = true;
  try {
    const j = it.kind === 'reco' ? await post('/api/save-reco', {date: it.date, format: it.format, edits: ch})
                                 : await post('/api/save', {date: it.date, edits: ch.map(e => ({option: it.id, ...e}))});
    const mine = (j.errors || []).filter(e => it.kind === 'reco' || (e.path || '').includes(it.id));
    const warns = (j.warnings || []).filter(e => it.kind === 'reco' || (e.path || '').includes(it.id)).filter(e => !/rights_unverified/.test(e.message || ''));
    lastSave[it.key] = {msg: mine.length ? `נשמר עם גיבוי · ${mine.length} לתיקון` : 'נשמר עם גיבוי', list: mine.map(e => ({text: e.message})).concat(warns.slice(0, 4).map(e => ({text: e.message, warn: true})))};
    await refresh(); renderGrid(); renderPicks(); renderStage(); renderProd(); toast(mine.length ? 'נשמר. יש מה לתקן, מתחת לשקופיות' : 'נשמר');
    return true;
  } catch (e) { toast('השמירה נכשלה: ' + e.message); $('#st-save-btn').disabled = false; dirtyBar(); return false; }
  finally { saving = false; }
}

/* ---------- grade and production ---------- */
function renderInsp() {
  const it = item(cur), s = g(it.key), box = $('#hs-insp'); box.textContent = '';
  const list = visible(), i = list.findIndex(x => x.key === cur);
  $('#op-pos').textContent = i >= 0 ? `${i + 1} מתוך ${list.length}` : '';
  const gs = el('section', 'in-sec'); gs.append(el('h2', null, 'ציון'));
  const sc = el('div', 'in-scores');
  [1, 2, 3, 4, 5].forEach(n => { const b = el('button'); b.type = 'button'; b.dataset.s = n; b.setAttribute('aria-pressed', String(s.score === n)); b.append(el('b', null, String(n)), el('span', null, SCORE[n])); b.onclick = () => grade({score: n}); sc.append(b); });
  gs.append(sc);
  const why = el('textarea', 'lb-textarea'); why.id = 'in-why'; why.rows = 4; why.dir = 'rtl'; why.placeholder = 'למה? מה עובד, מה לא, מה היית משנה'; why.value = s.why || '';
  why.addEventListener('input', () => { clearTimeout(whyTimer); state('...'); whyTimer = setTimeout(() => { whyTimer = null; grade({why: why.value}); }, 700); });
  why.addEventListener('blur', flushWhy); gs.append(why);
  const sw = el('div', 'in-switch'); const lab = el('label'); lab.htmlFor = 'in-pick'; lab.append(document.createTextNode('להפקה'), el('small', null, s.sent_at ? 'נשלח להפקה' : 'נכנסת לרשימת ההפקה בצד'));
  const pick = el('input', 'lb-switch'); pick.type = 'checkbox'; pick.id = 'in-pick'; pick.checked = !!s.produce; pick.onchange = () => grade({produce: pick.checked});
  sw.append(lab, pick); gs.append(sw);
  const stt = el('div', 'in-state'); stt.id = 'in-state'; gs.append(stt);
  box.append(gs);
  const ps = el('section', 'in-sec'); ps.id = 'in-prod'; box.append(ps); renderProd();
  const keys = el('p', 'in-keys'); keys.innerHTML = '<kbd>←</kbd> <kbd>→</kbd> ניווט · <kbd>1</kbd> עד <kbd>5</kbd> ציון · <kbd>P</kbd> להפקה · <kbd>W</kbd> הסבר · <kbd>⌘S</kbd> שמירת טקסט';
  box.append(keys);
}
function state(msg, err) { const s = $('#in-state'); if (!s) return; s.textContent = msg; s.classList.toggle('err', !!err); }
async function grade(fields, key) {
  key = key || cur; const here = isOpen() && key === cur; if (here) state('שומר...');
  try { const j = await post('/api/grade', {batch: S.batch, key, ...fields}); S.grades[key] = j.entry; if (here) state('נשמר');
    if (here && fields.score) document.querySelectorAll('.in-scores button').forEach(b => b.setAttribute('aria-pressed', String(Number(b.dataset.s) === fields.score)));
    renderGrid(); renderPicks(); if (here && fields.produce !== undefined) renderInsp(); }
  catch (e) { if (here) state('לא נשמר: ' + e.message, true); else toast('לא נשמר: ' + e.message); }
}
function flushWhy() { if (!whyTimer) return; clearTimeout(whyTimer); whyTimer = null; const w = $('#in-why'); if (w) grade({why: w.value}); }
/* Yarin, 22 Oct 2026: errors never block Produce; it fixes them itself (autofix.py). The list only says what it will fix. */
function blockers(it, box) {
  const errs = it.errors || []; if (!errs.length) return false;
  const w = el('div', 'in-block');
  w.append(el('p', 'in-block-h', `ההפקה תתקן לבד ${errs.length === 1 ? 'דבר אחד' : errs.length + ' דברים'}:`));
  const ul = el('ul', 'st-errs'); errs.forEach(e => ul.append(el('li', null, (e.slide ? `שקופית ${e.slide}: ` : '') + e.message))); w.append(ul);
  box.append(w); return false;
}
function renderProd() {
  const it = item(cur), r = run(it.key), box = $('#in-prod'); if (!box) return; box.textContent = '';
  const h = el('h2', null, 'הפקה'); box.append(h);
  const btns = el('div', 'in-btns');
  const blocked = (!r || ['failed', 'done'].includes(r.status)) && blockers(it, box);
  if (!r) {
    if (!blocked) box.append(el('p', 'in-keys', it.kind === 'reco' ? 'השקופיות כבר מוכנות: ייצוא ל-ZIP עם כיתוב, בלי עלות.' : 'תמונה אחת לכל הקרוסלה, עד $0.50. אחרי שמאשרים אותה, השקופיות וה-ZIP נבנים לבד.'));
    const b = el('button', 'lb-btn', it.kind === 'reco' ? 'ייצוא עכשיו' : 'להפיק עכשיו'); b.type = 'button'; b.disabled = blocked; b.onclick = () => act('start'); btns.append(b); box.append(btns); return;
  }
  const top = el('div', 'st-chips'); top.style.margin = '0'; top.append(statusPill(r)); if (r.kind !== 'reco' && r.spent_usd != null) top.append(el('span', 'hs-pill', `$${Number(r.spent_usd).toFixed(2)} מתוך $0.50`)); box.append(top);
  const src = r.status === 'done' ? (r.contact_sheet || (r.slides || [])[0]) : r.picture;
  if (src) { const a = el('a'); a.href = src; a.target = '_blank'; const img = el('img', 'in-pic'); img.src = src; img.alt = ''; a.append(img); box.append(a); }
  if (r.error) box.append(el(r.declined ? 'p' : 'pre', 'in-err', r.error));
  if (r.warning) box.append(el('p', 'in-warn', r.warning));
  if (r.fixed && r.fixed.length) { const ul = el('ul', 'in-checks'); r.fixed.forEach(f => ul.append(el('li', null, (f.slide ? `שקופית ${f.slide}: ` : '') + (f.after || '').replace(/\n/g, ' / ')))); box.append(el('p', 'in-keys', 'תוקן לבד לפני ההפקה:'), ul); }
  if (r.status === 'review') {
    const ul = el('ul', 'in-checks'); (S.qa || []).forEach(q => ul.append(el('li', null, q))); box.append(ul);
    const ok = el('button', 'lb-btn', 'מאשר, להרכיב את השקופיות'); ok.type = 'button'; ok.onclick = () => act('approve');
    const left = 2 - (r.replacements || 0);
    const ta = el('textarea', 'lb-textarea'); ta.rows = 2; ta.placeholder = 'מה לשנות בתמונה? למשל: הפנים לא למצלמה, אותיות על החולצה';
    const again = el('button', 'lb-btn secondary', left > 0 ? `תמונה אחרת (עוד ${left})` : 'אין עוד ניסיונות'); again.type = 'button'; again.disabled = left <= 0;
    again.onclick = () => { if (!ta.value.trim()) { ta.focus(); toast('כתבו מה לשנות'); return; } act('redo', {note: ta.value.trim()}); };
    btns.append(ok, ta, again);
  } else if (r.status === 'done') {
    if (r.zip) { const a = el('a', 'lb-btn', 'הורדת ZIP'); a.href = r.zip; a.download = ''; btns.append(a); }
    const f = el('button', 'lb-btn secondary', 'הצגה ב-Finder'); f.type = 'button'; f.onclick = () => act('reveal'); btns.append(f);
    if (r.caption_file) { const a = el('a', 'lb-btn ghost', 'הכיתוב'); a.href = r.caption_file; a.target = '_blank'; btns.append(a); }
    const again = el('button', 'lb-btn ghost', 'ייצוא מחדש אחרי עריכה'); again.type = 'button'; again.title = 'בלי תמונה חדשה ובלי עלות'; again.disabled = blocked; again.onclick = () => act('start'); btns.append(again);
  } else if (r.status === 'failed' && r.declined && it.image_action) {
    box.append(el('p', 'in-keys', 'תיאור הסצנה (באנגלית, כמו שהוא נשלח למודל):'));
    const ta = el('textarea', 'lb-textarea'); ta.rows = 6; ta.dir = 'ltr'; ta.value = it.image_action; box.append(ta);
    const again = el('button', 'lb-btn', 'לנסות עם התיאור הזה'); again.type = 'button'; again.disabled = blocked;
    again.onclick = () => { if (ta.value.trim() === it.image_action.trim()) { ta.focus(); toast('שנו קודם את התיאור'); return; } act('brief', {action: ta.value.trim()}); };
    btns.append(again);
  } else if (r.status === 'failed') {
    const again = el('button', 'lb-btn', 'להמשיך מאותה נקודה'); again.type = 'button'; again.disabled = blocked; again.onclick = () => act('start'); btns.append(again);
  } else {
    box.append(el('p', 'in-keys', 'רץ ברקע. אפשר להמשיך לדרג ולערוך בינתיים.'));
  }
  box.append(btns);
}
async function act(action, extra) {
  const it = item(cur);
  if (action === 'start' && edits().length) { const ok = await saveEdits(); if (!ok) return; }
  try { const j = await post('/api/production/' + action, {key: it.key, ...(extra || {})}); if (j.run) S.runs[it.key] = j.run; renderProd(); renderGrid(); renderPicks(); poll(); }
  catch (e) { if (e.data && e.data.errors) { it.errors = e.data.errors; renderProd(); } toast(e.message); }
}
function poll() {
  clearTimeout(poller);
  if (!Object.values(S.runs).some(r => BUSY.includes(r.status))) return;
  poller = setTimeout(async () => { try { const before = JSON.stringify(S.runs); await refresh(); if (JSON.stringify(S.runs) !== before) { renderGrid(); renderPicks(); if (isOpen()) renderProd(); } } catch (e) {} poll(); }, 3000);
}

/* ---------- moving around ---------- */
const isOpen = () => !$('#hs-open').hidden;
async function openCar(key) {
  if (isOpen() && key === cur) return;
  flushWhy();
  if (isOpen() && cur && edits().length) { const ok = await saveEdits(); if (!ok) return; }
  cur = key; history.replaceState(null, '', '#' + key);
  $('#hs-open').hidden = false; renderStage(); renderInsp(); $('#hs-stage').scrollTop = 0; $('.op-body').scrollTop = 0;
}
async function closeCar() {
  flushWhy();
  if (edits().length) { const ok = await saveEdits(); if (!ok) return; }
  $('#hs-open').hidden = true; orig.clear(); history.replaceState(null, '', location.pathname + location.search);
  const c = document.querySelector(`.gc[data-key="${CSS.escape(cur)}"] .gc-thumb`); if (c) { c.scrollIntoView({block: 'nearest'}); c.focus({preventScroll: true}); }
}
function step(d) { const list = visible(); const i = list.findIndex(x => x.key === cur); const n = list[i + d] || (i < 0 ? list[0] : null); if (n) openCar(n.key); }
function zoom(n) { const it = item(cur); if (!it.images || !it.images.length) return; zoomN = (n + it.images.length) % it.images.length; $('#hs-box img').src = it.images[zoomN]; $('#hs-box').classList.add('open'); }

document.querySelectorAll('.hs-filter button').forEach(b => b.onclick = () => { filter = b.dataset.f; renderGrid(); if (isOpen()) renderInsp(); });
$('#hs-review').onclick = () => { filter = 'review'; renderGrid(); const f = visible()[0]; if (f) openCar(f.key); };
$('#hs-pickbtn').onclick = () => $('#hs-picks').classList.toggle('open');
$('#op-close').onclick = () => closeCar();
$('#op-prev').onclick = () => step(-1);
$('#op-next').onclick = () => step(1);
$('#hs-open').onclick = e => { if (e.target.id === 'hs-open') closeCar(); };
$('#hs-week').onchange = e => { location.href = '/?batch=' + encodeURIComponent(e.target.value); };
$('#hs-send').onclick = async () => {
  flushWhy(); $('#hs-send').disabled = true;
  try { const j = await post('/api/produce-send', {batch: S.batch}); Object.assign(S.grades, j.grades); j.started.forEach(r => S.runs[r.key] = r);
    (j.blocked || []).forEach(b => { const x = S.items.find(i => i.key === b.key); if (x) x.errors = b.errors; });
    const nb = (j.blocked || []).length;
    toast((j.started.length ? `נשלחו להפקה: ${j.started.length}` : (nb ? 'לא נשלח כלום' : 'אין מה לשלוח')) + (nb ? ` · ${nb} מחכות לתיקון: ${j.blocked.map(b => b.key.split('/')[1]).join(', ')}` : ''));
    renderGrid(); renderPicks(); if (isOpen()) renderInsp(); poll(); }
  catch (e) { toast('השליחה נכשלה: ' + e.message); renderPicks(); }
};
$('#hs-push').onclick = async () => { const b = $('#hs-push'); b.disabled = true; b.textContent = 'שולח...';
  try { await post('/api/push-grades'); S.unsent = false; toast('הדירוגים בענן. הבאץ\' הבא יקרא אותם'); }
  catch (e) { toast('השליחה נכשלה: ' + e.message); }
  b.disabled = false; b.textContent = 'שליחת הדירוגים לענן'; meter(); };
$('#hs-sync').onclick = async () => { const b = $('#hs-sync'); b.disabled = true;
  try { const j = await post('/api/sync'); if (j.new) { toast(`חבילות חדשות מהענן: ${j.new}`); setTimeout(() => location.reload(), 900); } else toast('אין חדש בענן'); }
  catch (e) { toast('הבדיקה נכשלה: ' + e.message); }
  b.disabled = false; };
$('#hs-box').onclick = e => { if (e.target.id === 'hs-box' || e.target.dataset.close != null) $('#hs-box').classList.remove('open'); else zoom(zoomN + 1); };
document.addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') { e.preventDefault(); saveEdits(); return; }
  if ($('#hs-box').classList.contains('open')) { if (e.key === 'Escape') $('#hs-box').classList.remove('open'); else if (e.key === 'ArrowLeft') zoom(zoomN + 1); else if (e.key === 'ArrowRight') zoom(zoomN - 1); return; }
  if (e.target.closest('[contenteditable], textarea, input, select') || e.metaKey || e.ctrlKey || e.altKey) { if (e.key === 'Escape') e.target.blur(); return; }
  if (e.key === 'Escape') { if ($('#hs-picks').classList.contains('open')) closePicks(); else if (isOpen()) closeCar(); return; }
  if (!isOpen()) return;
  if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') { e.preventDefault(); step(1); }
  else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') { e.preventDefault(); step(-1); }
  else if ('12345'.includes(e.key) && e.key.length === 1) grade({score: Number(e.key)});
  else if (e.key === 'p' || e.key === 'פ') { const p = $('#in-pick'); if (p) p.click(); }
  else if (e.key === 'w' || e.key === "'") { e.preventDefault(); const w = $('#in-why'); if (w) w.focus(); }
});
window.addEventListener('beforeunload', e => { flushWhy(); if (edits().length) { e.preventDefault(); e.returnValue = ''; } });
renderGrid(); renderPicks();
if (S.items.length) {
  const want = decodeURIComponent(location.hash.slice(1));
  if (S.items.some(i => i.key === want)) openCar(want);
  poll();
} else { $('#hs-groups').textContent = ''; $('#hs-groups').append(el('p', 'hs-empty', 'אין עדיין באץ\' שבועי עם חבילות.')); }
"""


def app_page(batch_id=None):
    import create_review
    design = create_review.design
    st = state(batch_id)
    blob = json.dumps(st, ensure_ascii=False).replace("</", "<\\/")
    weeks = "".join(f'<option value="{esc(b)}"{" selected" if b == st["batch"] else ""}>שבוע {esc(b)}</option>' for b in st["batches"])
    filt = "".join(f'<button type="button" data-f="{k}" aria-pressed="false">{v}</button>'
                   for k, v in (("all", "הכול"), ("open", "לדירוג"), ("pick", "הפקה"), ("review", "לאישור")))
    fonts = ('<style>@font-face{font-family:"Rubik Slide";src:url("/assets/fonts/Rubik-VariableFont_wght.ttf") format("truetype");font-weight:300 900}'
             '@font-face{font-family:"Heebo Slide";src:url("/assets/fonts/Heebo-Black.ttf") format("truetype");font-weight:900}</style>')
    return ('<!doctype html>\n<html lang="he" dir="rtl">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Carousel Machine</title>{design.head()}{fonts}<style>{APP_CSS}</style></head>\n<body dir="rtl">'
            '<header class="hs-top">'
            f'<span class="hs-brand"><img src="{design.logo_data_uri()}" alt="">Carousel Machine</span>'
            f'<select class="hs-week" id="hs-week" aria-label="שבוע">{weeks}</select>'
            '<span class="hs-meter"><span id="hs-meter-n"></span><span class="bar"><i id="hs-meter-bar"></i></span></span>'
            '<span class="hs-sp"></span>'
            '<button class="lb-btn secondary sm" type="button" id="hs-review" hidden></button>'
            '<button class="lb-btn ghost sm opt" type="button" id="hs-push" hidden>שליחת הדירוגים לענן</button>'
            f'<button class="lb-btn ghost icon sm opt" type="button" id="hs-sync" title="בדיקת חבילות חדשות מהענן" aria-label="בדיקת חבילות חדשות מהענן">{icon("sync", 16)}</button>'
            '<button class="lb-btn secondary sm hs-pickbtn" type="button" id="hs-pickbtn">להפקה <span id="hs-pickbtn-n"></span></button>'
            f'{design.theme_toggle()}'
            '</header>'
            '<div class="hs-app">'
            f'<main class="hs-main" aria-label="הקרוסלות של השבוע"><div class="hs-filter"><div class="lb-segmented" role="group" aria-label="סינון">{filt}</div></div>'
            '<div id="hs-groups"></div></main>'
            '<aside class="hs-picks" id="hs-picks" aria-label="נבחרו להפקה">'
            '<div class="pk-head"><h2>נבחרו להפקה</h2><span class="c" id="pk-count"></span></div>'
            '<div class="pk-send"><button class="lb-btn" type="button" id="hs-send" disabled>להפיק</button><p class="in-keys" id="pk-cost"></p></div>'
            '<div class="pk-list" id="pk-wait"></div>'
            '<h3 class="pk-sub" id="pk-going-h" hidden>בהפקה ומוכנות</h3><div class="pk-list" id="pk-going"></div>'
            f'<p class="hs-foot">השבוע: {esc(st.get("week_he", ""))}<br>הבאץ\' הבא בענן: {esc(st.get("next_run_he", ""))}</p></aside>'
            '</div>'
            '<div class="hs-open" id="hs-open" role="dialog" aria-modal="true" aria-label="הקרוסלה" hidden><div class="op-sheet">'
            '<div class="op-bar"><button class="lb-btn secondary sm" type="button" id="op-prev">הקודם</button><span class="pos" id="op-pos"></span>'
            '<button class="lb-btn secondary sm" type="button" id="op-next">הבא</button><span class="hs-sp"></span>'
            '<button class="lb-btn ghost sm" type="button" id="op-close">סגירה</button></div>'
            '<div class="op-body"><main class="hs-stage" id="hs-stage"></main><aside class="hs-insp" id="hs-insp" aria-label="ציון והפקה"></aside></div>'
            '</div></div>'
            '<div class="hs-box" id="hs-box"><button class="lb-btn secondary sm" type="button" data-close>סגירה</button><img alt=""></div>'
            '<div class="lb-toast" id="hs-toast" role="status" hidden></div>'
            f'<script type="application/json" id="hs-state">{blob}</script><script>{APP_JS}</script></body></html>')
