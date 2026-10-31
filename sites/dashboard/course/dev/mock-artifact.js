// Check the course platform's artifact-database path without publishing (see ../README.md).
// Paste this whole file into the browser console on any page of the project server (http://localhost:8780/tools/
// works), then: await H.open() · await H.open({ readOnly: true }) · H.db() · H.set(path, data) · H.w.LBCourse.
// It runs the built dashboard (sites/dashboard/site/lumebook-dashboard/, after build_site.py) in a full-window
// iframe whose window.claude offers a stand-in db and user: doc/collection paths, get/set/update (nested objects
// merge, as in the db type definitions)/delete, onSnapshot, acquire, 256 KiB per document and invalid_argument for
// refused writes. The data lives in localStorage "__mockdb" of the project server; remove that key when done.
// Faults: H.w.__failWrites = true (every write) or "course/tasks" (that document only); H.w.__failCode = "unavailable".
// Claude's check: H.open({ sample: "correct" | "above" | "partial" | "wrong" | "error" | "denied" }) gives a stand-in
// sample whose json() answers with that verdict after 300 ms (or rejects upstream_error / not_granted); without the
// option use("sample") resolves null, as where Claude cannot run. The prompts sent are in H.w.__samples.
// Copied from the retired work board's harness (31 Oct 2026), with update() made a recursive merge.
window.mockRuntime = function mockRuntime(opts) {
  const LIMIT = 256 * 1024;
  const load = () => JSON.parse(localStorage.getItem("__mockdb") || "{}");
  const save = (s) => localStorage.setItem("__mockdb", JSON.stringify(s));
  const docL = new Map(), colL = new Map();
  const clone = (x) => JSON.parse(JSON.stringify(x));
  const dsnap = (path) => { const s = load(), ex = Object.prototype.hasOwnProperty.call(s, path); return { id: path.split("/").pop(), exists: ex, data: () => (ex ? clone(s[path]) : undefined), metadata: { fromCache: false, hasPendingWrites: false } }; };
  const kids = (col) => Object.keys(load()).filter((p) => p.startsWith(col + "/") && p.slice(col.length + 1).indexOf("/") < 0).sort();
  const qsnap = (col) => { const docs = kids(col).map(dsnap); return { docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata: { fromCache: false, hasPendingWrites: false } }; };
  const fire = (path) => {
    for (const fn of docL.get(path) || []) setTimeout(() => fn(dsnap(path)), 0);
    const col = path.split("/").slice(0, -1).join("/");
    for (const fn of colL.get(col) || []) setTimeout(() => fn(qsnap(col)), 0);
  };
  window.__mockFire = fire;
  window.__writes = [];
  const fail = (path) => { const f = window.__failWrites; return f && (f === true || (typeof f === "string" && path.endsWith(f))); };
  let readFails = Number(opts.failPartReads) || 0; // opts.failPartReads: that many part reads fail with "unavailable"
  const doc = (path) => ({
    id: path.split("/").pop(), path,
    async get() { if (readFails > 0 && path.includes("/parts/")) { readFails--; throw { code: "unavailable", message: "mock read failure" }; } return dsnap(path); },
    async set(data) {
      window.__writes.push(path);
      if (fail(path)) throw { code: window.__failCode || "unavailable", message: "mock failure" };
      if (opts.readOnly) throw { code: "invalid_argument", message: "not allowed" };
      if (new TextEncoder().encode(JSON.stringify(data)).length > LIMIT) throw { code: "invalid_argument", message: "document over 256 KiB" };
      const s = load(); s[path] = clone(data); save(s); fire(path);
    },
    async update(data) {
      window.__writes.push(path);
      if (fail(path)) throw { code: window.__failCode || "unavailable", message: "mock failure" };
      if (opts.readOnly) throw { code: "invalid_argument", message: "not allowed" };
      const s = load(); if (!s[path]) throw { code: "invalid_argument", message: "missing" };
      const isObj = (x) => x && typeof x === "object" && !Array.isArray(x);
      const merge = (t, p) => { const o = { ...t }; for (const [k, v] of Object.entries(p)) o[k] = isObj(v) && isObj(o[k]) ? merge(o[k], v) : clone(v); return o; };
      s[path] = merge(s[path], clone(data)); save(s); fire(path);
    },
    async delete() { const s = load(); delete s[path]; save(s); fire(path); },
    async acquire({ holder, ttlMs }) {
      const s = load(), k = "__lease:" + path, l = s[k];
      if (l && l.until > Date.now() && l.holder !== holder) return { acquired: false, expiresAt: new Date(l.until).toISOString() };
      s[k] = { holder, until: Date.now() + Math.min(600000, Math.max(1000, ttlMs || 30000)) }; save(s);
      return { acquired: true, holder };
    },
    onSnapshot(next) { if (!docL.has(path)) docL.set(path, new Set()); docL.get(path).add(next); setTimeout(() => next(dsnap(path)), 0); return () => docL.get(path).delete(next); },
    collection(sub) { return col(path + "/" + sub); },
  });
  const col = (path) => ({
    path,
    doc(id) { return doc(path + "/" + (id || Math.random().toString(36).slice(2))); },
    where() { return this; }, orderBy() { return this; }, limit() { return this; },
    async get() { return qsnap(path); },
    onSnapshot(next) { if (!colL.has(path)) colL.set(path, new Set()); colL.get(path).add(next); setTimeout(() => next(qsnap(path)), 0); return () => colL.get(path).delete(next); },
    async add(data) { const d = this.doc(); await d.set(data); return d; },
  });
  const db = { doc, collection: col };
  const user = { can: async (n) => (n === "data.write" ? !opts.readOnly : true), isOwner: () => true, canEdit: () => true, id: async () => "u_test" };
  window.__samples = [];
  const sample = !opts.sample ? null : Object.assign(async () => ({ text: "", truncated: false }), {
    json: async (input) => {
      window.__samples.push(input);
      await new Promise((r) => setTimeout(r, 300));
      if (opts.sample === "error") throw { code: "upstream_error", message: "mock failure" };
      if (opts.sample === "denied") throw { code: "not_granted", message: "mock decline" };
      const ok = opts.sample === "correct" || opts.sample === "above";
      return { verdict: opts.sample, feedback: "Mock feedback from the stand-in grader.", missing: ok ? [] : ["a mock missing point"], redo: !ok };
    },
  });
  window.claude = { use: async (name) => (name === "db" ? db : name === "user" ? user : name === "sample" ? sample : null) };
};
window.H = {
  site: "/sites/dashboard/site/lumebook-dashboard/",
  async open(opts = {}) {
    const html = await (await fetch(this.site, { cache: "no-store" })).text();
    const m = html.match(/<script>window\.__DASH__=([\s\S]*?);<\/script>/);
    if (!localStorage.getItem("__mockdb")) { // the dashboard's own documents, as the morning task leaves them
      const DASH = JSON.parse(m[1]), s = { "snapshot/latest": DASH.snap, "tracker/state": DASH.tracker };
      for (const h of DASH.history) s["history/" + h.date] = h;
      localStorage.setItem("__mockdb", JSON.stringify(s));
    }
    const mock = `<script>(${window.mockRuntime.toString()})(${JSON.stringify(opts)});<\/script>`;
    const page = html.replace(m[0], "").replace("<head>", `<head><base href="${location.origin + this.site}">` + mock);
    document.getElementById("hf")?.remove();
    const f = document.createElement("iframe");
    f.id = "hf"; f.style.cssText = "position:fixed;inset:0;width:100vw;height:100vh;border:0;background:#fff;z-index:9";
    f.srcdoc = page;
    document.body.appendChild(f);
    await new Promise((r) => (f.onload = r));
    await new Promise((r) => setTimeout(r, 400));
    this.w = f.contentWindow;
    return "opened";
  },
  db() { return JSON.parse(localStorage.getItem("__mockdb") || "{}"); },
  set(path, data) { const s = this.db(); s[path] = data; localStorage.setItem("__mockdb", JSON.stringify(s)); this.w?.__mockFire?.(path); },
};
