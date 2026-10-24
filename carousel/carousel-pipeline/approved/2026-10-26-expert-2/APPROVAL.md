# Approval sheet · expert-2 · 2026-10-26

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
הסיבה האמיתית  
שהיא מתפרקת  
ביום ההולדת שלה  
9 דברים שאפשר לעשות  

**2 · ההסבר**  
בגיל 5 יום הולדת  
הוא הכול או כלום  
משהו אחד לא כמו שדמיינו  
וכל היום מרגיש להם הרוס  

**3 · דוגמאות ממוספרות**  
1 רשימה של בטוח ואולי  
2 להבטיח פחות  
״בטוח תהיה עוגה ואולי בלונים״  
כך יש פחות מקום לאכזבה  

**4 · דוגמאות ממוספרות**  
3 לתכנן את זה ביחד  
בגיל 5 התכנון כיף כמעט כמו המסיבה  
״אלמה מה נשים על השולחן?״  

**5 · דוגמאות ממוספרות**  
4 לתת שם לאכזבה  
5 זמן לבכות בחיבוק  
״אני יודעת שאת מאוכזבת עכשיו״  
בלי למהר להחזיר אותה לחגיגה  

**6 · דוגמאות ממוספרות**  
6 תגובה רגועה ושקטה  
כשאת רגועה  
קל להם יותר להירגע לידך  

**7 · דוגמאות ממוספרות**  
7 לא לתקן מיד  
לא לרוץ להביא בלון חדש  
לפעמים צריך רק שתהיי שם  

**8 · דוגמאות ממוספרות**  
8 לדבר על זה בערב  
9 לשאול מה רצתה שיקרה  
״מה רצית שיקרה היום?״  
״ומה נעשה אחרת בפעם הבאה?״  

**9 · סיכום**  
פחות הבטחות  
ויותר הקשבה  
גם את רוצה לעזור להם  
להתמודד עם אכזבה?  

**10 · סיפור אישי וקריאה לפעולה**  
תשמרי את הפוסט  
לפעם הבאה שיש לה יום הולדת  

**כיתוב**  
למה דווקא ביום ההולדת שלה הכול מתפרק  
בגיל הזה יום הולדת הוא הכול או כלום  
לפני רשימה של בטוח ואולי ותכנון ביחד  
ברגע עצמו שם לאכזבה וחיבוק בלי למהר  
ובערב שאלה אחת ״מה רצית שיקרה?״  
ואחרי זה אפשר להמשיך עם סיפור שבו היא הגיבורה  
תשמרי את הפוסט לפעם הבאה שיש לה יום הולדת  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-26-expert-2/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-26-expert-2/README.md` for the exact commands.
