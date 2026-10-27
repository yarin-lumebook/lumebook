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
FONTS_URL = "https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&family=Assistant:wght@400;500;600;700&display=swap"
LOGOS = {"logo_square.png": ("fced3317e50c510f4abe26ccb21e46f5", 141241), "logo_wide.png": ("b8b883e0138996754585bb68186ae69c", 90647)}


def block(selector_regex):
    m = re.search(selector_regex + r"\s*\{(.*?)\n\}", CSS, re.S | re.M)
    return dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", m.group(1))) if m else {}


light = block(r"^:root")
if not light:
    light = dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", CSS.split("@media")[0]))
dark = block(r'^:root\[data-theme="dark"\]')   # black mode (21 Oct 2026): only the tokens it changes

COLOR_USAGE = {
    "lb-ink": "Brand ink (fixed in both modes).",
    "lb-ink-deep": "Brand ink, deepest.",
    "lb-gold": "Brand gold. never body text on light.",
    "lb-gold-deep": "Brand gold, deeper.",
    "lb-violet": "Brand violet.",
    "lb-cream": "Brand cream.",
    "bg": "Page ground: white, black in dark mode.",
    "surface": "Cards, grouped rows, tables, inputs.",
    "surface-2": "Sidebar, inset areas inside a card, table header row.",
    "surface-sunk": "Wells, code blocks.",
    "bar": "Translucent sticky top bars (with backdrop blur).",
    "overlay": "Scrim behind drawers, modals and the mobile sidebar.",
    "text": "Primary text and headings. 4.5:1 or more on every surface.",
    "text-2": "Secondary text: descriptions, table cells that support a primary value.",
    "text-3": "Tertiary text: labels, captions, metadata.",
    "text-on-tint": "Text on a solid tint button or count.",
    "fill": "Quiet fill: hover rows, chips, search field, code.",
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
         "bg", "surface", "surface-2", "surface-sunk", "bar", "overlay",
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
        if name in dark and dark[name].strip() != light[name].strip():
            val["dark"] = color_value(dark[name])
        colors.append({"name": name, "value": val, "usage": COLOR_USAGE.get(name, "")})
    fam = {"sans": light["font"], "secondary": light["font-2"], "mono": light["font-mono"]}
    fam = {k: v.strip() for k, v in fam.items()}
    t = {
        "name": "LumeBook", "version": 1,
        "meta": {"source": "shared/design/lumebook.css (LumeBook project repo)"},
        "color": {"themes": [{"id": "light", "name": "White"}, {"id": "dark", "name": "Black"}], "tokens": colors},
        "type": {"fonts": [], "families": fam, "groups": [
            {"name": "Display", "family": "sans", "styles": [
                {"name": "display", "fontSize": "38px", "lineHeight": 1.15, "fontWeight": 800, "sample": "לוח לומבוק", "usage": "Page titles (h1). Heebo ExtraBold, tracking -0.015em; once per page."},
                {"name": "title", "fontSize": "22px", "lineHeight": 1.25, "fontWeight": 700, "sample": "דורש תשומת לב", "usage": "Section titles (h2). Heebo Bold, tracking -0.01em."}]},
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
                              [("r-xs", "Code, bars, small marks."), ("r-sm", "Inputs, nav items, segmented control."),
                               ("r-md", "Grouped lists, tables, alerts, empty states."), ("r-lg", "Cards."), ("r-pill", "Buttons, chips, search.")]]},
        "shadow": {"tokens": [{"name": n, "value": {"light": light[n].strip(), "dark": dark[n].strip()}, "usage": u} for n, u in
                              [("shadow-1", "Active nav item, segmented thumb."), ("shadow-2", "Raised card, hovered link card."), ("shadow-3", "Drawers, modals, toasts, mobile sidebar.")]]},
    }
    return t


README = """# LumeBook

The design system for every internal LumeBook page: the project dashboard (לוח לומבוק), the SMM plan, the creator map, the research reports and the nightly carousel review. It is Hebrew first and right to left, white or black by a switch, and built for scanning operational data.

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
- Dates as day.month (8.10), numbers with tabular figures, handles and paths isolated left to right (`lb-ltr`).

## Visual foundations

- **Surfaces.** White page (`bg`) and cards (`surface`) set apart by hairlines, a light grey sidebar and inset areas (`surface-2`); in black mode a black page, near-black cards and a slightly lighter sidebar. Hierarchy comes from surface steps and hairlines (`line`), with shadows only on things that float.
- **Three roles for color.** `text` (neutral ink, near black or near white) for reading; `tint` (violet) for anything you can click, and only for that; `accent` (gold) for brand emphasis and progress. Gold text uses `accent-ink` so it passes contrast.
- **State is shape plus color.** Status always appears as a chip, dot, count or tinted alert row with a word, never color alone. `success`, `warning`, `danger`, `info` are separate from the accent.
- **Carousel pillars.** `kid` (violet) for "הילד מספר", `expert` (gold) for "גישה מקצועית", matching the slide designs.
- **Category colour.** Eight hues (`cat-1` to `cat-8`, each with a base, an ink and a soft) for a page's 3 to 8 stable categories that a reader scans or filters by: the playbook's tools, the dashboard's workstreams, the creator map's tracks. See "Category colour" below.
- **Type.** Heebo is the main font, headings included (h1 ExtraBold 800, h2 Bold 700, slightly tight tracking); Assistant is the secondary font for labels, captions, counts, chips, table headers and the sidebar group labels. Both carry Hebrew and Latin. Body text, buttons and inputs stay on Heebo. System mono for commands. Scale: display 38, title 22, headline 18, body 16, callout 15, footnote 13, caption 12. Varela Round was dropped on 18 Oct 2026.
- **Space and shape.** 4pt spacing, pill buttons and chips, 18px card radius, 12px for tables and grouped lists.
- **Theme.** White and black modes with a switch (Yarin, 21 Oct 2026; the cream and purple grounds are gone). White is `:root`, black is `:root[data-theme="dark"]`, with the same token names. `design.head()` sets `data-theme` before first paint from the viewer's saved choice (white by default) and `design.theme_toggle()` writes the switch (`.lb-theme-switch`, sun and moon) for the top bar. Only the switch changes the mode, never the system setting. Every text token passes 4.5:1 on every surface in both modes.
- **Motion.** Short (0.15s to 0.2s) color and slide transitions only; all motion stops under `prefers-reduced-motion`.

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

Inline SVG line icons on a 24 grid, `stroke="currentColor"`, stroke width 2, no fill, so they take the text color. No emoji as UI markers. The LumeBook logo is the only image mark (Logos group).

## Components

Each has a live preview and guidelines in Components. All class names start with `lb-` so a page can adopt the system one piece at a time.
"""

COMPONENTS = {
    "Button": ("Actions", 120, "Pill buttons. Primary (tint) for the one main action in a view, `secondary` for everything else, `ghost` for inline actions, `danger` only to remove something. Sizes: default and `sm`; `icon` for square icon buttons with an `aria-label`.",
               '<div dir="rtl" lang="he" class="lb-row" style="padding:16px"><button class="lb-btn" type="button">לפרסם מחדש</button><button class="lb-btn secondary" type="button">לתוכנית המלאה</button><button class="lb-btn ghost" type="button">פתיחה</button><button class="lb-btn secondary sm" type="button">להציג 2 שורות בדיקה</button><button class="lb-btn secondary sm icon" type="button" aria-label="עוד">+</button><button class="lb-btn" type="button" disabled>לא זמין</button></div>'),
    "Segmented": ("Actions", 90, "A small set of mutually exclusive filters. Each button carries `aria-pressed`. Use for 2 to 5 options; more belong in a select.",
                  '<div dir="rtl" lang="he" style="padding:16px"><div class="lb-segmented" role="group" aria-label="קבוצה"><button type="button" aria-pressed="true">הכול</button><button type="button" aria-pressed="false">ברטר</button><button type="button" aria-pressed="false">בתשלום</button><button type="button" aria-pressed="false">שורטליסט</button></div></div>'),
    "Field": ("Forms", 170, "Inputs, selects and the search field. Every control has a visible label (`lb-field`) or an `aria-label`. The search field is a pill on a quiet fill.",
              '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px;max-width:360px"><div class="lb-search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg><input class="lb-input" type="search" placeholder="חיפוש יוצר" aria-label="חיפוש יוצר"></div><label class="lb-field">שם היוצר<input class="lb-input" value="אורי"></label><label class="lb-field">מצב<select class="lb-select"><option>נשלחה פנייה</option><option>ענו</option></select></label></div>'),
    "Check": ("Forms", 130, "Checkbox rows for task lists. A checked task strikes through and dims. The tick is drawn with physical borders so it never mirrors on RTL pages.",
              '<div dir="rtl" lang="he" class="lb-stack" style="padding:16px"><label class="lb-check"><input type="checkbox" checked><span>לסגור את הבריף לרילס של השבוע</span></label><label class="lb-check"><input type="checkbox"><span>לשלוח 5 פניות ליוצרים מהברטר</span></label><label class="lb-check"><input type="checkbox" disabled><span>קריאה בלבד</span></label></div>'),
    "Switch": ("Forms", 80, "An on and off setting that applies immediately. Use a checkbox for list items and a switch for settings.",
               '<div dir="rtl" lang="he" class="lb-row" style="padding:16px;gap:12px"><input class="lb-switch" type="checkbox" checked aria-label="מצב כהה"><span>תזכורת בוקר</span><input class="lb-switch" type="checkbox" aria-label="כבוי"><span class="lb-muted">כבוי</span></div>'),
    "Stat": ("Data", 200, "A stat tile: label, big tabular number with an optional delta or small unit, a one-line foot, optional bar and sparkline. Open a dashboard with stat tiles only when the numbers are the point.",
             '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-card lb-stat"><span class="lb-stat-label">עוקבים <bdi class="lb-ltr">@lumebookai</bdi></span><span class="lb-stat-value">918<small class="lb-delta up"><bdi class="lb-ltr">+12</bdi></small></span><div class="lb-bar"><i style="width:31%"></i></div><span class="lb-stat-foot">יעד דצמבר 3-4K</span></div><div class="lb-card lb-stat"><span class="lb-stat-label">מאגר יוצרים</span><span class="lb-stat-value">204<small>15 בשורטליסט</small></span><span class="lb-stat-foot">12 בסבב ברטר ראשון</span></div></div>'),
    "Table": ("Data", 210, "Data tables sit in `lb-table-wrap`, which scrolls sideways on its own. Numbers get `num` (tabular, aligned to the end). Header row on `surface-2`; rows highlight on hover.",
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
    "Callout": ("Status", 110, "A tinted note for how-to or context inside a page. Gold by default, `info` for neutral help. One per section at most.",
                '<div dir="rtl" lang="he" style="padding:16px"><div class="lb-callout info"><b>לעבור על החבילה ולערוך</b><span>החבילה נבנית כל לילה ב-22:00. לעריכה במקום: <code class="lb-ltr">review_server.py</code></span></div></div>'),
    "Card": ("Layout", 190, "The main container. `is-quiet` for secondary groupings, `is-raised` for one floating element, `is-accent` for the current item (this week). A card that is a link uses `<a class=\"lb-card\">` and lifts on hover.",
             '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-card is-accent"><div class="lb-card-head"><span class="lb-card-title">שבוע 2 · עכשיו</span><span class="lb-xs lb-dim">3/7</span></div><span>לסגור בריף, לשלוח פניות, לבדוק חבילה</span></div><a class="lb-card" href="#"><span class="lb-chip accent">מחקר תוכן</span><b>מחקר קרוסלות</b><span class="lb-muted lb-small">752 חשבונות בישראל ובעולם</span></a></div>'),
    "Group": ("Layout", 150, "An Apple-style inset grouped list: rows separated by hairlines inside one rounded container. Rows can be links; metadata sits at the end.",
              '<div dir="rtl" lang="he" style="padding:16px;max-width:420px"><div class="lb-group"><a class="lb-group-row" href="#"><span>טופס יוצרי תוכן</span><span class="lb-meta">Google Form</span></a><a class="lb-group-row" href="#"><span>גיליון ההרשמות</span></a><a class="lb-group-row" href="#"><span>תיקיית שיווק בדרייב</span></a></div></div>'),
    "Navigation": ("Layout", 260, "Sidebar navigation for app pages: group labels, items with a 24-grid line icon, an optional count, `aria-current=\"page\"` on the current view. Under 860px the sidebar becomes a drawer.",
                   '<div dir="rtl" lang="he" style="padding:16px;max-width:260px"><nav class="lb-nav" style="background:var(--surface-2);padding:12px;border-radius:var(--r-lg)"><div class="lb-nav-label">היום</div><a class="lb-nav-item" href="#" aria-current="page"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>סקירה<span class="lb-count is-alert">3</span></a><div class="lb-nav-label">עבודה</div><a class="lb-nav-item" href="#"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/></svg>תוכנית<span class="lb-count">10</span></a><a class="lb-nav-item" href="#"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/></svg>יוצרים</a></nav></div>'),
    "Toc": ("Layout", 80, "Pill section navigation for reading pages and reports, usually inside the top bar. The current section gets `aria-current=\"true\"`.",
            '<div dir="rtl" lang="he" style="padding:16px"><nav class="lb-toc"><a href="#" aria-current="true">שבועות</a><a href="#">יעדים</a><a href="#">מדדים</a><a href="#">סרטונים שעבדו</a><a href="#">לוודא עם יוסי</a></nav></div>'),
    "Empty": ("Feedback", 110, "Empty and loading states say what will appear and how it gets there. Use `lb-skeleton` blocks while data loads.",
              '<div dir="rtl" lang="he" class="lb-grid cols-2" style="padding:16px"><div class="lb-empty">חבילת הלילה תופיע כאן אחרי הריצה הבאה ב-22:00.</div><div class="lb-stack"><div class="lb-skeleton" style="height:1.2rem;width:60%"></div><div class="lb-skeleton" style="height:2.4rem"></div></div></div>'),
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
  <p class="tag">One design system for every internal page: Hebrew first, white or black, violet to click, gold to celebrate.</p>
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
    rows = ["| Token | Hue | Base | Ink | Soft | Black base | Black ink | Playbook alias |", "|---|---|---|---|---|---|---|---|"]
    for i, hue in CAT_HUES.items():
        rows.append(f"| `cat-{i}` | {hue} | `{light[f'cat-{i}'].strip()}` | `{light[f'cat-{i}-ink'].strip()}` | `{light[f'cat-{i}-soft'].strip()}` "
                    f"| `{dark[f'cat-{i}'].strip()}` | `{dark[f'cat-{i}-ink'].strip()}` | {CAT_PLAYBOOK[i]} |")
    return "\n".join(rows)


def contrast_md():
    out, worst_all = [], 99
    for mode, t in (("White", light), ("Black", {**light, **dark})):
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
