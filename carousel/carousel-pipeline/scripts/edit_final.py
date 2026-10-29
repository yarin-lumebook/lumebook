#!/usr/bin/env python3
"""Change the words of a carousel that already has its images, in one command (no new images, no cost).

    python3 edit_final.py RUN_DIR --slide 1 --headline "אמא ואבא\\n2 דברים שיעזרו לי" --body "לפני שאתם שמים אותי בגן"
    python3 edit_final.py RUN_DIR --caption "שורה 1\\nשורה 2"          # caption body; the CTA stays its last line
    python3 edit_final.py RUN_DIR --cta 'כתבו "גן" בתגובות ...'        # also updates the last slide, the caption and the code word

"\\n" in a value is a line break. Steps, all automatic:
1. the edit goes into the nightly pack through the review editor's save: backup to versions/vN, voice log
   (Yarin's edits teach the voice skill), validation, review page rebuilt
2. if the pack is valid, the option is re-frozen; the images and their QA carry over because their jobs did not change
3. only the changed slides are re-exported (the caption, contact sheet and ZIP are refreshed too), in the run's own look:
   a story run (story-format.md, 29 Oct 2026; 9 to 12 slides, a picture each) keeps the story look, because
   compose_slides.py reads copy_style and the option's structure from the refrozen approved.json
If validation fails nothing is re-frozen or exported, and the errors are printed.
"""

import argparse
import contextlib
import io
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import prepare_fal_jobs  # noqa: E402
import review_server  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent


def build_edits(option, args):
    edits = []
    if args.headline is not None or args.body is not None:
        if args.slide is None:
            raise SystemExit("--headline and --body need --slide N")
        for field in ("headline", "body"):
            value = getattr(args, field)
            if value is not None:
                edits.append({"option": option, "field": field, "slide": args.slide, "value": value.replace("\\n", "\n")})
    for field in ("caption", "cta", "title"):
        value = getattr(args, field)
        if value is not None:
            edits.append({"option": option, "field": field, "slide": None, "value": value.replace("\\n", "\n")})
    if not edits:
        raise SystemExit("nothing to change: pass --slide with --headline/--body, or --caption, --cta, --title")
    return edits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir")
    ap.add_argument("--slide", type=int)
    ap.add_argument("--headline")
    ap.add_argument("--body")
    ap.add_argument("--caption")
    ap.add_argument("--cta")
    ap.add_argument("--title")
    ap.add_argument("--drafts", default=str(lib.DRAFTS), help=argparse.SUPPRESS)
    ap.add_argument("--history", default=str(lib.HISTORY), help=argparse.SUPPRESS)
    ap.add_argument("--edits-log", default=str(lib.VOICE_EDITS), help=argparse.SUPPRESS)
    args = ap.parse_args()

    start = time.time()
    run_dir = Path(args.run_dir).resolve()
    frozen = lib.read_json(run_dir / "approved.json")
    date, option = frozen["date"], frozen["option"]["id"]
    edits = build_edits(option, args)

    result = review_server.save(date, edits, drafts=args.drafts, history_path=Path(args.history), edits_log=Path(args.edits_log))
    if "error" in result:
        raise SystemExit(result["error"])
    if not result.get("valid"):
        print(json.dumps({"valid": False, "errors": result.get("errors"), "saved_to_pack": True, "backup": result.get("backup")}, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    pack_path = Path(args.drafts) / date / "pack.json"
    argv = ["prepare_fal_jobs.py", str(pack_path), option, "--refreeze", "--no-history", "--out-root", str(run_dir.parent)]
    with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
        prepare_fal_jobs.main()
    # the refreeze set the old export aside in versions/vN; bring back the unchanged slides, then re-render the changed ones
    backups = sorted((run_dir / "versions").glob("v*"), key=lambda d: int(d.name[1:]))
    old_final = backups[-1] / "final" if backups else None
    if old_final and old_final.exists():
        shutil.copytree(old_final, run_dir / "final", dirs_exist_ok=True)
    state = lib.read_json(run_dir / "state.json")["jobs"]
    lost = [n for n, s in state.items() if s.get("status") != "done"]
    if lost:   # never happens for a words-only edit; if it does, say so instead of exporting a broken carousel
        raise SystemExit("these images need generating again after the refreeze: " + ", ".join(lost))

    last = len(lib.read_json(run_dir / "approved.json")["option"]["slides"])
    slides = sorted({e["slide"] for e in edits if e["slide"]} | ({last} if any(e["field"] == "cta" for e in edits) else set()))
    cmd = [sys.executable, str(SCRIPTS / "compose_slides.py"), str(run_dir)] + (["--slides", *map(str, slides)] if slides else ["--slides", str(last)])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout[-2000:], res.stderr[-2000:])
        raise SystemExit("export failed")
    out = json.loads(res.stdout)
    print(json.dumps({"valid": True, "changed": result.get("changed"), "warnings": result.get("warnings"),
                      "re_exported_slides": slides, "zip": out["zip"], "rtl_problems": out["rtl_problems"],
                      "voice_samples": result.get("voice_samples"), "seconds": round(time.time() - start, 1)},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
