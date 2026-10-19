#!/usr/bin/env python3
"""Yarin's grades for a weekly batch, the produce picks, and the summary the next batch learns from.

    python3 carousel/carousel-pipeline/scripts/grades.py brief            # what the next batch reads before writing
    python3 carousel/carousel-pipeline/scripts/grades.py brief --limit 30

Yarin, 16 Oct 2026: "i want all carousels to be showed one by one with option to grade them and let me explain why
i think theyre good so you can learn for next weeks batch", and "let me select them quickly from the tool itself and
click to send you which one i want you to produce an exported version of".

Hook Studio serves the grading page at /grade/<batch id> (review_server.py, grade_page.py). Every carousel of the batch (6 kid and
expert options and 2 games and books carousels per pack) gets a 1 to 5 grade, a free "why" and a produce toggle.

- grades.json holds one entry per carousel, keyed "<date>/<id>" (id: kid-1 ... expert-3, reco, reco-2). The entry
  keeps a snapshot of what was graded (cover, headlines, hook formula and family, child, skill, products), so the
  lesson survives later edits to the drafts. Grades are taste, not performance: only hook-results.json can promote a
  hook formula (hook-bank.md, Measurement).
- Picking a carousel for production and pressing the send button starts it in producer.py (productions.json).
"""

import argparse
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import reco_lib as rl  # noqa: E402

GRADES = lib.PIPELINE / "grades.json"
SCORES = (1, 2, 3, 4, 5)
SCORE_HE = {1: "לא", 2: "חלש", 3: "בסדר", 4: "טוב", 5: "מעולה"}
KIND_HE = {"kid": lib.PILLARS["kid"]["name_he"], "expert": lib.PILLARS["expert"]["name_he"], "reco": "משחקים וספרים"}
WHY_MAX = 4000
_LOCK = threading.Lock()

GRADES_ABOUT = ("Yarin's grades from the Hook Studio grading page (/grade/<batch id>): one entry per carousel, keyed "
                "<date>/<id>. score 1 to 5, why in Yarin's words, produce = picked for production. The snapshot is what "
                "was graded. Taste, not performance: never cite it as evidence that a hook works (that is hook-results.json). "
                "Written by review_server.py; grades.py brief summarises it for the next batch.")


def now_iso():
    return lib.now_local().isoformat(timespec="seconds")


def load(path=None):
    path = Path(path or GRADES)
    data = lib.read_json(path) if path.exists() else {}
    data.setdefault("_about", GRADES_ABOUT)
    data.setdefault("grades", {})
    return data




# ---------------------------------------------------------------- what is in a batch

def _cover(slide):
    return lib.collapse(" ".join([slide.get("headline", ""), slide.get("body", "")]))


