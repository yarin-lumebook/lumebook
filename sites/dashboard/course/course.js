/* LumeBook course platform: the dashboard's default view (#course) since 31 Oct 2026, in place of the canvas work board.
   English and left to right inside the Hebrew dashboard (Yarin, 31 Oct 2026: "i need it to be like a course and a way
   for you to check my answers, i want the course fully in english").
   Opens on the Course tab: the lessons in order by track, each on its own page, a Continue button and the projects.
   Every lesson ends in a 3-question quiz sealed until submitted (peeking is allowed and recorded): the two set answers
   are checked against the key, and Claude grades the written third answer against the lesson's model answer (the
   sample capability). Projects are handed in and Claude checks them against what a good one contains. Where Claude
   cannot run (the Vercel copy, the local server, or the viewer said no), Yarin grades the written answer themself.
   Also: tasks with checklists that fade on a published schedule, the Sales tab (Yossi's order export in, the paid
   orders that carry Yarin's tag out, since 1 Nov 2026), the weekly numbers (Sundays), the link maker with its log, and
   the glossary. Plan: course/curriculum.md. Content: window.LB_COURSE (course/course-data.js, built by course/build.py).

   Where it saves (shown in the view, never implied):
   - claude.ai artifact with the db capability: documents course/tasks, course/progress, course/numbers,
     course/settings, course/links, course/sales. Items live in nested maps keyed by id and are written with update(), which merges
     nested objects, so the Mac and the phone can edit different items without overwriting each other. A removed task
     is {deleted: true}, never a missing key. One write at a time per document. Never touches boards/, snapshot,
     history or tracker. Quiz answers, Claude's grades and project hand-ins are all in course/progress, so Claude Code
     can read them back with ArtifactData.
   - anywhere else (the Vercel copy, the local project server, a file): this browser's localStorage, "lb-course:v1".
   No framework. */
