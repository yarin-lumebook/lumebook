#!/usr/bin/env python3
"""Build the creator brief page from creator-brief.md.

    python3 research/israeli-product-reels/src/build_creator_brief.py

Input:  research/israeli-product-reels/creator-brief.md, only its Hebrew parts (the <div dir="rtl"> blocks, read
        with the same parser as lint_creator_brief.py, so the page shows exactly the linted text). Blocks marked
        data-page="messages" make the second page (דף מסרים); everything else is the brief.
Output: research/israeli-product-reels/creator-brief.html, an artifact page (a fragment, as artifacts want), and
        sites/lumebook-creator-brief/index.html, the same page as a full document for Vercel (noindex).

Look (Yarin, 05 Nov 2026: every page white only, on the latest design system): the LumeBook design system as it is,
inlined with design.head(nav=False) (fonts included; no project nav: creators see this page): white ground, neutral ink text, violet for what you can press, gold for
brand emphasis, the system's lines, fills, radii and shadows. Heebo is the main font, Assistant (--font-2) the one for
labels, captions, counts and chips. PAGE_CSS only lays the page out and uses the system's tokens; it defines no palette
of its own, no dark mode and no switch (the 15 Oct ink/cream palette, its light/dark toggle and boot script are gone).
Laid out on Apple's design principles. A top bar holds the brand, a two-option switch (בריף / דף מסרים) and a
hamburger menu with the sections.

How blocks become the page: the first ### heading of each page is its cover, every other ### heading a section.
A block that starts with **name · A עד B שניות** is a shot step (the time strip is drawn from these), a block
that starts with למשל is an example for the step before it, a list item whose first line is bold is a beat of
the worked example (or a message card with <!--as:message-->), one whose first line is a quote (״...״) a worry
card, other list items do-not rules, "- [ ]" items a checklist, and the data-lint="cta" / "caption" blocks get a
copy button. Render hints are HTML comments: <!--icon:NAME--> (ICONS below), <!--as:ticks|lead|message-->, and
<!--visual:screens|topic|email--> as its own block. Edit the brief, then rebuild; never edit the HTML.
Standard library only.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402
from lint_creator_brief import ATTR_RE, BRIEF, DIV_RE, blocks  # noqa: E402

OUT = HERE.parent / "creator-brief.html"
SITE = ROOT / "sites" / "lumebook-creator-brief" / "index.html"  # standalone copy for Vercel
TITLE = "בריף הרילס של לומיבוק"
SITE_URL = json.loads((ROOT / "lumebook.json").read_text(encoding="utf-8"))["components"]["creator-brief"]["deploy"]["url"].rstrip("/") + "/"
PREVIEW = ROOT / "shared" / "brand" / "creator-brief-preview-v2.jpg"
PREVIEW_PATH = "img/creator-brief-preview-v2.jpg"
PAGES = ("brief", "messages")
# Runs before the first paint: right-to-left Hebrew on <html> (the artifact copy is a fragment without its own <html>).
# White only since 05 Nov 2026, so there is no mode to set any more.
RTL_BOOT = '<script>document.documentElement.setAttribute("dir","rtl");document.documentElement.setAttribute("lang","he")</script>'
# The example Reel, played on the page (<!--visual:reel-->). Web copies made with ffmpeg from the 15 Oct download
# (540p H.264, faststart); raw media stays out of git. The build copies them next to the Vercel page, and the
# artifact publish maps the same relative paths (see the md notes).
REEL_DIR = ROOT / "media" / "projects" / "2026-10-15-israeli-product-reels" / "web"
REEL = {"video": "media/shoham-reel.mp4", "poster": "media/shoham-reel-poster.jpg"}


def reel_files(slug):
    """The web copies of a card's example Reel (20 Oct 2026): media/ex-SLUG.mp4 and media/ex-SLUG-poster.jpg.
    Shoham's Reel keeps its 15 Oct file names; since 26 Oct it is the first card of the one example carousel."""
    if slug == "shoham":
        return REEL
    return {"video": f"media/ex-{slug}.mp4", "poster": f"media/ex-{slug}-poster.jpg"}

# Hebrew the page adds around the brief's own text (linted by lint_creator_brief.py too)
UI = {
    "brand": "לומיבוק",
    "brand_sub": "בריף ליוצרים",
    "og_description": "שלד צילום ודוגמה מלאה לרילס על הספר האישי שלכם",
    "view_brief": "בריף",
    "view_messages": "דף מסרים",
    "views_label": "עמודים",
    "menu": "תפריט",
    "toc": "בעמוד הזה",
    "copy": "העתקה",
    "copied": "הועתק",
    "copy_fallback": "הטקסט מסומן\nאפשר להעתיק",
    "checked_of": "מתוך",
    "reset": "ניקוי הסימונים",
    "seconds": "שניות",
    "strip_label": "{n} חלקים לאורך {t} שניות",
    "beat_see": "רואים",
    "beat_say": "אומרים",
    "msg_example": "למשל",
    "screens_title": "איפה כל דבר יושב על המסך",
    "swipe_hint": "החליקו הצידה",
    "prev": "הסרטון הקודם",
    "next": "הסרטון הבא",
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
    "reel_by": "הסרטון של",
    "reel_label": "הרילס לדוגמה",
}

# 24 x 24 stroke icons (currentColor), drawn to sit with Heebo at body size
ICONS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
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
    "chev-r": '<path d="m9 6 6 6-6 6"/>',
    "chev-l": '<path d="m15 6-6 6 6 6"/>',
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
    """{page: [section, ...]}; each section {title, icon, items}."""
    md = BRIEF.read_text(encoding="utf-8")
    pages = {p: [] for p in PAGES}
    for attrs, content in DIV_RE.findall(md):
        attrs = dict(ATTR_RE.findall(attrs))
        sections = pages[attrs.get("page", "brief")]
        if attrs.get("lint") in ("cta", "caption"):
            sections[-1]["items"].append({"type": "copy", "role": attrs["lint"], "lines": lines_of(content)})
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
                    kind = {"message": "message", "reelcard": "reelcard"}.get(hints.get("as"), "beat")
                    items.append({"type": kind, "icon": hints.get("icon"), "name": lines[0].strip("*"), "lines": lines[1:],
                                  "slug": hints.get("reel")})
                else:
                    items.append({"type": "worry" if lines[0].startswith("״") else "rule", "icon": hints.get("icon"), "lines": lines})
            elif m:
                items.append({"type": "step", "icon": hints.get("icon"), "name": m.group(1), "start": int(m.group(2)),
                              "end": int(m.group(3)), "lines": lines[1:]})
            elif lines[0] == "למשל":
                items.append({"type": "example", "lines": lines[1:]})
            elif hints.get("as") == "ticks":
                items.append({"type": "ticks", "label": lines[0], "lines": lines[1:]})
            elif hints.get("as") == "lead":
                items.append({"type": "lead", "lines": lines})
            else:
                items.append({"type": "para", "icon": hints.get("icon"), "lines": lines})
    return pages


