# קהילות פייסבוק: the Facebook community tracker

Yarin, 15 Nov 2026: "i need a combined tool like the ugc creator map to track the parent facebook communities and ugc creators facebook communities posts and leads (take the groups from the researches we made)".

Since the same evening it is the creator map's third view (Yarin: "i want a separate view for creators, professionals and facebook communities ... merge the other session working on the facebook communities map"): open the creator map on the project server and press the Facebook icon in the middle of its top bar, or go straight to http://localhost:8780/creators/creator-research/lumebook-creator-map.html#fb-home. The old address, `community-tracker.html` (HQ's tool קהילות פייסבוק in topic קהילות), only forwards there (`#parents` becomes `#fb-parents`).

## Inside the creator map

- `build.py` `embed_parts()` gives `creators/creator-research/src/build2.py` the code (`page.js`, `page.css`), the data (`window.CT_*`, with `CT_EMBED`) and the markup: the side bar group, the top bar's search, post and lead buttons and save state, and the drawer, dialog, menu and toast. Change anything here, then rebuild the map (`python3 creators/creator-research/src/build2.py`); `python3 build.py` writes only the forward page.
- `page.js` in embed mode: the map owns the address bar (`#fb-home`, `#fb-parents?st=join`...) and calls `CT.show(view)` / `CT.hide()`; links the script draws (`#parents`) are rewritten to `#fb-parents` (`fbLinks`). The script handles only events inside `.ct-scope` (its page section, its top bar tools, its overlays, a community card in the reminders stack), so the map's handlers and its handlers never meet. Its side bar items use `data-ctroute` and `data-ctcnt`, never the map's `data-route` and `data-cnt`.
- One reminders stack for the three views: the map's תזכורות להיום and כל התזכורות read `CT.reminders()` and draw each with the map's strip (מחר, עוד 3 ימים, בוצע; a post: נבדק) over `CT.card(r)` (the group card, or a lead or post card made for the stack). `CT.done(key)`, `CT.snooze(key, days)`; after every save the script calls `CT_HOST.changed()` so the map redraws the stack and its count. The communities view has no reminders page of its own any more.
- Rules that are not `ct-` prefixed in `page.css` are scoped to `.ct-scope`, so nothing here restyles the map.

## What is in it

