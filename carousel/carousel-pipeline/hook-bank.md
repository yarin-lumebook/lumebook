# Hook bank

Every carousel option (7 slides, about one named Israeli girl or boy, talking to mom or both parents, never dad) picks one formula from this bank for slide 1, fills the slots for tonight's topic, and scores itself with the hook formula below. Since 8 Oct 2026 the nightly writer first builds a private **hook slate** of 12 candidates (6 kid, 6 expert), scores them, and only then writes the six options from passing candidates (section "Nightly hook slate").

`scripts/validate_pack.py` checks: the formula exists and fits the direction and family, every formula has an evidence row, no formula is used twice in a pack, the 6-point hook score passes, a `current_trend` formula past its review date is not used, slide 2 does not lean on slide 1, and (schema_version 3) the slate and the diversity of the six. `nightly.py start` prints the bank with each formula's evidence and status, and what was used recently, so the writer rotates. `nightly.py hooks` prints the bank status on its own.

Research behind this file: `research/hook-strategy-2026-10-08.md` (evidence tables, a 44-post documented sample, what was rejected and why). Older sources: playbook section 7 (`docs/lumebook-instagram-carousel-playbook-he.md`), carousel research v2 (`research/carousel-research/lumebook-carousel-research.html`), market notes (`research/carousel-playbook-research/market.md`), psychology notes (`research/carousel-playbook-research/psych.md`).

**Nothing here is proven for LumeBook.** Every formula carries `lumebook_hypothesis` until LumeBook's own results (`hook-results.json`) support it. "Trendy", "frequently observed", "high performing" and "caused better performance" are kept apart (labels below).

## נוסחת הפתיח החזק

<div dir="rtl">

**פתיח = רגע ספציפי + רגש או בעיה + שאלה פתוחה שהקרוסלה עונה עליה**

ציון 0 עד 2 לכל אחד מששת הסעיפים. עובר רק עם 9 ומעלה, ובלי אף 0. (הציון הזה נשאר על כל אופציה בחבילה. הסלייט הלילי מוסיף עליו ציון של 10 סעיפים, בהמשך.)

| סעיף | key | 2 | 1 | 0 |
|---|---|---|---|---|
| ספציפי | `specific` | רגע, שעה, מקום, גיל או משפט אמיתי של ילד | נושא ברור בלי רגע | כללי ("טיפים לפרידה") |
| נוגע | `feeling` | ההורה מרגיש את זה עכשיו | מעניין אבל רחוק | בלי רגש או בעיה |
| פער כן | `honest_gap` | פותח שאלה שהקרוסלה באמת סוגרת, ואומרים באיזו שקופית | רמז לשאלה | קליקבייט, או שהתשובה לא בקרוסלה |
| קצר ומדובר | `short_spoken` | עד 8 מילים, משפט שאומרים בקול | ארוך או קצת כתוב | נשמע כמו כותרת של מאמר |
| מסנן | `filters` | ברור למי זה (גיל, רגע, תפקיד) | חלקית | מתאים לכולם |
| לא פרסומת | `not_an_ad` | אין מוצר, מותג או הבטחה | נשמע קצת שיווקי | מכירה בשקופית הראשונה |

למה ככה:
- רגע וגיל ספציפיים עוצרים פחות אנשים, אבל כנראה את האנשים הנכונים (פלייבוק סעיף 7, השערה לניסוי; שפה קונקרטית: psych.md סעיף 4)
- פער סקרנות עובד כשנותנים רמז ומבטיחים תשובה, ופוגע באמון כשהוא נהיה קליקבייט (psych.md, סעיף 1: Menon & Soman 2002, Molyneux & Coddington 2020)
- נקודת המבט של הילד חוזרת בכמה מהקרוסלות הבולטות שנבדקו (market.md דפוס 5; research/hook-strategy-2026-10-08.md). זה דפוס שנצפה, לא הוכחה שזה עובד אצלנו

אסור בפתיח ובשקופית 2 (הבדיקה נכשלת): ״לא תאמינו״, ״לא תאמיני״, ״הסוד ש״, ״חובה לראות״, ״האם ידעתם״, ״בואו נדבר על״, ״היום נדבר״, ״כל מה שצריך לדעת״, ״המדריך המלא״, ״אתם עושים את זה לא נכון״, ״את עושה את זה לא נכון״, ״הטעות שכל ההורים״, ״חייבת לדעת״, ״לפני שיהיה מאוחר״, ״מה שאף אחד לא מספר״, ״תפסיקי״ או ״תפסיקו״ (כפנייה להורה), ״הורים טובים לא״, ״אם את לא״, ״אם אתם לא״.

</div>

## Evidence labels

| label | meaning | how a formula earns it |
|---|---|---|
| `platform_supported` | current first-party Instagram or Meta guidance | a Meta or Instagram page or statement that says it, read and quoted |
| `external_performance_pattern` | repeated in several relevant posts with visible performance evidence | 3+ relevant posts, above their account's own median, metrics read by us (still not proof of cause or conversion) |
| `current_trend` | appearing repeatedly in recent content, not shown to cause performance | seen in recent posts; **expires** at `review_by` (at most 120 days after research) and must be re-checked before use |
| `research_supported_mechanism` | credible behavioural, attention or communication research | a peer-reviewed or large field study read at least at abstract level (psych.md or the research report) |
| `lumebook_hypothesis` | a promising adaptation that still needs LumeBook testing | every formula, until validated |
| `lumebook_validated` | LumeBook's own results support it | only with entries in `hook-results.json` (see Measurement). The validator rejects the label without them |

No formula in this bank is `platform_supported` as a formula: we found no first-party Instagram guidance on how to write a carousel's first slide (research P19). Three rules are platform supported: slide 2 must work on its own (P1, P2: Meta's Feed system card predicts "How likely you are to swipe through the whole carousel"), no clickbait or engagement bait (P8, P10), and no headline split across slides 1 and 2 (P1 against P15).

## Formulas

`direction`: kid (child voice), expert, or both. `family` must match the option's `hook_family`. The Hebrew name, template, examples and guardrails of each formula are in "Formula cards" below.

