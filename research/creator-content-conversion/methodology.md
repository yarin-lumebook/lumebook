# Methodology: creator content and purchase intent

Research run on 14 Oct 2026. Question: what content interests LumeBook's potential buyers, what prompts them to consider buying, and what LumeBook should test to turn that interest into purchases.

Labels used in every file: **Observed** (seen directly in a post, a profile, a comment or a file), **Interpretation** (my reading of observed material), **Hypothesis** (a claim to test, not yet supported).

## 1. Inputs read before browsing

| Source | What it gave | Status |
|---|---|---|
| `docs/lumebook-product-brief.md` | Product, price (₪119 printed, list ₪149), catalogue, occasions | Read 14 Oct; brief is dated 1 Oct |
| `docs/lumebook-sales-data-decisions-2026-10-12.md` | Internal sales figures from 17 admin screenshots of 12 Oct: top books, funnel, Meta segments, cities | Internal; figures stay out of public pages |
| `shared/facts.json` | Creator offer (one 25% allocation per sale via personal link), barter batch, paid hold, key dates | Read 14 Oct |
| `creators/creator-research/src/C_all.json` | The creator map | 243 creators on 14 Oct (the README still says 304: 61 under-5K creators were removed on 12 Oct) |
| Creator map live database (artifact `MPuqcaCXXF5CGQiDMaDpbB`, collection `outreach`) | Outreach status per creator, read only | 185 records: 84 sent, 56 declined, 12 in process, 8 follow-up due, 3 at book stage, 22 without a status |
| `creators/creator-research/src/research/` | How the map was built, pass-3 raw numbers | Map numbers were read 3 Oct and 11 Oct |
| `research/competitor-content-analysis/` | MeBook creator-collab reels and their comments (read 3 Oct) | Used as comparison only |
| `research/carousel-research/`, `research/kids-brand-content-research/` | Comment-keyword funnels, prior examples | Used as context only |
| `creators/correspondence/mor-knoll/` | One creator's private email (13 Oct) with a self-reported sales figure | Private, self-reported, not verified |
| lumebook.com public JavaScript (fetched 14 Oct) | What tracking the store already has | Observed in code; data behind it not seen |

## 2. Creator inventory and sample

**Inventory (observed, `C_all.json`, 14 Oct):** 243 Instagram creators, all Hebrew. Archetypes: parent guide/coach 58, parent 38, child-development professional 37, family travel 18, gan/preschool 13, homeschool 11, special education 10, others 58 (party producers, photographers, kids activities, grandparents 4, dads 4, books 5). Followers at map time: median 10,300, range 1,009 to 46,100. Location is recorded for 7 of 243 creators, so location could not be used as a sampling dimension. The map's scores (`s`, `score`) are fit estimates made when the map was built; they were not used as evidence of performance.

**Sample: 41 creators** (40 planned plus `ima.shir`, used to test the collector and kept). Purposive and stratified, chosen to cover:

| Stratum | Creators | Why |
|---|---|---|
| Parents and family creators | 15 (including 3 fathers) | Moms of babies to school-age kids, close-in-age siblings, twins, blended family, religious family, product-finds creators |
| Parenting and child-development professionals | 18 | Parent guides, speech and occupational therapists, gan teachers, a special-education teacher |
| Children's books | 3 | Two SLPs who recommend books, two authors (one wrote a MeBook book) |
| Gift-giver or occasion perspective | 4 | A real grandfather account, a grandmother comedy character, a birthday-party producer, a first-birthday photographer |
| Comparison | 1 | A high-reach travel couple with a baby (in process with LumeBook) |

Sizes on 14 Oct: 6 under 5,000 followers, 10 between 5,000 and 12,000, 13 between 12,000 and 25,000, 12 above 25,000. Current collaboration candidates included: 13 of the 15 creators marked "in process" or "book stage" in the map database, and 10 of the 12 barter-batch creators in `shared/facts.json`. Selection reason per creator: `creators.csv`.

**Exclusions:** creators whose last post was before July 2026 (stale), accounts whose content is mainly food, cleaning, fashion or adult relationships with little child content, nutrition and baby-sleep accounts outside LumeBook's 1 to 10 age range, and a second grandparent comedy character (one was enough to test the voice). The two other grandparent accounts are comedy characters; no verified real-grandparent creator exists in the map apart from `saba.chiche`. `mor_knoll` is a MeBook conflict; she was kept because her book posts are the only direct evidence of a creator selling a children's book.

## 3. Post collection

