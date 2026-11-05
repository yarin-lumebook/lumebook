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
| `shared/site-editor/` | The edit button (since 5 Nov 2026): every page the project server shows (Carousel Machine included) has a pencil at the bottom left to edit text, colors, pictures, size and spacing and drag things around in place; no separate editing server. Hand-written pages in `pages.json` save into their file, every other page keeps its edits in `edits/<page>.json`, applied over the page and written back into it after every build (README there; server side `tools/site_editor.py`) |
| `sites/` | `dashboard` (the all-in-one internal dashboard; artifact + lumebook-dashboard.vercel.app, which also serves the plan at /plan/ and, since 5 Nov 2026, read-only copies of five research pages at /research/ (the `shared/facts.json` artifacts with a `web` address; never pages with internal figures or personal data)), `lumebook-smm-plan` (the plan page, edited with the edit button, which saves into its file), `lumebook-creator-brief` (the creator Reel brief, public at lumebook-creator-brief.vercel.app; built from `research/israeli-product-reels/creator-brief.md`, deploy with `python3 tools/lumebook.py deploy creator-brief`), `lumebook-ambassadors` (retired 11 Oct 2026: Yarin no longer uses the Vercel ambassadors site; the folder is an archive, do not deploy or maintain it) |
| `creators/` | `creator-research` (creator map; grows by up to 100 creators every Saturday at 21:00 through the scheduled task `lumebook-creator-map-weekly` (off from 26 Oct 2026; switched back on by Yarin on 05 Nov 2026, now that Instagram is signed in to the built-in browser again), method in `src/research/weekly/README.md`; the same Saturday run then re-reads everyone and refreshes the six numbers on each card, `src/refresh/README.md`; the old Sunday task `lumebook-creator-refresh` is off), the signup Form's Apps Script, `correspondence/` (creator emails and DM recordings, one folder per handle, not in git) |
| `research/` | Competitor teardown, kids content lab (1.1 GB of raw video and frames, keep), carousel research, carousel playbook page, `carousel-audit` (every published carousel: Meta exports in, inventory, ranking and creative scores out; `src/audit.py import <export.csv>` after each export, `audit.py link <topic>` for UTM links; internal figures, local only, README there) |
| `carousel/` | `carousel-pipeline` (Carousel Machine: nightly at 22:00, hooks first, then content, then slide design; its drafts and paid `approved/` runs stay inside it) |
| `media/` | Every creative file (images, video, audio) since 14 Oct 2026: `projects/YYYY-MM-DD-slug/` one folder per job (reels, podcasts, character packs, stories, highlights, trend recreations, the frozen fal trial), `inbox/` for unsorted files. Index, rules and the cloud-archive steps: `media/README.md` |
| `_to-delete/` | Files the project no longer needs, under their original path, listed in its README. Yarin empties it; not in git |

One git repo for everything: github.com/yarin-lumebook/lumebook (private, since 8 Oct 2026; the four old repos are archived and their history is inside). Raw media is ignored (see `.gitignore`). The root `.githooks/pre-commit` enforces the SMM plan's English mirror and blocks Sheet exports.

**Account handoff in progress (since 26 Oct 2026):** the project moved to a new Claude account on this Mac. The artifact links below are the new account's (republished 26 Oct); the weekly cloud routine and a few checks are still open in `docs/account-handoff/README.md`; finish those first.

