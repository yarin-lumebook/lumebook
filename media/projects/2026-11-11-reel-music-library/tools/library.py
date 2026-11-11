#!/usr/bin/env python3
"""Reel music library: sort, cut the best 30 s, index, pick a song for a reel, mix it under a video.

Run from the project root with plain python3 (no librosa needed here):

  python3 $L/tools/library.py build            # sort by CAT, choose each best 30 s, cut, write library.json + README.md
  python3 $L/tools/library.py build --no-cut   # only sort and index (re-cuts nothing)
  (a plain build re-cuts only songs whose start moved; --recut cuts all 99 again)
  python3 $L/tools/library.py pick --length 16 --mood upbeat --talk
  python3 $L/tools/library.py mix VIDEO.mp4 ElspqCcCpvY --out final/x.mp4

  L=media/projects/2026-11-11-reel-music-library

The measurements come from tools/analyze.py (librosa, analysis/audio/) and tools/transcribe.sh
(whisper, analysis/lyrics/, local only). Made 11 Nov 2026.
"""
import argparse, difflib, json, re, shutil, subprocess, sys
from pathlib import Path

D = Path(__file__).resolve().parent.parent
PLAYLIST = "https://www.youtube.com/playlist?list=PLMCcUbO--M9QW9cf-QtnKSeWOnY_x_Y5d"
CUT = 30.0

FOLDERS = {
    "01-upbeat-feelgood": "Bright, positive pop. Hooks, gift moments, sale-day reels, 'smile' endings.",
    "02-heartfelt-emotional": "Warm love songs and big ballads. Grandparent, birthday, 'his name on the cover' moments.",
    "03-chill-mellow": "Soft, slow, indie and lo-fi. Quiet talking-take reels, behind the scenes, bedtime and reading.",
    "04-dance-remix-trending": "TikTok versions, remixes and mashups. Fast cuts, transitions, countdowns.",
    "05-latin-afro-world": "Afro, Latin, Brazilian funk, amapiano. Fun, rhythmic montages.",
    "06-throwback-retro": "2000s hits and older. Nostalgia, grandmother and 'when we were kids' reels.",
    "07-hiphop-rnb": "Rap and R&B without strong words in the lyrics. Confident, trend-style reels.",
    "08-adult-explicit-avoid": "Strong words or adult themes in the lyrics. Not for a kids' book brand.",
    "09-check-first": "Not sure. Listen before using.",
}
MOODS = {"upbeat": "01", "heartfelt": "02", "warm": "02", "chill": "03", "dance": "04", "latin": "05",
         "world": "05", "throwback": "06", "retro": "06", "hiphop": "07", "rnb": "07"}

# playlist position -> folder. Edit here, then `build --no-cut` moves the files.
CAT = {}
def put(folder, *idx):
    for i in idx:
        CAT[i] = folder
# 11 Nov afternoon, after the lyrics check: songs with strong words inside their cut (and no clean
# 30 s in the transcribed part) or a drugs/smoking theme moved to 08; 8 and 54 sorted by their lyrics.
put("01-upbeat-feelgood", 1, 2, 7, 15, 20, 29, 44, 45, 47, 80, 92)
put("02-heartfelt-emotional", 8, 10, 18, 25, 28, 30, 32, 40, 43, 50, 51, 55, 62, 66, 67, 73, 83, 89, 90, 94)
put("03-chill-mellow", 6, 9, 26, 27, 48, 49, 54, 63, 71, 75, 81, 93, 96, 98)
put("04-dance-remix-trending", 11, 17, 35, 36, 38, 42, 52, 79, 88, 97)
put("05-latin-afro-world", 4, 19, 33, 41, 53, 57, 58, 78, 99)
put("06-throwback-retro", 3, 5, 16, 21, 23, 76)
put("07-hiphop-rnb", 12, 22, 64, 84, 87)
put("08-adult-explicit-avoid", 13, 14, 24, 31, 34, 37, 39, 56, 59, 60, 61, 65, 68, 69, 70, 72, 77, 82, 85, 86, 91, 95)
put("09-check-first", 46, 74)

