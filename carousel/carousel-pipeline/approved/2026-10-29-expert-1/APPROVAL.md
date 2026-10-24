# Approval sheet · expert-1 · 2026-10-29

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
איך מכבים טאבלט  
לילדה בת ארבע  
בלי מלחמה?  
7 צעדים שעוזרים  

**2 · ההסבר**  
רוב העבודה קורית  
לפני שהמסך נדלק  
לפי האקדמיה האמריקאית  
לרפואת ילדים תכנון מראש  
מונע חלק מהמריבות  

**3 · דוגמאות ממוספרות**  
1 לסכם מראש  
כמה פרקים ומה אחרי  
״טליה שני פרקים  
ואחר כך אנחנו יוצאות לגינה״  

**4 · דוגמאות ממוספרות**  
2 לשבת לידה רגע  
לפני שמכבים  
להסתכל במה היא צופה ולחייך  
ככה קל לה יותר לחזור אלייך  

**5 · דוגמאות ממוספרות**  
3 לכבות בסוף פרק  
ולא באמצע  
לפי מחקר של אוניברסיטת וושינגטון  
בוחרים בנקודת סיום  
טבעית המקלה על המעבר  

**6 · דוגמאות ממוספרות**  
4 משפט אחד בלי הרצאה  
5 הטאבלט לא חוזר  
״אני יודעת שקשה  
ועכשיו מכבים״  
גם אם היא בוכה  

**7 · דוגמאות ממוספרות**  
6 פינה שקטה  
להירגע בה  
מובילים אותה ביד אם צריך  
״אחכה לך פה כשתהיי מוכנה״  

**8 · דוגמאות ממוספרות**  
7 לעבור למשהו  
שהיא אוהבת עוד יותר  
טיול עם הכלב  
או משימה קטנה במטבח איתך  

**9 · סיכום**  
תכנון לפני  
ומעט מילים ברגע עצמו  
גם את רוצה לעזור לה  
להיפרד מהמסך בלי מלחמה?  

**10 · סיפור אישי וקריאה לפעולה**  
תשמרי את הפוסט  
לפעם הבאה שקשה לה להיפרד מהמסך  

**כיתוב**  
7 צעדים לכיבוי טאבלט אצל ילדה בת 4  
רוב העבודה קורית עוד לפני שהמסך נדלק  
מסכמים מראש כמה פרקים ומה בא אחרי  
מכבים בסוף פרק ואומרים משפט אחד בלי הרצאה  
פינה שקטה ואחר כך משהו שהיא אוהבת עוד יותר  
ובערב אפשר להמשיך עם סיפור שבו היא הגיבורה  
תשמרי את הפוסט לפעם הבאה שקשה לה להיפרד מהמסך  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-29-expert-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-29-expert-1/README.md` for the exact commands.
