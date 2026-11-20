/* The Black Friday and Hanukkah editor of the content calendar (20 Nov 2026; Yarin: "create 2 options for each for everyday of
   uploading / i want full editing capabilities"). A piece of kind "season" (tools/seasonal.py) is one posting day with two
   options, א and ב, each a carousel or a single picture. Everything of an option is edited here: every text of every slide,
   the layout, the pictures in their boxes and where each photo sits (drag it on the preview), slides added, copied, moved
   and removed, the format, who it talks to, the caption, the CTA, the Facebook text, the comment word and the links.
   The preview is the PNG renderer itself (seasonal_batch.preview_html), the lint runs on every change, the option saves by
   itself, and ליצור תמונות draws the PNGs. Click a text on the preview to jump to its field. ⌘Z / ⇧⌘Z undo and redo, ⌘D copies
   the slide. page.js hands its helpers over as window.CCPage. */
(function () {
  "use strict";
  var SE = null, LIVE = {};
  var LAY = {
    cover: { he: "שער", f: ["label", "headline", "body"] },
    point: { he: "נקודה", f: ["num", "label", "headline", "body"] },
    quote: { he: "ציטוט", f: ["label", "quote", "by", "quote_from"] },
    covers: { he: "כריכות", f: ["label", "headline", "body"] },
    cta: { he: "קריאה לפעולה", f: ["label", "headline", "body"] }
  };
  var SINGLE_F = ["headline", "no", "yes", "badge", "body"];
  var OFFER_F = ["label", "headline", "yes", "p1", "p2", "body"];   /* the Black Friday offer post (20 Nov 2026) */
  var MODELS = { "real-cover": "עומד, בזווית", "real-cover-2": "עומד, זווית שנייה", "real-flat": "שוכב על השולחן", "real-stack": "ערימה של שלושה",
    "real-open": "פתוח, מלמעלה", "real-standing": "פתוח, עומד", "real-standing-2": "פתוח, עומד (זווית שנייה)" };
  var STYLES = { s1: "1 · ספר מימין, סרט למעלה", s2: "2 · ספר משמאל, רשת", s3: "3 · לבן", s4: "4 · סרט למטה, פסים", s5: "5 · מדבקות עגולות", s6: "6 · כותרת במסגרת", s7: "7 · לבן, ספר משמאל" };
  function selHtml(attr, label, opts, val) {
    return '<label class="st-f"><span>' + label + '</span><select class="lb-select" ' + attr + ">" + Object.keys(opts).map(function (k) {
      return '<option value="' + k + '"' + (k === val ? " selected" : "") + ">" + esc(opts[k]) + "</option>"; }).join("") + "</select></label>";
  }
  var F_HE = { badge: "תג על התמונה ✓ (ריק = בלי תג)", page: "הטקסט בעמוד הימני של הספר הפתוח", num: "מספר בעיגול", label: "תווית", headline: "כותרת", body: "גוף", quote: "ציטוט", by: "מאת", quote_from: "מקור הציטוט (ההקלטה)",
    no: "✗ במקום (מה שכולן קונות)", yes: "✓ האפשרות הטובה יותר", p1: "תג מחיר ראשון (שורה קטנה, ואז המחיר)", p2: "תג מחיר שני", title: "שם פנימי", caption: "כיתוב לאינסטגרם", cta: "קריאה לפעולה",
    fb_text: "טקסט לפייסבוק", comment_word: "מילת תגובה", angle_he: "הזווית (פנימי)", _note: "הערה פנימית" };
  var ONE_LINE = { num: 1, label: 1, by: 1, quote_from: 1, comment_word: 1, title: 1 };
  function G() { return window.CCPage; }
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(t) { return G().esc(t); }
  function ic(n) { return G().ic(n); }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function lib() { return ((G().S.data || {}).season_lib) || []; }
  function libOf(k) { var l = lib(); for (var i = 0; i < l.length; i++) if (l[i].k === k) return l[i]; return null; }
  function single() { return SE.car.format === "single"; }
  function offer() { return single() && (SE.car.slides[0] || {}).layout === "offer"; }
  function sl() { return SE.car.slides[SE.si]; }
  function items(p) { return (p.detail || {}).items || []; }

  /* ---------- the working copy: one option at a time, kept across the page's refreshes ---------- */
  function optIdx(p) {
    var its = items(p);
    if (LIVE[p.id] != null && LIVE[p.id] < its.length) return LIVE[p.id];
    var i = its.findIndex(function (x) { return x.key === p.picked; });
    return i < 0 ? 0 : i;
  }
  function sync(p) {
    var it = items(p)[optIdx(p)];
    if (!it) { SE = null; return; }
    if (!SE || SE.key !== it.key) {
      SE = { key: it.key, pid: p.id, car: clone(it.car), base: JSON.stringify(it.car), si: 0, hist: [], fut: [], dirty: false, saving: false,
        issues: it.issues || [], fresh: it.fresh, it: it, p: p, seq: 0, pick: null, html: "" };
    } else {
      SE.p = p; SE.it = it;
      if (!SE.dirty && !SE.saving && JSON.stringify(it.car) !== SE.base) { SE.car = clone(it.car); SE.base = JSON.stringify(it.car); SE.issues = it.issues || []; }
      if (!SE.dirty && !SE.saving) SE.fresh = it.fresh;
    }
    if (SE.si >= SE.car.slides.length) SE.si = SE.car.slides.length - 1;
  }
  function busy() { var r = document.getElementById("ccSeason"); return !!(SE && r && (SE.dirty || SE.saving || SE.drag || SE.pick || r.contains(document.activeElement))); }

  function change(fn, opt) {
    opt = opt || {};
    var now = Date.now();
    if (!(opt.merge && SE.lastMerge === opt.merge && now - SE.lastAt < 1500)) { SE.hist.push(JSON.stringify(SE.car)); if (SE.hist.length > 100) SE.hist.shift(); SE.fut = []; }
    SE.lastMerge = opt.merge || null; SE.lastAt = now;
    fn();
    dirty(opt.light);
  }
  function dirty(light) {
    SE.dirty = true; clearTimeout(SE.saveT); SE.saveT = setTimeout(save, 800);
    G().setSave("wait", "לא נשמר עדיין…");
    if (light) { paintStrip(); preview(); } else paint();
  }
  function undo() { if (!SE.hist.length) return; SE.fut.push(JSON.stringify(SE.car)); SE.car = JSON.parse(SE.hist.pop()); fixSi(); dirty(); }
  function redo() { if (!SE.fut.length) return; SE.hist.push(JSON.stringify(SE.car)); SE.car = JSON.parse(SE.fut.pop()); fixSi(); dirty(); }
  function fixSi() { if (SE.si >= SE.car.slides.length) SE.si = SE.car.slides.length - 1; if (SE.si < 0) SE.si = 0; }

  function save() {
    if (!SE || SE.saving) return;
    var key = SE.key, body = clone(SE.car), sent = JSON.stringify(SE.car);
    SE.saving = true; G().setSave("wait", "שומר…");
    G().post("/api/calendar/season", { op: "save", key: key, car: body }).then(function (b) {
      if (!SE || SE.key !== key) return;
      SE.saving = false; SE.base = sent;
      if (JSON.stringify(SE.car) === sent) SE.dirty = false;
      else { clearTimeout(SE.saveT); SE.saveT = setTimeout(save, 400); }
      SE.issues = b.issues || SE.issues; if (b.fresh != null) SE.fresh = b.fresh;
      var errs = SE.issues.filter(function (x) { return x.level === "ERROR"; }).length;
      G().setSave(errs ? "error" : "", errs ? "נשמר · " + errs + " לתיקון" : "נשמר");
      paintIssues(); paintPub();
    }).catch(function (e) {
      if (!SE || SE.key !== key) return;
      SE.saving = false; G().setSave("error", "לא נשמר: " + e.message); G().toast("השמירה נכשלה: " + e.message);
    });
  }

  /* ---------- the preview: the PNG renderer, one slide, in a frame scaled to fit ---------- */
  function preview() {
    clearTimeout(SE.prevT);
    SE.prevT = setTimeout(function () {
      var key = SE.key, seq = ++SE.seq;
      G().post("/api/calendar/season", { op: "preview", key: key, car: clone(SE.car), n: SE.si + 1 }).then(function (b) {
        if (!SE || SE.key !== key || seq !== SE.seq) return;
        SE.html = b.html; SE.issues = b.issues || SE.issues; if (b.fresh != null) SE.fresh = b.fresh;
        var f = $("#seFrame"); if (f) f.srcdoc = b.html;
        paintIssues(); paintPub();
      }).catch(function (e) { var w = $("#seWarn"); if (w) { w.hidden = false; w.textContent = e.message; } });
    }, 220);
  }
  function wireFrame() {
    var f = $("#seFrame"); if (!f) return;
    f.onload = function () {
      var d = f.contentDocument; if (!d) return;
      var st = d.createElement("style");
      st.textContent = "[data-f]{cursor:text}[data-f]:hover{outline:6px dashed rgba(91,43,214,.7);outline-offset:8px}.frame[data-k]{cursor:grab}.frame.is-drag{cursor:grabbing}";
      d.head.appendChild(st);
      $$("[data-f]", d).forEach(function (el) {
        el.addEventListener("click", function (e) { e.preventDefault(); focusField(el.getAttribute("data-f")); });
      });
      $$(".frame[data-k] img", d).forEach(function (img) {
        var fr = img.parentNode, k = fr.getAttribute("data-k");
        img.addEventListener("pointerdown", function (e) { dragPos(e, img, fr, k); });
      });
    };
    if (SE.html) f.srcdoc = SE.html;
  }
  /* drag the main photo inside its box: changes the slide's pos (object-position) */
  function dragPos(e, img, fr, k) {
    var s = sl();
    if (k !== s.bg) { G().toast("רק התמונה הראשית של השקופית זזה בתוך הקופסה"); return; }
    e.preventDefault();
    var lp = libOf(k), cur = (s.pos || (lp && lp.pos) || "50% 40%").split(" ").map(function (x) { return parseFloat(x) || 50; });
    var r = img.getBoundingClientRect(), sx = e.clientX, sy = e.clientY, x0 = cur[0], y0 = cur[1], moved = false;
    SE.drag = true; fr.classList.add("is-drag");
    function mv(ev) {
      var nx = Math.max(0, Math.min(100, x0 - (ev.clientX - sx) / r.width * 100)), ny = Math.max(0, Math.min(100, y0 - (ev.clientY - sy) / r.height * 100));
      img.style.objectPosition = nx.toFixed(0) + "% " + ny.toFixed(0) + "%"; moved = [nx, ny];
    }
    function up() {
      img.removeEventListener("pointermove", mv); img.removeEventListener("pointerup", up); img.removeEventListener("pointercancel", up);
      SE.drag = false; fr.classList.remove("is-drag");
      if (moved) change(function () { sl().pos = moved[0].toFixed(0) + "% " + moved[1].toFixed(0) + "%"; });
    }
    img.setPointerCapture(e.pointerId);
    img.addEventListener("pointermove", mv); img.addEventListener("pointerup", up); img.addEventListener("pointercancel", up);
  }
  function fitStage() {
    var w = $("#seWrap"), f = $("#seFrame"); if (!w || !f) return;
    var k = w.clientWidth / 1080; f.style.transform = "scale(" + k + ")";
  }

  /* ---------- html ---------- */
  function html(p) {
    sync(p);
    if (!SE) return '<p class="cc-note">אין אפשרויות ליום הזה.</p>';
    var g = G(), its = items(p), oi = optIdx(p);
    var flags = (p.flags || []).filter(function (f) { return f.code !== "stale"; }).map(function (f) { return '<div class="cc-flag">' + ic("info") + esc(f.he) + "</div>"; }).join("");
    var head = '<div class="cc-ph"><div class="r1">' + g.kindIcon(p) + "<span>" + esc(g.kindLabel(p)) + "</span>" + g.stChip(p) + g.chans(p) +
      '<span class="lb-spacer"></span>' + g.saveState() + '<span class="lb-num">' + esc(p.time || "") + "</span></div>" +
      '<h3 translate="no">' + esc(SE.car.title || p.title) + "</h3>" + flags + "</div>";
    var opts = '<div class="opts se-opts"><span class="lb-segmented" role="group" aria-label="אפשרויות">' + its.map(function (it, i) {
      var c = it.car, lab = it.key.slice(-1) === "a" ? "א" : "ב";
      return '<button type="button" data-se="opt" data-i="' + i + '" aria-pressed="' + (i === oi) + '">' + lab + " · " + (c.format === "single" ? "תמונה אחת" : (c.slides || []).length + " שקופיות") +
        (c.addressee === "grandma" ? " · סבתא" : c.addressee === "mom" ? " · אמא" : c.addressee === "parents" ? " · הורים" : "") + (it.key === p.picked ? " ✓" : "") + "</button>";
    }).join("") + "</span>" + (p.picked === SE.key ? '<span class="lb-chip success">' + ic("check") + 'נבחרה</span><button type="button" class="lb-btn ghost sm" data-se="unpick">ביטול הבחירה</button>'
      : '<button type="button" class="lb-btn sm" data-se="pick">בוחר בזו</button>') + "</div>";
    return head + opts +
      '<section class="cc-part" data-part="edit"><h4 class="cc-part-h">' + ic("pencil") + "עריכה" +
      '<span class="lb-spacer"></span><button type="button" class="lb-btn ghost sm" data-se="undo" title="⌘Z">' + ic("undo") + 'ביטול</button><button type="button" class="lb-btn ghost sm" data-se="redo" title="⇧⌘Z">חזרה</button></h4>' +
      '<div class="st-ed se-ed" id="ccSeason" data-key="' + esc(SE.key) + '"><div class="st-strip se-strip" id="seStrip"></div>' +
      '<div class="st-stage"><div class="st-fnav" id="seNav"></div><div class="se-wrap" id="seWrap"><iframe id="seFrame" title="תצוגה של השקופית" tabindex="-1"></iframe></div>' +
      '<p class="se-hint">לוחצים על טקסט בתצוגה כדי לערוך אותו · גוררים את התמונה כדי להזיז אותה בקופסה · <b>**מילה**</b> מודגשת</p>' +
      '<p class="lb-callout danger" id="seWarn" hidden></p></div>' +
      '<div class="st-props" id="seProps"></div></div>' +
      '<div class="se-issues" id="seIssues"></div></section>' +
      '<section class="cc-part" data-part="text"><h4 class="cc-part-h">' + ic("instagram") + "כיתוב, פרטים וקישורים</h4>" + '<div class="se-meta" id="seMeta"></div></section>' +
      '<section class="cc-part" data-part="publish"><h4 class="cc-part-h">' + ic("check-circle") + "תמונות ואישור</h4>" + '<div id="sePub"></div></section>';
  }
  function after(p) { if (!SE) return; wire(); paint(); }

  function paint() { paintStrip(); paintNav(); paintProps(); paintMeta(); paintIssues(); paintPub(); preview(); }

  function slideLabel(s, i) {
    var t = (s.headline || s.quote || s.yes || "").replace(/\*\*/g, "").split("\n")[0];
    return '<b>' + (i + 1) + "</b> <span class=\"t\">" + esc(single() ? "תמונה אחת" : (LAY[s.layout] || {}).he || s.layout) + "</span><span class=\"x\">" + esc(t.slice(0, 26)) + "</span>";
  }
  function paintStrip() {
    var el = $("#seStrip"); if (!el) return;
    var imgs = SE.fresh ? (SE.it.images || []) : [];
    el.innerHTML = SE.car.slides.map(function (s, i) {
      var errs = SE.issues.filter(function (x) { return x.level === "ERROR" && x.slide === i + 1; }).length;
      return '<button type="button" class="se-th' + (i === SE.si ? " is-on" : "") + '" data-se="slide" data-i="' + i + '" draggable="' + (!single()) + '">' +
        (imgs[i] ? '<img src="' + esc(imgs[i]) + '" alt="">' : "") + '<span class="se-tl">' + slideLabel(s, i) + "</span>" + (errs ? '<span class="se-bad">' + errs + "</span>" : "") + "</button>";
    }).join("") + (single() ? "" : '<div class="st-strip-act">' +
      '<select class="lb-select sm" data-se="add" aria-label="שקופית חדשה"' + (SE.car.slides.length >= 10 ? " disabled" : "") + '><option value="">+ שקופית</option>' +
      Object.keys(LAY).map(function (k) { return '<option value="' + k + '">' + LAY[k].he + "</option>"; }).join("") + "</select>" +
      '<button type="button" class="lb-btn ghost sm" data-se="dup" title="⌘D"' + (SE.car.slides.length >= 10 ? " disabled" : "") + ">" + ic("copy") + "שכפול</button>" +
      '<button type="button" class="lb-btn ghost sm" data-se="up" title="להזיז אחורה">↑</button><button type="button" class="lb-btn ghost sm" data-se="down" title="להזיז קדימה">↓</button>' +
      '<button type="button" class="lb-btn ghost sm danger" data-se="del"' + (SE.car.slides.length <= 1 ? " disabled" : "") + ">" + "מחיקה</button></div>");
  }
  function paintNav() {
    var el = $("#seNav"); if (!el) return;
    var n = SE.car.slides.length;
    el.innerHTML = '<button type="button" class="lb-btn ghost sm" data-se="prev"' + (SE.si ? "" : " disabled") + ' aria-label="הקודמת">' + ic("arrow-right") + "</button>" +
      "<span>שקופית " + (SE.si + 1) + " מתוך " + n + "</span>" +
      '<button type="button" class="lb-btn ghost sm" data-se="next"' + (SE.si < n - 1 ? "" : " disabled") + ' aria-label="הבאה">' + ic("arrow-left") + "</button>";
  }
  function fieldHtml(name, val, slide) {
    var one = ONE_LINE[name], id = "seF-" + (slide ? "s-" : "t-") + name;
    var input = name === "num" ? '<input class="lb-input" type="number" min="1" max="9" id="' + id + '" data-se-f="' + name + '"' + (slide ? ' data-se-s="1"' : "") + ' value="' + esc(val == null ? "" : val) + '">'
      : one ? '<input class="lb-input" dir="rtl" id="' + id + '" data-se-f="' + name + '"' + (slide ? ' data-se-s="1"' : "") + ' value="' + esc(val || "") + '">'
      : '<textarea class="lb-textarea" dir="rtl" rows="' + Math.max(2, String(val || "").split("\n").length + 1) + '" id="' + id + '" data-se-f="' + name + '"' + (slide ? ' data-se-s="1"' : "") + ">" + esc(val || "") + "</textarea>";
    return '<label class="st-f" for="' + id + '"><span>' + esc(F_HE[name] || name) + "</span>" + input + "</label>";
  }
  function picHtml(slot, label, keys, max) {
    var tiles = keys.map(function (k, i) {
      var l = libOf(k);
      return '<span class="se-pic">' + (l ? '<img src="' + esc(l.url) + '" alt="" title="' + esc(l.what) + '">' : '<span class="se-miss">' + esc(k) + "</span>") +
        '<button type="button" class="lb-btn ghost sm" data-se="pic-swap" data-slot="' + slot + '" data-i="' + i + '">החלפה</button>' +
        '<button type="button" class="lb-btn ghost sm" data-se="pic-del" data-slot="' + slot + '" data-i="' + i + '" aria-label="הסרה">' + ic("close") + "</button></span>";
    }).join("");
    var add = keys.length < max ? '<button type="button" class="lb-btn secondary sm" data-se="pic-add" data-slot="' + slot + '">' + ic("image") + (keys.length ? "עוד קופסה" : "בחירת תמונה") + "</button>" : "";
    var picker = SE.pick && SE.pick.slot === slot ? pickerHtml() : "";
    return '<div class="st-f"><span>' + esc(label) + "</span><div class=\"se-pics\">" + tiles + add + "</div>" + picker + "</div>";
  }
  function pickerHtml() {
    var q = (SE.pick.q || "").trim(), covers = SE.pick.slot === "covers" || SE.pick.slot === "cover";
    var list = lib().filter(function (l) { return (covers ? l.cover : true) && (!q || (l.what + " " + l.who + " " + l.k).indexOf(q) >= 0); });
    return '<div class="se-picker"><div class="st-row"><input class="lb-input" dir="rtl" data-se-q="1" placeholder="חיפוש: ילד, ספר, סבתא…" value="' + esc(SE.pick.q || "") + '">' +
      '<button type="button" class="lb-btn ghost sm" data-se="pic-close">סגירה</button></div>' +
      '<div class="st-lib se-lib">' + list.map(function (l) {
        return '<button type="button" data-se="pic-choose" data-k="' + esc(l.k) + '" title="' + esc(l.what + (l.who ? " · " + l.who : "")) + '"><img src="' + esc(l.url) + '" alt="" loading="lazy"></button>';
      }).join("") + (list.length ? "" : '<p class="cc-note">לא נמצאה תמונה</p>') + "</div>" +
      '<p class="se-hint">רק תמונות אמיתיות עם אישור שימוש (assets.json של סבב הניסוי). תמונה חדשה מייצרים רק עם תקציב ואישור.</p></div>';
  }
  function paintProps() {
    var el = $("#seProps"); if (!el) return;
    var s = sl(), lay = single() ? null : LAY[s.layout] || LAY.point;
    var fs = offer() ? OFFER_F : single() ? SINGLE_F : lay.f;
    var h = '<div class="st-ph"><b>שקופית ' + (SE.si + 1) + (single() ? "" : " · " + esc((LAY[s.layout] || {}).he || "")) + "</b></div>";
    if (!single()) h += '<label class="st-f"><span>סוג השקופית</span><select class="lb-select" data-se-lay="1">' + Object.keys(LAY).map(function (k) {
      return '<option value="' + k + '"' + (k === s.layout ? " selected" : "") + ">" + LAY[k].he + "</option>"; }).join("") + "</select></label>";
    fs.forEach(function (f) { h += fieldHtml(f, s[f], true); });
    /* pictures: the main photo (bg, the one that moves), more boxes (pics), the book cover on a CTA, the covers of a covers slide */
    if (offer()) {
      h += selHtml('data-se-model="1"', "דגם הספר", MODELS, s.model || "real-cover");
      if (/open|standing/.test(s.model || "")) h += fieldHtml("page", s.page, true);
      h += picHtml("cover", "הספר (כריכה אחת)", s.cover ? [s.cover] : [], 1);
    }
    else if (s.layout === "covers" && !single()) h += picHtml("covers", "כריכות (עד 3)", s.covers || [], 3);
    else {
      var boxes = s.pics && s.pics.length ? s.pics : (s.bg ? [s.bg] : []);
      h += picHtml("pics", single() ? "התמונה ב ✓" : "תמונות בקופסאות (עד 3)", boxes, single() ? 1 : 3);
      if (s.layout === "cta" && !single()) h += picHtml("cover", "כריכת ספר בשקופית הסיום (במקום התמונה)", s.cover ? [s.cover] : [], 1);
    }
    if (s.bg) {
      var pos = (s.pos || ((libOf(s.bg) || {}).pos) || "50% 40%").split(" ").map(function (x) { return parseFloat(x) || 0; });
      h += '<div class="st-f"><span>מיקום התמונה בקופסה <small>(או גוררים על התצוגה)</small></span>' +
        '<div class="st-num"><input type="range" min="0" max="100" data-se-pos="0" value="' + pos[0] + '" aria-label="ימינה ושמאלה"><span class="lb-num">' + pos[0].toFixed(0) + "%</span></div>" +
        '<div class="st-num"><input type="range" min="0" max="100" data-se-pos="1" value="' + pos[1] + '" aria-label="למעלה ולמטה"><span class="lb-num">' + pos[1].toFixed(0) + "%</span></div>" +
        (s.pos ? '<button type="button" class="lb-btn ghost sm" data-se="pos-reset">חזרה למיקום של התמונה</button>' : "") + "</div>";
    }
    el.innerHTML = h;
  }
  function paintMeta() {
    var el = $("#seMeta"); if (!el) return;
    var c = SE.car, L = c.links || {};
    el.innerHTML = '<div class="se-grid">' +
      '<label class="st-f"><span>פורמט</span><select class="lb-select" data-se-top="format"><option value="carousel"' + (single() ? "" : " selected") + '>קרוסלה</option><option value="single"' + (single() ? " selected" : "") + ">תמונה אחת (במקום ✗, האפשרות הטובה ✓)</option></select></label>" +
      '<label class="st-f"><span>מדברת אל</span><select class="lb-select" data-se-top="addressee"><option value="grandma"' + (c.addressee === "grandma" ? " selected" : "") + '>סבתא</option><option value="mom"' + (c.addressee === "mom" ? " selected" : "") + '>אמא</option><option value="parents"' + (c.addressee === "parents" ? " selected" : "") + ">הורים (רבים)</option></select></label>" +
      (offer() ? selHtml('data-se-style="1"', "עיצוב", STYLES, c.style || "s1") : "") +
      fieldHtml("comment_word", c.comment_word) + fieldHtml("title", c.title) + "</div>" +
      fieldHtml("caption", c.caption) + fieldHtml("cta", c.cta) + fieldHtml("fb_text", c.fb_text) +
      '<div class="se-grid">' + ["dm", "facebook"].map(function (k) {
        return '<label class="st-f"><span>' + (k === "dm" ? "קישור להודעה (DM)" : "קישור בפוסט בפייסבוק") + '</span><input class="lb-input" dir="ltr" data-se-link="' + k + '" value="' + esc(L[k] || "") + '"></label>';
      }).join("") + "</div>" + fieldHtml("angle_he", c.angle_he) + fieldHtml("_note", c._note);
  }
  function paintIssues() {
    var el = $("#seIssues"); if (!el) return;
    var errs = SE.issues.filter(function (x) { return x.level === "ERROR"; }), warns = SE.issues.filter(function (x) { return x.level !== "ERROR"; });
    if (!SE.issues.length) { el.innerHTML = '<p class="lb-callout success">' + ic("check") + "עובר את כל הבדיקות של הטקסט</p>"; paintStrip(); return; }
    el.innerHTML = '<ul class="se-list">' + errs.concat(warns).slice(0, 14).map(function (x) {
      return '<li class="lb-callout ' + (x.level === "ERROR" ? "danger" : "warning") + '">' + (x.slide ? '<button type="button" class="lb-btn ghost sm" data-se="slide" data-i="' + (x.slide - 1) + '">שקופית ' + x.slide + "</button> " : "") + esc(x.message) + "</li>";
    }).join("") + "</ul>";
    paintStrip();
  }
  function paintPub() {
    var el = $("#sePub"); if (!el) return;
    var it = SE.it, r = it.render || {}, running = r.status === "running", errs = SE.issues.filter(function (x) { return x.level === "ERROR"; }).length;
    var fresh = SE.fresh && !SE.dirty, approved = it.approved && !SE.dirty;
    var imgs = (it.images || []).map(function (u, i) { return '<a href="' + esc(u) + '" target="_blank" rel="noopener"><img src="' + esc(u) + '" alt="שקופית ' + (i + 1) + '" loading="lazy"></a>'; }).join("");
    el.innerHTML = '<div class="st-row">' +
      '<button type="button" class="lb-btn ' + (fresh ? "secondary " : "") + 'sm" data-se="render"' + (running || SE.dirty || SE.saving ? " disabled" : "") + ">" + (running ? '<span class="lb-spinner" aria-hidden="true"></span> יוצר תמונות…' : ic("image") + (fresh ? "ליצור שוב" : "ליצור תמונות")) + "</button>" +
      (approved ? '<span class="lb-chip success">' + ic("check") + 'אושרה</span><button type="button" class="lb-btn ghost sm" data-se="unapprove">ביטול האישור</button>'
        : '<button type="button" class="lb-btn ok sm" data-se="approve"' + (fresh && !errs ? "" : " disabled") + ' title="' + (errs ? "יש מה לתקן בטקסט" : fresh ? "" : "קודם ליצור תמונות מהטקסט הנוכחי") + '">' + ic("check") + "מאשר את האפשרות</button>") +
      '<span class="cc-note">' + (fresh ? "התמונות תואמות לטקסט" : (it.images || []).length ? "התמונות מגרסה קודמת של הטקסט" : "עוד אין תמונות") + "</span></div>" +
      ((r.problems || []).length ? '<ul class="se-list">' + r.problems.map(function (t) { return '<li class="lb-callout warning">' + esc(t) + "</li>"; }).join("") + "</ul>" : "") +
      (imgs ? '<div class="se-pngs' + (fresh ? "" : " is-stale") + '">' + imgs + "</div>" : "") +
      '<p class="se-hint">התזמון בפוסטיז עוד לא מחובר לכאן: אחרי שתבחר ותאשר יום, אני שולח לפוסטיז רק באישור שלך.</p>';
  }

  /* ---------- events ---------- */
  function focusField(f) {
    var el = $('[data-se-f="' + f + '"][data-se-s]') || $('[data-se-f="' + f + '"]');
    if (el) { el.scrollIntoView({ block: "nearest", behavior: "smooth" }); el.focus(); if (el.select && f !== "body") try { el.setSelectionRange(el.value.length, el.value.length); } catch (x) {} }
  }
  function setPics(slot, list) {
    var s = sl();
    if (slot === "covers") { if (list.length) s.covers = list; else delete s.covers; return; }
    if (slot === "cover") { if (list.length) s.cover = list[0]; else delete s.cover; return; }
    var oldBg = s.bg;
    if (list.length > 1) { s.pics = list; s.bg = list[0]; }
    else { delete s.pics; if (list.length) s.bg = list[0]; else delete s.bg; }
    if (s.bg !== oldBg) delete s.pos;
  }
  function getPics(slot) {
    var s = sl();
    if (slot === "covers") return (s.covers || []).slice();
    if (slot === "cover") return s.cover ? [s.cover] : [];
    return s.pics && s.pics.length ? s.pics.slice() : (s.bg ? [s.bg] : []);
  }
  function newSlide(lay) {
    var s = { layout: lay };
    if (lay === "point") { s.num = 1; s.label = ""; s.headline = "כותרת"; s.body = ""; }
    else if (lay === "quote") { s.quote = "ציטוט"; s.by = ""; }
    else { s.headline = "כותרת"; s.body = ""; }
    var cur = sl(); if (lay !== "covers" && cur && cur.bg) s.bg = cur.bg;
    return s;
  }
  function onClick(e) {
    var t = e.target.closest("[data-se]"); if (!t || !$("#ccSeason") || !document.contains(t)) return;
    var a = t.dataset.se, i = +t.dataset.i;
    if (t.tagName === "SELECT") return;
    e.preventDefault(); e.stopPropagation();
    if (a === "opt") {
      var pid = SE.pid;
      if (SE.dirty) { clearTimeout(SE.saveT); save(); }
      LIVE[pid] = i;
      var go = function () { if (SE && SE.saving) return setTimeout(go, 150); SE = null; G().openPiece(pid); };
      go(); return;
    }
    if (a === "pick" || a === "unpick") {
      G().post("/api/calendar/season", { op: "pick", id: SE.pid, key: a === "pick" ? SE.key : null }).then(function () { G().toast(a === "pick" ? "נבחרה ליום הזה" : "הבחירה בוטלה"); G().load(true); }).catch(function (x) { G().toast(x.message); });
      return;
    }
    if (a === "undo") return undo();
    if (a === "redo") return redo();
    if (a === "slide") { SE.si = i; SE.pick = null; paint(); return; }
    if (a === "prev" && SE.si > 0) { SE.si--; SE.pick = null; paint(); return; }
    if (a === "next" && SE.si < SE.car.slides.length - 1) { SE.si++; SE.pick = null; paint(); return; }
    if (a === "dup") return change(function () { SE.car.slides.splice(SE.si + 1, 0, clone(sl())); SE.si++; });
    if (a === "del") { if (!confirm("למחוק את שקופית " + (SE.si + 1) + "? (אפשר לבטל עם ⌘Z)")) return; return change(function () { SE.car.slides.splice(SE.si, 1); fixSi(); }); }
    if (a === "up" && SE.si > 0) return change(function () { var x = SE.car.slides.splice(SE.si, 1)[0]; SE.si--; SE.car.slides.splice(SE.si, 0, x); });
    if (a === "down" && SE.si < SE.car.slides.length - 1) return change(function () { var x = SE.car.slides.splice(SE.si, 1)[0]; SE.si++; SE.car.slides.splice(SE.si, 0, x); });
    if (a === "pic-add") { SE.pick = { slot: t.dataset.slot, i: null, q: "" }; paintProps(); return; }
    if (a === "pic-swap") { SE.pick = { slot: t.dataset.slot, i: i, q: "" }; paintProps(); return; }
    if (a === "pic-close") { SE.pick = null; paintProps(); return; }
    if (a === "pic-del") return change(function () { var l = getPics(t.dataset.slot); l.splice(i, 1); setPics(t.dataset.slot, l); });
    if (a === "pic-choose") {
      var pk = SE.pick, k = t.dataset.k; SE.pick = null;
      return change(function () { var l = getPics(pk.slot); if (pk.i == null) l.push(k); else l[pk.i] = k; setPics(pk.slot, l); });
    }
    if (a === "pos-reset") return change(function () { delete sl().pos; });
    if (a === "render") {
      G().post("/api/calendar/season", { op: "render", key: SE.key }).then(function () { SE.it.render = { status: "running", problems: [] }; paintPub(); pollRender(SE.key); }).catch(function (x) { G().toast(x.message); });
      return;
    }
    if (a === "approve" || a === "unapprove") {
      G().post("/api/calendar/season", { op: a, key: SE.key }).then(function () { G().toast(a === "approve" ? "אושרה" : "האישור בוטל"); G().load(true); }).catch(function (x) { G().toast(x.message); });
    }
  }
  function SE_PID() { return SE ? SE.pid : null; }
  function pollRender(key) {
    var n = 0;
    (function tick() {
      setTimeout(function () {
        if (!SE || SE.key !== key || n++ > 60) return;
        G().load(true).then(function () {
          var p = G().S.byId[SE.pid]; if (!p) return;
          var it = items(p).find(function (x) { return x.key === key; });
          if (it && (it.render || {}).status === "running") tick();
          else if (it) { SE.it = it; SE.fresh = it.fresh; paintPub(); paintStrip(); G().toast((it.render || {}).status === "failed" ? "יצירת התמונות נכשלה" : "התמונות מוכנות"); }
        });
      }, 2500);
    })();
  }
  function onInput(e) {
    var t = e.target; if (!$("#ccSeason") || !t.closest || !t.closest(".cc-part")) return;
    if (t.dataset.seQ) { SE.pick.q = t.value; var pos = t.selectionStart; paintProps(); var q = $("[data-se-q]"); if (q) { q.focus(); q.setSelectionRange(pos, pos); } return; }
    if (t.dataset.seF) {
      var f = t.dataset.seF, slide = !!t.dataset.seS, v = t.value;
      change(function () {
        var o = slide ? sl() : SE.car;
        if (f === "num") { if (v === "") delete o.num; else o.num = Math.max(1, Math.min(9, parseInt(v, 10) || 1)); }
        else if (v === "" && slide) delete o[f]; else o[f] = v;
      }, { merge: (slide ? SE.si + "." : "") + f, light: true });
      if (!slide && f === "title") { var h3 = $("#ccDlgB .cc-ph h3"); if (h3) h3.textContent = v; }
      return;
    }
    if (t.dataset.seLink) { var k = t.dataset.seLink; change(function () { SE.car.links = SE.car.links || {}; SE.car.links[k] = t.value.trim(); }, { merge: "link." + k, light: true }); return; }
    if (t.dataset.sePos != null) {
      var ax = +t.dataset.sePos, s = sl(), p0 = (s.pos || ((libOf(s.bg) || {}).pos) || "50% 40%").split(" ").map(function (x) { return parseFloat(x) || 0; });
      p0[ax] = +t.value; t.nextElementSibling.textContent = t.value + "%";
      change(function () { sl().pos = p0[0].toFixed(0) + "% " + p0[1].toFixed(0) + "%"; }, { merge: "pos", light: true });
    }
  }
  function onChange(e) {
    var t = e.target; if (!$("#ccSeason") || !t.closest || !t.closest(".cc-part")) return;
    if (t.dataset.se === "add" && t.value) { var lay = t.value; t.value = ""; change(function () { SE.car.slides.splice(SE.si + 1, 0, newSlide(lay)); SE.si++; }); return; }
    if (t.dataset.seLay) { var v = t.value; change(function () { var s = sl(); s.layout = v; if (v === "point" && s.num == null) s.num = 1; if (v === "quote" && !s.quote) s.quote = (s.headline || "").replace(/\*\*/g, ""); }); return; }
    if (t.dataset.seModel) { var mv = t.value; change(function () { sl().model = mv; }); return; }
    if (t.dataset.seStyle) { var sv = t.value; change(function () { SE.car.style = sv; }); return; }
    if (t.dataset.seTop === "addressee") { change(function () { SE.car.addressee = t.value; }); return; }
    if (t.dataset.seTop === "format") {
      var to = t.value;
      if (to === "single" && SE.car.slides.length > 1 && !confirm("תמונה אחת שומרת רק את השקופית הנוכחית, כקריאה לפעולה עם ✗ ו ✓. להמשיך? (אפשר לבטל עם ⌘Z)")) { t.value = "carousel"; return; }
      change(function () {
        if (to === "single") {
          var s = sl(); SE.car.format = "single";
          SE.car.slides = [{ layout: "cta", headline: s.headline || s.quote || "", no: s.no || "", yes: s.yes || "", body: s.body || "", bg: s.bg, pos: s.pos }];
          if (!SE.car.slides[0].bg) delete SE.car.slides[0].bg; if (!SE.car.slides[0].pos) delete SE.car.slides[0].pos; SE.si = 0;
        } else {
          delete SE.car.format;
          var o = SE.car.slides[0];
          SE.car.slides = [{ layout: "cover", headline: o.headline || "", body: "", bg: o.bg }, { layout: "cta", headline: o.yes || "", body: o.body || "", bg: o.bg }];
          SE.car.slides.forEach(function (x) { if (!x.bg) delete x.bg; });
        }
      });
    }
  }
  function onKey(e) {
    var r = $("#ccSeason"); if (!r || !SE) return;
    var inEd = r.contains(e.target) || (e.target.closest && e.target.closest('#ccDlgB [data-part="text"]'));
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName);
    if (inEd && e.key !== "Escape") e.stopPropagation();
    if (!(e.metaKey || e.ctrlKey) || typing) return;
    if (!inEd && !r.closest("#ccDlgB")) return;
    if (e.key.toLowerCase() === "z") { e.preventDefault(); if (e.shiftKey) redo(); else undo(); }
    else if (e.key.toLowerCase() === "d" && !single() && SE.car.slides.length < 10) { e.preventDefault(); change(function () { SE.car.slides.splice(SE.si + 1, 0, clone(sl())); SE.si++; }); }
  }
  /* drag a slide on the strip to reorder */
  function onDrag(e) {
    var th = e.target.closest && e.target.closest(".se-th"); if (!th || !$("#ccSeason")) return;
    if (e.type === "dragstart") { SE.dragI = +th.dataset.i; e.dataTransfer.effectAllowed = "move"; try { e.dataTransfer.setData("text/plain", "slide"); } catch (x) {} }
    else if (e.type === "dragover") { e.preventDefault(); th.classList.add("is-over"); }
    else if (e.type === "dragleave") th.classList.remove("is-over");
    else if (e.type === "drop") {
      e.preventDefault(); th.classList.remove("is-over");
      var from = SE.dragI, to = +th.dataset.i; SE.dragI = null;
      if (from == null || from === to) return;
      change(function () { var x = SE.car.slides.splice(from, 1)[0]; SE.car.slides.splice(to, 0, x); SE.si = to; });
    }
  }
  var wired = false;
  var RO = window.ResizeObserver ? new ResizeObserver(function () { fitStage(); }) : null;
  function wire() {
    wireFrame(); fitStage();
    var w = $("#seWrap"); if (RO && w) { RO.disconnect(); RO.observe(w); }
    if (wired) return; wired = true;
    document.addEventListener("click", onClick, true);
    document.addEventListener("input", onInput, true);
    document.addEventListener("change", onChange, true);
    document.addEventListener("keydown", onKey, true);
    ["dragstart", "dragover", "dragleave", "drop"].forEach(function (ev) { document.addEventListener(ev, onDrag, true); });
    addEventListener("resize", fitStage);
    addEventListener("beforeunload", function (e) { if (SE && (SE.dirty || SE.saving)) { save(); e.preventDefault(); e.returnValue = ""; } });
  }

  window.CCSeason = { html: html, after: after, busy: busy };
})();
