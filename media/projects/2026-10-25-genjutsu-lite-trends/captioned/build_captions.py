"""Caption versions of one Genjutsu Lite reel (sound version): Yarin's hooks of 25 Oct 2026 for 02-ben-window,
of 26 Oct for 03-mom-fridge, 04-lume-books-dance and 05-ben-lume-dance.
Run: <python with Pillow> build_captions.py [--reel=03-mom-fridge]   (default 02-ben-window; the watch-video .venv has Pillow)
Top: each hook from <reel without number>-captions.json (e.g. mom-fridge-captions.json), starting at y 290, below the top 14% of the frame.
Bottom: "_bottom" ("הסבר בתיאור👇🏻"), its baseline at the lowest safe line (65% of the height; the bottom 35%
is covered by Instagram's buttons and caption, research/israeli-product-reels/playbook.md).
Look follows 2026-10-21-genjutsu-ben-truck-jump/build_versions.py: SF Hebrew Bold, white, soft shadow.
Plain run: no flip or zoom. `--trial` writes trial/ versions with a seeded flip and slight zoom (see below);
a flipped picture mirrors the Hebrew title on Ben's book, the captions stay readable.
Emoji are drawn by macOS (emoji_png.swift), because Pillow here has no raqm and splits skin-tone sequences."""
import json, random, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
REEL = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--reel=")), "02-ben-window")
NAME = REEL.split("-", 1)[1]
SRC = HERE.parent / "results" / f"{REEL}-v1-1080p-sound.mp4"
copy = json.load(open(HERE / f"{NAME}-captions.json"))
TMP = HERE / "_cards"; TMP.mkdir(exist_ok=True)
SF = "/System/Library/Fonts/SFHebrew.ttf"
SF_LATIN = "/System/Library/Fonts/SFNS.ttf"  # SF Hebrew has no Latin letters; SF Pro supplies them
W, H = 1080, 1920
TOP, SAFE_BOTTOM = 290, int(H * 0.65)

def visual(line):
    # RTL line drawn left to right: reverse it, then put Latin words and numbers back in reading order
    return re.sub(r"[A-Za-z0-9]+", lambda m: m.group(0)[::-1], line[::-1])

def font(size):
    he = ImageFont.truetype(SF, size); he.set_variation_by_name("Bold")
    la = ImageFont.truetype(SF_LATIN, size); la.set_variation_by_name("Bold")
    return he, la

_tofu = None
def runs(vis, fonts):
    global _tofu
    he, la = fonts
    if _tofu is None: _tofu = bytes(he.getmask("\U000F0000"))
    out = []
    for c in vis:
        f = la if (c != " " and bytes(he.getmask(c)) == _tofu) else he
        if out and out[-1][1] is f: out[-1][0] += c
        else: out.append([c, f])
    return out

def width(d, vis, fonts): return sum(d.textlength(t, font=f) for t, f in runs(vis, fonts))
def draw(d, xy, vis, fonts, **kw):
    x, y = xy
    for t, f in runs(vis, fonts):
        d.text((x, y), t, font=f, **kw); x += d.textlength(t, font=f)

EMOJI = re.compile(r"[\U0001F300-\U0001FAFF][\U0001F3FB-\U0001F3FF]?$")
def emoji_img(seq, px):
    png = TMP / f"emoji-{'-'.join(f'{ord(c):x}' for c in seq)}.png"
    if not png.exists():
        subprocess.run(["swift", str(HERE / "emoji_png.swift"), seq, str(png), "160"], check=True)
    im = Image.open(png).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * px / im.height), px), Image.LANCZOS)

def block(im, shadow, text, size, top=None, bottom=None, max_w=900):
    """Draw centred RTL lines; an emoji at the end of the text goes at the left end of the last line."""
    d = ImageDraw.Draw(im); sd = ImageDraw.Draw(shadow)
    m = EMOJI.search(text); emo_seq = m.group(0) if m else None
    if emo_seq: text = text[:-len(emo_seq)].rstrip()
    lines = [visual(l) for l in text.split("\n")]
    f = font(size)
    while max(width(d, l, f) for l in lines) + 80 > max_w:
        size -= 2; f = font(size)
    h = int(size * 1.22)
    if top is None: top = bottom - len(lines) * h
    emo = emoji_img(emo_seq, int(size * 1.05)) if emo_seq else None
    gap = int(size * 0.18)
    for i, vis in enumerate(lines):
        extra = gap + emo.width if (emo and i == len(lines) - 1) else 0
        tw = width(d, vis, f); total = tw + extra
        x = (W - total) / 2 + extra; y = top + i * h
        if extra:
            im.alpha_composite(emo, (int((W - total) / 2), int(y + (h - emo.height) / 2 + size * 0.04)))
        draw(sd, (x, y + 3), vis, f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200))
        draw(d, (x, y), vis, f, fill="white")
    return size, top, top + len(lines) * h

