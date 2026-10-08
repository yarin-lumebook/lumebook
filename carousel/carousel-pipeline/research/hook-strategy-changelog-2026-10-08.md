# Hook strategy changelog, 8 Oct 2026

Full research: `hook-strategy-2026-10-08.md`. Evidence notes: `notes/platform-and-mechanisms-2026-10-08.md`.

## What changed

- **Hook bank** (`hook-bank.md`): 5 new formulas (`story-unresolved`, `just-so-you-know`, `positive-edition`, `parent-confession`, `analogy-scene`), 2 new families (`normalising`, `analogy`), an "Evidence and rotation" table (evidence labels, mechanisms, sentence shape, slide 2 moves, payoff slide, research date, review date) for all 22 formulas, a card per formula (Hebrew name, template, 3 examples, open question and payoff, a stand-alone slide 2, intent, risks, staleness signs, what to test), 3 new slide 2 moves (`first_answer`, `scene_restart`, `same_template`), a rejected-styles list, and 9 more banned openers (shame, fear, fake urgency, "stop doing")
- **Nightly hook slate**: before writing, each pack holds 6 kid and 6 expert candidates (`hook_slate`), scored 0 to 2 on ten criteria with four fail checks. Options are built only from passing candidates, chosen for difference. No winner is ever picked
- **Rotation**: the six options now need 4+ mechanisms (2+ per direction), 4+ sentence shapes, 3+ slide 2 moves, 2+ awareness stages and no near-identical openings. History records mechanism, shape, slide 2 move, awareness stage and slide 2 headlines. Warnings for formulas published in the last 14 days, recycled wording and repeated slide 2 headlines
- **Slide 2** must not open with a word that leans on slide 1 (error in new packs, warning in old ones)
- **Facts in hooks**: a hook that states something about children needs a sourced claim on slide 1 or 2
- **Trend expiry**: `current_trend` formulas carry a review date at most 120 days out and are blocked after it until re-checked
- **Validated label**: `lumebook_validated` is refused unless `hook-results.json` holds at least 6 posts with 300+ reach across 3 topics and a promotion note
- **Code**: `carousel_lib.py` (vocabularies, bank parsing, evidence status, near-duplicate check, history fields), `validate_pack.py` (slate and hook strategy checks), `nightly.py` (`start` prints the bank with status and rotation; new `hooks` command; `finish` requires schema_version 3), `pack.schema.json` (schema_version 2 or 3, `hook_slate`, `slate_id`, `mechanism`, `slide2_move`, two families), new `hook-results.json`
- **Docs**: README, the lumebook-carousel skill (SKILL.md and references/nightly.md step 5b) and the 22:00 task prompt now include the slate step
- **Tests**: 20 new tests; 95 in total, all passing. Worked example: `tests/fixtures/sample_slate_gan_separation.json`

## What was preserved

- All 17 existing formula ids, their families, directions and examples
- The 6-point hook score (9+ of 12, no zero) on every option, the banned openers, the slide 2 and re-hook move tables, every guardrail note
- The 7-slide arc, the CTA wording and code-word rules, no brand, no AI mention, no dad, named child, sourcing rules, topic and code-word cooldowns, family limits
- Version 2 packs (including today's `drafts/2026-10-08`) still validate under the earlier rules, so the review editor keeps working on them

## Current trends (expire 8 Jan 2027 unless re-checked)

`through-the-ages`, `just-so-you-know`, `positive-edition`.

## Research supported (mechanism, not LumeBook results)

`child-not-because`, `child-letter` (first-person wording and identification: M4, M8), `child-question`, `moment-time` (concreteness: psych.md 4), `parent-identity` (self-reference: psych.md 9), `story-unresolved` (narrative: psych.md 10). Also seen as an external performance pattern: `child-not-because`, `child-letter`, `instead-of-say`, `numbered-small-things`, `story-unresolved`, `parent-confession`.

Platform-supported rules (not formulas): slide 2 stands alone, no clickbait or engagement bait, no headline split across slides 1 and 2.

## LumeBook hypotheses

All 22 formulas. Hypothesis only, with no outside support beyond the playbook: `child-body-moment`, `child-hidden-half`, `child-numbered-ask`, `sentence-we-all-say`, `reversal`, `surprising-reframe`, `practical-question`, `milestone-week`, `parent-worry-quote`, `analogy-scene`. The slate pass mark (14 of 20) and the validation thresholds are hypotheses too.

## What LumeBook must measure before calling anything proven

Per published carousel, 7 days after posting, in `hook-results.json`: code-word comments per 1,000 reach (primary), preview visits per 1,000 reach, preview completions, purchases, then sends, saves and profile visits per reach and non-follower share. Change one hook variable at a time and repeat each formula across topics. A formula needs at least 6 comparable posts across 3 topics, beating the other formulas' median by 1.5x in at least 4 of 6, before Yarin may mark it validated. Check Account Status weekly while comment-word CTAs run.
