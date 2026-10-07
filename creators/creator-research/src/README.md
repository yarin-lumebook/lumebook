# Creator map source

`lumebook-creator-map.html` in the folder above is generated. Edit the files here, then rebuild:

```bash
python3 src/build2.py
```

- `template.html`: the page (styles, layout, outreach tool, dashboard script) with `__DATA__`-style placeholders.
- `build2.py`: fills the placeholders with the creator data and writes the map. It also turns long dashes into commas or hyphens.
- `enrich.py`: adds waves, opener lines and the "moment" for each creator.
- `C_all.json`: the 204 verified creators. `contacts.json`: the emails and phone numbers each creator publishes themselves.
- `kids.json`: how many kids each creator has and their genders (`n` total, `b` boys, `g` girls, `note`, `src`), only where the public bio says so. Nothing is guessed from names. Fill it in for every new creator.
- `research/`: the scripts and hand-written records that produced `C_all.json` (first pass, second pass, merge rules, edge cases and exclusions).

The published page is https://claude.ai/artifact/MPuqcaCXXF5CGQiDMaDpbB. After rebuilding, republish that file to the same artifact.
