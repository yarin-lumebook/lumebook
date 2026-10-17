#!/usr/bin/env python3
"""The weekly batch (Yarin, 16 Oct 2026): "lets move to a weekly batch, 14 games and books carousels, 42 kid and expert,
every thursday night", "one pool for the week, dont repeat the same topic twice", and about 10 to 20 percent on things
that happen in Israel ("holidays or special days, hard or exciting").

    python3 carousel/carousel-pipeline/scripts/nightly.py week-plan      # plan the next batch (writes drafts/batches/ID.json)
    python3 carousel/carousel-pipeline/scripts/nightly.py batch-check ID # duplicates and gaps across the batch

A batch is 7 packs, each a normal drafts/DATE folder with the six kid and expert options (pack.json) and two games and
books carousels (reco-carousel.json and reco-carousel-2.json): 42 options and 14 carousels. The dates are only keys, in a
row after the newest night already made, so rotation and history keep working; Hook Studio shows the batch as one pool
(/pool/ID). Slot 1 is the Israeli event pack, the other six use six different topics from topic-bank.md, and the 14
carousels get skills spread so none repeats within four packs. Standard library only.
"""

import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import reco_lib as rl  # noqa: E402

BATCHES = lib.DRAFTS / "batches"
BATCH_SIZE = 7                 # packs per week: 7 x 6 = 42 kid and expert options
EVENT_SLOT = 1                 # one event pack a week: 6 of 42 options and 2 of 14 carousels, about 14 percent
EVENT_WINDOW_DAYS = 14         # the event happens within two weeks of the batch being made
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CLOUD_BRANCHES = ("nightly", "batch")


def esc(text):
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------------------
# History from the cloud branches (the cloud clone of main does not have the nights the cloud already made)
# ---------------------------------------------------------------------------

def git(*args, timeout=30):
    return subprocess.run(["git", "-C", str(lib.ROOT), *args], capture_output=True, text=True, timeout=timeout)


def cloud_refs(fetch=True):
    """origin's nightly/* and batch/* branches as refs/remotes names, after an optional fetch."""
    if fetch:
        try:
            git("fetch", "--quiet", "--prune", "origin", *[f"+refs/heads/{b}/*:refs/remotes/origin/{b}/*" for b in CLOUD_BRANCHES])
        except (OSError, subprocess.TimeoutExpired):
            pass
    out = git("for-each-ref", "--format=%(refname:short)", *[f"refs/remotes/origin/{b}/" for b in CLOUD_BRANCHES])
    return [r for r in out.stdout.split() if r]


def merge_cloud_history(fetch=True, log=print):
    """Add every pack and carousel entry recorded on a cloud branch and missing here to history.json and reco-history.json.
    Returns how many entries were added."""
    pipe = lib.PIPELINE.relative_to(lib.ROOT).as_posix()
    packs = lib.load_history(lib.HISTORY)
    cars = rl.load_history(rl.HISTORY)
    have_p = {p["date"] for p in packs.get("packs", [])}
    have_c = {(c["date"], c["format"]) for c in cars.get("carousels", [])}
    added = 0
    for ref in cloud_refs(fetch):
        for name, key, have, data, ident in (("history.json", "packs", have_p, packs, lambda e: e.get("date")),
                                              ("reco-history.json", "carousels", have_c, cars, lambda e: (e.get("date"), e.get("format")))):
            out = git("show", f"{ref}:{pipe}/{name}")
            if out.returncode != 0:
                continue
            try:
                entries = json.loads(out.stdout).get(key, [])
            except json.JSONDecodeError:
                continue
            for e in entries:
                if ident(e) not in have:
                    data.setdefault(key, []).append(e)
                    have.add(ident(e))
                    added += 1
    if added:
        packs["packs"] = sorted(packs.get("packs", []), key=lambda p: p["date"])
        cars["carousels"] = sorted(cars.get("carousels", []), key=lambda c: (c["date"], c["format"]))
        lib.write_json(lib.HISTORY, packs)
        lib.write_json(rl.HISTORY, cars)
        log(f"history: added {added} entries from the cloud branches")
    return added


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

def plans():
    return [lib.read_json(p) for p in sorted(BATCHES.glob("*.json"))] if BATCHES.exists() else []


def load(batch_id):
    path = BATCHES / f"{batch_id}.json"
    return lib.read_json(path) if path.exists() else None


def plan_for_date(date_str):
    """The batch plan that has a slot on this date, and the slot."""
    for plan in plans():
        for slot in plan.get("slots", []):
            if slot.get("date") == date_str:
                return plan, slot
    return None, None


