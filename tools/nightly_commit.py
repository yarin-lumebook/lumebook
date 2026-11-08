#!/usr/bin/env python3
"""Nightly snapshot of the whole LumeBook repo (dashboard and every component it is fed by), run by launchd at 00:00:
refresh the dashboard snapshot, commit, push, deploy (changed since Yarin's 20 Oct 2026 request; before that it only committed).

First rebuilds the dashboard snapshot (sites/dashboard/refresh.py: the home numbers, Postiz, the last ambassadors Sheet export) and writes the edit button's edits back
into any page rebuilt since (tools/site_editor.py bake_all). Commits to the current branch, pushes it to origin (never forced), then deploys every Vercel component whose files
changed since its last deploy (lumebook.json deploy.type vercel: the dashboard and the creator brief). A failed push
skips the deploy, so the live sites never run ahead of what is on GitHub. Follows the repo's own rules instead of bypassing them:
  - .gitignore decides what is in (raw media, .lumebook/, creator state/ stay out)
  - the pre-commit rule is applied up front: a Sheet export (*sheet.md) is never staged (the SMM plan's English-mirror rule
    went with the plan page, retired 8 Nov 2026)
  - the hook itself still runs; if it fails anyway the staging is undone and the reason is logged
Skips the commit when there is nothing to commit, when git is busy (merge, rebase, index.lock) or when a commit is half done.

  python3 tools/nightly_commit.py            commit now
  python3 tools/nightly_commit.py --dry-run  show what would be committed (no push, no deploy)
Log: .lumebook/nightly-commit.log"""
import importlib.util, os, subprocess, sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, ".lumebook", "nightly-commit.log")
# launchd starts with a bare PATH; npx (Vercel CLI) and node live in /usr/local/bin
os.environ["PATH"] = "/usr/local/bin:/opt/homebrew/bin:" + os.environ.get("PATH", "/usr/bin:/bin")
os.environ["GIT_TERMINAL_PROMPT"] = "0"


def git(*args, check=False):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip() or f"git {args[0]} failed")
    return r


def log(msg):
    line = f"{datetime.now().astimezone().isoformat(timespec='seconds')}  {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def busy():
    gd = git("rev-parse", "--absolute-git-dir").stdout.strip()
    for name in ("index.lock", "MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD", "REVERT_HEAD"):
        if os.path.exists(os.path.join(gd, name)):
            return name
    return None


def refresh_dashboard():
    """Rebuild the dashboard snapshot (sites/dashboard/out/): local files, live-site checks, public Instagram counts.
    Runs before the commit so GitHub and the deployed copy hold the same numbers. No signup Sheet (needs the Drive
    connector, which only the Claude app has), no artifact database push. A failure is logged and never blocks the rest."""
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "sites", "dashboard", "refresh.py")],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        log("dashboard refresh timed out after 600 s, using the previous snapshot")
        return
    out = (r.stdout + r.stderr).strip().replace("\n", " | ")
    log(("dashboard refreshed: " + out[-200:]) if r.returncode == 0 else "dashboard refresh FAILED, using the previous snapshot: " + out[-300:])


def push(branch):
    """Push the branch to origin. True when GitHub has everything that is committed here."""
    if git("remote", "get-url", "origin").returncode:
        log("push skipped: no origin remote")
        return False
    r = git("push", "origin", branch)
    if r.returncode:
        log("push failed: " + (r.stdout + r.stderr).strip().replace("\n", " | ")[:400])
        return False
    log(f"pushed {branch} to origin")
    return True


def deploy_changed():
    """Deploy each Vercel component whose files differ from its last deploy (tools/lumebook.py deploy builds first)."""
    spec = importlib.util.spec_from_file_location("lumebook_tool", os.path.join(ROOT, "tools", "lumebook.py"))
    lb = importlib.util.module_from_spec(spec)
    sys.argv = ["lumebook.py"]
    spec.loader.exec_module(lb)
    st = lb.load_state()
    for cid, c in lb.COMP.items():
        if c.get("deploy", {}).get("type") != "vercel":
            continue
        last = st["components"].get(cid, {}).get("deployed_hash")
        if last and lb.digest(cid)[0] == last:
            log(f"deploy {cid}: unchanged since the last deploy")
            continue
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lumebook.py"), "deploy", cid],
                           cwd=ROOT, capture_output=True, text=True, timeout=900)
        tail = (r.stdout + r.stderr).strip().replace("\n", " | ")[-300:]
        log(f"deployed {cid}" if r.returncode == 0 else f"deploy {cid} FAILED: {tail}")


def bake_edits():
    """Edits made with the edit button go back into pages that were rebuilt outside tools/lumebook.py (shared/site-editor)."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import site_editor
        done = site_editor.bake_all()
        if done:
            log("edits written back into " + ", ".join(done))
    except Exception as e:   # never block the nightly commit over it
        log(f"bake step failed: {e}")
    try:   # the language switch's words go into every page too (tools/i18n.py, 8 Nov 2026)
        import i18n
        done = i18n.bake_all()
        if done:
            log(f"language words written into {len(done)} pages")
    except Exception as e:
        log(f"language bake step failed: {e}")


def ship(branch):
    """Push, then deploy. A failed push or deploy is logged and makes the job exit 1; the commit stays."""
    if not push(branch):
        return 1
    try:
        deploy_changed()
    except Exception as e:
        log(f"deploy step failed: {e}")
        return 1
    return 0


def main():
    dry = "--dry-run" in sys.argv
    if (b := busy()):
        log(f"skipped: git is busy ({b})")
        return 0
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch == "HEAD":
        log("skipped: detached HEAD")
        return 0
    if git("diff", "--cached", "--quiet").returncode:
        log("skipped: something is already staged (a commit may be in progress)")
        return 0

    if not dry:
        refresh_dashboard()
        bake_edits()
    git("add", "-A", check=True)
    notes = []
    staged = git("diff", "--cached", "--name-only").stdout.splitlines()
    for path in [x for x in staged if x.endswith("sheet.md")]:
        git("reset", "-q", "--", path)
        notes.append(f"left out {path} (Sheet export)")
    staged = git("diff", "--cached", "--name-only").stdout.splitlines()

    if not staged:
        log("nothing to commit" + (f" ({'; '.join(notes)})" if notes else ""))
        return ship(branch)
    if dry:
        print("\n".join(staged[:50]) + (f"\n... {len(staged)} files" if len(staged) > 50 else ""))
        print("notes:", notes)
        git("reset", "-q")
        return 0

    top = {}
    for x in staged:
        top[x.split("/")[0] if "/" in x else "."] = top.get(x.split("/")[0] if "/" in x else ".", 0) + 1
    areas = ", ".join(f"{k} {n}" for k, n in sorted(top.items(), key=lambda kv: -kv[1])[:6])
    msg = f"Nightly snapshot {datetime.now().date().isoformat()}: {len(staged)} files ({areas})"
    r = git("commit", "-q", "-m", msg)
    if r.returncode:
        git("reset", "-q")
        log("commit failed, staging undone: " + (r.stdout + r.stderr).strip().replace("\n", " | ")[:400])
        return 1
    sha = git("rev-parse", "--short", "HEAD").stdout.strip()
    log(f"committed {sha} on {branch}: {len(staged)} files" + (f"; {'; '.join(notes)}" if notes else ""))
    return ship(branch)


if __name__ == "__main__":
    sys.exit(main())