# --trial (Yarin, 25 Oct 2026): the same five for Instagram trial reels, each with its own seeded horizontal flip
# (some flipped, never all the same way) and one slight steady zoom (no two alike), like the 21 Oct truck reel.
# The picture is flipped and zoomed first, the captions go on top, so the text is never mirrored. The zoom crop sits
# anywhere sideways but only between the top and the centre vertically, so Ben's head never rises into the hook.
TRIAL = "--trial" in sys.argv
keys = sorted(k for k in copy if not k.startswith("_"))
ZOOMS = [1.03, 1.045, 1.06, 1.07, 1.085]
random.Random("ben-window-zooms").shuffle(ZOOMS)
flips = [True, True, False, False, random.Random("ben-window-flips").random() < 0.5]
random.Random("ben-window-order").shuffle(flips)

# Also a small speed change (audio tempo-matched, pitch kept) and a few frames trimmed at each end, so the
# five differ in length too (Yarin, 25 Oct 2026: "nothing substantial").
SPEEDS = [0.96, 0.98, 1.02, 1.035, 1.05]
random.Random("ben-window-speeds").shuffle(SPEEDS)

def picture_filter(i, key):
    if not TRIAL: return "[0:v]null[p]", "[0:a]anull[a]", {}
    rng = random.Random(f"ben-window-{key}")
    p = dict(flip=flips[i], zoom=round(ZOOMS[i] + rng.uniform(-0.004, 0.004), 3),
             anchor_x=round(rng.uniform(0.3, 0.7), 2), anchor_y=round(rng.uniform(0.0, 0.5), 2),
             speed=round(SPEEDS[i] + rng.uniform(-0.005, 0.005), 3),
             trim_start=round(rng.uniform(0.0, 0.25), 2), trim_end=round(rng.uniform(0.05, 0.35), 2))
    cw, ch = int(W / p["zoom"]) // 2 * 2, int(H / p["zoom"]) // 2 * 2
    x, y = int((W - cw) * p["anchor_x"]), int((H - ch) * p["anchor_y"])
    flip = "hflip," if p["flip"] else ""
    s, e = p["trim_start"], DUR - p["trim_end"]
    v = (f"[0:v]trim={s}:{e},setpts=(PTS-STARTPTS)/{p['speed']},{flip}crop={cw}:{ch}:{x}:{y},"
         f"scale={W}:{H}:flags=lanczos,setsar=1[p]")
    a = f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,atempo={p['speed']},afade=t=out:st={(e - s) / p['speed'] - 0.3:.2f}:d=0.3[a]"
    p["length_s"] = round((e - s) / p["speed"], 2)
    return v, a, p

DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(SRC)],
                           capture_output=True, text=True).stdout)

out_dir = HERE / "trial" if TRIAL else HERE
out_dir.mkdir(exist_ok=True)
record = {}
for i, key in enumerate(keys):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hook_px, hook_top, hook_bottom = block(im, shadow, copy[key], 64, top=TOP)
    # "_bottom" is optional: Yarin dropped "הסבר בתיאור👇🏻" from every reel on 26 Oct 2026
    low_px, low_top, low_bottom = (block(im, shadow, copy["_bottom"], 54, bottom=SAFE_BOTTOM)
                                   if copy.get("_bottom") else (None, None, None))
    card = TMP / f"caption-{NAME}-{key}.png"
    Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)), im).save(card)
    pic, aud, p = picture_filter(i, key)
    out = out_dir / (f"{REEL}-trial-{key}.mp4" if TRIAL else f"{REEL}-caption-{key}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-i", str(card),
                    "-filter_complex", f"{pic};[p][1:v]overlay=0:0:format=auto,format=yuv420p[v];{aud}",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-r", "24", "-movflags", "+faststart", str(out)], check=True)
    record[key] = dict(file=out.name, hook=copy[key], bottom=copy.get("_bottom"), hook_px=hook_px,
                       hook_y=[hook_top, hook_bottom], bottom_px=low_px, bottom_y=[low_top, low_bottom], **p)
    print(out.name, f"hook {hook_px}px y {hook_top}-{hook_bottom}", f"bottom {low_px}px y {low_top}-{low_bottom}",
          ("flip" if p.get("flip") else "no flip") if TRIAL else "", p.get("zoom", ""))
json.dump(record, open(out_dir / f"{NAME}-versions.json", "w"), ensure_ascii=False, indent=1)
