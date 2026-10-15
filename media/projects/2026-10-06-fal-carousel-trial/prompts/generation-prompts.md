# Generation prompts and costs

Every image in `generated-assets/` came from the jobs below, run by `source/fal_generate.py` through the official fal.ai MCP server (`https://mcp.fal.ai/mcp`: tools `run_model`, `upload_file`, `check_job`, `get_job_result`). Prompts are assembled from the named blocks in `source/jobs.json`, joined with blank lines in the listed order; the text below is exactly what each call received. No credentials or media URLs are recorded; request IDs let a job be looked up in the fal.ai dashboard.

## Models and prices (fal `get_pricing`, 6 Oct 2026)

| Use | Endpoint | Price | Settings |
|---|---|---|---|
| Photo-real set, text to image | `fal-ai/nano-banana-2` | $0.08 per image | `aspect_ratio` 4:5, `resolution` 1K (928×1152), png, `limit_generations` true, seed per job |
| Photo-real set, reference edits | `fal-ai/nano-banana-2/edit` | $0.08 per image | same, plus `image_urls` = the uploaded reference PNG |
| Cheap style drafts | `fal-ai/flux/schnell` | $0.003 per megapixel (~$0.003 each at 768×1024) | `image_size` portrait_4_3, 4 steps, png, seed 77 |

Seedream 5.0 Pro (`bytedance/seedream/v5/pro/text-to-image`, $0.0675) was priced as the second model for the first cover comparison and dropped when the user asked for Nano Banana 2 only. It was never run.

Seeds are the ones sent in the input; the responses did not echo a seed, and Nano Banana 2 does not guarantee identical output for the same seed.

## Reference-image workflow

1. The photo-real style test (`style-2-nb2`, boy + mother + newborn in a nursery) became the reference.
2. For each slide, that PNG is uploaded with `upload_file` (`prepare_upload: true`, then an HTTP PUT) and passed in `image_urls` to `fal-ai/nano-banana-2/edit`.
3. Each edit prompt opens with `P_REF` (keep this exact boy and mother, same photographic style, new scene and angle), then the scene, a layout block (`P_DAY` or `P_NIGHT`: subjects in the lower 55%, empty wall above) and `NO_TEXT`.
4. One reference was enough: the boy's face, hair and plum sweater, the mother's face, bun and linen shirt, and the grey rabbit held across all six edits.

## Cost

| Job | Endpoint | Seed | Request ID | Wall time | Est. cost |
|---|---|---|---|---|---|
| `style-2-nb2` | `fal-ai/nano-banana-2` | 77 | `01a112e0-82dd-7ba1-9f05-5dcac7be74b6` | 16.5 s | $0.080 |
| `p1` | `fal-ai/nano-banana-2/edit` | 5101 | `01a112e3-828a-7df3-a652-038db039a05d` | 13.6 s | $0.080 |
| `p2` | `fal-ai/nano-banana-2/edit` | 5102 | `01a112e3-82d5-7bb2-9f7b-e5414407022c` | 14.1 s | $0.080 |
| `p4` | `fal-ai/nano-banana-2/edit` | 5104 | `01a112e3-83e5-70d0-9905-ef0bb46a2a4a` | 13.8 s | $0.080 |
| `p5` | `fal-ai/nano-banana-2/edit` | 5105 | `01a112e3-8490-7662-a817-196f45d070f8` | 15.8 s | $0.080 |
| `p6` | `fal-ai/nano-banana-2/edit` | 5106 | `01a112e3-83bd-7e50-aa8f-082fc0601161` | 15.9 s | $0.080 |
| `p7` | `fal-ai/nano-banana-2/edit` | 5107 | `01a112e3-82c4-7932-9e44-dab3e8bde237` | 13.8 s | $0.080 |
| `style-1-3d-cartoon` | `fal-ai/flux/schnell` | 77 | `01a112dd-f776-7a91-8c43-b32df5d486f2` | 5.7 s | $0.003 |
| `style-2-photoreal` | `fal-ai/flux/schnell` | 77 | `01a112dd-f7b5-7372-8ff1-cdc484c433cf` | 5.7 s | $0.003 |
| `style-3-painted-lumebook` | `fal-ai/flux/schnell` | 77 | `01a112dd-f7b0-79b1-ac64-4db325c4d1c5` | 5.4 s | $0.003 |
| `style-4-mixed` | `fal-ai/flux/schnell` | 77 | `01a112dd-f751-7c50-8132-efc7497057d2` | 5.3 s | $0.003 |
| `style-3-nb2` | `fal-ai/nano-banana-2` | 77 | `01a112e0-8340-72e2-b121-32103f3f145a` | 14.0 s | $0.080 |
| `cover-A-nb2` | `fal-ai/nano-banana-2` | 4207 | `01a112b9-13d1-7191-9058-3bc675a119c7` | 13.7 s | $0.080 |
| `cover-B-nb2` | `fal-ai/nano-banana-2` | 4207 | `01a112b9-13bf-7593-b857-3187d2a9bfc9` | 13.8 s | $0.080 |
| `s2` | `fal-ai/nano-banana-2/edit` | 4212 | `01a112bc-0116-7b10-a9e2-0dc58541ba5e` | 15.8 s | $0.080 |
| `s2-fix` | `fal-ai/nano-banana-2/edit` | 4222 | `01a112bc-adbe-7bf1-b0af-ebab81323a7e` | 16.4 s | $0.080 |
| `s3` | `fal-ai/nano-banana-2/edit` | 4203 | `01a112ba-96f7-7c82-b174-795d7eaf411a` | 18.1 s | $0.080 |
| `s4` | `fal-ai/nano-banana-2/edit` | 4204 | `01a112ba-971c-7dd0-b696-d95ba2f0c93d` | 15.8 s | $0.080 |
| `s5` | `fal-ai/nano-banana-2/edit` | 4205 | `01a112ba-97fc-7b11-8887-387b175a948f` | 14.5 s | $0.080 |
| `s6` | `fal-ai/nano-banana-2/edit` | 4206 | `01a112ba-97c1-7dd2-aa13-923453dfd0df` | 15.6 s | $0.080 |
| `s7` | `fal-ai/nano-banana-2/edit` | 4207 | `01a112ba-96cf-7f22-b742-47dc29baa88b` | 16.3 s | $0.080 |
| `s2` first attempt (rejected, 422) | `fal-ai/nano-banana-2/edit` | 4202 | `01a112ba-975e-7121-a863-db5900c2d681` | about 15 s | $0.00 to $0.08 |

