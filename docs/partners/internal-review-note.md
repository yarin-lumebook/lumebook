# Partners page: internal commercial review

**Internal. Do not publish, do not paste into the page, do not name anyone in it.** Written 06 / 11 / 2026 for Yarin, updated the same day with Yarin's answers. It lists the commercial terms from one earlier author conversation, says which are confirmed, what the public page says, and what is still open.

## 1. What is confirmed (Yarin, 06 / 11 / 2026)

| Question | Answer | Where it went |
|---|---|---|
| Standard partner offer, or only individual agreements? | **Standard** | `shared/facts.json` `partners.standard_offer`. The page no longer says "agreed individually" or "no fixed package" |
| Where do inquiries land? | **yarin@lumebook.com** | Form hand-off email, no-JavaScript fallback and footer, in all four languages. Any future endpoint should notify the same address |
| Can per-title sales be reported monthly? | **Yes** | "Monthly report" card on the page |
| Dedicated author page and a printed copy: standard? | **Yes, both** | "Dedicated book page" and "A printed copy" cards on the page |
| Other languages? | **Yes: English, Arabic, Russian** | Drafted and built (`sites/lumebook-partners/src/content/`). Arabic and Russian need a native reader before going live |
| Can LumeBook produce a book from an outside author's text, and how? | Asked back ("wdym?"), **still open**, see section 4 | The page keeps "preparing and reviewing the book" as a step to be defined, with no promise of services |

**Not given yet: the terms of the standard offer.** The page therefore shows no percentage, amount, notice period, exclusivity or content cadence, and the lint blocks them. As soon as you confirm them (section 2) they can go on the page and into `shared/facts.json`.

