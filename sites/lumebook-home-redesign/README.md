# Home redesign (demo)

lumebook.com's three experiences, kids books (`/IL/he`), gift books for adults (`/IL/he/gift-books`) and photo albums (`/IL/he/albums`), as one site with one home page, one header and one design language, in three colour versions (purple tint, yellow tint, purple + yellow), each in light and dark. Made 17 / 11 / 2026 from Yarin's brief; Yarin, the same day: "its just a demo". Not deployed or published.

- Home: http://localhost:8780/sites/lumebook-home-redesign/index.html
- Category pages: `kids.html`, `gift-books.html`, `albums.html` (same folder)
- All versions in light and dark side by side (dev only): `compare.html` (page, width and height pickers)

## Files

| File | What |
|---|---|
| `src/build.py` | All copy, facts, links and picture choices, and the components. `python3 tools/lumebook.py build home-redesign` (or `python3 src/build.py`) writes the five pages. Never edit the HTML by hand |
| `assets/site.css` | Tokens (four blocks at the top) and every component |
| `assets/site.js` | Appearance toggle, start menu, phone drawer, hero picker, tabs, gallery filter, review carousel, reveal on scroll, campaign parameters, sliding segment thumbs, pointer light, the theme reveal, the dev version switch |
| `assets/studio.js` | The creation studio for all three products and the pretend account (sign up, log in, log out, הספרים שלי) |
| `src/store-books.json` | The title line and first three story pages of 11 kids books (boy and girl), read from `lumebook.com/api/book/<id>` on 17 / 11 / 2026, for the studio's preview |
| `img/` | Pictures made for this demo (sources below) |

## Identity v1 (since 17 / 11 / 2026)

The site uses the proposed LumeBook identity v1 (`shared/brand/identity-v1/`, copied from Yarin's brand kit `lumebook-brand-v1`): the purple 3D wizard hat with one yellow star (`img/hat-3d-96.webp` in the header and footer, `img/hat-3d-360.webp` on the studio's "making" screen) next to the outlined Heebo 900 wordmark, drawn in the theme's text colour (black on light, white on dark, as the guidelines ask). The kit's favicon, its icons (arrow, book, gift, album, delivery, preview, upload, sun, moon, star, edit), Heebo 700 for headings and buttons and 400 for body, and its radii (16 buttons, 24 cards, 32 large) are used too. The kit's hero and product scenes are concepts, so the site keeps the store's real pictures.

## Versions (17 / 11 / 2026)

Yarin, the same evening: "merge the purple and the orange into one ... yellow for CTAs", "those colors for the bg", then "i need a yellow and purple versions again" and "make it monochrome with a slight tint of the purple and yellow". Three versions, each in light and dark, all sharing the glass, paper, motion and shapes; only colour slots change (`site.css`, top):

- **Purple tint** (`data-dir="purple"`, the default): monochrome greys with a faint purple cast, ink-black buttons (white in dark), dusty purple `#5C4D80` (dark `#B8ACD6`) for selection, links, stars and progress, a lavender highlighter on the headline.
- **Yellow tint** (`data-dir="yellow"`): monochrome greys with a faint warm cast, ink-black buttons (white in dark), dusty ochre `#6E5C26` (dark `#D9C88F`) for selection and links, a yellow highlighter.
- **Purple + yellow** (`data-dir="both"`): the merged palette, purple brand with yellow buttons on cream `#FBF8F2` and sand `#F6EFE1` bands.

Product pictures and the logo keep their own colours in every version. Every text pair is 4.5:1 or more (checked with a script). Section bands alternate by position, so any order made with the edit button keeps alternating.

The version is a dev choice: a black `DEV` bar at the bottom (on localhost or with `?dev=1`, never inside an iframe) switches Purple, Yellow and Both and remembers it in `localStorage` `lbh-dir`; `?dir=purple|yellow|both` shows one without storing it. `compare.html` shows all six combinations.

## Order: gift books first (17 / 11 / 2026)

Yarin: "make the website focus on the ספר מתנה first, then the kid books and then the photo album". `ORDER` in `src/build.py` is gift, kids, albums, and everything follows it: the header and drawer, the hero picker (gift selected, the gift books lead the hero composition), the category rows, the personalisation tabs, the gallery and its filters, the comparison table (its row values are keyed by category, so columns can move), the FAQ groups, the final cards and the footer.

The emphasised headline words are plain accent-coloured text (the highlighter stripe was removed: "the highlighter behind the words in the hero is ugly"). The hero's soft light field belongs to the page, starts above the floating header and fades out below the hero ("the gradient in the bg gets cut where the navbar is"); `html { overflow-x: clip }` keeps it from widening the page.

