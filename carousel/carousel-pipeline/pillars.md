# Content pillars

Every nightly pack has two pillars with three options each. They must read as two different series at a glance in the feed, so each has its own colour, typeface, slide layout and photo direction. Source of truth for the values: `PILLARS` in `scripts/carousel_lib.py`. The renderer (`compose_slides.py`), the review page (`create_review.py`) and the image prompts (`compose_image_prompt`) all read from it.

**Slides (both pillars, since 8 Oct 2026):** Yarin asked for "the same method as the last carousel" (`carousel/fal-carousel-trial/source/flare_carousel.py`): centred Heebo Black straight on the picture's plain wall, a soft cream veil (dark ink) or a dark veil (cream ink) on the evening and last slides, no boxes or chips, the art pushed down until the characters start 60px under the text, a cream arrow circle at the bottom centre, no AI label. The pillars differ in the copy, the photo direction and the review page, not in the slide layout.

| | הילד מספר (kid) | גישה מקצועית (expert) |
|---|---|---|
| Purpose | The child says in first person what they feel, so the parent recognises the moment | A clear tip to try tomorrow, every tip leans on a source |
| Voice | Short spoken lines, "אני", feelings before explanations | Calm, direct, numbered steps, a source on every solution slide |
| Review page colour | violet `#5B2BD6`, deep `#3B1D78` (plum), Rubik headlines, bubble-shaped cards | gold `#A8741F`, ink `#1D1039`, Heebo headlines, gold rule on cards |
| Photo direction | Child's eye level or lower, close, parent partly in frame, soft violet cast | Adult eye level, medium to wide, both in frame, negative space, muted gold daylight |

Both pillars keep the shared rules: 7 slides, no brand, named child, mom or both parents, the comment CTA only on the last slide.
