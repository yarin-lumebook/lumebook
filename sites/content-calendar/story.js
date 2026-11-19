/* The story editor of the content calendar (19 Nov 2026; Yarin: "add it to our content-calendar with full story editing capabilities").
   A story piece (kind "story", tools/stories.py) is one set = one day of one series, a few frames of 1080 x 1920. Each frame is data:
   a background picture and layers (text, picture, shape, sticker placeholder) drawn by story-frame.js, the same renderer that makes the
   PNGs, so what is seen here is what goes out. Everything is edited in place: pick a frame on the strip, click a layer to select it,
   drag it to move, pull its side handles to resize, change it in the panel on the side; arrows nudge (Shift by 10), Delete removes,
   ⌘Z / ⇧⌘Z undo and redo, ⌘D duplicates. Saves by itself (POST /api/calendar/story op save), an edit after an approval clears it.
   page.js hands its helpers over as window.CCPage. */
(function () {
  "use strict";
  var ST = null, RV = null, CSS_ON = false;
  var SWATCH = ["#FFFFFF", "#F5C26B", "#C9954A", "#5B2BD6", "#2B1A5C", "#2B0E6E", "#111111", "#E8476A"];
  var TYPE_HE = { text: "טקסט", image: "תמונה", shape: "צורה", sticker: "מדבקה" };
  var STK = { link: "קישור", poll: "סקר", question: "תיבת שאלה", countdown: "ספירה לאחור", mention: "תיוג", emoji: "מחוון אימוג'י" };
  function G() { return window.CCPage; }
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(t) { return G().esc(t); }
  function ic(n) { return G().ic(n); }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function sig(s) { return JSON.stringify([s.frames, s.time, s.channels, s.notes]); }
  function fr() { return ST.set.frames[ST.fi]; }
  function layer() { var f = fr(); if (!f || !ST.sel) return null; for (var i = 0; i < f.layers.length; i++) if (f.layers[i].id === ST.sel) return f.layers[i]; return null; }
  function uid(p) { return p + Math.random().toString(36).slice(2, 7); }
  function lib() { var d = G().S.data || {}; return d.story_lib || { art: [], series: {} }; }
  function series() { return (lib().series || {})[ST.set.series] || {}; }
  function css() {
    if (CSS_ON || !window.LBStory) return;
    var s = document.createElement("style"); s.textContent = LBStory.css("/"); document.head.appendChild(s); CSS_ON = true;
  }

  /* ---------- the working copy: kept across the page's 15 second refreshes, replaced only by a newer server copy ---------- */
  function sync(p) {
    var d = p.detail, srv = d.set;
    if (!ST || ST.key !== d.key) {
      ST = { key: d.key, set: clone(srv), base: sig(srv), fi: 0, sel: null, safe: true, hist: [], fut: [], dirty: false, saving: false, ver: 0, p: p, pick: null };
    } else {
      ST.p = p;
      if (!ST.dirty && !ST.saving && sig(srv) !== ST.base) { ST.set = clone(srv); ST.base = sig(srv); }
      ST.set.approved = srv.approved; ST.set.rendered = srv.rendered; ST.set.postiz = srv.postiz;
    }
    if (ST.fi >= ST.set.frames.length) ST.fi = ST.set.frames.length - 1;
    if (!layer()) ST.sel = null;
  }
  function busy() { return !!(ST && document.getElementById("ccStory") && (ST.drag || ST.dirty || ST.saving || ST.pick)); }

  function pushHist() { ST.hist.push(JSON.stringify(ST.set.frames)); if (ST.hist.length > 80) ST.hist.shift(); ST.fut = []; }
  /* every edit goes through here: one undo step (typing in one field within 1.5 s is one step), then a save after 0.7 s */
  function change(fn, opt) {
    opt = opt || {};
    var now = Date.now();
    if (!(opt.merge && ST.lastMerge === opt.merge && now - ST.lastAt < 1500)) pushHist();
    ST.lastMerge = opt.merge || null; ST.lastAt = now;
    fn();
    dirty();
    if (opt.props === false) { paintStage(); paintStrip(); } else paint();
  }
  function dirty() { ST.dirty = true; ST.ver++; clearTimeout(ST.saveT); ST.saveT = setTimeout(save, 700); G().setSave("wait", "לא נשמר עדיין…"); }
  function undo() { if (!ST.hist.length) return; ST.fut.push(JSON.stringify(ST.set.frames)); ST.set.frames = JSON.parse(ST.hist.pop()); fix(); dirty(); paint(); }
  function redo() { if (!ST.fut.length) return; ST.hist.push(JSON.stringify(ST.set.frames)); ST.set.frames = JSON.parse(ST.fut.pop()); fix(); dirty(); paint(); }
  function fix() { if (ST.fi >= ST.set.frames.length) ST.fi = ST.set.frames.length - 1; if (!layer()) ST.sel = null; }

  function save() {
    if (!ST || !ST.dirty) return Promise.resolve();
    var v = ST.ver, key = ST.key, was = !!(ST.set.approved);
    var body = { op: "save", key: key, set: { frames: ST.set.frames, time: ST.set.time, title: ST.set.title || "", channels: ST.set.channels, notes: ST.set.notes || "" } };
    ST.saving = true; G().setSave("wait", "שומר…");
    return G().post("/api/calendar/story", body).then(function (b) {
      if (!ST || ST.key !== key) return;
      ST.saving = false;
      if (ST.ver === v) { ST.dirty = false; ST.base = sig(ST.set); }
      G().setSave("", "נשמר");
      if (was && b.approved === false) { ST.set.approved = null; G().toast("האישור בוטל, כי התוכן השתנה. צריך לאשר שוב"); }
      G().load(true);
    }).catch(function (e) {
      if (ST) ST.saving = false;
      G().setSave("error", "לא נשמר: " + e.message);
      G().toast("השמירה נכשלה: " + e.message, "לנסות שוב", save);
    });
  }
  function flush() { clearTimeout(ST.saveT); return ST.dirty ? save() : Promise.resolve(); }

  /* ---------- the panel ---------- */
  function html(p) {
    css(); sync(p);
    var g = G(), d = p.detail, s = ST.set;
    var chips = '<div class="cc-rchips">' + (d.day >= 1 && d.day <= d.days ? '<span class="lb-chip">יום ' + d.day + " מתוך " + d.days + "</span>" : "") +
      '<span class="lb-chip">' + s.frames.length + " פריימים</span>" +
      (series().link ? '<a class="lb-chip tint" href="' + esc(series().link) + '" target="_blank" rel="noopener" title="הקישור של הסדרה, עם UTM">' + ic("link") + "הקישור</a>" : "") +
      (d.approved ? '<span class="lb-chip success">' + ic("check") + "אושר</span>" : "") + (d.fresh ? "" : '<span class="lb-chip">התמונות לא מעודכנות</span>') + "</div>";
    var flags = (p.flags || []).filter(function (f) { return f.code !== "stale"; }).map(function (f) { return '<div class="cc-flag">' + ic("info") + esc(f.he) + "</div>"; }).join("");
    var head = '<div class="cc-ph"><div class="r1">' + g.kindIcon(p) + "<span>" + esc(g.kindLabel(p)) + "</span>" + g.stChip(p) + g.chans(p) +
      '<span class="lb-spacer"></span>' + g.saveState() + '<span class="lb-num">' + esc(s.time) + "</span></div>" +
      '<h3 translate="no">' + esc(p.title) + "</h3>" + (series().about ? '<p class="cc-note">' + esc(series().about) + "</p>" : "") + chips + flags + "</div>";
    return head + '<section class="cc-part" data-part="edit"><h4 class="cc-part-h">' + ic("pencil") + "עריכה</h4>" +
      '<div class="st-ed" id="ccStory" data-key="' + esc(ST.key) + '"><div class="st-strip" id="stStrip"></div>' + stageHtml() + '<div class="st-props" id="stProps"></div></div></section>' +
      '<section class="cc-part st-pub" data-part="publish"><h4 class="cc-part-h">' + ic("send") + "תמונות, אישור ופרסום</h4>" + publishHtml(p) + "</section>";
  }
  function after(p) { if (!ST) return; paint(); fit(); }

  function stageHtml() {
    return '<div class="st-stage"><div class="st-bar lb-btn-group">' +
      btn("add-text", "pencil", "טקסט") + btn("add-image", "image", "תמונה") + btn("add-shape", "stack", "צורה") + btn("add-sticker", "link", "מדבקה") + btn("add-review", "chat", "ביקורת") +
      '<span class="lb-spacer"></span>' + btn("undo", "undo", "", "ביטול פעולה (⌘Z)") + '<button type="button" class="lb-btn ghost sm" data-s="redo" title="שחזור (⇧⌘Z)">↷</button>' +
      '<button type="button" class="lb-chip check" data-s="safe" aria-pressed="' + ST.safe + '" title="האזורים שאינסטגרם מכסה (פרופיל למעלה, תגובה למטה)">אזורים מוסתרים</button></div>' +
      '<div class="st-view" id="stView"><div class="st-wrap" id="stWrap"><div class="st-canvas" id="stCanvas"></div><div class="st-guide" id="stGuide" hidden></div></div></div>' +
      '<div class="st-fnav"><button type="button" class="lb-btn ghost sm" data-s="fprev" aria-label="הפריים הקודם">' + ic("arrow-right") + '</button><span class="lb-num" id="stFn"></span>' +
      '<button type="button" class="lb-btn ghost sm" data-s="fnext" aria-label="הפריים הבא">' + ic("arrow-left") + "</button></div></div>";
  }
  function btn(s, icon, label, title) { return '<button type="button" class="lb-btn secondary sm" data-s="' + s + '"' + (title ? ' title="' + esc(title) + '" aria-label="' + esc(title) + '"' : "") + ">" + ic(icon) + esc(label) + "</button>"; }

  function paint() { paintStrip(); paintStage(); paintProps(); }
  function paintStrip() {
    var el = $("#stStrip"); if (!el) return;
    el.innerHTML = ST.set.frames.map(function (f, i) {
      return '<button type="button" class="st-th' + (i === ST.fi ? " is-on" : "") + '" data-s="frame" data-i="' + i + '" draggable="true" aria-label="פריים ' + (i + 1) + '"' + (i === ST.fi ? ' aria-current="true"' : "") + '>' +
        '<span class="st-mini"><span class="st-mini-c">' + LBStory.frameHtml(f, { base: "/", editor: false }) + '</span></span><span class="n lb-num">' + (i + 1) + "</span>" +
        (f.manual ? '<span class="m" title="עולה ידנית מהטלפון">ידני</span>' : "") + "</button>";
    }).join("") + '<div class="st-strip-act"><button type="button" class="lb-btn secondary sm" data-s="add-frame">' + ic("plus") + "פריים</button>" +
      '<button type="button" class="lb-btn ghost sm" data-s="dup-frame" title="שכפול הפריים">' + ic("copy") + "שכפול</button>" +
      '<button type="button" class="lb-btn ghost sm" data-s="fup" title="להקדים">' + ic("arrow-up") + "</button>" +
      '<button type="button" class="lb-btn ghost sm" data-s="del-frame" title="מחיקת הפריים">' + ic("close") + "</button></div>";
    var n = $("#stFn"); if (n) n.textContent = (ST.fi + 1) + " / " + ST.set.frames.length;
  }
  function paintStage() {
    var c = $("#stCanvas"); if (!c) return;
    c.innerHTML = LBStory.frameHtml(fr(), { base: "/", editor: true, safe: ST.safe });
    var el = ST.sel && c.querySelector('[data-lid="' + ST.sel + '"]');
    if (el) { el.classList.add("is-sel"); handles(el); }
  }
  function kNow() { var w = $("#stWrap"); return w ? w.getBoundingClientRect().height / 1920 : 0.3; }
  /* the frame's scale follows the box it sits in; the drawer may not be on screen yet when it is drawn, so wait for a size */
  function fit(n) {
    var w = $("#stWrap"); if (!w) return;
    var k = w.getBoundingClientRect().height / 1920;
    if (!k) { if ((n || 0) < 120) requestAnimationFrame(function () { fit((n || 0) + 1); }); return; }
    w.style.setProperty("--k", String(k));
    if (window.ResizeObserver && !w._ro) {
      w._ro = new ResizeObserver(function () { var k2 = w.getBoundingClientRect().height / 1920; if (k2) { w.style.setProperty("--k", String(k2)); var el = ST && ST.sel && $('#stCanvas [data-lid="' + ST.sel + '"]'); if (el) handles(el); } });
      w._ro.observe(w);
    }
  }
  function handles(el) {
    var c = $("#stCanvas"), l = layer(); if (!c || !l) return;
    $$(".st-hd", c).forEach(function (h) { h.remove(); });
    var x = el.offsetLeft, y = el.offsetTop, w = el.offsetWidth, h = el.offsetHeight;
    var add = function (mode, hx, hy) { var d = document.createElement("span"); d.className = "st-hd"; d.dataset.h = mode; d.style.left = hx + "px"; d.style.top = hy + "px"; c.appendChild(d); };
    add("wl", x, y + h / 2); add("wr", x + w, y + h / 2);
    if (l.type === "shape" || l.type === "sticker") add("h", x + w / 2, y + h);
    (l.blurs || []).forEach(function (b, i) {   /* each blur box: drag it to move, its corner to resize */
      var d = document.createElement("span"); d.className = "st-hd is-blur"; d.dataset.h = "b"; d.dataset.bi = i;
      d.style.left = (x + (b.x + b.w) / 100 * w) + "px"; d.style.top = (y + (b.y + b.h) / 100 * h) + "px"; c.appendChild(d);
    });
  }
  function blurPaint(el, b, i) {   /* one blur box redrawn in place while it is dragged (as story-frame.js draws it) */
    var box = el && el.querySelector('.stf-blur[data-bi="' + i + '"]'); if (!box) return;
    box.style.left = b.x + "%"; box.style.top = b.y + "%"; box.style.width = b.w + "%"; box.style.height = b.h + "%";
    var im = box.querySelector("img"); if (!im) return;
    im.style.left = (-b.x / b.w * 100) + "%"; im.style.top = (-b.y / b.h * 100) + "%"; im.style.width = (10000 / b.w) + "%"; im.style.height = (10000 / b.h) + "%";
  }

  /* ---------- the side panel: the selected layer, or the frame (background, scrim, note, request a picture) ---------- */
  function paintProps() {
    var el = $("#stProps"); if (!el) return;
    el.innerHTML = ST.pick ? pickerHtml() : layer() ? layerProps(layer()) : frameProps(fr());
    if (ST.pick && ST.pick.mode === "review") loadReviews();
  }
  function num(sc, p, v, min, max, step, label) {
    return '<label class="st-f"><span>' + esc(label) + '</span><span class="st-num"><input type="range" data-sc="' + sc + '" data-p="' + p + '" data-t="n" min="' + min + '" max="' + max + '" step="' + (step || 1) + '" value="' + esc(v) + '">' +
      '<input class="lb-input" type="number" data-sc="' + sc + '" data-p="' + p + '" data-t="n" min="' + min + '" max="' + max + '" step="' + (step || 1) + '" value="' + esc(v) + '"></span></label>';
  }
  function swatches(sc, p, cur, label) {
    return '<div class="st-f"><span>' + esc(label) + '</span><span class="st-sw">' + SWATCH.map(function (c) {
      return '<button type="button" data-s="sw" data-sc="' + sc + '" data-p="' + p + '" data-val="' + c + '" style="--c:' + c + '" aria-pressed="' + (String(cur).toUpperCase() === c) + '" aria-label="' + c + '"></button>';
    }).join("") + '<input type="color" data-sc="' + sc + '" data-p="' + p + '" value="' + esc(String(cur || "#FFFFFF").slice(0, 7)) + '" aria-label="צבע אחר"></span></div>';
  }
  function seg(sc, p, cur, opts) {
    return '<span class="lb-segmented">' + opts.map(function (o) { return '<button type="button" data-s="setp" data-sc="' + sc + '" data-p="' + p + '" data-val="' + esc(o[0]) + '" aria-pressed="' + (String(cur) === String(o[0])) + '">' + esc(o[1]) + "</button>"; }).join("") + "</span>";
  }
  function chk(sc, p, on, label) { return '<label class="st-chk"><input type="checkbox" data-sc="' + sc + '" data-p="' + p + '"' + (on ? " checked" : "") + ">" + esc(label) + "</label>"; }
  function lintFor(lid) {
    var d = (ST.p && ST.p.detail) || {}, out = (d.lint || []).filter(function (x) { return x.frame === ST.fi + 1 && x.layer === lid; });
    return out.map(function (x) { return '<div class="cc-flag' + (x.level === "error" ? " is-err" : "") + '">' + ic("info") + esc(x.he) + "</div>"; }).join("");
  }
  function layerProps(l) {
    var h = '<div class="st-ph"><b>' + esc(TYPE_HE[l.type]) + '</b><span class="lb-spacer"></span>' +
      '<button type="button" class="lb-btn ghost sm" data-s="fwd" title="קדימה (מעל השכבות האחרות)">' + ic("arrow-up") + "</button>" +
      '<button type="button" class="lb-btn ghost sm" data-s="dup-layer" title="שכפול (⌘D)">' + ic("copy") + "</button>" +
      '<button type="button" class="lb-btn ghost sm" data-s="del-layer" title="מחיקה (Delete)">' + ic("close") + "</button>" +
      '<button type="button" class="lb-btn ghost sm" data-s="desel" title="חזרה לפריים (Esc)">פריים</button></div>' + lintFor(l.id);
    if (l.type === "text") {
      h += '<label class="st-f"><span>הטקסט <small>(**מילה** בצבע ההדגשה, Enter לשורה חדשה)</small></span><textarea class="lb-textarea lb-editable" dir="rtl" rows="4" translate="no" data-sc="l" data-p="text">' + esc(l.text) + "</textarea></label>" +
        num("l", "size", l.size, 24, 220, 1, "גודל") +
        '<div class="st-f"><span>משקל וגופן</span><span class="st-row">' + seg("l", "weight", l.weight, [[900, "עבה"], [700, "רגיל"]]) + seg("l", "font", l.font || "heebo", [["heebo", "Heebo"], ["assistant", "Assistant"]]) + "</span></div>" +
        '<div class="st-f"><span>יישור</span>' + seg("l", "align", l.align, [["right", "ימין"], ["center", "מרכז"], ["left", "שמאל"]]) + "</div>" +
        swatches("l", "color", l.color, "צבע") + swatches("l", "accent", l.accent || "#F5C26B", "צבע ההדגשה") +
        num("l", "lh", l.lh, 0.8, 2, 0.02, "מרווח שורות") +
        '<div class="st-row">' + chk("l", "shadow", l.shadow, "צל") + '<label class="st-chk"><input type="checkbox" data-s="pill"' + (l.pill ? " checked" : "") + ">רקע מאחורי הטקסט</label></div>" +
        (l.pill ? swatches("l", "pill", l.pill, "צבע הרקע") + num("l", "pad", l.pad == null ? 28 : l.pad, 0, 120, 1, "ריווח פנימי") + num("l", "pillr", l.pillr == null ? 40 : l.pillr, 0, 200, 1, "עיגול פינות") : "");
    } else if (l.type === "image") {
      h += '<div class="st-f"><span>התמונה</span><div class="st-imgpick"><img src="/' + esc(encodeURI(l.src)) + '" alt=""><button type="button" class="lb-btn secondary sm" data-s="img-change">' + ic("image") + "החלפה</button></div></div>" +
        num("l", "radius", l.radius || 0, 0, 400, 1, "עיגול פינות") + '<div class="st-row">' + chk("l", "shadow", l.shadow, "צל") + "</div>" +
        '<div class="st-f"><span>טשטוש שמות ופנים <small>(גוררים את המלבן על התמונה, את הפינה כדי לשנות גודל)</small></span><div class="st-blurs">' +
        (l.blurs || []).map(function (b, i) { return '<span class="lb-chip">טשטוש ' + (i + 1) + '<button type="button" class="lb-btn ghost sm" data-s="blur-del" data-i="' + i + '" aria-label="הסרת טשטוש ' + (i + 1) + '">' + ic("close") + "</button></span>"; }).join("") +
        '<button type="button" class="lb-btn secondary sm" data-s="blur-add">' + ic("plus") + "טשטוש</button></div></div>" +
        ((l.blurs || []).length ? num("l", "blur", l.blur || 16, 4, 60, 1, "עוצמת הטשטוש") : "");
    } else if (l.type === "shape") {
      h += swatches("l", "fill", l.fill, "מילוי") + num("l", "h", l.h, 4, 1920, 1, "גובה") + num("l", "radius", l.radius || 0, 0, 800, 1, "עיגול פינות");
    } else if (l.type === "sticker") {
      h += '<p class="cc-note">מקום שמור למדבקה של אינסטגרם. היא לא מצוירת בתמונה, ופוסטיז לא שולח מדבקות: מוסיפים אותה באפליקציה כשמעלים את הפריים ידנית.</p>' +
        '<label class="st-f"><span>סוג</span><select class="lb-select" data-sc="l" data-p="kind">' + Object.keys(STK).map(function (k) { return '<option value="' + k + '"' + (l.kind === k ? " selected" : "") + ">" + STK[k] + "</option>"; }).join("") + "</select></label>" +
        '<label class="st-f"><span>מה כתוב בה / מה לשאול</span><input class="lb-input lb-editable" dir="rtl" data-sc="l" data-p="label" value="' + esc(l.label) + '" translate="no"></label>' +
        (l.kind === "link" ? '<label class="st-f"><span>הקישור</span><span class="st-row"><input class="lb-input" dir="ltr" data-sc="l" data-p="url" value="' + esc(l.url) + '"><button type="button" class="lb-btn ghost sm" data-s="copy" data-val="' + esc(l.url) + '">' + ic("copy") + "</button></span></label>" : "") +
        num("l", "h", l.h, 40, 800, 1, "גובה");
    }
    h += '<details class="st-more"><summary>מיקום ושקיפות</summary><div class="st-grid3">' +
      ["x", "y", "w"].map(function (k) { return '<label class="st-f"><span>' + { x: "מימין לשמאל x", y: "מלמעלה y", w: "רוחב" }[k] + '</span><input class="lb-input" type="number" data-sc="l" data-p="' + k + '" data-t="n" value="' + esc(l[k]) + '"></label>'; }).join("") + "</div>" +
      num("l", "op", l.op == null ? 100 : l.op, 0, 100, 1, "שקיפות") + num("l", "rot", l.rot || 0, -180, 180, 1, "סיבוב") +
      '<div class="st-row"><button type="button" class="lb-btn ghost sm" data-s="center">למרכז</button><button type="button" class="lb-btn ghost sm" data-s="back">אחורה</button></div></details>';
    return h;
  }
  function frameProps(f) {
    var b = f.bg || {};
    var h = '<div class="st-ph"><b>פריים ' + (ST.fi + 1) + '</b><span class="lb-spacer"></span><span class="cc-note">לחיצה על שכבה בוחרת אותה</span></div>' +
      '<div class="st-f"><span>רקע</span><div class="st-imgpick">' + (b.src ? '<img src="/' + esc(encodeURI(b.src)) + '" alt="">' : '<span class="st-fill" style="background:' + esc(b.fill) + '"></span>') +
      '<button type="button" class="lb-btn secondary sm" data-s="bg-change">' + ic("image") + "החלפה</button>" + (b.src ? '<button type="button" class="lb-btn ghost sm" data-s="bg-clear">צבע בלבד</button>' : "") + "</div></div>" +
      swatches("bg", "fill", b.fill || "#2B0E6E", "צבע הרקע") +
      (b.src ? num("bg", "zoom", b.zoom || 100, 100, 300, 1, "זום") + num("bg", "x", b.x == null ? 50 : b.x, 0, 100, 1, "מיקום אופקי") + num("bg", "y", b.y == null ? 50 : b.y, 0, 100, 1, "מיקום אנכי") : "") +
      num("scrim", "top", (f.scrim || {}).top || 0, 0, 1, 0.05, "הכהיה למעלה (לקריאות)") + num("scrim", "bottom", (f.scrim || {}).bottom || 0, 0, 1, 0.05, "הכהיה למטה") +
      '<label class="st-f"><span>בקשה לתמונה חדשה <small>(Claude מייצר ב־ChatGPT כשמבקשים ממנו בשיחה)</small></span><textarea class="lb-textarea lb-editable" dir="rtl" rows="2" data-sc="f" data-p="ask" translate="no" placeholder="למשל: אותה עגלה, אבל עם מתנה אחת עטופה בזהב">' + esc(f.ask || "") + "</textarea></label>" +
      '<label class="st-f"><span>הערה פנימית</span><textarea class="lb-textarea lb-editable" dir="rtl" rows="2" data-sc="f" data-p="note" translate="no">' + esc(f.note || "") + "</textarea></label>" +
      '<div class="st-row">' + chk("f", "manual", f.manual, "עולה ידנית מהטלפון (בשביל מדבקה), לא דרך פוסטיז") + "</div>" +
      '<div class="st-f"><span>השכבות</span><div class="st-layers">' + f.layers.slice().reverse().map(function (l) {
        var name = l.type === "text" ? String(l.text || "").replace(/\*\*/g, "").split("\n")[0].slice(0, 28) : l.type === "sticker" ? STK[l.kind] : TYPE_HE[l.type];
        return '<button type="button" data-s="sel" data-val="' + esc(l.id) + '"><span class="t">' + esc(TYPE_HE[l.type]) + '</span><span translate="no">' + esc(name || "") + "</span></button>";
      }).join("") + "</div></div>";
    return h;
  }

  /* ---------- pickers: a picture (background or picture layer), or a review from the social proof page ---------- */
  function pickerHtml() {
    var m = ST.pick.mode, h = '<div class="st-ph"><b>' + (m === "review" ? "ביקורת מעמוד ההוכחה החברתית" : m === "bg" ? "רקע לפריים" : "תמונה") + '</b><span class="lb-spacer"></span><button type="button" class="lb-btn ghost sm" data-s="pick-x">' + ic("close") + "</button></div>";
    if (m === "review") {
      return h + '<input class="lb-input" type="search" dir="rtl" id="stRvQ" placeholder="חיפוש במילים או בשם" value="' + esc(ST.pick.q || "") + '">' +
        '<p class="cc-note">צילום המסך האמיתי נכנס לפריים, והשם והתמונה של הכותב מטושטשים. בביקורת מגוגל נכנס גם ציטוט גדול, מילה במילה: לקצר רק בחיתוך עם …, בלי לשנות מילים.</p><div class="st-rvs" id="stRvs">' + (RV ? reviewList() : '<span class="lb-spinner"></span>') + "</div>";
    }
    var groups = {};
    (lib().art || []).forEach(function (a) { (groups[a.group] = groups[a.group] || []).push(a); });
    h += '<label class="lb-btn secondary sm st-up">' + ic("upload") + 'העלאת תמונה<input type="file" accept="image/png,image/jpeg,image/webp" data-up="' + m + '" hidden></label><p class="cc-note">או לגרור קובץ אל הפריים.</p>';
    Object.keys(groups).forEach(function (g) {
      h += '<div class="st-f"><span>' + esc(g) + '</span><div class="st-lib">' + groups[g].map(function (a) {
        return '<button type="button" data-s="pick-src" data-val="' + esc(a.src) + '" title="' + esc(a.name) + '"><img src="/' + esc(encodeURI(a.src)) + '" alt="' + esc(a.name) + '" loading="lazy"></button>';
      }).join("") + "</div></div>";
    });
    if (m !== "bg") h += '<button type="button" class="lb-btn ghost sm" data-s="pick-shots">צילומי מסך של ביקורות</button>' + (ST.pick.shots && RV ? '<div class="st-lib is-wide">' + RV.map(function (r) {
      return '<button type="button" data-s="pick-src" data-val="' + esc(r.src) + '" title="' + esc(r.author) + '"><img src="/' + esc(encodeURI(r.src)) + '" alt="" loading="lazy"></button>';
    }).join("") + "</div>" : "");
    return h;
  }
  function loadReviews() {
    if (RV) return Promise.resolve(RV);
    return G().api("/api/calendar/story-reviews").then(function (b) { RV = b.reviews || []; var l = $("#stRvs"); if (l) l.innerHTML = reviewList(); if (ST.pick && ST.pick.shots) paintProps(); return RV; });
  }
  function reviewList() {
    var q = (ST.pick && ST.pick.q || "").trim().toLowerCase(), used = {};
    ST.set.frames.forEach(function (f) { var m = /ביקורת ([\w\-]+):/.exec(f.note || ""); if (m) used[m[1]] = 1; });
    var PL = { google: "גוגל", instagram: "אינסטגרם", facebook: "פייסבוק", whatsapp: "וואטסאפ" };
    return RV.filter(function (r) { return !q || (r.text + " " + r.author).toLowerCase().indexOf(q) >= 0; }).slice(0, 80).map(function (r) {
      return '<button type="button" class="st-rv' + (used[r.id] ? " is-used" : "") + '" data-s="rv" data-val="' + esc(r.id) + '"><span class="h"><b translate="no">' + esc(r.author || "") + "</b>" + esc(PL[r.platform] || r.platform || "") +
        (r.stars ? " · " + "★".repeat(r.stars) : "") + (used[r.id] ? " · בסט הזה" : "") + '</span><span class="x" translate="no">' + esc(String(r.text || "").slice(0, 160)) + "</span></button>";
    }).join("") || '<p class="cc-note">לא נמצא.</p>';
  }
  /* a review frame: the real screenshot with the name and photo blurred (Yarin, 19 Nov 2026: "use the real comments and reviews
     screenshots just blur the names"). The server lays it out and finds the name (tools/stories.py review_layers); the layers it
     made before (group "review") are replaced, everything else on the frame stays. */
  function applyReview(r) {
    var f = fr(), cta = f.layers.some(function (l) { return l.type === "sticker" || (l.type === "text" && l.y >= 1280 && l.group !== "review"); });
    G().toast("מכין את הביקורת ומטשטש את השם…");
    G().post("/api/calendar/story", { op: "review-layers", key: ST.key, review: r.id, cta: cta }).then(function (b) {
      change(function () {
        var fr2 = fr(), keep = fr2.layers.filter(function (l) { return l.group !== "review" && !(l.type === "image" && /social-proof\/reviews\//.test(l.src || "")); });
        b.layers.forEach(function (l) { l.id = uid("l"); });
        fr2.layers = b.layers.concat(keep); fr2.note = b.note;
        var img = b.layers.filter(function (l) { return l.type === "image"; })[0];
        ST.sel = img ? img.id : null; ST.pick = null;
      });
      G().toast("הביקורת בפריים. כדאי לבדוק שהשם מטושטש");
    }).catch(function (e) { G().toast("לא הצלחתי: " + e.message); });
  }

  /* ---------- the publish part: PNGs, stickers to add by hand, approval, Postiz, the set itself ---------- */
  function publishHtml(p) {
    var d = p.detail, s = ST.set, g = G(), sent = d.sent || {}, chans = s.channels || ["ig", "fb"];
    var h = '<dl class="cc-kv"><dt>ערוצים</dt><dd class="st-row">' + chkSet("ig", chans, "סטורי באינסטגרם") + chkSet("fb", chans, "סטורי בפייסבוק") + "</dd>" +
      '<dt>שעה</dt><dd><input class="lb-input st-time" type="time" data-sc="set" data-p="time" value="' + esc(s.time) + '"></dd>' +
      "<dt>תאריך</dt><dd>" + g.full(s.date) + ' <span class="cc-note">(גוררים ביומן כדי להזיז)</span></dd></dl>';
    var lint = (d.lint || []).map(function (x) { return '<div class="cc-flag' + (x.level === "error" ? " is-err" : "") + '">' + ic("info") + "פריים " + x.frame + ": " + esc(x.he) + "</div>"; }).join("");
    if (lint) h += '<div class="cc-box is-warn"><h4>' + ic("info") + "בדיקת הטקסט</h4>" + lint + "</div>";
    var png = d.png || [];
    h += '<div class="cc-box"><h4>' + ic("image") + "התמונות שעולות (1080 על 1920)</h4>" +
      (d.fresh ? "<p>מעודכנות לתוכן הנוכחי.</p>" : "<p>צריך ליצור אותן מחדש אחרי העריכה. הן נוצרות גם לבד לפני התזמון.</p>") +
      '<div class="st-pngs">' + s.frames.map(function (f, i) {
        return png[i] ? '<a href="' + esc(png[i]) + '" download="' + esc(ST.key + "-" + (i + 1)) + '.png" title="הורדת פריים ' + (i + 1) + '"><img src="' + esc(png[i]) + '" alt="פריים ' + (i + 1) + '" loading="lazy"><span class="lb-num">' + (i + 1) + "</span></a>" : '<span class="st-nopng lb-num">' + (i + 1) + "</span>";
      }).join("") + '</div><div class="lb-row"><button type="button" class="lb-btn secondary sm" data-s="render">' + ic("sync") + "ליצור את התמונות</button>" +
      (png.filter(Boolean).length ? '<button type="button" class="lb-btn ghost sm" data-s="dl-all">' + ic("download") + "להוריד את כולן</button>" : "") + "</div></div>";
    var st = [];
    s.frames.forEach(function (f, i) { f.layers.forEach(function (l) { if (l.type === "sticker") st.push({ i: i, l: l, manual: f.manual }); }); });
    if (st.length) h += '<div class="cc-box"><h4>' + ic("link") + "מדבקות של אינסטגרם</h4><p>פוסטיז לא שולח מדבקות (קישור, סקר, שאלה, ספירה לאחור), ואי אפשר להוסיף מדבקה לסטורי שכבר עלה. פריים עם מדבקה: או לסמן אותו \"עולה ידנית\" ולהעלות מהטלפון עם המדבקה, או לשלוח דרך פוסטיז בלי המדבקה.</p><ul class=\"st-stk\">" +
      st.map(function (x) {
        return "<li><b>פריים " + (x.i + 1) + "</b> · " + esc(STK[x.l.kind]) + ': <span translate="no">' + esc(x.l.label) + "</span>" + (x.l.url ? ' <button type="button" class="lb-btn ghost sm" data-s="copy" data-val="' + esc(x.l.url) + '">' + ic("copy") + "להעתיק קישור</button>" : "") + (x.manual ? ' <span class="lb-chip">ידני</span>' : "") + "</li>";
      }).join("") + "</ul></div>";
    if (sent.ids && sent.ids.length) {
      var t = sent.date ? new Date(sent.date) : null;
      h += '<div class="cc-box"><h4>' + ic("check-circle") + "בפוסטיז</h4><p>" + (sent.status === "draft" ? "טיוטה" : "מתוזמן") + (t ? " · " + g.full(g.iso(t)) + " " + String(t.getHours()).padStart(2, "0") + ":" + String(t.getMinutes()).padStart(2, "0") : "") +
        " · " + Object.keys(sent.frames || {}).length + " פריימים. שינוי שם רק באישור שלך, מתוך פוסטיז.</p></div>";
    }
    var manual = s.frames.filter(function (f) { return f.manual; }).length, auto = s.frames.length - manual;
    h += '<div class="cc-box"><h4>' + ic("check-circle") + "אישור</h4>" + (d.approved ? "<p>אישרת את הסט הזה. עריכה מבטלת את האישור.</p>" + '<div class="lb-row"><button type="button" class="lb-btn ghost sm" data-s="unapprove">לבטל את האישור</button></div>'
      : '<p>לאשר אחרי שעברת על כל הפריימים. בלי אישור אין תזמון.</p><div class="lb-row"><button type="button" class="lb-btn ok sm" data-s="approve">' + ic("check") + "מאשר את הסט</button></div>") + "</div>";
    if (!(auto && Object.keys(sent.frames || {}).length >= auto)) {
      var dt = s.date >= g.today() ? s.date : g.today();
      h += '<div class="cc-box"><h4>' + ic("send") + "לתזמן בפוסטיז</h4>" + (auto ? "<p>" + auto + " פריימים, כל אחד סטורי נפרד, דקה אחרי הקודם, ל" + (chans.indexOf("ig") >= 0 ? "אינסטגרם" : "") + (chans.length > 1 ? " ול" : "") + (chans.indexOf("fb") >= 0 ? "פייסבוק" : "") + "." + (manual ? " " + manual + " פריימים מסומנים להעלאה ידנית ולא יישלחו." : "") + "</p>" : "<p>כל הפריימים מסומנים להעלאה ידנית.</p>") +
        '<div class="lb-row"><label class="lb-field">תאריך<input class="lb-input" type="date" id="stPzD" value="' + dt + '"></label><label class="lb-field">שעה<input class="lb-input" type="time" id="stPzT" value="' + esc(s.time) + '"></label></div>' +
        '<div class="lb-row"><button type="button" class="lb-btn" data-s="send"' + (d.approved && auto ? "" : " disabled") + ">לתזמן</button>" +
        '<button type="button" class="lb-btn secondary" data-s="send-draft"' + (d.approved && auto ? "" : " disabled") + ">טיוטה בלבד</button></div><p class=\"cc-note\" id=\"stPzNote\">" + (d.approved ? "" : "נפתח אחרי האישור.") + "</p></div>";
    }
    h += '<div class="cc-box"><h4>' + ic("copy") + 'הסט</h4><div class="lb-row"><label class="lb-field">לשכפל ליום<input class="lb-input" type="date" id="stDupD"></label><button type="button" class="lb-btn secondary sm" data-s="dup-set">שכפול</button>' +
      '<span class="lb-spacer"></span><button type="button" class="lb-btn ghost sm" data-s="del-set">' + ic("close") + "להסיר את הסט</button></div>" +
      '<label class="st-f"><span>הערות לסט</span><textarea class="lb-textarea lb-editable" dir="rtl" rows="2" data-sc="set" data-p="notes" translate="no">' + esc(s.notes || "") + "</textarea></label></div>";
    return h;
  }
  function chkSet(c, chans, label) { return '<label class="st-chk"><input type="checkbox" data-s-chan="' + c + '"' + (chans.indexOf(c) >= 0 ? " checked" : "") + ">" + esc(label) + "</label>"; }

  /* ---------- edits ---------- */
  function setProp(sc, p, v, opt) {
    if (sc === "set") { ST.set[p] = v; dirty(); return; }
    change(function () {
      var f = fr();
      if (sc === "l") { var l = layer(); if (l) l[p] = v; }
      else if (sc === "bg") { f.bg = f.bg || {}; f.bg[p] = v; }
      else if (sc === "scrim") { f.scrim = f.scrim || {}; f.scrim[p] = v; }
      else if (sc === "f") f[p] = v;
    }, opt);
  }
  function select(id) { ST.sel = id; ST.pick = null; paintStage(); paintProps(); }
  function addLayer(l) { change(function () { l.id = uid("l"); fr().layers.push(l); ST.sel = l.id; }); }
  function pickSrc(src) {
    var m = ST.pick && ST.pick.mode;
    if (m === "bg") change(function () { var b = fr().bg = fr().bg || {}; b.src = src; b.x = 50; b.y = 50; b.zoom = 100; ST.pick = null; });
    else if (m === "img") change(function () { var l = layer(); if (l) l.src = src; ST.pick = null; });
    else if (m === "img-new") addLayer({ type: "image", src: src, x: 240, y: 620, w: 600, radius: 32, shadow: true });
    if (m === "img-new") ST.pick = null;
    paintProps();
  }
  function upload(file, mode) {
    if (!file || !/^image\/(png|jpeg|webp)$/.test(file.type)) { G().toast("רק png, jpg או webp"); return; }
    G().toast("מעלה את התמונה…");
    fetch("/api/calendar/story-upload?name=" + encodeURIComponent(file.name), { method: "POST", headers: { "X-LumeBook-Board": "1", "Content-Type": "application/octet-stream" }, body: file })
      .then(function (r) { return r.json().then(function (b) { if (!r.ok) throw new Error(b.he || b.error || r.status); return b; }); })
      .then(function (b) {
        (lib().art = lib().art || []).unshift({ src: b.src, name: file.name, group: "הועלו" });
        ST.pick = { mode: mode || "bg" }; pickSrc(b.src); G().toast("התמונה עלתה");
      }).catch(function (e) { G().toast("ההעלאה נכשלה: " + e.message); });
  }
  function moveFrame(from, to) {
    if (to < 0 || to >= ST.set.frames.length || from === to) return;
    change(function () { var f = ST.set.frames.splice(from, 1)[0]; ST.set.frames.splice(to, 0, f); ST.fi = to; });
  }
  function op(body, okMsg) {
    return flush().then(function () { return G().post("/api/calendar/story", Object.assign({ key: ST.key }, body)); })
      .then(function (b) { if (okMsg) G().toast(okMsg); G().load(true); return b; })
      .catch(function (e) { G().toast(e.message); throw e; });
  }
  var armed = null;
  function send(t, draft) {
    var dd = ($("#stPzD") || {}).value, tt = ($("#stPzT") || {}).value, note = $("#stPzNote");
    if (!dd || !tt) { G().toast("בחרו תאריך ושעה"); return; }
    var s = ST.set, chans = s.channels || ["ig", "fb"], sigA = dd + tt + draft;
    if (armed !== sigA) {
      armed = sigA;
      var where = (chans.indexOf("ig") >= 0 ? "סטורי באינסטגרם" : "") + (chans.length > 1 ? " ו" : "") + (chans.indexOf("fb") >= 0 ? "סטורי בפייסבוק" : "");
      note.textContent = (draft ? "טיוטה בפוסטיז, " : "לתזמן ל־" + G().full(dd) + " " + tt + ", ") + where + "? לחיצה נוספת שולחת.";
      t.dataset.label = t.dataset.label || t.textContent; t.textContent = "כן, לשלוח"; return;
    }
    armed = null; t.disabled = true; note.textContent = "שולח לפוסטיז…";
    op({ op: "send", date: dd, time: tt, draft: draft, confirmed: true }).then(function (b) { G().toast((b.sent || 0) + " פריימים נשלחו לפוסטיז"); })
      .catch(function () { t.disabled = false; t.textContent = t.dataset.label || "לתזמן"; note.textContent = ""; });
  }
  function copy(v, t) {
    var done = function () { G().toast("הועתק"); };
    if (navigator.clipboard) navigator.clipboard.writeText(v).then(done, function () { G().toast(v); }); else G().toast(v);
  }

  /* ---------- events (document level, only inside the open story) ---------- */
  function inStory(t) { return t && t.closest && (t.closest("#ccStory") || t.closest(".st-pub")) && ST; }
  document.addEventListener("click", function (ev) {
    var t = ev.target.closest("[data-s]"); if (!t || !inStory(t)) return;
    var a = t.dataset.s, f = fr();
    if (a === "frame") { var i = +t.dataset.i; if (i !== ST.fi) { ST.fi = i; ST.sel = null; ST.pick = null; paint(); } return; }
    if (a === "fprev" || a === "fnext") { var n = ST.fi + (a === "fnext" ? 1 : -1); if (n >= 0 && n < ST.set.frames.length) { ST.fi = n; ST.sel = null; paint(); } return; }
    if (a === "add-frame") { change(function () { var nf = { id: uid("f"), bg: clone(f.bg || {}), scrim: clone(f.scrim || {}), layers: [], note: "" }; ST.set.frames.splice(ST.fi + 1, 0, nf); ST.fi++; ST.sel = null; }); return; }
    if (a === "dup-frame") { change(function () { var nf = clone(f); nf.id = uid("f"); nf.layers.forEach(function (l) { l.id = uid("l"); }); ST.set.frames.splice(ST.fi + 1, 0, nf); ST.fi++; ST.sel = null; }); return; }
    if (a === "del-frame") { if (ST.set.frames.length < 2) { G().toast("סט צריך לפחות פריים אחד"); return; } change(function () { ST.set.frames.splice(ST.fi, 1); fix(); ST.sel = null; }); G().toast("הפריים נמחק", "ביטול", undo); return; }
    if (a === "fup") { moveFrame(ST.fi, ST.fi - 1); return; }
    if (a === "add-text") { addLayer({ type: "text", text: "טקסט חדש", x: 90, y: 820, w: 900, size: 96, weight: 900, color: "#FFFFFF", accent: "#F5C26B", align: "center", lh: 1.1, shadow: true }); return; }
    if (a === "add-shape") { addLayer({ type: "shape", x: 90, y: 700, w: 900, h: 420, fill: "#FFFFFF", radius: 56, op: 92 }); return; }
    if (a === "add-sticker") { addLayer({ type: "sticker", kind: "link", label: "מדבקת קישור", x: 140, y: 1300, w: 800, h: 150, url: series().link || "" }); return; }
    if (a === "add-image") { ST.pick = { mode: "img-new" }; ST.sel = null; paintStage(); paintProps(); return; }
    if (a === "add-review") { ST.pick = { mode: "review", q: "" }; paintProps(); return; }
    if (a === "img-change") { ST.pick = { mode: "img" }; paintProps(); return; }
    if (a === "bg-change") { ST.pick = { mode: "bg" }; ST.sel = null; paintProps(); return; }
    if (a === "bg-clear") { change(function () { delete fr().bg.src; }); return; }
    if (a === "pick-x") { ST.pick = null; paintProps(); return; }
    if (a === "pick-src") { pickSrc(t.dataset.val); return; }
    if (a === "pick-shots") { ST.pick.shots = !ST.pick.shots; loadReviews(); paintProps(); return; }
    if (a === "rv") { var r = (RV || []).filter(function (x) { return x.id === t.dataset.val; })[0]; if (r) applyReview(r); return; }
    if (a === "sel") { select(t.dataset.val); return; }
    if (a === "desel") { select(null); return; }
    if (a === "del-layer") { change(function () { var fl = fr().layers; fr().layers = fl.filter(function (l) { return l.id !== ST.sel; }); ST.sel = null; }); return; }
    if (a === "dup-layer") { var l0 = layer(); if (l0) { var c = clone(l0); c.y += 60; addLayer(c); } return; }
    if (a === "fwd" || a === "back") {
      change(function () { var ls = fr().layers, i = ls.indexOf(layer()), j = a === "fwd" ? i + 1 : i - 1; if (i < 0 || j < 0 || j >= ls.length) return; var x = ls[i]; ls[i] = ls[j]; ls[j] = x; }); return;
    }
    if (a === "blur-add") { change(function () { var l = layer(); if (l) (l.blurs = l.blurs || []).push({ x: 5, y: 5, w: 40, h: 20 }); if (l && !l.blur) l.blur = 16; }); return; }
    if (a === "blur-del") { change(function () { var l = layer(); if (l && l.blurs) l.blurs.splice(+t.dataset.i, 1); }); return; }
    if (a === "center") { change(function () { var l = layer(); if (l) l.x = Math.round(540 - l.w / 2); }); return; }
    if (a === "sw" || a === "setp") { var v = t.dataset.val; setProp(t.dataset.sc, t.dataset.p, /^\d+$/.test(v) ? +v : v); return; }
    if (a === "safe") { ST.safe = !ST.safe; t.setAttribute("aria-pressed", String(ST.safe)); paintStage(); return; }
    if (a === "undo") { undo(); return; }
    if (a === "redo") { redo(); return; }
    if (a === "copy") { copy(t.dataset.val, t); return; }
    if (a === "render") { t.disabled = true; t.innerHTML = '<span class="lb-spinner"></span> יוצר…'; op({ op: "render" }, "התמונות מוכנות").catch(function () { t.disabled = false; }); return; }
    if (a === "dl-all") { $$(".st-pngs a").forEach(function (x, i) { setTimeout(function () { x.click(); }, i * 350); }); return; }
    if (a === "approve") { op({ op: "approve" }, "הסט אושר"); return; }
    if (a === "unapprove") { op({ op: "unapprove" }, "האישור בוטל"); return; }
    if (a === "send" || a === "send-draft") { send(t, a === "send-draft"); return; }
    if (a === "dup-set") { var dd = ($("#stDupD") || {}).value; if (!dd) { G().toast("בחרו יום"); return; } op({ op: "dup", date: dd }, "שוכפל ל־" + G().full(dd)); return; }
    if (a === "del-set") {
      if (t.dataset.armed !== "1") { t.dataset.armed = "1"; t.textContent = "בטוח? לחיצה נוספת מסירה (נשמר בצד ב־series.json)"; return; }
      op({ op: "delete" }, "הסט הוסר").then(function () { ST = null; G().closeDlg(); }); return;
    }
  });
  document.addEventListener("input", function (ev) {
    var t = ev.target; if (!inStory(t)) return;
    if (t.id === "stRvQ") { ST.pick.q = t.value; var l = $("#stRvs"); if (l && RV) l.innerHTML = reviewList(); return; }
    var p = t.dataset.p; if (!p || t.type === "checkbox") return;
    var sc = t.dataset.sc || "l", v = t.dataset.t === "n" ? +t.value : t.value;
    if (t.dataset.t === "n" && !isFinite(v)) return;
    setProp(sc, p, v, { merge: sc + p + (ST.sel || ST.fi), props: false });
    $$('[data-sc="' + sc + '"][data-p="' + p + '"]', $("#stProps") || document).forEach(function (o) { if (o !== t && o.type !== "checkbox" && o.tagName === "INPUT") o.value = v; });
  });
  document.addEventListener("change", function (ev) {
    var t = ev.target; if (!inStory(t)) return;
    if (t.dataset.up) { upload(t.files && t.files[0], t.dataset.up === "img-new" ? "img-new" : t.dataset.up); return; }
    if (t.dataset.sChan) {
      var ch = (ST.set.channels || ["ig", "fb"]).filter(function (c) { return c !== t.dataset.sChan; });
      if (t.checked) ch.push(t.dataset.sChan);
      if (!ch.length) { t.checked = true; G().toast("לפחות ערוץ אחד"); return; }
      ST.set.channels = ["ig", "fb"].filter(function (c) { return ch.indexOf(c) >= 0; }); dirty(); return;
    }
    if (t.dataset.s === "pill") { change(function () { var l = layer(); if (!l) return; if (t.checked) { l.pill = "#FFFFFF"; l.pad = 48; l.pillr = 48; if (String(l.color).toUpperCase() === "#FFFFFF") l.color = "#2B1A5C"; l.shadow = false; } else { delete l.pill; } }); return; }
    if (t.type === "checkbox" && t.dataset.p) { setProp(t.dataset.sc || "l", t.dataset.p, t.checked); return; }
    if (t.tagName === "SELECT" && t.dataset.p) { setProp(t.dataset.sc || "l", t.dataset.p, t.value); paintProps(); return; }
    if (t.dataset.sc === "set" && t.dataset.p === "time") { G().load(true); }
  });

  /* drag a layer to move it, its side handles to change its width (and the bottom one the height of a shape or sticker) */
  document.addEventListener("pointerdown", function (ev) {
    var c = ev.target.closest && ev.target.closest("#stCanvas"); if (!c || !ST || ev.button !== 0) return;
    var hd = ev.target.closest(".st-hd"), el = ev.target.closest(".stf-l[data-lid]"), bz = ev.target.closest(".stf-blur");
    if (!hd && bz && el && el.dataset.lid === ST.sel) {   /* a blur box of the selected picture moves on its own */
      var lb = layer(), bi = +bz.dataset.bi;
      ST.drag = { mode: "bmove", bi: bi, x0: ev.clientX, y0: ev.clientY, b: clone(lb.blurs[bi]), k: kNow(), moved: false, el: el, W: el.offsetWidth, H: el.offsetHeight };
      try { c.setPointerCapture(ev.pointerId); } catch (x) {}
      ev.preventDefault(); return;
    }
    if (!hd && el && el.dataset.lid !== ST.sel) { ST.sel = el.dataset.lid; ST.pick = null; paintStage(); paintProps(); el = c.querySelector('[data-lid="' + ST.sel + '"]'); }
    else if (!hd && !el) { if (ST.sel || ST.pick) { ST.sel = null; ST.pick = null; paintStage(); paintProps(); } return; }
    var l = layer(); if (!l) return;
    ST.drag = { mode: hd ? hd.dataset.h : "move", x0: ev.clientX, y0: ev.clientY, l: clone(l), k: kNow(), moved: false, el: c.querySelector('[data-lid="' + l.id + '"]') };
    if (hd && hd.dataset.h === "b") { var be = ST.drag.el; ST.drag.bi = +hd.dataset.bi; ST.drag.b = clone(l.blurs[ST.drag.bi]); ST.drag.W = be.offsetWidth; ST.drag.H = be.offsetHeight; }
    try { c.setPointerCapture(ev.pointerId); } catch (x) {}
    ev.preventDefault();
  });
  document.addEventListener("pointermove", function (ev) {
    var d = ST && ST.drag; if (!d) return;
    var dx = (ev.clientX - d.x0) / d.k, dy = (ev.clientY - d.y0) / d.k;
    if (!d.moved && Math.abs(dx) + Math.abs(dy) < 4) return;
    if (!d.moved) { d.moved = true; pushHist(); }
    var l = layer(), g = $("#stGuide"); if (!l) return;
    if (d.mode === "bmove" || d.mode === "b") {
      var B = l.blurs[d.bi], px = dx / d.W * 100, py = dy / d.H * 100, r2 = function (v) { return Math.round(v * 100) / 100; };
      if (d.mode === "bmove") { B.x = r2(Math.min(100 - B.w, Math.max(0, d.b.x + px))); B.y = r2(Math.min(100 - B.h, Math.max(0, d.b.y + py))); }
      else { B.w = r2(Math.min(100 - B.x, Math.max(1, d.b.w + px))); B.h = r2(Math.min(100 - B.y, Math.max(1, d.b.h + py))); }
      blurPaint(d.el, B, d.bi); handles(d.el); return;
    }
    if (d.mode === "move") {
      var nx = d.l.x + dx, snap = Math.abs(nx + l.w / 2 - 540) < 16 && !ev.altKey;
      l.x = Math.round(snap ? 540 - l.w / 2 : nx); l.y = Math.round(d.l.y + dy);
      if (g) g.hidden = !snap;
    } else if (d.mode === "wr") { l.w = Math.max(40, Math.round(d.l.w + dx)); }
    else if (d.mode === "wl") { var w = Math.max(40, Math.round(d.l.w - dx)); l.x = d.l.x + d.l.w - w; l.w = w; }
    else if (d.mode === "h") { l.h = Math.max(20, Math.round(d.l.h + dy)); }
    if (d.el) { d.el.style.left = l.x + "px"; d.el.style.top = l.y + "px"; d.el.style.width = l.w + "px"; if (l.h != null && (l.type === "shape" || l.type === "sticker")) d.el.style.height = l.h + "px"; handles(d.el); }
  });
  document.addEventListener("pointerup", function () {
    var d = ST && ST.drag; if (!d) return;
    ST.drag = null; var g = $("#stGuide"); if (g) g.hidden = true;
    if (d.moved) { dirty(); paintStrip(); paintProps(); }
  });
  /* keys, before the calendar's own (which would move the month): only while a story is open and no field is being typed in */
  document.addEventListener("keydown", function (ev) {
    if (!ST || !document.getElementById("ccStory")) return;
    var tag = (ev.target.tagName || "").toLowerCase(), typing = tag === "input" || tag === "textarea" || tag === "select" || ev.target.isContentEditable, mod = ev.metaKey || ev.ctrlKey;
    var stop = function () { ev.preventDefault(); ev.stopPropagation(); };
    if (mod && (ev.key === "z" || ev.key === "Z") && !typing) { if (ev.shiftKey) redo(); else undo(); stop(); return; }
    if (typing) return;
    if (ev.key === "Escape" && (ST.sel || ST.pick)) { ST.sel = null; ST.pick = null; paintStage(); paintProps(); stop(); return; }
    if (!ST.sel) return;
    if (ev.key === "Delete" || ev.key === "Backspace") { change(function () { fr().layers = fr().layers.filter(function (l) { return l.id !== ST.sel; }); ST.sel = null; }); stop(); return; }
    if (mod && (ev.key === "d" || ev.key === "D")) { var c = clone(layer()); c.y += 60; addLayer(c); stop(); return; }
    var mv = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[ev.key];
    if (mv) { var s = ev.shiftKey ? 10 : 1; change(function () { var l = layer(); l.x += mv[0] * s; l.y += mv[1] * s; }, { merge: "nudge" + ST.sel }); stop(); }
  }, true);
  /* frames reorder by dragging them on the strip; a picture file dropped on the frame becomes its background (or the selected picture) */
  var dragFi = null;
  document.addEventListener("dragstart", function (ev) { var t = ev.target.closest && ev.target.closest(".st-th"); if (!t || !ST) return; dragFi = +t.dataset.i; ev.dataTransfer.effectAllowed = "move"; try { ev.dataTransfer.setData("text/plain", "frame"); } catch (x) {} });
  document.addEventListener("dragover", function (ev) {
    if (!ST || !document.getElementById("ccStory")) return;
    var th = ev.target.closest && ev.target.closest(".st-th"), stage = ev.target.closest && ev.target.closest("#stView");
    if (th && dragFi != null) { ev.preventDefault(); ev.stopPropagation(); return; }
    if (stage && ev.dataTransfer && Array.prototype.indexOf.call(ev.dataTransfer.types || [], "Files") >= 0) { ev.preventDefault(); ev.stopPropagation(); ev.dataTransfer.dropEffect = "copy"; stage.classList.add("is-drop"); }
  }, true);
  document.addEventListener("dragleave", function (ev) { var s = ev.target.closest && ev.target.closest("#stView"); if (s) s.classList.remove("is-drop"); });
  document.addEventListener("drop", function (ev) {
    if (!ST || !document.getElementById("ccStory")) return;
    var th = ev.target.closest && ev.target.closest(".st-th"), stage = ev.target.closest && ev.target.closest("#stView");
    if (th && dragFi != null) { ev.preventDefault(); ev.stopPropagation(); var to = +th.dataset.i, from = dragFi; dragFi = null; moveFrame(from, to); return; }
    if (stage && ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files.length) { ev.preventDefault(); ev.stopPropagation(); stage.classList.remove("is-drop"); upload(ev.dataTransfer.files[0], layer() && layer().type === "image" ? "img" : "bg"); }
  }, true);
  document.addEventListener("dragend", function () { dragFi = null; });
  addEventListener("resize", function () { if (ST && document.getElementById("ccStory")) fit(); });
  document.addEventListener("dblclick", function (ev) {
    var el = ev.target.closest && ev.target.closest("#stCanvas .stf-t"); if (!el || !ST) return;
    var ta = $('#stProps textarea[data-p="text"]'); if (ta) { ta.focus(); ta.select(); }
  });

  window.CCStory = { html: html, after: after, busy: busy };
})();
