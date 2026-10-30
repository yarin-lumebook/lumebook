# Account handoff: LumeBook moves to a new Claude account

Started 26 Oct 2026 from the old account (yarinbruner02@gmail.com). Yarin keeps working on the same Mac, in the same folder, with a different Claude account. The old account stays active, but everything should be run and edited from the new one.

New account's Claude: read this file top to bottom, then do part 3. Tick the boxes here as you go.

## 1. What carries over by itself (same Mac)

Nothing to do for these; they live on the Mac, not in the Claude account.

- The project folder, git and GitHub (`gh`), Vercel CLI, Google Drive for desktop.
- Claude Code memory (`~/.claude/projects/-Users-yarinbruner-Claude-Projects-Lumebook/memory/`, keyed by folder), `CLAUDE.md`, the project skills in `.claude/skills/`, the personal skills in `~/.claude/skills/`, `settings.local.json`.
- The fal-ai MCP server (user config in `~/.claude.json`). Check it in `/mcp`; sign in again only if it shows needs-auth.
- The login items and launchd jobs: project server (:8780), Carousel Machine (:8777), the 00:00 nightly commit, the GA4 jobs.
- The scheduled task files in `~/.claude/scheduled-tasks/`. Whether the desktop app shows and runs them for the new account is not verified: check in 3.7.

## 2. What belongs to the old account

| Piece | Old account (26 Oct 2026) | New account |
|---|---|---|
| claude.ai artifacts | 17 LumeBook artifacts, all in `artifacts.json` | 11 to republish, the Design System from its type, the creator map not at all, 4 optional |
| Dashboard database (work board, ticks, history) | exported to `db-export/dashboard/` (not in git) | restore into the new dashboard (3.3) |
| Cloud routine "Hook Studio weekly batch (cloud)" | Thursdays 19:00 UTC, environment with Full network; settings in `routine-weekly-batch.json` | recreate (3.6), then the old one goes off |
| Connectors | Google Drive, Gmail, Google Calendar, Notion, Claude Docs, Spotify | reconnect what is needed (Drive is required: the dashboard reads Drive) |
| Built-in browser sign-ins | Instagram, used by the Saturday creator task | check (3.7) |

The old account also owns 25 artifacts from before or outside this project (GA4 book, Ginzburg, portfolio, agency research, the September social and carousel workbooks; `Artifact list` there). They stay there unless Yarin asks to move them too.

## 3. Steps

### 3.0 Yarin, by hand, before the first session in the new account

- [ ] In claude.ai, signed in with the new account: Settings, Connectors: add Google Drive (required), and Gmail, Google Calendar, Notion if you still use them there.
- [ ] Claude desktop app: sign out, sign in with the new account.
- [ ] claude.ai/code with the new account: connect GitHub with access to `yarinbruner/lumebook`, and create a cloud environment with network access set to Full. Note its name.
- [ ] Open a session in this folder and say "continue the account handoff".

### 3.1 Check the account

- [x] `Artifact list` must not show the old artifacts (for example `3y8LwbxtTNQW2HAL479aSQ`). If it does, this is still the old account: stop and tell Yarin. (26 Oct: empty list, new account.)
- [x] `python3 tools/account_handoff.py status` shows what is left.

### 3.2 Republish, first pass

For each row in `artifacts.json` with `"action": "republish"`, in this order: dashboard, hook_studio, then the rest.

1. If it has a `component`, rebuild it first: `python3 tools/lumebook.py build <component>`.
2. Publish `file` as a new artifact (no `url`), with `files` (and `root` where given), `capabilities` where given, and `icon`. The carousel research page also takes every `research/carousel-research/img2/*.jpg` as `img2/<name>`.
3. `python3 tools/account_handoff.py set <key> <new link>`.

The Design System: start it from the Design System type (`Artifact quickstart`, intent `other`), run `python3 shared/design/build_ds_artifact.py <scratch folder>`, publish what it writes as the type says, then `set design_system <new link>`.

Leave `creators` alone: the live creator map runs on the project server since 20 Oct 2026 (`creators/creator-research/src/README.md`), and republishing the old artifact would lose the local data. Ask Yarin before doing any of the `optional` rows.

- [x] dashboard   - [x] hook_studio   - [x] design_system   - [x] creator_brief   - [x] reels_research   - [x] parent_communities
- [x] teardown   - [x] kids_lab   - [x] carousel_research   - [x] carousel_playbook   - [x] strategy   - [x] reels

