#!/usr/bin/env python3
"""LumeBook carousel audit: Instagram exports in, inventory, ranking and creative audit out.

    python3 research/carousel-audit/src/audit.py import ~/Downloads/<export>.csv    copy the export in, then build
    python3 research/carousel-audit/src/audit.py build                              rebuild every output
    python3 research/carousel-audit/src/audit.py status                             what is new, missing or too young
    python3 research/carousel-audit/src/audit.py link pacifier-weaning              tagged links for a topic (today)
    python3 research/carousel-audit/src/audit.py link --carousel 2026-10-20-pacifier
    python3 research/carousel-audit/src/audit.py hook-results [--write]             results for the pipeline's log

Inputs (edit these, never the outputs):
  exports/*.csv          Meta post exports as downloaded (lifetime totals; Hebrew headers seen so far)
  data/carousels.json    one entry per published carousel: what it is, where its slides are, hand counts
  data/scores.json       creative scores on src/rubric.md
  data/rules.json        timezones, Yarin's own activity per post, thresholds, UTM format
  data/books.json        carousel topic -> store book page, for the link maker
Outputs (rebuilt from the inputs every time):
  data/posts.json, carousel-inventory.csv, performance-ranking.csv, creative-audit.md,
  out/hook-results.preview.json (hook-results --write merges it into carousel/carousel-pipeline/hook-results.json)

An export's numbers are taken as of the end of its date range (the file name says the range). Every export is kept,
so a post read twice shows both snapshots. Standard library only. Internal: the outputs hold Instagram numbers and
sales figures, keep them off public pages.
"""
import argparse
import csv
import json
import re
import shutil
import statistics
import urllib.parse
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
ROOT = AUDIT.parents[1]
DATA, EXPORTS, OUT = AUDIT / "data", AUDIT / "exports", AUDIT / "out"
APPROVED = ROOT / "carousel" / "carousel-pipeline" / "approved"
HOOK_RESULTS = ROOT / "carousel" / "carousel-pipeline" / "hook-results.json"

# Export header -> field. The Hebrew names are from the 24 Oct 2026 export; the English ones are a guess for an
# export made with the interface in English. Headers not listed here are kept under "extra".
HEADERS = {
    "post_id": ["מזהה הפוסט", "Post ID"],
    "account_id": ["מזהה חשבון:", "מזהה חשבון", "Account ID"],
    "username": ["שם המשתמש של החשבון", "Account username"],
    "account_name": ["שם החשבון", "Account name"],
    "caption": ["תיאור", "Description"],
    "duration": ["משך זמן (שניות)", "Duration (sec)"],
    "publish_time": ["שעת הפרסום", "Publish time"],
    "permalink": ["קישור קבוע", "Permalink"],
    "post_type": ["סוג הפוסט", "Post type"],
    "data_comment": ["תגובה על נתונים", "Data comment"],
    "date": ["תאריך", "Date"],
    "views": ["צפיות", "Views"],
    "reach": ["תפוצה", "Reach"],
    "likes": ["לייקים", "Likes"],
    "shares": ["שיתופים", "Shares"],
    "follows": ["עוקבים", "Follows"],
    "comments": ["תגובות", "Comments"],
    "saves": ["שמירות", "Saves"],
}
REQUIRED = ["post_id", "publish_time", "permalink", "post_type", "reach"]
METRICS = ["views", "reach", "likes", "shares", "follows", "comments", "saves"]
TIME_FORMATS = ["%m/%d/%Y %H:%M", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"]
RANGE = re.compile(r"([A-Z][a-z]{2})-(\d{2})-(\d{4})_([A-Z][a-z]{2})-(\d{2})-(\d{4})")
MONTHS = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
DIMS = {"hook": "Hook", "visual": "Visual", "audience": "Audience", "emotion": "Emotion", "progression": "Swipe",
        "readability": "Read", "density": "Density", "value": "Value", "product": "Product", "cta": "CTA"}
DIM_LONG = {"hook": "First-slide hook", "visual": "Visual stopping power", "audience": "Audience relevance",
            "emotion": "Emotional resonance", "progression": "Curiosity and progression", "readability": "Mobile readability",
            "density": "Information density", "value": "Value to parents", "product": "Product relevance", "cta": "CTA clarity"}
CAPTION_CHECKS = [(re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])|בינה מלאכותית"), "mentions AI"),
                  (re.compile("לומבוק"), "brand spelling לומבוק"),
                  (re.compile("קוד הנחה|קוד אישי"), "offer wording (קוד)"),
                  (re.compile("—"), "em dash")]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))


