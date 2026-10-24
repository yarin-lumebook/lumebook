# Approval sheet · expert-1 · 2026-10-28

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
הסיבה האמיתית  
שהוא אוכל רק פסטה  
7 דברים שאפשר לעשות  

**2 · ההסבר**  
ילדים קטנים נזהרים  
מאוכל שהם לא מכירים  
זה שלב טבעי שבדרך כלל עובר  
ובפסטה ואורז אין הפתעות במרקם  

**3 · דוגמאות ממוספרות**  
1 משהו מוכר בכל צלחת  
פסטה ולידה כף אחת של משהו חדש  
ככה נתן לא נשאר רעב  

**4 · דוגמאות ממוספרות**  
2 מאורז לפתיתים  
ומשם לקוסקוס  
צבע ומרקם דומים עוזרים להתקדם  

**5 · דוגמאות ממוספרות**  
3 לעשות טעימות  
״רק טעימה קטנה״  
ואם לא אז שוב בעוד שבוע  

**6 · דוגמאות ממוספרות**  
4 ירק עם טעם מוכר  
ברוקולי עם גבינה מגוררת  
מר ליד מלוח שהוא כבר אוהב  

**7 · דוגמאות ממוספרות**  
5 פסטה לא בכל ארוחה  
גם אם הוא מבקש רק פסטה  
תקופה של מאכל אחד לרוב קצרה  

**8 · דוגמאות ממוספרות**  
6 בלי קינוח כפרס  
7 הוא מחליט כמה לאכול  
פרס הופך את הירק למטלה  
את מגישה והוא מחליט אם ובכמה  

**9 · סיכום**  
מוכר ליד חדש  
ושוב ושוב בלי לחץ  
גם את רוצה לעזור להם  
לאכול דברים חדשים?  

**10 · סיפור אישי וקריאה לפעולה**  
תשמרי את הפוסט  
לפעם הבאה שהוא לא רוצה לאכול  

**כיתוב**  
למה ילד בן 3 אוכל רק פסטה ואורז  
ילדים קטנים נזהרים מאוכל שהם לא מכירים וזה שלב טבעי  
משהו מוכר בכל צלחת ומאורז לפתיתים לקוסקוס  
עשר טעימות ויותר ובלי קינוח כפרס  
ובערב אפשר להמשיך עם סיפור שבו הוא הגיבור  
תשמרי את הפוסט לפעם הבאה שהוא לא רוצה לאכול  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-28-expert-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-28-expert-1/README.md` for the exact commands.
