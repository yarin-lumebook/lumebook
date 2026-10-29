"""Reel editor: burned-in hook at the top, optional word-by-word captions in the lower half, and for trial reels
a seeded horizontal flip, a small zoom and a slight trim per version, so no two uploads are the same file.
Generalised from media/projects/2026-10-25-genjutsu-lite-trends/captioned/build_captions.py (Yarin, 25 and 26 Oct 2026).

Run with a Python that has Pillow (the watch-video .venv):
  PY=~/.claude/skills/watch-video/.venv/bin/python
  $PY reel_editor.py transcribe VIDEO words.json     # Hebrew word timings (ivrit-ai whisper, through /usr/bin/python3)
  $PY reel_editor.py build reel.json                 # plain versions, one per hook
  $PY reel_editor.py build reel.json --trial         # trial versions: flip, zoom, trim differ per version
Config keys are in the skill's SKILL.md. Paths in reel.json are relative to the file."""
import json, random, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCRIPTS = Path(__file__).parent
W, H = 1080, 1920
# Instagram's Reels safe zone (research/israeli-product-reels/playbook.md, section 8): keep text out of the top 14%,
# the bottom 35% and the outer 6% of each side, where the player draws its header, caption and buttons.
TOP = int(H * 0.15)
SAFE_BOTTOM = int(H * 0.65)
MAX_W = W - 2 * int(W * 0.06)
SF = "/System/Library/Fonts/SFHebrew.ttf"      # stand-in for Instagram's default font, as on the 19 to 26 Oct reels
SF_LATIN = "/System/Library/Fonts/SFNS.ttf"    # SF Hebrew has no Latin letters; SF Pro supplies them
BANNED = [(re.compile("[‐-―−־;-]"), "dash, hyphen, maqaf or semicolon"),
          (re.compile("לומיבוק"), "write לומבוק"),
          (re.compile(r"\bAI\b|בינה מלאכותית", re.I), "no AI in audience copy")]

# ---------- text drawing (RTL by hand: this Pillow has no raqm) ----------

def visual(line):
    # RTL line drawn left to right: reverse it, then put Latin words and numbers back in reading order
    return re.sub(r"[A-Za-z0-9]+", lambda m: m.group(0)[::-1], line[::-1])

def font(size):
    he = ImageFont.truetype(SF, size); he.set_variation_by_name("Bold")
    la = ImageFont.truetype(SF_LATIN, size); la.set_variation_by_name("Bold")
    return he, la

_tofu = {}   # the missing-glyph box per font size (a mask from one size never matches another)
def runs(vis, fonts):
    he, la = fonts
    if he.size not in _tofu: _tofu[he.size] = bytes(he.getmask("\U000F0000"))
    out = []
    for c in vis:
        f = la if (c != " " and bytes(he.getmask(c)) == _tofu[he.size]) else he
        if out and out[-1][1] is f: out[-1][0] += c
        else: out.append([c, f])
    return out

def width(d, vis, fonts): return sum(d.textlength(t, font=f) for t, f in runs(vis, fonts))
def draw(d, xy, vis, fonts, **kw):
    x, y = xy
    for t, f in runs(vis, fonts):
        d.text((x, y), t, font=f, **kw); x += d.textlength(t, font=f)

EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿][\U0001F3FB-\U0001F3FF️]?$")
def emoji_img(seq, px, tmp):
    png = tmp / f"emoji-{'-'.join(f'{ord(c):x}' for c in seq)}.png"
    if not png.exists():
        subprocess.run(["swift", str(SCRIPTS / "emoji_png.swift"), seq, str(png), "160"], check=True)
    im = Image.open(png).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * px / im.height), px), Image.LANCZOS)

BRAND_PURPLE = "#5B2BD6"   # --lb-violet in shared/design/lumebook.css, the logo's purple

