# The LumeBook Pipeline Course: Discovery Record

**Designed for:** Yarin Bruner
**Discovery:** 31 / 10 / 2026, 17 questions, one at a time
**Window:** 1 / 11 to 30 / 11 / 2026 (30 days)
**Status:** APPROVED by Yarin, 31 / 10 / 2026 ("Approve"). Next: the curriculum, `course/curriculum.md`.

Yarin's exact words are in **bold quotes** where they typed them; the rest were chosen options.

---

## 0. Profile and design consequences

| Dimension | Answer | Design consequence |
|---|---|---|
| What happened to the last book | **Never started it.** The LumeBook edition of the SMM book (14 days, 66,717 words) was built on 14 / 10 and scheduled for 15 to 28 / 10; `Google /SMM/book/answers.json` holds 0 answers and `pace-state.json` 0 confirmed days. The GA4 book holds 8 answers, all from Day 1 (24 / 08) | The most important answer in this record. A course that competes with the work for hours loses to the work. This one has no separate sessions at all (next row) |
| Time for learning | **None separate** | Every lesson is attached to a task Yarin is doing anyway and opens from that task. A lesson is at most 5 minutes of reading plus a 3-question check. No lesson exists unless a real task needs it |
| Goal | **"all of them"**: better judgement, run it without Claude, more attributed sales, proof for a next job | Four capabilities, all of them judged (§1), sequenced by the next row |
| First priority | **More attributed sales** | The first two weeks teach the steps closest to a sale. Judgement about topics and hooks is taught through those steps, not before them |
| Pay rule | Agreed with Yossi since 26 / 10: **only orders with Yarin's UTM tag count** toward their 25% | Tagging is the first lesson and a check on every task that posts a link. Two consequences, stated now: (a) under this rule, sales through a creator's personal link do not count toward Yarin's 25%, so creator time has to justify itself some other way, or the rule needs a question to Yossi; (b) the store keeps the tag in `sessionStorage` only (`research/cro-crm/audit.md` A21), so a buyer who closes the tab and comes back later loses it. That fix is Yossi's code: the course can make it a Yossi task, it cannot fix it |
| Sales provable today | **None** | The baseline is zero. The first number the platform tracks is tagged orders per week, read from the store admin |
| Technical base | Can do none of: run a terminal command, work a Meta export in a spreadsheet, make and check a UTM link, read a Python script | Everything is taught from zero inside the platform. Making and checking a tagged link comes in week 1 because pay depends on it. The numbers lessons have Yarin type a few numbers into the platform, which does the arithmetic and shows it, so no spreadsheet is a prerequisite |
| Off the table | **Terminal and code** | "Run it without Claude" is redefined for November: run every step through the apps' own screens, know what each step is for, recognise when one is broken and know what to ask for. The code layer stays with Claude. Full independence from Claude is not reachable by 30 / 11 with code excluded, and the course says so instead of pretending |
| Weak spots | All four still hold: consistency, jargon, numbers, open-ended tasks | One structural countermeasure each, §2 |
| Where lessons appear | **"i need a platform to manage my tasks and learn there as well"** | One platform: a task manager in which each task carries its lesson, quiz and checklist |
| Where it lives | **"replace the work board, i dont need it anymore"** | It becomes the dashboard's default view. The canvas board's files move to `_to-delete/` under the project rule; the other dashboard views stay |
| Device | Mac and iPhone, synced | The claude.ai dashboard artifact and its database, which already syncs between devices. 390px phone width is a hard requirement. Files that live only on the Mac are not reachable from the phone, so no lesson depends on them |
| Who adds tasks | **Yarin, by hand**, only | Nothing is added automatically by the pipeline or a schedule. Each task gets a type from a short fixed list (for example carousel, creator, reel, numbers, Yossi), and the type decides which lesson attaches. Recurring jobs get one-tap templates that Yarin chooses to add |
| Deadline | **End of November** (30 / 11 / 2026) | 30 days. The Hanukkah order cutoff (22 / 11, still marked unconfirmed in `shared/facts.json`) falls inside the window, so every sales lesson must be live by about 15 / 11 |
| Checks | Real numbers weekly, short quizzes, a final exam. **Not chosen:** decide first, then see | A weekly numbers screen (tagged clicks, DMs, tagged orders, against the week before). A 3-question quiz after each lesson with answers sealed until committed. One final exam in the last days of November. No forced "commit your call before the task" gate |
| Language | **All Hebrew**, platform and lessons. **Reversed 31 / 10 / 2026, later that day:** Yarin asked for "the course fully in english" (see `course/curriculum.md`, the note under Status) | Lessons in plain everyday Hebrew under the project's Hebrew rules (`creators/creator-research/src/hebrew-rules.md`), no em dashes. Loanwords Yarin already uses (UTM, UGC) stay loanwords. This record and the curriculum stay in English for approval unless Yarin asks otherwise |
| Budget | **Small tool budget, no ads** | No lesson needs ad spend. A paid tool is suggested only where no free path exists, with its price checked at the time |
| Internal sales figures | Carried forward from 14 / 10: point to them, never copy them | Lessons never contain LumeBook's sales numbers. Numbers Yarin types into the platform stay in the artifact database, and the public Vercel copy of the dashboard must not export them, as `boards/` is excluded today |
| On camera, Yossi | Neither ruled out | Reel lessons may offer Yarin's own voice or face as an option, never a requirement. Yossi tasks (the tag fix, a sales-per-link view) are allowed |
| Named parts | Asked after the playback: **"is rtm, cro, ga4 and meta analytics included?"**, then **"yes"** to adding them, then **"rtm is real time marketing"** | Real-time marketing, Meta analytics, CRO and GA4 are named parts, each scoped to what Yarin controls. CRM came in from my misreading of "rtm"; Yarin chose **"Keep CRM"** as a fifth part, since following up DMs with a tagged link is the step closest to a sale. See §1, "Named parts" |

