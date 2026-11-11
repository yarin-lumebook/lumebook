# @adar.motherhood: voice, hooks and CTAs (11 / 11 / 2026)

How Adar (@adar.motherhood, homeschooling mom of two who sells parent guidance, 7,030 followers on 11 / 11 / 2026) writes, opens and closes her content, and how to make content like hers for LumeBook. Asked by Yarin on 11 / 11 / 2026: "learn adar.motherhood voice, focus on the hooks and CTAs and create an analysis explaining how to create content like her". Internal study only: her videos, frames and transcripts stay on this Mac in `media/projects/2026-11-11-adar-motherhood-reels/` (not in git, never re-post).

## Files

| File | What |
|---|---|
| `report.md` | The analysis: her voice, hook families with counts, CTAs with results, carousels, a step by step method, what LumeBook can take, example lines (lint passed), tests |
| `data/reels.json` | Every Reel in her Reels tab on 11 / 11 / 2026 (591): plays, likes, comments, date decoded from the code |
| `data/selected.json` | The 34 Reels studied: 22 top since 2024 and 12 controls (2025 to 2026, 1,200 to 3,500 plays) |
| `data/reels_raw_2026-11-11.json` | The same 591 Reels as read from the page, before dates were added |
| `data/info_2026-11-11.json` | Full caption, duration, audio type and counts for the 34 (the video links were removed after download, so `src/pipeline.py` only reruns on the local videos) |
| `data/coded.json` | My coding per Reel: hook text on screen, hook type and family, husband central, speech, caption CTA, ratios (written by `src/coded_reels.py`) |
| `data/posts_info_2026-11-11.json` | 9 carousels (her biggest + the 8 newest): slides, likes, comments, caption |
| `data/comments_sample_2026-11-11.json` | First comment page of 11 Reels, handles masked (local only, `.gitignore`) |
| `src/pipeline.py`, `src/frames_rev.py` | Download from the info links, 0 to 6 s hook sheet, 1 frame every 2 s strip, Whisper |
| `src/minisheets.py` | 4 frames per Reel, 4 Reels per image, for reading hooks |
| `src/coded_reels.py` | The coding table and the counts used in the report |

## Rerun the counts

```bash
cd research/adar-motherhood
python3 src/coded_reels.py
```

Collected once, read only, from Yarin's signed-in session in the built-in browser (Reels tab query, then `/api/v1/media/<id>/info/` and the first comment page). Instagram's terms forbid automated collection without permission, so do not schedule it.
