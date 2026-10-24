// Copies a refresh result to the clipboard: localStorage.__rf_out (the profiles, collect.js) by default, or every
// __rc_p_<code> key as one object (the comments, comments.js) when the same call starts with window.__XK="__rc_p_";
// The page needs focus: be on https://www.instagram.com/robots.txt (nothing there to click) and run this in the same
// browser_batch right after a `computer` left_click on the page. Then in Bash: LC_ALL=en_US.UTF-8 pbpaste > <file>,
// and clear the clipboard with printf '' | pbcopy.
(() => {
  const K = window.__XK || "__rf_out"; let v;
  if (K.endsWith("_")) { const o = {}; Object.keys(localStorage).filter(k => k.startsWith(K)).forEach(k => { o[k.slice(K.length)] = JSON.parse(localStorage.getItem(k)) }); v = Object.keys(o).length ? JSON.stringify(o) : "" }
  else v = localStorage.getItem(K);
  window.__XK = "";
  if (!v) return { need: "nothing to export yet", key: K };
  const ta = document.createElement("textarea"); ta.value = v; document.body.appendChild(ta); ta.select();
  const ok = document.execCommand("copy"); ta.remove();
  return { ok, chars: v.length, key: K };
})()
