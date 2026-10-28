# Nightly review mode, step by step

> **Since 24 Oct 2026 (Yarin, after the carousel audit):** a pack holds two topics of two best-selling books and six child-voice options, kid-1 to kid-3 on topics[0] and kid-4 to kid-6 on topics[1], one `kid` direction, hook slate keys `a` and `b`, and since the evening of 24 Oct slide 10 is only the save for later CTA (`תשמרי את הפוסט` as the headline, `לפעם הבאה ש...` as the body; no story line, no `code_word`) and punctuation is back except dashes, semicolons and hyphens. The skill's section "Two topics a day" and the top block of `carousel/carousel-pipeline/cloud-nightly-prompt.md` have the rules; `nightly.py start` prints `pack_shape` and `cta_forms`; a complete passing pack is `carousel/carousel-pipeline/tests/fixtures/two_topic_pack.json`. The JSON skeleton below is the older shape: for a two-topic pack add `format` and `topics`, write one kid direction with six versions (each with `topic_id`), slate keys a and b, and drop `code_word` and `expert_frame`.


Project folder: `/Users/yarinbruner/Claude/Projects/Lumebook`. Use absolute paths in commands so the run works from any working directory.

## 0 · Guard rails

- No fal.ai calls, no paid tools, no publishing, no messages. This mode only reads, researches and writes files under `carousel/carousel-pipeline/drafts/` and `carousel/carousel-pipeline/history.json`
- Never overwrite a pack by hand. `nightly.py start` moves an existing pack for the same date to `versions/vN/` first
- Do not select a winner. Do not edit `voice-profile.md` or the example folders
- Never name LumeBook (לומבוק, LumeBook) or a catalogue book title in anything a parent reads. The last slide only hints that a book where the child is the hero can help; the comment link leads to the product