# ---------- exports ----------

def export_range(path):
    m = RANGE.search(Path(path).name)
    if not m:
        return None, None
    a = date(int(m[3]), MONTHS[m[1]], int(m[2]))
    b = date(int(m[6]), MONTHS[m[4]], int(m[5]))
    return a, b


def parse_time(text, tz_from, tz_to):
    for fmt in TIME_FORMATS:
        try:
            t = datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
        return t.replace(tzinfo=tz_from).astimezone(tz_to)
    raise SystemExit(f"unknown publish time format: {text!r}")


def num(v):
    v = (v or "").strip().replace(",", "")
    return int(float(v)) if v else None


def post_type(raw):
    s = (raw or "").lower()
    if "קרוסל" in s or "carousel" in s:
        return "carousel"
    if "reel" in s:
        return "reel"
    if "תמונה" in s or "image" in s or "photo" in s:
        return "image"
    return raw or "unknown"


def read_export(path, rules):
    tz_x, tz_l = ZoneInfo(rules["export_timezone"]), ZoneInfo(rules["local_timezone"])
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        found = reader.fieldnames or []
        cols, extra = {}, []
        for h in found:
            key = next((k for k, names in HEADERS.items() if h.strip() in names), None)
            if key and key not in cols:
                cols[key] = h
            else:
                extra.append(h)
        missing = [k for k in REQUIRED if k not in cols]
        if missing:
            raise SystemExit(f"{Path(path).name}: no column for {', '.join(missing)}. Headers found: {', '.join(found)}. "
                             "Add the new header names to HEADERS in src/audit.py.")
        start, end = export_range(path)
        if end:
            as_of = datetime(end.year, end.month, end.day, 23, 59, tzinfo=tz_x).astimezone(tz_l)
        else:
            as_of = datetime.fromtimestamp(Path(path).stat().st_mtime, tz_l)
        rows = []
        for r in reader:
            if not (r.get(cols["post_id"]) or "").strip():
                continue
            g = lambda k: (r.get(cols[k]) or "").strip() if k in cols else ""  # noqa: E731
            posted = parse_time(g("publish_time"), tz_x, tz_l)
            link = g("permalink")
            sc = re.search(r"/(?:p|reel|tv)/([^/?#]+)", link)
            rows.append({
                "post_id": g("post_id"), "shortcode": sc.group(1) if sc else None, "permalink": link,
                "type": post_type(g("post_type")), "username": g("username"), "caption": r.get(cols.get("caption", ""), "") or "",
                "duration_s": num(g("duration")), "posted_local": posted.strftime("%Y-%m-%dT%H:%M"),
                "metrics": {k: num(g(k)) for k in METRICS},
                "extra": {h: r.get(h) for h in extra if (r.get(h) or "").strip()},
            })
    info = {"file": rel(path), "range_start": start.isoformat() if start else None,
            "range_end": end.isoformat() if end else None, "as_of": as_of.strftime("%Y-%m-%dT%H:%M"), "rows": len(rows)}
    return info, rows


def collect_posts(rules):
    """Every export in exports/, oldest first; per post the latest snapshot wins and earlier ones are kept."""
    exports, seen = [], {}
    for f in sorted(EXPORTS.glob("*.csv")):
        info, rows = read_export(f, rules)
        exports.append(info)
        for r in rows:
            seen.setdefault(r["post_id"], []).append((info, r))
    posts = {}
    for pid, reads in seen.items():
        reads.sort(key=lambda ir: ir[0]["as_of"])
        info, row = reads[-1]
        posts[pid] = {k: v for k, v in row.items() if k != "metrics"}
        posts[pid]["snapshots"] = [{"export": i["file"], "as_of": i["as_of"], **r["metrics"]} for i, r in reads]
        posts[pid]["latest"] = posts[pid]["snapshots"][-1]
    exports.sort(key=lambda x: x["as_of"])
    return exports, posts


