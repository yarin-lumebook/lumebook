# QA audit of 08 / 11 / 2026: changes and rollback

Made by Claude during the full-project QA audit, between 23:00 and 00:00 on 08 / 11 / 2026. The midnight job
(`tools/nightly_commit.py`) commits everything uncommitted, so these changes land in the same nightly commit as the
work that was already uncommitted that evening. This file and `audit-2026-11-08-changes.patch` keep them apart.

Rollback of the code changes: `git apply -R docs/audit-2026-11-08-changes.patch` (checked to reverse cleanly on
08 / 11 / 2026 23:25). The items marked "not in the patch" are undone by hand as described.

## Changes

| # | File | What and why | Checked |
|---|---|---|---|
| 1 | `sites/dashboard/build_site.py` | `public_snapshot()`: the Vercel copy of HQ no longer embeds the store's ambassadors person by person (names, Instagram handles, personal-link slugs, open payout requests); counts and totals stay, plus `payouts_open_count`. An open-payout attention item keeps its place without the name. HQ on the project server reads the rows live from `/api/home`; the claude.ai artifact from its own database | `sites/dashboard/tests/test_build_site.py`; the real snapshot checked in memory: no ambassador name, handle or slug left |
| 2 | `sites/dashboard/lumebook-dashboard.html` (not in the patch) | Reads `payouts_open_count` when the rows are absent; the static copy says the list is only on the local and Claude HQ; name and handle cells are `translate="no"`; its `lumebook-i18n` block re-baked after item 3 | By reading; the page block holds no ambassador name |
| 3 | `shared/i18n/pages/sites/dashboard/lumebook-dashboard.html.json` (not in the patch) | 19 entries holding ambassador names or handles removed (16 `en`, 3 `he`); they came from the שגרירים table and were baked into the public page | Count before and after |
| 4 | `.githooks/pre-commit` | Restored `staged=$(git diff --cached --name-only)`; without it the hook never blocked a `*sheet.md` export | Old and new hook run in a throwaway repo: old one let a sheet export through, new one blocks it |
| 5 | `.gitignore` | `creators/creator-research/avatars/` (426 creators' Instagram profile pictures, re-downloadable) and heic, webm, m4v and avif files under `media/` stay out of git, as the file's own rule says for raw media | `git check-ignore` |
| 6 | `carousel/carousel-pipeline/scripts/review_server.py` | Carousel Machine answers only requests with its own Host, and a POST only from its own pages, the project server's pages or no Origin at all (the :8780 forward, scripts, tests). Any web site could otherwise POST there (save, approve, authorize spending, send to Postiz) | `carousel/carousel-pipeline/tests/test_local_only.py`, full suite. Live only after `python3 carousel/carousel-pipeline/scripts/hook_studio_login.py restart` (not run) |
| 7 | `tools/lumebook.py` | Project server: every method refuses a foreign Host (DNS rebinding could read the whole folder, `.git` and `creators/correspondence` included). `ack ID --published/--deployed` keeps a failed build's to-do and a good build clears it. Asia/Jerusalem time; to-do times compared as times | `tools/tests/test_pending.py`; AST check that all four handlers check the Host first; `check` clean. Server part live only after `python3 tools/serve_login.py restart` (not run) |
| 8 | `tools/site_editor.py`, `tools/account_handoff.py`, `sites/dashboard/refresh.py` | Asia/Jerusalem instead of a fixed UTC+2 or UTC+3 (an hour off half the year) | Compiled; offset test in `tools/tests/test_pending.py` |
| 9 | `shared/facts.json` | `local_tools.project_server` said to start the server from a terminal; it is a login item since 21 Oct 2026 and a second copy must never start. Now `serve_login.py status/restart` | `check` clean |
| 10 | `research/israeli-product-reels/src/scripts/series-2026-11/reels.py` | Price rule: מעולה, לפעולה, להעלות no longer fail it; ש״ח with gershayim, משלוח חינם and דמי משלוח now do | `tests/test_lint_rules.py` there; no current reel newly fails |
| 11 | `research/israeli-product-reels/src/scripts/series-2026-11/reel_make.py` | The transcript is made again when `voice-studio.wav` changes (hash in `words-raw.json.wav-sha1`), so captions follow a new take. The first make of each existing reel transcribes once more (local, no cost) | `tests/test_transcript_cache.py` there |
| 12 | `carousel/carousel-pipeline/scripts/openai_generate.py` | An unreadable or cut-off answer after the request went out counts as spent at the estimate; a failed crop after a paid picture is logged at its measured cost. Before, both left the job "running" with nothing in the spend log | `carousel/carousel-pipeline/tests/test_spend_log.py` |
| 13 | `carousel/carousel-pipeline/scripts/postiz_export.py` | A second send keeps the earlier sends in `postiz.json` (`previous`), so a duplicate post's id is not lost. It does not block a second send | `carousel/carousel-pipeline/tests/test_postiz_history.py` |

## Follow-up of 09 / 11 / 2026: creator outreach off the public HQ copy

Yarin answered the open question "strip creator outreach handles and counts from the public HQ copy too?" with "Yes, strip
them". These changes came after the midnight commit `8f0c811`. Rollback of the code: `git apply -R docs/audit-2026-11-09-creators.patch`.

| # | File | What and why | Checked |
|---|---|---|---|
| 14 | `sites/dashboard/build_site.py` | `public_snapshot()` also strips the creator outreach work: the 16 tracked creators (handles, names, contact channels), the MeBook conflict list, `with_direct_contact_hint`, every count on the home's creator block (contacted, in process, reply rate, books out, follow-ups and reminders due, post views) with its follow-up and reminder name lists, and the home's two creator attention items. The map's research totals stay (437 creators, audience bands, types, research passes). `public_tracker()` drops the tracker's per-creator stages and its outreach count. `public_words()` drops from the page's baked words block any entry that names a tracked creator or an ambassador (`private_strings()`, read from the full snapshot): the dictionary fills itself from what the local HQ shows and the server bakes it into the page, so a stale tab had already brought 6 contact channels back within minutes | `sites/dashboard/tests/test_build_site.py` (11 tests); the built HQ: no creator or ambassador name, handle, slug or contact channel (the two matches are Yarin's own name and handle in the test-row filter) |
| 15 | `sites/dashboard/lumebook-dashboard.html` | The built copy is both the Vercel copy and the local HQ (the project server opens `sites/dashboard/site/lumebook-dashboard/`). On the project server it now loads the full snapshot and tracker from `/sites/dashboard/out/` (`loadFullSnap()`), so the local HQ keeps every number and the tracked list; on Vercel that fetch fails and the stripped one stays, with "only on the local and Claude HQ" notes where the outreach numbers and the list were, the list's search and filter hidden. Everywhere: creators' handles in the two creator alerts are drawn outside the language switch, the name and contact cells are `translate="no"`, and the stage picker is labelled by the creator's cell instead of an `aria-label` holding the handle. Its `lumebook-i18n` block re-baked after item 16 | Stripped copy rendered from a scratchpad build on a spare port (notes and research charts, no script errors); local HQ on :8780 after `python3 tools/lumebook.py build dashboard`: 6 creator numbers, 16 rows, stage legend, both creator alerts, no console errors; no creator string came back into the dictionary after loading it |
| 16 | `shared/i18n/pages/sites/dashboard/lumebook-dashboard.html.json` (not in the patch) | 39 entries holding creators' handles, names or contact channels removed (33 `en`, 6 `he`); the 6 `he` ones came back once from a tab still running the old build and were removed again | Count before and after; the page block holds none |

The local HQ was rebuilt (`python3 tools/lumebook.py build dashboard`). Deployed to Vercel on Yarin's go ("Deploy now") with `python3 tools/lumebook.py deploy dashboard` on 09 / 11 / 2026 at 11:50; the live page was fetched and checked: no tracked creator, conflict, outreach count, creator attention item or ambassador row, only the two owner matches in the test-row filter, and its creators view shows the notes with no script errors.

## Moves (not in the patch)

| From | To | Rollback |
|---|---|---|
| `sites/dashboard/site/lumebook-dashboard/board/` (stale copy of the retired work board inside the Vercel deploy folder; its `seed.js` held the retired Form's edit address and Sheet and Drive links) | `_to-delete/sites/dashboard/site/lumebook-dashboard/board/` (line added to `_to-delete/README.md`) | Move it back |

Nothing else was moved. The loose files in `research/` and `docs/` are linked from built pages and the research hub, so moving them needs rebuilds; they stay where they are.
