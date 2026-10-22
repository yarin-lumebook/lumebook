# Daily recommendation carousel: games and books together

Every nightly run adds one complete carousel of games and books next to the six kid and expert options (Yarin, 14 Oct 2026: "combine the book and games to one carousel. 10-20 slides", then "cap it to 7-9 books and games"). It does not replace them, and the kid and expert rules (no brand, story CTA) stay as they are.

| file | what |
|---|---|
| `drafts/DATE/reco-carousel.json` | `"format": "mixed"`: 7 to 9 suggestions for one developmental stage and theme: at least 3 real games, at least 3 real books, plus the LumeBook book (10 to 12 slides) |
| `drafts/DATE/reco-slots.json` | tonight's random draw of the size, `{"mixed": N}` (written by `nightly.py start`, kept on reruns, enforced by the validator) |
| `drafts/DATE/reco-assets/` | the product and cover images, plus the LumeBook catalogue cover |
| `drafts/DATE/reco/` | `slides.html`, `01.png` to `NN.png` (up to 20, 1080 x 1350), `contact-sheet.png`, `render-report.json` |
| `drafts/DATE/reco.html` | the carousel's review page |

Nights up to 13 Oct 2026 have two separate carousels instead: `games-carousel.json` (format `games`) and `books-carousel.json` (format `books`), 3 to 7 suggestions each (6 to 10 slides), rendered into `games/` and `books/` with the pages `games.html` and `books.html`. They still validate, render and save edits exactly as before; the nightly run never writes them again.

