# The LumeBook Pipeline Course: Curriculum

**Designed for:** Yarin Bruner
**Window:** 1 / 11 to 30 / 11 / 2026
**Built on:** `course/discovery.md`, approved 31 / 10 / 2026
**Status:** APPROVED by Yarin, 31 / 10 / 2026 ("Approve"). Building: the platform and Track 1 first (§14).

**Changed 31 / 10 / 2026, later that day.** Yarin: "i need it to be like a course and a way for you to check my answers, i want the course fully in english". So: (1) the course is in English (lessons, checklists, the platform's screens; Hebrew only where a lesson quotes literal text Yarin sees or types); this reverses discovery's "All Hebrew". (2) The platform opens on a Course tab: lessons in order by track, each on its own page, with a Continue button; tasks still show the lesson of their type (§4), but a lesson no longer waits for a task. (3) Claude grades the open quiz answer and the project hand-ins in the page, on the §10 scale (✓ correct, ~ partial, ✗ wrong, ↑ above the standard), honestly ("redo it"). Where Claude cannot run (the Vercel copy, the local server), Yarin grades themself as before.

---

## 0. What the discovery forces

The full record with Yarin's words is `course/discovery.md`. Six of its answers change the structure itself, not just the content:

| Answer | Structure it forces |
|---|---|
| The last book was never started; **no separate time** | The unit is not a day or a session. It is a **lesson attached to a task type**, opened from a real task (§4) |
| **More attributed sales first**; pay counts **only orders with Yarin's UTM tag** | The first track is the pay path: tag, DM, count. Everything else comes after it |
| The store's admin **does not show which link brought a sale** (`research/cro-crm/numbers-2026-10-25.md:65`), although the store's code sends the tag with every book started (`research/creator-content-conversion/report.md:514`) | Yarin cannot see the number they are paid on today: the data probably exists, but no screen shows it to them. Week 1 makes reading it a Yossi task, and the numbers screen shows "not available yet" until it is, rather than a guess |
| **Terminal and code off the table** | "Run it without Claude" means running every step through its screen and knowing what to ask when one breaks. The code stays Claude's |
| **Tasks by hand only**, platform replaces the work board, synced Mac and iPhone | The platform is a task manager first. Lessons wait in a queue per task type and appear when Yarin opens a task of that type |
| **All Hebrew**; four failure modes; checks = numbers, quizzes, exam | Lessons in plain Hebrew, at most 5 minutes, at most 3 new terms, a 3-question quiz each, one weekly numbers screen, one final exam |

---

## 1. What "excel" means here

### Tier 1: the vocabulary (a hazard, not a milestone)

Knowing what UTM, CRO and RTM stand for. Free to acquire and easy to mistake for skill. No lesson exists to produce it on its own.

### Tier 2: runs the LumeBook pipeline unsupervised. **The target.**

By 30 / 11, without Claude deciding for them, Yarin can:

1. **Make every sale they cause countable.** Tag every link, follow the pay path from comment to paid order, spot a leak and name who fixes it.
2. **Choose well.** Pick topics, hooks, live moments, creators and reels that move people toward a sale, and say why.
3. **Run the pipeline through its screens.** Take each step end to end, know what it is for, recognise when it is broken and what to ask for.
4. **Explain and defend it**, to Yossi or an interviewer, **including what the numbers cannot prove.**

Capability 4's last clause is the one the course is built around. With zero provable sales today, a tag that leaks and no per-link view in the store, Yarin meets it in week 1.

> **The standard:** every lesson serves one of these four, or it is cut.

### Tier 3: specialist (beyond November)

Running paid ads, building automations (an auto-DM, the event slot back in the batch), lifecycle flows across WhatsApp and email, incrementality tests, managing creators at scale. Named in the last lesson, not taught.

---

## 2. Competency map

**[C]** core · **[I]** important · **[S]** stretch, first to cut · **[X]** out

| Domain | | Sub-skills |
|---|---|---|
| A. The pay path and attribution | **[C]** | parts of a link · the five UTM tags · LumeBook's tag values (`research/cro-crm/measurement.md` §4) · the link maker · the tag leak (A21) · the cookie gate: tags are kept only for visitors who accept analytics cookies (`research/creator-content-conversion/report.md:515`) · who counts tagged orders · a creator's link is not Yarin's tag |
| B. CRM: comments and DMs | **[C]** | comment word → DM → click → book started → paid · reply speed · one reminder, not three · Yarin's voice · consent limits (`research/cro-crm/crm-flows.md` §7) · the store's WhatsApp flows, read only |
| C. Carousels through Carousel Machine | **[C]** | the monthly batch · choosing among a day's options · hooks as hypotheses (`carousel/carousel-pipeline/hook-bank.md:11`) · grading with a reason · the comment word and booklet CTA (`story-format.md` §7) · the Postiz block · the pre-post check |
| D. Real-time marketing | **[C]** | does the moment touch a buying moment · is it safe to touch · formats outside the batch · add, never replace, a scheduled post · tag it · compare it · Hanukkah as a planned moment |
| E. Meta analytics | **[C]** | Insights per post · saves, shares, comments over reach · subtracting Yarin's own like and save · what Insights does not show · why Meta's sale count differs from the store's |
| F. Reading numbers honestly | **[C]** | rates before counts · denominators · baseline against this week · samples too small to say anything · writing the "cannot prove" sentence |
| G. CRO | **[I]** | the store journey from book page to payment · where people drop · choosing the fix that moves tagged sales · writing the ask · the before number |
| H. GA4 | **[I]** | the three events it receives · its gap 19 / 08 to 20 / 09 · "Organic Social" that is mostly paid · what it can and cannot show of tagged purchases |
| I. Creators | **[I]** | the admission bar · the offer wording · the barter book · Hanukkah creator books (key date 10 / 11) · creator sales and Yarin's pay |
| J. Reels | **[I]** | the first seconds · what the reel editor gives back · trial reels and how to read them |
| K. Running it through screens | **[I]** | where each step lives · which screens are Mac only · the signs of a broken step · what to ask Claude for |
| L. Explaining and defending | **[C]** | the report to Yossi, decision first · the two-minute pipeline explanation for an interview |
| Parent communities | **[S]** | Not in Yarin's current week. Added only if it comes back |
| TikTok | **[S]** | Not connected in Postiz (Postiz memory note, 26 / 10) |
| Running paid ads, code, terminal | **[X]** | Discovery: no ad budget; code off the table |

---

## 3. Prerequisites, taught at first use

The technical base is zero (discovery §0), so four prerequisites are taught. Each is a lesson of its own, placed before the first lesson that needs it, never deferred to make something land sooner:

- **P1 · What a link carries** (L01). The parts of a web address and where tags sit in it. Needed before anything about UTMs.
- **P2 · Rates and denominators** (L04, then woven through every numbers lesson). The weak spot Yarin flagged, so it is not a module: it appears at the point of a real decision, with the platform showing its arithmetic.
- **P3 · What happens after the click** (L03). Book page, the book wizard, the preview, payment. Needed before DMs, CRO or any sales number makes sense.
- **P4 · The map of the pipeline** (L07). Every step, whose it is (Yarin's or Claude's), and which screen it lives on.

---

## 4. The unit: a lesson attached to a task

### Task types (fixed list)

| Type (in the platform) | What it covers | Where the work happens |
|---|---|---|
| Carousel | choosing, grading, approving, scheduling a carousel | Carousel Machine, **Mac only** (localhost) |
| Messages | answering comment words and DMs | Instagram, phone |
| Live moment | a post for a live moment | Instagram, phone or Mac |
| Reel | a reel or a set of trial reels | the reel editor via Claude, Instagram |
| Creators | finding, messaging, following up with creators | creator map, **Mac only** (localhost) |
| Numbers | the weekly numbers, Meta, GA4, the store admin | Instagram, Meta, GA4, store admin |
| Yossi | an ask to Yossi | WhatsApp or a meeting |
| Other | anything else | no lesson attached |

### How a lesson reaches Yarin

1. Yarin adds a task by hand and picks its type (one tap templates exist for recurring jobs, added only when Yarin taps them).
2. Opening the task shows its **checklist** and, if one is waiting, the **next lesson of that type** whose prerequisites are done.
3. The lesson is at most 5 minutes, then a 3-question quiz. Neither blocks the task: "done" works with the lesson unread.
4. A lesson that is not yet due waits. Missed days create no backlog, because lessons wait on task types, not dates.
5. A "lessons waiting" strip shows which types have a lesson ready, with a button to add a task of that type, so a type Yarin rarely touches cannot hide its lessons forever.

### Lesson anatomy (every lesson, same shape, so the builder can parse it)

| Part | Rule |
|---|---|
| Title | A question or an action, in English |
| Do this now | One line: what the lesson changes in this task |
| The teaching | At most 5 minutes of reading. Starts from something Yarin sees in the task, then names it. At most 3 new terms, each in the glossary |
| Example | A worked example from LumeBook (internal figures pointed to, never copied) |
| Common mistake | The misconception this lesson kills (§7) |
| What the numbers can't prove | The recurring marker, one or two lines in every lesson. It argues the course's central point by repetition, as `### Against the certificate` did in the GA4 book |
| Quiz | 3 questions from memory. Answers sealed until committed (warn and record, never lock) |

### Checklist fade, by count of tasks of that type

| Tasks of this type done | Checklist |
|---|---|
| 1 to 3 | Open, every step |
| 4 to 6 | Folded, one tap to open |
| 7 and on | Yarin writes their own steps first, then the checklist opens to compare |

Published in the platform so the fade is visible, and never reordered.

---

## 5. The sequence

Four tracks, ordered by what they unlock. **The single source of truth for order, type, prerequisites and target week is `course/lessons.json`**; this table restates it and the build fails if the two drift. Lesson numbers never change once shipped.

Target weeks: W1 = 1 to 7 / 11, W2 = 8 to 14 / 11, W3 = 15 to 21 / 11, W4 = 22 to 30 / 11. Every lesson of tracks 1 and 2 is due by 14 / 11, ahead of the Hanukkah order cutoff (22 / 11, unconfirmed in `shared/facts.json`).

### Track 1 · Every sale countable (W1)

| # | Lesson (working title) | Type | Part | Cap. | Min |
|---|---|---|---|---|---|
| L01 | What a link carries (P1) | Messages | Attribution | 1 | 4 |
| L02 | No tag, no pay: choosing your tag values, then making a tagged link | Messages | Attribution | 1 | 5 |
| L03 | After the click: from comment word to paid order (P3) | Messages | CRM | 1 | 5 |
| L04 | The weekly numbers: five numbers and where each lives (P2) | Numbers | Meta analytics | 1, 4 | 5 |
| L05 | Who can see your tagged orders today, and who cannot | Numbers | Attribution | 1, 4 | 4 |
| L06 | Writing an ask Yossi can act on (the per-link view, A21) | Yossi | CRO | 1, 4 | 5 |
| L07 | The map: every step of the pipeline, whose it is, which screen (P4) | Carousel | Running it | 3 | 5 |
| L08 | The check before a carousel goes out | Carousel | Running it | 3 | 4 |

### Track 2 · Choose what sells (W2)

| # | Lesson (working title) | Type | Part | Cap. | Min |
|---|---|---|---|---|---|
| L09 | Choosing among the day's options | Carousel | Carousels | 2 | 5 |
| L10 | What a hook does, and why every formula is still a guess | Carousel | Carousels | 2 | 5 |
| L11 | Grading with a reason the next batch can use | Carousel | Carousels | 2, 3 | 4 |
| L12 | Is this moment worth it: fit, safety, speed | Live moment | RTM | 2 | 5 |
| L13 | Making a moment post fast, outside the batch | Live moment | RTM | 2, 3 | 5 |
| L14 | Hanukkah: the moment you can plan | Live moment | RTM | 2 | 4 |
| L15 | Following up: speed, one reminder, and when to stop | Messages | CRM | 1, 2 | 4 |
| L16 | The first seconds of a reel | Reel | Reels | 2 | 5 |
| L17 | Trial reels: what they test and how to read them | Reel | Reels | 2, 4 | 4 |
| L18 | Which creator: the admission bar and why it exists | Creators | Creators | 2 | 4 |
| L19 | The offer, the message and the Hanukkah books | Creators | Creators | 2 | 5 |
| L20 | Creator sales and your pay | Creators | Creators | 1, 4 | 4 |

### Track 3 · Read the numbers honestly (W3)

| # | Lesson (working title) | Type | Part | Cap. | Min |
|---|---|---|---|---|---|
| L21 | Insights per post: what counts, what to subtract, what is missing | Numbers | Meta analytics | 4 | 5 |
| L22 | Meta's sales against the store's | Numbers | Meta analytics | 4 | 5 |
| L23 | GA4: what it receives, what it mislabels, what it can still show | Numbers | GA4 | 1, 4 | 5 |
| L24 | When the numbers are too small to say anything | Numbers | Reading numbers | 4 | 5 |
| L25 | The store journey and where people drop | Yossi | CRO | 1, 4 | 5 |
| L26 | Choosing the fix that moves your tagged sales | Yossi | CRO | 1, 2 | 4 |

### Track 4 · Run it and defend it (W4)

| # | Lesson (working title) | Type | Part | Cap. | Min |
|---|---|---|---|---|---|
| L27 | When a step breaks: the signs and what to ask for | Carousel | Running it | 3 | 5 |
| L28 | The monthly report: decision first, then what cannot be proven | Numbers | Explaining | 4 | 5 |
| L29 | The pipeline in two minutes, for an interview | Other | Explaining | 4 | 4 |
| L30 | December from November's numbers | Numbers | Choosing | 2 | 4 |

**Totals:** 30 lessons, about 2 hours 20 minutes of reading and about 1 hour of quizzes, spread over 30 days. Small on purpose: the job is the practice.

---

## 6. Project ladder: real work, fading help

Every project is real LumeBook work. None of them can be blocked by someone else: an ask to Yossi counts as done when it is sent, not when he answers.

| # | Target | Project | Help |
|---|---|---|---|
| P1 | W1 | Choose your tag values, then make every DM link this week with the link maker and log it | Full: exact steps |
| P2 | W1 | The first weekly numbers screen, with "not available yet" where it is true | Full: exact steps |
| P3 | W1 | Tell Yossi which tag values are yours, and ask for a way to see tagged orders and for the A21 fix | Partial: a template |
| P4 | W2 | One live-moment post: chosen, made, tagged, compared a week later | Partial: the checklist |
| P5 | W2 | The Hanukkah creator round by 10 / 11 | Light: the goal only |
| P6 | W3 | A weekly read with Meta against the store and a "cannot prove" paragraph | Light: the goal only |
| P7 | W3 | Ask Yossi for one CRO fix, with its before number | Light: the goal only |
| CAP | W4 | November's report to Yossi | None: one line, "what happened in November and what we do in December" |

The fade only goes down. It is never reordered.

---

## 7. Misconceptions the course kills

| # | The belief | Killed in |
|---|---|---|
| 1 | "The store records nothing about where a buyer came from" (its own admin says so): the code sends the tag with each book started, the admin just does not show it | L01, L05 |
| 2 | "If the sale happened, I get credit for it" | L02 |
| 3 | "A comment word is a sale" | L03 |
| 4 | "A tagged link stays tagged until the buyer pays" | L06 (A21) |
| 5 | "Views and likes are the result" | L04, L21 |
| 6 | "My own like and save are signal" | L21 |
| 7 | "Every trend is a moment for us" | L12 |
| 8 | "One post that did well proves the format works" | L17, L24 |
| 9 | "Meta's purchase count and the store's are the same thing" | L22 |
| 10 | "GA4's Organic Social is my organic posts" | L23 (`research/cro-crm/numbers-2026-10-25.md`, section 5) |
| 11 | "Creator sales pay me" | L20 |
| 12 | "The batch will handle the timely stuff" | L13 (no event slot since 24 / 10, `cloud-monthly-prompt.md`) |

---

## 8. Memorise against understand

**Memorise** (needed mid-conversation, with Yossi or an interviewer):
the five UTM tags and LumeBook's values for them · the pay rule · the five stages from comment word to paid order · the five weekly numbers and where each comes from · the house rules (לומיבוק, no AI in audience copy, a personal link never a code, no em dashes) · the Hanukkah dates in `shared/facts.json`.

**Understand** (tested on new situations, never by recall): everything else. If a fact is one tap away in the platform or the app, it is not worth memorising.

---

## 9. Countermeasures, held to

From `course/discovery.md` §2, now as mechanisms in the platform:

| Failure mode | Mechanism |
|---|---|
| Built it, never started | No sessions. Lessons open from tasks. The platform is where the work is managed, so opening it is not an extra step |
| Consistency | 5 minutes at most. Nothing blocks a task. No backlog from missed days. One fixed ritual a week (the numbers screen) |
| Jargon | Nothing named before Yarin meets it in the task. 3 new terms at most. A glossary entry at first use. Hebrew first, the loanword in brackets |
| Numbers | Every number shown with its denominator and the decision it changes. The platform does the arithmetic and shows the working |
| Open-ended tasks | Every type has a checklist with a published fade (§4). Every open project follows a worked example of the same shape |

If the course breaks one of these, that is a defect Yarin can report.

---

## 10. Checks

- **Lesson quiz:** 3 questions, from memory, two with set answers and one "why" in Yarin's own words. Answers sealed until committed; opening early is allowed and recorded. Fewer than 2 of 3 brings the lesson back on the next task of that type. From L08 on, one of the three is from an earlier lesson (spaced recall).
- **Weekly numbers screen:** every Sunday (Yarin, 31 / 10). Tagged clicks, DMs sent with a tagged link, comment words received, tagged orders (or "not available yet"), and the best post's saves and shares over reach, each against the week before. It cannot be saved without one sentence on what the numbers cannot prove.
- **Final exam, 27 to 29 / 11:** three parts, closed book.
  - A. Recall: 15 questions on the memorise list (§8).
  - B. The case (§11).
  - C. Explain the case to Yossi in 150 words, decision first.
  Pass: 75 of 100, no part below 60. Every question maps back to the lesson that teaches it, so a miss names what to reread.
- **Grading:** Claude grades the exam and any weekly read on request: ✓ correct, ~ partial, ✗ wrong, ↑ above the standard. Four checks in order: correct, sound reasoning, would it pass professionally, what the error reveals. Each pass ends with a straight verdict. Licence in writing: Yarin chose **"Honest, say redo"** (31 / 10), so a pass that does not meet the standard says "redo it".

---

## 11. The case and its trap

LumeBook is the live case for everything except the exam, and its internal figures stay in LumeBook's own files. The exam uses **one invented brand**, with a generated week of numbers that reconcile across its Insights, Meta, GA4 and store views (name checked so it is not a real business).

**The loud story:** a live-moment reel reached eight times the usual audience and the week's orders rose, so "the reel drove sales" is the obvious answer.

**The planted noise:** Meta claims more purchases than the store has; GA4's Organic Social includes ad clicks; the founder's own like and save are on every post.

**The real story underneath:** the rise came from the code-word DMs on one carousel plus ads the founder started that week. The reel brought no tagged clicks, and one reel could not prove anything either way.

**Grading:** 25 of 100 marks for naming the real drivers **and** saying what cannot be proven. That line scores **zero** if the answer credits the reel.

---

## 12. The platform, in one paragraph

It replaces the dashboard's canvas work board as the default view of the dashboard artifact (`sites/dashboard/`). The board's files move to `_to-delete/` under the project rule; the other dashboard views stay. It holds:

- the task list (add, type, done)
- the task sheet with its checklist, lesson and quiz
- a **link maker** that builds tagged links from the book list (`research/carousel-audit/data/books.json`) and the tag values Yarin chooses in L02 (starting from `research/cro-crm/measurement.md` §4), kept as an editable setting
- the weekly numbers screen
- the glossary, the exam, and a "lessons waiting" strip

State goes in the artifact database under its own prefix (never `boards/`, `snapshot`, `history` or `tracker`), which syncs Mac and iPhone. The public Vercel copy never exports it. Design rules:

- English, left to right inside the Hebrew dashboard (since 31 Oct 2026, see the note at the top), the design system's `lb-` components
- white only (since 05 Nov 2026)
- works at 390px wide
- on the phone, a Mac-only link says so instead of failing

---

## 13. If November slips: the cut order, decided now

| If behind by | What goes |
|---|---|
| Track 1 not done by 7 / 11 | L29 moves after November |
| Track 2 not done by 14 / 11 | L16 and L17 merge into one reel lesson |
| Track 3 not done by 21 / 11 | L25 and L26 merge; L30 folds into the November report |
| Still behind on 25 / 11 | The exam drops part A; B and C stay |

**Never cut:** L01 to L06 (the pay path), L24 (what cannot be proven), the exam's case.

---

## 14. Build order

1. The platform with Track 1 (L01 to L08), the link maker and the numbers screen, live by about 4 / 11.
2. Track 2 (L09 to L20) by about 10 / 11.
3. Tracks 3 and 4 and the exam by about 20 / 11.

Lessons are written in Hebrew under the project's Hebrew rules (`creators/creator-research/src/hebrew-rules.md`). Every claim about Instagram, Meta or GA4 is checked against its primary source when the lesson is written, not now.

---

## 15. Questions, answered 31 / 10 unless open

1. **Honest marking:** "Honest, say redo". Recorded in §10.
2. **Which tag values count as Yarin's:** Yarin's answer, **"i need to create/choose them"**. So choosing them is part of L02 and P1, starting from the values `research/cro-crm/measurement.md` §4 proposes, and P3 tells Yossi which values to count. The values must keep Yarin's own posts and DMs apart from creator links (`creator`) and ads (`paid-social`).
3. **Who counts the tagged orders, and how Yarin sees them:** open. The admin does not show which link brought a sale today (`research/cro-crm/numbers-2026-10-25.md:65`), though the store's code sends the tag with each book started (`research/creator-content-conversion/report.md:514`), so P3 asks Yossi to show the orders that carry Yarin's tag, not to start recording them. Until he answers, the numbers screen says "not available yet". (Corrected 31 / 10: an earlier draft said the store cannot record the link at all.)
4. **Weekly numbers day:** Sunday.
5. **Task types:** the list in §4 as it is; parent communities stay out.
