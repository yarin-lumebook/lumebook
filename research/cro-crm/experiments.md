# Experiments and changes to measure

Internal, holds sales figures. Part of `research/cro-crm/` (start at `report.md`). Findings referenced as A1, B2 and so on are in `audit.md`; sources in square brackets (such as [S-timing]) are in `sources.md`.

## 1. Can LumeBook run A/B tests at all?

An A/B test (a randomised controlled experiment: visitors are split by chance between the current version and a change, and only the change differs) needs enough people to tell a real effect from noise. The numbers below come from the 12 Oct admin readout (`docs/lumebook-sales-data-decisions-2026-10-12.md`) and were computed with the standard two-proportion sample-size formula at 95% confidence and 80% power (close to the 16σ²/δ² rule of thumb in [S-exp]). Kohavi and co-authors put the practical floor for useful A/B tests at "at least, thousands of active users, preferably tens of thousands", and warn that underpowered tests that do reach significance exaggerate the effect [S-exp].

| Step being changed | Baseline | Volume per month (approx.) | To detect | Needed in total | Time at current volume |
|---|---|---|---|---|---|
| Payment step (paid ÷ reached payment) | 85 ÷ 202 = 42% (Mixpanel, undercounts) | about 200 reach payment | +10 points | about 780 arrivals | about 4 months |
| Same | 42% | about 200 | +15 points | about 350 | about 2 months |
| Person who starts a book pays within 7 days | 21.7% (all time) | about 480 people start (6,130 people; the monthly history starts in Oct 2025, about 12.5 months) | +5 points | about 2,300 people | about 5 months |
| Same | 21.7% | about 480 | +8 points | about 940 | about 2 months |
| Unfinished-book WhatsApp reminder, with a 20% holdout | 9% bought (13 of 146) | about 146 contacted | +4 points | about 2,700 contacted | well over a year |

What this means:

- **Only large effects are measurable by A/B test**, and only at the payment step or for the whole start-to-purchase rate. A change that adds 2 or 3 points will not be distinguishable from noise this year.
- **CRM holdouts cannot produce a precise answer per message.** They can still show direction when pooled over months and over several flows, and they protect against counting purchases that would have happened anyway.
- The store already splits visitors into flow arms (`localStorage.lumebook_flow_arm = "wizard"`, `book_flow_v1`), so randomisation infrastructure exists. Use it for the few tests below that can reach a decision; use the methods in section 2 for the rest.
- **Ads are the exception.** Meta credited about 45 purchases a week in late October, and the admin's decision centre (25 Oct [O-admin-oct25]) already plans one current ad against one new ad, ₪250 each, a random 50/50 split, up to 14 days, ending at about 102 Meta purchases. That is the one test with enough volume this quarter; read it on paid orders per arm as well as Meta's count, and do not split the budget across more ads during it.
- **Peeking**: deciding as soon as a difference looks good inflates false positives [S-exp]. Fix the sample size or the end date before starting, and read results once.

## 2. What to do when volume is too low

| Method | What it is | Good for | Limits |
|---|---|---|---|
| Moderated usability sessions | Watch 5 to 8 people on their own phone create a book up to the payment page, thinking aloud | Finding where people hesitate and why (price, preview, photo, phone step) | Finds problems, cannot size them; small samples miss rare problems [S-ux] |
| Non-buyer interviews | 15 to 20 minute calls with people who made a preview and did not pay (they already gave a phone number; ask consent first) | The real reason for leaving | Recall bias; people who agree to talk differ from those who do not |
| Support and WhatsApp log review | Read the last 90 days of support chats and tag them (price, delivery, likeness, payment, photo) | Cheap, real customer language | Only people who wrote in |
| Before/after with a pre-set rule | Ship the change on a set date, compare the same metric for a fixed number of weeks before and after, write the decision rule in advance | Clear defects (A1 to A3) where a test would be unethical or slow | Seasonality (Hanukkah, birthdays), ad spend changes and creator posts can cause the difference. Log every other change in the same weeks |
| Switchback | Alternate the version by week (week A, week B, week A...) | Changes that cannot be split per visitor | Weekly patterns and campaigns still interfere |
| Long-running holdout across flows | Keep 10 to 20% of eligible people out of all marketing flows for a quarter | The total extra sales CRM brings | Needs months; the left-out group must be truly random and kept clean |

## 3. Prioritised experiments and changes

Ordering: fix observed defects first (they need no test to justify), then the tests that can reach a decision at current volume, then the rest.

### X0. Show the book cover immediately on book pages (defect A1)

