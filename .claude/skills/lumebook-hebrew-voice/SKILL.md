---
name: lumebook-hebrew-voice
description: Yarin's everyday Israeli Hebrew voice for LumeBook audience copy, with the hard punctuation and RTL rules and a deterministic lint. Use it whenever you write or rewrite Hebrew that parents will read for LumeBook (carousel slides, Instagram captions, CTAs, comment replies, text on a design), whenever the lumebook-carousel skill drafts copy, and whenever someone says the Hebrew sounds translated, too polished, like a therapist or not like Yarin, even if they never mention a skill.
---

# LumeBook Hebrew voice

This skill decides how LumeBook's Hebrew sounds. It does not decide what a carousel says; the lumebook-carousel skill and the playbook do that.

The highest priority is Hebrew that sounds like Yarin talking to another parent: natural, everyday, Israeli. Not translated English, not a therapist, not a parenting guru, not brand copy.

## 1 · Check the calibration status first

```bash
python3 carousel/carousel-pipeline/scripts/nightly.py voice
```

- `fallback` (fewer than 15 approved samples): write in the documented fallback voice in `references/fallback-voice.md`, and say so wherever the copy is shown (the nightly pack has a `voice` field and the review page shows a badge). Never describe fallback copy as "in Yarin's voice"; it is a careful guess at it.
- `calibrated` (15 or more): read every file in `examples/approved/` and `references/voice-summary.md`, then write. Read `examples/rejected/` too, because it shows what Yarin pushed back on.

Samples count from three places: files in `examples/approved/`, fenced `text` blocks under "Writing samples" in `carousel/carousel-pipeline/voice-profile.md`, and Yarin's rewrites from the review page (`examples/edits.jsonl`, kind `rewrite`). The count comes from the script, never from memory.

## 2 · Hard rules (the build fails on these)

Audience facing Hebrew is everything a parent reads: slide headline and body, caption, CTA, comment code word, and any text placed on a design.

- No dash of any kind (em dash, en dash), no semicolon and no hyphen (also the maqaf ־), nor their lookalikes (Yarin, 24 Oct 2026: "lets bring back punctuation marks except em dashes, semicolon and hyphens"). Periods, commas, question and exclamation marks, colons and quotation marks are fine where a person would type them. For a prefix on a number write it apart or in words: ועוד 8, בשעה 17:40, 3 עד 6. Carousel packs written before that evening keep the old rule (no period or comma either)
- One thought per line, at most 12 words per line
- Hook main line up to 8 words, hook slide up to 12 words in total
- Regular slide up to 25 words, CTA slide up to 18 words
- No jargon or diagnosis words (חרדה, הפרעה, טראומה, ויסות, טריגר and similar). Say חשש, פחד, קשה לו
- No guarantee or fake certainty (מוכח, בלי דמעות, ייעלם, פותר, 100%)
- Never claim every child feels the same (כל הילדים, כל ילד). Use הרבה ילדים, יש ילדים, זה מוכר
- No guilt, no scare tactics, no slogans
- Carousels talk to mom (feminine singular) or both parents (plural), never to dad, about one named Israeli child from carousel/carousel-pipeline/names.md
- Carousels (slides, caption, CTA) never name the brand or a book title. A book where the child is the hero is hinted at as one possible tool. Since the evening of 24 Oct 2026 the carousel CTA asks to save the post for the next time the topic's situation comes up, always said about the child, short and everyday, never a scene (תשמרי את הפוסט / לפעם הבאה שהיא מפחדת מרעמים; to both parents תשמרו), with no story line, send line or comment word; older carousels used the save and share CTA or the comment CTA. In other copy the Hebrew spelling is לומבוק, never לומיבוק (the website still uses the yod spelling)

Line breaks still carry the rhythm: on a slide each line is read as one spoken beat, so punctuation is there to help the reader, not to fill every line. An em dash is the most visible sign of machine written Hebrew.

When a line fails, rewrite the line. Do not delete the character and hope.

- "זה טבעי — וזה עובר" becomes "זה מוכר, וזה עובר לאט"
- "ו-8 דברים שעוזרים" becomes "ועוד 8 דברים שעוזרים"

## 3 · How the voice sounds

Read `references/fallback-voice.md` for the full description with good and bad pairs. In short:

- Spoken words. If you would not say it out loud to a friend at the playground, rewrite it
- Concrete moments: a time, a place, an object, a sentence a child really says. "7:40 ביד על השער" beats "רגעי הפרידה"
- Parents are addressed as mom (את, כתבי) or both parents (אתם, כתבו), set per carousel; never dad
- Verbs before nouns. "קשה לו להיפרד" not "קושי בפרידה"
- Warm and direct, a little dry, never sugary. Humour only when it is light and kind
- Uncertainty is said plainly: "לפעמים", "אצל הרבה ילדים", "יכול להיות ש"
- Never: "חשוב לזכור", "בואו נדבר על", "המסע", "קסם", "להעצים", "חוסן", "להכיל", "לתקף", "מרחב בטוח", "בסופו של יום", "הנה הדבר", "מה שאף אחד לא מספר לכם"
- One exception since 10 Oct 2026 (Carousel Machine): on a carousel cover only, the hook bank's loud formulas may use "מה שלא מספרים לך" and "תפסיקי" about one action, when the carousel pays them off. In body lines and captions the list above still holds

