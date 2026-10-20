#!/usr/bin/env python3
"""Free draft cut of the bedtime story reel (no paid generation).

Layout panels are rendered by headless Chrome (Hebrew RTL + Heebo), the scratch
voice is macOS `say -v Carmit`, pictures come from Sapir's edited reel. The final
replaces the voice with the TTS take and the pictures with the raw clips and the
book's page images.

Run: python3 media/projects/2026-10-20-bedtime-story-reel/draft/build_draft.py
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOB = HERE.parent
ROOT = JOB.parents[2]
SRC = JOB / "references" / "sapir_ivan_mugatz_edited-reel_ariel-book.mov"
LOGO = ROOT / "shared" / "brand" / "logo_wide.png"
FONT = ROOT / "shared" / "brand" / "fonts" / "Heebo-Bold.ttf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WORK = HERE / "build"
OUT = HERE / "bedtime-story-draft-v1.mp4"

W, H, WIN_Y, WIN = 1080, 1920, 240, 1080
FPS = 30

# kind: still (frame at t, crop x:y:size), clip (start, len, crop), full (start, len, keep audio)
BEATS = [
    {"id": "01-hook", "kind": "clip", "t": 4.3, "len": None, "crop": (0, 200, 720),
     "panel": ["סיפור לפני השינה", "שבו אריאל הוא הגיבור"],
     "vo": "סיפור לפני השינה. שבו אריאל הוא הגיבור."},
    {"id": "02-cover", "kind": "still", "t": 25.0, "crop": (140, 114, 440),
     "panel": ["באנו חושך לגרש"],
     "vo": "באנו חושך לגרש."},
    {"id": "03-p4-p5", "kind": "still", "t": 31.9, "crop": (0, 202, 720),
     "panel": ["זה היה לילה שקט", "בחדרם של אריאל ואורי", "״מה אם יצוץ משהו?", "מתוך החשך הגובר״"],
     "vo": "זה היה לילה שקט, בחדרם של אריאל ואורי. מה אם יצוץ משהו? מתוך החושך הגובר."},
    {"id": "04-p6-p7", "kind": "still", "t": 32.7, "crop": (0, 250, 720),
     "panel": ["אריאל התכופף", "פתח את עיניו", "וראה מפלצת כחולה וקטנה", "רועדת בין ברכיה"],
     "vo": "אריאל התכופף, פתח את עיניו, וראה מפלצת כחולה וקטנה, רועדת בין ברכיה."},
    {"id": "05-flip", "kind": "clip", "t": 14.3, "len": 2.0, "crop": (0, 100, 720),
     "panel": ["אריאל התכופף", "פתח את עיניו", "וראה מפלצת כחולה וקטנה", "רועדת בין ברכיה"],
     "vo": None},
    {"id": "06-p8-p9", "kind": "still", "t": 33.9, "crop": (0, 100, 720),
     "panel": ["״מי אתה?״ שאל אריאל בקול", "״אני? אני חשכוני״"],
     "vo": "מי אתה? שאל אריאל בקול. אני? אני חשכוני."},
    {"id": "07-p10", "kind": "still", "t": 25.0, "crop": (200, 150, 330),
     "panel": ["אריאל חייך ואמר", "״אולי במקום לפחד", "ננסה לגלות יחדיו", "שהחשך הוא לא אויב״"],
     "vo": "אריאל חייך ואמר: אולי במקום לפחד, ננסה לגלות יחדיו, שהחושך הוא לא אויב."},
    {"id": "08-real-ending", "kind": "full", "t": 0.0, "len": 2.8, "panel": None, "vo": None},
    {"id": "09-cta", "kind": "still", "t": 25.0, "crop": (140, 114, 440),
     "panel": ["רוצים ספר שבו הילד שלכם הגיבור?", "כתבו \"לומי\" בתגובות", "ונשלח לכם קישור"],
     "vo": "רוצים ספר שבו הילד שלכם הגיבור? כתבו לומי בתגובות, ונשלח לכם קישור."},
]

HTML = """<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
@font-face {{ font-family: Heebo; src: url('{font}'); font-weight: 700; }}
html, body {{ margin: 0; width: {w}px; height: {h}px; background: #fff; overflow: hidden; }}
header {{ height: {win_y}px; display: flex; align-items: center; justify-content: center; }}
header img {{ height: 112px; }}
.win {{ height: {win}px; background: #ece8f4; }}
.panel {{ padding: 44px 60px 0; text-align: center; font-family: Heebo; font-weight: 700;
  font-size: {fs}px; line-height: 1.42; color: #2b2440; }}
.draft {{ position: absolute; top: 18px; left: 22px; font: 700 26px Heebo; color: #b4aac8; }}
</style></head><body><div class="draft">DRAFT</div><header><img src="{logo}"></header>
<div class="win"></div><div class="panel">{lines}</div></body></html>"""


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def panel_png(beat):
    lines = beat["panel"]
    fs = 46 if len(lines) <= 4 else 42
    html = HTML.format(font=FONT.as_uri(), logo=LOGO.as_uri(), w=W, h=H, win_y=WIN_Y, win=WIN, fs=fs,
                       lines="<br>".join(lines))
    page = WORK / f"{beat['id']}.html"
    page.write_text(html, encoding="utf-8")
    png = WORK / f"{beat['id']}-layout.png"
    png.unlink(missing_ok=True)
    # Chrome exits 2 on a CVDisplayLink warning even when the screenshot is written
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={W},{H}", f"--screenshot={png}",
                    page.as_uri()], capture_output=True)
    if not png.exists():
        raise RuntimeError(f"Chrome wrote no screenshot for {beat['id']}")
    return png


def scratch_vo(beat):
    aiff = WORK / f"{beat['id']}-vo.aiff"
    run(["say", "-v", "Carmit", "-r", "165", "-o", str(aiff), beat["vo"]])
    wav = WORK / f"{beat['id']}-vo.wav"
    run(["ffmpeg", "-y", "-i", str(aiff), "-ar", "48000", "-ac", "2", str(wav)])
    return wav


def segment(beat):
    seg = WORK / f"{beat['id']}.mp4"
    enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS), "-preset", "veryfast", "-crf", "20",
           "-c:a", "aac", "-ar", "48000", "-ac", "2"]
    if beat["kind"] == "full":
        run(["ffmpeg", "-y", "-ss", str(beat["t"]), "-t", str(beat["len"]), "-i", str(SRC),
             "-vf", f"scale={W}:{H},setsar=1,fps={FPS}", "-af", "aresample=48000", *enc, str(seg)])
        return seg, beat["len"]

    layout = panel_png(beat)
    vo = scratch_vo(beat) if beat["vo"] else None
    dur = (duration(vo) + 0.6) if vo else (beat.get("len") or 2.0)
    if beat["kind"] == "clip" and beat.get("len") is None:
        beat["len"] = dur
    x, y, s = beat["crop"]
    frames = int(round(dur * FPS))
    if beat["kind"] == "still":
        still = WORK / f"{beat['id']}-src.png"
        run(["ffmpeg", "-y", "-ss", str(beat["t"]), "-i", str(SRC), "-frames:v", "1", str(still)])
        pic_in = ["-i", str(still)]
        pic = (f"[1]crop={s}:{s}:{x}:{y},scale=2160:2160,"
               f"zoompan=z='1+0.07*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
               f":d={frames}:s={WIN}x{WIN}:fps={FPS}[pic]")
    else:
        pic_in = ["-ss", str(beat["t"]), "-t", f"{dur:.3f}", "-i", str(SRC)]
        pic = f"[1]crop={s}:{s}:{x}:{y},scale={WIN}:{WIN},fps={FPS}[pic]"
    audio_in = ["-i", str(vo)] if vo else ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    graph = f"{pic};[0][pic]overlay=0:{WIN_Y}:shortest=1,setsar=1[v];[2]apad[a]"
    run(["ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-i", str(layout), *pic_in, *audio_in,
         "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}", *enc, str(seg)])
    return seg, dur


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    timeline, t = [], 0.0
    parts = []
    for beat in BEATS:
        seg, dur = segment(beat)
        parts.append(seg)
        timeline.append({"id": beat["id"], "start": round(t, 2), "dur": round(dur, 2)})
        t += dur
    listing = WORK / "concat.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
         "-movflags", "+faststart", str(OUT)])
    (HERE / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
    print(OUT, f"{t:.1f}s")
    for row in timeline:
        print(row)


if __name__ == "__main__":
    main()
