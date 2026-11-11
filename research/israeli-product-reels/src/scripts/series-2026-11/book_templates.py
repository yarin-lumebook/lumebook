#!/usr/bin/env python3
"""Blank LumeBook book templates, made once with the OpenAI Images API, so real covers and pages can be pasted onto them for free.

Yarin, 11 Nov 2026: "if you need to generate a plain book (hard thin copy) in different positions so you could paste text and
images using gpt api tell me and ill give you an approval after you give me budget". He approved up to $0.15 for 8 positions
plus up to 4 retries (estimate about $0.0106 a picture, gpt-image-2.5-flare 1024x1536 low; measured runs cost $0.0053).

Each position is one blank square book (22 x 22 cm per docs/lumebook-product-brief.md, a thin hard cover as Yarin said), white
cover and white pages, on a plain light grey ground. The pictures go into the library (library.py) under
media/projects/2026-11-11-reel-broll-pool/book-templates/book-blank-<position>.png with kind "template"; broll.py warps the
store cover or a page onto the blank surfaces. A position already in the library is never made again.

Yarin's rules for the key (memory feedback-openai-api-key-rules) apply: `plan` spends nothing; `run` refuses without --max-usd
and --yes, and stops before a call whose estimate would take the logged spend past --max-usd. A call whose outcome is unknown
counts at its estimate. The key comes from the environment (run through zsh -ic) and is never printed or written.

    python3 research/israeli-product-reels/src/scripts/series-2026-11/book_templates.py plan
    zsh -ic 'python3 .../book_templates.py run --max-usd 0.15 --yes'                 every position not made yet
    zsh -ic 'python3 .../book_templates.py run open-flat-top-view --again --max-usd 0.15 --yes'   a retry (kept as -v2)
"""
import argparse, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "carousel/carousel-pipeline/scripts"))
import library  # noqa: E402
import openai_pictures as op  # noqa: E402

FOLDER = library.POOL / "book-templates"
LEDGER = FOLDER / "ledger.json"
BASE = ("A clean realistic 3D product render of one plain blank square children's picture book, 22 by 22 cm, a thin hard cover, "
        "about 24 pages. The cover and every page are completely blank matte white with no print at all: no text, no letters, "
        "no numbers, no pictures, no logo, no pattern. Soft even studio light, a soft natural shadow, a plain light grey seamless "
        "background with nothing else in the scene, no hands, no people. The whole book is in frame with clear space around it, "
        "with sharp straight edges and square corners. Position: ")
POSITIONS = {
    "closed-standing-cover-three-quarter": ("The book is closed and stands upright on its bottom edge, turned about 30 degrees so the "
        "front cover faces the viewer at three quarters, the spine on the right side, the thin page block visible along the left edge. "
        "The book is exactly square, as wide as it is tall, like a 22 by 22 cm picture book.",
        "closed book standing, cover turned three quarters to the camera (for lines about the cover)"),
    "closed-flat-above-angle": ("The book is closed and lies flat, front cover up, seen from above at a 45 degree angle, the spine on "
        "the right, the thin page block visible along the bottom and left edges.",
        "closed book lying flat, cover up, seen from above at an angle"),
    "open-flat-top-view": ("The book lies open flat, seen straight from above, both square pages fully visible side by side, the pages "
        "curving gently down into the gutter in the middle. Each page is exactly square, as wide as it is tall, so the open book is "
        "twice as wide as it is tall.",
        "open book seen from the top, both pages flat"),
    "open-angle-three-quarter": ("The book lies open, seen from the front at a low 30 degree angle, both pages visible and curving "
        "into the gutter, the thin page block visible at the outer edges.",
        "open book at an angle, pages curving into the middle"),
    "open-page-turning": ("The book lies open, seen from above at an angle, with one page lifted halfway in the middle of being turned "
        "from right to left, curving in the air, both lower pages visible.",
        "open book with one page halfway through a turn"),
    "open-right-page-close": ("The book lies open, seen close up from slightly above, the camera centred on the right-hand page, which "
        "fills most of the frame, the left-hand page partly visible at the left edge.",
        "open book, close on the right-hand page (title, dedication or name page)"),
    "open-standing-shown": ("The book stands upright and open towards the viewer, opened to about 150 degrees, both pages facing the "
        "camera, standing on its bottom edge as if it is being shown. Each page is exactly square, as wide as it is tall.",
        "open book standing up, both pages shown to the camera"),
    "three-closed-stacked": ("Three identical closed books lie in a loose stack, each turned a little differently, the top one fully "
        "visible with its front cover up, seen from above at an angle.",
        "three closed books in a small stack (one child, many stories)"),
}


