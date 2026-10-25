# Measurement and data plan

Internal. Part of `research/cro-crm/` (start at `report.md`). It specifies what to measure, where each number comes from, and how to keep personal data out of analytics. It does not change any tracking; every item here is a request for the store's developer (Yossi) or a reporting routine for Yarin.

## 1. What exists today (verified 24 Oct 2026 unless marked)

| Piece | Evidence | Status |
|---|---|---|
| GA4 property `G-HXMTP56QS9` inside GTM `GTM-5V3DL6S3` (container version 20) | `page_view` hit seen in the browser; GTM container read from code | Receives `page_view`, `user_identify` and `purchase` only. Tags for wizard steps, book creation and payment redirect listen for event names the site no longer sends, so they never fire. A tag meant to fire on CardCom can never fire (GTM does not run there). CardCom is not in the linker list (audit A20) |
| Google Ads `AW-17291292550` | GTM tag | One purchase conversion; enhanced conversions off |
| Meta pixel `1535930801145446` | loaded by site code, not GTM | PageView, ViewContent, Lead, CompleteRegistration, AddToCart, InitiateCheckout, Purchase. Lead, CompleteRegistration and AddToCart carry ₪50 (the disabled digital price); InitiateCheckout has no shipping; `external_id` is the order ID (audit A16, A20) |
| GA4 export, 27 Jul to 24 Oct 2026 [O-ga4-oct25] | `data/ga4-2026-10-25/`, `numbers-2026-10-25.md` section 5 | Three purchase events (`purchase` 164, `Purchase` 100, `payment_completed_and_redirect` 654); 42 purchasers in 19 to 24 Oct against 71 paid orders in the admin; "key events" include `form_start` and `user_identify`; 501 sessions from `secure.cardcom.solutions` and 235 from test or internal hosts (replit, Vercel previews, appium, 127.0.0.1) |
| Mixpanel | about 75 event names in code, including `Wizard Step Completed`, `OTP Verification Succeeded`, `Order Created`, `Story_Generation_Started/Completed/Failed`, `Editor_Ready`, `Purchase_CTA_Clicked`, `Checkout_Link_Created`, `Payment_Result`, `Purchase` | The richest funnel source today. Funnel events fire only for orders created with analytics consent; identity is the order ID (audit A21) |
| OpenAI ads pixel | `bzr.openai.com`; Purchase sent from the server with a phone hash (privacy policy) | Live |
| Affiracle (affiliate tracker, 48-hour cookie) | script and visit hit; conversion only when the server flags an affiliate order | Live; not named in the cookie policy |
| Sentry | loads on first tap; `sendDefaultPii: false` | Live |
| Acquisition attribution | first and last touch of `utm_*`, `fbclid`, `gclid`, landing path, sent with each new order as `acquisitionAttribution` | Kept in `sessionStorage` (lost when the tab closes); `visitorId` no longer sent (audit A21) |
| Consent | first visit writes `cookie_consent` with analytics on by default; notice-only banner; no Consent Mode default (audit A19) | Every tool loads before any choice |
| Flow experiment | code always returns the `wizard` arm; `book_flow_v1` keys are leftovers | Finished; no randomisation running |
| CRM sends | WhatsApp and SMS through Twilio (privacy policy); admin shows sends, purchases after, a left-alone group (12 Oct readout) | Live |
| Payment | CardCom hosted page, full redirect; return to the editor with `responsecode` (`0` = success), then `/order-confirmation/<uuid>` | Live |

Not verified: whether the server's `purchase` payload carries `transaction_id` and shipping; what goes to Meta's Conversions API; whether CardCom is excluded as a referral in the GA4 property settings; whether the SPA sends a `page_view` on each route change.

## 2. Sources of truth

