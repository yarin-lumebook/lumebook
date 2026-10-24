# Approval sheet · expert-1 · 2026-10-30

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
איך מחזירים לישון  
בת 4 שהתעוררה  
מחלום רע?  
9 צעדים שאפשר לעשות  

**2 · ההסבר**  
בגיל 3 עד 6  
חלום רע זה ממש מוכר  
9 הצעדים מתחילים ברגע שהיא קוראת  
ונגמרים בארוחת הבוקר  

**3 · דוגמאות ממוספרות**  
1 להגיע אליה מהר  
2 ״אני פה איתך״  
הנוכחות הרגועה שלך  
עוזרת לה להרגיש בטוחה  

**4 · דוגמאות ממוספרות**  
3 לתת שם למה שקרה  
״תמר זה היה חלום רע  
עכשיו את ערה והכול בסדר״  

**5 · דוגמאות ממוספרות**  
4 לבדוק צללים בחדר  
5 אור קטן אם זה עוזר  
מעיל על הדלת בחושך  
יכול להיראות כמו משהו אחר  

**6 · דוגמאות ממוספרות**  
6 לישון כשהיא מוכנה  
בלי שיחה ארוכה על החלום  
באמצע הלילה  

**7 · דוגמאות ממוספרות**  
7 בבוקר לספר ולצייר  
8 להמציא לחלום סוף חדש  
באור יום תמונות מפחידות  
יכולות לאבד מהכוח שלהן  

**8 · דוגמאות ממוספרות**  
9 לשאול את רופא הילדים  
אם זה יותר מפעם בשבוע  
או כשזה פוגע לה בשינה  

**9 · סיכום**  
בלילה להתקרב ולהרגיע  
ובבוקר ציור וסוף חדש  
גם את רוצה לעזור לה  
עם הפחד הבא?  

**10 · סיפור אישי וקריאה לפעולה**  
תשמרי את הפוסט  
לפעם הבאה שהיא מתעוררת מחלום רע  

**כיתוב**  
מה עושים כשבת 4 מתעוררת מחלום רע  
9 צעדים מהלילה ועד הבוקר  
להגיע מהר ולהגיד ״אני פה איתך״  
לתת שם לחלום ולבדוק צללים בחדר  
אור קטן ולחזור לישון כשהיא מוכנה  
בבוקר לספר לצייר ולהמציא לחלום סוף חדש  
ובערב אפשר להמשיך עם סיפור שבו היא הגיבורה  
תשמרי את הפוסט לפעם הבאה שהיא מתעוררת מחלום רע  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-30-expert-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-30-expert-1/README.md` for the exact commands.
