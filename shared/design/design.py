"""LumeBook design system helpers for page builds.

Every internal page build inlines the same stylesheet and fonts link, so one edit to
shared/design/lumebook.css restyles them all on the next `python3 tools/lumebook.py ripple`.

    import sys, pathlib
    sys.path.insert(0, str(<project root> / "shared" / "design"))
    import design
    html = html.replace("<!--LB:HEAD-->", design.head())       # in <head> or at the top of an artifact page
    design.cat_class("reels-tools", "hook")   # "lb-cat-1": the category colour class for one key
    design.icon("people")                     # one icon of the set in shared/design/icons.json, as inline <svg>
    design.head(nav=False)                    # without the project nav (only pages people outside LumeBook see)

Category colours: shared/design/categories.json says which category of which page gets which of the eight hues
(--cat-1 ... --cat-8 in lumebook.css). Builds read it through categories(), cat_class() and category_css(), never hexes.

Standard library only.
"""
import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# Heebo is the main font (headings included), Assistant the secondary one (labels, captions, counts); Yarin, 18 Oct 2026.
FONTS_URL = "https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&family=Assistant:wght@400;500;600;700&display=swap"
CATEGORIES = os.path.join(HERE, "categories.json")

# White only (Yarin, 05 Nov 2026: "only white mode from now on"). The black mode, its switch and the boot script that set
# data-theme from localStorage "lb-mode" (21 Oct 2026) are gone: pages carry no theme script and no switch.


def css():
    with open(os.path.join(HERE, "lumebook.css"), encoding="utf-8") as f:
        return f.read()


LOCAL_DASHBOARD = "/sites/dashboard/site/lumebook-dashboard/"


def local_links():
    """{artifact URL: path on the project server} for every artifact that has a built page (lumebook.json publish.file),
    plus the dashboard (its built site). On the project server (localhost:8780) the pages swap these links for the local page: a tab opened from a
    sandboxed artifact is blocked by claude.ai (20 Oct 2026)."""
    out = {}
    try:
        with open(os.path.join(ROOT, "lumebook.json"), encoding="utf-8") as f:
            comps = json.load(f)["components"]
    except (OSError, ValueError, KeyError):
        return out
    for c in comps.values():
        pub = c.get("publish") or {}
        if pub.get("type") == "artifact" and pub.get("url") and str(pub.get("file", "")).lower().endswith((".html", ".htm")):
            out[pub["url"]] = "/" + pub["file"]
    for c in comps.values():
        if c.get("kind") == "dashboard" and (c.get("publish") or {}).get("url"):
            out[c["publish"]["url"]] = LOCAL_DASHBOARD
    return out


def local_links_script():
    m = json.dumps(local_links(), ensure_ascii=False, separators=(",", ":"))
    return ('<script>document.addEventListener("DOMContentLoaded",function(){if(!/^(localhost|127\\.0\\.0\\.1)$/.test(location.hostname)||location.port!=="8780")return;'
            'var m=' + m + ';document.querySelectorAll("a[href]").forEach(function(a){var h=a.getAttribute("href");if(m[h])a.setAttribute("href",m[h])})})</script>')


def head(include_fonts=True, theme=None, nav=True, page=None):
    """Fonts link + the whole design system inline (+ the local-links script) + the project nav (nav.js, 5 Nov 2026).
    White only since 05 Nov 2026: there is no theme script any more; `theme` is accepted and ignored so older builds still run.
    nav=False leaves the project nav out: only for pages people outside LumeBook see (the creator brief).
    page is this page's path in the project ("research/x/page.html"), so the nav knows where it is inside a claude.ai
    artifact too; inside `lumebook.py build` it comes from the component being built (LB_PAGE_FILE)."""
    parts = []
    if include_fonts:
        parts += ['<link rel="preconnect" href="https://fonts.googleapis.com">',
                  '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
                  f'<link rel="stylesheet" href="{FONTS_URL}">']
    parts += [local_links_script(), "<style>\n" + css() + "\n" + categories_css() + "\n</style>"]
    if nav:
        page = page or os.environ.get("LB_PAGE_FILE")
        if page:
            parts.append("<script>window.LB_PAGE=" + _js({"file": page}) + ";</script>")
        parts.append("<script>\n" + nav_js() + "</script>")
    return "\n".join(parts)


