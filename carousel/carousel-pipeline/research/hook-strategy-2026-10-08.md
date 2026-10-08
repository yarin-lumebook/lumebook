# LumeBook carousel hook strategy: research and recommendations

Date: 8 Oct 2026. For the nightly carousel pipeline (`carousel/carousel-pipeline/`). Output: the updated `hook-bank.md`, a hook slate step in every nightly pack (`hook_slate`, schema_version 3), new validator rules and tests, and `hook-results.json` for LumeBook's own numbers.

Research question: which current hook structures are most likely to stop Israeli parents, create an honest reason to swipe, and attract the right audience for LumeBook?

## 1. Summary

1. **Nothing is proven for LumeBook.** LumeBook's own carousels had 0 to 3 likes each in the 6 Oct audit (`research/carousel-playbook-research/market.md` section 3), so there is no LumeBook signal yet. Every formula carries `lumebook_hypothesis`, and the validator refuses `lumebook_validated` until `hook-results.json` holds enough posts.
2. **Three hook rules are platform supported.** (a) Slide 2 must work as a first slide: Mosseri said unswiped carousels are often re-shown from slide 2 (P1), and Meta's Instagram Feed system card, updated 29 Jun 2026, predicts "How likely you are to swipe through the whole carousel" and uses "Whether the carousel was reordered in your Feed" (P2). (b) No clickbait or engagement bait: the Instagram Creators FAQ names "clickbait, engagement bait" as content people dislike (P8). (c) Never split one sentence across slides 1 and 2 (P1 against P15). We found **no first-party guidance on how to write a first slide** (P19).
3. **Topic and moment matter more than the wording formula.** In a registered report of thousands of headline A/B tests, a model of wording features picked the better headline 54.42% of the time (M4), and a study of 1,828 news headline rewrites concluded wording features alone cannot predict success (M2). The slate therefore scores fit to the moment and honesty as heavily as stopping power.
4. **What the research favours for wording:** a specific moment about one person (M3 working paper, psych.md 4), first-person "I" (M4, a small effect in M8), and curiosity with a hint and a guaranteed answer (M6). Question hooks and "you"-address hooks are **not** reliable lifts (M1 against M2, M3, M4, M5). Hooks where the parent is blamed are discounted or provoke anger (M16, M17).
5. **What the current sample shows (observational only).** Child-voice letters, one-moment stories, "instead of X" scripts and confession or normalisation lines did well against their own accounts' medians (S1, S2, S3, S9 to S14). Lists did well too, but almost always with a comment-word CTA attached (S5, S6, S29), so the list may not be the cause. Brand catalogue openings and personalised-book product carousels did poorly (S33, R5, market.md 2.15).
6. **Changes:** 17 formulas kept with stable ids, 5 added (`story-unresolved`, `just-so-you-know`, `positive-edition`, `parent-confession`, `analogy-scene`), 9 styles rejected, 2 families added (`normalising`, `analogy`), every formula now has evidence labels, mechanisms, sentence shape, slide 2 moves and a review date, and three are time-limited trends that expire on 8 Jan 2027 unless re-checked.

## 2. Method and limits

**Existing system read first:** `hook-bank.md`, `README.md`, `scripts/carousel_lib.py`, `scripts/nightly.py`, `scripts/validate_pack.py`, `pack.schema.json`, `history.json`, `drafts/2026-10-08/pack.json`, the test fixture, `docs/lumebook-instagram-carousel-playbook-he.md` (sections 5, 7, 16, 17), `research/carousel-playbook-research/platform.md`, `psych.md` and `market.md`, the lumebook-carousel and lumebook-hebrew-voice skills.

**Platform and research evidence:** a research subagent read first-party Meta and Instagram pages (rendered in a browser where needed) and papers through DOI records, OpenAlex, Crossref and open full texts. Full notes with every row: `research/notes/platform-and-mechanisms-2026-10-08.md`. I re-checked the three quotes this strategy leans on most against the live pages on 8 Oct 2026: the Feed system card swipe-through lines (P2), the Creators FAQ clickbait line (P8) and the Gligorić et al. second-person result and 54.42% accuracy (M4).

**Current-content sample:** 61 posts read (43 slide pairs and 19 strips, one post in both), 44 documented in section 5; the other 17 are mostly brand posts with no text hook on slide 1. 37 of the 44 were posted in the 90 days before capture (8 Jul to 6 Oct 2026) and 7 within the 12 months before. Dates not in the captured metadata were decoded from the post code (marked "decoded"). I did not collect new posts today: opening Instagram in the browser pane was refused by this session's permission classifier ("Interfere With Workloads"), and I did not work around it. Instead I re-read material collected on 6 Oct 2026 by earlier sessions:
- 43 slide-1-and-2 pairs from the playbook market scan (slide images plus `meta.json`: owner, date, likes and comments from the logged-out embed, captured 6 Oct 2026), read by me as image tiles
- 19 strips (slides 1 to 4 plus the last slide) of the carousel research v2 finalists in `research/carousel-research/img2/`, read by me
- likes, comments and medians for 6 Israeli finalists from `research/carousel-research/il_finalists.csv` (read this session)

