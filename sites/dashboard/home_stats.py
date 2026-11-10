#!/usr/bin/env python3
"""HQ's home: the live numbers and what needs attention (Yarin, 08 Nov 2026).

Yarin: "the main home page should be live stats from the carousel machine, creator map, reel calendar, performance of
lumebook ig and fb pages, require attention and quick access to most used tools", "i need it updated daily".

collect() returns one JSON-able dict with these parts, each None when its source is missing:
  carousels   Carousel Machine's own state (GET 127.0.0.1:8777/api/state, the login item), else productions.json and
              grades.json; plus the Postiz queue from social.json (what is scheduled, what failed)
  creators    the creator map's saved data (creators/creator-research/state/), the same rules the map uses for
              follow-ups (4 days after the first message), reminders (nad + nat) and a quiet month in process
  ambassadors the store's ambassador Sheet (shared/facts.json links.sheet_id), from its Drive export in
              out/ambassadors-sheet.md; never phones or emails
  reels       the November reel calendar (reels.json) and the finished videos in each reel's media folder
  social      out/social.json: Instagram and Facebook from Postiz analytics (refresh_social(), slow, once a day)
              plus the public Instagram follower count from the last snapshot
  most_used   the pages Yarin opened most in the last 30 days (the project server counts page opens in
              .lumebook/page-views.json)
  attention   the list on top of the home: crit, warn, info, each with a tag, a text and where to go

Who calls it: the project server (GET /api/home, live, no network beyond this Mac), refresh.py (every night at 00:00
through tools/nightly_commit.py, into snapshot.json for the Vercel copy and the artifact) and the daily scheduled task
lumebook-hq-daily (exports the Sheet, refreshes, pushes the snapshot into the artifact database).

  python3 sites/dashboard/home_stats.py            print collect() as JSON
  python3 sites/dashboard/home_stats.py social     refresh out/social.json from Postiz (4 CLI calls, about 2 minutes)
  python3 sites/dashboard/home_stats.py sheet RAW  save the Drive export of the ambassador Sheet (RAW, a file outside the
                                                   project) to out/ambassadors-sheet.md without phones, emails or payment numbers
Standard library only.
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, "lumebook.json")) and ROOT != os.path.dirname(ROOT):
    ROOT = os.path.dirname(ROOT)
OUT = os.path.join(HERE, "out")
SOCIAL = os.path.join(OUT, "social.json")
SHEET_EXPORT = os.path.join(OUT, "ambassadors-sheet.md")
VIEWS = os.path.join(ROOT, ".lumebook", "page-views.json")
STATE = os.path.join(ROOT, "creators", "creator-research", "state")
REELS = os.path.join(ROOT, "research", "israeli-product-reels", "src", "scripts", "series-2026-11", "reels.json")
CM = os.path.join(ROOT, "carousel", "carousel-pipeline")
CM_API = os.environ.get("LUMEBOOK_CM_API", "http://127.0.0.1:8777/api/state")
DAY = 86400


def p(*parts):
    return os.path.join(ROOT, *parts)


def read(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def now():
    return dt.datetime.now().astimezone()


def facts():
    return read(p("shared", "facts.json"), {})


def iso_day(d=None):
    return (d or now()).date().isoformat()


def ms_of_day(s):
    try:
        return dt.datetime.fromisoformat(s[:10]).timestamp() * 1000
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- Carousel Machine

RUNNING = {"queued", "preparing", "generating", "composing", "exporting"}
WAITING = {"review", "approval", "budget", "awaiting_approval", "waiting"}


def carousels():
    st = None
    try:
        with urllib.request.urlopen(CM_API, timeout=12) as r:
            st = json.load(r)
    except Exception:
        st = None
    runs_all = (read(os.path.join(CM, "productions.json"), {}) or {}).get("runs", {})
    out = {"live": st is not None, "produced_total": sum(1 for r in runs_all.values() if r.get("status") == "done"),
           "spent_usd": round(sum(float(r.get("spent_usd") or 0) for r in runs_all.values()), 2)}
    if st and st.get("batch"):
        items, grades = st.get("items", []), st.get("grades", {})
        keys = [i["key"] for i in items]
        g = [grades.get(k) or {} for k in keys]
        out.update(batch=st["batch"], range_he=st.get("week_he"), total=len(items),
                   graded=sum(1 for x in g if x.get("score")), picked=sum(1 for x in g if x.get("produce")),
                   days=len({i.get("date") for i in items}), next_run_he=st.get("next_run_he"))
    else:
        out.update(batch=None, total=None, graded=None, picked=None)
    # productions of every batch: the ones moving, waiting for Yarin and failed
    out["running"] = sum(1 for r in runs_all.values() if r.get("status") in RUNNING)
    out["waiting"] = sorted([r.get("key") for r in runs_all.values() if r.get("status") in WAITING or "אישור" in (r.get("status_he") or "")])
    out["failed"] = sorted([r.get("key") for r in runs_all.values() if r.get("status") == "failed"])
    return out


# ---------------------------------------------------------------- creator map

LEGS = {"replied": "process", "yes": "process", "code": "process", "due": "sent", "posted": "process", "book": "process", "content": "process"}
FU1, FU2, STALE = 4 * DAY * 1000, 7 * DAY * 1000, 30 * DAY * 1000


def _fu_due(o, raw, t):
    """Whether the creator map puts this creator in its Follow-ups tab: the first follow-up 4 days after the first message,
    an optional last one (fu2w) 7 days after the first follow-up, a skipped follow-up (fusk) never; same order as seq()."""
    sent = o.get("sat") or ms_of_day(o.get("on") or "")
    f1 = o.get("fuat") or ms_of_day(o.get("fu") or "")
    f2 = o.get("fu2at") or ms_of_day(o.get("fu2") or "")
    if f2 is not None:
        return False
    if f1 is not None:
        if not o.get("fu2w"):
            return False
        d = (o.get("dat") or f1 + FU2) if raw == "due" else f1 + FU2
        return t >= d
    if o.get("fusk"):
        return False
    if raw == "due":
        return True
    return sent is not None and t >= sent + FU1


def creators():
    od = read(os.path.join(STATE, "outreach.json"))
    if od is None:
        return None
    total = len(read(p("creators", "creator-research", "src", "C_all.json"), []) or []) or None
    t = time.time() * 1000
    stats = {"sent": 0, "process": 0, "retry": 0, "future": 0, "declined": 0, "books_out": 0, "content": 0,
             "followups_due": 0, "reminders_due": 0}
    due_names, rem_names = [], []
    for h, o in od.items():
        if not isinstance(o, dict):
            continue
        raw = o.get("s") or "new"
        st = LEGS.get(raw, raw)
        stg = o.get("stg") or ""
        stage = "booksent" if raw == "book" else "content" if raw in ("content", "posted") else stg
        late = stage in ("booksent", "content", "pending", "recv")
        content = stage in ("content", "recv")
        nad = ms_of_day(o.get("nad") or "")
        rem_at = None
        if nad is not None and not content:
            m = re.match(r"^(\d{1,2}):(\d{2})$", o.get("nat") or "")
            rem_at = nad + ((int(m.group(1)) * 60 + int(m.group(2))) * 60000 if m else 8 * 3600000)
        if st == "process" and not late:
            since = o.get("sct") or o.get("rat") or o.get("at")
            if since and t - max(since, rem_at or 0) >= STALE:
                st = "declined"
        if st in stats:
            stats[st] += 1
        if st == "process" and late:
            stats["books_out"] += 1
        if st == "process" and content:
            stats["content"] += 1
        if raw in ("sent", "due") and _fu_due(o, raw, t):   # the map's Follow-ups tab (template.html seq and bkOf)
            stats["followups_due"] += 1
            due_names.append(h)
        if rem_at is not None and rem_at <= t:
            stats["reminders_due"] += 1
            rem_names.append(h)
    contacted = sum(stats[k] for k in ("sent", "process", "retry", "future", "declined"))
    posts = (read(os.path.join(STATE, "posts.json"), {}) or {}).get("posts", {}) or {}
    views = sum(int(x.get("v") or 0) for x in posts.values()) if isinstance(posts, dict) else 0
    return dict(stats, total=total, contacted=contacted, new=(total - contacted) if total else None,
                reply_rate=round(100 * stats["process"] / contacted) if contacted else None,
                posts=len(posts), post_views=views, followups_who=due_names[:12], reminders_who=rem_names[:12])


# ---------------------------------------------------------------- ambassadors (the store's Sheet)

def _md_tables(raw):
    """{sheet name: rows} from the Drive connector's text export of a spreadsheet."""
    try:
        raw = json.loads(raw).get("fileContent", raw)
    except (ValueError, AttributeError):
        pass
    out = {}
    for part in raw.split("### Sheet Name:")[1:]:
        name, _, rest = part.partition("\n")
        block = rest.split("### Table Columns", 1)[0]
        rows = [[c.strip().replace("\\_", "_") for c in l.strip().strip("|").split("|")] for l in block.splitlines() if l.strip().startswith("|")]
        out[name.strip()] = [r for r in rows if not all(re.fullmatch(r":?-*:?", c) for c in r)]
    return out


