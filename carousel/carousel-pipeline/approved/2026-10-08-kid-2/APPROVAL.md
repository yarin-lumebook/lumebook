# Approval sheet · kid-2 · 2026-10-08

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
אמא ואבא  
2 דברים שיעזרו לי  
לפני שאתם שמים אותי בגן  

**2 · פתיח שני**  
בשער אני בוכה  
ואתם נוסעים לעבודה  
עם הבכי שלי בראש  

**3 · הבעיה או הרגש**  
קשה לי בעיקר ברגע שאתם הולכים  
כמה דקות אחר כך  
אני כבר בפינת הבובות  
אז מה עוזר לי ברגע עצמו?  

**4 · פתרון**  
דבר ראשון  
ביי אחד קצר וחיבוק  
בלי "עוד חמש דקות" בשער  
כשזה נמשך קשה לי יותר  

**5 · פתרון**  
דבר שני  
שיר קטן רק שלנו  
שאנחנו שרים כל בוקר בשער  
ואז ״נועה ביי נתראה בצהריים״  

**6 · הסגירה**  
ובצהריים אני מספרת לכם  
מה בניתי ועם מי שיחקתי  
ואת הבכי של הבוקר  
אני כבר לא זוכרת  

**7 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור לה גם בסיפור אישי  
כתבו "גן" בתגובות  
וקבלו קישור ליצירת ספר  
שבו הילדה שלכם היא הגיבורה  

**כיתוב**  
הבכי בשער הוא לפעמים רק חצי מהבוקר  
אצל הרבה ילדים הוא נרגע כמה דקות אחרי שההורים הולכים  
מה שעוזר ברגע עצמו הוא ביי אחד קצר  
ושיר קטן שחוזר כל בוקר  
ובערב אפשר לחזק אותה בעזרת סיפור שבו היא הגיבורה  
כתבו "גן" בתגובות וקבלו קישור ליצירת ספר שבו הילדה שלכם היא הגיבורה  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-08-kid-2/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-08-kid-2/README.md` for the exact commands.