**Total: 21 delivered generations = $1.37.** If fal also billed the rejected request (its FAQ says a 422 "may still be charged", fal docs read through the MCP `search_docs` tool), the total is $1.45.

**Budget:** the brief's cap was $1.25. After the style tests the user explicitly raised it to $1.40 to finish the photo-real set. The delivered-generation total of $1.37 is inside $1.40; the worst case with the rejected request ($1.45) is slightly over it. Check the fal.ai billing page for the exact figure. Only image generations are billed by fal; the Hebrew text, layout and export run locally for free.

## Rejected attempt (content checker)

The first illustrated slide 2 prompt was rejected with `content_policy_violation` on the `prompt` field (HTTP 422, no image, no reason given). The likely trigger is the pregnancy and body wording next to a child; the replacement scene (mother and son side by side with folded baby clothes) passed. Rejected scene block, kept in `jobs.json` as `SCENE_2_REJECTED`:

> Scene: the boy sits on the floor leaning his head against his pregnant mother's side; she sits beside him on the floor with her arm wrapped around him and her rounded belly visible in profile. Her head is bowed toward him and turned away from the viewer. The boy's face is in clear three-quarter view: thoughtful and a little unsure, but held and calmer. Closeness, quiet, no smiles forced.

## Prompts, job by job

## A. Final photo-real carousel (the delivered slides)

### `style-2-nb2`: Slide 3 art, also the character reference for slides 1, 2, 4 to 7 (this is the photo-real style test, reused)

- Endpoint: `fal-ai/nano-banana-2`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 77}`
- Reference images: none
- Blocks: `STYLE_PHOTO` + `SCENE_STYLE_FINAL`

```text
Warm golden-hour photo-realistic family portrait, soft cinematic backlight from a window, shallow depth of field, natural skin with visible pores and small imperfections, real fabric and wood textures, calm intimate documentary feel, muted warm palette of cream, plum and oak, no glossy retouching.

Scene: a 4-year-old boy with short tousled dark-brown hair, olive skin, plum-violet knitted sweater with a cream collar, leans his chin on the edge of a small wooden baby bed where a swaddled newborn sleeps. His mother, dark hair in a low bun, oatmeal linen shirt, stands behind him with one hand on his shoulder and looks down at both children with a soft, tender smile; her face is clearly visible and natural. The boy's expression is tender and a little wistful. Composition for a vertical 4:5 slide: figures and bed sit in the lower 55% of the frame; the upper 45% is plain, empty, softly lit wall with no objects, kept clear for typography. No text, no letters, no logos, no watermark.
```

### `p1`: Slide 1, uncertainty

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 5101}`
- Reference images: `generated-assets/style-2-nb2.png`
- Blocks: `P_REF` + `P_S1` + `P_DAY` + `NO_TEXT`

