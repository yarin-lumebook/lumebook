#!/usr/bin/env python3
"""Produce a carousel from Hook Studio itself, with no chat in between (Yarin, 16 Oct 2026: "i want the entire
carousel engine, editor and producer to be viewed in one place i can easily access no need of talking to you each time").

    python3 carousel/carousel-pipeline/scripts/producer.py status          # every production and where it stands
    python3 carousel/carousel-pipeline/scripts/producer.py export-reco 2026-10-19 reco-2   # games and books ZIP, no cost

Kid and expert option (one picture behind all ten slides, packs from 14 Oct 2026):
1. prepare_fal_jobs.py freezes the option into approved/DATE-ID/ (refreezes when the copy was edited since; images
   whose job did not change carry over)
2. fal_generate.py run picture --max-usd 0.50, through `zsh -ic` so FAL_KEY comes from ~/.zshrc and is never
   written anywhere. Picking the carousel for production in Hook Studio is the approval to spend up to $0.50 on it
   (the standing rule of 8 Oct 2026); the cap covers every attempt, replacements included
3. Yarin looks at the picture in Hook Studio and approves it (qa pass) or asks for another with a note (qa fail +
   replace, at most 2 replacements, inside the same $0.50)
4. compose_slides.py exports the 1080 x 1350 slides, contact sheet, RTL check, caption, sources and the ZIP

Games and books carousel: its slide PNGs are already final, so production is an export: approved/DATE-reco[-2]/final/
with the slides, caption, alt text, sources, contact sheet and the ZIP. No paid call.

State is productions.json (one entry per carousel, keyed "<date>/<id>"), written only here. Work runs in background
threads inside review_server.py; a restart in the middle marks the entry so the page offers to continue
(prepare and fal_generate are both resumable, a finished picture is never bought twice).
"""

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel_lib as lib  # noqa: E402
import reco_lib as rl  # noqa: E402

PRODUCTIONS = lib.PIPELINE / "productions.json"
MAX_USD = 0.50
PICTURE = "picture"
BUSY = ("queued", "preparing", "generating", "composing", "exporting")
STATUS_HE = {"queued": "בתור", "preparing": "מקפיא את הטקסט", "generating": "מייצר תמונה", "review": "מחכה לאישור שלך",
             "composing": "מרכיב שקופיות", "exporting": "מייצא", "done": "מוכן לפרסום", "failed": "נעצר"}
QA_CHECKS_HE = ("הפנים של הילד אל המצלמה, עם הבעה גדולה", "הרעיון של הקרוסלה נקרא מהתמונה", "יש אזור נקי לטקסט",
                "ידיים ופנים טבעיים, בלי אותיות או לוגו", "תלת ממד מונפש, לא צילום")
ABOUT = ("Hook Studio productions (producer.py). One entry per carousel keyed <date>/<id>; status: " + ", ".join(STATUS_HE)
         + ". Kid and expert: approved/DATE-ID, one picture, spend cap $0.50 per carousel. Games and books: export only.")

_lock = threading.RLock()
_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="produce")


def now_iso():
    return lib.now_local().isoformat(timespec="seconds")


def load(path=None):
    path = Path(path or PRODUCTIONS)
    data = lib.read_json(path) if path.exists() else {}
    data.setdefault("_about", ABOUT)
    data.setdefault("runs", {})
    return data


def get(key, path=None):
    return load(path)["runs"].get(key)


def _update(key, path=None, **fields):
    with _lock:
        data = load(path)
        rec = data["runs"].setdefault(key, {"key": key})
        rec.update(fields)
        rec["updated_at"] = now_iso()
        if fields.get("status"):
            rec["status_he"] = STATUS_HE.get(fields["status"], fields["status"])
        lib.write_json(path or PRODUCTIONS, data)
        return dict(rec)


def rel(path):
    """A path under the pipeline folder as the URL Hook Studio serves it from."""
    path = Path(path).resolve()
    if lib.PIPELINE.resolve() not in path.parents:   # tests write to a temporary folder
        return str(path)
    return "/" + str(path.relative_to(lib.PIPELINE.resolve())).replace("\\", "/")


