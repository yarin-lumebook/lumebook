# Grandma baking book reel (24 Oct 2026)

Yarin asked for "a reel from the Google Drive materials and the product reels playbook". Built from the printed-book close-ups in Drive and concept 5 of `research/israeli-product-reels/playbook.md` ("מתנה לנכד שאין לאף ילד אחר", a gift for a grandchild), with the 18 Oct research changes applied: voice from 0:00, hook text whole on the first frame, one CTA on screen at the end, text inside the Reels safe zone, straight cuts, length by content.

**Status: ready for Yarin's review. Not posted, not in the Drive content folder yet** (see "Before posting").

## Finals

| File | Voice | Length |
|---|---|---|
| `final/grandma-baking-book-reel-sarah.mp4` | ElevenLabs v4, Sarah (main) | 23.2 s |
| `final/grandma-baking-book-reel-matilda.mp4` | ElevenLabs v4, Matilda (same cut, retimed) | 23.9 s |

1080x1920, 30 fps, H.264 + AAC, -14.8 LUFS. No music: add a quiet track in Instagram (playbook E5: the licensed library is for personal use; Meta's Sound Collection is cleared for business accounts).

Both voice takes were transcribed with ivrit-ai Whisper large-v3 and came back word for word, so the Hebrew is pronounced right in both; which one sounds warmer is Yarin's call by ear.

## 8-second cut

`final/grandma-baking-book-reel-8s.mp4` (8.0 s, -14.3 LUFS), built by `build_8s.py` from `copy-8s.json`. Yarin asked for fast editing, retention and conversion first, no price, a quick story with a curiosity gap and the strongest footage. The gap: "look at this kid" over the illustrated boy, paid off by "it's him" on his real photo on the title page (photo beside illustration, a gap in the category per playbook section 1 point 4). About one cut per second; the voice is one Sarah take (`audio/vo-8s-sarah.mp3`, stability 0.35) cut into phrases, pauses removed and sped up 1.2x.

| Time | Picture | On screen | Voice |
|---|---|---|---|
| 0:00-1.8 | Grandma laughing | סבתא וסבא / הכינו לו מתנה | סבתא וסבא הכינו לו מתנה |
| 1.8-2.94 | The illustrated grandson | תסתכלו על הילד הזה | תסתכלו על הילד הזה |
| 2.94-3.57 | His real photo on the title page, zoomed | זה הוא | זה הוא! |
| 3.57-4.36 | His name in the text | עם השם שלו | עם השם שלו |
| 4.36-6.0 | The dedication, then a fast flip | והקדשה מסבא וסבתא | והקדשה מסבא וסבתא |
| 6.0-8.0 | Flip back to the title page | כתבו "לומי" בתגובות / וקבלו קישור לספר / שבו הנכד שלכם הגיבור | כתבו לומי בתגובות |

The CTA card is up for 2.0 s, a little under the 2.6 s its 45 characters need at 17 characters a second (playbook T5); the reel loops and the caption repeats it. This cut leans on the child's real photo even more than the long one, so the family's OK (below) matters more here. Caption in `copy-8s.json`.

## 8-second options with other children

Same format as the 8-second cut, built by `build_options.py` from `copy-options.json`, one Sarah take each (`audio/vo-opt-*.mp3`, pauses removed, 1.2 to 1.25x). Footage: three creator videos from Drive `תוכן לקוחות ויוצרים (UGC)`, already downloaded for the creator brief (`media/projects/2026-10-15-israeli-product-reels/creator-examples/raw/`). Each story keeps to what the creator says in her own video (`creator-examples/analysis/<video>/whisper.txt`). The exports carry the creators' burned-in captions (some say "AI" or spell לומיבוק), so every shot is cropped to a window above them; Nofit's video is HLG HDR and goes through avconvert first (`work/sdr/nofit.mov`).

| File | Child and story | Gap and payoff | Shots |
|---|---|---|---|
| `final/option-natali-8s.mp4` | Natali's son screamed at the gan gate; she made him the new-gan book | "עד שאמא שלו הכינה לו משהו" then the book; "ותראו מה הוא לוקח איתו לגן" then him walking in holding it | crying, mom with the page, him smiling with the rainbow cover, the gate |
| `final/option-nofit-8s.mp4` | Nofit picked one gallery photo of her son | "תמונה אחת שלו מהגלריה" then "וזה מה שהגיע הביתה": him on the cover | his real photo, the cover, the page in his hands, his laugh, mom's hug |
| `final/option-moran-8s.mp4` | Moran (the aunt) gave her niece Eve a book | "תראו מה היא מצאה בפנים" then "את עצמה" on a full-page portrait | Moran with the cover, Eve reading, the portrait, the ladder page, the title page |

All three are 8.0 s, -14.5 to -14.7 LUFS, voice from 0:00 with no pause over 0.25 s until the CTA. Two phrases were cut short in the audio to fit 8 s ("של הגן" and "בתוך הסיפור"); the on-screen text keeps the full lines. The hook card in Moran's cut half-covers the girl on the cover on purpose, so her face first shows on the "את עצמה" portrait.

Before posting: the creator brief records that these creators agreed to be shown on the public creator-brief site (`research/israeli-product-reels/creator-brief.md:14`); a new edit on @lumebook.il is a different use, so confirm with each creator, and tag her as a collaborator. All three show the children's faces (playbook section 6, S5). The build had one trap: a stream-copied concat that starts with a still hung the final encode, so `build_options.py` joins the shots with the concat filter.

## Mom-voice versions (supersede the 8-second options)

Yarin on the 8-second options: no length limit, a bold white hook burned in at the top, word-by-word white captions at the bottom, both in Instagram's default font, and the ElevenLabs voice does not sound natural, warm, Israeli or like a mom. So these keep each creator's own narration: `final/mom-voice-natali.mp4` (21.0 s), `mom-voice-nofit.mp4` (23.2 s), `mom-voice-moran.mp4` (22.9 s). Built by `moms/build_moms.py` from `moms/clips.json` (her segments and crop windows) and `moms/copy-moms.json` (hooks and CTA).

- **Voice:** her own lines, cut at word boundaries from `moms/<name>-words.json` (ivrit-ai whisper large-v3, word timestamps, `moms/transcribe.py`). Dropped: anything about AI (Natali's "ובעזרת AI" as a jump cut, Moran's model and "AI אשכרה מתאים" lines), Moran's 99-shekel price and "עוד לא ראיתי את זה באף מקום", and each creator's own "go to the site" ending. Where she is off camera a stronger shot can carry her voice (Natali's "מאז שיש לנו את לומבוק" over her son holding the cover; Moran's first 0.9 s over the cover, because her edit opens with a slide-up from black).
- **Hook:** her story as the gap, from her own words: "צרחות ובכי בכל בוקר בגן / עד שמצאתי את זה", "הפרידות בבוקר היו קשות / עד שעשינו את זה", "המתנה שכל המשפחה / לא הפסיקה לדבר עליה". Bold white, top, inside the safe zone; for the last 2.6 s it becomes the CTA (`כתבו "לומי" בתגובות...`) over a closing shot with her voice muted.
- **Captions:** one word at a time, white, timed to her voice; brand written לומבוק (she says "לומי בוק"), "הפרדות" spelled הפרידות. Placed on the lowest line inside the safe zone (just above the bottom 35%, where Instagram's caption and buttons sit, playbook section 6) rather than at the very bottom.
- **Font:** SF Hebrew Bold (hook) and Medium (captions) with a soft shadow, my closest match to Instagram's own text on iPhone; not checked against the app.
- **Checks:** a second transcription of each finished file put a caption on screen for every spoken word; the caption starts a median 0.02 to 0.03 s before the word (worst 0.26 s early); 78 to 89% of words match exactly 0.1 s in, the rest are short words split differently. -13.4 to -15.5 LUFS. No creator captions visible in any frame.
- **Watch-outs:** Natali's speech pauses sit at -24 dB against -21.5 dB in speech, so a music bed probably runs under her voice; if it is a licensed track, Instagram may mute a business-account repost. Confirm with each creator that LumeBook may post this edit of her video and voice (the creator brief records consent for the public brief page only, `research/israeli-product-reels/creator-brief.md:14`).

## Source

Drive `שיווק / חומרי גלם / ספרים פיזיים / 2026-10-11 תקריבים`, the "ספר סבתא אפייה" book (a dedication from סבתא מיכל וסבא מיכאל to אימרי מיכאל). The five clips under the Drive connector's 10 MB limit, in `source/`:

| Clip | Drive id | Used for |
|---|---|---|
| `..._תקריב-איור_01_IMG3840.mov` | 1hD2ByWDMTeP7sd0yvjjiq5q2xrrJE0N9 | 0:00 grandma and grandson baking (hook, "הוא הגיבור של הסיפור") |
| `..._תקריב-טקסט-עמודים_03_IMG3842.mov` | 1ZFVm5SrEagSTaBgUAdAiy--XQvRCxBUW | his name in the text (one frame, push-in) |
| `..._תקריב-הקדשה-וטקסט_02_IMG3841.mov` | 1HCHH0tALkyFQa5nH8sgjkod1brCxwVU0 | the dedication |
| `..._דפדוף-עמודים_05_IMG3844.mov` | 1rJRuOT2NKFHffZ2dui1u210z4oZCVhw- | flip through the pages |
| `..._דפדוף-מהכריכה-והקדשה_04_IMG3843.mov` | 17iip5MPaeMVIklznKwxZAKwMBg8WSpA- | flip back to the title page, end card |

Not used: `וידאו_06` (79 MB) and `וידאו_07` (162 MB). The connector stops at 10 MB and the built-in browser was refused on drive.usercontent.google.com, so they were not downloaded. Drop them in `source/` for a longer cut.

The clips are iPhone HLG HDR (BT.2020). This ffmpeg has no zscale or libplacebo, and its `colorspace` fallback washed the colours out, so each clip goes through macOS first:

```bash
avconvert --source source/<clip>.mov --output work/sdr/clipNN.mov --preset Preset1920x1080 --replace
```

## Build

```bash
~/.claude/skills/watch-video/.venv/bin/python build.py sarah     # or matilda
```

`build.py` cuts the segments to the voice's beat times (pause midpoints from the ElevenLabs character timestamps), renders the Hebrew cards with Pillow (Heebo Bold, white on `--tint` purple), overlays them and mixes the voice. `copy.json` holds the on-screen text and the caption. `work/` is regenerated by the build.

## Script

| Time (Sarah) | Picture | On screen | Voice |
|---|---|---|---|
| 0:00-3.2 | Grandma laughing, baking | מתנה לנכד / שאין לאף ילד אחר | מתנה לנכד, שאין לאף ילד אחר |
| 3.2-5.95 | The grandson in the same illustration | הוא הגיבור של הסיפור | ספר שהנכד שלכם הוא הגיבור שלו |
| 5.95-8.0 | His name in the text | עם השם שלו | עם השם שלו בתוך הסיפור |
| 8.0-10.85 | The dedication | והקדשה מסבא וסבתא | ועמוד הקדשה, מסבא וסבתא |
| 10.85-14.45 | Flip through the printed pages | ספר מודפס / ועותק דיגיטלי במתנה | מקבלים ספר מודפס, ועותק דיגיטלי במתנה |
| 14.45-18.3 | Flip back to the title page | ספר ב-119 ש״ח / ומשלוח עד הבית ב-30 ש״ח | מאה ותשעה עשר שקלים, ומשלוח עד הבית בשלושים |
| 18.3-23.2 | Title page, slow push-in | כתבו "לומי" בתגובות / וקבלו קישור לספר / שבו הנכד שלכם הגיבור | כתבו לומי בתגובות, ונשלח לכם קישור |

Price and digital copy checked on lumebook.com/IL/he on 24 Oct 2026: "ספר ₪119 + משלוח ₪30" and "עותק דיגיטלי במתנה בכל הזמנה". The price card shows both numbers together (playbook S3, Consumer Protection Law s.17ד). Re-check on the day you post.

Caption (in `copy.json`):

```text
מתנה לנכד שאין לאף ילד אחר
ספר שהוא הגיבור שלו
עם השם שלו והקדשה מכם
ספר מודפס ועותק דיגיטלי במתנה
119 ש״ח ומשלוח עד הבית ב-30 ש״ח
את הסיפור קוראים בחינם לפני שמזמינים
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הנכד שלכם הוא הגיבור
```

On-screen text and every caption line pass `voice_lint.py --cta cta --code-word לומי` (calibrated voice, 37 samples). The only lint error left is the caption's total word count, a per-slide limit that does not apply to a post caption.

## Before posting

1. **Whose book is this?** The reel shows a real child's name (אימרי מיכאל), his photo on the title page (end card, about 5 s) and the grandparents' names in the dedication. Post only with that family's written OK (playbook section 6, S5). If there is none, the photo can be blurred on the end card and the name shot swapped.
2. Pick the voice (Sarah or Matilda), or record your own over the same timeline: the playbook's research check says your own voice from 0:00 is the stronger test.
3. Add a quiet track in Instagram, tag @lumebook.il, use the caption above.
4. DM link for "לומי": `utm_source=instagram&utm_medium=reel&utm_campaign=grandparent-gift&utm_content=c5-v1` (lower case, playbook section 7). Log skip rate, average watch time, sends and non-follower share after 24 hours.
5. Once approved, copy the chosen final to Drive `LumeBook תוכן / reels / 2026-10-24-grandma-baking-book-reel` (Drive for desktop is not installed, so it was not uploaded).

## Cost

ElevenLabs Eleven v4 on fal (`elevenlabs/tts/eleven-v4`, $0.08 per 1,000 characters, read 24 Oct): two full takes of 230 characters plus four 8-second takes of about 100 characters, about $0.08. Everything else was local.
