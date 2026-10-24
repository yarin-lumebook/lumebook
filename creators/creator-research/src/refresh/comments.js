// Weekly refresh, comments step: reads the first page of comments (Instagram's own order, up to 15) on each reel in
// localStorage.__rc_todo, a JSON array of reel codes from `python3 comments.py todo` (read only: one GET per reel, nothing
// is liked, followed or sent). Run it again until it returns done:true; each call works about 30 seconds.
// Each reel is kept under its own key (__rc_p_<code>). When they add up to about 1.2 million characters the call returns
// export:true: export them (export.js with window.__XK="__rc_p_"), ingest the file (comments.py ingest), run
// clear.js, then carry on. done:true with export:true means one last export and ingest.
(async () => {
  if (!document.cookie.includes("ds_user_id")) return { stop: "signed out of Instagram" };
  if (!localStorage.__rc_todo) return { need: "set localStorage.__rc_todo (python3 comments.py todo)" };
  const T = JSON.parse(localStorage.__rc_todo), D = JSON.parse(localStorage.__rc_done || "{}");
  const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
  const pk = c => { let id = 0n; for (const ch of c.slice(0, 11)) id = id * 64n + BigInt(A.indexOf(ch)); return id.toString() };   // a reel code is its media id in base 64
  const waiting = () => Object.keys(localStorage).filter(k => k.startsWith("__rc_p_")).length;
  const t0 = Date.now();
  for (const code of T) {
    if (code in D) continue;
    if (+(localStorage.__rc_sz || 0) > 1200000) return { export: true, read: Object.keys(D).length, of: T.length, waiting: waiting() };
    if (Date.now() - t0 > 30000) break;
    const r = await fetch(`/api/v1/media/${pk(code)}/comments/?can_support_threading=true&permalink_enabled=false`,
      { headers: { "x-ig-app-id": "936619743392459", "x-requested-with": "XMLHttpRequest" }, credentials: "include" });
    if (r.status === 429) return { stop: "429 too many requests", read: Object.keys(D).length, of: T.length };
    const t = await r.text();
    if (t[0] !== "{") { if (r.status === 401 || r.status === 403) return { stop: "Instagram refused (" + r.status + "): signed out or checkpoint" }; D[code] = 0; localStorage.__rc_done = JSON.stringify(D); continue }
    const j = JSON.parse(t);
    if (j.status === "fail") { if (/checkpoint|login|challenge/i.test(j.message || "")) return { stop: "Instagram: " + (j.message || "fail") }; D[code] = 0; localStorage.__rc_done = JSON.stringify(D); continue }
    const owner = j.caption && j.caption.user && j.caption.user.username;
    // per comment: 1 when the reel's own creator wrote it, and the text. No commenter names are kept.
    const rec = JSON.stringify({ cap: ((j.caption && j.caption.text) || "").slice(0, 800), tot: j.comment_count,
      cm: (j.comments || []).map(c => [owner && c.user && c.user.username === owner ? 1 : 0, (c.text || "").slice(0, 300)]) });
    localStorage.setItem("__rc_p_" + code, rec); localStorage.__rc_sz = +(localStorage.__rc_sz || 0) + rec.length;
    D[code] = 1; localStorage.__rc_done = JSON.stringify(D);
    await new Promise(z => setTimeout(z, 300));
  }
  const done = T.every(c => c in D), w = waiting();
  return { done, read: Object.keys(D).length, of: T.length, failed: Object.values(D).filter(v => !v).length, waiting: w, export: w > 0 && (done || +(localStorage.__rc_sz || 0) > 1200000) };
})()
