# Approval sheet · kid-3 · 2026-10-12

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
את מכבה את המסך  
באמצע  
והיא מתפוצצת  
2 דברים שיעזרו לסיים לצפות  

**2 · פתיח שני**  
הפרק היה בדיוק  
בקטע הכי טוב  
והמסך נהיה שחור  
לפני שידעתי מה קרה  

**3 · הבעיה או הרגש**  
אני מאוכזבת שזה נגמר  
זה טבעי כשמפסיקים משהו כיפי  
אבל אני צריכה שיכינו אותי לזה  

**4 · פתרון**  
תגידי שאת מבינה  
״ליה אני יודעת שזה מתסכל  
שהפרק נגמר באמצע״  
ורק אחר כך מכבים  

**5 · פתרון**  
תגידי מה מחכה אחרי  
״ליה אחרי הארוחה והמקלחת  
תוכלי לסיים את הפרק״  

**6 · הסגירה**  
ובהמשך המסך נכבה  
בלי מלחמה  
לא מיד  
אבל זה נגמר רגוע יותר  

**7 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור לה גם  
בסיפור אישי  
כתבי "לומי" בתגובות  
וקבלי קישור ליצירת ספר  
שבו הילדה שלך היא הגיבורה  

**כיתוב**  
המסך נכבה באמצע פרק והיא מתפוצצת  
היא מאוכזבת שזה נגמר וזה טבעי כשמפסיקים משהו כיפי  
עוזר להגיד לה שאת מבינה לפני שמכבים  
ועוד עוזר להגיד לה מה מחכה אחרי  
ובערב אפשר להמשיך עם סיפור שבו היא הגיבורה  
כתבי "לומי" בתגובות וקבלי קישור ליצירת ספר שבו הילדה שלך היא הגיבורה  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-12-kid-3/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-12-kid-3/README.md` for the exact commands.