```text
Use the reference image as the character reference. Keep exactly the same boy (same face, short tousled dark-brown hair, olive skin, plum-violet knitted sweater with cream collar, oatmeal trousers) and the same mother (same face, dark hair in a low bun, oatmeal linen shirt). Keep the same photo-realistic style: natural skin with visible pores, soft natural light, real fabric textures, documentary feel, no retouching, no glossy skin. Photograph a completely new scene and camera angle.

Scene: the boy, alone, sits on the wooden floor of a quiet bedroom with his knees pulled up, one hand on his cheek, looking sideways at a small empty wooden baby crib made up with a folded cream blanket. His expression is uncertain and thoughtful, lips pressed together, not crying. A worn grey plush rabbit rests in his lap. His face is in clear three-quarter view.

Composition for a vertical 4:5 slide: the people and objects sit in the lower 55% of the frame; the upper 45% is a plain, softly lit, empty warm-cream wall with no objects, no curtains and no lamps, kept clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `p2`: Slide 2, closeness

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 5102}`
- Reference images: `generated-assets/style-2-nb2.png`
- Blocks: `P_REF` + `P_S2` + `P_DAY` + `NO_TEXT`

```text
Use the reference image as the character reference. Keep exactly the same boy (same face, short tousled dark-brown hair, olive skin, plum-violet knitted sweater with cream collar, oatmeal trousers) and the same mother (same face, dark hair in a low bun, oatmeal linen shirt). Keep the same photo-realistic style: natural skin with visible pores, soft natural light, real fabric textures, documentary feel, no retouching, no glossy skin. Photograph a completely new scene and camera angle.

Scene: the boy and his mother sit side by side on the floor of a quiet bedroom. He leans his head on her shoulder and she holds him close with one arm, her cheek resting on his hair, eyes closed, tender. Her face is visible. Beside them lies a small neat stack of folded tiny baby clothes with a little knitted baby hat on top. The boy looks unsure but held.

Composition for a vertical 4:5 slide: the people and objects sit in the lower 55% of the frame; the upper 45% is a plain, softly lit, empty warm-cream wall with no objects, no curtains and no lamps, kept clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `p4`: Slide 4, belonging (defect: flat slab over the sky, repaired in code)

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 5104}`
- Reference images: `generated-assets/style-2-nb2.png`
- Blocks: `P_REF` + `P_S4` + `P_DAY` + `NO_TEXT`

```text
Use the reference image as the character reference. Keep exactly the same boy (same face, short tousled dark-brown hair, olive skin, plum-violet knitted sweater with cream collar, oatmeal trousers) and the same mother (same face, dark hair in a low bun, oatmeal linen shirt). Keep the same photo-realistic style: natural skin with visible pores, soft natural light, real fabric textures, documentary feel, no retouching, no glossy skin. Photograph a completely new scene and camera angle.

Scene: the boy and his mother walk away along a sunlit park path hand in hand, photographed from behind and slightly to the side at child height; she glances down at him with a soft smile, her face visible in profile. Pale grass, a few trees in soft focus. No baby, no pram. Late-afternoon light.

Composition for a vertical 4:5 slide: the people and objects sit in the lower 55% of the frame; the upper 45% is a plain, softly lit, empty warm-cream wall with no objects, no curtains and no lamps, kept clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `p5`: Slide 5, permission to stay small

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 5105}`
- Reference images: `generated-assets/style-2-nb2.png`
- Blocks: `P_REF` + `P_S5` + `P_DAY` + `NO_TEXT`

```text
Use the reference image as the character reference. Keep exactly the same boy (same face, short tousled dark-brown hair, olive skin, plum-violet knitted sweater with cream collar, oatmeal trousers) and the same mother (same face, dark hair in a low bun, oatmeal linen shirt). Keep the same photo-realistic style: natural skin with visible pores, soft natural light, real fabric textures, documentary feel, no retouching, no glossy skin. Photograph a completely new scene and camera angle.

Scene: the boy is curled up in his mother's lap in a soft armchair, wrapped in a small cream knitted baby blanket that is too small for him, like a much younger child. Her arms hold him close, her face is visible and gentle, looking down at him. His eyes are half closed and his face is peaceful and safe. The grey plush rabbit is tucked under his chin.

Composition for a vertical 4:5 slide: the people and objects sit in the lower 55% of the frame; the upper 45% is a plain, softly lit, empty warm-cream wall with no objects, no curtains and no lamps, kept clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `p6`: Slide 6, the story world (dark)

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 5106}`
- Reference images: `generated-assets/style-2-nb2.png`
- Blocks: `P_REF` + `P_S6` + `P_NIGHT` + `NO_TEXT`

