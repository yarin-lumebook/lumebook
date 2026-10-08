# Production mode, step by step

Only after Yarin names one option ("produce kid-2").

**Standing approval (Yarin, 8 Oct 2026): up to $0.50 per carousel.** Naming the option is the go-ahead to spend up to $0.50 on that carousel without asking again. Pass `--max-usd 0.5` (the runner counts everything already logged for the run). A full run is about $0.475, so a replacement usually does not fit: if an image fails QA and fixing it would pass $0.50, finish everything else and ask in the single review message. Anything above $0.50 always needs a new yes in chat.

Scripts live in `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/`.

## 1 · Freeze and prepare (free)

```bash
python3 carousel/carousel-pipeline/scripts/prepare_fal_jobs.py carousel/carousel-pipeline/drafts/DATE/pack.json kid-2
```

- Validates the pack again, then writes `carousel/carousel-pipeline/approved/DATE-kid-2/` with `approved.json`, `jobs.json`, `state.json`, `APPROVAL.md`, `README.md`
- Checks every job against the endpoint snapshot in `scripts/fal_endpoints.json` (required fields, quality enum, size multiples of 16, pixel limits, 4:5)
- Marks the option as selected in `history.json` (feeds the "hook family at most twice in 7 days" rule)
- Rerunning is safe. If the frozen copy differs from the pack, it stops; `--refreeze` archives the old run to `versions/vN/`

If the snapshot date in `fal_endpoints.json` is older than 30 days, refresh it first with the fal MCP (`get_model_schema` and `get_pricing` are free) or the model pages.

If Yarin edited the copy, update the pack (or a copy of it), validate, then prepare with `--refreeze`.

## 2 · Approval

Covered by the standing $0.50 approval: do not stop to ask. Check `fal_generate.py RUN_DIR plan` is at or under $0.50 and go on. If the plan is over $0.50 (for example a price change), show `APPROVAL.md` and ask before any call.

## 3 · Reference, then all slides in parallel (no stop in between)

```bash
zsh -ic 'python3 carousel/carousel-pipeline/scripts/fal_generate.py RUN_DIR run --max-usd 0.5'          # makes the reference and stops
```

Open `generated-assets/character-reference.png` at full size yourself. Check: face and hands natural, age and wardrobe match the anchor, no letters or logos, feature-film 3D animated look (fail anything photo-real). If it passes, record it and go straight on; do not show it to Yarin first (the style is settled):

```bash
python3 carousel/carousel-pipeline/scripts/fal_generate.py RUN_DIR qa character-reference pass
zsh -ic 'python3 carousel/carousel-pipeline/scripts/fal_generate.py RUN_DIR run --max-usd 0.5'          # all 7 slides at once
```

The slides run in parallel (`--workers 7` by default; fal queues anything over the account's limit and never rejects it). The batch is checked against the cap before the first call, and one failed slide never stops the others; rerun the same command to resume.

## 4 · Visual QA of the seven slides

Inspect each `slide-0N.png` at full size: the same child and parent as the reference, hands, faces, anatomy, accidental words or letters, an empty text zone, who is in the scene versus what the copy says (no parents in a scene the copy says they left), duplicated props, continuity. Record `qa slide-0N pass` or `qa slide-0N fail --note "..."`.

Replace a failure only if it fits under the cap:

```bash
zsh -ic 'python3 carousel/carousel-pipeline/scripts/fal_generate.py RUN_DIR replace slide-04 --note "the parents are not in this scene" --max-usd 0.5'
```

If it does not fit, mark it pass-pending in your notes, export anyway and ask in the review message. After two failed replacements of the same image the runner refuses.

## 5 · Slide 7 has no product asset

The carousel never names the brand or a book, so the last slide is the generated picture-book scene under the story line and the CTA. If Yarin wants a real image there, it must show no brand name or logo; save it as `RUN_DIR/real-assets/preview.png` and add `--preview-card` in step 6.

## 6 · Compose and export

```bash
python3 carousel/carousel-pipeline/scripts/compose_slides.py RUN_DIR
```

It refuses to run until all seven slides passed QA. No logo and no product card by default (`--brand-mark` and `--preview-card` turn them on). It writes `final/slides.html` (editable), `final/01.png` to `08.png` at 1080 x 1350, `contact-sheet.png`, `rtl-check.png`, `rtl-report.json`, `caption.txt`, `sources.md`, `alt-text.txt` and the ZIP. It exits 1 if any text block is not RTL, overflows, or cannot fit at the readable floor (headline 56px, body 44px).

Open `contact-sheet.png` and `rtl-check.png` with Read and look: numerals, quotes and question marks must sit in the right place.

## 7 · One review message

Send Yarin one message: the contact sheet (SendUserFile), the ZIP path, the spend, and a short list of every image with a problem (slide number, what is wrong, whether fixing fits under $0.50). Ask everything in that one message. Never send images or questions one by one.

## Text changes after export (about 10 seconds, no cost)

When Yarin asks to change words on a produced carousel, run one command per change; do not hand-edit the pack, refreeze or compose yourself:

```bash
python3 carousel/carousel-pipeline/scripts/edit_final.py RUN_DIR --slide 1 --headline "שורה 1\nשורה 2" --body "..."
python3 carousel/carousel-pipeline/scripts/edit_final.py RUN_DIR --caption "..."   # or --cta '...' (quotes around the code word are added)
```

It saves through the review editor (backup, voice log, validation), re-freezes keeping the images, and re-exports only the changed slides. Then show the changed slide.

To change wording after export: edit `final/slides.html` or the frozen copy, then rerun compose (`--slides 3 5` re-exports only those).

## Posting reminders for Yarin (not automated)

- Never mention AI anywhere: not on slides, in the caption, alt text or comments (Yarin, 8 Oct 2026). The validator blocks it in copy
- Set the Meta Business Suite comment automation for the code word before posting
- Paste `alt-text.txt` lines into each slide's alt text