| Question | Source of truth | Why |
|---|---|---|
| Was an order paid, for how much, refunded? | Store order database and CardCom | Only the payment system knows. Analytics is reconciled to it, never the reverse |
| Who started, previewed, reached payment? | Store database events (server side), Mixpanel as a second view | Server events do not depend on cookie consent |
| Where did the visitor come from? | `acquisitionAttribution` on the order; GA4 for sessions | GA4 sees only consenting visitors |
| Which message went to whom, and who was held out? | The store's message log (Twilio send records joined to person and order) | Needed for holdout comparisons |
| What did a creator's link sell? | Ambassador ledger (7-day window, printed books) | Already built into the store |
| What does a sale cost? | Ad spend (Meta, Google), message fees, generation cost, print and shipping cost, discounts, commissions and referral rewards | Most of these are not yet known to Yarin (`roadmap.md`, missing data) |

Keep three purchase counts apart and never add them: **store orders**, **ambassador-credited orders**, **platform-reported purchases** (Meta, Google, OpenAI). This repeats the rule in `research/creator-content-conversion/report.md`.

## 3. Event plan

Names follow GA4's recommended ecommerce events where one fits (https://developers.google.com/analytics/devguides/collection/ga4/reference/events, read 24 Oct 2026): `purchase` requires `transaction_id`, `value`, `currency`, `items`; `begin_checkout`, `add_shipping_info` and `add_payment_info` require `currency`, `value`, `items`; `refund` requires `transaction_id`. Custom events cover the personalisation steps. The same event names should go to Mixpanel so the two can be compared.

Most of these moments already exist as Mixpanel events (section 1). The cheapest path is to push the existing ones to the dataLayer under the GA4 names below, rather than add new tracking: `Book Viewed` to `view_item`, `Wizard Step Completed` to `wizard_step_viewed`, `OTP Verification Succeeded` to `phone_verification_completed` and `generate_lead`, `Editor_Ready` or `Story_Generation_Completed` to `preview_ready`, `Purchase_CTA_Clicked` to `purchase_cta_clicked`, `Checkout_Link_Created` to `begin_checkout`, `Payment_Result` to `payment_result`, `Purchase` to `purchase`.

Shared parameters on every event below (none of them personal): `book_id` (catalogue ID such as `15`), `book_category`, `creation_mode` (`ready`, `ai`, `scratch`), `book_language`, `flow_arm`, `is_returning` (has a verified session), `traffic_type` (`internal` for Yarin, Yossi and test devices).

