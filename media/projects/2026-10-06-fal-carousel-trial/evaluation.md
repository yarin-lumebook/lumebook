# Evaluation: is fal.ai a good production partner for LumeBook carousels?

Trial run 6 Oct 2026. One seven-slide carousel ("a new sibling") produced end to end, twice: first an illustrated version, then, after the user chose the website-like look, a photo-real version (the delivered one). Model: Nano Banana 2 on fal.ai (`fal-ai/nano-banana-2` and `/edit`); Flux Schnell was used only for four cheap style drafts. Spend: 21 delivered generations, $1.37 (about $1.45 if fal billed one rejected request). The cap was $1.25; the user raised it to $1.40 after the style tests. Details in [prompts/generation-prompts.md](prompts/generation-prompts.md).

## Verdict

**Good fit with limitations**

The images are good enough to publish, consistent from one reference, fast and cheap. Model quality is not the limitation. Reliability is: the tool connection, an unexplained content rejection, and three of the 21 images needing a fix a careless reviewer could ship (an extra leg, a floor colour shift introduced by the repair, a flat slab pasted over a photo's sky). That makes fal.ai a good engine for a weekly carousel only if a person checks every image at full size and the layout stays in code, as it does here.

## Scores (final photo-real carousel)

| Criterion | Score | Evidence from this trial |
|---|---|---|
| Overall visual sophistication | 8 | Natural window light, believable skin and fabric, calm compositions; the light-to-dark change on slides 6 and 7 gives the carousel an arc (contact-sheet.png). It is clean "good family photography", not a signature look, and 1K output (928×1152) is upscaled about 1.17× to 1080×1350. |
| Emotional believability | 9 | The beats read without any copy: uncertain (1), held (2), watching the baby (3), walking together (4), curled up and safe (5), absorbed in a book (6), proud (7). The mother's face is natural in every scene. |
| Character consistency | 9 | From one reference photo, the boy's face, hair, plum sweater with cream collar and trousers, the mother's face, bun and linen shirt, and the grey rabbit held across six edits. Small drift: the crib's colour and shape change between slides 1, 3 and 7, and the boy reads about 5 to 7, older than the 4 in the prompt. |
| Prompt adherence | 7 | "No text" was obeyed in all 21 images, including on the open book pages. Misses: slide 4's photo had a flat wall-coloured slab pasted over the top third; slide 3's reference photo has a curtain and lamp in the text zone; slide 6 crops the mother at the frame edge; the book on slide 7 is a plain white block. |
| Negative space for typography | 7 | Four of six edits left a clean top 45%. Slides 1, 2, 3 and 6 needed the photo pushed down 80 to 170px in code (the plain wall is mirrored above it), and slide 3 needed a veil. No image needed regenerating for space, but none came out exactly as asked. |
| Brand fit for LumeBook | 7 | The user chose this direction themselves after seeing four looks. It is close to the website's warm, glowing photo tiles and the plum and gold palette, but the site's hero covers are glossy 3D cartoons, so it is not a copy of any one site style. The brief's rule against stock-photo and fake-photo looks was waived; the AI label stays. |
| Speed | 9 | 13.7 to 18.1 seconds per Nano Banana 2 image end to end, including upload of the reference and download; Schnell drafts took about 5 seconds. Six slides generated in parallel in under 20 seconds. |
| Cost | 9 | $0.08 per Nano Banana 2 image, about $0.003 per Schnell draft. The whole trial, two complete carousels plus style tests, was $1.37. A single carousel with one repair is under $0.80. Not a 10 because a rejected request can still be billed (fal FAQ), and only the dashboard confirms it. |
| Workflow reliability | 5 | The account was blocked until credits were added (clear message, easy fix). The fal MCP server showed "Connected" in `claude mcp list`, but its tools never loaded into the Claude desktop session, so the trial called the same endpoint directly over HTTP. One prompt was rejected by the content checker with no reason given. Seeds are not echoed back, so runs cannot be reproduced exactly. Three images needed a fix. |
| Suitability for one carousel a week | 8 | With this folder as the template, a new carousel is a new reference photo, about 6 edits (under $0.60), the copy pasted into carousel.html and a QA pass. The weekly human cost is the full-size check and the layout nudges, which no model choice removes. |

## Limitations caused by the image model

- **Pasted-slab artifact.** Slide 4's photograph came back with a flat beige rectangle over the top third of the sky and a hard seam. It would have shipped if I had judged only the thumbnail. Fixed free in code (`park()` in prep_art.py), but there was no budget left to regenerate.
- **Anatomy errors still happen.** In the illustrated version, slide 2 came back with an extra leg in a matching grey sock; one targeted edit removed it ($0.08).
- **Edits drift colour outside the edited area.** That leg-removal edit turned the floor from warm to neutral grey. Fixed in code, but a reviewer has to notice it.
- **The content checker is opaque.** A gentle scene of a pregnant mother hugging her son was rejected (HTTP 422) with no explanation. Expect friction on exactly the milestones LumeBook sells: pregnancy, bath time, bedtime. A rejected request may still be billed.
- **Layout requests are approximate.** "Keep the top 45% empty" worked in spirit, not to the pixel.
- **Objects are generic.** The book on slides 6 and 7 is a generic hardcover with a blank cover and a painted page, not LumeBook's 22×22 cm softcover. Only a photograph of the real book can show the product.
- **Resolution.** The 1K tier is 928×1152, below the 1080×1350 canvas. The 2K tier was not tested.

## Limitations caused by the layout or the copy (mine, not the model's)

- **Photo-real changes the trust question.** These images look like real photographs of a real family. The brief said to avoid fake photography and fake UGC; the user waived that for style. The two AI labels on slides 1 and 7 and the playbook's rule to label AI scenes (docs/lumebook-social-strategy.html) should be backed by an AI line in the caption and Instagram's AI label. Your carousel research found that buying talk follows real children holding a real book with their name on it (research/carousel-research/lumebook-carousel-research.html); an AI family cannot do that job.
- **Slide 7 shows a blank book.** No child's name and no real LumeBook cover appear anywhere, so the carousel is built for saves and shares, not as the conversion format that research points to. A photo of the printed "אח חדש" would be stronger on slide 7.
- **The thread is subtle.** At 5.5px with a bead it reads at 25% scale (source/qa-25pct.png), but it is still a thin line against big photographs.
- **Slide 6 headline is four lines.** It reads at 25% but is the longest block; "להתאמן עליו" and "לפני שהוא מגיע" could be one tighter line.
- **Copy.** The CTA follows the playbook ("צרו תצוגה מקדימה בחינם") rather than the brief's "הצצה חינם". Kickers were removed at the user's request. All seven slides' copy is otherwise the brief's wording.
- **Unchecked claim.** I did not measure Instagram's profile-grid crop; the 92px side margins are a safe estimate.

## What I would do before publishing

1. Replace slide 7's blank book with a real photo of the printed "אח חדש", or add that photo as an eighth slide.
2. Show the carousel to one or two parents in the target audience and ask which slide they would save (untested guess: slides 3 and 5).
3. Post it with a creator who pins their personal code in the comments, the pattern your carousel research recommends, and say in the caption that the images are AI-generated.
