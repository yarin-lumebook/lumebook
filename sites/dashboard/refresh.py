#!/usr/bin/env python3
"""Build the Lumebook dashboard snapshot.

Reads everything local to the project folder (SMM plan site, creator CSV,
competitor DB, ambassadors pages, file inventory), checks the live sites and
public Instagram follower counts, and optionally parses the signup Sheet
(the Google Drive connector's text export, saved to a file by the caller).

Usage:
  python3 sites/dashboard/refresh.py [--sheet-md PATH] [--skip-network]

Writes sites/dashboard/out/snapshot.json and sites/dashboard/out/history.json.
Only standard library; safe to run any time.
"""
import argparse, ast, csv, html, json, os, re, subprocess, time, urllib.request
from collections import Counter
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
# Project root = the nearest folder up that holds lumebook.json (the component registry)
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, "lumebook.json")) and ROOT != os.path.dirname(ROOT):
    ROOT = os.path.dirname(ROOT)
OUT = os.path.join(HERE, "out")
IL = timezone(timedelta(hours=3))  # Israel summer time; good enough for date stamps

# Shared facts (links, artifact URLs, dates, creator lists) live in shared/facts.json; component paths in lumebook.json.
REGISTRY = json.load(open(os.path.join(ROOT, "lumebook.json"), encoding="utf-8"))["components"]
FACTS = json.load(open(os.path.join(ROOT, "shared", "facts.json"), encoding="utf-8"))


def _src_file(component):
    return REGISTRY.get(component or "", {}).get("publish", {}).get("file")


ARTIFACTS = [{"key": a["key"], "label": a["label"], "url": a["url"], "file": _src_file(a.get("component")), "date": a["date"],
              "summary": a.get("summary", ""), "kind": a.get("kind", ""), "component": a.get("component")}
             for a in FACTS["artifacts"] if a["key"] != "dashboard"]
SITES = [{"key": x["key"], "label": x["label"], "url": x["url"],
          "dir": os.path.dirname(os.path.join(REGISTRY[x["component"]]["path"], x["page"])) if x.get("page") else None}
         for x in FACTS["sites"] if x["key"] != "dash"]
LINKS = {k: v for k, v in FACTS["links"].items() if k != "sheet_id"}
BARTER_BATCH = FACTS["creators"]["barter_batch"]
PAID_HOLD = FACTS["creators"]["paid_hold"]
KEY_DATES = FACTS["key_dates"]
BASELINES = FACTS["baselines"]
TEST_NAME = re.compile(FACTS["test_name_pattern"], re.I)  # the owner's own test submissions


def rel(p):
    return os.path.join(ROOT, p)


