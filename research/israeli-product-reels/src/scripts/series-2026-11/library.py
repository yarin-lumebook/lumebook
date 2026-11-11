#!/usr/bin/python3
"""The reels' media library: one named copy of every picture and clip we make or collect for the reels, so nothing is made twice.

Yarin, 11 Nov 2026: "name everything you create/generate and save it with the rest so you can always reuse it to save api cost".
So every GPT picture (reel_gpt.py), every drawn book (broll.py), every child clip behind a picture (reel_make.py) and the shared
clips live once in the B-roll pool, media/projects/2026-11-11-reel-broll-pool/, under a name that says what they show, and are
listed in its library.json:

    {"file": "gpt/gpt-grandma-inspects-with-magnifying-glass.png",   path inside the pool (or "path": from the project root)
     "kind": "gpt" | "drawn" | "child-bg" | "clip" | "screen" | "cover",
     "about": "what it shows, in English",
     "words": ["Hebrew words of a script line it fits"],             what the planner matches against what Yarin says
     "key": "...",                                                   the prompt or the drawing spec it was made from (reuse test)
     "cost_usd": 0.0053, "made": "2026-11-11", "reels": ["1.4"]}

A reel uses a library file through a link in its source/ folder (one copy per file; the project server already follows links into
media/). Before anything is generated or drawn, the maker looks the key up here and links the file that exists instead.

    /usr/bin/python3 research/israeli-product-reels/src/scripts/series-2026-11/library.py list [kind]
    /usr/bin/python3 .../library.py check          every listed file exists, every pool file is listed
"""
import hashlib, json, os, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
POOL = ROOT / "media/projects/2026-11-11-reel-broll-pool"
INDEX = POOL / "library.json"
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"}


def load():
    try:
        return json.loads(INDEX.read_text())["items"]
    except (OSError, ValueError, KeyError):
        return []


def save(items):
    items = sorted(items, key=lambda e: (e.get("kind", ""), e.get("file") or e.get("path") or ""))
    INDEX.write_text(json.dumps({"_about": "Index of the reels' media library. Written by library.py, broll.py, reel_gpt.py; "
                                           "see library.py for the fields.", "items": items}, ensure_ascii=False, indent=1) + "\n")


def path_of(e):
    """The file of an entry, as an absolute path."""
    return (POOL / e["file"]) if e.get("file") else (ROOT / e["path"])


def slug(text, n=60):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s[:n].rstrip("-") or "item"


def key_of(obj):
    """A stable key for a prompt (normalised text) or a drawing spec (sorted JSON)."""
    if isinstance(obj, str):
        return " ".join(obj.lower().split())
    return hashlib.sha1(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def find(kind, key):
    """The entry of this kind made from this key (key_of a prompt or a spec), when its file exists."""
    return next((e for e in load() if e.get("kind") == kind and e.get("key") == key and path_of(e).exists()), None)


def put(entry):
    """Add or replace (by file) one entry; returns it."""
    items = [e for e in load() if (e.get("file"), e.get("path")) != (entry.get("file"), entry.get("path"))]
    entry.setdefault("made", date.today().isoformat())
    items.append(entry)
    save(items)
    return entry


def used_in(entry_file, rid):
    items = load()
    for e in items:
        if e.get("file") == entry_file and rid not in e.setdefault("reels", []):
            e["reels"].append(rid)
    save(items)


def free_name(folder, base, ext):
    """base + ext inside folder, with -2, -3... when the name is taken."""
    p, n = folder / f"{base}{ext}", 2
    while p.exists() or p.is_symlink():
        p, n = folder / f"{base}-{n}{ext}", n + 1
    return p


def link(target, reel_folder, rel):
    """Make reel_folder/rel a relative link to target (a library file). A real file already at rel is never overwritten."""
    dst = Path(reel_folder) / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink():
        dst.unlink()
    elif dst.exists():
        raise FileExistsError(f"{dst} is a real file; move it into the library first")
    os.symlink(os.path.relpath(target, dst.parent), dst)
    return dst


def child_bgs():
    """The child clips that go, darkened, behind every picture of a reel (Yarin, 11 Nov 2026: "always have a darken video of a
    child in the bg")."""
    return [path_of(e) for e in load() if e.get("kind") == "child-bg" and path_of(e).exists()]


def for_prompt(limit=80):
    """The library as short lines for a planner prompt: path to link, kind, what it shows, the words it fits."""
    out = []
    for e in load():
        if e.get("kind") == "child-bg":
            continue
        rel = ("pool:" + e["file"]) if e.get("file") else ("project:" + e["path"])
        words = ", ".join(e.get("words") or [])
        out.append(f"- {rel} ({e['kind']}): {e.get('about', '')}" + (f"; fits: {words}" if words else ""))
    return out[:limit]


def cmd_list(kind=None):
    for e in load():
        if kind and e.get("kind") != kind:
            continue
        ok = "" if path_of(e).exists() else "  MISSING"
        print(f"{e['kind']:9} {e.get('file') or e.get('path')}  {e.get('about', '')[:70]}{ok}")


def cmd_check():
    items, bad = load(), 0
    listed = {str(path_of(e).resolve()) for e in items}
    for e in items:
        if not path_of(e).exists():
            print("missing:", e.get("file") or e.get("path")); bad += 1
    for f in POOL.rglob("*"):
        if f.suffix.lower() in MEDIA_EXT and f.is_file() and str(f.resolve()) not in listed and ".cache" not in f.parts:
            print("not listed:", f.relative_to(POOL)); bad += 1
    print(f"{len(items)} items, {bad} problem(s)")
    return bad


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in ("list", "check"):
        sys.exit(__doc__)
    if a[0] == "list":
        cmd_list(a[1] if len(a) > 1 else None)
    else:
        sys.exit(1 if cmd_check() else 0)
