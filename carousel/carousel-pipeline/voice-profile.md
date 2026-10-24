# Yarin voice profile

## Status

The hard rules are active and enforced by `scripts/validate_pack.py` and `scripts/voice_lint.py`.

The personal voice is **not calibrated**. Calibration needs at least 15 authentic samples of Yarin's own writing (approved examples, pasted samples, or rewrites made on the review page); there were 0 on 7 Oct 2026. Check the live count with:

```bash
python3 carousel/carousel-pipeline/scripts/nightly.py voice
```

Until then every pack uses the documented fallback voice in `.claude/skills/lumebook-hebrew-voice/references/fallback-voice.md`, and the pack and review page say "fallback". The validator fails any pack that claims to be calibrated with fewer than 15 samples.

## Learning from edits

The easiest way to calibrate: edit the copy on the review page (`python3 carousel/carousel-pipeline/scripts/review_server.py`). Every save logs the before and after of each changed line to `.claude/skills/lumebook-hebrew-voice/examples/edits.jsonl`. A rewrite where at least half of the words are yours counts as one sample; small tweaks and line-break changes are kept as style signals. The nightly writer reads the recent edits before writing.

## Where samples go

Preferred: one file per sample in `.claude/skills/lumebook-hebrew-voice/examples/approved/` (template in that folder's README). Rejected or rewritten copy, with the reason, goes in `examples/rejected/`.

Quick alternative: paste samples below under "Writing samples", one fenced `text` block each. Both places are counted.

Good samples are WhatsApp messages, captions, voice note transcripts and emails written without heavy editing. Remove private names, phone numbers and sensitive family details first. The writer does not imitate spelling mistakes or reuse personal facts.

## Hard rules

<div dir="rtl">

- עברית יומיומית שנשמעת כמו בן אדם שמדבר
- משפטים קצרים
- רעיון אחד בכל שורה
- בלי מקף ארוך, בלי מקף ובלי נקודה פסיק (מ־24 באוקטובר 2026 בערב נקודה, פסיק, סימן שאלה, סימן קריאה ונקודתיים מותרים כשזה טבעי)
- בלי ז׳רגון ובלי אבחנות
- בלי קלישאות של הורות
- בלי טון של גורו
- בלי סלוגנים
- בלי להפחיד הורים
- בלי לגרום להורה להרגיש אשם
- בלי הבטחות ובלי ודאות מזויפת
- בלי מילים גבוהות כשיש מילה פשוטה
- בלי לכתוב שכל הילדים מרגישים אותו דבר
- המוצר נכנס רק כשהוא באמת ממשיך את הרעיון
- לומבוק בלי יו״ד

</div>

## Voice dimensions to infer from samples

When 15 samples exist, summarise these in `.claude/skills/lumebook-hebrew-voice/references/voice-summary.md` before writing:

- how direct or soft the opening is
- typical sentence length
- favourite everyday connectors
- amount of humour
- how emotion is named
- how disagreement is expressed
- how calls to action sound
- words or phrases that never sound natural for Yarin

## Writing samples

Paste samples below. Keep each sample in its own fenced block and label the context above it.

### Sample template

Context

```text
Paste the exact message here
```