| id | family | direction | formula | example | source |
|---|---|---|---|---|---|
| `child-not-because` | child_pov | kid | אני לא [התנהגות] בגלל [מה שההורה חושב] / אני [התנהגות] כי [הצורך האמיתי] | אני לא בוכה בגלל הגן / אני בוכה כי את הולכת | market.md pattern 5; research S1, S12 |
| `child-question` | child_quote | kid | ״[שאלה שילדים באמת שואלים]״ / אני שואל את זה [מתי] | ״מתי אתם באים לקחת אותי?״ / אני שואל את זה כל בוקר | playbook 7 #2 |
| `child-body-moment` | moment | kid | [מקום או רגע] / אני מרגישה את זה ב[גוף] | כבר במדרגות של הגן / אני מרגישה את זה בבטן | playbook 7 #1 |
| `child-letter` | child_pov | kid | אמא / רציתי להגיד לך משהו על [רגע] | אמא / רציתי להגיד לך משהו על הבקרים | research v2 (letters), market.md #1; research S1, S13, S14 |
| `child-hidden-half` | child_pov | kid | מה שאתם לא רואים / אחרי ש[רגע] | מה שאתם לא רואים / אחרי שאתם יוצאים מהגן | market.md pattern 5 |
| `child-numbered-ask` | child_pov | kid | אמא ואבא / [מספר] דברים שיעזרו לי / לפני ש[רגע] | אמא ואבא / 2 דברים שיעזרו לי / לפני שאתם שמים אותי בגן | Yarin, 8 Oct 2026; research S1 |
| `moment-time` | moment | both | [שעה] / [מה הילד עושה ברגע הזה] | 7:40 / נועם נצמד לרגל שלך בשער | playbook 7 #1; psych.md 4 |
| `sentence-we-all-say` | sentences_we_say | both | ״[משפט שכולנו אומרים]״ / כולנו אומרים את זה [מתי] | ״אין ממה לפחד מאמי״ / כולנו אומרים את זה בשער הגן | playbook 7 #5 |
| `instead-of-say` | sentences_we_say | expert | במקום ״[X]״ / נסו ״[Y]״ | במקום ״אין ממה לפחד״ / נסו ״אני רואה שקשה לך״ | research v2 (avital.bashan), market.md pattern 6; research S2, S3 |
| `reversal` | reframe | expert | [מה שכולנו עושים] / בדרך כלל [התוצאה ההפוכה] | עוד חמש דקות בשער / בדרך כלל רק מאריכות את הבכי | playbook 7 #4, research v2 (contrarian hooks) |
| `surprising-reframe` | surprising_statement | expert | [התנהגות שמדאיגה] / היא לא בהכרח [הפירוש המפחיד] | הבכי בשער / לא אומר שבחרתם גן לא נכון | playbook 7 #9 |
| `practical-question` | practical_question | expert | איך [פעולה] לילד בן [גיל]? | איך מסבירים לבן 3 מתי חוזרים? | playbook 7 #3 |
| `parent-identity` | parent_identity | both | לאמא של [ילד ברגע ספציפי] | לאמא של ילד שחזר לבכות בשער אחרי החגים | playbook 7 #6; psych.md 9 |
| `numbered-small-things` | gentle_outcome | expert | [מספר] דברים קטנים ל[רגע] / [למי] | 2 דברים קטנים לבוקר בשער / לגילאי 2 עד 5 | research v2 (lists with a comment word); research S5, S6, S7 |
| `milestone-week` | milestone | both | [רגע התפתחותי] / [זמן מדויק] | השבוע הראשון אחרי החגים / בשער הגן | playbook 7 #10 |
| `through-the-ages` | story | both | [שם] בגיל [גיל] / [מה קורה ברגע הזה] | מאיה בגיל 3 / בוכה בשער הגן | research v2; research S15 |
| `parent-worry-quote` | objection | expert | ״[החשש של ההורה במילים שלו]״ | ״אם אלך מהר הוא יחשוב שלא אכפת לי״ | playbook 7 #12 |
| `story-unresolved` | story | both | [רגע רגיל] ו[שם] [עושה משהו שלא נפתר] / [מה שעזר בסוף היה קטן] | ערב רגיל ונדב מסרב להיכנס למיטה / מה שעזר בסוף היה ממש קטן | research S2, S9, S10, S11; psych.md 10 |
| `just-so-you-know` | normalising | expert | רק שתדעי / [התנהגות מוכרת] זה [חלק נורמלי מהשלב] | רק שתדעי / פספוס אחרי חודשים של גמילה זה חלק מהדרך | research S16 |
| `positive-edition` | milestone | both | ״[אזהרה שכולם אומרים להורים]״ / הגרסה הטובה | ״חכי חכי שתגיע לגיל שלוש״ / הגרסה הטובה | research S17 |
| `parent-confession` | normalising | expert | ״[מחשבה שהורים מתביישים בה]״ / [משפט שמוריד בושה בלי עובדה] | ״אני מתגעגעת לגדול שלי״ / והוא יושב לידי על הספה | research S12, S13, S18 |
| `analogy-scene` | analogy | expert | דמייני ש[מצב מקביל מעולם המבוגרים] / [הפרט שעושה את זה קשה] | דמייני שמישהו לוקח לך את הטלפון / בלי להגיד מתי תקבלי אותו | research S8 |

## Evidence and rotation

One row per formula. `evidence` lists every label that applies (joined with +). `mechanism` lists the psychological jobs it can do (the slate candidate and the option pick one). `shape` is the surface form of slide 1. `slide2` lists the slide 2 moves that fit. `payoff` is the usual slide that answers the hook. `review_by` is when the evidence must be looked at again; a `current_trend` row past that date blocks the formula until it is re-checked.