### Child narrator (kid direction)

The child talks to the parents about what the moment feels like from the inside. It is an imagined inner voice, not a quote of a real child, so it never pretends to be a testimonial.

- First person, present tense, short. Age 3 to 6 logic, no baby talk and no adult words (רגשות, צרכים, ביטחון, גבולות)
- One feeling per line, tied to something physical: the gate, the bag, the smell of the coat
- Shows the need behind the behaviour in the child's own words ("אני נצמד כי אני לא בטוח מתי את חוזרת")
- Never manipulative cuteness, never "Mommy I'm sad" melodrama, never guilt toward the parent
- Never claims all children feel this way. The parent should think "maybe that's him", not "that's every child"

### Expert narrator (expert direction)

A calm, plain-language take on one idea that a real source supports.

- One sourced idea per slide, explained in words a tired parent understands at 22:00
- Name the organisation when it helps ("לפי האקדמיה האמריקאית לרפואת ילדים"). No invented persona, no "ד״ר" or "פסיכולוגית מסבירה" unless a real, verifiable person said exactly that
- Give one thing to try tomorrow morning
- Separate what the source says from LumeBook's wording. The source supports the fact; the line about the book is ours

### Reel scripts (Yarin speaking)

Before writing or rewriting any reel script (voiceover, hook, cards), read `references/reel-scripts.md` (since 09 / 11 / 2026): a person and a moment are the subject, never the book; call out one person, answer a real question, a doubt and then the turn, point at what is on screen, count when explaining, one ask. Evidence: `research/israeli-product-reels/ugc-seller-scripts.md`. Its second part (same date, from `research/matan-nistor-reels/`) sets the structure: something happens on screen, this reel's cover or number in the first frame, a new owned picture for every line, the payoff named in `payoff` and kept on screen until the לומי card.

### Facts belong to sources, in every narrator

Voice is not a licence to add facts. A hedge like "הרבה פעמים" or "יש ילדים ש... ויש כאלה ש..." is still a claim about children. If the brief or a source you were given does not support it, either cut the line or turn it into a possibility about this one child ("יכול להיות שאצלו זה פחות קשור לצמא"), never an invented personal story, and in a nightly pack list every general statement in `claims` with its source. When rewriting someone else's draft, do not add facts it did not contain and do not promise content that is not there ("אספנו פה 3 דברים").

## 4 · Workflow for any piece of copy

1. Draft line by line, out loud in your head
2. Self review against `references/rubric.md` (sounds spoken, natural Israeli, narrator kept, one idea per line, no fake certainty)
3. Run the lint on loose copy:
   ```bash
   python3 carousel/carousel-pipeline/scripts/voice_lint.py FILE.json      # {"field name": "Hebrew text", ...}
   python3 carousel/carousel-pipeline/scripts/voice_lint.py FILE.json --cta cta --code-word גן
   python3 carousel/carousel-pipeline/scripts/voice_lint.py FILE.json --cta cta --addressee mom   # the save and share CTA (since 24 Oct 2026, no code word)
   ```
   For a full nightly pack use `validate_pack.py`, which applies the same rules plus structure
4. Rewrite every failed line and lint again until it passes. Warnings are for judgement: read the line and decide

## 5 · Learning from Yarin's edits (do this every time)

Every time Yarin edits copy on the review page and saves, the editor logs the change to `examples/edits.jsonl`: the line before, the line after, the field, the slide's role, the addressee and a `kind`:

- `rewrite`: at least half of the words are Yarin's (and 3+ words). These are Yarin's own writing and count toward the 15 calibration samples
- `tweak`: a few words changed. A strong signal of what Yarin does not like
- `line_breaks`: same words, different line splits. Shows how Yarin breaks lines

Before writing anything, read the recent edits (`nightly.py start` prints the last 30 as `recent_voice_edits_learn_from_these`; the full log is `examples/edits.jsonl`). For each pair ask: what was cut, what was added, how were the lines split, which words were replaced and with what, did it get shorter, plainer, warmer, more direct? Write tonight's copy the way the "after" lines sound. Learn the pattern; do not copy Yarin's lines into new carousels, and never undo one of Yarin's changes (if a word was cut, do not bring it back elsewhere).

When the log grows, update `references/voice-summary.md` with the patterns you see (with two or three before and after examples each), so the next run starts from them.

## 6 · Other samples from Yarin

- Approved samples go in `examples/approved/`, one file per sample, using `examples/approved/README.md`
- Rejected or heavily edited copy goes in `examples/rejected/` with the reason, using `examples/rejected/README.md`
- At 15 approved samples, write `references/voice-summary.md` (the dimensions are listed in `carousel/carousel-pipeline/voice-profile.md`) and the status switches to calibrated automatically
- Never imitate spelling mistakes and never reuse private facts from a sample
