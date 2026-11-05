#!/usr/bin/env python3
"""Build the Product Reels Playbook page (for Yarin): an app with one page per tool, principle, concept and Reel.

    python3 research/israeli-product-reels/src/build_research_page.py

Inputs:  README.md, playbook.md, breakdowns.md, source-index.md; smm-research/notes/*.md (the principles,
         their evidence and the myths), smm-research/overlaps.json, feature-map.json, sample-check.json;
         src/table/*.json (the 8-question rows), src/review.json, src/coded/, src/media_info_15oct.json,
         src/followers.json; media/projects/2026-10-15-israeli-product-reels/annotated/ (frame strips).
Output:  reels-research.html, an artifact page (no doctype: the artifact host wraps it). It is
         src/page/playbook.css and src/page/playbook.js around one JSON bundle; the browser renders each
         view from a plain hash route (#home, #tool-hook, #p-H1, #reel-DTugYwmDNKa, #concept-2, #dive-3).

Edit the markdown and JSON sources, then rebuild; never edit the HTML. Standard library only.
"""
import json
import re
import statistics as st
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIR = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "shared" / "design"))
sys.path.insert(0, str(HERE))
import design  # noqa: E402
from mdlite import inline, render, sections, strip_md, table_rows, img_tag  # noqa: E402
from mdlite import bullets_by_label as _bullets  # noqa: E402


def bullets_by_label(md):
    """Labelled bullets with each text starting on a capital letter."""
    return {k: (v[:1].upper() + v[1:] if v else v) for k, v in _bullets(md).items()}

OUT = DIR / "reels-research.html"
TITLE = "Product Reels Playbook"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def load(path):
    return json.loads(read(path))


def num(s):
    m = re.match(r"^([\d.]+)\s*([KkMm]?)$", str(s or "").replace(",", "").strip())
    return float(m.group(1)) * {"": 1, "k": 1e3, "m": 1e6}[m.group(2).lower()] if m else None


# ---------------------------------------------------------------- the 8 tools

TOOLS = [
    dict(id="hook", n=1, prefix="H", name="Hook", q="q1_hook", job="Win the first 3 seconds",
         ask="What's the hook, and why does it work?"),
    dict(id="watch", n=2, prefix="R", name="Keep them watching", q="q2_flow", job="A new reason to stay every few seconds, and one to send it",
         ask="What happens every few seconds, and why is it good for retention and interaction?"),
    dict(id="cta", n=3, prefix="C", name="Call to action", q="q3_cta", job="Ask for one thing, once the value is clear",
         ask="What's the CTA, and why does it work?"),
    dict(id="show", n=4, prefix="S", name="What to show", q="q4_shown", job="The book in use, and the proof that settles the doubt",
         ask="What is shown, and why?"),
    dict(id="edit", n=5, prefix="E", name="Editing", q="q5_edit", job="Cut dead air, keep a calm pace, build for sound",
         ask="How is the Reel edited, and why does it work?"),
    dict(id="topic", n=6, prefix="K", name="Topic", q="q6_topic", job="A moment parents feel, not a product pitch",
         ask="What is the content about, and why?"),
    dict(id="film", n=7, prefix="F", name="Filming", q="q7_filmed", job="Vertical, close, homemade and clean",
         ask="What is being filmed, and why?"),
    dict(id="text", n=8, prefix="T", name="Text and caption", q="q8_text", job="Words that work muted, inside the safe zone",
         ask="What is written on screen and in the caption, and why does it work?"),
]
BY_PREFIX = {t["prefix"]: t for t in TOOLS}
NOTES = [("hooks-retention", "Hooks, retention and interaction", "HR"), ("cta-text", "Calls to action, text and caption", "CT"),
         ("shown-filmed", "What is shown and filmed", "SF"), ("edit-topic", "Editing and content topic", "EK")]
NOTE_OF = {p: slug for slug, _, ps in NOTES for p in ps}

KIND_RULES = [("peer-review", "Peer-reviewed"), ("meta-analysis", "Peer-reviewed"), ("journal", "Peer-reviewed"), ("conference", "Conference paper"),
              ("regulator", "Regulator or law"), ("gov.", "Regulator or law"), ("law (", "Regulator or law"), ("[il]", "Regulator or law"),
              ("industry", "Industry data"), ("survey", "Industry data"), ("platform", "Platform"), ("official", "Platform"),
              ("news", "News report"), ("trade press", "News report"), ("press report", "News report"), ("practitioner", "Practitioner")]


