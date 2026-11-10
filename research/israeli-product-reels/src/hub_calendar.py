"""The November reel calendar as parts for the Reels hub page (Yarin, 05 Nov 2026: one tool for everything about reels).

build_page.py (series-2026-11) still builds the stand-alone calendar page. This module runs it, cuts the page
into parts and adapts them so they live inside the hub: the month grid and its filters render inside the
"לוח חודשי" view, the popup with the editable reel card, the toolbar and the comment box sit at page level, and
the script is patched to work with a view that is drawn again each time (delegated clicks, a mount() call).
Edits, ticks and comment requests save to the hub's own artifact database ("edits", "made", "requests"),
the same collections the stand-alone page used, so reels.py merge works on either.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERIES = HERE / "scripts" / "series-2026-11"
sys.path.insert(0, str(SERIES))
import build_page  # noqa: E402


def _between(h, start, end, include_end=True):
    a = h.index(start)
    b = h.index(end, a) + (len(end) if include_end else 0)
    return h[a:b]


def _sub1(s, old, new, what):
    if s.count(old) != 1:
        raise SystemExit(f"hub_calendar: cannot patch {what}: found {s.count(old)} times")
    return s.replace(old, new)


def parts(d):
    h = build_page.page(d)
    reels = {build_page.rid(r): r for r in d["reels"]}

    # ---- css: the page's own style block, with the two class names the hub also uses renamed
    css = h[h.index("<style>\n/* Layout: a sticky bar"):]
    css = css[len("<style>"):css.index("</style>")]
    css = css.replace(".filters {", ".cfilters {").replace(".meta {", ".cmeta {")
    css = re.sub(r"^body \{[^}]*\}\n", "", css, flags=re.M)          # the hub sets its own body
    css = re.sub(r"^body::before \{[^}]*\}\n", "", css, flags=re.M)  # and its own safe-area band
    css = re.sub(r"^\.lb-topbar-in, \.lb-page \{[^}]*\}\n", "", css, flags=re.M)  # the hub pads its own
    css = re.sub(r"^\.lb-topbar-in \.sp \{[^}]*\}\n", "", css, flags=re.M)
    css = re.sub(r"^\.lb-topbar-in \.sub \{[^}]*\}\n", "", css, flags=re.M)
    css = css.replace("  .lb-topbar-in .sub { display: none; }\n", "")
    css = css.replace(".intro { display: grid; gap: var(--sp-3); }", "")

    # ---- the view: brief, legend, filters, month grid
    brief = _between(h, '<section class="brief"', "</section>")
    legend = _between(h, '<div class="legend">', "</div>\n    </div>").rsplit("\n    </div>", 1)[0]
    filters = _between(h, '<div class="filters"', "</div>\n    <div class=\"lb-month\">").rsplit('\n    <div class="lb-month">', 1)[0]
    filters = filters.replace('class="filters"', 'class="cfilters"').replace("data-f=", "data-cf=")
    # approach chips, so the playbook's "N reels use it" button can filter the grid
    grid = _between(h, '<div class="lb-month">', "</div>\n  </section>").rsplit("\n  </section>", 1)[0]

    def add_ap(m):
        k = m.group(1)
        r = reels.get(k)
        return f'data-k="{k}" data-ap="{r["approach"] if r else ""}"'
    grid = re.sub(r'data-k="(r[\w-]+)"', add_ap, grid)

    # ---- page level: cards (hidden holder), dialog with toolbar and comment box, ask config
    cards = _between(h, '<div id="cards" hidden>', "</div>\n<dialog", include_end=False)
    cards = cards + "</div>"
    cards = cards.replace('data-copy="', 'data-ccopy="').replace('class="meta"', 'class="cmeta"')
    dialog = _between(h, "<dialog", "</dialog>")
    ask_cfg = _between(h, '<script type="application/json" id="ask-cfg">', "</script>")

    # ---- script
    js = build_page.SCRIPT
    js = _sub1(js, '''  var btns = $$(".filters [data-f]");
  function applyFilter(f) {
    btns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.f === f)); });
    $$(".lb-day[data-series]").forEach(function (el) {
      var hit = f === "all" || (f === "grandma" ? el.dataset.aud === "grandma" : el.dataset.series === f);
      el.classList.toggle("is-dim", !hit);
    });
    try { localStorage.setItem(KEY_F, f); } catch (x) {}
  }
  btns.forEach(function (b) { b.addEventListener("click", function () { applyFilter(b.dataset.f); }); });
  var savedF = "all";
  try { savedF = localStorage.getItem(KEY_F) || "all"; } catch (x) {}
  if ($('.filters [data-f="' + savedF + '"]')) applyFilter(savedF);
''', '''  function applyFilter(f) {
    $$("#calRoot [data-cf]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.cf === f)); });
    $$("#calRoot .lb-day[data-series]").forEach(function (el) {
      var hit = f === "all" || (f === "grandma" ? el.dataset.aud === "grandma" : f.indexOf("ap:") === 0 ? el.dataset.ap === f.slice(3) : el.dataset.series === f);
      el.classList.toggle("is-dim", !hit);
    });
    var note = $("#calApNote"); if (note) { note.hidden = f.indexOf("ap:") !== 0; if (!note.hidden) $("b", note).textContent = f.slice(3); }
    try { localStorage.setItem(KEY_F, f); } catch (x) {}
  }
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest && ev.target.closest("#calRoot [data-cf]"); if (b) applyFilter(b.dataset.cf);
  });
''', "filter block")
    js = _sub1(js, '''  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var el = document.getElementById(b.dataset.copy);
      var done = function () { b.textContent = "הועתק"; setTimeout(function () { b.textContent = "העתקה"; }, 1600); };''',
               '''  $$("[data-ccopy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var el = document.getElementById(b.dataset.ccopy);
      var done = function () { b.textContent = "הועתק"; setTimeout(function () { b.textContent = "העתקה"; }, 1600); };''', "copy buttons")
    js = _sub1(js, 'try { history.replaceState(null, "", "#" + id); } catch (x) {}', 'try { history.replaceState(null, "", "#calendar/" + id); } catch (x) {}', "open hash")
    js = _sub1(js, 'try { history.replaceState(null, "", location.pathname + location.search); } catch (x) {}',
               'try { if (/^#calendar\\//.test(location.hash)) history.replaceState(null, "", "#calendar"); } catch (x) {}', "close hash")  # leaving the month closes the drawer: keep the new hash
    js = _sub1(js, '''  $$("a.lb-day[data-k]").forEach(function (c) { c.addEventListener("click", function (ev) { ev.preventDefault(); openReel(c.dataset.k); }); });
  if (location.hash.length > 1) openReel(decodeURIComponent(location.hash.slice(1)));
''', '''  document.addEventListener("click", function (ev) {
    var c = ev.target.closest && ev.target.closest("a.lb-day[data-k]"); if (c) { ev.preventDefault(); openReel(c.dataset.k); }
  });
''', "cell clicks")
    js = _sub1(js, '''})();
</script>''', '''  /* the hub draws the view again each time it is opened: call mount() after it is in the page */
  window.CalMount = function () {
    var f = "all"; try { f = localStorage.getItem(KEY_F) || "all"; } catch (x) {}
    if (f !== "all" && f.indexOf("ap:") !== 0 && !$('#calRoot [data-cf="' + f + '"]')) f = "all";
    applyFilter(f);
    Object.keys(fields).forEach(syncHook);
    $$("[data-made]").forEach(function (b) { paintMade(b.dataset.made); });
    if (window.CalPicksPaint) CalPicksPaint();   /* two options a day (10 Nov 2026): fade the option not picked */
    if (window.CalJobsPaint) CalJobsPaint();
    var m = /^#calendar\\/(r[\\w-]+)$/.exec(decodeURIComponent(location.hash)); if (m) openReel(m[1]);
  };
  window.CalOpen = openReel;
  window.CalFilter = applyFilter;
})();
</script>''', "end of script")
    return {"css": css, "brief": brief, "legend": legend, "filters": filters, "grid": grid,
            "cards": cards, "dialog": dialog, "ask_cfg": ask_cfg, "js": js}


if __name__ == "__main__":
    d = json.loads((SERIES / "reels.json").read_text())
    p = parts(d)
    for k, v in p.items():
        print(f"{k:8} {len(v):7}")
