"""Grandma baking book reel (24 Oct 2026): concept 5 of research/israeli-product-reels/playbook.md
("מתנה לנכד שאין לאף ילד אחר"), cut from the 11 Oct physical-book close-ups in Drive
(שיווק / חומרי גלם / ספרים פיזיים / 2026-10-11 תקריבים) with an ElevenLabs v4 voiceover from 0:00.
Run: ~/.claude/skills/watch-video/.venv/bin/python build.py [sarah|matilda]   (that venv has Pillow)
Needs work/sdr/clipNN.mov first: the iPhone clips are HLG HDR and this ffmpeg has no tone mapping, so
they are converted with macOS avconvert (Preset1920x1080), see README.md.
Text stays inside the Reels safe zone (below the top 14%, above the bottom 35%, 6% from the sides)."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
SDR, WORK = HERE / "work" / "sdr", HERE / "work"
CARDS = WORK / "cards"; CARDS.mkdir(parents=True, exist_ok=True)
FONT = HERE.parents[2] / "shared" / "brand" / "fonts" / "Heebo-Bold.ttf"
W, H, FPS = 1080, 1920, 30
SAFE_TOP, SAFE_BOTTOM = int(H * 0.14), int(H * 0.65)
TINT = (91, 43, 214)  # --tint in shared/design/lumebook.css
TAIL = 1.75           # seconds of end card after the last word

# Where each voice's beats change, read from the ElevenLabs character timestamps (pause midpoints).
VOICES = {
    "sarah": {"file": "audio/vo-sarah.mp3", "end": 21.44, "cuts": [3.2, 5.95, 8.0, 10.85, 14.45, 18.3]},
    "matilda": {"file": "audio/vo-matilda.mp3", "end": 22.16, "cuts": [3.1, 5.95, 8.1, 11.05, 14.75, 19.0]},
}
copy = json.load(open(HERE / "copy.json"))


def visual(line):
    # RTL line drawn left to right: reverse it, then put numbers back in reading order
    return re.sub(r"[0-9]+", lambda m: m.group(0)[::-1], line[::-1])


def card(key, size, y_center):
    lines = [visual(l) for l in copy[key].split("\n")]
    font = ImageFont.truetype(str(FONT), size)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lh, pad_x, pad_y = int(size * 1.28), int(size * 0.62), int(size * 0.34)
    tw = max(probe.textlength(l, font=font) for l in lines)
    bw, bh = int(tw + 2 * pad_x), lh * len(lines) + 2 * pad_y
    assert bw <= W * 0.88, f"{key} too wide"
    x0, y0 = (W - bw) // 2, int(y_center - bh / 2)
    assert SAFE_TOP <= y0 and y0 + bh <= SAFE_BOTTOM, f"{key} outside the safe zone"
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0, y0 + 8, x0 + bw, y0 + bh + 8), 30, fill=(0, 0, 0, 110))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 30, fill=TINT + (240,))
    for i, l in enumerate(lines):
        y = y0 + pad_y + i * lh + (lh - size) / 2 - size * 0.12
        d.text(((W - probe.textlength(l, font=font)) / 2, y), l, font=font, fill="white")
    out = CARDS / f"{key}.png"
    im.save(out)
    return out


def run(cmd):
    subprocess.run(cmd, check=True)


def segment(out, src, start, src_dur, dur, rotate=False, window=None):
    # window = (f, x0, y0): keep a 9:16 box f of the frame high from (x0, y0), e.g. to drop burned-in captions
    crop = f"crop=iw*{window[0]}:ih*{window[0]}:iw*{window[1]}:ih*{window[2]}," if window else ""
    vf = ("transpose=1," if rotate else "") + crop + f"setpts={dur / src_dur:.5f}*PTS," + \
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(src_dur), "-i", str(src), "-an",
         "-vf", vf, "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", str(out)])


def still_zoom(out, src, at, dur, rotate=False, zoom=0.06, z0=1.0, cx=0.5, cy=0.5):
    # one frame with a push-in from z0 to z0 + zoom, centred on (cx, cy) as fractions of the frame
    png = out.with_suffix(".png")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", str(src), "-frames:v", "1"] +
        (["-vf", "transpose=1"] if rotate else []) + [str(png)])
    n = int(round(dur * FPS))
    x, y = f"max(0,min(iw-iw/zoom,{cx}*iw-iw/zoom/2))", f"max(0,min(ih-ih/zoom,{cy}*ih-ih/zoom/2))"
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(png), "-vf",
         f"scale={W * 4}:{H * 4},zoompan=z='{z0}+{zoom}*on/{n}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS}",
         "-frames:v", str(n), "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", str(out)])


def build(voice):
    v = VOICES[voice]
    c, end = v["cuts"], v["end"] + TAIL
    parts = [WORK / f"seg{i}.mp4" for i in range(1, 7)]
    # grandma and grandson baking (stops before the page slides off the table)
    segment(parts[0], SDR / "clip01.mov", 0.0, 4.4, c[1])
    # his name in the text: whole for only ~0.6 s of the shot, so one sharp frame with a push-in
    still_zoom(parts[1], SDR / "clip03.mov", 0.8, c[2] - c[1], rotate=True, zoom=0.04)
    segment(parts[2], SDR / "clip02.mov", 0.6, 4.0, c[3] - c[2])   # dedication from grandma and grandpa
    segment(parts[3], SDR / "clip05.mov", 0.0, 4.6, c[4] - c[3])   # flip through the printed pages
    segment(parts[4], SDR / "clip04.mov", 0.0, 3.85, c[5] - c[4])  # flip back to the title page
    still_zoom(parts[5], SDR / "clip04.mov", 3.85, end - c[5])      # end card
    (WORK / "concat.txt").write_text("".join(f"file '{p.name}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(WORK / "concat.txt"),
         "-c", "copy", str(WORK / "silent.mp4")])

    # (key, font size, vertical centre, start, end): clip01 has grandma's face in the top band
    plan = [("hook", 82, 1080, 0, c[0]), ("s2", 70, 1080, c[0], c[1]), ("s3", 70, 380, c[1], c[2]),
            ("s4", 70, 380, c[2], c[3]), ("s5", 66, 420, c[3], c[4]), ("s6", 66, 420, c[4], c[5]),
            ("cta", 66, 470, c[5], end)]
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "silent.mp4"), "-i", str(HERE / v["file"])]
    graph, last = [], "0:v"
    for k, (key, size, yc, a, b) in enumerate(plan):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b:.3f}", "-i", str(card(key, size, yc))]
        n = k + 2
        fade = f",fade=t=in:st={a:.3f}:d=0.15:alpha=1" if a else ""  # the hook is whole on frame one (the cover)
        graph.append(f"[{n}:v]format=rgba{fade}[c{k}]")
        graph.append(f"[{last}][c{k}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{k}]")
        last = f"v{k}"
    graph.append(f"[1:a]apad,atrim=0:{end:.3f},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    final = HERE / "final" / f"grandma-baking-book-reel-{voice}.mp4"
    final.parent.mkdir(exist_ok=True)
    cmd += ["-filter_complex", ";".join(graph), "-map", f"[{last}]", "-map", "[a]", "-t", f"{end:.3f}",
            "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)]
    run(cmd)
    print(final, f"{end:.2f}s")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "sarah")
