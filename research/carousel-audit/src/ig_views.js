// Reel views from Instagram's own profile grid, read only (15 Nov 2026).
// Run in the built-in browser on a tab that is already on https://www.instagram.com/lumebook.il/reels/ (signed in as Yarin).
// Scrolls the grid a few times so older reels load, then returns {ok, count, reels: {shortcode: "1,078"}}.
// Reads page text only: never clicks, follows, likes or opens anything. If the page shows a login or challenge, returns stop.
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  if (/accounts\/login|challenge|checkpoint/.test(location.href) || document.querySelector('input[name="password"]'))
    return { stop: "signed out or challenge page" };
  if (!/\/lumebook\.il\/reels\/?/.test(location.pathname)) return { stop: "not on /lumebook.il/reels/: " + location.pathname };
  const grab = () => {
    const out = {};
    for (const a of document.querySelectorAll('a[href*="/reel/"]')) {
      const code = (a.getAttribute("href").match(/\/reel\/([\w-]+)/) || [])[1];
      const txt = a.innerText.replace(/\s+/g, " ").trim();
      if (code && /^[\d.,]+\s*[KkMm]?$/.test(txt)) out[code] = txt;   // the view count printed on the tile; pinned/odd tiles are skipped
    }
    return out;
  };
  await sleep(2500);
  let seen = grab(), still = 0;
  for (let i = 0; i < 8 && still < 2; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await sleep(1800);
    const now = grab();
    still = Object.keys(now).length === Object.keys(seen).length ? still + 1 : 0;
    seen = { ...seen, ...now };
  }
  window.scrollTo(0, 0);
  return { ok: true, count: Object.keys(seen).length, reels: seen };
})()
