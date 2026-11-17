#!/usr/bin/env python3
"""Reel views as Instagram itself shows them (15 Nov 2026), next to the Postiz numbers.

Why: a spot check on 15 Nov 2026 found Postiz matching Instagram on five recent reels, 93 to 111 views short on two older ones,
and missing two reels that were not sent through Postiz (one of them the best, 1,078 views). So the nightly Postiz read is not
enough for views. This keeps Instagram's own count per reel, one row per day.

    python3 ig_views.py ingest <file.json>   save what ig_views.js returned (the whole result or just its "reels" object)
    python3 ig_views.py show                 Instagram next to Postiz, one line per reel

Writes data/instagram-views.json (internal figures, local only). Reels only: the grid prints views on reels; there is no
number on a carousel tile. Counts like 12.3K are rounded by Instagram; they are saved as approximate. A reel that is not on
the grid this time keeps its old numbers (never a 0 for "not seen"). Fewer than 3 reels read means the page did not load:
nothing is written. Instagram is read by the scheduled task lumebook-creator-cards-daily, part C (browser, read only)."""
import datetime as dt, json, os, re, sys
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
OUT = Path(os.environ.get("LUMEBOOK_IG_VIEWS") or DATA / "instagram-views.json")
POSTIZ = Path(os.environ.get("LUMEBOOK_POSTIZ_RESULTS") or DATA / "postiz-results.json")
IL = ZoneInfo("Asia/Jerusalem")
HANDLE = "lumebook.il"


def count(text):
    """'1,078' -> (1078, False); '12.3K' -> (12300, True)."""
    t = str(text).strip().replace(",", "")
    m = re.fullmatch(r"([\d.]+)\s*([KkMm]?)", t)
    if not m:
        return None
    n = float(m.group(1)) * {"": 1, "k": 1e3, "m": 1e6}[m.group(2).lower()]
    return int(round(n)), bool(m.group(2))


def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def ingest(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    reels = raw.get("reels", raw) if isinstance(raw, dict) else {}
    if isinstance(raw, dict) and raw.get("stop"):
        sys.exit(f"ig_views: stop: {raw['stop']}")
    got = {c: count(v) for c, v in reels.items()}
    got = {c: v for c, v in got.items() if v}
    if len(got) < 3:
        sys.exit(f"ig_views: only {len(got)} reels read, the grid did not load; nothing written")
    today = dt.datetime.now(IL).date().isoformat()
    data = load(OUT)
    posts = data.get("posts") or {}
    for code, (views, approx) in got.items():
        row = posts.setdefault(code, {"first_seen": today})
        row.update({"url": f"https://www.instagram.com/reel/{code}/", "views": views, "approx": approx, "as_of": today})
        row.setdefault("daily", {})[today] = views
    data = {"about": "Reel views as Instagram's own profile grid prints them, one row per day. Written by src/ig_views.py "
                     "(scheduled task lumebook-creator-cards-daily, part C); internal figures, local only.",
            "account": HANDLE, "updated": dt.datetime.now(IL).isoformat(timespec="minutes"),
            "last_run": {"read": len(got)}, "posts": posts}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(OUT)
    print(f"instagram views {today}: {len(got)} reels read; {len(posts)} reels on file")


def show():
    ig = (load(OUT).get("posts")) or {}
    pz = {}
    for pid, v in ((load(POSTIZ).get("posts")) or {}).items():
        m = re.search(r"/(?:reel|reels|p)/([\w-]+)", v.get("url") or "")
        if m and v.get("channel") == "instagram":
            pz[m.group(1)] = v
    print(f"{'reel':14} {'posted':10} {'Instagram':>10} {'Postiz':>8} {'gap':>6}")
    both = sorted((c for c in pz), key=lambda c: pz[c].get("published") or "", reverse=True)
    for code in both + sorted(c for c in ig if c not in pz):
        a = ig.get(code, {}).get("views")
        b = (pz.get(code, {}).get("latest") or {}).get("views")
        posted = (pz.get(code, {}).get("published") or "")[:10] or "not Postiz"
        gap = "" if a is None or b is None else a - b
        print(f"{code:14} {posted:10} {a if a is not None else '-':>10} {b if b is not None else '-':>8} {gap:>6}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "ingest":
        ingest(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "show":
        show()
    else:
        sys.exit(__doc__)
