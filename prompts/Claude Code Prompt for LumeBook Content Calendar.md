# Claude Code Prompt: LumeBook Content Calendar (Carousel Machine + test carousels + reel calendar in one place)

Written 11 / 11 / 2026 from Yarin's request in chat:

> "i need it to merge carousel machine, the new carousel ideas, and the reel calendar all in one place. it looks like a big montly calendar, i can open each day in it shows the hours and the content. i need it to be super efficient and clear, sophisticated but not messy, industry standard in the design, hierarchy, usability, features and editing capabilities but still in the design language and system we already have leaning heavily on clean apple liquid glass like design. everything must be big enough and clear enough and simple enough to understand, use color coding, icons, buttons, drawers and prevent the new combined tool to be too crowded, messy, unorganized, bad hierarchy, symmetry, spacing, margins etc. you can take inspiration from tools like postiz"

---

## 0. Before anything

1. Read `CLAUDE.md` in full (design system, Liquid Glass, language switch, edit button, project server, Carousel Machine and reels hub sections). Every rule there applies; this prompt only adds to it.
2. Read `docs/account-handoff/README.md` only to know what is still open; do not work on it here.
3. Work fast and precise. Use subagents only where they save real time (see section 8). Do the design and the build yourself.
4. Commit nothing unless Yarin asks.

## 1. Goal

One Hebrew tool, **לוח תוכן** (Content Calendar), where Yarin sees and runs every piece of content for the month:

- the child-voice carousels from **Carousel Machine** (packs, three kid options, grading, production, Postiz),
- the **test batch** carousels (`סבב ניסוי`, five types, options `a` and `b` every day, 11 to 30 Nov),
- the **reels** from the reel calendar / reels hub (two options a day, picks, scripts, make sheet, the made reel).

It opens on a big month calendar. A day opens into a drawer that shows the hours and what goes out at each one. A piece opens into its own panel where everything about it can be read, edited, picked, produced and checked. Nothing that works today is lost; it moves into one place with one look.

It is a new front end over the existing engines, not a rewrite of them. Carousel Machine, `test_batch.py`, `reels.py`, `reel_make.py` and their data files stay the single sources; the calendar reads them and writes through their existing save paths.

## 2. What exists today (read these, don't guess)

**Carousel Machine** (`carousel/carousel-pipeline/`)
- Page: `scripts/studio.py` (one page, lb-app shell since 8 Nov: page sidebar with views, days and batch menu; sticky glass top bar; day cards; picks panel). Served by `scripts/review_server.py` at http://localhost:8777/ (login item) and through the project server at http://localhost:8780/hook-studio/.
- Endpoints (`review_server.py`): `GET /api/state`, `POST /api/save`, `/api/save-reco`, `/api/save-test`, `/api/grade`, `/api/push-grades`, `/api/produce-send`, `/api/production/...`, `/api/productions`, `/api/postiz-preview`, `/api/sync`.
- Data: `drafts/DATE/` (packs), `productions.json`, `grades.json`, `history.json`, `approved/`. Story format rules: `story-format.md`. Picture rules: OpenAI Images API only, budget and approval stop in `producer.py`.
- Skill: `.claude/skills/lumebook-carousel`.

**Test batch** (`carousel/carousel-pipeline/test-batch/2026-11/`)
- `README.md` (read in full: the 11 Nov rewrite rules, the five types `say`, `how`, `gift`, `age`, `reveal`, the days table, the posting times), `plan.json`, `carousels/DATE-a.json` and `-b.json`, `slides/`, `assets.json`, `picture-proposals/`, `runs/`. Code: `scripts/test_batch.py`. Shown today in Carousel Machine under סבב ניסוי (`/?batch=test-2026-11`).
- Times from its README: Mon, Wed, Fri 20:30; Sun, Thu 06:00; Tue, Sat 20:30. Pressing produce on a carousel that shows a picture budget is Yarin's permission for that budget and that carousel only.

