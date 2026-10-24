// Weekly refresh: after a comments export is ingested, removes the exported reels (__rc_p_*) and resets the size count.
// With window.__ALL=1 in the same call it removes every key the refresh wrote (__rf_*, __rc_*): run that at the start and the end.
(() => {
  const all = window.__ALL; window.__ALL = 0;
  const k = Object.keys(localStorage).filter(x => all ? (x.startsWith("__rf_") || x.startsWith("__rc_")) : x.startsWith("__rc_p_"));
  k.forEach(x => localStorage.removeItem(x)); if (!all) localStorage.__rc_sz = 0;
  return { removed: k.length };
})()
