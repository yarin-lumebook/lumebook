#!/usr/bin/env python3
"""Freeze one chosen option and prepare its fal.ai jobs. Makes no network calls and spends nothing.

    python3 carousel/carousel-pipeline/scripts/prepare_fal_jobs.py PATH/pack.json kid-2
    python3 carousel/carousel-pipeline/scripts/prepare_fal_jobs.py PATH/pack.json kid-2 --refreeze

Creates carousel/carousel-pipeline/approved/DATE-OPTION/ with
    approved.json   frozen copy and visual briefs (never silently overwritten)
    jobs.json       one character reference job + one edit job per slide, checked against the endpoint schema
    state.json      per-job status, attempts, QA result and replacement count (resume point)
    APPROVAL.md     what to show Yarin before any paid call: copy, image count, endpoints, quality, cost, retry policy
    README.md       the exact commands for generation, QA, replacement and final export

Running it twice with the same option is safe. If the option's copy changed since it was frozen,
the script stops unless --refreeze is given, and then the old files move to versions/vN/.
A refreeze keeps every generated image whose job (prompt, endpoint, settings) did not change, with its QA
result, and keeps the spend log, so a copy-only change never throws away or re-buys images.

Story packs (copy_style "story", story-format.md, 29 Oct 2026) get a picture per slide: slide-01 is the cover
(text-to-image from option.image and the character anchor, as for one-picture runs), slide-02 to slide-NN are edits of
the approved cover (same characters), each from its slide's scene. The cover runs first and waits for approval; the
rest run in parallel. Spend cap STORY_MAX_USD for the whole carousel, every attempt included.

Pictures from ChatGPT (30 Oct 2026, production.json "picture_backend": "chatgpt", the default): the jobs and prompts are
the same, jobs.json gets "backend": "chatgpt" (and "max_usd": 0 on a story run), APPROVAL.md and README.md describe the free
ChatGPT flow (scripts/chatgpt_pictures.py) and the summary costs 0. Nothing here ever calls fal.ai either way.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402
import validate_pack  # noqa: E402

MAX_REPLACEMENTS = 2
JOB_ORDER = ["character-reference"] + [f"slide-{n:02d}" for n in range(1, lib.SLIDE_COUNT + 1)]
PICTURE_JOB = "picture"  # packs from 14 Oct 2026: one picture for the whole carousel
STORY_COVER_JOB = "slide-01"   # story packs (29 Oct 2026): the cover, the reference for every other slide's edit
STORY_MAX_USD = 1.00           # story packs: the cap for one carousel, every attempt and replacement included
# Every story scene keeps the top third calm for the words, which sit on an ink veil (story-format.md section 4)
STORY_COMPOSITION = (
    "Composition: vertical 4:5. Keep the upper third of the frame calm: a plain wall or soft background with no faces, "
    "hands or important objects in it, because words are set over it later. No words, letters or numbers anywhere in "
    "the image."
)


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
        lib.NO_TEXT,
    ] if p)


def build_story_jobs(version, cfg, base, pillar):
    t2i = "openai/gpt-image-2.5/flare/text-to-image"
    edit = "openai/gpt-image-2.5/flare/edit"
    anchor, image = version["character_anchor"], version["image"]
    jobs = {STORY_COVER_JOB: {
        "endpoint": t2i,
        "input": {**base, "prompt": lib.compose_image_prompt(anchor, image, 1, pillar=pillar, one_picture_prompt=True)},
        "refs": [],
        "estimated_cost_usd": cfg["estimate_usd_per_image"][t2i],
        "purpose": f"slide 1 · cover · {image.get('beat', '')}".rstrip(" ·"),
        "text_zone": image.get("text_zone", {}),
    }}
    for s in version["slides"][1:]:
        scene = s.get("scene") or {}
        if not str(scene.get("action", "")).strip():
            raise SystemExit(f"slide {s['number']} has no scene: every story slide from 2 on needs scene.action and scene.setting")
        jobs[f"slide-{s['number']:02d}"] = {
            "endpoint": edit,
            "input": {**base, "prompt": story_slide_prompt(anchor, scene)},
            "refs": [STORY_COVER_JOB],
            "estimated_cost_usd": cfg["estimate_usd_per_image"][edit],
            "purpose": f"slide {s['number']} · {s.get('role', '')} · {str(scene.get('action', '')).strip()[:90]}",
        }
    order = [f"slide-{s['number']:02d}" for s in version["slides"]]
    return {"order": order, "story": True, "reference_job": STORY_COVER_JOB, "max_usd": STORY_MAX_USD,
            "max_replacements_per_job": MAX_REPLACEMENTS, "jobs": jobs}


def endpoint_config():
    return lib.read_json(lib.FAL_ENDPOINTS)


def job_issues(name, job, cfg):
    """Check one job input against the endpoint snapshot. Returns a list of problems."""
    spec = cfg["endpoints"].get(job["endpoint"])
    if not spec:
        return [f"{name}: unknown endpoint {job['endpoint']}"]
    problems = []
    inp = dict(job["input"])
    if job.get("refs"):
        inp["image_urls"] = ["https://placeholder.invalid/ref.png" for _ in job["refs"]]
    for key in spec["required"]:
        if key not in inp:
            problems.append(f"{name}: missing {key}")
    for key in inp:
        if key not in spec["allowed"]:
            problems.append(f"{name}: {key} is not accepted by {job['endpoint']}")
    if inp.get("quality") not in spec["quality"]:
        problems.append(f"{name}: quality {inp.get('quality')} not in {spec['quality']}")
    if inp.get("output_format") not in spec["output_format"]:
        problems.append(f"{name}: output_format {inp.get('output_format')}")
    if not (1 <= inp.get("num_images", 1) <= spec["num_images_max"]):
        problems.append(f"{name}: num_images out of range")
    if len(inp.get("prompt", "")) > spec["prompt_max_chars"] or not inp.get("prompt", "").strip():
        problems.append(f"{name}: prompt length {len(inp.get('prompt', ''))}")
    if "image_urls" in inp and len(inp["image_urls"]) > spec.get("image_urls_max", 16):
        problems.append(f"{name}: too many reference images")
    size = inp.get("image_size")
    if isinstance(size, dict):
        w, h = size.get("width", 0), size.get("height", 0)
        c = spec["custom_size"]
        if w % c["multiple_of"] or h % c["multiple_of"]:
            problems.append(f"{name}: size {w}x{h} must be multiples of {c['multiple_of']}")
        if max(w, h) > c["max_edge"] or not (c["min_pixels"] <= w * h <= c["max_pixels"]) or max(w, h) / min(w, h) > c["max_aspect"]:
            problems.append(f"{name}: size {w}x{h} outside the endpoint limits")
        if abs(w / h - 0.8) > 0.001:
            problems.append(f"{name}: size {w}x{h} is not 4:5")
    return problems


def build_jobs(pack, version, cfg):
    anchor = version["character_anchor"]
    pillar = version["id"].split("-")[0]  # kid or expert: each pillar has its own photo direction
    t2i = "openai/gpt-image-2.5/flare/text-to-image"
    edit = "openai/gpt-image-2.5/flare/edit"
    base = {"image_size": dict(cfg["generation_size"]), "quality": cfg["quality"], "output_format": "png", "num_images": 1}
    if is_story(pack, version):
        return build_story_jobs(version, cfg, base, pillar)
    if lib.one_picture(version):
        # Yarin, 14 Oct 2026: one picture that depicts the idea for the whole carousel, shown behind every slide.
        image = version["image"]
        return {"order": [PICTURE_JOB], "max_replacements_per_job": MAX_REPLACEMENTS, "jobs": {PICTURE_JOB: {
            "endpoint": t2i,
            "input": {**base, "prompt": lib.compose_image_prompt(anchor, image, 1, pillar=pillar, one_picture_prompt=True)},
            "refs": [],
            "estimated_cost_usd": cfg["estimate_usd_per_image"][t2i],
            "purpose": f"the one picture behind all {len(version['slides'])} slides · {image['beat']}",
            "text_zone": image["text_zone"],
        }}}
    jobs = {
        "character-reference": {
            "endpoint": t2i,
            "input": {**base, "prompt": lib.reference_prompt(anchor, pillar)},
            "refs": [],
            "estimated_cost_usd": cfg["estimate_usd_per_image"][t2i],
            "purpose": "one character and style reference; every slide is an edit of it",
        }
    }
    for s in version["slides"]:
        name = f"slide-{s['number']:02d}"
        jobs[name] = {
            "endpoint": edit,
            "input": {**base, "prompt": lib.compose_image_prompt(anchor, s["image"], s["number"], for_edit=True, pillar=pillar)},
            "refs": ["character-reference"],
            "estimated_cost_usd": cfg["estimate_usd_per_image"][edit],
            "purpose": f"slide {s['number']} · {s['role']} · {s['image']['beat']}",
            "text_zone": s["image"]["text_zone"],
        }
    return {"order": JOB_ORDER, "max_replacements_per_job": MAX_REPLACEMENTS, "jobs": jobs}


def cost_summary(jobs):
    if jobs.get("backend") == "chatgpt":   # ChatGPT in Yarin's own account (30 Oct 2026): nothing is paid
        return 0.0, 0.0
    base = sum(j["estimated_cost_usd"] for j in jobs["jobs"].values())
    retries = sum(j["estimated_cost_usd"] * MAX_REPLACEMENTS for j in jobs["jobs"].values())
    if jobs.get("story"):   # a story carousel never spends past its cap, whatever the replacements
        return round(base, 3), round(min(base + retries, jobs.get("max_usd", STORY_MAX_USD)), 3)
    return round(base, 3), round(base + retries, 3)


def chatgpt_approval_text(pack, version, jobs, run_dir):
    """APPROVAL.md for a run whose pictures come from ChatGPT (30 Oct 2026): what will be made, at no cost."""
    n = len(jobs["jobs"])
    lines = [f"# Production sheet · {version['id']} · {pack['date']}", "",
             "Pictures are made in ChatGPT in Yarin's own Chrome, by Claude, at no cost (production.json picture_backend "
             "\"chatgpt\", 30 Oct 2026). fal.ai is never called.", "", "## Selected copy (frozen)", "", '<div dir="rtl" lang="he">', ""]
    for s in version["slides"]:
        lines.append(f"**{s['number']} · {lib.ROLE_LABELS_HE.get(s['role'], s['role'])}**  ")
        lines += [f"{l}  " for l in lib.lines_of(s["headline"])]
        lines += [f"{l}  " for l in lib.lines_of(s.get("body", ""))]
        lines.append("")
    lines += ["**כיתוב**  "] + [f"{l}  " for l in lib.lines_of(version["caption"])] + ["", "</div>", "", "## Images", ""]
    if jobs.get("story"):
        lines += [f"- Images: **{n}**, one per slide: the cover first, then {n - 1} slide scenes made from the approved cover as the reference picture (same characters)",
                  "- The cover waits for Yarin's approval in Carousel Machine; the other slides are made only after it"]
    else:
        lines.append(f"- Images: **{n}**" + (", the one picture behind every slide" if PICTURE_JOB in jobs["jobs"] else ""))
    lines += ["- Cost: **$0** (ChatGPT, Yarin's own account)", "", f"See `{run_dir / 'README.md'}` for the exact steps."]
    return "\n".join(lines) + "\n"


def chatgpt_readme_text(run_dir, jobs, slides):
    tool = lib.PIPELINE / "scripts" / "chatgpt_pictures.py"
    comp = lib.PIPELINE / "scripts" / "compose_slides.py"
    cover = jobs.get("reference_job") or jobs["order"][0]
    rest = ("" if not jobs.get("story") else
            f"\n## 2 · The other slides (after the cover is approved)\n\n`next` then lists `slide-02` to `slide-{slides:02d}`, each with the "
            f"approved cover as the reference picture. One new ChatGPT chat: attach `generated-assets/{cover}.png`, send the prompts "
            "one by one, ingest each download. When the last one is in, Carousel Machine builds the slides and the ZIP by itself.\n")
    return f"""# Production run (pictures from ChatGPT)

