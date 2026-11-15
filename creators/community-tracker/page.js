/* קהילות פייסבוק, the Facebook community tracker (15 Nov 2026). Inlined by build.py after window.CT_* (groups from the parent
   community research, default message texts, icons, metric hues, creator map handles). Yarin's work lives on the project server
   (GET /api/communities/state, PUT /api/communities/doc?path=<kind>/<id>, tools/communities.py); anywhere else the page keeps it
   in this browser only and says so. Hebrew, right to left.
   Since 15 Nov 2026 it runs inside the creator map as its third view (Yarin: "a separate view for creators, professionals and facebook
   communities ... merge the other session working on the facebook communities map"). With window.CT_EMBED set, the map owns the address
   bar (#fb-<view>), the side bar and the one reminders stack of all three views: this script draws the communities pages when the map
   calls CT.show(), handles only events inside .ct-scope, and gives the map its reminders and cards through window.CT. */
(function () {
  "use strict";
  const EMB = !!window.CT_EMBED, host = () => window.CT_HOST || {};
  let active = !EMB;   // embedded: true while the map shows the communities view
  const G = window.CT_GROUPS || [], IC = window.CT_ICONS || {}, CAT = window.CT_CAT || {}, META = window.CT_META || {};
  const TPL0 = window.CT_TEMPLATES || { parent: [], ugc: [] };
  const CREATORS = new Set(window.CT_CREATORS || []);
  const HDR = { "Content-Type": "application/json", "X-LumeBook-Board": "1" };
  const LS_STATE = "ct-tracker-v1", LS_UI = "ct-ui-v1";
  const byId = {}; G.forEach(g => { byId[g.id] = g; });

  const TRACK = { parent: "הורים", ugc: "יוצרי UGC" };
  const TRACK_ICON = { parent: "people", ugc: "sparkle" };
  const GS = [["new", "עוד לא התחלנו"], ["join", "ביקשתי להצטרף"], ["member", "חבר בקבוצה"], ["admin", "פניתי למנהלים"],
    ["ok", "אישרו לפרסם"], ["active", "פרסמנו"], ["later", "לנסות שוב"], ["no", "לא מתאים"]];
  const GSL = Object.fromEntries(GS);
  const LS = {
    parent: [["new", "חדש"], ["contacted", "פניתי"], ["replied", "ענו"], ["qualified", "מילאו טופס"], ["booked", "נקבע צילום"], ["done", "צולם"], ["no", "לא מתאים"]],
    ugc: [["new", "חדש"], ["contacted", "פניתי"], ["replied", "ענו"], ["qualified", "נשלחו פרטים"], ["booked", "הצטרפו"], ["done", "נוצר תוכן"], ["no", "לא מתאים"]],
    all: [["new", "חדש"], ["contacted", "פניתי"], ["replied", "ענו"], ["qualified", "טופס או פרטים"], ["booked", "צילום נקבע או הצטרפו"], ["done", "צולם או נוצר תוכן"], ["no", "לא מתאים"]]
  };
  const PS = [["live", "עלה"], ["pending", "מחכה לאישור"], ["declined", "לא אושר"], ["removed", "הוסר"]];
  const PSL = Object.fromEntries(PS);
  const CH = [["comment", "תגובה לפוסט"], ["dm", "הודעה בפרטי"], ["whatsapp", "וואטסאפ"], ["form", "טופס"], ["email", "מייל"], ["other", "אחר"]];
  const CHL = Object.fromEntries(CH);
  const AP = [["Post directly", "לפרסם ישירות"], ["Ask admin first", "לפנות קודם למנהלים"], ["Paid post or formal partnership", "פוסט בתשלום או שותפות"],
    ["Monitor", "מעקב בלבד"], ["Do not use", "לא להשתמש"]];
  const AP_CHIP = { "Post directly": "success", "Ask admin first": "info", "Paid post or formal partnership": "accent", "Monitor": "outline", "Do not use": "danger" };
  const BANDS = [["1", "באשקלון"], ["2", "עד 30 ק״מ"], ["3", "30 עד 55 ק״מ"], ["4", "55 עד 80 ק״מ"], ["5", "מעל 80 ק״מ"], ["6", "ארצית"]];
  const PRI = { A: 0, B: 1, C: 2, "": 3, Reject: 4 };
  const TITLES = { home: "בית", reminders: "תזכורות", parents: "קהילות הורים", ugc: "קהילות יוצרי UGC", posts: "פוסטים", leads: "לידים",
    templates: "נוסחים להעתקה", method: "מאיפה הקבוצות", search: "חיפוש" };
  const LISTS = ["parents", "ugc", "posts", "leads"];

  let S = { groups: {}, posts: {}, leads: {}, settings: {} };
  let online = false, pending = 0, route = "home", Q = "", drawerGid = null;
  let IDX = { posts: {}, leads: {}, leadsByPost: {} };
  const UI = Object.assign({
    parents: { st: "all", pri: "", ap: "", band: "", priv: "", rej: false, sort: "rec", n: 30 },
    ugc: { st: "all", pri: "", ap: "", band: "", priv: "", rej: false, sort: "rec", n: 30 },
    posts: { track: "all", st: "all" }, leads: { track: "all", st: "all" }
  }, stored(LS_UI, {}));

  // ---- small helpers ---------------------------------------------------------------------------------------------------
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const ic = n => IC[n] || "";
  const inScope = el => !EMB || !!(el && el.closest && el.closest(".ct-scope"));
  // embedded, every "#view" link in a drawn page becomes "#fb-view" (the map's address for it); "#reminders" is the map's shared stack
  function fbLinks(root) {
    if (!EMB || !root) return;
    root.querySelectorAll('a[href^="#"]').forEach(a => { const h = a.getAttribute("href"), k = h.slice(1).split("?")[0]; if (!TITLES[k] || k === "reminders") return; a.setAttribute("href", "#fb-" + h.slice(1)); });
  }
  const num = n => (n == null || n === "" ? "" : Number(n).toLocaleString("he-IL"));
  function stored(k, d) { try { const v = JSON.parse(localStorage.getItem(k) || "null"); return v == null ? d : v; } catch (x) { return d; } }
  function store(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (x) { /* private window */ } }
  function iso(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
  function today() { return iso(new Date()); }
  function addDays(s, n) { const p = s.split("-").map(Number); return iso(new Date(p[0], p[1] - 1, p[2] + n)); }
  function days(a, b) { const u = s => { const p = s.split("-").map(Number); return Date.UTC(p[0], p[1] - 1, p[2]); }; return Math.round((u(b) - u(a)) / 864e5); }
  function fmt(s) { if (!s) return ""; const p = s.slice(0, 10).split("-"); return '<bdi dir="ltr">' + p[2] + " / " + p[1] + " / " + p[0] + "</bdi>"; }
  function rel(s) {
    const n = days(today(), s);
    if (n === 0) return "היום"; if (n === 1) return "מחר"; if (n === -1) return "אתמול";
    if (n === 2) return "בעוד יומיים"; if (n === -2) return "לפני יומיים";
    return n < 0 ? "לפני " + (-n) + " ימים" : "בעוד " + n + " ימים";
  }
  function nowIso() { const d = new Date(); return iso(d) + "T" + [d.getHours(), d.getMinutes(), d.getSeconds()].map(n => String(n).padStart(2, "0")).join(":"); }   // local time, so the date shown is the day it happened
  function newId(p) { return p + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }
  function clone(o) { return JSON.parse(JSON.stringify(o || {})); }
  function firstName(n) { return String(n || "").trim().split(/\s+/)[0] || ""; }
  function km(g) { return g.km == null ? "" : (g.band === 1 ? "באשקלון" : g.km + " ק״מ"); }
  function toast(text) {
    const t = $("#ctToast"); t.textContent = text; t.hidden = false;
    clearTimeout(toast.t); toast.t = setTimeout(() => { t.hidden = true; }, 2600);
  }
  function copy(text) {
    const done = () => toast("הועתק");
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text).then(done, () => fallback());
    fallback();
    function fallback() {
      const a = document.createElement("textarea"); a.value = text; a.setAttribute("readonly", ""); a.style.position = "fixed"; a.style.opacity = "0";
      document.body.appendChild(a); a.select(); try { document.execCommand("copy"); done(); } catch (x) { toast("ההעתקה לא עבדה"); } a.remove();
    }
  }

  // ---- groups, posts and leads -----------------------------------------------------------------------------------------
  function customGroup(id, d) {
    const c = d.custom || {};
    return { id, name: c.name || "", url: c.url || "", about: "", track: c.track || "parent", pri: "", band: 7, km: null, geo: c.geo || "",
      mem: c.members_n, pm: null, priv: { Public: "ציבורית", Private: "פרטית" }[c.privacy] || "", privKey: c.privacy || "", appr: "",
      ap: "", apHe: "", pol: c.policy || "", notes: "", contact: "", seg: [], lang: "", conf: "", checked: "", custom: true };
  }
  function grp(id) { return byId[id] || (S.groups[id] && S.groups[id].custom ? customGroup(id, S.groups[id]) : null); }
  function allGroups() {
    const out = G.slice();
    Object.keys(S.groups).forEach(id => { if (S.groups[id].custom && !byId[id]) out.push(customGroup(id, S.groups[id])); });
    return out;
  }
  function gst(id) { return (S.groups[id] && S.groups[id].status) || "new"; }
  function gdoc(id) {
    return Object.assign({ status: "new", next_on: "", next_note: "", joined_on: "", asked_on: "", ok_on: "", post_day: "", notes: [] }, clone(S.groups[id]));
  }
  function lsl(track, st) { return (Object.fromEntries(LS[track] || LS.all))[st] || st; }
  function index() {
    IDX = { posts: {}, leads: {}, leadsByPost: {} };
    Object.keys(S.posts).forEach(id => { const p = S.posts[id]; (IDX.posts[p.gid] = IDX.posts[p.gid] || []).push(id); });
    Object.keys(S.leads).forEach(id => {
      const l = S.leads[id]; (IDX.leads[l.gid] = IDX.leads[l.gid] || []).push(id);
      if (l.pid) (IDX.leadsByPost[l.pid] = IDX.leadsByPost[l.pid] || []).push(id);
    });
    Object.values(IDX.posts).forEach(a => a.sort((x, y) => (S.posts[y].on || "").localeCompare(S.posts[x].on || "")));
  }
  function templates(track) {
    const m = S.settings.main, t = m && m.templates && m.templates[track];
    return t && t.length ? t : (TPL0[track] || []);
  }
  function fillTemplate(text, ctx) {
    let t = text;
    if (ctx.city) t = t.split("[העיר]").join(ctx.city);
    if (ctx.name) t = t.split("[שם]").join(ctx.name);
    return t;
  }

  // ---- saving ---------------------------------------------------------------------------------------------------------
  function setSave(state, msg) {
    const el = $("#ctSave"); el.className = "lb-savestate" + (state === "ok" ? "" : " is-" + state);
    el.textContent = state === "wait" ? "שומר…" : state === "error" ? (msg ? "השמירה נכשלה: " + msg : "השמירה נכשלה")
      : state === "local" ? "נשמר רק בדפדפן הזה" : "הכול נשמר";
    el.title = state === "local" ? "הדף לא פתוח בשרת הפרויקט (localhost:8780), אז העבודה נשמרת רק בדפדפן הזה" : "";
  }
  let chain = Promise.resolve();
  function put(kind, id, doc) {
    if (doc == null) delete S[kind][id]; else S[kind][id] = Object.assign({}, S[kind][id] || {}, doc);
    index();
    if (!online) { store(LS_STATE, S); setSave("local"); return Promise.resolve(); }
    pending++; setSave("wait");
    const run = () => fetch("/api/communities/doc?path=" + encodeURIComponent(kind + "/" + id), { method: "PUT", headers: HDR, body: JSON.stringify(doc) })
      .then(r => r.json().catch(() => ({})).then(j => ({ ok: r.ok, j })))
      .then(({ ok, j }) => {
        if (!ok) throw new Error(j.error || "שגיאה בשרת");
        if (j.doc) S[kind][id] = j.doc; else delete S[kind][id];
        index(); pending--; if (!pending) setSave("ok");
      })
      .catch(e => { pending--; setSave("error", e.message); toast("השמירה נכשלה: " + e.message); throw e; });
    chain = chain.then(run, run);
    return chain;
  }
  function putR(kind, id, doc) { const pr = put(kind, id, doc); refresh(); return pr.then(refresh, refresh); }   // redraw now and again with the saved copy
  function load() {
    return fetch("/api/communities/state", { cache: "no-store" })
      .then(r => { if (!r.ok) throw new Error("no server"); return r.json(); })
      .then(d => { S = norm(d); online = true; setSave("ok"); })
      .catch(() => { S = norm(stored(LS_STATE, {})); online = false; setSave("local"); })
      .then(() => { index(); });
  }
  function norm(d) { const o = { groups: {}, posts: {}, leads: {}, settings: {} }; ["groups", "posts", "leads", "settings"].forEach(k => { if (d && d[k] && typeof d[k] === "object") o[k] = d[k]; }); return o; }

  // ---- what to do next (automatic reminders, like the creator map) --------------------------------------------------------
  function groupNext(st, g) {
    const t = today();
    if (st === "join") return [addDays(t, 3), "לבדוק אם אישרו את ההצטרפות"];
    if (st === "member") return [t, g.ap === "Post directly" ? "לפרסם פוסט" : "לפנות למנהלי הקבוצה"];
    if (st === "admin") return [addDays(t, 3), "לבדוק אם המנהלים ענו"];
    if (st === "ok") return [t, "לפרסם פוסט"];
    if (st === "later") return [addDays(t, 30), "לנסות שוב"];
    return ["", ""];
  }
  function leadNext(st, track) {
    const t = today();
    if (st === "contacted") return [addDays(t, 2), "לבדוק אם ענו"];
    if (st === "replied") return [t, "להמשיך את השיחה"];
    if (st === "qualified") return [addDays(t, 2), track === "ugc" ? "לבדוק אם החליטו" : "לקבוע יום צילום"];
    if (st === "booked") return track === "ugc" ? [addDays(t, 7), "לבדוק שהתוכן עלה"] : null;
    if (st === "done" || st === "no") return ["", ""];
    return null;
  }
  function setGroupStatus(id, st) {
    const g = grp(id), d = gdoc(id), t = today();
    if (!g || d.status === st) return Promise.resolve();
    d.status = st;
    if (st === "member" && !d.joined_on) d.joined_on = t;
    if (st === "admin" && !d.asked_on) d.asked_on = t;
    if (st === "ok" && !d.ok_on) d.ok_on = t;
    const nx = groupNext(st, g); d.next_on = nx[0]; d.next_note = nx[1];
    d.notes.push({ at: nowIso(), t: "השלב השתנה ל: " + GSL[st] });
    return putR("groups", id, d);
  }
  function setLeadStatus(id, st) {
    const l = clone(S.leads[id]); if (!l || l.status === st) return Promise.resolve();
    l.status = st; l.log = l.log || []; l.log.push({ at: nowIso(), t: "השלב השתנה ל: " + lsl(l.track, st) });
    const nx = leadNext(st, l.track); if (nx) { l.next_on = nx[0]; l.next_note = nx[1]; }
    return putR("leads", id, l);
  }
  function postDue(p) {
    const lim = addDays(today(), 7);
    if (p.state === "pending") { const d = addDays(p.on, 1); return d <= lim ? { date: d, text: "לבדוק אם הפוסט אושר" } : null; }
    if (p.state !== "live") return null;
    for (const n of [2, 7]) {
      const d = addDays(p.on, n);
      if (!p.checked_on || p.checked_on < d) return d <= lim ? { date: d, text: n === 2 ? "לעדכן תגובות ולידים" : "בדיקה אחרונה של תגובות ולידים" } : null;
    }
    return null;
  }
  function reminders() {
    const out = [];
    Object.keys(S.groups).forEach(id => { const d = S.groups[id], g = grp(id); if (g && d.next_on && d.status !== "no") out.push({ k: "group", id, date: d.next_on, title: g.name, text: d.next_note || "הצעד הבא", track: g.track }); });
    Object.keys(S.leads).forEach(id => { const l = S.leads[id]; if (l.next_on && l.status !== "done" && l.status !== "no") out.push({ k: "lead", id, date: l.next_on, title: l.name, text: l.next_note || "הצעד הבא", track: l.track }); });
    Object.keys(S.posts).forEach(id => { const p = S.posts[id], g = grp(p.gid), due = postDue(p); if (due && g) out.push({ k: "post", id, date: due.date, title: g.name, text: due.text, track: g.track }); });
    return out.sort((a, b) => a.date.localeCompare(b.date));
  }

  // ---- pieces ------------------------------------------------------------------------------------------------------------
  function cube(key, label, icon, value, foot, cls) {
    return '<div class="lb-metric ' + (cls || CAT[key] || "") + '"><p class="lb-metric-label"><span class="lb-tile">' + ic(icon) + "</span>" + esc(label) + "</p>"
      + '<p class="lb-metric-value">' + value + "</p>" + (foot ? '<p class="lb-metric-foot">' + foot + "</p>" : "") + "</div>";
  }
  function pill(cls, label, attrs) {
    return attrs ? '<button type="button" class="ct-pill ' + cls + '" ' + attrs + ">" + esc(label) + ic("chevron-down") + "</button>"
      : '<span class="ct-pill ' + cls + '">' + esc(label) + "</span>";
  }
  function pipe(list, prefix, counts, hrefOf, skipNew) {
    const total = list.reduce((s, x) => s + (skipNew && x[0] === "new" ? 0 : counts[x[0]] || 0), 0);
    const bar = total ? '<div class="ct-pipe">' + list.filter(x => counts[x[0]] && !(skipNew && x[0] === "new"))
      .map(x => '<a class="' + prefix + x[0] + '" href="' + hrefOf(x[0]) + '" style="flex:' + counts[x[0]] + '" title="' + esc(x[1]) + ": " + counts[x[0]] + '"></a>').join("") + "</div>" : "";
    const legend = '<div class="ct-legend">' + list.filter(x => counts[x[0]]).map(x => '<a class="' + prefix + x[0] + '" href="' + hrefOf(x[0]) + '">' + esc(x[1]) + " <b>" + counts[x[0]] + "</b></a>").join("") + "</div>";
    return bar + legend;
  }
  function count(list, key) { const c = {}; list.forEach(x => { const k = key(x); c[k] = (c[k] || 0) + 1; }); return c; }
  function nextHtml(date, note) {
    if (!date) return '<span class="ct-next">' + ic("clock") + "<span>אין צעד הבא</span></span>";
    const t = today(), cls = date < t ? " is-late" : date === t ? " is-due" : "";
    return '<span class="ct-next' + cls + '" title="' + esc(note) + '">' + ic("clock") + "<span>" + rel(date) + (note ? ": " + esc(note) : "") + "</span></span>";
  }
  function contactIcons(l) {
    const a = [];
    if (l.fb) a.push('<a href="' + esc(l.fb) + '" target="_blank" rel="noopener" title="הפרופיל בפייסבוק" aria-label="הפרופיל בפייסבוק">' + ic("facebook") + "</a>");
    if (l.ig) a.push('<a href="https://www.instagram.com/' + esc(l.ig) + '/" target="_blank" rel="noopener" title="@' + esc(l.ig) + '" aria-label="אינסטגרם">' + ic("instagram") + "</a>");
    if (l.phone) { const d = l.phone.replace(/[^0-9+]/g, "").replace(/^\+/, "").replace(/^0/, "972"); a.push('<a href="https://wa.me/' + esc(d) + '" target="_blank" rel="noopener" title="' + esc(l.phone) + '" aria-label="וואטסאפ">' + ic("whatsapp") + "</a>"); }
    if (l.email) a.push('<a href="mailto:' + esc(l.email) + '" title="' + esc(l.email) + '" aria-label="מייל">' + ic("mail") + "</a>");
    return a.length ? '<span class="ct-icons">' + a.join("") + "</span>" : '<span class="lb-muted">אין</span>';
  }
  function select(attrs, opts, val, cls) {
    return '<select class="lb-select' + (cls ? " " + cls : "") + '" ' + attrs + ">" + opts.map(o => '<option value="' + esc(o[0]) + '"' + (String(o[0]) === String(val) ? " selected" : "") + ">" + esc(o[1]) + "</option>").join("") + "</select>";
  }
  function empty(text, icon) { return '<div class="lb-empty"><div class="ct-empty-ic">' + ic(icon || "check-circle") + "</div><p>" + esc(text) + "</p></div>"; }
  function section(title, body, extra) { return '<section class="lb-section"><div class="lb-section-head"><h2>' + title + "</h2>" + (extra || "") + "</div>" + body + "</section>"; }

  // ---- views ---------------------------------------------------------------------------------------------------------------
  function render() {
    if (!active) { navCounts(); return; }
    const page = $("#ctPage"), y = window.scrollY;
    const view = Q && LISTS.indexOf(route) < 0 ? "search" : route;
    const tt = $("#ctTitle"); if (tt) tt.textContent = TITLES[view] || "";
    if (EMB) { if (host().title) host().title(TITLES[view] || "", view); } else document.title = (TITLES[view] || "") + " · קהילות פייסבוק";
    page.innerHTML = view === "home" ? viewHome() : view === "reminders" ? viewReminders() : view === "parents" ? viewGroups("parent")
      : view === "ugc" ? viewGroups("ugc") : view === "posts" ? viewPosts() : view === "leads" ? viewLeads()
      : view === "templates" ? viewTemplates() : view === "method" ? viewMethod() : viewSearch();
    fbLinks(page);
    window.scrollTo(0, y);
    navCounts();
  }
  // redraw this view, the open drawer, and (embedded) the map's reminders stack and counts
  function refresh() { render(); if (drawerGid) renderDrawer(); if (EMB && host().changed) host().changed(); }
  function navCounts() {
    const rem = reminders().filter(r => r.date <= today()).length;
    const inWork = t => allGroups().filter(g => g.track === t && gst(g.id) !== "new").length;
    const set = (k, v, alert) => { const el = $('[data-ctcnt="' + k + '"]'); if (!el) return; el.textContent = v || ""; el.hidden = !v; el.classList.toggle("is-alert", !!alert); };
    set("rem", rem, rem > 0); set("parent", inWork("parent")); set("ugc", inWork("ugc"));
    set("posts", Object.keys(S.posts).length); set("leads", Object.keys(S.leads).length);
    $$("[data-ctroute]").forEach(a => { if (active && a.dataset.ctroute === route) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
  }

  function viewHome() {
    const gs = allGroups(), t = today();
    const work = gs.filter(g => gst(g.id) !== "new" && gst(g.id) !== "no").length;
    const posts = Object.values(S.posts), leads = Object.values(S.leads);
    const sum = k => posts.reduce((s, p) => s + (p[k] || 0), 0);
    const pendingN = posts.filter(p => p.state === "pending").length;
    const done = leads.filter(l => l.status === "done"), doneP = done.filter(l => l.track === "parent").length;
    const rem = reminders(), due = rem.filter(r => r.date <= t), late = rem.filter(r => r.date < t).length;
    const newLeads = leads.filter(l => l.status === "new").length;
    const cubes = '<div class="lb-metrics ct-cubes">'
      + cube("groups", "קבוצות בעבודה", "group", num(work), "מתוך " + num(gs.length))
      + cube("posts", "פוסטים", "send", num(posts.length), pendingN ? num(pendingN) + " מחכים לאישור" : "")
      + cube("comments", "תגובות", "chat", num(sum("comments")), sum("reactions") ? "ועוד " + num(sum("reactions")) + " תגובות רגש" : "")
      + cube("leads", "לידים", "user-plus", num(leads.length), newLeads ? num(newLeads) + " חדשים" : "")
      + cube("", "הגיעו לסוף", "check-circle", num(done.length), done.length ? num(doneP) + " משפחות צולמו · " + num(done.length - doneP) + " יוצרים יצרו תוכן" : "", done.length ? "is-ok" : "")
      + cube("", "תזכורות להיום", "bell", num(due.length), late ? num(late) + " באיחור" : "", due.length ? "is-warn" : "")
      + "</div>";
    const tracks = '<div class="ct-tracks">' + ["parent", "ugc"].map(tr => {
      const tg = gs.filter(g => g.track === tr), tl = leads.filter(l => l.track === tr);
      const gc = count(tg, g => gst(g.id)), lc = count(tl, l => l.status), view = tr === "parent" ? "parents" : "ugc";
      return '<article class="lb-card ct-track"><div class="lb-card-head"><h3><span class="lb-tile ' + (tr === "parent" ? "lb-cat-6" : "lb-cat-5") + '">' + ic(TRACK_ICON[tr]) + "</span>קהילות " + TRACK[tr]
        + ' <span class="lb-count">' + tg.length + '</span></h3><a href="#' + view + '">לכל הקבוצות</a></div>'
        + '<p class="ct-sub">הקבוצות לפי שלב</p>' + pipe(GS, "st-", gc, s => "#" + view + "?st=" + s, true)
        + '<p class="ct-sub">הלידים לפי שלב</p>' + (tl.length ? pipe(LS[tr], "ls-", lc, s => "#leads?track=" + tr + "&st=" + s) : '<p class="ct-hint">עוד אין לידים מהקבוצות האלה.</p>')
        + "</article>";
    }).join("") + "</div>";
    const remList = due.length ? '<ul class="ct-mini">' + due.slice(0, 6).map(remMini).join("") + "</ul>" : '<p class="ct-hint">אין תזכורות להיום.</p>';
    const byLeads = gs.map(g => [g, (IDX.leads[g.id] || []).length]).filter(x => x[1]).sort((a, b) => b[1] - a[1]).slice(0, 6);
    const startHere = gs.filter(g => g.top && gst(g.id) === "new").sort((a, b) => a.top - b.top).slice(0, 6);
    const best = byLeads.length
      ? '<div class="lb-card"><div class="lb-card-head"><h3>הקבוצות שהביאו הכי הרבה לידים</h3><a href="#leads">כל הלידים</a></div><ul class="ct-mini">'
        + byLeads.map(x => '<li><button type="button" class="ct-link ct-mini-t" data-open-g="' + esc(x[0].id) + '" translate="no">' + esc(x[0].name) + '</button><span class="ct-mini-m">' + x[1] + " לידים</span></li>").join("") + "</ul></div>"
      : '<div class="lb-card"><div class="lb-card-head"><h3>להתחיל מכאן</h3><a href="#parents">כל קבוצות ההורים</a></div><p class="ct-hint">הקבוצות הראשונות ב-Top 20 של המחקר שעוד לא התחלנו בהן.</p><ul class="ct-mini">'
        + startHere.map(g => '<li><span class="ct-pri p-' + esc(g.pri) + '">' + g.top + '</span><button type="button" class="ct-link ct-mini-t" data-open-g="' + esc(g.id) + '" translate="no">' + esc(g.name) + '</button><span class="ct-mini-m">' + esc(g.geo) + "</span></li>").join("") + "</ul></div>";
    const recent = posts.length ? Object.keys(S.posts).sort((a, b) => (S.posts[b].on || "").localeCompare(S.posts[a].on || "")).slice(0, 6).map(id => {
      const p = S.posts[id], g = grp(p.gid) || { name: "" };
      return '<li><span class="ct-mini-m">' + fmt(p.on) + '</span><button type="button" class="ct-link ct-mini-t" data-edit-post="' + esc(id) + '" translate="no">' + esc(g.name) + "</button>" + pill("ps-" + p.state, PSL[p.state] || p.state) + "</li>";
    }).join("") : "";
    return '<header class="lb-hero"><h2>קהילות פייסבוק</h2><p class="lb-lede">כל קבוצות ההורים ויוצרי ה-UGC מהמחקר: איפה אנחנו בכל קבוצה, מה פרסמנו ומי ענה.</p></header>'
      + cubes + tracks
      + '<div class="ct-two"><div class="lb-card"><div class="lb-card-head"><h3>צריך אותי היום</h3><a href="#reminders">כל התזכורות</a></div>' + remList + "</div>" + best + "</div>"
      + (recent ? '<div class="lb-card"><div class="lb-card-head"><h3>פוסטים אחרונים</h3><a href="#posts">כל הפוסטים</a></div><ul class="ct-mini">' + recent + "</ul></div>" : "");
  }
  function remMini(r) {
    const cls = r.date < today() ? "ct-late" : "ct-due";
    return '<li><span class="ct-mini-m ' + cls + '">' + rel(r.date) + '</span><button type="button" class="ct-link ct-mini-t" data-open-rem="' + r.k + ":" + esc(r.id) + '"><span translate="no">' + esc(r.title) + "</span>: " + esc(r.text) + "</button></li>";
  }

  function viewReminders() {
    const t = today(), all = reminders(), now = all.filter(r => r.date <= t), soon = all.filter(r => r.date > t);
    const row = r => {
      const icon = r.k === "group" ? "group" : r.k === "lead" ? "user-plus" : "send", cls = r.date < t ? "ct-late" : r.date === t ? "ct-due" : "";
      const key = r.k + ":" + esc(r.id);
      return '<article class="lb-card ct-remi"><span class="lb-tile is-soft ' + (r.track === "ugc" ? "lb-cat-5" : "lb-cat-6") + '">' + ic(icon) + "</span>"
        + '<div class="ct-remi-t"><b><button type="button" class="ct-link" data-open-rem="' + key + '" translate="no">' + esc(r.title) + "</button></b>"
        + "<small>" + esc(r.text) + ' · <span class="' + cls + '">' + rel(r.date) + "</span> · " + fmt(r.date) + " · " + TRACK[r.track || "parent"] + "</small></div>"
        + '<div class="ct-row"><button type="button" class="lb-btn ok sm" data-rem-done="' + key + '">' + ic("check") + (r.k === "post" ? "נבדק" : "בוצע") + "</button>"
        + (r.k === "post" ? '<button type="button" class="lb-btn secondary sm" data-edit-post="' + esc(r.id) + '">' + ic("pencil") + "עדכון המספרים</button>"
          : '<button type="button" class="lb-btn secondary sm" data-rem-snooze="' + key + ':1">מחר</button>'
          + '<button type="button" class="lb-btn secondary sm" data-rem-snooze="' + key + ':3">עוד 3 ימים</button>') + "</div></article>";
    };
    return '<header class="lb-hero"><h2>תזכורות</h2><p class="lb-lede">הצעד הבא של כל קבוצה וליד, ובדיקה של כל פוסט אחרי יומיים ואחרי שבוע.</p></header>'
      + section("להיום ובאיחור <span class=\"lb-count" + (now.length ? " is-alert" : "") + '">' + now.length + "</span>", now.length ? '<div class="ct-rem">' + now.map(row).join("") + "</div>" : empty("אין תזכורות להיום."))
      + section("בשבוע הקרוב <span class=\"lb-count\">" + soon.length + "</span>", soon.length ? '<div class="ct-rem">' + soon.map(row).join("") + "</div>" : '<p class="ct-hint">אין עוד תזכורות השבוע.</p>');
  }

  function groupMatches(g, f, q) {
    const st = gst(g.id);
    if (q && (g.name + " " + g.geo + " " + g.pol + " " + g.notes).toLowerCase().indexOf(q) < 0) return false;
    if (f.pri) { if (g.pri !== f.pri) return false; } else if (!f.rej && g.pri === "Reject" && st === "new") return false;
    if (f.ap && g.ap !== f.ap) return false;
    if (f.band && String(g.band) !== f.band) return false;
    if (f.priv && g.privKey !== f.priv) return false;
    return true;
  }
  function sortGroups(list, how) {
    const rec = (a, b) => (a.top || 99) - (b.top || 99) || PRI[a.pri] - PRI[b.pri] || a.band - b.band || (b.mem || 0) - (a.mem || 0);
    const lc = g => (IDX.leads[g.id] || []).length;
    const up = g => (S.groups[g.id] && S.groups[g.id].updated) || "";
    const by = { rec, near: (a, b) => a.band - b.band || (a.km == null) - (b.km == null) || (a.km || 0) - (b.km || 0) || rec(a, b),
      members: (a, b) => (b.mem || 0) - (a.mem || 0), activity: (a, b) => (b.pm || 0) - (a.pm || 0),
      leads: (a, b) => lc(b) - lc(a) || rec(a, b), updated: (a, b) => up(b).localeCompare(up(a)) || rec(a, b) };
    return list.sort(by[how] || rec);
  }
  function viewGroups(track) {
    const key = track === "parent" ? "parents" : "ugc", f = UI[key], q = Q.toLowerCase();
    const base = allGroups().filter(g => g.track === track && groupMatches(g, f, q));
    const counts = count(base, g => gst(g.id));
    const list = sortGroups(base.filter(g => f.st === "all" || gst(g.id) === f.st), f.sort);
    const chips = '<div class="ct-chips" role="group" aria-label="סינון לפי שלב"><button type="button" class="ct-chip" data-f="' + key + ':st:all" aria-pressed="' + (f.st === "all") + '">הכול <b>' + base.length + "</b></button>"
      + GS.map(s => '<button type="button" class="ct-chip st-' + s[0] + '" data-f="' + key + ":st:" + s[0] + '" aria-pressed="' + (f.st === s[0]) + '">' + esc(s[1]) + " <b>" + (counts[s[0]] || 0) + "</b></button>").join("") + "</div>";
    const row = '<div class="ct-row">'
      + select('data-fs="' + key + ':pri" aria-label="דירוג במחקר"', [["", "כל הדירוגים"], ["A", "דירוג A"], ["B", "דירוג B"], ["C", "דירוג C"], ["Reject", "נפסלו במחקר"]], f.pri)
      + select('data-fs="' + key + ':ap" aria-label="גישה"', [["", "כל הגישות"]].concat(AP), f.ap)
      + (track === "parent" ? select('data-fs="' + key + ':band" aria-label="מרחק מאשקלון"', [["", "כל המרחקים"]].concat(BANDS), f.band) : "")
      + select('data-fs="' + key + ':priv" aria-label="ציבורית או פרטית"', [["", "ציבורית ופרטית"], ["Public", "ציבורית"], ["Private", "פרטית"]], f.priv)
      + select('data-fs="' + key + ':sort" aria-label="מיון"', [["rec", "מיון: מומלץ"], ["near", "מהקרובה לרחוקה"], ["members", "הכי הרבה חברים"], ["activity", "הכי פעילה"], ["leads", "הכי הרבה לידים"], ["updated", "עודכנה לאחרונה"]], f.sort)
      + '<label class="lb-check"><input type="checkbox" data-fc="' + key + ':rej"' + (f.rej ? " checked" : "") + "> גם קבוצות שנפסלו במחקר</label>"
      + '<span class="lb-spacer"></span><button type="button" class="lb-btn secondary sm" data-add-group="' + track + '">' + ic("plus") + "קבוצה שלא במחקר</button></div>";
    const shown = list.slice(0, f.n);
    const cards = shown.length ? '<div class="ct-list">' + shown.map(groupCard).join("") + "</div>" : empty("אין קבוצה שמתאימה לסינון.", "search");
    const more = list.length > shown.length ? '<button type="button" class="lb-btn secondary ct-more" data-more="' + key + '">עוד ' + Math.min(30, list.length - shown.length) + " קבוצות</button>" : "";
    const lede = track === "parent"
      ? "קבוצות אמהות והורים ליום צילום בבית תמורת ספר. מסודרות לפי ה-Top 20 של המחקר, הדירוג והמרחק מאשקלון."
      : "קבוצות של יוצרי תוכן ו-UGC למציאת יוצרים. לפי המחקר יש ביניהן קבוצות שלא מאשרות ברטר או גובות על פוסט, אז כדאי לקרוא את הכללים ולפנות קודם למנהלים.";
    return '<header class="lb-hero"><h2>קהילות ' + TRACK[track] + '</h2><p class="lb-lede">' + lede + "</p></header>"
      + '<div class="ct-filters">' + chips + row + '<span class="ct-count">מציג ' + shown.length + " מתוך " + list.length + "</span></div>" + cards + more;
  }
  function groupCard(g) {
    const d = S.groups[g.id] || {}, st = d.status || "new", pc = (IDX.posts[g.id] || []).length, lc = (IDX.leads[g.id] || []).length;
    const facts = [];
    if (g.geo) facts.push("<span>" + ic("pin") + esc(g.geo) + (g.km != null && g.band > 1 && g.band < 6 ? " · " + km(g) : "") + "</span>");
    if (g.mem != null) facts.push("<span>" + ic("people") + "<b>" + num(g.mem) + "</b> חברים</span>");
    if (g.pm != null) facts.push("<span>" + ic("chat") + "<b>" + num(g.pm) + "</b> פוסטים בחודש</span>");
    if (g.priv) facts.push("<span>" + ic(g.privKey === "Private" ? "eye" : "globe") + esc(g.priv) + "</span>");
    if (g.top) facts.push('<span class="lb-chip success">מקום ' + g.top + " ב-Top 20</span>");
    if (g.custom) facts.push('<span class="lb-chip outline">נוספה ידנית</span>');
    return '<article class="lb-card ct-gc"><div class="ct-gc-top"><span class="ct-pri p-' + esc(g.pri || "x") + '" title="דירוג במחקר">' + esc(g.pri === "Reject" ? "נפסלה" : g.pri || "·") + "</span>"
      + '<div class="ct-gc-name"><button type="button" data-open-g="' + esc(g.id) + '" translate="no">' + esc(g.name) + '</button><div class="ct-facts">' + facts.join("") + "</div></div>"
      + pill("st-" + st, GSL[st], 'data-gstatus="' + esc(g.id) + '" aria-haspopup="menu" aria-label="שלב: ' + esc(GSL[st]) + '"') + "</div>"
      + (g.pol ? '<p class="ct-pol lb-clamp-2"><b>כללים:</b> ' + esc(g.pol) + "</p>" : "")
      + '<div class="ct-gc-foot">' + (g.apHe ? '<span class="lb-chip ' + (AP_CHIP[g.ap] || "") + '">' + esc(g.apHe) + "</span>" : "") + nextHtml(d.next_on, d.next_note)
      + '<span class="lb-spacer"></span><span class="ct-tally"><span><b>' + pc + "</b> פוסטים</span><span><b>" + lc + "</b> לידים</span></span>"
      + (g.url ? '<a class="lb-btn ghost sm icon" href="' + esc(g.url) + '" target="_blank" rel="noopener" aria-label="לקבוצה בפייסבוק" title="לקבוצה בפייסבוק">' + ic("facebook") + "</a>" : "")
      + '<button type="button" class="lb-btn secondary sm" data-add-post="' + esc(g.id) + '">' + ic("send") + "פוסט</button>"
      + '<button type="button" class="lb-btn secondary sm" data-add-lead="' + esc(g.id) + '">' + ic("user-plus") + "ליד</button></div></article>";
  }

  function viewPosts() {
    const f = UI.posts, q = Q.toLowerCase();
    const ids = Object.keys(S.posts).filter(id => {
      const p = S.posts[id], g = grp(p.gid);
      if (!g) return false;
      if (f.track !== "all" && g.track !== f.track) return false;
      if (q && (g.name + " " + (p.note || "") + " " + (p.template || "")).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
    const sc = count(ids, id => S.posts[id].state), shown = ids.filter(id => f.st === "all" || S.posts[id].state === f.st)
      .sort((a, b) => (S.posts[b].on || "").localeCompare(S.posts[a].on || ""));
    const sum = k => ids.reduce((s, id) => s + (S.posts[id][k] || 0), 0);
    const fromPosts = ids.reduce((s, id) => s + (IDX.leadsByPost[id] || []).length, 0);
    const cubes = '<div class="lb-metrics ct-cubes">' + cube("posts", "פוסטים", "send", num(ids.length), sc.pending ? num(sc.pending) + " מחכים לאישור" : "")
      + cube("reactions", "תגובות רגש", "heart", num(sum("reactions"))) + cube("comments", "תגובות", "chat", num(sum("comments")))
      + cube("leads", "לידים מהפוסטים", "user-plus", num(fromPosts)) + "</div>";
    const seg = '<span class="lb-segmented" role="group" aria-label="מסלול">' + [["all", "הכול"], ["parent", "הורים"], ["ugc", "יוצרי UGC"]].map(x => '<button type="button" data-f="posts:track:' + x[0] + '" aria-pressed="' + (f.track === x[0]) + '">' + x[1] + "</button>").join("") + "</span>";
    const chips = '<div class="ct-chips"><button type="button" class="ct-chip" data-f="posts:st:all" aria-pressed="' + (f.st === "all") + '">הכול <b>' + ids.length + "</b></button>"
      + PS.map(s => '<button type="button" class="ct-chip ps-' + s[0] + '" data-f="posts:st:' + s[0] + '" aria-pressed="' + (f.st === s[0]) + '">' + s[1] + " <b>" + (sc[s[0]] || 0) + "</b></button>").join("") + "</div>";
    const rows = shown.map(id => {
      const p = S.posts[id], g = grp(p.gid), lc = (IDX.leadsByPost[id] || []).length, due = postDue(p);
      const n = k => '<input class="lb-input ct-num" type="number" min="0" inputmode="numeric" data-pnum="' + esc(id) + ":" + k + '" value="' + (p[k] == null ? "" : p[k]) + '" aria-label="' + (k === "reactions" ? "תגובות רגש" : k === "comments" ? "תגובות" : "שיתופים") + '">';
      return "<tr><td>" + fmt(p.on) + (due && due.date <= today() ? '<br><button type="button" class="ct-link lb-small" data-checked="' + esc(id) + '">סימון שנבדק היום</button>' : "") + "</td>"
        + '<td class="ct-grp"><button type="button" class="ct-link" data-open-g="' + esc(p.gid) + '" translate="no">' + esc(g.name) + "</button></td><td>" + TRACK[g.track] + "</td>"
        + "<td>" + esc(p.template || "") + "</td><td>" + select('data-pstate="' + esc(id) + '" aria-label="מצב"', PS, p.state) + "</td>"
        + "<td>" + n("reactions") + "</td><td>" + n("comments") + "</td><td>" + n("shares") + "</td>"
        + '<td><button type="button" class="ct-link" data-add-lead="' + esc(p.gid) + '" data-pid="' + esc(id) + '" title="ליד חדש מהפוסט">' + lc + " +</button></td>"
        + '<td><span class="ct-icons">' + (p.url ? '<a href="' + esc(p.url) + '" target="_blank" rel="noopener" aria-label="לפוסט" title="לפוסט">' + ic("open-out") + "</a>" : "")
        + '<a href="#" data-edit-post="' + esc(id) + '" aria-label="עריכה" title="עריכה">' + ic("pencil") + "</a></span></td></tr>";
    }).join("");
    const table = shown.length ? '<div class="lb-table-wrap"><table class="lb-table ct-table"><thead><tr><th>תאריך</th><th>קבוצה</th><th>מסלול</th><th>נוסח</th><th>מצב</th><th>רגש</th><th>תגובות</th><th>שיתופים</th><th>לידים</th><th></th></tr></thead><tbody>' + rows + "</tbody></table></div>"
      : empty(ids.length ? "אין פוסט שמתאים לסינון." : "עוד לא נרשמו פוסטים. פוסט נרשם מהכרטיס של הקבוצה או מהכפתור פוסט למעלה.", "send");
    return '<header class="lb-hero"><h2>פוסטים</h2><p class="lb-lede">כל פוסט שעלה בקבוצה: מתי, איזה נוסח, כמה תגובות ומי ענה. את המספרים מקלידים מהפוסט בפייסבוק.</p></header>'
      + cubes + '<div class="ct-filters"><div class="ct-row">' + seg + "</div>" + chips + "</div>" + table;
  }

  function viewLeads() {
    const f = UI.leads, q = Q.toLowerCase();
    const ids = Object.keys(S.leads).filter(id => {
      const l = S.leads[id], g = grp(l.gid) || { name: "" };
      if (f.track !== "all" && l.track !== f.track) return false;
      if (q && (l.name + " " + l.city + " " + l.note + " " + l.ig + " " + l.kids + " " + g.name).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
    const sc = count(ids, id => S.leads[id].status), labels = LS[f.track] || LS.all;
    const shown = ids.filter(id => f.st === "all" || S.leads[id].status === f.st)
      .sort((a, b) => (S.leads[b].on || S.leads[b].created || "").localeCompare(S.leads[a].on || S.leads[a].created || ""));
    const open = ids.filter(id => ["contacted", "replied", "qualified", "booked"].indexOf(S.leads[id].status) >= 0).length;
    const cubes = '<div class="lb-metrics ct-cubes">' + cube("leads", "לידים", "user-plus", num(ids.length), sc.new ? num(sc.new) + " חדשים" : "")
      + cube("", "בתהליך", "chat", num(open), "", open ? "is-warn" : "")
      + cube("", "הגיעו לסוף", "check-circle", num(sc.done || 0), "", sc.done ? "is-ok" : "") + "</div>";
    const seg = '<span class="lb-segmented" role="group" aria-label="מסלול">' + [["all", "הכול"], ["parent", "הורים"], ["ugc", "יוצרי UGC"]].map(x => '<button type="button" data-f="leads:track:' + x[0] + '" aria-pressed="' + (f.track === x[0]) + '">' + x[1] + "</button>").join("") + "</span>";
    const chips = '<div class="ct-chips"><button type="button" class="ct-chip" data-f="leads:st:all" aria-pressed="' + (f.st === "all") + '">הכול <b>' + ids.length + "</b></button>"
      + labels.map(s => '<button type="button" class="ct-chip ls-' + s[0] + '" data-f="leads:st:' + s[0] + '" aria-pressed="' + (f.st === s[0]) + '">' + esc(s[1]) + " <b>" + (sc[s[0]] || 0) + "</b></button>").join("") + "</div>";
    const rows = shown.map(id => {
      const l = S.leads[id], g = grp(l.gid) || { name: "" }, inMap = l.ig && CREATORS.has(l.ig.toLowerCase());
      return '<tr><td class="ct-name"><button type="button" class="ct-link" data-edit-lead="' + esc(id) + '" translate="no">' + esc(l.name) + "</button>"
        + (inMap ? ' <a class="lb-chip tint" href="' + esc(META.creator_map) + '" data-cre="' + esc(l.ig.toLowerCase()) + '" title="היוצר כבר במפת היוצרים">במפת היוצרים</a>' : "") + "</td>"
        + "<td>" + TRACK[l.track] + '</td><td class="ct-grp"><button type="button" class="ct-link" data-open-g="' + esc(l.gid) + '" translate="no">' + esc(g.name) + "</button></td>"
        + "<td>" + esc(CHL[l.channel] || "") + "</td><td>" + select('data-lstatus="' + esc(id) + '" aria-label="שלב"', LS[l.track], l.status) + "</td>"
        + "<td>" + (l.next_on && l.status !== "done" && l.status !== "no" ? nextHtml(l.next_on, l.next_note) : '<span class="lb-muted">אין</span>') + "</td>"
        + "<td>" + contactIcons(l) + "</td><td>" + fmt(l.on || (l.created || "").slice(0, 10)) + "</td></tr>";
    }).join("");
    const table = shown.length ? '<div class="lb-table-wrap"><table class="lb-table ct-table"><thead><tr><th>שם</th><th>מסלול</th><th>קבוצה</th><th>ערוץ</th><th>שלב</th><th>הצעד הבא</th><th>קשר</th><th>נכנס</th></tr></thead><tbody>' + rows + "</tbody></table></div>"
      : empty(ids.length ? "אין ליד שמתאים לסינון." : "עוד אין לידים. ליד נרשם מהכרטיס של הקבוצה, מפוסט או מהכפתור ליד למעלה.", "user-plus");
    return '<header class="lb-hero"><h2>לידים</h2><p class="lb-lede">כל מי שענה לפוסט או כתב בפרטי: משפחות ליום צילום ויוצרים לשיתוף פעולה. נשמר רק על המחשב הזה.</p></header>'
      + cubes + '<div class="ct-filters"><div class="ct-row">' + seg + "</div>" + chips + "</div>" + table;
  }

  function viewTemplates() {
    const custom = !!(S.settings.main && S.settings.main.templates);
    const col = track => '<div class="ct-tcol"><h3>' + ic(TRACK_ICON[track]) + " קהילות " + TRACK[track] + "</h3>" + templates(track).map((t, i) =>
      '<article class="lb-card ct-tcard"><div class="ct-row"><input class="lb-input" dir="rtl" data-tf="' + track + ":" + i + ':title" value="' + esc(t.title) + '" aria-label="שם הנוסח">'
      + '<button type="button" class="lb-btn secondary sm" data-copy-tpl="' + track + ":" + esc(t.id) + '">' + ic("copy") + "העתקה</button>"
      + '<button type="button" class="lb-btn ghost sm icon" data-del-tpl="' + track + ":" + i + '" aria-label="מחיקת הנוסח" title="מחיקת הנוסח">' + ic("close") + "</button></div>"
      + '<textarea class="lb-textarea" dir="rtl" data-tf="' + track + ":" + i + ':text" aria-label="הנוסח">' + esc(t.text) + "</textarea></article>").join("")
      + '<button type="button" class="lb-btn secondary" data-new-tpl="' + track + '">' + ic("plus") + "נוסח חדש</button></div>";
    return '<header class="lb-hero"><h2>נוסחים להעתקה</h2><p class="lb-lede">הפוסטים וההודעות לכל מסלול. השינויים נשמרים לבד. בהעתקה מהכרטיס של קבוצה [העיר] מתחלף בעיר שלה, ובהעתקה מליד [שם] מתחלף בשם הפרטי.</p>'
      + (custom ? '<button type="button" class="ct-link lb-small" data-reset-tpl>חזרה לנוסחים המקוריים</button>' : "") + "</header>"
      + '<div class="ct-two">' + col("parent") + col("ugc") + "</div>";
  }

  function viewMethod() {
    return '<header class="lb-hero"><h2>מאיפה הקבוצות</h2></header><div class="lb-card lb-prose">'
      + "<h3>הקבוצות</h3><p>" + num(META.parent + META.ugc) + " קבוצות פייסבוק ממפת קהילות ההורים: " + num(META.parent) + " קבוצות הורים ו-" + num(META.ugc)
      + " קבוצות יוצרי תוכן ו-UGC. כל קבוצה נבדקה בדף ה-About שלה ב-" + fmt(META.checked) + ": חברים, פעילות, כללי פרסום ומנהלים. קבוצות הוואטסאפ, הטלגרם ועמודי הפייסבוק נשארו בדף המחקר, "
      + '<a href="' + esc(META.research) + '">מפת קהילות ההורים</a>.</p>'
      + "<h3>הדירוג והגישה</h3><p>A, B ו-C הם הדירוג של המחקר, והקבוצות שנפסלו בו מוסתרות עד שמסמנים להציג אותן. הגישה (לפרסם ישירות, לפנות קודם למנהלים, פוסט בתשלום) נקבעה לפי הכללים בדף ה-About. המרחק הוא בקו אווירי מאשקלון, בלי זמן נסיעה. הכללים תורגמו לעברית מהמחקר, והמקור באנגלית מופיע בכרטיס של הקבוצה.</p>"
      + "<h3>מה נשמר ואיפה</h3><p>השלבים, הפוסטים, הלידים והנוסחים נשמרים בשרת הפרויקט על המחשב הזה, בקובץ creators/community-tracker/state/tracker.json. הקובץ לא נכנס לגיט כי יש בו שמות וטלפונים של הורים, ובכל יום נשמר עותק בתיקייה state/backup. כשהדף פתוח בכתובת אחרת, העבודה נשמרת רק בדפדפן.</p>"
      + "<h3>תזכורות</h3><p>כל שינוי שלב קובע צעד הבא: 3 ימים אחרי בקשת הצטרפות או פנייה למנהלים, יומיים אחרי פנייה לליד. פוסט שעלה מקבל בדיקה של תגובות ולידים אחרי יומיים ואחרי שבוע. אפשר לשנות כל תאריך ביד.</p>"
      + "<h3>פרטיות</h3><p>רושמים רק מה שהאדם כתב או שלח. בפוסטים מבקשים לא לכתוב פרטים על ילדים בתגובות, ואת הפרטים של המשפחות אוספים בטופס.</p></div>";
  }

  function viewSearch() {
    const q = Q.toLowerCase();
    const gs = sortGroups(allGroups().filter(g => (g.name + " " + g.geo + " " + g.pol).toLowerCase().indexOf(q) >= 0), "rec");
    const ls = Object.keys(S.leads).filter(id => { const l = S.leads[id]; return (l.name + " " + l.city + " " + l.ig + " " + l.note).toLowerCase().indexOf(q) >= 0; });
    return section("קבוצות <span class=\"lb-count\">" + gs.length + "</span>", gs.length ? '<div class="ct-list">' + gs.slice(0, 30).map(groupCard).join("") + "</div>" : '<p class="ct-hint">אין קבוצה כזאת.</p>')
      + section("לידים <span class=\"lb-count\">" + ls.length + "</span>", ls.length ? '<ul class="ct-mini">' + ls.map(id => '<li><button type="button" class="ct-link ct-mini-t" data-edit-lead="' + esc(id) + '" translate="no">' + esc(S.leads[id].name) + "</button>" + pill("ls-" + S.leads[id].status, lsl(S.leads[id].track, S.leads[id].status)) + "</li>").join("") + "</ul>" : '<p class="ct-hint">אין ליד כזה.</p>');
  }

  // ---- the group drawer ----------------------------------------------------------------------------------------------------
  function openGroup(id) {
    if (!grp(id)) return;
    drawerGid = id; renderDrawer();
    const d = $("#ctDrawer"); d.hidden = false; $("#ctDScrim").hidden = false;
    $("#ctDrawerX").focus();
  }
  function closeDrawer() { drawerGid = null; $("#ctDrawer").hidden = true; $("#ctDScrim").hidden = true; }
  function renderDrawer() {
    const g = grp(drawerGid); if (!g) { closeDrawer(); return; }
    const d = gdoc(g.id), body = $("#ctDrawerB");
    $("#ctDrawerT").textContent = g.name;
    const posts = (IDX.posts[g.id] || []), leads = (IDX.leads[g.id] || []);
    const kv = (k, v) => v ? "<dt>" + k + "</dt><dd>" + v + "</dd>" : "";
    const links = '<div class="ct-row">' + (g.url ? '<a class="lb-btn secondary sm" href="' + esc(g.url) + '" target="_blank" rel="noopener">' + ic("facebook") + "לקבוצה" + ic("open-out") + "</a>" : "")
      + (g.about ? '<a class="lb-btn secondary sm" href="' + esc(g.about) + '" target="_blank" rel="noopener">' + ic("info") + "דף ה-About" + ic("open-out") + "</a>" : "") + "</div>";
    const html = []
      .concat('<div class="ct-dsec"><div class="ct-row">' + select('data-gf="status" aria-label="שלב"', GS, d.status) + (g.apHe ? '<span class="lb-chip ' + (AP_CHIP[g.ap] || "") + '">' + esc(g.apHe) + "</span>" : "") + "</div>" + links + "</div>")
      .concat(g.top ? '<p class="ct-why"><b>מקום ' + g.top + " ב-Top 20 של המחקר.</b> " + esc(g.why || "") + "</p>" : "")
      .concat('<div class="ct-dsec"><h3>' + ic("clock") + "הצעד הבא</h3><div class=\"ct-grid2\">"
        + '<label class="lb-field">תאריך<input class="lb-input" type="date" data-gf="next_on" value="' + esc(d.next_on) + '"></label>'
        + '<label class="lb-field">מה לעשות<input class="lb-input" dir="rtl" data-gf="next_note" value="' + esc(d.next_note) + '" maxlength="300"></label></div>'
        + (d.next_on ? '<div class="ct-row"><button type="button" class="lb-btn ok sm" data-rem-done="group:' + esc(g.id) + '">' + ic("check") + "בוצע</button></div>" : "") + "</div>")
      .concat('<div class="ct-dsec"><h3>' + ic("calendar") + "תאריכים</h3><div class=\"ct-grid2\">"
        + '<label class="lb-field">הצטרפנו לקבוצה<input class="lb-input" type="date" data-gf="joined_on" value="' + esc(d.joined_on) + '"></label>'
        + '<label class="lb-field">פנינו למנהלים<input class="lb-input" type="date" data-gf="asked_on" value="' + esc(d.asked_on) + '"></label>'
        + '<label class="lb-field">אישרו לפרסם<input class="lb-input" type="date" data-gf="ok_on" value="' + esc(d.ok_on) + '"></label>'
        + '<label class="lb-field">ימים שמותר לפרסם<input class="lb-input" dir="rtl" data-gf="post_day" value="' + esc(d.post_day) + '" placeholder="למשל ראשון וחמישי" maxlength="120"></label></div></div>')
      .concat('<div class="ct-dsec"><h3>' + ic("send") + 'פוסטים בקבוצה <span class="lb-count">' + posts.length + '</span><span class="lb-spacer"></span><button type="button" class="lb-btn secondary sm" data-add-post="' + esc(g.id) + '">' + ic("plus") + "פוסט</button></h3>"
        + (posts.length ? '<ul class="ct-mini">' + posts.map(pid => { const p = S.posts[pid]; return '<li><span class="ct-mini-m">' + fmt(p.on) + '</span><button type="button" class="ct-link ct-mini-t" data-edit-post="' + esc(pid) + '">' + esc(p.template || "פוסט") + "</button>"
          + '<span class="ct-mini-m">' + (p.reactions != null ? num(p.reactions) + " רגש · " : "") + (p.comments != null ? num(p.comments) + " תגובות · " : "") + (IDX.leadsByPost[pid] || []).length + " לידים</span>" + pill("ps-" + p.state, PSL[p.state]) + "</li>"; }).join("") + "</ul>" : '<p class="ct-hint">עוד לא פרסמנו כאן.</p>') + "</div>")
      .concat('<div class="ct-dsec"><h3>' + ic("user-plus") + 'לידים מהקבוצה <span class="lb-count">' + leads.length + '</span><span class="lb-spacer"></span><button type="button" class="lb-btn secondary sm" data-add-lead="' + esc(g.id) + '">' + ic("plus") + "ליד</button></h3>"
        + (leads.length ? '<ul class="ct-mini">' + leads.map(lid => { const l = S.leads[lid]; return '<li><button type="button" class="ct-link ct-mini-t" data-edit-lead="' + esc(lid) + '" translate="no">' + esc(l.name) + '</button><span class="ct-mini-m">' + esc(CHL[l.channel] || "") + "</span>" + pill("ls-" + l.status, lsl(l.track, l.status)) + "</li>"; }).join("") + "</ul>" : '<p class="ct-hint">עוד אין לידים מכאן.</p>') + "</div>")
      .concat('<div class="ct-dsec"><h3>' + ic("copy") + "נוסחים להעתקה</h3><div class=\"ct-tpls\">" + templates(g.track).map(t => '<button type="button" class="lb-btn secondary sm" data-copy-tpl="' + g.track + ":" + esc(t.id) + '" data-gid="' + esc(g.id) + '">' + ic("copy") + esc(t.title) + "</button>").join("") + "</div></div>")
      .concat(g.custom ? '<div class="ct-dsec"><h3>' + ic("pencil") + "פרטי הקבוצה</h3><div class=\"ct-grid2\">"
        + '<label class="lb-field is-wide">שם<input class="lb-input" dir="rtl" data-gc="name" value="' + esc(g.name) + '" maxlength="200"></label>'
        + '<label class="lb-field is-wide">קישור<input class="lb-input" dir="ltr" data-gc="url" value="' + esc(g.url) + '" placeholder="https://www.facebook.com/groups/..."></label>'
        + '<label class="lb-field">עיר או אזור<input class="lb-input" dir="rtl" data-gc="geo" value="' + esc(g.geo) + '"></label>'
        + '<label class="lb-field">חברים<input class="lb-input" type="number" min="0" data-gc="members_n" value="' + (g.mem == null ? "" : g.mem) + '"></label>'
        + '<label class="lb-field is-wide">כללי פרסום<textarea class="lb-textarea" dir="rtl" data-gc="policy">' + esc(g.pol) + "</textarea></label></div>"
        + '<div class="ct-row"><button type="button" class="lb-btn ghost sm" data-del-group="' + esc(g.id) + '">' + ic("close") + "הסרת הקבוצה</button></div></div>" : "")
      .concat(!g.custom ? '<div class="ct-dsec"><h3>' + ic("info") + "מהמחקר</h3><dl class=\"lb-kv\">"
        + kv("חברים", g.mem != null ? num(g.mem) : "") + kv("פוסטים בחודש", g.pm != null ? num(g.pm) : "") + kv("מרחק", esc(g.geo) + (g.band > 1 && g.band < 6 ? " · " + km(g) : ""))
        + kv("ציבורית או פרטית", esc(g.priv)) + kv("אישור מנהלים", esc(g.appr)) + kv("כללי פרסום", esc(g.pol) + (g.polEn && g.polEn !== g.pol ? '<div class="ct-en" lang="en">' + esc(g.polEn) + "</div>" : ""))
        + kv("דרך פנייה", esc(g.contact)) + kv("הערות", esc(g.notes)) + kv("קהל", esc((g.seg || []).join(", "))) + kv("שפה", esc(g.lang)) + kv("ביטחון בבדיקה", esc(g.conf)) + kv("נבדקה", fmt(g.checked))
        + "</dl></div>" : "")
      .concat('<div class="ct-dsec"><h3>' + ic("chat") + "הערות</h3>"
        + '<form class="ct-addnote" data-addnote><input class="lb-input" dir="rtl" name="t" placeholder="הערה חדשה" maxlength="2000" autocomplete="off"><button class="lb-btn secondary sm" type="submit">הוספה</button></form>'
        + (d.notes.length ? '<ul class="ct-notes">' + d.notes.slice().reverse().map(n => "<li><time>" + fmt(n.at) + "</time>" + esc(n.t) + "</li>").join("") + "</ul>" : "") + "</div>");
    body.innerHTML = html.join("");
  }
  function saveGroupField(field, value) {
    const id = drawerGid, d = gdoc(id);
    if (field === "status") return setGroupStatus(id, value);
    d[field] = value;
    return putR("groups", id, d);
  }
  function saveCustomField(field, value) {
    const id = drawerGid, d = gdoc(id);
    d.custom = Object.assign({}, d.custom, { [field]: field === "members_n" ? (value === "" ? null : Number(value)) : value });
    return putR("groups", id, d);
  }

  // ---- status popover --------------------------------------------------------------------------------------------------------
  function statusMenu(btn, id) {
    const pop = $("#ctPop"), st = gst(id);
    pop.innerHTML = '<p class="lb-popover-label">השלב בקבוצה</p>' + GS.map(s => '<button type="button" role="menuitemradio" aria-checked="' + (s[0] === st) + '" data-set-gst="' + esc(id) + ":" + s[0] + '"' + (s[0] === st ? ' aria-current="true"' : "") + ">" + pill("st-" + s[0], s[1]) + "</button>").join("");
    pop.hidden = false;
    const r = btn.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
    let left = getComputedStyle(btn).direction === "rtl" ? r.right - w : r.left;
    left = Math.max(8, Math.min(left, window.innerWidth - w - 8));
    let top = r.bottom + 6; if (top + h > window.innerHeight - 8) top = Math.max(8, r.top - h - 6);
    pop.style.left = left + "px"; pop.style.top = top + "px";
    const first = pop.querySelector('[aria-checked="true"]') || pop.querySelector("button"); if (first) first.focus();
  }
  function closePop() { $("#ctPop").hidden = true; }

  // ---- the add and edit dialog ----------------------------------------------------------------------------------------------
  const dlg = $("#ctDlg"), form = $("#ctForm");
  let dlgCtx = null;
  function openDlg(title, html, ctx) {
    dlgCtx = ctx; $("#ctDlgT").textContent = title; form.innerHTML = html;
    if (!dlg.open) dlg.showModal();
    const f = form.querySelector("[autofocus]") || form.querySelector("input:not([type=hidden]),select,textarea"); if (f) f.focus();
  }
  function groupPicker(gid, fixed) {
    const g = gid && grp(gid);
    if (g) return '<div class="lb-field">קבוצה<div class="ct-picked"><b translate="no">' + esc(g.name) + "</b><span class=\"lb-muted\">" + TRACK[g.track] + "</span>"
      + (fixed ? "" : '<button type="button" class="ct-link" data-pick-clear>החלפה</button>') + '</div><input type="hidden" name="gid" value="' + esc(g.id) + '"></div>';
    return '<div class="lb-field ct-combo">קבוצה<input class="lb-input" dir="rtl" data-combo placeholder="שם הקבוצה או העיר" autocomplete="off" autofocus aria-autocomplete="list"><ul class="ct-combo-list" hidden></ul><input type="hidden" name="gid" value=""></div>';
  }
  function comboResults(q) {
    q = q.trim().toLowerCase();
    const list = allGroups().filter(g => !q || (g.name + " " + g.geo).toLowerCase().indexOf(q) >= 0);
    list.sort((a, b) => ((gst(b.id) !== "new") - (gst(a.id) !== "new")) || (a.top || 99) - (b.top || 99) || PRI[a.pri] - PRI[b.pri] || a.band - b.band);
    return list.slice(0, 8);
  }
  function postForm(pid, gid) {
    const p = pid ? S.posts[pid] : { gid, on: today(), state: "live" }, g = grp(p.gid);
    const tpls = g ? templates(g.track).filter(t => t.kind === "post" || !t.kind) : [];
    const tplOpts = [["", "בלי נוסח מסוים"]].concat(tpls.map(t => [t.title, t.title]));
    if (p.template && !tplOpts.some(o => o[0] === p.template)) tplOpts.push([p.template, p.template]);
    const n = (k, l) => '<label class="lb-field">' + l + '<input class="lb-input" type="number" min="0" inputmode="numeric" name="' + k + '" value="' + (p[k] == null ? "" : p[k]) + '"></label>';
    return groupPicker(p.gid, !!pid)
      + '<div class="ct-grid2"><label class="lb-field">תאריך<input class="lb-input" type="date" name="on" value="' + esc(p.on || today()) + '" required></label>'
      + '<label class="lb-field">מצב' + select('name="state"', PS, p.state) + "</label>"
      + '<label class="lb-field is-wide">קישור לפוסט<input class="lb-input" dir="ltr" name="url" value="' + esc(p.url || "") + '" placeholder="https://www.facebook.com/groups/.../posts/..."></label>'
      + '<label class="lb-field is-wide">נוסח' + select('name="template"', tplOpts, p.template || "") + "</label>"
      + n("reactions", "תגובות רגש") + n("comments", "תגובות") + n("shares", "שיתופים")
      + '<label class="lb-field">נבדק לאחרונה<input class="lb-input" type="date" name="checked_on" value="' + esc(p.checked_on || "") + '"></label>'
      + '<label class="lb-field is-wide">הערה<textarea class="lb-textarea" dir="rtl" name="note" maxlength="2000">' + esc(p.note || "") + "</textarea></label></div>"
      + '<p class="lb-form-error" hidden></p><div class="lb-form-actions"><button class="lb-btn" type="submit">' + ic("check") + "שמירה</button>"
      + '<button class="lb-btn secondary" type="button" data-dlg-close>ביטול</button>'
      + (pid ? '<span class="lb-spacer"></span><button class="lb-btn ghost" type="button" data-del-post="' + esc(pid) + '">' + ic("close") + "מחיקת הפוסט</button>" : "") + "</div>";
  }
  function leadForm(lid, gid, pid) {
    const l = lid ? S.leads[lid] : { gid, pid: pid || "", status: "new", channel: pid ? "comment" : "dm", on: today() };
    const g = grp(l.gid), track = g ? g.track : "parent";
    const posts = g ? (IDX.posts[g.id] || []) : [];
    const postOpts = [["", "בלי פוסט מסוים"]].concat(posts.map(id => [id, (S.posts[id].on ? S.posts[id].on.split("-").reverse().join(" / ") + " · " : "") + (S.posts[id].template || "פוסט")]));
    const inMap = l.ig && CREATORS.has(String(l.ig).toLowerCase());
    return groupPicker(l.gid, !!lid)
      + '<div class="ct-grid2"><label class="lb-field is-wide">שם<input class="lb-input" dir="rtl" name="name" value="' + esc(l.name || "") + '" required maxlength="120" translate="no"' + (g ? " autofocus" : "") + "></label>"
      + '<label class="lb-field">מאיזה פוסט' + select('name="pid"', postOpts, l.pid || "") + "</label>"
      + '<label class="lb-field">ערוץ' + select('name="channel"', CH, l.channel) + "</label>"
      + '<label class="lb-field">שלב' + select('name="status"', LS[track], l.status) + "</label>"
      + '<label class="lb-field">נכנס ב-<input class="lb-input" type="date" name="on" value="' + esc(l.on || "") + '"></label>'
      + '<label class="lb-field is-wide">פרופיל בפייסבוק<input class="lb-input" dir="ltr" name="fb" value="' + esc(l.fb || "") + '" placeholder="https://www.facebook.com/..."></label>'
      + '<label class="lb-field">אינסטגרם<input class="lb-input" dir="ltr" name="ig" value="' + esc(l.ig || "") + '" placeholder="handle">' + (inMap ? '<span class="lb-chip tint">כבר במפת היוצרים</span>' : "") + "</label>"
      + '<label class="lb-field">טלפון<input class="lb-input" dir="ltr" type="tel" name="phone" value="' + esc(l.phone || "") + '"></label>'
      + '<label class="lb-field">מייל<input class="lb-input" dir="ltr" type="email" name="email" value="' + esc(l.email || "") + '"></label>'
      + '<label class="lb-field">עיר<input class="lb-input" dir="rtl" name="city" value="' + esc(l.city || "") + '"></label>'
      + '<label class="lb-field is-wide">' + (track === "ugc" ? "עוקבים ונישה" : "ילדים וגילים") + '<input class="lb-input" dir="rtl" name="kids" value="' + esc(l.kids || "") + '" maxlength="300"></label>'
      + '<label class="lb-field">הצעד הבא<input class="lb-input" type="date" name="next_on" value="' + esc(l.next_on || "") + '"></label>'
      + '<label class="lb-field">מה לעשות<input class="lb-input" dir="rtl" name="next_note" value="' + esc(l.next_note || "") + '" maxlength="300"></label>'
      + '<label class="lb-field is-wide">הערה<textarea class="lb-textarea" dir="rtl" name="note" maxlength="4000">' + esc(l.note || "") + "</textarea></label></div>"
      + (l.log && l.log.length ? '<ul class="ct-notes">' + l.log.slice().reverse().map(n => "<li><time>" + fmt(n.at) + "</time>" + esc(n.t) + "</li>").join("") + "</ul>" : "")
      + '<p class="ct-hint">רושמים רק מה שהאדם כתב או שלח. הטלפון והשם נשמרים רק על המחשב הזה.</p>'
      + '<p class="lb-form-error" hidden></p><div class="lb-form-actions"><button class="lb-btn" type="submit">' + ic("check") + "שמירה</button>"
      + '<button class="lb-btn secondary" type="button" data-dlg-close>ביטול</button>'
      + (lid ? '<button class="lb-btn secondary" type="button" data-copy-reply="' + esc(lid) + '">' + ic("copy") + "העתקת תשובה</button>"
        + '<span class="lb-spacer"></span><button class="lb-btn ghost" type="button" data-del-lead="' + esc(lid) + '">' + ic("close") + "מחיקת הליד</button>" : "") + "</div>";
  }
  function groupForm(track) {
    return '<div class="ct-grid2"><label class="lb-field is-wide">שם הקבוצה<input class="lb-input" dir="rtl" name="name" required maxlength="200" autofocus></label>'
      + '<label class="lb-field is-wide">קישור<input class="lb-input" dir="ltr" name="url" placeholder="https://www.facebook.com/groups/..."></label>'
      + '<label class="lb-field">מסלול' + select('name="track"', [["parent", "הורים"], ["ugc", "יוצרי UGC"]], track) + "</label>"
      + '<label class="lb-field">עיר או אזור<input class="lb-input" dir="rtl" name="geo"></label>'
      + '<label class="lb-field">חברים<input class="lb-input" type="number" min="0" name="members_n"></label>'
      + '<label class="lb-field">ציבורית או פרטית' + select('name="privacy"', [["", "לא ידוע"], ["Public", "ציבורית"], ["Private", "פרטית"]], "") + "</label>"
      + '<label class="lb-field is-wide">כללי פרסום<textarea class="lb-textarea" dir="rtl" name="policy" maxlength="1000"></textarea></label></div>'
      + '<p class="lb-form-error" hidden></p><div class="lb-form-actions"><button class="lb-btn" type="submit">' + ic("plus") + "הוספה</button><button class=\"lb-btn secondary\" type=\"button\" data-dlg-close>ביטול</button></div>";
  }
  function formData() { const o = {}; new FormData(form).forEach((v, k) => { o[k] = typeof v === "string" ? v.trim() : v; }); return o; }
  function formError(msg) { const e = form.querySelector(".lb-form-error"); if (e) { e.textContent = msg; e.hidden = false; } }
  function submitDlg() {
    const v = formData(), c = dlgCtx;
    if (!c) return;
    if (c.kind === "group") {
      if (!v.name) return formError("צריך שם לקבוצה.");
      if (v.url && !/^https?:\/\//.test(v.url)) return formError("הקישור צריך להתחיל ב-https://");
      const id = newId("m");
      const doc = { status: "new", notes: [], custom: { name: v.name, url: v.url, track: v.track, geo: v.geo, members_n: v.members_n === "" ? null : Number(v.members_n), privacy: v.privacy, policy: v.policy } };
      return put("groups", id, doc).then(() => { dlg.close(); refresh(); openGroup(id); }, e => formError(e.message));
    }
    if (!v.gid) return formError("צריך לבחור קבוצה.");
    if (c.kind === "post") {
      if (!v.on) return formError("צריך תאריך.");
      if (v.url && !/^https?:\/\//.test(v.url)) return formError("הקישור צריך להתחיל ב-https://");
      const old = c.id ? S.posts[c.id] : null, id = c.id || newId("p");
      const doc = { gid: v.gid, on: v.on, url: v.url, template: v.template, state: v.state, note: v.note, checked_on: v.checked_on,
        reactions: v.reactions === "" ? null : Number(v.reactions), comments: v.comments === "" ? null : Number(v.comments), shares: v.shares === "" ? null : Number(v.shares) };
      const changed = !old || ["reactions", "comments", "shares"].some(k => (old[k] == null ? null : old[k]) !== doc[k]);
      if (changed && (doc.reactions != null || doc.comments != null || doc.shares != null) && (!old || doc.checked_on === (old.checked_on || ""))) doc.checked_on = today();
      if (old && old.text) doc.text = old.text;
      return put("posts", id, doc).then(() => {
        const st = gst(v.gid);
        dlg.close();
        if (!old && ["new", "join", "member", "admin", "ok", "later"].indexOf(st) >= 0) return setGroupStatus(v.gid, "active");
        refresh();
      }, e => formError(e.message));
    }
    if (c.kind === "lead") {
      if (!v.name) return formError("צריך שם.");
      if (v.fb && !/^https?:\/\//.test(v.fb)) return formError("הקישור לפרופיל צריך להתחיל ב-https://");
      const g = grp(v.gid), old = c.id ? S.leads[c.id] : null, id = c.id || newId("l");
      const doc = { gid: v.gid, pid: v.pid || "", track: g ? g.track : "parent", name: v.name, channel: v.channel, status: v.status, fb: v.fb, ig: (v.ig || "").replace(/^@/, ""),
        phone: v.phone, email: v.email, city: v.city, kids: v.kids, next_on: v.next_on, next_note: v.next_note, note: v.note, on: v.on, log: old && old.log ? old.log.slice() : [] };
      if (doc.pid && (!S.posts[doc.pid] || S.posts[doc.pid].gid !== doc.gid)) doc.pid = "";
      if (!old) doc.log.push({ at: nowIso(), t: "נוסף: " + lsl(doc.track, doc.status) + " · " + (CHL[doc.channel] || "") });
      if (old && old.status !== doc.status) doc.log.push({ at: nowIso(), t: "השלב השתנה ל: " + lsl(doc.track, doc.status) });
      if ((!old || old.status !== doc.status) && (!old ? !doc.next_on : doc.next_on === (old.next_on || ""))) {
        const nx = !old && doc.status === "new" ? [today(), "לענות"] : leadNext(doc.status, doc.track);
        if (nx) { doc.next_on = nx[0]; doc.next_note = nx[1]; }
      }
      return put("leads", id, doc).then(() => { dlg.close(); refresh(); }, e => formError(e.message));
    }
  }
  function postDialog(pid, gid) { openDlg(pid ? "עריכת פוסט" : "פוסט חדש", postForm(pid, gid), { kind: "post", id: pid }); }
  function leadDialog(lid, gid, pid) { openDlg(lid ? "ליד" : "ליד חדש", leadForm(lid, gid, pid), { kind: "lead", id: lid, pid }); }
  function rerenderDlg(gid) {
    const c = dlgCtx, keep = formData();
    if (!c || c.id) return;   // an existing post or lead keeps its group
    form.innerHTML = c.kind === "post" ? postForm(null, gid) : leadForm(null, gid, "");
    Object.keys(keep).forEach(k => { if (k === "gid" || k === "pid" || k === "status" || k === "template") return; const el = form.elements[k]; if (el && keep[k]) el.value = keep[k]; });
    const f = form.querySelector('[name="name"]') || form.querySelector('[name="url"]'); if (f) f.focus();
  }

  // ---- reminders: done and later ------------------------------------------------------------------------------------------------
  function remAct(key, snooze) {
    const p = key.split(":"), k = p[0], id = p[1];
    if (k === "post") {
      const doc = clone(S.posts[id]); if (!doc) return;
      doc.checked_on = today(); return putR("posts", id, doc);
    }
    const kind = k === "group" ? "groups" : "leads";
    const doc = k === "group" ? gdoc(id) : clone(S.leads[id]); if (!doc) return;
    if (snooze) { doc.next_on = addDays(today(), snooze); }
    else {
      const what = doc.next_note || "הצעד הבא"; doc.next_on = ""; doc.next_note = "";
      if (k === "group") doc.notes.push({ at: nowIso(), t: "בוצע: " + what }); else { doc.log = doc.log || []; doc.log.push({ at: nowIso(), t: "בוצע: " + what }); }
    }
    return putR(kind, id, doc);
  }

  // ---- templates -------------------------------------------------------------------------------------------------------------------
  let tplTimer = null;
  function tplDoc() {
    const m = S.settings.main && S.settings.main.templates;
    return { templates: { parent: clone(m && m.parent && m.parent.length ? m.parent : TPL0.parent), ugc: clone(m && m.ugc && m.ugc.length ? m.ugc : TPL0.ugc) } };
  }
  function saveTpl(doc, rerender) {
    S.settings.main = doc; clearTimeout(tplTimer);
    const send = { templates: {} };
    Object.keys(doc.templates).forEach(k => { send.templates[k] = doc.templates[k].map(t => Object.assign({}, t, { title: (t.title || "").trim() || "בלי שם" })); });
    tplTimer = setTimeout(() => { put("settings", "main", send).then(() => { if (rerender) render(); }, () => {}); }, rerender ? 0 : 700);
    if (rerender) render();
  }

  // ---- routing ------------------------------------------------------------------------------------------------------------------------
  function readHash() { applyRoute(location.hash.replace(/^#/, "")); }
  function applyRoute(h) {
    const parts = String(h || "").split("?"), key = parts[0] || "home";
    route = TITLES[key] && key !== "search" && !(EMB && key === "reminders") ? key : "home";
    if (parts[1]) {
      const qs = new URLSearchParams(parts[1]), view = route === "parents" || route === "ugc" || route === "posts" || route === "leads" ? route : null;
      if (view) { qs.forEach((v, k) => { if (k in UI[view]) UI[view][k] = v; }); store(LS_UI, UI); }
    }
  }
  if (!EMB) window.addEventListener("hashchange", () => { readHash(); closeSide(); window.scrollTo(0, 0); render(); });
  function closeSide() { const sd = $("#ctSide"), sc = $("#ctScrim"); if (sd) sd.classList.remove("is-open"); if (sc) sc.hidden = true; }

  // ---- events ---------------------------------------------------------------------------------------------------------------------------
  document.addEventListener("click", e => {
    if (!inScope(e.target)) { closePop(); return; }
    const t = e.target.closest("button, a"); if (!t) { if (!e.target.closest("#ctPop")) closePop(); return; }
    const ds = t.dataset;
    if (!t.closest("#ctPop") && !ds.gstatus) closePop();
    if (ds.cre && EMB && window.openCreator) { e.preventDefault(); window.openCreator(ds.cre); return; }   // the creator's own card, in the creators or professionals view
    if (ds.openG) { e.preventDefault(); openGroup(ds.openG); return; }
    if (ds.gstatus) { e.preventDefault(); if (!$("#ctPop").hidden && $("#ctPop").dataset.for === ds.gstatus) { closePop(); return; } $("#ctPop").dataset.for = ds.gstatus; statusMenu(t, ds.gstatus); return; }
    if (ds.setGst) { const p = ds.setGst.split(":"); closePop(); setGroupStatus(p[0], p[1]); return; }
    if (ds.addPost !== undefined && t.id !== "ctAddPost") { e.preventDefault(); postDialog(null, ds.addPost); return; }
    if (ds.addLead !== undefined && t.id !== "ctAddLead") { e.preventDefault(); leadDialog(null, ds.addLead, ds.pid || ""); return; }
    if (ds.editPost) { e.preventDefault(); postDialog(ds.editPost); return; }
    if (ds.editLead) { e.preventDefault(); leadDialog(ds.editLead); return; }
    if (ds.addGroup) { openDlg("קבוצה שלא במחקר", groupForm(ds.addGroup), { kind: "group" }); return; }
    if (ds.openRem) { const p = ds.openRem.split(":"); if (p[0] === "group") openGroup(p[1]); else if (p[0] === "lead") leadDialog(p[1]); else postDialog(p[1]); return; }
    if (ds.remDone) { remAct(ds.remDone, 0); return; }
    if (ds.remSnooze) { const p = ds.remSnooze.split(":"); remAct(p[0] + ":" + p[1], Number(p[2])); return; }
    if (ds.checked) { const doc = clone(S.posts[ds.checked]); doc.checked_on = today(); putR("posts", ds.checked, doc); return; }
    if (ds.f) {
      const p = ds.f.split(":"); UI[p[0]][p[1]] = p[2];
      if (p[0] === "leads" && p[1] === "track") UI.leads.st = "all";
      if (UI[p[0]].n) UI[p[0]].n = 30; store(LS_UI, UI); render(); return;
    }
    if (ds.more) { UI[ds.more].n += 30; store(LS_UI, UI); render(); return; }
    if (ds.copyTpl) {
      const p = ds.copyTpl.split(":"), tp = templates(p[0]).find(x => x.id === p[1]); if (!tp) return;
      const g = ds.gid && grp(ds.gid);
      copy(fillTemplate(tp.text, { city: g && g.geo && g.geo !== "ארצית" ? g.geo : "" }));
      if (g && tp.kind === "admin" && gst(g.id) !== "admin" && ["new", "join", "member"].indexOf(gst(g.id)) >= 0) toast("הועתק. אחרי השליחה אפשר לסמן: פניתי למנהלים");
      return;
    }
    if (ds.copyReply) {
      const l = S.leads[ds.copyReply]; if (!l) return;
      const tp = templates(l.track).find(x => x.kind === "dm") || templates(l.track)[0];
      if (tp) copy(fillTemplate(tp.text, { name: firstName(l.name) }));
      return;
    }
    if (ds.newTpl) { const d = tplDoc(); d.templates[ds.newTpl].push({ id: newId("t"), kind: "other", title: "נוסח חדש", text: "" }); saveTpl(d, true); return; }
    if (ds.delTpl) {
      const p = ds.delTpl.split(":"), d = tplDoc(), it = d.templates[p[0]][Number(p[1])];
      if (!it || !confirm("למחוק את הנוסח ״" + it.title + "״?")) return;
      d.templates[p[0]].splice(Number(p[1]), 1);
      if (!d.templates[p[0]].length) { toast("צריך להשאיר לפחות נוסח אחד"); return; }
      saveTpl(d, true); return;
    }
    if (ds.resetTpl !== undefined) { if (!confirm("לחזור לנוסחים המקוריים? הנוסחים שערכת יימחקו.")) return; S.settings.main = undefined; put("settings", "main", null).then(render, render); return; }
    if (ds.delPost) {
      const n = (IDX.leadsByPost[ds.delPost] || []).length;
      if (!confirm("למחוק את הפוסט?" + (n ? " " + n + " לידים יישארו, בלי הקישור לפוסט." : ""))) return;
      const pid = ds.delPost;
      Promise.all((IDX.leadsByPost[pid] || []).map(lid => { const l = clone(S.leads[lid]); l.pid = ""; return put("leads", lid, l); }))
        .then(() => put("posts", pid, null)).then(() => { dlg.close(); refresh(); }, refresh);
      return;
    }
    if (ds.delLead) { if (!confirm("למחוק את הליד?")) return; put("leads", ds.delLead, null).then(() => { dlg.close(); refresh(); }, refresh); return; }
    if (ds.delGroup) {
      if ((IDX.posts[ds.delGroup] || []).length || (IDX.leads[ds.delGroup] || []).length) { toast("יש לקבוצה פוסטים או לידים. צריך למחוק אותם קודם."); return; }
      if (!confirm("להסיר את הקבוצה מהרשימה?")) return;
      const id = ds.delGroup; closeDrawer(); putR("groups", id, null); return;
    }
    if (ds.pickClear !== undefined) { const c = dlgCtx; if (!c || c.id) return; form.innerHTML = c.kind === "post" ? postForm(null, "") : leadForm(null, "", ""); const inp = form.querySelector("[data-combo]"); if (inp) inp.focus(); return; }
    if (ds.pickG) { rerenderDlg(ds.pickG); return; }
    if (ds.dlgClose !== undefined) { dlg.close(); return; }
    if (t.id === "ctAddPost") { postDialog(null, drawerGid || ""); return; }
    if (t.id === "ctAddLead") { leadDialog(null, drawerGid || "", ""); return; }
    if (t.id === "ctDrawerX") { closeDrawer(); return; }
    if (t.id === "ctDlgX") { dlg.close(); return; }
    if (t.id === "ctMenu") { $("#ctSide").classList.add("is-open"); $("#ctScrim").hidden = false; return; }
  });
  if ($("#ctScrim")) $("#ctScrim").addEventListener("click", closeSide);
  $("#ctDScrim").addEventListener("click", closeDrawer);
  dlg.addEventListener("click", e => { if (e.target === dlg) dlg.close(); });
  form.addEventListener("submit", e => { e.preventDefault(); submitDlg(); });

  document.addEventListener("change", e => {
    if (!inScope(e.target)) return;
    const t = e.target, ds = t.dataset;
    if (ds.fs) { const p = ds.fs.split(":"); UI[p[0]][p[1]] = t.value; if (UI[p[0]].n) UI[p[0]].n = 30; store(LS_UI, UI); render(); return; }
    if (ds.fc) { const p = ds.fc.split(":"); UI[p[0]][p[1]] = t.checked; UI[p[0]].n = 30; store(LS_UI, UI); render(); return; }
    if (ds.lstatus) { setLeadStatus(ds.lstatus, t.value); return; }
    if (ds.pstate) { const d = clone(S.posts[ds.pstate]); d.state = t.value; putR("posts", ds.pstate, d); return; }
    if (ds.pnum) {
      const p = ds.pnum.split(":"), d = clone(S.posts[p[0]]);
      d[p[1]] = t.value === "" ? null : Math.max(0, Math.round(Number(t.value))); d.checked_on = today();
      put("posts", p[0], d).then(navCounts, () => {}); return;
    }
    if (ds.gf) { saveGroupField(ds.gf, t.value.trim()); return; }
    if (ds.gc) { saveCustomField(ds.gc, t.value.trim()); return; }
  });
  document.addEventListener("input", e => {
    if (!inScope(e.target)) return;
    const t = e.target, ds = t.dataset;
    if (ds.tf) { const p = ds.tf.split(":"), d = tplDoc(), it = d.templates[p[0]][Number(p[1])]; if (!it) return; it[p[2]] = t.value; saveTpl(d, false); return; }
    if (ds.combo !== undefined) {
      const list = t.parentElement.querySelector(".ct-combo-list"), res = comboResults(t.value);
      list.innerHTML = res.length ? res.map((g, i) => '<li><button type="button" data-pick-g="' + esc(g.id) + '"' + (i === 0 ? ' class="is-on"' : "") + '><span translate="no">' + esc(g.name) + "</span><small>" + esc([TRACK[g.track], g.geo, GSL[gst(g.id)]].filter(Boolean).join(" · ")) + "</small></button></li>").join("") : '<li class="ct-hint">אין קבוצה כזאת</li>';
      list.hidden = false; return;
    }
    if (t.id === "ctQ") { Q = t.value.trim(); render(); if (EMB && Q && !window.CT.count(Q) && host().miss) host().miss(Q); }
  });
  document.addEventListener("submit", e => {
    if (!inScope(e.target)) return;
    if (e.target.matches("[data-addnote]")) {
      e.preventDefault(); const inp = e.target.elements.t, v = inp.value.trim(); if (!v || !drawerGid) return;
      const d = gdoc(drawerGid); d.notes.push({ at: nowIso(), t: v }); putR("groups", drawerGid, d);
    }
  });
  document.addEventListener("keydown", e => {
    const inField = /^(INPUT|TEXTAREA|SELECT)$/.test((e.target || {}).tagName || "");
    if (e.key === "/" && !inField && !dlg.open && active && $("#ctQ")) { e.preventDefault(); $("#ctQ").focus(); return; }
    if (e.key === "Escape") {
      if (!$("#ctPop").hidden) { closePop(); return; }
      if (dlg.open) return;
      if (drawerGid) { closeDrawer(); return; }
      if (e.target.id === "ctQ" && Q) { e.target.value = ""; Q = ""; render(); }
    }
    if (e.key === "Enter" && e.target.matches && e.target.matches("[data-combo]")) {
      e.preventDefault(); const b = e.target.parentElement.querySelector(".ct-combo-list button"); if (b) rerenderDlg(b.dataset.pickG);
    }
  });
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState !== "visible" || !online || pending || dlg.open) return;
    const active = document.activeElement; if (active && /^(INPUT|TEXTAREA)$/.test(active.tagName)) return;
    load().then(refresh);
  });

  // ---- embedded in the creator map: what the map calls -------------------------------------------------------------------------------
  // a lead or a post as a card for the shared reminders stack (a group uses its own card, groupCard)
  function leadCard(id) {
    const l = S.leads[id]; if (!l) return "";
    const g = grp(l.gid) || { name: "" }, facts = [];
    facts.push("<span>" + ic(TRACK_ICON[l.track] || "people") + esc(TRACK[l.track] || "") + "</span>");
    if (g.name) facts.push('<span>' + ic("group") + '<button type="button" class="ct-link" data-open-g="' + esc(l.gid) + '" translate="no">' + esc(g.name) + "</button></span>");
    if (l.channel) facts.push("<span>" + ic("chat") + esc(CHL[l.channel] || l.channel) + "</span>");
    if (l.city) facts.push("<span>" + ic("pin") + esc(l.city) + "</span>");
    return '<article class="lb-card ct-gc"><div class="ct-gc-top"><span class="lb-tile is-soft ' + (l.track === "ugc" ? "lb-cat-5" : "lb-cat-6") + '">' + ic("user-plus") + "</span>"
      + '<div class="ct-gc-name"><button type="button" data-edit-lead="' + esc(id) + '" translate="no">' + esc(l.name) + '</button><div class="ct-facts">' + facts.join("") + "</div></div>"
      + select('data-lstatus="' + esc(id) + '" aria-label="שלב"', LS[l.track] || LS.all, l.status) + "</div>"
      + (l.note ? '<p class="ct-pol lb-clamp-2">' + esc(l.note) + "</p>" : "")
      + '<div class="ct-gc-foot">' + nextHtml(l.next_on, l.next_note) + '<span class="lb-spacer"></span>' + contactIcons(l)
      + '<button type="button" class="lb-btn secondary sm" data-copy-reply="' + esc(id) + '">' + ic("copy") + "תשובה להעתקה</button>"
      + '<button type="button" class="lb-btn secondary sm" data-edit-lead="' + esc(id) + '">' + ic("pencil") + "עריכה</button></div></article>";
  }
  function postCard(id) {
    const p = S.posts[id]; if (!p) return "";
    const g = grp(p.gid) || { name: "", track: "parent" }, lc = (IDX.leadsByPost[id] || []).length;
    const n = (k, l) => '<label class="ct-next">' + esc(l) + ' <input class="lb-input ct-num" type="number" min="0" inputmode="numeric" data-pnum="' + esc(id) + ":" + k + '" value="' + (p[k] == null ? "" : p[k]) + '"></label>';
    return '<article class="lb-card ct-gc ct-table"><div class="ct-gc-top"><span class="lb-tile is-soft ' + (g.track === "ugc" ? "lb-cat-5" : "lb-cat-6") + '">' + ic("send") + "</span>"
      + '<div class="ct-gc-name"><button type="button" data-open-g="' + esc(p.gid) + '" translate="no">' + esc(g.name) + '</button><div class="ct-facts"><span>' + ic("calendar") + "פורסם " + fmt(p.on) + "</span>"
      + (p.template ? "<span>" + ic("copy") + esc(p.template) + "</span>" : "") + "<span>" + ic("user-plus") + "<b>" + lc + "</b> לידים</span></div></div>"
      + pill("ps-" + p.state, PSL[p.state] || p.state) + "</div>"
      + '<div class="ct-gc-foot">' + n("reactions", "רגש") + n("comments", "תגובות") + n("shares", "שיתופים") + '<span class="lb-spacer"></span>'
      + (p.url ? '<a class="lb-btn ghost sm icon" href="' + esc(p.url) + '" target="_blank" rel="noopener" aria-label="לפוסט" title="לפוסט">' + ic("open-out") + "</a>" : "")
      + '<button type="button" class="lb-btn secondary sm" data-add-lead="' + esc(p.gid) + '" data-pid="' + esc(id) + '">' + ic("user-plus") + "ליד</button>"
      + '<button type="button" class="lb-btn secondary sm" data-edit-post="' + esc(id) + '">' + ic("pencil") + "עריכה</button></div></article>";
  }
  if (EMB) window.CT = {
    show(sub) { const was = active; active = true; applyRoute(sub); if (!was) closePop(); render(); },
    hide() { if (!active) return; active = false; closePop(); navCounts(); },
    reminders() { return reminders(); },
    card(r) { if (r.k === "group") { const g = grp(r.id); return g ? groupCard(g) : ""; } return r.k === "lead" ? leadCard(r.id) : postCard(r.id); },
    done(key) { return remAct(key, 0); },
    snooze(key, days) { return remAct(key, days); },
    search(q) { Q = String(q || "").trim(); const i = $("#ctQ"); if (i) i.value = Q; render(); },
    // how many groups and leads a search finds (the map asks, to open a search in the view where it has results)
    count(q) { q = String(q || "").trim().toLowerCase(); if (!q) return 0;
      return allGroups().filter(g => (g.name + " " + g.geo + " " + g.pol + " " + g.notes).toLowerCase().indexOf(q) >= 0).length
        + Object.keys(S.leads).filter(id => { const l = S.leads[id]; return (l.name + " " + l.city + " " + l.ig + " " + l.note).toLowerCase().indexOf(q) >= 0; }).length; },
    titles: TITLES, track: TRACK
  };

  // ---- start ------------------------------------------------------------------------------------------------------------------------------
  if (EMB) { const h = location.hash.replace(/^#/, ""); if (h.indexOf("fb-") === 0) { active = true; applyRoute(h.slice(3)); } }
  else readHash();
  load().then(refresh);
})();
