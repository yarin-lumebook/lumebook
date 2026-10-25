# LumeBook CRO and customer CRM strategy

24 Oct 2026 · Internal: holds sales figures from the store's admin (`docs/lumebook-sales-data-decisions-2026-10-12.md`). Keep it off the SMM plan, the dashboard and any public page. Research, audit and planning only: nothing on the site, in the store's messages or in any tool was changed, and no customer was contacted.

CRO (conversion rate optimisation) here means getting more of the people who already arrive to buy, profitably. CRM means the customer lifecycle: messages and offers from the first visit to the second book. The creator outreach map is a separate workstream.

| File | What is in it |
|---|---|
| `report.md` | This summary: the five priorities, what changes the plan, decisions |
| `audit.md` | The buying journey as it runs today, 25 observed defects and 7 ideas to test, each with evidence; competitor comparison |
| `experiments.md` | What can and cannot be tested at current volume, and 12 specified experiments and changes (X0 to X11) |
| `crm-flows.md` | Customer states, 14 flows with rules and Hebrew message drafts, discounts, channel and legal points |
| `measurement.md` | Events, sources of truth, UTMs, KPIs, incrementality, weekly checks |
| `roadmap.md` | Backlog, first week, 30/60/90 days, who does what, missing access, stack |
| `sources.md` | Every source with its evidence type and limits |
| `numbers-2026-10-25.md` | The admin readout and GA4 exports of 25 Oct: ad cost per order, funnel, books, messages, what GA4 can and cannot see, and what it changes here (raw GA4 files in `data/ga4-2026-10-25/`) |
| `cro-crm-strategy.html` | All eight files as one page with a section menu, plus the Hebrew action list as section 2 (built by `src/build_strategy_page.py`: edit the Markdown or `src/journey-actions.json`, then rebuild) |
| `src/journey-actions.json` | Every action in the journey demo as Yarin's working list in Hebrew (47 items in seven stages, who does it, fix or test or decision, how we know it worked); filter tiles and done marks on the page, marks kept in the browser only |
| `journey-demo.html` | A step-by-step walkthrough of the fixed journey on a simulated phone, starting from a Facebook ad (since 24 Oct, at Yarin's request; it started from an Instagram post and DM before), with a note behind every change and the list of every change at the end (built from `src/journey-demo.template.html` by `src/build_journey_demo.py`; nothing in it is generated or live). |

## The five priorities

### 1. Show the delivered price and arrival date before the payment page

- **Why it matters:** in the last 30 days of the admin readout, 202 orders reached payment and 85 were paid; about half leave at the step where the home shipping fee (₪30) first appears. The site's own checkout summary says "המשלוח מתווסף בקארדקום. הסכום כאן הוא עבור הספר בלבד." The book page and the preview button show ₪119 alone, and the struck-through ₪149 is exactly the one-book total with home shipping. On CardCom the first shipping option, free pickup in Jerusalem, is preselected under a "משלוח עד הבית" label, so the page shows ₪119 until the buyer opens the menu, although buyers come from all over the country (`audit.md` A25).
- **Evidence:** observed on the site and in its code (`audit.md` A2, A3); admin numbers (`docs/lumebook-sales-data-decisions-2026-10-12.md`). In Baymard's US survey, extra costs are the top abandonment reason (40%) and slow delivery the second (20%) [S-baymard-reasons]; in a StubHub field experiment people who met fees only at checkout were almost 45% less likely to buy at that step, while a cinema field experiment found hiding a surcharge changed nothing overall, so showing it early costs little [S-price]. Israeli consumer law requires prices to be total prices including delivery, and a discount to state a true earlier price (`sources.md` L-consumer).
- **Confidence:** high that the information arrives late; medium on how much fixing it adds.
- **Action:** "₪119 + ₪30 משלוח עד הבית · או איסוף חינם בירושלים" and an estimated arrival date on the book page, the preview and the purchase button; until then, home delivery preselected on CardCom instead of Jerusalem pickup; a business and legal decision on the ₪149 reference price. Measure with a fixed before/after window (`experiments.md` X1).

### 2. Say exactly what the free preview includes, and back it with real pages and one likeness promise

- **Why it matters:** every preview is an order record, and 527 were created in 30 days against 202 that reached payment, so the biggest leak is between preview and payment. The preview shows only the personalised cover; inner pages are locked ("את האיור הזה ניצור עבורכם במיוחד לאחר הרכישה") while the home page says "קוראים את הסיפור בחינם · מזמינים רק אם מתאהבים". The guarantee is stated three different ways ("100% שביעות רצון מובטחת" on book pages, "לא ניתנים לביטול" in the FAQ, "ללא התחייבות לשביעות רצון" in the terms).
- **Evidence:** observed in the editor and policies (`audit.md` A4, A5); the store already has a likeness redraw that keeps the free try (code); MeBook, Magical Book and Wonderbly each state one defect remedy (`audit.md`, competitors); research on self-made products supports the preview as a selling step only when it meets expectations ([S-diy]).
- **Confidence:** high on the gap; medium on the effect.
- **Action:** one line before the photo step on what is free, two or three real inner pages from consented customer books on the preview, one sentence of likeness and defect policy near the button (`experiments.md` X2). Later, test one illustrated inner page only for people who left (X3), judged on contribution.

### 3. Make marketing consent separate before adding any message

- **Why it matters:** for Israeli numbers the store's code sends `marketingConsent: true` whenever the required terms box is ticked, and hides the separate promotions box that foreign numbers see; the privacy policy promises a separate explicit choice. The cookie banner is notice-only and every analytics and ad tag loads before any choice. Every lifecycle flow in this plan depends on a list that was gathered lawfully, and on the WhatsApp number staying in good standing.
- **Evidence:** code and policy text (`audit.md` A6, A19). The Communications Law's section 30A requires explicit prior written consent for advertising messages, "פרסומת" at the start of each, and a way to refuse, with up to ₪1,000 per message without proof of damage; its existing-customer exception requires that the person was told at collection and offered a refusal (law text, `sources.md` L-spam). No ruling applying it to WhatsApp was found, but WhatsApp fits the statute's definition of an electronic message. Meta classes the store's reminders, coupons and birthday messages as marketing templates and requires opt-in (`sources.md` W-categories, W-optin). Law-firm summaries of the Privacy Protection Authority's Feb 2026 consent opinion say opt-in is expected for direct marketing (`sources.md` L-privacy-consent).
- **Confidence:** high on the facts; the legal consequences need a lawyer (this is not legal advice; 14 questions are in `crm-flows.md` section 7.5).
- **Action:** show the existing unticked marketing box to Israeli numbers, keep the required box for terms and service messages, align the terms, and get counsel's view on the cookie banner before changing it (switching to opt-in needs Google's Consent Mode, the setting that lets tags respect the visitor's choice and model the missing data, in place first, or reporting collapses).

### 4. Get paid books approved and delivered on time, starting with Hanukkah

- **Why it matters:** after payment the buyer still edits and approves the book, and printing starts only then ("אחרי האישור הספר מועבר אוטומטית להדפסה"); home delivery is up to 7 business days. The new birthday reminders go out a week before the date, which mostly leaves a digital gift. Hanukkah starts on 4 Dec 2026; the order deadline in `shared/facts.json` (22 Nov) is unconfirmed, and none of the Israeli competitors reviewed shows a dated cut-off.
- **Evidence:** tutorials and reminder page (`audit.md` A7, steps 10 and 11); competitor review (`audit.md`); key dates (`shared/facts.json`).
- **Confidence:** high on the mismatch; timings are hypotheses.
- **Action:** an approval nudge at 24 and 72 hours after payment with a deadline line (`crm-flows.md` F6); reminders about 21 days ahead plus a last-print-day message (F11); a dated "order by" line on book pages, preview and payment from about 10 Nov once the business confirms the date (X6).

### 5. Make results visible: fix the funnel events, attribution and links

- **Why it matters:** GA4 (Google Analytics) receives page views and purchases only, because the tag manager listens for event names the site no longer sends; first-touch attribution (the record of which link first brought a visitor) is kept per browser tab and lost when it closes; the visitor ID is no longer sent with orders; ad events carry ₪50 for a ₪119 book; links use three UTM formats (UTMs are the labels added to a link that tell the store which post, creator or message sent the visitor), and before 24 Oct no social link had a UTM at all. Without this, nobody can tell whether priorities 1 to 4, a creator, or a message sold anything.
- **Evidence:** code (`audit.md` A16, A20, A21); `research/carousel-audit/README.md`; GA4 documentation (`measurement.md`).
- **Confidence:** high.
- **Action:** the event map, purchase with a non-empty `transaction_id` sent once from the server, CardCom as an unwanted referral, private paths redacted, attribution kept 30 days, one UTM taxonomy, and holdouts on every marketing flow (a random 10 to 20% of eligible people who get no message, so the extra sales a message causes can be told apart from sales that would have happened anyway) (`measurement.md`).

A sixth item belongs on the same developer list because it is small and sits upstream of everything: **show the book cover immediately on book pages** (8.7 s and 16.2 s waits measured for a returning visitor; first-time visitors also wait for a 3D viewer, `audit.md` A1).

## What the 25 Oct numbers change

The admin readout and seven GA4 exports came in on 25 Oct (`numbers-2026-10-25.md`). The five priorities stand; these points sharpen them.

1. **Ads are close to target, so the funnel is now the cheaper lever.** In the 7 full days to 24 Oct ads cost ₪33 per paid order across all orders and ₪52 per purchase Meta credits, against ₪47 and ₪89 the week before, a ₪30 target and a ₪50 ceiling, at ₪550 a day. Every point gained between preview and payment now lowers cost per order without more budget. Keep the budget flat until one Control-versus-Challenger ad test has run (the admin's own recommendation, and the one place with enough volume for a real A/B test).
2. **Priority 5 starts this week, with the ads owner:** more than half of GA4's "Organic Social" (1,441 of 2,606 sessions) is ad clicks whose Meta placement sits in `utm_medium`; the Meta source has eight spellings; CardCom's return visits give "Referral" more revenue than Paid Social; GA4 counts a third or more fewer purchasers than the store and has three purchase events. One URL parameter line on every ad and the unwanted-referral list fix most of it (`measurement.md` section 4).
3. **Recovery order confirmed, with today's admin comparison:** the plain "finish your book" reminder adds +9.5 purchases per 100 against people left alone, the first coupon +7.6, the third +2. Reminder first, one coupon at most, no third (X5). The admin also says there is no random control group, so holdouts become a fix.
4. **No list-wide broadcasts:** the back-to-school message went to 813 people and was followed by one purchase within 24 hours; it is also the riskiest kind of message while consent is bundled (priority 3).
5. **"למי הספר?" moves to do now** as one optional question on the thank-you page (X8): Meta credits 43 of the 102 purchases in its age table to women 45 and over.
6. **The ads probably land on general pages, not book pages** (the birthday book page has about 390 views in 90 days against 3,490 paid-social sessions), which makes the book deep link (X7) more valuable than assumed. Check the ads' destination URLs.

## What the research changed (assumptions challenged)

1. **"We need to set up phone-based lead capture and a CRM."** The store already does both. It verifies the phone (and requires an e-mail) before any preview, sends WhatsApp and SMS through Twilio, keeps a left-alone comparison group, and has reminders, a referral program, a reaction-video offer, a sibling offer and a marketing preferences page. The work is to fix consent, sequence and measure what exists, with the developer, not to add a new system.
2. **Phone first is right for service and recovery, but not alone.** WhatsApp is where reminders and help already happen, and the phone is the customer's identity. But marketing consent is currently bundled; Meta caps how many marketing templates one person receives, changed its rate cards four times in 2026 and resumed charging for utility messages inside the service window on 1 Oct (`crm-flows.md` section 7.1); and depending on one Meta-owned channel concentrates risk. In Baymard's survey 14% of shoppers refuse to give a phone number at all [S-phone], so the store's clear reason for asking ("כדי שנשמור לכם את הספר") matters. The store already collects e-mail; use it for order and approval messages and as a second marketing channel with its own consent (`crm-flows.md` section 4).
3. **The free greeting card is already live, so the question is whether it sells books.** `/holiday-cards` offers a personalised Hanukkah card or a five-page colouring booklet, then a ₪99 book code, but it is not in the sitemap and trackers are blocked on it. A free offer attracts people who value the zero price ([S-zero]), costs generation money and adds a step. Keep the direct book link as the default social CTA and test the card against it in the DM funnel, judged on paid books and cost per paid book (`experiments.md` X9).
4. **Tool access does not mean tracking works.** GA4 is nearly blind past the landing page (priority 5).
5. **ManyChat is an entry point, not the CRM.** Use it to answer comments and DMs with the right book link and one question ("למי הספר?"); let the store's own phone step identify people, so consent and identity stay in one place.
6. **Discounts are not the main recovery lever.** In the admin's own comparison the third coupon added +1.6 sales per 100 against +5.4 for the first (with a comparison group the dashboard calls probably tiny); on 25 Oct the plain reminder added +9.5, the first coupon +7.6 and the third +2, and the best linked message is still the ₪79 second book (62 purchases within 24 hours of 234 received), not a coupon. Fix clarity first; at most one coupon, never in the first message, judged on contribution (`crm-flows.md` section 6).
7. **The grandparent buyer is still a hypothesis, but a stronger one.** It rests on Meta's attribution by age (since 25 Oct: women 45 and over get 43 of 102 credited purchases, women 55 to 64 the cheapest at ₪81 each), not on verified buyers. Ask "למי הספר?" after purchase now, and in the DM router, for four weeks before building anything for gift givers (`experiments.md` X8).
8. **Faster recovery messages are not better.** In field experiments with 40,500 and 23,900 customers, cart reminders sent 30 to 60 minutes after abandonment made people less likely to buy than no message, while reminders 1 to 3 days later increased purchases [S-timing]. Every recovery flow here waits about a day (`crm-flows.md`, section 3).
9. **A/B tests are mostly out of reach.** About 200 people reach payment a month; detecting a 10-point change there needs about 780. Fix observed defects, use fixed before/after windows, usability sessions and non-buyer interviews, and keep holdouts running for a quarter (`experiments.md` section 1).

## Direct purchase vs lead magnet

| | Direct to the book | Free card first |
|---|---|---|
| When it fits | Content about a specific book or moment (birthday, new sibling, pacifier, Hanukkah book), creator videos, the bio link | Cold audiences with no occasion yet, holiday sharing moments, parents who are not ready to upload a photo for a paid product |
| Steps to purchase | Book page, wizard, preview, payment | Card request, card, a later book offer, then the same four steps |
| Cost | Preview generation per started book (cost unknown) | Card generation per request, plus the book preview later |
| Risk | Visitors not ready yet leave without trace | Draws freebie seekers; distracts from the book; tracking blocked on the route |
| Evidence for LumeBook | 21.1% of people who start a book pay within 7 days (25 Oct; 21.7% on 12 Oct) | None yet |
| Recommendation | Default | Test only (X9); also a good thank-you gift after purchase |

## Do now, test next, defer

- **Do now:** priorities 1, 3, 4 and 5 (starting with the Meta URL parameters and CardCom as an unwanted referral), the book-page cover fix, links to @lumebook.il, the photo-retention line at upload, coupon ladder without a first-message coupon, no list-wide broadcasts, the "למי הספר?" question after purchase. These are fixes; measure each with a before/after window written down in advance.
- **Test next:** priority 2 content (real pages, promise), the payment-step reminder (F4) with a holdout, the help, video, review and referral sequence after delivery (F8, F9, F12), the sibling framing of the second-book offer (X10), the DM router question (X8), per-channel preferences, one Control-versus-Challenger ad test before any budget increase.
- **Defer:** one illustrated inner page before payment (needs the generation cost), the free card as a default funnel, a gift-giver photo link or gift card, new discount levels, any new tool, small copy and design tests.

## Stack in one paragraph

Keep customer records, consent and WhatsApp in the store, which already sends through Twilio; add properly authenticated e-mail (a free or $15-a-month sender) as the second channel; use ManyChat (free or about $14 to $17 a month for Instagram only) to answer comments and DMs with the right book link. Nothing new is needed for analytics beyond fixing what is there. At about 1,500 marketing and 1,000 utility WhatsApp messages a month, Meta and Twilio fees come to roughly $70 at Israel's rates (about $0.035 per marketing and $0.005 per utility message, from third-party tables checked against Meta's card), and e-mail is near free. Two platform changes need the developer's attention: since 1 Oct 2026 WhatsApp charges utility messages even inside the service window, and from 13 Oct 2027 marketing templates can no longer go through Meta's Cloud API, so Twilio's migration path to the Marketing Messages API has to be checked. Move to a WhatsApp CRM (from about $49 to $79 a month) only if flows cannot be changed within two weeks, a shared support inbox is needed, or marketing e-mail outgrows the free tiers (`roadmap.md` section 7).

## What is still unverified

Where the ads land; what the "chatgpt / paid" traffic in GA4 is; reached-payment counts since 12 Oct (Mixpanel is not connected to the admin); card entry, and whether the wallets (all four show in Safari) appear inside Facebook's and Instagram's in-app browsers; payment failure and confirmation pages on screen; the server's purchase payload; the live WhatsApp templates and their timing; page speed and accessibility scores (PageSpeed Insights would not run); the first-visit experience on a clean phone; costs per order (print, shipping, generation, fees), which every profit decision needs. The access needed is listed in `roadmap.md` section 6.

## How this folder is kept private

`research/cro-crm/` is in the private GitHub repository. The nightly job (`tools/nightly_commit.py`, 00:00) commits and pushes everything not ignored, so these files will reach the private repo tonight; it deploys only the Vercel components (the dashboard and the creator brief), and the dashboard lists only components registered in `lumebook.json`. This folder is deliberately **not registered**, so it does not appear on the dashboard or its public read-only copy. Register it (with publish `null`) only if it should show up as a card on the internal board.
