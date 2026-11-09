# Store mock

lumebook.com/IL/he rebuilt as a landing page that drives a parent to start a book and buy it, in the LumeBook design system's components, dark in the store's own night purple and gold (light on a switch), heavily animated, and a working demo where a visitor makes a pretend book. Made 09 / 11 / 2026.

Yarin's requests that day, in order: "take the website https://lumebook.com/IL/he and create a mock version using the design system of the dashboard"; "you can change and move elements as you wish for it to have the best possible landing page structure driving people to start designing their own book and sell"; "Yes, deploy it"; "i dont need the side bar"; "this part doesnt look good" (the violet Hanukkah capsule); "make it dark mode and magical using the purple of the original website"; "heavily animate"; "add icons and images as much as you can"; "show deals not the delivery" and "usual price 149"; "create a fully working demo, everything does something, and let me create a fake book"; "dark + light mode switch".

- On the project server: http://localhost:8780/sites/lumebook-store-mock/index.html (side bar: מערכת, "החנות בעיצוב שלנו")
- Review copy for the store team: https://lumebook-store-mock.vercel.app (`?motion=full` to see the motion on a Mac with Reduce Motion on; `?theme=light` or `?theme=dark` to open in a mode)

The store's code is not in this repo, so this is a proposal, not a live page.

## Files

| File | What |
|---|---|
| `src/content.json` | All copy and data: promo, hero, numbers, marquee rows, the 8 categories and 94 books, steps, customer books, why, price and deals, questions, the demo's words (`demo`), the switch labels (`theme`), footer |
| `src/build.py` | `python3 tools/lumebook.py build store-mock` writes `index.html` (local) and `web/index.html` (Vercel). Never edit those by hand |
| `web/` | The deploy folder. `.vercel/` and `.env.local` (a Vercel token the CLI wrote) are git-ignored and `.vercelignore` keeps `.env*` off the site |

Deploy: `python3 tools/lumebook.py deploy store-mock` (builds first). The nightly job also redeploys it when its files changed.

## How it looks

- **Exception to the white-only rule, this page only.** The lb- components of `shared/design/lumebook.css` with page tokens on `html.st-night` in the store's own colours (read from lumebook.com's `:root` on 09 / 11 / 2026: ink #0B0518, #130827, #1D1039, #291852; gold #F3D9A1, #E6B762, #C9954A; cream #F8F0E1). Light mode is the design system's own white tokens plus a lavender sky. The page's own colour slots (`--st-*` on `html`, night values on `html.st-night`) carry everything that differs.
- **No project nav** (Yarin asked). Built with `design.head(nav=False)`, without the Reduce Transparency switch (the dark glass has its own tokens).
- **The switch:** sun or moon in the top bar, dark by default, the choice kept in this browser (`localStorage` `st-theme`), a circle reveal from the button where the browser has view transitions.
- **Motion:** night sky (aurora, two star layers, shooting stars, rising motes), gold shimmer text, a glowing sweep on every start button, a turning gold border on the start card, floating hero books and a waving Lume that follow the pointer, two cover marquees and a customer-photo marquee, numbers that count up, reveals on scroll, 3D tilt and shine on book cards, a sparkle trail on the pointer, bursts on clicks. Everything sits under `html.st-anim`. The local copy always animates (Yarin's Mac has Reduce Motion on, as with the glass and Reduce Transparency); the Vercel copy honours Reduce Motion unless `?motion=full` (remembered in `localStorage` `lb-motion`). `st-full` gives each animation its length back over lumebook.css's reduced-motion rule.
- **Pictures**, all loaded from lumebook.com: the store's covers (`/book_covers/<girl|boy>/B<id>_<girl|boy>.webp`, both versions exist for every book but 9003), customer photos (`/ugc/`), four hero books (`/hero/series2..5-transparent-768.avif`), Lume (`/LumeCharachter/lume_with_book.webp`), the banner (`/manifesto_banner.avif`, it carries the store's own spelling in the picture) and the logo. Icons from `shared/design/icons.json` (`sun` and `moon` added for the switch).

## Phones

