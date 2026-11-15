#!/usr/bin/env python3
"""Generate the LumeBook Design System artifact's files from shared/design/lumebook.css.

The stylesheet is the source of truth; this writes the browsable reference
(https://claude.ai/artifact/Cw3pWrTsoCKkCaPzZLrr5B) as files under <out>/project/:
tokens.json, README.md, components/bundle.css, components/<Comp>/{README.md,preview.html},
components/Cover/preview.html and design-system.json (the index).

    python3 shared/design/build_ds_artifact.py <out dir>

Then publish <out>/project/* to the artifact (see the Design System type's instructions). Standard library only.
"""
import json, os, re, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(HERE, "lumebook.css"), encoding="utf-8").read()
ICON_SET = json.load(open(os.path.join(HERE, "icons.json"), encoding="utf-8"))   # the icon set (5 Nov 2026)


def ico(name):
    """One icon of the set as inline svg (no attributes: lb-tile, lb-drag and the pickers style it)."""
    svg = ICON_SET["icons"].get(name) or ICON_SET["ui"][name]
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{svg["svg"]}</svg>'


def _ui(name):
    """One icon of the set with its stroke (fill none, currentColor, width 2), for cards whose CSS only sizes the svg."""
    svg = ICON_SET["icons"].get(name) or ICON_SET["ui"][name]
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{svg["svg"]}</svg>')


def _hq_cube(cat, icon, title, desc, where, alt="", count="", edit=False):
    t = f'<button type="button" class="lb-cube-title">{title}</button>' if edit else f'<a class="lb-cube-title" href="#">{title}</a>'
    return (f'<article class="lb-cube lb-cat-{cat}"><div class="lb-cube-top"><span class="lb-tile xl" aria-hidden="true">{ico(icon)}</span>'
            + (f'<span class="lb-count">{count}</span>' if count else "") + f'</div>{t}<p class="lb-cube-desc">{desc}</p>'
            f'<div class="lb-cube-foot"><span class="lb-cube-where">{where}</span>' + (f'<a class="lb-cube-alt" href="#">{alt}</a>' if alt else "") + '</div></article>')


def _hq_topic(cat, icon, title, n, desc, cubes, edit=False):
    head = (f'<header class="lb-topic-head">' + (f'<button type="button" class="lb-drag" aria-label="גרירת הנושא {title}">{ico("grip")}</button>' if edit else "")
            + f'<span class="lb-tile lg" aria-hidden="true">{ico(icon)}</span><div class="lb-topic-text"><h2 class="lb-topic-title">{title}<span class="lb-topic-n">{n}</span></h2>'
            f'<p class="lb-topic-desc">{desc}</p></div>'
            + (f'<button type="button" class="lb-btn secondary sm" aria-label="עריכת הנושא {title}">{ico("pencil")}<span class="lb-hide-sm">עריכת הנושא</span></button>' if edit else "")
            + '</header>')
    add = f'<button type="button" class="lb-cube-add">{ico("plus")}<span>כלי חדש</span></button>' if edit else ""
    return f'<section class="lb-topic lb-cat-{cat}">{head}<div class="lb-topic-grid">{"".join(cubes)}{add}</div></section>'
# the creator map's books tab hues (categories.json books-metrics), for the Metric preview
BK = {k: v["cat"] for k, v in json.load(open(os.path.join(HERE, "categories.json"), encoding="utf-8"))["sets"]["books-metrics"]["items"].items()}
FONTS_URL = "https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&family=Assistant:wght@400;500;600;700&display=swap"
LOGOS = {"logo_square.png": ("fced3317e50c510f4abe26ccb21e46f5", 141241), "logo_wide.png": ("b8b883e0138996754585bb68186ae69c", 90647)}


def block(selector_regex):
    m = re.search(selector_regex + r"\s*\{(.*?)\n\}", CSS, re.S | re.M)
    return dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", m.group(1))) if m else {}


light = block(r"^:root")
if not light:
    light = dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", CSS.split("@media")[0]))

COLOR_USAGE = {
    "lb-ink": "Brand ink.",
    "lb-ink-deep": "Brand ink, deepest.",
    "lb-gold": "Brand gold. never body text on light.",
    "lb-gold-deep": "Brand gold, deeper.",
    "lb-violet": "Brand violet.",
    "lb-cream": "Brand cream.",
    "bg": "Page ground: white.",
    "surface": "Cards, grouped rows, tables, inputs: white.",
    "surface-2": "Inset areas inside a card, table header row: pure light grey.",
    "sidebar": "A page's own sidebar (lb-sidebar), the inner one: pure light grey.",
    "sidenav": "The project nav's side bar (lb-gside), the outer one: the darkest pure grey, so it reads apart from the page sidebar.",
    "surface-sunk": "Wells, code blocks.",
    "bar": "Translucent sticky top bars (with backdrop blur).",
    "overlay": "Scrim behind drawers, modals and the mobile sidebar.",
    "overlay-2": "Backdrop behind an lb-dialog, a little darker so its floating cards stand out.",
    "glass": "Regular Liquid Glass: bars and small floating controls (translucent white over a blur).",
    "glass-thick": "Thick glass under text: menus, drawers, toasts, secondary buttons.",
    "glass-clear": "Clear glass over a photo or video: the play mark.",
    "glass-grey": "Glass of a page's own sidebar (lb-sidebar), the lighter grey, like sidebar.",
    "glass-grey-deep": "Glass of the project nav (lb-gside), the darker grey, like sidenav.",
    "text": "Primary text and headings. 4.5:1 or more on every surface.",
    "text-2": "Secondary text: descriptions, table cells that support a primary value.",
    "text-3": "Tertiary text: labels, captions, metadata.",
    "text-on-tint": "Text on a solid tint button or count.",
    "fill": "Quiet fill: hover rows, chips, search field, code (black at low alpha, pure grayscale).",
    "fill-2": "Tracks of bars, segmented control ground.",
    "fill-3": "Off state of a switch.",
    "line": "Hairline borders and dividers.",
    "line-strong": "Control borders, dashed empty states.",
    "tint": "Anything you can click: links, primary buttons, active nav, checked boxes.",
    "tint-hover": "Hover state of tint.",
    "tint-soft": "Soft tint ground: selected pill, tint chip, focus halo.",
    "focus": "Focus ring.",
    "accent": "Brand emphasis: progress fill, current week, sparkline.",
    "accent-soft": "Soft gold ground: callouts, accent chips, sparkline area.",
    "accent-ink": "Gold text that passes contrast: eyebrows, dates, accent chip text.",
    "success": "Good state text and dots.", "success-soft": "Good state ground.",
    "warning": "Needs attention text.", "warning-soft": "Needs attention ground.",
    "danger": "Broken or urgent text.", "danger-soft": "Broken or urgent ground.",
    "info": "Neutral information text.", "info-soft": "Neutral information ground.",
    "kid": "Carousel pillar 'הילד מספר' (kid) text.", "kid-soft": "Kid pillar ground.",
    "expert": "Carousel pillar 'גישה מקצועית' (expert) text.", "expert-soft": "Expert pillar ground.",
}
for i in range(1, 7):
    COLOR_USAGE[f"seq-{i}"] = f"Sequential data series step {i} of 6 (stages, bars), lightest to deepest."
CAT_HUES = {1: "orange", 2: "pink", 3: "green", 4: "blue", 5: "purple", 6: "teal", 7: "slate", 8: "ochre"}
CAT_PLAYBOOK = {1: "Hook", 2: "Keep them watching", 3: "Call to action", 4: "What to show", 5: "Editing", 6: "Topic", 7: "Filming", 8: "Text and caption"}
for i, hue in CAT_HUES.items():
    COLOR_USAGE[f"cat-{i}"] = f"Category {i} ({hue}; the playbook's {CAT_PLAYBOOK[i]}): tile, bar, card edge, swatch. Never under text."
    COLOR_USAGE[f"cat-{i}-ink"] = f"Category {i} text: chip, ID chip, eyebrow. 4.5:1 or more on surface, bg, surface-2 and its soft."
    COLOR_USAGE[f"cat-{i}-soft"] = f"Category {i} ground: chip, ID chip, current sub-item."

ORDER = ["lb-ink", "lb-ink-deep", "lb-gold", "lb-gold-deep", "lb-violet", "lb-cream",
         "bg", "surface", "surface-2", "surface-sunk", "sidebar", "sidenav", "bar", "overlay", "overlay-2",
         "glass", "glass-thick", "glass-clear", "glass-grey", "glass-grey-deep",
         "text", "text-2", "text-3", "text-on-tint", "fill", "fill-2", "fill-3", "line", "line-strong",
         "tint", "tint-hover", "tint-soft", "focus", "accent", "accent-soft", "accent-ink",
         "success", "success-soft", "warning", "warning-soft", "danger", "danger-soft", "info", "info-soft",
         "kid", "kid-soft", "expert", "expert-soft"] + [f"seq-{i}" for i in range(1, 7)] + \
        [f"cat-{i}{s}" for i in range(1, 9) for s in ("", "-ink", "-soft")]


def color_value(v):
    v = v.strip()
    return v.lower() if v.startswith("#") else v.replace(" ", "")


def tokens():
    colors = []
    for name in ORDER:
        if name not in light:
            continue
        val = {"light": color_value(light[name])}
        colors.append({"name": name, "value": val, "usage": COLOR_USAGE.get(name, "")})
    fam = {"sans": light["font"], "secondary": light["font-2"], "mono": light["font-mono"]}
    fam = {k: v.strip() for k, v in fam.items()}
    t = {
        "name": "LumeBook", "version": 1,
        "meta": {"source": "shared/design/lumebook.css (LumeBook project repo)"},
        "color": {"themes": [{"id": "light", "name": "White"}], "tokens": colors},
        "type": {"fonts": [], "families": fam, "groups": [
            {"name": "Display", "family": "sans", "styles": [
                {"name": "display", "fontSize": "38px", "lineHeight": 1.15, "fontWeight": 800, "sample": "לוח לומבוק", "usage": "Page titles (h1). Heebo ExtraBold, tracking -0.022em; once per page."},
                {"name": "title", "fontSize": "22px", "lineHeight": 1.25, "fontWeight": 700, "sample": "דורש תשומת לב", "usage": "Section titles (h2). Heebo Bold, tracking -0.014em."}]},
            {"name": "Text", "family": "sans", "styles": [
                {"name": "headline", "fontSize": "18px", "lineHeight": 1.3, "fontWeight": 700, "sample": "שבוע 2 · עכשיו", "usage": "Card titles (h3)."},
                {"name": "body", "fontSize": "16px", "lineHeight": 1.55, "fontWeight": 400, "sample": "ספר במתנה, קישור אישי עם הנחה לקהל ועד 25% עמלה.", "usage": "Running text, up to about 42rem wide."},
                {"name": "callout", "fontSize": "15px", "lineHeight": 1.5, "fontWeight": 400, "sample": "16 יוצרים במעקב", "usage": "Table cells, lists, buttons, nav items."},
                {"name": "footnote", "fontSize": "13px", "lineHeight": 1.45, "fontWeight": 500, "sample": "נבדק לפני 2 שע׳", "usage": "Labels, chips, metadata."},
                {"name": "caption", "fontSize": "12px", "lineHeight": 1.4, "fontWeight": 600, "sample": "עבודה", "usage": "Small running text in Heebo."}]},
            {"name": "Secondary", "family": "secondary", "styles": [
                {"name": "label", "fontSize": "13px", "lineHeight": 1.45, "fontWeight": 600, "sample": "מקור · נבדק לפני 2 שע׳", "usage": "Assistant: chips, table headers, stat labels, field labels, metadata, legends."},
                {"name": "eyebrow", "fontSize": "13px", "lineHeight": 1.4, "fontWeight": 700, "sample": "שבוע 2", "usage": "Assistant Bold in accent-ink or a category ink, above a title."},
                {"name": "count", "fontSize": "12px", "lineHeight": 1.4, "fontWeight": 700, "sample": "173", "usage": "Assistant Bold, tabular: counts, ID chips, sidebar group labels."}]},
            {"name": "Numbers", "family": "sans", "styles": [
                {"name": "stat", "fontSize": "30px", "lineHeight": 1.1, "fontWeight": 700, "sample": "918", "usage": "Big numbers in stat tiles; always tabular figures."}]},
            {"name": "Code", "family": "mono", "styles": [
                {"name": "code", "fontSize": "14px", "lineHeight": 1.5, "fontWeight": 400, "sample": "python3 tools/lumebook.py ripple", "usage": "Commands and file paths."}]},
        ]},
        "spacing": {"note": "4pt base. Gaps between siblings come from flex or grid gap, never margins.",
                    "tokens": [{"name": f"sp-{i}", "value": light[f"sp-{i}"].strip(), "usage": u} for i, u in
                               [(1, "Hairline gaps, chip internals."), (2, "Gap inside a row of chips or buttons."), (3, "Gap inside a card."),
                                (4, "Gap between cards in a grid; card padding (block)."), (5, "Card padding (inline); page gutter."),
                                (6, "Gap between sections."), (7, "Page bottom padding.")]]},
        "radius": {"tokens": [{"name": n, "value": light[n].strip(), "usage": u} for n, u in
                              [("r-xs", "Code, bars, small marks."), ("r-sm", "Inputs, small controls."),
                               ("r-md", "Nav items, alerts, empty states, inner corners of a card."), ("r-lg", "Cards, tables, grouped lists, menus."), ("r-xl", "Floating glass: the nav panel, a page sidebar, sheets, drawers, dialogs."), ("r-pill", "Buttons, chips, search, switches, segmented controls, the phone tab bar.")]]},
        "shadow": {"tokens": [{"name": n, "value": {"light": light[n].strip()}, "usage": u} for n, u in
                              [("shadow-1", "Cards, active nav item, segmented thumb: a close contact shadow."), ("shadow-2", "Raised card, hovered link card."), ("shadow-3", "Drawers, modals, menus, toasts, mobile sidebar.")]]},
    }
    return t


