# Black Friday and Hanukkah carousels, 2026

Yarin, 19 Nov 2026: "i need black friday and hannukah carousels / the black friday carousels end when black friday finishes / the hannukah one when hanukkah ends / schedule them to postiz on alternating days (i need the last black friday carousel to land on the day itself) / create one example for each to let me review, then well create the entire batch and then we can use photos and generate images to use for them and then schedule".

After the first review, the same day: "make black friday graphics black and white / hanukkah to be warm and magical / i want to pictures to be in the front in their own little boxes and themes ppattern for the bg / also give me 14 writen ideas for both / they dont have to be a carousel they can be one picture / push for 100% conversion friendly ad suggesting a better option for both", and "i want to promote this as well https://lumebook.com/IL/he/holiday-cards for hanukkah".

Order of work: (1) one example of each, for review ← **here, 19 / 11 / 2026 (second round)**; (2) the whole batch; (3) photos and made pictures (budget and yes first, OpenAI key rules); (4) Postiz.

## The format

The copy follows the test batch (`../../test-batch/2026-11/README.md`): one mom or one grandmother in the feminine singular, LumeBook may be named, a comment word for the link, Facebook gets its own text, and `test_batch.lint` checks it. The look is its own, in `scripts/seasonal_batch.py`: every picture sits in front in its own box over a themed pattern.

| type | look | what it sells | where it leads (`links` in each file) |
|---|---|---|---|
| `bf` בלאק פריידיי | black and white: dots and stripes, slides alternate black and white, photos in white (or black) boxes, a BLACK FRIDAY / בלאק פריידיי tape on the cover, the CTA and the ad | the personal book, awareness of the regular deal: no number or sale word until Yarin decides (`research/hanukkah-black-friday-2026/black-friday.md` 7.1) | the store, `utm_campaign=blackfriday26` |
| `hanukkah` חנוכה | warm and magical: an ember to plum glow, gold sparkles and small flames, photos in gold boxes with a glow, an arch on the cover | the free Hanukkah gift (personal greeting card or five-page colouring booklet); the book is the second step, through the holiday code on the same page | **lumebook.com/IL/he/holiday-cards**, `utm_campaign=hanukkah26` (Yarin, 18 and 19 / 11 / 2026: every Hanukkah piece promotes this page) |