Pictures are made in ChatGPT in Yarin's Chrome by Claude, free (production.json picture_backend "chatgpt", 30 Oct 2026). fal.ai is never called. Each picture lands in `generated-assets/<job>.png` (cropped to 4:5, 1024 x 1280; the download is kept in `generated-assets/chatgpt-originals/`), the resume point is `state.json`.

## 1 · The cover

```bash
python3 {tool} next            # the prompt, the file name to download as
python3 {tool} ingest {run_dir} {cover}
```

Carousel Machine then shows the picture for approval (or another take with a note, which puts it back in `next`).
{rest}
## Final composition

Carousel Machine runs it by itself after the approval. By hand: `python3 {comp} {run_dir}`. Status: `python3 {tool} status`
"""


def approval_text(pack, direction, version, jobs, run_dir):
    if jobs.get("backend") == "chatgpt":
        return chatgpt_approval_text(pack, version, jobs, run_dir)
    base, maximum = cost_summary(jobs)
    lines = [
        f"# Approval sheet · {version['id']} · {pack['date']}",
        "",
        "Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.",
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
    lines += ["**כיתוב**  "] + [f"{l}  " for l in lib.lines_of(version["caption"])] + ["", "</div>", ""]
    if jobs.get("story"):
        n = len(jobs["jobs"])
        lines += [
            "## Images",
            "",
            f"- Images: **{n}**, one per slide (story format, 29 Oct 2026): the cover by text-to-image, then {n - 1} slide scenes edited from the approved cover (same characters)",
            "- Endpoints: `openai/gpt-image-2.5/flare/text-to-image` (cover), `openai/gpt-image-2.5/flare/edit` (slides 2 to the last)",
            "- Quality: `high` · generation size 1024 x 1280 (4:5) · final export 1080 x 1350",
            f"- Estimated cost: about **${base:.2f}** if every image passes QA first time",
            f"- Cap: **${maximum:.2f}** for the whole carousel, every attempt and replacement included (the runner refuses to pass it)",
            "- Pricing is token based; estimates come from the fal pricing table checked "
            + endpoint_config()["checked_at"] + " (see scripts/fal_endpoints.json)",
            "",
            "## Order",
            "",
            "- The cover first. It is approved (qa slide-01 pass) or replaced with a note, at most twice.",
            "- Then every other slide in parallel, each an edit of the approved cover from its slide's scene, the upper third kept calm for the words.",
            "- Only a failed image is regenerated, with a short fix note added to its prompt.",
            "",
            "## After approval",
            "",
            f"See `{run_dir / 'README.md'}` for the exact commands.",
        ]
        return "\n".join(lines) + "\n"
    lines += [
        "## Images",
        "",
        (f"- Images: **1**, the one picture that depicts the idea, behind all {len(version['slides'])} slides (Yarin, 14 Oct 2026)"
         if PICTURE_JOB in jobs["jobs"] else
         f"- Images: **{len(jobs['jobs'])}** (1 character and style reference + {lib.SLIDE_COUNT} slide scenes edited from it)"),
        ("- Endpoint: `openai/gpt-image-2.5/flare/text-to-image`" if PICTURE_JOB in jobs["jobs"] else
         "- Endpoints: `openai/gpt-image-2.5/flare/text-to-image` (reference), `openai/gpt-image-2.5/flare/edit` (slides)"),
        "- Quality: `high` · generation size 1024 x 1280 (4:5) · final export 1080 x 1350",
        f"- Estimated cost: about **${base:.2f}** if every image passes QA first time",
        f"- Estimated maximum: **${maximum:.2f}** if every image needs the maximum {MAX_REPLACEMENTS} replacements (the runner refuses to spend past the approved amount)",
        "- Pricing is token based; estimates come from the fal pricing table checked "
        + endpoint_config()["checked_at"] + " (see scripts/fal_endpoints.json)",
        "",
        "## If visual QA fails",
        "",
        "- Every image is inspected at full size for character consistency, hands, faces, anatomy, accidental words or letters, clean typography space, product accuracy and continuity.",
        "- The reference image is checked first. Slides are generated only after the reference passes.",
        "- Only a failed image is regenerated, with a short fix note added to its prompt. Passed images are never regenerated.",
        f"- After {MAX_REPLACEMENTS} failed replacements of the same image, generation stops and Claude asks for direction.",
        "",
        "## Slide 7",
        "",
        "- The carousel never names the brand or a book title. Slide 7 only hints that a book where the child is the hero is one possible tool; the generated scene shows a child looking at a picture book with a drawing of themselves, with no logo or words.",
        f"- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `{run_dir / 'real-assets'}/preview.png`).",
        "",
        "## After approval",
        "",
        f"See `{run_dir / 'README.md'}` for the exact commands.",
    ]
    return "\n".join(lines) + "\n"


def readme_text(run_dir, maximum, one=False, slides=7, story=False):
    gen = lib.PIPELINE / "scripts" / "fal_generate.py"
    comp = lib.PIPELINE / "scripts" / "compose_slides.py"
    if story:
        return f"""# Production run (story format, a picture per slide)

