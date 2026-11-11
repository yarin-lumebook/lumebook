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
 8. Off by default since 11 Nov 2026 (Yarin: "ditch the 5 trials, lets have only one"): make writes the one reel above;
    `--trial` or `--trial-only` still builds the old trial set described here.
    Five trial reel versions (Yarin, 10 Nov 2026: "after i press create reel it gives me 5 different versions with
    different hook, zoom slightly in a random way and make them a tiny bit shorter or longer randomly so we could
    schedule them as trial reels and ig wont flag them as repetitive"): the reel editor's --trial build writes
    trial/reel-<id>-trial-1.mp4 to -5.mp4. Version 1 has the reel's hook, 2 to 5 the reel's "trial_hooks" in reels.json
    (Yarin's, edited on the card), else the "trial_hooks" Claude wrote into edit.json. Each version gets its own small
    zoom (1.02x to 1.08x at a random spot near the middle) and is 0.15 s to 0.8 s shorter or 0.15 s to 0.6 s longer
    (the last frame held), from a fresh seed each run; never mirrored (books and screens carry Hebrew). An earlier set
    moves to trial/earlier-<time>/. Whether this keeps Instagram from treating the uploads as repeats is not verified.

edit.json (in the reel's media folder, written by `reels.py new`, paths relative to that folder):

    {
      "hook_clip": "source/yarin/hook.mov",       Yarin's 2 s talking hook
      "hook_end": null,                           seconds; null = where his speech ends + 0.12 s
      "voice": "source/yarin/voice.m4a",          the voiceover take
      "voice_start": 0.0,                         skip a false start at the top of the take
      "speed_after_hook": 1.1,
      "background": {"src": "source/book.mov", "ss": 3.0},   blurred clip behind screen windows
      "hook_overlay": {"img": "source/cover.png", "y": 1230, "from": 0},  optional picture under the face, from the 2nd
                                                  hook word, or from "from" seconds: 0 puts this reel's cover on the first
                                                  frame (rule since 09 Nov 2026, research/matan-nistor-reels)
      "segments": [
        {"at": 0, "src": "source/cover.mov", "ss": 0.2},                    from voiceover line 0
        {"at": "כותבים", "src": "source/screen.mov", "ss": 3.0, "window": true},
        {"at": "ומעלים", "src": "source/wizard.mp4", "ss": 2.0, "window": true, "speed": 2, "crop": "887:1920:96:0"},
        {"at": "cta", "src": "source/flip.mov", "ss": 1.5}                  from the CTA line
      ]
    }

A reel that is one talking take (Yarin's whole script to camera, 10 Nov 2026) uses "take" instead of hook_clip, voice and
segments, and can lay pictures over the take while its sound runs on:

    {
      "take": "source/yarin/take.mov",
      "voice_start": 0.0, "speed_after_hook": 1.1,
      "hook_overlay": {"img": "source/cover.png", "from": 0, "y": 1230, "w": 420},   this reel's cover under the face while the hook is said
      "inserts": [
        {"at": "הכריכה", "src": "source/book.mov", "ss": 1.0},              from that word to the next script line
        {"at": 2, "until": "ודבר", "src": "source/preview.mov", "window": true, "speed": 1.5},   a screen recording in the window
        {"at": "תראו", "until": 2.0, "src": "source/mk-open.png"}           a still, 2 s, slow push-in
      ],
      "child_bg": ["source/pool-child-....mp4"],     optional: the child clips behind the pictures (default: the library's)

Since 11 Nov 2026 (Yarin): every still and every screen window sits over a darkened, slowed video of a child from the library
(library.py child-bg), a different child for each picture ("bg" on one insert picks its own). A drawn book (broll.py, transparent)
lies on it as it is; any other still (a GPT picture, a photo) is a rounded card. Stills glide in a push-in drawn frame by frame
(no shaking), cuts sit on the 30 fps frame grid, and a gap under a second between two pictures is closed so no frame of the take
slips in between. "fill" on a still is ignored now. An insert starts on the word that names what it shows.
      "trial_hooks": ["...", "...", "...", "..."]      four more top hooks for the trial versions (step 8)
    }

The hook clip always opens the reel; the first segment should start at line 0. Run it through reels.py:

    python3 research/israeli-product-reels/src/scripts/series-2026-11/reels.py make 1.7
    ... make 1.7                  the one reel (no trial versions since 11 Nov 2026)
    ... make 1.7 --trial          also the old set of five trial versions (only if Yarin asks again)
    ... make 1.7 --trial-only     only a fresh set of the five trial versions, from the reel.json the last make wrote
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
FPS = 30
TAIL = 3                                   # frames each insert is rendered past its cut (the overlay window cuts it on the frame)
FACE_GAP = 1.0                             # seconds: when the take would show for less than this between two pictures, the earlier
                                           # picture runs on to the next (Yarin, 11 Nov 2026: single frames of him slipped in between
                                           # B-rolls; the overlay windows also left 1 ms holes that let one frame through)
PUSH = 0.05                                # a still grows this much over its slot, drawn per frame with sub-pixel steps by Pillow
                                           # (ffmpeg's zoompan rounds to whole pixels, so pictures shook; Yarin, 11 Nov 2026)
CHILD_SLOW = 0.75                          # the child clip behind a picture plays at this speed, forward then backward
DARK = "gblur=sigma=3,lutyuv=y=val*0.52:u=128+(val-128)*0.7:v=128+(val-128)*0.7"   # the child behind a picture, darkened
READ_CPS = 17                             # principle T5: Hebrew on screen at most 17 characters a second
TRIAL_VERSIONS = 5                         # trial reel versions after the plain reel (Yarin, 10 Nov 2026)


def run(*a, **kw):
    return subprocess.run([str(x) for x in a], check=True, **kw)


def sound_hash(wav_path):
    import hashlib
    return hashlib.sha1(Path(wav_path).read_bytes()).hexdigest()


def transcript_is_stale(raw_path, wav_path):
    """True when words-raw.json is missing or was made from another voice-studio.wav (audit of 08 Nov 2026: a new take,
    or a changed voice_start or hook_end, kept the old words and so the old caption and cut times). The sound's hash
    is kept next to the transcript (words-raw.json.wav-sha1)."""
    mark = Path(str(raw_path) + ".wav-sha1")
    was = mark.read_text().strip() if mark.exists() else ""
    return not Path(raw_path).exists() or was != sound_hash(wav_path)


def mark_transcript(raw_path, wav_path):
    Path(str(raw_path) + ".wav-sha1").write_text(sound_hash(wav_path) + "\n")


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
        # aresample first_pts=0: an iPhone take's audio can start after its picture (E3498895: 0.78 s); without the
        # padding the wav starts at the first sound and every cut pairs the picture with sound from later (lips late)
        run(FF, "-y", "-v", "error", "-ss", cfg.get("voice_start", 0), "-i", src, "-vn", "-ac", 1, "-ar", 48000,
            "-af", "aresample=async=1:first_pts=0", work / "take-raw.wav")
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
    if retranscribe or transcript_is_stale(raw_path, work / "voice-studio.wav"):
        import os
        run("/usr/bin/python3", EDITOR.parent / "transcribe.py", work / "voice-studio.wav", raw_path,
            env=dict(os.environ, KMP_DUPLICATE_LIB_OK="TRUE"))
        mark_transcript(raw_path, work / "voice-studio.wav")
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
        line_t = [cue(i) for i in range(len(lines))]
        cta_t = cue("cta")
        if cfg.get("inserts") or cfg.get("hook_overlay"):
            starts = take_inserts(base, work, cfg, cue, line_t, cta_t, intro, end, rid)
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
    cta_i = max((i for i, w in enumerate(words) if norm(w["w"]) in ("תכתבו", "תכתבי", "כתבו")), default=line_start[-1])
    cta_from = tm(words[cta_i]["s"])
    job = {"source": "work/make/video.mp4", "name": f"reel-{rid.replace('.', '-')}",
           "hooks": [hook], "hook_seconds": max(intro, hook_read), "captions": "words.json",
           "cta": {"text": cta_screen, "seconds": round(end - cta_from + 0.05, 2), "highlight": True},
           "versions": 1, "flip": False, "audio": "work/make/sound.wav"}
    tops = [{"text": c["text"], "s": max(cue(c["at"]) + LEAD, job["hook_seconds"]),
             "size": c.get("size", 150 if len(c["text"]) <= 2 else 64), "until": c.get("until")} for c in cfg.get("top_cards", [])]   # a lone number reads big
    for i, c in enumerate(tops):             # each card stays until the next one, or the CTA, or its own "until" cue
        nxt = tops[i + 1]["s"] if i + 1 < len(tops) else cta_from
        u = c.pop("until")
        c["e"] = round(max(min(nxt, cue(u) + LEAD) if u is not None else nxt, c["s"] + 1.0), 3)
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


def trial_hooks_for(rid, hook, base, mine):
    """The five hooks of the trial versions: the reel's hook first, then reels.json "trial_hooks" (mine), else the ones Claude wrote
    into edit.json for a reel job. Returns (hooks, note): fewer than five hooks repeat in order, and note says so."""
    extra = [h for h in (mine or []) if isinstance(h, str) and h.strip()]
    if not extra:
        try:
            extra = [h for h in json.loads((base / "edit.json").read_text()).get("trial_hooks") or [] if isinstance(h, str) and h.strip()]
        except (OSError, ValueError):
            extra = []
    seen, hooks = set(), []
    for h in [hook] + extra:
        k = " ".join(h.split())
        if k not in seen:
            seen.add(k); hooks.append(h.strip())
    hooks = hooks[:TRIAL_VERSIONS]
    note = "" if len(hooks) >= TRIAL_VERSIONS else (
        f"only {len(hooks)} different hook{'s' if len(hooks) > 1 else ''} for {TRIAL_VERSIONS} trial versions: write trial_hooks for {rid} in reels.json")
    return hooks, note


def trial(rid, base, hooks):
    """Five trial versions from the reel.json the plain build used (step 8 of the docstring)."""
    import shutil
    from datetime import datetime
    job = json.loads((base / "reel.json").read_text())
    name = job["name"]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    tdir = base / "trial"
    old = list(tdir.glob(f"{name}-trial-*.mp4")) + [f for f in (tdir / f"{name}-versions.json", tdir / f"{name}-qc.jpg") if f.exists()]
    if old:
        keep = tdir / f"earlier-{stamp}"
        keep.mkdir(parents=True, exist_ok=True)
        for f in old:
            shutil.move(str(f), keep / f.name)
        print(f"trial: the earlier set moved to trial/{keep.name}/")
    read = max(len(h.replace("\n", " ")) / READ_CPS for h in hooks)
    tj = dict(job, hooks=hooks, versions=TRIAL_VERSIONS, flip=False, seed=f"{name}-{stamp}",
              hook_seconds=round(max(job.get("hook_seconds", 0), read), 2))
    (base / "reel-trial.json").write_text(json.dumps(tj, ensure_ascii=False, indent=1) + "\n")
    print(f"trial: {TRIAL_VERSIONS} versions, {len(hooks)} hooks, each its own zoom and a little shorter or longer")
    run(EDITOR_PY, EDITOR, "build", base / "reel-trial.json", "--trial")


IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")


def child_order(base, cfg, rid):
    """The child clips that go behind this reel's pictures, in turn (Yarin, 11 Nov 2026: "always have a darken video of a child in
    the bg"): edit.json "child_bg" (paths in the reel folder) when set, else every child-bg clip of the library, starting at a
    different one for each reel."""
    if cfg.get("child_bg"):
        paths = [base / p for p in cfg["child_bg"]]
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import library
        paths = library.child_bgs()
    if not paths:
        sys.exit("no child clip for the background: library.py list child-bg")
    import hashlib
    rot = int(hashlib.sha1(rid.encode()).hexdigest(), 16) % len(paths)
    return paths[rot:] + paths[:rot]


def dark_bg(src, work):
    """One child clip as a background that loops without a jump: full frame, slowed, forward then backward, blurred a little and
    darkened. Kept in work/make/bg/."""
    out = work / "bg" / (Path(src).stem + ".mp4")
    if out.exists() and out.stat().st_mtime >= Path(src).stat().st_mtime:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    fc = (f"[0:v]{FILL},setpts=PTS/{CHILD_SLOW},fps={FPS},{DARK},split[f][r0];[r0]reverse[r];"
          f"[f][r]concat=n=2:v=1:a=0,{OUT}[o]")
    run(FF, "-y", "-v", "error", "-i", sdr(Path("/"), src, work), "-filter_complex", fc, "-map", "[o]", "-an",
        "-c:v", "libx264", "-crf", 18, out)
    return out


def still_layer(src, crop):
    """A still as a 1080x1920 RGBA layer over the child: a drawn object on a transparent ground (broll.py) as it is, any other
    picture (a GPT gag, a cover, a photo) as a rounded card with a light rim and a soft shadow."""
    from PIL import Image, ImageDraw, ImageFilter
    with Image.open(src) as im0:
        im = im0.convert("RGBA")
    if crop:
        w, h, x, y = (int(v) for v in crop.split(":"))
        im = im.crop((x, y, x + w, y + h))
    W, H = im.size
    if im.getchannel("A").getextrema()[0] < 250:
        if abs(W / H - 9 / 16) < 0.01:
            return im.resize((1080, 1920), Image.LANCZOS)
        im.thumbnail((1000, 1400), Image.LANCZOS)
        lay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        lay.alpha_composite(im, ((1080 - im.width) // 2, max(120, 860 - im.height // 2)))
        return lay
    s = min(840 / W, 1240 / H)           # leaves the child around the card in view
    cw, ch = round(W * s), round(H * s)
    card = im.resize((cw, ch), Image.LANCZOS)
    m = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), 44, fill=255)
    card.putalpha(m)
    x, y = (1080 - cw) // 2, max(120, 860 - ch // 2)
    lay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sh = Image.new("L", (1080, 1920), 0)
    ImageDraw.Draw(sh).rounded_rectangle((x + 6, y + 30, x + cw - 6, y + ch + 30), 44, fill=200)
    lay.putalpha(sh.filter(ImageFilter.GaussianBlur(34)))
    lay.alpha_composite(card, (x, y))
    ImageDraw.Draw(lay).rounded_rectangle((x, y, x + cw - 1, y + ch - 1), 44, outline=(255, 255, 255, 70), width=2)
    return lay


def render_still(layer, frames, bg, out):
    """The layer over the darkened child for `frames` frames, growing by PUSH with an ease-out about its own middle. Each frame is
    drawn by Pillow with bicubic sub-pixel steps and piped to ffmpeg, so the picture glides instead of shaking."""
    from PIL import Image
    box = layer.getbbox() or (0, 0, 1080, 1920)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    pre = layer.convert("RGBa")              # premultiplied: no dark fringe on the object's edges when it is resampled
    grow = 1 + PUSH                          # only the area the object can reach is drawn each frame
    rx0, ry0 = max(0, int(cx - (cx - box[0]) * grow) - 2), max(0, int(cy - (cy - box[1]) * grow) - 2)
    rx1, ry1 = min(1080, int(cx + (box[2] - cx) * grow) + 3), min(1920, int(cy + (box[3] - cy) * grow) + 3)
    blank = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    p = subprocess.Popen([FF, "-y", "-v", "error", "-stream_loop", "-1", "-i", str(bg),
                          "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "1080x1920", "-framerate", str(FPS), "-i", "-",
                          "-filter_complex", f"[0:v]{OUT}[b];[b][1:v]overlay=0:0:format=auto,{OUT}[o]", "-map", "[o]",
                          "-frames:v", str(frames), "-an", "-c:v", "libx264", "-crf", "16", str(out)], stdin=subprocess.PIPE)
    def draw(k):
        x = k / max(1, frames - 1)
        a = 1 / (1 + PUSH * (1 - (1 - x) ** 2))
        # output pixel (rx0 + u, ry0 + v) reads input ((rx0 + u - cx) * a + cx, ...): sub-pixel steps, so no shake
        part = pre.transform((rx1 - rx0, ry1 - ry0), Image.AFFINE,
                             (a, 0, cx + (rx0 - cx) * a, 0, a, cy + (ry0 - cy) * a), resample=Image.BILINEAR)
        f = blank.copy()
        f.paste(part.convert("RGBA"), (rx0, ry0))
        return f.tobytes()
    from concurrent.futures import ThreadPoolExecutor
    try:
        with ThreadPoolExecutor(4) as pool:
            for b0 in range(0, frames, 8):
                for raw in pool.map(draw, range(b0, min(frames, b0 + 8))):
                    p.stdin.write(raw)
    finally:
        p.stdin.close()
    if p.wait():
        raise subprocess.CalledProcessError(p.returncode, "ffmpeg (still over the child)")


def take_inserts(base, work, cfg, cue, line_t, cta_t, intro, end, rid):
    """Pictures over a one-take reel (10 Nov 2026: Yarin's nine talking takes, "edit them"): the take's sound runs on, and from
    each insert's cue the picture shows what is said (the book, a cover, a screen recording) until its "until" (a line number or
    a word, or seconds written as a decimal such as 2.0), else until the next script line starts.

    Since 11 Nov 2026 (Yarin): every still and every screen window sits over a darkened video of a child (child_order, dark_bg);
    a still glides in a slow push-in drawn per frame (render_still: no more shaking); a screen recording sits in the rounded
    720x1440 window; a video clip fills the frame. Every cut is on a frame of the 30 fps grid and the overlay windows meet
    exactly, and when the take would show for less than FACE_GAP between two pictures the earlier one runs on, so no single
    frame of Yarin slips in between B-rolls. hook_overlay puts a picture (this reel's cover) on the take from "from" seconds to
    the end of the spoken hook (rule M1, 09 Nov 2026), or on to the first picture when that starts within FACE_GAP.
    Inserts never run into the לומי card. Writes work/video.mp4 again; returns the cut times."""
    last_f = int(round(end * FPS))
    ins = []
    for n, s in enumerate(cfg.get("inserts") or []):
        t0 = max(cue(s["at"]), 0.0)
        u = s.get("until")   # a line number (int) or word of the script, or seconds written as a decimal (2.0)
        if isinstance(u, float):
            t1 = t0 + u
        elif u is not None:
            t1 = cue(u)
        else:
            t1 = next((t for t in line_t if t > t0 + 0.3), cta_t)
        t1 = min(t1, cta_t, end)
        if t1 - t0 < 0.3:
            print(f"  insert {n} skipped: {t1 - t0:.2f} s between its cues")
            continue
        ins.append([n, s, int(round(t0 * FPS)), min(int(round(t1 * FPS)), last_f)])
    ins.sort(key=lambda x: x[2])
    for a, b in zip(ins, ins[1:]):
        gap = b[2] - a[3]
        if gap < -3:
            sys.exit(f"inserts overlap: {a[2] / FPS:.2f} to {a[3] / FPS:.2f} and {b[2] / FPS:.2f}")
        if gap < FACE_GAP * FPS:
            if gap > 0:
                print(f"  insert {a[0]} runs on {gap} frame(s) to meet the next: the take would have flashed between them")
            a[3] = b[2]
    (work / "take-only.mp4").write_bytes((work / "video.mp4").read_bytes())
    kids = child_order(base, cfg, rid)
    clips = []
    for k, (n, s, f0, f1) in enumerate(ins):
        frames = f1 - f0 + TAIL
        slot = frames / FPS
        src = base / s["src"]
        out = work / f"ins{n}.mp4"
        crop = f"crop={s['crop']}," if s.get("crop") else ""
        bg = None
        if src.suffix.lower() in IMAGE_EXT or s.get("window"):
            bg = dark_bg(base / s["bg"] if s.get("bg") else kids[k % len(kids)], work)
        if src.suffix.lower() in IMAGE_EXT:
            render_still(still_layer(src, s.get("crop")), frames, bg, out)
        else:
            rate = float(s.get("speed", 1))
            clip = sdr(base, s["src"], work)
            if s.get("window"):
                fc = (f"[0:v]{OUT}[bg];"
                      f"[1:v]{crop}{WIN},setpts=PTS/{rate},tpad=stop_mode=clone:stop_duration=30,{OUT},format=yuva420p[fw];"
                      f"[2:v]format=gray[mk];[fw][mk]alphamerge[fg];"
                      f"[bg][3:v]overlay={WIN_X - 60}:{WIN_Y - 60}[b2];[b2][fg]overlay={WIN_X}:{WIN_Y},{OUT}[o]")
                window_art(work)
                run(FF, "-y", "-v", "error", "-stream_loop", -1, "-i", bg,
                    "-ss", s.get("ss", 0), "-t", f"{slot * rate + 0.5:.3f}", "-i", clip,
                    "-loop", 1, "-i", work / "mask.png", "-loop", 1, "-i", work / "shadow.png",
                    "-filter_complex", fc, "-map", "[o]", "-an", "-frames:v", frames, "-c:v", "libx264", "-crf", 16, out)
            else:
                vf = f"{crop}{FILL},setpts=PTS/{rate},tpad=stop_mode=clone:stop_duration=30,{OUT}"
                run(FF, "-y", "-v", "error", "-ss", s.get("ss", 0), "-t", f"{slot * rate + 0.5:.3f}", "-i", clip, "-an", "-vf", vf,
                    "-frames:v", frames, "-c:v", "libx264", "-crf", 16, out)
        clips.append((out, f0, f1))
        print(f"  insert {f0 / FPS:6.2f} to {f1 / FPS:6.2f}  {(f1 - f0) / FPS:5.2f} s  {'window ' if s.get('window') else ''}{src.name}"
              + (f"  over {Path(bg).stem}" if bg else ""))
    # each window is half a frame wider than its frames, so a frame time never falls between two windows
    win = lambda a, b: f"between(t,{(a - 0.5) / FPS:.4f},{(b - 0.5) / FPS:.4f})"
    ov = cfg.get("hook_overlay")
    inputs, fc, last = ["-i", work / "take-only.mp4"], "", "[0:v]"
    for k, (out, f0, f1) in enumerate(clips, 1):
        inputs += ["-i", out]
        fc += f"[{k}:v]setpts=PTS-STARTPTS+{f0}/{FPS}/TB[i{k}];{last}[i{k}]overlay=0:0:enable='{win(f0, f1)}':eof_action=pass[v{k}];"
        last = f"[v{k}]"
    if ov:
        k = len(clips) + 1
        inputs += ["-loop", 1, "-i", base / ov["img"]]
        fr = int(round(float(ov.get("from", 0)) * FPS))
        w = int(ov.get("w", 380))   # just under the captions (they end at 65% of the height), clear of the face
        upto = int(round(intro * FPS))
        first = min((f0 for _, f0, _ in clips if f0 > fr), default=None)
        if first is not None and first - upto < FACE_GAP * FPS:   # the cover gives way to the first picture, or runs on to it
            upto = first
        fc += (f"[{k}:v]scale={w}:-2,format=rgba[ov];{last}[ov]overlay=x=(W-w)/2:y={ov.get('y', 1270)}:"
               f"enable='{win(fr, upto)}':shortest=1[vo];")
        last = "[vo]"
        print(f"  cover {fr / FPS:6.2f} to {upto / FPS:6.2f}  {Path(ov['img']).name}")
    fc += f"{last}{OUT}[o]"
    run(FF, "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[o]", "-an", "-t", end,
        "-c:v", "libx264", "-crf", 17, work / "video.mp4")
    (work / "inserts.json").write_text(json.dumps([{"insert": n, "src": s["src"], "from_frame": f0, "to_frame": f1}
                                                    for n, s, f0, f1 in ins], ensure_ascii=False, indent=1) + "\n")
    return sorted({0.0, intro, end} | {round(f / FPS, 3) for _, a, b in clips for f in (a, b)})


def window_art(work):
    """The rounded mask and the soft shadow of the screen window (reel 1.1 v9)."""
    if (work / "mask.png").exists() and (work / "shadow.png").exists():
        return
    from PIL import Image, ImageDraw, ImageFilter
    mk = Image.new("L", (WIN_W, WIN_H), 0)
    ImageDraw.Draw(mk).rounded_rectangle((0, 0, WIN_W - 1, WIN_H - 1), RAD, fill=255)
    mk.save(work / "mask.png")
    sh = Image.new("RGBA", (WIN_W + 120, WIN_H + 120), (0, 0, 0, 0))
    al = Image.new("L", sh.size, 0)
    ImageDraw.Draw(al).rounded_rectangle((60, 72, 60 + WIN_W, 72 + WIN_H), RAD, fill=150)
    sh.putalpha(al.filter(ImageFilter.GaussianBlur(24)))
    sh.save(work / "shadow.png")


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
        first_end = float(ov["from"]) if isinstance(ov.get("from"), (int, float)) else (raw_hook[0]["e"] if raw_hook else 0)
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
    """reel_make.py <id> [--folder DIR] [--retranscribe] [--no-build] [--no-trial] [--trial-only]: runs under the reel editor's
    Python (Pillow)."""
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
    # (Yarin's own closing words may run over two lines, 10 Nov 2026)
    cta_line = None if any("לומי" in l for l in r["vo"][-2:]) else d["defaults"]["cta_voice"]
    base = Path(folder)
    if "--trial-only" not in args:
        # a reel's own closing card (a grandmother reel says תכתבי ... ואשלח לך, 10 Nov 2026), else the default
        make(rid, folder, r["hook"], r["vo"], cta_line, r.get("cta_screen") or d["defaults"]["cta_screen"],
             retranscribe="--retranscribe" in args, build="--no-build" not in args)
    # one version per reel (Yarin, 11 Nov 2026: "ditch the 5 trials, lets have only one"): the trial set is made only
    # when asked for with --trial or --trial-only
    if not ({"--trial", "--trial-only"} & set(args)) or "--no-trial" in args or "--no-build" in args:
        return
    if not (base / "reel.json").exists():
        sys.exit(f"{rid}: no reel.json yet, run make without --trial-only first")
    hooks, note = trial_hooks_for(rid, r["hook"], base, r.get("trial_hooks"))
    if note:
        print("  check:", note)
    trial(rid, base, hooks)


if __name__ == "__main__":
    main()