Limits that matter:
- **Metrics are a 6 Oct snapshot** of likes and comments only. Saves, sends and reach are private. Logged-out embed counts can be about 30% lower than logged-in counts for the same post (market.md section 0)
- **Multiples** compare a post with its account's median over a 12-post window (market.md section 1), mixing embed post counts with logged-in medians in some rows. Treat them as rough
- **Account size**: follower counts were not verified this session. The 12-post median likes stands in as a size signal
- **Four numbers come from an earlier session's notes** (memory of the v2 research, not re-read today): Danit S9, Therapy for Mums S14, Teran Sands R2, and the existence of the S13 and S18 metrics. They are marked "not re-read"
- **Selection bias**: posts were picked for relevance and success, not at random
- **Engagement is not conversion.** No post here has public sales data. Comment-word CTAs inflate comment counts by design
- **No Hebrew or Israeli headline study exists** in what we found; every mechanism study is English or Dutch news, measuring clicks, not swipes, sends or saves

## 3. Evidence table: platform (first-party)

All accessed 8 Oct 2026. Full table with 19 rows: notes file, Table A. Labels: `platform_supported` unless stated.

| id | claim | source (title, URL, date) | verbatim | limits | what it means for hooks |
|---|---|---|---|---|---|
| P1 | An unswiped carousel is often re-shown from slide 2 | Mashable, "Why Instagram carousels sometimes start on the second slide", https://mashable.com/article/instagram-engagement-carousels-second-slide, 21 Oct 2024, quoting Mosseri's Reel https://www.instagram.com/p/DBOeUmTSmIC/ (17 Oct 2024) | "we'll often give that carousel a second chance and automatically move to that second piece of media for the viewer" | staff statement via a news report; the video was not heard; no second independent report found; 2024 | slide 2 is a second cover and must stand alone |
| P2 | Feed ranking predicts swipe-through and uses reordering as an input | Meta Transparency Center, "Instagram Feed AI system", https://transparency.meta.com/features/explaining-ranking/ig-feed/, updated 29 Jun 2026 | "How likely you are to swipe through the whole carousel"; "Whether the carousel was reordered in your Feed" | inputs only, no weights; "reordered" undefined | slide 1 must earn the swipe, not only the stop |
| P5 | For non-followers an LLM rates how informative a post is | Meta Transparency Center, "Instagram Feed Recommendations AI system", https://transparency.meta.com/features/explaining-ranking/ig-feed-recommendations/, updated 29 Jun 2026 | "This signal is purely generated by LLM to assess the post's content quality" | what the model reads is not stated | a hook that withholds everything behind thin slides is a risk (inference) |
| P7 | Send rate matters more for non-followers, like rate for followers | Social Media Today, https://www.socialmediatoday.com/news/instagram-engagement-rates-provide-insight-into-reach/821170/, 26 May 2026, quoting Mosseri | "send rates matter more for those who don't follow you" | via news report | prefer moments a mother would send to her partner or a friend |
| P8 | Clickbait and engagement bait can make content non-recommendable | Instagram for Creators FAQ, https://creators.instagram.com/faq?locale=en_US, undated | "content that users broadly tell us they dislike, including clickbait, engagement bait, or which promotes a contest or giveaway" | Instagram gives no definition of either | banned openers; honest gap rule |
| P9 | Meta's engagement-bait definition exempts a specific call to action (Facebook) | Meta Transparency Center, Engagement Bait, https://transparency.meta.com/features/approach-to-ranking/content-distribution-guidelines/engagement-bait/, parent page updated 2 Jul 2025 | "for purposes other than a specific call to action" | Facebook scope; the exempt examples are causes, not product links | the comment-word CTA is not ruled on either way (section 9) |
| P10 | Meta's clickbait definition: withholding information or sensational phrasing | Meta Transparency Center, Clickbait Links, same parent page | "by withholding information or using sensationalist phrasing" | Facebook link posts | no "you won't believe", no all caps |
| P12 | Account Status shows whether content is recommendable | Instagram Help Center, https://help.instagram.com/653964212890722/, undated | "If your account is not eligible to be recommended, none of your content will be recommended" | a flag, not a score | weekly check once comment-word carousels run |
| P15 | Instagram's Edits carousel editor encourages headlines that carry across slides | Instagram for Creators blog, https://creators.instagram.com/blog/edits-carousel-editor, 7 Oct 2026 | "a headline can carry across them" | design suggestion, not ranking | visual bleed is fine; split sentences are not (conflicts with P1) |
| P16 | Instagram advises relatable content | Creators FAQ (as P8) | "Make your content relatable" | mainly about Reels; Instagram's own observation | recognition hooks fit first-party advice |
| P19 | No first-party guidance on writing a carousel's first slide was found | Meta Business Help Center, carousel ads best practices, https://www.facebook.com/business/help/927639917355563 | "Tell your story with all the available carousel components." | ads context | every "hook formula" source is practitioner or our own |

## 4. Evidence table: mechanisms (research)

Full table with 20 rows: notes file, Table B. Read level: [F] full text, [A] abstract, [WP] working paper. Label: `research_supported_mechanism`.