{slides} slides, a picture each (story-format.md, 29 Oct 2026): `generated-assets/slide-01.png` is the cover, `slide-02.png` to `slide-{slides:02d}.png` are edits of the approved cover. Rejected attempts go to `generated-assets/rejected/`, the run log to `generated-assets/generation-log.jsonl`, the resume point to `state.json`. FAL_KEY is read from the environment only (`~/.zshrc`, so run through `zsh -ic`). Cap for the whole carousel: ${maximum:.2f}.

## 1 · The cover

```bash
zsh -ic 'python3 {gen} {run_dir} run {STORY_COVER_JOB} --max-usd {maximum:.2f}'
```

Inspect `generated-assets/{STORY_COVER_JOB}.png` at full size (the child's face to the viewer, a big expression, hands, no letters), then `python3 {gen} {run_dir} qa {STORY_COVER_JOB} pass`, or replace it:

```bash
zsh -ic 'python3 {gen} {run_dir} replace {STORY_COVER_JOB} --note "what is wrong" --max-usd {maximum:.2f}'
```

## 2 · The other slides, in parallel

```bash
zsh -ic 'python3 {gen} {run_dir} run --max-usd {maximum:.2f}'
```

Finished slides are skipped, so the same command resumes. Inspect each and record `qa slide-NN pass` or `qa slide-NN fail --note "..."`, then `replace slide-NN --note "..." --max-usd {maximum:.2f}`.

## 3 · Final composition

```bash
python3 {comp} {run_dir}
```

The story look (Varela Round on an ink veil). Writes `final/01.png` to `final/{slides:02d}.png` at 1080 x 1350, the contact sheet, the RTL check, caption, sources, alt text and the ZIP. Layout check with no paid images: `--placeholders`. Status: `python3 {gen} {run_dir} status`
"""
    if one:
        return f"""# Production run (one picture)

The carousel has one picture that depicts the idea, shown behind all {slides} slides (Yarin, 14 Oct 2026). Generated files land in `generated-assets/`, rejected attempts in `generated-assets/rejected/`, the run log in `generated-assets/generation-log.jsonl`, the resume point in `state.json`. FAL_KEY is read from the environment only (`~/.zshrc`, so run through `zsh -ic`).

## 1 · The picture

```bash
zsh -ic 'python3 {gen} {run_dir} run {PICTURE_JOB} --max-usd {maximum:.2f}'
```

Inspect `generated-assets/{PICTURE_JOB}.png` at full size (the child's face to the viewer, the idea readable, a clean text zone, hands, no letters), then `python3 {gen} {run_dir} qa {PICTURE_JOB} pass`, or replace it:

```bash
zsh -ic 'python3 {gen} {run_dir} replace {PICTURE_JOB} --note "what is wrong" --max-usd {maximum:.2f}'
```

## 2 · Final composition

```bash
python3 {comp} {run_dir}
```

Writes `final/slides.html`, `final/01.png` to `final/{slides:02d}.png` at 1080 x 1350, the contact sheet, the RTL check, caption, sources and the ZIP. Status: `python3 {gen} {run_dir} status`
"""
    return f"""# Production run

Generated files land in `generated-assets/`, rejected attempts in `generated-assets/rejected/`, the run log in `generated-assets/generation-log.jsonl` (endpoint, request id, seconds, estimated cost, never the key), and the resume point in `state.json`.

FAL_KEY is read from the environment only. It lives in `~/.zshrc`, so run the commands through `zsh -ic` and never paste the key into a file.

## 1 · Reference image (after explicit approval of APPROVAL.md)

```bash
zsh -ic 'python3 {gen} {run_dir} run character-reference --max-usd {maximum:.2f}'
```

Inspect `generated-assets/character-reference.png` at full size, then record the result:

```bash
python3 {gen} {run_dir} qa character-reference pass
```

## 2 · The slide scenes

```bash
zsh -ic 'python3 {gen} {run_dir} run --max-usd {maximum:.2f}'
```

Already finished jobs are skipped, so the same command resumes after a failure.
Inspect every slide at full size and record `qa slide-0N pass` or `qa slide-0N fail --note "what is wrong"`.

## 3 · Replace only failed slides

```bash
zsh -ic 'python3 {gen} {run_dir} replace slide-04 --note "five fingers on each hand, no letters on the book" --max-usd {maximum:.2f}'
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
    for name, job in jobs["jobs"].items():
        img = backup / "generated-assets" / f"{name}.png"
        if old_jobs.get(name) == job and old_state.get(name, {}).get("status") == "done" and img.exists():
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
    if lib.picture_backend() == "chatgpt":   # 30 Oct 2026: the same prompts, made in ChatGPT for free
        jobs["backend"] = "chatgpt"
        if jobs.get("story"):
            jobs["max_usd"] = 0
    problems = [p for name, job in jobs["jobs"].items() for p in job_issues(name, job, cfg)]
    if problems:
        print("Jobs do not match the endpoint schema:")
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
    (run_dir / "APPROVAL.md").write_text(approval_text(pack, direction, version, jobs, run_dir), encoding="utf-8")
    if jobs.get("backend") == "chatgpt":
        (run_dir / "README.md").write_text(chatgpt_readme_text(run_dir, jobs, len(version["slides"])), encoding="utf-8")
    else:
        (run_dir / "README.md").write_text(readme_text(run_dir, maximum, one=PICTURE_JOB in jobs["jobs"], slides=len(version["slides"]),
                                                       story=bool(jobs.get("story"))), encoding="utf-8")
    if not args.no_history:
        lib.mark_selected(pack["date"], version["id"])
    print(json.dumps({
        "run_dir": str(run_dir),
        "images": len(jobs["jobs"]),
        "endpoints": sorted({j["endpoint"] for j in jobs["jobs"].values()}),
        "quality": cfg["quality"],
        "size": cfg["generation_size"],
        "estimated_usd": base,
        "estimated_max_usd": maximum,
        **({"cap_usd": jobs["max_usd"], "story": True} if jobs.get("story") else {}),
        "backend": jobs.get("backend", "fal"),
        "approval_sheet": str(run_dir / "APPROVAL.md"),
        "network_calls": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
