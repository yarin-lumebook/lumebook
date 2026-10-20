#!/usr/bin/env python3
"""Check the research principles against the 173 verified Reels' public counts.

    python3 research/israeli-product-reels/src/evidence_check.py

For each Reel feature that a principle predicts should help (a hook in the first frame, subtitles,
a CTA on screen...), compare Reels with and without it on two public measures read 15 Oct 2026:

- plays per follower (plays / the creator's follower count): how far a Reel travelled past its own
  audience. Follower counts were read 14 to 18 Oct 2026 (`src/followers.json`).
- interaction rate ((likes + comments) / plays), Reels with hidden likes left out.

Medians per group, a two-sided Mann-Whitney U test (normal approximation with tie correction) and
Cliff's delta (from -1 to 1; positive means the feature's group is higher). Because the sample mixes
brand-grid collaboration posts with larger creators' own posts, every comparison is repeated inside
each group (collab, creator-only) and the result says whether the direction holds in both.

This is a correlation check on a non-random sample, not proof of cause. Inputs: src/review.json,
src/coded/, src/table/ (the 8-question pass), src/media_info_15oct.json, src/followers.json,
the captions in media/.../videos/CODE.info.json. Output: smm-research/sample-check.json and
smm-research/sample-check.md. Standard library only.
"""
import json
import math
import re
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIR = HERE.parent
ROOT = HERE.parents[2]
VIDEOS = ROOT / "media" / "projects" / "2026-10-15-israeli-product-reels" / "videos"
OUT_JSON = DIR / "smm-research" / "sample-check.json"
OUT_MD = DIR / "smm-research" / "sample-check.md"


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def num(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).replace(",", "").strip()
    m = re.match(r"^([\d.]+)\s*([KkMm]?)$", s)
    if not m:
        return None
    v = float(m.group(1))
    return v * {"": 1, "k": 1e3, "m": 1e6}[m.group(2).lower()]


review = load(HERE / "review.json")
info = load(HERE / "media_info_15oct.json")
followers = load(HERE / "followers.json")
codes = [k for k, v in review.items() if isinstance(v, dict) and v.get("status") == "verified"]

REELS = []
for c in codes:
    coded = load(HERE / "coded" / f"{c}.json")
    tp = HERE / "table" / f"{c}.json"
    table = load(tp) if tp.exists() else None
    mi = info.get(c, {})
    handle = (mi.get("owner") or coded.get("handle") or "").lstrip("@")
    f = followers.get(handle)
    fol = num(f[0]) if isinstance(f, list) else num(f)
    cap = ""
    ij = VIDEOS / f"{c}.info.json"
    if ij.exists():
        cap = load(ij).get("description") or ""
    plays, likes, comments = mi.get("plays"), mi.get("likes"), mi.get("comments")
    hidden = bool(mi.get("like_and_view_counts_hidden"))
    REELS.append({
        "code": c, "coded": coded, "table": table, "caption": cap, "handle": handle,
        "collab": bool(mi.get("coauthors")),
        "plays": plays, "followers": fol,
        "ppf": (plays / fol) if plays and fol else None,
        "ir": ((likes + (comments or 0)) / plays) if plays and likes is not None and not hidden else None,
        "duration": mi.get("duration_s") or None,
    })


# ---------- stats ----------

def mann_whitney(a, b):
    """Two-sided p-value, normal approximation with tie correction, and Cliff's delta (a vs b)."""
    n1, n2 = len(a), len(b)
    if n1 < 3 or n2 < 3:
        return None, None
    allv = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    ranks, i, ties = [0.0] * len(allv), 0, 0.0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        t = j - i + 1
        ties += t ** 3 - t
        i = j + 1
    r1 = sum(r for r, (_, g) in zip(ranks, allv) if g == 0)
    u1 = r1 - n1 * (n1 + 1) / 2
    n = n1 + n2
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 / 12 * ((n + 1) - ties / (n * (n - 1))))
    z = (u1 - mu) / sigma if sigma else 0.0
    p = math.erfc(abs(z) / math.sqrt(2))
    delta = (2 * u1) / (n1 * n2) - 1
    return p, delta