- **Problem and evidence:** main cover requested 8.7 s and 16.2 s after load in a returning profile; a loading mascot shows instead (audit A1). Book pages are where posts and creator links should land.
- **Hypothesis:** if the stock cover renders at once, fewer visitors leave book pages before acting.
- **Exact change:** render the catalogue cover immediately; load the personalised cover in the background with a short timeout; never block the page on it.
- **Audience and stage:** everyone landing on `/books/*`. Landing.
- **Primary metric:** share of `/books/*` landings that start the wizard (wizard step 1 viewed) in the same session.
- **Guardrails:** errors reported to Sentry from the cover components; page load time.
- **Tracking:** GA4 or Mixpanel landing page + `wizard_step_viewed` (see `measurement.md`).
- **Effort and dependencies:** developer, small. First confirm on a clean phone whether new visitors also wait.
- **Decision rule:** ship as a fix. Keep it unless the start rate falls.
- **Next action:** Yarin tests on a clean phone and sends Yossi the timings.

### X1. Total cost and arrival date before payment (defects A2, A3)

- **Problem and evidence:** ₪119 appears alone on book pages and the preview CTA; home shipping (₪30) and the 7 business days appear only on the CardCom page, where free pickup in Jerusalem is preselected so the total reads ₪119 (A25); the struck-through ₪149 equals the one-book total with shipping (audit A2, A3). About half of orders that reach payment are not paid (12 Oct readout). In Baymard's US survey, "extra costs too high" is the top abandonment reason (40%) and 12% could not see the total cost up front [S-baymard-reasons]. In a StubHub field experiment, buyers who saw fees only at checkout were almost 45% less likely to buy at that step, although total revenue rose because more people reached it; an online cinema field experiment found hiding a surcharge changed nothing overall [S-price]. So showing the fee early is unlikely to cost sales and likely to move the drop earlier, where it is cheaper (no generation spent).
- **Hypothesis:** showing the full cost and an arrival date earlier raises the share of previews that are paid, because fewer people meet a surprise on the payment page.
- **Exact change:** on the book page, the preview screen and the CTA: "₪119 + ₪30 משלוח עד הבית · או איסוף חינם בירושלים"; an estimated arrival line computed from today ("אם מאשרים היום, מגיע בערך עד [יום ותאריך]"); the shipping choice made on the preview and passed to CardCom, home delivery preselected; decide whether the ₪149 struck price stays (legal question in `crm-flows.md`). If the preview part takes longer, preselect home delivery on CardCom at once (a settings change) and note its date, since it moves the same metric.
- **Audience and stage:** everyone with a preview. Preview to payment.
- **Primary metric:** paid orders ÷ previews ready (book level, within 7 days).
- **Guardrails:** average order value; share choosing pickup; support questions about price.
- **Tracking:** `preview_ready`, `begin_checkout`, `purchase` with `transaction_id` (see `measurement.md`).
- **Effort and dependencies:** developer, small to medium (arrival date logic). Business decision on the reference price.
- **Decision rule:** before/after over 4 full weeks each side (fixed in advance), no other pricing change in that window. Keep if paid ÷ preview does not fall and price questions drop. If the store's flow-arm split can be used, an A/B test reaching about 780 payment-step arrivals detects a 10-point change.
- **Next action:** agree the exact wording with Yossi; record the start date in the publishing log.

### X2. Say what the preview includes, and show real inner pages (defects A4, A5)

- **Problem and evidence:** the free preview is the personalised cover only; inner pages are locked until after payment, while the home page promises "קוראים את הסיפור בחינם · מזמינים רק אם מתאהבים" (audit A4). Remedies for a poor likeness are stated in conflicting ways (A5). Research on self-designed products finds that people value products they helped create more, but much less when the result looks unattractive, and the IKEA effect disappears when the work is left unfinished [S-diy]. The closest evidence on reducing "what will I get" uncertainty is a set of randomised field experiments in which fit information raised conversion and order value at an online retailer [S-diy]. No study of free previews for personalised products was found.
- **Hypothesis:** setting the expectation before the photo step, and showing two or three real inner pages from consented customer books with a clear likeness promise, raises paid ÷ preview and reduces likeness complaints.
- **Exact change:** a line before the photo step ("בחינם רואים את הכריכה עם {{שם_הילד}}. את האיורים בפנים יוצרים אחרי הרכישה, ואפשר לתקן אותם עד שאתם מרוצים" only if that promise is true); on the preview, a strip of real inner pages; the likeness and fix policy in one sentence near the CTA.
- **Audience and stage:** everyone at photo step and preview.
- **Primary metric:** paid ÷ previews ready. **Guardrails:** wizard completion (photo step); likeness complaints; refunds.
- **Effort and dependencies:** content (consented customer pages; the reaction-video offer collects consented media), developer small, business decision on the promise.
- **Decision rule:** before/after, 4 weeks each side, or A/B with the flow-arm split. Keep if paid ÷ preview rises or holds while complaints fall.
- **Next action:** ask Yossi what `likenessRecoveryEnabled` does and what the current remedy is.

### X3. One illustrated inner page before payment, for people who left