def _num(v):
    try:
        return float(str(v).replace(",", "").replace("₪", "").strip() or 0)
    except ValueError:
        return 0.0


def ambassadors(path=SHEET_EXPORT):
    if not path or not os.path.exists(path):
        return None
    tabs = _md_tables(open(path, encoding="utf-8").read())
    test = re.compile(facts().get("test_name_pattern") or r"$^", re.I)
    rows = tabs.get("שגרירים") or []
    hi = next((i for i, r in enumerate(rows) if "הצטרפות" in r), None)
    people = []
    if hi is not None:
        H = rows[hi]
        col = lambda name: next((i for i, h in enumerate(H) if name in h), None)
        ix = {k: col(v) for k, v in {"joined": "הצטרפות", "name": "שם", "handle": "אינסטגרם", "band": "עוקבים", "status": "סטטוס",
                                       "link": "לינק", "discount": "הנחה", "reward": "תגמול לספר", "books": "ספרים שנקנו",
                                       "pending": "ממתינים", "final": "סופיים", "redeemed": "מומש", "balance": "יתרה",
                                       "expired": "נמחקו", "program": "תוכנית"}.items()}
        for r in rows[hi + 1:]:
            g = lambda k: r[ix[k]] if ix[k] is not None and ix[k] < len(r) else ""
            if not g("joined") and not g("name"):
                continue
            people.append({"joined": g("joined"), "name": g("name"), "handle": g("handle").lstrip("@"), "band": g("band"),
                           "status": g("status"), "slug": g("link").rstrip("/").rsplit("/", 1)[-1] if g("link") else "",
                           "discount": _num(g("discount")), "reward": _num(g("reward")), "books": int(_num(g("books"))),
                           "pending": _num(g("pending")), "final": _num(g("final")), "balance": _num(g("balance")),
                           "program": g("program"), "test": bool(test.search(g("name")) or test.search(g("handle")))})
    real = [x for x in people if not x["test"]]
    sales = (tabs.get("מכירות") or [])[1:]
    sale_state = {}
    for r in sales:
        if any(c for c in r):
            s = r[7] if len(r) > 7 else ""
            sale_state[s or "לא ידוע"] = sale_state.get(s or "לא ידוע", 0) + 1
    payouts = []
    prow = tabs.get("לתשלום") or []
    if prow:
        H = prow[0]
        ci = lambda name: next((i for i, h in enumerate(H) if name in h), None)
        i_req, i_due, i_who, i_kind, i_state, i_amount = ci("תאריך הבקשה"), ci("לטפל עד"), ci("שגריר"), ci("מימוש"), ci("מצב"), ci("ירד מהיתרה")
        for r in prow[1:]:
            g = lambda i: r[i] if i is not None and i < len(r) else ""
            if not any(c for c in r):
                continue
            state = g(i_state)
            if re.search(r"שולם|בוצע|נדחה|בוטל", state):
                continue
            payouts.append({"requested": g(i_req), "due": g(i_due), "who": g(i_who), "kind": g(i_kind), "state": state, "amount": _num(g(i_amount))})
    updated = None
    for r in tabs.get("הסבר") or []:
        if r and r[0].startswith("עודכן") and len(r) > 1:
            updated = r[1]
    week_ago = (now() - dt.timedelta(days=7)).strftime("%Y-%m-%d")
    return {"total": len(real), "tests": len(people) - len(real), "active": sum(1 for x in real if x["status"] == "פעיל"),
            "new_week": sum(1 for x in real if x["joined"][:10] >= week_ago),
            "books": sum(x["books"] for x in real), "rewards_pending": sum(x["pending"] for x in real),
            "rewards_final": sum(x["final"] for x in real), "balance": sum(x["balance"] for x in real),
            "sales": sum(sale_state.values()), "sales_by_state": sale_state, "payouts_open": payouts,
            "bands": {b: sum(1 for x in real if x["band"] == b) for b in sorted({x["band"] or "לא צוין" for x in real})},
            "rows": [{k: v for k, v in x.items() if k not in ("pending", "final", "balance")} for x in people],
            "sheet_updated": updated, "exported_at": dt.datetime.fromtimestamp(os.path.getmtime(path)).astimezone().isoformat(timespec="minutes")}


