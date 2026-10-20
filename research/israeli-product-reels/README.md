# Israeli creator product Reels: what to film for LumeBook, and how

Research of 15 Oct 2026 for Yarin's own filming. A phone, a home, no crew, no child on camera. On 18 Oct 2026 every Reel was broken down on eight questions, each why backed by SMM research, and every playbook rule was checked against that research and the sample (playbook section 8).

| File | What is in it |
|---|---|
| `playbook.md` | The filming guide: what the sample shows, seven approaches, weak choices and fixes, five LumeBook Reel concepts with Hebrew scripts and shot lists, and a 60-90 minute first shoot |
| `creator-brief.md` | The brief for barter creators (approach A): shot skeleton, one worry with checked facts, CTA, caption with disclosure, do-not list, checklist. Hebrew linted by `src/lint_creator_brief.py`. Not sent yet |
| `creator-brief.html` | The brief's Hebrew part as a page, built by `src/build_creator_brief.py`; artifact https://claude.ai/artifact/T9DJuNSzHoQ2WNHzceZq8L (component `creator-brief`) |
| `reels-research.html` | All of the above (except the creator brief) as one app: a sidebar with the 8 tools, a page per tool, principle, concept, deep dive and Reel, the proof board and a pre-post checklist; the frame strips embedded. Data from `src/build_research_page.py`, rendered by `src/page/playbook.js` and `playbook.css`; private artifact https://claude.ai/artifact/A8ytoWta3FoFHJX9tvjHUJ (component `reels-research-page`) |
| `breakdowns.md` | Eight Reels broken down second by second, with annotated frame strips |
| `smm-research/` | The SMM research of 18 Oct: `principles.md` (63 principles, each with its rule, evidence strength, sources and what it means for LumeBook; built by `src/build_principles.py` from `notes/`), `notes/` (the four full research passes: hooks and retention, CTA and text, what is shown and filmed, editing and topic, each with sources, sample sizes and traced myths), `sample-check.md` (each principle's feature compared on the 173 Reels' public counts, built by `src/evidence_check.py`) |
| `src/table/` | The 8-question table: one JSON per verified Reel (hook, every few seconds, CTA, what is shown, editing, topic, filming, text and caption), each what observed and each why citing principle IDs; written from `src/TABLE_BRIEF.md`, checked by `src/check_table.py`, shown on the page by `src/reel_table.py` |
| `source-index.md` | All 173 verified Reels (108 creators), the 24 excluded, and unwatched leads, with URLs, dates, relationship, disclosure and public counts |
| `sources.csv` | The same index, one row per Reel, every field |
| `src/` | Scripts, the coding brief, per-Reel coding (`coded/`), my verification file (`review.json`), Instagram counts read on 15 Oct (`media_info_15oct.json`), product facts checked on lumebook.com (`product-facts-2026-10-15.md`), the linted Hebrew scripts (`scripts/`) |

Raw videos, frames, transcripts and the annotated strips are in `media/projects/2026-10-15-israeli-product-reels/` (not in git).

## Bottom line

Updated the evening of 15 Oct with 150 more Reels: 197 watched, 173 verified from 108 creators, 24 excluded.

1. **Show the product in the first second, or open on a moment strong enough to wait for.** 150 of 173 Reels show the product within 2 seconds; the exceptions open on a mishap, a milestone or a personal story.
2. **Personalised-book Reels nearly all depend on a child on camera (29 of 36), and almost none shows the price (1 of 36, inside a screen recording).** Two things LumeBook can film without a child are mostly missing from the category: the child's real photo beside the illustration (5 of 36 here, 10 of 147 in the earlier competitor teardown) and the price shown openly. Only 5 of all 173 Reels show a price in the video.
3. **The most watched Reels are relatable moments and simple, useful objects,** not book pitches: makeup on a daughter (297,086 plays), backpacks for a family trip (198,007), a mother's surgery story with a scar gel (168,493), a gan teacher's push lights (154,090), a clinician's reading tips (113,036). This matches the 14 Oct creator study. The best personalised-book counts come from professionals presenting a book they co-created (19,983 and 12,705 plays): a pattern for creator briefs, not for Yarin's own camera.
4. **Comment words collect requests, not proof of buying.** Keep LumeBook's fixed word "לומי", but judge each Reel by DMs that lead to books started.
5. **Yarin's own formats:** hands and daylight, a labelled "what's inside" tour, facts to camera, problem-first stories told with objects, result-first gifts. Story-and-reaction Reels with children are for creator briefs.
6. **Checked against research (18 Oct, playbook section 8).** Holds: the product in the first second, text on screen from the first frame, one CTA on screen, the comment word (when it always delivers the link), relatable moments and useful objects over book pitches. Changed: a voice from the first second instead of voice as optional; the hands-only, no-face formats were the weakest group in the sample (median 0.45 plays per follower against 0.76), so add Yarin's voice from 0:00 and test an opening on his face; text above the bottom 35% of the frame; disclosure visible at first view; length by content, not 20 to 35 s. Unproven: open pricing, the photo beside the page, the screen recording, problem-first hooks. The proof that counts is LumeBook's own Reels, logged as in section 7.

None of this is tied to a sale: every number is a public count read on 15 Oct 2026.

## Watch these five first

