# Approval sheet · kid-2 · 2026-10-18

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
״אמא למה אני ער?״  
6 דברים שיעזרו לי  
להתרגל לשעון חורף  

**2 · ההסבר**  
הגוף שלי עדיין חי  
לפי השעון הישן  
המעבר לשעון חורף משפיע עליי  
גם אם לא שמים לב  
תעזרי לי להתרגל  

**3 · דוגמאות ממוספרות**  
1 להחשיך את החדר  
חושך בחדר נותן לי עוד זמן להתרגל  

**4 · דוגמאות ממוספרות**  
2 אור שמש בחצי שעה  
הראשונה כשאני מתעורר  
לצאת לאור היום מיד כשקמים  
מכוון את השעון הביולוגי שלי  

**5 · דוגמאות ממוספרות**  
3 ארוחות באותה השעה  
״אביב עכשיו ארוחת צהריים״  
גם אם אפור ומעונן בחוץ  
הגוף לומד לפי הארוחות  

**6 · דוגמאות ממוספרות**  
4 תנועה במהלך היום  
רגיעה לקראת הלילה  
ביום מתרוצצים ובערב נרגעים  
זה עוזר לי להירדם  

**7 · דוגמאות ממוספרות**  
5 מקלחת חמימה וספר  
מקלחת חמה וספר אמיתי ולא במסך  
מקלים על ההירדמות  

**8 · דוגמאות ממוספרות**  
6 שבוע של סבלנות  
לרוב לוקח לי בערך שבוע  
ואני אחזור לקום כרגיל  

**9 · סיכום**  
להרגיל את הגוף  
שבוע מראש  
חושך בחדר · שמש בבוקר  
ארוחות קבועות · תנועה ביום  
ערב שקט · סבלנות  

**10 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור לו גם  
בסיפור אישי  
כתבי "לומי" בתגובות  
וקבלי קישור ליצירת ספר  
שבו הילד שלך הוא הגיבור  

**כיתוב**  
כשהשעון זז אחורה אביב קם כשהגוף שלו מוכן ולא כשהשעון אומר  
תשאירי חושך בחדר ותצאו לשמש בבוקר  
ארוחה בזמן החדש וערב שקט  
ועוד כמה דברים קטנים לשבוע הראשון  
ובערב אפשר להוסיף סיפור שבו הוא הגיבור  
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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-18-kid-2/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-18-kid-2/README.md` for the exact commands.
