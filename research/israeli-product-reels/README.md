# Israeli creator product Reels: what to film for LumeBook, and how

Research of 15 Oct 2026 for Yarin's own filming. A phone, a home, no crew, no child on camera.

| File | What is in it |
|---|---|
| `playbook.md` | The filming guide: what the sample shows, seven approaches, weak choices and fixes, five LumeBook Reel concepts with Hebrew scripts and shot lists, and a 60-90 minute first shoot |
| `creator-brief.md` | The brief for barter creators (approach A): shot skeleton, one worry with checked facts, CTA, caption with disclosure, do-not list, checklist. Hebrew linted by `src/lint_creator_brief.py`. Not sent yet |
| `creator-brief.html` | The brief's Hebrew part as a page, built by `src/build_creator_brief.py`; artifact https://claude.ai/artifact/T9DJuNSzHoQ2WNHzceZq8L (component `creator-brief`) |
| `reels-research.html` | All of the above (except the creator brief) as one page with the frame strips embedded, built by `src/build_research_page.py`; private artifact https://claude.ai/artifact/A8ytoWta3FoFHJX9tvjHUJ (component `reels-research-page`) |
| `breakdowns.md` | Eight Reels broken down second by second, with annotated frame strips |
| `source-index.md` | All 41 verified Reels (34 creators), excluded Reels and unwatched leads, with URLs, dates, relationship, disclosure and public counts |
| `sources.csv` | The same index, one row per Reel, every field |
| `src/` | Scripts, the coding brief, per-Reel coding (`coded/`), my verification file (`review.json`), Instagram counts read on 15 Oct (`media_info_15oct.json`), product facts checked on lumebook.com (`product-facts-2026-10-15.md`), the linted Hebrew scripts (`scripts/`) |

Raw videos, frames, transcripts and the annotated strips are in `media/projects/2026-10-15-israeli-product-reels/` (not in git).

## Bottom line

1. **Show the product in the first second, or open on a moment strong enough to wait for.** 35 of 41 Reels show the product within 2 seconds; the exceptions open on a mishap or a milestone.
2. **Personalised-book Reels nearly all depend on a child on camera (13 of 14), and none shows the price.** Two things LumeBook can film without a child are mostly missing from the category: the child's real photo beside the illustration (2 of 14 here, 10 of 147 in the earlier competitor teardown) and the price shown openly.
3. **The most watched Reels are hands-on demonstrations and simple fixes,** not book pitches: a gan teacher's push lights (154,090 plays), a clinician's reading tips (113,036). This matches the 14 Oct creator study.
4. **Comment words collect requests, not proof of buying.** Keep LumeBook's fixed word "לומי", but judge each Reel by DMs that lead to books started.
5. **Yarin's own formats:** hands and daylight, a labelled "what's inside" tour, facts to camera, problem-first stories told with objects, result-first gifts. Story-and-reaction Reels with children are for creator briefs.

None of this is tied to a sale: every number is a public count read on 15 Oct 2026.

## Watch these five first

| # | Reel | What to pay attention to |
|---|---|---|
| 1 | [@shoham_novik × LumeBook](https://www.instagram.com/reel/DTugYwmDNKa/) (53 s) | LumeBook's own creator Reel. The problem line and the book on screen within 1 second; the screen recording of the ordering flow tucked into the story at 0:11; the delivery-time worry said out loud at 0:28; the honest close ("not magic"). Also what is missing: no CTA on screen, and a caption about birthdays on a potty-training video. |
| 2 | [@mayashany_photography × MeBook](https://www.instagram.com/reel/DWW7cLNDZvv/) (27 s) | The closest thing to what you can film tomorrow: hands, a book held up to daylight, headline text that builds word by word, and the dedication page as the last image. Notice how the ad-copy voiceover weakens it. |
| 3 | [@etti_haft](https://www.instagram.com/reel/Ddrev0jjauL/) (29 s) | Watch it muted. The first word picks the audience ("גננת?"), then one label per part of the product. This is the skeleton of your first Reel. Notice the dim, shaky top-down shots you should avoid. |
| 4 | [@nofar_aizik](https://www.instagram.com/reel/DcZCOp4ItbM/) (36 s) | The problem is shown before the product, which appears only at 0:16. Text and voiceover say exactly the same words, so it works with sound on or off. The comment word is on screen at the end. |
| 5 | [@topaz_meir_slp](https://www.instagram.com/reel/Dc6VXOdMWOv/) (30 s) | One set-up, a book in her hands, a new numbered heading every three seconds, and she demonstrates instead of explaining. Notice the hook text covering her face in the first frames. |

If you have time for a sixth: [@lital_magnezi](https://www.instagram.com/reel/Dd5sq3TI1I5/) (24 s), one action in close-up then the same action repeated, with buying questions in the comments and no CTA at all.

## Film this first

Concept 1, "מה באמת מקבלים" (what you actually get): a 33-second hands-only tour of one printed LumeBook, with labels, the price, the free preview and the CTA. The full shot list, Hebrew script and a minute-by-minute 60-90 minute shoot plan are in `playbook.md`, sections 4 and 5. The one thing you need first is a printed book you are allowed to show publicly; a book made from your own childhood photo (concept 2) needs nobody else's consent.

## Evidence limits

- **What was watched:** every Reel as one frame per second plus a local machine transcript (Whisper, Hebrew, first 90 seconds) and its caption. I cannot hear audio, so music and natural sound are reported only when the transcript or frames show them. Transcripts mishear words; quotes come from the creators' on-screen subtitles where possible.
- **Who coded what:** 47 Reels were downloaded. Sonnet agents coded 46 of them with one brief (`src/CODING_BRIEF.md`) and I coded the 47th; I checked every included Reel against its frames myself, fully for the eight deep dives and with a 10-frame strip for the rest. 41 are verified examples and 6 are excluded (synthetic visuals, a stock-footage slideshow, or no product to learn from).
- **Counts:** plays, likes and comments were read on 15 Oct 2026 (Instagram's media info in the logged-in Claude browser pane, read only). Shares, saves, reach, watch time and sales are unavailable. Plays on LumeBook's own collab may include ad delivery; check Ads Manager.
- **Sample:** not random. It grew from leads in `research/creator-content-conversion/` and `research/competitor-content-analysis/`, LumeBook's product brief, and two Instagram keyword searches. Creators range from 458 to about 54,000 followers. 40 of 41 Reels are from the past 12 months; one (July 2024) is kept because it is the most commented personalised-book Reel found.
- **Product facts and Hebrew:** facts were checked on lumebook.com on 15 Oct 2026; re-check price and delivery before posting. The Hebrew scripts follow the LumeBook voice skill's fallback voice (12 of 15 calibration samples) and pass its lint.
- **Not done, as asked:** no creator was contacted, nothing was published, bought, committed or pushed.

## Rebuild

```
python3 research/israeli-product-reels/src/build_index.py
```

Rebuilds `source-index.md` and `sources.csv` from `src/review.json`, `src/coded/`, `src/media_info_15oct.json` and `src/followers.json`. Annotated strips: `src/annotate.py` (needs Pillow, for example the watch-video skill's venv). Frames and transcripts: `src/process.py frames|whisper CODE`.
