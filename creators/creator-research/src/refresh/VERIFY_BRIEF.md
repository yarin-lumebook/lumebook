# Brief: find the purchase signals among Instagram comments (Hebrew)

Used by the weekly creator refresh (`comments.py cand` / `apply`). Same label definitions as the 14 Oct 2026 research (`research/creator-content-conversion/round2/CANDIDATE_BRIEF.md`), so the weekly numbers stay comparable.

You get `<dir>/in/NNN.json`: a list of reels, each `{c, cap, cm: [{i, t}]}` (reel code, caption excerpt, candidate comments). A broad keyword net picked these comments because they MIGHT be purchase signals. Most are not. Read each comment in Hebrew, with the caption for context.

A comment is a purchase signal when it is one of:

- `product_q`: asks where to buy, for a link to a product, the price, shipping or delivery, how to order, sizes, the name or brand of an item shown, or whether a product fits an age. A question about a product or service the post shows or mentions. Questions about the creator's own paid service (consultation, course) count. A trip destination, hotel or venue counts only if it asks how to book, the price, or where it is in order to go ("which hotel was it?" counts; "what a view" does not).
- `intent`: says they want to buy, order or get the product or service ("חייבת כזה", "אזמין", "רוצה להזמין", "בא לי גם כזה").
- `purchase`: says they already bought, ordered or own it ("קנינו", "יש לנו את זה", "הזמנתי").

Everything else is not a signal: asking for a free file, list, recording, guide, workshop link or WhatsApp group the creator offers; asking for advice that is not about buying; praise, jokes, stories, questions about the creator's life. If unsure, it is not a signal.

Write `<dir>/out/NNN.json` (same file name): a JSON array with ONLY the signals, `[{"c": "<code>", "i": 0, "l": "product_q"}, ...]`. An empty array `[]` when the batch has none. Check it parses with python3. Reply with the count per label. No em dashes.
