/* The language switch (Yarin, 08 Nov 2026: "i want the entire project in hebrew and english with a toggle that appears
   everywhere to switch between them"). Source: shared/design/i18n.src.js; design.py puts it in nav.js in front of the
   project nav, which draws the switch (עב | EN) as a capsule floating at the bottom left, right of the edit button. Server side and dictionaries: tools/i18n.py, shared/i18n/README.md.
   - The choice is kept in this browser (localStorage "lb-lang"). Until it is used a page shows the language it was written
     in; once it is set, every page shows that language: the page's words are swapped in place from its dictionaries
     (the lumebook-i18n block the server adds or the build bakes in), <html> gets lang and dir, and Hebrew containers
     (dir="rtl", lang="he") turn left to right in English, English ones (lang="en") right to left in Hebrew.
   - A key is the text of one block of the page (a paragraph, a button, a cell): its text pieces in order, joined by
     U+001F, white space collapsed, every number written {0} {1} ... so "12 יוצרים" and "13 יוצרים" share one entry.
   - Never touched: fields, editable text, code, the edit button, and anything inside translate="no" or SKIP below. The
     edit button calls suspend() before it opens and resume() when it closes, so an edit never saves a translation.
   - On the project server (:8780) words the dictionaries lack are reported (POST /api/i18n/missing); the server
     translates them in the background and the page polls GET /api/i18n/dict until they arrive. */
