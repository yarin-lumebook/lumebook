# Lumebook SMM plan site

- `index.html` is the site: Hebrew only, RTL, design tokens copied from lumebook.com.
- `content.en.md` is the English mirror. **Every change to Hebrew text in `index.html` must be mirrored in `content.en.md` in the same commit** (same sections, same order). A pre-commit hook in `.githooks/` blocks commits that change `index.html` without `content.en.md`.
- Scope: only what the SMM lead defines and owns. No content examples (hooks, captions, scripts), except the "סרטונים שעבדו" section of reference videos the SMM lead asked for (2.10.2026). Those play in place through TikTok's embed player, loaded only on tap (embeds pull the page's scroll while loading). Instagram reel embeds don't play inline logged out, so use a TikTok source. Never re-host the video files. The founder is Yossi (יוסי): refer to him by first name. He and the SMM lead are the only people on the project.
- Deploy: this page ships inside the dashboard site at https://lumebook-dashboard.vercel.app/plan/ (sites/dashboard/build_site.py copies it; the 08:14 task deploys). Its own Vercel project and repo were retired on 8 Oct 2026; it lives in the LumeBook monorepo.
- The mirror check is the monorepo's root `.githooks/pre-commit` (`git config core.hooksPath .githooks`).
- Styling: links `lumebook.css`, a synced copy of shared/design/lumebook.css. Never edit the copy; keep `sites/dashboard/refresh.py` plan_section patterns intact.
