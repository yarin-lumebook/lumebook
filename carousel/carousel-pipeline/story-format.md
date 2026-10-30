# Story format (Carousel Machine, from 29 Oct 2026)

Yarin, 29 Oct 2026, after the five Lotem-format carousels (`media/projects/2026-10-29-lotem-format-carousels/`, `runs/<id>/final-v4/` is the reference): "i like the new content, change the entire carousel machine and November batch to match it". Before that, the same evening: "too little text so the slides are not coherent enough and the format is too repetitive" and "why is it always 8 things? why always lists?".

A pack is in the story format when it has `"copy_style": "story"` at the top level. Packs without it keep every older rule (10 slides, numbered examples, one picture). Everything below applies only to story packs.

## What stays the same

- `format: "two_topics"`, two topics, kid-1 to kid-3 on topics[0] and kid-4 to kid-6 on topics[1], `topic_id` on each option, books, sources, product_facts, hook_slate, `voice_style: "to_parents"`, `cta_style: "save_for_later"`.
- The child talks to the parents everywhere (slides, caption). Addressee mom (feminine singular) or both parents (plural), never dad alone; names from `names.md`; 3 girls and 3 boys per pack as `nightly.py start` assigns them.
- Hebrew voice rules (lumebook-hebrew-voice skill): no dash of any kind, no semicolon, no hyphen or maqaf; no jargon or diagnosis words; no fake certainty; never "כל הילדים"; no brand, no book title, no AI mention.
- Cover (slide 1): the loud true hook, headline up to 3 lines of up to 18 characters, the child faces the viewer with an exaggerated expression (`image` on the option, as now).
- Last slide: the save CTA exactly as now (packs with `cta_style` `save_for_later`; since 30 Oct 2026 new packs use the book link CTA, section 7): headline `תשמרי את הפוסט` / `תשמרו את הפוסט`, body `לפעם הבאה ש...` about the child (הוא/היא), up to 5 words.
- Caption: the child's voice, line 1 restates the hook, value lines ask the parents for something, the bridge line `ובערב אפשר להמשיך עם סיפור שבו אני הגיבור/ה`, last line = the CTA word for word. `post_text` follows the caption with one emoji on the hook line and one on the CTA line only.

## What changes

### 1. Each option has a structure, not a list of 8

`option.structure` is one of:

| structure | how it reads | labels (`label` on slides) |
|---|---|---|
| `before_after` | "פעם" (2 to 3 slides of how it was), "ואז" (the change), "ומאז" (3 to 5 slides of what the child does now and why), one slide of what brings back "פעם", a turn back to the parents | `פעם`, `ואז`, `ומאז`, free text |
| `letter` | a letter from the child: slide 2 headline `אמא שלי,` or `אמא ואבא שלי,`, the following slides have no headline (body only), the last letter slide ends with the signature line `**אוהב, NAME**` / `**אוהבת, NAME**`. Rendered on a cream sheet | none |
| `thoughts_answers` | slide 2 sets up ("אני רואה איך אתם מסתכלים עליי..."), then each slide: label `אתם חושבים:` / `את חושבת:`, headline = the parent's thought in ״...״, body = the child's answer (`## אני עונה:` and/or `## מה יעזור לי:`); the last one labelled `ואחרונה:` | as described |
| `one_minute` | one hard moment slowed down, second by second, then what helps after | `הדקה מתחילה`, `עשר שניות`, `עשרים שניות`, ..., `בערב` |
| `one_day` | one day of the child by the clock, morning to bed | `07:30, בבוקר`, `13:30, בדלת`, ..., `20:00, במיטה` |
| `short_list` | a short list, 3 to 5 points only, each point slide with label `N: short title` and a monologue body; neighbouring point slides use different shapes (see 3) | `1: ...` to `5: ...` |

Per pack (6 options): at least 4 different structures, none more than twice, `short_list` at most once, and the three options of one topic use three different structures. The cover never promises "N דברים" unless the structure is `short_list`.

### 2. Slides

- 9 or 10 slides per option: cover, 7 or 8 story slides, the CTA (30 Oct 2026: Instagram through Postiz takes at most 10 images; packs written before then may have up to 12, and one story slide is dropped when such an option is produced). Roles: `hook` (slide 1), `beat` (story slides), `turn` (optional, the slide that turns back to the parents just before the CTA), `story_cta` (last).
- Slide fields: `number`, `role`, `headline` (may be `""` only on `letter` body slides), `body`, optional `label` (up to 28 characters), and `scene` on every slide from 2 to the last (the picture brief for that slide, see 4).
- Slide 1 `body` is the cover pill: up to 34 characters (for example `מה היה פעם, ומה קורה לי עכשיו`).
- Story slides carry 15 to 50 words (headline + body, markup not counted). This replaces the 25-word cap for story packs.
- Lines are broken by hand: every body line at most 38 characters and 12 words (markup not counted), so the renderer never wraps a line itself. Headlines up to 2 lines of up to 26 characters.

### 3. Body markup and slide shapes

- `## text` alone on a line: a small gold label (up to 26 characters), for example `## מה יעזור לי:`, `## מה אתם רואים:`, `## מה קורה לי בפנים:`, `## אני עונה:`.
- `> ״...״` alone on a line: a cream card with a sentence the parent can say. At most one per slide.
- `**word**`: gold emphasis, at most 2 per slide (her heavy-bold words).
- An empty line: a paragraph gap.

Shapes to rotate inside a carousel so no two neighbouring story slides look alike: a short monologue; short beats on their own lines ("אתמול הוא היה פה. / היום הוא איננו."); `## מה אתם רואים:` then `## מה קורה לי בפנים:`; a sentence to say on a card; the parent's question as the headline.

