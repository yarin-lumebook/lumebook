#!/usr/bin/env python3
"""Carousel Machine's pictures from ChatGPT in Yarin's own Chrome, made by Claude, free (Yarin, 30 Oct 2026: "disconnect my
fal account from the carousel machine, use my chatgpt in chrome to create the images so everything will be free").

    python3 carousel/carousel-pipeline/scripts/chatgpt_pictures.py next [RUN_DIR ...]     # JSON: what to make now
    python3 carousel/carousel-pipeline/scripts/chatgpt_pictures.py ingest RUN_DIR JOB [FILE]
    python3 carousel/carousel-pipeline/scripts/chatgpt_pictures.py status
    python3 carousel/carousel-pipeline/scripts/chatgpt_pictures.py qa RUN_DIR JOB pass|fail [--note "..."]   # chat-only runs

next      Every picture to make now, across the runs Carousel Machine marked "waiting for pictures from ChatGPT"
          (productions.json), or only the run folders given: run dir, job, the full prompt to send, the reference picture
          to attach (slide jobs of a story run: the approved cover), and the exact file name to download as. A run's cover
          comes first; its other slides are listed only after Yarin approved the cover in Carousel Machine.
ingest    Takes the downloaded picture (FILE, or the newest ~/Downloads/<download name>* when FILE is left out), keeps the
          original in generated-assets/chatgpt-originals/, writes generated-assets/<job>.png cropped to 4:5 at 1024 x 1280
          (what fal made), and records it in state.json like a finished generation (qa None, cost 0 in the log). Carousel
          Machine (review_server.py, every few seconds) then shows a cover for approval, and once every slide of an
          approved cover is in, builds the slides and the ZIP by itself.
status    Where each ChatGPT run stands.
qa        Records a QA result by hand, for a run produced from chat without Carousel Machine (the app records the cover's
          approval itself): `qa RUN slide-01 pass` makes `next RUN` list the other slides.

The browser side is scripts/chatgpt_helper.js (README "Pictures from ChatGPT"). Nothing here calls fal.ai or anything paid.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel_lib as lib  # noqa: E402

PRODUCTIONS = lib.PIPELINE / "productions.json"
HELPER = HERE / "chatgpt_helper.js"
SIZE = (1024, 1280)   # what the fal jobs made (4:5); compose_slides.py shows it at 1080 x 1350
IMAGE_SUFFIXES = (".png", ".webp", ".jpg", ".jpeg")
# ChatGPT makes 2:3 portraits; ingest crops the middle 4:5, so the lead asks for nothing important at the very top or bottom
LEAD = ("Make one image now, without questions and without describing it. A vertical portrait picture; keep everything "
        "important away from the very top and bottom edges, because the picture is cropped to 4:5.")
REFERENCE_LEAD = ("The reference image is the picture attached at the start of this chat (the cover of this carousel): "
                  "keep its characters, faces, clothes, home and 3D animated style exactly.")
QA_WITH_COVER = "approved with the cover in Carousel Machine"


# ---------------------------------------------------------------- the run folder

def downloads_dir():
    return Path(str((lib.production_config().get("chatgpt") or {}).get("downloads") or "~/Downloads")).expanduser()


def run_path(value):
    """A run folder from an absolute path, a path from the project or pipeline folder, a /approved/... app path or DATE-ID."""
    raw = str(value)
    p = Path(raw).expanduser()
    for cand in (p, lib.ROOT / raw, lib.PIPELINE / raw.lstrip("/"), lib.APPROVED / raw):
        if (cand / "jobs.json").exists():
            return cand.resolve()
    raise SystemExit(f"no production run at {value} (a folder with jobs.json, for example approved/2026-11-01-kid-1)")


def jobs_of(run_dir):
    return lib.read_json(Path(run_dir) / "jobs.json")


def state_of(run_dir):
    return lib.read_json(Path(run_dir) / "state.json")


def save_state(run_dir, state):
    lib.write_json(Path(run_dir) / "state.json", state)


def cover_of(jobs):
    """The picture Yarin approves: the cover of a story run (slide-01), else the run's first job (the one picture)."""
    return (jobs.get("reference_job") or "slide-01") if jobs.get("story") else jobs["order"][0]