| # | Reel | What to pay attention to |
|---|---|---|
| 1 | [@shoham_novik × LumeBook](https://www.instagram.com/reel/DTugYwmDNKa/) (53 s) | LumeBook's own creator Reel. The problem line and the book on screen within 1 second; the screen recording of the ordering flow tucked into the story at 0:11; the delivery-time worry said out loud at 0:28; the honest close ("not magic"). Also what is missing: no CTA on screen, and a caption about birthdays on a potty-training video. |
| 2 | [@mayashany_photography × MeBook](https://www.instagram.com/reel/DWW7cLNDZvv/) (27 s) | The closest thing to what you can film tomorrow: hands, a book held up to daylight, headline text that builds word by word, and the dedication page as the last image. Notice how the ad-copy voiceover weakens it. |
| 3 | [@etti_haft](https://www.instagram.com/reel/Ddrev0jjauL/) (29 s) | Watch it muted. The first word picks the audience ("גננת?"), then one label per part of the product. This is the skeleton of your first Reel. Notice the dim, shaky top-down shots you should avoid. |
| 4 | [@nofar_aizik](https://www.instagram.com/reel/DcZCOp4ItbM/) (36 s) | The problem is shown before the product, which appears only at 0:16. Text and voiceover say exactly the same words, so it works with sound on or off. The comment word is on screen at the end. |
| 5 | [@topaz_meir_slp](https://www.instagram.com/reel/Dc6VXOdMWOv/) (30 s) | One set-up, a book in her hands, a new numbered heading every three seconds, and she demonstrates instead of explaining. Notice the hook text box covering the book in the first two frames. |

If you have time for a sixth: [@lital_magnezi](https://www.instagram.com/reel/Dd5sq3TI1I5/) (24 s), one action in close-up then the same action repeated, with buying questions in the comments and no CTA at all.

## Film this first

Concept 1, "מה באמת מקבלים" (what you actually get): a 33-second hands-only tour of one printed LumeBook, with labels, the price, the free preview and the CTA. The full shot list, Hebrew script and a minute-by-minute 60-90 minute shoot plan are in `playbook.md`, sections 4 and 5. The one thing you need first is a printed book you are allowed to show publicly; a book made from your own childhood photo (concept 2) needs nobody else's consent.

## Evidence limits

- **What was watched:** every Reel as one frame per second plus a local machine transcript (Whisper, Hebrew, first 90 seconds) and its caption. I cannot hear audio, so music and natural sound are reported only when the transcript or frames show them. Transcripts mishear words; quotes come from the creators' on-screen subtitles where possible.
- **Who coded what:** 197 Reels were downloaded and watched (2 more candidates failed to download). Sonnet agents coded 196 with one brief (`src/CODING_BRIEF.md`, with yes/no fields added for round 2) and I coded one; I checked every Reel against its frames myself, fully for the eight deep dives and with a 10-frame strip for the rest. 173 are verified and 24 excluded (synthetic visuals, store hauls, digital or printable products, or no product). The yes/no fields for the first 47 were backfilled by an agent that could not see every sheet; the least certain ones are listed in `src/review.json`.
- **Counts:** plays, likes and comments were read on 15 Oct 2026 (Instagram's media info in the logged-in Claude browser pane, read only). Shares, saves, reach, watch time and sales are unavailable. Plays on LumeBook's own collab may include ad delivery; check Ads Manager.
- **Sample:** not random. Round 1 grew from leads in `research/creator-content-conversion/` and `research/competitor-content-analysis/`, LumeBook's product brief and two Instagram keyword searches. Round 2 came mainly from the Reels grids of 12 children's brands (creator collaborations only) and of 9 product-focused parent creators, plus the remaining product leads of the 14 Oct study, with off-topic leads (restaurants, beauty, travel) dropped. 169 of 173 Reels are from the past 12 months. Follower counts were read for round-1 creators only. Comments were not read for round-2 Reels.
- **Product facts and Hebrew:** facts were checked on lumebook.com on 15 Oct 2026; re-check price and delivery before posting. The Hebrew scripts follow the LumeBook voice skill's fallback voice (12 of 15 calibration samples) and pass its lint.
- **The 18 Oct research and table:** four research agents read platform documentation, peer-reviewed studies (for paywalled journals mostly the abstract, marked in the notes), industry datasets and Israeli regulators, about 100 web searches in all; every source cited was opened. Eight Sonnet agents wrote the 8-question rows from every contact sheet, the transcript and the caption, citing only the principle IDs. I wrote the worked example, checked every row with `src/check_table.py`, and checked eleven rows (at least one per agent) against the frames. Ten first-pass codings were corrected (`src/coded_fixes_2026-10-18.json`); resolution remarks were removed because downloaded copies can be smaller than what was posted. Follower counts for the 73 creators that had none were read on 18 Oct from Instagram's public og:description (`src/followers.json`, source `og18`).
- **Not done, as asked:** no creator was contacted, nothing was published, bought, committed or pushed.

## Rebuild

```
python3 research/israeli-product-reels/src/build_index.py
python3 research/israeli-product-reels/src/build_principles.py   # principles.md and principles-index.md from smm-research/notes/
python3 research/israeli-product-reels/src/check_table.py        # every 8-question row: fields, principle IDs, no em dashes
python3 research/israeli-product-reels/src/evidence_check.py     # smm-research/sample-check.md
python3 research/israeli-product-reels/src/build_research_page.py
```

Rebuilds `source-index.md` and `sources.csv` (and `src/sample_stats.py` prints the counts in `playbook.md` section 1) from `src/review.json`, `src/coded/`, `src/media_info_15oct.json` and `src/followers.json`. Annotated strips: `src/annotate.py` (needs Pillow, for example the watch-video skill's venv). Frames and transcripts: `src/process.py frames|whisper CODE`.
