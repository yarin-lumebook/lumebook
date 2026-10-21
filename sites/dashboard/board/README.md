# Dashboard work board

The dashboard's default view since 19 Oct 2026 (`#board`): a canvas of cards, areas (frames) and connections over the project's real resources, with a tools dock, templates, search, filters, a list view, undo/redo and saving. The older views (overview, plan, creators, signups, carousels, competitors, research, sync, sites) are unchanged and one click away in the menu.

| File | What it is |
|---|---|
| `board.js` | The board (no framework, no library). Loaded by `../lumebook-dashboard.html` after the dashboard script. |
| `board.css` | Board styles, on the design system tokens and `lb-` components (`../design/lumebook.css`). White and black modes (the switch in the sidebar). |
| `content.json` | Hand-written Hebrew: titles for discovered resources, the first board's areas and what goes in each, starter cards, prompts, the five built-in templates. |
| `catalog.py` | Builds the resource catalog from `lumebook.json`, `shared/facts.json`, `media/README.md` + `media/projects/`, `carousel/carousel-pipeline/approved/`, `shared/brand/` and `content.json`, lays out the first board, writes `seed.js`. Component `board-seed` in `lumebook.json`, so `ripple` reruns it. |
| `seed.js` | Generated (do not edit): `window.LB_SEED` = catalog, first board, templates. |
| `dev/mock-artifact.js` | Test harness for the artifact-database path (see below). Not deployed. |

## Where edits are saved

| Where the page runs | Saved in | Shown as |
|---|---|---|
| The artifact (claude.ai), with the `db` capability | The artifact's database: head `boards/main`, parts `boards/main/parts/<slot>-<n>` | "נשמר בלוח ב-Claude" |
| The read-only Vercel copy, the local project server, a file | This browser's `localStorage` (`lb-board:v1:static` or `:page`) | "נשמר במכשיר הזה" |

- Nothing claims more than that. The artifact board is shared across the devices where Yarin opens the artifact in Claude; the Vercel copy never sees it, and a browser-saved board never reaches the artifact. Moving a board between them: More (⋯) → export JSON, then import.
- The morning refresh writes only `snapshot/latest` and `history/<date>`; the page itself writes `tracker/state` (ticks, creator stages, counters). The board never writes any of those, and they never write `boards/`. `build_site.py` does not export `boards/` into the public Vercel copy.
- Each save writes the whole board into a new slot name (`r<rev><tab>`), in parts of at most about 180 KB (a db document holds 256 KiB), then moves the head. The previous version stays as the fallback (`head.prev`); older ones are deleted after the next save, and orphaned parts (a save that lost a conflict) are swept at most once a day.
- Saves take the head's short lease (`acquire`, 4 s) and check that no other tab or device saved past the version this page loaded or last saved. If one did, a banner asks: load the other version, or keep mine (saved on top; the other one stays as the fallback). Nothing is overwritten silently.
- A failed save shows "השמירה נכשלה" and retries (transient errors); edits stay in memory, and the browser asks before closing the tab. A save that the db refuses for permission makes the page read-only.
- Every board is versioned (`schema: 1`), validated and cleaned on load and import (ids, sizes, link protocols: only `https`, `http`, `mailto` or a relative project path; HTML is always shown as text). Migrations: `MIGRATIONS` in `board.js`; the raw board is kept in `localStorage` before migrating. Up to 6 local backups per browser (every 10 minutes of work, and before import, reset or restore): More → backups.
- Uploads never go into the board JSON. In the artifact, the `assets` capability (when declared) stores the file in the artifact's asset store; on the project server, `POST /api/media-inbox` saves it in `media/inbox/` (the unsorted folder of `media/README.md`; same-origin only, media types only, never overwrites). The Vercel copy has no upload. A dialog says where the file goes before anything is sent.

## What the board shows from the project, and what stays yours

- A card from the project has `ref` (a stable resource id such as `cmp:creator-map`, `media:2026-10-16-dj-ben-reel`). Its title, notes, tags, position and size are the board's; the panel's "מהמקור" section (read-only) shows the source title, summary, links, path, publish state and registry relations. Renaming a card never renames the source.
- Metric cards (`metric`) read the morning snapshot and the tracker; "יעד שלי" on a card is the board's own note. View cards open a dashboard view.
- New resources (a new artifact in `facts.json`, a new media job) arrive through the snapshot's catalog and wait in the dock's "חדש" tab. Nothing is placed on a saved board automatically.
- Registry dependencies (`lumebook.json` feeds) are drawn dashed with "מזין", only between cards in the same area on the first board; the toolbar's dependency button hides them, and the card panel lists all of them.
- Local tools (`facts.local_tools`: Hook Studio, the project server): on the project server the board pings them through `/api/local-tools`; elsewhere it tries from the page and says "לא זמין מכאן" when the browser blocks the check; the snapshot records whether each answered at refresh time. The page never runs a command: commands and prompts are copied. Hook Studio is a login item; the board never starts a copy.
- Files that only exist on the Mac (media, docs, research pages) preview and open only on the project server (`python3 tools/lumebook.py serve`, then `http://localhost:8780/sites/dashboard/site/lumebook-dashboard/`); elsewhere the card says so and offers the path.

## Differences between the copies

| | Artifact | Vercel copy | Project server |
|---|---|---|---|
| Board saved | artifact db, every device | this browser only | this browser only |
| Snapshot | live from the db | built in at deploy | built in at build |
| Ticks, stages, counters (tracker) | editable | read-only | read-only |
| Local media preview | no (the files are on the Mac) | no | yes |
| Upload | with `assets` declared | no | to `media/inbox/` |
| Local tool check | from the page, often blocked | from the page, often blocked | definitive |

## Publishing the artifact (only when Yarin asks)

Publish `sites/dashboard/lumebook-dashboard.html` to https://claude.ai/artifact/3y8LwbxtTNQW2HAL479aSQ with the files `design/lumebook.css`, `design/categories.css`, `img/logo.png`, `board/board.js`, `board/board.css`, `board/seed.js`. Capabilities: keep `db`, `user` and `mcp` (Google Drive `read_file_content`); add `assets` for uploads and `downloads` for a saved export file (both optional: without them the board hides upload and falls back to a browser download or copy). Then `python3 tools/lumebook.py ack dashboard --published`. If the board files are missing, the page says so and opens the overview.

## Rebuilding

```
python3 sites/dashboard/board/catalog.py      # seed.js (ripple does this when its sources change)
python3 sites/dashboard/build_site.py         # static copy in site/lumebook-dashboard/ (copies the board files)
python3 tools/lumebook.py serve               # local preview: /sites/dashboard/site/lumebook-dashboard/
```

## Testing the artifact path

On the project server, open any page (for example `/tools/`), paste `dev/mock-artifact.js` into the console, then `await H.open()`. The built dashboard runs in a full-window frame with a stand-in db that follows the db contract (paths, `onSnapshot`, `acquire`, 256 KiB per document, `invalid_argument`). Checked on 19 Oct 2026: first-run seeding into `boards/main`, each save keeping the previous version as the fallback, a failed head write (honest error, automatic retry), a torn live version (falls back to the previous one, says so, next save supersedes it), a save from another device (loads by itself when nothing is pending; banner when something is), a 900-card board in 5 parts, a read-only viewer, and the dashboard's own documents untouched. Remove `localStorage.__mockdb` afterwards.
