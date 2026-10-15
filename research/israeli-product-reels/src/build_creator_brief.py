#!/usr/bin/env python3
"""Build the creator brief page from creator-brief.md.

    python3 research/israeli-product-reels/src/build_creator_brief.py

Input:  research/israeli-product-reels/creator-brief.md, only its Hebrew part (the <div dir="rtl"> blocks,
        read with the same parser as lint_creator_brief.py, so the page shows exactly the linted text)
Output: research/israeli-product-reels/creator-brief.html, an artifact page (a fragment, as artifacts want), and
        sites/lumebook-creator-brief/index.html, the same page as a full document for Vercel (noindex). It is styled with the LumeBook design
        styled with the LumeBook design system (design.head() inlined, Heebo only, page rules use tokens only)

How blocks become the page: the first ### heading is the hero, every other ### heading a section.
A block that starts with **name · A עד B שניות** is a shot step (the time strip is drawn from these),
a block that starts with למשל is an example for the step before it, a list item whose first line is bold
is a beat of the worked example, one whose first line is a quote (״...״) a worry card, other list items
do-not rules, "- [ ]" items a checklist, and the data-lint="cta" / "caption" blocks get a copy button.
Render hints are HTML comments in the Markdown: <!--icon:NAME--> (ICONS below), <!--as:ticks--> on a
paragraph, and <!--visual:screens|topic|email--> as its own block. Edit the brief, then rebuild; never
edit the HTML. Standard library only.
"""
import base64
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402
from lint_creator_brief import BRIEF, DIV_RE, blocks  # noqa: E402

OUT = HERE.parent / "creator-brief.html"
SITE = ROOT / "sites" / "lumebook-creator-brief" / "index.html"  # standalone copy for Vercel
TITLE = "בריף הרילס של לומבוק"
MASCOT = ROOT / "shared" / "brand" / "mascot_3d_transparent_320.png"
FONTS = "https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&display=swap"

# Hebrew the page adds around the brief's own text (linted by lint_creator_brief.py too)
UI = {
    "brand": "לומבוק",
    "brand_sub": "בריף ליוצרים",
    "og_description": "שלד צילום ודוגמה מלאה לרילס על הספר האישי שלכם",
    "toc": "בעמוד הזה",
    "meta_parts": "{n} חלקים",
    "meta_secs": "בערך {t} שניות",
    "meta_collab": "שותף לפוסט",
    "copy": "העתקה",
    "copied": "הועתק",
    "copy_fallback": "הטקסט מסומן\nאפשר להעתיק",
    "watch": "לצפייה",
    "checked_of": "מתוך",
    "reset": "ניקוי הסימונים",
    "seconds": "שניות",
    "strip_label": "{n} חלקים לאורך {t} שניות",
    "beat_see": "רואים",
    "beat_say": "אומרים",
    "screens_title": "איפה כל דבר יושב על המסך",
    "screen_open": "פתיחה",
    "screen_rec": "הקלטת מסך",
    "screen_end": "סוף",
    "zone_hook": "טקסט הפתיחה",
    "zone_book": "הספר",
    "zone_subs": "כתוביות",
    "zone_ui": "אינסטגרם מכסה כאן",
    "zone_site": "האתר",
    "topic_hook": "פתיחה",
    "topic_video": "סרטון",
    "topic_caption": "כיתוב",
    "topic_same": "גמילה",
    "topic_other": "יום הולדת",
    "topic_yes": "כן",
    "topic_no": "לא",
    "caption_you": "השם שלכם",
    "caption_and": "ו-",
}

# 24 x 24 stroke icons (currentColor)
ICONS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    "film": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    "clapper": '<path d="M4 10h16v9a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/><path d="m4 10-.6-3.4a1 1 0 0 1 .8-1.2l13-2.3a1 1 0 0 1 1.2.8L19 7 4 10z"/><path d="m8.5 5.6 2.6 3.2M13.5 4.7l2.6 3.2"/>',
    "play": '<circle cx="12" cy="12" r="9"/><path d="M10 8.5v7l6-3.5z"/>',
    "home": '<path d="m3 11 9-7 9 7"/><path d="M5 9.5V20h5v-6h4v6h5V9.5"/>',
    "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M11 18.5h2"/>',
    "book": '<path d="M3 5.5c2.5-1 5.5-1 9 1 3.5-2 6.5-2 9-1v13c-2.5-1-5.5-1-9 1-3.5-2-6.5-2-9-1z"/><path d="M12 6.5v13"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.4a2.5 2.5 0 1 1 3.4 2.4c-.6.3-1 .9-1 1.6v.4"/><path d="M12 17h.01"/>',
    "megaphone": '<path d="M3 10v4a1 1 0 0 0 1 1h3l6 4V5L7 9H4a1 1 0 0 0-1 1z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/>',
    "captions": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 12h4M13 12h4M7 15.5h10"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
    "truck": '<path d="M3 6h11v10H3z"/><path d="M14 9h4l3 3v4h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    "package": '<path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5z"/><path d="m3 7.5 9 4.5 9-4.5M12 12v9"/>',
    "message": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.2a5 5 0 0 1 5.5 5.8"/>',
    "alert": '<path d="M12 4 2.5 20h19z"/><path d="M12 10v4M12 17h.01"/>',
    "quote": '<path d="M5 7h5v5c0 3-1.6 4.8-4.5 5.5M14 7h5v5c0 3-1.6 4.8-4.5 5.5"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
    "external": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "user": '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/>',
}