# ---------- inventory + metrics ----------

def pipeline_fields(run):
    f = ROOT / run / "approved.json" if run else None
    if not f or not f.exists():
        return {}
    a = load(f)
    o = a.get("option") or {}
    h = o.get("hook") or {}
    pack = re.search(r"drafts/(\d{4}-\d{2}-\d{2})", str(a.get("source_pack", "")))
    return {"option_id": a.get("option_id") or o.get("id"), "pack_date": pack.group(1) if pack else a.get("date"),
            "hook_formula": h.get("formula"), "hook_family": o.get("hook_family"),
            "mechanism": h.get("mechanism") or o.get("mechanism"), "slide2_move": h.get("slide2_move") or o.get("slide2_move"),
            "addressee": o.get("addressee"), "awareness_stage": o.get("awareness_stage")}


def slide_files(slides_dir):
    d = ROOT / slides_dir
    return sorted(d.glob("*.png")) if d.is_dir() else []


def per_k(n, reach):
    return None if n is None or not reach else round(1000 * n / reach, 1)


def pct(n, reach):
    return None if n is None or not reach else round(100 * n / reach, 2)


def enrich(rules, posts):
    inv = load(DATA / "carousels.json")
    scores = load(DATA / "scores.json")["scores"]
    by_code = {p["shortcode"]: p for p in posts.values() if p.get("shortcode")}
    self_ = rules["self_activity"]
    rows = []
    for c in inv["carousels"]:
        p = by_code.get(c["shortcode"])
        m = (p or {}).get("latest") or {}
        man = c.get("manual") or {}
        reach = m.get("reach")
        lk = None if m.get("likes") is None else max(0, m["likes"] - self_["likes"])
        sv = None if m.get("saves") is None else max(0, m["saves"] - self_["saves"])
        sh = None if m.get("shares") is None else max(0, m["shares"] - self_["shares"])
        pc, cw = man.get("parent_comments"), man.get("code_word_comments")
        actions = None if sv is None else sv + (sh or 0) + (pc or 0)
        age = None
        if p:
            age = (datetime.fromisoformat(m["as_of"]) - datetime.fromisoformat(p["posted_local"])).total_seconds() / 86400
        flags = []
        if age is not None and age < rules["mature_days"]:
            flags.append(f"too new ({age:.1f} d)")
        if reach is not None and reach < rules["low_reach"]:
            flags.append("low reach")
        if actions is not None and actions < rules["few_actions"]:
            flags.append("few actions")
        sc = scores.get(c["id"]) or {}
        vals = [sc[d] for d in DIMS if isinstance(sc.get(d), (int, float))]
        files = slide_files(c["slides_dir"])
        rows.append({**c, **pipeline_fields(c.get("pipeline_run")),
                     "post": p, "posted_local": (p or {}).get("posted_local"), "permalink": (p or {}).get("permalink")
                     or f"https://www.instagram.com/p/{c['shortcode']}/", "caption": (p or {}).get("caption", ""),
                     "slides": len(files), "slide_files": [rel(f) for f in files],
                     "m": {"as_of": m.get("as_of"), "views": m.get("views"), "reach": reach, "likes": m.get("likes"),
                           "likes_org": lk, "saves": m.get("saves"), "saves_org": sv, "shares": sh,
                           "comments": m.get("comments"), "parent_comments": pc, "code_word_comments": cw,
                           "follows": m.get("follows"), "actions": actions, "age": age,
                           "mature": age is not None and age >= rules["mature_days"], "flags": flags,
                           "intent_k": per_k(cw, reach), "resonance_k": per_k(None if sv is None else sv + (sh or 0), reach),
                           "engagement_k": per_k(None if lk is None else lk + (sv or 0) + (sh or 0) + (pc or 0), reach),
                           "orders": man.get("orders_matched"), "utm_campaign": man.get("utm_campaign")},
                     "score": sc, "score_mean": round(statistics.mean(vals), 1) if vals else None})
    rows.sort(key=lambda r: r["posted_local"] or "9999")
    return inv, rows