def mtime(p):
    try:
        return datetime.fromtimestamp(os.path.getmtime(rel(p)), IL).isoformat(timespec="minutes")
    except OSError:
        return None


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def fetch(url, ua="Mozilla/5.0 (Macintosh) LumebookDashboard/1.0", timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    t = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return r.status, round((time.time() - t) * 1000), body.decode("utf-8", "replace")


def parse_count(s):
    s = s.replace(",", "").strip()
    m = re.match(r"([\d.]+)\s*([KkMm]?)", s)
    if not m:
        return None
    n = float(m.group(1)) * {"": 1, "k": 1e3, "m": 1e6}[m.group(2).lower()]
    return int(round(n))


def ig_profile(handle):
    """Public follower/post counts from the og:description link-preview tag."""
    try:
        _, _, body = fetch(f"https://www.instagram.com/{handle}/", ua="facebookexternalhit/1.1")
    except Exception as e:
        return {"handle": handle, "error": str(e)[:80]}
    m = re.search(r'og:description" content="([^"]*)', body)
    if not m:
        return {"handle": handle, "error": "no og:description"}
    d = html.unescape(m.group(1))
    f = re.search(r"([\d.,]+[KkMm]?) Followers", d)
    p = re.search(r"([\d.,]+[KkMm]?) Posts", d)
    exact = bool(f and not re.search(r"[KkMm]$", f.group(1)))
    return {"handle": handle, "followers": parse_count(f.group(1)) if f else None,
            "followers_exact": exact, "posts": parse_count(p.group(1)) if p else None}


# ---------- sections ----------

def plan_section():
    src = open(rel("sites/lumebook-smm-plan/index.html"), encoding="utf-8").read()
    weeks = []
    for wm in re.finditer(r'<div class="when"><b>([^<]+)</b>.*?<ul class="tasks">(.*?)</ul>', src, re.S):
        tasks = [text_of(t) for t in re.findall(r"<span>(.*?)</span>", wm.group(2), re.S)]
        weeks.append({"name": wm.group(1).strip(), "tasks": [t for t in tasks if t]})
    targets = [{"n": text_of(n), "label": text_of(l)} for n, l in
               re.findall(r'<span class="n">(.*?)</span><span class="l">(.*?)</span>', src, re.S)]
    kpi_block = re.search(r'<section id="kpis">(.*?)</section>', src, re.S)
    kpis = []
    if kpi_block:
        for row in re.findall(r"<tr>(.*?)</tr>", kpi_block.group(1), re.S):
            cells = [text_of(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            if len(cells) == 4:
                kpis.append({"name": cells[0], "source": cells[1], "oct": cells[2], "dec": cells[3]})
    yossi = []
    ym = re.search(r"לוודא עם יוסי</h2>(.*?)</ul>", src, re.S)
    if ym:
        yossi = [text_of(li) for li in re.findall(r"<li>(.*?)</li>", ym.group(1), re.S)]
    roadmap = [{"dates": text_of(d), "name": text_of(h), "items": [text_of(i) for i in re.findall(r"<li>(.*?)</li>", ul, re.S)]}
               for d, h, ul in re.findall(r'<span class="d">(.*?)</span><h3>(.*?)</h3><ul>(.*?)</ul>', src, re.S)]
    last_commit = None
    try:
        last_commit = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%cI|%s", "--", "sites/lumebook-smm-plan"],
                                     capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        pass
    dirty = None
    try:
        dirty = bool(subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", "sites/lumebook-smm-plan"],
                                    capture_output=True, text=True, timeout=10).stdout.strip())
    except Exception:
        pass
    lc = last_commit.split("|", 1) if last_commit else [None, None]
    return {"weeks": weeks, "targets": targets, "kpis": kpis, "yossi": yossi, "roadmap": roadmap,
            "last_commit": {"at": lc[0], "msg": lc[1] if len(lc) > 1 else None}, "uncommitted": dirty,
            "modified": mtime("sites/lumebook-smm-plan/index.html")}


def ambassadors_section():
    hub = open(rel("sites/lumebook-ambassadors/creators/index.html"), encoding="utf-8").read()
    placeholders = []
    for m in re.finditer(r'<li>([^<]*)<span class="soon">([^<]*)</span>', hub):
        placeholders.append((m.group(1).strip() + " " + m.group(2).strip()).strip())
    for m in re.finditer(r'<p>([^<]*)<span class="soon">([^<]*)</span>', hub):
        placeholders.append((m.group(1).strip() + " " + m.group(2).strip()).strip())
    page = open(rel("sites/lumebook-ambassadors/index.html"), encoding="utf-8").read()
    demo = bool(re.search(r"DEMO\s*=\s*true", page))
    entry_ids = sorted(set(re.findall(r"entry\.(\d+)", page)))
    return {"placeholders": sorted(set(placeholders)), "demo_mode": demo, "entry_ids": len(entry_ids),
            "modified": max(filter(None, [mtime("sites/lumebook-ambassadors/index.html"),
                                          mtime("sites/lumebook-ambassadors/creators/index.html")]))}


def creators_section(network):
    rows = list(csv.DictReader(open(rel("creators/creator-research/creators-200-2026-10-03.csv"), encoding="utf-8-sig")))
    num = lambda v: int(float(v)) if v not in ("", None) else None
    tracked_handles = []
    for r in rows:
        h = r["handle"].lstrip("@")
        if r["shortlist"] == "yes" or h in BARTER_BATCH or h in PAID_HOLD:
            tracked_handles.append(h)
    by_handle = {r["handle"].lstrip("@"): r for r in rows}
    live = {}
    if network:
        for h in tracked_handles:
            live[h] = ig_profile(h)
            time.sleep(2)
    tracked = []
    for h in tracked_handles:
        r = by_handle[h]
        f0 = num(r["followers"])
        lv = live.get(h, {})
        tracked.append({
            "handle": h, "name": r["name"], "url": r["url"], "archetype": r["archetype"],
            "score": float(r["score"] or 0), "followers_at_research": f0,
            "followers_now": lv.get("followers"), "followers_exact": lv.get("followers_exact"),
            "live_error": lv.get("error"),
            "median_views": num(r["median_reel_views_last12"]), "last_reel": r["last_reel"],
            "contact": r["contact"], "conflict": r["brand_conflict"],
            "group": "barter" if h in BARTER_BATCH else "paid_hold" if h in PAID_HOLD else "shortlist",
            "concept": r["content_concept"],
        })
    tracked.sort(key=lambda x: -x["score"])
    followers = [num(r["followers"]) or 0 for r in rows]
    bands = Counter("1–5K" if f < 5000 else "5–10K" if f < 10000 else "10–25K" if f < 25000 else "25–50K" for f in followers)
    has_contact = sum(1 for r in rows if re.search(r"@|\b0\d|wa\.me|mailto|tel", r["contact"]))
    conflicts = [r["handle"] for r in rows if "COMPETITOR" in r["brand_conflict"].upper()]
    return {
        "total": len(rows), "shortlist": sum(r["shortlist"] == "yes" for r in rows),
        "by_pass": dict(Counter(r["research_pass"] for r in rows)),
        "archetypes": Counter(r["archetype"] for r in rows).most_common(8),
        "bands": [[b, bands.get(b, 0)] for b in ["1–5K", "5–10K", "10–25K", "25–50K"]],
        "competitor_conflicts": conflicts, "with_direct_contact_hint": has_contact,
        "tracked": tracked, "checked_on": rows[0]["checked_on"],
        "modified": mtime("creators/creator-research/creators-200-2026-10-03.csv"),
    }


def competitor_section():
    rows = json.load(open(rel("research/competitor-content-analysis/competitor_content_db.json"), encoding="utf-8"))
    def coded(r):
        c = r.get("coded")
        if isinstance(c, dict):
            return c
        try:
            return ast.literal_eval(c) if c else {}
        except Exception:
            return {}
    def as_list(v):
        if isinstance(v, list):
            return v
        return [v] if v else []
    cs = [coded(r) for r in rows]
    proof = Counter(p for c in cs for p in as_list(c.get("proof_mechanism")))
    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    outliers = sorted(
        [{"competitor": r["competitor_name"], "platform": r["platform"], "url": r["url"], "views": num(r.get("views")),
          "outlier": num(r.get("outlier_index")), "summary": (c.get("summary") or "")[:160], "date": r.get("date")}
         for r, c in zip(rows, cs) if num(r.get("outlier_index"))],
        key=lambda x: -(x["outlier"] or 0))[:6]
    by_comp = Counter(r["competitor_name"] for r in rows)
    return {
        "total": len(rows), "by_competitor": by_comp.most_common(),
        "by_source": dict(Counter(r["source"] for r in rows)),
        "pillars": Counter(c.get("pillar") for c in cs if c.get("pillar")).most_common(10),
        "funnel": Counter(c.get("funnel_stage") for c in cs if c.get("funnel_stage")).most_common(),
        "expert_endorsement": proof.get("expert_endorsement", 0),
        "photo_transform": proof.get("photo_to_character_transform", 0),
        "real_reaction": proof.get("real_child_reaction", 0),
        "outliers": outliers, "modified": mtime("research/competitor-content-analysis/competitor_content_db.json"),
    }


def sheet_section(path):
    """Parse the Drive connector's markdown table for the signup Sheet. No phones or emails kept."""
    if not path or not os.path.exists(path):
        return None
    raw = open(path, encoding="utf-8").read()
    try:
        raw = json.loads(raw).get("fileContent", raw)
    except Exception:
        pass
    block = raw.split("### Sheet Name: Form Responses 1", 1)[-1].split("### Table Columns", 1)[0]
    lines = [l for l in block.splitlines() if l.startswith("|")]
    rows = [[c.strip().replace("\\_", "_") for c in l.strip().strip("|").split("|")] for l in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-*:?", c) for c in r)]
    header = next((r for r in rows if "Timestamp" in r), None)
    if not header:
        return {"total": 0, "rows": []}
    data = rows[rows.index(header) + 1:]
    col = lambda name: next((i for i, h in enumerate(header) if name in h), None)
    i_ts, i_name, i_handle, i_band, i_ms = col("Timestamp"), col("שם"), col("אינסטגרם"), col("עוקבים"), col("מתקרב")
    out = []
    for r in data:
        g = lambda i: r[i] if i is not None and i < len(r) else ""
        out.append({"ts": g(i_ts), "name": g(i_name), "handle": g(i_handle), "band": g(i_band),
                    "milestone": g(i_ms), "test": bool(TEST_NAME.search(g(i_name) + " " + g(i_handle)))})
    real = [x for x in out if not x["test"]]
    return {"total": len(real), "tests": len(out) - len(real),
            "band_1k_plus": sum("ומעלה" in x["band"] for x in real),
            "band_under_1k": sum("פחות" in x["band"] for x in real),
            "rows": out[-25:], "header_has_old_columns": any(h in ("טיקטוק", "גילאי הילדים") for h in header)}


def sites_section(network):
    out = []
    for s in SITES:
        item = {k: s[k] for k in ("key", "label", "url")}
        item["modified"] = mtime(s["dir"]) if s["dir"] else None
        if s["dir"]:
            idx = os.path.join(s["dir"], "index.html")
            item["modified"] = mtime(idx) or item["modified"]
        if network:
            try:
                code, ms, body = fetch(s["url"])
                item.update(status=code, ms=ms)
            except Exception as e:
                item.update(status=getattr(e, "code", 0) or 0, error=str(e)[:80])
        out.append(item)
    return out


def carousel_section():
    """Nightly carousel pipeline: latest packs and approved production runs."""
    base = os.path.join(ROOT, REGISTRY["carousel-pipeline"]["path"])
    try:
        packs = json.load(open(os.path.join(base, "history.json"), encoding="utf-8")).get("packs", [])
    except (OSError, ValueError):
        packs = []
    approved_dir = os.path.join(base, "approved")
    approved = sorted(d for d in os.listdir(approved_dir) if not d.startswith(".")) if os.path.isdir(approved_dir) else []
    last = packs[-1] if packs else {}
    recent = [{"date": x.get("date"), "topic": x.get("topic"), "options": len(x.get("options", [])),
               "families": sorted(set(o.get("hook_family") for o in x.get("options", []) if o.get("hook_family")))}
              for x in packs[-10:]][::-1]
    return {"packs": len(packs), "last_date": last.get("date"), "last_topic": last.get("topic"), "recent": recent,
            "last_options": [{"id": o.get("id"), "title": o.get("title"), "hook_family": o.get("hook_family"),
                              "child_name": o.get("child_name"), "code_word": o.get("code_word")} for o in last.get("options", [])],
            "approved": approved, "modified": mtime(os.path.join(REGISTRY["carousel-pipeline"]["path"], "history.json"))}


def sync_section():
    """What changed, what it affects and what is waiting, from tools/lumebook.py (read-only status run)."""
    try:
        r = subprocess.run(["python3", os.path.join(ROOT, "tools", "lumebook.py"), "status", "--json"],
                           capture_output=True, text=True, timeout=120)
        st = json.loads(r.stdout)
    except Exception as e:
        return {"error": str(e)[:120]}
    return {"generated_at": st["generated_at"], "counts": st["counts"],
            "pending": [{"component": x["component"], "action": x["action"]} for x in st["pending"]],
            "warnings": [x["msg"] for x in st["checks"] if x["level"] in ("error", "warn")][:20],
            "components": [{"id": c["id"], "name": c["name"], "kind": c["kind"], "path": c["path"], "changed_at": c["changed_at"],
                            "behind": (c["publish"] or {}).get("behind"), "publish": (c["publish"] or {}).get("type"),
                            "url": (c["publish"] or {}).get("url"), "schedule": c.get("schedule"),
                            "feeds": REGISTRY.get(c["id"], {}).get("feeds", [])} for c in st["components"]]}


def files_section():
    skip = {".git", ".vercel", ".site-editor", "node_modules", "out", ".claude", ".agents", ".lumebook"}
    files = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in skip]
        for fn in fns:
            if fn.startswith("."):
                continue
            p = os.path.join(dp, fn)
            st = os.stat(p)
            files.append({"path": os.path.relpath(p, ROOT), "size": st.st_size,
                          "modified": datetime.fromtimestamp(st.st_mtime, IL).isoformat(timespec="minutes")})
    files.sort(key=lambda f: f["modified"], reverse=True)
    return {"count": len(files), "bytes": sum(f["size"] for f in files), "recent": files[:12]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet-md")
    ap.add_argument("--skip-network", action="store_true")
    a = ap.parse_args()
    net = not a.skip_network
    now = datetime.now(IL)
    social = {}
    if net:
        for h in ("lumebookai", "mebook.ai"):
            social[h] = ig_profile(h)
            time.sleep(2)
    snap = {
        "generated_at": now.isoformat(timespec="seconds"),
        "date": now.date().isoformat(),
        "social": social, "baselines": BASELINES,
        "plan": plan_section(), "ambassadors": ambassadors_section(),
        "signups": sheet_section(a.sheet_md),
        "creators": creators_section(net), "competitors": competitor_section(),
        "sites": sites_section(net), "files": files_section(),
        "carousel": carousel_section(), "sync": sync_section(),
        "artifacts": [dict(x, modified=mtime(x["file"]) if x["file"] else None) for x in ARTIFACTS],
        "links": LINKS, "key_dates": KEY_DATES,
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "snapshot.json"), "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    point = {"date": snap["date"], "at": snap["generated_at"],
             "ig_lumebookai": social.get("lumebookai", {}).get("followers"),
             "ig_mebook": social.get("mebook.ai", {}).get("followers"),
             "ig_lumebookai_posts": social.get("lumebookai", {}).get("posts"),
             "ig_mebook_posts": social.get("mebook.ai", {}).get("posts"),
             "signups": snap["signups"]["total"] if snap["signups"] else None,
             "creators_total": snap["creators"]["total"]}
    with open(os.path.join(OUT, "history.json"), "w", encoding="utf-8") as f:
        json.dump(point, f, ensure_ascii=False, indent=1)
    kb = os.path.getsize(os.path.join(OUT, "snapshot.json")) / 1024
    print(f"snapshot {kb:.0f} KB · {snap['date']} · IG {point['ig_lumebookai']} / MeBook {point['ig_mebook']} · signups {point['signups']}")


if __name__ == "__main__":
    main()