DUPES = {20: 2, 25: 18, 40: 10}
# lyrics mostly not in English: whisper small.en cannot check them, so no lyric verdict
NOT_ENGLISH = {4, 19, 53, 57, 58, 97, 99}
NOTES = {
    13: "55 s mashup, very short",
    23: "full song; 13 is a 55 s mashup of it",
    20: "same song as 2", 25: "same song as 18", 40: "same song as 10",
    46: "no strong words heard, but the song is about death and haunting",
    74: "whisper heard no lyrics around the cut; was in 08 on its title only",
    13: "strong words in the cut", 34: "strong word in the cut", 39: "strong words in the cut",
    65: "strong word in the cut", 72: "strong word in the cut", 85: "strong word in the cut",
    86: "strong words in the cut", 91: "strong words and weed in the cut",
    24: "about smoking weed", 69: "about smoking", 31: "strong words and drugs", 59: "strong words throughout",
    8: "love song (lyrics)", 54: "slow love song (lyrics)", 35: "'lean with it' is a dance line",
}

STRONG = r"f+u+c+k\w*|motherf\w*|shit\w*|bitch\w*|ass(?:hole)?s?|dick|pussy|cock|nigg\w*|hoes?|thots?|thottie|whores?|sluts?|cum|titt\w*"
ADULT = r"sex\w*|naked|nude|freaky|booty|horny|molly|weed|blunts?|cocaine|coke|drugs?|drunk|cigarettes?|smok\w*|kill\w*|guns?|glock|draco|shoot\w*|strip\w*|stripper|bed ?room|grind\w*|baddie"
MILD = r"damn|hell|sexy|crap|pissed?"
WINDOW = {}  # id -> [a, b] when only part of the song was transcribed
HALLU = re.compile(r"^\W*$|^(you|thank you\.?|thanks for watching!?|bye\.?)$", re.I)


# ---------- helpers ----------
def ids():
    return (D / "ids.txt").read_text().split()


def track_files():
    out = {}
    for p in D.glob("0*/*.mp3"):
        m = re.search(r"\[([\w-]{11})\]\.mp3$", p.name)
        if m:
            out[m.group(1)] = p
    return out


def ts(s):
    h, m, r = s.split(":")
    sec, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def lyrics(vid):
    p = D / "analysis" / "lyrics" / f"{vid}.json"
    if not p.exists():
        return None
    segs, last = [], None
    data = json.loads(p.read_text(errors="replace"))
    WINDOW[vid] = data.get("window")
    for s in data.get("transcription", []):
        t = re.sub(r"\[.*?\]|\(.*?\)|♪", "", s["text"]).strip()
        if HALLU.match(t) or not t:
            continue
        a, b = ts(s["timestamps"]["from"]), ts(s["timestamps"]["to"])
        if last and t == last["text"] and a - last["e"] < 0.5 and len(segs) > 2 and segs[-2]["text"] == t:
            continue  # whisper loop
        last = {"s": a, "e": b, "text": t}
        segs.append(last)
    norm = [re.sub(r"[^a-z' ]", "", s["text"].lower()).strip() for s in segs]
    for i, s in enumerate(segs):
        s["repeats"] = sum(1 for j, o in enumerate(norm) if j != i and norm[i] and difflib.SequenceMatcher(None, norm[i], o).ratio() > 0.78)
    return segs


def words(text, pat):
    return re.findall(rf"\b(?:{pat})\b", text.lower())


def mmss(s):
    return f"{int(s // 60)}:{int(s % 60):02d}"


