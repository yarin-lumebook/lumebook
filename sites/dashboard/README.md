# Lumebook dashboard

Self-updating Q4 dashboard for the Lumebook social project.

- `lumebook-dashboard.html` – the page. Published as a claude.ai artifact (live signups, saved ticks) and, read-only, on Vercel. Its default view is the work board (`#board`); the other views are in the menu.
- `board/` – the work board: canvas, cards, connections, templates, tools dock, saving. How it saves and what differs between the artifact, Vercel and the local server: `board/README.md`.
- `refresh.py` – builds `out/snapshot.json` from the project folder, the live sites, public Instagram counts and the signup Sheet export, plus the board's resource catalog (`board/catalog.py`) and whether each local tool answered.
- `build_site.py` – embeds the snapshot into the page for the static Vercel copy (`site/lumebook-dashboard/`) and copies the board files. Board edits made in the artifact are never exported into it.

A daily scheduled task in the Claude app runs refresh → artifact database → build → `npx vercel deploy --prod --yes` from `site/lumebook-dashboard`.
