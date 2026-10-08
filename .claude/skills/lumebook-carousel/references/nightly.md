# Nightly review mode, step by step

Project folder: `/Users/yarinbruner/Claude/Projects/Lumebook`. Use absolute paths in commands so the run works from any working directory.

## 0 · Guard rails

- No fal.ai calls, no paid tools, no publishing, no messages. This mode only reads, researches and writes files under `carousel/carousel-pipeline/drafts/` and `carousel/carousel-pipeline/history.json`
- Never overwrite a pack by hand. `nightly.py start` moves an existing pack for the same date to `versions/vN/` first
- Do not select a winner. Do not edit `voice-profile.md` or the example folders
- Never name LumeBook (לומבוק, LumeBook) or a catalogue book title in anything a parent reads. Slide 7 only hints that a book where the child is the hero can help; the comment link leads to the product

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
- Carousel research v2, "Niche Carousel Teardown" (`research/carousel-research/lumebook-carousel-research.html`, published as https://claude.ai/artifact/Rkt3DeuC86z23WcAbR7VHW): use it for format ideas when making the three options in a direction genuinely different. What it found in Israeli parenting accounts (6 Oct 2026, engagement signals, not sales data): comment-word carousels pull far more comments than the account's norm; letters told over one repeated photo and "life through the ages" stories get reach and shares; "instead of X, say Y" with illustrated characters and short how-to lists get leads; a story offered as the reward (saraigatt's "לב הקשת") drew more comments than likes. Never use ספר as a code word (MeBook creators use it); the validator blocks it
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
- Every candidate's Hebrew follows the same rules as the slides (no comma, period or em dash; hook main line up to 8 words, 12 in total; never dad; no sale words). Slide 2 never opens with a word that leans on slide 1 (אבל, ואז, כי, גם, זה, ככה...)
- Score honestly. A candidate fails with any fail check true, a 0 on honest_curiosity, emotional_truth, topic_fit or lumebook_fit, or a total under 14 of 20. Failed candidates stay in the slate, unused
- Mark exactly one candidate per option in `used_by`, choosing three different ones per direction for difference: across the six, 4+ mechanisms (2+ per direction), 4+ sentence shapes, 3+ slide 2 moves, 2+ awareness stages, and no two openings that share most of their words
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
  "hook_family": "<one of the families printed by start>", "code_word": "לב", "child_gender": "boy|girl",
  "character_anchor": {"child": "English, with age", "parent": "English", "wardrobe": "English"},
  "expert_frame": {"type": "evidence_based_take"},
  "slides": [{"number": 1, "role": "hook", "headline": "Hebrew", "body": "Hebrew lines or empty",
              "pull": {"type": "question|open_loop|next_step|contrast|numbered", "note": "what makes them swipe to slide 2"},
              "image": {"beat": "", "action": "", "setting": "", "camera": "", "lighting": "", "wardrobe_objects": "",
                        "text_zone": {"edge": "top", "percent": 40, "surface": "plain warm cream wall"}}}],
  "caption": "5 to 8 lines, last line = cta",
  "cta": "כתבו לב בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור",
  "sources": [{"id": "src-aap", "title": "", "publisher": "", "url": "", "accessed": "YYYY-MM-DD", "quote": "verbatim", "supports": ""}],
  "claims": [{"slide": 5, "wording_he": "", "kind": "sourced_fact|product_fact|lumebook_wording", "source_ids": [], "supports": ""}],
  "conversion_rationale": "Hebrew, why this version may convert"
}
```

Roles in order (7 slides): hook, second_hook, recognition or reframe, solution, solution, resolution, story_cta. Slides 1 to 6 each need a `pull`; slide 7 has none. Write each pull `note` in short Hebrew (it is shown to Yarin under the slide), for example "השאלה נענית בשקופית 3". Each version also needs `hook` right after `hook_family`: `{"formula": "<id from hook-bank.md>", "gap": "the question the hook opens", "payoff_slide": 3-6, "score": {"specific": 0-2, "feeling": 0-2, "honest_gap": 0-2, "short_spoken": 0-2, "filters": 0-2, "not_an_ad": 0-2}, "slate_id": "k1", "mechanism": "<from the candidate>", "slide2_move": "<from the candidate>"}`. If the candidate has `factual_claim: true`, map a sourced_fact claim to slide 1 or 2, and right after `child_gender`: `"addressee": "mom" or "parents"` and `"child_name": "<a name from names.md>"`. Never dad: no אבא or אתה, and the image anchor shows the mother (addressee mom) or both parents. `expert_frame` only on expert versions. Slide 6 closes the story with no book, story offer or link. Slide 7's headline is one short line suggesting a personalised story (סיפור אישי) and its body is the CTA, in the addressee's form, split into three short lines with the same words. Claims needed: a sourced fact on at least one solution slide (expert: on both, 4 and 5), a sourced fact on slide 7 that supports reading stories about this moment, and a product_fact on slide 7 for the personalised story (name in the text, child in every illustration).

A complete example that passed validation: `carousel/carousel-pipeline/tests/fixtures/valid_pack.json`.

## 7 · Finish and fix

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/nightly.py finish <write_pack_to>
```

