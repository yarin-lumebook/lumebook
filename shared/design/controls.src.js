/* LumeBook controls (Yarin, 7 Nov 2026: "there are some default chrome/mac elements, design them yourself").
   On a mouse or trackpad the popups the browser draws itself are replaced by glass popups of the design system:
   - select           -> lb-selmenu (a list of the options, the chosen one ticked, groups kept)
   - input type=date  -> lb-cal (a month grid, Sunday first, Today and Clear)
   - input type=time  -> lb-timepick (hours and minutes in two columns, minutes in the field's step)
   Nothing in a page changes: the real select or input stays where it is and keeps its value; the script sets it and fires input and
   change (bubbling), so every existing listener works, including pages that draw their selects later (the listeners are on the
   document). Touch screens keep the system pickers. Keyboard: Space or Enter on a select, Alt+Down or F4 on a date or time
   field open the popup; typing into a date or time field works as before. data-native on a field leaves it alone. Fields inside
   a shadow root (the site editor's own) are not touched. Styles: "native controls, redrawn" in lumebook.css.
   Source: shared/design/controls.src.js. design.py appends it to nav.js (HQ and the SMM plan link that) and inlines it with
   design.head() on every page, also where nav=False. */
(() => {
  "use strict";
  if (window.LBControls) return;
  const FINE = window.matchMedia("(hover: hover) and (pointer: fine)");
  const T = {
    he: { clear: "ניקוי", today: "היום", prev: "החודש הקודם", next: "החודש הבא", done: "אישור", hour: "שעה", min: "דקות", pick: "בחירת תאריך", time: "בחירת שעה" },
    en: { clear: "Clear", today: "Today", prev: "Previous month", next: "Next month", done: "Done", hour: "Hour", min: "Min", pick: "Choose a date", time: "Choose a time" },
  };
  let cur = null;   // the open popup: { el, owner, off }

  const lang = (n) => ((n.closest("[lang]") || document.documentElement).lang || "he").slice(0, 2).toLowerCase();
  const tr = (n) => T[lang(n)] || T.en;
  // the direction of the page around a field, not of the field: pages set date and time fields left to right so a date never flips
  const isRtl = (n) => getComputedStyle(n.tagName === "SELECT" ? n : n.parentElement || n).direction === "rtl";
  const pad = (n) => String(n).padStart(2, "0");
  const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const parseISO = (v) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || ""); return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null; };
  const same = (a, b) => a && b && a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
  const make = (tag, cls, attrs) => { const n = document.createElement(tag); if (cls) n.className = cls; for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, v); return n; };
  const emit = (n) => { n.dispatchEvent(new Event("input", { bubbles: true })); n.dispatchEvent(new Event("change", { bubbles: true })); };
  const usable = (n) => n && !n.disabled && !n.readOnly && n.dataset.native === undefined && !n.closest("[data-native]");
  const chev = (path) => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${path}"/></svg>`;

  // ---------- opening, placing and closing ----------
  function show(pop, owner, minWidth) {
    const host = owner.closest("dialog[open]") || document.body;
    pop.style.visibility = "hidden";
    if (minWidth) pop.style.minWidth = Math.max(minWidth, 160) + "px";
    host.append(pop);
    const a = owner.getBoundingClientRect(), p = pop.getBoundingClientRect(), vw = innerWidth, vh = innerHeight;
    const below = vh - a.bottom - 10, above = a.top - 10, up = below < Math.min(p.height, 260) && above > below;
    const room = (up ? above : below) - 6;
    if (p.height > room) pop.style.maxHeight = Math.max(160, room) + "px";
    const h = Math.min(p.height, parseFloat(pop.style.maxHeight) || p.height);
    let left = isRtl(owner) ? a.right - p.width : a.left;
    left = Math.max(8, Math.min(left, vw - p.width - 8));
    pop.style.left = left + "px";
    pop.style.top = (up ? Math.max(8, a.top - h - 6) : a.bottom + 6) + "px";
    pop.style.setProperty("--ox", Math.max(12, Math.min(a.left + a.width / 2 - left, p.width - 12)) + "px");
    pop.classList.toggle("is-up", up);
    pop.style.visibility = "";
    owner.setAttribute("aria-expanded", "true");
    const onOutside = (e) => { if (!pop.contains(e.target) && !owner.contains(e.target)) close(false); };
    const onScroll = (e) => { if (!pop.contains(e.target)) close(false); };
    const onResize = () => close(false);
    document.addEventListener("pointerdown", onOutside, true);
    addEventListener("scroll", onScroll, true);
    addEventListener("resize", onResize);
    pop.addEventListener("mousedown", (e) => { if (!e.target.closest("input, select, textarea")) e.preventDefault(); });   // keep the page's focus and selection
    cur = { el: pop, owner, off() { document.removeEventListener("pointerdown", onOutside, true); removeEventListener("scroll", onScroll, true); removeEventListener("resize", onResize); } };
  }
  function close(refocus = true) {
    if (!cur) return;
    const { el, owner, off } = cur;
    cur = null; off(); el.remove(); owner.removeAttribute("aria-expanded");
    if (refocus && owner.isConnected) owner.focus({ preventScroll: true });
  }

  // ---------- select ----------
  function openSelect(sel) {
    if (cur && cur.owner === sel) return close();
    close(false);
    sel.setAttribute("aria-haspopup", "listbox");
    const menu = make("div", "lb-popover lb-selmenu", { role: "listbox", tabindex: "-1" });
    menu.dir = isRtl(sel) ? "rtl" : "ltr";
    const items = [];
    const add = (opt, grp) => {
      const b = make("button", "", { type: "button", role: "option", tabindex: "-1", "aria-selected": String(opt.selected) });
      b.dataset.i = opt.index;
      b.disabled = opt.disabled || !!(grp && grp.disabled);
      const t = make("span", "lb-selopt-text"); t.textContent = opt.label || opt.textContent || " ";
      b.append(t); menu.append(b); items.push(b);
    };
    for (const n of sel.children) {
      if (n.tagName === "OPTGROUP") { const g = make("div", "lb-popover-label"); g.textContent = n.label; menu.append(g); for (const o of n.children) add(o, n); }
      else if (n.tagName === "OPTION") add(n);
    }
    const choose = (b) => {
      const i = +b.dataset.i;
      close(false);
      if (sel.selectedIndex !== i) { sel.selectedIndex = i; emit(sel); }
      if (sel.isConnected) sel.focus({ preventScroll: true });
    };
    const live = () => items.filter((b) => !b.disabled);
    const focusItem = (b) => { items.forEach((x) => x.classList.toggle("is-active", x === b)); if (b) { b.focus({ preventScroll: true }); b.scrollIntoView({ block: "nearest" }); } };
    let typed = "", timer = 0;
    menu.addEventListener("click", (e) => { const b = e.target.closest("button[role=option]"); if (b && !b.disabled) choose(b); });
    menu.addEventListener("keydown", (e) => {
      const l = live(), at = l.indexOf(document.activeElement);
      if (e.key === "ArrowDown") { e.preventDefault(); focusItem(l[Math.min(l.length - 1, at + 1)]); }
      else if (e.key === "ArrowUp") { e.preventDefault(); focusItem(l[Math.max(0, at - 1)]); }
      else if (e.key === "Home") { e.preventDefault(); focusItem(l[0]); }
      else if (e.key === "End") { e.preventDefault(); focusItem(l[l.length - 1]); }
      else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); }
      else if (e.key === "Tab") close();
      else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (at >= 0) choose(l[at]); }
      else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) {   // type-ahead
        clearTimeout(timer); typed += e.key.toLowerCase(); timer = setTimeout(() => { typed = ""; }, 700);
        const hit = l.find((b) => b.textContent.trim().toLowerCase().startsWith(typed)); if (hit) focusItem(hit);
      }
    });
    show(menu, sel, sel.getBoundingClientRect().width);
    focusItem(items.find((b) => b.getAttribute("aria-selected") === "true" && !b.disabled) || live()[0]);
  }

  // ---------- date ----------
  function openDate(inp) {
    if (cur && cur.owner === inp) return close();
    close(false);
    const L = tr(inp), lg = lang(inp), rtl = isRtl(inp);
    const val = parseISO(inp.value), min = parseISO(inp.min), max = parseISO(inp.max), today = new Date();
    const monthFmt = new Intl.DateTimeFormat(lg, { month: "long", year: "numeric" }), fullFmt = new Intl.DateTimeFormat(lg, { dateStyle: "full" });
    const dowFmt = new Intl.DateTimeFormat(lg, { weekday: "narrow" });
    let view = new Date((val || today).getFullYear(), (val || today).getMonth(), 1), fd = val || today;
    const pop = make("div", "lb-popover lb-cal", { role: "dialog", "aria-label": L.pick });
    pop.dir = rtl ? "rtl" : "ltr";
    const head = make("div", "lb-cal-head"), prev = make("button", "lb-cal-nav", { type: "button", "aria-label": L.prev }), next = make("button", "lb-cal-nav", { type: "button", "aria-label": L.next });
    const title = make("h3", "lb-cal-title", { "aria-live": "polite" });
    prev.innerHTML = chev(rtl ? "M9 6l6 6-6 6" : "M15 6l-6 6 6 6"); next.innerHTML = chev(rtl ? "M15 6l-6 6 6 6" : "M9 6l6 6-6 6");
    head.append(prev, title, next);
    const grid = make("div", "lb-cal-grid", { role: "grid" });
    const foot = make("div", "lb-cal-foot");
    const todayBtn = make("button", "lb-btn ghost sm", { type: "button" }); todayBtn.textContent = L.today;
    const clearBtn = make("button", "lb-btn ghost sm", { type: "button" }); clearBtn.textContent = L.clear;
    if (!inp.required) foot.append(clearBtn);
    foot.append(todayBtn);
    pop.append(head, grid, foot);
    const out = (d) => (min && d < min) || (max && d > max);
    const pick = (d) => { close(false); inp.value = iso(d); emit(inp); if (inp.isConnected) inp.focus({ preventScroll: true }); };
    const render = (focus) => {
      title.textContent = monthFmt.format(view);
      grid.textContent = "";
      for (let i = 0; i < 7; i++) { const d = make("span", "lb-cal-dow", { "aria-hidden": "true" }); d.textContent = dowFmt.format(new Date(2023, 0, 1 + i)); grid.append(d); }
      const first = new Date(view.getFullYear(), view.getMonth(), 1 - view.getDay());
      const focusable = same(fd, view) || (fd.getFullYear() === view.getFullYear() && fd.getMonth() === view.getMonth()) ? fd : view;
      for (let i = 0; i < 42; i++) {
        const d = new Date(first.getFullYear(), first.getMonth(), first.getDate() + i);
        const b = make("button", "lb-cal-day", { type: "button", role: "gridcell", "aria-label": fullFmt.format(d), tabindex: same(d, focusable) ? "0" : "-1" });
        b.dataset.d = iso(d); b.textContent = d.getDate(); b.disabled = !!out(d);
        if (d.getMonth() !== view.getMonth()) b.classList.add("is-out");
        if (same(d, today)) b.classList.add("is-today");
        if (same(d, val)) b.setAttribute("aria-selected", "true");
        grid.append(b);
      }
      if (focus) grid.querySelector(`[data-d="${iso(fd)}"]`)?.focus({ preventScroll: true });
    };
    const go = (d) => { fd = d; if (d.getMonth() !== view.getMonth() || d.getFullYear() !== view.getFullYear()) view = new Date(d.getFullYear(), d.getMonth(), 1); render(true); };
    prev.addEventListener("click", () => { view = new Date(view.getFullYear(), view.getMonth() - 1, 1); fd = view; render(false); });
    next.addEventListener("click", () => { view = new Date(view.getFullYear(), view.getMonth() + 1, 1); fd = view; render(false); });
    todayBtn.addEventListener("click", () => { if (!out(today)) pick(today); });
    clearBtn.addEventListener("click", () => { close(false); inp.value = ""; emit(inp); if (inp.isConnected) inp.focus({ preventScroll: true }); });
    grid.addEventListener("click", (e) => { const b = e.target.closest(".lb-cal-day"); if (b && !b.disabled) pick(parseISO(b.dataset.d)); });
    pop.addEventListener("keydown", (e) => {
      const day = (n) => new Date(fd.getFullYear(), fd.getMonth(), fd.getDate() + n), step = rtl ? -1 : 1;
      if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); }
      else if (e.key === "Tab" && !e.shiftKey && document.activeElement === (foot.lastElementChild)) close();
      else if (!e.target.closest(".lb-cal-day")) return;
      else if (e.key === "ArrowRight") { e.preventDefault(); go(day(step)); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); go(day(-step)); }
      else if (e.key === "ArrowDown") { e.preventDefault(); go(day(7)); }
      else if (e.key === "ArrowUp") { e.preventDefault(); go(day(-7)); }
      else if (e.key === "PageDown") { e.preventDefault(); go(new Date(fd.getFullYear(), fd.getMonth() + 1, Math.min(fd.getDate(), 28))); }
      else if (e.key === "PageUp") { e.preventDefault(); go(new Date(fd.getFullYear(), fd.getMonth() - 1, Math.min(fd.getDate(), 28))); }
      else if (e.key === "Home") { e.preventDefault(); go(day(-fd.getDay())); }
      else if (e.key === "End") { e.preventDefault(); go(day(6 - fd.getDay())); }
    });
    render(false);
    show(pop, inp);
    (grid.querySelector('[tabindex="0"]') || grid.querySelector(".lb-cal-day:not(:disabled)"))?.focus({ preventScroll: true });
  }

  // ---------- time ----------
  function openTime(inp) {
    if (cur && cur.owner === inp) return close();
    close(false);
    const L = tr(inp), stepMin = Math.max(1, Math.round((parseFloat(inp.step) || 60) / 60));
    const m0 = /^(\d{2}):(\d{2})/.exec(inp.value || "");
    let h = m0 ? +m0[1] : null, m = m0 ? +m0[2] : null;
    const pop = make("div", "lb-popover lb-timepick", { role: "dialog", "aria-label": L.time });
    const cols = make("div", "lb-timepick-cols"), hc = make("div", "lb-timepick-col", { role: "listbox", "aria-label": L.hour }), mc = make("div", "lb-timepick-col", { role: "listbox", "aria-label": L.min });
    const hh = make("b"); hh.textContent = L.hour; const mm = make("b"); mm.textContent = L.min; hc.append(hh); mc.append(mm);
    const opt = (v, kind) => { const b = make("button", "lb-timepick-opt", { type: "button", role: "option", "data-k": kind, "data-v": v, "aria-selected": "false" }); b.textContent = pad(v); return b; };
    for (let i = 0; i < 24; i++) hc.append(opt(i, "h"));
    for (let i = 0; i < 60; i += stepMin) mc.append(opt(i, "m"));
    cols.append(hc, mc);
    const foot = make("div", "lb-cal-foot");
    const clearBtn = make("button", "lb-btn ghost sm", { type: "button" }); clearBtn.textContent = L.clear;
    const doneBtn = make("button", "lb-btn sm", { type: "button" }); doneBtn.textContent = L.done;
    if (!inp.required) foot.append(clearBtn);
    foot.append(doneBtn);
    pop.append(cols, foot);
    const mark = () => pop.querySelectorAll(".lb-timepick-opt").forEach((b) => b.setAttribute("aria-selected", String(+b.dataset.v === (b.dataset.k === "h" ? h : m))));
    const write = () => { inp.value = `${pad(h ?? 0)}:${pad(m ?? 0)}`; emit(inp); mark(); };
    pop.addEventListener("click", (e) => {
      const b = e.target.closest(".lb-timepick-opt"); if (!b) return;
      if (b.dataset.k === "h") { h = +b.dataset.v; if (m === null) m = 0; write(); }
      else { m = +b.dataset.v; if (h === null) h = new Date().getHours(); write(); close(); }
    });
    clearBtn.addEventListener("click", () => { close(false); inp.value = ""; emit(inp); if (inp.isConnected) inp.focus({ preventScroll: true }); });
    doneBtn.addEventListener("click", () => close());
    pop.addEventListener("keydown", (e) => { if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); } });
    mark();
    show(pop, inp);
    for (const c of [hc, mc]) { const on = c.querySelector('[aria-selected="true"]'); if (on) c.scrollTop = on.offsetTop - c.clientHeight / 2 + on.offsetHeight / 2; }
    (pop.querySelector('[aria-selected="true"]') || pop.querySelector(".lb-timepick-opt"))?.focus({ preventScroll: true });
  }

  // ---------- dates always read dd / mm / yyyy (Yarin, 08 Nov 2026) ----------
  // The browser draws a date field in the Mac's own order (mm/dd/yyyy) and the page cannot change that. So the native text is made
  // transparent (data-dmy) and the day-first text is painted as the field's background (--lb-datetxt, see lumebook.css).
  const paintDate = (inp) => {
    if (inp.type !== "date" || !usable(inp) || !inp.classList.contains("lb-input")) return;
    const cs = getComputedStyle(inp), d = parseISO(inp.value), fs = parseFloat(cs.fontSize) || 16;
    const txt = d ? `${pad(d.getDate())} / ${pad(d.getMonth() + 1)} / ${d.getFullYear()}` : "dd / mm / yyyy";
    const fam = (cs.fontFamily || "sans-serif").replace(/["'<>&]/g, "");
    const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='${Math.ceil(fs * 9)}' height='${Math.ceil(fs * 2)}'><text x='0' y='50%' dominant-baseline='central' font-family='${fam}' font-size='${fs}' fill='${cs.color}' fill-opacity='${d ? 1 : 0.45}'>${txt}</text></svg>`;
    inp.setAttribute("data-dmy", "");
    inp.style.setProperty("--lb-datetxt", `url("data:image/svg+xml,${encodeURIComponent(svg)}")`);
  };
  const paintAll = (root) => { if (root.matches && root.matches("input[type=date]")) paintDate(root); root.querySelectorAll && root.querySelectorAll("input[type=date]").forEach(paintDate); };
  const valueDesc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
  if (valueDesc && valueDesc.set) Object.defineProperty(HTMLInputElement.prototype, "value", { ...valueDesc, set(v) { valueDesc.set.call(this, v); if (this.type === "date") paintDate(this); } });   // pages that set .value in code
  document.addEventListener("input", (e) => { if (e.target instanceof HTMLInputElement && e.target.type === "date") paintDate(e.target); }, true);
  document.addEventListener("change", (e) => { if (e.target instanceof HTMLInputElement && e.target.type === "date") paintDate(e.target); }, true);
  const startPaint = () => {
    paintAll(document);
    new MutationObserver((ms) => { for (const m of ms) { if (m.type === "attributes") paintDate(m.target); else m.addedNodes.forEach((n) => n.nodeType === 1 && paintAll(n)); } })
      .observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ["value", "class", "disabled"] });
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", startPaint); else startPaint();

  // ---------- wiring: listeners on the document, so selects and fields drawn later work too ----------
  const kind = (t) => {
    if (!(t instanceof Element) || !FINE.matches) return null;
    const sel = t.closest("select"); if (sel && usable(sel) && !sel.multiple && sel.size <= 1) return ["select", sel];
    const inp = t.closest("input[type=date], input[type=time]"); if (inp && usable(inp)) return [inp.type, inp];
    return null;
  };
  const open = (k) => (k[0] === "select" ? openSelect(k[1]) : k[0] === "date" ? openDate(k[1]) : openTime(k[1]));
  document.addEventListener("mousedown", (e) => {
    if (e.button !== 0) return;
    const k = kind(e.target); if (!k) return;
    e.preventDefault(); k[1].focus({ preventScroll: true }); open(k);
  }, true);
  document.addEventListener("keydown", (e) => {
    if (cur) return;
    const k = kind(e.target); if (!k) return;
    const go = k[0] === "select" ? (e.key === " " || e.key === "Enter") && !e.altKey : (e.altKey && e.key === "ArrowDown") || e.key === "F4";
    if (go) { e.preventDefault(); open(k); }
  }, true);
  document.addEventListener("keydown", (e) => { if (cur && e.key === "Escape") { e.preventDefault(); close(); } });

  window.LBControls = { close };
})();
