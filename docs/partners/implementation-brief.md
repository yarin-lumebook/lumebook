# Partners page: implementation brief

Written 06 / 11 / 2026. Audience: Yarin and whoever maintains the store site (lumebook.com). The visitor copy is in `sites/lumebook-partners/src/content/<lang>.json` (Hebrew, English, Arabic, Russian); this brief is in English.

Status: **built as a local review prototype, not published, not deployed.** Nothing on lumebook.com was changed.

## 1. The limitation: the store's source code is not in this repo

The existing ambassador page lives on the store, a React single-page app (Vite bundle `/assets/index-*.js`, the ambassador route is a lazy chunk `AmbassadorProgram-*.js` with its own `AmbassadorProgram-*.css`; read on the live site on 06 / 11 / 2026). This repository holds marketing material only:

- `sites/lumebook-ambassadors/` is the retired static Vercel version of the ambassador page (retired 11 / 10 / 2026, `lumebook.json` component `ambassadors`). It is an archive, not the live page, and its form (an Apps Script) is not the store's.
- `research/creator-content-conversion/report.md` section 11 records what was read from the store's public code on 14 / 10 / 2026.

So the real route cannot be added from here. What was done instead, as the brief asks: a working page for local review in the project's `sites/` folder, built from the live page's own tokens and patterns, plus this brief for whoever integrates it. It is not an unrelated site: it is the page itself, written so it can be moved into the store.

## 2. How the existing ambassador page works (what to reuse)

Read from the live page on 06 / 11 / 2026:

| Area | What the store does | Used in the prototype |
|---|---|---|
| Route | Router paths `/:country/:lang/ambassadors` and `/:lang/ambassadors` (so `/IL/he/ambassadors` and `/he/ambassadors`), sub-routes `/dashboard` and `/terms`; locales he, en, ar, ru (IL) and en (US) via `hreflang`. The main bundle also keeps a **hardcoded set of known top-level paths** (`""`, `wizard`, `books`, `gifts`, `kindergarten`, `ambassadors`, `recommend`, `about`, `blog`, ... and the organisation slugs `roladin`, `jetlek`, `prego`...), so a new route has to be added there as well | Target route `/IL/he/partners` (no existing `partners` path or slug found). Hebrew only for now (see section 8) |
| Naming | On the store, "partner" already means an organisation or club with a co-branded landing page (`PartnerLanding-*.js`, slugs such as `jetlek`, `prego`, `maccabitlv`, assets under `/landing_pages/partners/`) | The brief's route name is kept, but see section 8: a name like `/IL/he/authors` or `/IL/he/collaborate` would avoid the overlap |
| Look | Cream page (`#FAF6EF`) with a faint 3rem grid and a warm top glow, gold gradient pills (`linear-gradient(100deg,#EDC688,#D9A05A,#C3803C)` with dark ink text), 1.25rem rounded translucent cards, 26px radius tokens, Varela Round body font (Hebrew and Latin woff2 served from `/fonts/`), Fraunces for Latin display | Same tokens, same names (`--am-bg`, `--am-gold`, `--am-grad`...). The store already has them, so on integration the prototype's `:root` block is dropped |
| Hero | Eyebrow, big title, lede, gold pill CTA plus text link, three tilted cover images (`/book_covers/girl/B41_girl.avif`, `/book_covers/boy/B2_boy.avif`, `/book_covers/girl/B10_girl.avif`), small pill tags | Same pieces, same three covers |
| Sections | Cards, numbered steps with gold discs, FAQ as `<details>`, closing CTA | Same components, new content |
| Form | One panel on the page, violet gradient, follower-band slider, split slider, earnings examples, terms switch. Submits to `POST /api/ambassadors/signup`, which **creates the ambassador, a personal link and a dashboard** (answers `{status:"active", link}`; `401` verify by WhatsApp code, `404 PROGRAM_CLOSED`, `400 {fields}`) | **Not reused.** Different panel (cream and gold), different fields, different endpoint (section 5) |
| Program settings | `GET /api/ambassadors/program` (open, budget, discount steps, list and regular price, link window 7 days, hold 14 days) | Not used |
| Analytics | `gt.track("Event_Name", {props})` (for example `Family_Gift_Link_Clicked`, `Book_Selected`, `Purchase`); Mixpanel, Meta pixel and GTM run only after the visitor accepts analytics cookies (`cookie_consent`) | One DOM event, see section 4 |
| Contact | WhatsApp `https://wa.me/972559800791` and `support@lumebook.com` (product brief, 01 / 10 / 2026) | WhatsApp is kept as a fallback route. The inquiry email is **yarin@lumebook.com** (Yarin, 06 / 11 / 2026), not the support address |
| Privacy | `/IL/he/privacy-policy` | Linked from the form |

## 3. What was built

All in `sites/lumebook-partners/` (registered as component `partners-page` in `lumebook.json`):