- **Groups**: the 295 Facebook groups of the parent community research (`research/parent-community/data.json`, every row whose platform is "Facebook group"), split into two tracks: 278 parent groups (a family shooting day at home for a free book, `shared/facts.json` `parent_shoot_offer`) and 17 UGC creator groups (finding creators). A group is UGC when its research segments include "Content creators and UGC" and no parent segment (`track_of` in `build.py`). WhatsApp, Telegram and Facebook pages stay on the research page. Groups the research rejected are hidden until "גם קבוצות שנפסלו במחקר" is ticked or the rating filter is set to נפסלו; a rejected group that was started always shows. Groups not in the research are added by hand ("קבוצה שלא במחקר"), saved with their own details (`custom`).
- **Stage per group**: עוד לא התחלנו, ביקשתי להצטרף, חבר בקבוצה, פניתי למנהלים, אישרו לפרסם, פרסמנו, לנסות שוב, לא מתאים. Each change writes a note, fills the matching date and sets the next step (3 days after a join request or an admin message, today to post or to message the admins depending on the research approach, 30 days for לנסות שוב). The first post in a group moves it to פרסמנו.
- **Posts**: date, link, which text, state (עלה, מחכה לאישור, לא אושר, הוסר), reactions, comments and shares typed in from Facebook (empty means not counted, never 0), the leads that came from it. A live post asks for a check after 2 days and after 7; a pending one after a day.
- **Leads**: a family or a creator who answered: group, post, channel, stage (parents: חדש, פניתי, ענו, מילאו טופס, נקבע צילום, צולם, לא מתאים; creators: the same with נשלחו פרטים, הצטרפו, נוצר תוכן), Facebook profile, Instagram handle (marked when the creator is already in the creator map), phone (WhatsApp link), email, city, kids or followers, next step, a log of changes.
- **Reminders**: every group's and lead's next step and every post check; בוצע clears it and logs it. Since the merge they sit in the creator map's one reminders stack with the creators and professionals (see below).
- **Message texts** (נוסחים להעתקה): per track, editable, saved. Parents start from the research drafts (`data.json` `drafts`: full post, short post, admin message) plus a reply to commenters; creators from a group post, an admin message and a reply written on 15 Nov 2026 with the creator offer from `shared/facts.json` (personal link with an audience discount, never a code). Copying from a group's drawer puts the group's city in place of `[העיר]`; "העתקת תשובה" on a lead puts the first name in place of `[שם]`.
- **Home**: six number cubes (hues from `shared/design/categories.json` set `community-metrics`; done and reminders in the status colours), both tracks' groups and leads by stage, today's reminders, the groups that brought the most leads (until there are leads: the research's Top 20 not started yet), the latest posts.

## Files

- `build.py`: reads the research, `research-he.json`, `shared/facts.json` and the creator map handles (`creators/creator-research/src/C_all.json`) and hands them with the code to the creator map (`embed_parts()`, above); until the evening of 15 Nov 2026 it wrote a page of its own, `community-tracker.html`, which is now a forward. `python3 creators/community-tracker/build.py` or `python3 tools/lumebook.py build community-tracker`. It stops if an em or en dash is in our own text (two groups have one in their own name; those are kept).
- `page.css`, `page.js`: the communities view. Tokens and `lb-` components only, white, RTL.
- `research-he.json`: the Hebrew of each group's posting rules, research note and contact line, and of the Top 20 reasons, translated from the English in `data.json` on 15 Nov 2026 (the English stays the source and shows under the Hebrew in the drawer). When the research adds groups, translate the new rows into this file; a group without Hebrew shows its English.
- `state/` (not in git): `tracker.json` and `backup/` (a copy of the file from before the first save of every day, 21 days kept).

## Where the work is saved

`tools/communities.py` through the project server, same-origin only:

- `GET /api/communities/state`: `{groups, posts, leads, settings}`.
- `PUT /api/communities/doc?path=<kind>/<id>`: one document (`groups/<id>`, `posts/<id>`, `leads/<id>`, `settings/main`), checked by `clean_*` (known stages and channels, dates as YYYY-MM-DD, links that start with https://, numbers or null, a post's and a lead's group must exist, a lead's post must exist); the body `null` removes it.

The file holds names and phone numbers of parents, so it stays on this Mac (`.gitignore`), is never published and never goes to the artifact database. Opened anywhere else (a file, another port without the endpoints), the page keeps its work in that browser only and the save mark says so.

After editing `tools/communities.py` or `tools/lumebook.py`: `python3 tools/serve_login.py restart`.

## Testing

Never against Yarin's file: start a server on a spare port with `LUMEBOOK_COMMUNITIES_FILE` at a scratch file, and the usual scratch overrides so the language switch translates nothing for real (`LUMEBOOK_I18N_DIR` at a copy of `shared/i18n`, `LUMEBOOK_I18N_QUEUE`, `LUMEBOOK_CLAUDE=/usr/bin/false`), then `python3 tools/lumebook.py serve --port 8791` and open the creator map there (`#fb-home`). The creator map's own data has no scratch switch on that server, so press nothing on a creator card while testing.

## Not built (yet)

- Facebook is read by hand: the page cannot read a group, a post's numbers or its comments. A Claude session with the built-in browser signed in to Facebook could fill posts and leads on request, read only.
- Leads do not flow into the creator map; a UGC lead whose Instagram handle is in the map gets a chip, במפת היוצרים, that opens that creator's card in the map (in the creators or the professionals view).