def key_of(run_dir):
    a = Path(run_dir) / "approved.json"
    if a.exists():
        d = lib.read_json(a)
        if d.get("date") and d.get("option_id"):
            return f'{d["date"]}/{d["option_id"]}'
    return Path(run_dir).name


def download_name(run_dir, job):
    return f"lumebook-{Path(run_dir).name}-{job}.png"


def to_make(run_dir):
    """The jobs to make now: the cover while it has no picture; after the cover passed QA, every slide still missing."""
    jobs, st = jobs_of(run_dir), state_of(run_dir)["jobs"]
    cover = cover_of(jobs)
    if st.get(cover, {}).get("status") != "done":
        return [cover]
    if st[cover].get("qa") != "pass":
        return []
    return [n for n in jobs["order"] if n != cover and st.get(n, {}).get("status") != "done"]


def prompt_for(run_dir, job):
    """The full message for ChatGPT: the lead, the job's frozen prompt (as fal got it) and any fix notes from QA."""
    jobs, st = jobs_of(run_dir), state_of(run_dir)["jobs"].get(job, {})
    spec = jobs["jobs"][job]
    parts = [LEAD]
    if spec.get("refs"):
        parts.append(REFERENCE_LEAD)
    parts.append(spec["input"]["prompt"].strip())
    if st.get("replacements") and st.get("notes"):   # the same rule as fal_generate.payload_for
        parts.append("Fix from visual QA: " + " ".join(st["notes"]))
    return "\n\n".join(parts)


def reference_for(run_dir, job):
    spec = jobs_of(run_dir)["jobs"][job]
    refs = [Path(run_dir) / "generated-assets" / f"{r}.png" for r in spec.get("refs", [])]
    return str(refs[0]) if refs else None


def waiting_runs(path=None):
    """Run folders Carousel Machine marked as waiting for ChatGPT pictures (productions.json)."""
    path = Path(path or PRODUCTIONS)
    runs = lib.read_json(path).get("runs", {}) if path.exists() else {}
    out = []
    for key, rec in sorted(runs.items()):
        if rec.get("status") == "waiting" and rec.get("run_dir"):
            try:
                out.append(run_path(rec["run_dir"]))
            except SystemExit:
                continue
    return out


# ---------------------------------------------------------------- next, ingest, qa, replace

def next_jobs(run_dirs=None):
    dirs = [run_path(d) for d in run_dirs] if run_dirs else waiting_runs()
    jobs, runs = [], []
    for run_dir in dirs:
        names = to_make(run_dir)
        if not names:
            continue
        cover = cover_of(jobs_of(run_dir))
        stage = "cover" if names == [cover] else "slides"
        ref = reference_for(run_dir, names[0])
        runs.append({"key": key_of(run_dir), "run_dir": str(run_dir), "stage": stage, "jobs": names, "reference": ref})
        for n in names:
            jobs.append({"key": key_of(run_dir), "run_dir": str(run_dir), "job": n, "stage": stage, "prompt": prompt_for(run_dir, n),
                         "reference": reference_for(run_dir, n), "download_as": download_name(run_dir, n)})
    return {"backend": lib.picture_backend(), "downloads": str(downloads_dir()), "helper": str(HELPER), "runs": runs, "jobs": jobs,
            "steps": ["one new ChatGPT chat per run and stage (https://chatgpt.com/)",
                      "slides stage: attach the run's reference picture first (file_upload on the Attach photos input)",
                      "paste chatgpt_helper.js with the javascript tool, then LB.add(<this run's jobs as {name: download_as, prompt}>) and LB.next()",
                      "press Return with the computer tool whenever LB.status().state is 'press Return'",
                      "after each download: chatgpt_pictures.py ingest RUN_DIR JOB"]}


def find_download(run_dir, job, downloads=None):
    """The newest file in Downloads named like the job's download name (Chrome adds ' (1)' to a repeat)."""
    stem = Path(download_name(run_dir, job)).stem
    folder = Path(downloads or downloads_dir())
    hits = [p for p in folder.glob(stem + "*") if p.suffix.lower() in IMAGE_SUFFIXES and p.is_file()]
    if not hits:
        raise SystemExit(f"no download named {stem}* in {folder}")
    return max(hits, key=lambda p: p.stat().st_mtime)