**Reel calendar and reels hub** (`research/israeli-product-reels/src/scripts/series-2026-11/` and `research/israeli-product-reels/`)
- Data: `reels.json` (`reels` with `id`, `date`, `option` 1 or 2, `status`, `hook`, `vo`, `sees`, `caption`, `project`, `gpt`, `blockers`, `payoff`, `structure`; `picks` per day; `shoots`; `dropped`; `defaults.post_time` 21:30; `defaults.carousel_days`, the kid carousel topics at 06:00). `local-edits.json` holds the hub's unsaved-to-json edits; `reels.py merge local` folds them in.
- Code: `reels.py` (build, lint, merge, pick, make), `build_page.py`, `reel_make.py`, `broll.py`, `reel_gpt.py`; hub page `src/build_reels_explorer.py`, `src/hub_calendar.py`, `src/reels_explorer_template.html`.
- Endpoints on the project server (`tools/lumebook.py`): `GET /api/reels-hub/state`, `PUT /api/reels-hub/doc?path=edits/<key>` and `picks/<day>`, `/api/reel-files` (+ `raw`, `remove`), `/api/reel-make/jobs`, `/api/sample/jobs` (background asks).
- The make sheet, the docked drawer (`lb-dialog is-docked`, `html.lb-docked`), two options a day with בוחר בזו, one final per reel (`final/reel-<id>-1.mp4`), B-roll matches the words, GPT pictures only after Yarin's yes and budget.
- The read-only phone copy on Vercel (`/research/reels-calendar/`, `build_web()`, `WEB_BANNED`) must keep working.

**Shared**: `shared/design/lumebook.css` (tokens, `lb-` components, Liquid Glass sections), `design.py`, `categories.json`, `icons.json`, `hq-tools.json`, `nav.src.js`, `controls.src.js`, `i18n.src.js`; `shared/site-editor/`; `lumebook.json`; `tools/lumebook.py`; the Design System artifact builder `shared/design/build_ds_artifact.py`. Postiz: the global `postiz` skill and `reference-postiz` memory (ask before posting anything).

## 3. Research step (short, 15 minutes at most)

