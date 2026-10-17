#!/usr/bin/env python3
"""Keep Hook Studio running on this Mac: start it at login on http://localhost:8777/ and restart it if it stops.

    python3 carousel/carousel-pipeline/scripts/hook_studio_login.py install     # write the login item and start it now
    python3 carousel/carousel-pipeline/scripts/hook_studio_login.py restart     # after editing a Hook Studio script
    python3 carousel/carousel-pipeline/scripts/hook_studio_login.py status
    python3 carousel/carousel-pipeline/scripts/hook_studio_login.py uninstall   # stop it and remove the login item

Yarin, 16 Oct 2026: "set Hook Studio to start at login on port 8777 so I can bookmark it".

A launchd agent (~/Library/LaunchAgents/com.yarinbruner.hook-studio.plist, the same naming as the GA4 agents) runs
review_server.py --port 8777 from the project folder, at login and again whenever it exits. The server imports its
modules once, so after changing review_server.py, studio.py, grade_page.py, grades.py, producer.py, batch.py or the
page builders, run `restart`. Log: ~/Library/Logs/HookStudio.log. Standard library only.
"""

import argparse
import os
import plistlib
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

LABEL = "com.yarinbruner.hook-studio"
PORT = 8777
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
LOG = Path.home() / "Library" / "Logs" / "HookStudio.log"
SERVER = Path(__file__).resolve().parent / "review_server.py"
ROOT = SERVER.parents[3]
DOMAIN = f"gui/{os.getuid()}"


def python():
    """Homebrew's python3 (the one the project runs on), not macOS's older /usr/bin/python3."""
    for candidate in (shutil.which("python3"), "/usr/local/bin/python3", "/opt/homebrew/bin/python3", sys.executable):
        if candidate and Path(candidate).exists() and candidate != "/usr/bin/python3":
            return candidate
    return sys.executable


def launchctl(*args):
    p = subprocess.run(["launchctl", *args], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def ping(timeout=2):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/ping", timeout=timeout) as r:
            return r.status == 200
    except OSError:
        return False


def install():
    LOG.parent.mkdir(parents=True, exist_ok=True)
    PLIST.parent.mkdir(parents=True, exist_ok=True)
    spec = {
        "Label": LABEL,
        "ProgramArguments": [python(), str(SERVER), "--port", str(PORT)],
        "WorkingDirectory": str(ROOT),
        "EnvironmentVariables": {
            "PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "LANG": "en_US.UTF-8",
            "PYTHONIOENCODING": "utf-8",   # the log has Hebrew topic names
            "PYTHONUNBUFFERED": "1",
        },
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 30,
        "ProcessType": "Interactive",
        "StandardOutPath": str(LOG),
        "StandardErrorPath": str(LOG),
    }
    with PLIST.open("wb") as f:
        plistlib.dump(spec, f)
    launchctl("bootout", f"{DOMAIN}/{LABEL}")   # an older copy of the agent, if any
    code, out = launchctl("bootstrap", DOMAIN, str(PLIST))
    if code:
        raise SystemExit(f"launchctl bootstrap failed: {out}")
    return wait_up()


def wait_up(seconds=45):
    """The server syncs the cloud packs first (git fetch, 20 seconds at most), then listens."""
    end = time.time() + seconds
    while time.time() < end:
        if ping():
            print(f"Hook Studio is up: http://localhost:{PORT}/")
            return True
        time.sleep(1)
    print(f"Hook Studio did not answer on port {PORT} yet; see {LOG}")
    return False


def restart():
    code, out = launchctl("kickstart", "-k", f"{DOMAIN}/{LABEL}")
    if code:
        raise SystemExit(f"not installed or not loaded ({out}); run install")
    time.sleep(1)
    return wait_up()


def uninstall():
    launchctl("bootout", f"{DOMAIN}/{LABEL}")
    if PLIST.exists():
        PLIST.unlink()
    print("Hook Studio no longer starts at login")


def status():
    code, out = launchctl("print", f"{DOMAIN}/{LABEL}")
    state = next((l.strip() for l in out.splitlines() if l.strip().startswith(("state =", "pid ="))), "") if not code else "not loaded"
    print(f"login item: {'installed' if PLIST.exists() else 'missing'} ({PLIST})")
    print(f"launchd: {state}")
    print(f"answering on http://localhost:{PORT}/: {'yes' if ping() else 'no'}")
    print(f"log: {LOG}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("install", "restart", "status", "uninstall"))
    args = ap.parse_args()
    {"install": install, "restart": restart, "status": status, "uninstall": uninstall}[args.cmd]()


if __name__ == "__main__":
    main()
