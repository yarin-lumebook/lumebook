---
name: lumebook-carousel
description: Create the nightly LumeBook Hebrew carousel review pack (six 7-slide options, kid and expert directions, no paid images), or turn one chosen option such as kid-2 or expert-1 into a fal.ai GPT Image 2.5 Flare production run with approval, visual QA and final 1080x1350 export. Use it for the scheduled lumebook-nightly-carousel task, whenever someone asks for tonight's or tomorrow's carousel options, says "produce kid-2" or "make expert-1", or asks to regenerate, QA or export a LumeBook carousel.
---

# LumeBook carousel pipeline

One pipeline, two modes. Everything lives in `carousel/carousel-pipeline/` (scripts, schema, topic bank, history, drafts, approved runs) and the README there is the operator manual.

All Hebrew a parent will read follows the **lumebook-hebrew-voice** skill. Read its `SKILL.md` before writing any copy, in both modes.

## Mode 1 · Nightly review pack (no paid calls, ever)

Goal: by the morning, `carousel/carousel-pipeline/drafts/DATE/` holds one validated pack of six complete options on one topic, plus `review.html` and `review.md` for Yarin to compare and score. Never call fal.ai or any paid tool in this mode, and never pick a winner.

Follow `references/nightly.md` step by step. In short:

1. `python3 carousel/carousel-pipeline/scripts/nightly.py start` creates the folder, backs up any earlier pack for that date into `versions/vN/`, and prints the context as JSON: review date, voice status, ranked eligible topics, blocked code words and hook families, recent hooks, and the exact path to write
2. Read `carousel/carousel-pipeline/topic-bank.md`, `docs/lumebook-product-brief.md`, the relevant sections of `docs/lumebook-instagram-carousel-playbook-he.md` (4.2, 5, 7, 8, 10, 12, 19), the format findings in `research/carousel-research/lumebook-carousel-research.html` (carousel research v2) and the voice skill
3. Pick one topic from the shortlist and say why it fits tomorrow (season, Israeli calendar, catalogue). Check the calendar claim against a source
4. Verify product facts on the live site today (`https://lumebook.com/IL/he`, the book page you will name). Record each fact with its verbatim quote in `product_facts`
5. Research the topic in primary or high trust sources (official pediatric, psychology, education or public health bodies, original research). Read each page yourself and keep a verbatim quote
6. Write `pack.json` by hand to the path from step 1 (schema: `carousel/carousel-pipeline/pack.schema.json`)
7. `python3 carousel/carousel-pipeline/scripts/nightly.py finish PATH/pack.json` validates, writes the review files and records history. If it prints errors, rewrite those exact lines (never just strip punctuation) and run finish again until it says VALID
8. Write the two daily recommendation carousels, `games-carousel.json` and `books-carousel.json` (3 real games and 3 real books for one developmental stage each, popular in Israel with Israel-specific evidence, real product images, LumeBook once on slide 6), then `nightly.py finish-reco drafts/DATE`. Rules: `carousel/carousel-pipeline/recommendations.md`, steps: `references/nightly.md` 7b. These are extra carousels: the kid and expert rules (no brand) are unchanged
9. End with the absolute path of `review.html` (and `review.md`), the topic, the games and books carousels with their status, the voice status, and the editor command: `python3 carousel/carousel-pipeline/scripts/review_server.py` (Yarin edits and saves the copy from the review page)

### The six options

- Direction `kid` (ids kid-1, kid-2, kid-3): the child tells the parents what the moment feels like from the inside and what may sit behind the behaviour. Three genuinely different angles, not three rewrites
- Direction `expert` (ids expert-1, expert-2, expert-3): a clear, useful, evidence based take on the same topic. Use `expert_frame: {"type": "evidence_based_take"}` unless a real, verifiable person said exactly what you quote (then `named_expert` with their name and the source id)
- Vary across the six: hook family (at most 2 options per family), target parent, child gender, awareness stage and code word

The two directions differ in copy, photo direction and their colour on the review page (`carousel/carousel-pipeline/pillars.md`). On the slides both use the same layout, the one from the approved fal trial carousel: centred Heebo Black on the picture's plain wall, no boxes (Yarin, 8 Oct 2026). Write camera choices that leave a plain wall or sky in the text zone.

### Who every carousel is about

