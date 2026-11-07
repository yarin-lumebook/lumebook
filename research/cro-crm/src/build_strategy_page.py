#!/usr/bin/env python3
"""Build the CRO and CRM strategy page from the research Markdown.

    python3 research/cro-crm/src/build_strategy_page.py

Input:  research/cro-crm/{report,numbers-2026-10-25,audit,experiments,crm-flows,measurement,roadmap,sources}.md and
        research/cro-crm/src/journey-actions.json (the Hebrew action list, every action in the journey demo; its pictures
        come from media/projects/2026-10-24-cro-crm-actions/ and are left out when missing). Edit them, then rebuild,
        never edit the HTML
Output: research/cro-crm/cro-crm-strategy.html, one page on the LumeBook design system (design.head() inlined,
        white only) that opens straight from disk.
        Local only, not published: it holds internal sales figures.

The page opens on the action list ("מה עושים", Yarin, 24 Oct 2026): filter tiles, a strip of the journey stages (hues
from shared/design/categories.json, set journey-stages), one grouped list per stage with done marks kept in the
viewer's browser. Below it the seven research files sit closed, one lb-disclosure each; a top bar pill or any link
into a file opens it (and opens on load when the URL names it).
How the Markdown becomes a file's section: its # heading the title, ## headings sub-sections (listed under the
title when open, and the first few on the closed row), ### headings sub-heads. Tables become lb-table tables, ```text
blocks become right-to-left Hebrew message drafts, [S-...] citations and source IDs link to their row in Sources,
file names in backticks link to their section, and Hebrew runs are wrapped in <bdi> so they keep their order inside
English text.
Standard library only.
"""
import base64
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIR = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

OUT = DIR / "cro-crm-strategy.html"
TITLE = "CRO and CRM Strategy"
DOCS = [  # (file stem, pill label); "actions" is the Hebrew action list from src/journey-actions.json, open at the top
    ("actions", "מה עושים"),
    ("report", "Summary"),
    ("numbers-2026-10-25", "25 Oct numbers"),
    ("audit", "Audit"),
    ("experiments", "Experiments"),
    ("crm-flows", "CRM flows"),
    ("measurement", "Measurement"),
    ("roadmap", "Roadmap"),
    ("sources", "Sources"),
]
STEMS = {s for s, _ in DOCS if s != "actions"}

# a Hebrew run starts with a Hebrew letter and may hold digits, ₪ and punctuation, so "99 שקלים במקום 149" keeps its order
# (straight double quotes stay outside, so two quoted Hebrew phrases are two runs)
HEB = re.compile(r"[֐-׿][֐-׿0-9₪׳״' ,.?!\-־:·/%()…]*[֐-׿׳״'?!0-9₪)…]|[֐-׿]")
TOKEN = re.compile(r"`([^`]+)`|\*\*(.+?)\*\*|(https?://[^\s<>|]+[^\s<>|.,;:)\]])|\[([A-Z]{1,3}-[a-z0-9][a-z0-9-]*)\]")
SRC_ID = re.compile(r"\b((?:S|L|W|I|E|T|G|O|K|C|V|SMS)-[a-z][a-z0-9-]*)\b")
SOURCE_IDS = set()


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "s"


def plain(t):
    """Escape a plain-text run, link known source IDs, isolate Hebrew."""
    t = html.escape(t, quote=False)
    t = SRC_ID.sub(lambda m: f'<a class="src" href="#src-{m.group(1)}">{m.group(1)}</a>' if m.group(1) in SOURCE_IDS else m.group(0), t)
    # Hebrew isolation only outside the tags just added
    parts = re.split(r"(<[^>]+>)", t)
    return "".join(p if p.startswith("<") else HEB.sub(lambda m: f"<bdi>{m.group(0)}</bdi>", p) for p in parts)


def code(c):
    stem = re.sub(r"^(?:research/cro-crm/)?([a-z0-9-]+)\.md$", r"\1", c)
    if stem in STEMS and c.endswith(".md"):
        return f'<a href="#doc-{stem}"><code>{html.escape(c)}</code></a>'
    return f"<code>{html.escape(c)}</code>"


def inline(s):
    out, i = [], 0
    for m in TOKEN.finditer(s):
        out.append(plain(s[i:m.start()]))
        c, bold, url, cite = m.groups()
        if c is not None:
            out.append(code(c))
        elif bold is not None:
            out.append(f"<b>{inline(bold)}</b>")
        elif url:
            out.append(f'<a href="{html.escape(url)}" target="_blank" rel="noopener" dir="ltr">{html.escape(url)}</a>')
        elif cite:
            out.append(f'<a class="cite" href="#src-{cite}">{cite}</a>' if cite in SOURCE_IDS else f"[{html.escape(cite)}]")
        i = m.end()
    out.append(plain(s[i:]))
    return "".join(out)


