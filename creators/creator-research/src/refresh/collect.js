// Weekly refresh collector. Paste the whole file into javascript_tool on an instagram.com tab of the built-in browser
// (signed in, read only). Run it again until it returns done:true; progress survives hard reloads in localStorage.
// First call: set localStorage.__rf_todo to a JSON array of handles (see refresh/README.md), or this returns need:"todo".
// Each run works about 30 seconds, then returns a progress count. It never follows, likes, comments or sends anything.
(async () => {
  if (!localStorage.__rf_todo) return { need: "todo" };
  if (!window.__rfh) {
    window.__rfh = 1; window.__rfcap = [];
    const oo = XMLHttpRequest.prototype.open, os = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function () { return oo.apply(this, arguments) };
    XMLHttpRequest.prototype.send = function () { this.addEventListener("load", () => { try { if (this.responseText && this.responseText[0] === "{") window.__rfcap.push(this.responseText) } catch (e) {} }); return os.apply(this, arguments) };
    const of = window.fetch;
    window.fetch = async function (...a) { const r = await of.apply(this, a); try { r.clone().text().then(t => { if (t && t[0] === "{") window.__rfcap.push(t) }) } catch (e) {} return r };
  }
  const TODO = JSON.parse(localStorage.__rf_todo), R = JSON.parse(localStorage.__rf_out || "{}");
  // a profile that forced a hard reload last time is recorded as not loaded, so the run moves on
  // a missing handle (renamed or deleted) usually forces a hard reload, so a profile that did that is recorded as not loaded
  const pend = localStorage.__rf_pend; if (pend && !(pend in R)) { R[pend] = { err: "reload" }; localStorage.__rf_out = JSON.stringify(R) }
  const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
  const day = c => { let id = 0n; for (const ch of c.slice(0, 11)) id = id * 64n + BigInt(A.indexOf(ch)); return new Date(Number((id >> 23n) + 1314220021721n)).toISOString().slice(0, 10) };
  const LB = /lumebook|לומבוק/i;
  const t0 = Date.now();
  for (const h of TODO) {
    if (h in R) continue;
    if (Date.now() - t0 > 30000) break;
    localStorage.__rf_pend = h; window.__rfcap = [];
    history.pushState({}, "", "/" + h + "/reels/"); window.dispatchEvent(new PopStateEvent("popstate", { state: {} }));
    let user = null; const reels = {}; const s = Date.now();
    while (Date.now() - s < 5000) {
      await new Promise(r => setTimeout(r, 500)); user = null;
      for (const c of window.__rfcap) {
        try {
          (function walk(o) {
            if (!o || typeof o !== "object") return;
            if (Array.isArray(o)) { o.forEach(walk); return }
            if (o.username === h && o.follower_count != null) user = user || o;
            if (o.code && o.play_count != null) {
              const tags = ((o.usertags && o.usertags.in) || []).map(t => t.user && t.user.username).concat((o.coauthor_producers || []).map(u => u.username));
              const cap = (o.caption && o.caption.text) || "";
              reels[o.code] = { v: o.play_count, lb: LB.test(cap) || tags.some(u => LB.test(u || "")) };
            }
            for (const k in o) walk(o[k]);
          })(JSON.parse(c));
        } catch (e) {}
      }
      if (user && Object.keys(reels).length >= 6) break;
    }
    if (!user) { R[h] = { err: "notfound" }; localStorage.__rf_out = JSON.stringify(R); continue }
    const codes = Object.keys(reels), views = codes.map(c => reels[c].v).sort((a, b) => a - b), dates = codes.map(day).sort();
    R[h] = { fc: user.follower_count, pk: String(user.pk || user.id || ""), priv: user.is_private ? 1 : 0, n: user.full_name || "",
      med: views.length ? views[Math.floor(views.length / 2)] : null, nr: views.length, last: dates[dates.length - 1] || null,
      lb: codes.filter(c => reels[c].lb).map(c => ({ code: c, day: day(c), v: reels[c].v })) };
    localStorage.__rf_out = JSON.stringify(R);
  }
  localStorage.removeItem("__rf_pend");
  const done = TODO.every(h => h in R);
  return { done, have: Object.keys(R).length, of: TODO.length, notLoaded: Object.entries(R).filter(([, x]) => x.err).map(([h]) => h) };
})()