def run_dir_for(item):
    return lib.APPROVED / f'{item["date"]}-{item["id"]}'


# ---------------------------------------------------------------- spend and files

def spent(run_dir):
    log = Path(run_dir) / "generated-assets" / "generation-log.jsonl"
    total = 0.0
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except (ValueError, json.JSONDecodeError):
                continue
            if rec.get("billed", True):   # the same rule as fal_generate.Run.spent
                total += float(rec.get("estimated_cost_usd") or 0)
    return round(total, 3)


def outputs(run_dir):
    final = Path(run_dir) / "final"
    out = {}
    zips = sorted(final.glob("*.zip")) if final.exists() else []
    if zips:
        out["zip"] = rel(zips[-1])
    for name, key in (("contact-sheet.png", "contact_sheet"), ("rtl-check.png", "rtl_check"), ("caption.txt", "caption_file")):
        if (final / name).exists():
            out[key] = rel(final / name)
    slides = sorted(final.glob("[0-9][0-9].png")) if final.exists() else []
    out["slides"] = [rel(p) for p in slides]
    return out


def compose_problems(text):
    """The RTL and fit problems compose_slides.py prints in its closing JSON."""
    at = text.find('{\n  "out_dir"')
    if at < 0:
        return []
    try:
        return json.loads(text[at:text.rindex("}") + 1]).get("rtl_problems", [])
    except (ValueError, json.JSONDecodeError):
        return []


def _sh(args, timeout, env_shell=False):
    """Run a pipeline script. env_shell: through `zsh -ic` so FAL_KEY comes from ~/.zshrc (never echoed)."""
    if env_shell:
        cmd = ["zsh", "-ic", " ".join(shlex.quote(str(a)) for a in args)]
    else:
        cmd = [str(a) for a in args]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(lib.PIPELINE.parents[1]))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _tail(text, n=6):
    lines = [l for l in text.strip().splitlines() if l.strip() and "FAL_KEY" not in l]
    return "\n".join(lines[-n:])


def _picture_state(run_dir):
    state = Path(run_dir) / "state.json"
    if not state.exists():
        return {}
    return lib.read_json(state).get("jobs", {}).get(PICTURE, {})


# ---------------------------------------------------------------- games and books export (no cost)

