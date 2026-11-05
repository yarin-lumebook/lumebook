/*!
 * LumeBook page edits: the runtime. It applies the edits made with the edit button to this page, and applies them
 * again whenever the page's own scripts redraw part of it. Source: shared/site-editor/overlay.js (README there).
 * The project server adds it to every page it shows; pages that have edits also carry a copy (the lumebook-edits
 * block before </body>), so the artifact and Vercel copies show the same page.
 *
 * Edits are a list of operations on elements. An element is found by its path from the nearest element with an id
 * (or from <body>), checked against the first words it had before it was edited; when the page moved things around,
 * the one element of that kind with the same words is used instead. Nothing is guessed: an edit whose element is
 * gone is skipped and counted (window.__lbEdits.missing).
 */
(() => {
  "use strict";
  if (window.__lbEdits || !document.body) return;
  const body = document.body;
  const known = new WeakSet(document.querySelectorAll("*"));   // elements that came from the file (the editor's source mode)
  const origSig = new WeakMap();                                // element -> its words before the first edit touched it
  const done = new WeakMap(), doneRef = new WeakMap(), seen = new WeakMap();

  const skip = (c) => c.hasAttribute("data-site-editor") || c.hasAttribute("data-lb-ui") || (c.localName === "script" && /^lumebook-edits/.test(c.id));
  const kids = (p, tag) => { const out = []; if (p) for (const c of p.children) if (c.localName === tag && !skip(c)) out.push(c); return out; };
  const norm = (s) => (s || "").replace(/\s+/g, " ").trim();
  const sigText = (n, text) => {
    const t = norm((text === undefined ? n.textContent || "" : text).slice(0, 2000)).slice(0, 60);
    if (t) return t;
    if (n.localName === "img") return "img:" + (n.getAttribute("src") || "").slice(-60);
    return n.localName + ":" + norm(n.getAttribute("class") || "").slice(0, 40);
  };
  const sigOf = (n) => (origSig.has(n) ? origSig.get(n) : sigText(n));
  // Remember an element's words before an edit changes them, so every later edit still finds it by them.
  const touch = (n, sigBefore) => { if (n && n.nodeType === 1 && !origSig.has(n)) origSig.set(n, sigBefore !== undefined ? sigBefore : sigText(n)); };
  const uniqueId = (id) => { try { return id.length <= 80 && document.querySelectorAll("#" + CSS.escape(id)).length === 1; } catch { return false; } };
  const pathFrom = (anc, n) => {
    const p = [];
    for (let e = n; e && e !== anc; e = e.parentElement) {
      if (!e.parentElement) return null;
      p.unshift([e.localName, kids(e.parentElement, e.localName).indexOf(e)]);
    }
    return p;
  };
  // Where an element is: { a: anchor id | e: inserted copy id, p: path from it, b: path from <body>, s: its words }.
  const locate = (n) => {
    if (!n || n.nodeType !== 1) return null;
    if (n === body) return { body: 1 };
    if (!body.contains(n)) return null;
    const L = { s: sigOf(n) };
    for (let e = n; e && e !== body; e = e.parentElement) {
      const x = e.getAttribute("data-lb-edit");
      if (x) { L.e = x; L.p = pathFrom(e, n); break; }
      if (e.id && uniqueId(e.id)) { L.a = e.id; L.p = pathFrom(e, n); break; }
    }
    L.b = pathFrom(body, n);
    if (!L.p) L.p = L.b;
    return L;
  };
  const walk = (start, p) => {
    let e = start;
    for (const [tag, i] of p || []) { e = kids(e, tag)[i]; if (!e) return null; }
    return e;
  };
  const find = (L) => {
    if (!L) return null;
    if (L.body) return body;
    const start = L.e ? document.querySelector(`[data-lb-edit="${CSS.escape(L.e)}"]`) : L.a ? document.getElementById(L.a) : null;
    if (start && (!L.p || !L.p.length)) return start;          // the element has its own id: that is enough
    const tries = [];
    if (start) tries.push(walk(start, L.p));
    if (L.b) tries.push(walk(body, L.b));
    for (const t of tries) if (t && sigOf(t) === L.s) return t;
    // moved or redrawn in another order by the page: the one element of that kind with the same words
    const tag = (L.p && L.p.length ? L.p[L.p.length - 1] : (L.b || [])[(L.b || []).length - 1] || [])[0];
    if (!tag) return null;
    const all = (start || body).getElementsByTagName(tag);
    if (all.length > 4000) return null;
    let hit = null;
    for (const c of all) if (!skip(c) && sigOf(c) === L.s) { if (hit) return null; hit = c; }   // two alike: don't guess
    return hit;
  };
  const live = (m, op) => { const el = m.get(op); return el && el.isConnected ? el : null; };
  const probe = document.createElement("i");
  const normProp = (k, v, prio) => { probe.style.setProperty(k, v, prio || ""); const out = probe.style.getPropertyValue(k); probe.removeAttribute("style"); return out; };

  const applyOne = (op) => {
    switch (op.t) {
      case "html": {
        const prev = live(done, op);
        if (prev && prev.innerHTML === seen.get(op)) return true;
        const el = find(op.at);
        if (!el) return Boolean(prev);
        touch(el, op.at.s);
        el.innerHTML = op.v;
        done.set(op, el);
        seen.set(op, el.innerHTML);
        return true;
      }
      case "style": {
        const el = live(done, op) || find(op.at);
        if (!el) return false;
        touch(el, op.at.s);
        for (const [k, v] of Object.entries(op.v || {})) {
          if (!v) { if (el.style.getPropertyValue(k)) el.style.removeProperty(k); continue; }
          const [val, prio = ""] = v;
          if (el.style.getPropertyValue(k) !== normProp(k, val, prio) || el.style.getPropertyPriority(k) !== prio) el.style.setProperty(k, val, prio);
        }
        if (!(el.getAttribute("style") || "").trim()) el.removeAttribute("style");
        done.set(op, el);
        return true;
      }
      case "attr": {
        const el = live(done, op) || find(op.at);
        if (!el) return false;
        touch(el, op.at.s);
        if (op.v === null) { if (el.hasAttribute(op.n)) el.removeAttribute(op.n); } else if (el.getAttribute(op.n) !== op.v) el.setAttribute(op.n, op.v);
        done.set(op, el);
        return true;
      }
      case "hide": case "show": {
        const el = live(done, op) || find(op.at);
        if (!el) return false;
        touch(el, op.at.s);
        if (op.t === "hide") {
          if (el.style.getPropertyValue("display") !== "none") el.style.setProperty("display", "none", "important");
          el.setAttribute("data-lb-hidden", "");
        } else if (el.hasAttribute("data-lb-hidden")) {
          el.style.removeProperty("display");
          if (!(el.getAttribute("style") || "").trim()) el.removeAttribute("style");
          el.removeAttribute("data-lb-hidden");
        }
        done.set(op, el);
        return true;
      }
      case "move": {
        const el = live(done, op) || find(op.at);
        const ref = live(doneRef, op) || find(op.to);
        if (!el || !ref || el === ref || el.contains(ref)) return false;
        touch(el, op.at.s);
        touch(ref, op.to.s);
        if (op.pos === "before" ? ref.previousElementSibling !== el : op.pos === "after" ? ref.nextElementSibling !== el : el.parentElement !== ref) {
          if (op.pos === "before") ref.before(el); else if (op.pos === "after") ref.after(el); else ref.append(el);
        }
        done.set(op, el);
        doneRef.set(op, ref);
        return true;
      }
      case "insert": {
        if (document.querySelector(`[data-lb-edit="${CSS.escape(op.id)}"]`)) return true;
        const ref = find(op.at);
        if (!ref) return false;
        touch(ref, op.at.s);
        const t = document.createElement("template");
        t.innerHTML = op.v;
        const node = t.content.firstElementChild;
        if (!node) return false;
        if (op.pos === "before") ref.before(node); else ref.after(node);
        return true;
      }
      case "tag": {
        const prev = live(done, op);
        if (prev && prev.localName === op.v) return true;
        const el = find(op.at);
        if (!el) return Boolean(prev);
        const m = document.createElement(op.v);
        for (const a of el.attributes) m.setAttribute(a.name, a.value);
        m.append(...el.childNodes);
        el.replaceWith(m);
        origSig.set(m, op.at.s);
        done.set(op, m);
        return true;
      }
      case "css": return true;   // applied once, below: the last one wins
      default: return true;
    }
  };

  let ops = [], paused = false, missing = 0;
  const applyCss = () => {
    const last = [...ops].reverse().find((o) => o.t === "css");
    let st = document.getElementById("site-editor-styles");
    if (!last) return;
    if (!st) { st = document.createElement("style"); st.id = "site-editor-styles"; document.head.append(st); }
    if (st.textContent !== last.v) st.textContent = last.v;
  };
  // Right after the page's script changed the page (a microtask, before it is painted), so the old words never flash;
  // applyAll stops listening while it works, so its own changes don't call it again.
  const observer = new MutationObserver(() => { if (!paused) applyAll(); });
  const listen = () => observer.observe(body, { childList: true, subtree: true });
  const applyAll = () => {
    if (paused) return;
    observer.disconnect();
    let miss = 0;
    try {
      applyCss();
      for (const op of ops) { try { if (!applyOne(op)) miss++; } catch { miss++; } }
    } finally {
      missing = miss;
      observer.takeRecords();
      if (ops.length) listen();
    }
  };

  try {
    const tag = document.getElementById("lumebook-edits");
    const data = tag ? JSON.parse(tag.textContent || "{}") : {};
    ops = Array.isArray(data.ops) ? data.ops : [];
  } catch { ops = []; }

  window.__lbEdits = {
    known,
    get ops() { return ops; },
    get missing() { return missing; },
    // the editor hands over the whole list after each save; it applies them itself while it is open
    set(list, { apply = true } = {}) { ops = Array.isArray(list) ? list : []; if (apply) applyAll(); },
    pause() { paused = true; observer.disconnect(); },
    resume() { paused = false; applyAll(); },
    apply: applyAll,
    locate, find, sigOf, sigText, touch,
    // an edit the editor just made on this element (so it isn't applied a second time)
    mark(op, el, ref) { if (el) { done.set(op, el); if (op.t === "html") seen.set(op, el.innerHTML); } if (ref) doneRef.set(op, ref); },
  };
  if (ops.length) applyAll();
  // pages that draw their content after loading (data fetched, tabs built) get the edits as soon as it appears
  document.addEventListener("DOMContentLoaded", () => { if (ops.length) applyAll(); });
  window.addEventListener("load", () => { if (ops.length) applyAll(); });
})();
