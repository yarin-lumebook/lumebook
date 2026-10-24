// Removes every localStorage key the weekly search wrote (run it before the first step and again at the end).
(() => { const k = Object.keys(localStorage).filter(k => k.startsWith("__cw_")); k.forEach(x => localStorage.removeItem(x)); return { removed: k.length } })()
