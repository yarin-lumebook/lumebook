# Approval sheet · expert-1 · 2026-10-25

Nothing has been generated and nothing has been paid for. Generation starts only after Yarin explicitly approves this sheet in chat.

## Selected copy (frozen)

<div dir="rtl" lang="he">

**1 · פתיח**  
איך מרגיעים בת 4  
שמפחדת מרעמים?  
9 צעדים  

**2 · ההסבר**  
בגיל 4 בום חזק  
זה פחד אמיתי  
והיא בודקת דרכך  
כמה זה מפחיד באמת  

**3 · דוגמאות ממוספרות**  
1 להישאר רגועה לידה  
ילדים קוראים את מצב הרוח שלנו  
והשקט שלך מרגיע גם אותה  

**4 · דוגמאות ממוספרות**  
2 לתת לפחד שם  
3 ״את בטוחה ואני כאן״  
״הדר הבום הבהיל אותך״  
במקום ״זה כלום״  
ולהסביר שאת כאן איתה  

**5 · דוגמאות ממוספרות**  
4 להסביר מה זה רעם  
״הברק מחמם את האוויר ויש בום״  
לפעמים כשמבינים זה פחות מפחיד  

**6 · דוגמאות ממוספרות**  
5 לספור מהברק עד הבום  
6 מיטה רחוקה מהחלון  
כשהיא סופרת זה מרגיש רחוק  
ובפינה הקיצונית לחלון  
שומעים פחות רעם  

**7 · דוגמאות ממוספרות**  
7 ערכה רק לימי סופה  
8 לשחק בסופה ביום  
פאזל טושים ופנס על סוללות  
וביום חושפים לפחד בעדינות  
כשהכול רגוע  

**8 · דוגמאות ממוספרות**  
9 מילה טובה על האומץ  
״הדר ראיתי שנשארת במיטה  
גם כשהיה בום״  

**9 · סיכום**  
נשארים רגועים ומסבירים  
וסופרים את המרחק מהברק  
גם את רוצה לעזור לה לפחד פחות?  

**10 · סיפור אישי וקריאה לפעולה**  
תשמרי את הפוסט  
לפעם הבאה שהיא מפחדת מרעמים  

**כיתוב**  
9 צעדים לבת 4 שנבהלת מכל רעם  
להישאר רגועה לידה ולתת לפחד שם  
להגיד ״את בטוחה ואני כאן״ ולהסביר מה זה רעם  
לספור מהברק עד הבום בפינה רחוקה מהחלון  
ערכה לימי סופה משחק רעמים ביום ומילה טובה על אומץ  
ובערב אפשר להמשיך עם סיפור שבו היא הגיבורה  
תשמרי את הפוסט לפעם הבאה שהיא מפחדת מרעמים  

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
- Optional: an unbranded real image can be placed as a card with `--preview-card` (file: `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-25-expert-1/real-assets/preview.png`).

## After approval

See `/Users/yarinbruner/Claude/Projects/Lumebook/carousel/carousel-pipeline/approved/2026-10-25-expert-1/README.md` for the exact commands.
