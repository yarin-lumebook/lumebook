# @adar.motherhood: voice, hooks and CTAs (11 / 11 / 2026)

How Adar (@adar.motherhood) writes and opens her content, how she asks for action, and how to make content that works the same way for LumeBook. Internal study, one account, read on 11 / 11 / 2026 from the signed-in built-in browser.

**Who she is (profile read 11 / 11 / 2026):** a mom of two who homeschools, sells parent guidance in a holistic approach (homeschooling and potty training), 7,030 followers, 1,092 posts. She is in our creator map (`creators/creator-research/creators-200-2026-10-03.csv`) and got our ambassador DM on 11 / 10 / 2026 (`creators/creator-research/state/outreach.json`).

**What was read:**

| Evidence | Count | File |
|---|---|---|
| Every Reel in her Reels tab, with plays, likes, comments | 591 (2017 to 09 / 11 / 2026), 390 since 01 / 01 / 2025 | `data/reels.json` |
| Top Reels since 2024 (all with 19,000+ plays) | 22 | `data/selected.json`, `data/coded.json` |
| Controls: same period, plays 1,200 to 3,500 (her median is 2,404) | 12 | same |
| Frames of the first 6 seconds, full caption, audio type, for all 34 | 34 | `media/projects/2026-11-11-adar-motherhood-reels/` (local) |
| Whisper transcript, only where the audio is original sound | 12 | same |
| First page of comments (about 14 each) | 11 Reels | `data/comments_sample_2026-11-11.json` (handles masked) |
| Carousels: her biggest one plus the 8 latest | 9 | `data/posts_info_2026-11-11.json` |

Everything below is correlation inside one account with small samples (22 against 12). Treat the patterns as hypotheses to test, not rules. Where I counted something, the count is given.

---

## The short version

1. **Her account runs on rare breakouts.** Since 01 / 01 / 2025 the median Reel has 2,404 plays, 19 Reels passed 20,000 and 8 passed 100,000; the top 5 hold 54% of all plays (`data/reels.json`). So "like her" means: post a lot for followers, and build each Reel so it can break out.
2. **Breakouts are short, silent, text first.** 21 of the 22 top Reels have text on screen from the first frame (the 22nd by 1.5 s). Only 3 of the 22 have real speech; the rest are music plus text over raw phone video. Median length 19 seconds against 25 for the controls.
3. **The hook is a situation or someone else's sentence, never a topic.** Two families of hooks carry her top Reels: a judgement people say to her, answered by a number you can see (4 top Reels), and a one line "when / POV" situation, usually starring her husband (6 top Reels). The same quoted question format with an ordinary answer stayed at the median (3 controls).
4. **Most of her biggest Reels ask for nothing.** 18 of 22 top Reels have no call to action. When she does ask, the best one is a comment keyword for a free thing: one Reel got 250 comments, 12.8 per 1,000 plays against her median of 0.69, almost all of them the keyword.
5. **Her biggest carousel is a child talking to a parent.** 7,191 likes on a 7,030 follower account: a child's lines to dad, "today" against "one day", and a last slide that says send this to dad. Her later carousels that open with an abstract statement or a general question got 18 to 39 likes.

---

## 1. Her voice

She writes in two registers and switches between them by format.

**On the video (hook text):** spoken, short, a little cheeky. Slang and one-word reactions, an exclamation that sounds like her talking to a friend, two or three emoji at the end of the line. She laughs at her own life, mostly at her husband. Examples of the tone (my paraphrase unless quoted): a quoted "until when will you nurse him?" followed by "6 months? let's not overdo it!" over a toddler who has nursed for 33 months; a storm, a cold pool, and the line that she and her husband are a little crazy.

**In the caption and on carousel slides:** warm conviction, written for one woman. Patterns that repeat:

- **Addresses one mom in feminine singular** (את, תעקבי, שמרי), sometimes the couple in plural.
- **A rhetorical question, then her answer on its own line** ("and the thing that drives me most crazy?" then the answer).
- **Short lines with a lot of air**, often one sentence per line, three beats in a row (the respect, the presence, the way you talk to her).
- **Us against the norm:** "the system", "diaper companies", "the myths". She positions her family's choices (homeschool, long nursing, early potty training, birth at home) as the natural way and the norm as something sold to parents.
- **Faith and gratitude** sit inside the everyday lines (God makes no mistakes, thank God), and she ends with 🤍.
- **First person plural for the family** ("we believe", "we are building a life we love"), with the husband as a co-star: he is central in 12 of the 22 top Reels and 3 of the 12 controls.

