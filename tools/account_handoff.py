#!/usr/bin/env python3
"""Move the LumeBook claude.ai artifacts to the new Claude account (handoff of 26 Oct 2026).

Reads docs/account-handoff/artifacts.json (every artifact the old account owns). Steps: docs/account-handoff/README.md.

  python3 tools/account_handoff.py status            each artifact: what to do, its new link, whether it needs another
                                                     republish, and where old links of moved artifacts are still used
  python3 tools/account_handoff.py set KEY URL       record KEY's new link (and the hash of what was just published)
  python3 tools/account_handoff.py swap [--dry-run]  replace each moved artifact's old link with its new one in the project
                                                     sources, the Claude memory folder and the scheduled task prompts

Build outputs (lumebook.json build.outputs), carousel drafts and approved runs, _to-delete/ and this handoff folder are
never rewritten: rebuild with `lumebook.py ripple` / `build ID` after a swap. Standard library only.
"""
import argparse, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone, timedelta

try:  # Israel time with its summer and winter offsets (audit of 08 Nov 2026: a fixed UTC+3 was an hour off half the year)
    from zoneinfo import ZoneInfo
    IL = ZoneInfo("Asia/Jerusalem")
except Exception:  # no time zone data on this Python
    IL = timezone(timedelta(hours=3))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "docs", "account-handoff", "artifacts.json")
MEMORY = os.path.expanduser("~/.claude/projects/" + ROOT.replace("/", "-") + "/memory")
TASKS = os.path.expanduser("~/.claude/scheduled-tasks")
SCAN_EXT = {".py", ".sh", ".md", ".json", ".html", ".js", ".gs", ".css", ".txt"}
SKIP_PARTS = {"drafts", "approved", "_to-delete", "node_modules", ".vercel", ".site-editor"}
# Edited in the site editor and mirrored in content.en.md: change these by hand (CLAUDE.md rules)
BY_HAND = {"sites/lumebook-smm-plan/index.html", "sites/lumebook-smm-plan/content.en.md"}
URL_RE = re.compile(r"^https://claude\.ai/(code/)?artifact/[A-Za-z0-9-]+$")


def load():
    return json.load(open(MANIFEST, encoding="utf-8"))


def save(m):
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")


def published_paths(a):
    paths = [a["file"]] if a.get("file") else []
    paths += list((a.get("files") or {}).values())
    if a.get("files_glob"):
        folder = os.path.dirname(a["files_glob"].split(" ")[0])
        paths += sorted(os.path.join(folder, n) for n in os.listdir(os.path.join(ROOT, folder)))
    return paths


def digest(a):
    h = hashlib.sha256()
    for p in published_paths(a):
        full = os.path.join(ROOT, p)
        h.update(p.encode())
        h.update(open(full, "rb").read() if os.path.exists(full) else b"missing")
    return h.hexdigest()[:16]


def build_outputs():
    reg = json.load(open(os.path.join(ROOT, "lumebook.json"), encoding="utf-8"))["components"]
    return {o for c in reg.values() for o in ((c.get("build") or {}).get("outputs") or [])}


def scan_files():
    """Project text files git sees (tracked or not ignored), minus build outputs, plus memory and task prompts."""
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.splitlines()
    skip = build_outputs()
    for rel in sorted(set(out)):
        parts = rel.split("/")
        if rel in skip or rel in BY_HAND or rel.startswith("docs/account-handoff/") or SKIP_PARTS & set(parts):
            continue
        full = os.path.join(ROOT, rel)
        if os.path.splitext(rel)[1] in SCAN_EXT and os.path.isfile(full) and not os.path.islink(full):
            yield full
    for base in (MEMORY, TASKS):
        for dp, _, fns in os.walk(base):
            for fn in fns:
                if fn.endswith(".md"):
                    yield os.path.join(dp, fn)


def show(path):
    return os.path.relpath(path, ROOT) if path.startswith(ROOT) else path.replace(os.path.expanduser("~"), "~")


def cmd_status(m):
    moved = {}
    for a in m["artifacts"]:
        new = a.get("new_url")
        note = ""
        if new:
            moved[a["old_url"]] = a["key"]
            if a.get("file") and a.get("published_sha") != digest(a):
                note = "  << changed since it was published: republish to the new link, then set again"
        print(f"{a['key']:<20} {a['action'][:28]:<28} {new or '-'}{note}")
    left = sum(1 for a in m["artifacts"] if a["action"] == "republish" and not a.get("new_url"))
    print(f"\n{left} artifact(s) still to republish.")
    if not moved:
        return
    hits = []
    for path in scan_files():
        text = open(path, encoding="utf-8", errors="replace").read()
        for old, key in moved.items():
            if old in text:
                hits.append(f"  {show(path)}: {key} ({text.count(old)})")
    print(f"{len(hits)} file(s) still use an old link of a moved artifact" + (":" if hits else "."))
    if hits:
        print("\n".join(hits))
    for rel in sorted(BY_HAND):
        text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        if any(old in text for old in moved):
            print(f"  by hand (site editor + English mirror): {rel}")


def cmd_set(m, key, url):
    if not URL_RE.match(url):
        sys.exit(f"not an artifact link: {url}")
    a = next((a for a in m["artifacts"] if a["key"] == key), None)
    if not a:
        sys.exit(f"unknown key {key}; keys: " + ", ".join(x["key"] for x in m["artifacts"]))
    a["new_url"] = url
    a["published_sha"] = digest(a) if a.get("file") else None
    a["published_at"] = datetime.now(IL).isoformat(timespec="minutes")
    save(m)
    print(f"{key}: {url}")


def cmd_swap(m, dry):
    pairs = [(a["old_url"], a["new_url"]) for a in m["artifacts"] if a.get("new_url")]
    if not pairs:
        sys.exit("no new links recorded yet (set KEY URL first)")
    total = 0
    for path in scan_files():
        text = open(path, encoding="utf-8", errors="replace").read()
        new = text
        for old, url in pairs:
            new = new.replace(old, url)
        if new != text:
            n = sum(text.count(old) for old, _ in pairs)
            total += n
            print(f"  {show(path)}: {n}")
            if not dry:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
    print(f"{'would replace' if dry else 'replaced'} {total} link(s). Next: python3 tools/lumebook.py ripple, "
          "build the manual pages, then status.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("set")
    s.add_argument("key")
    s.add_argument("url")
    w = sub.add_parser("swap")
    w.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    m = load()
    if args.cmd == "status":
        cmd_status(m)
    elif args.cmd == "set":
        cmd_set(m, args.key, args.url)
    else:
        cmd_swap(m, args.dry_run)


if __name__ == "__main__":
    main()
