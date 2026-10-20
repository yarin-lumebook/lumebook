# Coding brief: Israeli creator product Reels (first pass)

You are watching Instagram Reels by Israeli creators for LumeBook (personalised children's books, Israel). The goal is a filming education for LumeBook's solo social media manager, who films with a phone at home. Accuracy beats coverage: never invent dialogue, shots, timestamps, metrics or creator details.

## Inputs per Reel CODE

All under `/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-15-israeli-product-reels/`:

- `analysis/CODE/index.json`: duration, `cuts` (scene-change timestamps in seconds from ffmpeg, threshold 0.28; it misses soft cuts and can fire on fast motion), `sheets`.
- `analysis/CODE/sheet_NN.jpg`: contact sheets, 6 frames each, one frame per second (1.5 s for long videos), timestamp above each frame (accurate to about ±0.5 s). **Open every sheet.**
- `analysis/CODE/whisper.srt` and `whisper.txt`: a local machine transcript (Whisper turbo, Hebrew). It can mishear words, it transcribes song lyrics as if they were speech, and it often outputs "תודה רבה" or nothing on music-only audio. If the file is missing, wait 2 minutes and check again (up to 20 minutes); if still missing, write `"transcript": "unavailable"`.
- `videos/CODE.info.json`: `description` is the caption, `upload_date`, `like_count`, `comment_count`, `channel` is the posting handle.
- `/Users/yarinbruner/Claude/Projects/Lumebook/research/israeli-product-reels/src/media_info_15oct.json`: owner, coauthors (collab partners), Instagram paid-partnership label, plays, likes, comments, duration, read 15 Oct 2026.

You cannot hear audio. Speech comes only from the transcript. Decide whether speech is direct-to-camera (mouth moving, facing lens, in sync with the transcript timing) or voiceover (speech while the frames show hands, the product or someone not talking). Music: say "music likely" only when the transcript shows lyrics, a music sticker or note is visible, or there is no speech at all; otherwise "unclear".

## Output

Write `/Users/yarinbruner/Claude/Projects/Lumebook/research/israeli-product-reels/src/coded/CODE.json` (valid JSON, UTF-8, escape quotes inside strings). Fields:

```json
{
  "code": "",
  "url": "https://www.instagram.com/reel/CODE/",
  "handle": "",
  "creator_type": "parent creator | professional (say which: SLP, OT, gan teacher...) | UGC creator | photographer | entertainer | other",
  "product": "what exactly, brand if named on screen or in the caption",
  "category": "personalised_book | childrens_book | toy_game | educational | parenting_product | gift | other",
  "include": true,
  "exclude_reason": "only if include=false: not a physical product, slideshow only, synthetic presenter, polished commercial with no creator filming, not Hebrew/Israeli",
  "language": "Hebrew | other",
  "relationship": "creator_posted | collaboration (coauthor=X) | brand_repost",
  "disclosure_visible": "exact words from caption or screen (e.g. 'שת\"פ', 'בשיתוף', 'פרסום', paid-partnership label) or 'none visible'",
  "format": "one short phrase: e.g. talking-head recommendation, hands-only demo with voiceover, unboxing, reaction, vlog story, skit, book list",
  "hook_0_3s": {
    "opening_image": "what the first frame shows",
    "spoken": "transcript words in the first ~3 s with timestamps, or 'none'",
    "on_screen_text": "exact Hebrew text visible in 0-3 s, or 'none'; say 'partly unreadable' when needed",
    "reason_to_keep_watching": "interpretation, labelled as such"
  },
  "shots": [
    {"start": 0.0, "end": 2.0, "framing": "close-up | medium | wide | top-down | POV | screen recording", "angle": "eye level | high | low | over-shoulder", "movement": "static | handheld | pan | tilt | push-in | unclear", "subject": "", "purpose": "what this shot contributes"}
  ],
  "n_shots_estimate": 0,
  "product_first_seen_s": 0.0,
  "value_understandable_s": 0.0,
  "how_value_is_shown": "",
  "demonstration": "what is shown being used, or 'none'",
  "proof": "what evidence is offered (result on screen, before/after, comparison, child using it) or 'none'",
  "emotion": "",
  "personal_story": "",
  "selling_language": "short quotes (max 12 words each) of claims, price, urgency, discount",
  "audio": {"speech": "direct-to-camera | voiceover | both | none", "music": "likely | unclear | none evident", "natural_sound": "evident from transcript or 'unclear'"},
  "captions_on_screen": "burned-in subtitles of speech | headline text | text boxes | none; style notes",
  "editing_rhythm": "number of shots, average shot length, any jump cuts or speed changes",
  "ending_and_cta": "what the last 3 s show and any CTA in video or caption (comment a word, link in bio, code)",
  "price_or_code": "",
  "convincing": "interpretation: what feels convincing and why",
  "weak_or_overproduced": "interpretation: what feels weak and why",
  "lumebook_lesson": "what LumeBook's SMM can learn and recreate with a phone",
  "solo_without_child": "yes | partly | no, with one line why",
  "relevance": "high | medium | low",
  "transcript_quality": "good | partial | poor | music only | unavailable",
  "not_verified": "anything you could not establish"
}
```

## Rules

- Quote Hebrew exactly as it appears; never "correct" it. Quotes from the transcript are marked as machine transcript. Keep quotes short.
- Observed facts in the descriptive fields; opinions only in `reason_to_keep_watching`, `convincing`, `weak_or_overproduced`, `lumebook_lesson` and say "interpretation".
- Do not claim sales, reach or retention. Plays and likes are public counts only.
- Do not name or describe children beyond what is needed (age range if visible, "a toddler", "a girl about 5").
- No em dashes in your output.
- When done with all your Reels, reply with one line per Reel: CODE, include yes/no, relevance, one-line summary.

## Extra fields (added 15 Oct, round 2)

Add these to every JSON, at the top level, each answered from the frames (and caption where said):

```json
{
  "child_on_camera": "yes | no | only hands or back of head",
  "face_on_camera": "creator's face | no face (hands only) | other adult",
  "price_on_screen": "the price as shown in the video, or 'no'",
  "price_in_caption": "the price as written in the caption, or 'no'",
  "likeness_proof": "for personalised products: 'photo beside illustration' | 'name visible on page' | 'no' ; otherwise 'n/a'",
  "screen_recording": "yes | no (a phone or computer screen recording appears)",
  "cta_type": ["comment_word", "code", "link_in_bio", "dm", "follow", "save_or_share", "website", "none"],
  "comment_word": "the exact word, or 'none'",
  "brand": "the product's brand as shown or tagged, or 'none visible'"
}
```

`cta_type` lists every CTA in the video or caption. A code mentioned only as "coupon in the caption" counts as `code`.

## Working order (round 2)

Code one Reel at a time: open its contact sheets, write its JSON straight away, then move to the next Reel. Images you opened earlier may be dropped from your view ("media removed") once many are open; if a sheet you need comes back that way, open it again before writing the field. Never fill a visual field from memory or guesswork: if you could not see it, say so in `not_verified`.
