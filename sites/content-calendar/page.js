/* לוח תוכן, the content calendar (11 Nov 2026). Reads GET /api/calendar?month= (tools/content_calendar.py) and writes through the
   existing endpoints: Carousel Machine's /api/save, /api/save-test, /api/grade, /api/production/* (forwarded by the project server),
   the reels hub's /api/reels-hub/doc + /api/calendar/reel-merge, and the calendar's own /api/calendar/doc, /move, /jobs, /gpt,
   /trials. Nothing spends money or touches Postiz without Yarin's click in that moment. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var ICON = window.CC_ICONS || {}, CAT = window.CC_CAT || {};
  var HDR = { "Content-Type": "application/json", "X-LumeBook-Board": "1" };
  var DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"], DOW = ["א׳", "ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ש׳"];
  var MONTHS = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"];
  var KIND = { kid: { he: "קרוסלת ילד", icon: "slides" }, test: { he: "קרוסלת ניסוי", icon: "flask" }, reel: { he: "ריל", icon: "clapper" },
    idea: { he: "רעיון", icon: "sparkle" }, post: { he: "פוסט מפוסטיז", icon: "send" }, story: { he: "סטוריז", icon: "stack" }, season: { he: "קרוסלת חג", icon: "gift" }, remind: { he: "תזכורת", icon: "bell" }, shoot: { he: "צילום", icon: "film" } };
  var ST_ICON = { idea: "sparkle", draft: "pencil", grade: "bars", pick: "check-circle", hook: "target", film: "film", produce: "play",
    making: "sync", approve: "wallet", ready: "check-circle", scheduled: "clock", posted: "check" };
  var NEED_HE = { grade: "לדרג", pick: "לבחור", hook: "לבחור הוק", film: "לצלם", approve: "לאשר", produce: "להפיק", remind: "לשתף לראשי ולפייסבוק" };
  var TEST_ICON = { say: "chat", how: "compass", gift: "gift", age: "trend", reveal: "eye" };
  var TEST_FIELDS = ["big", "headline", "body", "label", "no", "yes", "why", "quote", "by"];
  var FIELD_HE = { big: "הטקסט הגדול", headline: "כותרת", body: "גוף", label: "תווית", no: "במקום", yes: "תגידו", why: "למה", quote: "ציטוט",
    by: "מאת", tag: "תגית", highlight: "הדגשה", caption: "כיתוב", cta: "קריאה לפעולה", fb_text: "טקסט לפייסבוק", comment_word: "מילת תגובה",
    title: "שם פנימי", hook: "הוק", payoff: "התמורה", shot: "מה מצלמים", vo: "שורת קריינות", sees: "מה רואים" };
  var LS = "cc-cal-v1";
  var MON_SHORT = ["ינו׳", "פבר׳", "מרץ", "אפר׳", "מאי", "יוני", "יולי", "אוג׳", "ספט׳", "אוק׳", "נוב׳", "דצמ׳"];

  var S = { data: null, byId: {}, byDate: {}, month: null, view: "month", sel: null, q: "",
    kinds: { kid: true, test: true, reel: true, idea: true, post: true, story: true, season: true }, tests: { say: true, how: true, gift: true, age: true, reveal: true },
    drafts: false, sts: {}, open: null, cache: {}, all: [], sideOff: false, jobs: [], tasks: [], reelJobs: [], answers: {}, sort: "date", sortDir: 1, failed: false };

  /* ---------- small helpers ---------- */
  function esc(t) { return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function ic(name, cls) { var s = ICON[name] || ICON.info || ""; return cls ? s.replace("<svg", '<svg class="' + cls + '"') : s; }
  function iso(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
  function parse(s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +(p[2] || 1)); }
  function addDays(s, n) { var d = parse(s); d.setDate(d.getDate() + n); return iso(d); }
  function ddmm(s) { var p = s.split("-"); return "\u2066" + p[2] + " / " + p[1] + "\u2069"; }   /* isolated left to right, or RTL text reverses it */
  function full(s) { var p = s.split("-"); return "\u2066" + p[2] + " / " + p[1] + " / " + p[0] + "\u2069"; }
  function dayName(s) { return "יום " + DAYS[parse(s).getDay()]; }
  function monthHe(m) { var p = m.split("-"); return MONTHS[+p[1] - 1] + " " + p[0]; }
  function today() { return (S.data && S.data.today) || iso(new Date()); }
  function catOf(p) { return CAT[p.kind] || "lb-cat-0"; }
  function family(p) { return p.kind === "reel" || (p.kind === "idea" && p.subtype === "reel") ? "reel" : (p.kind === "kid" || p.kind === "test" || p.kind === "season" || p.kind === "idea") ? "carousel" : null; }
  /* a block that waits for Yarin carries a bell, with what it waits for as its tooltip (Yarin, 11 Nov 2026, replacing the banner on top) */
  function bellHtml(p) {
    var n = (p.needs || []).map(function (k) { return NEED_HE[k] || k; });
    return n.length ? '<span class="cc-bellbox" role="img" title="' + esc("צריך אותי: " + n.join(" · ")) + '" aria-label="' + esc("צריך אותי: " + n.join(" · ")) + '">' + ic("bell") + "</span>" : "";
  }
  function stChip(p) { return p.status ? '<span class="cc-st s-' + p.status + '">' + ic(ST_ICON[p.status] || "info") + esc(p.status_he) + "</span>" : ""; }
  function chans(p) { return (p.channels || []).map(function (c) { return '<span class="cc-s" title="' + (c === "ig" ? "אינסטגרם" : "פייסבוק") + '">' + ic(c === "ig" ? "instagram" : "facebook") + "</span>"; }).join(""); }
  function kindIcon(p) { return '<span class="cc-ico">' + ic(p.kind === "test" && TEST_ICON[p.subtype] ? TEST_ICON[p.subtype] : (KIND[p.kind] || {}).icon) + "</span>"; }
  function kindLabel(p) { return (KIND[p.kind] || {}).he + (p.subtype_he && p.kind !== "reel" ? " · " + p.subtype_he : p.kind === "reel" ? " · " + (p.detail && p.detail.option === 2 ? "ב" : "א") : ""); }
  function store(k, v) { try { var o = JSON.parse(localStorage.getItem(LS) || "{}"); o[k] = v; localStorage.setItem(LS, JSON.stringify(o)); } catch (x) {} }
  function stored(k, d) { try { var o = JSON.parse(localStorage.getItem(LS) || "{}"); return o[k] === undefined ? d : o[k]; } catch (x) { return d; } }
  function api(path, opt) {
    return fetch(path, Object.assign({ cache: "no-store" }, opt || {})).then(function (r) {
      return r.text().then(function (t) {
        var b = {}; try { b = t ? JSON.parse(t) : {}; } catch (x) { b = { error: t.slice(0, 200) }; }
        if (!r.ok) { var e = new Error(b.he || b.error || ("HTTP " + r.status)); e.body = b; e.status = r.status; throw e; }
        return b;
      });
    });
  }
  function post(path, body) { return api(path, { method: "POST", headers: HDR, body: JSON.stringify(body) }); }
  function put(path, body) { return api(path, { method: "PUT", headers: HDR, body: JSON.stringify(body) }); }
  function nowIso() { return new Date().toISOString(); }

  var toastT;
  function toast(text, btn, fn) {
    var t = $("#ccToast");
    t.innerHTML = '<span>' + esc(text) + "</span>" + (btn ? ' <button class="lb-btn ghost sm" type="button">' + esc(btn) + "</button>" : "");
    t.hidden = false;
    if (btn) $("button", t).onclick = function () { t.hidden = true; fn(); };
    clearTimeout(toastT); toastT = setTimeout(function () { t.hidden = true; }, btn ? 8000 : 4000);
  }

  /* ---------- data ---------- */
  function adjMonth(m, n) { var d = parse(m + "-01"); d.setMonth(d.getMonth() + n); return iso(d).slice(0, 7); }
  function fetchMonth(m, force) {
    var c = S.cache[m], q = "/api/calendar?month=" + m + (S.drafts ? "&drafts=1" : "") + (c && !force ? "&rev=" + c.rev : "");
    return api(q).then(function (b) { if (b.same) return false; S.cache[m] = b; return true; });
  }
  /* the shown month plus the one before and after: the month's hint days and a week or day across the month line need them */
  function load(force) {
    var m = S.month, side = [adjMonth(m, -1), adjMonth(m, 1)];
    /* one after another: the server builds a month around one shared Postiz list, so two months at once mix their posts */
    var ch = [];
    function side1(x) { return function () { return fetchMonth(x, force).catch(function () { return false; }).then(function (c) { ch.push(c); }); }; }
    return fetchMonth(m, force).then(function (c) { ch.push(c); }).then(side1(side[0])).then(side1(side[1])).then(function () {
      S.failed = false;
      if (S.month !== m) return;
      if (S.data && !ch.some(Boolean)) return;
      S.data = S.cache[m]; index(); render();
    }).catch(function (e) {
      S.failed = true;
      if (!S.data) $("#ccView").innerHTML = '<div class="lb-empty"><p>הלוח לא נטען: ' + esc(e.message) + '</p><button class="lb-btn" type="button" id="ccRetry">לנסות שוב</button></div>';
      var r = $("#ccRetry"); if (r) r.onclick = function () { load(true); };
    });
  }
  function setMonth(m) { if (m === S.month) return; S.month = m; S.data = S.cache[m] || null; if (S.data) index(); load(); }
  function index() {
    S.byId = {}; S.byDate = {}; S.all = [];
    [adjMonth(S.month, -1), S.month, adjMonth(S.month, 1)].forEach(function (m) {
      ((S.cache[m] || {}).pieces || []).forEach(function (p) { if (S.byId[p.id]) return; S.byId[p.id] = p; S.all.push(p); (S.byDate[p.date] = S.byDate[p.date] || []).push(p); });
    });
    Object.keys(S.byDate).forEach(function (d) {
      var seen = {};
      S.byDate[d].forEach(function (p) {
        p._clash = false;
        if (!p.time || ["kid", "test", "reel", "post"].indexOf(p.kind) < 0) return;
        (p.channels || []).forEach(function (c) { var k = p.time + c; (seen[k] = seen[k] || []).push(p); });
      });
      Object.keys(seen).forEach(function (k) { if (seen[k].length > 1) seen[k].forEach(function (p) { p._clash = true; }); });
    });
  }
  function visible(p) {
    var side = p.kind === "shoot" || p.kind === "remind";
    if (side && S.kinds.reel === false) return false;
    if (!side && S.kinds[p.kind] === false) return false;
    if (p.kind === "test" && S.tests[p.subtype] === false) return false;
    var any = Object.keys(S.sts).some(function (k) { return S.sts[k]; });
    if (any && !side && !S.sts[p.status]) return false;
    if (any && side) return false;
    if (S.q) {
      var d = p.detail || {}, tx = d.texts || {};
      var hay = [p.title, p.subtype_he, p.id, d.reel, d.note, (d.for || []).join(" "), tx.caption, tx.hook, (tx.vo || []).join(" "),
        d.set ? d.set.frames.map(function (f) { return f.layers.map(function (l) { return l.text || l.label || ""; }).join(" "); }).join(" ") : ""].concat((d.items || []).map(function (i) { return [i.title, i.caption, i.cta].join(" "); })).join(" ").toLowerCase();
      if (hay.indexOf(S.q.toLowerCase()) < 0) return false;
    }
    return true;
  }
  function dayPieces(d) { return (S.byDate[d] || []).filter(visible).sort(function (a, b) { return (a.time || "99").localeCompare(b.time || "99") || a.kind.localeCompare(b.kind); }); }
  function missing(d) {
    var t = (S.data && S.data.targets) || { carousel: 2, reel: 2 }, have = { carousel: 0, reel: 0 };
    if (d < today()) return { carousel: 0, reel: 0 };
    (S.byDate[d] || []).forEach(function (p) { var f = family(p); if (f) have[f]++; });
    return { carousel: Math.max(0, (t.carousel || 0) - have.carousel), reel: Math.max(0, (t.reel || 0) - have.reel) };
  }
  function slotsOf(ds) {   /* the day's empty planned slots, each with the hour the weekly plan gives it */
    var ms = missing(ds), out = [];
    [["carousel", "חסרה קרוסלה"], ["reel", "חסר ריל"]].forEach(function (f) {
      var times = missingTimes(ds, f[0]);
      for (var k = 0; k < ms[f[0]]; k++) out.push({ family: f[0], he: f[1], time: times[k] || "" });
    });
    return out;
  }
  function gapLabel(s) { return s.he + (s.time ? " · " + s.time : ""); }
  /* an empty slot is an outlined red row between the posts around its hour, saying what is missing (Yarin, 11 Nov 2026) */
  function gapHtml(s) {
    return '<span class="cc-it cc-gap" data-family="' + s.family + '" data-time="' + (s.time || "") + '" role="img" aria-label="' + esc(gapLabel(s)) + '" title="' + esc(gapLabel(s)) + '">' +
      (s.time ? '<span class="t">' + s.time + "</span>" : "") + '<span class="x">' + esc(s.he) + "</span></span>";
  }
  function keyDate(d) { return ((window.CC_DATES || {})[d]) || ""; }

  /* ---------- render ---------- */
  function render() { renderTop(); renderSide(); renderView(); if (S.open && calm() && !(window.CCStory && CCStory.busy()) && !(window.CCSeason && CCSeason.busy())) renderDrawer(); }

  function renderTop() {
    $("#ccMonth").textContent = viewTitle();
    var nm = { month: ["החודש הקודם", "החודש הבא"], week: ["השבוע הקודם", "השבוע הבא"], day: ["היום הקודם", "היום הבא"] }[S.view];
    $("#ccPrev").setAttribute("aria-label", nm[0]); $("#ccNext").setAttribute("aria-label", nm[1]);
    $("#ccPrev").title = nm[0]; $("#ccNext").title = nm[1];
    $$("#ccViews button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.v === S.view)); });
    var n = $("#ccNotice"), notes = (S.data && S.data.notices) || [];
    n.hidden = !notes.length; n.innerHTML = ic("info") + "<span>" + esc(notes.join(" ")) + "</span>";
  }

  function renderSide() {
    if (!S.data) return;
    var t = today(), end = addDays(t, 6), rows = [];
    S.all.forEach(function (p) {
      (p.needs || []).forEach(function (n) { if (p.date >= addDays(t, -2) && p.date <= end) rows.push({ p: p, n: n }); });
    });
    rows.sort(function (a, b) { return a.p.date.localeCompare(b.p.date) || (a.p.time || "99").localeCompare(b.p.time || "99"); });
    $("#ccQn").textContent = rows.length || "";
    var cap = S.qAll ? rows.length : 6;
    $("#ccQ").innerHTML = rows.length ? rows.slice(0, cap).map(function (r) {
      return '<button type="button" class="' + catOf(r.p) + '" data-open="' + esc(r.p.id) + '">' + kindIcon(r.p) +
        '<span class="w"><b>' + esc(NEED_HE[r.n] || r.n) + '</b><small translate="no">' + esc(r.p.title || "") + "</small></span>" +
        '<span class="d">' + (r.p.date === t ? "היום" : ddmm(r.p.date)) + "</span></button>";
    }).join("") + (rows.length > 6 ? '<button type="button" class="lb-btn ghost sm cc-qmore" data-act="qall">' + (S.qAll ? "פחות" : "הצגת כל " + rows.length) + "</button>" : "") : '<p class="cc-q-empty">אין כלום שמחכה לך השבוע.</p>';
    var mn = $("#ccMenuN"); if (mn) mn.textContent = rows.length ? String(rows.length) : "";
    var qp = $("#ccQPhone");
    if (qp) qp.innerHTML = '<h2>' + ic("bell") + "צריך אותי השבוע <span class=\"lb-count\">" + (rows.length || "") + "</span></h2>" + '<div class="cc-q">' +
      (rows.length ? rows.slice(0, 4).map(function (r) {
        return '<button type="button" class="' + catOf(r.p) + '" data-open="' + esc(r.p.id) + '">' + kindIcon(r.p) + '<span class="w"><b>' + esc(NEED_HE[r.n] || r.n) + '</b><small translate="no">' + esc(r.p.title || "") + '</small></span><span class="d">' + (r.p.date === t ? "היום" : ddmm(r.p.date)) + "</span></button>";
      }).join("") : '<p class="cc-q-empty">אין כלום שמחכה לך השבוע.</p>') + "</div>" + (rows.length > 4 ? '<button type="button" class="lb-btn ghost sm more" id="ccQMore">עוד ' + (rows.length - 4) + "</button>" : "");
    var qm = $("#ccQMore"); if (qm) qm.onclick = function () { $("#ccMenu").click(); };
    // mini month
    var first = parse(S.month + "-01"), days = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate(), h = DOW.map(function (x) { return "<span>" + x + "</span>"; }).join("");
    for (var i = 0; i < first.getDay(); i++) h += "<span></span>";
    for (var d = 1; d <= days; d++) {
      var ds = S.month + "-" + String(d).padStart(2, "0"), need = (S.byDate[ds] || []).some(function (p) { return (p.needs || []).length; });
      h += '<button type="button" data-day="' + ds + '" class="' + (ds === t ? "is-today " : "") + (ds === S.sel ? "is-sel " : "") + (need ? "has-need" : "") + '" aria-label="' + full(ds) + '">' + d + "</button>";
    }
    $("#ccMini").innerHTML = h; $("#ccMiniT").textContent = monthHe(S.month);
    // type filters with counts
    var cnt = {}, tc = {}, sc = {};
    (S.data.pieces || []).forEach(function (p) {
      cnt[p.kind] = (cnt[p.kind] || 0) + 1;
      if (p.kind === "test") tc[p.subtype] = (tc[p.subtype] || 0) + 1;
      if (p.status) sc[p.status] = (sc[p.status] || 0) + 1;
    });
    $("#ccTypes").innerHTML = ["kid", "test", "season", "reel", "story", "idea", "post"].filter(function (k) { return cnt[k] || k !== "post" && k !== "idea" && k !== "story" && k !== "season" && k !== "test"; }).map(function (k) {
      var row = '<button type="button" class="' + (CAT[k] || "") + '" data-kind="' + k + '" aria-pressed="' + (S.kinds[k] !== false) + '"><span class="ck"></span><span class="cc-ico">' + ic(KIND[k].icon) + "</span>" + esc(KIND[k].he) + '<span class="n">' + (cnt[k] || 0) + "</span></button>";
      if (k === "test" && cnt.test) row += '<div class="sub">' + ["say", "how", "gift", "age", "reveal"].map(function (s) {
        var lbl = { say: "תגידו את זה", how: "ככה זה עובד", gift: "מתנה לחנוכה", age: "מה קורה בגיל", reveal: "הרגע שרואים" }[s];
        return '<button type="button" class="' + CAT.test + '" data-test="' + s + '" aria-pressed="' + (S.tests[s] !== false) + '"><span class="ck"></span><span class="cc-ico">' + ic(TEST_ICON[s]) + "</span>" + lbl + '<span class="n">' + (tc[s] || 0) + "</span></button>";
      }).join("") + "</div>";
      return row;
    }).join("");
    var hd = S.data.hidden_drafts || 0;
    $("#ccDrafts").innerHTML = (hd || S.drafts) ? '<button type="button" data-drafts="1" aria-pressed="' + S.drafts + '"><span class="ck"></span><span class="cc-ico">' + ic("pencil") + "</span>טיוטות של חבילות שלא תוכננו" + (hd ? '<span class="n">' + hd + "</span>" : "") + "</button>" : "";
    $("#ccLegend").innerHTML = legend();
    $("#ccSts").innerHTML = (S.data.statuses || []).filter(function (s) { return sc[s.code]; }).map(function (s) {
      return '<button type="button" class="cc-st s-' + s.code + '" data-st="' + s.code + '" aria-pressed="' + !!S.sts[s.code] + '">' + ic(ST_ICON[s.code]) + esc(s.he) + " " + sc[s.code] + "</button>";
    }).join("");
  }

  function itemHtml(p, cell) {
    var title = p.kind === "shoot" ? "צילום" : p.title || "";
    var ab = (p.options || []).length > 1 && !p.picked ? '<span class="ab">' + (p.kind === "test" ? "א·ב" : (p.options || []).map(function (o) { return o.label; }).join("·")) + "</span>" : "";
    var drag = ["kid", "test", "reel", "idea", "story", "season"].indexOf(p.kind) >= 0 && p.status !== "posted" && !(p.kind === "story" && p.postiz);
    return '<button type="button" class="cc-it ' + catOf(p) + (p._clash ? " is-clash" : "") + '" data-open="' + esc(p.id) + '"' + (drag ? ' draggable="true"' : "") +
      ' aria-label="' + esc(kindLabel(p) + ", " + (p.time || "בלי שעה") + ", " + title + ", " + (p.status_he || "")) + '">' + kindIcon(p) +
      (p.time ? '<span class="t">' + p.time + "</span>" : "") + '<span class="x" translate="no">' + esc(title) + "</span>" + ab +
      (p.status ? '<span class="cc-s s-' + p.status + '">' + ic(ST_ICON[p.status]) + "</span>" : "") + "</button>";
  }

  function viewTitle() {
    if (S.view === "month") return monthHe(S.month);
    if (S.view === "week") {
      var a = parse(weekStart()), b = parse(addDays(weekStart(), 6));
      return a.getMonth() === b.getMonth() ? a.getDate() + " עד " + b.getDate() + " ב" + MONTHS[b.getMonth()] + " " + b.getFullYear()
        : a.getDate() + " ב" + MONTHS[a.getMonth()] + " עד " + b.getDate() + " ב" + MONTHS[b.getMonth()] + " " + b.getFullYear();
    }
    var d = parse(S.sel || today());
    return dayName(S.sel || today()) + ", " + d.getDate() + " ב" + MONTHS[d.getMonth()] + " " + d.getFullYear();
  }

  function renderView() {
    var v = $("#ccView");
    v.dataset.view = S.view;
    if (!S.data) { v.innerHTML = '<div class="cc-skel">' + new Array(36).join('<i class="lb-skeleton"></i>') + "</div>"; return; }
    if (S.view === "week") return renderWeek(v);
    if (S.view === "day") return renderDay(v);
    renderMonth(v);
  }

  /* the month fills the window: whole weeks, the days of the month before and after as a faded hint, and each day shows as many
     entries as fit, then "+N עוד" (Yarin, 11 Nov 2026: "view the entire month ... a hint of previous/next month ... i don't want to scroll") */
  function renderMonth(v) {
    var first = parse(S.month + "-01"), days = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate(), off = first.getDay();
    var weeks = Math.ceil((off + days) / 7), t = today(), start = addDays(S.month + "-01", -off), h = "";
    for (var i = 0; i < weeks * 7; i++) {
      var ds = addDays(start, i), wd = i % 7, dn = +ds.slice(8), adj = ds.slice(0, 7) !== S.month;
      var ps = dayPieces(ds), ms = missing(ds), mis = adj ? 0 : ms.carousel + ms.reel;
      var mtitle = mis ? "חסרים: " + [ms.carousel ? ms.carousel + " קרוסלות" : "", ms.reel ? ms.reel + " רילס" : ""].filter(Boolean).join(", ") : "";
      var rows = ps.map(function (p, k) { return { t: p.time || "99", k: k, html: itemHtml(p, true) }; })
        .concat((adj ? [] : slotsOf(ds)).map(function (sl, k) { return { t: sl.time || "99", k: 100 + k, html: gapHtml(sl) }; }))
        .sort(function (a, b) { return a.t.localeCompare(b.t) || a.k - b.k; });
      var num = dn + (dn === 1 || i === 0 ? " " + MON_SHORT[+ds.slice(5, 7) - 1] : "");
      h += '<div class="cc-cell' + (adj ? " is-adj" : "") + (wd >= 5 ? " is-we" : "") + (ds < t ? " is-past" : "") + (ds === t ? " is-today" : "") + (ds === S.sel ? " is-sel" : "") +
        '" role="button" tabindex="0" data-day="' + ds + '" aria-label="' + esc(dayName(ds) + " " + full(ds) + ", " + ps.length + " פריטים" + (mtitle ? ", " + mtitle : "")) + '">' +
        '<div class="cc-ch"><span class="cc-n">' + num + "</span>" + (keyDate(ds) ? '<span class="cc-hol" title="' + esc(keyDate(ds)) + '">' + esc(keyDate(ds)) + "</span>" : "") +
        "</div>" + rows.map(function (x) { return x.html; }).join("") +
        '<div class="cc-dots">' + ps.slice(0, 5).map(function (p) { return '<span class="' + catOf(p) + '">' + kindIcon(p) + "</span>"; }).join("") +
        (ps.some(function (p) { return (p.needs || []).length; }) ? '<span class="cc-ico need" title="מחכה לך">' + ic("bell") + "</span>" : "") + "</div></div>";
    }
    v.innerHTML = '<div class="cc-dow">' + DOW.map(function (x, i) { return "<span>" + DAYS[i] + "</span>"; }).join("") + '</div><div class="cc-month" style="--weeks:' + weeks + '">' + h + "</div>";
    fitMonth();
  }
  function settle() {
    $$(".cc-wcol").forEach(function (col) {
      var bs = $$(".cc-wb,.cc-db,.cc-wgap", col);
      bs.forEach(function (b) { if (!b.dataset.top) b.dataset.top = b.style.top; b.style.top = b.dataset.top; });   /* back to the place in time before it is settled again */
      /* blocks make room for every block they share space with side to side, a full-width block and a half-width one included
         (20 Nov 2026: a full-width 21:30 reel was lifted over the 19:30 story beside it) */
      var box = bs.map(function (b) { return { b: b, l: b.offsetLeft, r: b.offsetLeft + b.offsetWidth, t0: b.offsetTop, top: b.offsetTop, h: b.offsetHeight }; });
      function side(a, c) { return a.l < c.r - 1 && c.l < a.r - 1; }
      box.sort(function (a, c) { return a.top - c.top; });
      box.forEach(function (x, i) { for (var j = 0; j < i; j++) { var y = box[j]; if (side(x, y) && x.top < y.top + y.h + 3) x.top = y.top + y.h + 3; } });
      /* a block that would run past the bottom of the column is lifted so its text stays on screen, and the blocks above it make way */
      box.sort(function (a, c) { return a.top - c.top; });
      for (var i = box.length - 1; i >= 0; i--) {
        var x = box[i], lim = col.clientHeight - 3;
        for (var j = i + 1; j < box.length; j++) if (side(x, box[j])) lim = Math.min(lim, box[j].top - 3);
        if (x.top + x.h > lim) x.top = Math.max(0, lim - x.h);
      }
      box.forEach(function (x) { if (x.top !== x.t0) x.b.style.top = x.top + "px"; });
    });
  }
  function fitMonth() {
    var MORE = 22;
    $$(".cc-month .cc-cell").forEach(function (cell) {
      var its = $$(".cc-it", cell), old = $(".cc-more", cell), n = its.length;
      if (old) old.remove();
      its.forEach(function (x) { x.style.display = ""; });
      if (!n || !its[0].offsetHeight) return;
      var lim = cell.clientHeight - 4, last = its[n - 1];
      if (last.offsetTop + last.offsetHeight <= lim) return;
      var k = 0;
      for (var i = 0; i < n; i++) { if (its[i].offsetTop + its[i].offsetHeight <= lim - MORE) k = i + 1; else break; }
      its.slice(k).forEach(function (x) { x.style.display = "none"; });
      var b = document.createElement("button");
      var hid = its.slice(k).filter(function (x) { return !x.classList.contains("cc-gap"); }).length;
      if (!hid) return;
      b.type = "button"; b.className = "cc-more"; b.dataset.day = cell.dataset.day; b.textContent = "+" + hid + " עוד";
      var dots = $(".cc-dots", cell); cell.insertBefore(b, dots);
    });
  }

  function legend() {
    var tg = (S.data && S.data.targets) || {};
    return ["kid", "test", "season", "reel", "story"].filter(function (k) { return k !== "test" || ((S.data || {}).pieces || []).some(function (p) { return p.kind === "test"; }); }).map(function (k) { return '<span class="' + CAT[k] + '">' + '<span class="cc-ico">' + ic(KIND[k].icon) + "</span>" + KIND[k].he + "</span>"; }).join("") +
      '<span>' + ic("check", "cc-s s-posted") + "עלה</span><span>" + ic("clock", "cc-s s-scheduled") + "מתוזמן</span><span>" + ic("target", "cc-s s-hook") + "מחכה להחלטה שלך</span>" +
      '<span class="cc-lg-miss"><span class="cc-gap-lg" aria-hidden="true"></span> עוד לא מולא לפי היעד: ' + (tg.carousel || 2) + " קרוסלות ו־" + (tg.reel || 2) + " רילס ביום</span>";
  }

  /* week and day: hour after hour, like a calendar, the whole range of the day's posts on one screen (rows share the height) */
  function weekStart() { var d = parse(S.sel || today()); d.setDate(d.getDate() - d.getDay()); return iso(d); }
  function hourRange(dss, extra) {
    var H0 = 24, H1 = -1;
    dss.forEach(function (ds) { dayPieces(ds).forEach(function (p) { if (p.time) { var h = +p.time.slice(0, 2); H0 = Math.min(H0, h); H1 = Math.max(H1, h); } }); });
    (extra || []).forEach(function (tm) { var h = +tm.slice(0, 2); H0 = Math.min(H0, h); H1 = Math.max(H1, h); });
    if (H1 < 0) { H0 = 8; H1 = 21; }
    return [Math.max(0, Math.min(H0, 8)), Math.min(23, Math.max(H1 + 1, 22))];
  }
  function mins(tm) { var m = tm.split(":"); return +m[0] * 60 + +m[1]; }
  function lanesOf(list, dur) {   /* side by side when two entries overlap in time */
    var ends = [], group = [], gEnd = -1;
    function flush() { group.forEach(function (it) { it.n = ends.length; }); group = []; ends = []; gEnd = -1; }
    list.sort(function (a, b) { return a.min - b.min; }).forEach(function (it) {
      if (it.min >= gEnd) flush();
      var c = ends.findIndex(function (e) { return e <= it.min; });
      if (c < 0) { c = ends.length; ends.push(0); }
      ends[c] = it.min + dur; it.col = c; group.push(it); gEnd = Math.max(gEnd, it.min + dur);
    });
    flush(); return list;
  }
  function placeStyle(it, r, dur) {
    var tot = (r[1] - r[0] + 1) * 60, top = (it.min - r[0] * 60) / tot * 100, hh = (Math.min(it.min + dur, (r[1] + 1) * 60) - it.min) / tot * 100;
    /* a few pixels of air on every side, so a block never touches the edge of its column; a block is at least as tall as its slot in time but grows to show all its text (Yarin, 11 Nov 2026) */
    return "top:calc(" + top.toFixed(3) + "% + 3px);min-height:calc(" + hh.toFixed(3) + "% - 6px);height:auto;inset-inline-start:calc(" + (it.col * 100 / it.n).toFixed(3) + "% + 4px);width:calc(" + (100 / it.n).toFixed(3) + "% - 8px)";
  }
  function railHtml(r) { var h = ""; for (var x = r[0]; x <= r[1]; x++) h += "<span>" + String(x).padStart(2, "0") + ":00</span>"; return '<div class="cc-wrail">' + h + "</div>"; }
  function nowLine(ds, r) {
    if (ds !== today()) return "";
    var d = new Date(), m = d.getHours() * 60 + d.getMinutes(), tot = (r[1] - r[0] + 1) * 60;
    if (m < r[0] * 60 || m > (r[1] + 1) * 60) return "";
    return '<i class="cc-now" style="top:' + ((m - r[0] * 60) / tot * 100).toFixed(3) + '%" aria-hidden="true"></i>';
  }
  function renderWeek(v) {
    var ws = weekStart(), t = today(), dss = [], i;
    for (i = 0; i < 7; i++) dss.push(addDays(ws, i));
    var extra = [];
    dss.forEach(function (ds) { slotsOf(ds).forEach(function (x) { if (x.time) extra.push(x.time); }); });
    var r = hourRange(dss, extra), N = r[1] - r[0] + 1, DUR = 55, head = '<span></span><span class="cc-gut"></span>', lane = '<span></span><span class="cc-gut"></span>', cols = "", anyUntimed = false;
    dss.forEach(function (ds, j) {
      var ps = dayPieces(ds), sl = slotsOf(ds), untimed = ps.filter(function (p) { return !p.time; });
      if (untimed.length) anyUntimed = true;
      head += '<button type="button" class="cc-wh' + (ds === t ? " is-today" : "") + (ds === S.sel ? " is-sel" : "") + (ds.slice(0, 7) !== S.month ? " is-adj" : "") + '" data-day="' + ds + '"><span>' + DAYS[j] + "</span><b>" + ddmm(ds) + "</b>" +
        "</button>";
      lane += '<div class="cc-wnotime">' + untimed.map(function (p) { return itemHtml(p); }).join("") + "</div>";
      var its = lanesOf(ps.filter(function (p) { return p.time; }).map(function (p) { return { p: p, min: mins(p.time) }; }), DUR);
      cols += '<div class="cc-wcol' + (j >= 5 ? " is-we" : "") + (ds === t ? " is-today" : "") + (ds < t ? " is-past" : "") + '" data-day="' + ds + '" data-r0="' + r[0] + '" data-r1="' + r[1] + '">' + its.map(function (it) {
        var p = it.p;
        return '<button type="button" class="cc-wb ' + catOf(p) + (p._clash ? " is-clash" : "") + '" data-open="' + esc(p.id) + '"' + (["kid", "test", "reel", "idea"].indexOf(p.kind) >= 0 && p.status !== "posted" ? ' draggable="true"' : "") +
          ' style="' + placeStyle(it, r, DUR) + '"><span class="t">' + kindIcon(p) + p.time + (p.status ? '<span class="cc-s s-' + p.status + '">' + ic(ST_ICON[p.status]) + "</span>" : "") +
          '</span><span class="x" translate="no">' + esc(p.title || "") + "</span></button>";
      }).join("") + sl.filter(function (x) { return x.time; }).map(function (x) {
        return '<div class="cc-wgap" data-family="' + x.family + '" data-time="' + x.time + '" role="img" aria-label="' + esc(gapLabel(x)) + '" title="' + esc(gapLabel(x)) + '" style="' + placeStyle({ min: mins(x.time), col: 0, n: 1 }, r, DUR) + '"><span class="t">' + x.time + '</span><span class="x">' + esc(x.he) + "</span></div>";
      }).join("") + nowLine(ds, r) + "</div>";
    });
    v.innerHTML = '<div class="cc-week' + (anyUntimed ? " has-lane" : "") + '" style="--rows:' + N + '">' + head + lane + railHtml(r) + '<span class="cc-gut"></span>' + cols + "</div>";
    settle();
  }
  function renderDay(v) {
    var ds = S.sel || today(), t = today(), ps = dayPieces(ds), DUR = 60;   /* one hour: a block never reaches into the next hour's group, so a busy evening splits into its own rows instead of one wall of narrow columns */
    var timed = ps.filter(function (p) { return p.time; }), untimed = ps.filter(function (p) { return !p.time; });
    var slots = slotsOf(ds);
    var r = hourRange([ds], slots.filter(function (s) { return s.time; }).map(function (s) { return s.time; }));
    ps.concat(slots).forEach(function (x) { if (x.time) r[1] = Math.min(23, Math.max(r[1], Math.ceil((mins(x.time) + DUR) / 60) - 1)); });   /* room for the last block */
    var N = r[1] - r[0] + 1;
    var its = lanesOf(timed.map(function (p) { return { p: p, min: mins(p.time) }; }).concat(slots.filter(function (s) { return s.time; }).map(function (s) { return { slot: s, min: mins(s.time) }; })), DUR);
    var blocks = its.map(function (it) {
      if (it.slot) {
        var s = it.slot;
        return '<div class="cc-db is-slot" data-n="' + it.n + '" data-family="' + s.family + '" data-time="' + s.time + '" style="' + placeStyle(it, r, DUR) + '"><span class="r1">' + ic(s.family === "reel" ? "clapper" : "slides") + "<span>" + s.he + ' · <b class="lb-num">' + s.time + "</b></span></span>" +
          '' + (s.family === "reel" ? "" : '<button type="button" class="lb-btn secondary sm" data-act="new" data-for="' + s.family + '" data-day="' + ds + '" data-time="' + s.time + '">' + ic("plus") + "רעיון</button>") + "</div>";
      }
      var p = it.p, fl = (p.flags || [])[0];
      return '<button type="button" class="cc-db ' + catOf(p) + (p.kind === "reel" ? " is-reel" : "") + (p._clash ? " is-clash" : "") + '" data-n="' + it.n + '" data-open="' + esc(p.id) + '"' + (["kid", "test", "reel", "idea"].indexOf(p.kind) >= 0 && p.status !== "posted" ? ' draggable="true"' : "") + ' style="' + placeStyle(it, r, DUR) + '">' +
        '<span class="cc-thumb" aria-hidden="true">' + thumbHtml(p) + "</span>" +
        '<span class="b"><span class="r1">' + kindIcon(p) + '<span class="k">' + esc(kindLabel(p)) + '</span><b class="lb-num">' + p.time + "</b>" + stChip(p) + chans(p) + "</span>" +
        '<span class="tl" translate="no">' + esc(p.title || "") + "</span>" + (fl ? '<span class="cc-flag">' + ic("info") + esc(fl.he) + "</span>" : "") + "</span>" + bellHtml(p) + "</button>";
    }).join("");
    var nt = slots.filter(function (s) { return !s.time; }).map(function (s) {
      return '<span class="cc-slot">' + ic(s.family === "reel" ? "clapper" : "slides") + s.he + (s.family === "reel" ? "" : '<button type="button" class="lb-btn secondary sm" data-act="new" data-for="' + s.family + '" data-day="' + ds + '" data-time="">' + ic("plus") + "רעיון</button>") + "</span>";
    }).join("");
    var top = (untimed.length || nt ? '<div class="cc-dlane"><span class="l">בלי שעה</span>' + untimed.map(function (p) { return itemHtml(p); }).join("") + nt + "</div>" : "");
    v.innerHTML = '<div class="cc-dayv' + (ds < t ? " is-past" : "") + '" style="--rows:' + N + '">' + top +
      '<div class="cc-dgrid">' + railHtml(r) + '<span class="cc-gut"></span><div class="cc-wcol cc-dcol' + (ds === t ? " is-today" : "") + '" data-day="' + ds + '" data-r0="' + r[0] + '" data-r1="' + r[1] + '">' + blocks + nowLine(ds, r) +
      (!ps.length && !slots.length ? '<div class="cc-empty-day">אין כלום ביום הזה</div>' : "") + "</div></div></div>";
    settle();
  }

  /* ---------- the drawer: a day, or a piece inside it ---------- */
  var dlg, DOCK_MIN = 900, docked = false;
  function dockRoom() { var h = document.documentElement; return h.clientWidth - (parseFloat(getComputedStyle(h).paddingRight) || 0); }
  /* an open piece fills the calendar's own area (Yarin, 11 Nov 2026: "a day needs to expand to this red space"): below the top bar,
     next to the page sidebar; the calendar is hidden behind it */
  function placeFill() {
    var tb = $(".cc-top"), bd = $(".cc-body"); if (!tb || !bd) return;
    var top = Math.round(tb.getBoundingClientRect().bottom + 6), r = bd.getBoundingClientRect(), s = dlg.style;
    s.top = top + "px"; s.left = Math.round(r.left) + "px"; s.width = Math.round(r.width) + "px"; s.height = Math.max(240, innerHeight - top - 10) + "px";
  }
  function setDock(on) {
    var h = document.documentElement;
    docked = on; dlg.classList.toggle("is-fill", on); h.classList.toggle("cc-day", on);
    if (on) placeFill(); else { dlg.style.top = dlg.style.left = dlg.style.width = dlg.style.height = ""; }
  }
  function showDlg() {
    var want = dockRoom() >= DOCK_MIN;
    if (dlg.open && want === docked) { if (docked) setDock(true); return; }
    if (dlg.open) dlg.close();
    setDock(want);
    if (want) dlg.show(); else dlg.showModal();
  }
  function syncHash() {
    var h = S.open ? S.open.day + "/" + S.open.piece : S.view === "day" ? S.sel : S.month;
    try { history.replaceState(null, "", "#" + h); } catch (x) {}
  }
  /* a day opens as the day view; with a piece, that piece opens over the calendar */
  function openDay(ds, pid, tab) {
    S.sel = ds; setMonth(ds.slice(0, 7));
    if (pid) { if (S.byId[pid]) return openPiece(pid, tab); }
    if (S.open) closeDlg(true);
    S.view = "day"; store("view", S.view); renderAll(); syncHash();
  }
  function openPiece(pid, tab) {
    var p = S.byId[pid]; if (!p) return;
    S.sel = p.date; S.open = { day: p.date, piece: pid, opt: null };
    syncHash(); renderDrawer(); showDlg(); renderView(); renderSide();
    /* the list starts at the top; a piece waiting for its hook (or a link to a part) starts at that part */
    var jump = tab || (p.status === "hook" ? "hooks" : null), body = $("#ccDlgB");
    body.scrollTop = 0;
    if (jump) requestAnimationFrame(function () { var el = $('[data-part="' + jump + '"]', body); if (el) body.scrollTop += el.getBoundingClientRect().top - body.getBoundingClientRect().top - 12; });
  }
  function closeDlg(quiet) {
    tpStop(); S.open = null; if (dlg.open) dlg.close(); setDock(false);
    syncHash();
    if (!quiet) renderView();
  }
  function setView(v) { S.view = v; store("view", v); if (S.open) closeDlg(true); renderAll(); syncHash(); }
  /* the arrows move by the view: a month, a week or a day */
  function shift(n) {
    if (S.open) closeDlg(true);
    if (S.view === "month") { var m = adjMonth(S.month, n); S.sel = m === today().slice(0, 7) ? today() : m + "-01"; setMonth(m); }
    else { S.sel = addDays(S.sel || today(), S.view === "week" ? 7 * n : n); setMonth(S.sel.slice(0, 7)); }
    renderAll(); syncHash();
  }
  /* היום closes whatever is open and shows today in the current view, ringed for a moment */
  function goToday() {
    if (S.open) closeDlg(true);
    var t = today(); S.sel = t; setMonth(t.slice(0, 7)); renderAll(); syncHash();
    var el = $('.cc-cell.is-today, .cc-wh.is-today, .cc-dcol.is-today');
    if (el) { el.classList.remove("is-flash"); void el.offsetWidth; el.classList.add("is-flash"); }
  }

  function renderDrawer() {
    if (!S.open) return;
    var p = S.open.piece && S.byId[S.open.piece];
    if (!p) { if (S.data) closeDlg(); return; }
    var ds = S.open.day;
    $("#ccDlgT").innerHTML = p ? '<button type="button" class="lb-btn ghost sm" id="ccBack">' + ic("arrow-right") + dayName(ds) + " " + ddmm(ds) + "</button>"
      : esc(dayName(ds)) + " <small>" + full(ds) + "</small>";
    var body = $("#ccDlgB");
    var keep = body.scrollTop;
    body.classList.add("is-piece");
    body.classList.toggle("is-reel", p.kind === "reel");
    body.classList.toggle("is-story", p.kind === "story" || p.kind === "season");
    body.innerHTML = pieceHtml(p);
    afterPiece(p);
    body.scrollTop = keep;
  }

  function thumbHtml(p) {
    var d = p.detail || {}, img = p.thumb || (d.media && d.media.qc);
    if (img) return '<img src="' + esc(img) + '" alt="" loading="lazy">';
    if (d.media && d.media.final) return '<video src="' + esc(d.media.final) + '#t=0.5" muted preload="metadata"></video>';
    return ic((KIND[p.kind] || {}).icon || "image");
  }
  function missingTimes(ds, family) {   /* the planned times of the day's slots nobody fills yet, earliest first */
    var plan = (((S.data || {}).hours || {}).plan || {})[String(parse(ds).getDay())] || {}, roles = family === "reel" ? ["reel_a", "reel_b"] : ["kid", "test"], have = {};
    (S.byDate[ds] || []).forEach(function (p) {
      if (p.kind === "kid") have.kid = 1; else if (p.kind === "test" || p.kind === "season") have.test = 1;   /* a holiday carousel takes the test carousel's slot */
      else if (p.kind === "reel") have[(p.detail && p.detail.option === 2) ? "reel_b" : "reel_a"] = 1;
    });
    return roles.filter(function (r) { return !have[r] && plan[r]; }).map(function (r) { return plan[r]; }).sort();
  }
  /* ---------- the piece panel ---------- */
  function optIndex(p) {
    if (S.open.opt != null && S.open.opt < (p.options || []).length) return S.open.opt;
    var i = (p.options || []).findIndex(function (o) { return o.key === p.picked; });
    return i < 0 ? 0 : i;
  }
  function itemOf(p) { var d = p.detail || {}, i = optIndex(p); return (d.items || [])[i] || null; }
  /* one long list, no tabs (Yarin, 11 Nov 2026: "just make it a long list of features", "dont repeat features"): every part of the
     piece one under the other and each thing once. A reel's hook and a carousel's internal name are edited in the title, a reel's
     script and caption in place (no read-only copy), the finished reel stays beside the list, and nothing jumps between parts. */
  function partsOf(p) {
    if (p.kind === "story") return [["edit", "עריכה", "pencil"], ["publish", "פרסום", "send"]];   /* story.js draws them */
    if (p.kind === "season") return [["edit", "עריכה", "pencil"], ["text", "כיתוב", "instagram"], ["publish", "תמונות ואישור", "check-circle"]];   /* season.js draws them */
    if (p.kind === "post") return [["publish", "פרסום", "send"]];
    if (p.kind === "remind") return [["view", "תצוגה", "eye"]];
    if (p.kind === "idea") return [["view", "הרעיון", "sparkle"], ["hooks", "הוקים", "target"]];
    if (p.kind === "reel") return [["text", "טקסט", "pencil"], ["hooks", "הוקים", "target"], ["make", "הפקה", "clapper"], ["publish", "פרסום", "send"]];
    return [["view", "תצוגה", "eye"], ["hooks", "הוקים", "target"], ["text", "טקסט", "pencil"], ["caption", "כיתוב", "instagram"], ["make", "הפקה", "play"], ["publish", "פרסום", "send"]];
  }
  function pieceHtml(p) {
    if (p.kind === "story") return window.CCStory ? CCStory.html(p) : "";   /* the story editor (story.js, 19 Nov 2026) */
    if (p.kind === "season") return window.CCSeason ? CCSeason.html(p) : "";   /* Black Friday and Hanukkah (season.js, 20 Nov 2026) */
    var parts = partsOf(p), reel = p.kind === "reel", tx = (p.detail || {}).texts || {};
    var oi = optIndex(p);
    var opts = (p.options || []).length > 1 ? '<div class="opts"><span class="lb-segmented" role="group" aria-label="אפשרויות">' + p.options.map(function (o, i) {
      return '<button type="button" data-act="opt" data-i="' + i + '" aria-pressed="' + (i === oi) + '">' + esc(o.label) + (o.key === p.picked ? " ✓" : "") + (o.grade ? " · " + o.grade : "") + "</button>";
    }).join("") + "</span>" + (!p.picked || p.picked !== p.options[oi].key ? (["making", "approve", "ready", "scheduled", "posted"].indexOf(p.status) < 0 ? '<button type="button" class="lb-btn ' + (p.status === "pick" || p.status === "grade" ? "" : "secondary ") + 'sm" data-act="pick" data-id="' + esc(p.id) + '" data-key="' + esc(p.options[oi].key) + '">בוחר בזו</button>' : "") : '<span class="lb-chip success">נבחרה</span>') + "</div>" : "";
    var it = itemOf(p), edit = reel || !!it;
    var title = reel ? '<h3 class="cc-ttl">' + cellHtml("hook", tx.hook, "הוק (הטקסט למעלה)") + "</h3>"
      : it ? '<h3 class="cc-ttl">' + cellHtml("title", it.title, "שם פנימי") + "</h3>"
      : '<h3 translate="no">' + esc(p.title || "") + "</h3>";
    var head = '<div class="cc-ph"><div class="r1">' + kindIcon(p) + "<span>" + esc(kindLabel(p)) + "</span>" + stChip(p) + chans(p) +
      '<span class="lb-spacer"></span>' + (edit ? saveState() : "") + '<span class="lb-num">' + (p.time || "בלי שעה") + "</span></div>" +
      title + (reel ? reelChips(p) : "") + opts + "</div>";
    var PANES = { view: paneView, hooks: paneHooks, text: paneText, caption: paneCaption, make: paneMake, publish: panePublish };
    var body = parts.map(function (t) {
      var html = PANES[t[0]](p, it);
      return parts.length > 1 ? '<section class="cc-part" data-part="' + t[0] + '"><h4 class="cc-part-h">' + ic(t[2]) + t[1] + "</h4>" + html + "</section>"
        : '<div class="cc-part" data-part="' + t[0] + '">' + html + "</div>";
    }).join("");
    var main = reel ? '<div class="cc-reel" id="ccPane">' + reelSide(p) + '<div class="cc-rmain">' + body + "</div></div>" : '<div class="cc-pane" id="ccPane">' + body + "</div>";
    var ask = ["kid", "test", "reel", "idea"].indexOf(p.kind) >= 0 ? askHtml(p) : "";
    return head + main + ask;
  }

  function slideCards(it) {
    return (it.slides || []).map(function (s, i) {
      var t = [s.big, s.headline, s.no && "במקום: " + s.no, s.yes, s.quote].filter(Boolean)[0] || "", b = s.body || s.why || "";
      return '<div class="cc-slidecard"><span class="n">' + (i + 1) + "</span><b translate=\"no\">" + esc(String(t).replace(/\*\*/g, "")) + '</b><span translate="no">' + esc(String(b).replace(/\*\*/g, "")) + "</span></div>";
    }).join("");
  }
  function issues(it) {
    var l = (it && it.lint) || [], e = (it && it.errors) || [];
    var h = l.map(function (x) { return '<div class="' + (x.level === "ERROR" ? "e" : "w") + '">' + esc(x.message || x.path || "") + "</div>"; }).join("") +
      (Array.isArray(e) ? e.map(function (x) { return '<div class="e">' + esc(typeof x === "string" ? x : x.message || JSON.stringify(x)) + "</div>"; }).join("") : "");
    return h ? '<div class="cc-issues">' + h + "</div>" : "";
  }
  /* ---------- a reel is the reel calendar's card (Yarin, 11 Nov 2026: "add full capabilities from the reel calendar") ----------
     the header chips (עשיתי, series, length, voice, audience, the book page, the structure), the script as a table of what is said
     and what is seen with timings from the word count, copy buttons, the teleprompter scroll, the finished reel beside the words */
  function rcfg() { return (S.data && S.data.reels_defaults) || {}; }
  function wc(t) { return String(t || "").split(/\s+/).filter(Boolean).length; }
  function mmss(t) { t = Math.round(t); return Math.floor(t / 60) + ":" + String(t % 60).padStart(2, "0"); }
  function scriptLines(p, vo) {   /* the spoken lines, then the fixed closing line unless the take already says it (reels.own_cta) */
    var d = p.detail || {}, tx = d.texts || {}, R = rcfg(), sees = tx.sees || [];
    var rows = (vo || tx.vo || []).map(function (l, i) { return { say: l, see: sees[i] || "", i: i }; });
    if (!d.own_cta && p.status !== "posted" && R.cta_voice) rows.push({ say: R.cta_voice, see: R.cta_sees || "", fixed: true });
    return rows;
  }
  function timing(rows) {   /* the reel calendar's estimate (reels.seconds): lead seconds on the first line, then words a second */
    var R = rcfg(), lead = +R.lead_seconds || 1, wps = +R.words_per_second || 2.8, t = 0, words = 0;
    var at = rows.map(function (r, k) { var w = wc(r.say), a = t; t += (k === 0 ? lead : 0) + w / wps; words += w; return [a, t]; });
    return { at: at, secs: t, words: words };
  }
  function outOfRange(s) { var R = rcfg(); return s > (+R.max || 30) || s < (+R.min || 10); }
  function reelSecs(p) { var d = p.detail || {}, m = d.media || {}; return d.clip_seconds ? +d.clip_seconds : m.seconds ? m.seconds : Math.round(timing(scriptLines(p)).secs * 10) / 10; }
  function whenTxt(s) { return s ? ddmm(s.slice(0, 10)) + ", " + s.slice(11, 16) : ""; }
  function reelChips(p) {
    var d = p.detail || {}, m = d.media || {}, tx = d.texts || {}, gm = d.audience === "grandma";
    return '<div class="cc-rchips"><button type="button" class="lb-chip check" data-act="made" aria-pressed="' + !!d.made + '" title="סימון שעשית את הריל, כמו בלוח הרילס">עשיתי</button>' +
      (d.series_he ? '<span class="lb-chip" title="הסדרה">' + esc(d.series_he) + "</span>" : "") +
      '<span class="lb-chip" title="' + (m.seconds ? "האורך של הריל שנוצר" : "אורך משוער לפי מספר המילים") + '">' + reelSecs(p) + " שניות</span>" +
      (d.voice_he ? '<span class="lb-chip">' + esc(d.voice_he) + "</span>" : "") +
      '<span class="lb-chip' + (gm ? " accent" : "") + '" title="למי הריל מדבר">מדבר ל' + (gm ? "סבתות" : "הורים") + "</span>" +
      (d.book_url ? '<a class="lb-chip tint" href="' + esc(d.book_url) + '" target="_blank" rel="noopener" title="דף הספר באתר, שאליו מוביל הקישור בהודעה">' + ic("book") + '<span translate="no">' + esc(d.book) + "</span></a>" : "") +
      (tx.structure ? '<span class="lb-chip outline" title="המבנה">' + esc(tx.structure) + "</span>" : "") + "</div>";
  }
  function reelSide(p) {   /* the finished reel beside the words, with its download and open buttons */
    var d = p.detail || {}, m = d.media || {};
    if (!m.final) return '<aside class="cc-rside"><div class="cc-rnone">' + ic("clapper") + "<span>עוד אין ריל מוכן</span></div></aside>";
    return '<aside class="cc-rside"><video class="cc-video" src="' + esc(m.final) + '" controls playsinline preload="metadata"></video>' +
      '<div class="acts"><a class="lb-btn secondary sm" href="' + esc(m.final) + '" download="reel-' + esc(String(d.reel).replace(".", "-")) + '-1.mp4">' + ic("download") + "הורדה</a>" +
      '<a class="lb-btn secondary sm" href="' + esc(m.final) + '" target="_blank" rel="noopener">' + ic("open-out") + "פתיחה בלשונית</a></div>" +
      (m.final_at ? '<span class="cc-note">נוצר ' + whenTxt(m.final_at) + (m.seconds ? ", " + m.seconds + " שניות" : "") + "</span>" : "") + "</aside>";
  }
  function cellHtml(key, value, label, cls) {   /* a field edited in place: plain text until it is touched, saved when it is left */
    return '<textarea class="cc-cell lb-editable' + (cls ? " " + cls : "") + '" dir="rtl" rows="1" data-f="' + esc(key) + '" aria-label="' + esc(label) + '" translate="no">' + esc(value || "") + "</textarea>";
  }
  var TP = { on: false, lvl: 3, raf: 0, last: 0, acc: 0 }, TP_SPEED = [0, 8, 12, 18, 26, 36, 50, 68];   /* px a second for 1 to 7 */
  function tpHtml() {
    return '<span class="cc-tp" role="group" aria-label="גלילה אוטומטית של התסריט"><button type="button" class="lb-chip check" data-act="tp" aria-pressed="' + TP.on + '" title="גלילה איטית של התסריט, כמו טלפרומפטר">' + (TP.on ? "גלילה" : "▶ גלילה") + "</button>" +
      '<button type="button" class="lb-chip" data-act="tp-speed" data-d="-1" aria-label="לאט יותר">−</button><span class="lb-num" id="ccTpS" aria-live="polite">' + TP.lvl + "</span>" +
      '<button type="button" class="lb-chip" data-act="tp-speed" data-d="1" aria-label="מהר יותר">+</button></span>';
  }
  function tpPaint() { var g = $('[data-act="tp"]'); if (g) { g.setAttribute("aria-pressed", String(TP.on)); g.textContent = TP.on ? "גלילה" : "▶ גלילה"; } var s = $("#ccTpS"); if (s) s.textContent = TP.lvl; }
  function tpStep(now) {
    if (!TP.on) return;
    var b = $("#ccDlgB"); if (!b) { tpStop(); return; }
    var dt = TP.last ? Math.min(100, now - TP.last) : 16; TP.last = now;
    TP.acc += TP_SPEED[TP.lvl] * dt / 1000;
    if (TP.acc >= 1) { var n = Math.floor(TP.acc); TP.acc -= n; b.scrollTop += n; }
    if (b.scrollTop + b.clientHeight >= b.scrollHeight - 1) { tpStop(); return; }
    TP.raf = requestAnimationFrame(tpStep);
  }
  function tpStart() { TP.on = true; TP.last = 0; TP.acc = 0; cancelAnimationFrame(TP.raf); TP.raf = requestAnimationFrame(tpStep); tpPaint(); }
  function tpStop() { if (!TP.on) return; TP.on = false; cancelAnimationFrame(TP.raf); tpPaint(); }
  function scriptHtml(p, edit) {
    var rows = scriptLines(p), tm = timing(rows), R = rcfg();
    var trs = rows.map(function (r, k) {
      var say = edit && !r.fixed ? cellHtml("vo__" + r.i, r.say, "שורה " + (r.i + 1)) : '<div translate="no">' + esc(r.say) + "</div>";
      var see = edit && !r.fixed ? cellHtml("sees__" + r.i, r.see, "מה רואים בשורה " + (r.i + 1)) : '<div translate="no">' + esc(r.see) + "</div>";
      return "<tr" + (r.fixed ? ' class="is-fixed" title="קבוע לכל הרילס"' : "") + '><td class="tc" data-label="זמן"><span class="t0">' + mmss(tm.at[k][0]) + '</span><span class="t1">' + mmss(tm.at[k][1]) + "</span></td>" +
        '<td class="say" data-label="מה אני אומר">' + say + '</td><td class="see" data-label="מה רואים">' + see + "</td></tr>";
    }).join("");
    return '<section class="cc-rsec cc-scr" id="ccScr"><div class="cc-scr-head"><h4>' + ic("clapper") + "תסריט</h4>" +
      '<span class="cc-scr-sum' + (outOfRange(tm.secs) ? " is-out" : "") + '" title="ריל של ' + (R.min || 10) + " עד " + (R.max || 30) + ' שניות"><b class="s">' + Math.round(tm.secs) + '</b> שניות, <b class="w">' + tm.words + "</b> מילים</span>" +
      '<button type="button" class="lb-btn secondary sm cc-copy" data-act="copy-script" title="מעתיק רק את מה שאומרים, שורה לכל מחשבה">' + ic("copy") + "העתקת התסריט</button>" + tpHtml() + "</div>" +
      '<div class="lb-table-wrap"><table class="lb-table top is-stack"><thead><tr><th class="tc">זמן</th><th>מה אני אומר</th><th>מה רואים</th></tr></thead><tbody>' + trs + "</tbody></table></div></section>";
  }
  function retime() {   /* the timings follow a line while it is typed, like the reel calendar */
    var sc = $("#ccScr"), p = S.open && S.byId[S.open.piece]; if (!sc || !p || p.kind !== "reel") return;
    var vo = (p.detail.texts.vo || []).map(function (l, i) { var t = $('textarea[data-f="vo__' + i + '"]', sc); return t ? t.value : l; });
    var tm = timing(scriptLines(p, vo)), sum = $(".cc-scr-sum", sc);
    $$("tbody tr", sc).forEach(function (tr, k) { if (tm.at[k]) { $(".t0", tr).textContent = mmss(tm.at[k][0]); $(".t1", tr).textContent = mmss(tm.at[k][1]); } });
    $(".s", sum).textContent = Math.round(tm.secs); $(".w", sum).textContent = tm.words; sum.classList.toggle("is-out", outOfRange(tm.secs));
  }
  function capSec(p, edit) {
    var tx = (p.detail || {}).texts || {}, R = rcfg();
    return '<section class="cc-rsec"><div class="cc-scr-head"><h4>' + ic("instagram") + "כיתוב לאינסטגרם</h4>" +
      '<button type="button" class="lb-btn secondary sm cc-copy is-end" data-act="copy-cap" title="מעתיק את הכיתוב כמו שהוא עולה, עם ההסתייגות">' + ic("copy") + "העתקה</button></div>" +
      (edit ? cellHtml("caption", tx.caption, "כיתוב", "cc-cap-ed") : '<div class="lb-textblock cc-cap" translate="no">' + esc(tx.caption) + "</div>") +
      '<div class="cc-fixed">נוסף בסוף, קבוע: <span translate="no">' + esc(R.disclaimer || window.CC_DISCLAIMER || "") + "</span></div></section>";
  }
  function copyText(text, btn) {
    var lbl = btn.innerHTML, ok = function () { btn.textContent = "הועתק ✓"; setTimeout(function () { btn.innerHTML = lbl; }, 1600); };
    function old() {
      var ta = document.createElement("textarea"); ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); ok(); } catch (x) { toast("לא הצליח להעתיק"); }
      ta.remove();
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, old); else old();
  }
  function scriptText(p) {   /* only what is said, a line per thought; the lines being edited as they are now */
    var vo = (p.detail.texts.vo || []).map(function (l, i) { var t = $('#ccScr textarea[data-f="vo__' + i + '"]'); return t ? t.value : l; });
    return scriptLines(p, vo).map(function (r) { return r.say.trim(); }).filter(Boolean).join("\n");
  }

  function paneView(p, it) {
    var d = p.detail || {};
    if (p.kind === "remind") return '<div class="cc-box"><h4>' + ic("bell") + "גרסאות הניסיון של אתמול</h4><p>לבחור אחת, לשתף אותה לפיד הראשי באינסטגרם (באפליקציה) ולהעלות אותה לפייסבוק (מכאן).</p>" +
      '<div class="lb-row"><label class="lb-field">לפייסבוק, תאריך<input class="lb-input" type="date" id="ccFbD" value="' + (p.date >= today() ? p.date : today()) + '"></label><label class="lb-field">שעה<input class="lb-input" type="time" id="ccFbTm" value="10:00"></label></div>' +
      '<label class="cc-f"><span>טקסט לפייסבוק</span><textarea class="lb-textarea lb-editable" dir="rtl" id="ccFbTx" translate="no">' + esc(d.fb_text || "") + "</textarea></label>" +
      (d.trials || []).map(function (u, i) { var did = (d.fb_done || []).indexOf(i) >= 0; return '<div class="cc-box"><video class="cc-video" src="' + esc(u) + '" controls preload="metadata"></video>' +
        (did ? '<span class="lb-chip success">נשלחה לפייסבוק</span>' : '<button type="button" class="lb-btn secondary sm" data-act="reel-postiz" data-kind="fb_trial" data-i="' + i + '">להעלות את זו לפייסבוק</button>') + "</div>"; }).join("") +
      '<div class="lb-row"><button type="button" class="lb-btn ok" data-act="remind-done" data-id="' + esc(p.id) + '">' + (d.done ? "בוצע" : "סימון שבוצע") + "</button></div></div>";
    if (p.kind === "idea") {
      var idea = d.idea || {};
      return '<div class="cc-box"><h4>' + ic("sparkle") + (idea.for === "reel" ? "רעיון לריל" : "רעיון לקרוסלה") + '</h4><p translate="no">' + esc(idea.brief || "") + "</p>" +
        "<p>לבנות ממנו " + (idea.for === "reel" ? "ריל בלוח הרילס" : "קרוסלה במכונת הקרוסלות") + ": לכתוב ל-Claude בשיחה, למשל \"תבנה את הרעיונות שבלוח תוכן\". הוא קורא אותם משם, עם ההוק שבחרת.</p>" +
        '<div class="lb-row"><button type="button" class="lb-btn secondary sm" data-act="idea-del" data-id="' + esc(p.id) + '">למחוק את הרעיון</button></div></div>';
    }
    var imgs = [];
    if (p.picked && it && it.key === p.picked && (d.slides || []).length) imgs = d.slides;
    else if (it && (it.images || []).length) imgs = it.images;
    else if (!it && (d.slides || []).length) imgs = d.slides;
    var strip = imgs.length ? imgs.map(function (u) { return '<div><img src="' + esc(u) + '" alt="" loading="lazy"></div>'; }).join("") : it ? slideCards(it) : "";
    var o = (p.options || [])[optIndex(p)] || {};
    var grade = d.batch !== undefined || p.kind === "test" ? '<div class="cc-grade"><span class="cc-note">ציון</span><span class="lb-segmented" role="group" aria-label="ציון">' + [1, 2, 3, 4, 5].map(function (n) {
      return '<button type="button" data-act="grade" data-n="' + n + '" aria-pressed="' + (o.grade === n) + '">' + n + "</button>";
    }).join("") + "</span></div>" : "";
    return '<div class="cc-strip">' + (strip || '<div class="cc-slidecard"><b>אין עדיין שקופיות</b></div>') + "</div>" + (it && p.kind !== "reel" && p.status !== "posted" && p.status !== "scheduled" ? grade : "") + issues(it);
  }

  function hookKey(p) {
    if (p.kind === "reel") return p.id;
    if (p.kind === "idea") return p.id;
    var d = p.detail || {};
    if (!p.picked) return null;
    return d.hook_key || null;
  }
  function currentHook(p, it) {
    if (p.kind === "reel") return (p.detail.texts || {}).hook || "";
    if (p.kind === "idea") return "";
    var s = it && (it.slides || [])[0];
    return s ? (s.big || s.headline || "") : "";
  }
  function paneHooks(p, it) {
    var k = hookKey(p);
    if (!k) return '<p class="cc-note">נפתח אחרי שבוחרים אפשרות: חמשת ההוקים נכתבים לאפשרות שבחרת, ורק אחרי שבוחרים הוק אפשר להפיק.</p>';
    var hk = (p.detail || {}).hooks || {}, opts = hk.options || [], run = jobFor(p.id, "hooks"), h = "";
    if (opts.length) {
      h += '<div class="cc-hooks">' + opts.map(function (q, i) {
        var picked = hk.picked === i, trial = (hk.trial || []).indexOf(i) >= 0;
        return '<div class="cc-hook' + (picked ? " is-picked" : "") + '"><span class="lb-num lb-dim">' + (i + 1) + '</span><span class="q" translate="no">' + esc(q) + "</span><span class=\"lb-row\">" +
          (p.kind === "reel" ? '<label><input type="checkbox" data-act="trialhook" data-i="' + i + '"' + (trial ? " checked" : "") + (picked ? " disabled" : "") + ">לגרסת ניסיון</label>" : "") +
          (picked ? '<span class="lb-chip success">נבחר</span>' : '<button type="button" class="lb-btn secondary sm" data-act="hookpick" data-i="' + i + '">בוחר בזה</button>') + "</span></div>";
      }).join("") + "</div>";
      if (p.kind === "reel") h += '<p class="cc-note">ההוק שבחרת הוא הגרסה הראשית; 4 ההוקים האחרים שמסמנים הם גרסאות הניסיון (אינסטגרם בלבד), אחרי שהגרסה הראשית אושרה. מסומנים: ' + (hk.trial || []).length + ' מתוך 4.</p>';
    }
    h += '<div class="lb-row">' + (run ? '<span class="lb-spinner" aria-hidden="true"></span><span class="cc-note">כותב 5 הוקים…</span>' :
      '<button type="button" class="lb-btn' + (opts.length ? " secondary" : "") + ' sm" data-act="hooks">' + ic("sparkle") + (opts.length ? "5 הוקים חדשים" : "לכתוב 5 הוקים") + "</button>") + "</div>";
    return h;
  }

  function field(label, key, value, attrs) {
    return '<label class="cc-f"><span>' + esc(label) + '</span><textarea class="lb-textarea lb-editable" dir="rtl" rows="1" data-f="' + esc(key) + '"' + (attrs || "") + ' translate="no">' + esc(value || "") + "</textarea></label>";
  }
  function saveState() { return '<span class="lb-savestate" id="ccSave">נשמר</span>'; }
  function paneText(p, it) {
    var d = p.detail || {};
    if (p.kind === "reel") {   /* the reel calendar's card, edited in place (every cell saves when it is left); the hook is the title */
      var tx = d.texts || {};
      return scriptHtml(p, true) +
        '<section class="cc-rsec"><h4>' + ic("eye") + "השיא על המסך</h4>" + cellHtml("payoff", tx.payoff, "השיא על המסך") + "</section>" +
        '<section class="cc-rsec"><h4>' + ic("film") + "מה מצלמים</h4>" + cellHtml("shot", tx.shot, "מה מצלמים") + "</section>" +
        capSec(p, true) +
        (d.shoot ? '<section class="cc-rsec"><h4>' + ic("calendar") + 'יום צילום</h4><p translate="no">' + esc(d.shoot) + "</p></section>" : "") +
        '<div id="ccLint" class="cc-issues"></div>';
    }
    if (!it) return '<div class="cc-box"><h4>' + ic("pencil") + "הקרוסלה הזאת כבר הופקה</h4><p>הטקסט שלה נערך בעמוד מכונת הקרוסלות, ואחרי עריכה צריך לייצא מחדש.</p>" +
      '<div class="lb-row"><a class="lb-btn secondary sm" href="/hook-studio/" target="_blank">מכונת הקרוסלות</a></div></div>';
    var note = p.picked && ["ready", "scheduled", "posted"].indexOf(p.status) >= 0 ? '<div class="cc-box is-warn"><p>הקרוסלה כבר הופקה: עריכה כאן משנה את הטקסט, והשקופיות המוכנות משתנות רק אחרי ייצוא מחדש בהפקה למטה.</p></div>' : "";
    var h = note + '<div class="cc-fields">';
    (it.slides || []).forEach(function (s, i) {
      var n = i + 1, fs = [];
      if (p.kind === "test") TEST_FIELDS.forEach(function (f) { if (s[f] !== undefined) fs.push(field(FIELD_HE[f], f + "@" + n, s[f])); });
      else {
        var last = n === it.slides.length;
        if (!last) fs.push(field("כותרת", "headline@" + n, s.headline));
        if (!last) fs.push(field("גוף", "body@" + n, s.body));
        if (s.label !== undefined && n !== 1 && !last) fs.push(field("תווית", "label@" + n, s.label));
      }
      if (fs.length) h += '<div class="cc-fgroup"><b>שקופית ' + n + (s.layout ? " · " + esc(s.layout) : s.role ? " · " + esc(s.role) : "") + "</b>" + fs.join("") + "</div>";
    });
    return h + "</div>";
  }
  function paneCaption(p, it) {
    var disc = (window.CC_DISCLAIMER || "");
    if (!it) return '<div class="cc-fixed" translate="no">' + esc((p.detail || {}).caption || "") + "</div>";
    var h = '<div class="cc-two">' + field("כיתוב לאינסטגרם", "caption", it.caption) +
      (p.kind === "test" ? field("טקסט לפייסבוק", "fb_text", it.fb_text) : '<div class="cc-fixed">לפייסבוק נכתב טקסט משלו בייצוא, עם קישור לאתר.</div>') + "</div>" +
      field("קריאה לפעולה", "cta", it.cta) + (p.kind === "test" ? field("מילת תגובה", "comment_word", it.comment_word) : "");
    return h + '<div class="cc-fixed">נוסף בסוף כל כיתוב, קבוע: <span translate="no">' + esc(disc) + "</span></div>";
  }

  function jobFor(pid, kind) { return S.jobs.find(function (j) { return j.reel === pid && (!kind || j.kind === kind) && (j.status === "queued" || j.status === "running"); }); }
  function taskFor(kind, reel) { return S.tasks.find(function (t) { return t.kind === kind && t.reel === reel; }); }
  function reelJob(rkey) { return S.reelJobs.filter(function (j) { return j.reel === rkey; }).sort(function (a, b) { return (b.started || "").localeCompare(a.started || ""); })[0]; }

  function paneMake(p, it) {
    var d = p.detail || {};
    if (p.kind === "reel") return paneMakeReel(p, d);
    var run = d.run, o = (p.options || [])[optIndex(p)] || {}, h = "";
    var hk = d.hooks || {};
    if (!p.picked || (!run && hk.picked == null)) return '<p class="cc-note">נפתח אחרי שבוחרים ' + (p.picked ? "הוק" : "אפשרות והוק") + ".</p>";
    if (run) {
      h += '<dl class="cc-kv"><dt>מצב</dt><dd>' + esc(run.status_he || run.status || "") + "</dd>" + (run.spent_usd != null ? "<dt>עלות עד עכשיו</dt><dd>$" + Number(run.spent_usd).toFixed(3) + "</dd>" : "") +
        (run.error ? "<dt>נעצר</dt><dd>" + esc(run.error).slice(0, 300) + "</dd>" : "") + (run.warning ? "<dt>הערה</dt><dd>" + esc(run.warning) + "</dd>" : "") + "</dl>";
      if (run.status === "approval" && run.approval) {
        var ap = run.approval;
        h += '<div class="cc-box is-warn"><h4>' + ic("wallet") + "מחכה לתקציב ולאישור שלך</h4><p>השלב: " + esc(ap.stage_he || ap.stage || "") + " · הערכה: $" + Number(ap.usd || 0).toFixed(3) +
          (ap.tokens ? " · כ־" + ap.tokens + " טוקנים" : "") + (ap.images ? " · " + ap.images + " תמונות" : "") + "</p>" +
          '<div class="lb-row"><label class="lb-field">תקציב לכל הקרוסלה בדולרים<input class="lb-input" id="ccBudget" inputmode="decimal" dir="ltr" value="' + (Math.ceil(((run.spent_usd || 0) + Number(ap.usd || 0)) * 100) / 100).toFixed(2) + '"></label></div>' +
          '<label class="lb-row lb-small"><input type="checkbox" id="ccYes">אני מאשר את התקציב הזה לשלב הזה בלבד</label>' +
          '<div class="lb-row"><button type="button" class="lb-btn" data-act="authorize" data-key="' + esc(run.key) + '">לאשר ולהמשיך</button></div></div>';
      }
      if (run.status === "done") h += '<div class="lb-row">' + (run.zip ? '<a class="lb-btn secondary sm" href="' + esc(run.zip) + '" download>' + ic("download") + "ZIP</a>" : "") +
        '<button type="button" class="lb-btn secondary sm" data-act="reveal" data-key="' + esc(run.key) + '">' + ic("folder") + "להראות ב-Finder</button>" +
        (run.contact_sheet ? '<a class="lb-btn ghost sm" href="' + esc(run.contact_sheet) + '" target="_blank">דף מגע</a>' : "") +
        '<button type="button" class="lb-btn ghost sm" data-act="produce" data-key="' + esc(run.key) + '">ייצוא מחדש אחרי עריכה</button></div>';
      if (run.status === "failed") h += '<div class="lb-row"><button type="button" class="lb-btn sm" data-act="produce" data-key="' + esc(run.key) + '">לנסות שוב</button></div>';
      return h;
    }
    var b = o.budget || {}, cost = b && b.budget_usd ? Number(b.budget_usd) : 0;
    h += '<div class="cc-box"><h4>' + ic("play") + "להפיק את האפשרות שנבחרה</h4><p>" + (p.kind === "test" ? (cost ? "יש בה תמונות להכין: עד $" + cost.toFixed(2) + ". הלחיצה היא האישור לתקציב הזה ולקרוסלה הזאת בלבד." : "בלי תמונות להכין, בלי עלות: שקופיות, טקסטים ו-ZIP.") :
      "מכונת הקרוסלות עוצרת לפני כל שלב שעולה כסף ומחכה לתקציב ולאישור שלך.") + "</p>" +
      '<div class="lb-row"><button type="button" class="lb-btn" data-act="produce" data-key="' + esc(p.picked) + '" data-cost="' + cost + '">' + (cost ? "להפיק · עד $" + cost.toFixed(2) : "להפיק עכשיו") + "</button></div></div>";
    return h;
  }
  function paneMakeReel(p, d) {
    var r = d.reel, m = d.media || {}, hk = d.hooks || {}, appr = d.approval || {}, h = "", job = reelJob(d.rkey);
    if (d.blockers && d.blockers.length) h += '<div class="cc-box is-warn"><h4>' + ic("info") + "חסר</h4><p translate=\"no\">" + esc(d.blockers.join(" · ")) + "</p></div>";
    if (d.yarin_films && d.yarin_films.length) h += '<div class="cc-box"><h4>' + ic("film") + "מה אתה מצלם</h4><p translate=\"no\">" + esc(d.yarin_films.join(" · ")) + "</p></div>";
    // the main version
    h += '<div class="cc-box"><h4>' + ic("clapper") + "הגרסה הראשית</h4>";
    if (m.final) {   /* the reel itself is beside the list, not here again */
      h += '<div class="cc-finals" id="ccFinals"></div>';
      h += appr.main ? '<div class="lb-row"><span class="lb-chip success">אושרה</span><button type="button" class="lb-btn ghost sm" data-act="unapprove">לבטל את האישור</button></div>'
        : '<div class="lb-row"><button type="button" class="lb-btn ok" data-act="approve-main">לאשר את הגרסה הראשית</button></div>';
    } else h += "<p>עוד לא נוצרה. " + (hk.picked == null && p.status === "hook" ? "קודם בוחרים הוק." : "מעלים קבצים ולוחצים ליצור את הריל.") + "</p>";
    h += "</div>";
    // files and the make job: the reel calendar's make sheet (tiles with ✕, a drop zone, the composer); files dropped anywhere
    // on the open reel go in too
    var proj = d.project ? String(d.project).split("/").pop() : "";
    h += '<div class="cc-box cc-mk"><h4>' + ic("upload") + 'קבצים לריל <span class="cc-note" id="ccFilesN"></span></h4><ul class="lb-files" id="ccFiles">' + tilesHtml(d.rkey) + "</ul>" +
      '<label class="lb-drop" id="ccDrop">' + ic("upload") + '<span class="lb-drop-t">גוררים לכאן סרטונים, הקלטות ותמונות, או לוחצים לבחירה</span>' +
      '<span class="lb-drop-s">הכול נשמר בתיקיית הריל' + (proj ? ' <bdi dir="ltr" translate="no">' + esc(proj) + "</bdi>" : "") + '</span><input type="file" multiple id="ccFileIn"></label>';
    if (job && (job.status === "queued" || job.status === "running")) h += '<p><span class="lb-spinner"></span> ' + esc((job.steps ? "שלב " + job.steps + ": " : "") + (job.step || "בתור")) + "</p>";
    else if (hk.picked == null && !(p.status === "film" || p.status === "produce" || p.status === "approve" || p.status === "ready")) h += "<p>יצירת הריל נפתחת אחרי שבוחרים הוק.</p>";
    else h += '<div class="lb-composer"><label class="lb-composer-label" for="ccMakeAsk">מה לעשות עם החומרים? (לא חובה)</label>' +
      '<textarea class="lb-editable" dir="rtl" id="ccMakeAsk" placeholder="למשל: הטייק השני לפתיחה, לחתוך את השתיקות, ההקלטה מהבוקר לקריינות"></textarea>' +
      '<div class="lb-composer-bar"><span class="lb-composer-note" translate="no">' + esc(proj) + '</span><button type="button" class="lb-btn sm" data-act="make" title="⌘ Enter">' + (m.final ? "ליצור שוב" : "ליצור את הריל") + "</button></div></div>" +
      (job && job.status === "failed" ? '<p class="cc-note cc-err">' + esc(job.error || job.code || "נכשל") + "</p>" : "");
    h += "</div>";
    // GPT pictures, under Yarin's budget
    var g = d.gpt || {}, gt = taskFor("gpt", r);
    if ((g.images || []).length && !(d.gpt_state || {}).done) {
      var est = g.images.reduce(function (a, x) { return a + (x.estimate_usd || 0); }, 0);
      h += '<div class="cc-box is-warn"><h4>' + ic("wallet") + "תמונות GPT מצחיקות</h4><p>" + g.images.length + " תמונות, הערכה $" + est.toFixed(3) + ", תקציב מוצע $" + Number(g.budget_usd || 0).toFixed(2) + ".</p>" +
        '<ol class="cc-note">' + g.images.map(function (x) { return "<li>" + esc(x.scene) + " · $" + Number(x.estimate_usd || 0).toFixed(4) + "</li>"; }).join("") + "</ol>" +
        (gt && gt.status === "running" ? '<p><span class="lb-spinner"></span> מייצר…</p>' :
          '<div class="lb-row"><label class="lb-field">תקציב בדולרים<input class="lb-input" id="ccGptBudget" inputmode="decimal" dir="ltr" value="' + Number(g.budget_usd || 0).toFixed(2) + '"></label></div>' +
          '<label class="lb-row lb-small"><input type="checkbox" id="ccGptYes">אני מאשר לייצר את התמונות האלה עד התקציב הזה</label><div class="lb-row"><button type="button" class="lb-btn" data-act="gpt">לייצר את התמונות</button></div>') +
        (gt && gt.status === "failed" ? '<p class="cc-note">' + esc(gt.tail || "") + "</p>" : "") + "</div>";
    }
    // trial versions: only after the main version and the trial hooks were approved
    var tt = taskFor("trials", r), nTrial = (hk.trial || []).length;
    h += '<div class="cc-box"><h4>' + ic("layers") + "גרסאות ניסיון (אינסטגרם בלבד)</h4>";
    if (!appr.main) h += "<p>נפתח אחרי שמאשרים את הגרסה הראשית.</p>";
    else if (nTrial !== 4) h += '<p>לסמן בהוקים 4 הוקים לגרסאות הניסיון (מסומנים ' + nTrial + ").</p>";
    else if (tt && tt.status === "running") h += '<p><span class="lb-spinner"></span> יוצר ' + nTrial + " גרסאות…</p>";
    else h += '<div class="lb-row"><button type="button" class="lb-btn" data-act="trials">ליצור 5 גרסאות ניסיון</button></div>';
    (m.trials || []).forEach(function (u) { h += '<video class="cc-video" src="' + esc(u) + '" controls preload="metadata"></video>'; });
    return h + "</div>";
  }

  function panePublish(p, it) {
    var pz = p.postiz, h = '<dl class="cc-kv"><dt>ערוצים</dt><dd>' + (p.kind === "reel" ? "הגרסה הראשית: אינסטגרם ופייסבוק · גרסאות הניסיון: אינסטגרם בלבד" : "אינסטגרם ופייסבוק") + "</dd>";
    if (pz) {
      var t = pz.date ? new Date(pz.date) : null;
      h += "<dt>בפוסטיז</dt><dd>" + esc({ schedule: "מתוזמן", published: "עלה", draft: "טיוטה", gone: "לא נמצא בפוסטיז", error: "שגיאה" }[pz.status] || pz.status || "") +
        (t ? " · " + full(iso(t)) + " " + String(t.getHours()).padStart(2, "0") + ":" + String(t.getMinutes()).padStart(2, "0") : "") + "</dd>";
      (pz.live || []).forEach(function (l) { h += "<dt>" + (l.channel === "ig" ? "אינסטגרם" : "פייסבוק") + "</dt><dd>" + esc(l.state || "") + (l.url ? ' · <a href="' + esc(l.url) + '" target="_blank" rel="noopener">לפוסט</a>' : "") + "</dd>"; });
    }
    h += "</dl>";
    if (p.kind === "post") return h + '<p class="cc-note">פוסט שנמצא בפוסטיז ולא שייך לאף קרוסלה כאן.</p>';
    if (p.kind === "reel") return reelPublish(p, h);
    var run = (p.detail || {}).run;
    if (!run || run.status !== "done") return h + '<p class="lb-small lb-muted">התזמון נפתח כשהקרוסלה מוכנה.</p>';
    if (pz && pz.status === "schedule") return h + '<div class="cc-box"><p>כבר מתוזמנת. שינוי בפוסטיז רק באישור שלך באותו רגע, מתוך פוסטיז או בבקשה ל-Claude.</p><div class="lb-row"><a class="lb-btn secondary sm" href="https://platform.postiz.com/launches" target="_blank" rel="noopener">' + ic("open-out") + "לפתוח את פוסטיז</a></div></div>";
    var dt = p.date >= today() ? p.date : today();
    h += '<div class="cc-box"><h4>' + ic("send") + 'לתזמן בפוסטיז</h4><div class="lb-row"><label class="lb-field">תאריך<input class="lb-input" type="date" id="ccPzD" value="' + dt + '"></label>' +
      '<label class="lb-field">שעה<input class="lb-input" type="time" id="ccPzT" value="' + (p.time || "06:00") + '"></label></div>' +
      '<div class="lb-row"><button type="button" class="lb-btn" data-act="postiz" data-key="' + esc(run.key) + '">לתזמן באינסטגרם ובפייסבוק</button><button type="button" class="lb-btn secondary" data-act="postiz-draft" data-key="' + esc(run.key) + '">טיוטה בלבד</button></div>' +
      '<p class="cc-note" id="ccPzNote"></p></div><div class="cc-box"><h4>' + ic("eye") + 'איך זה ייראה</h4><div id="ccPzPrev"><button type="button" class="lb-btn secondary sm" data-act="pzprev" data-key="' + esc(run.key) + '">להציג</button></div></div>';
    return h;
  }

  function sentLine(rec) {
    if (!rec) return "";
    var t = rec.date ? new Date(rec.date) : null;
    return (rec.status === "draft" ? "טיוטה" : "מתוזמן") + (t ? " · " + full(iso(t)) + " " + String(t.getHours()).padStart(2, "0") + ":" + String(t.getMinutes()).padStart(2, "0") : "");
  }
  function reelPublish(p, h) {
    var d = p.detail, m = d.media || {}, appr = d.approval || {}, sent = d.pz_sent || {}, txt = d.pz_text || {};
    var dt = p.date >= today() ? p.date : today(), nTrials = (m.trials || []).length, doneTr = Object.keys(sent.trials || {}).length;
    if (sent.main) h += '<div class="cc-box"><h4>' + ic("check-circle") + "הריל הראשי בפוסטיז (אינסטגרם ופייסבוק)</h4><p>" + esc(sentLine(sent.main)) + "</p></div>";
    else if (!m.final) h += '<div class="cc-box"><h4>' + ic("clapper") + "הריל הראשי</h4><p>עוד אין קובץ מוכן. אחרי שיוצרים ומאשרים אותו אפשר לתזמן.</p></div>";
    else if (!appr.main) h += '<div class="cc-box"><h4>' + ic("clapper") + "הריל הראשי</h4><p>קודם לאשר אותו בהפקה.</p></div>";
    else h += '<div class="cc-box"><h4>' + ic("send") + 'הריל הראשי: אינסטגרם ופייסבוק</h4><div class="lb-row"><label class="lb-field">תאריך<input class="lb-input" type="date" id="ccPzD" value="' + dt + '"></label>' +
      '<label class="lb-field">שעה<input class="lb-input" type="time" id="ccPzT" value="' + (p.time || "21:30") + '"></label></div>' +
      '<p class="cc-note">לאינסטגרם עולה הכיתוב שלמעלה, עם ההסתייגות.</p>' +   /* one caption: the one in טקסט (the server adds the disclaimer) */
      '<label class="cc-f"><span>טקסט לפייסבוק</span><textarea class="lb-textarea lb-editable" dir="rtl" id="ccFbT" translate="no">' + esc(txt.fb || "") + "</textarea></label>" +
      '<div class="lb-row"><button type="button" class="lb-btn" data-act="reel-postiz" data-kind="main">לתזמן בשני הערוצים</button><button type="button" class="lb-btn secondary" data-act="reel-postiz" data-kind="main" data-draft="1">טיוטה בלבד</button></div>' +
      '<p class="cc-note" id="ccPzNote"></p></div>';
    if (nTrials) {
      if (doneTr >= nTrials) h += '<div class="cc-box"><h4>' + ic("layers") + "גרסאות ניסיון בפוסטיז (אינסטגרם בלבד)</h4><p>כל " + nTrials + " הגרסאות נשלחו.</p></div>";
      else if (!appr.main) h += '<div class="cc-box"><h4>' + ic("layers") + "גרסאות ניסיון</h4><p>נשלחות אחרי שהגרסה הראשית אושרה.</p></div>";
      else h += '<div class="cc-box"><h4>' + ic("layers") + (nTrials - doneTr) + " גרסאות ניסיון: אינסטגרם בלבד</h4><div class=\"lb-row\"><label class=\"lb-field\">מתחילות בתאריך<input class=\"lb-input\" type=\"date\" id=\"ccTrD\" value=\"" + dt + "\"></label>" +
        '<label class="lb-field">בשעה<input class="lb-input" type="time" id="ccTrT" value="' + (((S.data || {}).hours || {}).trial_start || "11:30") + '"></label></div><p class="cc-note">כל גרסה 5 דקות אחרי הקודמת, כגרסת ניסיון עם הצגה ידנית לפיד.</p>' +
        '<div class="lb-row"><button type="button" class="lb-btn" data-act="reel-postiz" data-kind="trials">לתזמן את גרסאות הניסיון</button></div><p class="cc-note" id="ccTrNote"></p></div>';
    }
    return h;
  }
  var rpArmed = null;
  function reelPostiz(t) {
    var p = S.byId[S.open.piece], kind = t.dataset.kind, draft = !!t.dataset.draft, body = { reel: p.detail.reel, kind: kind, draft: draft, confirmed: true };
    if (kind === "trials") { body.date = ($("#ccTrD") || {}).value; body.time = ($("#ccTrT") || {}).value; }
    else { body.date = ($("#ccPzD") || {}).value; body.time = ($("#ccPzT") || {}).value; body.fb_text = ($("#ccFbT") || {}).value; }
    if (kind === "fb_trial") { body.date = ($("#ccFbD") || {}).value; body.time = ($("#ccFbTm") || {}).value; body.fb_text = ($("#ccFbTx") || {}).value; body.trial_index = +t.dataset.i; body.draft = false; }
    if (!body.date || !body.time) { toast("בחרו תאריך ושעה"); return; }
    var sig = kind + body.date + body.time + draft + (t.dataset.i || ""), note = $(kind === "trials" ? "#ccTrNote" : "#ccPzNote");
    if (rpArmed !== sig) {
      rpArmed = sig;
      var where = kind === "main" ? "באינסטגרם ובפייסבוק" : kind === "trials" ? "באינסטגרם בלבד, כגרסאות ניסיון" : "בפייסבוק בלבד";
      var msg = (draft ? "טיוטה " : "לתזמן ל־" + full(body.date) + " " + body.time + " ") + where + "? לחיצה נוספת שולחת.";
      if (note) note.textContent = msg; else toast(msg);
      t.dataset.label = t.dataset.label || t.textContent; t.textContent = "כן, לשלוח"; return;
    }
    rpArmed = null; t.disabled = true;
    post("/api/calendar/reel-postiz", body).then(function (b) { toast(kind === "trials" ? (b.sent || 0) + " גרסאות נשלחו לפוסטיז" : "נשלח לפוסטיז"); load(true); })
      .catch(function (e) { t.disabled = false; t.textContent = t.dataset.label || "לשלוח"; toast(e.message); });
  }
  function askHtml(p) {
    var j = jobFor(p.id, "ask"), a = S.answers[p.id];
    if (a) {
      return '<div class="cc-ask"><b>' + ic("sparkle") + " " + esc(a.summary || "ההצעה") + '</b><div class="cc-diff">' + (a.changes || []).map(function (c) {
        var f = String(c.field).split("__"), n = f[1] != null && f[1] !== "" ? " " + (+f[1] + 1) : "";
        return "<div><span class=\"cc-note\">" + esc((FIELD_HE[f[0]] || c.field) + n + (c.slide ? " · שקופית " + c.slide : "")) + '</span><del translate="no">' + esc(c.before || "") + '</del><ins translate="no">' + esc(c.value) + "</ins></div>";
      }).join("") + '</div><div class="lb-row"><button type="button" class="lb-btn" data-act="ask-apply">להחיל</button><button type="button" class="lb-btn secondary" data-act="ask-drop">לבטל</button></div></div>';
    }
    /* the reel calendar's comment box: a composer, and for a reel רעיון חדש (a different idea for the same day, same series) */
    var reel = p.kind === "reel";
    return '<div class="cc-ask"><div class="lb-composer"><label class="lb-composer-label" for="ccAskT">' + (reel ? "הערה לשינוי הריל" : "מה לשנות? במילים שלך") + "</label>" +
      '<textarea class="lb-editable" dir="rtl" id="ccAskT" rows="1" placeholder="' + (reel ? "מה לשנות? למשל: כותרת יותר קצרה, פתיחה אחרת, שורה 3 בלי המילה מתנה" : "למשל: שהפתיח ידבר לסבתא, או משפט אחד קצר יותר בשקופית 3") + '"' + (j ? " disabled" : "") + "></textarea>" +
      '<div class="lb-composer-bar">' + (false ? '<button type="button" class="lb-btn secondary sm" data-act="idea" title="רעיון אחר לגמרי לאותו יום, באותה סדרה"' + (j ? " disabled" : "") + ">" + ic("sparkle") + "רעיון חדש</button>" : "") +
      '<span class="lb-composer-note">' + (j ? '<span class="lb-spinner" aria-hidden="true"></span> ' + (j.comment === "רעיון חדש" ? "כותב רעיון חדש…" : "עובד על ההערה…") : "") + "</span>" +
      '<button type="button" class="lb-btn sm" data-act="ask" title="⌘ Enter"' + (j ? " disabled" : "") + ">שליחה</button></div></div></div>";
  }

  function afterPiece(p) {
    var d = p.detail || {};
    if (p.kind === "story") { if (window.CCStory) CCStory.after(p); return; }
    if (p.kind === "season") { if (window.CCSeason) CCSeason.after(p); return; }
    if (p.kind === "reel") { wireTiles(); loadFiles(d.rkey); }
    $$("#ccDlgB textarea[data-f]").forEach(function (t) { t.dataset.v = t.value; });
    var j = S.jobs.find(function (x) { return x.reel === p.id && x.kind === "ask" && x.status === "done" && !x.claimed; });
    if (j && !S.answers[p.id]) claimAsk(j, p);
  }

  /* ---------- writes ---------- */
  function setSave(state, text) { var s = $("#ccSave"); if (!s) return; s.className = "lb-savestate" + (state ? " is-" + state : ""); s.textContent = text; }
  function saveField(p, key, value) {
    var it = itemOf(p), d = p.detail || {};
    setSave("wait", "שומר…");
    var done = function (b) {
      if (b && (b.errors || []).length) setSave("error", "נשמר, עם שגיאה: " + b.errors[0].message);
      else setSave("", "נשמר");
      load(true);
    }, fail = function (e) { setSave("error", "לא נשמר: " + e.message); toast("השמירה נכשלה", "לנסות שוב", function () { saveField(p, key, value); }); };
    if (p.kind === "reel") {
      var ek = d.rkey + "__" + key;
      return put("/api/reels-hub/doc?path=edits/" + encodeURIComponent(ek), { key: ek, text: value, at: nowIso() })
        .then(function () { return post("/api/calendar/reel-merge", { reel: d.reel }); })
        .then(function (b) {
          var l = $("#ccLint"); if (l) l.innerHTML = (b.lint || []).map(function (x) { return '<div class="e">' + esc(x) + "</div>"; }).join("");
          setSave(b.lint && b.lint.length ? "error" : "", b.lint && b.lint.length ? "נשמר, יש הערות בבדיקה" : "נשמר ונבדק"); load(true);
        }).catch(fail);
    }
    var parts = key.split("@"), f = parts[0], n = parts[1] ? +parts[1] : null;
    if (p.kind === "test") return post("/api/save-test", { key: it.key, edits: [{ field: f, slide: n, value: value }] }).then(done).catch(fail);
    if (p.kind === "kid") return post("/api/save", { date: d.pack_date, edits: [{ option: it.id, field: f, slide: n, value: value }] }).then(done).catch(fail);
  }
  function applyEdits(p, changes) {
    var it = itemOf(p), d = p.detail || {};
    if (p.kind === "reel") {
      return changes.reduce(function (pr, c) {
        var ek = d.rkey + "__" + c.field;
        return pr.then(function () { return put("/api/reels-hub/doc?path=edits/" + encodeURIComponent(ek), { key: ek, text: c.value, at: nowIso() }); });
      }, Promise.resolve()).then(function () { return post("/api/calendar/reel-merge", { reel: d.reel }); });
    }
    var edits = changes.map(function (c) { return p.kind === "kid" ? { option: it.id, field: c.field, slide: c.slide || null, value: c.value } : { field: c.field, slide: c.slide || null, value: c.value }; });
    return p.kind === "test" ? post("/api/save-test", { key: it.key, edits: edits }) : post("/api/save", { date: d.pack_date, edits: edits });
  }

  function pick(p, key) {
    var batch = p.kind === "test" ? "test-2026-11" : (p.detail || {}).batch;
    var reqs = (p.options || []).map(function (o) { return post("/api/grade", { batch: batch, key: o.key, produce: o.key === key }); });
    Promise.all(reqs).then(function () { toast("נבחרה"); load(true); }).catch(function (e) { toast("לא נשמר: " + e.message); });
  }

  function moveTo(p, ds, tm) {
    if (!p || (p.date === ds && (!tm || tm === p.time))) return;
    if (p.postiz && p.postiz.status === "schedule") { toast("מתוזמן בפוסטיז: לשנות שם? מכאן לא משנים פוסט שכבר בפוסטיז."); return; }
    var where = dayName(ds) + " " + ddmm(ds) + (tm ? " " + tm : "");
    if (p.kind === "idea") {
      var old = { date: p.date, time: p.time }, key = p.id.slice(2), idea = Object.assign({}, p.detail.idea, { date: ds });
      if (tm) idea.time = tm;
      return put("/api/calendar/doc?path=ideas/" + key, idea).then(function () { load(true); toast("הועבר ל-" + where, "ביטול", function () { put("/api/calendar/doc?path=ideas/" + key, Object.assign({}, idea, { date: old.date, time: old.time || null })).then(function () { load(true); }); }); });
    }
    var body = { id: p.id, date: ds }; if (tm) body.time = tm;
    post("/api/calendar/move", body).then(function (b) {
      load(true);
      toast("הועבר ל-" + where, "ביטול", function () {
        var u = b.undo || {};
        var back = p.kind === "reel" ? post("/api/calendar/move", { id: p.id, date: u.date, time: u.time || null })
          : u.date ? post("/api/calendar/move", { id: u.id || p.id, date: u.date, time: u.time || null }) : put("/api/calendar/doc?path=moves/" + p.id, { _delete: true });
        back.then(function () { load(true); toast("בוטל"); });
      });
    }).catch(function (e) { toast(e.message); });
  }

  /* ---------- background asks: 5 hooks, the prompt box, new ideas ---------- */
  var RULES = "Rules for the Hebrew: everyday Israeli Hebrew, warm and plain, like a mom talking, not like an ad. No dash of any kind (no em dash, no en dash, no hyphen, no maqaf), no semicolon. " +
    "Write the brand only as לומיבוק, exactly that spelling. Never write \"תצוגה מקדימה\" (preview): say how simple it is instead, \"בוחרים סיפור, מוסיפים תמונה של הילד, ובום, יש ספר\". Never mention AI. Never a price, a discount, a sale or delivery cost. Never language options or a digital copy. Yarin (LumeBook's marketing guy) is not a parent: never \"הילד שלי\" in LumeBook's voice. Never \"קוד הנחה\" or \"קוד אישי\".";
  function pieceContext(p, it) {
    var d = p.detail || {};
    if (p.kind === "reel") return { kind: "reel (Instagram, 10 to 30 seconds, Yarin's voiceover)", series: d.series_he, structure: d.texts.structure, hook: d.texts.hook, lines: d.texts.vo, sees: d.texts.sees, payoff: d.texts.payoff, shot: d.texts.shot, caption: d.texts.caption };
    if (p.kind === "idea") return { kind: "new " + (p.subtype === "reel" ? "reel" : "carousel"), brief: (d.idea || {}).brief, date: p.date };
    var c = { kind: p.kind === "test" ? "test carousel (" + p.subtype_he + "), feminine singular to one " + ((it && it.addressee_he) || "mom") : "child-voice carousel: the child talks to the parents (mom, or both parents), never dad alone", title: it && it.title };
    if (it) { c.slides = (it.slides || []).map(function (s, i) { var o = { slide: i + 1 }; Object.keys(s).forEach(function (k) { if (typeof s[k] === "string" && /[א-ת]/.test(s[k])) o[k] = s[k]; }); return o; }); c.caption = it.caption; c.cta = it.cta; if (it.fb_text) c.fb_text = it.fb_text; }
    return c;
  }
  function startJob(p, kind, prompt, label, comment) {
    return post("/api/calendar/jobs", { piece: p.id, kind: kind, prompt: prompt, label: label || "", comment: comment || "" }).then(function (b) {
      S.jobs.push(b.job); pollJobs(true); renderDrawer();
    }).catch(function (e) { toast(e.status === 409 ? "כבר יש בקשה שרצה לפריט הזה" : "הבקשה לא נשלחה: " + e.message); });
  }
  function askHooks(p) {
    var it = itemOf(p), cur = currentHook(p, it);
    var prompt = "You write hooks for LumeBook (personalised children's books with the child's name and face, Israel) for Instagram and Facebook. Write 5 different hooks in Hebrew for the " +
      (p.kind === "reel" ? "opening line and on-screen text of this reel" : p.kind === "idea" ? "post this new content idea will become" : "cover (slide 1) of this carousel") +
      ". Each hook stops a scrolling mom or grandmother in under two seconds: a real moment, a thought she has, a quoted line, or a number. Make the five clearly different from each other and from the current one. Up to 12 words each; a line break is allowed. " +
      RULES + "\n\nThe piece:\n" + JSON.stringify(pieceContext(p, it), null, 1) + (cur ? "\n\nCurrent hook: " + cur : "") +
      '\n\nAnswer with JSON only: {"hooks": ["...", "...", "...", "...", "..."]}';
    startJob(p, "hooks", prompt, hookKey(p));
  }
  function reelRules(p) {   /* the reel calendar's rules for its asks (build_page.py prompt and ideaPrompt) */
    var R = rcfg(), d = p.detail || {};
    return "Reel rules: the hook (the text at the top, also the first second) up to 8 words. The spoken lines together between " + (R.vo_min || 17) + " and " + (R.vo_max || 72) +
      " words, one thought a line, up to 12 words a line; the whole reel 10 to 30 seconds. " +
      (d.own_cta ? "The last spoken lines are Yarin's own closing ask (לומי in the comments): keep that ask. " : "The closing spoken line is fixed and added on its own (\"" + (R.cta_voice || "") + "\"): never write it in the lines. ") +
      "The caption always ends with this line, word for word: " + (R.cta_caption || "") + ". If the caption ends with a medical disclaimer, keep it exactly. " +
      "\"sees__N\", \"payoff\" and \"shot\" are internal notes for Yarin in plain Hebrew, second person (אתה), and \"sees__N\" stays matched to spoken line N. " +
      "No new facts; times and features only from these: " + (R.facts || "") + ". Never talk about the book's languages or a digital copy. Keep the same number of lines; every value non-empty.";
  }
  function askIdea(p) {   /* רעיון חדש: a completely different reel for the same day and series, every field rewritten */
    var d = p.detail || {}, n = (d.texts.vo || []).length, keys = ["hook"], i;
    for (i = 0; i < n; i++) keys.push("vo__" + i);
    for (i = 0; i < n; i++) keys.push("sees__" + i);
    keys.push("payoff", "shot", "caption");
    var others = S.all.filter(function (x) { return x.kind === "reel" && x.id !== p.id; }).map(function (x) { return x.title; }).filter(Boolean);
    var prompt = "You write a new reel for LumeBook's Instagram (personalised children's books with the child's name and face, Israel). Yarin, LumeBook's social media manager, did not like this reel's idea and wants a completely different one for the same day. " +
      "Series: " + (d.series_he || "") + ". Day: " + p.date + ". Keep the series, but a different angle, opening and structure; do not reword the old idea. Ideas of the month's other reels, do not repeat them: " + others.join(" | ") + ". " +
      "Yarin is in the reel: a talking clip to the camera and/or his voice over. No actors, no children who are strangers, no app trends. What he can film alone and cheaply: himself to the camera, a screen recording of the site and the order, the printed book, a book preview, a top shot, a phone recording. " +
      RULES + " " + reelRules(p) + "\n\nThe reel now:\n" + JSON.stringify(pieceContext(p), null, 1) +
      "\n\nReturn a new value for every one of these fields, and only these: " + keys.join(", ") + '.\nAnswer with JSON only: {"summary": "one short Hebrew sentence: the new idea", "changes": [{"field": "...", "value": "the new full text of that field"}]}';
    startJob(p, "ask", prompt, p.id, "רעיון חדש");
  }
  function askChange(p, text) {
    var it = itemOf(p);
    var fields = p.kind === "reel" ? 'field is one of "hook", "vo__N" (spoken line N from 0), "sees__N", "payoff", "shot", "caption". ' + reelRules(p) :
      p.kind === "test" ? 'field is one of "big", "headline", "body", "label", "no", "yes", "why" (with "slide": the slide number) or "caption", "cta", "fb_text", "title" (no slide)' :
        'field is "headline" or "body" (with "slide") or "caption", "cta", "title" (no slide); the last slide is only the CTA';
    var prompt = "You edit a LumeBook social post (Hebrew, RTL). Yarin asks, in his words: \"" + text + "\". Change only what he asks for, keep everything else word for word. " + RULES +
      "\n\nThe post now:\n" + JSON.stringify(pieceContext(p, it), null, 1) + "\n\nAnswer with JSON only: {\"summary\": \"one short Hebrew sentence of what you changed\", \"changes\": [{\"field\": \"...\", \"slide\": 1, \"value\": \"the new full text of that field\"}]}; " + fields + ".";
    startJob(p, "ask", prompt, it ? it.key : p.id, text);
  }
  function parseJson(t) { t = String(t || "").replace(/^\s*```(?:json)?\s*|\s*```\s*$/g, ""); var a = t.indexOf("{"), b = t.lastIndexOf("}"); return JSON.parse(a >= 0 ? t.slice(a, b + 1) : t); }
  function currentValue(p, c) {
    var it = itemOf(p), d = p.detail || {};
    if (p.kind === "reel") { var tx = d.texts || {}, k = String(c.field).split("__"); return k[0] === "vo" || k[0] === "sees" ? (tx[k[0]] || [])[+k[1]] || "" : tx[k[0]] || ""; }
    if (!it) return "";
    if (c.slide) return ((it.slides || [])[c.slide - 1] || {})[c.field] || "";
    return it[c.field] || "";
  }
  /* an answer is picked up once: the job poll and every redraw of the panel both try, and the poll replaces the job objects, so the
     guard is the job's id (a second claim used to come back 409); a failed call frees it to be tried again */
  var claiming = {};
  function claimAsk(j, p) {
    if (claiming[j.id]) return;
    claiming[j.id] = 1;
    post("/api/calendar/jobs/" + j.id + "/claim", {}).catch(function (e) { if (e.status !== 409) delete claiming[j.id]; throw e; }).then(function (b) {
      var res; try { res = parseJson(b.job.text); } catch (x) { toast("התשובה לא הייתה בפורמט הנכון"); return; }
      if (res.changes && !Array.isArray(res.changes)) res.changes = Object.keys(res.changes).map(function (k) { return { field: k, value: res.changes[k] }; });   /* the reel calendar's shape */
      if (p.kind === "reel") {   /* only the reel's own fields, never empty, and the house punctuation (the reel calendar's tidy) */
        var n = (p.detail.texts.vo || []).length;
        res.changes = (res.changes || []).filter(function (c) {
          var f = String(c.field || "").split("__");
          return typeof c.value === "string" && c.value.trim() && (["hook", "payoff", "shot", "caption"].indexOf(c.field) >= 0 || ((f[0] === "vo" || f[0] === "sees") && /^\d+$/.test(f[1] || "") && +f[1] < n));
        }).map(function (c) {
          c.value = c.value.replace(/\s*[\u2014\u2013]\s*/g, ", ").replace(/\u05BE/g, " ").replace(/(\S)\s+-\s+(\S)/g, "$1, $2").replace(/;/g, ",").replace(/לומבוק/g, "לומיבוק").replace(/,\s*,/g, ",").trim();
          return c;
        });
      }
      (res.changes || []).forEach(function (c) { c.before = currentValue(p, c); });
      res.changes = (res.changes || []).filter(function (c) { return c.value !== c.before; });
      if (!res.changes.length) { toast(res.summary ? "לא שונה כלום: " + res.summary : "לא שונה כלום"); return; }
      S.answers[p.id] = res; renderDrawer();
    }).catch(function () {});
  }
  function finishJob(j) {
    if (j.kind === "ask") { var p = S.byId[j.reel]; if (S.open && S.open.piece === j.reel && p) claimAsk(j, p); else if (p && !S.answers[p.id]) renderView(); return; }
    post("/api/calendar/jobs/" + j.id + "/claim", {}).then(function (b) {
      var res; try { res = parseJson(b.job.text); } catch (x) { toast("התשובה לא הייתה בפורמט הנכון"); return; }
      if (j.kind === "hooks") {
        var hooks = (res.hooks || []).map(String).filter(Boolean).slice(0, 5);
        if (hooks.length < 2) { toast("לא התקבלו הוקים. אפשר לבקש שוב."); return; }
        return put("/api/calendar/doc?path=hooks/" + encodeURIComponent(j.label), { options: hooks, picked: null, trial: [] }).then(function () { toast("5 הוקים מוכנים"); load(true); });
      }
      if (j.kind === "idea") {
        var key = j.reel.slice(2), p2 = S.byId[j.reel], idea = Object.assign({}, (p2 && p2.detail.idea) || {}, { title: res.title || "", brief: res.brief || ((p2 && p2.detail.idea) || {}).brief || "" });
        return put("/api/calendar/doc?path=ideas/" + key, idea).then(function () {
          return put("/api/calendar/doc?path=hooks/" + encodeURIComponent(j.reel), { options: (res.hooks || []).slice(0, 5), picked: null, trial: [] });
        }).then(function () { toast("הרעיון מוכן, עם 5 הוקים"); load(true); });
      }
    }).catch(function () {});
  }
  var jobT, seenDone = {}, jobSig = "";
  function calm() {   /* never redraw the drawer under a field being typed in or a video that plays */
    var a = document.activeElement;
    if (a && a.matches && a.matches("textarea,input") && a.closest("#ccDlg")) return false;
    return !$$("#ccDlgB video").some(function (v) { return !v.paused; });
  }
  function pollJobs(soon) {
    clearTimeout(jobT);
    api("/api/calendar/jobs").then(function (b) {
      S.jobs = b.jobs || []; S.tasks = b.tasks || []; S.reelJobs = b.reel_jobs || [];
      S.jobs.forEach(function (j) { if (j.status === "done" && !j.claimed && !seenDone[j.id]) { seenDone[j.id] = 1; finishJob(j); } });
      var busy = S.jobs.some(function (j) { return j.status === "queued" || j.status === "running"; }) || S.tasks.some(function (t) { return t.status === "running"; }) ||
        S.reelJobs.some(function (j) { return j.status === "queued" || j.status === "running"; });
      var sig = JSON.stringify([S.jobs.map(function (j) { return [j.id, j.status, j.step, j.claimed]; }), S.tasks.map(function (t) { return [t.id, t.status]; }),
        S.reelJobs.map(function (j) { return [j.id, j.status, j.steps]; })]);
      if (sig !== jobSig) { jobSig = sig; if (S.open && S.open.piece && calm()) renderDrawer(); }
      jobT = setTimeout(pollJobs, busy ? 3000 : 15000);
    }).catch(function () { jobT = setTimeout(pollJobs, 20000); });
  }

  /* the reel's files as the reel calendar's tiles (lb-files): a frame or the picture, the name, the size, ✕ to move one to
     _to-delete; files being uploaded show as tiles with a bar */
  var FILES = {}, UPS = {}, upSeq = 0, upBusy = false;
  var KIND_HE = { video: "סרטון", image: "תמונה", audio: "הקלטה", file: "קובץ" }, KIND_IC = { video: "film", image: "image", audio: "audio", file: "file" };
  var OKX = /\.(mp4|mov|m4v|webm|mkv|png|jpe?g|webp|gif|heic|mp3|m4a|wav|ogg|opus|aac|pdf)$/i;
  function kindOf(n) {
    var x = String(n).split(".").pop().toLowerCase();
    return /^(mp4|mov|m4v|webm|mkv)$/.test(x) ? "video" : /^(png|jpe?g|webp|gif|heic)$/.test(x) ? "image" : /^(mp3|m4a|wav|ogg|opus|aac)$/.test(x) ? "audio" : "file";
  }
  function fsize(b) { return b >= 1e9 ? (b / 1e9).toFixed(1) + " GB" : b >= 1e6 ? Math.round(b / 1e6) + " MB" : Math.max(1, Math.round(b / 1e3)) + " KB"; }
  function tileHtml(f) {
    var k = f.kind || kindOf(f.name), src = f.url || "", th;
    if (!f.up && src && k === "image") th = '<a class="lb-file-th" href="' + esc(src) + '" target="_blank" rel="noopener" tabindex="-1"><img src="' + esc(src) + '" alt="" loading="lazy"></a>';
    else if (!f.up && src && k === "video") th = '<a class="lb-file-th" href="' + esc(src) + '" target="_blank" rel="noopener" tabindex="-1"><video src="' + esc(src) + '#t=0.3" muted playsinline preload="metadata"></video><span class="lb-file-dur"></span></a>';
    else th = '<span class="lb-file-th">' + ic(KIND_IC[k] || "file") + "</span>";
    return '<li class="lb-file' + (f.up ? " is-up" : "") + '" ' + (f.up ? 'data-up="' + f.id + '"' : 'data-rf="' + esc(f.path) + '"') + ' style="--p:' + (f.p || 0).toFixed(3) + '">' + th +
      '<button type="button" class="lb-file-x" data-act="file-x" aria-label="' + (f.up ? "ביטול ההעלאה של " : "הסרה של ") + esc(f.name) + '">' + ic("close") + "</button>" +
      '<span class="lb-file-meta"><span class="lb-file-n" dir="ltr" translate="no" title="' + esc(f.name) + '">' + esc(f.name) + '</span><span class="lb-file-s">' + (f.up ? "מעלה, " : (KIND_HE[k] || "קובץ") + ", ") + fsize(f.size || 0) + "</span></span>" +
      '<span class="lb-file-bar"><i></i></span></li>';
  }
  function tilesHtml(rkey) {
    var b = FILES[rkey] || { files: [] }, ups = Object.keys(UPS).map(function (k) { return UPS[k]; }).filter(function (u) { return u.rkey === rkey; });
    return (b.files || []).concat(ups).map(tileHtml).join("");
  }
  function wireTiles() {   /* a video tile shows its length and plays while the pointer is on it; a picture that fails shows its icon */
    var ul = $("#ccFiles"); if (!ul) return;
    $$("video", ul).forEach(function (v) {
      var li = v.closest(".lb-file");
      v.addEventListener("loadedmetadata", function () { var d = $(".lb-file-dur", li); if (d && isFinite(v.duration)) d.textContent = mmss(v.duration); });
      li.addEventListener("mouseenter", function () { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); });
      li.addEventListener("mouseleave", function () { v.pause(); try { v.currentTime = 0.3; } catch (x) {} });
    });
    $$("img", ul).forEach(function (im) { im.addEventListener("error", function () { var a = im.parentNode; a.outerHTML = '<span class="lb-file-th">' + ic("image") + "</span>"; }); });
  }
  function paintTiles(rkey) {
    var ul = $("#ccFiles"), p = S.open && S.byId[S.open.piece]; if (!ul || !p || p.detail.rkey !== rkey) return;
    ul.innerHTML = tilesHtml(rkey); wireTiles();
    var b = FILES[rkey] || {}, n = (b.files || []).length, fn = $("#ccFilesN"); if (fn) fn.textContent = n ? n + " קבצים" : "אין עדיין קבצים";
    var fl = $("#ccFinals"), older = (b.finals || []).slice(1);
    if (fl) fl.innerHTML = older.length ? '<span class="cc-note">גרסאות קודמות:</span>' + older.map(function (f) {
      return '<a class="lb-chip outline" href="' + esc(f.url) + '" target="_blank" rel="noopener" dir="ltr" translate="no">' + esc(f.name.replace(/\.mp4$/i, "")) + "</a>";
    }).join("") : "";
  }
  function loadFiles(rkey) {
    api("/api/reel-files?reel=" + encodeURIComponent(rkey)).then(function (b) {
      var sig = JSON.stringify([(b.files || []).map(function (f) { return f.path + f.mtime; }), (b.finals || []).map(function (f) { return f.path + f.mtime; })]);
      var was = FILES[rkey] && FILES[rkey]._sig; b._sig = sig; FILES[rkey] = b;
      if (was !== sig || !$("#ccFiles li")) paintTiles(rkey); else { var fn = $("#ccFilesN"); if (fn) fn.textContent = (b.files || []).length ? b.files.length + " קבצים" : "אין עדיין קבצים"; }
    }).catch(function () { var fn = $("#ccFilesN"); if (fn) fn.textContent = "הרשימה לא נטענה"; });
  }
  function upload(rkey, files) {
    var list = Array.prototype.slice.call(files || []), bad = list.filter(function (f) { return !OKX.test(f.name); });
    if (bad.length) toast("לא נכנסו (רק סרטונים, תמונות, הקלטות ו-PDF): " + bad.map(function (f) { return f.name; }).join(", "));
    list = list.filter(function (f) { return OKX.test(f.name); }); if (!list.length) return;
    list.forEach(function (f) { var id = "u" + (++upSeq); UPS[id] = { id: id, rkey: rkey, name: f.name, size: f.size, kind: kindOf(f.name), p: 0, up: true, file: f }; });
    paintTiles(rkey); upNext();
  }
  function upNext() {   /* one file at a time, each with its own bar */
    if (upBusy) return;
    var u = Object.keys(UPS).map(function (k) { return UPS[k]; }).filter(function (x) { return !x.started; })[0]; if (!u) return;
    upBusy = true; u.started = true;
    var x = new XMLHttpRequest(); u.xhr = x;
    x.open("POST", "/api/reel-files?reel=" + encodeURIComponent(u.rkey) + "&name=" + encodeURIComponent(u.name));
    x.setRequestHeader("X-LumeBook-Board", "1"); x.setRequestHeader("Content-Type", "application/octet-stream");
    x.upload.onprogress = function (e) { if (!e.lengthComputable) return; u.p = e.loaded / e.total; var li = $('#ccFiles [data-up="' + u.id + '"]'); if (li) li.style.setProperty("--p", u.p.toFixed(3)); };
    x.onloadend = function () {
      upBusy = false; delete UPS[u.id];
      if (!u.cancelled && !(x.status >= 200 && x.status < 300)) toast("ההעלאה של " + u.name + " נכשלה" + (x.status ? " (" + x.status + ")" : ""));
      var left = Object.keys(UPS).some(function (k) { return UPS[k].rkey === u.rkey; });
      if (!left) { if (!u.cancelled) toast("הקבצים נשמרו בתיקיית הריל"); loadFiles(u.rkey); load(true); } else paintTiles(u.rkey);
      upNext();
    };
    x.send(u.file);
  }
  function removeFile(li) {
    var p = S.open && S.byId[S.open.piece]; if (!p) return;
    var rkey = p.detail.rkey;
    if (li.dataset.up) {
      var u = UPS[li.dataset.up]; if (!u) return;
      if (u.xhr) { u.cancelled = true; u.xhr.abort(); } else { delete UPS[u.id]; paintTiles(rkey); }
      return;
    }
    li.classList.add("is-up");
    post("/api/reel-files/remove?reel=" + encodeURIComponent(rkey) + "&f=" + encodeURIComponent(li.dataset.rf), {})
      .then(function () { toast("הקובץ הועבר ל-_to-delete"); loadFiles(rkey); load(true); })
      .catch(function (e) { li.classList.remove("is-up"); toast("לא הוסר: " + e.message); });
  }
  /* files dragged anywhere over an open reel go into that reel (the reel calendar's veil says which one) */
  function hasFiles(ev) { var t = ev.dataTransfer && ev.dataTransfer.types; return !!t && Array.prototype.indexOf.call(t, "Files") >= 0; }
  function openReel() { var p = S.open && S.open.piece && S.byId[S.open.piece]; return p && p.kind === "reel" ? p : null; }
  var veil = null, fileDragN = 0;
  function veilOn(on) {
    var dz = $("#ccDrop"); if (dz) dz.classList.toggle("is-over", on);
    var p = openReel();
    if (!veil) { veil = document.createElement("div"); veil.className = "lb-drop-veil"; veil.setAttribute("aria-hidden", "true"); veil.innerHTML = ic("upload") + "<span>משחררים, והקבצים נכנסים לריל</span><small translate=\"no\"></small>"; dlg.appendChild(veil); }
    if (!on || !p) { veil.classList.remove("is-on"); return; }
    var r = $(".lb-dialog-card", dlg).getBoundingClientRect(), top = Math.max(r.top, 0) + 8, bot = Math.min(r.bottom, innerHeight) - 8;
    veil.style.left = (r.left + 8) + "px"; veil.style.width = (r.width - 16) + "px"; veil.style.top = top + "px"; veil.style.height = Math.max(96, bot - top) + "px";
    $("small", veil).textContent = "ריל " + p.detail.reel + ": " + (p.title || "");
    veil.classList.add("is-on");
  }

  /* ---------- new idea ---------- */
  function openNew(forKind, ds, tm) {
    var d = $("#ccNew");
    $("#ccNewDate").value = ds || S.sel || today();
    $("#ccNewTime").value = tm || "";
    $$("#ccNewFor button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.for === "carousel")); });
    $("#ccNewBrief").value = ""; $("#ccNewErr").hidden = true;
    d.showModal(); $("#ccNewBrief").focus();
  }
  function submitNew(ev) {
    ev.preventDefault();
    var brief = $("#ccNewBrief").value.trim(), ds = $("#ccNewDate").value, fk = ($("#ccNewFor [aria-pressed=true]") || {}).dataset;
    if (brief.length < 4) { var e = $("#ccNewErr"); e.hidden = false; e.textContent = "כתבו במשפט אחד על מה הפוסט"; return; }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(ds)) { var e2 = $("#ccNewErr"); e2.hidden = false; e2.textContent = "בחרו תאריך"; return; }
    var key = "n" + Date.now().toString(36), forKind = fk ? fk.for : "carousel";
    var idea = { for: forKind, date: ds, time: $("#ccNewTime").value || null, brief: brief, title: brief.slice(0, 60) };
    $("#ccNew").close();
    put("/api/calendar/doc?path=ideas/" + key, idea).then(function () {
      var p = { id: "i-" + key, kind: "idea", subtype: forKind, detail: { idea: idea } };
      var prompt = "A new content idea for LumeBook (personalised children's books with the child's name and face, Israel), a " + (forKind === "reel" ? "reel" : "carousel") + " for Instagram and Facebook on " + ds +
        ". Yarin's brief: \"" + brief + "\". Write a short Hebrew title, a two-sentence Hebrew brief, and 5 different Hebrew hooks. " + RULES +
        '\n\nAnswer with JSON only: {"title": "...", "brief": "...", "hooks": ["...", "...", "...", "...", "..."]}';
      startJob(p, "idea", prompt, "i-" + key);
      load(true); openDay(ds);
    }).catch(function (e2) { toast("לא נשמר: " + e2.message); });
  }

  /* ---------- events ---------- */
  function onClick(ev) {
    var t = ev.target.closest("[data-act],[data-open],[data-day],[data-kind],[data-test],[data-st],[data-sort],[data-v],[data-drafts]");
    if (!t) return;
    var a = t.dataset.act, p = S.open && S.open.piece ? S.byId[S.open.piece] : null;
    if (t.dataset.v && t.closest("#ccViews")) { setView(t.dataset.v); return; }
    if (t.dataset.drafts) { S.drafts = !S.drafts; store("drafts", S.drafts); S.data = null; S.cache = {}; renderAll(); load(true); return; }
    if (t.dataset.kind) { S.kinds[t.dataset.kind] = !(S.kinds[t.dataset.kind] !== false); store("kinds", S.kinds); renderSide(); renderView(); if (S.open) renderDrawer(); return; }
    if (t.dataset.test) { S.tests[t.dataset.test] = !(S.tests[t.dataset.test] !== false); store("tests", S.tests); renderSide(); renderView(); return; }
    if (t.dataset.st && t.closest("#ccSts")) { S.sts[t.dataset.st] = !S.sts[t.dataset.st]; renderSide(); renderView(); return; }
    if (a === "opt") { S.open.opt = +t.dataset.i; renderDrawer(); return; }
    if (a === "optview") { var seg = t.parentNode; $$("button", seg).forEach(function (b) { b.setAttribute("aria-pressed", String(b === t)); }); var pp = S.byId[t.dataset.id]; var pb = seg.parentNode.querySelector('[data-act="pick"]'); if (pb && pp) pb.dataset.key = pp.options[+t.dataset.i].key; return; }
    if (a === "pick") { pick(S.byId[t.dataset.id], t.dataset.key); return; }
    if (a === "qall") { S.qAll = !S.qAll; renderSide(); return; }
    if (a === "remind-done") { var rp = S.byId[t.dataset.id]; put("/api/calendar/doc?path=reminders/" + rp.detail.reel, { done: nowIso() }).then(function () { toast("סומן שבוצע"); load(true); }); return; }
    if (a === "new") { openNew(t.dataset.for, t.dataset.day, t.dataset.time); return; }
    if (a === "idea-del") { put("/api/calendar/doc?path=ideas/" + p.id.slice(2), { _delete: true }).then(function () { closeDlg(); load(true); }); return; }
    if (a === "reel-postiz") { reelPostiz(t); return; }
    if (a === "hooks") { askHooks(p); return; }
    if (a === "hookpick") { hookPick(p, +t.dataset.i); return; }
    if (a === "grade") { var o = p.options[optIndex(p)]; post("/api/grade", { batch: p.kind === "test" ? "test-2026-11" : p.detail.batch, key: o.key, score: +t.dataset.n }).then(function () { toast("הציון נשמר"); load(true); }).catch(function (e) { toast(e.message); }); return; }
    if (a === "produce") { produce(t); return; }
    if (a === "authorize") { authorize(t); return; }
    if (a === "reveal") { post("/api/production/reveal", { key: t.dataset.key }).catch(function (e) { toast(e.message); }); return; }
    if (a === "postiz" || a === "postiz-draft") { sendPostiz(t, a === "postiz-draft"); return; }
    if (a === "pzprev") { api("/api/postiz-preview?key=" + encodeURIComponent(t.dataset.key)).then(function (b) { $("#ccPzPrev").innerHTML = '<div class="cc-two"><div class="cc-fixed" translate="no"><b>אינסטגרם</b><br>' + esc(b.instagram && b.instagram.text || b.ig || JSON.stringify(b.instagram || "")).replace(/\n/g, "<br>") + '</div><div class="cc-fixed" translate="no"><b>פייסבוק</b><br>' + esc(b.facebook && b.facebook.text || b.fb || "").replace(/\n/g, "<br>") + "</div></div>"; }).catch(function (e) { toast(e.message); }); return; }
    if (a === "approve-main") { put("/api/calendar/doc?path=approvals/" + p.id, { main: nowIso() }).then(function () { toast("הגרסה הראשית אושרה"); load(true); }); return; }
    if (a === "unapprove") { put("/api/calendar/doc?path=approvals/" + p.id, { _delete: true }).then(function () { load(true); }); return; }
    if (a === "make") { makeReel(p); return; }
    if (a === "gpt") { gpt(p); return; }
    if (a === "trials") { post("/api/calendar/trials", { reel: p.detail.reel }).then(function () { toast("יוצר גרסאות ניסיון"); pollJobs(true); }).catch(function (e) { toast(e.message); }); return; }
    if (a === "ask") { var tx = $("#ccAskT").value.trim(); if (tx.length < 3) { $("#ccAskT").focus(); return; } askChange(p, tx); return; }
    if (a === "ask-apply") { var res = S.answers[p.id]; applyEdits(p, res.changes || []).then(function () { delete S.answers[p.id]; toast("הוחל ונשמר"); load(true); }).catch(function (e) { toast("לא נשמר: " + e.message); }); return; }
    if (a === "ask-drop") { delete S.answers[p.id]; renderDrawer(); return; }
    if (a === "idea") { askIdea(p); return; }
    if (a === "made") {   /* עשיתי: the reel calendar's tick (local-edits.json "made", which HQ's home counts) */
      var dm = p.detail, on = !dm.made; dm.made = on; t.setAttribute("aria-pressed", String(on));
      put("/api/reels-hub/doc?path=made/" + encodeURIComponent(dm.rkey), { key: dm.rkey, made: on, at: nowIso() })
        .then(function () { toast(on ? "סומן שעשית" : "הסימון בוטל"); load(true); })
        .catch(function (e) { dm.made = !on; t.setAttribute("aria-pressed", String(!on)); toast("לא נשמר: " + e.message); });
      return;
    }
    if (a === "copy-script") { copyText(scriptText(p), t); return; }
    if (a === "copy-cap") { var ct = $('#ccPane textarea[data-f="caption"]'), R = rcfg(); copyText(ct ? ct.value + "\n\n" + (R.disclaimer || "") : ((p.detail.pz_text || {}).ig || p.detail.texts.caption), t); return; }
    if (a === "tp") { if (TP.on) tpStop(); else tpStart(); return; }
    if (a === "tp-speed") { TP.lvl = Math.max(1, Math.min(7, TP.lvl + (+t.dataset.d || 0))); tpPaint(); return; }
    if (a === "file-x") { removeFile(t.closest(".lb-file")); return; }
    if (t.dataset.open) { ev.preventDefault(); closeSideIfPhone(); openPiece(t.dataset.open, t.dataset.tab); return; }
    if (t.dataset.day && (t.classList.contains("cc-cell") || t.classList.contains("cc-more") || t.classList.contains("cc-wh") || t.closest("#ccMini"))) {
      if (t.closest("#ccMini") && ev.detail > 1) { closeSideIfPhone(); openDay(t.dataset.day); return; }   /* a double click opens the day (Yarin, 11 Nov 2026) */
      if (t.closest("#ccMini")) { S.sel = t.dataset.day; closeSideIfPhone(); if (S.open) closeDlg(true); setMonth(S.sel.slice(0, 7)); renderAll(); syncHash(); return; }
      openDay(t.dataset.day); return;
    }
  }
  function renderAll() { renderSide(); renderView(); renderTop(); }
  function hookPick(p, i) {
    var k = hookKey(p), hk = Object.assign({ options: [], trial: [] }, p.detail.hooks || {}), q = hk.options[i];
    hk.picked = i; hk.trial = (hk.trial || []).filter(function (x) { return x !== i; });
    put("/api/calendar/doc?path=hooks/" + encodeURIComponent(k), hk).then(function () {
      if (p.kind === "idea") return;
      var it = itemOf(p), field = p.kind === "reel" ? "hook" : p.kind === "test" && it && it.slides[0] && it.slides[0].big !== undefined ? "big" : "headline";
      return applyEdits(p, [{ field: field, slide: p.kind === "reel" ? null : 1, value: q }]);
    }).then(function () { toast("ההוק נבחר ונשמר"); load(true); }).catch(function (e) { toast("לא נשמר: " + e.message); });
  }
  function trialHook(p, i, on) {
    var k = hookKey(p), hk = Object.assign({ options: [], trial: [] }, p.detail.hooks || {});
    hk.trial = (hk.trial || []).filter(function (x) { return x !== i; });
    if (on) { if (hk.trial.length >= 4) { toast("עד 4 גרסאות ניסיון"); renderDrawer(); return; } hk.trial.push(i); }
    put("/api/calendar/doc?path=hooks/" + encodeURIComponent(k), hk).then(function () { load(true); });
  }
  var armed = null;
  function produce(t) {
    var cost = +t.dataset.cost || 0;
    if (cost && armed !== t.dataset.key) { armed = t.dataset.key; t.textContent = "לאשר: עד $" + cost.toFixed(2) + " לקרוסלה הזאת"; setTimeout(function () { armed = null; }, 8000); return; }
    armed = null; t.disabled = true;
    post("/api/production/start", { key: t.dataset.key }).then(function () { toast("ההפקה התחילה"); load(true); }).catch(function (e) { t.disabled = false; toast(e.message); });
  }
  function authorize(t) {
    var b = parseFloat($("#ccBudget").value), yes = $("#ccYes").checked;
    if (!yes) { toast("צריך לסמן שאתה מאשר"); return; }
    if (!(b > 0)) { toast("כתבו תקציב במספרים"); return; }
    post("/api/production/authorize", { key: t.dataset.key, budget_usd: b, confirmed: true }).then(function () { toast("אושר, ממשיך"); load(true); }).catch(function (e) { toast(e.message); });
  }
  function gpt(p) {
    var b = parseFloat($("#ccGptBudget").value), yes = $("#ccGptYes").checked;
    if (!yes) { toast("צריך לסמן שאתה מאשר"); return; }
    if (!(b > 0)) { toast("כתבו תקציב במספרים"); return; }
    post("/api/calendar/gpt", { reel: p.detail.reel, budget_usd: b, confirmed: true }).then(function () { toast("מייצר את התמונות"); pollJobs(true); }).catch(function (e) { toast(e.message); });
  }
  function makeReel(p) {
    var d = p.detail, ask = ($("#ccMakeAsk") || {}).value || "";
    post("/api/reel-make/jobs", { reel: d.rkey, prompt: ask, script: { hook: d.texts.hook, vo: d.texts.vo }, label: d.texts.hook.split("\n")[0] })
      .then(function () {   /* leave the note box, or the panel (which never redraws under a field being typed in) hides the steps */
        var ta = $("#ccMakeAsk"); if (ta && document.activeElement === ta) ta.blur();
        toast("יצירת הריל התחילה"); pollJobs(true);
      }).catch(function (e) { toast(e.body && e.body.code === "no_files" ? "קודם להעלות את הקבצים של הריל" : e.message); });
  }
  var pzArmed = null;
  function sendPostiz(t, draft) {
    var dd = $("#ccPzD").value, tt = $("#ccPzT").value;
    if (!dd || !tt) { toast("בחרו תאריך ושעה"); return; }
    var sig = t.dataset.key + dd + tt + draft;
    if (pzArmed !== sig) {
      pzArmed = sig; $("#ccPzNote").textContent = (draft ? "טיוטה בפוסטיז" : "לתזמן ל־" + full(dd) + " " + tt + " באינסטגרם ובפייסבוק") + "? לחיצה נוספת שולחת.";
      t.textContent = draft ? "כן, טיוטה" : "כן, לתזמן"; return;
    }
    pzArmed = null; t.disabled = true;
    post("/api/production/postiz", { key: t.dataset.key, when: dd + "T" + tt, draft: draft }).then(function () { toast(draft ? "נשמר כטיוטה בפוסטיז" : "תוזמן בפוסטיז"); load(true); })
      .catch(function (e) { t.disabled = false; toast(e.message); });
  }

  function onChange(ev) {
    var t = ev.target;
    if (t.matches("textarea[data-f]")) {
      var p = S.byId[S.open && S.open.piece]; if (!p || t.value === t.dataset.v) return;
      t.dataset.v = t.value; saveField(p, t.dataset.f, t.value); return;
    }
    if (t.matches('[data-act="trialhook"]')) { trialHook(S.byId[S.open.piece], +t.dataset.i, t.checked); return; }
    if (t.id === "ccFileIn") { upload(S.byId[S.open.piece].detail.rkey, t.files); t.value = ""; return; }
  }

  // drag to reschedule (mouse); on touch the piece panel's date is the way
  var dragId = null, navT = null, navBtn = null;
  function onDragStart(ev) { var it = ev.target.closest && ev.target.closest("[draggable=true][data-open]"); if (!it) return; dragId = it.dataset.open; it.classList.add("is-drag"); ev.dataTransfer.effectAllowed = "move"; try { ev.dataTransfer.setData("text/plain", dragId); } catch (x) {} hidePeek(); }
  /* held over an arrow button or its gutter at the left or right edge of the calendar, the view moves on to the next or previous day,
     week or month (Yarin, 11 Nov 2026: the arrows moved to the edges, the edge strips stay but are not drawn) */
  function edgeDir(el) { return el.dataset.dir ? +el.dataset.dir : (el.id === "ccNext" ? 1 : -1); }
  function dropLine(on) { var l = $("#ccDropLine"); if (l && !on) l.parentNode.removeChild(l); return l; }
  function onDragEnd() {
    dragId = null; clearTimeout(navT); navT = null; navBtn = null; dropLine(false);
    $$(".is-drag,.is-drop").forEach(function (x) { x.classList.remove("is-drag", "is-drop"); });
  }
  /* where a piece dropped: the day, and in the week and day views the hour under the pointer (15 minute steps), snapping to an
     empty planned slot of its own kind when it is near one; the month and the mini calendar keep the piece's own hour unless it
     lands on an empty slot's red outline (Yarin, 11 Nov 2026: "move content in each view to other days / time / week / month") */
  function dragTarget(ev) {
    var e = ev.target; if (!e || !e.closest) return null;
    var c = e.closest(".cc-wcol[data-day]");
    if (c) return { el: c, day: c.dataset.day, col: c };
    c = e.closest(".cc-cell[data-day],#ccMini [data-day],.cc-wh[data-day]");
    return c ? { el: c, day: c.dataset.day, col: null } : null;
  }
  function slotNear(root, fam, m, tol) {
    var best = null, bd = tol + 1;
    $$("[data-time][data-family]", root).forEach(function (g) {
      if (!g.dataset.time || g.dataset.family !== fam) return;
      var d = Math.abs(mins(g.dataset.time) - m); if (d < bd) { bd = d; best = g.dataset.time; }
    });
    return best;
  }
  function dropTime(t, ev, p) {
    var fam = family(p);
    if (t.col) {
      var r0 = +t.col.dataset.r0, r1 = +t.col.dataset.r1; if (!r1) return null;
      var rc = t.col.getBoundingClientRect(), m = r0 * 60 + (ev.clientY - rc.top) / rc.height * (r1 - r0 + 1) * 60;
      m = Math.max(0, Math.min(23 * 60 + 45, Math.round(m / 15) * 15));
      var near = fam ? slotNear(t.col, fam, m, 40) : null;
      if (near) return near;
      return String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0");
    }
    var g = ev.target.closest(".cc-gap[data-time]");
    return g && g.dataset.time && fam && g.dataset.family === fam ? g.dataset.time : null;
  }
  function onDragOver(ev) {
    if (!dragId) return;
    var nb = ev.target.closest && ev.target.closest("#ccPrev,#ccNext,.cc-edge");
    if (nb) {   /* held over the arrows, the view moves on: another week, month or day while the piece is held */
      ev.preventDefault();
      if (nb !== navBtn) {
        clearTimeout(navT); navBtn = nb;
        navT = setTimeout(function step() { shift(edgeDir(nb)); navT = setTimeout(step, 900); }, 500);
      }
      $$(".is-drop").forEach(function (x) { if (x !== nb) x.classList.remove("is-drop"); }); nb.classList.add("is-drop"); dropLine(false);
      return;
    }
    if (navBtn) { clearTimeout(navT); navT = null; navBtn = null; $$("#ccPrev,#ccNext,.cc-edge").forEach(function (x) { x.classList.remove("is-drop"); }); }
    var t = dragTarget(ev); if (!t) return;
    ev.preventDefault();
    $$(".is-drop").forEach(function (x) { if (x !== t.el) x.classList.remove("is-drop"); });
    t.el.classList.add("is-drop");
    var p = S.byId[dragId], l = dropLine(true);
    if (t.col && p) {
      var tm = dropTime(t, ev, p), r0 = +t.col.dataset.r0, r1 = +t.col.dataset.r1;
      if (tm && r1) {
        if (!l || l.parentNode !== t.col) { dropLine(false); l = document.createElement("i"); l.id = "ccDropLine"; l.className = "cc-dropline"; l.setAttribute("aria-hidden", "true"); t.col.appendChild(l); }
        l.style.top = ((mins(tm) - r0 * 60) / ((r1 - r0 + 1) * 60) * 100).toFixed(3) + "%"; l.innerHTML = "<b>" + tm + "</b>";
      }
    } else dropLine(false);
  }
  function onDrop(ev) {
    if (!dragId) return;
    if (ev.target.closest && ev.target.closest(".cc-edge")) { ev.preventDefault(); onDragEnd(); return; }
    var t = dragTarget(ev); if (!t) return;
    ev.preventDefault();
    var p = S.byId[dragId], tm = p ? dropTime(t, ev, p) : null;
    onDragEnd(); moveTo(p, t.day, tm);
  }

  // hover preview (mouse only)
  var peekT;
  function onOver(ev) {
    if (!matchMedia("(hover: hover)").matches || dragId) return;
    var it = ev.target.closest && ev.target.closest(".cc-it[data-open],.cc-wb[data-open]");
    clearTimeout(peekT);
    if (!it) { hidePeek(); return; }
    peekT = setTimeout(function () {
      var p = S.byId[it.dataset.open]; if (!p) return;
      var pk = $("#ccPeek"), r = it.getBoundingClientRect();
      pk.className = "cc-peek lb-popover " + catOf(p);
      pk.innerHTML = '<div class="hd">' + kindIcon(p) + esc(kindLabel(p)) + " · " + (p.time || "בלי שעה") + "</div><div class=\"tl\" translate=\"no\">" + esc(p.title || "") + "</div>" + stChip(p) +
        (p.thumb ? '<img src="' + esc(p.thumb) + '" alt="">' : "") + (p.flags || []).slice(0, 2).map(function (f) { return '<div class="cc-flag">' + esc(f.he) + "</div>"; }).join("");
      pk.hidden = false;
      var x = Math.min(window.innerWidth - pk.offsetWidth - 8, Math.max(8, r.left + r.width / 2 - pk.offsetWidth / 2)), y = r.bottom + 6;
      if (y + pk.offsetHeight > window.innerHeight - 8) y = Math.max(8, r.top - pk.offsetHeight - 6);
      pk.style.left = x + "px"; pk.style.top = y + "px";
    }, 350);
  }
  function hidePeek() { clearTimeout(peekT); var pk = $("#ccPeek"); if (pk) pk.hidden = true; }

  function step(n) {   /* month view: move the selected day with the keys */
    S.sel = addDays(S.sel || today(), n); setMonth(S.sel.slice(0, 7)); renderSide(); renderView();
    var c = $('.cc-cell[data-day="' + S.sel + '"]'); if (c) c.focus();
  }
  function goMonth(n) { var m = adjMonth(S.month, n); S.sel = m + "-01"; if (S.open) closeDlg(true); setMonth(m); renderAll(); syncHash(); }
  function onKey(ev) {
    var tag = (ev.target.tagName || "").toLowerCase();
    if (ev.key === "Escape") {
      if ($("#ccHelp") && !$("#ccHelp").hidden) { $("#ccHelp").hidden = true; return; }
      if (S.open && dlg.open && docked) { closeDlg(); ev.preventDefault(); }
      return;
    }
    if (tag === "input" || tag === "textarea" || tag === "select" || ev.target.isContentEditable || ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var rtl = document.documentElement.dir !== "ltr";
    if (ev.key === "t" || ev.key === "T" || ev.key === "א") { goToday(); ev.preventDefault(); }
    else if (ev.key === "1" || ev.key === "2" || ev.key === "3") { setView(["month", "week", "day"][+ev.key - 1]); }
    else if (ev.key === "/") { $("#ccQ2").focus(); ev.preventDefault(); }
    else if (ev.key === "?") { var h = $("#ccHelp"); h.hidden = !h.hidden; }
    else if (ev.key === "ArrowLeft" || ev.key === "ArrowRight") { if (!S.open) { shift((ev.key === "ArrowLeft") === rtl ? 1 : -1); ev.preventDefault(); } }
    else if (ev.key === "ArrowUp" || ev.key === "ArrowDown") { if (!S.open && S.view === "month") { step(ev.key === "ArrowDown" ? 7 : -7); ev.preventDefault(); } }
    else if (ev.key === "PageUp" || ev.key === "PageDown") { goMonth(ev.key === "PageDown" ? 1 : -1); ev.preventDefault(); }
    else if (ev.key === "Enter" && ev.target.classList && ev.target.classList.contains("cc-cell")) { openDay(ev.target.dataset.day); ev.preventDefault(); }
  }
  /* the page sidebar folds away on a wide screen (Yarin, 11 Nov 2026: "make it colapsable"), remembered in this browser */
  function setSide(off) {
    S.sideOff = off; store("sideOff", off);
    document.documentElement.classList.toggle("cc-side-off", off);
    var b = $("#ccSideBtn"); if (b) { b.setAttribute("aria-pressed", String(!off)); b.title = off ? "הצגת הסרגל" : "קיפול הסרגל"; }
    if (docked) placeFill();
  }
  function closeSideIfPhone() { var s = $("#ccSide"); if (s.classList.contains("is-open")) { s.classList.remove("is-open"); $("#ccScrim").hidden = true; } }

  /* the story editor (story.js) works with the page's own helpers */
  window.CCPage = { S: S, esc: esc, ic: ic, toast: toast, api: api, post: post, put: put, load: load, full: full, ddmm: ddmm, iso: iso, dayName: dayName,
    stChip: stChip, chans: chans, kindIcon: kindIcon, kindLabel: kindLabel, saveState: saveState, setSave: setSave, today: today,
    closeDlg: function () { closeDlg(); }, openPiece: function (id) { openPiece(id); } };

  function init() {
    dlg = $("#ccDlg");
    S.view = stored("view", "month"); if (["month", "week", "day"].indexOf(S.view) < 0) S.view = "month"; S.drafts = !!stored("drafts", false); S.kinds = Object.assign(S.kinds, stored("kinds", {})); S.tests = Object.assign(S.tests, stored("tests", {}));
    var m = /^#(\d{4}-\d{2})(?:-(\d{2}))?(?:\/(.+))?$/.exec(decodeURIComponent(location.hash));
    var t = iso(new Date());
    S.month = m ? m[1] : t.slice(0, 7); S.sel = m && m[2] ? m[1] + "-" + m[2] : (S.month === t.slice(0, 7) ? t : S.month + "-01");
    if (matchMedia("(max-width: 640px)").matches && S.view === "week") S.view = "day";
    setSide(!!stored("sideOff", false));
    renderAll();
    load(true).then(function () { if (m && m[2]) openDay(S.sel, m[3] || null); });
    pollJobs();
    addEventListener("hashchange", function () {   /* a link to #2026-11-13 or #2026-11-13/<piece> in the same tab */
      var h = /^#(\d{4}-\d{2})(?:-(\d{2}))?(?:\/(.+))?$/.exec(decodeURIComponent(location.hash));
      if (!h) return;
      if (h[2]) openDay(h[1] + "-" + h[2], h[3] || null);
      else if (h[1] !== S.month) { S.month = h[1]; S.sel = h[1] + "-01"; S.data = null; renderAll(); load(true); }
    });
    setInterval(function () { if (!document.hidden) load(); }, 15000);
    document.addEventListener("visibilitychange", function () { if (!document.hidden) load(); });
    document.addEventListener("click", onClick);
    document.addEventListener("change", onChange);
    document.addEventListener("keydown", onKey);
    document.addEventListener("dragstart", onDragStart); document.addEventListener("dragend", onDragEnd);
    document.addEventListener("dragover", onDragOver); document.addEventListener("drop", onDrop);
    document.addEventListener("mousemove", function (ev) { if (dragId && ev.buttons === 0) onDragEnd(); });
    document.addEventListener("mouseover", onOver);
    /* files from the Finder: anywhere on an open reel they go into it; anywhere else they are refused instead of opening in the tab */
    dlg.addEventListener("dragenter", function (ev) { if (!hasFiles(ev) || !openReel()) return; ev.preventDefault(); if (fileDragN++ === 0) veilOn(true); });
    dlg.addEventListener("dragleave", function (ev) { if (!hasFiles(ev) || !fileDragN) return; if (--fileDragN === 0) veilOn(false); });
    dlg.addEventListener("drop", function (ev) { if (!hasFiles(ev)) return; ev.preventDefault(); ev.stopPropagation(); fileDragN = 0; veilOn(false); var p = openReel(); if (p) upload(p.detail.rkey, ev.dataTransfer.files); });
    document.addEventListener("dragover", function (ev) { if (!hasFiles(ev) || dragId) return; ev.preventDefault(); ev.dataTransfer.dropEffect = openReel() && dlg.contains(ev.target) ? "copy" : "none"; });
    document.addEventListener("drop", function (ev) { if (hasFiles(ev) && !dragId) ev.preventDefault(); });
    /* the reel's script: timings follow the typing; the teleprompter stops when Yarin scrolls or touches the panel himself */
    document.addEventListener("input", function (ev) { if (ev.target.matches && ev.target.matches('#ccScr textarea[data-f^="vo__"]')) retime(); });
    ["wheel", "touchstart", "pointerdown"].forEach(function (k) { dlg.addEventListener(k, function (ev) { if (TP.on && !(ev.target.closest && ev.target.closest(".cc-tp"))) tpStop(); }, { passive: true }); });
    document.addEventListener("keydown", function (ev) {   /* ⌘ Enter sends the composer it is typed in */
      if (ev.key !== "Enter" || !(ev.metaKey || ev.ctrlKey)) return;
      if (ev.target.id === "ccAskT") { ev.preventDefault(); var b = $('#ccDlg [data-act="ask"]'); if (b && !b.disabled) b.click(); }
      else if (ev.target.id === "ccMakeAsk") { ev.preventDefault(); var m = $('#ccDlg [data-act="make"]'); if (m) m.click(); }
    });
    $("#ccPrev").onclick = function () { shift(-1); };
    $("#ccNext").onclick = function () { shift(1); };
    $("#ccSideBtn").onclick = function () { setSide(!S.sideOff); };
    $("#ccToday").onclick = goToday;
    $("#ccDlgX").onclick = function () { closeDlg(); };
    dlg.addEventListener("close", function () { if (S.open) { S.open = null; setDock(false); renderView(); } });
    $("#ccDlgT").addEventListener("click", function (ev) { if (ev.target.closest("#ccBack")) closeDlg(); });
    $("#ccQ2").addEventListener("input", function () { S.q = this.value.trim(); renderView(); });
    $("#ccNewBtn").onclick = function () { openNew("carousel", S.sel); };
    $("#ccNewForm").addEventListener("submit", submitNew);
    $("#ccNewX").onclick = function () { $("#ccNew").close(); };
    $$("#ccNewFor button").forEach(function (b) { b.onclick = function () { $$("#ccNewFor button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); }; });
    $("#ccHelpBtn").onclick = function () { var h = $("#ccHelp"); h.hidden = !h.hidden; };
    $("#ccMenu").onclick = function () { var s = $("#ccSide"), o = !s.classList.contains("is-open"); s.classList.toggle("is-open", o); $("#ccScrim").hidden = !o; };
    $("#ccScrim").onclick = closeSideIfPhone;
    if (window.ResizeObserver) {
      new ResizeObserver(function () { if (dlg.open) showDlg(); }).observe(document.documentElement);
      var fitT; new ResizeObserver(function () { cancelAnimationFrame(fitT); fitT = requestAnimationFrame(function () { if (S.view === "month") fitMonth(); else settle(); }); }).observe($("#ccView"));
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (S.view === "month") fitMonth(); else settle(); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
