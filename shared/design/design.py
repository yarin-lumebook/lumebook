"""LumeBook design system helpers for page builds.

Every internal page build inlines the same stylesheet, fonts link and theme script, so one edit to
shared/design/lumebook.css restyles them all on the next `python3 tools/lumebook.py ripple`.

    import sys, pathlib
    sys.path.insert(0, str(<project root> / "shared" / "design"))
    import design
    html = html.replace("<!--LB:HEAD-->", design.head())       # in <head> or at the top of an artifact page
    html = html.replace("<!--LB:THEME-TOGGLE-->", design.theme_toggle())   # the white/black switch, in the top bar
    design.cat_class("reels-tools", "hook")   # "lb-cat-1": the category colour class for one key

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

# White and black modes with a switch (Yarin, 21 Oct 2026). The boot script runs in <head>: it sets data-theme on
# <html> before first paint from the viewer's saved choice (localStorage "lb-mode", white by default; not "lb-theme", which old built pages still clear), flips it when any
# [data-lb-theme-toggle] is clicked, keeps aria-checked on every switch in step and follows a change made in another tab.
# The dashboard and the SMM plan (no build) carry a copy of this same script in their <head>.
THEME_BOOT = (
    '<script>(function(){if(window.lbThemeBoot)return;window.lbThemeBoot=1;var d=document.documentElement,K="lb-mode";'
    'function saved(){try{return localStorage.getItem(K)==="dark"?"dark":"light"}catch(e){return"light"}}'
    'function set(t){d.setAttribute("data-theme",t);var s=document.querySelectorAll("[data-lb-theme-toggle]");'
    'for(var i=0;i<s.length;i++)s[i].setAttribute("aria-checked",String(t==="dark"))}'
    'set(saved());document.addEventListener("DOMContentLoaded",function(){set(d.getAttribute("data-theme"))});'
    'document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("[data-lb-theme-toggle]");if(!b)return;'
    'var t=d.getAttribute("data-theme")==="dark"?"light":"dark";set(t);try{localStorage.setItem(K,t)}catch(x){}});'
    'addEventListener("storage",function(e){if(e.key===K)set(saved())})})()</script>'
)

SUN = ('<svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/>'
       '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')
MOON = '<svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'


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


def head(include_fonts=True, theme=True):
    """Fonts link + the whole design system inline + the theme boot script. theme=False leaves the boot script out, for a
    page with its own modes (the public creator brief) that must never pick up data-theme="dark"."""
    parts = []
    if include_fonts:
        parts += ['<link rel="preconnect" href="https://fonts.googleapis.com">',
                  '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
                  f'<link rel="stylesheet" href="{FONTS_URL}">']
    parts += ([THEME_BOOT] if theme else []) + [local_links_script(), "<style>\n" + css() + "\n" + categories_css() + "\n</style>"]
    return "\n".join(parts)


def theme_toggle(dark_label="מצב כהה", light_label=None):
    """The white/black switch for a page's top bar. light_label is unused (kept so existing builds still run): a switch
    has one label, for its on state."""
    return (f'<button class="lb-theme-switch" type="button" role="switch" aria-checked="false" data-lb-theme-toggle '
            f'aria-label="{dark_label}" title="{dark_label}">{SUN}{MOON}</button>')


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


if __name__ == "__main__":
    print("categories.css " + ("written" if write_categories_css() else "unchanged"))
