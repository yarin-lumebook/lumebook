# Lumebook SMM plan site

- `index.html` is the site: Hebrew only, RTL, design tokens copied from lumebook.com.
- `content.en.md` is the English mirror. **Every change to Hebrew text in `index.html` must be mirrored in `content.en.md` in the same commit** (same sections, same order). A pre-commit hook in `.githooks/` blocks commits that change `index.html` without `content.en.md`.
- Scope: only what the SMM lead defines and owns. No content examples (hooks, captions, scripts), except the "סרטונים שעבדו" section of reference videos the SMM lead asked for (2.10.2026). Those play in place through TikTok's embed player, loaded only on tap (embeds pull the page's scroll while loading). Instagram reel embeds don't play inline logged out, so use a TikTok source. Never re-host the video files. The founder is Yossi (יוסי): refer to him by first name. He and the SMM lead are the only people on the project.
- Deploy: pushing to `main` auto-deploys via the Vercel Git integration (project `lumebook-smm-plan`, https://lumebook-smm-plan.vercel.app). Commits must use the GitHub no-reply email set in this repo's git config, or Vercel blocks the deploy.
- After cloning, run `git config core.hooksPath .githooks` to turn the sync check on.