A carousel file with `"format": "single"` is a one-picture post or ad: one `cta` slide with `headline`, `no` (the usual buy, crossed out in a dashed box), `yes` (the better option, over its photo with a tick) and `body` (the reason to act and the CTA's last line). Up to 34 words.

```bash
python3 carousel/carousel-pipeline/scripts/seasonal_batch.py status
python3 carousel/carousel-pipeline/scripts/seasonal_batch.py lint [KEY ...]
python3 carousel/carousel-pipeline/scripts/seasonal_batch.py render [KEY ...]
```

Keys: `bf-YYYY-MM-DD` / `hn-YYYY-MM-DD` (the day it goes out) and `bf-ad-N` / `hn-ad-N` (single pictures). Not in Carousel Machine yet; review from `slides/KEY/contact-sheet.png` or `slides/KEY/01.png`.

## What is built (all $0, real pictures only)

| key | kind | to | hook |
|---|---|---|---|
| `bf-2026-11-21` | carousel, 8 slides | grandma | סבתא, בלאק פריידיי. מה מכל העגלה יישאר עד פסח? |
| `bf-ad-1` | one picture, the better option | grandma | סבתא, העגלה כמעט סגורה? ✗ עוד צעצוע לעגלה ✓ ספר שהנכד הוא הגיבור שלו |
| `hn-2026-12-02` | carousel, 8 slides | mom | חופש חנוכה. מה עושים בבוקר? |
| `hn-ad-1` | one picture, the better option | mom | אמא, ברכה לנר ראשון בקבוצה המשפחתית? ✗ עוד סטיקר של סביבון ✓ כרטיס ברכה עם הפנים שלה |

`ideas.md`: 14 written ideas for each holiday (carousels and single pictures), every line linted the same way. Built with a one-off script; edit the md directly from now on.

Facts: the free gift page read in the browser on 19 / 11 / 2026 (lumebook.com/IL/he/holiday-cards); preview, delivery and the child on the cover from `shared/facts.json` `store_facts`; dates from `shared/facts.json` `key_dates`; Hanukkah 2026 checked by web search on 19 / 11 / 2026 (first candle at sundown Friday 04 / 12, ends Saturday 12 / 12); Black Friday is Friday 27 / 11 (the Friday after Thanksgiving, 26 / 11). Moran's quote is checked word for word against her recording (`quote_check`).

## The schedule (proposal, nothing sent)

Every other day, each series ending on its day, in the day's test carousel slot (`sites/content-calendar/posting-hours.json` `plan`):

| series | days | times |
|---|---|---|
| Black Friday, 4 | Sat 21 / 11, Mon 23 / 11, Wed 25 / 11, **Fri 27 / 11** | 12:30, 09:30, 09:30, 09:00 |
| Hanukkah, 6 | Wed 02 / 12, Fri 04 / 12 (first candle that evening), Sun 06 / 12, Tue 08 / 12, Thu 10 / 12, **Sat 12 / 12** | 09:30, 09:00, 09:30, 09:30, 09:30, 12:30 (before the holiday ends at nightfall) |

On 21, 23, 25 and 27 / 11 the test slot holds a November test carousel that is not in Postiz yet (calendar, 19 / 11 / 2026): Black Friday takes that slot. Nothing in December is planned yet. The two single-picture ads can also run as paid ads across their series.

## Copy evals (19 / 11 / 2026)

Every piece passes `seasonal_batch.py lint` (the test batch rules). On top of that, scored by hand:

- **Yarin's voice**: against his 43 rewrites in `.claude/skills/lumebook-hebrew-voice/examples/edits.jsonl` (voice status calibrated). His pattern: a value-first promise with a number instead of a mystery hook, plain action headlines, the "why" in plain words, no sources or cute fragments on slides.
- **The rubric**: `.claude/skills/lumebook-hebrew-voice/references/rubric.md`, 12 yes/no questions.
- **Conversion checklist** (one point each): names the buyer, a value-first hook, one better option, risk reversal (free preview or free gift), a date that is true, proof, one CTA with a reason to comment.

| key | before | after | what changed |
|---|---|---|---|
| `bf-2026-11-21` | 4 / 7 | 6 / 7 | cover now "4 בדיקות לפני שסוגרת את העגלה"; slide 7 answers the cover ("אז מה יישאר עד פסח?") instead of the vague "לא צריך לחכות לשישי"; CTA says the preview is free |
| `bf-ad-1` | 6 / 7 | 7 / 7 | "רואה את כל הספר" removed (the preview locks inner pages, `research/cro-crm/audit.md` A4); free preview and pay only if she loves it |
| `hn-2026-12-02` | 4 / 7 | 6 / 7 | cover now "חופש חנוכה? דפי צביעה שהיא בתוכם" with "בחינם"; slide 2 no longer repeats the cover; CTA names the gift and that it is free |
| `hn-ad-1` | 5 / 7 | 6 / 7 | adds the first candle date (Friday 04 / 12) |

What none of them has yet: real proof for Hanukkah (no real card or booklet made), and the Black Friday price. In ideas.md, BF 5, 9, 11 and 14 were rewritten for the same reasons.

## Before the batch

- Black Friday offer (other session, 19 / 11 / 2026, `shared/facts.json` `black_friday_2026`): Yarin set ₪119 for the first book and ₪99 for the second. Start and end dates, per order or per day, and how the store applies it are open; on 19 / 11 the store did not show the ₪99 yet. The campaign brief (`research/hanukkah-black-friday-2026/black-friday.md`, brief 3) wants 21 and 23 / 11 without price (`bf-2026-11-21` fits) and 25 and 27 / 11 with the offer; ready drafts with and without price are in `research/hanukkah-black-friday-2026/drafts/`. The test batch lint still fails ₪, מחיר, הנחה, מבצע: it stays that way until Yarin says yes to price outside reels for these keys. No countdown or deadline slide until the offer has an end date. Links use `utm_campaign=bf-2026` with `utm_content=dm-YYYYMMDD` / `post-YYYYMMDD`.
- Preview wording: never "see the whole book before paying" (inner pages are locked, `research/cro-crm/audit.md` A4). Say "התצוגה המקדימה בחינם, ומשלמת רק אם אהבת".
- The gift page shows a ₪99 book code to everyone (hanukkah.md 7.1); with a ₪99 second book on Black Friday, pick which number leads in late November.
- Hanukkah after 05 / 12 (last order day for a book in time for the holiday): only the free gift, never a book in time for the holiday.
- `hn-ad-1` shows the store's Hanukkah book cover in the ✓ box as a stand-in. It is not the greeting card: replace it with a real card before posting.
- Pictures for stage 3: no real photo of the card or the colouring booklet exists. Options: make a real gift on the page from a photo we have rights to (free, needs Yarin's OK for that photo), use the page's own five example pictures (their alt text says the people are made up for illustration), or make pictures with the OpenAI key (budget first).
- Postiz export: `postiz_export.py` adds the home page link to Facebook today; the Hanukkah posts need `links.facebook` (holiday-cards) instead, to wire before scheduling.
- Hanukkah visuals show the store's Hanukkah book covers with a menorah; the pattern itself has only sparkles and small flames. The no-religious-images rule (7 Nov 2026) is for the partners page only.
