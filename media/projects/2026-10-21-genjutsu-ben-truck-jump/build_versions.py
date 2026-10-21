"""Five caption versions of ben-truck-jump-v1 (original audio kept), for Instagram trial reels.
Run: <python with Pillow> build_versions.py   (the watch-video .venv has Pillow)
Each version gets its own random horizontal flip and one slight steady zoom (seeded, recorded in versions.json),
so the five uploads are not frame-identical. The caption is never flipped.
Caption look follows 2026-10-19-genjutsu-ben-dance-lume/build_versions.py: SF Hebrew Bold, white, soft shadow,
but it starts at y 290, below the top 14% of the frame (Reels safe zone, research/israeli-product-reels/playbook.md)."""
import json, random, re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
SRC = HERE / "ben-truck-jump-v1-480p.mp4"
AUDIO = HERE / "ben-truck-jump-v1-480p-sound.mp4"
copy = json.load(open(HERE / "captions.json"))
TMP = HERE / "_cards"; TMP.mkdir(exist_ok=True)
SF = "/System/Library/Fonts/SFHebrew.ttf"
SF_LATIN = "/System/Library/Fonts/SFNS.ttf"  # SF Hebrew has no Latin letters or "?"; SF Pro supplies them
W, H, FPS, IN_W, IN_H = 1080, 1920, 24, 480, 854

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

EMOJI = re.compile(r"[\U0001F300-\U0001FAFF]$")
def emoji_img(ch, px):
    f = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 160)  # the only bitmap size
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    return im.crop(im.getbbox()).resize((px, px), Image.LANCZOS)

def card(key, size=64, top=290, max_w=900):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    text = copy[key]
    m = EMOJI.search(text); emo_ch = m.group(0) if m else None
    if emo_ch: text = text[:-len(emo_ch)].rstrip()
    lines = [visual(l) for l in text.split("\n")]
    f = font(size)
    while max(width(d, l, f) for l in lines) + 80 > max_w:
        size -= 2; f = font(size)
    h = int(size * 1.22)
    emo = emoji_img(emo_ch, int(size * 1.0)) if emo_ch else None
    gap = int(size * 0.18)
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    for i, vis in enumerate(lines):
        extra = gap + emo.width if (emo and i == len(lines) - 1) else 0  # emoji ends the sentence = left end of the last line
        tw = width(d, vis, f); total = tw + extra
        x = (W - total) / 2 + extra; y = top + i * h
        if extra:
            im.alpha_composite(emo, (int((W - total) / 2), int(y + (h - emo.height) / 2 + size * 0.02)))
        draw(sd, (x, y + 3), vis, f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200))
        draw(d, (x, y), vis, f, fill="white")
    out = TMP / f"caption-{key}.png"
    Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)), im).save(out)
    return out, size, top + len(lines) * h

ZOOMS = [1.03, 1.045, 1.06, 1.07, 1.085]
random.Random("ben-truck-zooms").shuffle(ZOOMS)  # one slight zoom per version, no two alike

def plan(key, flip, zoom):
    rng = random.Random(f"ben-truck-{key}")
    # where the crop sits inside the frame: 0 = left/top edge, 1 = right/bottom edge. Vertically only between
    # top and centre, so the zoom never pushes Ben's head up into the caption
    return dict(flip=flip, zoom=round(zoom + rng.uniform(-0.004, 0.004), 3),
                anchor_x=round(rng.uniform(0.3, 0.7), 2), anchor_y=round(rng.uniform(0.0, 0.5), 2))

def box(p):
    z = p["zoom"]; w, h = IN_W / z, IN_H / z
    x0, y0 = (IN_W - w) * p["anchor_x"], (IN_H - h) * p["anchor_y"]
    return (x0, y0, x0 + w, y0 + h)

flips = [True, True, False, False, random.Random("ben-truck-flips").random() < 0.5]
random.Random("ben-truck-order").shuffle(flips)  # random, but never all five the same way
record = {}
for i, key in enumerate(sorted(copy)):
    p = plan(key, flips[i], ZOOMS[i])
    png, size, bottom = card(key)
    cap = Image.open(png)
    out = HERE / "captioned" / f"ben-truck-jump-caption-{key}.mp4"; out.parent.mkdir(exist_ok=True)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(SRC), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", str(AUDIO), "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)],
                           stdin=subprocess.PIPE)
    n = 0
    while True:
        raw = dec.stdout.read(IN_W * IN_H * 3)
        if len(raw) < IN_W * IN_H * 3: break
        fr = Image.frombytes("RGB", (IN_W, IN_H), raw)
        if p["flip"]: fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
        fr = fr.resize((W, H), Image.LANCZOS, box=box(p)).convert("RGBA")
        fr.alpha_composite(cap)
        enc.stdin.write(fr.convert("RGB").tobytes()); n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    record[key] = dict(file=out.name, caption=copy[key], font_px=size, caption_bottom_y=bottom, frames=n, **p)
    print(out.name, "flip" if p["flip"] else "no flip", p["zoom"], p["anchor_x"], p["anchor_y"], f"{size}px")
json.dump(record, open(HERE / "versions.json", "w"), ensure_ascii=False, indent=1)