def block(im, shadow, text, size, tmp, top=None, bottom=None, cx=W / 2, highlight=None):
    """Centred RTL lines (\\n splits them) around x = cx; an emoji at the end goes at the left end of the last line.
    highlight: a colour for an Instagram style rounded box behind each line (the boxes join); no shadow then."""
    d = ImageDraw.Draw(im); sd = ImageDraw.Draw(shadow)
    m = EMOJI.search(text); emo_seq = m.group(0) if m else None
    if emo_seq: text = text[:-len(emo_seq)].rstrip()
    lines = [visual(l) for l in text.split("\n")]
    f = font(size)
    pad = lambda s: 2 * int(s * 0.32) if highlight else 0
    max_w = min(MAX_W, 2 * min(cx - (W - MAX_W) / 2, (W + MAX_W) / 2 - cx))   # stay inside the side margins
    while max(width(d, l, f) for l in lines) + (size if emo_seq else 0) + pad(size) > max_w:
        size -= 2; f = font(size)
    h = int(size * 1.22)
    if top is None: top = bottom - len(lines) * h
    emo = emoji_img(emo_seq, int(size * 1.05), tmp) if emo_seq else None
    gap = int(size * 0.18)
    rows = []
    for i, vis in enumerate(lines):
        extra = gap + emo.width if (emo and i == len(lines) - 1) else 0
        rows.append((vis, extra, width(d, vis, f) + extra, top + i * h))
    if highlight:
        px, py = pad(size) / 2, int(size * 0.14)
        for vis, extra, total, y in rows:
            d.rounded_rectangle((cx - total / 2 - px, y - py + size * 0.08, cx + total / 2 + px, y + h + py),
                                radius=int(size * 0.3), fill=highlight)
    for vis, extra, total, y in rows:
        x = cx - total / 2 + extra
        if extra:
            im.alpha_composite(emo, (int(cx - total / 2), int(y + (h - emo.height) / 2 + size * 0.04)))
        if not highlight:
            draw(sd, (x, y + 3), vis, f, fill=(0, 0, 0, 200), stroke_width=4, stroke_fill=(0, 0, 0, 200))
        draw(d, (x, y), vis, f, fill="white")
    return dict(px=size, y=[top, top + len(lines) * h])

# ---------- helpers ----------

def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,r_frame_rate,color_transfer:format=duration", "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    num, den = map(int, (v or {}).get("r_frame_rate", "0/1").split("/"))
    return dict(duration=float(j["format"]["duration"]), fps=min(round(num / den, 3), 60), video=v is not None,
                audio=any(s["codec_type"] == "audio" for s in j["streams"]),
                hlg=(v or {}).get("color_transfer") in ("arib-std-b67", "smpte2084"))

# ---------- sound: keep the source's, else the Higgsfield reference's, else ask ----------

MEDIA_EXT = {".m4a", ".mp3", ".wav", ".aac", ".mp4", ".mov"}
OUTPUT_DIRS = {"final", "trial", "work", "captioned", "qc", "_cards", "results"}

def job_folder(path):
    """The media/projects/<job> folder the source sits in (else its own folder)."""
    for p in path.parents:
        if p.parent.name == "projects" and p.parent.parent.name == "media": return p
    return path.parent

def ref_files(src, job):
    """Reference clips and sounds in the job folder: files under refs/ or audio/, or named original, reference, ref
    or mute. Those named after the source's slug (02-ben-window from 02-ben-window-v1-1080p) win."""
    slug = re.sub(r"-v\d+([-_].*)?$", "", src.stem)
    found = []
    for f in job.rglob("*"):
        rel = f.relative_to(job).parts
        if (f.suffix.lower() not in MEDIA_EXT or len(rel) > 4 or f == src or OUTPUT_DIRS & set(rel[:-1])
                or "caption" in f.name or "trial" in f.name): continue
        if {"refs", "audio"} & set(rel[:-1]) or re.search(r"original|reference|(^|[-_])ref([-_.]|$)|mute", f.name):
            found.append(f)
    named = [f for f in found if slug in f.stem]
    # a job-level reference (reference-original.mp4) only counts when no file names another reel
    return slug, named or [f for f in found if not re.match(r"\d\d-", f.name)]

def lum_series(path, fps=25):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-an", "-vf", f"fps={fps},scale=16:16,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = [raw[i:i + 256] for i in range(0, len(raw) - 255, 256)]
    return [sum(f) / 256 for f in fr], [0.0] + [sum(abs(a - b) for a, b in zip(f, g)) / 256 for f, g in zip(fr, fr[1:])]

def ref_offset(ref, orig, fps=25):
    """Where the trimmed reference (what Higgsfield got) starts in the original: brightness and motion curves
    matched over every lag. Tested on 26 Oct: 3.08 s for the truck jump (3.04 s used), 8.72 s for the fridge (8.7 s)."""
    def z(x):
        m = sum(x) / len(x); sd = (sum((v - m) ** 2 for v in x) / len(x)) ** 0.5 or 1
        return [(v - m) / sd for v in x]
    (rl, rm), (ol, om) = lum_series(ref, fps), lum_series(orig, fps)
    n = len(rl); zl, zm = z(rl), z(rm); best = (-9.0, 0)
    for lag in range(len(ol) - n + 1):
        c = (sum(a * b for a, b in zip(zl, z(ol[lag:lag + n]))) + sum(a * b for a, b in zip(zm, z(om[lag:lag + n])))) / (2 * n)
        best = max(best, (c, lag))
    return round(best[1] / fps, 2), round(best[0], 2)

