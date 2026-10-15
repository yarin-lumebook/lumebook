# Approval sheet · kid-2 · 2026-10-11

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
בכיתה הוא מלאך  
בבית הר געש  
2 דברים שיעזרו לו לנחות  

**2 · פתיח שני**  
נועם מחזיק את עצמו  
כל היום בכיתה  
ובבית הוא סוף סוף משחרר  
כי פה הוא יודע שאוהבים אותו  

**3 · מה עומד מאחורי זה**  
"אני לא  
עושה לכם דווקא"  
אחרי יום של להחזיק את עצמו  
הכוח נגמר ובבית זה יוצא  

**4 · פתרון**  
קודם חיבוק  
ואחר כך שאלות  
״נועם אני קודם רוצה חיבוק״  
לפני שמתחילים לשאול שאלות  
ויש עוד דבר אחד קטן  

**5 · פתרון**  
רבע שעה בלי דרישות  
אין שיעורים ואין שאלות  
רק שקט ומשחק חופשי  
ואז ממשיכים עם היום  

**6 · הסגירה**  
ואז הר הגעש מתקרר  
זה לא קורה מיד  
אבל לאט לאט הצהריים רגועים יותר  

**7 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור לו  
גם בסיפור אישי  
כתבו "לומי" בתגובות  
וקבלו קישור ליצירת ספר  
שבו הילד שלכם הוא הגיבור  

**כיתוב**  
בכיתה הוא מחזיק את עצמו ובבית הכול יוצא  
אצל הרבה ילדים אחרי יום ארוך הכוח נגמר  
קודם חיבוק בכניסה ורק אחר כך שאלות  
רבע שעה בלי דרישות ובלי שיעורים  
ולפעמים אחרי זה הצהריים רגועים יותר  
ובערב אפשר להמשיך עם סיפור שבו הוא הגיבור  
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור  

</div>

## Images

- Images: **8** (1 character and style reference + 7 slide scenes edited from it)
- Endpoints: `openai/gpt-image-2.5/flare/text-to-image` (reference), `openai/gpt-image-2.5/flare/edit` (slides)
- Quality: `high` · generation size 1024 x 1280 (4:5) · final export 1080 x 1350
- Estimated cost: about **$0.47** if every image passes QA first time
- Estimated maximum: **$1.43** if every image needs the maximum 2 replacements (the runner refuses to spend past the approved amount)
- Pricing is token based; estimates come from the fal pricing table checked 2026-10-07 (see scripts/fal_endpoints.json)

## If visual QA fails

- Every image is inspected at full size for character consistency, hands, faces, anatomy, accidental words or letters, clean typography space, product accuracy and continuity.
- The reference image is checked first. Slides are generated only after the reference passes.
- Only a failed image is regenerated, with a short fix note added to its prompt. Passed images are never regenerated.
- After 2 failed replacements of the same image, generation stops and Claude asks for direction.

## Slide 7

- The carousel never names the brand or a book title. Slide 7 only hints that a book where the child is the hero is one possible tool; the generated scene shows a child looking at a picture book with a drawing of themselves, with no logo or words.
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-11-kid-2/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-11-kid-2/README.md` for the exact commands.