One named Israeli child per option: a girl or a boy with a name from `carousel/carousel-pipeline/names.md` (`child_name`, matching `child_gender`, a different name for each option). The copy talks to mom (feminine singular: את, תגידי, כתבי) or to both parents (plural: אתם, תגידו, כתבו), set in `addressee`. Never to dad alone, and no dad without mom on the slides or in the image anchor (Yarin's rule, 7 Oct 2026). Talking to both parents may open with "אמא ואבא" (Yarin's own hook, 8 Oct 2026); the validator allows that pair only when `addressee` is parents. Use the name where a family would say it, usually in mom's quoted sentence ("״נועם אחרי המנוחה אני כאן״"). The validator blocks אבא, אתה and "בוא נ", names outside the list, a name that never appears before the last slide, and an image anchor that does not match the addressee.

### The seven slides

Yarin's brief (7 Oct 2026): give the reader real value, hook them again on every slide, touch a problem or a feeling, talk about a solution, and only at the very end suggest helping the child with a personalised story where they are the hero, then the CTA. The slides before the last one never prepare a sale, and the brand is never named.

| # | role | job |
|---|---|---|
| 1 | hook | built from a formula in `carousel/carousel-pipeline/hook-bank.md` and scored with its hook formula (9+ of 12, no zero). Main line up to 8 words, slide up to 12 |
| 2 | second_hook | a second hook that works on its own (Instagram may resurface the carousel from slide 2) and touches the feeling. Use a move from the bank's slide 2 table |
| 3 | recognition or reframe | what may sit behind the feeling or behaviour. Kid: the need in the child's words. Expert: one sourced idea in plain words |
| 4 and 5 | solution | two concrete things to try, each real value on its own. At least one mapped to a source (expert: both) |
| 6 | resolution | the story closes: the pickup, the promise kept, or a short recap. No book, story offer, link or comments talk (the validator blocks ספר שבו, סיפור אישי, גיבור, קישור, תגובות here) |
| 7 | story_cta | one short line that suggests helping the child with a personalised story (must say סיפור and אישי), then the CTA. Never LumeBook (לומבוק) or a book title. Up to 18 words in total |

**Hook bank and hook slate.** Before writing, read `carousel/carousel-pipeline/hook-bank.md` (formula cards, evidence labels, rotation rules). Then build the private hook slate first (`hook_slate` in pack.json, schema_version 3): 6 kid and 6 expert candidates for tonight's topic, six different formulas per direction across at least 3 families and 3 mechanisms, each with slide 1 text, a slide 2 that works as a first slide on its own, the open question, the payoff slide and how it closes, `factual_claim`, a 0 to 2 score on the ten slate criteria and the four fail checks. Never use a candidate that fails; never use a formula listed in `blocked_expired_formulas`. Build the six options from passing candidates, choosing for difference (4+ mechanisms, 4+ sentence shapes, 3+ slide 2 moves, 2+ awareness stages), not for the top scores, and never rank or recommend a winner. Each option records `hook: {formula, gap, payoff_slide, score, slate_id, mechanism, slide2_move}`; `gap` is the question the hook opens and `payoff_slide` (3 to 6) is where the carousel answers it. Prefer formulas not in `recent_hook_formulas_rotate_away_from`, but never force a weaker hook just to rotate. A hook that states a fact about children needs a sourced_fact claim on slide 1 or 2. Be honest in both scores; a weak hook gets rewritten, not re-scored. Everything in the bank is a LumeBook hypothesis until `hook-results.json` says otherwise; never describe a hook as proven.

**Pull on every slide.** Each of slides 1 to 6 ends with a reason to swipe, recorded as `pull` (`question`, `open_loop`, `next_step`, `contrast` or `numbered`, plus a short note). Good pulls: a question answered on the next slide, a line that sets up the next headline, "דבר ראשון / דבר שני", "ועוד משהו קטן לפני שאת הולכת". Never a sentence cut in the middle.

Headlines alone must tell the story. Up to 25 words on a regular slide, 18 on the last slide. A headline line over 30 characters or a body line over 42 characters will not fit the slide at a readable size, so break it.

### CTA and caption

