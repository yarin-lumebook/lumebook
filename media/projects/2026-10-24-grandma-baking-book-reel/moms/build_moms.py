"""Creator options in the mom's own voice (24 Oct 2026). Yarin: no length limit, a bold white hook burned in at
the top, word-by-word white captions at the bottom, and a voice that sounds natural, warm, Israeli and like a mom.
So each option is re-cut from the creator's own video and narration (local copies of the Drive UGC files in
media/projects/2026-10-15-israeli-product-reels/creator-examples/raw/), keeping her strongest lines and dropping
the ones that mention AI, the old price or her own "go to the site" ending. Every shot is cropped above her
burned-in captions. Word timings come from moms/transcribe.py (ivrit-ai whisper), checked by hand in CLIPS.
Font: SF Hebrew, my closest match to Instagram's own text on iPhone (not verified against the app).
Run: ~/.claude/skills/watch-video/.venv/bin/python moms/build_moms.py [natali nofit moran]"""
import json
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
PROJECT = HERE.parent
RAW = PROJECT.parent / "2026-10-15-israeli-product-reels" / "creator-examples" / "raw"
WORK = PROJECT / "work" / "moms"; WORK.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1080, 1920, 30
SAFE_TOP, SAFE_BOTTOM = int(H * 0.14), int(H * 0.65)
SF, SF_LATIN = "/System/Library/Fonts/SFHebrew.ttf", "/System/Library/Fonts/SFNS.ttf"
TAIL = 2.6  # CTA beat after her last word
copy = json.load(open(HERE / "copy-moms.json"))
CLIPS = json.load(open(HERE / "clips.json"))


def run(cmd):
    subprocess.run(cmd, check=True)


def visual(line):
    # RTL line drawn left to right: reverse it, then put Latin words and numbers back in reading order
    return re.sub(r"[A-Za-z0-9]+", lambda m: m.group(0)[::-1], line[::-1])


def fonts(size, weight):
    he = ImageFont.truetype(SF, size); he.set_variation_by_name(weight)
    la = ImageFont.truetype(SF_LATIN, size); la.set_variation_by_name(weight)
    return he, la


_tofu = {}
def runs(vis, f):
    # SF Hebrew has no Latin letters or ASCII punctuation; SF Pro supplies them
    he, la = f
    key = id(he)
    if key not in _tofu: _tofu[key] = bytes(he.getmask("\U000F0000"))
    out = []
    for c in vis:
        g = la if (c != " " and bytes(he.getmask(c)) == _tofu[key]) else he
        if out and out[-1][1] is g: out[-1][0] += c
        else: out.append([c, g])
    return out


def width(d, vis, f): return sum(d.textlength(t, font=g) for t, g in runs(vis, f))


def draw_lines(im, lines, f, size, top):
    # white text over a soft dark shadow, so it reads on white pages too
    lh = int(size * 1.22)
    placed = []
    probe = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        vis = visual(l); x = (W - width(probe, vis, f)) / 2
        for t, g in runs(vis, f):
            placed.append((x, top + i * lh, t, g)); x += probe.textlength(t, font=g)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for x, y, t, g in placed:
        sd.text((x, y + 3), t, font=g, fill=(0, 0, 0, 190), stroke_width=4, stroke_fill=(0, 0, 0, 190))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    for x, y, t, g in placed:
        d.text((x, y), t, font=g, fill="white")
    return top + len(lines) * lh


def frame(top_key, word):
    # one overlay frame: the hook (or CTA) at the top, the current word at the bottom
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if top_key:
        lines, size = copy[top_key].split("\n"), 76
        f = fonts(size, "Bold"); d = ImageDraw.Draw(base)
        while max(width(d, visual(l), f) for l in lines) > W * 0.86: size -= 2; f = fonts(size, "Bold")
        bottom = draw_lines(base, lines, f, size, SAFE_TOP + 20)
        assert bottom <= SAFE_BOTTOM
    if word:
        size = 84; f = fonts(size, "Medium")
        y = SAFE_BOTTOM - int(size * 1.22) - 10  # the lowest line inside the safe zone
        draw_lines(base, [word], f, size, y)
    im.alpha_composite(base)
    return im


