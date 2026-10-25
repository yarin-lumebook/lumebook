# Genjutsu Lite trend recreations (25 Oct 2026)

Yarin picked six of the 20 trends found in Higgsfield's Genjutsu "Community trending" feed on 25 Oct (list and reasons in that day's chat) and asked to make all of them on the free Genjutsu Lite generations, generating or pulling from Drive whatever input was missing.

**Status: all six generated on 25 Oct on Yarin's free Genjutsu Lite generations (10 a month on Plus; 4 left afterwards), 1080p, no credits spent.** The free generations work only on higgsfield.ai, not through the CLI (pricing page footnote, read 25 Oct), so the jobs were submitted in the website from the browser pane after Yarin signed in.

## Results (`results/`, contact sheets in `qc/`)

| # | File | Job id |
|---|---|---|
| 1 | `results/01-book-3d-v1-1080p.mp4` | 88cac170-136b-4c7d-a818-15aad1f3196c |
| 2 | `results/02-ben-window-v1-1080p.mp4` | cc9a436a-1d84-4673-a660-23b1c02d1f2b |
| 3 | `results/03-mom-fridge-v1-1080p.mp4` | 69ca0458-a998-4968-a384-17ebc3f1e268 |
| 4 | `results/04-lume-books-dance-v1-1080p.mp4` | dc727b2f-7c20-4533-83e5-d36aa49a642e |
| 5 | `results/05-ben-lume-dance-v1-1080p.mp4` | 40754f99-ea47-4088-8529-231ef451a967 |
| 6 | `results/06-mom-spa-v1-1080p.mp4` | 1fd3aaa0-b6b9-4f8b-9d4a-c94589515c68 |

All 1080x1920, 24 fps, no audio (the original sound of each reference is in `refs/audio/`).

How the website runs it (learned 25 Oct): on higgsfield.ai Genjutsu Lite always runs as **object swap** (`hf_mult_replace_object_flash`): the page code forces `replace-objects` for the Lite model even with `&type=motion-control` in the address, so the original scene stays and only the named characters and objects change. Motion transfer Lite (`hf_mult_motion_control_flash`) exists only through the CLI, on credits. Website steps that worked: the media picker's Uploads tab, "All" (newest first; "Recent" sorts by last use, so new CLI uploads are not at the top), pick by the upload id in each tile's thumbnail URL; in the Lexical prompt box type `@` and choose from the menu (order: Video 1, Image 1, Image 2...); switch on "Use free generations" and check the Generate button says Free; set Quality to 1080p (still free). Clear the prompt box with a select-all through the page (cmd+a by keyboard sometimes missed), and remove the old media before adding new ones, because removing an image renumbers the mentions left in the old prompt.

QC notes:
- 1: the open book floats, turns, shows the cover ("ספר היום הולדת של בן", LumeBook logo), close-ups of the page edge, then the top-down spread. In some frames the last two title words run together ("הולדתשל").
- 2: Ben on model (glasses, hair, white T-shirt) reads his book in the night window; at the end he lays it open on the sill and looks at the camera.
- 3: mom on model, grey sweater, chocolate birthday cake with sprinkles in the foil tray; the hand at the right edge came out adult-sized, not a toddler's.
- 4: Lume on model (purple-tipped tail, blue eyes) does the paw dance and the face close-up among stacks of LumeBooks, a floating open book above. Hila's book reads right ("ספר היום הולדת של הילה"); Ben's book in the stack carries a wrong title (first word garbled and "של הילה" instead of "של בן"), and the floating book's page text is gibberish. Crop or blur before posting, or rerun.
- 5: Ben (glasses, white T-shirt, beige shorts) and Lume do the shocked close-ups and the yard dance; Lume came out taller than Ben; one blurred paw fills the frame near the end, as in the original.
- 6: mom on model in the pink robe, towel turban and cat-eye sunglasses, phone, bubble tea, chips, popcorn and the pink chocolate bar; Ben's book lies on the bed with a correct title ("ספר היום הולדת של בן") and comes close to the camera at the end. No caption was baked in.

