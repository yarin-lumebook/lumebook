# Customer lifecycle (CRM) flows

Internal, holds sales figures. Part of `research/cro-crm/` (start at `report.md`). CRM here means the customer lifecycle: prospective buyers and customers of the store. The creator outreach map (`creators/creator-research/`) is a separate workstream; it connects only through creator links and the ambassador ledger.

Nothing here has been switched on. The store's developer owns the message system (WhatsApp and SMS through Twilio, per the privacy policy); every flow below is a specification to agree with him, not an automation to build elsewhere.

All timings are **initial hypotheses** unless a LumeBook number is quoted. Hebrew drafts use `{{placeholders}}` for anything not verified (prices, dates, policies). They were written in the calibrated LumeBook Hebrew voice (`.claude/skills/lumebook-hebrew-voice`) and pass its lint, apart from the expected warning for the Latin keyword STOP.

## 1. What already exists (do not rebuild)

| Piece | Evidence | Notes |
|---|---|---|
| Verified phone and required e-mail at book creation | Code: phone one-time code (WhatsApp first, SMS fallback) and a required e-mail before any preview | The phone is already the customer's identity and the main channel; for Israeli numbers marketing consent is bundled into the required box (audit A6) |
| Tokenised resume links | Code: `/support/resume`, `/support/draft`, `/support/address`, `/support/verify`, with trackers blocked on those routes | Ready-made links for F2 to F5 |
| WhatsApp and SMS sending | Privacy policy: Twilio for WhatsApp and SMS | Templates and timings not visible to Yarin |
| Unfinished-book reminder, three coupons, post-purchase offer, birthday reminder, broadcasts | Admin Marketing and Analytics tabs (`docs/lumebook-sales-data-decisions-2026-10-12.md`) | 90-day message fees about $96 in total |
| A left-alone comparison group | Admin Marketing tab | The Analytics tab says there is no random control group; the dashboard's own note says the group is probably tiny |
| Marketing preferences | `/marketing-preferences`: one switch for WhatsApp, SMS and e-mail; "הודעות שירות ועדכוני הזמנה ימשיכו להישלח" | Per-channel choice missing (audit A18) |
| STOP keyword | Privacy policy and terms | |
| Birthday and occasion reminders | `/my-reminders`, since 4 Oct 2026: name, day and month; WhatsApp or SMS a week before and on the day | Timing too late for print (audit A7) |
| Customer referral program | `/recommend`: up to 25% of the printed book, split between reward (site credit, or half in cash by Bit or PayBox) and friend discount; ready text with a disclosure line | No flow invites customers to it |
| Ambassador program (creators) | `/ambassadors`; 7-day link credit | Creator workstream |
| Reaction video request | QR code in the printed book opens WhatsApp with consent text; a free printed book if the video is used (`/reaction-offer`, until 31.12.2026) | The UGC flow exists; volume unknown |
| QR offer at ₪99 | `/offers/g10-99`, 22.08 to 31.10.2026, 7 days, same browser | Ends next week |
| Free Hanukkah greeting card or coloring booklet | Live at `/holiday-cards` (not in the sitemap), followed by a ₪99 book code; trackers blocked on that route | Lead magnet already built; its effect on book sales is unknown |
| Birthday offer and sibling offer | Code: a time-limited ₪20 birthday discount (`/api/birthday-offer/context`) and a sibling offer card | Terms and triggers to confirm with Yossi |
| Order status | `/my-books` lists books with status ("בעריכה") and order number; code shows an `/orders` page with shipped, at pickup, tracking number and expected date | Not seen on screen |

## 2. Customer states

The states follow the store's actual order of steps (`audit.md`). A person can be in several states at once (one paid book, one draft).

| State | Entered when | Identifiable? | Main flow |
|---|---|---|---|
| S0 Visitor | lands on the site | cookie only, consent-dependent | none (site CRO) |
| S1 Instagram contact | comments or DMs a keyword, ManyChat subscriber | Instagram-scoped ID | F1 |
| S2 Wizard started | step 1 filled | no (draft in `sessionStorage`) | none |
| S3 Identified, book started | phone verified, book record exists | yes | F2 |
| S4 Preview ready | personalised cover shown | yes | F3 |
| S5 Reached payment | redirected to CardCom | yes | F4 |
| S6 Payment failed | CardCom decline or error | yes | F5 |
| S7 Paid, not approved | payment confirmed, book not approved for print | yes | F6 |
| S8 In print | approved | yes | F7 |
| S9 Shipped | handed to courier or ready for pickup | yes | F7 |
| S10 Delivered | delivered or picked up (or estimated) | yes | F8, F9 |
| S11 Repeat buyer | second paid order | yes | F10, F12 |
| S12 Reminder subscriber | saved a reminder | yes | F11 |
| S13 Lapsed | no order, preview or reply for 9 months (hypothesis) | yes | F13 |
| S14 Marketing opted out | STOP or preference off | yes | service messages only |
| Group-order parent | uploaded through a kindergarten link | yes | excluded from B2C marketing unless they opt in themselves |

