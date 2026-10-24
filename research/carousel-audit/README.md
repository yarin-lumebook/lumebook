# Carousel audit

What every published LumeBook Instagram carousel was, how it did, and how each one scores as a creative. Started 24 Oct 2026. Local only: it holds Instagram numbers and sales figures, so keep it off public pages.

## Files

| File | What it is | Edit it? |
|---|---|---|
| `exports/*.csv` | Meta post exports as downloaded | Add new ones with `import` |
| `data/carousels.json` | One entry per published carousel: topic, hook, format, audience, CTA, slide folder, hand counts (parent comments, code-word comments, DM links, orders) | Yes |
| `data/scores.json` | Creative scores, 1 to 10 on `src/rubric.md`, with what worked, what failed and the fix | Yes |
| `data/rules.json` | Timezones, Yarin's own like and save per post, the 7-day rule, thresholds, UTM format | Yes |
| `data/books.json` | Carousel topic to store book page, for the link maker | Yes |
| `data/posts.json` | Every post in every export, latest numbers plus one snapshot per export | No, built |
| `carousel-inventory.csv` | The inventory, one row per carousel, with the full caption | No, built |
| `performance-ranking.csv` | Ranking and rates (per 1,000 reach and as %), flags | No, built |
| `creative-audit.md` | Scores, flags, carousel by carousel notes, rubric | No, built |
| `out/hook-results.preview.json` | 7+ day old pipeline carousels in the format of `carousel/carousel-pipeline/hook-results.json` | No, built |

## Commands

```
python3 research/carousel-audit/src/audit.py import ~/Downloads/<export>.csv   # copy it in, rebuild, list what is new
python3 research/carousel-audit/src/audit.py status                           # new posts, missing scores, young posts, admin checks
python3 research/carousel-audit/src/audit.py build                            # rebuild after editing data/
python3 research/carousel-audit/src/audit.py link pacifier-weaning            # tagged dm, bio and story links (today)
python3 research/carousel-audit/src/audit.py link --carousel 2026-10-20-pacifier --medium dm
python3 research/carousel-audit/src/audit.py hook-results --write             # copy results into the pipeline's log
```

`hook-results --write` changes the Carousel Machine's own results file, which can move hook formulas in its hook bank, so it only runs when asked.

## Adding a new export or carousel

1. Export from Meta with the date range starting at the account's first post (lifetime numbers per post) and run `import`. An older export stays in `exports/`; the latest one wins per post.
2. `import` prints `NEW` for every carousel without an inventory entry, with a guess at its slide folder in `carousel/carousel-pipeline/approved/*-all/`. Look at the slides, add the entry to `data/carousels.json` and score it in `data/scores.json` on the rubric. For Carousel Machine posts set `pipeline_run`: the hook fields are read from its `approved.json`.
3. Count comments by hand on the post (parent comments without LumeBook's replies, code-word comments, distinct people) and fill `manual`.
4. `build`. Posts under 7 days old stay unranked until a later export.

## Rules the numbers follow

- Export times are US Pacific; the importer converts them to Israel time (`data/rules.json`).
- Yarin likes, reposts, sends to themself and saves every post (24 Oct 2026): 1 like and 1 save come off every post. Shares stay as reported.
- No link had a UTM before 24 Oct 2026, so visits and orders per carousel are unknown. From now on send the link from `link`; the store's code records UTMs when a book is created (`docs/lumebook-sales-data-decisions-2026-10-12.md`), and Yossi can pull books started and orders by `utm_campaign`.
- Instagram has no per-slide numbers. Nothing here estimates swipe-through.
- Scores are judgement, not measurement. Do not cite them as evidence that a post performs.

## Still to do

- Run `import` on the full-history export Yarin sends after 31 Oct, add the pre-October carousels to the inventory and score them.
- Then write `winning-patterns.md`, `carousel-playbook-v2.md` and `next-10-carousel-experiments.md`.
- Check the admin for orders from the two parents who got a link (sorry and pacifier posts) and set `manual.orders_matched`.
