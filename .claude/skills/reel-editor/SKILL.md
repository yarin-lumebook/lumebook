---
name: reel-editor
description: Burn text into a LumeBook Instagram Reel and make trial reel versions. A bold white hook at the top, optional word-by-word captions in the lower half, both inside Instagram's safe zone, the Higgsfield reference's sound added automatically to silent results (or a question when there is none), and for trial reels a seeded horizontal flip, a small zoom and a slight trim per version so no two uploads are the same file. Use it whenever Yarin asks to caption a reel, add a hook or subtitles to a video, make trial reel versions or variants of a reel, or says "reel editor", even if the request only says "put this text on the video" or "make 5 versions for trial reels".
---

# Reel editor

One script does the work: `scripts/reel_editor.py` (Pillow draws the text, ffmpeg burns it in). Run it with the watch-video Python, which has Pillow:

```bash
PY=~/.claude/skills/watch-video/.venv/bin/python
S=.claude/skills/reel-editor/scripts
```

## 1 · Set up the job

- Work in the reel's own folder `media/projects/<start date>-<slug>/` (new folder if there is none). Source footage stays where it is; outputs go to `final/` (plain) or `trial/`, scratch to `work/`.
- Write `reel.json` there. Paths in it are relative to the file.

```json
{
  "source": "source/clip.mp4",
  "name": "ben-window",
  "hooks": ["השעה עשר בלילה\nומישהו פה לא הולך לישון", "מה הוא עושה\nכשהוא חושב שכולם ישנים"],
  "captions": "words.json",
  "cta": {"text": "תשמרי את הסרטון\nלפעם הבאה", "seconds": 2.5},
  "versions": 5,
  "flip": true
}
```

