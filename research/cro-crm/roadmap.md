# Backlog, stack and roadmap

Internal. Part of `research/cro-crm/` (start at `report.md`). IDs refer to `audit.md` (A, B), `experiments.md` (X) and `crm-flows.md` (F).

## 1. Who does what

| Role | Who | Owns |
|---|---|---|
| Social and creators, CRM content | Yarin | Links and UTMs on every post and creator, the DM router in ManyChat, Hebrew message copy, usability sessions and interviews, the weekly numbers routine |
| Development | Yossi (store developer and owner of the admin) | Store fixes, events, the message system (Twilio templates, timings, holdouts), CardCom settings, consent capture |
| Support | whoever answers the WhatsApp line (to confirm) | Human handoff from every flow, tagging chats, complaint log |
| Business decisions | the store owner(s) (to confirm who) | Prices and the ₪149 reference, guarantee and likeness policy, Hanukkah order-by date, discount rules, legal review, budget |

## 2. Prioritised backlog

Confidence: high = observed defect or strong evidence; medium = good evidence, LumeBook effect unknown; low = hypothesis. Effort: S = hours, M = days, L = weeks.

| # | Item | Evidence | Mechanism | Confidence | Effort | Depends on | Owner | Success metric |
|---|---|---|---|---|---|---|---|---|
| 1 | Book pages show the cover at once (X0, A1) | 8.7 s and 16.2 s waits observed | Visitors from posts see the product instead of a loader | High (defect); medium for new visitors | S to M | Clean-phone check | Yossi | Wizard starts per book-page landing |
| 2 | Total cost and arrival date before payment (X1, A2, A3, A25) | ₪30 shipping first appears at CardCom, where free Jerusalem pickup is preselected; ₪149 struck price equals the delivered total | Removes the surprise at the step where about half leave | High (defect), medium (effect) | S to M | Reference-price decision | Yossi, business | Paid ÷ preview ready |
| 3 | Separate marketing consent and aligned terms (A6) | Terms and privacy policy contradict each other | Lowers legal risk; makes the list usable | High | S | Legal review | Business, Yossi | Consent recorded per contact |
| 4 | Tell buyers what the preview includes; real inner pages; one likeness promise (X2, A4, A5) | Inner pages locked; guarantee contradicted | Sets expectations before payment | High (defect), medium (effect) | M | Policy decision, consented pages | Yossi, Yarin, business | Paid ÷ preview; likeness complaints |
| 5 | Approval nudge after payment (F6) | Printing starts only after approval | Faster approval, on-time gifts, fewer "where is my book" | High | S | Message template | Yossi | Days from payment to approval |
| 6 | Payment-step reminder without discount (F4, X4) | Half leave at payment; 12 Oct recommendation | Recovers abandoned payments | Medium | S | "Reached payment" event | Yossi | Paid within 72 h vs holdout |
| 7 | Reminder timing: 21 days and last-print-day (F11, X6, A7) | 7-day reminder vs up to 7 business days delivery plus approval | Turns reminders into on-time printed orders | High (mismatch), low (timing) | S | Print lead time | Yossi | Printed orders per reminder |
| 8 | Hanukkah order-by date on pages and messages (B5, X6) | No dated cut-off at any Israeli competitor reviewed | Removes timing doubt before the biggest gift date | Medium | S | Business confirms date | Business, Yossi, Yarin | Hanukkah orders paid before the cut-off |
| 9 | One UTM taxonomy and deep links to books (X7, `measurement.md` section 4) | Three formats in use; bio link to home | Makes social sales visible; shorter path | High (need), low (effect) | S | Yossi confirms the wizard accepts a book parameter | Yarin | Share of orders with UTMs |
| 10 | Purchase event with `transaction_id`, CardCom as unwanted referral, private paths redacted, pixel loaded once | GA4 and Meta docs; console warning | Trustworthy numbers | High | S to M | GA4 access | Yossi, Yarin | Weekly reconciliation passes |
| 11 | Coupon ladder: no coupon in message 1, no third coupon (X5) | +1.6 vs +5.4 extra sales per 100 | Same recovered sales at lower cost | Medium | S | Ladder settings | Yossi, business | Contribution per eligible person |
| 12 | Help after delivery, then video and review reminder, then referral (F8, F9, F12) | UGC and referral programs exist without a flow | More proof, more referred buyers, earlier fixes | Medium | S | Delivery date in the system | Yossi, support | Videos and reviews per 100 orders |
| 13 | Second-book message for siblings and family (F10, X10) | Strongest recorded message | More books per order | Medium | S | | Yossi, Yarin | Second books ÷ first purchases |
| 14 | Instagram DM router with "למי הספר?" (F1, X8) | Gift-giver share unknown | Measures gift buyers; routes to the right book | Medium | S | ManyChat setup | Yarin | Books started per 100 DMs; gift share |
| 15 | Per-channel marketing preferences; e-mail as second channel (A18, `crm-flows.md` section 4) | One switch for three channels | Fewer full opt-outs; less dependence on one channel | Medium | M | Consent design | Yossi | Opt-out rate by channel |
| 16 | Photo-retention line at upload (B3) | Policy says 60 days; nothing at upload | Lowers photo worry | Medium | S | | Yossi | Photo-step completion |
| 17 | Link the existing `/orders` status page from every order message (F7) | The page exists in code; MeBook and Magical Book show similar timelines | Fewer support questions | Medium | S | Courier data in the page | Yossi | "Where is my book" chats per 100 orders |
| 18 | Smaller fixes: links to @lumebook.il, step counter, seasonal ordering, Markdown in blog preview, "Unknown Book", sibling copy, age range (A8, A10 to A15) | Observed | Trust and polish | High | S each | | Yossi | n/a |
| 19 | One illustrated inner page for people who left (X3) | Inner pages locked | Removes the likeness doubt for the undecided | Low | M | Generation cost per page | Yossi, business | Contribution per person messaged |
| 20 | Free greeting card vs direct link (X9, F0) | Live at `/holiday-cards`, untracked; zero-price effect | Unknown | Low | M | Code redemptions per arm | Yarin, Yossi | Paid books per 100 DM conversations |
| 22 | Meta URL parameters: one line on every ad; CardCom and test hosts as unwanted referrals (`measurement.md` section 4) | 1,441 ad sessions counted as Organic Social; 8 source spellings; CardCom referral credited ₪4,376 (`numbers-2026-10-25.md`) | Ads and organic posts become separable; GA4 stops crediting CardCom | High | S | Ads Manager and GA4 access | whoever runs the ads, Yossi | Share of Meta sessions with `utm_medium=paid-social`; Referral revenue in GA4 |
| 23 | No list-wide marketing broadcasts until consent is separate (A6) | Back-to-school message: 813 sent, 1 purchase within 24 h | Removes the riskiest messages and their cost | High | S | | Yossi, business | Marketing messages sent without a trigger: zero |
| 24 | "למי הספר?" on the thank-you page, four weeks (X8) | Meta credits 43 of 102 purchases to women 45 and over | Tells whether gift givers need their own path | Medium | S | | Yossi, Yarin | Share answering "לנכד או לנכדה"; payment per preview by answer |
| 25 | One Control-versus-Challenger ad test before raising the budget | Admin recommendation, 25 Oct; ₪33 per paid order in 7 days, ₪30 target | Budget goes to the ad that sells | Medium | S | | whoever runs the ads | Meta purchases and paid orders per arm after about 102 Meta purchases |
| 21 | Gift-giver photo link or gift card (X8, B2) | Gift buyer share unknown; MeBook sells gift cards | Lets buyers without a photo order | Low | L | Result of item 14 | Business, Yossi | Gift orders |