def ranked(rows):
    have = [r for r in rows if r["m"]["reach"] is not None]
    key = lambda r: (-(r["m"]["intent_k"] or 0), -(r["m"]["resonance_k"] or 0), -r["m"]["reach"])  # noqa: E731
    mature = sorted([r for r in have if r["m"]["mature"]], key=key)
    young = sorted([r for r in have if not r["m"]["mature"]], key=key)
    return [(i + 1, r) for i, r in enumerate(mature)] + [(None, r) for r in young]


# ---------- outputs ----------

def fmt(v, nd=1):
    if v is None:
        return ""
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def write_inventory(rows, unmatched):
    cols = ["id", "posted_local", "permalink", "slides", "family", "topic", "topic_id", "cover_hook", "hook_structure",
            "hook_appeal", "perspective", "narrative", "motivation", "audience", "emotional_appeal", "product_focus",
            "picture_style", "text_weight", "cta_type", "code_word", "cta_slide", "caption", "status", "source",
            "slides_dir", "pipeline_run", "option_id", "pack_date", "hook_formula", "hook_family", "mechanism",
            "slide2_move", "addressee", "awareness_stage", "notes"]
    with open(AUDIT / "carousel-inventory.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**{k: "" if r.get(k) is None else r.get(k) for k in cols},
                        "posted_local": (r.get("posted_local") or "").replace("T", " "), "notes": r.get("cta_note", "")})
        for p in unmatched:
            w.writerow({"posted_local": p["posted_local"].replace("T", " "), "permalink": p["permalink"],
                        "caption": p["caption"], "notes": "in the export, no inventory entry yet: run status"})


