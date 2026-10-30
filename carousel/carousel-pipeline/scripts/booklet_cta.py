#!/usr/bin/env python3
"""Move a produced carousel to the book link CTA over the open booklet (Yarin, 30 Oct 2026: "אפשר גם לעזור להם עם X
בעזרת ספר מותאם אישית / תכתבו X ואשלח לכם קישור להכנת הספר", the booklet with the child's photo in a circle and an arrow
at each face, then "great implement in novembers batch"). story-format.md section 7.

    python3 booklet_cta.py RUN_DIR --problem "הגמילה מהמוצץ" --word מוצץ \\
        --page "רוני נפרדה מהמוצץ,|והארנב נשאר איתה|כל הלילה." --crop 134,192,950,516 --face .22,.48
    python3 booklet_cta.py --spec ../booklets-2026-11.json [RUN_ID ...]     # every run in a spec file (or the ones named)
    python3 booklet_cta.py --prompts "sitting on her bed hugging the bunny"  # the two fal prompts for a run's scene

Needs RUN_DIR/booklet/booklet.png (the open book from above, left page an illustration of the child in the topic's scene,
right page blank) and RUN_DIR/booklet/kid.png (a realistic close-up of the child's face). Both come from fal
nano-banana-2/edit with the run's cover picture (generated-assets/slide-01.png) as the reference: PROMPTS below.
--crop is the spread's two pages inside booklet.png (x, y, w, h in pixels), --face the child's face in the left page
illustration as a share of that crop (x, y from 0 to 1); the arrow points at it.

Steps: the old approved.json, pack option and last slide go to versions/booklet-N/; the CTA (two sentences), the last
slide, the caption's last two lines, post_text (📖 on the CTA line), code_word, cta_style "book_link" and `booklet` are
written into approved.json and the draft pack's option; the pack is validated (nothing is exported if it fails) and
only the last slide is re-exported (contact sheet, caption and ZIP refreshed). Images of the other slides are untouched.
Postiz is never touched: a carousel already queued there keeps its old slides until it is scheduled again.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent

PROMPTS = {
    "booklet": ("A realistic product photograph, shot straight from above, of an open square children's picture book. The two "
                "open pages fill the entire image edge to edge: no table, no background and no cover edges are visible around the "
                "book. The LEFT page is one full-page 3D animated feature film style illustration of the same child as in the "
                "reference image (same face, hair, skin tone and clothes), {scene}. The child's face is large, clearly visible and "
                "turned toward the viewer. Warm soft light. The RIGHT page is completely blank plain white paper with no text, no "
                "lines, no drawings and no page number. A soft shadow along the spine in the middle. Absolutely no text, letters or "
                "numbers anywhere in the image."),
    "kid": ("A natural realistic photograph of a real child who looks like the child in the reference image: same age, same hair "
            "colour and hairstyle, same skin tone and eye colour. A tight close-up of the face only: the face is centred and fills "
            "most of the square frame, looking straight at the camera with a soft natural smile. Soft daylight, softly blurred "
            "plain home background. A real photo, not an illustration. No text."),
}
FAL = {"endpoint": "fal-ai/nano-banana-2/edit", "booklet_aspect": "16:9", "kid_aspect": "1:1"}


def find_option(pack, oid):
    for d in pack.get("directions", []):
        for v in d.get("versions", []):
            if v.get("id") == oid:
                return v
    raise SystemExit(f"option {oid} is not in the pack")


def move_option(v, problem, word, page, crop, face):
    """Write the book link CTA and the booklet into one option (approved.json's or the pack's)."""
    old = v.get("cta", "")
    cta = lib.book_link_cta(problem, word, v.get("addressee"))
    gone = {lib.collapse(old)} | {lib.collapse(ln) for ln in lib.lines_of(old)} | {lib.collapse(ln) for ln in lib.lines_of(cta)}
    body = [ln for ln in lib.lines_of(v.get("caption", "")) if lib.collapse(ln) not in gone]
    v["cta_style"] = lib.BOOK_LINK_STYLE
    v["cta"] = cta
    v["code_word"] = word
    v["caption"] = "\n".join(body + lib.lines_of(cta))
    head, text = lib.book_link_slide(cta)
    v["slides"][-1]["headline"], v["slides"][-1]["body"] = head, text
    v["slides"][-1].pop("highlight", None)
    v["booklet"] = {"page_text": page, "crop": crop, "face": face}
    v["post_text"] = lib.post_texts(v, template=v.get("post_text") or {})


def apply(run_dir, problem, word, page, crop, face):
    run_dir = Path(run_dir).resolve()
    for name in ("booklet.png", "kid.png"):
        if not (run_dir / "booklet" / name).exists():
            raise SystemExit(f"{run_dir / 'booklet' / name} is missing (fal nano-banana-2/edit, see --prompts)")
    frozen = lib.read_json(run_dir / "approved.json")
    date, oid = frozen["date"], frozen["option"]["id"]
    pack_path = lib.DRAFTS / date / "pack.json"
    pack = lib.read_json(pack_path)
    pv = find_option(pack, oid)
    last = len(frozen["option"]["slides"])

    n = 1 + max([int(p.name.split("-")[1]) for p in (run_dir / "versions").glob("booklet-*")] or [0])
    backup = run_dir / "versions" / f"booklet-{n}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_dir / "approved.json", backup / "approved.json")
    lib.write_json(backup / "pack-option.json", pv)
    if (run_dir / "final" / f"{last:02d}.png").exists():
        shutil.copy2(run_dir / "final" / f"{last:02d}.png", backup / f"{last:02d}.png")

    move_option(frozen["option"], problem, word, page, crop, face)
    move_option(pv, problem, word, page, crop, face)
    tmp = backup / "pack.json"   # validated before anything is written back
    lib.write_json(tmp, pack)
    res = subprocess.run([sys.executable, str(SCRIPTS / "validate_pack.py"), str(tmp), "--json", "--no-history"], capture_output=True, text=True)
    report = json.loads(res.stdout)
    mine = [e for e in report["errors"] if f"/{oid}/" in e.get("path", "") or e.get("path", "").endswith(f"/{oid}")
            or "/code_word" in e.get("path", "")]
    if mine or not report["valid"]:
        print(json.dumps({"run": run_dir.name, "valid": False, "errors": mine or report["errors"][:10], "backup": str(backup)}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    tmp.unlink()
    lib.write_json(pack_path, pack)
    lib.write_json(run_dir / "approved.json", frozen)

    out = subprocess.run([sys.executable, str(SCRIPTS / "compose_slides.py"), str(run_dir), "--slides", str(last)], capture_output=True, text=True)
    if out.returncode != 0:
        print(out.stdout[-2000:], out.stderr[-2000:])
        raise SystemExit(f"{run_dir.name}: export failed (approved.json and the pack are already moved; backup in {backup})")
    result = json.loads(out.stdout)
    return {"run": run_dir.name, "cta": lib.collapse(frozen["option"]["cta"]), "slide": result["slides"][-1],
            "rtl_problems": result["rtl_problems"], "backup": str(backup)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", nargs="?")
    ap.add_argument("--problem")
    ap.add_argument("--word")
    ap.add_argument("--page", help="the booklet page, lines split by |")
    ap.add_argument("--crop", help="x,y,w,h of the two pages inside booklet.png")
    ap.add_argument("--face", help="x,y of the child's face inside the crop, 0 to 1")
    ap.add_argument("--spec", help="a JSON file {RUN_ID: {problem, word, page_text, crop, face}}")
    ap.add_argument("--prompts", metavar="SCENE", help="print the two fal prompts for this scene and stop")
    args, rest = ap.parse_known_args()
    if args.prompts:
        print(json.dumps({"endpoint": FAL["endpoint"], "booklet": {"prompt": PROMPTS["booklet"].format(scene=args.prompts), "aspect_ratio": FAL["booklet_aspect"]},
                          "kid": {"prompt": PROMPTS["kid"], "aspect_ratio": FAL["kid_aspect"]}}, ensure_ascii=False, indent=2))
        return
    jobs = []
    if args.spec:
        spec = {k: v for k, v in lib.read_json(args.spec).items() if not k.startswith("_")}
        names = ([args.run_dir] if args.run_dir else []) + rest
        for rid, s in spec.items():
            if names and rid not in names:
                continue
            jobs.append((lib.APPROVED / rid, s["problem"], s["word"], s["page_text"], s["crop"], s["face"]))
    else:
        if not (args.run_dir and args.problem and args.word and args.page and args.crop and args.face):
            raise SystemExit("pass RUN_DIR with --problem --word --page --crop --face, or --spec")
        jobs.append((args.run_dir, args.problem, args.word, args.page.split("|"), [int(x) for x in args.crop.split(",")],
                     [float(x) for x in args.face.split(",")]))
    results = [apply(*j) for j in jobs]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
