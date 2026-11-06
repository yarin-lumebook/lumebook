# Partners page (local review prototype)

Landing page and inquiry form (Hebrew, English, Arabic and Russian) for children's book authors and professionals who work with young children and parents. Target route on the store: `/IL/he/partners`. **Not published, not deployed.** lumebook.com is not in this repo, so this folder is the page ready to be moved into the store. Read `docs/partners/implementation-brief.md` first; the commercial side is in `docs/partners/internal-review-note.md` (internal).

## Preview

The project server already runs (login item, port 8780). Open:

http://localhost:8780/sites/lumebook-partners/ (Hebrew), and `/en/`, `/ar/`, `/ru/` after it.

Do not start a second server. The edit button (pencil, bottom left) works on these pages; its changes are kept in `shared/site-editor/edits/` (the pages are built), so for lasting wording changes edit the content files below.

## Files

| File | What |
|---|---|
| `src/content/<lang>.json` | **All the copy**, one file per language (he, en, ar, ru) |
| `src/build.py` | `python3 sites/lumebook-partners/src/build.py` builds `index.html` (Hebrew) and `en/`, `ar/`, `ru/` `index.html`. Never edit those by hand |
| `partners.css` | Styles (the store's `--am-*` tokens) |
| `partners.js` | Form: validation, hand-off, loading, success and failure, analytics event |
| `lint_copy.py` | `python3 sites/lumebook-partners/lint_copy.py` after every build |
| `img/`, `fonts/` | Reused assets. `img/logo.png` and `fonts/` are registered copies of `shared/brand/` (`lumebook.py sync`); the three `B*.avif` covers are the store's own |

## How the form behaves

- `form[data-endpoint]` is empty today. The form validates, then shows a hand-off: the inquiry written out, with buttons to send it by WhatsApp (`wa.me/972559800791`) or email (`yarin@lumebook.com`) and to copy it. It says that nothing was sent. No success state, no success event.
- With an endpoint set it POSTs JSON, shows a loading state, and shows success **only** for a 2xx answer with `{"ok": true}`. Anything else shows the failure state with the same fallback routes.
- It never calls the ambassador sign-up API (that creates a personal link and an account).
- To try the success and failure states without a backend, stub `window.fetch` in the browser console and set `data-endpoint` on the form. The script reads the attribute at submit time.

## Rules for this page

- A standard offer exists but its terms were not given: no percentage, amount, notice period, exclusivity or content cadence on the page until Yarin confirms them (`docs/partners/internal-review-note.md`, `shared/facts.json` `partners`).
- House rules: no em dashes in any language, no hyphens or semicolons in Hebrew copy, לומבוק never לומיבוק (LumeBook in Latin letters in en, ar, ru), no AI wording, no medical or guarantee claims. The lint enforces them.
- Arabic and Russian were drafted by Claude: have a native reader check them before they go anywhere.
- White and cream only, no side stripes. Fonts and tokens follow the store's ambassador page, not the internal design system.
- Never deploy from this folder (there is deliberately no `.vercel` link). The nightly job at 00:00 commits and pushes the repo to the private GitHub repository as usual, but it deploys only the dashboard and the creator brief.