Front door: the dashboard (https://claude.ai/artifact/R5tEXfKkNKzVYg8CWFh4s6; read-only copy https://lumebook-dashboard.vercel.app). It is HQ since 5 Nov 2026: no sidebar, the tools grid (`#tools`) is the home, every tool a coloured cube in its topic that opens the local version on :8780 and the artifact version inside claude.ai, and an edit mode where Yarin drags, adds, edits and deletes tools and topics (saved to `sites/dashboard/hq-layout.json` locally and to the artifact database `hq/layout`; README there). The course (since 31 Oct 2026) is the LumeBook pipeline course, in English, with tasks and Claude grading Yarin's written answers in the page (`sites/dashboard/course/`, README there; content and plan in `course/`, built by `python3 course/build.py`): it saves to the artifact database under `course/*` (never `snapshot`, `history`, `tracker` or the old `boards/`), and on Vercel or the local server only in that browser. It replaced the canvas work board (now in `_to-delete/`). Design System reference: https://claude.ai/artifact/Cw3pWrTsoCKkCaPzZLrr5B.

Project skills: `.claude/skills/lumebook-carousel`, `.claude/skills/lumebook-hebrew-voice`, `.claude/skills/reel-editor` (hook, word-by-word captions and trial reel versions, 26 Oct 2026). `.agents/skills/*` are symlinks to them; edit only `.claude/skills`.

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
- Style page-specific rules with tokens only (`--bg --surface --text --tint --accent ...`), use `lb-` components first, keep 390px phone width working, Hebrew pages RTL. White only (Yarin, 05 Nov 2026: "only white mode from now on"; replaces the white and black modes of 21 Oct): one set of tokens on `:root`, no black mode, no theme switch, no boot script, no `prefers-color-scheme`, no `data-theme` or `data-mode` rules. `design.theme_toggle()` returns nothing and `design.head(theme=...)` ignores `theme`; don't add new calls. This covers every page, the public creator brief included.
- No side stripes (Yarin, 05 Nov 2026: "dont use this ever again"): never a coloured bar on one side of a box (`border-inline-start`/`border-left` accent, `box-shadow: inset 3px 0 0`). Tint the whole box (`--tc-soft`, `--tint-soft`, `--warning-soft`) with at most a full 1px border.
- Everything goes in the design system (Yarin, 05 Nov 2026): before writing page CSS, look for the `lb-` piece (the "shared page patterns" section has hero, number disc and steps, text block with copy, scroller, media and post cards, pair, crumbs, pager, row list, popover, table and kv modifiers, savestate, kbd, spinner, flash). A pattern a second page needs moves into `lumebook.css` as an `lb-` component with a card in `build_ds_artifact.py`, never a second page copy.
- Fonts (Yarin, 18 Oct 2026): Heebo is the main font, headings included; Assistant (`--font-2`) is the secondary font for labels, captions, counts, chips and table headers. Varela Round is dropped.
- Category colour: eight hues (`--cat-1` ... `--cat-8`) only for a page's 3 to 8 stable categories that a reader scans or filters by, never for status or the kid/expert pillars. Which category gets which hue lives in `shared/design/categories.json` (builds read it via `design.py`; `sync` writes `categories.css` for the dashboard and the SMM plan). Add a set there before colouring a new page.
- Icons (5 Nov 2026): one set in `shared/design/icons.json` (`icons` for tools and topics, `ui` for interface glyphs); builds use `design.icon(name)`, pages without a build link the `icons.js` that `sync` writes and copies. Names never change (HQ layouts store them). HQ's launcher, edit mode and editor are design-system components (`lb-topics`, `lb-cube`, `lb-form`...).
- Project nav (Yarin, 5 Nov 2026): every internal page has the same navigation, `nav.js` (source `shared/design/nav.src.js`, tool list `shared/design/hq-tools.json`, which HQ's grid reads too): a fixed top bar with HQ's topics (first layer), the location path under it (HQ › topic › page), and a side bar on the right with every HQ tool (second layer) that collapses to an icon rail; on phones the side bar is a drawer and a bottom nav bar takes the topics. `design.head()` inlines it (`nav=False` only for the public creator brief); HQ and the SMM plan link the synced copy. A new tool goes in `hq-tools.json`, then `ripple`. A page's own sticky bar adds `var(--lb-gnav-top, 0px)` to its `top`; a page that fills the window takes off `--lb-gnav-space` (Carousel Machine) or `--lb-gnav-pad`. Pages built by `lumebook.py build` know which page they are inside an artifact too (`LB_PAGE_FILE`).
- Not for the carousel slide designs (the kid/expert pillar looks are audience content). The retired ambassadors site keeps its own styling.

## Rules that apply everywhere

- No em dashes in anything written for the user or audience. Brand: LumeBook / לומבוק, never לומיבוק.
- Creator offer: personal link with an audience discount, never "קוד הנחה" or "קוד אישי" (see `shared/facts.json` offer).
- Don't mention AI in audience copy.
- Hebrew grammar: `creators/creator-research/src/hebrew-rules.md`.
- Never edit built HTML (creator map, research pages); edit the sources and rebuild. Yarin's own changes with the edit button are kept apart (`shared/site-editor/edits/`) and written back after every build, `ripple` and the nightly job; never edit those files or a page's `lumebook-edits` block by hand (`python3 tools/lumebook.py edits` lists them).
- New images, videos and audio go in `media/projects/<start date>-<slug>/` (or `media/inbox/` until sorted), never in a new top-level folder; one copy per file. `output/` and `video/` were folded into `media/` on 14 Oct 2026.
- Google Drive (Yarin, 03 Nov 2026): when Yarin says "Drive" or "Google Drive" he means the shared `שיווק` folder (`shared/facts.json` `drive_marketing`). The old My Drive folder `LumeBook תוכן` is retired: never read it, write to it or link it; `drive_export.py` is switched off (no `drive_content` in facts). Finished content stays in `media/projects/` and `carousel/carousel-pipeline/approved/`; put something on Drive only when Yarin asks.
- OpenAI API key (Yarin, 03 Nov 2026): Carousel Machine makes its pictures only through the OpenAI Images API (`carousel/carousel-pipeline/scripts/openai_generate.py`, settings in `openai_models.json`); fal.ai and ChatGPT in Chrome are retired (their files are in `_to-delete/`), and no other image tool is used for a carousel. The key lives in the Keychain item `openai-api-key`, exported as `OPENAI_API_KEY` by `~/.zshrc`; run scripts through `zsh -ic` and never print or write it. Four rules for every use: always ask Yarin for a budget, never exceed it, tell him the estimated tokens and cost before generating, create nothing without his explicit yes (a yes covers one stage). Carousel Machine enforces them in code (an `approval` stop before every stage that spends).
- Never delete project files: move them to `_to-delete/` under their original path and add a line to `_to-delete/README.md`.
- `sites/lumebook-smm-plan`: mirror every Hebrew change in `content.en.md` in the same commit.
- Commit or push only when Yarin asks. Repos use the GitHub no-reply email. One exception (Yarin, 20 Oct 2026): a launchd job (`com.yarinbruner.lumebook-nightly-commit`) runs `tools/nightly_commit.py` every day at 00:00: rebuilds the dashboard snapshot (`sites/dashboard/refresh.py`, no signup Sheet), commits everything not ignored on the current branch (holds back `sheet.md` and an SMM plan `index.html` whose `content.en.md` mirror did not change), pushes it to origin (never forced), then deploys the Vercel sites that changed (dashboard, creator-brief; skipped if the push failed). Log: `~/Library/Logs/LumeBookNightlyCommit.log` and `.lumebook/nightly-commit.log`. Pause it with `launchctl bootout gui/$(id -u)/com.yarinbruner.lumebook-nightly-commit`.
- Preview servers: `.claude/launch.json`. Pages are edited with the edit button on the project server (`shared/site-editor`, 5 Nov 2026), not with a separate site-editor server. If Yarin has a page open in edit mode, ask him to press Done before writing that page's file or its edits.
- Carousel Machine (called Hook Studio until 22 Oct 2026; carousel pool, grading, production, editors) runs all the time at http://localhost:8777/ as a login item and is also reachable through the project server at http://localhost:8780/hook-studio/ (forwarded by `tools/lumebook.py serve`; there is no separate preview config since 20 Oct 2026), never start a second copy, and run `python3 carousel/carousel-pipeline/scripts/hook_studio_login.py restart` after editing its scripts.