PRIVATE_COLUMNS = ("טלפון", "מייל", "מספר להעברה", "קבלה או חשבונית")


def save_sheet_export(raw_path, out_path=SHEET_EXPORT):
    """The daily task's step: the Drive connector's export of the ambassador Sheet, written to out_path without the columns
    that hold phones, emails, payment numbers or documents (PRIVATE_COLUMNS). The raw file is the caller's to delete."""
    raw = open(raw_path, encoding="utf-8").read()
    try:
        raw = json.loads(raw).get("fileContent", raw)
    except (ValueError, AttributeError):
        pass
    out, drop = [], None
    for line in raw.splitlines():
        if line.startswith("### Sheet Name:"):
            drop = None
        if line.strip().startswith("|"):
            cells = line.strip().strip("|").split("|")
            if drop is None and any(any(k in c for k in PRIVATE_COLUMNS) for c in cells):
                drop = {i for i, c in enumerate(cells) if any(k in c for k in PRIVATE_COLUMNS)}
            if drop:
                cells = [c for i, c in enumerate(cells) if i not in drop]
            line = "|" + "|".join(cells) + "|"
        elif line.strip().startswith("- range:") or line.strip().startswith("- sample data:"):
            continue   # the column samples repeat every value, phones included
        out.append(line)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    return out_path