# ---------- choose the 30 s ----------
def choose(a, segs, dur):
    beats = a["beats"]
    lz, rp, dr = a["loud_z_per_beat"], a["repetition_per_beat"], a["drive_z_per_beat"]
    n = min(len(beats), len(lz), len(rp), len(dr))
    if dur <= CUT + 2:
        return 0.0, "whole track (shorter than 32 s)"
    import bisect
    cands = set(a.get("section_starts", []))
    if segs:  # line starts that sit near a section start, and every line that opens a repeated block
        for i, s in enumerate(segs):
            near = any(abs(s["s"] - c) < 2.0 for c in a.get("section_starts", []))
            opens = s["repeats"] >= 2 and (i == 0 or segs[i - 1]["repeats"] < 2 or s["s"] - segs[i - 1]["e"] > 1.5)
            if near or opens:
                cands.add(round(s["s"], 2))
    best = None
    win = WINDOW.get(a.get("id"))
    for t0 in sorted(cands):
        if t0 + CUT > dur - 0.3:
            continue
        if win and segs and not (win[0] <= t0 <= win[1] - CUT + 0.5):
            continue  # lyrics only cover the window
        i, j = bisect.bisect_left(beats[:n], t0), bisect.bisect_left(beats[:n], t0 + CUT)
        if j - i < 8:
            continue
        mean = lambda xs: sum(xs[i:j]) / (j - i)
        score = 0.40 * mean(lz) + 0.40 * mean(rp) + 0.20 * mean(dr)
        why = []
        if segs:
            inwin = [s for s in segs if t0 - 0.2 <= s["s"] < t0 + CUT]
            wtext = " ".join(s["text"] for s in inwin)
            score -= 1.5 * len(words(wtext, STRONG)) + 0.3 * len(words(wtext, ADULT))  # keep the cut clean
            if inwin:
                ch = sum(1 for s in inwin if s["repeats"] >= 2) / len(inwin)
                score += 0.6 * ch
                if ch >= 0.5:
                    why.append("chorus lines")
            first = next((s for s in segs if s["s"] >= t0 - 0.3), None)
            if first and abs(first["s"] - t0) < 0.6 and first["repeats"] >= 2:
                score += 0.3
                k = segs.index(first)
                if k == 0 or segs[k - 1]["repeats"] < 2 or first["s"] - segs[k - 1]["e"] > 1.5:
                    score += 0.3  # the first line of the repeated block, not one in the middle of it
                    why.append("starts on the chorus's first line")
                else:
                    why.append("starts on a chorus line")
            if any(s["s"] < t0 - 0.6 and s["e"] > t0 + 0.6 for s in segs):
                score -= 0.4  # would start in the middle of a sung line
        if t0 < 6:
            score -= 0.35
        if t0 > 0.75 * dur:
            score -= 0.5
        score -= 0.0015 * t0  # the first time the chorus comes is the one people know
        if best is None or score > best[0]:
            best = (score, t0, why)
    if best is None:
        return a["best30"]["start"], "audio only"
    t0 = best[1]
    if segs:
        # whisper misses lines: a section start up to 3.5 s earlier with nothing sung in between
        # is the real start of the phrase
        prev_end = max([s["e"] for s in segs if s["s"] < t0 - 0.3] or [0.0])
        earlier = [b for b in a.get("section_starts", []) if t0 - 3.5 <= b <= t0 - 0.3 and b >= prev_end - 0.2]
        if earlier:
            return round(min(earlier), 2), ", ".join(best[2] + ["section start"])
        # otherwise start a breath before the sung line
        line = next((s for s in segs if abs(s["s"] - t0) < 0.6), None)
        if line:
            t0 = max(0.0, line["s"] - 0.15)
    return round(t0, 2), ", ".join(best[2]) or "loud, repeated part"


def vocal_share(segs, a, b):
    if not segs:
        return None
    cov = 0.0
    for s in segs:
        cov += max(0.0, min(b, s["e"]) - max(a, s["s"]))
    return round(min(1.0, cov / max(0.1, b - a)), 2)


def cut(src, dst, start, length):
    dst.parent.mkdir(parents=True, exist_ok=True)
    fo = max(0.0, length - 2.0)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}", "-t", f"{length:.2f}", "-i", str(src),
                    "-af", f"afade=t=in:st=0:d=0.06,afade=t=out:st={fo:.2f}:d=2,loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "44100", "-b:a", "192k", str(dst)], check=True)