(() => {
  "use strict";
  const ROOT = document.getElementById("course-root");
  if (!ROOT) return;
  const C = window.LB_COURSE;
  if (!C) return; // the dashboard's fallback says the files were not published
  window.LBCourseLoaded = true;
  ROOT.dir = "ltr"; ROOT.lang = "en";

  const KEY = "lb-course:v1";
  const DOCS = ["tasks", "progress", "numbers", "settings", "links", "sales"];
  const EMPTY = { tasks: { items: {} }, progress: { lessons: {}, projects: {} }, numbers: { weeks: {} }, settings: { tags: {} }, links: { items: {} }, sales: { orders: {}, days: {}, imports: {} } };
  const TYPES = Object.fromEntries(C.types.map((t) => [t.id, t]));
  const LESSONS = Object.fromEntries(C.lessons.map((l) => [l.id, l]));
  const PROJECTS = Object.fromEntries(C.projects.map((p) => [p.id, p]));
  const SOURCES = [["instagram", "Instagram"], ["facebook", "Facebook"], ["whatsapp", "WhatsApp"]];
  const PLACES = [["dm", "DM"], ["story", "Story"], ["post", "Post"], ["bio", "Bio"]];
  const TEMPLATES = [
    ["carousel", "Today's carousel"], ["dm", "Answer comment words"], ["numbers", "Sunday numbers"],
    ["yossi", "An ask for Yossi"], ["moment", "Live moment"], ["reel", "Reel"], ["creator", "Creator follow-up"],
  ];
  const TABS = [["course", "Course"], ["tasks", "Tasks"], ["sales", "Sales"], ["numbers", "Numbers"], ["links", "Links"], ["terms", "Glossary"]];
  const HELP = { full: "full help", partial: "partial help", light: "light help", none: "no help" };
  const VERDICTS = { // the curriculum's grading scale (§10); a partial counts half toward the 2 of 3 pass
    correct: { sym: "✓", label: "Correct", score: 1, cls: "success" },
    above: { sym: "↑", label: "Above the standard", score: 1, cls: "success" },
    partial: { sym: "~", label: "Partial", score: 0.5, cls: "warning" },
    wrong: { sym: "✗", label: "Wrong", score: 0, cls: "danger" },
  };

  // ---------- helpers ----------
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const clone = (x) => JSON.parse(JSON.stringify(x ?? null));
  const isObj = (x) => x && typeof x === "object" && !Array.isArray(x);
  function merge(target, patch) { // the db's update() semantics: nested objects merge, anything else replaces
    const out = isObj(target) ? { ...target } : {};
    for (const [k, v] of Object.entries(patch)) out[k] = isObj(v) && isObj(out[k]) ? merge(out[k], v) : clone(v);
    return out;
  }
  const uid = (p) => { const r = new Uint32Array(1); crypto.getRandomValues(r); return p + Date.now().toString(36) + r[0].toString(36).slice(0, 4); };
  const nowIso = () => new Date().toISOString();
  const day0 = (d = new Date()) => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x; };
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const parseDay = (s) => { const [y, m, d] = String(s).slice(0, 10).split("-").map(Number); return new Date(y, m - 1, d); };
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const dmy = (d) => `${d.getDate()} ${MON[d.getMonth()]}`; // dates as 2 Nov
  const weekStart = (d) => { const x = day0(d); x.setDate(x.getDate() - x.getDay()); return x; }; // Israeli week, Sunday first
  const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
  const num = (v) => (v === "" || v == null || !Number.isFinite(Number(v)) ? null : Math.max(0, Math.round(Number(v))));
  const fmt = (n) => (n == null ? "-" : Number(n).toLocaleString("en-US"));
  const half = (n) => (Number.isInteger(n) ? String(n) : n.toFixed(1));
  const ltr = (s) => `<bdi dir="ltr">${esc(s)}</bdi>`;
  const plain = (html) => { const d = document.createElement("div"); d.innerHTML = html || ""; return d.textContent.replace(/\s+/g, " ").trim(); };
  const count = (o) => Object.keys(o || {}).length;

  // ---------- state ----------
  const D = clone(EMPTY);
  const ST = {
    mode: "local", loaded: false, slow: false, readOnly: false, saveErr: null,
    tab: "course", lesson: null, project: null, // lesson: {id, from: taskId|null}; project: id
    newType: "", lm: { dest: "", url: "", source: "instagram", place: "dm", date: iso(new Date()), campaign: "", term: "" },
    numWeek: null, drawer: null, // drawer: {kind: "task", id}
    salesPeriod: "month", imp: null, // imp: the export being pasted, before it is added (see salesTab)
    quiz: {}, // in-memory answers before submitting, by lesson id
    hand: {}, // in-memory project hand-in drafts, by project id
    claude: "pending", claudeOff: "", grading: {}, gradeErr: {}, // Claude's check: pending | on | off
    dirty: false, toTop: false,
  };
  try {
    const t = localStorage.getItem(KEY + ":tab"); if (TABS.some(([id]) => id === t)) ST.tab = t;
    const l = localStorage.getItem(KEY + ":lesson"); if (l && LESSONS[l]?.ready) ST.lesson = { id: l, from: null };
  } catch {}

  // ---------- storage ----------
  let db = null, sample = null;
  const exists = {}, pending = {}, writing = {}, retries = {};
  function localSave() { try { localStorage.setItem(KEY, JSON.stringify(D)); } catch {} }
  function localLoad() {
    try { const s = JSON.parse(localStorage.getItem(KEY) || "null"); if (s) for (const k of DOCS) if (isObj(s[k])) D[k] = merge(EMPTY[k], s[k]); } catch {}
  }
  function patch(doc, p) {
    if (ST.readOnly) { toast("You can't edit this page"); return; }
    D[doc] = merge(D[doc], p);
    if (ST.mode === "local") { localSave(); render(); return; }
    pending[doc] = merge(pending[doc] || {}, p);
    render();
    flush(doc);
  }
  async function flush(doc) {
    if (writing[doc] || !pending[doc]) return;
    const p = pending[doc]; delete pending[doc];
    writing[doc] = true;
    const ref = db.doc("course/" + doc);
    try {
      if (!exists[doc]) {
        const snap = await ref.get();
        if (snap.exists) { exists[doc] = true; await ref.update(p); }
        else { await ref.set(merge(merge(EMPTY[doc], snap.data() || {}), p)); exists[doc] = true; }
      } else await ref.update(p);
      retries[doc] = 0;
      if (ST.saveErr) { ST.saveErr = null; render(); }
    } catch (e) {
      const code = e && e.code;
      if (code === "invalid_argument") { // a well-formed write refused: this viewer cannot write here
        ST.readOnly = true; ST.saveErr = null; render(); toast("This page is read only. The change was not saved");
      } else {
        pending[doc] = merge(p, pending[doc] || {});
        retries[doc] = (retries[doc] || 0) + 1;
        ST.saveErr = code === "quota_exceeded" ? "The database is full" : "Saving failed, trying again";
        render();
        if (code !== "quota_exceeded" && code !== "revoked" && retries[doc] < 6) setTimeout(() => flush(doc), 1500 * retries[doc] + Math.random() * 800);
      }
    } finally {
      writing[doc] = false;
      if (pending[doc] && !retries[doc]) flush(doc);
    }
  }
  async function boot() {
    if (window.__DASH__ || !window.claude?.use) { ST.mode = "local"; ST.claude = "off"; localLoad(); ST.loaded = true; render(); return; }
    window.claude.use("sample").then((s) => { sample = s || null; ST.claude = s ? "on" : "off"; render(); }, () => { ST.claude = "off"; render(); });
    const [d, user] = await Promise.all([window.claude.use("db").catch(() => null), window.claude.use("user").catch(() => null)]);
    if (!d) { ST.mode = "local"; localLoad(); ST.loaded = true; render(); return; }
    db = d; ST.mode = "db";
    if (user) { try { if ((await user.can("data.write")) === false) ST.readOnly = true; } catch {} }
    const seen = new Set();
    const timer = setTimeout(() => { if (!ST.loaded) { ST.slow = true; render(); } }, 10000);
    for (const name of DOCS) {
      db.doc("course/" + name).onSnapshot((snap) => {
        exists[name] = snap.exists;
        D[name] = merge(merge(EMPTY[name], snap.exists ? snap.data() : {}), pending[name] || {});
        if (!snap.metadata?.fromCache) seen.add(name);
        if (seen.size === DOCS.length && !ST.loaded) { ST.loaded = true; ST.slow = false; clearTimeout(timer); }
        render();
      }, () => { seen.add(name); if (seen.size === DOCS.length) { ST.loaded = true; clearTimeout(timer); } render(); });
    }
    render();
  }

  // ---------- derived ----------
  const tasks = () => Object.values(D.tasks.items || {}).filter((t) => t && t.id && !t.deleted);
  const doneOfType = (type, exceptId) => tasks().filter((t) => t.type === type && t.done && t.id !== exceptId).length;
  function fadeFor(type, exceptId) {
    const n = doneOfType(type, exceptId);
    return C.fade.find((f) => f.upto == null || n < f.upto) || C.fade[C.fade.length - 1];
  }
  const LP = (id) => (D.progress.lessons || {})[id] || {};
  const PP = (id) => (D.progress.projects || {})[id] || {};
  const lastTry = (p) => { const n = count(p.tries); return n ? { n, t: p.tries[n] } : null; };
  const rightOf = (l, t) => l.quiz.filter((q) => q.kind === "choice" && Number((t.answers || {})[q.n]) === q.options.findIndex((o) => o.correct)).length;
  const openOf = (t) => (t.open != null ? t.open : t.self != null ? t.self : null); // older tries stored only self
  function lessonState(l) {
    if (!l.ready) return { s: "soon" };
    const p = LP(l.id);
    if (p.passed) return { s: "passed", score: p.score };
    const missing = l.pre.filter((id) => !LP(id).passed);
    if (missing.length) return { s: "locked", missing };
    const last = lastTry(p);
    if (last) return last.t.score == null ? { s: "grading" } : { s: "retry", score: last.t.score };
    return { s: p.opened_at ? "started" : "open" };
  }
  const ACTIVE = ["open", "started", "grading", "retry"];
  const isOpenable = (l) => ACTIVE.includes(lessonState(l).s) || lessonState(l).s === "passed";
  const nextLesson = (type) => C.lessons.find((l) => (!type || l.type === type) && ACTIVE.includes(lessonState(l).s)) || null;
  function courseWeek(d = new Date()) {
    const t = iso(d);
    for (const [k, w] of Object.entries(C.weeks)) if (t >= w.from && t <= w.to) return k;
    return t < C.weeks.W1.from ? "before" : "after";
  }
  const weekNo = (k) => Number(String(k).slice(1));
  const stateChip = (st) => ({
    passed: `<span class="lb-chip success">Passed${st.score != null ? ` · ${half(st.score)}/3` : ""}</span>`,
    open: `<span class="lb-chip tint">Start</span>`,
    started: `<span class="lb-chip tint">In progress</span>`,
    grading: `<span class="lb-chip warning">Needs a grade</span>`,
    retry: `<span class="lb-chip warning">Redo${st.score != null ? ` · ${half(st.score)}/3` : ""}</span>`,
    soon: `<span class="lb-chip outline">Coming soon</span>`,
    locked: `<span class="lb-chip outline">After ${st.missing ? st.missing.join(", ") : ""}</span>`,
  }[st.s]);
  const verdictChip = (v) => { const x = VERDICTS[v]; return x ? `<span class="lb-chip ${x.cls}">${x.sym} ${x.label}</span>` : ""; };

  // ---------- Claude's check (the sample capability) ----------
  const CONTEXT = "You are grading work in a short course written for Yarin, who runs marketing for LumeBook (personalised children's books sold online in Israel: Instagram carousels, DMs with tagged links, a 25% share of orders that carry Yarin's UTM tag). Yarin asked to be graded honestly: when work falls short, say so plainly and say what to redo.";
  const STYLE = "Ignore spelling and grammar; the answer may be in English or Hebrew. Write the feedback in English, to Yarin as \"you\", in plain words, with no em dashes.";
  function lessonPrompt(l, q, answer) {
    return [
      CONTEXT, "",
      `LESSON ${l.id}: ${l.title}`, "What the lesson teaches:", plain(l.teach_html).slice(0, 6000), "",
      `QUESTION: ${q.q}`, "MODEL ANSWER (the points a correct answer must contain):", plain(q.explain_html), "",
      "YARIN'S ANSWER:", String(answer || "").slice(0, 4000), "",
      "Grade on meaning, not wording. correct: it contains every essential point of the model answer, in any words. above: correct, and it adds a sound point the model answer lacks. partial: some of the essential points, but one is missing, blurred or slightly wrong. wrong: it misses the point or contradicts the lesson. Do not reward length. " + STYLE, "",
      'Reply with only this JSON: {"verdict": "correct" | "above" | "partial" | "wrong", "feedback": "two or three sentences: what you got right, and what is missing or wrong", "missing": ["each essential point the answer missed, a few words each"]}',
    ].join("\n");
  }
  function attachedData(p) {
    if (p.attach === "links") {
      const since = addDays(day0(), -7);
      const rows = Object.values(D.links.items || {}).filter((x) => x && !x.deleted && x.created_at && new Date(x.created_at) >= since)
        .map((x) => `${x.created_at.slice(0, 10)} · ${x.url} · DMs sent: ${Number(x.sent) || 0}`);
      return `Tag values: utm_medium=${tags().medium}${(D.settings.tags || {}).chosen_at ? " (chosen by Yarin)" : " (the default, not yet chosen by Yarin)"}\nLink log, last 7 days (${rows.length} links):\n${rows.join("\n") || "(empty)"}`;
    }
    if (p.attach === "numbers") {
      const ws = Object.entries(D.numbers.weeks || {}).filter(([, w]) => w && w.saved_at).sort().slice(-2);
      return ws.length ? ws.map(([k, w]) => `Week from ${k}: tagged clicks ${w.clicks_na ? "not available yet" : fmt(w.clicks)}; DMs with a tagged link ${fmt(w.dms)}; comment words ${fmt(w.words)}; tagged orders ${w.orders_na ? "not available yet" : fmt(w.orders)}; best post saves ${fmt(w.saves)}, shares ${fmt(w.shares)}, reach ${fmt(w.reach)}; can't prove: "${w.cannot || ""}"`).join("\n") : "(no saved weeks on the Numbers tab)";
    }
    return "";
  }
  function projectPrompt(p, text, attached) {
    return [
      CONTEXT, "",
      `PROJECT ${p.id} (week ${weekNo(p.week)}, ${HELP[p.help]}): ${p.text}`, "WHAT A GOOD HAND-IN CONTAINS:", p.check, "",
      attached ? "DATA THE PLATFORM ATTACHED (Yarin's own saved records):\n" + attached + "\n" : "",
      "YARIN'S HAND-IN:", String(text || "").slice(0, 8000), "",
      "Check four things in order: is it correct; is the reasoning sound; would it pass professionally (could the person it is for act on it); what any error reveals. correct: it meets every point above. above: it meets them and goes beyond. partial: it meets some but misses one that matters. wrong: it misses the project's point. " + STYLE, "",
      'Reply with only this JSON: {"verdict": "correct" | "above" | "partial" | "wrong", "feedback": "three to five sentences, ending with a straight verdict", "missing": ["each point still missing, a few words each"], "redo": true | false}',
    ].join("\n");
  }
  async function askClaude(key, prompt, fresh) {
    if (!sample || ST.grading[key]) return null;
    const ctl = new AbortController();
    ST.grading[key] = ctl; delete ST.gradeErr[key]; render();
    try {
      const r = await sample.json(prompt, fresh ? { signal: ctl.signal, cache: false } : { signal: ctl.signal });
      const v = String(r?.verdict || "").toLowerCase();
      if (!VERDICTS[v]) throw { code: "invalid_json" };
      const out = { verdict: v, feedback: String(r.feedback || "").slice(0, 1500), missing: Array.isArray(r.missing) ? r.missing.map(String).filter(Boolean).slice(0, 6) : [], at: nowIso() };
      if (typeof r.redo === "boolean") out.redo = r.redo;
      return out;
    } catch (e) {
      const c = e && e.code;
      if (["not_granted", "sampling_disabled", "not_declared", "capability_disabled", "capability_removed"].includes(c)) {
        ST.claude = "off";
        ST.claudeOff = c === "not_granted" ? "This page was not allowed to use Claude, so grade it yourself." : "Claude is not available in this view, so grade it yourself.";
      } else if (c !== "cancelled") {
        ST.gradeErr[key] = ({ rate_limited: "Claude is busy, or your usage limit was reached. Try again in a while.", session_expired: "Sign in to Claude again, then try again.", invalid_json: "Claude's answer came back unreadable. Try again.", refused: "Claude would not grade this. Rewrite it and try again.", empty_completion: "Claude returned nothing. Try again." })[c] || "The check did not go through. Try again.";
      }
      return null;
    } finally { delete ST.grading[key]; render(); }
  }

  // ---------- render ----------
  function render() {
    const ae = document.activeElement;
    if (ae && (ROOT.contains(ae) || drawerEl?.contains(ae)) && /^(INPUT|TEXTAREA|SELECT)$/.test(ae.tagName) && ae.type !== "checkbox" && ae.type !== "radio" && !ae.readOnly) {
      ST.dirty = true; return; // never redraw under someone typing; focusout redraws
    }
    ST.dirty = false;
    const y = ST.toTop ? 0 : window.scrollY;
    ST.toTop = false;
    ROOT.innerHTML = `<div class="lb-page cx">${head()}${body()}</div>`;
    window.scrollTo(0, y);
    renderDrawer();
  }
  function head() {
    const w = courseWeek(), today = new Date();
    const examDays = Math.round((parseDay(C.exam.from) - day0(today)) / 864e5);
    const wk = w === "before" ? `The course starts on ${dmy(parseDay(C.weeks.W1.from))}` : w === "after" ? "November is over: the report and the exam are behind you" : `Week ${weekNo(w)} of 4 · ${C.weeks[w].name}`;
    const where = ST.readOnly ? `<span class="lb-chip warning"><span class="lb-dot"></span>Read only</span>`
      : ST.mode === "db" ? `<span class="lb-chip success" title="Tasks and progress are saved in the page on Claude and sync between the Mac and the iPhone"><span class="lb-dot"></span>Saved in Claude</span>`
      : `<span class="lb-chip outline" title="Changes are saved only in this browser. On the page in Claude they sync between devices">Saved on this device only</span>`;
    const banners = [];
    if (ST.mode === "db" && !ST.loaded) banners.push(ST.slow ? `<span class="lb-chip warning">The data hasn't arrived yet. What you see may be out of date</span>` : `<span class="lb-chip"><span class="lb-dot"></span>Loading…</span>`);
    if (ST.saveErr) banners.push(`<span class="lb-chip danger">${esc(ST.saveErr)}</span>`);
    return `<div class="cx-head">
      <div class="lb-row"><div class="cx-week"><b>${esc(wk)}</b><span>${examDays > 0 ? `${examDays} days to the exam (${dmy(parseDay(C.exam.from))} to ${dmy(parseDay(C.exam.to))})` : examDays > -3 ? "Exam week" : ""}</span></div>
      <div class="cx-banner">${where}${banners.join("")}</div></div>
      <nav class="lb-tabs cx-tabs" role="tablist">${TABS.map(([id, name]) => `<button type="button" role="tab" data-tab="${id}" aria-selected="${ST.tab === id}">${name}</button>`).join("")}</nav>
    </div>`;
  }
  function body() {
    if (ST.tab === "course") return ST.lesson && LESSONS[ST.lesson.id]?.ready ? lessonPage(ST.lesson.id, ST.lesson.from) : ST.project && PROJECTS[ST.project] ? projectPage(ST.project) : courseTab();
    return ({ tasks: tasksTab, sales: salesTab, numbers: numbersTab, links: linksTab, terms: termsTab }[ST.tab] || courseTab)();
  }

  // ---------- course tab ----------
  function courseTab() {
    const ready = C.lessons.filter((l) => l.ready), passed = C.lessons.filter((l) => LP(l.id).passed);
    const next = nextLesson();
    const pct = Math.round((passed.length / C.lessons.length) * 100);
    const nst = next && lessonState(next);
    const cont = next
      ? `<div class="cx-next"><span class="lb-note">${nst.s === "open" ? "Start here" : nst.s === "retry" ? "Redo" : nst.s === "grading" ? "Needs a grade" : "Continue"} · week ${weekNo(next.week)} · ${next.min} min</span>
          <b>${esc(next.id)} · ${esc(next.title)}</b>
          <div><button type="button" class="lb-btn" data-lesson="${esc(next.id)}">${nst.s === "open" ? "Start the lesson" : "Continue"}</button></div></div>`
      : `<div class="cx-next"><b>${ready.length && passed.length >= ready.length ? "Every written lesson is passed." : "No lesson is open right now."}</b><span class="lb-note">${ready.length < C.lessons.length ? `Lessons ${C.lessons.find((l) => !l.ready).id} on are still being written; they appear here when they are ready.` : ""}</span></div>`;
    const grader = ST.claude === "on" ? "Claude checks your written answers and your projects here."
      : ST.claude === "pending" ? "Connecting to Claude…"
      : ST.mode === "db" ? (ST.claudeOff || "Claude's check is not available in this view, so you grade your written answers yourself.")
      : "Claude's check runs in the course page in Claude. Here you grade your written answers yourself.";
    const tracks = Object.keys(C.weeks).map((k) => ({ k, w: C.weeks[k], ls: C.lessons.filter((l) => l.week === k) }));
    const capRows = [1, 2, 3, 4].map((c) => { const ls = C.lessons.filter((l) => l.cap.includes(c)), p = ls.filter((l) => LP(l.id).passed).length;
      return `<div class="cx-cap"><span>${esc(C.caps[c])}</span><span class="lb-note">${p} of ${ls.length}</span><div class="lb-bar is-tint"><i style="width:${ls.length ? Math.round(p / ls.length * 100) : 0}%"></i></div></div>`; }).join("");
    return `
    <section class="lb-card cx-hero">
      <div class="cx-hero-top"><div><span class="lb-note">Your course · ${dmy(parseDay(C.weeks.W1.from))} to ${dmy(parseDay(C.weeks.W4.to))}</span><h2>The LumeBook marketing pipeline</h2></div>
        <div class="cx-score-big"><b>${passed.length}</b><span>of ${C.lessons.length} lessons passed</span></div></div>
      <div class="lb-bar is-tint" aria-label="${pct}% of lessons passed"><i style="width:${pct}%"></i></div>
      ${cont}
      <p class="lb-note">${esc(grader)}</p>
    </section>
    <details class="lb-disclosure"><summary><span class="lb-sum">How the course works<small>lessons, quizzes, Claude's check, projects, the exam</small></span></summary><div class="lb-disclosure-body lb-prose cx-how">
      <ul>
        <li>Each lesson takes about 5 minutes to read. It ends with 3 questions you answer from memory.</li>
        <li>Questions 1 and 2 are checked against the answer key. Claude checks your written answer to question 3 against the lesson's model answer: ✓ correct, ~ partial, ✗ wrong, ↑ above the standard.</li>
        <li>You pass at 2 of 3 (a partial counts half). Under that the lesson says redo, and the lessons that build on it stay locked until you pass it.</li>
        <li>Projects are real LumeBook work. Hand each one in and Claude checks it against what a good one contains.</li>
        <li>The final exam is ${dmy(parseDay(C.exam.from))} to ${dmy(parseDay(C.exam.to))}. Every answer you give is saved, so Claude Code can also go through them with you.</li>
      </ul></div></details>
    ${tracks.map(({ k, w, ls }) => `<section class="lb-section">
      <div class="lb-section-head"><h2>Week ${weekNo(k)} · ${esc(w.name)}</h2><span class="lb-meta">${dmy(parseDay(w.from))} to ${dmy(parseDay(w.to))} · ${ls.filter((l) => LP(l.id).passed).length} of ${ls.length} passed</span></div>
      <div class="lb-group">${ls.map((l) => { const st = lessonState(l); const can = isOpenable(l);
        return `<div class="cx-map-row ${st.s === "soon" ? "is-soon" : ""} ${next && next.id === l.id ? "is-next" : ""}"><span class="cx-id">${esc(l.id)}</span>
          ${can ? `<button type="button" class="cx-open" data-lesson="${esc(l.id)}"><span class="cx-name">${esc(l.title)}</span><span class="cx-sub">${esc(TYPES[l.type].name)} · ${l.min} min</span></button>`
                : `<div><span class="cx-name">${esc(l.title)}</span><div class="cx-sub">${esc(TYPES[l.type].name)} · ${l.min} min</div></div>`}
          ${stateChip(st)}</div>`; }).join("")}</div>
      ${projectRows(C.projects.filter((p) => p.week === k))}
    </section>`).join("")}
    <section class="lb-card"><div class="lb-card-head"><b>The four capabilities</b><span class="lb-note">every lesson serves at least one</span></div><div class="cx-caps">${capRows}</div></section>`;
  }
  function projectRows(ps) {
    if (!ps.length) return "";
    return `<div class="lb-group cx-projects">${ps.map((p) => { const pp = PP(p.id), last = lastCheck(pp);
      return `<div class="cx-map-row"><span class="cx-id">${esc(p.id)}</span>
        <button type="button" class="cx-open" data-project="${esc(p.id)}"><span class="cx-name">${esc(p.text)}</span><span class="cx-sub">Project · ${HELP[p.help]}</span></button>
        ${pp.done_at ? `<span class="lb-chip success">Done</span>` : last && last.verdict ? verdictChip(last.verdict) : last ? `<span class="lb-chip warning">Handed in</span>` : `<span class="lb-chip outline">To do</span>`}</div>`; }).join("")}</div>`;
  }

  // ---------- lesson page ----------
  function lessonPage(id, from) {
    const l = LESSONS[id];
    const idx = C.lessons.indexOf(l), prev = C.lessons[idx - 1], next = C.lessons[idx + 1];
    const caps = l.cap.map((c) => C.caps[c]).join(", ");
    const nextOk = next && next.ready && isOpenable(next);
    return `<div class="cx-crumbs"><button type="button" class="lb-btn ghost sm" data-home>← Course</button>${from && D.tasks.items[from] && !D.tasks.items[from].deleted ? `<button type="button" class="lb-btn ghost sm" data-task="${esc(from)}">Back to the task</button>` : ""}</div>
    <article class="cx-lesson">
      <header class="cx-lhead"><p class="lb-note">Week ${weekNo(l.week)} · Lesson ${idx + 1} of ${C.lessons.length} · ${esc(TYPES[l.type].name)} · ${l.min} min · ${esc(caps)}</p>
        <h2>${esc(l.id)} · ${esc(l.title)}</h2>${stateChip(lessonState(l))}</header>
      <div class="lb-callout"><b>Do this now</b><span>${l.now_html}</span></div>
      <div class="cx-part"><h3>The lesson</h3><div class="lb-prose">${l.teach_html}</div></div>
      <div class="cx-part"><h3>Example</h3><div class="lb-prose">${l.example_html}</div></div>
      <div class="cx-part"><h3>Common mistake</h3><div class="lb-prose">${l.mistake_html}</div></div>
      <div class="lb-card is-quiet cx-cannot"><div class="cx-part"><h3>What the numbers can't prove</h3><div class="lb-prose">${l.cannot_html}</div></div></div>
      ${l.terms.length ? `<div class="cx-part"><h3>Terms</h3><dl class="cx-terms">${l.terms.map((t) => `<dt>${esc(t.term)}</dt><dd>${t.def_html}</dd>`).join("")}</dl></div>` : ""}
      ${quizBlock(l)}
      <nav class="cx-pager">
        ${prev ? `<button type="button" class="lb-btn secondary sm" data-lesson="${esc(prev.id)}" ${isOpenable(prev) ? "" : "disabled"}>← ${esc(prev.id)}</button>` : "<span></span>"}
        ${next ? `<button type="button" class="lb-btn ${LP(id).passed && nextOk ? "" : "secondary"} sm" data-lesson="${esc(next.id)}" ${nextOk ? "" : "disabled"} title="${nextOk ? "" : next.ready ? `Opens after ${lessonState(next).missing?.join(", ") || ""}` : "Coming soon"}">${esc(next.id)} →</button>` : "<span></span>"}
      </nav>
    </article>`;
  }
  function quizBlock(l) {
    const id = l.id, p = LP(id), last = lastTry(p);
    const fresh = ST.quiz[id]?.fresh;
    const committed = last && last.t.committed_at && !fresh ? last.t : null;
    const draft = ST.quiz[id] || (ST.quiz[id] = { answers: {}, peek: false });
    const showKey = !!committed || draft.peek;
    const key = committed ? `${id}#${last.n}` : "";
    const qs = l.quiz.map((q) => {
      const ans = committed ? (committed.answers || {})[q.n] : draft.answers[q.n];
      if (q.kind === "open") {
        return `<div class="cx-q"><p>${q.n}. ${q.q_html}</p>
          <textarea class="lb-textarea" data-open="${id}" data-q="${q.n}" ${committed ? "disabled" : ""} placeholder="In your own words">${esc(ans || "")}</textarea>
          ${committed ? gradePanel(l, committed, key) : ""}
          ${showKey ? `<div class="cx-explain"><b>Model answer:</b> ${q.explain_html}</div>` : ""}
        </div>`;
      }
      return `<div class="cx-q"><p>${q.n}. ${q.recall ? `<span class="lb-chip outline">Recall ${esc(q.recall)}</span> ` : ""}${q.q_html}</p>
        ${q.options.map((o, i) => {
          const cls = showKey ? (o.correct ? "is-right" : committed && Number(ans) === i ? "is-wrong" : "") : "";
          return `<label class="cx-opt ${cls}"><input type="radio" name="q-${id}-${q.n}" data-choice="${id}" data-q="${q.n}" value="${i}" ${ans !== undefined && ans !== null && Number(ans) === i ? "checked" : ""} ${committed ? "disabled" : ""}><span>${o.html}</span></label>`;
        }).join("")}
        ${showKey ? `<div class="cx-explain">${q.explain_html}</div>` : ""}
      </div>`;
    }).join("");
    const answered = l.quiz.every((q) => { const a = draft.answers[q.n]; return q.kind === "open" ? String(a || "").trim().length > 0 : a !== undefined && a !== null; });
    let result = "";
    if (committed) {
      const right = rightOf(l, committed), score = committed.score;
      result = score == null
        ? `<div class="lb-callout"><b>${right} of 2 set answers right</b><span>Question 3 still needs a grade.</span></div>`
        : `<div class="lb-callout ${score >= 2 ? "info" : ""} cx-score"><b>${half(score)} of 3${committed.peeked ? " · with a peek" : ""} · ${score >= 2 ? "Passed" : "Redo"}</b>
            <span>${score >= 2 ? `Lesson passed.${C.lessons[C.lessons.indexOf(l) + 1]?.ready ? " The next lesson is open." : ""}` : "Under 2 of 3. Reread the lesson, then try again: the lessons that build on this one open when you pass it."}</span>
            ${score < 2 ? `<div><button type="button" class="lb-btn secondary sm" data-retry="${id}">Try again now</button></div>` : ""}</div>`;
    }
    return `<section class="lb-card cx-quiz" aria-label="Quiz">
      <div class="lb-card-head"><b>Quiz</b><span class="lb-note">${committed ? `Attempt ${last.n}` : "From memory, without scrolling up. The answers open after you submit"}</span></div>
      ${qs}
      ${committed ? result : `<div class="cx-actions">
        <button type="button" class="lb-btn" data-commit="${id}" ${answered && !ST.readOnly ? "" : "disabled"}>${ST.claude === "on" ? "Submit for Claude's check" : "Submit"}</button>
        ${draft.peek ? `<span class="lb-note">You peeked at the answers. That is recorded with the submission.</span>` : `<button type="button" class="lb-btn ghost sm" data-peek="${id}">Peek at the answers</button>`}
      </div>`}
    </section>`;
  }
  function gradePanel(l, t, key) {
    if (t.claude) {
      const c = t.claude;
      return `<div class="cx-grade"><div class="lb-row"><b>Claude's check</b>${verdictChip(c.verdict)}</div>
        ${c.feedback ? `<p>${esc(c.feedback)}</p>` : ""}
        ${c.missing && c.missing.length ? `<div class="cx-missing"><span class="lb-note">Missing</span><ul>${c.missing.map((m) => `<li>${esc(m)}</li>`).join("")}</ul></div>` : ""}</div>`;
    }
    if (t.self != null) return `<div class="cx-grade"><div class="lb-row"><b>Your own grade</b><span class="lb-chip ${t.self ? "success" : "danger"}">${t.self ? "✓ Got the point" : "✗ Missed it"}</span></div></div>`;
    if (ST.grading[key]) return `<div class="cx-grade is-busy"><div class="lb-row"><span class="lb-dot"></span><b>Claude is checking your answer…</b><button type="button" class="lb-btn ghost sm" data-stop="${esc(key)}">Stop</button></div><span class="lb-note">Usually under a minute. The first time, Claude asks you to allow this page.</span></div>`;
    const err = ST.gradeErr[key];
    const self = `<div class="lb-row"><span class="lb-note">Did your answer get the model answer's points?</span><button type="button" class="lb-btn sm" data-self="1" data-lid="${l.id}">Yes</button><button type="button" class="lb-btn secondary sm" data-self="0" data-lid="${l.id}">No</button></div>`;
    if (ST.claude === "on") return `<div class="cx-grade">${err ? `<span class="lb-chip danger">${esc(err)}</span>` : ""}
      <div class="lb-row"><button type="button" class="lb-btn sm" data-grade="${l.id}">${err ? "Ask Claude again" : "Ask Claude to check it"}</button></div>${err ? self : ""}</div>`;
    return `<div class="cx-grade"><span class="lb-note">${esc(ST.claude === "pending" ? "Connecting to Claude…" : ST.claudeOff || (ST.mode === "db" ? "Claude's check is not available in this view." : "Claude's check runs in the course page in Claude. Here you grade yourself."))}</span>${ST.claude === "pending" ? "" : self}</div>`;
  }
  function openLesson(id, from) {
    const l = LESSONS[id];
    if (!l || !isOpenable(l)) return;
    if (!LP(id).opened_at) patch("progress", { lessons: { [id]: { opened_at: nowIso(), opened_from: from ? "task" : "course" } } });
    ST.tab = "course"; ST.lesson = { id, from: from || null }; ST.project = null; ST.toTop = true;
    try { localStorage.setItem(KEY + ":tab", "course"); localStorage.setItem(KEY + ":lesson", id); } catch {}
    if (ST.drawer) closeDrawer();
    render();
  }
  function goHome() {
    ST.lesson = null; ST.project = null; ST.toTop = true;
    try { localStorage.removeItem(KEY + ":lesson"); } catch {}
    render();
  }
  function commit(id) {
    const l = LESSONS[id], draft = ST.quiz[id];
    if (!l || !draft) return;
    const n = count(LP(id).tries) + 1;
    const answers = {};
    for (const q of l.quiz) answers[q.n] = q.kind === "open" ? String(draft.answers[q.n] || "").trim() : Number(draft.answers[q.n]);
    ST.quiz[id] = { answers: {}, peek: false };
    patch("progress", { lessons: { [id]: { read_at: LP(id).read_at || nowIso(), tries: { [n]: { answers, committed_at: nowIso(), peeked: !!draft.peek } } } } });
    if (ST.claude === "on") gradeLesson(id, n);
  }
  async function gradeLesson(id, n) {
    const l = LESSONS[id], t = (LP(id).tries || {})[n], q = l && l.quiz.find((x) => x.kind === "open");
    if (!t || !q) return;
    const res = await askClaude(`${id}#${n}`, lessonPrompt(l, q, (t.answers || {})[q.n]));
    if (res) score(id, n, { claude: res, open: VERDICTS[res.verdict].score });
  }
  function score(id, n, extra) {
    const l = LESSONS[id], p = LP(id), t = (p.tries || {})[n];
    if (!l || !t) return;
    const s = rightOf(l, t) + extra.open, passed = s >= 2;
    patch("progress", { lessons: { [id]: { tries: { [n]: { ...extra, score: s } }, ...(passed && !p.passed ? { passed: true, passed_at: nowIso(), score: s } : {}) } } });
    toast(passed ? `${id} passed` : `${id}: redo`);
  }
  function selfGrade(id, ok) {
    const last = lastTry(LP(id));
    if (last) score(id, last.n, { self: ok ? 1 : 0, open: ok ? 1 : 0 });
  }

  // ---------- project page ----------
  const lastCheck = (pp) => { const n = count(pp.checks); return n ? { n, ...pp.checks[n] } : null; };
  function projectPage(id) {
    const p = PROJECTS[id], pp = PP(id), checks = Object.entries(pp.checks || {}).sort((a, b) => Number(b[0]) - Number(a[0]));
    const draft = ST.hand[id] ?? "", key = `${id}#${count(pp.checks)}`, busy = !!ST.grading[key];
    const last = lastCheck(pp), err = last && !last.verdict ? ST.gradeErr[key] : null;
    const attached = attachedData(p);
    const ro = ST.readOnly ? "disabled" : "";
    return `<div class="cx-crumbs"><button type="button" class="lb-btn ghost sm" data-home>← Course</button></div>
    <article class="cx-lesson">
      <header class="cx-lhead"><p class="lb-note">Project ${esc(p.id)} · week ${weekNo(p.week)} · ${HELP[p.help]}</p><h2>${esc(p.text)}</h2></header>
      <div class="lb-callout"><b>What Claude looks for</b><span>${esc(p.check)}</span></div>
      ${attached ? `<details class="lb-disclosure is-quiet"><summary><span class="lb-sum">Sent along with your hand-in<small>${p.attach === "links" ? "your tag values and this week's link log" : "your last saved weeks on the Numbers tab"}</small></span></summary><div class="lb-disclosure-body"><pre class="cx-pre">${esc(attached)}</pre></div></details>` : ""}
      <label class="lb-field">Your hand-in<textarea class="lb-textarea cx-hand" data-hand="${esc(id)}" placeholder="${p.attach === "links" ? "Which value you chose and why, and anything the link log doesn't show" : "Paste the message, the report or what you did"}" ${ro}>${esc(draft)}</textarea></label>
      <div class="cx-actions">
        <button type="button" class="lb-btn" data-handin="${esc(id)}" ${draft.trim() && !busy && !ST.readOnly ? "" : "disabled"}>${ST.claude === "on" ? "Hand in to Claude" : "Save the hand-in"}</button>
        <label class="lb-check"><input type="checkbox" data-project="${esc(id)}" ${pp.done_at ? "checked" : ""} ${ro}><span>Done</span></label>
      </div>
      ${ST.claude === "on" ? "" : `<p class="lb-note">${esc(ST.claudeOff || (ST.mode === "db" ? "Claude's check is not available in this view." : "Claude's check runs in the course page in Claude."))} Saved hand-ins stay in your progress, so Claude Code can check them later.</p>`}
      ${busy ? `<div class="cx-grade is-busy"><div class="lb-row"><span class="lb-dot"></span><b>Claude is checking your hand-in…</b><button type="button" class="lb-btn ghost sm" data-stop="${esc(key)}">Stop</button></div></div>` : ""}
      ${err ? `<div class="cx-grade"><span class="lb-chip danger">${esc(err)}</span><div><button type="button" class="lb-btn sm" data-recheck="${esc(id)}">Ask Claude again</button></div></div>` : ""}
      ${checks.length ? `<section class="lb-section"><div class="lb-section-head"><h2>Hand-ins</h2><span class="lb-meta">${checks.length}</span></div>
        ${checks.map(([n, c]) => `<div class="lb-card cx-grade"><div class="lb-row"><b>#${esc(n)} · ${dmy(new Date(c.at || c.handed_at))}</b>${c.verdict ? verdictChip(c.verdict) : `<span class="lb-chip outline">Not checked</span>`}${c.redo ? `<span class="lb-chip danger">Redo it</span>` : ""}</div>
          ${c.feedback ? `<p>${esc(c.feedback)}</p>` : ""}
          ${c.missing && c.missing.length ? `<div class="cx-missing"><span class="lb-note">Missing</span><ul>${c.missing.map((m) => `<li>${esc(m)}</li>`).join("")}</ul></div>` : ""}
          <details class="lb-disclosure is-quiet"><summary><span class="lb-sum">What you handed in</span></summary><div class="lb-disclosure-body"><p class="cx-pre">${esc(c.text)}</p></div></details></div>`).join("")}
      </section>` : ""}
    </article>`;
  }
  function handIn(id) {
    const p = PROJECTS[id], text = String(ST.hand[id] || "").trim();
    if (!p || !text) return;
    const n = count(PP(id).checks) + 1;
    patch("progress", { projects: { [id]: { checks: { [n]: { text: text.slice(0, 8000), handed_at: nowIso() } } } } });
    ST.hand[id] = "";
    if (ST.claude === "on") gradeProject(id, n); else toast("Hand-in saved");
  }
  async function gradeProject(id, n) {
    const p = PROJECTS[id], c = (PP(id).checks || {})[n];
    if (!p || !c) return;
    const res = await askClaude(`${id}#${n}`, projectPrompt(p, c.text, attachedData(p)), true);
    if (!res) return;
    const pass = (res.verdict === "correct" || res.verdict === "above") && !res.redo;
    patch("progress", { projects: { [id]: { checks: { [n]: res }, ...(pass && !PP(id).done_at ? { done_at: nowIso() } : {}) } } });
    toast(pass ? `${id} passed Claude's check` : `${id}: see Claude's notes`);
  }

  // ---------- tasks tab ----------
  function tasksTab() {
    const all = tasks().sort((a, b) => (a.created_at < b.created_at ? 1 : -1));
    const open = all.filter((t) => !t.done), done = all.filter((t) => t.done).sort((a, b) => (a.done_at < b.done_at ? 1 : -1));
    const w = courseWeek(), projects = C.projects.filter((p) => p.week === w);
    const typeRows = C.types.filter((t) => t.checklist.length).map((t) => `<tr><td>${esc(t.name)}</td><td>${fmt(doneOfType(t.id))}</td><td>${esc(fadeFor(t.id).label)}</td></tr>`).join("");
    return `
    <section class="lb-card cx-add">
      <form id="cx-add-form" autocomplete="off">
        <input class="lb-input" id="cx-new" name="title" placeholder="New task" aria-label="New task" maxlength="200" ${ST.readOnly ? "disabled" : ""}>
        <button class="lb-btn" type="submit" ${ST.readOnly ? "disabled" : ""}>Add</button>
      </form>
      <div class="cx-types" role="group" aria-label="Task type">${C.types.map((t) => `<button type="button" class="cx-type" data-newtype="${t.id}" aria-pressed="${ST.newType === t.id}">${esc(t.name)}</button>`).join("")}</div>
      <div class="cx-templates"><span class="lb-note">Templates:</span>${TEMPLATES.map(([type, title]) => `<button type="button" class="lb-btn secondary sm" data-template="${type}" data-title="${esc(title)}" ${ST.readOnly ? "disabled" : ""}>${esc(title)}</button>`).join("")}</div>
    </section>
    ${projects.length ? `<section class="lb-card is-quiet">
      <div class="lb-card-head"><b>This week's projects</b></div>
      <div class="cx-steps">${projects.map((p) => { const d = PP(p.id).done_at; return `<div class="cx-proj"><label class="lb-check"><input type="checkbox" data-project="${p.id}" ${d ? "checked" : ""} ${ST.readOnly ? "disabled" : ""}><span><b>${p.id}</b> · ${esc(p.text)} <span class="lb-note">(${HELP[p.help]})</span></span></label><button type="button" class="lb-btn ghost sm" data-project="${p.id}">Hand in</button></div>`; }).join("")}</div>
    </section>` : ""}
    <section class="lb-section">
      <div class="lb-section-head"><h2>Open</h2><span class="lb-meta">${open.length}</span></div>
      ${open.length ? `<div class="lb-group cx-list">${open.map(taskRow).join("")}</div>` : `<div class="lb-empty">${ST.loaded || ST.mode === "local" ? "No open tasks. Add one above, or tap a template." : "Loading tasks…"}</div>`}
    </section>
    ${done.length ? `<details class="lb-disclosure"><summary><span class="lb-sum">Done<small>${done.length} tasks</small></span></summary>
      <div class="lb-group cx-list">${done.slice(0, 60).map(taskRow).join("")}</div></details>` : ""}
    <details class="lb-disclosure is-quiet"><summary><span class="lb-sum">How the checklists fade<small>by how many tasks of that type are done</small></span></summary><div class="lb-disclosure-body">
      <p class="lb-note">${C.fade.map((f, i) => `${i === 0 ? "1" : C.fade[i - 1].upto + 1}${f.upto ? ` to ${f.upto}` : " and up"}: ${esc(f.label)}`).join(" · ")}</p>
      <div class="lb-table-wrap"><table class="lb-table"><thead><tr><th>Type</th><th>Done</th><th>The checklist now</th></tr></thead><tbody>${typeRows}</tbody></table></div></div></details>`;
  }
  function taskRow(t) {
    const type = TYPES[t.type] || TYPES.other, l = !t.done && nextLesson(t.type);
    return `<div class="cx-task ${t.done ? "is-done" : ""}">
      <label class="lb-check" aria-label="Done"><input type="checkbox" data-done="${esc(t.id)}" ${t.done ? "checked" : ""} ${ST.readOnly ? "disabled" : ""}><span class="lb-sr">Done</span></label>
      <button type="button" class="cx-open" data-task="${esc(t.id)}"><span class="cx-title">${esc(t.title)}</span>
        <span class="cx-meta"><span class="lb-chip">${esc(type.name)}</span>${l ? `<span class="lb-chip cx-lesson">Lesson ${esc(l.id)}</span>` : ""}${type.mac_only ? `<span class="lb-chip outline">Mac</span>` : ""}</span></button>
      <span class="cx-chev" aria-hidden="true"></span>
    </div>`;
  }

  // ---------- drawer (the task sheet) ----------
  let drawerEl = null, scrimEl = null;
  function openDrawer(d) { ST.drawer = d; renderDrawer(true); }
  function closeDrawer() { ST.drawer = null; renderDrawer(); }
  function renderDrawer(focus) {
    if (!ST.drawer) { drawerEl?.remove(); scrimEl?.remove(); drawerEl = scrimEl = null; document.body.style.overflow = ""; return; }
    if (!drawerEl) {
      scrimEl = document.createElement("div"); scrimEl.className = "lb-scrim"; scrimEl.addEventListener("click", closeDrawer);
      drawerEl = document.createElement("aside"); drawerEl.className = "lb-drawer cx-drawer"; drawerEl.setAttribute("role", "dialog"); drawerEl.setAttribute("aria-modal", "true"); drawerEl.dir = "ltr"; drawerEl.lang = "en";
      drawerEl.addEventListener("click", onClick); drawerEl.addEventListener("change", onChange); drawerEl.addEventListener("input", onInput); drawerEl.addEventListener("focusout", onFocusOut); drawerEl.addEventListener("submit", onSubmit);
      document.body.append(scrimEl, drawerEl);
      document.body.style.overflow = "hidden";
    }
    const html = taskSheet(ST.drawer.id);
    if (html == null) { closeDrawer(); return; }
    const scroller = drawerEl.querySelector(".lb-drawer-body"), top = scroller && !focus ? scroller.scrollTop : 0;
    drawerEl.innerHTML = html;
    const nb = drawerEl.querySelector(".lb-drawer-body"); if (nb) nb.scrollTop = top;
    if (focus) drawerEl.querySelector("[data-close]")?.focus();
  }
  function taskSheet(id) {
    const t = (D.tasks.items || {})[id];
    if (!t || t.deleted) return null;
    const type = TYPES[t.type] || TYPES.other, fade = fadeFor(t.type, t.id), l = nextLesson(t.type);
    const steps = type.checklist || [], checked = t.checked || {};
    const ro = ST.readOnly ? "disabled" : "";
    const list = steps.map((s, i) => `<label class="lb-check"><input type="checkbox" data-step="${i}" data-tid="${esc(t.id)}" ${checked[i] ? "checked" : ""} ${ro}><span>${esc(s)}</span></label>`).join("");
    let checklist = "";
    if (steps.length) {
      if (fade.mode === "open") checklist = `<div class="cx-steps">${list}</div>`;
      else if (fade.mode === "folded") checklist = `<details class="lb-disclosure"><summary><span class="lb-sum">The checklist<small>${steps.length} steps</small></span></summary><div class="lb-disclosure-body cx-steps">${list}</div></details>`;
      else checklist = `<label class="lb-field">Your steps, before you look at the checklist<textarea class="lb-textarea" data-own="${esc(t.id)}" ${ro}>${esc(t.own_steps || "")}</textarea></label>
        ${t.compared ? `<div class="cx-steps">${list}</div>` : `<div><button type="button" class="lb-btn secondary sm" data-compare="${esc(t.id)}" ${t.own_steps ? "" : "disabled"} ${ro}>Compare with the checklist</button></div>`}`;
    }
    const lst = l && lessonState(l);
    return `<div class="lb-drawer-head"><h2>${esc(t.title)}</h2>
      <button type="button" class="lb-btn ghost icon" data-close aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>
    <div class="lb-drawer-body"><div class="cx-sheet">
      <label class="lb-field">Task<input class="lb-input" data-title-of="${esc(t.id)}" value="${esc(t.title)}" maxlength="200" ${ro}></label>
      <label class="lb-field">Type<select class="lb-select" data-type-of="${esc(t.id)}" ${ro}>${C.types.map((x) => `<option value="${x.id}" ${x.id === t.type ? "selected" : ""}>${esc(x.name)}</option>`).join("")}</select></label>
      ${type.where ? `<p class="lb-note">Where: ${esc(type.where)}${type.mac_only ? ". That screen runs only on the Mac, so it won't open on the phone" : ""}</p>` : ""}
      ${l ? `<div class="lb-callout info"><b>${esc(l.id)} · ${esc(l.title)}</b><span>${l.min} minutes of reading and a 3-question quiz.${lst.s === "retry" ? " Last time it was under 2 of 3, so it is back." : ""}</span><div><button type="button" class="lb-btn sm" data-lesson="${esc(l.id)}" data-from="${esc(t.id)}">Open the lesson</button></div></div>` : `<p class="lb-note">${type.id === "other" ? "Tasks of type Other have no lesson." : "No lesson of this type is open right now."}</p>`}
      ${steps.length ? `<div class="cx-part"><h3>The checklist</h3><p class="cx-fade">${esc(fade.label)} (${doneOfType(t.type, t.id)} ${esc(type.name)} tasks done)</p>${checklist}</div>` : ""}
      ${t.type === "dm" || t.type === "moment" ? `<div><button type="button" class="lb-btn secondary sm" data-goto="links">Make a tagged link</button></div>` : ""}
      ${t.type === "numbers" ? `<div><button type="button" class="lb-btn secondary sm" data-goto="numbers">Go to the Numbers tab</button></div>` : ""}
      <label class="lb-field">Notes<textarea class="lb-textarea" data-note-of="${esc(t.id)}" ${ro}>${esc(t.note || "")}</textarea></label>
      <div class="cx-actions">
        <button type="button" class="lb-btn ${t.done ? "secondary" : ""}" data-toggle="${esc(t.id)}" ${ro}>${t.done ? "Back to open" : "Done"}</button>
        <button type="button" class="lb-btn ghost sm" data-del="${esc(t.id)}" ${ro}>Delete</button>
      </div>
      <p class="lb-note">Added ${dmy(new Date(t.created_at))}${t.done_at ? ` · done ${dmy(new Date(t.done_at))}` : ""}. "Done" works without reading the lesson.</p>
    </div></div>`;
  }

  // ---------- sales tab (Yossi's order export) ----------
  // Only paid orders whose utm_medium is exactly Yarin's tag value count toward their 25% (course/discovery.md, the pay
  // rule; research/cro-crm/yossi-messages-2026-10-31.md, message 1). The admin can't show that, so Yossi sends an
  // export and Yarin pastes it here. Its columns aren't fixed yet, so the import guesses which column is which and
  // Yarin corrects that before adding. Kept in course/sales:
  // - orders.<key>: only orders tagged with Yarin's value or an October value (dm, bio, story), keyed by order number,
  //   so an export that overlaps an earlier one updates those orders instead of counting them twice;
  // - days.<yyyy-mm-dd>: every paid order counted per day (all, and those with any tag), for the share of tagged
  //   orders. An import replaces each day it covers, days with no orders included;
  // - imports.<id>: what each paste added. Removing one sets its orders and days to null (keys are never removed).
  const OCT = ["dm", "bio", "story"]; // October's link values (research/cro-crm/measurement.md §4), not counted by the rule
  const ROLES = [
    { k: "order", name: "Order number", need: true }, { k: "date", name: "Payment date", need: true },
    { k: "amount", name: "Amount" }, { k: "medium", name: "utm_medium, the one that counts", need: true },
    { k: "medium2", name: "utm_medium, the other touch", hint: "only if the export has first and last touch" },
    { k: "source", name: "utm_source" }, { k: "campaign", name: "utm_campaign" }, { k: "content", name: "utm_content" },
    { k: "status", name: "Status", hint: "only if the export also lists unpaid orders" },
  ];
  const PERIODS = [["week", "This week"], ["lastweek", "Last week"], ["month", "This month"], ["lastmonth", "Last month"], ["all", "All"]];
  const UNPAID = /cancel|refund|fail|pend|draft|editor|abandon|unpaid|declin|בוטל|החזר|נכשל|ממתין|טיוטה|לא שולם/i;
  const ils = (n) => (n == null ? "-" : `₪${Number(n).toLocaleString("en-US", { maximumFractionDigits: 0 })}`);
  const pl = (n, one, many) => `${fmt(n)} ${n === 1 ? one : many}`;
  const okey = (n) => "o" + String(n).replace(/[^A-Za-z0-9_-]/g, "_").slice(0, 80);
  const amt = (s) => { const n = parseFloat(String(s ?? "").replace(/[^\d.\-]/g, "")); return Number.isFinite(n) ? n : null; };
  const okDate = (y, mo, d) => (y > 2000 && mo >= 1 && mo <= 12 && d >= 1 && d <= 31 ? `${y}-${String(mo).padStart(2, "0")}-${String(d).padStart(2, "0")}` : null);
  function parseDate(s) { // the day in Israel: ISO, a timestamp with a zone, day / month / year, or epoch
    s = String(s || "").trim(); let m;
    if (/^\d{10,13}$/.test(s)) return iso(new Date(Number(s) * (s.length === 10 ? 1000 : 1)));
    if (/T\d{2}:\d{2}.*(Z|[+-]\d{2}:?\d{2})$/.test(s) && !Number.isNaN(Date.parse(s))) return iso(new Date(s));
    if ((m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/))) return okDate(+m[1], +m[2], +m[3]);
    if ((m = s.match(/^(\d{1,2})[/.](\d{1,2})[/.](\d{2,4})/))) return okDate(+m[3] < 100 ? 2000 + +m[3] : +m[3], +m[2], +m[1]);
    const t = Date.parse(s); return Number.isNaN(t) ? null : iso(new Date(t));
  }
  function flatten(o, pre = "", out = {}) {
    for (const [k, v] of Object.entries(o || {})) {
      if (isObj(v)) flatten(v, pre + k + ".", out); else if (v != null && !Array.isArray(v)) out[pre + k] = String(v);
    }
    return out;
  }
  function parseTable(text) { // a spreadsheet copy (tabs), a CSV (comma or semicolon) or JSON rows → {head, rows}
    text = String(text || "").replace(/^﻿/, "").trim();
    if (!text) return null;
    if (/^[[{]/.test(text)) {
      try {
        let j = JSON.parse(text);
        if (isObj(j)) j = Object.values(j).find(Array.isArray) || [j];
        const flat = j.filter(isObj).map((x) => flatten(x)), head = [...new Set(flat.flatMap(Object.keys))];
        return flat.length ? { head, rows: flat.map((f) => head.map((h) => f[h] ?? "")) } : null;
      } catch {} // not JSON after all: read it as a table
    }
    const line = text.split(/\r?\n/, 1)[0];
    const delim = line.includes("\t") ? "\t" : line.split(";").length > line.split(",").length ? ";" : ",";
    const all = []; let row = [], cell = "", q = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
      else if (c === '"' && cell === "") q = true;
      else if (c === delim) { row.push(cell); cell = ""; }
      else if (c === "\n" || c === "\r") { if (c === "\r" && text[i + 1] === "\n") i++; row.push(cell); all.push(row); row = []; cell = ""; }
      else cell += c;
    }
    row.push(cell); all.push(row);
    const clean = all.map((r) => r.map((x) => x.trim())).filter((r) => r.some(Boolean));
    if (clean.length < 2) return null;
    const head0 = clean[0].map((h, i) => h || `Column ${i + 1}`);
    let head = head0, rows = clean.slice(1);
    head0.forEach((h, i) => { // a cell holding JSON (acquisitionAttribution, say) becomes one column per field
      if (!rows.some((r) => /^\{/.test(r[i] || ""))) return;
      const flat = rows.map((r) => { try { return flatten(JSON.parse(r[i])); } catch { return {}; } });
      const keys = [...new Set(flat.flatMap(Object.keys))];
      head = head.concat(keys.map((k) => `${h}.${k}`));
      rows = rows.map((r, n) => r.concat(keys.map((k) => flat[n][k] ?? "")));
    });
    return { head, rows };
  }
  function guessMap(head) { // the column for each role; utm columns of the same touch as the counted medium go together
    const H = head.map((h) => h.toLowerCase().replace(/[\s_-]+/g, ""));
    const find = (re, not) => H.map((h, i) => (re.test(h) && !(not && not.test(h)) ? i : -1)).filter((i) => i >= 0);
    const mediums = find(/medium/);
    const last = mediums.find((i) => /last/.test(H[i])), first = mediums.find((i) => /first/.test(H[i]));
    const medium = last ?? first ?? mediums[0] ?? -1, touch = last != null ? "last" : first != null ? "first" : "";
    const pick = (list) => list.find((i) => touch && H[i].includes(touch)) ?? list[0] ?? -1;
    const dates = find(/date|time|paidat|createdat|תאריך/), amounts = find(/amount|total|price|sum|revenue|value|סכום|מחיר/, /date|time|status|utm|תאריך/);
    return {
      order: find(/^(id|order|orderid|ordernumber|orderno|מספרהזמנה|הזמנה|מספר)$/)[0] ?? find(/order|הזמנה/, /date|time|status|amount|total|utm|תאריך|סכום/)[0] ?? -1,
      date: dates.find((i) => /paid|payment|תשלום/.test(H[i])) ?? dates[0] ?? -1,
      amount: amounts.find((i) => /amount|total|סכום/.test(H[i])) ?? amounts[0] ?? -1,
      medium, medium2: mediums.find((i) => i !== medium) ?? -1,
      source: pick(find(/source/)), campaign: pick(find(/campaign/)), content: pick(find(/content/)),
      status: find(/status|state|סטטוס|מצב/)[0] ?? -1,
    };
  }
  function fillStatus(I) {
    I.statuses = []; I.paid = {};
    if (!(I.map.status >= 0)) return;
    const seen = {};
    for (const r of I.table.rows) { const v = String(r[I.map.status] ?? "").trim(); seen[v] = (seen[v] || 0) + 1; }
    I.statuses = Object.entries(seen).sort((a, b) => b[1] - a[1]).slice(0, 30);
    for (const [v] of I.statuses) I.paid[v] = !UNPAID.test(v);
  }
  function loadImport(text, name) {
    if (ST.imp && ST.imp.text === text && !name) { render(); return; }
    const table = parseTable(text);
    const I = { text, name: name || "", table, map: {}, paid: {}, statuses: [], minor: false };
    if (table) {
      I.map = guessMap(table.head);
      fillStatus(I);
      const a = table.rows.map((r) => amt(r[I.map.amount])).filter((x) => x != null).sort((x, y) => x - y);
      I.minor = a.length > 0 && a[Math.floor(a.length / 2)] >= 1000; // the store's API counts in agorot (11900 = ₪119)
    }
    ST.imp = I; render();
  }
  const tagValue = () => slug(tags().medium) || "social";
  const keepOrder = (o, tag) => [o.medium, o.medium_other].some((m) => m && (m === tag || OCT.includes(m)));
  function readImport() { // the pasted export with the current column choices → what "Add" would write
    const I = ST.imp; if (!I || !I.table) return null;
    const M = I.map, missing = ROLES.filter((r) => r.need && !(M[r.k] >= 0)).map((r) => r.name);
    if (missing.length) return { missing };
    const col = (r, k) => (M[k] >= 0 ? String(r[M[k]] ?? "").trim() : "");
    const tag = tagValue(), byKey = {}, dup = new Set();
    let skipped = 0, unpaid = 0;
    const gone = new Set(); // unpaid now, so a refund drops an order an earlier export counted
    for (const r of I.table.rows) {
      const n = col(r, "order"), d = parseDate(col(r, "date"));
      if (!n || !d) { skipped++; continue; }
      if (M.status >= 0 && !I.paid[col(r, "status")]) { unpaid++; gone.add(okey(n)); continue; }
      let a = M.amount >= 0 ? amt(col(r, "amount")) : null;
      if (a != null) a = Math.round((I.minor ? a / 100 : a) * 100) / 100;
      const k = okey(n);
      if (byKey[k]) { dup.add(k); if (a != null) byKey[k].amount = Math.round(((byKey[k].amount || 0) + a) * 100) / 100; continue; }
      byKey[k] = { number: n.slice(0, 80), paid_on: d, amount: a, medium: col(r, "medium").toLowerCase(), medium_other: col(r, "medium2").toLowerCase(),
        source: col(r, "source").toLowerCase().slice(0, 60), campaign: col(r, "campaign").slice(0, 80), content: col(r, "content").slice(0, 80) };
    }
    const orders = Object.entries(byKey), dates = orders.map(([, o]) => o.paid_on).sort();
    const from = dates[0], to = dates[dates.length - 1];
    const span = from ? Math.round((parseDay(to) - parseDay(from)) / 864e5) + 1 : 0;
    const known = Object.keys(D.sales.days || {}).filter((d) => D.sales.days[d] && d >= from && d <= to).length;
    const dropped = [...gone].filter((k) => !byKey[k] && (D.sales.orders || {})[k]);
    return { orders, from, to, span, known, skipped, unpaid, dup: dup.size, tag, dropped,
      mine: orders.filter(([, o]) => o.medium === tag).length, kept: orders.filter(([, o]) => keepOrder(o, tag)).length };
  }
  function addImport() {
    const R = readImport();
    if (!R || R.missing || !R.orders.length || R.span > 400) return;
    const id = uid("i"), days = {}, orders = Object.fromEntries(R.dropped.map((k) => [k, null]));
    for (let d = parseDay(R.from); iso(d) <= R.to; d = addDays(d, 1)) days[iso(d)] = { paid: 0, tagged: 0, amount: 0, imp: id };
    for (const [k, o] of R.orders) {
      const x = days[o.paid_on];
      x.paid++; if (o.medium || o.medium_other) x.tagged++; if (o.amount != null) x.amount = Math.round((x.amount + o.amount) * 100) / 100;
      if (keepOrder(o, R.tag)) orders[k] = { ...o, imp: id };
    }
    const M = ST.imp.map, H = ST.imp.table.head;
    patch("sales", { orders, days, imports: { [id]: { at: nowIso(), file: ST.imp.name || null, from: R.from, to: R.to, paid: R.orders.length, mine: R.mine, counted_value: R.tag, medium_column: H[M.medium] || null } } });
    ST.imp = null;
    toast(`Added: ${R.mine} of ${R.orders.length} paid orders carry your tag`);
  }
  function removeImport(id) {
    const nulls = (o) => Object.fromEntries(Object.entries(o || {}).filter(([, x]) => x && x.imp === id).map(([k]) => [k, null]));
    patch("sales", { orders: nulls(D.sales.orders), days: nulls(D.sales.days), imports: { [id]: { removed_at: nowIso() } } });
    toast("Export removed");
  }
  function periodRange(p) {
    const t = day0();
    if (p === "week") { const a = weekStart(t); return [iso(a), iso(addDays(a, 6))]; }
    if (p === "lastweek") { const a = addDays(weekStart(t), -7); return [iso(a), iso(addDays(a, 6))]; }
    if (p === "month") return [iso(new Date(t.getFullYear(), t.getMonth(), 1)), iso(new Date(t.getFullYear(), t.getMonth() + 1, 0))];
    if (p === "lastmonth") return [iso(new Date(t.getFullYear(), t.getMonth() - 1, 1)), iso(new Date(t.getFullYear(), t.getMonth(), 0))];
    return ["0000-00-00", "9999-99-99"];
  }
  function salesIn(from, to) {
    const tag = tagValue(), sum = (xs, f) => xs.reduce((s, x) => s + (Number(f(x)) || 0), 0);
    const days = Object.entries(D.sales.days || {}).filter(([d, x]) => x && d >= from && d <= to).map(([d]) => d).sort();
    const all = Object.values(D.sales.orders || {}).filter((o) => o && o.paid_on >= from && o.paid_on <= to);
    const mine = all.filter((o) => o.medium === tag).sort((a, b) => (a.paid_on < b.paid_on ? 1 : -1));
    return {
      tag, days, mine, paid: sum(days, (d) => D.sales.days[d].paid), tagged: sum(days, (d) => D.sales.days[d].tagged),
      amount: mine.some((o) => o.amount != null) ? sum(mine, (o) => o.amount) : null,
      either: all.filter((o) => o.medium === tag || o.medium_other === tag).length,
      oct: all.filter((o) => o.medium !== tag && o.medium_other !== tag && (OCT.includes(o.medium) || OCT.includes(o.medium_other))).length,
    };
  }
  function salesTab() {
    const imps = Object.entries(D.sales.imports || {}).filter(([, x]) => x && !x.removed_at).sort((a, b) => (a[1].at < b[1].at ? 1 : -1));
    const [from, to] = periodRange(ST.salesPeriod), S = salesIn(from, to), today = iso(day0());
    const span = ST.salesPeriod === "all" ? null : Math.max(0, Math.round((parseDay(to < today ? to : today) - parseDay(from)) / 864e5) + 1);
    const cover = !S.days.length ? "No export covers these days yet"
      : span == null ? `Exports cover ${dmy(parseDay(S.days[0]))} to ${dmy(parseDay(S.days[S.days.length - 1]))}`
      : `Exports cover ${S.days.length} of the ${span} days so far`;
    const pct = (a, b) => (b ? `${Math.round((a / b) * 100)}%` : "-");
    const groups = {};
    for (const o of S.mine) { const k = [o.source, o.campaign, o.content].join("|"); (groups[k] ||= { o, n: 0, a: 0 }); groups[k].n++; groups[k].a += Number(o.amount) || 0; }
    const g = Object.values(groups).sort((a, b) => b.n - a.n || b.a - a.a);
    const cell = (v) => (v ? `<bdi dir="ltr">${esc(v)}</bdi>` : `<span class="lb-note">none</span>`);
    return `<section class="lb-section">
      <div class="lb-section-head"><h2>Sales that carry your tag</h2><span class="lb-meta">Paid orders with ${ltr("utm_medium=" + S.tag)}, from Yossi's export</span></div>
      <div class="lb-segmented cx-periods" role="group" aria-label="Period">${PERIODS.map(([v, l]) => `<button type="button" data-speriod="${v}" aria-pressed="${ST.salesPeriod === v}">${l}</button>`).join("")}</div>
      <div class="lb-grid cx-stats">
        <div class="lb-card lb-stat"><span class="lb-stat-label">Your orders</span><span class="lb-stat-value">${S.days.length ? fmt(S.mine.length) : "-"}</span><span class="lb-stat-foot">${esc(cover)}</span></div>
        <div class="lb-card lb-stat"><span class="lb-stat-label">Their amount</span><span class="lb-stat-value">${ils(S.amount)}</span><span class="lb-stat-foot">${S.days.length && S.amount == null ? "The export had no amount column" : "What these orders paid"}</span></div>
        <div class="lb-card lb-stat"><span class="lb-stat-label">Your 25%</span><span class="lb-stat-value">${S.amount == null ? "-" : ils(S.amount * 0.25)}</span><span class="lb-stat-foot">If it's 25% of that amount: price only or with shipping is still open with Yossi</span></div>
        <div class="lb-card lb-stat"><span class="lb-stat-label">Paid orders with any tag</span><span class="lb-stat-value">${S.days.length ? `${fmt(S.tagged)} <small>of ${fmt(S.paid)}</small>` : "-"}</span><span class="lb-stat-foot">${S.paid ? `${pct(S.tagged, S.paid)} of all paid orders. The rest carry no tag at all` : "All orders, yours, ads and the rest"}</span></div>
      </div>
      ${S.either > S.mine.length ? `<div class="lb-callout"><b>${fmt(S.either)} orders if either touch counted</b><span>${pl(S.either - S.mine.length, "more order carries", "more orders carry")} your tag on the other touch only. Settle in writing with Yossi which touch counts.</span></div>` : ""}
      ${S.oct ? `<div class="lb-callout"><b>${pl(S.oct, "more order", "more orders")} with your October link values</b><span>They carry ${ltr("utm_medium=dm")}, ${ltr("bio")} or ${ltr("story")}, which the exact rule doesn't count. Ask Yossi about them.</span></div>` : ""}
    </section>
    ${S.mine.length ? `<section class="lb-section"><div class="lb-section-head"><h2>Where they came from</h2><span class="lb-meta">By link</span></div>
      <div class="lb-table-wrap"><table class="lb-table"><thead><tr><th>Network</th><th>Campaign</th><th>Placement</th><th class="num">Orders</th><th class="num">Amount</th></tr></thead><tbody>
      ${g.map((x) => `<tr><td>${cell(x.o.source)}</td><td>${cell(x.o.campaign)}</td><td>${cell(x.o.content)}</td><td class="num">${fmt(x.n)}</td><td class="num">${S.amount == null ? "-" : ils(x.a)}</td></tr>`).join("")}
      </tbody></table></div></section>
    <details class="lb-disclosure"><summary><span class="lb-sum">Your orders<small>${fmt(S.mine.length)}, newest first</small></span></summary><div class="lb-disclosure-body">
      <div class="lb-table-wrap"><table class="lb-table"><thead><tr><th>Paid</th><th>Order</th><th class="num">Amount</th><th>Campaign</th><th>Placement</th></tr></thead><tbody>
      ${S.mine.slice(0, 200).map((o) => `<tr><td>${dmy(parseDay(o.paid_on))}</td><td>${cell(o.number)}</td><td class="num">${o.amount == null ? "-" : ils(o.amount)}</td><td>${cell(o.campaign)}</td><td>${cell(o.content)}</td></tr>`).join("")}
      </tbody></table></div></div></details>` : ""}
    <div class="lb-card is-quiet cx-cannot"><div class="cx-part"><h3>What this can't prove</h3><p>A sale your post caused that arrived without your tag isn't here: the tag is lost when the buyer closes the tab and comes back later, and visitors who decline cookies carry none. These are the orders Yossi's export shows with your tag, nothing more.</p></div></div>
    ${importSection(imps)}`;
  }
  function importSection(imps) {
    const I = ST.imp, ro = ST.readOnly ? "disabled" : "";
    return `<section class="lb-section">
      <div class="lb-section-head"><h2>Add Yossi's export</h2><span class="lb-meta">Paid orders, one row each</span></div>
      ${imps.length ? "" : `<div class="lb-callout"><b>No export yet</b><span>Ask Yossi for paid orders with order number, payment date, amount, utm_source, utm_medium, utm_campaign and utm_content. A spreadsheet copy, a CSV file or JSON all work. Before the first real one, make a test order through a link with its own campaign (say ${ltr("utm_campaign=test-1")}) and check it shows up here.</span></div>`}
      <div class="lb-card cx-imp">
        <label class="lb-field">Paste the rows, header row included<textarea class="lb-textarea cx-paste" dir="ltr" data-imptext placeholder="Select the rows in the spreadsheet, copy, paste here" ${ro}>${esc(I ? I.text : "")}</textarea></label>
        <div class="lb-row"><button type="button" class="lb-btn secondary sm" data-pickfile ${ro}>Or choose a file</button><input type="file" accept=".csv,.tsv,.txt,.json,text/csv,application/json" data-impfile hidden>${I && I.name ? `<span class="lb-note">${esc(I.name)}</span>` : ""}</div>
        ${importPreview()}
      </div>
    </section>
    ${imps.length ? `<details class="lb-disclosure is-quiet"><summary><span class="lb-sum">Exports added<small>${imps.length}</small></span></summary><div class="lb-disclosure-body"><div class="lb-group">
      ${imps.map(([id, x]) => `<div class="cx-log"><div><b>${dmy(parseDay(x.from))} to ${dmy(parseDay(x.to))}</b> <span class="lb-note">added ${dmy(new Date(x.at))}${x.file ? ` · ${esc(x.file)}` : ""}</span><div class="lb-note">${fmt(x.paid)} paid orders, ${fmt(x.mine)} with ${ltr("utm_medium=" + x.counted_value)}${x.medium_column ? `, from the column ${ltr(x.medium_column)}` : ""}</div></div>
        <button type="button" class="lb-btn ghost sm" data-impdel="${esc(id)}" ${ro}>Remove</button></div>`).join("")}
    </div></div></details>` : ""}`;
  }
  function importPreview() {
    const I = ST.imp;
    if (!I || !I.text.trim()) return "";
    if (!I.table) return `<span class="lb-note">No table found. Paste the rows together with their header row, or choose the CSV file.</span>`;
    const R = readImport(), H = I.table.head, ex = I.table.rows[0] || [], ro = ST.readOnly ? "disabled" : "";
    const sel = (r) => `<label class="lb-field">${esc(r.name)}${r.hint ? ` <span class="lb-note">${esc(r.hint)}</span>` : ""}<select class="lb-select" data-improle="${r.k}" ${ro}>
      <option value="-1">${r.need ? "Choose…" : "Not in this export"}</option>${H.map((h, i) => `<option value="${i}" ${I.map[r.k] === i ? "selected" : ""}>${esc(h)}${ex[i] ? ` · e.g. ${esc(String(ex[i]).slice(0, 28))}` : ""}</option>`).join("")}</select></label>`;
    let sum;
    if (R.missing) sum = `<div class="lb-callout"><b>Choose the column for ${esc(R.missing.join(", "))}</b><span>Then the count shows here.</span></div>`;
    else if (!R.orders.length) sum = `<div class="lb-callout"><b>No paid orders read</b><span>Check the order number and payment date columns${I.map.status >= 0 ? ", and which statuses count as paid" : ""}.</span></div>`;
    else if (R.span > 400) sum = `<div class="lb-callout"><b>The dates run from ${esc(R.from)} to ${esc(R.to)}</b><span>Over a year. Check the payment date column.</span></div>`;
    else sum = `<div class="lb-callout info"><b>${fmt(R.mine)} of ${fmt(R.orders.length)} paid orders carry ${ltr("utm_medium=" + R.tag)}</b>
      <span>Paid ${dmy(parseDay(R.from))} to ${dmy(parseDay(R.to))}.${R.known ? ` ${R.known} of these ${R.span} days came in an earlier export: this one replaces them.` : ""}${R.skipped ? ` ${pl(R.skipped, "row had", "rows had")} no order number or date and ${R.skipped === 1 ? "was" : "were"} left out.` : ""}${R.unpaid ? ` ${pl(R.unpaid, "unpaid row", "unpaid rows")} left out.` : ""}${R.dropped.length ? ` ${pl(R.dropped.length, "order an earlier export counted is", "orders an earlier export counted are")} no longer paid and will leave your count.` : ""}${R.dup ? ` ${pl(R.dup, "order number was", "order numbers were")} on more than one row: each counts once, amounts added.` : ""}${I.map.status >= 0 ? "" : " No status column, so every row counts as paid."}</span>
      <div class="lb-row"><button type="button" class="lb-btn" data-impadd ${ro}>Add ${pl(R.orders.length, "order", "orders")}</button><button type="button" class="lb-btn ghost sm" data-impclear>Clear</button></div></div>`;
    return `<div class="lb-grid cx-roles">${ROLES.map(sel).join("")}</div>
      ${I.map.status >= 0 && I.statuses.length ? `<div class="lb-field">Statuses that mean paid<div class="cx-statuses">${I.statuses.map(([v, n], i) => `<label class="lb-check"><input type="checkbox" data-imppaid="${i}" ${I.paid[v] ? "checked" : ""} ${ro}><span><bdi dir="ltr">${esc(v || "(empty)")}</bdi> <span class="lb-note">${fmt(n)}</span></span></label>`).join("")}</div></div>` : ""}
      ${I.map.amount >= 0 ? `<label class="lb-check"><input type="checkbox" data-impminor ${I.minor ? "checked" : ""} ${ro}><span>Amounts are in agorot (11900 means ₪119)</span></label>` : ""}
      ${sum}`;
  }

  // ---------- numbers tab ----------
  const FIELDS = [
    { k: "clicks", name: "Tagged clicks", hint: "How many times links with your tags were clicked", na: true },
    { k: "dms", name: "DMs with a tagged link", hint: "From the link log; you can correct it" },
    { k: "words", name: "Comment words received", hint: "Comments with the comment word, not counting yours" },
    { k: "orders", name: "Tagged orders", hint: "Only orders with your tag, from the source Yossi gives", na: true },
  ];
  function weekKeyOf(d) { return iso(weekStart(d)); }
  function defaultWeek() { return weekKeyOf(addDays(weekStart(new Date()), -7)); } // on Sunday: the week that just ended
  function logDms(weekKey) {
    const a = parseDay(weekKey), b = addDays(a, 7);
    return Object.values(D.links.items || {}).filter((x) => x && !x.deleted && x.created_at && new Date(x.created_at) >= a && new Date(x.created_at) < b).reduce((s, x) => s + (Number(x.sent) || 0), 0);
  }
  function salesWeek(weekKey) { // tagged orders from the Sales tab; filled in for the week only when exports cover all 7 days
    const S = salesIn(weekKey, iso(addDays(parseDay(weekKey), 6)));
    return { covered: S.days.length, mine: S.mine.length, auto: S.days.length === 7 ? S.mine.length : null };
  }
  function numbersTab() {
    const wk = ST.numWeek || defaultWeek(), w = (D.numbers.weeks || {})[wk] || {};
    const prevKey = iso(addDays(parseDay(wk), -7)), prev = (D.numbers.weeks || {})[prevKey] || null;
    const draft = ST.numDraft && ST.numDraft.week === wk ? ST.numDraft : (ST.numDraft = { week: wk, ...clone(w) });
    const autoDms = logDms(wk), sw = salesWeek(wk);
    const ro = ST.readOnly ? "disabled" : "";
    const val = (k) => (draft[k] == null ? "" : draft[k]);
    const weeks = Object.keys(D.numbers.weeks || {}).sort().reverse();
    const opts = [];
    for (let i = 0; i < 6; i++) opts.push(iso(addDays(parseDay(defaultWeek()), 7 - i * 7)));
    for (const k of weeks) if (!opts.includes(k)) opts.push(k);
    const label = (k) => `${dmy(parseDay(k))} to ${dmy(addDays(parseDay(k), 6))}`;
    const vs = (k) => { if (!prev || prev[k] == null || draft[k] == null || draft[k + "_na"]) return ""; const d = draft[k] - prev[k]; return `<span class="cx-vs">The week before: ${fmt(prev[k])} (${d > 0 ? "+" : ""}${fmt(d)})</span>`; };
    const rate = (a, b) => (a != null && b ? a / b : null);
    const dms = draft.dms != null ? draft.dms : autoDms;
    const orders = draft.orders != null ? draft.orders : sw.auto;
    const rWords = rate(dms, draft.words), rOrders = draft.orders_na ? null : rate(orders, dms);
    const best = draft.reach ? ((Number(draft.saves) || 0) + (Number(draft.shares) || 0)) / draft.reach : null;
    const pct = (r) => `${(r * 100).toFixed(r < 0.1 ? 1 : 0)}%`;
    const small = (b) => (b != null && b < 30 ? `<span class="lb-note">Small sample: ${fmt(b)}. Hard to conclude anything from it</span>` : "");
    const canSave = !ST.readOnly && String(draft.cannot || "").trim().length >= 10;
    return `<section class="lb-section">
      <div class="lb-section-head"><h2>This week's numbers</h2><span class="lb-meta">Fill in every Sunday, for the week that just ended</span></div>
      <label class="lb-field">Week<select class="lb-select" data-numweek>${opts.map((k) => `<option value="${k}" ${k === wk ? "selected" : ""}>${label(k)}${D.numbers.weeks?.[k]?.saved_at ? " · saved" : ""}</option>`).join("")}</select></label>
      <div class="lb-group cx-nums">
        ${FIELDS.map((f) => `<div class="cx-num">
          <label for="cx-n-${f.k}">${f.name}<small>${f.hint}</small></label>
          <input class="lb-input" id="cx-n-${f.k}" inputmode="numeric" data-num="${f.k}" value="${f.k === "dms" && draft.dms == null ? "" : esc(val(f.k))}" placeholder="${f.k === "dms" ? fmt(autoDms) : f.k === "orders" && sw.auto != null ? fmt(sw.auto) : ""}" ${f.na && draft[f.k + "_na"] ? "disabled" : ""} ${ro}>
          ${f.na ? `<label class="cx-na"><input type="checkbox" data-na="${f.k}" ${draft[f.k + "_na"] ? "checked" : ""} ${ro}> Not available yet</label>` : ""}
          ${f.k === "dms" ? `<span class="cx-vs">In the link log for this week: ${fmt(autoDms)}${draft.dms != null ? " (corrected by hand)" : ""}</span>` : ""}
          ${f.k === "orders" && sw.covered ? `<span class="cx-vs">On the Sales tab for this week: ${fmt(sw.mine)}${sw.covered < 7 ? ` (Yossi's exports cover ${sw.covered} of its 7 days)` : ""}${draft.orders != null ? " (corrected by hand)" : ""}</span>` : ""}
          ${vs(f.k)}
        </div>`).join("")}
        <div class="cx-num"><label for="cx-n-saves">Best post: saves<small>Not counting your own save</small></label><input class="lb-input" id="cx-n-saves" inputmode="numeric" data-num="saves" value="${esc(val("saves"))}" ${ro}></div>
        <div class="cx-num"><label for="cx-n-shares">Best post: shares</label><input class="lb-input" id="cx-n-shares" inputmode="numeric" data-num="shares" value="${esc(val("shares"))}" ${ro}></div>
        <div class="cx-num"><label for="cx-n-reach">Best post: reach<small>How many accounts saw it</small></label><input class="lb-input" id="cx-n-reach" inputmode="numeric" data-num="reach" value="${esc(val("reach"))}" ${ro}></div>
      </div>
      <div class="cx-rates">
        <div class="cx-rate"><span>Comment words that got a DM with a link</span><b>${rWords == null ? "-" : `${fmt(dms)} of ${fmt(draft.words)} (${pct(rWords)})`}</b>${small(draft.words)}</div>
        <div class="cx-rate"><span>DMs with a link that became a tagged order</span><b>${draft.orders_na ? "Not available yet" : rOrders == null ? "-" : `${fmt(orders)} of ${fmt(dms)} (${pct(rOrders)})`}</b>${draft.orders_na ? "" : small(dms)}</div>
        <div class="cx-rate"><span>Best post: saves and shares out of reach</span><b>${best == null ? "-" : pct(best)}</b>${draft.reach ? `<span>${fmt((Number(draft.saves) || 0) + (Number(draft.shares) || 0))} of ${fmt(draft.reach)}</span>` : ""}</div>
      </div>
      <label class="lb-field">What these numbers can't prove<textarea class="lb-textarea" data-num-text="cannot" placeholder="At least one sentence. Without it the week isn't saved" ${ro}>${esc(draft.cannot || "")}</textarea></label>
      <div class="cx-actions"><button type="button" class="lb-btn" data-savenums ${canSave ? "" : "disabled"}>Save the week</button>
        <span class="lb-note">${w.saved_at ? `Saved ${dmy(new Date(w.saved_at))}` : "Not saved yet"}</span></div>
    </section>
    ${weeks.length ? `<section class="lb-section"><div class="lb-section-head"><h2>Earlier weeks</h2></div>
      <div class="lb-table-wrap"><table class="lb-table cx-hist"><thead><tr><th>Week</th><th>Clicks</th><th>DMs</th><th>Words</th><th>Orders</th></tr></thead><tbody>
      ${weeks.map((k) => { const x = D.numbers.weeks[k]; return `<tr><td>${label(k)}</td><td>${x.clicks_na ? "n/a" : fmt(x.clicks)}</td><td>${fmt(x.dms)}</td><td>${fmt(x.words)}</td><td>${x.orders_na ? "n/a" : fmt(x.orders)}</td></tr>`; }).join("")}
      </tbody></table></div></section>` : ""}`;
  }
  function saveNumbers() {
    const d = ST.numDraft; if (!d) return;
    const wk = d.week, out = { saved_at: nowIso() };
    for (const k of ["clicks", "words", "orders", "saves", "shares", "reach"]) out[k] = num(d[k]);
    out.dms = d.dms != null ? num(d.dms) : logDms(wk);
    out.clicks_na = !!d.clicks_na; out.orders_na = !!d.orders_na;
    if (out.orders == null) out.orders = salesWeek(wk).auto;
    if (out.clicks_na) out.clicks = null;
    if (out.orders_na) out.orders = null;
    out.cannot = String(d.cannot || "").trim();
    ST.numDraft = null;
    patch("numbers", { weeks: { [wk]: out } });
    toast("Week saved");
  }

  // ---------- link maker ----------
  const tags = () => ({ medium: "social", ...(D.settings.tags || {}) });
  const slug = (s) => String(s || "").toLowerCase().trim().replace(/[\s_]+/g, "-").replace(/[^a-z0-9-]/g, "").replace(/-+/g, "-").replace(/^-|-$/g, "");
  function lmDest() {
    const v = ST.lm.dest;
    if (v === "home") return { url: C.store_url, campaign: "home", title: "Store home page" };
    if (v === "custom") return { url: ST.lm.url.trim(), campaign: "", title: "Another address" };
    const b = C.books.find((x) => x.topic === v);
    return b ? { url: b.url, campaign: "car-" + b.topic, title: `${b.topic} (book ${b.book})` } : null;
  }
  function buildLink() {
    const dest = lmDest();
    if (!dest || !dest.url) return { err: "Choose where the link goes" };
    let u;
    try { u = new URL(dest.url); } catch { return { err: "That address isn't valid. Paste a full address starting with https://" }; }
    if (!/^https?:$/.test(u.protocol)) return { err: "Only http or https addresses" };
    const campaign = slug(ST.lm.campaign) || dest.campaign || "general";
    const content = ST.lm.place === "bio" ? "bio" : `${ST.lm.place}-${ST.lm.date.replace(/-/g, "")}`;
    u.searchParams.set("utm_source", ST.lm.source);
    u.searchParams.set("utm_medium", slug(tags().medium) || "social");
    u.searchParams.set("utm_campaign", campaign);
    u.searchParams.set("utm_content", content);
    if (slug(ST.lm.term)) u.searchParams.set("utm_term", slug(ST.lm.term)); else u.searchParams.delete("utm_term");
    return { url: u.toString(), dest, campaign, content };
  }
  function linksTab() {
    const r = buildLink(), t = tags(), chosen = !!(D.settings.tags || {}).chosen_at;
    const ro = ST.readOnly ? "disabled" : "";
    const wk = parseDay(weekKeyOf(new Date()));
    const log = Object.entries(D.links.items || {}).map(([id, x]) => ({ id, ...x })).filter((x) => !x.deleted && x.created_at && new Date(x.created_at) >= wk).sort((a, b) => (a.created_at < b.created_at ? 1 : -1));
    const seg = (name, list, cur) => `<div class="lb-segmented" role="group">${list.map(([v, label]) => `<button type="button" data-lm="${name}" data-v="${v}" aria-pressed="${cur === v}">${label}</button>`).join("")}</div>`;
    return `<section class="lb-section">
      <div class="lb-section-head"><h2>Link maker</h2><span class="lb-meta">Only orders with your tag count toward your pay</span></div>
      ${chosen ? "" : `<div class="lb-callout"><b>Your tag values aren't chosen yet</b><span>Lesson L02 walks through the choice. Until then the link maker uses ${ltr("utm_medium=social")}.</span></div>`}
      <div class="lb-card cx-lm">
        <label class="lb-field">Where the link goes<select class="lb-select" data-lmdest>
          <option value="" ${!ST.lm.dest ? "selected" : ""}>Choose…</option>
          <optgroup label="A book's page, by topic">${C.books.map((b) => `<option value="${esc(b.topic)}" ${ST.lm.dest === b.topic ? "selected" : ""}>${esc(b.topic)} · book ${esc(b.book)}${b.about ? `: ${esc(b.about)}` : ""}${b.basis === "inferred" ? " (check on the site)" : ""}</option>`).join("")}</optgroup>
          <option value="home" ${ST.lm.dest === "home" ? "selected" : ""}>Store home page</option>
          <option value="custom" ${ST.lm.dest === "custom" ? "selected" : ""}>Another address</option>
        </select></label>
        ${ST.lm.dest === "custom" ? `<label class="lb-field">The address<input class="lb-input" dir="ltr" data-lmtext="url" value="${esc(ST.lm.url)}" placeholder="https://lumebook.com/IL/he/..."></label>` : ""}
        <div class="lb-field">Where the link will appear${seg("place", PLACES, ST.lm.place)}</div>
        <div class="lb-field">Which network${seg("source", SOURCES, ST.lm.source)}</div>
        ${ST.lm.place === "bio" ? "" : `<label class="lb-field">Date<input class="lb-input" type="date" data-lmtext="date" value="${esc(ST.lm.date)}"></label>`}
        <details class="lb-disclosure is-quiet"><summary><span class="lb-sum">More options<small>campaign, test</small></span></summary><div class="lb-disclosure-body">
          <label class="lb-field">Campaign (utm_campaign)<input class="lb-input" dir="ltr" data-lmtext="campaign" value="${esc(ST.lm.campaign)}" placeholder="${esc((lmDest() || {}).campaign || "general")}"></label>
          <label class="lb-field">Test (utm_term), only when you compare two versions<input class="lb-input" dir="ltr" data-lmtext="term" value="${esc(ST.lm.term)}"></label>
        </div></details>
        <div class="cx-out">
          ${r.err ? `<span class="lb-note">${esc(r.err)}</span>` : `<input class="lb-input" id="cx-link" readonly value="${esc(r.url)}" aria-label="The tagged link">
          <div class="lb-row"><button type="button" class="lb-btn" data-copy ${ro}>Copy and log</button><a class="lb-btn secondary sm" href="${esc(r.url)}" target="_blank" rel="noopener">Open and check</a></div>
          <span class="lb-note">After it opens, check that the address bar still ends with ${ltr("utm_content=" + r.content)}</span>`}
        </div>
      </div>
    </section>
    <section class="lb-section">
      <div class="lb-section-head"><h2>This week's link log</h2><span class="lb-meta">How many DMs went out with each link</span></div>
      ${log.length ? `<div class="lb-group">${log.map((x) => `<div class="cx-log"><div><b>${esc(x.title || "")}</b> <span class="lb-note">${esc((PLACES.find((p) => p[0] === x.place) || [, ""])[1])} · ${dmy(new Date(x.created_at))}</span><div class="cx-url">${esc(x.url)}</div></div>
        <div class="cx-count"><button type="button" class="lb-btn secondary icon sm" data-sent="${esc(x.id)}" data-d="-1" aria-label="One fewer" ${ro}>−</button><b>${fmt(Number(x.sent) || 0)}</b><button type="button" class="lb-btn secondary icon sm" data-sent="${esc(x.id)}" data-d="1" aria-label="One more DM sent" ${ro}>+</button></div></div>`).join("")}</div>`
        : `<div class="lb-empty">No links this week yet. A link copied here goes into the log, and then you count how many DMs went out with it.</div>`}
    </section>
    ${utmList(t)}
    <details class="lb-disclosure"><summary><span class="lb-sum">Your tag values<small>${ltr("utm_medium=" + t.medium)}${chosen ? ` · chosen ${dmy(new Date(D.settings.tags.chosen_at))}` : " · default"}</small></span></summary><div class="lb-disclosure-body">
      <p class="lb-note">The values Yossi counts as yours. ${ltr("creator")} is kept for creators and ${ltr("paid-social")} for ads, so don't use them here.</p>
      <label class="lb-field">utm_medium for your posts and DMs<input class="lb-input" dir="ltr" data-tagmedium value="${esc(t.medium)}" ${ro}></label>
      <div><button type="button" class="lb-btn secondary sm" data-savetags ${ro}>Save the values</button></div>
    </div></details>`;
  }
  // The UTM reference list (research/cro-crm/measurement.md §4; docs/utm-list-ig-fb.md). Read-only; the link maker above builds the real links.
  function utmList(t) {
    const med = slug(t.medium) || "social", base = (src) => `utm_source=${src}&utm_medium=${med}&utm_campaign=car-<topic>`;
    const mine = [
      ["Instagram DM", `${base("instagram")}&utm_content=dm-YYYYMMDD`],
      ["Instagram story", `${base("instagram")}&utm_content=story-YYYYMMDD`],
      ["Instagram bio", `${base("instagram")}&utm_content=bio`],
      ["Facebook post", `${base("facebook")}&utm_content=post-YYYYMMDD`],
      ["Testing two versions", "add &utm_term=a or &utm_term=b"],
    ];
    const notMine = [["creator", "Creator links"], ["paid-social", "Meta ads, tagged by Yossi"], ["community", "Parent groups"], ["crm", "The store's own WhatsApp, SMS and email"]];
    return `<details class="lb-disclosure"><summary><span class="lb-sum">UTM list<small>Instagram and Facebook, what counts as yours</small></span></summary><div class="lb-disclosure-body">
      <p class="lb-note">Only ${ltr("utm_medium=" + med)} counts toward your pay. Put <bdi dir="ltr">?</bdi> and then the tags after the page address. Replace <bdi dir="ltr">&lt;topic&gt;</bdi> with the carousel topic and <bdi dir="ltr">YYYYMMDD</bdi> with the day the link goes out. The link maker above does this for you.</p>
      <div class="lb-group">${mine.map(([n, v]) => `<div class="cx-log"><div><b>${esc(n)}</b><div class="cx-url">${esc(v)}</div></div></div>`).join("")}</div>
      <p class="lb-note"><b>Never use these on your links.</b> They belong to others, so your sales would mix with theirs:</p>
      <div class="lb-group">${notMine.map(([v, w]) => `<div class="cx-log"><div><b>${ltr("utm_medium=" + v)}</b> <span class="lb-note">${esc(w)}</span></div></div>`).join("")}</div>
      <p class="lb-note">Before sending: open the link on your phone. The right page opens and the address still ends with ${ltr("?utm_")} (extra bits like ${ltr("fbclid")} are fine). Instagram adds its own tag to a bio link, so put your full tagged link there. Links made before 1 Nov may carry ${ltr("utm_medium=dm")}, ${ltr("bio")} or ${ltr("story")}: that is the old format, not a mistake.</p>
    </div></details>`;
  }
  async function copyLink() {
    const r = buildLink(); if (r.err) return;
    let ok = false;
    try { await navigator.clipboard.writeText(r.url); ok = true; } catch {}
    if (!ok) { const el = document.getElementById("cx-link"); if (el) { el.select(); try { ok = document.execCommand("copy"); } catch {} } }
    const existing = Object.entries(D.links.items || {}).find(([, x]) => x && !x.deleted && x.url === r.url);
    if (!existing) patch("links", { items: { [uid("l")]: { url: r.url, title: r.dest.title, place: ST.lm.place, source: ST.lm.source, campaign: r.campaign, content: r.content, created_at: nowIso(), sent: 0 } } });
    toast(ok ? (existing ? "Copied. The link is already in the log" : "Copied and logged") : "Copying was blocked. Select the link and copy it by hand");
    if (!ok) document.getElementById("cx-link")?.select();
  }

  // ---------- glossary ----------
  function termsTab() {
    const met = C.lessons.filter((l) => l.ready && LP(l.id).opened_at);
    const later = C.lessons.filter((l) => l.ready && !LP(l.id).opened_at).reduce((s, l) => s + l.terms.length, 0);
    const rows = met.flatMap((l) => l.terms.map((t) => ({ ...t, lid: l.id }))).sort((a, b) => a.term.localeCompare(b.term, "en"));
    return `<section class="lb-section"><div class="lb-section-head"><h2>Glossary</h2><span class="lb-meta">Only terms from lessons you have opened</span></div>
      ${rows.length ? `<div class="lb-card"><dl class="cx-terms">${rows.map((t) => `<dt>${esc(t.term)} <span class="lb-note">${esc(t.lid)}</span></dt><dd>${t.def_html}</dd>`).join("")}</dl></div>` : `<div class="lb-empty">No terms yet. Each term shows up here after you meet it in a lesson.</div>`}
      ${later ? `<p class="lb-note">${later} more terms in lessons you haven't opened.</p>` : ""}</section>`;
  }

  // ---------- actions ----------
  function addTask(title, type) {
    title = String(title || "").trim();
    if (!title) { toast("Write the task first"); return; }
    const id = uid("t"), now = nowIso();
    patch("tasks", { items: { [id]: { id, title: title.slice(0, 200), type: TYPES[type] ? type : "other", done: false, created_at: now, updated_at: now } } });
    toast(`Task added: ${(TYPES[type] || TYPES.other).name}`);
    return id;
  }
  const setTask = (id, p) => patch("tasks", { items: { [id]: { ...p, updated_at: nowIso() } } });
  let toastT = null;
  function toast(msg) {
    let el = document.getElementById("cx-toast");
    if (!el) { el = document.createElement("div"); el.id = "cx-toast"; el.className = "lb-toast"; el.dir = "ltr"; el.lang = "en"; el.setAttribute("role", "status"); document.body.appendChild(el); }
    el.textContent = msg; el.hidden = false;
    clearTimeout(toastT); toastT = setTimeout(() => { el.hidden = true; }, 2600);
  }

  function onClick(e) {
    const b = e.target.closest("button, a[data-goto]");
    if (!b) return;
    const ds = b.dataset;
    if (ds.tab) { if (ds.tab === "course" && ST.tab === "course") { goHome(); return; } ST.tab = ds.tab; try { localStorage.setItem(KEY + ":tab", ds.tab); } catch {} render(); return; }
    if (b.hasAttribute("data-home")) { goHome(); return; }
    if (ds.newtype) { ST.newType = ST.newType === ds.newtype ? "" : ds.newtype; render(); document.getElementById("cx-new")?.focus(); return; }
    if (ds.template) { addTask(ds.title, ds.template); return; }
    if (ds.task) { openDrawer({ kind: "task", id: ds.task }); return; }
    if (b.hasAttribute("data-close")) { closeDrawer(); return; }
    if (ds.lesson) { openLesson(ds.lesson, ds.from || null); return; }
    if (ds.project && b.tagName === "BUTTON") { ST.tab = "course"; ST.project = ds.project; ST.lesson = null; ST.toTop = true; try { localStorage.removeItem(KEY + ":lesson"); } catch {} render(); return; }
    if (ds.toggle) { const t = D.tasks.items[ds.toggle]; if (t) { setTask(ds.toggle, { done: !t.done, done_at: t.done ? null : nowIso() }); if (!t.done) closeDrawer(); } return; }
    if (ds.del) { if (confirm("Delete this task?")) { setTask(ds.del, { deleted: true }); closeDrawer(); } return; }
    if (ds.compare) { setTask(ds.compare, { compared: true }); return; }
    if (ds.goto) { ST.tab = ds.goto; closeDrawer(); render(); return; }
    if (ds.peek) { if (confirm("Peeking is recorded with your submission. Peek?")) { ST.quiz[ds.peek].peek = true; render(); } return; }
    if (ds.commit) { commit(ds.commit); return; }
    if (ds.grade) { const last = lastTry(LP(ds.grade)); if (last) gradeLesson(ds.grade, last.n); return; }
    if (ds.stop) { ST.grading[ds.stop]?.abort(); return; }
    if (ds.self) { selfGrade(ds.lid, ds.self === "1"); return; }
    if (ds.retry) { ST.quiz[ds.retry] = { answers: {}, peek: false, fresh: true }; render(); return; }
    if (ds.handin) { handIn(ds.handin); return; }
    if (ds.recheck) { gradeProject(ds.recheck, count(PP(ds.recheck).checks)); return; }
    if (ds.lm) { ST.lm[ds.lm] = ds.v; render(); return; }
    if (b.hasAttribute("data-copy")) { copyLink(); return; }
    if (ds.sent) { const x = D.links.items[ds.sent]; if (x) patch("links", { items: { [ds.sent]: { sent: Math.max(0, (Number(x.sent) || 0) + Number(ds.d)) } } }); return; }
    if (b.hasAttribute("data-savetags")) { const el = document.querySelector("[data-tagmedium]"); const m = slug(el?.value); if (!m) { toast("An empty value isn't saved"); return; } if (m === "creator" || m === "paid-social") { toast(`${m} is kept for creators and ads`); return; } patch("settings", { tags: { medium: m, chosen_at: nowIso() } }); toast("Values saved"); return; }
    if (b.hasAttribute("data-savenums")) { saveNumbers(); return; }
    if (ds.speriod) { ST.salesPeriod = ds.speriod; render(); return; }
    if (b.hasAttribute("data-pickfile")) { ROOT.querySelector("[data-impfile]")?.click(); return; }
    if (b.hasAttribute("data-impadd")) { addImport(); return; }
    if (b.hasAttribute("data-impclear")) { ST.imp = null; render(); return; }
    if (ds.impdel) { if (confirm("Remove this export? Its orders and days leave the counts.")) removeImport(ds.impdel); return; }
  }
  function onChange(e) {
    const el = e.target, ds = el.dataset;
    if (ds.done) { const t = D.tasks.items[ds.done]; if (t) setTask(ds.done, { done: el.checked, done_at: el.checked ? nowIso() : null }); return; }
    if (ds.step !== undefined && ds.tid) { setTask(ds.tid, { checked: { [ds.step]: el.checked } }); return; }
    if (ds.project && el.type === "checkbox") { patch("progress", { projects: { [ds.project]: { done_at: el.checked ? nowIso() : null } } }); return; }
    if (ds.typeOf) { setTask(ds.typeOf, { type: el.value }); return; }
    if (ds.choice) { const q = ST.quiz[ds.choice] || (ST.quiz[ds.choice] = { answers: {}, peek: false }); q.answers[ds.q] = Number(el.value); render(); return; }
    if (ds.numweek !== undefined && el.matches("[data-numweek]")) { ST.numWeek = el.value; ST.numDraft = null; el.blur(); render(); return; }
    if (ds.na) { ST.numDraft[ds.na + "_na"] = el.checked; render(); return; }
    if (el.matches("[data-lmdest]")) { ST.lm.dest = el.value; ST.lm.campaign = ""; el.blur(); render(); return; }
    if (ds.improle && ST.imp) { ST.imp.map[ds.improle] = Number(el.value); if (ds.improle === "status") fillStatus(ST.imp); el.blur(); render(); return; }
    if (ds.imppaid !== undefined && ST.imp) { const s = ST.imp.statuses[Number(ds.imppaid)]; if (s) ST.imp.paid[s[0]] = el.checked; render(); return; }
    if (el.matches("[data-impminor]") && ST.imp) { ST.imp.minor = el.checked; render(); return; }
    if (el.matches("[data-impfile]") && el.files && el.files[0]) { const f = el.files[0]; f.text().then((t) => loadImport(t, f.name), () => toast("That file couldn't be read")); el.value = ""; return; }
  }
  function onInput(e) {
    const el = e.target, ds = el.dataset;
    if (ds.open) { const q = ST.quiz[ds.open] || (ST.quiz[ds.open] = { answers: {}, peek: false }); q.answers[ds.q] = el.value; const btn = ROOT.querySelector("[data-commit]"); if (btn) { const l = LESSONS[ds.open]; btn.disabled = ST.readOnly || !l.quiz.every((x) => { const a = q.answers[x.n]; return x.kind === "open" ? String(a || "").trim() : a !== undefined && a !== null; }); } return; }
    if (ds.hand) { ST.hand[ds.hand] = el.value; const btn = ROOT.querySelector("[data-handin]"); if (btn) btn.disabled = ST.readOnly || !el.value.trim() || !!ST.grading[`${ds.hand}#${count(PP(ds.hand).checks)}`]; return; }
    if (ds.num) { ST.numDraft[ds.num] = el.value === "" ? null : num(el.value); return; }
    if (ds.numText) { ST.numDraft[ds.numText] = el.value; const btn = document.querySelector("[data-savenums]"); if (btn) btn.disabled = ST.readOnly || el.value.trim().length < 10; return; }
    if (ds.lmtext) { ST.lm[ds.lmtext] = el.value; return; }
    if (el.matches("[data-imptext]")) { if (/^insertFrom(Paste|Drop)/.test(e.inputType || "")) { el.blur(); loadImport(el.value); } return; } // a paste shows the count at once
    if (ds.own) { const btn = drawerEl?.querySelector("[data-compare]"); if (btn) btn.disabled = !el.value.trim(); return; }
  }
  function onFocusOut(e) {
    const el = e.target, ds = el.dataset;
    if (ds.titleOf) { const v = el.value.trim(); const t = D.tasks.items[ds.titleOf]; if (v && t && v !== t.title) setTask(ds.titleOf, { title: v.slice(0, 200) }); }
    if (ds.noteOf !== undefined && el.matches("[data-note-of]")) { const t = D.tasks.items[ds.noteOf]; if (t && el.value !== (t.note || "")) setTask(ds.noteOf, { note: el.value.slice(0, 4000) }); }
    if (ds.own) { const t = D.tasks.items[ds.own]; if (t && el.value !== (t.own_steps || "")) setTask(ds.own, { own_steps: el.value.slice(0, 4000) }); }
    if (ds.lmtext || ds.num) { setTimeout(render, 0); }
    if (el.matches("[data-imptext]")) { const v = el.value; setTimeout(() => loadImport(v), 0); return; }
    if (ST.dirty) setTimeout(() => { if (ST.dirty) render(); }, 0);
  }
  function onSubmit(e) {
    if (e.target.id !== "cx-add-form") return;
    e.preventDefault();
    const input = document.getElementById("cx-new");
    const id = addTask(input.value, ST.newType || "other");
    if (id) { input.value = ""; input.blur(); ST.newType = ""; render(); }
  }
  ROOT.addEventListener("click", onClick);
  ROOT.addEventListener("change", onChange);
  ROOT.addEventListener("input", onInput);
  ROOT.addEventListener("focusout", onFocusOut);
  ROOT.addEventListener("submit", onSubmit);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && ST.drawer) closeDrawer(); });
  document.addEventListener("lb:route", (e) => { if (e.detail?.view !== "course" && ST.drawer) closeDrawer(); });

  window.LBCourse = { state: ST, data: D, render }; // for testing from the console
  render();
  boot();
})();
