"""Assemble a daily reel the way reel 1.1 was made, from one edit.json instead of nine hand-written scripts.

Reel 1.1 (04 Nov 2026) needed build_v3.py to build_v9.py plus build_v5_audio.py in its media folder. This file is
that recipe made general (media/projects/2026-11-03-reel-1-1-preview-screen/build_v5_audio.py and build_v9.py):

 1. iPhone HDR (HLG) sources are converted with avconvert, as the reel editor does.
 2. Sound: the hook clip's own audio, then the voiceover with every pause cut to 0.1 s, the studio chain
    (rumble cut, light denoise, warmth, presence, de-ess, compression) and loudness to -14 LUFS.
 3. ivrit-ai whisper transcribes that sound once (cached in work/make/words-raw.json). The words are then
    matched to the script in reels.json, so the captions take the script's spelling and only the times
    come from whisper. Words the matcher could not place are listed; fix the script or edit the cache.
 4. Everything after the hook clip runs at 1.1x (picture, voice and captions), the hook clip at 1x.
 5. Shots are cut on script words: each segment in edit.json starts at a voiceover line or word, so a new
    take of the voice moves the cuts with it. Screen recordings sit in a centred 720x1440 window with
    rounded corners and a soft shadow over a blurred clip of the book, as in 1.1.
 6. Captions keep only ? and " (Yarin, 04 Nov 2026), "לומי" gets quotes, and the purple CTA covers the
    last line from its first word. The hook stays on top through the hook clip, and at least long
    enough to read it at 17 characters a second (principle T5, research/israeli-product-reels/
    smm-research/principles.md), then no top text until the CTA.
 7. The reel editor burns the text and writes final/reel-<id>-1.mp4 and its QC sheet.

edit.json (in the reel's media folder, written by `reels.py new`, paths relative to that folder):

    {
      "hook_clip": "source/yarin/hook.mov",       Yarin's 2 s talking hook
      "hook_end": null,                           seconds; null = where his speech ends + 0.12 s
      "voice": "source/yarin/voice.m4a",          the voiceover take
      "voice_start": 0.0,                         skip a false start at the top of the take
      "speed_after_hook": 1.1,
      "background": {"src": "source/book.mov", "ss": 3.0},   blurred clip behind screen windows
      "hook_overlay": {"img": "source/photo.png", "y": 1230}, optional picture under the face, from the 2nd hook word
      "segments": [
        {"at": 0, "src": "source/cover.mov", "ss": 0.2},                    from voiceover line 0
        {"at": "כותבים", "src": "source/screen.mov", "ss": 3.0, "window": true},
        {"at": "ומעלים", "src": "source/wizard.mp4", "ss": 2.0, "window": true, "speed": 2, "crop": "887:1920:96:0"},
        {"at": "cta", "src": "source/flip.mov", "ss": 1.5}                  from the CTA line
      ]
    }

The hook clip always opens the reel; the first segment should start at line 0. Run it through reels.py:

    python3 research/israeli-product-reels/src/scripts/series-2026-11/reels.py make 1.7
"""
import json, re, subprocess, sys
from difflib import SequenceMatcher
from pathlib import Path

FF = "ffmpeg"
EDITOR = Path(__file__).resolve().parents[5] / ".claude/skills/reel-editor/scripts/reel_editor.py"
EDITOR_PY = Path.home() / ".claude/skills/watch-video/.venv/bin/python"
GAP, PAD, LEAD = 0.10, 0.05, 0.04          # pause length after cutting, kept around speech, cut before a cue word
WIN_W, WIN_H, WIN_X, WIN_Y, RAD = 720, 1440, 180, 240, 54
FILL = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
WIN = f"scale={WIN_W}:{WIN_H}:force_original_aspect_ratio=increase,crop={WIN_W}:{WIN_H}"
OUT = "fps=30,format=yuv420p,setsar=1"
STUDIO = ("highpass=f=75,afftdn=nr=12:nf=-45,equalizer=f=280:t=q:w=1.2:g=-2.5,equalizer=f=110:t=q:w=1:g=2,"
          "equalizer=f=3500:t=q:w=1.4:g=3,equalizer=f=11000:t=q:w=1:g=2,deesser=i=0.35,"
          "acompressor=threshold=-21dB:ratio=3:attack=5:release=90:makeup=4")
