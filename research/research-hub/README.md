# Research hub (ספריית המחקר)

One Hebrew page with every research LumeBook has made, by topic, so Yarin can find any finding fast (Yarin, 08 Nov 2026: "combine every research we ever made to one super organized page").

Open it on the project server: http://localhost:8780/research/research-hub/research-hub.html

**Local only.** The page holds internal figures (sales, orders, outreach counts). It has no Vercel address, is not an artifact, and is never deployed. Its public research pages keep their own `web` addresses in `shared/facts.json`.

## Files

| File | What it is |
|---|---|
| `research.json` | The source: the topics (in order), the bottom line (`headlines`, each pointing at the research it comes from), and one entry per research |
| `build.py` | Writes `research-hub.html` with `design.head()` (design system and project nav). Fails on a broken entry |
| `research-hub.html` | The built page. Never edit it by hand |

Build: `python3 tools/lumebook.py build research-hub` (or `python3 build.py` here). `ripple` rebuilds it when `research.json` or `build.py` changes.

## An entry

```json
{
  "id": "carousel-audit",
  "topic": "carousels",
  "title": "Hebrew name",
  "date": "2026-10-24",
  "updated": null,
  "scale": "sample and method, one line",
  "summary": "what it asked and the bottom line, 1 to 2 sentences",
  "findings": ["terse bullets, the number in each"],
  "actions": ["what it changed or which tool uses it"],
  "evidence": "strong | medium | early",
  "evidence_note": "why",
  "status": "active | done | superseded | stopped",
  "status_note": "e.g. which later decision replaced it, or null",
  "internal": true,
  "links": [{"label": "the full page", "path": "repo-relative path"}],
  "tags": ["search words"]
}
```

- `topic` is one of the topics in `research.json`; its hue comes from `shared/design/categories.json` set `research-topics` (add the topic there first). A topic marked `"neutral": true` in `research.json` (tools) has no hue and is drawn in ink, so the set stays at 8 colours.
- `links`: the first link is the best page to read (a built page, else the main Markdown). Markdown links open in the page's own reader (it fetches the file from the project server); other files open in a new tab. The build checks that every path exists (a `#view` after the path is allowed, e.g. an HQ view).
- `evidence`: strong = our own measured data or a large verified sample; medium = a careful sample or verified outside sources; early = small sample, inference or hypotheses.
- `internal`: true when the research holds internal sales figures, order counts, outreach counts or personal data.
- Text rules: no em or en dash, brand לומיבוק / LumeBook (never לומבוק), dates in the page read 30 / 10 / 2026 (data stays ISO). `code` in backticks stays left to right.

## Adding a research

1. Add its entry to `research.json` (read the source, not only its built page; every number from the source).
2. If the research is a component in `lumebook.json`, add `research-hub` to its `feeds`, so a change to it leaves a "review the hub entry" to-do in `status`.
3. `python3 tools/lumebook.py build research-hub`, then `ripple`.

## How it was made

08 Nov 2026: seven readers each read one group of sources (the Markdown, data and READMEs behind each research, not only the built pages) and wrote draft entries; the lead session checked them against the sources, wrote the bottom line and built the page. The components that feed it are listed in `lumebook.json` (`feeds: ["research-hub"]`). Two research folders have no component of their own (`research/cro-crm`, `research/creator-crm`), so a change there does not leave a to-do.