## Sound (`results/*-v1-1080p-sound.mp4`, 25 Oct)

Yarin asked for audio on all six. `audio/mux.sh` puts the trend's own sound back under each result from the same start point as the trimmed reference, levels it to -14 LUFS (true peak under -1 dB) with a short fade in and a 0.5 s fade out; the picture is stream-copied. The silent `*-v1-1080p.mp4` files stay as they were.
- 1 book: the reference had no sound at all, so a sound bed was generated: Seed Audio 1.0 on Higgsfield (`audio/01-book-3d-sound-seed-v1.wav`, prompt `inputs/prompts/a1-book-sound.txt`, job f2d5b230, 0.1 credits, exactly 7.0 s): airy whoosh, page flutter, shimmer and chimes, a soft settle at the end. Checked by spectrogram only, not by ear.
- 2 window: the original sound (mostly laughter), from 0.
- 3 fridge: the original sound (music) from 8.7 s, matching the trim.
- 4 Lume: Higgsfield's copy of this trend is silent until its end card, so the sound comes from the original reel, instagram.com/cookie_mat_hongcha/reel/DejGvU3yAS- (13.375 s, frames line up with the reference at 2, 6 and 10 s), saved as `refs/audio/04-lume-books-dance-reel-audio.m4a`.
- 5 Ben and Lume: the original sound (music) from 0, to 21.0 s.
- 6 mom spa: the original sound, a song with English lyrics, from 0.
These are other creators' sounds (songs in 3 to 6); before posting from the business account, check they can be used, or pick the same sound from Instagram's library when uploading.

## Captions (`captions.json`, 25 Oct)

Yarin asked for 10 caption options per reel using everything learned about Reels. `captions.json` holds 10 on-screen hook captions per video plus one shared end CTA (`כתבו "לומי" בתגובות / וקבלו קישור לספר / שבו הילד שלכם הגיבור`, the same as the 24 Oct reels). What they follow:
- Yarin's calibrated voice (40 logged rewrites in the hebrew voice skill) and his own caption formats on the 19 and 21 Oct Genjutsu reels: "כש...", "POV", "זה מה שקורה כש...", mom in the first person, an emoji at the end now and then.
- `research/israeli-product-reels/playbook.md` section 8: hook text on the first frame; relatable moments and humour beat product pitches (humour clearly higher, product showcase clearly lower in the 173 Reels), so 5 of the 6 sets open on a parent moment, not the product; one CTA, on screen for the last 2 to 3 seconds; text below the top 14% of the frame.
- Audience rules: no dash, semicolon or hyphen, no AI, no guilt or fake certainty, no "כל הילדים"; lines up to 7 words, captions up to 12.
- Product facts used in set 1 (name on the cover, the child in the pictures inside) come from the 15 Oct product facts in the playbook header.
All 60 and the CTA pass `voice_lint.py --cta cta --code-word לומי`; the six "POV" lines warn about Latin text in RTL (Yarin used the format on 21 Oct), so check them in the render. Set 6 line 1 is the trend's own English joke in Hebrew. Not yet burned in.

## Ben in the window: five captioned versions (`captioned/`, 25 Oct)

