/* The content experiment log on the MeBook customer study page (14 Nov 2026). Inlined by build.py after
   experiments-metrics.js. Records live in research/mebook-customer-research/experiments.json through the project server
   (GET /api/experiments, PUT /api/experiments/doc?id=), never in the browser. window.MB_SRC holds the source records
   (purchase intents, research findings, content hypotheses) that experiments link to. */
(function () {
  var M = window.MBMetrics, SRC = window.MB_SRC || { intents: {}, findings: {}, hyps: {} };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var STATUS = { idea: 'רעיון', ready: 'מוכן', running: 'רץ', completed: 'הושלם', archived: 'בארכיון' };
  var STATUS_CLS = { idea: 'outline', ready: 'info', running: 'warning', completed: 'success', archived: 'outline' };
  var CONCL = { promising: 'מבטיח', inconclusive: 'לא חד משמעי', not_supported: 'לא נתמך' };
  var CONCL_CLS = { promising: 'success', inconclusive: 'info', not_supported: 'danger' };
  var MODE = { organic: 'אורגני', paid: 'ממומן' };
  var NUMS = ['impressions', 'views', 'clicks', 'visits', 'purchases', 'revenue', 'spend'];
  var TRACK = ['url', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  var TEXTS = ['title', 'hypothesis', 'audience', 'motivation', 'hook', 'proof', 'cta', 'format', 'channel', 'content_url',
    'data_source', 'period', 'attribution_notes', 'explanation', 'next'];
  var REASON = {
    not_paid: 'רק בניסוי ממומן', no_spend: 'לא הוזנה הוצאה על מודעות', zero_spend: 'ההוצאה על מודעות היא 0',
    purchases_not_measured: 'הרכישות לא נמדדו', zero_purchases: '0 רכישות מיוחסות, אין על מה לחלק',
    revenue_not_measured: 'ההכנסה לא נמדדה', visits_not_measured: 'הביקורים לא נמדדו', zero_visits: '0 ביקורים, אין על מה לחלק'
  };
  var log = { experiments: {} }, online = false, current = null;
  var dlg = $('#mbx-dlg'), form = $('#mbx-form'), err = $('#mbx-err'), list = $('#mbx-list'), note = $('#mbx-note');
  if (!dlg || !form || !list) return;

  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function newId() { return ('x' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7)).toLowerCase(); }
  function fmtDate(iso) { if (!iso) return ''; var p = iso.slice(0, 10).split('-'); return p[2] + ' / ' + p[1] + ' / ' + p[0]; }
  function fmtNum(v, digits) { return v.toLocaleString('he-IL', { maximumFractionDigits: digits == null ? 2 : digits }); }
  function money(v) { return '₪' + fmtNum(v, 2); }
  function linkLabel(l) {
    var p = l.split(':'), k = p[0], v = p[1];
    if (k === 'intent') { var it = SRC.intents[v]; return 'כוונה #' + v + (it ? ' · ' + it.intent.slice(0, 50) : ''); }
    if (k === 'finding') { var f = SRC.findings[v]; return 'ממצא · ' + (f ? f.title : v); }
    if (k === 'hyp') { var h = SRC.hyps[v]; return v + (h ? ' · ' + h.title : ''); }
    return l;
  }
  function all() { return Object.keys(log.experiments).map(function (k) { return log.experiments[k]; }); }
  function byUpdated(a, b) { return (b.updated || '').localeCompare(a.updated || ''); }
  function purchasesText(e) {
    var p = M.num((e.results || {}).purchases);
    return p === null ? 'רכישות: לא נמדד' : 'רכישות מיוחסות: ' + fmtNum(p, 0);
  }

  // ---------- storage (the project server) ----------
  function load() {
    return fetch('/api/experiments', { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    }).then(function (d) {
      log = d && d.experiments ? d : { experiments: {} }; online = true;
    }).catch(function () {
      online = false;
      note.hidden = false;
      note.textContent = 'היומן נשמר דרך שרת הפרויקט (localhost:8780). כאן הוא לקריאה בלבד, ואי אפשר ליצור או לשמור ניסויים.';
    }).then(render);
  }
  function save(doc) {
    return fetch('/api/experiments/doc?id=' + encodeURIComponent(doc.id), {
      method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-LumeBook-Board': '1' }, body: JSON.stringify(doc)
    }).then(function (r) { return r.json().then(function (b) { if (!r.ok) throw new Error(b.error || r.status); return b.doc; }); })
      .then(function (saved) { log.experiments[saved.id] = saved; render(); return saved; });
  }

  // ---------- prefill from a source record ----------
  function template(aud, msg, insight) {
    return 'אני מאמין ש' + (aud || '[קהל]') + ' יקנו אם נראה ' + (msg || '[מסר או הוכחה]') +
      ', כי המניע או ההיסוס שלהם עכשיו הוא ' + (insight || '[תובנה]') + '.';
  }
  function stripFlag(s) { return String(s || '').split('⚑')[0].trim().replace(/[;,]$/, ''); }
  function blank() {
    var d = { id: newId(), links: [], status: 'idea', mode: '', results: {}, tracking: {}, conclusion: '', prev: '' };
    TEXTS.forEach(function (k) { d[k] = ''; });
    NUMS.forEach(function (k) { d.results[k] = null; });
    TRACK.forEach(function (k) { d.tracking[k] = ''; });
    return d;
  }
  function fromSource(link) {
    var d = blank(), p = link.split(':'), k = p[0], v = p[1];
    d.links = [link];
    if (k === 'intent' && SRC.intents[v]) {
      var it = SRC.intents[v];
      d.title = '#' + v + ' ' + it.intent;
      d.audience = it.buyer;
      d.motivation = it.intent + (it.hes ? ' היסוס: ' + it.hes : '');
      d.proof = stripFlag(it.show);
      d.hypothesis = it.sales || template(it.buyer, d.proof, it.hes || it.intent);
    } else if (k === 'finding' && SRC.findings[v]) {
      var f = SRC.findings[v];
      d.title = f.title;
      d.motivation = f.text;
      d.hypothesis = template('', '', f.title);
    } else if (k === 'hyp' && SRC.hyps[v]) {
      var h = SRC.hyps[v], parts = (h.statement.match(/\*\*(.+?)\*\*/g) || []).map(function (s) { return s.replace(/\*\*/g, ''); });
      d.title = v + ': ' + h.title;
      d.audience = parts[0] || '';
      d.proof = h.footage || parts[1] || '';
      d.motivation = parts[2] || '';
      d.hook = h.hook || '';
      d.hypothesis = template(parts[0], parts[1], parts[2]);
    }
    return d;
  }
  function followUp(prev) {
    var d = blank();
    ['audience', 'motivation', 'hook', 'proof', 'cta', 'format', 'channel'].forEach(function (k) { d[k] = prev[k] || ''; });
    d.mode = prev.mode || '';
    d.links = (prev.links || []).slice();
    d.title = 'המשך: ' + prev.title;
    d.hypothesis = prev.next || prev.hypothesis;
    d.prev = prev.id;
    return d;
  }

  // ---------- the list ----------
  var flt = { status: '', mode: '', channel: '', intent: '' };
  function render() {
    var xs = all().sort(byUpdated);
    // channel and intent filters list what the log holds
    var chans = {}, ints = {};
    xs.forEach(function (e) {
      if (e.channel) chans[e.channel] = 1;
      (e.links || []).forEach(function (l) { if (l.indexOf('intent:') === 0) ints[l.slice(7)] = 1; });
    });
    fillSelect($('#mbx-f-channel'), 'כל הערוצים', Object.keys(chans).sort(), function (c) { return c; }, flt.channel);
    fillSelect($('#mbx-f-intent'), 'כל הכוונות', Object.keys(ints).sort(function (a, b) { return a - b; }),
      function (n) { return '#' + n + (SRC.intents[n] ? ' ' + SRC.intents[n].intent.slice(0, 40) : ''); }, flt.intent);
    var shown = xs.filter(function (e) {
      return (!flt.status || e.status === flt.status) && (!flt.mode || e.mode === flt.mode) &&
        (!flt.channel || e.channel === flt.channel) && (!flt.intent || (e.links || []).indexOf('intent:' + flt.intent) >= 0);
    });
    $('#mbx-count').textContent = shown.length === xs.length ? xs.length + ' ניסויים' : shown.length + ' מתוך ' + xs.length;
    list.innerHTML = shown.map(rowHtml).join('') ||
      '<p class="lb-empty">' + (xs.length ? 'אין ניסוי שמתאים לסינון.' : 'עוד אין ניסויים. אפשר להתחיל מכוונת קנייה, ממצא או השערה בדף, או מ״ניסוי חדש״.') + '</p>';
    $$('[data-open]', list).forEach(function (b) { b.addEventListener('click', function () { open(log.experiments[b.dataset.open]); }); });
    $('#mbx-new').disabled = !online;
    renderSources();
  }
  function fillSelect(sel, allLabel, values, label, cur) {
    if (!sel) return;
    sel.innerHTML = '<option value="">' + esc(allLabel) + '</option>' + values.map(function (v) {
      return '<option value="' + esc(v) + '"' + (v === cur ? ' selected' : '') + '>' + esc(label(v)) + '</option>';
    }).join('');
  }
  function rowHtml(e) {
    var chips = '<span class="lb-chip ' + STATUS_CLS[e.status] + '">' + STATUS[e.status] + '</span>';
    if (e.mode) chips += '<span class="lb-chip outline">' + MODE[e.mode] + '</span>';
    if (e.channel) chips += '<span class="lb-chip outline">' + esc(e.channel) + '</span>';
    if (e.conclusion) chips += '<span class="lb-chip ' + CONCL_CLS[e.conclusion] + '">' + CONCL[e.conclusion] + '</span>';
    var ints = (e.links || []).filter(function (l) { return l.indexOf('intent:') === 0; }).map(function (l) { return '#' + l.slice(7); });
    return '<button type="button" class="lb-card mbx-row" data-open="' + esc(e.id) + '">' +
      '<span class="mbx-row-title">' + esc(e.title) + '</span><span class="mb-chips">' + chips + '</span>' +
      '<span class="mbx-row-meta">' + esc(purchasesText(e)) + (ints.length ? ' · כוונות ' + esc(ints.join(', ')) : '') +
      (e.updated ? ' · עודכן <span class="lb-ltr">' + fmtDate(e.updated) + '</span>' : '') + '</span></button>';
  }
  $$('[data-xstatus]').forEach(function (b) { b.addEventListener('click', function () {
    flt.status = b.dataset.xstatus; $$('[data-xstatus]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); render(); }); });
  $$('[data-xmode]').forEach(function (b) { b.addEventListener('click', function () {
    flt.mode = b.dataset.xmode; $$('[data-xmode]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); render(); }); });
  $('#mbx-f-channel').addEventListener('change', function (ev) { flt.channel = ev.target.value; render(); });
  $('#mbx-f-intent').addEventListener('change', function (ev) { flt.intent = ev.target.value; render(); });
  $('#mbx-new').addEventListener('click', function () { open(blank(), true); });

  // ---------- experiments shown on their source records ----------
  function renderSources() {
    var by = {};
    all().forEach(function (e) { (e.links || []).forEach(function (l) { (by[l] = by[l] || []).push(e); }); });
    $$('.mbx-src').forEach(function (box) {
      var key = box.dataset.for, xs = (by[key] || []).sort(byUpdated);
      var items = xs.map(function (e) {
        var learn = e.conclusion ? '<span class="lb-chip ' + CONCL_CLS[e.conclusion] + '">' + CONCL[e.conclusion] + '</span> ' +
          esc((e.explanation || '').slice(0, 160)) + ((e.explanation || '').length > 160 ? '…' : '') : '';
        return '<li><button type="button" class="mbx-srclink" data-open="' + esc(e.id) + '">' + esc(e.title) + '</button> ' +
          '<span class="lb-chip ' + STATUS_CLS[e.status] + '">' + STATUS[e.status] + '</span>' + (learn ? '<div class="mbx-learn">' + learn + '</div>' : '') + '</li>';
      }).join('');
      box.innerHTML = (xs.length ? '<span class="lb-eyebrow">ניסויים (' + xs.length + ')</span><ul>' + items + '</ul>' : '') +
        (online ? '<button type="button" class="lb-btn secondary sm" data-from="' + esc(key) + '">+ ניסוי מכאן</button>' : '');
      $$('[data-open]', box).forEach(function (b) { b.addEventListener('click', function () { open(log.experiments[b.dataset.open]); }); });
      $$('[data-from]', box).forEach(function (b) { b.addEventListener('click', function () { open(fromSource(b.dataset.from), true); }); });
    });
  }

  // ---------- the dialog ----------
  var F = function (name) { return form.elements[name]; };
  function open(doc, isNew) {
    if (!doc) return;
    current = JSON.parse(JSON.stringify(doc));
    err.hidden = true;
    $('#mbx-dlg-title').textContent = isNew ? 'ניסוי חדש' : 'ניסוי';
    TEXTS.forEach(function (k) { if (F(k)) F(k).value = current[k] || ''; });
    NUMS.forEach(function (k) { var v = (current.results || {})[k]; F('r_' + k).value = v === null || v === undefined ? '' : String(v); });
    TRACK.forEach(function (k) { F('t_' + k).value = (current.tracking || {})[k] || ''; });
    F('status').value = current.status || 'idea';
    F('start').value = current.start || ''; F('end').value = current.end || '';
    $$('input[name="mode"]', form).forEach(function (r) { r.checked = r.value === (current.mode || ''); });
    $$('input[name="conclusion"]', form).forEach(function (r) { r.checked = r.value === (current.conclusion || ''); });
    renderLinks(); refresh(); renderChain();
    $$('button, input, select, textarea', form).forEach(function (el) { if (el.dataset.keep !== '1') el.disabled = !online; });
    if (!dlg.open) dlg.showModal();
    dlg.querySelector('.lb-dialog-body').scrollTop = 0;
  }
  function renderLinks() {
    $('#mbx-links').innerHTML = (current.links || []).map(function (l) {
      return '<span class="lb-chip outline mbx-linkchip">' + esc(linkLabel(l)) +
        '<button type="button" aria-label="הסרת הקישור" data-unlink="' + esc(l) + '">✕</button></span>';
    }).join('') || '<span class="lb-dim lb-xs">אין קישור עדיין</span>';
    $$('[data-unlink]', form).forEach(function (b) { b.addEventListener('click', function () {
      current.links = current.links.filter(function (x) { return x !== b.dataset.unlink; }); renderLinks(); }); });
  }
  $('#mbx-addlink').addEventListener('change', function (ev) {
    var v = ev.target.value; ev.target.value = '';
    if (v && current.links.indexOf(v) < 0) { current.links.push(v); renderLinks(); }
  });
  function renderChain() {
    var box = $('#mbx-chain'), prev = current.prev && log.experiments[current.prev];
    var next = all().filter(function (e) { return e.prev === current.id; });
    var html = '';
    if (prev) html += '<p>המשך של: <button type="button" class="mbx-srclink" data-open="' + esc(prev.id) + '">' + esc(prev.title) + '</button></p>';
    if (next.length) html += '<p>ניסויי המשך: ' + next.map(function (e) {
      return '<button type="button" class="mbx-srclink" data-open="' + esc(e.id) + '">' + esc(e.title) + '</button>'; }).join(', ') + '</p>';
    box.innerHTML = html; box.hidden = !html;
    $$('[data-open]', box).forEach(function (b) { b.addEventListener('click', function () { open(log.experiments[b.dataset.open]); }); });
    $('#mbx-follow').disabled = !online || !log.experiments[current.id] || !(log.experiments[current.id].conclusion);
  }
  function read() {
    var d = JSON.parse(JSON.stringify(current)), bad = [];
    TEXTS.forEach(function (k) { if (F(k)) d[k] = F(k).value.trim(); });
    d.results = {};
    NUMS.forEach(function (k) {
      var raw = F('r_' + k).value.trim();
      if (raw === '') { d.results[k] = null; return; }
      var n = M.num(raw);
      if (n === null) bad.push(F('r_' + k).dataset.label); else d.results[k] = n;
    });
    d.tracking = {}; TRACK.forEach(function (k) { d.tracking[k] = F('t_' + k).value.trim(); });
    d.status = F('status').value; d.start = F('start').value; d.end = F('end').value;
    var m = $('input[name="mode"]:checked', form); d.mode = m ? m.value : '';
    var c = $('input[name="conclusion"]:checked', form); d.conclusion = c ? c.value : '';
    if (d.mode !== 'paid') d.results.spend = null;
    return { doc: d, bad: bad };
  }
  function refresh() {
    var r = read(), d = r.doc, paid = d.mode === 'paid';
    $$('.mbx-paid', form).forEach(function (el) { el.hidden = !paid; });
    $('#mbx-organic-note').hidden = d.mode !== 'organic';
    var mt = M.metrics(d.results, d.mode);
    function cell(label, m, fmt, sub) {
      var v = m.value === null ? '<span class="mbx-na">לא זמין</span><small>' + esc(REASON[m.reason] || '') + '</small>' : '<b>' + fmt(m.value) + '</b>';
      return '<div class="lb-metric"><span class="lb-metric-label">' + label + '</span><span class="lb-metric-value">' + v + '</span>' +
        (sub ? '<span class="lb-metric-foot">' + sub + '</span>' : '') + '</div>';
    }
    var p = M.num(d.results.purchases);
    $('#mbx-metrics').innerHTML =
      cell('CPA', mt.cpa, money, 'הוצאה על מודעות חלקי רכישות מיוחסות. לא CAC כולל') +
      cell('ROAS', mt.roas, function (v) { return 'x' + fmtNum(v, 2); }, 'הכנסה מיוחסת חלקי הוצאה על מודעות') +
      cell('המרה מביקור לרכישה', mt.conversion, function (v) { return fmtNum(v * 100, 1) + '%'; }, 'רכישות מיוחסות חלקי ביקורים בדף הנחיתה') +
      '<div class="lb-metric"><span class="lb-metric-label">רכישות מיוחסות</span><span class="lb-metric-value">' +
      (p === null ? '<span class="mbx-na">לא נמדד</span>' : '<b>' + fmtNum(p, 0) + '</b><small>נמדד</small>') + '</span></div>';
    var on = M.prompts(d.results), res = d.results;
    var reach = M.num(res.views) !== null ? ['צפיות', M.num(res.views)] : (M.num(res.impressions) !== null ? ['חשיפות', M.num(res.impressions)] : null);
    $$('[data-prompt]', form).forEach(function (el) {
      var k = el.dataset.prompt, active = on.indexOf(k) >= 0, nums = '';
      if (active && k === 'reach_vs_visits') nums = reach[0] + ' ' + fmtNum(reach[1], 0) + ', ביקורים ' + fmtNum(M.num(res.visits), 0);
      if (active && k === 'visits_vs_purchases') nums = 'ביקורים ' + fmtNum(M.num(res.visits), 0) + ', רכישות מיוחסות ' + fmtNum(M.num(res.purchases), 0);
      el.classList.toggle('is-on', active);
      $('.mbx-prompt-nums', el).textContent = nums ? '(' + nums + ')' : (k === 'single_purchase' ? '' : 'עוד אין את שני המספרים');
    });
    $('#mbx-tpl').disabled = !online;
  }
  form.addEventListener('input', refresh);
  form.addEventListener('change', refresh);
  $('#mbx-tpl').addEventListener('click', function () {
    F('hypothesis').value = template(F('audience').value.trim(), F('proof').value.trim(), F('motivation').value.trim()); refresh();
  });
  function submit(statusOverride) {
    var r = read(), d = r.doc;
    if (statusOverride) d.status = statusOverride;
    var problems = [];
    if (!d.title) problems.push('צריך כותרת.');
    if (!d.hypothesis) problems.push('צריך השערה.');
    if (r.bad.length) problems.push('מספר לא תקין ב: ' + r.bad.join(', ') + '. משאירים ריק כשלא נמדד.');
    if (d.status === 'completed' && (!d.conclusion || !d.explanation)) problems.push('כדי לסמן ״הושלם״ צריך לבחור מסקנה ולכתוב הסבר.');
    if (d.start && d.end && d.end < d.start) problems.push('תאריך הסיום לפני תאריך ההתחלה.');
    if (problems.length) { err.textContent = problems.join(' '); err.hidden = false; return Promise.resolve(null); }
    err.hidden = true;
    return save(d).then(function (saved) {
      current = JSON.parse(JSON.stringify(saved)); F('status').value = saved.status; renderChain();
      flash('נשמר'); return saved;
    }).catch(function (e) { err.textContent = 'השמירה נכשלה: ' + e.message; err.hidden = false; return null; });
  }
  function flash(msg) { var s = $('#mbx-saved'); s.textContent = msg; s.hidden = false; setTimeout(function () { s.hidden = true; }, 2200); }
  form.addEventListener('submit', function (ev) { ev.preventDefault(); submit(); });
  $('#mbx-complete').addEventListener('click', function () { submit('completed'); });
  $('#mbx-follow').addEventListener('click', function () {
    var saved = log.experiments[current.id]; if (!saved) return;
    open(followUp(saved), true);
  });
  $('#mbx-close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (ev) { if (ev.target === dlg) dlg.close(); });

  // the "+ link" picker lists every source record
  (function () {
    var sel = $('#mbx-addlink'), html = '';
    function group(label, items) { return items.length ? '<optgroup label="' + esc(label) + '">' + items.join('') + '</optgroup>' : ''; }
    html += group('השערות תוכן', Object.keys(SRC.hyps).map(function (k) { return '<option value="hyp:' + esc(k) + '">' + esc(linkLabel('hyp:' + k)) + '</option>'; }));
    html += group('ממצאים ודפוסים', Object.keys(SRC.findings).map(function (k) { return '<option value="finding:' + esc(k) + '">' + esc(linkLabel('finding:' + k)) + '</option>'; }));
    html += group('כוונות קנייה', Object.keys(SRC.intents).sort(function (a, b) { return a - b; }).map(function (k) { return '<option value="intent:' + esc(k) + '">' + esc(linkLabel('intent:' + k)) + '</option>'; }));
    sel.insertAdjacentHTML('beforeend', html);
  })();

  window.MBX = { reload: load, open: open, fromSource: fromSource };   // for checks in the browser console
  load();
})();