## Apple layer: Liquid Glass, skeuomorphism, motion

Yarin, 17 / 11 / 2026: "implement apple design system principles and animations, liquid glass and skeumorphism". The section at the end of `site.css`:

- **Liquid Glass** on the control layer only (same recipe as `shared/design/lumebook.css`): the header floats as a glass capsule that tightens on scroll, menus, the phone drawer, sheets and toasts are thick glass, carousel arrows are clear glass, segmented controls (tabs, filters, appearance, sign-in tabs) have a glass thumb that slides with a spring. Content cards are lit, near-opaque glass cards without blur (no blur on anything repeated). Light follows the pointer across the header, the picker tiles, the final cards and every yellow button.
- **Skeuomorphism** for real objects: covers are books with a spine on the right (Hebrew books bind on the right), stacked page edges and gloss, standing on a shelf and straightening on hover; preview pages are paper with grain and a gutter; the order summary is a paper receipt with a torn edge; customer photos are prints with white borders, yellow washi tape and a slight tilt; radios and checkboxes are sockets with a glossy purple bead; fields are pressed-in wells.
- **Motion**: real spring curves (a damped spring sampled into CSS `linear()`, with cubic fallbacks), the hero rising in on load, a slow light field behind it, hero products drifting at different speeds as you scroll (scroll-driven animations, wide screens only), studio steps sliding in from the reading direction, preview pages swinging in on their spine, sheets rising and falling, buttons pressing in, a circle of the new appearance growing from the switch (View Transitions). Everything turns off under Reduce Motion.

## Appearance

- First visit follows the device (`prefers-color-scheme`). The sun or moon in the header switches; the footer and the phone drawer have בהיר / כהה / לפי המכשיר. The choice is kept in `localStorage` `lbh-theme`; an inline script in `<head>` applies it before paint, so there is no flash. `?theme=light|dark` shows a mode without storing it (`compare.html` uses it to show both side by side).

## The creation studio (added 17 / 11 / 2026, Yarin: "i need a working demo of the entire product creation process")

Every start button opens the studio over the page; a modifier click (cmd, ctrl, shift) still opens the store, and the studio's top bar links to the real flow.

