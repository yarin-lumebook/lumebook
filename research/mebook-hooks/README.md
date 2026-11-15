# MeBook's 50 best performing hooks

15 Nov 2026. Three lists of 50 hooks from MeBook's Instagram Reels, ranked by view count: on-screen text, the first spoken sentence, and the first line of the caption, plus an appendix with MeBook's 21 video ads from the Meta Ad Library. Read `mebook-hooks.md`; method notes are at its top.

| File | What it is |
|---|---|
| `mebook-hooks.md` | The three lists and the ads appendix (built by `assemble.py`; edit the inputs, not this file) |
| `hooks.json` | Every Reel and ad with its views, account, date, on-screen, spoken and caption hook, and the three top 50 lists |
| `raw/ig-reels-grid.json` | The play counts read from instagram.com/mebook.ai/reels/ on 15 Nov 2026 |
| `raw/ads.json` | The 21 video ads (Ad Library, Israel, sorted by the Library's total impressions option) and the start of each ad text |
| `work/reels-meta.json` | Caption, account and date of each Reel (from the yt-dlp info files) |
| `work/onscreen-*.json` | On-screen text read from the frame strips (`READ_BRIEF.md`), `onscreen-fixes.json` the readings checked or corrected by hand |
| `work/whisper/` | Local Hebrew transcripts of the first 12 seconds (whisper-cli turbo, greedy); `work/whisper-beam/` four re-runs with beam search |
| `work/spoken-fixes.json` | Spoken lines corrected against each Reel's own subtitles (basis per line) |
| `process.py` | `strips` makes the frame strips, `whisper` the transcripts |
| `dl.sh`, `dl-ads.sh`, `dl-ads-retry.sh` | Downloads (yt-dlp, public pages only; Facebook rate-limits ad downloads, so the retry waits 45 s between ads) |

Videos and strips live in `media/projects/2026-11-15-mebook-hooks/` (not in git).

Rebuild after a correction: `python3 assemble.py`.

Limits: views come from creators' collab audiences as much as from the hook; ads have no public numbers; transcripts can mishear Hebrew (lines not confirmed by subtitles are marked); a few word-by-word subtitles were caught mid-build and read from the transcript.
