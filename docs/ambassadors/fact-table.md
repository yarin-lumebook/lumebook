# Ambassador program: fact table

Written 15 / 11 / 2026 for the redesign of https://lumebook.com/IL/he/ambassadors (prototype: `sites/lumebook-ambassadors-v2/`). Every answer has a source. "Live" means read from lumebook.com that day; nothing was submitted.

## Sources

| Code | What it is |
|---|---|
| T | Binding terms shown at `/IL/he/ambassadors/terms`: "תקנון תוכניות השגרירים והממליצים של LumeBook", in force from 1 / 10 / 2026, updated 1 / 11 / 2026, version id `ambassadors-2026-11-01b` (the `termsVersion` the form sends). Section numbers below are its own |
| T-rec | The other terms text in the same chunk, shown only at `/IL/he/recommend/terms` (recommenders, version `recommenders-2026-10-31`) |
| API | `GET https://lumebook.com/api/ambassadors/program`, live: `{"open":true,"budgetMinor":3000,"stepMinor":500,"discountOptions":[0..3000],"regularPriceMinor":11900,"listPriceMinor":14900,"followerBands":[4 bands],"linkWindowDays":7,"holdDays":14}` |
| Page | The live page's Hebrew strings (store locale chunk, `ambassadors.*`) |
| Code | The live page's code: `AmbassadorProgram-*.js` (form), `index-*.js` (signup call, constants), `AmbassadorDashboard-*.js` |
| Facts | `shared/facts.json` `offer` (Yossi via Yarin, 4 to 11 / 10 / 2026) |

## The table