def next_dates(history, n=BATCH_SIZE, today=None):
    """n dates in a row after the newest night already made (folder, history entry or another plan) and after today."""
    today = today or lib.now_local().date()
    seen = [today.isoformat()]
    if lib.DRAFTS.exists():
        seen += [p.name for p in lib.DRAFTS.iterdir() if p.is_dir() and DATE_RE.match(p.name)]
    seen += [p["date"] for p in history.get("packs", [])]
    seen += [c["date"] for c in rl.load_history(rl.HISTORY).get("carousels", [])]
    seen += [s["date"] for plan in plans() for s in plan.get("slots", [])]
    start = lib.parse_date(max(seen)) + dt.timedelta(days=1)
    return [(start + dt.timedelta(days=i)).isoformat() for i in range(n)]


def assign_skills(dates, cars_history, per_date=2):
    """Two skills per pack, none repeated within the last SKILL_COOLDOWN_RUNS packs (history first, then this batch);
    the least recently used skills go first."""
    last_used = {}
    for c in cars_history.get("carousels", []):
        last_used[c["skill"]] = max(last_used.get(c["skill"], ""), c["date"])
    recent_dates = sorted({c["date"] for c in cars_history.get("carousels", [])})[-rl.SKILL_COOLDOWN_RUNS:]
    window = [[c["skill"] for c in cars_history.get("carousels", []) if c["date"] == d] for d in recent_dates]
    out = []
    for date in dates:
        blocked = {s for group in window[-rl.SKILL_COOLDOWN_RUNS:] for s in group}
        free = sorted((s for s in rl.SKILLS if s not in blocked), key=lambda s: (last_used.get(s, ""), s))
        if len(free) < per_date:  # never happens with 13 skills, but never stall a batch
            free += sorted((s for s in rl.SKILLS if s not in free), key=lambda s: (last_used.get(s, ""), s))
        picked = free[:per_date]
        for s in picked:
            last_used[s] = date
        window.append(picked)
        out.append(picked)
    return out


def make_plan(today=None, merge=True, log=print):
    """Plan the next weekly batch and write drafts/batches/ID.json (ID = its first date). Returns the plan."""
    if merge:
        merge_cloud_history(log=log)
    today = today or lib.now_local().date()
    history = lib.load_history(lib.HISTORY)
    dates = next_dates(history, today=today)
    ctx = lib.rotation_context(history, dates[0])
    eligible = [t for t in ctx["topics"] if t["eligible"]]
    regular_needed = BATCH_SIZE - 1
    if len(eligible) < regular_needed + 1:
        raise SystemExit(f"only {len(eligible)} topics are free of the last {lib.TOPIC_COOLDOWN_PACKS} packs; add rows to topic-bank.md "
                         f"(a batch needs {regular_needed} plus a fallback for the event slot)")
    regular, fallback = eligible[:regular_needed], eligible[regular_needed]
    skills = assign_skills(dates, rl.load_history(rl.HISTORY))
    slots = []
    for i, date in enumerate(dates, start=1):
        if i == EVENT_SLOT:
            topic = {"kind": "event", "topic_id": None, "fallback_topic_id": fallback["id"], "fallback_topic_he": fallback["title_he"]}
        else:
            t = regular[i - 2 if i > EVENT_SLOT else i - 1]
            topic = {"kind": "regular", "topic_id": t["id"], "topic_he": t["title_he"]}
        slots.append({"n": i, "date": date, **topic,
                      "reco": [{"format": f, "skill": s, "skill_he": rl.SKILLS[s]["he"], "event": i == EVENT_SLOT}
                               for f, s in zip(rl.BATCH_FORMATS, skills[i - 1])]})
    plan = {
        "id": dates[0],
        "kind": "weekly",
        "created_at": lib.now_local().isoformat(timespec="seconds"),
        "made_on": today.isoformat(),
        "event_window": [today.isoformat(), (today + dt.timedelta(days=EVENT_WINDOW_DAYS)).isoformat()],
        "rules": ("7 packs on 7 different topics, each with 6 kid and expert options and 2 games and books carousels (42 and 14). "
                  f"Slot {EVENT_SLOT} is the Israeli event pack (topic-bank.md \"Israeli events\"): one event in event_window, "
                  "topic id event-<slug>, topic.event with a source read today; both its carousels record the same event. "
                  "If no event fits, use fallback_topic_id and say why in topic.reason. Every other slot uses its topic_id. "
                  "Each carousel uses its assigned skill; the two carousels of a pack use different ages and never share a product."),
        "slots": slots,
    }
    lib.write_json(BATCHES / f"{plan['id']}.json", plan)
    return plan


# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------