- **Problem and evidence:** as X2. Generating inner illustrations for everyone costs money per started book, and only about 1 in 5 starters pays (12 Oct readout).
- **Hypothesis:** generating one inner page only for people whose preview is ready and who did not pay within 24 hours (a much smaller group) lifts their purchase rate by more than it costs.
- **Exact change:** in the preview-not-purchased flow (`crm-flows.md`, F3), the second message links to a preview where page 1 is already illustrated.
- **Audience:** previews ready, not paid after 24 hours, marketing consent not required if the message is a service reminder (legal question).
- **Primary metric:** paid within 7 days of the message ÷ people messaged, against a randomly held-out group that gets the standard reminder.
- **Guardrails:** generation cost per extra sale; opt-outs.
- **Tracking:** message sends with flow and variant IDs; orders joined by order ID.
- **Effort and dependencies:** developer medium (generate on demand). Needs the cost of one illustration from Yossi.
- **Decision rule (contribution, not purchases):** continue if (extra purchases × contribution per order) is greater than (illustrations generated × cost per illustration) after enough people for a +6-point difference (about 900 people across both groups); otherwise stop.
- **Next action:** get the generation cost and the contribution per order.

### X4. Payment-step reminder without a discount

- **Problem and evidence:** about half of orders that reach payment are not paid; the 12 Oct readout recommends a message for people who reached payment and did not pay; the current coupon ladder exists but a plain reminder for this step was not listed.
- **Hypothesis:** a service-style reminder with a help offer, about a day after leaving CardCom, recovers some orders without giving away margin. Field experiments found reminders within the first hour reduced purchases and reminders after 1 to 3 days increased them [S-timing].
- **Exact change:** flow F4 in `crm-flows.md`.
- **Audience:** reached payment, no payment within 24 hours, not a test name, not already purchased.
- **Primary metric:** paid within 72 hours ÷ eligible, treatment vs a 20% random holdout.
- **Guardrails:** STOP replies, complaints, WhatsApp quality rating.
- **Decision rule:** keep if the treated group is not worse than holdout after about 300 eligible people and complaints stay low; read the size of the effect after a full quarter.
- **Next action:** Yossi confirms whether a "reached payment" event exists server-side (CardCom notifications).

### X5. Rationalise the coupon ladder

- **Problem and evidence:** in the admin's comparison with a left-alone group, the first coupon added +5.4 sales per 100 and the third +1.6 (12 Oct readout); on 25 Oct the plain reminder added +9.5, the first coupon +7.6 and the third +2 [O-admin-oct25]. The dashboard's own notes flag that the left-alone group is probably tiny and not random. In 70 randomised discount e-mail tests, about 90% of the extra spending came from people who never redeemed the code, so the reminder did most of the work; deeper discounts lowered later buying by established customers in catalogue field tests; and a minority of buyers (5% to 19% in airline data) wait strategically for deals [S-wait].
- **Hypothesis:** dropping the third coupon, and making the first reminder a no-discount help message, keeps most recovered sales and raises contribution per recovered sale.
- **Exact change:** reminder 1 without coupon; coupon only at step 2 for people still eligible; no third coupon.
- **Primary metric:** contribution per eligible person (revenue minus discount, print, shipping and message costs), not purchases.
- **Guardrails:** paid ÷ eligible; complaints.
- **Decision rule:** compare a quarter with the new ladder to the holdout. Keep the cheaper ladder unless contribution per eligible person is lower.
- **Next action:** get the ladder's current timing and coupon values from the admin.

### X6. Order-by dates and earlier reminders (A7, B5, B6)

- **Problem and evidence:** birthday reminders go a week before the date, while printed home delivery takes up to 7 business days after approval (A7). Hanukkah starts 4 Dec 2026; the order deadline in `shared/facts.json` (22 Nov) is unconfirmed.
- **Hypothesis:** dated order-by messages and earlier reminders increase on-time printed orders and reduce late, digital-only gifts.
- **Exact change:** first reminder about 21 days before (hypothesis), a "last day for a printed book" reminder, and the digital copy as the late answer; a dated Hanukkah line on book pages from 10 Nov.
- **Primary metric:** printed orders paid ÷ reminders sent; share of reminder-driven orders delivered before the date.
- **Guardrails:** opt-outs from reminders.
- **Decision rule:** compare reminder cohorts by send timing over the season. The store's reminder service started on 4 Oct 2026, so there is no baseline yet; record from day one.
- **Next action:** business confirms the Hanukkah order-by date and print lead time.

### X7. Deep links from social to the book in the post (B1)