| Event | Exact trigger | Extra parameters | Validation check |
|---|---|---|---|
| `view_item` | Book page (`/books/:id`) rendered with the catalogue data loaded | `items[{item_id, item_name, item_category, price}]` | One per book page view in DebugView |
| `wizard_step_viewed` | Each wizard step shown | `step_number`, `step_name` (`details`, `mode`, `book`, `photo`, `phone`), `step_total` | Step totals match the counter (audit A10) |
| `wizard_error` | A validation message shown | `step_name`, `error_code` (for example `name_missing`, `age_missing`, `photo_missing`, `photo_rejected`) | Never the field value |
| `book_selected` | Book chosen in the wizard | `items[...]` | |
| `photo_upload_started` / `photo_upload_completed` / `photo_upload_failed` | File chosen / server accepted / server or client rejected | `file_type` (`jpeg`, `heic` ...), `failure_reason` | No file name, no image data |
| `phone_verification_started` / `phone_verification_completed` | Code sent / code accepted | `method` (`whatsapp`, `sms`) | No phone number |
| `generate_lead` | First time a person is identified (phone verified) | `lead_source` (`wizard`, `reminders`, `referral`, `gift_card`) | One per person, not per book |
| `preview_ready` | Personalised cover shown to the buyer for the first time | `wait_seconds` (from photo accepted to cover shown), `preview_scope` (`cover_only`, `cover_plus_page`) | Server-side equivalent recorded with the order |
| `preview_page_viewed` | Buyer flips to a page | `page_index`, `locked` (true/false) | Shows how far people look at locked pages |
| `purchase_cta_clicked` | "לרכישה ועריכת הספר" pressed | `value`, `currency` | |
| `begin_checkout` | Redirect to CardCom started | `value`, `currency`, `items`, `coupon` | Count matches server "reached payment" |
| `add_shipping_info` | Only if the store learns the shipping choice before payment; otherwise from the CardCom notification | `shipping_tier` (`home`, `pickup_jerusalem`, `pickup_rishon`, `join_today`) | |
| `purchase` | **Once per paid order**, from the server after CardCom confirms payment (or on `/order-confirmation/:order_id` with a guard so a reload does not resend) | `transaction_id` (the order number shown to the customer, never empty), `value` (paid amount after discount, excluding shipping, or state which), `shipping`, `tax`, `currency=ILS`, `coupon`, `items`, `acquisition_source` copied from the order | Deduplication: GA4 deduplicates purchases with the same `transaction_id` on web streams; an empty string deduplicates all blank IDs together (https://support.google.com/analytics/answer/12313109). Choose one sender (browser or server) |
| `book_approved_for_print` | "אישור ספר" confirmed | `transaction_id`, `days_from_purchase` | Needed for the activation flow (F6 in `crm-flows.md`) |
| `refund` | Refund recorded in the store or CardCom | `transaction_id`, `value`, `currency` | Monthly reconciliation |
| `reminder_saved` | Reminder saved on `/my-reminders` | `reminders_count`, `days_until_next` | No names or dates |

### Payment provider and cross-domain checks

- CardCom's hosted page lives on another domain. Add `secure.cardcom.solutions` (and any CardCom return domain) to GA4's **unwanted referrals**, otherwise sessions returning from payment can be credited to CardCom; GA4 says the referrer is then ignored for attribution and lists a third-party payment processor as the typical case (https://support.google.com/analytics/answer/10327750).
- Do not rely on a browser `purchase` event alone: a buyer who closes the tab on CardCom never reaches the confirmation page. The server already knows when CardCom confirms; send `purchase` from there (GA4 Measurement Protocol, with the visitor's GA client ID stored on the order) or reconcile from the store database.
- Check that the Meta pixel is loaded once, and that the browser Purchase and any Conversions API Purchase share an `event_id` (audit A16).

### Keeping personal data out of analytics

Google's policy: nothing Google could recognise as personally identifiable may be sent, and "Both the URL path and parameters must be free of PII" (https://support.google.com/analytics/answer/6366371). In LumeBook's case:

- **Never in any event, URL or title:** phone, e-mail, parent or child name, child age with name, photos, reminder names and dates, dedication text.
- **Private links:** `/editor/<order uuid>`, `/order-confirmation/<order id>`, `/company/<token>/...`, support resume links. Rewrite `page_location` and `page_path` to a template (`/editor/[order]`) before sending to GA4, Meta and Mixpanel. GA4's data redaction can strip named **query parameters** and e-mail-like text on a best-effort basis, but it does not cover path segments or Measurement Protocol (https://support.google.com/analytics/answer/13544947).
- **The wizard heading contains the child's name** ("מצאנו 66 ספרים ל..."): make sure no tag reads page text into events.
- **Image URLs are personal data here.** The code sends the child's illustrated cover URL to Mixpanel in the likeness events (`Adjust Likeness Question Shown/Answered`); remove it, as the scrubber already does for names and phones (audit A22).
- **Hashed phone to ad platforms** (the OpenAI line in the privacy policy, and any Meta advanced matching) is personal data processing that needs a lawful basis and consent; list it in the consent banner's purpose text. Question for counsel (`crm-flows.md`, legal section).

## 4. Links and UTMs

UTMs are the `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` and `utm_term` tags added to a link so the store can tell which post, creator or message brought the visitor. Three formats are in use today:

| Where | Format seen | Problem |
|---|---|---|
| Instagram bio (added by Instagram itself) | `utm_source=ig&utm_medium=social&utm_content=link_in_bio` | `ig`, not `instagram`; no campaign |
| Carousel link maker (`research/carousel-audit/src/audit.py link`) | `utm_source=instagram&utm_medium=dm|bio|story&utm_campaign=car-<topic>&utm_content=YYYYMMDD[-variant]` | The placement is in the medium |
| Creator plan (`research/creator-content-conversion/report.md`) | `utm_source=instagram&utm_medium=creator&utm_campaign=<handle>&utm_content=<shortcode>&utm_term=<test arm>` | Fine |

Proposed single taxonomy (lowercase, hyphens, no spaces, no personal data):

| Tag | Values | Example |
|---|---|---|
| `utm_source` | platform: `instagram`, `facebook`, `tiktok`, `whatsapp`, `sms`, `email`, `qr`, `google` | `instagram` |
| `utm_medium` | `social` (own posts), `creator`, `community` (parent groups), `crm` (lifecycle messages), `referral` (customer referral), `paid-social`, `print` (QR in the book or flyers) | `crm` |
| `utm_campaign` | program and topic: `car-<topic>`, `<creator handle>`, `f3-preview`, `hanukkah-2026` | `f3-preview` |
| `utm_content` | placement and date or step: `dm-20261025`, `bio`, `story-20261025`, `step2-a` | `step2-a` |
| `utm_term` | test arm only | `x9-card` |

- **Meta ads** (seen in the GA4 export of 25 Oct, `numbers-2026-10-25.md` section 5): eight spellings of the source (`facebook`, `fb`, `meta`, `ig`, `an`, `facebook-SiteLink`, `fb-SiteLink`, `th`), and some ads put Meta's placement (`Facebook_Mobile_Feed`, `Instagram_Reels`) in `utm_medium`, which GA4 files as Organic Social (1,441 sessions, more than half of that channel). Give every ad the same URL parameters line: `utm_source=facebook&utm_medium=paid-social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{placement}}` (for ads only, `utm_term` holds the placement; confirm the dynamic parameter names in Ads Manager's URL parameter builder). Map `fb`, `ig`, `meta` and `an` with a `paid` medium to Paid Social in the weekly export until old ads stop.
- Keep the carousel link maker as is for October (its data is already logged) and move the placement from `utm_medium` into `utm_content` from November, recording the date of the change.
- Map `ig` to `instagram` in reporting (a GA4 custom channel group or a rule in the weekly export) instead of fighting Instagram's own tags.
- **CRM links** carry `utm_source=whatsapp|sms|email&utm_medium=crm&utm_campaign=<flow id>&utm_content=<step>-<variant>`. These links open private pages; the redaction rule above applies.
- **Creator links** stay on the ambassador link with UTMs appended, once Yossi confirms the link keeps extra parameters (open question in `research/creator-content-conversion/report.md`).

## 5. Matching people, messages and orders

- **Join key:** the order ID, and a stable person ID in the store (the verified phone lives only there). Never join in GA4.
- **Message log fields needed per send:** person ID, order ID (if any), flow ID, step, variant, holdout flag, channel, template name, sent time, delivered, read (if the channel reports it), replied, opted out.
- **Holdout flag** is assigned once per person per flow, at random, before the first message, and stored.
- **Test orders:** mark at creation when the child or parent name matches `test_name_pattern` in `shared/facts.json` (`בדיקה|test|Yarin Bruner`) or the phone belongs to the team; exclude from every report and every CRM flow. Add a GA4 internal-traffic rule for the team's devices.
- **Refunds and cancellations** reduce revenue in the month they happen; report gross and net.

## 6. Attribution windows and limits

- GA4 key events default to a 90-day lookback (30 days for first visit), and the first click, linear, time decay and position-based models were retired in November 2023 (https://support.google.com/analytics/answer/10597962). GA4's default model is data-driven, which at LumeBook's volume behaves close to last click; read it as a hint, not a measure.
- Ambassador credit: 7 days, printed books only (store settings, 14 Oct). QR ₪99 offer: 7 days, same browser (`/offers/g10-99`).
- CRM windows (proposed, for reporting only): payment-step reminder 72 hours; preview reminder 7 days; win-back 14 days. Incrementality comes from the holdout, not from the window (section 8).
- Known blind spots: visitors who decline analytics cookies (no UTMs in GA4 or Mixpanel; the store's own attribution may also be consent-gated), Instagram's in-app browser and device switches, gift buyers who return weeks later, and organic spill-over from posts seen but not clicked.

## 7. KPI definitions

| KPI | Numerator | Denominator | Source | Frequency |
|---|---|---|---|---|
| Book start rate | sessions with `wizard_step_viewed` step 1 | sessions (consenting) | GA4 | weekly |
| Wizard completion | books reaching `preview_ready` | books starting step 1 | store DB | weekly |
| Preview to payment | books with `begin_checkout` | books with `preview_ready` | store DB | weekly |
| Payment completion | paid orders | orders reaching CardCom | store DB + CardCom | weekly |
| Purchase conversion (person) | people who paid within 7 days of first book | people who started a book | store DB (the admin's 21.7% definition) | monthly |
| Revenue per visitor | net revenue | sessions (GA4) or unique visitors | store DB ÷ GA4 | monthly, directional |
| Contribution per order | net revenue minus print, shipping, payment fees, generation, discounts, commissions, message fees | paid orders | store DB + cost inputs | monthly once costs are known |
| Contribution per visitor | total contribution | sessions | as above | monthly |
| Repeat purchase by cohort | buyers of month M with a second paid order within 30, 90, 180 days | buyers of month M | store DB | monthly |
| Second book within 24 hours | orders using the ₪79 offer | first orders | store DB | weekly |
| Approval lag | median days from payment to `book_approved_for_print` | paid printed orders | store DB | weekly |
| On-time delivery | orders delivered by the promised date | delivered orders | courier data | monthly |
| CRM opt-out rate | STOP replies + preference turn-offs | people messaged | message log | per flow, monthly |
| Complaints | complaints tagged in support or Meta quality warnings | people messaged | support log, WhatsApp Manager | monthly |
| Incremental CRM contribution | (purchase rate treated − purchase rate holdout) × eligible people × contribution per order − message and discount costs | per flow and pooled | message log + store DB | quarterly |

## 8. Incrementality: how to count what CRM really adds

- A purchase that follows a message is not necessarily caused by it. The admin's "purchases after a message" table (12 Oct readout) counts both.
- **Per-flow holdout:** a random share (10 to 20%) of eligible people get no message from that flow. Extra sales = (rate in treated − rate in holdout) × treated people.
- **Global holdout:** a random 10% of people get no marketing flows at all for a quarter (service messages continue). This is the only way to see CRM's total effect, including overlap between flows.
- **Low volume:** with about 150 eligible people a month in a flow, per-flow results stay uncertain for many months (`experiments.md`, section 1). Report the difference with its range, pool flows that share a goal, and decide on direction plus cost, not on a single month.
- **Discounts:** count the discount given to people who would have bought anyway as a cost. A coupon flow can raise purchases and still lower contribution.

## 9. Weekly validation routine (15 minutes, Yarin or Yossi)

1. Store paid orders vs GA4 `purchase` count vs Meta purchases for the same 7 days. Investigate when the ratio between them moves, not against a fixed target.
2. Share of orders with a non-empty `acquisitionAttribution.utm_source`. A drop means links or consent broke.
3. Any `purchase` without `transaction_id`, or two with the same ID.
4. GA4 traffic from `cardcom` as a referral (should be zero after the exclusion).
5. Spot-check five GA4 page paths for order IDs, tokens or names.
6. Message log: sends per flow, opt-outs, holdout share still near its setting.