```text
Use the reference image as the character reference. Keep exactly the same boy (same face, short tousled dark-brown hair, olive skin, plum-violet knitted sweater with cream collar, oatmeal trousers) and the same mother (same face, dark hair in a low bun, oatmeal linen shirt). Keep the same photo-realistic style: natural skin with visible pores, soft natural light, real fabric textures, documentary feel, no retouching, no glossy skin. Photograph a completely new scene and camera angle.

Scene: the boy sits on the floor in the lamplight with a large square picture book open on his lap, seen over his shoulder. The open pages show a painted storybook illustration of this same boy in a plum sweater gently holding a newborn's tiny hand beside a small crib. The pages contain illustration only and no writing at all. His face is visible in three-quarter profile: absorbed, recognising himself, a small beginning of a smile.

Composition for a vertical 4:5 slide: the people and objects sit in the lower 55% of the frame; the upper 45% is a plain, empty, dark violet-blue wall in deep shadow with no objects, kept clear for typography. Dim evening light: deep violet-blue shadows with one small warm lamp as the only light source.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `p7`: Slide 7, new role (dark)

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 5107}`
- Reference images: `generated-assets/style-2-nb2.png`
- Blocks: `P_REF` + `P_S7` + `P_NIGHT` + `NO_TEXT`

```text
Use the reference image as the character reference. Keep exactly the same boy (same face, short tousled dark-brown hair, olive skin, plum-violet knitted sweater with cream collar, oatmeal trousers) and the same mother (same face, dark hair in a low bun, oatmeal linen shirt). Keep the same photo-realistic style: natural skin with visible pores, soft natural light, real fabric textures, documentary feel, no retouching, no glossy skin. Photograph a completely new scene and camera angle.

Scene: the boy sits upright and proud on the floor in the lamplight next to a small wooden crib where a swaddled newborn sleeps, reading aloud from a large square softcover picture book held open toward the baby; a thin ochre-gold ribbon bookmark hangs from the book. His face is in clear three-quarter view: confident, gentle, a quiet smile. The grey plush rabbit sits beside him.

Composition for a vertical 4:5 slide: the people and objects sit in the lower 55% of the frame; the upper 45% is a plain, empty, dark violet-blue wall in deep shadow with no objects, kept clear for typography. Dim evening light: deep violet-blue shadows with one small warm lamp as the only light source.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

## B. Style tests that led to the photo-real choice

### `style-1-3d-cartoon`: Draft: 3D cartoon (Flux Schnell)

- Endpoint: `fal-ai/flux/schnell`
- Parameters: `{"image_size": "portrait_4_3", "num_inference_steps": 4, "num_images": 1, "output_format": "png", "enable_safety_checker": true, "seed": 77}`
- Reference images: none
- Blocks: `style-1-3d-cartoon-blk` + `STYLE_TEST_SCENE`

```text
Glossy Pixar-style 3D-rendered children's book cover illustration: rounded, big-eyed, expressive characters, saturated jewel colours, warm magical glow, soft rim light, rich purple and gold palette, polished and cinematic.

Scene: a 4-year-old boy with short tousled dark-brown hair, plum-violet sweater with a cream collar, leans on the edge of a small wooden baby bed where a swaddled newborn sleeps. His mother, dark hair in a low bun, in an oatmeal linen shirt, stands behind him with a hand on his shoulder, looking down at both children with a soft smile; her face is clearly visible. The upper 40% of the frame is plain empty space for typography. No text, no letters, no logos, no watermark.
```

### `style-2-photoreal`: Draft: photo-real (Flux Schnell)

- Endpoint: `fal-ai/flux/schnell`
- Parameters: `{"image_size": "portrait_4_3", "num_inference_steps": 4, "num_images": 1, "output_format": "png", "enable_safety_checker": true, "seed": 77}`
- Reference images: none
- Blocks: `style-2-photoreal-blk` + `STYLE_TEST_SCENE`

```text
Warm golden-hour photo-realistic portrait, soft cinematic backlight, shallow depth of field, glowing natural light, realistic skin and fabrics, intimate family moment.

