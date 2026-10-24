// Weekly creator search, step 2: a quick screen of every account chain.js found, from its profile page alone
// (the meta description gives rounded followers and the bio). Read only. Run it again until it returns done:true;
// about 650 profiles per 28-second call. When done it writes the accounts in range (4,500 to 55,000 rounded followers)
// to localStorage.__cw_out as [handle, pk, full name, times suggested, followers, bio, suggested by]; copy it out with export.js.
(async () => {
  if (!document.cookie.includes("ds_user_id")) return { stop: "signed out of Instagram" };
  if (!localStorage.__cw_u) return { need: "run chain.js first" };
  const U = JSON.parse(localStorage.__cw_u);
  // names that were never a fit in four passes: birth, sleep, food, shops, beauty, fitness, weddings, pets, real estate
  const EX = /הנקה|לידה|דולה|מיילדת|תזונ|דיאט|שינה|sleep|doula|midwife|birth|nutri|shop|store|חנות|בוטיק|עיצוב|מאפ|עוגות|cake|קייטרינג|nail|ציפורנ|makeup|איפור|hair|שיער|פילאטיס|יוגה|fitness|כושר|נדל|ריסים|lash|כלב|dog|wedding|חתונ|צלמת הריון|real estate|beauty|קוסמטי|food|אוכל|מתכונ|recipe|הריון|pregnan|tattoo|קעקוע|אופנה|fashion|בגדי/i;
  if (!localStorage.__cw_L) localStorage.__cw_L = JSON.stringify(Object.entries(U).filter(([k, x]) => !x.priv && !EX.test(x.n) && !EX.test(k)).map(([k]) => k));
  const L = JSON.parse(localStorage.__cw_L), R = JSON.parse(localStorage.__cw_R || "{}");
  const todo = L.filter(h => !(h in R));
  const dec = s => { const e = document.createElement("textarea"); e.innerHTML = s; return e.value };
  const pf = s => { const m = s.match(/^([\d.,]+)([KM]?) Followers/); if (!m) return -1; let n = parseFloat(m[1].replace(/,/g, "")); if (m[2] == "K") n *= 1000; if (m[2] == "M") n *= 1e6; return Math.round(n) };
  const t0 = Date.now(); let i = 0, bad = 0, blank = 0;
  await Promise.all(Array.from({ length: 16 }, async () => {
    while (i < todo.length && Date.now() - t0 < 28000 && bad < 8 && blank < 40) {
      const h = todo[i++];
      try {
        const r = await fetch("/" + h + "/", { credentials: "include" });
        if (r.status === 429) { bad++; continue }      // not recorded, so the next call tries it again
        const m = (await r.text()).match(/<meta content="([^"]*)" name="description"/);
        if (!m) { R[h] = -2; blank++; continue }
        blank = 0;
        const d = dec(m[1]), f = pf(d);
        if (f >= 4500 && f <= 55000) { const b = d.match(/on Instagram: "([\s\S]*)"$/); R[h] = [f, (b ? b[1] : "").slice(0, 400)] } else R[h] = f;
      } catch (e) { bad++ }
    }
  }));
  localStorage.__cw_R = JSON.stringify(R);
  const v = Object.values(R), done = L.every(h => h in R);
  if (done) localStorage.__cw_out = JSON.stringify(Object.entries(R).filter(([, x]) => Array.isArray(x)).map(([h, x]) => [h, U[h].pk, U[h].n, U[h].c, x[0], x[1], U[h].from]));
  const res = { done, of: L.length, screened: v.length, inRange: v.filter(Array.isArray).length, noMeta: v.filter(x => x === -2).length };
  if (bad >= 8) res.stop = "Instagram answered 429 eight times in this call: stop and report";
  if (blank >= 40) res.stop = "40 profile pages in a row came back without a description (signed out or a checkpoint): stop and report";
  return res;
})()
