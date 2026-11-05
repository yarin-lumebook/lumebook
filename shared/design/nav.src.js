/* The LumeBook project nav (Yarin, 5 Nov 2026): one navigation on every internal page.
   - top bar (first layer): the logo home to HQ and HQ's topics; a topic opens its tools in the side bar
   - location path under it: HQ › topic › this page
   - side bar on the right (second layer): every HQ tool by topic; collapses to an icon rail, the menu button toggles it,
     the choice is kept in this browser
   - phones (760px and narrower): the side bar is a drawer over the page, a bottom nav bar holds HQ, the first three
     topics and "עוד"; both bars slide away while scrolling down and come back on the way up
   Source: shared/design/nav.src.js. design.py puts window.LB_NAV_DATA in front of it (hq-tools.json with the topic
   colours, the icons, the logo, the HQ and Vercel addresses, HQ's saved layout) and writes shared/design/nav.js.
   Builds inline it with design.head(); HQ and the SMM plan link a synced copy. Styles: "project nav" in lumebook.css.
   A page tells it where it is with window.LB_PAGE = { file: "<path in the project>" } (design.head() does this inside
   a lumebook.py build) or { hq: true } (HQ, which then calls LBNav.setCurrent on every view). Without it the address
   decides: the path on the project server, the address on Vercel. */
