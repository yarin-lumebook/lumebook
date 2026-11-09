# How the creator map's top product sellers script a Reel

09 / 11 / 2026. Yarin: "take the top 10 ugc creators from the creator map that focus on selling products, analyze their scripts and improve your writing". He had rejected the November reel scripts as too much like an ad, too clean, one formula, not his voice, and weak at hooking and converting.

The writing rules that came out of this live in `.claude/skills/lumebook-hebrew-voice/references/reel-scripts.md`. This file is the evidence.

## Who the ten are and how they were picked

- **Pool:** the 134 creators of the creator map whose posts and comments were measured on 14 / 10 / 2026 (`research/creator-content-conversion/round2/posts_kpi.csv`, `creators_kpi.csv`). The other creators in the map have no comment data, so they could not be ranked.
- **"Focus on selling products":** at least half of their coded posts show, demonstrate or sell a product (`product_visible` featured or demonstrated, or `status` own_product_promo, likely_sponsored or collaboration), or the map says they offer UGC (`prac` in `creators/creator-research/src/C_all.json`). Trips and attractions were left out (sivan_grosman_zukerman, hodelia.travel and the travel accounts), because they sell outings, not products.
- **Ranked by:** buying signals in the comments of their product posts (people asking where to buy, the price, the link, or saying they bought). These are public proxies, not sales (`round2/round2.md` says so).

| # | Creator | What they sell | Product posts / coded posts | Buying signals on product posts |
|---|---|---|---|---|
| 1 | michal_nunu | evening dresses she found cheap, in the store | 3 / 4 | 49 |
| 2 | orelcabelli | cleaning products, sponsored (Tyroler, Sano); offers UGC | 3 / 6 | 22 |
| 3 | tom_zakai_levinkopf | a kids' shoe with a toy garage, sponsored (Skechers) | 2 / 3 | 21 |
| 4 | lital_magnezi | gan solutions and crafts, her own digital booklets | 6 / 12 | 19 |
| 5 | morkeisar | a kitchen machine and a play mat, sponsored (Kenwood, Bliss) | 3 / 5 | 16 |
| 6 | hen.kalimian.kids | a reading corner, her own games and guides | 7 / 12 | 14 |
| 7 | _shirley_unger_kids_activities | her own letter learning kits; offers UGC | 4 / 12 | 10 |
| 8 | nofar_aizik | AliExpress finds and sponsored products | 7 / 8 | 9 |
| 9 | valerialauren | baby gear, sponsored (Anex, Lunalu); offers UGC | 3 / 4 | 8 |
| 10 | racheli.h.m | paints, shoes and a store, sponsored (Giotto, Papaya, HaStok); offers UGC | 6 / 12 | 7 |

## What was read

28 Reels: each creator's product Reels with the most buying signals, plus the ones already coded in the October product Reels research. 13 had a transcript from 15 / 10 / 2026 (`media/projects/2026-10-15-israeli-product-reels/analysis/CODE/whisper.txt`); 15 were downloaded and transcribed today (`media/projects/2026-11-09-ugc-seller-scripts/`, local Whisper, Hebrew, first 90 s, with a frame sheet every 2 s). Six have no speech, only music and on-screen text. Also re-read: the one LumeBook creator Reel, @shoham_novik (`breakdowns.md` section 1).

Limits: Whisper mishears Hebrew, so quotes below are cleaned of obvious mishearings and marked (transcript). Plays and buying signals are from 14 / 10 / 2026 and may include paid boosts. Nobody's sales are known. 28 Reels from 10 creators is a small sample: these are patterns to try, not proven rules.

## What the strong ones do

**1. They talk to one person in one moment, by name of the moment.**
- orelcabelli, her biggest product Reel (294,835 plays, 12 buying signals): "מי שמתכננת ניקיונות לחג, תעצרי רגע" (transcript and on-screen text).
- tom_zakai_levinkopf (18 buying signals): on screen "POV: את אמא לבנים ומוצאת את הנעל המושלמת", caption "אמהות לבנים קטנטנים להתפקד".
- nofar_aizik: "אם יש לכם יום הולדת לילדים בקרוב, אתן חייבות לשמור את הריל הזה" (transcript).

