"""LumeBook design system helpers for page builds.

Every internal page build inlines the same stylesheet, fonts link and theme script, so one edit to
shared/design/lumebook.css restyles them all on the next `python3 tools/lumebook.py ripple`.

    import sys, pathlib
    sys.path.insert(0, str(<project root> / "shared" / "design"))
    import design
    html = html.replace("<!--LB:HEAD-->", design.head())       # in <head> or at the top of an artifact page
    html = html.replace("<!--LB:THEME-TOGGLE-->", design.theme_toggle())

Standard library only.
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

FONTS_URL = "https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&family=Varela+Round&display=swap"

# Sets data-theme on <html> before first paint: the viewer's saved choice, light by default (Yarin's choice).
THEME_BOOT = ('<script>(function(){var t="light";try{t=localStorage.getItem("lb-theme")||"light"}catch(e){}'
              'document.documentElement.setAttribute("data-theme",t)})();</script>')

THEME_JS = """<script>
(function () {
  function sync(btn) {
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    btn.setAttribute("aria-pressed", String(dark));
    btn.title = dark ? btn.dataset.light : btn.dataset.dark;
    btn.querySelector(".lb-theme-label") && (btn.querySelector(".lb-theme-label").textContent = btn.title);
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-lb-theme-toggle]");
    if (!btn) return;
    var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("lb-theme", next); } catch (err) {}
    document.querySelectorAll("[data-lb-theme-toggle]").forEach(sync);
  });
  document.querySelectorAll("[data-lb-theme-toggle]").forEach(sync);
})();
</script>"""


def css():
    with open(os.path.join(HERE, "lumebook.css"), encoding="utf-8") as f:
        return f.read()


def head(include_fonts=True):
    """Fonts link + the whole design system inline + the theme boot script."""
    parts = []
    if include_fonts:
        parts += ['<link rel="preconnect" href="https://fonts.googleapis.com">',
                  '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
                  f'<link rel="stylesheet" href="{FONTS_URL}">']
    parts += [THEME_BOOT, "<style>\n" + css() + "\n</style>"]
    return "\n".join(parts)


def theme_toggle(dark_label="מצב כהה", light_label="מצב בהיר"):
    """A theme button plus its script. Put it once per page."""
    icon = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
            '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')
    return (f'<button class="lb-btn secondary sm" type="button" data-lb-theme-toggle data-dark="{dark_label}" '
            f'data-light="{light_label}" aria-pressed="false">{icon}<span class="lb-theme-label">{dark_label}</span></button>'
            + THEME_JS)


def logo_data_uri(name="logo_square_96.png"):
    """Brand mark from shared/brand as a data: URI (artifacts cannot load local files). The 96px copy (11 KB) is plenty for a 28-32px top-bar mark."""
    with open(os.path.join(ROOT, "shared", "brand", name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()