README = """# LumeBook

The design system for every internal LumeBook page: the project dashboard (לוח לומבוק), the SMM plan, the creator map, the research reports and the nightly carousel review. It is Hebrew first and right to left, white only, and built for scanning operational data.

It is **not** used by the public ambassadors site (lumebook-ambassadors.vercel.app), which keeps its own look for creators, or by the carousel slides themselves, whose two pillar looks are audience content.

## Where it lives

- Source of truth: `shared/design/lumebook.css` in the LumeBook project repo. Every page build inlines it (`shared/design/design.py`: `design.head()`, `design.logo_data_uri()`). The SMM plan has no build, so it links a synced copy (`tools/lumebook.py sync`).
- After any change: `python3 tools/lumebook.py ripple` rebuilds every page that uses it and lists the artifacts to republish.
- This reference is generated from that file by `shared/design/build_ds_artifact.py`. Edit the CSS, not this page.

## Content fundamentals

- Hebrew first, everyday Israeli Hebrew, written the way Yarin talks: short, direct, first person or plural. English pages (some research reports) follow the same layout, left to right.
- No em dashes anywhere. Use commas, colons or periods.
- The brand is **LumeBook** in Latin letters and **לומבוק** in Hebrew. Never לומיבוק.
- The creator offer is a personal link with an audience discount and up to 25% commission (עד 25%). Never "קוד הנחה" or "קוד אישי".
- Audience copy never mentions AI.
- Labels name what a person recognizes ("משימות פתוחות", "לפרסם מחדש"), not how the system is built.
- Dates as dd / mm / yyyy (30 / 10 / 2026; Yarin, 30 Oct 2026), numbers with tabular figures. Dates, handles, paths and numbers with signs are isolated left to right (`<bdi class="lb-ltr">`, `dir="ltr"` on an input): inside Hebrew a bare date flips to 2026 / 10 / 30.

## Visual foundations

- **Surfaces.** A white page (`bg`) and glass cards (a translucent grayscale body, a specular rim and a soft lift: `--glass-card`, `--glass-card-rim`, `--glass-card-lift`; Yarin, 07 Nov 2026) instead of hairline boxes, a light grey page sidebar (`sidebar`, the inner one), a darker grey project nav side bar (`sidenav`, the outer one) and inset areas (`surface-2`). Every surface and fill is pure grayscale (equal R, G, B); only text, lines and shadows carry a slight LumeBook tint (hue 33), never pure black (Yarin, 06 Nov 2026). Hierarchy comes from surface steps and hairlines (`line`), with shadows only on things that float.
- **Three roles for color.** `text` (neutral ink, near black) for reading; `tint` (violet) for anything you can click, and only for that; `accent` (gold) for brand emphasis and progress. Gold text uses `accent-ink` so it passes contrast.
- **State is shape plus color.** Status always appears as a chip, dot, count or tinted alert row with a word, never color alone. `success`, `warning`, `danger`, `info` are separate from the accent.
- **Carousel pillars.** `kid` (violet) for "הילד מספר", `expert` (gold) for "גישה מקצועית", matching the slide designs.
- **Category colour.** Eight hues (`cat-1` to `cat-8`, each with a base, an ink and a soft) for a page's 3 to 8 stable categories that a reader scans or filters by: the playbook's tools, the dashboard's workstreams, the creator map's tracks and the numbers on its books tab. See "Category colour" below.
- **Type.** Heebo is the main font, headings included (h1 ExtraBold 800, h2 Bold 700, slightly tight tracking); Assistant is the secondary font for labels, captions, counts, chips, table headers and the sidebar group labels. Both carry Hebrew and Latin. Body text, buttons and inputs stay on Heebo. System mono for commands. Scale: display 38, title 22, headline 18, body 16, callout 15, footnote 13, caption 12. Varela Round was dropped on 18 Oct 2026.
- **Space and shape.** 4pt spacing, pill buttons and chips, 20px card radius, 28px for floating glass. Corners are concentric (an inner corner is its container's radius minus the padding between them), as in iOS 26. Touch screens get 44px targets and 16px fields.
- **Colours.** Vibrant (Yarin, 06 Nov 2026: "lets go back to vibrant colors"): violet to click, gold for emphasis and the eight category hues at full colour. Earlier that day the palette was lumebook.com/IL/he's; that was undone.
- **Theme.** Light only (Yarin, 05 Nov 2026: "only white mode from now on"). One set of tokens on `:root`; no black mode, no theme switch, no `prefers-color-scheme`. The black mode and its switch (21 Oct 2026) are gone, and so are the cream and purple grounds before it. `design.theme_toggle()` returns nothing. Every text token passes 4.5:1 on every surface.
- **Motion.** Short and springy (0.14s to 0.42s, `--ease` and `--ease-spring`), never decorative: press states scale to 97%, the switch knob stretches, cubes and link cards lift. All of it stops under `prefers-reduced-motion`.
- **Liquid Glass** (Yarin, 07 Nov 2026: "apply apple design principles and latest liquid glass to the entire project"). Two layers, both glass. Every card is Liquid Glass (Yarin, 07 Nov 2026: "construct every card in the design system to look like apple made it using liquid glass"): a translucent grayscale body that is bright at the lit corner, a specular rim and glow, a two-layer lift (`--glass-card`, `--glass-card-rim`, `--glass-card-lift`), no blur when repeated; tables, text, tiles and charts stay opaque. The control layer above the content (project nav, top and edit bars, menus, sheets, drawers, toasts, buttons, switches, segmented controls) is Liquid Glass: a translucent grayscale tint over a blurred, saturated copy of what is behind it, a bright specular rim on the top edge, a darker one below, and a soft lift shadow (`--glass`, `--glass-thick`, `--glass-clear`, `--glass-rim`, `--glass-lift`; the `lb-glass` class and its `is-thick`, `is-clear`, `is-tint`, `is-capsule` and `is-interactive` variants). Rules of the material: never glass on glass, always legible (thick glass under text), tinted only through `lb-glass is-tint` (violet), and nothing repeated in a list carries a backdrop blur. It falls back to flat white and grey surfaces for more contrast and browsers without `backdrop-filter` (and for Reduce Transparency on a page that sets `data-honor-transparency`, as the public creator brief does; the internal tools ignore that setting so the glass shows). Full-width sticky bars use the most transparent glass (`--glass-bar`) and the faded edge of `lb-edge`. On a mouse, the select list, date calendar and time clock are glass popups too (`lb-selmenu`, `lb-cal`, `lb-timepick`, drawn by `controls.src.js`); touch screens keep the system pickers. The project nav and a page's own sidebar are floating panels inset from the window edge (the nav the darker grey, the sidebar the lighter), the phone tab bar is a floating capsule. Carousel slides and the retired ambassadors site keep their own looks.

## Layout

- App pages: `lb-app` (sidebar + main), `lb-sidebar` with `lb-nav-item`s grouped by `lb-nav-label`, a sticky `lb-topbar`, content in `lb-page` > `lb-section` blocks. Under 860px the sidebar becomes a drawer opened from `lb-menu-btn`.
- Reading pages and reports: `lb-topbar` with logo, page name, an `lb-toc` section nav, and the link back to the dashboard; then `lb-page`.
- Grids: `lb-grid` (auto-fit, set `--min`), or `cols-2/3/4` that step down to 2 then 1 column. Rows: `lb-row`, stacks: `lb-stack`.
- Phone width (390px) never scrolls sideways; wide tables scroll inside `lb-table-wrap`.

## Type pairing

| Role | Font | Weight | Where |
|---|---|---|---|
| Page title (h1) | Heebo | 800 | Once per page, `--fs-display` |
| Section title (h2) | Heebo | 700 | `--fs-title` |
| Card title (h3), body, buttons, inputs, nav items | Heebo | 400 to 700 | Everything you read or press |
| Labels, eyebrows, chips, counts, table headers, legends, captions, field labels, metadata | Assistant (`--font-2`) | 600 to 700 | Anything that names or counts rather than says |

Use `lb-font-2` to put any other element on the secondary font. Fonts link: `{{FONTS_URL}}`.

## Category colour

Eight hues for categories, kept apart from status (`success`, `warning`, `danger`, `info`), the carousel pillars (`kid`, `expert`) and the brand violet and gold. They came from the Product Reels Playbook (18 Oct 2026), where each of the eight tools owns one; the playbook's names are aliases, not the token names.

{{PALETTE}}

**Contrast** (computed from the stylesheet; text needs 4.5:1):

{{CONTRAST}}

**Rules**

- Use category colour only where a page already has 3 to 8 stable categories that a reader scans or filters by. A page with no categories, or with more than 8, gets none. Never invent categories to have something to colour.
- **A category colour is never also a status colour.** Done, late, broken, waiting: status chips with a word. A category says what something is, never how it is doing. Never colour the carousel pillars or a state with these hues.
- One category, one hue, everywhere it appears on the page: sidebar tile, chip, ID chip, chart bar, card edge, legend swatch. Within a set every category gets a different hue.
- The mapping lives in `shared/design/categories.json`, never in a page: builds read it (`design.head()` adds a `.lb-<set>-<key>` class per category, `design.cat_class()`, `design.category_css()`); the dashboard and the SMM plan link the synced `categories.css`.
- Base colours mark things (tiles, bars, edges, swatches) and never sit under text: white text fails on most of them. Text in a category colour uses its ink, on surface, bg, surface-2 or its own soft.
- Category chips carry a small square swatch; status chips carry a dot or a word. Shape plus word, never colour alone.
- Where a page also shows status, prefer hues 2, 4, 5, 6 and 7: 1 sits near warning, 3 near success and 8 near the gold accent.
- Add one legend only where the colour is not already labelled next to it (a chart, a stacked bar). A labelled chip or tile is its own legend.

## Iconography

Inline SVG line icons on a 24 grid, `stroke="currentColor"`, stroke width 2, no fill, so they take the text color. No emoji as UI markers. The set lives in `shared/design/icons.json` (Icons group): `icons` for tools and topics, `ui` for interface glyphs; names never change. Builds use `design.icon(name)`, pages without a build link the synced `design/icons.js`. The LumeBook logo is the only image mark (Logos group).

## Components

Each has a live preview and guidelines in Components. All class names start with `lb-` so a page can adopt the system one piece at a time.
"""

