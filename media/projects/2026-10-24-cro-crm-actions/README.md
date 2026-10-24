# CRO and CRM page pictures (24 Oct 2026)

Small WebP copies that the two `research/cro-crm/` builds embed: `src/build_strategy_page.py` (the Hebrew action list in `cro-crm-strategy.html`) and `src/build_journey_demo.py` (`journey-demo.html`). Both leave a picture out when its file is missing, so the pages still build without this folder (the demo then shows a bare screen instead of the iPhone).

| File | Source | Used for |
|---|---|---|
| `cover-birthday-girl.webp` (360 px) | lumebook.com/book_covers/girl/B15_girl.webp, the birthday book's cover on the live site (24 Oct) | the Facebook ad sketch, stage 1 |
| `cover-birthday-boy.webp` (200 px) | lumebook.com/book_covers/boy/B15_boy.webp | the ₪79 extra-book row, stage 6 |
| `cover-hanukkah-girl.webp` (200 px) | lumebook.com/book_covers/girl/B86_girl.webp ("החנוכה שלי") | the Hanukkah order-by row, stage 2 |
| `lume-magic.webp` (240 px) | lumebook.com/LumeCharachter/LumeMagic.webp, the mascot as the site shows it | the "start with these five" card |
| `iphone-frame.webp` (1024 x 1536) | the iPhone mockup Yarin supplied in chat, 24 Oct (transparent screen and background) | the original, kept as sent |
| `iphone-frame-crop.webp` (698 x 1397) | `iphone-frame.webp` cropped to the phone; the screen opening is x 44 to 652, y 35 to 1360, corner radius about 85 px | the frame over the demo's 393 x 856 screen |
| `cover-birthday-girl-640.webp`, `cover-birthday-boy-640.webp` (640 px) | lumebook.com/book_covers/girl/B15_girl.webp and boy/B15_boy.webp | the covers inside the demo's phone (ad, book page, wizard, preview) |
| `book-birthday-hila-mockup.webp` (560 px) | resized from `../2026-10-16-genjutsu-truck-box/inputs/book-birthday-hila.webp` (the book mockup Yarin supplied) | the section's hero picture |
| `cardcom-payment-page-iphone.jpg`, `cardcom-shipping-picker-iphone.jpg` | Yarin's iPhone screenshots of the CardCom payment page in Safari, sent in chat 24 Oct 22:28 (full page, and the open shipping picker) | evidence only, not embedded: `research/cro-crm/audit.md` step 9 and A25, `sources.md` O-cardcom-phone |

The covers are the store's own catalogue art and also sit in the Drive "שיווק" folder as `cover_book*.png`. Resized with Pillow (`/usr/bin/python3`, quality 80).