def build(name):
    c = CLIPS[name]
    src = PROJECT / c["src"] if not c["src"].startswith("RAW/") else RAW / c["src"][4:]
    words = json.load(open(HERE / f"{name}-words.json"))
    fixes = c.get("fixes", {})

    # 1. cut her segments, cropped above her captions; then the CTA tail. A segment is [voice start, voice end,
    #    crop window (f, x0, y0)] with an optional picture start, for voice-over moments where a stronger shot fits
    parts, timeline, t = [], [], 0.0
    for i, seg in enumerate(c["segments"] + [[c["tail"][0], c["tail"][0] + TAIL, c["tail"][1]]]):
        s, e, win = seg[:3]
        v = seg[3] if len(seg) > 3 else s
        tail = i == len(c["segments"])
        out = WORK / f"{name}_{i:02d}.mp4"; dur = e - s
        crop = f"crop=iw*{win[0]}:ih*{win[0]}:iw*{win[1]}:ih*{win[2]},scale={W}:{H},fps={FPS},setsar=1"
        af = "volume=0" if tail else f"afade=t=in:d=0.03,afade=t=out:st={dur - 0.04:.3f}:d=0.04"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(v), "-t", f"{dur:.3f}", "-i", str(src),
             "-ss", str(s), "-t", f"{dur:.3f}", "-i", str(src), "-map", "0:v", "-map", "1:a", "-vf", crop, "-af", af,
             "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
             "-ar", "48000", "-ac", "2", str(out)])
        parts.append(out)
        if not tail: timeline.append((s, e, t))
        t += dur
    end = t
    n = len(parts)
    run(["ffmpeg", "-v", "error", "-y"] + sum((["-i", str(p)] for p in parts), []) +
        ["-filter_complex", "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", str(WORK / f"{name}_cut.mp4")])

    # 2. her words on the new timeline, one at a time, each held until the next one starts
    events = []
    for s, e, off in timeline:
        for w in words:
            if s - 0.05 <= w["s"] < e - 0.05:
                bare = w["w"].strip(" ,.?!")
                text = fixes.get(bare, bare)
                if text: events.append([off + max(w["s"] - s, 0), off + min(w["e"], e) - s, text])
    for a, b in zip(events, events[1:]):
        a[1] = min(max(a[1], a[0] + 0.12), b[0]) if b[0] - a[1] < 0.35 else a[1]
    cta_at = end - TAIL

    # 3. overlay track: a PNG per change, timed by the concat demuxer
    marks = sorted({0.0, cta_at, end} | {x for ev in events for x in ev[:2]})
    lines, prev = [], None
    for i, (a, b) in enumerate(zip(marks, marks[1:])):
        word = next((ev[2] for ev in events if ev[0] <= a < ev[1]), None)
        top = "cta" if a >= cta_at - 1e-6 else c["hook"]
        key = (top, word)
        png = WORK / f"{name}_ov_{i:03d}.png"
        if key != prev:
            frame(top, word).save(png)
        else:
            png = Path(lines[-2][6:-1])  # same picture as the last one
        lines += [f"file '{png}'", f"duration {b - a:.3f}"]
        prev = key
    lines.append(lines[-2])
    (WORK / f"{name}_ov.txt").write_text("\n".join(lines) + "\n")

    final = PROJECT / "final" / f"mom-voice-{name}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(WORK / f"{name}_cut.mp4"), "-f", "concat", "-safe", "0",
         "-i", str(WORK / f"{name}_ov.txt"), "-filter_complex",
         f"[1:v]fps={FPS},format=rgba[o];[0:v][o]overlay=0:0:shortest=1[v];[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{end:.3f}", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)])
    (WORK / f"{name}_captions.json").write_text(json.dumps(events, ensure_ascii=False, indent=0))
    print(final, f"{end:.2f}s", len(events), "words")


if __name__ == "__main__":
    for name in sys.argv[1:] or list(CLIPS):
        build(name)
