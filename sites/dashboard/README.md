# Lumebook dashboard

Self-updating Q4 dashboard for the Lumebook social project.

- `lumebook-dashboard.html` – the page. Published as a claude.ai artifact (live signups, saved ticks) and, read-only, on Vercel.
- `refresh.py` – builds `out/snapshot.json` from the project folder, the live sites, public Instagram counts and the signup Sheet export.
- `build_site.py` – embeds the snapshot into the page for the static Vercel copy (`site/lumebook-dashboard/`).

A daily scheduled task in the Claude app runs refresh → artifact database → build → `npx vercel deploy --prod --yes` from `site/lumebook-dashboard`.
