#!/usr/bin/env python3
"""Build the Lumebook dashboard snapshot.

Reads everything local to the project folder (SMM plan site, creator CSV,
competitor DB, ambassadors pages, file inventory), checks the live sites and
public Instagram follower counts, and optionally parses the signup Sheet
(the Google Drive connector's text export, saved to a file by the caller).

Usage:
  python3 dashboard/refresh.py [--sheet-md PATH] [--skip-network]

Writes dashboard/out/snapshot.json and dashboard/out/history.json.
Only standard library; safe to run any time.
"""
import argparse, ast, csv, html, json, os, re, subprocess, time, urllib.request
from collections import Counter
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dashboard", "out")
IL = timezone(timedelta(hours=3))  # Israel summer time; good enough for date stamps

# Things only memory/conversation knows. Update here when they change.
ARTIFACTS = [
    {"key": "strategy", "label": "פלייבוק סושיאל Q4", "url": "https://claude.ai/artifact/BALURpPXY8psXxCNvb6jH6", "file": "lumebook-social-strategy.html", "date": "2026-10-01"},
    {"key": "reels", "label": "35 סרטונים שעבדו (ליוסי)", "url": "https://claude.ai/artifact/UstDM1kr9jBpqfMPS2gZxP", "file": None, "date": "2026-10-02"},
    {"key": "creators", "label": "מפת יוצרים · 204", "url": "https://claude.ai/artifact/MPuqcaCXXF5CGQiDMaDpbB", "file": "creator-research/lumebook-creator-map.html", "date": "2026-10-03"},
    {"key": "teardown", "label": "ניתוח תוכן מתחרים · 147", "url": "https://claude.ai/artifact/2aQamEfoJhb1Cix9CgZ1rY", "file": "competitor-content-analysis/competitor_content_db.json", "date": "2026-10-03"},
]
SITES = [
    {"key": "smm", "label": "תוכנית סושיאל", "url": "https://lumebook-smm-plan.vercel.app", "dir": "lumebook-smm-plan"},
    {"key": "amb", "label": "דף שגרירים", "url": "https://lumebook-ambassadors.vercel.app", "dir": "lumebook-ambassadors"},
    {"key": "hub", "label": "מרכז היוצרים", "url": "https://lumebook-ambassadors.vercel.app/creators/", "dir": "lumebook-ambassadors/creators"},
    {"key": "store", "label": "lumebook.com", "url": "https://lumebook.com/IL/he", "dir": None},
]
LINKS = {
    "form": "https://docs.google.com/forms/d/e/1FAIpQLSculYe4LpG8WUFNDXCVDiP-BPaSbuqx0h7_dGcyU0owmxIxAg/viewform",
    "sheet": "https://docs.google.com/spreadsheets/d/1ARYFCX1tfIR69GhGn-p92qOodGeENasGu9fI_TskHkI/edit",
    "drive": "https://drive.google.com/drive/folders/1awITcQFWfsQqpbL8Lupikw12b6y4EWvB",
    "tracker": "https://docs.google.com/spreadsheets/d/1JU9y80sIQvzQ_Xt8lgKiJSb6MbKrbglKLMgap-3JNMk",
    "repo": "https://github.com/yarinbruner/lumebook-smm-plan",
}
BARTER_BATCH = ["knafaim.ot_by_noy", "eden_spaiev", "yeladim_ktanim", "etti_haft", "ima.shir", "rotem__unger",
                "daria_mansour1", "hadas.shvat", "saba.chiche", "bar.levi.adiel", "nataliegaash", "books_are_friends_slp"]
PAID_HOLD = ["lital_magnezi", "ganotmor", "almaanddad"]
KEY_DATES = [
    {"date": "2026-10-31", "label": "אנליטיקה ראשונית + יעדים חדשים"},
    {"date": "2026-11-10", "label": "ספרי יוצרים לחנוכה"},
    {"date": "2026-11-22", "label": "דדליין הזמנות לחנוכה", "unconfirmed": True},
    {"date": "2026-12-04", "label": "חנוכה מתחיל"},
    {"date": "2026-12-12", "label": "סוף חנוכה"},
    {"date": "2026-12-31", "label": "סקירה רבעונית"},
]
BASELINES = {"lumebook_reels_median": {"value": 48, "date": "2026-10-02"},
             "mebook_reels_median": {"value": 4000, "date": "2026-10-02"},
             "mebook_collab_peak": {"value": 86500, "date": "2026-10-02"}}
TEST_NAME = re.compile(r"בדיקה|test|Yarin Bruner", re.I)  # the owner's own test submissions


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
    src = open(rel("lumebook-smm-plan/index.html"), encoding="utf-8").read()
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
        last_commit = subprocess.run(["git", "-C", rel("lumebook-smm-plan"), "log", "-1", "--format=%cI|%s"],
                                     capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        pass
    dirty = None
    try:
        dirty = bool(subprocess.run(["git", "-C", rel("lumebook-smm-plan"), "status", "--porcelain"],
                                    capture_output=True, text=True, timeout=10).stdout.strip())
    except Exception:
        pass
    lc = last_commit.split("|", 1) if last_commit else [None, None]
    return {"weeks": weeks, "targets": targets, "kpis": kpis, "yossi": yossi, "roadmap": roadmap,
            "last_commit": {"at": lc[0], "msg": lc[1] if len(lc) > 1 else None}, "uncommitted": dirty,
            "modified": mtime("lumebook-smm-plan/index.html")}


def ambassadors_section():
    hub = open(rel("lumebook-ambassadors/creators/index.html"), encoding="utf-8").read()
    placeholders = []
    for m in re.finditer(r'<li>([^<]*)<span class="soon">([^<]*)</span>', hub):
        placeholders.append((m.group(1).strip() + " " + m.group(2).strip()).strip())
    for m in re.finditer(r'<p>([^<]*)<span class="soon">([^<]*)</span>', hub):
        placeholders.append((m.group(1).strip() + " " + m.group(2).strip()).strip())
    page = open(rel("lumebook-ambassadors/index.html"), encoding="utf-8").read()
    demo = bool(re.search(r"DEMO\s*=\s*true", page))
    entry_ids = sorted(set(re.findall(r"entry\.(\d+)", page)))
    return {"placeholders": sorted(set(placeholders)), "demo_mode": demo, "entry_ids": len(entry_ids),
            "modified": max(filter(None, [mtime("lumebook-ambassadors/index.html"),
                                          mtime("lumebook-ambassadors/creators/index.html")]))}


def creators_section(network):
    rows = list(csv.DictReader(open(rel("creator-research/creators-200-2026-10-03.csv"), encoding="utf-8-sig")))
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
        "modified": mtime("creator-research/creators-200-2026-10-03.csv"),
    }


def competitor_section():
    rows = json.load(open(rel("competitor-content-analysis/competitor_content_db.json"), encoding="utf-8"))
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
        "outliers": outliers, "modified": mtime("competitor-content-analysis/competitor_content_db.json"),
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


def files_section():
    skip = {".git", ".vercel", ".site-editor", "node_modules", "out", ".claude"}
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
