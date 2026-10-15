# Topic bank

One topic per nightly pack, so the six candidates compare voice and angle rather than six unrelated ideas.

`scripts/nightly.py start` reads the table below, checks `history.json` and prints the topics ranked for tonight: eligible first (not used in the previous 14 packs), then in season for the review month, then the longest since last use. The validator rejects a pack whose topic id is not in this table or was used in the previous 14 packs.

## How to edit

- Add a row to add a topic. The id is lowercase with hyphens and must stay stable once used (history refers to it).
- `months` is a list of month numbers when the topic is most timely, or `any`.
- `code words` are old ideas for the comment keyword, kept for reference only: since 10 Oct 2026 the CTA word is always `לומי` (Yarin) and the rotation is off. Never use ספר: MeBook's creators already ask for "comment ספר" (carousel research v2, `research/carousel-research/lumebook-carousel-research.html`), so pick a milestone word.
- `books` are catalogue titles that may fit. Always check the exact title and story on the live site during the run; never invent a title or a feature.

## Topics

| id | topic | topic (en) | months | code words | books to check on lumebook.com |
|---|---|---|---|---|---|
| `new-sibling` | אח חדש והגדול שחוזר אחורה | new sibling and regression | any | אח / אחות / גדול | אח חדש · אחות חדשה |
| `gan-separation` | פרידה בבוקר בגן | separation at kindergarten drop-off | 8, 9, 10 | גן / פרידה / לב / בוקר | לב האומץ של אלי · הגן הקסום של הגדולים |
| `fear-of-dark` | פחד מחושך | fear of the dark | 10, 11, 12, 1, 2 | חושך / לילה / פנס | check catalogue |
| `pacifier-weaning` | פרידה מהמוצץ | pacifier weaning | any | מוצץ / ביי | ביי ביי מוצץ · עץ המוצצים |
| `toilet-setbacks` | פספוסים אחרי גמילה | toilet setbacks after potty training | any | גמילה / סיר | check catalogue |
| `sibling-conflict` | מריבות בין אחים | sibling conflict | any | אחים / ריב | check catalogue |
| `big-feelings` | מכה נושך או צועק | hitting biting or shouting | any | כעס / רגש | check catalogue |
| `transitions` | מסרב לעבור מפעילות לפעילות | refusing transitions | any | מעבר / עוד | check catalogue |
| `same-story` | רוצה את אותו סיפור שוב ושוב | wanting the same story again | any | שוב / סיפור | check catalogue |
| `sorry-on-command` | קשה לו להגיד סליחה | difficulty apologising on command | any | סליחה | check catalogue |
| `cautious-child` | ילד זהיר מול אתגר חדש | cautious children and new challenges | any | אומץ / מגלשה | לב האומץ של אלי |
| `first-grade-decompression` | פריקה אחרי יום בכיתה א׳ | first grade decompression after school | 9, 10, 11 | כיתה / בסדר | שלום כיתה א׳ |
| `bedtime-stalling` | עוד כוס מים לפני השינה | bedtime stalling | any | מים / לילה / שינה | check catalogue |
| `birthday-expectations` | יום הולדת שלא הולך לפי התוכנית | birthday expectations | any | הולדת / עוגה | check catalogue (birthdays category) |
| `left-out` | הרגיש שלא שיתפו אותו | feeling left out | any | חבר / לבד | חברים צבעוניים |
| `grandparents-gifts` | סבא וסבתא שואלים מה לקנות | grandparents as gift buyers | 11, 12 | סבתא / נכדים / מתנה | check gifts page |

## Selection rules

- Match the season, the Israeli calendar and the current LumeBook catalogue when relevant
- Rotate between awareness, consideration and product adjacent topics
- A hook family may appear at most twice inside one pack, and a family that was already published twice in the last 7 days is blocked (selections are recorded when an option goes to production)
- Never invent a book title or feature
- Check time sensitive product details against the live site before using them
- Keep the product out of slides 1 to 6; it appears on slide 7