What her voice does not do: no jargon, no long proofs, no brand talk. The opinion is strong, the words are simple.

## 2. Hooks: what her breakouts open with

All counts from `data/coded.json` (my coding of the first 6 seconds of each Reel; `python3 src/coded_reels.py` prints them).

| Hook family | Top 22 | Controls 12 | How it looks |
|---|---|---|---|
| Judgement someone says to her, in quotes, answered by a fact on screen | 4 | 0 | "until when will you nurse him?" over a 33 month old nursing; "how will she gain weight if you only nurse?" with the birth weight on screen and then the same baby months later; "it can't be that your daughter poops in the toilet at six months" while she films it; "how did you potty train before 2?" over two toddlers in a pool |
| Same quoted question, ordinary answer | 0 | 3 | three homeschool questions ("what do they do all day?", "what do they learn?", "what does he miss in kindergarten?") over normal day footage |
| "When X" or "POV:" situation, one line | 6 | 2 | a holiday with a lost suitcase and the husband in her clothes; a booked holiday that hits a religious couple's rule; the son jealous of dad; the reservist dad's tough talk while the reality behind him is softer |
| A norm breaking or counterintuitive claim as the headline | 4 | 0 | "this is the most normal thing in the world" + a list of very not normal facts (born at home, 2 and still nursing, no daycare); a sentence against the school system; a list of what they will not do; why play fighting with dad is healthy, "⬇️ in the post" |
| Question then a turn | 2 | 0 | "you want your daughter to marry a real man?" then the turn: make sure her dad is one; "who would you be stuck on an island with?" over the husband improvising a knife |
| Time contrast or life story | 2 | 0 | 2018 and now, the same couple; a list of hard years, then 10 years later |
| Cute moment + one word reaction | 1 | 0 | the 1.5M Reel: a baby on the breast, one slang word and three emoji |
| News moment, reminder or meme | 3 | 0 | a joke line on a war news day; flowers before Shabbat as a reminder to husbands; a dance meme for homeschool on 1 September |
| Reply to a critic | 0 | 1 | a reply-to-comment sticker answered with sarcasm |
| Weak or none (English trend text, abstract praise, motivation over dance, show-and-tell, no text) | 0 | 6 | |

**What separates the top from the controls (my reading, small sample):**

