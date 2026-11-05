/* Product Reels Playbook: renders every view from the JSON bundle in #pb-data. Routes are plain hash
   tokens (#home, #tool-hook, #p-H1, #reel-CODE, #concept-2, #dive-3, #note-cta-text ...). */
(function () {
  'use strict';
  var D = JSON.parse(document.getElementById('pb-data').textContent);
  var TOOL = {}, BY_PREFIX = {}, REEL = {};
  D.tools.forEach(function (t) { TOOL[t.id] = t; BY_PREFIX[t.prefix] = t; });
  D.reels.forEach(function (r) { REEL[r.code] = r; });
  var FEATURE = {};
  D.features.forEach(function (f) { FEATURE[f.id] = f; });
  var CAT = { personalised_book: 'Personalised book', childrens_book: "Children's book", toy_game: 'Toy or game', educational: 'Educational',
    parenting_product: 'Parenting product', gift: 'Gift', other: 'Other' };
  var APPROACH = { Story: 'Story with a turn', Hands: 'Hands and light', Inside: "What's inside", Talk: 'Talk with it in hand',
    Problem: 'Problem first', Result: 'Result first', List: 'Stack and list', Use: 'Children using it' };
  var LEVEL = { strong: ['Strong evidence', 'ok', 3], moderate: ['Moderate evidence', 'info', 2], 'weak-moderate': ['Weak to moderate', '', 1],
    weak: ['Weak evidence', '', 1], contested: ['Contested', 'warn', 0], mixed: ['Mixed evidence', 'warn', 2] };
  var VERDICT = { works: ['Works', 'ok', 'v-works'], partly: ['Partly', 'warn', 'v-partly'], weak: ['Weak', 'bad', 'v-weak'] };

  var I = {
    home: '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16 9.8"/>',
    list: '<path d="M10 6h10M10 12h10M10 18h10"/><path d="M4 6l1.2 1.2L7.5 5M4 12l1.2 1.2 2.3-2.2M4 18l1.2 1.2 2.3-2.2"/>',
    hook: '<path d="M13 2L4.5 13.5H11l-1 8.5 8.5-11.5H12z"/>',
    watch: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    cta: '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8"/>',
    show: '<path d="M3 5.5c3-1.5 6-1.5 9 .5 3-2 6-2 9-.5V19c-3-1.5-6-1.5-9 .5-3-2-6-2-9-.5z"/><path d="M12 6v13.5"/>',
    edit: '<circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><path d="M8 7.5L20 18M8 16.5L20 6"/>',
    topic: '<path d="M12 20s-7-4.4-8.6-9A4.7 4.7 0 0 1 12 6.5a4.7 4.7 0 0 1 8.6 4.5C19 15.6 12 20 12 20z"/>',
    film: '<path d="M3 7.5h3l2-2.5h8l2 2.5h3V19H3z"/><circle cx="12" cy="13" r="3.4"/>',
    text: '<path d="M5 6h14M12 6v13M9 19h6"/>',
    library: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    bulb: '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    phone: '<rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18h2"/>',
    log: '<path d="M4 19V5M4 19h16"/><path d="M8 15l3-4 3 2 4-6"/>',
    bars: '<path d="M6 20V11M12 20V4M18 20v-7"/>',
    search: '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
    book: '<path d="M4 5h7v14H4zM13 5h7v14h-7z"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v5h1"/>',
    chev: '<path d="M9 6l6 6-6 6"/>',
    up: '<path d="M12 19V5M6 11l6-6 6 6"/>',
    down: '<path d="M12 5v14M6 13l6 6 6-6"/>',
    flat: '<path d="M5 12h14"/>',
    ext: '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    warn: '<path d="M12 3l9.5 17h-19z"/><path d="M12 10v4M12 17h.01"/>',
    spark: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M6 18l2.5-2.5M15.5 8.5L18 6"/>'
  };
  function svg(name) { return '<svg viewBox="0 0 24 24" aria-hidden="true">' + (I[name] || '') + '</svg>'; }
  function tile(id) { return '<span class="tile t-' + id + '">' + svg(id) + '</span>'; }
  function ico(name) { return '<span class="ico">' + svg(name) + '</span>'; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function text(html) { var d = document.createElement('div'); d.innerHTML = html || ''; return (d.textContent || '').trim(); }
  function heb(s) { return esc(s).replace(/(["״]?[\u0590-\u05FF][\u0590-\u05FF0-9\s'״׳\-.,:?!·%₪]*[\u0590-\u05FF0-9?!]["״]?)/g, '<bdi lang="he">$1</bdi>'); }
  function first(html, n) { var t = text(html); if (t.length <= n) return t; var cut = t.slice(0, n); return cut.slice(0, cut.lastIndexOf(' ')) + '…'; }
  function toolOf(pid) { return BY_PREFIX[pid.charAt(0)]; }
  function pid(id, cls) { var t = toolOf(id); return '<a class="pid t-' + (t ? t.id : 'none') + (cls ? ' ' + cls : '') + '" href="#p-' + id + '" title="' + esc(D.principles[id] ? D.principles[id].title : id) + '">' + id + '</a>'; }
  function linkIds(html) {
    return String(html || '').split(/(<[^>]+>)/).map(function (part) {
      if (part.charAt(0) === '<') return part;
      return part.replace(/\b([HRCSEKFT]\d{1,2})\b/g, function (m) { return D.principles[m] ? pid(m, 'in') : m; });
    }).join('');
  }
  function fmt(n, d) { return n == null ? 'n/a' : Number(n).toLocaleString('en-US', { maximumFractionDigits: d == null ? 0 : d, minimumFractionDigits: d || 0 }); }
  function strengthChip(level) { var L = LEVEL[level] || LEVEL.mixed; return '<span class="chip ' + L[1] + '"><span class="meter" data-n="' + L[2] + '"><i></i><i></i><i></i></span>' + L[0] + '</span>'; }
  function verdictChip(v) { var V = VERDICT[v]; return V ? '<span class="chip ' + V[1] + '">' + V[0] + '</span>' : ''; }
  function more(title, sub, body, open, cls) {
    return '<details class="more ' + (cls || '') + '"' + (open ? ' open' : '') + '><summary><span class="sum-text">' + title +
      (sub ? '<span class="sum-sub">' + sub + '</span>' : '') + '</span>' + svg('chev').replace('<svg', '<svg class="chev"') + '</summary><div class="more-body">' + body + '</div></details>';
  }
  function head(o) {
    var h = '<header class="ph">';
    if (o.crumb) h += '<nav class="ph-crumb" aria-label="Where you are">' + o.crumb.map(function (c, i) {
      return (i ? svg('chev') : '') + (c[1] ? '<a href="#' + c[1] + '">' + c[0] + '</a>' : '<span>' + c[0] + '</span>');
    }).join('') + '</nav>';
    if (o.tool) {
      h += '<div class="ph-tool">' + tile(o.tool) + '<div class="ph">' + (o.eyebrow ? '<span class="ph-eyebrow">' + o.eyebrow + '</span>' : '') + '<h1>' + o.title + '</h1></div></div>';
    } else {
      if (o.eyebrow) h += '<span class="ph-eyebrow">' + o.eyebrow + '</span>';
      h += '<h1>' + o.title + '</h1>';
    }
    if (o.lede) h += '<p class="ph-lede">' + o.lede + '</p>';
    if (o.extra) h += o.extra;
    return h + '</header>';
  }
  function sec(title, sub, body) { return '<section class="sec"><div class="sec-head"><h2>' + title + '</h2>' + (sub ? '<p>' + sub + '</p>' : '') + '</div>' + body + '</section>'; }
  function page(html, wide, cls) { return '<div class="pb-page' + (wide ? ' is-wide' : '') + (cls ? ' ' + cls : '') + '">' + html + '</div>'; }
  function callout(kind, icon, title, body) { return '<div class="callout ' + kind + '">' + svg(icon) + '<div>' + (title ? '<b>' + title + '</b>' : '') + '<div>' + body + '</div></div></div>'; }

  // ---------------------------------------------------------------- the sample check
  function parseVerdict(v) {
    v = v || '';
    if (v.indexOf('too few') === 0) return { dir: 'flat', word: 'Too few Reels to tell', sure: '' };
    if (v.indexOf('no clear') === 0) return { dir: 'flat', word: 'No clear difference', sure: '' };
    var sure = v.split(':')[0], dir = v.indexOf('higher') >= 0 ? 'up' : 'down';
    return { dir: dir, word: dir === 'up' ? 'Higher with it' : 'Lower with it', sure: sure };
  }
  function sig(f) {
    var p = parseVerdict(f.v);
    return '<span class="sig ' + p.dir + '">' + svg(p.dir) + p.word + (p.sure ? ' · ' + p.sure : '') + '</span>';
  }
  function fx(f) {
    var max = Math.max(f.my || 0, f.mn || 0) || 1;
    return '<div class="fx"><div class="fx-head"><b>' + esc(f.label) + '</b>' + sig(f) + '</div>' +
      '<div class="fx-bars"><span>With it</span><span class="track"><i style="width:' + ((f.my || 0) / max * 100).toFixed(1) + '%"></i></span><span class="v">' + fmt(f.my, 2) + '</span>' +
      '<span>Without</span><span class="track off"><i style="width:' + ((f.mn || 0) / max * 100).toFixed(1) + '%"></i></span><span class="v">' + fmt(f.mn, 2) + '</span></div>' +
      '<span class="fx-note">Median plays per follower · ' + f.ny + ' Reels with it, ' + f.nn + ' without' + (f.p != null ? ' · p = ' + fmt(f.p, 3) : '') + '</span></div>';
  }

  // ---------------------------------------------------------------- reels
  function reelCard(r, snippet) {
    var V = VERDICT[r.verdict] || ['', '', ''];
    return '<article class="card reel" style="position:relative">' +
      '<div class="reel-top"><b><a class="stretch" href="#reel-' + r.code + '">@' + esc(r.handle) + '</a></b><span class="dot ' + V[2] + '" title="' + V[0] + '"></span></div>' +
      '<div class="reel-prod">' + r.product + '</div>' +
      '<div class="reel-one">' + (snippet || r.one) + '</div>' +
      '<div class="reel-meta">' + (r.plays ? fmt(r.plays) + ' plays' : '') + (r.ppf ? ' · ' + fmt(r.ppf, 1) + '× followers' : '') + (r.dur ? ' · ' + r.dur + ' s' : '') + '</div></article>';
  }

  // ---------------------------------------------------------------- views
  var V = {};

  V.home = function () {
    var m = D.meta;
    var h = head({ eyebrow: 'LumeBook · updated 18 Oct 2026', title: 'Reels Playbook',
      lede: 'How to film LumeBook product Reels that hold attention and get asked for, built from ' + m.reels + ' Israeli creator Reels and ' + m.principles + ' research principles.' });
    h += '<div class="stats">' + [[m.reels, 'Reels broken down'], [m.creators, 'creators'], [m.principles, 'research principles'], [8, 'questions per Reel']].map(function (s) {
      return '<div class="stat"><b>' + s[0] + '</b><span>' + s[1] + '</span></div>'; }).join('') + '</div>';
    h += sec('Start here', '', '<div class="grid" style="--min:16rem">' +
      startCard('#concept-2', 'Film this first', 'A book from my photo at 4', 'The best-supported concept after the research check: your face, a question the photo answers, a real story. It needs nobody else\'s consent.', 'Open concept 2') +
      startCard('#checklist', 'Before you post', 'Check your Reel, tool by tool', 'All ' + m.principles + ' principles as a checklist. Your ticks stay on this device.', 'Open the checklist') +
      startCard('#proof', 'What holds up', 'Every rule, checked', 'Which playbook rules the research confirmed, which it changed and which are still unproven.', 'See the verdicts') + '</div>');
    h += sec('The 8 tools', 'One for each question you asked of every Reel', '<div class="grid" style="--min:15.5rem">' + D.tools.map(function (t) {
      var n = D.order.filter(function (p) { return p.charAt(0) === t.prefix; }).length;
      return '<article class="card tool-card t-' + t.id + '" style="position:relative">' + tile(t.id) + '<h3><a class="stretch" href="#tool-' + t.id + '">' + esc(t.name) + '</a></h3><p>' + esc(t.job) + '</p><span class="dim">' + n + ' principles</span></article>';
    }).join('') + '</div>');
    var changed = D.proof.rows.filter(function (r) { return r.key === 'changed'; });
    h += sec('What the research changed', changed.length + ' rules', '<div class="stack">' + changed.map(function (r) {
      return '<article class="card vrow k-changed"><div class="pc-top"><span class="chip warn">Changed</span></div><h3>' + r.rule + '</h3><p class="verdict">' + linkIds(verdictRest(r.verdict)) + '</p></article>';
    }).join('') + '</div>' + '<p><a class="go" href="#proof">All verdicts ' + svg('chev') + '</a></p>');
    h += '<div class="stack">' + more('Bottom line of the research', 'The 15 Oct summary, updated 18 Oct', '<div class="prose">' + D.home.bottom + '</div>') +
      more('Five Reels to watch first', 'With what to pay attention to', '<div class="prose">' + D.home.five + '</div>') + '</div>';
    return page(h, true);
  };
  function startCard(href, label, title, body, go) {
    return '<article class="card" style="position:relative"><span class="label">' + label + '</span><h3><a class="stretch" href="' + href + '">' + title + '</a></h3><p class="muted small">' + body + '</p><span class="go">' + go + ' ' + svg('chev') + '</span></article>';
  }

  V.tool = function (id) {
    var t = TOOL[id], ps = D.order.filter(function (p) { return p.charAt(0) === t.prefix; });
    var h = head({ tool: id, eyebrow: 'Tool ' + t.n + ' of 8', title: esc(t.name), lede: esc(t.job),
      extra: '<p class="ph-ask">Your question for every Reel: <b>' + esc(t.ask) + '</b></p>' });
    h += sec('Principles', ps.length + ' · open one for the rule, the evidence and examples', '<div class="stack">' + ps.map(principleCard).join('') + '</div>');
    var dist = D.dist[id];
    if (dist && dist.rows.length) {
      var max = Math.max.apply(null, dist.rows.map(function (r) { return r[1]; })) || 1;
      var rows = dist.rows.slice(0, 8).map(function (r) {
        return '<div class="dist-row"><span>' + esc(r[0]) + '</span><span class="track"><i style="width:' + (r[1] / max * 100).toFixed(1) + '%"></i></span><span class="v">' + r[1] + '</span></div>';
      }).join('');
      h += sec(esc(dist.title), 'Out of ' + D.meta.reels + ' Reels', '<div class="card"><div class="dist">' + rows + '</div></div>');
    }
    var best = D.reels.filter(function (r) { return r.verdict === 'works'; }).sort(function (a, b) { return (b.ppf || 0) - (a.ppf || 0); }).slice(0, 3);
    h += sec('Strong examples', 'Rated "works", ranked by plays per follower', '<div class="grid" style="--min:14rem">' + best.map(function (r) {
      return reelCard(r, first(r.q[id].what, 170)); }).join('') + '</div>');
    var fs = D.features.filter(function (f) { return f.q === t.n; });
    if (fs.length) h += more('What our 173 Reels show', fs.length + ' checks on public plays per follower · correlation, not proof', '<div>' + fs.map(fx).join('') + '</div>');
    var i = D.tools.indexOf(t), pv = D.tools[i - 1], nx = D.tools[i + 1];
    h += '<nav class="pager">' + (pv ? '<a class="t-' + pv.id + '" href="#tool-' + pv.id + '"><small>Previous tool</small><span>' + esc(pv.name) + '</span></a>' : '') +
      (nx ? '<a class="next t-' + nx.id + '" href="#tool-' + nx.id + '"><small>Next tool</small><span>' + esc(nx.name) + '</span></a>' : '') + '</nav>';
    return page(h, false, 't-' + id);
  };
  function principleCard(id) {
    var p = D.principles[id], f = p.features.length ? FEATURE[p.features[0]] : null;
    return '<article class="card pc t-' + p.tool + '" style="position:relative">' +
      '<div class="pc-top">' + pid(id) + strengthChip(p.level) + '<span class="spacer"></span>' + '</div>' +
      '<h3><a class="stretch" href="#p-' + id + '">' + esc(p.title) + '</a></h3>' +
      '<p class="pc-apply">' + p.apply + '</p>' +
      '<div class="pc-foot">' + (f ? '<span class="ph-row" style="gap:.4rem"><span class="fx-note">In our Reels</span>' + sig(f) + '</span>' : '<span class="fx-note">Cited in ' + p.cites + ' of ' + D.meta.reels + ' Reel breakdowns</span>') +
      '<span class="go">Rule and evidence ' + svg('chev') + '</span></div></article>';
  }

  V.principle = function (id) {
    var p = D.principles[id], t = TOOL[p.tool];
    var extra = '<div class="ph-row">' + strengthChip(p.level) + '<span class="chip line">Cited in ' + p.cites + ' of ' + D.meta.reels + ' Reels</span>' +
      (p.overlaps && p.overlaps.length ? '<span class="chip line">Same point as ' + p.overlaps.map(function (o) { return pid(o); }).join(' ') + '</span>' : '') + '</div>';
    var h = head({ crumb: [[esc(t.name), 'tool-' + t.id], [id]], eyebrow: id + ' · ' + esc(t.name), title: esc(p.title), extra: extra });
    h += '<div class="rule"><span class="label tc">The rule</span><p>' + p.rule + '</p></div>';
    h += sec('How to apply it at LumeBook', '', '<p class="apply">' + linkIds(p.apply) + '</p>');
    var body = '';
    if (p.features.length) body += '<div class="card">' + p.features.map(function (k) { return fx(FEATURE[k]); }).join('') + '</div>';
    var ex = p.examples.map(function (c) { return REEL[c]; }).filter(Boolean);
    if (ex.length) body += '<div class="grid" style="--min:14rem">' + ex.map(function (r) { return reelCard(r, first(r.q[p.tool].why, 170)); }).join('') + '</div>';
    else body += '<p class="dim small">No Reel rated "works" cites it under ' + esc(t.name) + '.</p>';
    h += sec('In our 173 Reels', p.features.length ? 'Public plays per follower with and without it, then Reels that use it well' : 'Reels that use it well', body);
    h += '<div class="stack">' + more('Why the evidence is rated ' + (LEVEL[p.level] || LEVEL.mixed)[0].toLowerCase(), '', '<div class="prose">' + p.strength + '</div>') +
      more('Sources', p.sources.length + ' studies and platform pages, each opened during the research', '<div class="stack">' + p.sources.map(function (s) {
        return '<div class="src"><div class="ph-row"><span class="chip line">' + esc(s.kind) + '</span>' + (s.url ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener"><b>' + esc(s.title) + '</b></a>' : '<b>' + esc(s.title) + '</b>') + '</div><div class="small muted" style="margin-top:.3rem">' + s.html + '</div></div>';
      }).join('<hr style="margin:0;border:0;border-top:1px solid var(--line)">') + '</div>') +
      more('Full research notes', '', '<p class="small">This principle comes from the research pass on ' + esc(noteTitle(p.note)) + '. <a href="#note-' + p.note + '">Open the notes</a> for the summary, the traced myths and every source.</p>') + '</div>';
    var i = D.order.indexOf(id), pv = D.order[i - 1], nx = D.order[i + 1];
    h += '<nav class="pager">' + (pv ? '<a class="t-' + toolOf(pv).id + '" href="#p-' + pv + '"><small>' + pv + '</small><span>' + esc(D.principles[pv].title) + '</span></a>' : '') +
      (nx ? '<a class="next t-' + toolOf(nx).id + '" href="#p-' + nx + '"><small>' + nx + '</small><span>' + esc(D.principles[nx].title) + '</span></a>' : '') + '</nav>';
    return page(h, false, 't-' + p.tool);
  };
  function noteTitle(slug) { var n = D.notes.filter(function (x) { return x.slug === slug; })[0]; return n ? n.title.toLowerCase() : slug; }

  // library
  var LIB = { q: '', verdict: 'all', cat: '', sort: 'ppf', mode: 'cards', tool: 'hook' };
  V.library = function () {
    var cats = {}; D.reels.forEach(function (r) { cats[r.cat] = (cats[r.cat] || 0) + 1; });
    var h = head({ title: 'Reel library', lede: D.meta.reels + ' Israeli creator Reels, each answered on the 8 questions. Open one for the full breakdown, or compare all of them on one question.' });
    h += '<div class="stack"><div class="toolbar"><label class="search">' + svg('search') + '<input id="lib-q" type="search" placeholder="Search handle, product or any word" aria-label="Search the Reels" value="' + esc(LIB.q) + '"></label>' +
      '<select id="lib-cat" aria-label="Category"><option value="">All categories</option>' + Object.keys(cats).sort().map(function (c) {
        return '<option value="' + c + '"' + (LIB.cat === c ? ' selected' : '') + '>' + (CAT[c] || c) + ' (' + cats[c] + ')</option>'; }).join('') + '</select>' +
      '<select id="lib-sort" aria-label="Sort"><option value="ppf">Travelled furthest</option><option value="plays">Most plays</option><option value="short">Shortest first</option><option value="deep">Deep dives first</option></select></div>' +
      '<div class="toolbar"><div class="seg" role="group" aria-label="Verdict">' + [['all', 'All'], ['works', 'Works'], ['partly', 'Partly'], ['weak', 'Weak']].map(function (v) {
        return '<button type="button" data-v="' + v[0] + '" aria-pressed="' + (LIB.verdict === v[0]) + '">' + v[1] + '</button>'; }).join('') + '</div>' +
      '<div class="seg" role="group" aria-label="View"><button type="button" data-m="cards" aria-pressed="' + (LIB.mode === 'cards') + '">Cards</button><button type="button" data-m="compare" aria-pressed="' + (LIB.mode === 'compare') + '">Compare one question</button></div></div>' +
      '<div class="seg" id="lib-tools" role="group" aria-label="Question"' + (LIB.mode === 'compare' ? '' : ' hidden') + '>' + D.tools.map(function (t) {
        return '<button type="button" data-t="' + t.id + '" class="t-' + t.id + '" aria-pressed="' + (LIB.tool === t.id) + '"><span class="dot" style="color:var(--tc);margin-right:.35rem"></span>' + esc(t.name) + '</button>'; }).join('') + '</div>' +
      '<p class="fx-note" id="lib-count"></p><div id="lib-list"></div></div>';
    return page(h, true);
  };
  function libRows() {
    var q = LIB.q.toLowerCase().split(/\s+/).filter(Boolean);
    var rows = D.reels.filter(function (r) {
      if (LIB.verdict !== 'all' && r.verdict !== LIB.verdict) return false;
      if (LIB.cat && r.cat !== LIB.cat) return false;
      if (!q.length) return true;
      var hay = (r.code + ' ' + r.handle + ' ' + text(r.product) + ' ' + text(r.one)).toLowerCase();
      if (LIB.mode === 'compare') hay += ' ' + text(r.q[LIB.tool].what + ' ' + r.q[LIB.tool].why).toLowerCase();
      return q.every(function (w) { return hay.indexOf(w) >= 0; });
    });
    var key = { ppf: function (r) { return -(r.ppf || 0); }, plays: function (r) { return -(r.plays || 0); }, short: function (r) { return r.dur || 999; },
      deep: function (r) { return r.deep ? +r.deep : 99 + -(r.ppf || 0) / 1000; } }[LIB.sort];
    return rows.sort(function (a, b) { return key(a) - key(b); });
  }
  function libDraw() {
    var rows = libRows(), list = document.getElementById('lib-list');
    document.getElementById('lib-count').textContent = rows.length + (rows.length === 1 ? ' Reel' : ' Reels');
    if (!rows.length) { list.innerHTML = '<p class="dim">No Reel matches. Clear the search or pick another filter.</p>'; return; }
    if (LIB.mode === 'cards') { list.innerHTML = '<div class="grid" style="--min:15rem">' + rows.map(function (r) { return reelCard(r); }).join('') + '</div>'; return; }
    var t = TOOL[LIB.tool];
    list.innerHTML = '<div class="card t-' + t.id + '">' + rows.map(function (r) {
      var x = r.q[t.id], what = t.id === 'watch' ? (x.beats || []).map(function (b) { return '<b>' + esc(b.t) + '</b> ' + text(b.what); }).join(' · ') : x.what;
      return '<div class="cmp-row"><div class="who"><a href="#reel-' + r.code + '">@' + esc(r.handle) + '</a><span class="reel-meta">' + (r.ppf ? fmt(r.ppf, 1) + '× followers' : '') + '</span>' + verdictChip(r.verdict) + '</div>' +
        '<div><div class="what">' + what + '</div><div class="why"><b>Why:</b> ' + linkIds(x.why) + '</div></div></div>';
    }).join('') + '</div>';
  }
  function libWire() {
    var on = function (id, ev, fn) { var el = document.getElementById(id); if (el) el.addEventListener(ev, fn); };
    on('lib-q', 'input', function (e) { LIB.q = e.target.value; libDraw(); });
    on('lib-cat', 'change', function (e) { LIB.cat = e.target.value; libDraw(); });
    var sort = document.getElementById('lib-sort'); sort.value = LIB.sort;
    sort.addEventListener('change', function (e) { LIB.sort = e.target.value; libDraw(); });
    document.querySelectorAll('[data-v]').forEach(function (b) { b.addEventListener('click', function () {
      LIB.verdict = b.dataset.v; document.querySelectorAll('[data-v]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); }); libDraw(); }); });
    document.querySelectorAll('[data-m]').forEach(function (b) { b.addEventListener('click', function () {
      LIB.mode = b.dataset.m; document.querySelectorAll('[data-m]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      document.getElementById('lib-tools').hidden = LIB.mode !== 'compare'; libDraw(); }); });
    document.querySelectorAll('[data-t]').forEach(function (b) { b.addEventListener('click', function () {
      LIB.tool = b.dataset.t; document.querySelectorAll('[data-t]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); }); libDraw(); }); });
    libDraw();
  }

  V.reel = function (code) {
    var r = REEL[code];
    var chips = '<div class="ph-row">' + verdictChip(r.verdict) + '<span class="chip line">' + (CAT[r.cat] || r.cat) + '</span>' + (r.approach ? '<span class="chip line">' + (APPROACH[r.approach] || r.approach) + '</span>' : '') +
      (r.deep ? '<a class="chip tint" href="#dive-' + r.deep + '">Deep dive ' + r.deep + '</a>' : '') + '</div>';
    var h = head({ crumb: [['Reel library', 'library'], ['@' + esc(r.handle)]], title: '@' + esc(r.handle), lede: r.product, extra: chips });
    h += '<div class="stats">' + [[r.plays ? fmt(r.plays) : 'n/a', 'plays on 15 Oct'], [r.ppf ? fmt(r.ppf, 1) + '×' : 'n/a', 'plays per follower'], [r.dur ? r.dur + ' s' : 'n/a', 'length'],
      [r.followers ? fmt(r.followers) : 'n/a', 'followers']].map(function (s) { return '<div class="stat"><b>' + s[0] + '</b><span>' + s[1] + '</span></div>'; }).join('') + '</div>';
    h += '<p><a class="btn plain" href="https://www.instagram.com/reel/' + r.code + '/" target="_blank" rel="noopener">' + svg('ext') + 'Watch on Instagram</a></p>';
    h += '<div class="three"><div class="card ok"><span class="label">Copy this</span><p>' + r.one + '</p></div><div class="card bad"><span class="label">Avoid</span><p>' + r.weak + '</p></div><div class="card lb"><span class="label">For LumeBook</span><p>' + r.lb + '</p></div></div>';
    h += sec('The 8 questions', 'Open one for what happens and why', '<div class="stack">' + D.tools.map(function (t, i) { return qBlock(r, t, i === 0); }).join('') + '</div>');
    var i = D.reels.indexOf(r), pv = D.reels[i - 1], nx = D.reels[i + 1];
    h += '<nav class="pager">' + (pv ? '<a href="#reel-' + pv.code + '"><small>Previous Reel</small><span>@' + esc(pv.handle) + '</span></a>' : '') + (nx ? '<a class="next" href="#reel-' + nx.code + '"><small>Next Reel</small><span>@' + esc(nx.handle) + '</span></a>' : '') + '</nav>';
    return page(h);
  };
  function qBlock(r, t, open) {
    var x = r.q[t.id], body = '';
    if (t.id === 'watch') {
      body += '<ol class="beats">' + (x.beats || []).map(function (b) {
        return '<li><span class="t">' + esc(b.t) + '</span><div><span class="does">' + esc(String(b.does).replace(/_/g, ' ')) + '</span><div class="w">' + b.what + '</div></div>' + (b.why ? '<span class="y">' + b.why + '</span>' : '') + '</li>'; }).join('') + '</ol>';
      if (x.what) body += '<p class="small"><b>Invites interaction:</b> ' + x.what + '</p>';
    } else if (t.id === 'text') {
      body += '<p><span class="label">On screen</span><br>' + x.screen + '</p><p><span class="label">Caption</span><br>' + x.caption + '</p>';
    } else body += '<p>' + x.what + '</p>';
    if (x.tags && x.tags.length) body += '<div class="tags">' + x.tags.map(function (g) { return '<span>' + esc(g.replace(/_/g, ' ')) + '</span>'; }).join('') + '</div>';
    body += '<div class="why"><span class="label tc">Why</span>' + linkIds(x.why) + '</div>';
    var prev = t.id === 'watch' ? (x.beats && x.beats[0] ? text(x.beats[0].what) : '') : first(x.what, 140);
    return '<details class="q t-' + t.id + '"' + (open ? ' open' : '') + '><summary>' + tile(t.id) + '<span><b>' + esc(t.name) + '</b><span class="prev">' + heb(prev) + '</span></span>' + svg('chev').replace('<svg', '<svg class="chev"') + '</summary><div class="q-body">' + body + '</div></details>';
  }

  V.proof = function () {
    var P = D.proof, n = { holds: 0, changed: 0, unproven: 0 };
    P.rows.forEach(function (r) { if (n[r.key] != null) n[r.key]++; });
    var h = head({ eyebrow: 'Research check · 18 Oct 2026', title: 'Is the playbook proven?', lede: 'Each playbook rule, checked against outside research and against the public numbers of our 173 Reels.' });
    h += '<div class="stats"><div class="stat"><b class="v-works">' + n.holds + '</b><span>rules hold</span></div><div class="stat"><b class="v-partly">' + n.changed + '</b><span>rules changed</span></div><div class="stat"><b class="dim">' + n.unproven + '</b><span>still unproven</span></div></div>';
    h += sec('Three kinds of evidence', 'Strongest for LumeBook last', '<div class="grid" style="--min:13rem">' + P.kinds.map(function (k, i) {
      return '<div class="card"><span class="label">' + (i + 1) + ' of 3</span><h3>' + esc(k.title.replace(/\.$/, '')) + '</h3><p class="small muted">' + esc(text(k.text).split(/(?<=\.)\s/)[0]) + '</p></div>'; }).join('') + '</div>' +
      more('More on each kind of evidence', 'Where each one lives in the project', '<div class="prose small">' + P.kinds.map(function (k) { return '<p><b>' + esc(k.title) + '</b> ' + k.text + '</p>'; }).join('') + '</div>'));
    h += callout('info', 'info', 'How to read the verdicts', P.clear);
    h += '<div class="stack"><div class="seg" role="group" aria-label="Filter verdicts">' + [['all', 'All ' + P.rows.length], ['holds', 'Holds ' + n.holds], ['changed', 'Changed ' + n.changed], ['unproven', 'Unproven ' + n.unproven]].map(function (v, i) {
      return '<button type="button" data-k="' + v[0] + '" aria-pressed="' + (i === 0) + '">' + v[1] + '</button>'; }).join('') + '</div>' +
      '<div class="stack" id="proof-list">' + P.rows.map(function (r) {
        var chip = r.key === 'holds' ? '<span class="chip ok">Holds</span>' : r.key === 'changed' ? '<span class="chip warn">Changed</span>' : r.key === 'unproven' ? '<span class="chip">Unproven</span>' : '';
        return '<article class="card vrow k-' + r.key + '" data-k="' + r.key + '"><div class="pc-top">' + chip + '</div><h3>' + r.rule + '</h3>' +
          (verdictRest(r.verdict) ? '<p class="verdict">' + linkIds(verdictRest(r.verdict)) + '</p>' : '') + '<p class="sample"><span class="label">Our 173 Reels</span><br>' + r.sample + '</p>' +
          more('Research behind it', '', '<p class="small">' + linkIds(r.research) + '</p>') + '</article>';
      }).join('') + '</div></div>';
    h += sec('What changes in the five concepts', '', '<div class="grid" style="--min:15rem">' + Object.keys(P.changes).map(function (k) {
      var c = D.concepts.items.filter(function (x) { return String(x.n) === k; })[0];
      return '<article class="card" style="position:relative"><div class="ph-row"><span class="num-tile">' + k + '</span><b><a class="stretch" href="#concept-' + k + '" dir="rtl" lang="he">' + esc(c ? c.he : '') + '</a></b></div><p class="small muted">' + linkIds(P.changes[k]) + '</p></article>';
    }).join('') + '</div>');
    h += more('How sure this is', '', '<div class="prose">' + P.sure + '</div>');
    return page(h);
  };
  function verdictRest(v) {
    var m = /^<strong>([^<]*)<\/strong>\s*(.*)$/.exec(v || '');
    if (!m) return v;
    var head = m[1].replace(/^(Holds|Changed|Unproven)\b[,:]?\s*/i, '').replace(/[:;.]\s*$/, '');
    var rest = (head ? head + (m[2] ? ': ' : '') : '') + m[2];
    rest = rest.replace(/^[,;:]\s*/, '');
    return rest ? rest.charAt(0).toUpperCase() + rest.slice(1) : '';
  }
  function proofWire() {
    document.querySelectorAll('[data-k]').forEach(function (b) {
      if (b.tagName !== 'BUTTON') return;
      b.addEventListener('click', function () {
        document.querySelectorAll('button[data-k]').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        document.querySelectorAll('#proof-list > [data-k]').forEach(function (c) { c.hidden = b.dataset.k !== 'all' && c.dataset.k !== b.dataset.k; });
      });
    });
  }

  // checklist
  var CK_KEY = 'pb-checklist-1';
  function ckLoad() { try { return JSON.parse(localStorage.getItem(CK_KEY) || '[]'); } catch (e) { return []; } }
  function ckSave(a) { try { localStorage.setItem(CK_KEY, JSON.stringify(a)); } catch (e) { /* storage blocked: ticks last for this visit */ } }
  var CK = null;
  V.checklist = function () {
    CK = CK || ckLoad();
    var h = head({ eyebrow: 'Before you post', title: 'Pre-post checklist', lede: 'Check a Reel against every principle, tool by tool. Ticks stay on this device; clear them for the next Reel.',
      extra: '<div class="stack"><div class="progress"><i id="ck-all" style="width:0"></i></div><div class="ph-row"><span class="fx-note" id="ck-count"></span><span style="flex:1"></span><button class="btn plain" type="button" id="ck-reset">Clear all ticks</button></div></div>' });
    h += D.tools.map(function (t) {
      var ps = D.order.filter(function (p) { return p.charAt(0) === t.prefix; });
      return '<section class="sec t-' + t.id + '"><div class="sec-head"><div class="ph-row">' + tile(t.id) + '<h2>' + esc(t.name) + '</h2></div><p id="ck-n-' + t.id + '"></p></div>' +
        '<div class="card"><div class="ck">' + ps.map(function (id) {
          var p = D.principles[id];
          return '<label><input type="checkbox" id="ck-' + id + '" data-id="' + id + '"' + (CK.indexOf(id) >= 0 ? ' checked' : '') + '>' + pid(id) + '<span>' + esc(p.title) + '</span></label>';
        }).join('') + '</div></div></section>';
    }).join('');
    return page(h);
  };
  function ckDraw() {
    var total = D.order.length, done = CK.length;
    document.getElementById('ck-all').style.width = (done / total * 100) + '%';
    document.getElementById('ck-count').textContent = done + ' of ' + total + ' checked';
    D.tools.forEach(function (t) {
      var ps = D.order.filter(function (p) { return p.charAt(0) === t.prefix; });
      var el = document.getElementById('ck-n-' + t.id);
      if (el) el.textContent = ps.filter(function (p) { return CK.indexOf(p) >= 0; }).length + ' of ' + ps.length;
    });
  }
  function ckWire() {
    document.querySelectorAll('.ck input').forEach(function (inp) {
      inp.addEventListener('change', function () {
        var id = inp.dataset.id, i = CK.indexOf(id);
        if (inp.checked && i < 0) CK.push(id); if (!inp.checked && i >= 0) CK.splice(i, 1);
        ckSave(CK); ckDraw();
      });
    });
    document.getElementById('ck-reset').addEventListener('click', function () {
      CK = []; ckSave(CK); document.querySelectorAll('.ck input').forEach(function (x) { x.checked = false; }); ckDraw();
    });
    ckDraw();
  }

  // concepts
  V.concepts = function () {
    var h = head({ eyebrow: 'Make a Reel', title: 'Five Reel concepts', lede: 'Each one filmable with a phone at home, with no child on camera. Hebrew scripts are linted with the comment word לומי.' });
    h += '<div class="grid" style="--min:16rem">' + D.concepts.items.map(function (c) {
      var ch = D.proof.changes[String(c.n)];
      var len = c.summary.filter(function (x) { return x[0] === 'Length'; })[0];
      return '<article class="card" style="position:relative"><div class="ph-row"><span class="num-tile">' + c.n + '</span>' + (c.n === 2 ? '<span class="chip ok">Film first</span>' : '') + '</div>' +
        '<h3 class="he-title" style="font-size:var(--t-title3)" lang="he"><a class="stretch" href="#concept-' + c.n + '">' + esc(c.he) + '</a></h3><p class="muted small">' + c.en + '</p>' +
        (ch ? '<p class="small">' + esc(first(ch, 150)) + '</p>' : '') + (len ? '<span class="fx-note">' + text(len[1]) + '</span>' : '') + '</article>';
    }).join('') + '</div>';
    h += '<div class="card"><div class="prose">' + D.concepts.intro + '</div></div>';
    h += more('Before you film', 'Product facts, the Hebrew voice and the Instagram handle', '<div class="prose">' + D.preface + '</div>');
    return page(h, true);
  };
  V.concept = function (n) {
    var c = D.concepts.items.filter(function (x) { return x.n === n; })[0];
    var h = head({ crumb: [['Five concepts', 'concepts'], ['Concept ' + n]], title: '<span class="he-title" lang="he" dir="rtl" style="font-size:inherit">' + esc(c.he) + '</span>', lede: c.en,
      extra: '<div class="ph-row"><span class="num-tile">' + n + '</span>' + c.summary.filter(function (x) { return x[0] === 'Length'; }).map(function (x) { return '<span class="chip line">' + text(x[1]) + '</span>'; }).join('') + '</div>' });
    var ch = D.proof.changes[String(n)];
    if (ch) h += callout(n === 2 ? 'ok' : 'info', 'spark', 'After the research check', linkIds(ch));
    h += '<dl class="kv">' + c.summary.filter(function (x) { return x[0] !== 'Length'; }).map(function (x) { return '<dt>' + esc(x[0]) + '</dt><dd>' + x[1] + '</dd>'; }).join('') + '</dl>';
    h += c.warn.map(function (w) { return callout('warn', 'warn', esc(w[0]), linkIds(w[1])); }).join('');
    h += '<div class="prose">' + c.main + '</div>';
    h += '<div class="stack">' + (c.why.length ? more('Why this concept', 'The Reels it is built from', '<div class="prose">' + c.why.map(function (x) { return '<p>' + x[1] + '</p>'; }).join('') + '</div>') : '') +
      more('Production notes', c.production.map(function (x) { return x[0]; }).join(', '), '<dl class="kv">' + c.production.map(function (x) { return '<dt>' + esc(x[0]) + '</dt><dd>' + linkIds(x[1]) + '</dd>'; }).join('') + '</dl>') + '</div>';
    var pv = n > 1 ? n - 1 : null, nx = n < D.concepts.items.length ? n + 1 : null;
    h += '<nav class="pager">' + (pv ? '<a href="#concept-' + pv + '"><small>Previous concept</small><span>Concept ' + pv + '</span></a>' : '') + (nx ? '<a class="next" href="#concept-' + nx + '"><small>Next concept</small><span>Concept ' + nx + '</span></a>' : '') + '</nav>';
    return page(h);
  };

  V.shoot = function () {
    var h = head({ eyebrow: 'Make a Reel', title: 'Your first shoot', lede: 'Concept 1 in 60 to 90 minutes, grouped by set-up, not by timeline.' });
    h += callout('info', 'spark', 'After the research check', 'Concept 2 is now the best-supported concept. This plan still works for concept 1; record the voiceover from 0:00 and keep text above the bottom 35% of the frame (' + pid('H4') + ' ' + pid('F2') + ').');
    h += '<div class="prose">' + D.shoot.intro + '</div>';
    h += '<div class="steps">' + D.shoot.steps.map(function (s) {
      return '<div class="step"><div class="step-rail"><span class="dot"></span><span class="line"></span></div><div class="step-body"><div class="ph-row"><h3>' + s.title + '</h3>' + (s.note ? '<span class="chip line">' + s.note + '</span>' : '') + '</div><div class="prose small">' + s.html + '</div></div></div>';
    }).join('') + '</div>';
    return page(h);
  };
  V.setup = function () {
    var h = head({ eyebrow: 'Make a Reel', title: 'Phone set-up', lede: 'Once, for every concept: rigs, light, focus, framing and sound.' });
    h += '<div class="grid" style="--min:17rem">' + D.setup.map(function (x) { return '<div class="card"><h3>' + esc(x[0]) + '</h3><p class="small">' + linkIds(x[1]) + '</p></div>'; }).join('') + '</div>';
    return page(h, true);
  };
  V.log = function () {
    return page(head({ eyebrow: 'Make a Reel', title: 'After posting', lede: 'What to log for each Reel, so concepts can be compared by books started, not by plays.' }) + '<div class="card"><div class="prose">' + linkIds(D.log) + '</div></div>');
  };

  // patterns
  function patternTabs(cur) {
    return '<nav class="seg" aria-label="Patterns">' + [['patterns', 'What the 173 show'], ['approaches', 'Seven approaches'], ['fixes', 'Weak choices and fixes']].map(function (x) {
      return '<a href="#' + x[0] + '"' + (x[0] === cur ? ' aria-current="page"' : '') + '>' + x[1] + '</a>'; }).join('') + '</nav>';
  }
  V.patterns = function () {
    var F = D.findings;
    var h = head({ eyebrow: 'Evidence', title: 'Patterns in 173 Reels', lede: 'What the sample shows, counted first and read after.', extra: patternTabs('patterns') });
    h += '<div class="stack">' + F.items.map(function (f) {
      return '<article class="card"><div class="ph-row"><span class="num-tile" style="width:2rem;height:2rem;font-size:var(--t-callout)">' + f.n + '</span><h3>' + f.title + '</h3></div>' +
        (f.read ? '<p>' + f.read + '</p>' : '') + more('What we counted', '', '<div class="prose small">' + f.seen + '</div>') + '</article>';
    }).join('') + '</div>';
    h += more('How the sample was counted', '', '<div class="prose small">' + F.intro + F.outro + '</div>');
    return page(h);
  };
  V.approaches = function () {
    var h = head({ eyebrow: 'Evidence', title: 'Seven approaches', lede: 'The ways Israeli creators film a product, with who at LumeBook should film each.', extra: patternTabs('approaches') });
    h += '<div class="stack">' + D.approaches.map(function (a) {
      return '<article class="card"><div class="ph-row"><span class="num-tile">' + esc(a.letter) + '</span><h3>' + a.name + '</h3></div><p>' + a.what + '</p>' +
        '<p class="small"><span class="label">Who films it</span><br>' + a.who + '</p>' +
        '<div class="ph-row">' + a.examples.map(function (c) { var r = REEL[c]; return r ? '<a class="chip tint" href="#reel-' + c + '">@' + esc(r.handle) + '</a>' : ''; }).join('') + '</div>' +
        more('Why it works, when it fits, limits', '', '<dl class="kv">' + [['Why it works', a.why], ['Fits LumeBook when', a.fits], ['Limits', a.limits], ['Phone notes', a.phone]].filter(function (x) { return x[1]; }).map(function (x) {
          return '<dt>' + x[0] + '</dt><dd>' + x[1] + '</dd>'; }).join('') + '</dl>') + '</article>';
    }).join('') + '</div>';
    return page(h);
  };
  V.fixes = function () {
    var h = head({ eyebrow: 'Evidence', title: 'Weak choices and fixes', lede: 'What went wrong in the sample, and what to do instead.', extra: patternTabs('fixes') });
    h += '<div class="stack">' + D.fixes.map(function (f) {
      return '<article class="card"><div class="three" style="grid-template-columns:repeat(2,minmax(0,1fr))"><div class="card bad"><span class="label">Instead of</span><p>' + f.saw + '</p></div><div class="card ok"><span class="label">Do this</span><p>' + linkIds(f['do']) + '</p></div></div><p class="fx-note">Seen in ' + f.where + '</p></article>';
    }).join('') + '</div>';
    return page(h);
  };

  V.dives = function () {
    var h = head({ eyebrow: 'Evidence', title: 'Eight deep dives', lede: 'Eight Reels broken down second by second, each teaching one way to film a product with a phone.' });
    h += '<div class="grid" style="--min:16rem">' + D.dives.items.map(function (d) {
      return '<article class="card" style="position:relative"><div class="ph-row"><span class="num-tile">' + d.n + '</span></div><h3><a class="stretch" href="#dive-' + d.n + '">' + d.who + '</a></h3><p class="small muted">' + d.sub + '</p><p class="small">' + d.teaches + '</p></article>';
    }).join('') + '</div>';
    h += more('How to read the breakdowns', 'Seen, said and my read', '<div class="prose small">' + D.dives.howto + '</div>');
    return page(h, true);
  };
  V.dive = function (n) {
    var d = D.dives.items.filter(function (x) { return x.n === n; })[0];
    var h = head({ crumb: [['Deep dives', 'dives'], ['Deep dive ' + n]], eyebrow: 'Deep dive ' + n + ' of 8', title: d.who, lede: d.sub });
    h += '<div class="card"><dl class="kv">' + d.meta.map(function (m) { return '<dt>' + esc(m[0]) + '</dt><dd>' + m[1] + '</dd>'; }).join('') + '</dl></div>';
    h += d.strip;
    h += '<div class="stack">' + d.sections.map(function (s, i) { return more(s.n + '. ' + s.title, '', '<div class="prose">' + s.html + '</div>', i === 0); }).join('') + '</div>';
    var pv = n > 1 ? n - 1 : null, nx = n < D.dives.items.length ? n + 1 : null;
    h += '<nav class="pager">' + (pv ? '<a href="#dive-' + pv + '"><small>Previous</small><span>Deep dive ' + pv + '</span></a>' : '') + (nx ? '<a class="next" href="#dive-' + nx + '"><small>Next</small><span>Deep dive ' + nx + '</span></a>' : '') + '</nav>';
    return page(h);
  };

  V.notes = function () {
    var h = head({ eyebrow: 'Evidence', title: 'Research notes', lede: 'The four research passes of 18 Oct 2026: platform documentation, peer-reviewed studies, industry data and Israeli regulators, with the popular statistics traced to their origin.' });
    var pairs = { 'hooks-retention': ['hook', 'watch'], 'cta-text': ['cta', 'text'], 'shown-filmed': ['show', 'film'], 'edit-topic': ['edit', 'topic'] };
    h += '<div class="grid" style="--min:16rem">' + D.notes.map(function (n) {
      return '<article class="card" style="position:relative"><div class="ph-row">' + pairs[n.slug].map(tile).join('') + '</div><h3><a class="stretch" href="#note-' + n.slug + '">' + esc(n.title) + '</a></h3><p class="small muted">' + n.sections.map(function (s) { return text(s.title); }).join(' · ') + '</p></article>';
    }).join('') + '</div>';
    return page(h, true);
  };
  V.note = function (slug) {
    var n = D.notes.filter(function (x) { return x.slug === slug; })[0];
    var h = head({ crumb: [['Research notes', 'notes'], [esc(n.title)]], eyebrow: 'Research notes', title: esc(n.title) });
    h += '<div class="prose small dim">' + n.lead + '</div>';
    h += n.sections.map(function (s, i) {
      return i === 0 ? sec(s.title, '', '<div class="card"><div class="prose">' + linkIds(s.html) + '</div></div>') : more(s.title, '', '<div class="prose small">' + linkIds(s.html) + '</div>');
    }).join('');
    return page(h);
  };
  V.method = function () {
    var h = head({ eyebrow: 'Evidence', title: 'Sources and method', lede: 'How the Reels were watched and coded, what the numbers can and cannot say, and every Reel in the sample.' });
    h += '<div class="stack">' + D.method.limits.map(function (l) {
      var m = l.match(/^<strong>(.+?)<\/strong>:?\s*([\s\S]*)$/);
      return m ? more(m[1].replace(/:$/, ''), '', '<div class="prose small">' + m[2] + '</div>') : '<p>' + l + '</p>';
    }).join('') + '</div>';
    h += sec('Every Reel in the sample', 'With links, dates, relationship, disclosure and public counts', more('Source index', '173 verified, 24 excluded, and the leads not watched', '<div class="prose small">' + D.method.sources + '</div>'));
    h += more('Rebuild the page', 'The scripts behind it', '<div class="prose small">' + D.method.rebuild + '</div>');
    return page(h);
  };

  // ---------------------------------------------------------------- routing
  function resolve(h) {
    var m;
    if (['home', 'proof', 'checklist', 'library', 'concepts', 'shoot', 'setup', 'log', 'patterns', 'approaches', 'fixes', 'dives', 'notes', 'method'].indexOf(h) >= 0)
      return { key: h, html: function () { return V[h](); } };
    if ((m = /^tool-(\w+)$/.exec(h)) && TOOL[m[1]]) return { key: h, tool: m[1], html: function () { return V.tool(m[1]); } };
    if ((m = /^p-([A-Z]\d{1,2})$/.exec(h)) && D.principles[m[1]]) return { key: h, tool: D.principles[m[1]].tool, p: m[1], html: function () { return V.principle(m[1]); } };
    if ((m = /^reel-([\w-]+)$/.exec(h)) && REEL[m[1]]) return { key: h, parent: 'library', html: function () { return V.reel(m[1]); } };
    if ((m = /^concept-(\d)$/.exec(h)) && +m[1] >= 1 && +m[1] <= D.concepts.items.length) return { key: h, parent: 'concepts', html: function () { return V.concept(+m[1]); } };
    if ((m = /^dive-(\d)$/.exec(h)) && +m[1] >= 1 && +m[1] <= D.dives.items.length) return { key: h, parent: 'dives', html: function () { return V.dive(+m[1]); } };
    if ((m = /^note-([\w-]+)$/.exec(h)) && D.notes.some(function (n) { return n.slug === m[1]; })) return { key: h, parent: 'notes', html: function () { return V.note(m[1]); } };
    return { key: 'home', html: function () { return V.home(); } };
  }
  var TITLES = { home: 'Home', proof: 'Is it proven?', checklist: 'Pre-post checklist', library: 'Reel library', concepts: 'Five concepts', shoot: 'First shoot', setup: 'Phone set-up',
    log: 'After posting', patterns: 'Patterns in 173 Reels', approaches: 'Seven approaches', fixes: 'Weak choices and fixes', dives: 'Deep dives', notes: 'Research notes', method: 'Sources and method' };

  function navItem(key, label, icon, cur, count, cls) {
    var on = cur.key === key;
    return '<a class="sb-item' + (cls ? ' ' + cls : '') + '" href="#' + key + '"' + (on ? ' aria-current="page"' : '') + '>' + icon + '<span>' + label + '</span>' + (count != null ? '<span class="sb-count">' + count + '</span>' : '<span></span>') + '</a>';
  }
  function sidebar(cur) {
    var h = '<a class="sb-brand" href="#home"><img src="' + D.logo + '" alt=""><span><b>Reels Playbook</b><small>LumeBook · product Reels</small></span></a>';
    h += '<label class="sb-search">' + svg('search') + '<input id="sb-q" type="search" placeholder="Search principles, Reels" aria-label="Search the playbook" autocomplete="off"></label>';
    h += '<nav class="sb-nav" id="sb-nav">';
    h += '<div class="sb-group"><span class="sb-label">Start</span>' + navItem('home', 'Home', ico('home'), cur) + navItem('proof', 'Is it proven?', ico('check'), cur) +
      navItem('checklist', 'Pre-post checklist', ico('list'), cur) + '</div>';
    h += '<div class="sb-group"><span class="sb-label">The 8 tools</span>' + D.tools.map(function (t) {
      var open = cur.tool === t.id, ps = D.order.filter(function (p) { return p.charAt(0) === t.prefix; });
      var s = '<a class="sb-item t-' + t.id + '" href="#tool-' + t.id + '"' + (cur.key === 'tool-' + t.id ? ' aria-current="page"' : '') + '>' + tile(t.id) + '<span>' + esc(t.name) + '</span><span class="sb-count">' + ps.length + '</span></a>';
      if (open) s += '<div class="sb-sub t-' + t.id + '">' + ps.map(function (id) {
        return '<a href="#p-' + id + '"' + (cur.p === id ? ' aria-current="page"' : '') + '><span class="pid">' + id + '</span><span>' + esc(D.principles[id].title) + '</span></a>'; }).join('') + '</div>';
      return s;
    }).join('') + '</div>';
    h += '<div class="sb-group"><span class="sb-label">Make a Reel</span>' + navItem('concepts', 'Five concepts', ico('bulb'), cur, 5);
    if (cur.parent === 'concepts' || cur.key === 'concepts') h += '<div class="sb-sub t-none">' + D.concepts.items.map(function (c) {
      return '<a href="#concept-' + c.n + '"' + (cur.key === 'concept-' + c.n ? ' aria-current="page"' : '') + '><span class="pid">' + c.n + '</span><span lang="he" dir="rtl">' + esc(c.he) + '</span></a>'; }).join('') + '</div>';
    h += navItem('shoot', 'First shoot', ico('clock'), cur) + navItem('setup', 'Phone set-up', ico('phone'), cur) + navItem('log', 'After posting', ico('log'), cur) + '</div>';
    h += '<div class="sb-group"><span class="sb-label">Evidence</span>' + navItem('library', 'Reel library', ico('library'), cur, D.meta.reels) +
      navItem('patterns', 'Patterns in 173 Reels', ico('bars'), { key: ['patterns', 'approaches', 'fixes'].indexOf(cur.key) >= 0 ? 'patterns' : cur.key }) + navItem('dives', 'Deep dives', ico('search'), cur, 8);
    if (cur.parent === 'dives' || cur.key === 'dives') h += '<div class="sb-sub t-none">' + D.dives.items.map(function (d) {
      return '<a href="#dive-' + d.n + '"' + (cur.key === 'dive-' + d.n ? ' aria-current="page"' : '') + '><span class="pid">' + d.n + '</span><span>' + text(d.who) + '</span></a>'; }).join('') + '</div>';
    h += navItem('notes', 'Research notes', ico('book'), cur, 4);
    if (cur.parent === 'notes' || cur.key === 'notes') h += '<div class="sb-sub t-none">' + D.notes.map(function (n) {
      return '<a href="#note-' + n.slug + '"' + (cur.key === 'note-' + n.slug ? ' aria-current="page"' : '') + '><span>' + esc(n.title) + '</span></a>'; }).join('') + '</div>';
    h += navItem('method', 'Sources and method', ico('info'), cur) + '</div>';
    h += '</nav><div class="sb-results" id="sb-results" hidden></div>';
    h += '<p class="sb-foot">Internal. Public counts read 15 Oct 2026; none is tied to a sale. Research checked 18 Oct 2026.</p>';
    return h;
  }
  function search(q) {
    var nav = document.getElementById('sb-nav'), out = document.getElementById('sb-results');
    q = q.trim().toLowerCase();
    if (!q) { nav.hidden = false; out.hidden = true; return; }
    var words = q.split(/\s+/);
    function hit(s) { s = s.toLowerCase(); return words.every(function (w) { return s.indexOf(w) >= 0; }); }
    var ps = D.order.filter(function (id) { var p = D.principles[id]; return hit(id + ' ' + p.title + ' ' + text(p.rule) + ' ' + text(p.apply)); }).slice(0, 10);
    var rs = D.reels.filter(function (r) { return hit(r.code + ' ' + r.handle + ' ' + text(r.product) + ' ' + text(r.one)); }).slice(0, 8);
    var ts = D.tools.filter(function (t) { return hit(t.name + ' ' + t.job); });
    var cs = D.concepts.items.filter(function (c) { return hit(c.he + ' ' + text(c.en) + ' concept ' + c.n); });
    var h = '';
    if (ts.length) h += '<div class="sb-group"><span class="sb-label">Tools</span>' + ts.map(function (t) { return '<a class="sb-item" href="#tool-' + t.id + '"><span>' + esc(t.name) + '</span></a>'; }).join('') + '</div>';
    if (ps.length) h += '<div class="sb-group"><span class="sb-label">Principles</span>' + ps.map(function (id) { return '<a class="sb-item" href="#p-' + id + '"><span><span class="pid t-' + toolOf(id).id + '">' + id + '</span> ' + esc(D.principles[id].title) + '</span></a>'; }).join('') + '</div>';
    if (cs.length) h += '<div class="sb-group"><span class="sb-label">Concepts</span>' + cs.map(function (c) { return '<a class="sb-item" href="#concept-' + c.n + '"><span lang="he" dir="rtl">' + esc(c.he) + '</span></a>'; }).join('') + '</div>';
    if (rs.length) h += '<div class="sb-group"><span class="sb-label">Reels</span>' + rs.map(function (r) { return '<a class="sb-item" href="#reel-' + r.code + '"><span>@' + esc(r.handle) + '</span></a>'; }).join('') + '</div>';
    out.innerHTML = h || '<p class="sb-empty">Nothing matches "' + esc(q) + '".</p>';
    nav.hidden = true; out.hidden = false;
  }

  var side = document.getElementById('pb-side'), view = document.getElementById('pb-view'), main = document.getElementById('pb-main'), scrim = document.getElementById('pb-scrim');
  function closeNav() { side.classList.remove('is-open'); scrim.hidden = true; }
  function go() {
    var h = (location.hash || '#home').slice(1), r = resolve(h), keepQ = document.getElementById('sb-q');
    var q = keepQ ? keepQ.value : '';
    side.innerHTML = sidebar(r);
    var inp = document.getElementById('sb-q');
    inp.value = q; if (q) search(q);
    inp.addEventListener('input', function () { search(inp.value); });
    inp.addEventListener('keydown', function (e) { if (e.key === 'Escape') { inp.value = ''; search(''); } });
    view.innerHTML = r.html();
    var title = r.key.indexOf('tool-') === 0 ? TOOL[r.tool].name : r.p ? r.p + ' ' + D.principles[r.p].title : r.key.indexOf('reel-') === 0 ? '@' + REEL[r.key.slice(5)].handle : TITLES[r.key] || text(view.querySelector('h1') ? view.querySelector('h1').innerHTML : '');
    document.getElementById('pb-bar-title').textContent = title;
    if (r.key === 'library') libWire();
    if (r.key === 'proof') proofWire();
    if (r.key === 'checklist') ckWire();
    closeNav();
    window.scrollTo(0, 0);
    main.focus({ preventScroll: true });
    var a = side.querySelector('[aria-current="page"]'); if (a && a.scrollIntoView) a.scrollIntoView({ block: 'nearest' });
  }
  document.getElementById('pb-menu').addEventListener('click', function () { side.classList.add('is-open'); scrim.hidden = false; });
  scrim.addEventListener('click', closeNav);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeNav(); });
  window.addEventListener('hashchange', go);
  go();
})();
