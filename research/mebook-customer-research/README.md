# MeBook customer study (מה לקוחות מיבוק אומרים)

14 Nov 2026. Who buys MeBook books, why, what almost stopped them and what they said when the book arrived, turned into six content hypotheses for LumeBook. Evidence about MeBook customers, not proof about LumeBook's.

Open the page on the project server: http://localhost:8780/research/mebook-customer-research/mebook-customer-research.html

## Files

| File | What it is |
|---|---|
| `report.md` | The full write-up in English (sections A to F, translations of every quote, method) |
| `data.json` | The source of the Hebrew page: quotes, counts, patterns, language bank, hypotheses, questions |
| `build.py` | Writes `mebook-customer-research.html` with `design.head()`. Fails on an unknown theme, a quote number that does not exist, an em or en dash, or the brand spelt לומיבוק |
| `mebook-customer-research.html` | The built page. Never edit it by hand |
| `purchase-intents.md` | 100 purchase intents in Hebrew (34 direct evidence, 36 inference, 30 hypothesis), each with a source code, and the 10 to test first with sales hypotheses (14 Nov 2026) |
| `sources/google-reviews.json` | The 46 Google reviews with text, original Hebrew, numbered G1 to G46, no names |
| `sources/site-reviews.json` | The 41 verified reviews from mebook.ai book pages, numbered S1 to S41, no names |
| `sources/live-pages.md` | Exact text from pages read live and not saved elsewhere (MeBook site, one ad, posts), codes L1 to L9 |
| `../mebook-hooks/hooks.json` | Read by the page's "50 ההוקים" section (15 Nov 2026): MeBook's 50 best performing on-screen, spoken and caption hooks by Reel views, and the 21 video ads. Built by `research/mebook-hooks/assemble.py`; correct a hook there, not in the page |

Build: `python3 tools/lumebook.py build mebook-customer-research` (or `python3 build.py` here). Theme hues: `shared/design/categories.json` set `mebook-themes`.

`report.md` and `data.json` carry the same findings; a change to one needs the same change in the other.

The page's "100 כוונות קנייה" section is parsed from `purchase-intents.md` at build time (its only source): keep its tables in the same shape (`### ` category headings, rows `| n | intent | buyer | hesitation | label · source | what to show |`, the top 10 table and the numbered sales hypotheses `N. **#n** ...`). The build fails if numbers skip, a label is not ישירה, הסקה or השערה, or a top 10 intent has no hypothesis. Source codes G, S and L show their original text on hover; Q codes jump to the quote card.

## Tabs and trimmed page (15 Nov 2026)

The sidebar opens one section at a time (tabs, `#hash` links work; a quote or intent link opens its own tab first; typing in the search from another tab jumps to the quotes tab). The number cubes moved into the quotes tab, where they filter. Yarin's edit-button changes of 15 Nov were ported into `build.py`: the page no longer shows the identity, experiments and method sections, the logo, the hero text, the warning, the brand-claims box, our suggested phrases and the how-to notes; the title is "Mebook: מחקר". The data stays in `data.json` and `report.md`. The 27 operations were archived in `_to-delete/shared/site-editor/edits/`; the live edits list for this page is empty.

**Every statement is a card (15 Nov 2026, Yarin: "add all, i dont want any missing pieces").** The quotes tab now holds all 150 statements of the sample (46 Google, 41 site, 54 Instagram and TikTok comments, 9 Facebook), cards #1 to #150; each card carries `codes` (G and S ids of `sources/`, IG, TT, FB) and `count` when one card is several people (#28 is 3). Added cards also have an English line `en`, used by `report.md` table B (rows 48 to 150). The build fails if a Google or site review has no card, or if a cube or a themed pattern disagrees with the count of the table (`validate()`). Comments that are only "מושלם", an emoji, a tag or a joke about the creator are not counted. Theme chips on the cards are buttons that filter to that theme.

**MeBook's reels per purchase intent (15 Nov 2026, Yarin: "i meant from mebook reels").** `mebook-reel-intents.json` maps MeBook's own reels and video ads (the 62 reels and 21 ads of `research/mebook-hooks/hooks.json`, by Instagram shortcode or Meta Ad Library id) to the intents they are about, by topic: it says what a reel shows, not that it was made for that intent or that it sold. Each intent card and each top-10 card has a "רילס של מיבוק" row (most viewed first, then the ads) whose chips open the reel on Instagram or the ad in the Meta Ad Library. The intents tab filters "יש רילס של מיבוק" / "אין רילס שמתאימים". The build fails if an id is not in hooks.json. (A first version matched our own November reels; archived in `_to-delete/research/mebook-customer-research/`.)

## Experiment log (יומן ניסויים, 14 Nov 2026)

A content experiment log on the page, linked to the research. Records live in `experiments.json` (created on the first save, in git so the nightly commit keeps it), read and written by the project server (`tools/experiments.py`: `GET /api/experiments`, `PUT /api/experiments/doc?id=`, same-origin only). The built page never holds them, so the log works only on the project server (http://localhost:8780); elsewhere it is read-only.

- Start an experiment from any purchase intent, summary finding, pattern or content hypothesis (the "+ ניסוי מכאן" button on each), or with "+ ניסוי חדש". Prefill: an intent brings its buyer, intent, hesitation, what to show, and its sales hypothesis when it is in the top 10; a hypothesis brings audience, message, insight and hook; a finding brings its text. Only a title and a hypothesis are required.
- Each source record lists its experiments with status and the conclusion and explanation once recorded.
- Results are typed in by hand. An empty field is "not measured" (null), 0 is "measured, none". CPA (ad spend / attributed purchases, paid only, not total CAC), ROAS (attributed revenue / ad spend) and visit to purchase (attributed purchases / visits) show "unavailable" with the reason when a value is missing or a denominator is 0 (`experiments-metrics.js`). Organic experiments show a note that attribution is partial and does not prove the content caused a sale.
- Three investigation prompts light up when their numbers exist (reach vs visits, visits vs purchases, a single purchase); there are no thresholds.
- "Completed" needs a conclusion (מבטיח, לא חד משמעי, לא נתמך) and an explanation, checked on the page and on the server. "ניסוי המשך" opens a new experiment linked to the previous one, with its "הניסוי הבא" text as the hypothesis.
- Files: `experiments.src.js` (the page script), `experiments-metrics.js` (pure calculations, also run by the tests), `tools/experiments.py` (validation and storage), `tools/tests/test_experiments.py` (`python3 -m unittest discover -s tools/tests`). Restart the server (`python3 tools/serve_login.py restart`) after editing `tools/experiments.py`; test endpoint changes on a spare port with `LUMEBOOK_EXPERIMENTS_FILE` pointing at a scratch file.

## Sources

MeBook's Google listing (67 reviews, read in the original Hebrew), 41 verified-purchase reviews on mebook.ai book pages, 252 Instagram and TikTok comments from the competitor teardown (`research/competitor-content-analysis/competitor_content_db.json`), one public Facebook group question, and Facebook read signed in on 14 Nov 2026: every MeBook page post with comments (4), the page's Mentions tab and the Facebook copy of a creator reel (71 of 73 comments, none about the book). Not read: comments on MeBook's Facebook ads (Meta's Ad Library shows ads without comments, and ads that are not page posts have no public link), 3 of 4 Facebook page reviews (signed in, Facebook hides the Reviews tab; signed out it shows one), Trustpilot (bot check), closed parent groups. Reviewer names and commenter handles are left out.
