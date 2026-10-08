#!/usr/bin/env python3
"""Generate the LumeBook Design System artifact's files from shared/design/lumebook.css.

The stylesheet is the source of truth; this writes the browsable reference
(https://claude.ai/artifact/RjUuSdYDwaJe4HWyEErNmF) as files under <out>/project/:
tokens.json, README.md, components/bundle.css, components/<Comp>/{README.md,preview.html},
components/Cover/preview.html and design-system.json (the index).

    python3 shared/design/build_ds_artifact.py <out dir>

Then publish <out>/project/* to the artifact (see the Design System type's instructions). Standard library only.
"""
import json, os, re, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(HERE, "lumebook.css"), encoding="utf-8").read()
FONTS_URL = "https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&family=Varela+Round&display=swap"
LOGOS = {"logo_square.png": ("d2e355f0add8153fb9f1b34b4e5b765d", 141241), "logo_wide.png": ("6c21967df0d6986aaa6b654fa3bb759a", 90647)}


def block(selector_regex):
    m = re.search(selector_regex + r"\s*\{(.*?)\n\}", CSS, re.S)
    return dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", m.group(1))) if m else {}


light = block(r"^:root")
if not light:
    light = dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", CSS.split("@media")[0]))
dark = block(r":root\[data-theme=\"dark\"\]")

