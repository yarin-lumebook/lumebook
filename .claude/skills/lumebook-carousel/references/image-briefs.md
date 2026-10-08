# Image briefs

The image model (GPT Image 2.5 Flare on fal.ai) gets the brief only after Yarin picks an option and approves the cost. The nightly brief must already be production ready, because the review page shows the exact prompt.

## What the scripts add for you

`carousel_lib.compose_image_prompt()` builds the final English prompt from your fields and always adds:

- the option's character anchor, word for word, on every slide
- the pillar's photo direction from `PILLARS` in carousel_lib.py (see carousel/carousel-pipeline/pillars.md): kid = child's eye level, close, parent partly in frame, soft violet cast; expert = adult eye level, medium to wide, both in frame, negative space, muted gold daylight. Pick `camera` values that agree with it
- the style: feature-film 3D animated, cute stylised characters with large expressive eyes and rosy cheeks, warm cinematic light, knit and linen textures; never photo-real (Yarin rejected a photo-real reference on 8 Oct 2026)
- the palette: cream, plum and violet accents, muted gold, low saturation
- avoid: glossy ad smiles, exaggerated sadness or tears, stock poses, distorted hands
- the text zone sentence from your `text_zone`, keeping faces, hands and key objects out of it
- on the last slide: any book, tablet or phone shows only a soft storybook illustration of the same child, with no words, logos or interface, and nothing identifies a brand
- no generated words, letters, numbers, logos, watermarks, signatures, frames or UI anywhere, including on books and screens
- for the paid edit jobs: the reference lock (same child and parent, new scene)

Do not repeat these in your fields.

## What you write per slide

- `beat`: the emotional beat in a few words ("relief when the goodbye is predictable")
- `action`: who does what, with the child and parent from the anchor, one clear moment
- `setting`: an Israeli place with concrete detail (gan gate with bougainvillea, kitchen with cream tiles)
- `camera`: distance and angle ("child eye level, medium shot from the side, 35mm look")
- `lighting`: time of day and quality
- `wardrobe_objects`: what is visible in this scene beyond the anchor (backpack, plush, marker)
- `text_zone`: `edge` top or bottom, `percent` 30 to 50, `surface` (what the empty area is: "plain warm cream wall", "soft pale morning sky above the fence"). The last slide uses about 50 percent; it is darkened for the CTA

## Rules of thumb

- Say who is NOT in the scene when the copy depends on it. The edit model copies everyone from the reference image, so a slide where the child is alone after the parents left must say "the parents are not in this scene" (kid-2 slide 3, 8 Oct 2026, came back with both parents in the doll corner)
- Name each prop once and say who holds it. "Dad carries her backpack" plus a backpack in the anchor gave two identical backpacks (kid-2 slide 6)

- Keep the same child and parent across all seven slides of an option. A different family per option is fine
- The parent in the anchor is the mother (addressee mom) or both parents with the mother clearly present (addressee parents). Never a father alone
- State the child's age in the anchor
- Other children only as soft blurred shapes in the background
- Real feelings, small and quiet. A trembling lip, not sobbing
- No pregnancy or body wording near children (the content checker rejected it in the 6 Oct trial)
- No clocks, signs, printed books with text, shirts with words: the model may render letters. Book pages show pictures only
- The last slide's scene shows the mother (or both parents) and child looking at an open picture book in which the child appears as the hero (it sits under the darkened CTA). No brand, no real product screenshot. Slide 6 is usually the reunion or a calm moment that closes the story
