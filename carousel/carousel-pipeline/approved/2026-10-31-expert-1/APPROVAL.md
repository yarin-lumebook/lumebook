# Approval sheet · expert-1 · 2026-10-31

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
הסיבה האמיתית  
שהוא לא ניגש  
לילדים חדשים  
7 דברים שאפשר לעשות  

**2 · ההסבר**  
יש ילדים שצריכים  
יותר זמן להיפתח  
לפי בית החולים לילדים בפילדלפיה  
זה חלק טבעי מההתפתחות  
וצריך לעזור להם בהכנה ובתרגול  

**3 · דוגמאות ממוספרות**  
1 לספר מראש מי יהיה שם  
״נועם היום נפגוש שכנים חדשים״  
ככה הוא יודע למה לצפות  

**4 · דוגמאות ממוספרות**  
2 ללכת לפי הקצב שלו  
אם הוא רוצה קודם להסתכל  
מסתכלים איתו ולא ממהרים  

**5 · דוגמאות ממוספרות**  
3 להגיד שלום ראשונה  
״היי כמה הוא בן?״ לאמא בגינה  
הוא רואה ממך איך מתחילים  

**6 · דוגמאות ממוספרות**  
4 להזמין חבר אחד הביתה  
בבית הוא הכי רגוע  
ואז קל לו לשחק איתו גם בגן  

**7 · דוגמאות ממוספרות**  
5 להתאמן עם בני דודים  
עם ילדים שהוא מכיר  
הוא מתרגל איך מתחילים לשחק  

**8 · דוגמאות ממוספרות**  
6 להציע משחק שהוא אוהב  
7 לפרגן על צעד קטן  
״ראיתי ששיחקת ליד הילדים״  

**9 · סיכום**  
מכינים מתרגלים  
ומפרגנים על כל צעד  
גם את רוצה לעזור להם  
להתחבר לילדים חדשים?  

**10 · סיפור אישי וקריאה לפעולה**  
תשמרי את הפוסט  
לפעם הבאה שהוא פוגש ילדים חדשים  

**כיתוב**  
למה יש ילדים שלא ניגשים לילדים חדשים ומה עוזר להם  
לפי בית החולים לילדים בפילדלפיה יש ילדים שצריכים יותר זמן להיפתח  
7 דברים שאפשר לעשות כבר השבוע  
לספר מראש מי יהיה שם וללכת לפי הקצב שלו  
להגיד שלום ראשונה ולהזמין חבר אחד הביתה  
ובערב אפשר להמשיך עם סיפור שבו הוא הגיבור  
תשמרי את הפוסט לפעם הבאה שהוא פוגש ילדים חדשים  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-31-expert-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-31-expert-1/README.md` for the exact commands.