| File | What it is |
|---|---|
| `src/content/he.json`, `en.json`, `ar.json`, `ru.json` | **The copy, one file per language** (page text, form labels, validation and result messages). Edit these, never the built pages |
| `src/build.py` | Builds the four pages from the content files (`python3 sites/lumebook-partners/src/build.py`) |
| `index.html` (Hebrew), `en/`, `ar/`, `ru/` | The built pages: hero, who it is for (two entry points), example topics, what a partnership includes, how it works, what is agreed together, FAQ (10 questions), inquiry form, closing CTA, footer disclaimer, language links. Metadata: title, description, canonical per language, Open Graph, `hreflang` for all four plus `x-default`, `noindex` while it is a review copy |
| `partners.css` | Styles, store tokens and patterns, RTL and LTR (Hebrew and Arabic right to left, English and Russian left to right) |
| `partners.js` | Validation, conditional fields, loading, success, failure and hand-off states, analytics event. No dependencies. Reads its strings from the page's i18n block |
| `lint_copy.py` | Copy lint for all four languages (see section 6) |
| `img/`, `fonts/` | Existing assets reused (logo and fonts are registered copies of `shared/brand/`, the three covers are the store's own, taken from the archived ambassadors site) |

Not carried over from the ambassador page, on purpose: the follower slider, the discount-split slider, the earnings examples, instant personal-link creation, mandatory UGC or raw-footage delivery, the program terms, dashboard access, the violet form panel.

Page decisions worth knowing:

- A standard partner offer exists (Yarin, 06 / 11 / 2026) but its terms were not given, so no commercial figure appears anywhere (no percentage, amount, notice period, trial length, exclusivity). The confirmed standard items are on the page: a dedicated book page, a printed copy, compensation tied to sales, a monthly report. `internal-review-note.md` lists what is still open.
- The copy never says the books are made with AI, and never calls them treatment, diagnosis or a replacement for professional care (footer disclaimer).
- Hebrew: predominantly feminine direct address, with one line saying the page is open to everyone. English, Russian and Arabic use neutral or plural address, the way the store's own ambassador pages in those languages do.
- Arabic and Russian were drafted by Claude and **have not been read by a native speaker**. Brand is written LumeBook in Latin letters in all three, as on the store. Arabic and Cyrillic fall back to system fonts, as on the store (Varela Round has no glyphs for them).
- "Book preparation and review" is a process step, not a promise of editing or production services. Whether LumeBook can produce a book from an outside author's text is **not verified** (internal note).

## 4. Analytics

The prototype fires one DOM event, `lumebook:track`, with `detail = {name, props}`. On the store, wire it once next to the other trackers, inside the same consent gate:

```js
document.addEventListener('lumebook:track', (e) => gt.track(e.detail.name, e.detail.props));
```

| Event | When | Props (closed lists, from `partners.js`) |
|---|---|---|
| `Partner_Cta_Clicked` | A CTA is clicked | `location`: header, hero_primary, hero_secondary, entry_story, entry_expertise, closing, closing_whatsapp, handoff_whatsapp, handoff_email, handoff_copy |
| `Partner_Inquiry_Submitted` | **Only after the server answered 2xx with `{ok:true}`** | `starting_point` (expertise, idea, story, book), `professional_field` (author, parenting, sleep, potty, slp, ot, psychology, biblio, classes, other) |
| `Partner_Inquiry_Failed` | The send failed | `reason`: network, timeout, server |

Rules built into `track()`: a prop whose key or value is not in the closed lists is dropped, so no name, email, phone, link, description, book title or other free text can reach analytics. Validation errors are not tracked. In hand-off mode (no endpoint) no success event exists and none is sent.

Do not map `Partner_Inquiry_Submitted` to a Meta standard event (`Lead`, `CompleteRegistration`) or an ads conversion: the pixel is used to optimise ads for book sales, and a partner inquiry would pollute that signal.

## 5. The form backend (the main open item)

I listed every `/api/` route in the store's main bundle and in the 184 lazy chunks it references (06 / 11 / 2026). The sign-up endpoints are the ambassador and recommender ones (`/api/ambassadors/signup`, `/api/recommenders/signup`), and both create an account and a personal link. A partnership inquiry must **not** use them: it would enroll the person, create a referral link and imply terms. The rest are ordering, B2B batches (`/api/company/*`), marketing preferences and support. There is no lead, partner or inquiry endpoint.

The closest existing channel is `POST /api/support` (the customer support dialog): JSON `{orderId?, email, phone?, topic, description}`, where `topic` is a free-text field and `orderId` is only needed when no topic is given. It looks usable for a partnership inquiry (topic "שיתוף פעולה", the form fields written into `description`), but what it does on the server (ticket, email, order lookup, topic validation) is **not verified**, and testing it would send a real message to LumeBook support. So it was not called and not wired. Ask the store team before choosing it.

Current behaviour in the prototype (`form[data-endpoint=""]`): the form validates, then shows "the inquiry is ready, send it by WhatsApp or email" with the message pre-written, and a copy button. It says plainly that nothing was sent and shows **no success state and fires no success event**. The routes are `https://wa.me/972559800791` and `yarin@lumebook.com` (the inquiry address Yarin gave on 06 / 11 / 2026).

To make the form real, one of these (the page needs only a `POST` that answers 2xx with the JSON `{"ok": true}`; the strict JSON check is deliberate, because a single-page-app host can answer 200 with HTML for an unknown `/api/` path, and that must never show as a success):

- **A. Store endpoint (preferred):** `POST /api/partners/inquiry`. It stores a record and notifies `yarin@lumebook.com`. No ambassador, link, account, marketing-list enrollment or promise in any auto-reply. Then set `data-endpoint="/api/partners/inquiry"` on the form.
- **A2. Reuse support:** if the store team confirms `/api/support` may carry inquiries, add a small adapter that maps the fields into `{email, phone, topic, description}` and treats `res.ok` as success.
- **B. Interim:** an Apps Script web app writing to a Sheet, like the project's existing form scripts (`creators/lumebook-ugc-form.gs`). It must answer the JSON above with the right CORS headers. Deploying it is a publishing step: do it only with Yarin's approval, and keep the Sheet out of git (the pre-commit hook already blocks Sheet exports).

Request body (JSON), sent only when valid (`locale` is the page language: he, en, ar or ru):

```json
{
  "source": "partners_page", "locale": "he-IL", "page": "/IL/he/partners",
  "fullName": "...", "field": "author|parenting|sleep|potty|slp|ot|psychology|biblio|classes|other",
  "fieldOther": "... (only when field is other)", "email": "...", "whatsapp": "... (optional)",
  "profile": "... (optional)", "startingPoint": "expertise|idea|story|book",
  "rightsControl": "yes|unsure|publisher (only for story or book)",
  "description": "... (max 1200)", "bookTitle": "... (optional)"
}
```

Server rules to apply: validate every enum and length again, never trust the client, rate-limit, keep the honeypot idea (the page's hidden `company` field is dropped client-side), store the notice version that was shown, and use the data only for answering the inquiry. Not collected, on purpose: manuscript files, children's photos, client or patient information, follower counts.

The form's consent line is a notice, not a marketing opt-in (the CRM research flags the marketing-consent problem: `research/cro-crm/numbers-2026-10-25.md`, `report.md`). Whether the privacy policy already covers partnership inquiries, and whether a checkbox is required, is **not verified**: ask whoever owns the policy.

Not built, per the brief: a royalty engine, CRM or dashboard. The sales reporting the page mentions ("reporting under the agreed arrangement") needs a per-title, per-author sales view that the admin does not have today (the 12 / 10 / 2026 sales note says the admin cannot show where a sale came from; per-title totals were not checked). See the internal note.

## 6. Checks to run

In this repo:

```bash
python3 sites/lumebook-partners/src/build.py     # rebuilds the four pages from src/content/*.json
python3 sites/lumebook-partners/lint_copy.py     # all four languages: same content shape, brand spelling, no dashes (Hebrew: no hyphens), no AI wording, no commercial figures, no ambassador wording, page structure
python3 tools/lumebook.py check                  # registry, brand copies (no new warnings from this page)
```

On integration (store): desktop and mobile, RTL with mixed Hebrew and English (emails and links are LTR islands), keyboard navigation and focus rings, form validation, loading, success and failure states, every CTA, `title` and meta description, and the ambassador page unchanged. Then remove the review banner (`[data-review-only]`) and the `noindex` line, and add the route to the sitemap.

## 7. Integration steps (store team)

1. Add the route as a lazy chunk like `AmbassadorProgram`, inside the store's layout (header and footer come from the store, not from this file): router paths `/:country/:lang/partners` and `/:lang/partners`, plus `"partners"` in the known-paths set of the main bundle, plus the sitemap.
2. Port `index.html` sections to components, `partners.css` rules under a `.partners-page` scope (tokens already exist), `partners.js` as the form component. Keep the markup semantics: one `h1`, `fieldset` and `legend` for the radio groups, `details` for the FAQ.
3. Fonts and the three cover images are already served by the store (`/fonts/`, `/book_covers/`). The logo comes from the store header.
4. Wire `lumebook:track` (section 4) and the endpoint (section 5).
5. Page metadata as in each page's `<head>` (canonical and `hreflang` for he, en, ar, ru). Move the strings into the store's own translation files; the content JSON has the same keys in all four languages.
6. Keep the ambassador program untouched. Cross-links between the two pages are already in the copy (header, footer, one FAQ answer).

## 8. Blockers and open items

- **Store source not available here** (section 1): the prototype cannot go live by itself.
- **No inquiry endpoint** (section 5): until one exists the form can only hand off to WhatsApp or email. `/api/support` is a possible shortcut, unverified.
- **Route name.** `/IL/he/partners` matches the suggestion, but "partner" already means organisations on the store. Yarin decides: keep it, or use `/authors` or `/collaborate`. Changing it means changing the canonical and Open Graph URLs in `index.html` and the route registration.
- **Languages:** he, en, ar and ru exist in the prototype. A native reader should check the Arabic and Russian copy. The store's US/en version was not made (the page targets `/IL/...`).
- **Privacy and legal wording** for the form, the page's disclaimer and any statement about professionals (for example how a therapist may describe a book) were not reviewed by anyone qualified.
- **Commercial terms**: still undecided, see `internal-review-note.md`.
- **Images**: the three covers are existing store assets and were not changed; a partner-specific image was not made.
