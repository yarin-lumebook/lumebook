// Weekly creator search, step 1: Instagram's similar-accounts list for every creator already in the map.
// Paste the whole file into javascript_tool on a signed-in instagram.com tab of the built-in browser. Read only: it never
// follows, likes, comments or sends anything. First set the inputs printed by `python3 weekly/prep.py` (localStorage
// __cw_seeds and __cw_have), then run this again until it returns done:true. Each call works about 28 seconds and keeps
// its progress in localStorage, so a hard reload loses nothing.
(async () => {
  if (!document.cookie.includes("ds_user_id")) return { stop: "signed out of Instagram" };
  if (!localStorage.__cw_seeds || !localStorage.__cw_have) return { need: "seeds: run the prep.py output first" };
  const SEEDS = JSON.parse(localStorage.__cw_seeds), have = new Set(JSON.parse(localStorage.__cw_have));
  const PK = JSON.parse(localStorage.__cw_pk || "{}"), CD = JSON.parse(localStorage.__cw_cd || "{}"), U = JSON.parse(localStorage.__cw_u || "{}");
  const H = { headers: { "x-ig-app-id": "936619743392459" }, credentials: "include" };
  for (const [h, p] of SEEDS) if (p && !(h in PK)) PK[h] = String(p);
  const t0 = Date.now(), live = () => Date.now() - t0 < 28000 && bad < 8;
  let bad = 0, i = 0;
  // a seed without a known pk: the profile page carries it as "profile_id" ("" = the handle no longer exists)
  const nopk = SEEDS.map(s => s[0]).filter(h => !(h in PK));
  await Promise.all(Array.from({ length: 12 }, async () => {
    while (i < nopk.length && live()) {
      const h = nopk[i++];
      try {
        const r = await fetch("/" + h + "/", { credentials: "include" });
        if (r.status !== 200 && r.status !== 404) { bad++; continue }
        const m = (await r.text()).match(/"profile_id":"(\d+)"/); PK[h] = m ? m[1] : "";
      } catch (e) { bad++ }
    }
  }));
  localStorage.__cw_pk = JSON.stringify(PK);
  // similar accounts, 4 at a time (no 429 at this pace on 18 Oct 2026); dedupe by username, keep the pk for the merge
  const todo = SEEDS.map(s => s[0]).filter(h => h in PK && !(h in CD)); i = 0;
  await Promise.all(Array.from({ length: 4 }, async () => {
    while (i < todo.length && live()) {
      const h = todo[i++];
      if (!PK[h]) { CD[h] = -1; continue }
      try {
        const r = await fetch("/api/v1/discover/chaining/?target_id=" + PK[h], H);
        if (r.status !== 200) { if (r.status === 404) CD[h] = -1; else bad++; continue }
        const j = await r.json(); CD[h] = (j.users || []).length;
        for (const u of j.users || []) {
          if (have.has(u.username)) continue;
          const x = U[u.username] || (U[u.username] = { pk: String(u.pk), n: u.full_name || "", priv: u.is_private ? 1 : 0, c: 0, from: [] });
          x.c++; if (x.from.length < 3) x.from.push(h);
        }
      } catch (e) { bad++ }       // HTML instead of JSON: signed out or a checkpoint page
    }
  }));
  localStorage.__cw_cd = JSON.stringify(CD); localStorage.__cw_u = JSON.stringify(U);
  const done = SEEDS.every(s => s[0] in CD);
  const res = { done, seeds: SEEDS.length, chained: Object.keys(CD).length, failed: Object.values(CD).filter(x => x < 0).length, unseen: Object.keys(U).length };
  if (bad >= 8) res.stop = "Instagram refused 8 requests in this call (rate limit or checkpoint): stop and report";
  return res;
})()