def items(plan, drafts=None):
    """Every carousel of a batch in pool order: per pack the six options, then its two games and books carousels (only
    while reco_lib.ACTIVE; off since 18 Oct 2026, so batches made before then show their options only).
    Each item has what the page shows (slides) and the snapshot a grade keeps."""
    drafts = Path(drafts or lib.DRAFTS)
    out = []
    for slot in plan.get("slots", []):
        folder = drafts / slot["date"]
        pack_path = folder / "pack.json"
        pack = lib.read_json(pack_path) if pack_path.exists() else None
        topic = (pack or {}).get("topic", {})
        topic_id = topic.get("id") or slot.get("topic_id") or ""
        topic_he = topic.get("title_he") or slot.get("topic_he") or ""
        event = (topic.get("event") or {}).get("name_he", "")
        base = {"batch": plan["id"], "date": slot["date"], "slot": slot["n"], "topic_id": topic_id, "topic_he": topic_he}
        if event:
            base["event"] = event
        for d in (pack or {}).get("directions", []):
            for v in d.get("versions", []):
                hook = v.get("hook") or {}
                slides = [{"n": s["number"], "role": s.get("role", ""), "headline": s.get("headline", ""), "body": s.get("body", ""),
                           **({"highlight": s["highlight"]} if "highlight" in s else {})} for s in v.get("slides", [])]
                cap = lib.lines_of(v.get("caption", ""))
                cta = v.get("cta", "")
                cap_body = cap[:-1] if cap and lib.collapse(cap[-1]) == lib.collapse(cta) else cap
                out.append({**base, "key": f'{slot["date"]}/{v["id"]}', "kind": d["id"], "id": v["id"], "title": v.get("title", ""),
                            "child_name": v.get("child_name", ""), "addressee": v.get("addressee", ""),
                            "hook_formula": hook.get("formula", ""), "hook_family": v.get("hook_family", ""),
                            "mechanism": hook.get("mechanism", ""), "slide2_move": hook.get("slide2_move", ""),
                            "examples_target": v.get("examples_target"),
                            "image_action": (v.get("image") or {}).get("action", "") if isinstance(v.get("image"), dict) else "",
                            "cover": _cover(v["slides"][0]) if v.get("slides") else "",
                            "headlines": [lib.collapse(s["headline"]) for s in slides],
                            "slides": slides, "caption": "\n".join(cap), "caption_body": "\n".join(cap_body), "cta": cta})
        for r in slot.get("reco", []) if rl.ACTIVE else []:  # hidden since 18 Oct 2026 (Yarin no longer wants them)
            fmt = r["format"]
            path = rl.carousel_path(folder, fmt)
            if not path.exists():
                continue
            car = lib.read_json(path)
            out_dir = rl.OUT_DIRS[fmt]
            stage = car.get("stage") or {}
            slides = car.get("slides", [])
            pngs = [folder / out_dir / f"{i:02d}.png" for i in range(1, len(slides) + 1)]
            images = [f'/drafts/{slot["date"]}/{out_dir}/{p.name}?v={int(p.stat().st_mtime)}' for p in pngs if p.exists()]
            out.append({**base, "key": f'{slot["date"]}/{out_dir}', "kind": "reco", "id": out_dir, "format": fmt,
                        "title": car.get("title", ""), "skill": r.get("skill", ""), "skill_he": r.get("skill_he", ""),
                        "ages": stage.get("age_label_he", ""), "addressee": car.get("addressee", ""),
                        "products": [f'{p.get("title_he", "")} ({rl.KIND_HE.get(p.get("kind"), p.get("kind", ""))})' for p in car.get("products", [])],
                        "cover": _cover(slides[0]) if slides else "",
                        "headlines": [lib.collapse(s.get("headline", "")) for s in slides],
                        "slides": [{"n": i + 1, "role": s.get("role", ""), **{f: s[f] for f in ("headline", "body", "highlight", "age", "why", "how") if f in s}}
                                   for i, s in enumerate(slides)],
                        "images": images, "caption": car.get("caption", "")})
    return out


SNAPSHOT_KEYS = ("batch", "date", "slot", "topic_id", "topic_he", "event", "kind", "id", "format", "title", "child_name",
                 "addressee", "hook_formula", "hook_family", "mechanism", "slide2_move", "examples_target", "skill",
                 "ages", "products", "cover", "headlines")


def snapshot(item):
    return {k: item[k] for k in SNAPSHOT_KEYS if item.get(k) not in (None, "", [])}


# ---------------------------------------------------------------- writes

def upsert(item, score=None, why=None, produce=None, path=None):
    """Save one carousel's grade. Fields left None keep their stored value. Returns the stored entry."""
    if score is not None and score not in SCORES:
        raise ValueError("score must be 1 to 5")
    with _LOCK:
        data = load(path)
        entry = data["grades"].get(item["key"], {})
        entry.update(snapshot(item))
        if score is not None:
            entry["score"] = score
        if why is not None:
            entry["why"] = str(why).strip()[:WHY_MAX]
        if produce is not None:
            entry["produce"] = bool(produce)
            if not produce:
                entry.pop("sent_at", None)
        entry["updated_at"] = now_iso()
        data["grades"][item["key"]] = entry
        lib.write_json(path or GRADES, data)
        return entry


def unsend(keys, path=None):
    """Clear sent_at again for picks that could not start (producer.Blocked), so the next send tries them again."""
    with _LOCK:
        data = load(path)
        for key in keys:
            data["grades"].get(key, {}).pop("sent_at", None)
        if keys:
            lib.write_json(path or GRADES, data)


