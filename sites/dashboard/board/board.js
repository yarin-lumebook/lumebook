/* LumeBook work board: the dashboard's default view. A Miro-style canvas of cards, frames and connections over the
   project's real resources, with a tools dock, templates, search, filters, a list view, undo/redo and saving.

   Where edits are saved (shown in the toolbar, never implied):
   - claude.ai artifact with the db capability: the artifact database, under boards/main (head) and
     boards/main/parts/<slot>-<n> (the board in parts of at most ~180 KB, written to the slot the head does not point
     at, head last, so an interrupted save leaves the previous version whole). Never under snapshot, history or tracker.
   - anywhere else (the read-only Vercel copy, the local project server, a file): this browser's localStorage only,
     labelled "saved on this device", with JSON export and import.
   The daily refresh only changes snapshot/latest and history; cards point at catalog resources by id (`ref`) and keep
   their own title, notes and position, so a refresh updates what a card shows from its source and nothing else.

   Data: window.LB_SEED (board/seed.js, from catalog.py: resources, first board, templates) and window.LBDash.data
   (published by the dashboard script: snapshot, history, tracker, signups). Light mode, Hebrew RTL, no framework. */
(() => {
  "use strict";
  const ROOT = document.getElementById("board-root");
  if (!ROOT) return;
  window.LBBoardLoaded = true;
  const SEED = window.LB_SEED || { resources: [], seed: { frames: [], cards: [], edges: [], dock: [], known: [] }, templates: [], areas: {} };
  const SCHEMA = 1;
  const KEY = "lb-board:v1";
  const TAB = "t" + Math.random().toString(36).slice(2, 10);
  const GRID = 20;
  const PART_LIMIT = 180 * 1024;

  // ---------- small helpers ----------
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const uid = (p) => { const r = new Uint32Array(2); crypto.getRandomValues(r); return p + Date.now().toString(36) + r[0].toString(36) + r[1].toString(36).slice(0, 3); };
  const nowIso = () => new Date().toISOString();
  const dm = (d) => `${d.getDate()}.${d.getMonth() + 1}`;
  const hm = (d) => `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
  const parseDay = (s) => { const [y, m, d] = String(s).slice(0, 10).split("-").map(Number); return new Date(y, m - 1, d); };
  const today0 = () => { const d = new Date(); d.setHours(0, 0, 0, 0); return d; };
  const ago = (iso) => {
    if (!iso) return "";
    const ms = Date.now() - new Date(iso).getTime(), h = ms / 36e5;
    if (!Number.isFinite(h)) return "";
    if (h < 1) return `לפני ${Math.max(1, Math.round(ms / 6e4))} דק׳`;
    if (h < 24) return `לפני ${Math.round(h)} שע׳`;
    return `לפני ${Math.round(h / 24)} ימים`;
  };
  const enc = new TextEncoder();
  const bytes = (s) => enc.encode(s).length;
  const norm = (s) => String(s || "").toLowerCase().replace(/[֑-ׇ]/g, "").replace(/[״׳"'`.,:;!?()\[\]{}]/g, " ");
  const snapTo = (v) => Math.round(v / GRID) * GRID;
  const isTyping = (el) => !!el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));
  const fmt = (n) => n == null ? "–" : n >= 10000 ? (n / 1000).toFixed(n >= 100000 ? 0 : 1).replace(/\.0$/, "") + "K" : Number(n).toLocaleString("en-US");

  // links: only http(s) and mailto open; anything else is a project path (relative, no "..") or rejected
  function safeHref(u) {
    u = String(u || "").trim();
    if (!/^(https?:\/\/|mailto:)/i.test(u)) return null;
    try { const x = new URL(u); return /^(https?|mailto):$/.test(x.protocol) ? x.href : null; } catch { return null; }
  }
  function safePath(p) {
    p = String(p || "").trim().replace(/^\.\//, "");
    if (!p || p.length > 400 || /^[a-z][a-z0-9+.-]*:/i.test(p) || p.startsWith("/") || p.startsWith("\\")) return null;
    if (p.split("/").some((s) => s === ".." || s === ".")) return null;
    return /^[\w\-. /֐-׿()+,@&]+$/.test(p) ? p.replace(/\/+$/, "") : null;
  }
  const extKind = (s) => {
    const e = (String(s || "").split("?")[0].match(/\.([a-z0-9]+)$/i) || [])[1]?.toLowerCase();
    return !e ? null : ["png", "jpg", "jpeg", "webp", "gif", "svg", "avif"].includes(e) ? "image" : ["mp4", "mov", "webm", "m4v"].includes(e) ? "video"
      : ["mp3", "m4a", "wav", "ogg", "opus", "aac"].includes(e) ? "audio" : e === "pdf" ? "pdf" : ["html", "htm"].includes(e) ? "html" : ["md", "txt", "csv", "json"].includes(e) ? "text" : null;
  };
  const host = (u) => { try { const x = new URL(u); return (x.host + x.pathname).replace(/\/$/, ""); } catch { return u; } };
  const driveId = (u) => (/drive\.google\.com\/file\/d\/([\w-]+)/.exec(u || "") || [])[1] || null;

  // ---------- icons ----------
  const P = {
    note: '<path d="M5 3h10l4 4v14H5z"/><path d="M15 3v4h4M8 11h8M8 15h6"/>',
    task: '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M8 12l3 3 5-6"/>',
    project: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    doc: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    media: '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-8 8"/>',
    tool: '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.8-.7-.7-2.8z"/>',
    prompt: '<path d="M4 5h16v11H8l-4 4z"/><path d="M8 9l2 2-2 2M12 13h4"/>',
    workflow: '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="12" r="2.5"/><circle cx="6" cy="18" r="2.5"/><path d="M8.5 6H13a3 3 0 0 1 3 3v.5M15.5 12H11a3 3 0 0 0-3 3v.5"/>',
    metric: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    view: '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>',
    frame: '<path d="M7 3v18M17 3v18M3 7h18M3 17h18"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    undo: '<path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
    redo: '<path d="M15 14l5-5-5-5"/><path d="M20 9H10a6 6 0 0 0 0 12h3"/>',
    hand: '<path d="M8 13V5.5a1.5 1.5 0 0 1 3 0V12M11 11.5v-7a1.5 1.5 0 0 1 3 0V12M14 11.5V6.5a1.5 1.5 0 0 1 3 0V15a6 6 0 0 1-6 6h-1a6 6 0 0 1-5-2.7L3.2 14a1.6 1.6 0 0 1 2.6-1.9L8 15"/>',
    cursor: '<path d="M5 3l14 7-6 2-2 6z"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    filter: '<path d="M3 5h18l-7 8v6l-4 2v-8z"/>',
    grid: '<path d="M4 4h4v4H4zM10 4h4v4h-4zM16 4h4v4h-4zM4 10h4v4H4zM10 10h4v4h-4zM16 10h4v4h-4zM4 16h4v4H4zM10 16h4v4h-4zM16 16h4v4h-4z"/>',
    deps: '<path d="M5 6h6M5 12h14M13 18h6" stroke-dasharray="3 3"/><circle cx="5" cy="6" r="1.5"/><circle cx="19" cy="18" r="1.5"/>',
    list: '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    board: '<rect x="3" y="3" width="18" height="18" rx="2"/><rect x="6.5" y="6.5" width="5" height="4" rx="1"/><rect x="13" y="12" width="5" height="5" rx="1"/><path d="M11.5 9h2a2 2 0 0 1 2 2v1"/>',
    more: '<circle cx="5" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="19" cy="12" r="1.3"/>',
    help: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 0 1 4.8 1c0 1.7-2.3 2.2-2.3 3.5M12 17.2v.1"/>',
    open: '<path d="M14 4h6v6M20 4l-9 9"/><path d="M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>',
    eye: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    edit: '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
    copy: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
    dup: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M4 16V5a1 1 0 0 1 1-1h11M14 11v6M11 14h6"/>',
    trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    pin: '<path d="M9 4h6l-1 6 3 3H7l3-3zM12 13v8"/>',
    pinned: '<path d="M9 4h6l-1 6 3 3H7l3-3zM12 13v8" fill="currentColor"/>',
    close: '<path d="M6 6l12 12M18 6L6 18"/>',
    home: '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    fit: '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
    minus: '<path d="M5 12h14"/>',
    connect: '<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="12" r="2.5"/><path d="M8.5 12h7"/>',
    tpl: '<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><path d="M17 14v6M14 17h6"/>',
    nav: '<path d="M12 3l8 4-8 4-8-4z"/><path d="M4 12l8 4 8-4M4 17l8 4 8-4"/>',
    spark: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M6 18l2.5-2.5M15.5 8.5L18 6"/>',
    alignR: '<path d="M20 4v16M8 8h10M12 14h6"/>', alignL: '<path d="M4 4v16M6 8h10M6 14h6"/>',
    alignT: '<path d="M4 4h16M8 6v10M14 6v6"/>', alignB: '<path d="M4 20h16M8 8v10M14 12v6"/>',
    alignC: '<path d="M12 3v18M6 8h12M8 14h8"/>', alignM: '<path d="M3 12h18M8 6v12M14 8v8"/>',
    distH: '<path d="M4 4v16M20 4v16M10 8v8h4V8z"/>', distV: '<path d="M4 4h16M4 20h16M8 10h8v4H8z"/>',
    upload: '<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v4h16v-4"/>',
    download: '<path d="M12 4v12M7 11l5 5 5-5"/><path d="M4 20h16"/>',
    swap: '<path d="M7 4L3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7"/>',
    chev: '<path d="M9 6l6 6-6 6"/>', check: '<path d="M5 12l5 5 9-10"/>', up: '<path d="M12 19V5M6 11l6-6 6 6"/>', down: '<path d="M12 5v14M6 13l6 6 6-6"/>',
    play: '<path d="M7 4l13 8-13 8z"/>', backup: '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5M12 8v4l3 2"/>',
  };
  const I = (n) => `<svg viewBox="0 0 24 24" aria-hidden="true">${P[n] || P.note}</svg>`;

  // ---------- vocabulary ----------
  const TYPES = {
    note: { label: "פתק", icon: "note", w: 260, h: 180, untitled: "פתק חדש" },
    task: { label: "משימה", icon: "task", w: 260, h: 180, untitled: "משימה חדשה" },
    project: { label: "פרויקט", icon: "project", w: 300, h: 200, untitled: "פרויקט חדש" },
    link: { label: "קישור", icon: "link", w: 260, h: 140, untitled: "קישור חדש" },
    doc: { label: "מסמך", icon: "doc", w: 260, h: 140, untitled: "מסמך חדש" },
    media: { label: "מדיה", icon: "media", w: 260, h: 240, untitled: "מדיה חדשה" },
    tool: { label: "כלי", icon: "tool", w: 260, h: 160, untitled: "כלי חדש" },
    prompt: { label: "פרומפט", icon: "prompt", w: 260, h: 160, untitled: "פרומפט חדש" },
    workflow: { label: "תהליך", icon: "workflow", w: 260, h: 240, untitled: "תהליך חדש" },
    metric: { label: "מדד", icon: "metric", w: 260, h: 160, untitled: "מדד" },
    view: { label: "תצוגה", icon: "view", w: 260, h: 140, untitled: "תצוגה" },
  };
  const ADDABLE = ["note", "task", "project", "link", "doc", "media", "prompt", "workflow", "tool", "metric", "view"];
  const STATUS = { todo: ["לעשות", ""], doing: ["בעבודה", "info"], review: ["לבדיקה", "accent"], blocked: ["תקוע", "warning"], done: ["בוצע", "success"] };
  const PRIO = { low: "נמוכה", normal: "רגילה", high: "גבוהה" };
  const COLORS = { plain: "לבן", cream: "קרם", violet: "סגול", sand: "חול" };
  const KIND_GROUP = { "local-tool": "כלים מקומיים", command: "פקודות", prompt: "פרומפטים", artifact: "דפים וארטיפקטים", site: "קישורים ו-Drive",
    link: "קישורים ו-Drive", form: "קישורים ו-Drive", sheet: "קישורים ו-Drive", drive: "קישורים ו-Drive", file: "קבצים ותיקיות", folder: "קבצים ותיקיות",
    media: "מדיה", view: "תצוגות ומדדים", metric: "תצוגות ומדדים" };
  const GROUP_ORDER = ["כלים מקומיים", "דפים וארטיפקטים", "קישורים ו-Drive", "פרומפטים", "פקודות", "תצוגות ומדדים", "קבצים ותיקיות", "מדיה"];
  const VIEW_NAMES = { overview: "סקירה", plan: "תוכנית", creators: "יוצרים", signups: "הרשמות", content: "קרוסלות", competitors: "מתחרים", research: "ספריית מחקר", sync: "סנכרון", assets: "אתרים וקבצים" };
  const COUNTERS = { reels: ["רילס", 18], books: ["ספרים ליוצרים", 10], customer_videos: ["סרטוני לקוחות בהסכמה", 10], outreach: ["פניות ליוצרים", null] };
  const AREAS = SEED.areas || {};
  const areaCat = (a) => (AREAS[a] ? `lb-cat-${AREAS[a].cat}` : "lb-cat-0");

  // ---------- environment and per-device preferences ----------
  const ENV = { isStatic: !!window.__DASH__, projectServer: null, mode: "loading", canWrite: true, assets: null, downloads: null, localTools: {} };
  const LS = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { localStorage.setItem(k, v); },
    del(k) { try { localStorage.removeItem(k); } catch {} },
  };
  const PREF_KEY = KEY + ":prefs";
  const small = () => window.matchMedia("(max-width: 760px)").matches;
  let prefs = { view: null, mode: null, dockOpen: null, dockTab: "tools", showDeps: true, snap: true, open: {} };
  try { Object.assign(prefs, JSON.parse(LS.get(PREF_KEY) || "{}")); } catch {}
  let prefTimer = 0;
  const savePrefs = () => { clearTimeout(prefTimer); prefTimer = setTimeout(() => { try { LS.set(PREF_KEY, JSON.stringify(prefs)); } catch {} }, 300); };

  // ---------- catalog (seed.js, newer copy from the morning snapshot) and dashboard data ----------
  const CAT = new Map();
  let catAt = "";
  let D = {};
  let live = 0; // bumps when dashboard data or the catalog change, so cards that show them re-render
  function loadCatalog() {
    CAT.clear();
    for (const r of SEED.resources || []) CAT.set(r.id, r);
    catAt = SEED.generated_at || "";
    const snapRes = D.snap?.resources;
    const t = (x) => Date.parse(x || "") || 0;
    if (Array.isArray(snapRes) && t(D.snap.resources_at) >= t(catAt)) {
      for (const r of snapRes) if (r && typeof r.id === "string") CAT.set(r.id, { ...(CAT.get(r.id) || {}), ...r });
      catAt = D.snap.resources_at || catAt;
    }
  }
  function onDash() {
    D = (window.LBDash && window.LBDash.data) || {};
    loadCatalog();
    for (const t of D.snap?.local_tools || []) if (t?.key && !ENV.localTools[t.key]?.live) ENV.localTools[t.key] = { ok: t.ok, at: t.at, from: "snapshot" };
    live++;
    if (B) renderAll();
  }
  window.addEventListener("lb:data", onDash);

  // ---------- the board model ----------
  const emptyBoard = () => ({ schema: SCHEMA, id: "main", rev: 0, savedAt: null, cards: {}, edges: {}, frames: {}, templates: {}, home: null, dock: [], known: [], dismissed: [] });
  const ID_RE = /^[A-Za-z0-9_-]{1,80}$/;
  const S = (v, max) => (typeof v === "string" ? v.slice(0, max) : "");
  const N = (v, d, lo, hi) => { v = Number(v); return Number.isFinite(v) ? clamp(v, lo, hi) : d; };
  const W = 200000;
  function cleanList(items, max = 60) {
    return (Array.isArray(items) ? items : []).slice(0, max).filter((x) => x && typeof x === "object").map((x, i) => ({
      id: ID_RE.test(x.id) ? x.id : "i" + i + Math.random().toString(36).slice(2, 6), text: S(x.text, 300), done: !!x.done }));
  }
  function cleanMedia(m) {
    if (!m || typeof m !== "object") return null;
    const out = {};
    if (typeof m.src === "string") { const s = safeHref(m.src) || safePath(m.src); if (s) out.src = s; }
    if (typeof m.asset === "string" && /^[0-9a-f]{32}$/.test(m.asset)) out.asset = m.asset;
    if (typeof m.url === "string" && safeHref(m.url)) out.url = safeHref(m.url);
    if (["image", "video", "audio", "pdf", "html", "text"].includes(m.kind)) out.kind = m.kind;
    if (Array.isArray(m.files)) out.files = m.files.map((f) => safeHref(f) || safePath(f)).filter(Boolean).slice(0, 24);
    return Object.keys(out).length ? out : null;
  }
  function cleanCard(c) {
    if (!c || typeof c !== "object" || !ID_RE.test(c.id)) return null;
    const type = TYPES[c.type] ? c.type : "note";
    const out = { id: c.id, type, title: S(c.title, 300), desc: S(c.desc, 8000), tags: (Array.isArray(c.tags) ? c.tags : []).map((t) => S(t, 40).trim()).filter(Boolean).slice(0, 12),
      x: N(c.x, 0, -W, W), y: N(c.y, 0, -W, W), w: N(c.w, TYPES[type].w, 120, 2400), h: N(c.h, TYPES[type].h, 80, 2400), z: N(c.z, 0, 0, 1e9) };
    if (typeof c.ref === "string" && /^[a-z]+:[^\s]{1,160}$/.test(c.ref)) out.ref = c.ref;
    if (c.url) { const u = safeHref(c.url) || safePath(c.url); if (u) out.url = u; }
    if (STATUS[c.status]) out.status = c.status;
    if (PRIO[c.priority]) out.priority = c.priority;
    if (typeof c.due === "string" && /^\d{4}-\d{2}-\d{2}$/.test(c.due)) out.due = c.due;
    if (Array.isArray(c.checklist) && c.checklist.length) out.checklist = cleanList(c.checklist);
    if (COLORS[c.color] && c.color !== "plain") out.color = c.color;
    if (typeof c.prompt === "string" && c.prompt) out.prompt = S(c.prompt, 8000);
    if (typeof c.metric === "string" && /^[a-z_]{1,40}$/.test(c.metric)) out.metric = c.metric;
    if (typeof c.view === "string" && VIEW_NAMES[c.view]) out.view = c.view;
    if (typeof c.target === "string" && c.target) out.target = S(c.target, 60);
    if (typeof c.project === "string" && ID_RE.test(c.project)) out.project = c.project;
    const m = cleanMedia(c.media); if (m) out.media = m;
    for (const k of ["createdAt", "updatedAt"]) if (typeof c[k] === "string" && c[k].length < 40) out[k] = c[k];
    return out;
  }
  function cleanFrame(f) {
    if (!f || typeof f !== "object" || !ID_RE.test(f.id)) return null;
    const out = { id: f.id, title: S(f.title, 120) || "אזור", x: N(f.x, 0, -W, W), y: N(f.y, 0, -W, W), w: N(f.w, 900, 240, 20000), h: N(f.h, 600, 160, 20000) };
    if (typeof f.area === "string" && AREAS[f.area]) out.area = f.area;
    return out;
  }
  function cleanEdge(e, cards) {
    if (!e || typeof e !== "object" || !ID_RE.test(e.id) || !cards[e.from] || !cards[e.to] || e.from === e.to) return null;
    return { id: e.id, from: e.from, to: e.to, label: S(e.label, 80), kind: e.kind === "dep" ? "dep" : "manual" };
  }
  function cleanTemplate(t) {
    if (!t || typeof t !== "object" || !ID_RE.test(t.id)) return null;
    const cards = (Array.isArray(t.cards) ? t.cards : []).slice(0, 80).filter((c) => c && typeof c === "object").map((c) => {
      const cc = cleanCard({ ...c, id: ID_RE.test(c?.k) ? c.k : "x" }); if (!cc) return null;
      delete cc.id; cc.k = ID_RE.test(c.k) ? c.k : uid("k"); return cc;
    }).filter(Boolean);
    const ks = new Set(cards.map((c) => c.k));
    const edges = (Array.isArray(t.edges) ? t.edges : []).filter((e) => e && ks.has(e.from) && ks.has(e.to) && e.from !== e.to).map((e) => ({ from: e.from, to: e.to, label: S(e.label, 80) }));
    const out = { id: t.id, title: S(t.title, 120) || "תבנית", desc: S(t.desc, 600), tags: (Array.isArray(t.tags) ? t.tags : []).map((x) => S(x, 40)).filter(Boolean).slice(0, 8), cards, edges,
      createdAt: S(t.createdAt, 40) };
    if (t.frame && typeof t.frame === "object") out.frame = { title: S(t.frame.title, 120), w: N(t.frame.w, 900, 240, 20000), h: N(t.frame.h, 600, 160, 20000), area: AREAS[t.frame.area] ? t.frame.area : undefined };
    if (typeof t.project === "string" && ks.has(t.project)) out.project = t.project;
    return out;
  }
  function cleanBoard(raw) {
    const b = emptyBoard();
    let dropped = 0;
    if (!raw || typeof raw !== "object") return { board: b, dropped: 1 };
    b.rev = N(raw.rev, 0, 0, 1e12); b.savedAt = S(raw.savedAt, 40) || null;
    for (const c of Object.values(raw.cards || {})) { const x = cleanCard(c); if (x) b.cards[x.id] = x; else dropped++; }
    for (const f of Object.values(raw.frames || {})) { const x = cleanFrame(f); if (x) b.frames[x.id] = x; else dropped++; }
    for (const e of Object.values(raw.edges || {})) { const x = cleanEdge(e, b.cards); if (x) b.edges[x.id] = x; else dropped++; }
    for (const t of Object.values(raw.templates || {})) { const x = cleanTemplate(t); if (x) b.templates[x.id] = x; else dropped++; }
    for (const c of Object.values(b.cards)) if (c.project && !b.cards[c.project]) delete c.project;
    if (raw.home && typeof raw.home === "object") b.home = { x: N(raw.home.x, 0, -W, W), y: N(raw.home.y, 0, -W, W), w: N(raw.home.w, 1200, 100, 40000), h: N(raw.home.h, 800, 100, 40000) };
    b.dock = (Array.isArray(raw.dock) ? raw.dock : []).filter((d) => d && ID_RE.test(d.id) && typeof d.ref === "string" && d.ref.length < 200).map((d) => ({ id: d.id, ref: d.ref })).slice(0, 60);
    b.known = (Array.isArray(raw.known) ? raw.known : []).filter((x) => typeof x === "string" && x.length < 200).slice(0, 5000);
    b.dismissed = (Array.isArray(raw.dismissed) ? raw.dismissed : []).filter((x) => typeof x === "string" && x.length < 200).slice(0, 5000);
    return { board: b, dropped };
  }
  // migrations: MIGRATIONS[n] turns a schema-n board into schema n+1; the raw board is kept as a local backup first
  const MIGRATIONS = {};
  function migrate(raw) {
    const from = Number(raw?.schema) || 1;
    if (from > SCHEMA) return { ...cleanBoard(raw), tooNew: true, from };
    let b = raw, migrated = false;
    for (let s = from; s < SCHEMA; s++) { if (!MIGRATIONS[s]) break; b = MIGRATIONS[s](b); migrated = true; }
    return { ...cleanBoard(b), migrated, from };
  }
  function boardFromSeed() {
    const s = SEED.seed || {}, b = emptyBoard(), t = nowIso();
    for (const f of s.frames || []) { const x = cleanFrame(f); if (x) b.frames[x.id] = x; }
    for (const c of s.cards || []) { const x = cleanCard({ ...c, createdAt: t }); if (x) b.cards[x.id] = x; }
    for (const e of s.edges || []) { const x = cleanEdge(e, b.cards); if (x) b.edges[x.id] = x; }
    b.home = s.home || null;
    b.dock = (s.dock || []).map((ref) => ({ id: "d-" + ref.replace(/[^A-Za-z0-9_-]/g, "-"), ref }));
    b.known = [...(s.known || [])];
    return b;
  }

  // ---------- state ----------
  let B = null;
  const U = { sel: new Set(), selEdge: null, panel: null, tool: "select", mode: "canvas", view: { tx: 0, ty: 0, z: 1 }, filters: { types: new Set(), status: new Set(), tag: "", project: "", source: "" },
    connectFrom: null, editing: null, space: false, visible: false, dockQ: "", tplQ: "", newOpen: false };
  let zTop = 1;

  // ---------- history: entity diffs, coalesced for typing ----------
  const H = { past: [], future: [], base: new Map() };
  function entityMap() {
    const m = new Map();
    for (const [k, coll] of [["c", B.cards], ["e", B.edges], ["f", B.frames], ["t", B.templates]]) for (const id in coll) m.set(k + ":" + id, JSON.stringify(coll[id]));
    for (const k of ["home", "dock", "known", "dismissed"]) m.set("m:" + k, JSON.stringify(B[k]));
    return m;
  }
  function setEntity(key, json) {
    const i = key.indexOf(":"), kind = key.slice(0, i), id = key.slice(i + 1);
    if (kind === "m") { B[id] = json == null ? emptyBoard()[id] : JSON.parse(json); return; }
    const coll = { c: B.cards, e: B.edges, f: B.frames, t: B.templates }[kind];
    if (json == null) delete coll[id]; else coll[id] = JSON.parse(json);
  }
  function commit(label, merge) {
    const now = entityMap(), diff = [];
    for (const k of new Set([...H.base.keys(), ...now.keys()])) { const a = H.base.get(k), b = now.get(k); if (a !== b) diff.push([k, a, b]); }
    if (!diff.length) return false;
    const last = H.past[H.past.length - 1];
    if (merge && last && last.merge === merge && Date.now() - last.at < 2500) {
      const before = new Map(last.diff.map(([k, a]) => [k, a]));
      for (const [k, a] of diff) if (!before.has(k)) before.set(k, a);
      last.diff = [...before].map(([k, a]) => [k, a, now.get(k)]).filter(([, a, b]) => a !== b);
      last.at = Date.now();
    } else {
      H.past.push({ label, diff, merge: merge || null, at: Date.now() });
      if (H.past.length > 200) H.past.shift();
    }
    H.future = [];
    H.base = now;
    markDirty();
    return true;
  }
  function undo() {
    const h = H.past.pop(); if (!h) return;
    for (const [k, a] of h.diff) setEntity(k, a);
    H.future.push(h); H.base = entityMap(); tidySelection(); markDirty(); renderAll({ panel: true });
    toast(`בוטל: ${h.label}`);
  }
  function redo() {
    const h = H.future.pop(); if (!h) return;
    for (const [k, , b] of h.diff) setEntity(k, b);
    H.past.push(h); H.base = entityMap(); tidySelection(); markDirty(); renderAll({ panel: true });
    toast(`חזר: ${h.label}`);
  }
  function tidySelection() {
    for (const id of [...U.sel]) if (!B.cards[id] && !B.frames[id]) U.sel.delete(id);
    if (U.selEdge && !B.edges[U.selEdge]) U.selEdge = null;
    if (U.panel && !({ card: B.cards, frame: B.frames, edge: B.edges }[U.panel.kind] || {})[U.panel.id]) U.panel = null;
  }

  // ---------- stores ----------
  function splitBoard(b) {
    const meta = { schema: b.schema, id: b.id, home: b.home, dock: b.dock, known: b.known, dismissed: b.dismissed, savedAt: b.savedAt };
    const items = [];
    for (const v of Object.values(b.frames)) items.push({ k: "f", v });
    for (const v of Object.values(b.cards)) items.push({ k: "c", v });
    for (const v of Object.values(b.edges)) items.push({ k: "e", v });
    for (const v of Object.values(b.templates)) items.push({ k: "t", v });
    const parts = [];
    let cur = { meta, items: [] }, size = bytes(JSON.stringify(meta)) + 200;
    for (const it of items) {
      const s = bytes(JSON.stringify(it)) + 2;
      if (s > PART_LIMIT) throw Object.assign(new Error("פריט אחד גדול מדי לשמירה"), { code: "too_big" });
      if (size + s > PART_LIMIT && cur.items.length) { parts.push(cur); cur = { items: [] }; size = 200; }
      cur.items.push(it); size += s;
    }
    parts.push(cur);
    return parts;
  }
  function joinParts(parts) {
    const raw = { ...(parts[0].meta || {}), cards: {}, edges: {}, frames: {}, templates: {} };
    for (const p of parts) for (const it of p.items || []) {
      const coll = { c: raw.cards, e: raw.edges, f: raw.frames, t: raw.templates }[it.k];
      if (coll && it.v && it.v.id) coll[it.v.id] = it.v;
    }
    return raw;
  }
  class LocalStore {
    constructor(scope) { this.kind = "local"; this.key = `${KEY}:${scope}`; this.scope = scope; }
    async load() {
      const s = LS.get(this.key);
      if (s == null) return { board: null };
      try { return { board: JSON.parse(s) }; } catch { return { board: null, error: "corrupt" }; }
    }
    async save(b, rev, base) {
      try { const cur = JSON.parse(LS.get(this.key) || "null"); if (cur && cur.tab && cur.tab !== TAB && (Number(cur.rev) || 0) > base) throw Object.assign(new Error("remote"), { code: "remote", head: { rev: cur.rev, tab: cur.tab } }); } catch (e) { if (e?.code === "remote") throw e; }
      const s = JSON.stringify({ ...b, rev, tab: TAB });
      LS.set(this.key, s);
      if (LS.get(this.key)?.length !== s.length) throw Object.assign(new Error("השמירה בדפדפן לא אומתה"), { code: "verify" });
      return { rev };
    }
    watch(cb) {
      window.addEventListener("storage", (e) => {
        if (e.key !== this.key || !e.newValue) return;
        try { const b = JSON.parse(e.newValue); cb({ rev: b.rev, tab: b.tab || "other", board: b }); } catch {}
      });
    }
  }
  // The artifact database: boards/main is the head {rev, tab, slot, n, prev, prevN}; the board itself is in
  // boards/main/parts/<slot>-<i>, at most ~180 KB each, where every save writes a new slot name (r<rev><tab>), so a
  // save never overwrites the parts of the live version or of another tab's save. The head moves last; the version
  // before it stays readable as the fallback, and anything older is deleted after the next save.
  class DbStore {
    constructor(db) { this.kind = "db"; this.db = db; this.head = db.doc("boards/main"); this.parts = this.head.collection("parts"); }
    part(slot, i) { return this.parts.doc(`${slot}-${i}`); }
    async load() {
      const h = await withRetry(() => this.head.get());
      if (!h.exists) return { board: null };
      const hd = h.data();
      // Only a missing part or a part from another save (rev or tab mismatch) makes a version unreadable; a read
      // error (unavailable, rate limit) is retried once and then reported, so a passing hiccup never looks like a
      // broken save and never sends the page to the older version.
      for (const [slot, n, check] of [[hd.slot, hd.n, hd], [hd.prev, hd.prevN, null]]) {
        if (!slot) continue;
        const b = await this.readSlot(slot, n, check);
        if (b && slot !== hd.slot) this.broken = { slot: hd.slot, n: hd.n }; // skipped as the fallback on the next save
        if (b) return { board: b, head: hd, recovered: slot !== hd.slot };
      }
      return { board: null, error: "unreadable", head: hd };
    }
    async readSlot(slot, n, hd) {
      const all = [];
      for (let i = 0; i < (n || 1); i++) {
        const p = await withRetry(() => this.part(slot, i).get());
        if (!p.exists) return null;
        const d = p.data();
        if (all.length && (d.rev !== all[0].rev || d.tab !== all[0].tab)) return null;
        all.push(d);
      }
      if (hd && (all[0].rev !== hd.rev || all[0].tab !== hd.tab)) return null;
      if (all[0].n !== all.length) return null;
      return { ...joinParts(all), rev: all[0].rev };
    }
    // Takes the head's short lease (acquire) so tabs that all use it never interleave; refuses to save over a
    // version another tab or device saved after `base` (throws "remote": the page asks which one to keep).
    async save(b, rev, base) {
      if (typeof this.head.acquire === "function") {
        const l = await this.head.acquire({ holder: TAB, ttlMs: 4000 }).catch(() => null);
        if (l && l.acquired === false) throw Object.assign(new Error("another tab is saving"), { code: "busy" });
      }
      const remoteErr = (h) => Object.assign(new Error("remote"), { code: "remote", head: h });
      const h0 = await this.head.get(), cur = h0.exists ? h0.data() : null;
      if (cur && cur.tab !== TAB && (Number(cur.rev) || 0) > base) throw remoteErr(cur);
      const parts = splitBoard(b), slot = `r${rev}${TAB}`, n = parts.length;
      let total = 0;
      for (let i = 0; i < n; i++) {
        const body = { rev, tab: TAB, i, n, ...parts[i] };
        total += bytes(JSON.stringify(body));
        await withRetry(() => this.part(slot, i).set(body));
      }
      const h1 = await this.head.get(), now = h1.exists ? h1.data() : null;
      if ((now && !cur) || (now && cur && (now.rev !== cur.rev || now.tab !== cur.tab))) throw remoteErr(now);
      // the fallback is the version this one replaces, unless that one was unreadable when the page loaded
      const skip = this.broken && cur?.slot === this.broken.slot;
      const prev = skip ? cur.prev : cur?.slot, prevN = skip ? cur.prevN : cur?.n;
      await withRetry(() => this.head.set({ schema: SCHEMA, rev, tab: TAB, slot, n, prev: prev || null, prevN: prevN || 0, savedAt: b.savedAt, bytes: total }));
      // no longer referenced: the version before the fallback (a skipped broken version is left to the daily sweep)
      const drop = !skip && cur?.prev && cur.prev !== slot ? [{ slot: cur.prev, n: cur.prevN }] : [];
      for (const v of drop) for (let i = 0; i < (v.n || 0); i++) this.part(v.slot, i).delete().catch(() => {});
      this.broken = null;
      return { rev, bytes: total, parts: n };
    }
    // Parts no head points at (a save that lost a conflict or failed half way), older than the live version.
    // Run at most once a day per device; a part newer than the head may be another tab's save in progress.
    async sweep() {
      const k = KEY + ":sweep";
      if (Date.now() - (Number(LS.get(k)) || 0) < 864e5) return;
      try { LS.set(k, String(Date.now())); } catch {}
      const h = await this.head.get(); if (!h.exists) return;
      const hd = h.data(), keep = new Set([hd.slot, hd.prev].filter(Boolean));
      const q = await this.parts.get();
      for (const d of q.docs) {
        const slot = d.id.replace(/-\d+$/, ""), body = d.data() || {};
        if (!keep.has(slot) && (Number(body.rev) || 0) < hd.rev) await this.parts.doc(d.id).delete().catch(() => {});
      }
    }
    watch(cb) {
      this.head.onSnapshot((s) => { if (s.exists) cb(s.data()); }, (e) => { if (e?.code === "revoked") setSave("error", "הגישה ללוח בוטלה"); });
    }
  }
  async function withRetry(fn) {
    try { return await fn(); } catch (e) {
      if (e?.code !== "unavailable" && e?.code !== "resource_exhausted") throw e;
      await new Promise((r) => setTimeout(r, 400 + Math.random() * 600));
      return fn();
    }
  }

  // ---------- saving ----------
  let store = null, dirty = false, saving = false, again = false, saveTimer = 0, readOnly = false;
  const SAVE = { state: "loading", at: null, error: "", rev: 0 };
  function markDirty() {
    if (!B) return;
    dirty = true;
    if (readOnly) { setSave("ro"); return; }
    setSave("pending");
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flush, 700);
  }
  async function flush() {
    clearTimeout(saveTimer);
    if (!store || readOnly || !dirty) return;
    if (remote) { setSave("pending"); return; } // another tab or device saved: wait for the choice in the banner
    if (saving) { again = true; return; }
    saving = true; dirty = false;
    setSave("saving");
    const base = B.rev || 0, rev = base + 1, savedAt = nowIso();
    try {
      await store.save({ ...B, savedAt }, rev, base);
      B.rev = rev; B.savedAt = savedAt;
      setSave("saved");
      backupMaybe();
    } catch (e) {
      dirty = true;
      const code = e?.code;
      if (code === "remote") { remote = { rev: Number(e.head?.rev) || 0, tab: e.head?.tab }; setSave("pending"); renderBanner(); return; }
      if (code === "busy") { setSave("pending"); clearTimeout(saveTimer); saveTimer = setTimeout(flush, 1500); return; }
      const msg = code === "quota_exceeded" || e?.name === "QuotaExceededError" ? "אין מקום: הלוח גדול מדי לשמירה כאן. כדאי לייצא גיבוי"
        : code === "invalid_argument" ? "אין הרשאה לשמור בלוח הזה" : code === "too_big" ? e.message : code === "resource_exhausted" ? "יותר מדי שמירות ברצף, מנסה שוב בעוד רגע"
        : e?.message ? String(e.message).slice(0, 120) : "שגיאה לא ידועה";
      setSave("error", msg);
      if (code === "invalid_argument") { readOnly = true; setSave("ro", msg); }
      else if (code === "resource_exhausted" || code === "unavailable") { clearTimeout(saveTimer); saveTimer = setTimeout(flush, 5000); }
    } finally {
      saving = false;
      if (again) { again = false; if (dirty) flush(); }
    }
  }
  function setSave(state, error) {
    SAVE.state = state; SAVE.error = error || "";
    if (state === "saved") SAVE.at = new Date();
    renderSave();
  }
  window.addEventListener("beforeunload", (e) => {
    if (!dirty && !saving) return;
    if (store?.kind === "local" && !readOnly && !remote) { try { flushLocalNow(); return; } catch {} }
    e.preventDefault(); e.returnValue = "";
  });
  function flushLocalNow() { if (remote) return; const rev = (B.rev || 0) + 1; const s = JSON.stringify({ ...B, rev, tab: TAB, savedAt: nowIso() }); LS.set(store.key, s); B.rev = rev; dirty = false; }
  function backupKey() { return `${KEY}:backups:${store?.kind === "db" ? "artifact" : store?.scope || "page"}`; }
  function backups() { try { return JSON.parse(LS.get(backupKey()) || "[]"); } catch { return []; } }
  function backupNow(reason) {
    try {
      const list = backups();
      list.unshift({ at: nowIso(), reason: reason || "", rev: B.rev, cards: Object.keys(B.cards).length, json: JSON.stringify(B) });
      while (list.length > 6) list.pop();
      let s = JSON.stringify(list);
      while (s.length > 2.5e6 && list.length > 1) { list.pop(); s = JSON.stringify(list); }
      LS.set(backupKey(), s);
      return true;
    } catch { return false; }
  }
  function backupMaybe() { const l = backups(); if (!l.length || Date.now() - new Date(l[0].at).getTime() > 10 * 6e4) backupNow("אוטומטי"); }

  // remote changes (another tab or device saved)
  let remote = null;
  const editingNow = () => !!(U.editing || G || el.bd.querySelector(".bc-edit, .bl-lab input"));
  const busyHere = () => dirty || saving || editingNow();
  function onRemote(info) {
    if (info.tab === TAB) return;
    if (info.rev && B && info.rev <= B.rev && !info.board) return;
    remote = info;
    if (!busyHere()) reloadRemote();
    else renderBanner();
  }
  async function reloadRemote(force) {
    const info = remote;
    let raw = info?.board, rev = Number(raw?.rev) || 0;
    if (!raw) {
      const r = await store.load().catch(() => null);
      raw = r?.board;
      rev = r?.recovered ? Number(r.head?.rev) || 0 : Number(raw?.rev) || 0; // after a fallback, supersede the broken head
    }
    if (!raw || (!force && busyHere())) { renderBanner(); return; } // edits arrived meanwhile: ask instead
    remote = null;
    const m = migrate(raw);
    B = m.board; B.rev = rev || info?.rev || B.rev;
    G = null; U.editing = null;
    H.past = []; H.future = []; H.base = entityMap(); tidySelection(); dirty = false;
    setSave("saved"); renderAll({ panel: true }); renderBanner();
    toast("הלוח עודכן משינוי שנשמר במקום אחר");
  }

  // ---------- geometry ----------
  const rectOf = (o) => ({ x: o.x, y: o.y, w: o.w, h: o.h });
  const inside = (r, f) => { const cx = r.x + r.w / 2, cy = r.y + r.h / 2; return cx >= f.x && cx <= f.x + f.w && cy >= f.y && cy <= f.y + f.h; };
  const contains = (f, r) => r.x >= f.x && r.y >= f.y && r.x + r.w <= f.x + f.w && r.y + r.h <= f.y + f.h;
  const hits = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  function frameOf(c) {
    let best = null;
    for (const f of Object.values(B.frames)) if (inside(c, f) && (!best || f.w * f.h < best.w * best.h)) best = f;
    return best;
  }
  function frameMembers(f) {
    const cards = Object.values(B.cards).filter((c) => frameOf(c)?.id === f.id || (inside(c, f) && contains(f, c)));
    const frames = Object.values(B.frames).filter((g) => g.id !== f.id && contains(f, g) && g.w * g.h < f.w * f.h);
    return { cards, frames };
  }
  function bbox(list) {
    if (!list.length) return null;
    let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    for (const r of list) { x1 = Math.min(x1, r.x); y1 = Math.min(y1, r.y); x2 = Math.max(x2, r.x + r.w); y2 = Math.max(y2, r.y + r.h); }
    return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 };
  }
  function anchor(r, tx, ty) {
    const cx = r.x + r.w / 2, cy = r.y + r.h / 2, dx = tx - cx, dy = ty - cy;
    if (!dx && !dy) return { x: cx, y: r.y, nx: 0, ny: -1 };
    const sx = (r.w / 2) / Math.abs(dx || 1e-9), sy = (r.h / 2) / Math.abs(dy || 1e-9), s = Math.min(sx, sy);
    const n = sx < sy ? [Math.sign(dx), 0] : [0, Math.sign(dy)];
    return { x: cx + dx * s, y: cy + dy * s, nx: n[0], ny: n[1] };
  }
  function edgeGeom(a, b) {
    const ca = { x: a.x + a.w / 2, y: a.y + a.h / 2 }, cb = { x: b.x + b.w / 2, y: b.y + b.h / 2 };
    const p1 = anchor(a, cb.x, cb.y), p2 = anchor(b, ca.x, ca.y);
    const dist = Math.hypot(p2.x - p1.x, p2.y - p1.y), k = clamp(dist * 0.4, 24, 160);
    const c1 = { x: p1.x + p1.nx * k, y: p1.y + p1.ny * k }, c2 = { x: p2.x + p2.nx * k, y: p2.y + p2.ny * k };
    const mid = { x: (p1.x + 3 * c1.x + 3 * c2.x + p2.x) / 8, y: (p1.y + 3 * c1.y + 3 * c2.y + p2.y) / 8 };
    return { d: `M${p1.x.toFixed(1)},${p1.y.toFixed(1)} C${c1.x.toFixed(1)},${c1.y.toFixed(1)} ${c2.x.toFixed(1)},${c2.y.toFixed(1)} ${p2.x.toFixed(1)},${p2.y.toFixed(1)}`, mid };
  }
  // the nearest spot around (x, y) where a w x h card overlaps no other card (a spiral of grid steps)
  function freeSpot(x, y, w, h) {
    const cards = Object.values(B.cards), m = 16;
    const free = (px, py) => !cards.some((c) => hits({ x: px - m, y: py - m, w: w + 2 * m, h: h + 2 * m }, c));
    const sn = (v) => (prefs.snap ? snapTo(v) : v);
    if (free(sn(x), sn(y))) return { x: sn(x), y: sn(y) };
    const step = 40;
    for (let r = 1; r < 40; r++) for (let i = -r; i <= r; i++) for (const [dx, dy] of [[i, -r], [i, r], [-r, i], [r, i]]) {
      const px = sn(x + dx * step), py = sn(y + dy * step);
      if (free(px, py)) return { x: px, y: py };
    }
    return { x: sn(x), y: sn(y) };
  }
  // top-left corner for a w x h block (a new project area, a duplicate) near the centre point (cx, cy) that overlaps
  // no frame and no card; spirals outwards, else goes to the left of everything (the board grows leftwards in RTL)
  function freeArea(w, h, cx, cy, skip) {
    const items = [...Object.values(B.frames), ...Object.values(B.cards)].filter((o) => !skip?.has(o.id)), m = 60;
    const free = (x, y) => !items.some((o) => hits({ x: x - m, y: y - m, w: w + 2 * m, h: h + 2 * m }, o));
    const sn = (v) => (prefs.snap ? snapTo(v) : v);
    const x0 = cx - w / 2, y0 = cy - h / 2;
    if (free(sn(x0), sn(y0))) return { x: sn(x0), y: sn(y0) };
    const step = 160;
    for (let r = 1; r < 36; r++) for (let i = -r; i <= r; i++) for (const [dx, dy] of [[-r, i], [i, r], [i, -r], [r, i]]) {
      const x = sn(x0 + dx * step), y = sn(y0 + dy * step);
      if (free(x, y)) return { x, y };
    }
    const all = bbox(items) || { x: 0, y: 0, w: 0, h: 0 };
    return { x: sn(all.x - w - 160), y: sn(all.y) };
  }

  // ---------- skeleton ----------
  ROOT.innerHTML = `
  <div class="bd" id="bd" data-mode="canvas">
    <div class="bd-bar" role="toolbar" aria-label="כלי הלוח">
      <button class="bd-ib" type="button" data-a="dock" aria-label="מגירת הכלים" title="מגירת הכלים" aria-pressed="true">${I("nav")}</button>
      <span class="bd-sep"></span>
      <button class="bd-ib bd-canvas-only" type="button" data-a="tool-select" aria-label="בחירה (V)" title="בחירה · V" aria-pressed="true">${I("cursor")}</button>
      <button class="bd-ib bd-canvas-only" type="button" data-a="tool-hand" aria-label="הזזת הלוח (H)" title="הזזת הלוח · H, או רווח וגרירה" aria-pressed="false">${I("hand")}</button>
      <button class="bd-btn is-primary" type="button" data-a="add" aria-haspopup="menu" title="הוספת כרטיס">${I("plus")}<span>הוספה</span></button>
      <button class="bd-ib" type="button" data-a="undo" aria-label="ביטול (Cmd+Z)" title="ביטול · Cmd+Z">${I("undo")}</button>
      <button class="bd-ib" type="button" data-a="redo" aria-label="חזרה (Shift+Cmd+Z)" title="חזרה · Shift+Cmd+Z">${I("redo")}</button>
      <span class="bd-sep"></span>
      <div class="bd-search">${I("search")}<input class="lb-input" id="bd-q" type="search" autocomplete="off" placeholder="חיפוש בלוח, בכלים ובתבניות" aria-label="חיפוש בלוח" aria-controls="bd-results" aria-expanded="false"><kbd>/</kbd></div>
      <button class="bd-ib" type="button" data-a="filters" aria-label="סינון" title="סינון לפי סוג, מצב, תגית ופרויקט">${I("filter")}<span class="bd-badge" id="bd-fcount" hidden></span></button>
      <button class="bd-ib bd-canvas-only bd-hide-sm" type="button" data-a="deps" aria-label="תלויות מהרישום" title="תלויות בין הרכיבים (lumebook.json)" aria-pressed="true">${I("deps")}</button>
      <button class="bd-ib bd-canvas-only bd-hide-sm" type="button" data-a="snap" aria-label="הצמדה לרשת (G)" title="הצמדה לרשת · G" aria-pressed="true">${I("grid")}</button>
      <span class="bd-sep"></span>
      <div class="lb-segmented" role="group" aria-label="תצוגה"><button type="button" data-a="mode-canvas" aria-pressed="true">לוח</button><button type="button" data-a="mode-list" aria-pressed="false">רשימה</button></div>
      <button class="lb-chip bd-save" type="button" id="bd-save" data-a="save-info" aria-live="polite">טוען את הלוח…</button>
      <button class="bd-ib" type="button" data-a="more" aria-label="עוד" title="ייצוא, ייבוא, גיבויים ותצוגת בית" aria-haspopup="menu">${I("more")}</button>
      <button class="bd-ib" type="button" data-a="keys" aria-label="קיצורי מקלדת (?)" title="קיצורי מקלדת · ?">${I("help")}</button>
    </div>
    <div class="bd-body">
      <aside class="bd-dock" id="bd-dock" data-open="true" aria-label="מגירת הכלים">
        <div class="bd-dock-tabs" role="tablist">
          <button class="bd-tab" type="button" role="tab" data-tab="tools" title="כלים ומקורות">${I("tool")}<span class="bd-tab-label">כלים</span></button>
          <button class="bd-tab" type="button" role="tab" data-tab="tpl" title="תבניות">${I("tpl")}<span class="bd-tab-label">תבניות</span></button>
          <button class="bd-tab" type="button" role="tab" data-tab="nav" title="אזורים">${I("frame")}<span class="bd-tab-label">אזורים</span></button>
          <button class="bd-tab" type="button" role="tab" data-tab="new" title="חדש בפרויקט">${I("spark")}<span class="bd-tab-label">חדש</span><span class="bd-badge" id="bd-newcount" hidden></span></button>
        </div>
        <div class="bd-dock-main" id="bd-dock-main" role="tabpanel"></div>
      </aside>
      <div class="bd-stage" id="bd-stage" tabindex="0" aria-label="לוח העבודה. חיצים מזיזים כרטיס מסומן, Enter פותח פרטים, ? מציג קיצורים">
        <div class="bd-world" id="bd-world">
          <div class="bd-layer" id="bd-frames"></div>
          <svg class="bd-edges" id="bd-edges" aria-hidden="true"><defs>
            <marker id="bd-ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="var(--text-3)"/></marker>
            <marker id="bd-ar-hot" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="var(--tint)"/></marker>
          </defs><g id="bd-edge-g"></g><path class="be-temp" id="bd-temp" d="" /></svg>
          <div class="bd-layer bd-labels" id="bd-labels"></div>
          <div class="bd-layer" id="bd-cards"></div>
          <div class="bd-handles" id="bd-handles"></div>
        </div>
        <div class="bd-marquee" id="bd-marquee" hidden></div>
        <div class="bd-ctx" id="bd-ctx" hidden></div>
        <div class="bd-banner" id="bd-banner" hidden></div>
        <div class="bd-zoom" role="group" aria-label="זום">
          <button class="bd-ib" type="button" data-a="zoom-out" aria-label="הקטנה (-)" title="הקטנה · −">${I("minus")}</button>
          <output id="bd-zoomv">100%</output>
          <button class="bd-ib" type="button" data-a="zoom-in" aria-label="הגדלה (+)" title="הגדלה · +">${I("plus")}</button>
          <button class="bd-ib" type="button" data-a="fit" aria-label="כל הלוח (Shift+1)" title="כל הלוח · Shift+1">${I("fit")}</button>
          <button class="bd-ib" type="button" data-a="home" aria-label="תצוגת בית (Shift+H)" title="תצוגת בית · Shift+H">${I("home")}</button>
        </div>
      </div>
      <div class="bd-list" id="bd-list" hidden></div>
      <aside class="bd-panel" id="bd-panel" hidden aria-label="פרטים"></aside>
    </div>
    <div class="bd-toasts" id="bd-toasts" aria-live="polite"></div>
  </div>`;
  const $ = (id) => document.getElementById(id);
  const el = { bd: $("bd"), stage: $("bd-stage"), world: $("bd-world"), frames: $("bd-frames"), edgeG: $("bd-edge-g"), temp: $("bd-temp"), labels: $("bd-labels"),
    cards: $("bd-cards"), handles: $("bd-handles"), marquee: $("bd-marquee"), ctx: $("bd-ctx"), banner: $("bd-banner"), zoomv: $("bd-zoomv"), list: $("bd-list"),
    panel: $("bd-panel"), dock: $("bd-dock"), dockMain: $("bd-dock-main"), q: $("bd-q"), save: $("bd-save"), toasts: $("bd-toasts") };

  // ---------- view transform ----------
  function applyView() {
    const { tx, ty, z } = U.view;
    el.world.style.transform = `translate(${tx}px, ${ty}px) scale(${z})`;
    el.world.style.setProperty("--inv", String(1 / z));
    el.world.style.setProperty("--fz", String(Math.max(1, 0.55 / z)));
    el.stage.style.setProperty("--grid", `${GRID * z}px`);
    el.stage.style.setProperty("--gx", `${tx}px`); el.stage.style.setProperty("--gy", `${ty}px`);
    el.world.classList.toggle("is-far", z < 0.42);
    el.zoomv.textContent = `${Math.round(z * 100)}%`;
    renderCtx();
    if (U.viewSet) { prefs.view = { ...U.view }; savePrefs(); }
  }
  const stageRect = () => el.stage.getBoundingClientRect();
  function toWorld(cx, cy) { const r = stageRect(); return { x: (cx - r.left - U.view.tx) / U.view.z, y: (cy - r.top - U.view.ty) / U.view.z }; }
  function toScreen(x, y) { return { x: x * U.view.z + U.view.tx, y: y * U.view.z + U.view.ty }; }
  function zoomAt(sx, sy, factor) {
    const z = U.view.z, nz = clamp(z * factor, 0.08, 2.5);
    U.view.tx = sx - (sx - U.view.tx) * (nz / z); U.view.ty = sy - (sy - U.view.ty) * (nz / z); U.view.z = nz;
    applyView();
  }
  function zoomBy(f) { const r = stageRect(); zoomAt(r.width / 2, r.height / 2, f); }
  function fitRect(r, maxZ = 1.1, pad = 48) {
    if (!r) return;
    const s = stageRect(); if (!s.width || !s.height) return;
    const z = clamp(Math.min((s.width - pad * 2) / r.w, (s.height - pad * 2) / r.h, maxZ), 0.08, 2.5);
    U.view = { z, tx: s.width / 2 - (r.x + r.w / 2) * z, ty: s.height / 2 - (r.y + r.h / 2) * z };
    applyView();
  }
  const allRect = () => bbox([...Object.values(B.cards), ...Object.values(B.frames)]);
  const viewCenter = () => { const s = stageRect(); return toWorld(s.left + s.width / 2, s.top + s.height / 2); };
  function goHome() { if (B.home) fitRect(B.home, 1); else fitRect(allRect()); }
  function focusCard(id, open) {
    const c = B.cards[id], f = B.frames[id];
    if (!c && !f) return;
    if (U.mode === "list") { selectOnly(id); renderAll(); document.querySelector(`.bd-row[data-id="${CSS.escape(id)}"]`)?.scrollIntoView({ block: "center" }); if (open) openPanel(c ? "card" : "frame", id); return; }
    const r = rectOf(c || f), s = stageRect();
    const z = c ? Math.max(U.view.z, 0.85) : U.view.z;
    if (c) U.view = { z, tx: s.width / 2 - (r.x + r.w / 2) * z, ty: s.height / 2 - (r.y + r.h / 2) * z }, applyView(); else fitRect(r, 1);
    selectOnly(id); renderAll();
    const node = el.cards.querySelector(`[data-id="${CSS.escape(id)}"]`);
    if (node) { node.classList.remove("is-flash"); void node.offsetWidth; node.classList.add("is-flash"); }
    if (open) openPanel(c ? "card" : "frame", id);
  }

  // ---------- dashboard numbers for metric and view cards ----------
  const hash = (s) => { let h = 5381; for (const c of s) h = ((h << 5) + h + c.codePointAt(0)) >>> 0; return "k" + h.toString(36); };
  function weekIndex() { const t = today0(); if (t.getMonth() !== 9 || t.getFullYear() !== 2026) return t < new Date(2026, 9, 1) ? 0 : -1; return Math.min(3, Math.floor((t.getDate() - 1) / 7)); }
  function metricOf(key) {
    const s = D.snap, tr = D.tracker || { tasks: {}, creators: {}, counts: {} };
    if (!s) return { value: "–", sub: D.dbMissing ? "אין נתונים כאן" : "הנתונים עוד נטענים", none: true };
    const at = s.generated_at;
    switch (key) {
      case "refresh": { const stale = Date.now() - new Date(at).getTime() > 36 * 36e5; return { value: dm(new Date(at)), unit: hm(new Date(at)), sub: (stale ? "ישן: " : "") + ago(at), warn: stale }; }
      case "ig_followers": {
        // the handle refresh.py counted (facts brand.instagram_live); history points before 19 Oct 2026 hold the old handle's count as ig_lumebookai
        const handle = s.ig_handle || "lumebookai", ig = s.social?.[handle];
        const count = (h) => typeof h.ig_lumebook === "number" ? h.ig_lumebook : typeof h.ig_lumebookai === "number" ? h.ig_lumebookai : null;
        const last = [...(D.history || [])].reverse().find((h) => count(h) != null);
        const v = ig?.followers ?? (last ? count(last) : null);
        return { value: fmt(v), sub: ig?.followers != null ? `@${handle} · ${ago(at)}` : ig?.error ? `הפרופיל לא נטען${last ? `, נתון מ-${dm(parseDay(last.date))}` : ""}` : "", warn: !!ig?.error && ig?.followers == null };
      }
      case "signups": { const su = D.signups; return su ? { value: String(su.total), unit: su.tests ? `ועוד ${su.tests} בדיקות` : "", sub: D.liveSignups ? "חי מהגיליון" : `מהרענון · ${ago(at)}` } : { value: "–", sub: "מחכה לגיליון", none: true }; }
      case "creators_contacted": { const t = s.creators?.tracked || []; const n = t.filter((x) => (tr.creators?.[x.handle] ?? 0) > 0).length; return { value: `${n}`, unit: `מתוך ${t.length}`, sub: "יוצרים במעקב שקיבלו פנייה", prog: t.length ? n / t.length : 0 }; }
      case "week_tasks": {
        const wi = weekIndex(), w = s.plan?.weeks?.[wi];
        if (!w) return { value: "–", sub: "אין שבוע פעיל בתוכנית אוקטובר", none: true };
        const done = w.tasks.filter((t) => tr.tasks?.[hash(w.name + "|" + t)]).length;
        return { value: `${done}`, unit: `מתוך ${w.tasks.length}`, sub: w.name, prog: w.tasks.length ? done / w.tasks.length : 0 };
      }
      case "counter_reels": case "counter_books": case "counter_customer_videos": case "counter_outreach": {
        const k = key.slice(8), [label, target] = COUNTERS[k] || [k, null], v = tr.counts?.[k] || 0;
        return { value: `${v}`, unit: target ? `מתוך ${target}` : "", sub: label, prog: target ? Math.min(1, v / target) : null };
      }
      case "carousel_pack": { const c = s.carousel; return c?.last_date ? { value: dm(parseDay(c.last_date)), unit: `${c.last_options?.length || 0} אופציות`, sub: c.last_topic || "", extra: `${c.approved?.length || 0} בהפקה` } : { value: "–", sub: "אין עדיין חבילה", none: true }; }
      case "key_dates": {
        const t = today0(), next = (s.key_dates || []).filter((d) => parseDay(d.date) >= t).slice(0, 3);
        return { dates: next.map((d) => ({ d: dm(parseDay(d.date)), n: Math.round((parseDay(d.date) - t) / 864e5), l: d.label, u: d.unconfirmed })), sub: next.length ? "" : "אין תאריכים קרובים" };
      }
      case "sync": { const y = s.sync; return y && !y.error ? { value: `${y.counts?.pending ?? 0}`, unit: "משימות", sub: `${y.counts?.warnings ?? 0} אי-התאמות · נבדק ${ago(y.generated_at)}`, warn: (y.counts?.errors || 0) > 0 } : { value: "–", sub: "אין בדיקת סנכרון", none: true }; }
      default: return { value: "–", sub: "מדד לא מוכר", none: true };
    }
  }
  function viewLine(view) {
    const s = D.snap; if (!s) return "";
    const tr = D.tracker || {};
    switch (view) {
      case "overview": return D.alerts ? `${D.alerts.length} פריטים · ${D.alerts.filter((a) => a.sev !== "info").length} דורשים טיפול` : "";
      case "plan": { const m = metricOf("week_tasks"); return m.none ? "" : `השבוע: ${m.value}${m.unit ? " " + m.unit : ""} משימות`; }
      case "creators": { const t = s.creators?.tracked || []; return `${t.length} במעקב · ${t.filter((x) => (tr.creators?.[x.handle] ?? 0) > 0).length} קיבלו פנייה`; }
      case "signups": return D.signups ? `${D.signups.total} הרשמות` : "";
      case "content": return s.carousel?.last_date ? `חבילה ל-${dm(parseDay(s.carousel.last_date))} · ${s.carousel.approved?.length || 0} בהפקה` : "";
      case "competitors": return s.competitors ? `${s.competitors.total} פריטי תוכן` : "";
      case "research": return `${(s.artifacts || []).length} מחקרים ומסמכים`;
      case "sync": return s.sync?.counts ? `${s.sync.counts.pending} משימות · ${s.sync.counts.warnings} אי-התאמות` : "";
      case "assets": return s.sites ? `${s.sites.filter((x) => x.status === 200).length}/${s.sites.length} אתרים באוויר` : "";
      default: return "";
    }
  }
  function behind(r) { if (!r?.component) return false; return !!(D.snap?.sync?.components || []).find((c) => c.id === r.component)?.behind; }

  // ---------- what a card points at ----------
  const resOf = (c) => (c.ref ? CAT.get(c.ref) : null);
  function fileUrl(path) {
    const p = safePath(path); if (!p) return null;
    return ENV.projectServer ? "/" + p.split("/").map(encodeURIComponent).join("/") : null;
  }
  function mediaOf(c) {
    const m = c.media || resOf(c)?.media || null;
    if (!m) return null;
    const files = m.files && m.files.length ? m.files : m.src ? [m.src] : [];
    return { ...m, files };
  }
  function srcUrl(src, m) {
    if (m?.asset && m.url) return m.url;
    if (!src) return m?.published && !ENV.projectServer ? m.published : null;
    if (safeHref(src)) return safeHref(src);
    if (m?.published && src === m.src && !ENV.projectServer) return m.published;
    return fileUrl(src);
  }
  function openTarget(c) {
    const r = resOf(c);
    if (c.url) return safeHref(c.url) ? { url: safeHref(c.url) } : { path: c.url };
    if (r?.url) return ENV.projectServer && r.kind === "artifact" && /\.html?$/i.test(r.path || "") ? { path: r.path } : { url: r.url };
    if (r?.kind === "view" || c.view) return { view: c.view || r?.view };
    if (r?.command) return { command: r.command };
    if (r?.path) return { path: r.path };
    const m = mediaOf(c); if (m?.files?.[0]) return safeHref(m.files[0]) ? { url: m.files[0] } : { path: m.files[0] };
    return null;
  }
  const canPreview = (c) => {
    const m = mediaOf(c), t = openTarget(c);
    return !!(m?.files?.length || (t?.url && driveId(t.url)) || (t?.path && extKind(t.path)) || c.type === "prompt");
  };
  function sourceTitle(c) { const r = resOf(c); return r?.title || ""; }

  // ---------- render: cards ----------
  const nodes = { cards: new Map(), frames: new Map(), edges: new Map(), labels: new Map() };
  const chip = (t, cls = "", title = "") => `<span class="lb-chip ${cls}"${title ? ` title="${esc(title)}"` : ""}>${esc(t)}</span>`;
  const statusChip = (s) => { const [l, cls] = STATUS[s] || STATUS.todo; return chip(l, cls); };
  function projectStats(id) {
    const kids = Object.values(B.cards).filter((c) => c.project === id), tasks = kids.filter((c) => c.type === "task");
    return { n: kids.length, tasks: tasks.length, done: tasks.filter((c) => c.status === "done").length };
  }
  function toolState(r) {
    const key = r?.tool?.key; if (!key) return null;
    const st = ENV.localTools[key];
    if (!st) return { cls: "", text: "לא נבדק" };
    if (st.ok) return { cls: "success", text: st.from === "snapshot" ? `ענה ${dmAt(st.at)}` : "פעיל" };
    return { cls: "warning", text: st.from === "server" ? "לא פעיל" : st.from === "snapshot" ? `לא ענה ${dmAt(st.at)}` : "לא זמין מכאן" };
  }
  const dmAt = (iso) => { try { const d = new Date(iso); return `${dm(d)} ${hm(d)}`; } catch { return ""; } };
  function cardInner(c) {
    const T = TYPES[c.type] || TYPES.note, r = resOf(c), badges = [];
    if (c.ref && r) badges.push(chip("מקור", "outline", "הכרטיס מחובר למקור בפרויקט. עריכה כאן לא משנה את המקור"));
    if (c.ref && !r) badges.push(chip("המקור לא נמצא", "warning"));
    if (r?.private) badges.push(chip("פנימי", "warning", "מספרים פנימיים, נשאר במחשב"));
    if (behind(r)) badges.push(chip("לפרסם מחדש", "warning", "המקור השתנה מאז הפרסום האחרון"));
    if (c.type === "task" || c.type === "project") badges.push(statusChip(c.status));
    if (c.priority === "high") badges.push(chip("עדיפות גבוהה", "danger"));
    const ts = toolState(r); if (ts) badges.push(chip(ts.text, ts.cls));
    const desc = c.desc || "", srcDesc = !desc && r?.summary ? r.summary : "";
    let body = "";
    const descHtml = desc ? `<div class="bc-desc" dir="auto">${esc(desc)}</div>` : srcDesc ? `<div class="bc-desc is-src" dir="auto">${esc(srcDesc)}</div>` : "";
    if (c.type === "metric") {
      const m = metricOf(c.metric || r?.metric);
      body = m.dates ? `<div class="bc-dates">${m.dates.map((d) => `<div><span dir="auto">${esc(d.l)}${d.u ? " (לא מאושר)" : ""}</span><b>${esc(d.d)} · ${d.n === 0 ? "היום" : `${d.n} ימים`}</b></div>`).join("") || `<span class="bc-sub">${esc(m.sub)}</span>`}</div>`
        : `<div class="bc-val ${m.warn ? "is-warn" : ""}">${esc(m.value)}${m.unit ? `<small>${esc(m.unit)}</small>` : ""}</div>${m.prog != null ? `<div class="bc-prog"><i style="width:${Math.round(m.prog * 100)}%"></i></div>` : ""}<div class="bc-sub" dir="auto">${esc(m.sub || "")}${m.extra ? " · " + esc(m.extra) : ""}</div>`;
      if (c.target) body += `<div class="bc-mine">יעד שלי: ${esc(c.target)}</div>`;
      if (desc) body += descHtml;
    } else if (c.type === "view") {
      const line = viewLine(c.view || r?.view);
      body = descHtml + (line ? `<div class="bc-sub" dir="auto">${esc(line)}</div>` : "");
    } else if (c.type === "media") {
      const m = mediaOf(c), f = m?.files?.[0], kind = m?.kind || extKind(f), u = srcUrl(f, m);
      body = !f && !m?.published ? `<div class="bc-thumb is-empty">אין עדיין קובץ. מוסיפים קישור או מעלים בפרטים.</div>`
        : u && kind === "image" ? `<div class="bc-thumb"><img src="${esc(u)}" alt="" loading="lazy" decoding="async"></div>`
        : u && kind === "video" ? `<div class="bc-thumb"><video src="${esc(u)}#t=0.5" preload="metadata" muted playsinline></video><span class="bc-play">וידאו</span></div>`
        : u && kind === "audio" ? `<div class="bc-thumb">אודיו · לחיצה על תצוגה מקדימה</div>`
        : u ? `<div class="bc-thumb">${esc(kind === "html" ? "דף" : kind === "pdf" ? "PDF" : "קובץ")} · לחיצה על תצוגה מקדימה</div>`
        : `<div class="bc-thumb">קובץ במחשב. נפתח בשרת הפרויקט המקומי</div>`;
      if (desc || srcDesc) body = descHtml + body;
    } else if (c.type === "prompt") {
      const text = c.prompt || r?.prompt || "";
      body = (text ? `<div class="bc-prompt" dir="auto">${esc(text)}</div>` : `<div class="bc-desc is-src">אין עדיין טקסט</div>`) + (desc ? descHtml : "");
    } else if (c.type === "workflow") {
      const st = c.checklist || [];
      body = descHtml + (st.length ? `<ol class="bc-steps">${st.slice(0, 7).map((s) => `<li class="${s.done ? "done" : ""}" dir="auto">${esc(s.text)}</li>`).join("")}</ol>` : "");
    } else if (c.type === "project") {
      const p = projectStats(c.id);
      body = descHtml + (p.n ? `<div class="bc-sub">${p.n} כרטיסים · ${p.done}/${p.tasks} משימות</div>${p.tasks ? `<div class="bc-prog"><i style="width:${Math.round(p.done / p.tasks * 100)}%"></i></div>` : ""}` : "");
    } else {
      body = descHtml;
      if (c.type === "task" && c.checklist?.length) { const d = c.checklist.filter((x) => x.done).length; body += `<div class="bc-prog"><i style="width:${Math.round(d / c.checklist.length * 100)}%"></i></div><div class="bc-sub">${d}/${c.checklist.length} בצ׳קליסט</div>`; }
      const t = openTarget(c);
      if (r?.command) body += `<div class="bc-prompt" dir="ltr">${esc(r.command)}</div>`;
      else if (t?.url) body += `<div class="bc-url" title="${esc(t.url)}">${esc(host(t.url))}</div>`;
      else if (t?.path) body += `<div class="bc-url" title="${esc(t.path)}">${esc(t.path)}</div>`;
    }
    const foot = [];
    for (const t of c.tags.slice(0, 3)) foot.push(`<span class="bc-tag" dir="auto">${esc(t)}</span>`);
    if (c.tags.length > 3) foot.push(`<span>+${c.tags.length - 3}</span>`);
    if (c.due) { const n = Math.round((parseDay(c.due) - today0()) / 864e5); foot.push(`<span class="${n < 0 && c.status !== "done" ? "bd-err" : ""}">${n < 0 ? "עבר" : "עד"} ${esc(dm(parseDay(c.due)))}</span>`); }
    const acts = [];
    if (openTarget(c)) acts.push(`<button class="bc-act" type="button" data-act="open" aria-label="פתיחה" title="פתיחה">${I(openTarget(c).command ? "copy" : "open")}</button>`);
    if (canPreview(c)) acts.push(`<button class="bc-act" type="button" data-act="preview" aria-label="תצוגה מקדימה" title="תצוגה מקדימה">${I("eye")}</button>`);
    acts.push(`<button class="bc-act" type="button" data-act="details" aria-label="פרטים ועריכה" title="פרטים ועריכה · Enter">${I("edit")}</button>`);
    return `<div class="bc-head"><span class="lb-tile is-soft lb-cat-0">${I(T.icon)}</span><span class="bc-type">${esc(T.label)}</span><span class="bc-badges">${badges.join("")}</span></div>
      <div class="bc-title" dir="auto">${esc(c.title || sourceTitle(c) || T.untitled)}</div>
      <div class="bc-body">${body}</div>${foot.length ? `<div class="bc-foot">${foot.join("")}</div>` : ""}
      <div class="bc-acts">${acts.join("")}</div>`;
  }
  function cardSig(c) { return JSON.stringify(c) + "|" + (c.ref || c.type === "metric" || c.type === "view" || c.type === "project" || c.type === "media" ? live : 0) + "|" + (ENV.projectServer ? 1 : 0); }
  function placeNode(n, o) { n.style.left = o.x + "px"; n.style.top = o.y + "px"; n.style.width = o.w + "px"; n.style.height = o.h + "px"; }
  function renderCards(full) {
    const seen = new Set();
    const order = Object.values(B.cards).sort((a, b) => a.y - b.y || b.x - a.x);
    for (const c of order) {
      seen.add(c.id);
      let n = nodes.cards.get(c.id);
      if (!n) {
        n = { el: document.createElement("div"), sig: "" };
        n.el.className = "bc"; n.el.dataset.id = c.id; n.el.tabIndex = 0;
        el.cards.appendChild(n.el); nodes.cards.set(c.id, n);
      }
      const sig = cardSig(c);
      if (sig !== n.sig && U.editing !== c.id) { n.el.innerHTML = cardInner(c); n.sig = sig; }
      n.el.className = `bc t-${c.type}${c.color ? " c-" + c.color : ""}`;
      n.el.setAttribute("role", "group");
      n.el.setAttribute("aria-label", `${TYPES[c.type]?.label || ""}: ${c.title || sourceTitle(c)}`);
      placeNode(n.el, c);
      n.el.style.zIndex = String(c.z || 0);
      zTop = Math.max(zTop, c.z || 0);
      if (full) el.cards.appendChild(n.el); // keep DOM (and Tab) order in reading order
    }
    for (const [id, n] of nodes.cards) if (!seen.has(id)) { n.el.remove(); nodes.cards.delete(id); }
    flagCards();
  }
  function flagCards() {
    const rel = related(), match = filterFn();
    for (const [id, n] of nodes.cards) {
      const c = B.cards[id];
      n.el.classList.toggle("is-sel", U.sel.has(id));
      n.el.classList.toggle("is-rel", rel.has(id) && !U.sel.has(id));
      n.el.classList.toggle("is-dim", !!match && !match(c));
    }
  }
  function related() {
    const s = new Set();
    const focus = U.sel.size === 1 ? [...U.sel][0] : null;
    if (focus && B.cards[focus]) for (const e of Object.values(B.edges)) { if (e.from === focus) s.add(e.to); if (e.to === focus) s.add(e.from); }
    if (U.selEdge && B.edges[U.selEdge]) { s.add(B.edges[U.selEdge].from); s.add(B.edges[U.selEdge].to); }
    return s;
  }

  // ---------- render: frames ----------
  function renderFrames() {
    const seen = new Set(), match = filterFn();
    const list = Object.values(B.frames).sort((a, b) => b.w * b.h - a.w * a.h);
    for (const f of list) {
      seen.add(f.id);
      let n = nodes.frames.get(f.id);
      if (!n) { n = { el: document.createElement("div"), sig: "" }; n.el.dataset.id = f.id; el.frames.appendChild(n.el); nodes.frames.set(f.id, n); }
      const members = frameMembers(f).cards;
      const sig = f.title + "|" + f.area + "|" + members.length;
      if (sig !== n.sig) {
        n.el.innerHTML = `<div class="bf-title"><button class="bf-name" type="button" data-frame="${esc(f.id)}" title="גרירה מזיזה את האזור עם הכרטיסים. לחיצה כפולה משנה את השם"><span class="lb-tile ${areaCat(f.area)}">${I("frame")}</span><span dir="auto">${esc(f.title)}</span></button><span class="bf-count">${members.length}</span></div>`;
        n.sig = sig;
      }
      n.el.className = `bf ${areaCat(f.area)}`;
      n.el.classList.toggle("is-sel", U.sel.has(f.id));
      n.el.classList.toggle("is-dim", !!match && !members.some(match));
      placeNode(n.el, f);
      el.frames.appendChild(n.el);
    }
    for (const [id, n] of nodes.frames) if (!seen.has(id)) { n.el.remove(); nodes.frames.delete(id); }
  }

  // ---------- render: edges ----------
  function renderEdges() {
    const seen = new Set(), focus = U.sel.size === 1 ? [...U.sel][0] : null, match = filterFn();
    for (const e of Object.values(B.edges)) {
      const a = B.cards[e.from], b = B.cards[e.to];
      if (!a || !b) continue;
      const show = e.kind !== "dep" || prefs.showDeps;
      let n = nodes.edges.get(e.id);
      if (!show) { if (n) { n.g.remove(); nodes.edges.delete(e.id); } const l = nodes.labels.get(e.id); if (l) { l.remove(); nodes.labels.delete(e.id); } continue; }
      seen.add(e.id);
      if (!n) {
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.dataset.id = e.id;
        g.innerHTML = `<path class="be-hit"/><path class="be-line"/>`;
        el.edgeG.appendChild(g);
        n = { g, hit: g.firstChild, line: g.lastChild };
        nodes.edges.set(e.id, n);
      }
      const geo = edgeGeom(a, b), hot = focus && (e.from === focus || e.to === focus), sel = U.selEdge === e.id;
      n.hit.setAttribute("d", geo.d); n.line.setAttribute("d", geo.d);
      n.line.setAttribute("marker-end", hot || sel ? "url(#bd-ar-hot)" : "url(#bd-ar)");
      n.g.setAttribute("class", `be ${e.kind}${hot ? " is-hot" : ""}${sel ? " is-sel" : ""}${match && !(match(a) && match(b)) ? " is-dim" : ""}`);
      let l = nodes.labels.get(e.id);
      if (e.label) {
        if (!l) { l = document.createElement("div"); l.dataset.edge = e.id; el.labels.appendChild(l); nodes.labels.set(e.id, l); }
        if (!l.querySelector("input")) l.textContent = e.label;
        l.className = `bl-lab ${e.kind}${hot ? " is-hot" : ""}${sel ? " is-sel" : ""}${match && !(match(a) && match(b)) ? " is-dim" : ""}`;
        l.style.left = geo.mid.x + "px"; l.style.top = geo.mid.y + "px";
        l.title = e.kind === "dep" ? "תלות מהרישום (lumebook.json)" : "חיבור שלי. לחיצה כפולה לעריכה";
      } else if (l && !l.querySelector("input")) { l.remove(); nodes.labels.delete(e.id); }
    }
    for (const [id, n] of nodes.edges) if (!seen.has(id)) { n.g.remove(); nodes.edges.delete(id); }
    for (const [id, l] of nodes.labels) if (!seen.has(id) || !B.edges[id]?.label) { if (!l.querySelector("input")) { l.remove(); nodes.labels.delete(id); } }
  }

  // ---------- render: handles and the context toolbar ----------
  function selItems() { return [...U.sel].map((id) => B.cards[id] || B.frames[id]).filter(Boolean); }
  function renderHandles() {
    const items = selItems();
    let h = "";
    if (U.mode === "canvas" && items.length === 1 && !readOnlyUI()) {
      const o = items[0], isF = !!B.frames[o.id];
      for (const [k, x, y] of [["nw", o.x, o.y], ["ne", o.x + o.w, o.y], ["sw", o.x, o.y + o.h], ["se", o.x + o.w, o.y + o.h]])
        h += `<div class="bh" data-h="${k}" data-id="${esc(o.id)}" style="left:${x}px;top:${y}px" title="שינוי גודל"></div>`;
      if (!isF) h += `<div class="bh-conn" data-conn="${esc(o.id)}" style="left:${o.x - 18}px;top:${o.y + o.h / 2}px" title="גרירה לכרטיס אחר יוצרת חיבור">${I("plus")}</div>`;
    } else if (U.mode === "canvas" && items.length > 1) {
      const r = bbox(items);
      h += `<div class="bh-box" style="left:${r.x - 8}px;top:${r.y - 8}px;width:${r.w + 16}px;height:${r.h + 16}px"></div>`;
    }
    el.handles.innerHTML = h;
  }
  function renderCtx() {
    const items = selItems();
    if (U.mode !== "canvas" || (!items.length && !U.selEdge) || G?.moved) { el.ctx.hidden = true; return; }
    let r, html = "";
    const b = (a, icon, label) => `<button class="bd-ib" type="button" data-a="${a}" aria-label="${esc(label)}" title="${esc(label)}">${I(icon)}</button>`;
    if (U.selEdge && !items.length) {
      const e = B.edges[U.selEdge]; if (!e) { el.ctx.hidden = true; return; }
      const geo = edgeGeom(B.cards[e.from], B.cards[e.to]);
      r = { x: geo.mid.x, y: geo.mid.y - 12, w: 0, h: 0 };
      html = b("edge-label", "edit", "תווית") + b("edge-swap", "swap", "היפוך כיוון") + b("edge-details", "eye", "פרטים") + b("delete", "trash", "מחיקת החיבור");
    } else if (items.length === 1) {
      const o = items[0], c = B.cards[o.id];
      r = o;
      if (c) {
        if (openTarget(c)) html += b("ctx-open", openTarget(c).command ? "copy" : "open", openTarget(c).command ? "העתקת הפקודה" : "פתיחה");
        if (canPreview(c)) html += b("ctx-preview", "eye", "תצוגה מקדימה");
        html += b("ctx-details", "edit", "פרטים ועריכה") + b("connect", "connect", "חיבור לכרטיס (C)") + b("duplicate", "dup", "שכפול (Cmd+D)") + b("ctx-pin", isPinned(c) ? "pinned" : "pin", isPinned(c) ? "הסרה מהמגירה" : "הצמדה למגירה") + `<span class="bd-sep"></span>` + b("delete", "trash", "הסרה מהלוח (Delete)");
      } else {
        html = b("ctx-details", "edit", "שם ופרטים") + b("fit-sel", "fit", "התאמה לאזור") + b("save-tpl", "tpl", "שמירה כתבנית") + b("duplicate", "dup", "שכפול עם הכרטיסים") + `<span class="bd-sep"></span>` + b("delete", "trash", "מחיקת האזור");
      }
    } else {
      r = bbox(items);
      html = b("align-r", "alignR", "יישור לימין") + b("align-c", "alignC", "מרכוז אופקי") + b("align-l", "alignL", "יישור לשמאל") + b("align-t", "alignT", "יישור למעלה") + b("align-m", "alignM", "מרכוז אנכי") + b("align-b", "alignB", "יישור למטה")
        + b("dist-h", "distH", "פיזור אופקי") + b("dist-v", "distV", "פיזור אנכי") + `<span class="bd-sep"></span>` + b("frame-sel", "frame", "אזור סביב הבחירה (F)") + b("save-tpl", "tpl", "שמירה כתבנית") + b("duplicate", "dup", "שכפול") + b("delete", "trash", "מחיקה");
    }
    if (readOnlyUI()) html = html.replace(/<button[^>]*data-a="(delete|duplicate|connect|align-[a-z]|dist-[a-z]|frame-sel|edge-swap|edge-label|ctx-pin|save-tpl)"[\s\S]*?<\/button>/g, "");
    el.ctx.innerHTML = html;
    const s = toScreen(r.x + r.w / 2, r.y), sr = stageRect();
    el.ctx.style.left = clamp(s.x, 160, sr.width - 160) + "px";
    el.ctx.style.top = Math.max(56, s.y) + "px";
    el.ctx.hidden = !html;
  }

  // ---------- filters ----------
  function filterFn() {
    const f = U.filters;
    if (!f.types.size && !f.status.size && !f.tag && !f.project && !f.source) return null;
    return (c) => (!f.types.size || f.types.has(c.type)) && (!f.status.size || f.status.has(c.status || (c.type === "task" ? "todo" : "")))
      && (!f.tag || c.tags.includes(f.tag)) && (!f.project || c.project === f.project || c.id === f.project) && (!f.source || (f.source === "src" ? !!c.ref : !c.ref));
  }
  const filterCount = () => U.filters.types.size + U.filters.status.size + (U.filters.tag ? 1 : 0) + (U.filters.project ? 1 : 0) + (U.filters.source ? 1 : 0);

  // ---------- render: everything ----------
  let renderQueued = false;
  function renderAll(opts = {}) {
    if (!B) return;
    renderFrames(); renderCards(true); renderEdges(); renderHandles(); renderCtx();
    renderBar(); renderDock();
    if (U.mode === "list") renderList();
    if (opts.panel || (U.panel && !el.panel.contains(document.activeElement))) renderPanel();
  }
  function renderSoon() { if (renderQueued) return; renderQueued = true; requestAnimationFrame(() => { renderQueued = false; renderAll(); }); }
  function renderMoving() { for (const id of U.sel) { const o = B.cards[id]; if (o) { const n = nodes.cards.get(id); if (n) placeNode(n.el, o); } } for (const it of G?.items || []) { const o = it.kind === "c" ? B.cards[it.id] : B.frames[it.id]; const n = (it.kind === "c" ? nodes.cards : nodes.frames).get(it.id); if (o && n) placeNode(n.el, o); } renderEdges(); renderHandles(); }
  const readOnlyUI = () => readOnly || !B;

  function renderBar() {
    const q = (a) => el.bd.querySelector(`[data-a="${a}"]`);
    q("undo").disabled = !H.past.length || readOnlyUI(); q("redo").disabled = !H.future.length || readOnlyUI();
    q("undo").title = H.past.length ? `ביטול: ${H.past[H.past.length - 1].label} · Cmd+Z` : "ביטול · Cmd+Z";
    q("tool-select").setAttribute("aria-pressed", String(U.tool === "select")); q("tool-hand").setAttribute("aria-pressed", String(U.tool === "hand"));
    q("deps").setAttribute("aria-pressed", String(!!prefs.showDeps)); q("snap").setAttribute("aria-pressed", String(!!prefs.snap));
    q("mode-canvas").setAttribute("aria-pressed", String(U.mode === "canvas")); q("mode-list").setAttribute("aria-pressed", String(U.mode === "list"));
    q("dock").setAttribute("aria-pressed", String(el.dock.dataset.open === "true"));
    q("add").disabled = readOnlyUI();
    const fc = filterCount(), fb = $("bd-fcount"); fb.hidden = !fc; fb.textContent = fc;
    el.stage.classList.toggle("is-hand", U.tool === "hand");
    el.stage.classList.toggle("is-connecting", !!U.connectFrom);
    el.bd.querySelectorAll(".bd-canvas-only").forEach((b) => (b.hidden = U.mode !== "canvas"));
  }
  function renderSave() {
    const s = el.save, where = store?.kind === "db" ? "בלוח ב-Claude" : "במכשיר הזה";
    let cls = "", text = "";
    switch (SAVE.state) {
      case "loading": text = "טוען את הלוח…"; break;
      case "pending": cls = "is-pending"; text = "יש שינויים שעוד לא נשמרו"; break;
      case "saving": cls = "is-pending"; text = "שומר…"; break;
      case "saved": cls = "is-ok"; text = `נשמר ${where}${SAVE.at ? " · " + hm(SAVE.at) : ""}`; break;
      case "idle": cls = "is-ok"; text = B?.savedAt ? `שמור ${where} · ${dmAt(B.savedAt)}` : `נשמר ${where}`; break;
      case "error": cls = "is-error"; text = "השמירה נכשלה · לנסות שוב"; break;
      case "ro": cls = "is-ro"; text = "קריאה בלבד: השינויים לא נשמרים"; break;
    }
    s.className = `lb-chip bd-save ${cls}`;
    s.textContent = text;
    s.title = SAVE.error || (store?.kind === "db" ? "השינויים נשמרים במסד הנתונים של הלוח ב-claude.ai ונראים בכל מכשיר שבו פותחים אותו שם" : "השינויים נשמרים רק בדפדפן הזה. כדי להעביר למכשיר אחר: ייצוא וייבוא");
  }
  function renderBanner() {
    let html = "", cls = "";
    if (remote) html = `<span>הלוח נשמר בינתיים במקום אחר (לשונית או מכשיר אחר). השינויים האחרונים שלך עוד לא נשמרו.</span><button class="bd-btn" type="button" data-a="remote-load">לטעון את הגרסה האחרת</button><button class="bd-btn is-primary" type="button" data-a="remote-keep">לשמור את שלי</button>`;
    else if (ENV.bannerMsg) { html = `<span>${esc(ENV.bannerMsg)}</span><button class="bd-ib" type="button" data-a="banner-close" aria-label="סגירה">${I("close")}</button>`; cls = ENV.bannerErr ? "is-error" : ""; }
    el.banner.innerHTML = html; el.banner.hidden = !html; el.banner.className = `bd-banner ${cls}`;
  }

  // ---------- selection ----------
  function selectOnly(id) { U.sel = new Set(id ? [id] : []); U.selEdge = null; }
  function setSelection(ids) { U.sel = new Set(ids); U.selEdge = null; if (U.panel && U.panel.kind !== "edge" && !U.sel.has(U.panel.id)) closePanel(); }

  // ---------- creating and changing things ----------
  function newCard(type, at, extra = {}) {
    const T = TYPES[type] || TYPES.note, p = at || viewCenter();
    const pos = freeSpot(p.x - T.w / 2, p.y - T.h / 2, T.w, T.h);
    const c = cleanCard({ id: uid("c"), type, title: "", desc: "", tags: [], x: pos.x, y: pos.y, w: T.w, h: T.h, z: ++zTop, createdAt: nowIso(), ...(type === "task" ? { status: "todo" } : {}), ...extra });
    B.cards[c.id] = c;
    return c;
  }
  function addCard(type, at, extra) {
    if (readOnlyUI()) return null;
    const c = newCard(type, at, extra);
    if (type === "metric" && !c.metric) c.metric = "refresh";
    if (type === "view" && !c.view) c.view = "overview";
    commit(`הוספה: ${TYPES[type].label}`);
    selectOnly(c.id); renderAll();
    if (["note", "task", "project", "workflow"].includes(type) && U.mode === "canvas") startInlineEdit(c.id);
    else openPanel("card", c.id);
    return c;
  }
  function addFromResource(ref, at) {
    if (readOnlyUI()) return null;
    const r = CAT.get(ref); if (!r) return null;
    const type = TYPES[r.type] ? r.type : "link";
    const c = newCard(type, at, { ref, title: r.title, tags: [...(r.tags || [])], ...(r.prompt ? { prompt: r.prompt } : {}), ...(r.metric ? { metric: r.metric } : {}), ...(r.view ? { view: r.view } : {}) });
    if (!B.known.includes(ref)) B.known.push(ref);
    commit(`הוספת ${r.title}`);
    selectOnly(c.id); renderAll();
    return c;
  }
  function deleteSelection() {
    if (readOnlyUI()) return;
    if (U.selEdge && !U.sel.size) { const e = B.edges[U.selEdge]; delete B.edges[U.selEdge]; U.selEdge = null; commit("מחיקת חיבור"); closePanelIf("edge"); renderAll(); toastUndo(e?.kind === "dep" ? "החיבור הוסר מהלוח. lumebook.json לא השתנה" : "החיבור נמחק"); return; }
    if (!U.sel.size) return;
    let n = 0, srcN = 0;
    for (const id of U.sel) {
      if (B.cards[id]) { if (B.cards[id].ref) srcN++; delete B.cards[id]; n++; for (const e of Object.values(B.edges)) if (e.from === id || e.to === id) delete B.edges[e.id]; for (const c of Object.values(B.cards)) if (c.project === id) delete c.project; }
      else if (B.frames[id]) { delete B.frames[id]; n++; }
    }
    U.sel.clear(); commit(n === 1 ? "מחיקה" : `מחיקת ${n} פריטים`); tidySelection(); renderAll({ panel: true });
    toastUndo(srcN ? `${n === 1 ? "הכרטיס הוסר" : `הוסרו ${n} פריטים`} מהלוח. המקורות עצמם לא השתנו` : n === 1 ? "נמחק" : `נמחקו ${n} פריטים`);
  }
  function closePanelIf(kind) { if (U.panel?.kind === kind) closePanel(); }
  function cloneItems(cards, frames, dx, dy, edgeList = Object.values(B.edges)) {
    const map = {};
    const outCards = cards.map((c) => { const id = uid("c"); map[c.id] = id; return { ...JSON.parse(JSON.stringify(c)), id, x: c.x + dx, y: c.y + dy, z: ++zTop, createdAt: nowIso() }; });
    const outFrames = frames.map((f) => ({ ...JSON.parse(JSON.stringify(f)), id: uid("f"), x: f.x + dx, y: f.y + dy }));
    for (const c of outCards) if (c.project && map[c.project]) c.project = map[c.project];
    const edges = edgeList.filter((e) => map[e.from] && map[e.to] && e.from !== e.to).map((e) => ({ ...e, id: uid("e"), from: map[e.from], to: map[e.to], kind: "manual" }));
    return { cards: outCards, frames: outFrames, edges, map };
  }
  function expandSelection() {
    const cards = new Map(), frames = new Map();
    for (const id of U.sel) {
      if (B.cards[id]) cards.set(id, B.cards[id]);
      if (B.frames[id]) { frames.set(id, B.frames[id]); const m = frameMembers(B.frames[id]); m.cards.forEach((c) => cards.set(c.id, c)); m.frames.forEach((f) => frames.set(f.id, f)); }
    }
    return { cards: [...cards.values()], frames: [...frames.values()] };
  }
  function duplicateSelection() {
    if (readOnlyUI() || !U.sel.size) return;
    const { cards, frames } = expandSelection();
    let off = { dx: -40, dy: 40 };
    if (frames.length) { const r = bbox([...frames, ...cards]), spot = freeArea(r.w, r.h, r.x - r.w / 2 - 200, r.y + r.h / 2); off = { dx: spot.x - r.x, dy: spot.y - r.y }; }
    const out = cloneItems(cards, frames, off.dx, off.dy);
    out.cards.forEach((c) => (B.cards[c.id] = c)); out.frames.forEach((f) => (B.frames[f.id] = f)); out.edges.forEach((e) => (B.edges[e.id] = e));
    commit("שכפול");
    setSelection([...out.frames.map((f) => f.id), ...(out.frames.length ? [] : out.cards.map((c) => c.id))]);
    renderAll();
  }
  function connect(from, to, label = "") {
    if (readOnlyUI() || !B.cards[from] || !B.cards[to] || from === to) return null;
    const ex = Object.values(B.edges).find((e) => e.from === from && e.to === to);
    if (ex) { U.selEdge = ex.id; U.sel.clear(); renderAll(); toast("החיבור הזה כבר קיים"); return ex; }
    const e = { id: uid("e"), from, to, label, kind: "manual" };
    B.edges[e.id] = e; commit("חיבור"); U.sel.clear(); U.selEdge = e.id; renderAll();
    return e;
  }
  function align(how) {
    const items = selItems(); if (items.length < 2 || readOnlyUI()) return;
    const r = bbox(items);
    for (const o of items) {
      if (how === "r") o.x = r.x + r.w - o.w; if (how === "l") o.x = r.x; if (how === "c") o.x = r.x + (r.w - o.w) / 2;
      if (how === "t") o.y = r.y; if (how === "b") o.y = r.y + r.h - o.h; if (how === "m") o.y = r.y + (r.h - o.h) / 2;
    }
    if (how === "h" || how === "v") {
      const k = how === "h" ? "x" : "y", s = how === "h" ? "w" : "h", sorted = [...items].sort((a, b) => a[k] - b[k]);
      const total = sorted.reduce((a, o) => a + o[s], 0), gap = (r[s] - total) / (sorted.length - 1);
      let cur = r[k]; for (const o of sorted) { o[k] = cur; cur += o[s] + gap; }
    }
    commit("יישור"); renderAll();
  }
  function frameAround(ids) {
    if (readOnlyUI()) return;
    const items = (ids || [...U.sel]).map((id) => B.cards[id] || B.frames[id]).filter(Boolean);
    let r = bbox(items);
    if (!r) { const p = viewCenter(); r = { x: p.x - 450, y: p.y - 300, w: 900, h: 600 }; } else r = { x: r.x - 40, y: r.y - 90, w: r.w + 80, h: r.h + 130 };
    const f = cleanFrame({ id: uid("f"), title: "אזור חדש", x: prefs.snap ? snapTo(r.x) : r.x, y: prefs.snap ? snapTo(r.y) : r.y, w: r.w, h: r.h });
    B.frames[f.id] = f; commit("אזור חדש"); selectOnly(f.id); renderAll(); startFrameRename(f.id);
  }
  function placeInFrame(c, f) {
    const others = frameMembers(f).cards.filter((x) => x.id !== c.id);
    const bottom = others.length ? Math.max(...others.map((x) => x.y + x.h)) + 24 : f.y + 76;
    c.x = f.x + f.w - 36 - c.w; c.y = bottom;
    if (c.y + c.h + 36 > f.y + f.h) f.h = c.y + c.h + 36 - f.y;
  }
  function isPinned(c) { return B.dock.some((d) => d.ref === (c.ref || "card:" + c.id)); }
  function togglePin(ref) {
    if (readOnlyUI()) return;
    const i = B.dock.findIndex((d) => d.ref === ref);
    if (i >= 0) B.dock.splice(i, 1); else B.dock.push({ id: uid("d"), ref });
    commit(i >= 0 ? "הסרה מהמגירה" : "הצמדה למגירה"); renderAll();
  }

  // ---------- templates ----------
  const builtinTemplates = () => (SEED.templates || []).map((t) => ({ ...t, id: "tpl-" + t.key, builtin: true }));
  const allTemplates = () => [...builtinTemplates(), ...Object.values(B?.templates || {})];
  function instantiate(tplId, at) {
    if (readOnlyUI()) return;
    const t = allTemplates().find((x) => x.id === tplId); if (!t) return;
    const p = at || viewCenter(), idOf = {}, made = [];
    const stamp = dm(new Date());
    let frame;
    if (t.builtin) {
      const specs = [...(t.project ? [{ k: "project", type: "project", title: t.project.title, desc: t.project.desc, status: "todo" }] : []), ...t.cards];
      const cols = 4, colW = 260, gap = 40, pad = 40, head = 80;
      const rowsH = []; specs.forEach((s, i) => { const r = Math.floor(i / cols); rowsH[r] = Math.max(rowsH[r] || 0, (TYPES[s.type] || TYPES.note).h); });
      const w = pad * 2 + Math.min(cols, specs.length) * colW + (Math.min(cols, specs.length) - 1) * gap, h = head + rowsH.reduce((a, b) => a + b + gap, 0) - gap + pad;
      const { x: x0, y: y0 } = freeArea(w, h, p.x, p.y);
      frame = cleanFrame({ id: uid("f"), title: `${t.project?.title || t.title} · ${stamp}`, area: t.area, x: x0, y: y0, w, h });
      let yAcc = y0 + head;
      specs.forEach((s, i) => {
        const r = Math.floor(i / cols), ci = i % cols; if (ci === 0 && r > 0) yAcc += rowsH[r - 1] + gap;
        const T = TYPES[s.type] || TYPES.note, refR = s.ref ? CAT.get(s.ref) : null;
        const c = cleanCard({ id: uid("c"), type: s.type, title: s.title || refR?.title || "", desc: s.desc || "", tags: [...(t.tags || [])], ref: s.ref, url: s.url,
          prompt: s.prompt, status: s.type === "task" || s.type === "project" ? "todo" : undefined,
          checklist: (s.checklist || []).map((x, n) => ({ id: "k" + n, text: x, done: false })),
          x: x0 + w - pad - (ci + 1) * colW - ci * gap, y: yAcc, w: T.w > colW ? colW : T.w, h: T.h, z: ++zTop, createdAt: nowIso() });
        idOf[s.k] = c.id; made.push(c);
      });
      for (const c of made) if (idOf.project && c.id !== idOf.project) c.project = idOf.project;
      for (const [a, b, label] of t.edges || []) if (idOf[a] && idOf[b] && a !== b) { const e = { id: uid("e"), from: idOf[a], to: idOf[b], label: label || "", kind: "manual" }; B.edges[e.id] = e; }
    } else {
      const fw = t.frame?.w || (bbox(t.cards.map((c) => ({ x: c.x, y: c.y, w: c.w, h: c.h })))?.w || 600) + 80;
      const fh = t.frame?.h || (bbox(t.cards.map((c) => ({ x: c.x, y: c.y, w: c.w, h: c.h })))?.h || 400) + 130;
      const { x: x0, y: y0 } = freeArea(fw, fh, p.x, p.y);
      frame = cleanFrame({ id: uid("f"), title: `${t.title} · ${stamp}`, area: t.frame?.area, x: x0, y: y0, w: fw, h: fh });
      const ox = t.frame ? 0 : 40, oy = t.frame ? 0 : 90;
      for (const s of t.cards) {
        const c = cleanCard({ ...JSON.parse(JSON.stringify(s)), id: uid("c"), x: x0 + ox + s.x, y: y0 + oy + s.y, z: ++zTop, createdAt: nowIso() });
        if (!c) continue; idOf[s.k] = c.id; made.push(c);
      }
      for (const c of made) { const k = Object.keys(idOf).find((kk) => idOf[kk] === c.id); const src = t.cards.find((x) => x.k === k); if (src?.project && idOf[src.project]) c.project = idOf[src.project]; else delete c.project; }
      for (const e of t.edges || []) if (idOf[e.from] && idOf[e.to]) { const ne = { id: uid("e"), from: idOf[e.from], to: idOf[e.to], label: e.label || "", kind: "manual" }; B.edges[ne.id] = ne; }
    }
    B.frames[frame.id] = frame;
    for (const c of made) B.cards[c.id] = c;
    commit(`תבנית: ${t.title}`);
    selectOnly(frame.id); renderAll();
    if (U.mode === "canvas") fitRect(frame, 1);
    toast(`נוצר עותק חדש של "${t.title}". אפשר לשנות אותו בלי לגעת בתבנית או בפרויקטים קודמים`);
  }
  function saveTemplateFromSelection() {
    if (readOnlyUI() || !U.sel.size) return;
    const { cards, frames } = expandSelection();
    if (!cards.length) { toast("אין כרטיסים בבחירה"); return; }
    const oneFrame = frames.length === 1 ? frames[0] : null;
    const origin = oneFrame ? { x: oneFrame.x, y: oneFrame.y } : (() => { const r = bbox(cards); return { x: r.x, y: r.y }; })();
    const k = new Map(cards.map((c, i) => [c.id, "k" + i]));
    const tcards = cards.map((c) => {
      const x = JSON.parse(JSON.stringify(c));
      delete x.id; delete x.createdAt; delete x.updatedAt; delete x.due; delete x.z;
      x.k = k.get(c.id); x.x = c.x - origin.x; x.y = c.y - origin.y;
      if (x.status) x.status = "todo";
      if (x.checklist) x.checklist = x.checklist.map((s) => ({ ...s, done: false }));
      if (x.project) { if (k.has(x.project)) x.project = k.get(x.project); else delete x.project; }
      return x;
    });
    const edges = Object.values(B.edges).filter((e) => k.has(e.from) && k.has(e.to)).map((e) => ({ from: k.get(e.from), to: k.get(e.to), label: e.label }));
    const proj = cards.find((c) => c.type === "project");
    dialog({
      title: "שמירה כתבנית",
      body: `<label class="lb-field">שם התבנית<input class="lb-input" id="tpl-name" dir="rtl" value="${esc((oneFrame?.title || proj?.title || "תבנית חדשה").replace(/ · \d+\.\d+$/, ""))}"></label>
        <label class="lb-field">תיאור<textarea class="lb-textarea" id="tpl-desc" dir="rtl" rows="2"></textarea></label>
        <p class="lb-note">${cards.length} כרטיסים ו-${edges.length} חיבורים. התבנית שומרת עותק: שינויים בה לא משנים את הכרטיסים האלה, ושימוש בה יוצר כרטיסים חדשים. מצב המשימות מתאפס ותאריכים לא נשמרים.</p>`,
      foot: `<button class="bd-btn is-primary" type="button" data-d="ok">שמירה</button><button class="bd-btn" type="button" data-d="cancel">ביטול</button>`,
      onAction(a, d) {
        if (a !== "ok") return true;
        const t = cleanTemplate({ id: uid("t"), title: d.querySelector("#tpl-name").value.trim() || "תבנית", desc: d.querySelector("#tpl-desc").value.trim(), cards: tcards, edges,
          tags: [...new Set(cards.flatMap((c) => c.tags))].slice(0, 6), frame: oneFrame ? { title: oneFrame.title.replace(/ · \d+\.\d+$/, ""), w: oneFrame.w, h: oneFrame.h, area: oneFrame.area } : null,
          project: proj ? k.get(proj.id) : undefined, createdAt: nowIso() });
        B.templates[t.id] = t; commit("תבנית חדשה"); setDockTab("tpl"); renderAll(); toast(`התבנית "${t.title}" נשמרה במגירה`);
        return true;
      },
    });
  }

  // ---------- opening, previewing, copying ----------
  async function copyText(text, what = "הטקסט") {
    try { await navigator.clipboard.writeText(text); toast(`${what} הועתק`); return true; } catch {}
    try {
      const ta = document.createElement("textarea"); ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select(); const ok = document.execCommand("copy"); ta.remove();
      if (ok) { toast(`${what} הועתק`); return true; }
    } catch {}
    dialog({ title: "להעתיק ידנית", body: `<p class="lb-note">הדפדפן לא איפשר להעתיק מכאן. מסמנים ומעתיקים:</p><textarea class="lb-textarea" rows="4" dir="rtl" readonly>${esc(text)}</textarea>`, foot: `<button class="bd-btn" type="button" data-d="cancel">סגירה</button>`, onOpen: (d) => d.querySelector("textarea").select() });
    return false;
  }
  function openExternal(url) { const w = window.open(url, "_blank", "noopener,noreferrer"); if (!w) toast("הדפדפן חסם חלון חדש. אפשר להעתיק את הקישור מהפרטים"); }
  function goView(view) { if (VIEW_NAMES[view]) location.hash = "#" + view; }
  function openCard(c) {
    const t = openTarget(c), r = resOf(c);
    if (!t) { openPanel("card", c.id); return; }
    if (r?.tool) { launchTool(r); return; }
    if (t.view) { goView(t.view); return; }
    if (t.command) { copyText(t.command, "הפקודה"); return; }
    if (t.url) { openExternal(t.url); return; }
    if (t.path) {
      const u = fileUrl(t.path);
      if (u) openExternal(u);
      else localOnly(t.path);
    }
  }
  function localOnly(path) {
    const facts = (SEED.resources || []).find((r) => r.id === "tool:project_server")?.tool;
    dialog({ title: "קובץ במחשב", body: `<p>הקובץ נמצא בתיקיית הפרויקט במחשב, ואין לו כתובת ברשת. אפשר לפתוח אותו דרך שרת הפרויקט המקומי:</p>
      <div class="bd-code"><code>${esc(path)}</code><button class="bd-ib" type="button" data-d="copy-path" aria-label="העתקת הנתיב">${I("copy")}</button></div>
      <p class="lb-note">אם השרת לא רץ, מפעילים אותו מתיקיית הפרויקט (או דרך הגדרת התצוגה "lumebook"):</p>
      <div class="bd-code"><code>${esc(facts?.start_cmd || "python3 tools/lumebook.py serve")}</code><button class="bd-ib" type="button" data-d="copy-cmd" aria-label="העתקת הפקודה">${I("copy")}</button></div>`,
      foot: `<a class="bd-btn is-primary" href="http://localhost:8780/${esc(path.split("/").map(encodeURIComponent).join("/"))}" target="_blank" rel="noopener">פתיחה בשרת המקומי</a><button class="bd-btn" type="button" data-d="cancel">סגירה</button>`,
      onAction(a) { if (a === "copy-path") copyText(path, "הנתיב"); if (a === "copy-cmd") copyText(facts?.start_cmd || "python3 tools/lumebook.py serve", "הפקודה"); return a === "cancel"; } });
  }
  function launchResource(ref) {
    if (ref.startsWith("card:")) { const c = B.cards[ref.slice(5)]; if (c) openCard(c); return; }
    const r = CAT.get(ref); if (!r) return;
    openCard({ ref, type: r.type, tags: [] });
  }
  async function launchTool(r) {
    openExternal(r.tool.url);
    const st = await checkTool(r);
    if (st && !st.ok) {
      dialog({ title: `${r.title} לא ענה`, body: `<p>${st.from === "server" ? "שרת הפרויקט בדק ו" : ""}הכתובת <bdi class="lb-ltr">${esc(r.tool.url)}</bdi> לא ענתה${st.from === "server" ? "." : " מהדף הזה. ייתכן שהוא פועל והדפדפן רק חוסם את הבדיקה."}</p>
        ${r.tool.runs_as_he || r.tool.runs_as ? `<p class="lb-note" dir="auto">${esc(r.tool.runs_as_he || r.tool.runs_as)}</p>` : ""}
        <p class="lb-note">בדיקה מהמסוף, מתיקיית הפרויקט:</p><div class="bd-code"><code>${esc(r.tool.status_cmd || "")}</code><button class="bd-ib" type="button" data-d="c1" aria-label="העתקה">${I("copy")}</button></div>
        <p class="lb-note">ואם הוא לא פועל:</p><div class="bd-code"><code>${esc(r.tool.start_cmd || "")}</code><button class="bd-ib" type="button" data-d="c2" aria-label="העתקה">${I("copy")}</button></div>
        <p class="lb-note">הדף לא מריץ פקודות במחשב. מעתיקים ומריצים במסוף.</p>`,
        foot: `<button class="bd-btn" type="button" data-d="cancel">סגירה</button>`,
        onAction(a) { if (a === "c1") copyText(r.tool.status_cmd, "הפקודה"); if (a === "c2") copyText(r.tool.start_cmd, "הפקודה"); return a === "cancel"; } });
    }
  }
  const toolCache = { at: 0, data: null };
  async function checkTool(r) {
    const key = r?.tool?.key; if (!key) return null;
    if (ENV.projectServer) {
      try {
        if (Date.now() - toolCache.at > 8000) { const res = await fetch("/api/local-tools", { cache: "no-store" }); toolCache.data = await res.json(); toolCache.at = Date.now(); }
        const t = (toolCache.data?.tools || []).find((x) => x.key === key);
        if (t) { ENV.localTools[key] = { ok: !!t.ok, at: nowIso(), from: "server", live: true }; live++; renderSoon(); return ENV.localTools[key]; }
      } catch {}
    }
    const ctl = new AbortController(), timer = setTimeout(() => ctl.abort(), 2500);
    try { await fetch(r.tool.ping || r.tool.url, { mode: "no-cors", cache: "no-store", signal: ctl.signal }); ENV.localTools[key] = { ok: true, at: nowIso(), from: "page", live: true }; }
    catch { ENV.localTools[key] = { ok: false, at: nowIso(), from: "page", live: true }; }
    finally { clearTimeout(timer); }
    live++; renderSoon();
    return ENV.localTools[key];
  }
  function previewCard(c) {
    const m = mediaOf(c), t = openTarget(c), r = resOf(c);
    if (c.type === "prompt" || r?.prompt) {
      const text = c.prompt || r?.prompt || "";
      dialog({ title: c.title || "פרומפט", body: `<pre class="lb-small" dir="auto" style="white-space:pre-wrap">${esc(text)}</pre>`, foot: `<button class="bd-btn is-primary" type="button" data-d="copy">העתקת הפרומפט</button><button class="bd-btn" type="button" data-d="cancel">סגירה</button>`, onAction(a) { if (a === "copy") copyText(text, "הפרומפט"); return a === "cancel"; } });
      return;
    }
    const files = m?.files?.length ? m.files : t?.url && driveId(t.url) ? [t.url] : t?.path ? [t.path] : [];
    if (!files.length && m?.published) files.push(m.published);
    let cur = 0;
    const view = (f) => {
      const did = safeHref(f) && driveId(f);
      // the file's own extension decides first; a declared kind only fills in for links without one
      const kind = did ? "drive" : extKind(f) || (m?.kind && files.length === 1 ? m.kind : null) || "other";
      const trusted = did || extKind(f) === "pdf"; // Drive's own preview page and real PDFs; every other page is sandboxed
      const u = did ? `https://drive.google.com/file/d/${did}/preview` : f === m?.published ? f : srcUrl(f, m);
      if (!u) return `<div class="bd-preview"><div style="padding:var(--sp-5);text-align:center;display:grid;gap:var(--sp-2)"><b>הקובץ נמצא במחשב</b><span class="lb-note">אפשר לראות אותו רק דרך שרת הפרויקט המקומי (<bdi class="lb-ltr">python3 tools/lumebook.py serve</bdi>, ואז הלוח בכתובת <bdi class="lb-ltr">localhost:8780</bdi>).</span><code class="lb-ltr">${esc(f)}</code></div></div>`;
      if (kind === "image") return `<div class="bd-preview"><img src="${esc(u)}" alt="${esc(c.title)}"></div>`;
      if (kind === "video") return `<div class="bd-preview"><video src="${esc(u)}" controls playsinline preload="metadata"></video></div>`;
      if (kind === "audio") return `<div class="bd-preview"><audio src="${esc(u)}" controls preload="metadata"></audio></div>`;
      if (kind === "text") return `<div class="bd-preview"><pre class="lb-small" data-src="${esc(u)}">טוען…</pre></div>`;
      if (kind === "html" || kind === "pdf" || kind === "drive") return `<div class="bd-preview"><iframe src="${esc(u)}" title="${esc(c.title)}" ${trusted ? "" : 'sandbox="allow-scripts allow-popups"'} referrerpolicy="no-referrer"></iframe></div><p class="lb-note">אם התצוגה נשארת ריקה, האתר חוסם הצגה בתוך דף אחר. אפשר לפתוח בחלון חדש.</p>`;
      return `<div class="bd-preview"><span class="lb-note">אין תצוגה מקדימה לסוג הזה</span></div>`;
    };
    const ext = (f) => { const did = safeHref(f) && driveId(f); return did ? f : f === m?.published ? f : srcUrl(f, m); };
    const gal = () => files.length > 1 ? `<div class="bd-gal" role="group" aria-label="קבצים">${files.map((f, i) => { const u = srcUrl(f, m); return `<button type="button" data-d="g${i}" aria-pressed="${i === cur}" title="${esc(f)}">${u && extKind(f) === "image" ? `<img src="${esc(u)}" alt="" loading="lazy">` : esc((f.split("/").pop() || "").slice(0, 14))}</button>`; }).join("")}</div>` : "";
    const d = dialog({
      title: c.title || sourceTitle(c) || "תצוגה מקדימה", wide: true,
      body: `<div id="pv-main">${files.length ? view(files[0]) : `<div class="bd-preview"><span class="lb-note">אין קובץ להציג</span></div>`}</div>${gal()}<p class="lb-note lb-ltr" id="pv-path" style="text-align:end">${esc(files[0] || "")}</p>`,
      foot: `${files.length && ext(files[0]) ? `<a class="bd-btn is-primary" id="pv-open" href="${esc(ext(files[0]))}" target="_blank" rel="noopener">פתיחה בחלון חדש</a>` : ""}${files[0] ? `<button class="bd-btn" type="button" data-d="copy">העתקת הנתיב</button>` : ""}<button class="bd-btn" type="button" data-d="cancel">סגירה</button>`,
      onOpen: (dd) => loadText(dd),
      onAction(a, dd) {
        if (a === "copy") copyText(files[cur], "הנתיב");
        if (a.startsWith("g")) { cur = Number(a.slice(1)); dd.querySelector("#pv-main").innerHTML = view(files[cur]); dd.querySelector("#pv-path").textContent = files[cur]; dd.querySelectorAll(".bd-gal button").forEach((b, i) => b.setAttribute("aria-pressed", String(i === cur))); const o = dd.querySelector("#pv-open"); if (o && ext(files[cur])) o.href = ext(files[cur]); loadText(dd); }
        return a === "cancel";
      },
    });
    function loadText(dd) {
      const pre = dd.querySelector("pre[data-src]"); if (!pre) return;
      fetch(pre.dataset.src, { cache: "no-store" }).then((r) => (r.ok ? r.text() : Promise.reject(r.status))).then((t) => { pre.textContent = t.slice(0, 200000); }).catch(() => { pre.textContent = "לא הצלחתי לקרוא את הקובץ מכאן."; });
    }
    return d;
  }

  // ---------- uploads (never silent: a dialog says where the file will go) ----------
  function uploadTarget() {
    if (ENV.assets) return { kind: "assets", text: "הקבצים יישמרו במאגר הקבצים של הלוח ב-claude.ai. רק מי שיש לו גישה ללוח יכול לראות אותם.", max: 20 * 1024 * 1024 };
    if (ENV.projectServer) return { kind: "inbox", text: "הקבצים יישמרו במחשב בתיקייה media/inbox של הפרויקט (קבצים שעוד לא סודרו, לפי media/README.md). הם לא עולים לשום מקום ברשת ולא נכנסים ל-git.", max: (ENV.projectServer.upload_max_mb || 300) * 1024 * 1024 };
    return null;
  }
  function uploadFiles(files, at, cardId) {
    files = [...files].filter((f) => /^(image|video|audio)\//.test(f.type) || /\.pdf$/i.test(f.name));
    if (!files.length) { toast("אפשר להעלות תמונה, וידאו, אודיו או PDF"); return; }
    const t = uploadTarget();
    if (!t) {
      dialog({ title: "אין כאן מקום לשמור קבצים", body: `<p>בעותק הזה של הלוח אין אחסון לקבצים. אפשר להעלות דרך הלוח ב-claude.ai או דרך שרת הפרויקט המקומי (<bdi class="lb-ltr">localhost:8780</bdi>).</p><p class="lb-note">אפשר גם להעלות את הקובץ ל-Drive ולהדביק כאן את הקישור בכרטיס מדיה.</p>`, foot: `<button class="bd-btn" type="button" data-d="cancel">סגירה</button>` });
      return;
    }
    const big = files.filter((f) => f.size > t.max);
    dialog({ title: `להעלות ${files.length === 1 ? "קובץ אחד" : files.length + " קבצים"}?`, body: `<p>${esc(t.text)}</p><ul class="lb-list">${files.map((f) => `<li><span dir="auto">${esc(f.name)}</span><span class="lb-meta">${Math.max(1, Math.round(f.size / 1024))} KB${f.size > t.max ? " · גדול מדי" : ""}</span></li>`).join("")}</ul>`,
      foot: `<button class="bd-btn is-primary" type="button" data-d="ok"${big.length === files.length ? " disabled" : ""}>העלאה</button><button class="bd-btn" type="button" data-d="cancel">ביטול</button>`,
      onAction(a) {
        if (a !== "ok") return true;
        (async () => {
          let i = 0;
          for (const f of files) {
            if (f.size > t.max) continue;
            try {
              const media = t.kind === "assets" ? await uploadAsset(f) : await uploadInbox(f);
              if (cardId && B.cards[cardId]) { B.cards[cardId].media = cleanMedia(media); if (!B.cards[cardId].title) B.cards[cardId].title = f.name; }
              else { const p = at || viewCenter(); newCard("media", { x: p.x - i * 30, y: p.y + i * 30 }, { title: f.name, media }); }
              i++;
            } catch (e) { toast(`ההעלאה של ${f.name} נכשלה: ${String(e?.message || e).slice(0, 80)}`); }
          }
          if (i) { commit(i === 1 ? "העלאת קובץ" : `העלאת ${i} קבצים`); renderAll({ panel: true }); toast(t.kind === "assets" ? "הקבצים נשמרו בלוח ב-claude.ai" : "הקבצים נשמרו ב-media/inbox"); }
        })();
        return true;
      } });
  }
  async function uploadAsset(f) { const r = await ENV.assets.upload(f); return { asset: r.id, url: r.url, kind: extKind(f.name) || (f.type.startsWith("image") ? "image" : f.type.startsWith("video") ? "video" : "audio") }; }
  async function uploadInbox(f) {
    const res = await fetch(`/api/media-inbox?name=${encodeURIComponent(f.name)}`, { method: "POST", headers: { "X-LumeBook-Board": "1", "Content-Type": "application/octet-stream" }, body: f });
    const j = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(j.error || res.status);
    return { src: j.path, kind: extKind(j.path) };
  }

  // ---------- dialogs and toasts ----------
  let openDialogs = 0;
  function dialog({ title, body, foot, wide, onOpen, onAction }) {
    const wrap = document.createElement("div");
    wrap.className = "bd-modal";
    wrap.innerHTML = `<div class="bd-dialog${wide ? " is-wide" : ""}" role="dialog" aria-modal="true" aria-label="${esc(title)}"><div class="bd-dialog-head"><h2 dir="auto">${esc(title)}</h2><button class="bd-ib" type="button" data-d="cancel" aria-label="סגירה">${I("close")}</button></div><div class="bd-dialog-body">${body}</div>${foot ? `<div class="bd-dialog-foot">${foot}</div>` : ""}</div>`;
    const prev = document.activeElement;
    document.body.appendChild(wrap); openDialogs++;
    const d = wrap.firstChild;
    const close = () => { if (!wrap.isConnected) return; wrap.remove(); openDialogs--; try { prev?.focus?.({ preventScroll: true }); } catch {} };
    wrap.addEventListener("click", (e) => {
      if (e.target === wrap) { close(); return; }
      const b = e.target.closest("[data-d]"); if (!b) return;
      const a = b.dataset.d;
      const done = onAction ? onAction(a, d, close) : a === "cancel";
      if (done || a === "cancel") close();
    });
    wrap.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { e.stopPropagation(); close(); }
      if (e.key === "Enter" && !e.shiftKey && e.target.tagName === "INPUT") { const ok = d.querySelector('[data-d="ok"]'); if (ok) { e.preventDefault(); ok.click(); } }
    });
    onOpen?.(d);
    (d.querySelector("input, textarea, select, .is-primary") || d.querySelector("button"))?.focus({ preventScroll: true });
    return { el: d, close };
  }
  function toast(text, action) {
    const t = document.createElement("div");
    t.className = "bd-toast"; t.setAttribute("role", "status");
    t.innerHTML = `<span dir="auto">${esc(text)}</span>${action ? `<button type="button">${esc(action.label)}</button>` : ""}`;
    if (action) t.querySelector("button").addEventListener("click", () => { action.run(); t.remove(); });
    el.toasts.appendChild(t);
    while (el.toasts.children.length > 3) el.toasts.firstChild.remove();
    setTimeout(() => t.remove(), action ? 7000 : 3600);
  }
  const toastUndo = (text) => {
    const step = H.past[H.past.length - 1];
    toast(text, { label: "ביטול", run: () => { if (step && H.past[H.past.length - 1] === step) undo(); else toast("כבר היו שינויים אחרי זה. Cmd+Z מבטל לפי הסדר"); } });
  };

  // ---------- inline editing on the canvas ----------
  function startInlineEdit(id) {
    if (readOnlyUI()) return;
    const c = B.cards[id], n = nodes.cards.get(id); if (!c || !n) return;
    const t = n.el.querySelector(".bc-title"); if (!t) return;
    U.editing = id;
    const ta = document.createElement("textarea");
    ta.className = "bc-edit"; ta.dir = "rtl"; ta.value = c.title || ""; ta.rows = c.type === "note" ? 4 : 2; ta.setAttribute("aria-label", "כותרת הכרטיס");
    ta.placeholder = TYPES[c.type].untitled;
    t.replaceWith(ta); ta.focus(); ta.select();
    let done = false;
    const finish = (save) => {
      if (done) return; done = true; U.editing = null;
      if (save && ta.value.trim() !== (c.title || "")) { c.title = ta.value.trim().slice(0, 300); c.updatedAt = nowIso(); commit("עריכת כותרת"); }
      nodes.cards.get(id) && (nodes.cards.get(id).sig = "");
      renderAll({ panel: true }); el.stage.focus({ preventScroll: true });
    };
    ta.addEventListener("keydown", (e) => { e.stopPropagation(); if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); finish(true); } if (e.key === "Escape") { e.preventDefault(); finish(false); } });
    ta.addEventListener("blur", () => finish(true));
    ta.addEventListener("pointerdown", (e) => e.stopPropagation());
  }
  function startFrameRename(id) {
    if (readOnlyUI()) return;
    const f = B.frames[id], n = nodes.frames.get(id); if (!f || !n) return;
    const name = n.el.querySelector(".bf-name span[dir]"); if (!name) return;
    const inp = document.createElement("input");
    inp.className = "bc-edit"; inp.dir = "rtl"; inp.value = f.title; inp.style.width = "18rem"; inp.style.fontSize = "20px"; inp.setAttribute("aria-label", "שם האזור");
    name.replaceWith(inp); inp.focus(); inp.select();
    let done = false;
    const finish = (save) => { if (done) return; done = true; if (save && inp.value.trim() && inp.value.trim() !== f.title) { f.title = inp.value.trim().slice(0, 120); commit("שם אזור"); } n.sig = ""; renderAll({ panel: true }); el.stage.focus({ preventScroll: true }); };
    inp.addEventListener("keydown", (e) => { e.stopPropagation(); if (e.key === "Enter") finish(true); if (e.key === "Escape") finish(false); });
    inp.addEventListener("blur", () => finish(true));
    inp.addEventListener("pointerdown", (e) => e.stopPropagation());
  }
  function startLabelEdit(eid) {
    if (readOnlyUI()) return;
    const e = B.edges[eid]; if (!e) return;
    let l = nodes.labels.get(eid);
    if (!l) { const geo = edgeGeom(B.cards[e.from], B.cards[e.to]); l = document.createElement("div"); l.className = "bl-lab is-sel"; l.style.left = geo.mid.x + "px"; l.style.top = geo.mid.y + "px"; el.labels.appendChild(l); nodes.labels.set(eid, l); }
    l.innerHTML = `<input dir="rtl" aria-label="תווית החיבור" value="${esc(e.label)}" placeholder="תווית">`;
    const inp = l.querySelector("input"); inp.focus(); inp.select();
    let done = false;
    const finish = (save) => { if (done) return; done = true; l.innerHTML = ""; if (save && inp.value.trim() !== e.label) { e.label = inp.value.trim().slice(0, 80); commit("תווית חיבור"); } if (!e.label) { l.remove(); nodes.labels.delete(eid); } renderAll({ panel: true }); el.stage.focus({ preventScroll: true }); };
    inp.addEventListener("keydown", (ev) => { ev.stopPropagation(); if (ev.key === "Enter") finish(true); if (ev.key === "Escape") finish(false); });
    inp.addEventListener("blur", () => finish(true));
    inp.addEventListener("pointerdown", (ev) => ev.stopPropagation());
  }

  // ---------- pointer gestures ----------
  let G = null;
  const pointers = new Map();
  el.stage.addEventListener("pointerdown", (e) => {
    if (!B || e.button === 2) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2) {
      if (G?.moved && (G.kind === "drag" || G.kind === "resize")) commit(G.kind === "drag" ? "הזזה" : "שינוי גודל");
      el.cards.querySelectorAll(".is-dragging").forEach((n) => n.classList.remove("is-dragging"));
      const [a, b] = [...pointers.values()];
      G = { kind: "pinch", d0: Math.hypot(a.x - b.x, a.y - b.y), z0: U.view.z, tx0: U.view.tx, ty0: U.view.ty, mid0: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }, moved: true };
      return;
    }
    const t = e.target;
    if (t.closest(".bc-act, .bc-edit, input, textarea, select, a, .bd-ctx, .bd-zoom, .bd-banner")) return;
    if (!isTyping(document.activeElement) || !el.stage.contains(document.activeElement)) el.stage.focus({ preventScroll: true });
    const sx = e.clientX, sy = e.clientY, w = toWorld(sx, sy);
    const base = { sx, sy, w0: w, moved: false, pid: e.pointerId };
    const ro = readOnlyUI();
    const handle = t.closest(".bh");
    if (handle && !ro) { const id = handle.dataset.id, o = B.cards[id] || B.frames[id]; G = { ...base, kind: "resize", id, h: handle.dataset.h, r0: rectOf(o), isFrame: !!B.frames[id] }; capture(e); return; }
    const conn = t.closest(".bh-conn");
    if (conn && !ro) { G = { ...base, kind: "connect", from: conn.dataset.conn }; capture(e); return; }
    if (U.space || U.tool === "hand" || e.button === 1) { G = { ...base, kind: "pan", tx0: U.view.tx, ty0: U.view.ty }; el.stage.classList.add("is-panning"); capture(e); return; }
    const card = t.closest(".bc");
    if (card) {
      const id = card.dataset.id;
      if (U.connectFrom) { const from = U.connectFrom; U.connectFrom = null; if (from !== id) connect(from, id); renderBar(); return; }
      const add = e.shiftKey || e.metaKey || e.ctrlKey;
      let clickOnly = null;
      if (add) { if (U.sel.has(id)) U.sel.delete(id); else U.sel.add(id); U.selEdge = null; }
      else if (!U.sel.has(id)) selectOnly(id);
      else clickOnly = id;
      if (U.panel && U.panel.kind === "card" && U.panel.id !== id && U.sel.size === 1) openPanel("card", id, false);
      startDrag(base, clickOnly, add);
      capture(e); renderAll(); return;
    }
    const fname = t.closest(".bf-name");
    if (fname) {
      const id = fname.dataset.frame, add = e.shiftKey || e.metaKey || e.ctrlKey;
      if (add) { if (U.sel.has(id)) U.sel.delete(id); else U.sel.add(id); } else if (!U.sel.has(id)) selectOnly(id);
      startDrag(base, U.sel.size > 1 && !add ? id : null, add);
      capture(e); renderAll(); return;
    }
    const edge = t.closest("[data-edge], .be");
    if (edge) { const id = edge.dataset.edge || edge.closest(".be")?.dataset.id; if (id && B.edges[id]) { U.sel.clear(); U.selEdge = id; if (U.panel) openPanel("edge", id, false); renderAll(); } return; }
    if (U.connectFrom) { U.connectFrom = null; renderBar(); }
    if (e.pointerType === "touch") { G = { ...base, kind: "pan", tx0: U.view.tx, ty0: U.view.ty, tap: true }; capture(e); return; }
    G = { ...base, kind: "marquee", base: e.shiftKey || e.metaKey ? new Set(U.sel) : new Set() };
    capture(e);
  });
  function capture(e) { try { el.stage.setPointerCapture(e.pointerId); } catch {} }
  function startDrag(base, clickOnly, additive) {
    if (readOnlyUI()) { G = { ...base, kind: "noop" }; return; }
    const cards = new Map(), frames = new Map();
    for (const id of U.sel) {
      if (B.cards[id]) cards.set(id, B.cards[id]);
      if (B.frames[id]) { frames.set(id, B.frames[id]); const m = frameMembers(B.frames[id]); m.cards.forEach((c) => cards.set(c.id, c)); m.frames.forEach((f) => frames.set(f.id, f)); }
    }
    const items = [...[...frames.values()].map((f) => ({ kind: "f", id: f.id, x0: f.x, y0: f.y })), ...[...cards.values()].map((c) => ({ kind: "c", id: c.id, x0: c.x, y0: c.y }))];
    G = { ...base, kind: "drag", items, clickOnly, additive, primary: items.find((i) => U.sel.has(i.id)) || items[0] };
  }
  el.stage.addEventListener("pointermove", (e) => {
    if (pointers.has(e.pointerId)) pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (!G) { if (U.connectFrom) drawTemp(U.connectFrom, toWorld(e.clientX, e.clientY), e); return; }
    if (G.kind === "pinch") {
      if (pointers.size < 2) return;
      const [a, b] = [...pointers.values()], d = Math.hypot(a.x - b.x, a.y - b.y), mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }, r = stageRect();
      const nz = clamp(G.z0 * d / (G.d0 || 1), 0.08, 2.5), wx = (G.mid0.x - r.left - G.tx0) / G.z0, wy = (G.mid0.y - r.top - G.ty0) / G.z0;
      U.view = { z: nz, tx: mid.x - r.left - wx * nz, ty: mid.y - r.top - wy * nz }; applyView(); return;
    }
    if (e.pointerId !== G.pid) return;
    const dxs = e.clientX - G.sx, dys = e.clientY - G.sy;
    if (!G.moved && Math.hypot(dxs, dys) < 4) return;
    if (!G.moved) { G.moved = true; el.ctx.hidden = true; if (G.kind === "drag") { for (const it of G.items) if (it.kind === "c" && B.cards[it.id]) { B.cards[it.id].z = ++zTop; const n = nodes.cards.get(it.id); if (n) { n.el.style.zIndex = String(zTop); n.el.classList.add("is-dragging"); } } } }
    const w = toWorld(e.clientX, e.clientY);
    let dx = w.x - G.w0.x, dy = w.y - G.w0.y;
    if (G.kind === "pan") { U.view.tx = G.tx0 + dxs; U.view.ty = G.ty0 + dys; applyView(); return; }
    if (G.kind === "drag") {
      if (prefs.snap && G.primary) { dx = snapTo(G.primary.x0 + dx) - G.primary.x0; dy = snapTo(G.primary.y0 + dy) - G.primary.y0; }
      for (const it of G.items) { const o = it.kind === "c" ? B.cards[it.id] : B.frames[it.id]; if (o) { o.x = it.x0 + dx; o.y = it.y0 + dy; } }
      renderMoving(); return;
    }
    if (G.kind === "resize") {
      const o = B.cards[G.id] || B.frames[G.id], r = G.r0, minW = G.isFrame ? 300 : 140, minH = G.isFrame ? 200 : 90;
      if (!o) { G = null; return; }
      let { x, y, w: ww, h } = r;
      if (G.h.includes("e")) ww = r.w + dx; if (G.h.includes("w")) { ww = r.w - dx; x = r.x + dx; }
      if (G.h.includes("s")) h = r.h + dy; if (G.h.includes("n")) { h = r.h - dy; y = r.y + dy; }
      if (prefs.snap) { const x2 = snapTo(x + ww), y2 = snapTo(y + h); x = snapTo(x); y = snapTo(y); ww = x2 - x; h = y2 - y; }
      if (ww < minW) { if (G.h.includes("w")) x = r.x + r.w - minW; ww = minW; }
      if (h < minH) { if (G.h.includes("n")) y = r.y + r.h - minH; h = minH; }
      Object.assign(o, { x, y, w: ww, h });
      const n = (G.isFrame ? nodes.frames : nodes.cards).get(G.id); if (n) placeNode(n.el, o);
      renderEdges(); renderHandles(); return;
    }
    if (G.kind === "connect") { drawTemp(G.from, w, e); return; }
    if (G.kind === "marquee") {
      const r = stageRect(), x1 = Math.min(G.sx, e.clientX) - r.left, y1 = Math.min(G.sy, e.clientY) - r.top;
      Object.assign(el.marquee.style, { left: x1 + "px", top: y1 + "px", width: Math.abs(dxs) + "px", height: Math.abs(dys) + "px" }); el.marquee.hidden = false;
      const a = toWorld(Math.min(G.sx, e.clientX), Math.min(G.sy, e.clientY)), b = toWorld(Math.max(G.sx, e.clientX), Math.max(G.sy, e.clientY));
      const box = { x: a.x, y: a.y, w: b.x - a.x, h: b.y - a.y };
      const ids = new Set(G.base);
      for (const c of Object.values(B.cards)) if (hits(box, c)) ids.add(c.id);
      for (const f of Object.values(B.frames)) if (contains(box, f)) ids.add(f.id);
      U.sel = ids; U.selEdge = null; flagCards(); renderFrames(); renderHandles();
    }
  });
  function drawTemp(from, w, e) {
    const a = B.cards[from]; if (!a) return;
    const p = anchor(a, w.x, w.y);
    el.temp.setAttribute("d", `M${p.x},${p.y} L${w.x},${w.y}`);
    const under = document.elementFromPoint(e.clientX, e.clientY)?.closest?.(".bc");
    el.cards.querySelectorAll(".is-target").forEach((n) => n.classList.remove("is-target"));
    if (under && under.dataset.id !== from) under.classList.add("is-target");
  }
  function endPointer(e) {
    pointers.delete(e.pointerId);
    if (!G) return;
    if (G.kind === "pinch") { if (pointers.size < 2) G = null; return; }
    if (e.pointerId !== G.pid) return;
    const g = G; G = null;
    el.stage.classList.remove("is-panning");
    el.marquee.hidden = true;
    el.cards.querySelectorAll(".is-dragging").forEach((n) => n.classList.remove("is-dragging"));
    if (g.kind === "drag") {
      if (g.moved) commit(g.items.length > 1 ? `הזזת ${g.items.length} פריטים` : "הזזה");
      else if (g.clickOnly && !g.additive) selectOnly(g.clickOnly);
      renderAll();
    } else if (g.kind === "resize") { if (g.moved) commit("שינוי גודל"); renderAll(); }
    else if (g.kind === "connect") {
      el.temp.setAttribute("d", "");
      const under = document.elementFromPoint(e.clientX, e.clientY)?.closest?.(".bc");
      el.cards.querySelectorAll(".is-target").forEach((n) => n.classList.remove("is-target"));
      if (!g.moved) { U.connectFrom = g.from; renderBar(); toast("לוחצים על הכרטיס שרוצים לחבר אליו. Esc לביטול"); return; }
      if (under && under.dataset.id !== g.from) connect(g.from, under.dataset.id);
      else if (!under) {
        const w = toWorld(e.clientX, e.clientY), c = newCard("note", w);
        const ed = { id: uid("e"), from: g.from, to: c.id, label: "", kind: "manual" }; B.edges[ed.id] = ed;
        commit("פתק מחובר"); selectOnly(c.id); renderAll(); startInlineEdit(c.id);
      }
    } else if (g.kind === "marquee") { if (!g.moved && !g.base.size) { U.sel.clear(); U.selEdge = null; if (U.panel) closePanel(); } renderAll(); }
    else if (g.kind === "pan") { if (g.tap && !g.moved) { U.sel.clear(); U.selEdge = null; renderAll(); } }
  }
  el.stage.addEventListener("pointerup", endPointer);
  el.stage.addEventListener("pointercancel", endPointer);
  el.stage.addEventListener("lostpointercapture", (e) => { if (G && e.pointerId === G.pid && G.kind !== "pinch") endPointer(e); });
  el.stage.addEventListener("wheel", (e) => {
    if (!B || e.target.closest(".bd-ctx, .bd-banner, .bc-edit")) return;
    e.preventDefault();
    const r = stageRect();
    if (e.ctrlKey || e.metaKey) zoomAt(e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * (e.deltaMode ? 0.05 : 0.0025) * (e.ctrlKey && !e.metaKey ? 4 : 1)));
    else { const k = e.deltaMode ? 16 : 1; U.view.tx -= (e.shiftKey ? e.deltaY : e.deltaX) * k; U.view.ty -= (e.shiftKey ? 0 : e.deltaY) * k; applyView(); }
  }, { passive: false });
  el.stage.addEventListener("dblclick", (e) => {
    if (!B || readOnlyUI()) return;
    if (e.target.closest(".bc-act, .bd-ctx, .bd-zoom, input, textarea")) return;
    const card = e.target.closest(".bc"), fname = e.target.closest(".bf-name"), lab = e.target.closest("[data-edge]"), edge = e.target.closest(".be");
    if (card) { startInlineEdit(card.dataset.id); return; }
    if (fname) { startFrameRename(fname.dataset.frame); return; }
    if (lab || edge) { startLabelEdit(lab?.dataset.edge || edge.dataset.id); return; }
    if (e.target.closest(".bh, .bh-conn")) return;
    const c = newCard("note", toWorld(e.clientX, e.clientY)); commit("פתק חדש"); selectOnly(c.id); renderAll(); startInlineEdit(c.id);
  });
  el.stage.addEventListener("click", (e) => {
    const b = e.target.closest(".bc-act"); if (!b) return;
    const id = b.closest(".bc")?.dataset.id, c = B.cards[id]; if (!c) return;
    e.stopPropagation();
    if (b.dataset.act === "open") openCard(c);
    if (b.dataset.act === "preview") previewCard(c);
    if (b.dataset.act === "details") { selectOnly(id); openPanel("card", id); renderAll(); }
  });
  el.stage.addEventListener("focusin", (e) => {
    const card = e.target.closest?.(".bc"); if (!card || G) return;
    const id = card.dataset.id;
    if (!U.sel.has(id) && !e.target.closest(".bc-act")) { selectOnly(id); flagCards(); renderHandles(); renderCtx(); ensureVisible(B.cards[id]); }
  });
  function ensureVisible(o) {
    if (!o || U.mode !== "canvas") return;
    const s = stageRect(), a = toScreen(o.x, o.y), b = toScreen(o.x + o.w, o.y + o.h), m = 40;
    let dx = 0, dy = 0;
    if (a.x < m) dx = m - a.x; else if (b.x > s.width - m) dx = s.width - m - b.x;
    if (a.y < m) dy = m - a.y; else if (b.y > s.height - m) dy = s.height - m - b.y;
    if (dx || dy) { U.view.tx += dx; U.view.ty += dy; applyView(); }
  }

  // drag from the dock (resources, templates), files and links from outside
  el.stage.addEventListener("dragover", (e) => { if (readOnlyUI()) return; e.preventDefault(); e.dataTransfer.dropEffect = "copy"; });
  el.stage.addEventListener("drop", (e) => {
    if (readOnlyUI()) return;
    e.preventDefault();
    const at = toWorld(e.clientX, e.clientY), dt = e.dataTransfer;
    const res = dt.getData("application/x-lb-res"), tpl = dt.getData("application/x-lb-tpl");
    if (res) { const c = addFromResource(res, at); if (c) toast(`"${c.title}" נוסף ללוח`); return; }
    if (tpl) { instantiate(tpl, at); return; }
    if (dt.files?.length) { uploadFiles(dt.files, at); return; }
    const u = (dt.getData("text/uri-list") || dt.getData("text/plain") || "").trim().split(/\s+/)[0];
    if (safeHref(u)) { addCard("link", at, { url: safeHref(u), title: host(u) }); }
  });
  document.addEventListener("paste", (e) => {
    if (!U.visible || !B || readOnlyUI() || isTyping(document.activeElement) || openDialogs) return;
    const files = e.clipboardData?.files;
    if (files?.length) { e.preventDefault(); uploadFiles(files, viewCenter()); return; }
    const text = (e.clipboardData?.getData("text/plain") || "").trim();
    if (!text) return;
    e.preventDefault();
    try { const j = JSON.parse(text); if (j && j.lumebookBoardClip === 1) { pasteClip(j); return; } } catch {}
    if (safeHref(text) && !/\s/.test(text)) addCard("link", viewCenter(), { url: safeHref(text), title: host(text) });
    else { const c = newCard("note", viewCenter(), { title: text.slice(0, 300), desc: text.length > 300 ? text.slice(300, 8300) : "" }); commit("הדבקה"); selectOnly(c.id); renderAll(); }
  });
  let CLIP = null;
  function copySelection() {
    if (!U.sel.size) return;
    const { cards, frames } = expandSelection();
    const ids = new Set(cards.map((c) => c.id));
    CLIP = { lumebookBoardClip: 1, cards, frames, edges: Object.values(B.edges).filter((e) => ids.has(e.from) && ids.has(e.to)) };
    const clip = CLIP; clip.written = false;
    try { navigator.clipboard.writeText(JSON.stringify(clip)).then(() => { clip.written = true; }, () => {}); } catch {}
    toast(cards.length === 1 ? "כרטיס אחד הועתק" : `${cards.length} כרטיסים הועתקו`);
  }
  function pasteClip(clip) {
    clip = clip || CLIP; if (!clip || readOnlyUI()) return;
    const raw = cleanBoard({ cards: Object.fromEntries((clip.cards || []).map((c) => [c.id, c])), frames: Object.fromEntries((clip.frames || []).map((f) => [f.id, f])), edges: Object.fromEntries((clip.edges || []).map((e) => [e.id, e])) }).board;
    const items = [...Object.values(raw.cards), ...Object.values(raw.frames)], r = bbox(items); if (!r) return;
    const p = viewCenter(), dx = snapTo(p.x - (r.x + r.w / 2)), dy = snapTo(p.y - (r.y + r.h / 2));
    const out = cloneItems(Object.values(raw.cards), Object.values(raw.frames), dx, dy, Object.values(raw.edges));
    out.cards.forEach((c) => (B.cards[c.id] = c)); out.frames.forEach((f) => (B.frames[f.id] = f)); out.edges.forEach((e) => (B.edges[e.id] = e));
    commit("הדבקה"); setSelection([...out.cards.map((c) => c.id), ...out.frames.map((f) => f.id)]); renderAll();
  }

  // ---------- keyboard ----------
  window.addEventListener("keydown", (e) => {
    if (!U.visible || !B) return;
    if (openDialogs) return;
    const typing = isTyping(e.target);
    const mod = e.metaKey || e.ctrlKey;
    if (typing) { if (e.key === "Escape" && e.target === el.q) { el.q.value = ""; closeResults(); el.stage.focus(); } return; }
    if (closeMenus(e)) return;
    // physical key first (letter shortcuts work on a Hebrew layout too), the character when a device sends no code
    const k = e.code || (/^[a-z]$/i.test(e.key) ? "Key" + e.key.toUpperCase() : { " ": "Space", "/": "Slash", "?": "Slash", "+": "Equal", "=": "Equal", "-": "Minus", "!": "Digit1", "@": "Digit2" }[e.key] || ""), sel = [...U.sel];
    if (mod && k === "KeyZ") { e.preventDefault(); if (e.shiftKey) redo(); else undo(); return; }
    if (mod && k === "KeyY") { e.preventDefault(); redo(); return; }
    if (mod && k === "KeyK") { e.preventDefault(); el.q.focus(); el.q.select(); return; }
    if (mod && k === "KeyA" && U.mode === "canvas") { e.preventDefault(); U.sel = new Set(Object.keys(B.cards)); U.selEdge = null; renderAll(); return; }
    if (mod && k === "KeyD") { e.preventDefault(); duplicateSelection(); return; }
    if (mod && k === "KeyC") { if (U.sel.size) { e.preventDefault(); copySelection(); } return; }
    if (mod && k === "KeyV") { if (CLIP && !CLIP.written) { e.preventDefault(); pasteClip(); } return; }
    if (mod && k === "KeyS") { e.preventDefault(); flush(); return; }
    if (mod && (k === "Digit0" || k === "Numpad0")) { e.preventDefault(); const s = stageRect(); zoomAt(s.width / 2, s.height / 2, 1 / U.view.z); return; }
    if (mod) return;
    if (e.key === "Escape") { if (U.connectFrom) { U.connectFrom = null; el.temp.setAttribute("d", ""); renderBar(); return; } if (U.panel) { closePanel(); return; } U.sel.clear(); U.selEdge = null; renderAll(); return; }
    if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); deleteSelection(); return; }
    if (k === "Space") { e.preventDefault(); if (!U.space) { U.space = true; el.stage.classList.add("is-space"); } return; }
    const onControl = e.target !== el.stage && !e.target.classList?.contains("bc") && e.target.closest?.("button, a, select, summary, [role=button], [role=menuitem], [role=option], [role=tab]");
    if (onControl && (e.key === "Enter" || e.key === " " || k === "Space")) return;
    if (e.key === "Enter" && sel.length === 1) { e.preventDefault(); if (B.cards[sel[0]]) openPanel("card", sel[0]); else if (B.frames[sel[0]]) openPanel("frame", sel[0]); renderAll(); return; }
    if (e.key === "Enter" && U.selEdge) { e.preventDefault(); openPanel("edge", U.selEdge); return; }
    if (k === "F2" && sel.length === 1) { e.preventDefault(); if (B.cards[sel[0]]) startInlineEdit(sel[0]); else startFrameRename(sel[0]); return; }
    if (e.key.startsWith("Arrow") && sel.length && U.mode === "canvas" && !readOnlyUI()) {
      e.preventDefault();
      const st = (prefs.snap ? GRID : 4) * (e.shiftKey ? 5 : 1), dx = e.key === "ArrowLeft" ? -st : e.key === "ArrowRight" ? st : 0, dy = e.key === "ArrowUp" ? -st : e.key === "ArrowDown" ? st : 0;
      const { cards, frames } = expandSelection();
      for (const o of [...cards, ...frames]) { o.x += dx; o.y += dy; }
      commit("הזזה", "nudge"); renderAll(); return;
    }
    if (e.shiftKey && k === "Digit1") { e.preventDefault(); fitRect(allRect()); return; }
    if (e.shiftKey && k === "Digit2") { e.preventDefault(); fitRect(bbox(selItems()) || allRect(), 1.2); return; }
    if ((e.shiftKey && k === "KeyH") || k === "Home") { e.preventDefault(); goHome(); return; }
    if (k === "Equal" || k === "NumpadAdd") { e.preventDefault(); zoomBy(1.2); return; }
    if (k === "Minus" || k === "NumpadSubtract") { e.preventDefault(); zoomBy(1 / 1.2); return; }
    if (e.key === "?" || (k === "Slash" && e.shiftKey)) { e.preventDefault(); showKeys(); return; }
    if (e.shiftKey || e.altKey) return;
    const map = { KeyV: () => setTool("select"), KeyH: () => setTool("hand"), KeyN: () => addCard("note"), KeyT: () => addCard("task"), KeyL: () => addCard("link"),
      KeyF: () => frameAround(sel.length ? sel : null), KeyG: () => { prefs.snap = !prefs.snap; savePrefs(); renderBar(); toast(prefs.snap ? "הצמדה לרשת פועלת" : "הצמדה לרשת כבויה"); },
      KeyC: () => { if (sel.length === 1 && B.cards[sel[0]]) { U.connectFrom = sel[0]; renderBar(); toast("לוחצים על הכרטיס שרוצים לחבר אליו. Esc לביטול"); } },
      KeyP: () => { if (sel.length === 1 && B.cards[sel[0]] && canPreview(B.cards[sel[0]])) previewCard(B.cards[sel[0]]); },
      KeyO: () => { if (sel.length === 1 && B.cards[sel[0]]) openCard(B.cards[sel[0]]); } };
    if (map[k] && U.mode === "canvas") { e.preventDefault(); map[k](); }
    else if (map[k] && ["KeyN", "KeyT", "KeyL"].includes(k)) { e.preventDefault(); map[k](); }
  });
  window.addEventListener("keyup", (e) => { if (e.code === "Space") { U.space = false; el.stage.classList.remove("is-space"); } });
  window.addEventListener("blur", () => { U.space = false; el.stage.classList.remove("is-space"); });
  function setTool(t) { U.tool = t; renderBar(); }

  // ---------- toolbar, menus, search ----------
  let menu = null;
  function closeMenus(e) { if (menu && e?.key === "Escape") { menu.remove(); menu = null; return true; } return false; }
  function popMenu(anchorEl, html, onPick, cls = "") {
    if (menu) menu.remove();
    menu = document.createElement("div");
    menu.className = `bd-pop ${cls}`; menu.setAttribute("role", "menu"); menu.innerHTML = html;
    el.bd.appendChild(menu);
    const a = anchorEl.getBoundingClientRect(), r = el.bd.getBoundingClientRect(), mw = menu.offsetWidth;
    menu.style.top = (a.bottom - r.top + 6) + "px";
    menu.style.left = clamp(a.right - r.left - mw, 8, r.width - mw - 8) + "px";
    menu.addEventListener("click", (e) => { const b = e.target.closest("[data-m]"); if (!b) return; const keep = onPick(b.dataset.m, b, e); if (!keep) { menu?.remove(); menu = null; } });
    menu.querySelector("button, input")?.focus({ preventScroll: true });
    return menu;
  }
  document.addEventListener("pointerdown", (e) => { if (menu && !menu.contains(e.target) && !e.target.closest('[data-a="add"], [data-a="more"], [data-a="filters"], [data-a="save-info"]')) { menu.remove(); menu = null; } }, true);
  const KEYS = { note: "N", task: "T", link: "L" };
  el.bd.addEventListener("click", (e) => {
    const b = e.target.closest("[data-a]"); if (!b || !el.bd.contains(b)) return;
    const a = b.dataset.a;
    const S1 = [...U.sel];
    switch (a) {
      case "dock": setDock(el.dock.dataset.open !== "true"); break;
      case "tool-select": setTool("select"); break;
      case "tool-hand": setTool("hand"); break;
      case "undo": undo(); break;
      case "redo": redo(); break;
      case "deps": prefs.showDeps = !prefs.showDeps; savePrefs(); renderAll(); toast(prefs.showDeps ? "התלויות מהרישום מוצגות" : "התלויות מהרישום מוסתרות. החיבורים שלך נשארים"); break;
      case "snap": prefs.snap = !prefs.snap; savePrefs(); renderBar(); break;
      case "mode-canvas": setMode("canvas"); break;
      case "mode-list": setMode("list"); break;
      case "zoom-in": zoomBy(1.2); break;
      case "zoom-out": zoomBy(1 / 1.2); break;
      case "fit": fitRect(allRect()); break;
      case "home": goHome(); break;
      case "keys": showKeys(); break;
      case "add": popMenu(b, ADDABLE.map((t) => `<button class="bd-mi" type="button" role="menuitem" data-m="${t}"><span class="lb-tile is-soft lb-cat-0">${I(TYPES[t].icon)}</span><span>${esc(TYPES[t].label)}</span>${KEYS[t] ? `<kbd>${KEYS[t]}</kbd>` : ""}</button>`).join("")
        + `<hr><button class="bd-mi" type="button" data-m="frame"><span class="lb-tile is-soft lb-cat-0">${I("frame")}</span><span>אזור</span><kbd>F</kbd></button><button class="bd-mi" type="button" data-m="upload"><span class="lb-tile is-soft lb-cat-0">${I("upload")}</span><span>העלאת קובץ</span></button><button class="bd-mi" type="button" data-m="tpl"><span class="lb-tile is-soft lb-cat-0">${I("tpl")}</span><span>מתבנית…</span></button>`,
        (m) => { if (m === "frame") frameAround(S1.length ? S1 : null); else if (m === "upload") pickFiles(); else if (m === "tpl") { setDock(true); setDockTab("tpl"); } else addCard(m); }); break;
      case "more": popMenu(b, [
        ["export", "download", "ייצוא הלוח (JSON)"], ["import", "upload", "ייבוא לוח…"], ["backups", "backup", "גיבויים בדפדפן הזה"], ["set-home", "home", "לשמור את התצוגה הזאת כבית"],
        ["reset", "undo", "איפוס ללוח ההתחלתי…"], ["where", "help", "איפה השינויים נשמרים"]].map(([m, ic, t]) => `<button class="bd-mi" type="button" role="menuitem" data-m="${m}"><span class="lb-tile is-soft lb-cat-0">${I(ic)}</span><span>${t}</span></button>`).join(""),
        (m) => { ({ export: exportBoard, import: importBoard, backups: showBackups, "set-home": setHome, reset: resetBoard, where: saveInfo })[m](); }); break;
      case "save-info": if (SAVE.state === "error") flush(); else saveInfo(); break;
      case "filters": filtersMenu(b); break;
      case "remote-load": U.editing = null; reloadRemote(true); break;
      case "remote-keep": B.rev = Math.max(B.rev || 0, remote?.rev || 0); remote = null; renderBanner(); markDirty(); break;
      case "banner-close": ENV.bannerMsg = ""; renderBanner(); break;
      // context toolbar
      case "ctx-open": if (B.cards[S1[0]]) openCard(B.cards[S1[0]]); break;
      case "ctx-preview": if (B.cards[S1[0]]) previewCard(B.cards[S1[0]]); break;
      case "ctx-details": if (B.cards[S1[0]]) openPanel("card", S1[0]); else if (B.frames[S1[0]]) openPanel("frame", S1[0]); renderAll(); break;
      case "ctx-pin": { const c = B.cards[S1[0]]; if (c) togglePin(c.ref || "card:" + c.id); break; }
      case "connect": if (S1.length === 1) { U.connectFrom = S1[0]; renderBar(); toast("לוחצים על הכרטיס שרוצים לחבר אליו. Esc לביטול"); } break;
      case "duplicate": duplicateSelection(); break;
      case "delete": deleteSelection(); break;
      case "fit-sel": fitRect(bbox(selItems()), 1); break;
      case "save-tpl": saveTemplateFromSelection(); break;
      case "frame-sel": frameAround(S1); break;
      case "align-r": case "align-l": case "align-c": case "align-t": case "align-b": case "align-m": align(a.slice(-1)); break;
      case "dist-h": align("h"); break;
      case "dist-v": align("v"); break;
      case "edge-label": if (U.selEdge) startLabelEdit(U.selEdge); break;
      case "edge-swap": { const ed = B.edges[U.selEdge]; if (ed) { [ed.from, ed.to] = [ed.to, ed.from]; commit("היפוך כיוון"); renderAll({ panel: true }); } break; }
      case "edge-details": if (U.selEdge) openPanel("edge", U.selEdge); break;
    }
  });
  function setMode(m, remember = true) {
    U.mode = m;
    if (remember) { prefs.mode = m; savePrefs(); }
    el.bd.dataset.mode = m; el.stage.hidden = m !== "canvas"; el.list.hidden = m !== "list";
    if (m === "canvas") requestAnimationFrame(() => { if (!U.viewSet && U.visible && B) initView(); else applyView(); renderAll(); });
    renderAll();
  }
  function setDock(open) { el.dock.dataset.open = String(open); prefs.dockOpen = open; savePrefs(); renderBar(); renderDock(); }
  function setDockTab(t) { prefs.dockTab = t; savePrefs(); renderDock(); }
  function pickFiles(cardId) {
    if (!uploadTarget()) { uploadFiles([], null, cardId); return; }
    const inp = document.createElement("input"); inp.type = "file"; inp.multiple = !cardId; inp.accept = "image/*,video/*,audio/*,application/pdf";
    inp.addEventListener("change", () => uploadFiles(inp.files, null, cardId)); inp.click();
  }
  function filtersMenu(anchorEl) {
    const tags = [...new Set(Object.values(B.cards).flatMap((c) => c.tags))].sort((a, b) => a.localeCompare(b, "he"));
    const projects = Object.values(B.cards).filter((c) => c.type === "project");
    const f = U.filters;
    const html = `<div class="bd-mlabel">סוג</div>${Object.entries(TYPES).map(([k, t]) => `<label class="lb-check"><input type="checkbox" data-ft="${k}" ${f.types.has(k) ? "checked" : ""}><span>${t.label}</span></label>`).join("")}
      <hr><div class="bd-mlabel">מצב משימה</div>${Object.entries(STATUS).map(([k, [l]]) => `<label class="lb-check"><input type="checkbox" data-fs="${k}" ${f.status.has(k) ? "checked" : ""}><span>${l}</span></label>`).join("")}
      <hr><label class="lb-field" style="padding:0 .6rem">תגית<select class="lb-select" data-fg><option value="">הכול</option>${tags.map((t) => `<option ${t === f.tag ? "selected" : ""}>${esc(t)}</option>`).join("")}</select></label>
      <label class="lb-field" style="padding:0 .6rem">פרויקט<select class="lb-select" data-fp><option value="">הכול</option>${projects.map((p) => `<option value="${esc(p.id)}" ${p.id === f.project ? "selected" : ""}>${esc(p.title || "ללא שם")}</option>`).join("")}</select></label>
      <label class="lb-field" style="padding:0 .6rem">מקור<select class="lb-select" data-fo><option value="">הכול</option><option value="src" ${f.source === "src" ? "selected" : ""}>מחוברים למקור בפרויקט</option><option value="mine" ${f.source === "mine" ? "selected" : ""}>כרטיסים שלי</option></select></label>
      <hr><button class="bd-mi" type="button" data-m="clear"><span>ניקוי הסינון</span></button>`;
    const m = popMenu(anchorEl, html, (x) => { if (x === "clear") { U.filters = { types: new Set(), status: new Set(), tag: "", project: "", source: "" }; renderAll(); } return false; });
    m.addEventListener("change", (e) => {
      const t = e.target;
      if (t.dataset.ft) t.checked ? f.types.add(t.dataset.ft) : f.types.delete(t.dataset.ft);
      if (t.dataset.fs) t.checked ? f.status.add(t.dataset.fs) : f.status.delete(t.dataset.fs);
      if ("fg" in t.dataset) f.tag = t.value; if ("fp" in t.dataset) f.project = t.value; if ("fo" in t.dataset) f.source = t.value;
      renderAll();
    });
  }

  // search across cards, frames, tools and templates
  let results = null, resIdx = 0;
  const hay = (c) => { const r = resOf(c); return norm([c.title, c.desc, c.tags.join(" "), c.url, c.prompt, (c.checklist || []).map((x) => x.text).join(" "), r?.title, r?.summary, r?.url, r?.path, r?.command, TYPES[c.type]?.label].join(" ")); };
  function search(q) {
    const toks = norm(q).split(/\s+/).filter(Boolean); if (!toks.length) return [];
    const ok = (h) => toks.every((t) => h.includes(t));
    const out = [];
    for (const c of Object.values(B.cards)) { const h = hay(c); if (ok(h)) out.push({ kind: "card", id: c.id, title: c.title || sourceTitle(c) || TYPES[c.type].untitled, sub: `${TYPES[c.type].label}${frameOf(c) ? " · " + frameOf(c).title : ""}`, icon: TYPES[c.type].icon, score: norm(c.title).includes(toks[0]) ? 0 : 1 }); }
    for (const f of Object.values(B.frames)) if (ok(norm(f.title))) out.push({ kind: "frame", id: f.id, title: f.title, sub: "אזור", icon: "frame", score: 0 });
    const onBoard = new Set(Object.values(B.cards).map((c) => c.ref).filter(Boolean));
    for (const r of CAT.values()) if (!onBoard.has(r.id) && ok(norm([r.title, r.summary, r.url, r.path, r.command].join(" ")))) out.push({ kind: "res", id: r.id, title: r.title, sub: `לא בלוח · ${KIND_GROUP[r.kind] || ""}`, icon: TYPES[r.type]?.icon || "link", score: 2 });
    for (const t of allTemplates()) if (ok(norm([t.title, t.desc, (t.tags || []).join(" ")].join(" ")))) out.push({ kind: "tpl", id: t.id, title: t.title, sub: "תבנית", icon: "tpl", score: 3 });
    return out.sort((a, b) => a.score - b.score).slice(0, 14);
  }
  function showResults() {
    const q = el.q.value.trim();
    if (!q) { closeResults(); return; }
    const list = search(q);
    if (!results) { results = document.createElement("div"); results.className = "bd-pop"; results.id = "bd-results"; results.setAttribute("role", "listbox"); el.bd.appendChild(results);
      results.addEventListener("pointerdown", (e) => e.preventDefault());
      results.addEventListener("click", (e) => { const b = e.target.closest("[data-i]"); if (b) pickResult(Number(b.dataset.i)); }); }
    results._list = list; resIdx = 0;
    results.innerHTML = list.length ? list.map((x, i) => `<button class="bd-mi${i === resIdx ? " is-active" : ""}" type="button" role="option" data-i="${i}"><span class="lb-tile is-soft lb-cat-0">${I(x.icon)}</span><span><span dir="auto">${esc(x.title)}</span><small>${esc(x.sub)}</small></span></button>`).join("") : `<div class="bd-empty-note">לא נמצא כלום</div>`;
    const a = el.q.getBoundingClientRect(), r = el.bd.getBoundingClientRect();
    results.style.top = (a.bottom - r.top + 6) + "px"; results.style.left = clamp(a.right - r.left - Math.max(a.width, 320), 8, r.width - 330) + "px"; results.style.width = Math.max(a.width, 320) + "px";
    el.q.setAttribute("aria-expanded", "true");
  }
  function closeResults() { results?.remove(); results = null; el.q.setAttribute("aria-expanded", "false"); }
  function pickResult(i) {
    const x = results?._list?.[i]; if (!x) return;
    closeResults(); el.q.blur();
    if (x.kind === "card" || x.kind === "frame") focusCard(x.id);
    if (x.kind === "res") { const r = CAT.get(x.id); if (r?.tool || r?.url || r?.command || r?.view) launchResource(x.id); else { setDock(true); setDockTab("tools"); U.dockQ = r?.title || ""; renderDock(); } }
    if (x.kind === "tpl") instantiate(x.id);
  }
  el.q.addEventListener("input", showResults);
  el.q.addEventListener("focus", showResults);
  el.q.addEventListener("blur", () => setTimeout(closeResults, 150));
  el.q.addEventListener("keydown", (e) => {
    if (!results?._list?.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); resIdx = (resIdx + (e.key === "ArrowDown" ? 1 : -1) + results._list.length) % results._list.length; results.querySelectorAll(".bd-mi").forEach((b, i) => b.classList.toggle("is-active", i === resIdx)); }
    if (e.key === "Enter") { e.preventDefault(); pickResult(resIdx); }
  });
  window.addEventListener("keydown", (e) => { if (U.visible && !openDialogs && !isTyping(e.target) && (e.key === "/" || e.code === "Slash") && !e.shiftKey && !e.metaKey && !e.ctrlKey) { e.preventDefault(); e.stopImmediatePropagation(); el.q.focus(); } }, true);

  // ---------- dock ----------
  el.dock.addEventListener("click", (e) => {
    const t = e.target.closest("[data-tab]"); if (t) { if (el.dock.dataset.open !== "true") setDock(true); setDockTab(t.dataset.tab); return; }
    const b = e.target.closest("[data-k]"); if (!b) return;
    const k = b.dataset.k, ref = b.dataset.ref, id = b.dataset.id;
    if (k === "launch") launchResource(ref);
    if (k === "pin") togglePin(ref);
    if (k === "add") { const c = ref.startsWith("card:") ? null : addFromResource(ref); if (c) { if (U.mode === "canvas") focusCard(c.id); toast(`"${c.title}" נוסף ללוח`); } else if (ref.startsWith("card:")) focusCard(ref.slice(5)); }
    if (k === "up" || k === "down") { const i = B.dock.findIndex((d) => d.id === id), j = i + (k === "up" ? -1 : 1); if (i >= 0 && j >= 0 && j < B.dock.length) { [B.dock[i], B.dock[j]] = [B.dock[j], B.dock[i]]; commit("סדר במגירה"); renderAll(); } }
    if (k === "tpl-add") instantiate(id);
    if (k === "tpl-del") { delete B.templates[id]; commit("מחיקת תבנית"); renderAll(); toastUndo("התבנית נמחקה. פרויקטים שנוצרו ממנה לא השתנו"); }
    if (k === "tpl-from-sel") saveTemplateFromSelection();
    if (k === "go") focusCard(id);
    if (k === "fold") { prefs.open[id] = !prefs.open[id]; savePrefs(); renderDock(); }
    if (k === "home") goHome();
    if (k === "all") fitRect(allRect());
    if (k === "new-add") { const c = addFromResource(ref); if (c) toast(`"${c.title}" נוסף ללוח`); }
    if (k === "new-hide") { if (!B.dismissed.includes(ref)) B.dismissed.push(ref); commit("הסתרה"); renderAll(); }
    if (k === "new-hide-all") { for (const r of newResources()) B.dismissed.push(r.id); commit("הסתרת הכול"); renderAll(); }
  });
  el.dock.addEventListener("input", (e) => { if (e.target.id === "dock-q") { U.dockQ = e.target.value; renderDock(true); } if (e.target.id === "tpl-q") { U.tplQ = e.target.value; renderDock(true); } });
  let dragDock = null;
  el.dock.addEventListener("dragstart", (e) => {
    const it = e.target.closest("[draggable=true]"); if (!it) return;
    if (it.dataset.ref) e.dataTransfer.setData("application/x-lb-res", it.dataset.ref.startsWith("card:") ? "" : it.dataset.ref);
    if (it.dataset.tpl) e.dataTransfer.setData("application/x-lb-tpl", it.dataset.tpl);
    e.dataTransfer.setData("text/plain", it.dataset.title || "");
    e.dataTransfer.effectAllowed = "copyMove";
    dragDock = it.dataset.pin || null;
  });
  el.dock.addEventListener("dragover", (e) => { const it = e.target.closest("[data-pin]"); if (dragDock && it) { e.preventDefault(); el.dock.querySelectorAll(".is-drop").forEach((x) => x.classList.remove("is-drop")); it.classList.add("is-drop"); } });
  el.dock.addEventListener("drop", (e) => {
    const it = e.target.closest("[data-pin]"); if (!dragDock || !it) return;
    e.preventDefault();
    const i = B.dock.findIndex((d) => d.id === dragDock), j = B.dock.findIndex((d) => d.id === it.dataset.pin);
    if (i >= 0 && j >= 0 && i !== j) { const [x] = B.dock.splice(i, 1); B.dock.splice(j, 0, x); commit("סדר במגירה"); renderAll(); }
    dragDock = null;
  });
  el.dock.addEventListener("dragend", () => { dragDock = null; el.dock.querySelectorAll(".is-drop").forEach((x) => x.classList.remove("is-drop")); });
  function newResources() {
    const onBoard = new Set(Object.values(B.cards).map((c) => c.ref).filter(Boolean)), known = new Set(B.known), hid = new Set(B.dismissed);
    return [...CAT.values()].filter((r) => !known.has(r.id) && !onBoard.has(r.id) && !hid.has(r.id));
  }
  function resSub(r) {
    if (r.tool) { const st = toolState(r); return `מקומי · ${r.tool.url.replace(/^https?:\/\//, "").replace(/\/$/, "")}${st ? " · " + st.text : ""}`; }
    if (r.command) return r.command;
    if (r.url) return host(r.url);
    if (r.path) return r.path;
    if (r.view) return "תצוגה בלוח";
    if (r.metric) return "מדד מהרענון";
    return r.summary || "";
  }
  function dockRow(ref, pinId) {
    const card = ref.startsWith("card:") ? B.cards[ref.slice(5)] : null, r = card ? null : CAT.get(ref);
    if (!card && !r) return "";
    const title = card ? card.title || TYPES[card.type].untitled : r.title, type = card ? card.type : r.type, pinned = B.dock.some((d) => d.ref === ref), ro = readOnlyUI();
    return `<div class="bd-di" draggable="${ro ? "false" : "true"}" data-ref="${esc(ref)}" data-title="${esc(title)}"${pinId ? ` data-pin="${esc(pinId)}"` : ""}>
      <span class="lb-tile is-soft lb-cat-0">${I(TYPES[type]?.icon || "link")}</span>
      <span class="bd-dt"><b dir="auto">${esc(title)}</b><small dir="auto">${esc(card ? "כרטיס בלוח" : resSub(r))}</small></span>
      <button class="bd-ib" type="button" data-k="launch" data-ref="${esc(ref)}" aria-label="פתיחה: ${esc(title)}" title="${r?.command || r?.prompt ? "העתקה" : "פתיחה"}">${I(r?.command || r?.prompt ? "copy" : r?.tool ? "play" : "open")}</button>
      ${ro ? "" : `<button class="bd-ib" type="button" data-k="pin" data-ref="${esc(ref)}" aria-pressed="${pinned}" aria-label="${pinned ? "הסרה מהמוצמדים" : "הצמדה"}" title="${pinned ? "הסרה מהמוצמדים" : "הצמדה למעלה"}">${I(pinned ? "pinned" : "pin")}</button>`}
      ${pinId && !ro ? `<button class="bd-ib bd-hide-sm" type="button" data-k="up" data-id="${esc(pinId)}" aria-label="למעלה">${I("up")}</button><button class="bd-ib bd-hide-sm" type="button" data-k="down" data-id="${esc(pinId)}" aria-label="למטה">${I("down")}</button>` : ""}
      ${!pinId && !ro ? `<button class="bd-ib" type="button" data-k="add" data-ref="${esc(ref)}" aria-label="הוספה ללוח" title="הוספה ללוח (או גרירה)">${I("plus")}</button>` : ""}
    </div>`;
  }
  function renderDock(keepFocus) {
    if (!B) return;
    const tab = prefs.dockTab || "tools";
    el.dock.querySelectorAll("[data-tab]").forEach((t) => t.setAttribute("aria-selected", String(t.dataset.tab === tab)));
    const nn = newResources().length, nb = $("bd-newcount"); nb.hidden = !nn; nb.textContent = nn;
    if (el.dock.dataset.open !== "true") return;
    const focus = keepFocus ? document.activeElement?.id : null, caret = keepFocus ? document.activeElement?.selectionStart : null;
    let h = "";
    if (tab === "tools") {
      const q = norm(U.dockQ).trim();
      const m = (r) => !q || norm([r.title, r.summary, r.url, r.path, r.command].join(" ")).includes(q);
      h += `<div class="lb-search">${I("search")}<input class="lb-input" id="dock-q" type="search" value="${esc(U.dockQ)}" placeholder="חיפוש כלי, דף, תיקייה או קישור" aria-label="חיפוש במגירה"></div>`;
      const pins = B.dock.filter((d) => { const r = d.ref.startsWith("card:") ? B.cards[d.ref.slice(5)] : CAT.get(d.ref); return r && (!q || m(r.title ? r : { title: r.title })); });
      h += `<div class="bd-dh"><span>מוצמדים</span><span>${B.dock.length}</span></div>` + (pins.length ? pins.map((d) => dockRow(d.ref, d.id)).join("") : `<div class="bd-empty-note">${q ? "אין התאמה במוצמדים" : "מצמידים כאן כלים בלחיצה על הסיכה"}</div>`);
      const groups = {};
      for (const r of CAT.values()) if (m(r)) (groups[KIND_GROUP[r.kind] || "אחר"] ||= []).push(r);
      for (const g of [...GROUP_ORDER, "אחר"]) if (groups[g]?.length) h += `<div class="bd-dh"><span>${esc(g)}</span><span>${groups[g].length}</span></div>` + groups[g].slice(0, q ? 60 : g === "מדיה" ? 12 : 40).map((r) => dockRow(r.id)).join("");
      h += `<p class="lb-note">גוררים פריט ללוח כדי ליצור כרטיס. פקודות ופרומפטים מועתקים, לא רצים.</p>`;
    } else if (tab === "tpl") {
      const q = norm(U.tplQ).trim();
      const list = allTemplates().filter((t) => !q || norm([t.title, t.desc, (t.tags || []).join(" ")].join(" ")).includes(q));
      h += `<div class="lb-search">${I("search")}<input class="lb-input" id="tpl-q" type="search" value="${esc(U.tplQ)}" placeholder="חיפוש תבנית" aria-label="חיפוש תבנית"></div>`;
      if (!readOnlyUI()) h += `<button class="bd-btn" type="button" data-k="tpl-from-sel" ${U.sel.size ? "" : "disabled"} title="מסמנים כרטיסים או אזור בלוח ואז שומרים">${I("tpl")}תבנית מהבחירה</button>`;
      for (const [label, items] of [["תבניות מוכנות", list.filter((t) => t.builtin)], ["התבניות שלי", list.filter((t) => !t.builtin)]]) {
        h += `<div class="bd-dh"><span>${label}</span><span>${items.length}</span></div>`;
        h += items.length ? items.map((t) => `<div class="bd-di" draggable="${readOnlyUI() ? "false" : "true"}" data-tpl="${esc(t.id)}" data-title="${esc(t.title)}"><span class="lb-tile is-soft ${areaCat(t.area || t.frame?.area)}">${I("tpl")}</span>
          <span class="bd-dt"><b dir="auto">${esc(t.title)}</b><small dir="auto">${esc(t.desc || `${t.cards.length} כרטיסים`)}</small></span>
          ${readOnlyUI() ? "" : `<button class="bd-ib" type="button" data-k="tpl-add" data-id="${esc(t.id)}" aria-label="יצירה מהתבנית: ${esc(t.title)}" title="יצירת עותק בלוח (או גרירה)">${I("plus")}</button>${t.builtin ? "" : `<button class="bd-ib" type="button" data-k="tpl-del" data-id="${esc(t.id)}" aria-label="מחיקת התבנית" title="מחיקת התבנית">${I("trash")}</button>`}`}</div>`).join("")
          : `<div class="bd-empty-note">${label === "התבניות שלי" ? "מסמנים כרטיסים ושומרים כתבנית" : "אין התאמה"}</div>`;
      }
      h += `<p class="lb-note">כל שימוש בתבנית יוצר עותק חדש עם מזהים חדשים, בתוך אזור משלו.</p>`;
    } else if (tab === "nav") {
      h += `<div class="bd-acts"><button class="bd-btn" type="button" data-k="home">${I("home")}בית</button><button class="bd-btn" type="button" data-k="all">${I("fit")}כל הלוח</button></div>`;
      const frames = Object.values(B.frames).sort((a, b) => a.y - b.y || b.x - a.x);
      const loose = Object.values(B.cards).filter((c) => !frameOf(c));
      h += `<div class="bd-tree">`;
      for (const f of frames) {
        const kids = frameMembers(f).cards.sort((a, b) => a.y - b.y || b.x - a.x), open = !!prefs.open[f.id];
        h += `<div class="bd-tree-f ${areaCat(f.area)}"><button class="bd-ib" type="button" data-k="fold" data-id="${esc(f.id)}" aria-expanded="${open}" aria-label="${open ? "קיפול" : "פתיחה"}">${I("chev").replace("<svg", '<svg class="bd-chev"')}</button><button class="bd-mi" type="button" data-k="go" data-id="${esc(f.id)}"><span class="lb-tile ${areaCat(f.area)}">${I("frame")}</span><span dir="auto">${esc(f.title)}</span><span class="lb-nav-n">${kids.length}</span></button></div>`;
        if (open) h += `<div class="bd-tree-kids ${areaCat(f.area)}">${kids.map((c) => `<button class="bd-mi" type="button" data-k="go" data-id="${esc(c.id)}"><span dir="auto">${esc(c.title || sourceTitle(c) || TYPES[c.type].untitled)}</span></button>`).join("") || `<span class="bd-empty-note">ריק</span>`}</div>`;
      }
      if (loose.length) {
        const open = !!prefs.open.__loose;
        h += `<div class="bd-tree-f"><button class="bd-ib" type="button" data-k="fold" data-id="__loose" aria-expanded="${open}" aria-label="פתיחה">${I("chev").replace("<svg", '<svg class="bd-chev"')}</button><span class="bd-mi"><span>מחוץ לאזורים</span><span class="lb-nav-n">${loose.length}</span></span></div>`;
        if (open) h += `<div class="bd-tree-kids">${loose.map((c) => `<button class="bd-mi" type="button" data-k="go" data-id="${esc(c.id)}"><span dir="auto">${esc(c.title || sourceTitle(c) || TYPES[c.type].untitled)}</span></button>`).join("")}</div>`;
      }
      h += `</div>`;
    } else if (tab === "new") {
      const list = newResources();
      h += `<p class="lb-note">מקורות שנוספו לפרויקט מאז שהלוח נוצר (מהרענון האחרון${catAt ? " · " + esc(dmAt(catAt)) : ""}). שום דבר לא נכנס ללוח לבד.</p>`;
      h += list.length ? list.map((r) => `<div class="bd-di" draggable="${readOnlyUI() ? "false" : "true"}" data-ref="${esc(r.id)}" data-title="${esc(r.title)}"><span class="lb-tile is-soft lb-cat-0">${I(TYPES[r.type]?.icon || "link")}</span><span class="bd-dt"><b dir="auto">${esc(r.title)}</b><small dir="auto">${esc(resSub(r))}</small></span>${readOnlyUI() ? "" : `<button class="bd-ib" type="button" data-k="new-add" data-ref="${esc(r.id)}" aria-label="הוספה ללוח">${I("plus")}</button><button class="bd-ib" type="button" data-k="new-hide" data-ref="${esc(r.id)}" aria-label="הסתרה">${I("close")}</button>`}</div>`).join("")
        + (readOnlyUI() ? "" : `<button class="bd-btn" type="button" data-k="new-hide-all">הסתרת הכול</button>`) : `<div class="bd-empty-note">אין מקורות חדשים</div>`;
    }
    el.dockMain.innerHTML = h;
    if (focus) { const f = $(focus); if (f) { f.focus(); try { f.setSelectionRange(caret, caret); } catch {} } }
  }

  // ---------- list view ----------
  el.list.addEventListener("click", (e) => {
    const b = e.target.closest("[data-l]");
    if (b) { e.stopPropagation(); const c = B.cards[b.dataset.id]; if (b.dataset.l === "open" && c) openCard(c); if (b.dataset.l === "add") addCard(b.dataset.t || "note"); if (b.dataset.l === "canvas") { setMode("canvas"); focusCard(b.dataset.id); } return; }
    const row = e.target.closest(".bd-row"); if (row) { selectOnly(row.dataset.id); openPanel("card", row.dataset.id); renderAll(); }
  });
  el.list.addEventListener("keydown", (e) => { const row = e.target.closest(".bd-row"); if (row && (e.key === "Enter" || e.key === " ") && e.target === row) { e.preventDefault(); selectOnly(row.dataset.id); openPanel("card", row.dataset.id); renderAll(); } });
  function renderList() {
    const match = filterFn(), q = norm(el.q.value).trim();
    const toks = q.split(/\s+/).filter(Boolean);
    const pass = (c) => (!match || match(c)) && (!toks.length || toks.every((t) => hay(c).includes(t)));
    const frames = Object.values(B.frames).sort((a, b) => a.y - b.y || b.x - a.x);
    const groups = frames.map((f) => [f, frameMembers(f).cards.filter((c) => frameOf(c)?.id === f.id)]);
    groups.push([null, Object.values(B.cards).filter((c) => !frameOf(c))]);
    let total = 0, h = `<div class="bd-list-head"><h2>כל הכרטיסים</h2><div class="bd-acts">${readOnlyUI() ? "" : ADDABLE.slice(0, 3).map((t) => `<button class="bd-btn" type="button" data-l="add" data-t="${t}">${I("plus")}${TYPES[t].label}</button>`).join("")}</div></div>`;
    for (const [f, cards] of groups) {
      const list = cards.filter(pass).sort((a, b) => a.y - b.y || b.x - a.x);
      if (!list.length) continue;
      total += list.length;
      h += `<section class="bd-lg ${f ? areaCat(f.area) : "lb-cat-0"}"><h3><span class="lb-tile ${f ? areaCat(f.area) : "lb-cat-0"}">${I("frame")}</span><span dir="auto">${esc(f ? f.title : "מחוץ לאזורים")}</span><small>${list.length}</small></h3>`;
      for (const c of list) {
        const r = resOf(c), bits = [TYPES[c.type].label];
        if (c.type === "task" || c.type === "project") bits.push(STATUS[c.status || "todo"][0]);
        if (c.due) bits.push("עד " + dm(parseDay(c.due)));
        if (c.type === "metric") { const m = metricOf(c.metric || r?.metric); bits.push(m.dates ? (m.dates[0] ? `${m.dates[0].l} ${m.dates[0].d}` : "") : `${m.value}${m.unit ? " " + m.unit : ""}`); }
        if (r) bits.push("מקור");
        if (c.tags.length) bits.push(c.tags.slice(0, 2).join(", "));
        h += `<div class="bd-row${U.sel.has(c.id) ? " is-sel" : ""}" data-id="${esc(c.id)}" tabindex="0" role="button" aria-label="${esc((c.title || sourceTitle(c)) + ", " + TYPES[c.type].label)}">
          <span class="lb-tile is-soft lb-cat-0">${I(TYPES[c.type].icon)}</span><span class="bd-row-t"><b dir="auto">${esc(c.title || sourceTitle(c) || TYPES[c.type].untitled)}</b><small dir="auto">${esc(bits.filter(Boolean).join(" · "))}</small></span>
          ${openTarget(c) ? `<button class="bd-ib" type="button" data-l="open" data-id="${esc(c.id)}" aria-label="פתיחה" title="פתיחה">${I(openTarget(c).command ? "copy" : "open")}</button>` : ""}
          <button class="bd-ib bd-hide-sm" type="button" data-l="canvas" data-id="${esc(c.id)}" aria-label="הצגה בלוח" title="הצגה בלוח">${I("board")}</button></div>`;
      }
      h += `</section>`;
    }
    if (!total) h += `<div class="lb-empty">${q || match ? "אין כרטיסים שמתאימים לחיפוש או לסינון" : "הלוח ריק"}</div>`;
    el.list.innerHTML = h;
  }

  // ---------- side panel ----------
  function openPanel(kind, id, focus = true) { U.panel = { kind, id }; renderPanel(); el.panel.hidden = false; if (focus) el.panel.querySelector("[data-f='title'], [data-fr='title'], [data-fe='label']")?.focus({ preventScroll: true }); }
  function closePanel() { U.panel = null; el.panel.hidden = true; el.panel.innerHTML = ""; if (U.visible) el.stage.focus({ preventScroll: true }); }
  const field = (label, html, hint) => `<label class="lb-field">${label}${html}${hint ? `<span class="lb-note" style="font-weight:400">${hint}</span>` : ""}</label>`;
  function renderPanel() {
    if (!U.panel) { el.panel.hidden = true; return; }
    const { kind, id } = U.panel, ro = readOnlyUI(), dis = ro ? "disabled" : "";
    let h = "";
    if (kind === "card") {
      const c = B.cards[id]; if (!c) { closePanel(); return; }
      const r = resOf(c), T = TYPES[c.type];
      const types = ["note", "task", "project", "link", "doc", "media", "prompt", "workflow", "tool"];
      h += `<div class="bd-panel-head"><span class="lb-tile is-soft lb-cat-0">${I(T.icon)}</span><h2 dir="auto">${esc(c.title || sourceTitle(c) || T.untitled)}</h2><button class="bd-ib" type="button" data-p="close" aria-label="סגירה (Esc)">${I("close")}</button></div><div class="bd-panel-body">`;
      h += `<section class="bd-sec"><h3>בלוח<span class="lb-note">עריכה כאן משנה רק את הכרטיס${r ? ", לא את המקור" : ""}</span></h3>`;
      h += field("כותרת", `<input class="lb-input" data-f="title" dir="rtl" value="${esc(c.title)}" placeholder="${esc(sourceTitle(c) || T.untitled)}" ${dis}>`);
      if (!c.ref && !["metric", "view"].includes(c.type)) h += field("סוג", `<select class="lb-select" data-f="type" ${dis}>${types.map((t) => `<option value="${t}" ${t === c.type ? "selected" : ""}>${TYPES[t].label}</option>`).join("")}</select>`);
      h += field("תיאור", `<textarea class="lb-textarea" data-f="desc" dir="rtl" rows="4" placeholder="${esc(r?.summary ? "במקור: " + r.summary : "")}" ${dis}>${esc(c.desc)}</textarea>`);
      if (c.type === "task" || c.type === "project") h += `<div class="bd-2">${field("מצב", `<select class="lb-select" data-f="status" ${dis}>${Object.entries(STATUS).map(([k, [l]]) => `<option value="${k}" ${k === (c.status || "todo") ? "selected" : ""}>${l}</option>`).join("")}</select>`)}${field("עדיפות", `<select class="lb-select" data-f="priority" ${dis}><option value="">רגילה</option>${["low", "high"].map((k) => `<option value="${k}" ${k === c.priority ? "selected" : ""}>${PRIO[k]}</option>`).join("")}</select>`)}</div>` + field("תאריך יעד", `<input class="lb-input" type="date" data-f="due" value="${esc(c.due || "")}" ${dis}>`);
      if (["task", "workflow", "project"].includes(c.type)) {
        const list = c.checklist || [];
        h += `<div class="lb-field">${c.type === "workflow" ? "שלבים" : "צ׳קליסט"}<div class="bd-chk">${list.map((s, i) => `<div class="bd-chk-row"><label class="lb-check"><input type="checkbox" data-ck="toggle" data-i="${i}" ${s.done ? "checked" : ""} ${dis} aria-label="סימון"><span></span></label><input class="lb-input" data-ck="text" data-i="${i}" dir="rtl" value="${esc(s.text)}" ${dis} aria-label="שלב ${i + 1}">
          ${ro ? "" : `<button class="bd-ib" type="button" data-ck="up" data-i="${i}" aria-label="למעלה">${I("up")}</button><button class="bd-ib" type="button" data-ck="del" data-i="${i}" aria-label="מחיקה">${I("trash")}</button>`}</div>`).join("")}
          ${ro ? "" : `<div class="bd-chk-row"><input class="lb-input" data-ck="new" dir="rtl" placeholder="שלב חדש ו-Enter"><button class="bd-ib" type="button" data-ck="add" aria-label="הוספה">${I("plus")}</button></div>`}
          ${c.type === "workflow" && list.some((s) => s.done) && !ro ? `<button class="bd-btn" type="button" data-ck="reset">איפוס הסימונים</button>` : ""}</div></div>`;
      }
      if (!r && ["link", "doc", "tool"].includes(c.type)) h += field("קישור או נתיב בפרויקט", `<input class="lb-input lb-ltr" data-f="url" dir="ltr" value="${esc(c.url || "")}" placeholder="https://… או media/projects/…" ${dis}>`, `מותר: https, http, mailto או נתיב יחסי בתיקיית הפרויקט`) + `<span class="bd-err" id="url-err" hidden></span>`;
      if (r && ["link", "doc", "tool"].includes(c.type)) h += field("קישור משלי (לא חובה)", `<input class="lb-input lb-ltr" data-f="url" dir="ltr" value="${esc(c.url || "")}" placeholder="${esc(r.url || r.path || "")}" ${dis}>`, "אם ממלאים, הכרטיס נפתח בקישור הזה במקום במקור") + `<span class="bd-err" id="url-err" hidden></span>`;
      if (c.type === "media") {
        const m = mediaOf(c);
        h += field("קובץ: קישור או נתיב בפרויקט", `<input class="lb-input lb-ltr" data-f="media" dir="ltr" value="${esc(c.media?.src || c.media?.url || "")}" placeholder="${esc(r?.media?.src || "https://drive.google.com/… או media/projects/…")}" ${dis}>`, c.media?.asset ? "הקובץ שמור במאגר הקבצים של הלוח ב-claude.ai" : "") + `<span class="bd-err" id="media-err" hidden></span>`;
        if (!ro) h += `<div class="bd-acts"><button class="bd-btn" type="button" data-p="upload">${I("upload")}העלאת קובץ</button>${m?.files?.length ? `<button class="bd-btn" type="button" data-p="preview">${I("eye")}תצוגה מקדימה</button>` : ""}</div>`;
      }
      if (c.type === "prompt") h += field("הפרומפט", `<textarea class="lb-textarea" data-f="prompt" dir="rtl" rows="5" ${dis}>${esc(c.prompt || r?.prompt || "")}</textarea>`) + `<div class="bd-acts"><button class="bd-btn is-primary" type="button" data-p="copy-prompt">${I("copy")}העתקת הפרומפט</button></div>`;
      if (c.type === "metric") {
        h += field("מדד", `<select class="lb-select" data-f="metric" ${dis}>${[...CAT.values()].filter((x) => x.metric).map((x) => `<option value="${esc(x.metric)}" ${x.metric === (c.metric || r?.metric) ? "selected" : ""}>${esc(x.title)}</option>`).join("")}${Object.entries(COUNTERS).map(([k, [l]]) => `<option value="counter_${k}" ${("counter_" + k) === c.metric ? "selected" : ""}>מונה: ${esc(l)}</option>`).join("")}</select>`);
        h += field("יעד שלי", `<input class="lb-input" data-f="target" dir="rtl" value="${esc(c.target || "")}" placeholder="למשל 3,000 עד דצמבר" ${dis}>`, "נשמר בכרטיס בלבד. המספר עצמו מגיע מהרענון ולא נערך כאן");
      }
      if (c.type === "view") h += field("תצוגה בלוח", `<select class="lb-select" data-f="view" ${dis}>${Object.entries(VIEW_NAMES).map(([k, l]) => `<option value="${k}" ${k === (c.view || r?.view) ? "selected" : ""}>${l}</option>`).join("")}</select>`);
      if (c.type === "note") h += `<div class="lb-field">צבע<div class="lb-segmented" role="group">${Object.entries(COLORS).map(([k, l]) => `<button type="button" data-p="color" data-v="${k}" aria-pressed="${(c.color || "plain") === k}" ${dis}>${l}</button>`).join("")}</div></div>`;
      h += field("תגיות", `<input class="lb-input" data-f="tags" dir="rtl" value="${esc(c.tags.join(", "))}" placeholder="מופרדות בפסיק" ${dis}>`);
      const projects = Object.values(B.cards).filter((p) => p.type === "project" && p.id !== c.id);
      if (c.type !== "project") h += field("פרויקט", `<select class="lb-select" data-f="project" ${dis}><option value="">ללא</option>${projects.map((p) => `<option value="${esc(p.id)}" ${p.id === c.project ? "selected" : ""}>${esc(p.title || "ללא שם")}</option>`).join("")}</select>`);
      const fr = frameOf(c);
      h += field("אזור", `<select class="lb-select" data-f="frame" ${dis}><option value="">מחוץ לאזורים</option>${Object.values(B.frames).map((f) => `<option value="${esc(f.id)}" ${fr?.id === f.id ? "selected" : ""}>${esc(f.title)}</option>`).join("")}</select>`, "בחירת אזור מעבירה את הכרטיס לתחתית האזור");
      h += `</section>`;
      if (r) h += sourceSection(c, r);
      h += connectionsSection(c);
      h += `<section class="bd-sec"><h3>פעולות</h3><div class="bd-acts">
        ${openTarget(c) ? `<button class="bd-btn is-primary" type="button" data-p="open">${I(openTarget(c).command ? "copy" : "open")}${openTarget(c).command ? "העתקת הפקודה" : openTarget(c).view ? "מעבר לתצוגה" : "פתיחה"}</button>` : ""}
        ${canPreview(c) ? `<button class="bd-btn" type="button" data-p="preview">${I("eye")}תצוגה מקדימה</button>` : ""}
        ${linkOf(c) ? `<button class="bd-btn" type="button" data-p="copy-link">${I("copy")}העתקת קישור</button>` : ""}
        ${ro ? "" : `<button class="bd-btn" type="button" data-p="duplicate">${I("dup")}שכפול</button><button class="bd-btn" type="button" data-p="pin">${I(isPinned(c) ? "pinned" : "pin")}${isPinned(c) ? "הסרה מהמגירה" : "הצמדה למגירה"}</button><button class="bd-btn" type="button" data-p="save-tpl">${I("tpl")}שמירה כתבנית</button><button class="bd-btn" type="button" data-p="show-conn">${I("connect")}הצגת החיבורים</button><button class="bd-btn is-danger" type="button" data-p="delete">${I("trash")}${r ? "הסרה מהלוח" : "מחיקה"}</button>`}
      </div></section>`;
      h += `<section class="bd-sec"><dl class="bd-kv"><dt>מזהה</dt><dd class="lb-ltr">${esc(c.id)}</dd>${c.ref ? `<dt>מקור</dt><dd class="lb-ltr">${esc(c.ref)}</dd>` : ""}${c.createdAt ? `<dt>נוצר</dt><dd>${esc(dmAt(c.createdAt))}</dd>` : ""}${c.updatedAt ? `<dt>נערך</dt><dd>${esc(dmAt(c.updatedAt))}</dd>` : ""}</dl></section>`;
      h += `</div>`;
    } else if (kind === "frame") {
      const f = B.frames[id]; if (!f) { closePanel(); return; }
      const kids = frameMembers(f).cards;
      h += `<div class="bd-panel-head"><span class="lb-tile ${areaCat(f.area)}">${I("frame")}</span><h2 dir="auto">${esc(f.title)}</h2><button class="bd-ib" type="button" data-p="close" aria-label="סגירה (Esc)">${I("close")}</button></div><div class="bd-panel-body">
        <section class="bd-sec"><h3>אזור</h3>${field("שם", `<input class="lb-input" data-fr="title" dir="rtl" value="${esc(f.title)}" ${dis}>`)}
        ${field("צבע האזור", `<select class="lb-select" data-fr="area" ${dis}><option value="">ללא</option>${Object.entries(AREAS).map(([k, a]) => `<option value="${k}" ${k === f.area ? "selected" : ""}>${esc(a.label)}</option>`).join("")}</select>`, "הצבעים לפי shared/design/categories.json")}</section>
        <section class="bd-sec"><h3>בתוך האזור<span>${kids.length}</span></h3><div class="bd-picker">${kids.map((c) => `<button class="bd-mi" type="button" data-p="go" data-id="${esc(c.id)}"><span class="lb-tile is-soft lb-cat-0">${I(TYPES[c.type].icon)}</span><span dir="auto">${esc(c.title || sourceTitle(c) || TYPES[c.type].untitled)}</span></button>`).join("") || `<span class="bd-empty-note">ריק</span>`}</div></section>
        <section class="bd-sec"><h3>פעולות</h3><div class="bd-acts"><button class="bd-btn" type="button" data-p="fit-frame">${I("fit")}התאמה לאזור</button>${ro ? "" : `<button class="bd-btn" type="button" data-p="home-frame">${I("home")}האזור הזה כבית</button><button class="bd-btn" type="button" data-p="tpl-frame">${I("tpl")}שמירה כתבנית</button><button class="bd-btn" type="button" data-p="dup-frame">${I("dup")}שכפול</button><button class="bd-btn is-danger" type="button" data-p="del-frame">${I("trash")}מחיקת האזור בלבד</button><button class="bd-btn is-danger" type="button" data-p="del-frame-all">${I("trash")}מחיקה עם הכרטיסים</button>`}</div></section></div>`;
    } else if (kind === "edge") {
      const e = B.edges[id]; if (!e) { closePanel(); return; }
      const a = B.cards[e.from], b = B.cards[e.to];
      h += `<div class="bd-panel-head"><span class="lb-tile is-soft lb-cat-0">${I("connect")}</span><h2>חיבור</h2><button class="bd-ib" type="button" data-p="close" aria-label="סגירה (Esc)">${I("close")}</button></div><div class="bd-panel-body">
        <section class="bd-sec"><h3>${e.kind === "dep" ? "תלות מהרישום" : "חיבור שלי"}</h3>
        ${e.kind === "dep" ? `<p class="lb-note">נוצר מ-lumebook.json: הרכיב הראשון מזין את השני. אפשר לערוך או להסיר מהלוח; הרישום עצמו לא משתנה.</p>` : ""}
        ${field("תווית", `<input class="lb-input" data-fe="label" dir="rtl" value="${esc(e.label)}" placeholder="למשל: לפי, מזין, תוצר" ${dis}>`)}
        <div class="bd-picker"><button class="bd-mi" type="button" data-p="go" data-id="${esc(a.id)}"><span>מ:</span><span dir="auto">${esc(a.title || sourceTitle(a))}</span></button><button class="bd-mi" type="button" data-p="go" data-id="${esc(b.id)}"><span>אל:</span><span dir="auto">${esc(b.title || sourceTitle(b))}</span></button></div>
        ${ro ? "" : `<div class="bd-acts"><button class="bd-btn" type="button" data-p="swap">${I("swap")}היפוך כיוון</button><button class="bd-btn is-danger" type="button" data-p="del-edge">${I("trash")}מחיקה</button></div>`}</section></div>`;
    }
    el.panel.innerHTML = h;
    el.panel.hidden = false;
  }
  function linkOf(c) { const t = openTarget(c); return t?.url || (t?.path ? (fileUrl(t.path) ? new URL(fileUrl(t.path), location.href).href : t.path) : null); }
  function sourceSection(c, r) {
    const links = (r.links || (r.url ? [{ label: "קישור", url: r.url }] : [])).filter((l) => safeHref(l.url));
    const feeds = (r.feeds || []).map((id) => CAT.get(id)).filter(Boolean);
    const fedBy = [...CAT.values()].filter((x) => (x.feeds || []).includes(r.id));
    const onBoard = (rid) => Object.values(B.cards).find((x) => x.ref === rid);
    const ts = toolState(r);
    let h = `<section class="bd-sec is-src"><h3>מהמקור<span class="lb-note">לקריאה בלבד</span></h3>`;
    if (r.title !== c.title) h += `<div class="lb-small"><b>שם במקור:</b> <span dir="auto">${esc(r.title)}</span></div>`;
    if (r.summary) h += `<p class="lb-small lb-muted" dir="auto">${esc(r.summary)}</p>`;
    h += `<dl class="bd-kv">`;
    if (r.date) h += `<dt>פורסם</dt><dd>${esc(dm(parseDay(r.date)))}</dd>`;
    if (r.modified) h += `<dt>המקור נערך</dt><dd>${esc(ago(r.modified))}</dd>`;
    if (r.component) h += `<dt>רכיב</dt><dd class="lb-ltr">${esc(r.component)}</dd>`;
    if (behind(r)) h += `<dt>פרסום</dt><dd><span class="lb-chip warning">המקור השתנה מאז הפרסום</span></dd>`;
    if (r.status) h += `<dt>מצב בתיקייה</dt><dd>${esc({ active: "פעיל", done: "הסתיים", superseded: "הוחלף", cloud: "בענן", unlisted: "לא באינדקס של media/README.md" }[r.status] || r.status)}</dd>`;
    if (r.local_only) h += `<dt>איפה</dt><dd>במחשב בלבד${ENV.projectServer ? " · השרת המקומי פעיל" : ""}</dd>`;
    if (r.private) h += `<dt>שימו לב</dt><dd>מספרים פנימיים, לא לשתף</dd>`;
    h += `</dl>`;
    for (const l of links) h += `<div class="bd-code"><span class="lb-xs lb-dim">${esc(l.label)}</span><code title="${esc(l.url)}">${esc(host(l.url))}</code><a class="bd-ib" href="${esc(l.url)}" target="_blank" rel="noopener" aria-label="פתיחה">${I("open")}</a><button class="bd-ib" type="button" data-p="copy" data-v="${esc(l.url)}" aria-label="העתקה">${I("copy")}</button></div>`;
    if (r.path) h += `<div class="bd-code"><code title="${esc(r.path)}">${esc(r.path)}</code>${fileUrl(r.path) ? `<a class="bd-ib" href="${esc(fileUrl(r.path))}" target="_blank" rel="noopener" aria-label="פתיחה בשרת המקומי">${I("open")}</a>` : ""}<button class="bd-ib" type="button" data-p="copy" data-v="${esc(r.path)}" aria-label="העתקת הנתיב">${I("copy")}</button></div>`;
    if (r.command) h += `<div class="bd-code"><code>${esc(r.command)}</code><button class="bd-ib" type="button" data-p="copy" data-v="${esc(r.command)}" aria-label="העתקת הפקודה">${I("copy")}</button></div><p class="lb-note">הדף לא מריץ פקודות. מעתיקים ומריצים במסוף, מתיקיית הפרויקט.</p>`;
    if (r.tool) {
      h += `<div class="lb-row"><span class="lb-chip ${ts?.cls || ""}">${esc(ts?.text || "לא נבדק")}</span><button class="bd-btn" type="button" data-p="check-tool">בדיקה עכשיו</button></div>`;
      if (r.tool.runs_as_he || r.tool.runs_as) h += `<p class="lb-note" dir="auto">${esc(r.tool.runs_as_he || r.tool.runs_as)}</p>`;
      for (const [label, cmd] of [["בדיקה", r.tool.status_cmd], ["הפעלה מחדש", r.tool.start_cmd]]) if (cmd) h += `<div class="lb-note">${label}:</div><div class="bd-code"><code>${esc(cmd)}</code><button class="bd-ib" type="button" data-p="copy" data-v="${esc(cmd)}" aria-label="העתקה">${I("copy")}</button></div>`;
      h += `<p class="lb-note">${ENV.projectServer ? "הבדיקה רצה דרך שרת הפרויקט." : "מהדף הזה הדפדפן לא תמיד מאפשר לבדוק כתובת במחשב, אז \"לא זמין מכאן\" לא אומר בהכרח שהכלי כבוי."}</p>`;
    }
    if (feeds.length || fedBy.length) {
      for (const [label, list] of [["ניזון מ", fedBy], ["מזין את", feeds]]) if (list.length) h += `<div class="lb-field">${label} (lumebook.json)<div class="bd-picker">${list.map((x) => { const on = onBoard(x.id); return `<button class="bd-mi" type="button" data-p="${on ? "go" : "add-res"}" data-id="${esc(on ? on.id : x.id)}"><span dir="auto">${esc(x.title)}</span><small>${on ? "בלוח" : "הוספה ללוח"}</small></button>`; }).join("")}</div></div>`;
    }
    return h + `</section>`;
  }
  function connectionsSection(c) {
    const out = Object.values(B.edges).filter((e) => e.from === c.id), inn = Object.values(B.edges).filter((e) => e.to === c.id), ro = readOnlyUI();
    const row = (e, other, dir) => `<div class="bd-conn-row"><span>${dir === "out" ? "אל" : "מ"}: <button class="bd-mi" style="display:inline;padding:0;width:auto" type="button" data-p="go" data-id="${esc(other.id)}"><span dir="auto">${esc(other.title || sourceTitle(other) || TYPES[other.type].untitled)}</span></button>${e.kind === "dep" ? ' <span class="lb-chip outline">רישום</span>' : ""}</span>
      <input class="lb-input" data-fe2="${esc(e.id)}" dir="rtl" value="${esc(e.label)}" placeholder="תווית" ${ro ? "disabled" : ""} aria-label="תווית">${ro ? "" : `<button class="bd-ib" type="button" data-p="del-edge2" data-id="${esc(e.id)}" aria-label="מחיקת החיבור">${I("trash")}</button>`}</div>`;
    let h = `<section class="bd-sec"><h3>חיבורים<span>${out.length + inn.length}</span></h3>`;
    h += [...inn.map((e) => row(e, B.cards[e.from], "in")), ...out.map((e) => row(e, B.cards[e.to], "out"))].join("") || `<span class="bd-empty-note">אין עדיין חיבורים</span>`;
    if (!ro) h += `<div class="lb-field">חיבור לכרטיס<input class="lb-input" id="conn-q" dir="rtl" placeholder="חיפוש כרטיס לחיבור" autocomplete="off"></div><div class="bd-picker" id="conn-list"></div>`;
    return h + `</section>`;
  }
  // panel edits: every change goes through commit() with a merge key, so typing makes one undo step
  el.panel.addEventListener("input", (e) => {
    const t = e.target;
    if (t.id === "conn-q") { connPicker(t.value); return; }
    if (readOnlyUI()) return;
    const P2 = U.panel; if (!P2) return;
    if (P2.kind === "card") {
      const c = B.cards[P2.id]; if (!c) return;
      const f = t.dataset.f;
      if (f === "title") { c.title = t.value.slice(0, 300); el.panel.querySelector(".bd-panel-head h2").textContent = c.title || sourceTitle(c) || TYPES[c.type].untitled; }
      else if (f === "desc") c.desc = t.value.slice(0, 8000);
      else if (f === "prompt") c.prompt = t.value.slice(0, 8000);
      else if (f === "target") c.target = t.value.slice(0, 60);
      else if (f === "tags") c.tags = t.value.split(/[,،]/).map((x) => x.trim().slice(0, 40)).filter(Boolean).slice(0, 12);
      else if (f === "url") { const v = t.value.trim(), ok = !v || safeHref(v) || safePath(v), err = $("url-err"); if (err) { err.hidden = !!ok; err.textContent = ok ? "" : "הקישור לא נשמר: מותר רק https, http, mailto או נתיב בתיקיית הפרויקט"; } if (!ok) return; if (v) c.url = safeHref(v) || safePath(v); else delete c.url; }
      else if (f === "media") { const v = t.value.trim(), ok = !v || safeHref(v) || safePath(v), err = $("media-err"); if (err) { err.hidden = !!ok; err.textContent = ok ? "" : "לא נשמר: מותר רק קישור https או נתיב בתיקיית הפרויקט"; } if (!ok) return; if (v) c.media = cleanMedia({ src: v, kind: extKind(v) || undefined }); else delete c.media; }
      else if (t.dataset.ck === "text") { const s = c.checklist?.[Number(t.dataset.i)]; if (s) s.text = t.value.slice(0, 300); }
      else if (t.dataset.fe2) { const ed = B.edges[t.dataset.fe2]; if (ed) ed.label = t.value.slice(0, 80); commit("תווית חיבור", "lab:" + ed?.id); renderAll(); return; }
      else return;
      c.updatedAt = nowIso();
      commit("עריכה", `${f || t.dataset.ck}:${c.id}`); renderAll();
    } else if (P2.kind === "frame") {
      const fr = B.frames[P2.id]; if (!fr || t.dataset.fr !== "title") return;
      fr.title = t.value.slice(0, 120) || "אזור"; commit("שם אזור", "ftitle:" + fr.id); renderAll();
    } else if (P2.kind === "edge") {
      const ed = B.edges[P2.id]; if (!ed || t.dataset.fe !== "label") return;
      ed.label = t.value.slice(0, 80); commit("תווית חיבור", "lab:" + ed.id); renderAll();
    }
  });
  el.panel.addEventListener("change", (e) => {
    const t = e.target, P2 = U.panel; if (!P2 || readOnlyUI()) return;
    if (P2.kind === "card") {
      const c = B.cards[P2.id]; if (!c) return;
      const f = t.dataset.f;
      if (f === "type") { c.type = t.value; if ((c.type === "task" || c.type === "project") && !c.status) c.status = "todo"; }
      else if (f === "status") c.status = t.value;
      else if (f === "priority") { if (t.value) c.priority = t.value; else delete c.priority; }
      else if (f === "due") { if (t.value) c.due = t.value; else delete c.due; }
      else if (f === "project") { if (t.value) c.project = t.value; else delete c.project; }
      else if (f === "metric") c.metric = t.value;
      else if (f === "view") c.view = t.value;
      else if (f === "frame") { const fr = B.frames[t.value]; if (fr) placeInFrame(c, fr); else { const cur = frameOf(c); if (cur) { c.x = cur.x + cur.w + 60; } } }
      else if (t.dataset.ck === "toggle") { const s = c.checklist?.[Number(t.dataset.i)]; if (s) s.done = t.checked; }
      else return;
      c.updatedAt = nowIso();
      commit("עריכה"); renderAll({ panel: f === "type" || f === "frame" });
    } else if (P2.kind === "frame" && t.dataset.fr === "area") {
      const fr = B.frames[P2.id]; if (!fr) return; if (t.value) fr.area = t.value; else delete fr.area; commit("צבע אזור"); renderAll({ panel: true });
    }
  });
  el.panel.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { e.stopPropagation(); closePanel(); return; }
    if (e.target.dataset?.ck === "new" && e.key === "Enter") { e.preventDefault(); addCheck(e.target.value); }
  });
  function addCheck(text) {
    const c = B.cards[U.panel?.id]; if (!c || !text.trim()) return;
    (c.checklist ||= []).push({ id: uid("k"), text: text.trim().slice(0, 300), done: false });
    commit("שלב חדש"); renderAll({ panel: true }); el.panel.querySelector("[data-ck='new']")?.focus();
  }
  el.panel.addEventListener("click", (e) => {
    const b = e.target.closest("[data-p], [data-ck]"); if (!b) return;
    const P2 = U.panel; if (!P2) return;
    const c = B.cards[P2.id], a = b.dataset.p, ck = b.dataset.ck;
    if (ck && c && !readOnlyUI()) {
      const i = Number(b.dataset.i), list = c.checklist || [];
      if (ck === "add") { addCheck(el.panel.querySelector("[data-ck='new']")?.value || ""); return; }
      if (ck === "del") { list.splice(i, 1); commit("מחיקת שלב"); renderAll({ panel: true }); return; }
      if (ck === "up" && i > 0) { [list[i - 1], list[i]] = [list[i], list[i - 1]]; commit("סדר שלבים"); renderAll({ panel: true }); return; }
      if (ck === "reset") { list.forEach((s) => (s.done = false)); commit("איפוס שלבים"); renderAll({ panel: true }); return; }
      return;
    }
    switch (a) {
      case "close": closePanel(); renderAll(); break;
      case "open": if (c) openCard(c); break;
      case "preview": if (c) previewCard(c); break;
      case "copy-link": if (c) copyText(linkOf(c), "הקישור"); break;
      case "copy-prompt": if (c) copyText(c.prompt || resOf(c)?.prompt || "", "הפרומפט"); break;
      case "copy": copyText(b.dataset.v, "הטקסט"); break;
      case "duplicate": duplicateSelection(); break;
      case "pin": if (c) togglePin(c.ref || "card:" + c.id); renderPanel(); break;
      case "save-tpl": saveTemplateFromSelection(); break;
      case "show-conn": if (c) { const ids = [c.id, ...Object.values(B.edges).flatMap((ed) => (ed.from === c.id ? [ed.to] : ed.to === c.id ? [ed.from] : []))]; if (U.mode === "list") setMode("canvas"); fitRect(bbox(ids.map((x) => B.cards[x]).filter(Boolean)), 1); selectOnly(c.id); renderAll(); } break;
      case "delete": deleteSelection(); break;
      case "upload": pickFiles(P2.id); break;
      case "color": if (c && !readOnlyUI()) { if (b.dataset.v === "plain") delete c.color; else c.color = b.dataset.v; commit("צבע"); renderAll({ panel: true }); } break;
      case "check-tool": { const r = resOf(c); if (r) checkTool(r).then(() => renderPanel()); break; }
      case "go": focusCard(b.dataset.id); break;
      case "add-res": { const nc = addFromResource(b.dataset.id); if (nc) toast(`"${nc.title}" נוסף ללוח`); break; }
      case "connect-to": if (c) { connect(c.id, b.dataset.id); openPanel("card", c.id); } break;
      case "del-edge2": { delete B.edges[b.dataset.id]; commit("מחיקת חיבור"); renderAll({ panel: true }); break; }
      case "fit-frame": fitRect(B.frames[P2.id], 1); break;
      case "home-frame": { const f = B.frames[P2.id]; if (f) { B.home = { x: f.x - 40, y: f.y - 40, w: f.w + 80, h: f.h + 80 }; commit("תצוגת בית"); toast("האזור הזה הוא עכשיו תצוגת הבית"); } break; }
      case "tpl-frame": selectOnly(P2.id); saveTemplateFromSelection(); break;
      case "dup-frame": selectOnly(P2.id); duplicateSelection(); break;
      case "del-frame": selectOnly(P2.id); deleteSelection(); break;
      case "del-frame-all": { const f = B.frames[P2.id]; if (f) { setSelection([f.id, ...frameMembers(f).cards.map((x) => x.id)]); deleteSelection(); } break; }
      case "swap": { const ed = B.edges[P2.id]; if (ed) { [ed.from, ed.to] = [ed.to, ed.from]; commit("היפוך כיוון"); renderAll({ panel: true }); } break; }
      case "del-edge": U.sel.clear(); U.selEdge = P2.id; deleteSelection(); break;
    }
  });
  function connPicker(q) {
    const box = $("conn-list"), c = B.cards[U.panel?.id]; if (!box || !c) return;
    const toks = norm(q).split(/\s+/).filter(Boolean);
    if (!toks.length) { box.innerHTML = ""; return; }
    const list = Object.values(B.cards).filter((x) => x.id !== c.id && toks.every((t) => hay(x).includes(t))).slice(0, 8);
    box.innerHTML = list.map((x) => `<button class="bd-mi" type="button" data-p="connect-to" data-id="${esc(x.id)}"><span class="lb-tile is-soft lb-cat-0">${I(TYPES[x.type].icon)}</span><span dir="auto">${esc(x.title || sourceTitle(x) || TYPES[x.type].untitled)}</span><small>${esc(frameOf(x)?.title || "")}</small></button>`).join("") || `<span class="bd-empty-note">לא נמצא</span>`;
  }

  // ---------- export, import, backups, reset, home ----------
  function exportJson() { return JSON.stringify({ format: "lumebook-board", schema: SCHEMA, exportedAt: nowIso(), source: store?.kind === "db" ? "artifact" : ENV.isStatic ? "static" : "page", board: cleanBoard(B).board }, null, 1); }
  async function exportBoard() {
    const json = exportJson(), name = `lumebook-board-${new Date().toISOString().slice(0, 10)}.json`;
    if (ENV.downloads) { try { await ENV.downloads.save({ filename: name, data: json }); toast("הקובץ נשמר"); return; } catch (e) { if (e?.code === "declined" || e?.code === "cancelled") return; } }
    try {
      const u = URL.createObjectURL(new Blob([json], { type: "application/json" }));
      const a = document.createElement("a"); a.href = u; a.download = name; document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(u), 4000);
      dialog({ title: "ייצוא הלוח", body: `<p>הקובץ <bdi class="lb-ltr">${esc(name)}</bdi> הורד (${Math.round(bytes(json) / 1024)} KB). אם הדפדפן לא הוריד אותו, אפשר להעתיק את התוכן.</p>`, foot: `<button class="bd-btn" type="button" data-d="copy">העתקת ה-JSON</button><button class="bd-btn is-primary" type="button" data-d="cancel">סגירה</button>`, onAction(a) { if (a === "copy") copyText(json, "ה-JSON"); return a === "cancel"; } });
    } catch { copyText(json, "ה-JSON"); }
  }
  function importBoard() {
    if (readOnlyUI()) { toast("הלוח במצב קריאה בלבד"); return; }
    let parsed = null;
    const summary = (d) => {
      const box = d.querySelector("#imp-sum"), okBtns = d.querySelectorAll("[data-d='replace'], [data-d='merge']");
      okBtns.forEach((b) => (b.disabled = !parsed));
      if (!parsed) return;
      const b = parsed.board;
      box.innerHTML = `<div class="lb-callout info"><b>נמצא לוח תקין</b><span>${Object.keys(b.cards).length} כרטיסים · ${Object.keys(b.edges).length} חיבורים · ${Object.keys(b.frames).length} אזורים · ${Object.keys(b.templates).length} תבניות${parsed.dropped ? ` · ${parsed.dropped} פריטים לא תקינים יושמטו` : ""}${parsed.tooNew ? " · נשמר בגרסה חדשה יותר של הלוח, ייתכן שחלק מהפרטים לא ייקראו" : ""}</span></div>`;
    };
    const read = (text, d) => {
      parsed = null;
      const box = d.querySelector("#imp-sum");
      try {
        const j = JSON.parse(text);
        const raw = j && j.format === "lumebook-board" ? j.board : j && j.cards ? j : null;
        if (!raw) throw new Error("זה לא קובץ לוח של לומבוק");
        parsed = migrate({ ...raw, schema: j.schema || raw.schema || 1 });
        if (!Object.keys(parsed.board.cards).length && !Object.keys(parsed.board.frames).length) { parsed = null; throw new Error("אין בקובץ כרטיסים"); }
      } catch (e) { box.innerHTML = `<span class="bd-err">${esc(e.message || "הקובץ לא נקרא")}</span>`; }
      summary(d);
    };
    dialog({
      title: "ייבוא לוח",
      body: `<label class="lb-field">קובץ JSON שיוצא מהלוח<input type="file" accept="application/json,.json" id="imp-file"></label><label class="lb-field">או הדבקה של התוכן<textarea class="lb-textarea" id="imp-text" rows="4" dir="ltr" placeholder="{&quot;format&quot;:&quot;lumebook-board&quot;, …}"></textarea></label><div id="imp-sum"></div>
        <p class="lb-note">לפני החלפה נשמר גיבוי של הלוח הנוכחי בדפדפן הזה, ואפשר גם לבטל עם Cmd+Z. "להוסיף" מכניס עותק עם מזהים חדשים לצד הלוח הקיים.</p>`,
      foot: `<button class="bd-btn is-primary" type="button" data-d="merge" disabled>להוסיף לצד הלוח</button><button class="bd-btn" type="button" data-d="replace" disabled>להחליף את הלוח</button><button class="bd-btn" type="button" data-d="cancel">ביטול</button>`,
      onOpen(d) {
        d.querySelector("#imp-file").addEventListener("change", (e) => { const f = e.target.files[0]; if (!f) return; if (f.size > 20e6) { d.querySelector("#imp-sum").innerHTML = `<span class="bd-err">הקובץ גדול מדי</span>`; return; } f.text().then((t) => read(t, d)); });
        d.querySelector("#imp-text").addEventListener("input", (e) => read(e.target.value, d));
      },
      onAction(a) {
        if (a === "cancel") return true;
        if (!parsed) return false;
        const nb = parsed.board;
        if (a === "replace") {
          backupNow("לפני ייבוא");
          const keep = { dock: nb.dock.length ? nb.dock : B.dock, known: [...new Set([...B.known, ...nb.known])] };
          B.cards = nb.cards; B.edges = nb.edges; B.frames = nb.frames; B.templates = { ...B.templates, ...nb.templates }; B.home = nb.home || B.home; B.dock = keep.dock; B.known = keep.known; B.dismissed = nb.dismissed;
          U.sel.clear(); U.selEdge = null; closePanel(); commit("ייבוא (החלפה)"); renderAll(); fitRect(allRect()); toastUndo("הלוח הוחלף מהקובץ");
        } else {
          const cur = allRect(), inc = bbox([...Object.values(nb.cards), ...Object.values(nb.frames)]);
          const dx = cur && inc ? cur.x - 200 - (inc.x + inc.w) : 0, dy = cur && inc ? cur.y - inc.y : 0;
          const out = cloneItems(Object.values(nb.cards), Object.values(nb.frames), dx, dy, Object.values(nb.edges));
          out.cards.forEach((c) => (B.cards[c.id] = c)); out.frames.forEach((f) => (B.frames[f.id] = f)); out.edges.forEach((e) => (B.edges[e.id] = e));
          for (const t of Object.values(nb.templates)) { const id = uid("t"); B.templates[id] = { ...t, id }; }
          commit("ייבוא (הוספה)"); setSelection(out.frames.map((f) => f.id)); renderAll(); fitRect(bbox([...out.cards, ...out.frames])); toastUndo(`נוספו ${out.cards.length} כרטיסים מהקובץ`);
        }
        return true;
      },
    });
  }
  function showBackups() {
    const list = backups();
    dialog({ title: "גיבויים בדפדפן הזה", body: `<p class="lb-note">עד 6 גרסאות אחרונות של הלוח נשמרות כאן אוטומטית (כל 10 דקות של עבודה, ולפני ייבוא או איפוס). הן לא עוברות למכשיר אחר.</p>
      ${list.length ? `<div class="lb-group">${list.map((b, i) => `<div class="lb-group-row"><span>${esc(dmAt(b.at))}${b.reason ? " · " + esc(b.reason) : ""} · ${b.cards} כרטיסים</span><span class="lb-meta"><button class="bd-btn" type="button" data-d="r${i}">שחזור</button></span></div>`).join("")}</div>` : `<div class="lb-empty">עוד אין גיבויים</div>`}`,
      foot: `<button class="bd-btn" type="button" data-d="now">גיבוי עכשיו</button><button class="bd-btn" type="button" data-d="cancel">סגירה</button>`,
      onAction(a) {
        if (a === "now") { toast(backupNow("ידני") ? "נשמר גיבוי" : "הגיבוי נכשל: אין מקום בדפדפן"); return true; }
        if (a[0] === "r" && !readOnlyUI()) {
          const b = list[Number(a.slice(1))]; if (!b) return true;
          try { const m = migrate(JSON.parse(b.json)); backupNow("לפני שחזור"); Object.assign(B, { cards: m.board.cards, edges: m.board.edges, frames: m.board.frames, templates: m.board.templates, home: m.board.home, dock: m.board.dock, known: m.board.known, dismissed: m.board.dismissed }); U.sel.clear(); commit("שחזור גיבוי"); renderAll({ panel: true }); toastUndo("הגיבוי שוחזר"); } catch { toast("הגיבוי לא נקרא"); }
          return true;
        }
        return a === "cancel";
      } });
  }
  function resetBoard() {
    if (readOnlyUI()) return;
    dialog({ title: "איפוס ללוח ההתחלתי", body: `<p>הלוח יחזור למבנה ההתחלתי, עם המקורות הנוכחיים של הפרויקט. כל הכרטיסים, החיבורים והאזורים שיצרת יוסרו מהלוח.</p><p class="lb-note">לפני האיפוס נשמר גיבוי בדפדפן הזה, ואפשר לבטל עם Cmd+Z. התבניות שלך נשארות.</p>`,
      foot: `<button class="bd-btn is-danger" type="button" data-d="ok">איפוס</button><button class="bd-btn" type="button" data-d="cancel">ביטול</button>`,
      onAction(a) {
        if (a !== "ok") return true;
        backupNow("לפני איפוס");
        const s = boardFromSeed();
        Object.assign(B, { cards: s.cards, edges: s.edges, frames: s.frames, home: s.home, dock: s.dock, known: [...new Set([...s.known, ...CAT.keys()])], dismissed: [] });
        U.sel.clear(); closePanel(); commit("איפוס"); renderAll(); goHome(); toastUndo("הלוח אופס");
        return true;
      } });
  }
  function setHome() { if (readOnlyUI()) return; const s = stageRect(), a = toWorld(s.left, s.top), b = toWorld(s.right, s.bottom); B.home = { x: a.x, y: a.y, w: b.x - a.x, h: b.y - a.y }; commit("תצוגת בית"); toast("התצוגה הזאת היא עכשיו תצוגת הבית (Shift+H)"); }
  function saveInfo() {
    const db = store?.kind === "db";
    const where = db ? `<p><b>בלוח ב-claude.ai.</b> השינויים נשמרים במסד הנתונים של הארטיפקט, ונראים בכל מכשיר שבו פותחים את הלוח ב-Claude. הרענון של כל בוקר לא נוגע בהם.</p><p class="lb-note">העותק לקריאה ב-Vercel לא רואה את הלוח הזה, ויש לו שמירה נפרדת בדפדפן.</p>`
      : `<p><b>במכשיר הזה בלבד.</b> השינויים נשמרים בדפדפן הזה (localStorage), ולא עוברים ללוח ב-Claude, למכשיר אחר או לדפדפן אחר. ניקוי נתוני האתר מוחק אותם.</p><p class="lb-note">כדי להעביר או לגבות: ייצוא לקובץ JSON וייבוא במקום האחר.${ENV.projectServer ? " בשרת המקומי אפשר גם לראות קבצי מדיה מהפרויקט ולהעלות קבצים ל-media/inbox." : ""}</p>`;
    dialog({ title: "איפה השינויים נשמרים", body: `${where}<dl class="bd-kv"><dt>מצב</dt><dd>${esc(el.save.textContent)}</dd>${SAVE.error ? `<dt>שגיאה</dt><dd class="bd-err">${esc(SAVE.error)}</dd>` : ""}<dt>גרסה</dt><dd>${B?.rev || 0}${B?.savedAt ? " · " + esc(dmAt(B.savedAt)) : ""}</dd><dt>כרטיסים</dt><dd>${Object.keys(B?.cards || {}).length}</dd><dt>נתוני הפרויקט</dt><dd>${D.snap?.generated_at ? "רענון " + esc(dmAt(D.snap.generated_at)) : "אין"}</dd></dl>`,
      foot: `${dirty && !readOnly ? `<button class="bd-btn is-primary" type="button" data-d="save">לשמור עכשיו</button>` : ""}<button class="bd-btn" type="button" data-d="export">ייצוא</button><button class="bd-btn" type="button" data-d="cancel">סגירה</button>`,
      onAction(a) { if (a === "save") flush(); if (a === "export") exportBoard(); return true; } });
  }
  function showKeys() {
    const sec = (t, rows) => `<section><h3>${t}</h3>${rows.map(([k, d]) => `<div><span>${d}</span><kbd dir="${/[\u0590-\u05FF]/.test(k) ? "rtl" : "ltr"}">${k}</kbd></div>`).join("")}</section>`;
    dialog({ title: "קיצורי מקלדת", wide: true, body: `<div class="bd-keys">
      ${sec("תנועה", [["גלגלת / שתי אצבעות", "הזזת הלוח"], ["Cmd + גלגלת / צביטה", "זום"], ["רווח + גרירה", "הזזת הלוח"], ["H / V", "יד / בחירה"], ["+ / −", "זום"], ["Cmd+0", "זום 100%"], ["Shift+1", "כל הלוח"], ["Shift+2", "התאמה לבחירה"], ["Shift+H", "תצוגת בית"], ["/ או Cmd+K", "חיפוש"]])}
      ${sec("יצירה", [["N", "פתק"], ["T", "משימה"], ["L", "קישור"], ["F", "אזור (סביב הבחירה)"], ["C", "חיבור מהכרטיס המסומן"], ["לחיצה כפולה על הרקע", "פתק במקום"], ["גרירה מהעיגול", "חיבור, או פתק מחובר"], ["הדבקה", "קישור, טקסט או קבצים"]])}
      ${sec("עריכה", [["לחיצה כפולה", "עריכת כותרת"], ["F2", "עריכת כותרת"], ["Enter", "פרטים בחלונית"], ["חיצים (Shift)", "הזזה"], ["Cmd+D", "שכפול"], ["Cmd+C / Cmd+V", "העתקה והדבקה"], ["Delete", "מחיקה"], ["Cmd+Z / Shift+Cmd+Z", "ביטול / חזרה"], ["Shift+לחיצה", "בחירה מרובה"], ["G", "הצמדה לרשת"]])}
      ${sec("כרטיס מסומן", [["O", "פתיחת המקור"], ["P", "תצוגה מקדימה"], ["Esc", "ביטול בחירה / סגירה"], ["Tab", "מעבר בין כרטיסים"], ["Cmd+S", "שמירה עכשיו"], ["?", "החלון הזה"]])}
    </div><p class="lb-note">גרירה של כרטיס מזיזה אותו. כפתורים בכרטיס רק לוחצים. עריכת טקסט: לחיצה כפולה או Enter. ב-Windows, Ctrl במקום Cmd.</p>`, foot: `<button class="bd-btn is-primary" type="button" data-d="cancel">סגירה</button>` });
  }

  // ---------- show / hide with the dashboard router ----------
  const ro = new ResizeObserver(() => { if (U.visible && U.mode === "canvas") renderCtx(); });
  ro.observe(el.stage);
  function onRoute(view) {
    const vis = view === "board";
    U.visible = vis;
    if (vis && B) requestAnimationFrame(() => { if (!U.viewSet) initView(); applyView(); renderAll(); });
  }
  document.addEventListener("lb:route", (e) => onRoute(e.detail?.view));
  function initView() {
    const s = stageRect(); if (!s.width) return;
    U.viewSet = true;
    if (prefs.view && Number.isFinite(prefs.view.z)) { U.view = { tx: prefs.view.tx, ty: prefs.view.ty, z: clamp(prefs.view.z, 0.08, 2.5) }; applyView(); }
    else goHome();
  }

  // ---------- boot ----------
  async function boot() {
    const mode = prefs.mode || (small() ? "list" : "canvas");
    el.dock.dataset.open = String(prefs.dockOpen ?? !small());
    setMode(mode, false);
    onDash();
    renderSave();
    if (/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname)) {
      fetch("/api/board/env", { cache: "no-store" }).then((r) => (r.ok ? r.json() : null)).then((j) => {
        if (j?.server !== "lumebook") return;
        ENV.projectServer = j; live++; renderSoon();
        // on the project server the check is definitive and cheap, so local tools show their state from the start
        for (const r of CAT.values()) if (r.tool) checkTool(r);
      }).catch(() => {});
    }
    let db = null, user = null;
    if (window.claude?.use) {
      [db, user] = await Promise.all([window.claude.use("db").catch(() => null), window.claude.use("user").catch(() => null)]);
      window.claude.use("assets").then((a) => { ENV.assets = a || null; }).catch(() => {});
      window.claude.use("downloads").then((d) => { ENV.downloads = d || null; }).catch(() => {});
    }
    if (db) {
      store = new DbStore(db);
      try { const w = await user?.can?.("data.write"); if (w === false) { readOnly = true; ENV.bannerMsg = "אין לך הרשאת עריכה בלוח הזה. אפשר לעיין, והשינויים לא נשמרים."; } } catch {}
    } else {
      store = new LocalStore(ENV.isStatic ? "static" : "page");
      try { LS.set(KEY + ":probe", "1"); LS.del(KEY + ":probe"); } catch { readOnly = true; ENV.bannerMsg = "הדפדפן חוסם שמירה מקומית (למשל בחלון פרטי), אז השינויים לא יישמרו. אפשר לייצא לקובץ."; ENV.bannerErr = true; }
    }
    let res;
    try { res = await store.load(); } catch (e) { res = { error: e?.code || e?.message || "load" }; }
    if (res.error) {
      const bk = backups()[0];
      let raw = null; try { raw = bk ? JSON.parse(bk.json) : null; } catch {}
      B = raw ? migrate(raw).board : boardFromSeed();
      readOnly = true;
      ENV.bannerMsg = `הלוח השמור לא נקרא (${res.error}). מוצג ${raw ? "הגיבוי האחרון מהדפדפן הזה" : "הלוח ההתחלתי"}, בלי לשמור מעליו. אפשר לייצא, ולנסות שוב ברענון הדף.`; ENV.bannerErr = true;
    } else if (!res.board) {
      B = boardFromSeed();
      if (!readOnly) dirty = true;
    } else {
      const m = migrate(res.board);
      if (m.migrated) { try { LS.set(`${KEY}:premigration:${m.from}`, JSON.stringify(res.board)); } catch {} }
      // after a fallback to the previous version, the next save must supersede the broken head, not conflict with it
      B = m.board; B.rev = res.recovered ? Number(res.head?.rev) || Number(res.board.rev) || 0 : Number(res.board.rev) || 0;
      if (m.tooNew) { readOnly = true; ENV.bannerMsg = "הלוח נשמר בגרסה חדשה יותר של הדף. רעננו את הדף כדי לערוך אותו."; }
      if (m.dropped) ENV.bannerMsg = `${m.dropped} פריטים בלוח השמור לא היו תקינים והושמטו.`;
      if (res.recovered) ENV.bannerMsg = "השמירה האחרונה לא הושלמה, אז נטענה הגרסה שלפניה.";
      if (m.migrated) dirty = true;
    }
    zTop = Math.max(1, ...Object.values(B.cards).map((c) => c.z || 0));
    H.base = entityMap();
    SAVE.state = readOnly ? "ro" : dirty ? "pending" : B.savedAt ? "idle" : "saved";
    renderSave(); renderBanner();
    U.visible = !document.getElementById("v-board")?.hidden;
    renderAll();
    if (U.visible) requestAnimationFrame(() => { initView(); renderAll(); });
    if (dirty && !readOnly) flush();
    store.watch?.(onRemote);
    if (store.kind === "db" && !readOnly) setTimeout(() => store.sweep().catch(() => {}), 4000);
    // a small handle for checks from the console: read state, save now, focus a card, export as text
    window.LBBoard = { get state() { return B; }, flush, focus: focusCard, mode: () => store?.kind, readOnly: () => readOnly, exportJson, saveState: () => ({ ...SAVE, dirty }) };
  }
  boot();
})();