def job(slug, cfg):
    return {"mode": "generate", "model": cfg["model"],
            "input": {"prompt": BASE + POSITIONS[slug][0], "size": cfg["size"], "quality": cfg["quality"], "n": 1}}


def spent():
    try:
        return round(sum(r.get("usd", 0) for r in json.loads(LEDGER.read_text())), 5)
    except (OSError, ValueError):
        return 0.0


def log(rec):
    rows = json.loads(LEDGER.read_text()) if LEDGER.exists() else []
    rows.append(rec)
    LEDGER.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")


def made(slug):
    return library.find("template", library.key_of(BASE + POSITIONS[slug][0]))


def cmd_plan(a):
    cfg = op.config()
    tot, tok = 0.0, 0
    for s in POSITIONS:
        e = op.estimate_job(job(s, cfg), cfg)
        have = made(s)
        if not have:
            tot += e["usd"]; tok += e["input_text_tokens"] + e["output_tokens"]
        print(f"{s:38} ${e['usd']:.4f}  {'in library: ' + have['file'] if have else 'to make'}")
    print(f"\nto make: ${tot:.4f} estimated, about {tok} tokens; spent so far ${spent():.4f}")


def cmd_run(a):
    if not a.max_usd:
        sys.exit("--max-usd is required: the budget Yarin approved")
    if not a.yes:
        sys.exit("--yes is required, and only after Yarin said yes to this budget in chat")
    cfg = op.config()
    want = a.slugs or list(POSITIONS)
    bad = [s for s in want if s not in POSITIONS]
    if bad:
        sys.exit(f"unknown position: {', '.join(bad)}")
    todo = [s for s in want if a.again or not made(s)]
    FOLDER.mkdir(parents=True, exist_ok=True)
    running = spent()
    est = sum(op.estimate_job(job(s, cfg), cfg)["usd"] for s in todo)
    print(f"{len(todo)} to make, estimate ${est:.4f}, spent so far ${running:.4f}, budget ${a.max_usd:.4f}")
    client = op.OpenAIImages()
    for i, s in enumerate(todo, 1):
        j = job(s, cfg)
        e = op.estimate_job(j, cfg)
        if running + e["usd"] > a.max_usd + 1e-9:
            sys.exit(f"stop before {s}: ${running:.4f} spent + ${e['usd']:.4f} would pass ${a.max_usd:.4f}")
        rec = {"position": s, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "pre_estimate_usd": e["usd"]}
        try:
            rid, png, usage = client.generate(j, cfg)
        except op.ApiError as exc:
            rec.update(status="error", error=str(exc)[:300], usd=e["usd"] if exc.billed else 0.0)
            log(rec); running += rec["usd"]
            print(f"PROGRESS {i}/{len(todo)} {s} failed: {exc}")
            continue
        usd = op.usage_cost(usage, cfg)
        out = library.free_name(FOLDER, f"book-blank-{s}", ".png")
        out.write_bytes(png)
        rec.update(status="ok", usd=usd, request_id=rid, usage=usage, file=out.name)
        log(rec); running += usd
        library.put({"file": str(out.relative_to(library.POOL)), "kind": "template", "about": "Blank LumeBook book template: " + POSITIONS[s][1],
                     "position": s, "key": library.key_of(j["input"]["prompt"]), "prompt": j["input"]["prompt"],
                     "cost_usd": usd, "model": cfg["model"], "size": cfg["size"], "quality": cfg["quality"]})
        print(f"PROGRESS {i}/{len(todo)} {s} -> {out.relative_to(ROOT)}  ${usd:.4f}  (total ${running:.4f} of ${a.max_usd:.4f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("run"); p.add_argument("slugs", nargs="*"); p.add_argument("--again", action="store_true")
    p.add_argument("--max-usd", type=float); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_run)
    a = ap.parse_args()
    a.fn(a)