Background, checked on 06 / 11 / 2026 (`shared/facts.json`, `docs/`, `lumebook.json`, the project memory): before your answers no partner offer existed in the project. The only approved offer was the creator and ambassador one (`offer`: one 25% allocation per sale through a personal link, split between the creator's earnings and an audience discount). It is a different program (creators promote existing books). Its still-open questions (how the sale value is calculated, payout method and timing, tracking) are open for the partner offer too.

## 2. The standard terms: which of the earlier proposals are the standard?

These came from a single negotiation with one author. They were **proposals**, and the author's counterproposal was not accepted in the correspondence available. Please say for each whether it is part of the standard offer.

| # | Proposed by LumeBook | Status now | On the page | What to confirm |
|---|---|---|---|---|
| 1 | 25% commission on every sale of the author's own book, whatever the source | Proposal | "Compensation is tied to sales of the agreed book; amount and calculation are in the written agreement" | The rate. What it is calculated on: price only, or shipping and VAT too, before or after discounts and refunds. All sales channels or only some. Payout method, schedule, minimum payout, invoice rules (an עוסק פטור question, as in `docs/lumebook-ugc-ambassador-research.md`), clawback on refunds |
| 2 | Dedicated book page with the author's name and an agreed professional bio | **Standard (confirmed)** | "A dedicated book page", wording agreed together | Who approves the bio and any professional claims in it. Whether the store can build a per-author page is **not verified** (a question for whoever maintains the store) |
| 3 | Dynamic website placement, no guaranteed homepage spot | Proposal | Nothing about placement | Whether to say anything about placement (recommended: no) |
| 4 | Exposure through existing traffic and marketing, no dedicated ad campaign | Proposal | Nothing about reach. The FAQ says there is no promise of income or sales | Keep silent on reach (recommended) or state the "no dedicated campaign" limit |
| 5 | A printed copy | **Standard (confirmed)** | "A printed copy" | Cost and how many copies |
| 6 | Monthly sales and commission reporting | **Standard (confirmed)** | "Monthly report" | Format, and how the data is produced. The 12 / 10 / 2026 sales note says the admin cannot show where a sale came from, and per-title totals were not checked (`docs/lumebook-sales-data-decisions-2026-10-12.md`). A per-title monthly total may be enough if the commission covers every sale |
| 7 | Recurring promotional content, frequency still open | Under negotiation | "Content and promotion in a scope agreed in advance" | Minimum cadence, length of any trial, who approves content, disclosure wording for a commercial relationship (the UGC research cites the Israeli Consumer Protection Authority on disclosure of free products, `docs/lumebook-ugc-ambassador-research.md`; ask a lawyer) |
| 8 | Either side may end it with 30 days' email notice | Proposal | "Ending conditions are set in the agreement" (no period stated) | The notice period. What happens to the book page, to orders already placed and to commission after the end |
| 9 | Exclusivity against other personalised-book websites during the partnership, other publishing channels allowed | Proposal | "What is possible alongside the partnership is set in the agreement" (the word exclusivity is not used) | Is exclusivity standard, its scope and duration. Context: the competitor MeBook runs expert "creator" pages with co-authored books (`docs/lumebook-ugc-ambassador-research.md`) |

The author's counterproposal, **not accepted and not policy**: one Reel or post a month at the author's choice during a three-month trial, content woven into the author's own professional content (not always a direct ad), creative discretion, freedom to approach a commercial publisher, and review of a draft agreement before the final decision. Worth answering: whether a monthly minimum is enough, what "creative discretion" may cover (claims about the book, disclosure), whether a draft agreement is shared before commitment (the page does not promise it), and whether the author can go to a publisher.

## 3. Never discussed, so never invented on the page

These need an answer before any agreement, and none is on the page:

- How commission is calculated: VAT, shipping, discounts, refunds and cancellations, orders that are never paid, the attribution window.
- Payout dates, minimum payout, payment method, tax documents.
- **Rights and licensing:** who owns the text; the licence LumeBook gets (print, digital, languages, territory, term); who owns the illustrated characters and cover; what happens to a title after the partnership ends; the author's rights to publish elsewhere in another form.
- **Professional content:** how a professional describes the book without a therapeutic claim (the page and the product brief say it is not treatment or a replacement for care), who checks the content, liability.
- **Children's data and privacy** for the inquiry form and for books made from an author's story.
- **Age range:** the product brief shows inconsistent ranges across the site (1 to 10, 2 to 8, 2 to 10, 3 to 8). A partner book needs one.

## 4. About the production question, in plain words

Today a parent picks one of LumeBook's own stories in the store, adds the child's name and photo, and the book is made (`docs/lumebook-product-brief.md`). A partner's book is different: the story or the idea comes from outside. So the question is what LumeBook can do with it:

- Can an author's finished text be added to the store as a new title, so a parent can personalise it? Who does that work (editing, illustrations, layout, setting it up in the store), what does it cost, how long does it take?
- If the author only has an idea or professional knowledge, who writes the story?

Nothing in the project says whether this process exists. It is a question for whoever builds new titles for the store. Until it has an answer the page only says that preparing and reviewing the book is a step, with each side's role "defined before work starts".

## 5. What the public page does and does not claim

Does: that an inquiry is a request for a suitability discussion; that responsibilities, compensation and promotion are defined before work starts, in writing; the confirmed standard items (a dedicated book page, a printed copy, compensation tied to sales, joint content and promotion, a monthly report); that a written agreement covers compensation and its calculation, each side's responsibilities, content and promotion, review, rights and permitted uses, other publishing, reporting, payment and ending; that no manuscript, audience size or publishing experience is required to inquire.

Does not: any percentage or amount, exclusivity, notice period, trial length, monthly content, homepage placement, a dedicated campaign, an acceptance, publication or production promise, writing or editing services, distribution, income or sales, or any therapeutic claim. `sites/lumebook-partners/lint_copy.py` blocks the words for these in all four languages.

## 6. Still open, in the order they unlock work

1. **The standard terms** (section 2, rows 1, 3, 4, 7, 8, 9). Say which of the earlier proposals are standard and with what numbers, and they go on the page.
2. **The production question** (section 4), for whoever maintains the store.
3. **Rights and licensing model** (section 3). Needs a lawyer before any agreement draft.
4. **Route name** (`/partners` against `/authors` or `/collaborate`), because the store already uses "partner" for organisations.
5. **A native reader for the Arabic and Russian copy** (drafted by Claude, not checked by a person).
6. **The inquiry backend** (`implementation-brief.md` section 5). Until it exists the form hands off to WhatsApp or email to yarin@lumebook.com.

When the terms are decided: put them in `shared/facts.json` (the `partners` block), update the four content files, run `python3 sites/lumebook-partners/src/build.py` and `python3 sites/lumebook-partners/lint_copy.py`, and relax the lint's blocklist only for terms that were actually approved.