## 3. Rules that apply to every flow

**Priority when flows overlap** (higher wins; a lower flow pauses while a higher one is active):
1. Service and transactional: F5 payment failed, F6 approval, F7 order and delivery, OTP codes.
2. F4 reached payment.
3. F3 preview ready.
4. F2 unfinished book.
5. F8 help after delivery, F9 review and video.
6. F10 second book.
7. F11 reminders the customer asked for.
8. F12 referral invitation.
9. F13 seasonal and win-back.

**Frequency caps (hypotheses, set in the message system):**
- At most one marketing message per person per day, and at most 2 per rolling 7 days and 4 per 30 days, across all flows. Service messages do not count but are never bundled with offers.
- No marketing between 21:00 and 08:00, on Shabbat or on Jewish holidays (Friday from 14:00 to Saturday night). Service messages that the customer is waiting for (OTP, payment failure) may go any time.

**Deduplication:** one active flow instance per person per flow; a person with two drafts gets one message about the newest, naming both only if both are ready.

**Suppression (never send marketing):** STOP or preference off; open support conversation in the last 48 hours; complaint or refund request in the last 30 days; test names or team phones; group-order parents without their own opt-in; anyone whose WhatsApp marketing message failed delivery twice in a row (switch to SMS or e-mail only with consent for that channel).

**Exit conditions:** purchase exits F2, F3, F4 and F5 immediately (checked at send time, not at schedule time); approval exits F6; a reply exits automation and opens a human conversation.

**Human handoff:** any free-text reply goes to the support inbox; replies with "לא דומה", "בעיה", "החזר", "ביטול", "לא הגיע" are tagged urgent. Response hours are stated in the first automated reply (for example "עונים בימים א׳ עד ה׳ בין {{שעות}}"; set real hours).