Errors name the field, line, column and character. Rewrite the failed line into natural Hebrew (a comma usually means two thoughts: make two lines). Then run finish again. Warnings are for judgement; read each and fix the real ones.

## 7b · Games and books carousels (every night, after the pack)

Two more complete carousels, next to the pack and never instead of it: `games-carousel.json` and `books-carousel.json` in the same folder (paths in the start JSON under `recommendations`). Read `carousel/carousel-pipeline/recommendations.md` first; the fixtures in `carousel/carousel-pipeline/tests/fixtures/reco/` are complete examples that pass. No image generation and no paid call, ever, and nothing is posted.

1. Pick a stage for each: one age range and one skill not in `recommendations.rotation.<format>.blocked_skills`, a hook structure other than `last_hook_structure`. The two may share the age range
2. Developmental sources: CDC milestone pages, AAP / HealthyChildren, ZERO TO THREE, Child Mind Institute, KidsHealth or peer reviewed research. Read each page and keep a verbatim quote
3. Products: 3 games and 3 books, each popular or clearly established in Israel with Israel-specific evidence you read today (Israeli bestseller lists or retailer rankings, Sifriyat Pijama, several independent Israeli retailers, an established Hebrew publisher or Israeli distributor, credible Israeli recommendations, Israeli review counts). International popularity never counts; label `available_in_israel` when the evidence is thin and prefer to replace the product. Nothing from `blocked_products`. Official age from the product source. Never invent rankings, sales or reviews
4. Images: download the real packshot or cover from the publisher, manufacturer, an official page, Sifriyat Pijama or an established Israeli retailer into `reco-assets/` (`curl -A "Mozilla/5.0"`), never Google Images. Record the URLs and size. `rights_status` is `rights_unverified` unless the page grants media use. Slide 6 uses a real LumeBook catalogue cover from lumebook.com (`https://lumebook.com/book_covers/<boy|girl>/B<n>_<gender>.webp`, `rights_status: owned`)
5. Copy: slide 1 hook (age or need), slide 2 what children practise (ages approximate, sourced), slides 3 to 5 exact title + age + why (the actual activity) + how, slide 6 LumeBook once, relaxed, tied to the same need, slide 7 a useful summary and a light save, share or comment prompt. All the voice skill's hard rules apply
6. Run finish-reco and fix until both say VALID:

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/nightly.py finish-reco /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/drafts/DATE
```

It renders both decks with Chrome (1080 x 1350 PNGs in `games/` and `books/`), rebuilds `review.html` with a section for them and records `reco-history.json`. Look at both contact sheets yourself before reporting. "valid" is not "publish-ready": any `rights_unverified` image or `available_in_israel` product keeps a carousel not publish-ready, and the report says so.

## 8 · Report

Final message: the absolute path to `review.html`, then `review.md`, the topic, the six option ids with their child's name and hook, the games and books carousels (stage, the three titles each, valid and publish-ready status, open flags), the voice status (for example "קול ברירת מחדל, 0 מתוך 15 דוגמאות"), and how to edit: `python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/review_server.py`.