STEP_RE = re.compile(r"^\*\*(.+?) · (\d+) עד (\d+) שניות\*\*")
HINT_RE = re.compile(r"<!--\s*(\w+):([\w-]+)\s*-->")


def icon(name, cls="ico"):
    body = ICONS.get(name or "")
    if not body:
        return ""
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


# ---------- inline markdown ----------

def inline(text):
    """Escape, then bold, `handles` and [links](url)."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`([^`]+)`", r'<bdi class="handle" dir="ltr">\1</bdi>', out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                 lambda m: f'<a class="extlink" href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}{icon("external")}</a>', out)
    return out


def lines_of(block):
    """A raw block as rendered lines (markdown list and quote markers removed, <br> = line break)."""
    text = []
    for line in block.splitlines():
        line = re.sub(r"^\s*(?:>\s?|#+\s+|-\s+\[ \]\s+|-\s+)", "", line).strip()
        if line:
            text.append(line)
    return [part.strip() for part in re.split(r"<br>", " ".join(text)) if part.strip()]


def plain(lines):
    return "\n".join(re.sub(r"`([^`]+)`", r"\1", l) for l in lines)


def br(lines):
    return "<br>".join(inline(l) for l in lines)


def unquote(line):
    return line.strip().strip("״").strip()


# ---------- parse ----------

def parse():
    md = BRIEF.read_text(encoding="utf-8")
    sections = []
    for kind, content in DIV_RE.findall(md):
        if kind in ("cta", "caption"):
            sections[-1]["items"].append({"type": "copy", "role": kind, "lines": lines_of(content)})
            continue
        for b in blocks(content):
            hints = dict(HINT_RE.findall(b))
            raw = HINT_RE.sub("", b)
            first = raw.lstrip()
            if first.startswith("### "):
                sections.append({"title": lines_of(raw)[0], "icon": hints.get("icon"), "items": []})
                continue
            if not sections:
                continue
            items = sections[-1]["items"]
            if not raw.strip():
                if "visual" in hints:
                    items.append({"type": "visual", "name": hints["visual"]})
                continue
            lines = lines_of(raw)
            m = STEP_RE.match(first)
            if first.startswith("- [ ]"):
                items.append({"type": "check", "lines": lines})
            elif first.startswith("- "):
                if re.fullmatch(r"\*\*[^*]+\*\*", lines[0]):
                    items.append({"type": "beat", "name": lines[0].strip("*"), "lines": lines[1:]})
                else:
                    items.append({"type": "worry" if lines[0].startswith("״") else "rule", "icon": hints.get("icon"), "lines": lines})
            elif m:
                items.append({"type": "step", "icon": hints.get("icon"), "name": m.group(1), "start": int(m.group(2)),
                              "end": int(m.group(3)), "lines": lines[1:]})
            elif lines[0] == "למשל":
                items.append({"type": "example", "lines": lines[1:]})
            elif hints.get("as") == "ticks":
                items.append({"type": "ticks", "label": lines[0], "lines": lines[1:]})
            else:
                items.append({"type": "para", "icon": hints.get("icon"), "lines": lines})
    return sections


def find(sections, kind):
    return [it for s in sections for it in s["items"] if it["type"] == kind]


def code_spans(md_text):
    return re.findall(r"`([^`]+)`", md_text)


# ---------- render pieces ----------

def copy_btn(target, text, cls="lb-btn sm"):
    return (f'<button class="{cls}" type="button" data-copy="{target}" data-text="{html.escape(text)}">'
            f'{icon("copy")}<span>{UI["copy"]}</span></button>')


def strip(steps):
    total = steps[-1]["end"]
    segs = "".join(
        f'<span class="seg" style="flex-grow:{s["end"] - s["start"]}"><b>{i}</b><small>{html.escape(s["name"])}</small></span>'
        for i, s in enumerate(steps, 1))
    label = UI["strip_label"].format(n=len(steps), t=total)
    return (f'<div class="strip" role="img" aria-label="{label}"><div class="segs">{segs}</div>'
            f'<div class="ticks-row"><span>0</span><span>{total} {UI["seconds"]}</span></div></div>')


def phone(kind, ctx):
    if kind == "open":
        inner = (f'<div class="z z-hook">{html.escape(ctx["hook"])}</div>'
                 '<div class="z z-book"><span class="mini-book"><i></i></span></div>')
    elif kind == "rec":
        inner = (f'<div class="z z-site"><span>{UI["zone_site"]}</span><i></i><i></i><i></i></div>'
                 '<div class="z z-scene"><span class="sofa"></span><span class="mini-book small"><i></i></span></div>')
    else:
        inner = (f'<div class="z z-spread"><span class="spread"><i></i><i></i></span></div>'
                 f'<div class="z z-cta">{html.escape(ctx["cta"])}</div>')
    subs = f'<div class="z z-subs"><span>{UI["zone_subs"]}</span></div>' if kind != "end" else ""
    return f'<div class="phone p-{kind}"><span class="notch"></span>{inner}{subs}<div class="z z-ui"></div></div>'


def visual(name, ctx):
    if name == "screens":
        phones = "".join(f'<div class="phone-wrap">{phone(k, ctx)}<span class="phone-label">{UI[l]}</span></div>'
                         for k, l in (("open", "screen_open"), ("rec", "screen_rec"), ("end", "screen_end")))
        legend = "".join(f'<span class="key {c}"><i></i>{UI[k]}</span>' for c, k in
                         (("k-hook", "zone_hook"), ("k-book", "zone_book"), ("k-subs", "zone_subs"), ("k-ui", "zone_ui")))
        return (f'<figure class="screens"><figcaption>{UI["screens_title"]}</figcaption>'
                f'<div class="phones">{phones}</div><div class="legend">{legend}</div></figure>')
    if name == "topic":
        def row(ok):
            cap = UI["topic_same"] if ok else UI["topic_other"]
            pills = (f'<span class="pill">{UI["topic_hook"]} · {UI["topic_same"]}</span>'
                     f'<span class="pill">{UI["topic_video"]} · {UI["topic_same"]}</span>'
                     f'<span class="pill{"" if ok else " bad"}">{UI["topic_caption"]} · {cap}</span>')
            verdict = UI["topic_yes"] if ok else UI["topic_no"]
            return (f'<div class="topic-row {"ok" if ok else "no"}"><span class="verdict">{icon("check" if ok else "x")}'
                    f'<span>{verdict}</span></span><div class="pills">{pills}</div></div>')
        return f'<div class="topic">{row(True)}{row(False)}</div>'
    if name == "email":
        email = ctx["email"]
        return (f'<div class="emailcard"><span class="badge gold">{icon("mail")}</span>'
                f'<a class="email" id="email-addr" href="mailto:{html.escape(email)}" dir="ltr">{html.escape(email)}</a>'
                f'{copy_btn("email-addr", email, "lb-btn secondary sm")}</div>')
    return ""


def render_items(items, sec_id, ctx):
    out, i, n_copy, n_check = [], 0, 0, 0
    while i < len(items):
        it = items[i]
        t = it["type"]
        if t == "step":
            run = []
            while i < len(items) and items[i]["type"] in ("step", "example", "para") and (items[i]["type"] == "step" or run):
                run.append(items[i]); i += 1
            steps = [s for s in run if s["type"] == "step"]
            out.append(strip(steps))
            lis, num = [], 0
            for s in run:
                if s["type"] == "step":
                    num += 1
                    lis.append([f'<span class="node">{num}</span><div class="step-card"><div class="step-head">'
                                f'<span class="step-ico">{icon(s["icon"])}</span><h3>{inline(s["name"])}</h3>'
                                f'<span class="time">{icon("clock")}{s["start"]} עד {s["end"]} {UI["seconds"]}</span></div>'
                                f'<p class="step-body">{br(s["lines"])}</p>'])
                elif s["type"] == "example":
                    lis[-1].append('<div class="example">' + "".join(f"<p>{inline(l)}</p>" for l in s["lines"]) + "</div>")
                else:
                    lis[-1].append(f'<p class="note">{br(s["lines"])}</p>')
            out.append('<ol class="steps">' + "".join(f'<li>{li[0]}{"".join(li[1:])}</div></li>' for li in lis) + "</ol>")
            continue
        if t in ("worry", "rule", "check", "beat"):
            run = []
            while i < len(items) and items[i]["type"] == t:
                run.append(items[i]); i += 1
            if t == "worry":
                out.append('<div class="cards worries">' + "".join(
                    f'<div class="card worry"><div class="card-head"><span class="badge gold">{icon(w.get("icon") or "help")}</span>'
                    f'<h3>{inline(w["lines"][0])}</h3></div><p>{br(w["lines"][1:])}</p></div>' for w in run) + "</div>")
            elif t == "rule":
                out.append('<div class="cards rules">' + "".join(
                    f'<div class="card rule"><div class="card-head"><span class="badge red">{icon(r.get("icon") or "x")}</span>'
                    f'<h3>{inline(r["lines"][0])}</h3></div><p>{br(r["lines"][1:])}</p></div>' for r in run) + "</div>")
            elif t == "beat":
                cards = []
                for n, b in enumerate(run, 1):
                    see = [l for l in b["lines"] if not l.startswith("״")]
                    say = [l for l in b["lines"] if l.startswith("״")]
                    part = f'<li class="beat"><div class="beat-head"><span class="beat-n">{n}</span><h3>{inline(b["name"])}</h3></div>'
                    if see:
                        part += (f'<div class="beat-see"><span class="tag">{icon("camera")}{UI["beat_see"]}</span>'
                                 f'<p>{br(see)}</p></div>')
                    if say:
                        part += (f'<div class="beat-say"><span class="tag">{icon("mic")}{UI["beat_say"]}</span>'
                                 + "".join(f"<p>{inline(l)}</p>" for l in say) + "</div>")
                    cards.append(part + "</li>")
                out.append('<ol class="board">' + "".join(cards) + "</ol>")
            else:
                boxes = []
                for c in run:
                    n_check += 1
                    boxes.append(f'<li><label class="lb-check"><input type="checkbox" id="chk-{n_check}"><span>{br(c["lines"])}</span></label></li>')
                out.append(f'<div class="card checklist"><div class="lb-row between"><span class="lb-count is-tint" id="chk-count">0 {UI["checked_of"]} {n_check}</span>'
                           f'<button class="lb-btn ghost sm" type="button" id="chk-reset">{UI["reset"]}</button></div>'
                           f'<ul>{"".join(boxes)}</ul></div>')
            continue
        if t == "copy":
            n_copy += 1
            tid = f"copy-{sec_id}-{n_copy}"
            if it["role"] == "cta":
                out.append(f'<div class="ctabox"><p class="cta-text" id="{tid}">{br(it["lines"])}</p>'
                           f'{copy_btn(tid, plain(it["lines"]))}</div>')
            else:
                body, last = it["lines"][:-1], it["lines"][-1]
                out.append(f'<div class="igpost"><div class="ig-head"><span class="av">{icon("user")}</span>'
                           f'<span class="av brand"><img src="{ctx["logo"]}" alt=""></span>'
                           f'<span class="ig-names"><b>{UI["caption_you"]}</b> {UI["caption_and"]}<bdi dir="ltr">{html.escape(ctx["handle"])}</bdi></span></div>'
                           f'<p class="ig-body" id="{tid}">{br(body)}<br><strong class="ig-cta">{inline(last)}</strong></p>'
                           f'<div class="ig-foot">{copy_btn(tid, plain(it["lines"]), "lb-btn secondary sm")}</div></div>')
        elif t == "visual":
            out.append(visual(it["name"], ctx))
        elif t == "ticks":
            out.append(f'<div class="tickbox"><p class="tick-label">{inline(it["label"])}</p><ul>'
                       + "".join(f'<li>{icon("check")}<span>{inline(l)}</span></li>' for l in it["lines"]) + "</ul></div>")
        elif t == "example":
            out.append('<div class="example">' + "".join(f"<p>{inline(l)}</p>" for l in it["lines"]) + "</div>")
        elif it.get("icon"):
            out.append(f'<div class="iconpara"><span class="badge">{icon(it["icon"])}</span><p>{br(it["lines"])}</p></div>')
        else:
            out.append(f'<p class="para">{br(it["lines"])}</p>')
        i += 1
    return "\n".join(out)


PAGE_CSS = """
/* Creator brief. One formal reading column: an ink cover, then sections that each open with an icon badge,
   the shot list as a time strip plus a numbered timeline, a storyboard for the worked example, phone screens
   for the layout, and real-looking previews of the CTA and the caption. Heebo only. Tokens only. */
