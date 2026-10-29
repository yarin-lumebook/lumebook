# Lotem-format carousels (29 Oct 2026)

Five kid carousels built on the structure that works for @lotem_lerner (`research/lotem-lerner-carousels/README.md`), kept inside LumeBook's standing carousel rules.

| Option | Topic (best-selling book) | Child | Talks to |
|---|---|---|---|
| lotem-1 | new-sibling-jealousy (2 אח חדש) | איתי, 3.5 | both parents |
| lotem-2 | pacifier-weaning (41 ביי ביי מוצץ) | מאיה, 3 | mom |
| lotem-3 | potty-start (43 נפרדים מהטיטולים) | נועם, 2.5 | both parents |
| lotem-4 | birthday-expectations (15 יום הולדת) | תמר, 4 | mom |
| lotem-5 | first-grade-decompression (10 שלום כיתה א׳) | יונתן, 6 | both parents |

What is taken from Lotem: a "what I'm really trying to tell you" cover, 12 slides, 8 numbered behaviours, each point slide in three parts (the behaviour in the child's words / "בעצם..." / "מה יעזור לי: ..."). What stays ours: the child's voice to the parents everywhere, one picture behind all slides, no brand, the save CTA (no comment keyword), no dad without mom, the 24 Oct punctuation rule.

Not run through `validate_pack.py` (it expects 10 slides, a hook slate and claims). Copy passed `voice_lint.py` apart from the CTA and caption checks, which do not fit a loose file. The "בעצם" and "מה יעזור לי" lines rest on the sources the November packs already checked for these topics (listed in each option and in `runs/<id>/final/sources.md`).

## Version 2: her text look and a picture per slide (29 Oct 2026, evening)

Yarin: "design the text like her but in lumebooks design system, change the font to the websites font", then "create a different image for each slide like her as well".

- Pictures: slide 1 keeps `pictures/<id>.png`; slides 2 to 12 are `pictures/<id>/NN.png`, one scene each (`scenes.json`), made in ChatGPT with the cover picture uploaded as the character reference, one chat per option.
- Text: `render.py` writes `runs/<id>/final-v2/`. Her treatment (light type on a dimmed picture, a big cover line with one pill under it, a small label above each part of a point slide) in the site's palette: ink #0B0518 veil, cream #F8F0E1 type, gold #E6B762 for the number badge, the cover pill, the labels "בעצם" and "מה יעזור לי:" and the save button; spoken lines in soft gold #F3D9A1. Font: Varela Round, the font lumebook.com sets for its body and headings (`--font-body` in the site's CSS), from the files the site serves (`shared/brand/fonts/VarelaRound-*.woff2`). It has one weight, so headlines get a thin stroke in their own colour to read heavier.
- No logo, handle or swipe arrow (no brand on carousels; she has no arrow). `final/` keeps version 1 (one picture, clean look) for comparison.

## Version 3: more text, linked slides, varied shapes (29 Oct 2026, late evening)

Yarin: "i feel like theres too little text so the slides are not coherent enough and the format is too repetitive". Copy in `copy-long.json` (merged into `options.json`; the short copy is kept in `options-short.json`), rendered to `runs/<id>/final-v3/`, same pictures.

- Like her top post (DaK3TJUDNY0): slide 2 sets up the story ("אמא ואבא, בטח שמתם לב"), each point is a short inner monologue of 25 to 45 words under a small numbered tag ("1: פתאום אני קטן"), slide 11 turns back to the parents.
- Five shapes alternate so no two neighbours look alike: monologue, short beats on their own lines, "מה אתם רואים / מה קורה לי בפנים", a sentence to say on a cream card, and the parents' question as the headline.
- Markup in the copy: `## ` gold label, `> ` card, `**x**` gold emphasis, blank line a gap. Lines are broken by hand (no automatic wrapping), the type shrinks only when a line is still too wide.
- Over the 25 words a slide that `voice_lint.py` allows, on purpose; every other voice rule passes. The "בעצם" meanings and "מה יעזור לי" actions are unchanged from the checked copy; added lines are the child's feelings only.

## Version 4: five structures, no list of 8 (29 Oct 2026, night)

Yarin: "why is it always 8 things? why always lists?", then "Yes, five structures". The 8 was my habit, the list came from Carousel Machine's numbered-examples rule; her own lists run 3 to 11 points and her top post is mostly story. Copy in `copy-structures.json` (merged into `options.json`; version 3 kept in `options-lists.json`), rendered to `runs/<id>/final-v4/`. Every slide names its picture (`picture`, a path under `pictures/`).

| Option | Structure | Slides | How it reads |
|---|---|---|---|
| lotem-1 | before and after | 12 | "פעם" (2 new pictures: bedtime story, proud on the potty), "ואז" she arrives, "ומאז" what changed, then what brings back "פעם" |
| lotem-2 | a letter | 11 | "אמא שלי," on a cream sheet in ink across the slides, signed "אוהבת, מאיה" |
| lotem-3 | your thoughts, my answers | 12 | each slide opens with "אתם חושבים:" and a parent's thought in quotes, the child answers |
| lotem-4 | one minute, slowed down | 10 | the birthday song second by second (5 new pictures: lights off, the cake, her face, mom's lap, blowing the candles together), then the evening |
| lotem-5 | one day | 12 | time tags from 08:00 in class to 20:00 in bed, all from the existing pictures |

Voice lint: only the 25-word cap (on purpose) and «תמיד» in the sentence the parents say to the child. The "מה יעזור לי" actions are the checked ones; the stories are the child's imagined voice.

## Files

- `options.json`: the copy, anchors and picture briefs (edit here)
- `prompts.json`, `prompt-*.txt`: the picture prompts (pipeline builder for lotem-1, a shorter version of the same for 2 to 5)
- `pictures/`: the five pictures, made in ChatGPT (Chrome, Yarin's account) on 29 Oct 2026, no fal spend
- `make_runs.py [id ...]`: writes `runs/<id>/` (approved.json, state.json, the picture) and renders with `carousel/carousel-pipeline/scripts/compose_slides.py --look clean`
- `runs/<id>/final/`: 12 PNGs at 1080 x 1350, contact sheet, caption, sources, ZIP (version 1)
- `scenes.json`, `render.py [id ...]`, `runs/<id>/final-v2/`: version 2 (above); `fit-report.json` there shows the type size each slide got and that the font loaded

Not copied to Drive and not in Postiz: these are options for Yarin to choose from.
