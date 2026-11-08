# Language switch: Hebrew and English on every page

Since 08 / 11 / 2026 (Yarin: "i want the entire project in hebrew and english with a toggle that appears everywhere to switch between them").

## What you see

- Every internal page (everything with the project nav) has **עב | EN** in a small glass capsule floating at the bottom left of the window. On the project server it sits right of the edit button (the pencil) and moves with it; on claude.ai artifacts and the Vercel copy, which have no edit button, it takes the pencil's place. On a phone it floats above the bottom bar. It hides while the editor is open (Yarin, 08 / 11 / 2026: "make the language button float next to the edit site button to the right"; it was at the foot of the side bar before that).
- Until it is used, a page shows the language it was written in. After that, every page on the same address shows the chosen language: Hebrew pages turn English and left to right, English pages turn Hebrew and right to left, and the English bits of a Hebrew page turn Hebrew.
- The choice is kept per browser and address (`localStorage` key `lb-lang`): once on the project server (`localhost:8780`) covers every page there. Each claude.ai artifact and the Vercel copy remember their own. A link with `?lang=en` or `?lang=he` sets it.
- The side bar stays on the right in both languages.

## What is never translated

- Fields (text boxes, text areas), editable text (`contenteditable`, `.lb-editable`), code (`code`, `pre`, `kbd`).
- Hebrew copy written for parents: carousel slide previews (`.sty`), text blocks people copy (`.lb-textblock`), messages to creators (text areas), reel scripts and hooks (editable).
- Anything inside `translate="no"`, `.notranslate` or `data-i18n="off"`. Mark a part this way in its page source when it must stay as written.
- The edit button: while it is open the page shows its own words, so an edit never saves a translation.

## Where the words come from

| File | What is there |
|---|---|
| `common.json` | The side bar, the controls and words many pages share |
| `pages/<page path>.json` | One page's words, keyed like the edit button's edits (`pages/research/research-hub/research-hub.html.json`) |

Each file has `en` (Hebrew to English) and `he` (English to Hebrew). A key is the text of one block of the page (a paragraph, a button, a table cell): its pieces in order, joined by the invisible character U+001F where bold, a link or a line break splits it, white space collapsed, and every number written `{0}`, `{1}` ... so one entry covers "12 יוצרים" and "13 יוצרים". A value is a string, or a list with one piece per piece of the key.

## How new words get translated

1. On the project server a page reports the blocks its dictionaries lack (`POST /api/i18n/missing`).
2. The server's background worker (`tools/i18n.py` `Worker`) sends them, 60 at a time, three calls at once, to `claude -p` with Sonnet and thinking off (about 22 seconds a batch): no tools, no files, the Claude login of this Mac, never an API key (the same locked down call as `/api/sample`). The prompt carries the Hebrew rules (everyday Israeli Hebrew, infinitive buttons, loanwords such as UTM and UGC, the prefix hyphen, לומבוק never לומיבוק) and forbids em and en dashes.
3. Every answer is checked (same number of pieces, every `{n}` kept, no dashes) and written into the dictionary; the page polls `GET /api/i18n/dict` and swaps the words in a few seconds later. The switch shows "מתרגם N…" meanwhile.
4. A block that fails three times is dropped from the queue (`.lumebook/i18n-queue.json`) and asked for again the next time a page shows it. A usage limit pauses the worker for 15 minutes; a missing `claude auth login` for an hour.

Words waiting when the server stops are picked up when it starts again. `python3 tools/i18n.py translate` does the same work in a terminal.

## Artifacts and Vercel

A page's file carries its dictionaries (the `lumebook-i18n` block before `</body>`), so the claude.ai artifact and the Vercel copy switch too, with the words known when the file was last baked. `tools/lumebook.py` bakes after every build and in `ripple`; the nightly job bakes every page. Pages away from the project server can't ask for new words: republish the artifact after its words are filled.

## Commands

```
python3 tools/i18n.py status                  # dictionaries per page and what is waiting
python3 tools/i18n.py translate [--page KEY]  # translate what is waiting, in this terminal
python3 tools/i18n.py check                   # placeholders, dashes, לומיבוק
python3 tools/i18n.py bake [PAGE ...]         # write the words block into page files
```

A wrong translation: fix it in the dictionary file here (keep the `{n}` and the number of pieces), then `python3 tools/i18n.py bake`. The project server shows the fix on the next page load.

## Code

- `shared/design/i18n.src.js`: the runtime in the page (design.py puts it in `nav.js` in front of the nav).
- `shared/design/nav.src.js`: the switch markup (`langSwitch`, drawn as its own floating element), styles `.lb-langfab` in `lumebook.css`. `shared/site-editor/loader.js` tells it where the edit button ends (`--lb-editbtn-x`, `--lb-editbtn-b` on `html`).
- `tools/i18n.py`: dictionaries, queue, worker, bake, CLI. `tools/site_editor.py` `inject` adds the live words block to every page the server shows; `tools/lumebook.py` has the two endpoints.
- `shared/site-editor/loader.js` suspends the switch while editing; `overlay.js` `resync()` keeps saved edits from being applied again over translated words.

Test changes on a spare port: `LUMEBOOK_I18N_DIR` (scratch dictionaries), `LUMEBOOK_I18N_QUEUE` (scratch queue), `LUMEBOOK_CLAUDE` (a stand-in command), `serve --port 8791`.
