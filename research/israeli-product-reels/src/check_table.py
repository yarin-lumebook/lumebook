#!/usr/bin/env python3
"""Check the 8-question table rows in src/table/ before they go on the page.

    python3 research/israeli-product-reels/src/check_table.py [--quiet]

For every verified Reel: the row exists, is valid JSON with every field of src/TABLE_BRIEF.md, every
why cites at least one principle (or says none applies), every cited ID exists in
smm-research/principles.md, no em or en dashes, enum fields use the brief's values, word limits are
roughly kept (flagged above 1.5x). Prints problems per Reel and a summary; exit code 1 if any row
is missing or broken. Standard library only.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIR = HERE.parent
QUIET = "--quiet" in sys.argv

review = json.loads((HERE / "review.json").read_text(encoding="utf-8"))
codes = [k for k, v in review.items() if isinstance(v, dict) and v.get("status") == "verified"]
known = set(re.findall(r"^###\s+([HRCSEKFT]\d{1,2})\.", (DIR / "smm-research" / "principles.md").read_text(encoding="utf-8"), re.M))

Q = {
    "q1_hook": {"what": 40, "why": 55}, "q2_flow": {"why": 60, "interaction_prompts": 35}, "q3_cta": {"what": 40, "why": 50},
    "q4_shown": {"what": 45, "why": 55}, "q5_edit": {"what": 45, "why": 50}, "q6_topic": {"what": 30, "why": 50},
    "q7_filmed": {"what": 45, "why": 50}, "q8_text": {"on_screen": 70, "caption": 50, "why": 55},
}
ENUMS = {
    ("q1_hook", "hook_type"): {"problem", "audience_callout", "question", "result_first", "bold_claim", "curiosity_gap", "pattern_interrupt", "face_to_camera",
                               "product_reveal", "relatable_moment", "list_promise", "price_or_offer", "none_clear"},
    ("q2_flow", "retention_devices"): {"open_loop", "numbered_list", "reveal_held_back", "new_visual_every_few_s", "re_hook_mid", "story_arc", "payoff_at_end",
                                       "loop_ending", "repetition", "none"},
    ("q3_cta", "placement"): {"on_screen_end", "on_screen_early", "spoken", "caption", "none"},
    ("q4_shown", "proof_type"): {"in_use", "result", "before_after", "side_by_side", "child_reaction", "testimonial_story", "screen_recording", "price",
                                 "expert_authority", "none"},
    ("q6_topic", "topic_type"): {"milestone_problem", "useful_tip", "product_showcase", "gift_occasion", "personal_story", "humour_skit", "list_review",
                                 "unboxing", "making_diy", "child_using_it", "expert_advice"},
}
DOES = {"hook", "setup", "problem", "turn", "demo", "proof", "detail", "objection", "payoff", "reveal", "re_hook", "cta", "filler"}


def words(s):
    return len(re.findall(r"\S+", str(s or "")))


problems, missing, n_ok = {}, [], 0
for c in codes:
    p = HERE / "table" / f"{c}.json"
    if not p.exists():
        missing.append(c)
        continue
    out = []
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        problems[c] = [f"invalid JSON: {e}"]
        continue
    raw = p.read_text(encoding="utf-8")
    if "—" in raw or "–" in raw:
        out.append("em or en dash")
    if d.get("code") != c:
        out.append(f"code field is {d.get('code')!r}")
    if str(d.get("verdict", "")).lower() not in ("works", "partly", "weak"):
        out.append(f"verdict {d.get('verdict')!r}")
    for k in ("one_line", "weak_points", "lumebook_takeaway"):
        if not d.get(k):
            out.append(f"{k} empty")
    for qk, limits in Q.items():
        q = d.get(qk)
        if not isinstance(q, dict):
            out.append(f"{qk} missing")
            continue
        for f, lim in limits.items():
            if not q.get(f) and f != "interaction_prompts":
                out.append(f"{qk}.{f} empty")
            elif words(q.get(f)) > lim * 1.5:
                out.append(f"{qk}.{f} {words(q.get(f))} words (limit {lim})")
        refs = q.get("refs") or []
        said = set(re.findall(r"\b[HRCSEKFT]\d{1,2}\b", q.get("why", "")))
        for r in set(refs) | said:
            if r not in known:
                out.append(f"{qk} cites unknown {r}")
        if not refs and not said and "none" not in q.get("why", "").lower() and "no principle" not in q.get("why", "").lower():
            out.append(f"{qk} why cites nothing")
        for (eq, ef), allowed in ENUMS.items():
            if eq == qk:
                bad = [x for x in (q.get(ef) or []) if x not in allowed]
                if bad:
                    out.append(f"{qk}.{ef} unknown {bad}")
                if not q.get(ef):
                    out.append(f"{qk}.{ef} empty")
    q1 = d.get("q1_hook") or {}
    for f in ("text_in_first_frame", "face_in_first_frame"):
        if q1.get(f) not in ("yes", "no"):
            out.append(f"q1_hook.{f} {q1.get(f)!r}")
    beats = (d.get("q2_flow") or {}).get("beats") or []
    if not beats:
        out.append("no beats")
    for b in beats:
        if b.get("does") not in DOES:
            out.append(f"beat does {b.get('does')!r}")
    if len(beats) > 12:
        out.append(f"{len(beats)} beats")
    if out:
        problems[c] = out
    else:
        n_ok += 1

if not QUIET:
    for c, out in sorted(problems.items()):
        print(f"{c}: " + "; ".join(out))
print(f"{len(codes)} verified, {len(codes) - len(missing)} rows, {n_ok} clean, {len(problems)} with problems, {len(missing)} missing")
if missing and not QUIET:
    print("missing: " + " ".join(missing))
sys.exit(1 if missing or any("invalid JSON" in " ".join(v) for v in problems.values()) else 0)
