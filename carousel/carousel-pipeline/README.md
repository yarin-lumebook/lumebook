# Carousel Machine · the LumeBook nightly carousel pipeline

Named Hook Studio on 10 Oct 2026, renamed Carousel Machine on 22 Oct 2026 (Yarin: "change hook studio name to carousel machine"). The work goes in this order: the hook (the loudest true cover the topic allows), the content (every slide worth the swipe on its own), the slide design (very large type, one highlighted phrase per slide). Sources and rotation are guardrails. The folder, the skill, the scheduled task, the cloud routine, the login item (`hook_studio_login.py`, `com.yarinbruner.hook-studio`), the `/hook-studio/` path and `hook-studio.html` keep their old names.

Every night at 22:00 Claude prepares six complete Hebrew carousel options on one topic for the next morning. No picture is made until Yarin picks an option. Since 03 Nov 2026 the pictures come from the OpenAI Images API only (fal.ai and ChatGPT in Chrome are retired), and nothing is generated without Yarin's budget and yes (see "Pictures from the OpenAI API" below).

```
nightly or monthly run (free)       Yarin                        after picking (free since 30 Oct 2026)
topic + research + 6 options  ──▶   Carousel Machine: read,    ──▶  pictures from the GPT API, approval,
validated, review.html/md           edit, pick e.g. kid-2           Hebrew overlay, 1080x1350 PNGs, ZIP
```

The Claude side is the project skill `.claude/skills/lumebook-carousel` (both modes) plus the voice skill `.claude/skills/lumebook-hebrew-voice`. This README is the manual for people.

## Folder map

```
carousel/carousel-pipeline/
  README.md               this manual
  pack.schema.json        structure of a nightly pack (2 directions x 3 options x 7 slides)
  reco.schema.json        structure of the daily games and books carousel (recommendations.md has the rules)
  recommendations.md      the games and books carousel: stage, Israeli popularity evidence, slides, images, rotation
  reco-history.json       which stages, skills, products and hook structures the recommendation carousels used
  topic-bank.md           topics with ids, season months, code word ideas, books to check
  hook-bank.md            hook formulas with evidence labels and review dates, formula cards, the hook slate method,
                          rotation rules, slide 2 moves and per-slide re-hook moves
  hook-results.json       LumeBook's own results per published carousel (the only route to "lumebook_validated")
  research/               hook-strategy-2026-10-08.md (the research behind the bank) and notes/
  names.md                Israeli girl and boy names the carousels may use
  pillars.md              the two content pillars (kid, expert): colours, fonts, slide layout, photo direction
  history.json            what ran when: topic, hook families, code words, hooks, selected option
  voice-profile.md        voice rules, calibration status, where samples go
  drafts/DATE/            pack.json, review.html, review.md (+ versions/vN/ backups of reruns),
                          reco-carousel.json, reco.html, reco-assets/, reco/ (rendered slides); nights up to
                          13 Oct 2026: games-carousel.json, books-carousel.json, games/ and books/
  approved/DATE-OPTION/   one production run: approved.json, jobs.json, state.json, APPROVAL.md,
                          generated-assets/, real-assets/, final/
  grades.json             Yarin's 1 to 5 grades and reasons from the Carousel Machine grading page (the next batch reads them)
  productions.json        what Carousel Machine is producing or has produced, per carousel (written by producer.py)
  scripts/                all the tools (standard library Python, plus Google Chrome for rendering)
  assets/                 fonts (Heebo, Assistant, Rubik, SIL OFL) and the logo (off by default on slides)
  tests/                  unit tests and the valid pack fixture
  voice-eval-workspace/   skill-creator evaluation of the voice skill (benchmark + review.html)
```

DATE is the morning the pack is for. A run at 22:00 on the 7th writes `drafts/<the 8th>/`.

## Carousel Machine, the app (since 16 Oct 2026)

Yarin, 16 Oct 2026: "i want the entire carousel engine, editor and producer to be viewed in one place i can easily access no need of talking to you each time", one by one grading with reasons "so you can learn for next weeks batch", picking what to produce "from the tool itself", and "design it better using heebo as the main font, better hierarchy and apple design principles".

**Always on at http://localhost:8777/** (Yarin, 16 Oct 2026: "set Carousel Machine to start at login on port 8777 so I can bookmark it"): the login item `com.yarinbruner.hook-studio` starts `review_server.py --port 8777` at login and again if it stops (`scripts/hook_studio_login.py install|restart|status|uninstall`, log `~/Library/Logs/HookStudio.log`). The server imports its scripts once, so after editing any Carousel Machine script run `python3 carousel/carousel-pipeline/scripts/hook_studio_login.py restart`. Sessions attach with the preview config `hook-studio` instead of starting a second copy; two copies would both write grades.json and productions.json. `carousel-review-editor` still starts one by hand when the login item is off. **One page, no subpages** (Yarin, 17 Oct 2026: "why cant i edit them directly from the local host?" and "i want one page for everything without any subpages"). `scripts/studio.py` builds it. Since 24 Oct 2026 (Yarin: "a grid that shows the first slide of each carousel and only when i click on it the carousel exapnds", and "the side panel to view what carousels i chose to produce with a button to batch produce them"):

