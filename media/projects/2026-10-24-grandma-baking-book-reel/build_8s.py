"""8-second cut of the grandma baking book reel (24 Oct 2026), asked for as fast editing, retention and
conversion first, no price, a quick story with a curiosity gap. The gap: "תסתכלו על הילד הזה" over the
illustrated boy, paid off by "זה הוא" on his real photo on the title page, then his name, the
dedication and the CTA. Reuses the helpers in build.py; same sources and safe zone.
Run: ~/.claude/skills/watch-video/.venv/bin/python build_8s.py"""
import json
import build
from build import FPS, HERE, SDR, WORK, card, run, segment, still_zoom

END, SPEED, GAP = 8.0, 1.2, 0.06
build.copy = json.load(open(HERE / "copy-8s.json"))

# Phrases in audio/vo-8s-sarah.mp3 (ElevenLabs character timestamps), cut out, sped up and laid end to end.
PHRASES = [(0.00, 2.12), (2.50, 3.80), (4.12, 4.80), (4.84, 5.72), (6.06, 7.96), (8.28, 9.86)]


def main():
    starts, t = [], 0.0
    for s, e in PHRASES:
        starts.append(t)
        t += (e - s) / SPEED + GAP
    ends = [st + (e - s) / SPEED for st, (s, e) in zip(starts, PHRASES)]
    # picture and card changes sit in the gap before each phrase; phrase 4 and 5 share the name/dedication run
    c = [(ends[i] + starts[i + 1]) / 2 for i in range(5)]

    parts = [WORK / f"s8_seg{i}.mp4" for i in range(1, 9)]
    segment(parts[0], SDR / "clip01.mov", 0.15, c[0], c[0])                 # grandma laughing
    segment(parts[1], SDR / "clip01.mov", 2.75, c[1] - c[0], c[1] - c[0])   # the illustrated grandson
    still_zoom(parts[2], SDR / "clip04.mov", 3.85, c[2] - c[1], zoom=0.2, z0=2.1, cx=0.372, cy=0.50)  # his photo
    still_zoom(parts[3], SDR / "clip03.mov", 0.8, c[3] - c[2], rotate=True, zoom=0.04)  # his name in the text
    mid = c[3] + (c[4] - c[3]) * 0.55
    segment(parts[4], SDR / "clip02.mov", 1.0, 1.8, mid - c[3])             # "הספר הזה מוקדש מכל הלב"
    segment(parts[5], SDR / "clip05.mov", 2.3, 2.1, c[4] - mid)             # fast flip through the pages
    hold = 0.5
    segment(parts[6], SDR / "clip04.mov", 0.6, 3.25, END - c[4] - hold)     # flip back to the title page
    still_zoom(parts[7], SDR / "clip04.mov", 3.85, hold, zoom=0.02)
    (WORK / "s8_concat.txt").write_text("".join(f"file '{p.name}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(WORK / "s8_concat.txt"),
         "-c", "copy", str(WORK / "s8_silent.mp4")])

    plan = [("s8_hook", 82, 1080, 0, c[0]), ("s8_look", 78, 1080, c[0], c[1]), ("s8_him", 112, 380, c[1], c[2]),
            ("s8_name", 74, 380, c[2], c[3]), ("s8_dedication", 74, 380, c[3], c[4]), ("cta", 66, 470, c[4], END)]
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(WORK / "s8_silent.mp4"), "-i", str(HERE / "audio" / "vo-8s-sarah.mp3")]
    graph, last = [], "0:v"
    for k, (key, size, yc, a, b) in enumerate(plan):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b:.3f}", "-i", str(card(key, size, yc))]
        fade = f",fade=t=in:st={a:.3f}:d=0.08:alpha=1" if a else ""  # the hook is whole on frame one
        graph.append(f"[{k + 2}:v]format=rgba{fade}[c{k}]")
        graph.append(f"[{last}][c{k}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{k}]")
        last = f"v{k}"
    graph.append(f"[1:a]asplit={len(PHRASES)}" + "".join(f"[a{i}]" for i in range(len(PHRASES))))
    for i, ((s, e), st) in enumerate(zip(PHRASES, starts)):
        graph.append(f"[a{i}]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={e - s - 0.02:.3f}:d=0.02,"
                     f"atempo={SPEED},adelay=delays={int(st * 1000)}:all=1[p{i}]")
    graph.append("".join(f"[p{i}]" for i in range(len(PHRASES))) +
                 f"amix=inputs={len(PHRASES)}:normalize=0,apad,atrim=0:{END},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    final = HERE / "final" / "grandma-baking-book-reel-8s.mp4"
    cmd += ["-filter_complex", ";".join(graph), "-map", f"[{last}]", "-map", "[a]", "-t", str(END),
            "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)]
    run(cmd)
    print(final, "cuts", [round(x, 2) for x in c], "voice ends", round(ends[-1], 2))


if __name__ == "__main__":
    main()
