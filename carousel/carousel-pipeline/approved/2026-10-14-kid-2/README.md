# Production run (one picture)

The carousel has one picture that depicts the idea, shown behind all 10 slides (Yarin, 14 Oct 2026). Generated files land in `generated-assets/`, rejected attempts in `generated-assets/rejected/`, the run log in `generated-assets/generation-log.jsonl`, the resume point in `state.json`. FAL_KEY is read from the environment only (`~/.zshrc`, so run through `zsh -ic`).

## 1 · The picture

```bash
zsh -ic 'python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-14-kid-2 run picture --max-usd 0.17'
```

Inspect `generated-assets/picture.png` at full size (the child's face to the viewer, the idea readable, a clean text zone, hands, no letters), then `python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-14-kid-2 qa picture pass`, or replace it:

```bash
zsh -ic 'python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-14-kid-2 replace picture --note "what is wrong" --max-usd 0.17'
```

## 2 · Final composition

```bash
python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/compose_slides.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-14-kid-2
```

Writes `final/slides.html`, `final/01.png` to `final/10.png` at 1080 x 1350, the contact sheet, the RTL check, caption, sources and the ZIP. Status: `python3 /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/scripts/fal_generate.py /Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-14-kid-2 status`