# ---------------------------------------------------------------- reel calendar

REEL_STATUS = {"posted": "פורסם", "ready": "מוכן לפרסום", "needs-edit": "מחכה לעריכה", "needs-voice": "מחכה לקריינות ולצילום שלך",
               "needs-footage": "מחכה לחומר", "blocked": "חסום", "spare": "ספייר"}


def reels():
    d = read(REELS)
    if not d:
        return None
    today = iso_day()
    month = today[:7]
    # two options a day since 10 Nov 2026 (reels.json "option" 1 and 2, "picks" {date: id}): the numbers count days, each
    # day standing for its posted reel, else its picked one, else option 1; a day with no pick yet shows both options
    picks = d.get("picks") or {}
    days = {}
    for r in sorted((r for r in d.get("reels", []) if r.get("date")), key=lambda r: r.get("option") or 1):
        days.setdefault(r["date"], []).append(r)

    def stands(rs):
        return (next((r for r in rs if r.get("status") == "posted"), None)
                or next((r for r in rs if r["id"] == picks.get(rs[0]["date"])), None) or rs[0])
    dated = [stands(rs) for _, rs in sorted(days.items())]
    mine = [r for r in dated if r["date"][:7] == month] or dated

    def made(r):
        proj = r.get("project")
        return bool(proj and glob.glob(p(proj, "final", "*.mp4")))
    by = {}
    for r in mine:
        by[r.get("status") or "?"] = by.get(r.get("status") or "?", 0) + 1
    upcoming = [r for r in dated if r["date"] >= today]

    def brief(r):
        rs = days[r["date"]]
        if len(rs) > 1 and r.get("status") != "posted" and not picks.get(r["date"]):   # nothing picked: both options, one row
            return {"id": " / ".join(x["id"] for x in rs), "date": r["date"], "status": "choose", "status_he": "לבחור אפשרות",
                    "hook": " / ".join((x.get("hook") or "").replace("\n", " ") for x in rs), "made": any(made(x) for x in rs)}
        return {"id": r["id"], "date": r["date"], "status": r.get("status"), "status_he": REEL_STATUS.get(r.get("status"), r.get("status")),
                "hook": (r.get("hook") or "").replace("\n", " "), "made": made(r)}
    shoots = [s for s in d.get("shoots", []) if s.get("date") == today]
    return {"month": month, "total": len(mine), "by_status": by, "posted": by.get("posted", 0),
            "made": sum(1 for r in mine if made(r)), "waiting_on_yarin": by.get("needs-voice", 0) + by.get("needs-footage", 0),
            "today": [brief(r) for r in upcoming if r["date"] == today], "next": [brief(r) for r in upcoming if r["date"] > today][:3],
            "shoot_today": [s.get("note", "") for s in shoots], "post_time": (d.get("defaults") or {}).get("post_time")}