def export_reco(date, out_dir_name, drafts=None, approved=None):
    """Copy a games and books carousel's final slides into approved/DATE-<reco|reco-2>/final with its texts and a ZIP."""
    drafts = Path(drafts or lib.DRAFTS)
    folder = drafts / date
    fmt = {v: k for k, v in rl.OUT_DIRS.items()}[out_dir_name]
    car = lib.read_json(rl.carousel_path(folder, fmt))
    src = folder / out_dir_name
    slides = car.get("slides", [])
    pngs = [src / f"{i:02d}.png" for i in range(1, len(slides) + 1)]
    missing = [p.name for p in pngs if not p.exists()]
    if missing:
        raise RuntimeError("חסרות שקופיות: " + ", ".join(missing))
    final = Path(approved or lib.APPROVED) / f"{date}-{out_dir_name}" / "final"
    final.mkdir(parents=True, exist_ok=True)
    for p in pngs:
        shutil.copy2(p, final / p.name)
    if (src / "contact-sheet.png").exists():
        shutil.copy2(src / "contact-sheet.png", final / "contact-sheet.png")
    (final / "caption.txt").write_text(car.get("caption", "").strip() + "\n", encoding="utf-8")
    alt = [f'{i}: {lib.collapse(" ".join([s.get("headline", ""), s.get("body", "")]))}' for i, s in enumerate(slides, 1)]
    (final / "alt-text.txt").write_text("\n".join(alt) + "\n", encoding="utf-8")
    stage = car.get("stage") or {}
    md = [f"# Sources · games and books · {date}", "", f'Stage: {stage.get("age_label_he", "")} · {stage.get("skill", "")}', "", "## Development sources", ""]
    for s in car.get("dev_sources", []):
        md.append(f'- [{s.get("title", "")}]({s.get("url", "")}) · {s.get("publisher", "")} · read {s.get("accessed", "")}')
    md += ["", "## Products (slide order)", ""]
    for p in car.get("products", []):
        md.append(f'- {rl.KIND_HE.get(p.get("kind"), p.get("kind", ""))} · {p.get("title_he", "")} · {p.get("popularity_label", "")}')
        for a in p.get("availability", []):
            md.append(f'  - available: {a.get("retailer", "")} · {a.get("status", "")} · {a.get("url", "")} · {a.get("accessed", "")}')
    (final / "sources.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    zip_path = final / f"{date}-{out_dir_name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in pngs:
            z.write(final / p.name, f"slides/{p.name}")
        for name in ("caption.txt", "alt-text.txt", "sources.md", "contact-sheet.png"):
            if (final / name).exists():
                z.write(final / name, name)
    import drive_export  # Yarin's Drive content folder (18 Oct 2026); only real approved/ runs reach it
    drive_export.export(final.parent, quiet=True)
    return final.parent


# ---------------------------------------------------------------- the steps

def _prepare(item):
    pack = lib.DRAFTS / item["date"] / "pack.json"
    script = HERE / "prepare_fal_jobs.py"
    code, out = _sh([sys.executable, script, pack, item["id"]], 120)
    if code and "--refreeze" in out:   # Yarin edited the copy after an earlier freeze: archive it, keep matching images
        code, out = _sh([sys.executable, script, pack, item["id"], "--refreeze"], 120)
    if code:
        raise RuntimeError("ההקפאה נכשלה:\n" + _tail(out))
    run_dir = run_dir_for(item)
    jobs = lib.read_json(run_dir / "jobs.json")
    if jobs.get("order") != [PICTURE]:
        raise RuntimeError("זו קרוסלה בפורמט הישן (תמונה לכל שקופית). אותה מפיקים דרך קלוד.")
    return run_dir


def _generate(key, run_dir, replace_note=None):
    _update(key, status="generating", error=None)
    fal = HERE / "fal_generate.py"
    if replace_note is not None:
        code, out = _sh([sys.executable, fal, run_dir, "qa", PICTURE, "fail", "--note", replace_note], 60)
        if code:
            raise RuntimeError(_tail(out))
        args = [sys.executable, fal, run_dir, "replace", PICTURE, "--note", replace_note, "--max-usd", MAX_USD]
    else:
        args = [sys.executable, fal, run_dir, "run", PICTURE, "--max-usd", MAX_USD]
    code, out = _sh(args, 900, env_shell=True)
    st = _picture_state(run_dir)
    if st.get("status") != "done":
        raise RuntimeError("התמונה לא נוצרה:\n" + _tail(out))
    pic = Path(run_dir) / "generated-assets" / f"{PICTURE}.png"
    _update(key, status="review", picture=rel(pic) + f"?v={st.get('attempts', 1)}", spent_usd=spent(run_dir),
            replacements=st.get("replacements", 0), attempts=st.get("attempts", 1),
            error=_tail(out) if code else None)


def _compose(key, run_dir):
    _update(key, status="composing", error=None)
    code, out = _sh([sys.executable, HERE / "compose_slides.py", run_dir], 600)
    files = outputs(run_dir)
    if not files.get("zip"):
        raise RuntimeError("הייצוא נכשל:\n" + _tail(out))
    problems = compose_problems(out)
    warn = ("לבדוק לפני פרסום: " + "; ".join(problems[:4])) if problems else (_tail(out) if code else None)
    _update(key, status="done", done_at=now_iso(), spent_usd=spent(run_dir), warning=warn, rtl_problems=len(problems), **files)


def _work(key, item, action, note=None):
    try:
        if item["kind"] == "reco":
            _update(key, status="exporting", error=None)
            run_dir = export_reco(item["date"], item["id"])
            _update(key, status="done", done_at=now_iso(), run_dir=rel(run_dir), spent_usd=0, **outputs(run_dir))
            return
        if action == "approve":
            run_dir = lib.PIPELINE / get(key)["run_dir"].lstrip("/")
            code, out = _sh([sys.executable, HERE / "fal_generate.py", run_dir, "qa", PICTURE, "pass"], 60)
            if code:
                raise RuntimeError(_tail(out))
            return _compose(key, run_dir)
        if action == "redo":
            run_dir = lib.PIPELINE / get(key)["run_dir"].lstrip("/")
            return _generate(key, run_dir, replace_note=note or "another take")
        _update(key, status="preparing", error=None)
        run_dir = _prepare(item)
        _update(key, run_dir=rel(run_dir), spent_usd=spent(run_dir))
        st = _picture_state(run_dir)
        if st.get("status") == "done" and st.get("qa") == "pass":
            return _compose(key, run_dir)          # a picture approved earlier: only re-export
        if st.get("status") == "done":
            pic = Path(run_dir) / "generated-assets" / f"{PICTURE}.png"
            _update(key, status="review", picture=rel(pic) + f"?v={st.get('attempts', 1)}", spent_usd=spent(run_dir))
            return
        _generate(key, run_dir)
    except Exception as exc:  # noqa: BLE001 - the page shows the reason and offers to try again
        rec = get(key) or {}
        back = "review" if action == "redo" and rec.get("picture") else "failed"
        _update(key, status=back, error=str(exc)[:1500])


def _item_fields(item):
    return {k: item[k] for k in ("date", "kind", "id", "format", "topic_he", "cover", "batch", "child_name", "skill_he") if item.get(k)}


def start(item):
    """Queue one carousel. A carousel already in progress or done is left alone (done: use start again after edits)."""
    key = item["key"]
    with _lock:
        rec = get(key)
        if rec and rec.get("status") in BUSY + ("review",):
            return rec
        rec = _update(key, status="queued", requested_at=now_iso(), error=None, warning=None, **_item_fields(item))
    _pool.submit(_work, key, item, "start")
    return rec


def approve(key, item):
    with _lock:
        rec = get(key)
        if not rec or rec.get("status") != "review":
            raise ValueError("אין תמונה שמחכה לאישור")
        rec = _update(key, status="composing")
    _pool.submit(_work, key, item, "approve")
    return rec


def redo(key, item, note):
    with _lock:
        rec = get(key)
        if not rec or rec.get("status") != "review":
            raise ValueError("אין תמונה שמחכה לאישור")
        if rec.get("replacements", 0) >= 2:
            raise ValueError("כבר נוצרו 3 תמונות לקרוסלה הזו. כדי לנסות שוב צריך את קלוד.")
        rec = _update(key, status="generating", note=str(note)[:500])
    _pool.submit(_work, key, item, "redo", str(note)[:500])
    return rec


def recover(path=None):
    """On server start: anything that was running when the server stopped."""
    with _lock:
        data = load(path)
        changed = False
        for key, rec in data["runs"].items():
            if rec.get("status") not in BUSY:
                continue
            run_dir = lib.PIPELINE / rec["run_dir"].lstrip("/") if rec.get("run_dir") else None
            st = _picture_state(run_dir) if run_dir else {}
            if rec.get("kind") != "reco" and st.get("status") == "done" and st.get("qa") != "pass":
                rec.update(status="review", status_he=STATUS_HE["review"],
                           picture=rel(run_dir / "generated-assets" / f"{PICTURE}.png") + f"?v={st.get('attempts', 1)}")
            else:
                rec.update(status="failed", status_he=STATUS_HE["failed"], error="Hook Studio נסגר באמצע. אפשר להמשיך מאותה נקודה, בלי לשלם שוב על מה שכבר נוצר.")
            changed = True
        if changed:
            lib.write_json(path or PRODUCTIONS, data)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    e = sub.add_parser("export-reco")
    e.add_argument("date")
    e.add_argument("which", choices=sorted(rl.OUT_DIRS[f] for f in rl.MIXED_FORMATS))
    args = ap.parse_args()
    if args.cmd == "status":
        for key, rec in sorted(load()["runs"].items()):
            print(f'{key:24} {rec.get("status", ""):10} ${rec.get("spent_usd", 0):.2f} {rec.get("zip", "")} {rec.get("error") or ""}'.rstrip())
    else:
        print(export_reco(args.date, args.which))


if __name__ == "__main__":
    main()