- **Platform:** Instagram only (the map holds no TikTok handles).
- **How:** the built-in browser pane, signed in to Instagram (read-only use: no follows, likes, comments or messages). For each creator I replayed the requests Instagram's own profile page makes: the profile posts query (12 posts a page, up to 7 pages), the profile query (exact follower count, bio) and the reels-tab query (play counts). Collected 14 Oct 2026 between 18:04 and 18:19 Israel time. 2,992 posts were fetched in total.
- **Grid order is not date order.** Instagram lets creators rearrange their grid, so posts were sorted by publish time after fetching, and pages were fetched until two consecutive pages had no post from the last 200 days.
- **Eligible post:** a feed post (reel, carousel, single image) that the creator owns or co-authored, published 7 to 90 days before observation. Posts under 7 days old were excluded from the baseline because their counts were still growing.
- **Sample:** up to the 12 most recent eligible posts per creator. Where the 90-day window gave fewer than 6 posts, it was extended to 180 days. This happened for `heli_sabag`, `hilla_gover_slp`, `nataliegaash` and `yuli.brosh` (labelled in `creators.csv` and `posts.csv`). Seven creators have fewer than 12 sample posts because they posted less.
- **Result:** 469 sample posts (312 reels, 146 carousels, 11 images), published 18 Apr to 7 Oct 2026; 59 of them co-authored (Instagram collab posts).
- **Older breakouts, analysed separately:** an older or pinned post whose plays (reels) or likes (other formats) were at least 5 times the creator's in-sample median for that format. Up to the 3 largest per creator were kept: 96 posts, published June 2023 to September 2026. They are excluded from every baseline and leaderboard of recent posts.

## 4. Metrics and formulas

All counts are what Instagram's web client returned to a signed-in viewer on 14 Oct. None are unique people.

| Metric | Source | Status |
|---|---|---|
| Plays (reels) | reels-tab `play_count` | Publicly observed (shown on the reels grid). Plays are not unique reach: replays count |
| Likes | `like_count` | Publicly observed; hidden by the creator on 41 sample posts (left blank) |
| Comments | `comment_count` | Publicly observed; includes replies |
| Reposts | `media_repost_count` | Returned by Instagram's web client; missing on 105 sample posts (left blank). Not the same as DM shares, which are not public |
| Facebook cross-post likes and comments | `fb_like_count`, `fb_comment_count` | Returned by the API for cross-posted posts; reported separately, never added to Instagram counts |
| Followers | profile `follower_count` on 14 Oct | Publicly observed. Followers are not exposure |
| Paid-partnership label | `is_paid_partnership` | Observed: false on all 469 sample posts. Sponsorship was therefore coded from captions and tags |

Formulas (denominators stated, blanks where the denominator is missing):

- `likes_per_1k_plays = likes ÷ plays × 1,000` (reels only)
- `comments_per_1k_plays = comments ÷ plays × 1,000`
- `reposts_per_1k_plays = reposts ÷ plays × 1,000`
- `plays_per_follower_proxy = plays ÷ followers` (**proxy**: followers are not the audience that saw the post)
- `likes_per_1k_followers_proxy`, `comments_per_1k_followers_proxy` (**proxy**, used for carousels and images, which have no public view count)
- `rel_plays = plays ÷ median plays of the creator's sample reels`; `rel_likes`, `rel_comments` the same for likes and comments within the same format. Computed only against the creator's own posts, so audience size cancels out. A format with fewer than 3 sample posts is flagged as a thin baseline.

Medians, not means, throughout. Leaderboards keep reels, carousels and images apart and never mix platforms.

## 5. Content coding

Every sample and breakout post (565) was coded against a fixed schema (`posts.csv` columns `topic` to `notes`): topic, problem or desire, buying occasion, proposed buyer segment and its basis, format, length, on-screen hook, caption first line, hook type, emotional angle, practical takeaway, product visibility and category, proof, price visibility, discount wording, CTA, destination, sponsorship status, LumeBook relevance.