| Key | Meaning |
|---|---|
| `source` | the video. Any size: it is scaled to fill 1080x1920. iPhone HDR (HLG) is converted with `avconvert` first, automatically |
| `name` | output file prefix (default the source file name) |
| `hooks` / `hook` | top text, one per version; `\n` breaks the line. Fewer hooks than versions: they repeat in order |
| `versions` | how many files (default: one per hook) |
| `captions` | a words file (step 2), or leave it out for no captions ("captions if needed") |
| `words_per_card` | words shown at once, default 1 (word by word) |
| `hook_seconds` | optional: show the hook only for the first N seconds (an opening clip, say), then no top text until the CTA. Default: the whole reel (Yarin, 4 Nov 2026) |
| `top_cards` | optional: timed top text between the hook and the CTA, `[{"text": "1", "s": 2.1, "e": 6.0}, ...]` in source seconds, such as a number per point or one key word (Yarin, 05 Nov 2026). Same style as the hook, `"size"` (px) optional per card; re-timed with each trial trim |
| `cta` | optional: replaces the hook for the last `seconds`. `"highlight": true` puts it on LumeBook purple rounded boxes (#5B2BD6, Instagram's highlighted text look; a hex colour also works), Yarin, 29 Oct 2026 |
| `bottom` | optional fixed line at the lowest safe line, such as `הסבר בתיאור👇🏻`; captions then sit just above it |
| `flip` | trial only, default true. Set false when the frame shows Hebrew text (a book title, a screen): a flip mirrors it |
| `seed` | trial only, default `name`. Same seed, same versions; change it for a fresh set |
| `hook_size`, `caption_size` | px, default 64 and 74; long lines shrink to fit automatically |
| `caption_x` | optional: the captions' horizontal centre as a share of the width, default 0.5. Move them aside when the default spot covers the book or a face (0.72 put them on the free side of the frame on 29 Oct); they stay inside the side margins |
| `audio` | leave it out for automatic sound (see below); a file path to use that sound; `"source"` to keep the source's own; `"none"` for a silent file (sound added in Instagram) |
| `audio_offset` | seconds into the `audio` file where the reel starts; worked out automatically for Higgsfield references |

### Sound (Yarin, 26 Oct 2026: add the Higgsfield reference's audio automatically, ask when there is none)

With no `audio` key the build decides:
1. The source has sound: it is kept.
2. The source is silent (a Higgsfield result): it looks in the job folder (`media/projects/<job>/`) for the reference's sound: files under `refs/` or `audio/`, or named original, reference, ref or mute, preferring those named after the source (`02-ben-window` for `results/02-ben-window-v1-1080p.mp4`). A sound-only file beats a video with sound. When the folder also has the muted, trimmed reference that went to Higgsfield and the original with sound, it finds where the trimmed part starts in the original by matching their picture over time, and starts the sound there (tested on 26 Oct: 3.08 s for the truck jump, where 3.04 s was used by hand; 8.72 s for the fridge, 8.7 s). The sound is levelled to -14 LUFS with short fades, like `2026-10-25-genjutsu-lite-trends/audio/mux.sh`, and re-timed with each trial trim.
3. Nothing found, or more than one sound could fit: the build stops with `NO AUDIO` and the reason. **Then ask Yarin** (AskUserQuestion) before building, offering: send or name a sound file (then set `audio`, and `audio_offset` if it does not start with the clip); pick one of the listed candidates; leave it silent and add a sound from Instagram's library when uploading (`"audio": "none"`); or generate a sound bed (Seed Audio on Higgsfield, costs credits, ask first). Never fall back to a silent file on your own.

The build prints which sound it used and from where (`sound:` line, also in `<name>-versions.json`). Say it in the hand-over message. Reference sounds are usually other creators' songs: before posting from the business account, Yarin checks the sound can be used or picks the same sound from Instagram's library (the 25 Oct trends README notes the same).

Hook and CTA text is audience copy: write it with the `lumebook-hebrew-voice` skill and lint it (`python3 carousel/carousel-pipeline/scripts/voice_lint.py`). The build itself refuses any dash, hyphen, maqaf or semicolon, לומיבוק, and AI wording in the hook, CTA, bottom line and every caption word.

## 2 · Captions (only if the reel has speech)

```bash
$PY $S/reel_editor.py transcribe source/clip.mp4 words.json
```

ivrit-ai whisper on the CPU, about a minute for 20 s of speech. Then **read words.json and fix it by hand**: misheard words, לומיבוק spelling, numbers, and remove words that must not show (AI, prices). Each entry is `{"w", "s", "e"}` in source seconds; edit the text, keep the times. A pause of 0.6 s or more clears the caption until the next word.

## 3 · Build

```bash
$PY $S/reel_editor.py build reel.json            # plain: final/<name>-1.mp4 ...
$PY $S/reel_editor.py build reel.json --trial    # trial: trial/<name>-trial-1.mp4 ...
```

About 50 s of encoding per 20 s version. Each run writes `<name>-versions.json` (every hook, flip, zoom, crop spot, trim and real length) and `<name>-qc.jpg` (first frame and one caption frame of each version, safe-zone lines in magenta).

What a trial build changes per version (Yarin, 25 and 26 Oct 2026), all seeded and spread out so no two match:
- **Flip:** about half are mirrored, never all the same way. The picture is flipped first and the text burned on top, so the text is never mirrored.
- **Zoom:** one steady zoom between about 1.02x and 1.08x, a different amount per version, cropped at a random spot near the middle.
- **Length** (Yarin, 10 Nov 2026: "a tiny bit shorter or longer randomly"): about half the versions are shorter, 0.15 s up to 0.8 s (at most 6% of the clip) cut off, at most 0.12 s of it from the start so the opening frame stays, the rest from the end with a 0.25 s sound fade; the others are 0.15 s up to 0.6 s longer, the last frame held (the closing card stays a little longer, the sound runs on or goes quiet). Never all the same way. Captions are re-timed to the trim. Versions built before 10 Nov were all shorter.
- File metadata is stripped.

Whether this keeps Instagram from treating the uploads as repeats is not verified; it is Yarin's request, not a tested rule.

## 4 · Check, then hand over

- Look at `<name>-qc.jpg` yourself: no text above the top magenta line, below the 65% line or outside the side lines; the hook does not cover a face or the book; Hebrew reads right to left.
- Spot-check caption sync: grab a frame at a word's time (`ffmpeg -ss T -i out.mp4 -frames:v 1 f.png`) and read it.
- In flipped versions, look for mirrored text in the footage itself. If a book title or logo shows, rebuild with `"flip": false`.
- Send Yarin the files (or the qc sheet) in one message with the list of hooks and lengths.

## Layout rules the script follows

- Safe zone from `research/israeli-product-reels/playbook.md` section 8: text stays out of the top 14%, the bottom 35% and the outer 6% of each side, where Instagram draws its header, caption and buttons. The hook starts at 15% of the height; captions end at 65%, the lowest safe line (the "bottom half" of the safe area).
- Font: SF Hebrew Bold (SF Pro for Latin letters), white, soft black shadow. It is the stand-in for Instagram's default font used on every reel since 19 Oct; Instagram's own font file is not available here.
- Emoji at the end of a line are drawn by macOS (`scripts/emoji_png.swift`), since this Pillow splits skin-tone emoji.
- Known limits: right-to-left is done by reversing the line (no raqm), so brackets would come out mirrored; avoid them.
