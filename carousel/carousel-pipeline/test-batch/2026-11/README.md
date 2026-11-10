# Test batch, 11 to 30 Nov 2026

Yarin, 10 Nov 2026: "lets do them all, everyday in addition to what we have, build it all and add it to the carousel machine as a test batch section, give me different options for each day, you can use media from google drive, if you need to generate images for a carousel just add a budget (lowest possible) and if i decide to produce it gives you permission for that specific carousel". On the times: "try an evening hour on one of the new days and compare" and "we can upload in the evening".

A second kind of carousel every day, next to the child-voice carousels (Mon, Wed, Fri 06:00, already in Postiz until 30 / 11). Five types, four days each, two options a day (`a`, `b`). Carousel Machine shows them under **סבב ניסוי** in its sidebar (or `/?batch=test-2026-11`). Code: `scripts/test_batch.py` (format, checks, slides, budget, production).

## The days (plan.json)

| type | days | what it is |
|---|---|---|
| `say` במקום זה, תגידו את זה | 11, 16, 21, 26 | a sentence parents say and a better one to try; parent voice; no brand |
| `how` ככה זה עובד | 12, 17, 25, 28 | the questions before ordering; store screens and a real child's book; LumeBook named |
| `gift` מתנה לחנוכה | 13, 18, 22, 27 | for grandparents and gift givers; real covers; last Hanukkah order day 05 / 12 |
| `age` מה קורה בגיל | 14, 19, 23, 29 | age-stage cheat sheet, every point on a source (age-sources.md); no brand |
| `reveal` הרגע שהם רואים את הספר | 15, 20, 24, 30 | real children with their books (creator footage); LumeBook named |

Times: Mon, Wed and Fri go out at 20:30 (06:00 is the child-voice carousel); Sun and Thu at 06:00; Tue and Sat at 20:30. 20:30 is an assumption, not a measured best hour. Each type lands on both morning and evening days, so the comparison is type against type and morning against evening.

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

6 to 10 slides (Postiz sends at most 10). Slide 1 is `cover`, the last is `cta`.

| layout | fields | notes |
|---|---|---|
| `cover` | `tag`, `big`, `headline`, `body`, and one of `photo` / `picture` / `covers` / `no`+`yes` | up to 22 words; `big` is a giant word or number (the age); `no`+`yes` draws a preview swap |
| `swap` | `num`, `label`, `no`, `yes`, `why` | the say type; `num` 1 to 9 draws the number disc |
| `point` | `num`, `label`, `headline`, `body`, optional `photo` / `picture` | |
| `photo` | `photo` or `picture`, `label`, `headline`, `body` | the picture on top |
| `covers` | `covers` (asset keys, 1 to 4), `label`, `headline`, `body` | book covers, tilted |
| `quote` | `quote`, `by`, `body`, optional `photo` | only real words someone said; never invented testimonials |
| `cta` | `headline`, `body`, `cover` (a book cover key) or `photo` | the body ends with the CTA's last line |

`**word**` paints a word in the type's accent colour. A new line in a field is a line break on the slide. Up to 48 words on a slide, 12 words on a line.

`photo`, `covers` and `cover` take keys from `assets.json` (real pictures only). `picture` takes a key from the carousel's own `pictures`: a picture made with the OpenAI Images API at the lowest quality when Yarin produces the carousel. Each one adds about $0.011 to the estimate; `test_batch.py budget` lists them.

## Rules (`test_batch.py lint` checks most)

- Hebrew voice: `.claude/skills/lumebook-hebrew-voice/SKILL.md` and `creators/creator-research/src/hebrew-rules.md`. Punctuation yes, but no dash of any kind, no semicolon, no maqaf. No em dash anywhere.
- To mom or both parents (plural), never dad alone. Yarin is not a parent: never הילד שלי in LumeBook's voice.
- Never mention AI. Never a price, discount, sale or delivery cost. Never language options or the digital copy. Never קוד הנחה or קוד אישי.
- `say` and `age` name no brand on the slides; their CTA is the book link (`אפשר גם לעזור להם עם X בעזרת ספר מותאם אישית.` then `תכתבו "WORD" ואשלח לכם קישור להכנת הספר`) over the real cover of a best-selling book that covers X. The medical disclaimer is drawn at the foot of slides 2 onward.
- `how`, `gift` and `reveal` may say לומבוק. Product facts only from `shared/facts.json`, the live site, or `docs/lumebook-product-brief.md` (read 01 / 10 / 2026, re-check before quoting). No invented reviews or quotes.
- Comment word: one short Hebrew word, never ספר (MeBook uses it).
- Facebook: its own text, ends with a line like `להכנת הספר 👇`; the export adds the site link with the UTM.
- Every written caption gets the short disclaimer at export (31 Oct 2026 rule).

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

`assets.json` lists every real picture. From the Drive שיווק folder: frames of sapir_ivan_mugatz's footage (Ariel and his book באנו חושך לגרש, and her screen recording of the store's preview) and of ellinore.speech's birthday book (עומר בת שנתיים). Files in `media/projects/2026-11-10-test-carousel-batch/`; the store covers in `media/projects/2026-11-10-store-covers/`. Check with each creator that a carousel may use her footage before posting. The Drive folder `חומרי גלם/UGC Images` holds made-up "customers" and is not used.
