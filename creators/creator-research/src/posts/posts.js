// Daily read of the creators' posts linked in the books table ("ספרים שנוצרו"). Paste the whole file into javascript_tool
// on an instagram.com tab of the built-in browser (signed in, read only). First call: start it with
// `window.__PP=<what posts.py todo printed>;` so it knows which posts to read. Run it again until it returns done:true;
// progress survives hard reloads in localStorage.__pp_out. The done call returns `out`: save it to a file for posts.py ingest.
// Per post it opens the owner's reels tab (up to 4 pages, then 2 of the posts grid) and takes the post's views
// (play_count), likes and comments from what Instagram's own page loads, the way refresh/collect.js reads profiles.
// It never follows, likes, comments, sends or opens messages.
(async () => {
  if (!document.cookie.includes("ds_user_id")) return { stop: "signed out of Instagram" };
  if (window.__PP) { localStorage.__pp_todo = JSON.stringify(window.__PP); localStorage.removeItem("__pp_out"); localStorage.removeItem("__pp_pend"); window.__PP = null }
  if (!localStorage.__pp_todo) return { need: "todo" };
  if (!window.__pph) {
    window.__pph = 1; window.__ppcap = [];
    const os = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function () { this.addEventListener("load", () => { try { if (this.responseText && this.responseText[0] === "{") window.__ppcap.push(this.responseText) } catch (e) {} }); return os.apply(this, arguments) };
    const of = window.fetch;
    window.fetch = async function (...a) { const r = await of.apply(this, a); try { r.clone().text().then(t => { if (t && t[0] === "{") window.__ppcap.push(t) }) } catch (e) {} return r };
  }
  const TODO = JSON.parse(localStorage.__pp_todo), R = JSON.parse(localStorage.__pp_out || "{}");
  const BY = {}; for (const p of TODO) (BY[p.h] = BY[p.h] || []).push(p.c);   // one visit per profile: Instagram reuses a profile it already loaded
  // a profile that forced a hard reload last time (a renamed or deleted handle does this): its posts are recorded as not found
  const pend = localStorage.__pp_pend; if (pend && BY[pend]) { BY[pend].forEach(c => { if (!(c in R)) R[c] = { err: "reload" } }); localStorage.__pp_out = JSON.stringify(R) }
  const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
  const day = c => { let id = 0n; for (const ch of c.slice(0, 11)) id = id * 64n + BigInt(A.indexOf(ch)); return new Date(Number((id >> 23n) + 1314220021721n)).toISOString().slice(0, 10) };
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const scan = (want, hits, via) => {               // every wanted post in what the page has loaded so far
    for (const c of window.__ppcap) {
      try {
        (function walk(o) {
          if (!o || typeof o !== "object") return;
          if (Array.isArray(o)) { o.forEach(walk); return }
          if (want.includes(o.code) && !hits[o.code] && (o.play_count != null || o.like_count != null || o.comment_count != null)) hits[o.code] = [o, via];
          for (const k in o) walk(o[k]);
        })(JSON.parse(c));
      } catch (e) {}
    }
    return want.every(c => hits[c]);
  };
  // the browser tool stops a call after 45 seconds: a profile can take about 20 (posts not found: 4 pages of reels, 2 of
  // the grid), so a new profile starts only in the first 15 seconds of a call
  const t0 = Date.now();
  for (const h of Object.keys(BY)) {
    const want = BY[h].filter(c => !(c in R)); if (!want.length) continue;
    if (Date.now() - t0 > 15000) break;
    localStorage.__pp_pend = h;
    const hits = {};
    for (const [tab, pages] of [["reels/", 4], ["", 2]]) {   // reels carry the views; the posts grid also has photos and carousels
      window.__ppcap = []; window.scrollTo(0, 0);
      history.pushState({}, "", "/" + h + "/" + tab); window.dispatchEvent(new PopStateEvent("popstate", { state: {} }));
      let all = false;
      for (let page = 0; page < pages && !all; page++) {
        const s = Date.now();
        while (Date.now() - s < 3000 && !(all = scan(want, hits, tab ? "reels" : "grid"))) await sleep(400);
        if (!all) { window.scrollTo(0, document.body.scrollHeight); await sleep(300) }
      }
      if (all) break;
    }
    window.scrollTo(0, 0);
    for (const c of want) {
      const [o, via] = hits[c] || [];
      R[c] = o ? { v: o.play_count != null ? o.play_count : o.ig_play_count != null ? o.ig_play_count : null,
        l: o.like_and_view_counts_disabled ? null : (o.like_count != null ? o.like_count : null),
        m: o.comment_count != null ? o.comment_count : null, on: day(c), u: (o.user && o.user.username) || h, via } : { err: "notfound" };
    }
    localStorage.__pp_out = JSON.stringify(R);
  }
  localStorage.removeItem("__pp_pend");
  const done = TODO.every(p => p.c in R);
  const res = { done, have: Object.keys(R).length, of: TODO.length, notFound: Object.entries(R).filter(([, x]) => x.err).map(([c]) => c) };
  if (done) res.out = R;                          // kept in localStorage until the next run starts, in case this reply is lost
  return res;
})()