**Marketing labelling:** every message classed as marketing (F2, F3, F4, F10, F11, F12, F13 and F0's second message, see section 7) starts with the word "פרסומת", names לומבוק, and ends with "להפסקת הודעות שיווקיות השיבו STOP". The drafts below show this in full for F10 and F13; the message system should add the same first and last line to the others. Service messages (F5 to F8) carry no offer, so they stay service.

**Holdout:** each flow keeps a random 10 to 20% of eligible people unmessaged for a quarter (`measurement.md`, section 8). Service flows (F5 to F7) have no holdout.

**Timing rule for recovery messages:** nothing within the first hour after someone leaves; the first reminder about a day later. Early messages annoyed people and reduced purchases in field experiments; later ones helped [S-timing].

**Delivery failures:** WhatsApp may refuse to deliver marketing templates to a person who has had too many from businesses recently (error 131049, per Meta's per-user limits [W-caps]). Log these failures and leave those people out of the flow's results; do not retry within 24 hours.

## 4. Channel choice: phone-first, with e-mail as the second channel

Yarin's preference for phone-based capture is already how the store works: the phone is verified before the preview, and WhatsApp is the reminder channel. The evidence supports keeping it for service and recovery messages, with three changes:

1. **Consent must be separate.** The terms treat giving a phone number as consent to marketing; the privacy policy says marketing needs a separate explicit choice (audit A6). Keep the phone and OTP for the book and service messages, and ask for marketing consent with its own unticked choice at the preview or after payment.
2. **Use the e-mail the store already collects as the second channel.** The phone step already requires an e-mail ("אימייל לעותק הדיגיטלי"), and CardCom asks for an invoice e-mail. Use it for order confirmations and long content (the full order summary, the approval link, the digital copy), and as a fallback when WhatsApp marketing delivery fails or Meta changes its rules or prices. Separate marketing consent applies. Consider making the e-mail optional at the phone step and asking for it at payment instead (audit B7), since two required contact fields before any preview is a lot on a phone.
3. **ManyChat stays at the Instagram edge.** It is good at turning a comment or DM into a link with UTMs and a first question ("למי הספר?"). Do not copy phone numbers from ManyChat into the store's lists; let the store's own OTP identify the person, so consent and identity stay in one system.

Costs, delivery rules and legal points per channel are in section 7. In short: WhatsApp marketing messages cost about $0.035 each in Israel and utility messages about $0.005 (third-party tables checked against Meta's card); SMS through Twilio costs about $0.26 per 70-character Hebrew segment; e-mail is close to free at this size.

## 5. Flows

Each flow lists trigger, eligibility, timing, channel, sequence, personalisation with fallback, exit, metric and measurement. "Exists" means the store already sends something similar.

### F1. Instagram DM router (ManyChat): new

- **Trigger:** a comment or DM with a post's keyword, or a story reply, on posts that use one (carousels since 24 Oct use save-and-share instead; this is for creator and product posts).
- **Prerequisite:** Instagram's messaging rules (section 7); the keyword is set per post.
- **Eligibility and exclusions:** anyone who wrote; skip accounts that already got this post's link.
- **Timing and channel:** immediately, Instagram DM.
- **Sequence:** (1) one question with quick replies; (2) the link to the book shown in the post, tagged with UTMs; (3) no follow-up unless they reply.
- **Personalisation and fallback:** the book is set per post; fallback is the catalogue page.
- **Exit:** link clicked or 24 hours.
- **Metric:** books started per 100 DM conversations (UTM `utm_content=dm-<post>`), and the gift-giver share from the question (X8).
- **Measurement:** directional, by post (`experiments.md`, X7).

Hebrew draft:

```text
היי 👋
למי הספר?
{{כפתור_לילד_שלי}}
{{כפתור_מתנה_לנכד_או_לנכדה}}
{{כפתור_מתנה_למישהו_אחר}}
```

```text
מעולה
זה הספר מהפוסט
בוחרים שם ותמונה ורואים את הכריכה בחינם
{{קישור_ספר_עם_UTM}}
ספר מודפס ב{{מחיר_ספר}} ועוד {{מחיר_משלוח}} משלוח עד הבית
```

### F0. Free greeting card or coloring booklet, then the book: test only

- **Status:** live at `/holiday-cards` since at least 24 Oct 2026, not linked from the sitemap or the store's menus seen. It ends with a ₪99 book code ("ספר במחיר מוזל, 99 שקלים בלבד במקום 149"). Do not push it as the default social CTA until X9 (`experiments.md`) shows it sells books; meanwhile measure it through the code's redemptions, since trackers are blocked on that route.
- **Trigger:** a request on the gift page (phone and optional e-mail; the policy says no OTP and no automatic messages from that page).
- **Eligibility:** parents and guardians; the policy keeps the gift's data up to a year.
- **Sequence (if X9 wins):** (1) the card, immediately on the page and by e-mail if given; (2) only with marketing consent, one message after 2 days linking to the matching book; (3) stop.
- **Exit:** a book started, or after message 2.
- **Metric:** paid books within 30 days per 100 requests; cost per paid book including generation.
- **Risk:** a free offer draws people who value it because it is free, not because they will buy (zero-price effect, [S-zero]); customers acquired through a free trial of a TV service were worth 59% less over their lifetime, though more responsive to follow-up messages [S-zero]. It also spends generation money and adds a step before the book. Judge it on paid books, never on requests.

```text
הכרטיס של {{שם_הילד}} מוכן 🎉
אפשר להוריד ולשלוח מכאן
{{קישור_כרטיס}}
רוצים {{שהוא_שהיא}} {{יהיה_תהיה}} גם {{הגיבור_הגיבורה}} של ספר שלם?
{{קישור_ספר}}
```

### F2. Unfinished book: exists, adjust

- **Trigger:** phone verified and book record created, but no preview ready (generation failed or stuck, or the buyer left the editor before it finished) after a day. Since the code creates the order only after the photo and phone steps, this flow is about generation problems and early exits, not missing photos.
- **Eligibility:** not a test; no newer book from the same person in preview or later state.
- **Consent:** a reminder meant to get the book bought fits the statutory definition of advertising, and Meta classes it as marketing (section 7). Until a lawyer says otherwise, send it only to people with separate marketing consent, with the marketing first and last lines. If generation failed on LumeBook's side, a plain service message saying the preview is ready is different and needs no offer.
- **Timing and channel:** WhatsApp about 24 hours after the last activity (hypothesis, guided by [S-timing]); if generation failed on LumeBook's side, a service message as soon as it is fixed instead. One more at day 3 only to offer help with the photo.
- **Personalisation and fallback:** child's first name (fallback "הספר שלכם"); what is missing (`preview not finished`, `new photo needed`), fallback "כמה פרטים". The reminder should open the finished preview where one exists, not the start of the wizard: the IKEA-effect studies found that value attaches to completed work [S-diy].
- **Exit:** preview ready, purchase, STOP, reply.
- **Metric:** previews ready within 7 days ÷ eligible, vs holdout. Today: 13 of 146 contacted bought, +4.1 extra sales per 100 against the left-alone group (12 Oct readout).

```text
היי
הספר של {{שם_הילד}} מחכה לכם
נשאר רק {{מה_חסר}}
ממשיכים מאותה נקודה כאן
{{קישור_המשך}}
```

### F3. Preview ready, not purchased: exists partly (coupon ladder), redesign

- **Trigger:** `preview_ready`, no `begin_checkout` within 24 hours.
- **Eligibility:** as F2; not already in F4.
- **Timing and channel:** WhatsApp at 24 hours (message 1, no discount); day 3 (message 2, proof: a real customer video or printed-book photo, consented); day 6 (message 3, optional: either the one illustrated inner page of X3 or a single coupon, never both, and never a third coupon).
- **Personalisation:** child's first name, book title (fallback "הספר"), total cost and pickup options from live settings (never hard-coded), deadline line if a reminder date or a holiday is within 21 days.
- **Exit:** checkout, purchase, STOP, reply, 7 days.
- **Metric:** paid within 7 days of message 1 ÷ eligible, vs holdout; contribution per eligible person (X5).

```text
היי
הכריכה של {{שם_הילד}} מוכנה ושמורה אצלכם
אפשר לחזור אליה מתי שנוח
{{קישור_תצוגה}}
```

```text
מה מקבלים
ספר מודפס ב{{מחיר_ספר}} ועוד {{מחיר_משלוח}} משלוח עד הבית
או איסוף בחינם מ{{נקודת_איסוף}}
ועותק דיגיטלי במייל תוך דקות
שאלה? עונים לכם כאן
```

```text
היי
רצינו להראות לכם איך ספר נראה כשהוא מגיע הביתה
{{קישור_סרטון_לקוח}}
הכריכה של {{שם_הילד}} עדיין שמורה כאן
{{קישור_תצוגה}}
```

### F4. Reached payment, not paid: new

- **Trigger:** redirected to CardCom, no payment confirmation within 60 minutes.
- **Eligibility:** not a test; no payment failure event (that is F5); not purchased on another order since.
- **Timing and channel:** WhatsApp about 24 hours after leaving CardCom, one message only; e-mail the next day if consent allows (the e-mail is collected at the phone step). Not within the first hour: in two field experiments (40,500 customers by e-mail and app, 23,900 by SMS) cart reminders sent 30 minutes to 1 hour after abandonment made people less likely to buy than no message, while reminders 1 to 3 days later helped [S-timing]. Those were other stores; test 24 hours against LumeBook's current timing with a holdout.
- **Personalisation:** child's first name, a resume link to the same payment page.
- **Exit:** purchase, reply, 72 hours.
- **Metric:** paid within 72 hours ÷ eligible, vs 20% holdout (X4).

```text
היי
ההזמנה של הספר של {{שם_הילד}} לא הושלמה
אם משהו בתשלום לא עבד או לא היה ברור
כתבו לנו כאן ונעזור
להמשך התשלום
{{קישור_תשלום}}
```

### F5. Payment failed: new, service

- **Trigger:** CardCom returns a decline or technical error.
- **Timing and channel:** immediately on the page (clear Hebrew error and a retry button), then WhatsApp after 10 minutes if no successful retry.
- **Personalisation:** reason only if CardCom gives a customer-safe one; fallback none.
- **Exit:** successful payment, reply.
- **Metric:** recovered payments ÷ failed payments. No holdout (service).

```text
היי
התשלום על הספר של {{שם_הילד}} לא עבר
ההזמנה שמורה ואפשר לנסות שוב כאן
{{קישור_תשלום}}
או לכתוב לנו ונעזור
```

### F6. Paid, not approved for print: new, service

- **Why:** after payment the buyer still edits and approves the book; printing starts only then (tutorial "בדיקה ואישור הספר להדפסה"). Every day of delay pushes delivery past birthdays and Hanukkah.
- **Trigger:** paid printed order, not approved after 24 hours; again at 72 hours; a deadline message when an event date is known (reminder date, Hanukkah) and the last safe approval day is within 3 days.
- **Timing and channel:** WhatsApp, then e-mail with the same link.
- **Personalisation:** child's first name, approval link, delivery days from live settings, event name and last approval date (fallback: no deadline line).
- **Exit:** approved; reply.
- **Metric:** median days from payment to approval; share of orders approved within 48 hours; on-time delivery for dated events.

```text
היי
הספר של {{שם_הילד}} שולם ומחכה רק לאישור שלכם
אחרי האישור הוא יוצא להדפסה
ומגיע עד {{ימי_אספקה}} ימי עסקים
לבדיקה ואישור
{{קישור_עורך}}
```

```text
רוצים שהספר יגיע לפני {{שם_האירוע}}?
כדאי לאשר אותו עד {{תאריך_אישור}}
{{קישור_עורך}}
```

### F7. Order and delivery updates: confirm what exists

- **Messages:** payment received (with what happens next), approved and sent to print (with the estimated arrival), shipped or ready for pickup (pickup: the Bookpod instructions in the FAQ), delivered if the courier reports it.
- **Channel:** e-mail for the full summary; WhatsApp for the short status.
- **Metric:** "where is my book" support questions per 100 orders. The store's code already has an `/orders` status page (tracking number, expected date); every F7 message should link to it.

### F8. Help after delivery: new, service

- **Trigger:** 2 days after delivery, or 10 business days after approval if delivery is not reported (hypothesis).
- **Sequence:** one message; a reply opens a human conversation.
- **Exit:** reply or 7 days. A complaint suppresses F9, F10 and F12 for 30 days.
- **Metric:** complaint rate; time to resolve.

```text
היי
הספר של {{שם_הילד}} הגיע?
אם משהו לא תקין בהדפסה או במשלוח
כתבו לנו כאן ונסדר
```

### F9. Reaction video and review: exists partly (QR in the book), add one reminder

- **Trigger:** 5 days after F8 with no complaint.
- **Sequence:** (1) reaction video reminder pointing to the QR in the book (the existing offer and its consent text); (2) a week later, only if no video, a review request with a direct Google review link. No reward for reviews (only the existing video offer, which is a separate consented promotion).
- **Personalisation:** child's first name; gendered verb from the gender chosen in the wizard (`הגיב` or `הגיבה`), fallback "איך היה עם הספר?".
- **Metric:** videos received per 100 delivered orders; reviews per 100 delivered orders.
- **Why it matters:** in Spiegel Research Center's retailer data, the first five reviews were associated with a much higher purchase likelihood, more so for higher-priced gifts, and prompted verified-buyer reviews averaged 4.34 stars against 3.89 for unprompted ones [S-reviews]; 72% of Israeli online buyers in a Wolt and Kantar survey said they check reviews before every purchase [S-israel]. Both are observational or commissioned; the direction is consistent.

```text
איך {{שם_הילד}} {{הגיב_הגיבה}} לספר?
צילמתם את הרגע?
סרקו את הקוד שבסוף הספר ושלחו לנו
אם נפרסם תקבלו ספר מודפס נוסף במתנה
{{קישור_תנאים}}
```

```text
יש לכם דקה לכתוב ביקורת בגוגל?
זה עוזר להורים אחרים להחליט
{{קישור_ביקורת}}
```

### F10. Second book, sibling or family copy: exists, reframe

- **Trigger:** payment confirmed; the ₪79 window is 24 hours (`/api/config/pricing`: `repeatBookPriceMinor 7900`, `windowHours 24`).
- **Timing and channel:** on the thank-you page, then WhatsApp at 2 hours (hypothesis) if no second book. Marketing consent required.
- **Personalisation:** end time of the window, price from live settings.
- **Exit:** second book; window closed.
- **Metric:** second books ÷ first purchases, vs holdout (X10). Today the strongest recorded message: 48 purchases after 209 sends in 90 days (12 Oct readout; not shown to be caused by the message).

```text
פרסומת
עוד ילד או ילדה בבית?
עד {{שעת_סיום}} כל ספר נוסף ב{{מחיר_ספר_נוסף}}
והוא מצטרף לאותו משלוח
{{קישור}}
להפסקת הודעות שיווקיות השיבו STOP
```

### F11. Occasion reminders the customer asked for: exists, change timing

- **Trigger:** a saved reminder (`/my-reminders`).
- **Timing (hypothesis):** about 21 days before; on the last day a printed book can still arrive (from live print and delivery times); the day itself, offering the digital copy. Today it is a week before and the day itself (audit A7).
- **Consent:** the store treats saving a reminder as the request to receive it (privacy policy). Meta classes birthday messages as marketing, and a reminder that links to a book likely counts as advertising (section 7); the lawyer's answer decides whether the reminder needs the marketing first and last lines.
- **Metric:** printed orders paid ÷ reminders sent, by timing; on-time delivery.

```text
עוד שלושה שבועות יום ההולדת של {{שם}} 🎈
ספר מודפס מגיע עד {{ימי_אספקה}} ימי עסקים מרגע האישור
אם מזמינים השבוע הוא מגיע בזמן
{{קישור}}
```

```text
יום ההולדת של {{שם}} בעוד {{מספר_ימים}} ימים
זה היום האחרון להזמין ספר מודפס שיגיע בזמן
אחרי היום עדיין אפשר עותק דיגיטלי שמגיע תוך דקות
{{קישור}}
```

Also offer the reminder at the right moment: on the thank-you page ("רוצים שנזכיר לכם לפני יום ההולדת הבא?"), since a birthday book buyer has just shown the occasion matters.

### F12. Referral invitation: program exists, flow new

- **Trigger:** a positive reply to F8 or a video sent in F9; never before delivery.
- **Sequence:** one message with the `/recommend` link; the program's own disclosure line ("רק שתדעו, יש לי תגמול על רכישה דרך הקישור שלי") stays in the ready text.
- **Metric:** referrers enrolled per 100 delivered orders; referred paid orders; cost per referred order (reward plus discount) against the ₪61 to ₪113 ad cost per sale. Referred bank customers were worth at least 16% more than similar non-referred ones [S-referral]; for a gift book the value would come from cheaper acquisition, not retention. A field experiment found moderate rewards beat both small and large ones once new-customer profitability is counted, and another found an uncertain reward for the friend attracted fewer, less active friends [S-referral], so keep the friend's discount fixed and simple, as the program already does.

```text
שמחים שהספר אהוב אצלכם
אם תרצו לשלוח אותו לחברים
בתוכנית הממליצים החברים מקבלים הנחה
ואתם צוברים קרדיט לספרים
{{קישור_ממליצים}}
```

### F13. Seasonal and win-back: replaces whole-list broadcasts

- **Why:** the back-to-school broadcast went to 813 people and one purchase followed (12 Oct readout).
- **Trigger:** a seasonal window (Hanukkah from about 3 weeks before the first night) for people who previewed or bought in the last 12 months and gave marketing consent; or 9 months without activity (hypothesis).
- **Sequence:** one message per season; a second only to people who clicked.
- **Personalisation:** child's first name and gender from the last book; book matched to the season; order-by date from live settings.
- **Metric:** paid orders ÷ messaged, vs holdout; opt-out rate per send.

```text
פרסומת
כאן לומבוק 🕎
חנוכה מתקרב
ספר חנוכה שבו {{שם_הילד}} {{הגיבור_הגיבורה}}
הזמנה עד {{תאריך_אחרון}} מגיעה לפני הנר הראשון
{{קישור}}
להפסקת הודעות שיווקיות השיבו STOP
```

## 6. Discounts: when they help and when they hurt

- **Likely to raise contribution:** the ₪79 second book in the 24-hour window (no new acquisition cost, shared shipping, illustrations partly reusable); a time-limited seasonal price with a real end date.
- **Likely to lower it:** a coupon in the first recovery message (it goes to people who would have bought anyway), a fixed three-coupon ladder, and permanent "limited time" prices. In 70 randomised e-mail tests at a ticketing site, about 90% of the extra spending from discount e-mails came from people who never used the code, so most of the effect was the reminder itself [S-wait]. Deeper discounts raised later buying by first-time customers but lowered it for established customers in three catalogue field experiments [S-wait], so a coupon to past buyers can pull purchases forward and raise deal-seeking. The admin's own comparison shows the third coupon adding much less than the first (+1.6 vs +5.4 extra sales per 100, a probably tiny comparison group).
- **Rule of thumb for LumeBook:** non-price help first (clarity, a deadline, free pickup, help with the photo); at most one coupon per person per 90 days, never in the first message; judge every discount by contribution per eligible person against a holdout, not by purchases.

## 7. Channel rules, costs and Israeli legal points

**This section summarises official documentation, law texts and law-firm commentary read on 24 Oct 2026. It is not legal advice;** the open questions at the end are for an Israeli lawyer. Sources are listed in `sources.md`, sections 6 and 7.

### 7.1 WhatsApp (Meta)

- **Pricing is per delivered message** since 1 July 2025, by template category: marketing, utility, authentication, plus free-form service replies inside a 24-hour customer service window [W-pricing].
- **Since 1 October 2026** utility templates sent inside an open service window are charged again, and service replies are free only for the first 1,000 a month per number [W-pricing]. The assumption that order updates inside the window are free no longer holds.
- **Israel rates (USD, effective 1 Oct 2026):** marketing about $0.0353, utility and authentication about $0.0053 per delivered message. These come from two third-party tables that say they were checked against Meta's rate card; Meta's own rate-card file could not be opened, so confirm in WhatsApp Manager or with Twilio before budgeting [W-rates]. The store's own estimate ($0.036 per message, 12 Oct readout) matches the marketing rate.
- **Categories:** Meta lists abandoned-cart reminders, discount or coupon offers and birthday messages as **marketing**; order confirmations and shipping updates with order details as **utility**; mixed content defaults to marketing, and Meta re-categorises templates [W-categories]. In this plan, F2, F3, F4, F10, F11, F12, F13 and F0's second message are marketing; F5, F6, F7 and F8 are utility if they contain no offer; F9's review request is utility only when tied to a specific order, and its reaction-video offer is marketing.
- **Opt-in:** Meta requires a clear opt-in that names the business, and prompt escalation to a human from any automation; opt-outs must be respected on or off WhatsApp [W-optin]. Israeli law is stricter (7.4).
- **Per-user marketing limits:** WhatsApp caps how many marketing templates one person receives from businesses, adapting to that person's engagement; blocked sends fail with error 131049 and are not charged. Israel is not exempt [W-caps]. A coupon ladder sent in quick succession may silently lose its later steps.
- **Messaging limits and quality:** business-initiated messages are limited per portfolio (250, then 2,000, 10,000 unique people per rolling 24 hours); blocks and "not interested" feedback lower template quality and can pause templates [W-limits]. A whole-list broadcast risks both.
- **Marketing Messages API:** Meta's separate API for marketing templates is generally available since 19 Nov 2025. Accounts created from 13 Apr 2027 cannot send marketing through the Cloud API, and from 13 Oct 2027 marketing sends through the Cloud API fail; utility and service stay on the Cloud API [W-mm]. The store sends through Twilio, so Yossi should ask Twilio how and when it migrates.
- **Click-to-WhatsApp ads** open a free entry point window of up to 7 days in which Meta does not charge for messages [W-pricing]. Relevant only if paid ads are used again.

### 7.2 Instagram DMs (Meta, through ManyChat)

- An automated comment-to-DM gets **one private reply per comment, within 7 days**; further messages only after the person replies, within 24 hours of that reply [I-private]. Quick-reply buttons (F1) are how the conversation continues.
- Automated promotional messages are allowed only inside the 24-hour window (up to 7 days after a click-to-Direct ad); a human agent tag allows manual replies for 7 days [I-window]. Recurring "marketing messages" on Messenger were deprecated on 10 Feb 2026, and no current Instagram equivalent was found [I-window]. Instagram is an entry point, not a re-engagement channel.
- Rate limit: 750 private replies per hour per account [I-limits]. Not a constraint at LumeBook's volume.

### 7.3 SMS and e-mail

- **SMS through Twilio to Israel:** $0.2575 per segment; Hebrew uses UCS-2, so 70 characters per segment (67 when concatenated), about $0.77 for a 140-character message; a branded sender ID needs domestic registration (about a week) [SMS-twilio]. Local providers publish far lower unit prices (for example 019 SMS ₪20 + VAT per 1,000 verification messages; ActiveTrail about ₪0.111 per message) [SMS-local]. Use SMS only as a fallback for people without WhatsApp, with the same consent and labelling.
- **E-mail:** Gmail and Yahoo require SPF, DKIM and DMARC for bulk senders, a one-click unsubscribe (RFC 8058) on marketing mail, and unsubscribes honoured within about two days; Microsoft rejects non-compliant high-volume mail [E-auth]. Set up SPF, DKIM and DMARC on lumebook.com regardless of volume. The store already has a one-click unsubscribe endpoint (code).

### 7.4 Israeli law: what it means for these flows

- **Spam law (Communications Law, section 30A):** an advertising message ("דבר פרסומת", a commercial message meant to encourage buying) by e-mail, SMS, automatic dialling or electronic message needs the recipient's explicit prior consent in writing (electronic counts). Each must start with the word "פרסומת" (in the e-mail subject), name the advertiser and give a simple way to refuse. Courts may award up to ₪1,000 per message without proof of damage [L-spam]. The Supreme Court held in 2014 that an unsubscribe link does not reduce the compensation [L-spam-court].
- **Existing-customer exception (30A(c)):** consent is not needed where the person gave their details during a purchase **or during negotiation for a purchase**, was told the details would be used for advertising, was offered a chance to refuse and did not, and the advertising is for similar products [L-spam]. A parent who created a book may fall in "negotiation for a purchase", but only if the phone step told them about offers and let them refuse. Today the Israeli phone step bundles marketing into the required box (audit A6), and a magistrates' court certification decision (as reported by a vendor blog, not opened) held that a clause buried in general terms is not explicit consent [L-spam-court].
- **WhatsApp:** no ruling applying 30A to WhatsApp was found, but a WhatsApp message travels over the internet and fits the statute's definition of an electronic message; Israeli law-firm commentary advises treating it like SMS and e-mail [L-spam-wa]. **Plan as if marketing WhatsApp templates are covered.**
- **Which messages are advertising:** order, production and shipping updates are service. A reminder whose purpose is to get the unfinished book bought fits the statutory definition of advertising, as do coupons, the second-book offer, birthday reminders that link to a book, and broadcasts (assessment for the lawyer, not a ruling).
- **What to do until a lawyer answers:** (1) show the separate unticked marketing box to Israeli numbers and store consent text, version, time and source per person; (2) send F2, F3, F4, F10 to F13 only to people with that consent; (3) start every marketing template with "פרסומת", name לומבוק, and end with the STOP line, which must stop marketing on WhatsApp, SMS and e-mail together; (4) keep service messages free of offers so they stay service.
- **Privacy Protection Law, Amendment 13 (in force 14 Aug 2025):** the notice at the point of collection (section 11) must state whether giving the data is a legal duty or depends on consent and the consequence of refusing, the purpose, the controller's name and contact, recipients, and access and correction rights; administrative sanctions start at ₪50 per person asked with a ₪30,000 floor [L-privacy]. Most private databases no longer need registration [L-privacy]. A photo counts as data of special sensitivity only as a biometric identifier used to identify a person digitally; whether LumeBook's likeness pipeline does that is a lawyer question [L-privacy]. Per law-firm summaries of the Privacy Protection Authority's Feb 2026 consent opinion, opt-in is expected for direct marketing, and services aimed at minors must adapt consent [L-privacy-consent].
- **Cookies and pixels:** the Authority recommended opt-in for cookies in 2020 (not binding), and the Feb 2026 opinion questions implied consent for third-party advertising tools [L-privacy-consent]. The store's default-on, notice-only banner (audit A19) is therefore a live question.
- **Consumer Protection Law:** goods made specially for the consumer are excepted from the 14-day distance-sale cancellation right, but the disclosure duties still apply; "price" includes delivery; prices must be total prices in shekels including VAT; a sale must state the price before the sale, and the "regular or previously charged price" is a material term for misleading-conduct purposes [L-consumer]. A Consumer Protection Authority enforcement note on custom-made goods (2018) was read only partly (scrambled PDF) [S-cancel]. The ₪149 struck price, "limited time" wording and every "instead of ₪X" coupon need a true earlier price.
- **Accessibility:** service websites must meet Israeli Standard 5568 (identical to WCAG 2.0) at level AA, with an accessibility statement; exemption only for VAT-exempt dealers or turnover up to ₪100,000 a year; damages up to ₪50,000 without proof of damage (indexed) [L-access]. The store has a statement page; conformance was not tested.

### 7.5 Questions for an Israeli lawyer

1. Do WhatsApp templates fall under section 30A, and is there a ruling either way?
2. Does a parent who created a book without paying fall under "negotiation for a purchase" (30A(c)(1))? What notice and refusal wording at the phone step satisfies 30A(c)?
3. Is the unfinished-book reminder advertising if it has no discount and only links back to the draft? The birthday reminder the customer asked for, when it links to a book?
4. Is a second book "a similar product" under 30A(c)(3)?
5. Must "פרסומת" be the first word of every marketing template; is a "הסר" quick reply an adequate refusal route; must a WhatsApp refusal also stop e-mail and SMS?
6. What consent record is enough as evidence, and for how long should it be kept?
7. Does the direct-mailing disclosure in Privacy Law section 17F(a) apply to segment-based campaigns to the store's own customers?
8. Is a child's photo used to generate an illustrated likeness, or any face embedding, a biometric identifier and so data of special sensitivity? Which security level applies?
9. Is opt-in needed for advertising cookies and pixels (GA4, Google Ads, Meta, OpenAI, Affiracle) under the Feb 2026 consent opinion?
10. Does the custom-goods cancellation exception apply from the order or only once production starts, and how does it interact with the 4-month right for seniors, people with disabilities and new immigrants?
11. Is the ₪149 reference price lawful as presented, and what proof of a prior price does a coupon need?
12. Do the accessibility regulations apply at LumeBook's turnover, and what is the remediation priority?
13. Who is liable for spam-law breaches by automated sends, the store owner or the developer, and what should their contract say?
14. Cross-border transfers of photos and contact data to US and EU processors (Meta, Twilio, analytics, image generation): what the transfer regulations require (not researched here).