## 1 · Start

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/nightly.py start
```

Keep the printed JSON: `date`, `generated_at`, `write_pack_to`, `voice`, `voice_note_suggestion`, `topic_shortlist`, `blocked_code_words`, `blocked_hook_families`, `hook_family_use_last_7_days`, `recent_hooks_do_not_repeat`. For the hook slate also keep: `hook_bank` (each formula with evidence, mechanisms, shape, slide 2 moves and status), `blocked_expired_formulas`, `recent_hook_formulas_rotate_away_from`, `published_formulas_last_14_days`, `recent_mechanisms`, `recent_shapes`, `recent_slide2_moves`, `recent_awareness_stages`, `recent_slide2_hooks_do_not_repeat` and `hook_slate_rules`.

## 2 · Read

- `.claude/skills/lumebook-hebrew-voice/SKILL.md` and its `references/fallback-voice.md` (or the approved examples when calibrated)
- Yarin's recent edits: `recent_voice_edits_learn_from_these` in the start JSON (before and after of each line Yarin changed on the review page). Read every pair and write tonight's copy the way the "after" lines sound
- `carousel/carousel-pipeline/topic-bank.md`
- `docs/lumebook-product-brief.md`
- Playbook `docs/lumebook-instagram-carousel-playbook-he.md`: sections 4.2 (what we may claim about the book), 5 (anatomy), 7 (hook families), 8 (copy rules), 10 (bridge to product), 12 (CTA). Section 19 has worked concepts per topic. Where the playbook says to write לומבוק or the exact book title on the product slide (8.2, 10.4, section 19 concepts), Yarin's later rule wins: no brand, no title, only the hint that a story where the child is the hero is one option
- Carousel research v2, "Niche Carousel Teardown" (`research/carousel-research/lumebook-carousel-research.html`, published as https://claude.ai/artifact/B2YkxMHGTeM5T5LLC2wnYU): use it for format ideas when making the three options in a direction genuinely different. What it found in Israeli parenting accounts (6 Oct 2026, engagement signals, not sales data): comment-word carousels pull far more comments than the account's norm; letters told over one repeated photo and "life through the ages" stories get reach and shares; "instead of X, say Y" with illustrated characters and short how-to lists get leads; a story offered as the reward (saraigatt's "לב הקשת") drew more comments than likes. Never use ספר as a code word (MeBook creators use it); the validator blocks it
- The last three `carousel/carousel-pipeline/drafts/*/pack.json` files, if any, to avoid similar angles

## 3 · Topic

Take the first eligible topic unless a later one fits tomorrow clearly better (a holiday, school calendar event or catalogue launch). Write `topic.reason` in Hebrew for Yarin: why tomorrow, and anything sensitive about the date. Any calendar fact in the reason needs a source you read (for Israeli school dates: the Ministry of Education vacation notices).

## 4 · Product facts (live site, today)

The carousel names no brand and no book, but the personalised story suggested on the last slide must still be true. Read `https://lumebook.com/IL/he` (and, to check that a fitting book exists for the topic, `https://lumebook.com/IL/he/books`; story text at `https://lumebook.com/api/book/ID`). For each fact behind the last slide, add to `product_facts`:

```json
{"id": "site-preview", "fact": "what it means", "quote": "verbatim Hebrew from the page", "url": "https://lumebook.com/...", "checked_at": "YYYY-MM-DD"}
```

Safe defaults verified on 2026-10-07 (re-check, they change): free creation and preview, pay only if you love it; the child's name in the text and the child in every illustration; upload a photo and add the name. Do not use prices, payment talk, "limited time", review counts or ratings. Mention a fitting catalogue book only in internal fields (angle, rationale), for the DM link.

## 5 · Research

For each sourced idea: open the page, read it, copy a verbatim quote, note the publisher and update date. Raising Children Network blocks scripted fetching; read it in the in-app browser if needed. If you cannot read a page, do not cite it. Prefer: AAP HealthyChildren.org, Raising Children Network, Zero To Three, Child Mind Institute, NHS, CDC, Nemours KidsHealth, peer reviewed papers.

## 5b · Hook slate (before any slide is written)

This is the step that gets the most time. Carousel Machine order (SKILL.md "What comes first"): the hook, then the content, then the slide design. For every candidate write three wordings from calm to loud and keep the loudest that is still true; start from the "Loud formulas" in the hook bank when the topic allows.

Read `carousel/carousel-pipeline/hook-bank.md`: the formula cards, the slate scoring table and the rotation rules. Then write 12 candidates into `hook_slate` (a worked example: `carousel/carousel-pipeline/tests/fixtures/sample_slate_gan_separation.json`):

```json
"hook_slate": {
  "kid": [{"id": "k1", "formula": "child-not-because", "family": "child_pov",
           "hook": "slide 1 Hebrew, lines split by \n", "slide2": "slide 2 Hebrew that works as a first slide",
           "slide2_move": "name_trigger", "mechanism": "perspective_shift", "awareness_stage": "problem_aware",
           "gap": "the exact question it opens", "payoff_slide": 3, "answer": "how that slide closes it",
           "factual_claim": true,
           "score": {"stopping_power": 2, "specificity": 2, "parent_relevance": 2, "honest_curiosity": 2, "emotional_truth": 2,
                     "swipe_promise": 2, "usefulness": 1, "topic_fit": 2, "lumebook_fit": 2, "freshness": 2},
           "fail_checks": {"clickbait": false, "unsupported_claim": false, "unfulfilled_promise": false, "blames_parent": false},
           "used_by": "kid-1", "note": "optional, internal"}, ... 6 in total],
  "expert": [... 6 candidates e1 to e6 ...]
}
```

- Six different formulas per direction, at least 3 families (at most 2 candidates per family) and 3 mechanisms. Skip formulas in `blocked_expired_formulas`
- Every candidate's Hebrew follows the same rules as the slides (no dash, semicolon or hyphen since the evening of 24 Oct 2026, no comma or period before it; hook main line up to 8 words, 12 in total; never dad; no sale words). Slide 2 never opens with a word that leans on slide 1 (אבל, ואז, כי, גם, זה, ככה...)
- Score honestly. A candidate fails with any fail check true, a 0 on honest_curiosity, emotional_truth, topic_fit or lumebook_fit, or a total under 14 of 20. Failed candidates stay in the slate, unused
- Mark exactly one candidate per option in `used_by`, choosing three different ones per direction for difference: across the six, 4+ mechanisms (2+ per direction), 4+ sentence shapes, 3+ slide 2 moves, 2+ awareness stages, and no two openings that share most of their words
- Slide 1 is the thumbnail (Yarin, 10 Oct 2026; hook-bank.md "Slide 1 is the thumbnail"): write every candidate's slide 1 as the biggest honest gap the topic allows (a tease may open it, but the cover says what the viewer gets: a number of things, a sentence to say, a result or an answer; value first, Yarin 11 Oct 2026; no soft words). An option may only use a candidate that scores 2 on `stopping_power`, `honest_curiosity`, `swipe_promise` and `usefulness`. The slide 1 image brief of every option shows the child facing the viewer, looking into the camera, with one named exaggerated expression, in a close shot (image-briefs.md "Slide 1 is the cover")
- Take the loudest passing candidates first and swap only as far as the difference rules need
- Then write the six options from those candidates. Slide 1 and slide 2 of each option start from the candidate's text (polishing is fine; the validator only warns if slide 1 drifts)
- Never rank, recommend or describe a winner anywhere, including the final message

## 6 · Write pack.json

Top level:

```json
{
  "schema_version": 3,
  "date": "<date from start>",
  "generated_at": "<generated_at from start>",
  "topic": {"id": "...", "title_he": "...", "reason": "..."},
  "voice": {"status": "<voice.status>", "approved_samples": <voice.approved_samples>, "note": "<Hebrew note, say fallback plainly>"},
  "product_facts": [...],
  "hook_slate": {"kid": [<k1 to k6>], "expert": [<e1 to e6>]},
  "directions": [
    {"id": "kid", "label_he": "הילד מספר להורים", "versions": [<kid-1>, <kid-2>, <kid-3>]},
    {"id": "expert", "label_he": "גישה מקצועית מבוססת מקורות", "versions": [<expert-1>, <expert-2>, <expert-3>]}
  ]
}
```

Each version:

```json
{
  "id": "kid-1", "title": "Hebrew working title",
  "angle": "Hebrew, internal", "target_parent": "Hebrew, internal",
  "awareness_stage": "unaware|problem_aware|solution_aware|product_aware|most_aware",
  "hook_family": "<one of the families printed by start>", "code_word": "לומי", "child_gender": "boy|girl (child_gender_per_option from start: 3 and 3 since 24 Oct 2026)",
  "character_anchor": {"child": "English, with age", "parent": "English", "wardrobe": "English"},
  "expert_frame": {"type": "evidence_based_take"},
  "examples_target": 6,
  "image": {"beat": "", "action": "", "setting": "", "camera": "", "lighting": "", "wardrobe_objects": "",
            "text_zone": {"edge": "top", "percent": 45, "surface": "plain warm cream wall"}},
  "slides": [{"number": 1, "role": "hook", "headline": "Hebrew", "body": "Hebrew lines or empty", "highlight": "1 to 3 whole words of the headline",
              "pull": {"type": "question|open_loop|next_step|contrast|numbered", "note": "what makes them swipe to slide 2"}},
             {"number": 3, "role": "example", "headline": "1 לחכות שאירגע", "body": "...", "highlight": "לחכות שאירגע",
              "examples": ["לחכות שאירגע"], "pull": {"type": "numbered", "note": "..."}}],
  "caption": "5 to 8 lines, last line = cta",
  "post_text": {"caption": "the caption, punctuated, one emoji ending the hook line, 🔖 ending the CTA", "fb_text": "slides 2 to 10 as written text, punctuated, the same emojis"},
  "cta": "כתבו לב בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור",
  "sources": [{"id": "src-aap", "title": "", "publisher": "", "url": "", "accessed": "YYYY-MM-DD", "quote": "verbatim", "supports": ""}],
  "claims": [{"slide": 5, "wording_he": "", "kind": "sourced_fact|product_fact|lumebook_wording", "source_ids": [], "supports": ""}],
  "conversion_rationale": "Hebrew, why this version may convert"
}
```

Roles in order (10 slides, packs from 2026-10-14 10:00; Yarin, 14 Oct 2026): hook, explain, example x6 (slides 3 to 8), recap, story_cta. Slide 2 explains the idea (what sits behind it and why the examples work) and still stops someone who lands there first. Slides 3 to 8 each carry `"examples": [...]` with 1 or 2 items, numbered 1, 2, 3... across the carousel, the digit right before each example on the slide ("1 חיבוק של 3 שניות"); the total equals `examples_target` (6 to 9, from `examples_per_option`) and the cover's number matches it. Slide 9 recaps: the examples in a few words and the idea they share, no new example. Older packs had 7 slides: hook, second_hook, recognition or reframe, solution, solution, resolution, story_cta.

One picture per option: put ONE `image` brief on the option (not on the slides). It depicts the carousel's idea, is shown behind all ten slides, and is also the cover, so it follows the slide 1 cover rules in `image-briefs.md` (child faces the viewer, exaggerated expression). Its `text_zone` must stay empty enough for every slide's text.

Slides 1 to 9 each need a `pull`; slide 10 has none. Write each pull `note` in short Hebrew (it is shown to Yarin under the slide), for example "השאלה נענית בשקופית 3". Each version also needs `hook` right after `hook_family`: `{"formula": "<id from hook-bank.md>", "gap": "the question the hook opens", "payoff_slide": 2-9, "score": {"specific": 0-2, "feeling": 0-2, "honest_gap": 0-2, "short_spoken": 0-2, "filters": 0-2, "not_an_ad": 0-2}, "slate_id": "k1", "mechanism": "<from the candidate>", "slide2_move": "<from the candidate>"}`. If the candidate has `factual_claim: true`, map a sourced_fact claim to slide 1 or 2, and right after `child_gender`: `"addressee": "mom" or "parents"` and `"child_name": "<a name from names.md>"`. Never dad: no אבא or אתה, and the image anchor shows the mother (addressee mom) or both parents. `expert_frame` only on expert versions. Slides 1 to 9 carry no book, story offer or link. Slide 10's headline is one short line suggesting a personalised story (סיפור אישי) and its body is the CTA, in the addressee's form, split into three short lines with the same words. Claims needed: a sourced fact on at least one of slides 2 to 9 (expert: on at least two of them), a sourced fact on slide 10 that supports reading stories about this moment, and a product_fact on slide 10 for the personalised story (name in the text, child in every illustration).

Post texts (packs from 2026-10-26 21:00; Yarin, 26 Oct 2026: "in the written captions add punctuation marks and emojis (dont overdo it only at cta and hooks)"): each option also carries `post_text`, the two texts that go out with the carousel. `caption` is the caption and `fb_text` is the Facebook post above slide 1: slides 2 to 10, each slide's headline then body lines, a blank line between slides. Both keep exactly the same words and line breaks as their source (the validator compares them word by word) and add the periods, commas, question marks, colons and quotation marks a person would type, never a dash, semicolon or hyphen. Exactly two emojis in each: one at the end of the hook (line 1, or line 2 when the first sentence runs over two lines) that fits the topic (🎂 a birthday, 🌙 a bad dream, 🍝 picky eating, 📱 screens, 💛 feelings), and 🔖 at the end of the CTA line. No emoji anywhere else and none on the slides. Review edits keep the punctuation by themselves (`carousel_lib.post_texts`), and Carousel Machine sends these texts to Postiz.

Headlines are the story (Yarin, 10 Oct 2026): after writing, read only the ten headlines in order and check that they narrate the whole carousel by themselves. Each example headline names the thing itself after its number (never just "דבר ראשון"), numbers and times sit in the headline, and every headline is a full thought of 3 or more words. The validator checks the last two and the review page shows the headlines in one line for you to check the first.

Bold look (packs from 10 Oct 2026 18:30, `bold_look_rules` in the start JSON; the validator enforces all of it): cover headline up to 3 lines of 18 characters, other headlines up to 2 lines of 22, body up to 3 lines of 34, up to 20 words on slides 2 to 9. Since the clean look (14 Oct 2026) only the last slide's `highlight` is painted, so `highlight` is optional on slides 1 to 9 of 10 slide packs; when given it is the 1 to 3 whole words of its headline (on one line, with their prefix letter: "בסיפור אישי", not "סיפור אישי" cut out of "בסיפור") that get the colour block. Each headline of slides 2 to 9 is written like a cover and each example gives something concrete: a sentence to say in quotation marks, a ten second action or a number. If the copy does not fit, cut lines; never keep a connecting or softening line at the cost of the type size.

A complete 10 slide option that passes validation: `carousel/carousel-pipeline/tests/fixtures/ten_slide_option.json` (`version`). A whole pack of the older 7 slide shape: `carousel/carousel-pipeline/tests/fixtures/valid_pack.json`.

## 7 · Finish and fix

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/nightly.py finish <write_pack_to>
```

Errors name the field, line, column and character. Rewrite the failed line into natural Hebrew (a comma usually means two thoughts: make two lines). Then run finish again. Warnings are for judgement; read each and fix the real ones.

## 7b · The games and books carousel (OFF since 18 Oct 2026: skip this section)

Yarin, 18 Oct 2026: "i dont want the games and books carousels anymore". Kept for the carousels already made.

One more complete carousel, next to the pack and never instead of it: games and books together (Yarin, 14 Oct 2026: "combine the book and games to one carousel. 10-20 slides", then "cap it to 7-9 books and games"), written to `reco-carousel.json` (`"format": "mixed"`, path in the start JSON under `recommendations.write_to`). It has a random number of suggestions, 7 to 9, drawn by `nightly.py start` (`recommendations.suggestions.tonight`, saved in `reco-slots.json` so a rerun keeps it); the LumeBook book counts as one of them, so N suggestions = N - 1 real products + the LumeBook book, N + 3 slides (10 to 12), the hook is always `X משחקים וספרים לגילאי A-B ש...` with X = N, and the validator refuses any other size. Read `carousel/carousel-pipeline/recommendations.md` first; `carousel/carousel-pipeline/tests/fixtures/reco/reco-carousel.json` is a complete 20-slide example that passes. No image generation and no paid call, ever, and nothing is posted. Nights up to 13 Oct 2026 have `games-carousel.json` and `books-carousel.json` instead; never write those again.

0. Read `recommendations.recent_edits_learn_from_these` (Yarin's edits on reco.html, and on games.html and books.html of older nights: before and after, per slide role and field) and write tonight's copy the way the after lines sound. Never bring back what Yarin removed and do not copy the lines
1. Pick one stage and theme for the whole carousel: one age range and one skill not in `recommendations.rotation.mixed.blocked_skills` (it already counts the older games and books carousels). Both the games and the books serve that same stage. `hook_structure` is always `count_ages_skill`
2. Developmental sources: CDC milestone pages, AAP / HealthyChildren, ZERO TO THREE, Child Mind Institute, KidsHealth or peer reviewed research. Read each page and keep a verbatim quote
3. Products: N - 1 real products (N from tonight's draw), at least 3 games and at least 3 books, each with `kind` (`game` or `book`; games record the manufacturer, books the author and the Hebrew edition's publisher), no two of the same `type`, nothing from `blocked_products` or `recent_titles`. Each popular or clearly established in Israel with Israel-specific evidence you read today (Israeli bestseller lists or retailer rankings, Sifriyat Pijama, several independent Israeli retailers, an established Hebrew publisher or Israeli distributor, credible Israeli recommendations, Israeli review counts). International popularity never counts; label `available_in_israel` when the evidence is thin and prefer to replace the product. Nothing from `blocked_products`. Official age from the product source. Never invent rankings, sales or reviews
4. Images: download the real packshot or cover from the publisher, manufacturer, an official page, Sifriyat Pijama or an established Israeli retailer into `reco-assets/` (`curl -A "Mozilla/5.0"`), never Google Images. Record the URLs and size. `rights_status` is `rights_unverified` unless the page grants media use. The LumeBook slide (second to last suggestion) shows the COVER of the catalogue book whose idea the slide's line states (Yarin, 10 Oct 2026: the picture must depict the idea of the line). Pick the catalogue book first (its id is in the link `lumebook.com/IL/he/books/<id>`, read its description there), write the line `שבו הם... X` from what the book is about, then download its cover: `curl -A "Mozilla/5.0" https://lumebook.com/book_covers/boy/B<id>_boy.avif` (or `girl/B<id>_girl.avif`), convert with `sips -s format png`, `source_type: lumebook_site`, `rights_status: owned`, `catalogue_book_id: <id>`. OPEN the picture and check it: it must show the line's idea (if the cover shows only part of it, put that part in the line: "שבו הם פותחים ארגז צעצועים ומגלים שכיף יותר לשתף"), the book's age must fit the carousel's age, and there must be no garbled lettering (some covers have gibberish letters on a shirt; use the other variant, boy or girl, or another book). Write what you saw in `image.depicts`. Homepage hero renders are no longer used
4b. Carousel Machine (Yarin, 10 Oct 2026): the hook is `X משחקים וספרים לגילאי A-B ש...` (14 Oct 2026; X counts every suggestion, LumeBook included) and still maps to a developmental source, but write at least three wordings calm to loud, keep the loudest one the source supports, and list them in `hook_alternatives` (chosen one first on slide 1). The ending says the VALUE (Yarin, 11 Oct 2026): what the games or books help the children do, concretely ("שיעזרו להם לתכנן כמה צעדים קדימה", "שיעזרו להם לשתף פעולה ביחד"), with the מתרגלים / הזדמנות ל wording and never a promise of a result. Add `highlight` (1 to 3 whole headline words on one line) to slide 1 and slide 2, and optionally to the last slide's question line; see `recommendations.md` "Carousel Machine for games and books"
5. Copy, always in the plural to both parents and about children (`addressee: parents`; שאלו, תנו, הילדים, הם): slide 1 the fixed hook sentence in the headline (no body, with a slide-1 developmental claim), slide 2 what children practise (ages approximate, sourced), then the product slides with the games and books MIXED in order (Yarin, 16 Oct 2026: "mix their order instead of games and then books"; never 3 of the same kind in a row, alternate where the counts allow), the LumeBook slide second to last; every product slide exact title + age + why (why it is good: what the children practise, not how the game works) + how, the LumeBook slide (second to last suggestion) headline `ספר של LumeBook` and body `סיפור מותאם אישית עם תמונה של הילדים שלכם` / `שבו... X` (X fits the carousel's topic, from a catalogue book that covers the theme), last slide only the save and comment lines in the headline (no summary; the renderer puts every suggestion under a purple layer behind it). All the voice skill's hard rules apply
6. Run finish-reco and fix until it says VALID:

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/nightly.py finish-reco /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/drafts/DATE
```

It renders the deck with Chrome (1080 x 1350 PNGs, up to 20, in `reco/`, each product slide with a small משחק or ספר word above the title, plain plum text with no colour blocks except on the close slide), writes its page `reco.html` (one tab from `review.html`, the slides scroll sideways on a phone), and records `reco-history.json`. A 20-slide render takes about two minutes. Look at the contact sheet (`reco/contact-sheet.png`) yourself before reporting. "valid" is not "publish-ready": any `rights_unverified` image or `available_in_israel` product keeps a carousel not publish-ready, and the report says so.

## 8 · Report

Final message: the absolute path to `review.html`, then `review.md`, the topic, the six option ids with their child's name and hook, the games and books carousel (stage, size, the game and book titles, valid and publish-ready status, open flags), the voice status (for example "קול ברירת מחדל, 0 מתוך 15 דוגמאות"), and how to edit: `python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/review_server.py`.

## The child tells the parents (28 Oct 2026)

Yarin: "make this carousels about the kids sound like the kid is telling his parents". Slides 1 to 9 and the caption of every kid option are the child talking to mom or both parents, in first person with direct asks, never a narrator about the child. Slide 9 closes in the child voice, the caption bridge is `ובערב אפשר להמשיך עם סיפור שבו אני הגיבור/ה`, and the pack carries `"voice_style": "to_parents"`. The validator (`lib.to_parents_issues`) rejects third person lines.
