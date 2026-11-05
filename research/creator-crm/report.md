# A creator CRM for LumeBook: research, design and plan

Written 19 Oct 2026 for Yarin. Research and design only: nothing was built, the creator map and its data were not changed, nothing was republished or committed.

How to read the labels: **verified** means the source was opened and says it; **vendor claim** means a company says it about itself or its market; **inference** means it is my reading. Codes in square brackets, like [G1], point to `sources.md`. Repository files are cited by path and line.

---

## Summary in plain words

**What we have.** The creator map is good at the first half of the job. It holds 343 vetted creators, drafts a personal Hebrew message for each one (with their kids and the right moment), checks the grammar and the offer wording, learns Yarin's voice from edits, and times follow-ups. Yarin has used it to message 242 creators since 4 Oct.

**Where it stops.** Everything after the first message is almost empty in the live records:

- 0 follow-ups are recorded as sent, so about 102 creators show as "Follow-up due".
- None of the 74 declines has a reason.
- There are 0 next actions, 0 personal links, 0 sales numbers and 0 notes.
- The map has no place for the deal itself: what was agreed, the book, the shipping, the video due date, the posted link, the results.
- The dashboard and the CSV still show zero outreach, because only the map knows.

**What the research says.**

1. Plan for about half of agreed creators to post (vendor claims [G1][G2]).
2. Creators like barter least of all deal types: 2.4 out of 5, against 4.2 for no-strings gifts (vendor claim [G1]).
3. Ask first and ship only after a written yes (advice from several vendors, never measured [G4][G7][G11]).
4. A cold Instagram DM can sit unseen in the Requests folder, so silence is not a no (verified [M3]).
5. Even paid creator tools leave status changes manual (verified [T8]), and no creator tool documents Hebrew [T1 to T16].
6. LumeBook's own store already runs a personal-link programme that credits printed books per creator (`research/creator-content-conversion/report.md:517`). Nobody reads its data yet.

**What to change, in order.**

1. **A "Today" screen.** One short list on the phone: deals with dates, "did they answer?" with one tap per creator, follow-ups due, results to read, new creators to contact.
2. **Track the deal.** Agreed terms saved as they were on the day of the yes, then book ordered, book delivered, video due, posted. Creator books for Hanukkah are due 10 Nov (`shared/facts.json`).
3. **Results per creator from the store.** Enrol each agreed creator in the store's ambassador programme, get a weekly per-creator export from Yossi, add the cost of the book and shipping, decide who to repeat.
4. **Never lose an edit.** A history line for every tap, retries when the connection drops, a weekly backup.
5. **Outreach rules.** A channel rule pending a lawyer's check, a daily send limit, honest test sizes.

**What Yarin needs to decide** is in section 6.3. The two most urgent: whether follow-ups were sent without pressing the button, and the default time from book delivery to video.

---

## 1. How this was made

- **Step 1** (the tool today) comes from the code in `creators/creator-research/src/`, one read-only export of the map's live database (261 outreach records, 19 Oct 2026), the dashboard's `tracker/state` document, the creators CSV, and a look at the built page at phone width in the built-in browser.
- **Step 2** (research) was split between three research assistants working inside this session, each with a source list and a search cap. 98 of the shared budget of about 200 searches were used. I re-read 8 of their key sources myself (marked "checked" in `sources.md`), and read 2 Instagram help pages directly.
- **Steps 3 to 5** are my synthesis. Where evidence ran out, the text says so.
- Not touched: DMs, email, the creator map's source, its data, its artifact or its scheduled task.

---

## 2. The tool we have today

Read from the code on 19 Oct 2026. File references are to `creators/creator-research/src/` unless another path is given.

### 2.1 What it is

The creator map is one HTML page. `build2.py` fills `template.html` with the research data and writes `lumebook-creator-map.html`, which is published as https://claude.ai/artifact/DCJ2ZT1Y4K8MrcH5bot2Hj.

Two kinds of data live in two places:

| Data | Where | How it changes |
|---|---|---|
| Research record: 343 creators with 22 fields each (`C_all.json`), kids for 164 (`kids.json`), a public email or phone for 90 (`contacts.json`: 34 emails, 78 phones) | Baked into the page at build time | A Claude session edits the JSON, runs `build2.py`, republishes |
| Outreach record: status, dates, channel, edited messages, notes | The artifact database: `outreach/<handle>` (one document per creator), `settings/main` (sender, preview link, saved templates, saved views, tests), `voice/main` (learned voice) | Yarin, on the page; saved at once |

Outside claude.ai (a local preview, a file) the page cannot reach the database. It then says "Saved in this browser only" and keeps everything in `localStorage` (`template.html:951`, `:1699`).

### 2.2 Statuses and steps

There are five stored statuses, plus two that the page works out from dates (`template.html:530`, `:843`, `:852`):

```
Not contacted --Mark sent--> Message sent --4 days, no follow-up recorded--> Follow-up due (worked out)
                                  |                                              | "Follow-up sent"
                                  |                                              v
                                  |                       sequence finished + 7 days --> No reply (worked out)
                                  '-- Yarin picks --> In process --> Declined
                                                      steps: Info sent, Follow-up sent, They signed,
                                                             Book created, Book sent, Content created
```

What moves a creator:

- **Mark sent** (`template.html:1165`) saves the status, the date, the channel, the track, the style, whether the text was hand-edited, and a copy of the text as sent.
- **Follow-up due** is never stored. It appears 4 days after the send (`FU1_MS`, `:824`) until **Follow-up sent** is pressed (`:1169`). A final follow-up is optional, planned per creator, and due 7 days after the first one (`FU2_MS`).
- **No reply** appears 7 days after the last follow-up. A creator with no recorded follow-up never reaches No reply; they stay in Follow-up due.
- **In process**, its step, and **Declined** are picked by hand from a menu, or with the X on the card.
- **In process with no change for 30 days reads as Declined** (`STALE_MS`, `:830`), unless the book was already sent. Picking a status again restarts the clock.
- The weekly refresh never changes a status (`refresh/README.md:15`).

### 2.3 Follow-ups: timing and display

- First follow-up at day 4, an optional final one 7 days later, then stop. The follow-up template is written to "add something, no nudge" (`template.html:1221`).
- Shown as a chip on the card (orange, red from 3 days overdue), as a count in the sidebar, and as the top 6 on the Overview page (`:1569`). When a follow-up is due, the card opens on the follow-up message.

### 2.4 What is stored per creator

- **Research record** (baked in):
  - who: handle, name, platform, language, city, archetype, role, child ages, topics, content roles
  - numbers: followers, median reel views, last reel date
  - judgement: a practicality estimate, a brand-conflict note, ten sub-scores of 1 to 5 and a total score, a content concept, a risk note, a contact note
