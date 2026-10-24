// Weekly creator search, step 3: read each shortlisted profile in full (exact followers, bio, bio links, category and the
// latest 12 reels' views, likes and comments, for weekly/gate.py), the same way as the 18 Oct 2026 pass. Read only. Set localStorage.__cw_P to a JSON array of
// handles first, then run this again until it returns done:true (about 20 profiles per 30-second call; a profile that
// forces a hard reload is recorded as not loaded and skipped). When done, localStorage.__cw_out holds every profile read
// so far as {h, pk, fc, n, bio, links, ext, cat, priv, med, max, nr, last, prev, rl}; rl is the 12 newest reels as
// [code, day, views, likes, comments] (hidden likes = null). Copy it out with export.js.
(async () => {
  if (!document.cookie.includes("ds_user_id")) return { stop: "signed out of Instagram" };
  if (!localStorage.__cw_P) return { need: "set localStorage.__cw_P to the shortlisted handles" };
  if (!window.__cwh) {                              // capture every JSON response the app loads (reinstalled after a hard reload)
    window.__cwh = 1; window.__cwcap = [];
    const os = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function () { this.addEventListener("load", () => { try { if (this.responseText && this.responseText[0] === "{") window.__cwcap.push(this.responseText) } catch (e) {} }); return os.apply(this, arguments) };
    const of = window.fetch;
    window.fetch = async function (...a) { const r = await of.apply(this, a); try { r.clone().text().then(t => { if (t && t[0] === "{") window.__cwcap.push(t) }) } catch (e) {} return r };
  }
  const P = JSON.parse(localStorage.__cw_P), B = JSON.parse(localStorage.__cw_B || "{}");
  const pend = localStorage.__cw_pend; if (pend && !(pend in B)) { B[pend] = { err: "reload" }; localStorage.__cw_B = JSON.stringify(B) }
  const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
  const day = c => { let id = 0n; for (const ch of c.slice(0, 11)) id = id * 64n + BigInt(A.indexOf(ch)); return new Date(Number((id >> 23n) + 1314220021721n)).toISOString().slice(0, 10) };
  const t0 = Date.now();
  for (const h of P) {
    if (h in B) continue;
    if (Date.now() - t0 > 30000) break;
    localStorage.__cw_pend = h; window.__cwcap = [];
    history.pushState({}, "", "/" + h + "/reels/"); window.dispatchEvent(new PopStateEvent("popstate", { state: {} }));
    let user = null; const reels = {}; const s = Date.now();
    while (Date.now() - s < 5000) {
      await new Promise(r => setTimeout(r, 500)); user = null;
      for (const c of window.__cwcap) {
        try {
          (function walk(o) {
            if (!o || typeof o !== "object") return;
            if (Array.isArray(o)) { o.forEach(walk); return }
            if (o.username === h && o.follower_count != null) user = user || o;
            if (o.code && o.play_count != null) { const p = reels[o.code] || {};
              reels[o.code] = { v: o.play_count, l: o.like_and_view_counts_disabled ? null : (o.like_count != null ? o.like_count : (p.l != null ? p.l : null)), m: o.comment_count != null ? o.comment_count : (p.m != null ? p.m : null) } }
            for (const k in o) walk(o[k]);
          })(JSON.parse(c));
        } catch (e) {}
      }
      if (user && Object.keys(reels).length >= 6) break;
    }
    const codes = Object.keys(reels), v = codes.map(c => reels[c].v).sort((a, b) => a - b), dates = codes.map(day).sort();
    B[h] = user ? { pk: String(user.pk || user.id || ""), fc: user.follower_count, n: user.full_name || "", bio: user.biography || "", links: (user.bio_links || []).map(l => l.url), ext: user.external_url || "",
      cat: user.category || "", priv: user.is_private ? 1 : 0, med: v.length ? v[Math.floor(v.length / 2)] : null, max: v.length ? v[v.length - 1] : null, nr: v.length,
      last: dates[dates.length - 1] || null, prev: dates[dates.length - 2] || null,
      rl: codes.slice().sort((a, b) => day(b).localeCompare(day(a))).slice(0, 12).map(c => [c, day(c), reels[c].v, reels[c].l, reels[c].m]) } : { err: "notfound" };
    localStorage.__cw_B = JSON.stringify(B);
  }
  localStorage.removeItem("__cw_pend");
  const done = P.every(h => h in B);
  if (done) localStorage.__cw_out = JSON.stringify(Object.entries(B).map(([h, x]) => Object.assign({ h }, x)));
  return { done, read: Object.keys(B).length, of: P.length, notLoaded: Object.entries(B).filter(([, x]) => x.err).map(([h]) => h) };
})()