- **The grid:** slide 1 of every carousel of the batch, grouped by topic (the final slide 1 once a production is done, otherwise the cover text in the pillar look), each with its grade, production state and a "+ להפקה" button that picks it. Views: הכול, לדירוג, הפקה, לאישור (in the sidebar since 8 Nov 2026). The batch menu at the foot of the sidebar switches to an older batch. A click opens the carousel in a sheet over the grid (הקודם, הבא, סגירה or Esc; leaving saves first) with the editor and, beside it, the grade and production panel
- **The page, since 8 Nov 2026** (Yarin: "i want the carousel machine to have the same design treatment as the creator map and the reel calendar"): the same shell as those two pages. A page sidebar on the right (glass, `lb-sidebar`) with the views and their counts (כל הקרוסלות, לדירוג, הפקה, מחכות לאישור), the batch's posting days (a click scrolls to that day; days outside the search are dimmed), the batch menu and the cloud buttons; a sticky glass top bar (`lb-topbar lb-edge`) with the view's title, the grading meter, one search (cover, topic, child, option, structure) and "מחכות לאישור"; each day a glass card (`lb-glass-card`); the picks panel a glass panel on the left. On a phone the sidebar is a drawer (תפריט) and the picks open from להפקה. The page scrolls as one, with no scrollbar anywhere.
- **Side panel, נבחרו להפקה:** the picked carousels not yet produced (× takes one off), "להפיק את כולן" (since 03 Nov 2026 it says that a budget and a yes are asked before any picture is made), then the ones in production or done, waiting for approval first. A click opens that carousel. The batch button skips a pick that already has a production (re-export stays in that carousel's own panel). On a phone it is a drawer from the "להפקה" button
- **In the sheet, the carousel:** the slides with every headline, body and highlight editable in place, the caption and the CTA (kid and expert); the rendered slides plus their text fields and the caption (games and books). "שמירה" or Cmd+S saves through the editors' own save (backup to versions/vN, voice log, validation, rebuilt review pages; games and books slides are re-rendered); moving to another carousel saves first. Problems the validator finds show under the save bar
- **In the sheet, beside it, grade and production:** 1 to 5, the reason, the "להפקה" switch (all saved on change to grades.json), and the carousel's production: "להפיק עכשיו" (freezes the text for free, then stops at "מחכה לתקציב ולאישור שלך": the estimated tokens and cost, a budget to type and "אני מאשר, ליצור"; the same again for a story's other slides and for every another-take), the picture to approve or redo with a note (2 at most), then the slides, contact sheet, RTL check and ZIP by themselves; games and books export at once with no cost. ZIP, Finder, re-export after a text edit. producer.py, productions.json
- **Top bar:** the view's title, progress, the search, "מחכות לאישור"; at the foot of the sidebar "שליחת הדירוגים לענן" (commits grades.json alone and pushes main, so the next batch reads it) and the cloud check (cloud_sync.py without a restart)
- Keys in the sheet: arrows, 1 to 5, P, W, Cmd+S, Esc closes. The old addresses (/pool/ID, /grade/ID, /productions, /packs) open the page; the older pack editors (drafts/DATE/review.html) still work by address

Learning: `scripts/grades.py brief` turns grades.json into the summary the weekly cloud run reads before it writes (cloud-weekly-prompt.md, step 0.3). Grades are taste, not results: only hook-results.json can move a hook formula.

## 0 · The monthly batch (since 29 Oct 2026; the weekly batch below is history)

Yarin, 29 Oct 2026: "i need a monthly batch from now on (the morning of the last day of every month)"; size chosen: one pack per posting day. Cloud routine "Carousel Machine monthly batch (cloud)" (trig_013C3V1RxF3M38utouVepaVC), cron `0 4 28-31 * *` UTC (06:00 or 07:00 Israel); `cloud-monthly-prompt.md` step 00 stops the run unless tomorrow is day 1 in Israel. `nightly.py week-plan --monthly` plans the next month: every other day, Saturday moved to Sunday (13 to 15 packs, two topics each); a topic may return after 4 packs (batch.py `posting_dates`, `pick_pairs(monthly=True)`; batch-check accepts it). First run Sat 31 Oct 2026, covering 1 to 29 Nov. It reads `main`, so the code must be pushed first (the nightly commit does it). Pause it by switching the routine off.

## 0b · The weekly batch (since 16 Oct 2026, off since 29 Oct)

**Since 24 Oct 2026 (Yarin, after the carousel audit in `research/carousel-audit/`): two topics a day, child voice only, and the save and share CTA.** "Keep the child-voice numbered lists, on 2 topics that have a best-selling book (6 versions for each day (3 options for each) so i can choose the strongest one)", "change the cta to save the post and share to a parent who would agree", one carousel posted a day, and "do it" on the contrast fix. Packs from `lib.DAILY_PAIR_FROM` (2026-10-24 18:00) have `format: "two_topics"`: `topics` holds the day's two topics, `topic` repeats the first, and one `kid` direction holds kid-1 to kid-3 (topics[0]) and kid-4 to kid-6 (topics[1]), each with `topic_id`; the hook slate has keys `a` and `b`. `week-plan` (`batch.make_pair_plan`) gives each of the 7 days two topics of two different books from topic-bank.md "Best-selling books" (in season first, then the longest since last use; no topic twice in the week, no book more than twice, none from the previous 3 packs) and no event slot. Slide 10's headline is always `אפשר לעזור להם גם בסיפור אישי` (`lib.STORY_LINE`; Yarin: "change the cta to אפשר לעזור להם גם בסיפור אישי"). The CTA under it has no comment word: `תשמרי את הפוסט` / `ותשלחי לאמא שתתחבר` or `תשמרו את הפוסט` / `ותשלחו לאמא שתתחבר` (`lib.SAVE_SHARE_FORMS`), and a comment or link request anywhere is a second CTA. Every option must be in the child's voice (an ERROR now). Half the options are about a girl and half about a boy, and each topic has at least one of each (Yarin, 24 Oct 2026: "make sure the carousel machine do 50/50 boys and girls"): `nightly.py start` prints `child_gender_per_option` (`lib.gender_slots`: alternating, the first option flipping day to day so kid-1 is not always a girl), and `nightly.py finish` and `validate_pack.py` reject a pack generated from `lib.GENDER_BALANCE_FROM` (2026-10-24 21:00) that is not 3 and 3 (`lib.gender_balance_issues`; it does not block producing an option). Carousel Machine shows each day as its two topics side by side, three options each. The validator keeps the older rules for older packs. The week of 25 to 31 Oct 2026 (batch 2026-10-25, written that morning in the old shape) was switched to the new last slide on 24 Oct (Yarin: "switch this week's 42 carousels to the new last slide"): its packs carry `cta_style: "save_share"` (`lib.save_share_applies`), so the CTA rules are the new ones while the one topic and the kid and expert directions stay; each pack's version before the switch is in its `versions/v1`. A complete passing pack: `tests/fixtures/two_topic_pack.json`; tests: `tests/test_two_topics.py`. The notes below describe the batches up to then.