def evidence_kind(text):
    low = text.lower()
    return next((v for k, v in KIND_RULES if k in low), "Source")


def strength_level(text):
    first = re.split(r"(?<=[a-z)])\.\s", text.strip(), maxsplit=1)[0].lower()
    words = set(re.findall(r"strong|moderate|weak|contested", first))
    if first.startswith("contested"):
        return "contested"
    if "strong" in words and ({"weak", "contested"} & words):
        return "mixed"
    if first.startswith("weak to moderate"):
        return "weak-moderate"
    for k in ("strong", "moderate", "weak"):
        if first.startswith(k):
            return k
    return "mixed"


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def field(block, name):
    m = re.search(r"^- \*\*" + re.escape(name) + r":\*\*\s*(.*?)(?=^- \*\*|\Z)", block, re.S | re.M)
    return m.group(1).strip() if m else ""


def evidence_items(block):
    items, cur = [], None
    for line in block.splitlines():
        m = re.match(r"^\s{2,}- (.*)$", line)
        if m:
            cur = m.group(1).strip()
            items.append(cur)
        elif items and line.startswith("    ") and line.strip():
            items[-1] += " " + line.strip()
    out = []
    for t in items:
        link = re.search(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", t)
        title = link.group(1) if link else strip_md(re.split(r",|\(link in", t, maxsplit=1)[0])
        out.append({"title": strip_md(title), "url": link.group(2) if link else "", "kind": evidence_kind(t), "html": inline(t)})
    return out


def parse_principles():
    P = {}
    for slug, _, prefixes in NOTES:
        text = read(DIR / "smm-research" / "notes" / f"{slug}.md")
        for m in re.finditer(r"^####\s+([A-Z]\d{1,2})\.\s+(.+?)\n(.*?)(?=^#{2,4}\s|\Z)", text, re.S | re.M):
            pid, title, block = m.group(1), m.group(2).strip(), m.group(3)
            if pid[0] not in prefixes:
                continue
            strength = field(block, "Strength")
            P[pid] = {
                "id": pid, "tool": BY_PREFIX[pid[0]]["id"], "title": strip_md(title),
                "rule": inline(field(block, "Rule")),
                "apply": inline(cap(field(block, "Transfer to LumeBook"))),
                "level": strength_level(strength), "strength": inline(strength),
                "sources": evidence_items(field(block, "Evidence")),
                "note": slug,
            }
    return P


# ---------------------------------------------------------------- the 173 Reels

def reels():
    review = load(HERE / "review.json")
    info = load(HERE / "media_info_15oct.json")
    fol = load(HERE / "followers.json")
    out = []
    for code, rv in review.items():
        if not isinstance(rv, dict) or rv.get("status") != "verified":
            continue
        tp = HERE / "table" / f"{code}.json"
        if not tp.exists():
            continue
        t, coded, mi = load(tp), load(HERE / "coded" / f"{code}.json"), info.get(code, {})
        handle = (mi.get("owner") or coded.get("handle") or "").lstrip("@")
        f = fol.get(handle)
        followers = num(f[0]) if isinstance(f, list) else None
        plays = mi.get("plays")
        q = {}
        for tool in TOOLS:
            d = t.get(tool["q"]) or {}
            tags = d.get("hook_type") or d.get("retention_devices") or d.get("placement") or d.get("proof_type") or d.get("topic_type") or []
            item = {"what": inline(d.get("what", "")), "why": inline(d.get("why", "")), "refs": d.get("refs") or [],
                    "tags": [x for x in tags if x not in ("none", "none_clear")]}
            if tool["id"] == "watch":
                item["beats"] = [{"t": b.get("t", ""), "does": b.get("does", ""), "what": inline(b.get("what", "")), "why": inline(b.get("why", ""))}
                                 for b in d.get("beats") or []]
                item["what"] = inline(d.get("interaction_prompts", ""))
            if tool["id"] == "text":
                item["screen"] = inline(d.get("on_screen", ""))
                item["caption"] = inline(d.get("caption", ""))
                item["what"] = item["screen"]
            q[tool["id"]] = item
        out.append({
            "code": code, "handle": handle, "product": inline(rv.get("product", "")), "cat": coded.get("category", "other"),
            "approach": rv.get("approach", ""), "verdict": str(t.get("verdict", "")).lower(), "deep": rv.get("deep"),
            "plays": plays, "ppf": round(plays / followers, 2) if plays and followers else None, "followers": followers,
            "dur": mi.get("duration_s"), "date": rv.get("published", ""),
            "one": inline(t.get("one_line", "")), "weak": inline(t.get("weak_points", "")), "lb": inline(t.get("lumebook_takeaway", "")),
            "q": q,
        })
    out.sort(key=lambda r: (r["deep"] is None, int(r["deep"] or 99), -(r["ppf"] or 0)))
    return out


PRETTY = {"audience_callout": "Calls out the viewer", "curiosity_gap": "Curiosity gap", "face_to_camera": "Face to camera", "product_reveal": "Product in frame",
          "relatable_moment": "Relatable moment", "result_first": "Result first", "bold_claim": "Bold claim", "list_promise": "List promise",
          "pattern_interrupt": "Pattern interrupt", "price_or_offer": "Price or offer", "problem": "Names a problem", "question": "Question",
          "new_visual_every_few_s": "New visual every few seconds", "story_arc": "Story arc", "payoff_at_end": "Payoff at the end", "open_loop": "Open loop",
          "reveal_held_back": "Reveal held back", "re_hook_mid": "Re-hook in the middle", "numbered_list": "Numbered list", "loop_ending": "Loops back",
          "repetition": "Repetition", "caption": "In the caption", "on_screen_end": "On screen at the end", "spoken": "Said out loud",
          "on_screen_early": "On screen early", "none": "No CTA", "in_use": "Product in use", "child_reaction": "Child's reaction", "result": "The result",
          "testimonial_story": "Personal story", "screen_recording": "Screen recording", "before_after": "Before and after", "side_by_side": "Side by side",
          "expert_authority": "Expert", "price": "Price", "product_showcase": "Product showcase", "child_using_it": "Child using it",
          "personal_story": "Personal story", "useful_tip": "Useful tip", "expert_advice": "Expert advice", "making_diy": "Making or DIY",
          "milestone_problem": "Milestone problem", "gift_occasion": "Gift or occasion", "unboxing": "Unboxing", "list_review": "List review",
          "humour_skit": "Humour or skit"}


def distributions(R):
    """What the 173 Reels do, per tool: one count list each."""
    def tagcount(tool, key):
        c = Counter()
        for r in R:
            for x in r["q"][tool]["tags"]:
                c[x] += 1
        return [[PRETTY.get(k, k.replace("_", " ").capitalize()), v] for k, v in c.most_common()]
    coded = {c: load(HERE / "coded" / f"{c}.json") for c in (r["code"] for r in R)}

    def bucket(values, edges, labels):
        c = Counter()
        for v in values:
            if v is None:
                continue
            for e, lab in zip(edges, labels):
                if v <= e:
                    c[lab] += 1
                    break
        return [[lab, c[lab]] for lab in labels]

    shot = [(r["dur"] / coded[r["code"]]["n_shots_estimate"]) if r["dur"] and coded[r["code"]].get("n_shots_estimate") else None for r in R]
    face = Counter()
    for r in R:
        c = coded[r["code"]]
        if c.get("face_on_camera") in ("creator's face", "other adult"):
            face["An adult's face"] += 1
        elif c.get("child_on_camera") == "yes":
            face["A child, no adult face"] += 1
        else:
            face["No face (hands only)"] += 1
    text = Counter()
    for r in R:
        cap = str(coded[r["code"]].get("captions_on_screen") or "").lower()
        if cap.startswith("none"):
            text["No text on screen"] += 1
        elif "subtitle" in cap:
            text["Subtitles of the speech"] += 1
        else:
            text["Headline or labels only"] += 1
    return {
        "hook": {"title": "Hook types in the 173 Reels", "rows": tagcount("hook", "hook_type")},
        "watch": {"title": "What keeps them watching", "rows": tagcount("watch", "retention_devices")},
        "cta": {"title": "Where the CTA sits", "rows": tagcount("cta", "placement")},
        "show": {"title": "The proof they show", "rows": tagcount("show", "proof_type")},
        "edit": {"title": "Average shot length", "rows": bucket(shot, [2, 3, 5, 1e9], ["Under 2 s", "2 to 3 s", "3 to 5 s", "Over 5 s"])},
        "topic": {"title": "What the Reels are about", "rows": tagcount("topic", "topic_type")},
        "film": {"title": "Who is on camera", "rows": [[k, face[k]] for k in ("An adult's face", "A child, no adult face", "No face (hands only)")]},
        "text": {"title": "Words on screen", "rows": [[k, text[k]] for k in ("Subtitles of the speech", "Headline or labels only", "No text on screen")]},
    }


def sample_features():
    sc = load(DIR / "smm-research" / "sample-check.json")
    out = []
    for f in sc["features"]:
        a = f["ppf"]["all"]
        out.append({"id": f["id"], "q": f["question"], "label": f["label"], "refs": f.get("refs", []),
                    "ny": a["n_yes"], "nn": a["n_no"], "my": a["median_yes"], "mn": a["median_no"], "p": a["p"], "d": a["delta"],
                    "v": f["ppf"]["verdict"], "iv": f["ir"]["verdict"],
                    "iy": f["ir"]["all"]["median_yes"], "in": f["ir"]["all"]["median_no"]})
    return sc["meta"], out


# ---------------------------------------------------------------- playbook sections

def playbook():
    play = sections(read(DIR / "playbook.md"), 2)
    P = {t.split(". ", 1)[0]: (t, b) for t, b in play[1:]}
    intro = play[0][1].split("\n", 2)[-1]
    return P, intro


def findings(body):
    items, intro, outro = [], [], []
    for line in body.splitlines():
        m = re.match(r"^(\d+)\. \*\*(.+?)\*\*\s*(.*)$", line.strip())
        if m:
            text = m.group(3)
            seen, _, mine = text.partition("My read:")
            items.append({"n": int(m.group(1)), "title": inline(m.group(2).rstrip(".")), "seen": inline(seen.strip()), "read": inline(cap(mine.strip()))})
        elif line.strip():
            (outro if items else intro).append(line)
    return {"intro": render("\n".join(intro)), "items": items, "outro": render("\n".join(outro))}


def approaches(body):
    head_rows = [l for l in body.splitlines() if l.strip().startswith("|")]
    _, rows = table_rows(head_rows)
    subs = {t.split(".", 1)[0]: bullets_by_label(b) for t, b in sections(body, 3)[1:]}
    out = []
    for r in rows:
        letter = r[0]
        codes = re.findall(r"\[([A-Za-z0-9_-]{8,})\]\(https://www\.instagram\.com/reel/", r[3])
        sub = subs.get(letter, {})
        out.append({"letter": letter, "name": inline(r[1]), "what": inline(r[2]), "examples": codes, "who": inline(r[4]),
                    "why": inline(next((v for k, v in sub.items() if k.startswith("Why it works")), "")),
                    "fits": inline(sub.get("Fits LumeBook when", "")), "limits": inline(sub.get("Limits", "")), "phone": inline(sub.get("Phone notes", ""))})
    return out


def fixes(body):
    _, rows = table_rows([l for l in body.splitlines() if l.strip().startswith("|")])
    return [{"saw": inline(r[0]), "where": inline(r[1]), "do": inline(r[2])} for r in rows]


CONCEPT_GROUPS = {
    "summary": ["Idea", "Intended response", "Length"],
    "warn": ["Honesty rule", "Book caveat", "Price on screen (S3, added 18 Oct)"],
    "why": ["Grounded in"],
}


def concepts(body):
    parts = sections(body, 3)
    pre = parts[0][1]
    out = []
    for title, b in parts[1:]:
        m = re.match(r'Concept (\d): "(.+?)" \((.+?)\)', title)
        labels = bullets_by_label(b)
        main_lines, skip = [], False
        for line in b.splitlines():
            if line.startswith("- **"):
                skip = True
                continue
            if skip and (line.startswith("  ") and line.strip()):
                continue
            skip = False
            main_lines.append(line)
        used = {k for g in CONCEPT_GROUPS.values() for k in g}
        out.append({
            "n": int(m.group(1)), "he": m.group(2), "en": inline(m.group(3)),
            "summary": [[k, inline(labels[k])] for k in CONCEPT_GROUPS["summary"] if k in labels],
            "warn": [[re.sub(r" \(.*\)$", "", k), inline(labels[k])] for k in CONCEPT_GROUPS["warn"] if k in labels],
            "why": [[k, inline(labels[k])] for k in CONCEPT_GROUPS["why"] if k in labels],
            "production": [[k, inline(v)] for k, v in labels.items() if k not in used],
            "main": render("\n".join(main_lines)),
        })
    return {"intro": render(pre), "items": out}


def steps(body):
    intro, out, cur = [], [], None
    for line in body.splitlines():
        m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", line.strip())
        if m and not line.startswith("-"):
            cur = {"title": inline(m.group(1)), "note": inline(m.group(2).strip("() ")), "md": []}
            out.append(cur)
        elif cur:
            cur["md"].append(line)
        else:
            intro.append(line)
    for s in out:
        s["html"] = render("\n".join(s.pop("md")))
    return {"intro": render("\n".join(intro)), "steps": out}


def proof(body):
    lines = body.splitlines()
    tbl = [l for l in lines if l.strip().startswith("|")]
    _, rows = table_rows(tbl)
    out = []
    for r in rows:
        v = r[3]
        key = "holds" if v.startswith("**Holds") else "changed" if v.startswith("**Changed") else "unproven" if v.startswith("**Unproven") else "other"
        out.append({"rule": inline(r[0]), "research": inline(r[1]), "sample": inline(r[2]), "key": key, "verdict": inline(v)})
    kinds = [inline(m.group(2)) + " " + inline(m.group(3)) for m in re.finditer(r"^(\d)\. \*\*(.+?)\*\*\s*(.*)$", body, re.M)]
    kind_titles = [strip_md(m.group(2)) for m in re.finditer(r"^(\d)\. \*\*(.+?)\*\*\s*(.*)$", body, re.M)]
    kind_text = [inline(m.group(3)) for m in re.finditer(r"^(\d)\. \*\*(.+?)\*\*\s*(.*)$", body, re.M)]
    clear = next((l for l in lines if l.startswith('"Clear" below')), "")
    changes = {}
    for m in re.finditer(r"^- \*\*Concept (\d) \((.+?)\):\*\*\s*(.*)$", body, re.M):
        changes[m.group(1)] = inline(cap(m.group(3)))
    sure = next((l for l in lines if l.startswith("**How sure this is:**")), "")
    return {"kinds": [{"title": a, "text": b} for a, b in zip(kind_titles, kind_text)], "clear": inline(clear),
            "rows": out, "changes": changes, "sure": inline(sure.replace("**How sure this is:**", "").strip())}


def dives():
    parts = sections(read(DIR / "breakdowns.md"), 2)
    intro_md = parts[0][1].split("\n", 2)[-1]
    howto = next((b for t, b in parts[1:] if t.startswith("How to read")), "")
    tbl = [l for l in intro_md.splitlines() if l.strip().startswith("|")]
    _, list_rows = table_rows(tbl)
    out = []
    for t, b in parts[1:]:
        m = re.match(r"^(\d)\. (.+?): (.+)$", t)
        if not m:
            continue
        lines = b.splitlines()
        meta_rows = [l for l in lines if l.strip().startswith("| ") and not l.strip().startswith("| Time")]
        meta = []
        first_tbl = []
        for l in lines:
            if l.strip().startswith("|"):
                first_tbl.append(l)
            elif first_tbl:
                break
        if first_tbl:
            _, mr = table_rows(first_tbl)
            meta = [[strip_md(r[0]), inline(r[1])] for r in mr if len(r) > 1]
        img = next((l.strip() for l in lines if l.strip().startswith("![")), "")
        strip = ""
        if img:
            mm = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", img)
            strip = img_tag(mm.group(1), mm.group(2)) if mm else ""
        secs, cur = [], None
        after_img = False
        for l in lines:
            if l.strip().startswith("!["):
                after_img = True
                continue
            if not after_img:
                continue
            mm = re.match(r"^\*\*(\d)\. (.+?)\*\*\s*(.*)$", l)
            if mm:
                cur = {"n": int(mm.group(1)), "title": inline(mm.group(2).rstrip(".")), "md": [mm.group(3)]}
                secs.append(cur)
            elif cur is not None:
                cur["md"].append(l)
        for s in secs:
            s["html"] = render("\n".join(s.pop("md")))
        n = int(m.group(1))
        lr = list_rows[n - 1] if n - 1 < len(list_rows) else ["", "", "", ""]
        out.append({"n": n, "who": inline(m.group(2)), "sub": inline(m.group(3)), "teaches": inline(lr[2]), "product": inline(lr[3]),
                    "meta": meta, "strip": strip, "sections": secs})
    intro_text = "\n".join(l for l in intro_md.splitlines() if not l.strip().startswith("|"))
    return {"intro": render(intro_text), "howto": render(howto), "items": out}


def notes():
    out = []
    for slug, title, _ in NOTES:
        parts = sections(read(DIR / "smm-research" / "notes" / f"{slug}.md"), 2)
        lead = render(parts[0][1].split("\n", 1)[-1])
        secs = []
        for t, b in parts[1:]:
            name = re.sub(r"^\d+\.\s*", "", t)
            if name.lower().startswith("principles"):
                continue
            secs.append({"title": inline(name), "html": render(b)})
        out.append({"slug": slug, "title": title, "lead": lead, "sections": secs})
    return out


def home_and_method():
    rd = dict(sections(read(DIR / "README.md"), 2))
    return {"bottom": render(rd.get("Bottom line", "")), "five": render(rd.get("Watch these five first", "")),
            "film": render(rd.get("Film this first", ""))}, \
           {"limits": [inline(re.sub(r"^- ", "", l)) for l in rd.get("Evidence limits", "").splitlines() if l.startswith("- ")],
            "rebuild": render(rd.get("Rebuild", "")), "sources": render(read(DIR / "source-index.md").split("\n", 2)[-1])}


# ---------------------------------------------------------------- assemble

def build():
    P = parse_principles()
    R = reels()
    meta, feats = sample_features()
    overlaps = load(DIR / "smm-research" / "overlaps.json")["groups"]
    for g in overlaps:
        for pid in g["ids"]:
            if pid in P:
                P[pid]["overlaps"] = [x for x in g["ids"] if x != pid]
    for pid, p in P.items():
        p["features"] = [f["id"] for f in feats if pid in f["refs"]]
        cites, ex = 0, []
        tool = next(t for t in TOOLS if t["id"] == p["tool"])
        for r in R:
            hit = any(pid in (r["q"][t["id"]]["refs"] or []) or re.search(r"\b" + pid + r"\b", r["q"][t["id"]]["why"]) for t in TOOLS)
            if hit:
                cites += 1
                own = r["q"][tool["id"]]
                if r["verdict"] == "works" and (pid in own["refs"] or re.search(r"\b" + pid + r"\b", own["why"])):
                    ex.append(r)
        ex.sort(key=lambda r: -(r["ppf"] or 0))
        p["cites"] = cites
        p["examples"] = [r["code"] for r in ex[:3]]
    PB, pb_intro = playbook()
    home, method = home_and_method()
    data = {
        "tools": TOOLS,
        "principles": P,
        "order": sorted(P, key=lambda k: ([t["prefix"] for t in TOOLS].index(k[0]), int(k[1:]))),
        "reels": R,
        "dist": distributions(R),
        "features": feats,
        "meta": {**meta, "reels": len(R), "creators": len({r["handle"] for r in R}), "principles": len(P)},
        "proof": proof(PB["8"][1]),
        "findings": findings(PB["1"][1]),
        "preface": render(pb_intro),
        "approaches": approaches(PB["2"][1]),
        "fixes": fixes(PB["3"][1]),
        "concepts": concepts(PB["4"][1]),
        "shoot": steps(PB["5"][1]),
        "setup": [[k, inline(v)] for k, v in bullets_by_label(PB["6"][1]).items()],
        "log": render(PB["7"][1]),
        "dives": dives(),
        "notes": notes(),
        "home": home,
        "method": method,
        "logo": design.logo_data_uri(),
    }
    return data


def page(data):
    css = read(HERE / "page" / "playbook.css")
    js = read(HERE / "page" / "playbook.js")
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="claude:viewport-fit-sides" content="cover">
<title>{TITLE}</title>
{design.head()}
<style>{design.category_css("reels-tools")}
{css}</style>
<div class="pb" id="pb" dir="ltr" lang="en">
  <aside class="pb-side" id="pb-side" aria-label="Playbook sections"></aside>
  <div class="pb-scrim" id="pb-scrim" hidden></div>
  <main class="pb-main" id="pb-main" tabindex="-1">
    <header class="pb-bar"><button class="pb-menu" id="pb-menu" type="button" aria-label="Open the menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button><span class="pb-bar-title" id="pb-bar-title">Reels Playbook</span></header>
    <div class="pb-view" id="pb-view"><noscript>This page needs JavaScript to show its sections.</noscript></div>
  </main>
</div>
<script type="application/json" id="pb-data">{blob}</script>
<script>{js}</script>
"""


if __name__ == "__main__":
    d = build()
    html_out = page(d)
    OUT.write_text(html_out, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(html_out):,} bytes, {len(d['principles'])} principles, {len(d['reels'])} Reels")