**2. The Reel is an answer to someone.** A follower asked, so here it is.
- lital_magnezi (153,216 plays, 14 buying signals): "גננת מהממת שלחה לי לפני כמה ימים הודעה, מה עושים בנוגע לשירותי הילדים?" (transcript), caption "ביקוש למנורה החזירה אותי לפתרון הפשוט הזה".
- valerialauren: "כל האימהות בסטורי שכנעו אותי שהגיע הזמן להחליף מנשא" (transcript, with the story replies on screen).
- michal_nunu: "ביקשתן סרטון מדידה, קיבלתן" (caption, 18 buying signals).

**3. Something goes wrong first, then the turn.**
- nofar_aizik (48,362 plays, 914 comments): the daughter shouts "אמא, אני חייבת פיפי!" at the airport, toilet paper keeps falling, then "ואז אני קולטת, איך שכחתי שיש לי את זה על העגלה?" (transcript).
- valerialauren: "הסתבר שזה לא התינוק שגדל... אלא המנשא שהיה לי פשוט לא טוב" (transcript).
- morkeisar: "ילדה בת שנתיים וילד בן חודשיים, ואיך מחלקים את הזמן ביניהם?" then "ומאז שקיבלתי את המשלוח..." (transcript).
- shoham_novik for LumeBook: "הייתי סקפטית", then "הייתי בשוק, זאת באמת היא".

**4. They point and react on camera, live.** "תראו", "תסתכלו", "כן כן, אתן רואות נכון" (tom_zakai_levinkopf), "איך אפשר להשאיר דבר כזה בחנות?" (michal_nunu). The product is in their hands and the words describe what we see right now.

**5. Rough edges stay in.** "סורי על כל הרעש והמהירות, אני עושה את זה תוך כדי" (michal_nunu, 130,951 plays), "זה פדיחה שלי שלא הראתי לכם את זה עד עכשיו" (lital_magnezi), "בקיצור", "תקשיבו", "בתכלס", and the honest limit "אני לא אומרת שזה קסם" (shoham_novik).

**6. When they explain, it is a numbered list said in use.** orelcabelli shows 1 to 5 on screen, one product per shot, one benefit each ("המוצר הראשון... המוצר השני..."). valerialauren: "דבר ראשון... דבר נוסף... הכי חשוב...".

**7. One concrete ask with a word.** "רוצות קישור? תכתבו לי אסלה, ואני שולחת" (nofar_aizik), "תגיבו מיקסר ואשלח לכם" (morkeisar). Price and discounts drive several of them (michal_nunu, orelcabelli); LumeBook reels never mention price, so that lever is out.

## What the weak ones do (the same mistakes as our scripts)

racheli.h.m's sponsored store and shoe Reels have the fewest buying signals in the ten, and they sound like our November scripts:
- "בפפאיה מחכות לכם נעלי חג מושלמות, כאלה שמתאימות לכל לוק שתבחרו" (3,186 plays, 2 buying signals).
- "חגים זה קניות וקניות זה הסטוק... יש כאן הכל מהכל" then a catalogue list (2 buying signals).

No person, no moment, no problem, the brand is the subject of the sentence. Our "יש ספר שבו הוא המלך של היום" is the same sentence shape. Her own best Reel is the one with a question and a reason to stay: "מה הקשר בין צבעי המים של ג'יוטו לבין הים? רוצים לדעת? תישארו איתי" (transcript).

## How this changes LumeBook's scripts

Yarin is not a parent (`reels.py` lint fails him speaking as one), so patterns 1 to 3 have to be his honest moments: the questions people send after "לומי", the books he builds and sees in the preview, the printed books in his hands. Rules in `.claude/skills/lumebook-hebrew-voice/references/reel-scripts.md`.
