# Test batch, 11 to 30 Nov 2026

Yarin, 10 Nov 2026: "lets do them all, everyday in addition to what we have, build it all and add it to the carousel machine as a test batch section, give me different options for each day, you can use media from google drive, if you need to generate images for a carousel just add a budget (lowest possible) and if i decide to produce it gives you permission for that specific carousel". On the times: "try an evening hour on one of the new days and compare" and "we can upload in the evening".

A second kind of carousel every day, next to the child-voice carousels (Mon, Wed, Fri 06:00, already in Postiz until 30 / 11). Five types, four days each, two options a day (`a`, `b`). Carousel Machine shows them under **סבב ניסוי** in its sidebar (or `/?batch=test-2026-11`). Code: `scripts/test_batch.py` (format, checks, slides, budget, production).

## Rewritten on 11 Nov 2026

Yarin, 11 Nov 2026: "dont use only sapirs kid in the carousels, utilize all of the media we have", "i need the media to fill most of the bg", "some of them dont sound natural, maybe use the voice of previously analyzed creators", "talk to moms and grandmothers".

- **Every slide has a real picture filling the background** (`bg`, a key from `assets.json`), with the words in white on a dark fade at the bottom, the top, or over the whole slide (`text_at`: `bottom`, `top`, `full`). Pick the side that keeps the faces clear.
- **95 pictures from 11 sources** in `assets.json`: the five creators' clips on the Mac (Koral, Mor Keisar, Moran Arges, Natali Fridman, Nofit Hazut, stills cut clear of their burned-in captions), Sapir's Ariel, Omer's birthday book, the grandma baking book close-ups, 31 photos from Drive's חומרי גלם folder (children reading, the BookPod bag, piles and rows of printed books, the back cover, the dedication page), store screens and covers. Use many of them: never the same picture twice in one carousel, at most 3 slides of one family per carousel.
- **One mom or one grandmother** (`addressee`: `mom` or `grandma`): feminine singular all through (את, תכתבי, לך), never the plural. Option a talks to mom and option b to grandma, except the gift days (a grandma, b mom).
- **The voice of the creators we analyzed** (`research/israeli-product-reels/ugc-seller-scripts.md`, `.claude/skills/lumebook-hebrew-voice/references/reel-scripts.md`, and the creators' own recorded words in `media/projects/2026-10-24-grandma-baking-book-reel/moms/*-words.json`): one person in one moment, a problem or a doubt first and then the turn, one rough edge (בתכלס, בקיצור, תקשיבי), count when explaining, plain spoken words, the person and the moment as the subject (never the brand or the book). Short: up to 18 words on a cover, 36 on a slide.
- **Real quotes only**: a `quote` slide takes `quote_from` (`nofit_hazut`, `natali_fridman`, `moran_arges`) and the lint checks the words are in her recording, in order.

## The days (plan.json)

| type | days | what it is |
|---|---|---|
| `say` במקום זה, תגידו את זה | 11, 16, 21, 26 | a sentence parents say and a better one to try; parent voice; no brand |
| `how` ככה זה עובד | 12, 17, 25, 28 | the questions before ordering; store screens and a real child's book; LumeBook named |
| `gift` מתנה לחנוכה | 13, 18, 22, 27 | for grandparents and gift givers; real covers; last Hanukkah order day 05 / 12 |
| `age` מה קורה בגיל | 14, 19, 23, 29 | age-stage cheat sheet, every point on a source (age-sources.md); no brand |
| `reveal` הרגע שהם רואים את הספר | 15, 20, 24, 30 | real children with their books (creator footage); LumeBook named |

Times (retimed 11 Nov 2026, Yarin: 4 posting hours a day from the follower activity charts; the single source is `sites/content-calendar/posting-hours.json` `plan`, `plan.json` follows it): Sun to Thu 09:30, Friday 09:00, Saturday 15:30. The child-voice carousel goes out the same day in the evening peak (18:30; Friday 15:00, Saturday 21:30), so the day holds two carousels and two reels at least 3 hours apart. The earlier plan (06:00 and 20:30, morning against evening) rested on assumptions; the charts show 06:00 to 09:00 at 60 to 70% of a day's peak, so the comparison is dropped.

## A carousel file (carousels/DATE-OPT.json)

```json
{
  "id": "2026-11-11-a", "date": "2026-11-11", "option": "a", "type": "say",
  "title": "internal title, Hebrew", "angle_he": "the angle in a few words", "topic_id": "topic-bank id or empty",
  "comment_word": "תור", "emoji": "🧸",
  "slides": [ { "layout": "cover", ... }, ..., { "layout": "cta", ... } ],
  "caption": "...ends with the CTA, word for word",
  "cta": "two lines: what the book helps with, then תכתבו \"WORD\" ואשלח לכם קישור ...",
  "fb_text": "Facebook's own text, no comment word, no link (the export adds the site link)",
  "sources": [ {"title": "", "publisher": "", "url": "", "accessed": "2026-11-10", "supports": "what it backs"} ],
  "pictures": { "pic-1": {"scene": "English scene for a 3D animated picture, 40+ chars", "purpose": "Hebrew, what it shows"} }
}
```

6 to 10 slides (Postiz sends at most 10). Slide 1 is `cover`, the last is `cta`. Every slide: `bg` (picture key), optional `text_at` and `pos` (CSS object-position, to move the picture).

| layout | fields | notes |
|---|---|---|
| `cover` | `tag`, `big`, `headline`, `body`, optional `no`+`yes` | up to 18 words; `big` is a giant word or number (the age); `no`+`yes` draws a preview swap |
| `swap` | `num`, `label`, `no`, `yes`, `why` | the say type; `num` 1 to 9 draws the number disc |
| `point` | `num`, `label`, `headline`, `body` | |
| `photo` | `label`, `headline`, `body` | the same as point, for a slide that is mostly picture |
| `covers` | `covers` (asset keys, 1 to 4), `label`, `headline`, `body` | book covers, tilted |
| `quote` | `quote`, `quote_from`, `by`, `body` | only a creator's recorded words (checked) |
| `cta` | `headline`, `body`, `cover` (a book cover key) or `photo` | the body ends with the CTA's last line |

`**word**` paints a word in the type's accent colour. A new line in a field is a line break on the slide. Up to 48 words on a slide, 12 words on a line.

`photo`, `covers` and `cover` take keys from `assets.json` (real pictures only). `picture` takes a key from the carousel's own `pictures`: a picture made with the OpenAI Images API at the lowest quality when Yarin produces the carousel. Each one adds about $0.011 to the estimate; `test_batch.py budget` lists them.

## Rules (`test_batch.py lint` checks most)

- Hebrew voice: `.claude/skills/lumebook-hebrew-voice/SKILL.md` and `creators/creator-research/src/hebrew-rules.md`. Punctuation yes, but no dash of any kind, no semicolon, no maqaf. No em dash anywhere.
- To mom or both parents (plural), never dad alone. Yarin is not a parent: never הילד שלי in LumeBook's voice.
- Never mention AI. Never a price, discount, sale or delivery cost. Never language options or the digital copy. Never קוד הנחה or קוד אישי.
- `say` and `age` name no brand on the slides; their CTA is the book link (`אפשר גם לעזור להם עם X בעזרת ספר מותאם אישית.` then `תכתבו "WORD" ואשלח לכם קישור להכנת הספר`) over the real cover of a best-selling book that covers X. No disclaimer on the slides (see "Design rules of 11 Nov" below).
- `how`, `gift` and `reveal` may say לומיבוק. Product facts only from `shared/facts.json`, the live site, or `docs/lumebook-product-brief.md` (read 01 / 10 / 2026, re-check before quoting). No invented reviews or quotes.
- Comment word: one short Hebrew word, never ספר (MeBook uses it).
- Facebook: its own text, ends with a line like `להכנת הספר 👇`; the export adds the site link with the UTM.
- Every written caption gets the short disclaimer at export (31 Oct 2026 rule).

## Design rules of 11 Nov 2026 (Yarin, all test carousels; in the renderer since the evening of 11 Nov; recreated under them so far, one per type: 2026-11-11-a say, 2026-11-12-a how, 2026-11-13-a gift, 2026-11-14-a age, 2026-11-15-a reveal, all real pictures, $0 except the 14-a pictures already approved; the other 35 still use the old look)

1. No separate tag chip (like "מה קורה בגיל") on the cover: its words go into the headline.
2. The hook is the big text: on `age` that is "5 דברים ..." (the number and the claim), larger than the rest of the headline, not just the giant age.
3. No disclaimer drawn on any slide. It lives in the post caption only (IG and FB).
4. The arrow icon sits in the middle of the slide foot, not at the left corner.
5. Last slide (CTA): much bigger text, and the book is an OPEN LumeBook book, not a closed flat cover: the real dedication page on the right (the one-book-in-the-world line, the child's round photo, the logo), an illustration page on the left (`spread_art`, `spread_photo`; the page can be a picture made for this carousel so it fits the topic), tilted on a cover board with page edges and a shadow (11 Nov 2026).

## Commands

```bash
python3 carousel/carousel-pipeline/scripts/test_batch.py status
python3 carousel/carousel-pipeline/scripts/test_batch.py lint 2026-11-11-a
python3 carousel/carousel-pipeline/scripts/test_batch.py render 2026-11-11-a
python3 carousel/carousel-pipeline/scripts/test_batch.py budget
```

## Producing

In Carousel Machine, "להפיק עכשיו" on a test carousel: with no picture to make it renders the final slides, the texts and the ZIP at once (no cost). With pictures, the button shows the budget (the estimate rounded up to the cent); pressing it is Yarin's permission for that carousel and that budget only, and `openai_generate.py --max-usd` refuses anything past it. Then the same Postiz box as every carousel, starting on the day's time. Runs live in `runs/DATE-OPT/`.

## Pictures from Drive

`assets.json` lists every real picture. From the Drive שיווק folder: frames of sapir_ivan_mugatz's footage (Ariel and his book באנו חושך לגרש, and her screen recording of the store's preview) and of ellinore.speech's birthday book (עומר בת שנתיים). Files in `media/projects/2026-11-10-test-carousel-batch/`; the store covers in `media/projects/2026-11-10-store-covers/`. Approved for use: Yarin, 11 Nov 2026, "we have their approval, use it freely" (every creator and the Drive families). The Drive folder `חומרי גלם/UGC Images` holds made-up "customers" and is not used.

In the renderer: a cover with `big` draws `headline` as the small context line and `big` as the hook; `tag` is no longer drawn (lint WARN, still in the other carousels until each is recreated); the CTA's `cover` is a 3D book (`_book3d`).

6. A background says what the slide says (Yarin, 11 Nov 2026): pick the picture by the slide's words, never by what is left. When no real picture fits, list a made one under `pictures` and ask Yarin for a budget (`budget()`; picture proposals wait in `picture-proposals/DATE-OPT.json` until he says yes).
7. Media names say what you see (11 Nov 2026): asset keys and files are `who-what-where` in English, no person's name (`sapir-boy5-holds-own-book-laughing`); the raw Drive downloads in `media/projects/2026-11-10-test-carousel-batch/drive/` were renamed too, old names in its `NAMES.md`. `assets.json` keeps `old_key`. Store covers keep their store file names (B43_boy.webp) but their keys are `cover-b43-eden-and-free-animals-boy`.

8. Real pictures keep the child's face clear (Yarin, 11 Nov 2026): pick `text_at` so the headline, number disc and fade sit on the other half; if the face fills the frame, choose another picture. The cover is always a real picture (a made one only on later slides). A CTA over a photo with faces in it uses a no-face real picture instead (covers on marble, a stack of books).
9. Today and one day (Yarin, 11 Nov 2026, from `research/adar-motherhood/report.md:116`): a new test carousel may pair a small child's line "היום" with the same child grown, "יום אחד" (the grown child's voice is allowed on test carousels; the child-narrator age limit of the child-voice carousels does not apply here). Send-to-dad is NOT approved: Yarin has only asked for an example (11 Nov 2026); `lint` still fails אבא alone.
10. The recurring child in made pictures is described in words, not from a photo (Yarin, 11 Nov 2026): `character` in the carousel file is put in front of every made picture's prompt (round face, curly auburn-brown hair, big dark eyes, striped knit sweater for 2026-11-14-a). No photo of a child is sent to the image API.
11. Rewrite from the Adar report (`research/adar-motherhood/report.md`, one account, hypotheses to test): open with a line a person says in a real moment, quote it, pay it off across the slides, caption in short lines with a rhetorical question and its answer, one ask matched to the job.
12. No child names at all (Yarin, 11 Nov 2026): say the friend, her, the grandchildren; `lint` fails a list of common names.
13. The same kid or kids on every slide of a carousel: one real family from the footage, or made pictures with `character` (budget first); a made picture can also be `spread_photo`. Made so far: 2026-11-11-a (8, $0.0548) and 2026-11-13-a (4, $0.0270).
14. No brand word in the slide corner, no pills or cards: the swap slide is plain red text (instead) and plain green text (try), labels are plain text.
15. Swap slide: white text, red X and green V icons. 16. Creator credit in the caption and Facebook text only. 17. Toys and games in general, no specific game. 18. Hooks are her own thought, slides explain without "you need to". 19. The line that names her (סבתא, אמא) is the big cover line. 20. Never פרצוף, say פנים.