def record_all(batch_id):
    """Record every pack and carousel of the batch in the histories again (idempotent). Packs finished in parallel can
    race on history.json; this puts every entry back before the batch is checked and pushed."""
    plan = load(batch_id)
    for slot in (plan or {}).get("slots", []):
        folder = lib.DRAFTS / slot["date"]
        if (folder / "pack.json").exists():
            lib.record_history(lib.read_json(folder / "pack.json"), lib.HISTORY)
        for f in rl.MIXED_FORMATS:
            if rl.carousel_path(folder, f).exists():
                rl.record_history(lib.read_json(rl.carousel_path(folder, f)), rl.HISTORY)


def check(batch_id):
    """Problems across the batch: missing packs or carousels, a repeated topic, a carousel product used twice, skills
    off the plan, the event share. Returns (errors, warnings) as lists of strings."""
    plan = load(batch_id)
    if not plan:
        return [f"no plan drafts/batches/{batch_id}.json"], []
    errors, warns = [], []
    topics, products, events = {}, {}, 0
    for slot in plan["slots"]:
        folder = lib.DRAFTS / slot["date"]
        tag = f"slot {slot['n']} ({slot['date']})"
        pack_path = folder / "pack.json"
        if not pack_path.exists():
            errors.append(f"{tag}: no pack.json")
        else:
            topic = lib.read_json(pack_path).get("topic", {})
            tid = topic.get("id")
            if tid in topics:
                errors.append(f"{tag}: topic {tid} repeats slot {topics[tid]}")
            topics[tid] = slot["n"]
            if slot["kind"] == "event":
                if lib.is_event_topic(tid):
                    events += 1
                elif tid == slot.get("fallback_topic_id"):
                    warns.append(f"{tag}: the event slot used its fallback topic {tid}; this week has no event pack")
                else:
                    errors.append(f"{tag}: the event slot needs an event- topic or its fallback {slot.get('fallback_topic_id')}")
            elif tid != slot["topic_id"]:
                errors.append(f"{tag}: planned topic {slot['topic_id']}, the pack has {tid}")
        for r in slot["reco"]:
            path = rl.carousel_path(folder, r["format"])
            if not path.exists():
                errors.append(f"{tag}: no {path.name}")
                continue
            car = lib.read_json(path)
            if car.get("stage", {}).get("skill") != r["skill"]:
                warns.append(f"{tag} {path.name}: planned skill {r['skill']}, the carousel has {car.get('stage', {}).get('skill')}")
            if r.get("event") and lib.is_event_topic((lib.read_json(pack_path).get("topic", {}) if pack_path.exists() else {}).get("id")) and not car.get("event"):
                errors.append(f"{tag} {path.name}: a carousel of the event pack records the event")
            for p in car.get("products", []):
                key = rl.norm_title(p.get("title_he", "")) or p.get("id")
                if key in products:
                    errors.append(f"{tag} {path.name}: {p.get('title_he')} is also in {products[key]}")
                else:
                    products[key] = f"slot {slot['n']} {path.name}"
    if events == 0 and not any("fallback" in w for w in warns):
        warns.append("no Israeli event pack in this batch")
    return errors, warns


# ---------------------------------------------------------------------------
# Pool page (served by review_server.py at /pool/ID)
# ---------------------------------------------------------------------------

POOL_CSS = """
.pl-head{display:flex;flex-wrap:wrap;gap:var(--sp-2);align-items:center}
.pl-head .hs-h2{margin-inline-end:var(--sp-2)}
.pl-head .lb-toolbar{margin-inline-start:auto}
.pl-row{display:flex;align-items:center;gap:var(--sp-3);padding:.7rem var(--sp-4);min-height:3.25rem;color:inherit;text-decoration:none}
a.pl-row:hover{background:var(--fill);text-decoration:none;color:inherit}
.pl-row .hs-row-main b{white-space:nowrap}
.pl-recos{display:grid;grid-template-columns:repeat(auto-fill,minmax(10rem,1fr));gap:var(--sp-3)}
.pl-reco{display:grid;color:var(--text);text-decoration:none;border:1px solid var(--line);border-radius:var(--r-md);overflow:hidden;background:var(--surface);transition:box-shadow .15s,border-color .15s}
a.pl-reco:hover{border-color:var(--tint);box-shadow:var(--shadow-2);text-decoration:none;color:var(--text)}
.pl-reco img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;background:var(--tint-soft)}
.pl-reco span{display:flex;gap:var(--sp-2);align-items:center;justify-content:space-between;padding:var(--sp-2) var(--sp-3);font-size:var(--fs-footnote)}
.pl-wait{color:var(--text-3);padding:var(--sp-3)}
"""


def _cover(version):
    slides = version.get("slides") or [{}]
    return lib.collapse(slides[0].get("headline", ""))