| id | evidence | mechanism | shape | slide2 | payoff | researched | review_by |
|---|---|---|---|---|---|---|---|
| `child-not-because` | external_performance_pattern + research_supported_mechanism + lumebook_hypothesis | perspective_shift + reframe | negation | other_side + first_answer | 3 | 2026-10-08 | 2027-04-08 |
| `child-question` | research_supported_mechanism + lumebook_hypothesis | recognition + honest_curiosity | quote | name_trigger + zoom_in | 3 | 2026-10-08 | 2027-04-08 |
| `child-body-moment` | lumebook_hypothesis | recognition | time_place | zoom_in + name_trigger | 3 | 2026-10-08 | 2027-04-08 |
| `child-letter` | external_performance_pattern + research_supported_mechanism + lumebook_hypothesis | perspective_shift + recognition | address | scene_restart + first_answer | 3 | 2026-10-08 | 2027-04-08 |
| `child-hidden-half` | lumebook_hypothesis | perspective_shift | statement | zoom_in + other_side | 3 | 2026-10-08 | 2027-04-08 |
| `child-numbered-ask` | lumebook_hypothesis | practical_utility + perspective_shift | numbered | promise + first_answer | 4 | 2026-10-08 | 2027-04-08 |
| `moment-time` | research_supported_mechanism + lumebook_hypothesis | recognition | time_place | zoom_in + other_side + name_trigger | 3 | 2026-10-08 | 2027-04-08 |
| `sentence-we-all-say` | lumebook_hypothesis | recognition + reframe | quote | other_side + contrast | 3 | 2026-10-08 | 2027-04-08 |
| `instead-of-say` | external_performance_pattern + lumebook_hypothesis | practical_utility | contrast_pair | first_answer + contrast | 3 | 2026-10-08 | 2027-04-08 |
| `reversal` | lumebook_hypothesis | reframe | statement | contrast + first_answer | 3 | 2026-10-08 | 2027-04-08 |
| `surprising-reframe` | lumebook_hypothesis | reframe + reassurance | negation | name_trigger + first_answer | 3 | 2026-10-08 | 2027-04-08 |
| `practical-question` | lumebook_hypothesis | practical_utility + honest_curiosity | question | first_answer + promise | 4 | 2026-10-08 | 2027-04-08 |
| `parent-identity` | research_supported_mechanism + lumebook_hypothesis | identity_filter | identity_label | zoom_in + name_trigger | 3 | 2026-10-08 | 2027-04-08 |
| `numbered-small-things` | external_performance_pattern + lumebook_hypothesis | practical_utility | numbered | promise + contrast | 4 | 2026-10-08 | 2027-04-08 |
| `milestone-week` | lumebook_hypothesis | anticipation | time_place | name_trigger + zoom_in | 3 | 2026-10-08 | 2027-04-08 |
| `through-the-ages` | current_trend + lumebook_hypothesis | narrative_tension + recognition | ages_sequence | same_template | 3 | 2026-10-08 | 2027-01-08 |
| `parent-worry-quote` | lumebook_hypothesis | reassurance + honest_curiosity | quote | first_answer + other_side | 3 | 2026-10-08 | 2027-04-08 |
| `story-unresolved` | external_performance_pattern + research_supported_mechanism + lumebook_hypothesis | narrative_tension | story_open | scene_restart + zoom_in | 4 | 2026-10-08 | 2027-04-08 |
| `just-so-you-know` | current_trend + lumebook_hypothesis | reassurance | just_so_you_know | same_template + first_answer | 3 | 2026-10-08 | 2027-01-08 |
| `positive-edition` | current_trend + lumebook_hypothesis | anticipation + reframe | quote | same_template + contrast | 3 | 2026-10-08 | 2027-01-08 |
| `parent-confession` | external_performance_pattern + lumebook_hypothesis | reassurance | quote | first_answer + other_side | 3 | 2026-10-08 | 2027-04-08 |
| `analogy-scene` | lumebook_hypothesis | perspective_shift + reframe | imagine | scene_restart + first_answer | 3 | 2026-10-08 | 2027-04-08 |

Research ids (S1 to S18, P and M ids) point to the tables in `research/hook-strategy-2026-10-08.md`.

## Formula cards

Each card: Hebrew name, template, three examples (illustrative, written for this bank, not taken from any account), the moments it fits, the open question and where it closes, a slide 2 that stands alone, likely audience intent, risks and what is not allowed, signs it is going stale, and what to test. Examples marked (מקור) state something about children and need a sourced fact on slide 1 or 2 before use.

### Kid direction

**`child-not-because` · ״אני לא... אני...״**
<div dir="rtl">

- תבנית: אני לא [התנהגות] בגלל [מה שההורה חושב] / אני [התנהגות] כי [הצורך]
- דוגמאות: ״אני לא בוכה בגלל הגן / אני בוכה כי את הולכת״ · ״אני לא מפחדת מהחושך / אני מפחדת להיות בו לבד״ · ״אני לא דוחף את התינוק כי אני רע / אני דוחף כי אני מתגעגע אלייך״
- רגעים: פרידה, חושך, אח חדש, מכות, סירוב
- שאלה שנפתחת: אם זה לא X, אז מה כן? נסגרת בשקופית 3 (הצורך במילים של הילד)
- שקופית 2 (other_side): ״בשער את אומרת ״יהיה בסדר״ / ואני לא יודע מתי זה אחר כך״
</div>

- Intent: problem-aware parents in the moment. First-person singular wording was one of the more consistent positive cues in randomised headline tests (research M4), with small effects. Risk: the "real reason" is an imagined inner voice, so it must be framed as a possibility, never as what every child feels. Not allowed: a "real reason" that blames the parent ("כי את תמיד ממהרת"). Stale when: three packs in a row open with "אני לא". Test: negation hook vs the same carousel opening on the need ("אני בוכה כי את הולכת").

**`child-question` · ציטוט של שאלה**
<div dir="rtl">

- תבנית: ״[שאלה שילדים שואלים]״ / אני שואל את זה [מתי]
- דוגמאות: ״מתי אתם באים לקחת אותי?״ / אני שואל את זה כל בוקר · ״עוד סיפור אחד?״ / אני לא מבקש בגלל הסיפור · ״למה התינוק נשאר איתך כל היום?״ / אני שואלת את זה כל ערב
- שאלה שנפתחת: למה השאלה הזאת חוזרת ומה עונים? נסגרת בשקופית 3, תשובה בשקופיות 4 ו-5
- שקופית 2 (name_trigger): ״השאלה הזאת חזרה אחרי החגים / ״אחר כך״ זה המון זמן בגיל שלוש״
</div>

