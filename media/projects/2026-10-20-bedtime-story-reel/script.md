# Bedtime story reel: Ariel's book (draft v1, 20 Oct 2026)

Status: **draft, waiting for Yarin's approval. Nothing paid has run.**

## The reference

MeBook reel by @liron_ofir, 12 Aug 2026, 2:56 ([instagram.com/reel/Db79B6COOSN](https://www.instagram.com/reel/Db79B6COOSN/)). Watched frame by frame; no captions, and I cannot hear audio, so the sound below is inferred from the on-screen text.

What it does (observed):

- The whole reel is one book-page layout: brand logo bar on top, an animated illustration in the middle, white text panel below.
- The text panel holds what is being said, one beat per line (a dad improvising a bedtime story with his son, the kid's answers included).
- Each page holds its text while two to five short animated shots play in the window (the kid hero in a castle, a sword, a dragon).
- Page-curl transitions between pages.
- Real-life shots drop into the same window: dad reading on the couch, the boy laughing, dad thinking.
- Ends full screen on a real moment: dad hugging the boy, logo in the corner.

What we keep: the page layout, one beat per line in the panel, the kid as the hero, real moments cut into the window, a real ending. What we change: a narrator reads Ariel's real LumeBook book (the text on screen is the book's own text), 35 s instead of 3 min (`research/israeli-product-reels/playbook.md:92` says aim for 20 to 35 s), and a CTA at the end.

## Our content

Drive: `שיווק / תוכן לקוחות ויוצרים (UGC) / sapir_ivan_mugatz` (uploaded today). Sapir got Ariel's book "באנו חושך לגרש" as a gift (creator map: stage `booksent`). Five clips:

| File | Size | Status |
|---|---|---|
| `edited-reel_ariel-book.mov` | 8 MB | downloaded to `references/` |
| `screen-recording_book-preview-pages.mov` | 17 MB | **needed**, over the Drive connector's 10 MB limit |
| `raw_flipping-through-book.mov` | 34 MB | **needed**, same |
| `raw_holding-cover-smile.mov` | 18 MB | **needed**, same |
| `screen-recording_site-catalog-to-preview.mov` | 13 MB | optional |

Sapir's edited reel has her own captions burned in (one says the book was made with AI, which we never say) and a CapCut mark, so the final uses the raw clips. The draft borrows from the edited reel only.

## Script (about 35 s)

Narrator: one warm female voice, slow bedtime pace. It reads; it is not Sapir and is never presented as her. Panel text = exactly what the narrator reads at that moment. Book lines keep the book's words; commas and periods become line breaks.

| # | Time | Window (middle) | Panel text (on screen) | Sound |
|---|---|---|---|---|
| 1 | 0:00-0:03 | Real: Ariel opens the box and finds the book | סיפור לפני השינה<br>שבו אריאל הוא הגיבור | Narrator reads the two lines |
| 2 | 0:03-0:05 | Ariel's cover, slow push in | באנו חושך לגרש | Narrator reads the title |
| 3 | 0:05-0:11 | Page 5: Ariel and his puppy over a glowing book | זה היה לילה שקט<br>בחדרם של אריאל ואורי<br>״מה אם יצוץ משהו?<br>מתוך החשך הגובר״ | Narrator (text page 4, lines 1 and 4) |
| 4 | 0:11-0:17 | Page 7: Ariel peeks under the bed, a monster eye looks back | אריאל התכופף<br>פתח את עיניו<br>וראה מפלצת כחולה וקטנה<br>רועדת בין ברכיה | Narrator (text page 6) |
| 5 | 0:17-0:19 | Real: Ariel flipping pages | (panel keeps beat 4) | Page-turn sound |
| 6 | 0:19-0:23 | Page 9: Ariel laughing with the monster | ״מי אתה?״ שאל אריאל בקול<br>״אני? אני חשכוני״ | Narrator (text page 8) |
| 7 | 0:23-0:29 | Page 11 (not seen yet; draft repeats the cover) | אריאל חייך ואמר<br>״אולי במקום לפחד<br>ננסה לגלות יחדיו<br>שהחשך הוא לא אויב״ | Narrator (text page 10) |
| 8 | 0:29-0:32 | Real, full screen: Ariel laughing with his book | (no panel) | **Ariel's own voice** from Sapir's clip. Her caption quotes him: ״אני לא מפחד מהחושך!״. Check by ear that he says it |
| 9 | 0:32-0:36 | End card: the cover, logo | רוצים ספר שבו הילד שלכם הגיבור?<br>כתבו "לומי" בתגובות<br>ונשלח לכם קישור | Narrator reads it |

Book lines were read off Sapir's screen recording at phone resolution. Before the voice is made I re-check every word against the preview recording. The narrator gets the same words in full spelling (החושך), so it says them right; the screen keeps the book's spelling. Narration is about 380 characters.

Post caption (draft):

```text
סיפור לפני השינה
שבו אריאל הוא הגיבור
תודה @sapir_ivan_mugatz
רוצים ספר שבו הילד שלכם הגיבור?
כתבו "לומי" בתגובות
ונשלח לכם קישור
```

Hook, CTA and caption pass `voice_lint.py` (calibrated voice, 33 samples). The one warning is the @handle in Latin letters, which has to stay.

## Draft v1 (free)

`draft/bedtime-story-draft-v1.mp4`, 39 s, built by `draft/build_draft.py` (`timeline.json` beside it). Stand-ins, all replaced in the final: the macOS Hebrew voice (Carmit) for the narrator, frames from Sapir's edited reel for the pages (soft, a few with black side bars), the cover repeated for page 11, and Sapir's own clip with her caption and CapCut mark for the ending. It shows layout, order, text and pace.

## Look

1080x1920. White page. Logo bar 0-240 px (`shared/brand/logo_wide.png`), picture window 240-1320 (1080x1080), text panel 1320-1920 with the text kept above the bottom 280 px (Instagram buttons). Heebo, dark text, one beat per line, centred. Page-curl right to left between pages (Hebrew book direction), done in CapCut or as an ffmpeg wipe.

## Cost (estimate, nothing spent yet)

Generation, on the fal account (prices read from fal on 20 Oct 2026):

| Item | Model | Rate | Plan | Estimate |
|---|---|---|---|---|
| Narrator voice | ElevenLabs Eleven v4 (`elevenlabs/tts/eleven-v4`) | $0.08 per 1,000 characters | 2 voices tried on the hook, 1 full take, 1 retake (about 4 x 380 characters) | about $0.15 |
| Camera moves on the book pages | local ffmpeg | free | all pages | $0 |
| Optional: animate 2 pages without the monster (cover, page 5), 5 s each | test one page on Kling 2.5 Turbo Pro ($0.07/s) and MiniMax H3 Max Turbo ($0.01625/s), then the second page on the one you pick | | | $0.50 to $0.80 |

- Option A, voice + camera moves: **about $0.15**
- Option B, voice + 2 animated pages: **about $0.65 to $0.95**
- Cap I would work to, retakes included: **$1.50**

Claude usage (Max plan, no per-token bill; it counts toward the plan limits): this session so far is about 258K tokens of context, 3% of the 5-hour limit and 16% of the week (whole account). Production would be roughly 30 to 50 more tool calls, best in a fresh session that reads this file first: my estimate is another 3 to 5% of the 5-hour limit and about 1% of the week.

## Open questions for Yarin

1. Sapir's OK to post Ariel's face and voice on LumeBook's account (she sent the files, but the DM offer was a book for a video on her page). Collab post with her?
2. The four big files: drag them into `media/projects/2026-10-20-bedtime-story-reel/references/` (the connector stops at 10 MB and Drive for desktop is not installed). Even better, the book's page images from the admin, sharper than a screen recording.
3. The blue monster inside the book looks close to Sulley from Monsters, Inc. (my read), and so does the teal monster on the site's sample cover for this book (seen in Sapir's screen recording). I keep the monster pages as real pages with a camera move and do not generate new frames of it. The sample cover may be worth a look by whoever owns the catalog.
4. Voice: a warm female narrator (recommended) or Lume's voice (Higgsfield "Lume", which would start a "Lume reads" series).
