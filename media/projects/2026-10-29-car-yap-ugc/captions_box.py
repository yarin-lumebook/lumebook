"""Burned-in hook at the top, plus full-sentence captions in a white box that hides the kid's name on the book.

Reads work/name-track.json (track_name.py, un-zoomed coordinates) and maps the name through the slow push-in
(zoom_cuts.py). Each sentence gets one box, always centred on the screen (Yarin, 29 Oct 2026); it widens evenly
on both sides until it covers every tracked spot of the name during that sentence, inside the side margins and
above the variant's floor (take 2: Instagram's safe line). On the fal take the name sits at the left edge,
under the safe line, so its boxes run the full width, lower down, with square ends. Since the evening of
29 Oct 2026 Yarin wants the fal take without captions (variants.py captions=False): hook and push-in only.
The hook uses the reel editor's style (SF Hebrew Bold, white, soft shadow, 15% line).
Run with the watch-video Python (Pillow with the SF Hebrew font):
  ~/.claude/skills/watch-video/.venv/bin/python captions_box.py [higgsfield|fal]  ->  the variant's final mp4
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / ".claude/skills/reel-editor/scripts"))
from reel_editor import font, visual, width, draw, lint, block   # same font and RTL handling as the reel editor
from zoom_cuts import to_zoomed, W, H
from variants import V

OUT, ZOOMED, CUTS = V["final"], V["zoomed"], V.get("sentences")   # sentence k runs from frame CUTS[k] to CUTS[k + 1] - 1
HOOK = "הבן שלי הגיבור של ספר אמיתי\nואני עדיין בהלם"   # voice_lint PASS, 29 Oct 2026
SENTENCES = ["בנות, עצרתי באוטו\nכי אני חייבת להראות לכן.",
             "העליתי תמונה אחת של הבן שלי,\nותראו מה יצא.",
             "זה הוא, עם השם שלו,\nבתוך ספר אמיתי.",
             "תגידו לי שזה לא מטורף."] if V.get("captions", True) else []
SIZE, PAD_X, PAD_Y, RADIUS, HOOK_SIZE = 58, 36, 20, 24, 64
NAME_PAD_X, NAME_PAD_Y = 22, 16           # keep the box this far past the name on every side
SIDE, TOP, BOTTOM = int(W * V.get("side", 0.06)), int(H * 0.15), int(H * V.get("floor", 0.65))
MIN_SCORE = 0.75                          # weaker matches are skipped (one frame at a cut)

lint([("hook", HOOK)] + [(f"caption {i + 1}", s) for i, s in enumerate(SENTENCES)])
track = json.load(open(V["track"])) if SENTENCES else []
work = Path(V["boxes"]); work.mkdir(parents=True, exist_ok=True)

# hook: white text with the reel editor's blurred shadow, on screen the whole time
im, sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)), Image.new("RGBA", (W, H), (0, 0, 0, 0))
hook_lay = block(im, sh, HOOK, HOOK_SIZE, work, top=TOP)
Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), im).save(work / "hook.png")
inputs, chain = ["-loop", "1", "-i", str(work / "hook.png")], ["[0:v][1:v]overlay=0:0[v0]"]
report = [f"hook: {hook_lay['px']}px, y {hook_lay['y']}"]

for k, text in enumerate(SENTENCES):
    a, b = CUTS[k], CUTS[k + 1]
    names = []
    for n in range(a, b):
        f = track[n]
        if f["score"] < MIN_SCORE: continue
        x0, y0 = to_zoomed(f["name"][0], f["name"][1], n); x1, y1 = to_zoomed(f["name"][2], f["name"][3], n)
        names.append((x0, y0, x1, y1))
    ux0 = max(0, min(v[0] for v in names) - NAME_PAD_X); uy0 = min(v[1] for v in names) - NAME_PAD_Y
    ux1 = min(W, max(v[2] for v in names) + NAME_PAD_X); uy1 = max(v[3] for v in names) + NAME_PAD_Y

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(SIZE); lines = [visual(l) for l in text.split("\n")]; lh = int(SIZE * 1.22)
    bw = max(max(width(d, l, f) for l in lines) + 2 * PAD_X, 2 * (W / 2 - ux0), 2 * (ux1 - W / 2))
    bw = min(bw, W - 2 * SIDE)
    if bw > W - 2 * RADIUS: bw = W                                   # nearly edge to edge: go all the way
    bh = max(len(lines) * lh + 2 * PAD_Y, uy1 - uy0)
    bx0 = W / 2 - bw / 2                                            # always centred
    by0 = max(TOP, min((uy0 + uy1) / 2 - bh / 2, BOTTOM - bh))
    box = [bx0, by0, bx0 + bw, by0 + bh]
    covered = box[0] <= ux0 + .5 and box[1] <= uy0 + .5 and box[2] >= ux1 - .5 and box[3] >= uy1 - .5
    d.rounded_rectangle(box, RADIUS if bw < W else 0, fill=(255, 255, 255, 255))   # edge to edge: square ends
    ty = by0 + (bh - len(lines) * lh) / 2 - SIZE * 0.08
    for i, l in enumerate(lines):
        draw(d, (W / 2 - width(d, l, f) / 2, ty + i * lh), l, f, fill=(17, 17, 17, 255))
    png = work / f"sentence-{k + 1}.png"; im.save(png)
    inputs += ["-loop", "1", "-i", str(png)]
    chain.append(f"[v{k}][{k + 2}:v]overlay=0:0:enable='between(n,{a},{b - 1})'[v{k + 1}]")
    report.append(f"sentence {k + 1} frames {a}-{b - 1}: box {[round(v) for v in box]}, name area "
                  f"{[round(v) for v in (ux0, uy0, ux1, uy1)]}, {len(names)}/{b - a} frames tracked, "
                  f"{'covered' if covered else 'NOT COVERED'}")

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ZOOMED, *inputs, "-filter_complex", ";".join(chain),
                "-map", f"[v{len(SENTENCES)}]", "-map", "0:a", "-t", "10", "-c:v", "libx264", "-crf", "17",
                "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", "-map_metadata", "-1",
                "-movflags", "+faststart", OUT], check=True)
print("\n".join(report)); print(OUT)
