# LumeBook project

Social media work for LumeBook (personalised kids' books, Israel). Solo SMM: Yarin. Hebrew audience copy, RTL.

## Layout (since 8 Oct 2026)

| Folder | What is there |
|---|---|
| `lumebook.json` | Component registry: every workstream, what it watches, how it builds, where it is published, what it feeds |
| `tools/lumebook.py` | Keeps components in step (see below) |
| `shared/facts.json` | Facts several components repeat: artifact and site URLs, Form/Sheet IDs, creator offer, key dates, barter list, baselines |
| `shared/brand/` | Canonical logos, mascot, fonts, carousel backgrounds, link-preview image |
| `docs/` | Product brief, Q4 strategy page, Hebrew carousel playbook, UGC research, Hebrew voice tool note |
| `prompts/` | The master prompts each workstream was built from (historical; paths updated to this layout) |
| `sites/` | `lumebook-smm-plan`, `lumebook-ambassadors` (each its own git repo, push = Vercel deploy), `dashboard` (git repo, CLI deploy) |
| `creators/` | `creator-research` (creator map, git repo) and the signup Form's Apps Script |
| `research/` | Competitor teardown, kids content lab (1.1 GB of raw video and frames, keep), carousel research, carousel playbook page |
| `carousel/` | `carousel-pipeline` (nightly, 22:00), `fal-carousel-trial` (frozen reference), `references/` |

Project skills: `.Codex/skills/lumebook-carousel`, `.Codex/skills/lumebook-hebrew-voice`. `.agents/skills/*` are symlinks to them; edit only `.Codex/skills`.

## How components stay connected

```
python3 tools/lumebook.py status     # what changed, what it affects, open to-dos, consistency warnings
python3 tools/lumebook.py ripple     # same + rebuild safe local pages, sync brand copies, queue the rest
python3 tools/lumebook.py check      # registry, brand copies, offer wording, לומיבוק, em dashes, old paths
python3 tools/lumebook.py ack ID --published   # after republishing an artifact
python3 tools/lumebook.py map        # the dependency graph
```

- The 08:14 dashboard task runs `ripple` first, so the dashboard's "סנכרון בין הרכיבים" panel shows what is waiting.
- After changing a component, run `ripple`. After republishing an artifact, run `ack <id> --published`.
- A new workstream gets an entry in `lumebook.json` (and in `shared/facts.json` if it has a URL). Use paths relative to this folder.
- A fact that more than one component uses goes in `shared/facts.json`, not in a script constant.
- A new brand file goes in `shared/brand/`; if a site or the pipeline needs a physical copy, add it to `brand.copies` and run `sync`.
- `.lumebook/` is generated state (hashes, to-dos, log). Don't edit by hand.

## Rules that apply everywhere

- No em dashes in anything written for the user or audience. Brand: LumeBook / לומבוק, never לומיבוק.
- Creator offer: personal link with an audience discount, never "קוד הנחה" or "קוד אישי" (see `shared/facts.json` offer).
- Don't mention AI in audience copy.
- Hebrew grammar: `creators/creator-research/src/hebrew-rules.md`.
- Never edit built HTML (creator map, research pages); edit the sources and rebuild.
- `sites/lumebook-smm-plan`: mirror every Hebrew change in `content.en.md` in the same commit.
- Commit or push only when Yarin asks. Repos use the GitHub no-reply email.
- Preview servers: `.Codex/launch.json`. If Yarin has a page open in the site editor, ask before writing that file.