**The book link CTA over the booklet (Yarin, 30 Oct 2026).** After the Lotem CTA study: the last slide asks `אפשר גם לעזור להם עם <problem> בעזרת ספר מותאם אישית.` / `תכתבו "<word>" ואשלח לכם קישור להכנת הספר`, over an open booklet (GPT API pictures: the child in the topic on the left page, Claude's page text on the right, a realistic photo of the child in a circle on the corner, a yellow arrow at each face). Rules, sizes and the production steps: `story-format.md` section 7. `cta_style: "book_link"` on a pack or on one option; `lib.book_link_cta`, `lib.book_link_slide`, `lib.book_link_cta_issues`, `lib.booklet_issues`, `compose_slides.booklet_html`, `scripts/booklet_cta.py` (moves a produced carousel and re-exports its last slide). The 14 produced November carousels (packs 2026-11-30 to 2026-12-06) were moved that evening from `booklets-2026-11.json`; their earlier last slides are in each run's `versions/booklet-N/`. The carousels queued in Postiz were replaced with the booklet versions on 31 Oct 2026 (see below).

**Disclaimers, the 3D booklet and the Facebook post (Yarin, 31 Oct 2026).** Every slide from slide 2 carries the medical disclaimer at its foot and every written caption ends with the short one (`lib.SLIDE_DISCLAIMER`, `lib.CAPTION_DISCLAIMER`, added at export). The booklet is drawn in 3D from the same picture (`compose_slides.booklet_geometry`). Facebook gets its own converting post, `RUN_DIR/facebook/facebook.txt`, ending with the UTM site link, over slide 1 with its text, editable in Carousel Machine's preview; `postiz_export.py --replace` swaps a queued post for the new one (only with Yarin's OK). Rules: `story-format.md` section 8. The 14 November carousels were re-exported that day; their previous final/ is in each run's `versions/pre-3d-booklet/`. The same day Yarin's morning copy edits from Carousel Machine (7 of those runs, kept as written; previous approved.json and final/ in `versions/morning-edits-31oct/`) were applied and re-exported, and all 14 queued Postiz posts were replaced at their old times (`postiz_export.py --replace`).

**The child tells the parents and the posting rhythm (Yarin, 28 Oct 2026).** Every kid option is the child talking to mom or both parents: slides 1 to 9 and the caption in first person with direct asks, no narrator and no third person about the child, slide 9 closes in the child's voice, the CTA slide keeps its save for later wording (`lib.to_parents_issues`, packs from `lib.TO_PARENTS_FROM` or `voice_style: to_parents`). Posting: one carousel every other day at 06:00 from Friday 30 Oct, a Saturday slot moves to Sunday and the count restarts (`postiz_export.py --slots N` prints them, sends nothing); a post already uploaded to Postiz is never scheduled again. The produced carousels 27 to 31 Oct got the new text on their existing pictures (`compose_slides.py`, no new images, the earlier export is in each run's `versions/vN`).

