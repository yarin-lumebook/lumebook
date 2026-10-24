# Topic bank

Since 24 Oct 2026 every pack (one per day) has two topics, each tied to a best-selling book (see "Best-selling books"), with three child-voice options on each: six options a day to choose one from. Yarin, 24 Oct 2026, after the carousel audit: "Keep the child-voice numbered lists, on 2 topics that have a best-selling book (6 versions for each day (3 options for each) so i can choose the strongest one)". The weekly batch is 7 such packs, 14 different topics, and has no Israeli event slot any more. Packs made before then have one topic, six kid and expert options, and one event pack a week (see "Israeli events").

`scripts/nightly.py week-plan` reads the table below and "Best-selling books", checks `history.json` and gives every day two topics of two different best-selling books: in season first, then the longest since last use, no topic twice in a week, no book more than twice in a week, and no topic from the previous 3 packs. The validator rejects a two-topic pack whose topics are not best-seller rows or were used in the previous 3 packs. Older one-topic packs: not used in the previous 14 packs.

## How to edit

- Add a row to add a topic. The id is lowercase with hyphens and must stay stable once used (history refers to it).
- `months` is a list of month numbers when the topic is most timely, or `any`.
- `code words` are old ideas for the comment keyword, kept for reference only: since 10 Oct 2026 the CTA word is always `לומי` (Yarin) and the rotation is off. Never use ספר: MeBook's creators already ask for "comment ספר" (carousel research v2, `research/carousel-research/lumebook-carousel-research.html`), so pick a milestone word.
- `books` are catalogue titles that may fit. Always check the exact title and story on the live site during the run; never invent a title or a feature.

## Topics

