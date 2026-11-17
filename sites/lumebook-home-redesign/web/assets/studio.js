/* LumeBook home redesign (demo): the creation studio and a pretend account.
   Nothing here leaves the browser: accounts, photos and books live in this browser's localStorage,
   photos are shrunk in the page, passwords are kept only as a salted SHA-256 hash, and an "order"
   is a confirmation screen with no payment step. Every start button opens the studio; the real
   store flow stays one click away at the top of the studio. */
(function () {
  'use strict';
  var DATA = JSON.parse(document.getElementById('studio-data').textContent);
  var root = document.documentElement;
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- small helpers ---------- */
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function $(sel, el) { return (el || document).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function ils(n) { return n + '&nbsp;₪'; }
  function load(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function icon(name) { var t = document.getElementById('ic-' + name); return t ? t.innerHTML : ''; }
  function uid() { return Math.random().toString(36).slice(2, 8); }
  function openDialog(d) { if (!d.open) { if (d.showModal) d.showModal(); else d.setAttribute('open', ''); } }
  function closeDialog(d) { if (d.open) { if (d.close) d.close(); else d.removeAttribute('open'); } }
  function toast(msg) {
    var t = document.createElement('div');
    t.className = 'toast'; t.setAttribute('role', 'status'); t.textContent = msg;
    (document.querySelector('dialog[open]') || document.body).appendChild(t);
    requestAnimationFrame(function () { t.classList.add('show'); });
    setTimeout(function () { t.classList.remove('show'); setTimeout(function () { t.remove(); }, 400); }, 2600);
  }
  /* shrink a picked photo in the page; nothing is uploaded */
  function shrink(file, max, q) {
    return new Promise(function (res, rej) {
      if (!/^image\//.test(file.type) && !/\.(heic|heif)$/i.test(file.name)) { rej(new Error('type')); return; }
      var url = URL.createObjectURL(file), im = new Image();
      im.onload = function () {
        var s = Math.min(1, max / Math.max(im.naturalWidth, im.naturalHeight));
        var c = document.createElement('canvas');
        c.width = Math.round(im.naturalWidth * s); c.height = Math.round(im.naturalHeight * s);
        c.getContext('2d').drawImage(im, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        res(c.toDataURL('image/jpeg', q || 0.8));
      };
      im.onerror = function () { URL.revokeObjectURL(url); rej(new Error('read')); };
      im.src = url;
    });
  }

  /* ================================================================ account */
  var USERS = 'lbh-users', SESSION = 'lbh-session';
  function users() { return load(USERS, {}); }
  function me() { var e = load(SESSION, null); var u = e && users()[e]; return u ? { email: e, name: u.name } : null; }
  function booksKey(email) { return 'lbh-books:' + email; }
  function myBooks() { var m = me(); return m ? load(booksKey(m.email), []) : []; }
  function putBook(b) {
    var m = me(); if (!m) return false;
    var list = load(booksKey(m.email), []).filter(function (x) { return x.id !== b.id; });
    list.unshift(b);
    if (!save(booksKey(m.email), list)) {            // storage full: keep the book without its photos
      b = JSON.parse(JSON.stringify(b)); if (b.state) { b.state.photos = []; b.state.photo = null; } b.thumb = b.thumb && b.thumb.indexOf('data:') === 0 ? null : b.thumb;
      list[0] = b; return save(booksKey(m.email), list);
    }
    return true;
  }
  async function hash(email, pw) {
    var bytes = new TextEncoder().encode('lumebook-demo:' + email.toLowerCase() + ':' + pw);
    if (window.crypto && crypto.subtle) {
      var buf = await crypto.subtle.digest('SHA-256', bytes);
      return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
    }
    var h = 0; for (var i = 0; i < bytes.length; i++) { h = (h * 31 + bytes[i]) | 0; } return 'x' + h;
  }

  var auth = document.getElementById('auth');
  var afterAuth = null;
  function authMode(mode) {
    setTimeout(function () { if (window.LBH_glide) window.LBH_glide(auth); }, 0);
    $$('#auth [role="tab"]').forEach(function (t) { var on = t.dataset.mode === mode; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1; });
    $('#auth-up').hidden = mode !== 'up';
    $('#auth-in').hidden = mode !== 'in';
    $$('#auth .err').forEach(function (e) { e.textContent = ''; });
    $$('#auth .inp').forEach(function (i) { i.removeAttribute('aria-invalid'); });
    var f = $(mode === 'up' ? '#auth-up .inp' : '#auth-in .inp'); if (f) setTimeout(function () { f.focus(); }, 30);
  }
  function openAuth(mode, why, then) {
    afterAuth = then || null;
    $('#auth-why').textContent = why || 'החשבון שומר את הספרים שיצרתם, כדי לחזור אליהם ולהזמין.';
    authMode(mode || 'up');
    openDialog(auth);
    if (window.LBH_glide) setTimeout(function () { window.LBH_glide(auth); }, 30);
  }
  function fieldErr(input, msg) { input.setAttribute('aria-invalid', 'true'); var e = document.getElementById(input.getAttribute('aria-describedby')); if (e) e.textContent = msg; return false; }
  function okEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }
  function signedIn(user, fresh) {
    save(SESSION, user.email);
    closeDialog(auth);
    renderAccount();
    toast(fresh ? 'נוצר חשבון. שלום ' + user.name + '!' : 'שלום ' + user.name + ', התחברתם');
    var f = afterAuth; afterAuth = null; if (f) f();
  }
  if (auth) {
    $$('#auth [role="tab"]').forEach(function (t) { t.addEventListener('click', function () { authMode(t.dataset.mode); }); });
    $('#auth-up').addEventListener('submit', async function (e) {
      e.preventDefault();
      var name = $('#up-name'), email = $('#up-email'), pw = $('#up-pw');
      $$('#auth-up .err').forEach(function (x) { x.textContent = ''; }); $$('#auth-up .inp').forEach(function (i) { i.removeAttribute('aria-invalid'); });
      var ok = true, em = email.value.trim().toLowerCase();
      if (name.value.trim().length < 2) ok = fieldErr(name, 'מה השם?') && ok;
      if (!okEmail(em)) ok = fieldErr(email, 'כתובת המייל לא נראית תקינה') && ok;
      else if (users()[em]) ok = fieldErr(email, 'יש כבר חשבון עם המייל הזה. אפשר להתחבר') && ok;
      if (pw.value.length < 8) ok = fieldErr(pw, 'לפחות 8 תווים') && ok;
      if (!ok) { var bad = $('#auth-up [aria-invalid="true"]'); if (bad) bad.focus(); return; }
      var all = users();
      all[em] = { name: name.value.trim(), pw: await hash(em, pw.value), since: new Date().toISOString().slice(0, 10) };
      save(USERS, all);
      e.target.reset();
      signedIn({ email: em, name: all[em].name }, true);
    });
    $('#auth-in').addEventListener('submit', async function (e) {
      e.preventDefault();
      var email = $('#in-email'), pw = $('#in-pw'), em = email.value.trim().toLowerCase();
      $$('#auth-in .err').forEach(function (x) { x.textContent = ''; }); $$('#auth-in .inp').forEach(function (i) { i.removeAttribute('aria-invalid'); });
      var u = users()[em];
      if (!okEmail(em)) { fieldErr(email, 'כתובת המייל לא נראית תקינה'); email.focus(); return; }
      if (!u) { fieldErr(email, 'אין חשבון עם המייל הזה בדפדפן. אפשר להירשם'); email.focus(); return; }
      if (u.pw !== await hash(em, pw.value)) { fieldErr(pw, 'הסיסמה לא נכונה'); pw.focus(); return; }
      e.target.reset();
      signedIn({ email: em, name: u.name }, false);
    });
    $('#auth-forgot').addEventListener('click', function () {
      $('#in-pw-err').textContent = 'בדמו אין שחזור סיסמה. אפשר ליצור חשבון חדש.';
    });
    auth.addEventListener('close', function () { afterAuth = null; });
  }

  /* header and drawer */
  function renderAccount() {
    var u = me();
    $$('.acct-btn').forEach(function (b) {
      b.classList.toggle('in', !!u);
      b.setAttribute('aria-label', u ? 'החשבון של ' + u.name : 'התחברות או הרשמה');
      var av = b.querySelector('.av'); if (av) av.textContent = u ? u.name.trim().charAt(0) : '';
    });
    var who = $('.acct-pop .who'); if (who && u) who.innerHTML = '<b>' + esc(u.name) + '</b><span class="ltr">' + esc(u.email) + '</span>';
    var dr = $('#drawer-acct');
    if (dr) dr.innerHTML = u
      ? '<p class="small" style="margin:8px 0">מחוברים בתור ' + esc(u.name) + '</p><button type="button" class="link-row" data-mybooks>הספרים שלי</button><button type="button" class="link-row" data-logout>התנתקות</button>'
      : '<button type="button" class="link-row" data-auth="in">התחברות</button><button type="button" class="link-row" data-auth="up">הרשמה</button>';
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.acct-btn');
    if (b) {
      if (!me()) { openAuth('in'); return; }
      var pop = b.parentElement.querySelector('.acct-pop');
      var open = !pop.classList.contains('open');
      pop.classList.toggle('open', open); b.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) { var f = pop.querySelector('button'); if (f) f.focus(); }
      return;
    }
    if (!e.target.closest('.acct')) $$('.acct-pop.open').forEach(function (p) { p.classList.remove('open'); });
    var a = e.target.closest('[data-auth]');
    if (a) { e.preventDefault(); openAuth(a.dataset.auth); return; }
    if (e.target.closest('[data-mybooks]')) { e.preventDefault(); $$('.acct-pop').forEach(function (p) { p.classList.remove('open'); }); openMyBooks(); return; }
    if (e.target.closest('[data-logout]')) {
      e.preventDefault(); save(SESSION, null); try { localStorage.removeItem(SESSION); } catch (x) {}
      $$('.acct-pop').forEach(function (p) { p.classList.remove('open'); });
      renderAccount(); toast('התנתקתם');
    }
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') $$('.acct-pop.open').forEach(function (p) { p.classList.remove('open'); var b = p.parentElement.querySelector('.acct-btn'); if (b) b.focus(); }); });

  /* my books */
  var mb = document.getElementById('mybooks');
  var KIND = { kids: 'ספר ילדים', gift: 'ספר מתנה', albums: 'אלבום תמונות' };
  function openMyBooks() {
    var list = myBooks(), box = $('#mb-list');
    if (!list.length) {
      box.innerHTML = '<div class="mb-empty"><p>עוד אין כאן ספרים.</p><p class="small">ספר שתיצרו נשמר כאן.</p></div>';
    } else {
      box.innerHTML = '<ul class="mb-list">' + list.map(function (b) {
        var pic = b.thumb ? '<img src="' + esc(b.thumb) + '" alt="">' : '<span class="mb-ph"></span>';
        var st = b.status === 'ordered' ? 'הזמנה לדוגמה ' + esc(b.order) : 'טיוטה';
        var btn = b.status === 'ordered' ? '<button class="btn btn-quiet btn-sm" type="button" data-del="' + b.id + '">מחיקה</button>'
          : '<button class="btn btn-primary btn-sm" type="button" data-resume="' + b.id + '">להמשיך</button>';
        return '<li class="mb-item">' + pic + '<div><b>' + esc(b.title) + '</b><span>' + KIND[b.kind] + ' · ' + st + ' · ' + esc(b.date) + '</span></div>' + btn + '</li>';
      }).join('') + '</ul>';
    }
    openDialog(mb);
  }
  if (mb) mb.addEventListener('click', function (e) {
    var r = e.target.closest('[data-resume]'), d = e.target.closest('[data-del]');
    if (r) { var b = myBooks().filter(function (x) { return x.id === r.dataset.resume; })[0]; closeDialog(mb); if (b) openStudio(b.kind, b); }
    if (d) { var m = me(); save(booksKey(m.email), myBooks().filter(function (x) { return x.id !== d.dataset.del; })); openMyBooks(); }
  });
  $$('.sheet').forEach(function (d) {
    d.addEventListener('click', function (e) { if (e.target === d || e.target.closest('[data-close]')) closeDialog(d); });
  });

  /* ================================================================ studio */
  var st = document.getElementById('studio');
  var S = null;            // the open session: {kind, step, state, id}
  var FLOWS = {};
  var DEL = DATA.delivery;

  function deliveryOptions(name, cur, onlyHome) {
    return '<div class="order" role="radiogroup" aria-label="משלוח">' + DEL.filter(function (d) { return !onlyHome || d.k === 'home'; }).map(function (d) {
      return '<label class="opt"><input type="radio" name="' + name + '" value="' + d.k + '"' + (cur === d.k ? ' checked' : '') + '>' +
        '<div><b>' + d.name + '</b><span>' + d.time + '</span></div><span class="pr">' + (d.price ? ils(d.price) : 'חינם') + '</span></label>';
    }).join('') + '</div>';
  }
  function delPrice(k) { var d = DEL.filter(function (x) { return x.k === k; })[0]; return d ? d.price : 0; }
  function bill(rows, total) {
    return '<div class="receipt"><ul class="bill">' + rows.map(function (r) { return '<li><span>' + r[0] + '</span><span>' + r[1] + '</span></li>'; }).join('') +
      '<li class="tot"><span>סה״כ</span><span>' + ils(total) + '</span></li></ul></div>';
  }
  function drop(id, multiple, label, sub) {
    return '<label class="drop" id="' + id + '" tabindex="0"><span>' + icon('photo') + '</span><b>' + label + '</b><span>' + sub + '</span>' +
      '<input class="sr-only" type="file" accept="image/*,.heic,.heif"' + (multiple ? ' multiple' : '') + '></label>';
  }
  function wireDrop(id, onFiles) {
    var d = document.getElementById(id); if (!d) return;
    var inp = d.querySelector('input');
    inp.addEventListener('change', function () { if (inp.files.length) onFiles(Array.prototype.slice.call(inp.files)); inp.value = ''; });
    d.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); inp.click(); } });
    ['dragenter', 'dragover'].forEach(function (t) { d.addEventListener(t, function (e) { e.preventDefault(); d.classList.add('over'); }); });
    ['dragleave', 'drop'].forEach(function (t) { d.addEventListener(t, function (e) { e.preventDefault(); d.classList.remove('over'); }); });
    d.addEventListener('drop', function (e) { var f = Array.prototype.slice.call(e.dataTransfer.files || []); if (f.length) onFiles(f); });
  }
  function choices(name, opts, cur, multi) {
    return '<div class="choices" role="' + (multi ? 'group' : 'radiogroup') + '" data-choice="' + name + '"' + (multi ? ' data-multi' : '') + '>' + opts.map(function (o) {
      var on = multi ? (cur || []).indexOf(o) > -1 : cur === o;
      return '<button type="button" class="choice" role="' + (multi ? 'checkbox' : 'radio') + '" aria-checked="' + (on ? 'true' : 'false') + '" data-v="' + esc(o) + '">' + esc(o) + '</button>';
    }).join('') + '</div>';
  }
  function bindChoices(state) {
    $$('[data-choice]', st).forEach(function (g) {
      g.addEventListener('click', function (e) {
        var b = e.target.closest('.choice'); if (!b) return;
        var key = g.dataset.choice, v = b.dataset.v;
        if (g.hasAttribute('data-multi')) {
          var arr = state[key] || []; var i = arr.indexOf(v);
          if (i > -1) arr.splice(i, 1); else arr.push(v);
          state[key] = arr; b.setAttribute('aria-checked', i > -1 ? 'false' : 'true');
        } else {
          state[key] = v; $$('.choice', g).forEach(function (x) { x.setAttribute('aria-checked', x === b ? 'true' : 'false'); });
        }
        refreshFoot();
      });
    });
  }
  function bindInputs(state) {
    $$('[data-k]', st).forEach(function (inp) {
      var ev = inp.tagName === 'SELECT' ? 'change' : 'input';
      inp.addEventListener(ev, function () { state[inp.dataset.k] = inp.value; inp.removeAttribute('aria-invalid'); if (inp.dataset.live) renderPreviewPart(); refreshFoot(); });
    });
  }

  /* ---------- book preview (shared) ---------- */
  var PV = { pages: [], i: 0 };
  function previewBlock(pages, note) {
    PV.pages = pages; PV.i = Math.min(PV.i, pages.length - 1);
    return '<div class="pv"><div class="pv-stage" id="pv-stage" aria-live="polite"></div>' +
      '<div class="pv-nav"><button class="icon-btn" type="button" id="pv-prev" aria-label="העמוד הקודם">' + icon('chev-r') + '</button>' +
      '<span class="pv-dots" id="pv-dots"></span>' +
      '<button class="icon-btn" type="button" id="pv-next" aria-label="העמוד הבא">' + icon('chev-l') + '</button></div>' +
      '<div class="pv-strip" id="pv-strip" role="group" aria-label="עמודים"></div>' + (note ? '<p class="st-note">' + note + '</p>' : '') + '</div>';
  }
  function drawPreview(dir) {
    var stage = $('#pv-stage'); if (!stage) return;
    var p = PV.pages[PV.i];
    stage.innerHTML = p.html;
    if (dir) { var pg = stage.firstElementChild; if (pg) pg.classList.add(dir > 0 ? 'turn-fwd' : 'turn-back'); }
    $('#pv-dots').textContent = (PV.i + 1) + ' מתוך ' + PV.pages.length;
    $('#pv-prev').disabled = PV.i === 0; $('#pv-next').disabled = PV.i === PV.pages.length - 1;
    $('#pv-strip').innerHTML = PV.pages.map(function (q, k) {
      return '<button type="button" aria-label="' + esc(q.label) + '" aria-current="' + (k === PV.i ? 'true' : 'false') + '" data-pg="' + k + '">' + (q.thumb ? '<img src="' + esc(q.thumb) + '" alt="">' : esc(q.short || (k + 1))) + '</button>';
    }).join('');
  }
  function bindPreview() {
    if (!$('#pv-stage')) return;
    $('#pv-prev').addEventListener('click', function () { if (PV.i > 0) { PV.i--; drawPreview(-1); } });
    $('#pv-next').addEventListener('click', function () { if (PV.i < PV.pages.length - 1) { PV.i++; drawPreview(1); } });
    $('#pv-strip').addEventListener('click', function (e) { var b = e.target.closest('[data-pg]'); if (b) { var to = +b.dataset.pg, d = to > PV.i ? 1 : to < PV.i ? -1 : 0; PV.i = to; drawPreview(d); } });
    $('#pv-stage').addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft' && PV.i < PV.pages.length - 1) { PV.i++; drawPreview(1); }
      if (e.key === 'ArrowRight' && PV.i > 0) { PV.i--; drawPreview(-1); }
    });
    $('#pv-stage').tabIndex = 0;
    drawPreview();
  }
  var renderPreviewPart = function () {};

  /* ================= kids ================= */
  FLOWS.kids = {
    title: 'ספר ילדים',
    steps: ['הגיבור', 'הסיפור', 'התמונה', 'תצוגה מקדימה', 'הזמנה'],
    init: function () { return { name: '', age: '', gender: '', lang: 'עברית', book: null, photo: null, ded: '', pack: '1', del: 'home' }; },
    book: function (s) { return DATA.kids.books.filter(function (b) { return b.id === s.book; })[0]; },
    g: function (s) { return s.gender === 'בת' ? 'girl' : 'boy'; },
    fill: function (line, s) { return esc(line).split('{{child_name}}').join('<mark>' + esc(s.name) + '</mark>'); },
    plain: function (line, s) { return String(line).split('{{child_name}}').join(s.name); },
    render: function (s, step) {
      var K = DATA.kids;
      if (step === 0) return '<div class="st-grid"><div><h3>בואו נכיר את הגיבור שלכם</h3><p class="sub">השם יופיע בטקסט, והילד או הילדה בכל האיורים.</p>' +
        '<div class="field"><label for="k-name">מה השם? <span class="hint">כפי שיופיע בספר, שם פרטי בלבד</span></label><input class="inp" id="k-name" data-k="name" autocomplete="off" maxlength="16" dir="rtl" value="' + esc(s.name) + '" placeholder="למשל: אריאל" aria-describedby="k-name-err"><span class="err" id="k-name-err"></span></div>' +
        '<div class="st-two"><div class="field"><label for="k-age">גיל</label><select class="inp" id="k-age" data-k="age"><option value="">בוחרים גיל</option>' + K.ages.map(function (a) { return '<option' + (String(s.age) === String(a) ? ' selected' : '') + '>' + a + '</option>'; }).join('') + '</select></div>' +
        '<div class="field"><span>בן או בת</span>' + choices('gender', ['בן', 'בת'], s.gender) + '</div></div>' +
        '<div class="field"><span>שפת הספר</span>' + choices('lang', K.langs, s.lang) + '</div></div>' +
        '<div class="pv-stage" aria-hidden="true"><img src="' + esc(K.heroImg) + '" alt="" style="max-width:380px;width:100%;filter:var(--book-shadow)"></div></div>';
      if (step === 1) return '<h3>בוחרים סיפור ל' + esc(s.name || 'גיבור') + '</h3><p class="sub">סיפורים לרגעים של הילדות. אפשר להחליף אחר כך.</p><div class="book-grid" role="radiogroup" aria-label="סיפור">' +
        K.books.map(function (b) {
          return '<button type="button" class="book-opt" role="radio" aria-checked="' + (s.book === b.id ? 'true' : 'false') + '" data-book="' + b.id + '"><span class="book"><img src="' + esc(b.cover[FLOWS.kids.g(s)]) + '" alt="" loading="lazy" width="300" height="300"></span><b>' + esc(b.title) + '</b><span>' + (b.ages ? 'לגילאי ' + esc(b.ages) : '&nbsp;') + '</span></button>';
        }).join('') + '</div>';
      if (step === 2) return '<div class="st-grid"><div><h3>תמונה של ' + esc(s.name) + '</h3><p class="sub">תמונה ברורה ומוארת של הפנים. תמיד אפשר לנסות תמונה אחרת.</p>' +
        drop('k-drop', false, 'בוחרים תמונה או גוררים לכאן', 'JPG, PNG או HEIC') +
        '<p class="st-note">בדמו התמונה מוקטנת בדפדפן ולא נשלחת לשום מקום.</p></div><div id="k-face" style="text-align:center">' +
        (s.photo ? '<img class="face" src="' + s.photo + '" alt="התמונה שבחרתם"><p class="small">אפשר לבחור תמונה אחרת</p>' : '<p class="small" style="margin-top:40px">עוד לא נבחרה תמונה</p>') + '</div></div>';
      if (step === 3) {
        var b = FLOWS.kids.book(s), g = FLOWS.kids.g(s), pg = b.pages[g];
        var title = FLOWS.kids.plain(pg[0][0] || b.title, s);
        var pages = [{ label: 'כריכה', thumb: b.cover[g], html: '<div class="pv-page pv-cover"><img class="art" src="' + esc(b.cover[g]) + '" alt="">' +
            (s.photo ? '<img class="me" src="' + s.photo + '" alt="התמונה של ' + esc(s.name) + '"><span class="me-tag">התמונה שלכם</span>' : '') +
            '<div class="ttl">' + FLOWS.kids.fill(pg[0][0] || b.title, s) + '</div></div>' },
          { label: 'הקדשה', short: 'הקדשה', html: '<div class="pv-page"><div class="pv-text pv-ded"><small>הקדשה</small><p id="pv-ded-text">' + (s.ded ? esc(s.ded) : 'כאן תופיע ההקדשה שלכם') + '</p></div></div>' }];
        [1, 2, 3].forEach(function (n) {
          var lines = pg[n] || []; if (!lines.length) return;
          pages.push({ label: 'עמוד ' + n, short: 'עמ׳ ' + n, html: '<div class="pv-page"><div class="pv-pic"><img src="' + esc(b.cover[g]) + '" alt="" style="object-position:50% ' + (20 + n * 20) + '%"><span>כאן האיור עם ' + esc(s.name) + '</span></div><div class="pv-text">' + lines.map(function (l) { return '<div>' + FLOWS.kids.fill(l, s) + '</div>'; }).join('') + '</div><span class="pv-num">' + n + '</span></div>' });
        });
        PV.i = 0;
        return '<div class="st-grid"><div>' + previewBlock(pages, 'הטקסט הוא הטקסט האמיתי של הספר עם השם שלכם. בדמו האיורים לקוחים מהכריכה; בספר האמיתי ' + esc(s.name) + ' מופיע בכל האיורים.') + '</div>' +
          '<div><h3>' + esc(title) + '</h3><p class="sub">' + esc(b.title) + (b.ages ? ' · לגילאי ' + esc(b.ages) : '') + ' · ' + esc(s.lang) + '</p>' +
          (s.lang !== 'עברית' ? '<p class="st-note">בדמו התצוגה בעברית. באתר האמיתי הספר נכתב ב' + esc(s.lang) + '.</p>' : '') +
          '<div class="field"><label for="k-ded">הקדשה <span class="hint">לא חובה, מודפסת בעמוד הראשון</span></label><textarea class="inp" id="k-ded" data-k="ded" data-live="1" dir="rtl" maxlength="220" placeholder="לאריאל שלנו, באהבה גדולה">' + esc(s.ded) + '</textarea></div>' +
          '<ul class="facts">' + ['22×22 ס״מ, כריכה רכה, 24 עמודים צבעוניים', 'עמוד הקדשה', 'עותק דיגיטלי במתנה, במייל תוך דקות'].map(function (t) { return '<li>' + icon('check') + '<span>' + t + '</span></li>'; }).join('') + '</ul></div></div>';
      }
      if (step === 4) {
        var tiers = DATA.kids.tiers;
        var cur = tiers.filter(function (t) { return String(t.n) === s.pack; })[0] || tiers[0];
        var del = cur.n === 1 ? s.del : 'home';
        var ship = cur.n === 1 ? delPrice(del) : 0;
        var total = cur.price + ship;
        var rows = [[cur.n === 1 ? 'ספר מודפס' : cur.n + ' ספרים, משלוח כלול', ils(cur.price)]];
        if (cur.n === 1) rows.push(['משלוח', ship ? ils(ship) : 'חינם']);
        rows.push(['עותק דיגיטלי', 'במתנה']);
        return '<div class="st-grid"><div><h3>הזמנה</h3><p class="sub">' + (cur.n > 1 ? 'את שאר הספרים בוחרים באתר אחרי ההזמנה הראשונה.' : 'הספר נשלח להדפסה רק אחרי שמאשרים.') + '</p>' +
          '<div class="order" role="radiogroup" aria-label="כמה ספרים">' + tiers.map(function (t) {
            return '<label class="opt"><input type="radio" name="k-pack" value="' + t.n + '"' + (String(t.n) === s.pack ? ' checked' : '') + '><div><b>' + (t.n === 1 ? 'ספר אחד' : t.n + ' ספרים') + '</b><span>' + (t.n === 1 ? ils(119) + ' ומשלוח' : 'משלוח מהיר עד הבית כלול') + '</span></div><span class="pr">' + (t.was ? '<s class="small">' + ils(t.was) + '</s> ' : '') + ils(t.price) + '</span></label>';
          }).join('') + '</div>' +
          (cur.n === 1 ? '<h4 style="margin:22px 0 10px;font-size:17px">משלוח</h4>' + deliveryOptions('k-del', del) : '') + '</div>' +
          '<div><h4 style="margin-bottom:10px;font-size:17px">סיכום</h4>' + bill(rows, total) + '<p class="st-note">בדמו אין תשלום ושום דבר לא נשלח. באתר האמיתי התשלום מאובטח.</p></div></div>';
      }
    },
    bind: function (s, step) {
      if (step === 1) $$('.book-opt', st).forEach(function (b) { b.addEventListener('click', function () { s.book = +b.dataset.book; $$('.book-opt', st).forEach(function (x) { x.setAttribute('aria-checked', x === b ? 'true' : 'false'); }); refreshFoot(); }); });
      if (step === 2) wireDrop('k-drop', function (files) {
        shrink(files[0], 360, 0.82).then(function (d) { s.photo = d; $('#k-face').innerHTML = '<img class="face" src="' + d + '" alt="התמונה שבחרתם"><p class="small">אפשר לבחור תמונה אחרת</p>'; refreshFoot(); })
          .catch(function () { toast('לא הצלחנו לקרוא את התמונה. אפשר לנסות אחרת'); });
      });
      if (step === 3) { bindPreview(); renderPreviewPart = function () { var t = $('#pv-ded-text'); if (t) t.textContent = s.ded || 'כאן תופיע ההקדשה שלכם'; PV.pages[1].html = '<div class="pv-page"><div class="pv-text pv-ded"><small>הקדשה</small><p id="pv-ded-text">' + (s.ded ? esc(s.ded) : 'כאן תופיע ההקדשה שלכם') + '</p></div></div>'; }; }
      if (step === 4) {
        $$('input[name="k-pack"]', st).forEach(function (r) { r.addEventListener('change', function () { s.pack = r.value; go(4, true); }); });
        $$('input[name="k-del"]', st).forEach(function (r) { r.addEventListener('change', function () { s.del = r.value; go(4, true); }); });
      }
    },
    valid: function (s, step) {
      if (step === 0) return s.name.trim().length >= 2 && s.age && s.gender && s.lang;
      if (step === 1) return !!s.book;
      return true;
    },
    hint: function (s, step) {
      if (step === 0) return !s.name.trim() ? 'מה השם?' : !s.age ? 'בוחרים גיל' : !s.gender ? 'בן או בת?' : '';
      if (step === 1) return s.book ? '' : 'בוחרים סיפור';
      if (step === 2) return s.photo ? '' : 'אפשר להמשיך גם בלי תמונה בדמו';
      return '';
    },
    making: 2,
    total: function (s) { var t = DATA.kids.tiers.filter(function (x) { return String(x.n) === s.pack; })[0] || DATA.kids.tiers[0]; return t.price + (t.n === 1 ? delPrice(s.del) : 0); },
    summary: function (s) { var b = FLOWS.kids.book(s); return b ? FLOWS.kids.plain(b.pages[FLOWS.kids.g(s)][0][0] || b.title, s) : 'ספר ילדים'; },
    thumb: function (s) { var b = FLOWS.kids.book(s); return b ? b.cover[FLOWS.kids.g(s)] : null; }
  };

  /* ================= gift ================= */
  FLOWS.gift = {
    title: 'ספר מתנה',
    steps: ['למי הספר', 'ספרו עליהם', 'כריכה', 'תצוגה מקדימה', 'הזמנה'],
    init: function () { return { reason: '', people: 'אדם אחד', who: '', age: '', from: '', rel: '', traits: [], about: '', memory: '', ded: '', title: '', photo: null, photoMode: 'איור מהתמונה', addons: [], del: 'home' }; },
    bookTitle: function (s) { return s.title.trim() || 'הספר של ' + s.who.trim(); },
    render: function (s, step) {
      var G = DATA.gift;
      if (step === 0) return '<div class="st-grid"><div><h3>למי הספר?</h3><p class="sub">ספר מתנה עם הסיפורים והבדיחות שרק אתם מכירים.</p>' +
        '<div class="field"><span>לאיזה אירוע?</span>' + choices('reason', G.reasons, s.reason) + '</div>' +
        '<div class="field"><span>על מי הספר?</span>' + choices('people', ['אדם אחד', 'זוג'], s.people) + '</div>' +
        '<div class="st-two"><div class="field"><label for="g-who">' + (s.people === 'זוג' ? 'השמות שלהם' : 'השם') + '</label><input class="inp" id="g-who" data-k="who" dir="rtl" maxlength="40" value="' + esc(s.who) + '" placeholder="' + (s.people === 'זוג' ? 'למשל: סבא משה וסבתא רותי' : 'למשל: תמר') + '"></div>' +
        '<div class="field"><label for="g-age">גיל <span class="hint">לא חובה</span></label><input class="inp" id="g-age" data-k="age" inputmode="numeric" maxlength="3" value="' + esc(s.age) + '"></div></div>' +
        '<div class="field"><label for="g-from">ממי המתנה?</label><input class="inp" id="g-from" data-k="from" dir="rtl" maxlength="40" value="' + esc(s.from) + '" placeholder="למשל: מיכל"></div>' +
        '<div class="field"><span>מה הקשר ביניכם?</span>' + choices('rel', G.rels, s.rel) + '</div></div>' +
        '<div class="pv-stage" aria-hidden="true"><img src="' + esc(G.heroImg) + '" alt="" style="width:100%;max-width:440px;border-radius:12px"></div></div>';
      if (step === 1) return '<h3>ספרו עליהם</h3><p class="sub">לא צריך לדעת לכתוב. עונים במילים פשוטות, ואפשר לדלג.</p><div class="st-grid"><div>' +
        '<div class="field"><span>מה מתאר אותם? <span class="hint">אפשר כמה</span></span>' + choices('traits', G.traits, s.traits, true) + '</div>' +
        '<div class="field"><label for="g-about">מי ' + (s.people === 'זוג' ? 'הם' : esc(s.who || 'הם')) + '? מה אוהבים, מה תמיד אומרים?</label><textarea class="inp" id="g-about" data-k="about" dir="rtl" maxlength="900" placeholder="' + esc(G.aboutHint) + '">' + esc(s.about) + '</textarea></div></div><div>' +
        '<div class="field"><label for="g-mem">זיכרון משותף <span class="hint">לא חובה</span></label><textarea class="inp" id="g-mem" data-k="memory" dir="rtl" maxlength="900" placeholder="' + esc(G.memoryHint) + '">' + esc(s.memory) + '</textarea></div>' +
        '<div class="field"><label for="g-ded">הקדשה <span class="hint">מודפסת בתחילת הספר</span></label><textarea class="inp" id="g-ded" data-k="ded" dir="rtl" maxlength="260" placeholder="' + esc(G.dedHint) + '">' + esc(s.ded) + '</textarea></div></div></div>';
      if (step === 2) return '<div class="st-grid"><div><h3>הכריכה</h3><p class="sub">תמונה משותפת או תמונה שלהם על הכריכה. לא חובה.</p>' +
        drop('g-drop', false, 'בוחרים תמונה או גוררים לכאן', 'JPG, PNG או HEIC') +
        '<div class="field" style="margin-top:16px"><span>איך להשתמש בתמונה?</span>' + choices('photoMode', ['איור מהתמונה', 'תמונה כמו שהיא'], s.photoMode) + '</div>' +
        '<div class="field"><label for="g-title">שם לספר <span class="hint">לא חובה. בלי שם, הספר יקבל שם משלו</span></label><input class="inp" id="g-title" data-k="title" dir="rtl" maxlength="40" value="' + esc(s.title) + '" placeholder="למשל: רק נעצור לרגע"></div></div>' +
        '<div id="g-face" style="text-align:center">' + (s.photo ? '<img class="face" src="' + s.photo + '" alt="התמונה שבחרתם">' : '<p class="small" style="margin-top:40px">עוד לא נבחרה תמונה</p>') + '</div></div>';
      if (step === 3) {
        var t = FLOWS.gift.bookTitle(s);
        var cover = '<div class="pv-page"><div class="pv-mono">' + (s.photo ? '<img src="' + s.photo + '" alt="">' : esc((s.who.trim() || '?').charAt(0))) + '</div><div class="pv-gtitle">' + esc(t) + '</div><div class="pv-gsub">' + esc(s.reason || 'מתנה') + (s.from ? ' · מ' + esc(s.from) : '') + '</div></div>';
        var ded = '<div class="pv-page"><div class="pv-text pv-ded"><small>הקדשה</small><p>' + (s.ded ? esc(s.ded) : 'כאן תופיע ההקדשה שלכם') + '</p></div></div>';
        var toc = '<div class="pv-page pv-plain"><ol class="pv-toc"><b>כיוון לפרקים</b>' + DATA.gift.chapterHints.map(function (c, k) { return '<li><span>' + (k + 1) + '. ' + esc(c.split('{who}').join(s.who.trim() || '')) + '</span><span>' + (k * 4 + 3) + '</span></li>'; }).join('') + '</ol></div>';
        var ch1 = '<div class="pv-page"><div class="pv-text" style="text-align:start;justify-content:flex-start;padding-top:12%"><b style="font-size:20px;margin-bottom:10px">פרק ראשון</b><p style="color:var(--paper-ink-2);font-size:15px">באתר האמיתי כאן מופיע הפרק הראשון, שנכתב מהפרטים ששיתפתם. מה שסיפרתם:</p>' +
          '<p style="margin-top:10px">״' + esc((s.memory || s.about).slice(0, 240)) + ((s.memory || s.about).length > 240 ? '…' : '') + '״</p></div></div>';
        PV.i = 0;
        return '<div class="st-grid"><div>' + previewBlock([{ label: 'כריכה', short: 'כריכה', html: cover }, { label: 'הקדשה', short: 'הקדשה', html: ded }, { label: 'כיוון לפרקים', short: 'פרקים', html: toc }, { label: 'פרק ראשון', short: 'פרק 1', html: ch1 }],
          'כך נראית התצוגה המקדימה: כריכה, כיוון לפרקים ופרק ראשון. בדמו הפרקים הם דוגמה; באתר האמיתי הם נכתבים מהפרטים שלכם, והספר המלא נכתב אחרי התשלום.') + '</div>' +
          '<div><h3>' + esc(t) + '</h3><p class="sub">ספר ' + (s.people === 'זוג' ? 'על ' + esc(s.who) : 'על ' + esc(s.who)) + (s.rel ? ' · ' + esc(s.rel) : '') + '</p>' +
          '<ul class="facts">' + ['כריכה אישית ושם לספר', 'ספר אישי על ' + (s.people === 'זוג' ? 'הזוג' : 'האדם') + ' שלכם', 'הקדשה אישית בתחילת הספר', 'ספר מודפס, ומשלוח לפי ההזמנה'].map(function (x) { return '<li>' + icon('check') + '<span>' + esc(x) + '</span></li>'; }).join('') + '</ul>' +
          '<p class="st-note"><a href="' + esc(DATA.gift.sample) + '" target="_blank" rel="noopener">לקריאת ספר דוגמה מלא באתר</a></p></div></div>';
      }
      if (step === 4) {
        var rows = [['הספר המודפס, מחיר השקה', '<s class="small">' + ils(DATA.gift.list) + '</s> ' + ils(DATA.gift.price)]];
        DATA.gift.addons.forEach(function (a) { if (s.addons.indexOf(a.k) > -1) rows.push([a.name, ils(a.price)]); });
        var ship = delPrice(s.del); rows.push(['משלוח', ship ? ils(ship) : 'חינם']);
        return '<div class="st-grid"><div><h3>הזמנה</h3><p class="sub">אפשר להוסיף תוספות. כל המחירים מוצגים לפני התשלום.</p><div class="order">' +
          DATA.gift.addons.map(function (a) { return '<label class="opt"><input type="checkbox" value="' + a.k + '"' + (s.addons.indexOf(a.k) > -1 ? ' checked' : '') + ' data-addon><div><b>' + a.name + '</b><span>' + a.desc + '</span></div><span class="pr">+' + ils(a.price) + '</span></label>'; }).join('') +
          '</div><h4 style="margin:22px 0 10px;font-size:17px">משלוח</h4>' + deliveryOptions('g-del', s.del) + '</div>' +
          '<div><h4 style="margin-bottom:10px;font-size:17px">סיכום</h4>' + bill(rows, FLOWS.gift.total(s)) + '<p class="st-note">בדמו אין תשלום ושום דבר לא נשלח.</p></div></div>';
      }
    },
    bind: function (s, step) {
      if (step === 0) $$('[data-choice="people"] .choice', st).forEach(function (b) { b.addEventListener('click', function () { setTimeout(function () { go(0, true); }, 0); }); });
      if (step === 2) wireDrop('g-drop', function (files) {
        shrink(files[0], 480, 0.82).then(function (d) { s.photo = d; $('#g-face').innerHTML = '<img class="face" src="' + d + '" alt="התמונה שבחרתם">'; })
          .catch(function () { toast('לא הצלחנו לקרוא את התמונה. אפשר לנסות אחרת'); });
      });
      if (step === 3) bindPreview();
      if (step === 4) {
        $$('[data-addon]', st).forEach(function (c) { c.addEventListener('change', function () { var i = s.addons.indexOf(c.value); if (c.checked && i < 0) s.addons.push(c.value); if (!c.checked && i > -1) s.addons.splice(i, 1); go(4, true); }); });
        $$('input[name="g-del"]', st).forEach(function (r) { r.addEventListener('change', function () { s.del = r.value; go(4, true); }); });
      }
    },
    valid: function (s, step) {
      if (step === 0) return !!s.reason && s.who.trim().length >= 2 && s.from.trim().length >= 2 && !!s.rel;
      if (step === 1) return s.about.trim().length >= 10;
      return true;
    },
    hint: function (s, step) {
      if (step === 0) return !s.reason ? 'בוחרים אירוע' : s.who.trim().length < 2 ? 'על מי הספר?' : s.from.trim().length < 2 ? 'ממי המתנה?' : !s.rel ? 'מה הקשר?' : '';
      if (step === 1) return s.about.trim().length < 10 ? 'כמה מילים עליהם' : '';
      return '';
    },
    making: 2,
    total: function (s) { var t = DATA.gift.price + delPrice(s.del); DATA.gift.addons.forEach(function (a) { if (s.addons.indexOf(a.k) > -1) t += a.price; }); return t; },
    summary: function (s) { return FLOWS.gift.bookTitle(s); },
    thumb: function (s) { return s.photo || DATA.gift.thumb; }
  };

  /* ================= albums ================= */
  FLOWS.albums = {
    title: 'אלבום תמונות',
    steps: ['התמונות', 'מה חשוב לכם', 'האלבום', 'הזמנה'],
    init: function () { return { src: 'device', link: '', photos: [], sample: false, note: '', title: '', cover: 0, copies: 1, del: 'home' }; },
    pages: function (s) {
      var ph = s.photos.slice(), out = [], pattern = [1, 2, 3, 1, 3, 2], k = 0;
      var cover = ph.splice(Math.min(s.cover, ph.length - 1), 1)[0];
      while (ph.length && out.length < DATA.albums.maxPages - 1) { var n = Math.min(pattern[k++ % pattern.length], ph.length); out.push(ph.splice(0, n)); }
      return { cover: cover, pages: out };
    },
    render: function (s, step) {
      var Al = DATA.albums;
      if (step === 0) return '<h3>מאיפה התמונות?</h3><p class="sub">לא צריך למיין. אנחנו בוחרים את הטובות, ותמונות דומות נשמרות בצד.</p>' +
        '<div class="tabs" role="tablist" aria-label="מקור התמונות" style="margin-bottom:18px"><button class="tab" type="button" role="tab" aria-selected="' + (s.src === 'device') + '" data-src="device">מהטלפון או מהמחשב</button><button class="tab" type="button" role="tab" aria-selected="' + (s.src === 'link') + '" data-src="link">קישור לתמונות</button></div>' +
        (s.src === 'device'
          ? drop('a-drop', true, 'בוחרים תמונות או גוררים לכאן', 'אייפון או אנדרואיד, גם תמונות HEIC. עד 60 תמונות בדמו')
          : '<div class="field"><label for="a-link">קישור לאלבום <span class="hint">גוגל פוטוס או JumboMail</span></label><div style="display:flex;gap:8px"><input class="inp ltr" id="a-link" data-k="link" inputmode="url" placeholder="photos.app.goo.gl/…" value="' + esc(s.link) + '"><button class="btn btn-quiet" type="button" id="a-link-go">טעינה</button></div><p class="st-note">בדמו הקישור לא נפתח: נטענות תמונות לדוגמה מהאתר של לומבוק.</p></div>') +
        '<div class="thumbs" id="a-thumbs">' + FLOWS.albums.thumbs(s) + '</div>' +
        '<p class="st-note">' + (s.photos.length ? s.photos.length + ' תמונות' + (s.sample ? ' לדוגמה' : '') : 'בדמו התמונות מוקטנות בדפדפן ולא נשלחות לשום מקום.') + '</p>';
      if (step === 1) return '<div class="st-grid"><div><h3>מה חשוב לכם באלבום?</h3><p class="sub">כמה מילים על אנשים, מקומות או רגעים שחשוב שיהיו באלבום. לא חובה.</p>' +
        '<div class="field"><label for="a-note">מה חשוב לכם</label><textarea class="inp" id="a-note" data-k="note" dir="rtl" maxlength="400" placeholder="' + esc(Al.noteHint) + '">' + esc(s.note) + '</textarea></div>' +
        '<div class="field"><label for="a-title">שם לאלבום <span class="hint">אפשר לשנות גם אחר כך</span></label><input class="inp" id="a-title" data-k="title" dir="rtl" maxlength="34" value="' + esc(s.title) + '" placeholder="למשל: ימים של חופש"></div></div>' +
        '<div class="thumbs" aria-hidden="true">' + s.photos.slice(0, 12).map(function (p) { return '<div class="t"><img src="' + esc(p) + '" alt=""></div>'; }).join('') + '</div></div>';
      if (step === 2) {
        var L = FLOWS.albums.pages(s), title = s.title.trim() || 'האלבום שלנו';
        var spreads = [{ label: 'כריכה', thumb: L.cover, html: '<div class="pv-page"><div class="al-cover" style="position:relative;flex:1;display:flex;flex-direction:column"><img src="' + esc(L.cover) + '" alt=""><div class="ttl">' + esc(title) + '</div></div></div>' }];
        for (var i = 0; i < L.pages.length; i += 2) {
          var a = L.pages[i], b = L.pages[i + 1];
          var side = function (pg) { return pg ? '<div><div class="al-page l' + pg.length + '">' + pg.map(function (p) { return '<img src="' + esc(p) + '" alt="">'; }).join('') + '</div></div>' : '<div></div>'; };
          spreads.push({ label: 'עמודים ' + (i + 1) + ' ו ' + (i + 2), thumb: a[0], html: '<div class="pv-page wide"><div class="al-spread">' + side(a) + side(b) + '</div></div>' });
        }
        PV.i = Math.min(PV.i, spreads.length - 1);
        var count = L.pages.length;
        return '<div class="st-grid"><div>' + previewBlock(spreads, 'האלבום מעוצב לפי מה שקורה בתמונות. בדמו העימוד פשוט; באתר יש 400 עיצובים לעמודים.') + '</div>' +
          '<div><h3>' + esc(title) + '</h3><p class="sub">' + (count + 1) + ' עמודים מתוך עד ' + Al.maxPages + ' · 22×22 ס״מ · כריכה רכה</p>' +
          '<div class="field"><label for="a-title2">שם לאלבום</label><input class="inp" id="a-title2" data-k="title" dir="rtl" maxlength="34" value="' + esc(s.title) + '" placeholder="האלבום שלנו"></div>' +
          '<p class="field"><span>תמונת הכריכה <span class="hint">נוגעים בתמונה כדי לבחור</span></span></p><div class="thumbs" id="a-cover">' +
          s.photos.map(function (p, k) { return '<button type="button" class="t' + (k === s.cover ? ' cover' : '') + '" data-cover="' + k + '" aria-label="לבחור כתמונת כריכה" aria-pressed="' + (k === s.cover) + '" style="border:0;padding:0;cursor:pointer"><img src="' + esc(p) + '" alt=""></button>'; }).join('') + '</div></div></div>';
      }
      if (step === 3) {
        var ship = delPrice(s.del), sub = s.copies * Al.price;
        return '<div class="st-grid"><div><h3>הזמנה</h3><p class="sub">העיצוב כלול. משלמים משלוח פעם אחת לכל ההזמנה, כמה שתזמינו.</p>' +
          '<div class="field"><span>כמה עותקים?</span><div class="stepper"><button type="button" id="a-minus" aria-label="פחות עותקים">−</button><output id="a-copies" aria-live="polite">' + s.copies + '</output><button type="button" id="a-plus" aria-label="עוד עותק">+</button></div></div>' +
          '<h4 style="margin:22px 0 10px;font-size:17px">משלוח</h4>' + deliveryOptions('a-del', s.del) + '</div>' +
          '<div><h4 style="margin-bottom:10px;font-size:17px">סיכום</h4>' + bill([[s.copies + ' × אלבום מודפס', ils(sub)], ['משלוח', ship ? ils(ship) : 'חינם']], sub + ship) + '<p class="st-note">בדמו אין תשלום ושום דבר לא נשלח.</p></div></div>';
      }
    },
    thumbs: function (s) {
      return s.photos.map(function (p, k) { return '<div class="t"><img src="' + esc(p) + '" alt=""><button type="button" data-rm="' + k + '" aria-label="להסיר את התמונה">' + icon('close') + '</button></div>'; }).join('');
    },
    bind: function (s, step) {
      if (step === 0) {
        $$('[data-src]', st).forEach(function (t) { t.addEventListener('click', function () { s.src = t.dataset.src; go(0, true); }); });
        wireDrop('a-drop', function (files) {
          var room = 60 - s.photos.length; files = files.slice(0, Math.max(0, room));
          if (s.sample) { s.photos = []; s.sample = false; }
          Promise.all(files.map(function (f) { return shrink(f, 520, 0.72).catch(function () { return null; }); })).then(function (list) {
            list.forEach(function (d) { if (d) s.photos.push(d); }); go(0, true);
          });
        });
        var lg = $('#a-link-go');
        if (lg) lg.addEventListener('click', function () { s.photos = DATA.albums.samples.slice(); s.sample = true; s.cover = 0; if (!s.title) s.title = 'ימים של חופש'; go(0, true); });
        var th = $('#a-thumbs');
        if (th) th.addEventListener('click', function (e) { var b = e.target.closest('[data-rm]'); if (b) { s.photos.splice(+b.dataset.rm, 1); if (s.cover >= s.photos.length) s.cover = 0; go(0, true); } });
      }
      if (step === 2) {
        bindPreview();
        $('#a-cover').addEventListener('click', function (e) { var b = e.target.closest('[data-cover]'); if (b) { s.cover = +b.dataset.cover; PV.i = 0; go(2, true); } });
        $('#a-title2').addEventListener('change', function () { go(2, true); });
      }
      if (step === 3) {
        $('#a-minus').addEventListener('click', function () { if (s.copies > 1) { s.copies--; go(3, true); } });
        $('#a-plus').addEventListener('click', function () { if (s.copies < 20) { s.copies++; go(3, true); } });
        $$('input[name="a-del"]', st).forEach(function (r) { r.addEventListener('change', function () { s.del = r.value; go(3, true); }); });
      }
    },
    valid: function (s, step) { return step !== 0 || s.photos.length > 0; },
    hint: function (s, step) { return step === 0 && !s.photos.length ? 'מוסיפים תמונות' : ''; },
    making: 1,
    total: function (s) { return s.copies * DATA.albums.price + delPrice(s.del); },
    summary: function (s) { return s.title.trim() || 'האלבום שלנו'; },
    thumb: function (s) { return s.photos[s.cover] || null; }
  };

  /* ---------- studio frame ---------- */
  function refreshFoot() {
    if (!S) return;
    var F = FLOWS[S.kind], last = S.step === F.steps.length - 1;
    var next = $('#st-next'), back = $('#st-back'), hint = $('#st-hint');
    back.hidden = S.step === 0 || S.done;
    var ok = F.valid(S.state, S.step);
    next.disabled = !ok;
    next.querySelector('.lbl').textContent = S.done ? 'סגירה' : last ? 'להזמין (דמו)' : S.step === F.making ? 'לתצוגה מקדימה' : S.step === F.making + 1 ? 'להזמנה' : 'להמשיך';
    hint.textContent = S.done ? '' : (ok ? '' : F.hint(S.state, S.step)) || (S.step >= F.making + 1 && !S.done ? 'סה״כ ' + F.total(S.state) + ' ₪' : '');
    $('#st-steplbl').textContent = S.done ? 'הוזמן' : 'שלב ' + (S.step + 1) + ' מתוך ' + F.steps.length + ': ' + F.steps[S.step];
    $$('#st-progress i').forEach(function (i, k) { i.classList.toggle('on', S.done || k <= S.step); });
  }
  function go(step, keepScroll) {
    var F = FLOWS[S.kind];
    S.step = step; S.done = false;
    var body = $('#st-body');
    var top = body.scrollTop;
    var dir = keepScroll ? 0 : (S.prev == null ? 1 : step >= S.prev ? 1 : -1); S.prev = step;
    body.classList.remove('go-fwd', 'go-back'); void body.offsetWidth;
    if (dir) body.classList.add(dir > 0 ? 'go-fwd' : 'go-back');
    body.innerHTML = F.render(S.state, step);
    renderPreviewPart = function () {};
    bindChoices(S.state); bindInputs(S.state); F.bind(S.state, step);
    body.scrollTop = keepScroll ? top : 0;
    refreshFoot();
    if (window.LBH_glide) window.LBH_glide(st);
    if (!keepScroll) { var h = body.querySelector('h3'); if (h) { h.tabIndex = -1; h.focus({ preventScroll: true }); } }
  }
  function saveDraft(status, order) {
    var F = FLOWS[S.kind];
    var item = { id: S.id, kind: S.kind, title: F.summary(S.state), thumb: F.thumb(S.state), status: status || 'draft', order: order || '', total: F.total(S.state), date: new Date().toLocaleDateString('he-IL'), state: S.state, step: S.step };
    return putBook(item);
  }
  function making(then) {
    var body = $('#st-body');
    var F = FLOWS[S.kind];
    body.innerHTML = '<div class="making" role="status"><img class="hat-bob" src="img/hat-3d-360.webp" width="411" height="360" alt=""><h3>' + (S.kind === 'albums' ? 'מסדרים את האלבום…' : S.kind === 'gift' ? 'מכינים את התצוגה המקדימה…' : 'יוצרים את הספר של ' + esc(S.state.name) + '…') + '</h3><p class="small">בדמו זה לוקח שתי שניות.</p></div>';
    $('#st-next').disabled = true; $('#st-back').hidden = true;
    setTimeout(then, calm ? 400 : 2000);
  }
  function placeOrder() {
    var num = 'LB-' + Math.floor(100000 + Math.random() * 899999);
    saveDraft('ordered', num);
    S.done = true;
    var F = FLOWS[S.kind];
    $('#st-body').innerHTML = '<div class="done"><span class="tick">' + icon('check') + '</span><h3>ההזמנה נקלטה (דמו)</h3>' +
      '<p class="sub">' + esc(F.summary(S.state)) + ' · ' + F.total(S.state) + ' ₪ · מספר <span class="ltr">' + num + '</span></p>' +
      '<p class="small">זו הזמנה לדוגמה: שום דבר לא חויב ולא נשלח. הספר נשמר ב״הספרים שלי״.</p>' +
      '<div class="cat-actions" style="justify-content:center"><button class="btn btn-quiet" type="button" data-mybooks>הספרים שלי</button><a class="btn btn-text" href="' + esc(DATA.flows[S.kind]) + '" target="_blank" rel="noopener">לתהליך האמיתי באתר</a></div></div>';
    refreshFoot();
    toast('ההזמנה לדוגמה נשמרה');
  }
  function next() {
    var F = FLOWS[S.kind];
    if (S.done) { closeDialog(st); return; }
    if (!F.valid(S.state, S.step)) { refreshFoot(); return; }
    var last = S.step === F.steps.length - 1;
    if (last) {
      if (!me()) { openAuth('up', 'כדי להזמין ולשמור את הספר, נכנסים לחשבון. בדמו החשבון נשמר רק בדפדפן הזה.', placeOrder); return; }
      placeOrder(); return;
    }
    if (S.step === F.making) { making(function () { go(S.step + 1); if (me()) saveDraft('draft'); }); return; }
    go(S.step + 1);
  }
  function openStudio(kind, resume) {
    if (!FLOWS[kind] || !st) return false;
    var F = FLOWS[kind];
    S = resume ? { kind: kind, id: resume.id, state: resume.state, step: Math.min(resume.step || 0, F.steps.length - 1) } : { kind: kind, id: uid(), state: F.init(), step: 0 };
    PV.i = 0;
    $('#st-title').textContent = F.title;
    $('#st-real').href = (window.LBH_withCarry || function (h) { return h; })(DATA.flows[kind]);
    $('#st-progress').innerHTML = F.steps.map(function () { return '<i></i>'; }).join('');
    openDialog(st);
    go(S.step);
    return true;
  }
  if (st) {
    $('#st-next').addEventListener('click', next);
    $('#st-back').addEventListener('click', function () { if (S && S.step > 0) go(S.step - 1); });
    st.addEventListener('close', function () { if (S && !S.done && me() && S.step > FLOWS[S.kind].making) saveDraft('draft'); S = null; });
  }

  /* every start button opens the studio; a modifier click still goes to the store */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-flow]');
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button > 0) return;
    if (a.closest('.studio')) return;
    if (openStudio(a.dataset.flow)) { e.preventDefault(); $$('.start-pop.open').forEach(function (p) { p.classList.remove('open'); }); var d = document.getElementById('drawer'); if (d && d.open) d.close(); }
  });

  renderAccount();
  window.addEventListener('storage', function (e) { if (e.key === SESSION || e.key === USERS) renderAccount(); });
  window.LBH = { openStudio: openStudio, openAuth: openAuth, me: me };
})();
