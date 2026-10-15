# Round 2: which creator content hits the public buying signals (134 creators)

Collected 14 Oct 2026, evening. Extends the first round (41 creators) to the top half of the creator map.

**What this is and is not.** None of these creators works with LumeBook yet, so there is no sales data per creator. The question here is narrower: which of their own posts already show the public signals that usually sit just before a purchase (people asking where to buy, what it costs, saying they want it or bought it, asking for the link the creator offers). These are **proxies**, not conversions. A post that triggers them shows that this creator's audience is willing to ask about buying something; it does not prove anyone bought.

## Sample

- **Creators:** the top half of the 243-creator map by median reel views (122 accounts, cutoff 5,844 median views in the map) plus the 13 first-round creators below that line. One account no longer exists (shanina_advent.learn), so **134 creators** (121 of the top 122).
- **Posts:** up to 12 most recent posts per creator, 7 to 90 days old (180 days where fewer than 6): **1,456 posts**.
- **Comments:** up to 30 per post in Instagram's ranked order, on every post with comments: **22,428 comments on 1,391 posts** (22,281 from the audience, 147 from the creators).
- **Content coding from frames, slides and captions:** all 469 first-round posts plus 253 round-2 posts (the top posts on each KPI and a random 120 as baseline).

## The KPIs (every one public, none is a sale)