| id | topic | topic (en) | months | code words | books to check on lumebook.com |
|---|---|---|---|---|---|
| `new-sibling` | אח חדש והגדול שחוזר אחורה | new sibling and regression | any | אח / אחות / גדול | אח חדש · אחות חדשה |
| `new-sibling-coming` | מכינים את הגדול לתינוק שבדרך | preparing the older child for the baby on the way | any | אח / תינוק | אח חדש · אחות חדשה |
| `new-sibling-jealousy` | מקנא בתינוק החדש | jealous of the new baby | any | אח / קנאה | אח חדש · אחות חדשה |
| `gan-separation` | פרידה בבוקר בגן | separation at kindergarten drop-off | 8, 9, 10 | גן / פרידה / לב / בוקר | לב האומץ של אלי · הגן הקסום של הגדולים |
| `fear-of-dark` | פחד מחושך | fear of the dark | 10, 11, 12, 1, 2 | חושך / לילה / פנס | check catalogue |
| `pacifier-weaning` | פרידה מהמוצץ | pacifier weaning | any | מוצץ / ביי | ביי ביי מוצץ · עץ המוצצים |
| `pacifier-first-nights` | הלילות הראשונים בלי מוצץ | the first nights without the pacifier | any | מוצץ / לילה | ביי ביי מוצץ |
| `toilet-setbacks` | פספוסים אחרי גמילה | toilet setbacks after potty training | any | גמילה / סיר | עדן והחיות החופשיות - נפרדים מהטיטולים |
| `potty-start` | מתחילים להיפרד מהטיטול | starting to say goodbye to diapers | any | טיטול / סיר | עדן והחיות החופשיות - נפרדים מהטיטולים |
| `sibling-conflict` | מריבות בין אחים | sibling conflict | any | אחים / ריב | check catalogue |
| `big-feelings` | מכה נושך או צועק | hitting biting or shouting | any | כעס / רגש | check catalogue |
| `transitions` | מסרב לעבור מפעילות לפעילות | refusing transitions | any | מעבר / עוד | check catalogue |
| `same-story` | רוצה את אותו סיפור שוב ושוב | wanting the same story again | any | שוב / סיפור | חברים צבעוניים |
| `first-words` | המילים הראשונות | first words | any | מילה / תינוק | חברים צבעוניים |
| `baby-reading` | תינוק שלא יושב רגע עם ספר ביד | reading with a baby who will not sit still | any | קריאה / תינוק | חברים צבעוניים |
| `sorry-on-command` | קשה לו להגיד סליחה | difficulty apologising on command | any | סליחה | הלב של יובל · ארמון הנימוסים |
| `kindness-small-acts` | מגלה כמה כיף לעזור לאחרים | small acts of kindness | any | לב / עזרה | הלב של יובל |
| `cautious-child` | ילד זהיר מול אתגר חדש | cautious children and new challenges | any | אומץ / מגלשה | לב האומץ של אלי |
| `first-grade-decompression` | פריקה אחרי יום בכיתה א׳ | first grade decompression after school | 9, 10, 11 | כיתה / בסדר | שלום כיתה א׳ |
| `first-grade-mornings` | בוקר לחוץ לפני בית הספר | rushed school mornings in first grade | 9, 10, 11, 12 | בוקר / תיק | שלום כיתה א׳ |
| `first-grade-ready` | מתכוננים לכיתה א׳ | getting ready for first grade | 5, 6, 7, 8 | כיתה / תיק | שלום כיתה א׳ |
| `bedtime-stalling` | עוד כוס מים לפני השינה | bedtime stalling | any | מים / לילה / שינה | check catalogue |
| `birthday-expectations` | יום הולדת שלא הולך לפי התוכנית | birthday expectations | any | הולדת / עוגה | יום הולדת |
| `birthday-countdown` | סופר את הימים עד יום ההולדת | counting the days to the birthday | any | הולדת / ימים | יום הולדת |
| `birthday-at-gan` | חוגגים לה יום הולדת בגן | being the birthday child at gan | any | הולדת / גן | יום הולדת |
| `left-out` | הרגיש שלא שיתפו אותו | feeling left out | any | חבר / לבד | check catalogue |
| `grandparents-gifts` | סבא וסבתא שואלים מה לקנות | grandparents as gift buyers | 11, 12 | סבתא / נכדים / מתנה | check gifts page |
| `picky-eating` | אוכל רק פסטה ואורז | picky eating | any | צלחת / ארוחה | check catalogue |
| `screen-time-end` | בכי כשנגמר המסך | meltdown when screen time ends | any | מסך / טאבלט | check catalogue |
| `bad-dream` | מתעורר מחלום רע | waking from a bad dream | any | חלום / לילה | check catalogue |
| `making-friends` | קשה לו להתחבר לילדים חדשים | making new friends | any | חבר / גן | check catalogue |
| `losing-games` | לא מסוגל להפסיד במשחק | not coping with losing a game | any | משחק / ניצחון | הטורניר הגדול של נוי |
| `giving-up` | מוותר מהר כשמשהו קשה | giving up fast when something is hard | any | ניסיון / התמדה | הטורניר הגדול של נוי |
| `whining` | מדבר בקול בכייני | whining | any | קול / בקשה | check catalogue |
| `doctor-visit` | פחד מרופא ומזריקה | fear of the doctor and shots | any | רופא / זריקה | check catalogue |
| `haircut-fear` | בוכה בתספורת | crying at haircuts | any | תספורת / שיער | check catalogue |
| `morning-dressing` | לא מתלבש בבוקר | morning dressing battles | any | בגדים / בוקר | check catalogue |
| `sharing-toys` | לא רוצה לתת לאף אחד את הצעצוע | not wanting to share toys | any | צעצוע / תור | הלב של יובל · ארגז הצעצועים המיוחד |
| `moving-home` | עוברים דירה | moving home | any | דירה / חדר | check catalogue |
| `public-tantrum` | התפרצות באמצע הסופר | tantrums in public | any | סופר / התפרצות | check catalogue |
| `own-bed` | עובר למיטה של ההורים בלילה | coming into the parents' bed at night | any | מיטה / לילה | check catalogue |
| `toothbrushing` | מלחמה על צחצוח שיניים | toothbrushing battles | any | שיניים / מברשת | check catalogue |

## Best-selling books (Yarin, 24 Oct 2026)

Every pack's two topics come from this table: the catalogue books with 50 or more paid orders of all time in the admin export of 12 Oct 2026 (`docs/lumebook-sales-data-decisions-2026-10-12.md`, internal: keep these numbers off public pages). Book numbers and what each book is about were read on the live book pages on 24 Oct 2026 (lumebook.com/IL/he/books/<book>). אח חדש and אחות חדשה are one book in two versions, counted together. Custom stories (237 orders) are not a catalogue book and have no topic. The carousels still never name a book: the book only decides the topic.