def pick_audio(cfg, base, src, has_audio):
    """Returns (file or None, offset seconds, note). None with note 'source' keeps the source's own sound.
    Exits with status 3 and NO AUDIO when there is nothing to use, so the caller asks Yarin for a sound."""
    a = cfg.get("audio")
    if a == "none": return None, 0, "silent (audio: none)"
    if a and a != "source":
        return (base / a).resolve(), float(cfg.get("audio_offset", 0)), f"given: {a}"
    if has_audio: return None, 0, "source"
    if a == "source": sys.exit("audio is 'source' but the source has no sound")
    job = job_folder(src)
    slug, refs = ref_files(src, job)
    info = {f: probe(f) if f.suffix.lower() in {".mp4", ".mov"} else dict(audio=True, video=False) for f in refs}
    sounds = [f for f in refs if info[f].get("audio")]
    audio_only = [f for f in sounds if not info[f].get("video", True)]
    pool = audio_only or sounds
    if not pool:
        sys.exit(f"NO AUDIO: {src.name} is silent and no reference sound was found in {job} "
                 f"(looked at: {', '.join(f.name for f in refs) or 'nothing'}). Ask Yarin for a sound file, then set "
                 f'"audio" (and "audio_offset" if needed) in reel.json, or "audio": "none" to add the sound in Instagram.')
    if len(pool) > 1:
        sys.exit("NO AUDIO: several reference sounds could fit, ask Yarin which one and set \"audio\" in reel.json:\n  "
                 + "\n  ".join(str(f.relative_to(job)) for f in pool))
    sound = pool[0]
    if "audio_offset" in cfg: return sound, float(cfg["audio_offset"]), f"reference: {sound.relative_to(job)}"
    # The result follows the trimmed, muted reference; the sound belongs to the untrimmed original
    mutes = [f for f in refs if info[f].get("video", True) and not info[f].get("audio")]
    origs = [f for f in refs if info[f].get("video", True) and info[f].get("audio")]
    if len(mutes) == 1 and len(origs) == 1:
        off, score = ref_offset(mutes[0], origs[0])
        note = f"reference: {sound.relative_to(job)} from {off}s (matched {mutes[0].name} in {origs[0].name}, score {score})"
        if score < 0.7: note += " LOW MATCH, check the sync or set audio_offset"
        return sound, off, note
    return sound, 0.0, f"reference: {sound.relative_to(job)} from 0s (no muted reference + original pair to sync from)"

def lint(texts):
    bad = [f"  {where}: {why}: {t!r}" for where, t in texts for rx, why in BANNED if t and rx.search(t)]
    if bad:
        sys.exit("Audience text breaks the project rules, fix the config or words file:\n" + "\n".join(bad))

def caption_cards(words, per_card):
    """Group words into cards: per_card words each, a new card after a pause of 0.6 s or more."""
    cards, cur = [], []
    for w in words:
        if cur and (len(cur) == per_card or w["s"] - cur[-1]["e"] >= 0.6):
            cards.append(cur); cur = []
        cur.append(w)
    if cur: cards.append(cur)
    out = []
    for i, c in enumerate(cards):
        nxt = cards[i + 1][0]["s"] if i + 1 < len(cards) else None
        end = c[-1]["e"] + 0.25
        if nxt is not None and nxt - c[-1]["e"] < 0.6: end = nxt   # keep the text on screen until the next word
        out.append(dict(text=" ".join(w["w"] for w in c), s=c[0]["s"], e=end))
    return out

# ---------- trial variation ----------