def compare(rows, test, metric):
    yes_rows = [r for r in rows if test(r) is True and r[metric] is not None]
    no_rows = [r for r in rows if test(r) is False and r[metric] is not None]
    yes, no = [r[metric] for r in yes_rows], [r[metric] for r in no_rows]
    p, d = mann_whitney(yes, no)
    return {
        "n_yes": len(yes), "n_no": len(no),
        "creators_yes": len({r["handle"] for r in yes_rows}), "creators_no": len({r["handle"] for r in no_rows}),
        "median_yes": st.median(yes) if yes else None, "median_no": st.median(no) if no else None,
        "p": p, "delta": d,
    }


def verdict(whole, strata):
    """Plain-words reading of one comparison."""
    d, p = whole["delta"], whole["p"]
    if d is None or min(whole["n_yes"], whole["n_no"]) < 8 or min(whole["creators_yes"], whole["creators_no"]) < 5:
        return "too few to tell"
    same_dir = all(s["delta"] is not None and (s["delta"] > 0) == (d > 0) for s in strata if s["delta"] is not None and min(s["n_yes"], s["n_no"]) >= 5)
    if abs(d) < 0.12:
        return "no clear difference"
    word = "higher" if d > 0 else "lower"
    sure = "clear" if p is not None and p < 0.05 and same_dir else ("leaning" if same_dir else "mixed")
    return f"{sure}: {word} with the feature"


# ---------- features ----------

def t(r, *path):
    v = r["table"]
    for k in path:
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    return v


def has_any(lst, *vals):
    return bool(lst) and any(v in lst for v in vals)


def first_seen(r):
    v = r["coded"].get("product_first_seen_s")
    return v if isinstance(v, (int, float)) else None


def speech(r):
    return (r["coded"].get("audio") or {}).get("speech", "")


def caption_words(r):
    return len(re.findall(r"\S+", r["caption"]))


def hashtags(r):
    return len(re.findall(r"#\S+", r["caption"]))


def avg_shot(r):
    n = r["coded"].get("n_shots_estimate")
    return (r["duration"] / n) if r["duration"] and isinstance(n, (int, float)) and n > 0 else None


def b(x):
    return None if x is None else bool(x)


