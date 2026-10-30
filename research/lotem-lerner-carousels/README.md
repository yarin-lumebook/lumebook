# @lotem_lerner carousel teardown (29 Oct 2026)

Lotem Lerner: Israeli nurse, sleep and breastfeeding consultant, 18.4K followers, 100 posts (profile read 29 Oct 2026). Of the 100, **52 are carousels** (45 Reels, 3 single images), May 2025 to 25 Oct 2026. All 52 were read slide by slide (592 slides).

Internal study only. Her slides stay in `media/projects/2026-10-29-lotem-lerner-carousels/` (not in git, never re-post).

## Files

| File | What |
|---|---|
| `src/posts.json` | All 100 posts as captured from her logged-in profile grid (type, slide count, likes, comments, caption, slide image links that expire) |
| `src/dossiers/<code>.json` | One per carousel: date, counts, caption, video slides |
| `src/coded/<code>.json` | One per carousel, coded by Sonnet agents from `src/AGENT_BRIEF.md`: topic, hook text, hook type, voice, art, layout, slide-by-slide roles, CTA keyword and positions, takeaway |
| `src/all_coded.json` | The coded files joined with date, likes and comments |
| `src/download.py` | Downloads slides and builds the reading sheets (rerun only with fresh links in `posts.json`) |

Checked by hand against the slides: DaK3TJUDNY0, DeWtNXkDOqI, DecgjMvDG_A, DKUdSFpM-aA. Agents marked a few body lines `[unclear]` (thin body font); headlines and keywords are exact.

## What performs (median likes / comments)

Counts are from 29 Oct 2026. Her account grew over the period, so newer posts get more of everything; the 2026-only line below holds time roughly still. Small groups, read as direction, not proof.

| Split | Carousels | Likes | Comments |
|---|---|---|---|
| Child speaks to the parents (whole or most of it) | 12 | 793 | 1,028 |
| Lotem speaks to the parents | 40 | 116 | 249 |
| Same split, 2026 only: child voice | 12 | 793 | 1,028 |
| Same split, 2026 only: Lotem voice | 14 | 130 | 301 |
| Comment-keyword offer on the slides | 44 | 176 | 501 |
| No keyword | 8 | 41 | 20 |
| 14+ slides | 15 | 467 | 533 |
| 10 slides or fewer | 24 | 101 | 176 |
| Development and behaviour by age | 13 | about 440 to 760 | about 490 to 630 |
| Sleep (her main subject) | 32 | 118 | 278 |

Top 5 by likes, all 3D animated, all age-stage behaviour or development: DaK3TJUDNY0 "מה אני מנסה לספר לכם בגיל שנה" (1,818 / 2,519), DbDeDUrjPq9 "התנהגויות בגיל 6-8 חודשים" (1,501), DecgjMvDG_A "התנהגויות בגיל שנה - שנה וחצי" (1,344), DeroqOSkT-p "שנה וחצי - שנתיים" (1,196), Dc6cRZTEagc "8-11 חודשים" (1,052). Bottom: her first flat-graphic tip cards and real-photo posts (22 to 71 likes).

## How she builds them

**Visual**
- 3D animated, Pixar-like, one family that repeats across posts: curly-haired mom, bearded dad, toddler or baby. 35 of 52 are 3D; the oldest 2025 ones were flat purple cards and real photos.
- Warm night palette: purple, lavender, amber lamp light. Same picture world on every slide of a post.
- Slide 1: the child's face with a big emotion (crying, pouting, cheeky), headline in heavy white on the picture, one red pill under it with the age or "ואיך להגיב אליהן".
- Inner slides: small label at the top ("1: חרדת נטישה"), light headline, 2 to 4 body lines with one or two words in heavy bold. Logo top-right, handle and a small disclaimer at the bottom.

**Topics**
- Ages and stages win: "התנהגויות בגיל X ואיך להגיב אליהן" became a series (6-8m, 8-11m, 1y, 1.5y, 2y). Sleep is most of what she posts but does less.

**Hook**
- Two forms carry the top posts: the child's confession ("אמא..אבא.. הלוואי שהייתם מבינים אותי", "מה אני מנסה לספר לכם") and an age-plus-list title ("התנהגויות בגיל שנה - שנה וחצי"). Questions and "the mistakes you make" lists sit in the middle.

**Content (the point slide)**
- Three parts, same every time: the child says it ("אני מביע התנגדות על הכל בערך"), then "אבל מה שבעצם קורה זה" (her reframe), then "אז מה עושים?" (one action). 8 to 10 numbered points.
- Long: the best ones run 14 to 16 slides.

**CTA**
- A comment keyword tied to the topic ("פעוט", "גיל שנה", "חדר", "טנטרום"), promising the full explanation in DMs. 44 of 52 have one.
- Repeated inside the post, every 2 to 3 slides, on the slide where she cuts the explanation short: "להסבר המלא - כתבו 'חדר' ואשלח לכם בפרטי". This is likely why comments often beat likes.
- Fixed ending in 25 posts: about-me slide (her real photo, credentials, "אני כאן בשבילכם"), a reviews slide (WhatsApp screenshots), then "אם אתם חדשים כאן... עקבו ושתפו" with like, share and save icons.
- Captions are short: a title line plus the keyword again.