Scene: a 4-year-old boy with short tousled dark-brown hair, plum-violet sweater with a cream collar, leans on the edge of a small wooden baby bed where a swaddled newborn sleeps. His mother, dark hair in a low bun, in an oatmeal linen shirt, stands behind him with a hand on his shoulder, looking down at both children with a soft smile; her face is clearly visible. The upper 40% of the frame is plain empty space for typography. No text, no letters, no logos, no watermark.
```

### `style-3-painted-lumebook`: Draft: painted + LumeBook (Flux Schnell)

- Endpoint: `fal-ai/flux/schnell`
- Parameters: `{"image_size": "portrait_4_3", "num_inference_steps": 4, "num_images": 1, "output_format": "png", "enable_safety_checker": true, "seed": 77}`
- Reference images: none
- Blocks: `style-3-painted-lumebook-blk` + `STYLE_TEST_SCENE`

```text
Hand-painted gouache storybook illustration with a little more cartoon charm in the faces, richer saturated plum, ochre and rose, warm glow, brand violet and gold accents, soft paper texture.

Scene: a 4-year-old boy with short tousled dark-brown hair, plum-violet sweater with a cream collar, leans on the edge of a small wooden baby bed where a swaddled newborn sleeps. His mother, dark hair in a low bun, in an oatmeal linen shirt, stands behind him with a hand on his shoulder, looking down at both children with a soft smile; her face is clearly visible. The upper 40% of the frame is plain empty space for typography. No text, no letters, no logos, no watermark.
```

### `style-4-mixed`: Draft: mixed (Flux Schnell)

- Endpoint: `fal-ai/flux/schnell`
- Parameters: `{"image_size": "portrait_4_3", "num_inference_steps": 4, "num_images": 1, "output_format": "png", "enable_safety_checker": true, "seed": 77}`
- Reference images: none
- Blocks: `style-4-mixed-blk` + `STYLE_TEST_SCENE`

```text
A rounded, slightly stylised 3D-ish child character with large friendly eyes and soft clay-like shading, placed inside a soft painterly paper-textured room with muted watercolour walls and warm window light.

Scene: a 4-year-old boy with short tousled dark-brown hair, plum-violet sweater with a cream collar, leans on the edge of a small wooden baby bed where a swaddled newborn sleeps. His mother, dark hair in a low bun, in an oatmeal linen shirt, stands behind him with a hand on his shoulder, looking down at both children with a soft smile; her face is clearly visible. The upper 40% of the frame is plain empty space for typography. No text, no letters, no logos, no watermark.
```

### `style-3-nb2`: Finalist: painted + LumeBook (Nano Banana 2, not used)

- Endpoint: `fal-ai/nano-banana-2`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 77}`
- Reference images: none
- Blocks: `STYLE_PAINT_LB` + `SCENE_STYLE_FINAL`

```text
Hand-painted gouache and coloured-pencil storybook illustration with warm, charming, slightly rounded faces, richer saturated plum-violet, ochre gold and dusty rose, a soft golden glow of window light, visible paper texture and brush edges, brand violet and gold accents, calm and emotionally honest, not glossy, not 3D.

Scene: a 4-year-old boy with short tousled dark-brown hair, olive skin, plum-violet knitted sweater with a cream collar, leans his chin on the edge of a small wooden baby bed where a swaddled newborn sleeps. His mother, dark hair in a low bun, oatmeal linen shirt, stands behind him with one hand on his shoulder and looks down at both children with a soft, tender smile; her face is clearly visible and natural. The boy's expression is tender and a little wistful. Composition for a vertical 4:5 slide: figures and bed sit in the lower 55% of the frame; the upper 45% is plain, empty, softly lit wall with no objects, kept clear for typography. No text, no letters, no logos, no watermark.
```

## C. First direction, illustrated paper style (replaced by photo-real; kept in source/legacy-illustrated/)

### `cover-A-nb2`: Cover A, paper

- Endpoint: `fal-ai/nano-banana-2`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4207}`
- Reference images: none
- Blocks: `STYLE_PAPER` + `CHILD` + `SCENE_COVER` + `COMP_TOP_EMPTY_PAPER` + `NO_TEXT`

```text
Editorial children's picture-book illustration in gouache and soft coloured pencil on warm off-white cotton paper. Visible paper tooth, dry-brush edges and fine pencil hatching; matte and hand-made, no digital gloss. Soft natural daylight from a window on the left, gentle lilac-grey shadows. Restrained palette: warm cream paper, deep plum-violet, muted ochre gold, dusty rose, pale oak wood, soft warm grey. Quiet, intimate, emotionally honest and understated, like a modern European picture book that adults linger over. Not cartoon, not anime, not 3D, not photographic, no airbrushed skin, no sparkles, no fantasy glow.

