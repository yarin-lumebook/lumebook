# Social proof (הוכחה חברתית)

Every good review and comment on LumeBook as a screenshot, tagged by theme and buying intent, and every real photo or video of a child with their LumeBook book. Page: http://localhost:8780/media/projects/2026-11-15-social-proof/social-proof.html (local only). Built 15 Nov 2026; updated every day at 06:30 by the scheduled task `lumebook-social-proof-daily`. Incremental: add only what is new, never rebuild from scratch.

## Files

| File | What |
|---|---|
| `data.json` | The source: `reviews[]`, `kids[]`, `drive` (folder ids), `gaps` (sources that could not be read, Hebrew) |
| `removed.json` | Cards Yarin removed on the page (`review:<id>`, `kid:<file name>`). Never add them back or use them |
| `build.py` | Builds `social-proof.html` (INTENTS, creators, card builders). Run through `python3 tools/lumebook.py build social-proof` so the edit button changes stay |
| `reviews/` | Screenshots: `google-review-NN-S-stars.png`, `instagram-<shortcode>-N.png`, `facebook-<post>-N.png`, `whatsapp-*` |
| `kids/`, `kids/thumbs/` | Local copies and thumbnails of the kid photos and videos |

Row shapes: copy the neighbouring rows. A review row has `id, platform, kind, file, author, when, stars, text (word for word), themes, url, intent (want, bought, share, praise), creator, note`, plus `drive` (the id of its first Drive copy) for rows added by the daily run. A kid row has `name, type, source (creator, customer, unknown), folder, desc (one Hebrew line), drive_src, drive, local, thumb, creator`.

## Daily run, as run on 16 Nov 2026

1. **Load** `data.json` and `removed.json`.
2. **Instagram** (built-in browser, signed in as Yarin, read only).
   - Creator reels: `creators/creator-research/state/posts.json` keeps a comment count per reel per night (`hist` rows `[date, views, likes, comments]`). Only a reel whose count went up since the last run needs opening.
   - Our own posts: open https://www.instagram.com/lumebook.il/ and open each post from the last few days. `get_page_text` shows the like count only; a reel with comments shows its comments in the side panel ("No comments yet" otherwise). The grid shows about 12 posts and does not load more.
   - Already covered posts: to find new comments, open the post and run JS that scrolls every scrollable box in `main`, clicks the "Load more comments" buttons, then lists `main time[datetime]` and counts those newer than the last run.
3. **Google reviews**: open the Maps place (`https://www.google.com/maps/place/LumeBook+%7C+%D7%9C%D7%95%D7%9E%D7%99%D7%91%D7%95%D7%A7/data=!4m8!3m7!1s0x2e132a90c4c0badb:0x72dd82a98ee1c9b3!8m2!3d31.4062525!4d35.0817938!9m1!1b1!16s%2Fg%2F11wvtfydkb?hl=iw`), sort by newest (the sort button, then the second `menuitemradio`), read the rows with JS (`[data-review-id]`, name `.d4r55`, stars `[role=img][aria-label]`, time `.rsqaWe`, text `.wiI7pd`) and compare authors with the google rows. Yarin Bruner's own review is left out. The plain Google search page no longer shows the review panel.
4. **Facebook**: the mentions page https://www.facebook.com/profile.php?id=61575235094083&sk=mentions (newest first; Daniel Ben Zino, 37 weeks, was the top one on 16 Nov). `&sk=reviews` returns 404. The page feed is virtualised and loads slowly: scroll in steps of about 900px with 2 to 3 seconds between them and read with `get_page_text`.
5. **Screenshots** (the built-in browser has no save button, but every screenshot and zoom is saved to the session's `tool-results` folder and the path is printed as `Image: source: ...png`):
   - JS: find the review or comment element, `cloneNode(true)` it into `<div id="__ov" style="position:fixed;left:0;top:0;z-index:2147483647;background:#fff;padding:12px;width:420px;direction:rtl">` and set `zoom` so it is about 1000 page pixels wide (the window is 1024 x 768, device pixel ratio 1).
   - `computer zoom` on the overlay's region (screenshot frame 800 x 600) gives a crisp PNG of about 780px wide; crop off any edge with `ffmpeg -i SRC -vf crop=W:H:0:0 reviews/<name>.png`. The 15 Nov files are wider (about 1140px) because they were taken in Chrome with `save_to_disk`.
6. **Drive** (connector): `search_files` with `createdTime > '<last run>' and (mimeType contains 'image/' or mimeType contains 'video/')` finds every upload in one query; anything in the result outside our own copy folders is a candidate. Raw folders: `חומרי גלם` `1YxBywPRxgPVE6MHv3VuVwh3iNZiXuGjM` and `תוכן לקוחות ויוצרים` `1C-VjkLdTq7xM830Txm_ulbQrS2E14vml` with their creator subfolders. Compare ids with `kids[].drive_src`. `כפילויות תמונות שיווק - 2026-11-15` (`1UWMA_Ex6LveujHTpftkF8pr1c_gNcTcH`) holds duplicates moved there on 15 Nov 2026, including 60 of our `drive_src` originals: skip it. The thumbnail address (`drive.google.com/thumbnail?id=...`) works only for files Drive made a thumbnail for.
7. **Drive copies of a new review screenshot**: upload it once with `create_file` (`base64Content` as `sha256:<hash>:<absolute path>`, `disableConversionToGoogleType` true) into its first theme folder, then `copy_file` into its other theme folders and its intent folder under `לפי כוונת קנייה` (`1 - רוצים לקנות` `1K33h4hF21Z30sSTZ-nTRher59LXbmGci`, `2 - קנו או הזמינו` `15f9AYF8Ei7gAt-7057KwMpRflNxV_PVa`, `3 - מעבירים הלאה או ממליצים` `1MVMj5XJYII6OkpD67bnnKS878XOWV9bq`, `4 - מחמאה בלבד` `1V5oGDpCwNhZ_rJixbScU2t3wIHkxj71u`). Title: `<פלטפורמה> - <author> - <5 כוכבים | id>.png`, e.g. `גוגל - Maayan Kabra - 5 כוכבים.png`. Theme folder ids are in `data.json` `drive.theme_folders`. Kid files: `copy_file` the original into `drive.kids_photos` or `drive.kids_videos`; over 10 MB goes to `gaps`.
8. **Add rows** to `data.json` (a Google row goes after the last Google row; keep the file's one-space indent), then `python3 tools/lumebook.py build social-proof`.
9. **Check** the page: number of review cards equals the rows, no image with `naturalWidth` 0 (set `loading=eager` first), no console errors.
10. Update `gaps` only when a source could not be read; update this README only when a step changed.

Hard rules: every platform read only (sort and "load more" clicks only); skip a source that shows a login, checkpoint or 429; never move, rename or edit a Drive original; no commit (the 00:00 job commits), no artifact publish, no `ack`, no new Drive folders.
