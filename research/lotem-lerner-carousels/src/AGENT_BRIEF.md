# Coding brief: @lotem_lerner carousels

Lotem Lerner is an Israeli sleep consultant and nurse (18.4K followers). We study how she builds Instagram carousels so LumeBook (personalised kids' books) can learn from her.

Folder: `/Users/yarinbruner/Claude/Projects/Lumebook/research/lotem-lerner-carousels/`

For each carousel code you are given:

1. Read `src/dossiers/<code>.json` (date, likes, comments, caption, which slides are video).
2. Look at EVERY sheet listed in `sheets` (8 slides per sheet, 4 per row, right-to-left reading inside a slide, but slides run left to right then top to bottom: slide 1 top-left). If a slide's Hebrew is hard to read, open the single slide in `slides/<code>/NN.jpg`.
3. Write `src/coded/<code>.json` (valid JSON, escape quotes in Hebrew with \\" or use ״) with exactly these keys:

```json
{
  "code": "",
  "topic": "one English line: what the carousel is about",
  "topic_category": "one of: sleep | development_milestones | behaviour_emotions | feeding | parent_wellbeing | product_or_service | personal_story | other",
  "age_target": "e.g. newborn, 6-12m, 1y, toddler 2-3, mixed",
  "slide1_hook_he": "exact Hebrew text on slide 1, all lines in reading order",
  "slide1_hook_type": "one of: child_voice_confession | question | number_list | myth_bust | warning_mistake | relatable_moment | promise_result | other",
  "slide1_visual": "one line: who is in the picture, expression, framing, any badge or label",
  "voice": "who speaks across the slides: child_to_parents | lotem_to_parents | parent | mixed",
  "art_style": "e.g. 3D animated (Pixar-like), real photo of Lotem, real photo of kids, flat graphics, screenshots",
  "same_character_all_slides": true,
  "palette": "main colours in a few words",
  "text_layout": "where text sits, how many fonts/weights, what gets highlighted (bold word, pill, underline)",
  "structure": [ {"slide": 1, "role": "hook | context | point | numbered_point | turn | cta | about_me | social_proof | follow_share | other", "text_he_short": "the slide's headline or first line in Hebrew, max ~12 words"} ],
  "numbered_points": "how many numbered points and their label style, or 0",
  "cta_type": "comment_keyword | link_in_bio | save | share | follow | dm | none (list all that appear, in order)",
  "cta_keyword_he": "the exact word she asks people to comment, or empty",
  "cta_slide_positions": [ ],
  "brand_presence": "where her logo/handle/photo appears and how often",
  "caption_summary": "one line: caption length and what it does (short title, long story, repeats the CTA, hashtags)",
  "what_makes_it_work": "two sentences max, your judgement, tied to what you saw",
  "lumebook_takeaway": "one sentence: what a kids' book brand could copy from this specific carousel"
}
```

Rules:
- Quote Hebrew exactly as it appears. Do not translate the `_he` fields. Do not guess text you cannot read; write `[unclear]`.
- Do not invent likes, comments or reasons. Facts come from the dossier and the images only.
- Video slides show only their cover image; note `video cover` in that slide's role text.
- When done with all your codes, reply with just the list of codes written and anything you could not read.