def parse(md):
    """Return (title, blocks). A block is (kind, payload): p, h2, h3, ul, ol, table, he (Hebrew draft), pre."""
    title, blocks = "", []
    para, items, rows, kind = [], [], [], None
    fence = None

    def flush():
        nonlocal para, items, rows, kind
        if para:
            blocks.append(("p", " ".join(para)))
        if items:
            blocks.append((kind, items))
        if rows:
            blocks.append(("table", rows))
        para, items, rows, kind = [], [], [], None

    for line in md.splitlines():
        s = line.strip()
        if fence is not None:
            if s.startswith("```"):
                blocks.append(fence)
                fence = None
            else:
                fence[1].append(line)
            continue
        if s.startswith("```"):
            flush()
            fence = ("he" if s[3:].strip() == "text" else "pre", [])
        elif not s:
            flush()
        elif s.startswith("# ") and not title:
            flush(); title = s[2:]
        elif s.startswith("## "):
            flush(); blocks.append(("h2", s[3:]))
        elif s.startswith("### "):
            flush(); blocks.append(("h3", s[4:]))
        elif s.startswith("|"):
            if para or items:
                flush()
            if not re.fullmatch(r"\|[\s:|-]+\|", s):
                rows.append([c.strip() for c in re.split(r"(?<!\\)\|", s.strip().strip("|"))])
        elif re.match(r"\d+\. ", s):
            if kind not in (None, "ol") or para or rows:
                flush()
            kind = "ol"; items.append(re.sub(r"^\d+\. ", "", s))
        elif s.startswith("- "):
            if kind not in (None, "ul") or para or rows:
                flush()
            kind = "ul"; items.append(s[2:])
        else:
            if items or rows:
                flush()
            para.append(s)
    flush()
    return title, blocks


