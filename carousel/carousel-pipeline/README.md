# Carousel Machine · the LumeBook nightly carousel pipeline

Named Hook Studio on 10 Oct 2026, renamed Carousel Machine on 22 Oct 2026 (Yarin: "change hook studio name to carousel machine"). The work goes in this order: the hook (the loudest true cover the topic allows), the content (every slide worth the swipe on its own), the slide design (very large type, one highlighted phrase per slide). Sources and rotation are guardrails. The folder, the skill, the scheduled task, the cloud routine, the login item (`hook_studio_login.py`, `com.yarinbruner.hook-studio`), the `/hook-studio/` path and `hook-studio.html` keep their old names.

Every night at 22:00 Claude prepares six complete Hebrew carousel options on one topic for the next morning. Nothing is generated or paid for until Yarin picks one option and approves the cost.

```
22:00 nightly run (free)            morning (Yarin)              after approval (paid)
topic + research + 6 options  ──▶   review.html: read, edit,   ──▶  8 images on fal.ai, visual QA,
validated, review.html/md           choose e.g. kid-2               Hebrew overlay, 1080x1350 PNGs, ZIP
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

- **The grid:** slide 1 of every carousel of the batch, grouped by topic (the final slide 1 once a production is done, otherwise the cover text in the pillar look), each with its grade, production state and a "+ להפקה" button that picks it. Filter: הכול, לדירוג, הפקה, לאישור. The week menu in the top bar switches to an older batch. A click opens the carousel in a sheet over the grid (הקודם, הבא, סגירה or Esc; leaving saves first) with the editor and, beside it, the grade and production panel
- **Side panel, נבחרו להפקה:** the picked carousels not yet produced (× takes one off), "להפיק את כולן" with the most it can cost (up to $0.50 each, games and books free), then the ones in production or done, waiting for approval first. A click opens that carousel. The batch button skips a pick that already has a production (re-export stays in that carousel's own panel). On a phone it is a drawer from the "להפקה" button
- **In the sheet, the carousel:** the slides with every headline, body and highlight editable in place, the caption and the CTA (kid and expert); the rendered slides plus their text fields and the caption (games and books). "שמירה" or Cmd+S saves through the editors' own save (backup to versions/vN, voice log, validation, rebuilt review pages; games and books slides are re-rendered); moving to another carousel saves first. Problems the validator finds show under the save bar
- **In the sheet, beside it, grade and production:** 1 to 5, the reason, the "להפקה" switch (all saved on change to grades.json), and the carousel's production: "להפיק עכשיו" (kid or expert: one picture, picking it is the approval to spend up to $0.50 with every attempt), the picture to approve or redo with a note (2 at most), then the slides, contact sheet, RTL check and ZIP by themselves; games and books export at once with no cost. ZIP, Finder, re-export after a text edit. producer.py, productions.json
- **Top bar:** progress, "מחכות לאישור", "שליחת הדירוגים לענן" (commits grades.json alone and pushes main, so the next batch reads it), the cloud check (cloud_sync.py without a restart)
- Keys in the sheet: arrows, 1 to 5, P, W, Cmd+S, Esc closes. The old addresses (/pool/ID, /grade/ID, /productions, /packs) open the page; the older pack editors (drafts/DATE/review.html) still work by address

Learning: `scripts/grades.py brief` turns grades.json into the summary the weekly cloud run reads before it writes (cloud-weekly-prompt.md, step 0.3). Grades are taste, not results: only hook-results.json can move a hook formula.

## 0 · The weekly batch (since 16 Oct 2026)

**Since 24 Oct 2026 (Yarin, after the carousel audit in `research/carousel-audit/`): two topics a day, child voice only, and the save and share CTA.** "Keep the child-voice numbered lists, on 2 topics that have a best-selling book (6 versions for each day (3 options for each) so i can choose the strongest one)", "change the cta to save the post and share to a parent who would agree", one carousel posted a day, and "do it" on the contrast fix. Packs from `lib.DAILY_PAIR_FROM` (2026-10-24 18:00) have `format: "two_topics"`: `topics` holds the day's two topics, `topic` repeats the first, and one `kid` direction holds kid-1 to kid-3 (topics[0]) and kid-4 to kid-6 (topics[1]), each with `topic_id`; the hook slate has keys `a` and `b`. `week-plan` (`batch.make_pair_plan`) gives each of the 7 days two topics of two different books from topic-bank.md "Best-selling books" (in season first, then the longest since last use; no topic twice in the week, no book more than twice, none from the previous 3 packs) and no event slot. Slide 10's headline is always `אפשר לעזור להם גם בסיפור אישי` (`lib.STORY_LINE`; Yarin: "change the cta to אפשר לעזור להם גם בסיפור אישי"). The CTA under it has no comment word: `תשמרי את הפוסט` / `ותשלחי לאמא שתתחבר` or `תשמרו את הפוסט` / `ותשלחו לאמא שתתחבר` (`lib.SAVE_SHARE_FORMS`), and a comment or link request anywhere is a second CTA. Every option must be in the child's voice (an ERROR now). Half the options are about a girl and half about a boy, and each topic has at least one of each (Yarin, 24 Oct 2026: "make sure the carousel machine do 50/50 boys and girls"): `nightly.py start` prints `child_gender_per_option` (`lib.gender_slots`: alternating, the first option flipping day to day so kid-1 is not always a girl), and `nightly.py finish` and `validate_pack.py` reject a pack generated from `lib.GENDER_BALANCE_FROM` (2026-10-24 21:00) that is not 3 and 3 (`lib.gender_balance_issues`; it does not block producing an option). Carousel Machine shows each day as its two topics side by side, three options each. The validator keeps the older rules for older packs. The week of 25 to 31 Oct 2026 (batch 2026-10-25, written that morning in the old shape) was switched to the new last slide on 24 Oct (Yarin: "switch this week's 42 carousels to the new last slide"): its packs carry `cta_style: "save_share"` (`lib.save_share_applies`), so the CTA rules are the new ones while the one topic and the kid and expert directions stay; each pack's version before the switch is in its `versions/v1`. A complete passing pack: `tests/fixtures/two_topic_pack.json`; tests: `tests/test_two_topics.py`. The notes below describe the batches up to then.

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
- It never calls fal.ai or anything paid
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

## 3 · Approval

Claude runs `prepare_fal_jobs.py`, which freezes the option and writes `approved/DATE-OPTION/APPROVAL.md` without any network call. Claude then shows:

- the frozen copy
- 8 images: 1 character and style reference (`openai/gpt-image-2.5/flare/text-to-image`) + 7 slide scenes edited from it (`openai/gpt-image-2.5/flare/edit`)
- quality high, 1024 x 1280 (4:5), final export 1080 x 1350
- estimated cost about $0.48, estimated maximum about $1.43 if every image needed two replacements (fal prices this model by tokens; the estimate comes from the fal pricing table checked 2026-10-07)
- what is regenerated on QA failure: only that image, at most twice

Generation starts only after a clear yes. The approved amount becomes `--max-usd` and the runner refuses to pass it.

## 4 · Image generation and QA

1. Reference image first. Claude inspects it at full size and records `qa character-reference pass|fail`
2. Then the 7 slides. Each is inspected for the same child and parent, hands and faces, accidental letters, a clean text zone, product accuracy and continuity
3. Failed slides only are replaced, with a fix note added to the prompt. After two failed replacements of one image, Claude stops and asks

Details and commands: `approved/DATE-OPTION/README.md` and `.claude/skills/lumebook-carousel/references/production.md`.

The fal key lives only in the shell environment (`~/.zshrc`), so Claude runs the generator through `zsh -ic`. It is never written to a file or a log.

## 5 · Final export

```bash
python3 carousel/carousel-pipeline/scripts/compose_slides.py carousel/carousel-pipeline/approved/DATE-OPTION
```

Output in `final/`: `slides.html` (editable source), `01.png` to `08.png` (1080 x 1350), `contact-sheet.png`, `rtl-check.png` (every line mixing Hebrew with digits or Latin, large), `caption.txt`, `sources.md`, `alt-text.txt` and `DATE-OPTION.zip`. The Hebrew is HTML text on top of the images; the image model never draws letters.

Two looks. Bold (10 Oct 2026, the default for copy that has highlights): very large headline, the `highlight` phrase in a colour block, speech bubbles for quoted sentences, the comment line as a button. Classic (8 Oct 2026, automatic for older copy): the earlier, smaller layout. `--look bold` or `--look classic` forces one, and `--out NAME` writes to another folder so two looks can be compared side by side.

**Text on the plain wall, the picture untouched (Yarin, 24 Oct 2026: "i dont want you to distort the images anymore, fit the text on the flat space in the generated picture even if it means to play a bit with the sizing of the text or make another line").** The picture fills every slide exactly as generated. Until then the art was pushed down under the text and the gap filled by stretching its top rows. Now `compose_slides.py` (`fitTop`) measures, for every text width, the row where the picture stops being plain wall or sky, and fits the copy above it with 28px to spare: it tries each headline size from the largest down, first on the copy's own lines and then breaking the widest line that does not fit at its most even word gap (up to 3 more lines, each costing 10px of headline size), keeps the largest type, then grows the body as far as the wall allows. Under the usual floors it goes on to 80 percent of them. If nothing fits even then, the closest layout gets the soft panel and the export reports how many px it runs into the picture. The copy starts 72px from the top (108 before). `rtl-report.json` records `headSize`, `bodySize`, `splits` and `clearance` per slide; `push` is always 0.

**Save and send icons (Yarin, 24 Oct 2026: "add default save and send icons").** On the last slide of a save and share CTA, the yellow save button carries Instagram's save (bookmark) glyph and the send line its send (paper plane) glyph, drawn as outlines in `compose_slides.py` (`SAVE_ICON`, `SEND_ICON`). The older comment button has none.

The carousel never names the brand: no logo and no product card by default. `--brand-mark` adds the logo and `--preview-card` adds an unbranded `real-assets/preview.png` on slide 7, if ever wanted.

To test the layout without paid images: add `--placeholders` (writes to `final-placeholders/`).

**Drive copy (Yarin, 18 Oct 2026: "export there from now on").** Every export into `approved/*/final/` (kid, expert, and games and books from the app) is also copied to Yarin's My Drive folder `LumeBook תוכן/קרוסלות/DATE-OPTION TOPIC/` (slides, caption, alt text, contact sheet; ids in `shared/facts.json` `drive_content`). The copy goes through Google Drive for desktop, so it needs that app signed in as yarinbruner02@gmail.com on this Mac. Until then each run waits in `drive-pending.json`; `python3 carousel/carousel-pipeline/scripts/drive_export.py` reports the status and copies everything waiting once Drive is there.

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
| fal call failed mid-run | Rerun the same `fal_generate.py ... run` command. Finished images are skipped |
| Over budget | The runner stops before passing `--max-usd`. Ask for a new cap before continuing |
| Same slide failed twice | The runner refuses. Decide: accept, change the scene brief, or drop the image |
| Copy changed after freezing | `prepare_fal_jobs.py ... --refreeze` archives the old run to `versions/vN/` |
| Text overflows or RTL looks wrong | `compose_slides.py` exits 1 and lists the line; shorten or split it, rerun |
| fal endpoints or prices changed | Refresh `scripts/fal_endpoints.json` from the fal model pages or the fal MCP `get_model_schema` and `get_pricing` |

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
