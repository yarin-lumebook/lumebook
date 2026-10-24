# Content pillars

Every nightly pack has two pillars with three options each. They must read as two different series at a glance in the feed, so each has its own colour, typeface, slide layout and photo direction. Source of truth for the values: `PILLARS` in `scripts/carousel_lib.py`. The renderer (`compose_slides.py`), the review page (`create_review.py`) and the image prompts (`compose_image_prompt`) all read from it.

**Slides, the bold look (both pillars, since 10 Oct 2026; Yarin: "focus heavily on click baity hooks, content and slide design"):** type first. Centred Heebo Black straight on the picture's plain wall, far larger than before (cover up to 156px, other slides up to 118px, never under 84px and 72px), which is why the copy limits are short. One phrase per slide (`highlight`) sits in a tilted colour block: violet with cream ink on kid slides, yellow with dark ink on expert slides. The body steps down to Rubik semibold. A spoken sentence in quotation marks becomes a white speech bubble. On slide 7 the comment line is a yellow button. The arrow circle takes the pillar colour. A soft cream veil (dark ink) or a dark veil (cream ink) keeps the wall quiet, no AI label. Since 24 Oct 2026 the picture is never moved or stretched (Yarin: "i dont want you to distort the images anymore"): the type is sized and, if needed, broken into one more line to fit the plain wall above the characters (README section 5). `compose_slides.py --look bold` (the default for copy with highlights).

**The classic look (8 Oct 2026)** stays available with `--look classic` and is used automatically for copy written before the bold look: the layout of `media/projects/2026-10-06-fal-carousel-trial/source/flare_carousel.py`, centred Heebo Black at up to 96px, no blocks or bubbles, a cream arrow circle.

| | הילד מספר (kid) | גישה מקצועית (expert) |
|---|---|---|
| Purpose | The child says in first person what they feel, so the parent recognises the moment | A clear tip to try tomorrow, every tip leans on a source |
| Voice | Short spoken lines, "אני", feelings before explanations | Calm, direct, numbered steps, a source on every solution slide |
| Review page colour | violet `#5B2BD6`, deep `#3B1D78` (plum), Rubik headlines, bubble-shaped cards | gold `#A8741F`, ink `#1D1039`, Heebo headlines, gold rule on cards |
| Photo direction | Child's eye level or lower, close, parent partly in frame, soft violet cast | Adult eye level, medium to wide, both in frame, negative space, muted gold daylight |

Both pillars keep the shared rules: 7 slides, no brand, named child, mom or both parents, the comment CTA only on the last slide.
