# Daily post numbers (books tab)

Since 5 Nov 2026 the creator map's "ספרים שנוצרו" tab has a post link field (column "פוסט ודרייב"): Yarin pastes the link to the creator's post
about the book (saved on the row as `post` in `state/settings.json` `main.books`; pasting a link also ticks "תוכן עלה").
Every day the scheduled task `lumebook-creator-posts-daily` (09:00) reads each linked post on Instagram, read only, and
the table shows its views, likes and comments as three small cubes under the creator's name, with the change since the
previous reading. The cubes at the top of the tab add them up.

Only Instagram posts and reels can be read (`/p/`, `/reel/`, `/reels/`, `/tv/` links). A story disappears after 24 hours,
so a story link shows a note instead of numbers. Views exist for reels only; a photo or carousel shows likes and comments.

## Files

| File | What |
|---|---|
| `posts.py todo` | the posts to read, from the books rows: `[{"c": shortcode, "h": owner handle}]` (the handle in the link, else the row's creator) |
| `posts.js` | runs in the built-in browser on instagram.com (signed in): opens each owner's reels tab (4 pages, then 2 of the posts grid) once and takes the post's `play_count`, `like_count`, `comment_count` from what Instagram's own page loads, like `../refresh/collect.js` |
| `posts.py ingest <file>` | saves the result into `state/posts.json` (shortcode: `h`, `on` posted, `d` read, `v` views, `l` likes, `m` comments, `hist` one row per day `[date, v, l, m]`, `miss` when it was not found) |
| `posts.py show` | the saved numbers, one line per post |

`state/posts.json` is written only by `posts.py`; the map reads it from the project server (`state/posts.json` next to
the map page, fetched again at most every 5 minutes while the tab is open). A post that is not found keeps its last
numbers and the row says on which day it was missed (a deleted post, an archived one, or one deeper than 4 pages of reels).

## Steps (what the daily task does)

1. `cd creators/creator-research/src/posts && python3 posts.py todo > $S/todo.json`. If it prints 0 posts, stop: nothing to read.
2. Built-in browser: `navigate` to `https://www.instagram.com/` (a fresh page, so every profile loads anew).
3. `javascript_tool`: `window.__PP=<contents of $S/todo.json>;` followed by the whole of `posts.js`. Run `posts.js` alone
   again until it returns `done: true` (a call returns within about 40 seconds; each profile is opened once). If it returns
   `stop`, or Instagram shows a login or challenge page, stop and report it. Never retry in a loop.
4. Save the `out` object of the done call to `$S/out.json`, then `python3 posts.py ingest $S/out.json`.
5. Report the lines `ingest` prints, and every post that was not found.

Read only: it never follows, likes, comments, sends or opens messages, and never signs in or out.
