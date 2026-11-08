// Profile pictures for the creator cards. Paste into javascript_tool on a signed-in instagram.com tab of the built-in browser
// (read only, nothing is followed, liked or sent). First call: set localStorage.__pic_todo to a JSON array of handles.
// Run again until it returns done:true; then read localStorage.__pic_out ({handle: picture url}) and give it to pics.py.
// Each run works about 40 seconds. Returns {stop} on a login page or a rate limit: stop the whole run, never retry in a loop.
(async () => {
  if (!document.cookie.includes("ds_user_id")) return { stop: "signed out of Instagram" };
  if (!localStorage.__pic_todo) return { need: "todo" };
  if (!window.__pich) {
    window.__pich = 1; window.__piccap = [];
    const oo = XMLHttpRequest.prototype.open, os = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function () { return oo.apply(this, arguments) };
    XMLHttpRequest.prototype.send = function () { this.addEventListener("load", () => { try { if (this.status === 429) window.__pic429 = 1; if (this.responseText && this.responseText[0] === "{") window.__piccap.push(this.responseText) } catch (e) {} }); return os.apply(this, arguments) };
    const of = window.fetch;
    window.fetch = async function (...a) { const r = await of.apply(this, a); try { if (r.status === 429) window.__pic429 = 1; r.clone().text().then(t => { if (t && t[0] === "{") window.__piccap.push(t) }) } catch (e) {} return r };
  }
  const TODO = JSON.parse(localStorage.__pic_todo), R = JSON.parse(localStorage.__pic_out || "{}");
  const pend = localStorage.__pic_pend; if (pend && !(pend in R)) { R[pend] = ""; localStorage.__pic_out = JSON.stringify(R) }
  const t0 = Date.now(); let n = 0;
  for (const h of TODO) {
    if (h in R) continue;
    if (Date.now() - t0 > 40000) break;
    if (window.__pic429) return { stop: "rate limited (429)", done_so_far: Object.keys(R).length };
    localStorage.__pic_pend = h; window.__piccap = [];
    history.pushState({}, "", "/" + h + "/"); window.dispatchEvent(new PopStateEvent("popstate", { state: {} }));
    let pic = "", s = Date.now();
    while (Date.now() - s < 4000 && !pic) {
      await new Promise(r => setTimeout(r, 400));
      for (const c of window.__piccap) {
        try { (function walk(o) { if (!o || typeof o !== "object" || pic) return; if (Array.isArray(o)) { o.forEach(walk); return } if (o.username === h && (o.profile_pic_url_hd || o.profile_pic_url)) { pic = o.profile_pic_url_hd || o.profile_pic_url; return } for (const k in o) walk(o[k]) })(JSON.parse(c)) } catch (e) {}
      }
    }
    R[h] = pic; localStorage.__pic_out = JSON.stringify(R); n++;
    await new Promise(r => setTimeout(r, 800 + Math.random() * 800));
  }
  const left = TODO.filter(h => !(h in R)).length;
  return { done: left === 0, left, got: Object.values(R).filter(Boolean).length, read: Object.keys(R).length };
})()