### 4. One picture per slide

- `option.image` stays the cover brief (slide 1) and `option.character_anchor` stays the characters. Every slide from 2 to the last has `scene`: `{"action": "...", "setting": "..."}` in English, one concrete moment that matches that slide (same characters, same home, 3D animated). The CTA slide's scene is a calm, warm resolution.
- Every scene keeps the upper third of the frame calm (a wall or soft background, no faces or hands there) and asks for no words, letters or numbers anywhere.
- Production makes the cover first and every other slide from the approved cover as the reference image (same characters). Since 30 Oct 2026 Claude makes them in ChatGPT in Yarin's Chrome, free (README section 2b, `scripts/chatgpt_pictures.py`); with `picture_backend` "fal" in `production.json` the fal text-to-image and edit endpoints make them as before.

### 5. Facts

- Every "מה יעזור לי" (or `## אני עונה:`) action and every statement about why a child does something is listed in `claims` with its slide number and source ids, as now.
- The child's story lines (what happened at 13:30, what the room looked like, how it felt) are the imagined voice of this one child: no claim needed, but never a statement about children in general.

### 6. The look

`compose_slides.py --look story` (the default for story packs): Lotem's text treatment in lumebook.com's palette and font: an ink #0B0518 veil over each slide's picture, cream #F8F0E1 type in Varela Round (the site's font, `assets/fonts/VarelaRound-*.woff2`), gold #E6B762 tags, labels, emphasis and save button, soft gold #F3D9A1 for quoted speech, a cream card for `> ` lines, the cover pill in gold, the letter structure on a cream sheet in ink. No logo, handle or swipe arrow. Reference implementation: `media/projects/2026-10-29-lotem-format-carousels/render.py`.

### 7. The book link CTA over the booklet (Yarin, 30 Oct 2026)

Yarin, after the Lotem CTA and caption study (`research/lotem-lerner-carousels/README.md`): "i want the cta to point to a book that might help them with x problem and then theyll get a link to the website"; the wording and the look the same afternoon ("אפשר גם לעזור להם עם X בעזרת ספר מותאם אישית / תכתבו X ואשלח לכם קישור להכנת הספר", an open booklet "with a realistic image of the kid inside a small circle in the corner", "straight short arrows", "bigger, add a thin black outline"), then "great implement in novembers batch". The approved reference: `approved/2026-12-06-kid-1/final/09.png`.

A pack has it with `"cta_style": "book_link"` at the top level, or one option with its own `"cta_style": "book_link"` (the 14 produced November carousels were moved one by one; the other options of their packs keep the save CTA). The validator then replaces the save for later and save and share rules with these.

- `cta`: two sentences on two lines, `carousel_lib.book_link_cta(problem, word, addressee)`: `אפשר גם לעזור להם עם הגמילה מהמוצץ בעזרת ספר מותאם אישית.` then `תכתבו "מוצץ" ואשלח לכם קישור להכנת הספר` (mom: `תכתבי`, `ואשלח לך`). The problem is the topic's everyday problem in 1 to 3 words, one headline line of 26 characters at most with `עם`.
- The caption ends with both lines (one line each); post_text ends the CTA line with 📖 instead of 🔖.
- Slide 10 is only the CTA: headline `אפשר גם לעזור להם / עם <problem> / בעזרת ספר מותאם אישית.`, body `תכתבו "<word>" / ואשלח לכם קישור להכנת הספר` (`book_link_slide`), the word in gold.
- `code_word`: the topic's own word (מוצץ, אח, עוגה), one word, never `ספר` (MeBook uses it) or `לומי`, the same on every book link option of a topic.
- Nothing of it before slide 10 or before the caption's last two lines. No brand, no catalogue title, no web address: the link to the website goes in the DM Yarin (or an automation he sets up) sends to each commenter. Nothing sends DMs yet.

**The booklet** (`option.booklet`, made at production, not in the pack):

- `RUN_DIR/booklet/booklet.png`: fal `nano-banana-2/edit`, 16:9, the run's cover picture as the reference: an open picture book from above, the pages edge to edge, the left page a 3D illustration of the same child in the topic's scene with the face turned to the viewer, the right page blank. `RUN_DIR/booklet/kid.png`: the same endpoint, 1:1, a realistic close-up photo of a child who looks like the cover's child. Prompts: `booklet_cta.py --prompts "<scene>"`. About $0.08 an image (6 Oct 2026 price, not checked since).
- `booklet`: `page_text` (up to 3 lines of 21 characters, set by Claude in Varela Round on the blank page, never asked of the model), `crop` ([x, y, w, h] of the two pages inside booklet.png, the spine in the middle), `face` ([x, y] of the child's face in that crop, 0 to 1, and an optional arrow scale, 0.5 for a small face). Look at the picture with a grid to set them.
- The slide (`compose_slides.booklet_html`): the last slide's own picture behind, a soft dark band above the booklet, the booklet 950 px wide at y 620 with rounded corners and a shadow, the page text centred on the white page, the photo in a 230 px white ringed circle over the booklet's top right corner, and two straight yellow arrows (#FFC21A, thin black outline): one at the child's face in the illustration, one up at the photo's chin. The CTA text shrinks to fit above the circle (66 to 50 px).
- One command per produced carousel: `python3 scripts/booklet_cta.py RUN_DIR --problem ... --word ... --page "a|b|c" --crop x,y,w,h --face x,y[,k]` or `--spec booklets-YYYY-MM.json`. It backs up to `versions/booklet-N/`, writes approved.json and the pack option, validates the pack and re-exports only the last slide. It never touches Postiz.
- Checks: `lib.book_link_cta_issues`, `lib.booklet_issues`, `tests/test_book_link.py`.
