(function(){
  var pages = Array.prototype.slice.call(document.querySelectorAll('.page'));
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav a[data-route]'));
  var toc = document.querySelector('.lb-topbar .lb-toc');
  var tocLinks = toc ? Array.prototype.slice.call(toc.querySelectorAll('a[data-routes]')) : [];
  var nav = document.getElementById('nav');
  var scrim = document.querySelector('.scrim');
  var menu = document.querySelector('.menu');
  var toast = document.querySelector('.toast');
  var toastTimer = null;

  function showToast(msg){
    toast.textContent = msg; toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function(){ toast.hidden = true; }, 2600);
  }
  function setDrawer(open){
    nav.classList.toggle('open', open);
    nav.classList.toggle('is-open', open);
    scrim.hidden = !open;
    if (menu) menu.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  function route(){
    var id = (location.hash || '').replace('#','');
    if (!document.querySelector('[data-page="' + id + '"]')) id = 's1';
    pages.forEach(function(p){ p.hidden = p.getAttribute('data-page') !== id; });
    links.forEach(function(a){
      var on = a.getAttribute('data-route') === id;
      a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    // top bar: light the pill of the part this section belongs to
    var activePill = null;
    tocLinks.forEach(function(a){
      var on = (' ' + a.getAttribute('data-routes') + ' ').indexOf(' ' + id + ' ') >= 0;
      a.setAttribute('aria-current', on ? 'true' : 'false');
      if (on) activePill = a;
    });
    if (activePill && toc.scrollWidth > toc.clientWidth && activePill.scrollIntoView) activePill.scrollIntoView({block:'nearest', inline:'nearest'});
    nav.classList.toggle('show-c', id === 's19' || id.charAt(0) === 'c');
    var active = nav.querySelector('a.active');
    if (active && active.scrollIntoView) active.scrollIntoView({block:'nearest'});
    window.scrollTo(0, 0);
    setDrawer(false);
  }
  window.addEventListener('hashchange', route);
  route();

  if (menu) menu.addEventListener('click', function(){ setDrawer(!nav.classList.contains('open')); });
  scrim.addEventListener('click', function(){ setDrawer(false); });
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') setDrawer(false); });

  // copy all slide text of a concept (for Canva)
  document.addEventListener('click', function(e){
    var btn = e.target.closest('.copy');
    if (!btn) return;
    var text = btn.getAttribute('data-copy');
    function fallback(){
      var box = btn.parentNode.parentNode.querySelector('.copy-fallback');
      if (!box){
        box = document.createElement('textarea');
        box.className = 'copy-fallback lb-textarea'; box.readOnly = true;
        btn.parentNode.insertAdjacentElement('afterend', box);
      }
      box.value = text; box.focus(); box.select();
      showToast('הטקסט מסומן. העתיקו אותו ידנית');
    }
    try {
      navigator.clipboard.writeText(text).then(function(){ showToast('הטקסט של כל השקופיות הועתק'); }, fallback);
    } catch (err) { fallback(); }
  });

  // checklist ticks are remembered in this browser only
  var KEY = 'lb-playbook-checks';
  var boxes = Array.prototype.slice.call(document.querySelectorAll('li.check input'));
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (err) { saved = {}; }
  boxes.forEach(function(b, i){
    b.id = 'chk-' + i;
    b.checked = !!saved[i];
    b.addEventListener('change', function(){
      saved[i] = b.checked;
      try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (err) {}
    });
  });
})();