def trial_params(n, seed, flip_ok, length):
    """Seeded and spread out: about half flipped (never all the same way), zooms and cuts evenly spread then
    shuffled, so no two versions share a zoom or a length."""
    rng = random.Random(seed)
    flips = [i % 2 == 0 for i in range(n)] if flip_ok else [False] * n
    if n == 1 and flip_ok: flips = [rng.random() < 0.5]
    rng.shuffle(flips)
    zooms = [1.02 + 0.06 * (i + 0.5) / n + rng.uniform(-0.02, 0.02) / n for i in range(n)]
    max_cut = min(0.8, length * 0.06)
    cuts = [0.15 + (max_cut - 0.15) * (i + 0.5) / n + rng.uniform(-0.1, 0.1) * (max_cut - 0.15) / n for i in range(n)]
    rng.shuffle(zooms); rng.shuffle(cuts)
    out = []
    for i in range(n):
        start = round(min(0.12, cuts[i] * rng.uniform(0.0, 0.4)), 2)   # keep the opening frame nearly intact
        out.append(dict(flip=flips[i], zoom=round(zooms[i], 3),
                        anchor_x=round(rng.uniform(0.25, 0.75), 2), anchor_y=round(rng.uniform(0.3, 0.7), 2),
                        trim_start=start, trim_end=round(cuts[i] - start, 2)))
    return out

# ---------- commands ----------

def transcribe(video, out):
    import os
    env = dict(os.environ, KMP_DUPLICATE_LIB_OK="TRUE")
    subprocess.run(["/usr/bin/python3", str(SCRIPTS / "transcribe.py"), video, out], check=True, env=env)

def build(cfg_path, trial):
    cfg_path = Path(cfg_path).resolve(); base = cfg_path.parent
    cfg = json.load(open(cfg_path))
    src = (base / cfg["source"]).resolve()
    name = cfg.get("name", src.stem)
    hooks = cfg.get("hooks") or [cfg["hook"]]
    n = int(cfg.get("versions", len(hooks)))
    cta = cfg.get("cta")
    bottom = cfg.get("bottom")
    words = json.load(open(base / cfg["captions"])) if cfg.get("captions") else []
    lint([("hook", h) for h in hooks] + [("cta", cta and cta["text"]), ("bottom", bottom)]
         + [(f"caption word at {w['s']}s", w["w"]) for w in words])

    out_dir = base / cfg.get("out", "trial" if trial else "final"); out_dir.mkdir(parents=True, exist_ok=True)
    work = base / cfg.get("work", "work"); work.mkdir(exist_ok=True)
    info = probe(src)
    sound, sound_off, sound_note = pick_audio(cfg, base, src, info["audio"])
    print("sound:", sound_note)
    if info["hlg"]:   # iPhone HDR: the local ffmpeg cannot tone-map well, avconvert can (reel-build-toolchain memory)
        sdr = work / f"{src.stem}-sdr.mov"
        if not sdr.exists():
            subprocess.run(["avconvert", "--preset", "Preset1920x1080", "--source", str(src), "--output", str(sdr)], check=True)
        src, info = sdr, probe(sdr)
    fps, dur = info["fps"], info["duration"]
    params = trial_params(n, cfg.get("seed", name), cfg.get("flip", True), dur) if trial else [{}] * n

    hook_size, cap_size = cfg.get("hook_size", 64), cfg.get("caption_size", 74)
    cap_bottom = SAFE_BOTTOM - (90 if bottom else 0)
    record = {}
    for i in range(n):
        p = dict(params[i]); hook = hooks[i % len(hooks)]
        s = p.get("trim_start", 0.0); e = dur - p.get("trim_end", 0.0); length = round(e - s, 3)
        cta_start = length - cta.get("seconds", 2.5) if cta else length
        cards = [dict(c, s=c["s"] - s, e=min(c["e"] - s, length))
                 for c in caption_cards(words, cfg.get("words_per_card", 1)) if c["e"] - s > 0 and c["s"] - s < length]
        cuts = sorted({0.0, length, max(cta_start, 0.0)} | {max(c["s"], 0.0) for c in cards} | {c["e"] for c in cards})
        cuts = [t for t in cuts if 0 <= t <= length]
        tmp = work / f"cards-{name}-{i + 1}"; tmp.mkdir(exist_ok=True)
        segs, cache, layout = [], {}, {}
        for a, b in zip(cuts, cuts[1:]):
            if b - a < 0.01: continue
            mid = (a + b) / 2
            top_text = cta["text"] if mid >= cta_start else hook
            word = next((c["text"] for c in cards if c["s"] <= mid < c["e"]), None)
            key = (top_text, word)
            if key not in cache:
                im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                is_cta = top_text != hook
                hl = cta.get("highlight") if is_cta else None
                lay = {"cta" if is_cta else "hook": block(im, sh, top_text, hook_size, tmp, top=TOP,
                                                         highlight=BRAND_PURPLE if hl is True else hl)}
                if bottom: lay["bottom"] = block(im, sh, bottom, 54, tmp, bottom=SAFE_BOTTOM)
                if word: lay["caption"] = block(im, sh, word, cap_size, tmp, bottom=cap_bottom,
                                                cx=W * cfg.get("caption_x", 0.5))
                png = tmp / f"card-{len(cache):03d}.png"
                Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), im).save(png)
                cache[key] = png
                for k, v in lay.items(): layout.setdefault(k, v)
            segs.append((cache[key], b - a))
        lst = tmp / "track.ffconcat"
        lst.write_text("ffconcat version 1.0\n" + "".join(f"file '{f.name}'\nduration {d:.3f}\n" for f, d in segs)
                       + f"file '{segs[-1][0].name}'\n")

        v = (f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS,"
             f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},")
        if p.get("flip"): v += "hflip,"
        if p.get("zoom"):
            cw, ch = int(W / p["zoom"]) // 2 * 2, int(H / p["zoom"]) // 2 * 2
            v += f"crop={cw}:{ch}:{int((W - cw) * p['anchor_x'])}:{int((H - ch) * p['anchor_y'])},scale={W}:{H}:flags=lanczos,"
        v += f"setsar=1,fps={fps}[p];[1:v]fps={fps},format=rgba[t];[p][t]overlay=0:0:format=auto:eof_action=repeat,format=yuv420p[v]"
        maps, extra_in = ["-map", "[v]"], []
        fade = f"afade=t=out:st={max(length - 0.25, 0):.2f}:d=0.25"
        if sound:   # reference or given sound, levelled to -14 LUFS like audio/mux.sh of 25 Oct
            extra_in = ["-ss", f"{sound_off:.3f}", "-i", str(sound)]
            v += (f";[2:a]aresample=48000,apad,atrim=start={s}:end={e},asetpts=PTS-STARTPTS,"
                  f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,afade=t=in:st=0:d=0.05,{fade}[a]")
        elif sound_note == "source":
            v += f";[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,{fade}[a]"
        if sound or sound_note == "source":
            maps += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
        out = out_dir / (f"{name}-trial-{i + 1}.mp4" if trial else f"{name}-{i + 1}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-f", "concat", "-safe", "0", "-i", str(lst),
                        *extra_in, "-filter_complex", v, *maps, "-t", f"{length:.3f}", "-c:v", "libx264", "-crf", "17",
                        "-preset", "medium", "-r", str(fps), "-map_metadata", "-1", "-movflags", "+faststart", str(out)],
                       check=True)
        real = probe(out)["duration"]
        record[str(i + 1)] = dict(file=out.name, hook=hook, length_s=round(real, 2), captions=len(cards), layout=layout, **p)
        print(out.name, f"{real:.2f}s", "flip" if p.get("flip") else "", p.get("zoom", ""), f"{len(cards)} caption cards")

    json.dump(dict(source=str(src), trial=trial, sound=sound_note, sound_offset=sound_off, versions=record), open(out_dir / f"{name}-versions.json", "w"),
              ensure_ascii=False, indent=1)
    qc_sheet(out_dir, name, record, words and cards)

