# What makes LumeBook's potential buyers stop, ask and consider buying

Research of 14 Oct 2026 on 41 creators from the LumeBook creator map. **Internal:** it uses sales figures from `docs/lumebook-sales-data-decisions-2026-10-12.md`; keep them off public pages.

Files in this folder: `evidence.md` (examples and sources behind each conclusion, E1 to E14), `methodology.md` (definitions, formulas, coverage, biases), `posts.csv` (565 posts), `creators.csv` (41 creators), `src/` (scripts and coding briefs).

Labels: **Observed** (seen in a post, comment, profile or file), **Interpretation** (my reading), **Hypothesis** (to test).

## Bottom line

**Strongest findings**

1. **Nothing in the creator map is yet tied to a LumeBook sale.** Every result below is attention, engagement or an intent proxy. The store already has the plumbing to change that: an ambassador link that credits printed books for 7 days, and UTM attribution sent with each book started when the visitor accepts analytics cookies (observed in the store's public code, section 11). Nobody has read that data for creators yet.
2. **Milestone topics do not win reach.** Inside each creator's own feed, LumeBook's buying occasions perform at the creator's normal level (median 0.93x); humour, family moments, nostalgia and hands-on demonstrations are what spread (E1).
3. **Buying questions follow a useful thing shown in use, mostly by professionals.** Only 83 of 2,982 sampled comments (2.8%) show purchase intent, and they cluster on posts that demonstrate a product (7.1 per 100 comments) against 0.6 where no product is shown. Professionals' posts carry 3.8 per 100, parents' 1.1 (E2, E4).
4. **Israeli parenting professionals already sell through "comment a word, I'll DM you".** 15% of recent posts use it, and book lists made this way drew 882 to 1,389 comments (speech therapists, a parent guide). That is the natural way in for a personalised book (E3, E5).
5. **Gift-givers barely show up.** 5 self-identified grandparents and 2 gift mentions in 2,982 comments; birthday posts are tributes that collect greetings. The "older buyers are grandmothers" idea stays a hypothesis (E6, E7).

**What we still do not know:** whether any of these posts, topics or creators produce books started or paid orders; reach, saves, shares, profile visits and link clicks for any post; who the buyer is relative to the child. Section 12 lists the rest.

**First test to run:** a book-list post by a speech therapist who already runs comment-word funnels, with LumeBook's pacifier book as the one personalised pick and the creator's own ambassador link in the DM. Start with `topaz_meir_slp` (already "in process" in the map). Section 10, T1.

One blocker found on the way: **`instagram.com/lumebookai` could not be loaded on 14 Oct** (E14). Check it before any creator tags LumeBook.

---

## 1. Evidence boundary

| Funnel stage | KPI | What this study has | Status |
|---|---|---|---|
| Attention | Plays (reels) | 300 recent reels with plays | Publicly observed (plays are not unique reach) |
| Attention | Reach, impressions, watch time, retention, completion | None | Unavailable (creator Insights only) |
| Engagement | Likes, comments, reposts | All recent posts (likes hidden on 41, reposts missing on 105) | Publicly observed |
| Engagement | Saves, DM shares | None | Unavailable |
| Consideration | Product or price questions, buying intent, keyword requests | 2,982 classified comments on 184 posts | Proxy (from public comments) |
| Consideration | Profile visits, follows, link clicks, CTR, qualified DMs | None | Unavailable |
| Product activation | Sessions, books started, previews | Store-wide only: 6,130 people started a book, 21.7% paid within 7 days (12 Oct note) | Privately verified, not per creator |
| Checkout | Checkout starts, payment step, abandonment | Store-wide only: last 30 days 202 orders reached payment, 85 purchased (Mixpanel, undercounts) | Privately verified, not per creator |
| Purchase and economics | Attributed orders, revenue, AOV, cost per purchase | None per creator. Store-wide: 1.40 books per buyer; ₪111 revenue per sale in the ad window (12 Oct note) | Unavailable per creator |
| Self-reported sales | Creator claims | 530 families, 4,000+ homes (one author, public posts); 100+ copies (one creator, private email) | Self-reported, unverified |

Missing means unknown, not zero.

## 2. Sample in one paragraph

243 creators in the map on 14 Oct (not 304: the 12 Oct cleanup removed 61). I chose 41 across parents (15, including 3 fathers), professionals (18), book people (3), gift or occasion perspectives (4) and one high-reach comparison, sized from 1,555 to 40,996 followers, including 13 of the 15 creators the map marks "in process" or "book stage" and 10 of the 12 barter-batch creators (`creators.csv` has each reason). For each, up to 12 consecutive posts from 7 to 90 days old (180 days for 4 low-volume creators): 469 recent posts, 312 reels, 146 carousels, 11 images. 96 older breakouts were analysed separately. Every post was coded from its frames or slides plus caption. Comments: up to 30 per post on 184 posts (2,982 comments), in Instagram's ranked order. Full method and biases: `methodology.md`.

## 3. KPI leaderboards (one per KPI, never combined)

Recent sample only. Breakouts are excluded. Reels, carousels and images are kept apart. Instagram only.

### Attention
**A1. Reels: highest raw plays**

| Creator | Post | Published | Topic (coded) | Plays | Followers |
|---|---|---|---|---|---|
| nataliegaash | [DXvwsYVN0lN](https://www.instagram.com/p/DXvwsYVN0lN/) | 2026-04-30 | Morning mantra routine for children and the brain science … | 1,205,190 | 33,040 |
| ima.shir | [DeCZjK0NZpm](https://www.instagram.com/p/DeCZjK0NZpm/) | 2026-10-03 | Spontaneous night ice cream outing with the children | 858,323 | 18,778 |
| rivki_shashar | [DdEhOlyqJ5P](https://www.instagram.com/p/DdEhOlyqJ5P/) | 2026-09-09 | Surprising her husband the doctor as a patient at his clin… | 731,961 | 23,374 |
| savta_ziona_official | [DdMP8MYIva7](https://www.instagram.com/p/DdMP8MYIva7/) | 2026-09-12 | Boat trip: a wife 'humiliates' her husband by making him d… | 622,766 | 7,727 |
| rivki_shashar | [Dd9CfAqKg9c](https://www.instagram.com/p/Dd9CfAqKg9c/) | 2026-10-01 | Surprise family visit to dad's clinic with the children | 441,409 | 23,374 |
| may_rot1 | [DdUFGI3oO8T](https://www.instagram.com/p/DdUFGI3oO8T/) | 2026-09-15 | Teaching a child to wipe after the toilet using a balloon … | 381,775 | 27,625 |
| hen.kalimian.kids | [DdGLBpXOU6U](https://www.instagram.com/p/DdGLBpXOU6U/) | 2026-09-10 | Fake-pregnancy prank on friends, mother of four | 314,611 | 39,185 |
| hatravelers_ | [Dd62NmMI-J4](https://www.instagram.com/p/Dd62NmMI-J4/) | 2026-10-02 | Slovenia presented as the cheaper, underrated destination … | 272,991 | 38,152 |
| hatravelers_ | [DdLguWMoSQ8](https://www.instagram.com/p/DdLguWMoSQ8/) | 2026-10-05 | List of special and beautiful lodging places in Israel | 256,142 | 38,152 |
| hen.kalimian.kids | [DdO-bRluTBw](https://www.instagram.com/p/DdO-bRluTBw/) | 2026-09-13 | Three-generation family reveal from a couple to a large ga… | 248,556 | 39,185 |


**A2. Reels: plays vs the creator's own reel median** (only formats with at least 3 sample reels)

| Creator | Post | Published | Topic (coded) | Plays | Creator median | Ratio |
|---|---|---|---|---|---|---|
| nataliegaash | [DXvwsYVN0lN](https://www.instagram.com/p/DXvwsYVN0lN/) | 2026-04-30 | Morning mantra routine for children and the brain science … | 1,205,190 | 5,754 | 209.4x |
| savta_ziona_official | [DdMP8MYIva7](https://www.instagram.com/p/DdMP8MYIva7/) | 2026-09-12 | Boat trip: a wife 'humiliates' her husband by making him d… | 622,766 | 8,986 | 69.3x |
| may_rot1 | [DdUFGI3oO8T](https://www.instagram.com/p/DdUFGI3oO8T/) | 2026-09-15 | Teaching a child to wipe after the toilet using a balloon … | 381,775 | 9,720 | 39.3x |
| ima.shir | [DeCZjK0NZpm](https://www.instagram.com/p/DeCZjK0NZpm/) | 2026-10-03 | Spontaneous night ice cream outing with the children | 858,323 | 29,787 | 28.8x |
| yuli.brosh | [DaPzBaVNElA](https://www.instagram.com/p/DaPzBaVNElA/) | 2026-07-01 | 90s nostalgia: a song intro that only women who grew up in… | 103,567 | 4,258 | 24.3x |
| shaniben_shushan11 | [DdtPUiLAhsS](https://www.instagram.com/p/DdtPUiLAhsS/) | 2026-09-25 | Semolina and orange cake with syrup for the holiday | 76,984 | 3,712 | 20.7x |
| edenmarlel00 | [Ddedn8egsQM](https://www.instagram.com/p/Ddedn8egsQM/) | 2026-09-20 | Husband-in-the-toilet joke over a lock screen of three chi… | 181,580 | 9,424 | 19.3x |
| nofar_aizik | [DcZCOp4ItbM](https://www.instagram.com/p/DcZCOp4ItbM/) | 2026-08-23 | Foldable toilet seat reducer for public toilets with a chi… | 48,356 | 2,912 | 16.6x |
| baryona | [Ddwi7Lfs8-g](https://www.instagram.com/p/Ddwi7Lfs8-g/) | 2026-09-26 | Baby growth from newborn to 9 months | 158,647 | 10,399 | 15.3x |
| natallyaharon | [DdtOB6FNczn](https://www.instagram.com/p/DdtOB6FNczn/) | 2026-09-25 | Skit: someone says 'how lazy you are' and she shows hersel… | 56,458 | 4,080 | 13.8x |


**A3. Creators: median reel plays per follower (proxy: followers are not exposure)**

| Creator | Followers | Median reel plays | Plays per follower |
|---|---|---|---|
| imkassandra__ | 5,876 | 46,269 | 7.87 |
| rivki_shashar | 23,374 | 109,347 | 4.68 |
| topaz_meir_slp | 6,957 | 22,610 | 3.25 |
| hatravelers_ | 38,152 | 86,155 | 2.26 |
| knafaim.ot_by_noy | 10,745 | 20,368 | 1.90 |
| almaanddad | 14,938 | 26,781 | 1.79 |
| daria_mansour1 | 2,681 | 4,660 | 1.74 |
| lital_magnezi | 27,512 | 44,710 | 1.63 |
| ima.shir | 18,778 | 29,787 | 1.59 |
| daniel.gabbai (lowest) | 40,996 | 1,654 | 0.04 |

Watch time, retention and completion: unavailable for every post.

### Engagement
**E1. Reels: likes per 1,000 plays** (reels with at least 2,000 plays; likes hidden on 41 sample posts)

| Creator | Post | Published | Topic (coded) | Likes | Plays | Likes/1k plays |
|---|---|---|---|---|---|---|
| almaanddad | [Dd3uY5oNOD8](https://www.instagram.com/p/Dd3uY5oNOD8/) | 2026-09-29 | Cheesecake topped with fried kataifi 'hair', baked with hi… | 1,643 | 25,749 | 63.81 |
| almaanddad | [DbYhQ4ZNWeQ](https://www.instagram.com/p/DbYhQ4ZNWeQ/) | 2026-07-29 | Girl opens a delivery of squishy toys | 1,577 | 26,781 | 58.89 |
| almaanddad | [Dcd2pjyNkDW](https://www.instagram.com/p/Dcd2pjyNkDW/) | 2026-08-25 | '2023 vs 2026' newborn-to-girl growth video | 1,279 | 21,882 | 58.45 |
| almaanddad | [DbDy-bDtymq](https://www.instagram.com/p/DbDy-bDtymq/) | 2026-07-21 | Girl acts out five emotions on cue ('acting lessons') | 1,159 | 22,016 | 52.64 |
| knafaim.ot_by_noy | [DeCdYktq2pF](https://www.instagram.com/p/DeCdYktq2pF/) | 2026-10-03 | Creator's engagement announcement (travel-style aerial ree… | 738 | 15,613 | 47.27 |
| almaanddad | [DcRYyoStIjm](https://www.instagram.com/p/DcRYyoStIjm/) | 2026-08-20 | Dad and daughter taste a croissant with an ice-cream-style… | 1,543 | 34,703 | 44.46 |
| almaanddad | [DbgMcZltpcp](https://www.instagram.com/p/DbgMcZltpcp/) | 2026-08-01 | Chocolate-coated Bamba frozen snack (kitchen experiment wi… | 5,906 | 141,343 | 41.78 |
| almaanddad | [Dbn5aeVtHl3](https://www.instagram.com/p/Dbn5aeVtHl3/) | 2026-08-04 | Little girl makes her own bed, using her foot | 852 | 20,914 | 40.74 |


**E2a. Reels: comments per 1,000 plays, all CTAs** (reels with at least 2,000 plays)

| Creator | Post | Published | Topic (coded) | CTA | Comments | Plays | Comments/1k plays |
|---|---|---|---|---|---|---|---|
| racheli.h.m | [DdDS4cEKMhG](https://www.instagram.com/p/DdDS4cEKMhG/) | 2026-09-09 | Editable Rosh Hashana greeting-card template with a child'… | comment_keyword | 264 | 8,508 | 31.03 |
| nofar_aizik | [DcZCOp4ItbM](https://www.instagram.com/p/DcZCOp4ItbM/) | 2026-08-23 | Foldable toilet seat reducer for public toilets with a chi… | comment_keyword | 914 | 48,356 | 18.90 |
| etti_haft | [DeFlHmEErcl](https://www.instagram.com/p/DeFlHmEErcl/) | 2026-10-04 | Autumn learning with the spinning wheel (file in WhatsApp … | join_group_or_course | 49 | 2,597 | 18.87 |
| orli.parenthood | [Dc81mploSLt](https://www.instagram.com/p/Dc81mploSLt/) | 2026-09-06 | Reel with a short rant, topic not determinable from the vi… | none | 44 | 2,752 | 15.99 |
| topaz_meir_slp | [Dd6wU2IM2Do](https://www.instagram.com/p/Dd6wU2IM2Do/) | 2026-09-30 | Teaching straw drinking to a baby, part 2: the trick, plus… | comment_keyword | 435 | 34,363 | 12.66 |
| topaz_meir_slp | [DcL0hr6sQAd](https://www.instagram.com/p/DcL0hr6sQAd/) | 2026-08-18 | Helping children retrieve words by adding information abou… | comment_keyword | 598 | 48,395 | 12.36 |
| knafaim.ot_by_noy | [DdPHzcoOTGT](https://www.instagram.com/p/DdPHzcoOTGT/) | 2026-09-13 | Learning games for two-year-olds that an OT plays with her… | comment_keyword | 142 | 11,693 | 12.14 |
| knafaim.ot_by_noy | [DeCdYktq2pF](https://www.instagram.com/p/DeCdYktq2pF/) | 2026-10-03 | Creator's engagement announcement (travel-style aerial ree… | none | 188 | 15,613 | 12.04 |


**E2b. Reels: comments per 1,000 plays, posts without a comment-keyword CTA or giveaway**

| Creator | Post | Published | Topic (coded) | Comments | Plays | Comments/1k plays |
|---|---|---|---|---|---|---|
| orli.parenthood | [Dc81mploSLt](https://www.instagram.com/p/Dc81mploSLt/) | 2026-09-06 | Reel with a short rant, topic not determinable from the vi… | 44 | 2,752 | 15.99 |
| knafaim.ot_by_noy | [DeCdYktq2pF](https://www.instagram.com/p/DeCdYktq2pF/) | 2026-10-03 | Creator's engagement announcement (travel-style aerial ree… | 188 | 15,613 | 12.04 |
| _shirley_unger_kids_activities | [DdqdQnKtzkK](https://www.instagram.com/p/DdqdQnKtzkK/) | 2026-09-24 | Letter-learning pizza game kit (Letter Pizza) | 105 | 9,341 | 11.24 |
| hatravelers_ | [DdcBaYHo1hl](https://www.instagram.com/p/DdcBaYHo1hl/) | 2026-09-19 | POV: Hotel Park Bled in Slovenia with a lake and castle vi… | 2,311 | 212,249 | 10.89 |
| _shirley_unger_kids_activities | [Ddyw5zANBDs](https://www.instagram.com/p/Ddyw5zANBDs/) | 2026-09-27 | Rainbow cutting and gluing worksheet for colour matching | 71 | 7,376 | 9.63 |
| nofar_aizik | [DdVnpKgIXV6](https://www.instagram.com/p/DdVnpKgIXV6/) | 2026-09-16 | Sponsored plant-extract drops for calm and focus while kid… | 28 | 2,912 | 9.62 |
| yuli.brosh | [DdYKUOyNiR0](https://www.instagram.com/p/DdYKUOyNiR0/) | 2026-09-17 | Family studio photo session where everyone lies on the flo… | 21 | 2,558 | 8.21 |
| lotanelias | [Dcjq3TmoN7n](https://www.instagram.com/p/Dcjq3TmoN7n/) | 2026-08-29 | Three Rosh Hashana outfits with a discount code | 40 | 5,560 | 7.19 |


**E3. Reels: reposts per 1,000 plays** (public repost count; DM shares are not public)

| Creator | Post | Published | Topic (coded) | Reposts | Plays | Reposts/1k plays |
|---|---|---|---|---|---|---|
| natallyaharon | [DdtOB6FNczn](https://www.instagram.com/p/DdtOB6FNczn/) | 2026-09-25 | Skit: someone says 'how lazy you are' and she shows hersel… | 230 | 56,458 | 4.07 |
| yuli.brosh | [DbVBILbt5q4](https://www.instagram.com/p/DbVBILbt5q4/) | 2026-07-28 | Personal-branding photo sessions for women who run their o… | 8 | 2,359 | 3.39 |
| edenmarlel00 | [DdzAJCTTmGJ](https://www.instagram.com/p/DdzAJCTTmGJ/) | 2026-09-28 | Relationship meme: 'I love your personality' skit with rea… | 23 | 9,818 | 2.34 |
| books_are_friends_slp | [DbGbwdhoKIb](https://www.instagram.com/p/DbGbwdhoKIb/) | 2026-07-22 | Book list for conversations about a new start, tied to 1 S… | 5 | 3,124 | 1.60 |
| lotanelias | [Ddk9C_No95s](https://www.instagram.com/p/Ddk9C_No95s/) | 2026-09-26 | Quick star-clip hairstyle for a daughter | 9 | 5,965 | 1.51 |
| books_are_friends_slp | [DbS8_qGo0Y5](https://www.instagram.com/p/DbS8_qGo0Y5/) | 2026-07-27 | Three questions to build theory of mind (TOM) with the pic… | 3 | 2,070 | 1.45 |
| shaniben_shushan11 | [Ddat4KcAG7B](https://www.instagram.com/p/Ddat4KcAG7B/) | 2026-09-18 | 'Resting' on Friday while cooking for Shabbat | 3 | 2,121 | 1.41 |
| mor_knoll | [DeKRSlliGrh](https://www.instagram.com/p/DeKRSlliGrh/) | 2026-10-06 | Eight tips for taking a child to the dental hygienist or d… | 4 | 2,861 | 1.40 |


**E4. Carousels and images: highest raw comments**

| Creator | Post | Published | Topic (coded) | CTA / status | Comments | Likes | Comments vs creator median |
|---|---|---|---|---|---|---|---|
| lotanelias | [Dblup6pCOLS](https://www.instagram.com/p/Dblup6pCOLS/) | 2026-08-03 | Five cookies to bake with the kids, plus a one-sentence co… | comment_keyword / organic | 3,342 | 1,916 | 21.5x |
| lotanelias | [Dbckzf0CAnm](https://www.instagram.com/p/Dbckzf0CAnm/) | 2026-07-31 | Five easy loaf cakes to bake with the kids | comment_keyword / organic | 2,128 | 1,553 | 13.7x |
| nofar_aizik | [Dc-esGNiLFJ](https://www.instagram.com/p/Dc-esGNiLFJ/) | 2026-09-07 | 8 most-ordered AliExpress products of August (kids and hom… | comment_keyword / likely_sponsored | 1,687 | 380 | 1.9x |
| yaffa_michaela_zukerman | [DdoeylHDeQQ](https://www.instagram.com/p/DdoeylHDeQQ/) | 2026-09-23 | Personal story behind her sexuality and abuse-prevention d… | comment_keyword / own_product_promo | 1,182 | 2,165 | 12.7x |
| nofar_aizik | [DbnBH1PCPn6](https://www.instagram.com/p/DbnBH1PCPn6/) | 2026-08-04 | 8 most-ordered AliExpress products of July (kids and home) | comment_keyword / likely_sponsored | 1,099 | n/a | 1.2x |
| nofar_aizik | [Dd65NcGiC9S](https://www.instagram.com/p/Dd65NcGiC9S/) | 2026-09-30 | Speech therapist picks 6 AliExpress games for oral and lan… | comment_keyword / collaboration | 893 | 436 | 1.0x |
| hilla_gover_slp | [Da0n_qzACqS](https://www.instagram.com/p/Da0n_qzACqS/) | 2026-07-15 | Recommended children's books by age, birth to 3 years | comment_keyword / collaboration | 882 | 617 | 3.9x |
| lotanelias | [Dcc_GgriJtp](https://www.instagram.com/p/Dcc_GgriJtp/) | 2026-08-25 | 10 free dot-marker activity pages for kids | comment_keyword / organic | 833 | 432 | 5.4x |


**E5. Carousels and images: likes per 1,000 followers (proxy)**

| Creator | Post | Published | Topic (coded) | Likes | Followers | Likes/1k followers |
|---|---|---|---|---|---|---|
| daria_mansour1 | [DdmQS6TDNG9](https://www.instagram.com/p/DdmQS6TDNG9/) | 2026-09-22 | Twins' birth story and tribute to her husband | 2,581 | 2,681 | 963 |
| aba.maor | [Dbk9ilvDGs4](https://www.instagram.com/p/Dbk9ilvDGs4/) | 2026-08-03 | Giving each child a fixed cash budget in a toy store (Jumb… | 5,709 | 21,164 | 270 |
| aba.maor | [Dd_6ZOfDjxd](https://www.instagram.com/p/Dd_6ZOfDjxd/) | 2026-10-02 | Birthday tribute to his son with a compilation of past ree… | 5,387 | 21,164 | 255 |
| lotanelias | [Dblup6pCOLS](https://www.instagram.com/p/Dblup6pCOLS/) | 2026-08-03 | Five cookies to bake with the kids, plus a one-sentence co… | 1,916 | 8,158 | 235 |
| lotanelias | [Dbckzf0CAnm](https://www.instagram.com/p/Dbckzf0CAnm/) | 2026-07-31 | Five easy loaf cakes to bake with the kids | 1,553 | 8,158 | 190 |
| noa__lankri | [Dde-1lRCasX](https://www.instagram.com/p/Dde-1lRCasX/) | 2026-09-19 | Yom Kippur faith message: stop explaining, God has seen ev… | 1,653 | 10,662 | 155 |
| hadarv | [DbLUIGyDIgL](https://www.instagram.com/p/DbLUIGyDIgL/) | 2026-07-24 | Sunset beach family photoshoot with a baby | 173 | 1,555 | 111 |
| imkassandra__ | [Dd8W3LKDQdx](https://www.instagram.com/p/Dd8W3LKDQdx/) | 2026-10-01 | Affirmation carousel: you are not “just a mom” | 651 | 5,876 | 111 |


Saves and DM shares: unavailable.

### Consideration (proxies from comments)
**C1. Purchase-intent comments (explicit intent + product or price questions + self-reported purchases), raw and per 100 sampled comments** (posts with at least 5 sampled comments; Instagram ranked order)

| Creator | Post | Topic (coded) | Sampled | Intent comments | Per 100 | Keyword requests (separate) |
|---|---|---|---|---|---|---|
| lital_magnezi | [Dd5sq3TI1I5](https://www.instagram.com/p/Dd5sq3TI1I5/) | Push light on a toilet stall door in a gan bathroom | 30 | 16 | 53 | 0 |
| _shirley_unger_kids_activities | [DeKFbzRAmIy](https://www.instagram.com/p/DeKFbzRAmIy/) | Children's books about autumn from a gan teacher's classro… | 13 | 9 | 69 | 0 |
| knafaim.ot_by_noy | [DdWglWIKur-](https://www.instagram.com/p/DdWglWIKur-/) | Kodkod children's box games recommended by an OT, with the… | 12 | 4 | 33 | 0 |
| tal_strul | [DdwREvSCJg2](https://www.instagram.com/p/DdwREvSCJg2/) | Five children's books to end the day together at bedtime | 25 | 4 | 16 | 18 |
| hatravelers_ | [Dd1dbIsIvnV](https://www.instagram.com/p/Dd1dbIsIvnV/) | Dyland entertainment center in Ashkelon: rides, bowling, a… | 30 | 4 | 13 | 3 |
| racheli.h.m | [DcppgRWq2kN](https://www.instagram.com/p/DcppgRWq2kN/) | A prayer for the gan teacher before the new year | 12 | 3 | 25 | 0 |
| _shirley_unger_kids_activities | [DeFQglpNYu8](https://www.instagram.com/p/DeFQglpNYu8/) | Snail shell fine-motor activity with coloured stones or bu… | 30 | 3 | 10 | 21 |
| saraigatt | [DeD-nV8iv3k](https://www.instagram.com/p/DeD-nV8iv3k/) | Respond smaller when a child has a big outburst, plus free… | 30 | 3 | 10 | 26 |
| lotanelias | [DbPz3goIMPA](https://www.instagram.com/p/DbPz3goIMPA/) | Dyland indoor entertainment park in Ashkelon (recommendati… | 6 | 2 | 33 | 0 |
| yuli.brosh | [DbnIxtrtw32](https://www.instagram.com/p/DbnIxtrtw32/) | Showing her photography portfolio as a wall of reels insid… | 6 | 2 | 33 | 0 |


**C2. Requests for an offered link, file or list (keyword requests), per 100 sampled comments** (a request for the creator's offer, not spontaneous intent)

| Creator | Post | Topic (coded) | Sampled | Keyword requests | Post total comments |
|---|---|---|---|---|---|
| racheli.h.m | [DdDS4cEKMhG](https://www.instagram.com/p/DdDS4cEKMhG/) | Editable Rosh Hashana greeting-card template with a child'… | 30 | 30 | 264 |
| lotanelias | [Dblup6pCOLS](https://www.instagram.com/p/Dblup6pCOLS/) | Five cookies to bake with the kids, plus a one-sentence co… | 30 | 30 | 3,342 |
| nofar_aizik | [Dc-esGNiLFJ](https://www.instagram.com/p/Dc-esGNiLFJ/) | 8 most-ordered AliExpress products of August (kids and hom… | 30 | 30 | 1,687 |
| saraigatt | [DdnorEBDU1j](https://www.instagram.com/p/DdnorEBDU1j/) | Six social skills to teach children, more important than s… | 30 | 30 | 777 |
| etti_haft | [DeHCwwijbGq](https://www.instagram.com/p/DeHCwwijbGq/) | Autumn musical chairs game for language enrichment (file v… | 30 | 30 | 399 |
| orli.parenthood | [DV9CEWPCKpk](https://www.instagram.com/p/DV9CEWPCKpk/) | Five biggest mistakes parents make in diaper separation, w… | 30 | 30 | 155 |
| nofar_aizik | [DbVCNNJiFUw](https://www.instagram.com/p/DbVCNNJiFUw/) | Back-to-gan must-haves from AliExpress (named items, lunch… | 30 | 30 | 596 |
| tal_strul | [DZphMo0CAUb](https://www.instagram.com/p/DZphMo0CAUb/) | Five recommended books for the move to a municipal gan, wi… | 30 | 30 | 1,389 |
| _shirley_unger_kids_activities | [Dd_e2zPNA8f](https://www.instagram.com/p/Dd_e2zPNA8f/) | Autumn leaves made with gouache dots and cotton swabs | 30 | 29 | 205 |
| hatravelers_ | [DdtIIGHoNnu](https://www.instagram.com/p/DdtIIGHoNnu/) | POV: a lakeside Alps hotel in Slovenia at half the price o… | 30 | 29 | 703 |


**C3. Substantive discussion (identification + personal experience + help requests), per 100 sampled comments** (posts with at least 10 sampled comments)

| Creator | Post | Topic (coded) | Sampled | Substantive | Per 100 | Help requests |
|---|---|---|---|---|---|---|
| ima.shir | [DdwlAMSNv5S](https://www.instagram.com/p/DdwlAMSNv5S/) | Pregnancy diary week 6: hiding an early belly | 18 | 16 | 89 | 0 |
| natallyaharon | [DdtOB6FNczn](https://www.instagram.com/p/DdtOB6FNczn/) | Skit: someone says 'how lazy you are' and she shows hersel… | 14 | 11 | 79 | 0 |
| sapir_ivan_mugatz | [Dci_wrxjUD6](https://www.instagram.com/p/Dci_wrxjUD6/) | What parents of children on the autism spectrum hear from … | 10 | 7 | 70 | 0 |
| yuli.brosh | [DaPzBaVNElA](https://www.instagram.com/p/DaPzBaVNElA/) | 90s nostalgia: a song intro that only women who grew up in… | 30 | 18 | 60 | 0 |
| daria_mansour1 | [DdrVsexjBMZ](https://www.instagram.com/p/DdrVsexjBMZ/) | What my 8-month-old twins eat in a day | 13 | 7 | 54 | 6 |
| ima.shir | [DdtDs1WNRDp](https://www.instagram.com/p/DdtDs1WNRDp/) | A child senses the pregnancy before it begins | 30 | 16 | 53 | 0 |
| yaffa_michaela_zukerman | [Dc8FqRTtSgF](https://www.instagram.com/p/Dc8FqRTtSgF/) | Covert aggression and 'plausible deniability': trusting th… | 20 | 10 | 50 | 1 |
| imkassandra__ | [Ddou6LetHHq](https://www.instagram.com/p/Ddou6LetHHq/) | Pain after birth gets stronger with each birth | 30 | 14 | 47 | 0 |
| adar_azulay | [Dd6bVxysL5V](https://www.instagram.com/p/Dd6bVxysL5V/) | Mother of boys jokes about being annoyed at her future dau… | 30 | 14 | 47 | 0 |
| hilla_gover_slp | [Dar4kTwCMJV](https://www.instagram.com/p/Dar4kTwCMJV/) | Reading a board book to a baby, guest SLP tips | 12 | 5 | 42 | 4 |

Profile visits, follows, link clicks, CTR and qualified DMs: unavailable.

### Product activation, checkout, purchase and economics

No leaderboard is possible: no post, creator or topic in this study has attributed sessions, books started, previews, checkouts or orders. The only purchase figures tied to a creator are self-reported (E12). Do not call any post here "highest converting".

## 4. What the content does

### Attention by topic (within-creator ratio, reels)

| Topic group | Reels | Creators (any format) | Median plays vs creator median | Comments per 1k plays | Likes per 1k plays |
|---|---|---|---|---|---|
| Humour and entertainment | 49 | 18 | 1.25 | 0.95 | 11.6 |
| Family outings | 13 | 12 | 1.91 | 1.01 | 5.5 |
| Development and behaviour | 50 | 26 | 1.00 | 3.06 | 9.1 |
| Everyday parenting | 40 | 26 | 1.00 | 1.06 | 12.2 |
| LumeBook buying occasions (all) | 82 | 33 | 0.93 | 1.58 | 9.8 |
| of which potty and toilet skills | 5 | 5 | 3.43 | 2.37 | 14.2 |
| of which gan start | 9 | 12 | 1.36 | 1.71 | 15.0 |
| of which first grade | 9 | 4 | 0.72 | 3.55 | 4.2 |
| of which birthday | 6 | 7 | 0.70 | 3.48 | 15.1 |
| Books and reading (incl. bedtime) | 11 | 10 | 0.90 | 1.33 | 11.3 |

Small cells (under 10 reels) are directions, not findings.

### Discussion and intent by topic (comment sample)

| Coded topic | Posts | Comments | Identification + experience + help per 100 | Purchase-intent signals per 100 | Keyword requests per 100 |
|---|---|---|---|---|---|
| Pregnancy | 5 | 103 | 36.9 | 1.0 | 0 |
| Everyday parenting | 14 | 214 | 20.6 | 1.4 | 18 |
| Humour | 15 | 238 | 18.5 | 0.0 | 0 |
| Behaviour and emotions | 15 | 186 | 11.8 | 1.6 | 47 |
| Gan start | 23 | 283 | 7.4 | 2.5 | 38 |
| Development and learning | 23 | 386 | 6.5 | 2.6 | 70 |
| Potty and diapers | 11 | 191 | 7.3 | 8.9 | 33 |
| Reading and books | 6 | 102 | 6.9 | 9.8 | 53 |
| First grade | 9 | 196 | 5.1 | 2.0 | 80 |
| Birthday | 5 | 98 | 0.0 | 1.0 | 11 |

### Patterns that repeat across creators

- **Comment-word CTAs lift comments in 18 of 20 creators who use them** and turn most comments into requests for the offer (E3).
- **Showing a useful object in use draws "where do I buy"** on posts by 5 different creators (lital_magnezi, _shirley_unger_kids_activities, knafaim.ot_by_noy, tal_strul, hen.kalimian.kids), even with no CTA (E4).
- **Professional book lists draw hundreds of keyword requests** at 4 creators (tal_strul, hilla_gover_slp, topaz_meir_slp, hen.kalimian.kids) (E3, E5).
- **Commercial posts trade likes for comments:** sponsored and own-product reels get about half the likes per 1,000 plays of organic reels (E9).
- **Price is almost never shown** (7 of 469) and a child's reaction is the proof in only 17 (E10).

### Isolated outliers (do not build on these alone)

- nataliegaash's morning-mantra reel, 1,205,190 plays, 209x her median, from April (180-day window): [DXvwsYVN0lN](https://www.instagram.com/p/DXvwsYVN0lN/).
- yaffa_michaela_zukerman's crisis-call reel, 3.5M plays and 0 comments (older breakout, possibly a re-share of someone else's clip): [DbFft0dN8PE](https://www.instagram.com/p/DbFft0dN8PE/).
- baryona's sponsored pan reel, 277,026 plays with 125 likes, a like rate consistent with paid promotion (inference): [DcjCHEkMWTR](https://www.instagram.com/p/DcjCHEkMWTR/).

### Older breakouts (96 posts, analysed separately)

Mostly humour (25) and reassurance (18); text-on-video (21) and hands-on demos (19); 10 of 96 are LumeBook-relevant, and 4 of those 10 are toilet or diaper skills (orli.parenthood's clothespin exercise, 171K plays, 52x; eden_spaiev's wiping exercises, 120K, 25x) and 3 are first-grade or gan transitions with a keyword offer (hen.kalimian.kids, 1,379 and 1,401 comments; tal_strul's gan book list, 1,389 comments). The same two patterns as the recent sample: practical skill demos travel; keyword offers on transitions collect requests.

### Format notes

- Of the 24 deep-dive reels transcribed (first 30 to 45 seconds), 14 have no speech at all: the strong reels in this sample are mostly text on video with music, or burned-in subtitles. A LumeBook creator brief should not depend on a talking head.
- Co-authored (collab) reels get a higher median ratio (1.61x) because they are shown to two audiences.

## 5. Audience language

Composition of the 2,982 sampled comments: generic praise 46.6%, keyword requests 34.7%, personal experience 5.4%, identification 3.1%, help requests 2.5%, product or price questions 2.3%, objections 2.0%, tag or share 1.7%, creator replies 0.8%, explicit buying intent 0.2% (7), self-reported purchases 0.2% (6). 2,885 unique commenters (summed per post). Instagram's ranking decides which comments were sampled, so long tails of keyword comments may be under-represented and creator-friendly comments over-represented.

What parents say when they are close to buying (observed, more in `evidence.md`):
- Where and how: "איפה קונים?", "אשמח לקישור", "אפשר קישור בבקשה".
- Fit: "אשמח להמלצות למתוקי בן 3", "לאיזה גיל מומלץ".
- Price: "קופון הנחה" (a request, on a book post that offered a coupon).
- Ownership: "קנינו", "יש לנו" (self-reported).

What they say when they relate but are not buying: "גם אצלנו", "מזדהה", "גם הבת שלי ידעה", long personal stories on pregnancy and first-grade posts.

Objections seen are about the advice, not about products: toilet-training method (5 comments on orli.parenthood), teaching reading before first grade (1), screen-time rules (7). The only product objection: an item was cheaper elsewhere. No comments about delivery, personalisation quality or trust in a personalised book appear, because no post in the sample sells one; MeBook's creator posts did draw price, delivery-time and how-to-order questions (`research/competitor-content-analysis/comments_mebook_hebrew.md`).

## 6. Answers to the decision questions

| Question | Answer | Evidence |
|---|---|---|
| Which topics attract attention? | Humour and relatable moments, family outings and surprises, nostalgia, and practical skill demos (toilet wiping, potty). Milestone topics hold the baseline, they do not lift it. | E1 |
| Which topics generate substantive discussion or practical interest? | Pregnancy and family life (identification), behaviour and gan adjustment (help requests and objections), reading aloud (book recommendation requests), development (keyword requests for files). | E2, section 4 |
| Which content produces explicit purchase-intent signals? | Posts that show a useful object in use or recommend specific items: a gan toilet light, board games, picture books, bedtime books, an attraction. Signals are few (83 in 2,982). | E4 |
| Which content has verified activation or purchase results? | None in this study. Self-reported: one author's 530 families and 4,000+ homes; one creator's 100+ copies. | E12 |
| Which ICP segments are supported, uncertain or contradicted? | Section 7. | |
| Which popular topics are weakly connected to buying a LumeBook? | Couple and husband humour, comedy characters, travel, recipes, cleaning, beauty, pranks. High plays, comments are laughter or praise. | E11 |
| Which creators and approaches deserve testing first? | Professionals who already run comment-word funnels on LumeBook occasions (pacifier, potty, gan, first grade, reading), then parents living a new-sibling moment. Sections 8 and 10. | E3, E5, E8 |

## 7. Buyer segments (ICP)

The buyer and the child are different people. The store records the child (name, gender; age is mostly a default value), not the buyer's relation to the child.

| Candidate segment | Buyer | Child | Occasion | Sales evidence (internal, 12 Oct note) | Creator-content evidence (this study) | Status |
|---|---|---|---|---|---|---|
| Parents of toddlers facing a weaning step | Mother (or both parents) | 1 to 3 | Pacifier, diapers | ביי ביי מוצץ 86 orders, נפרדים מהטיטולים 66 | Professionals' pacifier and potty posts draw timing questions and keyword requests; toilet-skill demos are among the biggest outliers | **Supported** for interest; purchase unknown |
| Parents before a transition | Mother (or both parents) | 3 to 6 | Gan start, first grade | שלום כיתה א' 57; gan books in catalogue | First-grade readiness and gan-adjustment posts are the most-requested lead magnets (1,379 and 1,401 comments); book lists for the move draw hundreds of requests | **Supported** for interest; purchase unknown |
| Expecting parents with an older child | Mother | Older sibling 2 to 6 | New sibling | אח חדש + אחות חדשה 132 | Pregnancy posts draw the most identification (36.9 per 100) but almost no product talk | **Supported** for attention; purchase link **uncertain** |
| Birthday gift buyers (parents) | Parent | 1 to 8 | Birthday | Birthday book is the top seller (262) | Birthday posts are tributes with greetings; no gift conversation | **Uncertain**: strong in sales, absent in creator conversation |
| Grandparents and relatives as gift-givers | Grandmother, aunt | Grandchild | Birthday, holidays | Meta credits most ad purchases to women 55 to 64 (17 of 62); Meta attribution, not verified buyers | 5 self-identified grandparents in 2,982 comments, asking practical questions; grandparent comedy draws banter | **Uncertain**, weakly supported as present in audiences |
| Fathers | Father | Any | Any | Men 25 to 34: 8 Meta purchases on ₪112 spend (too small to trust) | Dad creators get the highest likes per play (almaanddad 40 to 64 per 1,000) but comments are praise | **Uncertain** |
| Gan teachers buying for a class | Educator | Class of 3 to 6 | Gan year, holidays | B2B tiers on the site (product brief); no B2B sales split seen | Gan-teacher creators (lital_magnezi, racheli.h.m, etti_haft) speak mostly to other teachers, who request files and ask where to buy classroom items | **Supported** as an audience for B2B, not for B2C |
| "Only young moms buy" | | | | Contradicted by the age spread of Meta purchases (12 Oct note) | Not testable here | **Contradicted** as a sole assumption |

## 8. Creators to test first

Separate lists by evidence type, not a combined score. Numbers from `creators.csv`.

**A. Professionals with LumeBook occasions and a working comment-word funnel** (best fit for a book-list or how-to post with a personal link)

| Creator | Map status | Followers | Why |
|---|---|---|---|
| topaz_meir_slp | in process | 6,957 | 3.25 plays per follower; comment word on 10 of 12 posts; pacifier posts with weaning-timing questions; book-picks reel with 112,928 plays |
| hen.kalimian.kids | follow-up due | 39,185 | First-grade readiness; keyword offers drew 1,379 and 1,401 comments; already promoted a children's book via "ספר" |
| hilla_gover_slp | follow-up due | 28,786 | Books-by-age list, 882 comments; parents ask her which books to read and where to buy |
| orli.parenthood | in process | 12,688 | 8 of 12 recent posts on potty or gan start; help requests and objections show an engaged audience |
| tal_strul | not contacted | 14,381 | Gan-transition book list, 1,389 comments; bedtime books with a publisher; asks for book picks by age |
| knafaim.ot_by_noy | sent, barter batch | 10,745 | Product lists draw "where do I buy" and a grandmother's question; 1.9 plays per follower |

**B. Parents living a LumeBook moment now** (new sibling)

| Creator | Map status | Followers | Why |
|---|---|---|---|
| ima.shir | sent, barter batch | 18,778 | Pregnant with a third child; 7 of 12 posts are a pregnancy diary; 46 of 85 sampled comments are identification or stories |
| imkassandra__ | sent | 5,876 | New baby, three older siblings; 7.87 plays per follower, the highest in the sample |
| lotanelias | no status | 8,158 | Three kids born in three years; keyword offers reach thousands of comments; uses a personal discount code already |

**C. Book voices** (small but on-topic): books_are_friends_slp (barter batch; the only explicit want for a named children's book), yaffa_michaela_zukerman (sells her own books to her audience; sensitive topic, check fit first).

**D. Gan teachers, for the B2B kindergarten offer rather than B2C:** lital_magnezi (in process; her toilet-light post drew 16 of 30 "where do I buy"), racheli.h.m (in process), _shirley_unger_kids_activities (in process; autumn books post 9 of 13 product questions), etti_haft (in process, barter batch).

**Not first for sales tests:** humour, travel and comedy accounts with high reach but no buying talk (rivki_shashar, hatravelers_, savta_ziona_official, adar_azulay, edenmarlel00, natallyaharon, almaanddad). They may suit reach-only posts later. mor_knoll is a competitor conflict and posted no book content in the recent sample.

## 9. Ten content concepts

Hebrew hooks are written in the fallback voice (`lumebook-hebrew-voice` status: fallback, 12 of 15 samples), addressed to parents in the plural, and pass `voice_lint.py`. In creator posts the creator rewrites them in her own words; LumeBook's own carousels still never name the brand or a title.

**1. Professional book list for a transition, with one personalised pick**
- Buyer and occasion (hypothesis): parents of 3 to 6 year olds before gan or first grade.
- Format: carousel or reel by a speech therapist or parent guide, 5 picture books plus 1 where the child is the hero, comment word for the list.
- Hook:
  > 5 ספרים לפני כיתה א
  > ואחד שהילד שלכם בתוכו
- Product link: שלום כיתה א' or a gan book.
- Proof or objection: the creator's credential; answers "is it a real printed book" by showing pages.
- CTA: comment a word, the DM carries the creator's ambassador link.
- Examples: [DZphMo0CAUb](https://www.instagram.com/p/DZphMo0CAUb/), [Da0n_qzACqS](https://www.instagram.com/p/Da0n_qzACqS/), [Dc6VXOdMWOv](https://www.instagram.com/p/Dc6VXOdMWOv/), [DdegHrWjvH9](https://www.instagram.com/p/DdegHrWjvH9/).
- Primary KPI: books started via the link per 1,000 accounts reached. Confidence: medium for requests, low for purchases.

**2. Pacifier timing Q&A**
- Buyer and occasion: parents of 1 to 3 year olds planning to drop the pacifier.
- Format: SLP reel answering the questions her own comments asked.
- Hook:
  > מתי נפרדים מהמוצץ
  > ומה עוזר בלילה הראשון
- Product link: ביי ביי מוצץ.
- Proof or objection: professional answer to "when is it time"; avoid promises about results.
- CTA: comment word for a short guide plus the link.
- Examples: [Db6Bi-nMywx](https://www.instagram.com/p/Db6Bi-nMywx/).
- Primary KPI: books started for the pacifier title. Confidence: medium-low.

**3. One toilet skill, shown**
- Buyer and occasion: parents of 2 to 3 year olds starting diaper weaning.
- Format: hands-on demo reel (the format with the biggest outliers), the book as the story read before.
- Hook:
  > תרגיל אחד קטן
  > לפני שנפרדים מהטיטול
- Product link: נפרדים מהטיטולים.
- Proof: the demo itself. Objection: "my child isn't ready", answered by the professional.
- CTA: save, plus link in story.
- Examples: [DdUFGI3oO8T](https://www.instagram.com/p/DdUFGI3oO8T/), [DX6Ij0HIzlj](https://www.instagram.com/p/DX6Ij0HIzlj/), [Db2tjBCoLP3](https://www.instagram.com/p/Db2tjBCoLP3/).
- Primary KPI: plays vs the creator's median, then link sessions. Confidence: medium for attention, low for purchase.

**4. Telling the older child about the baby**
- Buyer and occasion: expecting mother with a 2 to 6 year old.
- Format: an episode of a pregnancy diary by a creator who is pregnant now.
- Hook:
  > איך מספרים לגדולה
  > שמגיע אח קטן
- Product link: אח חדש / אחות חדשה.
- Proof: the older child's reaction on camera (with consent).
- CTA: answer a question ("how did you tell yours?"), personal link in story.
- Examples: [DdtDs1WNRDp](https://www.instagram.com/p/DdtDs1WNRDp/), [DdwlAMSNv5S](https://www.instagram.com/p/DdwlAMSNv5S/).
- Primary KPI: books started for the sibling titles. Confidence: medium for engagement, low for purchase.

**5. What went in the gan bag**
- Buyer and occasion: parents in the first weeks of gan.
- Format: object-by-object reel, the book among practical items.
- Hook:
  > מה שמנו בתיק
  > לשבוע הראשון בגן
- Proof: objects shown in use. Objection: price, answered on screen.
- CTA: comment word for the list of links.
- Examples: [Dd5sq3TI1I5](https://www.instagram.com/p/Dd5sq3TI1I5/), [DbVCNNJiFUw](https://www.instagram.com/p/DbVCNNJiFUw/).
- Primary KPI: product questions per 100 comments, then link sessions. Confidence: medium.

**6. Price and delivery, said out loud**
- Buyer and occasion: any parent already considering (the payment step loses about half, 12 Oct note).
- Format: printed book in hand, the price with the follower discount, how many days it takes, what the preview shows.
- Hook:
  > כמה זה עולה
  > ותוך כמה זמן זה מגיע
- Proof: the real book. Objection: price, delivery, "will it look like my child".
- CTA: personal link.
- Examples: MeBook comments asking these questions (`research/competitor-content-analysis/comments_mebook_hebrew.md`); no creator in this sample shows a price on a book.
- Primary KPI: paid orders ÷ books started for the linked cohort. Confidence: low (hypothesis).

**7. Grandma asked what to buy**
- Buyer and occasion: grandmothers and aunts, birthday or Hanukkah.
- Format: a parent creator films the grandmother giving the book (real family, consent).
- Hook:
  > סבתא שאלה מה לקנות לנכדה
  > הנה מה שבחרנו
- Product link: birthday book or a holiday book.
- Objection: "I don't have a photo of the child", answered by showing how the parent helps.
- CTA: "send this to grandma", personal link.
- Examples: grandparent comments in E6; the weekly gift-giver post decided on 12 Oct.
- Primary KPI: orders through the gift-tagged link. Confidence: low.

**8. The present she opened first**
- Buyer and occasion: parents planning a 3rd or 4th birthday.
- Format: party reel ending with the child seeing herself in the book.
- Hook:
  > המתנה שהיא פתחה ראשונה
  > ביום הולדת 4
- Product link: birthday book (top seller).
- Proof: the child's reaction. Objection: timing before the party date.
- CTA: personal link, order-by date in the caption.
- Examples: [Dc0QYruIchn](https://www.instagram.com/p/Dc0QYruIchn/) (a 4th-birthday post), [Dd_6ZOfDjxd](https://www.instagram.com/p/Dd_6ZOfDjxd/) (tribute format).
- Primary KPI: product questions per 100 comments and books started. Confidence: low (no proven pattern).

**9. Reading aloud, page by page**
- Buyer and occasion: parents of 1 to 4 year olds who ask what to read.
- Format: SLP shows three questions to ask on any page, using the child's own book.
- Hook:
  > 3 שאלות לשאול
  > על כל עמוד בספר
- Proof: a real child answering. Objection: "my child won't sit for a book".
- CTA: save, comment word for a list by age.
- Examples: [Dar4kTwCMJV](https://www.instagram.com/p/Dar4kTwCMJV/), [Dc6VXOdMWOv](https://www.instagram.com/p/Dc6VXOdMWOv/).
- Primary KPI: saves (from Insights) and keyword requests. Confidence: medium.

**10. The gan gate, from the parent's side**
- Buyer and occasion: parents in gan adjustment.
- Format: relatable humour reel (the reach format), product only in the caption.
- Hook:
  > אני עדיין בשער של הגן
  > והיא כבר בפנים
- Product link: a gan book, soft.
- CTA: tag a partner; link in story.
- Examples: [DcrLtsFqzc0](https://www.instagram.com/p/DcrLtsFqzc0/), [DW5ze--jd01](https://www.instagram.com/p/DW5ze--jd01/) (807K plays, older breakout).
- Primary KPI: plays vs the creator's median (reach), with link sessions as a secondary check. Confidence: medium for reach, low for purchase.

## 10. Five tests for the next four weeks (15 Oct to 11 Nov 2026)

Before any test: confirm the ambassador link format with Yossi, enrol each test creator in the store's ambassador program, get read access to the ambassador ledger and to `acquisitionAttribution` per order, and fix or confirm `@lumebookai`. Creator books for Hanukkah are due 10 Nov (`shared/facts.json`).

All numeric thresholds below are **proposed test criteria**, not verified baselines. The only verified funnel numbers are store-wide (21.7% of people who start a book pay within 7 days; 85 of 202 orders that reached payment were bought in the last 30 days, Mixpanel, undercounted).

| | T1. Professional book list | T2. Comment word vs link sticker | T3. Lived moment vs expert | T4. Price shown vs not | T5. Gift-giver framing |
|---|---|---|---|---|---|
| Hypothesis | A professional's transition book list with one personalised pick (concept 1 or 2) yields more books started per 1,000 reached than a single-product post | Comment word with the link in a DM yields more books started per 1,000 plays than a story link sticker, not just more comments | A parent living the new-sibling moment yields more sibling-book starts than an expert talking about it | Showing price and delivery time raises paid orders per book started | Grandparent framing reaches buyers parent framing does not |
| Who | topaz_meir_slp first, then hen.kalimian.kids or hilla_gover_slp | topaz_meir_slp and orli.parenthood, 2 posts each | ima.shir, imkassandra__ vs nataliegaash | Two creators posting the same concept, one with price and delivery on screen, one without | One parent creator with a real grandparent on camera, plus LumeBook's weekly gift-giver post |
| Comparison | T3 and T4 single-product posts, normalised per 1,000 accounts reached | Same creator, same concept, alternating arms | Between creators, normalised per 1,000 reached | Arm A vs arm B, each vs the store-wide paid ÷ started rate | Gift-tagged link vs parent-tagged link |
| Primary outcome | Books started via the link within 7 days | Books started per 1,000 plays | Sibling-title books started | Paid orders ÷ books started (attributed) | Books started and paid via the gift link, plus "who is it for" answers in the post-purchase WhatsApp message |
| Tracking | Ambassador link + `utm_content=<shortcode>`; keyword count on day 7; Insights screenshot (reach, saves, shares, link taps) | `utm_content=dm-<shortcode>` vs `story-<date>` | `utm_term=t3-lived` / `t3-expert` | `utm_term=t4-price` / `t4-noprice` | `utm_term=t5-gift` / `t5-parent`; one WhatsApp question after purchase |
| Window | 7 days (link memory), final after the 14-day hold | 7 days per post | 7 days | 14 days | 14 days |
| Decision rule (proposed) | Keep the format with a creator if the post produces at least 1 paid printed order and at least 10 books started per 10,000 reached; otherwise change format before changing creator | Adopt the arm with at least 1.5x the books started per 1,000 plays over 2 pairs; otherwise treat as equal and use the creator's habit | Prefer lived-moment creators for sibling titles if they produce at least 2x the starts per 1,000 reached | Show price in every product post if the price arm's paid ÷ started is at least the store-wide rate and higher than the other arm | Continue the weekly gift-giver post after 4 weeks only if the gift link's starts per 1,000 sessions are at least those of the parent link |

**Recommended first:** T1 with topaz_meir_slp. She is already in process, has the strongest plays-per-follower among the professionals (3.25), runs a comment word on almost every post, and her own commenters asked when to wean. LumeBook has a pacifier title with 86 orders.

## 11. Measurement plan

### What tracking already exists (observed in lumebook.com's public JavaScript, fetched 14 Oct 2026)

| Piece | What the code does | What we do not know |
|---|---|---|
| Acquisition attribution | On landing, the site stores `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `fbclid`, `gclid` and the landing path as first touch and last touch (`lumebook_acquisition_attribution`). When a book is created (`POST /api/order`), it sends that record as `acquisitionAttribution` together with a `visitorId`. | Whether the admin stores and reports it per order. The 12 Oct note says the site does not save which link brought an order; the code sends it, so the gap may be in reporting, not in capture. The admin's own warning that "UTM coverage is under 80%" (12 Oct note) suggests UTMs are stored for some orders. |
| Consent gate | Attribution, Mixpanel, Meta pixel and GTM run only when the visitor accepts analytics cookies. | The share of visitors who accept. Everyone who declines is invisible to UTM attribution. |
| Funnel events | Mixpanel: page viewed, contents viewed, items added, checkout started, order created. Meta pixel: PageView, ViewContent, AddToCart, InitiateCheckout, Purchase. | Whether "preview completed" is its own event. Which events are available per UTM in Mixpanel. |
| Ambassador and recommender programs | Live pages `/IL/he/ambassadors` and `/IL/he/recommend`. Public settings (`/api/ambassadors/program`, 14 Oct): open, a ₪30 budget per printed book split between the follower's discount (₪0 to ₪30 in ₪5 steps) and the creator's commission, regular price ₪119, list ₪149, follower bands under 5K to 30K+, **link remembers the visitor for 7 days**, commission held **14 days**. Each ambassador gets a personal link and a dashboard listing books, pending, final and cancelled sales, and payouts by bit, PayBox or site credit. The Hebrew copy says every **printed** book bought through the link is credited. | Whether any creator from the map is enrolled. The exact link format and whether extra UTM parameters survive it. Whether digital-only purchases are credited (the copy says printed). How "₪30" relates to the 25% in `shared/facts.json` (₪30 is 25.2% of ₪119). |

**Interpretation:** LumeBook already has store-side, per-creator purchase attribution through the ambassador link. The research could not see any of its data. The cheapest path to real conversion numbers is to put every test creator on an ambassador link and get read access to the ambassador ledger and to `acquisitionAttribution` per order.

### Identifiers

- **Creator ID** = Instagram handle (lowercase, as in `C_all.json`).
- **Post ID** = Instagram shortcode (the `XXXXXXXXXXX` in `instagram.com/p/XXXXXXXXXXX/`), logged the day it goes live.
- **Test arm** = the concept and test ID from section 8 (e.g. `t1-sibling-a`).

### Link format (proposed)

Each creator's ambassador link, with UTMs appended if the link keeps them (to confirm with Yossi):

`<ambassador link>?utm_source=instagram&utm_medium=creator&utm_campaign=<handle>&utm_content=<shortcode or story-date>&utm_term=<test-arm>`

One link per placement: bio link, story link sticker and DM reply each get their own `utm_content` (`bio`, `story-YYYYMMDD`, `dm-<shortcode>`). Never a code (house rule: personal link, never קוד הנחה).

### Funnel, step by step

| Step | Measure | Source | Unique unit | Status today |
|---|---|---|---|---|
| Exposure | Reach, plays, average watch time | Creator Insights screenshot, 7 days after posting | accounts reached (reach), plays | Private to creator; ask in the brief |
| Engagement | Likes, comments, saves, shares, reposts | Public counts + creator Insights | interactions | Partly public |
| Consideration | Link-sticker taps, profile visits, keyword comments, DMs received | Creator Insights + comment count of the keyword | taps, people | Private / public (keyword) |
| Session | Landing page views with the UTMs | Mixpanel `page_viewed` (consent-gated) | sessions | Exists, not yet read |
| Book started | Orders created with `acquisitionAttribution.utm_campaign = <handle>` | Store order table | books (one person can start several) | Exists, reporting unknown |
| Preview completed | Preview viewed event | Mixpanel or store | books | Unknown if tracked |
| Checkout | `checkout_started`, payment-step arrivals | Mixpanel + store | sessions / orders | Exists |
| Purchase | Paid orders credited to the ambassador link (printed, 7-day window) and paid orders with matching UTMs | Ambassador ledger + order table | orders, books, people | Exists, not yet read |
| Economics | Revenue, average order value, revenue per session, cost per purchase (book cost + ₪30 allocation + shipping), contribution after costs | Order table + print cost from Yossi | ₪ | Print cost unknown (open question in the 12 Oct note) |

Keep three counts apart and never add them: **store orders** (server), **ambassador-credited orders** (7-day printed rule) and **platform-reported purchases** (Meta). Count people, sessions, books and orders separately; one buyer averaged 1.40 books (12 Oct note).

### Weekly routine (fits the daily log already agreed on 12 Oct)

1. Each creator post: log date, time, handle, shortcode, format, concept, link used.
2. Day 7 after each post: public counts (likes, comments, plays, reposts), keyword-comment count, and the creator's Insights screenshot (reach, saves, shares, profile visits, link taps).
3. Monday: export orders of the past week with `acquisitionAttribution` and the ambassador ledger; join on `utm_campaign` / ambassador ID; compare each creator's days against the store's daily orders.

### Attribution limits

- Consent: visitors who decline analytics cookies carry no UTMs; the ambassador link (server-side) may still credit them.
- 7-day window: a gift-giver who buys two weeks later is not credited.
- Cross-device and in-app browser: Instagram opens links in its own browser; a purchase finished later on another device can lose the link.
- Printed only: digital-only orders may not be credited to ambassadors.
- Organic spill-over: people who saw a creator but searched Google later are invisible; the daily-orders comparison is the only (weak) check.
- Platform-reported purchases (Meta) are modelled and overlap with store orders; report them separately.

## 12. What we still do not know

- Whether any creator content sells LumeBook books, and how many per post. No attributed data has been read.
- Reach, watch time, saves, shares, profile visits and link taps for any post (creator Insights only).
- Whether keyword requests become link clicks, books started or orders.
- Who buys: the store does not record the buyer's relation to the child; Meta's age segments are model attributions.
- Whether the ambassador link keeps extra UTM parameters, credits digital orders, and how many creators are enrolled.
- Whether `@lumebookai` was renamed, deactivated or restricted, and since when.
- Whether the patterns hold on TikTok (no TikTok handles in the map) or outside these 41 creators.
- Whether undisclosed paid promotion inflated any of the outliers.
- How comments outside Instagram's top-ranked 30 differ from the sample.