- **Outreach record** (database). All fields are optional except the status:
  - the send: date and time, channel, track at send, style, the text as sent
  - follow-up dates, reply time
  - the deal so far: step, next action and its date, an "interested" tick, the reason for a no (8 fixed reasons), their reply in their own words, a note on the reason
  - the personal link, a sales number typed by hand, free notes
  - overrides for the greeting name, the personal line and the kids
  - the track, a test label, and every edited message per type, track and style
- **Stored nowhere:**
  - what was agreed (book title, the child's name for the book, video type, due date)
  - shipping date, when content went live, its link and its numbers
  - usage rights and consent
  - the cost of the book and shipping
  - link clicks or orders from the store

### 2.5 How messages are written, edited and learned from

- **Message types:** six (first message, email, follow-up, final follow-up, interested reply, offer details), in three tracks (General, Professionals, Parents) and two styles (Warm, Short). The offer numbers come from `shared/facts.json` at build time (`build2.py:14`).
- **Filling:** each message gets the creator's name, a personal line, a "moment" (weaning, new sibling, starting gan), and the kids' names and genders where known. Hebrew grammar fixes are applied (`template.html:917`).
- **Checks:** a Hebrew check and an offer check run under the box (`:1264`, `:1283`).
- **Sending:** copy and paste for Instagram. WhatsApp and email open pre-filled through `wa.me` and `mailto:` links (`:946`). The suggested first channel is WhatsApp when a public phone exists, then email, then Instagram DM (`:879`).
- **Voice learning** (`:1379` to `:1422`): when Yarin edits a message and leaves the box, the page asks Claude (the `sample` capability) to do two things. It rewrites that creator's other messages to match, and it updates the track's templates and up to 12 voice rules. A "fingerprint" of the offer facts (percentages, link, video ask, gift, price, earnings) blocks any rewrite that changes the offer (`factSig`, `:1323`). The last learning can be undone.
- **Tests** (`:1577`): two versions of the first message, assigned at random in matched pairs and compared on replies by day 7. These are drafts and labels only; nothing is sent.

### 2.6 The weekly refresh

`refresh/README.md` and `refresh/refresh.py` re-read each public Instagram profile and flag:

- never-contacted creators now under 5K or over 50K followers
- no reel for 60 days
- followers up or down 25%
- a private account
- a profile that did not load
- a reel naming LumeBook since the first message

Running it needs a signed-in browser tab, a pasted script run about 17 times, a clipboard copy, a database export, two commands and a republish. The scheduled task `lumebook-creator-refresh` (Sundays 10:07) is enabled and next due 25 Oct 2026. It has not run yet: there is no `refresh/latest.json` and no last-run time.

### 2.7 What is done by hand today

| Job | Who | The tool's part |
|---|---|---|
| Finding creators | Claude sessions, 4 research passes | Shows the result |
| Writing the message | The page drafts, Yarin edits | Drafts, checks, learns |
| Sending | Yarin, in Instagram, WhatsApp or email | Copy button, pre-filled links |
| Noticing a reply | Yarin, in Instagram, WhatsApp or email | Nothing (fixed by decision) |
| Recording the reply, the reason, the next step | Yarin, with menus and fields | The fields exist |
| Personal link, shipping, posting date, sales | Yarin, by hand, if at all | One link field and one sales number |
| Refresh | A Claude session, about 8 manual steps | Flags on the card |

### 2.8 What the live records show (19 Oct 2026, internal)

- 242 of 343 creators were contacted between 4 and 19 Oct. 37 messages went out on 19 Oct alone.
- Stored status: 145 Message sent, 8 Follow-up due, 15 In process (12 Info sent, 3 Book sent), 74 Declined. Content created: 0.
- Of the 91 creators messaged 7 or more days ago, 29 answered (32%), and 15 of those are in process (16%).
- The channel was recorded for 101 sends since 11 Oct: 79 Instagram DM, 19 WhatsApp, 3 email.
- One message test is running, with 34 creators.
- **Fields after the first message are almost empty:**
  - 0 follow-ups recorded as sent
  - 0 reasons for the 74 declines, 0 replies pasted
  - 0 next actions, 0 interested ticks
  - 0 personal links, 0 sales numbers
  - 0 notes, 1 kids correction
- Because no follow-up is recorded, about 102 creators show as Follow-up due right now, and the No reply list is empty.
- Elsewhere, the dashboard's `tracker/state` has `creators: {}` and `outreach: 0`. The 343-row creators CSV has empty `status`, `sent_on` and `promo_code` columns. Only the map knows the real state.

My reading (inference): the first-contact half of the tool is used every day; the half after a reply is not used at all. Either that part lives in Yarin's memory and in the chats themselves, or filling it costs more taps than it gives back. Section 6.3 asks which.

### 2.9 What the tool cannot do, or does badly

**Limits of the setup** (one published page, a small database, one person, manual sending):

1. **The research record is frozen into the page.** Adding a creator or correcting a number needs a Claude session, a rebuild and a republish.
2. **Saving only works inside claude.ai.** Anywhere else, edits stay in that browser and never reach the database (`template.html:1702`).
3. **A failed save is not retried.** If a write fails (a dropped connection on a bus, for example), the page shows "Couldn't save the last change" and keeps the change only in memory. A reload loses it (`template.html:957`).
4. **No history.** Each change overwrites the creator's whole document. Undo covers the last action, for 6 seconds. There is no record of who said what, when.
5. **The page never knows a reply came in.** Sending and reading stay manual by decision, so every reply must be recorded by hand, and nothing prompts Yarin to do it.
6. **Platform caps:** a document holds at most 256 KiB and a view at most 64 live subscriptions. The caps on documents per collection and on database size exist but their numbers are not stated (runtime type definitions, `db.d.ts`, contract 0.2.85). Fine at 343 creators.
7. **The refresh is long and manual,** and has not run yet.
8. **Phone use is heavy.** At 375 px wide there is no sideways scroll. But one card is about 976 px tall with 15 buttons, and the first card starts below the fold (checked in the built-in browser on the static copy, 19 Oct). The labels are English; the messages are Hebrew, right to left.
9. **Four other places hold creator status, and they disagree:** the CSV, the dashboard tracker, the old Drive tracker and the signup Form sheet.

**Missing features:**

1. No single "today" list. Follow-ups, next actions and content due sit in three short lists on the Overview, and the 102 due follow-ups bury the rest.
2. No record of the deal: what was agreed, which book, when it shipped, when the video is due, usage rights, consent.
3. No content tracking after the book is sent: posted or not, link, views.
4. No results: no link to the store's ambassador data, no orders per creator, no cost per creator.
5. No quick "they answered" action that stops follow-ups and logs the time without choosing a full status.
6. No stage after content: repeat, keep as an ambassador, or do not work with again.
7. Nothing is learned about the creator from working with them (on time, quality, would repeat).
8. Form signups are not in the map.
9. The 30-day auto-decline hides stalled deals instead of showing them.

---

## 3. What the research found

### 3.1 Creator relationship tools

- **The shared pipeline.** Across vendors, the stages are: shortlist, contacted, negotiating, agreed, shipped and delivered, posted, results, then ended or declined (inference from [T4][T5][T7][T8][T14][T28][T29]).
  - Modash's defaults are Shortlisted, Contacted, Active, Ended, Blocked (verified, checked [T8]).
  - Aspire's gifting flow is the clearest: welcome, brief, the creator types their own shipping address, link or code, fulfilment, content, payment, with optional contract and post tracking (verified [T5]).
  - Shopify Collabs tracks each gift as sent, redeemed, fulfilled or canceled (verified [T14]).
- **Shipping and content are often sub-steps of one "active" stage,** not top-level stages (inference from [T5][T8][T14]).
- **Statuses stay manual even in paid tools.** Modash's help centre: "Status updates are currently manual" (verified, checked [T8]). The automatic statuses in Upfluence, HypeAuditor and GRIN depend on email or inbox activity (vendor claims [T4][T6][T7]), which LumeBook has ruled out.
- **What can be automated without an inbox** (inference from [T5][T7][T12][T16]):
  - a creator-filled address form
  - watching public posts (HypeAuditor says Instagram Stories are not tracked that way, vendor claim [T7])
  - a link that applies the discount at checkout (verified for GoAffPro [T16])
  - shipping status from the store
- **GRIN "locks" deal terms once the creator accepts** (vendor claim [T4]). Modash keeps an activity timeline of status changes (verified [T8]).
- **Price:** platforms that publish prices start at $199 a month (Modash Essentials) to $500 a month (GRIN Growth, Insense Brand), with the currency code not named (verified, 19 Oct 2026, [T4][T8][T11]). Several do not publish prices at all [T1][T2][T3][T5][T6][T12][T13]. Free tiers exist with small caps [T4][T7][T10]. Details are in `tools-compared.md`.
- **Hebrew:** no influencer tool reviewed documents Hebrew or right-to-left [T1 to T16].

### 3.2 Gifting, seeding and ambassador programmes

- **Post rates are about half, at best.**
  - Creators told Modash they post about half of the gifted products they accept, under barter and no-strings deals alike (vendor claim, 25 creator interviews plus a poll of unstated size, checked [G1]).
  - Modash's survey of 74 marketers: 50% for barter against 43.8% for no-strings gifting (vendor claim; the base is unclear [G2]).
  - GRIN says 20% to 40% for well-run programmes, 50% or more when gifting existing customers (vendor claim, no sample [G3]).
- **Barter is the least-liked deal.** Creators rated barter 2.4 out of 5 and no-strings gifting 4.2 (vendor claim, checked [G1]). Over 80% say barter brands ask for video as well as Stories, and creators see video as too much for a gift (vendor claim [G1]). LumeBook asks for one video, so the full value (a personalised book plus the 25% link) has to be clear from the first message (inference).
- **What goes wrong** (all vendor claims):
  - no answer: the second biggest barrier for 43.2% of 74 marketers [G2]
  - ghosting after the gift: 90.5% say it happens more with gifting [G2]
  - pressure: aggressive brand communication is the third most cited reason creators do not post [G1]
  - no contract: nearly half of marketers use none [G2]
  - usage rights: 4 in 10 creators grant them only if paid [G1]
  - lost parcels [G4]
- **What fixes it** (all vendor claims, none measured):
  - ask first and ship after a yes [G4][G7][G11]
  - choose people who already know the brand: existing customers post 2 to 3 times more [G3]
  - a short written agreement with honest intent [G1][G4]
  - a light brief, not a script [G3][G10]
  - a delivery check and a few check-ins after delivery: GRIN suggests day 0 to 1, day 3 to 5 and day 7 to 10 [G3]; 74.3% of 74 marketers follow up two or three times after delivery [G2]
  - tracking each unit through approved, shipped, delivered, posted [G10][T14]
- **Ambassador programmes:** over a third of marketers say fewer than 20% of their affiliates post at least once a month (vendor claim [AF1]). Top programmes recruit customers first and give a low-effort first task (vendor claim [AF2]).

### 3.3 Lightweight CRMs and what people actually use

- **No study measures which features solo users keep and which they drop.** The best numbers are vendor-run surveys of small businesses. In a survey of more than 1,500 US small businesses commissioned by Zoho, ease of use was the top reason to choose a CRM (53%), and 39% of non-users run on spreadsheets and email (verified that the release says so, vendor-commissioned [F1]). The often-quoted "43% use less than half the features" has no traceable source [F6].
- **Practitioners keep returning to four fields:** stage, next action, next date, note (opinion and anecdote [F8][F9]). One freelancer's lesson is that tools are dropped because the person stops going back to them, not because a feature is missing (anecdote [F10]).
- **Hebrew in general tools:**
  - Only Google Sheets [RTL1] and Notion [RTL2] document right-to-left for the content a CRM would hold (verified).
  - Airtable shows Hebrew left to right and has no Hebrew interface (verified, checked [RTL4]).
  - Trello's right-to-left request is still open (verified [RTL7]).
  - HubSpot has no Hebrew interface (verified [RTL8]).
  - monday.com documents right-to-left for forms only (verified [RTL5]).
  - Notion downloads only the first 50 rows of a database for offline use (verified [T20]).

### 3.4 Outreach practice: replies and follow-ups

- **Creator-specific reply data with a stated sample does not exist** in what was found. The ranges that circulate (5% to 15% cold, 20% to 40% warm) are unsourced vendor figures [C3][C4]. LumeBook's own number is the benchmark: 32% of creators messaged 7 or more days ago answered (section 2.8).
- **Follow-up count.** 72% of 51 creator marketers send 1 or 2 follow-ups (vendor claim [C1]). In B2B email (a different audience): 2 to 3 follow-ups are best [E3], replies keep coming from later steps [E2][E5], and unsubscribes rise after the third [E6] (all vendor claims). The map's current cadence (one follow-up, an optional final one) sits inside that range (inference).
- **Length.** In B2B email, top performers keep first emails under 80 words [E2], and replies drop above 100 words [E7] (vendor claims, not creators).
- **Instagram DM rules** (all verified on Meta's pages):
  - A DM to someone who does not follow you may arrive as a message request [M1].
  - A request can only hold text, and the recipient can choose not to receive requests at all [M2].
  - In professional accounts, requests sit in their own folder and are not marked "seen" until accepted [M3].
  - Sending too many messages can lead to a warning and then a block on sending DMs, with no number published [M4].
  - Spam filters can hide requests [M5][M6].
  - Accounts run by adults that mainly feature children get the strictest message settings (verified, Meta post [P10]). Some parent creators may never see a cold DM (inference).
- **WhatsApp.** WhatsApp's business policy requires the person's opt-in before a business contacts them, and this covers the WhatsApp Business app (verified, checked [W1]). The policy does not cover personal accounts. For all users, repeated unwanted contact counts as spam (verified [W2]).

### 3.5 Israeli context

- **Channels:** WhatsApp is used by 99% and Instagram by 82% of respondents in the Israel Internet Association's May 2026 survey (1,040 people, run by Geocartography; verified in a news report, checked [IL1]). The base population is not stated.
- **Creator norms on pay and barter:** no Israeli source with numbers on barter for micro-creators was found. A pricing guide by an influencer platform puts micro-creator deals "between hundreds and thousands of shekels" (vendor claim, reported 12 Oct 2026 [N1]). In LumeBook's own research, 0 of 469 recent posts by 41 parent and professional creators carried the paid-partnership label, and personal codes were common (`research/creator-content-conversion/evidence.md:133`).
- **Disclosure:**
  - The Consumer Protection Law counts "any other benefit" as making content an advertisement, so a free book counts (verified, unofficial statute copy [D4]).
  - The Attorney General's 2020 position says a tag or hashtag is not enough: the post must say at its opening that it is an advertisement or sponsored, and the rule applies with extra force where minors are in the audience (verified, primary gov.il document [D5]).
  - A 2021 draft directive adds that an incentive must not depend on a positive review (verified as a draft; final status unknown [D6]).
  - Instagram's own policy counts free gifts as branded content that needs the paid-partnership label (verified, read directly [D11]).
  - **Useful side effect:** once a creator tags LumeBook with the label, LumeBook gets a notification and the post's insights (verified, read directly [D10]).
- **Privacy** (law text from an unofficial copy [P1][P2], law-firm summaries [P3][P4]; not legal advice):
  - **High confidence:** the creator CRM does not need registration. Registration is now only for databases that sell data to others above 10,000 people, and for public bodies (checked [P1]).
  - **Medium confidence:** it is a "database" under the law. Kids and notes take it beyond the contact-only exclusion (checked [P1]). The security duty therefore applies, most likely at the lightest "managed by an individual" level or at basic [P2].
  - **When Yarin asks a creator for a phone number or an address,** that message should say what it is for, who receives it, and that giving it is voluntary (section 11 [P1]).
  - **Open, low to medium confidence:**
    - whether sending the same pitch to creators filtered by a trait counts as "direct mailing" [P1][P3]
    - whether the number of kids or free notes count as sensitive "family privacy" data [P1]
    - whether the anti-spam rule (up to ₪1,000 per message, verified only in a secondary source [P5]) covers a first collaboration pitch by email, SMS or WhatsApp; a one-time offer to a business may be allowed (law-firm summary [P6])
  - **Kids' names:** a consumer protection regulation forbids an advertiser to use a minor's name or contact details without a parent's consent, except to deliver a product (verified, unofficial copy [P8]). Whether this covers using a child's name, taken from a parent's public bio, in a message to that parent is not clear (inference).
- **Children on camera:** employing a child under 15 in advertising filming needs a Labour Ministry permit (verified on a secondary legal site [P9]). Whether a parent filming their own child at home for a barter post counts as employment was not addressed by any source.

### 3.6 Measuring results with no tracking budget

- **The store already captures attribution** (from its public code, read 14 Oct 2026):
  - UTM tags, click IDs and the landing page as first and last touch, sent with every new book, but only after the visitor accepts analytics cookies (`research/creator-content-conversion/report.md:514`, `:515`)
  - a personal-link ambassador programme: ₪30 per printed book split between follower discount and commission, 7-day link memory, 14-day hold, a dashboard per ambassador, payouts by bit, PayBox or site credit (`report.md:517`)
- **What is missing** is a per-link, per-creator report in the admin (`docs/lumebook-sales-data-decisions-2026-10-12.md:37`). Also unknown: whether any map creator is enrolled, and how ₪30 relates to the 25% in `shared/facts.json` (`report.md:517`).
- **Link tracking misses sales** that happen on another device, after the link's memory ends, or through forwarded links in chats (vendor claims [U7][U10][U12]; no independent size found).
- **The cheapest check on the gap** is one question after purchase, "where did you hear about us?", compared with link-credited orders (method suggested by a survey vendor [U12]). The store already sends a WhatsApp message after purchase (`docs/lumebook-sales-data-decisions-2026-10-12.md:133`).
- **Keep three counts apart and never add them:** store orders, ambassador-credited orders, and Meta-reported purchases (`report.md:549`).

---

## 4. What the tool needs

Each requirement says why it matters here, the evidence, and whether today's map meets it: **fully**, **partly** or **not**.

### 4.1 Pipeline

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R1 | Stages that cover a barter deal end to end: to contact, contacted, talking, agreed, book on its way, video due, posted, results, done. Exits: declined, silent, not now, dropped | The map stops at "Content created". Hanukkah books are due 10 Nov | Shared vendor pipeline [T5][T8][T14] (inference) | Partly |
| R2 | Each stage asks for one thing only, the fact that proves it | Fields after the first message are 0% filled (2.8) | Ease of use is the top selection factor [F1]; practitioners keep 4 fields [F8][F9] | Partly |
| R3 | No book is ordered before a written yes is saved | Barter is the least-liked deal; creators who chose post more consistently | [G1][G2][G4][G7] (vendor) | Not |
| R4 | "Silent" is its own state, never read as a no | Cold DMs can sit unseen in Requests | [M2][M3] (verified) | Partly: exists, never reached |
| R5 | Stalled deals are shown, not auto-declined | The 30-day auto-decline hides them (`template.html:830`) | Inference | Not |

### 4.2 Per-creator record

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R6 | Followers, views, last reel and "posted about LumeBook" fill in by themselves | Numbers drift; posting is the main proof | Watching public posts needs no inbox [T12][T7] | Partly: built, not run yet |
| R7 | Keep the deal: book title, child's first name for the book, deliverable, posting window, link split, personal link, ordered, sent and delivered dates | None of it is stored now | Vendor deal records [T4][T5] | Not (link field only) |
| R8 | Leave out: home address (it stays in the store order), child photos, DM text, ID numbers, payout details | Less personal data means less risk | Section 11 duty and security duty [P1][P2] | Fully today (none stored) |
| R9 | A dated line for every touch: who said what, in a few words | "Keep track of who said what" is in the brief | Modash timeline [T8] | Not |

### 4.3 Contact and follow-up

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R10 | One "today" list, ranked, on the phone | 102 follow-ups due bury everything else | People drop tools they do not return to [F10] (anecdote) | Partly |
| R11 | Outreach cap: first message plus at most 2 follow-ups, each adding something. After delivery: confirm, ask about the book, one content nudge, stop | Pressure makes creators not post | [C1][E3][E6][G1][G2][G3] (vendor) | Fully for outreach; not after delivery |
| R12 | A channel rule and a channel switch: start where it is allowed and likely to be seen; if a DM stays silent, try the creator's published business email | DM requests can be hidden; WhatsApp business policy needs opt-in; anti-spam law unclear | [M2][M3][W1][P5][P6] | Partly: WhatsApp is the default first channel |
| R13 | One tap to record an answer: yes, question, not now, no (reason optional) | 0 reasons, 0 replies recorded | Inference | Partly |
| R14 | A daily send limit Yarin sets | 37 sent on 19 Oct; Instagram blocks heavy senders with no number given | [M4] (verified) | Not |
| R15 | Copying a follow-up counts as sending it, with undo | 0 follow-ups recorded | Inference | Not |

### 4.4 Messages

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R16 | Templates plus a personal line plus learned voice, with the offer locked | Personal messages at volume without writing each one | No reviewed tool has this [T1 to T27] | Fully |
| R17 | The version sent is recorded, and reply rates show their sample size honestly | Tests of 17 per version cannot tell 16% from 32% apart: about 110 per version are needed for that (inference, standard two-proportion sample size at 95% confidence and 80% power) | Statistics; [E1 to E6] for why versions matter | Partly |
| R18 | First message short and text only, ending with one question | DM requests are text only; short messages do better in B2B email | [M2] (verified); [E2][E7] (vendor, B2B) | Fully |

### 4.5 Terms and deliverables

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R19 | The agreement saved as it was on the day of the yes: offer version, deliverable, window, split, usage scope, disclosure line, consent | Nearly half of marketers have no contract; terms then drift | [G2] (vendor); GRIN locks terms [T4] | Not |
| R20 | Usage rights default to "repost on LumeBook with credit"; ads or raw footage only if agreed separately | 4 in 10 creators grant rights only if paid; the brief asks for raw footage without saying what it is for | [G1] (vendor); `research/israeli-product-reels/creator-brief.md:35` | Not |
| R21 | Disclosure and paid-partnership label checked when the post goes up | Required by Israeli law and Instagram policy, and the label gives LumeBook the insights | [D4][D5][D10][D11] (verified) | Not |
| R22 | Due dates and a "stuck" view: book not ordered, not delivered, video overdue | Hanukkah deadline; about half will not post | [G1][G2][G3] | Not |

### 4.6 Results

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R23 | Per creator: post link, views at day 7, orders through the personal link, cost of book and shipping, cost per order | To know who is worth repeating | Store programme (`report.md:517`); label insights [D10] | Partly (one sales field, never filled) |
| R24 | Store orders, link-credited orders and Meta purchases kept apart | They overlap and mislead if added | `report.md:549` | Not |
| R25 | A repeat decision per creator: repeat, maybe, no | Top programmes keep working with proven people | [AF2] (vendor) | Not |
| R26 | A rough check on what links miss: one "where did you hear about us?" question after purchase | Links miss cross-device and later buys | [U12] (vendor method); store already messages buyers | Not |

### 4.7 Creator quality

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R27 | Fit signals kept fresh: archetype, kids' ages, recent reels, views per follower, buying-signal history | Professionals drew 3.8 purchase-intent comments per 100 against 1.1 for parents in LumeBook's own data | `research/creator-content-conversion/report.md:15` | Partly (score is static) |
| R28 | Reliability learned from working together: answered, agreed, posted on time, content usable | The best predictor of the next deal is the last one (inference) | [AF2][G3] (vendor) | Not |
| R29 | Risk flags block outreach: competitor link, sensitive account, "no collabs" bio | Already a rule (MeBook conflict) | `build2.py:60` exclusions | Fully |
| R30 | A "knows LumeBook" mark: customer, follower, has engaged | Existing customers post 2 to 3 times more | [G3][AF2] (vendor) | Not |

### 4.8 Risk and consent

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R31 | Store only what has a use; delete or blank contact data of creators who said no after a set time | Database duties apply; fines exist | [P1][P3][P4] | Not |
| R32 | When asking for a phone or address, the message says why, who gets it, and that it is voluntary | Section 11 | [P1] | Not |
| R33 | A consent record: the parent agrees to the child in the video and to LumeBook reposting it, with an easy takedown | The collab post also shows on LumeBook's account | `creator-brief.md` open item 8; [D5] | Not |
| R34 | Kids' names used only as the law allows | Regulation 7A on minors' details | [P8] (unclear reach) | Unclear |

### 4.9 Everyday use

| ID | Requirement | Why here | Evidence | Today |
|---|---|---|---|---|
| R35 | Phone first: one row per task, two lines, big buttons; the full card one tap away | Cards are about 976 px tall now | Checked at 375 px (2.9) | Partly |
| R36 | Hebrew, right to left, for the daily screen | Messages are Hebrew; dashboard is Hebrew | Project rule (CLAUDE.md) | Partly (messages only) |
| R37 | Works on a bus: changes queue when offline and save on reconnect, with a visible count | A failed write is lost on reload today | `template.html:957` | Not |
| R38 | Undo for every action and a history to look back on | Mistaken taps on a phone | Inference | Partly (6-second undo) |
| R39 | One source of truth: the dashboard and the CSV read from the map | Four places disagree today (2.9) | Inference | Not |

### 4.10 What not to build

These look useful but would not pay off for one person with a ₪0 budget:

1. **Reading or sending DMs, email automation, inbox sync.** Ruled out by decision. Instagram also limits heavy senders [M4].
2. **A paid creator platform.** Published prices start around $199 a month, none documents Hebrew, and their best automations need the inbox [T4][T8][T11].
3. **More creator discovery.** 343 vetted creators are already mapped, with 101 not yet contacted.
4. **E-signatures and contracts.** A short agreement in the chat, saved in the CRM as text, is enough for a book-for-video deal (inference). A lawyer should still check the wording once.
5. **Commission payouts.** The store's ambassador dashboard already pays by bit, PayBox or credit (`report.md:517`).
6. **Story tracking.** Stories expire; tracking them needs paid listening tools [T12]. Ask for one screenshot, or rely on the label's insights [D10].
7. **More A/B testing machinery.** About 110 creators per version are needed to see a doubling; the map has 101 creators left to contact (inference).
8. **Predictive scores or AI ranking.** Too few deals to learn from; a simple reliability mark is enough.
9. **Reminders by email or push.** No email automation; the Today screen is the reminder.
10. **A media library inside the CRM.** Files belong in `media/projects/` and Drive (CLAUDE.md); store a link only.
11. **Moving to a new platform.** See 5.8: the move would cost the Hebrew messages and voice learning, which nothing else offers.
12. **Automatic status changes from guesses.** For example, the 30-day auto-decline: show stalled deals instead.

---

## 5. Design

### 5.1 Principles

1. **One screen a day.** Everything Yarin must do today is on one list, in order. The full creator card stays one tap away.
2. **One tap per fact.** Every stage asks for one fact, prefilled where possible. Free text is optional.
3. **The tool works out time.** Due dates, follow-ups and "stuck" are calculated, never typed.
4. **Nothing reads the inbox.** Answers are recorded by Yarin with one tap. Posts are found on public profiles. Sales come from the store.
5. **Nothing is lost.** Every tap is a line in the history, saved even when the connection drops.

### 5.2 Pipeline stages

| Stage | Means | Moves on when | Asks for | Set by |
|---|---|---|---|---|
| To contact | In the map, vetted, not messaged | First message sent | Nothing | |
| Contacted | First message out | An answer is recorded | Channel, version (automatic at Mark sent) | Tap |
| Silent | Follow-ups done, no answer. Not a no | An answer, or a revisit date | Nothing | Worked out |
| Talking | They answered and have not decided | Yes, no or not now | Optional one-line note | Tap |
| Not now | Timing | The revisit date passes, then back to Contacted | Revisit date (default 30 days) | Tap |
| Agreed | A written yes to the deal | Book ordered | Book title and the child's first name(s); the rest is prefilled from the offer | Tap + 2 fields |
| Book on its way | Ordered, then sent | Delivered | Dates, one tap each | Tap |
| Video due | Delivered, video not yet up | Posted | Due date, worked out as delivered + N days (Yarin sets N) | Worked out |
| Posted | Live | Results read | Link (suggested by the refresh, or pasted); disclosure and label ticks | Tap |
| Results | Read at day 7 and day 30 | A decision | Views and orders where available; cost from the offer facts | Mostly automatic |
| Done | Decided | | Repeat, maybe or no | Tap |
| Declined | Said no | | Reason (optional chip) | Tap |
| Dropped | Did not post after the nudges | | Nothing | Tap |

How it maps onto today's map: Message sent becomes Contacted; In process with Info sent becomes Talking; They signed becomes Agreed; Book created and Book sent become Book on its way; Content created becomes Posted. "Follow-up due" stays a flag on Contacted, not a stage. Video due, Results, Done, Silent, Not now and Dropped are new.

### 5.3 Data model

```
Creator ─────────< Touch            every message out and every answer in, one line each
   │
   └─────────────< Deal ─────────< Post       usually one deal, one post
                     │
                     └── Result                read at day 7 and day 30

Template version ──< Touch            which version of a message was sent
Offer facts (shared/facts.json) ── copied into the Deal at "Agreed", so later offer changes never rewrite an old deal
```

| Thing | Kept in | Filled automatically | Filled by hand |
|---|---|---|---|
| **Creator** | Research files (as today) plus `outreach/<handle>` for the current state | Followers, views, last reel, posted flag (refresh); kids from the research; track from the archetype | Corrections only |
| **Touch** | New: `log/<handle>/events/<id>` | Date, kind, channel, message version, text sent | A few words on what they said (optional) |
| **Deal** | New: `deals/<id>` | Offer version and split example (from facts), personal link (once enrolled), due date, cost per book and shipping (from facts) | Book title, child's first name(s), posting window if not the default; one tap for ordered, sent, delivered |
| **Post** | Inside the deal | Link and date (refresh suggests it); views at day 7 | Disclosure tick, label tick, "content usable" mark |
| **Result** | Inside the deal | Orders and revenue from the store export; cost per order | The repeat decision |
| **Settings** | `settings/main` (as today) | | Daily send limit, video window N, revisit default, channel rule |

Not kept: home address, child photos, DM text, payout details (R8).

### 5.4 The screen where Yarin spends each day

Phone width, Hebrew and right to left in the real page. Labels are in English here only so the sketch lines up.

```
+--------------------------------------+
| Today                  saved, 0 waiting|
| 14 to do                              |
+--------------------------------------+
| DEALS WITH A DATE                     |
| @handle  video due in 2 days          |
|          [Nudge]   [Posted]           |
| @handle  agreed 3 days ago            |
|          [Book ordered]               |
+--------------------------------------+
| DID THEY ANSWER?   sent 2 to 7 days ago|
| @handle  DM, 3 days                   |
| [Yes] [Question] [Not now] [No] [Not yet]|
| @handle  WhatsApp, 5 days             |
| [Yes] [Question] [Not now] [No] [Not yet]|
+--------------------------------------+
| FOLLOW-UPS DUE      3 of 9 (limit)    |
| @handle  first follow-up, day 5       |
|          [Copy = sent]                |
+--------------------------------------+
| RESULTS TO READ                       |
| @handle  posted 7 days ago  [Read]    |
+--------------------------------------+
| NEW TO CONTACT      0 of 15 today     |
| @handle  score 88, Professionals      |
|          [Open message]               |
+--------------------------------------+
```

- **Order:** deals first (a promised video is worth most), then answers (fast to clear), follow-ups, results, and new contacts last. New contacts are capped by the daily limit.
- **Tapping a handle** opens today's full card in a drawer (`lb-drawer`).
- **"Not yet"** keeps the creator on the list until the follow-up date. After the last follow-up the creator moves to Silent.

### 5.5 The four views that matter most

1. **Today** (above).
2. **Waiting on creators**: Contacted, Silent and Talking, grouped, with days since the last touch and the next planned touch. A Silent group with "try email" where a business email is public.
3. **Deals in motion**: one row per deal, from Agreed to Posted, with a stage bar (`lb-stages`) and the due date. A "stuck" filter: agreed with no book after 3 days, delivered with no post after N days, posted with no label tick.

   ```
   @handle   Agreed > Ordered > Delivered > [Video due 29 Oct] > Posted
   @handle   Agreed > [Book not ordered, 4 days]
   ```

4. **Results**: one row per finished deal: posted on time, views at day 7, link orders, cost, cost per order, and the decision. A short note under the table keeps store orders, link orders and Meta purchases apart, and shows each sample size.

   ```
   creator   posted   on time  views d7  link orders  cost     per order  decision
   @handle   24 Oct   yes      12.4K     3            ₪xx      ₪xx        repeat
   ```

   Cost needs the print cost from Yossi; until then it reads "unknown".

Research pages (database, archetypes, method) stay as they are, out of the daily path.

### 5.6 What to automate, what takes one tap, what stays manual

| Job | Mode | Why |
|---|---|---|
| Follow-up due dates, "stuck" deals, video due dates, the Today order | Automatic | Pure date arithmetic; nobody should type it |
| Followers, views, last reel, "posted about LumeBook" | Automatic (weekly refresh) | Public profiles, no inbox [T12] |
| Offer terms in a new deal | Automatic (copied from `shared/facts.json`) | Keeps the deal true to the offer of that day |
| Cost per deal | Automatic (book cost + shipping from facts) | Once Yossi gives the print cost |
| Link orders per creator | Automatic, weekly import of the store export | Only if Yossi can provide it (`report.md:519`) |
| A history line for every tap | Automatic | Costs nothing, gives "who said what" |
| Recording an answer | One tap | Only Yarin sees the chats |
| Follow-up sent | One tap (copying counts as sent, with undo) | Removes the step that is skipped today |
| Agreed, ordered, sent, delivered, posted | One tap each, prefilled | Yarin is the one who knows |
| Reminder texts (nudge, delivery check) | One tap to copy, drafted by the page | Same voice learning as today |
| Writing and sending messages | Manual | Fixed decision; Instagram limits heavy sending [M4] |
| Reading answers | Manual | Fixed decision |
| Who to contact, whether content is usable, the repeat decision | Manual | Judgement |
| Ordering the book in the store | Manual | The address stays in the store, not the CRM |

### 5.7 Look and behaviour

- **Design system:** `shared/design/lumebook.css`, inlined with `design.head()` as the map does now (`build2.py:94`). Light mode only. Heebo for text and headings; Assistant (`--font-2`) for labels, counts, chips and table headers.
- **Components first:**
  - `lb-card` for task rows
  - `lb-chip` for due and stage chips
  - `lb-btn` for actions
  - `lb-segmented` for the answer taps
  - `lb-stages` for the deal bar
  - `lb-drawer` for the creator card
  - `lb-toast` for undo
  - `lb-table` for results
  - `lb-stat` for the four counts at the top
  - `lb-empty` for an empty day
- **Colour:**
  - Due, overdue and done use the status tokens (`--warning`, `--danger`, `--success`), never category hues.
  - Tracks keep their existing category set (`creator-tracks` in `shared/design/categories.json`).
  - Stages are a status, so no category colour.
- **Phone (390 px):**
  - one task per row, at most two lines
  - buttons wide enough for a thumb
  - no sideways scroll
  - the creator card in a drawer, not inline
  - the first task visible without scrolling
- **Right to left:** `dir="rtl"` on the page; handles, links and numbers in `<bdi dir="ltr">`, as the map already does for @lumebookai (`template.html:818`).
- **Saving:** a small "saved / 2 waiting" note in the top bar. Every tap shows a toast with Undo. Changes made offline wait in browser storage and are written when the connection is back, oldest first.

### 5.8 Where it should live

| Option | Good | Bad |
|---|---|---|
| **A. Stay a published page with its database (today's setup), improved** | Already used daily (242 sends). Hebrew messages, offer lock and voice learning exist only here. Claude can read and write the data (`ArtifactData`), so the refresh, backups and analysis need no new tool. No extra cost | Works only inside claude.ai while signed in (2.1); no built-in history; caps on documents and database size are not stated (`db.d.ts`); research data is baked into the page |
| B. Google Sheets as the store, the page as the screen | Right to left per sheet [RTL1], offline editing once switched on [T18], easy export | The page would need a connector to read and write the sheet; voice learning and live updates would have to be rebuilt; two systems to keep in step |
| C. Notion database | Hebrew interface with mirrored layout [RTL2], phone app, Claude has a Notion connector here | Offline only for the first 50 rows of a database [T20]; right to left inside databases not documented [RTL2]; message drafting, offer lock and voice learning would be lost or rebuilt |
| D. A paid creator platform | Built for the pipeline | From about $199 a month, no Hebrew, inbox-based automation ruled out [T4][T8] |
| E. A local app on the Mac, like Carousel Machine | Files in the repo, full control | Not on the phone, so not on the bus |

**Recommendation (inference): stay with A,** and fix its two real weaknesses:

1. **Data loss:** the offline queue (R37) and a weekly export of every collection to a folder that is not in git. Creator contact data should not go into the repo history.
2. **One source of truth:** the dashboard reads the map's counts from that export (R39).

Move only if Yarin needs the CRM outside claude.ai (for example, on a phone where claude.ai artifacts do not save). I could not check that; see question 3.

---

## 6. Gap analysis and plan

### 6.1 Gaps

| Requirement | Today | Gap | Effort | Payoff |
|---|---|---|---|---|
| R10, R13, R15 Today list, one-tap answers, copy = sent | Three lists on Overview; status menu; separate Sent button | One ranked list; answer taps; follow-up recorded on copy | Medium | High: clears the 102 and starts the record |
| R1, R7, R19, R22 Deal stages, terms, due dates | Steps without data | Deal record, dates, stuck view | Medium | High: Hanukkah deadline, 15 in process |
| R23 to R26 Results | One sales field | Store export, cost, decision | Medium (needs Yossi) | High: tells who to repeat |
| R37, R38, R9 No loss, history | No retry, no history | Offline queue, touch log, weekly backup | Small | Medium: insurance |
| R12, R14, R17 Outreach rules | WhatsApp first; no limit; small tests | Channel rule, daily limit, honest test sizes | Small | Medium: protects the account and the law position |
| R5 Stalled deals | Auto-declined after 30 days | Show as stuck | Small | Medium |
| R6 Refresh | Built, not run | Run it; feed "posted" into deals | Small | Medium |
| R21, R33, R20 Disclosure, consent, rights | Not tracked | Ticks in the deal | Small (with R19) | Medium: legal safety |
| R35, R36 Phone, Hebrew | Long cards, English labels | Row layout, Hebrew labels | Medium | Medium |
| R39 One source of truth | Four places disagree | Dashboard reads the export | Small | Low to medium |
| R27, R28, R30 Quality signals | Static score | Reliability and "knows LumeBook" | Small | Low now, higher after a few deals |
| R31, R32, R34 Privacy | Nothing set | Retention rule, section 11 wording, kids' names policy | Small (after a lawyer) | Medium: risk |
| R16, R18 Messages | Met | None | | |
| R29 Risk flags | Met | None | | |

### 6.2 The top five changes, in order

**1. A Today screen with one-tap answers.**
- **What:** replace the Overview's three lists with one ranked list: deals with dates, "did they answer?", follow-ups due, results to read, new to contact. Each row has one or two buttons. Copying a follow-up records it as sent, with Undo. Answer taps (yes, question, not now, no) stop the follow-ups and log the time; a reason chip is optional.
- **The backlog:** a one-off clean-up for the 102 creators shown as due: "already followed up on (date)", "skip follow-up", or leave as due.
- **Done looks like:** Yarin clears a day's list on the phone in one sitting. Every contacted creator sits in exactly one bucket. The "due" number matches what is really due.
- **What could go wrong:**
  - The clean-up records follow-ups that were never sent; keep it per creator with Undo.
  - Copy-equals-sent records a message that was copied but not sent; keep the Undo visible.
  - A list that grows too long; the daily limit caps new contacts.

**2. Track the deal from yes to posted.**
- **What:** when Yarin taps Agreed, the page saves the offer of that day (from `shared/facts.json`), asks for the book title and the child's first name(s), and prefills everything else. That includes the posting window, the usage scope ("repost on LumeBook with credit"), the disclosure line, the parent's consent and the personal link once enrolled.
- **Then:** one tap each for ordered, sent and delivered. The video due date is worked out. The page drafts three check-ins after delivery (arrived?, how was reading it?, one content nudge), then stops. Posted takes the link (the refresh suggests it) and two ticks: disclosure and label. Stalled deals show in a "stuck" filter instead of turning into declines.
- **Done looks like:** each of the 15 creators in process has a deal row with a stage and a date. The creator books for Hanukkah (due 10 Nov) are visible with their dates. The refresh of 25 Oct fills "posted" where it finds a reel.
- **What could go wrong:**
  - Yarin dislikes extra forms on the card (memory note of 11 Oct), so the Agreed step must be two fields, not ten.
  - The address must stay out.
  - The disclosure wording in the creator brief ("נוצר בשיתוף פעולה עם LumeBook", `creator-brief.md:208`) may not meet the Attorney General's "advertisement or sponsored" standard [D5]; a lawyer should check it before the first post.

**3. Results per creator, from the store.**
- **What:**
  - Enrol every agreed creator in the store's ambassador programme and save the link in the deal.
  - Ask Yossi for one weekly export: orders per ambassador link, with printed or digital and the date.
  - Read views at day 7 from the refresh, and insights through the paid-partnership label [D10].
  - Work out cost per deal from the book's print cost plus shipping (₪30 home delivery at retail, `docs/lumebook-product-brief.md`; the real cost is unknown).
  - Show cost per link order and a repeat decision.
  - Separately, add one "where did you hear about us?" question to the store's post-purchase WhatsApp.
- **Done looks like:** the Results view lists every posted creator with link orders (or "no data"), cost and a decision, and keeps the three order counts apart.
- **What could go wrong:**
  - Yossi cannot give an export.
  - The ₪30 programme and the 25% offer disagree and confuse creators (`report.md:517`).
  - The 7-day link memory and printed-only crediting undercount sales.
  - Numbers stay too small to judge for months: one or two orders per creator is noise (inference).

**4. Never lose an edit.**
- **What:**
  - Every tap writes a short history line (date, what, channel, version).
  - A write that fails is kept in browser storage and retried, with a "2 waiting" note.
  - The weekly refresh task also exports all collections to a local folder outside git and updates the dashboard's counts from it.
- **Done looks like:** turn the network off, make three changes, turn it back on, reload: all three are saved. Each creator shows a timeline.
- **What could go wrong:**
  - More writes hit the platform's call rate (`db.d.ts`: `resource_exhausted`); history lines must be small and batched.
  - An export with phone numbers and kids' data must stay out of git and off Vercel.

**5. Outreach rules that protect replies, the account and the law position.**
- **What:**
  - A channel rule in settings, until a lawyer answers: Instagram DM for the first touch; email first only where the creator publishes it for collaborations; WhatsApp after a yes or when the creator invites it.
  - A daily send limit Yarin picks.
  - Silent stays separate from no.
  - After a silent DM, suggest the creator's public business email once.
  - The test panel shows the sample needed (about 110 per version to see a doubling) or is hidden.
- **Done looks like:** the card shows the suggested channel and why; the Today list stops new contacts at the limit.
- **What could go wrong:**
  - Fewer messages a day.
  - The lawyer may allow WhatsApp, making the rule needlessly strict, or rule email out too.
  - A creator who prefers WhatsApp may answer more slowly on Instagram.

Changes 1 and 4 can be built together. Change 3 should start now as a message to Yossi, because everything in it depends on Yossi's answer.

### 6.3 Questions for Yarin

1. **Follow-ups:** about 102 creators show as Follow-up due. Did you send follow-ups without pressing "Follow-up sent", or are they really not sent?
2. **The empty fields:** reasons, next actions, notes and personal links are all empty. Not needed yet, or too many taps?
3. **The phone:** do you open the map on your phone, in the Claude app or a browser, and do changes save there? I could not check this.
4. **Language:** should the daily screen be in Hebrew? The map's labels are English today; the dashboard is Hebrew.
5. **Daily limit:** how many new creators a day are you comfortable messaging?
6. **Video window:** how many days from book delivery to the video (for example 7, 10 or 14)? No source gives a number for barter; GRIN suggests a content invite around day 7 to 10 [G3].
7. **Usage rights:** repost on LumeBook only, or ads too? And what is the raw footage the brief asks for allowed to be used for?
8. **Kids' names:** keep collecting them from public bios (your 7 Oct rule), or only when the parent gives them for the book? A consumer protection regulation may limit using a minor's name without a parent's consent [P8].
9. **WhatsApp:** do you send from a personal number or the WhatsApp Business app? The business policy requires opt-in [W1].
10. **Paid-hold creators** (three in `shared/facts.json`): same tool, or separate?
11. **Signups:** is the Google Form still in use? If so, its signups should land in the map.

**For Yossi** (for change 3):
- a weekly export of orders per ambassador link
- whether the ₪30 programme is the 25% offer
- the print cost of one book
- whether digital orders are credited
- enrolment for each agreed creator

**For a lawyer** (from `sources.md`, Israel section):
- whether a pitch sent to creators filtered by type is "direct mailing"
- whether kids' counts and notes are sensitive data
- the security level that applies
- whether a first pitch by email, SMS or WhatsApp falls under the anti-spam rule, and whether creators with public business contacts count as businesses
- the section 11 wording when asking for a phone or address, and how long to keep data of creators who declined
- the disclosure wording for a barter-plus-link post
- whether a parent filming their own child needs a child-performance permit

---

## 7. What could not be verified

- Any creator reply-rate study with a stated sample, or any comparison of Instagram DM, email and WhatsApp for creators.
- Any Israeli number on creator outreach, barter norms or gifting post rates.
- An opt-in versus unsolicited gifting comparison; any measured on-time rate for creator content.
- A study of which CRM features solo users keep or drop.
- How much link tracking misses, from an independent source.
- The final text of Israel's influencer disclosure rules after the 2021 draft; the text of the anti-spam section itself; any ruling on WhatsApp or Instagram DMs under it.
- Whether a parent filming their own child at home needs a permit.
- Whether claude.ai artifacts save from Yarin's phone; whether Notion databases show Hebrew right to left.
- Collabstr, Later Influence's stage names, Pipedrive's pricing page and monday.com's interface languages (pages returned errors).
- Whether the store is on Shopify, and whether Shopify Collabs accepts Israeli creators.
