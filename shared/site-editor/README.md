# Edit button (every page on localhost:8780)

Since 05 / 11 / 2026 every page the project server shows has a round pencil button at the bottom left. Press it to edit the page right where it is; **Done** puts the page back and the button returns. There is no separate editing server: the tools open as usual (from HQ, on `http://localhost:8780/`), including Carousel Machine through `/hook-studio/`.

## Using it

- **Click anything** to select it. The panel shows its colors, its size and spacing (text size, width, height, padding, space above and below, gap, corners, border, opacity), and Move up, Move down, Duplicate, Delete, plus Replace and Describe for pictures and Link and Open for links. Height shows for text boxes too (11 Nov 2026).
- **Resize by dragging** (Yarin, 11 Nov 2026): the selected box has handles on its left and right sides (width), its top and bottom (height, from either side) and its four corners (both). The page still decides where the box sits, so dragging the top handle up makes it taller and the box grows downward. The label shows the size while you drag; letting go saves one step that Undo takes back. The edge snaps to the edges of nearby boxes (the parent's outer and inner edges, the siblings, the cousins) and the size snaps to a sibling's width or height, with a pink guide line; hold ⌥ (Alt) to resize freely. Width and height are saved like the panel's fields (inline `!important` pixels, with `max-width` / `max-height: none` and `min-height: 0` so the size holds).
- **Auto layout** (Yarin, 11 Nov 2026: "add full auto layout capabilities in the edit site option"), like a design tool's. A box with things inside shows **Add auto layout** (⇧A): it reads how the items sit now (one column, one row, or rows that wrap), makes the box a flex box in that direction and turns the space between the items into the gap (their margins along the flow go to 0). A box that already lays out its items (flex or grid, from the page or from here) shows the **Auto layout** section: Column, Row, Wrap or Grid; Gap (Gap ↔ and Gap ↕ for wrap and grid); Columns for a grid; padding across and down, or each side with **Sides**; a 3 x 3 picker that places the items (top, middle, bottom by left, center, right, as seen on the page, right to left included); **Auto spacing** (spread over the box, the gap shows Auto); **Baseline** for rows; **Clip content**; **Remove** (⌥⇧A). The selected auto layout box shows its padding shaded pink and its gaps striped. Any box shows **Resizing**: W and H as **Fixed** (its size now), **Hug** (as big as what is inside) or **Fill** (the room in the box around it: grows along a row or column, stretches across it), Min W, Max W, Min H, Max H (empty for none), Span cols and Span rows inside a grid, **Ignore auto layout** (it stays where it is, on top, out of the flow; ⌥ drag places it) and **Reset**. All of it is inline `!important` styles, saved and undone like the other fields, so it works on built and script-drawn pages too. The old Gap and Padding fields moved into the auto layout section for such boxes.
- **Click text to type.** Select words to format them with the toolbar at the top: style, font, size, bold, italic, color, highlight, alignment, lists, links.
- **Drag things around:** drag the ⠿ on the selected element's label (or press and drag a selected box). Drop it between its neighbours, or next to something like it elsewhere, for example a card into another list. Hold ⌥ (Alt) while dragging to place it freely.
- **Colors** (in the bar) recolors the whole page: background, text and the page's color variables.
- **Delete** hides the part. Undo (⌘Z) brings back anything from this visit.
- Changes save by themselves. Alt + ↑ selects the box around the selected one; Esc stops typing, then deselects.

## Where the edits go

| Page | How it saves |
|---|---|
| Hand-written pages listed in `pages.json` → `source` (the SMM plan) | What the file holds is edited in the file itself, as the site-editor skill does. Parts the page's scripts draw go to the edits layer below. The version each save replaced is kept in `.site-editor/backup/` (not in git). |
| Every other page: built pages (research pages, creator map, strategy, creator brief), HQ, Carousel Machine | Nothing of the page is rewritten. Each change is an operation (new text, a style, a move, a hidden part...) in `edits/<page path>.json`. |

- `overlay.js` applies a page's operations whenever the page shows, and again whenever the page's own scripts redraw part of it, so edits work on script-drawn content (creator cards, HQ cubes, research tables) and **survive rebuilds**.
- Each edited page also carries its edits in its own file, in the `lumebook-edits` block before `</body>` (the operations plus a copy of `overlay.js`), so the artifact and Vercel copies show them after the next republish or deploy. `tools/lumebook.py build` writes the block back after every build, `ripple` and the nightly job (`tools/nightly_commit.py`) do it for every edited page, so a page rebuilt by any script gets its edits back. `ripple` then lists the artifacts to republish as usual.
- An element is found again by its place in the page and the first words it had. If a rebuild changed those words or removed the element, that edit is skipped (never guessed) and the editor says how many edits "couldn't find their place".

## Files

| File | What it is |
|---|---|
| `loader.js` | The pencil button. The server adds it to every page it shows; never part of a page's file. |
| `editor.js` | The editor, loaded when the button is pressed. Project copy of the site-editor skill's editor (`~/.claude/skills/site-editor/assets/editor.js`, 29 / 09 / 2026) with: the edits layer (operations next to every command, so Undo takes them back too), drag to move, the size and spacing fields, the Done button. |
| `overlay.js` | The runtime that applies the operations (served to every page, and copied into each edited page's block). |
| `pages.json` | `source` pages, `alias` (HQ's built copy edits HQ's source), `off` (no button: `_to-delete/`, the retired ambassadors site, the dashboard's Vercel copies of the plan and research pages), `notes` shown in the editor's help. |
| `edits/` | One JSON per edited page, one operation per line. In git. |
| `test/` | Two test pages (`index.html` layer mode, `source.html` source mode) with fixed and script-drawn cards and a redraw button. Safe to edit. |
| `../../tools/site_editor.py` | The server side: which mode a page gets, adding the button, `/__site-editor/` (info, source, save, upload), baking. |

## For Claude

- `python3 tools/lumebook.py edits` lists edited pages; `edits bake` writes every page's edits back into its file.
- Never edit an `edits/*.json` file or a page's `lumebook-edits` block by hand: the editor checks versions and refuses saves over changes it didn't make (it shows Reload). To make a layer edit permanent in a page's sources (its builder, md or json), port it there and then remove the operation through the editor (Undo, or Yarin deletes it), or ask Yarin before emptying the list.
- While Yarin has a page open in the editor, ask him to press Done before changing that page's file or its edits (memory: site-editor-concurrent-edits).
- After editing `tools/site_editor.py` or `tools/lumebook.py`: `python3 tools/serve_login.py restart`. `editor.js`, `loader.js` and `overlay.js` are served fresh (reload the page); after changing `overlay.js`, run `ripple` or `edits bake` so baked copies get it.
- Pictures added with the editor go to `media/inbox/` (one copy, the unsorted folder of `media/README.md`) and the page links them by a relative path, so they show on localhost only; before republishing such a page, embed or move the picture.
- Not editable: text drawn by CSS (`::before`), canvas, pictures of text, iframes, SVG text. Inside claude.ai the artifact copies show the edits but have no button (they can't save to this folder).