def write_ranking(rows):
    cols = ["rank", "id", "posted_local", "age_days", "mature", "family", "slides", "reach", "views", "likes_reported",
            "likes_organic", "saves_reported", "saves_organic", "shares", "comments_reported", "parent_comments",
            "code_word_comments", "follows", "intent_per_1k_reach", "resonance_per_1k_reach", "engagement_per_1k_reach",
            "save_rate_pct", "share_rate_pct", "comment_rate_pct", "follow_rate_pct", "site_visits", "orders",
            "status", "flags", "creative_mean"]
    with open(AUDIT / "performance-ranking.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for rank, r in ranked(rows):
            m = r["m"]
            w.writerow([rank if rank else "too new", r["id"], (r["posted_local"] or "").replace("T", " "), fmt(m["age"]),
                        "yes" if m["mature"] else "no", r["family"], r["slides"], m["reach"], m["views"], m["likes"],
                        m["likes_org"], m["saves"], m["saves_org"], m["shares"], m["comments"], m["parent_comments"],
                        m["code_word_comments"], m["follows"], fmt(m["intent_k"]), fmt(m["resonance_k"]),
                        fmt(m["engagement_k"]), fmt(pct(m["saves_org"], m["reach"]), 2),
                        fmt(pct(m["shares"], m["reach"]), 2), fmt(pct(m["parent_comments"], m["reach"]), 2),
                        fmt(pct(m["follows"], m["reach"]), 2),
                        "unknown (no UTM)" if not m["utm_campaign"] else "ask Yossi: utm_campaign " + m["utm_campaign"],
                        "unknown" if m["orders"] is None else m["orders"], r.get("status", ""), "; ".join(m["flags"]),
                        fmt(r["score_mean"])])


def caption_flags(rows):
    out = []
    for r in rows:
        for rx, why in CAPTION_CHECKS:
            if rx.search(r.get("caption") or ""):
                out.append((r["id"], f"caption {why}"))
        if r.get("cta_note"):
            out.append((r["id"], r["cta_note"]))
        elif r.get("cta_type") == "mixed":
            out.append((r["id"], "the slide and the caption ask for different things"))
    return out


def write_creative(rows, exports):
    today = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%d %b %Y").lstrip("0")
    asof = exports[-1]["as_of"].replace("T", " ") if exports else "no export"
    L = ["# Carousel creative audit", "",
         f"Built by `research/carousel-audit/src/audit.py` on {today} from `data/scores.json` and `data/carousels.json`; "
         f"numbers from the export of {asof} (Israel time). Edit the JSON and run `build`; never edit this file.", "",
         "Scores are a reviewer's judgement from the posted slides at phone width, on the rubric at the end. They say what to "
         "fix, not what performs. Every post is organic. Numbers are after taking Yarin's own like and save off each post; "
         "shares stay as reported. A post under 7 days old is marked too new.", "",
         "## Scores", "",
         "| Carousel | Posted | " + " | ".join(DIMS.values()) + " | Mean |",
         "|---|---|" + "---:|" * (len(DIMS) + 1)]
    for r in rows:
        s = r["score"]
        L.append(f"| {r['id']} | {(r['posted_local'] or '')[:10]} | " + " | ".join(fmt(s.get(d)) for d in DIMS) +
                 f" | {fmt(r['score_mean'])} |")
    scored = [r for r in rows if r["score"]]
    if scored:
        means = {d: statistics.mean(r["score"][d] for r in scored if d in r["score"]) for d in DIMS}
        L.append("| **All** | | " + " | ".join(f"{means[d]:.1f}" for d in DIMS) + " | |")
        lo = sorted(means, key=means.get)[:3]
        low = lambda d: DIM_LONG[d] if d == "cta" else DIM_LONG[d][0].lower() + DIM_LONG[d][1:]  # noqa: E731
        L += ["", "Weakest dimensions across the set: " + ", ".join(f"{low(d)} ({means[d]:.1f})" for d in lo) + "."]
    flags = caption_flags(rows)
    if flags:
        L += ["", "## Flags", ""] + [f"- **{i}**: {why}" for i, why in flags]
    L += ["", "## Carousel by carousel"]
    for r in rows:
        m, s = r["m"], r["score"]
        L += ["", f"### {(r['posted_local'] or '')[:10]} · {r['topic']}", "",
              f"[{r['shortcode']}]({r['permalink']}) · {r['slides']} slides · {r['family']} · {r['source']} · slides in `{r['slides_dir']}`", "",
              f"Cover: {r['cover_hook']}", ""]
        if m["reach"] is not None:
            L += [f"Numbers: reach {m['reach']}, organic likes {m['likes_org']}, organic saves {m['saves_org']}, shares {m['shares']}, "
                  f"parent comments {fmt(m['parent_comments']) or 'not counted'}, code-word comments {fmt(m['code_word_comments']) or 'not counted'}, "
                  f"follows {m['follows']}" + (f". Flags: {', '.join(m['flags'])}." if m["flags"] else "."), ""]
        if s:
            L += ["Scores: " + ", ".join(f"{DIMS[d].lower()} {s.get(d)}" for d in DIMS) + f" (mean {fmt(r['score_mean'])}).", "",
                  f"**Worked.** {s.get('worked', '')}", "", f"**Failed.** {s.get('failed', '')}", "",
                  f"**Highest-priority fix.** {s.get('fix', '')}"]
        else:
            L += ["Not scored yet: add it to `data/scores.json`."]
    L += ["", (HERE / "rubric.md").read_text(encoding="utf-8").strip(), ""]
    text = "\n".join(L)
    (AUDIT / "creative-audit.md").write_text(text, encoding="utf-8")


# ---------- status, hook results, links ----------

def slide_folders():
    out = []
    for d in sorted(APPROVED.glob("*-all")):
        for sub in [d] + sorted(x for x in d.rglob("*") if x.is_dir()):
            if sub != d and any(sub.glob("*.png")):
                out.append(rel(sub))
    return out


def folder_guess(posted_local, used):
    t = datetime.fromisoformat(posted_local).date()
    names = [f"{x.day}.{x.month}.{x:%y}" for x in (t, t + timedelta(days=1), t - timedelta(days=1))]
    return [f for f in slide_folders() if f not in used and any(f.split("/")[-1] == n or f"/{n}/" in f + "/" for n in names)]


def status(inv, rows, posts, exports, rules):
    msgs = []
    handle = load(ROOT / "shared" / "facts.json")["brand"].get("instagram_live")
    known = {c["shortcode"] for c in inv["carousels"]}
    used = {c["slides_dir"] for c in inv["carousels"]} | {x["slides_dir"] for x in inv.get("not_posted", [])}
    if not exports:
        msgs.append("No export in exports/. Run: audit.py import <file.csv>")
    for p in sorted(posts.values(), key=lambda p: p["posted_local"]):
        if p["type"] == "carousel" and p.get("username") == handle and p.get("shortcode") not in known:
            guess = folder_guess(p["posted_local"], used)
            msgs.append(f"NEW  {p['posted_local'].replace('T', ' ')} {p['permalink']} has no inventory entry"
                        + (f"; slide folder may be {', '.join(guess)}" if guess else "; no slide folder found for that date"))
    for r in rows:
        if r["post"] is None and exports:
            msgs.append(f"MISS {r['id']} is in the inventory but in no export")
        if not r["score"]:
            msgs.append(f"SCORE {r['id']} has no creative score")
        if r["slides"] == 0:
            msgs.append(f"SLIDES {r['id']}: no PNGs in {r['slides_dir']}")
        if r["m"]["age"] is not None and not r["m"]["mature"]:
            ready = datetime.fromisoformat(r["posted_local"]) + timedelta(days=rules["mature_days"])
            msgs.append(f"YOUNG {r['id']} was {r['m']['age']:.1f} days old in the latest export; read it again after {ready:%d %b %H:%M}")
        man = r.get("manual") or {}
        if (man.get("dm_links_sent") or 0) > 0 and man.get("orders_matched") is None:
            msgs.append(f"ADMIN {r['id']}: {man['dm_links_sent']} DM link(s) sent; check the admin for matching orders and set manual.orders_matched")
    for f in slide_folders():
        if f not in used:
            msgs.append(f"FOLDER {f} is not in the inventory or the not_posted list")
    return msgs


def hook_results(rows, write=False):
    recs = []
    for r in rows:
        if not r.get("option_id") or r["family"] not in ("kid", "expert") or not r["m"]["mature"]:
            continue
        m = r["m"]
        recs.append({"date_posted": r["posted_local"][:10], "pack_date": r.get("pack_date"), "option_id": r["option_id"],
                     "topic_id": r["topic_id"], "hook_formula": r.get("hook_formula"), "hook_family": r.get("hook_family"),
                     "mechanism": r.get("mechanism"), "slide2_move": r.get("slide2_move"), "addressee": r.get("addressee"),
                     "code_word": r.get("code_word"), "test_id": None, "variable_changed": None,
                     "posted_at_local": r["posted_local"][11:16], "reach": m["reach"], "non_follower_share": None,
                     "cta_comments": m["code_word_comments"], "preview_visits": None, "preview_completions": None,
                     "purchases": m["orders"], "sends": m["shares"], "saves": m["saves"], "profile_visits": None,
                     "account_status_flag": None,
                     "notes": f"From research/carousel-audit (export of {m['as_of']}). Saves include Yarin's own save; "
                              "no UTM on any link before 24 Oct 2026, so preview_visits and purchases are unknown.",
                     "promotion_note": None})
    save(OUT / "hook-results.preview.json", {"posts": recs})
    if write:
        hr = load(HOOK_RESULTS)
        have = {(p.get("date_posted"), p.get("option_id")): i for i, p in enumerate(hr.get("posts", []))}
        for rec in recs:
            k = (rec["date_posted"], rec["option_id"])
            if k in have:
                hr["posts"][have[k]] = rec
            else:
                hr.setdefault("posts", []).append(rec)
        save(HOOK_RESULTS, hr)
    return recs


def links(topic, day, book=None, place=None, variant=None):
    rules, books = load(DATA / "rules.json"), load(DATA / "books.json")
    if not re.fullmatch(r"[a-z0-9-]+", topic or ""):
        raise SystemExit(f"topic must be a slug like pacifier-weaning, got {topic!r}")
    note = None
    if book is None and topic in books["topics"]:
        book = books["topics"][topic]["book"]
        if books["topics"][topic].get("basis") != "pack":
            note = f"book {book} for {topic} is inferred, check the page before sending"
    if book is None:
        note = f"no book for {topic} in data/books.json: the link opens the store home page (add the topic, or pass --book)"
    base = f"{books['store_url']}/books/{book}" if book else books["store_url"]
    u = rules["utm"]
    out = []
    for pl in [place] if place else u["places"]:
        q = {"utm_source": u["source"], "utm_medium": u["medium"], "utm_campaign": u["campaign_prefix"] + topic,
             "utm_content": "bio" if pl == "bio" else f"{pl}-{day.strftime('%Y%m%d')}"}
        if variant:
            q["utm_term"] = variant.lower()
        out.append((pl, base + "?" + urllib.parse.urlencode(q)))
    return out, note


# ---------- commands ----------

def build(quiet=False):
    rules = load(DATA / "rules.json")
    exports, posts = collect_posts(rules)
    save(DATA / "posts.json", {"_about": "Built by src/audit.py from exports/*.csv; do not edit. Times are Israel time.",
                               "exports": exports, "posts": dict(sorted(posts.items(), key=lambda kv: kv[1]["posted_local"]))})
    inv, rows = enrich(rules, posts)
    handle = load(ROOT / "shared" / "facts.json")["brand"].get("instagram_live")
    known = {c["shortcode"] for c in inv["carousels"]}
    unmatched = [p for p in posts.values() if p["type"] == "carousel" and p.get("username") == handle and p.get("shortcode") not in known]
    write_inventory(rows, sorted(unmatched, key=lambda p: p["posted_local"]))
    write_ranking(rows)
    write_creative(rows, exports)
    hook_results(rows)
    if "—" in (AUDIT / "creative-audit.md").read_text(encoding="utf-8"):
        print("warning: creative-audit.md has an em dash (from a caption or a data file); fix the source")
    msgs = status(inv, rows, posts, exports, rules)
    if not quiet:
        print(f"built {len(rows)} carousels from {len(exports)} export(s): carousel-inventory.csv, performance-ranking.csv, "
              f"creative-audit.md, out/hook-results.preview.json")
        for m in msgs:
            print("  " + m)
    return msgs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("import", help="copy Meta export(s) into exports/ and rebuild")
    a.add_argument("files", nargs="+")
    sub.add_parser("build", help="rebuild every output")
    sub.add_parser("status", help="what is new, missing or too young")
    lk = sub.add_parser("link", help="tagged links for a carousel topic")
    lk.add_argument("topic", nargs="?")
    lk.add_argument("--carousel", help="an id from data/carousels.json: takes its topic and post date")
    lk.add_argument("--date", help="post date YYYY-MM-DD (default today)")
    lk.add_argument("--book", type=int, help="store book number, overrides data/books.json")
    lk.add_argument("--place", choices=["dm", "bio", "story"], help="where the link goes out (utm_content)")
    lk.add_argument("--variant", help="test arm, sent as utm_term, e.g. a or b")
    hr = sub.add_parser("hook-results", help="results of 7+ day old pipeline carousels in the hook-results.json format")
    hr.add_argument("--write", action="store_true", help="merge them into carousel/carousel-pipeline/hook-results.json")
    args = ap.parse_args()

    if args.cmd == "import":
        EXPORTS.mkdir(parents=True, exist_ok=True)
        for f in args.files:
            src = Path(f).expanduser().resolve()
            if not src.is_file():
                raise SystemExit(f"no such file: {f}")
            dst = EXPORTS / src.name
            if src != dst:
                shutil.copy2(src, dst)
                print(f"copied {src.name} into {rel(EXPORTS)}/")
        build()
    elif args.cmd == "build":
        build()
    elif args.cmd == "status":
        for m in build(quiet=True) or ["nothing to do"]:
            print(m)
    elif args.cmd == "link":
        topic, day = args.topic, None
        if args.carousel:
            c = next((c for c in load(DATA / "carousels.json")["carousels"] if c["id"] == args.carousel), None)
            if not c:
                raise SystemExit(f"no carousel {args.carousel} in data/carousels.json")
            topic = c["topic_id"]
            day = date.fromisoformat(c["id"][:10])
        if args.date:
            day = date.fromisoformat(args.date)
        day = day or datetime.now(ZoneInfo("Asia/Jerusalem")).date()
        out, note = links(topic, day, args.book, args.place, args.variant)
        for pl, url in out:
            print(f"{pl:5} {url}")
        if note:
            print("note: " + note)
    elif args.cmd == "hook-results":
        rules = load(DATA / "rules.json")
        _, posts = collect_posts(rules)
        _, rows = enrich(rules, posts)
        recs = hook_results(rows, write=args.write)
        print(f"{len(recs)} record(s) in {rel(OUT / 'hook-results.preview.json')}"
              + (f", merged into {rel(HOOK_RESULTS)}" if args.write else "; add --write to merge them into the pipeline's log"))


if __name__ == "__main__":
    main()