:root {
  --font-display: var(--font);
  --on-ink: #F5EFE4;
  --on-ink-2: rgba(245, 239, 228, .72);
  --on-ink-fill: rgba(245, 239, 228, .1);
  --on-ink-line: rgba(245, 239, 228, .18);
  --gold-glow: rgba(230, 183, 98, .22);
}
body { font-family: var(--font); }
h1, h2, h3, h4 { font-family: var(--font); }
.brief { max-width: 52rem; gap: 0; padding-block: var(--sp-5) var(--sp-7); }
.ico { width: 1.15rem; height: 1.15rem; flex: none; }

/* cover */
.cover { position: relative; overflow: hidden; background: var(--lb-ink); color: var(--on-ink); border-radius: var(--r-lg);
  padding: var(--sp-6) var(--sp-5); display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: var(--sp-4); align-items: end; }
.cover .eyebrow { color: var(--lb-gold); font-size: var(--fs-footnote); font-weight: 700; letter-spacing: .06em; }
.cover h1 { color: var(--on-ink); font-weight: 800; font-size: clamp(2.1rem, 7vw, 3.2rem); line-height: 1.05; letter-spacing: -.02em; margin-top: var(--sp-2); }
.cover .meta { display: flex; flex-wrap: wrap; gap: var(--sp-2); margin-top: var(--sp-4); }
.cover .meta span { display: inline-flex; align-items: center; gap: .4rem; padding: .35rem .75rem; border-radius: var(--r-pill);
  background: var(--on-ink-fill); box-shadow: inset 0 0 0 1px var(--on-ink-line); color: var(--on-ink); font-size: var(--fs-callout); font-weight: 500; }