(26 Oct: the Design System's two logos were uploaded to its new asset store; their new ids are in `shared/design/build_ds_artifact.py` LOGOS.)

### 3.3 Restore the dashboard database

One `ArtifactData` `batch` on the new dashboard link, every write `op: "set"` with `file_path` and no `if_version` (all new documents):

- `boards` / `main`: `docs/account-handoff/db-export/dashboard/boards/main.json`
- `boards/main/parts` / `r10tisimr5p0-0` and `r11ta8se1e6q-0`: the two files in `db-export/dashboard/boards/main/parts/`
- `tracker` / `state`: `db-export/dashboard/tracker/state.json`
- `history` / each date: the six files in `db-export/dashboard/history/`

Not `snapshot/latest`: write that one in 3.4 from a fresh build, so it carries the new links. Then open the dashboard: the work board must show the 21 Oct board (rev 11), not the starter board.

- [x] restored and checked (26 Oct: the page had already saved a starter board, rev 1, on its first load; it was overwritten pinned to that version, and `boards/main` reads back rev 11. Not yet checked by eye in the page.)

### 3.4 Swap the links and rebuild

1. `python3 tools/account_handoff.py swap --dry-run`, then `swap`. It rewrites the old links of moved artifacts in sources, `shared/facts.json`, `lumebook.json`, `CLAUDE.md`, the memory folder and the scheduled task prompts. It never touches build outputs, carousel drafts and approved runs, `_to-delete/` or this folder.
2. The SMM plan is done by hand: ask Yarin to close it in the site editor first, change the dashboard link in `sites/lumebook-smm-plan/index.html`, and add a dated line to `content.en.md` so the pre-commit mirror check passes in the same commit.
3. `python3 tools/lumebook.py ripple`, then `python3 tools/lumebook.py build <id>` for every changed page whose build is not auto (the dashboard: `build dashboard`).
4. Snapshot: `python3 sites/dashboard/refresh.py --skip-network` (or without the flag), then `ArtifactData` `set` `snapshot` / `latest` with `file_path` `sites/dashboard/out/snapshot.json` on the new dashboard.

- [x] swapped   - [x] SMM plan   - [x] rebuilt   - [x] snapshot (plus `history/2026-10-26`, as the old daily refresh did)

### 3.5 Republish, second pass

`python3 tools/account_handoff.py status` marks every artifact whose files changed since its first publish (the swapped links). Republish each one to its new link (`url`), `set` it again, and repeat until nothing is marked and no file still uses an old link. Then, for each component: `python3 tools/lumebook.py ack <component> --published`.

- [x] nothing marked   - [x] acked (not `creator-map`: it stays frozen on its old link)

### 3.6 The weekly cloud routine

1. `RemoteTrigger create` from `routine-weekly-batch.json`: name, cron, model, allowed tools, the repo as source, the prompt, and the new environment's id in place of `NEW_ENVIRONMENT_ID`. Tell Yarin the next run time it reports.
2. The old routine (`trig_01DpZqMp4fUTqkC67RHjTBok`) must be off, or both will push a batch on Thursday. If the old account did not pause it on 26 Oct, Yarin turns it off in claude.ai/code (Routines) signed in with the old account.

- [x] new routine created (28 Oct: `trig_013C3V1RxF3M38utouVepaVC`, env `env_015dxmDDSVHVQFvzuD7nrPNm`, next run Thu 29 Oct 19:03 UTC; repo moved to yarin-lumebook/lumebook, Claude GitHub app installed there)   - [ ] old routine off (30 Oct: it still ran on Thu 29 Oct and pushed batch/2026-11-30; the new account gets 404 for it. Neutralised instead: `cloud-weekly-prompt.md` now starts with a stop step. Yarin can still switch it off in claude.ai/code > Routines with the old account.)

(26 Oct: blocked. The new account has no cloud environment yet (`list_start_targets`: no_environment), so 3.0's third step is still open. The new account's routines list shows only "Morning brief".)

### 3.7 Scheduled tasks and the browser

- [ ] `list_scheduled_tasks` shows `lumebook-creator-map-weekly` (on, Saturdays 21:00) and `lumebook-creator-refresh` (off). If not, create them again from `~/.claude/scheduled-tasks/<id>/SKILL.md` with the same schedule (`0 21 * * 6`; the refresh `0 10 * * 0`, off).
  (26 Oct: the list was empty. `lumebook-creator-map-weekly` is recreated with the same prompt and schedule; the old account's copy of its folder is in `~/.claude/scheduled-tasks-old-account-2026-10-26/`. Creating `lumebook-creator-refresh` was refused by the permission check; its folder is back in place, still to be created and switched off.)
- [x] The built-in browser is still signed in to Instagram (read only; the Saturday task needs it). If not, Yarin signs in by hand. (26 Oct: not signed in. Yarin chose to switch `lumebook-creator-map-weekly` off for now instead (schedule kept); `lumebook-creator-refresh` is recreated as manual-only. To restart the Saturday runs: sign in to Instagram in the built-in browser, then switch the task back on.)

### 3.8 Finish

- [x] `python3 tools/lumebook.py deploy dashboard` (or let the 00:00 nightly commit deploy it) so the Vercel copy carries the new links. (26 Oct: deployed; the live page and /plan/ link only to new artifacts.)
- [x] Save a memory: the new account owns the artifacts since <date>; the old links in old carousel drafts and approved runs are history and stay. (26 Oct: `lumebook-account-handoff-2026-10.md` updated.)
- [ ] Remove the handoff pointer from `CLAUDE.md`, and move `tools/account_handoff.py` and this folder to `_to-delete/` with a line in `_to-delete/README.md`.
- [ ] Tell Yarin the old LumeBook artifacts can now be deleted from the old account at any time (only from there, signed in to it).

## Files here

| File | What it is |
|---|---|
| `artifacts.json` | Every LumeBook artifact of the old account: old link, what to do, what to publish, new link once set |
| `routine-weekly-batch.json` | The weekly cloud routine's settings, to recreate it |
| `db-export/dashboard/` | The dashboard artifact database as of 26 Oct 2026 (git-ignored, private) |
| `artifact-copies/` | Pages that only existed as artifacts (reels for Yossi, project map, hook strategy, Q4 brief, the 29 Sep deck) |
| `../../tools/account_handoff.py` | `status`, `set`, `swap` |