READ_CPS = 17                              # principle T5: Hebrew on screen at most 17 characters a second


def run(*a, **kw):
    return subprocess.run([str(x) for x in a], check=True, **kw)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def is_hdr(p):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=color_transfer", "-of", "csv=p=0", str(p)], text=True).strip()
    return out in ("arib-std-b67", "smpte2084")


def sdr(base, rel, work):
    """iPhone HDR clips go through avconvert once (the local ffmpeg cannot tone-map them well)."""
    src = base / rel
    if src.suffix.lower() not in (".mov", ".mp4") or not is_hdr(src):
        return src
    out = work / "sdr" / (src.stem + ".mov")
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        run("avconvert", "--preset", "Preset1920x1080", "--source", src, "--output", out)
    return out


def silences(wav, noise="-38dB", d=0.15):
    log = subprocess.run([FF, "-v", "info", "-i", str(wav), "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    total = dur(wav)
    return list(zip(st, en + [total] * (len(st) - len(en)))), total


def norm(w):
    return re.sub(r"[^\w]", "", w).replace("_", "")


def align(raw, script):
    """Give whisper's timed words the script's spelling. Returns (words, problems)."""
    a, b = [norm(w["w"]) for w in raw], [norm(w) for w in script]
    out, problems = [], []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
            out += [dict(raw[i], w=script[j]) for i, j in zip(range(i1, i2), range(j1, j2))]
            if op == "replace":
                problems.append(f"heard {' '.join(w['w'] for w in raw[i1:i2])!r}, script says {' '.join(script[j1:j2])!r} (script kept)")
        elif op == "replace":       # different counts: spread the script words over the heard stretch
            s, e = raw[i1]["s"], raw[i2 - 1]["e"]
            step = (e - s) / (j2 - j1)
            out += [{"w": script[j1 + k], "s": round(s + k * step, 3), "e": round(s + (k + 1) * step, 3)} for k in range(j2 - j1)]
            problems.append(f"heard {' '.join(w['w'] for w in raw[i1:i2])!r}, script says {' '.join(script[j1:j2])!r} (times spread)")
        elif op == "insert":
            problems.append(f"not heard: {' '.join(script[j1:j2])!r} (check the take, or the script changed)")
        elif op == "delete":
            problems.append(f"heard but not in the script: {' '.join(w['w'] for w in raw[i1:i2])!r} (left out of the captions)")
    return out, problems


def speech(wav):
    """The spoken stretches of a take, with PAD kept around each, as (start, end) pairs."""
    sil, total = silences(wav)
    keep, cur = [], 0.0
    for s, e in sil:
        if s > cur:
            keep.append((max(0, cur - PAD), s + PAD))
        cur = e
    if cur < total:
        keep.append((max(0, cur - PAD), total))
    return [(a, b) for a, b in keep if b - a > 0.08], total


def studio(work, tight):
    """The studio chain and loudness of reel 1.1, into work/voice-studio.wav."""
    run(FF, "-y", "-v", "error", "-i", tight, "-af", STUDIO, work / "studio-pre.wav")
    m = subprocess.run([FF, "-v", "info", "-i", str(work / "studio-pre.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.89")
    run(FF, "-y", "-v", "error", "-i", work / "studio-pre.wav", "-af", ln, "-ar", 48000, "-ac", 2, work / "voice-studio.wav")


def make(rid, folder, hook, vo, cta_line, cta_screen, retranscribe=False, build=True):
    """Two kinds of reel. With "take" in edit.json: one talking take to camera is the whole reel (1.7), cut
    on its pauses (jump cuts, principle E2). Otherwise: a hook clip, then a voiceover over the segments (1.1)."""
    base = Path(folder)
    cfg = json.loads((base / "edit.json").read_text())
    work = base / "work/make"
    work.mkdir(parents=True, exist_ok=True)
    after = float(cfg.get("speed_after_hook", 1.1))
    take = cfg.get("take")
    lines = list(vo) + ([cta_line] if cta_line else [])
    script = [w for l in lines for w in l.split()]
    hook_words = [] if take else hook.replace("\n", " ").split()

    # 1 and 2. sources and sound at 1x
    if take:
        src = sdr(base, take, work)
        run(FF, "-y", "-v", "error", "-ss", cfg.get("voice_start", 0), "-i", src, "-vn", "-ac", 1, "-ar", 48000, work / "take-raw.wav")
        keep, total = speech(work / "take-raw.wav")
        fc = "".join(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,{FILL},{OUT}[v{i}];"
                     f"[1:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.02:.3f}:d=0.02[a{i}];"
                     for i, (a, b) in enumerate(keep))
        fc += "".join(f"[v{i}][a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
        run(FF, "-y", "-v", "error", "-ss", cfg.get("voice_start", 0), "-i", src, "-i", work / "take-raw.wav",
            "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", 16, "-c:a", "pcm_s16le",
            work / "take-tight.mov")
        run(FF, "-y", "-v", "error", "-i", work / "take-tight.mov", "-vn", "-ac", 1, "-ar", 48000, work / "tight.wav")
        studio(work, work / "tight.wav")
        print(f"sound: take {total:.1f} s cut to {dur(work / 'voice-studio.wav'):.1f} s ({len(keep)} stretches, jump cuts)")
    else:
        hook_clip = sdr(base, cfg["hook_clip"], work)
        run(FF, "-y", "-v", "error", "-i", hook_clip, "-vn", "-ac", 1, "-ar", 48000, work / "hook-full.wav")
        if cfg.get("hook_end"):
            intro = float(cfg["hook_end"])
        else:
            sil, htotal = silences(work / "hook-full.wav", d=0.25)
            speech_end = next((s for s, e in reversed(sil) if e >= htotal - 0.05 and s > 0.3), htotal)
            intro = round(min(speech_end + 0.12, htotal), 2)
        run(FF, "-y", "-v", "error", "-i", work / "hook-full.wav", "-t", intro, work / "hook.wav")
        run(FF, "-y", "-v", "error", "-ss", cfg.get("voice_start", 0), "-i", base / cfg["voice"], "-ac", 1, "-ar", 48000, work / "voice-raw.wav")
        keep, total = speech(work / "voice-raw.wav")
        fc, labels = f"[0:a]anull[h];aevalsrc=0:d={GAP}:s=48000[g0];", ["[h]", "[g0]"]
        for i, (a, b) in enumerate(keep):
            fc += f"[1:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.02:.3f}:d=0.02[k{i}];"
            labels.append(f"[k{i}]")
            if i < len(keep) - 1:
                fc += f"aevalsrc=0:d={GAP}:s=48000[g{i + 1}];"
                labels.append(f"[g{i + 1}]")
        fc += "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[o]"
        run(FF, "-y", "-v", "error", "-i", work / "hook.wav", "-i", work / "voice-raw.wav", "-filter_complex", fc, "-map", "[o]", work / "tight.wav")
        studio(work, work / "tight.wav")
        print(f"sound: hook clip {intro} s, voiceover {total:.1f} s cut to {dur(work / 'voice-studio.wav') - intro:.1f} s ({len(keep)} stretches)")

    # 3. transcript, matched to the script (hook + voiceover in one pass: whisper's times drift around the join)
    raw_path = work / "words-raw.json"
    if retranscribe or not raw_path.exists():
        import os
        run("/usr/bin/python3", EDITOR.parent / "transcribe.py", work / "voice-studio.wav", raw_path,
            env=dict(os.environ, KMP_DUPLICATE_LIB_OK="TRUE"))
    raw = json.loads(raw_path.read_text())
    both, problems = align(raw, hook_words + script)
    raw_hook, words = both[:len(hook_words)], both[len(hook_words):]
    line_start, k = [], 0                    # index into words of each line's first word
    for l in lines:
        line_start.append(k)
        k += len(l.split())
    if len(words) != len(script):
        problems.append(f"matched {len(words)} of {len(script)} script words; cue words may be off")
    if take:                                 # the spoken first line is the hook: 1x until it ends
        n0 = len(lines[0].split())
        intro = float(cfg["hook_end"]) if cfg.get("hook_end") else round(words[min(n0, len(words)) - 1]["e"] + 0.08, 2)
    else:
        for w in words:                      # nothing of the voiceover can start inside the hook clip
            w["s"] = max(w["s"], intro + GAP / 2)
            w["e"] = max(w["e"], w["s"] + 0.05)

    # 4. 1.1x after the hook
    tm = lambda t: t if t <= intro else intro + (t - intro) / after
    end = round(max(tm(dur(work / "voice-studio.wav")), tm(words[-1]["e"]) + 0.32), 2)

    def cue(at):
        if at == "cta":
            at = len(lines) - 1
        if isinstance(at, int):
            w = words[min(line_start[at], len(words) - 1)]
        else:
            w = next((x for x in words if norm(x["w"]) == norm(at)), None)
            if not w:
                sys.exit(f"cue word {at!r} is not in the script")
        return round(tm(w["s"]) - LEAD, 3)

    # 5. picture
    if take:
        starts = [0.0, intro, end]
        run(FF, "-y", "-v", "error", "-i", work / "take-tight.mov", "-filter_complex",
            f"[0:v]split[x][y];[x]trim=0:{intro},setpts=PTS-STARTPTS[p1];[y]trim=start={intro},setpts=(PTS-STARTPTS)/{after}[p2];"
            f"[p1][p2]concat=n=2:v=1:a=0,tpad=stop_mode=clone:stop_duration=5,trim=0:{end},{OUT}[o]",
            "-map", "[o]", "-an", "-c:v", "libx264", "-crf", 17, work / "video.mp4")
        print(f"  take  0.00 to {intro:5.2f} at 1x, then {after:g}x to {end:.2f}")
    else:
        starts = build_segments(base, work, cfg, hook_clip, intro, end, after, cue, raw_hook)

    # sound: the hook at 1x, the rest at 1.1x (atempo keeps the pitch)
    run(FF, "-y", "-v", "error", "-i", work / "voice-studio.wav", "-filter_complex",
        f"[0:a]asplit[x][y];[x]atrim=0:{intro},asetpts=PTS-STARTPTS[a1];[y]atrim=start={intro},asetpts=PTS-STARTPTS,atempo={after}[a2];"
        f"[a1][a2]concat=n=2:v=0:a=1,apad,atrim=0:{end},afade=t=out:st={end - 0.25}:d=0.25[o]",
        "-map", "[o]", "-ar", 48000, work / "sound.wav")

    # 6. captions, top cards and the reel editor's job file
    caps = []
    for w in words:
        t = re.sub(r'[^\w?"]', "", w["w"])
        t = '"לומי"' if t == "לומי" else t
        if t:
            caps.append({"w": t, "s": round(tm(w["s"]), 3), "e": round(tm(w["e"]), 3)})
    (base / "words.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1) + "\n")
    hook_read = round(len(hook.replace("\n", " ")) / READ_CPS, 2)
    cta_i = max((i for i, w in enumerate(words) if norm(w["w"]) == "תכתבו"), default=line_start[-1])
    cta_from = tm(words[cta_i]["s"])
    job = {"source": "work/make/video.mp4", "name": f"reel-{rid.replace('.', '-')}",
           "hooks": [hook], "hook_seconds": max(intro, hook_read), "captions": "words.json",
           "cta": {"text": cta_screen, "seconds": round(end - cta_from + 0.05, 2), "highlight": True},
           "versions": 1, "flip": False, "audio": "work/make/sound.wav"}
    tops = [{"text": c["text"], "s": max(cue(c["at"]) + LEAD, job["hook_seconds"]),
             "size": c.get("size", 150 if len(c["text"]) <= 2 else 64)} for c in cfg.get("top_cards", [])]   # a lone number reads big
    for i, c in enumerate(tops):             # each card stays until the next one, or the CTA
        c["e"] = round(max(tops[i + 1]["s"] if i + 1 < len(tops) else cta_from, c["s"] + 1.0), 3)
    if tops:
        job["top_cards"] = tops
    (base / "reel.json").write_text(json.dumps(job, ensure_ascii=False, indent=1) + "\n")
    report = {"length": end, "hook_spoken": intro, "hook_on_screen": job["hook_seconds"], "cuts": starts,
              "top_cards": tops, "problems": problems}
    (work / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n")
    print(f"length {end} s, hook on screen {job['hook_seconds']} s (spoken {intro} s, reading time {hook_read} s)")
    for p_ in problems:
        print("  check:", p_)
    if build:
        run(EDITOR_PY, EDITOR, "build", base / "reel.json")
    return report


def build_segments(base, work, cfg, hook_clip, intro, end, after, cue, raw_hook):
    """Hook clip, then each segment from its cue word, screen recordings in windows (reel 1.1 v9)."""
    segs = cfg["segments"]
    starts = [0.0, intro] + [cue(s["at"]) for s in segs[1:]] + [end]
    if any(b <= a for a, b in zip(starts, starts[1:])):
        sys.exit(f"segments are out of order: {starts}")
    pieces = [("hook", hook_clip, 0.0, 1.0, "", False, 0.0, intro)]
    for n, (s, t0, t1) in enumerate(zip(segs, starts[1:], starts[2:])):
        crop = f"crop={s['crop']}," if s.get("crop") else ""
        pieces.append((f"s{n}", sdr(base, s["src"], work), float(s.get("ss", 0)), float(s.get("speed", 1)) * after,
                       crop, bool(s.get("window")), t0, t1))
    for name, src, ss, rate, crop, window, t0, t1 in pieces:
        slot = round(t1 - t0, 3)
        vf = f"{crop}{WIN if window else FILL},setpts=PTS/{rate},tpad=stop_mode=clone:stop_duration=30,{OUT}"
        run(FF, "-y", "-v", "error", "-ss", ss, "-t", f"{slot * rate + 0.5:.3f}", "-i", src, "-an", "-vf", vf,
            "-t", f"{slot:.3f}", "-c:v", "libx264", "-crf", 16, work / f"{name}.mp4")
        print(f"  {name:5} {t0:6.2f} to {t1:6.2f}  {slot:5.2f} s  {rate:g}x  {'window ' if window else ''}{Path(src).name}")
    ov = cfg.get("hook_overlay")
    if ov:
        first_end = raw_hook[0]["e"] if raw_hook else 0
        run(FF, "-y", "-v", "error", "-i", work / "hook.mp4", "-loop", 1, "-i", base / ov["img"], "-filter_complex",
            f"[0:v][1:v]overlay=x=(W-w)/2:y={ov.get('y', 1230)}:enable='gte(t,{first_end})':shortest=1,{OUT}[o]",
            "-map", "[o]", "-c:v", "libx264", "-crf", 16, work / "hook-ov.mp4")
        (work / "hook-ov.mp4").replace(work / "hook.mp4")
    # consecutive windows become one block over the blurred background
    from PIL import Image, ImageDraw, ImageFilter
    mk = Image.new("L", (WIN_W, WIN_H), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, WIN_W - 1, WIN_H - 1), RAD, fill=255)
    mk.save(work / "mask.png")
    sh = Image.new("RGBA", (WIN_W + 120, WIN_H + 120), (0, 0, 0, 0))
    al = Image.new("L", sh.size, 0)
    ImageDraw.Draw(al).rounded_rectangle((60, 72, 60 + WIN_W, 72 + WIN_H), RAD, fill=150)
    sh.putalpha(al.filter(ImageFilter.GaussianBlur(24)))
    sh.save(work / "shadow.png")
    order, block, bi = [], [], 0
    for name, *_rest, window, t0, t1 in pieces:
        if window:
            block.append((name, t1 - t0))
            continue
        if block:
            order.append(("win", block)); block = []
        order.append(("full", name))
    if block:
        order.append(("win", block))
    bg = cfg.get("background") or next(({"src": s["src"], "ss": s.get("ss", 0)} for s in segs if not s.get("window")), None)
    final_list = []
    for kind, item in order:
        if kind == "full":
            final_list.append(f"{item}.mp4"); continue
        bi += 1
        (work / f"win{bi}.txt").write_text("".join(f"file '{n}.mp4'\n" for n, _ in item))
        run(FF, "-y", "-v", "error", "-f", "concat", "-safe", 0, "-i", work / f"win{bi}.txt", "-c", "copy", work / f"win{bi}-raw.mp4")
        wlen = round(sum(s for _, s in item), 3)
        fc = (f"[0:v]{FILL},gblur=sigma=30,eq=brightness=-0.10:saturation=1.15,{OUT}[bg];"
              f"[1:v]format=yuva420p[fw];[2:v]format=gray[mk];[fw][mk]alphamerge[fg];"
              f"[bg][3:v]overlay={WIN_X - 60}:{WIN_Y - 60}[b2];[b2][fg]overlay={WIN_X}:{WIN_Y}:shortest=1,{OUT}[o]")
        run(FF, "-y", "-v", "error", "-stream_loop", -1, "-ss", bg["ss"], "-i", sdr(base, bg["src"], work),
            "-i", work / f"win{bi}-raw.mp4", "-loop", 1, "-i", work / "mask.png", "-loop", 1, "-i", work / "shadow.png",
            "-filter_complex", fc, "-map", "[o]", "-t", wlen, "-an", "-c:v", "libx264", "-crf", 16, work / f"win{bi}.mp4")
        final_list.append(f"win{bi}.mp4")
    (work / "list.txt").write_text("".join(f"file '{n}'\n" for n in final_list))
    run(FF, "-y", "-v", "error", "-f", "concat", "-safe", 0, "-i", work / "list.txt", "-c:v", "libx264", "-crf", 17,
        "-pix_fmt", "yuv420p", work / "video.mp4")
    return starts


def main():
    """reel_make.py <id> [--folder DIR] [--retranscribe] [--no-build]: runs under the reel editor's Python (Pillow)."""
    args = sys.argv[1:]
    rid = args[0]
    d = json.loads((Path(__file__).resolve().parent / "reels.json").read_text())
    r = next((x for x in d["reels"] if x["id"] == rid), None)
    if not r:
        sys.exit(f"no reel {rid}")
    folder = args[args.index("--folder") + 1] if "--folder" in args else None
    root = Path(__file__).resolve().parents[5]
    if not folder:
        if not r.get("project"):
            sys.exit(f"{rid} has no media project yet: reels.py new {rid}")
        folder = root / r["project"]
    if not r.get("vo"):
        sys.exit(f"{rid} has no voiceover lines: this assembler is for talking hook + voiceover reels")
    # the CTA line is said at the end unless the script already ends with it (1.1 did)
    cta_line = None if "לומי" in r["vo"][-1] else d["defaults"]["cta_voice"]
    make(rid, folder, r["hook"], r["vo"], cta_line, d["defaults"]["cta_screen"],
         retranscribe="--retranscribe" in args, build="--no-build" not in args)


if __name__ == "__main__":
    main()
