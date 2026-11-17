/*!
 * LumeBook edit button: the round pencil at the bottom left of every page the project server shows (localhost:8780).
 * Press it to edit the page right where it is: text, colors, pictures, sizes and spacing, drag things around.
 * "Done" puts the button back. The editor (editor.js) loads only when the button is pressed.
 * Source: shared/site-editor/loader.js (README there). Never part of a page's file; the server adds it when serving.
 */
(() => {
  "use strict";
  if (window.__lbEditButton || window.top !== window || !document.body) return;
  const me = document.currentScript;
  const cfg = { page: me.dataset.page || "", mode: me.dataset.mode || "layer", note: me.dataset.note || "", file: me.dataset.file || "" };
  const BASE = me.src.replace(/loader\.js(\?.*)?$/, "");

  const host = document.createElement("div");
  host.setAttribute("data-lb-ui", "");
  host.style.cssText = "all: initial !important; position: fixed !important; left: 0 !important; bottom: 0 !important; width: 0 !important; height: 0 !important; z-index: 2147482999 !important; display: block !important;";
  const shadow = host.attachShadow({ mode: "open" });
  shadow.innerHTML = `<style>
:host { all: initial; }
/* no scrollbars, ever (Yarin, 08 Nov 2026) */
*, *::before, *::after { scrollbar-width: none !important; }
::-webkit-scrollbar { display: none !important; width: 0 !important; height: 0 !important; }
button {
  position: fixed; left: 16px; bottom: max(16px, env(safe-area-inset-bottom)); display: inline-flex; align-items: center; gap: 0;
  height: 44px; min-width: 44px; padding: 0 12px; border: 0; border-radius: 999px; color: #1d1d1f; cursor: pointer; direction: ltr;
  /* Liquid Glass (7 Nov 2026): translucent white over a blurred copy of the page, a bright top edge, a soft lift */
  background: radial-gradient(130% 160% at 14% -30%, rgb(255 255 255 / 80%), rgb(255 255 255 / 0%) 58%), rgb(255 255 255 / 70%);
  -webkit-backdrop-filter: saturate(190%) blur(24px); backdrop-filter: saturate(190%) blur(24px);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 95%), inset 0 -1px 0 rgb(0 0 0 / 5%), inset 0 0 0 1px rgb(43 36 29 / 9%), 0 12px 30px -10px rgb(0 0 0 / 26%), 0 1px 3px rgb(0 0 0 / 10%);
  font: 600 13px/1 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; opacity: .94; transition: opacity .14s, transform .24s cubic-bezier(.34, 1.45, .64, 1);
}
button:hover, button:focus-visible { opacity: 1; }
button:active { transform: scale(.96); }
@media (prefers-reduced-motion: reduce) { button:active { transform: none; } }
button:focus-visible { outline: 2px solid #0a64c8; outline-offset: 2px; }
svg { width: 18px; height: 18px; flex: none; fill: none; stroke: currentColor; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
span { max-width: 0; overflow: hidden; white-space: nowrap; transition: max-width .2s, margin .2s; }
button:hover span, button:focus-visible span, button[aria-busy="true"] span { max-width: 9em; margin-left: 8px; }
button[hidden] { display: none; }
/* dark mode (16 Nov 2026): the same glass, dark, following the system appearance like the pages */
@media (prefers-color-scheme: dark) {
  button { color: #f5f5f7; background: radial-gradient(130% 160% at 14% -30%, rgb(255 255 255 / 10%), rgb(255 255 255 / 0%) 58%), rgb(44 44 44 / 72%);
    box-shadow: inset 0 1px 0 rgb(255 255 255 / 14%), inset 0 -1px 0 rgb(0 0 0 / 40%), inset 0 0 0 1px rgb(255 255 255 / 9%), 0 12px 30px -10px rgb(0 0 0 / 70%), 0 1px 3px rgb(0 0 0 / 45%); }
  button:focus-visible { outline-color: #0a84ff; }
}
@media print { :host { display: none !important; } }
</style><button type="button" title="Edit this page" aria-label="Edit this page"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10.5 2.5l3 3L6 13H3v-3z"/><path d="M9 4l3 3"/></svg><span>Edit</span></button>`;
  const btn = shadow.querySelector("button");
  const label = shadow.querySelector("span");
  document.documentElement.append(host);
  // A bar fixed along the bottom of the page (the project nav's phone bar): sit above it, not on it.
  const lift = () => {
    let over = 0;
    for (const el of document.querySelectorAll(".lb-gbottom, [data-bottom-bar]")) {
      const r = el.getBoundingClientRect();
      if (r.height && r.left < 72 && r.bottom > innerHeight - 40) over = Math.max(over, innerHeight - r.top);   // 40: the phone bar floats since 7 Nov 2026
    }
    btn.style.bottom = over ? `${Math.round(over + 12)}px` : "";
    place();
  };
  // The language switch floats right of this button (nav.js, .lb-langfab): tell it where the button ends, also while the
  // button widens on hover. Two CSS variables on <html>, only in the live page (the editor saves from its own copy of the file).
  const R = document.documentElement.style;
  let was = "";
  const place = () => {
    const r = btn.hidden ? null : btn.getBoundingClientRect();
    const now = r && r.width ? `${Math.round(r.right)}|${Math.round(innerHeight - r.bottom)}` : "";
    if (now === was) return;
    was = now;
    if (!now) {
      R.removeProperty("--lb-editbtn-x"); R.removeProperty("--lb-editbtn-b");
      if (!R.length) document.documentElement.removeAttribute("style");
      return;
    }
    const [x, b] = now.split("|");
    R.setProperty("--lb-editbtn-x", `${x}px`);
    R.setProperty("--lb-editbtn-b", `${b}px`);
  };
  if (window.ResizeObserver) new ResizeObserver(place).observe(btn);
  addEventListener("resize", lift, { passive: true });
  addEventListener("scroll", lift, { passive: true });
  setTimeout(lift, 300);
  setInterval(lift, 2000);

  let loading = false;
  btn.addEventListener("click", () => {
    // the language switch puts the page's own words back first, so an edit never saves a translation (8 Nov 2026)
    if (window.LBI18N) window.LBI18N.suspend();
    if (window.__siteEditorOpen) { window.__siteEditorOpen(); return; }
    if (loading) return;
    loading = true;
    btn.setAttribute("aria-busy", "true");
    label.textContent = "Opening…";
    const s = document.createElement("script");
    s.src = BASE + "editor.js";
    s.dataset.page = cfg.page;
    s.dataset.mode = cfg.mode;
    s.dataset.note = cfg.note;
    s.dataset.file = cfg.file;
    s.onerror = () => { loading = false; btn.removeAttribute("aria-busy"); label.textContent = "Couldn't open the editor"; if (window.LBI18N) window.LBI18N.resume(); };
    document.documentElement.append(s);
  });
  window.__lbEditButton = {
    show() { btn.hidden = false; loading = false; btn.removeAttribute("aria-busy"); label.textContent = "Edit"; if (window.LBI18N) window.LBI18N.resume(); place(); },
    hide() { btn.hidden = true; place(); },
  };
})();
