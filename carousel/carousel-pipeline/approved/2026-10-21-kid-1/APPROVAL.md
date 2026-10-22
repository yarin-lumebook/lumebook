# Approval sheet · kid-1 · 2026-10-21

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
אמא ואבא  
9 דברים שיעזרו לנו  
כשאנחנו רבים  

**2 · ההסבר**  
אני רבה עם אחי  
למרות שאני אוהבת אותו  
אצל הרבה אחים יש קנאה ותחרות  
הנה מה שיעזור לנו  

**3 · דוגמאות ממוספרות**  
1 תנו לנו לנסות לבד  
2 תיכנסו רק כשיש סכנה  
אם אפשר אל תתערבו מיד  
רק כשמישהו עלול להיפגע  

**4 · דוגמאות ממוספרות**  
3 תפרידו אותנו  
עד שנירגע  
אחר כך נדבר על זה  
לא באמצע הצעקות  

**5 · דוגמאות ממוספרות**  
4 אל תחפשו מי התחיל  
5 תקשיבו לשנינו  
שנינו קצת אשמים  
תנו לשנינו לספר מה קרה  

**6 · דוגמאות ממוספרות**  
6 תנו לנו משחק  
שמנצחים בו ביחד  
כשאנחנו רוצים את אותו צעצוע  
אולי יש משחק לשנינו  

**7 · דוגמאות ממוספרות**  
7 זמן רק איתכם  
8 פינה משלנו בבית  
אנחנו רבים כי אנחנו רוצים אתכם  
או כי אנחנו רוצים שקט  

**8 · דוגמאות ממוספרות**  
9 תגידו לנו כשאנחנו  
משחקים יפה  
״מאיה אני רואה אתכם  
משתפים אחד את השניה״  
אנחנו נשמח לשמוע את זה יותר  

**9 · סיכום**  
תנו לנו לנסות  
ותהיו שם כשצריך  
ככה אנחנו לומדים להסתדר  

**10 · סיפור אישי וקריאה לפעולה**  
אפשר לעזור להם גם  
בסיפור אישי  
כתבו "לומי" בתגובות  
וקבלו קישור ליצירת ספר  
שבו הילדה שלכם היא הגיבורה  

**כיתוב**  
9 דברים שמבקשת ילדה כשהיא רבה עם אחיה  
לנסות לבד קודם ולהיכנס כשיש סכנה  
להפריד עד שנרגעים ולהקשיב לשניהם  
משחק שמנצחים בו ביחד וזמן אחד על אחד  
״אני רואה אתכם משתפים בצעצוע״  
ובערב אפשר להמשיך עם סיפור שבו הילדה שלכם היא הגיבורה  
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הילדה שלכם היא הגיבורה  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-21-kid-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-21-kid-1/README.md` for the exact commands.
