// Check: every suggested message names the kids at most once (Yarin, 22 Oct 2026), and no kid name is left in English.
// Runs the message code of the built map on every creator with names in kids.json.
//   node src/test_kids_names.mjs                 check the built map
//   node src/test_kids_names.mjs --show h1,h2    also print the messages of these creators
//   node src/test_kids_names.mjs --map other.html
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";

const here = path.dirname(new URL(import.meta.url).pathname);
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null };
const mapFile = arg("--map") || path.join(here, "..", "lumebook-creator-map.html");
const html = fs.readFileSync(mapFile, "utf8");
const lines = html.split("\n");

// one top-level statement: its first line, and the lines after it that are indented or close it
function stmt(rx, need = true) {
  const i = lines.findIndex((l) => rx.test(l));
  if (i < 0) { if (need) throw new Error("not found in map: " + rx); return "" }
  let j = i + 1;
  while (j < lines.length && /^(\s|\}|\])/.test(lines[j]) && !/^\s*$/.test(lines[j])) j++;
  return lines.slice(i, j).join("\n");
}
const decl = (name, need) => stmt(new RegExp("^(const|let|function) " + name + "\\b"), need);

// who() leaves {name} in place while checking: the greeting is the account name, not a mention of the kids
const src = [
  decl("C"), decl("KNOTE_HE"), decl("MONTH_EN", false), decl("srcL"),
  "const HOOK={ko:()=>null}; const SET={}; const get=()=>({}); const who=c=>(globalThis.SHOW?c.n||c.h:'{name}'); const lineOf=c=>c.l||''; const signer=()=>'ירין';",
  decl("knum"), decl("kidsOf"), decl("kidsForm"), decl("KB"), decl("KW"), decl("namesJoin"), decl("kidsG"), decl("kidsOnce", false), decl("kidsGeneric"),
  decl("HEROOT"), decl("addH"), decl("dropH"), decl("HEN"), decl("hebArt"),
  decl("BRAND"), decl("brand"), decl("HP"), decl("RX"), decl("heTidy"),
  decl("OFFERF"), decl("PRE"), decl("SPLIT"), decl("DEF"), decl("ANGLE"), decl("VIDEO_RX"), decl("derive"),
  stmt(/^Object\.keys\(DEF\)/), stmt(/^\["pro","par"\]\.forEach\(T=>\{ DEF\[PRE\[T\]\+"of"\]/),
  decl("MOMDUP"), decl("momDedupe"), decl("fill"), decl("OFFER"),
  "globalThis.T={C,DEF,OFFER,fill,kidsG,kidsOf,namesJoin,kidsOnce:typeof kidsOnce==='function'?kidsOnce:null};",
].join("\n");
const ctx = {}; vm.createContext(ctx); vm.runInContext(src, ctx);
const { C, DEF, OFFER, fill, kidsG, kidsOf } = ctx.T;

// the messages one creator can be shown: every template on every track and style, the email as one text, and the gifted offer
const KEYS = Object.keys(DEF).filter((k) => !/(^|_)(es|eb)(_b)?$/.test(k));
function messages(c) {
  const out = {};
  KEYS.forEach((k) => { out[k] = fill(DEF[k], c) });
  ["", "pro_", "par_"].forEach((p) => ["", "_b"].forEach((s) => {
    if (DEF[p + "es" + s] !== undefined) out[p + "em" + s] = fill(DEF[p + "es" + s] + "\n\n" + DEF[p + "eb" + s], c);
  }));
  out.of_own = kidsG(OFFER, c);
  return out;
}
// a mention: the names as a word, alone or after a prefix letter (לאלי, ואלי), never inside another word (אליכם)
const count = (s, w) => (s.match(new RegExp("(?<![\\u05D0-\\u05EA])[ובלכמש]?" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(?![\\u05D0-\\u05EA])", "g")) || []).length;

let bad = 0, checked = 0;
const show = new Set((arg("--show") || "").split(",").filter(Boolean));
for (const c of C) {
  const names = kidsOf(c).names;
  if (!names.length) continue;
  checked++;
  if (names.some((n) => /[A-Za-z]/.test(n))) { bad++; console.log("English name: @" + c.h + " " + names.join(", ")) }
  const N = ctx.T.namesJoin(names);
  for (const [k, s] of Object.entries(messages(c))) {
    const n = count(s, N);
    if (n > 1) { bad++; if (bad < 15) console.log("@" + c.h + " " + k + ": named " + n + " times") }
  }
  if (show.has(c.h)) { ctx.SHOW = true; const m = messages(c); ctx.SHOW = false; console.log("\n=== @" + c.h + " (" + N + ")\n--- dm\n" + m.dm + "\n--- d2\n" + m.d2 + "\n--- of\n" + m.of_own.split("\n").filter((l) => l.includes(N) || /הילד|לילד/.test(l)).join("\n")) }
}
// kidsOnce on a hand-written text
if (ctx.T.kidsOnce) {
  const c = C.find((x) => kidsOf(x).names.length > 1);
  const N = ctx.T.namesJoin(kidsOf(c).names);
  const s = "ספר במתנה ל" + N + ". סרטון של " + N + " עם הספר, ו" + N + " יאהבו.";
  const r = ctx.T.kidsOnce(s, c);
  if (count(r, N) !== 1) { bad++; console.log("kidsOnce kept " + count(r, N) + " mentions: " + r) }
}
console.log((bad ? "FAIL" : "OK") + ": " + checked + " creators with names, " + bad + " problems");
process.exit(bad ? 1 : 0);
