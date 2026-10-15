# Approval sheet · kid-2 · 2026-10-14

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
תפסיקו להגיד לי  
״תבקש סליחה״  
6 דברים שעדיף לעשות במקום  

**2 · ההסבר**  
אני אומר סליחה מהר  
כדי לחזור לשחק  
כשאני לא מבין מה קרה לצד השני  
המילה הזאת לא מלמדת אותי כלום  

**3 · דוגמאות ממוספרות**  
1 תחכו עד שאירגע  
עשר שניות בלי מילים  
עד שהנשימה שלי נרגעת  

**4 · דוגמאות ממוספרות**  
2 תסבירו לי מה קרה  
״אלון בוכה  
כי המגדל שלו נפל״  

**5 · דוגמאות ממוספרות**  
3 תשאלו מה הוא הרגיש  
״איך אלון הרגיש  
כשהפלת לו את המגדל?״  
זה עוזר לי לחשוב עליו  

**6 · דוגמאות ממוספרות**  
4 תנו לי לתקן בעצמי  
לבנות לו מגדל חדש  
זו סליחה שאני מבין  

**7 · דוגמאות ממוספרות**  
5 תתנצלו גם אתם כשצריך  
״סליחה שצעקתי עליך״  
ככה אני לומד מכם איך עושים את זה  

**8 · דוגמאות ממוספרות**  
6 תנו לי זמן להבין  
אני לא בטוח שאבין מהפעם הראשונה  
ואני לומד לאט  

**9 · סיכום**  
סליחה אמיתית היא  
להבין ולתקן  
לחכות · להסביר · לשאול  
לתקן · להתנצל · לתת זמן  

**10 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור לו גם  
בסיפור אישי  
כתבו "לומי" בתגובות  
וקבלו קישור ליצירת ספר  
שבו הילד שלכם הוא הגיבור  

**כיתוב**  
יכול להיות שהוא לא ממש יודע מה זה סליחה  
6 דברים קטנים שיכולים לעזור לו להבין  
לחכות שיירגע ולהסביר לו מה קרה  
לשאול מה הרגיש ולתת לו לתקן  
להתנצל בעצמנו ולתת לזה זמן  
ובערב אפשר להמשיך עם סיפור שבו הוא הגיבור  
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-14-kid-2/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-14-kid-2/README.md` for the exact commands.
