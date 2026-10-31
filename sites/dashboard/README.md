# Lumebook dashboard

Self-updating Q4 dashboard for the Lumebook social project.

- `lumebook-dashboard.html` – the page. Published as a claude.ai artifact (live signups, saved ticks) and, read-only, on Vercel. Its default view is the course (`#course`, since 31 Oct 2026, in English); the other views are in the menu.
- `course/` – the course: lessons in order with quizzes Claude grades, projects Claude checks, tasks with checklists, weekly numbers, link maker, glossary. How it saves and how to test it: `course/README.md`. It replaced the canvas work board on 31 Oct 2026 (now in `_to-delete/sites/dashboard/board/`).
- `refresh.py` – builds `out/snapshot.json` from the project folder, the live sites, public Instagram counts and the signup Sheet export, plus whether each local tool answered.
- `build_site.py` – embeds the snapshot into the page for the static Vercel copy (`site/lumebook-dashboard/`) and copies the course files. Tasks, quiz answers and numbers saved in the artifact are never exported into it.

A daily scheduled task in the Claude app runs refresh → artifact database → build → `npx vercel deploy --prod --yes` from `site/lumebook-dashboard`.