# ---------- build ----------
def build(no_cut=False, recut=False):
    order = ids()
    files = track_files()
    rows = []
    # cut starts of the last build: only songs whose start moved are cut again
    lp = D / "library.json"
    prev = {r["id"]: r.get("cut", {}).get("start") for r in json.loads(lp.read_text())["tracks"]} if lp.exists() else {}
    # 1 sort
    for n, vid in enumerate(order, 1):
        p = files.get(vid)
        if not p:
            continue
        folder = CAT.get(n, "09-check-first")
        dest = D / folder / p.name
        if p != dest:
            dest.parent.mkdir(exist_ok=True)
            shutil.move(str(p), str(dest))
            old = p.parent / "30s" / p.name.replace(".mp3", " 30s.mp3")
            if old.exists():
                (dest.parent / "30s").mkdir(exist_ok=True)
                shutil.move(str(old), str(dest.parent / "30s" / old.name))
        files[vid] = dest
    # energy needs the whole library for scale
    aud = {}
    for vid in order:
        ap = D / "analysis" / "audio" / f"{vid}.json"
        if ap.exists():
            aud[vid] = json.loads(ap.read_text())
    def rank(key):
        vals = sorted(aud[v][key] for v in aud)
        return lambda x: sum(1 for v in vals if v <= x) / len(vals)
    rl, ro, rb = rank("loudness_db"), rank("onset_strength"), rank("bpm") if aud else None
    total = len(order)
    for n, vid in enumerate(order, 1):
        p = files.get(vid)
        if not p:
            continue
        title = re.sub(r"\s*\[[\w-]{11}\]\.mp3$", "", p.name)
        a = aud.get(vid)
        segs = lyrics(vid)
        r = {"n": n, "id": vid, "title": title, "folder": p.parent.name, "file": f"{p.parent.name}/{p.name}",
             "url": f"https://www.youtube.com/watch?v={vid}", "duplicate_of": DUPES.get(n), "note": NOTES.get(n, "")}
        if a:
            dur = a["seconds"]
            e = 0.45 * rl(a["loudness_db"]) + 0.40 * ro(a["onset_strength"]) + 0.15 * min(1.0, a["bpm"] / 150)
            r.update({"seconds": dur, "bpm": a["bpm"], "key": a["key"], "brightness_hz": a["brightness_hz"],
                      "energy": 1 + min(4, int(e * 5))})
            start, why = choose(a, segs, dur)
            length = min(CUT, round(dur - start, 2))
            cutf = p.parent / "30s" / p.name.replace(".mp3", " 30s.mp3")
            r["cut"] = {"file": f"{p.parent.name}/30s/{cutf.name}", "start": start, "end": round(start + length, 2),
                        "why": why, "vocals": vocal_share(segs, start, start + length)}
            if not cutf.exists() or (not no_cut and (recut or prev.get(vid) != start)):
                cut(p, cutf, start, length)
        if segs is not None:
            win = WINDOW.get(vid)  # set when only ~60 s around the cut was transcribed
            whole = " ".join(s["text"] for s in segs)
            incut = " ".join(s["text"] for s in segs if a and r["cut"]["start"] - 0.5 <= s["s"] < r["cut"]["end"])
            r["lyrics"] = {
                "checked": n not in NOT_ENGLISH,
                "lines_heard": len(segs),
                "window": win,
                "first_vocal_s": round(segs[0]["s"], 1) if segs and not (win and win[0] > 0) else None,
                "vocals_share": (vocal_share(segs, win[0], win[1]) if win else vocal_share(segs, 0, r.get("seconds", 1))) if segs else 0,
                "strong_words": len(words(whole, STRONG)), "adult_words": len(words(whole, ADULT)),
                "mild_words": len(words(whole, MILD)),
                "strong_in_cut": len(words(incut, STRONG)), "adult_in_cut": len(words(incut, ADULT)),
            }
        rows.append(r)
        print(f"PROGRESS {n}/{total} {vid}", flush=True)
    (D / "library.json").write_text(json.dumps({"source_playlist": PLAYLIST, "made": "2026-11-11", "tracks": rows},
                                               ensure_ascii=False, indent=1) + "\n")
    readme(rows)
    print(f"{len(rows)} tracks indexed")


def flag(r):
    l = r.get("lyrics")
    if not l:
        return "?"
    if not l["checked"]:
        return "not English"
    if l.get("lines_heard", 9) < 4:
        return "not heard"
    part = " (around the cut)" if l.get("window") else ""
    if l["strong_words"]:
        return f"strong x{l['strong_words']}{part}"
    if l["adult_words"]:
        return f"adult x{l['adult_words']}{part}"
    return "clean" + part


def start_label(r, checks):
    """How the cut's start was verified (tools/check_cuts.py, analysis/cut-check.json)."""
    c = checks.get(r["id"])
    if not c or abs(c.get("start", -1) - r.get("cut", {}).get("start", -2)) > 0.05:
        return "not checked"
    v = c["verdict"]
    if v.startswith("opens on a chorus"):
        return "chorus line"
    if v.startswith("opens on a sung"):
        return "sung line"
    if v.startswith("unconfirmed"):
        return "unconfirmed"
    if v.startswith("not checked"):
        return "not checked"
    if v.startswith("no singing"):
        return "no singing heard"
    return v.split(" (")[0]