COLOR_USAGE = {
    "lb-ink": "Brand ink. Same in both themes; the toast ground.",
    "lb-ink-deep": "Brand ink, deepest. Same in both themes.",
    "lb-gold": "Brand gold. Same in both themes; never body text on light.",
    "lb-gold-deep": "Brand gold, deeper. Same in both themes.",
    "lb-violet": "Brand violet. Same in both themes.",
    "lb-cream": "Brand cream. Same in both themes.",
    "bg": "Page ground (warm cream in light).",
    "surface": "Cards, grouped rows, tables, inputs.",
    "surface-2": "Sidebar, inset areas inside a card, table header row.",
    "surface-sunk": "Wells, code blocks.",
    "bar": "Translucent sticky top bars (with backdrop blur).",
    "overlay": "Scrim behind drawers, modals and the mobile sidebar.",
    "text": "Primary text and headings. 4.5:1 or more on every surface.",
    "text-2": "Secondary text: descriptions, table cells that support a primary value.",
    "text-3": "Tertiary text: labels, captions, metadata.",
    "text-on-tint": "Text on a solid tint button or count (white in light, ink in dark).",
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
    COLOR_USAGE[f"seq-{i}"] = f"Sequential data series step {i} of 6 (stages, bars), light to dark."

ORDER = ["lb-ink", "lb-ink-deep", "lb-gold", "lb-gold-deep", "lb-violet", "lb-cream",
         "bg", "surface", "surface-2", "surface-sunk", "bar", "overlay",
         "text", "text-2", "text-3", "text-on-tint", "fill", "fill-2", "fill-3", "line", "line-strong",
         "tint", "tint-hover", "tint-soft", "focus", "accent", "accent-soft", "accent-ink",
         "success", "success-soft", "warning", "warning-soft", "danger", "danger-soft", "info", "info-soft",
         "kid", "kid-soft", "expert", "expert-soft"] + [f"seq-{i}" for i in range(1, 7)]


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
    fam = {"sans": light["font"], "display": light["font-display"], "mono": light["font-mono"]}
    fam = {k: v.strip() for k, v in fam.items()}
    t = {
        "name": "LumeBook", "version": 1,
        "meta": {"source": "shared/design/lumebook.css (LumeBook project repo)"},
        "color": {"themes": [{"id": "light", "name": "Light"}, {"id": "dark", "name": "Dark"}], "tokens": colors},
        "type": {"fonts": [], "families": fam, "groups": [
            {"name": "Display", "family": "display", "styles": [
                {"name": "display", "fontSize": "40px", "lineHeight": 1.12, "fontWeight": 400, "sample": "לוח לומבוק", "usage": "Page titles (h1). Varela Round, rounded and friendly like the books; once per page."},
                {"name": "title", "fontSize": "24px", "lineHeight": 1.2, "fontWeight": 400, "sample": "דורש תשומת לב", "usage": "Section titles (h2)."}]},
            {"name": "Text", "family": "sans", "styles": [
                {"name": "headline", "fontSize": "18px", "lineHeight": 1.3, "fontWeight": 700, "sample": "שבוע 2 · עכשיו", "usage": "Card titles (h3)."},
                {"name": "body", "fontSize": "16px", "lineHeight": 1.55, "fontWeight": 400, "sample": "ספר במתנה, קישור אישי עם הנחה לקהל ועד 25% עמלה.", "usage": "Running text, up to about 42rem wide."},
                {"name": "callout", "fontSize": "15px", "lineHeight": 1.5, "fontWeight": 400, "sample": "16 יוצרים במעקב", "usage": "Table cells, lists, buttons, nav items."},
                {"name": "footnote", "fontSize": "13px", "lineHeight": 1.45, "fontWeight": 500, "sample": "נבדק לפני 2 שע׳", "usage": "Labels, chips, metadata."},
                {"name": "caption", "fontSize": "12px", "lineHeight": 1.4, "fontWeight": 600, "sample": "עבודה", "usage": "Sidebar group labels, counts."}]},
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
        "shadow": {"tokens": [{"name": n, "value": {"light": light[n].strip(), "dark": dark.get(n, light[n]).strip()}, "usage": u} for n, u in
                              [("shadow-1", "Active nav item, segmented thumb."), ("shadow-2", "Raised card, hovered link card."), ("shadow-3", "Drawers, modals, toasts, mobile sidebar.")]]},
    }
    return t


README = """# LumeBook

The design system for every internal LumeBook page: the project dashboard (לוח לומבוק), the SMM plan, the creator map, the research reports and the nightly carousel review. It is Hebrew first and right to left, light by default with a dark theme, and built for scanning operational data.

It is **not** used by the public ambassadors site (lumebook-ambassadors.vercel.app), which keeps its own look for creators, or by the carousel slides themselves, whose two pillar looks are audience content.

## Where it lives

- Source of truth: `shared/design/lumebook.css` in the LumeBook project repo. Every page build inlines it (`shared/design/design.py`: `design.head()`, `design.theme_toggle()`, `design.logo_data_uri()`). The SMM plan has no build, so it links a synced copy (`tools/lumebook.py sync`).
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

- **Surfaces.** Warm cream page (`bg`), white cards (`surface`), a slightly darker sidebar and inset areas (`surface-2`). Hierarchy comes from surface steps and hairlines (`line`), with shadows only on things that float.
- **Three roles for color.** `text` (LumeBook ink) for reading; `tint` (violet) for anything you can click, and only for that; `accent` (gold) for brand emphasis and progress. Gold text uses `accent-ink` so it passes contrast.
- **State is shape plus color.** Status always appears as a chip, dot, count or tinted alert row with a word, never color alone. `success`, `warning`, `danger`, `info` are separate from the accent.
- **Carousel pillars.** `kid` (violet) for "הילד מספר", `expert` (gold) for "גישה מקצועית", matching the slide designs.
- **Type.** Varela Round for page and section titles (rounded like the books), Heebo for everything else (Hebrew and Latin from one family), system mono for commands. Scale: display 40, title 24, headline 18, body 16, callout 15, footnote 13, caption 12.
- **Space and shape.** 4pt spacing, pill buttons and chips, 18px card radius, 12px for tables and grouped lists.
- **Themes.** Light on bare `:root`; dark under `[data-theme="dark"]` and the OS preference unless the viewer chose light. Pages start light (Yarin's choice) and remember the toggle in `localStorage` key `lb-theme`. Every text token passes 4.5:1 on every surface in both themes.
- **Motion.** Short (0.15s to 0.2s) color and slide transitions only; all motion stops under `prefers-reduced-motion`.

## Layout

- App pages: `lb-app` (sidebar + main), `lb-sidebar` with `lb-nav-item`s grouped by `lb-nav-label`, a sticky `lb-topbar`, content in `lb-page` > `lb-section` blocks. Under 860px the sidebar becomes a drawer opened from `lb-menu-btn`.
- Reading pages and reports: `lb-topbar` with logo, page name, an `lb-toc` section nav, the link back to the dashboard and the theme toggle; then `lb-page`.
- Grids: `lb-grid` (auto-fit, set `--min`), or `cols-2/3/4` that step down to 2 then 1 column. Rows: `lb-row`, stacks: `lb-stack`.
- Phone width (390px) never scrolls sideways; wide tables scroll inside `lb-table-wrap`.

## Iconography

Inline SVG line icons on a 24 grid, `stroke="currentColor"`, stroke width 2, no fill, so they take the text color and theme. No emoji as UI markers. The LumeBook logo is the only image mark (Logos group).

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
    "Chip": ("Status", 110, "Short status words. Neutral by default; `tint`, `accent`, `success`, `warning`, `danger`, `info`, and the pillars `kid` and `expert`; `outline` for tags. Add `lb-dot` for live or health state. A chip always carries a word, never color alone.",
             '<div dir="rtl" lang="he" class="lb-row" style="padding:16px"><span class="lb-chip">שורטליסט</span><span class="lb-chip tint">סנכרון</span><span class="lb-chip accent">ברטר</span><span class="lb-chip success"><span class="lb-dot"></span>באוויר</span><span class="lb-chip warning">לפרסם מחדש</span><span class="lb-chip danger">מחזיר 500</span><span class="lb-chip info">לוודא עם יוסי</span><span class="lb-chip kid">kid-2 · הילד מספר</span><span class="lb-chip expert">expert-1 · גישה מקצועית</span><span class="lb-chip outline">רגע</span><span class="lb-count">16</span><span class="lb-count is-alert">3</span></div>'),
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
.cv .name{position:absolute;left:40px;bottom:64px;font-family:var(--font-display);font-size:96px;line-height:.92;color:var(--text);margin:0}
.cv .tag{position:absolute;left:44px;bottom:36px;font-size:14px;color:var(--text-2);margin:0;max-width:420px}
</style>
<div class="cv" dir="ltr">
  <svg viewBox="0 0 960 300" width="960" height="300" aria-hidden="true">
    <!-- blocks: lb-ink 208x300 slab, lb-gold 176x176 pill-cornered (r-lg), tint 120x120 disc, accent-soft 168x96 band, surface-2 ground strip
         arrangement: one tall ink slab bleeding off the top and bottom with satellites stacked toward the right edge, like a book spine and its pages
         pattern: discs and half-rounds (soft, friendly, pill radii in the system; rounded display face) - a 4x3 grid of sp-5 dots cut out of the ink slab
         scales: sp-4/sp-5/sp-6 gaps, radius r-lg (18px) and r-pill (half side) -->
    <rect class="cream" x="480" y="0" width="480" height="300"/>
    <rect class="ink" x="520" y="-20" width="208" height="340" rx="18"/>
    <g class="dot">%s</g>
    <rect class="gold" x="752" y="24" width="176" height="176" rx="18"/>
    <circle class="violet" cx="840" cy="246" r="60"/>
    <rect class="soft" x="752" y="214" width="96" height="64" rx="32"/>
  </svg>
  <p class="name">LumeBook</p>
  <p class="tag">One design system for every internal page: Hebrew first, cream and ink, violet to click, gold to celebrate.</p>
</div>
"""


def main(out):
    proj = os.path.join(out, "project")
    os.makedirs(os.path.join(proj, "components"), exist_ok=True)
    w = lambda rel, text: (os.makedirs(os.path.dirname(os.path.join(proj, rel)), exist_ok=True), open(os.path.join(proj, rel), "w", encoding="utf-8").write(text))
    w("tokens.json", json.dumps(tokens(), ensure_ascii=False, indent=2))
    w("README.md", README)
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