The child: a 4-year-old boy with short, slightly tousled dark-brown hair, warm olive skin, soft round cheeks, dark brown eyes, small straight eyebrows and a small nose. He wears a plum-violet knitted sweater with a cream rounded collar, loose oatmeal-beige trousers and grey wool socks.

Scene: the boy sits on the floorboards of a quiet bedroom with his knees pulled up, beside a small empty wooden bassinet made up with a folded cream blanket. One arm hugs a worn, floppy grey plush rabbit. He looks sideways up at the empty bassinet with an uncertain, thoughtful expression, lips pressed together, not crying. His face is in clear three-quarter view toward the viewer.

Composition for a vertical 4:5 slide: the boy and the bassinet sit in the lower half of the frame, slightly right of centre; the whole upper half is plain, empty cream paper with only the faintest wash of wall tone, kept clear for typography. A soft patch of afternoon light falls across the floor.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `cover-B-nb2`: Cover B, night light

- Endpoint: `fal-ai/nano-banana-2`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4207}`
- Reference images: none
- Blocks: `STYLE_NIGHT` + `CHILD` + `SCENE_COVER` + `COMP_TOP_EMPTY_NIGHT` + `NO_TEXT`

```text
Editorial children's picture-book illustration in gouache on dark toned paper. A deep ink-violet night palette (near-black violet, plum, muted indigo) with a single warm light source: a small paper lamp standing on the floor that casts a soft golden pool of light. Visible brush texture and paper tooth; matte and hand-made, no digital gloss, no neon, no sparkles, no stars. Quiet, intimate, emotionally honest and understated, like a modern European picture book that adults linger over. Not cartoon, not anime, not 3D, not photographic, no airbrushed skin.

The child: a 4-year-old boy with short, slightly tousled dark-brown hair, warm olive skin, soft round cheeks, dark brown eyes, small straight eyebrows and a small nose. He wears a plum-violet knitted sweater with a cream rounded collar, loose oatmeal-beige trousers and grey wool socks.

Scene: the boy sits on the floorboards of a quiet bedroom with his knees pulled up, beside a small empty wooden bassinet made up with a folded cream blanket. One arm hugs a worn, floppy grey plush rabbit. He looks sideways up at the empty bassinet with an uncertain, thoughtful expression, lips pressed together, not crying. His face is in clear three-quarter view toward the viewer.

Composition for a vertical 4:5 slide: the boy, the bassinet and the lamp sit in the lower half of the frame, slightly right of centre, inside the pool of lamplight; the whole upper half is calm, empty dark violet with only subtle paper texture, kept clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `s2`: Slide 2

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4212}`
- Reference images: `generated-assets/cover-A-nb2.png`
- Blocks: `REF_LOCK` + `CHILD` + `MOTHER` + `SCENE_2` + `COMP_TOP_EMPTY` + `NO_TEXT`

```text
Use the reference image as the character and style reference. Keep exactly the same boy: the same face, the same tousled dark-brown hair, the same warm olive skin and rosy cheeks, the same plum-violet knitted sweater with the cream rounded collar, the same oatmeal-beige trousers and grey wool socks. Keep exactly the same illustration technique: gouache and soft coloured pencil on warm off-white paper, the same fine pencil linework and paper tooth, the same restrained palette of cream, plum-violet, lilac-grey shadows and pale oak wood, the same soft daylight. Draw a completely new scene and camera angle; do not copy the reference layout.

The child: a 4-year-old boy with short, slightly tousled dark-brown hair, warm olive skin, soft round cheeks, dark brown eyes, small straight eyebrows and a small nose. He wears a plum-violet knitted sweater with a cream rounded collar, loose oatmeal-beige trousers and grey wool socks.

His mother appears only partly: dark hair in a loose low bun, a soft oatmeal linen shirt; her face is never shown (turned away, bowed and hidden by her hair, or out of frame).

Scene: the boy and his mother sit side by side on the floor of a quiet bedroom. He leans his head against her shoulder and she rests her arm around his shoulders, her head tilted toward his and turned away from the viewer. Beside them on the floor lies a small neat stack of folded tiny baby clothes with a little knitted baby hat on top: the new baby is coming. The boy's face is in clear three-quarter view: thoughtful and a little unsure, but held and calmer.