def find(sections, kind):
    return [it for s in sections for it in s["items"] if it["type"] == kind]


# ---------- render pieces ----------

def copy_btn(target, text, cls="lb-btn sm"):
    return (f'<button class="{cls}" type="button" data-copy="{target}" data-text="{html.escape(text)}">'
            f'{icon("copy")}<span>{UI["copy"]}</span></button>')


def dots(n):
    """Position dots for a swipe row (shown on phones only)."""
    return f'<div class="dots" aria-hidden="true"><span>{UI["swipe_hint"]}</span>' + "<i></i>" * n + "</div>"


def carousel_nav(n):
    """Dots plus previous / next buttons for the example Reels carousel (shown at every width, 26 Oct 2026)."""
    return (f'<div class="dots nav"><button class="iconbtn" type="button" data-step="-1" aria-label="{UI["prev"]}">{icon("chev-r")}</button>'
            f'<span>{UI["swipe_hint"]}</span>' + "<i></i>" * n +
            f'<button class="iconbtn" type="button" data-step="1" aria-label="{UI["next"]}">{icon("chev-l")}</button></div>')


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
    # Meta's Reels safe zone (smm-research F2, T4; 18 Oct 2026): nothing in the top 14%, the bottom 35% or 6% at each side
    ui = "".join(f'<div class="z z-ui {c}"></div>' for c in ("ui-bottom", "ui-top", "ui-side ui-start", "ui-side ui-end"))
    return f'<div class="phone p-{kind}"><span class="notch"></span>{inner}{subs}{ui}</div>'


def visual(name, ctx):
    if name == "screens":
        phones = "".join(f'<div class="phone-wrap">{phone(k, ctx)}<span class="phone-label">{UI[l]}</span></div>'
                         for k, l in (("open", "screen_open"), ("rec", "screen_rec"), ("end", "screen_end")))
        legend = "".join(f'<span class="key {c}"><i></i>{UI[k]}</span>' for c, k in
                         (("k-hook", "zone_hook"), ("k-book", "zone_book"), ("k-subs", "zone_subs"), ("k-ui", "zone_ui")))
        return (f'<figure class="screens"><figcaption>{UI["screens_title"]}</figcaption>'
                f'<div class="phones" data-carousel>{phones}</div>{dots(3)}<div class="legend">{legend}</div></figure>')
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
    if name == "reel":
        return (f'<figure class="reel"><div class="reel-frame"><video src="{REEL["video"]}" poster="{REEL["poster"]}" controls playsinline '
                f'preload="metadata" aria-label="{UI["reel_label"]}"></video></div>'
                f'<figcaption>{UI["reel_by"]} <bdi dir="ltr">{html.escape(ctx["creator"])}</bdi></figcaption></figure>')
    if name == "email":
        email = ctx["email"]
        return (f'<div class="emailcard"><span class="badge">{icon("mail")}</span>'
                f'<a class="email" id="email-addr" href="mailto:{html.escape(email)}" dir="ltr">{html.escape(email)}</a>'
                f'{copy_btn("email-addr", email, "lb-btn secondary sm")}</div>')
    return ""


def card_head(icon_name, title, badge=""):
    return (f'<div class="card-head"><span class="badge{badge}">{icon(icon_name)}</span>'
            f'<h3>{inline(title)}</h3></div>')


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
        if t in ("worry", "rule", "check", "beat", "message", "reelcard"):
            run = []
            while i < len(items) and items[i]["type"] == t:
                run.append(items[i]); i += 1
            if t == "worry":
                out.append('<div class="cards">' + "".join(
                    f'<div class="card">{card_head(w.get("icon") or "help", w["lines"][0], " gold")}<p>{br(w["lines"][1:])}</p></div>'
                    for w in run) + "</div>")
            elif t == "rule":
                out.append('<div class="cards">' + "".join(
                    f'<div class="card rule">{card_head(r.get("icon") or "x", r["lines"][0], " dark")}<p>{br(r["lines"][1:])}</p></div>'
                    for r in run) + "</div>")
            elif t == "reelcard":
                cards = []
                for c in run:
                    f = reel_files(c["slug"])
                    who, _, topic = c["name"].partition(" · ")
                    cards.append(
                        f'<li class="rcard"><div class="reel-frame"><video src="{f["video"]}" poster="{f["poster"]}" controls playsinline '
                        f'preload="none" aria-label="{html.escape(who)}"></video></div>'
                        f'<h3>{inline(who)}<small>{inline(topic)}</small></h3><ul>'
                        + "".join(f'<li>{inline(l)}</li>' for l in c["lines"]) + "</ul></li>")
                out.append('<ul class="reelrow" data-carousel>' + "".join(cards) + "</ul>" + carousel_nav(len(cards)))
            elif t == "message":
                cards = []
                for msg in run:
                    facts = [l for l in msg["lines"] if not l.startswith("״")]
                    says = [l for l in msg["lines"] if l.startswith("״")]
                    part = f'<div class="card msg">{card_head(msg.get("icon") or "message", msg["name"])}'
                    if facts:
                        part += f'<p>{br(facts)}</p>'
                    if says:
                        part += (f'<div class="say"><span class="tag">{icon("quote")}{UI["msg_example"]}</span>'
                                 + "".join(f"<p>{inline(l)}</p>" for l in says) + "</div>")
                    cards.append(part + "</div>")
                out.append('<div class="cards msgs">' + "".join(cards) + "</div>")
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
                        part += (f'<div class="say"><span class="tag">{icon("mic")}{UI["beat_say"]}</span>'
                                 + "".join(f"<p>{inline(l)}</p>" for l in say) + "</div>")
                    cards.append(part + "</li>")
                out.append('<ol class="board" data-carousel>' + "".join(cards) + "</ol>" + dots(len(cards)))
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
        elif t == "lead":
            out.append(f'<p class="lead">{br(it["lines"])}</p>')
        elif t == "example":
            out.append('<div class="example">' + "".join(f"<p>{inline(l)}</p>" for l in it["lines"]) + "</div>")
        elif it.get("icon"):
            out.append(f'<div class="iconpara"><span class="badge">{icon(it["icon"])}</span><p>{br(it["lines"])}</p></div>')
        else:
            out.append(f'<p class="para">{br(it["lines"])}</p>')
        i += 1
    return "\n".join(out)


