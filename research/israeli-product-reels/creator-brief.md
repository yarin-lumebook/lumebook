# Creator brief: a Reel about your LumeBook book

For Yarin, 15 Oct 2026. A short brief LumeBook can send to barter creators who film one Reel about their personalised book. Draft: nobody has been contacted and nothing is published.

- **Built from:** `playbook.md` approach A "Story with a turn" and section 3 "Weaker choices", `breakdowns.md` deep dive 1 ([@shoham_novik × LumeBook](https://www.instagram.com/reel/DTugYwmDNKa/)), product facts in `src/product-facts-2026-10-15.md`, the creator offer in `shared/facts.json`.
- **Hebrew voice:** the LumeBook Hebrew voice skill in its fallback voice (12 of the 15 approved samples it needs), so it is a careful guess at your voice. Creators are addressed in the plural and the example lines are first person past tense, so nothing assumes the creator's gender (`creators/creator-research/src/hebrew-rules.md`). Every Hebrew block below passes `voice_lint.py`: `python3 research/israeli-product-reels/src/lint_creator_brief.py` (add `--text` to print the Hebrew as plain lines for pasting into a DM or a document).
- **Send only the Hebrew part** ("The brief" below). The English is for you.
- **Page:** https://claude.ai/artifact/T9DJuNSzHoQ2WNHzceZq8L (private until you share it), built from the Hebrew part by `src/build_creator_brief.py` with copy buttons for the CTA and caption and a checklist creators can tick. After editing the Hebrew: lint, `python3 tools/lumebook.py build creator-brief`, republish the HTML, then `python3 tools/lumebook.py ack creator-brief --published`.

## How the brief maps to the research

| In the brief | Where it comes from |
|---|---|
| Problem or moment in the first line, book on screen within 1 second | Shoham's opening (cover at 0:01); 35 of 41 Reels show the product within 2 s (`playbook.md` section 1) |
| Home footage, one short screen recording, page close-ups | Shoham 0:04-0:47; "show the ordering flow once, for three or four seconds, inside a story" (section 3) |
| One buyer worry answered with a checked fact | Shoham's delivery question at 0:28; facts read on lumebook.com on 15 Oct |
| Honest close | Shoham's "not magic" close (the brief avoids the word, the voice skill bans it) |
| CTA on screen and as the caption's last line | Shoham and @etti_haft had the CTA only in the caption (section 3) |
| One topic in hook, video and caption | Shoham's caption sold a birthday gift on a potty-training video |
| Collaborator invite to @lumebook.il plus a plain disclosure line | Disclosure was loose in the sample, 0 of 41 used the paid-partnership label (section 1, point 8) |
| Subtitles clear of overlays, nothing in the bottom fifth or at the sides | Shoham 0:11-0:27; the bottom fifth and right edge are the playbook's working rule, not a measured fact (sections 3 and 6). The brief says "the sides" because I haven't checked whether Instagram's Hebrew interface moves the buttons to the left |
| 30 to 40 seconds | The playbook's 20 to 35 s is a production choice with no watch-time data behind it; seven beats need about 35 s |

## Decide or check before sending

1. **Price and delivery.** The brief tells creators the facts were checked on 15 Oct 2026 and that LumeBook will confirm them before they post. Re-check lumebook.com each time (₪119 printed, ₪30 home delivery, up to 7 business days, digital copy by email within minutes, free preview).
2. **The personal link must exist first.** Each creator needs their link and their split of the 25% before filming. Still open in `shared/facts.json`: how the sale value is calculated, payout, how the link is tracked at checkout, whether the split can change.
3. **Who answers "לומי".** The CTA has the creator send their own personal link by DM. My understanding (not checked) is that a collab post shows one shared comment section on both accounts. If @lumebook.il runs a DM automation on "לומי" (I don't know whether it does), it could answer those comments with a generic link and the sale would not reach the creator's link. Check before the first creator posts.
4. **Review before posting.** The brief does not ask creators to send their cut first. Add one line if you want to see it before it goes up.
5. **AI wording.** The do-not item says "don't explain how the illustrations are made, don't mention any technology or software" and never names AI itself, so the lint passes and the idea isn't planted. If a creator asks, say it plainly in the DM.
6. **Professionals.** Approach A needs a real family moment. A therapist or gan teacher without their own child in that moment fits approach D ("talk with it in your hands", `playbook.md`) better; this brief doesn't cover it.
7. **Instagram handle in facts.** `shared/facts.json` still lists `brand.instagram` as `lumebookai`; the live handle is @lumebook.il (`playbook.md`, line 7). Not changed here.

## The brief (send this part)

<div dir="rtl" lang="he">

### רילס אחד על הספר שלכם

תודה שאתם מצטרפים אלינו<br>
קיבלתם ספר אישי במתנה<br>
וקישור אישי עם הנחה לקהל

אנחנו מבקשים רילס אחד<br>
על רגע אמיתי שלכם עם הספר<br>
בערך 30 עד 40 שניות

מספרים רק מה שקרה אצלכם באמת<br>
ואם משהו לא עבד<br>
זה בסדר להגיד את זה

### דוגמה שאנחנו אוהבים

הסרטון של `@shoham_novik` עם הספר של הבת שלה<br>
הפחד מהגמילה בשורה הראשונה<br>
והספר על המסך כבר בשנייה הראשונה<br>
[לצפייה בסרטון](https://www.instagram.com/reel/DTugYwmDNKa/)

מה נוסיף אצלכם<br>
קריאה לפעולה על המסך בסוף<br>
כיתוב על אותו נושא כמו הסרטון<br>
כתוביות שלא מתנגשות בהקלטת המסך

### שלד הצילום

שבעה חלקים קצרים לפי הסדר<br>
הזמנים הם בערך

**הפתיחה · 0 עד 3 שניות**<br>
הבעיה או הרגע שלכם במשפט אחד<br>
והספר על המסך כבר בשנייה הראשונה<br>
אותו משפט גם כטקסט בשליש העליון

למשל<br>
״לא ידעתי איך מתחילים גמילה מחיתולים״<br>
״המוצץ היה צריך ללכת ולא ידעתי איך״<br>
״חיפשתי מתנה ליום הולדת 4 שתהיה רק שלו״

רק אם זה קרה אצלכם<br>
ובמילים שלכם

**הבית · 3 עד 10 שניות**<br>
צילומים אמיתיים מהבית<br>
קוראים יחד על הספה או לפני השינה<br>
טלפון יציב ואור מהחלון

**ההזמנה · 10 עד 14 שניות**<br>
הקלטת מסך אחת קצרה מהאתר<br>
בוחרים ספר<br>
מעלים תמונה<br>
ורואים את התצוגה המקדימה

הקלטת המסך בפינה העליונה<br>
או על כל המסך לשתי שניות<br>
ומסתירים מייל וכתובת ומספר הזמנה

**העמודים · 14 עד 22 שניות**<br>
צילום מקרוב מלמעלה<br>
השם של הילד בתוך הסיפור<br>
ואם בא לכם גם התמונה שלו ליד האיור

**דאגה אחת · 22 עד 29 שניות**<br>
אומרים בקול דאגה אחת של הורים לפני שמזמינים<br>
ועונים עליה בעובדה מהרשימה למטה

**סוף כן · 29 עד 33 שניות**<br>
מה היה טוב ומה הספר לא עשה<br>
בלי הבטחות

למשל<br>
״זה לא שהכל הסתדר בבת אחת״<br>
״אבל זה נתן לנו דרך לדבר על זה״<br>
רק מה שנכון אצלכם

**הקריאה לפעולה · 33 עד 36 שניות**<br>
על התמונה הכי חזקה<br>
העמוד הכי יפה בספר או עמוד ההקדשה

### קריינות וכתוביות

מקליטים קריינות אחרי הצילום<br>
שמים כתוביות על כל הסרטון<br>
ובודקים כל מילה בעברית

### נושא אחד

נושא אחד לכל הרילס<br>
אם הפתיחה על גמילה<br>
גם הסרטון וגם הכיתוב על גמילה<br>
ולא על יום הולדת

### דאגה אחת ועובדה אחת

בוחרים אחת מהדאגות האלה<br>
העובדות נבדקו באתר ב-15 באוקטובר 2026<br>
ולפני שמעלים נבדוק איתכם שהן עדיין נכונות

- ״זה יגיע בזמן?״<br>
  משלוח עד הבית עד 7 ימי עסקים<br>
  ועותק דיגיטלי מגיע במייל אחרי כמה דקות

- ״זה באמת ייראה כמו הילד שלי?״<br>
  את התצוגה המקדימה רואים בחינם<br>
  ומשלמים רק אם אהבתם

- ״כמה זה עולה?״<br>
  ספר מודפס 119 ש״ח<br>
  ומשלוח עד הבית 30 ש״ח

- ״מה מקבלים בדיוק?״<br>
  ספר מודפס 22 על 22 עם 24 עמודים בצבע<br>
  הילד על הכריכה ובעוד 10 תמונות בפנים

### הקריאה לפעולה

אותו משפט על המסך בסוף<br>
ובשורה האחרונה בכיתוב

</div>

<div dir="rtl" lang="he" data-lint="cta">

> כתבו "לומי" בתגובות ואשלח לכם קישור לספר שבו הילד שלכם הוא הגיבור

</div>

<div dir="rtl" lang="he">

לכל מי שכותב ״לומי״<br>
שולחים בהודעה פרטית את הקישור האישי שלכם<br>
ככה ההזמנה עוברת דרך הקישור שלכם

### הכיתוב

שורה ראשונה על אותו נושא כמו הפתיחה<br>
שורת גילוי נאות לפני הסוף<br>
והקריאה לפעולה היא השורה האחרונה

בזמן ההעלאה מזמינים את `@lumebook.il` כשותף לפוסט<br>
וגם כותבים שורת גילוי נאות בכיתוב<br>
צריך את שניהם

גילוי נאות פשוט<br>
שקיבלתם את הספר במתנה<br>
ושיש לכם עמלה על הזמנות דרך הקישור

אם בחרתם לתת לעוקבים הנחה מתוך ה-25%<br>
כתבו בכיתוב כמה הנחה יש בקישור

דוגמה לכיתוב<br>
החליפו את הסיפור במילים שלכם<br>
ושורת ההנחה רק אם בחרתם הנחה

</div>

<div dir="rtl" lang="he" data-lint="caption">

> לא ידעתי איך מתחילים גמילה מחיתולים<br>
> אז הכנו לה ספר שבו היא הגיבורה<br>
> והיא ביקשה לקרוא אותו שוב ושוב<br>
> בקישור שלי יש 10% הנחה<br>
> שיתוף פעולה עם לומבוק<br>
> קיבלתי את הספר במתנה<br>
> ועל הזמנות דרך הקישור שלי מגיעה לי עמלה<br>
> כתבו "לומי" בתגובות ואשלח לכם קישור לספר שבו הילד שלכם הוא הגיבור

</div>

<div dir="rtl" lang="he">

### מה לא עושים

- לא מסבירים איך נוצרים האיורים<br>
  ולא מזכירים שום טכנולוגיה או תוכנה<br>
  גם לא ״המערכת עשתה הכל״<br>
  מראים רק את התוצאה

- לא מבטיחים תוצאה<br>
  לא ״נגמלה תוך שבוע״ ולא ״הפסיק לפחד״<br>
  מספרים מה קרה אצלכם וזהו

- ילדים של משפחות אחרות רק באישור בכתב מההורים שלהם<br>
  גם ברקע וגם בגן

- כתוביות מעל החלק התחתון של המסך<br>
  ולא צמוד לצדי המסך<br>
  שם אינסטגרם מכסה בכיתוב ובכפתורים<br>
  ושום שכבה לא עולה על הכתוביות

- לא משפטי פרסומת<br>
  משפט אמיתי אחד לכל צילום<br>
  כמו ״היא צחקה כשראתה את עצמה״

- בלי קודים בכיתוב<br>
  ההנחה עובדת רק דרך הקישור האישי

### צ׳קליסט לפני שמעלים

- [ ] הרגע שלכם בשורה הראשונה והספר על המסך בשנייה הראשונה
- [ ] צילומים אמיתיים מהבית באור יום
- [ ] הקלטת מסך אחת של ההזמנה עד 4 שניות
- [ ] צילומי עמודים מקרוב
- [ ] דאגה אחת ועובדה אחת מהרשימה
- [ ] סוף כן בלי הבטחות
- [ ] נושא אחד מהפתיחה ועד הכיתוב
- [ ] כתוביות לאורך כל הסרטון בלי שכבות מעליהן
- [ ] אותה קריאה לפעולה על המסך ובשורה האחרונה בכיתוב
- [ ] גילוי נאות בכיתוב ו-`@lumebook.il` כשותף לפוסט
- [ ] אין ילדים של משפחות אחרות בלי אישור בכתב
- [ ] אין הסבר על איך נוצרים האיורים ואין קודים
- [ ] עונים בפרטי לכל ״לומי״ עם הקישור האישי

</div>