**Save for later, the evening of 24 Oct 2026 (Yarin: "remove אפשר לעזור להם גם בסיפור אישי from the cta" and "i want the cta to change, 'תשמרו את הפוסט לפעם הבאה שX'").** Slide 10 is only the CTA: its headline is the save line (`תשמרי את הפוסט`, both parents `תשמרו את הפוסט`), which `compose_slides.py` draws as the yellow button with the save icon, and its body is the topic's everyday situation, always about the child (Yarin, same evening: "too specific", "doesnt sound natural", "always refer to the kid"): הוא or היא as the option's child, up to 5 words, one line per topic and gender (`לפעם הבאה שהיא מפחדת מרעמים`, `לפעם הבאה שיש לו יום הולדת`). `lib.save_later_topic_issues` and `KID_REF` check it. `lib.SAVE_LATER_FORMS`, `lib.save_later_slide` (breaks after לפעם הבאה), `lib.save_later_cta_issues`; packs from `lib.SAVE_LATER_FROM` (2026-10-24 21:00) and packs with `cta_style: save_for_later` (the week of 25 to 31 Oct, moved that evening, one line per topic; each pack's earlier version is in its `versions/`). Editing the CTA in Carousel Machine rebuilds slide 10; its headline and body are not edited on their own. The caption keeps its bridge line. The same evening punctuation came back except dashes, semicolons and hyphens (section 6).

**Readable type (24 Oct 2026):** the picture prompt asks for a light warm text zone (`lib.text_zone_sentence`), and `compose_slides.py` measures the WCAG contrast of each text block against the picture behind it (15th percentile of the pixels): under 4.5:1 the body takes the headline's darker ink, then the slide turns light on dark if that reads better, and only then a soft panel of the wall colour goes behind the copy. `rtl-report.json` records `contrast`, `contrastAfter` and `contrastFix` per slide. On the posted clock change slides (2.7:1) it adds the panel, on the pacifier slides (3.1:1) the darker body alone reaches 4.6:1, and cream walls (about 7:1) stay untouched.

**Yarin, 18 Oct 2026: "i dont want the games and books carousels anymore". No new games and books carousels: `reco_lib.ACTIVE = False`, so `week-plan` plans none, `nightly.py start` prints no `recommendations`, and no run writes `reco-carousel*.json` or runs finish-reco. The ones already made still show in Carousel Machine, validate, render and export.** The notes below on carousels describe the batches made up to then.

Yarin, 16 Oct 2026: "lets move to a weekly batch, 14 games and books carousels, 42 kid and expert, every thursday night", "one pool for the week, dont repeat the same topic twice", about 10 to 20 percent on things that happen in Israel, and in the games and books carousels "mix their order instead of games and then books".

- **When:** the cloud routine "Hook Studio weekly batch (cloud)" (its name from before the rename) runs every Thursday at 19:00 UTC (22:00 Israel summer time, 21:00 winter) and follows `cloud-weekly-prompt.md`. Its environment needs network access set to Full (section 9)
- **What:** `nightly.py week-plan` plans 7 packs on 7 different topics, each a normal `drafts/DATE` folder with the six kid and expert options and two games and books carousels (`reco-carousel.json`, `reco-carousel-2.json`, format `mixed2` for the second): 42 options and 14 carousels. The dates are only keys, in a row after the newest night; the plan is `drafts/batches/ID.json` (ID = its first date)
- **Israeli events:** slot 1 is the event pack (topic-bank.md "Israeli events"): one holiday, special day, or hard or exciting moment in Israel within two weeks, sourced that day, topic id `event-...` with `topic.event`; its two carousels record the same event. That is 6 of 42 options and 2 of 14 carousels, about 14 percent. No event that fits: the slot uses its fallback topic
- **No repeats:** six topics come from the bank (none of the last 14 packs; the bank has 30 rows since 16 Oct 2026, enough for 7 a week), the 14 carousels get skills spread so none repeats within four packs, and `nightly.py batch-check ID` rejects a topic or a product used twice in the batch
- **Delivery:** the run pushes `batch/ID` after every pack, so a run that stops halfway still delivers. Opening Carousel Machine pulls the new packs (section 9) and opens the pool page, `/pool/ID`: every topic with its six options and two carousels, no days. Each pack page links back to it ("מאגר השבוע")
- **Safe to run twice (24 Oct 2026):** the 22 Oct run called `week-plan` twice, got a second plan for the week after, was refused moving it aside, and stopped with only the plan pushed (batch 2026-10-25 had no packs). `week-plan` now returns a plan made the same day that has no packs yet instead of making another (`batch.unbuilt_plan_from`), and step 0.2 of the prompt says to run it once and never stop over a stray plan file. Carousel Machine lists only weeks with packs, so a week whose run stopped early does not show at all
- **Order in the games and books carousels:** mixed, never 3 of the same kind in a row (carousels made before 16 Oct 2026 keep every game first)

## 1 · The nightly run (up to 15 Oct 2026)

Scheduled task `lumebook-nightly-carousel` in Claude Desktop (Code, Routines), daily at 22:00 local time (Asia/Jerusalem), working folder `/Users/yarinbruner/Claude/Projects/Lumebook`.

- Claude Desktop must be open and the Mac awake at 22:00. If the app is closed, the run starts the next time it opens; a run after midnight and before 06:00 still targets the same morning
- It never calls the OpenAI API or anything else that is paid
- When it finishes, the session ends with the path to `review.html`

What it does: `nightly.py start` (folder, backup, rotation context) → choose a topic → check product facts on lumebook.com → read sources → write the hook slate (12 scored candidates) → write the six options in `pack.json` → `nightly.py finish` (validate, review files, history). If validation fails it rewrites the failing lines and tries again.

Run it by hand any time:

```bash
python3 carousel/carousel-pipeline/scripts/nightly.py start
```

then ask Claude: "use the lumebook-carousel skill in nightly review mode".

**Off since 18 Oct 2026 (see section 0).** Up to then every run also wrote one extra carousel of games and books together (Yarin, 14 Oct 2026: "combine the book and games to one carousel. 10-20 slides", then "cap it to 7-9 books and games"): `reco-carousel.json`, a random 7 to 9 suggestions (the LumeBook book counts as one; 10 to 12 slides), at least 3 real games and at least 3 real books for the same one developmental stage, games and books mixed in order (since 16 Oct 2026, never 3 of the same kind in a row), each popular in Israel with Israel-specific evidence, a real product image in the middle of each recommendation slide with a small משחק or ספר word above the title, plain dark plum Heebo text with no colour blocks except on the close slide (Yarin, 14 Oct 2026), and the LumeBook book as the second to last suggestion (its slide shows the cover of the catalogue book whose idea its line states, flat in a white card like the other books since 14 Oct 2026). It follows Carousel Machine too: `X משחקים וספרים לגילאי A-B ש...` with a value ending, a `highlight` on slides 1 and 2, the bold look, and the wordings considered in `hook_alternatives`. It has its own page, `reco.html`, one tab away from `review.html` (the slides scroll sideways on a phone), with the sources, popularity evidence, availability and image rights in dropdowns, and editable there. No image generation, no paid call, nothing posted. Nights up to 13 Oct 2026 have two separate carousels instead (`games-carousel.json`, `books-carousel.json`, 3 to 7 suggestions each, pages `games.html` and `books.html`); they still validate and render. Rules: `recommendations.md`. Check it by hand:

```bash
python3 carousel/carousel-pipeline/scripts/nightly.py finish-reco carousel/carousel-pipeline/drafts/DATE
```

## 2 · Morning review and selection

Open `drafts/DATE/review.html` (or `review.md` anywhere Markdown renders).

A light page with two sections: the child talks (kid-1 to kid-3) and the evidence based take (expert-1 to expert-3). Each option is one card:

- the header: option id, title, the child (name, girl or boy, talks to mom or both parents), the hook formula and its score, the code word
- one row with the angle, who it is for and why it may convert
- the seven slides side by side (they scroll sideways on a phone), each with its role, word count and why it pulls to the next slide
- the caption and the single CTA side by side
- under each slide, on packs written for the bold look, the highlighted phrase (click to change it)
- two dropdowns: "טענות ומקורות" (every claim, its source and the verbatim quote) and "תיאורי תמונות ועוגן הדמויות" (each slide's text next to its image brief and the exact prompt)

The topic reason and the live-site product facts sit in dropdowns too. The chip at the top says whether the voice is calibrated (it counts your rewrites, see section 7).

**Edit and save from the page.** Start the editor:

```bash
python3 carousel/carousel-pipeline/scripts/review_server.py
```

and open http://localhost:8777 (or start `carousel-review-editor` from Claude Desktop's preview). Click any headline, body line, caption, CTA or option title and type; Enter adds a line. "שמירה" or Cmd+S saves into `pack.json` (the previous version is copied to `versions/vN/` first), rebuilds the page, and lists anything that breaks a rule in Hebrew next to the field, for example "פסיק בשורה 1". Edits are saved even when something still needs fixing, so nothing typed is lost; a pack with errors cannot go to production until it is fixed. Changing the CTA also updates the last slide, the caption's last line and the code word. Every saved change to slide text or the caption is also logged as before and after for the voice skill to learn from (section 7). Opened as a plain file, the page is read only and says how to start the editor.

Nothing is chosen automatically. Tell Claude, for example: `produce kid-2 from the 2026-10-08 pack` (edits welcome: "change slide 3 to ...").

## 2b · Pictures from the OpenAI API (since 03 Nov 2026)

Yarin, 03 Nov 2026: "disconnect carousel machine from any other image generation tool, i want it to use the gpt api from now on". The picture sources before it, fal.ai (until 30 Oct 2026) and ChatGPT in Yarin's Chrome (30 Oct to 03 Nov 2026), are retired: their files are in `_to-delete/`, and `tests/test_openai_pictures.py` fails if a script reaches them again.

**Where.** `scripts/openai_pictures.py` (client, estimate, 4:5 crop), `scripts/openai_generate.py` (the job runner: run, replace, qa, plan, status) and `scripts/openai_models.json` (the model `gpt-image-2.5-flare`, size 1024x1536 made then cropped to the centred 4:5 at 1024x1280, quality `low`, the per-token rates, the estimate assumptions). `OPENAI_API_KEY` comes from the macOS Keychain item `openai-api-key` through `~/.zshrc`, so scripts run through `zsh -ic`. It is never written to a file, a log or an error.

**Yarin's four rules for the key** (03 Nov 2026, memory `feedback-openai-api-key-rules`): always ask for a budget, never exceed it, tell the estimated tokens and cost before generating, create nothing without his explicit permission. They are enforced in code, not only by habit:

- `openai_generate.py run` and `replace` need `--max-usd`, the budget Yarin approved for this carousel, with no default. The whole batch is checked once before the first call and every call again when it starts (logged spend + calls in flight + this call's estimate); a call whose outcome is unknown (a timeout) counts at its estimate. The real cost of each finished call is logged from the usage OpenAI returns (`generation-log.jsonl`: model, request id, tokens, cost, never the key). `--dry-run` and `plan` print the prompts and the estimate and call nothing.
- In Carousel Machine, `producer.py` stops every stage that would spend in status `approval` ("מחכה לתקציב ולאישור שלך"): the page shows the number of pictures, the model and quality, the estimated tokens (prompt, reference picture, picture output) and dollars, and asks for the budget (the most the whole carousel may cost, what is already spent included; it must cover the estimate) and a click on "אני מאשר, ליצור". The permission covers that one stage and is used up: the cover or the one picture, a story's other slides, and every another-take ask separately. "לא עכשיו" makes nothing. A restart never carries a permission over.
- Only quality `low` is allowed, because it is the only one measured (03 Nov 2026: 121 text tokens in, 158 picture tokens out, about $0.0053). The estimates are deliberately high (320 output tokens a picture, 1,500 tokens for a reference picture); raise the quality in `openai_models.json` only after one measured run.
- The model and edit calls were tested on 03 Nov 2026 only for text-to-image at 1024x1536 (`media/inbox/2026-11-03-*`, about $0.03 in all). The edit call (slides 2 to the last, multipart `image[]`) and the booklet sizes are written to the API's documented shape and have not run yet: the first real run confirms them, and an error answer is not billed.

**In the app.** Picking a carousel and pressing produce freezes it as before (free), then it waits in "מחכה לתקציב ולאישור שלך" until the budget and the yes. After the cover is approved, a story waits again for the other slides. Another take with a note waits again too. `producer.authorize` and `producer.cancel` are `/api/production/authorize` and `/cancel`.

**By hand** (the lumebook-carousel skill, Mode 2): `prepare_picture_jobs.py PATH/pack.json OPTION`, show Yarin `APPROVAL.md` or `openai_generate.py RUN_DIR plan`, get a budget and a yes, then `zsh -ic 'python3 scripts/openai_generate.py RUN_DIR run JOB --max-usd BUDGET'`.

Tests: `tests/test_openai_pictures.py`, `tests/test_story_production.py`, the Production class in `tests/test_pipeline.py`. None touches the network.

## 3 · Approval

Claude (or the app) runs `prepare_picture_jobs.py`, which freezes the option and writes `approved/DATE-OPTION/APPROVAL.md` without any network call. It shows:

- the frozen copy
- the number of images: one for the older one-picture packs, a picture per slide for story packs (the cover by text-to-image, the others edited from it)
- the model, quality and sizes, the estimated tokens, the estimated cost and the estimated maximum if every image needed two replacements
- what is regenerated on QA failure: only that image, at most twice

Generation starts only after Yarin gives a budget and a clear yes. The budget becomes `--max-usd` and the runner refuses to pass it.

## 4 · Image generation and QA

1. The cover (or the one picture) first. Claude inspects it at full size and records `qa JOB pass|fail`
2. Then, for a story, the other slides in parallel (after the cover is approved and Yarin approves that stage). Each is inspected for the same child and parent, hands and faces, accidental letters, a clean text zone and continuity
3. Failed pictures only are replaced, with a fix note added to the prompt. After two failed replacements of one image, Claude stops and asks. Each replacement needs Yarin's yes and room in the budget

Details and commands: `approved/DATE-OPTION/README.md` and `.claude/skills/lumebook-carousel/references/production.md`.

The key lives only in the shell environment (Keychain through `~/.zshrc`), so scripts run through `zsh -ic`. It is never written to a file or a log.

## 5 · Final export

```bash
python3 carousel/carousel-pipeline/scripts/compose_slides.py carousel/carousel-pipeline/approved/DATE-OPTION
```

Output in `final/`: `slides.html` (editable source), `01.png` to `08.png` (1080 x 1350), `contact-sheet.png`, `rtl-check.png` (every line mixing Hebrew with digits or Latin, large), `caption.txt`, `sources.md`, `alt-text.txt` and `DATE-OPTION.zip`. The Hebrew is HTML text on top of the images; the image model never draws letters.

**The story look and a picture per slide (29 Oct 2026, `story-format.md`).** A run frozen from a story pack (`copy_style: "story"`, or an option with `structure`) renders with `--look story`, the default for it: Varela Round (`assets/fonts/VarelaRound-*.woff2`, brand copies) in cream on an ink veil over each slide's own picture, gold tags (`N: text` gets a number badge), gold `## ` labels, a cream card for `> ` lines, `**x**` in gold, the gold cover pill and save button, the letter structure on a cream sheet; port of `media/projects/2026-10-29-lotem-format-carousels/render.py` (renders its final-v4 byte for byte). Slide N shows `generated-assets/slide-NN.png` (the cover `slide-01.png`), each QA-passed; `--placeholders` makes one per slide. Production: `prepare_picture_jobs.py` writes jobs `slide-01` (text-to-image from `option.image`) and `slide-02..NN` (an edit, the approved cover as the reference, the slide's `scene`, the upper third calm, no text); Carousel Machine makes the cover, waits for its approval, then (after Yarin approves that stage) makes the rest in parallel and marks them passed with the cover, then exports. No built-in cap: the budget is whatever Yarin types for each carousel (section 2b). Since 03 Nov 2026 every picture comes from the OpenAI Images API, the cover attached as the reference. Older runs and looks are unchanged.

Two looks. Bold (10 Oct 2026, the default for copy that has highlights): very large headline, the `highlight` phrase in a colour block, speech bubbles for quoted sentences, the comment line as a button. Classic (8 Oct 2026, automatic for older copy): the earlier, smaller layout. `--look bold` or `--look classic` forces one, and `--out NAME` writes to another folder so two looks can be compared side by side.

**Text on the plain wall, the picture untouched (Yarin, 24 Oct 2026: "i dont want you to distort the images anymore, fit the text on the flat space in the generated picture even if it means to play a bit with the sizing of the text or make another line").** The picture fills every slide exactly as generated. Until then the art was pushed down under the text and the gap filled by stretching its top rows. Now `compose_slides.py` (`fitTop`) measures, for every text width, the row where the picture stops being plain wall or sky, and fits the copy above it with 28px to spare: it tries each headline size from the largest down, first on the copy's own lines and then breaking the widest line that does not fit at its most even word gap (up to 3 more lines, each costing 10px of headline size), keeps the largest type, then grows the body as far as the wall allows. Under the usual floors it goes on to 80 percent of them. If nothing fits even then, the closest layout gets the soft panel and the export reports how many px it runs into the picture. The copy starts 72px from the top (108 before). `rtl-report.json` records `headSize`, `bodySize`, `splits` and `clearance` per slide; `push` is always 0.

**Save and send icons (Yarin, 24 Oct 2026: "add default save and send icons").** On the last slide of a save and share CTA, the yellow save button carries Instagram's save (bookmark) glyph and the send line its send (paper plane) glyph, drawn as outlines in `compose_slides.py` (`SAVE_ICON`, `SEND_ICON`). The older comment button has none.

The carousel never names the brand: no logo and no product card by default. `--brand-mark` adds the logo and `--preview-card` adds an unbranded `real-assets/preview.png` on slide 7, if ever wanted.

To test the layout without paid images: add `--placeholders` (writes to `final-placeholders/`).

**Drive copy: off since 03 Nov 2026** (Yarin: never use the My Drive folder `LumeBook תוכן` again). `scripts/drive_export.py` stays in place but does nothing while `shared/facts.json` has no `drive_content`; exports stay in `approved/*/final/`.

When posting: set the comment automation for the code word in Meta Business Suite (always לומי since 10 Oct 2026, one automation for every carousel), paste the alt text.

## 6 · Hard rules the validator enforces

On everything a parent reads (slide text, caption, CTA, code word):

- no dash of any kind, semicolon or hyphen (nor their lookalikes) since the evening of 24 Oct 2026 (Yarin: "lets bring back punctuation marks except em dashes, semicolon and hyphens"; `lib.FORBIDDEN_CHARS`, gated by `lib.punctuation_rule_applies`); older packs and the games and books carousels keep the old rule, no em dash, period or comma (`lib.LEGACY_FORBIDDEN_CHARS`). The error names the field, line, column and character, and nothing is deleted automatically
- one thought per line (12 words max), hook 8 words in the main line and 12 on the slide, 18 on the CTA slide
- packs from 10 Oct 2026 22:00: every headline is a full thought of at least 3 words and never only an order word ("דבר ראשון"), so the seven headlines read alone tell the whole story (Yarin); the review page prints them in one line
- the CTA word is always לומי (Yarin, 10 Oct 2026) in packs from the same time
- packs from 10 Oct 2026 23:00: wherever a slide lists examples, the list (`examples` on the slide) has exactly the number drawn for the option, from 3 to 7 (`examples_per_option` in the start JSON, saved in `drafts/DATE/example-slots.json`, copied into `examples_target`); the slide count stays 7
- packs from 10 Oct 2026 18:30 (the bold look): cover headline up to 3 lines of 18 characters, other headlines 2 lines of 22, body 3 lines of 34, up to 20 words on slides 2 to 6, and a `highlight` of 1 to 3 whole headline words on slides 1 to 6. Older packs: 25 words per slide, 30 characters per headline line, 42 per body line
- hook openers: shame, guilt, fear and threats aimed at the parent are rejected, and so are openers with no gap (״חובה לראות״, ״האם ידעתם״). Loud openers that the carousel pays off are allowed since 10 Oct 2026 (״תפסיקי״ about one action, ״מה שלא מספרים לך״, ״הסיבה האמיתית״, ״לא תאמיני״)
- no brand name (לומבוק, LumeBook) and no catalogue book title: only the last slide suggests a personalised story where the child is the hero
- no diagnosis or jargon words, no guarantees, no "every child", no second CTA
- the CTA keeps the brief's idea (כתבו "X" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור) and appears word for word on slide 8 and as the caption's last line

Arc (Yarin's brief, 10 slides since 14 Oct 2026): 1 hook from the hook bank, 2 explains the idea, 3 to 8 one or two numbered examples each (numbered 1, 2, 3... across the carousel, 6 to 9 in all, Yarin's choice), 9 the recap (nothing that prepares a sale), 10 a short suggestion to help the child with a personalised story where they are the hero, then the CTA. Every option is about one named Israeli girl or boy and talks to mom or both parents, never dad; the CTA follows (כתבי for mom, כתבו for both parents). Each option has ONE picture that depicts the idea, shown behind every slide (older packs: 7 slides, a picture per slide). Every slide before the last records its pull, the examples and the story map to sources, and each option's hook names its formula, the question it opens, where it is answered, and a score of at least 9 of 12 (`hook-bank.md`).

Hooks (since 8 Oct 2026, schema_version 3): before the six options the pack holds a private hook slate of 6 kid and 6 expert candidates (different formulas, 3+ families and 3+ mechanisms per direction), each scored 0 to 2 on ten criteria with four honesty checks; a failing candidate is never used. The six options must use 4+ mechanisms, 4+ sentence shapes, 3+ slide 2 moves and 2+ awareness stages, with no two near-identical openings. Slide 2 must not lean on slide 1. A hook that states a fact about children needs a sourced claim on slide 1 or 2. A trend formula past its review date is blocked. The system never picks a winner. `python3 carousel/carousel-pipeline/scripts/nightly.py hooks` shows each formula's evidence and status. Older version 2 packs still validate with the earlier rules.

Structure: exactly kid + expert, 3 options each, 7 slides each with the fixed roles, a named child from `names.md` per option (each different), talking to mom or both parents and never dad, a different hook formula per option, unique ids, a source for every option, a sourced fact in every expert option, a live-site product fact behind the slide 7 hint, product facts checked within 2 days, no topic from the last 14 packs, no code word from the last 14 days, a hook family at most twice per pack and blocked after two selections in 7 days, and an honest voice status.

```bash
python3 carousel/carousel-pipeline/scripts/validate_pack.py carousel/carousel-pipeline/drafts/DATE/pack.json
python3 -m unittest discover -s carousel/carousel-pipeline/tests -v
```

## 7 · Voice

`voice-profile.md` and `.claude/skills/lumebook-hebrew-voice/`. Status today: fallback (`python3 carousel/carousel-pipeline/scripts/nightly.py voice` shows the live count).

The voice learns from your edits. Every save on the review page logs each changed line, before and after, to `.claude/skills/lumebook-hebrew-voice/examples/edits.jsonl`, and every nightly run reads the latest 30 before writing (what you cut, add, split and soften). A rewrite where at least half of the words are yours counts as one of the 15 samples needed to call the voice calibrated; small tweaks and line-break changes count as style signals only. You can also add samples directly: one real message or caption per file in `.claude/skills/lumebook-hebrew-voice/examples/approved/` (template in that folder's README).

The voice skill was built and evaluated with Anthropic's skill-creator: 3 test prompts with and without the skill, graded by the same lint (`voice-eval-workspace/iteration-1/benchmark.md` and `review.html`): 100% vs 40% on the hard rules.

## 8 · Recovering from failure

| What happened | What to do |
|---|---|
| No review in the morning | Check Claude Desktop, Code, Routines, lumebook-nightly-carousel, Runs. Usually the Mac slept or the app was closed. Run it now from the Routines page or by hand (section 1) |
| The run stopped on a permission prompt | Open the run, approve "always allow" for the listed command, run again |
| `finish` keeps failing | Read the errors; each names a field and character. Fix the lines in `pack.json`, run `nightly.py finish` again |
| A rerun for the same morning | Safe. The earlier pack moves to `drafts/DATE/versions/vN/` and history keeps one entry per date |
| Two packs on the same topic | Delete nothing. `nightly.py topics` shows what is eligible; the validator blocks topics from the last 14 packs |
| A carousel stays on "מחכה לתקציב ולאישור שלך" | Expected: nothing is made until Yarin types a budget and presses "אני מאשר, ליצור" (or "לא עכשיו"). Nothing is lost while it waits, also across a restart |
| `OPENAI_API_KEY is not set` | Run through `zsh -ic`, and check the Keychain item: `security find-generic-password -s openai-api-key` |
| `openai_generate.py` says it was frozen before 03 Nov 2026 | Freeze it again, free, keeping the pictures already made: `prepare_picture_jobs.py PATH/pack.json OPTION` |
| A picture call failed mid-run | Rerun the same `openai_generate.py ... run` command with a budget. Finished images are skipped; an error answer from OpenAI is not billed, a timeout is counted as spent |
| Over budget | The runner stops before passing `--max-usd`. Ask Yarin for a bigger budget before continuing |
| Same slide failed twice | The runner refuses. Decide: accept, change the scene brief, or drop the image |
| Copy changed after freezing | `prepare_picture_jobs.py ... --refreeze` archives the old run to `versions/vN/` and keeps every picture whose prompt did not change |
| Text overflows or RTL looks wrong | `compose_slides.py` exits 1 and lists the line; shorten or split it, rerun |
| Prices or the model changed | Update `scripts/openai_models.json` (model, rates, estimate assumptions), after one measured run at the new setting |

## 9 · Running in the cloud

The slide PNGs (`compose_slides.py` for production runs, `reco_render.py` for the games and books carousel) need a headless Chrome. `carousel_lib.find_chrome()` looks in this order: `CHROME_PATH` if set, the Mac app, then `google-chrome`, `google-chrome-stable`, `chromium`, `chromium-browser` on PATH. Off the Mac the renderer adds `--no-sandbox --disable-dev-shm-usage`. Everything else in the pipeline runs without Chrome; the render tests skip when none is found.

On a Linux box (Claude Code on the web), once per environment. Debian:

```bash
apt-get update && apt-get install -y chromium
```

If apt has no `chromium` package, or only a snap wrapper (Ubuntu), install Google Chrome instead:

```bash
curl -fsSLo /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt-get install -y /tmp/chrome.deb
```

Prefix `sudo` when not root. If Chrome sits somewhere unusual, set `CHROME_PATH` (see `.env.example`).

Fonts: nothing to install. The slides load Heebo, Assistant and Rubik with `@font-face` from `assets/fonts/` (copies of `shared/brand/fonts/`, kept equal by `lumebook.py sync`), and those `.ttf` files are in git. Optional safety net for an emoji or symbol in copy: `apt-get install -y fonts-noto-core fonts-noto-color-emoji`.

Check it works: `python3 -m unittest discover carousel/carousel-pipeline/tests` should run the `test_chrome_export_*` and `BoldLook` tests instead of skipping them.

### Seeing the cloud packs on the Mac

The weekly routine pushes each batch to `batch/ID` (section 0); the older nightly routine pushed each night to `nightly/DATE` (`nightly/DATE-2` when that date already had one). Its cloud environment needs network access set to Full; on the default (Trusted) setting it cannot read lumebook.com or the sources and stops without a pack (what happened on 15 Oct 2026).

Opening Carousel Machine (`review_server.py`, or the `carousel-review-editor` preview) brings them down by itself: it runs `scripts/cloud_sync.py` first, which fetches the `batch/*` and `nightly/*` branches, copies the batch plans and each new `drafts/DATE` folder (product images and slide PNGs included) with `git archive`, adds the night to `history.json` and `reco-history.json`, and notes the branch and commit in `drafts/DATE/cloud-source.json`. A folder that already exists here is never overwritten, because it may hold your edits; a newer cloud version is only reported (`cloud_sync.py --force DATE` takes it). The row of dates on every page is redrawn on each load, so the new night shows on the older pages too. Offline it says so and opens what is already here; `--no-cloud` skips the check. To pull without opening the editor: `python3 carousel/carousel-pipeline/scripts/cloud_sync.py`.

The cloud run starts from `main`, so `week-plan` first merges the history the earlier cloud runs left on their branches; rotation knows every cloud night even when nothing was pushed to `main`.