Composition for a vertical 4:5 slide: all figures and objects sit in the lower 55% of the frame; the upper 45% is plain, empty cream paper with only the faintest wash of wall tone, kept completely clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `s2-fix`: Slide 2 repair

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4222}`
- Reference images: `generated-assets/s2.png`
- Blocks: `FIX_2` + `NO_TEXT`

```text
Edit this illustration. Remove the pair of outstretched legs in beige trousers and grey socks that extend to the left from behind the boy in the lower-left of the image, and fill that area with the same plain pale floorboards and soft lilac shadow. The mother now sits with her legs folded beside her, hidden behind the boy. Keep everything else exactly the same: the boy, his face and expression, his sweater, his own legs and grey socks, the mother, her hands, the folded baby clothes, the illustration style, paper texture, colours, composition and framing.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `s3`: Slide 3

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4203}`
- Reference images: `generated-assets/cover-A-nb2.png`
- Blocks: `REF_LOCK` + `CHILD` + `SCENE_3` + `COMP_TOP_EMPTY` + `NO_TEXT`

```text
Use the reference image as the character and style reference. Keep exactly the same boy: the same face, the same tousled dark-brown hair, the same warm olive skin and rosy cheeks, the same plum-violet knitted sweater with the cream rounded collar, the same oatmeal-beige trousers and grey wool socks. Keep exactly the same illustration technique: gouache and soft coloured pencil on warm off-white paper, the same fine pencil linework and paper tooth, the same restrained palette of cream, plum-violet, lilac-grey shadows and pale oak wood, the same soft daylight. Draw a completely new scene and camera angle; do not copy the reference layout.

The child: a 4-year-old boy with short, slightly tousled dark-brown hair, warm olive skin, soft round cheeks, dark brown eyes, small straight eyebrows and a small nose. He wears a plum-violet knitted sweater with a cream rounded collar, loose oatmeal-beige trousers and grey wool socks.

Scene: the same small wooden baby bed from the reference now holds a sleeping newborn swaddled in a cream blanket (only the swaddled bundle and a tiny sleeping face in profile are visible). The boy stands beside it on tiptoe with his chin resting on the bed's edge, looking at the baby with a mixed expression: tender and curious, and also a little wistful. Behind his back, his other hand still holds the worn grey plush rabbit by one ear.

Composition for a vertical 4:5 slide: all figures and objects sit in the lower 55% of the frame; the upper 45% is plain, empty cream paper with only the faintest wash of wall tone, kept completely clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `s4`: Slide 4

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4204}`
- Reference images: `generated-assets/cover-A-nb2.png`
- Blocks: `REF_LOCK` + `CHILD` + `MOTHER` + `SCENE_4` + `COMP_TOP_EMPTY` + `NO_TEXT`

```text
Use the reference image as the character and style reference. Keep exactly the same boy: the same face, the same tousled dark-brown hair, the same warm olive skin and rosy cheeks, the same plum-violet knitted sweater with the cream rounded collar, the same oatmeal-beige trousers and grey wool socks. Keep exactly the same illustration technique: gouache and soft coloured pencil on warm off-white paper, the same fine pencil linework and paper tooth, the same restrained palette of cream, plum-violet, lilac-grey shadows and pale oak wood, the same soft daylight. Draw a completely new scene and camera angle; do not copy the reference layout.

The child: a 4-year-old boy with short, slightly tousled dark-brown hair, warm olive skin, soft round cheeks, dark brown eyes, small straight eyebrows and a small nose. He wears a plum-violet knitted sweater with a cream rounded collar, loose oatmeal-beige trousers and grey wool socks.

His mother appears only partly: dark hair in a loose low bun, a soft oatmeal linen shirt; her face is never shown (turned away, bowed and hidden by her hair, or out of frame).

Scene: a wide, quiet view from behind. The boy and his mother walk away from the viewer, hand in hand, along a simple path through a sparse park drawn with a few pencil trees and pale grass; just the two of them, no baby, no pram. His small hand is in hers; he looks up at her. Their backs are to the viewer. Calm, private, unhurried.

Composition for a vertical 4:5 slide: all figures and objects sit in the lower 55% of the frame; the upper 45% is plain, empty cream paper with only the faintest wash of wall tone, kept completely clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `s5`: Slide 5

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4205}`
- Reference images: `generated-assets/cover-A-nb2.png`
- Blocks: `REF_LOCK` + `CHILD` + `MOTHER` + `SCENE_5` + `COMP_TOP_EMPTY` + `NO_TEXT`

```text
Use the reference image as the character and style reference. Keep exactly the same boy: the same face, the same tousled dark-brown hair, the same warm olive skin and rosy cheeks, the same plum-violet knitted sweater with the cream rounded collar, the same oatmeal-beige trousers and grey wool socks. Keep exactly the same illustration technique: gouache and soft coloured pencil on warm off-white paper, the same fine pencil linework and paper tooth, the same restrained palette of cream, plum-violet, lilac-grey shadows and pale oak wood, the same soft daylight. Draw a completely new scene and camera angle; do not copy the reference layout.

