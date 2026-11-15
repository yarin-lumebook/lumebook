#!/usr/bin/env python3
"""Numbers per published post, from Postiz, every night (Yarin, 15 Nov 2026: "analyze what should we update automatically").

Until now a post's numbers only came in when Yarin downloaded a Meta export (audit.py import). Postiz can read them per post
(`postiz analytics:post <id>`): Instagram views, reach, saves, likes, comments, shares; Facebook impressions, reactions,
clicks. Postiz gives only today's total, never the history, so this keeps one row per day per post: run it every night and
each post gets its own growth curve, which no export has.

    python3 research/carousel-audit/src/postiz_results.py              read every post published in the last 45 days
    python3 research/carousel-audit/src/postiz_results.py --days 90    a longer window
    python3 research/carousel-audit/src/postiz_results.py --dry-run    read and print, write nothing

Writes data/postiz-results.json (internal figures: local only, like the rest of this folder). Read only on Postiz: it lists
posts and reads analytics, never creates, edits, connects or deletes anything. A post Postiz cannot read today keeps its old
numbers (never a 0 for "not read"); a post that left the window keeps its last numbers. The midnight job
(tools/nightly_commit.py) runs it before ripple. Prints PROGRESS lines for the background progress bar."""
import argparse, datetime as dt, json, os, re, subprocess, sys, time
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("LUMEBOOK_POSTIZ_RESULTS") or HERE.parent / "data" / "postiz-results.json")
POSTIZ = os.environ.get("LUMEBOOK_POSTIZ_CMD") or str(Path.home() / ".local" / "bin" / "postiz")
IL = ZoneInfo("Asia/Jerusalem")
# launchd starts with a bare PATH; the postiz CLI is a node script and node lives in /usr/local/bin or /opt/homebrew/bin
os.environ["PATH"] = "/usr/local/bin:/opt/homebrew/bin:" + os.environ.get("PATH", "/usr/bin:/bin") + ":" + str(Path.home() / ".local" / "bin")
PAUSE = 1.0          # seconds between analytics calls
DEADLINE = 15 * 60   # the whole run, so the midnight job never hangs on it


def postiz(*args, timeout=90):
    r = subprocess.run([POSTIZ, *args], capture_output=True, text=True, timeout=timeout)
    text = r.stdout
    starts = [i for i in (text.find("["), text.find("{")) if i >= 0]
    if not starts:
        raise RuntimeError((r.stderr or text or f"exit {r.returncode}").strip().replace("\n", " ")[:160])
    return json.loads(text[min(starts):])


def key(label):
    return re.sub(r"[^a-z0-9]+", "_", (label or "").lower()).strip("_")


def numbers(rows):
    """[{label, data: [{total, date}]}] -> {views: 197, ...}: the newest date's total of each metric."""
    out = {}
    for m in rows or []:
        data = [x for x in m.get("data") or [] if x.get("date")]
        if not data:
            continue
        last = max(data, key=lambda x: x["date"])
        try:
            out[key(m.get("label"))] = int(float(last.get("total")))
        except (TypeError, ValueError):
            continue
    return out


def plain(html):
    t = re.sub(r"<[^>]+>", " ", html or "")
    t = re.sub(r"&nbsp;|\s+", " ", t).strip()
    return t[:90]


def local(iso):
    try:
        return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(IL).isoformat(timespec="minutes")
    except (AttributeError, ValueError):
        return iso


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=45)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    started = time.monotonic()
    now = dt.datetime.now(dt.timezone.utc)
    today = now.astimezone(IL).date().isoformat()

    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except ValueError:
            sys.exit(f"{OUT} is not valid JSON; fix or move it before the next run")
    posts = old.get("posts") or {}

    try:
        listed = postiz("posts:list", "--startDate", (now - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT00:00:00Z"),
                        "--endDate", now.strftime("%Y-%m-%dT%H:%M:%SZ"), timeout=150)
    except Exception as e:
        print(f"postiz results: list failed, nothing changed ({e})")
        return 1
    listed = listed.get("posts", []) if isinstance(listed, dict) else listed
    live = [x for x in listed if (x.get("state") or x.get("status")) == "PUBLISHED" and x.get("id")]
    live.sort(key=lambda x: x.get("publishDate") or "")

    read = missing = failed = 0
    errors = []
    for i, x in enumerate(live, 1):
        if time.monotonic() - started > DEADLINE:
            errors.append(f"stopped at {i - 1} of {len(live)}: over {DEADLINE // 60} minutes")
            break
        integ = x.get("integration") or {}
        row = posts.setdefault(x["id"], {})
        row.update({"channel": integ.get("providerIdentifier"), "account": integ.get("name"), "group": x.get("group"),
                    "published": local(x.get("publishDate")), "url": x.get("releaseURL") or "",
                    "first_line": plain(x.get("content"))})
        try:
            res = postiz("analytics:post", x["id"])
        except Exception as e:
            failed += 1
            row["error"] = {"at": today, "what": str(e)[:160]}
            errors.append(f"{x['id']}: {str(e)[:80]}")
            if failed >= 3 and read == 0:   # Postiz is down or signed out: stop instead of hammering it
                errors.append("stopped after 3 failures in a row")
                break
            continue
        if isinstance(res, dict) and res.get("missing"):
            missing += 1   # published, but the platform gave Postiz no post id; fixing it (posts:connect) is a write, so only noted
            row["missing"] = today
            continue
        got = numbers(res if isinstance(res, list) else [])
        if not got:
            failed += 1
            row["error"] = {"at": today, "what": "no numbers in the answer"}
            continue
        read += 1
        row.pop("error", None)
        row.pop("missing", None)
        row["latest"] = {**got, "as_of": today}
        row.setdefault("daily", {})[today] = got
        print(f"PROGRESS {i}/{len(live)} {row['channel']} {row['published'][:10]}", flush=True)
        time.sleep(PAUSE)

    summary = (f"postiz results {today}: {read} of {len(live)} published posts read"
               + (f", {missing} without a platform id" if missing else "") + (f", {failed} failed" if failed else "")
               + f"; {len(posts)} posts on file")
    if a.dry_run:
        print(json.dumps({k: posts[k] for k in [x["id"] for x in live][-3:] if k in posts}, ensure_ascii=False, indent=1))
        print(summary + " (dry run, nothing written)")
        return 0
    if read == 0 and not live:
        print(summary)
        return 0
    data = {"about": "Numbers per published post as Postiz reports them (today's total; one row per day under daily). "
                     "Written by src/postiz_results.py every night; internal figures, local only.",
            "updated": now.astimezone(IL).isoformat(timespec="minutes"), "window_days": a.days,
            "last_run": {"read": read, "listed": len(live), "missing": missing, "failed": failed, "errors": errors[:10]},
            "posts": dict(sorted(posts.items(), key=lambda kv: kv[1].get("published") or ""))}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(OUT)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