- CTA idea, fixed by the brief, in the option's addressee: to both parents `כתבו "X" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור`, to mom `כתבי "X" בתגובות וקבלי קישור ליצירת ספר שבו הילד שלך הוא הגיבור` (girl: הילדה ... היא הגיבורה). X is one short topic specific Hebrew code word, not used in the last 14 days (never ספר)
- The code word always sits inside straight quotation marks right after the verb: כתבו "גן" בתגובות (Yarin, 8 Oct 2026). The validator rejects a bare code word
- The CTA text appears on slide 7 and, word for word, as the caption's last line. No second CTA anywhere (no link in bio, save, share, follow, tag)
- Never say or hint that anything is made with AI: no label on slides, nothing in the caption, alt text or comments (Yarin, 8 Oct 2026: it ruins trust and engagement). The validator rejects AI, בינה מלאכותית and "נוצר בעזרת"
- No brand and no book title anywhere a parent reads (slides, caption, CTA). The comment link does the selling; the validator rejects לומבוק, LumeBook and catalogue titles
- Caption: line 1 restates the hook in other words, then 2 to 4 short value lines, then one bridge line, then the CTA. 5 to 8 lines, no em dash, period or comma

### Claims and sources

Every factual statement goes into `claims` with its slide, the Hebrew wording, its kind and what the source supports:

- `sourced_fact`: cites ids from this option's `sources` (title, publisher, url, date read, verbatim quote, what it supports)
- `product_fact`: cites `site-...` ids from `product_facts` (checked on the live site in this run)
- `lumebook_wording`: our own phrasing, such as an imagined child line; say what it rests on

If a source is about a related situation (an illness absence, a return after lockdown), say so in `supports`. Do not stretch a source to cover more than it says.

### Image briefs

Each slide has an English `image` brief: beat, action, setting, camera, lighting, wardrobe and objects, and a text zone (edge top or bottom, 30 to 50 percent, and what the empty surface is). Each option has one `character_anchor` (child with age, parent, wardrobe) used on the reference and all seven slides. `carousel_lib.compose_image_prompt()` adds the anchor, the feature-film 3D animated style (never photo-real, Yarin 8 Oct 2026), the cream plum violet and muted gold palette, the reserved typography zone and the no-text rule, so the review page shows the exact prompt the model would get. Read `references/image-briefs.md` before writing them.

## Mode 2 · Production run (paid, standing approval up to $0.50 per carousel)

Trigger: Yarin names one option, for example "produce kid-2 from tomorrow's pack". Follow `references/production.md`. In short:

1. `python3 carousel/carousel-pipeline/scripts/prepare_fal_jobs.py PATH/pack.json kid-2` freezes the copy and briefs into `carousel/carousel-pipeline/approved/DATE-kid-2/`, writes valid jobs for `openai/gpt-image-2.5/flare/text-to-image` (reference) and `openai/gpt-image-2.5/flare/edit` (7 slides) at 1024 x 1280, quality high, and makes no network calls
2. Naming the option is approval to spend up to $0.50 on it (Yarin, 8 Oct 2026); more always needs a new yes. Run with `--max-usd 0.5`
3. Generate the reference, QA it yourself and go straight on (no stop), then all seven slides in parallel, QA each, replace only failures that fit under the cap
4. `compose_slides.py` overlays the Hebrew in HTML and CSS (no logo and no product card by default, because the carousel never names the brand), exports 1080 x 1350 PNGs, the contact sheet, the RTL check and the ZIP. View the contact sheet and the RTL check yourself before reporting
5. One review message with the contact sheet, the ZIP, the spend and every open problem. Later text changes: `scripts/edit_final.py` (about 10 seconds, no images)

FAL_KEY stays in the environment (it is in `~/.zshrc`, so run the generator through `zsh -ic`). Never print it, write it to a file or put it in a log.

## Editing from the review page

`python3 carousel/carousel-pipeline/scripts/review_server.py` serves the newest pack at http://localhost:8777 (also the `carousel-review-editor` preview config). Yarin clicks any headline, body line, caption, CTA or title and types; Enter adds a line; "שמירה" or Cmd+S saves. The server copies the old files to `versions/vN/`, applies the edits (a CTA edit also updates the last slide, the caption's last line and the code word), validates with the same rules, saves even if something fails so nothing typed is lost, rebuilds the review, and the page highlights each field that still breaks a rule. When Yarin later says "produce kid-2", `prepare_fal_jobs.py` freezes the edited copy.