def readme(rows):
    cp = D / "analysis" / "cut-check.json"
    checks = json.loads(cp.read_text()) if cp.exists() else {}
    out = ["# Reel music library", "",
           f"Yarin's YouTube playlist ({PLAYLIST}), mp3 only, {len(rows)} tracks, downloaded 11 / 11 / 2026. "
           "Every track is measured (tempo, energy, key, where the singing is, the lyrics) and has a ready 30 second cut "
           "of its strongest part in its folder's `30s/`, levelled to -14 LUFS with a 2 s fade at the end. "
           "Full numbers: `library.json`.", "",
           "## Using it for a reel", "",
           "```bash",
           "python3 media/projects/2026-11-11-reel-music-library/tools/library.py pick --length 16 --mood upbeat --talk",
           "python3 media/projects/2026-11-11-reel-music-library/tools/library.py mix final/reel.mp4 <id> --out final/reel-music.mp4",
           "```", "",
           "- `pick` lists the best fits: never folder 08 or a cut with strong words; songs with strong words elsewhere come last and say so; cuts whose opening was confirmed come first; `--talk` puts the cuts with the least singing first (a talking take), `--mood` is upbeat, heartfelt, chill, dance, latin, throwback or hiphop.",
           "- `mix` lays the 30 s cut under the video, ducked whenever someone talks, with a fade at the end. `--from S` uses the full song from second S instead.",
           "- With the reel editor: set `\"audio\": \"<cut path>\"` in reel.json for a video without its own sound.",
           "- These are commercial songs. Before posting from the business account, pick the same sound from Instagram's music library; a file here is for choosing and timing, not a licence.",
           "- How it was measured: tempo, energy, key and sections with librosa (`tools/analyze.py`); the singing and the lyrics with whisper small.en (`tools/transcribe.sh`, local only, never committed). The best 30 s is the loud, repeated part that opens on a sung line, preferring the first chorus. Energy 1 to 5 is relative to this library. BPM is the beat tracker's reading and can come out double on slow songs (a ballad at 150). Lyrics are machine heard: a 'clean' song can still have a word whisper missed, and songs mostly not in English were not checked. To save time, most songs were transcribed only around their cut (about 15 s before to 45 s after its start); their check says 'around the cut' and covers only that part, so the rest of the song can still have strong words.",
           "- Every usable cut's start was checked by transcribing its opening seconds again (`tools/check_cuts.py`): 'chorus line' and 'sung line' are confirmed; 'unconfirmed' means the two checks disagreed, so listen to the first seconds before using it. Folder 08 was not checked.", "",
           "Columns: tempo (BPM), energy 1 to 5, singing in the 30 s cut, lyrics check, where the cut starts in the song, what the cut opens on.", ""]
    for f, desc in FOLDERS.items():
        rs = [r for r in rows if r["folder"] == f]
        if not rs:
            continue
        out += [f"## {f} ({len(rs)})", "", desc, "", "| # | Track | BPM | Energy | Singing in cut | Lyrics | Cut from | Opens on |", "|---|---|---|---|---|---|---|---|"]
        for r in rs:
            c = r.get("cut", {})
            voc = f"{int(c['vocals'] * 100)}%" if c.get("vocals") is not None else "?"
            note = f" ({r['note']})" if r["note"] else ""
            t = r["title"].replace("|", "/").replace("｜", "/")[:70]
            out.append(f"| {r['n']:02d} | {t}{note} | {int(r.get('bpm', 0))} | {r.get('energy', '?')} | {voc} | {flag(r)} | {mmss(c.get('start', 0))} | {start_label(r, checks)} |")
        out.append("")
    (D / "README.md").write_text("\n".join(out))


