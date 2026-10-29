#!/usr/bin/env python3
"""The weekly batch (Yarin, 16 Oct 2026): "lets move to a weekly batch, 14 games and books carousels, 42 kid and expert,
every thursday night", "one pool for the week, dont repeat the same topic twice", and about 10 to 20 percent on things
that happen in Israel ("holidays or special days, hard or exciting").

    python3 carousel/carousel-pipeline/scripts/nightly.py week-plan      # plan the next batch (writes drafts/batches/ID.json)
    python3 carousel/carousel-pipeline/scripts/nightly.py batch-check ID # duplicates and gaps across the batch

Since 18 Oct 2026 (Yarin: "i dont want the games and books carousels anymore", reco_lib.ACTIVE) a batch has no games and
books carousels: 42 options only. Until then:
A batch is 7 packs, each a normal drafts/DATE folder with the six kid and expert options (pack.json) and two games and
books carousels (reco-carousel.json and reco-carousel-2.json): 42 options and 14 carousels. The dates are only keys, in a
row after the newest night already made, so rotation and history keep working; Carousel Machine shows the batch as one pool
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


def unbuilt_plan_from(today, history):
    """A plan made on `today` that has no pack yet (no drafts/DATE/pack.json, no history entry), or None. The 22 Oct 2026
    cloud run called week-plan twice, got a second plan for the week after, and stopped without building anything."""
    made = {p["date"] for p in history.get("packs", [])}
    for plan in reversed(plans()):
        dates = [s["date"] for s in plan.get("slots", [])]
        if plan.get("made_on") == today.isoformat() and not any(d in made or (lib.DRAFTS / d / "pack.json").exists() for d in dates):
            return plan
    return None


def make_plan(today=None, merge=True, log=print, monthly=False):
    """Plan the next weekly batch and write drafts/batches/ID.json (ID = its first date). Returns the plan.
    Safe to run twice: a plan made today with nothing built yet is returned as it is."""
    if merge:
        merge_cloud_history(log=log)
    today = today or lib.now_local().date()
    history = lib.load_history(lib.HISTORY)
    same = unbuilt_plan_from(today, history)
    if same:
        log(f"week-plan: plan {same['id']} was made today and has no packs yet, so it stays the plan (no new one)")
        return same
    dates = posting_dates(history, today=today) if monthly else next_dates(history, today=today)
    ctx = lib.rotation_context(history, dates[0])
    if today >= lib.parse_date(lib.DAILY_PAIR_FROM[:10]):   # two topics a day, plans made from 24 Oct 2026
        plan = make_pair_plan(dates, ctx, today, log=log, monthly=monthly)
        lib.write_json(BATCHES / f"{plan['id']}.json", plan)
        return plan
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
                               for f, s in zip(rl.BATCH_FORMATS, skills[i - 1])] if rl.ACTIVE else []})
    plan = {
        "id": dates[0],
        "kind": "weekly",
        "created_at": lib.now_local().isoformat(timespec="seconds"),
        "made_on": today.isoformat(),
        "event_window": [today.isoformat(), (today + dt.timedelta(days=EVENT_WINDOW_DAYS)).isoformat()],
        "rules": (("7 packs on 7 different topics, each with 6 kid and expert options and 2 games and books carousels (42 and 14). "
                   if rl.ACTIVE else "7 packs on 7 different topics, each with 6 kid and expert options (42); no games and books carousels. ")
                  + f"Slot {EVENT_SLOT} is the Israeli event pack (topic-bank.md \"Israeli events\"): one event in event_window, "
                  "topic id event-<slug>, topic.event with a source read today"
                  + ("; both its carousels record the same event. " if rl.ACTIVE else ". ")
                  + "If no event fits, use fallback_topic_id and say why in topic.reason. Every other slot uses its topic_id."
                  + (" Each carousel uses its assigned skill; the two carousels of a pack use different ages and never share a product."
                     if rl.ACTIVE else "")),
        "slots": slots,
    }
    lib.write_json(BATCHES / f"{plan['id']}.json", plan)
    return plan


def posting_dates(history, today=None):
    """The monthly batch's keys (Yarin, 29 Oct 2026): every other day from the first free date, a Saturday moving to the
    Sunday (28 Oct rhythm: Fri 30 Oct, Sun 1, Tue 3, Thu 5, Sun 8 ...), up to the end of that month."""
    first = lib.parse_date(next_dates(history, n=1, today=today)[0])
    out, d = [], first
    while d.month == first.month:
        out.append(d.isoformat())
        d += dt.timedelta(days=2)
        if d.weekday() == 5:   # Saturday
            d += dt.timedelta(days=1)
    return out


def pick_pairs(dates, ctx, log=print, monthly=False):
    """Two topics a day from two different best-selling books (topic-bank.md "Best-selling books", Yarin 24 Oct 2026).
    In season first, then the longest since last use, then the book with more orders; no topic twice in the batch, no book
    more than PAIR_BOOK_MAX_IN_BATCH times, a book of the day before only when nothing else is left, and none of the
    topics of the last PAIR_TOPIC_COOLDOWN_PACKS packs (relaxed, oldest first, only if the batch cannot be filled)."""
    best = [t for t in ctx["topics"] if t.get("bestseller")]
    ranked = sorted(best, key=lambda t: (not t["in_season"], t["last_used"] or "", -(t["bestseller"].get("orders") or 0), t["id"]))
    recent = set(ctx["recent_pair_topic_ids"])

    book_max = lib.PAIR_BOOK_MAX_IN_BATCH * (-(-len(dates) // 7))   # the weekly cap per 7 packs
    cool = lib.PAIR_TOPIC_COOLDOWN_PACKS + 1                        # monthly: a topic may return after this many packs

    def fill(blocked):
        used, per_book, days, prev_books, uses = set(), {}, [], set(), {}
        for _ in dates:
            if monthly:   # topics may repeat in a month: least used first, never within the cooldown
                recent_in_batch = {t["id"] for day in days[-cool:] for t in day}
                free = sorted((t for t in ranked if t["id"] not in blocked and t["id"] not in recent_in_batch
                               and per_book.get(t["bestseller"]["book"], 0) < book_max), key=lambda t: uses.get(t["id"], 0))
            else:
                free = [t for t in ranked if t["id"] not in used and t["id"] not in blocked
                        and per_book.get(t["bestseller"]["book"], 0) < lib.PAIR_BOOK_MAX_IN_BATCH]
            day = []
            for t in sorted(free, key=lambda t: t["bestseller"]["book"] in prev_books):  # stable: keeps the ranking / least used
                if len(day) < 2 and all(t["bestseller"]["book"] != d["bestseller"]["book"] for d in day):
                    day.append(t)
            if len(day) < 2:
                return None
            for t in day:
                used.add(t["id"])
                uses[t["id"]] = uses.get(t["id"], 0) + 1
                per_book[t["bestseller"]["book"]] = per_book.get(t["bestseller"]["book"], 0) + 1
            prev_books = {t["bestseller"]["book"] for t in day}
            days.append(day)
        return days

    days = fill(recent)
    if days is None:
        log(f"week-plan: not enough best-seller topics outside the last {lib.PAIR_TOPIC_COOLDOWN_PACKS} packs; allowing them, oldest first")
        days = fill(set())
    if days is None:
        raise SystemExit(f"only {len(best)} best-seller topics in topic-bank.md; a week of two-topic packs needs {2 * len(dates)} "
                         f"from at least {len(dates) + 1} books (add rows under \"Best-selling books\")")
    return days


def make_pair_plan(dates, ctx, today, log=print, monthly=False):
    """The weekly batch since 24 Oct 2026: 7 packs, each with two best-seller topics and three child-voice options on each
    (Yarin: "6 versions for each day (3 options for each) so i can choose the strongest one"). No event slot."""
    days = pick_pairs(dates, ctx, log=log, monthly=monthly)
    slots = []
    for i, (date, day) in enumerate(zip(dates, days), start=1):
        topics = [{"topic_id": t["id"], "topic_he": t["title_he"], "book": {"id": t["bestseller"]["book"], "title_he": t["bestseller"]["title_he"]},
                   "options": list(ids)} for t, (_, ids) in zip(day, lib.PAIR_LANES)]
        slots.append({"n": i, "date": date, "kind": "pair", "topic_id": topics[0]["topic_id"],
                      "topic_he": " · ".join(t["topic_he"] for t in topics), "topics": topics, "reco": []})
    return {
        "id": dates[0],
        "kind": "monthly" if monthly else "weekly",
        "format": lib.PAIR_FORMAT,
        "created_at": lib.now_local().isoformat(timespec="seconds"),
        "made_on": today.isoformat(),
        "rules": (f"{len(dates)} packs, one per posting day (every other day, Saturday moved to Sunday), made once a month; a topic may "
                  f"return after {lib.PAIR_TOPIC_COOLDOWN_PACKS + 1} packs. Each pack has" if monthly else "7 packs, one a day, each with two topics of two different best-selling books (topic-bank.md \"Best-selling books\") "
                  "and three child-voice options per topic: kid-1 to kid-3 on topics[0], kid-4 to kid-6 on topics[1] (42 options). "
                  "The CTA asks to save the post and send it to a mom who will relate; no comment word. No Israeli event slot. "
                  "Every slot uses exactly its two topics."),
        "slots": slots,
    }


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
        elif slot["kind"] == "pair":   # two topics a pack since 24 Oct 2026
            pack = lib.read_json(pack_path)
            got = [t.get("id") for t in lib.pack_topics(pack)]
            want = [t["topic_id"] for t in slot["topics"]]
            if got != want:
                errors.append(f"{tag}: planned topics {' + '.join(want)}, the pack has {' + '.join(map(str, got)) or 'none'}")
            for tid in got:
                if tid in topics and (plan.get("kind") != "monthly" or slot["n"] - topics[tid] <= lib.PAIR_TOPIC_COOLDOWN_PACKS):
                    errors.append(f"{tag}: topic {tid} repeats slot {topics[tid]}")
                topics[tid] = slot["n"]
            n = sum(len(d.get("versions", [])) for d in pack.get("directions", []))
            if n != len(lib.PAIR_OPTION_IDS):
                errors.append(f"{tag}: {n} options; a two-topic pack has {len(lib.PAIR_OPTION_IDS)}")
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
    if events == 0 and not any("fallback" in w for w in warns) and plan.get("format") != lib.PAIR_FORMAT:
        warns.append("no Israeli event pack in this batch")
    return errors, warns


def newest_batch_with_content():
    """The newest plan that has at least one slot folder here."""
    for plan in reversed(plans()):
        if any((lib.DRAFTS / s["date"] / "review.html").exists() for s in plan.get("slots", [])):
            return plan
    return None
