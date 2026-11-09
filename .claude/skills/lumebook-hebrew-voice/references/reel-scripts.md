# Writing a reel script (since 09 / 11 / 2026)

Yarin rejected the November reel scripts on 09 / 11 / 2026 as too much like an ad, too clean, one formula and not his voice. These rules come from the ten creators in the creator map who sell products best (evidence: `research/israeli-product-reels/ugc-seller-scripts.md`). They are patterns from 28 Reels, not proven rules; Yarin's reactions to the pilots decide what stays.

The reel's hard rules still apply (`reels.py lint`): 10 to 30 s, no price, no language options or digital copy, Yarin never speaks as a parent, the "לומי" CTA, plus this skill's punctuation rules.

## The test before anything else

Read the script out loud. If the brand or the book is the subject of most sentences ("יש ספר שבו...", "מחכה לכם...", "עם השם שלו והפנים שלו בכל עמוד"), it is an ad. Rewrite so a person and a moment are the subject, and the book is what happens in that moment.

## Seven moves

1. **Call out one person in one moment.** "סבתא שהנכד חוגג יומולדת החודש, תעצרי רגע." Not "ספר מושלם לכל ילד".
2. **Make it an answer.** If someone really asked (a "לומי" DM, a comment, a customer), say so: "שאלו אותי את זה בתגובות". Never invent a question; without a real one, start from the moment.
3. **A problem or a doubt first, then the turn.** "ואז", "הסתבר ש", "רגע, זה הוא?" The turn is shown, not claimed.
4. **Point and react while the camera sees it.** "תראו", "תסתכלו", "כן כן". The words describe what is on screen at that second (a page, the preview, the printed book).
5. **Keep one rough edge.** "בתכלס", "בקיצור", "תקשיבו", a small admission ("הכי הרבה זמן לקח לי לבחור סיפור"), an honest limit. Only true ones.
6. **To explain, count.** "דבר ראשון... דבר שני... והכי חשוב...", one fact per shot, with the number on screen.
7. **One ask, the word, done.** The default "לומי" CTA. Nothing after it.

## Never

- The brand or the book as the subject of the sentence ("יש ספר ש", "הספר הזה מושלם", "מחכים לכם").
- The same closing line in every reel. "עם השם שלו והפנים שלו בכל עמוד" is spent.
- A follower question, a time, a reaction or a customer story that did not happen. Mark any line that depends on something real as "only if true" in the script's notes.
- Catalogue lists of features with no shot to show each one.

## Writing for Yarin's voice

He is the man who builds the books and answers the DMs, so first person masculine ("הפעלתי טיימר", "אני שולח"), talking to parents (אתם) or to one grandmother (את). Short spoken lines, one thought each, at most 12 words a line (the lint counts). The hook line on screen stays at most 34 characters and 8 words, and the first spoken line says it.

## Structure and edit (since 09 / 11 / 2026, from the @matan.nistor study)

Evidence: `research/matan-nistor-reels/report.md` (his top 100 Reels against 20 weak ones from the same months; correlation in one account, so these are working rules, and `experiments.md` tests them). The seven moves above say how a line sounds; these say what the reel is built around.

1. **Something happens on screen.** A reel is built around an act or a reveal the viewer sees (a gift opened, a timer stopped, the name found on a page, a question answered), not around Yarin explaining. His talk carries it; it does not replace it. A story or reveal ran through 54 of his top 100 and 1 of the 20 weak ones.
2. **The first frame is the thing.** In the first second the viewer sees what the reel is about: this reel's cover with a readable name (in Yarin's hand, or beside him from the first frame, added in the edit), or the number it is about (a date, a timer). Never "any book I have" alone. The first spoken line makes sense with no context (72 of 100 against 8 of 20).
3. **A new picture for every line.** After the 2 s hook clip every voiceover line plays over its own owned shot that shows what the line says: a page, the cover, the preview screen, an object. No stock, no film clips, no cut back to Yarin's face in the middle.
4. **The payoff stays on screen.** Every reel names its payoff in `reels.json` (`payoff`): what the viewer sees when the reel pays off. What the hook promises is answered on screen. It is the last picture before the לומי card; practical lines (the photo from the parents on WhatsApp, the approval, delivery) go before it, and nothing new comes after it, except the order deadline right before the ask in a Hanukkah reel.
5. **Edits carry information.** On screen only what answers a question or proves something: a number, a date, a timer, a label. No confetti, stickers or decorative graphics, and no fast cutting for its own sake: cut where a new line starts.
6. **לומי after the payoff.** The ask comes once, after the reel has delivered. לומי reels are judged by DMs and books started from the reel's link (`reels.py link`), not by views: across 753 of his Reels, a comment-word caption brought 3.4 times the comments per view but reached his top tenth far less often (1.6% against 12%).

`reels.py lint` warns (M1 to M4) when a reel has no `payoff`, opens on any book without this reel's cover, cuts to Yarin's face mid-reel, or ends on a talking shot instead of the payoff.
