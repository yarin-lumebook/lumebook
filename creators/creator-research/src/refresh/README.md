# Weekly refresh

Re-reads every creator in the map from Instagram, read only, and updates the six numbers on each card plus the flags.
Since 15 Nov 2026 it runs every night at 00:00 as part B of the scheduled task `lumebook-creator-cards-daily` (part A
reads the creator post numbers, `../posts/README.md`), and it is the only full re-read: the Saturday 21:00 task
`lumebook-creator-map-weekly` only adds new creators, and the midnight run measures them the same night. (From 24 Oct to
15 Nov it was the second part of the Saturday task; before that its own Sunday 10:00 task, `lumebook-creator-refresh`, now
manual only.) It never opens DMs or email and never sends, likes or follows anything.

## What it updates

| Box on the card | How | Source |
|---|---|---|
| עוקבים, צפיות חציון, צפיות לעוקב | followers and the median views of the reels on the profile's reels tab | `collect.js` |
| לייקים ל-1K צפיות, תגובות ל-1K צפיות | the median over the 12 newest reels of likes (comments) x 1,000 / views; 3 reels at least; hidden like counts are left out | `collect.js` |
| שאלות קנייה ל-100 תגובות | purchase signals per 100 audience comments over the 12 newest reels, the first page of comments of each (up to 15); 20 audience comments at least | `comments.js`, `comments.py` |

Purchase signals are counted as in the 14 Oct 2026 research (`research/creator-content-conversion/round2`): its rules
(`classify.py`) set aside the creator's own comments and requests for the post's offer, a broad net picks the comments that
might be a signal, and a reader checks them (`VERIFY_BRIEF.md`). A comment is read once, when its reel first shows up among a
creator's 12 newest; until a reel is checked its rule labels stand in. A number that cannot be measured this week keeps the
14 Oct one where there is one (`build2.py`), else the box says אין נתונים.

Flags shown as chips on the card, and under Must have › "Flagged by the weekly refresh" in the filters:
- never-contacted creators who are now under 5K or over 50K followers
- no new reel for over 60 days
- followers up or down by 25% or more since the research
- the account went private
- the profile didn't load (a renamed or deleted handle does this): check the handle
- **posted a reel about LumeBook**: a reel since the first message whose caption, tags or collab names LumeBook or לומיבוק, linked on the chip (Must have › "Posted about LumeBook"). It stays English ("posted ... : https://") because the map finds it by that.
- The outreach status is never changed by the refresh: move a creator to Content created yourself when the chip shows a post.

## Steps

`$S` is the run's scratch folder. Commands run in `creators/creator-research/src/refresh`. If any script returns `stop`
(signed out, 429, checkpoint) or Instagram shows a login or challenge page, stop the whole refresh and report it; never
retry in a loop. Exports: the tab must be on `https://www.instagram.com/robots.txt` (same origin, nothing to click), then
one `browser_batch`: `computer` left_click in the middle of the page, then the export script. If the pasted file is empty,
run the export again.

1. Handles: `python3 -c "import json;print(json.dumps([c['h'] for c in json.load(open('../C_all.json'))]))"`
2. Built-in browser, `https://www.instagram.com/` (signed in). Run `window.__ALL=1;` followed by `clear.js`, then set
   `localStorage.__rf_todo` to the handles.
3. Run `collect.js` until it returns `done: true` (about 20 profiles per call; "page navigated" means a forced reload:
   just run it again).
4. Export the profiles: robots.txt, click, `export.js`. Bash: `LC_ALL=en_US.UTF-8 pbpaste > $S/rf.json; printf '' | pbcopy`.
5. `python3 comments.py todo $S/rf.json > $S/todo.json` (it says how many reels; at most 1,500 a run, creators with no
   number yet first; the rest wait for next week). On the robots.txt tab set `localStorage.__rc_todo` to the contents of
   `$S/todo.json`, then run `comments.js` until `done: true` (about 30 reels per call). Whenever a call returns
   `export: true`: click, `window.__XK="__rc_p_";` followed by `export.js`, paste to `$S/cm<k>.json` (k = 1, 2...),
   `python3 comments.py ingest $S/cm<k>.json`, clear the clipboard, run `clear.js`, carry on.
6. `python3 comments.py cand $S/cand` writes the comments to check in batches (`$S/cand/in/NNN.json`, about 350 each).
   Give each batch to a Sonnet subagent (Agent tool, model sonnet, several at once) with `VERIFY_BRIEF.md` and the two
   paths; it writes `$S/cand/out/NNN.json`. Then `python3 comments.py apply $S/cand`. A batch with no labels keeps its
   rule labels until a later run checks it.
7. `python3 refresh.py $S/rf.json --db ../../state`, then `cd .. && python3 build2.py` (it must end with "0 problems").
   Do not republish the old map artifact (frozen since 20 Oct 2026); reload the open map page to see the new numbers.
8. `window.__ALL=1;` + `clear.js`, close the Instagram tab, clear the clipboard.
9. Report: profiles read and not loaded, flags by kind, anyone who posted about LumeBook (with the link), never-contacted
   creators now under 5K or over 50K, reels whose comments were read and how many waited for next week, comments checked
   and purchase signals found.

Test run without touching the map: `comments.py ... --cache $S/comments.json` and
`refresh.py ... --out $S/out --cache $S/comments.json` write somewhere else.

## Files

| File | What |
|---|---|
| `collect.js` | profiles: followers, median views, last reel, reels about LumeBook, the 12 newest reels' views, likes and comments |
| `comments.js` | the first page of comments of each reel in `__rc_todo`; no commenter names are kept |
| `export.js`, `clear.js` | clipboard export and localStorage clean-up |
| `comments.py` | which reels to read, rule labels, the batches to check and their labels; cache in `cache/comments.json` (not in git; a reel's comment text is dropped once it is checked) |
| `VERIFY_BRIEF.md` | the brief for the comment check |
| `pics.js`, `pics.py` | profile pictures for the cards (8 Nov 2026): `pics.js` in the signed-in built-in browser collects the picture links (`__pic_todo` handles, run until `done:true`, export with `export.js` and `window.__XK="__pic_out"`), `/usr/bin/python3 pics.py FILE.json [--missing]` saves 120px JPEGs to `creators/creator-research/avatars/<handle>.jpg` (Instagram's links expire). Not part of the weekly run yet; new creators show their initial until their picture is added. 11 handles never loaded (the page reloads on them), they keep the initial |
| `refresh.py` | writes `latest.json` (read by `../build2.py`) and `history/<date>.json` |

## Cost (estimates, 24 Oct 2026)

Measured on 5 creators: about 1 reel of comments per second, about 2 comments to check per reel, and about 1.3 new reels
per creator per week. With about 450 creators: the first run reads 1,500 reels (about 25 minutes) and checks about 3,000
comments (about 9 Sonnet batches); the backlog of about 5,000 reels clears in about three weeks; after that a week is
roughly 600 to 700 new reels and 1,200 to 1,400 comments to check (about 4 batches). The profile read is about 20
profiles per 30 seconds (about 12 minutes for 450).