- Intent: recognition, high relevance. Caution: in one study of 1,828 news headline rewrites, headlines that were entirely a quote did worse (research M2); keep the second line as framing ("אני שואל את זה כל בוקר"), and test quote alone vs quote plus framing. Risk: the quote must sound like a child, not an adult writing a child. Not allowed: a funny quote that mocks the child. Stale when: every kid option opens with quotation marks. Test: question quote vs statement quote.

**`child-body-moment` · רגע בגוף**
<div dir="rtl">

- תבנית: [מקום או רגע] / אני מרגישה את זה ב[גוף]
- דוגמאות: כבר במדרגות של הגן / אני מרגישה את זה בבטן · כשהאור במסדרון נכבה / הלב שלי דופק חזק · כשאת לוקחת את המוצץ / הידיים שלי מחפשות אותו
- שאלה שנפתחת: מה היא מרגישה ומה יעזור? נסגרת בשקופית 3
- שקופית 2 (zoom_in): ״כל בוקר הפרידה אחרת / ואני לא יודעת מה יהיה היום״
</div>

- Intent: emotional recognition. Risk: inventing physical symptoms. Keep to ordinary sensations and never imply a medical sign. Not allowed: "כאב בטן" as a symptom to worry about. Stale when: the body word repeats (בטן) across packs. Test: body line vs no body line on the same moment.

**`child-letter` · מכתב קצר מהילד**
<div dir="rtl">

- תבנית: אמא / רציתי להגיד לך משהו על [רגע]
- דוגמאות: אמא / רציתי להגיד לך משהו על הבקרים · אמא ואבא / לפני שהתינוק מגיע יש לי בקשה · אמא / אחרי הגן אני מתפוצץ דווקא עלייך
- שאלה שנפתחת: מה הוא רוצה להגיד? נסגרת בשקופית 3
- שקופית 2 (scene_restart): ״בגן אני מחכה כל היום בתור / אז בבית כבר אין לי כוח לחכות״
</div>

- Intent: emotional, shareable to a co-parent. Evidence: Big Life Journal's "Dear Mom and Dad, I love you but..." (S1) and two other letter-to-a-parent carousels (S13, S14) did well against their accounts; the third uses a parent-to-parent voice. Risk: the letter is imagined; never present it as a real child or a testimonial. The child notices or needs, never accuses: if the mother is cast as the opponent, identification with the child may be blocked (research M11) and blame is discounted or provokes anger (M16, M17). Not allowed: guilt ("למה את אף פעם לא..."). Stale when: "אמא /" opens more than one option a night or more than twice a week. Test: letter vs moment-time on the same topic.

**`child-hidden-half` · מה שלא רואים**
<div dir="rtl">

- תבנית: מה שאתם לא רואים / אחרי ש[רגע]
- דוגמאות: מה שאת לא רואה / אחרי שאת יוצאת מהגן · מה שאתם לא רואים / אחרי שמכבים לי את האור · מה שאת לא רואה / כשכולם מסתכלים על התינוק
- שאלה שנפתחת: מה קורה כשההורה לא שם? נסגרת בשקופית 3. חובה שהתשובה תהיה מרגיעה או מעשית, לא מפחידה
- שקופית 2 (zoom_in): ״חמש דקות אחרי שהלכת / אני כבר ליד הקוביות״
</div>

- Intent: reassurance for worried parents. Risk: curiosity built on worry; the answer must be honest (sometimes the child calms quickly, sometimes not). Not allowed: implying something bad happens. Stale when: used for two topics in a row. Test: hidden-half vs child-letter.

**`child-numbered-ask` · שני דברים שיעזרו לי**
<div dir="rtl">

- תבנית: אמא ואבא / [מספר] דברים שיעזרו לי / לפני ש[רגע] (לאמא לבד: ״אמא / 2 דברים שיעזרו לי״)
- דוגמאות: אמא ואבא / 2 דברים שיעזרו לי / לפני שאתם שמים אותי בגן · אמא / 2 דברים שיעזרו לי / בלילה הראשון בלי מוצץ · אמא ואבא / 2 דברים שיעזרו לי / כשהתינוק בוכה בלילה
- שאלה שנפתחת: מה שני הדברים? נסגרת בשקופיות 4 ו-5 (דבר ראשון / דבר שני)
- שקופית 2 (first_answer): ״הכי קשה לי הרגע של הדלת / שם אני צריך אתכם הכי הרבה״
</div>

- Intent: solution-aware parents. Yarin's formula (8 Oct 2026); Big Life Journal used the letter-then-numbered-requests structure (S1). Risk: the number must match the solution slides. Not allowed: "אמא ואבא" when the addressee is mom only. Stale when: numbers open more than two options a night. Test: "2 דברים" vs letter without a number.

### Both directions

**`moment-time` · שעה ורגע**
<div dir="rtl">

- תבנית: [שעה] / [מה הילד עושה ברגע הזה]
- דוגמאות: 7:40 / נועם נצמד לרגל שלך בשער · 20:30 / שירה קוראת לך בפעם החמישית · 13:10 באיסוף / ואיתי לא מוכן לבוא איתך
- שאלה שנפתחת: למה זה קורה דווקא עכשיו ומה עושים? נסגרת בשקופית 3
- שקופית 2 (other_side): ״כבר באוטו הוא שואל / ״את נשארת קצת?״״
</div>

- Intent: in-the-moment parents. Concrete language is linked to attention and to feeling understood (psych.md 4). Risk: a time that is wrong for the topic. Stale when: digits open two options a night. Test: time hook vs identity hook (playbook N1).

**`sentence-we-all-say` · משפט שכולנו אומרים**
<div dir="rtl">

- תבנית: ״[משפט שהורים אומרים]״ / כולנו אומרים את זה [מתי]
- דוגמאות: ״אין ממה לפחד מאמי״ / כולנו אומרות את זה בשער הגן · ״תגיד סליחה עכשיו״ / כולנו אומרים את זה אחרי מכה · ״את כבר גדולה״ / כולנו אומרות את זה כשנולד התינוק
- שאלה שנפתחת: למה המשפט הזה לא עובד ומה במקומו? נסגרת בשקופית 3
- שקופית 2 (other_side): ״בשבילה הפחד בשער אמיתי לגמרי / ולכן ההרגעה לא נקלטת״
</div>

