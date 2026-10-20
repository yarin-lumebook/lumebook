# Creator CRM research (19 Oct 2026)

What a good CRM for LumeBook's creator outreach needs to do, how it should be designed, and what to change in the current creator map, in what order. Research and design only: nothing here is built, and the creator map, its data, its artifact and its scheduled task were not changed.

Made from the prompt `prompts/Claude Code Prompt for Creator CRM Design Research.md`.

## Files

| File | What is in it |
|---|---|
| `report.md` | Start here. One-page summary, then: the tool today (from its code and live records), the research findings, the requirements, the design, the gap table, the top five changes, and the questions for Yarin, Yossi and a lawyer |
| `sources.md` | Every source with its URL, the date read, what it was used for, its label (verified, vendor claim, law-firm summary) and who read it |
| `tools-compared.md` | One short entry per tool or approach: what it is for, what it does well, what a solo barter programme would take from it, price with date |

## How it was made

1. **The tool today.** Read from `creators/creator-research/src/` (`template.html`, `build2.py`, `enrich.py`, `refresh/`, the JSON data). One read-only export of the map's live `outreach` collection (261 records) and the dashboard's `tracker/state` document gave the real counts. The built map was opened at phone width in the built-in browser, as a static copy with no data. The export stayed in the session's scratch folder and is not saved here.
2. **Research.** Three research assistants worked in parallel inside the same session, each on a fixed slice with a source list and a search cap:
   - tools and CRMs
   - gifting and outreach
   - Israel and attribution
   
   They used 97 searches, and the lead session one more, out of a shared budget of about 200. Every cited page was opened; search results alone were not used as sources. The lead session re-read 8 key sources to check them and read two Instagram help pages directly. `sources.md` marks which.
3. **Requirements, design and plan** are the lead session's synthesis. Where the evidence ran out, the report says so and labels the point as an inference.

Not read or touched: anyone's DMs or email (including `creators/correspondence/`), the creator map's source and data (read only), its published artifact, its scheduled task.

## Notes

- **Internal figures:** `report.md` section 2.8 holds internal outreach counts. Keep them off public pages, like the sales figures in `docs/`.
- **Law:** the privacy, anti-spam and disclosure points come from unofficial statute copies and law-firm summaries. They are not legal advice. `report.md` section 6.3 lists what a lawyer should confirm.
- **Prices** are as shown on the vendors' pages on 19 Oct 2026. Many pages show "$" without naming the currency.
- **Registry:** this folder is not yet in `lumebook.json`. Other research folders are registered as `kind: docs`; add an entry if it should show up in `python3 tools/lumebook.py status`.
