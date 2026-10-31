# Two messages to Yossi, 31 Oct 2026

Internal. Part of `research/cro-crm/` (start at `report.md`). Ready to paste into WhatsApp. Message 1 is the one that affects Yarin's pay (project P3 in `course/curriculum.md` §6: paste it into P3's hand-in after sending). Message 2 makes GA4 and Meta accurate and does not change the pay. Send it the same day, later, or not at all.

Message 1 was rewritten later on 31 Oct 2026: Yarin asked what to do if they cannot rely on Yossi's numbers, so it now asks for a filterable column in the admin they can open themselves, and for rows instead of totals.

Where each point comes from:

| Point | Source |
|---|---|
| The code sends the tags with each book created, as first and last touch | `research/creator-content-conversion/report.md:514` |
| The admin says the site does not record which link brought an order; its panel warns "UTM coverage is under 80%" | `docs/lumebook-sales-data-decisions-2026-10-12.md:24` and `:93` |
| Whether the server saves the tags on the order is not confirmed | same two lines |
| Ads arrive as `paid_social` or with a Meta placement in `utm_medium`. No ad uses bare `social`. The bio arrives as `ig / social` | `research/cro-crm/data/ga4-2026-10-25/Reports_snapshot.csv`, session source / medium, 27 Jul to 24 Oct |
| The Facebook post link is `utm_medium=social` | `shared/facts.json`, `postiz.facebook_link` |
| The bio links as Yarin set them: Instagram `utm_source=instagram&utm_medium=social`, Facebook `utm_source=facebook&utm_medium=social`. No other tagged links before 1 Nov | Yarin, 31 Oct 2026. The audit read the Instagram bio as `ig / social / link_in_bio` on 24 Oct (`research/cro-crm/audit.md` step 0), hence "instagram or ig" |
| October's DM links went out untagged (`utm_campaign` null) | `research/carousel-audit/data/carousels.json`, 2026-10-14-sorry and 2026-10-20-pacifier |
| Only orders with Yarin's tag count toward their 25% | `course/discovery.md:20` |
| The tag lives in `sessionStorage`. Fix: 30 days, with consent. Measure by the share of orders with a UTM | `research/cro-crm/audit.md` A21 |
| GA4 fixes: ad URL line, purchase events, CardCom, test hosts | `research/cro-crm/measurement.md` §3 and §4, `numbers-2026-10-25.md` §5 and §6 |
| No random control group for the messages | `numbers-2026-10-25.md` §4, `measurement.md` §8 |

## Message 1: the pay (send now)

```
יוסי, אני צריך ממך דבר אחד שקשור לתשלום שלי, ועוד תיקון קטן.

מה אני צריך:
בדף ההזמנות באדמין (pdf.lumebook.com/api/admin), עמודות utm_source, utm_medium ו-utm_campaign לכל הזמנה, ופילטר, כדי שאוכל לפתוח ולראות בעצמי כמה הזמנות ששולמו הגיעו עם utm_medium=social.
אם קל יותר, ייצוא CSV שבועי עם שורות (מספר הזמנה, תאריך תשלום, סכום, שלושת השדות), לא רק סכום כולל.

למה:
ההסכמה שלנו היא שרק הזמנות עם התגית שלי נספרות, ובאדמין היום אי אפשר לראות את זה.
הקוד כבר שולח את ה-UTM עם כל ספר שנוצר (acquisitionAttribution), אז נראה לי שחסר רק להציג אותו.
אם השרת לא שומר אותו על ההזמנה, תגיד לי ונחשוב מה עושים.

מה נספר כשלי:
utm_medium=social, בדיוק ככה. לא "מכיל social", כי המודעות מגיעות עם paid_social.
זה הקישורים בביו באינסטגרם ובפייסבוק, הקישור בסוף הפוסטים בפייסבוק והקישורים בהודעות הפרטיות.
מהביו באינסטגרם יכול להגיע utm_source=instagram או ig, שניהם שלי.
וחשוב שנסגור בכתב אם נספרת הכניסה הראשונה, האחרונה, או כל אחת מהן. אם אפשר, שני הערכים יופיעו.

איך נדע שזה עובד:
אני אעשה הזמנה אחת עם utm_campaign ייחודי ונבדוק שהיא מופיעה.

תיקון קטן:
היום התגית נשמרת רק ב-sessionStorage, אז מי שסוגר את הטאב וחוזר אחר כך מאבד אותה, גם אם הגיע מהקישור שלי.
אפשר לשמור אותה 30 יום ב-localStorage או בעוגייה של האתר, עם הסכמה? (A21 באודיט)
לפני השינוי: לרשום כמה אחוז מההזמנות ששולמו מגיעות עם UTM כלשהו, ולבדוק שוב שבועיים אחרי.

ועוד דבר: שמודעות אף פעם לא יקבלו utm_medium=social, שלא יתערבבו עם שלי.
```

## Message 2: GA4 and Meta (optional, does not affect the pay)

For Yossi, or for whoever runs the ads if that is someone else (not confirmed).

```
ועוד רשימה קצרה שלא דחופה, רק כדי ש-GA4 ו-Meta יראו נכון:

1. מודעות: שורת פרמטרים אחת לכל מודעה (בשדה URL parameters של Ads Manager):
utm_source=facebook&utm_medium=paid-social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{placement}}
היום יש 8 שמות מקור שונים (facebook, fb, meta, ig, an ועוד), ובחלק מהמודעות המיקום (Instagram_Reels וכו') יושב ב-utm_medium, אז GA4 סופר אותן כאורגני.

2. רכישה: היום יש ב-GA4 שלושה אירועים (purchase, Purchase, payment_completed_and_redirect). עדיף purchase אחד לכל הזמנה ששולמה, מהשרת, עם transaction_id.

3. CardCom: להוסיף את secure.cardcom.solutions לרשימת ה-unwanted referrals ב-GA4. היום מי שחוזר מהתשלום נספר כביקור חדש ש-CardCom הביאה.

4. תנועת בדיקות: replit, תצוגות מקדימות של Vercel, appium ו-127.0.0.1 נכנסים לנתונים. להוציא אותם, ולהגדיר את המכשירים שלנו כ-internal traffic.

5. הודעות וואטסאפ ו-SMS: אם אפשר, קבוצת ביקורת אקראית (10 עד 20%) שלא מקבלת את ההודעה, כדי לדעת אם ההודעות באמת מביאות קניות.
```
