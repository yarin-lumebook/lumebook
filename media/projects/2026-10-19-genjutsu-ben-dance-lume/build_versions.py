"""Three caption versions of ben-dance-lume-v1 (original audio kept).
Run: <python with Pillow> build_versions.py
v1: plain.  v2: picture mirrored (caption stays readable).  v3: zoomed 1.08x and sped up from 15 s to 13 s (audio tempo-matched, pitch kept).
Caption look follows 2026-10-14-reel-captions-1014/build.py: SF Hebrew Bold, white, soft shadow, top of the frame."""
import json, re, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
SRC = HERE / "ben-dance-lume-v1-480p-music.mp4"
copy = json.load(open(HERE / "captions.json"))
TMP = HERE / "_cards"; TMP.mkdir(exist_ok=True)
SF = "/System/Library/Fonts/SFHebrew.ttf"
SF_LATIN = "/System/Library/Fonts/SFNS.ttf"  # SF Hebrew has no "?"; SF Pro supplies it

def visual(line):
    return re.sub(r"\d+", lambda m: m.group(0)[::-1], line[::-1])

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

EMOJI = "\U0001F923"  # 🤣 at the end of the sentence = the left end of the last line (RTL)
def emoji_img(px):
    f = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 160)  # the only bitmap size
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), EMOJI, font=f, embedded_color=True)
    return im.crop(im.getbbox()).resize((px, px), Image.LANCZOS)

def card(key, size=64, top=240, max_w=900):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lines = [visual(l) for l in copy[key].split("\n")]
    f = font(size)
    while max(width(d, l, f) for l in lines) + 80 > max_w:
        size -= 2; f = font(size)
    h = int(size * 1.22)
    emo = emoji_img(int(size * 1.0)); gap = int(size * 0.18)
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    for i, vis in enumerate(lines):
        last = i == len(lines) - 1
        tw = width(d, vis, f); total = tw + (gap + emo.width if last else 0)
        x = (1080 - total) / 2 + (gap + emo.width if last else 0); y = top + i * h
        if last:
            ex, ey = int((1080 - total) / 2), int(y + (h - emo.height) / 2 + size * 0.02)
            im.alpha_composite(emo, (ex, ey))
        draw(sd, (x, y + 3), vis, f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200))
        draw(d, (x, y), vis, f, fill="white")
    out = TMP / f"{key}.png"
    Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)), im).save(out)
    return out

BASE = "scale=1080:1920:flags=lanczos,setsar=1"
VERSIONS = {
    "v1": dict(vf=BASE, af="anull", out="ben-dance-lume-caption-1.mp4"),
    "v2": dict(vf="hflip," + BASE, af="anull", out="ben-dance-lume-caption-2-mirrored.mp4"),
    "v3": dict(vf="crop=iw/1.08:ih/1.08,setpts=PTS*13/15," + BASE, af="atempo=1.153846", out="ben-dance-lume-caption-3-zoom-13s.mp4"),
}
for key, v in VERSIONS.items():
    png = card(key)
    fc = f"[0:v]{v['vf']}[b];[b][1:v]overlay[vout];[0:a]{v['af']}[aout]"
    out = HERE / v["out"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-t", "15", "-i", str(SRC), "-i", str(png),
                    "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "16",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(out)], check=True, stdin=subprocess.DEVNULL)
    print(out.name, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate,duration",
          "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.replace("\n", " "))
