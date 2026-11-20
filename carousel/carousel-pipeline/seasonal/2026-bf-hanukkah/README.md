# Black Friday and Hanukkah carousels, 2026

Yarin, 19 Nov 2026: "i need black friday and hannukah carousels / the black friday carousels end when black friday finishes / the hannukah one when hanukkah ends / schedule them to postiz on alternating days (i need the last black friday carousel to land on the day itself) / create one example for each to let me review, then well create the entire batch and then we can use photos and generate images to use for them and then schedule".

After the first review, the same day: "make black friday graphics black and white / hanukkah to be warm and magical / i want to pictures to be in the front in their own little boxes and themes ppattern for the bg / also give me 14 writen ideas for both / they dont have to be a carousel they can be one picture / push for 100% conversion friendly ad suggesting a better option for both", and "i want to promote this as well https://lumebook.com/IL/he/holiday-cards for hanukkah".

Order of work: (1) one example of each, for review (19 / 11 / 2026); (2) the whole batch, two options a day ← **here, 20 / 11 / 2026**; (3) photos and made pictures (budget and yes first, OpenAI key rules); (4) Postiz.

## The format

The copy follows the test batch (`../../test-batch/2026-11/README.md`): one mom or one grandmother in the feminine singular, LumeBook may be named, a comment word for the link, Facebook gets its own text, and `test_batch.lint` checks it. The look is its own, in `scripts/seasonal_batch.py`: every picture sits in front in its own box over a themed pattern.

| type | look | what it sells | where it leads (`links` in each file) |
|---|---|---|---|
| `bf` בלאק פריידיי | black and white: dots and stripes, slides alternate black and white, photos in white (or black) boxes, a BLACK FRIDAY / בלאק פריידיי tape on the cover, the CTA and the ad | the personal book and the offer, ₪119 first book and ₪99 second (price approved 20 / 11 / 2026; 21 and 23 / 11 without it); never a sale or discount word | the store, `utm_campaign=bf-2026` |
| `hanukkah` חנוכה | warm and magical: an ember to plum glow, gold sparkles and small flames, photos in gold boxes with a glow, an arch on the cover | the free Hanukkah gift (personal greeting card or five-page colouring booklet); the book is the second step, through the holiday code on the same page | **lumebook.com/IL/he/holiday-cards**, `utm_campaign=hanukkah26` (Yarin, 18 and 19 / 11 / 2026: every Hanukkah piece promotes this page) |