FEATURES = [
    # id, question, label, principle refs (filled from principles.md), test -> True / False / None
    ("product_2s", 1, "Product on screen within 2 s", lambda r: b(first_seen(r) is not None and first_seen(r) <= 2) if first_seen(r) is not None else None),
    ("text_first_frame", 1, "Text on screen in the first frame", lambda r: None if t(r, "q1_hook", "text_in_first_frame") is None else t(r, "q1_hook", "text_in_first_frame") == "yes"),
    ("face_first_frame", 1, "A face in the first frame", lambda r: None if t(r, "q1_hook", "face_in_first_frame") is None else t(r, "q1_hook", "face_in_first_frame") == "yes"),
    ("hook_problem", 1, "Hook names a problem or worry", lambda r: None if t(r, "q1_hook", "hook_type") is None else has_any(t(r, "q1_hook", "hook_type"), "problem")),
    ("hook_callout", 1, "Hook calls out the audience", lambda r: None if t(r, "q1_hook", "hook_type") is None else has_any(t(r, "q1_hook", "hook_type"), "audience_callout")),
    ("hook_curiosity", 1, "Hook opens a question or curiosity gap", lambda r: None if t(r, "q1_hook", "hook_type") is None else has_any(t(r, "q1_hook", "hook_type"), "question", "curiosity_gap")),
    ("hook_relatable", 1, "Hook opens on a relatable moment", lambda r: None if t(r, "q1_hook", "hook_type") is None else has_any(t(r, "q1_hook", "hook_type"), "relatable_moment")),
    ("open_loop", 2, "An open loop or a held-back reveal", lambda r: None if t(r, "q2_flow", "retention_devices") is None else has_any(t(r, "q2_flow", "retention_devices"), "open_loop", "reveal_held_back")),
    ("story_arc", 2, "A story arc with a payoff", lambda r: None if t(r, "q2_flow", "retention_devices") is None else has_any(t(r, "q2_flow", "retention_devices"), "story_arc", "payoff_at_end")),
    ("numbered", 2, "A numbered list", lambda r: None if t(r, "q2_flow", "retention_devices") is None else has_any(t(r, "q2_flow", "retention_devices"), "numbered_list")),
    ("interaction_prompt", 2, "An invitation to comment, share or save", lambda r: None if t(r, "q2_flow", "interaction_prompts") is None else not str(t(r, "q2_flow", "interaction_prompts")).strip().lower().startswith("none")),
    ("cta_any", 3, "Any CTA", lambda r: None if not r["coded"].get("cta_type") else r["coded"]["cta_type"] != ["none"]),
    ("cta_comment_word", 3, "Comment-a-word CTA", lambda r: None if not r["coded"].get("cta_type") else "comment_word" in r["coded"]["cta_type"]),
    ("cta_code", 3, "A discount code", lambda r: None if not r["coded"].get("cta_type") else "code" in r["coded"]["cta_type"]),
    ("cta_on_screen", 3, "CTA on screen in the video", lambda r: None if t(r, "q3_cta", "placement") is None else has_any(t(r, "q3_cta", "placement"), "on_screen_end", "on_screen_early")),
    ("price_shown", 4, "Price shown in the video", lambda r: None if not r["coded"].get("price_on_screen") else r["coded"]["price_on_screen"] != "no"),
    ("child_on_camera", 4, "A child on camera", lambda r: None if not r["coded"].get("child_on_camera") else r["coded"]["child_on_camera"] == "yes"),
    ("hands_only", 4, "No face at all, adult or child (hands only)", lambda r: None if not r["coded"].get("face_on_camera") else (r["coded"]["face_on_camera"].startswith("no") and r["coded"].get("child_on_camera") != "yes")),
    ("adult_face", 4, "An adult's face on camera", lambda r: None if not r["coded"].get("face_on_camera") else r["coded"]["face_on_camera"] in ("creator's face", "other adult")),
    ("in_use", 4, "Product shown in use", lambda r: None if t(r, "q4_shown", "proof_type") is None else has_any(t(r, "q4_shown", "proof_type"), "in_use", "child_reaction")),
    ("screen_rec", 4, "A screen recording", lambda r: None if not r["coded"].get("screen_recording") else r["coded"]["screen_recording"].startswith("yes")),
    ("fast_cuts", 5, "Average shot under 3 s", lambda r: None if avg_shot(r) is None else avg_shot(r) < 3),
    ("short", 5, "30 s or shorter", lambda r: None if not r["duration"] else r["duration"] <= 30),
    ("voice", 5, "Speech (voiceover or to camera)", lambda r: None if not speech(r) else speech(r) != "none"),
    ("topic_tip", 6, "Topic is a useful tip or expert advice", lambda r: None if t(r, "q6_topic", "topic_type") is None else has_any(t(r, "q6_topic", "topic_type"), "useful_tip", "expert_advice")),
    ("topic_story", 6, "Topic is a personal story or milestone problem", lambda r: None if t(r, "q6_topic", "topic_type") is None else has_any(t(r, "q6_topic", "topic_type"), "personal_story", "milestone_problem")),
    ("topic_showcase", 6, "Topic tagged product showcase or unboxing", lambda r: None if t(r, "q6_topic", "topic_type") is None else has_any(t(r, "q6_topic", "topic_type"), "product_showcase", "unboxing")),
    ("topic_humour", 6, "Topic is humour or a skit", lambda r: None if t(r, "q6_topic", "topic_type") is None else has_any(t(r, "q6_topic", "topic_type"), "humour_skit")),
    ("talking_head", 7, "Talking to camera", lambda r: None if not speech(r) else speech(r) in ("direct-to-camera", "both")),
    ("subtitles", 8, "Speech subtitled on screen", lambda r: None if speech(r) in ("", "none") else "subtitle" in (r["coded"].get("captions_on_screen") or "").lower()),
    ("text_any", 8, "Any text on screen", lambda r: None if not r["coded"].get("captions_on_screen") else not (r["coded"]["captions_on_screen"] or "").lower().startswith("none")),
    ("caption_long", 8, "Caption of 60 words or more", lambda r: None if not r["caption"] else caption_words(r) >= 60),
    ("caption_question", 8, "Caption asks a question", lambda r: None if not r["caption"] else "?" in r["caption"]),
    ("hashtags_6plus", 8, "Six or more hashtags", lambda r: None if not r["caption"] else hashtags(r) >= 6),
]


