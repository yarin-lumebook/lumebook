#!/usr/bin/env python3
"""Entry point for the nightly review run. No network, no paid calls.

    python3 carousel/carousel-pipeline/scripts/nightly.py start            # before writing pack.json
    python3 carousel/carousel-pipeline/scripts/nightly.py finish PATH      # after writing pack.json
    python3 carousel/carousel-pipeline/scripts/nightly.py topics [--date D]
    python3 carousel/carousel-pipeline/scripts/nightly.py voice
    python3 carousel/carousel-pipeline/scripts/nightly.py hooks [--date D]   # hook bank evidence and status

start
    Works out the review date (the next morning; a run after midnight and before 06:00
    targets the same morning), creates drafts/DATE/, moves an existing pack into
    drafts/DATE/versions/vN/ so nothing is overwritten, and prints the context the
    writer needs as JSON: voice status, ranked topics, blocked hook families, recent
    code words and hooks, and the exact path to write.

finish
    Validates the pack (exit 1 with exact errors if anything fails), writes review.html
    and review.md, checks RTL, records the pack in history.json (replacing an earlier
    entry for the same date, so reruns are idempotent) and prints the review paths.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import create_review  # noqa: E402
import reco_lib  # noqa: E402  (daily games and books carousels)
import validate_pack  # noqa: E402


def cmd_start(args):
    date = args.date or lib.review_date_for().isoformat()
    folder = lib.DRAFTS / date
    folder.mkdir(parents=True, exist_ok=True)
    backup = lib.backup_existing(folder)
    reco_backup = reco_lib.backup_existing(folder, target=backup)
    history = lib.load_history()
    ctx = lib.rotation_context(history, date)
    voice = lib.voice_status()
    eligible = [t for t in ctx["topics"] if t["eligible"]]
    out = {
        "date": date,
        "generated_at": lib.now_local().isoformat(timespec="seconds"),
        "write_pack_to": str(folder / "pack.json"),
        "backed_up_previous_pack_to": str(backup) if backup else None,
        "backed_up_previous_recommendations_to": str(reco_backup) if reco_backup else None,
        "voice": voice,
        "voice_note_suggestion": (
            f"Fallback voice: {voice['approved_samples']} of {voice['required']} approved samples. Written from the documented fallback voice, not yet calibrated to Yarin."
            if voice["status"] == "fallback" else f"Calibrated on {voice['approved_samples']} approved samples."
        ),
        "topic_shortlist": [
            {k: t[k] for k in ("id", "title_he", "title_en", "in_season", "last_used", "free_code_words", "books")}
            for t in eligible[:6]
        ],
        "blocked_topic_ids": ctx["recent_topic_ids"],
        "blocked_code_words": ctx["recent_code_words"],
        "blocked_hook_families": ctx["blocked_hook_families"],
        "hook_family_use_last_7_days": ctx["hook_family_candidates_last_7_days"],
        "recent_hooks_do_not_repeat": ctx["recent_hooks"],
        "hook_families": lib.HOOK_FAMILIES,
        **hook_context(ctx, date),
        "hook_min_score": lib.HOOK_MIN_SCORE,
        "recent_voice_edits_learn_from_these": lib.recent_voice_edits(30),
        "child_names": lib.load_names(),
        "recent_child_names_rotate_away_from": ctx["recent_child_names"],
        "addressees": {"mom": "feminine singular (את, כתבי)", "parents": "plural (אתם, כתבו)", "never": "dad"},
        "cta_forms": {
            "mom_boy": "כתבי \"X\" בתגובות וקבלי קישור ליצירת ספר שבו הילד שלך הוא הגיבור",
            "mom_girl": "כתבי \"X\" בתגובות וקבלי קישור ליצירת ספר שבו הילדה שלך היא הגיבורה",
            "parents_boy": "כתבו \"X\" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור",
            "parents_girl": "כתבו \"X\" בתגובות וקבלו קישור ליצירת ספר שבו הילדה שלכם היא הגיבורה",
        },
        "slide_roles": {str(k): list(v) for k, v in lib.SLIDE_ROLES.items()},
        "rules": {
            "slides": lib.SLIDE_COUNT,
            "hook_main_max_words": lib.HOOK_MAIN_MAX_WORDS,
            "hook_total_max_words": lib.HOOK_TOTAL_MAX_WORDS,
            "slide_max_words": lib.SLIDE_MAX_WORDS,
            "cta_slide_max_words": lib.CTA_SLIDE_MAX_WORDS,
            "line_max_words": lib.LINE_MAX_WORDS,
            "caption_lines": [lib.CAPTION_MIN_LINES, lib.CAPTION_MAX_LINES],
            "max_options_per_hook_family": lib.HOOK_FAMILY_MAX_IN_WINDOW,
        },
        # The two extra daily carousels (games and books for one developmental stage): recommendations.md
        "recommendations": reco_lib.start_context(date, folder),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def hook_context(ctx, date):
    """What the writer needs to build tonight's hook slate: the bank with evidence and status, recent rotation, rules."""
    today = lib.parse_date(date)
    bank = []
    for f in lib.load_hook_bank().values():
        bank.append({
            **{k: f[k] for k in ("id", "family", "direction", "formula", "example")},
            "evidence": f["evidence"], "mechanisms": f["mechanisms"], "shape": f["shape"], "slide2_moves": f["slide2_moves"],
            "review_by": f["review_by"], "status": lib.formula_status(f, today),
        })
    return {
        "schema_version": 3,
        "hook_bank": bank,
        "blocked_expired_formulas": [f["id"] for f in bank if f["status"] == "expired"],
        "recent_hook_formulas_rotate_away_from": ctx["recent_hook_formulas"],
        "published_formulas_last_14_days": ctx["selected_formulas_last_14_days"],
        "recent_mechanisms": ctx["recent_mechanisms"],
        "recent_shapes": ctx["recent_shapes"],
        "recent_slide2_moves": ctx["recent_slide2_moves"],
        "recent_awareness_stages": ctx["recent_awareness"],
        "recent_slide2_hooks_do_not_repeat": ctx["recent_slide2_hooks"],
        "mechanisms": lib.MECHANISMS,
        "sentence_shapes": lib.SENTENCE_SHAPES,
        "slide2_moves": lib.SLIDE2_MOVES,
        "hook_slate_rules": {
            "per_direction": lib.SLATE_SIZE,
            "score_keys_0_to_2": list(lib.SLATE_SCORE_KEYS),
            "must_not_be_zero": list(lib.SLATE_NO_ZERO),
            "min_total": lib.SLATE_MIN_SCORE,
            "min_total_is": "a LumeBook hypothesis, not a finding",
            "fail_checks_any_true_fails": list(lib.SLATE_FAIL_CHECKS),
            "min_families_per_direction": lib.SLATE_MIN_FAMILIES,
            "min_mechanisms_per_direction": lib.SLATE_MIN_MECHANISMS,
            "six_options_need": {"mechanisms": lib.PACK_MIN_MECHANISMS, "per_direction_mechanisms": 2, "sentence_shapes": lib.PACK_MIN_SHAPES,
                                 "slide2_moves": lib.PACK_MIN_SLIDE2_MOVES, "awareness_stages": lib.PACK_MIN_AWARENESS},
            "never": "pick or rank a winner; the slate is private working material",
        },
    }


