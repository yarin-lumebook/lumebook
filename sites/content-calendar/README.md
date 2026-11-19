# לוח תוכן (content calendar)

Built 11 / 11 / 2026 from Yarin's request ("merge carousel machine, the new carousel ideas, and the reel calendar all in one place ... a big monthly calendar, i can open each day ... the hours and the content"; prompt in `prompts/Claude Code Prompt for LumeBook Content Calendar.md`). Same day: "every day should have 2 reels and 2 carousels", "everything ... uploaded both to ig and fb except trial reels", "5 different hook suggestions for each piece of content before you generate anything", "trial reels ... only after the main version and the different hooks got approved".

Open it at http://localhost:8780/sites/content-calendar/ (project server). It is a front end over the existing engines; Carousel Machine, `test_batch.py`, `reels.py`, `reel_make.py` and their files stay the single sources. The old pages (Carousel Machine, the reels hub, the reel calendar) keep working and link here.

## Files

| File | What |
|---|---|
| `build.py` | Writes `index.html`: `design.head()` (design system, project nav, language switch), `page.css`, `page.js`, icons, the `content-types` hues, key dates from `shared/facts.json`, the caption disclaimer |
| `page.css`, `page.js` | The page (tokens and `lb-` components only) |
| `posting-hours.json` | Targets per day (2 carousels, 2 reels), the current times, the suggested times and the stats behind them |
| `calendar-state.json` | The calendar's own state (hooks, approvals, carousel moves, trial reels, reminders, ideas, GPT runs); written only by the server |
| `../../tools/content_calendar.py` | The read model and the calendar's few writes; `month` and `hours` commands |

Rebuild after changing `page.css`, `page.js` or `build.py`: `python3 tools/lumebook.py build content-calendar` (or `python3 sites/content-calendar/build.py`), then `python3 tools/i18n.py bake`. After changing `tools/content_calendar.py` or `tools/lumebook.py`: `python3 tools/serve_login.py restart`.

## The page (11 Nov 2026, second pass)

Yarin: "month/week/list get changed to month/week/day", "view the entire month/week/day and a hint of previous/next month ... i don't want to scroll", "day view - like in calendar an hour after an hour", "היום - exit everything and goes back to main calendar view highlighting today", the sidebar "make it colapsable" and the legend "add it to the side bar".

