# LumeBook project

Social media work for LumeBook (personalised kids' books, Israel). Solo SMM: Yarin. Hebrew audience copy, RTL.

## Layout (since 8 Oct 2026)

| Folder | What is there |
|---|---|
| `lumebook.json` | Component registry: every workstream, what it watches, how it builds, where it is published, what it feeds |
| `tools/lumebook.py` | Keeps components in step (see below) |
| `shared/facts.json` | Facts several components repeat: artifact and site URLs, Form/Sheet IDs, creator offer, key dates, barter list, baselines |
| `shared/brand/` | Canonical logos, mascot, fonts, carousel backgrounds, link-preview image |
| `docs/` | Product brief, Q4 strategy page, Hebrew carousel playbook, UGC research, Hebrew voice tool note, sales data and social decisions of 12 Oct 2026 (internal figures, keep them off the public plan page; `lumebook-sales-readout.html` is built from the md by `docs/src/build_sales_readout.py`, local only) |
| `prompts/` | The master prompts each workstream was built from (historical; paths updated to this layout) |
| `shared/design/` | The LumeBook design system: `lumebook.css` (tokens + `lb-` components), `design.py` (build helpers), `build_ds_artifact.py` (regenerates the Design System artifact) |
| `sites/` | `dashboard` (the all-in-one internal dashboard; artifact + lumebook-dashboard.vercel.app, which also serves the plan at /plan/), `lumebook-smm-plan` (the plan page, edited in the site editor), `lumebook-creator-brief` (the creator Reel brief, public at lumebook-creator-brief.vercel.app; built from `research/israeli-product-reels/creator-brief.md`, deploy with `python3 tools/lumebook.py deploy creator-brief`), `lumebook-ambassadors` (retired 11 Oct 2026: Yarin no longer uses the Vercel ambassadors site; the folder is an archive, do not deploy or maintain it) |
| `creators/` | `creator-research` (creator map; grows by up to 100 creators every Saturday at 21:00 through the scheduled task `lumebook-creator-map-weekly`, method in `src/research/weekly/README.md`; the same Saturday run then re-reads everyone and refreshes the six numbers on each card, `src/refresh/README.md`; the old Sunday task `lumebook-creator-refresh` is off), the signup Form's Apps Script, `correspondence/` (creator emails and DM recordings, one folder per handle, not in git) |
| `research/` | Competitor teardown, kids content lab (1.1 GB of raw video and frames, keep), carousel research, carousel playbook page, `carousel-audit` (every published carousel: Meta exports in, inventory, ranking and creative scores out; `src/audit.py import <export.csv>` after each export, `audit.py link <topic>` for UTM links; internal figures, local only, README there) |
| `carousel/` | `carousel-pipeline` (Carousel Machine: nightly at 22:00, hooks first, then content, then slide design; its drafts and paid `approved/` runs stay inside it) |
| `media/` | Every creative file (images, video, audio) since 14 Oct 2026: `projects/YYYY-MM-DD-slug/` one folder per job (reels, podcasts, character packs, stories, highlights, trend recreations, the frozen fal trial), `inbox/` for unsorted files. Index, rules and the cloud-archive steps: `media/README.md` |
| `_to-delete/` | Files the project no longer needs, under their original path, listed in its README. Yarin empties it; not in git |

One git repo for everything: github.com/yarinbruner/lumebook (private, since 8 Oct 2026; the four old repos are archived and their history is inside). Raw media is ignored (see `.gitignore`). The root `.githooks/pre-commit` enforces the SMM plan's English mirror and blocks Sheet exports.

Front door: the dashboard (https://claude.ai/artifact/3y8LwbxtTNQW2HAL479aSQ; read-only copy https://lumebook-dashboard.vercel.app). Its default view is the work board (`sites/dashboard/board/`, README there): board edits save to the artifact database under `boards/` (never `snapshot`, `history` or `tracker`), and on Vercel or the local server only in that browser. Design System reference: https://claude.ai/artifact/RjUuSdYDwaJe4HWyEErNmF.

Project skills: `.claude/skills/lumebook-carousel`, `.claude/skills/lumebook-hebrew-voice`. `.agents/skills/*` are symlinks to them; edit only `.claude/skills`.

## How components stay connected

```
python3 tools/lumebook.py status     # what changed, what it affects, open to-dos, consistency warnings
python3 tools/lumebook.py ripple     # same + rebuild safe local pages, sync brand copies, queue the rest
python3 tools/lumebook.py check      # registry, brand copies, offer wording, לומיבוק, em dashes, old paths
python3 tools/lumebook.py ack ID --published   # after republishing an artifact
python3 tools/lumebook.py map        # the dependency graph
python3 tools/lumebook.py build ID   # run one component's build
python3 tools/lumebook.py deploy ID  # Vercel deploy (dashboard)
python3 tools/lumebook.py serve      # one local server for the whole folder: http://localhost:8780/ (runs as a login item, see below)
```

- The project server (`tools/lumebook.py serve`, port 8780: the creator map saves through it, and it serves the dashboard and Carousel Machine) runs as a login item since 21 Oct 2026, like Carousel Machine: `python3 tools/serve_login.py status|restart|install|uninstall`. Run `restart` after editing `tools/lumebook.py`. Never start a second copy (a preview config, a terminal): only one process can hold the port. The `lumebook` preview config only attaches to it. Log: `~/Library/Logs/LumeBookServe.log`.
- The 08:14 dashboard task was deleted (Yarin, 20 Oct 2026); nothing runs `ripple` on a schedule now, so run it by hand for the dashboard's "סנכרון בין הרכיבים" panel to be current.
- After changing a component, run `ripple`. After republishing an artifact, run `ack <id> --published`.
- A new workstream gets an entry in `lumebook.json` (and in `shared/facts.json` if it has a URL). Use paths relative to this folder.
- A fact that more than one component uses goes in `shared/facts.json`, not in a script constant.
- A new brand file goes in `shared/brand/`; if a site or the pipeline needs a physical copy, add it to `brand.copies` and run `sync`.
- `.lumebook/` is generated state (hashes, to-dos, log). Don't edit by hand.

## Design system

- Every internal page uses `shared/design/lumebook.css`: builds inline it with `design.head()`; the SMM plan and the dashboard link synced copies (`design.copies`, kept equal by `sync`). Change the CSS, then `ripple` rebuilds the pages and lists artifacts to republish; regenerate the Design System artifact with `build_ds_artifact.py`.
- Style page-specific rules with tokens only (`--bg --surface --text --tint --accent ...`), use `lb-` components first, keep 390px phone width working, Hebrew pages RTL. White and black modes with a switch (Yarin, 21 Oct 2026; replaces light-only, the cream and purple grounds are gone): black is `:root[data-theme="dark"]`, `design.head()` sets the mode before first paint from localStorage `lb-mode` (white by default), `design.theme_toggle()` is the switch every internal page carries in its top bar or sidebar; the dashboard and the SMM plan hold a hand copy of the boot script. Check new pages in both modes. The public creator brief keeps its own modes (`design.head(theme=False)`).
- Fonts (Yarin, 18 Oct 2026): Heebo is the main font, headings included; Assistant (`--font-2`) is the secondary font for labels, captions, counts, chips and table headers. Varela Round is dropped.
- Category colour: eight hues (`--cat-1` ... `--cat-8`) only for a page's 3 to 8 stable categories that a reader scans or filters by, never for status or the kid/expert pillars. Which category gets which hue lives in `shared/design/categories.json` (builds read it via `design.py`; `sync` writes `categories.css` for the dashboard and the SMM plan). Add a set there before colouring a new page.
- Not for the carousel slide designs (the kid/expert pillar looks are audience content). The retired ambassadors site keeps its own styling.

## Rules that apply everywhere

- No em dashes in anything written for the user or audience. Brand: LumeBook / לומבוק, never לומיבוק.
- Creator offer: personal link with an audience discount, never "קוד הנחה" or "קוד אישי" (see `shared/facts.json` offer).
- Don't mention AI in audience copy.
- Hebrew grammar: `creators/creator-research/src/hebrew-rules.md`.
- Never edit built HTML (creator map, research pages); edit the sources and rebuild.
- New images, videos and audio go in `media/projects/<start date>-<slug>/` (or `media/inbox/` until sorted), never in a new top-level folder; one copy per file. `output/` and `video/` were folded into `media/` on 14 Oct 2026.
- Finished content (carousel exports, final reels and images) also goes to Yarin's Drive folder `LumeBook תוכן` (My Drive, ids in `shared/facts.json` `drive_content`; Yarin, 18 Oct 2026). Carousels are copied by `carousel/carousel-pipeline/scripts/drive_export.py` through Google Drive for desktop; anything else goes in a subfolder by type, one folder per job named like its `media/projects/` folder.
- Never delete project files: move them to `_to-delete/` under their original path and add a line to `_to-delete/README.md`.
- `sites/lumebook-smm-plan`: mirror every Hebrew change in `content.en.md` in the same commit.
- Commit or push only when Yarin asks. Repos use the GitHub no-reply email. One exception (Yarin, 20 Oct 2026): a launchd job (`com.yarinbruner.lumebook-nightly-commit`) runs `tools/nightly_commit.py` every day at 00:00: rebuilds the dashboard snapshot (`sites/dashboard/refresh.py`, no signup Sheet), commits everything not ignored on the current branch (holds back `sheet.md` and an SMM plan `index.html` whose `content.en.md` mirror did not change), pushes it to origin (never forced), then deploys the Vercel sites that changed (dashboard, creator-brief; skipped if the push failed). Log: `~/Library/Logs/LumeBookNightlyCommit.log` and `.lumebook/nightly-commit.log`. Pause it with `launchctl bootout gui/$(id -u)/com.yarinbruner.lumebook-nightly-commit`.
- Preview servers: `.claude/launch.json`. If Yarin has a page open in the site editor, ask before writing that file.
- Carousel Machine (called Hook Studio until 22 Oct 2026; carousel pool, grading, production, editors) runs all the time at http://localhost:8777/ as a login item and is also reachable through the project server at http://localhost:8780/hook-studio/ (forwarded by `tools/lumebook.py serve`; there is no separate preview config since 20 Oct 2026), never start a second copy, and run `python3 carousel/carousel-pipeline/scripts/hook_studio_login.py restart` after editing its scripts.
