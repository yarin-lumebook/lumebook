"""Turn options.json into Carousel Machine run folders (approved.json + state.json + the ChatGPT picture)
and render them with compose_slides.py. Usage: python3 make_runs.py [lotem-1 ...]"""
import json, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPE = HERE.parents[2] / "carousel" / "carousel-pipeline"
VOICE = {"status": "calibrated", "note": "קול מכויל, מבנה לפי @lotem_lerner (29 Oct 2026)"}

opts = {o["id"]: o for o in json.load(open(HERE / "options.json"))}

# the full source records (url, quote, date read) as the November packs checked them, keyed by topic and id
def _options(x):
    if isinstance(x, dict):
        if "slides" in x and "sources" in x:
            yield x
        for v in x.values():
            yield from _options(v)
    elif isinstance(x, list):
        for v in x:
            yield from _options(v)
SRC = {}
for f in sorted((PIPE / "drafts").glob("2026-11-*/pack.json")):
    for o in _options(json.load(open(f))):
        for s in o.get("sources", []):
            SRC.setdefault((o.get("topic_id"), s["id"]), s)
for oid in (sys.argv[1:] or list(opts)):
    o = opts[oid]
    pic = HERE / "pictures" / f"{oid}.png"
    if not pic.exists():
        print(oid, "no picture yet"); continue
    run = HERE / "runs" / oid
    (run / "generated-assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(pic, run / "generated-assets" / "picture.png")
    slides = [dict(s, number=n) for n, s in enumerate(o["slides"], 1)]
    option = {
        "id": oid, "title": slides[0]["headline"].replace("\n", " "), "child_name": o["child_name"],
        "child_gender": o["child_gender"], "addressee": o["addressee"], "character_anchor": o["character_anchor"],
        "image": o["image"], "slides": slides, "caption": o["caption"],
        "cta": slides[-1]["headline"] + "\n" + slides[-1]["body"],
        "sources": [SRC[(o["topic_id"], s.split(" ")[0])] for s in o["sources"]], "claims": [],
    }
    frozen = {"date": "2026-10-29", "topic": {"id": o["topic_id"]}, "direction": "kid", "option_id": oid,
              "source_pack": "media/projects/2026-10-29-lotem-format-carousels/options.json", "voice": VOICE,
              "product_facts": [], "option": option}
    (run / "approved.json").write_text(json.dumps(frozen, ensure_ascii=False, indent=1), encoding="utf-8")
    (run / "state.json").write_text(json.dumps({"jobs": {"picture": {"qa": "pass"}}}), encoding="utf-8")
    r = subprocess.run(["python3", str(PIPE / "scripts" / "compose_slides.py"), str(run), "--look", "clean"],
                       capture_output=True, text=True)
    print(oid, "OK" if r.returncode == 0 else "FAILED", (r.stdout + r.stderr).strip()[-600:])
