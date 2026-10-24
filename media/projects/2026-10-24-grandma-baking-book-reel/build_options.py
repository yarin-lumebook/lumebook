"""8-second options with other children (24 Oct 2026): the fast, curiosity-gap format of build_8s.py, cut from
three creator videos already downloaded for the creator brief (Drive תוכן לקוחות ויוצרים (UGC), local copies in
media/projects/2026-10-15-israeli-product-reels/creator-examples/raw/). Each story keeps to what the creator says
in her own video (creator-examples/analysis/<video>/whisper.txt). The exports have the creators' captions burned in
(some say "AI"), so every shot is cropped to a window above them. Nofit's video is HLG HDR: convert it first with
avconvert into work/sdr/nofit.mov (see README.md).
Run: ~/.claude/skills/watch-video/.venv/bin/python build_options.py [natali nofit moran]"""
import json
import sys
import build
from build import FPS, HERE, WORK, card, run, segment, still_zoom

RAW = HERE.parent / "2026-10-15-israeli-product-reels" / "creator-examples" / "raw"
END, GAP = 8.0, 0.03
build.copy = json.load(open(HERE / "copy-options.json"))

# phrases: (start, end) in the voice take; beats: one shot per phrase, the last one runs to END.
# A shot is ("seg", source start, crop window (f, x0, y0)) at 1x, or ("still", at, z0, cx, cy) with a push-in.
# cards: (copy key, font size, vertical centre) per phrase.
OPTIONS = {
    "natali": {  # her son screamed at the gan gate; she made him the new-gan book; he walks in holding it
        "voice": "vo-opt-natali.mp3", "speed": 1.25, "src": RAW / "Natali_Fridman_v2.mp4",
        "phrases": [(0.00, 2.12), (2.44, 4.46), (4.84, 6.44), (7.40, 9.34), (9.72, 11.38)],  # 3rd ends before "של הגן"
        "beats": [("seg", 3.35, (0.69, 0.0, 0.0)), ("seg", 24.0, (0.69, 0.155, 0.0)), ("seg", 27.3, (0.69, 0.155, 0.02)),
                  ("seg", 39.0, (0.69, 0.155, 0.0)), ("seg", 40.5, (0.69, 0.155, 0.0))],
        "cards": [("nat_hook", 82, 1080), ("nat_gap", 74, 410), ("nat_hero", 74, 410), ("nat_take", 74, 410), ("cta", 66, 470)],
    },
    "nofit": {  # one photo from her gallery; the book with him on the cover; he sees himself
        "voice": "vo-opt-nofit.mp3", "speed": 1.2, "src": WORK / "sdr" / "nofit.mov",
        "phrases": [(0.00, 2.52), (2.92, 4.62), (5.00, 6.70), (7.00, 8.12), (9.40, 11.14)],  # 4th ends before "בתוך הסיפור"
        # times are in the SDR copy; her captions sit at 66-70%, so every window ends by 65%
        "beats": [("still", 20.1, 1.55, 0.5, 0.33), ("seg", 0.0, (0.63, 0.185, 0.02)), ("seg", 12.0, (0.63, 0.1, 0.0)),
                  ("still", 11.5, 1.55, 0.5, 0.32), ("seg", 28.2, (0.64, 0.18, 0.0))],
        "cards": [("nof_hook", 82, 420), ("nof_gap", 74, 1080), ("nof_hero", 74, 380), ("nof_sees", 74, 410), ("cta", 66, 470)],
    },
    "moran": {  # the aunt's gift the family talked about; her niece finds herself in the book
        "voice": "vo-opt-moran.mp3", "speed": 1.2, "src": RAW / "Moran_arges_v3.mp4",
        "phrases": [(0.00, 3.34), (3.72, 5.16), (5.40, 6.30), (6.44, 7.88), (8.28, 9.94)],
        "beats": [("seg", 4.6, (0.78, 0.11, 0.0)), ("seg", 8.1, (0.78, 0.11, 0.0)), ("seg", 25.3, (0.6, 0.15, 0.08)),
                  ("seg", 29.6, (0.78, 0.11, 0.02)), ("seg", 52.0, (0.78, 0.11, 0.0))],
        "cards": [("mor_hook", 66, 1135), ("mor_gap", 74, 1000), ("mor_her", 112, 380), ("mor_all", 74, 380), ("cta", 66, 470)],
    },
}


def build_option(name):
    o = OPTIONS[name]
    sp, starts, t = o["speed"], [], 0.0
    for s, e in o["phrases"]:
        starts.append(t)
        t += (e - s) / sp + GAP
    ends = [st + (e - s) / sp for st, (s, e) in zip(starts, o["phrases"])]
    cuts = [0.0] + [(ends[i] + starts[i + 1]) / 2 for i in range(len(starts) - 1)] + [END]

    parts = []
    for i, shot in enumerate(o["beats"]):
        out, dur = WORK / f"opt_{name}_{i + 1}.mp4", cuts[i + 1] - cuts[i]
        if shot[0] == "seg":
            segment(out, o["src"], shot[1], dur, dur, window=shot[2])
        else:
            still_zoom(out, o["src"], shot[1], dur, zoom=0.08, z0=shot[2], cx=shot[3], cy=shot[4])
        parts.append(out)
    # concat filter, not a stream copy: a still first in a copied concat hands its encoder headers to every clip
    run(["ffmpeg", "-v", "error", "-y"] + sum((["-i", str(p)] for p in parts), []) +
        ["-filter_complex", "".join(f"[{i}:v]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[v]",
         "-map", "[v]", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
         str(WORK / f"opt_{name}_silent.mp4")])

    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", "-i", str(WORK / f"opt_{name}_silent.mp4"), "-i", str(HERE / "audio" / o["voice"])]
    graph, last = [], "0:v"
    for k, (key, size, yc) in enumerate(o["cards"]):
        a, b = cuts[k], cuts[k + 1]
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b:.3f}", "-i", str(card(key, size, yc))]
        fade = f",fade=t=in:st={a:.3f}:d=0.08:alpha=1" if a else ""  # the hook is whole on frame one
        graph.append(f"[{k + 2}:v]format=rgba{fade}[c{k}]")
        graph.append(f"[{last}][c{k}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{k}]")
        last = f"v{k}"
    n = len(o["phrases"])
    graph.append(f"[1:a]asplit={n}" + "".join(f"[a{i}]" for i in range(n)))
    for i, ((s, e), st) in enumerate(zip(o["phrases"], starts)):
        graph.append(f"[a{i}]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={e - s - 0.02:.3f}:d=0.02,"
                     f"atempo={sp},adelay=delays={int(st * 1000)}:all=1[p{i}]")
    graph.append("".join(f"[p{i}]" for i in range(n)) +
                 f"amix=inputs={n}:normalize=0,apad,atrim=0:{END},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    final = HERE / "final" / f"option-{name}-8s.mp4"
    cmd += ["-filter_complex", ";".join(graph), "-map", f"[{last}]", "-map", "[a]", "-t", str(END),
            "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)]
    run(cmd)
    print(final, "cuts", [round(x, 2) for x in cuts[1:-1]], "voice ends", round(ends[-1], 2))


if __name__ == "__main__":
    for name in sys.argv[1:] or list(OPTIONS):
        build_option(name)