| id | finding | source | read | limits | use in hooks |
|---|---|---|---|---|---|
| M1 | Question headlines raised readership, especially self-referencing ones | Lai & Farbrot 2014, *Social Influence* 9(4), https://doi.org/10.1080/15534510.2013.847859 | [A] | older; other studies disagree | if a question, the parent's own question about her child |
| M2 | Wording features alone cannot predict headline success; full-quote headlines and questions did worse in rewrites | Kuiken et al. 2017, *Digital Journalism* 5(10), https://doi.org/10.1080/21670811.2017.1279978 | [F] | observational, Dutch news | caution on quote-only kid hooks; test quote plus framing |
| M3 | Wording matters but advice often predicts the wrong direction; working paper: concreteness and stories about one person helped, reader-directed and question cues hurt | Banerjee & Urminsky 2025, *Marketing Science* 44(3), https://doi.org/10.1287/mksc.2021.0018 | [A] final, [WP] 2021 | the specific directions are unverified in the final paper | one named child, one concrete moment |
| M4 | First-person singular helped (β = 0.24); second person did not; model accuracy 54.42% | Gligorić et al. 2023, *PLOS ONE* 18(3) e0281682, https://doi.org/10.1371/journal.pone.0281682 | [F], quotes re-checked by me | English news clicks | supports child "I" voice; "you" is not a lever; topic matters most |
| M5 | Summary headlines were chosen more than curiosity headlines on 9 news sites | Scacco & Muddiman 2020, *New Media & Society* 22(3), https://doi.org/10.1177/1461444819863408 | [A] | US local news | say what it is about, keep one open element |
| M6 | Curiosity works with a hint and an assured resolution; clickbait may cost credibility | psych.md section 1 (Menon & Soman 2002, https://doi.org/10.1080/00913367.2002.10673672; Molyneux & Coddington 2020) | [A] | simulated ads | payoff slide named in every candidate |
| M8 | First-person narration slightly raised identification (d = 0.10) | Chen & Bell 2021, *Psychology & Health*, https://doi.org/10.1080/08870446.2021.1894331 | [A] | health narratives, small effect | child voice is reasonable, not magic |
| M11 | High similarity to the story's opponent blocked identification | Hoeken et al. 2016, *Human Communication Research* 42(2), https://doi.org/10.1111/hcre.12076 | [A] | lab | the child needs or notices, never accuses the mother |
| M16, M17 | Guilt or shame the reader already feels is discounted; shame provokes anger and perceived manipulation | Agrawal & Duhachek 2010, *JMR* 47(2), https://doi.org/10.1509/jmkr.47.2.263; Boudewyns et al. 2013, *Psychology & Marketing* 30(9), https://doi.org/10.1002/mar.20647 | [A] | health topics | no blame hooks; normalise instead |
| M18 | Maternal guilt and shame track the gap between "actual me" and "the mum I should be" | Kenny & Robinson 2026, *J Child Fam Stud* 35(5), https://doi.org/10.1007/s10826-026-03274-5 | [A] | N = 94, correlational | confession and "רק שתדעי" hooks shrink the gap |
| psych.md 4, 9, 10 | Concrete language; self-reference; narrative transportation (modest effects) | Packard & Berger 2021; Symons & Johnson 1997; Braddock & Dillard 2016 (in psych.md) | per psych.md | per psych.md | moment, identity and story formulas |

## 5. Current-content sample

Columns: id, account, URL code, date, format, slide 1 (verbatim, shortened with "..."), slide 2, hook family (our taxonomy), moment, mechanism, the question it opens and where it is answered, visible metrics (likes / comments, 6 Oct snapshot) and multiple of the account's 12-post median, size signal, transfer to LumeBook, evidence label for what it shows. All Instagram carousels unless stated. URL: https://www.instagram.com/p/CODE/.

### 5.1 Used as support for formulas (S)

| id | account, code, date | slide 1 | slide 2 | family / moment / mechanism | question, answered | metrics, multiple, size | transfer | label |
|---|---|---|---|---|---|---|---|---|
| S1 | biglifejournal, DeHOmAFExxS, 5 Oct 2026 | Dear Mom and Dad, I love you but... I fall apart the second I get home from school. And it's not because I had a bad day. Here's what I wish you knew | At school, I spend hours... listening following directions waiting my turn being "good". So when I get home... I'm often just DONE. | child letter + "not because" / after-school meltdown / perspective shift | why does she fall apart? slide 2 to 3, then numbered requests | 1,619 / 578; 1.8x the median of its normal-looking posts (877; market.md 2.7); comment CTA "SDC" | very high: same structure as `child-letter`, `child-not-because`, `child-numbered-ask` | external_performance_pattern (with S12 to S14) |
| S2 | drbeckyatgoodinside, DeIDQsODAis, 5 Oct 2026 | True story from my house this morning: My kid screamed out from bed: "I DON'T WANT TO GO TO SCHOOL TODAY!" Here's what I wanted to do in that moment. And here's what I did instead. | I wanted to say: "You have to go!..." What I did instead: I got in bed with her and said, "Ugh. I know that feeling." Then I stopped talking. | story + instead-of / school refusal / narrative tension | what did she do? slide 2 | 5,483 / 45; 1.06x (median 5,158) | high, but LumeBook is not a parent: third person, named character | external_performance_pattern (weak alone) |
| S3 | avital.bashan, DboKFT-DWcc, 4 Aug 2026 (decoded) | כלים מדהימים שאת מלמדת את הילדים שלך וישפיעו עליהם כל החיים | כשהילד שלך שובר כוס בטעות / ובמקום ״אתה אף פעם לא שם לב!״ / את מרגיעה ואומרת... (illustrated mother and child) | instead-of / everyday mishaps / practical utility | what to say instead, answered on each slide | 1,751 / 1,771; 21.1x likes, 65.6x comments (il_finalists.csv); comment CTA "כלים" | high: the slide 2 scene carries it; slide 1 itself is generic | external_performance_pattern |
| S4 | drbeckyatgoodinside, Ddy2lyDF6Q1, 27 Sep 2026 | How to raise a good loser / Not because winning doesn't matter... | Here's the thing about sore losing: ... It feels like "I am a loser..." That's not a character flaw, it's a confidence problem. | reframe / losing / reframe | why do kids melt down? slide 2 | 4,231 / 32; 0.82x | medium | shows a reframe can sit at the median |
| S5 | tal_strul, DZphMo0CAUb, 16 Jun 2026 | 5 ספרים מומלצים לקראת מעבר לגן עירייה | רגע לפני שתעברו להמלצות... כי המעבר לגן הוא הרבה מעבר לזה | numbered list / move to municipal gan / practical utility | which books, slides 3 onward | 613 / 1,389; 13.0x likes, 231.5x comments (csv); CTA comment "ספר" + coupon | medium: a list of books sells on the slides; LumeBook keeps value first | external_performance_pattern, CTA-confounded |
| S6 | hilla_gover_slp, Da0n_qzACqS, 15 Jul 2026 | ספרים מומלצים לפי גיל / לרך הנולד | ספרים מומלצים לפי גיל / מגיל 4 חודשים | numbered list by age / reading / practical utility | which books per age | 617 / 878; 2.8x, 14.9x (csv); CTA comment "רשימה" | low for hooks: catalogue format | external_performance_pattern, CTA-confounded |
| S7 | merav.levy, DRKqmgSDYXo, 17 Nov 2025 (12-month window) | ככה תהפכי את שגרת הבוקר שלכם לנעימה ורגועה יותר ב-4 שלבים פשוטים | 1. התעוררי לפני הילדים... | numbered / mornings / practical utility | which steps, slides 2 to 5 | 961 / 67 logged-in; 9.2x | high: feminine singular address, blurred children | external_performance_pattern |
| S8 | drbeckyatgoodinside, Dcq2baejOXf, 30 Aug 2026 | You're on a flight from New York to Los Angeles when the pilot makes this announcement... | "Folks, we need to make an emergency landing..." You're annoyed... Then the cabin erupts... | analogy / limits and protest / perspective shift | what does the pilot do? slide 3 | 64,395 / 334; 12.5x | medium: reach reflects her authority | one post: `lumebook_hypothesis` |
| S9 | danit_parenting_coaching, Das4fCQDTBf, 12 Jul 2026 (decoded) | הבת שלי בת כמעט 10 / נפגשת די הרבה עם חברות בערב / השבוע היא הפרה את ההסכם שלנו ולא עמדה בחוק שקבענו | בחופש הגדול היא נפגשת המון עם חברות בפארק... 19:30 זו השעה שנקבעה | parent story, unresolved / a broken rule / narrative tension | what did the mother do? slides 3 to 5 | 23,367 likes (earlier session, not re-read) | high as structure; first person parent is not allowed for LumeBook | external_performance_pattern |
| S10 | yaffa_michaela_zukerman, DdoeylHDeQQ, 23 Sep 2026 | כשהייתי בת 11 יצאנו להתרים בבתים... (handwritten story) | כשהייתי בכיתה ו׳... | personal story / childhood memory / narrative tension | what happened? sells a digital book on the last slide | 2,033 / 1,149; 8.5x, 34.8x (csv) | medium: story structure transfers, the topic does not | external_performance_pattern |
| S11 | biglifejournal, DeEsCzDk3QO, 4 Oct 2026 | One of my dad-friends has the sweetest relationship with his grown-up kids. So one day I asked him how he did it | He smiled and said: For the longest time, I thought the secret was sharing the stuff I loved with them... | story about one person / relationship / narrative tension | how did he do it? slides 2 onward | 1,011 / 125; 1.15x the normal median | medium (a dad-centred story; LumeBook never addresses dad) | supports `story-unresolved` |
| S12 | saraigatt, DcIYOqZjZoQ, 17 Aug 2026 | אני לא אוהבת את הילדים שלי אותו הדבר / והילדים שלי יודעים את זה | זה לא שאני אוהבת אחד מהם פחות או יותר / זה שאני אוהבת אותם אחרת | confession + "not X, Y" / siblings / reassurance | how can she say that? answered on slide 2 | 315 / 1,388; 1.4x, 7.2x (csv); story offered as a reward for commenting "לב" | very high: confession resolved on slide 2, story as the gift | external_performance_pattern |
| S13 | natashagolan_, Dd1JpBCDLQe, 28 Sep 2026 (decoded) | היי אמא / עוד מעט תלדי את הילד השני שלך / ויש כמה דברים שאני רוצה לספר לך לפני | זה יהיה קשה / ממש קשה... | letter to a mother / second birth / perspective | what does she want to say? slides 2 to 5 | in the v2 finalists; numbers not re-read | high as a letter structure; voice is parent-to-parent | external_performance_pattern (with S1, S14) |
| S14 | therapyformums, DReSKEGCZEW, 25 Nov 2025 (decoded, 12-month window) | Dear partner, Why things feels easier when you're away (from a couples therapist) | You've gone away for the weekend with your friends. | letter / mental load / recognition | why? slides 3 to 4 | about 136K likes (earlier session, not re-read) | medium: partner-directed | external_performance_pattern |
| S15 | Hebrew account (handle not recorded), DdzLT8mnJXg, 27 Sep 2026 (decoded) | אני בת 5 / אמא מכינה עוגה ואני רוצה לשבור את הביצים | אמא נותנת לי ביצה / ואני דופקת אותה על הקערה... | child first person across ages / failure / narrative | what happens when the egg breaks? last slide: לא כישלון | not recorded | high: the child voice through ages | current_trend |
| S16 | noadotan.ot, Dd1lsyhjdil, 28 Sep 2026 | רק בודקת שאת יודעת שילד לא צריך לשבת או להסתכל לך בעיניים כדי להקשיב לך. | רק בודקת שאת יודעת שתינוקות ופעוטות לא אמורים להחזיק כלי כתיבה כמו גדולים. | repeated line / development myths / reassurance | is this normal? each slide answers itself | 111 / 7; 3.5x (median 31.5) | high as a format; LumeBook writes "רק שתדעי" (no first-person persona) | current_trend |
| S17 | lovevery, DeIA5ptklwD, 5 Oct 2026 | oh, it's your baby's first halloween? just wait... (positive edition) | until you get to pick out their very first costume | flipped warning / firsts / anticipation | what's coming? each slide | 2,330 / 14; 1.3x | medium: Halloween is marginal in Israel; the flip transfers | current_trend |
| S18 | thriveafterbabywithalex, Ddg5kxcGyjv, 20 Sep 2026 (decoded) | No one warned me I might miss my older child after having another baby. Even though they were still right there | I missed us. I missed being able to say, "Come sit with me"... | confession / new sibling / reassurance | why miss them? slides 2 to 4 | in the v2 finalists; numbers not re-read | high: maps to `parent-confession` in quotes | external_performance_pattern (with S12) |
| S19 | feedinglittles (Megan), DbQmeoom8_L, 26 Jul 2026 (decoded) | If you're packing school lunch for the first time this fall, here's everything you need to know to make it easier | 1. Get a lunch box (or 2) that your kid is excited to open. | season + identity / first school lunch / anticipation | how? slides 2 to 4; CTA "LUNCH" | not recorded | medium: "first time this fall" filter | supports `milestone-week` (hypothesis) |
| S20 | lumebookai, DcSssc6GzWs, 21 Aug 2026 | שאלה אחת לשישי / מה יעזור לך להרגיש קצת יותר בטוח ביום הראשון? | תשובות שילדים באמת נותנים | question / first day / practical | answered on slide 2 | 0 / 0 | our baseline: tiny reach, not a test of the format | n/a |
| S21 | lumebookai, Ddlav41GB6W, 22 Sep 2026 | הוא לא מוכן להגיד סליחה / אל תכריחו מילה ריקה. | 1 קודם עוצרים את הפגיעה / אני לא מרשה להכות. | statement / apology / practical | slide 2 | 0 / 1 | baseline | n/a |
| S22 | lumebookai, DdBZCDWG1uN, 8 Sep 2026 | 5 שאלות קטנות במקום ״איך היה?״ / כי ״איך היה?״ היא שאלה ענקית. | 1 שאלה שפותחת סיפור / מי הצחיק אותך היום? | numbered + instead-of / after school | slides 2 onward | 1 / 1 | baseline | n/a |
| S23 | lumebookai, DdZbXZYHW0I, 17 Sep 2026 | מה אומרים אחרי פספוס, מילה במילה / גמילה היא תהליך. גם הפספוסים שלה. | לא / ״למה לא אמרת?״ (struck out) | instead-of / toilet setbacks | slides 2 onward | 0 / 1 | baseline | n/a |

### 5.2 Context posts (seen, not used as formula support)

| id | account, code, date | slide 1 | metrics, multiple | note |
|---|---|---|---|---|
| S24 | wonderbly, Ddn8bV3iGMB, 23 Sep 2026 | "Whats your favourite colour?" / Me: (illustration) | 242 / 43; 2.8x (median 86.5) | meme template over the book's art; no moment |
| S25 | takingcarababies, DdthhIqmwxn, 25 Sep 2026 | We asked 40,000 moms this question | 3,240 / 127; 1.5x the all-post median | crowd-answer format (rejected R3) |
| S26 | little.kinder.pals x slumberkins, DeFz5limy4N, 4 Oct 2026 | Parents, we're not just raising children. We're raising future adults. | 93 / 19; 1.7x Slumberkins' recent median | creator collab beat the brand post S27 |
| S27 | slumberkins, DeDXYLhma_R, 4 Oct 2026 | How to navigate Halloween with confidence and connection. Boo! | 49 / 0; 0.9x | brand "how to" with no moment |
| S28 | iris_maayan, Dd0u4omEW3z, 28 Sep 2026 | 12 פעולות פשוטות להפחתת סטרס / חלק 1 | 31 / 17; 1.0x | a list alone did not lift |
| S29 | busytoddler, Ddm7jDzHfwh, 22 Sep 2026 | How you organize toys can determine whether the toys are played with / Here are 8 storage ideas that I love | 7,512 / 2,791; 1.5x; CTA "STORAGE" | list plus comment word |
| S30 | wonderbly, DVf6q-ojdHQ, 5 Mar 2026 (12-month) | Need costume ideas for World Book Day / Read Across America? | 165 / 114; 1.9x | dated occasion question |
| S31 | merav.levy, DS-j67GDVZH, 1 Jan 2026 (12-month) | כשאנחנו אומרים לילדים שלנו מילים פוגעניות בזמן מריבה | 469 / 42; 4.5x | slow reveal split across slides; opens with guilt (not for LumeBook) |
| S32 | etti_haft, DdYpED4DTdp, 17 Sep 2026 | a small confession: games she regrets bringing to her gan (market.md 2.14) | 97 / 245; 3.8x | product confession; 51 of 60 comments asked for the link |
| S33 | mebook.ai, DdenXHwgA0C, 19 Sep 2026 | הכבאית האדומה (cover with photo to illustration arrow, trust strip) | 1 / 0 | personalised-book product hook: near zero |
| S34 | libriogram, DdgCk2EDKrJ, 20 Sep 2026 | Was passiert, wenn ein Wald seine Farben verliert? | 16 / 0; 0.65x | story-question hook from a personalised-book brand |
| S35 | Hebrew sleep consultant (handle not recorded), Dbp7SEEjnXh, 5 Aug 2026 (decoded) | ספטמבר מתקרב. / התינוק שלך נכנס לגן. / והוא גם ככה לא ישן כמו שצריך בבית. | not recorded | seasonal worry; ends with a PDF lead magnet |
| S36 | biglittlefeelings, DeHxxpCmWEu, 5 Oct 2026 | Do you know what your attachment style is? | 1,262 / 65; 0.17x | quiz label (rejected R7) |
| S37 | lumebookai, DcdUcxJFsUC, 25 Aug 2026 | 5 דברים שכדאי לתרגל לפני כיתה א׳ / ואף אחד מהם הוא לא לקרוא. | 1 / 1 | baseline |

Other posts read and not listed individually: 17, mostly brand or product posts with no hook text on slide 1 (Wonderbly illustration-only posts, Hooray Heroes dog books, Yoto sale, Sifriyat Pijama book cover, Solid Starts app tour, Busy Toddler toy list, Wonderbly's "we don't use AI" post), plus the rejected rows below.

### 5.3 Rejected (R)

| id | account, code, date | slide 1 | why rejected |
|---|---|---|---|
| R1 | mommyandmishti, DZDgG2ogewZ, 1 Jun 2026 (decoded, 12-month window) | Stop telling your child "I love you" ❌ Say this instead and watch what changes in them | "you are doing it wrong"; slide 4 claims "Neuroscientists call this habituation" without a source; fear of harm |
| R2 | teransands, DcV6rUQlive, 22 Aug 2026 (decoded) | 8 unpopular parenting choices | opinion bait, broad; about 47.8K likes (earlier session, not re-read) shows reach, not fit |
| R3 | takingcarababies, DdthhIqmwxn | We asked 40,000 moms this question | LumeBook has no such data; would be invented |
| R4 | wonderbly, DdgN7EHiiR8, 20 Sep 2026 | Reasons you should absolutely NOT buy your kids Wonderbly books. | sells on slide 1; 0.75x |
| R5 | tinybook.co.il, DY4UAc2DK8y, 28 May 2026 | 5 ספרים שהילד שלך יחכה להם | catalogue opening; 5 / 0, 0.5x |
| R6 | larissaginatmethod, DcOFta8DL1W, 19 Aug 2026 (decoded) | למה כדאי לך להתחיל גמילה מהחיתול לפני שההתנגדות של הפעוט שלך נכנסת לתמונה? | urgency and fear before a developmental stage |
| R7 | biglittlefeelings, DeHxxpCmWEu | Do you know what your attachment style is? | diagnosis-like label; 0.17x |
| R8 | solidstarts, DeFHklroK3E, 4 Oct 2026 | A haunted house, but it's just: BABY-LED WEANING | 7,501 / 66, 6.5x, but broad humour on a local-holiday template; watchlist only |
| R9 | biglittlefeelings, Dd2Vn9Rj2NL, 28 Sep 2026 | NORMALIZE RUINING RAPISTS' LIVES | advocacy; 112,708 likes (15x) shows outrage reach, not parenting fit |

## 6. Which hook structures held up

The brief's starting list, judged against the evidence:

| starting category | decision | formulas | why |
|---|---|---|---|
| a highly specific parent-child moment | kept | `moment-time`, `child-body-moment`, `milestone-week` | concreteness (psych.md 4; M3 working paper); fits the self-filtering goal |
| a believable child quote | kept, with a caveat | `child-question` | full-quote headlines did worse in M2; test quote plus framing line |
| the child's imagined inner voice | kept, strongest kid evidence | `child-not-because`, `child-letter`, `child-hidden-half`, `child-numbered-ask` | S1, S12 to S15; first person helped in M4 (small); never accusing (M11) |
| a parent's private worry in their own words | kept | `parent-worry-quote` | hypothesis; no direct sample |
| a gentle counterintuitive reframe | kept, must be sourced | `reversal`, `surprising-reframe` | mixed sample (S4 at 0.82x); a claim needs a source |
| a practical question tied to an age | kept as hypothesis only | `practical-question` | questions are not a reliable lift (M1 to M5); LumeBook's question post S20 got 0 likes at tiny reach |
| "what to say instead" | kept | `instead-of-say` | S2, S3 |
| a numbered set of small actions | kept, cause unclear | `numbered-small-things` | S5 to S7 and S29 did well, mostly with a comment-word CTA; S28 did not |
| a seasonal or developmental moment | kept | `milestone-week`, new `positive-edition` (trend) | S17, S19 |
| tension between what the parent sees and what the child feels | merged | into the `perspective_shift` mechanism of the child formulas | not a separate surface form |
| a concrete outcome without an unrealistic promise | merged | into `numbered-small-things` (gentle_outcome) | no separate evidence |
| a confession or normalisation that reduces shame | added | `parent-confession`, `just-so-you-know` | S12, S16, S18; M16 to M18 |
| a story opening with an unresolved moment | added | `story-unresolved` | S2, S9 to S11; psych.md 10 |
| (new) an adult analogy | added as hypothesis | `analogy-scene` | S8 is one strong post from a large expert account |

Rejected styles are listed in `hook-bank.md` ("Rejected hook styles") with the R rows above.

## 7. The nightly hook slate and rotation

The method is in `hook-bank.md` ("Nightly hook slate", "Rotation rules") and `.claude/skills/lumebook-carousel/references/nightly.md` step 5b. In short: 12 private candidates per night, scored 0 to 2 on ten criteria (stopping power, specificity, parent relevance, honest curiosity, emotional truth, swipe promise, usefulness, topic fit, LumeBook fit, freshness), four fail checks (clickbait, unsupported claim, unfulfilled promise, blames parent), a pass mark of 14 of 20 with no zero on the four honesty and fit criteria, and the six options chosen for difference. The system never ranks the options.

Why the weights look like this: wording explained little of headline success in the largest tests (M2, M4), and Instagram's own documents point at swipe-through, sends and informativeness (P2, P5, P7), so the slate gives honesty, fit and the slide 2 promise the same weight as stopping power. The pass mark of 14 is a guess to revisit once results exist.

Trend expiry: `current_trend` rows carry a review date at most 120 days after research. `through-the-ages`, `just-so-you-know` and `positive-edition` expire on 8 Jan 2027. After that the validator blocks them in new packs until someone re-checks recent posts and re-dates the row. Other rows show "review due" after 8 Apr 2027 (a warning, not a block).

## 8. Measurement plan

External trends do not prove that a hook converts. Only LumeBook's own numbers can.

**What to record** (`hook-results.json`, one entry per published carousel, read 7 days after posting, the same weekday each week, as playbook section 17.1 already sets): reach, non-follower share, code-word comments, preview visits, preview completions, purchases, sends, saves and profile visits, plus the hook formula, mechanism, slide 2 move, topic, posting time, CTA word, any test id and the week's notes. A field is left null when the number is not available; nothing is estimated.

**Primary metric per hook:** code-word comments per 1,000 reached accounts (the code word sits only on slide 7, so it also shows the reader got to the end; playbook 5.1). Then preview visits per 1,000 reach, preview completions, purchases. Sends, saves, profile visits per reach and non-follower reach are secondary: they tell us about reach, not conversion.

**How to test:**
- Change one main hook variable at a time: formula, mechanism, slide 2 move, or address (mom vs both parents). Keep topic, CTA word style, slide count, visual style and posting slot as close as possible (playbook 16.1 pairs: same concept in two versions in the same week)
- Repeat a formula across several comparable posts and topics before reading anything into it
- Record what differed anyway (holiday, news, a creator share, a boost) in `notes`
- Check Account Status weekly once comment-word carousels run (P12). A recommendation flag pauses the test

**When a formula may be called `lumebook_validated`** (all thresholds are hypotheses, set because the current data cannot support any, and to be revised after the first 12 weeks):
- at least 6 posts using it, each with at least 300 reach, across at least 3 topics (the validator enforces these counts and a written `promotion_note`)
- its median code-word comments per 1,000 reach is at least 1.5x the median of the other formulas posted in the same period (the playbook's 16.1 decision rule), it beats that median in at least 4 of the 6 posts, and preview visits per 1,000 reach are not lower
- nothing is decided from one post, and the validator does not decide it: Yarin writes the promotion note

**Expect it to take months.** At current reach the small-account benchmark is about one save per post (Socialinsider, cited in platform.md 5.1), so early results give direction, not proof.

## 9. Conflicts with existing rules, and what changed

| conflict | resolution |
|---|---|
| Instagram's Edits blog encourages headlines that carry across slides (P15); Mosseri says slide 2 is often shown first (P1) | kept the existing rule: slide 2 stands alone, never a split sentence; visual bleed is fine |
| The fixed comment-word CTA (Yarin's brief) vs Instagram's "engagement bait" (P8). Meta's only definition exempts a "specific call to action" but is Facebook-scoped (P9) | no change to the CTA (it is Yarin's rule and it promises a specific thing); added the weekly Account Status check to the measurement plan. No first-party source says it is demoted or safe |
| Playbook 7 rates question hooks as medium to high reach; the research found questions unreliable (M1 to M5) | kept `practical-question`, labelled hypothesis, guidance to use only the parent's own specific question |
| The old hook bank said Israeli parents respond to a child's sentence, citing market.md pattern 5, which mostly describes English accounts | softened to "a pattern seen in several standout carousels, not proof" |
| psych.md 1 marked "question headlines reduce clicks" as secondary-only | now supported by the M3 working paper and M2, still not the final M3 paper |
| Kid hooks are first-person child quotes; M2 found full-quote headlines did worse | no rule change; added a test variable (quote alone vs quote plus framing line) |
| "Slide 2 must stand alone" was guidance only | now enforced as an error for new packs, by a list of words that lean on slide 1. This is a heuristic: it cannot catch every dependency, so the writer still checks by reading slide 2 alone |

## 10. Verification (8 Oct 2026)

- **Existing tests:** all 75 pass. **New tests:** 20 in `HookStrategy`. Total 95, all passing (`python3 -m unittest discover -s carousel/carousel-pipeline/tests`)
- **Existing packs:** `tests/fixtures/valid_pack.json` and `drafts/2026-10-08/pack.json` stay VALID as schema_version 2, with history
- **Sample hook slate:** `tests/fixtures/sample_slate_gan_separation.json`, topic `gan-separation`. Merged with the fixture's six options it validates as a schema_version 3 pack (the test builds it as `load_v3()`):
  - 6 kid and 6 expert candidates, 6 different formulas per direction, 4 families and 4 mechanisms in kid, 5 families and 5 mechanisms in expert
  - every candidate names its open question, its payoff slide and how that slide closes it
  - every slide 2 passes the stand-alone check, and I read each one as a first slide
  - all 24 Hebrew strings pass `voice_lint.py` (no comma, period or em dash, no jargon, no dad, no brand)
  - no candidate contains sale words (the `SALE_PREP_RE` check)
  - five of the six used candidates state something about children; each of those options maps a sourced fact to slide 1 or 2. One candidate (k6) fails on an unsupported promise and stays unused
  - the six options use 5 mechanisms, 5 sentence shapes, 5 slide 2 moves and 2 awareness stages
- **No paid call, nothing posted:** the review page was rebuilt from the v3 pack (RTL check clean) and `prepare_fal_jobs.py` froze one option in a scratch folder, reporting `"network_calls": 0`. No fal.ai tool or script that calls it was run. Nothing was published or sent

The sample slate, readable:

| id | formula | slide 1 | slide 2 | mechanism | score | result |
|---|---|---|---|---|---|---|
| k1 | child-not-because | אני לא בוכה בגלל הגן / אני בוכה כי את הולכת | אחרי החגים שוב קשה לי בשער... | perspective_shift | 19 | used, kid-1 |
| k2 | child-body-moment | כבר במדרגות של הגן / אני מרגישה את זה בבטן | כל בוקר הפרידה אחרת... | recognition | 17 | used, kid-2 |
| k3 | child-question | ״מתי אתם באים לקחת אותי?״ / אני שואל את זה כל בוקר | השאלה הזאת חזרה אחרי החגים... | honest_curiosity | 20 | used, kid-3 |
| k4 | child-letter | אמא / רציתי להגיד לך משהו על השער | בספטמבר נכנסתי לבד / אחרי החגים שכחתי איך עושים את זה | perspective_shift | 15 | passes; too close to the 8 Oct hook |
| k5 | moment-time | 7:50 / הגננת כבר פותחת את השער ואני עוד באוטו | בכל צעד מהאוטו לשער / אני מחזיק לך את היד יותר חזק | recognition | 16 | passes; family and mechanism already used |
| k6 | through-the-ages | אני בן 3 / ואחרי החגים השער שוב גדול עליי | אני בן 4 / ומנופף לך מהחלון בלי לבכות | narrative_tension | 16 | **fails**: promises the crying stops by 4 with no source |
| e1 | reversal | עוד חמש דקות בשער / בדרך כלל רק מאריכות את הבכי | פרידה קצרה היא לא פרידה קרה... | reframe | 18 | used, expert-1 |
| e2 | practical-question | איך מסבירים לבן 3 מתי חוזרים? / בלי שעון ובלי ״עוד מעט״ | ״עוד מעט אני חוזרת״ / לא אומר לו הרבה... | practical_utility | 18 | used, expert-2 |
| e3 | sentence-we-all-say | ״אין ממה לפחד מאמי״ / כולנו אומרות את זה בשער הגן | בשבילה הפחד בשער אמיתי לגמרי... | recognition | 19 | used, expert-3 |
| e4 | just-so-you-know | רק שתדעי / בכי בשער אחרי חופש ארוך זה מוכר | רק שתדעי / גם ילדה שכבר נכנסה לבד יכולה להיצמד שוב | reassurance | 15 | passes; no concrete step |
| e5 | analogy-scene | דמייני יום ראשון בעבודה חדשה / ואין לך מושג מתי נגמר היום | בוקר בגן אחרי החגים / מרגיש בערך ככה בגיל שלוש | perspective_shift | 17 | passes; overlaps e2's insight |
| e6 | parent-confession | ״לפעמים אני מקנאה באמהות שהפרידה שלהן קלה״ / ומותר להרגיש את זה | בכי בשער הוא לא ציון על האמא / הוא חלק מהפרידה של הילדה | reassurance | 16 | passes; would need a source on slide 2 |

The "result" column is the writer's working note, not a ranking for Yarin: the review page shows the six options without any order of preference.

## 11. Open items

- Re-collect a fresh 90-day sample in the logged-in Instagram pane when Yarin allows it (blocked this session), and fill in the four "not re-read" numbers
- Check the slide-2 re-show and Hebrew swipe direction on a phone with the app in Hebrew (platform.md section 7)
- Re-check the three trend formulas before 8 Jan 2027
- After 12 weeks of `hook-results.json`, revisit the pass mark (14), the validation thresholds and the evidence labels