Yarin picked five hooks for video 2 (four from the list, line 2 and line 5 in his own words) and asked for "הסבר בתיאור👇🏻" at the bottom, white, bold, Instagram's default font. `captioned/build_captions.py` (run with the watch-video `.venv` Python) burns both into `results/02-ben-window-v1-1080p-sound.mp4`, sound kept:
- `02-ben-window-caption-1.mp4`: השעה עשר בלילה / ומישהו פה לא הולך לישון
- `02-ben-window-caption-2.mp4`: מה הוא עושה אחרי / שאני אומרת לו לכבות את האור
- `02-ben-window-caption-3.mp4`: השכנים שאלו / למה האור אצלו דולק בלילה
- `02-ben-window-caption-4.mp4`: מה הוא עושה / כשהוא חושב שכולם ישנים
- `02-ben-window-caption-5.mp4`: כש״עוד עמוד אחד אמא״ / מקבל משמעות חדשה (Yarin wrote it as one line; split after the quote so it stays at full size)
Look: SF Hebrew Bold white with a soft shadow (the stand-in for Instagram's font, as on the 19 and 21 Oct reels), hook from y 290 (below the top 14%), the bottom line ending at 65% of the height, the lowest line Instagram's buttons and description do not cover; it sits over Ben's book. No flip or zoom: a mirrored frame would reverse the Hebrew on the book. The 👇🏻 is drawn by macOS (`captioned/emoji_png.swift`), because Pillow without raqm splits skin-tone emoji into a yellow hand and a colour square. Positions per version: `captioned/ben-window-versions.json`; check sheet: `qc/ben-window-captions-sheet.jpg` (magenta lines at 14% and 65%). No end CTA, since the bottom line sends viewers to the description.

Trial reel versions (Yarin, 25 Oct: some flipped and each zoomed by a small random amount, so Instagram does not treat the five uploads as repeats): `captioned/trial/02-ben-window-trial-1..5.mp4`, built by `build_captions.py --trial`. Seeded, recorded in `captioned/trial/ben-window-versions.json`: 1 flipped, zoom 1.073; 2 not flipped, 1.087; 3 flipped, 1.063; 4 not flipped, 1.028; 5 flipped, 1.044. The crop sits at a random spot sideways and between the top and the centre vertically. Picture first, captions on top, so no text is mirrored; in the flipped versions the title on Ben's book is mirrored. Check sheet: `qc/ben-window-trial-sheet.jpg`. The plain `02-ben-window-caption-1..5.mp4` stay as they were.
Speed and length added the same day (Yarin: "nothing substantial"): each version also plays at its own speed (audio tempo-matched, pitch kept) with 0 to 0.35 s trimmed at each end and a 0.3 s sound fade at the end: 1 at 1.036x, 12.6 s; 2 at 1.051x, 12.2 s; 3 at 0.963x, 13.5 s; 4 at 0.982x, 13.0 s; 5 at 1.018x, 12.8 s (original 13.3 s). Values in `captioned/trial/ben-window-versions.json`; first frames in `qc/ben-window-trial-v2-first-frames.jpg`.

Description (the post text "הסבר בתיאור" points to): `captioned/02-ben-window-description.txt`, one text for all five versions. It explains the reel (he is reading a book where he is the hero), then how it works and the one CTA with "לומי". Product facts re-read on https://lumebook.com/IL/he on 25 Oct: upload a photo and add the name, free preview, pay only if you liked it, printed book with a free digital copy. No price (the ₪119 shown without the ₪30 delivery is an open legal question in the reels research notes) and no brand name, like the 24 Oct reel caption; no hashtags, like the approved carousel captions. Passes `voice_lint.py` line by line with `--cta cta --code-word לומי`.

Next: export the approved versions to Drive `LumeBook תוכן`; make sure "לומי" comments get the link. 4 free Genjutsu Lite generations left this month for reruns (#4's title is the obvious one).

## The six jobs

| # | Trend (Higgsfield title, likes on 25 Oct) | Reference clip | Images, in attach order | Prompt |
|---|---|---|---|---|
| 1 | Studio Product Showcase (614) | `refs/01-book-3d-ref.mp4`, 7.0 s | Image 1 open book, Image 2 closed book | `prompts/01-book-3d.txt` |
| 2 | Window Dog (246) | `refs/02-ben-window-ref.mp4`, 13.3 s | Image 1 Ben, Image 2 open book | `prompts/02-ben-window.txt` |
| 3 | Midnight Fridge Feast (363) | `refs/03-mom-fridge-ref.mp4`, 12.0 s | Image 1 mom | `prompts/03-mom-fridge.txt` |
| 4 | Feline Dance Pose (315) | `refs/04-lume-books-dance-ref.mp4`, 13.3 s | Image 1 Lume, Image 2 Ben's closed book, Image 3 Hila's book | `prompts/04-lume-books-dance.txt` |
| 5 | Feline Dance Duo (556) | `refs/05-ben-lume-dance-ref.mp4`, 21.0 s | Image 1 Ben, Image 2 Lume | `prompts/05-ben-lume-dance.txt` |
| 6 | Pampered Spa Feline (87) | `refs/06-mom-spa-ref.mp4`, 11.0 s | Image 1 mom, Image 2 closed book | `prompts/06-mom-spa.txt` |

Upload ids for every clip and image: `inputs/uploads.tsv` (they show in the website's media picker, Uploads tab). If the website route fails, the same jobs through the CLI (`hf_mult_motion_control_flash`, 720p) were quoted at 14, 26, 24, 26, 30 and 22 credits: 142 in all.

## References (`refs/`)

- `*-original.mp4`: the clips as served by Higgsfield's community presets (originally other creators' Reels and TikToks; internal reference only).
- `*-ref.mp4`: what gets uploaded, all without audio (a known song can trigger `ip_detected`). The original sound of each is in `refs/audio/`.
  - 03: 8.7 s to 20.7 s of the original (after a black frame and a WhatsApp banner), cropped to 9:16 from the left so the TikTok buttons on the right are gone, 720x1280 at 30 fps.
  - 04: cut at 13.3 s, before the Instagram end card.
  - 05: cut at 20.95 s, before the TikTok end card.
- `trends.json`: preset ids, likes, original and example URLs, and the community example's prompt.

## Inputs (`inputs/`)

From Drive (`שיווק`, owner Support@lumebook.com), in `inputs/drive/`:
- `cover_book15_יום_הולדת___מלך_ליום_אחד.png`: the "birthday, king for a day" boy cover art, the base for Ben's book.
- `physical-family-spread-v01.png`: the family recipe book lying open, used as the format reference for the open-book mockup.
- Also pulled for a look, not used: `physical-open-book-v01.png`, `physical-open-book-thin-v02.png`, `interior-family-branded-v01.png`, and two pages of book 94 (an IAI book, left out because it carries a client's logo).

Generated on Higgsfield (`inputs/generated/`, prompts in `inputs/prompts/`, 12 credits in all):
- `ben-cover-art-v1.png`: Nano Banana 2, the Drive cover redrawn with Ben (glasses, crown, cake). Job 11f8fe8b.
- `ben-page2-art-v1.png`: Nano Banana 2, the next page: Ben hugging mom on the sofa with a present. Job f0d2ee3c.
- `mom-portrait-v1.png`: Seedream 5.0 Pro from the mom in `../2026-10-11-fan-transition-reel/stills/02-kid-mom.png` (crop: `mom-crop-from-fan-transition.png`), so both mom videos share one face. Job 834686d7.
- `ben-book-closed-v1.png`: GPT Image 2.5 high, the Hila book mockup with Ben's art and the title "ספר היום הולדת של בן" (checked letter by letter). Job 7b980493.
- `ben-book-open-v1.png`: GPT Image 2.5 high, the same book lying open on light grey: cover art on the left page, page 2 on the right, no text on the pages. Job 0e7655f6.

Characters reused: Ben `../2026-10-11-toddler-character-pack/final/01_front.png`, Lume `../2026-10-11-lume-character-pack/final/01_front.png`, Hila's book `../2026-10-16-genjutsu-truck-box/inputs/book-birthday-hila.png`.

## Before posting

- These are recreations of other creators' trends; captions and sound are added afterwards (the mom spa original carried an English caption, to be replaced with Hebrew in post).
- Ben is a generated character, so no family permission is needed; the mom is generated too.
