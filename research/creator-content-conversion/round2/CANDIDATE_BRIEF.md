# Brief: verify possible purchase-signal comments (Hebrew, Instagram)

You get `cand/<batch>.json`: a list of posts, each with the post's creator, a caption excerpt and a list of candidate comments `{i, t}`. A broad keyword net picked these comments because they MIGHT be purchase signals. Most are not. Read each comment in Hebrew, with the caption for context, and give exactly one label:

- `product_q`: asks where to buy, for a link to a product, the price, shipping or delivery, how to order, sizes, the name or brand of an item shown, or whether a product fits an age. A question about a product or service the post shows or mentions.
- `intent`: says they want to buy, order or get the product or service ("חייבת כזה", "אזמין", "רוצה להזמין", "בא לי גם כזה").
- `purchase`: says they already bought, ordered or own it ("קנינו", "יש לנו את זה", "הזמנתי").
- `resource_request`: asks for a free file, list, recording, guide, workshop link or WhatsApp group the creator offers. A request for the creator's offer, not a purchase question.
- `help`: asks for advice or information that is not about buying (how to handle a child, what to do, when to start).
- `other`: anything else (praise, jokes, stories, questions to the creator about her life, place or trip details not tied to buying).

Rules:
- Questions about a trip destination, hotel or venue count as `product_q` only if the comment asks how to book, the price, or where it is in order to go. "Which hotel was it?" counts as `product_q`; "what a view" is `other`.
- Questions about the creator's own paid service (consultation, course) are `product_q`.
- Do not guess. If unsure between `product_q` and `help`, choose `help`.
- No em dashes.

Output `cand_out/<batch>.json`: `[{"code": "...", "i": 0, "label": "product_q"}, ...]`, one object per candidate comment, in input order. Validate with python3. Reply with counts per label.