(() => {
  "use strict";
  if (window.LBNav) return;
  const D = window.LB_NAV_DATA || { topics: [], icons: {}, ui: {}, hq: {}, web_copies: {} };
  const PAGE = window.LB_PAGE || {};
  const host = location.hostname;
  const LOCALHOST = /^(localhost|127\.0\.0\.1)$/.test(host);
  const ON_SERVER = LOCALHOST && location.port === "8780";
  // where this page is open decides which version of a tool a link opens (as on HQ's cubes): the project server opens the
  // local page, the claude.ai artifact the artifact, the Vercel copy the copy or the artifact. claude.ai opens a link from
  // an artifact in a new tab and allows nothing else.
  const MODE = LOCALHOST || location.protocol === "file:" ? "local" : /\.vercel\.app$/.test(host) ? "web" : "artifact";
  const NEW_TAB = MODE === "artifact" ? ' target="_blank" rel="noopener noreferrer"' : "";
  const PHONE = window.matchMedia("(max-width: 760px)");
  const KEY = "lb-gside";

  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const svg = (inner) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${inner || ""}</svg>`;
  const ico = (name) => svg((D.icons || {})[name] || (D.icons || {}).grid);
  const ui = (name) => svg((D.ui || {})[name]);
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const localUrl = (p) => (ON_SERVER ? "/" : "http://localhost:8780/") + p.split("/").map(encodeURIComponent).join("/");
  const HQ_URL = PAGE.hq ? "" : MODE === "local" ? localUrl(D.hq.local) : MODE === "web" ? D.hq.web : D.hq.artifact;
  const hqTarget = PAGE.hq || MODE !== "artifact" ? "" : NEW_TAB;

  // ---------- the layout: hq-tools.json, then Yarin's own arrangement from HQ edit mode ----------
  const toolId = (t) => t.id || (t.view ? "v:" + t.view + (t.tab ? ":" + t.tab : "") : t.local ? "l:" + t.local : t.art ? "a:" + t.art : "w:" + (t.web || t.t));
  function defaultLayout() {
    return { v: 1, removed: [], topics: (D.topics || []).map((tp) => ({ id: tp.id, label: tp.label, desc: tp.desc || "", icon: tp.icon || "grid",
      cat: Number(tp.cat) || 0, tools: (tp.tools || []).map((t) => ({ ...clone(t), id: toolId(t) })) })) };
  }
  // a saved layout wins; a tool added to hq-tools.json later still shows up (in its topic) unless Yarin deleted it (removed)
  function mergeLayout(saved) {
    const def = defaultLayout();
    if (!saved || saved.default || !Array.isArray(saved.topics)) return def;   // default: true = reset, follow hq-tools.json
    const L = { v: 1, removed: Array.isArray(saved.removed) ? saved.removed.slice() : [],
      topics: clone(saved.topics).filter((t) => t && t.id).map((t) => ({ ...t, cat: Number(t.cat) || 0, tools: (t.tools || []).filter((x) => x && x.id) })) };
    const have = new Set(L.topics.flatMap((t) => t.tools.map((x) => x.id))), gone = new Set(L.removed);
    for (const dt of def.topics) for (const tool of dt.tools) {
      if (have.has(tool.id) || gone.has(tool.id)) continue;
      let home = L.topics.find((t) => t.id === dt.id);
      if (!home) { home = { ...dt, tools: [] }; L.topics.push(home); }
      home.tools.push(tool); have.add(tool.id);
    }
    return L;
  }

  // the version a tool opens here (main) and, when there is one, the other version (alt): HQ's cubes use the same rule
  function toolLinks(t) {
    if (t.view) return { main: { href: HQ_URL + "#" + t.view, where: "ב-HQ", kind: "view" }, alt: null };
    const copy = MODE === "web" && (D.web_copies || {})[t.art];
    const v = { local: t.local && { href: localUrl(t.local), where: "מקומי", kind: "local" },
                art: t.art && { href: "https://claude.ai/artifact/" + t.art, where: "ארטיפקט", kind: "art" },
                web: t.web && { href: t.web, where: t.webLabel || "אתר", kind: "web" },
                copy: copy && { href: copy, where: "Vercel", kind: "web" } };
    const main = (MODE === "local" ? [v.local, v.art, v.web] : [v.copy, v.art, v.web, v.local]).find(Boolean);
    if (!main) return { main: { href: HQ_URL + "#tools", where: "אין קישור עדיין", kind: "view" }, alt: null };
    if (MODE !== "local" && main.kind === "local") main.where = "מקומי בלבד";
    const alt = MODE === "local" ? (main.kind !== "art" ? v.art : null) : (main.kind !== "local" ? v.local : null);
    return { main, alt: alt ? { ...alt, label: alt.kind === "art" ? "גרסת ארטיפקט" : "גרסה מקומית" } : null };
  }

  // ---------- where this page is ----------
  const norm = (p) => String(p || "").replace(/^\/+/, "").replace(/(^|\/)index\.html?$/i, "$1");
  const sameUrl = (a, b) => { try { const x = new URL(a), y = new URL(b, a); return x.host === y.host && norm(x.pathname) === norm(y.pathname); } catch { return false; } };
  function findCurrent(L) {
    if (PAGE.hq) return S.view ? L.topics.flatMap((tp) => tp.tools.map((t) => [t, tp])).find(([t]) => t.view === S.view && !t.tab) || null : null;
    const here = norm(decodeURIComponent(location.pathname)), art = PAGE.file && (D.pages || {})[PAGE.file];
    for (const tp of L.topics) for (const t of tp.tools) {
      if (t.view) continue;
      if (PAGE.file && t.local && norm(PAGE.file) === norm(t.local)) return [t, tp];
      if (art && t.art === art) return [t, tp];
      if (ON_SERVER && t.local && (here === norm(t.local) || (t.local.endsWith("/") && here.startsWith(t.local)))) return [t, tp];
      if (LOCALHOST && location.port === "8777" && t.local === "hook-studio/") return [t, tp];
      if (MODE === "web" && ((t.web && sameUrl(location.href, t.web)) || (t.art && (D.web_copies || {})[t.art] && sameUrl(location.href, D.web_copies[t.art])))) return [t, tp];
    }
    return null;
  }

  // ---------- state ----------
  const S = { L: mergeLayout(D.saved), view: null, viewTitle: "", focus: "", away: false, lastY: 0, opener: null };
  const readPref = () => { try { return localStorage.getItem(KEY) === "expanded"; } catch { return false; } };
  const writePref = (on) => { try { localStorage.setItem(KEY, on ? "expanded" : "collapsed"); } catch {} };
  let expanded = readPref();   // the side bar starts as a collapsed icon rail
  const root = document.documentElement;
  const el = {};

  // ---------- markup ----------
  function topBar(cur) {
    const curTopic = cur ? cur[1].id : "";
    return `<button type="button" class="lb-gnav-toggle" data-gnav="toggle" aria-controls="lb-gside" aria-expanded="false" aria-label="כל הכלים">${ui("menu")}</button>
      <a class="lb-gnav-brand" href="${esc(HQ_URL || "#tools")}"${hqTarget} aria-label="HQ, כל הכלים"><img src="${esc(D.logo || "")}" alt="" width="28" height="28"><b>LumeBook</b></a>
      <nav class="lb-gnav-topics" aria-label="נושאים">${S.L.topics.filter((tp) => tp.tools.length).map((tp) =>
        `<button type="button" class="lb-gnav-topic lb-cat-${tp.cat}" data-gtopic="${esc(tp.id)}" aria-controls="lb-gside"${tp.id === curTopic ? ' aria-current="true"' : ""}>${ico(tp.icon)}<span>${esc(tp.label)}</span></button>`).join("")}</nav>`;
  }
  function path(cur) {
    const items = [];
    const atHome = PAGE.hq && (!S.view || S.view === "tools");
    items.push(atHome ? `<b aria-current="page">HQ</b>` : `<a href="${esc(HQ_URL || "#tools")}"${hqTarget}>HQ</a>`);
    if (cur) items.push(`<button type="button" data-gtopic="${esc(cur[1].id)}" aria-controls="lb-gside">${esc(cur[1].label)}</button>`);
    if (!atHome) {
      const name = PAGE.hq ? S.viewTitle || (cur && cur[0].t) : cur ? cur[0].t : pageTitle();
      if (name) items.push(`<b aria-current="page"${cur && cur[0].en ? ' lang="en" dir="ltr"' : ""}>${esc(name)}</b>`);
    }
    return `<nav class="lb-crumbs" aria-label="מיקום בפרויקט">${items.join("")}</nav><div class="lb-gpath-slot"></div>`;
  }
  // a page that is not one of HQ's tools shows its own title, without the "LumeBook ·" part many titles start with
  const pageTitle = () => (document.title || "").replace(/^\s*(LumeBook|לומבוק)\s*[·|:\-]\s*/i, "").trim();
  function side(cur) {
    const curId = cur ? cur[0].id : "";
    return `<div class="lb-gside-head"><b>כל הכלים</b><button type="button" class="lb-gside-close" data-gnav="close" aria-label="סגירה">${ui("close")}</button></div>
      <nav class="lb-gside-scroll" aria-label="כל הכלים">${S.L.topics.filter((tp) => tp.tools.length).map((tp) =>
        `<section class="lb-gside-topic lb-cat-${tp.cat}${tp.id === S.focus ? " is-focus" : ""}" data-gtopic-sec="${esc(tp.id)}" aria-labelledby="lb-gside-${esc(tp.id)}">
          <h2 class="lb-gside-h" id="lb-gside-${esc(tp.id)}">${esc(tp.label)}</h2>
          <ul>${tp.tools.map((t) => {
            const { main } = toolLinks(t), nt = main.kind === "view" ? "" : NEW_TAB;
            const tab = PAGE.hq && t.tab ? ` data-open-tab="${esc(t.tab)}"` : "";
            return `<li><a class="lb-gside-item" href="${esc(main.href)}"${nt}${tab} title="${esc(t.t + (t.sub ? ": " + t.sub : ""))}"${t.id === curId ? ' aria-current="page"' : ""}>`
              + `<span class="lb-tile" aria-hidden="true">${ico(t.icon)}</span><span class="lb-gside-name"${t.en ? ' lang="en" dir="ltr"' : ""}>${esc(t.t)}</span></a></li>`;
          }).join("")}</ul>
        </section>`).join("")}</nav>`;
  }
  function bottom(cur) {
    const first = S.L.topics.filter((tp) => tp.tools.length).slice(0, 3);
    const curTopic = cur ? cur[1].id : "", home = PAGE.hq && (!S.view || S.view === "tools");
    const inMore = curTopic && !first.some((tp) => tp.id === curTopic);
    return `<a class="lb-gbottom-item" href="${esc(HQ_URL || "#tools")}"${hqTarget}${home ? ' aria-current="page"' : ""}>${ico("grid")}<span>HQ</span></a>`
      + first.map((tp) => `<button type="button" class="lb-gbottom-item lb-cat-${tp.cat}" data-gtopic="${esc(tp.id)}" aria-controls="lb-gside"${tp.id === curTopic ? ' aria-current="true"' : ""}>${ico(tp.icon)}<span>${esc(tp.label)}</span></button>`).join("")
      + `<button type="button" class="lb-gbottom-item" data-gnav="more" aria-controls="lb-gside" aria-expanded="false"${inMore ? ' aria-current="true"' : ""}>${ui("menu")}<span>עוד</span></button>`;
  }

  // ---------- drawing ----------
  function mount() {
    if (el.bar || !document.body) return;
    const make = (tag, cls, attrs) => { const n = document.createElement(tag); n.className = cls; n.dir = "rtl"; n.lang = "he"; for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, v); return n; };
    el.bar = make("header", "lb-gnav");
    el.path = make("div", "lb-gpath");
    el.side = make("aside", "lb-gside", { id: "lb-gside", "aria-label": "כל הכלים" });
    el.scrim = make("div", "lb-gscrim", { "data-gnav": "close" });
    el.bottom = make("nav", "lb-gbottom", { "aria-label": "ניווט ראשי" });
    document.body.prepend(el.bar, el.path);
    document.body.append(el.side, el.scrim, el.bottom);
    root.classList.add("lb-has-gnav");
    draw();
    // anything the page marks for the path row (HQ: its data freshness) moves to its end
    document.querySelectorAll("[data-lb-gpath-slot]").forEach((n) => el.path.querySelector(".lb-gpath-slot").append(n));
    el.bar.addEventListener("click", onClick); el.path.addEventListener("click", onClick); el.side.addEventListener("click", onClick);
    el.scrim.addEventListener("click", onClick); el.bottom.addEventListener("click", onClick);
    document.addEventListener("keydown", onKey);
    PHONE.addEventListener("change", () => { closeDrawer(false); setAway(false); applyState(); });
    // the path row's height, for pages that fill the window (--lb-gnav-space in lumebook.css)
    const measure = () => root.style.setProperty("--lb-gpath-h", el.path.offsetHeight + "px");
    measure(); if (window.ResizeObserver) new ResizeObserver(measure).observe(el.path);
    window.addEventListener("scroll", onScroll, { passive: true });
    if (MODE === "local" && ON_SERVER && !PAGE.hq) loadSaved();
  }
  function draw() {
    if (!el.bar) return;
    const cur = findCurrent(S.L);
    el.bar.innerHTML = topBar(cur);
    const slot = el.path.querySelector(".lb-gpath-slot"), kept = slot ? [...slot.childNodes] : [];
    el.path.innerHTML = path(cur);
    el.path.querySelector(".lb-gpath-slot").append(...kept);
    const scroll = el.side.querySelector(".lb-gside-scroll"), top = scroll ? scroll.scrollTop : 0;
    el.side.innerHTML = side(cur);
    el.side.querySelector(".lb-gside-scroll").scrollTop = top;
    el.bottom.innerHTML = bottom(cur);
    applyState();
  }
  function applyState() {
    const phone = PHONE.matches, open = root.classList.contains("lb-gdrawer-open");
    root.dataset.gside = expanded ? "expanded" : "collapsed";
    const tog = el.bar && el.bar.querySelector('[data-gnav="toggle"]');
    if (tog) { tog.setAttribute("aria-expanded", String(phone ? open : expanded)); tog.setAttribute("aria-label", phone ? "כל הכלים" : expanded ? "כיווץ סרגל הכלים" : "הרחבת סרגל הכלים"); }
    const more = el.bottom && el.bottom.querySelector('[data-gnav="more"]');
    if (more) more.setAttribute("aria-expanded", String(open));
    if (el.side) {
      if (phone && open) { el.side.setAttribute("role", "dialog"); el.side.setAttribute("aria-modal", "true"); }
      else { el.side.removeAttribute("role"); el.side.removeAttribute("aria-modal"); }
    }
  }

  // ---------- the side bar ----------
  function setExpanded(on) { expanded = on; writePref(on); applyState(); }
  function openDrawer() {
    S.opener = document.activeElement;
    root.classList.add("lb-gdrawer-open"); setAway(false); applyState();
    const close = el.side.querySelector('[data-gnav="close"]'); if (close) close.focus({ preventScroll: true });
  }
  function closeDrawer(refocus = true) {
    if (!root.classList.contains("lb-gdrawer-open")) return;
    root.classList.remove("lb-gdrawer-open"); applyState();
    if (refocus && S.opener && S.opener.focus) S.opener.focus({ preventScroll: true });
  }
  // a topic in the top bar, the path or the bottom bar opens its tools in the side bar (the second layer)
  function showTopic(id) {
    S.focus = id;
    el.side.querySelectorAll("[data-gtopic-sec]").forEach((s) => s.classList.toggle("is-focus", s.dataset.gtopicSec === id));
    if (PHONE.matches) openDrawer(); else if (!expanded) setExpanded(true);
    const sec = el.side.querySelector(`[data-gtopic-sec="${CSS.escape(id)}"]`), scroll = el.side.querySelector(".lb-gside-scroll");
    if (sec && scroll) scroll.scrollTo({ top: sec.offsetTop - scroll.offsetTop - 8, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }
  function onClick(e) {
    const t = e.target.closest("[data-gtopic], [data-gnav], a");
    if (!t) return;
    if (t.dataset.gtopic) return showTopic(t.dataset.gtopic);
    const act = t.dataset.gnav;
    if (act === "toggle") return PHONE.matches ? openDrawer() : setExpanded(!expanded);
    if (act === "more") { S.focus = ""; el.side.querySelectorAll(".is-focus").forEach((s) => s.classList.remove("is-focus")); return openDrawer(); }
    if (act === "close") return closeDrawer();
    if (t.tagName === "A" && root.classList.contains("lb-gdrawer-open")) closeDrawer(false);   // a link inside HQ (#view) keeps the page
  }
  function onKey(e) {
    if (!root.classList.contains("lb-gdrawer-open")) return;
    if (e.key === "Escape") { e.preventDefault(); return closeDrawer(); }
    if (e.key !== "Tab") return;   // keep the focus inside the open drawer
    const f = [...el.side.querySelectorAll("a[href], button")].filter((n) => n.offsetParent !== null);
    if (!f.length) return;
    const first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  // ---------- phones: the top and bottom bars slide away while scrolling down ----------
  function setAway(on) { if (S.away === on) return; S.away = on; root.classList.toggle("lb-gnav-away", on); }
  let ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      const y = Math.max(0, window.scrollY);
      if (!PHONE.matches || root.classList.contains("lb-gdrawer-open")) { S.lastY = y; return setAway(false); }
      if (y < 56) setAway(false);
      else if (y > S.lastY + 6) setAway(true);
      else if (y < S.lastY - 6) setAway(false);
      if (Math.abs(y - S.lastY) > 6) S.lastY = y;
    });
  }

  // on the project server the side bar follows HQ's saved arrangement as it is now
  async function loadSaved() {
    try {
      const r = await fetch("/api/hq/layout", { cache: "no-store" });
      if (r.ok) { const j = await r.json(); if (j && (Array.isArray(j.topics) || j.default)) { S.L = mergeLayout(j); draw(); } }
    } catch {}
  }

  // ---------- for HQ ----------
  window.LBNav = {
    MODE, toolId, toolLinks, defaultLayout, mergeLayout,
    // HQ's own layout as it loads and as Yarin edits it
    setLayout(L) { S.L = clone(L); draw(); },
    // HQ's view: { view: "overview", title: "סקירה" }
    setCurrent({ view, title } = {}) { S.view = view || null; S.viewTitle = title || ""; draw(); },
  };

  if (document.body) mount(); else document.addEventListener("DOMContentLoaded", mount);
})();
