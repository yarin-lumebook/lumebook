"""Copy finished carousels into Yarin's Google Drive folder "LumeBook תוכן" (Yarin, 18 Oct 2026: "export there from now on").

The copy goes through Google Drive for desktop: the folder lives in My Drive, so on this Mac it appears under
~/Library/CloudStorage/GoogleDrive-<account>/<My Drive>/LumeBook תוכן and Drive uploads whatever lands there.
The folder's name and ids are in shared/facts.json (drive_content).

    python3 carousel/carousel-pipeline/scripts/drive_export.py                    # status + flush the waiting list
    python3 carousel/carousel-pipeline/scripts/drive_export.py approved/DATE-ID   # export one finished run now

compose_slides.py (kid and expert) and producer.export_reco (games and books) call export() after every export.
When Drive for desktop is not set up yet, the run is added to drive-pending.json and copied on the next flush.
Only runs inside approved/ are exported, so tests and side-by-side --out checks never reach Drive.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel_lib as lib  # noqa: E402

CLOUD = Path.home() / "Library" / "CloudStorage"
FILES = ("caption.txt", "alt-text.txt", "contact-sheet.png")


def config():
    return lib.read_json(lib.ROOT / "shared" / "facts.json").get("drive_content") or {}


def pending_path():
    return lib.APPROVED.parent / "drive-pending.json"


def local_root(cloud=None):
    """The synced "LumeBook תוכן" folder on this Mac, or None when Drive for desktop does not show it."""
    cloud = cloud or CLOUD
    cfg = config()
    name, account = cfg.get("name"), cfg.get("account", "")
    if not name or not cloud.exists():
        return None
    mounts = sorted(cloud.glob("GoogleDrive-*"), key=lambda p: account not in p.name)
    for m in mounts:
        for my_drive in m.iterdir():  # "My Drive" or the localised name ("האחסון שלי")
            if (my_drive / name).is_dir():
                return my_drive / name
    return None


def _title(run_dir):
    run_dir = Path(run_dir)
    topic = ""
    approved = run_dir / "approved.json"
    if approved.exists():
        topic = (lib.read_json(approved).get("topic") or {}).get("title_he", "")
    return f"{run_dir.name} {topic}".strip()


def _is_real(run_dir):
    try:
        Path(run_dir).resolve().relative_to(lib.APPROVED.resolve())
        return True
    except ValueError:
        return False


def _load_pending():
    path = pending_path()
    return lib.read_json(path).get("runs", []) if path.exists() else []


def _save_pending(runs):
    if runs:
        lib.write_json(pending_path(), {"_about": "Finished carousels waiting to be copied to Drive (scripts/drive_export.py).", "runs": runs})
    elif pending_path().exists():
        pending_path().unlink()


def copy_run(run_dir, root):
    final = Path(run_dir) / "final"
    slides = sorted(p for p in final.glob("[0-9][0-9].png"))
    if not slides:
        raise FileNotFoundError(f"{final} has no slides")
    dest = root / config().get("carousels", {}).get("name", "קרוסלות") / _title(run_dir)
    dest.mkdir(parents=True, exist_ok=True)
    for p in slides + [final / n for n in FILES if (final / n).exists()]:
        shutil.copy2(p, dest / p.name)
    return dest


def export(run_dir, quiet=False):
    """Copy one finished run to Drive, or queue it. Returns the destination folder or None."""
    if not _is_real(run_dir):
        return None
    rel = Path(run_dir).resolve().name
    root = local_root()
    pending = [r for r in _load_pending() if r != rel]
    if root is None:
        _save_pending(pending + [rel])
        if not quiet:
            print(f"Drive: Google Drive for desktop is not set up, {rel} waits in drive-pending.json", file=sys.stderr)
        return None
    dest = copy_run(run_dir, root)
    _save_pending(pending)
    if not quiet:
        print(f"Drive: copied to {dest}", file=sys.stderr)
    return dest


def flush():
    root = local_root()
    runs = _load_pending()
    if root is None:
        return root, [], runs
    done, left = [], []
    for rel in runs:
        try:
            done.append(str(copy_run(lib.APPROVED / rel, root)))
        except FileNotFoundError:
            left.append(rel)
    _save_pending(left)
    return root, done, left


def main():
    cfg = config()
    if len(sys.argv) > 1:
        run = Path(sys.argv[1])
        run = run if run.is_absolute() else (lib.PIPELINE / run if (lib.PIPELINE / run).exists() else run.resolve())
        dest = export(run, quiet=True)
        print(json.dumps({"run": str(run), "copied_to": str(dest) if dest else None, "waiting": dest is None}, ensure_ascii=False, indent=2))
        return
    root, done, left = flush()
    print(json.dumps({"drive_folder": cfg.get("url"), "local_folder": str(root) if root else None,
                      "copied": done, "waiting": left,
                      "note": None if root else "Install Google Drive for desktop and sign in with " + cfg.get("account", "the Drive account")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