.cover .meta .ico { color: var(--lb-gold); width: 1rem; height: 1rem; }
.cover .meta bdi { font-weight: 700; }
.cover img { width: clamp(5.5rem, 22vw, 9rem); height: auto; margin-block-end: calc(-1 * var(--sp-6)); align-self: end; }
.cover .meta span { white-space: nowrap; }
@media (max-width: 560px) {
  .cover { grid-template-columns: minmax(0, 1fr); padding-block: var(--sp-5); }
  .cover img { position: absolute; inset-inline-end: var(--sp-3); top: var(--sp-3); width: 4.75rem; margin: 0; z-index: 1; }
  .cover h1, .cover .eyebrow { padding-inline-end: 5rem; }
}
.cover::after { content: ""; position: absolute; inset-inline-end: -4rem; top: -4rem; width: 14rem; height: 14rem; border-radius: 50%;
  background: radial-gradient(circle, var(--gold-glow), transparent 70%); pointer-events: none; }

/* contents */
.toc { display: grid; gap: var(--sp-2); padding-block: var(--sp-5) var(--sp-2); }
.toc > span { font-size: var(--fs-footnote); font-weight: 700; color: var(--text-3); letter-spacing: .04em; }
.toc nav { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
.toc a { display: inline-flex; align-items: center; gap: .35rem; padding: .35rem .7rem; border-radius: var(--r-pill); background: var(--surface);
  box-shadow: inset 0 0 0 1px var(--line); color: var(--text-2); font-size: var(--fs-footnote); font-weight: 500; }
.toc a:hover { color: var(--tint); box-shadow: inset 0 0 0 1px var(--tint); text-decoration: none; }
.toc a .ico { width: .95rem; height: .95rem; color: var(--tint); }

/* sections */
.sec { display: grid; gap: var(--sp-4); padding-block: var(--sp-6) 0; min-width: 0; }
.sec + .sec { border-top: 1px solid var(--line); margin-top: var(--sp-6); }
.sec-head { display: flex; align-items: center; gap: var(--sp-3); }
.sec-head h2 { font-weight: 800; font-size: clamp(1.35rem, 4vw, 1.65rem); letter-spacing: -.01em; }
.badge { display: grid; place-items: center; width: 2.5rem; height: 2.5rem; border-radius: var(--r-md); background: var(--tint-soft); color: var(--tint); flex: none; }
.badge .ico { width: 1.25rem; height: 1.25rem; }
.badge.gold { background: var(--accent-soft); color: var(--accent-ink); }
.badge.red { background: var(--danger-soft); color: var(--danger); }
.para { color: var(--text-2); font-size: 1.0625rem; line-height: 1.65; }
.para strong, .para .handle { color: var(--text); }
.extlink { display: inline-flex; align-items: center; gap: .35rem; margin-top: var(--sp-2); padding: .4rem .85rem; border-radius: var(--r-pill);
  background: var(--tint); color: var(--text-on-tint); font-weight: 600; font-size: var(--fs-callout); }
.extlink:hover { background: var(--tint-hover); color: var(--text-on-tint); text-decoration: none; }
.extlink .ico { width: .95rem; height: .95rem; }
.handle { font-weight: 700; unicode-bidi: isolate; }
.iconpara { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: var(--sp-3); align-items: start; background: var(--surface-2);
  border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); }
