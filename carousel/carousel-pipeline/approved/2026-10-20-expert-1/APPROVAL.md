# Approval sheet · expert-1 · 2026-10-20

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
הסיבה האמיתית  
לפספוס אחרי גמילה  
6 דברים שאפשר לעשות  

**2 · ההסבר**  
פספוס לא בהכרח  
אומר שהם לא מוכנים  
לפי האקדמיה האמריקאית לרפואת ילדים  
תגובה טבעית לשינוי  
שנמשכת לרוב ימים או שבועות  

**3 · דוגמאות ממוספרות**  
1 שינוי בחיים שלהם  
גן חדש תינוק חדש או מעבר דירה  
יכולים להחזיר פספוסים  

**4 · דוגמאות ממוספרות**  
2 לבדוק אצל רופא ילדים  
עצירות או דלקת בדרכי השתן  
יכולות להיות הסיבה  

**5 · דוגמאות ממוספרות**  
3 לתקן מה שאפשר בבית  
סיר בחדר עם חפצים מוכרים  
ואפשר ללוות אותה לשירותים  

**6 · דוגמאות ממוספרות**  
4 להראות שאתם  
מאמינים בהם  
חיבוק ושבח על כל ניסיון  

**7 · דוגמאות ממוספרות**  
5 הפסקה אחרי חודש  
אם זה נמשך חודש או יותר  
אפשר להניח את הסיר בצד קצת  

**8 · דוגמאות ממוספרות**  
6 בלי לחזור לחיתולים  
אפשר מכנסי אימון מתחת לתחתונים  
עד שהם מרגישים בטוחים שוב  

**9 · סיכום**  
פספוס הוא תגובה לשינוי  
גם את רוצה לעזור למעיין  
להפסיק לפספס?  

**10 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור לה גם  
בסיפור אישי  
כתבי "לומי" בתגובות  
וקבלי קישור ליצירת ספר  
שבו הילדה שלך היא הגיבורה  

**כיתוב**  
למה ילדים מפספסים שוב אחרי שכבר נגמלו  
לפי עמוד של האקדמיה האמריקאית לרפואת ילדים  
לרוב זו תגובה לשינוי ולא סימן שהיא לא מוכנה  
6 דברים: בדיקה אצל רופא ילדים ותיקון בבית  
חיבוק ושבח על כל ניסיון  
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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-20-expert-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-20-expert-1/README.md` for the exact commands.
