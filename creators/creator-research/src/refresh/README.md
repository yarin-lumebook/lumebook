# Weekly refresh

Re-reads every creator in the map from their public Instagram profile, read only, and shows what changed on the map.
It runs as the weekly scheduled task `lumebook-creator-refresh` (Sundays 10:00). It never opens DMs or email and never sends anything.

What it does:
- Fresh **followers, median reel views and last reel date** replace the research numbers on the map (C_all.json keeps the original research record).
- Flags shown as chips on the creator's card, and under Must have › "Flagged by the weekly refresh" in the filters:
  - never-contacted creators who are now under 5K or over 50K followers
  - no new reel for over 60 days
  - followers up or down by 25% or more since the research
  - the account went private
  - the profile didn't load (a renamed or deleted handle does this): check the handle
  - **posted a reel about LumeBook**: a reel since the first message whose caption, tags or collab names LumeBook or לומבוק, linked on the chip (Must have › "Posted about LumeBook")
- The flags are written in Hebrew (20 Oct 2026), except the posted one: the map finds that chip by its English start ("posted") and the ": https://" before the link, so it stays English until `template.html` matches a Hebrew version too.
- The outreach status is never changed by the refresh: move a creator to Content created yourself when the chip shows a post.

How to run it by hand:
1. Built-in browser, a signed-in instagram.com tab. `localStorage.__rf_todo = JSON.stringify([...handles])`, the handles from
   `python3 -c "import json;print(json.dumps([c['h'] for c in json.load(open('C_all.json'))]))"` run in `src/`.
2. Paste `collect.js` into javascript_tool and run it again until it returns `done: true` (about 20 profiles per run).
3. Copy `localStorage.__rf_out` out (click the page once, then a hidden textarea with `document.execCommand('copy')`,
   then `LC_ALL=en_US.UTF-8 pbpaste > /tmp/rf.json`; clear the clipboard afterwards).
4. Nothing to export: the outreach records are read straight from `creators/creator-research/state/outreach.json` (since 20 Oct 2026).
5. `python3 refresh/refresh.py /tmp/rf.json --db ../state`, then `python3 build2.py`. Do not republish the old map artifact (it is frozen); the map is served from the project server. Reload the open map page to see the new flags.
6. Remove the `__rf_*` localStorage keys.

`latest.json` is what the map shows; `history/<date>.json` keeps every week.
