// Copies localStorage.__cw_out (written by screen.js or read.js when they finish) to the clipboard.
// The page needs focus: run this in the same browser_batch right after a real `computer` left_click on an empty part of the page.
// Then in Bash: LC_ALL=en_US.UTF-8 pbpaste > <file>, and clear the clipboard with printf '' | pbcopy.
(() => {
  const v = localStorage.__cw_out; if (!v) return { need: "nothing to export yet" };
  const ta = document.createElement("textarea"); ta.value = v; document.body.appendChild(ta); ta.select();
  const ok = document.execCommand("copy"); ta.remove();
  return { ok, chars: v.length };
})()
