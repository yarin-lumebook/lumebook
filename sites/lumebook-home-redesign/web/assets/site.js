/* LumeBook home redesign (demo): page behaviour. The theme and direction are set
   before paint by the inline boot script in <head>; this file wires the controls. */
(function () {
  'use strict';
  var root = document.documentElement;
  var THEME_KEY = 'lbh-theme';   // 'light' | 'dark' | absent = follow the device
  var DIR_KEY = 'lbh-dir';       // dev only: 'purple' | 'yellow' | 'both'
  var pinned = root.dataset.pinned === '1';  // ?theme= in the address: show, never store
  var mq = window.matchMedia('(prefers-color-scheme: dark)');

  /* Campaign parameters to keep on every link into a store flow (utm_*, a creator's personal link,
     click ids). Dev parameters are dropped. */
  var DEV_PARAMS = { dir: 1, theme: 1, dev: 1 };
  var incoming = new URLSearchParams(location.search);
  var carry = [];
  incoming.forEach(function (v, k) { if (!DEV_PARAMS[k]) carry.push([k, v]); });
  function withPageCarry(h) {  // relative demo page links: page.html?utm...#hash
    if (!carry.length || h.indexOf('?') > -1) return h;
    var hash = '';
    if (h.indexOf('#') > -1) { hash = h.slice(h.indexOf('#')); h = h.slice(0, h.indexOf('#')); }
    return h + '?' + carry.map(function (kv) { return encodeURIComponent(kv[0]) + '=' + encodeURIComponent(kv[1]); }).join('&') + hash;
  }
  function withCarry(href) {
    if (!carry.length) return href;
    try {
      var u = new URL(href, location.href);
      carry.forEach(function (kv) { if (!u.searchParams.has(kv[0])) u.searchParams.set(kv[0], kv[1]); });
      return u.toString();
    } catch (e) { return href; }
  }

  window.LBH_withCarry = function (h) { return withCarry(h); };
  function store(key, value) {
    try { if (value == null) localStorage.removeItem(key); else localStorage.setItem(key, value); } catch (e) { /* private mode */ }
  }
  function read(key) { try { return localStorage.getItem(key); } catch (e) { return null; } }

  /* ---------- Appearance ---------- */
  function themeMeta() {
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute('content', getComputedStyle(root).getPropertyValue('--bg').trim() || '#ffffff');
  }
  function syncThemeControls() {
    var pref = read(THEME_KEY) || 'system';
    var dark = root.dataset.theme === 'dark';
    document.querySelectorAll('.theme-toggle').forEach(function (b) {
      b.setAttribute('aria-pressed', dark ? 'true' : 'false');
      b.setAttribute('aria-label', dark ? 'מעבר למצב בהיר' : 'מעבר למצב כהה');
      b.title = dark ? 'מצב בהיר' : 'מצב כהה';
    });
    document.querySelectorAll('[data-appearance]').forEach(function (b) {
      b.setAttribute('aria-pressed', b.dataset.appearance === pref ? 'true' : 'false');
    });
    themeMeta();
  }
  function applyTheme(t) { root.dataset.theme = t; syncThemeControls(); }
  function setPreference(pref) {
    if (pref === 'system') { store(THEME_KEY, null); applyTheme(mq.matches ? 'dark' : 'light'); }
    else { store(THEME_KEY, pref); applyTheme(pref); }
  }
  var calmMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  function withReveal(from, change) {
    var before = root.dataset.theme, beforeDir = root.dataset.dir;
    if (!document.startViewTransition || calmMotion.matches || !from) { change(); return; }
    var r = from.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
    var far = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    var vt = document.startViewTransition(function () { change(); });
    vt.ready.then(function () {
      if (root.dataset.theme === before && root.dataset.dir === beforeDir) return;
      root.animate({ clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + far + 'px at ' + x + 'px ' + y + 'px)'] },
        { duration: 620, easing: 'cubic-bezier(.22, 1, .36, 1)', pseudoElement: '::view-transition-new(root)' });
    }).catch(function () {});
  }
  document.addEventListener('click', function (e) {
    var t = e.target.closest('.theme-toggle');
    if (t) { withReveal(t, function () { setPreference(root.dataset.theme === 'dark' ? 'light' : 'dark'); }); return; }
    var a = e.target.closest('[data-appearance]');
    if (a) withReveal(a, function () { setPreference(a.dataset.appearance); });
  });
  var onScheme = function () { if (!pinned && !read(THEME_KEY)) applyTheme(mq.matches ? 'dark' : 'light'); };
  if (mq.addEventListener) mq.addEventListener('change', onScheme); else if (mq.addListener) mq.addListener(onScheme);
  window.addEventListener('storage', function (e) {
    if (e.key === THEME_KEY && !pinned) applyTheme(e.newValue === 'light' || e.newValue === 'dark' ? e.newValue : (mq.matches ? 'dark' : 'light'));
  });
  syncThemeControls();

  /* ---------- Header ---------- */
  var header = document.querySelector('.site-header');
  var onScroll = function () { if (header) header.classList.toggle('scrolled', window.scrollY > 8); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Start chooser */
  document.querySelectorAll('.start').forEach(function (wrap) {
    var btn = wrap.querySelector('[data-start-toggle]');
    var pop = wrap.querySelector('.start-pop');
    if (!btn || !pop) return;
    function close(focus) { pop.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); if (focus) btn.focus(); }
    btn.addEventListener('click', function () {
      var open = !pop.classList.contains('open');
      pop.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) { var first = pop.querySelector('a'); if (first) first.focus(); }
    });
    document.addEventListener('click', function (e) { if (!wrap.contains(e.target)) close(false); });
    wrap.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close(true);
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        var items = Array.prototype.slice.call(pop.querySelectorAll('a'));
        var i = items.indexOf(document.activeElement);
        if (i < 0) return;
        e.preventDefault();
        items[(i + (e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length].focus();
      }
    });
  });

  /* Mobile drawer */
  var drawer = document.getElementById('drawer');
  document.querySelectorAll('[data-drawer-open]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (!drawer) return;
      if (drawer.showModal) drawer.showModal(); else drawer.setAttribute('open', '');
      b.setAttribute('aria-expanded', 'true');
    });
  });
  if (drawer) {
    drawer.addEventListener('close', function () { document.querySelectorAll('[data-drawer-open]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); }); });
    drawer.addEventListener('click', function (e) {
      if (e.target === drawer || e.target.closest('[data-drawer-close]') || e.target.closest('a')) drawer.close();
    });
  }

  /* ---------- Hero picker (radio group) ---------- */
  var picker = document.querySelector('.picker');
  if (picker) {
    var picks = Array.prototype.slice.call(picker.querySelectorAll('.pick'));
    var stage = document.querySelector('.stage');
    var cta = document.getElementById('hero-cta');
    var note = document.getElementById('hero-note');
    var more = document.getElementById('hero-more');
    function choose(p, focus) {
      picks.forEach(function (x) { var on = x === p; x.setAttribute('aria-checked', on ? 'true' : 'false'); x.tabIndex = on ? 0 : -1; });
      if (focus) p.focus();
      if (stage) stage.dataset.focus = p.dataset.cat;
      if (cta) {
        cta.href = withCarry(p.dataset.href);
        cta.dataset.flow = p.dataset.cat;
        cta.querySelector('.lbl').textContent = p.dataset.cta;
      }
      if (note) note.innerHTML = p.querySelector('template').innerHTML;
      if (more) { more.setAttribute('href', withPageCarry(p.dataset.page)); more.textContent = p.dataset.more; }
    }
    picks.forEach(function (p) {
      p.addEventListener('click', function () { choose(p, false); });
      p.addEventListener('keydown', function (e) {
        var i = picks.indexOf(p), n = null;
        // RTL: the visual next item is to the left
        if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') n = picks[(i + 1) % picks.length];
        if (e.key === 'ArrowRight' || e.key === 'ArrowUp') n = picks[(i + picks.length - 1) % picks.length];
        if (e.key === 'Home') n = picks[0];
        if (e.key === 'End') n = picks[picks.length - 1];
        if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); choose(p, false); return; }
        if (n) { e.preventDefault(); choose(n, true); }
      });
    });
    var start = picks.filter(function (p) { return p.getAttribute('aria-checked') === 'true'; })[0] || picks[0];
    choose(start, false);
  }

  /* ---------- Tabs ---------- */
  document.querySelectorAll('[role="tablist"]').forEach(function (list) {
    var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
    function select(t, focus) {
      tabs.forEach(function (x) {
        var on = x === t;
        x.setAttribute('aria-selected', on ? 'true' : 'false');
        x.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(x.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
      if (focus) t.focus();
    }
    tabs.forEach(function (t) {
      t.addEventListener('click', function () { select(t, false); });
      t.addEventListener('keydown', function (e) {
        var i = tabs.indexOf(t), n = null;
        if (e.key === 'ArrowLeft') n = tabs[(i + 1) % tabs.length];
        if (e.key === 'ArrowRight') n = tabs[(i + tabs.length - 1) % tabs.length];
        if (e.key === 'Home') n = tabs[0];
        if (e.key === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* Kids photo-to-cover pairs */
  document.querySelectorAll('[data-pairs]').forEach(function (box) {
    var main = box.querySelector('.pair-main img');
    var cap = box.querySelector('[data-pair-caption]');
    box.querySelectorAll('.pair-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        box.querySelectorAll('.pair-btn').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        main.src = b.dataset.src; main.alt = b.dataset.alt;
        if (cap) cap.textContent = b.dataset.title;
      });
    });
  });

  /* ---------- Review carousel ---------- */
  document.querySelectorAll('[data-carousel]').forEach(function (rv) {
    var track = rv.querySelector('.rv-track');
    var cards = Array.prototype.slice.call(track.children);
    var prev = rv.querySelector('.rv-nav.prev'), next = rv.querySelector('.rv-nav.next');
    var dotsBox = rv.querySelector('.rv-dots');
    var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var rtl = getComputedStyle(track).direction === 'rtl';
    function step() {
      if (!cards[0]) return 1;
      return cards[0].getBoundingClientRect().width + (parseFloat(getComputedStyle(track).columnGap) || 0);
    }
    function perView() { return Math.max(1, Math.round((track.clientWidth + 1) / step())); }
    function maxIndex() { return Math.max(0, cards.length - perView()); }
    function index() { return Math.min(maxIndex(), Math.round(Math.abs(track.scrollLeft) / step())); }
    function go(i) {
      i = Math.max(0, Math.min(i, maxIndex()));
      track.scrollTo({ left: (rtl ? -1 : 1) * i * step(), behavior: calm ? 'auto' : 'smooth' });
    }
    function buildDots() {
      var n = maxIndex() + 1;
      dotsBox.innerHTML = '';
      for (var i = 0; i < n; i++) {
        var b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('aria-label', 'ביקורת ' + (i + 1) + ' מתוך ' + cards.length);
        b.dataset.i = i;
        dotsBox.appendChild(b);
      }
      dotsBox.hidden = n < 2;
      sync();
    }
    function sync() {
      var i = index();
      Array.prototype.forEach.call(dotsBox.children, function (b, k) { b.setAttribute('aria-current', k === i ? 'true' : 'false'); });
      prev.disabled = i <= 0;
      next.disabled = i >= maxIndex();
    }
    var ticking = false;
    track.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { ticking = false; sync(); });
    }, { passive: true });
    prev.addEventListener('click', function () { go(index() - 1); });
    next.addEventListener('click', function () { go(index() + 1); });
    dotsBox.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) go(+b.dataset.i); });
    var t;
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(buildDots, 150); });
    buildDots();

    /* "Read the whole review": shown only when the text is cut */
    function checkMore() {
      cards.forEach(function (c) {
        var txt = c.querySelector('.rv-text'), btn = c.querySelector('.rv-more');
        if (!txt || !btn || txt.classList.contains('open')) return;
        btn.hidden = txt.scrollHeight <= txt.clientHeight + 2;
      });
    }
    rv.addEventListener('click', function (e) {
      var btn = e.target.closest('.rv-more');
      if (!btn) return;
      var txt = document.getElementById(btn.getAttribute('aria-controls'));
      var open = !txt.classList.contains('open');
      txt.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'פחות' : 'לקריאת כל הביקורת';
    });
    checkMore();
    window.addEventListener('resize', checkMore);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(checkMore);
  });

  /* ---------- Segmented controls: a glass thumb slides to the chosen segment ---------- */
  function glideOne(group) {
    var g = group.querySelector(':scope > .glider');
    if (!g) { g = document.createElement('span'); g.className = 'glider'; g.setAttribute('aria-hidden', 'true'); group.insertBefore(g, group.firstChild); }
    var on = group.querySelector('[aria-selected="true"], [aria-pressed="true"]');
    if (!on || !on.offsetWidth) { g.style.opacity = '0'; return; }
    var gr = group.getBoundingClientRect(), r = on.getBoundingClientRect();
    g.style.opacity = '1';
    g.style.width = r.width + 'px';
    g.style.transform = 'translateX(' + (r.left - gr.left + group.scrollLeft) + 'px)';
  }
  function glide(scope) {
    (scope || document).querySelectorAll('.tabs, .seg, .filters[data-filter-for]').forEach(function (grp) {
      if (!grp.dataset.glide) {
        grp.dataset.glide = '1';
        new MutationObserver(function () { glideOne(grp); }).observe(grp, { subtree: true, attributes: true, attributeFilter: ['aria-selected', 'aria-pressed'] });
      }
      glideOne(grp);
    });
  }
  window.LBH_glide = glide;
  glide();
  window.addEventListener('resize', function () { glide(); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { glide(); });
  document.addEventListener('toggle', function () { glide(); }, true);

  /* ---------- Light follows the pointer across glass and buttons ---------- */
  var litSel = '.btn-primary, .pick, .final-card, .site-header .hdr';
  var litEl = null, litX = 0, litY = 0, litQueued = false;
  document.addEventListener('pointermove', function (e) {
    if (e.pointerType !== 'mouse') return;
    litEl = e.target.closest && e.target.closest(litSel); litX = e.clientX; litY = e.clientY;
    if (!litEl || litQueued) return;
    litQueued = true;
    requestAnimationFrame(function () {
      litQueued = false; if (!litEl) return;
      var r = litEl.getBoundingClientRect();
      litEl.style.setProperty('--mx', (litX - r.left) + 'px');
      litEl.style.setProperty('--my', (litY - r.top) + 'px');
    });
  }, { passive: true });

  /* ---------- Gallery filter ---------- */
  document.querySelectorAll('[data-filter-for]').forEach(function (bar) {
    var gallery = document.getElementById(bar.dataset.filterFor);
    var status = document.getElementById(bar.dataset.filterFor + '-status');
    bar.querySelectorAll('.filter').forEach(function (f) {
      f.addEventListener('click', function () {
        bar.querySelectorAll('.filter').forEach(function (x) { x.setAttribute('aria-pressed', x === f ? 'true' : 'false'); });
        var cat = f.dataset.cat, shown = 0;
        gallery.querySelectorAll('.g-item').forEach(function (it) {
          var on = cat === 'all' || it.dataset.cat === cat;
          it.hidden = !on; if (on) shown++;
        });
        if (status) status.textContent = 'מוצגות ' + shown + ' דוגמאות';
      });
    });
  });

  /* ---------- Reveal on scroll ---------- */
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var reveals = document.querySelectorAll('.reveal');
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- Attribution and analytics ----------
     Every link into the store keeps the visitor's campaign parameters, so attribution survives the new home page.
     Links between the demo pages keep them too, so a visitor who browses first still carries them. */
  if (carry.length) {
    document.querySelectorAll('a[data-flow], a[data-store]').forEach(function (a) { a.href = withCarry(a.getAttribute('href')); });
    document.querySelectorAll('a[href$=".html"], a[href*=".html#"]').forEach(function (a) {
      if (a.closest('.dev-dir')) return;
      a.setAttribute('href', withPageCarry(a.getAttribute('href')));
    });
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-flow]');
    if (!a) return;
    var payload = { event: 'start_flow', flow: a.dataset.flow, placement: a.dataset.place || '' };
    if (window.dataLayer && window.dataLayer.push) window.dataLayer.push(payload);
  });

  /* ---------- Dev only: switch versions (purple tint, yellow tint, both) ---------- */
  var devBox = document.querySelector('.dev-dir');
  var isDev = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname) || incoming.get('dev') === '1';
  function syncDev() {
    if (!devBox) return;
    devBox.querySelectorAll('[data-dir-set]').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.dirSet === root.dataset.dir ? 'true' : 'false'); });
  }
  if (devBox && isDev && window.self === window.top) {
    devBox.hidden = false;
    devBox.addEventListener('click', function (e) {
      var b = e.target.closest('[data-dir-set]');
      if (b) withReveal(b, function () { root.dataset.dir = b.dataset.dirSet; if (!pinned) store(DIR_KEY, b.dataset.dirSet); syncDev(); themeMeta(); });
      if (e.target.closest('.x')) devBox.hidden = true;
    });
    syncDev();
  }
  window.addEventListener('storage', function (e) {
    if (e.key === DIR_KEY && !pinned && /^(purple|yellow|both)$/.test(e.newValue || '')) { root.dataset.dir = e.newValue; syncDev(); themeMeta(); }
  });
})();