def pool_page(batch_id):
    import grades
    import producer
    import studio
    plan = load(batch_id)
    if not plan:
        return None
    stored = grades.load()["grades"]
    runs = producer.load()["runs"]

    def marks(key):
        g = stored.get(key, {})
        out = f'<span class="hs-badge{" on" if g.get("score") else ""}" title="ציון">{g.get("score") or "·"}</span>'
        r = runs.get(key)
        if r:
            cls = {"review": "review", "done": "done", "failed": "failed"}.get(r.get("status"), "busy")
            out = f'<span class="hs-pill {cls}">{esc(r.get("status_he", ""))}</span>' + out
        elif g.get("produce"):
            out = '<span class="hs-pill review">להפקה</span>' + out
        return out

    ready = sum(1 for s in plan["slots"] if (lib.DRAFTS / s["date"] / "pack.json").exists())
    n_reco = sum(1 for s in plan["slots"] for r in s["reco"] if rl.carousel_path(lib.DRAFTS / s["date"], r["format"]).exists())
    parts = []
    for slot in plan["slots"]:
        folder = lib.DRAFTS / slot["date"]
        pack_path = folder / "pack.json"
        pack = lib.read_json(pack_path) if pack_path.exists() else None
        topic = (pack or {}).get("topic", {})
        title = topic.get("title_he") or slot.get("topic_he") or ("אירוע בישראל" if slot["kind"] == "event" else slot.get("topic_id", ""))
        chips = ""
        event = topic.get("event")
        if event:
            chips += f'<span class="hs-pill review">אירוע · {esc(event.get("name_he", ""))} · {esc(event.get("date", ""))}</span>'
        elif slot["kind"] == "event":
            chips += '<span class="hs-pill">משבצת אירוע</span>'
        chips += '' if pack else '<span class="hs-pill">עוד לא הגיע</span>'
        tools = ""
        if pack:
            tools = f'<a class="lb-btn ghost sm" href="/drafts/{slot["date"]}/review.html">עריכת ילד ומומחה</a>'
        body = [f'<section class="lb-section" id="slot-{slot["n"]}"><div class="pl-head"><h2 class="hs-h2">{slot["n"]} · {esc(title)}</h2>{chips}'
                f'<span class="lb-toolbar">{tools}</span></div>']
        if pack:
            body.append('<div class="lb-group">')
            for d in pack.get("directions", []):
                for v in d.get("versions", []):
                    key = f'{slot["date"]}/{v.get("id", "")}'
                    body.append(f'<a class="pl-row" href="/grade/{esc(plan["id"])}#{esc(key)}"><span class="hs-id">{esc(v.get("id", ""))}</span>'
                                f'<span class="hs-pill {esc(d["id"])}">{esc(lib.PILLARS.get(d["id"], {}).get("name_he", d["id"]))}</span>'
                                f'<span class="hs-row-main"><b>{esc(_cover(v))}</b><span>{esc(v.get("child_name", ""))}</span></span>{marks(key)}</a>')
            body.append('</div>')
        else:
            body.append('<p class="lb-empty">החבילה עוד בדרך מהענן</p>')
        body.append('<div class="pl-recos">')
        for r in slot["reco"]:
            path = rl.carousel_path(folder, r["format"])
            out_dir = rl.OUT_DIRS[r["format"]]
            if path.exists():
                car = lib.read_json(path)
                thumb = folder / out_dir / "01.png"
                img = f'<img src="/drafts/{slot["date"]}/{out_dir}/01.png" alt="" loading="lazy">' if thumb.exists() else ""
                key = f'{slot["date"]}/{out_dir}'
                body.append(f'<a class="pl-reco" href="/grade/{esc(plan["id"])}#{esc(key)}" title="{esc(lib.collapse(car.get("slides", [{}])[0].get("headline", "")))}">{img}'
                            f'<span><b>{esc(r.get("skill_he", ""))}</b>{marks(key)}</span></a>')
            else:
                body.append(f'<div class="pl-reco"><span class="pl-wait">משחקים וספרים · {esc(r.get("skill_he", ""))} · עוד בדרך</span></div>')
        body.append('</div></section>')
        parts.append("".join(body))
    sub = (f'נוצר {esc(plan.get("made_on", ""))} · {ready} מתוך {len(plan["slots"])} נושאים · {ready * 6} קרוסלות ילד ומומחה · {n_reco} משחקים וספרים. '
           'בלי סדר של ימים: בוחרים כל קרוסלה מכל נושא. לחיצה פותחת אותה בדירוג.')
    actions = f'<a class="lb-btn sm" href="/grade/{esc(plan["id"])}">לדרג אחת אחת</a>'
    return studio.page("מאגר השבוע", "pool", "".join(parts), subtitle=sub, actions=actions, css=POOL_CSS)


def newest_batch_with_content():
    """The newest plan that has at least one slot folder here."""
    for plan in reversed(plans()):
        if any((lib.DRAFTS / s["date"] / "review.html").exists() for s in plan.get("slots", [])):
            return plan
    return None