Yarin, 09 / 11 / 2026: "review the mobile version, it needs to be perfect". The phone rules are `MOBILE_CSS` in `src/build.py`, last in the stylesheet so they win. Checked at 320, 360, 375, 390 and 430 wide, landscape (844 by 390) and tablet (768), in both modes: no sideways scroll, every tap target 44px, fields at 16px or more (iOS does not zoom).

- Top bar: one row with the square logo mark (`/logo_squre-96.webp`), the switch, "הספרים שלי" with its count and the start button; the label shortens under 400px ("ליצור ספר בחינם") and 350px ("ליצור ספר"). The section pills and the "דמה" chip are hidden on phones and on landscape phones.
- The promo strip is one link to the Hanukkah shelf (44px, an arrow instead of the words).
- Hero, from 760px down (Yarin, 09 / 11 / 2026): the picture comes first, above the headline, and Lume, the "הילד שלכם בתפקיד הראשי" name tag and the age chip are hidden ("remove all of it"); the child's name still goes onto the start buttons. No empty strip under the picture (Yarin's marked screenshot): the third small book sits beside the main one and the headline starts about 20px under the book. One-column checks, the floating books kept inside the screen; the three numbers share a row. Wider screens keep all three.
- Steps and reasons are compact rows (all four steps fit one screen); the offer card puts the cover beside the price; deal badges sit in the card's corner; 8 books before "עוד" instead of 12.
- Every dialog is a bottom sheet with a grabber; the book maker shows the step numbers with only the current label, a small live preview, and its main button (and the order's total and confirm) fixed at the bottom of the sheet. Sheets blur what is behind them and are near solid in light mode.

## The working demo

Every link stays in the page. A start button opens the book maker; a book (shelf or marquee) opens its card; a category link filters the shelf; the Hanukkah link shows the holidays shelf; "הספרים שלי" opens the saved books; anything else opens a sheet that says what the link opens in the real store, with a button that does open it. The notice's "לחנות כפי שהיא" link goes straight to the store.

The book maker: pick a book (by category), the child's name, boy or girl, a photo (picked or dropped; shrunk to 320px in the browser and never sent anywhere) and a dedication, a short making moment, a four-page flip preview (the cover with the photo and a "בכיכוב" ribbon, the dedication, a page with the name, an end page with Lume), a pretend order (book 119 ₪ with 149 ₪ struck, digital copy free, the Hanukkah second book at 99 ₪, the store's three delivery options and prices, a live total), confetti, and "הספרים שלי" (up to 12 books in this browser's `localStorage` `st-mybooks`). It never asks for payment details and says that nothing is sent or charged. The first deal card opens the maker with the second book already added.

## The structure and why

Promo strip, sticky bar with the start button, hero with a start card (name and boy or girl go onto the hero picture, every start button and every cover), the store's trust numbers, a covers marquee, one filterable shelf instead of eight rows (best sellers first, led by `shared/facts.json` `top_books`), four steps, customer books with a review, why (with the banner), price and deals, questions, a final start card, other products and guides, footer.

From `research/cro-crm/report.md`: the page says exactly what is free (the cover; priority 2, `audit.md` A4) and never promises the story for free. Price: Yarin asked for the deals and the usual price (149 ₪ struck) in the price section instead of delivery; delivery stays in the questions and in the demo order. The CRO report's points that the struck 149 ₪ is a legal question and that the total with delivery should show early (priority 1) still stand as notes for the store team. None of this has been tested on real visitors.

## Rules

- Prices, delivery, books and answers come from the live store (read 09 / 11 / 2026). Re-read the store before changing them; never state a policy the store does not.
- Parent-facing Hebrew follows the `lumebook-hebrew-voice` hard rules (no dash, hyphen or semicolon, no guarantees, no "כל הילדים"). Store book titles keep their words with dashes turned into colons or spaces. The brand in Latin letters (LumeBook). The build fails on an em or en dash or the yod spelling.
- The page is `translate="no"` (audience copy stays Hebrew).
- Not applied here, ask first: the Partners page's no-religious-images rule. The שומרי מסורת category shows the store's religious covers when picked; it is never the default view or in the marquees.
- The review copy keeps robots noindex, nofollow and a canonical to lumebook.com/IL/he, and carries no project nav, local-links map or design comments.