- **Media inspected:** for reels, 6 frames per video (0.3 s, 1.5 s, 3 s, 35%, 65% and 92% of the duration) on one contact sheet; for carousels, every slide up to 12; for images, the image. Plus the full caption and Instagram's automatic alt text. The `inspection` column records what was seen per post. Carousels longer than 12 slides were seen only up to slide 12 (noted per post).
- **Audio:** not available for most posts. 24 of the 105 deep-dive reels were transcribed with local Whisper (Hebrew turbo model): the first 45 seconds for the first 6, the first 30 seconds after that, strongest and ordinary pairs first; the run was stopped for time (about 3 minutes per reel on this Mac). 14 of the 24 returned no speech (Whisper writes "תודה רבה" over music-only audio). Result per reel: `whisper_first_30s` in `posts.csv`. Spoken content is otherwise unknown and coders were told never to describe it.
- **Who coded:** Claude Sonnet sub-agents, one creator dossier at a time, under a written brief (Hebrew quoted exactly or marked unclear, observed vs inferred separated, no guessing about people's age, location or parenthood). I checked a sample of posts against the sheets myself (see section 8).
- **Sponsorship:** `paid_partnership_label` only when Instagram's flag was true (never, in this sample). `likely_sponsored` = brand tagged or named plus a code, link or partnership wording. `giveaway` = giveaway rules in the caption. Undisclosed paid support cannot be ruled out.

## 6. Comments

- **Which posts (184):** 150 "deep-dive" posts: per creator, the strongest recent post (highest `rel_plays` for reels or `rel_likes` otherwise, among formats with at least 3 sample posts), a matched ordinary post (same format, ratio closest to 1.0, nearest in date) and up to 2 more sample posts whose caption mentions a LumeBook buying occasion, books, gifts or an offer (keyword match). After coding, 34 more posts coded as high LumeBook relevance (books, gan, potty, first grade, birthday, new sibling) with at least 5 comments were added (`deep_role = extra_high_relevance` in `posts.csv`), including 9 older breakouts.
- **Which comments:** up to 30 top-level comments per post, as Instagram's web client served them, plus the preview replies it attached. 2,982 comments in total (2,488 on the deep-dive posts, 494 on the extra posts). In the deep-dive set Instagram marked most comments as ranked and the order was neither newest nor oldest first, so the sample follows Instagram's relevance ranking. **Bias:** ranking favours liked comments, comments from accounts close to the creator and possibly from the viewer's own network. Posts with more than 30 comments are represented by their top-ranked 30, not a random sample.
- **Classification:** one primary class per comment (identification, personal experience, help request, product or price question, objection, explicit buying intent, purchase report, keyword request, tag or share, giveaway entry, generic praise, creator reply, spam). Unique commenters counted per post, excluding the creator. Done by Sonnet sub-agents under `COMMENT_BRIEF` rules; I re-read the purchase-intent and objection comments quoted in `evidence.md` myself.
- **Purchase-intent signal** (proxy) = explicit buying intent + product or price questions + self-reported purchases. Keyword requests (comments that only repeat a word the post asked for to get a link) are counted separately: they are requests for an offer, not spontaneous intent.

## 7. What could not be measured

| Funnel stage | Status in this study |
|---|---|
| Reach, impressions, watch time, retention, completion | **Unavailable**: only the creator sees them in Insights |
| Saves, DM shares | **Unavailable** |
| Profile visits, follows from a post, link clicks, CTR, DMs | **Unavailable** |
| Site sessions, books started, previews, checkout, payment step, orders, revenue per creator or post | **Unavailable** for creators. The store already records UTM and click-ID attribution on each order it creates and runs an ambassador-link program (see `report.md`, measurement plan), but no creator data from either was available to this study |
| Store-wide funnel | **Privately verified** baseline only (internal admin screenshots of 12 Oct, not tied to any creator or post) |
| Creator-reported sales | One self-reported figure in private email, not verified |

Missing means unknown, not zero.

## 8. Quality checks

- Contact sheets were spot-checked for legibility of Hebrew burned-in captions before coding started.
- Coded posts re-checked by hand against their sheets and captions: the first-grade book carousel (hen.kalimian.kids `DdegHrWjvH9`), the two self-reported sales posts (yaffa_michaela_zukerman `DdoeylHDeQQ`, `DdjvPhvjbmw`), the gan book list (tal_strul `DZphMo0CAUb`; her bedtime list `DdwREvSCJg2` was checked on caption, tags and comments only) and a pregnancy reel (ima.shir `Dd3waGvtkfm`). The coding matched what the slides and frames show.
- Every comment quoted in `evidence.md` and `report.md` was re-read in the raw comment data, not only in the coders' summaries, and a keyword scan of all raw comments (price, how to order, want, bought, gift, book words) was compared with the classifier's counts.
- Coder conventions to know: where a caption was cut off but every comment was the same word answered by a templated creator reply, comments were coded as keyword requests; age-fit questions about books count as product questions, about activities as help requests; an occasion is marked on a comment only when the comment itself names it.
- Comment counts per post: the fetcher logged the pre-trim count; the stored and classified comments are capped at 30 per post (2,982 in total).
- Follower counts drift: `saba.chiche` had 4,143 followers in the map and 1,901 on 14 Oct.

## 9. Biases and limits

- Purposive sample: findings describe these 41 creators, not Israeli parenting Instagram as a whole.
- Observational: no comparison here shows that a topic causes attention or purchases.
- Post age differs inside the 7 to 90 day window; older posts had more time to collect plays. Within-creator ratios reduce but do not remove this.
- Co-authored posts are distributed to two audiences, which inflates their counts; they are flagged.
- Giveaways inflate comments; comment-keyword CTAs inflate comments by design. Both are flagged and analysed separately.
- Re-shared content (some creators subtitle other people's clips) is coded as such where visible.
- Undisclosed paid boosting cannot be detected.
- The Instagram account used for viewing affects comment ranking.
- Coding by language models can misread Hebrew; quotes used as evidence were re-read by hand.

## 10. Access limits met

- `@lumebookai`, the Instagram account the store links to, returned "Sorry, this page isn't available" in the signed-in pane on 14 Oct, and a crawler-style fetch returned no profile data while two control accounts returned theirs. Cause unknown (renamed, deactivated or restricted). LumeBook's own posts could therefore not be included.
- Reels plays come from the reels tab, which covers the most recent ~60 reels; 12 sample reels had no play count there.
- No access to any creator's Insights, to the store's admin, to Mixpanel, or to the ambassador-program dashboard.