Look (Yarin, 14 Oct 2026, "go back to cream"): the combined carousel sits on cream (#FAF6EF) with plain dark plum type on every slide but the close slide, which keeps its pastel purple collage layer and its look.

Structure: `reco.schema.json`. Rules: `scripts/reco_lib.py`. Slides and review page: `scripts/reco_render.py`. History: `reco-history.json`. Examples that pass: `tests/fixtures/reco/reco-carousel.json` (12 slides), and the older `games-carousel.json` and `books-carousel.json`.

No image generation and no paid API in this format, ever. Nothing is posted. The carousel gets its own minimal page, `drafts/DATE/reco.html`, reached from the tab משחקים וספרים on `review.html` (older nights show the tabs משחקים and ספרים instead). On a phone the slides sit in one row that scrolls sideways. The page shows the title, status chips and every slide with its text right under it; products, sources, LumeBook and checks sit in dropdowns. Served by `review_server.py`, the text under each slide and the caption are editable in place: ⌘S saves (backup in `versions/`, revalidate, re-render the PNGs, rebuild the page). Every changed line is logged to the voice skill's `examples/edits.jsonl` with its format, slide, role and field, and `nightly.py start` hands the latest 40 back under `recommendations.recent_edits_learn_from_these`, so the next night writes the way Yarin's edits sound.

## Carousel Machine for games and books (10 Oct 2026)

Yarin asked for the click baity approach on these carousels too (the rule order is the one in the lumebook-carousel skill: the hook, then the content, then the slide design). The count-and-product sentence is still Yarin's: `X משחקים וספרים לגילאי A-B ש...` (14 Oct 2026; older nights `X משחקי קופסא ש...` / `X ספרי ילדים ש...`), X is the number of suggestions with the LumeBook book counted and A-B the stage's ages (age_min-age_max, Yarin 14 Oct 2026). What changes:

- **The ending says the value (Yarin, 11 Oct 2026: "i want the hooks to focus on what value is it going to provide").** Say what the games or books help the children do, concretely: "שיעזרו להם לתכנן כמה צעדים קדימה", "שיעזרו להם לשתף פעולה ביחד" (the validator flags a hook with no value verb: שיעזרו, שעוזרים, שמתרגלים, שמלמדים). A scene ("שבהם הילדים מתכננים...") describes the content but does not say what the parent gets, so it is the second choice. Still the wording rules of section 1 (מתרגלים, הזדמנות ל, יכול לעזור) and still mapped to a developmental source: a louder ending the source does not support is cut. Never a promise about what the games or books will do to the children
- **Three wordings, calm to loud.** Write at least three versions of the hook, keep the loudest one that the source supports, and list all of them in `hook_alternatives` (the chosen one is slide 1). The review page shows them in a dropdown so Yarin can swap
- **`highlight` on the hook and the frame slide** (and optionally on the close slide): 1 to 3 whole words of the headline, on one line, with their prefix letter, that get the colour block ("כמה צעדים קדימה", "לשתף פעולה", "ממשחקים עם חוקים"). On the hook the number is never part of it. A product title is never highlighted. Required in carousels generated from 2026-10-10 18:30 (`lib.BOLD_RULE_FROM`); older ones keep the classic look
- **The plain text look (Yarin, 14 Oct 2026: "from now on design the text of the carousels like these except the cta slide leave it as it is")**, the look of the combined carousel: every slide except the close one has centred Heebo Black headlines in dark plum (#1C1233), the number inside the hook sentence (not on its own big line), no colour block behind any word, secondary lines (age, why, how, frame body, LumeBook line) in Heebo Bold in a lighter plum (#3D2F5E), and the משחק / ספר tag as a small plum word above the title. The `highlight` fields are still written and validated (they drive the close slide and Carousel Machine), they are just not painted. The close slide renders exactly as before. Older games and books carousels keep the bold look below
- **The bold look** (`reco_render.py`, automatic when a slide has a highlight): the number of suggestions at 380px, the hook set up to 124px, the frame up to 112px, the highlighted phrase in a tilted colour block (violet; on older nights violet for games, pink for books), the arrow bigger. Product slides, the LumeBook slide and the collage close slide keep their layout. The picture on slide 1 stays the fan of real product covers: the face-to-camera thumbnail rule (hook-bank.md) is for the six kid and expert options only

## 1 · Stage

The carousel picks one age range and one developmental need (`stage.skill`), and every game and every book in it serves that same stage and theme: language_vocabulary, fine_motor, gross_motor, imagination, early_literacy, problem_solving, memory, emotional_understanding, turn_taking, cooperation, independence, attention_self_regulation, early_numeracy.

- Ages are approximate. `stage.age_caveat` says so for Yarin, and slides 1 and 2 or the caption say it to parents (בערך, יש ילדים ש..., בקצב של כל ילד). The validator errors without it
- Every developmental claim maps to a source in `dev_sources` (CDC milestones, AAP and HealthyChildren, ZERO TO THREE, Child Mind Institute, KidsHealth, a government page, or peer reviewed research) with a verbatim quote. Slides 1 and 2 and every product slide each need a `developmental` claim
- Wording: "מתרגלים", "הזדמנות ל", "יכול לעזור". Never a guarantee, a treatment, "smarter", "develops the brain" or "great for development"

## 2 · Products: popular in Israel, proven in Israel

The most important rule. International popularity never counts.

Israel-specific signals (`popularity_signals[].type`):

| strong (one is enough) | supporting (two independent ones) |
|---|---|
| `bestseller_list` current Israeli bestseller list | `multi_retailer` several independent Israeli retailers |
| `retailer_ranking` an Israeli retailer ranking, position 20 or better or top 10 percent (`rank`, `out_of`); lower = supporting | `hebrew_edition_established_publisher` |
| `sifriyat_pijama` chosen and distributed by Sifriyat Pijama | `prominent_placement`, `credible_recommendation`, `review_volume`, `social_attention`, `award_israel`, `library` |

- `popular_in_israel` only with one strong signal or two signals from different `group`s. Otherwise `available_in_israel` (a reviewer warning: replace it if a popular product fits)
- A signal counts only from an `.il` page or with `israel_specific: true` for an Israeli source elsewhere
- Rankings, placements and review counts must be read within 3 days of the run; availability too, with at least one Israeli retailer listing it now
- Per product record: `kind` (`game` or `book`), exact Hebrew and original title, author and the Hebrew edition's publisher (books) or manufacturer (games), official age from the product source (`official_age` with URL and quote), availability, popularity evidence, developmental relevance, source URLs and access dates, image source, confidence and limitations
- Never invent sales, rankings, reviews or popularity. No affiliate listicles or copied "best of" pages as evidence
- Exclude: unavailable or discontinued, international trend only, unsafe, official age that conflicts with the stage (the validator errors when the official minimum is above the stage), paid placements, near-identical products (`type` must differ inside one carousel)
- The mix (14 Oct 2026): at least 3 games and at least 3 books. All the popularity, availability, age, image and rights rules apply to every product, whatever its kind
- Books: prefer the Hebrew edition. Games: prefer Hebrew instructions or language-independent play
- Never imply LumeBook tested or endorsed a product

## 3 · How long: a random 7 to 9 suggestions, 10 to 12 slides

Every night `nightly.py start` draws how many suggestions the carousel has: a random number from 7 to 9 (Yarin, 14 Oct 2026: 10 to 12 slides). The LumeBook book counts as one of them (Yarin, 8 Oct 2026), so a carousel of N has N - 1 real products plus the LumeBook book, and N + 3 slides: hook, frame, the N suggestions, close. The draw is printed under `recommendations.suggestions.tonight` (with `products_tonight` and `slides_tonight`) and saved to `reco-slots.json`; the validator refuses a carousel of any other size. The order mixes games and books (Yarin, 16 Oct 2026: "in the book and games i want it to mix their order instead of games and then books"): never 3 of the same kind in a row, alternate where the counts allow, and the LumeBook book is always the second to last suggestion. Carousels made before 16 Oct 2026 show every game first, then the books, and stay valid. The hook is always one sentence (Yarin, 9 Oct 2026): `X משחקים וספרים לגילאי A-B ש...`, where X is N (the LumeBook book counted), the stage's ages right after it as «לגילאי A-B» (or «לגיל A»; Yarin, 14 Oct 2026: "add what ages are they suitable for", replacing the 9 Oct no-ages rule for this carousel), X stays inside the sentence, and the ending says what they help with (שיעזרו להם לספור ולזהות מספרים). Up to 12 words on the slide and up to 8 on the first line, as before. Map it to a developmental source (slide 1 claim).

Older nights: 3 to 7 suggestions of one kind, `X משחקי קופסא ש...` or `X ספרי ילדים ש...`.

`reco_lib.layout(N)` gives the slide roles for every size; the table below uses slide numbers for N suggestions.

## 4 · The slides

| # | role | fields | job |
|---|---|---|---|
| 1 | hook | headline only | the fixed sentence above, broken into lines in the headline, no body. Up to 12 words, first line up to 8 |
| 2 | frame | headline, body | what children practise at this stage and what makes a game or book suitable. Plain spoken Hebrew, sourced, ages approximate. Up to 30 words |
| 3 to N+2, except the LumeBook one | recommendation | product_id, headline, age, why, how | Games and books mixed, never 3 of the same kind in a row. On the combined carousel the renderer puts a small plum word above the title (משחק or ספר) from the product's `kind`; nothing to write. `headline` contains the exact product title. `age` follows the official age (shown as a plain line under the title, no badge). `why`: why it is good at this stage, starting from what the child practises (מתרגלים לחכות, לנחש, לספר), not how the game works. `how`: one practical way to use it together. Up to 16 words each, 2 lines each |
| N+1 (second to last suggestion) | lumebook | headline, body | The second to last suggestion, in Yarin's format (8 Oct 2026): headline `ספר של LumeBook`, body `סיפור מותאם אישית עם תמונה של הילדים שלכם` and `שבו הם... X` (plural, broken into lines that fit), where X is what that book's story is about. LumeBook exactly once, no urgency, discounts, prices or promises. The image is the cover of the catalogue book whose idea X states (`https://lumebook.com/book_covers/boy/B<id>_boy.avif` or `girl/B<id>_girl.avif`, LumeBook's own art, converted to PNG; Yarin, 10 Oct 2026: "i want the lumebook image to depict the idea of the caption"). The renderer shows the cover flat, in the same white card, size and place as the other books' covers (Yarin, 14 Oct 2026: "from now on i want the lumebook example to look flat like the rest of the book examples and not as a 3d object", replacing the 10 Oct 3D book); the cover itself is never changed or generated. The picture must show the line: write X from what that catalogue book is about, open the cover, and if it shows only part of the idea put that part in the line. Record `catalogue_book_id` and `image.depicts` (what the cover shows and how it is the line's idea); check that the book's age fits the carousel and that the cover has no garbled lettering (otherwise use the other variant or another book). Carousels generated before 2026-10-10 22:00 keep the homepage 3D hero render (`hero/series<N>-transparent-768.avif`). Write X to fit the carousel's topic (the skill the carousel is about) and keep it true: base it on a catalogue book that really covers that theme (read its description on lumebook.com, claim kind `product_fact`) or on the site's "the child is the hero" plus a developmental source for the activity |
| N+3 (last) | close | headline only | only the save and comment lines (for example תשמרו בשביל הערב הבא / מה הילדים שלכם מבקשים שוב ושוב? / ספרו בתגובות), no summary and no body. The background is a collage of every suggestion (all products and the LumeBook book) under a light pastel purple layer (Yarin, 9 Oct 2026): 3 x 4 tiles (at most 9 suggestions since 14 Oct 2026). The line ending in ? is the big one (it wraps if long), the lines around it are smaller, and under them sit Instagram-style save, send and comment icons, no labels. No sales, no link, no brand |

Caption: 3 to 8 lines, the same Hebrew rules, no brand, no sales talk.

Every slide sits on a light pastel of the LumeBook purple (#F1ECFF; Yarin, 9 Oct 2026). On the text-only slides the headline is big and the body is a quieter, smaller line with more space above it.

LumeBook appears on its one slide only (second to last suggestion): never on the other slides or the caption. Slides carry no badges or numbering; the arrow sits in the bottom middle.

## 5 · Images

- No generated images. Real product photos or covers from the publisher, the manufacturer, an official product page, Sifriyat Pijama or an established Israeli retailer (`source_type`). Never Google Images, a pin board or an unattributed repost (the validator blocks those hosts and image generators)
- Download the largest verified version into `reco-assets/`, record `image_url`, `page_url`, size and access date
- The renderer keeps the aspect ratio (object-fit contain in a white card), centres it, and keeps the text above and below. When the source put the product on a white band (Steimatzky's 1200x1600 canvases, for example), set `trim_padding: true` on that image and the renderer hides only the band (CSS object-view-box, the file is untouched). Never set it on a cover with its own light background: that would crop the cover `render-report.json` fails a distorted, off-centre, too small or overlapped image
- `rights_status`: `owned` (LumeBook's own), `cleared` (the page grants press or media use, or permission is documented), otherwise `rights_unverified`. An image being online does not make it cleared. Any `rights_unverified` image means the carousel is valid but not publish-ready, and the review page says so

## 6 · Hebrew

All the hard rules of the voice skill apply (no comma, period or em dash, one thought per line, no jargon, no guarantees, mom or both parents and never dad, never AI). Never write «יש שמגיעים לזה קודם ויש שאחר כך» (Yarin, 9 Oct 2026; the validator blocks it): say ages are approximate with בסביבות גיל X. Always plural (Yarin, 9 Oct 2026): talk to both parents (`addressee: parents`; שאלו, עצרו, תנו, שלכם) and about children in the plural (הילדים, הם, להם). The validator errors on a singular child (ילד, הילד), a singular you (שלך, לך) or a feminine singular command (שאלי, עצרי, תני), and warns on a singular pronoun (הוא, היא, לו, לה); quotes and product titles are exempt. A product title is exempt from the punctuation rule inside its own headline. Research notes and metadata use normal punctuation.

## 7 · Rotation (`reco-history.json`)

Each entry records the date, format (`mixed`, or `games` / `books` on older nights), stage, skill, hook and every product with its `kind`. The combined carousel rotates against every earlier entry, mixed, games and books alike:

- No product twice within 30 days (any format, by id or by the same Hebrew title) unless `seasonal_reason` is documented. `rotation.mixed.recent_titles` lists the titles of the recent entries
- A skill may not return within the last 4 nights, a stage id within 14 days, an identical hook never repeats
- Warnings: the same age range as the previous carousel, an author, publisher or manufacturer from the last 14 days, or twice inside one carousel
- An older games or books carousel (revalidated or edited) still rotates only against its own format
- Hook structure: always `count_ages_skill` (the fixed sentence); inside it, the loudest ending the source supports (Carousel Machine section above)

`nightly.py start` prints all of this under `recommendations`.

## 8 · Commands

```bash
python3 carousel/carousel-pipeline/scripts/nightly.py finish-reco carousel/carousel-pipeline/drafts/DATE
python3 carousel/carousel-pipeline/scripts/reco_lib.py carousel/carousel-pipeline/drafts/DATE/reco-carousel.json
python3 carousel/carousel-pipeline/scripts/reco_render.py carousel/carousel-pipeline/drafts/DATE/reco-carousel.json
python3 -m unittest discover -s carousel/carousel-pipeline/tests -v
```

`finish-reco` validates `reco-carousel.json`, renders the deck (a 20-slide render takes about two minutes), rebuilds `review.html` and `reco.html` and records history when it is valid. On an older night's folder (only `games-carousel.json` and `books-carousel.json`) it finishes those two the same way. It exits 1 on any error, render problem or missing file.

## 9 · What the review page flags

The page shows the slide count (and on the combined carousel how many games and books), its slide previews and, in dropdowns, the editable Hebrew copy and, for every recommendation: the kind, the exact title, the official and slide age, the developmental reason with sources, the popularity label and every Israeli signal with its quote, availability, the image source and rights status, confidence and limitations. Issues are grouped: missing Israeli popularity evidence, weak developmental sourcing, incorrect age fit, unavailable products, missing images, unverified image rights, repeated products, unsupported claims, Hebrew voice violations.
