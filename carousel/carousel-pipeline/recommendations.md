# Daily recommendation carousels: games and books

Every nightly run adds two complete carousels next to the six kid and expert options. They do not replace them, and the kid and expert rules (no brand, story CTA) stay as they are.

| file | what |
|---|---|
| `drafts/DATE/games-carousel.json` | 3 real games for one developmental stage |
| `drafts/DATE/books-carousel.json` | 3 real books for one developmental stage |
| `drafts/DATE/reco-assets/` | the product and cover images, plus the LumeBook image for slide 6 |
| `drafts/DATE/games/`, `drafts/DATE/books/` | `slides.html`, `01.png` to `07.png` (1080 x 1350), `contact-sheet.png`, `render-report.json` |

Structure: `reco.schema.json`. Rules: `scripts/reco_lib.py`. Slides and review section: `scripts/reco_render.py`. History: `reco-history.json`. Example that passes: `tests/fixtures/reco/`.

No image generation and no paid API in this format, ever. Nothing is posted. Each carousel gets its own minimal page, `drafts/DATE/games.html` and `books.html`, reached from tabs on `review.html` (קרוסלות · משחקים · ספרים). The page shows the title, status chips and the seven slides; text, products, sources, slide 6 and checks sit in dropdowns. Copy is editable in place when served by `review_server.py`.

## 1 · Stage

Each carousel picks one age range and one developmental need (`stage.skill`): language_vocabulary, fine_motor, gross_motor, imagination, early_literacy, problem_solving, memory, emotional_understanding, turn_taking, cooperation, independence, attention_self_regulation, early_numeracy.

- Ages are approximate. `stage.age_caveat` says so for Yarin, and slides 1 and 2 or the caption say it to parents (בערך, יש ילדים ש..., בקצב של כל ילד). The validator errors without it
- Every developmental claim maps to a source in `dev_sources` (CDC milestones, AAP and HealthyChildren, ZERO TO THREE, Child Mind Institute, KidsHealth, a government page, or peer reviewed research) with a verbatim quote. Slides 2, 3, 4 and 5 each need a `developmental` claim
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
- Per product record: exact Hebrew and original title, author and publisher (books) or manufacturer (games), official age from the product source (`official_age` with URL and quote), availability, popularity evidence, developmental relevance, source URLs and access dates, image source, confidence and limitations
- Never invent sales, rankings, reviews or popularity. No affiliate listicles or copied "best of" pages as evidence
- Exclude: unavailable or discontinued, international trend only, unsafe, official age that conflicts with the stage (the validator errors when the official minimum is above the stage), paid placements, near-identical products (`type` must differ inside one carousel)
- Books: prefer the Hebrew edition. Games: prefer Hebrew instructions or language-independent play
- Never imply LumeBook tested or endorsed a product

## 3 · The seven slides

| # | role | fields | job |
|---|---|---|---|
| 1 | hook | headline, body | the stage, the need or the age range. Specific, not clickbait, no LumeBook. Up to 12 words, main line up to 8 |
| 2 | frame | headline, body | what children practise at this stage and what makes a game or book suitable. Plain spoken Hebrew, sourced, ages approximate. Up to 30 words |
| 3 to 5 | recommendation | product_id, headline, age, why, how | `headline` contains the exact product title. `age` follows the official age. `why`: one concise reason that names the activity (waiting for a turn, matching, retelling, predicting, building, sorting, planning). `how`: one practical way to use it together. Up to 16 words each, 2 lines each |
| 6 | lumebook | headline, body | LumeBook (לומבוק) exactly once, relaxed and editorial: one more option for the same need, for example a story where the child is the hero as another chance to practise the same skill. No urgency, discounts, prices, free offers or promised results. A live-site `product_fact` claim and an approved LumeBook image (a real catalogue cover from lumebook.com or an asset already in the repo) |
| 7 | close | headline, body | a useful summary and a light save, share or comment prompt. No sales, no link, no brand |

Caption: 3 to 8 lines, the same Hebrew rules, no brand, no sales talk.

LumeBook appears on slide 6 only: never on slides 1 to 5, slide 7 or the caption.

## 4 · Images

- No generated images. Real product photos or covers from the publisher, the manufacturer, an official product page, Sifriyat Pijama or an established Israeli retailer (`source_type`). Never Google Images, a pin board or an unattributed repost (the validator blocks those hosts and image generators)
- Download the largest verified version into `reco-assets/`, record `image_url`, `page_url`, size and access date
- The renderer keeps the aspect ratio (object-fit contain in a white card), centres it, and keeps the text above and below. When the source put the product on a white band (Steimatzky's 1200x1600 canvases, for example), set `trim_padding: true` on that image and the renderer hides only the band (CSS object-view-box, the file is untouched). Never set it on a cover with its own light background: that would crop the cover `render-report.json` fails a distorted, off-centre, too small or overlapped image
- `rights_status`: `owned` (LumeBook's own), `cleared` (the page grants press or media use, or permission is documented), otherwise `rights_unverified`. An image being online does not make it cleared. Any `rights_unverified` image means the carousel is valid but not publish-ready, and the review page says so

## 5 · Hebrew

All the hard rules of the voice skill apply (no comma, period or em dash, one thought per line, no jargon, no guarantees, mom or both parents and never dad, never AI). A product title is exempt from the punctuation rule inside its own headline. Research notes and metadata use normal punctuation.

## 6 · Rotation (`reco-history.json`)

- No product twice within 30 days (any format) unless `seasonal_reason` is documented
- Same format: a skill may not return within its last 4 carousels, a stage id within 14 days, the hook structure of the previous carousel never repeats, an identical hook never repeats
- Warnings: the same age range as the previous carousel of the format, an author, publisher or manufacturer from the last 14 days, or twice inside one carousel
- Hook structures: `age_need_list`, `moment_question`, `skill_reveal`, `parent_quote`, `shelf_check`, `gift_list`, `observation`, `myth_vs_fact`

`nightly.py start` prints all of this under `recommendations`.

## 7 · Commands

```bash
python3 carousel/carousel-pipeline/scripts/nightly.py finish-reco carousel/carousel-pipeline/drafts/DATE
python3 carousel/carousel-pipeline/scripts/reco_lib.py carousel/carousel-pipeline/drafts/DATE/games-carousel.json
python3 carousel/carousel-pipeline/scripts/reco_render.py carousel/carousel-pipeline/drafts/DATE/books-carousel.json
python3 -m unittest discover -s carousel/carousel-pipeline/tests -v
```

`finish-reco` validates both files, renders both decks, rebuilds `review.html` and records history for the valid ones. It exits 1 on any error or render problem.

## 8 · What the review page flags

Each page shows its slide previews and, in dropdowns, the editable Hebrew copy and, for every recommendation: the exact title, the official and slide age, the developmental reason with sources, the popularity label and every Israeli signal with its quote, availability, the image source and rights status, confidence and limitations. Issues are grouped: missing Israeli popularity evidence, weak developmental sourcing, incorrect age fit, unavailable products, missing images, unverified image rights, repeated products, unsupported claims, Hebrew voice violations.