_I = {"gift": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M5 12v9h14v-9M12 8C10.5 5 7 4.5 7 7s3 1 5 1c2 0 5 1.5 5-1s-3.5-2-5 1"/></svg>',
      "check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
      "eye": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
      "heart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-8-4.8-8-10.2A4.3 4.3 0 0 1 12 8a4.3 4.3 0 0 1 8 1.8C20 15.2 12 20 12 20z"/></svg>',
      "comment": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11h-9l-5 4v-4H4z"/></svg>'}

COMPONENTS = {
    "Button": ("Actions", 120, "Pill buttons. Primary (tint) for the one main action in a view, `secondary` for everything else, `ghost` for inline actions, `danger` only to remove something; `quiet` (grey, red on hover) for an icon action repeated on every row, such as removing the row, so a table does not shout. Sizes: default and `sm`; `icon` for square icon buttons with an `aria-label`.",
               '<div dir="rtl" lang="he" class="lb-row" style="padding:16px"><button class="lb-btn" type="button">לפרסם מחדש</button><button class="lb-btn secondary" type="button">לתוכנית המלאה</button><button class="lb-btn ghost" type="button">פתיחה</button><button class="lb-btn secondary sm" type="button">להציג 2 שורות בדיקה</button><button class="lb-btn secondary sm icon" type="button" aria-label="עוד">+</button><button class="lb-btn" type="button" disabled>לא זמין</button></div>'),
    "Segmented": ("Actions", 90, "A small set of mutually exclusive filters. Each button carries `aria-pressed`. Use for 2 to 5 options; more belong in a select.",
                  '<div dir="rtl" lang="he" style="padding:16px"><div class="lb-segmented" role="group" aria-label="קבוצה"><button type="button" aria-pressed="true">הכול</button><button type="button" aria-pressed="false">ברטר</button><button type="button" aria-pressed="false">בתשלום</button><button type="button" aria-pressed="false">שורטליסט</button></div></div>'),
    "Field": ("Forms", 170, "Inputs, selects and the search field. Every control has a visible label (`lb-field`) or an `aria-label`. The search field is a pill on a quiet fill.",
              '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px;max-width:360px"><div class="lb-search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg><input class="lb-input" type="search" placeholder="חיפוש יוצר" aria-label="חיפוש יוצר"></div><label class="lb-field">שם היוצר<input class="lb-input" value="אורי"></label><label class="lb-field">מצב<select class="lb-select"><option>נשלחה פנייה</option><option>ענו</option></select></label></div>'),
    "Check": ("Forms", 130, "Checkbox rows for task lists. A checked task strikes through and dims. The tick is drawn with physical borders so it never mirrors on RTL pages.",
              '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px"><label class="lb-check"><input type="checkbox" checked><span>לסגור את הבריף לרילס של השבוע</span></label><label class="lb-check"><input type="checkbox"><span>לשלוח 5 פניות ליוצרים מהברטר</span></label><label class="lb-check"><input type="checkbox" disabled><span>קריאה בלבד</span></label></div>'),
    "Switch": ("Forms", 80, "An on and off setting that applies immediately. Use a checkbox for list items and a switch for settings.",
               '<div dir="rtl" lang="he" class="lb-row" style="padding:16px;gap:12px"><input class="lb-switch" type="checkbox" checked aria-label="תזכורת בוקר"><span>תזכורת בוקר</span><input class="lb-switch" type="checkbox" aria-label="כבוי"><span class="lb-muted">כבוי</span></div>'),
    "Stat": ("Data", 200, "A stat tile: label, big tabular number with an optional delta or small unit, a one-line foot, optional bar and sparkline. Open a dashboard with stat tiles only when the numbers are the point.",
             '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-card lb-stat"><span class="lb-stat-label">עוקבים <bdi class="lb-ltr">@lumebookai</bdi></span><span class="lb-stat-value">918<small class="lb-delta up"><bdi class="lb-ltr">+12</bdi></small></span><div class="lb-bar"><i style="width:31%"></i></div><span class="lb-stat-foot">יעד דצמבר 3-4K</span></div><div class="lb-card lb-stat"><span class="lb-stat-label">מאגר יוצרים</span><span class="lb-stat-value">204<small>15 בשורטליסט</small></span><span class="lb-stat-foot">12 בסבב ברטר ראשון</span></div></div>'),
    "Table": ("Data", 210, "Data tables sit in `lb-table-wrap`, which scrolls sideways on its own. Numbers get `num` (tabular, aligned to the end). `is-roomy` for a table people work in all day: larger header labels and taller rows. Header row on `surface-2`; rows highlight on hover. `top` aligns cells to the top; `mid` (40rem) and `wide` (56rem) set a minimum width so the wrap scrolls instead of squeezing; `is-stack` turns each row into a labelled card on a phone (put `data-label` on every td).",
              '<div dir="rtl" lang="he" style="padding:16px"><div class="lb-table-wrap"><table class="lb-table"><thead><tr><th>מדד</th><th>מקור</th><th class="num">אוקטובר</th><th class="num">יעד דצמבר</th></tr></thead><tbody><tr><td>עוקבים באינסטגרם</td><td class="lb-muted">Instagram</td><td class="num">918</td><td class="num">3-4K</td></tr><tr><td>סרטוני לקוחות</td><td class="lb-muted">אקסל</td><td class="num">10</td><td class="num">25</td></tr></tbody></table></div></div>'),
    "Hbars": ("Data", 170, "Horizontal bars for ranked counts: label, track, value. One scale per list (the longest bar is the largest value). Use `--seq-*` for stacked stage bars with a legend.",
              '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px"><div class="lb-hbars"><div class="lb-hbar"><span>הדגמת מוצר</span><span class="track"><i style="width:100%"></i></span><span class="v">38</span></div><div class="lb-hbar"><span>סיפור לקוח</span><span class="track"><i style="width:63%"></i></span><span class="v">24</span></div><div class="lb-hbar"><span>מתנה ואירוע</span><span class="track"><i style="width:42%"></i></span><span class="v">16</span></div></div><div class="lb-stages"><i style="flex:9;background:var(--seq-1)"></i><i style="flex:4;background:var(--seq-2)"></i><i style="flex:2;background:var(--seq-4)"></i><i style="flex:1;background:var(--seq-6)"></i></div><div class="lb-legend"><span><b style="background:var(--seq-1)"></b>לא פנינו 9</span><span><b style="background:var(--seq-2)"></b>נשלחה פנייה 4</span><span><b style="background:var(--seq-4)"></b>ספר בהכנה 2</span><span><b style="background:var(--seq-6)"></b>פורסם 1</span></div></div>'),
    "Chip": ("Status", 110, "Short status words in the secondary font (Assistant). Neutral by default; `tint`, `accent`, `success`, `warning`, `danger`, `info`, and the pillars `kid` and `expert`; `outline` for tags; `cat` (with an `lb-cat-N` class) for a category, which adds a square swatch. Add `lb-dot` for live or health state. A chip always carries a word, never color alone.",
             '<div dir="rtl" lang="he" class="lb-row" style="padding:16px"><span class="lb-chip">שורטליסט</span><span class="lb-chip tint">סנכרון</span><span class="lb-chip accent">ברטר</span><span class="lb-chip success"><span class="lb-dot"></span>באוויר</span><span class="lb-chip warning">לפרסם מחדש</span><span class="lb-chip danger">מחזיר 500</span><span class="lb-chip info">לוודא עם יוסי</span><span class="lb-chip kid">kid-2 · הילד מספר</span><span class="lb-chip expert">expert-1 · גישה מקצועית</span><span class="lb-chip outline">רגע</span><span class="lb-count">16</span><span class="lb-count is-alert">3</span></div>'),
    "Category": ("Category", 260, "Category colour for a page's 3 to 8 stable categories (see the README). Put `lb-cat-1` ... `lb-cat-8` (or a generated `.lb-<set>-<key>` class from categories.json) on the row, card or nav item; the pieces inside read it. `lb-tile` is the category's mark (icons only; `is-soft` for a letter or number; `lg`, `xl`). `lb-chip cat` adds a square swatch so it never reads as a status chip. `lb-pid` is a short ID in the category's ink. `lb-card is-cat` draws the edge, `lb-hbar is-cat` the bar, `lb-swatch` the legend mark. Never use it for state.",
                 '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px">'
                 '<div class="lb-row">' + "".join(f'<span class="lb-tile lb-cat-{i}">' + '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>' + '</span>' for i in range(1, 9)) + '</div>'
                 '<div class="lb-row"><span class="lb-chip cat lb-cat-4">תוכנית ואסטרטגיה</span><span class="lb-chip cat lb-cat-2">יוצרים</span><span class="lb-chip cat lb-cat-5">קרוסלות</span><span class="lb-chip cat lb-cat-1">רילס ווידאו</span><span class="lb-chip cat lb-cat-7">מתחרים</span><span class="lb-chip cat lb-cat-6">קהילות</span><span class="lb-chip success"><span class="lb-dot"></span>באוויר</span></div>'
                 '<div class="lb-row"><span class="lb-pid lb-cat-1">H1</span><span class="lb-pid lb-cat-2">R3</span><span class="lb-pid lb-cat-3">C2</span><a class="lb-pid lb-cat-4" href="#">S1</a><span class="lb-tile is-soft lb-cat-6">3</span><span class="lb-eyebrow cat lb-cat-5">כלי 5 מתוך 8</span></div>'
                 '<div class="lb-grid cols-2"><div class="lb-card is-cat lb-cat-6"><span class="lb-card-title">Hooray Heroes</span><div class="lb-hbars"><div class="lb-hbar is-cat"><span>הדגמת מוצר</span><span class="track"><i style="width:100%"></i></span><span class="v">12</span></div><div class="lb-hbar is-cat"><span>סיפור לקוח</span><span class="track"><i style="width:55%"></i></span><span class="v">7</span></div></div></div>'
                 '<div class="lb-card"><div class="lb-stages"><i class="lb-swatch lb-cat-4" style="flex:5"></i><i class="lb-swatch lb-cat-2" style="flex:3"></i><i class="lb-swatch lb-cat-5" style="flex:2"></i></div><div class="lb-legend"><span><b class="lb-swatch lb-cat-4"></b>תוכנית 5</span><span><b class="lb-swatch lb-cat-2"></b>יוצרים 3</span><span><b class="lb-swatch lb-cat-5"></b>קרוסלות 2</span></div></div></div></div>'),
    "Disclosure": ("Layout", 230, "Secondary detail behind a toggle, the way the Reels playbook keeps each page short: the summary says what is inside (an optional `small` line under it), the chevron points forward and turns down when open. `is-quiet` drops the box inside a card; `is-cat` marks an open one with its category edge. Keep the main point outside; put sources, method, long profiles and examples inside. Not for text someone edits in the site editor.",
                   '<div dir="rtl" lang="he" class="lb-disclosures" style="padding:16px;max-width:520px"><details class="lb-disclosure" open><summary><span class="lb-sum">מקורות<small>4 מחקרים ועמודי פלטפורמה</small></span></summary><div class="lb-disclosure-body"><p class="lb-small">כל מקור נפתח בזמן המחקר. הנתונים הציבוריים נבדקו ב-15.10.</p></div></details><details class="lb-disclosure is-cat lb-cat-1"><summary><span class="lb-sum">למה הראיות מדורגות כבינוניות</span></summary><div class="lb-disclosure-body"><p class="lb-small">שני מחקרים, מדגם קטן.</p></div></details></div>'),
    "SourceList": ("Layout", 300, "An Apple-style source list: `lb-nav-item` with an `lb-tile` (the category's colour) and an optional plain count (`lb-nav-n`) or a pill count (`lb-count`). The current item keeps ink text in bold; its children open in `lb-nav-sub` under it, edged in the category's soft colour, with `lb-pid` IDs. Items without a category keep a line icon.",
                   '<div dir="rtl" lang="he" style="padding:16px;max-width:280px"><nav class="lb-nav" style="background:var(--surface-2);padding:12px;border-radius:var(--r-lg)"><div class="lb-nav-label">כלים</div><a class="lb-nav-item lb-cat-1" href="#" aria-current="page"><span class="lb-tile">' + '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>' + '</span><span class="lb-nav-text">הוק</span><span class="lb-nav-n">8</span></a><div class="lb-nav-sub lb-cat-1"><a href="#" aria-current="page"><span class="lb-pid">H1</span><span>מבחן הדילוג של 3 שניות</span></a><a href="#"><span class="lb-pid">H2</span><span>להראות את הערך מוקדם</span></a></div><a class="lb-nav-item lb-cat-2" href="#"><span class="lb-tile">' + '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>' + '</span><span class="lb-nav-text">להמשיך לצפות</span><span class="lb-nav-n">9</span></a><a class="lb-nav-item lb-cat-3" href="#"><span class="lb-tile">' + '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>' + '</span><span class="lb-nav-text">קריאה לפעולה</span><span class="lb-nav-n">7</span></a></nav></div>'),
    "Alert": ("Status", 170, "Rows in the attention list: a severity chip, one sentence, an optional link. `crit` and `warn` tint the whole row; info rows stay on the surface. Sort critical first.",
              '<div dir="rtl" lang="he" class="lb-alerts" style="padding:16px"><div class="lb-alert crit"><span class="lb-chip danger">אתר</span><span class="lb-alert-text">דף השגרירים מחזיר 500</span><a href="#">פתיחה</a></div><div class="lb-alert warn"><span class="lb-chip warning">אינסטגרם</span><span class="lb-alert-text">אינסטגרם לא החזיר את הפרופיל היום</span><a href="#">פתיחה</a></div><div class="lb-alert info"><span class="lb-chip info">לוודא עם יוסי</span><span class="lb-alert-text">דדליין הזמנות לחנוכה עוד לא מאושר</span><span></span></div></div>'),
    "Callout": ("Status", 330, "A tinted note for how-to or context inside a page. Gold by default, `info` for neutral help, `success`, `warning` and `danger` for a result or a caution. `has-icon` puts a line icon in its own column at the start. One per section at most.",
                '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px"><div class="lb-callout info"><b>לעבור על החבילה ולערוך</b><span>החבילה נבנית כל לילה ב-22:00. לעריכה במקום: <code class="lb-ltr">review_server.py</code></span></div><div class="lb-callout success has-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg><b>הבדיקה עברה</b><span>כל 10 השקופיות בגודל הנכון.</span></div><div class="lb-callout warning has-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg><b>לבדוק לפני פרסום</b><span>בשקופית 4 יש שתי שורות ארוכות.</span></div><div class="lb-callout danger"><b>התמונה לא נוצרה</b><span>התקציב שאושר נגמר. צריך אישור חדש.</span></div></div>'),
    "Card": ("Layout", 190, "The main container. `is-quiet` for secondary groupings, `is-raised` for one floating element, `is-accent` for the current item (this week). A card that is a link uses `<a class=\"lb-card\">` and lifts on hover. Since 7 Nov 2026 every card is Liquid Glass: a translucent grayscale body that is bright at the lit corner, a specular rim and glow, a two-layer lift; a tinted card (`is-cat`, `lb-tinted`, `lb-metric`, `lb-cube`, the status alerts and callouts) lays its tint over the glass body. `is-glass` adds the blur to one feature card; `lb-glass-card` gives a page's own card class the same look; `lb-ground` is an optional colour wash behind a section whose glass should show.",
             '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-card is-accent"><div class="lb-card-head"><span class="lb-card-title">שבוע 2 · עכשיו</span><span class="lb-xs lb-dim">3/7</span></div><span>לסגור בריף, לשלוח פניות, לבדוק חבילה</span></div><a class="lb-card" href="#"><span class="lb-chip accent">מחקר תוכן</span><b>מחקר קרוסלות</b><span class="lb-muted lb-small">752 חשבונות בישראל ובעולם</span></a></div>'
             '<div dir="rtl" lang="he" style="padding:0 16px 16px"><div class="lb-ground"><div class="lb-grid cols-2" style="gap:16px"><div class="lb-card"><div class="lb-card-head"><span class="lb-card-title">כרטיס זכוכית על רקע צבעוני</span></div><span class="lb-muted lb-small">הגוף שקוף, הקצה בוהק והצל רכה: הצבע שמאחור נראה דרכו.</span></div>'
             '<dl class="lb-metrics" style="grid-template-columns:1fr 1fr;gap:12px"><div class="lb-metric lb-cat-4"><dt class="lb-metric-label">צפיות</dt><dd class="lb-metric-value">7,169</dd></div><div class="lb-metric lb-cat-3"><dt class="lb-metric-label">יוצרים</dt><dd class="lb-metric-value">437</dd></div></dl>'
             '<div class="lb-callout info"><b>תובנה</b><span>גם הודעות וכרטיסי סטטוס הם זכוכית מוצללת בצבע.</span></div><article class="lb-card is-cat lb-cat-2"><span class="lb-card-title">כרטיס בצבע קטגוריה</span><span class="lb-small">הגוון מונח על גוף הזכוכית.</span></article></div></div></div>'),
    "Group": ("Layout", 150, "An Apple-style inset grouped list: rows separated by hairlines inside one rounded container. Rows can be links; metadata sits at the end.",
              '<div dir="rtl" lang="he" style="padding:16px;max-width:420px"><div class="lb-group"><a class="lb-group-row" href="#"><span>טופס יוצרי תוכן</span><span class="lb-meta">Google Form</span></a><a class="lb-group-row" href="#"><span>גיליון ההרשמות</span></a><a class="lb-group-row" href="#"><span>תיקיית שיווק בדרייב</span></a></div></div>'),
    "Navigation": ("Layout", 260, "Sidebar navigation for app pages: group labels, items with a 24-grid line icon, an optional count, `aria-current=\"page\"` on the current view. Under 860px the sidebar becomes a drawer.",
                   '<div dir="rtl" lang="he" style="padding:16px;max-width:260px"><nav class="lb-nav" style="background:var(--surface-2);padding:12px;border-radius:var(--r-lg)"><div class="lb-nav-label">היום</div><a class="lb-nav-item" href="#" aria-current="page"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>סקירה<span class="lb-count is-alert">3</span></a><div class="lb-nav-label">עבודה</div><a class="lb-nav-item" href="#"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/></svg>תוכנית<span class="lb-count">10</span></a><a class="lb-nav-item" href="#"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/></svg>יוצרים</a></nav></div>'),
    "Toc": ("Layout", 80, "Pill section navigation for reading pages and reports, usually inside the top bar. The current section gets `aria-current=\"true\"`.",
            '<div dir="rtl" lang="he" style="padding:16px"><nav class="lb-toc"><a href="#" aria-current="true">שבועות</a><a href="#">יעדים</a><a href="#">מדדים</a><a href="#">סרטונים שעבדו</a><a href="#">לוודא עם יוסי</a></nav></div>'),
    "Empty": ("Feedback", 110, "Empty and loading states say what will appear and how it gets there. Use `lb-skeleton` blocks while data loads.",
              '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-empty">חבילת הלילה תופיע כאן אחרי הריצה הבאה ב-22:00.</div><div class="lb-stack"><div class="lb-skeleton" style="height:1.2rem;width:60%"></div><div class="lb-skeleton" style="height:2.4rem"></div></div></div>'),
    "Text": ("Type", 340, "Text helpers. `lb-eyebrow` (Assistant Bold in `accent-ink`, or `cat` in a category ink) sits above a title; `lb-lede` is the one intro paragraph under the h1; `lb-muted` and `lb-dim` step text down to `text-2` and `text-3`; `lb-small` and `lb-xs` set callout and footnote size; `lb-num` gives tabular figures; `lb-ltr` isolates handles, paths and numbers inside Hebrew; `lb-truncate` cuts one line with an ellipsis; `lb-prose` keeps running text to 42rem; `lb-note` is a small source or method line; `lb-font-2` puts any element on the secondary font; `lb-sr` hides text on screen but keeps it for screen readers.",
             '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px;max-width:560px"><span class="lb-eyebrow">שבוע 2 · נובמבר</span><h1 style="font-size:1.75rem">מפת היוצרים</h1><p class="lb-lede">כל היוצרים שאנחנו עוקבים אחריהם, עם המסלול, ההודעה הבאה והביצועים.</p><div class="lb-prose"><p>הפנייה האחרונה נשלחה ל-<bdi class="lb-ltr">@topaz_meir_slp</bdi> לפני <span class="lb-num">3</span> ימים.</p></div><p class="lb-muted lb-small">משני: תיאור או הסבר קצר</p><p class="lb-dim lb-xs lb-truncate" style="max-width:260px">שלישי: תאריך, מקור או מידע נלווה שנחתך בסוף השורה</p><p class="lb-note">מקור: ייצוא אינסטגרם, נקרא <bdi class="lb-ltr">24 / 10 / 2026</bdi></p></div>'),
    "PageLayout": ("Layout", 420, "Page structure. `lb-page` centres the content (76rem at most, a gutter on each side, 2rem between sections); each block is an `lb-section` opened by an `lb-section-head` (the h2 and an `lb-meta` line); `lb-footer` closes the page. Inside a section: `lb-grid` (auto-fit, set `--min`) or `cols-2`, `cols-3`, `cols-4`, which step down to 2 and then 1 column; `lb-stack` for a column; `lb-row` for a wrapping row (`between` spreads it); `lb-spacer` pushes what follows to the end. Gaps come from the grid, never margins.",
                   '<div dir="rtl" lang="he" class="lb-page" style="padding-block:16px;gap:16px"><section class="lb-section"><div class="lb-section-head"><h2>השבוע</h2><span class="lb-meta">עודכן היום ב-08:15</span></div><div class="lb-grid cols-3"><div class="lb-card is-quiet"><b>3 קרוסלות</b><span class="lb-dim lb-xs">שני, רביעי, שישי</span></div><div class="lb-card is-quiet"><b>7 רילס</b><span class="lb-dim lb-xs">ריל ביום</span></div><div class="lb-card is-quiet"><b>12 פניות</b><span class="lb-dim lb-xs">ליוצרים חדשים</span></div></div><div class="lb-row"><span class="lb-chip">טיוטה</span><span class="lb-spacer"></span><button class="lb-btn sm secondary" type="button">לכל השבוע</button></div></section><footer class="lb-footer"><span>פנימי. נבנה מ-<bdi class="lb-ltr">shared/design</bdi>.</span></footer></div>'),
    "AppShell": ("Layout", 320, "The frame for a tool with several views. `lb-app` puts an `lb-sidebar` (with `lb-brand` at the top and `lb-sidebar-foot` at the bottom) beside `lb-main`, which starts with a sticky translucent `lb-topbar` (`lb-topbar-in` holds the page name, actions and an `lb-menu-btn`). Under 860px the sidebar slides in from the start edge over an `lb-scrim`. Reading pages skip the sidebar and keep only the top bar with an `lb-toc`.",
                 '<div dir="rtl" lang="he" class="lb-app" style="min-height:300px;grid-template-columns:13rem minmax(0,1fr)"><aside class="lb-sidebar" style="position:static;height:300px"><a class="lb-brand" href="#"><img src="/_blob/fced3317e50c510f4abe26ccb21e46f5" alt=""><span><b>לומבוק</b><small>לוח העבודה</small></span></a><nav class="lb-nav"><div class="lb-nav-label">היום</div><a class="lb-nav-item" href="#" aria-current="page">סקירה <span class="lb-count is-tint">4</span></a><a class="lb-nav-item" href="#">יוצרים</a><a class="lb-nav-item" href="#">קרוסלות</a></nav><div class="lb-sidebar-foot">מתעדכן כל בוקר</div></aside><div class="lb-main"><header class="lb-topbar"><div class="lb-topbar-in"><h1>סקירה</h1><span class="lb-spacer"></span><span class="lb-chip success"><span class="lb-dot"></span>מעודכן</span></div></header><div class="lb-page" style="padding-block:16px"><div class="lb-card"><span class="lb-card-title">תוכן העמוד</span><span class="lb-dim lb-small">כל תצוגה היא lb-page בתוך lb-main</span></div></div></div></div>'),
    "Tabs": ("Actions", 150, "`lb-tabs` switches between views of the same thing: each tab is a button with `aria-selected` (or a link with `aria-current`), the current one underlined in tint; the row scrolls sideways on a phone. `lb-toolbar` is the wrapping row of controls above a list or table: search first, then filters, the main action last.",
             '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px"><div class="lb-tabs" role="tablist"><button type="button" role="tab" aria-selected="true">כולם</button><button type="button" role="tab" aria-selected="false">במעקב</button><button type="button" role="tab" aria-selected="false">ספרים שנוצרו</button><button type="button" role="tab" aria-selected="false">תזכורות</button></div><div class="lb-toolbar"><div class="lb-search" style="flex:1;min-width:160px"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg><input class="lb-input" type="search" placeholder="חיפוש יוצר" aria-label="חיפוש יוצר"></div><div class="lb-segmented" role="group" aria-label="מסלול"><button type="button" aria-pressed="true">הכול</button><button type="button" aria-pressed="false">הורים</button><button type="button" aria-pressed="false">אנשי מקצוע</button></div><button class="lb-btn sm" type="button">יוצר חדש</button></div></div>'),
    "KeyValue": ("Data", 260, "`lb-kv` is a two-column list of facts about one thing: the label in Assistant on the start side, the value in Heebo beside it. `lb-list` is a plain list where each item has a title and an `lb-meta` line under it. `lb-kv stack` drops to one column on a phone; `lb-kv tight` is the smaller version for side panels and drawers.",
                 '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-card"><span class="lb-card-title">פרטי היוצרת</span><dl class="lb-kv"><dt>חשבון</dt><dd><bdi class="lb-ltr">@topaz_meir_slp</bdi></dd><dt>עוקבים</dt><dd class="lb-num">18.4K</dd><dt>מסלול</dt><dd><span class="lb-chip cat lb-track-pro">אנשי מקצוע</span></dd><dt>ילדים</dt><dd>בן ובת</dd></dl></div><div class="lb-card"><span class="lb-card-title">פעולות אחרונות</span><ul class="lb-list"><li><b>נשלחה פנייה ראשונה</b><span class="lb-meta">לפני 3 ימים</span></li><li><b>הספר נשלח</b><span class="lb-meta"><bdi class="lb-ltr">28 / 10 / 2026</bdi></span></li><li><b>ריל עלה לאוויר</b><span class="lb-meta"><bdi class="lb-ltr">01 / 11 / 2026</bdi></span></li></ul></div></div>'),
    "Progress": ("Data", 230, "`lb-bar` is a thin progress track filled in gold (`is-tint` for violet, `is-cat` for a category, `is-progress` for x of y where the rest is waiting: done in success on an amber track, with the waiting count as `lb-wait` text beside it). `svg.lb-spark` is a sparkline drawn with a `.grid` hairline, a soft gold `.area`, a gold `.line` and a `.dot` on the last point. `lb-stages` is one stacked bar of pipeline stages, each segment an `lb-swatch` with a category class or a `--seq-*` colour, explained by an `lb-legend`.",
                 '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-card lb-stat"><span class="lb-stat-label">משימות השבוע</span><span class="lb-stat-value">5<small>מתוך 8</small></span><div class="lb-bar"><i style="width:62%"></i></div><svg class="lb-spark" viewBox="0 0 100 30" preserveAspectRatio="none" aria-hidden="true"><line class="grid" x1="0" y1="29" x2="100" y2="29"/><path class="area" d="M0 24 L20 20 L40 22 L60 12 L80 14 L100 6 L100 30 L0 30Z"/><path class="line" d="M0 24 L20 20 L40 22 L60 12 L80 14 L100 6"/><circle class="dot" cx="100" cy="6" r="2.5"/></svg></div><div class="lb-card"><span class="lb-card-title">יוצרים לפי שלב</span><div class="lb-stages"><i style="flex:6;background:var(--seq-2)"></i><i style="flex:4;background:var(--seq-3)"></i><i style="flex:3;background:var(--seq-4)"></i><i style="flex:2;background:var(--seq-5)"></i></div><div class="lb-legend"><span><b style="background:var(--seq-2)"></b>חדש 6</span><span><b style="background:var(--seq-3)"></b>פנייה 4</span><span><b style="background:var(--seq-4)"></b>ספר 3</span><span><b style="background:var(--seq-5)"></b>תוכן 2</span></div></div></div>'),
    "Count": ("Status", 100, "`lb-count` is a small pill number beside a nav item or a heading (`is-alert` in danger, `is-tint` in violet). `lb-dot` is the status dot inside a chip (`live` pulses). `lb-delta` shows a change on a stat (`up` green, `down` red) and always carries its sign.",
              '<div dir="rtl" lang="he" class="lb-row" style="padding:16px;gap:16px"><span class="lb-row" style="gap:6px">תזכורות <span class="lb-count is-alert">3</span></span><span class="lb-row" style="gap:6px">להפקה <span class="lb-count is-tint">2</span></span><span class="lb-row" style="gap:6px">ארכיון <span class="lb-count">41</span></span><span class="lb-chip success"><span class="lb-dot live"></span>שרת פעיל</span><span class="lb-delta up"><bdi class="lb-ltr">+12</bdi></span><span class="lb-delta down"><bdi class="lb-ltr">-3</bdi></span></div>'),
    "Chart": ("Data", 235, "`lb-chart` is one daily series as a filled line chart: `lb-chart-head` (title and one summary figure), a y axis `lb-chart-y` (0, half, top), three hairlines, a gradient under the line in the category colour, the last point as `lb-chart-dot`, and `lb-chart-x` with the first, middle and last date. Time runs right to left on Hebrew pages. On hover a dot and a small ink label `lb-chart-tip` show the day. In a flex column the chart grows, so two cards side by side end level. Draw it with `areaChart()` in the HQ page script. `lb-metrics is-aligned` lines the tiles' labels, numbers, changes and feet up across a row.",
              '<div dir="rtl" lang="he" class="lb-cat-2" style="padding:16px"><figure class="lb-chart"><figcaption class="lb-chart-head"><span class="lb-chart-title">חשיפה יומית, 14 ימים</span><span class="lb-chart-sum">ממוצע יומי <b>2,530</b></span></figcaption><div class="lb-chart-body"><div class="lb-chart-y"><span>4K</span><span>2K</span><span>0</span></div><div class="lb-chart-plot" dir="ltr"><svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="dsg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--tc);stop-opacity:.28"/><stop offset="1" style="stop-color:var(--tc);stop-opacity:0"/></linearGradient></defs><line class="grid" x1="0" x2="100" y1="0" y2="0"/><line class="grid" x1="0" x2="100" y1="50" y2="50"/><line class="base" x1="0" x2="100" y1="100" y2="100"/><path class="area" fill="url(#dsg)" d="M98,40 L82,55 L66,35 L50,60 L34,30 L18,45 L2,25 L2,100 L98,100Z"/><path class="line" d="M98,40 L82,55 L66,35 L50,60 L34,30 L18,45 L2,25"/></svg><i class="lb-chart-dot" style="left:2%;top:25%"></i></div><div class="lb-chart-x"><span>01 / 11</span><span>07 / 11</span><span>14 / 11</span></div></div></figure></div>'),
    "Toast": ("Feedback", 120, "One short confirmation after an action (נשמר, הועתק, נשלח), bottom centre, ink on the page colour. No buttons; it leaves by itself after about 3 seconds. Errors that need an action belong in an `lb-alert`, not a toast.",
              '<div dir="rtl" lang="he" style="padding:16px"><p class="lb-muted lb-small">אחרי שמירה:</p><div class="lb-toast" role="status">הטיוטה נשמרה</div></div>'),
    "Drawer": ("Overlays", 320, "`lb-drawer` slides in from the end edge to show one item in detail without leaving the list: an `lb-drawer-head` (title and a close button) and a scrolling `lb-drawer-body`. Put an `lb-scrim` behind it; Escape and a tap on the scrim close it.",
               '<div dir="rtl" lang="he" style="padding:16px"><p class="lb-muted lb-small">הרשימה מאחור</p><div class="lb-scrim"></div><aside class="lb-drawer" style="width:min(100%,22rem)" aria-label="פרטי יוצר"><div class="lb-drawer-head"><b><bdi class="lb-ltr">@topaz_meir_slp</bdi></b><span class="lb-spacer"></span><button class="lb-btn ghost icon sm" type="button" aria-label="סגירה"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button></div><div class="lb-drawer-body"><dl class="lb-kv"><dt>עוקבים</dt><dd>18.4K</dd><dt>שלב</dt><dd><span class="lb-chip info">ספר נשלח</span></dd></dl><label class="lb-field">הערה<textarea class="lb-textarea">לבדוק את הריל בשבת</textarea></label></div></aside></div>'),
    "Modal": ("Overlays", 280, "`lb-modal` centres one `lb-card` for a short decision or form that must be answered before going on (a status change with a note, a confirm before sending). Keep it to one question and two buttons, the main one last.",
              '<div dir="rtl" lang="he" style="padding:16px"><div class="lb-scrim"></div><div class="lb-modal" role="dialog" aria-label="שינוי סטטוס"><div class="lb-card"><h3>להעביר ל״ספר נשלח״?</h3><label class="lb-field">הערה<input class="lb-input" value="נשלח בדואר שליחים"></label><label class="lb-field">תאריך<input class="lb-input" dir="ltr" value="05 / 11 / 2026"></label><div class="lb-row" style="justify-content:flex-end"><button class="lb-btn secondary sm" type="button">ביטול</button><button class="lb-btn sm" type="button">שמירה</button></div></div></div></div>'),
    "Metric": ("Data", 470, "Metric tiles, the \"number cubes\" (5 Nov 2026, from the creator map's books tab): a row of counts a reader scans first, instead of a sentence of figures. `lb-metrics` holds them (3 across; `cols-6` puts six in one row from 1200px; two on phones). Each `lb-metric` has an `lb-metric-label` (an `lb-tile is-soft` icon and a short name), an `lb-metric-value` (a big tabular number, with an optional `lb-delta up` or `down` for the change), an optional `lb-metric-foot` and an optional `lb-bar is-progress`. Colour: one hue per metric from categories.json (`lb-cat-N`), the same wherever that metric appears, or `is-ok` for a status count (done in success, what waits as `lb-wait`). `is-empty` with an `lb-none` word when there is no number yet. `sm` is the compact size for a table row or a card: the icon without a tile, three across, numbers on one line even when a label takes two. A number rated against the rest (the creator map's card) is `is-ok` (good, green) or `is-bad` (weak, red), neither in the middle, with an `lb-metric-mark` arrow at the top end (`up`, `down`, `mid`) whose `aria-label` says the rating in words. A rating is status, never a category hue. Not the same thing as the clickable `lb-cube` launcher tile.",
               '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px">'
               '<dl class="lb-metrics">'
               f'<div class="lb-metric lb-cat-{BK["books"]}"><dt class="lb-metric-label"><span class="lb-tile is-soft">{_I["gift"]}</span>ספרים שנוצרו</dt><dd class="lb-metric-value">12</dd><dd class="lb-metric-foot">ל-9 יוצרים</dd></div>'
               f'<div class="lb-metric is-ok"><dt class="lb-metric-label"><span class="lb-tile is-soft">{_I["check"]}</span>הגיעו ליוצרים</dt><dd class="lb-metric-value">8</dd><dd class="lb-metric-foot">מתוך 12 · <b class="lb-wait">4 בדרך</b></dd><dd class="lb-bar is-progress"><i style="width:67%"></i></dd></div>'
               f'<div class="lb-metric lb-cat-{BK["views"]}"><dt class="lb-metric-label"><span class="lb-tile is-soft">{_I["eye"]}</span>צפיות בפוסטים</dt><dd class="lb-metric-value">7,169<i class="lb-delta up">+164</i></dd><dd class="lb-metric-foot">ב-3 פוסטים · נבדק היום</dd></div>'
               '</dl>'
               '<dl class="lb-metrics sm" style="max-width:340px">'
               f'<div class="lb-metric lb-cat-{BK["views"]}"><dt class="lb-metric-label">{_I["eye"]}צפיות</dt><dd class="lb-metric-value">1,566<i class="lb-delta up">+2</i></dd></div>'
               f'<div class="lb-metric lb-cat-{BK["likes"]}"><dt class="lb-metric-label">{_I["heart"]}לייקים</dt><dd class="lb-metric-value">44</dd></div>'
               f'<div class="lb-metric lb-cat-{BK["comments"]}"><dt class="lb-metric-label">{_I["comment"]}תגובות</dt><dd class="lb-metric-value">46</dd></div>'
               '</dl>'
               '<dl class="lb-metrics sm" style="max-width:340px">'
               f'<div class="lb-metric lb-cat-{BK["views"]} is-empty"><dt class="lb-metric-label">{_I["eye"]}צפיות</dt><dd class="lb-metric-value"><span class="lb-none">לא מוצג</span></dd></div>'
               f'<div class="lb-metric lb-cat-{BK["likes"]}"><dt class="lb-metric-label">{_I["heart"]}לייקים</dt><dd class="lb-metric-value">74</dd></div>'
               f'<div class="lb-metric lb-cat-{BK["comments"]}"><dt class="lb-metric-label">{_I["comment"]}תגובות</dt><dd class="lb-metric-value">32<i class="lb-delta down">-1</i></dd></div>'
               '</dl>'
               '<dl class="lb-metrics sm" style="max-width:340px">'
               f'<div class="lb-metric is-ok" title="טוב: גבוה מ-82% מהיוצרים במפה"><dt class="lb-metric-label">{_I["eye"]}צפיות חציון</dt><dd class="lb-metric-value">16.6K<i class="lb-delta up">+18%</i></dd><svg class="lb-metric-mark up" viewBox="0 0 20 20" role="img" aria-label="טוב"><path d="M10 15.5v-11M5.5 9L10 4.5 14.5 9"/></svg></div>'
               f'<div class="lb-metric" title="בינוני: גבוה מ-51% מה-134 שנמדדו"><dt class="lb-metric-label">{_I["comment"]}תגובות ל-1K צפיות</dt><dd class="lb-metric-value">2.3</dd><svg class="lb-metric-mark mid" viewBox="0 0 20 20" role="img" aria-label="בינוני"><path d="M5 10h10"/></svg></div>'
               f'<div class="lb-metric is-bad" title="חלש: גבוה מ-20% מה-134 שנמדדו"><dt class="lb-metric-label">{_I["heart"]}לייקים ל-1K צפיות</dt><dd class="lb-metric-value">8.4</dd><svg class="lb-metric-mark down" viewBox="0 0 20 20" role="img" aria-label="חלש"><path d="M10 4.5v11M5.5 11l4.5 4.5 4.5-4.5"/></svg></div>'
               '</dl></div>'),
    "Toggle": ("Forms", 90, "`lb-toggle`: a switch with its state in words, for a done or waiting step in a table row (a book that arrived, content that is up). The chip says the state: `success` when on, `warning` when the step is now waiting, neutral when it is not due yet. Rows that can be removed end with `lb-btn quiet icon`.",
               '<div dir="rtl" lang="he" class="lb-row" style="padding:16px;gap:16px"><label class="lb-toggle"><input class="lb-switch" type="checkbox" checked aria-label="הספרים הגיעו"><span class="lb-chip success">הגיע</span></label><label class="lb-toggle"><input class="lb-switch" type="checkbox" aria-label="הספרים הגיעו"><span class="lb-chip warning">בדרך</span></label><label class="lb-toggle"><input class="lb-switch" type="checkbox" aria-label="התוכן עלה"><span class="lb-chip warning">מחכה לתוכן</span></label><label class="lb-toggle"><input class="lb-switch" type="checkbox" aria-label="התוכן עלה"><span class="lb-chip">עוד לא</span></label><button class="lb-btn quiet icon" type="button" aria-label="הסרת השורה">×</button></div>'),
    "LinkField": ("Forms", 130, "`lb-linkfield`: a short label, the URL (left to right) and an `lb-btn secondary sm icon` that opens it, for links typed into a row (a post, a Drive folder). Stack them in `lb-linkfields`. The button shows only when the field holds a link; an empty `span` keeps its slot so the inputs line up.",
                  '<div dir="rtl" lang="he" style="padding:16px;max-width:360px"><div class="lb-linkfields"><div class="lb-linkfield"><span>פוסט</span><input class="lb-input" value="https://www.instagram.com/reel/Detno1aN7dQ/" aria-label="קישור לפוסט"><a class="lb-btn secondary sm icon" href="#" aria-label="פתיחת הפוסט">↗</a></div><div class="lb-linkfield"><span>דרייב</span><input class="lb-input" placeholder="https://drive.google.com/…" aria-label="תיקיית דרייב"><span></span></div></div></div>'),
    "Launcher": ("Layout", 600, "A home page of tools (HQ since 5 Nov 2026): `lb-topics` holds one `lb-topic` per topic, one under the other. A topic is an `lb-topic-head` (an `lb-tile lg` icon, an `lb-topic-title` with its `lb-topic-n` count, one `lb-topic-desc` line) over an `lb-topic-grid` of `lb-cube` tiles. A cube is one tool: an `lb-tile xl` icon (with an optional `lb-count`), the `lb-cube-title` link, which covers the whole cube, one `lb-cube-desc` line, and an `lb-cube-foot` with where it opens (`lb-cube-where`) and, when there is one, a button for the other version (`lb-cube-alt`). Put the topic's `lb-cat-N` on the topic and on each cube. `lb-filters` above it: pill filters, each with an `lb-swatch` and `aria-pressed`. On phones two cubes a row. Use it for a page whose job is to open other pages; a page of numbers uses Stat or Metrics instead.",
                 '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px">'
                 '<div class="lb-filters" role="group" aria-label="סינון לפי תחום"><button type="button" aria-pressed="true">הכול · 5</button><button type="button" class="lb-cat-2" aria-pressed="false"><b class="lb-swatch" aria-hidden="true"></b>יוצרים</button><button type="button" class="lb-cat-1" aria-pressed="false"><b class="lb-swatch" aria-hidden="true"></b>רילס ווידאו</button></div>'
                 '<div class="lb-topics">'
                 + _hq_topic(2, "people", "יוצרים", 3, "מציאת יוצרים, פניות והרשמות", [
                     _hq_cube(2, "people", "מפת יוצרים", "פניות, תזכורות ומעקב אחרי כל יוצר", "מקומי", count="4"),
                     _hq_cube(2, "signup", "הרשמות", "מי נרשם בטופס היוצרים", "ב-HQ"),
                     _hq_cube(2, "brief", "בריף ליוצרים", "שלד הצילום לרילס שיוצרים מקבלים", "מקומי", alt="גרסת ארטיפקט")])
                 + _hq_topic(1, "clapper", "רילס ווידאו", 2, "תכנון, צילום ומחקר של רילס", [
                     _hq_cube(1, "clapper", "פלייבוק רילס", "מה עובד ברילס מוצר ואיך מצלמים", "מקומי", alt="גרסת ארטיפקט"),
                     _hq_cube(1, "flask", "מעבדת תוכן ילדים", "64 סרטונים קצרים מפורקים לפורמטים", "מקומי", alt="גרסת ארטיפקט")])
                 + '</div></div>'),
    "LauncherEdit": ("Layout", 360, "Edit mode of a Launcher: `is-editing` on `lb-topics`. Each topic sits on a surface with an `lb-drag` handle (a button with an `aria-label`) and an edit button; cubes get a dashed category edge and a grab cursor, the title becomes a button that opens the editor, and `lb-cube-add` ends each grid. `lb-sort-ghost` and `lb-sort-drag` are the drag states (SortableJS `ghostClass` and `dragClass`). Save after every change and say so (a `success` chip, נשמר); reset asks once more in place.",
                     '<div dir="rtl" lang="he" style="padding:16px"><div class="lb-topics is-editing">'
                     + _hq_topic(5, "slides", "קרוסלות", 2, "הפקת קרוסלות והמחקר שמאחוריהן", [
                         _hq_cube(5, "slides", "מכונת הקרוסלות", "חבילות, ציונים והפקה של קרוסלות", "מקומי", edit=True),
                         _hq_cube(5, "book", "פלייבוק קרוסלות", "מה גורם לקרוסלה להמיר, ולוח בדיקות", "מקומי", edit=True).replace('class="lb-cube lb-cat-5"', 'class="lb-cube lb-cat-5 lb-sort-ghost"', 1)], edit=True)
                     + '</div></div>'),
    "Form": ("Forms", 600, "`lb-form`: a form in an `lb-card`, usually in an `lb-modal` over an `lb-scrim`. `lb-field` rows, fieldsets with a plain legend, one `lb-form-error` line (`role=\"alert\"`, hidden until there is something to say), and `lb-form-actions`: the main action first, cancel next, a destructive one at the far end behind an `lb-spacer` that turns into a `danger` button saying what it will do and acts on the second click. `lb-icon-picker`: a grid of icon buttons from the icon set, each with `aria-pressed` and an `aria-label`. `lb-color-picker`: round swatches, one per `lb-cat-N` (`lb-cat-0` is neutral ink), each with `aria-pressed` and the colour's name. Escape and a click outside close the modal.",
             '<div dir="rtl" lang="he" style="padding:16px;max-width:480px"><form class="lb-card lb-form" onsubmit="return false"><h2>עריכת כלי</h2>'
             '<label class="lb-field">שם הכלי<input class="lb-input" value="מפת יוצרים"></label><label class="lb-field">שורת תיאור<input class="lb-input" value="פניות, תזכורות ומעקב אחרי כל יוצר"></label>'
             '<fieldset><legend>אייקון</legend><div class="lb-icon-picker" role="group" aria-label="אייקון">'
             + "".join(f'<button type="button" aria-pressed="{str(k == "people").lower()}" aria-label="{k}">{ico(k)}</button>' for k in ("people", "signup", "brief", "chat", "sheet", "slides", "book", "clapper", "flask", "pin"))
             + '</div></fieldset><fieldset><legend>צבע</legend><div class="lb-color-picker" role="group" aria-label="צבע">'
             + "".join(f'<button type="button" class="lb-cat-{c}" aria-pressed="{str(c == 2).lower()}" aria-label="{n}"></button>' for c, n in ((0, "שחור"), (1, "כתום"), (2, "ורוד"), (3, "ירוק"), (4, "כחול"), (5, "סגול"), (6, "טורקיז"), (7, "אפור"), (8, "חרדל")))
             + '</div></fieldset><p class="lb-form-error" role="alert">צריך לפחות מקום אחד שהכלי נפתח בו.</p>'
             '<div class="lb-form-actions"><button type="submit" class="lb-btn">שמירה</button><button type="button" class="lb-btn ghost">ביטול</button><span class="lb-spacer"></span><button type="button" class="lb-btn danger">בטוח? למחוק את הכלי</button></div></form></div>'),
    "Icons": ("Iconography", 700, "The icon set: `shared/design/icons.json`. Line icons on a 24 grid (fill none, stroke `currentColor`, stroke width 2, round caps and joins). `icons` are pictures for tools and topics; `ui` are interface glyphs (drag grip, plus, pencil, open elsewhere, back). Names are stable ids, since saved layouts store them: add icons, never rename or remove one. Builds call `design.icon(name)`; pages without a build link `design/icons.js` (`window.LB_ICONS`, `window.LB_UI_ICONS`), which `tools/lumebook.py sync` writes and copies.",
              '<div dir="rtl" lang="he" style="padding:16px"><div class="lb-grid" style="--min:8rem;gap:8px">'
              + "".join(f'<div class="lb-card is-quiet" style="justify-items:center;text-align:center;gap:6px;padding:12px"><span class="lb-tile {"lb-cat-0" if g == "ui" else "lb-cat-4"}">{ico(k)}</span><code class="lb-ltr lb-xs">{k}</code><span class="lb-xs lb-muted">{v["use"]}</span></div>'
                        for g in ("icons", "ui") for k, v in ICON_SET[g].items())
              + '</div></div>'),
    "Dialog": ("Overlays", 560, "`lb-dialog`: a `dialog` element that opens one record from a list or a calendar (the reel calendar, 5 Nov 2026). It holds two separate cards 16px apart on the `overlay-2` backdrop: the `lb-dialog-card` (a sticky translucent `lb-dialog-head` with an `lb-editbar` or a title and the round `lb-dialog-x` close button with an `aria-label`, then `lb-dialog-body` with the record, usually an `lb-card lb-tinted`, which drops its edge there) and an optional `lb-ask` comment card under it. The dialog scrolls as one. Open it with `showModal()`; Escape, the close button and a click on the backdrop close it, and focus goes back to the item that opened it. Both cards float on the backdrop with no drop shadow: the scrolling dialog would clip a shadow at its own edge into a hard dark box.",
               '<div dir="rtl" lang="he" style="padding:16px;background:var(--overlay-2)"><dialog open class="lb-dialog" style="position:static;margin:0 auto;max-height:none" aria-label="ריל"><div class="lb-dialog-card"><div class="lb-dialog-head"><div class="lb-editbar" role="toolbar" aria-label="עיצוב טקסט"><div class="lb-editbar-in"><button type="button"><b>B</b></button><button type="button"><i>I</i></button><button type="button"><u>U</u></button><span class="sep"></span><button type="button">•</button><button type="button">1.</button><span class="hint">לוחצים על טקסט כדי לערוך</span></div></div><button type="button" class="lb-dialog-x" aria-label="סגירה">✕</button></div>'
               '<div class="lb-dialog-body"><article class="lb-card lb-tinted lb-cat-4"><div class="lb-row"><b>ראשון</b><span class="lb-muted lb-num">08 / 11</span><button type="button" class="lb-chip check" aria-pressed="false">עשיתי</button><span class="lb-pid">1.2</span><span class="lb-chip cat">לפני שמזמינים</span></div><h3 class="lb-editable" contenteditable="true">כמה זמן לוקח להזמין? בואו נמדוד</h3><p class="lb-small lb-editable is-edited">מודדים כמה זמן לוקח להזמין ספר.</p></article></div></div>'
               '<form class="lb-ask" onsubmit="return false"><div class="lb-composer"><label class="lb-composer-label lb-ask-label" for="ds-ask">הערה לשינוי הריל</label><textarea id="ds-ask" rows="2" dir="rtl" placeholder="מה לשנות?"></textarea><div class="lb-composer-bar"><button type="button" class="lb-btn secondary sm">' + _ui("sparkle") + '<span>רעיון חדש</span></button><span class="lb-composer-note">⌘ Enter לשליחה</span><button type="submit" class="lb-btn sm">' + _ui("arrow-up") + '<span>שליחה</span></button></div></div><p class="lb-ask-msg" role="status">קיצרתי את הכותרת.<button type="button">ביטול</button></p></form></dialog></div>'),
    "Docked dialog": ("Overlays", 330, "`lb-dialog is-docked` (7 Nov 2026, Yarin: the reel card opens \"from the calendar like a drawer (from right to left)\" and the calendar narrows to the right): on a wide screen the same `lb-dialog` opens as a drawer on the left edge instead of a popup. Open it with `show()`, add `is-docked`, and put `lb-docked` on the `html` element with the drawer width in `--lb-dock-w` (the reel calendar: half the room left of the project nav, up to 860px, from 1100px of room). The page, top bar included, narrows to the right and stays in use: another day opens in the same drawer, and the open day gets `aria-current=\"true\"`, a violet ring. A page's own `lb-sidebar` steps aside while it is open. It slides in from the right, its cards float .625rem from the window edges, it scrolls on its own and has no backdrop: the close button and Escape close it. A month it narrows under 46rem gives its days smaller text and four lines. Below the room, it is the popup.",
               '<div dir="rtl" lang="he" style="padding:16px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;align-items:start"><div class="lb-month" style="grid-template-columns:repeat(3,minmax(0,1fr))">'
               '<a class="lb-day lb-tinted lb-cat-4" href="#" onclick="return false"><span class="lb-day-top"><span class="lb-day-num">8</span><span class="lb-pid">1.2</span></span><span class="lb-day-text">כמה זמן לוקח להכין ספר ליום הולדת?</span><span class="lb-day-foot"></span></a>'
               '<a class="lb-day lb-tinted lb-cat-6" href="#" onclick="return false" aria-current="true"><span class="lb-day-top"><span class="lb-day-num">9</span><span class="lb-pid">5.5</span></span><span class="lb-day-text">גיבור על בלי גלימה גר אצלכם בבית?</span><span class="lb-day-foot"></span></a>'
               '<a class="lb-day lb-tinted lb-cat-2" href="#" onclick="return false"><span class="lb-day-top"><span class="lb-day-num">10</span><span class="lb-pid">1.4</span></span><span class="lb-day-text">סבתא, זה מה שהנכד יפתח בקופסה</span><span class="lb-day-foot"></span></a></div>'
               '<div class="lb-dialog-card"><div class="lb-dialog-head"><b style="flex:1;padding-inline-start:16px">ריל 5.5</b><button type="button" class="lb-dialog-x" aria-label="סגירה">✕</button></div><div class="lb-dialog-body"><article class="lb-card lb-tinted lb-cat-6"><h3 class="lb-card-title">גיבור על בלי גלימה גר אצלכם בבית?</h3><p class="lb-small lb-muted">נפתח ליד הלוח, והלוח ממשיך לעבוד</p></article></div></div></div>'),
    "Month": ("Data", 380, "`lb-month`: a month as a 7-day grid, Sunday first (`lb-month-dow` day names). Each `lb-day` is a day: `is-out` outside the month, `is-empty` with nothing on it, or a link to its record, tinted in its category (`a.lb-day lb-tinted lb-cat-N`). Inside: `lb-day-top` (the `lb-day-num` and an `lb-pid`), `lb-day-text` (three lines at most, hidden on phones), and `lb-day-foot` for small marks, ending with `lb-day-tick`, the green tick shown when the day `is-done`. `is-dim` fades a day a filter leaves out. `lb-tinted` is the category's soft ground with a light 28% edge, lighter than `lb-card is-cat`, for pages that show many records; never a side stripe. `lb-chip check` is the chip button that marks a record done (`aria-pressed`): off on the surface, on in success with a tick.",
              '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px;max-width:620px"><div class="lb-month">'
              + "".join(f'<div class="lb-month-dow">{d}</div>' for d in ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"])
              + '<div class="lb-day is-out"></div><div class="lb-day is-out"></div><div class="lb-day is-empty"><span class="lb-day-num">3</span></div>'
              '<a class="lb-day lb-tinted lb-cat-4 is-done" href="#"><span class="lb-day-top"><span class="lb-day-num">4</span><span class="lb-pid">1.1</span></span><span class="lb-day-text">כמה זמן לוקח להזמין ספר</span><span class="lb-day-foot"><span class="lb-day-tick" title="עשית">✓</span></span></a>'
              '<a class="lb-day lb-tinted lb-cat-2" href="#"><span class="lb-day-top"><span class="lb-day-num">5</span><span class="lb-pid">2.1</span></span><span class="lb-day-text">סבתא, מה תביאי לו ליום הולדת?</span><span class="lb-day-foot"><span class="lb-day-tick">✓</span></span></a>'
              '<a class="lb-day lb-tinted lb-cat-6 is-dim" href="#"><span class="lb-day-top"><span class="lb-day-num">6</span><span class="lb-pid">3.1</span></span><span class="lb-day-text">הספר שהוא מבקש כל ערב</span><span class="lb-day-foot"><span class="lb-day-tick">✓</span></span></a>'
              '<div class="lb-day is-empty"><span class="lb-day-num">7</span></div></div>'
              '<div class="lb-row"><button type="button" class="lb-chip check" aria-pressed="false">עשיתי</button><button type="button" class="lb-chip check" aria-pressed="true">עשיתי</button></div></div>'),
    "Editable": ("Forms", 300, "Text someone edits in the page. `lb-editable` on the element (the script sets `contenteditable` and saves by itself): a dashed hairline on hover, the focus ring and a tint ground while typing. States the script sets: `is-edited` (a saved edit is shown, tint ground), `is-stale` (an edit is hidden because the source text changed, warning ground) and `is-changed` (just rewritten from a comment, a green ground that fades). `lb-editbar` (`role=\"toolbar\"`) is its formatting bar: icon buttons, selects, `.sep` dividers, `.clr` colour pickers (`.hl` for the highlight), a link input and a `.hint`; it is faded until a field has the selection, then `is-on`. Sticky under the top bar, or inside an `lb-dialog-head`.",
                 '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px;max-width:520px"><div class="lb-editbar is-on" role="toolbar" aria-label="עיצוב טקסט" style="position:static"><div class="lb-editbar-in"><button type="button">↶</button><button type="button">↷</button><span class="sep"></span><select aria-label="סגנון"><option>סגנון</option></select><span class="sep"></span><button type="button"><b>B</b></button><button type="button"><i>I</i></button><button type="button"><u>U</u></button><label class="clr" title="צבע טקסט"><span class="a">A</span><input type="color" value="#5b2bd6"></label><label class="clr hl" title="הדגשת רקע"><span class="a">▇</span><input type="color" value="#fbebc9"></label><span class="sep"></span><button type="button">•</button><button type="button">1.</button><span class="hint">לוחצים על טקסט כדי לערוך</span></div></div>'
                 '<p class="lb-editable" contenteditable="true">טקסט שאפשר לערוך: לוחצים וכותבים</p><p class="lb-editable is-edited">עריכה שנשמרה</p><p class="lb-editable is-stale">עריכה שהוסתרה כי המקור השתנה</p><p class="lb-editable is-changed">שונה עכשיו לפי ההערה</p></div>'),
    "Comment": ("Forms", 230, "`lb-ask`: a comment box under a record that asks for a change (in an `lb-dialog` it is the second card). Since 7 Nov 2026 it holds one `lb-composer` with an even 8px of the card around it, so the composer's 20px corners nest in the card's 28px: the `lb-composer-label` (also `lb-ask-label`) inside on top, the textarea, and the bar with the secondary action at the start (`lb-btn secondary sm`, like רעיון חדש) and the send button at the end (`lb-btn sm`), the same height, a quiet hint between them. ⌘ Enter sends; a running button turns into עצירה (its icon hides). `lb-ask-msg` is the status line under the composer (`role=\"status\"`), hidden while empty, `is-error` in danger, and may end with an undo link (a `button` inside it). The older `lb-ask-top` and `lb-ask-row` markup still lays out.",
                '<div dir="rtl" lang="he" style="padding:16px;max-width:520px"><form class="lb-ask" onsubmit="return false"><div class="lb-composer"><label class="lb-composer-label lb-ask-label" for="ds-ask2">הערה לשינוי הריל</label><textarea id="ds-ask2" rows="2" dir="rtl" placeholder="מה לשנות? למשל: כותרת יותר קצרה"></textarea><div class="lb-composer-bar"><button type="button" class="lb-btn secondary sm">' + _ui("sparkle") + '<span>רעיון חדש</span></button><span class="lb-composer-note">⌘ Enter לשליחה</span><button type="submit" class="lb-btn sm">' + _ui("arrow-up") + '<span>שליחה</span></button></div></div><p class="lb-ask-msg is-error" role="status">יותר מדי בקשות כרגע. נסה שוב עוד קצת.</p></form></div>'),
    "Composer": ("Forms", 250, "`lb-composer`: a text box with its actions inside it, like a message field (7 Nov 2026, the reels hub's comment box and make sheet). An optional `lb-composer-label` on top, the textarea (no frame of its own, it grows with the text up to 12rem), then `lb-composer-bar`: one action at each end, the start secondary and the end the main one (both `lb-btn sm`), and an optional `lb-composer-note` between them (centred, quiet, hidden while empty). A pressed-in well with 20px corners and a 6px rim, so the 30px capsules nest in its corners; the focus ring is on the whole box. On a sheet set `--lb-composer-r` to the sheet's radius minus the gap (the make sheet: 20px minus 6px).",
                 '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px;max-width:520px"><div class="lb-composer"><textarea rows="2" dir="rtl" aria-label="הוראות" placeholder="מה לעשות עם החומרים? למשל: הטייק השני לפתיחה, לחתוך את השתיקות"></textarea><div class="lb-composer-bar"><span class="lb-composer-note" style="text-align:start;padding-inline:8px"><bdi>2026-11-07-reel-5-5</bdi></span><button type="button" class="lb-btn sm">' + _ui("play") + '<span>ליצור את הריל</span></button></div></div></div>'),
    "Drop": ("Forms", 420, "`lb-drop` is where files are dropped or picked: a dashed well with an icon, an `lb-drop-t` line and a smaller `lb-drop-s` line, as a `label` around a hidden `input type=file multiple`; `is-over` while files are dragged over it (or over the card it serves). `lb-drop-veil` says the same over a whole card while files are dragged anywhere on it (the script places it over the visible part and adds `is-on`). `lb-files` is a grid of `lb-file` tiles, one per file: `lb-file-th` (a video's frame with an `lb-file-dur` badge, the picture, or a type icon), `lb-file-meta` (`lb-file-n` the name, `lb-file-s` kind and size), a round `lb-file-x` remove button in the top end corner (on hover, always on touch screens) and `lb-file-bar` while it uploads (`is-up`, `--p` from 0 to 1); `is-bad` when it failed. Tiles are 14px glass cards without blur, since they repeat.",
             '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px;max-width:560px"><label class="lb-drop">' + _ui("upload") + '<span class="lb-drop-t">גוררים לכאן סרטונים, הקלטות ותמונות</span><span class="lb-drop-s">או לוחצים לבחירה. הכול נשמר בתיקיית הריל</span><input type="file" multiple aria-label="בחירת קבצים"></label>'
             '<ul class="lb-files"><li class="lb-file"><span class="lb-file-th" style="background:linear-gradient(160deg,#F6B26B,#E06666)"><span class="lb-file-dur">0:23</span></span><button type="button" class="lb-file-x" aria-label="הסרה">' + _ui("close") + '</button><span class="lb-file-meta"><span class="lb-file-n">IMG_0042.mov</span><span class="lb-file-s">סרטון, 84 MB</span></span><span class="lb-file-bar"><i></i></span></li>'
             '<li class="lb-file"><span class="lb-file-th">' + _ui("audio") + '</span><button type="button" class="lb-file-x" aria-label="הסרה">' + _ui("close") + '</button><span class="lb-file-meta"><span class="lb-file-n">voice.m4a</span><span class="lb-file-s">הקלטה, 2 MB</span></span><span class="lb-file-bar"><i></i></span></li>'
             '<li class="lb-file is-up" style="--p:.62"><span class="lb-file-th">' + _ui("film") + '</span><button type="button" class="lb-file-x" aria-label="ביטול">' + _ui("close") + '</button><span class="lb-file-meta"><span class="lb-file-n">screen.mp4</span><span class="lb-file-s">מעלה, 31 MB</span></span><span class="lb-file-bar"><i></i></span></li>'
             '<li class="lb-file is-bad"><span class="lb-file-th">' + _ui("file") + '</span><button type="button" class="lb-file-x" aria-label="הסרה">' + _ui("close") + '</button><span class="lb-file-meta"><span class="lb-file-n">notes.pages</span><span class="lb-file-s">סוג קובץ שלא נתמך</span></span><span class="lb-file-bar"><i></i></span></li></ul></div>'),
    "TopBar": ("Layout", 190, "The top bar of a reading page or report. `lb-brand` inside an `lb-topbar` takes the bar size (a 28px logo, the name on one line with an ellipsis); `is-stacked` puts a small gold line above the name. `lb-topbar has-toc` holds the `lb-toc` section pills, which move to their own full-width row under 980px. The link back to the dashboard and any actions sit at the end.",
               '<div dir="rtl" lang="he" style="padding:16px 0"><header class="lb-topbar has-toc" style="position:static"><div class="lb-topbar-in"><a class="lb-brand is-stacked" href="#"><img src="/_blob/fced3317e50c510f4abe26ccb21e46f5" alt=""><span><small>לומבוק</small><b>פלייבוק הקרוסלות</b></span></a><nav class="lb-toc"><a href="#" aria-current="true">סיכום</a><a href="#">מבנים</a><a href="#">פתיחים</a><a href="#">מדדים</a><a href="#">מקורות</a></nav><span class="lb-spacer"></span><a class="lb-btn ghost sm" href="#">ללוח</a></div></header></div>'),
    "Hero": ("Layout", 240, "The opening block of a page: an `lb-eyebrow`, the h1, one `lb-lede`, then an `lb-hero-meta` row (dates, counts, chips). A view inside an app page may use an h2 as its title; it gets the smaller hero size. `has-media` adds a picture or demo column beside `lb-hero-text`; it drops under the text on a phone.",
             '<div dir="rtl" lang="he" style="padding:16px"><header class="lb-hero"><span class="lb-eyebrow">מחקר · נובמבר</span><h1>מה גורם להורים לשמור קרוסלה</h1><p class="lb-lede">752 חשבונות מישראל ומהעולם, ומה משותף לפוסטים שקיבלו הכי הרבה שמירות.</p><div class="lb-hero-meta"><span>עודכן <bdi class="lb-ltr">05 / 11 / 2026</bdi></span><span class="lb-chip">פנימי</span><span class="lb-chip accent">12 מסקנות</span></div></header></div>'),
    "Disc": ("Data", 300, "`lb-disc` is a round number for a step, a rank or a point: gold soft by default, `tint`, `solid` (brand gold with ink), `quiet`, `warning`, `cat` (with an `lb-cat-N` class); `sm` and `lg` sizes. `ol.lb-steps` numbers its items with the same disc. `lb-timeline` hangs items on a rail, each starting with a disc and an optional `lb-timeline-time`.",
             '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-stack"><div class="lb-row"><span class="lb-disc">1</span><span class="lb-disc tint">2</span><span class="lb-disc solid">3</span><span class="lb-disc quiet">4</span><span class="lb-disc cat lb-cat-6">5</span><span class="lb-disc sm">6</span><span class="lb-disc lg">7</span></div><ol class="lb-steps"><li><b>בוחרים ספר מהשבעה הנמכרים</b></li><li><b>כותבים את הפתיח מהצד של הילד</b></li><li><b>מוסיפים קריאה לפעולה עם מילת קוד</b></li></ol></div><ol class="lb-timeline"><li><span class="lb-disc sm solid">1</span><div><span class="lb-timeline-time"><bdi class="lb-ltr">0:00</bdi></span><p>הפנים של הילד, לפני שמשהו קורה</p></div></li><li><span class="lb-disc sm solid">2</span><div><span class="lb-timeline-time"><bdi class="lb-ltr">0:03</bdi></span><p>הספר נפתח והוא רואה את עצמו</p></div></li><li><span class="lb-disc sm solid">3</span><div><span class="lb-timeline-time"><bdi class="lb-ltr">0:08</bdi></span><p>התגובה, ואז הכריכה</p></div></li></ol></div>'),
    "TextBlock": ("Type", 230, "`lb-textblock` holds text someone will paste somewhere else (a caption, a DM, a script, a command) exactly as written, line breaks kept. `is-code` is a left-to-right monospace command; `is-boxed` adds the hairline. `lb-copy` puts the block beside its copy button (`is-below`: the button under it).",
                  '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px"><div class="lb-copy"><p class="lb-textblock">היי, אני ירין מ-LumeBook.\nראיתי את הריל על יום ההולדת וממש התחברתי.\nנשמח לשלוח ספר במתנה, בלי התחייבות.</p><button class="lb-btn secondary sm" type="button">העתקה</button></div><div class="lb-copy"><pre class="lb-textblock is-code">python3 tools/lumebook.py ripple</pre><button class="lb-btn secondary sm" type="button">העתקה</button></div></div>'),
    "Scroller": ("Layout", 400, "`lb-scroller` is a sideways swipe row of items (reels, slides, examples): set `--item` for the item width, `snap` to snap each item to the start (`snap center`: to the middle), `bleed` to run edge to edge on a phone. `lb-dots` under it shows the position. The items here are `lb-media` cards: a poster in `lb-media-frame` (9:16 by default; `is-4x5`, `is-1x1`, `is-16x9`) with an optional `lb-media-play` mark, then `lb-media-title` and `lb-media-meta`; `is-side` puts the poster beside the text.",
                 '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px"><div class="lb-scroller snap" style="--item:9rem">' + "".join(f'<a class="lb-media" href="#"><span class="lb-media-frame"><span class="lb-media-play"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></span></span><span class="lb-media-body"><span class="lb-media-title">{t}</span><span class="lb-media-meta">{m}</span></span></a>' for t, m in [("סבתא אופה עם הנכד", "3.2K צפיות"), ("הספר נפתח", "1.8K צפיות"), ("ריל של יוצרת", "6.4K צפיות"), ("לפני השינה", "940 צפיות"), ("יום הולדת 4", "2.1K צפיות")]) + '</div><div class="lb-dots"><i class="is-on"></i><i></i><i></i></div></div>'),
    "Post": ("Data", 440, "`lb-post` shows how a caption or an ad will read in the feed: `lb-post-head` (an `lb-post-avatar` and `lb-post-name` with a small line), `lb-post-text` with the line breaks kept, then an `lb-media-frame`. A mock for review, never a real post.",
             '<div dir="rtl" lang="he" style="padding:16px;max-width:340px"><article class="lb-post"><div class="lb-post-head"><span class="lb-post-avatar"></span><span class="lb-post-name">lumebook.il<small>ממומן</small></span></div><p class="lb-post-text">הוא עוד לא יודע שהוא הגיבור של הספר הזה\nתצוגה מקדימה בחינם, קישור בביו</p><span class="lb-media-frame is-4x5"></span></article></div>'),
    "Pair": ("Layout", 250, "`lb-pair` sets two boxes side by side to compare: mark each `yes` and `no` (do and don\'t) or `was` and `now` (before and after); its `lb-pair-label` takes the colour and `was` sits on the quiet ground. One column on a phone.",
             '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px"><div class="lb-pair"><div class="yes"><span class="lb-pair-label">כן</span><span>ספר שעוזר לדבר על האח החדש</span></div><div class="no"><span class="lb-pair-label">לא</span><span>ספר שפותר קנאת אחים</span></div></div><div class="lb-pair"><div class="was"><span class="lb-pair-label">היה</span><span>טיפ להורים בלי קשר לספר</span></div><div class="now"><span class="lb-pair-label">עכשיו</span><span>רגע של הילד, ואז הספר ככלי לרגע הזה</span></div></div></div>'),
    "ProjectNav": ("Layout", 400, "The project nav (5 Nov 2026) on every internal page, drawn by `nav.js` (source `shared/design/nav.src.js`, data `shared/design/hq-tools.json`; `design.head()` inlines it, HQ and the SMM plan link a synced copy, `design.head(nav=False)` only for the public creator brief). Since 6 Nov 2026 it is one `lb-gside` side bar on the right that runs the full height of the window, with no top bar and no location path. Its head (`lb-gside-head`) holds the logo home to HQ (`lb-gside-brand`) and the menu button (`lb-gside-toggle`), which on touch screens opens the rail over the page and closes it (`html[data-gside]`); under it every HQ tool by topic (`lb-gside-topic` with its `lb-cat-N`, `lb-gside-item` with an `lb-tile`, the current page tinted). Since 15 Nov 2026 (Yarin: \"main topics ... to expand when clicking\") a topic is a row, `lb-gside-h` holding the button `lb-gside-tbtn` (the topic's solid tile, its name, `lb-gside-chev`), that folds its pages open and closed (`lb-gside-tools` > `lb-gside-clip` > `ul`, inert while closed; `is-open`, and `has-current` raises a closed topic that holds the current page); pages have soft tiles under the topic's solid one; the topics a person opens stay open in that browser, the current page's topic starts open. The same day (\"always closed expect when hovering\") the side bar became an icon rail that opens over the page only while hovered, never pushing it: hover intent (it opens once the pointer settles, a fast pass does nothing, a press opens it at once), a 420ms close delay, a 28px forgiving edge, kept open while a press is held, while keyboard focus is in it and when the pointer leaves across the screen edge; after a link click or Esc it waits for the pointer to leave. With a mouse or trackpad the menu button is hidden; touch screens keep it. On phones the side bar is a drawer over the page with `lb-gscrim` and a close button (`lb-gside-close`), and `lb-gbottom` is the bottom nav bar (HQ, the first three topics, עוד), which slides away while scrolling down. `html.lb-has-gnav` makes room. `--lb-gnav-top`, `--lb-gnav-pad` and `--lb-gnav-space` stay defined for pages that use them and are 0px (the bottom bar's room on a phone). The nav also draws the language switch (8 Nov 2026) `lb-langfab`: a thick glass capsule floating at the bottom left of the window with two buttons, עב and EN, the current one pressed (`aria-pressed`), each a full 44px target, never translated themselves, and `lb-langfab-note` inside it while new words are being translated. On the project server it sits 8px right of the edit button and moves with it (the edit button sets `--lb-editbtn-x` and `--lb-editbtn-b` on `html`); elsewhere it takes the edit button's place, above the phone bottom bar; hidden while the editor is open (`html.lb-i18n-paused`). The switch (`window.LBI18N`, `shared/design/i18n.src.js`, words in `shared/i18n`) turns every page Hebrew or English; the side bar stays on the right in both, its words and direction follow the language. Since 7 Nov 2026 the side bar is a floating Liquid Glass panel inset .625rem from the window edge (the darker grey of the two) and the phone bottom bar a floating capsule with a tinted lens on the current topic. The preview shows it in place, without its fixed positions.",
                   '<div dir="rtl" lang="he" style="padding:16px"><div style="display:flex;height:340px;border:1px solid var(--line);border-radius:var(--r-md);overflow:hidden">'
                   f'<aside class="lb-gside" style="position:relative;inset:auto;width:13rem;z-index:auto" aria-label="כל הכלים"><div class="lb-gside-head"><a class="lb-gside-brand" href="#"><b>LumeBook</b></a><button type="button" class="lb-gside-toggle" aria-label="פתיחת סרגל הכלים">{ico("menu")}</button></div><nav class="lb-gside-scroll">'
                   f'<section class="lb-gside-topic lb-cat-2 is-open has-current"><h2 class="lb-gside-h"><button type="button" class="lb-gside-tbtn" aria-expanded="true"><span class="lb-tile" aria-hidden="true">{ico("people")}</span><span class="lb-gside-name">יוצרים</span><span class="lb-gside-chev" aria-hidden="true">{ico("chevron-down")}</span></button></h2><div class="lb-gside-tools"><div class="lb-gside-clip"><ul><li><a class="lb-gside-item" href="#" aria-current="page"><span class="lb-tile" aria-hidden="true">{ico("people")}</span><span class="lb-gside-name">מפת יוצרים</span></a></li><li><a class="lb-gside-item" href="#"><span class="lb-tile" aria-hidden="true">{ico("signup")}</span><span class="lb-gside-name">שגרירים</span></a></li><li><a class="lb-gside-item" href="#"><span class="lb-tile" aria-hidden="true">{ico("brief")}</span><span class="lb-gside-name">בריף ליוצרים</span></a></li></ul></div></div></section>'
                   f'<section class="lb-gside-topic lb-cat-5"><h2 class="lb-gside-h"><button type="button" class="lb-gside-tbtn" aria-expanded="false"><span class="lb-tile" aria-hidden="true">{ico("slides")}</span><span class="lb-gside-name">קרוסלות</span><span class="lb-gside-chev" aria-hidden="true">{ico("chevron-down")}</span></button></h2><div class="lb-gside-tools" inert><div class="lb-gside-clip"><ul><li><a class="lb-gside-item" href="#"><span class="lb-tile" aria-hidden="true">{ico("slides")}</span><span class="lb-gside-name">מכונת הקרוסלות</span></a></li></ul></div></div></section></nav>'
                   '</aside>'
                   '<div style="flex:1;min-width:0;position:relative"><p class="lb-small" style="padding:16px;margin:0">הדף עצמו</p>'
                   '<div class="lb-langfab lb-glass is-capsule is-thick" style="position:absolute;left:16px;bottom:16px;z-index:auto" role="group" aria-label="שפה · Language" translate="no" dir="ltr"><button type="button" lang="he" aria-pressed="true">עב</button><button type="button" lang="en" aria-pressed="false">EN</button></div></div>'
                   '</div></div>'),
    "Crumbs": ("Layout", 170, "`lb-crumbs` says where a view sits (the current item carries `aria-current` and cuts with an ellipsis; the chevron turns with the page direction; `hide-sm` hides the trail under 760px). `lb-pager` closes a lesson or section with the previous and next links, each a small label and a title.",
               '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px;max-width:560px"><nav class="lb-crumbs" aria-label="מיקום"><a href="#">מפת היוצרים</a><a href="#">מסלולים</a><span aria-current="page">הורים</span></nav><nav class="lb-pager"><a class="prev" href="#"><small>הקודם</small><b>פתיחים שעובדים</b></a><a class="next" href="#"><small>הבא</small><b>מילות קוד ותגובות</b></a></nav></div>'),
    "RowList": ("Layout", 260, "`lb-rowlist` is a list of rows that open (tasks, notes, actions). Each `details.lb-rowitem` has a summary with a marker (an `lb-disc` or a check), an `lb-rowitem-title` with a small line, an `lb-rowitem-meta` and the chevron; `lb-rowitem-body` lines up with the title. `is-done` strikes the title through. On a phone the meta drops under the title.",
                '<div dir="rtl" lang="he" style="padding:16px"><div class="lb-rowlist"><details class="lb-rowitem" open><summary><span class="lb-disc sm">1</span><span class="lb-rowitem-title">להוסיף שאלה בקופה: איך שמעתם עלינו?<small>בלי זה לא רואים מכירות מסרטון</small></span><span class="lb-rowitem-meta">צריך את יוסי</span></summary><div class="lb-rowitem-body"><p class="lb-small lb-muted">שאלה אחת עם 5 תשובות, שמורה עם ההזמנה.</p></div></details><details class="lb-rowitem"><summary><span class="lb-disc sm">2</span><span class="lb-rowitem-title">קישור אישי לכל יוצר<small>עם ההנחה לקהל בתוכו</small></span><span class="lb-rowitem-meta">השבוע</span></summary><div class="lb-rowitem-body"><p>הקישור מחיל את ההנחה לבד.</p></div></details><details class="lb-rowitem is-done"><summary><span class="lb-disc sm quiet">3</span><span class="lb-rowitem-title">תגי UTM על כל קישור</span><span class="lb-rowitem-meta">בוצע</span></summary></details></div></div>'),
    "Popover": ("Overlays", 300, "`lb-popover` is a small floating list under the button that opened it (a status menu, a page menu). Buttons or links inside, an optional `lb-popover-label` for a group, an `hr` between groups. The script places it and closes it on Escape and on a click outside.",
                '<div dir="rtl" lang="he" style="padding:16px;position:relative;min-height:200px"><button class="lb-btn secondary sm" type="button" aria-expanded="true">סטטוס: פנייה נשלחה</button><div class="lb-popover" style="top:56px;inset-inline-start:16px"><span class="lb-popover-label">להעביר אל</span><button type="button">חדש</button><button type="button" aria-current="true">פנייה נשלחה</button><button type="button">ספר נשלח</button><hr><button type="button">לא מתאים</button></div></div>'),
    "Glass": ("Materials", 430, "Liquid Glass (7 Nov 2026), the material of the control layer that floats above the content: a translucent grayscale tint over a blurred, saturated copy of what is behind it, a bright rim on the top edge, a soft lift. `lb-glass` is regular glass; `is-thick` goes under text (menus, sheets, drawers), `is-clear` over a photo or video, `is-tint` is violet glass for the one main action floating over content, `is-capsule` a pill, `is-interactive` lifts on hover and scales on press; `lb-btn-group` puts icon buttons in one capsule. Elements stack as sheets (Yarin, 07 Nov 2026: \"make every element like a sheet of glass on top of each other\"): `lb-sheet` is a sheet on a card, `lb-window` a separate window over its host, wider by `--overhang` (the creator card's follow-up), glass inside a card is lifted off it, and `lb-textblock` is a pressed-in well. Never glass on glass, never a table or paragraph, and no backdrop blur on anything repeated in a list (cards are glass without blur: see Card). More contrast and browsers without backdrop-filter get flat white and grey surfaces from the same tokens. The picture behind it in this preview is only here so the glass has something to show.",
              '<div dir="rtl" lang="he" style="padding:16px"><div style="position:relative;border-radius:var(--r-xl);overflow:hidden;min-height:370px;padding:20px;background:'
              'radial-gradient(60% 70% at 15% 20%,var(--cat-2) 0,transparent 70%),radial-gradient(55% 65% at 85% 25%,var(--cat-4) 0,transparent 70%),radial-gradient(60% 70% at 50% 100%,var(--cat-1) 0,transparent 70%),var(--lb-gold)">'
              '<div class="lb-glass is-capsule lb-row" style="padding:6px 8px;gap:6px;justify-content:space-between"><span class="lb-row" style="gap:6px"><span class="lb-btn secondary sm">לוח</span><span class="lb-btn secondary sm">יוצרים</span></span><span class="lb-chip" style="background:transparent">lb-glass is-capsule</span></div>'
              '<div class="lb-grid cols-2" style="margin-top:16px;gap:16px">'
              '<div class="lb-glass is-thick" style="padding:16px;display:grid;gap:8px"><b>זכוכית עבה</b><span class="lb-small lb-muted">מתחת לטקסט: תפריטים, מגירות, הודעות. הטקסט תמיד קריא.</span><span class="lb-row"><button class="lb-btn sm" type="button">פעולה ראשית</button><button class="lb-btn secondary sm" type="button">ביטול</button></span></div>'
              '<div class="lb-glass is-clear" style="padding:16px;display:grid;gap:8px;place-items:center;min-height:120px"><span class="lb-media-play" style="position:static"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></span><span class="lb-small" style="color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.4)">זכוכית שקופה מעל תמונה</span></div></div>'
              '<div class="lb-row" style="margin-top:16px;gap:12px"><span class="lb-btn-group"><button class="lb-btn icon" type="button" aria-pressed="true" aria-label="רשת"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/></svg></button><button class="lb-btn icon" type="button" aria-label="רשימה"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M5 7h14M5 12h14M5 17h14"/></svg></button></span>'
              '<span class="lb-glass is-tint is-capsule is-interactive" style="padding:10px 18px;font-weight:700">זכוכית בגוון</span>'
              '<span class="lb-segmented"><button type="button" aria-pressed="true">יום</button><button type="button" aria-pressed="false">שבוע</button><button type="button" aria-pressed="false">חודש</button></span></div></div></div>'),
    "Utilities": ("Type", 200, "Small pieces: `lb-clamp-2` and `lb-clamp-3` cut text after two or three lines; `ul.lb-bullets` (and `lb-prose` lists) get gold bullets; `lb-kbd` is a keycap; `lb-spinner` shows work in progress; `lb-savestate` is a dot and a word for whether edits are saved (`is-wait`, `is-error`, `is-local` for this browser only); `lb-pid is-solid` is a dark ID chip; `lb-flash` (or `lb-target` on a #target) rings the item a link just jumped to.",
                  '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-stack"><p class="lb-clamp-2 lb-small">טקסט ארוך שנחתך אחרי שתי שורות כדי שהכרטיס יישאר באותו גובה כמו השכנים שלו, גם כשהתיאור של הריל ארוך מאוד ומפורט.</p><ul class="lb-bullets lb-small"><li>פנים בשתי השניות הראשונות</li><li>כתוביות על כל סרטון</li></ul></div><div class="lb-stack"><div class="lb-row"><span>חיפוש</span><kbd class="lb-kbd">/</kbd><span class="lb-spinner" aria-label="טוען"></span><span class="lb-pid is-solid">kid-2</span></div><div class="lb-row"><span class="lb-savestate">נשמר</span><span class="lb-savestate is-wait">שומר...</span></div><div class="lb-row"><span class="lb-savestate is-error">לא נשמר</span><span class="lb-savestate is-local">רק בדפדפן הזה</span></div></div></div>'),
}


def preview(name, group, height, body):
    return (f'<!-- @dsCard group="{group}" height={height} -->\n<link rel="stylesheet" href="{FONTS_URL}">\n'
            f'{body}\n<script>document.documentElement.setAttribute("dir","rtl")</script>\n')


COVER = """<!-- @dsCard height=300 -->
<link rel="stylesheet" href="%s">
<style>
.cv{position:relative;width:960px;height:300px;background:var(--bg);overflow:hidden;font-family:var(--font)}
.cv svg{position:absolute;inset:0}
.ink{fill:var(--text)} .gold{fill:var(--lb-gold)} .violet{fill:var(--tint)} .cream{fill:var(--surface-2)} .soft{fill:var(--accent-soft)}
.dot{fill:var(--bg)}
.cv .name{position:absolute;left:40px;bottom:64px;font-family:var(--font);font-weight:800;letter-spacing:-.03em;font-size:96px;line-height:.92;color:var(--text);margin:0}
.cv .tag{position:absolute;left:44px;bottom:36px;font-size:14px;color:var(--text-2);margin:0;max-width:420px}
</style>
<div class="cv" dir="ltr">
  <svg viewBox="0 0 960 300" width="960" height="300" aria-hidden="true">
    <!-- blocks: lb-ink 208x300 slab, lb-gold 176x176 pill-cornered (r-lg), tint 120x120 disc, accent-soft 168x96 band, surface-2 ground strip
         arrangement: one tall ink slab bleeding off the top and bottom with satellites stacked toward the right edge, like a book spine and its pages
         pattern: discs and half-rounds (soft, friendly, pill radii in the system) - a 4x3 grid of sp-5 dots cut out of the ink slab
         scales: sp-4/sp-5/sp-6 gaps, radius r-lg (18px) and r-pill (half side) -->
    <rect class="cream" x="480" y="0" width="480" height="300"/>
    <rect class="ink" x="520" y="-20" width="208" height="340" rx="18"/>
    <g class="dot">%s</g>
    <rect class="gold" x="752" y="24" width="176" height="176" rx="18"/>
    <circle class="violet" cx="840" cy="246" r="60"/>
    <rect class="soft" x="752" y="214" width="96" height="64" rx="32"/>
  </svg>
  <p class="name">LumeBook</p>
  <p class="tag">One design system for every internal page: Hebrew first, light only, violet to click, gold to celebrate.</p>
</div>
"""


def _rgb(v):
    v = v.strip()
    if v.startswith("#"):
        return [int(v[i:i + 2], 16) / 255 for i in (1, 3, 5)], 1.0
    m = re.match(r"rgba?\(([^)]*)\)", v)
    parts = [float(x) for x in m.group(1).replace(" ", "").split(",")]
    return [x / 255 for x in parts[:3]], (parts[3] if len(parts) > 3 else 1.0)


def _over(top, ground):
    (c, a), (g, _) = _rgb(top), _rgb(ground)
    return [a * x + (1 - a) * y for x, y in zip(c, g)]


def _ratio(fg, bg):
    lum = lambda c: sum(w * (x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4) for w, x in zip((.2126, .7152, .0722), c))
    a, b = sorted((lum(fg), lum(bg)), reverse=True)
    return (a + .05) / (b + .05)


def palette_md():
    rows = ["| Token | Hue | Base | Ink | Soft | Playbook alias |", "|---|---|---|---|---|---|"]
    for i, hue in CAT_HUES.items():
        rows.append(f"| `cat-{i}` | {hue} | `{light[f'cat-{i}'].strip()}` | `{light[f'cat-{i}-ink'].strip()}` | `{light[f'cat-{i}-soft'].strip()}` "
                    f"| {CAT_PLAYBOOK[i]} |")
    return "\n".join(rows)


def contrast_md():
    out, worst_all = [], 99
    for mode, t in (("White", light),):
        surf, bg, s2 = (t[k].strip() for k in ("surface", "bg", "surface-2"))
        grounds = lambda soft: (_rgb(surf)[0], _rgb(bg)[0], _rgb(s2)[0], _over(soft, surf), _over(soft, bg))
        rows = [f"**{mode}**", "", "| Token | ink on surface | ink on bg | ink on surface-2 | ink on soft (on surface) | ink on soft (on bg) | base under icons |", "|---|---|---|---|---|---|---|"]
        for i in CAT_HUES:
            ink, soft, base = _rgb(t[f"cat-{i}-ink"])[0], t[f"cat-{i}-soft"], t[f"cat-{i}"]
            r = [_ratio(ink, g) for g in grounds(soft)] + [_ratio(_rgb(t["text-on-tint"])[0], _rgb(base)[0])]
            rows.append(f"| `cat-{i}` | " + " | ".join(f"{x:.2f}" for x in r[:5]) + f" | {r[5]:.2f} (icons only) |")
        worst = min(_ratio(_rgb(t[f"cat-{i}-ink"])[0], g) for i in CAT_HUES for g in grounds(t[f"cat-{i}-soft"]))
        # text and the coloured text tokens on every surface, and text on a tint button
        pairs = [(k, g) for k in ("text", "text-2", "text-3", "tint", "accent-ink", "success", "warning", "danger", "info", "kid", "expert")
                 for g in (surf, bg, s2)] + [("text-on-tint", t["tint"].strip())]
        low = min((_ratio(_rgb(t[k])[0], _rgb(g if g.startswith("#") else t[g])[0]), k) for k, g in pairs)
        assert worst >= 4.5, f"{mode}: a category ink falls below 4.5:1 ({worst:.2f})"
        assert low[0] >= 4.5, f"{mode}: {low[1]} falls below 4.5:1 ({low[0]:.2f})"
        rows += ["", f"Lowest category ink: {worst:.2f}:1. Lowest text token: {low[0]:.2f}:1 (`{low[1]}`)."]
        out.append("\n".join(rows))
    return "\n\n".join(out)


def main(out):
    proj = os.path.join(out, "project")
    os.makedirs(os.path.join(proj, "components"), exist_ok=True)
    w = lambda rel, text: (os.makedirs(os.path.dirname(os.path.join(proj, rel)), exist_ok=True), open(os.path.join(proj, rel), "w", encoding="utf-8").write(text))
    w("tokens.json", json.dumps(tokens(), ensure_ascii=False, indent=2))
    w("README.md", README.replace("{{FONTS_URL}}", FONTS_URL).replace("{{PALETTE}}", palette_md()).replace("{{CONTRAST}}", contrast_md()))
    w("components/bundle.css", f'@import url("{FONTS_URL}");\n' + CSS)
    for name, (group, height, guide, body) in COMPONENTS.items():
        w(f"components/{name}/README.md", f"# {name}\n\n{guide}\n")
        w(f"components/{name}/preview.html", preview(name, group, height, body))
    dots = "".join(f'<circle cx="{556 + c * 44}" cy="{40 + r * 44}" r="10"/>' for r in range(6) for c in range(4) if (r + c) % 2 == 0)
    w("components/Cover/preview.html", COVER % (FONTS_URL, dots))
    w("assets/Logos/README.md", "# Logos\n\nThe LumeBook marks. `logo_square.png` is the square mark used in page top bars (about 28px); `logo_wide.png` is the wordmark used in the dashboard sidebar. Use them as given on a light surface; never recolor or redraw them.\n")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index = {"v": 3, "layout": "files", "createdOnFiles": {"v": 1, "at": now}, "title": "LumeBook", "namespace": "LumeBook",
             "libraries": [], "sections": {}, "groups": ["Logos"],
             "assetGroups": {"Logos": {"name": "Logos", "tile": "l", "order": list(LOGOS),
                                       "files": {k: {"name": k, "blob": v[0], "size": v[1], "type": "image/png"} for k, v in LOGOS.items()}}},
             "blobs": {}, "docs": {"readme": "project/README.md", "sections": []},
             "lastChange": {"by": "Yarin Bruner", "at": now, "via": "Claude Code", "note": "Generated from shared/design/lumebook.css"}}
    w("design-system.json", json.dumps(index, ensure_ascii=False, indent=2))
    files = sorted(os.path.relpath(os.path.join(dp, f), out) for dp, _, fs in os.walk(proj) for f in fs)
    print(json.dumps(files, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "_ds_artifact"))
