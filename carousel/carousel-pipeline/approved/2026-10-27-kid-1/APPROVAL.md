# Approval sheet · kid-1 · 2026-10-27

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
אמא אל תגידי  
״לא נורא״  
כשלא שיתפו אותי  
6 דברים שכן עוזרים  

**2 · ההסבר**  
כשאת אומרת ״לא נורא״  
אני מרגישה לבד שוב  
אני צריכה שתשמעי אותי  
ואז נחשוב ביחד מה עושים  

**3 · דוגמאות ממוספרות**  
1 חיבוק ארוך בלי שאלות  
רגע על הידיים שלך  
לפני שאני מספרת  

**4 · דוגמאות ממוספרות**  
2 תשמעי אותי עד הסוף  
בלי לתקן ובלי למהר  
״ספרי לי מה קרה בחצר״  

**5 · דוגמאות ממוספרות**  
3 תגידי לי שזה עצוב  
״הילה זה עצוב כשלא משתפים״  
ואז אני יודעת שהבנת  

**6 · דוגמאות ממוספרות**  
4 נדבר שוב לפני השינה  
במיטה קל לי יותר לספר  
מה באמת קרה היום  

**7 · דוגמאות ממוספרות**  
5 נתאמן עם הבובות  
הדובי שואל ״אפשר להצטרף?״  
ואני מתאמנת להגיד את זה  

**8 · דוגמאות ממוספרות**  
6 תזכירי שמחר יום חדש  
היום לא שיתפו אותי  
ומחר אפשר לנסות שוב  

**9 · סיכום**  
קודם תשמעי אותי  
ואז ננסה שוב ביחד  
ככה אני מרגישה שיש לי מקום  

**10 · סיפור אישי וקריאה לפעולה**  
תשמרי את הפוסט  
לפעם הבאה שלא משתפים אותה  

**כיתוב**  
מה הילה צריכה ממך אחרי שלא שיתפו אותה בגן  
חיבוק ארוך והקשבה עד הסוף  
״זה עצוב כשלא משתפים״ במקום ״לא נורא״  
שיחה לפני השינה ותרגול עם הבובות  
ותזכורת שמחר אפשר לנסות שוב  
ובערב אפשר להמשיך עם סיפור שבו היא הגיבורה  
תשמרי את הפוסט לפעם הבאה שלא משתפים אותה  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-27-kid-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-27-kid-1/README.md` for the exact commands.