- Intent: recognition without blame. The "כולנו" must stay; "אתם אומרים" turns it into blame (playbook 7 #5). Stale when: quote shapes open more than two options a night. Test: "כולנו" vs no "כולנו".

**`parent-identity` · לאמא של**
<div dir="rtl">

- תבנית: לאמא של [ילד ברגע ספציפי]
- דוגמאות: לאמא של ילד שחזר לבכות בשער אחרי החגים · לאמא של בת 3 שמתעוררת כל לילה ב-2 · להורים של גדול שפתאום מבקש מוצץ
- שאלה שנפתחת: מה עובר עליו ומה יעזור? נסגרת בשקופית 3
- שקופית 2 (name_trigger): ״אחרי חופש ארוך / הרבה ילדים צריכים שוב זמן להתרגל״ (מקור)
</div>

- Intent: very high relevance, low reach (playbook 7 #6). Self-reference research supports tailoring to the reader (psych.md 9). Risk: too narrow a moment for the season. Stale when: the label repeats a moment from the last 14 days. Test: identity vs moment-time (N1 variant).

**`milestone-week` · רגע התפתחותי עם זמן**
<div dir="rtl">

- תבנית: [רגע התפתחותי] / [זמן מדויק]
- דוגמאות: השבוע הראשון אחרי החגים / בשער הגן · הלילה הראשון בלי מוצץ / אצל אלה בת 3 · שבוע לפני שהתינוק נולד / ונועם כבר שואל איפה הוא יישן
- שאלה שנפתחת: מה מחכה בשבוע הזה ואיך מתכוננים? נסגרת בשקופית 3
- שקופית 2 (name_trigger): ״אחרי שבועיים בבית / הבוקר הראשון מרגיש כמו התחלה מחדש״
</div>

- Intent: anticipation; fits the Israeli calendar. Risk: calendar facts need a source (topic.reason). Stale when: the date is past. Test: milestone vs practical-question for the same week.

**`through-the-ages` · גיל אחרי גיל** (current_trend, review by 2027-01-08)
<div dir="rtl">

- תבנית: [שם] בגיל [גיל] / [מה קורה ברגע הזה] (או בגוף ראשון: ״אני בת 5 / ...״)
- דוגמאות: מאיה בגיל 3 / בוכה בשער הגן · אני בן 4 / ואמא מביאה הביתה תינוק · אני בת 5 / ואמא מכבה לי את האור
- שאלה שנפתחת: מה ישתנה כשהיא תגדל ומה עוזר עכשיו? נסגרת בשקופית 6 (הגיל הבא)
- שקופית 2 (same_template): ״מאיה בגיל 4 / כבר נכנסת לבד ומנופפת״
</div>

- Intent: emotional, shareable. Seen in a Hebrew carousel told in the child's first person over ages (S15) and in Lovevery's "firsts" list (S17); no verified performance data for the Hebrew one. Risk: it pulls against the 7-slide arc (problem, two solutions); keep the ages to slides 1, 2 and 6. Stale when: the review date passes or the format shows up in most IL parenting feeds. Test: ages vs single moment.

**`story-unresolved` · סיפור שנעצר באמצע**
<div dir="rtl">

- תבנית: [רגע רגיל] ו[שם] [עושה משהו שלא נפתר] / [מה שעזר בסוף היה קטן]
- דוגמאות: ערב רגיל ונדב מסרב להיכנס למיטה / מה שעזר בסוף היה ממש קטן · סעודת חג אצל סבתא / ועומר מתחבא מתחת לשולחן · הבוקר של יום ההולדת / וטליה לא רוצה לצאת מהחדר
- שאלה שנפתחת: מה קרה ומה עזר? נסגרת בשקופית 4 (הדבר הקטן), הסיפור נסגר בשקופית 6
- שקופית 2 (scene_restart): ״נדב בן 4 / והמיטה פתאום הכי מפחידה בבית״
</div>

- Intent: unaware to problem-aware; the story carries the value. Seen with strong results in parenting accounts that tell a moment from their own home (Dr Becky S2, Danit S9, Yaffa S10) and a friend's story (S11); narrative research supports stories for attention and attitudes, with modest effects (psych.md 10). Risk: LumeBook is not a parent. The story is about one named LumeBook character in present tense, never "אצלי בבית", never "אתמול" as if it really happened. Not allowed: a "true story" claim. Stale when: two story openings in one pack. Test: story vs list on the same topic (playbook N2).

### Expert direction

**`instead-of-say` · במקום X נסי Y**
<div dir="rtl">

- תבנית: במקום ״[X]״ / נסי ״[Y]״ (להורים: נסו)
- דוגמאות: במקום ״איך היה בגן?״ / נסי ״מה היה הכי מצחיק היום?״ · במקום ״אין ממה לפחד״ / נסו ״ספר לי מה מפחיד אותך״ · במקום ״תהיה אח גדול״ / נסי ״גם לך מגיע זמן איתי״
- שאלה שנפתחת: למה Y עובד יותר טוב? נסגרת בשקופית 3 (חובה מקור)
- שקופית 2 (first_answer): ״״איך היה?״ זו שאלה ענקית / ״מה הצחיק אותך?״ זה רגע אחד שקל לספר״
</div>

- Intent: solution-aware, saves. Seen with strong results on Avital Bashan's illustrated "ובמקום" carousel (S3) and on Dr Becky's "what I wanted to say / what I did instead" (S2); LumeBook's own "במקום" carousels got 0 to 1 likes (S22, S23) at a much smaller reach. Risk: X must be something "כולנו" say, not a shamed quote. Not allowed: "stop saying X" framing (rejected R1). Stale when: "במקום" opened a pack in the last 7 days. Test: instead-of with illustration of mom and child vs text-only.

**`reversal` · מה שכולנו עושים ולמה זה הפוך**
<div dir="rtl">

- תבנית: [מה שכולנו עושים] / בדרך כלל [התוצאה ההפוכה]
- דוגמאות: עוד חמש דקות בשער / בדרך כלל רק מאריכות את הבכי (מקור) · הסבר ארוך לפני השינה / לפעמים רק מעיר אותה יותר (מקור) · עוד חיבוק אחרון בשער / לפעמים מקשה על הפרידה (מקור)
- שאלה שנפתחת: למה זה הפוך? נסגרת בשקופית 3 עם מקור
- שקופית 2 (contrast): ״פרידה קצרה היא לא פרידה קרה״
</div>

- Intent: curiosity with a claim. Risk: a contrarian claim without a source is a promise (playbook 7 #9). Always factual_claim. Stale when: two reframes in one pack. Test: reversal vs surprising-reframe.

**`surprising-reframe` · זה לא אומר ש**
<div dir="rtl">

- תבנית: [התנהגות שמדאיגה] / לא בהכרח [הפירוש המפחיד]
- דוגמאות: הבכי בשער / לא אומר שבחרתם גן לא נכון · פספוס אחרי שנולד התינוק / לא אומר שהגמילה נכשלה (מקור) · ״אני שונא את התינוק״ / לא אומר שהוא לא אוהב אותו
- שאלה שנפתחת: אז מה זה כן אומר? נסגרת בשקופית 3
- שקופית 2 (name_trigger): ״שבועיים בבית / ופתאום הוא שוב נצמד בבוקר״
</div>

- Intent: reassurance for worried parents. Risk: "לא אומר" is a claim and needs a source on the payoff slide. Not allowed: replacing one certainty with another ("זה בטוח בגלל..."). Stale when: "לא אומר ש" in two packs a week.

**`practical-question` · שאלה מעשית עם גיל**
<div dir="rtl">

- תבנית: איך [פעולה] לילד בן [גיל]?
- דוגמאות: איך מסבירים לבן 3 מתי חוזרים? · איך מספרים לבת 4 שהמוצץ הולך? · מה עונים כשבן 5 שואל למה התינוק בוכה?
- שאלה שנפתחת: השאלה עצמה. נסגרת בשקופיות 4 ו-5
- שקופית 2 (first_answer): ״״עוד מעט״ לא אומר לו הרבה / בגיל שלוש עוד מעט זה גם עכשיו וגם מחר״ (מקור)
</div>

- Intent: solution-aware, search-like. Research on question headlines is mixed: one study found self-referencing questions helped (M1), others found questions did worse (M2, M3 working paper, M5). If used, it must be the parent's own specific question about her child (M1); LumeBook's own question-led carousels got near-zero engagement at tiny reach (S20). Keep as hypothesis. Not allowed: yes/no questions. Stale when: two question shapes in one pack.

**`numbered-small-things` · שני דברים קטנים**
<div dir="rtl">

- תבנית: [מספר] דברים קטנים ל[רגע] / [למי]
- דוגמאות: 2 דברים קטנים לבוקר בשער / לגילאי 2 עד 5 · 2 משפטים לפני כיבוי האור / לבת 3 שמפחדת מהחושך · 2 דברים קטנים לשבוע הראשון עם התינוק / בשביל הגדול
- שאלה שנפתחת: מה הם? נסגרת בשקופיות 4 ו-5
- שקופית 2 (promise): ״אף אחד מהם לא דורש זמן / הראשון לוקח עשר שניות בשער״
</div>

- Intent: savers, solution-aware. Lists with a comment word did well in Israeli accounts (Tal Strul S5, Hilla Gover S6) and Merav Levy's 4-step morning list (S7), but every strong case also had a comment-word CTA or a large audience, so the list itself is not shown to be the cause. Stale when: numbers open more than two options a night.

**`parent-worry-quote` · החשש במילים של ההורה**
<div dir="rtl">

- תבנית: ״[החשש של ההורה במילים שלו]״
- דוגמאות: ״אם אלך מהר הוא יחשוב שלא אכפת לי״ · ״אם אקח לה את המוצץ היא לא תירדם״ · ״מה אם הוא ירגיש שהחלפנו אותו?״
- שאלה שנפתחת: האם החשש נכון ומה עושים? נסגרת בשקופית 3
- שקופית 2 (first_answer): ״פרידה קצרה היא לא פרידה קרה / ככה הוא יודע למה לצפות״
</div>

- Intent: hesitant, problem-aware parents. Risk: naming a worry must not feed it. Not allowed: "ואת תצטערי". Stale when: quote shapes open more than two options a night.

**`just-so-you-know` · רק שתדעי** (current_trend, review by 2027-01-08)
<div dir="rtl">

- תבנית: רק שתדעי / [התנהגות מוכרת] זה [חלק מהשלב] (להורים: רק שתדעו)
- דוגמאות: רק שתדעי / פספוס אחרי חודשים של גמילה זה חלק מהדרך (מקור) · רק שתדעו / בכי בשער אחרי חופש זה מוכר מאוד (מקור) · רק שתדעי / בקשה לעוד סיפור היא לא תמיד תרגיל (מקור)
- שאלה שנפתחת: למה זה נורמלי ומה עושים? נסגרת בשקופית 3 עם מקור
- שקופית 2 (same_template): ״רק שתדעי / גם ילד שכבר נכנס לבד יכול להיצמד שוב״ (מקור)
</div>

- Intent: reassurance, shares between mothers. Seen as a repeated-line format in Hebrew parenting carousels (Noa Dotan's "רק בודקת שאת יודעת ש..." S16; market.md section 4). LumeBook uses "רק שתדעי" because "בודקת" would give the account a first-person female persona. Always factual_claim: the normalising line needs a source. Stale when: the review date passes or the line appears in most IL parenting carousels. Test: repeated line vs single statement.

**`positive-edition` · הגרסה הטובה** (current_trend, review by 2027-01-08)
<div dir="rtl">

- תבנית: ״[אזהרה שכולם אומרים להורים]״ / הגרסה הטובה
- דוגמאות: ״חכי חכי שתגיע לגיל שלוש״ / הגרסה הטובה · ״עכשיו עם שניים תראי מה זה״ / הגרסה הטובה · ״כיתה א׳ זה כבר סיפור אחר״ / הגרסה הטובה
- שאלה שנפתחת: מה הצד הטוב, ואיך עוזרים לו לקרות? נסגרת בשקופיות 3 עד 5
- שקופית 2 (same_template): ״״חכי חכי״ / עד שהיא מספרת לך בדיחה ראשונה משלה״
</div>

- Intent: warm, shareable, unaware audience. Seen in Lovevery's "just wait... (positive edition)" (S17, 1.3x its median, one post). Risk: drifts away from a problem the carousel solves; use only when slides 3 to 5 still give two concrete things to do. Stale when: the review date passes. Test: positive edition vs milestone-week for the same milestone.

**`parent-confession` · מחשבה שמתביישים בה**
<div dir="rtl">

- תבנית: ״[מחשבה שהורים מתביישים בה]״ / [משפט שמוריד בושה, בלי עובדה]
- דוגמאות: ״אני מתגעגעת לגדול שלי״ / והוא יושב לידי על הספה · ״אין לי כוח לעוד סיפור הערב״ / ומותר להגיד את זה · ״לפעמים אני מחכה שהוא כבר יירדם״ / ומותר לחשוב את זה
- שאלה שנפתחת: האם זה בסדר, ומה עושים עם זה? נסגרת בשקופית 3
- שקופית 2 (first_answer): ״להתגעגע לגדול זה לא לאהוב את התינוק פחות / זה לשים לב למה שהשתנה״
</div>

- Intent: tired parents, strong saves and sends; Sarai Gatt's "אני לא אוהבת את הילדים שלי אותו הדבר" (S12) and Alex's "No one warned me I might miss my older child" (S18) did well. Risk: LumeBook is not a parent, so the confession is always in quotation marks as a thought many parents have, never "I". Not allowed: a confession that shames ("אני אמא גרועה") or stays unresolved. Stale when: used twice in 14 days. Test: confession vs parent-worry-quote.

**`analogy-scene` · דמייני ש**
<div dir="rtl">

- תבנית: דמייני ש[מצב מקביל מעולם המבוגרים] / [הפרט שעושה את זה קשה] (להורים: דמיינו)
- דוגמאות: דמייני שמישהו לוקח לך את הטלפון / בלי להגיד מתי תקבלי אותו · דמייני שמחר מישהי חדשה / יושבת על הכיסא שלך בעבודה · דמייני שנוחתים בארץ זרה / ואת לא מבינה אף מילה
- שאלה שנפתחת: מה זה אומר על הילד שלי? נסגרת בשקופית 3 (החיבור לילד)
- שקופית 2 (scene_restart): ״מוצץ שנעלם בלילה / מרגיש בערך ככה בגיל שלוש״
</div>

- Intent: unaware parents; perspective-taking. Dr Becky's pilot analogy (S8) is the strongest single post in the sample (12.5x her median) but it is one post from a very large expert account, so this stays a hypothesis. Risk: the analogy must not make the child's feeling look silly or dramatic. Stale when: two analogies in 14 days.

## Notes per formula (guardrails)

- `child-*` formulas are an imagined inner voice. Never present them as a real child or a testimonial
- `reversal`, `surprising-reframe`, `just-so-you-know` and any example marked (מקור) must be backed by a source on slide 1 or 2 (claims, kind sourced_fact) and on the payoff slide. In the slate set `factual_claim: true`
- `instead-of-say` gives the answer in the hook; the gap is *why*, and slide 3 must explain it
- `child-numbered-ask`: only for options that talk to both parents ("אמא ואבא"; with mom alone write "אמא"). The number must match the solution slides (two: slides 4 and 5 open with דבר ראשון / דבר שני)
- `numbered-small-things`: the number in the hook must match the solution slides that follow (two in a 7-slide carousel)
- `through-the-ages` works for milestone topics (new sibling, first grade), each slide moving one age forward; keep the child as one consistent character
- `parent-worry-quote` names a worry; never feed it (no "and you'll regret it")
- `story-unresolved`, `parent-confession`: LumeBook is never a parent. No first person parent story ("I", "my son", "אצלי בבית"), no "true story", no "אתמול" that pretends it happened
- Do not use a first person parent story ("I", "my son") as if the account were a real parent: it invents an identity

## Slide 2: second hook moves

Slide 2 must work as a first slide on its own: Instagram may re-show a carousel from slide 2 to someone who did not swipe (platform_supported, research P-table). The validator rejects a slide 2 headline that opens with a word leaning on slide 1 (ואז, אז, אבל, כי, וגם, גם, ולכן, לכן, ואם, זה, זאת, ככה, הנה, ובגלל, ועוד, וזה, וזאת).

| move | Hebrew | example |
|---|---|---|
| `zoom_in` | אותו רגע מקרוב יותר | "כבר במדרגות" then "בבטן" |
| `other_side` | מעבר בין הצד של הילד לצד של ההורה | "בשער את אומרת ״יהיה בסדר״" |
| `name_trigger` | מה הפעיל את זה עכשיו | "אחרי החגים זה חוזר" |
| `contrast` | ניגוד שמבקש הסבר | "פרידה קצרה היא לא פרידה קרה" |
| `promise` | מה מקבלים בהמשך | "2 דברים קטנים שעוזרים / הראשון בשקופית הבאה" |
| `first_answer` | חצי תשובה שעומדת לבד | "״איך היה?״ זו שאלה ענקית" |
| `scene_restart` | הסצנה מסופרת מחדש במשפט אחד | "נדב בן 4 / והמיטה פתאום הכי מפחידה בבית" |
| `same_template` | עוד מופע של אותה תבנית | "רק שתדעי / ..." again with a new case |

## Slides 3 to 6: re-hook moves (the `pull` of each slide)

| pull type | Hebrew pattern |
|---|---|
| `question` | the slide ends with a question the next slide answers |
| `open_loop` | the last line sets up the next headline ("ואת בטח חושבת שאני עושה דווקא" then "אני לא עושה לך דווקא") |
| `numbered` | "דבר ראשון / דבר שני" |
| `next_step` | "ועוד דבר קטן בשער" |
| `contrast` | "בבוקר הולכים מהר / בערב מאטים ביחד" |

Never cut a sentence in the middle to force a swipe (playbook 5.1).

## Nightly hook slate

Before writing the six options, the writer builds a private slate in `pack.json` under `hook_slate` (schema_version 3). It is internal: it never reaches parents and it never ranks the options for Yarin.

1. **Twelve candidates for tonight's topic**: 6 kid (`k1` to `k6`) and 6 expert (`e1` to `e6`). In each direction: 6 different formulas, at least 3 families (at most 2 candidates per family) and at least 3 mechanisms. Prefer formulas whose status is current and that are not in `recent_hook_formulas_rotate_away_from`
2. **For each candidate write**: the slide 1 text (`hook`), a slide 2 that works as a first slide (`slide2`) and its `slide2_move`, the `mechanism`, the awareness stage, the exact open question (`gap`), the `payoff_slide` and how it closes the question (`answer`), and `factual_claim` (true if slide 1 or 2 says something about children in general)
3. **Score each candidate 0 to 2** on the ten criteria below, and answer the four fail checks honestly
4. **A candidate fails** if any fail check is true, if it scores 0 on honest curiosity, emotional truth, topic fit or LumeBook fit, or if the total is under 14 of 20 (a LumeBook hypothesis, to revisit when results exist). A failed candidate stays in the slate with its scores; it is never used
5. **Build three options per direction** from passing candidates (`used_by`: kid-1 to kid-3, expert-1 to expert-3), choosing for difference, not for the highest score: the six options together need at least 4 mechanisms (2 per direction), 4 sentence shapes, 3 slide 2 moves and 2 awareness stages, and no two openings that share most of their words. Each option's `hook` records `slate_id`, `mechanism` and `slide2_move`
6. **Never pick a winner.** The slate is a working tool. The review page shows six options; Yarin chooses

| criterion | key | 2 | 1 | 0 |
|---|---|---|---|---|
| עוצר | `stopping_power` | a parent in this moment stops on it | interesting | easy to scroll past |
| ספציפי | `specificity` | a time, place, age or real sentence | a clear topic without a moment | general |
| רלוונטי להורה | `parent_relevance` | the parent of a 2 to 7 year old feels it now | relevant to some | not about parenting |
| סקרנות כנה | `honest_curiosity` | opens a real question the carousel closes, on the named slide | a hint of a question | clickbait, or no question |
| אמת רגשית | `emotional_truth` | how this moment really feels | a little polished | invented drama or manipulation |
| הבטחה להחלקה | `swipe_promise` | clear why to swipe, and slide 2 delivers | vague | none |
| שימושי | `usefulness` | leads to something to do or understand tomorrow | some value | none |
| מתאים לנושא | `topic_fit` | exactly tonight's topic and season | related | off topic |
| מתאים ללומבוק | `lumebook_fit` | a moment where a story with the child as the hero is a natural tool later | loosely | none (for example broad parent humour) |
| טרי | `freshness` | new wording and formula against the last 3 packs | a formula used recently with new wording | repeats a recent hook |

Fail checks (any true fails the candidate): `clickbait` (the gap is bigger than the answer, or a banned opener), `unsupported_claim` (a fact about children with no source we can cite), `unfulfilled_promise` (the carousel does not deliver what slide 1 or 2 promises), `blames_parent` (the parent is the cause, or "you are doing it wrong").

## Rotation rules

| what | rule | enforced by |
|---|---|---|
| formula | different formula for each of the six options; avoid formulas used in the last 3 packs and formulas published in the last 14 days, but **never force a weaker hook just to rotate** | ERROR inside the pack; WARN against history |
| family | at most 2 options per family in a pack; a family selected twice in 7 days is blocked | ERROR (unchanged) |
| mechanism | at least 4 different mechanisms across the six, at least 2 per direction | ERROR (schema_version 3) |
| sentence shape | at least 4 different shapes across the six | ERROR (schema_version 3) |
| awareness stage | at least 2 different stages across the six | ERROR (schema_version 3) |
| slide 2 move | at least 3 different moves across the six; slide 2 never leans on slide 1 | ERROR (schema_version 3) |
| topic and season | no topic from the last 14 packs; seasonal formulas only in their season | ERROR (unchanged) / writer |
| wording | no slide 1 headline from the last 30 packs; no two openings in a pack that share most of their words; WARN when a hook reuses most of a recent hook's words or a slide 2 headline repeats | ERROR / WARN |
| trends | a `current_trend` formula past `review_by` cannot be used until its row is re-checked and re-dated | ERROR (schema_version 3) |

`nightly.py start` prints `recent_mechanisms`, `recent_shapes`, `recent_slide2_moves`, `recent_awareness` and each formula's status, so the writer can see what is overused before writing the slate.

## Rejected hook styles (do not use)

From the research (section 5 of the report). Each was seen in the sample; none fits LumeBook's rules.

| style | example seen | why not |
|---|---|---|
| "Stop saying X" | "Stop telling your child 'I love you'" (R1) | you-are-doing-it-wrong, plus a brain claim the post cannot back |
| unpopular opinion | "8 unpopular parenting choices" (R2) | broad, opinion bait, no moment the book answers |
| crowd or authority number | "We asked 40,000 moms" (R3) | LumeBook has no such data; would be invented |
| reverse-psychology product | "Reasons NOT to buy" (R4) | sells on slide 1 |
| catalogue opening | "5 ספרים שהילד שלך יחכה להם" (R5) | sells on slide 1; near-zero engagement in the sample |
| urgency before a stage | "לפני שההתנגדות של הפעוט נכנסת לתמונה" (R6) | fear and urgency |
| quiz or label | "Do you know your attachment style?" (R7) | diagnosis-like labels |
| seasonal meme | "A haunted house, but it's just..." (R8) | broad humour, Halloween is marginal in Israel; watchlist only |
| hot take or news | advocacy carousels (R9) | not LumeBook's audience or job |

## Measurement

What would move a formula from `lumebook_hypothesis` to `lumebook_validated` is in `research/hook-strategy-2026-10-08.md` section 8 and in `hook-results.json` (one entry per published carousel, read 7 days after posting). Until then every formula is a hypothesis, and the validator rejects `lumebook_validated` without at least 6 posts with 300+ reach across 3 topics and a written promotion note (these thresholds are themselves a hypothesis).