- **The answer must be visible and must break a norm.** The quoted-judgement format won 4 times when the picture proved a surprising number (33 months, 2.45 kg, six months, before age 2). The same format answered with a regular day lost 3 times. The quote creates the tension; the number on screen pays it.
- **Text from frame one, 1 to 3 short lines.** 21 of the top Reels show text in the first frame and the last one by 1.5 s; 2 controls had none at all. The one "when" situation that stayed low ran about 20 words; the top ones are about 6 to 15.
- **Reveal in beats.** Her strongest Reels change the text card 2 or 3 times in the first 6 seconds: quoted question, then the surprising answer, then the twist (the potty Reel: the question, "night and day too", "this is what diaper companies don't want you to know").
- **One person's real moment, filmed raw.** Phone video, no studio, the family is in the frame. Faces, hands, a child doing the thing.
- **Short.** Median 19 s for the top, 25 s for the controls. The long argument goes in the caption, not in the video.
- **Music, not talk.** 13 of 22 top Reels use licensed music, 9 original sound, and only 3 contain speech (voiceover, talking in the moment, the husband's selfie message). She lets the text and the picture do the work.

**Comments follow provocation.** The norm-breaking claim Reel got 646 comments (2.9 per 1,000 plays, about 4 times her median); the first comment page is mostly people arguing with her. Debate lifts distribution but it also brings the ugly comments that sit under her religious couple Reel. That is a choice, not an accident: her hooks pick a side.

## 3. CTAs: how she asks for action

**Reels: mostly no ask.** 18 of 22 top Reels ask for nothing (one of them ends with advice, no action), so her reach does not come from asking. Where she does ask:

| CTA | Where | Result (her numbers) |
|---|---|---|
| Comment a keyword for a free thing ("comment tools" for 5 tools to read your baby) | caption + said at 41 s in the voiceover | 250 comments on 19,481 plays: 12.8 per 1,000, about 19 times her median 0.69; the first comment page is almost all the keyword |
| Comment a keyword for a location ("comment storm") | caption | 41 comments on 120,961 plays, many of them asking for the location in their own words |
| Comment a question and get a video about it ("what would you most like to understand? maybe the next video is your question") | end of caption | 23 comments on 51,146 plays |
| "⬇️ in the post" on screen, the list in the caption | first frame | 2 comments on 23,461 plays |
| Follow with a promise ("if you like seeing another way to build a family, follow us") | end of caption | only on controls (3 of 12) |

**Carousels: one ask on the last slide, a follow line in the caption.**

| CTA | Carousel | Likes / comments |
|---|---|---|
| Send to a specific person: "send to dad who loves being a dad so much" | child to dad, today and one day | 7,191 / 116 (164 reposts in `research/carousel-research/il_finalists.csv`) |
| Comment a keyword to join a Zoom meeting for men | wife's lines in speech bubbles, "she wants to be your wife, not your mom" | 725 / 21 |
| Save it for the next time you need it ("save this carousel for the moment you need one clear sentence") | mom's inner thoughts during a boundary | 336 / 13 |
| Message me the word "guidance" and I'll send the details | her life story, sells her paid guidance | 82 / 4 |
| Comment question + follow | abstract couple statements | 24 and 39 / 0 |

**What her CTAs teach:**

1. **The ask matches the job.** Keyword comments for leads (her freebie, her Zoom, her paid service); send-to-a-person for reach; save for a moment the reader will need it again. She never asks for all three at once.
2. **The keyword gets something concrete** (5 tools, a location, a Zoom). The comment count jumped only where the reward was clear.
3. **Send-to-a-person is the best one she has.** The sentence names who gets it and why they will love it. It turned a carousel into something people forward.
4. **The ask is said in her voice**, a short line with a heart, often promising what comes next ("maybe the next video is your question").
5. **Follow CTAs alone did nothing visible**; they sat on the low Reels.

## 4. Carousels: what changed and what wins

Since October 2026 she posts far fewer Reels (3 in October, 3 so far in November, against 15 to 37 a month in the six months before; `data/reels.json`), and 7 of the 9 newest feed items that are not pinned are carousels. The switch came after the 17 / 09 / 2026 carousel that got 7,191 likes; I am inferring the reason from the timing.

The look: warm illustrated pictures of the same couple and kids, big bold Hebrew on the picture, a small watermark, 7 to 12 slides.

**Winners open with a line a specific person says in a specific moment:** the child to dad ("dad, can you stay until I fall asleep?"), the wife's sentence in a speech bubble, the mom's thought while the child is still angry. **Losers open with an abstract statement or a general question** ("how will you know you are in a healthy relationship?", "a person who feels good with himself...", "how much more could our kids do if we let them try?"): 18 to 39 likes. The same split as her Reels: a person and a moment beat a topic.

The structure of the winner: each slide pairs "today" (the small child's ask) with "one day" (the grown child's ask), and the last slide turns to the reader and gives the send line. It is a reveal across slides, the same beats as her Reels.

## 5. How to make content like hers (step by step)

1. **Pick a norm your audience was told** and the moment that proves the other side. Write down the sentence people say about it (the doubt, the judgement, the question in the DMs).
2. **Put that sentence in quotes on the first frame**, 1 to 2 lines, up to 8 words a line, 2 emoji at most.
3. **Answer it with something the viewer can see**: a number on screen, the child doing it, the before and after. If the answer is "a regular day", pick another sentence.
4. **Reveal in 2 or 3 text beats** in the first 6 seconds: the quote, the surprising fact, the twist.
5. **Film one real moment on a phone**, 10 to 20 seconds, with the person in it. Music under it. Talk only if the talking is the moment.
6. **Put the argument in the caption**: short lines, a rhetorical question and its answer, three beats, one woman addressed as "you".
7. **One ask, matched to the job**: send to a person for reach, a keyword with a concrete reward for leads, save for a named future moment for usefulness. Leave the breakout candidates without an ask, as she does.
8. **For carousels, open with a person's line in a moment**, never a topic, and pay it off across slides (today and one day, the wrong sentence and the right one).

## 6. What LumeBook can take, and what not

**Take (fits our rules):**

- **Quoted doubt + visible answer** for Reels. Use a real sentence parents send us and answer it with what is on screen. This fits the reel script rules (a doubt then the turn, point at what is on screen, `.claude/skills/lumebook-hebrew-voice/references/reel-scripts.md`).
- **"When" situations of one line** for the grandmother and gift lanes.
- **Text from frame one, reveal in beats, under 20 seconds** for the posts meant to reach new people.
- **Keyword comment only with a concrete reward**, and judged by DMs and orders, not reach. Her numbers agree with the @matan.nistor finding that keyword Reels collect leads more than reach (`research/matan-nistor-reels/report.md`).
- **Child's line in a moment as the carousel opener.** This already matches our child voice carousels; her winner is more evidence for it.

**Do not take:**

- Her provocation against daycare and the school system, and her health claims (nursing and immunity, potty training from birth). They create debate for her because they are her identity; for a brand selling to all parents they are a risk, and the facts would need sources.
- War and religious couple humour, news moments, and the husband as a co-star: we have no couple, and these are her life, not a format.
- The "what diaper companies don't want you to know" line: it is the formula our voice rules ban outside a carousel cover ("מה שלא מספרים לך").

**Two places where her best result conflicts with our current rules (your call):**

1. Her biggest carousel is a child talking **to dad** with a **send to dad** CTA. Our carousel rule is mom or both parents, never dad alone, and the CTA is save for the next time. A both-parents version ("אמא, אבא, ...") with a send line would test the share mechanic without breaking the dad rule, but it changes the save CTA.
2. The "today and one day" structure puts the grown child's voice on some slides, which goes past the age 3 to 6 child narrator.

## 7. Example lines (passed `voice_lint.py`, need a real moment before use)

Reel, quoted doubt and the answer on screen (as LumeBook, never as a parent):

```text
״הוא בן שנתיים, הוא בכלל יבין שזה הוא?״
תסתכלו מה הוא עושה בעמוד 3
```

Reel, one line situation (grandmother lane):

```text
סבתא מגיעה עם ספר שהנכד הוא הגיבור שלו
```

Reel, situation:

```text
כשהיא מבקשת את אותו סיפור בפעם החמישית הערב
```

Reel, comment question that promises the next video:

```text
מה הכי קשה אצלכם בשעת השינה?
כתבו לנו, אולי הסרטון הבא יהיה בדיוק על זה
```

Carousel, child's line as the hook, and the current save CTA:

```text
אמא, אבא, עוד סיפור אחד?
```

```text
תשמרו את הפוסט
לפעם הבאה שהוא לא נרדם
```

## 8. Tests worth running

| Test | Change one thing | Measure |
|---|---|---|
| Quoted doubt vs topic hook (Reels) | the first frame only: a real parent's doubt in quotes vs our usual topic line, same footage | 3 second hold and plays against our monthly median |
| Send-to-a-person CTA (carousels) | last slide: "send to the mom who..." vs the save line | shares and reposts per 1,000 reach |
| Keyword with a reward (Reels) | caption: לומי + a named reward vs לומי alone | comments per 1,000 plays and DMs that turn into orders |

## Method and limits

- Collection: the Reels tab's own query from the signed-in built-in browser (50 pages, 591 items), then `/api/v1/media/<id>/info/` for the 34 selected Reels and the 9 carousels, first comment page for 11 Reels. Dates decoded from the media id. One read-only pass; Instagram's terms forbid automated collection without permission, so do not schedule it.
- Selection: the 22 Reels since 2024 with the most plays, and 12 controls spread over 2025 and 2026 with plays between 1,200 and 3,500 (her median since 2025 is 2,404).
- Coding: I read 4 frames from the first 5 seconds of every Reel (plus 18 frames for 8 of them) and every caption; the hook text is my reading of the frames. Whisper (turbo, Hebrew, greedy) ran only on the 12 Reels with original sound; 3 of those were song lyrics and are marked unusable.
- Her full feed (about 500 posts that are not Reels) could not be listed in this pass, so the carousel part rests on 9 carousels, of which one is a big hit. Treat it as weaker evidence than the Reel part.
- Play counts include Facebook plays when a Reel was cross-posted. Comments are the first page only, in Instagram's order.
- Her videos, frames and transcripts stay on this Mac in `media/projects/2026-11-11-adar-motherhood-reels/` (not in git). Never re-post them.