- **Kids book**, five steps: the hero (name, age 1 to 10, boy or girl, language, as the store's wizard asks), the story (11 best sellers, cover in the chosen version), the photo, a preview, the order. The preview uses the book's real title line and first three pages with the child's name marked; the pictures are the book's cover art, and the screen says so (the real book draws the child in every picture). Order: one book 119 ₪ plus delivery, or 3 for 347 ₪ or 5 for 545 ₪ with delivery, digital copy free.
- **Gift book**, five steps: who it is for (occasion, one person or a couple, name, from, relationship), about them (traits, a few words, a shared memory, a dedication), the cover (photo as is or as an illustration, optional title), a preview (cover, dedication, a sample chapter outline marked as a sample, and the first chapter's place with what they wrote), the order (199 ₪, the three extras at 49, 45 and 25 ₪, delivery).
- **Album**, four steps: the photos (from the device, shrunk in the page, up to 60; or a link, which in the demo loads the store's sample pictures), what matters (note and title), the album (auto layout of 1, 2 or 3 photos a page into spreads, cover picker, title), the order (149 ₪ a copy plus one delivery).
- Delivery everywhere: home 30 ₪ (up to 7 business days), Jerusalem pickup free, Rishon LeZion point 20 ₪ (up to 14).

## The pretend account

Person icon in the header (and in the phone drawer). Sign up (name, email, password of 8 or more), log in, wrong password and unknown email errors, "forgot password" says there is none in the demo, log out. Ordering asks to sign up or log in first and then completes the order. הספרים שלי lists drafts (saved when a preview is reached) and pretend orders with their numbers.

Everything stays in this browser: `localStorage` `lbh-users` (name and a salted SHA-256 of the password, never the password), `lbh-session`, `lbh-books:<email>`. Nothing is sent anywhere and there is no payment step. Every screen says "דמו" and asks not to use a real password.

## Corners

Every rounded corner is an Apple style squircle (`corner-shape: squircle` on every element under `@supports`, radius tokens raised so the curve keeps its size). Browsers without `corner-shape` keep plain rounded corners. Round avatars and dots become squircles too.

## Where every action goes

Without the studio script (or with a modifier click), every start button leads to the store's own flow: kids `/IL/he/wizard`, gift `/IL/he/gift-books/create`, albums `/IL/he/albums/create`. Book cards open `/IL/he/books/<id>`, the gift sample opens the store's PDF and its "what was entered" page, footer links go to the store's privacy, terms, accessibility, tutorials and contact pages. Campaign parameters in the address (`utm_*`, a creator's link, click ids) are copied onto every store link and every link between the demo pages, so attribution survives the new home page. A click on a start button pushes `{event: 'start_flow', flow, placement}` to `dataLayer` when there is one.

Proposed routes for the real store: the unified home at `/IL/he`; today's kids landing content moves to a kids category page (the demo's `kids.html`); `/IL/he/gift-books` and `/IL/he/albums` keep their addresses; every flow and book address stays as it is.

## Facts used (read on lumebook.com, 17 / 11 / 2026)

| | Kids book | Gift book | Album |
|---|---|---|---|
| Price | 119 ₪ (149 ₪ struck, "limited time"); 3 books 347 ₪, 5 books 545 ₪ with delivery | 199 ₪ launch price (299 ₪ struck); extras: pictures and illustrations +49, editing +45, digital copy +25 | 149 ₪, design included |
| Format | 22×22 cm, soft cover, 24 pages, dedication page | printed; page count depends on the story (sample: 52 inner pages, 10 chapters) | 22×22 cm, soft cover, up to 40 pages, 170 g chromo paper |
| Before paying | free preview | cover, chapter outline and first chapter; the full book is written after payment | the whole album, editable, approved before payment |
| Delivery | 30 ₪, up to 7 business days | "printed book and delivery by order", shown before payment | 30 ₪, about 7 business days |

Shared: one delivery fee for everything ordered the same day ("צירוף למשלוח קודם מהיום"), free pickup in Jerusalem, a Rishon LeZion pickup point for 20 ₪. Kids books: Hebrew, English, Arabic or Russian; digital copy free. The Hanukkah offer (every extra book 99 ₪) appears only on the kids page.

## Pictures

| Where | Pictures | Source |
|---|---|---|
| Kids photo to cover (hero, demo) | `/hero/series2..5-transparent-768.avif` | the store's home hero: its own photo and cover pairs |
| Kids covers | `/book_covers/<girl|boy>/B<id>_<g>.webp` | the store (B2 and B7 are left out: a kippah on the cover; B67 has garbled text) |
| Kids open pages | `../lumebook-partners/img/book-open.webp`; `img/kids-open-*.webp` | the Partners page's open book; drawings from `media/projects/2026-11-11-reel-broll-pool/drawn/` (cropped). Both are illustrations of pages and are labelled so |
| Gift books | `/adult-books/three-adult-books-1280.webp`; `img/gift-*.webp` | the store's photo; pages rendered from the store's sample PDF (`/adult-books/sample/sample-book.pdf`), whose input page says the people and details are made up |
| Albums | `/albums/marketing/*` | the store's album page. The store itself says these people are generated; the demo labels them "דוגמאות להמחשה. האנשים בתמונות אינם לקוחות" instead (project rule: no AI wording in audience copy) |
| Customers | `/ugc/ugc-*-384.webp` with the store's captions; `ugc-couch.webp` | photos the store already shows on its home page. `ugc-books` and `ugc-mor-story` are left out (AI wording burned into them) |
| Reviews (carousel) | nine public reviews, word for word, first name and initial: six on Google, two Facebook recommendations, one Instagram comment from a buyer. The bold line on each card is an exact part of its review | `media/projects/2026-11-15-social-proof/data.json`. Left out: private WhatsApp messages, a creator's paid post, and anything with AI wording. There is no picture of the reviewer's book: the reviews do not say which book they bought |
| Logo | `shared/brand/lumebook-wordmark-honey.svg` | the store's wordmark (`/adult-books/brand/lumebook-primary-honey.svg`), drawn in the theme's ink and accent |

## Open questions for the store team

- The kids page says ages 1 to 10 in its hero and 2 to 8 in its FAQ data. The demo says 1 to 10 and points to each book's own ages.
- The struck 149 ₪ and 299 ₪ prices (the CRO report already flags struck prices as a legal question).
- Gift books: delivery time and print format are not stated on the store page; the demo does not state them.
- Album and gift sample pictures show made-up people; the store says so with AI wording, the demo with "for illustration". Which wording the real site uses is the store's call.
- There are no customer photos or reviews of gift books or albums yet; the customer section shows kids books only and says so.
- Heebo is loaded from Google Fonts (400, 500, 600, 700, 800).