The child: a 4-year-old boy with short, slightly tousled dark-brown hair, warm olive skin, soft round cheeks, dark brown eyes, small straight eyebrows and a small nose. He wears a plum-violet knitted sweater with a cream rounded collar, loose oatmeal-beige trousers and grey wool socks.

His mother appears only partly: dark hair in a loose low bun, a soft oatmeal linen shirt; her face is never shown (turned away, bowed and hidden by her hair, or out of frame).

Scene: the boy is curled up in his mother's lap in a soft armchair, wrapped in a cream knitted baby blanket that is too small for him, like a much younger child. Her arms hold him close; her head is bowed over him so her face is hidden by her hair and out of view. The boy's eyes are half closed and his face is peaceful and safe. The worn grey plush rabbit is tucked under his chin.

Composition for a vertical 4:5 slide: all figures and objects sit in the lower 55% of the frame; the upper 45% is plain, empty cream paper with only the faintest wash of wall tone, kept completely clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `s6`: Slide 6

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4206}`
- Reference images: `generated-assets/cover-A-nb2.png`
- Blocks: `REF_LOCK` + `CHILD` + `SCENE_6` + `COMP_TOP_EMPTY` + `NO_TEXT`

```text
Use the reference image as the character and style reference. Keep exactly the same boy: the same face, the same tousled dark-brown hair, the same warm olive skin and rosy cheeks, the same plum-violet knitted sweater with the cream rounded collar, the same oatmeal-beige trousers and grey wool socks. Keep exactly the same illustration technique: gouache and soft coloured pencil on warm off-white paper, the same fine pencil linework and paper tooth, the same restrained palette of cream, plum-violet, lilac-grey shadows and pale oak wood, the same soft daylight. Draw a completely new scene and camera angle; do not copy the reference layout.

The child: a 4-year-old boy with short, slightly tousled dark-brown hair, warm olive skin, soft round cheeks, dark brown eyes, small straight eyebrows and a small nose. He wears a plum-violet knitted sweater with a cream rounded collar, loose oatmeal-beige trousers and grey wool socks.

Scene: a close view over the boy's shoulder as he sits on the floor with a large square picture book open on his lap. The open pages show a painted illustration, in the same style, of this same boy in his plum-violet sweater gently holding a newborn's tiny hand beside a small wooden baby bed. The book's pages contain illustration only, with no writing at all. His face is partly visible in three-quarter profile: absorbed, recognising himself, a small beginning of a smile.

Composition for a vertical 4:5 slide: all figures and objects sit in the lower 55% of the frame; the upper 45% is plain, empty cream paper with only the faintest wash of wall tone, kept completely clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```

### `s7`: Slide 7

- Endpoint: `fal-ai/nano-banana-2/edit`
- Parameters: `{"aspect_ratio": "4:5", "resolution": "1K", "output_format": "png", "num_images": 1, "limit_generations": true, "seed": 4207}`
- Reference images: `generated-assets/cover-A-nb2.png`
- Blocks: `REF_LOCK` + `CHILD` + `SCENE_7` + `COMP_TOP_EMPTY` + `NO_TEXT`

```text
Use the reference image as the character and style reference. Keep exactly the same boy: the same face, the same tousled dark-brown hair, the same warm olive skin and rosy cheeks, the same plum-violet knitted sweater with the cream rounded collar, the same oatmeal-beige trousers and grey wool socks. Keep exactly the same illustration technique: gouache and soft coloured pencil on warm off-white paper, the same fine pencil linework and paper tooth, the same restrained palette of cream, plum-violet, lilac-grey shadows and pale oak wood, the same soft daylight. Draw a completely new scene and camera angle; do not copy the reference layout.

The child: a 4-year-old boy with short, slightly tousled dark-brown hair, warm olive skin, soft round cheeks, dark brown eyes, small straight eyebrows and a small nose. He wears a plum-violet knitted sweater with a cream rounded collar, loose oatmeal-beige trousers and grey wool socks.

Scene: the boy sits upright and proud on the floor next to the small wooden baby bed where the swaddled newborn sleeps, reading aloud from a large square softcover picture book held open in both hands, tilted toward the baby. A thin ochre-gold ribbon bookmark hangs from the book. His face is in clear three-quarter view: confident, gentle, a quiet smile. The grey plush rabbit sits beside him on the floor.

Composition for a vertical 4:5 slide: all figures and objects sit in the lower 55% of the frame; the upper 45% is plain, empty cream paper with only the faintest wash of wall tone, kept completely clear for typography.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame or border.
```