- Three views, חודש · שבוע · יום (keys 1 2 3), each fitted to the window above 860px (no page scroll). The month shows whole weeks, the days of the month before and after faded; a day shows as many one-line entries as fit, then "+N עוד". Week and day go hour by hour, the rows sharing the height between the earliest and latest post (08:00 to 22:00 at least), entries placed by their time and side by side when they overlap, a red line at the current time today. The day view also shows each empty planned slot (חסר ריל · 13:30) with its + רעיון button, and what has no hour in a lane at the top.
- The arrows move a month, a week or a day by the view (← → too). היום closes an open piece, jumps to today in the current view and rings it for a moment.
- Clicking a day (a month cell, a week header, +N) opens the day view; clicking an entry opens the piece over the calendar area (Escape, ✕ or the back button close it).
- The page loads the month and the months before and after (one after another; the server builds one month at a time, `collect()` holds `_collect_lock`, because each build keeps that month's Postiz list in the shared `_LIVE`, and two at once mixed their posts).
- The sidebar folds away from the button at the start of the top bar on a wide screen (remembered in this browser); below 1400px it opens from תור וסינון as before. The legend is its last section.

## Endpoints (project server, `tools/lumebook.py`; writes same-origin only with `X-LumeBook-Board: 1`)

- `GET /api/calendar?month=YYYY-MM[&rev=]`: every piece of the month in one shape (below); `{"same": true}` when `rev` is unchanged (the page polls every 15 seconds).
- `PUT /api/calendar/doc?path=<collection>/<key>`: one document of `calendar-state.json` (`{"_delete": true}` removes it). Collections: hooks, approvals, moves, trials, reminders, ideas, gpt.
- `POST /api/calendar/move {id, date, time?}`: drag to reschedule (see Rules).
- `POST /api/calendar/reel-merge {reel}`: `reels.py merge local <id>`, then `reels.py lint`; returns this reel's lint lines.
- `POST /api/calendar/jobs` and `GET /api/calendar/jobs`, `.../<id>/claim|cancel|dismiss`: background asks to Claude (`claude -p`, no tools, the Mac's login) for the 5 hooks, the prompt box and new ideas. Its own job list (`.lumebook/calendar-jobs.json`), so the reels hub's tray never takes a calendar answer. `GET` also returns the calendar's running tasks and the hub's reel jobs.
- `POST /api/calendar/gpt {reel, budget_usd, confirmed: true}`: a reel's GPT pictures, `reel_gpt.py run <id> --max-usd N --yes` through `zsh -ic`; refused without the explicit yes or above $5.
- `POST /api/calendar/trials {reel}`: the trial versions, `reels.py make <id> --trial-only`; refused until the main version is approved and 4 trial hooks are ticked.

Every other write goes through the existing endpoints: Carousel Machine's `/api/save` (kid), `/api/save-test` (test), `/api/grade` (grade, pick), `/api/production/start|authorize|reveal|postiz`, `/api/postiz-preview` (forwarded by the project server); the hub's `/api/reels-hub/doc` (reel text), `/api/reel-files` (drop files), `/api/reel-make/jobs` (make the main version).

- `POST /api/calendar/reel-postiz {reel, kind: main|trials|fb_trial, date, time, ig_text?, fb_text?, draft?, trial_index?, confirmed: true}`: a reel to Postiz (11 Nov 2026, "so connect it"). `main`: the approved final to Instagram and Facebook; `trials`: every trial version not sent yet, Instagram only with `is_trial_reel` and `graduation_strategy` MANUAL, 5 minutes apart; `fb_trial`: one trial version to Facebook only (the next-day reminder's button). Refused without `confirmed`, before the main version is approved, in the past (under 5 minutes ahead), with a dash or the wrong brand spelling, and a second time (a second send would make a second post). The page asks twice and shows the date, time and channels. Texts: Instagram gets the caption, Facebook the caption without the comment-word line plus the store link with the UTM (`FB_LINK`), both ending with the short disclaimer; both editable before sending. Sends are recorded in `calendar-state.json` `postiz`; the live Postiz list then decides queued or published. Postiz's CLI has no graduate command (checked in `postiz --help`), so moving a trial reel to the main feed stays in the Instagram app.

## The piece

`{id, kind (kid|test|reel|idea|post|remind|shoot), subtype, subtype_he, date, time, channels, title, options[], picked, status, status_he, flags[], needs[], thumb, postiz, moved, source: {file, key}, detail}`

- `k-<pack date>-<lane>` a child-voice carousel: one topic (lane a or b) of a pack, its three options. Unproduced options come only from the batch Carousel Machine opens by default (the 1 to 29 Nov packs, never produced, are hidden). Produced ones come from `productions.json`, placed on their Postiz date (November's posts were made from the 30.11 to 6.12 packs).
- `t-<date>` a test batch day, options a and b.
- `r-<id>` one reel of `reels.json` (both reels of a day are posted; spare reels without a date are not on the calendar).
- `i-<key>` an idea from + חדש (in `calendar-state.json`); `p-<group>` a post found in Postiz that belongs to no carousel here (a reel matched by its words joins its reel instead); `m-<reel>` the next-day reminder; `s-<date>` a shoot day from `reels.json` `shoots`.

## Status mapping (one ladder for all kinds)

| Step | Kid carousel | Test carousel | Reel |
|---|---|---|---|
| רעיון | | | an idea from + חדש |
| טיוטה | every option has errors | every option fails lint | |
| לדרג | no option graded | no option graded | |
| לבחור | graded, none sent to production | graded, none picked | (both reels of a day go up) |
| לבחור הוק | picked, no hook chosen in the calendar | same | no hook chosen and no final made |
| לצלם | | | `needs-voice`, `needs-footage`, `needs-edit`, `blocked` (blockers show as a flag) |
| להפיק | hook chosen, not produced | same (the button shows the picture budget) | `ready` without a final |
| בהפקה | production queued, generating, composing, exporting | same | a reel job running |
| מחכה לאישור שלי | production in `approval` (budget) or `review` | same | final made, main version not approved |
| מוכן | production done, not in Postiz (or a Postiz draft, or deleted there) | same | main version approved |
| מתוזמן בפוסטיז | in Postiz, queued | same | matched to a queued Postiz post |
| עלה | Postiz says published | same | `posted`, or a published Postiz post matched to it |

Postiz is checked live (`postiz posts:list`, read only, every 5 minutes in the background). It wins over a run's `postiz.json`: on 30 Oct 2026 the 1 and 3 Nov posts were deleted in Postiz while their records still said scheduled.

## Rules

- Nothing spends money without Yarin's click in that moment: a test carousel's produce button asks twice and shows the budget; Carousel Machine's approval stop shows the estimate and takes a budget and an explicit tick; GPT pictures for a reel take a budget and a tick and go through `reel_gpt.py --max-usd --yes`.
- Nothing changes in Postiz without his click: scheduling asks twice and shows the date, time and channels. A piece already queued in Postiz never moves from the calendar ("מתוזמן בפוסטיז: לשנות שם?").
- Channels: carousels and main reels go to Instagram and Facebook; trial reels only to Instagram. The day after a reel's trial versions exist, a reminder asks to share one to the main feed and post it on Facebook (`m-<reel>`, "סימון שבוצע").
- 5 hooks before anything is generated: after an option is picked the piece waits in לבחור הוק; the hooks come from a background ask; picking one writes it into the source (reel `hook`, test cover `big` or `headline`, kid slide 1 `headline`) through the normal save. A reel's other 4 hooks can be ticked as trial hooks.
- Trial reels only after the main version is approved and exactly 4 trial hooks are ticked (`reel_make.py` builds five versions: the main hook and four more).
- Moves: a reel's date goes into `reels.json`; a carousel keeps its pack and file names (they carry the date) and the move is kept in `calendar-state.json` `moves`, which the calendar's Postiz button uses. Every move has an undo.
- Every day should hold 2 carousels and 2 reels (`posting-hours.json` `targets`): a day from today on that has fewer shows each empty slot as a row with a red outline between the posts around its planned hour, saying what is missing, e.g. "18:30 חסרה קרוסלה" (month and week; Yarin, 11 Nov 2026: first a gray line, then "change the line to a red outline of the line that says what's missing"; no amber chip any more), and the day view lists the empty slots with a button for a new idea. Every weekday, Saturday included, runs carousel, reel, carousel, reel (Saturday 12:30 test carousel, 15:30 reel א, 18:30 child-voice carousel, 21:30 reel ב; the test batch's `plan.json` Saturdays follow).
- Audience Hebrew on the page is `translate="no"` and every field is `lb-editable`, `dir="rtl"`; dates show as dd / mm / yyyy (isolated left to right).

## Posting hours

The weekly plan lives in `posting-hours.json` `plan` (weekday 0 = Sunday; roles kid, test, reel_a, reel_b) and is the single source of every time: the calendar, the test batch's `plan.json`, Carousel Machine's Postiz box (`postiz_export.plan_time`, `kid_times` in its state) and the reels (option א is `reel_a`, option ב `reel_b`). Yarin, 11 Nov 2026: four posting hours a day, enough gap not to feel spammy. Rules used: two carousels and two reels a day, formats alternate, at least `min_gap_minutes` (180) between posts (the calendar flags less), nothing before 09:00 (06:00 to 09:00 is 60 to 70% of a day's peak in `follower_active`, 30% on Saturday), the strongest blocks to the child-voice carousel and a reel.

| Day | Test carousel | Reel א | Child-voice carousel | Reel ב |
|---|---|---|---|---|
| Sun to Thu | 09:30 | 13:30 | 18:30 | 21:30 |
| Fri | 09:00 | 12:00 | 15:00 | 18:30 |
| Sat | 15:30 | 12:30 | 21:30 | 18:30 |

Posts already queued in Postiz keep their time (a note says so on the piece) until Yarin says to replace them. Trial reels sit outside the four (Instagram only; their start time field defaults to `trial_start`, 11:30). Not measured: the best hour inside a 3 hour block, and Facebook. `python3 tools/content_calendar.py hours [export.csv ...]` still writes evidence from post results (`suggested`, `stats`); it no longer overrides the plan.

## The piece panel is one long list (11 Nov 2026, evening)

Yarin: "just make it a long list of features", then "dont repeat features". No tabs: every part of a piece one under the other, each with its heading, and each thing shown once.

- Carousel: תצוגה (slides, grade, lint), הוקים, טקסט (slide fields), כיתוב, הפקה, פרסום. Reel: טקסט (script, payoff, shot, caption, shoot day, lint), הוקים, הפקה, פרסום. Idea: הרעיון, הוקים. A reminder or a stray Postiz post has one part and no heading.
- Once each: a reel's hook and a carousel's internal name are edited in the title (no "שם פנימי" field, no "ההוק עכשיו" line under the hooks); the script and caption are the editable cells (no read-only copy); lint shows once; one save state in the header row; the reel's video only beside the list (not again in הפקה); a reel's Instagram text is the caption in טקסט (פרסום keeps only the Facebook text; the server adds the disclaimer); no buttons that only jumped between tabs (להוקים, להפקה, לערוך את התסריט).
- Opening a piece starts at the top; a piece waiting for its hook (status `hook`) starts at הוקים.

## A reel in the panel = the reel calendar's card (11 Nov 2026)

Yarin: "fix and add full capabilities from the reel calendar". Everything the reel card in the reels hub does, a reel piece does here, on the same files and endpoints:

- The fix: a piece taller than the window squashed its rows to 6px (the panel body is a grid of fixed height, and a row holding a scroll box may shrink to nothing). `grid-auto-rows: max-content` on the body keeps every row whole.
- Two columns on a wide panel: the list on the right, the finished reel on the left, sticky the whole way down, with הורדה and פתיחה בלשונית and when it was made; one column under 50rem of panel, the reel first.
- The header chips: עשיתי (the hub's tick, `/api/reels-hub/doc?path=made/<rkey>`, local-edits.json `made`), the series, the length (the made reel's real length from `work/make/report.json`, else the estimate), the voice, who it talks to, the book page link (`defaults.pages`) and the structure. The server sends them in the reel's `detail` (`series_he`, `voice_he`, `page`, `book`, `book_url`, `made`, `own_cta`, `clip_seconds`, `media.seconds`) and the month's `reels_defaults` (`reels_cfg()`: timing, the fixed closing line, the facts and word limits the asks use).
- The script as the hub's table: time, what I say, what is seen. Times come from the word count like `reels.seconds` (lead seconds on the first line, then words a second), the fixed closing line added unless the take says it itself (`own_cta`), the total in red outside 10 to 30 seconds. העתקת התסריט copies only what is said; ▶ גלילה is the teleprompter (speed 1 to 7, stops on any touch or scroll).
- The text is edited in place, no read-only copy: the hook is the title, then every line and what is seen, the payoff, the shot and the caption with העתקה (the Instagram text with the disclaimer); cells save when left, then `reels.py merge local` and lint; timings follow the typing.
- הפקה: the files as the hub's tiles (`lb-files`: frame or picture, length, size, ✕ moves one to `_to-delete`), uploads with a bar each, the `lb-drop` zone, and files dropped anywhere on the open reel go into it (a veil says which reel); the make prompt is an `lb-composer` (⌘ Enter), ליצור שוב once a reel exists, older finals listed.
- The ask box is the hub's composer: הערה לשינוי הריל with שליחה, and רעיון חדש (a different reel for the same day and series, every field rewritten, the month's other hooks not repeated). Both carry the hub's reel rules (word limits, the fixed closing line, the caption's last line, internal notes in second person, facts only); the answer is shown as a diff to apply, only the reel's own fields, with the house punctuation.
- The day view's bell box (same day, Yarin: "fix"): a fixed 2.75rem square centred at the block's far end, the bell 1.5rem (a wider rule had kept it at 1rem while the box grew to the block's height), opaque so the block's hue does not tint it.

## Testing (never on the real files)

A scratch copy of the project with Carousel Machine on a spare port, and the project server on 8791 pointed at it: `LUMEBOOK_PIPELINE`, `LUMEBOOK_TEST_BATCH_DIR`, `LUMEBOOK_CM_URL`, `LUMEBOOK_HS_PORT` (Carousel Machine), `LUMEBOOK_REELS_DATA`, `LUMEBOOK_REELS_HUB_FILE` (reels, also read by `reels.py`), `LUMEBOOK_CALENDAR_STATE`, `LUMEBOOK_CALENDAR_JOBS_FILE`, `LUMEBOOK_SAMPLE_JOBS_FILE`, `LUMEBOOK_REEL_MEDIA`, `LUMEBOOK_REEL_MAKE_CMD`, `LUMEBOOK_REEL_GPT_CMD`, `LUMEBOOK_TRIAL_CMD`, `LUMEBOOK_CLAUDE` (stand-ins), `LUMEBOOK_I18N_DIR`, `LUMEBOOK_I18N_QUEUE` (so the language switch does not write the real dictionaries), `LUMEBOOK_POSTIZ_CMD` (a stand-in script, or `off`) and `LUMEBOOK_TEST_MEDIA_ROOT` for the reel files of a test send.

## Not done yet

- Turning an idea into a real pack or reel: the idea waits with its 5 hooks in `calendar-state.json` `ideas`; tell Claude in a session "build the ideas in the calendar" and it reads them from there. The page's own Claude has no tools and cannot build files.
- The time of the second daily reel and every default time: Yarin will time all content again when he sends his stats (11 Nov 2026).
- Yarin's Instagram and Facebook exports for the hours analysis (`hours` reads Meta's Instagram format only; a Facebook export is read once Yarin sends one).
- Not tested against the real Postiz account (a stand-in recorded the calls); the first real send is Yarin's click.
- Drag to move (Yarin, 11 Nov 2026: "move content in each view to other days / time / week / month"): every piece that is not posted or already in Postiz drags in the month, week and day views. In the week and day views the drop sets the day and the hour under the pointer (15 minute steps, a blue line shows it) and snaps to an empty slot of its own kind when it is within 40 minutes; in the month a drop sets the day and keeps the hour, unless it lands on an empty slot's red outline, which gives it that slot's hour. The mini calendar and the week headers are drop targets too, and holding a piece over the previous or next button, or the gutter around it at the left or right edge of the calendar (nothing is drawn; the gutter does what its button does), moves the view on after half a second, then every 0.9 s, so a piece can cross a day, a week or a month. The previous and next buttons are long thin bars as tall as the calendar, one on each side, the arrow in the middle (Yarin, 11 Nov 2026: "make them long and thin like the drawing"); on a phone they are two round buttons in a row above it. The top bar keeps only היום. A toast offers ביטול.
- Day view (Yarin, 11 Nov 2026): no banner on top; a block that waits for Yarin carries a bell in an amber box at its far end (left in Hebrew; a 2.75rem square since the evening of 11 Nov), tooltip: what it waits for (Yarin: "move the bell and make it bigger and inside a box"). In the day and week views the previous bar stands between the hour labels and the content, and every block keeps 3 to 4 px of air from the edges of its column.
- All the text of a block shows in the week and day views (Yarin, 11 Nov 2026: "make sure i always see all the text of the content box", "except for the month view"): a block is at least as tall as its slot in time and grows to fit its words; a block that would cover the next one in its lane pushes it down, and one that would run past the bottom of the day is lifted (page.js settle(), run after each render, on resize and when the fonts load). The month keeps one line per entry.

## Stories (19 Nov 2026)

Yarin: "a daily story series we can schedule in postiz ... add it to our content-calendar with full story editing capabilities". A story set (one day of one series: Black Friday, Hanukkah, reviews) is a piece of kind `story` (`st-<series>-<date>`, blue), from `tools/stories.py` and `media/projects/2026-11-19-story-series/series.json` (README there). It drags to another day like a reel; its status is מחכה לאישור שלי until approved, then מוכן, then מתוזמן בפוסטיז and עלה.

- The editor (`story.js`) is the open piece: the frames on a strip (drag to reorder, add, duplicate, delete), the frame itself at its real size scaled down, and a side panel. Click a layer to select it, drag to move (snaps to the middle; Alt turns it off), pull its side handles for the width; arrows nudge (Shift by 10), Delete removes, ⌘Z and ⇧⌘Z undo and redo, ⌘D duplicates, Esc goes back to the frame. Layers: text (`**word**` in the emphasis colour, size, weight, font, alignment, colours, line height, shadow, a box behind it), picture (from the series' art, the brand backgrounds, an upload or a file dropped on the frame; blur boxes over names and faces, dragged on the picture), shape, sticker placeholder (link, poll, question, countdown: shown dashed here, never drawn into the PNG). The frame: background picture or colour, zoom and position, a darkening at the top or bottom, a request for a new picture, a note, "עולה ידנית". ביקורת puts a real screenshot from the social proof page on the frame with the name and photo blurred (the server finds them).
- `story-frame.js` draws a frame for the editor and, in headless Chrome, for the PNG, so the preview is the export.
- The publish part: channels, time, text check, the PNGs (create, download), the stickers to add by hand, approval (any edit clears it), Postiz (asks twice; one post per frame, both channels, one minute apart; refused before approval and a second time), duplicate the set to another day, remove it (kept in series.json).
- Endpoints: `POST /api/calendar/story {op: save|new|dup|delete|approve|unapprove|render|send|review-layers}`, `POST /api/calendar/story-upload?name=` (the picture is the body, up to 15 MB), `GET /api/calendar/story-reviews`. Same-origin only. Test on a spare port with `LUMEBOOK_STORIES_DIR` at a scratch copy and `LUMEBOOK_POSTIZ_CMD` at a stand-in (done 19 Nov 2026: three frames went out as three posts, both channels, a minute apart; the second send, an edit and a move were refused).