PAGE_CSS = """
/* Creator brief, white (Yarin, 05 Nov 2026: every page white only, on the latest design system). The page runs on
   the design system's own tokens, which design.head() inlines above: white ground, neutral ink text (--text, --text-2,
   --text-3), violet (--tint) for what you can press, gold (--accent, --accent-ink, --accent-soft) for brand emphasis,
   the system's lines, fills, radii and shadows. Nothing here redefines a system token or adds a palette, a dark mode
   or a switch (the 15 Oct ink/cream palette and its light/dark toggle are gone). Apple's principles still lead the
   layout: clarity (one big headline, a strict type scale, softer ink for secondary text), deference (white cards
   with a hairline, the content leads) and depth (a translucent top bar, a raised menu; no glows, the cover is plain
   white). Heebo for reading, Assistant (--font-2) for labels, captions, counts and chips. Brand fixed tokens
   (--lb-gold, --lb-cream ...) only where the mock book and phone pictures need a fixed colour. */
.brief { --gutter: var(--sp-5); max-width: 52rem; gap: 0; padding-block: 0 var(--sp-7); }
.ico { width: 1.15rem; height: 1.15rem; flex: none; }

/* top bar: brand, page switch, menu */
.lb-topbar-in { max-width: 52rem; min-height: 3.25rem; gap: var(--sp-3); }
.lb-brand { padding-inline: 0; color: var(--text); }
.lb-brand:hover { color: var(--text); }
.lb-brand img { height: 1.75rem; }
.lb-brand b { font-family: var(--font); font-weight: 700; font-size: 1.0625rem; letter-spacing: -.01em; }
.top-actions { margin-inline-start: auto; display: flex; align-items: center; gap: var(--sp-1); }
.segctl { display: inline-flex; padding: 2px; gap: 2px; border-radius: .6rem; background: var(--fill-2); }
.segctl button { appearance: none; border: 0; background: transparent; color: var(--text-2); font: inherit; font-size: var(--fs-footnote);
  font-weight: 600; min-height: 2rem; padding: 0 .95rem; border-radius: .5rem; cursor: pointer; }
.segctl button[aria-selected="true"] { background: var(--surface); color: var(--text); box-shadow: var(--shadow-1), 0 0 0 .5px var(--line); }
.iconbtn { display: grid; place-items: center; width: 2.75rem; height: 2.75rem; border: 0; border-radius: 50%; background: transparent; color: var(--text); cursor: pointer; }
.iconbtn:hover { background: var(--fill-2); }
.iconbtn .ico { width: 1.4rem; height: 1.4rem; }
.iconbtn .i-close, .iconbtn[aria-expanded="true"] .i-open { display: none; }
.iconbtn[aria-expanded="true"] .i-close { display: block; }
.scrim { position: fixed; inset: 0; z-index: 25; background: var(--overlay); }
.menu { position: fixed; z-index: 30; top: calc(env(safe-area-inset-top, 0px) + 3.6rem);
  inset-inline-end: max(var(--sp-3), calc((100vw - 52rem) / 2 + var(--sp-3))); width: min(21rem, calc(100vw - 2 * var(--sp-3)));
  max-height: calc(100dvh - 5rem); overflow: auto; overscroll-behavior: contain; padding: var(--sp-2); display: grid; gap: 2px;
  background: var(--surface); border-radius: var(--r-lg); box-shadow: var(--shadow-3), 0 0 0 1px var(--line); }
.menu h2 { font-family: var(--font-2); font-size: var(--fs-caption); font-weight: 600; color: var(--text-3); padding: var(--sp-2) var(--sp-3) 2px; letter-spacing: .02em; }
.menu a { display: flex; align-items: center; gap: var(--sp-3); min-height: 2.75rem; padding-inline: var(--sp-3); border-radius: var(--r-md);
  color: var(--text); font-size: var(--fs-body); font-weight: 500; }
.menu a:hover { background: var(--fill-2); color: var(--text); text-decoration: none; }
.menu a .ico { color: var(--tint); }
.menu a.is-active { background: var(--tint-soft); font-weight: 700; }
.menu hr { border: 0; height: 1px; background: var(--line); margin: var(--sp-1) var(--sp-3); }
.menu .group { display: grid; gap: 2px; }

/* cover */
.cover { position: relative; display: grid; gap: var(--sp-2); padding-block: var(--sp-7) var(--sp-1); }
.cover .eyebrow { font-family: var(--font-2); font-size: var(--fs-callout); font-weight: 700; color: var(--accent-ink); letter-spacing: .02em; }
.cover h1 { font-family: var(--font); font-weight: 800; font-size: clamp(2.75rem, 9vw, 4.5rem); line-height: 1.02; letter-spacing: -.035em; color: var(--text); }
.cover .lede { text-wrap: pretty; margin-top: var(--sp-3); max-width: 34rem; font-size: clamp(1.2rem, 3vw, 1.45rem); line-height: 1.45; font-weight: 500; color: var(--text-2); }
main { position: relative; isolation: isolate; overflow-x: clip; } /* nothing inside may widen the page */

/* sections */
.sec { display: grid; gap: var(--sp-4); padding-block-start: var(--sp-7); min-width: 0; }
.sec-head { display: flex; align-items: center; gap: var(--sp-3); }
.sec-head h2 { font-weight: 800; font-size: clamp(1.55rem, 4.6vw, 2.1rem); line-height: 1.15; letter-spacing: -.025em; }
.badge { display: grid; place-items: center; width: 2.25rem; height: 2.25rem; border-radius: .625rem; background: var(--tint-soft); color: var(--tint); flex: none; }
.badge .ico { width: 1.2rem; height: 1.2rem; }
.badge.gold { background: var(--accent-soft); color: var(--accent-ink); }
.badge.dark { background: var(--danger-soft); color: var(--danger); }
.para { color: var(--text-2); font-size: 1.0625rem; line-height: 1.6; }
.para strong, .para .handle { color: var(--text); }
.lead { font-size: clamp(1.3rem, 4.4vw, 2rem); font-weight: 700; line-height: 1.3; letter-spacing: -.02em; color: var(--text); text-wrap: balance; }
.handle { font-weight: 700; unicode-bidi: isolate; color: var(--text); }
.extlink { display: inline-flex; align-items: center; gap: .4rem; margin-top: var(--sp-3); min-height: 2.5rem; padding-inline: 1.1rem; border-radius: var(--r-pill);
  background: var(--tint); color: var(--text-on-tint); font-weight: 600; font-size: var(--fs-callout); }
.extlink:hover { background: var(--tint-hover); color: var(--text-on-tint); text-decoration: none; }
.extlink .ico { width: 1rem; height: 1rem; }

/* white cards: a hairline sets them apart from the white ground (as .lb-card) */
.card, .step-card, .beat, .tickbox, .screens, .topic-row, .emailcard, .iconpara, .igpost { background: var(--glass-sheen), var(--glass-card); border: 1px solid transparent; box-shadow: var(--glass-card-rim), var(--glass-card-lift); }
.iconpara { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: var(--sp-3); align-items: center; border-radius: var(--r-lg); padding: var(--sp-3) var(--sp-4); }
.iconpara p { color: var(--text); line-height: 1.55; }

.tickbox { border-radius: var(--r-lg); padding: var(--sp-4) var(--sp-5); display: grid; gap: var(--sp-3); }
.tick-label { font-weight: 700; }
.tickbox ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); }
.tickbox li { display: flex; gap: var(--sp-2); align-items: flex-start; color: var(--text-2); }
.tickbox li .ico { color: var(--success); margin-top: .25rem; }

/* time strip and timeline */
.strip { display: grid; gap: var(--sp-1); }
.segs { display: flex; gap: 3px; }
.seg { min-width: 0; display: grid; gap: 2px; padding: .5rem .4rem; border-radius: var(--r-sm); background: var(--glass-sheen), linear-gradient(var(--tint-soft), var(--tint-soft)), var(--glass-card); box-shadow: var(--glass-card-rim-sm); color: var(--tint); text-align: center; font-family: var(--font-2); }
.seg:nth-child(even) { background: var(--glass-sheen), linear-gradient(color-mix(in srgb, var(--accent-soft) 84%, transparent), color-mix(in srgb, var(--accent-soft) 84%, transparent)), var(--glass-card); color: var(--accent-ink); }
.seg b { font-size: var(--fs-callout); font-variant-numeric: tabular-nums; }
.seg small { font-size: var(--fs-caption); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ticks-row { display: flex; justify-content: space-between; font-family: var(--font-2); font-size: var(--fs-caption); color: var(--text-3); font-variant-numeric: tabular-nums; }
@media (max-width: 560px) { .seg small { display: none; } }
.steps { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-3); position: relative; }
.steps::before { content: ""; position: absolute; inset-inline-start: 1.05rem; top: 1rem; bottom: 1rem; width: 1.5px; background: var(--line-strong); }
.steps > li { display: grid; grid-template-columns: 2.1rem minmax(0, 1fr); gap: var(--sp-3); align-items: start; position: relative; }
/* gold number discs carry ink numbers (white on gold fails 4.5:1) */
.node { display: grid; place-items: center; width: 2.1rem; height: 2.1rem; border-radius: 50%; background: var(--accent); color: var(--text);
  font-family: var(--font-2); font-weight: 800; font-variant-numeric: tabular-nums; box-shadow: 0 0 0 4px var(--bg); margin-top: .6rem; }
.step-card { border-radius: var(--r-lg); padding: var(--sp-4) var(--sp-5); display: grid; gap: var(--sp-3); min-width: 0; }
.step-head { display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-2) var(--sp-3); }
.step-ico { color: var(--tint); display: inline-flex; }
.step-head h3 { font-size: var(--fs-headline); font-weight: 700; letter-spacing: -.01em; }
.time { display: inline-flex; align-items: center; gap: .3rem; margin-inline-start: auto; font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); font-variant-numeric: tabular-nums; }
.time .ico { width: .9rem; height: .9rem; }
.step-body { color: var(--text); line-height: 1.6; }
.example { display: grid; gap: var(--sp-1); background: var(--glass-sheen), linear-gradient(color-mix(in srgb, var(--accent-soft) 84%, transparent), color-mix(in srgb, var(--accent-soft) 84%, transparent)), var(--glass-card); box-shadow: var(--glass-card-rim-sm); border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); }
.example p { font-weight: 600; color: var(--accent-ink); }
.note { font-size: var(--fs-callout); color: var(--text-2); }

/* worked example and message examples */
.board { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr)); }
.beat { border-radius: var(--r-lg); padding: var(--sp-4); display: grid; gap: var(--sp-3); align-content: start; }
.beat-head { display: flex; align-items: center; gap: var(--sp-2); }
.beat-n { display: grid; place-items: center; width: 1.75rem; height: 1.75rem; border-radius: 50%; background: var(--accent); color: var(--text);
  font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 800; font-variant-numeric: tabular-nums; }
.beat-head h3 { font-size: var(--fs-body); font-weight: 700; }
.tag { display: inline-flex; align-items: center; gap: .3rem; font-family: var(--font-2); font-size: var(--fs-caption); font-weight: 600; letter-spacing: .02em; color: var(--text-3); }
.tag .ico { width: .85rem; height: .85rem; }
.beat-see { display: grid; gap: var(--sp-1); }
.beat-see p { color: var(--text-2); font-size: var(--fs-callout); }
.say { display: grid; gap: 2px; background: var(--tint-soft); border-radius: var(--r-md); padding: var(--sp-2) var(--sp-3); }
.say .tag { margin-bottom: 2px; color: var(--tint); }
.say p { font-weight: 600; color: var(--text); }

/* phone screens */
.screens { margin: 0; display: grid; gap: var(--sp-3); border-radius: var(--r-lg); padding: var(--sp-5); }
.screens figcaption { font-weight: 700; }
.phones { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--sp-4); max-width: 34rem; }
.phone-wrap { display: grid; gap: var(--sp-2); justify-items: center; min-width: 0; }
.phone-label { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-2); }
.phone { container-type: inline-size; position: relative; width: 100%; max-width: 10rem; aspect-ratio: 9 / 16; border: 3px solid var(--text);
  border-radius: 1.2rem; background: var(--surface-2); overflow: hidden; }
.notch { position: absolute; top: 4px; left: 50%; transform: translateX(-50%); width: 28%; height: 5px; border-radius: 3px; background: var(--text); z-index: 2; }
/* everything that matters sits between 14% and 65% of the height and 6% in from each side (Meta's Reels safe zone,
   smm-research F2 and T4, 18 Oct 2026); the hatched bands are where Instagram's caption and buttons sit */
.z { position: absolute; inset-inline: 7%; display: grid; place-items: center; text-align: center; border-radius: 6px; }
.z-hook { top: 16%; height: 13%; background: var(--tint-soft); color: var(--tint); font-size: .55rem; font-size: 6.4cqw; font-weight: 800; line-height: 1.2; padding: 3px 4px; }
.z-book { top: 31%; height: 21%; }
.mini-book { position: relative; width: 40%; aspect-ratio: 1; border-radius: 4px; background: linear-gradient(160deg, var(--lb-gold), var(--lb-gold-deep));
  box-shadow: 0 6px 14px -8px var(--overlay); display: grid; place-items: center; }
.mini-book i { width: 42%; aspect-ratio: 1; border-radius: 50%; background: var(--lb-cream); }
.mini-book.small { width: 32%; position: absolute; inset-inline-end: 12%; bottom: 47%; }
.z-subs { top: 55%; height: 8%; }
.z-subs span { background: var(--text); color: var(--bg); font-size: .55rem; font-size: 6cqw; font-weight: 700; padding: 2px 8px; border-radius: 4px; }
.z-ui { inset-inline: 0; border-radius: 0; background: repeating-linear-gradient(135deg, var(--danger-soft) 0 6px, transparent 6px 12px); z-index: 1; }
.ui-bottom { bottom: 0; height: 35%; box-shadow: inset 0 1px 0 var(--danger-soft); }
.ui-top { top: 0; height: 14%; box-shadow: inset 0 -1px 0 var(--danger-soft); }
.ui-side { top: 14%; bottom: 35%; width: 6%; }
.ui-start { inset-inline: 0 auto; }
.ui-end { inset-inline: auto 0; }
.z-site { top: 16%; inset-inline-start: 7%; inset-inline-end: auto; width: 40%; height: 20%; background: var(--surface); border: 1.5px solid var(--tint);
  align-content: start; gap: 3px; padding: 4px; place-items: stretch; z-index: 1; }
.z-site span { font-size: .5rem; font-size: 5.5cqw; font-weight: 700; color: var(--tint); }
.z-site i { display: block; height: 3px; border-radius: 2px; background: var(--fill-3); }
.z-scene { top: 0; bottom: 0; inset-inline: 0; border-radius: 0; background: linear-gradient(180deg, var(--surface-2), var(--surface-sunk)); }
.sofa { position: absolute; inset-inline: 10%; bottom: 30%; height: 18%; border-radius: 10px 10px 4px 4px; background: var(--fill-3); }
.z-spread { top: 16%; height: 24%; }
.spread { display: flex; width: 76%; aspect-ratio: 2 / 1.25; box-shadow: 0 6px 14px -8px var(--overlay); }
.spread i { flex: 1; background: var(--surface); }
.spread i:first-child { background: linear-gradient(160deg, var(--lb-gold), var(--lb-gold-deep)); }
.z-cta { top: 42%; height: 21%; background: var(--tint); color: var(--text-on-tint); font-size: .5rem; font-size: 5.6cqw; font-weight: 600; line-height: 1.25; padding: 4px 6px; }
.legend { display: flex; flex-wrap: wrap; gap: var(--sp-2) var(--sp-4); font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-2); }
.key { display: inline-flex; align-items: center; gap: .4rem; }
.key i { width: .85rem; height: .85rem; border-radius: 3px; }
.k-hook i { background: var(--tint-soft); box-shadow: inset 0 0 0 1px var(--tint); }
.k-book i { background: var(--lb-gold); }
.k-subs i { background: var(--text); }
.k-ui i { background: repeating-linear-gradient(135deg, var(--danger-soft) 0 3px, transparent 3px 6px); box-shadow: inset 0 0 0 1px var(--danger); }

/* one topic */
.topic { display: grid; gap: var(--sp-2); }
.topic-row { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: var(--sp-3); align-items: center; border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4); }
.verdict { display: inline-flex; align-items: center; gap: .3rem; font-family: var(--font-2); font-weight: 700; font-size: var(--fs-callout); }
.ok .verdict { color: var(--success); }
.no .verdict { color: var(--danger); }
.pills { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
.pill { padding: .3rem .7rem; border-radius: var(--r-pill); background: var(--success-soft); color: var(--success); font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; }
.no .pill { background: var(--fill-2); color: var(--text-2); }
.no .pill.bad { background: transparent; border: 1px dashed var(--danger); color: var(--danger); text-decoration: line-through; }

/* cards */
.cards { display: grid; gap: var(--sp-3); grid-template-columns: repeat(auto-fit, minmax(min(100%, 15.5rem), 1fr)); }
.card { border-radius: var(--r-lg); padding: var(--sp-4) var(--sp-5); display: grid; gap: var(--sp-2); align-content: start; min-width: 0; }
.card-head { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: var(--sp-3); align-items: center; }
.card h3 { font-size: var(--fs-headline); font-weight: 700; line-height: 1.35; letter-spacing: -.01em; }
.card p { color: var(--text-2); line-height: 1.6; }
.msg .say { margin-top: var(--sp-1); }

/* the example Reel, playing in a phone frame */
.reel { margin: 0; display: grid; justify-items: center; gap: var(--sp-2); }
.reel-frame { width: min(17rem, 72vw); aspect-ratio: 9 / 16; border-radius: 1.6rem; overflow: hidden; background: var(--lb-ink-deep);
  border: 4px solid var(--surface-sunk); box-shadow: 0 0 0 1px var(--line), var(--shadow-3); }
.reel video { display: block; width: 100%; height: 100%; object-fit: cover; }
.reel figcaption { font-size: var(--fs-footnote); color: var(--text-3); }
.reel figcaption bdi { color: var(--text-2); font-weight: 600; }

/* all the example Reels in one carousel at every width (26 Oct 2026): swipe, or the arrows under it */
.reelrow { list-style: none; margin: 0; padding: 2px 0 var(--sp-1); display: flex; gap: var(--sp-4); overflow-x: auto; scroll-snap-type: x mandatory;
  scrollbar-width: none; overscroll-behavior-x: contain; }
.reelrow::-webkit-scrollbar { display: none; }
.rcard { flex: 0 0 15rem; scroll-snap-align: center; display: grid; gap: var(--sp-2); align-content: start; justify-items: center; min-width: 0; }
.dots.nav { display: flex; }
.dots.nav .iconbtn { width: 2.25rem; height: 2.25rem; background: var(--surface); box-shadow: inset 0 0 0 1px var(--line-strong); }
.dots.nav .iconbtn:hover { background: var(--fill-2); }
.dots.nav button:first-child { margin-inline-end: var(--sp-2); }
.dots.nav button:last-child { margin-inline-start: var(--sp-2); }
.rcard .reel-frame { width: 100%; }
.rcard h3 { width: 100%; font-size: var(--fs-headline); font-weight: 700; line-height: 1.35; display: grid; }
.rcard h3 small { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); }
.rcard ul { width: 100%; list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-1); color: var(--text-2); font-size: var(--fs-footnote); line-height: 1.55; }
.rcard ul li { position: relative; padding-inline-start: .9rem; }
.rcard ul li::before { content: ""; position: absolute; inset-inline-start: 0; top: .6em; width: .35rem; height: .35rem; border-radius: 50%; background: var(--text-3); }

/* CTA and caption previews: the CTA sits on the gold brand ground in ink, its copy button is the system's violet button */
.ctabox { display: grid; gap: var(--sp-4); justify-items: start; border-radius: var(--r-lg); padding: var(--sp-6) var(--sp-5);
  background: var(--glass-sheen), linear-gradient(color-mix(in srgb, var(--accent-soft) 84%, transparent), color-mix(in srgb, var(--accent-soft) 84%, transparent)), var(--glass-card); box-shadow: var(--glass-card-rim), var(--glass-card-lift); color: var(--text); }
.cta-text { font-size: clamp(1.3rem, 3.8vw, 1.65rem); font-weight: 700; line-height: 1.35; letter-spacing: -.015em; color: var(--text); }
.lb-btn { gap: .4rem; }
.lb-btn .ico { width: 1rem; height: 1rem; }
.igpost { border-radius: var(--r-lg); padding: var(--sp-4) var(--sp-5); display: grid; gap: var(--sp-3); max-width: 30rem; box-shadow: var(--shadow-2); }
.ig-head { display: flex; align-items: center; gap: var(--sp-2); }
.av { display: grid; place-items: center; width: 2.1rem; height: 2.1rem; border-radius: 50%; background: var(--surface-2); color: var(--text-3);
  box-shadow: 0 0 0 2px var(--surface), 0 0 0 3.5px var(--accent); overflow: hidden; }
.av.brand { margin-inline-start: -.9rem; background: var(--surface); }
.av.brand img { width: 100%; height: 100%; object-fit: cover; }
.ig-names { font-family: var(--font-2); font-size: var(--fs-callout); color: var(--text-2); }
.ig-names b, .ig-names bdi { font-weight: 700; color: var(--text); }
.ig-body { line-height: 1.65; font-size: var(--fs-callout); color: var(--text); }
.ig-cta { color: var(--accent-ink); }
.ig-foot { display: flex; }
.emailcard { display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-3); border-radius: var(--r-lg); padding: var(--sp-3) var(--sp-4); }
.email { font-weight: 700; font-size: 1.125rem; color: var(--text); unicode-bidi: isolate; user-select: all; }
.email:hover { color: var(--tint); text-decoration: none; }
.emailcard .lb-btn { margin-inline-start: auto; }

.checklist ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); }
.foot { display: flex; align-items: center; gap: var(--sp-2); margin-top: var(--sp-7); padding-top: var(--sp-4); border-top: 1px solid var(--line); font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }
.foot img { height: 1.4rem; width: auto; }
.dots { display: none; align-items: center; justify-content: center; gap: 6px; }
.dots span { font-family: var(--font-2); font-size: var(--fs-caption); color: var(--text-3); margin-inline-end: var(--sp-2); }
.dots i { width: 6px; height: 6px; border-radius: 3px; background: var(--fill-3); }
.dots i.on { width: 18px; background: var(--accent); }
@media (prefers-reduced-motion: no-preference) {
  .lb-btn, .extlink, .menu a, .segctl button, .iconbtn { transition: background .15s ease, color .15s ease, box-shadow .15s ease; }
  .dots i { transition: width .2s ease, background .2s ease; }
}

/* phones: tighter gutter and spacing, the screens and the worked example become swipe rows,
   buttons become full-width 44px targets */
@media (max-width: 640px) {
  .brief { --gutter: var(--sp-4); }
  .cover { padding-block: var(--sp-6) 0; }
  .sec { padding-block-start: var(--sp-6); gap: var(--sp-3); }
  .sec-head .badge { width: 2.1rem; height: 2.1rem; }
  .para { font-size: var(--fs-body); }
  .steps > li { grid-template-columns: 1.75rem minmax(0, 1fr); gap: var(--sp-2); }
  .steps::before { inset-inline-start: .85rem; }
  .node { width: 1.75rem; height: 1.75rem; font-size: var(--fs-footnote); margin-top: .75rem; }
  .step-card { padding: var(--sp-3) var(--sp-4); gap: var(--sp-2); }
  .time { margin-inline-start: 0; flex-basis: 100%; }
  .phones, .board { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; overscroll-behavior-x: contain;
    gap: var(--sp-3); padding-block: 2px var(--sp-1); max-width: none; }
  .phones::-webkit-scrollbar, .board::-webkit-scrollbar { display: none; }
  .reelrow { margin-inline: calc(-1 * var(--gutter)); padding-inline: var(--gutter); }
  .rcard { flex: 0 0 68%; }
  .phones { margin-inline: calc(-1 * var(--sp-4)); padding-inline: var(--sp-4); }
  .phone-wrap { flex: 0 0 60%; scroll-snap-align: center; }
  .phone { max-width: none; }
  .board { margin-inline: calc(-1 * var(--gutter)); padding-inline: var(--gutter); }
  .board > li { flex: 0 0 84%; scroll-snap-align: center; }
  .dots { display: flex; }
  .screens, .card, .tickbox, .igpost { padding: var(--sp-4); }
  .lb-btn.sm { min-height: 2.75rem; padding-inline: var(--sp-4); font-size: var(--fs-callout); }
  .ctabox { padding: var(--sp-5) var(--sp-4); }
  .ctabox .lb-btn, .ig-foot .lb-btn, .emailcard .lb-btn { width: 100%; justify-content: center; margin-inline-start: 0; }
  .ig-foot { display: block; }
  .email { font-size: 1.0625rem; }
  .extlink { min-height: 2.75rem; }
  .lb-brand small { display: none; }
}
@media (max-width: 360px) {
  .lb-brand > span { display: none; }
  .segctl button { padding: 0 .7rem; }
}
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
})();
(function () {
  /* two pages (brief / messages) and the hamburger menu */
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var views = { brief: document.getElementById("view-brief"), messages: document.getElementById("view-messages") };
  var menu = document.getElementById("menu"), scrim = document.getElementById("scrim"), toggle = document.getElementById("menu-btn");
  function show(name, scrollTop) {
    if (!views[name]) name = "brief";
    Object.keys(views).forEach(function (k) { if (views[k]) views[k].hidden = k !== name; });
    document.querySelectorAll(".segctl [data-show]").forEach(function (b) { b.setAttribute("aria-selected", b.getAttribute("data-show") === name ? "true" : "false"); });
    document.querySelectorAll(".menu a[data-show]").forEach(function (a) { a.classList.toggle("is-active", a.getAttribute("data-show") === name); });
    document.querySelectorAll("[data-menu-for]").forEach(function (g) { g.hidden = g.getAttribute("data-menu-for") !== name; });
    if (scrollTop) window.scrollTo(0, 0);
  }
  function setHash(h) { try { history.replaceState(null, "", h || (location.pathname + location.search)); } catch (e) {} }
  function viewOf(id) { var el = id && document.getElementById(id); var v = el && el.closest("[data-view]"); return v ? v.getAttribute("data-view") : null; }
  function setMenu(open) {
    menu.hidden = !open; scrim.hidden = !open;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) { var first = menu.querySelector(".group:not([hidden]) a, a"); if (first) first.focus(); }
  }
  toggle.addEventListener("click", function () { setMenu(menu.hidden); });
  scrim.addEventListener("click", function () { setMenu(false); toggle.focus(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !menu.hidden) { setMenu(false); toggle.focus(); } });
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-show]");
    if (t) {
      e.preventDefault();
      var name = t.getAttribute("data-show");
      show(name, true); setHash(name === "messages" ? "#messages" : "");
      setMenu(false);
      return;
    }
    var a = e.target.closest('.menu a[href^="#"]');
    if (a) {
      e.preventDefault();
      var id = a.getAttribute("href").slice(1), v = viewOf(id);
      if (v && views[v].hidden) show(v, false);
      setMenu(false);
      var el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      setHash("#" + id);
    }
  });
  var h = location.hash.slice(1);
  if (h === "messages") show("messages", false);
  else if (h && viewOf(h)) { show(viewOf(h), false); var el = document.getElementById(h); if (el) el.scrollIntoView(); }
  else show("brief", false);

  /* the section in view is marked in the menu */
  var links = Array.prototype.slice.call(document.querySelectorAll('.menu .group a[href^="#"]'));
  if (links.length && "IntersectionObserver" in window) {
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var a = byId[en.target.id];
        if (!a) return;
        links.forEach(function (l) { if (l.parentNode === a.parentNode) l.classList.toggle("is-active", l === a); });
      });
    }, { rootMargin: "-30% 0px -65% 0px" });
    document.querySelectorAll(".sec[id]").forEach(function (s) { io.observe(s); });
  }

  /* swipe rows on phones: the dot under the card nearest the middle */
  document.querySelectorAll("[data-carousel]").forEach(function (row) {
    var dots = row.nextElementSibling && row.nextElementSibling.classList.contains("dots") ? row.nextElementSibling.querySelectorAll("i") : [];
    if (!dots.length) return;
    function update() {
      var rr = row.getBoundingClientRect(), mid = rr.left + rr.width / 2, best = 0, bestD = Infinity;
      Array.prototype.forEach.call(row.children, function (c, i) {
        var cr = c.getBoundingClientRect(), d = Math.abs(cr.left + cr.width / 2 - mid);
        if (d < bestD) { bestD = d; best = i; }
      });
      Array.prototype.forEach.call(dots, function (d, i) { d.classList.toggle("on", i === best); });
    }
    row.addEventListener("scroll", update, { passive: true });
    Array.prototype.forEach.call(row.nextElementSibling.querySelectorAll("[data-step]"), function (b) {
      b.addEventListener("click", function () {
        var on = Array.prototype.indexOf.call(dots, row.nextElementSibling.querySelector("i.on"));
        var c = row.children[Math.max(0, Math.min(row.children.length - 1, on + Number(b.getAttribute("data-step"))))];
        row.scrollTo({ left: row.scrollLeft + c.getBoundingClientRect().left + c.offsetWidth / 2 - row.getBoundingClientRect().left - row.clientWidth / 2, behavior: "smooth" });
      });
    });
    window.addEventListener("resize", update);
    update();
  });
})();
(function () {
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


def render_page(name, sections, ctx, prefix):
    hero, rest = sections[0], sections[1:]
    lede = "".join(f'<p class="lede">{br(it["lines"])}</p>' for it in hero["items"] if it["type"] == "para")
    cover = (f'<header class="cover"><span class="eyebrow">{UI["brand"]}</span><h1>{inline(hero["title"])}</h1>{lede}</header>')
    body = []
    for n, s in enumerate(rest, 1):
        body.append(f'<section class="sec" id="{prefix}{n}"><div class="sec-head"><span class="badge">{icon(s["icon"])}</span>'
                    f'<h2>{inline(s["title"])}</h2></div>\n{render_items(s["items"], f"{prefix}{n}", ctx)}\n</section>')
    hidden = "" if name == "brief" else " hidden"
    main = (f'<main class="lb-page brief" id="view-{name}" data-view="{name}" dir="rtl" lang="he"{hidden}>\n{cover}\n'
            + "\n".join(body)
            + f'\n<footer class="foot"><img src="{ctx["logo"]}" alt=""><span>{UI["brand"]} · {UI["brand_sub"]}</span></footer>\n</main>')
    links = "".join(f'<a href="#{prefix}{n}">{icon(s["icon"])}<span>{inline(s["title"])}</span></a>' for n, s in enumerate(rest, 1))
    group = f'<div class="group" data-menu-for="{name}"{hidden}><h2>{UI["toc"]}</h2>{links}</div>'
    return main, group


def build():
    # Share crawlers need a public raster URL, not an embedded data URI.
    # Keep this copy in the normal build so a later rebuild preserves previews.
    if not PREVIEW.is_file():
        raise FileNotFoundError(f"Missing share card: {PREVIEW}")
    md = BRIEF.read_text(encoding="utf-8")
    pages = parse()
    brief = pages["brief"]
    spans = re.findall(r"`([^`]+)`", md[md.index('<div dir="rtl"'):])
    examples = find(brief, "example")
    ctas = [it for it in find(brief, "copy") if it["role"] == "cta"]
    ctx = {
        "logo": design.logo_data_uri(),
        "handle": next((s for s in spans if s.startswith("@lumebook")), "@lumebook.il"),
        "email": next((s for s in spans if "@" in s and not s.startswith("@")), ""),
        "creator": next((s for s in spans if s.startswith("@") and not s.startswith("@lumebook")), ""),
        "hook": unquote(examples[0]["lines"][0]) if examples else "",
        "cta": plain(ctas[0]["lines"]) if ctas else "",
    }
    mains, groups = [], []
    for name, prefix in (("brief", "s"), ("messages", "m")):
        if pages[name]:
            m, g = render_page(name, pages[name], ctx, prefix)
            mains.append(m); groups.append(g)
    has_messages = bool(pages["messages"])
    segctl = ""
    page_links = ""
    if has_messages:
        segctl = (f'<div class="segctl" role="tablist" aria-label="{UI["views_label"]}">'
                  f'<button type="button" role="tab" data-show="brief" aria-selected="true" aria-controls="view-brief">{UI["view_brief"]}</button>'
                  f'<button type="button" role="tab" data-show="messages" aria-selected="false" aria-controls="view-messages">{UI["view_messages"]}</button></div>')
        page_links = (f'<h2>{UI["views_label"]}</h2>'
                      f'<a href="#" data-show="brief" class="is-active">{icon("film")}<span>{UI["view_brief"]}</span></a>'
                      f'<a href="#messages" data-show="messages">{icon("message")}<span>{UI["view_messages"]}</span></a><hr>')
    js = (PAGE_JS.replace("__COPIED__", repr(UI["copied"])).replace("__OF__", repr(UI["checked_of"]))
          .replace("__FALLBACK__", repr(UI["copy_fallback"].replace("\n", " "))))
    page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
{design.head(nav=False)}
<meta name="theme-color" content="#FFFFFF">
{RTL_BOOT}
<style>{PAGE_CSS}</style>

<header class="lb-topbar" dir="rtl" lang="he">
  <div class="lb-topbar-in">
    <span class="lb-brand"><img src="{ctx["logo"]}" alt=""><span><b>{UI["brand"]}</b><small>{UI["brand_sub"]}</small></span></span>
    <div class="top-actions">{segctl}<button class="iconbtn" id="menu-btn" type="button" aria-expanded="false" aria-controls="menu" aria-label="{UI["menu"]}">{icon("menu", "ico i-open")}{icon("x", "ico i-close")}</button></div>
  </div>
</header>
<div class="scrim" id="scrim" hidden></div>
<nav class="menu" id="menu" dir="rtl" lang="he" aria-label="{UI["menu"]}" hidden>{page_links}{"".join(groups)}</nav>

{chr(10).join(mains)}
{js}"""
    OUT.write_text(page, encoding="utf-8")
    cut = page.index('<header class="lb-topbar"')
    head = page[:cut].replace("<title>", (
        '<meta name="robots" content="noindex">\n'
        f'<meta name="description" content="{html.escape(UI["og_description"], quote=True)}">\n'
        f'<link rel="canonical" href="{SITE_URL}">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:site_name" content="LumeBook">\n'
        f'<meta property="og:url" content="{SITE_URL}">\n'
        f'<meta property="og:title" content="{TITLE}">\n'
        f'<meta property="og:description" content="{UI["og_description"]}">\n'
        '<meta property="og:locale" content="he_IL">\n'
        f'<meta property="og:image" content="{SITE_URL}{PREVIEW_PATH}">\n'
        f'<meta property="og:image:secure_url" content="{SITE_URL}{PREVIEW_PATH}">\n'
        '<meta property="og:image:type" content="image/jpeg">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        f'<meta property="og:image:alt" content="{TITLE}">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{TITLE}">\n'
        f'<meta name="twitter:description" content="{UI["og_description"]}">\n'
        f'<meta name="twitter:image" content="{SITE_URL}{PREVIEW_PATH}">\n'
        f'<meta name="twitter:image:alt" content="{TITLE}">\n<title>'), 1)
    SITE.parent.mkdir(parents=True, exist_ok=True)
    preview_dst = SITE.parent / PREVIEW_PATH
    preview_dst.parent.mkdir(parents=True, exist_ok=True)
    if not preview_dst.exists() or preview_dst.read_bytes() != PREVIEW.read_bytes():
        shutil.copy2(PREVIEW, preview_dst)
    cards = [it["slug"] for sec in pages["brief"] for it in sec["items"] if it["type"] == "reelcard"]
    for rel in [*REEL.values(), *(r for slug in cards for r in reel_files(slug).values())]:  # web files sit next to the Vercel page
        src, dst = REEL_DIR / Path(rel).name, SITE.parent / rel
        if src.exists() and (not dst.exists() or dst.read_bytes() != src.read_bytes()):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    SITE.write_text(f'<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n{head.rstrip()}\n</head>\n<body>\n{page[cut:].strip()}\n</body>\n</html>\n',
                    encoding="utf-8")
    n = sum(len(v) - 1 for v in pages.values() if v)
    print(f"wrote {OUT.relative_to(ROOT)} and {SITE.relative_to(ROOT)} ({len(page) // 1024} KB, {n} sections on {len(mains)} pages)")


if __name__ == "__main__":
    build()
