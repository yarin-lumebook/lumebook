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
button {
  position: fixed; left: 16px; bottom: max(16px, env(safe-area-inset-bottom)); display: inline-flex; align-items: center; gap: 0;
  height: 44px; min-width: 44px; padding: 0 12px; border: 1px solid rgb(0 0 0 / 10%); border-radius: 999px; background: #fff; color: #1d1d1f;
  box-shadow: 0 6px 18px rgb(0 0 0 / 14%), 0 1px 3px rgb(0 0 0 / 10%); cursor: pointer; direction: ltr;
  font: 600 13px/1 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; opacity: .9; transition: opacity .15s, box-shadow .15s;
}
button:hover, button:focus-visible { opacity: 1; box-shadow: 0 8px 22px rgb(0 0 0 / 18%), 0 1px 3px rgb(0 0 0 / 12%); }
button:focus-visible { outline: 2px solid #0a64c8; outline-offset: 2px; }
svg { width: 18px; height: 18px; flex: none; fill: none; stroke: currentColor; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
span { max-width: 0; overflow: hidden; white-space: nowrap; transition: max-width .2s, margin .2s; }
button:hover span, button:focus-visible span, button[aria-busy="true"] span { max-width: 9em; margin-left: 8px; }
button[hidden] { display: none; }
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
      if (r.height && r.left < 72 && r.bottom > innerHeight - 4) over = Math.max(over, innerHeight - r.top);
    }
    btn.style.bottom = over ? `${Math.round(over + 12)}px` : "";
  };
  addEventListener("resize", lift, { passive: true });
  addEventListener("scroll", lift, { passive: true });
  setTimeout(lift, 300);
  setInterval(lift, 2000);

  let loading = false;
  btn.addEventListener("click", () => {
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
    s.onerror = () => { loading = false; btn.removeAttribute("aria-busy"); label.textContent = "Couldn't open the editor"; };
    document.documentElement.append(s);
  });
  window.__lbEditButton = {
    show() { btn.hidden = false; loading = false; btn.removeAttribute("aria-busy"); label.textContent = "Edit"; },
    hide() { btn.hidden = true; },
  };
})();
