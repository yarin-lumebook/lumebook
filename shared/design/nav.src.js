/* The LumeBook project nav (Yarin, 5 Nov 2026): one navigation on every internal page.
   Since 6 Nov 2026 there is no top bar and no location path (Yarin: "remove the top navbar"): the side bar runs the full
   height of the window and holds everything. Since 8 Nov 2026 it is the only list of tools (Yarin: "move everything to the
   side bar"): HQ's front page is the live numbers (#home), first in the side bar as "בית".
   - side bar on the right: the logo home to HQ and the menu button at its top, then every HQ tool by topic. The current page
     is marked in the list.
   - topics fold (Yarin, 15 Nov 2026: "i want main topics ... to expand when clicking"): each topic is a row with its icon;
     a click opens or closes its pages under it (several can be open). The topic of the page you are on starts open; the
     topics you open stay open in this browser (localStorage lb-gside-open).
   - always a closed icon rail except while hovered (Yarin, 15 Nov 2026: "always closed expect when hovering ... so it wont
     close unexpectedly"): with a mouse or trackpad the rail opens over the page, never pushing it, once the pointer rests
     on it (hover intent: it settles for one 70ms beat, or 300ms at most; a fast pass does nothing; a press opens it at
     once) and closes 420ms after the pointer leaves (back in time, nothing happens). It stays open while the pointer is
     within 28px of its edge, while a press that began in it is held, while keyboard focus is in it, and when the pointer
     leaves the window across the screen edge (it closes once the pointer comes back over the page). After a click on a
     link, Esc or a page load under the pointer it waits for the pointer to leave before it opens again. Keyboard: Tab
     into it opens it. Touch screens wider than a phone: the menu button opens it, a tap outside closes it.
   - phones (760px and narrower): the side bar is a drawer over the page, a bottom nav bar holds HQ, the first three
     topics and "עוד"; it slides away while scrolling down and comes back on the way up
   Source: shared/design/nav.src.js. design.py puts window.LB_NAV_DATA in front of it (hq-tools.json with the topic
   colours, the icons, the logo, the HQ and Vercel addresses, HQ's saved layout) and writes shared/design/nav.js.
   Builds inline it with design.head(); HQ links a synced copy. Styles: "project nav" in lumebook.css.
   Since 8 Nov 2026 its foot holds the language switch (עב | EN): window.LBI18N (i18n.src.js, in front of this
   script in nav.js) swaps the words of the page, this side bar's included; the switch itself is never translated.
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
  const FINE = window.matchMedia("(hover: hover) and (pointer: fine)");
  const OPEN_KEY = "lb-gside-open";

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
    if (!main) return { main: { href: HQ_URL + "#home", where: "אין קישור עדיין", kind: "view" }, alt: null };
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
  const S = { L: mergeLayout(D.saved), view: null, viewTitle: "", focus: "", away: false, lastY: 0, opener: null,
    open: readOpen(), auto: null, autoFor: undefined };
  // the topics Yarin opened (kept in this browser); the topic of the current page is open too (auto) until he closes it
  function readOpen() { try { const a = JSON.parse(localStorage.getItem(OPEN_KEY) || "[]"); return new Set(Array.isArray(a) ? a.map(String) : []); } catch { return new Set(); } }
  const writeOpen = () => { try { localStorage.setItem(OPEN_KEY, JSON.stringify([...S.open])); } catch {} };
  const topicOpen = (id) => S.open.has(id) || S.auto === id;
  const root = document.documentElement;
  const el = {};

  // ---------- markup ----------
  // the language switch (8 Nov 2026): both languages always readable, the current one pressed. It floats at the bottom left,
  // right of the edit button (Yarin, 8 Nov 2026: "make the language button float next to the edit site button to the right")
  function langSwitch() {
    const cur = window.LBI18N ? window.LBI18N.lang() : "he";
    return [["he", "עב", "עברית"], ["en", "EN", "English"]].map(([v, t, full]) =>
        `<button type="button" data-glang="${v}" lang="${v}" aria-pressed="${cur === v}" title="${full}">${t}</button>`).join("")
      + `<span class="lb-langfab-note" hidden></span>`;
  }
  function side(cur) {
    const curId = cur ? cur[0].id : "", curTopic = cur ? cur[1].id : "";
    return `<div class="lb-gside-head">
        <a class="lb-gside-brand" href="${esc(HQ_URL + "#home")}"${hqTarget} aria-label="HQ, הבית"><img src="${esc(D.logo || "")}" alt="" width="28" height="28"><b translate="no">LumeBook</b></a>
        <button type="button" class="lb-gside-toggle" data-gnav="toggle" aria-controls="lb-gside" aria-expanded="false" aria-label="כל הכלים">${ui("menu")}</button>
        <button type="button" class="lb-gside-close" data-gnav="close" aria-label="סגירה">${ui("close")}</button></div>
      <nav class="lb-gside-scroll" aria-label="כל הכלים"><ul class="lb-gside-home lb-cat-0"><li><a class="lb-gside-item" href="${esc(HQ_URL + "#home")}"${hqTarget} title="בית: המספרים של היום ומה דורש טיפול"${PAGE.hq && S.view === "home" ? ' aria-current="page"' : ""}><span class="lb-tile" aria-hidden="true">${ico("home")}</span><span class="lb-gside-name">בית</span></a></li></ul>${S.L.topics.filter((tp) => tp.tools.length).map((tp) => {
        const open = topicOpen(tp.id), hid = "lb-gside-" + tp.id;
        return `<section class="lb-gside-topic lb-cat-${tp.cat}${open ? " is-open" : ""}${tp.id === curTopic ? " has-current" : ""}${tp.id === S.focus ? " is-focus" : ""}" data-gtopic-sec="${esc(tp.id)}" aria-labelledby="${esc(hid)}">
          <h2 class="lb-gside-h"><button type="button" class="lb-gside-tbtn" id="${esc(hid)}" data-gfold="${esc(tp.id)}" aria-expanded="${open}" aria-controls="${esc(hid)}-tools" title="${esc(tp.label + (tp.desc ? ": " + tp.desc : ""))}"><span class="lb-tile" aria-hidden="true">${ico(tp.icon)}</span><span class="lb-gside-name">${esc(tp.label)}</span><span class="lb-gside-chev" aria-hidden="true">${ui("chevron-down")}</span></button></h2>
          <div class="lb-gside-tools" id="${esc(hid)}-tools"${open ? "" : " inert"}><div class="lb-gside-clip"><ul>${tp.tools.map((t) => {
            const { main } = toolLinks(t), nt = main.kind === "view" ? "" : NEW_TAB;
            const tab = PAGE.hq && t.tab ? ` data-open-tab="${esc(t.tab)}"` : "";
            return `<li><a class="lb-gside-item" href="${esc(main.href)}"${nt}${tab} title="${esc(t.t + (t.sub ? ": " + t.sub : ""))}"${t.id === curId ? ' aria-current="page"' : ""}>`
              + `<span class="lb-tile" aria-hidden="true">${ico(t.icon)}</span><span class="lb-gside-name"${t.en ? ' lang="en" dir="ltr"' : ""}>${esc(t.t)}</span></a></li>`;
          }).join("")}</ul></div></div>
        </section>`;
      }).join("")}</nav>`;
  }
  function bottom(cur) {
    const first = S.L.topics.filter((tp) => tp.tools.length).slice(0, 3);
    const curTopic = cur ? cur[1].id : "", home = PAGE.hq && (!S.view || S.view === "home");
    const inMore = curTopic && !first.some((tp) => tp.id === curTopic);
    return `<a class="lb-gbottom-item" href="${esc(HQ_URL + "#home")}"${hqTarget}${home ? ' aria-current="page"' : ""}>${ico("home")}<span>בית</span></a>`
      + first.map((tp) => `<button type="button" class="lb-gbottom-item lb-cat-${tp.cat}" data-gtopic="${esc(tp.id)}" aria-controls="lb-gside"${tp.id === curTopic ? ' aria-current="true"' : ""}>${ico(tp.icon)}<span>${esc(tp.label)}</span></button>`).join("")
      + `<button type="button" class="lb-gbottom-item" data-gnav="more" aria-controls="lb-gside" aria-expanded="false"${inMore ? ' aria-current="true"' : ""}>${ui("menu")}<span>עוד</span></button>`;
  }

  // ---------- drawing ----------
  function mount() {
    if (el.side || !document.body) return;
    const make = (tag, cls, attrs) => { const n = document.createElement(tag); n.className = cls; n.dir = "rtl"; n.lang = "he"; for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, v); return n; };
    el.side = make("aside", "lb-gside", { id: "lb-gside", "aria-label": "כל הכלים" });
    el.scrim = make("div", "lb-gscrim", { "data-gnav": "close" });
    el.bottom = make("nav", "lb-gbottom", { "aria-label": "ניווט ראשי" });
    el.lang = make("div", "lb-langfab lb-glass is-capsule is-thick", { role: "group", "aria-label": "שפה · Language", translate: "no" });
    el.lang.dir = "ltr";
    el.lang.innerHTML = langSwitch();
    document.body.append(el.side, el.scrim, el.bottom, el.lang);
    root.classList.add("lb-has-gnav");
    draw();
    el.side.addEventListener("click", onClick); el.scrim.addEventListener("click", onClick); el.bottom.addEventListener("click", onClick); el.lang.addEventListener("click", onClick);
    document.addEventListener("keydown", onKey);
    PHONE.addEventListener("change", () => { closeDrawer(false); setAway(false); closeRail(); applyState(); });
    window.addEventListener("scroll", onScroll, { passive: true });
    hoverRail();
    if (MODE === "local" && ON_SERVER && !PAGE.hq) loadSaved();
  }
  function draw() {
    if (!el.side) return;
    const cur = findCurrent(S.L), curId = cur ? cur[0].id : "";
    if (curId !== S.autoFor) { S.autoFor = curId; S.auto = cur ? cur[1].id : null; }   // a new current page opens its topic
    const scroll = el.side.querySelector(".lb-gside-scroll"), top = scroll ? scroll.scrollTop : 0;
    el.side.innerHTML = side(cur);
    el.side.querySelector(".lb-gside-scroll").scrollTop = top;
    el.bottom.innerHTML = bottom(cur);
    applyState();
  }
  function applyState() {
    const phone = PHONE.matches, open = root.classList.contains("lb-gdrawer-open");
    root.dataset.gside = !phone && H.open ? "expanded" : "collapsed";
    const tog = el.side && el.side.querySelector('[data-gnav="toggle"]');
    if (tog) { tog.setAttribute("aria-expanded", String(phone ? open : H.open)); tog.setAttribute("aria-label", phone ? "כל הכלים" : H.open ? "סגירת סרגל הכלים" : "פתיחת סרגל הכלים"); }
    const more = el.bottom && el.bottom.querySelector('[data-gnav="more"]');
    if (more) more.setAttribute("aria-expanded", String(open));
    if (el.side) {
      if (phone && open) { el.side.setAttribute("role", "dialog"); el.side.setAttribute("aria-modal", "true"); }
      else { el.side.removeAttribute("role"); el.side.removeAttribute("aria-modal"); }
    }
  }

  // ---------- topics fold open and closed (15 Nov 2026) ----------
  // only the classes change, so the fold animates and the list keeps its place
  function setTopic(id, on) {
    if (on) S.open.add(id); else { S.open.delete(id); if (S.auto === id) S.auto = null; }
    writeOpen();
    const sec = el.side && el.side.querySelector(`[data-gtopic-sec="${CSS.escape(id)}"]`);
    if (!sec) return;
    sec.classList.toggle("is-open", on);
    const b = sec.querySelector("[data-gfold]"); if (b) b.setAttribute("aria-expanded", String(on));
    const w = sec.querySelector(".lb-gside-tools"); if (w) w.toggleAttribute("inert", !on);
  }

  // ---------- the rail opens over the page while hovered (15 Nov 2026) ----------
  // H.open: open over the page; H.inside: the pointer is on it; H.armed: the pointer has been outside it since the page
  // loaded or since the last link click / Esc, so a hover may open it; H.held: a press that began in it is still down.
  const H = { open: false, inside: false, armed: false, held: false, x: 0, y: 0, px: 0, py: 0, t0: 0, poll: 0, close: 0 };
  const HT = { POLL: 70, SENS: 6, OPEN_MAX: 300, CLOSE: 420, EDGE: 28, WINDOW_EDGE: 24 };
  const railMode = () => !PHONE.matches;
  const keyboardInside = () => !!(el.side && el.side.querySelector(":focus-visible"));
  function openRail() {
    stopIntent(); cancelClose();
    if (H.open || !railMode()) return;
    H.open = true; applyState();
  }
  function closeRail() {
    stopIntent(); cancelClose();
    if (!H.open) return;
    H.open = false; applyState();
  }
  function stopIntent() { if (H.poll) { clearInterval(H.poll); H.poll = 0; } }
  function cancelClose() { if (H.close) { clearTimeout(H.close); H.close = 0; } }
  function scheduleClose() {
    if (!H.open || H.close) return;
    H.close = setTimeout(() => {
      H.close = 0;
      if (H.inside || H.held || keyboardInside()) return;
      closeRail();
    }, HT.CLOSE);
  }
  // hover intent: open once the pointer settles (moves less than SENS px in one POLL beat), or after OPEN_MAX in any case
  function startIntent() {
    if (H.open || H.poll || !H.armed || !railMode()) return;
    H.px = H.x; H.py = H.y; H.t0 = performance.now();
    H.poll = setInterval(() => {
      if (!H.inside) return stopIntent();
      if (Math.hypot(H.x - H.px, H.y - H.py) < HT.SENS || performance.now() - H.t0 >= HT.OPEN_MAX) return openRail();
      H.px = H.x; H.py = H.y;
    }, HT.POLL);
  }
  // the glass panel's left edge (the element includes the air around it)
  const railEdge = () => { const r = el.side.getBoundingClientRect(); return r.left + parseFloat(getComputedStyle(el.side).paddingLeft || 0); };
  function hoverRail() {
    const mouse = (e) => e.pointerType === "mouse" || e.pointerType === "pen";
    el.side.addEventListener("pointerenter", (e) => {
      if (!mouse(e)) return;
      H.inside = true; H.x = e.clientX; H.y = e.clientY;
      cancelClose(); startIntent();
    });
    el.side.addEventListener("pointermove", (e) => {
      if (!mouse(e)) return;
      H.inside = true; H.x = e.clientX; H.y = e.clientY;
      if (!H.open) startIntent();
    });
    el.side.addEventListener("pointerleave", (e) => {
      if (!mouse(e)) return;
      H.inside = false; H.armed = true; stopIntent();
      // left the window across the screen edge (to the Dock, the menu bar, another screen): stay open until the pointer is back
      const offWindow = !e.relatedTarget && (e.clientX <= HT.WINDOW_EDGE || e.clientY <= HT.WINDOW_EDGE
        || e.clientX >= innerWidth - HT.WINDOW_EDGE || e.clientY >= innerHeight - HT.WINDOW_EDGE);
      if (!offWindow) scheduleClose();
    });
    // a press opens it at once (no waiting for the hover); a press held from inside keeps it open until released
    el.side.addEventListener("pointerdown", (e) => {
      if (!railMode()) return;
      H.held = true;
      if (!H.open && !e.target.closest('[data-gnav="toggle"], [data-gnav="close"]')) openRail();
    });
    document.addEventListener("pointerup", () => { if (!H.held) return; H.held = false; if (H.open && !H.inside && FINE.matches) scheduleClose(); }, true);
    // outside it: arm the hover; while open, the 28px next to its edge still count as on it, further out it starts to close
    document.addEventListener("pointermove", (e) => {
      if (!mouse(e) || !el.side || el.side.contains(e.target)) return;
      H.inside = false; H.armed = true;
      if (!H.open || H.held) return;
      if (e.clientX >= railEdge() - HT.EDGE) cancelClose(); else scheduleClose();
    }, { passive: true });
    // touch screens wider than a phone: a tap outside closes it
    document.addEventListener("pointerdown", (e) => { if (H.open && el.side && !el.side.contains(e.target)) closeRail(); }, true);
    // keyboard: focus in opens it, focus leaving closes it (a mouse click inside never keeps it open)
    el.side.addEventListener("focusin", () => { if (railMode() && keyboardInside()) openRail(); });
    el.side.addEventListener("focusout", (e) => {
      if (e.relatedTarget && el.side.contains(e.relatedTarget)) return;
      if (H.open && !H.inside && !H.held) closeRail();
    });
  }

  // ---------- the side bar ----------
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
  // a topic in the bottom bar (phones) opens its tools in the side bar drawer
  function showTopic(id) {
    S.focus = id;
    el.side.querySelectorAll("[data-gtopic-sec]").forEach((s) => s.classList.toggle("is-focus", s.dataset.gtopicSec === id));
    setTopic(id, true);
    if (PHONE.matches) openDrawer(); else openRail();
    const sec = el.side.querySelector(`[data-gtopic-sec="${CSS.escape(id)}"]`), scroll = el.side.querySelector(".lb-gside-scroll");
    if (sec && scroll) scroll.scrollTo({ top: sec.offsetTop - scroll.offsetTop - 8, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }
  function onClick(e) {
    const t = e.target.closest("[data-gtopic], [data-gfold], [data-gnav], [data-glang], a");
    if (!t) return;
    if (t.dataset.glang) { if (window.LBI18N) window.LBI18N.set(t.dataset.glang); return; }
    if (t.dataset.gtopic) return showTopic(t.dataset.gtopic);
    if (t.dataset.gfold) { openRail(); return setTopic(t.dataset.gfold, !topicOpen(t.dataset.gfold)); }
    const act = t.dataset.gnav;
    if (act === "toggle") { if (PHONE.matches) return openDrawer(); if (H.open) { H.armed = false; return closeRail(); } return openRail(); }
    if (act === "more") { S.focus = ""; el.side.querySelectorAll(".is-focus").forEach((s) => s.classList.remove("is-focus")); return openDrawer(); }
    if (act === "close") return closeDrawer();
    if (t.tagName === "A") {
      if (root.classList.contains("lb-gdrawer-open")) closeDrawer(false);   // a link inside HQ (#view) keeps the page
      if (H.open) { H.armed = false; closeRail(); if (document.activeElement && el.side.contains(document.activeElement)) document.activeElement.blur(); }
    }
  }
  function onKey(e) {
    if (H.open && e.key === "Escape" && !root.classList.contains("lb-gdrawer-open")) {
      e.preventDefault(); H.armed = false;
      const back = el.side.contains(document.activeElement); closeRail();
      if (back) document.activeElement.blur();
      return;
    }
    if (!root.classList.contains("lb-gdrawer-open")) return;
    if (e.key === "Escape") { e.preventDefault(); return closeDrawer(); }
    if (e.key !== "Tab") return;   // keep the focus inside the open drawer
    const f = [...el.side.querySelectorAll("a[href], button")].filter((n) => n.offsetParent !== null && !n.closest("[inert]"));
    if (!f.length) return;
    const first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  // ---------- phones: the bottom bar slides away while scrolling down ----------
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
    // HQ's view: { view: "home", title: "בית" }
    setCurrent({ view, title } = {}) { S.view = view || null; S.viewTitle = title || ""; draw(); },
  };

  if (document.body) mount(); else document.addEventListener("DOMContentLoaded", mount);
})();