## 1. What "excel" means: four capabilities (draft, confirmed in the curriculum)

By 30 / 11, unsupervised, Yarin can:

1. **Make every sale they cause countable.** Tag every link, read tagged orders each week, spot a leak and name who fixes it.
2. **Choose well.** Pick topics, hooks, creators and posts that move people toward a sale, and say why.
3. **Run the pipeline through its screens.** Take each step end to end, know what it is for, recognise when it is broken and what to ask for.
4. **Explain and defend it.** Show the system and its numbers to Yossi or an interviewer, including what the numbers cannot prove.

The one the course is built around, because it is the hardest to fake: **saying what the numbers cannot prove.** With zero provable sales today and a tag that leaks, Yarin will meet it every week.

> Every lesson serves one of these four, or it is cut.

### Named parts (Yarin, 31 / 10)

Four parts Yarin asked for by name, plus CRM (see §0). Each is scoped to what Yarin controls, since code is off the table and the store is Yossi's.

| Part | What Yarin does in it | What stays out | Serves |
|---|---|---|---|
| **Real-time marketing** | Spot a live moment (a holiday, a change of season, a trending format or sound), decide fast whether it fits LumeBook and is safe to touch, make it in a format that does not wait for the monthly carousel batch (a trend reel, a story, an extra post), tag its link, and compare it with the scheduled posts | Changing the carousel pipeline (code). The batch dropped its Israeli event slot on 24 / 10 (`carousel/carousel-pipeline/cloud-monthly-prompt.md`), so whether to ask for it back is a decision the course prepares Yarin to make, not something it builds | 1, 2, 4 |
| **Meta analytics** | Read Instagram Insights per post (saves, shares, comments, code-word DMs) and enter them on the weekly numbers screen. Read Yossi's Meta ad numbers, and say why Meta's sale count differs from the store's | Running or changing ads (no ad budget) | 1, 2, 4 |
| **CRO** | Choose which store fixes to ask Yossi for, ask, then check whether they moved tagged sales. Of the 49 actions in `research/cro-crm/src/journey-actions.json`, 38 are Yossi's alone, 5 shared, 2 Yarin's alone. First up: the tag leak, A21 | Changing the store or its code | 1, 4 |
| **CRM** (kept by Yarin) | Follow up code-word DMs with a tagged link, since nothing sends those automatically today | Running the store's WhatsApp reminders (Yossi's); Yarin reads their results only | 1, 2 |
| **GA4** | Know what LumeBook's GA4 can and cannot show, and why pay is read from the store admin. It receives only `page_view`, `user_identify` and `purchase` (`research/cro-crm/measurement.md`), and more than half of its "Organic Social" visits are paid Meta ad clicks (`research/cro-crm/numbers-2026-10-25.md`) | Setting up or fixing tracking (code). The tool in depth lives in the separate GA4 book | 1, 4 |

## 2. Countermeasures for the failure modes

| They said | The course's answer |
|---|---|
| Built it, never started | No separate sessions. A lesson opens only from a task. Progress counts real tasks done, so doing the job is doing the course |
| Consistency | No lesson over 5 minutes. A lesson never blocks a task. Missed days leave no backlog, because lessons wait on task types, not dates. The weekly numbers screen is the only fixed ritual |
| Jargon | Nothing named before Yarin meets it in a real task. At most 3 new terms a lesson, each in the glossary at first use. Hebrew first, loanword in brackets |
| Numbers | Rates before counts. Every number shown with its denominator and the decision it changes. The platform does the arithmetic and shows its working |
| Open-ended tasks | Every task type has a fixed checklist. The help fades on a published schedule: week 1 the full checklist is open, by week 4 the task starts blank and the checklist is one tap away |

## 3. Carried forward, not re-asked

- From `Google /SMM/SMM-Discovery.md` and its 14 / 10 re-discovery: the internal-figures rule, Instagram first, LumeBook's house rules (לומיבוק, no AI in audience copy, a personal link never a code, no em dashes).
- The SMM book's LumeBook edition (`Google /SMM/book/parts/`) is mined for lesson material instead of being written again.

## 4. Scale, honestly

- **Platform:** the dashboard's board view replaced by tasks, lessons, quizzes, the weekly numbers screen and the exam. The largest build in this project.
- **Lessons:** an estimated 25 to 35 short Hebrew lessons across about 8 task types, each with a 3-question quiz, plus one final exam. About 2 to 3 hours of reading spread over 30 days. Far smaller than the GA4 book's 239 hours, on purpose: the job is the practice.
- **Phases:** (1) this record approved, (2) the curriculum: capabilities, task types, lesson list and order, countermeasures, assessment, approved, (3) the platform with the week-1 lessons, live as early as possible, (4) the remaining lessons, (5) running it: weekly numbers and the final exam.

## 5. Open questions carried into the curriculum

1. Which task types Yarin actually has. The curriculum proposes a list from the repo; Yarin corrects it.
2. Whether creator sales that Yarin brought in should count toward their 25%. A question for Yossi, not for the course.
3. Who reads tagged orders out of the store admin, and how often the admin can show them.