| KPI | How it is measured | Status |
|---|---|---|
| **Purchase signals** | Audience comments that ask where to buy, for a product link, the price, sizes, shipping or how to order (`product_q`), say they want to buy (`intent`), or say they bought or own it (`purchase`). Counted and per 100 sampled audience comments | Proxy, from public comments |
| **Offer requests** | Comments that ask for what the creator offered (the post's comment word, a free file, list, guide, workshop, group) | Proxy |
| Comments per 1,000 plays | Conversation depth on reels | Public |
| Reposts per 1,000 plays | Public repost count. DM shares are not public | Public |
| Plays per follower | Reach beyond the follower base (proxy: followers are not exposure) | Public |
| Saves, shares, link taps, profile visits, sales | Only in the creator's Insights or the store | Unavailable |

**How comments were classified.** A rule-based Hebrew classifier finds offer requests; checked against the 2,982 comments the agents classified in round 1, it agrees closely on offer requests per post (rank correlation 0.94). For buying signals the rules alone were weaker (0.50), so a broad net flagged every comment that might be a buying signal (4,481 candidates, 20% of comments; it caught 64 of the 68 buying-signal examples from round 1) and Sonnet agents read every candidate in Hebrew and labelled it. All counts below use those verified labels.

## Results in plain words

**1. Buying signals are rare, and concentrated.** 595 purchase signals in 22,281 audience comments (2.7%): 471 product or price questions, 74 statements of wanting to buy, 50 self-reported purchases. 241 of 1,391 posts have at least one; only **71 posts have 3 or more**. 99 of the 134 creators had at least one post with a buying signal; 35 had three or more such posts.

**2. What the 71 top buying-signal posts look like, compared with 548 ordinary coded posts:**

| Trait | Top buying-signal posts | Ordinary posts |
|---|---|---|
| A product is shown or demonstrated | 77% | 30% |
| The product is demonstrated in use | 41% | 8% |
| Format is a product review | 28% | 5% |
| A price is visible | 13% | 1% |
| A discount, code or deal is offered | 14% | 5% |
| Sponsored or a brand collaboration | 49% | 15% |
| Humour | 4% | 19% |
| A skit or POV | 0% | 9% |
| A practical takeaway | 90% | 62% |

**Interpretation:** people ask how to buy when they see one specific, useful thing working, with its price or a deal attached. Jokes and skits almost never produce it.

**3. Offer requests come from a different kind of post.** The 50 posts with the most offer requests per follower: 92% ask for a comment word (vs 15% of ordinary posts), 34% promote the creator's own product or service (vs 10%), 34% lean on an expert credential (vs 10%). They are mostly professionals' tips carousels and "comment X and I'll send you the list". 70 of the 134 creators ran at least one post where half or more of the sampled comments were offer requests.

**4. Sharing (reposts) comes from a third kind of post:** talking heads (33% vs 11%), expert credentials (23% vs 10%), reassurance (33% vs 20%) and skits (20% vs 9%), almost never a product (10% vs 30%) or a price (0%).

**So there are three different engines, and no post does all three.** Reach and sharing come from experts and relatable moments; offer requests come from free resources behind a comment word; buying questions come from a product shown working with a price or code.

## Creators whose own content reaches the buying signals

Separate lists, not a combined score. Numbers from `creators_kpi.csv`; "sampled" means the creator's comments we read.

**Most purchase signals (verified buying comments on their recent posts)**

| Creator | Map type | Followers | Purchase signals | Per 100 comments | Posts with a signal | What triggers it |
|---|---|---|---|---|---|---|
| michal_nunu | Parent | 17,088 | 54 | 34.6 | 8 of 12 | Try-on reels of evening dresses with a price ("₪100") |
| orelcabelli | Parent | 33,666 | 47 | 13.2 | 9 of 12 | Cleaning products demonstrated, personal code |
| sivan_grosman_zukerman | Family travel | 33,476 | 29 | 9.2 | 5 of 12 | Attraction recommendations (several "purchases" are bad reviews) |
| lital_magnezi | Gan teacher | 27,512 | 25 | 13.9 | 6 of 12 | Classroom items shown in use (toilet push light) |
| tom_zakai_levinkopf | Parent | 27,106 | 22 | 7.3 | 3 of 12 | Kids' shoes, sponsored, "I must get these for my son" |
| morkeisar | Parent | 29,811 | 17 | 16.8 | 4 of 12 | Sponsored posts (a Kenwood mixer with a comment word, a baby play mat, a brand collaboration) |
| hen.kalimian.kids | Child-dev professional | 39,185 | 14 | 6.0 | 2 of 12 | Reading-room makeover: "where is the rug from" |
| shelly.yudaikin | Special ed | 11,711 | 14 | 9.7 | 5 of 11 | Enquiries about her own therapy service and course ("where do you see clients", link requests) |
| ima.shir | Parent guide | 18,778 | 13 | 6.4 | 3 of 12 | Home device seen in a reel ("where is the steam cleaner from") |
| orel_zamir_ovadia | Parent | 21,556 | 13 | 7.1 | 4 of 12 | Recipes and kitchen-appliance deals (Cooking Chef sale) |

**Most offer requests (people asking for what the creator offered)**

saraigatt 316, danit_parenting_coaching 222, topaz_meir_slp 218, avigalg 179, lotanelias 179, hamatkonia 157, nofar_aizik 149, marialguide 146, netalie_kirstain 145, hodelia.travel 133 (requests among sampled comments).

**Kids' products and LumeBook-type moments inside the top buying-signal posts** (the closest evidence for LumeBook):
- Gift lists for a 3-year-old by development area: mash_iz `DZqIIV_DjFM`, hadar_baier_slp `DdGWWI1CACd` (Kodkod games), knafaim.ot_by_noy `DdWglWIKur-`.
- Toy reviews by therapists: trainingwheelsclinic (kinetic sand), maya_doskalovich_ot (Giotto kits), yana.nachmani (bath toy).
- A reading-room makeover (hen.kalimian.kids `DdZFL7NoIXu`) and a gan teacher's autumn book shelf (_shirley_unger_kids_activities `DeKFbzRAmIy`, 9 of 13 comments about the books).
- Back-to-school and gan items demonstrated (lital_magnezi, mamash_pashut, knafaim.ot_by_noy).
- Only 1 of the 71 top posts features a children's book. Books are not yet where these audiences ask to buy; toys, games and gear are.

## What this means for LumeBook

- **To get buying questions, the post must show the printed book working**: a child opening it and seeing themselves, the pages, the price with the follower discount, and how to get it. This matches what produced buying questions everywhere in this sample.
- **Best-fit creators for a buying test are the ones whose audiences already ask "where do I buy" about kids' products**: hadar_baier_slp, knafaim.ot_by_noy, mash_iz, maya_doskalovich_ot, trainingwheelsclinic, yana.nachmani, lital_magnezi, hen.kalimian.kids, _shirley_unger_kids_activities, shelly.yudaikin. Most are child-development professionals or gan teachers.
- **A "gift for a 3-year-old" list with the book in it** is the format that already pulls buying questions on kids' products (three creators).
- **Comment-word funnels fill DMs, not carts.** They are worth using to deliver the personal link, but their comment counts should not be read as demand for a book.
- **Humour and skits are for reach, not sales**, in this sample.

## Limits

- Proxies only: no clicks, sessions, carts or orders. A creator's buying-signal score reflects what they usually post (many sell clothing, cleaning products or trips), not how their audience would respond to a personalised book.
- Comments are Instagram's top-ranked 30 per post; buying questions further down are missed, and ranking may favour them or not (unknown).
- Self-reported "purchases" include negative reviews of the thing bought.
- The agents' labels have judgement calls (venue questions, recipe questions, age-fit questions); their notes are kept in the session scratchpad.
- Content coding covers all round-1 posts but only 253 round-2 posts (top groups plus a random 120), so trait comparisons for round-2 creators rest on that sample.

## Files

- `posts_kpi.csv`: 1,456 posts × KPIs (+ content codes where coded). No captions or commenter names.
- `creators_kpi.csv`: 134 creators × KPIs.
- `traits.json`: the top-vs-baseline trait tables.
- `classify.py`, `validate.py`, `kpi.py`, `round2.py`, `CANDIDATE_BRIEF.md`: how it was made.