def run():
    principles = {}
    pf = DIR / "smm-research" / "feature-map.json"
    if pf.exists():
        principles = load(pf)
    out = []
    for fid, q, label, test in FEATURES:
        res = {"id": fid, "question": q, "label": label, "refs": principles.get(fid, [])}
        for metric in ("ppf", "ir"):
            whole = compare(REELS, test, metric)
            strata = [compare([r for r in REELS if r["collab"] == flag], test, metric) for flag in (True, False)]
            res[metric] = {"all": whole, "collab": strata[0], "creator_only": strata[1], "verdict": verdict(whole, strata)}
        out.append(res)
    meta = {
        "reels": len(REELS),
        "with_followers": sum(1 for r in REELS if r["ppf"] is not None),
        "with_interaction": sum(1 for r in REELS if r["ir"] is not None),
        "with_table": sum(1 for r in REELS if r["table"]),
        "median_ppf": st.median([r["ppf"] for r in REELS if r["ppf"] is not None]),
        "median_ir": st.median([r["ir"] for r in REELS if r["ir"] is not None]),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"meta": meta, "features": out}, ensure_ascii=False, indent=1), encoding="utf-8")

    def fmt(v, pct=False):
        if v is None:
            return "n/a"
        return f"{v * 100:.1f}%" if pct else f"{v:.2f}"

    lines = [
        "# Does it hold in our 173 Reels?",
        "",
        f"Built by `src/evidence_check.py`. {meta['reels']} verified Reels; plays per follower for {meta['with_followers']}, interaction rate for {meta['with_interaction']}. "
        f"Median plays per follower {fmt(meta['median_ppf'])}, median interaction rate {fmt(meta['median_ir'], True)}. Public counts read 15 Oct 2026; followers read 14 to 18 Oct 2026.",
        "",
        "A correlation check on a non-random sample: it can agree or disagree with a principle, never prove it. Delta runs from -1 to 1; positive means Reels with the feature score higher.",
        "",
        "| Q | Feature | Principles | Reels (creators) with / without | Plays per follower, median with / without | Delta | Reading | Interaction rate, median with / without | Delta | Reading |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in out:
        a, i = r["ppf"]["all"], r["ir"]["all"]
        lines.append(
            f"| {r['question']} | {r['label']} | {', '.join(r['refs']) or ''} | {a['n_yes']} ({a['creators_yes']}) / {a['n_no']} ({a['creators_no']}) | {fmt(a['median_yes'])} / {fmt(a['median_no'])} | "
            f"{fmt(a['delta'])} | {r['ppf']['verdict']} | {fmt(i['median_yes'], True)} / {fmt(i['median_no'], True)} | {fmt(i['delta'])} | {r['ir']['verdict']} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(ROOT)} ({len(out)} features, {meta['with_table']} Reels with the 8-question pass)")


if __name__ == "__main__":
    run()