`scripts/nightly.py week-plan` reads the topics cell. To add a topic for a best-selling book, add its row to the Topics table and its id here.

| book | title | orders | what it is about (live page) | topics |
|---|---|---|---|---|
| 15 | יום הולדת | 262 | the birthday as a magical day, king or queen for a day | `birthday-expectations` `birthday-countdown` `birthday-at-gan` |
| 13 | הלב של יובל | 167 | real heroism through empathy, generosity and everyday kindness | `kindness-small-acts` `sharing-toys` `sorry-on-command` |
| 2 | אח חדש | 132 | preparing for and welcoming a new brother or sister (with אחות חדשה, book 7) | `new-sibling` `new-sibling-coming` `new-sibling-jealousy` |
| 29 | חברים צבעוניים | 118 | colours and animals for one-year-olds, simple repeating text | `same-story` `first-words` `baby-reading` |
| 41 | ביי ביי מוצץ | 86 | a goodbye ceremony for the pacifier | `pacifier-weaning` `pacifier-first-nights` |
| 43 | עדן והחיות החופשיות - נפרדים מהטיטולים | 66 | saying goodbye to diapers with zoo animals | `potty-start` `toilet-setbacks` |
| 10 | שלום כיתה א׳ | 57 | from gan to first grade, worries into excitement | `first-grade-decompression` `first-grade-mornings` `first-grade-ready` |
| 23 | הטורניר הגדול של נוי | 50 | a football-loving child learns perseverance and teamwork | `losing-games` `giving-up` |

## Israeli events (weekly batch, Yarin 16 Oct 2026; no event slot since 24 Oct 2026)

"I need the carousels to have social and event context about things that happen in Israel like holidays or special days, hard or exciting. I don't want all carousels to be about them, let's say about 10%-20% of the weekly batch."

Every weekly batch has one event pack (6 of 42 options) and its two games and books carousels (2 of 14), all about one thing that happens in Israel in the two weeks after the batch is made: a holiday, a special day, or a hard or exciting moment the whole country is talking about. That is about 14 percent; everything else uses the topics above. The event pack does not use a row of this table: its topic id is `event-` plus a short English slug (`event-hanukkah-2026`), and `topic.event` records the name, the date, the kind, the tone and a source read that day. If nothing fits the window, the slot falls back to the plan's regular topic and the reason says so.

Where to look (always confirm the date in a source you read that day, never from memory):

- Holidays and the Hebrew calendar: hebcal.com, the Ministry of Education school calendar on gov.il
- Special days: יום המשפחה, יום הזיכרון ליצחק רבין, ט״ו בשבט, הסיגד, the first day of school, the last day of school, the summer break, the first rain
- Hard or exciting moments: a national news event that families with young children are living through (an escalation, sirens, evacuations, a disaster; a big sports win, a national celebration). Read Israeli news (ynet, Kan, Haaretz, Mako) and an official source for how to talk with children (the Ministry of Education psychological service, the Ministry of Health, NATAL or ERAN for hard moments)

How to write it:

- Hard moments: what children may feel and what parents can say and do, from the official guidance. No graphic detail, no politics, no fear or blame aimed at the parent, nothing the child did wrong. Never a joke or a sales angle on a hard day; the story offer on slide 10 stays gentle
- Exciting moments and holidays: the child's view of the day, rituals the family can do, a feeling to name
- The two games and books carousels of the event pack pick games and books that fit the event (a holiday's books, games for a long break at home), still for one developmental stage, and record the same `event`

## Selection rules

- Match the season, the Israeli calendar and the current LumeBook catalogue when relevant
- Rotate between awareness, consideration and product adjacent topics
- A hook family may appear at most twice inside one pack, and a family that was already published twice in the last 7 days is blocked (selections are recorded when an option goes to production)
- Never invent a book title or feature
- Check time sensitive product details against the live site before using them
- Keep the product out of slides 1 to 6; it appears on slide 7
