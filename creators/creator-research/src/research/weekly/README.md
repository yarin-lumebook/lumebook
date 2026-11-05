# Weekly creator search (every Saturday night)

Since 24 Oct 2026 the map grows by up to 100 creators every Saturday at 21:00, run by the scheduled task
`lumebook-creator-map-weekly` (Yarin: "i want the creator map to add 100 more every Saturday night"). Each run is one
pass: pass 6 on 24 Oct, then 7, 8 and so on. The method is the fourth pass's (18 Oct), turned into files:

| File | What it does |
|---|---|
| `weekly.py next` | the pass number for this run, and whether a weekly pass already added creators today |
| `weekly.py prep` | prints the javascript that puts the seeds (every creator in the map, with its Instagram pk when known) and the known list (map, removed, excluded) into the Instagram tab |
| `chain.js` | Instagram's similar-accounts list for every seed (`/api/v1/discover/chaining/`, 4 at a time); seeds without a pk get it from their profile page |
| `screen.js` | rounded followers and bio of every new account from its profile page, 16 at a time; keeps 4,500 to 55,000 |
| `export.js` | copies the finished step's result to the clipboard |
| `weekly.py shortlist` | drops known creators, accounts reviewed in the last 90 days (`reviewed.json`), non-Hebrew and off-topic bios; writes `review.txt`, most suggested first. `|LIKE <handle>` marks a handle that may be a map creator renamed |
| `read.js` | the full profile of each pick: exact followers, bio, bio links, category, the latest 12 reels' views and dates |
| `weekly.py check` | the map's rules (public, 3+ reels, a reel in the last 90 days, not already in the map, also when renamed) and the admission bar (`gate.py`), and writes `../pass<N>_raw.json` |
| `gate.py` | the admission bar of 24 Oct 2026, read from `shared/facts.json` `creators.admission`; `check` and `../merge_pass.py` both apply it |
| `weekly.py queue`, `requests` | the handles waiting from the map's "הוספת יוצרים" button (read from `state/settings.json`, never written), and what happened to each (`requests.json`, built into the map) |
| `hop.js` | optional second hop from this run's picks when the first one is short |
| `clean.js` | removes the `__cw_*` localStorage keys |
| `../merge_pass.py <N>` | appends `../data<N>.py` to `C_all.json`, `contacts.json`, `kids.json` and the CSV; adds the reviewed accounts to `reviewed.json` |

## Order

All Instagram work is read only, in the built-in browser, signed in as Yarin: no follows, likes, comments, messages, DMs.
If a script returns `stop` (signed out, 429, checkpoint), stop the run and report it; never sign in or retry in a loop.
Work in a scratch folder (below: `$S`). Paste each `.js` file's full text into `javascript_tool`; each call works about 30 seconds.

1. `cd src/research/weekly && python3 weekly.py next` (not 0 already added today: stop). Note N.
2. Open `https://www.instagram.com/` (`preview_start` with the url). Run `clean.js`, then the line `python3 weekly.py prep` prints.
3. `chain.js` until `done: true` (about 6 calls), then `screen.js` until `done: true` (about 10 calls).
4. Export: navigate the tab to `https://www.instagram.com/robots.txt` (same origin, same localStorage, nothing on it to click), then one
   `browser_batch`: `computer` left_click at the middle of the page, `export.js`. In Bash: `LC_ALL=en_US.UTF-8 pbpaste > $S/screened.json; printf '' | pbcopy`.
5. `python3 weekly.py shortlist $S/screened.json $S/r1` and read `$S/r1/review.txt` (about 500 lines on 18 Oct).
6. Pick every likely fit, up to about 300 (rules below; the admission bar lets through only about a third of them). Add every handle
   `python3 weekly.py queue` prints: Yarin added those with the map's "הוספת יוצרים" button; they skip the topic rules, not the bar. Navigate back to `https://www.instagram.com/`, set `localStorage.__cw_P` to their handles,
   `read.js` until `done: true` (a "page navigated" message is a forced reload: just run it again). Export as in step 4 into `$S/read.json`.
