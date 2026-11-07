/*!
 * LumeBook editor: edit any element of a page right where it is: text, colors, pictures, sizes and spacing,
 * and drag things to a new place. Project copy of the site-editor skill's editor (shared/site-editor/README.md).
 *
 * The project server (tools/lumebook.py serve, localhost:8780) adds an edit button to every page it shows
 * (loader.js); pressing it loads this file with data-page (the page's key), data-mode and data-note.
 *  - mode "source" (hand-written pages listed in pages.json): what the file holds is edited in the file itself,
 *    as the skill does; parts the page's scripts draw go to the edits layer.
 *  - mode "layer" (every other page: built pages, pages drawn by scripts, Carousel Machine): nothing is written
 *    into the page; every change is an operation in shared/site-editor/edits/<page>.json, applied by overlay.js
 *    whenever the page shows, and again after every rebuild or redraw.
 * By hand it still works like the skill: <script src="editor.js"></script> and ?edit in the URL.
 *
 * Why saves stay clean: in source mode the editor keeps its own copy of the page's file and applies every edit
 * to both the live page and that copy; only the copy is saved. In layer mode only the list of operations is saved.
 */
(() => {
  "use strict";
  if (window.__siteEditor) return;
  const me = document.currentScript;
  const PAGE = (me && me.dataset.page) || "";            // set by the project server: the page being edited
  const API = "/__site-editor/";
  const SERVED = Boolean(PAGE);
  const LAYER = SERVED && me.dataset.mode === "layer";    // nothing of the file is written: every change is an edit operation
  const NOTE = (me && me.dataset.note) || "";
  const RT = window.__lbEdits || null;                    // overlay.js, the runtime that applies saved edits
  const asked = /(?:^|&)edit(?:[=&]|$)/.test(location.search.slice(1)) || location.hash === "#edit";
  if ((!SERVED && !asked && location.protocol !== "file:") || !document.body) return;
  window.__siteEditor = true;

  const root = document.documentElement;
  const body = document.body;
  // Elements that came from the page's HTML, as opposed to ones its scripts add later (overlay.js notes them early).
  const known = (RT && RT.known) || new WeakSet(document.querySelectorAll("*"));
  // Without the server, the page as parsed so far is the fallback copy of the source.
  const early = SERVED ? "" : "<!doctype html>\n" + root.outerHTML;
  const FILE_NAME = (() => {
    let n = decodeURIComponent(((me && me.dataset.file) || PAGE || location.pathname).split("/").pop() || "") || "index.html";
    return /\.html?$/i.test(n) ? n : n + ".html";
  })();
  const SHEET_ID = "site-editor-styles";                   // the page's own <style> for page-wide colors
  const SENTINEL = "site-editor-apply";
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");

  // ---------- Small helpers ----------
  const h = (tag, attrs = {}, html = "") => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined && v !== false) n.setAttribute(k, v === true ? "" : v);
    if (html) n.innerHTML = html;
    return n;
  };
  const keepFocus = (b) => { b.addEventListener("mousedown", (e) => e.preventDefault()); return b; };
  const elOf = (node) => (node && (node.nodeType === 1 ? node : node.parentElement)) || null;

  // ---------- Icons: inline SVG only ----------
  const dot = (x, y, r = 1) => `<circle cx="${x}" cy="${y}" r="${r}" fill="currentColor" stroke="none"/>`;
  const ICONS = {
    undo: '<path d="M4.5 6.5h6a3 3 0 0 1 0 6H7"/><path d="M6.5 4 4 6.5 6.5 9"/>',
    redo: '<path d="M11.5 6.5h-6a3 3 0 0 0 0 6H9"/><path d="M9.5 4 12 6.5 9.5 9"/>',
    bold: '<path d="M5 3.5h3.8a2.3 2.3 0 0 1 0 4.6H5zM5 8.1h4.3a2.2 2.2 0 0 1 0 4.4H5z" stroke-width="1.8"/>',
    italic: '<path d="M10.5 3.5h-4M9.5 12.5h-4M8.9 3.5 7.1 12.5"/>',
    underline: '<path d="M4.5 3v4.5a3.5 3.5 0 0 0 7 0V3M3.5 13.5h9"/>',
    strike: '<path d="M3 8h10"/><path d="M10.7 5.3C10.4 4.2 9.3 3.5 8 3.5c-1.6 0-2.8.8-2.8 2 0 .6.3 1.1.9 1.5M5.3 10.6c.3 1.1 1.4 1.9 2.8 1.9 1.6 0 2.8-.9 2.8-2.1 0-.5-.2-1-.6-1.3"/>',
    textColor: '<path d="M4.5 10.5 8 2.5l3.5 8M5.8 7.6h4.4"/><rect x="2.5" y="12.4" width="11" height="2.2" rx="1.1" stroke="none" style="fill: var(--swatch, currentColor)"/>',
    highlight: '<path d="m9.8 2.6 3.4 3.4-5.6 5.6H4.2V8.2z"/><rect x="2.5" y="12.4" width="11" height="2.2" rx="1.1" stroke="none" style="fill: var(--swatch, #f5d547)"/>',
    alignLeft: '<path d="M3 4h10M3 7h6.5M3 10h10M3 13h6.5"/>',
    alignCenter: '<path d="M3 4h10M4.75 7h6.5M3 10h10M4.75 13h6.5"/>',
    alignRight: '<path d="M3 4h10M6.5 7H13M3 10h10M6.5 13H13"/>',
    alignJustify: '<path d="M3 4h10M3 7h10M3 10h10M3 13h10"/>',
    bullets: dot(3.5, 4.5) + dot(3.5, 8) + dot(3.5, 11.5) + '<path d="M6.5 4.5H13M6.5 8H13M6.5 11.5H13"/>',
    numbers: '<path d="M2.6 3.2 3.6 2.6v3.3M2.5 5.9h2.2M2.6 9.2c.2-.5.6-.7 1-.7.6 0 1 .4 1 .9 0 .8-2 1.4-2 2.4h2.1" stroke-width="1.2"/><path d="M7 4.5h6M7 10.5h6"/>',
    indent: '<path d="M3 3.5h10M7.5 6.5H13M7.5 9.5H13M3 12.5h10M3 6l2.2 2L3 10"/>',
    outdent: '<path d="M3 3.5h10M7.5 6.5H13M7.5 9.5H13M3 12.5h10M5.2 6 3 8l2.2 2"/>',
    link: '<path d="M6.8 9.2a2.8 2.8 0 0 0 4 0l1.9-1.9a2.8 2.8 0 0 0-4-4l-.7.7"/><path d="M9.2 6.8a2.8 2.8 0 0 0-4 0L3.3 8.7a2.8 2.8 0 0 0 4 4l.7-.7"/>',
    clear: '<path d="M3.5 3.5h7M7 3.5l-1.4 7"/><path d="m9.5 9.5 3.5 3.5M13 9.5l-3.5 3.5"/>',
    more: dot(3.5, 8, 1.1) + dot(8, 8, 1.1) + dot(12.5, 8, 1.1),
    sup: '<path d="m3 6 5 6.5M8 6l-5 6.5"/><path d="M10.2 3.8c.2-.5.6-.8 1.1-.8.6 0 1 .4 1 .9 0 .8-2.1 1.4-2.1 2.5h2.2" stroke-width="1.2"/>',
    sub: '<path d="m3 3.5 5 6.5M8 3.5 3 10"/><path d="M10.2 10.3c.2-.5.6-.8 1.1-.8.6 0 1 .4 1 .9 0 .8-2.1 1.4-2.1 2.5h2.2" stroke-width="1.2"/>',
    hr: '<path d="M2.5 8h11"/><path d="M4 4.5h8M4 11.5h8" opacity=".4"/>',
    chevron: '<path d="m4.5 6.5 3.5 3.5 3.5-3.5"/>',
    check: '<path d="m3.5 8.5 3 3 6-7"/>',
    picture: '<rect x="2" y="3" width="12" height="10" rx="2"/><circle cx="10.6" cy="6.2" r="1.1"/><path d="m2.5 11.5 3.3-3.3 2.4 2.4 1.8-1.8 3.4 3.3"/>',
    palette: '<path d="M8 2.5a5.5 5.5 0 1 0 0 11c.8 0 1.2-.5 1.2-1.1 0-.8-.6-1-.6-1.7 0-.6.5-1.1 1.2-1.1h1.3a2.4 2.4 0 0 0 2.4-2.4C13.5 4.6 11.1 2.5 8 2.5z"/>' + dot(5.3, 7, 0.9) + dot(7.5, 4.9, 0.9) + dot(10.4, 5.6, 0.9),
    trash: '<path d="M3 4.5h10M6.5 4.5V3h3v1.5M4.5 4.5l.6 8.5h5.8l.6-8.5"/>',
    copy: '<rect x="5.5" y="5.5" width="8" height="8" rx="1.5"/><path d="M10.5 5.5V3.8a1.3 1.3 0 0 0-1.3-1.3H3.8a1.3 1.3 0 0 0-1.3 1.3v5.4a1.3 1.3 0 0 0 1.3 1.3h1.7"/>',
    describe: '<path d="M3 3.5h10a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H8l-3 2.5v-2.5H3a1 1 0 0 1-1-1v-6a1 1 0 0 1 1-1z"/><path d="M5 6.5h6M5 8.8h4"/>',
    none: '<circle cx="8" cy="8" r="5.5"/><path d="M4.1 11.9 11.9 4.1"/>',
    reset: '<path d="M3.5 8a4.5 4.5 0 1 0 1.3-3.2"/><path d="M3.3 3v2.5h2.5"/>',
    eye: '<path d="M1.5 8S4 3.5 8 3.5 14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8z"/><circle cx="8" cy="8" r="2"/>',
    pencil: '<path d="M10.5 2.5l3 3L6 13H3v-3z"/><path d="M9 4l3 3"/>',
    up: '<path d="M8 13V3M4 7l4-4 4 4"/>',
    down: '<path d="M8 3v10M4 9l4 4 4-4"/>',
    parent: '<path d="M13 13V8.5A2.5 2.5 0 0 0 10.5 6H3"/><path d="M6 3 3 6l3 3"/>',
    close: '<path d="M4 4l8 8M12 4l-8 8"/>',
    save: '<path d="M8 2.5v8M4.5 7 8 10.5 11.5 7"/><path d="M3 13.5h10"/>',
    help: '<circle cx="8" cy="8" r="5.5"/><path d="M6.4 6.3a1.7 1.7 0 0 1 3.2.6c0 1.1-1.6 1.3-1.6 2.4"/>' + dot(8, 11.3, 0.8),
    open: '<path d="M9 3h4v4M13 3 7.5 8.5"/><path d="M11.5 9.5v3a1 1 0 0 1-1 1h-7a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1h3"/>',
  };
  const svg = (name, cls = "i") => `<svg class="${cls}" viewBox="0 0 16 16" aria-hidden="true" focusable="false">${ICONS[name]}</svg>`;

  // ---------- Colors ----------
  const cvs = document.createElement("canvas");
  cvs.width = cvs.height = 1;
  const ctx = cvs.getContext("2d", { willReadFrequently: true });
  // Any CSS color (including var(), color-mix(), oklch()…) → [r, g, b, a]; null if it isn't a color.
  const painted = new Map();
  const paint = (v) => {
    if (painted.has(v)) return painted.get(v);
    ctx.fillStyle = "#010203";
    ctx.fillStyle = v;
    let out = null;
    if (ctx.fillStyle !== "#010203" || /^#010203$/i.test(v)) {
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillRect(0, 0, 1, 1);
      const d = ctx.getImageData(0, 0, 1, 1).data;
      out = [d[0], d[1], d[2], d[3] / 255];
    }
    painted.set(v, out);
    return out;
  };
  const rgba = (value) => {
    if (!value) return null;
    let v = String(value).trim();
    if (/var\(|currentcolor|color-mix|light-dark/i.test(v)) {
      const probe = h("i", { style: `position:absolute;visibility:hidden;color:${v.replace(/[;{}]/g, "")}` });
      body.append(probe);
      v = getComputedStyle(probe).color;
      probe.remove();
    }
    return paint(v);
  };
  const shown = (value) => { const c = rgba(value); return c ? `rgb(${c[0]} ${c[1]} ${c[2]} / ${c[3]})` : "transparent"; };
  const toHex = (value) => { const c = rgba(value); return c ? "#" + c.slice(0, 3).map((x) => x.toString(16).padStart(2, "0")).join("") : ""; };
  const lum = ([r, g, b]) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const backdropOf = (n) => {
    for (let e = n; e && e.nodeType === 1; e = e.parentElement) {
      const c = rgba(getComputedStyle(e).backgroundColor);
      if (c && c[3] >= 0.5) return c;
    }
    return [255, 255, 255, 1];
  };
  const hasText = (n) => Boolean(n.textContent && n.textContent.trim());

  // The page's own color variables (custom properties on :root / html whose value is a color).
  const colorVars = () => {
    const names = new Set();
    const visit = (rules) => {
      for (const r of rules) {
        if (r.styleSheet) { try { visit(r.styleSheet.cssRules); } catch {} continue; }
        if (r.cssRules && !r.selectorText && !(r instanceof CSSMediaRule)) { visit(r.cssRules); continue; }
        if (!r.style || !r.selectorText || !/(^|,)\s*(:root|html)\s*(,|$)/.test(r.selectorText)) continue;
        for (const p of r.style) if (p.startsWith("--")) names.add(p);
      }
    };
    for (const sheet of document.styleSheets) { try { visit(sheet.cssRules); } catch {} }
    const cs = getComputedStyle(root);
    return [...names]
      .map((name) => ({ name, value: cs.getPropertyValue(name).trim() }))
      .filter(({ value }) => value && !/^(inherit|initial|unset|revert)$/i.test(value) && CSS.supports("color", value) && rgba(value));
  };
  // The colors actually painted on the page, most used first.
  const usedColors = (skip) => {
    const count = new Map();
    const add = (c, w = 1) => {
      const v = rgba(c);
      if (!v || v[3] < 0.5) return;
      const hex = toHex(c);
      count.set(hex, (count.get(hex) || 0) + w);
    };
    [...body.querySelectorAll("*")].slice(0, 4000).forEach((n) => {
      if (n === ui) return;
      const cs = getComputedStyle(n);
      if (cs.display === "none") return;
      if ([...n.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim())) add(cs.color, 2);
      add(cs.backgroundColor, 3);
      if (parseFloat(cs.borderTopWidth) > 0) add(cs.borderTopColor);
    });
    add(getComputedStyle(body).backgroundColor, 5);
    return [...count.entries()].sort((a, b) => b[1] - a[1]).map(([hex]) => hex).filter((hex) => !skip.has(hex)).slice(0, 14);
  };

  // ---------- The page's source: the copy that gets saved ----------
  let srcDoc = null, srcPrefix = "<!doctype html>\n";
  const toSrc = new WeakMap();
  // The source element behind a live one, or null when the page's scripts made it.
  const S = (n) => { if (LAYER) return null; const s = n && toSrc.get(n); return s && srcDoc && srcDoc.contains(s) ? s : null; };
  const adopt = (n) => { known.add(n); n.querySelectorAll("*").forEach((c) => known.add(c)); };
  const sameKind = (a, b) => a.localName === b.localName && (!a.id || !b.id || a.id === b.id);
  const textSig = (n) => n.localName + "\u0000" + (n.id || "") + "\u0000" + (n.textContent || "").replace(/\s+/g, " ").trim().slice(0, 80);
  // Pair every live element with its source element: first by kind + text, then by kind between neighbors.
  const align = (live, src) => {
    toSrc.set(live, src);
    const L = [...live.children].filter((n) => known.has(n) && n !== ui);
    const R = [...src.children];
    if (!L.length || !R.length) return;
    const ls = L.map(textSig), rs = R.map(textSig);
    const pair = new Array(R.length).fill(-1);
    let j = 0;
    R.forEach((r, i) => { for (let k = j; k < L.length; k++) if (ls[k] === rs[i]) { pair[i] = k; j = k + 1; break; } });
    let lo = 0;
    R.forEach((r, i) => {
      if (pair[i] >= 0) { lo = pair[i] + 1; return; }
      let hi = L.length;
      for (let n = i + 1; n < R.length; n++) if (pair[n] >= 0) { hi = pair[n]; break; }
      for (let k = lo; k < hi; k++) if (sameKind(L[k], r)) { pair[i] = k; lo = k + 1; break; }
    });
    pair.forEach((k, i) => { if (k >= 0) align(L[k], R[i]); });
  };
  const SVG_EMPTY = /<(path|circle|rect|line|polyline|polygon|ellipse|use|stop|image|animate|animateTransform|feBlend|feColorMatrix|feOffset|feGaussianBlur|feFlood|feComposite|feMergeNode)(\s[^<>]*?)?><\/\1>/g;
  let selfClosingSvg = false, headGap = "\n", tail = ["\n", "\n", "\n"], bareAttrs = new Set();
  const TAG = /<[a-zA-Z][^<>]*>/g;
  // Attributes the file writes without a value (hidden, data-open…) and never as ="": they stay bare when saved.
  const findBareAttrs = (text) => {
    const bare = new Set(), empty = new Set();
    for (const tag of text.match(TAG) || []) {
      for (const [, name, value] of tag.matchAll(/\s([^\s"'<>\/=]+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s"'=<>`]+))?/g)) {
        if (value === undefined) bare.add(name.toLowerCase());
        else if (value === '""' || value === "''") empty.add(name.toLowerCase());
      }
    }
    return new Set([...bare].filter((n) => !empty.has(n)));
  };
  // The parser drops or moves the whitespace around <head> and </body></html>; put the file's own back.
  const serialize = () => {
    let html = srcDoc.documentElement.outerHTML
      .replace(/^(<html[^>]*>)<head>/i, `$1${headGap}<head>`)
      .replace(/\s*<\/body>\s*<\/html>\s*$/i, `${tail[0]}</body>${tail[1]}</html>${tail[2]}`);
    if (selfClosingSvg) html = html.replace(SVG_EMPTY, (m, tag, attrs = "") => `<${tag}${attrs}/>`);
    if (bareAttrs.size) html = html.replace(TAG, (tag) => tag.replace(/\s([^\s"'<>\/=]+)=""/g, (m, name) => (bareAttrs.has(name.toLowerCase()) ? " " + name : m)));
    return srcPrefix + html;
  };
  // Whitespace text right before a source node (its line break + indentation), if any.
  const wsBefore = (s) => { const p = s.previousSibling; return p && p.nodeType === 3 && !p.textContent.trim() ? p : null; };

  // Clean HTML for the file: no editor or browser-extension leftovers.
  const EXT_ATTR = /^(contenteditable|spellcheck|data-gramm.*|data-gr-.*|data-new-gr-.*|data-enable-grammarly|data-lt-.*|data-ms-editor)$/i;
  const EXT_TAG = /^(grammarly-|lt-|deepl-)/i;
  const BLOCK_TAGS = new Set(["UL", "OL", "DIV", "P", "H1", "H2", "H3", "H4", "H5", "H6", "BLOCKQUOTE", "DL", "HR", "TABLE", "PRE"]);
  const fixNesting = (scope) => {
    scope.querySelectorAll("p, h1, h2, h3, h4, h5, h6").forEach((p) => {
      if (![...p.children].some((c) => BLOCK_TAGS.has(c.tagName))) return;
      const out = document.createDocumentFragment();
      let run = null;
      const flush = () => { if (run && (run.textContent.trim() || run.querySelector("img"))) out.append(run); run = null; };
      [...p.childNodes].forEach((n) => {
        if (n.nodeType === 1 && BLOCK_TAGS.has(n.tagName)) { flush(); out.append(n); }
        else { if (!run) run = p.cloneNode(false); run.append(n); }
      });
      flush();
      p.replaceWith(out);
    });
  };
  const cleanTree = (top) => {
    top.querySelectorAll("*").forEach((n) => { if (EXT_TAG.test(n.localName)) n.remove(); });
    [top, ...top.querySelectorAll("*")].forEach((n) => [...n.attributes].forEach((a) => { if (EXT_ATTR.test(a.name)) n.removeAttribute(a.name); }));
    top.querySelectorAll("font").forEach((f) => {
      const s = document.createElement("span");
      if (f.getAttribute("color")) s.style.color = f.getAttribute("color");
      const face = f.getAttribute("face");
      if (face && face !== SENTINEL) s.style.fontFamily = face;
      s.append(...f.childNodes);
      if (s.getAttribute("style")) f.replaceWith(s); else f.replaceWith(...s.childNodes);
    });
    fixNesting(top);
    return top;
  };
  // New paragraphs and list items go on their own lines, indented like their neighbors.
  const BLOCKISH = /^(p|h[1-6]|ul|ol|li|blockquote|pre|dl|dt|dd|hr|div|figure|figcaption|table)$/;
  const tidy = (n) => {
    const ws = [...n.childNodes].find((c) => c.nodeType === 3 && c.textContent.includes("\n") && !c.textContent.trim());
    if (ws) {
      const indent = "\n" + ws.textContent.split("\n").pop();
      [...n.children].forEach((c) => {
        const prev = c.previousSibling;
        if (BLOCKISH.test(c.localName) && prev && prev.nodeType === 1 && BLOCKISH.test(prev.localName)) n.insertBefore(document.createTextNode(indent), c);
      });
    }
    [...n.children].forEach((c) => { if (/^(ul|ol|dl|blockquote|div)$/.test(c.localName)) tidy(c); });
  };
  const cleanInner = (host) => { const c = cleanTree(host.cloneNode(true)); tidy(c); return c.innerHTML; };

  // ---------- History: every change is a command that edits the live page and the source together ----------
  const hist = { past: [], future: [] };
  let textSession = null;            // { host, before } while a text area is being typed in
  const run = (cmd) => {
    commitText();
    cmd.do();
    hist.past.push(cmd);
    if (hist.past.length > 300) hist.past.shift();
    hist.future = [];
    changed();
  };
  const undo = () => {
    commitText();
    const c = hist.past.pop();
    if (!c) return;
    c.undo();
    hist.future.push(c);
    changed();
    announce(`Undid: ${c.label}.`);
  };
  const redo = () => {
    commitText();
    const c = hist.future.pop();
    if (!c) return;
    c.do();
    hist.past.push(c);
    changed();
    announce(`Redid: ${c.label}.`);
  };
  const group = (label, cmds) => ({ label, get ops() { return cmds.flatMap((c) => c.ops || []); }, do: () => cmds.forEach((c) => c.do()), undo: () => [...cmds].reverse().forEach((c) => c.undo()) });

  // ---------- Edits layer: changes to what the file doesn't hold (built pages, parts drawn by the page's scripts) ----------
  // Every command on such an element also carries the operations overlay.js replays on the next visit. The list saved
  // is the operations of earlier visits plus those of the commands still in the history, so Undo takes them back too.
  const OVL = Boolean(RT) && SERVED;
  const O = (n) => OVL && Boolean(n) && n.nodeType === 1 && !S(n) && (n === body || body.contains(n)) && !ui.contains(n);
  const ED = (n) => Boolean(n && n.nodeType === 1 && (S(n) || O(n)));
  const textOf = (html) => { const t = document.createElement("template"); t.innerHTML = html; return t.content.textContent || ""; };
  const L = (n, sigBefore) => { RT.touch(n, sigBefore); return RT.locate(n); };
  const markOp = (op, el, ref) => { RT.mark(op, el, ref); return op; };
  const withOps = (cmd, make) => {
    const first = cmd.do;
    let made = false;
    cmd.ops = [];
    cmd.do = () => { first(); if (!made) { made = true; cmd.ops = make() || []; } };
    return cmd;
  };
  const opKey = (op) => op.t + "\u0000" + (op.n || "") + "\u0000" + JSON.stringify(op.at || null);
  // Typing makes one operation per pause; neighbours on the same element fold into one.
  const compact = (list) => {
    const out = [];
    for (const op of list) {
      const prev = out[out.length - 1];
      if (prev && op.t === "css" && prev.t === "css") { out[out.length - 1] = op; continue; }
      if (prev && /^(html|style|attr)$/.test(op.t) && opKey(prev) === opKey(op)) {
        out[out.length - 1] = op.t === "style" ? { ...op, v: { ...prev.v, ...op.v } } : op;
        continue;
      }
      out.push(op);
    }
    return out;
  };
  let baseOps = [];
  const allOps = () => compact([...baseOps, ...hist.past.flatMap((c) => c.ops || [])]);

  // One CSS property on one element (inline style).
  const setProp = (n, prop, value, prio) => {
    if (!n) return;
    if (value) n.style.setProperty(prop, value, prio || ""); else n.style.removeProperty(prop);
    if (!(n.getAttribute("style") || "").trim()) n.removeAttribute("style");
  };
  const styleCmd = (n, prop, value, important, label) => {
    const s = S(n);
    const was = (x) => (x ? [x.style.getPropertyValue(prop), x.style.getPropertyPriority(prop)] : null);
    const a = was(n), b = was(s);
    const prio = important ? "important" : "";
    const ov = O(n), at = ov ? L(n) : null;
    return withOps({
      label,
      do: () => { setProp(n, prop, value, prio); setProp(s, prop, value, prio); },
      undo: () => { setProp(n, prop, a[0], a[1]); if (b) setProp(s, prop, b[0], b[1]); },
    }, () => (ov ? [markOp({ t: "style", at, v: { [prop]: value ? [value, prio] : null } }, n)] : []));
  };
  const setAttr = (n, name, v) => { if (!n) return; if (v === null) n.removeAttribute(name); else n.setAttribute(name, v); };
  const attrCmd = (n, name, value, label) => {
    const s = S(n);
    const a = n.getAttribute(name), b = s ? s.getAttribute(name) : null;
    const ov = O(n), at = ov ? L(n) : null;
    return withOps(
      { label, do: () => { setAttr(n, name, value); setAttr(s, name, value); }, undo: () => { setAttr(n, name, a); setAttr(s, name, b); } },
      () => (ov ? [markOp({ t: "attr", at, n: name, v: value }, n)] : []),
    );
  };
  const setInner = (host, live, src) => {
    if (host.innerHTML !== live) host.innerHTML = live;
    const s = S(host);
    if (s) { s.innerHTML = src; adopt(host); align(host, s); }
    if (textSession && textSession.host === host) textSession.before = host.innerHTML;
  };
  const htmlCmd = (host, liveBefore, liveAfter, label = "Edit text") => {
    const s = S(host);
    const srcBefore = s ? s.innerHTML : "", srcAfter = cleanInner(host);
    // the words it had before this edit identify it next time (typing has already changed the live text)
    const ov = O(host), at = ov ? L(host, RT.sigText(host, textOf(liveBefore))) : null;
    return withOps(
      { label, do: () => setInner(host, liveAfter, srcAfter), undo: () => setInner(host, liveBefore, srcBefore) },
      () => (ov ? [markOp({ t: "html", at, v: srcAfter }, host)] : []),
    );
  };
  const removeCmd = (n, label = "Delete") => {
    if (O(n)) {
      // Parts the file doesn't hold are hidden, not taken out, so the page's own scripts never miss them.
      const at = L(n), had = [n.style.getPropertyValue("display"), n.style.getPropertyPriority("display")];
      return withOps({
        label,
        do: () => { n.style.setProperty("display", "none", "important"); n.setAttribute("data-lb-hidden", ""); },
        undo: () => { setProp(n, "display", had[0], had[1]); n.removeAttribute("data-lb-hidden"); },
      }, () => [markOp({ t: "hide", at }, n)]);
    }
    const parent = n.parentNode, next = n.nextSibling;
    const s = S(n), sp = s && s.parentNode, sn = s && s.nextSibling, ws = s && wsBefore(s);
    return {
      label,
      do: () => { n.remove(); if (s) { s.remove(); if (ws) ws.remove(); } },
      undo: () => { parent.insertBefore(n, next && next.parentNode === parent ? next : null); if (s) { sp.insertBefore(s, sn && sn.parentNode === sp ? sn : null); if (ws) sp.insertBefore(ws, s); } },
    };
  };
  const stripClone = (c) => {
    [c, ...c.querySelectorAll("*")].forEach((x) => {
      x.removeAttribute("id");
      [...x.attributes].forEach((a) => { if (EXT_ATTR.test(a.name)) x.removeAttribute(a.name); });
    });
    return c;
  };
  const duplicateCmd = (n) => {
    const s = S(n);
    if (!s) {
      const id = "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      const at = L(n);
      const copy = stripClone(n.cloneNode(true));
      copy.querySelectorAll("[data-lb-edit]").forEach((x) => x.removeAttribute("data-lb-edit"));
      copy.setAttribute("data-lb-edit", id);
      const v = copy.outerHTML;
      return withOps({ label: "Duplicate", node: copy, do: () => n.after(copy), undo: () => copy.remove() },
        () => [markOp({ t: "insert", at, pos: "after", id, v }, copy)]);
    }
    const copy = stripClone(n.cloneNode(true));
    const scopy = stripClone(s.cloneNode(true));
    const ws = wsBefore(s);
    const gap = srcDoc.createTextNode(ws ? "\n" + ws.textContent.split("\n").pop() : "");
    adopt(copy);
    align(copy, scopy);
    return {
      label: "Duplicate",
      node: copy,
      do: () => { n.after(copy); s.after(gap, scopy); },
      undo: () => { copy.remove(); gap.remove(); scopy.remove(); },
    };
  };
  // Moving next to another element; when either one isn't in the file, the move is an edit operation.
  const moveOvCmd = (n, target, pos, label) => {
    const at = L(n), to = L(target);
    const parent = n.parentNode, next = n.nextSibling;
    return withOps({
      label,
      do: () => { if (pos === "before") target.before(n); else if (pos === "after") target.after(n); else target.append(n); },
      undo: () => parent.insertBefore(n, next && next.parentNode === parent ? next : null),
    }, () => [markOp({ t: "move", at, to, pos }, n, target)]);
  };
  const moveCmd = (n, target, before, label = before ? "Move up" : "Move down") => {
    const s = S(n), t = S(target);
    if (!s || !t) return moveOvCmd(n, target, before ? "before" : "after", label);
    const next = n.nextSibling, sNext = s.nextSibling, ws = wsBefore(s);
    return {
      label,
      do: () => {
        if (before) target.before(n); else target.after(n);
        if (ws) ws.remove();
        if (before) t.parentNode.insertBefore(s, wsBefore(t) || t); else t.after(s);
        if (ws) s.parentNode.insertBefore(ws, s);
      },
      undo: () => {
        n.parentNode.insertBefore(n, next && next.parentNode === n.parentNode ? next : null);
        if (ws) ws.remove();
        s.parentNode.insertBefore(s, sNext && sNext.parentNode === s.parentNode ? sNext : null);
        if (ws) s.parentNode.insertBefore(ws, s);
      },
    };
  };
  const retagCmd = (n, tag) => {
    const s = S(n);
    if (!s) {
      const at = L(n), m = document.createElement(tag);
      [...n.attributes].forEach((a) => m.setAttribute(a.name, a.value));
      known.add(m);
      RT.touch(m, RT.sigOf(n));
      return withOps({
        label: "Change text style",
        node: m,
        do: () => { m.append(...n.childNodes); n.replaceWith(m); },
        undo: () => { n.append(...m.childNodes); m.replaceWith(n); },
      }, () => [markOp({ t: "tag", at, v: tag }, m)]);
    }
    const m = document.createElement(tag), sm = srcDoc.createElement(tag);
    [...n.attributes].forEach((a) => m.setAttribute(a.name, a.value));
    [...s.attributes].forEach((a) => sm.setAttribute(a.name, a.value));
    known.add(m);
    toSrc.set(m, sm);
    return {
      label: "Change text style",
      node: m,
      do: () => { m.append(...n.childNodes); n.replaceWith(m); sm.append(...s.childNodes); s.replaceWith(sm); },
      undo: () => { n.append(...m.childNodes); m.replaceWith(n); s.append(...sm.childNodes); sm.replaceWith(s); },
    };
  };

  // Page-wide colors live in one <style id="site-editor-styles"> in the page's <head>.
  let sheetModel = { vars: {}, rules: {} };
  const copyModel = (m) => ({ vars: { ...m.vars }, rules: Object.fromEntries(Object.entries(m.rules).map(([k, v]) => [k, { ...v }])) });
  const readSheet = () => {
    const tag = document.getElementById(SHEET_ID);
    if (!tag || !tag.sheet) return;
    for (const r of tag.sheet.cssRules) {
      if (!r.style) continue;
      const isRoot = r.selectorText === ":root";
      for (const p of r.style) {
        const v = r.style.getPropertyValue(p).trim();
        if (isRoot && p.startsWith("--")) sheetModel.vars[p] = v;
        else (sheetModel.rules[r.selectorText] ||= {})[p] = v;
      }
    }
  };
  const cssOf = (m) => {
    const block = (sel, decls) => { const d = Object.entries(decls); return d.length ? `${sel} {\n${d.map(([k, v]) => `  ${k}: ${v} !important;`).join("\n")}\n}` : ""; };
    return [block(":root", m.vars), ...Object.entries(m.rules).map(([sel, d]) => block(sel, d))].filter(Boolean).join("\n");
  };
  const writeSheet = (m) => {
    sheetModel = copyModel(m);
    const css = cssOf(sheetModel);
    let live = document.getElementById(SHEET_ID), src = srcDoc.getElementById(SHEET_ID);
    if (!css) {
      if (live) live.remove();
      if (src) { const ws = wsBefore(src); if (ws) ws.remove(); src.remove(); }
      return;
    }
    if (!live) { live = h("style", { id: SHEET_ID }); document.head.append(live); known.add(live); }
    if (!src) {
      src = srcDoc.createElement("style");
      src.id = SHEET_ID;
      const head = srcDoc.head, last = head.lastChild;
      const prev = head.lastElementChild && wsBefore(head.lastElementChild);
      const indent = prev ? prev.textContent.split("\n").pop() : "";
      if (last && last.nodeType === 3 && !last.textContent.trim()) head.insertBefore(src, last);
      else head.append(src, srcDoc.createTextNode("\n"));
      head.insertBefore(srcDoc.createTextNode("\n" + indent), src);
    }
    toSrc.set(live, src);
    live.textContent = src.textContent = "\n" + css + "\n";
  };
  const sheetCmd = (next, label) => {
    const before = copyModel(sheetModel), after = copyModel(next);
    const css = cssOf(after);
    return withOps({ label, do: () => writeSheet(after), undo: () => writeSheet(before) },
      () => (LAYER && OVL ? [{ t: "css", v: css ? "\n" + css + "\n" : "" }] : []));
  };

  // ---------- Which element is being edited ----------
  const PHRASING = new Set("a abbr b bdi bdo br cite code data del dfn em font i img ins kbd mark q s samp small span strong sub sup svg time u var wbr picture label".split(" "));
  const NO_TEXT = new Set("html head body script style noscript template svg math canvas video audio iframe object embed img picture input textarea select option optgroup datalist progress meter title meta link br hr".split(" "));
  const TEXT_BLOCKS = new Set("p h1 h2 h3 h4 h5 h6 blockquote pre ul ol dl hr figcaption".split(" "));
  const FORMATTING = new Set("b strong i em u s span font mark sub sup small code br del ins".split(" "));
  const RETAG = new Set("p h1 h2 h3 h4 h5 h6 blockquote div".split(" "));
  const MEDIA = "img, svg, video, iframe, canvas, input, button, select, textarea, picture, object, embed, audio";
  const ownText = (n) => [...n.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim());
  const isInline = (n) => getComputedStyle(n).display === "inline";
  // Text you can type into: has its own words, or holds only words and inline formatting.
  const isTextual = (n) => {
    if (!n || n.nodeType !== 1 || NO_TEXT.has(n.localName) || n.closest("svg, math") || !ED(n) || !hasText(n)) return false;
    if (ownText(n)) return true;
    return [...n.children].every((c) => PHRASING.has(c.localName) || isInline(c));
  };
  // A run of paragraphs, headings and lists edited as one area (Enter makes a new paragraph, lists work).
  const isFlow = (p) => {
    if (!p || p === body || p === root || !ED(p) || ownText(p) || p.children.length < 2) return false;
    return [...p.children].every((c) => {
      if (!TEXT_BLOCKS.has(c.localName) || !ED(c) || Boolean(S(c)) !== Boolean(S(p)) || c.querySelector(MEDIA)) return false;
      if (c.localName === "hr") return true;
      if (/^(ul|ol|dl)$/.test(c.localName)) return [...c.children].every((li) => /^(li|dt|dd)$/.test(li.localName) && (isTextual(li) || !hasText(li)));
      return isTextual(c) || !hasText(c);
    });
  };
  const hostFor = (t) => {
    let best = isTextual(t) ? t : null;
    for (let n = t; n.parentElement && isInline(n) && isTextual(n.parentElement); n = n.parentElement) best = n.parentElement;
    if (!best) return null;
    if (TEXT_BLOCKS.has(best.localName) && isFlow(best.parentElement)) return best.parentElement;
    if (/^(li|dt|dd)$/.test(best.localName)) {
      const list = best.parentElement;
      if (list && TEXT_BLOCKS.has(list.localName) && isFlow(list.parentElement)) return list.parentElement;
    }
    return best;
  };
  const pickFor = (t, host) => {
    let n = t.closest("svg") ? t.closest("svg").ownerSVGElement || t.closest("svg") : t;
    while (host && n !== host && host.contains(n) && FORMATTING.has(n.localName) && !n.className) n = n.parentElement;
    return n;
  };

  // ---------- Editor chrome: one shadow root, so the page's CSS and the editor's never mix ----------
  const ui = document.createElement("div");
  ui.setAttribute("data-site-editor", "");
  ui.style.cssText = "all: initial !important; position: fixed !important; top: 0 !important; left: 0 !important; width: 0 !important; height: 0 !important; z-index: 2147483000 !important; display: block !important;";
  const shadow = ui.attachShadow({ mode: "open" });
  shadow.innerHTML = `<style>
:host { all: initial; }
* { box-sizing: border-box; }
.wrap {
  --se-ink: #1d1d1f; --se-muted: #6e6e73; --se-line: rgb(0 0 0 / 10%); --se-hover: rgb(0 0 0 / 6%);
  --se-accent: #0a64c8; --se-accent-soft: rgb(10 100 200 / 12%); --se-accent-ink: #084a93; --se-danger: #b3261e;
  --se-shadow: 0 14px 38px -10px rgb(0 0 0 / 24%), 0 1px 3px rgb(0 0 0 / 10%);
  /* Liquid Glass (7 Nov 2026), the same material as the design system's: translucent white, a bright top edge, a soft lift */
  --se-rim: inset 0 1px 0 rgb(255 255 255 / 95%), inset 0 -1px 0 rgb(0 0 0 / 5%), inset 0 0 0 1px rgb(43 36 29 / 8%);
  --se-sheen: radial-gradient(130% 160% at 14% -30%, rgb(255 255 255 / 80%), rgb(255 255 255 / 0%) 58%);
  --se-font: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, Roboto, "Helvetica Neue", Arial, sans-serif;
  font: 13px/1.3 var(--se-font); color: var(--se-ink); -webkit-font-smoothing: antialiased; text-align: left; letter-spacing: normal;
  direction: ltr; unicode-bidi: isolate;   /* "all: initial" leaves direction alone, so right-to-left pages would mirror the editor */
}
.i { display: block; width: 16px; height: 16px; flex: none; fill: none; stroke: currentColor; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
button { font: inherit; color: inherit; }
[hidden] { display: none !important; }

.box { position: fixed; pointer-events: none; border-radius: 3px; }
.box.hover { outline: 1px dashed var(--se-accent); outline-offset: 1px; }
.box.sel { outline: 2px solid var(--se-accent); outline-offset: 2px; }
.box.host { outline: 1px solid color-mix(in srgb, var(--se-accent) 45%, transparent); outline-offset: 5px; }
.box .tag { position: absolute; left: -2px; bottom: calc(100% + 4px); display: flex; align-items: center; gap: 4px; max-width: 60vw; white-space: nowrap;
  padding: 2px 6px; border-radius: 4px; background: var(--se-accent); color: #fff; font: 600 11px/1.4 var(--se-font); }
.box .tag .tt { overflow: hidden; text-overflow: ellipsis; }
.box.flip .tag { bottom: auto; top: calc(100% + 4px); }
.grip { pointer-events: auto; flex: none; display: inline-grid; place-items: center; width: 20px; height: 18px; margin: -1px 0 -1px -4px; padding: 0; border: 0; border-radius: 3px;
  background: rgb(255 255 255 / 20%); color: #fff; cursor: grab; touch-action: none; }
.grip:hover { background: rgb(255 255 255 / 36%); }
.grip svg { width: 12px; height: 12px; fill: currentColor; stroke: none; }
.dropline { position: fixed; pointer-events: none; border-radius: 2px; background: var(--se-accent); box-shadow: 0 0 0 2px rgb(255 255 255 / 85%); }
.box.dragging { outline-style: dashed; }

.bar, .dock, .panel, .pop { background: #fff; box-shadow: var(--se-rim), var(--se-shadow); }
@supports ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .bar, .dock { background: var(--se-sheen), rgb(255 255 255 / 66%); -webkit-backdrop-filter: saturate(190%) blur(24px); backdrop-filter: saturate(190%) blur(24px); }
  .panel, .pop { background: var(--se-sheen), rgb(255 255 255 / 84%); -webkit-backdrop-filter: saturate(190%) blur(24px); backdrop-filter: saturate(190%) blur(24px); }
}
.bar { position: fixed; top: 10px; left: 50%; transform: translateX(-50%); display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 2px;
  width: max-content; max-width: min(1100px, calc(100vw - 24px)); padding: 5px; border-radius: 24px; }
.bar.low { top: auto; bottom: 76px; left: 16px; transform: none; justify-content: flex-start; max-width: calc(100vw - 32px - 316px); }
.dock { position: fixed; left: 16px; bottom: max(16px, env(safe-area-inset-bottom)); display: flex; align-items: center; gap: 2px; padding: 4px; border-radius: 999px; max-width: calc(100vw - 32px); }
.btn { flex: none; display: inline-flex; align-items: center; justify-content: center; gap: 6px; min-width: 36px; height: 36px; padding: 0 8px; border: 0; border-radius: 12px;
  background: none; font: 500 13px/1 var(--se-font); white-space: nowrap; cursor: pointer; transition: background .14s, transform .24s cubic-bezier(.34, 1.45, .64, 1); }
.btn:active { transform: scale(.96); }
.btn:hover { background: var(--se-hover); }
.btn[aria-pressed="true"], .btn[aria-expanded="true"] { background: var(--se-accent-soft); color: var(--se-accent-ink); box-shadow: inset 0 1px 0 rgb(255 255 255 / 70%); }
.btn:disabled { opacity: 0.35; cursor: default; background: none; }
.btn:focus-visible, .item:focus-visible, .sw:focus-visible, .seg button:focus-visible { outline: 2px solid var(--se-accent); outline-offset: 1px; }
.btn .i-chev { width: 12px; height: 12px; }
.btn .txt { min-width: 1.6em; max-width: 7em; overflow: hidden; text-overflow: ellipsis; text-align: left; }
.dock .btn { height: 44px; min-width: 44px; padding: 0 14px; border-radius: 999px; }
.dock .btn .lbl { font-weight: 600; }
.dock .btn.done { background: var(--se-ink); color: #fff; }
.dock .btn.done:hover { background: #000; }
.sizes { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px; padding: 2px 4px 4px; }
.num { display: flex; align-items: center; gap: 4px; min-width: 0; min-height: 34px; padding: 0 4px 0 8px; border-radius: 9px; background: var(--se-hover); cursor: text; }
.num span { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--se-muted); font-size: 12px; }
.num.set span { color: var(--se-accent-ink); font-weight: 600; }
.num input { flex: none; width: 46px; height: 26px; padding: 0 4px; border: 1px solid rgb(0 0 0 / 14%); border-radius: 6px; background: #fff; color: var(--se-ink);
  font: 500 12px/1 var(--se-font); text-align: right; }
.num input:focus-visible { outline: 2px solid var(--se-accent); outline-offset: 1px; }
.num em { flex: none; width: 1.3em; color: var(--se-muted); font: 11px/1 var(--se-font); font-style: normal; }
.num input::-webkit-inner-spin-button { margin-left: 2px; }
.p-sub { margin: 8px 8px 2px; color: var(--se-muted); font-size: 11px; font-weight: 600; letter-spacing: .03em; text-transform: uppercase; }
.sep { flex: none; width: 1px; height: 20px; margin: 0 4px; background: var(--se-line); }
.status { display: inline-flex; align-items: center; gap: 7px; margin: 0 8px 0 6px; max-width: 22em; font-weight: 600; line-height: 1.3; }
.status::before { content: ""; flex: none; width: 8px; height: 8px; border-radius: 50%; background: #3a9a5b; }
.status[data-state="saving"]::before { background: #d8a800; }
.status[data-state="error"]::before, .status[data-state="warn"]::before { background: var(--se-danger); }
.status[data-state="unsaved"]::before { background: #d8a800; }

.panel.aside { right: auto; left: 16px; bottom: calc(max(16px, env(safe-area-inset-bottom)) + 64px); }
.panel { position: fixed; right: 16px; bottom: max(16px, env(safe-area-inset-bottom)); width: 300px; max-height: min(70vh, 560px); overflow: auto; padding: 8px; border-radius: 26px; }
.p-head { display: flex; align-items: center; gap: 4px; padding: 2px 2px 6px 8px; }
.p-name { flex: 1; min-width: 0; }
.p-name b { display: block; font-size: 14px; }
.p-name code { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--se-muted); font: 12px/1.4 ui-monospace, "SF Mono", Menlo, Consolas, monospace; }
.p-note { margin: 4px 8px 8px; color: var(--se-muted); line-height: 1.4; }
.p-note.warn { color: var(--se-danger); }
.row { display: flex; align-items: center; gap: 8px; width: 100%; min-height: 40px; padding: 4px 8px; border: 0; border-radius: 14px; background: none; cursor: pointer; text-align: left; }
.row:hover { background: var(--se-hover); }
.row .lbl { flex: 1; }
.row .val { color: var(--se-muted); font: 12px/1 ui-monospace, "SF Mono", Menlo, Consolas, monospace; }
.chip { flex: none; width: 22px; height: 22px; border-radius: 50%; box-shadow: inset 0 0 0 1px rgb(0 0 0 / 18%); background-image: linear-gradient(45deg, #ddd 25%, transparent 25%, transparent 75%, #ddd 75%), linear-gradient(45deg, #ddd 25%, transparent 25%, transparent 75%, #ddd 75%); background-size: 8px 8px; background-position: 0 0, 4px 4px; position: relative; overflow: hidden; }
.chip > i { position: absolute; inset: 0; }
.tools { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2px; margin-top: 4px; }
.tools .btn { flex-direction: column; height: auto; min-height: 52px; padding: 6px 2px; gap: 4px; font-size: 11px; font-weight: 500; }
.tools .btn.danger { color: var(--se-danger); }
.hr { height: 1px; margin: 6px 4px; background: var(--se-line); }

.pop { position: fixed; z-index: 2; width: max-content; min-width: 200px; max-width: min(340px, calc(100vw - 16px)); max-height: min(74vh, 640px); overflow: auto;
  padding: 6px; border-radius: 20px; }
.pop.wide { width: min(360px, calc(100vw - 16px)); max-width: none; }
.pop-title { margin: 8px 10px 6px; font-size: 12px; font-weight: 600; color: var(--se-muted); }
.pop-sep { height: 1px; margin: 6px 4px; background: var(--se-line); }
.item { display: flex; align-items: center; gap: 10px; width: 100%; min-height: 36px; padding: 6px 10px; border: 0; border-radius: 14px; background: none; text-align: left; cursor: pointer; }
.item:hover { background: var(--se-hover); }
.item .check { margin-left: auto; visibility: hidden; color: var(--se-accent); }
.item[aria-checked="true"] .check { visibility: visible; }
.item.danger { color: var(--se-danger); }
.swatches { display: grid; grid-template-columns: repeat(8, 30px); gap: 6px; padding: 4px 10px; }
.sw { width: 30px; height: 30px; padding: 0; border: 0; border-radius: 50%; display: grid; place-items: center; background: #fff; color: var(--se-muted); cursor: pointer;
  box-shadow: inset 0 0 0 1px rgb(0 0 0 / 16%); }
.sw[aria-pressed="true"] { outline: 2px solid var(--se-accent); outline-offset: 2px; }
.seg { display: flex; gap: 2px; margin: 4px 10px 8px; padding: 3px; border-radius: 999px; background: var(--se-hover); }
.seg button { flex: 1; min-height: 30px; padding: 4px 8px; border: 0; border-radius: 999px; background: none; font: 500 12px/1.2 var(--se-font); cursor: pointer; }
.seg button[aria-checked="true"] { background: var(--se-sheen), #fff; box-shadow: var(--se-rim), 0 2px 6px -2px rgb(0 0 0 / 25%); font-weight: 600; }
.seg-hint { margin: -4px 10px 6px; color: var(--se-muted); font: 11px/1.4 ui-monospace, "SF Mono", Menlo, Consolas, monospace; overflow-wrap: anywhere; }
.custom { display: flex; align-items: center; gap: 6px; padding: 4px 10px 8px; }
.custom input[type="color"] { flex: none; width: 36px; height: 32px; padding: 0; border: 1px solid var(--se-line); border-radius: 8px; background: none; cursor: pointer; }
.field { flex: 1; min-width: 0; height: 32px; padding: 0 10px; border: 1px solid rgb(0 0 0 / 18%); border-radius: 8px; background: #fff; color: var(--se-ink); font: 500 13px/1 var(--se-font); }
.field.mono { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 12px; }
.form { display: grid; gap: 8px; padding: 8px 10px; }
.actions { display: flex; justify-content: flex-end; gap: 6px; }
.pbtn { min-height: 32px; padding: 0 12px; border: 0; border-radius: 8px; background: var(--se-hover); font: 600 13px/1 var(--se-font); cursor: pointer; }
.pbtn.primary { background: var(--se-ink); color: #fff; }
.help { margin: 4px 10px 8px; padding-left: 16px; line-height: 1.5; }
.help li + li { margin-top: 4px; }
kbd { font: 600 11px/1 var(--se-font); padding: 2px 5px; border-radius: 4px; background: var(--se-hover); }

.toast { position: fixed; z-index: 3; left: 50%; bottom: 84px; transform: translateX(-50%); display: inline-flex; align-items: center; gap: 12px; max-width: calc(100vw - 32px);
  min-height: 40px; padding: 8px 6px 8px 16px; border-radius: 999px; background: var(--se-sheen), rgb(255 255 255 / 88%); -webkit-backdrop-filter: saturate(190%) blur(24px); backdrop-filter: saturate(190%) blur(24px); color: var(--se-ink); font: 600 13px/1.3 var(--se-font); box-shadow: var(--se-rim), var(--se-shadow); }
.toast:not(:has(button)) { padding-right: 16px; }
.toast button { flex: none; min-height: 30px; padding: 0 12px; border: 0; border-radius: 999px; background: var(--se-hover); color: var(--se-accent-ink); cursor: pointer; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

.addpic { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; min-height: 40px; margin: 2px 0; padding: 0 12px; border: 0; border-radius: 10px;
  background: var(--se-ink); color: #fff; font: 600 13px/1 var(--se-font); cursor: pointer; }
.addpic:hover { background: #000; }
.addpic:focus-visible, .pos button:focus-visible, .zoom input:focus-visible { outline: 2px solid var(--se-accent); outline-offset: 2px; }
.frame { display: grid; gap: 10px; padding: 2px 8px 6px; }
.frame .seg { margin: 0; }
.frame .pbtn { justify-self: start; }
.zoom { display: flex; align-items: center; gap: 10px; }
.zoom > span { flex: none; color: var(--se-muted); }
.zoom input { flex: 1; min-width: 0; margin: 0; accent-color: var(--se-accent); }
.zoom output { flex: none; min-width: 3.2em; text-align: right; color: var(--se-muted); font: 12px/1 ui-monospace, "SF Mono", Menlo, Consolas, monospace; }
.posrow { display: flex; align-items: center; gap: 10px; }
.pos { flex: none; display: grid; grid-template-columns: repeat(3, 20px); gap: 2px; padding: 3px; border-radius: 8px; background: var(--se-hover); }
.pos button { display: grid; place-items: center; width: 20px; height: 20px; padding: 0; border: 0; border-radius: 5px; background: none; cursor: pointer; }
.pos button::after { content: ""; width: 5px; height: 5px; border-radius: 50%; background: rgb(0 0 0 / 30%); }
.pos button:hover { background: #fff; }
.pos button[aria-pressed="true"]::after { width: 8px; height: 8px; background: var(--se-accent); }
.posrow p { flex: 1; margin: 0; color: var(--se-muted); line-height: 1.4; }

@media (pointer: coarse) {
  .btn { min-width: 44px; height: 44px; }
  .item, .row { min-height: 44px; }
  .sw { width: 36px; height: 36px; }
  .swatches { grid-template-columns: repeat(6, 36px); }
  .pos { grid-template-columns: repeat(3, 30px); }
  .pos button { width: 30px; height: 30px; }
  .addpic { min-height: 44px; }
}
@media (max-width: 640px) {
  .dock .lbl, .status { display: none; }
  .dock .btn { padding: 0; }
  .panel { left: 8px; right: 8px; width: auto; bottom: calc(max(16px, env(safe-area-inset-bottom)) + 60px); max-height: 46vh; }
  .bar { flex-wrap: nowrap; justify-content: flex-start; overflow-x: auto; scrollbar-width: none; }
  .bar.low { bottom: auto; top: 10px; }
  .toast { bottom: auto; top: 64px; }
}
@media print { :host { display: none !important; } }
</style><div class="wrap"></div>`;
  const wrap = shadow.querySelector(".wrap");
  const fromUI = (e) => e.composedPath().includes(ui);
  const deepActive = () => { let a = document.activeElement; while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement; return a; };

  // Outlines: hover, selected element, active text area.
  const mkBox = (cls) => { const b = h("div", { class: "box " + cls, hidden: "" }); wrap.append(b); return b; };
  const hoverBox = mkBox("hover"), hostBox = mkBox("host"), selBox = mkBox("sel");
  const selTag = h("span", { class: "tag" });
  // The grip on the selected element's label: drag it to move the element (hold ⌥ / Alt to place it freely).
  const grip = h("button", { type: "button", class: "grip", title: "Drag to move it. Hold ⌥ (Alt) while dragging to place it freely.", "aria-label": "Move" },
    '<svg viewBox="0 0 12 12" aria-hidden="true"><circle cx="4" cy="2.5" r="1.1"/><circle cx="8" cy="2.5" r="1.1"/><circle cx="4" cy="6" r="1.1"/><circle cx="8" cy="6" r="1.1"/><circle cx="4" cy="9.5" r="1.1"/><circle cx="8" cy="9.5" r="1.1"/></svg>');
  const selText = h("span", { class: "tt" });
  selTag.append(grip, selText);
  selBox.append(selTag);
  const dropLine = h("div", { class: "dropline", hidden: "" });
  wrap.append(dropLine);

  // ---------- Status, messages, announcements ----------
  const live = h("div", { class: "sr", "aria-live": "polite" });
  const toastEl = h("div", { class: "toast", role: "status", hidden: "" });
  wrap.append(live, toastEl);
  const announce = (msg) => { live.textContent = ""; setTimeout(() => { live.textContent = msg; }, 60); };
  let toastTimer = 0;
  const toast = (msg, actionLabel, action) => {
    toastEl.replaceChildren(document.createTextNode(msg));
    if (actionLabel) {
      const b = h("button", { type: "button" });
      b.textContent = actionLabel;
      b.addEventListener("click", () => { toastEl.hidden = true; action(); });
      toastEl.append(b);
    }
    toastEl.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toastEl.hidden = true; }, 7000);
    announce(msg);
  };

  // ---------- Popovers ----------
  let openPop = null;
  const closePop = (restoreFocus = true) => {
    if (!openPop) return;
    const { el, anchor, outside, returnFocus } = openPop;
    openPop = null;
    el.remove();
    document.removeEventListener("pointerdown", outside, true);
    if (anchor) anchor.setAttribute("aria-expanded", "false");
    if (restoreFocus && returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
  };
  const placePop = (el, anchor) => {
    const r = anchor.getBoundingClientRect();
    const w = el.offsetWidth, ht = el.offsetHeight;
    const left = Math.min(Math.max(8, r.left), innerWidth - w - 8);
    let top = r.bottom + 6;
    if (top + ht > innerHeight - 8 && r.top - ht - 6 > 8) top = r.top - ht - 6;
    top = Math.max(8, Math.min(top, innerHeight - ht - 8));
    el.style.left = `${left}px`;
    el.style.top = `${top}px`;
  };
  const popover = (anchor, build, { label = "Options", wide = false, returnFocus = null, viaKeyboard = false } = {}) => {
    closePop(false);
    const el = h("div", { class: "pop" + (wide ? " wide" : ""), role: "dialog", "aria-label": label });
    build(el);
    wrap.append(el);
    placePop(el, anchor);
    anchor.setAttribute("aria-expanded", "true");
    const outside = (e) => { const p = e.composedPath(); if (!p.includes(el) && !p.includes(anchor)) closePop(false); };
    document.addEventListener("pointerdown", outside, true);
    openPop = { el, anchor, outside, returnFocus: returnFocus || (viaKeyboard ? anchor : null), rebuild: () => { el.replaceChildren(); build(el); placePop(el, anchor); } };
    if (viaKeyboard) { const first = el.querySelector("button, input"); if (first) first.focus(); }
    return el;
  };
  const popTitle = (text) => { const p = h("p", { class: "pop-title" }); p.textContent = text; return p; };
  const popSep = () => h("div", { class: "pop-sep" });
  const popItem = (icon, text, onClick, { checked = null, danger = false, keep = false, style = "" } = {}) => {
    const b = h("button", { type: "button", class: "item" + (danger ? " danger" : ""), role: checked === null ? null : "menuitemradio", "aria-checked": checked === null ? null : String(checked) });
    b.innerHTML = (icon ? svg(icon) : "") + "<span></span>" + (checked === null ? "" : svg("check", "i check"));
    const span = b.querySelector("span");
    span.textContent = text;
    if (style) span.style.cssText = style;
    if (keep) keepFocus(b);
    b.addEventListener("click", onClick);
    return b;
  };
  const formPop = (anchor, { label, value = "", placeholder = "", type = "text", apply, remove = null, viaKeyboard = false }) => {
    popover(anchor, (el) => {
      const form = h("div", { class: "form" });
      const input = h("input", { type, class: "field", "aria-label": label, placeholder });
      input.value = value;
      const actions = h("div", { class: "actions" });
      if (remove) { const r = h("button", { type: "button", class: "pbtn" }); r.textContent = remove.label; r.addEventListener("click", () => { closePop(false); remove.run(); }); actions.append(r); }
      const ok = h("button", { type: "button", class: "pbtn primary" }, "Apply");
      ok.addEventListener("click", () => { const v = input.value.trim(); closePop(false); apply(v); });
      input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); ok.click(); } });
      actions.append(ok);
      form.append(popTitle(label), input, actions);
      el.append(form);
      setTimeout(() => { input.focus(); input.select(); }, 0);
    }, { label, viaKeyboard });
  };

  // One color picker for everything: page colors, colors used on the page, lighter/darker, any custom color.
  const colorPop = (anchor, { title, value = "", noneLabel = "Default", scopes = null, literal = false, exclude = null, keep = false, viaKeyboard = false, onPick }) => {
    let scope = scopes ? scopes[0].key : null;
    const vars = colorVars().filter((v) => v.name !== exclude);
    const varHex = new Set(vars.map((v) => toHex(v.value)));
    const current = toHex(value), currentKey = value ? shown(value) : "";
    popover(anchor, (el) => {
      el.append(popTitle(title));
      if (scopes) {
        const seg = h("div", { class: "seg", role: "radiogroup", "aria-label": "Apply to" });
        const hint = h("p", { class: "seg-hint" });
        scopes.forEach((s) => {
          const b = h("button", { type: "button", role: "radio", "aria-checked": String(s.key === scope) });
          b.textContent = s.label;
          if (keep) keepFocus(b);
          b.addEventListener("click", () => {
            scope = s.key;
            seg.querySelectorAll("button").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
            hint.textContent = s.hint || "";
            hint.hidden = !s.hint;
          });
          seg.append(b);
        });
        hint.textContent = scopes[0].hint || "";
        hint.hidden = !scopes[0].hint;
        el.append(seg, hint);
      }
      const pick = (v) => { closePop(!keep); onPick(v, scope); };
      const grid = (label, items) => {
        if (!items.length) return;
        el.append(popTitle(label));
        const g = h("div", { class: "swatches", role: "group", "aria-label": label });
        items.forEach(([name, v]) => {
          const b = h("button", { type: "button", class: "sw", "aria-label": name, title: name, "aria-pressed": String(v ? Boolean(current) && shown(v) === currentKey : !value) });
          if (v) b.style.background = shown(v); else b.innerHTML = svg("none");
          if (keep) keepFocus(b);
          b.addEventListener("click", () => pick(v));
          g.append(b);
        });
        el.append(g);
      };
      grid("Reset", [[noneLabel, ""]]);
      grid("Page colors", vars.map((v) => [`${v.name} (${toHex(v.value)})`, literal ? toHex(v.value) : `var(${v.name})`]));
      const used = usedColors(varHex);
      ["#ffffff", "#000000"].forEach((c) => { if (!used.includes(c) && !varHex.has(c)) used.push(c); });
      grid("Used on this page", used.map((hex) => [hex, hex]));
      if (current && value) {
        const base = literal ? current : value;
        const mix = (pct, to) => `color-mix(in srgb, ${base} ${pct}%, ${to})`;
        const shades = [["Much lighter", mix(30, "white")], ["Lighter", mix(60, "white")], ["Current", base], ["Darker", mix(72, "black")], ["Much darker", mix(45, "black")]];
        grid("Lighter / darker", literal ? shades.map(([n, v]) => [n, toHex(v)]) : shades);
      }
      el.append(popTitle("Custom"));
      const row = h("div", { class: "custom" });
      const input = h("input", { type: "color", "aria-label": "Pick any color" });
      input.value = current || "#000000";
      const text = h("input", { type: "text", class: "field mono", "aria-label": "Color value", placeholder: "#hex, rgb(), hsl(), var(--name)", spellcheck: "false" });
      text.value = /^var\(/.test(value) ? value : current;
      const ok = h("button", { type: "button", class: "pbtn primary" }, "Apply");
      input.addEventListener("input", () => { text.value = input.value; });
      input.addEventListener("change", () => pick(input.value));
      const apply = () => {
        const v = text.value.trim();
        if (!v) return pick("");
        if (!CSS.supports("color", v) || !rgba(v)) { text.setCustomValidity("Not a color"); text.reportValidity(); return; }
        pick(v);
      };
      ok.addEventListener("click", apply);
      text.addEventListener("input", () => text.setCustomValidity(""));
      text.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); apply(); } });
      row.append(input, text, ok);
      el.append(row);
    }, { label: title, wide: true, returnFocus: anchor, viaKeyboard });
  };

  // ---------- Selecting elements ----------
  let editing = false, selected = null, hovered = null, activeHost = null, activeFlow = false, savedRange = null, pendingStyle = null;
  const FRIENDLY = {
    p: "Paragraph", h1: "Heading 1", h2: "Heading 2", h3: "Heading 3", h4: "Heading 4", h5: "Heading 5", h6: "Heading 6",
    a: "Link", button: "Button", img: "Picture", picture: "Picture", svg: "Icon", video: "Video", iframe: "Embedded frame",
    ul: "List", ol: "Numbered list", li: "List item", dl: "List", dt: "Term", dd: "Description", blockquote: "Quote",
    section: "Section", header: "Header", footer: "Footer", nav: "Navigation", main: "Main area", article: "Article", aside: "Side area",
    div: "Box", span: "Text", strong: "Bold text", b: "Bold text", em: "Italic text", i: "Italic text", label: "Label", small: "Small text",
    body: "Page", html: "Page", figure: "Figure", figcaption: "Caption", table: "Table", tr: "Table row", td: "Table cell", th: "Table header",
    form: "Form", input: "Input", textarea: "Text field", select: "Menu", hr: "Divider", code: "Code", pre: "Code block",
  };
  const describe = (n) => {
    const s = S(n) || n;
    const cls = s.classList ? [...s.classList].slice(0, 3).map((c) => "." + c).join("") : "";
    return { name: FRIENDLY[n.localName] || "Element", code: n.localName + (s.id ? "#" + s.id : "") + cls };
  };
  const select = (n) => {
    if (n === root || n === document.head) n = body;
    selected = n;
    renderPanel();
  };
  const deselect = () => { selected = null; renderPanel(); };

  const hostStyleProps = ["outline", "-webkit-user-select", "user-select"];
  const activateHost = (n) => {
    if (activeHost === n) return;
    deactivateHost();
    activeHost = n;
    activeFlow = isFlow(n);
    n.contentEditable = "true";
    n.spellcheck = true;
    // Ask Grammarly-style extensions not to inject their own elements.
    n.setAttribute("data-gramm", "false");
    n.setAttribute("data-gramm_editor", "false");
    n.setAttribute("data-enable-grammarly", "false");
    n.__seHad = hostStyleProps.map((p) => [p, n.style.getPropertyValue(p), n.style.getPropertyPriority(p)]);
    n.style.setProperty("outline", "none");
    if (getComputedStyle(n).userSelect === "none") { n.style.setProperty("-webkit-user-select", "text"); n.style.setProperty("user-select", "text"); }
    textSession = { host: n, before: n.innerHTML };
    bar.hidden = false;
    updateBar();
  };
  const deactivateHost = () => {
    const n = activeHost;
    if (!n) return;
    commitText();
    textSession = null;
    activeHost = null;
    savedRange = null;
    pendingStyle = null;
    ["contenteditable", "spellcheck", "data-gramm", "data-gramm_editor", "data-enable-grammarly"].forEach((a) => n.removeAttribute(a));
    (n.__seHad || []).forEach(([p, v, prio]) => { if (v) n.style.setProperty(p, v, prio); else n.style.removeProperty(p); });
    if (!(n.getAttribute("style") || "").trim()) n.removeAttribute("style");
    delete n.__seHad;
    if (n.contains(elOf(getSelection().anchorNode))) getSelection().removeAllRanges();
    if (n.isConnected && document.activeElement === n) n.blur();
    bar.hidden = true;
    if (openPop && bar.contains(openPop.anchor)) closePop(false);
  };
  let commitTimer = 0;
  const commitText = () => {
    clearTimeout(commitTimer);
    commitTimer = 0;
    if (!textSession || !textSession.host.isConnected) return;
    const { host, before } = textSession;
    const after = host.innerHTML;
    if (after === before) return;
    textSession.before = after;
    const cmd = htmlCmd(host, before, after);
    cmd.do();
    hist.past.push(cmd);
    hist.future = [];
    changed();
  };
  const scheduleCommit = () => { clearTimeout(commitTimer); commitTimer = setTimeout(commitText, 700); };
  const placeCaret = (n, atEnd = true) => {
    n.focus({ preventScroll: true });
    const r = document.createRange();
    r.selectNodeContents(n);
    r.collapse(!atEnd);
    const sel = getSelection();
    sel.removeAllRanges();
    sel.addRange(r);
  };

  // ---------- Rich text ----------
  const restoreSelection = () => {
    const sel = getSelection();
    const a = sel.rangeCount ? elOf(sel.getRangeAt(0).commonAncestorContainer) : null;
    if (activeHost && a && activeHost.contains(a)) { savedRange = sel.getRangeAt(0).cloneRange(); return true; }
    if (!activeHost || !activeHost.isConnected) return false;
    if (savedRange && activeHost.contains(savedRange.commonAncestorContainer)) {
      if (document.activeElement !== activeHost) activeHost.focus({ preventScroll: true });
      sel.removeAllRanges();
      sel.addRange(savedRange);
    } else placeCaret(activeHost);
    return true;
  };
  const afterEdit = () => {
    if (!activeHost) return;
    fixNesting(activeHost);
    const sel = getSelection();
    if (sel.rangeCount && activeHost.contains(sel.anchorNode)) savedRange = sel.getRangeAt(0).cloneRange();
    updateBar();
    scheduleCommit();
  };
  const exec = (cmd, value = null) => {
    if (!restoreSelection()) return false;
    document.execCommand("styleWithCSS", false, false);
    const ok = document.execCommand(cmd, false, value);
    afterEdit();
    return ok;
  };
  // Inline styles (font, size, color, highlight): wrap the selection, then set exactly one CSS property.
  const convertSentinels = (host, prop, value) => {
    const out = [];
    host.querySelectorAll(`font[face="${SENTINEL}"]`).forEach((f) => {
      const span = document.createElement("span");
      span.append(...f.childNodes);
      span.querySelectorAll("[style]").forEach((s) => { s.style.removeProperty(prop); if (!s.getAttribute("style").trim()) s.removeAttribute("style"); });
      span.querySelectorAll("span:not([style]):not([class])").forEach((s) => s.replaceWith(...s.childNodes));
      if (value) span.style.setProperty(prop, value);
      f.replaceWith(span);
      if (!value) {
        // Clearing: also clear the property from a wrapper that only holds this selection.
        let up = span.parentElement;
        while (up && up !== host && up.tagName === "SPAN" && up.textContent.trim() === span.textContent.trim()) {
          up.style.removeProperty(prop);
          if (!(up.getAttribute("style") || "").trim()) up.removeAttribute("style");
          up = up.parentElement;
        }
        const kids = [...span.childNodes];
        span.replaceWith(...kids);
        out.push(...kids);
      } else out.push(span);
    });
    return out;
  };
  const styleSelection = (prop, value) => {
    if (!restoreSelection()) return;
    const sel = getSelection();
    document.execCommand("styleWithCSS", false, false);
    if (sel.isCollapsed) {
      pendingStyle = { prop, value };
      document.execCommand("fontName", false, SENTINEL);
      return;
    }
    document.execCommand("fontName", false, SENTINEL);
    const nodes = convertSentinels(activeHost, prop, value);
    if (nodes.length) {
      const r = document.createRange();
      r.setStartBefore(nodes[0]);
      r.setEndAfter(nodes[nodes.length - 1]);
      sel.removeAllRanges();
      sel.addRange(r);
    }
    afterEdit();
  };
  const isFlowHost = () => Boolean(activeHost) && activeFlow;
  const BLOCK_SEL = "p, h1, h2, h3, h4, h5, h6, blockquote, pre, li, dt, dd, div";
  const STYLES = [["p", "Paragraph"], ["h1", "Heading 1"], ["h2", "Heading 2"], ["h3", "Heading 3"], ["h4", "Heading 4"], ["blockquote", "Quote"]];
  const blocksInSelection = () => {
    const sel = getSelection();
    if (!activeHost || !sel.rangeCount) return [];
    const range = sel.getRangeAt(0);
    const found = new Set();
    const addFrom = (n) => { const e = elOf(n); const b = e && e.closest(BLOCK_SEL); if (b && activeHost.contains(b) && b !== activeHost) found.add(b); };
    addFrom(range.startContainer);
    const walker = document.createTreeWalker(activeHost, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) if (range.intersectsNode(n) && n.textContent.trim()) addFrom(n);
    addFrom(range.endContainer);
    return [...found].filter((b) => ![...found].some((o) => o !== b && o.contains(b) && o.tagName !== "LI"));
  };
  const styleNameOf = (b) => (b && (STYLES.find(([t]) => t === b.localName) || [])[1]) || "Text";
  const setBlockStyle = (tag) => {
    if (!activeHost) return;
    if (!isFlowHost()) {
      if (!RETAG.has(activeHost.localName) || activeHost.localName === tag) return;
      const old = activeHost;
      deactivateHost();
      const cmd = retagCmd(old, tag);
      run(cmd);
      activateHost(cmd.node);
      placeCaret(cmd.node);
      select(cmd.node);
      return;
    }
    if (!restoreSelection()) return;
    const done = [];
    blocksInSelection().forEach((b) => {
      let n = b;
      if (!["LI", "DT", "DD"].includes(b.tagName) && b.localName !== tag) {
        n = document.createElement(tag);
        [...b.attributes].forEach((a) => n.setAttribute(a.name, a.value));
        n.append(...b.childNodes);
        b.replaceWith(n);
      }
      done.push(n);
    });
    if (done.length) {
      const r = document.createRange();
      r.setStart(done[0], 0);
      r.setEnd(done[done.length - 1], done[done.length - 1].childNodes.length);
      const sel = getSelection();
      sel.removeAllRanges();
      sel.addRange(r);
    }
    afterEdit();
  };

  const GENERIC_FONTS = [
    ["System", 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'],
    ["Serif", 'ui-serif, Georgia, "Times New Roman", serif'],
    ["Rounded", 'ui-rounded, "SF Pro Rounded", system-ui, sans-serif'],
    ["Mono", 'ui-monospace, "SF Mono", Menlo, Consolas, monospace'],
  ];
  const firstFamily = (f) => {
    const name = (f.split(",")[0] || "").replace(/["']/g, "").trim();
    return /^(-apple-system|system-ui|BlinkMacSystemFont|ui-sans-serif)$/i.test(name) ? "System" : name;
  };
  const pageFonts = () => {
    const count = new Map();
    [...body.querySelectorAll("*")].slice(0, 3000).forEach((n) => {
      if (n === ui || !ownText(n)) return;
      const f = getComputedStyle(n).fontFamily;
      count.set(f, (count.get(f) || 0) + 1);
    });
    return [...count.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5).map(([f]) => [firstFamily(f), f]);
  };
  const SIZES = [12, 13, 14, 15, 17, 20, 24, 28, 34, 40, 48, 60, 72];
  const ALIGNS = [["left", "Align left", "alignLeft", "justifyLeft"], ["center", "Center", "alignCenter", "justifyCenter"], ["right", "Align right", "alignRight", "justifyRight"], ["justify", "Justify", "alignJustify", "justifyFull"]];
  const setAlign = (value, cmd) => {
    if (!restoreSelection()) return;
    if (!isFlowHost()) {
      run(styleCmd(activeHost, "text-align", value === "left" ? "" : value, false, "Align text"));
      updateBar();
      return;
    }
    document.execCommand("styleWithCSS", false, true);
    document.execCommand(cmd, false, null);
    document.execCommand("styleWithCSS", false, false);
    afterEdit();
  };
  const currentLink = () => {
    const a = elOf(getSelection().anchorNode);
    const link = a && a.closest("a");
    return link && activeHost && activeHost.contains(link) ? link : null;
  };
  const cleanUrl = (url) => (/^(https?:|mailto:|tel:|#|\/|\.{0,2}\/)/i.test(url) || /\.[a-z0-9]+(?:[?#].*)?$/i.test(url) && !/^[\w-]+\.[a-z]{2,}(\/|$)/i.test(url) ? url : "https://" + url);
  const openLink = (anchor, viaKeyboard = false) => {
    if (!restoreSelection()) return;
    const a = currentLink();
    formPop(anchor, {
      label: a ? "Edit link" : "Add link",
      type: "text",
      value: a ? a.getAttribute("href") : "",
      placeholder: "https://",
      viaKeyboard,
      apply: (url) => {
        if (!url) return;
        url = cleanUrl(url);
        if (/^\s*javascript:/i.test(url)) return;
        restoreSelection();
        if (a) { a.setAttribute("href", url); afterEdit(); } else exec("createLink", url);
      },
      remove: a ? { label: "Remove link", run: () => { restoreSelection(); const r = document.createRange(); r.selectNodeContents(a); const s = getSelection(); s.removeAllRanges(); s.addRange(r); exec("unlink"); } } : null,
    });
  };
  const clearFormatting = () => {
    if (!restoreSelection()) return;
    document.execCommand("styleWithCSS", false, false);
    document.execCommand("removeFormat", false, null);
    document.execCommand("unlink", false, null);
    afterEdit();
  };

  // ---------- Formatting toolbar (shows while typing in a text area) ----------
  const bar = h("div", { class: "bar", role: "toolbar", "aria-label": "Text formatting", hidden: "" });
  const tb = {};
  const viaKb = (e) => e.detail === 0;
  const tbButton = (id, { icon = null, text = null, label, menu = false, pressed = false }) => {
    const b = h("button", { type: "button", class: "btn", "aria-label": label, title: label, "aria-pressed": pressed ? "false" : null, "aria-haspopup": menu ? "dialog" : null, "aria-expanded": menu ? "false" : null });
    b.innerHTML = (icon ? svg(icon) : "") + (text !== null ? `<span class="txt"></span>` : "") + (menu ? svg("chevron", "i i-chev") : "");
    if (text !== null) b.querySelector(".txt").textContent = text;
    keepFocus(b);
    tb[id] = b;
    bar.append(b);
    return b;
  };
  const tbSep = () => bar.append(h("span", { class: "sep", "aria-hidden": "true" }));
  tbButton("undo", { icon: "undo", label: "Undo typing (⌘Z)" }).addEventListener("click", () => exec("undo"));
  tbButton("redo", { icon: "redo", label: "Redo typing (⇧⌘Z)" }).addEventListener("click", () => exec("redo"));
  tbSep();
  tbButton("style", { text: "Text", label: "Text style", menu: true }).addEventListener("click", (e) => {
    const cur = isFlowHost() ? styleNameOf(blocksInSelection()[0]) : styleNameOf(activeHost);
    popover(tb.style, (el) => {
      STYLES.forEach(([tag, name]) => el.append(popItem(null, name, () => { closePop(false); setBlockStyle(tag); }, { checked: cur === name, keep: true })));
    }, { label: "Text style", viaKeyboard: viaKb(e) });
  });
  tbButton("font", { text: "Font", label: "Font", menu: true }).addEventListener("click", (e) => {
    const cur = tb.font.querySelector(".txt").textContent;
    popover(tb.font, (el) => {
      el.append(popItem(null, "Default font", () => { closePop(false); styleSelection("font-family", ""); }, { keep: true }));
      const fonts = pageFonts();
      if (fonts.length) {
        el.append(popTitle("Fonts on this page"));
        fonts.forEach(([name, fam]) => el.append(popItem(null, name, () => { closePop(false); styleSelection("font-family", fam); }, { checked: cur === name, keep: true, style: `font-family:${fam}` })));
      }
      el.append(popTitle("More"));
      GENERIC_FONTS.forEach(([name, fam]) => el.append(popItem(null, name, () => { closePop(false); styleSelection("font-family", fam); }, { checked: cur === name, keep: true, style: `font-family:${fam}` })));
    }, { label: "Font", viaKeyboard: viaKb(e) });
  });
  tbButton("size", { text: "16", label: "Text size", menu: true }).addEventListener("click", (e) => {
    const cur = tb.size.querySelector(".txt").textContent;
    popover(tb.size, (el) => {
      el.append(popItem(null, "Default size", () => { closePop(false); styleSelection("font-size", ""); }, { keep: true }));
      el.append(popSep());
      SIZES.forEach((px) => el.append(popItem(null, `${px}`, () => { closePop(false); styleSelection("font-size", `${px / 16}rem`); }, { checked: cur === String(px), keep: true })));
    }, { label: "Text size", viaKeyboard: viaKb(e) });
  });
  tbSep();
  const toggle = (id, icon, label, cmd) => tbButton(id, { icon, label, pressed: true }).addEventListener("click", () => exec(cmd));
  toggle("bold", "bold", "Bold (⌘B)", "bold");
  toggle("italic", "italic", "Italic (⌘I)", "italic");
  toggle("underline", "underline", "Underline (⌘U)", "underline");
  toggle("strike", "strike", "Strikethrough", "strikeThrough");
  tbSep();
  const colorButton = (id, icon, label, prop, noneLabel) => tbButton(id, { icon, label, menu: true }).addEventListener("click", (e) => {
    const n = elOf(getSelection().anchorNode);
    const cur = n ? (prop === "color" ? getComputedStyle(n).color : ((n.closest("[style*='background-color']") || {}).style || {}).backgroundColor || "") : "";
    colorPop(tb[id], {
      title: `${label} for the selected words`,
      value: cur,
      noneLabel,
      keep: true,
      viaKeyboard: viaKb(e),
      onPick: (v) => { styleSelection(prop, v); tb[id].style.setProperty("--swatch", v || null); },
    });
  });
  colorButton("color", "textColor", "Text color", "color", "Default");
  colorButton("highlight", "highlight", "Highlight", "background-color", "None");
  tbSep();
  tbButton("align", { icon: "alignLeft", label: "Alignment", menu: true }).addEventListener("click", (e) => {
    popover(tb.align, (el) => {
      ALIGNS.forEach(([v, name, icon, cmd]) => el.append(popItem(icon, name, () => { closePop(false); setAlign(v, cmd); }, { checked: tb.align.dataset.value === v, keep: true })));
    }, { label: "Alignment", viaKeyboard: viaKb(e) });
  });
  toggle("ul", "bullets", "Bulleted list", "insertUnorderedList");
  toggle("ol", "numbers", "Numbered list", "insertOrderedList");
  tbButton("outdent", { icon: "outdent", label: "Decrease indent" }).addEventListener("click", () => exec("outdent"));
  tbButton("indent", { icon: "indent", label: "Increase indent" }).addEventListener("click", () => exec("indent"));
  tbSep();
  tbButton("link", { icon: "link", label: "Link (⌘K)", menu: true }).addEventListener("click", (e) => openLink(tb.link, viaKb(e)));
  tbButton("more", { icon: "more", label: "More formatting", menu: true }).addEventListener("click", (e) => {
    popover(tb.more, (el) => {
      el.append(popItem("sup", "Superscript", () => { closePop(false); exec("superscript"); }, { checked: document.queryCommandState("superscript"), keep: true }));
      el.append(popItem("sub", "Subscript", () => { closePop(false); exec("subscript"); }, { checked: document.queryCommandState("subscript"), keep: true }));
      if (isFlowHost()) el.append(popItem("hr", "Horizontal line", () => { closePop(false); exec("insertHorizontalRule"); }, { keep: true }));
      el.append(popSep());
      el.append(popItem("clear", "Clear formatting", () => { closePop(false); clearFormatting(); }, { keep: true }));
    }, { label: "More formatting", viaKeyboard: viaKb(e) });
  });
  const FLOW_ONLY = ["ul", "ol", "outdent", "indent"];

  const updateBar = () => {
    if (!activeHost || bar.hidden) return;
    const flow = isFlowHost();
    FLOW_ONLY.forEach((id) => { tb[id].disabled = !flow; });
    tb.style.disabled = !flow && !RETAG.has(activeHost.localName);
    const q = (c) => { try { return document.queryCommandState(c); } catch { return false; } };
    [["bold", "bold"], ["italic", "italic"], ["underline", "underline"], ["strike", "strikeThrough"], ["ul", "insertUnorderedList"], ["ol", "insertOrderedList"]].forEach(([id, c]) => tb[id].setAttribute("aria-pressed", String(q(c))));
    const e = elOf(getSelection().rangeCount ? getSelection().anchorNode : null);
    if (!e || !activeHost.contains(e)) return;
    const cs = getComputedStyle(e);
    tb.size.querySelector(".txt").textContent = String(Math.round(parseFloat(cs.fontSize)));
    tb.font.querySelector(".txt").textContent = firstFamily(cs.fontFamily) || "Font";
    tb.style.querySelector(".txt").textContent = flow ? styleNameOf(blocksInSelection()[0]) : styleNameOf(activeHost);
    const block = flow ? e.closest(BLOCK_SEL) || activeHost : activeHost;
    const align = getComputedStyle(block).textAlign;
    const a = ALIGNS.find(([v]) => align === v || (v === "left" && (align === "start" || align === "left"))) || ALIGNS[0];
    tb.align.dataset.value = a[0];
    tb.align.querySelector(".i").outerHTML = svg(a[2]);
    tb.color.style.setProperty("--swatch", cs.color);
  };

  // ---------- Element panel (shows for the selected element) ----------
  const panel = h("div", { class: "panel", role: "region", "aria-label": "Selected element", hidden: "" });
  const colorProps = [["color", "Text color"], ["background-color", "Background"], ["border-color", "Border"]];
  const editorColor = (n, prop) => (n.style.getPropertyPriority(prop) === "important" ? n.style.getPropertyValue(prop) : "");
  const hasBorder = (cs) => ["Top", "Right", "Bottom", "Left"].some((s) => parseFloat(cs[`border${s}Width`]) > 0 && cs[`border${s}Style`] !== "none");
  const selectorFor = (n) => {
    const s = S(n) || n;
    const cls = (x) => [...(x.classList || [])].filter((c) => /^-?[_a-zA-Z][\w-]*$/.test(c)).map((c) => "." + CSS.escape(c)).join("");
    const tag = n.localName;
    if (n === body || n === root) return tag;
    const own = cls(s);
    if (own) return tag + own;
    const p = n.parentElement;
    const pc = p ? cls(S(p) || p) : "";
    return pc ? `${p.localName}${pc} > ${tag}` : tag;
  };
  const countOf = (sel) => { try { return document.querySelectorAll(sel).length; } catch { return 0; } };
  const imgOf = (n) => {
    if (n.localName === "img") return n;
    const imgs = n.querySelectorAll ? n.querySelectorAll("img") : [];
    return imgs.length === 1 && n !== body ? imgs[0] : null;
  };
  const linkOf = (n) => (n.closest ? n.closest("a[href]") : null);
  const siblingsOf = (n) => [...n.parentElement.children].filter((c) => c !== ui && ED(c) && !c.hasAttribute("data-lb-hidden"));
  const readableCheck = (n) => {
    if (!hasText(n)) return;
    const fg = rgba(getComputedStyle(n).color);
    const bg = backdropOf(n);
    if (!fg) return;
    const r = ratio(fg, bg);
    if (r >= 4.5) return;
    const best = ratio([255, 255, 255], bg) >= ratio([17, 17, 17], bg) ? "#ffffff" : "#111111";
    toast(`Hard to read: contrast is ${r.toFixed(1)}:1 (aim for 4.5:1).`, "Fix text color", () => { run(styleCmd(n, "color", best, true, "Fix text color")); });
  };
  const setElementColor = (n, prop, value, scope) => {
    if (scope === "all") {
      const sel = selectorFor(n);
      const next = copyModel(sheetModel);
      if (value) (next.rules[sel] ||= {})[prop] = value;
      else if (next.rules[sel]) { delete next.rules[sel][prop]; if (!Object.keys(next.rules[sel]).length) delete next.rules[sel]; }
      const cmds = [sheetCmd(next, "Color all like this")];
      if (editorColor(n, prop)) cmds.push(styleCmd(n, prop, "", false, "Color"));
      run(group(`Change ${prop === "color" ? "text color" : prop.replace("-color", " color")} of every ${sel}`, cmds));
    } else run(styleCmd(n, prop, value, true, prop === "color" ? "Change text color" : prop === "background-color" ? "Change background" : "Change border color"));
    if (prop !== "border-color") readableCheck(n);
  };
  const openElementColor = (n, prop, label, anchor, viaKeyboard) => {
    const sel = selectorFor(n), count = countOf(sel);
    const cs = getComputedStyle(n);
    const cur = editorColor(n, prop) || (prop === "border-color" ? cs.borderTopColor : cs.getPropertyValue(prop));
    const scopes = count > 1 ? [
      { key: "one", label: "Only this one" },
      { key: "all", label: `All ${count} like it`, hint: sel },
    ] : null;
    colorPop(anchor, { title: `${label}: ${describe(n).name}`, value: cur, noneLabel: "Default", scopes, viaKeyboard, onPick: (v, scope) => setElementColor(n, prop, v, scope) });
  };
  const replacePicture = async (img, file) => {
    const pic = await getPicture(file);
    if (!pic) return;
    const cmds = [attrCmd(img, "src", pic.src, "Picture"), attrCmd(img, "srcset", null, "Picture"), attrCmd(img, "sizes", null, "Picture"), attrCmd(img, "width", String(pic.w), "Picture"), attrCmd(img, "height", String(pic.h), "Picture")];
    if (img.parentElement && img.parentElement.localName === "picture") img.parentElement.querySelectorAll("source").forEach((s) => { if (S(s)) cmds.push(removeCmd(s)); else if (O(s)) cmds.push(attrCmd(s, "srcset", null, "Picture")); });
    run(group("Replace picture", cmds));
    if (pic.local) toast("Picture added into the page itself. Save with ⌘S.");
    announce("Picture replaced.");
  };
  const tool = (icon, label, onClick, { danger = false, disabled = false } = {}) => {
    const b = h("button", { type: "button", class: "btn" + (danger ? " danger" : ""), title: label, disabled });
    b.innerHTML = svg(icon) + "<span></span>";
    b.querySelector("span").textContent = label;
    b.addEventListener("click", onClick);
    return b;
  };
  const renderPanel = () => {
    const n = selected;
    panel.hidden = !n || !editing;
    selBox.hidden = panel.hidden;
    if (panel.hidden) return;
    const saved = ED(n);
    const { name, code } = describe(n);
    panel.replaceChildren();

    const head = h("div", { class: "p-head" });
    const title = h("div", { class: "p-name" });
    title.append(h("b"), h("code"));
    title.querySelector("b").textContent = name;
    title.querySelector("code").textContent = code;
    const up = h("button", { type: "button", class: "btn", title: "Select the element around it (Alt+↑)", "aria-label": "Select parent", disabled: n === body }, svg("parent"));
    up.addEventListener("click", () => { if (n.parentElement && n !== body) select(n.parentElement); });
    const x = h("button", { type: "button", class: "btn", title: "Deselect (Esc)", "aria-label": "Deselect" }, svg("close"));
    x.addEventListener("click", () => { deactivateHost(); deselect(); });
    head.append(title, up, x);
    panel.append(head);

    if (!saved) {
      const note = h("p", { class: "p-note warn" });
      note.textContent = OVL ? "This part can't be edited here." : "The page's own script makes this part, so changes here can't be saved. Select the element around it, or ask Claude to change the script.";
      panel.append(note);
      return;
    }
    const slot = placeholderFor(n), framedPic = framedImg(n);
    if (slot) panel.append(...pictureSlot(slot));
    else if (framedPic) panel.append(frameControls(framedPic), h("div", { class: "hr" }));
    const cs = getComputedStyle(n);
    colorProps.forEach(([prop, label]) => {
      if (prop === "border-color" && !hasBorder(cs)) return;
      if (prop === "color" && /^(img|video|iframe|canvas|audio|picture|hr|embed|object)$/.test(n.localName)) return;
      const value = prop === "border-color" ? cs.borderTopColor : cs.getPropertyValue(prop);
      const row = h("button", { type: "button", class: "row", "aria-haspopup": "dialog", "aria-expanded": "false" });
      const chip = h("span", { class: "chip", "aria-hidden": "true" }, "<i></i>");
      chip.firstChild.style.background = shown(value);
      const lbl = h("span", { class: "lbl" });
      lbl.textContent = label;
      const val = h("span", { class: "val" });
      const c = rgba(value);
      val.textContent = !c || c[3] === 0 ? "none" : toHex(value) + (c[3] < 1 ? ` ${Math.round(c[3] * 100)}%` : "") + (editorColor(n, prop) ? " •" : "");
      val.title = editorColor(n, prop) ? "Set here" : "From the page's styles";
      row.append(chip, lbl, val);
      row.addEventListener("click", (e) => openElementColor(n, prop, label, row, viaKb(e)));
      panel.append(row);
    });

    const sizes = sizeControls(n);
    if (sizes.childElementCount) panel.append(h("p", { class: "p-sub" }, "Size and spacing"), sizes);

    const note = h("p", { class: "p-note" });
    if (n === activeHost || (activeHost && activeHost.contains(n))) note.textContent = "Type to change the text. Select words to format them with the toolbar.";
    else if (hostFor(n)) note.textContent = "Click the text to change it.";
    else if (movable(n)) note.textContent = "Drag the ⠿ on its label to move it. Hold ⌥ (Alt) to place it freely.";
    if (!LAYER && O(n) && n !== body) note.textContent += (note.textContent ? " " : "") + "The page's script draws this part: your change is kept and applied each time it is drawn.";
    if (note.textContent) panel.append(note);

    const extra = [];
    const img = imgOf(n);
    if (img && ED(img)) {
      extra.push(tool("picture", "Replace", () => replacePicture(img)));
      extra.push(tool("describe", "Describe", (e) => formPop(e.currentTarget, {
        label: "Describe this picture (for screen readers)",
        value: img.getAttribute("alt") || "",
        placeholder: "e.g. Two friends laughing at a table",
        apply: (v) => run(attrCmd(img, "alt", v, "Describe picture")),
      })));
    }
    const a = linkOf(n);
    if (a && ED(a)) {
      extra.push(tool("link", "Link", (e) => formPop(e.currentTarget, {
        label: "Link address",
        value: a.getAttribute("href") || "",
        placeholder: "https://",
        apply: (v) => { if (v && !/^\s*javascript:/i.test(v)) run(attrCmd(a, "href", cleanUrl(v), "Change link")); },
      })));
      extra.push(tool("open", "Open", () => window.open(a.href, "_blank", "noopener")));
    }
    const fixed = n === body || n === root || !n.parentElement || n.parentElement === root;
    const sibs = fixed ? [] : siblingsOf(n);
    const i = sibs.indexOf(n);
    const tools = h("div", { class: "tools" });
    tools.append(
      tool("up", "Move up", () => { run(moveCmd(n, sibs[i - 1], true)); announce("Moved up."); }, { disabled: fixed || i <= 0 }),
      tool("down", "Move down", () => { run(moveCmd(n, sibs[i + 1], false)); announce("Moved down."); }, { disabled: fixed || i < 0 || i >= sibs.length - 1 }),
      tool("copy", "Duplicate", () => duplicate(n), { disabled: fixed }),
      tool("trash", "Delete", () => remove(n), { danger: true, disabled: fixed }),
      ...extra,
    );
    if (colorProps.some(([p]) => editorColor(n, p))) {
      tools.append(tool("reset", "Colors", () => run(group("Reset colors", colorProps.filter(([p]) => editorColor(n, p)).map(([p]) => styleCmd(n, p, "", false, "Reset color")))), {}));
      tools.lastChild.title = "Reset the colors set on this element";
    }
    const setSizes = SIZE_PROPS.filter((p) => editorColor(n, p));
    if (setSizes.length) {
      tools.append(tool("reset", "Sizes", () => run(group("Reset size and spacing", setSizes.map((p) => styleCmd(n, p, "", false, "Reset size"))))));
      tools.lastChild.title = "Reset the sizes and spacing set on this element";
    }
    if (n.style.getPropertyValue("translate")) {
      tools.append(tool("reset", "Position", () => run(styleCmd(n, "translate", "", false, "Back to its place"))));
      tools.lastChild.title = "Put it back where the page places it";
    }
    panel.append(h("div", { class: "hr" }), tools);
    if (focusProp) {
      const f = panel.querySelector(`input[data-prop="${focusProp}"]`);
      focusProp = null;
      if (f) { f.focus({ preventScroll: true }); f.select(); }
    }
  };

  // Size and spacing of the selected element: inline "!important" pixels, like its colors.
  const SIZE_FIELDS = [
    ["font-size", "Text size", "px", (n) => hasText(n)],
    ["width", "Width", "px", (n, cs) => cs.display !== "inline"],
    ["height", "Height", "px", (n, cs) => cs.display !== "inline" && !hasText(n)],
    ["padding", "Padding", "px", (n, cs) => cs.display !== "inline"],
    ["margin-top", "Space above", "px", (n, cs) => cs.display !== "inline"],
    ["margin-bottom", "Space below", "px", (n, cs) => cs.display !== "inline"],
    ["gap", "Gap", "px", (n, cs) => /flex|grid/.test(cs.display)],
    ["border-radius", "Corners", "px", () => true],
    ["border-width", "Border", "px", (n, cs) => cs.display !== "inline"],
    ["opacity", "Opacity", "%", () => true],
  ];
  const SIZE_PROPS = [...SIZE_FIELDS.map((f) => f[0]), "border-style"];
  let focusProp = null;
  const readSize = (cs, prop) => {
    switch (prop) {
      case "padding": return parseFloat(cs.paddingTop);
      case "border-radius": return parseFloat(cs.borderTopLeftRadius);
      case "border-width": return cs.borderTopStyle === "none" ? 0 : parseFloat(cs.borderTopWidth);
      case "opacity": return parseFloat(cs.opacity) * 100;
      case "gap": return parseFloat(cs.rowGap) || parseFloat(cs.columnGap) || 0;
      default: return parseFloat(cs.getPropertyValue(prop));
    }
  };
  const sizeControls = (n) => {
    const box = h("div", { class: "sizes", role: "group", "aria-label": "Size and spacing" });
    if (n === body || n === root) return box;
    const cs = getComputedStyle(n);
    SIZE_FIELDS.filter((f) => f[3](n, cs)).forEach(([prop, label, unit]) => {
      const lab = h("label", { class: "num" + (editorColor(n, prop) ? " set" : ""), title: editorColor(n, prop) ? `${label}: set here` : `${label}: from the page's styles` });
      const name = h("span");
      name.textContent = label;
      const input = h("input", { type: "number", step: "1", min: /^margin/.test(prop) ? null : "0", max: prop === "opacity" ? "100" : null, "data-prop": prop, "aria-label": `${label} (${unit})` });
      const v = readSize(cs, prop);
      input.value = Number.isFinite(v) ? String(Math.round(v * 10) / 10) : "";
      const em = h("em");
      em.textContent = unit;
      lab.append(name, input, em);
      const before = { [prop]: [n.style.getPropertyValue(prop), n.style.getPropertyPriority(prop)], "border-style": [n.style.getPropertyValue("border-style"), n.style.getPropertyPriority("border-style")] };
      const cssVal = (x) => (x === "" || !Number.isFinite(+x) ? "" : prop === "opacity" ? String(clamp(+x, 0, 100) / 100) : `${+x}px`);
      const needsStyle = () => prop === "border-width" && cs.borderTopStyle === "none";
      input.addEventListener("input", () => {
        if (input.value === "") return;
        setProp(n, prop, cssVal(input.value), "important");
        if (needsStyle()) setProp(n, "border-style", "solid", "important");
      });
      input.addEventListener("change", () => {
        Object.entries(before).forEach(([p, [val, prio]]) => setProp(n, p, val, prio));
        const val = cssVal(input.value);
        const cmds = [styleCmd(n, prop, val, true, `Change ${label.toLowerCase()}`)];
        if (val && needsStyle()) cmds.push(styleCmd(n, "border-style", "solid", true, "Border"));
        focusProp = prop;
        run(cmds.length > 1 ? group(`Change ${label.toLowerCase()}`, cmds) : cmds[0]);
      });
      box.append(lab);
    });
    return box;
  };
  const duplicate = (n) => {
    if (activeHost && (n === activeHost || n.contains(activeHost))) deactivateHost();
    const cmd = duplicateCmd(n);
    run(cmd);
    select(cmd.node);
    announce("Duplicated.");
  };
  const remove = (n) => {
    if (activeHost && n.contains(activeHost)) deactivateHost();
    const { name } = describe(n);
    run(removeCmd(n, `Delete ${name.toLowerCase()}`));
    deselect();
    toast(`Deleted ${name.toLowerCase()}.`, "Undo", undo);
  };

  // ---------- Pictures ----------
  const pickFile = () => new Promise((resolve) => {
    const input = h("input", { type: "file", accept: "image/*", hidden: "" });
    const done = (f) => { input.remove(); resolve(f); };
    input.addEventListener("change", () => done(input.files && input.files[0] ? input.files[0] : null));
    input.addEventListener("cancel", () => done(null));
    wrap.append(input);
    input.click();
  });
  const loadImage = (file) => new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => resolve({ img, url });
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("decode")); };
    img.src = url;
  });
  // Pictures are scaled to at most 2000px; SVG files stay SVG.
  const preparePicture = async (file) => {
    const { img, url } = await loadImage(file);
    const w = img.naturalWidth || 1200, ht = img.naturalHeight || 800;
    if (file.type === "image/svg+xml") { URL.revokeObjectURL(url); return { blob: file, type: file.type, w, h: ht }; }
    const scale = Math.min(1, 2000 / Math.max(w, ht));
    const cw = Math.round(w * scale), ch = Math.round(ht * scale);
    const canvas = document.createElement("canvas");
    canvas.width = cw;
    canvas.height = ch;
    canvas.getContext("2d").drawImage(img, 0, 0, cw, ch);
    URL.revokeObjectURL(url);
    const type = /png|gif/.test(file.type) ? "image/png" : "image/jpeg";
    const blob = await new Promise((res) => canvas.toBlob(res, type, 0.86));
    return { blob, type, w: cw, h: ch };
  };
  const getPicture = async (given) => {
    const file = given || await pickFile();
    if (!file) return null;
    setStatus("saving", "Adding picture…");
    try {
      const pic = await preparePicture(file);
      if (mode === "server") {
        const r = await fetch(`${API}upload?page=${encodeURIComponent(PAGE)}&name=${encodeURIComponent(file.name || "picture")}`, { method: "PUT", headers: { "Content-Type": pic.type, "X-Site-Editor": "1" }, body: pic.blob });
        const res = await r.json().catch(() => ({}));
        if (!r.ok || !res.ok) throw new Error(res.error || String(r.status));
        setStatus("saved", "Picture added");
        return { src: res.path, w: pic.w, h: pic.h };
      }
      const src = await new Promise((res, rej) => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.onerror = rej; fr.readAsDataURL(pic.blob); });
      return { src, w: pic.w, h: pic.h, local: true };
    } catch {
      setStatus("error", "Couldn't add that picture. Try a JPEG, PNG, WebP, GIF or SVG file.");
      return null;
    }
  };

  // Picture placeholders: boxes standing in for a picture, like a grey box reading "[Hero image]",
  // an empty painted box, or one whose class says so (.placeholder, .ph, .cover, .thumb…).
  const PH_WORDS = new Set("ph placeholder img image images photo photos picture pic cover thumb thumbnail avatar media poster".split(" "));
  const MEDIA_INSIDE = "img, picture, video, iframe, canvas, object, embed";
  const CONTENT = "a, button, input, select, textarea, label, h1, h2, h3, h4, h5, h6, p, ul, ol";
  const inFlow = (c) => { const cs = getComputedStyle(c); return cs.display !== "none" && !/^(absolute|fixed)$/.test(cs.position); };
  // What a placeholder shows until it has a picture: a short label or an icon, never real content.
  const isLabel = (c) => !c.matches(CONTENT) && !c.querySelector(CONTENT) && c.textContent.trim().length <= 80;
  const isPlaceholder = (n) => {
    if (!n || n.nodeType !== 1 || n === body || n === root || !ED(n) || NO_TEXT.has(n.localName) || /^(p|h[1-6]|li|label|button)$/.test(n.localName)) return false;
    if (n.querySelector(MEDIA_INSIDE)) return false;
    const cs = getComputedStyle(n);
    if (/^(inline|contents|none)$/.test(cs.display)) return false;
    const r = n.getBoundingClientRect();
    if (r.width < 24 || r.height < 24) return false;
    const own = [...n.childNodes].filter((c) => c.nodeType === 3).map((c) => c.textContent).join("").trim();
    if (own.length > 80 || ![...n.children].filter(inFlow).every(isLabel)) return false;
    const s = S(n) || n;
    const words = `${s.getAttribute("class") || ""} ${s.id || ""}`.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase().split(/[^a-z0-9]+/);
    if (s.hasAttribute("data-placeholder") || words.some((w) => PH_WORDS.has(w))) return true;
    const bg = rgba(cs.backgroundColor);
    if (!((bg && bg[3] > 0.05) || hasBorder(cs)) || r.width < 48 || r.height < 48) return false;
    const text = n.textContent.replace(/\s+/g, " ").trim();
    return text ? /^\[[^\]]{1,80}\]$/.test(text) && r.height >= 3 * parseFloat(cs.fontSize) : !n.children.length;
  };
  // The placeholder a selection belongs to: the box itself, or the box around its label.
  const placeholderFor = (n) => {
    if (isPlaceholder(n)) return n;
    const p = n && n.parentElement;
    return p && isPlaceholder(p) && inFlow(n) ? p : null;
  };

  // Words sitting right in the box, outside any child element: cleared, keeping the file's line breaks.
  const clearTextCmd = (n) => {
    const pick = (x) => (x ? [...x.childNodes].filter((c) => c.nodeType === 3 && c.textContent.trim()).map((c) => [c, c.textContent]) : []);
    const all = [...pick(n), ...pick(S(n))];
    return {
      label: "Clear placeholder text",
      do: () => all.forEach(([t, v]) => { t.textContent = v.match(/^\s*/)[0]; }),
      undo: () => all.forEach(([t, v]) => { t.textContent = v; }),
    };
  };
  // The picture goes first in the box, so badges and buttons positioned over the box stay on top of it.
  const insertImgCmd = (frame, img, simg) => {
    const s = S(frame);
    let added = [];
    return {
      label: "Add picture",
      do: () => {
        frame.insertBefore(img, frame.firstChild);
        const first = s.firstChild;
        if (first && first.nodeType === 3 && !first.textContent.trim() && first.textContent.includes("\n") && s.children.length) {
          const gap = srcDoc.createTextNode(first.textContent);
          s.insertBefore(simg, first.nextSibling);
          s.insertBefore(gap, simg.nextSibling);
          added = [simg, gap];
        } else {
          s.insertBefore(simg, first);
          added = [simg];
        }
      },
      undo: () => { img.remove(); added.forEach((x) => x.remove()); },
    };
  };
  const FILL = "position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;";
  const addPicture = async (frame, file) => {
    const pic = await getPicture(file);
    if (!pic || !frame.isConnected || !ED(frame)) return;
    if (activeHost && (frame.contains(activeHost) || activeHost.contains(frame))) deactivateHost();
    const attrs = { src: pic.src, alt: "", width: String(pic.w), height: String(pic.h), style: FILL };
    if (!S(frame)) {
      // A box the file doesn't hold: the picture replaces what the box showed, as one edit operation.
      const at = L(frame), was = frame.innerHTML, st = frame.getAttribute("style");
      const img = h("img", attrs);
      const fcs = getComputedStyle(frame), size0 = frame.getBoundingClientRect();
      const extra = {};
      if (fcs.position === "static") extra.position = ["relative", ""];
      if (fcs.overflowX === "visible" && fcs.overflowY === "visible") extra.overflow = ["hidden", ""];
      run(withOps({
        label: "Add picture",
        do: () => { frame.replaceChildren(img); Object.entries(extra).forEach(([k, [v]]) => frame.style.setProperty(k, v)); },
        undo: () => { frame.innerHTML = was; if (st === null) frame.removeAttribute("style"); else frame.setAttribute("style", st); },
      }, () => [markOp({ t: "html", at, v: frame.innerHTML }, frame), ...(Object.keys(extra).length ? [markOp({ t: "style", at, v: extra }, frame)] : [])]));
      const now0 = frame.getBoundingClientRect();
      if (size0.height - now0.height > 1) run(styleCmd(frame, "aspect-ratio", `${Math.round(size0.width)} / ${Math.round(size0.height)}`, false, "Keep the box's size"));
      select(img);
      toast("Picture added. Drag it to choose which part shows.");
      return;
    }
    const img = h("img", attrs), simg = srcDoc.createElement("img");
    Object.entries(attrs).forEach(([k, v]) => simg.setAttribute(k, v));
    adopt(img);
    toSrc.set(img, simg);
    const size = frame.getBoundingClientRect();
    const cs = getComputedStyle(frame);
    const cmds = [
      ...[...frame.children].filter((c) => S(c) && inFlow(c)).map((c) => removeCmd(c, "Remove placeholder label")),
      clearTextCmd(frame),
      insertImgCmd(frame, img, simg),
    ];
    if (cs.position === "static") cmds.push(styleCmd(frame, "position", "relative", false, "Frame the picture"));
    if (cs.overflowX === "visible" && cs.overflowY === "visible") cmds.push(styleCmd(frame, "overflow", "hidden", false, "Frame the picture"));
    run(group("Add picture", cmds));
    // If the label was what gave the box its height, keep the size the box had.
    const now = frame.getBoundingClientRect();
    if (size.height - now.height > 1) {
      const keep = styleCmd(frame, "aspect-ratio", `${Math.round(size.width)} / ${Math.round(size.height)}`, false, "Keep the box's size");
      keep.do();
      cmds.push(keep);
      changed();
    }
    select(img);
    toast(pic.local ? "Picture added into the page itself. Save with ⌘S." : "Picture added. Drag it to choose which part shows.");
  };

  // Framing a picture in its box: fill or fit, which part shows, and zoom. Saved as inline styles on the <img>.
  const FRAME_PROPS = ["object-fit", "object-position", "transform", "transform-origin"];
  const readFrame = (n) => Object.fromEntries(FRAME_PROPS.map((p) => [p, n ? n.style.getPropertyValue(p) : ""]));
  const writeFrame = (n, f) => FRAME_PROPS.forEach((p) => setProp(n, p, f[p]));
  const frameCmd = (img, before, after, label) => {
    const s = S(img), sBefore = readFrame(s);
    const ov = O(img), at = ov ? L(img) : null;
    return withOps(
      { label, do: () => { writeFrame(img, after); if (s) writeFrame(s, after); }, undo: () => { writeFrame(img, before); if (s) writeFrame(s, sBefore); } },
      () => (ov ? [markOp({ t: "style", at, v: Object.fromEntries(FRAME_PROPS.map((p) => [p, after[p] ? [after[p], ""] : null])) }, img)] : []),
    );
  };
  const framed = (img) => /^(cover|contain)$/.test(getComputedStyle(img).objectFit);
  const framedImg = (n) => { const i = n && imgOf(n); return i && ED(i) && framed(i) ? i : null; };
  const frameOf = (img) => {
    const cs = getComputedStyle(img);
    const [x = 50, y = 50] = cs.objectPosition.split(/\s+/).map((v) => (/%$/.test(v) ? parseFloat(v) : 50));
    const z = parseFloat((img.style.transform.match(/scale\(\s*([\d.]+)/) || [])[1]) || 1;
    return { fit: cs.objectFit, x, y, z: Math.max(1, z) };
  };
  const pct = (v) => `${Math.round(v * 10) / 10}%`;
  // Zoom scales around the point that shows, so zooming in or out keeps that part in view.
  const framing = (base, m) => {
    const pos = `${pct(m.x)} ${pct(m.y)}`, zoomed = m.z > 1.004;
    return { ...base, "object-position": pos, transform: zoomed ? `scale(${Math.round(m.z * 100) / 100})` : "", "transform-origin": zoomed ? pos : "" };
  };
  // How far the picture overhangs its box on each axis, in pixels (negative: it's smaller than the box).
  const overhang = (img, m) => {
    const bw = img.offsetWidth, bh = img.offsetHeight;
    const nw = img.naturalWidth || bw, nh = img.naturalHeight || bh;
    const s = (m.fit === "contain" ? Math.min : Math.max)(bw / nw, bh / nh);
    return [m.z * nw * s - bw, m.z * nh * s - bh];
  };
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

  // Dragging a framed picture moves it inside its box. Only the live page changes until you let go.
  let pan = null;
  const startPan = (e, img) => {
    const m = frameOf(img);
    pan = { img, m, before: readFrame(img), over: overhang(img, m), x: e.clientX, y: e.clientY, moved: false };
    try { img.setPointerCapture(e.pointerId); } catch {}
  };
  const movePan = (e) => {
    const dx = e.clientX - pan.x, dy = e.clientY - pan.y;
    if (!pan.moved && Math.hypot(dx, dy) < 3) return;
    if (!pan.moved) { pan.moved = true; setProp(root, "cursor", "grabbing", "important"); }
    const [ox, oy] = pan.over;
    const x = Math.abs(ox) < 1 ? pan.m.x : clamp(pan.m.x - (dx / ox) * 100, 0, 100);
    const y = Math.abs(oy) < 1 ? pan.m.y : clamp(pan.m.y - (dy / oy) * 100, 0, 100);
    writeFrame(pan.img, framing(pan.before, { ...pan.m, x, y }));
  };
  const endPan = () => {
    const p = pan;
    pan = null;
    setProp(root, "cursor", "");
    if (p.moved) run(frameCmd(p.img, p.before, readFrame(p.img), "Move picture"));
  };
  // Pinch (or Ctrl + scroll) over the selected picture zooms it.
  let wheel = null, wheelTimer = 0;
  const wheelZoom = (e, img) => {
    if (!wheel) wheel = { img, before: readFrame(img), m: frameOf(img) };
    wheel.m.z = clamp(wheel.m.z * Math.exp(-clamp(e.deltaY, -25, 25) * 0.01), 1, 4);
    writeFrame(img, framing(wheel.before, wheel.m));
    clearTimeout(wheelTimer);
    wheelTimer = setTimeout(() => { const w = wheel; wheel = null; run(frameCmd(w.img, w.before, readFrame(w.img), "Zoom picture")); }, 350);
  };

  const pictureSlot = (frame) => {
    const b = h("button", { type: "button", class: "addpic" });
    b.innerHTML = svg("picture") + "<span>Add picture</span>";
    b.addEventListener("click", () => addPicture(frame));
    const tip = h("p", { class: "p-note" });
    tip.textContent = "This box stands in for a picture. Add one, or drop an image file onto it.";
    return [b, tip];
  };
  const frameControls = (img) => {
    const m = frameOf(img);
    const box = h("div", { class: "frame", role: "group", "aria-label": "Picture framing" });
    const seg = h("div", { class: "seg", role: "radiogroup", "aria-label": "How the picture fills its box" });
    [["cover", "Fill the box"], ["contain", "Show it whole"]].forEach(([fit, label]) => {
      const b = h("button", { type: "button", role: "radio", "aria-checked": String(m.fit === fit) });
      b.textContent = label;
      b.addEventListener("click", () => {
        if (m.fit === fit) return;
        const before = readFrame(img);
        run(frameCmd(img, before, { ...before, "object-fit": fit }, label));
      });
      seg.append(b);
    });
    const zoom = h("label", { class: "zoom" }, "<span>Zoom</span>");
    const range = h("input", { type: "range", min: "100", max: "400", step: "5", "aria-label": "Zoom" });
    range.value = String(Math.round(m.z * 100));
    const out = h("output");
    out.textContent = `${range.value}%`;
    let zb = null;
    range.addEventListener("input", () => {
      if (!zb) zb = readFrame(img);
      out.textContent = `${range.value}%`;
      writeFrame(img, framing(zb, { ...m, z: range.value / 100 }));
    });
    range.addEventListener("change", () => {
      if (!zb) return;
      const before = zb;
      zb = null;
      run(frameCmd(img, before, readFrame(img), "Zoom picture"));
    });
    zoom.append(range, out);
    const row = h("div", { class: "posrow" });
    const grid = h("div", { class: "pos", role: "group", "aria-label": "Which part of the picture shows" });
    const Y = ["top", "", "bottom"], X = ["left", "", "right"];
    [0, 50, 100].forEach((y, j) => [0, 50, 100].forEach((x, i) => {
      const name = [Y[j], X[i]].filter(Boolean).join(" ") || "center";
      const b = h("button", { type: "button", title: `Show the ${name}`, "aria-label": `Show the ${name}`, "aria-pressed": String(Math.abs(m.x - x) < 0.5 && Math.abs(m.y - y) < 0.5) });
      b.addEventListener("click", () => { const before = readFrame(img); run(frameCmd(img, before, framing(before, { ...m, x, y }), `Show the ${name}`)); });
      grid.append(b);
    }));
    const tip = h("p");
    tip.textContent = "Drag the picture to move it. Pinch or Ctrl + scroll on it to zoom.";
    row.append(grid, tip);
    box.append(seg, zoom, row);
    const f = readFrame(img);
    if (f["object-position"] || f.transform) {
      const reset = h("button", { type: "button", class: "pbtn" });
      reset.textContent = "Reset position and zoom";
      reset.addEventListener("click", () => run(frameCmd(img, f, { ...f, "object-position": "", transform: "", "transform-origin": "" }, "Reset picture")));
      box.append(reset);
    }
    return box;
  };

  // Dropping an image file: onto a placeholder adds it, onto a picture (or its box) replaces it.
  const dropTarget = (t) => {
    for (let n = t, k = 0; n && n !== body && k < 8; n = n.parentElement, k++) {
      if (n.localName === "img") return ED(n) ? { img: n } : null;
      if (isPlaceholder(n)) return { frame: n };
      const own = [...n.children].find((c) => c.localName === "img" && ED(c) && framed(c));
      if (own) return { img: own };
    }
    return null;
  };

  // ---------- Page colors (dock) ----------
  const PAGE_TARGETS = [
    { label: "Page background", sel: "html, body", prop: "background-color", el: () => body, bg: true },
    { label: "Page text", sel: "body", prop: "color", el: () => body },
  ];
  const openPageColors = (anchor, viaKeyboard) => {
    popover(anchor, (el) => {
      const vars = colorVars();
      const unset = (m, sel, prop) => { if (m.rules[sel]) { delete m.rules[sel][prop]; if (!Object.keys(m.rules[sel]).length) delete m.rules[sel]; } };
      const targets = [
        ...PAGE_TARGETS.map((t) => ({
          label: t.label,
          now: () => (t.bg ? getComputedStyle(body).backgroundColor : getComputedStyle(body).color),
          set: (v) => { const m = copyModel(sheetModel); if (v) (m.rules[t.sel] ||= {})[t.prop] = v; else unset(m, t.sel, t.prop); run(sheetCmd(m, `Change ${t.label.toLowerCase()}`)); },
          changed: () => Boolean((sheetModel.rules[t.sel] || {})[t.prop]),
        })),
        ...vars.map((v) => ({
          label: v.name,
          varName: v.name,
          now: () => getComputedStyle(root).getPropertyValue(v.name).trim(),
          set: (val) => { const m = copyModel(sheetModel); if (val) m.vars[v.name] = val; else delete m.vars[v.name]; run(sheetCmd(m, `Change ${v.name}`)); },
          changed: () => Boolean(sheetModel.vars[v.name]),
        })),
      ];
      el.append(popTitle(vars.length ? "Recolor the whole page" : "Recolor the whole page (it has no color variables)"));
      targets.forEach((t) => {
        const item = popItem(null, t.label + (t.changed() ? "  •" : ""), () => colorPop(anchor, {
          title: t.varName ? `${t.varName}: everything that uses it changes` : t.label,
          value: t.now(),
          noneLabel: "Original",
          literal: Boolean(t.varName),
          exclude: t.varName || null,
          onPick: (v) => { t.set(v); setTimeout(() => openPageColors(anchor, false), 0); },
        }));
        item.setAttribute("aria-haspopup", "dialog");
        const chip = h("span", { class: "chip", "aria-hidden": "true" }, "<i></i>");
        chip.firstChild.style.background = shown(t.now());
        item.prepend(chip);
        if (t.varName) item.querySelector("span:not(.chip)").style.fontFamily = 'ui-monospace, "SF Mono", Menlo, Consolas, monospace';
        el.append(item);
      });
      if (Object.keys(sheetModel.vars).length || Object.keys(sheetModel.rules).length) {
        el.append(popSep());
        el.append(popItem("reset", "Reset page-wide colors", () => { run(sheetCmd({ vars: {}, rules: {} }, "Reset page-wide colors")); openPop.rebuild(); }));
      }
      const tip = popTitle("To recolor one thing, click it on the page. To color words, select them and use the toolbar.");
      tip.style.fontWeight = "400";
      el.append(tip);
    }, { label: "Page colors", wide: true, returnFocus: anchor, viaKeyboard });
  };

  // ---------- Dock ----------
  const dock = h("div", { class: "dock", role: "toolbar", "aria-label": "Site editor" });
  const dockBtn = (icon, label, text = null) => {
    const b = h("button", { type: "button", class: "btn", "aria-label": label, title: label });
    b.innerHTML = svg(icon) + (text ? `<span class="lbl"></span>` : "");
    if (text) b.querySelector(".lbl").textContent = text;
    dock.append(b);
    return b;
  };
  const undoBtn = dockBtn("undo", "Undo (⌘Z)");
  const redoBtn = dockBtn("redo", "Redo (⇧⌘Z)");
  dock.append(h("span", { class: "sep", "aria-hidden": "true" }));
  const colorsBtn = dockBtn("palette", "Page colors", "Colors");
  colorsBtn.setAttribute("aria-haspopup", "dialog");
  colorsBtn.setAttribute("aria-expanded", "false");
  const saveBtn = dockBtn("save", "Save the page (⌘S)", "Save");
  saveBtn.hidden = true;
  const helpBtn = dockBtn("help", "How to edit");
  helpBtn.setAttribute("aria-haspopup", "dialog");
  helpBtn.setAttribute("aria-expanded", "false");
  const status = h("span", { class: "status", role: "status", hidden: "" });
  dock.append(status);
  // Done: back to the page as it normally is; the edit button brings the editor back.
  const doneBtn = dockBtn("check", "Done: back to the page (the edit button reopens the editor)", "Done");
  doneBtn.classList.add("done");
  undoBtn.addEventListener("click", undo);
  redoBtn.addEventListener("click", redo);
  colorsBtn.addEventListener("click", (e) => openPageColors(colorsBtn, viaKb(e)));
  doneBtn.addEventListener("click", () => { saveNow(); setEditing(false); });
  saveBtn.addEventListener("click", () => saveNow());
  helpBtn.addEventListener("click", (e) => popover(helpBtn, (el) => {
    el.append(popTitle("How to edit"));
    const ul = h("ul", { class: "help" });
    [
      "Click any element to select it. Its colors, picture, link and position show in the panel.",
      "Click text to type. Select words to format them with the toolbar at the top.",
      "<kbd>Alt</kbd> + <kbd>↑</kbd> selects the element around the selected one.",
      "<kbd>Esc</kbd> stops typing, then deselects.",
      "<kbd>⌘Z</kbd> / <kbd>Ctrl+Z</kbd> undoes, <kbd>⇧⌘Z</kbd> redoes.",
      "Colors (bottom left) recolors the page's background, text and color variables.",
      "Drag the ⠿ on the selected element's label to move it: drop it between its neighbours, or next to something like it elsewhere. Hold <kbd>⌥</kbd> / <kbd>Alt</kbd> while dragging to place it freely. You can also drag a selected box by itself.",
      "Size and spacing in the panel: text size, width, padding, space above and below, corners, border and opacity.",
      "Picture placeholders: select one and press Add picture, or drop an image file onto it. Drag a picture to move it inside its box; the panel sets zoom and fit.",
      "Done puts the page back as it normally is; the edit button at the bottom left opens the editor again.",
      mode === "server"
        ? (LAYER ? "Every change saves by itself, as an edit kept apart from the page's file, so it stays after the page is rebuilt." : "Every change saves into the page's file by itself.")
        : "<kbd>⌘S</kbd> / <kbd>Ctrl+S</kbd> saves the page.",
    ].forEach((t) => ul.append(h("li", {}, t)));
    el.append(ul);
    if (NOTE) { const p = h("p", { class: "p-note" }); p.textContent = NOTE; el.append(p); }
  }, { label: "How to edit", wide: true, returnFocus: helpBtn, viaKeyboard: viaKb(e) }));
  const updateHistoryButtons = () => { undoBtn.disabled = !hist.past.length; redoBtn.disabled = !hist.future.length; };

  // ---------- Saving: into the file (serve.py), or a copy you save yourself ----------
  let mode = "none";                // "server" (the project server) or "copy" (⌘S saves a copy)
  let version = null, opsVersion = null, saveTimer = 0, retryTimer = 0, inFlight = false, dirty = false, blocked = false, unsaved = false, fileHandle = null;
  let quietTimer = 0;
  const setStatus = (kind, text) => {
    status.dataset.state = kind;
    status.textContent = text;
    status.title = text;
    status.hidden = false;
    clearTimeout(quietTimer);
  };
  const flush = async () => {
    if (inFlight || !dirty || blocked) return;
    inFlight = true;
    dirty = false;
    clearTimeout(retryTimer);
    let ok = false;
    try {
      const ops = allOps();
      const payload = { ops };
      if (!LAYER) payload.html = serialize();
      const r = await fetch(`${API}save?page=${encodeURIComponent(PAGE)}`, { method: "PUT", cache: "no-store", headers: { "Content-Type": "application/json; charset=utf-8", "X-Site-Editor": "1", "X-Base-Version": version || "", "X-Ops-Version": opsVersion || "" }, body: JSON.stringify(payload) });
      const res = await r.json().catch(() => ({}));
      if (r.status === 409) {
        blocked = true;
        dirty = true;
        const what = res.error === "edits changed" ? "this page's edits were saved from another tab" : "the file changed on disk";
        setStatus("error", `Not saved: ${what}. Reload to get the latest version.`);
        toast(`Not saved: ${what}. Reload to get the latest version.`, "Reload", () => location.reload());
      } else if (r.ok && res.ok) {
        version = res.version;
        opsVersion = res.opsVersion;
        if (RT) RT.set(ops, { apply: false });
        ok = true;
      } else throw new Error(res.error || String(r.status));
    } catch {
      if (!blocked) {
        dirty = true;
        setStatus("error", "Couldn't save. Is the project server (localhost:8780) running? Retrying…");
        retryTimer = setTimeout(flush, 5000);
      }
    } finally {
      inFlight = false;
    }
    if (ok) {
      if (dirty) flush();
      else setStatus("saved", LAYER ? "Saved" : `Saved to ${FILE_NAME}`);
    }
  };
  const queueSave = () => {
    if (blocked) return;
    dirty = true;
    setStatus("saving", "Saving…");
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flush, 400);
  };
  const saveCopy = async () => {
    const text = serialize();
    try {
      if (window.showSaveFilePicker) {
        if (!fileHandle) fileHandle = await window.showSaveFilePicker({ suggestedName: FILE_NAME, types: [{ description: "Web page", accept: { "text/html": [".html", ".htm"] } }] });
        const w = await fileHandle.createWritable();
        await w.write(text);
        await w.close();
        unsaved = false;
        setStatus("saved", `Saved ${fileHandle.name}`);
        return;
      }
    } catch (err) {
      if (err && err.name === "AbortError") return;
      fileHandle = null;
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type: "text/html" }));
    a.download = FILE_NAME;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    unsaved = false;
    setStatus("saved", `Downloaded ${FILE_NAME}. Replace the original with it.`);
  };
  const saveNow = () => {
    commitText();
    if (mode === "server") { clearTimeout(saveTimer); if (!blocked) { dirty = true; flush(); } }
    else if (mode === "copy") saveCopy();
  };
  const changed = () => {
    updateHistoryButtons();
    if (activeHost && !activeHost.isConnected) { textSession = null; activeHost = null; bar.hidden = true; }
    if (textSession) textSession.before = textSession.host.innerHTML;
    if (selected && !selected.isConnected) selected = null;
    renderPanel();
    if (openPop && !openPop.anchor.isConnected) closePop(false);
    if (mode === "server") queueSave();
    else if (mode === "copy") { unsaved = true; setStatus("unsaved", "Unsaved changes. ⌘S saves the page."); }
  };

  // ---------- Page events while editing ----------
  // The page's own click / key handlers are paused while editing, so links don't navigate and buttons don't fire.
  const PAUSE = ["click", "dblclick", "auxclick", "mouseup", "pointerup", "touchstart", "touchend", "submit"];
  PAUSE.forEach((type) => window.addEventListener(type, (e) => {
    if (!editing || fromUI(e)) return;
    e.stopPropagation();
    if (type === "click" || type === "submit" || type === "auxclick") e.preventDefault();
    if (type === "pointerup") requestAnimationFrame(renderPanel);   // colors read after :active ends
  }, true));
  window.addEventListener("pointerdown", (e) => {
    if (!editing || fromUI(e)) return;
    e.stopPropagation();
    if (openPop) closePop(false);
    if (e.button !== 0 || e.clientX >= root.clientWidth || e.clientY >= root.clientHeight) return;   // not on a scrollbar
    const a = deepActive();
    if (a && shadow.contains(a)) a.blur();
    commitText();                                             // so what was just typed counts when deciding what was clicked
    const t = elOf(e.target);
    // A picture framed in a box: pressing selects it, dragging moves it inside the box.
    if (t && t.localName === "img" && ED(t) && framed(t)) {
      deactivateHost();
      if (selected !== t) select(t);
      startPan(e, t);
      return;
    }
    if (!t || !body.contains(t)) { deactivateHost(); select(body); return; }
    const host = hostFor(t);
    const picked = pickFor(t, host);
    // pressing a box that is already selected (not its text) and dragging moves it
    if (!host && picked === selected && movable(picked)) { deactivateHost(); startDrag(e, picked); return; }
    select(picked);
    if (host) activateHost(host); else deactivateHost();
    renderPanel();
  }, true);
  window.addEventListener("mousedown", (e) => {
    if (!editing || fromUI(e)) return;
    e.stopPropagation();
    if (!(activeHost && activeHost.contains(elOf(e.target)))) e.preventDefault();   // no focus, drag or text selection outside text areas
  }, true);
  window.addEventListener("dragstart", (e) => { if (editing && !fromUI(e)) e.preventDefault(); }, true);
  window.addEventListener("pointermove", (e) => {
    if (!editing || fromUI(e)) { hovered = null; return; }
    const t = elOf(e.target);
    hovered = t && body.contains(t) ? t : null;
  }, { capture: true, passive: true });
  root.addEventListener("mouseleave", () => { hovered = null; });
  window.addEventListener("pointermove", (e) => { if (pan) movePan(e); }, true);
  ["pointerup", "pointercancel"].forEach((type) => window.addEventListener(type, () => { if (pan) endPan(); }, true));

  // ---------- Dragging elements to a new place ----------
  // Drop between its neighbours, or next to an element like it elsewhere (a card into another column).
  // With ⌥ / Alt held, it moves freely instead (saved as an inline "translate").
  let drag = null;
  const movable = (n) => Boolean(n) && n !== body && n !== root && Boolean(n.parentElement) && n.parentElement !== root && ED(n) && body.contains(n);
  const shownEl = (c) => { const r = c.getBoundingClientRect(); return r.width > 0 || r.height > 0; };
  const alike = (a, n) => {
    if (a.localName !== n.localName || !ED(a) || !ED(a.parentElement)) return false;
    const ca = [...a.classList], cn = [...n.classList];
    return (!ca.length && !cn.length) || ca.some((c) => cn.includes(c));
  };
  const nearestChild = (p, n, x, y) => {
    let best = null, bd = Infinity;
    for (const c of p.children) {
      if (c === n || c === ui || !ED(c) || c.hasAttribute("data-lb-hidden") || !shownEl(c)) continue;
      const r = c.getBoundingClientRect();
      const dx = Math.max(r.left - x, 0, x - r.right), dy = Math.max(r.top - y, 0, y - r.bottom);
      const d = Math.hypot(dx, dy);
      if (d < bd) { bd = d; best = c; }
    }
    return best;
  };
  const rowOf = (ref) => {
    const r = ref.getBoundingClientRect();
    const nb = [ref.previousElementSibling, ref.nextElementSibling].find((c) => c && c !== ui && shownEl(c));
    if (!nb) { const cs = getComputedStyle(ref.parentElement); return /flex/.test(cs.display) && /^row/.test(cs.flexDirection); }
    const q = nb.getBoundingClientRect();
    return Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top) > Math.min(r.height, q.height) / 2;
  };
  const dropSpot = (n, x, y) => {
    const t = document.elementsFromPoint(x, y).find((el) => el !== ui && !ui.contains(el) && body.contains(el) && el !== n && !n.contains(el));
    if (!t) return null;
    let ref = null;
    for (let e = t; e && e !== root; e = e.parentElement) {
      if (e.contains(n)) { ref = nearestChild(n.parentElement, n, x, y); break; }   // over its own list: the nearest neighbour
      if (e === body) break;
      if (e.parentElement === n.parentElement || alike(e, n)) { ref = e; break; }
    }
    if (!ref || !ED(ref)) return null;
    const r = ref.getBoundingClientRect(), row = rowOf(ref);
    const rtl = getComputedStyle(ref.parentElement).direction === "rtl";
    const before = row ? (rtl ? x > r.left + r.width / 2 : x < r.left + r.width / 2) : y < r.top + r.height / 2;
    return { ref, before, row, rtl, r };
  };
  const showDropLine = (spot) => {
    if (!spot) { dropLine.hidden = true; return; }
    const { r, row, before, rtl } = spot;
    dropLine.hidden = false;
    if (row) {
      const atLeft = before !== rtl;
      Object.assign(dropLine.style, { left: `${(atLeft ? r.left : r.right) - 2}px`, top: `${r.top}px`, width: "3px", height: `${r.height}px` });
    } else Object.assign(dropLine.style, { left: `${r.left}px`, top: `${(before ? r.top : r.bottom) - 2}px`, width: `${r.width}px`, height: "3px" });
  };
  const readTranslate = (n) => { const [x = 0, y = 0] = (n.style.getPropertyValue("translate") || "").split(/\s+/).map((v) => parseFloat(v) || 0); return [x, y]; };
  const startDrag = (e, n) => {
    if (e.button !== 0 || !movable(n)) return;
    const [tx, ty] = readTranslate(n);
    drag = { n, x: e.clientX, y: e.clientY, tx, ty, moved: false, spot: null, free: false, had: [n.style.getPropertyValue("translate"), n.style.getPropertyPriority("translate")] };
  };
  const moveDrag = (e) => {
    const d = drag, dx = e.clientX - d.x, dy = e.clientY - d.y;
    if (!d.moved && Math.hypot(dx, dy) < 4) return;
    if (!d.moved) { d.moved = true; setProp(root, "cursor", "grabbing", "important"); selBox.classList.add("dragging"); }
    d.free = e.altKey;
    if (d.free) {
      d.n.style.setProperty("translate", `${Math.round(d.tx + dx)}px ${Math.round(d.ty + dy)}px`, "important");
      d.spot = null;
      showDropLine(null);
      return;
    }
    setProp(d.n, "translate", d.had[0], d.had[1]);
    d.spot = dropSpot(d.n, e.clientX, e.clientY);
    showDropLine(d.spot);
  };
  const cancelDrag = () => {
    if (!drag) return;
    const d = drag;
    drag = null;
    setProp(d.n, "translate", d.had[0], d.had[1]);
    setProp(root, "cursor", "");
    selBox.classList.remove("dragging");
    showDropLine(null);
  };
  const endDrag = () => {
    const d = drag;
    if (!d) return;
    const free = d.free && d.n.style.getPropertyValue("translate");
    cancelDrag();
    if (!d.moved) return;
    if (free) { run(styleCmd(d.n, "translate", free, true, "Move freely")); announce("Moved."); return; }
    const s = d.spot;
    if (!s || s.ref === d.n) return;
    if ((s.before && s.ref.previousElementSibling === d.n) || (!s.before && s.ref.nextElementSibling === d.n)) return;   // already there
    run(moveCmd(d.n, s.ref, s.before, "Move"));
    select(d.n);
    announce("Moved.");
  };
  grip.addEventListener("pointerdown", (e) => {
    if (!selected) return;
    e.preventDefault();
    if (activeHost && (selected === activeHost || selected.contains(activeHost) || activeHost.contains(selected))) deactivateHost();
    startDrag(e, selected);
  });
  window.addEventListener("pointermove", (e) => { if (drag) moveDrag(e); }, true);
  window.addEventListener("pointerup", () => { if (drag) endDrag(); }, true);
  window.addEventListener("pointercancel", () => cancelDrag(), true);
  window.addEventListener("wheel", (e) => {
    if (!editing || !e.ctrlKey || fromUI(e)) return;
    const img = framedImg(selected);
    if (!img || elOf(e.target) !== img) return;
    e.preventDefault();
    wheelZoom(e, img);
  }, { capture: true, passive: false });

  document.addEventListener("selectionchange", () => {
    if (!activeHost) return;
    const sel = getSelection();
    if (!sel.rangeCount || !activeHost.contains(elOf(sel.anchorNode))) return;
    savedRange = sel.getRangeAt(0).cloneRange();
    updateBar();
  });
  document.addEventListener("input", (e) => {
    const host = activeHost;
    if (!host || !host.contains(elOf(e.target))) return;
    if (pendingStyle && host.querySelector(`font[face="${SENTINEL}"]`)) { convertSentinels(host, pendingStyle.prop, pendingStyle.value); pendingStyle = null; }
    scheduleCommit();
  }, true);
  document.addEventListener("paste", (e) => {
    if (!activeHost || !activeHost.contains(elOf(e.target))) return;
    e.preventDefault();
    e.stopPropagation();
    const text = (e.clipboardData && e.clipboardData.getData("text/plain")) || "";
    document.execCommand("insertText", false, isFlowHost() ? text : text.replace(/\s*\n\s*/g, " "));
  }, true);
  const draggingFiles = (e) => Boolean(e.dataTransfer && [...e.dataTransfer.types].includes("Files"));
  document.addEventListener("dragover", (e) => {
    if (!editing || fromUI(e) || !draggingFiles(e)) return;
    e.preventDefault();
    const d = dropTarget(elOf(e.target));
    e.dataTransfer.dropEffect = d ? "copy" : "none";
    hovered = d ? d.img || d.frame : null;
  }, true);
  document.addEventListener("dragleave", (e) => { if (!e.relatedTarget) hovered = null; }, true);
  document.addEventListener("drop", (e) => {
    if (!editing || fromUI(e)) return;
    e.preventDefault();
    const file = [...((e.dataTransfer && e.dataTransfer.files) || [])].find((f) => /^image\//.test(f.type));
    if (!file) return;
    const d = dropTarget(elOf(e.target));
    if (!d) { toast("Drop pictures onto a picture or a picture placeholder."); return; }
    if (d.img) { select(d.img); replacePicture(d.img, file); } else addPicture(d.frame, file);
  }, true);

  // ---------- Keyboard ----------
  window.addEventListener("keydown", (e) => {
    if (!srcDoc) return;
    const mod = e.metaKey || e.ctrlKey;
    const k = e.key.toLowerCase();
    const inUI = fromUI(e);
    const target = inUI ? deepActive() : elOf(e.target);
    const inHost = !inUI && Boolean(activeHost && target && activeHost.contains(target));
    const inField = Boolean(target && target.matches && target.matches("input, textarea, select"));
    if (!editing) return;
    if (mod && k === "s") { e.preventDefault(); e.stopPropagation(); saveNow(); return; }
    if (e.key === "Escape" && drag) { e.preventDefault(); e.stopPropagation(); cancelDrag(); return; }
    if (e.key === "Escape") {
      if (openPop) { e.preventDefault(); closePop(true); return; }
      if (inUI && activeHost && bar.contains(target)) { e.preventDefault(); restoreSelection(); return; }
      if (activeHost) { e.preventDefault(); deactivateHost(); renderPanel(); return; }
      if (selected) { e.preventDefault(); deselect(); return; }
    }
    if (inHost) {
      e.stopPropagation();                                   // the page's own shortcuts stay quiet while typing
      if (mod && k === "k") { e.preventDefault(); openLink(tb.link, false); return; }
      if (e.key === "Enter" && !e.isComposing && !isFlowHost()) { e.preventDefault(); document.execCommand("insertLineBreak"); return; }
      if (e.altKey && e.key === "F10") { e.preventDefault(); bar.querySelector("button:not(:disabled)").focus(); }
      return;
    }
    if (!inUI) e.stopPropagation();
    if (inField) return;
    if (mod && k === "z") { e.preventDefault(); if (e.shiftKey) redo(); else undo(); return; }
    if (mod && k === "y") { e.preventDefault(); redo(); return; }
    if (inUI || !selected) return;
    if (e.altKey && e.key === "ArrowUp") { e.preventDefault(); if (selected !== body && selected.parentElement) select(selected.parentElement); return; }
    if ((e.key === "Delete" || e.key === "Backspace") && ED(selected) && selected !== body) { e.preventDefault(); remove(selected); return; }
    if (e.key === "Enter") {
      const host = hostFor(selected);
      if (host) { e.preventDefault(); activateHost(host); placeCaret(host); renderPanel(); }
    }
  }, true);
  window.addEventListener("beforeunload", (e) => {
    if (commitTimer) commitText();
    if ((mode === "server" && (dirty || inFlight)) || (mode === "copy" && unsaved)) { e.preventDefault(); e.returnValue = ""; }
  });

  // ---------- Outlines follow their elements ----------
  const place = (box, n, label) => {
    if (!n || !n.isConnected || !editing) { box.hidden = true; return; }
    const r = n.getBoundingClientRect();
    if (!r.width && !r.height) { box.hidden = true; return; }
    box.hidden = false;
    box.style.left = `${r.left}px`;
    box.style.top = `${r.top}px`;
    box.style.width = `${r.width}px`;
    box.style.height = `${r.height}px`;
    if (label !== undefined) {
      if (selText.textContent !== label) selText.textContent = label;
      const canMove = movable(n);
      if (grip.hidden === canMove) grip.hidden = !canMove;
      box.classList.toggle("flip", r.top < 28);
    }
  };
  const tick = () => {
    if (editing) {
      place(hoverBox, hovered && hovered !== selected && hovered !== activeHost ? hovered : null);
      place(hostBox, activeHost && activeHost !== selected ? activeHost : null);
      place(selBox, selected, selected ? describe(selected).code + (selected.localName === "img" && framedImg(selected) ? "  ·  drag to move" : "") : "");
      if (selected && !panel.hidden && innerWidth > 640) {
        const r = selected.getBoundingClientRect();
        const covers = (x) => r.right > x && r.bottom > innerHeight - panel.offsetHeight - 24 && r.top < innerHeight;
        const aside = panel.classList.contains("aside");
        if (!aside && covers(innerWidth - 332) && !(r.left < 332)) panel.classList.add("aside");
        else if (aside && (!covers(innerWidth - 332) || r.left < 332)) panel.classList.remove("aside");
      }
      if (activeHost && !bar.hidden) {
        const r = activeHost.getBoundingClientRect();
        const zone = 10 + bar.offsetHeight + 12;
        bar.classList.toggle("low", r.top < zone && r.bottom > 0 && r.bottom < innerHeight - zone - 70);
      }
    }
    requestAnimationFrame(tick);
  };

  const setEditing = (on) => {
    editing = on;
    if (!on) { cancelDrag(); deactivateHost(); closePop(false); hovered = null; selected = null; toastEl.hidden = true; }
    [hoverBox, hostBox, selBox].forEach((b) => { if (!on) b.hidden = true; });
    dock.hidden = !on && SERVED;
    colorsBtn.disabled = !on;
    // the runtime stays out of the way while the editor changes the page, and takes over again after Done
    if (RT && OVL) { if (on) RT.pause(); else RT.resume(); }
    if (window.__lbEditButton) { if (on) window.__lbEditButton.hide(); else window.__lbEditButton.show(); }
    renderPanel();
  };
  window.__siteEditorOpen = () => { if (mode !== "none") setEditing(true); };

  // ---------- Start ----------
  const EMPTY = "<!doctype html>\n<html><head></head><body></body></html>\n";
  const start = async () => {
    let text = "";
    if (SERVED) {
      try {
        const r = await fetch(`${API}info?page=${encodeURIComponent(PAGE)}`, { cache: "no-store", headers: { "X-Site-Editor": "1" } });
        const info = await r.json();
        if (r.ok && info.ok) {
          mode = "server";
          version = info.version || null;
          opsVersion = info.opsVersion || null;
          baseOps = Array.isArray(info.ops) ? info.ops : [];
          // another tab saved edits since this page was shown: show them before editing on top
          if (RT && JSON.stringify(RT.ops) !== JSON.stringify(baseOps)) RT.set(baseOps);
        }
      } catch {}
      if (mode === "server" && !LAYER) {
        try {
          const r = await fetch(`${API}source?page=${encodeURIComponent(PAGE)}`, { cache: "no-store", headers: { "X-Site-Editor": "1" } });
          if (r.ok) { text = await r.text(); version = r.headers.get("X-Version"); } else mode = "none";
        } catch { mode = "none"; }
      } else if (mode === "server") text = EMPTY;   // layer mode: nothing of the file is edited, only the list of edits
    } else if (/^https?:$/.test(location.protocol)) {
      try {
        const r = await fetch(location.href.split("#")[0], { cache: "no-store" });
        if (r.ok && /html/i.test(r.headers.get("Content-Type") || "")) text = await r.text();
      } catch {}
    }
    if (!text && !SERVED) text = early;
    root.append(ui);
    wrap.append(bar, panel, dock);
    if (!text) {
      mode = "none";
      [undoBtn, redoBtn, colorsBtn].forEach((b) => { b.disabled = true; });
      setStatus("error", "Couldn't reach the project server (localhost:8780), so editing is off. Reload to try again.");
      if (window.__lbEditButton) window.__lbEditButton.hide();
      return;
    }
    if (mode !== "server") mode = "copy";
    srcDoc = new DOMParser().parseFromString(text, "text/html");
    selfClosingSvg = /<(path|circle|rect|line|polyline|polygon|ellipse|use|stop)\b[^<>]*\/>/i.test(text);
    bareAttrs = findBareAttrs(text);
    headGap = (text.match(/<html[^>]*>(\s*)<head[\s>]/i) || [, "\n"])[1];
    const end = text.match(/(\s*)<\/body>(\s*)<\/html>(\s*)$/i);
    if (end) tail = [end[1], end[2], end[3]];
    const at = text.search(/<html[\s>]/i);
    srcPrefix = at >= 0 ? text.slice(0, at) : ((text.match(/^\s*<!doctype[^>]*>\s*/i) || ["<!doctype html>\n"])[0]);
    if (!LAYER) align(root, srcDoc.documentElement);
    readSheet();
    try { document.execCommand("defaultParagraphSeparator", false, "p"); } catch {}
    saveBtn.hidden = mode !== "copy";
    doneBtn.hidden = !SERVED;
    updateHistoryButtons();
    setEditing(true);
    requestAnimationFrame(tick);
    if (mode === "server") {
      const lost = RT ? RT.missing : 0;
      if (lost) setStatus("warn", `${lost} earlier edit${lost > 1 ? "s" : ""} couldn't find ${lost > 1 ? "their" : "its"} place: the page changed since.`);
      else setStatus("saved", LAYER ? "Editing. Changes save by themselves." : `Editing ${FILE_NAME}. Changes save by themselves.`);
    } else setStatus("saved", "Editing. ⌘S saves the page.");
  };
  if (document.readyState === "complete") setTimeout(start, 0);
  else window.addEventListener("load", () => setTimeout(start, 0), { once: true });
})();