.iconpara .badge { width: 2.1rem; height: 2.1rem; background: var(--surface); }
.iconpara p { color: var(--text); line-height: 1.6; }

.tickbox { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-4) var(--sp-5); display: grid; gap: var(--sp-3); }
.tick-label { font-weight: 700; }
.tickbox ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); }
.tickbox li { display: flex; gap: var(--sp-2); align-items: flex-start; color: var(--text-2); }
.tickbox li .ico { color: var(--success); margin-top: .2rem; }

/* time strip and timeline */
.strip { display: grid; gap: var(--sp-1); }
.segs { display: flex; gap: 3px; }
.seg { min-width: 0; display: grid; gap: 2px; padding: .45rem .4rem; border-radius: var(--r-xs); background: var(--tint-soft); color: var(--tint); text-align: center; }
.seg:nth-child(even) { background: var(--accent-soft); color: var(--accent-ink); }
.seg b { font-size: var(--fs-callout); font-variant-numeric: tabular-nums; }
.seg small { font-size: var(--fs-caption); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ticks-row { display: flex; justify-content: space-between; font-size: var(--fs-caption); color: var(--text-3); font-variant-numeric: tabular-nums; }
@media (max-width: 560px) { .seg small { display: none; } }

.steps { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-3); position: relative; }
.steps::before { content: ""; position: absolute; inset-inline-start: 1.05rem; top: 1rem; bottom: 1rem; width: 2px; background: var(--line); }
.steps > li { display: grid; grid-template-columns: 2.1rem minmax(0, 1fr); gap: var(--sp-3); align-items: start; position: relative; }
.node { display: grid; place-items: center; width: 2.1rem; height: 2.1rem; border-radius: 50%; background: var(--lb-ink); color: var(--on-ink);
  font-weight: 700; font-variant-numeric: tabular-nums; box-shadow: 0 0 0 4px var(--bg); margin-top: .6rem; }
.step-card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-4); display: grid; gap: var(--sp-3); min-width: 0; }
.step-head { display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-2) var(--sp-3); }
.step-ico { color: var(--tint); display: inline-flex; }
.step-head h3 { font-size: var(--fs-headline); font-weight: 700; }
.time { display: inline-flex; align-items: center; gap: .3rem; margin-inline-start: auto; font-size: var(--fs-footnote); color: var(--text-3);
  font-variant-numeric: tabular-nums; }
