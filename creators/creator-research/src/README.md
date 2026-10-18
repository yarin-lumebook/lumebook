# Creator map source

`lumebook-creator-map.html` in the folder above is generated. Edit the files here, then rebuild:

```bash
python3 src/build2.py
```

- `template.html`: the page (styles, layout, outreach tool, dashboard script) with `__DATA__`-style placeholders.
- `build2.py`: fills the placeholders with the creator data and writes the map. It also turns long dashes into commas or hyphens.
- `build2.py` also reads the offer from `../../../shared/facts.json` (the 25% allocation, the split example, the paid-hold list), so the messages and the offer check never keep their own copy of the numbers. Change the offer there, then rebuild.
- `enrich.py`: adds waves, opener lines and the "moment" for each creator.
- `C_all.json`: the 343 verified creators (204 from 3 Oct, 100 from 11 Oct, 61 under-5K removed on 12 Oct, 100 added on 18 Oct). `contacts.json`: the emails and phone numbers each creator publishes themselves.
- `kids.json`: how many kids each creator has and their genders (`n` total, `b` boys, `g` girls, `names` as written in the bio, `note`, `src`), only where the public bio says so. Nothing is guessed from names. Fill it in for every new creator.
- `hebrew-rules.md`: the Hebrew rules the messages follow (agreement, definite article, construct chains, prepositions, punctuation). The map checks the checkable ones.
- `research/`: the scripts and hand-written records that produced `C_all.json` (first pass, second pass, merge rules, edge cases and exclusions).
- Third pass (11 Oct 2026): `research/data3.py` holds the 100 added creators, `research/pass3_raw.json` the numbers and bios as read that day, and `research/merge3.py` appends them to `C_all.json`, `kids.json` and `contacts.json`. To add more creators later, write a new data file in the same shape and run a copy of `merge3.py`.
- Fourth pass (18 Oct 2026): `research/data4.py`, `research/pass4_raw.json` and `research/merge4.py` (same shape; it also appends the rows to the CSV the dashboard counts). Found by pulling Instagram's similar-accounts list for all 304 known handles (about 6,300 new accounts), screening about 5,800 by the follower count and bio in each profile page's description, then a second hop from the first 91 picks. Every one of the 100 has 5,000 to 50,000 followers and a reel since July. A profile's Instagram id (pk) is the safe duplicate check: `by_shanina` turned out to be the renamed `shanina_advent.learn`.

The published page is https://claude.ai/artifact/MPuqcaCXXF5CGQiDMaDpbB. After rebuilding, republish that file to the same artifact.
