# Approval sheet · kid-1 · 2026-10-19

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
אמא  
6 דברים שרציתי  
להגיד לך על המוצץ  
ויעזרו לי להיפרד ממנו  

**2 · ההסבר**  
אני צריכה דרך חדשה  
להירגע בלי המוצץ  
זה לוקח לי זמן  
ואת יכולה ללמד אותי צעד צעד  

**3 · דוגמאות ממוספרות**  
1 תספרי לי ימים  
״רז בעוד 3 ימים נגיד ביי למוצץ״  
עד אז נתכונן ביחד  

**4 · דוגמאות ממוספרות**  
2 המוצץ נשאר רק במיטה  
״ביום אין מוצץ  
בלילה במיטה אפשר״  

**5 · דוגמאות ממוספרות**  
3 דובי שבחרתי בעצמי  
משהו רך לחבק בלילה  
במקום המוצץ  

**6 · דוגמאות ממוספרות**  
4 שלא יהיה בזווית העין  
בארון גבוה ולא על השולחן  
כדי שלא אחפש אותו כל היום  

**7 · דוגמאות ממוספרות**  
5 תפרגני לי בבוקר  
״רז איזה כיף שישנת בלי מוצץ״  
ואחר כך חיבוק גדול  

**8 · דוגמאות ממוספרות**  
6 תישארי רגועה  
בימים הראשונים  
הימים הראשונים הכי קשים  
ואני צריכה אותך קרובה  

**9 · סיכום**  
ככה אני נפרדת  
מהמוצץ צעד צעד  
גם את רוצה לעזור להם  
להיפרד מהמוצץ?  

**10 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור לה גם  
בסיפור אישי  
כתבי "לומי" בתגובות  
וקבלי קישור ליצירת ספר  
שבו הילדה שלך היא הגיבורה  

**כיתוב**  
6 דברים שילדה בת 3 הייתה רוצה להגיד לאמא על המוצץ  
לספר לה מראש ולהשאיר את המוצץ רק במיטה  
לתת לה דובי שבחרה בעצמה ולשים את המוצץ מחוץ לזווית העין  
לפרגן לה בבוקר ולהישאר רגועה בימים הראשונים  
״רז איזה כיף שישנת בלי מוצץ״  
ובערב אפשר להמשיך עם סיפור שבו היא הגיבורה  
כתבי "לומי" בתגובות וקבלי קישור ליצירת ספר שבו הילדה שלך היא הגיבורה  

</div>

## Images

- Images: **1**, the one picture that depicts the idea, behind all 10 slides (Yarin, 14 Oct 2026)
- Endpoint: `openai/gpt-image-2.5/flare/text-to-image`
- Quality: `high` · generation size 1024 x 1280 (4:5) · final export 1080 x 1350
- Estimated cost: about **$0.06** if every image passes QA first time
- Estimated maximum: **$0.17** if every image needs the maximum 2 replacements (the runner refuses to spend past the approved amount)
- Pricing is token based; estimates come from the fal pricing table checked 2026-10-07 (see scripts/fal_endpoints.json)

## If visual QA fails

- Every image is inspected at full size for character consistency, hands, faces, anatomy, accidental words or letters, clean typography space, product accuracy and continuity.
- The reference image is checked first. Slides are generated only after the reference passes.
- Only a failed image is regenerated, with a short fix note added to its prompt. Passed images are never regenerated.
- After 2 failed replacements of the same image, generation stops and Claude asks for direction.

## Slide 7

- The carousel never names the brand or a book title. Slide 7 only hints that a book where the child is the hero is one possible tool; the generated scene shows a child looking at a picture book with a drawing of themselves, with no logo or words.
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-19-kid-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-19-kid-1/README.md` for the exact commands.