7. `python3 weekly.py check $S/read.json` (its OUT lines give the reason, the bar's included). If fewer than about 100 pass: on `https://www.instagram.com/` run `hop.js`, then `chain.js`,
   `screen.js`, export to `$S/screened2.json`, `python3 weekly.py shortlist $S/screened2.json $S/r2 --skip $S/r1/review.json`, pick,
   set `__cw_P` to the new picks only, `read.js`, export to `$S/read.json` (it holds both rounds), `check` again.
8. Write `../data<N>.py` with the best 100 of those that passed `check` (fewer if there are not 100; never pad, and never add one that failed), in the shape of `../data5.py`.
   Queued handles that passed come first and count toward the 100.
9. `cd .. && python3 merge_pass.py <N> --reviewed $S/r1/review.json[,$S/r2/review.json]`, then `cd weekly && python3 weekly.py requests $S/read.json`
   (what happened to each queued handle, shown in the map's add form), then `cd ../.. && python3 build2.py`
   (it also runs `test_kids_names.mjs`; it must say 0 problems).
10. `clean.js`, close the tab, clear the clipboard.

## Who gets in

- Israeli, writes in Hebrew, public, a reel in the last 90 days (`check` enforces the numbers).
- The admission bar (Yarin, 24 Oct 2026; `gate.py`, numbers in `shared/facts.json` `creators.admission`), all five:
  5,000 to 50,000 followers; median views 2,000 or more; 0.4 views per follower or more; 9 likes per 1,000 views or more (was 10 until Yarin loosened it on 03 Nov 2026);
  1 comment per 1,000 views or more. Likes and comments are the median per reel over the 12 newest reels, like the card.
  A profile whose likes are hidden cannot show it meets the bar and stays out. `check` and `merge_pass.py` both enforce it.
  It only decides who joins: creators already in the map are never removed or changed because of it. A creator Yarin names by hand
  goes through the same bar; if one fails, tell him the numbers instead of adding it.
- The content is about children (about 0 to 10), parenting, child development, education, family outings or kids' activities, and
  there is a real person on camera or behind it. Parents, parent guides, child-development professionals, gan and teachers, special
  ed, dads, twins, grandparents, family travel, books and reading are the core.
- Left out, as in every pass: shops, venues, brands and deal pages; baby-sleep, birth, breastfeeding, pregnancy and nutrition
  accounts; people living abroad; teen-focused accounts; Arabic or Russian; accounts that say they do no collaborations;
  sensitive ones (memorial pages); anyone already in the map under another handle (check `|LIKE` lines and `check`'s "renamed?").
  `mor_knoll` is a MeBook conflict (on mebook.ai's tagged tab).
- About 80 clear fits and up to about 20 borderline ones is the usual mix; a borderline one says why in its risk note.

## Writing data<N>.py

Same shape as `../data5.py`: `N<N> = [(handle, name, code, role, ages, concept, risk), ...]` and `KIDS<N> = {handle: {...}}`.
All free text in Hebrew, following `../../hebrew-rules.md`; no em dashes; LumeBook never written as לומיבוק.

- `name`: the person's name in Hebrew letters as the profile writes it (a brand or couple name if that is the account).
- `code`: one of `CD PG GAN EL NC P PD PT PS TR SE HS BK CM GP SF` (meanings in `AR` in `merge_pass.py`), or `UX:<english description>`.
- `role`: what the bio says, ending `(מהביו)`. `ages`: the children the content is about, `2 עד 8`, or `לא צוין`.
- `concept`: one sentence, a LumeBook video idea that fits this creator (the child as the hero of their own book).
- `risk`: what to watch. The merge reads two things from it: write `מוכרת ...` (or `מוכר`, `מכירת`) when they sell their own
  books or products, and `סוכנות` or `ניהול` when an agency represents them. Views far above followers: say a fee is possible.
- `KIDS<N>`: only what the bio states: `n` total, `b` boys, `g` girls, `names` in Hebrew letters (`names_en` too when the bio has
  them only in English), `note`. Never infer a gender from a name; leave out what is not stated.
