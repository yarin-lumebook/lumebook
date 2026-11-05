#!/usr/bin/env python3
"""Freeze one chosen option and prepare its OpenAI picture jobs. Makes no network calls and spends nothing.

    python3 carousel/carousel-pipeline/scripts/prepare_picture_jobs.py PATH/pack.json kid-2
    python3 carousel/carousel-pipeline/scripts/prepare_picture_jobs.py PATH/pack.json kid-2 --refreeze

(Called prepare_fal_jobs.py until 03 Nov 2026, when Carousel Machine moved to the OpenAI Images API only.)

Creates carousel/carousel-pipeline/approved/DATE-OPTION/ with
    approved.json   frozen copy and visual briefs (never silently overwritten)
    jobs.json       one picture job per image (mode generate or edit, model, prompt, estimate), checked against openai_models.json
    state.json      per-job status, attempts, QA result and replacement count (resume point)
    APPROVAL.md     what to show Yarin before any paid call: copy, image count, model, quality, estimated tokens and cost, retry policy
    README.md       the exact commands for generation, QA, replacement and final export

Running it twice with the same option is safe. If the option's copy changed since it was frozen,
the script stops unless --refreeze is given, and then the old files move to versions/vN/.
A refreeze keeps every generated image whose job (prompt, model, settings) did not change, with its QA
result, and keeps the spend log, so a copy-only change never throws away or re-buys images.

Story packs (copy_style "story", story-format.md, 29 Oct 2026) get a picture per slide: slide-01 is the cover
(text-to-image from option.image and the character anchor, as for one-picture runs), slide-02 to slide-NN are edits of
the approved cover (same characters), each from its slide's scene. The cover runs first and waits for approval; the
rest run in parallel.

There is no built-in spending cap any more: the budget is whatever Yarin approves for the carousel (Carousel Machine asks,
openai_generate.py --max-usd enforces it, 03 Nov 2026).
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import openai_pictures as op  # noqa: E402
import validate_pack  # noqa: E402

MAX_REPLACEMENTS = 2
JOB_ORDER = ["character-reference"] + [f"slide-{n:02d}" for n in range(1, lib.SLIDE_COUNT + 1)]
PICTURE_JOB = "picture"  # packs from 14 Oct 2026: one picture for the whole carousel
STORY_COVER_JOB = "slide-01"   # story packs (29 Oct 2026): the cover, the reference for every other slide's edit
# Every story scene keeps the top third calm for the words, which sit on an ink veil (story-format.md section 4)
STORY_COMPOSITION = (
    "Composition: vertical 4:5. Keep the upper third of the frame calm: a plain wall or soft background with no faces, "
    "hands or important objects in it, because words are set over it later. No words, letters or numbers anywhere in "
    "the image."
)
# The picture is made at 2:3 and the centred 4:5 is kept (openai_pictures.normalize), so the very top and bottom are cut
CROP_NOTE = ("The picture is cropped to a centred 4:5 afterwards: keep every face and important object well inside the middle, "
             "and nothing important at the very top or bottom edge.")


def is_story(pack, version):
    """A story-format option (story-format.md): the pack's copy_style, or the option's own structure."""
    return (pack or {}).get("copy_style") == "story" or (version or {}).get("copy_style") == "story" or bool((version or {}).get("structure"))


def story_slide_prompt(anchor, scene):
    """The edit prompt for a story slide from 2 on: the cover as the reference (same characters), this slide's scene,
    the standing style block, the calm upper third and no text."""
    scene_line = f"Scene: {str(scene.get('action', '')).strip()} Setting: {str(scene.get('setting', '')).strip()}"
    extra = " ".join(f"{label}: {str(scene[k]).strip()}" for k, label in (("camera", "Camera"), ("lighting", "Lighting")) if scene.get(k))
    return "\n\n".join(p for p in [
        lib.REFERENCE_LOCK,
        "Characters, identical on every slide: "
        f"{anchor['child'].strip()} {anchor['parent'].strip()} Wardrobe: {anchor['wardrobe'].strip()}",
        scene_line + (" " + extra if extra else ""),
        lib.STYLE, lib.PALETTE, lib.AVOID,
        STORY_COMPOSITION,
        CROP_NOTE,
        lib.NO_TEXT,
    ] if p)


def make_job(cfg, mode, prompt, refs, base, **extra):
    """One jobs.json entry with its estimate (estimated_cost_usd: what spent() sums when a call's real cost is not known)."""
    job = {"mode": mode, "model": cfg["model"], "input": {**base, "prompt": prompt}, "refs": refs, **extra}
    job["estimated_cost_usd"] = op.estimate_job(job, cfg)["usd"]
    return job


def build_story_jobs(version, cfg, base, pillar):
    anchor, image = version["character_anchor"], version["image"]
    cover_prompt = lib.compose_image_prompt(anchor, image, 1, pillar=pillar, one_picture_prompt=True) + "\n\n" + CROP_NOTE
    jobs = {STORY_COVER_JOB: make_job(cfg, "generate", cover_prompt, [], base,
                                      purpose=f"slide 1 · cover · {image.get('beat', '')}".rstrip(" ·"), text_zone=image.get("text_zone", {}))}
    for s in version["slides"][1:]:
        scene = s.get("scene") or {}
        if not str(scene.get("action", "")).strip():
            raise SystemExit(f"slide {s['number']} has no scene: every story slide from 2 on needs scene.action and scene.setting")
        jobs[f"slide-{s['number']:02d}"] = make_job(
            cfg, "edit", story_slide_prompt(anchor, scene), [STORY_COVER_JOB], base,
            purpose=f"slide {s['number']} · {s.get('role', '')} · {str(scene.get('action', '')).strip()[:90]}")
    order = [f"slide-{s['number']:02d}" for s in version["slides"]]
    return {"order": order, "story": True, "reference_job": STORY_COVER_JOB, "backend": "openai",
            "max_replacements_per_job": MAX_REPLACEMENTS, "jobs": jobs}


def endpoint_config():
    return op.config()


def job_issues(name, job, cfg):
    """Check one job against the model snapshot. Returns a list of problems."""
    return op.job_issues(name, job, cfg)


def build_jobs(pack, version, cfg):
    anchor = version["character_anchor"]
    pillar = version["id"].split("-")[0]  # kid or expert: each pillar has its own photo direction
    base = op.base_input(cfg)
    if is_story(pack, version):
        return build_story_jobs(version, cfg, base, pillar)
    if lib.one_picture(version):
        # Yarin, 14 Oct 2026: one picture that depicts the idea for the whole carousel, shown behind every slide.
        image = version["image"]
        prompt = lib.compose_image_prompt(anchor, image, 1, pillar=pillar, one_picture_prompt=True) + "\n\n" + CROP_NOTE
        return {"order": [PICTURE_JOB], "backend": "openai", "max_replacements_per_job": MAX_REPLACEMENTS, "jobs": {PICTURE_JOB: make_job(
            cfg, "generate", prompt, [], base,
            purpose=f"the one picture behind all {len(version['slides'])} slides · {image['beat']}", text_zone=image["text_zone"])}}
    jobs = {"character-reference": make_job(cfg, "generate", lib.reference_prompt(anchor, pillar) + "\n\n" + CROP_NOTE, [], base,
                                            purpose="one character and style reference; every slide is an edit of it")}
    for s in version["slides"]:
        name = f"slide-{s['number']:02d}"
        jobs[name] = make_job(cfg, "edit", lib.compose_image_prompt(anchor, s["image"], s["number"], for_edit=True, pillar=pillar) + "\n\n" + CROP_NOTE,
                              ["character-reference"], base, purpose=f"slide {s['number']} · {s['role']} · {s['image']['beat']}",
                              text_zone=s["image"]["text_zone"])
    return {"order": JOB_ORDER, "backend": "openai", "max_replacements_per_job": MAX_REPLACEMENTS, "jobs": jobs}


def cost_summary(jobs):
    """(estimated dollars if every picture passes first time, estimated dollars if every picture needs MAX_REPLACEMENTS more)."""
    base = sum(j["estimated_cost_usd"] for j in jobs["jobs"].values())
    return round(base, 4), round(base * (1 + MAX_REPLACEMENTS), 4)


def approval_text(pack, direction, version, jobs, run_dir, cfg):
    base, maximum = cost_summary(jobs)
    total = op.estimate_total(jobs, cfg=cfg)
    lines = [
        f"# Approval sheet · {version['id']} · {pack['date']}",
        "",
        "Nothing has been generated and nothing has been paid for. Generation starts only after Yarin approves a budget for this carousel "
        "(Carousel Machine asks; by hand, openai_generate.py --max-usd).",
        "",
        "## Selected copy (frozen)",
        "",
        '<div dir="rtl" lang="he">',
        "",
    ]
    for s in version["slides"]:
        lines.append(f"**{s['number']} · {lib.ROLE_LABELS_HE.get(s['role'], s['role'])}**  ")
        lines += [f"{l}  " for l in lib.lines_of(s["headline"])]
        lines += [f"{l}  " for l in lib.lines_of(s.get("body", ""))]
        lines.append("")
    lines += ["**כיתוב**  "] + [f"{l}  " for l in lib.lines_of(version["caption"])] + ["", "</div>", "", "## Images", ""]
    if jobs.get("story"):
        n = len(jobs["jobs"])
        lines += [f"- Images: **{n}**, one per slide (story format, 29 Oct 2026): the cover by text-to-image, then {n - 1} slide scenes edited from the approved cover (same characters)"]
    elif PICTURE_JOB in jobs["jobs"]:
        lines += [f"- Images: **1**, the one picture that depicts the idea, behind all {len(version['slides'])} slides (Yarin, 14 Oct 2026)"]
    else:
        lines += [f"- Images: **{len(jobs['jobs'])}** (1 character and style reference + {lib.SLIDE_COUNT} slide scenes edited from it)"]
    lines += [
        f"- Model: `{cfg['model']}` through the OpenAI Images API · quality `{cfg['quality']}` · made at {cfg['size']}, saved as a centred 4:5 crop at 1024 x 1280 · final export 1080 x 1350",
        f"- Estimated tokens: about **{total['total_tokens']:,}** ({total['input_text_tokens']:,} prompt, {total['input_image_tokens']:,} reference picture, {total['output_tokens']:,} picture output)",
        f"- Estimated cost: about **${base:.2f}** if every image passes QA first time",
        f"- Estimated maximum: **${maximum:.2f}** if every image needs the maximum {MAX_REPLACEMENTS} replacements",
        "- The estimate is deliberately high (see scripts/openai_models.json); the real cost of each call is logged from the usage OpenAI returns",
        "- The runner refuses any call that would pass the budget Yarin approves, and asks for a bigger one first",
        "",
    ]
    if jobs.get("story"):
        lines += ["## Order", "",
                  "- The cover first. It is approved (qa slide-01 pass) or replaced with a note, at most twice.",
                  "- Then every other slide in parallel, each an edit of the approved cover from its slide's scene, the upper third kept calm for the words.",
                  "- Only a failed image is regenerated, with a short fix note added to its prompt.", ""]
    else:
        lines += ["## If visual QA fails", "",
                  "- Every image is inspected at full size for character consistency, hands, faces, anatomy, accidental words or letters, clean typography space, product accuracy and continuity.",
                  "- The reference image is checked first. Slides are generated only after the reference passes.",
                  "- Only a failed image is regenerated, with a short fix note added to its prompt. Passed images are never regenerated.",
                  f"- After {MAX_REPLACEMENTS} failed replacements of the same image, generation stops and Claude asks for direction.", "",
                  "## Slide 7", "",
                  "- The carousel never names the brand or a book title. Slide 7 only hints that a book where the child is the hero is one possible tool; the generated scene shows a child looking at a picture book with a drawing of themselves, with no logo or words.",
                  f"- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `{run_dir / 'real-assets'}/preview.png`).", ""]
    lines += ["## After approval", "", f"See `{run_dir / 'README.md'}` for the exact commands."]
    return "\n".join(lines) + "\n"


def readme_text(run_dir, jobs, slides=7):
    gen = lib.PIPELINE / "scripts" / "openai_generate.py"
    comp = lib.PIPELINE / "scripts" / "compose_slides.py"
    story = bool(jobs.get("story"))
    one = PICTURE_JOB in jobs["jobs"]
    cover = jobs.get("reference_job") or jobs["order"][0]
    head = (f"Generated pictures land in `generated-assets/` (4:5 crops; the 2:3 originals in `generated-assets/openai-originals/`), rejected attempts in `generated-assets/rejected/`, "
            "the run log in `generated-assets/generation-log.jsonl` (model, request id, token usage, real cost, never the key), the resume point in `state.json`. "
            "OPENAI_API_KEY comes from the environment only (the Keychain through `~/.zshrc`, so run through `zsh -ic`). "
            "**Every command that makes a picture needs `--max-usd`: the budget Yarin approved for this carousel. Ask for it, show the estimate (`plan`), and wait for his yes.**")
    plan = f"zsh -ic 'python3 {gen} {run_dir} plan'"
    if story:
        return f"""# Production run (story format, a picture per slide)

{slides} slides, a picture each (story-format.md, 29 Oct 2026): `generated-assets/slide-01.png` is the cover, `slide-02.png` to `slide-{slides:02d}.png` are edits of the approved cover. {head}

## 0 · The estimate

```bash
{plan}
```

## 1 · The cover

```bash
zsh -ic 'python3 {gen} {run_dir} run {cover} --max-usd BUDGET'
```

Inspect `generated-assets/{cover}.png` at full size (the child's face to the viewer, a big expression, hands, no letters), then `python3 {gen} {run_dir} qa {cover} pass`, or replace it:

```bash
zsh -ic 'python3 {gen} {run_dir} replace {cover} --note "what is wrong" --max-usd BUDGET'
```

## 2 · The other slides, in parallel

```bash
zsh -ic 'python3 {gen} {run_dir} run --max-usd BUDGET'
```

Finished slides are skipped, so the same command resumes. Inspect each and record `qa slide-NN pass` or `qa slide-NN fail --note "..."`, then `replace slide-NN --note "..." --max-usd BUDGET`.

## 3 · Final composition

```bash
python3 {comp} {run_dir}
```

The story look (Varela Round on an ink veil). Writes `final/01.png` to `final/{slides:02d}.png` at 1080 x 1350, the contact sheet, the RTL check, caption, sources, alt text and the ZIP. Layout check with no paid images: `--placeholders`. Status: `python3 {gen} {run_dir} status`
"""
    if one:
        return f"""# Production run (one picture)

The carousel has one picture that depicts the idea, shown behind all {slides} slides (Yarin, 14 Oct 2026). {head}

## 0 · The estimate

```bash
{plan}
```

## 1 · The picture

```bash
zsh -ic 'python3 {gen} {run_dir} run {PICTURE_JOB} --max-usd BUDGET'
```

Inspect `generated-assets/{PICTURE_JOB}.png` at full size (the child's face to the viewer, the idea readable, a clean text zone, hands, no letters), then `python3 {gen} {run_dir} qa {PICTURE_JOB} pass`, or replace it:

```bash
zsh -ic 'python3 {gen} {run_dir} replace {PICTURE_JOB} --note "what is wrong" --max-usd BUDGET'
```

## 2 · Final composition

```bash
python3 {comp} {run_dir}
```

Writes `final/slides.html`, `final/01.png` to `final/{slides:02d}.png` at 1080 x 1350, the contact sheet, the RTL check, caption, sources and the ZIP. Status: `python3 {gen} {run_dir} status`
"""
    return f"""# Production run

{head}

## 0 · The estimate

```bash
{plan}
```

## 1 · Reference image (after Yarin approves a budget)

```bash
zsh -ic 'python3 {gen} {run_dir} run character-reference --max-usd BUDGET'
```

Inspect `generated-assets/character-reference.png` at full size, then record the result:

```bash
python3 {gen} {run_dir} qa character-reference pass
```

## 2 · The slide scenes

```bash
zsh -ic 'python3 {gen} {run_dir} run --max-usd BUDGET'
```

Already finished jobs are skipped, so the same command resumes after a failure.
Inspect every slide at full size and record `qa slide-0N pass` or `qa slide-0N fail --note "what is wrong"`.

## 3 · Replace only failed slides

```bash
zsh -ic 'python3 {gen} {run_dir} replace slide-04 --note "five fingers on each hand, no letters on the book" --max-usd BUDGET'
```

Each image can be replaced {MAX_REPLACEMENTS} times. After that the runner stops and asks for direction.

## 4 · Final composition

```bash
python3 {comp} {run_dir}
```

No logo and no product card by default, because the carousel does not name the brand. `--preview-card` adds an unbranded `real-assets/preview.png` on slide 7; `--brand-mark` adds the logo.

This writes `final/slides.html` (editable), `final/01.png` to `final/08.png` at 1080 x 1350, `final/contact-sheet.png`, `final/rtl-check.png`, `final/caption.txt`, `final/sources.md` and the ZIP.

Status at any time: `python3 {gen} {run_dir} status`
"""


def carry_over(backup, run_dir, jobs):
    """After a refreeze: bring back images whose job is unchanged (with their state) and the spend log."""
    old_jobs_path, old_state_path = backup / "jobs.json", backup / "state.json"
    old_log = backup / "generated-assets" / "generation-log.jsonl"
    if old_log.exists():
        shutil.copy2(old_log, run_dir / "generated-assets" / "generation-log.jsonl")
    if not (old_jobs_path.exists() and old_state_path.exists()):
        return {}
    old_jobs = lib.read_json(old_jobs_path).get("jobs", {})
    old_state = lib.read_json(old_state_path).get("jobs", {})
    kept = {}
    tail = "\n\n" + CROP_NOTE

    def prompt_of(j):   # runs frozen before 03 Nov 2026 have no model or mode and no crop note: the prompt is what decides
        return str((j.get("input") or {}).get("prompt", "")).removesuffix(tail)

    for name, job in jobs["jobs"].items():
        img = backup / "generated-assets" / f"{name}.png"
        same = name in old_jobs and prompt_of(old_jobs[name]) == prompt_of(job) and (old_jobs[name].get("refs") or []) == (job.get("refs") or [])
        if same and old_state.get(name, {}).get("status") == "done" and img.exists():
            shutil.copy2(img, run_dir / "generated-assets" / img.name)
            kept[name] = old_state[name]
    return kept


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    ap.add_argument("option")
    ap.add_argument("--refreeze", action="store_true", help="replace a frozen option whose copy changed (old files go to versions/)")
    ap.add_argument("--out-root", default=str(lib.APPROVED), help=argparse.SUPPRESS)
    ap.add_argument("--no-history", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    pack_path = Path(args.pack).resolve()
    pack = lib.read_json(pack_path)
    errors = validate_pack.option_errors(pack, args.option, history=None)
    if errors:
        print(f"{args.option} is not valid, so nothing was frozen:")
        for i in errors:
            print(f"- {i}")
        raise SystemExit(1)
    found = [(d, v) for d in pack["directions"] for v in d["versions"] if v["id"] == args.option]
    if not found:
        raise SystemExit(f"unknown option {args.option}; choose one of " + ", ".join(v["id"] for d in pack["directions"] for v in d["versions"]))
    direction, version = found[0]

    run_dir = Path(args.out_root) / f"{pack['date']}-{version['id']}"
    frozen = {
        "date": pack["date"],
        "topic": lib.option_topic(pack, version) or pack["topic"],   # the option's own topic in a two-topic pack (24 Oct 2026)
        "direction": direction["id"],
        "option_id": version["id"],
        "source_pack": str(pack_path),
        "voice": pack["voice"],
        "product_facts": pack["product_facts"],
        "option": version,
    }
    if pack.get("copy_style"):   # the story format (29 Oct 2026): compose_slides.py picks its look from this
        frozen["copy_style"] = pack["copy_style"]
    approved_path = run_dir / "approved.json"
    backup = None
    if approved_path.exists():
        old = lib.read_json(approved_path)
        if old.get("option") != version:
            if not args.refreeze:
                raise SystemExit(f"{approved_path} already holds a different version of {version['id']}. Re-run with --refreeze to archive it and freeze the new copy.")
            backup = lib.backup_existing(run_dir, names=("approved.json", "jobs.json", "state.json", "APPROVAL.md", "README.md", "generated-assets", "final"))
        else:
            frozen["frozen_at"] = old.get("frozen_at")
    frozen.setdefault("frozen_at", None)
    frozen["frozen_at"] = frozen["frozen_at"] or lib.now_local().isoformat(timespec="seconds")

    cfg = endpoint_config()
    jobs = build_jobs(pack, version, cfg)
    problems = [p for name, job in jobs["jobs"].items() for p in job_issues(name, job, cfg)]
    if problems:
        print("Jobs do not match the model settings:")
        for p in problems:
            print(f"- {p}")
        raise SystemExit(1)

    for sub in ("generated-assets", "generated-assets/rejected", "real-assets", "final"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)
    lib.write_json(approved_path, frozen)
    lib.write_json(run_dir / "jobs.json", jobs)
    state_path = run_dir / "state.json"
    kept = carry_over(backup, run_dir, jobs) if backup else {}
    if not state_path.exists():
        fresh = {n: {"status": "pending", "attempts": 0, "replacements": 0, "qa": None, "notes": []} for n in jobs["order"]}
        fresh.update(kept)
        lib.write_json(state_path, {"jobs": fresh})
    base, maximum = cost_summary(jobs)
    (run_dir / "APPROVAL.md").write_text(approval_text(pack, direction, version, jobs, run_dir, cfg), encoding="utf-8")
    (run_dir / "README.md").write_text(readme_text(run_dir, jobs, slides=len(version["slides"])), encoding="utf-8")
    if not args.no_history:
        lib.mark_selected(pack["date"], version["id"])
    total = op.estimate_total(jobs, cfg=cfg)
    print(json.dumps({
        "run_dir": str(run_dir),
        "images": len(jobs["jobs"]),
        "model": cfg["model"],
        "quality": cfg["quality"],
        "size": cfg["size"],
        "estimated_tokens": total["total_tokens"],
        "estimated_usd": base,
        "estimated_max_usd": maximum,
        **({"story": True} if jobs.get("story") else {}),
        "backend": "openai",
        "approval_sheet": str(run_dir / "APPROVAL.md"),
        "network_calls": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