1. **Postiz** (Yarin named it). Open the Postiz app in the built-in browser if Yarin is signed in there, otherwise its public docs or site. Write down in 5 to 10 bullets which calendar patterns to borrow: views, how a post shows inside a day cell, the preview, moving a post to another time, the create and edit flow, how status is shown. Only what you actually saw.
2. **Apple Calendar** as the visual reference for the Apple look (month grid, day timeline, inspector). From memory is fine for layout ideas; do not quote facts about it.
3. Put the bullets in chat, not in a page (Yarin's rule: findings in chat).

## 4. The design

Hebrew, RTL, white only, the design system and Liquid Glass rules of `CLAUDE.md`. Phone 390px must work. Below is the target; adjust only where something in the code makes it wrong, and say why.

### 4.1 Layers, from back to front (one level of hierarchy each)

| Layer | What | Look |
|---|---|---|
| Project nav | the usual right side bar | as on every page |
| Page sidebar (`lb-sidebar`) | mini month, the type filters, the status filters, the "needs me" queue | lighter grey glass |
| Top bar (sticky, `lb-topbar` / `lb-edge`) | title and month name, ‹ היום ›, view switch, search, one primary button | `--glass-bar` |
| Month grid | the main surface | white ground, cells opaque grayscale, glass cards for items only where the rules allow |
| Day drawer | the hours of one day | `lb-dialog is-docked` on wide screens, popup on narrow, like the reels hub |
| Piece panel | everything about one piece | a sheet inside the drawer (or a second docked panel on very wide screens) with `lb-sheet` sections |

Never glass on glass. No `backdrop-filter` on anything repeated (calendar items, chips, rows). No side stripes. No scrollbars.

### 4.2 Colour and icons

- **Type = category hue.** Add one set to `shared/design/categories.json`, e.g. `content-types`: kid carousel, test carousel, reel (three hues). If the five test types need telling apart, show the type as an icon and a word, not five more hues. Run `sync` after.
- **Status = status colours**, never a category hue. One status ladder for all three kinds, mapped from each source (write the mapping table in the code and in the README):
  `רעיון / טיוטה` → `לדרג` → `לבחור` (two options, none picked) → `לצלם` (reels) → `בהפקה` → `מחכה לאישור שלי` (picture budget, OpenAI stop) → `מוכן` → `מתוזמן בפוסטיז` → `עלה`.
- **Icons** from `shared/design/icons.json` (`design.icon(name)`); add any missing glyph there, names never change.
- Every coloured thing also has a word or an icon (colour is never the only signal).

### 4.3 Month view (default)

- 7 columns, Sunday first, RTL (Sunday on the right). Six rows max, equal heights, generous gutters, the grid fills the width left of the page sidebar.
- Each cell: the date number (today in a violet ring), a tiny lane row of up to 3 items, then `+N עוד`. An item is one line: type colour dot + type icon + time (06:00 / 20:30 / 21:30) + a short title (hook or topic, clipped) + status dot. Minimum text 14px, cell targets 44px.
- **Two options in one slot** (reels א and ב, test `a` and `b`, the three kid options of a pack) show as **one item** with a small `א · ב` mark; the picked one is named, an unpicked slot says `לבחור` in its status.
- Fri and Sat get a faint grey ground; past days are dimmed; holidays only if a source already has them (Hanukkah dates from the test batch README, last order day 05 / 12).
- Hover (mouse) shows a quick preview card; click opens the day drawer. Drag an item to another day (see 4.6).

### 4.4 Week and list views

- **Week**: 7 columns with an hour rail (05:00 to 23:00), the same items as blocks at their time. Same drawer on click.
- **List** (רשימה): one row per piece, grouped by day, sortable columns (date, time, type, status, title), the fastest way to work through a queue. Use `lb-table` / `lb-rowlist`.
- View switch is an `lb-` segmented control: חודש · שבוע · רשימה. The day is the drawer, not a fourth view.

### 4.5 Day drawer

- Header: the day name and date (dd / mm / yyyy in text), ‹ › to step days, close.
- Body: an hour timeline of that day showing only the hours that hold something plus a light rail around them (no empty 24-row wall). At each hour a glass card per piece: type, title, status, the options (`א | ב` segmented, with בוחר בזו), thumbnail (slide 1 or the reel's first frame / final), and 2 or 3 actions that fit the status (לדרג, לבחור, להפיק, לאשר תקציב, לפתוח בפוסטיז). Nothing more on the card.
- A "what this day needs from me" line at the top when something waits (a pick, a grade, a shoot, a budget).
- Shoot days from `reels.json` `shoots` show as a separate non-posting row ("צילום").

### 4.6 Piece panel (editing)

Tabs (`lb-` tabs), only those that apply to the piece:

| Tab | Carousel (kid / test) | Reel |
|---|---|---|
| תצוגה | the slides as a swipeable strip at real ratio (1080x1350), slide editor beside the preview as Carousel Machine does today | the final video if made, otherwise the script view (hook, lines, what we see) |
| טקסט | every headline, body, label editable in place, saved through `/api/save` or `/api/save-test` (backup, voice lint, validation as today) | hook, lines, payoff, caption, saved through `/api/reels-hub/doc` then `reels.py merge local` |
| כיתוב | IG caption and FB text side by side, disclaimer shown as fixed | caption with search line and hashtags |
| הפקה | grade, produce, picture budget with the estimate and an explicit approve button, production steps, ZIP / Finder | the make sheet: drop zone into `source/`, files, ליצור את הריל job, progress, the made final |
| פרסום | Postiz state (scheduled time, posted or not), preview; any change in Postiz only after Yarin says yes in that moment | same |

Editing rules:
- Edits save in place with the `lb-` savestate indicator; Hebrew fields `dir="rtl"`, never `dir="auto"`.
- Every write goes through an existing endpoint. If a new one is unavoidable, add it to `tools/lumebook.py` (same-origin only, like the others) and say so in the README.
- **Drag to reschedule**: changes the date (and time slot) in the piece's own source (`reels.json` date, `plan.json` day). If the piece is already scheduled in Postiz, the move is blocked with a clear message ("מתוזמן בפוסטיז: לשנות שם?") and nothing is sent to Postiz without Yarin's yes. Every move has an undo toast.
- Two pieces at the same hour on the same channel show a warning on both.

### 4.7 Page sidebar

1. Mini month (click a day to jump).
2. **Type filters**: three toggles with hue dot, icon and count (kid carousels, test carousels, reels), and inside test carousels the five types as small toggles.
3. **Status filters**: the ladder from 4.2 with counts.
4. **"צריך אותי"** queue: everything waiting on Yarin this week (to pick, to grade, to film, budget to approve), each row opens its piece. This is the most important block; keep it at the top on a phone.

### 4.8 Top bar

Title `לוח תוכן` and the month name; ‹ היום ›; the view switch; search (hook, topic, caption text, reel id); one primary button (`+ חדש`: new reel idea or new carousel request, both through the existing background ask jobs, `/api/sample/jobs`).

### 4.9 Keyboard

`T` today, arrows move day or month (RTL aware), `1` `2` `3` views, `/` search, `Esc` closes the top drawer, `Enter` opens the focused item. Show them in a small `lb-kbd` help popover.

### 4.10 States

Loading skeletons in the grid, an empty day ("אין כלום ביום הזה"), a server that does not answer (Carousel Machine on :8777 down: show the reels and test batch anyway, with one quiet notice), save errors with retry. Never a blank page.

### 4.11 Quality bar for the look

Before calling it done, check every screen against this list and fix what fails:
- one clear primary action per surface; secondary actions quieter; destructive actions never next to primary ones,
- consistent spacing scale from the tokens, aligned edges, equal cell sizes, symmetric gutters,
- text never under 14px, body 16px, 44px targets, contrast on glass is readable,
- at most three levels visible at once (grid, drawer, panel),
- no more than one sentence of help text anywhere; labels do the work,
- the month at 1440px, 1280px and 390px all look intentional.

### 4.12 Best posting hours (from Yarin's stats)

The hours in this prompt (06:00, 20:30, 21:30) are placeholders from the test batch README and `reels.json`; 20:30 is an assumption, not a measured best hour. Do not hard-code them as final.

- **Ask first.** At the checkpoint, ask Yarin to share his stats (Instagram and Facebook insights exports, Postiz analytics, anything with post time and results). Note `lumebook-ig-insights-export-format` in memory: Meta CSVs have Hebrew headers and US Pacific times, so convert to Israel time, and subtract Yarin's own like and save from each post.
- **Analyse only what he gives you**, plus `research/carousel-audit/` data if useful. Per channel and per kind (carousel, reel), compare reach, saves, shares, comments and profile visits by hour block and weekday. Report in chat in plain words: the best 2 or 3 hour blocks per kind with the sample size behind each, and say plainly when a block has too few posts to trust. Never present a guess as a finding.
- **Put the result in the tool**: one `posting_hours` setting (a small JSON file the calendar reads, not scattered constants) holding the suggested slot per kind and weekday and the stats behind it. The month, week and day views use it as the default time of a new or moved piece, and the day drawer marks the suggested slots on the hour rail ("שעה מומלצת", with a one-line reason such as "הכי הרבה שמירות ב-20:00-21:00, 14 פוסטים"). A piece scheduled outside a suggested slot gets a quiet hint, never a block.
- **Keep it comparable**: the test batch compares morning against evening on purpose; the calendar must keep the existing times until Yarin approves the new ones, and show both, current and suggested.
- Update the stats later by running one command (`python3 tools/content_calendar.py hours <export>`), documented in the README.

## 5. Architecture

- **Where**: a new component, suggested `sites/content-calendar/` with `build.py` (uses `design.head()`, inlines the design system) and a page served by the project server, e.g. http://localhost:8780/sites/content-calendar/. Pick another path only if the code makes it clearly better.
- **One read endpoint**: `GET /api/calendar?month=YYYY-MM` in the project server (a small module, e.g. `tools/content_calendar.py`, imported by `tools/lumebook.py`), which reads Carousel Machine's `/api/state` from :8777, the test batch `plan.json` and `carousels/`, `reels.json` plus `local-edits.json` and `picks`, and returns one list of pieces in one shape:
  `{id, kind (kid|test|reel), subtype, date, time, channel, title, options[], picked, status, thumb, source: {file, key}, actions[]}`.
  Cache it briefly like `/api/home`. Writes keep going to the existing endpoints.
- **Old pages**: Carousel Machine, the reels hub and the reel calendar keep working unchanged until Yarin says to retire them. Add a link to the new tool from each.
- **Registry**: add the component to `lumebook.json` (watch, build, feeds), the tool to `shared/design/hq-tools.json` in the content topic, and run `python3 tools/lumebook.py ripple`. Any new pattern a second page could use goes into `lumebook.css` as an `lb-` component with a card in `build_ds_artifact.py`.
- **Language switch**: the page uses the normal `nav.js` switch; audience Hebrew (slide text, reel lines, captions) is marked `translate="no"`. Run `python3 tools/i18n.py bake` after builds.
- **Edit button**: works as on every page; the calendar's editable fields are `lb-editable` so the switch never touches them.
- **Phone copy**: not in this task. Do not touch the Vercel `/research/reels-calendar/` copy except to keep it building.

## 6. Hard rules (from CLAUDE.md and memory; repeat them to yourself before writing)

- OpenAI pictures: always ask the budget, never exceed it, show estimated tokens and cost before generating, nothing without an explicit yes; the calendar shows the approval stop, it never skips it.
- Postiz: never post, schedule, move or delete a Postiz post without Yarin's yes in that moment; never touch already uploaded posts.
- Reels: no price, discount or delivery cost; no languages or digital copy; Yarin is not a parent; `reels.py lint` must pass after any reel text change.
- Audience copy: no em dashes, לומבוק never לומיבוק, no AI mention, Hebrew grammar rules, feminine singular in test carousels as their README says.
- Dates shown as dd / mm / yyyy; ISO in data.
- White only, no scrollbars, no side stripes, Liquid Glass rules, Heebo + Assistant, tokens only in page CSS.
- Never stop the login items (:8780, :8777); test on a spare port: `python3 tools/lumebook.py serve --port 8791` with `LUMEBOOK_REELS_HUB_FILE`, `LUMEBOOK_SAMPLE_JOBS_FILE`, `LUMEBOOK_REEL_MEDIA`, `LUMEBOOK_REEL_MAKE_CMD`, `LUMEBOOK_CLAUDE` pointing at scratch copies and stand-ins. Never test date pickers or saves against real data; never test on the creator map.
- If Yarin has a page open in edit mode, ask him to press Done before writing that page.
- Never delete project files: `_to-delete/` with a README line.
- Restart what you changed: `python3 tools/serve_login.py restart` after `tools/lumebook.py`, `python3 carousel/carousel-pipeline/scripts/hook_studio_login.py restart` after Carousel Machine scripts.

## 7. Order of work

1. Read (section 2) and research (section 3).
2. **Checkpoint with Yarin**: in chat, 10 lines at most: the IA, the status ladder mapping, the three hues, and one ASCII sketch of the month and the open day. In the same message ask him for the stats to base posting hours on (see section 4.12) and say which files or exports would work (Meta Insights CSV, Postiz analytics, `research/carousel-audit/`). Wait for his yes, changes and the stats. This is the only stop before building.
3. Build the read endpoint and test it on :8791 against the real data read-only.
4. Build the month view, then the day drawer, then the piece panel (carousel first, then reel), then week and list, then sidebar filters, the queue and search, then drag to reschedule and keyboard.
5. Wire every write to its existing endpoint and test each one on scratch copies (section 6).
6. Registry, nav entry, categories, icons, DS cards, `ripple`, `i18n.py bake`.
7. Verify (section 9).
8. Report in chat: what works, what is not done, what was not verified, and the to-dos (republish, retire old pages).

## 8. Subagents (only where they save time)

- Up to **one Explore agent** at the start, only if reading `studio.py`, `review_server.py`, `hub_calendar.py` and the reels hub template yourself would take more than a few minutes: ask it for the exact data shapes and save paths, not a summary of the UI.
- **One fresh-eyes review agent** at the end: give it the screenshots (1440 and 390, month, day drawer, piece panel) and the quality list in 4.11, not your opinion; fix what it finds that is real.
- Everything else yourself. No workflows.

## 9. Verify (in the built-in browser, on :8791)

- Month, week, list, day drawer, piece panel at 1440, 1280 and 390 wide; screenshots of each.
- Every filter, the queue, search, keyboard keys, drag with undo, the Postiz block on a scheduled piece.
- Every write round-trips: edit a slide text, a caption, a reel line, a pick, a reschedule on scratch copies, reload, still there; `reels.py lint` passes; Carousel Machine's own page shows the same change.
- עב / EN switch: interface flips, audience Hebrew stays Hebrew.
- Console clean; no scrollbar visible; no em dash in any text you wrote (`python3 tools/lumebook.py check`).
- Carousel Machine down (stop nothing: point the endpoint at a dead port on :8791) still shows reels and test carousels with the notice.

## 10. Done means

- One page, לוח תוכן, in the side bar, that shows every kid carousel, test carousel and reel of the month with time, type, options and status, and lets Yarin open a day, open a piece and do there everything he does today in the three tools.
- All writes go to the same files as before; the three old pages still work and link to it.
- `ripple`, `check`, `reels.py lint` and the i18n check pass; README in the component folder with the status mapping, the endpoint, the rules and how to rebuild.
- Posting hours come from the stats Yarin shared (4.12), with the evidence shown, not from the placeholders.
- A short chat report with screenshots and the list of what is left.
