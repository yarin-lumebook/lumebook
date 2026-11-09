# Transcript check pass (text only)

Many Reels were coded before their Whisper transcript existed (`evidence.transcript: "pending"`), so their speech fields came from burned-in captions sampled once a second. This pass compares each such coded file with its transcript and fixes only what the transcript changes. No images are needed; do not change any visual, text-on-screen, edit or metrics field.

## Inputs per Reel CODE

- `research/matan-nistor-reels/src/coded/CODE.json` (the coded record)
- `media/projects/2026-11-09-matan-nistor-reels/analysis/CODE/whisper.srt` (Whisper turbo, Hebrew, timestamps; first 120 s only; mishears words, may print song lyrics as speech or "תודה רבה" on music)

## What to check and fix

1. `opening.spoken_hook`, `opening.s0_1`, `opening.s1_3`, `opening.s3_5`: the speech parts. Add the spoken words with timestamps if missing; correct the timing if the transcript shows speech starts later or earlier. Keep on-screen text quotes as they are (captions are more exact for spelling).
2. `opening.first_sentence_standalone`, `opening.number_or_money_in_first_3s`, `opening.topic_clear_at_s`, `opening.payoff_promised_at_s`: change only if the transcript shows something the captions missed (for example a spoken number at 1.5 s that never appeared on screen).
3. `sound.speech`, `sound.delivery`, `sound.music`, `sound.sync`: speech present or not, pace, pauses; "music likely" if the transcript prints lyrics.
4. `story.*` and `standout_moments`: only if the transcript reveals a step, reveal or payoff the captions missed.
5. `engagement.explicit_prompts` and `conversion.next_action`, `conversion.cta_timing`: add a spoken CTA (for example "תגיבו אני" said at 52 s) that the captions missed, with where = "video".
6. Set `evidence.transcript` to good, partial, poor, "music only" or "none (no speech)", and append to `evidence.limits`: "Speech fields checked against the transcript on 09 Nov 2026 (text-only pass)."

Never invent: if the transcript is garbled at a point, say "transcript unclear at N s" rather than guessing. Quotes stay short (max 12 words) and are marked as machine transcript. No em dashes.

## Log

Append one object per Reel to `research/matan-nistor-reels/src/transcript_check_log.jsonl`: `{"code": "...", "transcript": "good|partial|poor|music only|none", "changed": ["field path: old -> new (short)"], "notes": "..."}`. Write `"changed": []` when nothing needed fixing.

Validate each JSON file with `python3 -m json.tool FILE > /dev/null` after editing.