| Question | Answer | Source | Status |
|---|---|---|---|
| Who is it for? | 18+, living in Israel, parent or guardian of the children, with a public and active Instagram profile of their own. No follower minimum. One link per person and per phone | T 2.1, 2.2, 2.4 | Confirmed |
| What do you get? | (1) One printed book with your children's photos and name, shipping included, agreed value ₪149. (2) A personal link: from every printed book bought through it, 25% of the price, split between the buyer's discount and your reward (Yarin, 15 / 11 / 2026: "זה 25% לא 30 שקלים"; the store's settings hold it as a ₪30 budget, which its page shows as 25%). (3) A personal area (dashboard) with every book, its status and your balance | T 4.1, 10.1, 13.1; Code (`bn` = 14900); API `budgetMinor` 3000 | Confirmed |
| Conditions on the book | It is the payment for the content below and for the 8 month permission to use it. No cash alternative | T 10.1, 12.4 | Confirmed |
| What must you do? | At least one original Reel on Instagram following LumeBook's brief (a post, story, carousel or another platform does not count); send the final video and the raw footage; tag ‎@lumebook.il; send ‎@lumebook.il an Instagram collaboration invite on the Reel (required, a tag is not enough); mark every post about LumeBook or with the link as a commercial collaboration; say you get a reward when you share the link; no link in private messages to people who did not ask | T 9.2, 9.4, 10.2 | Confirmed |
| Permission to use the content | The content stays yours. LumeBook may publish the final video, raw footage and photos (your children included) in any media, paid ads included, for 8 months from LumeBook's first publication, or from 30 days after it received the material if it did not publish sooner. After 8 months you can end it at no cost; LumeBook handles a stop request within 7 business days | T 12.1 to 12.6 | Confirmed |
| Children in the content | You are the parent or guardian; the other parent (if any) agrees; other children only with their parents' OK; no nudity, bath or toilet. If a child may be harmed, consent is missing or the other parent objects, LumeBook stops active publication without a minimum period or payment | T 11.1 to 11.4, 12.6 | Confirmed |
| Does joining cost money? | No. Free to join, no purchase first | T 2.1, "בקצרה" | Confirmed |
| Does the book or shipping cost money? | No, the book is given without payment, shipping included | T 10.1 | Confirmed |
| Any cost later? | Only if you ask LumeBook to stop using the content before the 8 months end: you repay the agreed book value, ₪149 incl. shipping and VAT if any, minus anything you already paid, within 30 days of a written demand. No automatic charge | T 12.5 | Confirmed |
| Approval needed to join? | No review before the link: the link is created at signup, right after the WhatsApp code. LumeBook may check the details and refuse or end membership if they are false (fake profile, bought followers) | T 2.3, 3.1; Code (signup returns `status:"active"` with the link) | Confirmed |
| Discount code or personal link? | Personal link. The buyer sees the discounted price automatically, no coupon code | T 3.1; Facts `offer.banned_wording_he` | Confirmed |
| Who gets the discount, who gets the reward? | Out of 25% of each printed book's price you choose how much is the buyer's discount, the rest is your reward. The store offers 7 steps: 0%, 4.2%, 8.3%, 12.5%, 16.7%, 20.8%, 25% (its ₪0 to ₪30 in ₪5 steps, shown as a share of 25%, as the live page does). Fixed once the link exists; a second link to change it is not allowed | Yarin 15 / 11 / 2026; T 4.2, 4.3; API `discountOptions`; Code (`ambassadorPercent-*.js`) | Confirmed |
| Which purchases count? | A regular printed book (not a group order for a kindergarten or company, not digital only, not an upgrade or add-on), within 7 days of the last click on your link (last link wins, stored in the browser), paid at the link price, not bought with your own phone number. Not combined with other LumeBook offers | T 3.2, 3.3, 5.1 | Confirmed |
| When is the reward final? | Pending 14 days after payment, then final if not returned or cancelled. A later return or cancellation takes it back | T 5.2; API `holdDays` | Confirmed |
| How is it paid? | Final reward goes to a balance. Redeem the whole available balance at once: (a) books on lumebook.com, any amount, no receipt needed, the team writes on WhatsApp within 7 business days; or (b) money by bit or PayBox, full value, from ₪300 balance, with a legal receipt or invoice (an עוסק פטור file is enough), paid within 7 business days of a valid request. Final reward not redeemed within 180 days expires | T 6.1 to 6.5, 8.2; Code (`qh` 30000, `nc` 180, `ic` 7) | Confirmed for ambassadors (see conflict 1) |
| Taxes | Participation is independent, not employment; the reward is a referral fee; the book and books bought with the balance may count as income; reporting is yours; tax may be withheld at source | T 7, 8 | Confirmed |
| What happens right after the form? | WhatsApp code (phone verification dialog) → the link appears on screen with copy and share buttons, and in the dashboard. Next for the book: create a book on the site and send its tracking number on WhatsApp (055 980 0791); the number is in the book editor and on "my books" | Page `form.phoneNote`, `success.*`, `dashboard.gift.*`; Code (401 → `PhoneVerificationDialog`, then resubmit) | Confirmed |
| Commitments, dates, limits | One Reel minimum; 8 month use permission; no exclusivity, no sales target, stop sharing any time; LumeBook may change or end the program with at least 14 days' notice; the program has no fixed term | T 7.3, 12.4, 16.1, 16.2 | Confirmed |
| Deadline to publish the Reel | **Not stated anywhere** (terms, page, dashboard) | none | **Open** |
| When and how the brief is sent | "The brief you will receive from LumeBook". When, and in which channel, is not stated | T 10.2 | **Open** |
| Does the team check anything before printing the book? | Terms only say "we handle the rest" | T 10.1 | **Open** |
| Contact | WhatsApp 055 980 0791, support@lumebook.com | T 1.1; Code (`Gh` 972559800791) | Confirmed |

## Where the sources disagree

1. **Cash payout share.** T (ambassadors) 6.3, the live page, the dashboard and the consent text: money for the **full** balance from ₪300. T-rec section 5 (recommend terms, 31 / 10 / 2026): **half** of the balance from ₪300. The ambassador page follows T. The recommend page's own FAQ also says full value, so T-rec looks out of date. Not this page's problem, but someone should fix one of them.
2. **"25%" against "₪30". Decided: 25%** (Yarin, 15 / 11 / 2026: "זה 25% לא 30 שקלים"). The live hero says "עד 25% מכל ספר" and its slider shows percentages; T 4.1 and the API say ₪30 per book in ₪5 steps (25.2% of ₪119). The new page presents 25% and computes the steps exactly as the live store does (`floor(budget / price)` = 25, each ₪5 step as its part of it, so ₪15 = 12.5%). Worth aligning the terms' wording with 25% so the page and the terms say the same thing; until then a price change would move the store's computed percentage.
3. **`shared/facts.json` `offer`** still lists four open questions (sale value, payout method and timing, tracking, changing the split). T answers all four (sections 4.1 to 6.5 and 4.3). The block was not changed in this pass; a new `ambassador_program` block holds the store's terms.
4. **"Book in return for content approved for publication"** (dashboard `gift.title`, success `next`). T 10.1 gives the book to every ambassador against the content obligations; it mentions no approval of the content before the book. The new page avoids the ambiguous phrase.
5. **Old Google Form and Vercel ambassadors site** (`sites/lumebook-ambassadors`, retired) said 20%. Both are retired; nothing here uses them.

## Not used on the new page, on purpose

- The live page's "כמה זה יכול להצטבר?" box (100, 200, 300 books → ₪1,500, ₪3,000, ₪4,500): it is labelled an illustration, but it reads as an income expectation. The new page shows one book only.
- "UGC", "Collaborator", "יתרת התגמול" without explanation.