def pick_unsent(batch_id, path=None):
    """Mark every picked, not yet started carousel of the batch as sent and return their keys (producer.start runs them)."""
    with _LOCK:
        data = load(path)
        stamp = now_iso()
        keys = []
        for key, g in sorted(data["grades"].items()):
            if g.get("batch") == batch_id and g.get("produce") and not g.get("sent_at"):
                g["sent_at"] = stamp
                keys.append(key)
        if keys:
            lib.write_json(path or GRADES, data)
        return keys


# ---------------------------------------------------------------- the lesson for the next batch

def _avg(rows):
    return sum(r["score"] for r in rows) / len(rows)


def _table(title, rows, field):
    groups = {}
    for r in rows:
        if r.get(field):
            groups.setdefault(r[field], []).append(r)
    if not groups:
        return []
    ranked = sorted(groups.items(), key=lambda kv: (-_avg(kv[1]), -len(kv[1])))
    return [f"{title}: " + "; ".join(f"{k} {_avg(v):.1f} (n={len(v)})" for k, v in ranked)]


def _line(g):
    what = f'{g["date"]} {g["id"]}'
    tags = [KIND_HE.get(g["kind"], g["kind"])]
    if g["kind"] == "reco":
        tags += [t for t in (g.get("skill"), g.get("ages")) if t]
    else:
        tags += [t for t in (g.get("hook_formula"), g.get("hook_family"), g.get("mechanism")) if t]
    why = lib.collapse(g.get("why", "")) or "(no reason written)"
    return f'- [{g["score"]}] {what} · {" · ".join(tags)} · topic {g.get("topic_id", "")}\n  cover: "{g.get("cover", "")}"\n  Yarin: {why}'


def brief(path=None, limit=60):
    """Plain text for the next batch: averages, then every graded carousel with Yarin's reason, best first."""
    rows = [g for g in load(path)["grades"].values() if g.get("score") in SCORES]
    if not rows:
        return "No grades yet (carousel/carousel-pipeline/grades.json is empty). Write the batch from the skill rules alone."
    rows.sort(key=lambda g: (g.get("batch", ""), g.get("updated_at", "")), reverse=True)
    batches = sorted({g.get("batch", "") for g in rows}, reverse=True)
    reasons = sum(1 for g in rows if g.get("why"))
    out = [f"Yarin's grades: {len(rows)} carousels graded in {len(batches)} batch(es) ({', '.join(batches)}), {reasons} with a reason. Average {_avg(rows):.1f} of 5.",
           "How to use them: they are Yarin's taste, not performance data. Write toward what scored 4 to 5 and away from what scored 1 to 2, "
           "following the written reasons (a reason beats a pattern in the numbers; one grade is a hint, the same reason twice is a rule). "
           "Never claim a hook works because it was graded high; only hook-results.json can do that. Hard rules in the skill and the validator still win."]
    out += _table("By pillar", rows, "kind")
    opts = [g for g in rows if g["kind"] != "reco"]
    out += _table("By hook family (kid and expert)", opts, "hook_family")
    out += _table("By hook formula (kid and expert)", opts, "hook_formula")
    out += _table("By mechanism (kid and expert)", opts, "mechanism")
    out += _table("By topic", rows, "topic_id")
    shown = rows[:limit]
    for title, lo, hi in (("Liked (4 to 5)", 4, 5), ("Middle (3)", 3, 3), ("Disliked (1 to 2)", 1, 2)):
        part = sorted((g for g in shown if lo <= g["score"] <= hi), key=lambda g: -g["score"])
        if part:
            out.append(f"\n{title}:")
            out += [_line(g) for g in part]
    if len(rows) > limit:
        out.append(f"\n({len(rows) - limit} older grades not listed; they are in the averages.)")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("brief", help="the summary the next batch reads")
    b.add_argument("--limit", type=int, default=60)
    args = ap.parse_args()
    print(brief(limit=args.limit))


if __name__ == "__main__":
    main()