- **Problem and evidence:** the bio link goes to the home page; the visitor must choose among three creation modes and about 66 books (audit steps 4 and 5).
- **Hypothesis:** a link to the matching book page (or the wizard with the book preselected) raises books started per click.
- **Exact change:** every post, story and creator link uses the book URL with UTMs (`measurement.md`); ask Yossi whether the wizard accepts a `book` parameter.
- **Primary metric:** books started ÷ sessions, by link type (home vs book).
- **Decision rule:** sequential by post; judge after 20 posts of each type. Directional only.
- **Effort:** none for Yarin beyond link discipline.

### X8. Gift giver photo request (B2)

- **Problem and evidence:** ad delivery skews to women 55 and over, read as grandmothers but not verified (12 Oct readout); on 25 Oct Meta credited 43 of the 102 purchases in its age table to women 45 and over, women 55 to 64 the cheapest at ₪81 each [O-admin-oct25], still Meta's attribution and not buyers. A gift giver may not have a good photo. **First step, now:** one optional question on the thank-you page, "למי הספר?" (לילד שלי, לנכד או לנכדה, לאחיין או לאחיינית, מתנה לחברים), for four weeks, read against payment per preview by answer (journey demo step 8, note 5). The group-order flow already sends parents an upload link.
- **Hypothesis:** letting a gift buyer send the parent an upload link increases gift orders.
- **Step 1 (no development):** ask "למי הספר?" in the Instagram DM router (`crm-flows.md`, F1) and in the post-purchase message, for four weeks, to size the gift-giver share.
- **Decision rule:** build the request link only if gift givers are a meaningful share (business sets the bar before reading the answers).

### X9. Free greeting card first vs straight to the book, in the DM funnel

- **Problem and evidence:** a free Hanukkah greeting card or coloring booklet is live at `/holiday-cards`, followed by a ₪99 book code (audit step 12), but nothing shows whether it sells books. A free offer attracts people for whom the price is zero, not necessarily buyers [S-zero]; generation and messages cost money.
- **Hypothesis to test, not assume:** for cold audiences around Hanukkah, a free card first produces more paid books per 100 DM conversations within 30 days than a direct book link.
- **Exact change:** in ManyChat, randomly assign people who comment or DM the keyword to (a) direct book link or (b) free card, then a book link after delivery. Use ManyChat's randomiser step if available (see `sources.md`), or alternate by week.
- **Primary metric:** paid books within 30 days per 100 DM conversations, joined by UTM `utm_content` per arm.
- **Guardrails:** cost per paid book including generation; opt-outs; share of card requesters who start a book.
- **Decision rule:** keep (b) only if paid books per 100 are higher **and** cost per paid book is lower than (a). Otherwise use the card only as a post-purchase gift.
- **Dependencies:** trackers are blocked on `/holiday-cards`, so the arm must be read from the ₪99 code redemptions and from orders whose phone matches a card request (in the store, not in analytics); consent design per `crm-flows.md`.

### X10. Second book offer framed for siblings and family

- **Problem and evidence:** the post-purchase offer is the strongest recorded message (48 purchases after 209 sends in 90 days, $0.16 message cost per purchase, 12 Oct; 62 purchases within 24 hours of 234 received, $0.15, 25 Oct [O-admin-oct25]; not shown to be caused by the message) and buyers average 1.41 books.
- **Hypothesis:** a sibling and cousin framing ("עוד ילד או ילדה בבית?") raises second-book take-up versus the current wording.
- **Primary metric:** second book within the ₪79 window ÷ first purchases, by variant, with a holdout that gets no offer.
- **Decision rule:** sizeable effects only (volume is about 70 sends a month); run for a quarter.

### X11. Reminder timing for unfinished books and previews

- **Problem and evidence:** the timing of the store's current reminders is not visible to Yarin. Field experiments (other stores) found that cart reminders sent 30 to 60 minutes after abandonment reduced purchases versus no message, while 1 to 3 days later increased them, by e-mail, app and SMS [S-timing].
- **Hypothesis:** moving any reminder that now goes out within an hour to about 24 hours raises paid ÷ eligible.
- **Primary metric:** paid within 7 days ÷ eligible, by timing arm, against the holdout.
- **Decision rule:** if the current timing is already a day or more, skip the test. Otherwise alternate timing by week for 8 weeks (switchback), because monthly volume (about 150 people in the unfinished-book flow) cannot support a per-person split with a holdout.
- **Next action:** Yossi reports the current send delays.

## 4. What not to test now

- A progress bar or step counter as a lift: a meta-analysis of 32 randomised web-survey experiments found constant progress indicators did not reduce drop-off [S-progress]. Fix the 4-to-5 step counter (audit A10) because it is inaccurate, not because it will sell books.

- Button colours, headline wording on the home page and other small copy changes: the volume cannot detect their effects.
- New discount levels: they change margin and teach waiting [S-wait] before the basics (X0 to X2) are fixed.
- A new CRM or messaging tool: the store already sends WhatsApp and SMS (Twilio) with consent records and a holdout (see `roadmap.md`).