.time .ico { width: .9rem; height: .9rem; }
.step-body { color: var(--text); line-height: 1.6; }
.example { display: grid; gap: var(--sp-1); background: var(--accent-soft); border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); }
.example p { font-weight: 600; color: var(--text); }
.note { font-size: var(--fs-callout); color: var(--text-2); }

/* worked example */
.board { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr)); }
.beat { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-4); display: grid; gap: var(--sp-3); align-content: start; }
.beat-head { display: flex; align-items: center; gap: var(--sp-2); }
.beat-n { display: grid; place-items: center; width: 1.75rem; height: 1.75rem; border-radius: 50%; background: var(--lb-ink); color: var(--on-ink);
  font-size: var(--fs-footnote); font-weight: 700; font-variant-numeric: tabular-nums; }
.beat-head h3 { font-size: var(--fs-body); font-weight: 700; }
.tag { display: inline-flex; align-items: center; gap: .3rem; font-size: var(--fs-caption); font-weight: 700; letter-spacing: .04em; color: var(--text-3); }
.tag .ico { width: .85rem; height: .85rem; }
.beat-see { display: grid; gap: var(--sp-1); }
.beat-see p { color: var(--text-2); font-size: var(--fs-callout); }
.beat-say { display: grid; gap: 2px; background: var(--tint-soft); border-radius: var(--r-md); padding: var(--sp-2) var(--sp-3); }
.beat-say .tag { color: var(--tint); margin-bottom: 2px; }
.beat-say p { font-weight: 600; color: var(--text); }

/* phone screens */
.screens { margin: 0; display: grid; gap: var(--sp-3); background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-4); }
.screens figcaption { font-weight: 700; }
.phones { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--sp-3); max-width: 34rem; }
.phone-wrap { display: grid; gap: var(--sp-2); justify-items: center; min-width: 0; }
.phone-label { font-size: var(--fs-footnote); font-weight: 600; color: var(--text-2); }
.phone { position: relative; width: 100%; max-width: 10rem; aspect-ratio: 9 / 16; border: 3px solid var(--lb-ink); border-radius: 1.1rem;
  background: var(--bg); overflow: hidden; }
.notch { position: absolute; top: 4px; left: 50%; transform: translateX(-50%); width: 28%; height: 5px; border-radius: 3px; background: var(--lb-ink); z-index: 2; }
.z { position: absolute; inset-inline: 7%; display: grid; place-items: center; text-align: center; border-radius: 6px; }
.z-hook { top: 7%; height: 22%; background: var(--tint-soft); color: var(--tint); font-size: clamp(.5rem, 1.7vw, .72rem); font-weight: 800; line-height: 1.2; padding: 4px; }
.z-book { top: 32%; height: 30%; }
.mini-book { position: relative; width: 52%; aspect-ratio: 1; border-radius: 4px; background: linear-gradient(160deg, var(--lb-gold), var(--lb-gold-deep));
  box-shadow: 0 6px 14px -8px var(--lb-ink-deep); display: grid; place-items: center; }
.mini-book i { width: 42%; aspect-ratio: 1; border-radius: 50%; background: var(--lb-cream); }
.mini-book.small { width: 34%; position: absolute; inset-inline-start: 18%; bottom: 14%; }
.z-subs { top: 65%; height: 9%; }
.z-subs span { background: var(--lb-ink); color: var(--on-ink); font-size: clamp(.45rem, 1.5vw, .62rem); font-weight: 600; padding: 2px 8px; border-radius: 4px; }
.z-ui { inset-inline: 0; bottom: 0; height: 20%; border-radius: 0;
  background: repeating-linear-gradient(135deg, var(--danger-soft) 0 6px, transparent 6px 12px); box-shadow: inset 0 1px 0 var(--danger-soft); }
.z-site { top: 7%; inset-inline-start: 7%; inset-inline-end: auto; width: 40%; height: 22%; background: var(--surface); border: 1.5px solid var(--tint);
  align-content: start; gap: 3px; padding: 4px; place-items: stretch; z-index: 1; }
