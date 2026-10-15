"""Reel 4 from Yarin's upscaled 1014.mp4: three caption versions, original audio, CTA freeze.
Run: <python with Pillow> build.py <captions.json> [versions to flip, e.g. 2]
A flipped version mirrors the picture only (captions stay readable) and is saved as reel-1014-caption-N-flipped.mp4."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
PIC = HERE / "source/1014.mp4"   # 13.2 s, the clean reel-4 picture (no text), upscaled to 2160x3830
AUD = ROOT / "media/projects/2026-10-13-reels-superhero-book/source/whatsapp-2026-10-13-reading-session.mp4"
FONT = str(ROOT / "shared/brand/fonts/Heebo-Black.ttf")
copy = json.load(open(sys.argv[1]))
FLIP = {int(v) for v in sys.argv[2:]}
TMP = HERE / "_cards"; TMP.mkdir(exist_ok=True)

def visual(line):
    # Hebrew right-to-left: reverse the line, then put digit runs back in reading order
    return re.sub(r"\d+", lambda m: m.group(0)[::-1], line[::-1])

SF = "/System/Library/Fonts/SFHebrew.ttf"  # Apple's system Hebrew face, bold: closest local match to Instagram's plain text style

SF_LATIN = "/System/Library/Fonts/SFNS.ttf"  # SF Hebrew has no digits, hyphen or question mark; SF Pro supplies them

def font(size):
    he = ImageFont.truetype(SF, size); he.set_variation_by_name("Bold")
    la = ImageFont.truetype(SF_LATIN, size); la.set_variation_by_name("Bold")
    return he, la

MISSING = None
def runs(vis, fonts):
    """Split a visual-order line into (text, font) runs, sending glyphs SF Hebrew lacks to SF Pro."""
    global MISSING
    he, la = fonts
    if MISSING is None:
        tofu = bytes(he.getmask("\U000F0000"))
        MISSING = lambda c: c != " " and bytes(he.getmask(c)) == tofu
    out = []
    for c in vis:
        f = la if MISSING(c) else he
        if out and out[-1][1] is f: out[-1][0] += c
        else: out.append([c, f])
    return out

def width(d, vis, fonts):
    return sum(d.textlength(t, font=f) for t, f in runs(vis, fonts))

def draw(d, xy, vis, fonts, **kw):
    x, y = xy
    for t, f in runs(vis, fonts):
        d.text((x, y), t, font=f, **kw); x += d.textlength(t, font=f)

def card(key, size, top=None, bottom=None, max_w=900):
    """White bold text, no box, soft shadow for legibility on the white wall. Anchor by top or bottom edge."""
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lines = [visual(l) for l in copy[key].split("\n")]
    assert len(lines) <= 3 or not key.startswith("hook"), f"{key} has more than 3 lines"
    f = font(size)
    while max(width(d, l, f) for l in lines) > max_w:
        size -= 2; f = font(size)
    h = int(size * 1.22)
    y0 = top if top is not None else bottom - len(lines) * h
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    for i, vis in enumerate(lines):
        w = width(d, vis, f); x = (1080 - w) / 2; y = y0 + i * h
        draw(sd, (x, y + 3), vis, f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200))
        draw(d, (x, y), vis, f, fill="white")
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    out = TMP / f"{key}.png"; Image.alpha_composite(shadow, im).save(out); return out

norm = "setpts=PTS-STARTPTS,scale=1084:1920:flags=lanczos,crop=1080:1920,setsar=1"
fc_pic = (f"[0:v]trim=0:5.7,{norm}[v0];"
          f"[0:v]trim=5.7:9.7,setpts=PTS-STARTPTS,crop=1800:3192:74:120,scale=1080:1920:flags=lanczos,setsar=1[v1];"
          f"[0:v]trim=9.7:12.2,{norm}[v2];"
          f"[0:v]trim=12.2:13.2,{norm},tpad=stop_mode=clone:stop_duration=2.2[v3];")
fc_aud = ""
for i, (s, ae, vdur) in enumerate([(5.8, 11.5, 5.7), (16.5, 20.5, 4.0), (28.5, 31.0, 2.5), (162.6, 165.2, 3.2)]):
    fo = 0.6 if i == 3 else 0.05
    fc_aud += (f"[1:a]atrim={s}:{ae},asetpts=PTS-STARTPTS,apad=whole_dur={vdur},atrim=0:{vdur},"
               f"afade=t=in:d=0.05,afade=t=out:st={vdur - fo:.2f}:d={fo}[a{i}];")
fc_join = ("[v0][a0][v1][a1][v2][a2][v3][a3]concat=n=4:v=1:a=1[pic][araw];"
           "[araw]highpass=f=80,afftdn=nf=-25,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[aout];")

BOTTOM = 1560  # bottom edge of the lower text, above Instagram's caption and buttons
shared = {"beat2": card("beat2", 70, bottom=BOTTOM), "beat3": card("beat3", 66, bottom=BOTTOM),
          "beat4": card("beat4", 66, bottom=BOTTOM), "cta": card("cta", 62, bottom=BOTTOM)}
for n in sorted(FLIP) if FLIP else (1, 2, 3):
    hook = card(f"hook{n}", 64, top=240)  # stays on screen the whole reel
    times = [(hook, 0, 15.42), (shared["beat2"], 3.8, 5.7), (shared["beat3"], 5.7, 9.7),
             (shared["beat4"], 9.7, 12.2), (shared["cta"], 12.2, 15.4)]
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(PIC), "-i", str(AUD)]
    fc = fc_pic + fc_aud + fc_join + ("[pic]hflip[b0];" if n in FLIP else "[pic]null[b0];")
    for k, (png, a, b) in enumerate(times):
        cmd += ["-i", str(png)]
        fc += f"[b{k}][{k+2}:v]overlay=enable='between(t,{a},{b-0.02})'[b{k+1}];"
    out = HERE / (f"reel-1014-caption-{n}-flipped.mp4" if n in FLIP else f"reel-1014-caption-{n}.mp4")
    cmd += ["-filter_complex", fc.rstrip(";"), "-map", "[b5]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(out.name, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate,duration",
          "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.replace("\n", " "))