def _size_sips(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)], capture_output=True, text=True, timeout=60).stdout
    vals = {k.strip(): v.strip() for k, _, v in (l.partition(":") for l in out.splitlines()) if k.strip() in ("pixelWidth", "pixelHeight")}
    return int(vals["pixelWidth"]), int(vals["pixelHeight"])


def crop_box(w, h, ratio=SIZE[0] / SIZE[1]):
    """The centred 4:5 area of a w x h picture, as (width, height)."""
    if w / h > ratio:
        return round(h * ratio), h
    return w, round(w / ratio)


def normalize(src, dst):
    """src (PNG, WebP or JPEG) -> dst PNG, the centred 4:5 crop at 1024 x 1280. Pillow when present, else macOS sips."""
    src, dst = Path(src), Path(dst)
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if Image is not None:
        with Image.open(src) as im:
            im = im.convert("RGB")
            cw, ch = crop_box(*im.size)
            left, top = (im.width - cw) // 2, (im.height - ch) // 2
            im.crop((left, top, left + cw, top + ch)).resize(SIZE, Image.LANCZOS).save(dst, "PNG")
        return
    if not shutil.which("sips"):
        raise SystemExit("cannot convert the picture: neither Pillow nor macOS sips is available")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work.png"
        run = lambda *a: subprocess.run(["sips", *a], capture_output=True, text=True, timeout=120, check=True)  # noqa: E731
        run("-s", "format", "png", str(src), "--out", str(work))
        cw, ch = crop_box(*_size_sips(work))
        run("-c", str(ch), str(cw), str(work))          # sips crops around the centre
        run("-z", str(SIZE[1]), str(SIZE[0]), str(work))
        shutil.move(str(work), str(dst))


def ingest(run_dir, job, file=None, downloads=None):
    """Take one ChatGPT picture into the run as generated-assets/<job>.png and record it like a finished generation."""
    run_dir = run_path(run_dir)
    jobs = jobs_of(run_dir)
    if job not in jobs["jobs"]:
        raise SystemExit(f"unknown job {job}; this run has " + ", ".join(jobs["order"]))
    allowed = to_make(run_dir)
    if job not in allowed:
        cover = cover_of(jobs)
        st = state_of(run_dir)["jobs"].get(job, {})
        if st.get("status") == "done":
            raise SystemExit(f"{job} already has a picture. For another take, ask for it in Carousel Machine (a note), then ingest again.")
        raise SystemExit(f"{job} is not due yet: the cover {cover} has to be made and approved in Carousel Machine first.")
    src = Path(file).expanduser() if file else find_download(run_dir, job, downloads)
    if not src.is_file():
        raise SystemExit(f"no file at {src}")
    gen = run_dir / "generated-assets"
    (gen / "rejected").mkdir(parents=True, exist_ok=True)
    originals = gen / "chatgpt-originals"
    originals.mkdir(parents=True, exist_ok=True)
    state = state_of(run_dir)
    st = state["jobs"].setdefault(job, {"status": "pending", "attempts": 0, "replacements": 0, "qa": None, "notes": []})
    attempt = int(st.get("attempts", 0)) + 1
    kept = originals / f"{job}-attempt{attempt}{src.suffix.lower() or '.png'}"
    shutil.move(str(src), str(kept))   # the download leaves ~/Downloads; the original stays with the run
    out = gen / f"{job}.png"
    try:
        normalize(kept, out)
    except Exception:
        shutil.move(str(kept), str(src))   # put the download back so nothing is lost
        raise
    st.update({"status": "done", "qa": None, "attempts": attempt, "source": "chatgpt",
               "ingested_at": lib.now_local().isoformat(timespec="seconds"), "original": str(kept.relative_to(run_dir))})
    save_state(run_dir, state)
    with (gen / "generation-log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"job": job, "backend": "chatgpt", "attempt": attempt, "replacement": bool(st.get("replacements")),
                             "estimated_cost_usd": 0, "billed": False, "status": "ok", "file": out.name,
                             "original": kept.name, "at": st["ingested_at"]}, ensure_ascii=False) + "\n")
    left = to_make(run_dir)
    return {"run_dir": str(run_dir), "job": job, "file": str(out), "original": str(kept), "still_to_make": left,
            "next": ("Carousel Machine shows it to Yarin for approval" if job == cover_of(jobs)
                     else ("all slides are in: Carousel Machine builds the slides and the ZIP by itself" if not left else f"{len(left)} more"))}


