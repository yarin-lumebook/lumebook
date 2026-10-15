# Production run

Generated files land in `generated-assets/`, rejected attempts in `generated-assets/rejected/`, the run log in `generated-assets/generation-log.jsonl` (endpoint, request id, seconds, estimated cost, never the key), and the resume point in `state.json`.

FAL_KEY is read from the environment only. It lives in `~/.zshrc`, so run the commands through `zsh -ic` and never paste the key into a file.

## 1 · Reference image (after explicit approval of APPROVAL.md)

```bash
zsh -ic 'python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-11-kid-2 run character-reference --max-usd 1.43'
```

Inspect `generated-assets/character-reference.png` at full size, then record the result:

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-11-kid-2 qa character-reference pass
```

## 2 · The slide scenes

```bash
zsh -ic 'python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-11-kid-2 run --max-usd 1.43'
```

Already finished jobs are skipped, so the same command resumes after a failure.
Inspect every slide at full size and record `qa slide-0N pass` or `qa slide-0N fail --note "what is wrong"`.

## 3 · Replace only failed slides

```bash
zsh -ic 'python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-11-kid-2 replace slide-04 --note "five fingers on each hand, no letters on the book" --max-usd 1.43'
```

Each image can be replaced 2 times. After that the runner stops and asks for direction.

## 4 · Final composition

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/compose_slides.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-11-kid-2
```

No logo and no product card by default, because the carousel does not name the brand. `--preview-card` adds an unbranded `real-assets/preview.png` on slide 7; `--brand-mark` adds the logo.

This writes `final/slides.html` (editable), `final/01.png` to `final/08.png` at 1080 x 1350, `final/contact-sheet.png`, `final/rtl-check.png`, `final/caption.txt`, `final/sources.md` and the ZIP.

Status at any time: `python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-11-kid-2 status`
