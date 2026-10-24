// Optional second hop, when the first shortlist gives fewer than about 110 good profiles: the profiles read.js read
// become the seeds, and every account already found or screened joins the known list, so chain.js and screen.js only
// look at new accounts. Profiles already read stay in __cw_B (read.js skips them). Then run chain.js, screen.js and export.js again.
(() => {
  const B = JSON.parse(localStorage.__cw_B || "{}"), U = JSON.parse(localStorage.__cw_u || "{}");
  const have = new Set(JSON.parse(localStorage.__cw_have || "[]"));
  for (const h of Object.keys(U).concat(Object.keys(B))) have.add(h);
  const seeds = Object.entries(B).filter(([, x]) => x.pk && !x.err).map(([h, x]) => [h, x.pk]);
  localStorage.__cw_have = JSON.stringify([...have]); localStorage.__cw_seeds = JSON.stringify(seeds);
  for (const k of ["__cw_cd", "__cw_u", "__cw_L", "__cw_R", "__cw_out"]) localStorage.removeItem(k);
  return { seeds: seeds.length, known: have.size };
})()
