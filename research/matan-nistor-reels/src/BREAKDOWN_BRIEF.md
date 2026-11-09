# Breakdown brief

Write an annotated breakdown of one Instagram Reel by @matan.nistor (Hebrew), for a social media manager who wants to learn the craft. Map time to what happens, so a reader can rebuild the Reel's skeleton without watching it.

## Inputs per Reel CODE (all under /Users/yarinbruner/Claude/Projects/Lumebook/)

- `research/matan-nistor-reels/src/coded/CODE.json`: the coded record (start here: opening, shots, edits, text, story, engagement, conversion)
- `research/matan-nistor-reels/src/dossiers/CODE.json`: metrics, caption, sampled comments
- `media/projects/2026-11-09-matan-nistor-reels/analysis/CODE/whisper.srt`: Hebrew machine transcript with timestamps (first 120 s; mishears words). If missing, check every 2 minutes for up to 15 minutes; if still missing, use the burned-in captions and say so.
- `media/projects/2026-11-09-matan-nistor-reels/analysis/CODE/hook_NN.jpg` (0 to 5 s at 4 fps) and `sheet_NN.jpg` (1 frame per second; 1.5 s or more for long Reels), `index.json` (cuts, loudness per 0.5 s: about -90 silence, -30 to -12 speech or music)

Open the hook sheets and every contact sheet once, in order. Images are expensive: do not reopen one unless it came back as "media removed".

## Output

Write `research/matan-nistor-reels/src/breakdowns/CODE.md` (for a pair, the brief names one file). Markdown, this shape:

```
### <short English title>: <one-line what it is>

[CODE](https://www.instagram.com/reel/CODE/) · rank N of 100 (or "comparison for CODE") · posted DD / MM / YYYY · NN s · views N · likes N · comments N · shares N (or "not comparable", before Nov 2024) · N x the median of his Reels that month

**Why it is here:** one line (what it teaches).

| Time | Picture | Edit | Text on screen | Audio | Likely function |
|---|---|---|---|---|---|
| 0:00-0:01 | ... | ... | exact Hebrew, short | speech (machine transcript, short) or music evidence | interpretation |

(6 to 14 rows; one per beat, not per second. Times from frame labels or the transcript; write "about" between frames.)

**What carries it (interpretation):** 2 to 4 bullets tied to rows above.
**Friction (interpretation):** 1 to 3 bullets.
**Engagement and next step (observed):** prompts, CTA timing, what the sampled comments do (with the sample caveat), creator replies.
**For LumeBook:** what principle transfers, and what must not be copied (third-party footage, identifiable bystanders, his persona, money handouts, anything about price).
```

Rules: quote Hebrew exactly as on screen, max 12 words per quote; summarise speech, never paste the transcript. Mark interpretation as interpretation. You cannot hear: music only with evidence (licensed track in the dossier `music`, lyrics in the transcript, steady loudness without speech); sound effects "not determinable". Never invent a shot, line or reaction. No em dashes. Dates as DD / MM / YYYY. Metrics: copy from the dossier (`views_grid`, `likes`, `comments`, `shares`, and `views_vs_month_median` from `research/matan-nistor-reels/data/reels.csv`).