def cmd_hooks(args):
    """Print each formula's evidence and status, and how many LumeBook results exist for it."""
    date = args.date or lib.review_date_for().isoformat()
    today = lib.parse_date(date)
    bank = lib.load_hook_bank()
    results = lib.load_hook_results()
    for f in bank.values():
        obs = lib.formula_observations(f["id"], results)
        print(f"{lib.formula_status(f, today):10} {f['id']:24} {f['direction']:6} {'+'.join(f['evidence']):70} review {f['review_by']}  lumebook posts {obs['posts']}")
    issues = lib.bank_issues(bank, results)
    for i in issues:
        print(f"- {i}")
    raise SystemExit(1 if any(i.level == "ERROR" for i in issues) else 0)


CURRENT_SCHEMA = 3


def finish_schema_issues(pack):
    """New nightly packs must carry the hook slate (schema_version 3). Older packs still validate for editing."""
    if pack.get("schema_version", 2) < CURRENT_SCHEMA:
        return [lib.Issue("ERROR", "pack/schema_version", f"new nightly packs are schema_version {CURRENT_SCHEMA} with a hook_slate (hook-bank.md, Nightly hook slate; references/nightly.md step 5b)")]
    return []


def cmd_finish(args):
    path = Path(args.pack).resolve()
    pack = lib.read_json(path)
    issues = finish_schema_issues(pack) + validate_pack.pack_issues(pack, history=lib.load_history())
    errors = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level == "WARN"]
    if errors:
        print(f"INVALID {path}")
        for i in errors:
            print(f"- {i}")
        print("Rewrite the failed lines (never just delete punctuation) and run finish again.")
        raise SystemExit(1)
    html_path, md_path = create_review.write_review(path)
    problems = create_review.rtl_issues(html_path.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("RTL check failed: " + "; ".join(problems))
    entry = lib.record_history(pack)
    n = sum(len(v["slides"]) for d in pack["directions"] for v in d["versions"])
    print(f"VALID 2 directions, 6 options, {n} slides")
    if warns:
        print(f"{len(warns)} reviewer warnings:")
        for i in warns:
            print(f"- {i}")
    print(f"history: {entry['date']} {entry['topic_id']} code words {', '.join(entry['code_words'])}")
    print(f"REVIEW_HTML {html_path}")
    print(f"REVIEW_MD {md_path}")


def cmd_finish_reco(args):
    """Validate games-carousel.json and books-carousel.json, render their slides, rebuild the review page, record history."""
    import reco_render
    folder = Path(args.folder).resolve()
    if folder.name.endswith(".json"):
        folder = folder.parent
    have = reco_lib.present(folder)
    history = reco_lib.load_history()
    failed = False
    for fmt in reco_lib.FORMATS:
        if fmt not in have:
            print(f"MISSING {folder / reco_lib.FILES[fmt]}")
            failed = True
            continue
        car, issues, st = reco_lib.validate_file(have[fmt], history=history)
        problems = [] if args.no_png else reco_render.render(have[fmt])[1]
        errors = [i for i in issues if i.level == "ERROR"]
        print(f"{'VALID' if st['valid'] and not problems else 'INVALID'} {fmt}: {car['stage']['age_label_he']} · {car['stage']['skill']} · "
              f"publish-ready {'yes' if st['publish_ready'] else 'no'}{'' if st['rights_clear'] else ' (rights_unverified images)'}")
        for i in errors:
            print(f"- [{getattr(i, 'flag', '')}] {i}")
        for p in problems:
            print(f"- [render] {p}")
        warns = [i for i in issues if i.level == "WARN"]
        if warns:
            print(f"  {len(warns)} reviewer warnings:")
            for i in warns:
                print(f"  - [{getattr(i, 'flag', '')}] {i}")
        if errors or problems:
            failed = True
        else:
            reco_lib.record_history(car)
    page = reco_render.write_review(folder)
    problems = create_review.rtl_issues(page.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("RTL check failed: " + "; ".join(problems))
    print(f"REVIEW_HTML {page}")
    if failed:
        print("Fix the listed lines or evidence (never delete punctuation, never invent evidence) and run finish-reco again.")
        raise SystemExit(1)


def cmd_topics(args):
    date = args.date or lib.review_date_for().isoformat()
    ctx = lib.rotation_context(lib.load_history(), date)
    for t in ctx["topics"]:
        flag = "ok " if t["eligible"] else "used"
        season = "season" if t["in_season"] and t["months"] else ("any" if not t["months"] else "off")
        print(f"{flag} {season:6} {t['id']:28} last {t['last_used'] or '-':10} {t['title_he']}")


def cmd_voice(_args):
    print(json.dumps(lib.voice_status(), ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--date", help="override the review date YYYY-MM-DD")
    s.set_defaults(func=cmd_start)
    f = sub.add_parser("finish")
    f.add_argument("pack")
    f.set_defaults(func=cmd_finish)
    t = sub.add_parser("topics")
    t.add_argument("--date")
    t.set_defaults(func=cmd_topics)
    v = sub.add_parser("voice")
    v.set_defaults(func=cmd_voice)
    fr = sub.add_parser("finish-reco", help="validate and render the games and books carousels in a draft folder")
    fr.add_argument("folder", help="drafts/DATE (or a carousel file inside it)")
    fr.add_argument("--no-png", action="store_true", help="skip the Chrome export (tests)")
    fr.set_defaults(func=cmd_finish_reco)
    hk = sub.add_parser("hooks")
    hk.add_argument("--date", help="judge review dates as of this day YYYY-MM-DD")
    hk.set_defaults(func=cmd_hooks)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