# ---------- pick ----------
def pick(length, mood, talk, n, bpm_min, bpm_max):
    lib = json.loads((D / "library.json").read_text())["tracks"]
    want = MOODS.get(mood) if mood else None
    res = []
    for r in lib:
        if r["folder"].startswith(("08", "09")) or r.get("duplicate_of") or "cut" not in r:
            continue
        if want and not r["folder"].startswith(want):
            continue
        l = r.get("lyrics") or {}
        if l.get("strong_in_cut") or l.get("adult_in_cut", 0) >= 2:
            continue
        if not (bpm_min <= r.get("bpm", 0) <= bpm_max):
            continue
        voc = r["cut"].get("vocals")
        s = (r.get("energy", 3) if not talk else 3 - abs(r.get("energy", 3) - 3)) - (2 * (voc or 0.5) if talk else 0)
        s -= 1.0 if l.get("strong_words") else 0  # clean cut, but the song has strong words elsewhere
        res.append((s, r))
    cp = D / "analysis" / "cut-check.json"
    checks = json.loads(cp.read_text()) if cp.exists() else {}
    res = [(s + (0.3 if start_label(r, checks) in ("chorus line", "sung line") else 0), r) for s, r in res]
    res.sort(key=lambda x: -x[0])
    for s, r in res[:n]:
        c = r["cut"]
        voc = f"{int(c['vocals'] * 100)}% singing" if c.get("vocals") is not None else ""
        warn = f"  lyrics: {flag(r)} (not in the cut)" if (r.get("lyrics") or {}).get("strong_words") else ""
        print(f"{r['id']}  {r['title'][:55]:55}  {int(r['bpm'])} BPM  energy {r['energy']}  {voc}  opens on: {start_label(r, checks)}  ({r['folder']}){warn}")
        print(f"             {D.relative_to(Path.cwd()) if D.is_relative_to(Path.cwd()) else D}/{c['file']}")


# ---------- mix ----------
def has_audio(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        sys.exit(f"Cannot read {p}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'no duration'}")


def mix(video, vid, out, start, music_db):
    lib = {r["id"]: r for r in json.loads((D / "library.json").read_text())["tracks"]}
    r = lib[vid]
    if r["folder"].startswith("08"):
        sys.exit(f"{vid} is in 08-adult-explicit-avoid. Pick another song.")
    if start is None:
        src, ss = D / r["cut"]["file"], 0.0
    else:
        src, ss = D / r["file"], start
    v = Path(video)
    if not v.is_file():
        sys.exit(f"No video at {v}")
    dur = duration(v)
    fo = max(0.0, dur - 1.5)
    g = 10 ** (music_db / 20)
    mus = f"[1:a]aresample=48000,volume={g:.3f},afade=t=out:st={fo:.2f}:d=1.5"
    if ss == 0.0 and start is None:
        mus += ""
    else:
        mus += ",afade=t=in:st=0:d=0.5"
    if has_audio(v):
        fc = (f"[0:a]aresample=48000,asplit=2[v][sc];{mus}[m];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];"
              f"[v][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    else:
        fc = f"{mus},apad,atrim=0:{dur:.2f},loudnorm=I=-14:TP=-1.5[a]"
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(v), "-ss", f"{ss:.2f}", "-i", str(src), "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.2f}", str(out)], check=True)
    lufs = subprocess.run(["ffmpeg", "-nostats", "-i", str(out), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lufs)
    print(f"{out}  music: {r['title']} from {mmss(r['cut']['start'] if start is None else start)}  loudness {m[-1] if m else '?'} LUFS")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--no-cut", action="store_true", help="never cut, only sort and index")
    b.add_argument("--recut", action="store_true", help="cut every song again, even if its start did not move")
    p = sub.add_parser("pick")
    p.add_argument("--length", type=float, default=15)
    p.add_argument("--mood")
    p.add_argument("--talk", action="store_true")
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--bpm-min", type=float, default=0)
    p.add_argument("--bpm-max", type=float, default=999)
    m = sub.add_parser("mix")
    m.add_argument("video")
    m.add_argument("id")
    m.add_argument("--out", required=True)
    m.add_argument("--from", dest="start", type=float)
    m.add_argument("--music-db", type=float, default=-9.0, help="music level before ducking, dB (default -9)")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.no_cut, a.recut)
    elif a.cmd == "pick":
        pick(a.length, a.mood, a.talk, a.n, a.bpm_min, a.bpm_max)
    else:
        mix(a.video, a.id, a.out, a.start, a.music_db)


if __name__ == "__main__":
    main()