## For LumeBook

- Our kid carousels already use her strongest form (child to parents, 3D, one picture world). Her data backs it: in 2026 the child voice got about 6 times the likes of her own voice.
- Worth testing: the three-part point slide (child line / what is really going on / what to do), an age-stage series ("מה אני מנסה לספר לכם בגיל 3"), 12 to 15 slides instead of 10, and a keyword repeated mid-post where a book or a free guide fits naturally, not only on slide 10.
- Different from our rules: she adds an about-me and a reviews slide (we keep the brand out), and she uses dad in the picture.

## CTAs and captions (30 Oct 2026)

Read from `src/all_coded.json` (coded CTA slides, `cap` = her full caption) for all 52 carousels. Medians, small groups, confounded by voice and topic (the child-voice posts are also the ones with the shortest captions), so read as direction.

### CTA on the slides

- **Keyword pill repeated, 2 or more times before the closing slides**: median 309 likes / 571 comments (25 posts) vs 104 / 200 with fewer (27 posts). Best ones: "גיל שנה" (slides 10, 12), "פעוט" (slides 2, 4, 7, 9), "התנהגות" (4, 7, 9, 12).
- **One keyword per post, one word, the topic itself**: "פעוט", "גיל שנה", "טנטרום", "חדר", "אחים", "חג", "אוטו", "מזגן", "שעון". Never a generic word like "מדריך" on the top posts, except DaK3TJUDNY0 and Dacu5bDjLDw ("מדריך" next to a guide that sorts things out).
- **Wording patterns on the slide (her words, for structure only):**
  - the cut-off: the explanation stops, then "להסבר המלא / הגיבו פה ״X״ ואשלח לכם"
  - the promise sentence: "הבנה של התינוק שלנו זה הצעד הראשון, לדעת איך להגיב זה העיקר" + comment keyword
  - the stakes line before it: "אז בפעם הבאה שזה קורה... תזכרו משפט אחד" + keyword
  - the guide line: "לוטם הכינה מדריך על מה שעובר עלי... הגיבו פה ״X״" (in child voice posts she refers to herself in third person, the child talks about "her" guide)
  - a mid-post question as the CTA: "מה באמת קורה בעייפות יתר? הגיבו פה ״עייפות״"
- **Last slides**: about-me, then "אם אתם חדשים כאן... עקבו אחריי ושתפו" (22 of 52). Older posts: "עקבו אחריי, שמרו ושלחו להורים שחייבים לדעת את זה". Not the driver of results.
- **Coupon / product pills** (Ddqnlj1jG8H, one keyword per product, code "lotem") got 100 likes: a shopping list does not travel like a topic.

### Captions

- **Short**: 13 captions of 60 characters or less got 186 likes / 705 comments; 61 to 200 characters 213 / 389; over 200 characters 101 / 203. The top 5 by likes all have a one-line caption.
- **The top child-voice and age-stage posts carry a title only**, or title plus keyword: "גיל שנה - קווים לדמותו", "התנהגויות בגיל 8-11 חודשים 🙂", "התנהגויות נפוצות בגיל שנה- שנה וחצי - להסבר המלא הגיבו ״פעוט״ ואשלח לכם לפרטי 👇🏻".
- **Keyword in the caption is not what drives comments**: 23 captions ask for the keyword (115 likes / 206 comments), 29 do not (226 / 510). The keyword on the slides does the work; the caption only repeats it on the posts that are less strong. Keep it in the caption anyway where there is room, it is the first thing under the post.
- **Shapes that repeat**:
  1. Title line only.
  2. Title + one line with the keyword: "הגיבו ״X״ ואשלח לכם את ההסבר המלא".
  3. Question + normalising line + the promise ("כתבתי לכם 10 טיפים... כתבו ״צינון״ ואשלח לכם").
  4. The "forgot to say" line: "וואי אפילו שכחתי לציין שמי שיגיבו ״מדריך״ יקבלו גם..." (Dacu5bDjLDw: 633 likes, 1,752 comments, the highest comments-to-likes of the top 10).
- **Punctuation and emoji**: she keeps quotes around the keyword (״X״), ♥️ 👇🏻 💜 at the end, rarely in the middle. Posts with an emoji got fewer likes (112 vs 186), but they are the older, Lotem-voice ones, so no conclusion.
- **Medical disclaimer** in 15 captions (115 likes vs 184 without): she is a nurse, we are not; LumeBook should not copy it.

### For LumeBook

- Keep captions to 1 to 2 lines: the hook topic, then one line asking for the keyword and promising what lands in the DM. Matches what Yarin already approved ([[feedback-post-text-emojis]]: one emoji on hook, one on CTA).
- Test the keyword on two or three slides, on the slides where the text is cut short, not only on slide 10. A keyword needs a thing to send (a free guide, a book idea list); decide what that is before using one.
- Do not copy: about-me and reviews slides, the medical disclaimer, the coupon code, the third-person "Lotem prepared a guide".
