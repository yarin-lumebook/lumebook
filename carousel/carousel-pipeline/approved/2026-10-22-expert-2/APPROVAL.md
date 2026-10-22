# Approval sheet · expert-2 · 2026-10-22

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
איך עוצרים ילד  
בן 3 שמרביץ  
בלי לצעוק?  
7 צעדים שעובדים  

**2 · ההסבר**  
בגיל 3 הידיים  
מהירות מהמילים  
ילדים קטנים מגיבים בגוף  
כשאין להם עוד מילים  

**3 · דוגמאות ממוספרות**  
1 קודם עוצרים  
2 משפט קבוע וקצר  
מרחיקים את היד וזהו  
״בבית שלנו לא מרביצים״  

**4 · דוגמאות ממוספרות**  
3 לתת שם לכעס שלו  
״עידו כועס כי הגיע הזמן ללכת״  
זה עוזר לו לדבר במקום להרביץ  

**5 · דוגמאות ממוספרות**  
4 פינה שקטה לנשימה  
נותנים לו להירגע  
ומשתדלים לא לזרז אותו  

**6 · דוגמאות ממוספרות**  
5 לדבר רק אחרי שנרגע  
לא לדחוף אותו לדבר על זה מיד  
לפעמים צריך קצת זמן  

**7 · דוגמאות ממוספרות**  
6 מחמאה ספציפית  
״אני שמחה שלקחת הפסקה כדי להירגע״  
אחרי שהוא חזר לעצמו  

**8 · דוגמאות ממוספרות**  
7 אזהרה לפני רגע קשה  
״אם תמשיך אנחנו יוצאים עכשיו״  

**9 · סיכום**  
נותנים לכעס שם  
ומחכים שהוא ירגע  
קודם הגוף ואז המילים  
ולא להפך  

**10 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור לו גם  
בסיפור אישי  
כתבי "לומי" בתגובות  
וקבלי קישור ליצירת ספר  
שבו הילד שלך הוא הגיבור  

**כיתוב**  
איך עוצרים ילד בן 3 שמרביץ בלי לצעוק  
בגיל הזה הידיים מהירות מהמילים  
7 צעדים שעובדים בסדר הזה  
לעצור ולהגיד משפט קבוע וקצר  
לתת שם לכעס ופינה שקטה  
לדבר אחרי שהוא נרגע ולהחמיא  
ובערב אפשר להמשיך עם סיפור שבו הוא הגיבור  
כתבי "לומי" בתגובות וקבלי קישור ליצירת ספר שבו הילד שלך הוא הגיבור  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-22-expert-2/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-22-expert-2/README.md` for the exact commands.
