# Brief: classify Hebrew Instagram comments for LumeBook research

## Context
LumeBook (לומיבוק) sells personalised children's books in Israel. We study which creator posts make parents show interest in buying something. You classify audience comments on Instagram posts by Israeli parenting creators. Each comment file covers one creator's selected posts: `comments/<handle>.json` with, per post, the caption, the post role (strong = the creator's best recent post vs their own median; ordinary = a typical post; relevant_kw = a post whose caption mentions a buying occasion, books, gifts or an offer), the comment-keyword CTA if any, and up to 30 top-level comments as Instagram's web client returned them (with any preview replies).

## Categories (choose ONE primary per comment)
- `identification`: says the problem/situation is theirs ("זה בדיוק הבן שלי", "גם אצלנו", "מרגישה ככה").
- `personal_experience`: tells their own story or detail beyond identifying.
- `practical_help_request`: asks how to handle something, asks for advice or a recommendation (not about buying a specific product).
- `product_or_price_question`: asks about a product, brand, price, where to buy, link, size, age fit, shipping time, how to order.
- `objection`: doubt or complaint about delivery, personalisation, quality, price, trust, safety or the creator's claim.
- `explicit_buying_intent`: says they want to buy/order/get it ("חייבת כזה", "הולכת להזמין", "איך מזמינים? רוצה").
- `purchase_report`: says they already bought/ordered/have it ("הזמנתי", "יש לנו", "קנינו"). Self-reported.
- `keyword_request`: the comment is just the keyword the post asked people to comment in order to receive a link, file or DM (e.g. the caption says comment "ספר" and the comment is "ספר"). Count it separately: it is a request for the offer, a consideration proxy, not organic intent.
- `tag_or_share`: tags another person with little or no text, or says they are sending it to someone.
- `giveaway_entry`: entering a giveaway (tags, "משתתפת", "רוצה לזכות").
- `generic_praise`: praise, emoji, laughter, compliments, "מהממת", "חחח", hearts.
- `creator_reply`: written by the post's own account (compare username with the creator handle).
- `spam_or_unrelated`: promotion of another account, bots, off-topic.

Also mark per comment:
- `about_offer`: true if the comment refers to the product, brand, service, link, price or offer shown in the post (not just the topic).
- `gift_mention`: true if it mentions buying for someone else (grandchild, niece, friend's child, a gift).
- `occasion`: a LumeBook buying occasion the comment mentions: birthday, new_sibling, pregnancy, pacifier, potty_diaper, gan_start, first_grade, bedtime, holiday, none.

## Rules
- Read the Hebrew yourself. Do not infer age, gender beyond grammar, parenthood, location or income from usernames or names. Grammatical gender of the comment is fine to note only if relevant; do not record it otherwise.
- Quote at most 12 words of any comment in your examples; no usernames in examples (use the comment id).
- No em dashes.

## Output
Write `comments_coded/<handle>.json`:
```
{"handle": "", "posts": [
  {"code": "", "n_comments": 0, "n_unique_commenters": 0, "n_creator_replies_top_level": 0,
   "counts": {"identification":0, "personal_experience":0, "practical_help_request":0, "product_or_price_question":0, "objection":0, "explicit_buying_intent":0, "purchase_report":0, "keyword_request":0, "tag_or_share":0, "giveaway_entry":0, "generic_praise":0, "creator_reply":0, "spam_or_unrelated":0},
   "about_offer": 0, "gift_mention": 0, "occasions": {"birthday":0},
   "creator_replies_in_threads": 0,
   "examples": [{"id": "", "class": "", "he": "short Hebrew quote", "en": "English gloss"}],
   "summary": "2 sentences: what the audience talks about, and whether anything signals buying interest. Separate what commenters SAY from your interpretation."}
]}
```
`n_unique_commenters` counts distinct usernames among the top-level comments, excluding the creator. `creator_replies_in_threads` counts preview replies written by the creator. Include 3 to 6 examples per post, prioritising buying intent, product questions, objections, help requests and identification over praise. Validate with python3 at the end and reply with a 3-line summary.