def theme_toggle(*args, **kwargs):
    """Retired with the black mode (05 Nov 2026): returns "" so a build that still calls it gets no switch. Don't add new calls."""
    return ""


def logo_data_uri(name="logo_square_96.png"):
    """Brand mark from shared/brand as a data: URI (artifacts cannot load local files). The 96px copy (11 KB) is plenty for a 28-32px top-bar mark."""
    with open(os.path.join(ROOT, "shared", "brand", name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def categories(set_id):
    """One category set from categories.json as {key: {"cat": 1-8, "label": ..., ...}}, in reading order."""
    sets = _sets()
    if set_id not in sets:
        raise KeyError(f"categories.json has no set {set_id!r} (sets: {', '.join(sets)})")
    return sets[set_id]["items"]


def cat_class(set_id, key, default=0):
    """The lb-cat-N class for one key of a set; lb-cat-0 (neutral) for a key the set does not list."""
    item = categories(set_id).get(key)
    return f"lb-cat-{item['cat'] if item else default}"


def _sets():
    with open(CATEGORIES, encoding="utf-8") as f:
        return json.load(f)["sets"]


def _vars(n):
    if not n:  # 0: neutral ink, the same values as .lb-cat-0
        return "--tc: var(--text); --tc-ink: var(--text); --tc-soft: var(--fill);"
    return f"--tc: var(--cat-{n}); --tc-ink: var(--cat-{n}-ink); --tc-soft: var(--cat-{n}-soft);"


def categories_css():
    """One class per category of every set that names a class: .lb-ws-creators { --tc: var(--cat-2); ... }.
    design.head() inlines it; pages without a build link the categories.css that write_categories_css() makes."""
    lines = ["/* category classes, generated from shared/design/categories.json by design.py: do not edit */"]
    for set_id, st in _sets().items():
        if st.get("class"):
            lines += [f".lb-{st['class']}-{key} {{ {_vars(item['cat'])} }}" for key, item in st["items"].items()]
    return "\n".join(lines)


def write_categories_css():
    """Write shared/design/categories.css (for the linked copies); returns True when the file changed."""
    path = os.path.join(HERE, "categories.css")
    text = categories_css() + "\n"
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return old != text


def category_css(set_id, selector=".t-{key}"):
    """Alias rules for a page whose own code already names its categories (the playbook's .t-hook and so on):
    `.t-hook { --tc: var(--cat-1); --tc-ink: var(--cat-1-ink); --tc-soft: var(--cat-1-soft); }` for every key."""
    return "\n".join(f"{selector.format(key=key)} {{ {_vars(item['cat'])} }}" for key, item in categories(set_id).items())


ICONS = os.path.join(HERE, "icons.json")
SVG_ATTRS = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'


def icons(group="icons"):
    """One group of the icon set in icons.json as {name: inner svg markup} (24 grid line icons, 5 Nov 2026):
    "icons" (pictures for tools and topics) or "ui" (interface glyphs)."""
    with open(ICONS, encoding="utf-8") as f:
        return {k: v["svg"] for k, v in json.load(f).get(group, {}).items()}


def ui_icons():
    return icons("ui")


def icon(name, cls="", label=None):
    """One icon as inline <svg>; decorative (aria-hidden) unless a label is given."""
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return f'<svg{f" class=\"{cls}\"" if cls else ""} {SVG_ATTRS} {a11y}>{({**icons(), **ui_icons()})[name]}</svg>'


def icons_js():
    """window.LB_ICONS for pages without a build (the dashboard links the synced copy design/icons.js)."""
    return ("/* the LumeBook icon set, generated from shared/design/icons.json by design.py: do not edit */\n"
            "window.LB_ICONS = " + json.dumps(icons(), ensure_ascii=False, indent=0) + ";\n"
            "window.LB_UI_ICONS = " + json.dumps(ui_icons(), ensure_ascii=False, indent=0) + ";\n")


def write_icons_js():
    """Write shared/design/icons.js (for the linked copies); returns True when the file changed."""
    path = os.path.join(HERE, "icons.js")
    text = icons_js()
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return old != text


# ---------- the project nav (5 Nov 2026) ----------
# hq-tools.json is HQ's built-in tool list; nav.src.js draws the top bar (HQ's topics), the location path, the side bar
# (every tool) and the bottom nav bar on phones. nav_js() puts the data in front of the script; builds inline it through
# head(), and write_nav_js() writes shared/design/nav.js for the pages without a build (HQ, the SMM plan), which sync copies.
HQ_TOOLS = os.path.join(HERE, "hq-tools.json")
NAV_SRC = os.path.join(HERE, "nav.src.js")
HQ_LOCAL = "sites/dashboard/site/lumebook-dashboard/"   # HQ on the project server (its built copy; "/" redirects there)


def _js(obj):
    """JSON safe inside an inline <script>."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _read_json(*parts, default=None):
    try:
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def nav_data():
    """window.LB_NAV_DATA: the topics and tools (hq-tools.json, each topic's hue from categories.json set workstreams),
    the icons, the logo, where HQ is (project server, artifact, Vercel), the Vercel copies of research artifacts
    (facts.json artifacts with a web address), each built page's artifact id (lumebook.json publish) and HQ's saved
    arrangement (sites/dashboard/hq-layout.json)."""
    with open(HQ_TOOLS, encoding="utf-8") as f:
        topics = json.load(f)["topics"]
    ws = _sets().get("workstreams", {}).get("items", {})
    topics = [dict(t, cat=(ws.get(t["id"]) or {}).get("cat", 0)) for t in topics]
    facts = _read_json("shared", "facts.json", default={})
    comps = (_read_json("lumebook.json", default={}) or {}).get("components", {})
    dash = next((s.get("url") for s in facts.get("sites", []) if s.get("key") == "dash"), "https://lumebook-dashboard.vercel.app")
    hq_art = ((comps.get("dashboard") or {}).get("publish") or {}).get("url", "")
    webs = {a["url"].rstrip("/").split("/")[-1]: a["web"] for a in facts.get("artifacts", []) if a.get("web") and a.get("url")}
    saved = _read_json("sites", "dashboard", "hq-layout.json")
    # built page → its artifact id, for a tool whose local address is not the built file (Carousel Machine: hook-studio/)
    pages = {c["publish"]["file"]: c["publish"]["url"].rstrip("/").split("/")[-1] for c in comps.values()
             if (c.get("publish") or {}).get("type") == "artifact" and str(c["publish"].get("file", "")).endswith(".html")}
    return {"topics": topics, "icons": icons(), "ui": ui_icons(), "logo": logo_data_uri(),
            "hq": {"local": HQ_LOCAL, "artifact": hq_art, "web": dash.rstrip("/") + "/"},
            "web_copies": webs, "pages": pages, "saved": saved if isinstance(saved, dict) and not saved.get("default") else None}


def nav_js():
    with open(NAV_SRC, encoding="utf-8") as f:
        src = f.read()
    return ("/* the LumeBook project nav, generated by shared/design/design.py from hq-tools.json and nav.src.js: do not edit */\n"
            "window.LB_NAV_DATA = " + _js(nav_data()) + ";\n" + src)


def write_nav_js():
    """Write shared/design/nav.js (for the linked copies); returns True when the file changed."""
    path = os.path.join(HERE, "nav.js")
    text = nav_js()
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return old != text


if __name__ == "__main__":
    print("categories.css " + ("written" if write_categories_css() else "unchanged"))
    print("icons.js " + ("written" if write_icons_js() else "unchanged"))
    print("nav.js " + ("written" if write_nav_js() else "unchanged"))
