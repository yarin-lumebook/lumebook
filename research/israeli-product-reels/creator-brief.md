# Creator brief: a Reel about your LumeBook book

For Yarin, 15 Oct 2026. A short brief LumeBook can send to barter creators who film one Reel about their personalised book. Nobody has been contacted.

- **Built from:** `playbook.md` approach A "Story with a turn" and section 3 "Weaker choices", `breakdowns.md` deep dive 1 ([@shoham_novik × LumeBook](https://www.instagram.com/reel/DTugYwmDNKa/)), product facts in `src/product-facts-2026-10-15.md`, the creator offer in `shared/facts.json`.
- **Your edits (15 Oct, site editor) are in:** no hero intro, no "honest close" step, no price worry, no do-not rules on explaining the illustrations or on codes, no checklist, plus your rewrites. Small follow-on fixes: "שבעה חלקים" became "שישה חלקים", the CTA moved to 29-32 s so the times stay continuous, "משפטים אמיתיים" (plural), the disclosure quote closed and spelled LumeBook, and 24 pages as you confirmed (lumebook.com/IL/he said 24 on 15 Oct).
- **Added on 15 Oct at your request:** creators send their raw footage to yarin@lumebook.com, a full worked example (a pacifier Reel, beat by beat), and the page redesign (Heebo only, icons, phone-screen layouts, a caption preview).
- **Hebrew voice:** the LumeBook Hebrew voice skill in its fallback voice (12 of the 15 approved samples it needs). Creators are addressed in the plural and the example lines are first person past tense, so nothing assumes the creator's gender (`creators/creator-research/src/hebrew-rules.md`). Every Hebrew block passes `voice_lint.py`: `python3 research/israeli-product-reels/src/lint_creator_brief.py` (`--text` prints the Hebrew as plain lines for a DM).
- **Page:** https://claude.ai/artifact/T9DJuNSzHoQ2WNHzceZq8L (private until you share it), built from the Hebrew part by `src/build_creator_brief.py`. Render hints in the Hebrew part are HTML comments, invisible in the Markdown: `<!--icon:NAME-->` on a heading, step or item, `<!--as:ticks-->` on a paragraph (first line is a label, the rest a tick list), `<!--visual:screens|topic|email-->` as its own block. After editing the Hebrew: lint, `python3 tools/lumebook.py build creator-brief`, republish the HTML, then `python3 tools/lumebook.py ack creator-brief --published`.
- **Public site (for creators):** https://lumebook-creator-brief.vercel.app (its own Vercel project, `noindex`), the same page as a full document in `sites/lumebook-creator-brief/`, written by the same build. After a rebuild: `python3 tools/lumebook.py deploy creator-brief`.

## How the brief maps to the research

| In the brief | Where it comes from |
|---|---|
| Problem or moment in the first line, book on screen within 1 second | Shoham's opening (cover at 0:01); 35 of 41 Reels show the product within 2 s (`playbook.md` section 1) |
| Home footage, one short screen recording, page close-ups | Shoham 0:04-0:47; "show the ordering flow once, for three or four seconds, inside a story" (section 3) |
| One buyer worry answered with a checked fact | Shoham's delivery question at 0:28; facts read on lumebook.com on 15 Oct |
| CTA on screen and as the caption's last line | Shoham and @etti_haft had the CTA only in the caption (section 3) |
| One topic in hook, video and caption | Shoham's caption sold a birthday gift on a potty-training video |
| Collaborator invite to @lumebook.il plus a plain disclosure line | Disclosure was loose in the sample, 0 of 41 used the paid-partnership label (section 1, point 8) |
| Subtitles clear of overlays, nothing in the bottom fifth or at the sides | Shoham 0:11-0:27; the bottom fifth and right edge are the playbook's working rule, not a measured fact (sections 3 and 6). The brief says "the sides" because I haven't checked whether Instagram's Hebrew interface moves the buttons to the left |
| About 32 seconds | The playbook's 20 to 35 s is a production choice with no watch-time data behind it |

## Decide or check before sending

1. **Price and delivery.** The brief tells creators the facts were checked on 15 Oct 2026 and that LumeBook will confirm them before they post. Re-check lumebook.com each time (up to 7 business days for home delivery, digital copy by email within minutes, free preview, 24 colour pages).
2. **The personal link must exist first.** Each creator needs their link and their split of the 25% before filming. Still open in `shared/facts.json`: how the sale value is calculated, payout, how the link is tracked at checkout, whether the split can change.
3. **Who answers "לומי".** The CTA has the creator send their own personal link by DM. My understanding (not checked) is that a collab post shows one shared comment section on both accounts. If @lumebook.il runs a DM automation on "לומי" (I don't know whether it does), it could answer those comments with a generic link and the sale would not reach the creator's link.
4. **Raw footage.** The brief asks creators to email their unedited clips, screen recording, voiceover and final video. It says nothing about what LumeBook may do with them; if you plan to reuse them (ads, LumeBook's own posts), agree that with each creator in writing.
5. **Rules you removed.** The brief no longer tells creators not to explain how the illustrations are made, and no longer says "no codes, only the personal link". The project rules still apply to what they post (CLAUDE.md: no AI in audience copy; the offer is a personal link, never a code). Say it in the DM, or ask me to put the lines back.
6. **Professionals.** Approach A needs a real family moment. A therapist or gan teacher without their own child in that moment fits approach D ("talk with it in your hands", `playbook.md`) better; this brief doesn't cover it.
7. **Instagram handle in facts.** `shared/facts.json` still lists `brand.instagram` as `lumebookai`; the live handle is @lumebook.il (`playbook.md`, line 7). Not changed here.

## The brief (send this part)

<div dir="rtl" lang="he">

### בריף ליוצרים

### <!--icon:star--> דוגמה שאנחנו אוהבים

הסרטון של `@shoham_novik` עם הספר של הבת שלה<br>
הפחד מהגמילה בשורה הראשונה<br>
והספר על המסך כבר בשנייה הראשונה<br>
[לצפייה בסרטון](https://www.instagram.com/reel/DTugYwmDNKa/)

<!--as:ticks-->מה נוסיף אצלכם<br>
קריאה לפעולה על המסך בסוף<br>
כיתוב על אותו נושא כמו הסרטון<br>
כתוביות שלא מתנגשות בהקלטת המסך

### <!--icon:film--> שלד הצילום

שישה חלקים קצרים לפי הסדר<br>
הזמנים הם בערך

<!--icon:play-->**הפתיחה · 0 עד 3 שניות**<br>
הבעיה או הרגע שלכם במשפט אחד<br>
והספר על המסך כבר בשנייה הראשונה<br>
אותו משפט גם כטקסט בשליש העליון

למשל<br>
״לא ידעתי איך מתחילים גמילה מחיתולים״<br>
״המוצץ היה צריך ללכת ולא ידעתי איך״<br>
״חיפשתי מתנה ליום הולדת 4 שתהיה רק שלו״

רק אם זה קרה אצלכם<br>
ובמילים שלכם

<!--icon:home-->**הבית · 3 עד 10 שניות**<br>
צילומים אמיתיים מהבית<br>
קוראים יחד על הספה או לפני השינה<br>
טלפון יציב ותאורה טובה

<!--icon:phone-->**ההזמנה · 10 עד 14 שניות**<br>
הקלטת מסך אחת קצרה מהאתר<br>
בוחרים ספר<br>
מעלים תמונה<br>
ורואים את התצוגה המקדימה

הקלטת המסך בפינה העליונה<br>
או על כל המסך לשתי שניות<br>
ומסתירים מייל וכתובת ומספר הזמנה

<!--icon:book-->**העמודים · 14 עד 22 שניות**<br>
צילום מקרוב מלמעלה<br>
השם של הילד בתוך הסיפור<br>
ואם בא לכם גם התמונה שלו ליד האיור

<!--icon:help-->**דאגה אחת · 22 עד 29 שניות**<br>
אומרים בקול דאגה אחת של הורים לפני שמזמינים<br>
ועונים עליה בעובדה מהרשימה למטה

<!--icon:megaphone-->**הקריאה לפעולה · 29 עד 32 שניות**<br>
על התמונה הכי חזקה<br>
העמוד הכי יפה בספר או עמוד ההקדשה

### <!--icon:clapper--> דוגמה מלאה

רילס על פרידה מהמוצץ<br>
רק כדי להראות איך זה נראה<br>
צלמו את מה שקרה אצלכם

- **הפתיחה**<br>
  הספר ביד כבר בשנייה הראשונה<br>
  ״המוצץ היה צריך ללכת״<br>
  ״ולא ידעתי איך מתחילים״

- **הבית**<br>
  צילום רחב על הספה לפני השינה<br>
  ״הכנו לה ספר שבו היא הגיבורה״

- **ההזמנה**<br>
  הקלטת מסך קטנה בפינה העליונה<br>
  ״העליתי תמונה אחת שלה״<br>
  ״ובחרתי סיפור על פרידה מהמוצץ״

- **העמודים**<br>
  צילום מקרוב של השם שלה בסיפור<br>
  ״והנה היא בתוך הסיפור״

- **דאגה אחת**<br>
  דפדוף בעמודים מלמעלה<br>
  ״חששתי שזה לא יגיע בזמן״<br>
  ״משלוח עד הבית עד 7 ימי עסקים״<br>
  ״ועותק דיגיטלי מגיע במייל אחרי כמה דקות״

- **הקריאה לפעולה**<br>
  עמוד ההקדשה על המסך<br>
  והקריאה לפעולה כטקסט

### <!--icon:captions--> קריינות וכתוביות

מקליטים קריינות אחרי הצילום<br>
שמים כתוביות על כל הסרטון<br>
ובודקים כל מילה בעברית

<!--visual:screens-->

### <!--icon:target--> נושא אחד

נושא אחד לכל הרילס<br>
אם הפתיחה על גמילה<br>
גם הסרטון וגם הכיתוב על גמילה<br>
ולא על יום הולדת

<!--visual:topic-->

### <!--icon:help--> דאגה אחת ועובדה אחת

בוחרים אחת מהדאגות האלה<br>
העובדות נבדקו באתר ב-15 באוקטובר 2026<br>
ולפני שמעלים נבדוק איתכם שהן עדיין נכונות

- <!--icon:truck-->״זה יגיע בזמן?״<br>
  משלוח עד הבית עד 7 ימי עסקים<br>
  ועותק דיגיטלי מגיע במייל אחרי כמה דקות

- <!--icon:eye-->״זה באמת ייראה כמו הילד שלי?״<br>
  את התצוגה המקדימה רואים בחינם<br>
  ומשלמים רק אם אהבתם

- <!--icon:package-->״מה מקבלים בדיוק?״<br>
  ספר מודפס עם 24 עמודים בצבע<br>
  הילד על הכריכה ועוד 10 תמונות בפנים

### <!--icon:megaphone--> הקריאה לפעולה

אותו משפט על המסך בסוף<br>
ובשורה האחרונה בכיתוב

</div>

<div dir="rtl" lang="he" data-lint="cta">

> כתבו "לומי" בתגובות ואשלח לכם קישור לספר שבו הילד שלכם הוא הגיבור

</div>

<div dir="rtl" lang="he">

<!--icon:message-->לכל מי שכותב ״לומי״<br>
שולחים בהודעה פרטית את הקישור האישי שלכם<br>
ככה ההזמנה עוברת דרך הקישור שלכם

### <!--icon:message--> הכיתוב מתחת לסרטון

שורה ראשונה על אותו נושא כמו הפתיחה<br>
שורת גילוי נאות לפני הסוף<br>
והקריאה לפעולה היא השורה האחרונה

בזמן ההעלאה מזמינים את `@lumebook.il` כשותף לפוסט<br>
וגם כותבים שורת גילוי נאות בכיתוב<br>
צריך את שניהם

גילוי נאות פשוט<br>
״נוצר בשיתוף פעולה עם LumeBook״

אם בחרתם לתת לעוקבים הנחה מתוך ה-25%<br>
כתבו בכיתוב כמה הנחה יש בקישור

דוגמה לכיתוב<br>
החליפו את הסיפור במילים שלכם<br>
ושורת ההנחה רק אם בחרתם הנחה

</div>

<div dir="rtl" lang="he" data-lint="caption">

> לא ידענו איך מתחילים גמילה מחיתולים<br>
> אז הכנו לה ספר שבו היא הגיבורה<br>
> והיא ביקשה לקרוא אותו שוב ושוב<br>
> בקישור שלי יש 10% הנחה<br>
> שיתוף פעולה עם לומבוק<br>
> קיבלתי את הספר במתנה<br>
> ועל הזמנות דרך הקישור שלי מגיעה לי עמלה<br>
> כתבו "לומי" בתגובות ואשלח לכם קישור לספר שבו הילד שלכם הוא הגיבור

</div>

<div dir="rtl" lang="he">

### <!--icon:mail--> חומרי הגלם

שולחים גם את חומרי הגלם<br>
למייל `yarin@lumebook.com`

<!--visual:email-->

<!--as:ticks-->מה שולחים<br>
הצילומים המקוריים בלי עריכה<br>
הקלטת המסך והקריינות<br>
והסרטון הסופי

אם הקבצים גדולים<br>
אפשר לשלוח קישור להורדה

### <!--icon:x--> מה לא עושים

- <!--icon:alert-->לא מבטיחים תוצאה<br>
  לא ״נגמלה תוך שבוע״ ולא ״הפסיק לפחד״<br>
  מספרים רק מה קרה אצלכם ולמה אתם חושבים שזה יכול לעזור

- <!--icon:users-->ילדים של משפחות אחרות רק באישור בכתב מההורים שלהם<br>
  גם ברקע וגם בגן

- <!--icon:captions-->כתוביות מעל החלק התחתון של המסך<br>
  ולא צמוד לצדי המסך<br>
  שם אינסטגרם מכסה בכיתוב ובכפתורים<br>
  ושום שכבה לא עולה על הכתוביות

- <!--icon:quote-->בלי משפטי פרסומת<br>
  משפטים אמיתיים ואותנטיים

</div>
