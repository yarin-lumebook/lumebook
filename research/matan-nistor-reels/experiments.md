# Five LumeBook tests from the @matan.nistor study

Each test turns one finding in `report.md` into a change LumeBook can film and measure with what it already has:
- Trial Reels on @lumebook.il (shown to non-followers first; the November reels already go out this way, `reels.json` defaults)
- the Meta export (`research/carousel-audit/src/audit.py import`)
- the numbers Yarin logs from Insights 24 hours after posting (`reels.py log <id> skip=.. watch=.. nonfollow=.. lumi=.. dms=..`)
- a UTM link per Reel (`reels.py link <id>`), which shows sessions and books started

Every threshold below is a **proposed testing rule** chosen for this small account, not an industry benchmark. LumeBook's Reels have had small counts (median 48 views on 02 / 10 / 2026, `shared/facts.json` baselines), so each test runs as pairs and repeats before deciding; one pair never decides anything.

Priority is the expected value of the answer against the cost of producing it.

| # | Test | From finding | Cost | Why this rank |
|---|---|---|---|---|
| 1 | A situation with a payoff against the same message said to camera | 1 | Medium (needs a real grandmother) | The widest gap in the study; decides what most future Reels look like |
| 2 | Re-cut the first 2 seconds only | 3, 4 | Low (re-edit existing reels) | Cheapest; tells whether openings are the bottleneck |
| 3 | The keyword earned at the end against no keyword | 6 | Low | Decides how reach and לומי Reels are judged and split |
| 4 | Narrated montage from owned footage against a talking head | 2 | Medium | A repeatable format Yarin can make alone |
| 5 | A 10-second one-look card against a 25-second version | 8 | Very low | Weakest evidence, nearly free |

---

## Test 1: Something happens, against something said

- **Hypothesis.** A Reel where a real person does something with the book and reacts (a grandmother opens it, finds the grandchild's name and writes the dedication) holds non-followers longer than the same facts said to camera. Basis: a story engine in 54 of his top 100 and 1 of 20 comparisons.
- **Creative change.**
  - Version B (brief 1): the grandmother situation, about 28 s.
  - Version A: reel 1.4 in `reels.json` ("סבתא, זה מה שהנכד מקבל אצלנו"), already scripted, Yarin naming the same three facts (the cover, the name inside, the handwritten dedication).
  - Same book, same hook text, same לומי ending, same posting hour.
- **Primary metric.** Skip rate from Insights (lower is better), logged 24 hours after posting.
- **Secondary metrics.**
  - Average watch time.
  - Views from non-followers.
  - Shares per 100 reach.
- **Guardrails.**
  - לומי comments and DMs per 1,000 views no lower than A by more than a third.
  - No child on camera.
  - No price.
  - The grandmother's written consent, and the parents' consent before the grandchild's face appears on the cover.
- **Decision rule (proposed testing rule).**
  - Run 3 pairs on 3 different books.
  - Adopt "situation first" for reach Reels if B has the lower skip rate in at least 2 of 3 pairs and the higher median views from non-followers.
  - If results split, run 2 more pairs before deciding.

## Test 2: The first two seconds

- **Hypothesis.** An opening that makes sense on its own and shows something concrete in the first second (the child's name on the cover, the hero page) keeps more viewers than a question-style hook over a general shot. Basis:
  - 72 of his top 100 open with a self-contained sentence, against 8 of 20 comparisons.
  - Concrete hooks are more common in his top 25 (8 money or number hooks against 2 in ranks 76 to 100).
- **Creative change.**
  - Take two finished November reels.
  - Keep everything after 0:02.
  - Version A keeps the current opening.
  - Version B opens on a close-up of the cover with the name readable, with a first spoken line that is a whole statement (brief 3).
  - Post both as Trial Reels on separate days at the same hour.
- **Primary metric.** Skip rate.
- **Secondary metric.** Average watch time.
- **Guardrails.**
  - The name shown is a sample book's or used with written consent.
  - The lint passes (`reels.py lint`).
- **Decision rule (proposed testing rule).**
  - Adopt B's opening style if its skip rate is lower in both pairs by 5 percentage points or more.
  - If it is lower in one pair only, run a third.

## Test 3: Earn the keyword, or don't ask

- **Hypothesis.** A לומי ask lowers reach, as it did across 124 of his keyword Reels (1.6% in his top tenth against 12.0%). Placed after a story with a stake, it still collects DMs.
- **Creative change.**
  - Brief 4's Hanukkah deadline story in two edits:
    - Version A ends on the default purple לומי card (spoken and on screen) and the caption CTA.
    - Version B ends on the story's last beat, with the CTA in the caption only.
  - This needs a one-off exception to the reel defaults, which burn `cta_screen` on every reel. Yarin decides.
- **Primary metrics** (one for each purpose, because the two versions serve two purposes):
  - Views from non-followers (reach).
  - DMs that received the link, per 1,000 views (leads).
- **Secondary metrics.**
  - Books started from the Reel's UTM link.
  - Shares per 100 reach.
- **Guardrails.** Hanukkah dates stated exactly as in `shared/facts.json` (last order day 05 / 12 / 2026); no promise beyond it.
- **Decision rule (proposed testing rule).**
  - If B reaches at least 30% more non-followers and A brings at least twice B's DMs per 1,000 views, split the calendar: reach Reels without the on-screen ask, לומי Reels with it.
  - If A matches B on reach, keep the ask everywhere.

## Test 4: Narrated montage from owned footage

- **Hypothesis.** One voiceover argument over footage that changes with every line (his strongest format outside cash stunts: 6 top Reels, a median 13.5 times their month) holds attention better than the same words said by a talking head.
- **Creative change.**
  - Version B: brief 2, reel 4.1 rebuilt as a narrated montage, Yarin's voice, one owned shot per line.
  - Version A: Yarin says the same lines to camera holding the book.
  - Same length, about 25 s.
- **Primary metric.** Average watch time as a share of the Reel's length.
- **Secondary metrics.**
  - Skip rate.
  - Shares per 100 reach.
- **Guardrails.**
  - Only footage LumeBook owns or has the rights to (no film clips, no stock pretending to be real).
  - No AI wording.
  - No price.
- **Decision rule (proposed testing rule).** Make the narrated montage a monthly format if B's watch share is higher in 2 of 2 pairs and its skip rate is not worse by more than 3 points.

## Test 5: The one-look card

- **Hypothesis.** A still card readable in one look draws views and shares out of proportion to its effort. In his account, Reels under 15 s sit at 1.74 times their month across 51 Reels, but five of his six top cards are ordinary.
- **Creative change.**
  - Version A: brief 5 as a 10 s still card (three "instead of" swaps for a grandparent's Hanukkah gift).
  - Version B: the same three lines as a 25 s Reel, each line over its own shot.
- **Primary metric.** Views relative to LumeBook's own Reel median that month.
- **Secondary metrics.**
  - Shares per 100 reach.
  - Comments.
- **Guardrails.**
  - Card text passes the voice lint.
  - Inside the 10 to 30 s reel rule.
  - CTA in the caption.
- **Decision rule (proposed testing rule).** Keep cards as an occasional low-cost slot if A beats LumeBook's monthly Reel median in views in 2 of 3 posts; drop them otherwise.

---

## Logging

For every Reel in these tests, log the same row:
- the brief and its version
- the posting date and hour
- Trial Reel or not
- views, non-follower views, skip rate, average watch time
- shares, saves, לומי comments, DMs sent
- UTM sessions and books started

`reels.py report` already prints most of these per series. Record the test number in the Reel's notes in `reels.json`, so the hub's calendar shows which version is which.