.z-site span { font-size: clamp(.42rem, 1.4vw, .58rem); font-weight: 700; color: var(--tint); }
.z-site i { display: block; height: 3px; border-radius: 2px; background: var(--fill-3); }
.z-scene { top: 7%; bottom: 20%; inset-inline: 0; border-radius: 0; background: linear-gradient(180deg, var(--surface-2), var(--surface-sunk)); }
.sofa { position: absolute; inset-inline: 10%; bottom: 18%; height: 22%; border-radius: 10px 10px 4px 4px; background: var(--seq-2); }
.z-spread { top: 9%; height: 40%; }
.spread { display: flex; width: 76%; aspect-ratio: 2 / 1.25; box-shadow: 0 6px 14px -8px var(--lb-ink-deep); }
.spread i { flex: 1; background: var(--surface); border: 1px solid var(--line); }
.spread i:first-child { background: linear-gradient(160deg, var(--seq-2), var(--seq-3)); }
.z-cta { top: 53%; height: 25%; background: var(--lb-ink); color: var(--on-ink); font-size: clamp(.42rem, 1.45vw, .6rem); font-weight: 600; line-height: 1.25; padding: 4px 6px; }
.legend { display: flex; flex-wrap: wrap; gap: var(--sp-2) var(--sp-4); font-size: var(--fs-footnote); color: var(--text-2); }
.key { display: inline-flex; align-items: center; gap: .4rem; }
.key i { width: .85rem; height: .85rem; border-radius: 3px; }
.k-hook i { background: var(--tint-soft); box-shadow: inset 0 0 0 1px var(--tint); }
.k-book i { background: var(--lb-gold); }
.k-subs i { background: var(--lb-ink); }
.k-ui i { background: repeating-linear-gradient(135deg, var(--danger-soft) 0 3px, transparent 3px 6px); box-shadow: inset 0 0 0 1px var(--danger); }

/* one topic */
.topic { display: grid; gap: var(--sp-2); }
.topic-row { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: var(--sp-3); align-items: center; background: var(--surface);
  border: 1px solid var(--line); border-radius: var(--r-md); padding: var(--sp-3); }
.verdict { display: inline-flex; align-items: center; gap: .3rem; font-weight: 700; font-size: var(--fs-callout); }
.ok .verdict { color: var(--success); }
.no .verdict { color: var(--danger); }
.pills { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
.pill { padding: .3rem .65rem; border-radius: var(--r-pill); background: var(--success-soft); color: var(--success); font-size: var(--fs-footnote); font-weight: 600; }
.no .pill { background: var(--fill); color: var(--text-2); }
.no .pill.bad { background: var(--danger-soft); color: var(--danger); }

/* cards */
.cards { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 15.5rem), 1fr)); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-4) var(--sp-5); display: grid; gap: var(--sp-2); align-content: start; min-width: 0; }
.card h3 { font-size: var(--fs-headline); font-weight: 700; line-height: 1.35; }
.card p { color: var(--text-2); line-height: 1.6; }
.card-head { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: var(--sp-3); align-items: center; }

/* CTA and caption previews */
.ctabox { display: grid; gap: var(--sp-3); justify-items: start; background: var(--lb-ink); color: var(--on-ink); border-radius: var(--r-lg); padding: var(--sp-5); }
.cta-text { font-size: clamp(1.2rem, 3.6vw, 1.5rem); font-weight: 700; line-height: 1.4; color: var(--on-ink); }
.ctabox .lb-btn { background: var(--lb-gold); color: var(--lb-ink); }
.ctabox .lb-btn:hover { background: var(--lb-cream); color: var(--lb-ink); }
.lb-btn { display: inline-flex; align-items: center; gap: .4rem; }
.lb-btn .ico { width: 1rem; height: 1rem; }
.igpost { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-4); display: grid; gap: var(--sp-3); max-width: 30rem; box-shadow: var(--shadow-2); }
.ig-head { display: flex; align-items: center; gap: var(--sp-2); }
.av { display: grid; place-items: center; width: 2.1rem; height: 2.1rem; border-radius: 50%; background: var(--surface-2); color: var(--text-3);
  box-shadow: 0 0 0 2px var(--surface), 0 0 0 3.5px var(--accent); overflow: hidden; }
.av.brand { margin-inline-start: -.9rem; background: var(--surface); }
.av.brand img { width: 100%; height: 100%; object-fit: cover; }
.ig-names { font-size: var(--fs-callout); color: var(--text-2); }
.ig-names b { color: var(--text); }
.ig-names bdi { font-weight: 700; color: var(--text); }
.ig-body { line-height: 1.65; font-size: var(--fs-callout); }
.ig-cta { color: var(--tint); }
.ig-foot { display: flex; }
.emailcard { display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-3); background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-lg); padding: var(--sp-3) var(--sp-4); }
.email { font-weight: 700; font-size: 1.125rem; color: var(--text); unicode-bidi: isolate; user-select: all; }
.emailcard .lb-btn { margin-inline-start: auto; }

