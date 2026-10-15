# Creator content and purchase intent: source

How the files one level up were made (14 Oct 2026). Method and limits: `../methodology.md`.

Raw data stays out of the repo: per-creator Instagram exports (`raw/`), downloaded media and contact sheets (`media/`, about 2 GB), raw comments with usernames (`cm.json`, `cm_extra.json`) and the per-post coding files lived in the session scratchpad. `posts.csv` and `creators.csv` carry everything needed to read the results; re-collect to rebuild.

| Step | File | What it does |
|---|---|---|
| 1 | `collector.js` | The in-browser Instagram collector (posts, reels plays, profile, comments) |
| 2 | `parse_export.py` | Turns an exported browser result into `raw/<handle>.json` |
| 3 | `sample.py` | Builds each creator's sample (7 to 90 days, up to 12 posts, 180-day fallback) and older breakouts; writes `sample.json` |
| 4 | `media.py` | Downloads each sampled post's media and makes contact sheets (6 reel frames, every carousel slide up to 12) |
| 5 | `dossier.py` | One coding dossier per creator (metrics, caption, sheets) |
| 6 | `CODING_BRIEF.md` | The schema and rules the coding agents followed |
| 7 | `select_deep.py` | Picks the comment posts per creator (strong, ordinary, relevant); `deep.json`, plus `extra_list.json` for the 34 high-relevance posts added after coding |
| 8 | `COMMENT_BRIEF.md` | Comment classes and rules |
| 9 | `transcribe_deep.py` | Whisper on deep-dive reels (stopped after 24) |
| 10 | `analysis.py` | Merges metrics, codes and comment codes; `python3 analysis.py <outdir>` writes `posts.csv` and `creators.csv` |
| 11 | `aggregate.py`, `comment_stats.py`, `leaderboards.py` | Topic tables, comment tables and the KPI leaderboards used in `report.md` |
| 12 | `build_page.py` | Builds `../report.html`, the sidebar app on the LumeBook design system (13 views; tables and charts computed from the CSVs; evidence and method views from the .md files). `build_html.py` holds its markdown helpers. Local only: the page holds sales figures |
| | `strata.json` | Sampling stratum and reason per creator |
| | `concept_hooks_he.json` | The ten Hebrew concept hooks, linted with `carousel/carousel-pipeline/scripts/voice_lint.py` (fallback voice) |

The scripts use absolute paths from the session that made them (scratchpad and project); change `B`/`BASE` before re-running.
