# Image briefs

The image model (GPT Image 2.5 Flare on fal.ai) gets the brief only after Yarin picks an option and approves the cost. The nightly brief must already be production ready, because the review page shows the exact prompt.

## One picture per option (Yarin, 14 Oct 2026)

"One picture that depicts the idea for the entire carousel." Since packs of 14 Oct 2026 each option has ONE brief, `image` on the option, and the slides have none. The picture shows the carousel's idea in one scene (the moment the examples help with, or the calm after it), sits behind all ten slides, and is also the cover: everything in "Slide 1 is the cover" below applies to it, and `compose_image_prompt()` gets it as slide 1. Write its `text_zone` for the busiest slide (45 percent, a truly plain wall or sky), because every slide's text sits there. The per-slide guidance further down applies to older 7 slide packs only.

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
- `text_zone` (the bold look sets the headline very large, so the zone must be truly empty: a plain wall or sky, no branches, lamps or shelves): `edge` top or bottom, `percent` 30 to 50 (use 45 on the cover, 40 on slides 2 to 6), `surface` (what the empty area is: "plain warm cream wall", "soft pale morning sky above the fence"). The last slide uses about 50 percent; it is darkened for the CTA

## Slide 1 is the cover (Yarin, 10 Oct 2026)

Slide 1 always shows the child's face to the viewer with an exaggerated expression, like an animated film poster. `compose_image_prompt()` adds the cover line on slide 1 and drops the pillar's wider framing there. Your slide 1 brief must agree with it, and the validator rejects it otherwise:

- `action`: "The girl faces the viewer and looks straight into the camera with huge wide eyes and raised eyebrows, both hands gripping her backpack straps; her mother is small and soft in the background at the gate."
- `camera`: "Child eye level, close head-and-shoulders shot, the face large in the frame."
- Name one big expression that fits the hook's feeling: wide eyes and raised eyebrows, a dramatic pout with puffed cheeks, an open-mouthed gasp, a jaw-dropped stare, a giant grin
- Never from behind, over the shoulder, in profile, from the side, face down or with the face hidden
- The cover headline is up to 3 very large lines, so keep the child's head in the lower half of the frame with plain wall or sky above it

## Rules of thumb

- Say who is NOT in the scene when the copy depends on it. The edit model copies everyone from the reference image, so a slide where the child is alone after the parents left must say "the parents are not in this scene" (kid-2 slide 3, 8 Oct 2026, came back with both parents in the doll corner)
- Name each prop once and say who holds it. "Dad carries her backpack" plus a backpack in the anchor gave two identical backpacks (kid-2 slide 6)

- Keep the same child and parent across all the slides of an option (older packs). A different family per option is fine
- The parent in the anchor is the mother (addressee mom) or both parents with the mother clearly present (addressee parents). Never a father alone
- State the child's age in the anchor
- Other children only as soft blurred shapes in the background
- Real feelings, small and quiet. A trembling lip, not sobbing
- No pregnancy or body wording near children (the content checker rejected it in the 6 Oct trial)
- The same goes for body parts and touch words in a child's action, and for the `--note` of `qa` and `replace` (the runner appends every note to the prompt). On 12 Oct 2026 (kid-3) the checker blocked a cover with "fists clenched at her chest" and a replacement whose note said "she does not touch the girl"; the cover passed once the girl hugged a cushion instead. Which words tripped it is a reading, not confirmed. A blocked call can still be billed, so it counts toward the cap
- No clocks, signs, printed books with text, shirts with words: the model may render letters. Book pages show pictures only
- The last slide's scene shows the mother (or both parents) and child looking at an open picture book in which the child appears as the hero (it sits under the darkened CTA). No brand, no real product screenshot. Slide 6 (the idea as a whole) is a calm moment that sums up the examples, often the reunion. Slides 2 to 5 picture the example the slide numbers (with two examples, the first one)
