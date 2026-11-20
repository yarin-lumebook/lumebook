# Filming playbook: LumeBook product Reels with a phone

For Yarin, 15 Oct 2026. Built from 173 Israeli creator Reels that I watched and verified (197 watched, 24 excluded; `source-index.md`) and eight deep dives (`breakdowns.md`). Assumes one phone, a home, no crew, no new equipment and no child on camera.

- **Product facts** in the scripts were checked on lumebook.com on 15 Oct 2026 (`src/product-facts-2026-10-15.md`): ₪119 printed book with a free digital copy, home delivery ₪30, up to 7 business days, free preview and pay only if you liked it, 22 x 22 cm softcover with 24 colour pages, the child on the cover and in 10 pictures inside, a printed or handwritten dedication page. Re-check price and delivery the day you post.
- **Hebrew scripts** follow the LumeBook Hebrew voice skill in its documented fallback voice (calibration has 12 of the 15 approved samples it needs), so they are a careful guess at your voice, not your voice. All five passed `voice_lint.py` with the fixed comment word "לומי" (`src/scripts/`). Rewrite any line that doesn't sound like you; the lint is a floor, not a judge.
- **Instagram handle:** LumeBook's collab with @shoham_novik lists the co-author as @lumebook.il, which loads (948 followers on 15 Oct). @lumebookai no longer loads. Tag @lumebook.il.
- **Research check (18 Oct 2026):** every rule below was checked against 63 principles from platform documentation, peer-reviewed studies, industry datasets and Israeli regulators (`smm-research/principles.md`, IDs such as H1 or T4), and each of the 173 Reels was broken down on eight questions with the research behind every why (`src/table/`, the page's "Reel-by-reel table"). Section 8 lists which rules the research confirmed, which it changed and which stay unproven. Rules changed on 18 Oct say so where they stand.

## 1. What the 173 Reels show

Observed counts first, my reading after each. The first 41 Reels were watched in the morning of 15 Oct; 150 more were added the same evening (132 verified, 24 excluded across both rounds), mostly creator collaborations found on the Reels grids of children's brands (Giotto, Palphot, Bliss, MeBook, FunSome, TinyBook, Kodkod, Superkit, Zikit) plus leads from the 14 Oct creator study. Where the larger sample changed a finding from the first 41, the point says so. Counts are recomputed by `src/sample_stats.py`.

1. **The product is on screen almost at once.** 150 of 173 show it within 2 seconds (35 of 41 in the first round). The 13 that hold it past 5 seconds open on a moment or a person instead: a toilet mishap (16 s, [DcZCOp4ItbM](https://www.instagram.com/reel/DcZCOp4ItbM/)), the first day of school (8 s, [Dcqjk_UN7da](https://www.instagram.com/reel/Dcqjk_UN7da/)), a gan-crying story in LumeBook's second collab (11 s, [DSCtVl0iKXo](https://www.instagram.com/reel/DSCtVl0iKXo/)), and a mother's story about her son's surgery where the scar gel appears at 51 s ([DcbqVsnN42E](https://www.instagram.com/reel/DcbqVsnN42E/), 168,493 plays). My read: unchanged. Show the thing in the first second, or open on a moment strong enough to wait for.
2. **Text on screen is the norm, not universal.** 154 of 173 burn in text. The 19 without are mostly craft and unboxing Reels that rely on the hands and music (most of them Giotto and Palphot collabs). My read: a muted viewer understands a craft from the hands; a book's value (the child's name, the story, the price) needs words on screen.
3. **Voice is optional.** 75 voiceover only, 21 voiceover plus talking to camera, 21 only to camera, 55 no speech at all, 1 with only in-scene speech. My read: unchanged, a voiceover recorded afterwards is the easiest way to sound natural; text and music alone are common and fine for show-and-do Reels.
4. **Personalised-book Reels still lean on children and still hide the price.** 36 Reels from five brands (26 MeBook, 4 FunSome, 3 TinyBook, 2 LumeBook, 1 Zikit). 29 of 36 put a child on camera. Likeness proof: 5 show the child's real photo beside the illustration, 21 show the name on a page, 10 show neither (one recoded on 18 Oct: its photo and illustration come one shot after the other, never in one frame). 9 show the ordering site or app on a screen. **One shows a price**, and only inside a screen recording of the order form ([DVMKY6yiNgg](https://www.instagram.com/reel/DVMKY6yiNgg/), Zikit, 184 ש"ח); none puts the price in the caption. 19 offer a discount code. Across all 173 Reels, only 5 show a price in the video ([DU3kze_iAnR](https://www.instagram.com/reel/DU3kze_iAnR/), [DcIpyqmseIp](https://www.instagram.com/reel/DcIpyqmseIp/), [DeUcRMgNTVu](https://www.instagram.com/reel/DeUcRMgNTVu/), [DbaVPWWMmhx](https://www.instagram.com/reel/DbaVPWWMmhx/), DVMKY6yiNgg). My read: the larger sample confirms it. Open pricing and photo-beside-page proof are the two things LumeBook can show that the category mostly doesn't, and both can be filmed without a child.
5. **Public counts for personalised books are small.** 29 of 36 sit below 6,500 plays. The six above 10,000 are a 2024 sponsored explainer with a comment-word coupon (34,544), LumeBook's own @shoham_novik collab (23,532; boosting unknown, check Ads Manager), a speech clinician reading the MeBook book she co-created (19,983, [DRINeJwjBIZ](https://www.instagram.com/reel/DRINeJwjBIZ/)), a gan teacher's skit where a boy holds the cover beside his face (13,301, [DR7X1mIDJZC](https://www.instagram.com/reel/DR7X1mIDJZC/)), a physiotherapist's co-created book (12,705, [DP9YQwsiKQd](https://www.instagram.com/reel/DP9YQwsiKQd/)) and a first-day-of-gan story with the app on screen (10,417, [DNKYaDlsaCS](https://www.instagram.com/reel/DNKYaDlsaCS/)). Two of those six are professionals presenting a book they co-created, and a third is a gan teacher. The biggest counts in the whole sample are relatable moments and simple, useful objects: makeup on a daughter (297,086), a Winnie the Pooh baby collection on Shilav's own account (296,303), AliExpress backpacks for a family trip (198,007), the scar-gel story (168,493), a stroller-assembly joke (167,034), push lights in a gan (154,090), a clinician's reading tips (113,036). My read: this matches the 14 Oct study (`research/creator-content-conversion/report.md`, findings 2 and 3). A professional's own voice on a book is the strongest personalised-book pattern in public counts; Yarin can't be that voice, so it belongs in creator briefs (the creator brief and test T1).
6. **Comment words collect requests, not proof of buying.** 53 of 173 ask for a comment (32 name a specific word), 28 give a code, 63 have no CTA at all (recounted 18 Oct after the 8-question pass corrected four CTA codings, `src/coded_fixes_2026-10-18.json`). The first-round comment evidence still holds: 28 of 30 sampled comments on two comment-word Reels were keyword requests, while the push-light Reel with no CTA drew 14 to 16 buying questions in 30 (14 Oct study). Comments on the 132 new Reels were not read. My read: unchanged. Use LumeBook's fixed word, judge by DMs that lead to books started.
7. **Collaboration posts sit lower in public counts.** 125 of 173 are collaboration posts with a brand as co-author; their median is 4,785 plays against 15,689 for the 48 creator-only posts. This is not a fair comparison: most collabs came from brand grids of small and mid-size creators, while the creator-only posts came from the 14 Oct study's larger accounts. My read: don't conclude that collabs reach less; do note that a brand co-author tag does not by itself lift a small creator's Reel.
8. **A new common pattern: children using the product.** 39 of the 132 added Reels show children playing with or using the product with a voiceover or text (mostly Bliss play gyms and Palphot toys). It works for toys because the play is the proof. For a book the proof is the page, not the play, so this pattern needs a child and adds little that approaches A and B don't (section 2).
9. **Short wins on effort, not proven on results.** Median length 36 s; 64 of 173 are 30 s or shorter; 22 run past 60 s. No watch-time data, so "keep it under 35 seconds" stays a production choice.
10. **Disclosure is loose.** 70 of 173 say "בשיתוף" or similar in the caption or video, 4 use Instagram's paid-partnership label, and many collaboration posts (co-author tag) carry no disclosure words at all. When LumeBook briefs creators, ask for both the co-author tag and a plain disclosure line. Revised 18 Oct (T8, S7): Israeli guidance asks for the disclosure to be visible at first view, in the first caption line or on screen at the start, not only after "more" or in a tag; use Instagram's paid-partnership label too, and say in the barter terms that the book does not depend on a positive review (the Consumer Protection Authority's 2021 draft directive; its final status was not confirmed, so check with a lawyer).

Limits: not a random sample (brand grids and earlier leads); 4 of 173 are older than 12 months (kept as instructive); round-1 creators ranged from 458 to about 54,000 followers, and follower counts were not read for the 74 creators added in round 2; two brand-owned accounts (Shilav, Duty Free) appear as owners of collab posts; plays are not reach, 24 Reels have like counts hidden by the creator, and nothing here is tied to a sale. 2 candidate Reels failed to download and were not watched.

## 2. Seven approaches

| # | Approach | What it is | Best examples | Who should film it |
|---|---|---|---|---|
| A | Story with a turn | A real moment told in voiceover over home footage, the product as part of it | [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/), [DdCPPrKKRXG](https://www.instagram.com/reel/DdCPPrKKRXG/), [Dcqjk_UN7da](https://www.instagram.com/reel/Dcqjk_UN7da/), [DbAfvCdowT3](https://www.instagram.com/reel/DbAfvCdowT3/) | Creators with a real moment; Yarin only with his own true story (concept 2) |
| B | Hands and light | No face: hands, the product and daylight, with headline text | [DWW7cLNDZvv](https://www.instagram.com/reel/DWW7cLNDZvv/), [DV5ekKViujI](https://www.instagram.com/reel/DV5ekKViujI/), [DbgHCAioBPO](https://www.instagram.com/reel/DbgHCAioBPO/), [DdUJM72IFWN](https://www.instagram.com/reel/DdUJM72IFWN/) | Yarin (concepts 1 and 5) |
| C | What's inside | One label per part of the product, top-down | [Ddrev0jjauL](https://www.instagram.com/reel/Ddrev0jjauL/), [DeFlHmEErcl](https://www.instagram.com/reel/DeFlHmEErcl/), [DdqdQnKtzkK](https://www.instagram.com/reel/DdqdQnKtzkK/) | Yarin (concept 1) |
| D | Talk with it in your hands | One locked-off take to camera, product as a prop, numbered headings | [Dc6VXOdMWOv](https://www.instagram.com/reel/Dc6VXOdMWOv/), [DcSrULbN9dU](https://www.instagram.com/reel/DcSrULbN9dU/), [Dd1xnUzsb0o](https://www.instagram.com/reel/Dd1xnUzsb0o/) | Yarin for facts (concept 4); experts for expert advice |
| E | Problem first | The problem shown, then the product as the turn | [DcZCOp4ItbM](https://www.instagram.com/reel/DcZCOp4ItbM/), [Dd5sq3TI1I5](https://www.instagram.com/reel/Dd5sq3TI1I5/), [DcOu_b-sq8a](https://www.instagram.com/reel/DcOu_b-sq8a/), [Dd6wU2IM2Do](https://www.instagram.com/reel/Dd6wU2IM2Do/) | Yarin with objects (concept 3); creators with the real moment |
| F | Result first, then how | The finished thing in frame one, then the making | [DU3kze_iAnR](https://www.instagram.com/reel/DU3kze_iAnR/), [Dd4MAzHsYCr](https://www.instagram.com/reel/Dd4MAzHsYCr/), [DdZFL7NoIXu](https://www.instagram.com/reel/DdZFL7NoIXu/), [DY-LLgXI2cs](https://www.instagram.com/reel/DY-LLgXI2cs/) | Yarin (concept 5, and the making-of in concept 2) |
| G | Stack and list | Several items, one reason each | [DdWglWIKur-](https://www.instagram.com/reel/DdWglWIKur-/), [DbGbwdhoKIb](https://www.instagram.com/reel/DbGbwdhoKIb/), [DdPHzcoOTGT](https://www.instagram.com/reel/DdPHzcoOTGT/) | Yarin once three printed books are available |

### A. Story with a turn
- **Why it works (my read):** the viewer follows a person, not a product; the honest hedges in [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/) ("I was sceptical", "not magic") make the praise easier to believe, and the delivery-time question at 0:28 is exactly what a buyer worries about.
- **Fits LumeBook when:** a creator or a customer family lives a catalogue moment now (new sibling, pacifier, potty, first grade, a birthday). This is the brief for the barter creators.
- **Limits:** it needs a real moment and nearly always a child. Never script a story that did not happen. Yarin's honest version is his own test of the product (concept 2).
- **Phone notes:** voiceover recorded after filming; three or four kinds of shot (selfie, wide room shot, top-down pages, a screen recording); subtitles above the bottom 35% of the frame, where the Reels caption and buttons sit (F2, T4; revised 18 Oct from "the lower third").

### B. Hands and light
- **Why it works:** the printed book is the star; daylight and a hand make it look real and tactile. [DWW7cLNDZvv](https://www.instagram.com/reel/DWW7cLNDZvv/) holds the book up to a window or a view and ends on the dedication page.
- **Fits LumeBook when:** you need a Reel this week with no people. It is also the base layer of every other approach.
- **Limits:** on its own it can feel like an ad ([DV5ekKViujI](https://www.instagram.com/reel/DV5ekKViujI/) reads brand copy and ends on a blurry box). It needs a reason to watch: a question, a fact, a price.
- **Phone notes:** side light from a window, the phone in one hand and the book in the other, focus locked on the book.

### C. What's inside
- **Why it works:** one label per part answers "what exactly do I get" in the order a buyer asks it. [Ddrev0jjauL](https://www.instagram.com/reel/Ddrev0jjauL/) does it in 29 seconds with music only.
- **Fits LumeBook when:** answering doubts before payment. The 12 Oct note guesses that people drop at the payment step partly because they are unsure what they will get (`docs/lumebook-sales-data-decisions-2026-10-12.md`, decision 4; internal, a guess the note itself labels as one).
- **Limits:** the book has few physical parts, so fill the tour with the parts that matter: cover, the name in the text, the pictures, the dedication page, the digital copy, the price.
- **Phone notes:** steady top-down (the overhang trick in section 6), a light surface, labels in the top third.

### D. Talk with it in your hands
- **Why it works:** [Dc6VXOdMWOv](https://www.instagram.com/reel/Dc6VXOdMWOv/) is one set-up, one take with jump cuts, a new heading every three seconds, and she shows the technique instead of explaining it.
- **Fits LumeBook when:** the message is facts LumeBook owns (time, price, preview). The competitor teardown found objection-handling content only from Yoto (5 of 147 pieces), none from MeBook (`research/competitor-content-analysis/competitor_content_db.csv`).
- **Limits:** Yarin is not a clinician, so no developmental advice in his mouth; that is a job for an expert creator (topaz_meir_slp was already "in process" in the creator map on 14 Oct). Being on camera is a skill; jump cuts hide restarts.
- **Phone notes:** phone at eye level about 1 m away, window in front of you, quiet room, answers written on a sticky note next to the lens.

### E. Problem first
- **Why it works:** in [DcZCOp4ItbM](https://www.instagram.com/reel/DcZCOp4ItbM/) the paper keeps falling off the seat before the product appears, so the product's value is obvious when it does. The on-screen text and the voiceover are word for word the same, so it works muted.
- **Fits LumeBook when:** a milestone moment (pacifier, new sibling, first day at gan). These are the buying moments in the 12 Oct note (decision 1).
- **Limits:** a book does not fix a problem the way a toilet seat reducer does. Frame it as a way to talk about the moment, which is how lumebook.com itself describes the books ("כלי תומך לשיח משפחתי"). Never promise a result.
- **Phone notes:** objects can stand in for people: a pacifier on a nightstand says "toddler" without a toddler.

### F. Result first, then how
- **Why it works:** [DU3kze_iAnR](https://www.instagram.com/reel/DU3kze_iAnR/) shows the finished gift in frame one, then the making with a price on screen for every part.
- **Fits LumeBook when:** gifts (birthday is the top-selling book in the 12 Oct note; one gift-giver post a week is decision 2) and the photo-to-book journey.
- **Limits:** the process must be short and the result must look good in the very first frame.
- **Phone notes:** a wide locked-off shot for the process (phone on a shelf or a stack of books), handheld close-ups for details.

### G. Stack and list
- **Why it works:** in [DdWglWIKur-](https://www.instagram.com/reel/DdWglWIKur-/) the growing stack promises a list, then each item gets a few seconds and one reason.
- **Fits LumeBook when:** you can show three different printed stories for three moments (for example ביי ביי מוצץ, אח חדש, יום הולדת, all live on the site on 15 Oct).
- **Limits:** needs several printed books LumeBook may show; long lists drag (67 s there). Keep to three items and about 25 seconds.
- **Phone notes:** start with a locked-off medium shot of hands stacking, then top-down per book.

## 3. Weaker choices in the sample, and what to do instead

| What I saw | Where | Do this instead |
|---|---|---|
| Brand copy read as voiceover ("אמיץ, חכם, מיוחד", "ולא עוד צעצוע") | [DV5ekKViujI](https://www.instagram.com/reel/DV5ekKViujI/), [DWW7cLNDZvv](https://www.instagram.com/reel/DWW7cLNDZvv/) | Say one concrete, true thing per shot ("the name is on the first page"). |
| Ending on a blurry pan across the box | [DV5ekKViujI](https://www.instagram.com/reel/DV5ekKViujI/) 0:21-0:27 | End on the strongest image (the hero page or the dedication) with the CTA on screen. |
| Subtitles running into a screen-recording overlay | [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/) 0:11-0:27 | One layer at a time: overlay in an upper corner, subtitles just above the bottom 35% of the frame, or the screen recording full screen for two seconds. |
| 34 shots in 33.6 s of screen recording and flashing text | [C9sW-JWxUgJ](https://www.instagram.com/reel/C9sW-JWxUgJ/) | Show the ordering flow once, for three or four seconds, inside a story. |
| CTA only in the caption | [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/), [Ddrev0jjauL](https://www.instagram.com/reel/Ddrev0jjauL/) | Say the CTA and show it on screen for the last two to three seconds, after the value is clear, and put it in the caption; one action only (C1, C6). |
| Caption about a birthday, video about potty training | [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/) | One topic per Reel, same in the hook, the video and the caption. |
| No captions at all | [Dd5sq3TI1I5](https://www.instagram.com/reel/Dd5sq3TI1I5/) | Burn in captions every time. |
| Two to three minutes long | [DbAfvCdowT3](https://www.instagram.com/reel/DbAfvCdowT3/) 125 s, [Dd9cMNRs1X4](https://www.instagram.com/reel/Dd9cMNRs1X4/) 159 s | Aim for 20 to 35 seconds; cut every sentence that repeats an earlier one. |
| Hook text box covering the product in the first frames | [Dc6VXOdMWOv](https://www.instagram.com/reel/Dc6VXOdMWOv/) | Text below the top 14% and above the bottom 35% of the frame, 6% clear of each side, the product in the middle (Meta's Reels safe zone, F2 and T4; published for ads, organic Reels have the same buttons; revised 18 Oct from "the bottom fifth"). |
| Dim, blurry handheld top-down shots | [Ddrev0jjauL](https://www.instagram.com/reel/Ddrev0jjauL/) | Daylight from a window and a steadied phone. |
| "Illustrations made with AI" printed on screen | [DbydNecM1GW](https://www.instagram.com/reel/DbydNecM1GW/) at 0:14 | LumeBook rule: never mention AI in audience copy. Show the result; don't explain the method. |

## 4. Five LumeBook Reel concepts

Every concept below is filmable without a child. Times are **estimates** for a first attempt and will drop with practice. Hebrew lines are the linted script files in `src/scripts/c1.json` to `c5.json`; each Hebrew line is one beat, and line breaks replace commas on purpose.

The CTA is the same everywhere (the fixed LumeBook comment word):

<div dir="rtl" lang="he">

כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור

</div>

**One-time prerequisite for concepts 1, 2, 4, 5 and the main version of 3:** a printed LumeBook that may be shown publicly. The simplest one is a book made from Yarin's own childhood photo (concept 2), because it needs nobody else's consent. A customer or creator family's book needs that family's written OK. Ordering costs ₪119 plus delivery (or free pickup in Jerusalem) as of 15 Oct; ask Yossi whether the company covers it.

### Concept 1: "מה באמת מקבלים" (what you actually get)

- **Idea:** a hands-only tour of one printed book that answers what a buyer gets and what it costs.
- **Intended response:** "Now I know exactly what I'd get, and for how much." Save, share, comment the word.
- **Grounded in:** the labelled tour of [Ddrev0jjauL](https://www.instagram.com/reel/Ddrev0jjauL/), the window light and dedication ending of [DWW7cLNDZvv](https://www.instagram.com/reel/DWW7cLNDZvv/), the unboxing order of [DV5ekKViujI](https://www.instagram.com/reel/DV5ekKViujI/) (minus its weak ending), prices on screen as in [DU3kze_iAnR](https://www.instagram.com/reel/DU3kze_iAnR/), page close-ups as in [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/).
- **Length:** about 33 seconds.

**Hook (on screen, 0:00-0:02):**
<div dir="rtl" lang="he">

מה באמת מקבלים<br>
ב-119 ש״ח?

</div>

**Shot list**

| # | Time | Shot | How to film it | Voiceover beat | Label on screen |
|---|---|---|---|---|---|
| 1 | 0:00-0:03 | Top-down: the book comes out of its packaging | Phone on the overhang rig (section 6), 30-40 cm above the table. Hold your finger on the packaging to lock focus and exposure. Start recording, wait one second, pull the book out and lay it cover up. No packaging? Start with the book face down and flip it. | V1 | Hook |
| 2 | 0:03-0:07 | The cover held up beside the window | Stand next to the window so daylight hits the cover from the side, not from behind. Book in your left hand at arm's length, phone in your right at chest height, cover filling most of the frame. Hold 3 seconds still, then tilt the book slowly. | V2 | 22 על 22 ס״מ, then 24 עמודים בצבע |
| 3 | 0:07-0:11 | Close-up: the cover, then the first spread with the name in the text | Back on the table, phone handheld 15-20 cm above, tap to focus on the name. Open slowly. | V3 | 10 תמונות בפנים |
| 4 | 0:11-0:16 | Top-down flip-through | Overhang rig again. Turn four pages, about one per second, flat hand, no rushing. Speed up 1.5x in the edit if it drags. | (continues V3) | השם בתוך הסיפור |
| 5 | 0:16-0:20 | The dedication page | Open to the dedication page, rest a pen beside it. Hold still 3 seconds. | V4 | עמוד הקדשה |
| 6 | 0:20-0:24 | The digital copy | Screen-record your own order email or the digital book on a phone or laptop (hide email addresses and order numbers). Or film a phone showing the digital book next to the printed one. | V5 | עותק דיגיטלי במייל |
| 7 | 0:24-0:29 | The free preview | Screen-record the preview step on lumebook.com, 3-4 seconds of it. | V6 | תצוגה מקדימה בחינם |
| 8 | 0:29-0:33 | End card | The book standing upright on the table, cover to camera, static, 5 seconds. | CTA | The CTA |

**Voiceover beats**

<div dir="rtl" lang="he">

V1: מה באמת מקבלים<br>
בספר אישי של לומיבוק?

V2: ספר מודפס 22 על 22<br>
כריכה רכה ו-24 עמודים בצבע

V3: על הכריכה הילד שלכם<br>
ובפנים עוד 10 תמונות שלו<br>
והשם שלו בתוך הסיפור

V4: פה יש עמוד הקדשה<br>
מודפסת או ריקה<br>
כדי לכתוב ביד

V5: ועוד לפני שהוא מגיע<br>
מקבלים עותק דיגיטלי במייל

V6: את התצוגה המקדימה רואים בחינם<br>
ומשלמים רק אם אהבתם

</div>

**Caption** (last line is the CTA):
<div dir="rtl" lang="he">

ספר מודפס 22 על 22<br>
24 עמודים בצבע<br>
הילד שלכם על הכריכה ובתוך הסיפור<br>
עמוד הקדשה<br>
עותק דיגיטלי במייל<br>
119 ש״ח ומשלוח עד הבית ב-30 ש״ח<br>
את התצוגה המקדימה רואים בחינם<br>
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור

</div>

- **Price on screen (S3, added 18 Oct):** Israel's Consumer Protection Law (section 17ד) says a published price must be the total price. Free pickup may make ₪119 the total, but the hook shows ₪119 alone while home delivery costs ₪30, so either add "ומשלוח 30 ש״ח" to the hook card or check with a lawyer before posting. The caption already states both.
- **Props:** the printed book, its packaging if you kept it, a pen, a light plain surface (white sheet, poster board or a light table), a second screen for the screen recordings.
- **Location and light:** a table beside a window in daytime, ceiling lights off (mixed light turns skin and paper yellow-green). Avoid direct sun on the page; a white sheet on the far side bounces light back.
- **Phone placement:** overhang rig for top-down shots, handheld for the window and close-up shots.
- **Sound:** voiceover recorded afterwards in a quiet room (see section 6). Music optional, low, added in Instagram from a track the account may use (E5: Instagram's licensed library is for personal, non-commercial use and some business accounts can't use it; Meta's Sound Collection is cleared for commercial use).
- **Editing recipe:** clips in shot order; cut each to its beat; record the voiceover over the timeline; auto captions, then fix every Hebrew word by hand; labels in the top third; page flips at 1.2-1.5x; hook text on the first frame; export 1080 x 1920; pick the cover frame with the hook text on it.
- **With a family instead:** a parent opens the same book with their child at a table; the same labels on screen. Creator brief, not Yarin's shoot.
- **Estimated time:** filming 45-60 minutes, editing 60-90 minutes the first time.

### Concept 2: "הכנתי ספר מתמונה שלי בגיל 4" (the likeness test, on himself)

- **Idea:** Yarin makes a LumeBook from a photo of himself at about four, then holds the photo beside the illustrated page.
- **Intended response:** a smile, "it really is him", then "what would my kid look like?" Comments answering the question at the end; free previews started.
- **Grounded in:** the photo-beside-page split screen of [DbAfvCdowT3](https://www.instagram.com/reel/DbAfvCdowT3/) and the photo cards of [DV6fjEojHSs](https://www.instagram.com/reel/DV6fjEojHSs/); the sceptic-to-"it's really her" line and screen overlay of [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/); the creation-on-a-screen shots of [DdCPPrKKRXG](https://www.instagram.com/reel/DdCPPrKKRXG/) and [DVlyDocjXU4](https://www.instagram.com/reel/DVlyDocjXU4/); the 10-of-147 likeness-proof gap in the competitor teardown.
- **Honesty rule:** film your real first look at the printed book. If you have already seen the preview, don't act surprised; say the lines calmly. Use the real age in the photo instead of 4.
- **Length:** 30-35 seconds.

**Hook (on screen and spoken, 0:00-0:02):**
<div dir="rtl" lang="he">

הכנתי ספר<br>
מתמונה שלי בגיל 4

</div>

| # | Time | Shot | How to film it | Beat |
|---|---|---|---|---|
| 1 | 0:00-0:03 | Selfie at eye level holding the old photo beside your face | Phone propped at eye level about 70 cm away, window in front of you. No-face version: your hand holds the photo in front of the lens with the book's cover blurred behind it. | V1 |
| 2 | 0:03-0:07 | You to camera, or the photo full screen | Say the lines once each, three takes, keep the best. | V2 |
| 3 | 0:07-0:13 | Screen recording of making it, sped up | Phone screen recorder while you choose the story, upload the photo and wait for the preview. Crop to the screen. | V3 |
| 4 | 0:13-0:17 | The printed book on the table; a hand opens it to your page | Overhang rig, top-down. | |
| 5 | 0:17-0:23 | The comparison: old photo beside the illustrated page, same size, both in frame | Top-down, hold 3 seconds still. In the edit, add the two labels and leave 1.5 seconds of silence after "וזה מה שיצא". | V4 |
| 6 | 0:23-0:27 | Your face looking at it, or a second page with you on it | Handheld. Optional. | |
| 7 | 0:27-0:30 | The question | Text on screen over shot 5 or 6. | V5 |
| 8 | 0:30-0:33 | End card | Book upright, static. | CTA |

<div dir="rtl" lang="he">

V1: הכנתי ספר<br>
מתמונה שלי בגיל 4

V2: אני ירין<br>
אני מנהל את הסושיאל של לומיבוק<br>
ורציתי לבדוק בעצמי אם זה יוצא דומה

V3: בחרתי סיפור<br>
העליתי תמונה אחת שלי מגיל 4<br>
וחיכיתי לתצוגה המקדימה

V4: וזה מה שיצא

V5: תגידו אתם<br>
זה אני או לא?

תוויות: אני בגיל 4 · אני בספר

כיתוב: רציתי לבדוק על עצמי לפני שאני ממליץ לכם<br>
תמונה אחת שלי מגיל 4<br>
וזה מה שיצא<br>
זה אני או לא?<br>
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור

</div>

- **Props:** the old photo (a print, or on a second phone), the printed book, a phone or laptop for the screen recording.
- **Location and light:** the same window table; for the selfie, face the window.
- **Phone placement:** at eye level on a shelf or a stack of books, leaning on a mug.
- **Sound:** lines to camera in a quiet room with soft furnishings, phone within 1 m; or voiceover afterwards.
- **Editing recipe:** keep the comparison as one real top-down shot (no split-screen work needed); labels on the right for the photo and on the left for the page, matching Hebrew reading order; screen recording at 2-3x.
- **Without showing a child:** the whole concept is child-free. A digital-only variant works before the print arrives: phone showing the preview next to the old photo.
- **Estimated time:** making the book 15 minutes plus delivery (up to 7 business days); filming 40-60 minutes; editing 60-90 minutes.

### Concept 3: "הלילה האחרון עם המוצץ" (a pacifier night, told with objects)

- **Idea:** a POV night told in on-screen text, with objects instead of a child. The book enters halfway as a way to talk about the change. The catalogue's "ביי ביי מוצץ" (live on 15 Oct) is a goodbye story in which the family decorates the pacifier with flowers and ribbons, so the props echo the book.
- **Intended response:** "That's our week." Send to a partner, save, comment the word.
- **Grounded in:** the POV mishap with the product as the turn in [DcZCOp4ItbM](https://www.instagram.com/reel/DcZCOp4ItbM/); the milestone-fear hook of [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/); one action in close-up from [Dd5sq3TI1I5](https://www.instagram.com/reel/Dd5sq3TI1I5/); the pacifier as a top milestone in the 12 Oct note (decision 1).
- **Length:** about 25 seconds. No voice.

| # | Time | Shot | How to film it | Text on screen |
|---|---|---|---|---|
| 1 | 0:00-0:03 | A pacifier on a nightstand beside a lit night-light, dark room | Phone handheld 20 cm away, slow push-in of about 10 cm. Tap the pacifier and drag exposure down so the room stays dark and the light stays soft. | T1 |
| 2 | 0:03-0:07 | A hand picks the pacifier up and turns it | Same light, a little wider. | T2 |
| 3 | 0:07-0:11 | The book on a blanket under the lamp; a hand opens it | Top-down or 45 degrees. | T3 |
| 4 | 0:11-0:15 | Close-up on the page with the character and name | Hold still. | T4 |
| 5 | 0:15-0:19 | Hands tie a ribbon or a small flower on the pacifier | Close-up; slow hands. | T5 |
| 6 | 0:19-0:22 | The decorated pacifier laid on the open book; the night-light clicks off | One take. | T6 |
| 7 | 0:22-0:25 | End card | Same frame, lamp off, CTA text. | CTA |

<div dir="rtl" lang="he">

T1: הלילה האחרון<br>
עם המוצץ

T2: ועוד לא החלטתם<br>
איך מדברים איתו על זה

T3: יש סיפור שבו הוא בעצמו<br>
נפרד מהמוצץ

T4: עם השם שלו<br>
והדמות שלו בתוך הסיפור

T5: בסיפור מקשטים את המוצץ<br>
ונפרדים ממנו יחד

T6: וככה מתחילים לדבר על זה<br>
כבר מהסיפור

כיתוב: הלילה האחרון עם המוצץ<br>
בספר ביי ביי מוצץ הילד שלכם הוא זה שנפרד<br>
עם השם שלו והדמות שלו<br>
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור

</div>

- **Props:** a clean pacifier, a night-light or bedside lamp, a ribbon or a small fabric flower, a blanket, and the ביי ביי מוצץ book (printed, or its preview on a phone lying on the blanket).
- **Book caveat:** the book shown must be one LumeBook may show: a consenting family's copy, or the phone-preview variant. A pacifier book about Yarin works too, but it reads less naturally.
- **Location and light:** a bedroom or the sofa at night; one warm lamp close to the props, every other light off.
- **Sound:** no voice; a quiet track at low volume (from Meta's Sound Collection if the account can't use the licensed library, E5), or just the lamp click. Instagram shows muted Reels less (H6), so never post it silent.
- **Editing recipe:** six text cards, each 3-4 seconds, two lines each in the top third; straight cuts; end card 3 seconds.
- **With a family instead:** the parent films the real ceremony with the child, faces optional (hands, back of the head). Creator brief.
- **Estimated time:** filming 30-45 minutes, editing 45-60 minutes.

### Concept 4: "3 דברים לדעת לפני שמזמינים" (three facts, to camera)

- **Idea:** Yarin, book in hand, answers three practical questions with checked facts.
- **Intended response:** fewer doubts before paying. That doubts cause the drop at payment is the 12 Oct note's guess, not a finding, so treat this Reel as a test.
- **Grounded in:** the one-take, numbered, product-in-hand format of [Dc6VXOdMWOv](https://www.instagram.com/reel/Dc6VXOdMWOv/); the objection said out loud in [DTugYwmDNKa](https://www.instagram.com/reel/DTugYwmDNKa/); the talking-head bookends of [DcSrULbN9dU](https://www.instagram.com/reel/DcSrULbN9dU/); the gap in objection content in the competitor teardown.
- **Length:** 30-35 seconds.

| # | Time | Shot | How to film it | Beat | Label |
|---|---|---|---|---|---|
| 1 | 0:00-0:03 | Medium shot, chest up, book held to camera | Phone at eye level about 1 m away on a shelf or a stack of books; window in front of you; plain wall 1 m or more behind you. | V1 | Hook |
| 2 | 0:03-0:12 | You answering question 1, with a 2-second cutaway to the phone showing the digital copy | Each answer is its own take; do three of each. | V2 | 1 כמה זמן? |
| 3 | 0:12-0:21 | You answering question 2, cutaway to a screen recording of the preview | | V3 | 2 זה דומה? |
| 4 | 0:21-0:29 | You answering question 3, cutaway to the price on the product page | Screen-record the price the day you post. | V4 | 3 כמה זה עולה? |
| 5 | 0:29-0:34 | You saying the CTA, then the end card | | CTA | |

<div dir="rtl" lang="he">

V1: 3 דברים שכדאי לדעת<br>
לפני שמזמינים ספר אישי

V2: כמה זמן זה לוקח?<br>
המודפס מגיע עד 7 ימי עסקים<br>
והדיגיטלי במייל תוך דקות

V3: זה באמת ייראה כמו הילד שלי?<br>
את זה רואים לפני שמשלמים<br>
התצוגה המקדימה בחינם

V4: כמה זה עולה?<br>
119 ש״ח לספר מודפס<br>
ומשלוח עד הבית ב-30 ש״ח

כיתוב: מודפס עד 7 ימי עסקים<br>
דיגיטלי במייל תוך דקות<br>
תצוגה מקדימה בחינם<br>
119 ש״ח ומשלוח עד הבית ב-30 ש״ח<br>
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור

</div>

- **Props:** the book, a sticky note with the three answers stuck beside the lens, a second screen for the cutaways.
- **Sound:** the room matters more than the phone: a bedroom with a bed and curtains echoes less than a kitchen. Phone within 1 m. Wired earphones with a mic, if you already own a pair, put the mic closer to your mouth than the phone can be.
- **Editing recipe:** cut out pauses and restarts (jump cuts are fine); auto captions, corrected by hand; numbered labels in the top third; cutaways full screen for 2 seconds each.
- **Without showing a child:** child-free by design.
- **Estimated time:** filming 45-75 minutes (most of it is retakes), editing 60-90 minutes.

### Concept 5: "מתנה לנכד שאין לאף ילד אחר" (a gift with a handwritten dedication)

- **Idea:** for grandparents and relatives: the wrapped gift first, then the dedication being written, the wrapping, the price.
- **Intended response:** "That's what I'm bringing to the birthday." Shared in a family WhatsApp, the word commented.
- **Grounded in:** result first and prices on screen from [DU3kze_iAnR](https://www.instagram.com/reel/DU3kze_iAnR/); the dedication-page close of [DWW7cLNDZvv](https://www.instagram.com/reel/DWW7cLNDZvv/); hands-only gift steps with word-by-word captions from [DdBkaEoIT_F](https://www.instagram.com/reel/DdBkaEoIT_F/); decision 2 of the 12 Oct note (one gift-giver post a week; that buyers are grandmothers is still a hypothesis there).
- **Honesty rule:** write a neutral sample dedication ("יום הולדת שמח" and a heart), never a made-up message signed by a grandparent. The label says it is the viewer's space.
- **Length:** about 25 seconds.

| # | Time | Shot | How to film it | Beat | Label |
|---|---|---|---|---|---|
| 1 | 0:00-0:02 | Top-down: the wrapped gift with a ribbon | Overhang rig. | V1 | Hook |
| 2 | 0:02-0:05 | Hands lay the unwrapped book on the wrapping paper | Same rig. | V2 | |
| 3 | 0:05-0:10 | Close-up: the pen writes on the dedication page | Handheld 15 cm, focus locked on the page. | V3 | עמוד הקדשה, then ההקדשה שלכם כאן |
| 4 | 0:10-0:15 | Hands fold the paper around the book | Rig; speed 2x in the edit. | V4 | |
| 5 | 0:15-0:18 | Tying the ribbon | Close-up. | (V4) | |
| 6 | 0:18-0:21 | The wrapped gift with the price on screen | Rig. | | 119 ש״ח ומשלוח עד הבית ב-30 ש״ח |
| 7 | 0:21-0:25 | End card | Same frame. | CTA | |

<div dir="rtl" lang="he">

V1: מתנה לנכד<br>
שאין לאף ילד אחר

V2: ספר שהוא הגיבור שלו<br>
עם השם שלו והדמות שלו

V3: יש בו עמוד להקדשה<br>
ואפשר לכתוב אותה ביד

V4: עוטפים<br>
מוסיפים סרט<br>
ומחכים ליום ההולדת

CTA: כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הנכד שלכם הוא הגיבור

כיתוב: מתנה ליום הולדת שאין לאף ילד אחר<br>
השם שלו והדמות שלו בתוך הסיפור<br>
ועמוד הקדשה שכותבים ביד<br>
119 ש״ח ומשלוח עד הבית ב-30 ש״ח<br>
כתבו "לומי" בתגובות וקבלו קישור ליצירת ספר שבו הנכד שלכם הוא הגיבור

</div>

- **Props:** the book (ordered with the blank dedication option, or any copy with a dedication page), wrapping paper, a ribbon, a pen that writes well on paper, scissors and tape.
- **Location and light:** the window table in daytime.
- **Sound:** voiceover afterwards, or text only with quiet music.
- **Editing recipe:** word-by-word captions for the voiceover; wrapping at 2x; price card for three seconds before the CTA.
- **With a creator instead:** a grandmother-age creator writes her own real dedication (the 12 Oct note asks for two or three creators of grandmother age).
- **Estimated time:** filming 30-45 minutes, editing 45-60 minutes.

## 5. Your first shoot: concept 1, in 60 to 90 minutes

Concept 1 is the best start: no face, no voice on camera, one room, and every line is a checked fact. Follow this order exactly; it groups shots by set-up, not by timeline. After the 18 Oct research check, concept 2 is the better-supported first Reel (section 8); this plan stays written for concept 1, with the voiceover starting at 0:00.

**The day before (10 minutes)**
- Make sure you have the printed book you may show publicly. If you don't have one yet, this shoot waits for it.
- Charge the phone, free at least 5 GB, and save the script (`src/scripts/c1.json`) or this section where you can read it while filming.
- Collect: the book, its packaging if you have it, a pen, a white sheet or poster board, 25-30 cm of books for the overhang rig, a laptop or second phone for screen recordings.

**0:00-0:10 Set up**
- Table next to the window, ceiling lights off, white sheet on the table.
- Build the overhang rig (section 6) at the table edge. Check the frame: the whole book fits with a little space around it.
- Phone: video at 1080p or 4K, 30 fps, grid on, Do Not Disturb on, lens wiped with a soft cloth.

**0:10-0:35 Set-up 1, overhead rig: shots 1, 4, 5, 8** (essential)
- Shot 1 (book out of the packaging): three takes.
- Shot 4 (flip-through): three takes, slow and even.
- Shot 5 (dedication page): one 5-second hold.
- Shot 8 (end card): lift the book off the rig area and stand it up in the frame; one 5-second static take.
- Before each take: hold your finger on the book to lock focus and exposure.

**0:35-0:50 Set-up 2, handheld at the window: shots 2 and 3** (essential)
- Shot 2: cover held up beside the window, three takes, the last one with a slow tilt.
- Shot 3: close-up of the cover, then the first spread with the name, two takes.

**0:50-1:00 Set-up 3, screen recordings: shots 6 and 7** (essential)
- Shot 6: your order email or the digital book, 6 seconds; blur personal details later.
- Shot 7: the preview step on lumebook.com, 6 seconds.
- Also screen-record the product page with today's price (spare footage for concepts 4 and 5).

**1:00-1:15 Voiceover**
- Quiet room with soft furnishings (a bedroom or a closet full of clothes), phone 20 cm from your mouth, the phone's voice recorder or the editing app's voiceover tool.
- Read V1 to V6 and the CTA, each line three times, slowly, with a short pause between lines. Keep the take that sounds most like you talking to a friend.

**1:15-1:30 Optional extras** (only if time allows)
- A slow push-in on the closed book on the table (B-roll for later).
- Hands holding the book up to the window from the other side of the room (a second angle for shot 2).
- Your hand writing on the dedication page (spare footage for concept 5).

**Edit order (60-90 minutes, a separate session; estimate)**
1. Import everything into a free editor you already have (CapCut's free tier or Instagram's Edits); don't pay for anything.
2. Lay the best take of each shot in shot-list order.
3. Trim each shot to its beat; page flips at 1.2-1.5x.
4. Drop in the voiceover; move clips so each label lands with its line.
5. Auto captions, then fix every Hebrew word by hand.
6. Labels from the shot list in the top third, one at a time.
7. The hook text on the first frame; check that frame works as the cover.
8. The end card with the CTA for the last 3 seconds.
9. Watch it once muted and once with sound. Fix anything that only one of the two explains.
10. Export 1080 x 1920. Post with the caption above, tag @lumebook.il, and put the UTM link you use for the comment word in your DM reply (section 7).

## 6. Phone set-up, once for all concepts

- **Overhang rig (no tripod):** stack 25-30 cm of heavy books at the edge of the table, lay the phone flat on top with the camera end sticking out past the edge, screen up, lens pointing down. Put something heavy on the phone's other end. The space beneath the lens is your top-down stage.
- **Eye-level rig:** a shelf or a stack of books at face height, the phone standing against a mug, about 1 m from you.
- **Lock focus and exposure** on the product before every take (press and hold on it). Drag exposure down a little for dark scenes.
- **Light:** one window, side-on to the product. No overhead lights mixed in. No direct sun on glossy pages (reflections).
- **Lens:** wipe it before every set-up.
- **Frame for Reels:** keep text and the product out of the top 14%, the bottom 35% and the outer 6% of each side, where the Reels player shows its caption and buttons (Meta's Reels safe zone, F2 and T4; revised 18 Oct from "the bottom fifth"; check your own Reel in the app before posting).
- **Hebrew text:** start every line with a Hebrew letter, not a digit, an emoji or "LumeBook", so punctuation and numbers land on the right side; keep each card on screen for at least its character count divided by 17 seconds (T5, T6, from Netflix's Hebrew subtitle standard and Unicode's bidi rules).
- **Sound:** record speech in soft rooms, close to the phone. Record voiceovers separately; it is easier to sound natural reading to nobody.
- **Privacy:** no other family's child, name or photo without their written OK; blur email addresses and order numbers in screen recordings. Israel's Privacy Protection Authority (guidance of 25 Nov 2025) recommends not showing a young child's face in public posts, and using a person's image for profit without consent is a privacy violation under section 2(6) of the Privacy Protection Law (S5). Whether the Youth Employment permit for children under 15 in advertising covers barter creator content is a question for a lawyer.

## 7. After posting: what to log

The store's public code sends UTM parameters and a visitor ID with each book started, when the visitor accepts analytics cookies; whether the admin reports them per order is still unknown (`research/creator-content-conversion/report.md`, section 11). Tag every link anyway, so the data exists once someone can read it:

- Give each concept its own link for the DM reply, for example `utm_source=instagram&utm_medium=social&utm_campaign=whats-inside&utm_content=dm-20261102&utm_term=c1-v1` (since 31 Oct 2026: `utm_medium` is always `social`, the value Yossi counts as Yarin's, and the concept goes in `utm_term`; `research/cro-crm/measurement.md` section 4). Keep names lower case and identical every time: UTM values are case sensitive in Google Analytics (`research/organic-content-conversion-notes-2026-10-14.md`).
- One line per Reel in the daily log the 12 Oct note asks for: date, concept, hook, plays after 24 hours, comment-word requests, DMs answered, link clicks, books started (if the admin shows them per UTM).
- Compare concepts by books started and DMs, not by plays. One Reel proves nothing; run each concept at least twice before judging it.
- Added 18 Oct: also log from Insights, 24 hours after posting, the **skip rate** (share who left in the first 3 seconds), **average watch time**, **sends** per reach and the share of views from **non-followers**. These are the signals Instagram says it ranks Reels on (H1, R1, R5, R8). To test two hooks on the same footage, post one as a Trial Reel (shown to non-followers first) and keep the hook with the lower skip rate.

## 8. Is the playbook proven? The research check of 18 Oct 2026

Three kinds of evidence stand behind each rule, weakest last for LumeBook:

1. **Outside research.** 63 principles from platform documentation (Instagram, Meta, TikTok, YouTube), peer-reviewed studies, large industry datasets and Israeli regulators, each rated strong, moderate, weak or contested (`smm-research/principles.md`; the full evidence and the traced myths are in `smm-research/notes/`). Most platform numbers come from paid ads, not organic Reels, and nothing found is specific to Hebrew Reels except the legal rules and Netflix's Hebrew subtitle standard.
2. **Our 173 Reels.** Every Reel answers the eight questions (hook, every few seconds, CTA, what is shown, editing, topic, filming, text), and every why names the principles behind it (`src/table/`, on the page as "Reel-by-reel table"). Each feature a principle predicts was then compared on public counts: plays per follower and interaction rate, with and without the feature, overall and again inside collaboration posts and creators' own posts (`smm-research/sample-check.md`, built by `src/evidence_check.py`). This is correlation in a sample that was not chosen at random: it can agree or disagree with a rule, never prove it.
3. **LumeBook's own Reels.** The only real proof, and it doesn't exist yet. Section 7 lists what to log.

"Clear" below means p < 0.05 and the same direction inside both groups of posts; "leaning" means the same direction without that certainty. With 68 comparisons, about three would look clear by chance, so treat a single clear result as a lead, not a finding. Medians are plays per follower (all 173 Reels have a follower count, read 14 to 18 Oct 2026).

| Playbook rule | Outside research | Our 173 Reels | Verdict |
|---|---|---|---|
| Product on screen in the first second | S1, H2 moderate; H1 strong: Instagram's ranking model predicts skips within 3 seconds | 150 with vs 23 without: 0.74 vs 0.48, leaning | **Holds** |
| Text on screen, hook text on the first frame | T1, T3, H6 moderate | Any text 0.74 vs 0.29 (clear, only 19 without); text in the first frame 0.76 vs 0.43 (clear) | **Holds** |
| Subtitle every spoken line | T1 moderate; T2: short key phrases beat full transcripts (learning research); Meta says most Reels views are sound on | Subtitled speech 0.71 vs 1.27 unsubtitled, leaning lower, only 13 without | **Holds, changed:** key phrases, not full sentences, above the bottom 35% |
| Voice is optional | H4, H6 moderate: speech in the first 3 seconds lifted early retention in 10,110 brand Facebook Reels; Instagram shows muted Reels less | Speech: no clear difference in plays, leaning higher interaction | **Changed:** voice recommended from the first second; a text-and-music Reel (concept 3) becomes the test, not the default |
| Hands only, no face (Yarin's main formats) | Mixed: S4 (hands holding the product drew more purchase-intent comments in 250,000 brand photos) against H4 and K8 (faces lift likes and early retention) | No face at all: 0.45 vs 0.76, clear lower on both measures and inside both groups; an adult's face: 0.77 vs 0.65, clear higher | **Changed, the biggest finding:** keep hands for the product shots, but add Yarin's voice from 0:00 and test an opening second on his face |
| No child on camera in Yarin's Reels | S5 strong as a legal and policy rule (Israel's Privacy Protection Authority, Nov 2025; Privacy Protection Law section 2(6)) | Child on camera: 0.75 vs 0.69 leaning, interaction clearly higher | **Holds for legal reasons, at a likely cost;** creator Reels with written consent fill the gap |
| Relatable moments and useful objects beat book pitches | K1 strong (high-arousal positive emotion is shared), K3 strong (relatable humour), K4 contested alone, consistent with emotion | Tagged product showcase or unboxing: 0.61 vs 1.09, clear lower; humour 1.81 vs 0.71, clear higher (10 Reels); useful tip 0.81 vs 0.64, mixed | **Holds, stronger:** every product Reel needs a reason to watch beyond the product |
| Comment word לומי, judged by DMs | C3 strong on the mechanics (one private reply per comment, within 7 days), weak on the effect; C2: asks made only to raise counts are engagement bait | Comment-word Reels 0.86 vs 0.65, leaning; interaction clearly higher, partly because the word itself is a comment | **Holds, with conditions:** the word always delivers the link; never "comment yes" for its own sake |
| One CTA, on screen at the end and in the caption | C1 moderate (more than one CTA lowered engagement), C6 weak for organic Reels | Any CTA 0.81 vs 0.52, clear; CTA on screen 0.91 vs 0.64, clear; discount code no difference | **Holds** |
| Invite a comment with a real question | C5, R6 moderate | Any invitation to comment, share or save 0.86 vs 0.58, clear; a question in the caption 0.84 vs 0.62, mixed | **Holds** |
| Keep it 20 to 35 seconds | R2 weak for any best length (Socialinsider's 6 million brand Reels: 45 to 60 s did best, correlational); R1 strong: watch time is judged against Reels of the same length | 30 s or shorter 0.61 vs 0.74, no clear difference | **Changed:** length follows the content; cut every second that adds nothing |
| A cut every 3 to 5 seconds, no fast cutting | E2, R3 moderate: moderate pace and jump cuts within one scene; very fast pace lowered intent to keep watching | Average shot under 3 s: 0.62 vs 0.78, mixed lower | **Holds** |
| Show the price openly; photo beside the illustration | S3 strong as law (a published price must be the total price), contested for sales; S2 weak to moderate | 7 and 5 Reels: too few to tell | **Unproven:** gaps in the category to test, not proven winners |
| A short screen recording of making the book | S8 moderate (customising raises the buyer's own valuation; watching someone else do it is untested) | 12 Reels: 0.88 vs 0.72, leaning | **Unproven, promising** |
| Problem first, a story with a turn | K2 strong (narrative persuasion), K6 moderate, H5 moderate | Hook names a problem: no difference; story arc: no difference | **Unproven in the sample;** keep for creators with a real moment |
| Text placement, disclosure, music, Hebrew lines, logging | F2, T4 (safe zone), T8, S7 (disclosure at first view), E5 (music licences), T5, T6 (Hebrew reading speed and RTL), R8 (Insights signals) | Not testable from public counts | **Changed on 18 Oct** where each rule stands (sections 1, 2, 3, 6, 7 and concept 1) |

**What this changes in the five concepts**

- **Concept 1 (what you actually get):** keep the voiceover from 0:00 (it already has one). Film a second version that opens on one second of Yarin's face saying V1, and post both as Trial Reels; keep the one with the lower skip rate. Fix the price card (S3, the note in concept 1).
- **Concept 2 (a book from my photo at 4):** the best-supported concept now: a face, a curiosity gap paid off by the photo beside the page, a story with a turn (H4, H5, K2, S2). Film it first if a printed book is available; it needs nobody's consent.
- **Concept 3 (the pacifier night):** the research leans against a voiceless Reel (H4, H6). Record a whispered voiceover version and test it against the text-only one.
- **Concept 4 (three facts to camera):** a face and direct address are supported (F6, H4), and facts in emotion beat facts alone (K4). Numbered lists leaned lower in the sample (21 Reels), so keep the three facts short and warm.
- **Concept 5 (a gift with a dedication):** a buying moment and a buyer named (K7) are supported; it is hands only, so the voiceover must start at 0:00.

**How sure this is:** the principles are as strong as their rating says; the sample check is 173 public Reels read on 15 Oct 2026, no shares, saves, watch time or sales; the 8-question rows were written by eight agents from the frames, transcripts and captions with one brief (`src/TABLE_BRIEF.md`), all rows pass `src/check_table.py`, and I checked the Hebrew quotes, timings and text positions of eleven rows, at least one from each agent, against the frames myself: all matched, apart from one banner listed a second early. Ten first-pass codings were corrected along the way (`src/coded_fixes_2026-10-18.json`); remarks about video resolution were removed from the rows, because a downloaded copy can be smaller than what was posted.
