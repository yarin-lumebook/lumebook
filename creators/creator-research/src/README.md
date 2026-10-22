# Creator map source

`lumebook-creator-map.html` in the folder above is generated. Edit the files here, then rebuild:

```bash
python3 src/build2.py
```

- `template.html`: the page (styles, layout, outreach tool, dashboard script) with `__DATA__`-style placeholders.
- `build2.py`: fills the placeholders with the creator data and writes the map. It also turns long dashes into commas or hyphens.
- `build2.py` also reads the offer from `../../../shared/facts.json` (the 25% allocation, the split example, the paid-hold list), so the messages and the offer check never keep their own copy of the numbers. Change the offer there, then rebuild.
- `enrich.py`: adds waves, opener lines and the "moment" for each creator.
- `C_all.json`: the 347 verified creators (204 from 3 Oct, 100 from 11 Oct, 61 under-5K removed on 12 Oct, 100 added on 18 Oct, 2 added by hand on 20 Oct, 1 on 21 Oct, 1 on 22 Oct). `contacts.json`: the emails and phone numbers each creator publishes themselves.
- Since 20 Oct 2026 the free text in `C_all.json` is Hebrew, like the rest of the map: `role`, `topics`, `concept`, `risk`, `ages` (״2 עד 8״), `loc`, `contact` and the `roles` list. The English is in git history. `arch`, `prac` and `conflict` stay English because they are keys that `template.html` maps to Hebrew labels. The `research/data*.py` files are still English, so a new research pass should write its new rows in Hebrew, following `hebrew-rules.md`. `enrich.py` reads both languages and gives each of the 343 creators the same moment and wave as before.
- `kids.json`: how many kids each creator has and their genders (`n` total, `b` boys, `g` girls, `names` in Hebrew letters, `names_en` when the bio writes them only in English and `names` is the transliteration, `note`, `src`), only where the public bio says so. Nothing is guessed from names. Fill it in for every new creator.
- `test_kids_names.mjs`: checks the built map: every suggested message names the kids at most once (later mentions say הילדים, הילדה and so on) and no name is left in English. Run `node src/test_kids_names.mjs` after a build; `--show handle1,handle2` prints those creators' messages.
- `hebrew-rules.md`: the Hebrew rules the messages follow (agreement, definite article, construct chains, prepositions, punctuation). The map checks the checkable ones.
- `research/`: the scripts and hand-written records that produced `C_all.json` (first pass, second pass, merge rules, edge cases and exclusions).
- Third pass (11 Oct 2026): `research/data3.py` holds the 100 added creators, `research/pass3_raw.json` the numbers and bios as read that day, and `research/merge3.py` appends them to `C_all.json`, `kids.json` and `contacts.json`. To add more creators later, write a new data file in the same shape and run a copy of `merge3.py`.
- Fourth pass (18 Oct 2026): `research/data4.py`, `research/pass4_raw.json` and `research/merge4.py` (same shape; it also appends the rows to the CSV the dashboard counts). Found by pulling Instagram's similar-accounts list for all 304 known handles (about 6,300 new accounts), screening about 5,800 by the follower count and bio in each profile page's description, then a second hop from the first 91 picks. Every one of the 100 has 5,000 to 50,000 followers and a reel since July. A profile's Instagram id (pk) is the safe duplicate check: `by_shanina` turned out to be the renamed `shanina_advent.learn`.

Where the map runs, and where its data lives (since 20 Oct 2026): open it on the project server, `http://localhost:8780/creators/creator-research/lumebook-creator-map.html` (`python3 tools/lumebook.py serve`). Statuses, notes, reminders, settings and the voice are saved by the server into `creators/creator-research/state/` (`outreach.json`, `settings.json`, `voice.json`, `log.json`; private, not in git; `state/export-2026-10-20/` is the copy taken from the artifact database that day). The page detects the server and uses `/api/creator-map/state` and `/api/creator-map/doc`; elsewhere it behaves as before (artifact database, or browser-only in a preview). The artifact https://claude.ai/artifact/MPuqcaCXXF5CGQiDMaDpbB still holds the old database and is no longer updated: do not republish it, it would not carry the local data.