def table(rows, stem):
    head, body = rows[0], rows[1:]
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    trs = []
    seen = set()
    for r in body:
        rid = ""
        if stem == "sources" and r and re.fullmatch(r"[A-Z]{1,3}-[a-z0-9-]+", r[0]) and r[0] not in seen:
            seen.add(r[0]); rid = f' id="src-{r[0]}"'
        trs.append(f"<tr{rid}>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    wide = " wide" if len(head) >= 6 else ""
    return f'<div class="lb-table-wrap"><table class="lb-table top{wide}"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def render(stem, blocks):
    out, toc = [], []
    for kind, val in blocks:
        if kind == "p":
            out.append(f"<p>{inline(val)}</p>")
        elif kind == "h2":
            hid = f"{stem}-{slug(val)}"
            toc.append((hid, val))
            out.append(f'<h3 id="{hid}">{inline(val)}</h3>')
        elif kind == "h3":
            out.append(f'<h4 id="{stem}-{slug(val)}">{inline(val)}</h4>')
        elif kind == "ul":
            out.append('<ul class="lb-bullets">' + "".join(f"<li>{inline(i)}</li>" for i in val) + "</ul>")
        elif kind == "ol":
            out.append('<ol class="list">' + "".join(f"<li>{inline(i)}</li>" for i in val) + "</ol>")
        elif kind == "table":
            out.append(table(val, stem))
        elif kind == "he":
            out.append(f'<pre class="lb-textblock" dir="rtl" lang="he">{html.escape(chr(10).join(val))}</pre>')
        elif kind == "pre":
            out.append(f"<pre>{html.escape(chr(10).join(val))}</pre>")
    return "\n".join(out), toc


# ---------- the action list (Hebrew): src/journey-actions.json, every action in the journey demo ----------
ACTIONS = HERE / "journey-actions.json"
ACT_MEDIA = ROOT / "media" / "projects" / "2026-10-24-cro-crm-actions"  # resized site covers and the book mockup (not in git)
DEMO_PAGE = "journey-demo.html"

# 24px line icons in the design system's tile style (stroke drawn by .lb-tile svg / .acts svg)
ICONS = {
    "megaphone": '<path d="M3 10v4a1 1 0 0 0 1 1h3l6 4V5L7 9H4a1 1 0 0 0-1 1z"/><path d="M16.5 8.5a5 5 0 0 1 0 7"/><path d="M19.5 5.5a9 9 0 0 1 0 13"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
    "wand": '<path d="M4 20 15 9"/><path d="m13 7 4 4"/><path d="M17 3v3M15.5 4.5h3M20 8v2M19 9h2M9 4v2M8 5h2"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2.5"/><path d="M2 10h20M6 15h4"/>',
    "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C10 3 12 8 12 8s2-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8 9h8M8 13h5"/>',
    "list": '<path d="M9 6h12M9 12h12M9 18h12"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "question": '<circle cx="12" cy="12" r="9.5"/><path d="M9.2 9.2a3 3 0 0 1 5.7 1.1c0 2-2.9 2.6-2.9 4.2"/><path d="M12 17.6h.01"/>',
    "scale": '<path d="M12 3v18M8 21h8M4 7h16"/><path d="m7 7-3 7a3 3 0 0 0 6 0zM17 7l-3 7a3 3 0 0 0 6 0z"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 16.5v-5M12 8h.01"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "chevron": '<path d="m15 18-6-6 6-6"/>',
    "arrow": '<path d="M17 7 7 17M16 17H7V8"/>',
    "seal": '<path d="M12 2.5 14.6 5l3.6-.4.4 3.6L21.5 12l-2.9 3.8-.4 3.6-3.6-.4L12 21.5 9.4 19l-3.6.4-.4-3.6L2.5 12l2.9-3.8.4-3.6 3.6.4z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
}
KINDS = {"fix": ("לתקן", "success"), "test": ("לבדוק", "info"), "decide": ("החלטה", "warning"), "legal": ("עורך דין", "danger")}
WHO = {"me": "אני", "yossi": "יוסי", "lawyer": "עורך דין"}
# the smart-list tiles at the top: (filter, label, icon, colour token)
TILES = [("all", "הכל", "list", "var(--text)"), ("me", "אצלי", "person", "var(--tint)"), ("yossi", "אצל יוסי", "wrench", "var(--accent-ink)"),
         ("decide", "מחכה להחלטה", "question", "var(--warning)"), ("legal", "לעורך דין", "scale", "var(--danger)")]


def svg(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def act_img(name):
    """A media file as a data: URI, or None when it is not on this disk (the build then leaves the picture out)."""
    path = ACT_MEDIA / name
    if not path.exists():
        return None
    return "data:image/webp;base64," + base64.b64encode(path.read_bytes()).decode()


def he(t):
    """Escape Hebrew text; isolate Latin runs (event names, ₪ amounts stay put) so they keep their order."""
    t = html.escape(t, quote=False)
    return re.sub(r"[A-Za-z][A-Za-z0-9_./:@-]*(?: [A-Za-z][A-Za-z0-9_./:@-]*)*", lambda m: f'<bdi dir="ltr">{m.group(0)}</bdi>', t)


def item_filters(it):
    f = ["all"]
    if "me" in it["who"]:
        f.append("me")
    if "yossi" in it["who"] and it["kind"] in ("fix", "test"):
        f.append("yossi")
    if it["kind"] in ("decide", "legal"):
        f.append(it["kind"])
    return f


def act_item(it):
    step, note = it["demo"]
    label, tone = KINDS[it["kind"]]
    who = [WHO[w] for w in it["who"] if not (it["kind"] == "legal" and w == "lawyer")]
    prio = it.get("prio")
    badge = ""
    if prio is not None:
        badge = (f'<span class="lb-disc sm" title="לפני הכל">★</span>' if prio == 0
                 else f'<span class="lb-disc sm" title="עדיפות {prio} מתוך 5">{prio}</span>')
    rows = [("היום", it.get("today")), ("מה בדיוק", it.get("detail")), ("איך נדע שעבד", it.get("measure"))]
    dl = "".join(f"<dt>{k}</dt><dd>{he(v)}</dd>" for k, v in rows if v)
    pic = act_img(it["img"]) if it.get("img") else None
    who_html = f'<span>{" · ".join(who)}</span>' if who else ""
    thumb = f'<img class="acts-thumb" src="{pic}" alt="{html.escape(it.get("img_alt", ""))}" width="88" height="88" loading="lazy">' if pic else ""
    return (f'<details class="lb-rowitem" id="act-{it["id"].replace(".", "-")}" data-id="{it["id"]}" data-f="{" ".join(item_filters(it))}">'
            f'<summary>'
            f'<button type="button" class="acts-check" aria-pressed="false" aria-label="סימון: בוצע">{svg("check")}</button>'
            f'<span class="lb-rowitem-title"><span>{he(it["title"])}</span><small>{he(it["why"])}</small></span>'
            f'<span class="lb-rowitem-meta">{badge}<span class="lb-chip {tone}">{label}</span>'
            f'{who_html}</span>'
            f'</summary>'
            f'<div class="lb-rowitem-body acts-more">{thumb}<dl class="lb-kv stack">{dl}</dl>'
            f'<a class="acts-demo-link" href="{DEMO_PAGE}#step-{step}">{svg("arrow")}בדמו: שלב {step}, הערה {note}, עם המקורות</a></div>'
            f'</details>')


def act_visual(kind, stage):
    if kind == "ad":
        pic = act_img("cover-birthday-girl.webp")
        media = (f'<div class="lb-media-frame is-1x1"><img src="{pic}" alt="הכריכה של ספר יום ההולדת מהאתר" width="240" height="240" loading="lazy"></div>'
                 if pic else "")
        return (f'<figure class="acts-visual"><div class="lb-post acts-ad"><div class="lb-post-head"><img class="lb-post-avatar" src="{design.logo_data_uri()}" alt="" width="28" height="28">'
                f'<span class="lb-post-name"><b dir="ltr">LumeBook</b><small>ממומן</small></span></div><p class="lb-post-text">ספר יום הולדת שהילד שלכם הוא הגיבור שלו 🎂</p>{media}'
                f'<div class="acts-ad-link"><small dir="ltr">LUMEBOOK.COM</small><b>יום הולדת · ספר אישי</b><span>₪119 ועוד ₪30 משלוח</span></div></div>'
                f'<figcaption>הכריכה מהאתר, המודעה להמחשה</figcaption></figure>')
    if kind == "price":
        return ('<figure class="acts-visual"><div class="acts-price"><b>₪119</b><span>ועוד ₪30 משלוח עד הבית · איסוף חינם בירושלים</span>'
                '<span class="acts-eta">📦 מאשרים היום? מגיע עד <b data-eta="7">תאריך</b></span>'
                '<span class="acts-eta">🕎 לחנוכה מזמינים עד <b>22.11</b> <small>(לא מאושר)</small></span></div>'
                '<figcaption>ככה המחיר צריך להיראות בדף הספר</figcaption></figure>')
    if kind == "funnel":
        bars = [("תצוגות מקדימות", 527, 100), ("הגיעו לתשלום", 202, 38.3), ("שילמו", 85, 16.1)]
        rows = "".join(f'<div class="acts-bar"><span>{l}</span><b>{v}</b><i style="--w:{p}%"></i></div>' for l, v, p in bars)
        return f'<figure class="acts-visual"><div class="acts-funnel">{rows}</div><figcaption>30 יום עד 12.10, לפי Mixpanel</figcaption></figure>'
    return ""


def actions_section():
    data = json.loads(ACTIONS.read_text(encoding="utf-8"))
    stages_meta = design.categories("journey-stages")
    items = [it for st in data["stages"] for g in st["groups"] for it in g["items"]]
    counts = {f: sum(f in item_filters(it) for it in items) for f, *_ in TILES}

    tiles = "".join(f'<button type="button" class="acts-tile" data-filter="{f}" aria-pressed="{str(f == "all").lower()}" style="--c:{c}">'
                    f'<span class="acts-tile-ic">{svg(ic)}</span><b class="acts-tile-n">{counts[f]}</b><span class="acts-tile-l">{lbl}</span></button>'
                    for f, lbl, ic, c in TILES)
    strip, stages = [], []
    for st in data["stages"]:
        meta = stages_meta[st["key"]]
        cat = f'lb-cat-{meta["cat"]}'
        n = sum(len(g["items"]) for g in st["groups"])
        steps = st["steps"]
        steps_txt = f"שלב {steps[0]}" if len(steps) == 1 else f"שלבים {steps[0]} עד {steps[-1]}"
        strip.append(f'<a class="acts-chip {cat}" href="#act-stage-{st["key"]}" data-stage="{st["key"]}"><span class="lb-tile">{svg(st["icon"])}</span>'
                     f'<span>{meta["label"]}</span><span class="lb-count">{n}</span></a>')
        note = f'<p class="acts-note">{svg("info")}<span>{he(st["note"])}</span></p>' if st.get("note") else ""
        visual = act_visual(st.get("visual"), st)
        ctx = f'<div class="acts-context{" has-visual" if visual else ""}">{note}{visual}</div>' if (note or visual) else ""
        groups = []
        for g in st["groups"]:
            head = (f'<h4>{g["title"]}<a href="{DEMO_PAGE}#step-{g["step"]}">שלב {g["step"]} בדמו</a></h4>' if g.get("title") else "")
            keep = ""
            if g.get("keep"):
                keep_items = "".join("<li>" + he(x) + "</li>" for x in g["keep"])
                keep = (f'<details class="acts-keep"><summary>{svg("seal")}עובד היום, לא לגעת · {len(g["keep"])}</summary>'
                        f'<ul class="lb-bullets">{keep_items}</ul></details>')
            groups.append(f'<div class="acts-group">{head}<div class="lb-rowlist">{"".join(act_item(it) for it in g["items"])}</div>{keep}</div>')
        stages.append(f'<section class="acts-stage lb-topic {cat}" id="act-stage-{st["key"]}" data-stage="{st["key"]}">'
                      f'<header class="lb-topic-head"><span class="lb-tile lg">{svg(st["icon"])}</span>'
                      f'<div class="lb-topic-text"><h3 class="lb-topic-title">{meta["label"]}<span class="lb-topic-n">{n} פעולות</span></h3>'
                      f'<p class="lb-topic-desc">{steps_txt} בדמו</p></div>'
                      f'<a class="lb-btn secondary sm" href="{DEMO_PAGE}#step-{steps[0]}">לראות בדמו</a></header>'
                      f'{ctx}{"".join(groups)}</section>')

    legend = "".join(f'<span class="lb-chip {tone}">{lbl}</span>' for lbl, tone in KINDS.values())
    hero_img = act_img(data["hero_image"]["file"])
    hero_pic = (f'<img class="acts-hero-img" src="{hero_img}" alt="{html.escape(data["hero_image"]["alt"])}" width="280" height="280">' if hero_img else "")
    return f"""<section class="doc acts" id="doc-actions" dir="rtl" lang="he">
<div class="lb-hero has-media"><div class="lb-hero-text"><div class="lb-row"><span class="lb-eyebrow">מה עושים · 24.10.2026</span><span class="lb-chip warning">פנימי: יש כאן נתוני מכירות</span></div><h1>{he(data["title"])}</h1>
<p class="lb-lede">{he(data["lede"])}</p>
<div class="lb-row"><a class="lb-btn" href="{DEMO_PAGE}#step-1">לפתוח את הדמו</a><span class="acts-legend">{legend}</span></div></div>{hero_pic}</div>
<div class="acts-tiles" role="group" aria-label="סינון לפי מי ומה">{tiles}</div>
<div class="acts-bar-row lb-edge"><nav class="lb-scroller" style="--item: max-content" aria-label="שלבי המסע">{"".join(strip)}</nav>
<div class="acts-progress"><span><span id="acts-done-n">0</span> מתוך {len(items)} סומנו</span><label><input type="checkbox" id="acts-hide-done"> להסתיר מה שסימנתי</label></div></div>
{"".join(stages)}
<p class="acts-empty" hidden>אין כאן כלום בסינון הזה.</p>
<p class="lb-note">המקור: <code dir="ltr">research/cro-crm/src/journey-actions.json</code>, שורה לכל הערה בדמו שמבקשת משהו. הסימונים נשמרים רק בדפדפן הזה. הכריכות מ-lumebook.com, הספר המודפס מהמוקאפ של ספר היום הולדת של הילה.</p>
</section>"""


ACTS_STYLE = """<style>
/* The action list (Hebrew, right to left): smart-list tiles that filter, a strip of the seven journey stages (lb-scroller),
   then one lb-topic per stage (lb-topic-head, grouped lb-rowlist rows). Stage hues come from categories.json
   (journey-stages) through lb-cat-N; status keeps its chips. Hero is lb-hero has-media, the ad sketch an lb-post, the
   priority an lb-disc, the details an lb-kv. Page rules below are only what those leave to the page.
   Check circles take the stage hue, like a list colour in Reminders (a round button, so it works inside the row's summary). */
.acts { display: grid; gap: var(--sp-5); }
.acts-legend { display: inline-flex; flex-wrap: wrap; gap: var(--sp-1); margin-inline-start: var(--sp-2); }
.acts-hero-img { width: 100%; max-width: 16rem; height: auto; justify-self: center; border-radius: var(--r-lg); box-shadow: var(--shadow-3); border: 1px solid var(--line); }
@media (max-width: 760px) { .acts-hero-img { max-width: 13rem; } }

.acts-tiles { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 8.75rem), 1fr)); }
.acts-tile { appearance: none; font: inherit; text-align: start; cursor: pointer; display: grid; grid-template-columns: auto 1fr; align-items: center; gap: var(--sp-2) var(--sp-3);
  padding: var(--sp-3) var(--sp-4); border-radius: var(--r-lg); background: var(--surface-2); border: 1px solid var(--line); color: var(--text); transition: background .15s, transform .15s; }
.acts-tile:hover { background: var(--fill-2); }
.acts-tile:active { transform: scale(.98); }
.acts-tile:focus-visible, .acts-check:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
.acts-tile-ic { width: 2.1rem; height: 2.1rem; border-radius: 50%; display: grid; place-items: center; background: var(--c); color: var(--bg); }
.acts-tile-n { justify-self: end; font-size: var(--fs-num); font-weight: 700; line-height: 1; font-variant-numeric: tabular-nums; }
.acts-tile-l { grid-column: 1 / -1; font-family: var(--font-2); font-weight: 700; font-size: var(--fs-callout); color: var(--text-2); }
.acts-tile[aria-pressed="true"] { background: var(--c); border-color: transparent; color: var(--bg); }
.acts-tile[aria-pressed="true"] .acts-tile-l { color: var(--bg); }
.acts-tile[aria-pressed="true"] .acts-tile-ic { background: var(--bg); color: var(--c); }
.acts svg { width: 1.1rem; height: 1.1rem; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; flex: none; }
.acts-tile-ic svg { width: 1.15rem; height: 1.15rem; stroke-width: 2.2; }

.acts-bar-row { position: sticky; top: calc(max(env(safe-area-inset-top, 0px), var(--lb-gnav-top, 0px)) + 3.5rem); z-index: 5; display: grid; gap: var(--sp-2); padding: var(--sp-2) 0; }
@media (max-width: 980px) { .acts-bar-row { position: static; } .acts-bar-row::before, .acts-bar-row::after { display: none; } }
.acts-chip { display: inline-flex; align-items: center; gap: var(--sp-2); padding: .3rem .4rem .3rem .7rem; border-radius: var(--r-pill); background: var(--surface); border: 1px solid var(--line);
  color: var(--text); font-weight: 600; font-size: var(--fs-callout); text-decoration: none; white-space: nowrap; }
.acts-chip:hover { border-color: var(--tc); text-decoration: none; color: var(--text); }
.acts-chip .lb-tile { width: 1.5rem; height: 1.5rem; border-radius: 50%; }
.acts-chip .lb-tile svg { width: .85rem; height: .85rem; }
.acts-chip.is-empty { opacity: .4; }
.acts-progress { display: flex; flex-wrap: wrap; gap: var(--sp-2) var(--sp-4); align-items: center; font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }
.acts-progress label { display: inline-flex; align-items: center; gap: var(--sp-2); cursor: pointer; color: var(--text-2); }
.acts-progress input { accent-color: var(--tint); }

.acts-stage { scroll-margin-top: 9rem; padding-top: var(--sp-4); }
.acts-context { display: grid; gap: var(--sp-4); align-items: start; }
.acts-context.has-visual { grid-template-columns: minmax(0, 1fr) auto; }
@media (max-width: 640px) { .acts-context.has-visual { grid-template-columns: minmax(0, 1fr); } }
.acts-note { display: flex; gap: var(--sp-2); align-items: flex-start; margin: 0; padding: var(--sp-3) var(--sp-4); border-radius: var(--r-md); background: var(--tc-soft); color: var(--text); font-size: var(--fs-callout); line-height: 1.5; max-width: 40rem; }
.acts-note svg { color: var(--tc-ink); margin-top: .15rem; }
.acts-visual { margin: 0; display: grid; gap: var(--sp-1); justify-items: center; }
.acts-visual figcaption { font-family: var(--font-2); font-size: var(--fs-caption); color: var(--text-3); }
.acts-ad { width: 15rem; box-shadow: var(--shadow-2); }
.acts-ad-link { display: grid; gap: 1px; padding: var(--sp-2) var(--sp-3); border-radius: var(--r-sm); background: var(--glass-sheen), color-mix(in srgb, var(--surface-2) 72%, transparent); box-shadow: var(--glass-card-rim-sm); font-size: var(--fs-footnote); }
.acts-ad-link small { color: var(--text-3); font-size: var(--fs-caption); text-align: end; }
.acts-price { width: 15rem; display: grid; gap: var(--sp-1); padding: var(--sp-4); border-radius: var(--r-lg); background: var(--glass-sheen), var(--glass-card); border: 1px solid transparent; box-shadow: var(--glass-card-rim), var(--shadow-2); font-size: var(--fs-footnote); color: var(--text-2); }
.acts-price > b { font-size: 2rem; line-height: 1; color: var(--tc-ink); font-weight: 800; }
.acts-eta { color: var(--text); }
.acts-eta small { color: var(--text-3); }
.acts-funnel { width: 15rem; display: grid; gap: var(--sp-2); padding: var(--sp-4); border-radius: var(--r-lg); background: var(--glass-sheen), var(--glass-card); border: 1px solid transparent; box-shadow: var(--glass-card-rim), var(--glass-card-lift); }
.acts-bar { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 2px var(--sp-2); font-size: var(--fs-footnote); }
.acts-bar b { font-variant-numeric: tabular-nums; }
.acts-bar i { grid-column: 1 / -1; height: .5rem; border-radius: var(--r-pill); background: linear-gradient(90deg, var(--tc) var(--w), var(--fill-2) var(--w)); }
[dir="rtl"] .acts-bar i { background: linear-gradient(270deg, var(--tc) var(--w), var(--fill-2) var(--w)); }

.acts-group { display: grid; gap: var(--sp-2); }
.acts-group h4 { display: flex; gap: var(--sp-2); align-items: baseline; font-size: var(--fs-callout); font-family: var(--font-2); font-weight: 700; color: var(--text-3); margin: var(--sp-2) var(--sp-4) 0; }
.acts-group h4 a { font-weight: 600; font-size: var(--fs-caption); }
.acts-check { appearance: none; width: 1.45rem; height: 1.45rem; border-radius: 50%; border: 2px solid var(--tc); background: transparent; color: var(--text-on-tint); display: grid; place-items: center; padding: 0; cursor: pointer; }
.acts-check svg { width: .85rem; height: .85rem; stroke-width: 3; opacity: 0; }
.acts-check[aria-pressed="true"] { background: var(--tc); }
.acts-check[aria-pressed="true"] svg { opacity: 1; }
.acts .lb-rowitem-meta { display: inline-flex; align-items: center; gap: var(--sp-2); }
.acts-more { grid-template-columns: minmax(0, 1fr) auto; column-gap: var(--sp-4); }
.acts-more .lb-kv { margin: 0; }
.acts-thumb { grid-column: 2; grid-row: 1 / span 2; width: 5.5rem; height: 5.5rem; border-radius: var(--r-md); object-fit: cover; box-shadow: var(--shadow-2); }
.acts-demo-link { grid-column: 1; display: inline-flex; align-items: center; gap: var(--sp-1); font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; justify-self: start; }
.acts-demo-link svg { width: .9rem; height: .9rem; transform: scaleX(-1); }
@media (max-width: 640px) { .acts-more { grid-template-columns: minmax(0, 1fr); } .acts-thumb { grid-column: 1; grid-row: auto; } }
.acts-keep { margin: 0 var(--sp-4); font-size: var(--fs-footnote); color: var(--text-3); }
.acts-keep summary { display: inline-flex; align-items: center; gap: var(--sp-1); cursor: pointer; font-family: var(--font-2); font-weight: 700; }
.acts-keep summary svg { color: var(--success); }
.acts-keep .lb-bullets { margin-top: var(--sp-2); color: var(--text-2); }
.acts-empty { color: var(--text-3); font-family: var(--font-2); }
@media (prefers-reduced-motion: reduce) { .acts-tile { transition: none; } }
</style>"""

ACTS_JS = """<script>
/* The action list: filter tiles, done marks (kept in this browser only), the hide-done switch and the arrival date. */
(function () {
  var root = document.getElementById("doc-actions");
  if (!root) return;
  var KEY = "lb-cro-actions-done", done = {}, filter = "all";
  try { JSON.parse(localStorage.getItem(KEY) || "[]").forEach(function (id) { done[id] = 1; }); } catch (e) { /* no storage */ }
  var items = [].slice.call(root.querySelectorAll(".lb-rowitem"));
  var hide = root.querySelector("#acts-hide-done");
  function save() { try { localStorage.setItem(KEY, JSON.stringify(Object.keys(done))); } catch (e) { /* no storage */ } }
  function apply() {
    items.forEach(function (li) {
      var on = !!done[li.dataset.id];
      li.classList.toggle("is-done", on);
      li.querySelector(".acts-check").setAttribute("aria-pressed", on ? "true" : "false");
      li.hidden = li.dataset.f.split(" ").indexOf(filter) < 0 || (hide.checked && on);
    });
    var any = false;
    [].slice.call(root.querySelectorAll(".acts-group")).forEach(function (g) {
      var n = g.querySelectorAll(".lb-rowitem:not([hidden])").length;
      g.hidden = !n;
      var keep = g.querySelector(".acts-keep"); if (keep) keep.hidden = filter !== "all";
    });
    [].slice.call(root.querySelectorAll(".acts-stage")).forEach(function (s) {
      var n = s.querySelectorAll(".lb-rowitem:not([hidden])").length;
      s.hidden = !n; any = any || n > 0;
      var chip = root.querySelector('.acts-chip[data-stage="' + s.dataset.stage + '"]');
      if (chip) { chip.querySelector(".lb-count").textContent = n; chip.classList.toggle("is-empty", !n); }
    });
    root.querySelector(".acts-empty").hidden = any;
    root.querySelector("#acts-done-n").textContent = Object.keys(done).filter(function (id) { return root.querySelector('.lb-rowitem[data-id="' + id + '"]'); }).length;
  }
  root.addEventListener("click", function (e) {
    var c = e.target.closest(".acts-check");
    if (c) {
      e.preventDefault(); e.stopPropagation();
      var id = c.closest(".lb-rowitem").dataset.id;
      if (done[id]) delete done[id]; else done[id] = 1;
      save(); apply(); return;
    }
    var t = e.target.closest(".acts-tile");
    if (t) {
      filter = t.dataset.filter;
      [].slice.call(root.querySelectorAll(".acts-tile")).forEach(function (b) { b.setAttribute("aria-pressed", b === t ? "true" : "false"); });
      apply();
    }
  });
  hide.addEventListener("change", apply);
  /* arrival date on the price sketch: today plus N business days (Sunday to Thursday), no holidays */
  var DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"];
  [].slice.call(root.querySelectorAll("[data-eta]")).forEach(function (el) {
    var d = new Date(), k = 0, n = +el.dataset.eta;
    while (k < n) { d.setDate(d.getDate() + 1); if (d.getDay() !== 5 && d.getDay() !== 6) k++; }
    el.textContent = "יום " + DAYS[d.getDay()] + " " + d.getDate() + "." + (d.getMonth() + 1);
  });
  apply();
})();
</script>"""


STYLE = """<style>
/* Layout: the action list open at the top, then the seven research files as closed disclosures. Top bar (lb-topbar has-toc,
   lb-brand is-stacked) pills per section (scroll-tracked) open the one they name. Lists are ul.lb-bullets, tables
   lb-table top (wide for six columns or more), Hebrew drafts lb-textblock. Page rules use design tokens only. */
:root { --read-w: 74ch; }
.lb-topbar .lb-toc { flex: 1 1 0; } /* the pills shrink first, so the brand keeps its full name beside them */
.doc { min-width: 0; }
.research { display: grid; gap: var(--sp-4); padding-top: var(--sp-6); border-top: 1px solid var(--line); }
.research-head { display: grid; gap: var(--sp-2); }
.research-head h2 { font-size: var(--fs-title); }
.research-head p { max-width: var(--read-w); color: var(--text-2); text-wrap: pretty; }
.research-head .lb-row { gap: var(--sp-2); }
.doc > summary { padding: var(--sp-4) var(--sp-5); }
.doc > summary h2 { font-size: var(--fs-headline); line-height: 1.3; margin: 0; }
.doc > summary small { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.doc-body { gap: var(--sp-4); padding: var(--sp-5); }
.doc-toc { display: flex; flex-wrap: wrap; gap: var(--sp-1) var(--sp-2); }
.doc-toc a { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-2); background: var(--fill); border-radius: var(--r-pill); padding: .25rem .65rem; text-decoration: none; }
.doc-toc a:hover { background: var(--tint-soft); color: var(--tint); text-decoration: none; }
.doc-body h3 { font-size: var(--fs-title); margin-top: var(--sp-4); }
.doc-body h4 { font-size: var(--fs-headline); margin-top: var(--sp-2); }
.doc-body > p, .doc-body > ul, .doc-body > ol { max-width: var(--read-w); color: var(--text-2); }
.doc-body > p { text-wrap: pretty; }
.doc-body > p b, .doc-body li b { color: var(--text); }
@media (max-width: 640px) { .doc > summary { padding: var(--sp-3) var(--sp-4); } .doc-body { padding: var(--sp-4); } }
ol.list { margin: 0; padding-inline-start: 1.3rem; display: grid; gap: var(--sp-2); }
ol.list li::marker { color: var(--accent-ink); font-weight: 700; font-family: var(--font-2); }
.lb-table td { min-width: 7rem; }
.lb-table td:first-child { min-width: 4rem; }
.lb-table th { white-space: normal; }
.doc-body > .lb-textblock { max-width: 28rem; }
code { overflow-wrap: anywhere; }
a.cite, a.src { font-family: var(--font-2); font-size: .85em; font-weight: 700; white-space: nowrap; }
bdi { unicode-bidi: isolate; }
main p, main li, .lb-table td { overflow-wrap: anywhere; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
</style>"""

SPY_JS = """<script>
/* In-page links scroll instead of navigating: the desktop app's file preview loads the page as a data: URL, where
   following a link, even "#doc-audit", is blocked. A link into a closed research file or action row opens it first, and
   the row or source line it lands on flashes (lb-flash). */
function go(el, smooth) {
  if (el.hidden || (el.closest && el.closest("[hidden]"))) { var all = document.querySelector('.acts-tile[data-filter="all"]'), hd = document.getElementById("acts-hide-done"); if (hd && hd.checked) { hd.checked = false; hd.dispatchEvent(new Event("change")); } if (all) all.click(); }
  for (var p = el; p; p = p.parentElement) if (p.tagName === "DETAILS") p.open = true;
  el.scrollIntoView({ behavior: smooth && !matchMedia("(prefers-reduced-motion: reduce)").matches ? "smooth" : "auto", block: "start" });
  if (el.tagName === "TR" || el.classList.contains("lb-rowitem")) { el.classList.remove("lb-flash"); void el.offsetWidth; el.classList.add("lb-flash"); setTimeout(function () { el.classList.remove("lb-flash"); }, 1800); }
}
document.addEventListener("click", function (e) {
  var a = e.target.closest && e.target.closest('a[href^="#"]');
  if (!a) return;
  var el = document.getElementById(a.getAttribute("href").slice(1));
  if (!el) return;
  e.preventDefault();
  go(el, true);
});
(function () {
  var id = location.hash.slice(1), el = id && document.getElementById(decodeURIComponent(id));
  if (el) go(el, false);
})();
(function () {
  var pills = [].slice.call(document.querySelectorAll(".lb-toc a"));
  var map = {}; pills.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
  if (!("IntersectionObserver" in window)) return;
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      pills.forEach(function (a) { a.removeAttribute("aria-current"); });
      var a = map[e.target.id]; if (a) { a.setAttribute("aria-current", "true"); a.scrollIntoView({ block: "nearest", inline: "nearest" }); }
    });
  }, { rootMargin: "-30% 0px -60% 0px" });
  document.querySelectorAll(".doc").forEach(function (s) { io.observe(s); });
})();
</script>"""


def build():
    texts = {stem: (DIR / f"{stem}.md").read_text(encoding="utf-8") for stem in STEMS}
    SOURCE_IDS.update(re.findall(r"^\| ([A-Z]{1,3}-[a-z0-9-]+) \|", texts["sources"], re.M))
    pills, files = [], []
    for stem, label in DOCS:
        if stem == "actions":
            pills.append(f'<a href="#doc-actions" lang="he">{label}</a>')
            continue
        title, blocks = parse(texts[stem])
        body, toc = render(stem, blocks)
        pills.append(f'<a href="#doc-{stem}">{label}</a>')
        toc_html = "".join(f'<a href="#{hid}">{inline(t)}</a>' for hid, t in toc)
        peek = " · ".join(inline(t) for _, t in toc[:4]) + (" …" if len(toc) > 4 else "")
        files.append(f'<details class="lb-disclosure doc" id="doc-{stem}">\n<summary><span class="lb-sum"><h2>{inline(title)}</h2>'
                     f'<small><code>{stem}.md</code>{" · " + peek if peek else ""}</small></span></summary>\n'
                     f'<div class="lb-disclosure-body doc-body">{f"<nav class=doc-toc aria-label=Contents>{toc_html}</nav>" if toc_html else ""}\n{body}\n</div></details>')
    research = f"""<section class="research" id="research" aria-labelledby="research-h">
<header class="research-head">
<div class="lb-row"><span class="lb-chip warning">Internal: holds sales figures</span><span class="lb-chip outline">24 Oct 2026</span><span class="lb-chip outline">Research and planning only</span></div>
<h2 id="research-h">The research behind the list</h2>
<p>What would most likely increase profitable purchases, recover lost buyers and bring repeat orders, based on a walk through lumebook.com, the store's public code, a competitor review and the research in {code("sources.md")}. Nothing on the site or in the store's messages was changed. Each file opens when you need it: click its row, its pill in the top bar or any link that points into it.</p>
</header>
<div class="lb-disclosures">
{chr(10).join(files)}
</div>
</section>"""
    page = f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="robots" content="noindex, nofollow">
{design.head()}
{STYLE}
{ACTS_STYLE}
</head>
<body>
<header class="lb-topbar has-toc">
  <div class="lb-topbar-in">
    <a class="lb-brand is-stacked" href="#doc-actions"><img src="{design.logo_data_uri()}" alt="" width="28" height="28"><span><small>LumeBook · internal</small><b>CRO and CRM strategy</b></span></a>
    <nav class="lb-toc" aria-label="Sections">{"".join(pills)}</nav>
  </div>
</header>
<main class="lb-page" dir="ltr" lang="en">
{actions_section()}
{research}
<p class="lb-note">Built from <code>research/cro-crm/*.md</code> by <code>research/cro-crm/src/build_strategy_page.py</code>. Edit the Markdown, then rebuild. Not legal advice: the legal points are summaries for a lawyer.</p>
</main>
{SPY_JS}
{ACTS_JS}
</body>
</html>
"""
    if "—" in page:
        raise SystemExit("em dash in the page; fix the Markdown")
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page) // 1024} KB, action list + {len(files)} research files, {len(SOURCE_IDS)} source IDs)")


if __name__ == "__main__":
    build()