def qc_sheet(out_dir, name, record, cards):
    """First frame of every version plus one frame with a caption, safe-zone lines in magenta."""
    t2 = (cards[len(cards) // 2]["s"] + cards[len(cards) // 2]["e"]) / 2 if cards else 1.5
    tiles = []
    for r in record.values():
        for t in (0.05, t2):
            f = out_dir / f".qc-{r['file']}-{t:.2f}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{min(t, r['length_s'] - 0.1):.2f}",
                            "-i", str(out_dir / r["file"]), "-frames:v", "1", str(f)], check=True)
            im = Image.open(f).convert("RGB"); f.unlink()
            d = ImageDraw.Draw(im)
            for y in (int(H * 0.14), SAFE_BOTTOM): d.line([(0, y), (W, y)], fill=(255, 0, 255), width=4)
            for x in (int(W * 0.06), W - int(W * 0.06)): d.line([(x, 0), (x, H)], fill=(255, 0, 255), width=4)
            tiles.append(im.resize((270, 480)))
    cols = 2 * min(len(record), 4); rows = -(-len(tiles) // cols)
    sheet = Image.new("RGB", (cols * 270, rows * 480), "black")
    for k, t in enumerate(tiles): sheet.paste(t, ((k % cols) * 270, (k // cols) * 480))
    qc = out_dir / f"{name}-qc.jpg"; sheet.save(qc, quality=85)
    print("qc sheet:", qc)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "transcribe": transcribe(sys.argv[2], sys.argv[3])
    elif cmd == "build": build(sys.argv[2], "--trial" in sys.argv)
    else: sys.exit(__doc__)