.checklist ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); }
.foot { display: flex; align-items: center; gap: var(--sp-2); margin-top: var(--sp-7); padding-top: var(--sp-4); border-top: 1px solid var(--line); font-size: var(--fs-footnote); color: var(--text-3); }
.foot img { height: 1.5rem; width: auto; }
@media (prefers-reduced-motion: no-preference) { .lb-btn, .toc a, .extlink { transition: background .15s ease, color .15s ease, box-shadow .15s ease; } }
"""

PAGE_JS = """
<div class="lb-toast" id="toast" role="status" aria-live="polite" hidden></div>
<script>
(function () {
  var toast = document.getElementById("toast"), timer;
  function say(text) { toast.textContent = text; toast.hidden = false; clearTimeout(timer); timer = setTimeout(function () { toast.hidden = true; }, 2200); }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    var text = btn.getAttribute("data-text"), el = document.getElementById(btn.getAttribute("data-copy"));
    function fallback() {
      var r = document.createRange(); r.selectNodeContents(el);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      say(__FALLBACK__);
    }
    try { navigator.clipboard.writeText(text).then(function () { say(__COPIED__); }, fallback); } catch (err) { fallback(); }
  });
  var KEY = "lb-creator-brief-checks", boxes = Array.prototype.slice.call(document.querySelectorAll(".checklist input[type=checkbox]"));
  if (!boxes.length) return;
  var count = document.getElementById("chk-count");
  function update() {
    var n = boxes.filter(function (b) { return b.checked; }).length;
    if (count) count.textContent = n + " " + __OF__ + " " + boxes.length;
    try { localStorage.setItem(KEY, JSON.stringify(boxes.map(function (b) { return b.checked; }))); } catch (err) {}
  }
  try { var saved = JSON.parse(localStorage.getItem(KEY) || "[]"); boxes.forEach(function (b, i) { b.checked = !!saved[i]; }); } catch (err) {}
  boxes.forEach(function (b) { b.addEventListener("change", update); });
  var reset = document.getElementById("chk-reset");
  if (reset) reset.addEventListener("click", function () { boxes.forEach(function (b) { b.checked = false; }); update(); });
  update();
})();
</script>
"""


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def build():
    md = BRIEF.read_text(encoding="utf-8")
    sections = parse()
    hero, rest = sections[0], sections[1:]
    spans = code_spans(md[md.index('<div dir="rtl"'):])
    steps = find(rest, "step")
    examples = find(rest, "example")
    ctas = [it for it in find(rest, "copy") if it["role"] == "cta"]
    ctx = {
        "logo": design.logo_data_uri(),
        "handle": next((s for s in spans if s.startswith("@lumebook")), "@lumebook.il"),
        "email": next((s for s in spans if "@" in s and not s.startswith("@")), ""),
        "hook": unquote(examples[0]["lines"][0]) if examples else "",
        "cta": plain(ctas[0]["lines"]) if ctas else "",
    }
    meta = ""
    if steps:
        meta = (f'<div class="meta"><span>{icon("film")}{UI["meta_parts"].format(n=len(steps))}</span>'
                f'<span>{icon("clock")}{UI["meta_secs"].format(t=steps[-1]["end"])}</span>'
                f'<span>{icon("users")}{UI["meta_collab"]} <bdi dir="ltr">{html.escape(ctx["handle"])}</bdi></span></div>')
    cover = (f'<header class="cover"><div><span class="eyebrow">{UI["brand"]}</span><h1>{inline(hero["title"])}</h1>{meta}</div>'
             f'<img src="{data_uri(MASCOT)}" alt=""></header>')
    toc = (f'<div class="toc"><span>{UI["toc"]}</span><nav>'
           + "".join(f'<a href="#s{n}">{icon(s["icon"])}{inline(s["title"])}</a>' for n, s in enumerate(rest, 1)) + "</nav></div>")
    body = []
    for n, s in enumerate(rest, 1):
        body.append(f'<section class="sec" id="s{n}"><div class="sec-head"><span class="badge">{icon(s["icon"])}</span>'
                    f'<h2>{inline(s["title"])}</h2></div>\n{render_items(s["items"], n, ctx)}\n</section>')
    js = (PAGE_JS.replace("__COPIED__", repr(UI["copied"])).replace("__OF__", repr(UI["checked_of"]))
          .replace("__FALLBACK__", repr(UI["copy_fallback"].replace("\n", " "))))
    page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
{design.head(include_fonts=False)}
<script>document.documentElement.setAttribute("dir","rtl");document.documentElement.setAttribute("lang","he");</script>
<style>{PAGE_CSS}</style>

<header class="lb-topbar" dir="rtl" lang="he">
  <div class="lb-topbar-in">
    <span class="lb-brand"><img src="{ctx["logo"]}" alt=""><span><b>{UI["brand"]}</b><small>{UI["brand_sub"]}</small></span></span>
  </div>
</header>

<main class="lb-page brief" dir="rtl" lang="he">
{cover}
{toc}
{chr(10).join(body)}
<footer class="foot"><img src="{ctx["logo"]}" alt=""><span>{UI["brand"]} · {UI["brand_sub"]}</span></footer>
</main>
{js}"""
    OUT.write_text(page, encoding="utf-8")
    cut = page.index('<header class="lb-topbar"')
    head = page[:cut].replace("<title>", (
        '<meta name="robots" content="noindex">\n'
        f'<meta property="og:title" content="{TITLE}">\n'
        f'<meta property="og:description" content="{UI["og_description"]}">\n'
        '<meta property="og:locale" content="he_IL">\n<title>'), 1)
    SITE.parent.mkdir(parents=True, exist_ok=True)
    SITE.write_text(f'<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n{head.rstrip()}\n</head>\n<body>\n{page[cut:].strip()}\n</body>\n</html>\n',
                    encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} and {SITE.relative_to(ROOT)} ({len(page) // 1024} KB, {len(rest)} sections)")


if __name__ == "__main__":
    build()