# ---------------------------------------------------------------- Instagram and Facebook (Postiz)

def _postiz(args, timeout=150):
    r = subprocess.run(["postiz", *args], capture_output=True, text=True, timeout=timeout,
                       env=dict(os.environ, PATH=os.environ.get("PATH", "") + ":" + os.path.expanduser("~/.local/bin")))
    text = r.stdout
    starts = [i for i in (text.find("["), text.find("{")) if i >= 0]
    if not starts:
        raise RuntimeError((r.stderr or text or "no output").strip()[:160])
    return json.loads(text[min(starts):])


def _metrics(rows):
    out = {}
    for m in rows or []:
        data = [[x.get("date"), x.get("total")] for x in m.get("data", []) if x.get("date")]
        out[m.get("label")] = {"total": sum(v or 0 for _, v in data), "series": data}
    return out


def refresh_social():
    """Postiz analytics for both channels, the last 7 days and the 7 before (the CLI only gives totals for a window, so
    the second window is 14 days minus the first), and the post queue. Writes out/social.json; keeps the old file on failure."""
    f = facts().get("postiz") or {}
    chans = {"ig": f.get("instagram"), "fb": f.get("facebook")}
    res, errs = {}, {}

    def run(key, args):
        try:
            res[key] = _postiz(args)
        except Exception as e:  # one failing call never blocks the others
            errs[key] = str(e)[:160]
    t = dt.datetime.now(dt.timezone.utc)
    jobs = [(f"{c}{d}", ["analytics:platform", cid, "-d", str(d)]) for c, cid in chans.items() if cid for d in (7, 14)]
    jobs.append(("posts", ["posts:list", "--startDate", (t - dt.timedelta(days=14)).strftime("%Y-%m-%dT00:00:00Z"),
                           "--endDate", (t + dt.timedelta(days=21)).strftime("%Y-%m-%dT23:59:59Z")]))
    threads = [threading.Thread(target=run, args=j) for j in jobs]
    [th.start() for th in threads]
    [th.join() for th in threads]
    out = {"at": now().isoformat(timespec="minutes"), "errors": errs}
    for c in chans:
        a, b = _metrics(res.get(f"{c}7")), _metrics(res.get(f"{c}14"))
        out[c] = {k: {"week": v["total"], "prev": (b.get(k, {}).get("total", 0) - v["total"]) if k in b else None,
                      "series": b.get(k, v)["series"]} for k, v in a.items()} if a else None
    posts = (res.get("posts") or {}).get("posts") if isinstance(res.get("posts"), dict) else res.get("posts")
    if posts is not None:
        rows = []
        for x in posts:
            prov = (x.get("integration") or {}).get("providerIdentifier") or ""
            rows.append({"when": x.get("publishDate"), "status": x.get("status") or x.get("state"), "channel": prov,
                         "url": x.get("releaseURL") or "", "first_line": (x.get("content") or "").strip().split("\n", 1)[0][:80]})
        out["posts"] = sorted(rows, key=lambda r: r["when"] or "")
    old = read(SOCIAL, {}) or {}
    for k in ("ig", "fb", "posts"):   # a channel that failed today keeps yesterday's numbers, marked by its date
        if out.get(k) is None and old.get(k) is not None:
            out[k] = old[k]
            out.setdefault("stale", []).append(k)
    os.makedirs(OUT, exist_ok=True)
    with open(SOCIAL, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def social():
    s = read(SOCIAL)
    snap = read(os.path.join(OUT, "snapshot.json"), {}) or {}
    h = snap.get("ig_handle")
    prof = (snap.get("social") or {}).get(h) or {}
    if not s and not prof:
        return None
    s = dict(s or {})
    s["ig_followers"] = prof.get("followers")
    s["ig_posts"] = prof.get("posts")
    s["ig_handle"] = h
    hist = read(os.path.join(OUT, "follower-history.json"), []) or []
    s["followers_series"] = [[x["date"], x["ig"]] for x in hist if x.get("ig") is not None][-30:]
    return s


def note_followers(snap):
    """Called by refresh.py: one point a day of the public follower count, for the home's trend line (30 days kept)."""
    h = snap.get("ig_handle")
    n = ((snap.get("social") or {}).get(h) or {}).get("followers")
    path = os.path.join(OUT, "follower-history.json")
    hist = [x for x in (read(path, []) or []) if x.get("date") != snap.get("date")]
    if n is not None:
        hist.append({"date": snap.get("date"), "ig": n})
    hist = sorted(hist, key=lambda x: x["date"])[-120:]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(hist, fh, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- most used pages

def most_used(days=30, n=8):
    v = read(VIEWS, {}) or {}
    cut = (now() - dt.timedelta(days=days)).date().isoformat()
    tally = {}
    for day, pages in (v.get("days") or {}).items():
        if day >= cut:
            for page, c in pages.items():
                tally[page] = tally.get(page, 0) + c
    return [{"local": k, "opens": c} for k, c in sorted(tally.items(), key=lambda kv: -kv[1])[:n]]


# ---------------------------------------------------------------- what needs attention

def attention(c, cr, am, rl, so):
    out = []
    add = lambda sev, tag, text, local=None, view=None: out.append({k: v for k, v in
                                                                   {"sev": sev, "tag": tag, "text": text, "local": local, "view": view}.items() if v})
    today = iso_day()
    if c:
        if c.get("failed"):
            add("crit", "קרוסלות", f"{len(c['failed'])} הפקות נכשלו: {', '.join(c['failed'][:3])}", "hook-studio/")
        if c.get("waiting"):
            add("warn", "קרוסלות", f"{len(c['waiting'])} קרוסלות מחכות לאישור שלך", "hook-studio/")
        if c.get("total") and c.get("graded") is not None and c["graded"] < c["total"]:
            add("info", "קרוסלות", f"{c['total'] - c['graded']} מתוך {c['total']} הקרוסלות של {c.get('range_he') or 'החבילה'} עוד לא דורגו", "hook-studio/")
        if not c.get("live"):
            add("warn", "קרוסלות", "מכונת הקרוסלות לא ענתה (פריט ההתחברות על 8777)", "hook-studio/")
    posts = (so or {}).get("posts") or []
    failed = [x for x in posts if (x.get("status") or "").upper() == "ERROR" and (x.get("when") or "")[:10] >= (now() - dt.timedelta(days=14)).date().isoformat()]
    for x in failed[:3]:
        ch = "אינסטגרם" if x.get("channel") == "instagram" else "פייסבוק" if x.get("channel") == "facebook" else x.get("channel")
        add("crit", "Postiz", f"פוסט ב{ch} לא עלה ({(x.get('when') or '')[:10]}): {x.get('first_line') or ''}")
    if posts:
        soon = [x for x in posts if (x.get("status") or "").upper() == "QUEUE" and today <= (x.get("when") or "")[:10] <= (now() + dt.timedelta(days=3)).date().isoformat()]
        if not soon:
            add("warn", "Postiz", "אין פוסט מתוזמן ל-3 הימים הקרובים")
    if cr:
        if cr.get("reminders_due"):
            add("warn", "יוצרים", f"{cr['reminders_due']} תזכורות ליוצרים הגיעו לזמנן", "creators/creator-research/lumebook-creator-map.html")
        if cr.get("followups_due"):
            add("warn", "יוצרים", f"{cr['followups_due']} יוצרים מחכים לפולואפ", "creators/creator-research/lumebook-creator-map.html")
    if am:
        for x in am.get("payouts_open", [])[:5]:
            add("crit", "שגרירים", f"בקשת {x.get('kind') or 'מימוש'} פתוחה של {x.get('who') or 'שגריר'}" + (f", לטפל עד {x['due']}" if x.get("due") else ""), view="signups")
        if am.get("new_week"):
            add("info", "שגרירים", f"{am['new_week']} שגרירים חדשים השבוע", view="signups")
        try:
            age = (now() - dt.datetime.fromisoformat(am["exported_at"])).days
        except (KeyError, ValueError, TypeError):
            age = 0
        if age >= 3:
            add("info", "שגרירים", f"נתוני השגרירים נקראו לפני {age} ימים", view="signups")
    if rl:
        for r in rl.get("today", []):
            if r["status"] == "choose":   # two options, none picked yet (10 Nov 2026)
                add("warn", "רילס", f"לבחור את הריל של היום: {r['id'].replace(' / ', ' או ')}", "research/israeli-product-reels/reels-explorer.html")
            elif r["status"] not in ("posted", "ready"):
                add("warn", "רילס", f"הריל של היום ({r['id']}) {r['status_he']}", "research/israeli-product-reels/reels-explorer.html")
        for note in rl.get("shoot_today", []):
            add("info", "רילס", f"צילום היום: {note}", "research/israeli-product-reels/reels-explorer.html")
    if so:
        try:
            age = (now() - dt.datetime.fromisoformat(so["at"])).days if so.get("at") else None
        except ValueError:
            age = None
        if age is not None and age >= 2:
            add("info", "ביצועים", f"נתוני אינסטגרם ופייסבוק מלפני {age} ימים")
        for ch in so.get("errors") or {}:
            add("info", "ביצועים", f"Postiz לא החזיר נתונים ({ch})")
    order = {"crit": 0, "warn": 1, "info": 2}
    return sorted(out, key=lambda a: order[a["sev"]])


# ---------------------------------------------------------------- all of it

def collect(sheet_path=SHEET_EXPORT):
    parts = {}
    for name, fn in (("carousels", carousels), ("creators", creators), ("reels", reels), ("social", social),
                     ("ambassadors", lambda: ambassadors(sheet_path))):
        try:
            parts[name] = fn()
        except Exception as e:  # one broken source never empties the home
            parts[name] = None
            parts.setdefault("errors", {})[name] = f"{type(e).__name__}: {e}"[:200]
    parts["most_used"] = most_used()
    parts["attention"] = attention(parts["carousels"], parts["creators"], parts["ambassadors"], parts["reels"], parts["social"])
    parts["generated_at"] = now().isoformat(timespec="seconds")
    return parts


if __name__ == "__main__":
    if sys.argv[1:2] == ["sheet"] and len(sys.argv) == 3:
        a = ambassadors(save_sheet_export(sys.argv[2]))
        print(f"ambassadors {a['total']} (+{a['tests']} test), books {a['books']}, open payout requests {len(a['payouts_open'])}, sheet updated {a['sheet_updated']}")
    elif sys.argv[1:] == ["social"]:
        s = refresh_social()
        print(json.dumps({k: (list(v) if isinstance(v, dict) else len(v) if isinstance(v, list) else v) for k, v in s.items()}, ensure_ascii=False))
    else:
        print(json.dumps(collect(), ensure_ascii=False, indent=1))
