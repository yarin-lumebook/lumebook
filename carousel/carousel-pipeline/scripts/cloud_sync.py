#!/usr/bin/env python3
"""Bring the cloud packs down from GitHub into drafts/.

    python3 carousel/carousel-pipeline/scripts/cloud_sync.py
    python3 carousel/carousel-pipeline/scripts/cloud_sync.py --force 2026-10-18   # replace a local copy with the cloud's

The cloud routine pushes its work to branches: the weekly batch to batch/ID (one drafts/DATE folder per pack, pushed
after each pack, plus drafts/batches/ID.json), and the older nightly runs to nightly/DATE (nightly/DATE-2 when that date
already had one). This script:

1. fetches origin's batch/* and nightly/* branches (20 seconds at most; offline it says so and stops)
2. for every drafts/DATE folder on those branches (the newest branch wins for a date) that is not here yet, copies it with
   git archive, so the index and everything outside that folder are never touched; product images and slide PNGs come too
3. copies the batch plans (drafts/batches/*.json), which nobody edits by hand
4. records each new night in history.json and reco-history.json, as the finish scripts would have on the Mac
5. writes drafts/DATE/cloud-source.json (branch, commit, folder tree) so the same folder is never imported twice

A folder that already exists here is never overwritten, because it may hold Yarin's edits; a newer cloud version of it is
only reported (use --force DATE to take it). review_server.py runs this on start. Standard library only.
"""

import argparse
import io
import re
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402

BRANCH_RE = re.compile(r"^origin/(nightly|batch)/(\d{4}-\d{2}-\d{2})(?:-(\d+))?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_FILE = "cloud-source.json"
DRAFTS_REL = lib.DRAFTS.relative_to(lib.ROOT).as_posix()


def git(*args, timeout=20):
    return subprocess.run(["git", "-C", str(lib.ROOT), *args], capture_output=True, text=True, timeout=timeout)


def branches():
    """[(name, commit)] for origin's batch/* and nightly/* branches, oldest first (by date, then -N), so later ones win."""
    out = git("for-each-ref", "--format=%(refname:short) %(objectname)", "refs/remotes/origin/nightly/", "refs/remotes/origin/batch/")
    found = []
    for line in out.stdout.splitlines():
        name, _, commit = line.partition(" ")
        m = BRANCH_RE.match(name)
        if m:
            found.append(((m.group(2), int(m.group(3) or 1), m.group(1)), name, commit))
    return [(name, commit) for _, name, commit in sorted(found)]


def folders_on(ref):
    """{date: tree id} for the drafts/DATE folders on a branch."""
    out = git("ls-tree", "-d", ref, f"{DRAFTS_REL}/")
    trees = {}
    for line in out.stdout.splitlines():
        meta, _, path = line.partition("\t")
        name = path.rsplit("/", 1)[-1]
        if DATE_RE.match(name):
            trees[name] = meta.split()[2]
    return trees


def extract(ref, prefix):
    """Copy one path (a folder or a file) from the branch into the working tree."""
    out = subprocess.run(["git", "-C", str(lib.ROOT), "archive", "--format=tar", ref, prefix], capture_output=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.decode("utf-8", "replace").strip() or "git archive failed")
    with tarfile.open(fileobj=io.BytesIO(out.stdout)) as tar:
        members = [m for m in tar.getmembers() if m.name == prefix or m.name.startswith(prefix + "/")]
        tar.extractall(lib.ROOT, members=members, filter="data")


def record(folder):
    """Add the night to the local histories, so rotation here knows what the cloud already used."""
    import reco_lib as rl
    if (folder / "pack.json").exists():
        lib.record_history(lib.read_json(folder / "pack.json"))
    for f in rl.FORMATS:
        path = rl.carousel_path(folder, f)
        if path.exists():
            rl.record_history(lib.read_json(path))


def is_local_work(folder):
    return any((folder / n).exists() for n in ("pack.json", "reco-carousel.json", "reco-carousel-2.json"))


def same_on_main(date, tree):
    """True when the folder is the same on origin/main (committed here and pushed), so there is nothing to say."""
    out = git("rev-parse", f"origin/main:{DRAFTS_REL}/{date}")
    return out.returncode == 0 and out.stdout.strip() == tree


def sync(log=print, force=()):
    """Import every cloud folder that is not here yet. Returns the imported dates."""
    try:
        fetched = git("fetch", "--quiet", "--prune", "origin",
                      "+refs/heads/nightly/*:refs/remotes/origin/nightly/*", "+refs/heads/batch/*:refs/remotes/origin/batch/*")
        ok = fetched.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        ok = False
    if not ok:
        log("cloud: could not reach GitHub, showing the nights already here")
        return []
    newest = {}  # date: (branch, commit, tree); later branches win
    for branch, commit in branches():
        for date, tree in folders_on(branch).items():
            newest[date] = (branch, commit, tree)
        if branch.startswith("origin/batch/"):
            for path in git("ls-tree", "--name-only", branch, f"{DRAFTS_REL}/batches/").stdout.split():
                if path.endswith(".json"):
                    try:
                        extract(branch, path)
                    except (RuntimeError, OSError, subprocess.TimeoutExpired, tarfile.TarError) as e:
                        log(f"cloud: plan {path} failed to copy: {e}")
    imported = []
    for date, (branch, commit, tree) in sorted(newest.items()):
        folder = lib.DRAFTS / date
        source = folder / SOURCE_FILE
        meta = lib.read_json(source) if source.exists() else {}
        if meta.get("tree") == tree or (not meta.get("tree") and meta.get("commit") == commit):
            continue
        short = branch.removeprefix("origin/")
        if is_local_work(folder) and date not in force:
            if meta:
                log(f"cloud: a newer {date} is on {short}; not imported because yours may hold edits (cloud_sync.py --force {date} takes it)")
            elif not same_on_main(date, tree):
                log(f"cloud: {date} on {short} not imported, {date} already exists here")
            continue
        try:
            extract(branch, f"{DRAFTS_REL}/{date}")
            record(folder)
        except (RuntimeError, OSError, subprocess.TimeoutExpired, tarfile.TarError, ValueError, KeyError) as e:
            log(f"cloud: {date} from {short} failed to import: {e}")
            continue
        lib.write_json(source, {"branch": short, "commit": commit, "tree": tree,
                                "imported_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        imported.append(date)
        log(f"cloud: imported {date} from {short}")
    return imported


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", nargs="*", default=[], metavar="DATE", help="replace these local folders with the cloud's")
    args = ap.parse_args()
    if not sync(force=set(args.force)):
        print("cloud: nothing new")