A carousel file with `"format": "single"` is a one-picture post or ad: one `cta` slide with `headline`, `no` (the usual buy, crossed out in a dashed box), `yes` (the better option, over its photo with a tick) and `body` (the reason to act and the CTA's last line). Up to 34 words.

```bash
python3 carousel/carousel-pipeline/scripts/seasonal_batch.py status
python3 carousel/carousel-pipeline/scripts/seasonal_batch.py lint [KEY ...]
python3 carousel/carousel-pipeline/scripts/seasonal_batch.py render [KEY ...]
```

Keys: `bf-YYYY-MM-DD-a|b` / `hn-YYYY-MM-DD-a|b` (the day it goes out and the option). Not in Carousel Machine: they live in the content calendar, with their own editor.

## What is built (all $0, real pictures only)

Yarin, 20 Nov 2026: "create 2 options for each for everyday of uploading / i want full editing capabilities". Every posting day has option a and option b (`bf-YYYY-MM-DD-a|b`, renamed from the first examples the same day: `bf-ad-1` is now `bf-2026-11-27-b`, `hn-ad-1` is `hn-2026-12-04-b`). Edit, pick, draw and approve them in the content calendar (לוח תוכן, the day's "קרוסלת חג" piece; `sites/content-calendar/README.md` "Black Friday and Hanukkah"); the day's pick, approvals and drawn hashes live in `state.json` here.

| key | day | kind | to | hook | comment word |
|---|---|---|---|---|---|
| `bf-2026-11-21-a` | 21 / 11 | offer post, book 15 | parents | יום הולדת בחודש הבא? דמיינו אותו מלך ליום אחד | מלך |
| `bf-2026-11-21-b` | 21 / 11 | offer post, book 64 | parents | יום הולדת בקרוב, והיא חולמת על במה? דמיינו אותה כוכבת קיי פופ | במה |
| `bf-2026-11-22-a` | 22 / 11 | offer post, book 49 | parents | שני ילדים בבית? דמיינו את הגדולה טסה למאדים | מאדים |
| `bf-2026-11-22-b` | 22 / 11 | offer post, book 67 | parents | שני ילדים בבית? דמיינו את הקטן בפארק הדינוזאורים | דינוזאור |
| `bf-2026-11-23-a` | 23 / 11 | offer post, book 23 | parents | כל היום עם כדור ברגליים? דמיינו אותו בטורניר הגדול | גול |
| `bf-2026-11-23-b` | 23 / 11 | offer post, book 22 | parents | מתה על סוסים? דמיינו אותה באורווה עם הסוסים | סוס |
| `bf-2026-11-24-a` | 24 / 11 | offer post, book 2 | parents | התינוק כבר בדרך? דמיינו אותו אח גדול וגאה | אח |
| `bf-2026-11-24-b` | 24 / 11 | offer post, book 2 | parents | עוד מעט היא כבר לא הקטנה? דמיינו אותה אחות גדולה וגאה | אחות |
| `bf-2026-11-25-a` | 25 / 11 | offer post, book 18 | parents | סבא וסבתא, מה הוא יהיה כשיגדל? דמיינו את הנכד רופא, טייס, צייר | נכד |
| `bf-2026-11-25-b` | 25 / 11 | offer post, book 49 | parents | סבא וסבתא, הנכד שואל על הכוכבים? דמיינו אותו טס בין כוכבי הלכת | כוכבים |
| `bf-2026-11-26-a` | 26 / 11 | offer post, book 13 | parents | ילד עם לב ענק? דמיינו אותו גיבור על של טוב לב | לב |
| `bf-2026-11-26-b` | 26 / 11 | offer post, book 47 | parents | יום ראשון במקום חדש? דמיינו אותה באקדמיה לגיבורות על | גיבורה |
| `bf-2026-11-27-a` | 27 / 11 | offer post, book 86 | parents | היום בלאק פריידיי, ועוד שבוע חנוכה דמיינו אותו מדליק את הנר הראשון | נר |
| `bf-2026-11-27-b` | 27 / 11 | offer post, book 86 | parents | מתנה לחנוכה? מזמינים עד 05 / 12 דמיינו אותה הגיבורה של חנוכה | סביבון |
| `hn-2026-11-28-a` | 28 / 11 | one picture | mom | בשבוע הבא נר ראשון. הברכה שלה כבר מוכנה? | שבוע |
| `hn-2026-11-28-b` | 28 / 11 | carousel, 6 slides | grandma | חנוכה בשבוע הבא. הנכד יקבל ממך כרטיס? | הנכד |
| `hn-2026-11-29-a` | 29 / 11 | carousel, 7 slides | mom | כרטיס ברכה או חוברת צביעה? | בחירה |
| `hn-2026-11-29-b` | 29 / 11 | one picture | grandma | סבתא, דמי חנוכה וכרטיס עם הנכד | מעטפה |
| `hn-2026-11-30-a` | 30 / 11 | carousel, 6 slides | mom | איזו תמונה מתאימה לכרטיס החנוכה? | פנים |
| `hn-2026-11-30-b` | 30 / 11 | one picture | mom | ליד שולחן החג, יש לה מה לעשות? | שולחן |
| `hn-2026-12-01-a` | 01 / 12 | one picture | mom | עד שישי בערב מתחילים מתמונה אחת | שישי |
| `hn-2026-12-01-b` | 01 / 12 | carousel, 7 slides | grandma | סבתא, ספר חנוכה לנכד, מהטלפון. מזמינים עד 05 / 12 | טלפון |
| `hn-2026-12-02-a` | 02 / 12 | carousel, 8 slides | mom | חופש חנוכה? דפי צביעה שהיא בתוכם | מתנה |
| `hn-2026-12-02-b` | 02 / 12 | one picture | grandma | סבתא, ברכת חנוכה עם הנכדה בפנים | ברכה |
| `hn-2026-12-03-a` | 03 / 12 | carousel, 7 slides | mom | מחר בערב נר ראשון. מה עוד נשאר להכין? | נרות |
| `hn-2026-12-03-b` | 03 / 12 | one picture | grandma | סבתא, ברכה שהנכד ישמור | לשמור |
| `hn-2026-12-04-a` | 04 / 12 | carousel, 7 slides | grandma | נר ראשון הערב. ספר חנוכה לנכדים? | חנוכה |
| `hn-2026-12-04-b` | 04 / 12 | one picture | mom | אמא, ברכה לנר ראשון בקבוצה המשפחתית? | כרטיס |
| `hn-2026-12-05-a` | 05 / 12 | one picture | mom | נר שני הערב. מה שולחים הפעם? | הערב |
| `hn-2026-12-05-b` | 05 / 12 | carousel, 6 slides | grandma | סבתא, איך מבקשים תמונה מההורים? | תמונה |
| `hn-2026-12-06-a` | 06 / 12 | one picture | mom | פספסת את ההזמנה? יש מתנה בלי שליח | שליח |
| `hn-2026-12-06-b` | 06 / 12 | carousel, 7 slides | mom | סבא וסבתא רחוקים? שלחי להם אותו | רחוקים |
| `hn-2026-12-07-a` | 07 / 12 | one picture | mom | נר רביעי הערב. מתנה קטנה, בלי לצאת מהבית? | רביעי |
| `hn-2026-12-07-b` | 07 / 12 | carousel, 7 slides | mom | אחרי הנרות והסופגניות, מה עושים עם הילדה? | צבעים |
| `hn-2026-12-08-a` | 08 / 12 | carousel, 7 slides | mom | שני ילדים, כרטיס חנוכה אחד | אחים |
| `hn-2026-12-08-b` | 08 / 12 | one picture | mom | ברכת חנוכה לגננת, מהילדה עצמה | גננת |
| `hn-2026-12-09-a` | 09 / 12 | one picture | mom | ברכת חנוכה לחברה הכי טובה שלה | חברה |
| `hn-2026-12-09-b` | 09 / 12 | carousel, 7 slides | mom | חמש מילים על כרטיס החנוכה שלה. מה כותבים? | חמש |
| `hn-2026-12-10-a` | 10 / 12 | carousel, 7 slides | grandma | הנכדים אצלך בחופש? דפי צביעה שהם בתוכם | סבתא |
| `hn-2026-12-10-b` | 10 / 12 | one picture | mom | עוד דף צביעה מהאינטרנט? | צביעה |
| `hn-2026-12-11-a` | 11 / 12 | one picture | mom | הערב הנר השמיני. הכרטיס שלה כבר מוכן? | שמיני |
| `hn-2026-12-11-b` | 11 / 12 | carousel, 6 slides | mom | עוד לא הספקת? כרטיס חנוכה בשלושה צעדים | שלושה |
| `hn-2026-12-12-a` | 12 / 12 | one picture | mom | היום האחרון של חנוכה. מה נשאר מהחג? | זיכרון |
| `hn-2026-12-12-b` | 12 / 12 | carousel, 7 slides | grandma | החג נגמר הערב. כרטיס עם הנכדה? | נכדה |

**Black Friday is one-picture offer posts (Yarin, 20 Nov 2026):** "i want black friday carousels instead to be one picture posts, everyday until the 27.11 (including the 27th) each of them should be about one icp, one book example and show the discount (first book 119 second 99) and say that its a ספר מותאם אישית בכיכוב הילד שלכם", then "it needs to be special, everyday invents a different story 'imagine your kid as...'". Every day from 21 to 27 / 11 has one ICP (`icp_he`: a birthday coming, two kids at home, a kid who loves football or horses, a baby on the way, grandparents, a kid with a big heart, a Hanukkah gift) and two options, each a made-up story ("דמיינו אותו...") around one real book, with what happens in it taken from that book's page on lumebook.com (read 20 Nov 2026). Layout `offer` (`seasonal_batch.py`): the story, one cover in its box, "ספר מותאם אישית בכיכוב הילד שלכם", the price tags `p1` / `p2`, the CTA. They talk to both parents (`addressee: parents`, plural, תכתבו); the grandparents day says "בכיכוב הנכד שלכם". Links go to the book's own page. Written by `make_bf_offers.py` (one-off; edit in the calendar from now on). Eight more store covers were fetched with Yarin's OK (`media/projects/2026-11-10-store-covers/README.md`). The earlier Black Friday carousels and single pictures are in `_to-delete/`.

Notes on the batch (20 Nov 2026): Every Hanukkah piece leads to holiday-cards and carries a stand-in `_note` (no real card or booklet picture yet). Some real photos in the Hanukkah pieces show a child's name printed on the book (`שני`, `אמילי ודויד`): check before posting.

`ideas.md`: 14 written ideas for each holiday (carousels and single pictures), every line linted the same way. Built with a one-off script; edit the md directly from now on.

Facts: the free gift page read in the browser on 19 / 11 / 2026 (lumebook.com/IL/he/holiday-cards); preview, delivery and the child on the cover from `shared/facts.json` `store_facts`; dates from `shared/facts.json` `key_dates`; Hanukkah 2026 checked by web search on 19 / 11 / 2026 (first candle at sundown Friday 04 / 12, ends Saturday 12 / 12); Black Friday is Friday 27 / 11 (the Friday after Thanksgiving, 26 / 11). Moran's quote is checked word for word against her recording (`quote_check`).

## The schedule (proposal, nothing sent)

One post a day, each series ending on its day (Yarin, 20 Nov 2026: "i want one black friday post a day until the 27th / and one hanukkah post a day until the end of hanukkah, after that we'll see"), in the day's old test carousel slot (`sites/content-calendar/posting-hours.json` `plan`, the test carousels are off the calendar since 20 Nov 2026):

| series | days | times |
|---|---|---|
| Black Friday, 7 | every day Sat 21 / 11 to **Fri 27 / 11** | 12:30, then 09:30 a day, 09:00 on the Friday |
| Hanukkah, 15 | every day Sat 28 / 11 to **Sat 12 / 12** (first candle at sundown Fri 04 / 12, last candle Fri 11 / 12, the holiday ends at nightfall Sat 12 / 12); 28 / 11 to 01 / 12 count down to the first candle | 09:30, 09:00 on Fridays, 12:30 on Saturdays |

Hanukkah starts on 28 / 11, the day after Black Friday ends (Yarin, 20 Nov 2026: "Fill those days", for the four days between the two series), so every day from 21 / 11 to 12 / 12 has a seasonal post. The first four days count down to the first candle ("בשבוע הבא נר ראשון", five, four and three days) and stay on the free gift; only `hn-2026-12-01-b` mentions the book, as the second step with the 05 / 12 order date and the free preview, worded as in `hn-2026-12-04-a`. After 12 / 12 nothing is planned. Every day has two options, a and b: pick one in the calendar. 05 / 12 and 12 / 12 are Saturdays (their posts go out at 12:30 in the plan). The two single-picture ads can also run as paid ads across their series.

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

- Black Friday offer (other session, 19 / 11 / 2026, `shared/facts.json` `black_friday_2026`): Yarin set ₪119 for the first book and ₪99 for the second. **Price on the Black Friday carousels and ads approved by Yarin on 20 / 11 / 2026** ("Yes, show the price"): `seasonal_batch.py lint` lets ₪ through for type `bf` only; מחיר, הנחה, מבצע and delivery cost stay banned, and Hanukkah keeps the full ban. `bf-2026-11-27-b` (was `bf-ad-1`) carries "ספר ראשון 119 ₪, השני 99 ₪" as its own line. The campaign brief (`research/hanukkah-black-friday-2026/black-friday.md`, brief 3) keeps 21 and 23 / 11 without price (`bf-2026-11-21-a` and `-b`) and 25 and 27 / 11 with the offer; the draft for 25 / 11 is in `research/hanukkah-black-friday-2026/drafts/`. Still open: start and end dates, per order or per day, and how the store applies it. On 19 / 11 the store did not show the ₪99 second book: check it does before anything with the price is posted. No countdown or deadline slide until the offer has an end date. Links use `utm_campaign=bf-2026` with `utm_content=dm-YYYYMMDD` / `post-YYYYMMDD`.
- Preview wording: never "see the whole book before paying" (inner pages are locked, `research/cro-crm/audit.md` A4). Say "התצוגה המקדימה בחינם, ומשלמת רק אם אהבת".
- The gift page shows a ₪99 book code to everyone (hanukkah.md 7.1); with a ₪99 second book on Black Friday, pick which number leads in late November.
- Hanukkah after 05 / 12 (last order day for a book in time for the holiday): only the free gift, never a book in time for the holiday.
- `hn-2026-12-04-b` (was `hn-ad-1`) shows the store's Hanukkah book cover in the ✓ box as a stand-in. It is not the greeting card: replace it with a real card before posting.
- Pictures for stage 3: no real photo of the card or the colouring booklet exists. Options: make a real gift on the page from a photo we have rights to (free, needs Yarin's OK for that photo), use the page's own five example pictures (their alt text says the people are made up for illustration), or make pictures with the OpenAI key (budget first).
- Postiz export: `postiz_export.py` adds the home page link to Facebook today; the Hanukkah posts need `links.facebook` (holiday-cards) instead, to wire before scheduling.
- Hanukkah visuals show the store's Hanukkah book covers with a menorah; the pattern itself has only sparkles and small flames. The no-religious-images rule (7 Nov 2026) is for the partners page only.

**Real books (20 Nov 2026, Yarin: "make the books look real"):** the offer layout shows the store cover on the realistic book render (`real_book.py cover`, the reels' books), drawn once per cover into `media/projects/2026-11-11-reel-broll-pool/drawn/real-cover-<asset key>.png` and redrawn when the cover file changes; white bars on a store cover are trimmed. The bottom line is "רוצים גם ספר בכיכוב הילדים?" (הנכדים on the 25th), never the preview.

**Seven looks and seven book models (20 Nov 2026, Yarin: "design each one differently, but not drastically ... using different book models as well"):** each offer post has `style` (s1 to s7: book side, pattern, white ground on s3 and s7, tape at the bottom on s4 and s7, round price stickers on s5, an outlined headline on s6) and the slide's `model` (real-cover, real-cover-2, real-flat, real-stack, real-open, real-standing, real-standing-2 from `real_book.py`; the open ones print the slide's `page` on the right page, taken from what the book's own page says). Both are picked in the content calendar's editor (עיצוב, דגם הספר).

**Hanukkah from 21 / 11, one picture each, comment word מתנה (20 Nov 2026 evening):** Yarin: "i want them to start from tomorrow" (chose "add 7 new days": `hn-2026-11-21` to `-27`, a and b, written by the session from the gift page facts, the countdown in their own words: 13 days on 21 / 11 down to "עוד שבוע" on 27 / 11), then "i want them all to be 1 image posts including the carousel ones that were already made, i need conversion to the free gift tool" and "tell them to write מתנה to get it". So all 44 Hanukkah options (21 / 11 to 12 / 12) are `format: single` (the ✗ / ✓ layout, the ✓ picture a stand-in until a real card or booklet exists), every one leads to holiday-cards only (the two that sold the book, `hn-2026-12-01-b` and `hn-2026-12-04-a`, were rewritten to the free card) and asks for "מתנה". The carousels as they were are kept in `versions/<key>/v1.json`. In the calendar the 21 to 27 / 11 pieces sit at 18:30 (16:00 on 23 and 25 / 11, where the kid carousel holds 18:30; 21:30 on Friday 27 / 11), because the Black Friday posts hold the morning slot; nothing is in Postiz.

**Hanukkah wording, same evening (Yarin, 20 Nov 2026):** "instead of כרטיס write ברכה" (ברכה, ברכת חנוכה, feminine agreement; כרטיס אשראי stays), 'delete "תמונה אחת, שם וחודש לידה." from hanukkah content' (every photo / name / birth month line is gone from the slides, captions and Facebook text), "dont say בחינם לגמרי only במתנה!" (no בחינם anywhere in the Hanukkah posts: "במתנה מלומיבוק לחנוכה", "רוצה ... במתנה?"), and "add a מתנה חינמית badge" (slide field `badge`, a round gold sticker on the corner of the ✓ picture, editable in the calendar; empty = no badge).