def qa(run_dir, job, result, note=None):
    """Record QA like fal_generate.py qa (the producer calls this for ChatGPT runs)."""
    run_dir = Path(run_dir)
    state = state_of(run_dir)
    st = state["jobs"][job]
    if st.get("status") != "done":
        raise RuntimeError(f"{job} has no finished picture to QA")
    st["qa"] = result
    if note:
        st.setdefault("notes", []).append(note)
    save_state(run_dir, state)


def replace(run_dir, job, note):
    """Another take with a note: the picture moves to generated-assets/rejected/, the job is due again in `next`, and
    its prompt carries the note (Fix from visual QA). At most max_replacements_per_job, like fal."""
    run_dir = Path(run_dir)
    jobs, state = jobs_of(run_dir), state_of(run_dir)
    st = state["jobs"][job]
    if st.get("replacements", 0) >= jobs.get("max_replacements_per_job", 2):
        raise RuntimeError(f"{job} already had {st['replacements']} other takes")
    pic = run_dir / "generated-assets" / f"{job}.png"
    if pic.exists():
        (pic.parent / "rejected").mkdir(exist_ok=True)
        pic.replace(pic.parent / "rejected" / f"{job}-attempt{st.get('attempts', 0)}.png")
    st.update({"status": "pending", "qa": "fail", "replacements": st.get("replacements", 0) + 1})
    if note:
        st.setdefault("notes", []).append(note)
    save_state(run_dir, state)
    return st


def counts(run_dir):
    """(pictures made, pictures in the run)."""
    jobs, st = jobs_of(run_dir), state_of(run_dir)["jobs"]
    return sum(1 for n in jobs["order"] if st.get(n, {}).get("status") == "done"), len(jobs["order"])


# ---------------------------------------------------------------- command line

def cmd_status():
    runs = lib.read_json(PRODUCTIONS).get("runs", {}) if PRODUCTIONS.exists() else {}
    shown = 0
    for key, rec in sorted(runs.items()):
        if rec.get("kind") == "reco" or not rec.get("run_dir") or rec.get("status") == "done":
            continue
        try:
            run_dir = run_path(rec["run_dir"])
        except SystemExit:
            continue
        made, total = counts(run_dir)
        todo = to_make(run_dir)
        print(f'{key:22} {rec.get("status", ""):9} pictures {made}/{total}  make now: {", ".join(todo) or "nothing"}')
        shown += 1
    if not shown:
        print("no production is waiting for pictures")
    print(f"picture backend: {lib.picture_backend()} (carousel/carousel-pipeline/production.json)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("next")
    n.add_argument("runs", nargs="*")
    i = sub.add_parser("ingest")
    i.add_argument("run_dir")
    i.add_argument("job")
    i.add_argument("file", nargs="?")
    sub.add_parser("status")
    q = sub.add_parser("qa")
    q.add_argument("run_dir")
    q.add_argument("job")
    q.add_argument("result", choices=["pass", "fail"])
    q.add_argument("--note")
    args = ap.parse_args()
    if args.cmd == "next":
        print(json.dumps(next_jobs(args.runs), ensure_ascii=False, indent=2))
    elif args.cmd == "ingest":
        print(json.dumps(ingest(args.run_dir, args.job, args.file), ensure_ascii=False, indent=2))
    elif args.cmd == "qa":
        try:
            qa(run_path(args.run_dir), args.job, args.result, args.note)
        except (RuntimeError, KeyError) as exc:
            raise SystemExit(str(exc))
        print(f"{args.job} qa {args.result}")
    else:
        cmd_status()


if __name__ == "__main__":
    main()
