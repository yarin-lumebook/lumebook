# Story series (סטוריז)

Started 19 / 11 / 2026. Yarin: "use my chatgpt through chrome to create a daily story series we can schedule in postiz, i want one for hannukah one for black friday and one with 3-5 reviews ... (they end at the last day of each event) ... add it to our content-calendar with full story editing capabilities ... first create 1 day batch, let me review it". Later the same day: "use the real comments and reviews screenshots just blur the names" and "i want to promote this https://lumebook.com/IL/he/holiday-cards for hanukkah".

Edited in the content calendar (http://localhost:8780/sites/content-calendar/, a set opens like any piece). Nothing here goes to Postiz without Yarin's approval of exactly that content and his click.

## The three series

| Key | Series | Days (my proposal, waiting for Yarin) | Time | Leads to |
|---|---|---|---|---|
| `bf` | בלאק פריידיי | 23 / 11 to 30 / 11 / 2026 (Cyber Monday) | 19:30 | /books, with the campaign tag `bf-2026`. Follows the story sequence of brief 5 in `research/hanukkah-black-friday-2026/black-friday.md` (anticipation, proof and questions, then from 25 / 11 the offer: first book 119, second 99). No price on a frame until Yarin approves price outside reels |
| `hanukkah` | חנוכה | 23 / 11 to 12 / 12 / 2026 (the last day of Hanukkah) | 14:30 | /holiday-cards, the free gift (greeting card or colouring booklet). Every frame promotes it |
| `reviews` | ביקורות | 23 / 11 to 12 / 12 / 2026 | 10:30 | the store. 3 to 5 real screenshots a day, names and profile photos blurred |

Links carry `utm_source=instagram&utm_medium=social&utm_campaign=<bf-2026 | story-hanukkah | story-reviews>&utm_content=story-YYYYMMDD` (the carousel audit's scheme, medium `social` is the value that counts as Yarin's).

## Files

| File | What |
|---|---|
| `series.json` | The source: `series` (name, dates, default time, link) and `sets`, one per series and day (`<series>-<date>`). A set has `frames`; a frame is data: `bg` (picture, fill, position, zoom), `scrim`, `layers` (text, image, shape, sticker placeholder), `note`, `ask` (a request for a new picture), `manual` (posted by hand from the phone). Removed sets go to `removed`, never deleted |
| `art/` | Backgrounds made in Yarin's ChatGPT through Claude in Chrome (3D animated look, violet and gold, no text, no books, no people). Named for what they show |
| `uploads/` | Pictures dropped in the editor |
| `frames/<set>/<frame id>.png` | 1080 x 1920 PNGs drawn by `tools/stories.py render` with the editor's own renderer (`sites/content-calendar/story-frame.js`) in headless Chrome. What goes to Postiz |
| `make_sets.py` | Seeds days of the series (`python3 make_sets.py day1`). Never overwrites an approved or sent set |
| `find_names.swift` | macOS Vision text finder for the review screenshots (Latin only: it finds Instagram usernames; Google names sit in a fixed strip). Compiled once into the temp folder by `tools/stories.py` |
| `blur-boxes.json` | Where the builder put each screenshot's blur boxes and how it found them |

## Rules

- Review frames: the real screenshot from `media/projects/2026-11-15-social-proof/` (never one in its `removed.json`, no WhatsApp chats, no comment that tags someone with @), the writer's name and profile photo blurred inside the PNG. Google screenshots get a large pull quote of their own words above them (their text is about 22 px on 1140, too small to read in a story); cuts are marked with … and the builder checks every piece is word for word. Check every blur by eye before approving: the boxes move in the editor.
- Copy: the project's Hebrew rules (no dash, no semicolon, לומבוק, no AI wording, "קישור אישי" never "קוד"); `tools/stories.py` lints every text layer and blocks approval on an error.
- Stickers: Postiz cannot send Instagram stickers (link, poll, question, countdown) and a sticker cannot be added to a story after it is up. A frame with a sticker is either marked `manual` and posted from the phone with the sticker, or sent through Postiz without it. Yarin decides (open question, 19 / 11 / 2026).
- Postiz: one post per frame (Instagram takes one picture per story post; Facebook publishes each picture as its own story), both channels in each, one minute apart. Approved content only, fresh PNGs only, never twice; a set in Postiz can no longer be edited or moved from the calendar.
- ChatGPT in Chrome is used here because Yarin asked for it on 19 / 11 / 2026; Carousel Machine still makes its pictures only through the OpenAI API.

## Status

- 19 / 11 / 2026: day 1 (23 / 11) of all three series made, for Yarin's review: Black Friday 3 frames, Hanukkah 3 frames, reviews 4 frames. Not approved, not in Postiz.
- Next, after Yarin's review: the rest of the days to 30 / 11 (Black Friday) and 12 / 12 (Hanukkah, reviews), reviewed again before anything is scheduled.
- 19 / 11 / 2026, from the Black Friday session (sent with Yarin's OK): the `bf` days follow brief 5's twelve frames by date (19 to 21 anticipation, 22 to 24 proof, 25 to 26 offer, 27 the day itself, 28 to 30 after). Guardrails: no price until Yarin approves it, no countdown to the offer's end without an end date (the 05 / 12 Hanukkah order countdown is fine), never "see the whole book before paying" (say "תצוגה מקדימה"), link tag `bf-2026`. Day 1 is in the proof stage; the anticipation frames need the series to start before 23 / 11 if Yarin wants them.