## 3. Do now, test next, defer

**Do now (fixes and low-risk changes, no test needed):** items 1, 2, 3, 5, 7, 8, 9, 10, 16, 18, 22, 23, 24 (22 first: it takes minutes and makes every later read possible). Measure each with a before/after window written down in advance.

**Test next (with a holdout or a fixed before/after window):** items 4, 6, 11, 12, 13, 14, 15, 17, 25.

**Defer until the basics are fixed and costs are known:** items 19, 20, 21, new discount levels, any new tool, small copy and design tests.

## 4. First week (from Mon 26 Oct 2026)

| Day | Who | Action |
|---|---|---|
| Mon | Yarin | Load `/books/15` and `/books/2` on a phone in a private window over mobile data; note when the cover appears. Send Yossi the results with audit A1. |
| Mon | Yarin | Send Yossi one message with: A1, A2/A3, A6, F6, F4 and the missing-data list (section 6 below). Ask for a 30-minute call. |
| Mon | Yarin | Send whoever runs the Meta ads the URL parameters line (item 22) and ask for the destination URL of every live ad; ask Yossi what the `chatgpt / paid` traffic in GA4 is and whether money is spent on it. |
| Tue | Yarin | Start using one UTM format (`measurement.md` section 4) on every link; link posts to the book page, not the home page. |
| Tue | Yarin | Ask whoever answers support for the last 90 days of chats, or read them; tag price, delivery, likeness, payment, photo, other. |
| Wed | Business | Confirm the Hanukkah order-by date and the real print plus delivery time (`shared/facts.json` key date is unconfirmed). |
| Wed | Business | Decide the likeness and defect policy (one sentence for preview and payment) and whether ₪149 stays as a reference price. |
| Thu | Yarin | Recruit 5 parents (Yarin's network or the parent-community map) for a 20-minute recorded phone session up to the payment page, with their own phone and a photo they choose; nobody pays. |
| Thu | Yossi | Put home delivery first and preselected on the CardCom page (A25). Ask CardCom how its server notification reports declines, whether the wallets (all four are on) can sit right under the total, and whether the redirect can pass the e-mail and the shipping choice. |
| Fri | Yarin | Write the before-numbers for the 31 Oct admin screenshots (already planned in `docs/lumebook-sales-data-decisions-2026-10-12.md`) and add: previews ready, reached payment, paid, approval lag. |

## 5. 30, 60 and 90 days

**By 24 Nov 2026 (Hanukkah push):**
- Items 1, 2, 3, 5, 7, 8, 9, 10 shipped; the order-by date on book pages, preview and payment from about 10 Nov.
- Usability sessions and 5 to 10 non-buyer interviews done and summarised (in `research/cro-crm/` as a new file).
- F4 and F6 live with holdouts on F4; coupon ladder changed (item 11).
- Weekly reconciliation routine running (`measurement.md` section 9).

**By 24 Dec 2026 (after Hanukkah):**
- Read Hanukkah: orders before the cut-off, approval lag, late deliveries, F6 effect.
- Items 4, 12, 13, 14 live; the first quarter of holdout data accumulating.
- Decide on X3 (illustrated page) and X9 (free card) using the cost numbers.

**By 24 Jan 2027:**
- First quarterly incrementality read for CRM, pooled across flows, with ranges (`measurement.md` section 8).
- Cohort repeat-purchase report for buyers since Oct 2025.
- Decide whether volume justifies any A/B test beyond the payment step; otherwise keep to fixes, sequential changes and qualitative research.

## 6. Minimum missing access and data

| Need | From | Why |
|---|---|---|
| Mixpanel connected to the admin again ("mixpanel_export_too_large" on 25 Oct) | Yossi | The only source of reached-payment counts, the biggest leak in the plan |
| Read access to the admin's order table with `acquisitionAttribution`, flow arm, and the message log (sends, holdout flag, opt-outs) | Yossi | Every KPI and holdout read |
| GA4 property `G-HXMTP56QS9` admin or editor access | Yossi | Unwanted referrals, data redaction, internal traffic, DebugView |
| Cost per order: print, shipping, CardCom fee, illustration generation per page and per preview, message fees | Yossi, business | Contribution per order and every discount or preview decision |
| Live WhatsApp templates, timings and coupon values | Yossi | To redesign F2, F3, F10 rather than guess |
| Which marketing consent each contact gave, and when | Yossi | Lawful marketing (`crm-flows.md` section 7) |
| Whether new visitors also wait for the cover; what `likenessRecoveryEnabled` does; whether all flows lock inner pages | Yossi | A1, A4, A5 |
| Hanukkah order-by date; print and courier lead times | Business | X6, F6, F11 |
| The flow-arm test (`book_flow_v1`): arms and results | Yossi | Whether randomisation can be reused |
| Support chats, last 90 days | Support | Qualitative evidence |
| A lawyer's answers to the legal questions | Business | Consent and price display |

## 7. Stack

### What exists (inventory, 24 Oct 2026)

| Job | Tool today | Owner | Evidence |
|---|---|---|---|
| Customer and order records, consent | The store's own database (Supabase and AWS per the privacy policy), admin at pdf.lumebook.com | Yossi | Privacy policy; 12 Oct readout |
| WhatsApp and SMS | Twilio (WhatsApp Business Platform), templates and a left-alone group in the admin | Yossi | Privacy policy; admin |
| E-mail | The store sends the digital copy and has a one-click unsubscribe endpoint; sending provider not identified | Yossi | Code |
| Instagram DMs | ManyChat (plan not checked) | Yarin | Yarin's brief |
| Analytics | GA4 and Google Ads through GTM, Meta pixel, Mixpanel, OpenAI ads pixel, Affiracle, Sentry | Yossi | Code, browser |
| Payment | CardCom hosted page (Israel), Stripe (US) | Yossi | Code |
| Edge | Cloudflare (proxy, no caching) | Yossi, Yarin has access | Headers |

### Options compared (prices verified 24 Oct 2026 unless marked)

| | A. Keep the store's sender, add e-mail properly (recommended) | B. ManyChat at the Instagram edge (add to A) | C. Replace the WhatsApp sender with a WhatsApp CRM |
|---|---|---|---|
| What it is | Twilio WhatsApp as now; a transactional e-mail sender and, if needed, a marketing e-mail tool with a shared suppression list | Comment and DM keyword flows that hand a tagged book link and one question | 360dialog, Wati, respond.io or Glassix with inbox, broadcasts and automations |
| Tool fees | Resend free (3,000 e-mails a month, 100 a day) or Postmark $15 a month (10,000); Brevo free (300 a day) or Resend marketing free (1,000 contacts) for newsletters; Amazon SES $0.10 to $0.16 per 1,000 | Free (25 active contacts a month), Essential $14 a month annual or $17 monthly (250, Instagram only), Pro $29 or $39 (2,500); ManyChat prices from search snippets of its own help centre and a third-party page, since its site blocked automated reading | 360dialog €49 or €99 per number a month; Wati from $59 a month (annual); respond.io from $79 a month (annual); Glassix from $49 per agent a month |
| Usage costs | WhatsApp about $0.0353 per marketing and $0.0053 per utility message delivered (Israel, from third-party tables checked against Meta's card); Twilio adds $0.005 per WhatsApp message | none on Instagram | Meta rates plus any markup (360dialog states none) |
| Hebrew and RTL | Transactional HTML is whatever the developer writes (`dir="rtl"`); Brevo has a text-direction setting (help snippet); Israeli ESPs (ActiveTrail, Smoove, Inforu) are native Hebrew | Instagram renders Hebrew; ManyChat's builder has no official RTL support (open community request since Feb 2025) | varies; Glassix is Israeli |
| Israel support | yes for all; Klaviyo cannot send SMS to Israel | yes | yes |
| Integration effort | low for transactional (order events already exist); medium for marketing e-mail (consent flags, shared opt-out, one-click unsubscribe already built) | low (External Request or Make to post the lead to the store, paid tier) | high: templates, webhooks, opt-outs, holdouts and number migration rebuilt |
| Maintenance | DNS records (SPF, DKIM, DMARC), bounce and complaint handling; the Marketing Messages API migration before Oct 2027 (ask Twilio) | keyword flows per post, Meta policy changes | moves to the vendor, but fees dominate the budget |

Sources: `sources.md` sections 6 and 7.

### Recommendation: the simplest viable setup

- **Records, consent, messages:** stay in the store (option A). Every flow in `crm-flows.md` is a template plus a trigger in the system Yossi already runs. The changes are consent capture, labelling, holdouts, timing and logging, not a new tool.
- **E-mail:** keep whatever sends the digital copy today if it authenticates properly (SPF, DKIM, DMARC on lumebook.com); add Resend or Postmark only if it does not. For marketing e-mail, start with Brevo's free tier or Resend's free marketing tier, synced to the store's consent and opt-out flags.
- **Instagram:** ManyChat Free or Essential for the DM router (F1). It hands a link; it does not store phones or consent.
- **Analytics and reporting:** GA4 and Mixpanel as they are, with the fixes in `measurement.md`; a weekly export from the admin into a Google Sheet for the KPIs. No new analytics tool.
- **SMS:** only as a fallback for people without WhatsApp, through a local provider if Twilio's $0.2575 per segment proves material.

**Illustrative monthly cost** (unit prices above times assumed volumes, not a quote): about 1,500 marketing and 1,000 utility WhatsApp messages come to roughly $53 + $5 in Meta fees, plus about $12 in Twilio's per-message fee; e-mail $0 to $15; ManyChat $0 to $17. Roughly $70 to $100 a month, plus developer time. For comparison, the admin estimated about $96 in message fees over the 90 days to 12 Oct.

**Upgrade triggers** (move to option C or a marketing platform such as Klaviyo or an Israeli ESP only if one holds for two months running):
- Yossi cannot ship or change a flow within two weeks of the request.
- More than one person answers WhatsApp support and needs a shared inbox with assignment.
- Marketing e-mail goes beyond the free tiers (about 1,000 contacts or 300 a day).
- Meta's Marketing Messages API migration cannot be done on the current sender.