(() => {
  "use strict";
  if (window.LBI18N) return;
  const STORE = "lb-lang", SEP = "\u001f";
  const HE = /[֐-׿]/, NUM = /\d+(?:[.,:]\d+)*/g, PH = /\{(\d+)\}/g;
  const root = document.documentElement;
  let ON_SERVER = false;   // set by the page's words block: the project server adds "live" (a baked copy has no one to ask)
  // never translated: Hebrew copy for parents (carousel slides .sty, text blocks people copy), editable text, the edit button
  const SKIP = '[translate="no"], .notranslate, [data-i18n="off"], .lb-editable, .lb-textblock, .sty, [data-lb-ui], [data-site-editor], .lb-langfab';
  const SKIP_TAGS = new Set(["script", "style", "noscript", "textarea", "input", "code", "pre", "kbd", "samp", "template", "iframe", "object", "canvas", "video", "audio", "math"]);
  const SKIP_UP = [...SKIP_TAGS].join(",") + "," + SKIP;
  const INLINE = new Set(["a", "abbr", "b", "bdi", "bdo", "cite", "data", "dfn", "em", "i", "mark", "q", "s", "small", "span", "strong", "sub", "sup", "time", "u", "var", "font", "del", "ins", "br", "wbr", "img"]);
  const ATTRS = ["placeholder", "title", "aria-label", "alt", "data-ph"];
  const COMMON = ".lb-gside, .lb-gbottom, .lb-gscrim, .lb-selmenu, .lb-cal, .lb-timepick, [data-i18n-scope='common']";
  const FIELD = new Set(["input", "textarea", "select", "option"]);

  const readPref = () => { try { const v = localStorage.getItem(STORE); return v === "he" || v === "en" ? v : null; } catch { return null; } };
  const writePref = (v) => { try { localStorage.setItem(STORE, v); } catch {} };
  const q = new URLSearchParams(location.search).get("lang");
  if (q === "he" || q === "en") writePref(q);   // a link can carry the choice to another origin (claude.ai, Vercel)
  let LANG = readPref();
  const ORIG = { lang: root.getAttribute("lang"), dir: root.getAttribute("dir"), title: null };
  let SOURCE = /^he/i.test(ORIG.lang || "") ? "he" : /^en/i.test(ORIG.lang || "") ? "en" : null;
  let PAGE = (window.LB_PAGE && window.LB_PAGE.file) || "", REV = "", COMMON_D = { en: {}, he: {} }, PAGE_D = { en: {}, he: {} };
  let paused = false, ready = false, pending = 0, DRY = false;   // DRY: harvest() only collects what is missing

  // the direction comes first, before the page is drawn, so nothing jumps; the words follow once the page has loaded
  const setRootDir = () => { if (!LANG) return; root.setAttribute("lang", LANG); root.setAttribute("dir", LANG === "he" ? "rtl" : "ltr"); };
  const restoreRootDir = () => {
    ORIG.lang == null ? root.removeAttribute("lang") : root.setAttribute("lang", ORIG.lang);
    ORIG.dir == null ? root.removeAttribute("dir") : root.setAttribute("dir", ORIG.dir);
  };
  if (LANG) {
    setRootDir();
    root.classList.add("lb-i18n-wait");
    const st = document.createElement("style");
    st.textContent = "html.lb-i18n-wait body{visibility:hidden}";
    document.head.append(st);
    setTimeout(() => root.classList.remove("lb-i18n-wait"), 1500);   // never keep a page hidden
  }

  // ---------- what needs translating ----------
  const codeLike = (s) => {
    const t = s.trim();
    return /^(https?:\/\/|www\.)/i.test(t) || /^\S+@\S+\.\S+$/.test(t) || /^[@#][\w.֐-׿-]+$/.test(t)
      || (!/\s/.test(t) && (/[\/\\_=<>{}|]/.test(t) || /\.[a-z0-9]{1,5}$/i.test(t) || /^[A-Z0-9&+.-]{1,6}$/.test(t)));
  };
  const needs = (s, to = LANG) => (to === "en" ? HE.test(s) : !HE.test(s) && /[A-Za-z]{2}/.test(s) && !codeLike(s));
  const keyOf = (srcs) => {
    const nums = []; let i = 0;
    const key = srcs.map((s) => s.replace(/\s+/g, " ").trim().replace(NUM, (m) => { nums.push(m); return "{" + i++ + "}"; })).join(SEP);
    return { key, nums };
  };
  const lookup = (key) => { const p = PAGE_D[LANG] || {}, c = COMMON_D[LANG] || {}; return key in p ? p[key] : key in c ? c[key] : undefined; };
  const fill = (v, nums) => String(v).replace(PH, (m, d) => (nums[+d] !== undefined ? nums[+d] : m));

  // ---------- what was changed, so it can be put back ----------
  const T = new WeakMap(), LIVE = new Set();          // text node -> { src, out }
  const A = new WeakMap(), LIVE_A = new Set();        // element -> { attr: { src, out } }
  const D = new WeakMap(), LIVE_D = new Set();        // element -> { lang, dir } before the flip
  const prune = () => { if (LIVE.size > 30000) for (const n of LIVE) if (!n.isConnected) LIVE.delete(n); };
  const srcOf = (n) => { const r = T.get(n); if (r && n.data === r.out) return r.src; if (r) T.delete(n); return n.data; };
  const put = (n, src, val, nums) => {
    if (DRY) return;
    const lead = /^\s*/.exec(src)[0], trail = /\s*$/.exec(src)[0];
    const out = lead + fill(val, nums) + trail;
    if (n.data !== out) n.data = out;
    T.set(n, { src, out }); LIVE.add(n);
  };

  const skipped = (el) => !el || SKIP_TAGS.has(el.localName) || el.isContentEditable || (el.matches && el.matches(SKIP));
  const inSkip = (el) => !el || el.isContentEditable || Boolean(el.closest && el.closest(SKIP_UP));
  const blockOf = (n) => { let e = n.parentElement; while (e && e !== document.body && INLINE.has(e.localName)) e = e.parentElement; return e; };

  // ---------- missing words: reported to the project server, picked up when translated ----------
  const MISS = new Map(), ASKED = new Set();
  let flushT = 0, polling = false;
  function miss(node, key) {
    if (!ON_SERVER || !PAGE) return;
    const id = LANG + SEP + key;
    if (ASKED.has(id) || MISS.has(id)) return;
    const el = node.nodeType === 1 ? node : node.parentElement;
    MISS.set(id, { k: key, to: LANG, scope: el && el.closest(COMMON) ? "common" : "page" });
    clearTimeout(flushT); flushT = setTimeout(flush, 700);
  }
  async function flush() {
    const by = { en: [], he: [] };
    for (const [id, it] of MISS) { by[it.to].push({ k: it.k, scope: it.scope }); ASKED.add(id); }
    MISS.clear();
    let sent = 0;
    for (const to of ["en", "he"]) {
      const items = by[to];
      for (let i = 0; i < items.length; i += 300) {
        try {
          const r = await fetch("/api/i18n/missing", { method: "POST", headers: { "Content-Type": "application/json", "X-LumeBook-Board": "1" },
            body: JSON.stringify({ page: PAGE, to, items: items.slice(i, i + 300) }) });
          if (r.ok) { const j = await r.json(); sent += j.new || 0; if (to === LANG) setPending(j.pending || 0); }
        } catch {}
      }
    }
    if (LANG) poll();
    return sent;
  }
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function poll() {
    if (polling || !ON_SERVER) return;
    polling = true;
    let quiet = 0;
    try {
      while (LANG && quiet < 120) {
        await sleep(pending > 0 ? 3000 : 6000);
        let j = null;
        try {
          const r = await fetch(`/api/i18n/dict?page=${encodeURIComponent(PAGE)}&lang=${LANG}&rev=${encodeURIComponent(REV)}`, { cache: "no-store" });
          if (r.ok) j = await r.json();
        } catch {}
        if (!j) { quiet += 10; continue; }
        setPending(j.pending || 0);
        if (j.rev && j.rev !== REV && j.common) {
          REV = j.rev; COMMON_D[LANG] = j.common; PAGE_D[LANG] = j.page || {};
          ASKED.clear();   // anything still missing is asked again once
          rescan();
          quiet = 0;
        } else quiet++;
        if (!j.pending) break;
      }
    } finally { polling = false; }
  }
  function setPending(n) {
    pending = n;
    for (const e of document.querySelectorAll(".lb-langfab-note")) {
      e.hidden = !n;
      e.dir = LANG === "en" ? "ltr" : "rtl";
      e.textContent = !n ? "" : LANG === "en" ? `Translating ${n}…` : `מתרגם ${n}…`;
    }
  }

  // ---------- translating a part of the page ----------
  function unit(nodes) {
    const srcs = nodes.map(srcOf);
    if (!srcs.some((s) => needs(s))) return;
    const { key, nums } = keyOf(srcs);
    const v = lookup(key);
    if (v !== undefined) {
      const vals = Array.isArray(v) ? v : [v];
      if (vals.length === nodes.length) { nodes.forEach((n, i) => put(n, srcs[i], vals[i], nums)); return; }
    }
    // not known as a whole: the pieces one by one (words many blocks share), and ask for the whole
    if (nodes.length > 1) nodes.forEach((n, i) => {
      if (!needs(srcs[i])) return;
      const one = keyOf([srcs[i]]), w = lookup(one.key);
      if (w !== undefined && !Array.isArray(w)) put(n, srcs[i], w, one.nums);
    });
    miss(nodes[0], key);   // the whole block reads better than its pieces: ask for it even when the pieces were known
  }
  function attrs(el, known) {
    if (!el.getAttribute || (!known && el.closest(SKIP))) return;
    const list = el.localName === "input" && /^(button|submit|reset)$/i.test(el.type) ? ATTRS.concat("value") : ATTRS;
    for (const a of list) {
      const cur = el.getAttribute(a);
      if (cur == null || !cur.trim()) continue;
      const m = A.get(el), r = m && m[a];
      const src = r && cur === r.out ? r.src : cur;
      if (!needs(src)) continue;
      const { key, nums } = keyOf([src]), v = lookup(key);
      if (v === undefined || Array.isArray(v)) { miss(el, key); continue; }
      if (DRY) continue;
      const out = fill(v, nums);
      const mm = m || {}; mm[a] = { src, out };
      if (!m) { A.set(el, mm); LIVE_A.add(el); }
      if (cur !== out) el.setAttribute(a, out);
    }
  }
  function flip(el, known) {
    if (el === root || FIELD.has(el.localName) || el.isContentEditable || (!known && el.closest(SKIP))) return;
    const lang = el.getAttribute("lang"), dir = el.getAttribute("dir");
    const want = LANG === "he" ? "rtl" : "ltr";
    const change = lang ? !lang.toLowerCase().startsWith(LANG) || (dir && dir !== want) : LANG === "en" && dir === "rtl";
    if (!change || DRY) return;
    if (!D.has(el)) { D.set(el, { lang, dir }); LIVE_D.add(el); }
    if (lang) el.setAttribute("lang", LANG);
    if (dir) el.setAttribute("dir", want);
  }
  // Hebrew that stays Hebrew (copy for parents, editable text) keeps right to left inside an English page
  function keepRtl(el) {
    if (DRY || LANG !== "en" || el.hasAttribute("dir") || FIELD.has(el.localName) || !HE.test(el.textContent || "")) return;
    if (!D.has(el)) { D.set(el, { lang: el.getAttribute("lang"), dir: null }); LIVE_D.add(el); }
    el.setAttribute("dir", "auto");
  }

  function scan(start) {
    if (!LANG || paused || !start) return;
    let top = start.nodeType === 1 ? start : start.parentElement;
    if (!top || !top.isConnected) return;
    while (top !== document.body && top.parentElement && INLINE.has(top.localName)) top = top.parentElement;
    if (top !== document.body && top.parentElement && inSkip(top.parentElement)) return;
    if (skipped(top) && top !== document.body) { if (top.matches(SKIP)) keepRtl(top); attrs(top); return; }
    const blocks = new Map();
    const w = document.createTreeWalker(top, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode(n) {
        if (n.nodeType === 3) return n.data.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
        if (skipped(n)) {
          if (n.matches && n.matches(SKIP)) keepRtl(n);
          if ((n.localName === "input" || n.localName === "textarea") && !n.matches(SKIP)) attrs(n, true);
          return NodeFilter.FILTER_REJECT;
        }
        if (n.hasAttribute("lang") || n.hasAttribute("dir")) flip(n, true);
        if (n.attributes.length) attrs(n, true);
        return NodeFilter.FILTER_SKIP;
      },
    });
    if (top.attributes) {   // the walker never shows its own root (a <body dir="rtl"> included)
      if (top.hasAttribute("lang") || top.hasAttribute("dir")) flip(top, top === document.body);
      if (top !== document.body) attrs(top);
    }
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      const b = blockOf(n) || top;
      const list = blocks.get(b);
      if (list) list.push(n); else blocks.set(b, [n]);
    }
    for (const nodes of blocks.values()) {
      const size = nodes.reduce((s, n) => s + srcOf(n).length, 0);
      if (nodes.length > 40 || size > 3500) nodes.forEach((n) => unit([n]));
      else unit(nodes);
    }
    prune();
  }
  function doTitle() {
    const t = document.querySelector("title");
    if (!t) return;
    const cur = t.textContent;
    if (ORIG.title === null || (ORIG.titleOut !== cur)) ORIG.title = cur;
    if (!needs(ORIG.title)) return;
    const { key, nums } = keyOf([ORIG.title]), v = lookup(key);
    if (v === undefined || Array.isArray(v)) return miss(document.body, key);
    if (DRY) return;
    ORIG.titleOut = fill(v, nums);
    if (cur !== ORIG.titleOut) t.textContent = ORIG.titleOut;
  }

  // the edit button's own runtime re-applies saved edits on every change; tell it this text is now the page's
  const resyncEdits = () => { try { if (window.LBEdits && window.LBEdits.resync) window.LBEdits.resync(); } catch {} };
  const mo = new MutationObserver((recs) => {
    if (!LANG || paused || !ready) return;
    const tops = new Set();
    for (const r of recs) {
      if (r.type === "characterData") tops.add(r.target.parentElement);
      else if (r.type === "attributes") tops.add(r.target);
      else for (const n of r.addedNodes) tops.add(n.nodeType === 1 ? n : n.parentElement);
    }
    const lifted = new Set();
    for (let t of tops) {
      if (!t || !t.isConnected) continue;
      while (t !== document.body && t.parentElement && INLINE.has(t.localName)) t = t.parentElement;
      lifted.add(t);
    }
    for (const t of lifted) {
      let up = t.parentElement, covered = false;
      while (up) { if (lifted.has(up)) { covered = true; break; } up = up.parentElement; }
      if (!covered) scan(t);
    }
    doTitle();
    mo.takeRecords();
    resyncEdits();
  });
  const watch = () => {
    mo.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS.concat(["lang", "dir"]) });
    const t = document.querySelector("title");
    if (t) mo.observe(t, { childList: true, characterData: true, subtree: true });
  };

  function applyAll() {
    if (!LANG || paused || !document.body) return;
    setRootDir();
    scan(document.body);
    doTitle();
    mo.takeRecords();
    resyncEdits();
  }
  function restoreAll() {
    mo.takeRecords();
    for (const n of LIVE) { const r = T.get(n); if (r && n.data === r.out) n.data = r.src; T.delete(n); }
    LIVE.clear();
    for (const el of LIVE_A) {
      const m = A.get(el);
      if (m) for (const [a, r] of Object.entries(m)) if (el.getAttribute(a) === r.out) el.setAttribute(a, r.src);
      A.delete(el);
    }
    LIVE_A.clear();
    for (const el of LIVE_D) {
      const r = D.get(el);
      if (r) {
        r.lang == null ? el.removeAttribute("lang") : el.setAttribute("lang", r.lang);
        r.dir == null ? el.removeAttribute("dir") : el.setAttribute("dir", r.dir);
      }
      D.delete(el);
    }
    LIVE_D.clear();
    const t = document.querySelector("title");
    if (t && ORIG.title !== null && t.textContent === ORIG.titleOut) t.textContent = ORIG.title;
    restoreRootDir();
    mo.takeRecords();
    resyncEdits();
  }
  const rescan = () => { if (LANG && !paused && ready) applyAll(); };
  const showPressed = () => {
    const cur = LANG || SOURCE || "he";
    for (const b of document.querySelectorAll("[data-glang]")) b.setAttribute("aria-pressed", String(b.dataset.glang === cur));
  };

  function load() {
    try {
      const tag = document.getElementById("lumebook-i18n");
      const data = tag ? JSON.parse(tag.textContent || "{}") : {};
      if (data.page) PAGE = data.page;
      ON_SERVER = Boolean(data.live) && /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
      REV = data.rev || "";
      for (const l of ["en", "he"]) {
        COMMON_D[l] = (data.common && data.common[l]) || {};
        PAGE_D[l] = (data.dict && data.dict[l]) || {};
      }
    } catch {}
    if (!SOURCE && document.body) {   // no lang on <html>: the letters decide
      const t = document.body.innerText || "";
      SOURCE = (t.match(/[֐-׿]/g) || []).length >= (t.match(/[A-Za-z]/g) || []).length / 2 ? "he" : "en";
    }
  }
  function start() {
    load();
    ready = true;
    showPressed();
    if (LANG) { applyAll(); watch(); }
    root.classList.remove("lb-i18n-wait");
    if (LANG && ON_SERVER) poll();
  }

  window.LBI18N = {
    lang: () => LANG || SOURCE || "he",
    chosen: () => LANG,
    source: () => SOURCE,
    set(l) {
      if (l !== "he" && l !== "en") return;
      writePref(l);
      if (l === LANG) return showPressed();
      if (LANG) restoreAll();
      LANG = l;
      ASKED.clear(); MISS.clear();
      showPressed();
      if (!ready) return;
      applyAll(); watch();
      setPending(0);
      if (ON_SERVER) poll();
      window.dispatchEvent(new CustomEvent("lb:lang", { detail: { lang: l } }));
    },
    // the edit button: the page's own words while it is open
    suspend() { if (paused) return; paused = true; root.classList.add("lb-i18n-paused"); mo.disconnect(); if (LANG) restoreAll(); },
    resume() { if (!paused) return; paused = false; root.classList.remove("lb-i18n-paused"); if (LANG && ready) { applyAll(); watch(); } },
    refresh: rescan,
    // collect what the dictionaries lack for both languages without changing the page, and report it (project server only):
    // how the dictionaries are filled for a whole page at once. Resolves to the number of new blocks the server queued.
    async harvest(root) {
      if (!ON_SERVER) return 0;
      const keep = LANG, wasPaused = paused;
      paused = false; DRY = true;
      try { for (const l of ["en", "he"]) { LANG = l; scan(root || document.body); doTitle(); } }
      finally { LANG = keep; DRY = false; paused = wasPaused; }
      clearTimeout(flushT);
      return flush();
    },
    showPressed,
    needs, keyOf,
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
