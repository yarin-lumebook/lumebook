"""november-calendar.html: the November reel calendar as a page (Yarin, 04 Nov 2026: "html").

Built from reels.json by `reels.py build` (which calls page()). Never edit the HTML; edit reels.json and build.
Design system: shared/design (design.head(), lb- components, white only). Series colours come from the
"reel-series" set in shared/design/categories.json; status has its own chips, never a category hue.

Editing (Yarin, 04 Nov 2026: "just make the text editable and auto save with full text editor options"): every text on
the page carries data-ek (a stable key such as r1-2__vo__3) and is contenteditable, with a formatting toolbar. Edits save
by themselves, on claude.ai to the artifact's db (collection "edits", one document per key: html, text, base, at); on the
project server to local-edits.json next to this file (through /api/reels-hub/*, since 06 Nov 2026; what the browser had
kept in localStorage moves there on the first visit); anywhere else (Vercel) only in that browser. An edit is shown only
while its base still equals the built text, so a later change to reels.json is never hidden under an old edit.
`reels.py merge FILE` copies saved edits back into reels.json (FILE = the "edits" collection read with ArtifactData;
`reels.py merge local` reads local-edits.json instead).
"""
import calendar, html, json, sys
from datetime import date
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "shared" / "design"))
sys.path.insert(0, str(HERE))
import design  # noqa: E402
import reels  # noqa: E402

OUT = HERE / "november-calendar.html"
WEEK = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]   # Israeli week, Sunday first
STATUS = {  # label, chip class
    "posted": ("פורסם", "success"),
    "ready": ("מוכן לפרסום", "success"),
    "needs-edit": ("מחכה לעריכה שלי", "info"),
    "needs-voice": ("מחכה לצילום וקריינות שלך", "warning"),
    "needs-footage": ("מחכה לחומר", "warning"),
    "blocked": ("חסום", "danger"),
    "spare": ("ספייר", ""),
}
VOICE = {"yarin": "הקריינות שלך", "text": "טקסט בלי קול", "trend": "טרנד מוכן"}
e = html.escape



def ddmm(iso, year=True):
    y, m, d = iso.split("-")
    return f"{d} / {m} / {y}" if year else f"{d} / {m}"


def wd(iso):
    return WEEK[(date.fromisoformat(iso).weekday() + 1) % 7]


def series_cls(n):
    return design.cat_class("reel-series", str(n))


def rid(r):
    return "r" + r["id"].replace(".", "-")


def ek(*parts):
    """Editable key: letters, digits, - and _ only, so it is also a valid db document id."""
    return "__".join(str(p) for p in parts).replace(".", "-").replace("/", "-")


def month_grid(rs, carousels):
    by_date = {r["date"]: r for r in rs if r["date"]}
    cal = calendar.Calendar(firstweekday=6)  # Sunday
    cells = [f'<div class="lb-month-dow" aria-hidden="true">{d}</div>' for d in WEEK]
    for day in cal.itermonthdates(2026, 11):
        iso = day.isoformat()
        if day.month != 11:
            cells.append('<div class="lb-day is-out" aria-hidden="true"></div>')
            continue
        r = by_date.get(iso)
        car = carousels.get(iso)
        car_html = f'<span class="car" title="קרוסלה 06:00: {e(car)}">קרוסלה</span>' if car else ""
        if not r:
            cells.append(f'<div class="lb-day is-empty"><span class="lb-day-num">{day.day}</span>{car_html}</div>')
            continue
        lab, cls = STATUS[r["status"]]
        aud_html = '<span class="aud" title="מדבר לסבתות">סבתא</span>' if r.get("audience") == "grandma" else ""
        cells.append(
            f'<a class="lb-day lb-tinted {series_cls(r["series"])}" href="#{rid(r)}" data-k="{rid(r)}" data-series="{r["series"]}" data-aud="{r.get("audience", "parents")}" '
            f'aria-label="{day.day} בנובמבר, ריל {e(r["id"])}, {e(lab)}">'
            f'<span class="lb-day-top"><span class="lb-day-num">{day.day}</span><span class="lb-pid">{e(r["id"])}</span></span>'
            f'<span class="lb-day-text" data-hook-of="{ek(rid(r), "hook")}">{e(r["hook"].replace(chr(10), " "))}</span>'
            f'<span class="lb-day-foot"><span class="st {cls}" title="{e(lab)}"></span>{aud_html}{car_html}<span class="lb-day-tick" title="עשית">✓</span></span></a>')
    return f'<div class="lb-month">{"".join(cells)}</div>'



def ed(tag, key, inner, cls="", attrs=""):
    """An editable element."""
    c = f' class="lb-editable {cls}"' if cls else ' class="lb-editable"'
    return f'<{tag}{c} data-ek="{key}" dir="auto"{attrs}>{inner}</{tag}>'


def card(r, d):
    lab, cls = STATUS[r["status"]]
    s = d["defaults"]
    k = rid(r)
    rows = []
    shot = ed("p", ek(k, "shot"), e(r["shot"])) if r.get("shot") else ""
    if r.get("yarin_films"):
        shot += '<span class="sub">אתה מצלם</span>' + ed("p", ek(k, "films"), e(", ".join(r["yarin_films"])))
    if shot:
        rows.append(("צילום", f'<details class="shot"><summary>הצגה</summary>{shot}</details>'))
    if r.get("vo"):
        lines = r["vo"] + ([s["cta_voice"]] if r["status"] != "posted" else [])
        n = sum(len(x.split()) for x in lines)
        lis = "".join(ed("li", ek(k, "vo", i), e(x)) for i, x in enumerate(r["vo"]))
        if r["status"] != "posted":
            lis += f'<li class="fixed" title="קבוע לכל הרילס">{e(s["cta_voice"])}</li>'
        rows.append((f"קריינות, {n} מילים", f'<ol class="vo">{lis}</ol>'))
    if r["voice"] == "trend":
        lis = f'<li><span data-hook-of="{ek(k, "hook")}">{e(r["hook"].replace(chr(10), " "))}</span></li>'
        if r["status"] != "posted":
            lis += f'<li class="fixed" title="קבוע לכל הרילס">{e(s["cta_screen"].replace(chr(10), " "))}</li>'
        rows.append((f"טקסט על המסך, טרנד {r['clip_seconds']:g} שניות", f'<ol class="vo">{lis}</ol>'))
    if r.get("cards"):
        rows.append(("כרטיסיות על המסך", '<ol class="vo">' + "".join(ed("li", ek(k, "cards", i), e(x)) for i, x in enumerate(r["cards"])) + "</ol>"))
    cap = reels.caption_of(r, d)
    rows.append(("כיתוב לאינסטגרם",
                 f'<div class="cap">{ed("div", ek(k, "caption"), e(cap), "capbox", f" id=cap-{k}")}'
                 f'<button class="lb-btn copy" type="button" data-copy="cap-{k}">העתקה</button></div>'))
    body = "".join(f'<div class="row"><dt>{t}</dt><dd>{v}</dd></div>' for t, v in rows)
    car = s["carousel_days"].get(r["date"]) if r["date"] else None
    car_html = f'<span class="lb-chip outline">באותו יום קרוסלה: {e(car)}</span>' if car else ""
    aud = "סבתות" if r.get("audience") == "grandma" else "הורים"
    aud_html = f'<span class="lb-chip {"accent" if r.get("audience") == "grandma" else ""}" title="למי הריל מדבר">מדבר ל{aud}</span>'
    pg = r.get("page")
    pg_html = (f'<a class="lb-chip tint" target="_blank" rel="noopener" href="https://lumebook.com/IL/he/{e(pg)}" title="הדף שהקישור ב DM פותח">'
               f'{e(d["defaults"].get("pages", {}).get(pg, pg))}</a>') if pg else ""
    when = (f'<span class="wd">{wd(r["date"])}</span><span class="dd">{ddmm(r["date"], False)}</span><span class="tm">{e(s["post_time"])}</span>'
            if r["date"] else '<span class="wd">ספייר</span>')
    sec = reels.seconds(r, d)
    return f"""
<article class="reel lb-card lb-tinted {series_cls(r['series'])}" id="{k}" data-series="{r['series']}" data-status="{r['status']}">
  <header class="reel-head">
    <div class="when">{when}</div>
    <button type="button" class="lb-chip check" data-made="{k}" data-def="{1 if r['status'] == 'posted' else 0}" aria-pressed="false">עשיתי</button>
    <div class="meta">
      <span class="lb-pid">{e(r['id'])}</span>
      <span class="lb-chip cat">{e(design.categories('reel-series')[str(r['series'])]['label'])}</span>
      <span class="lb-chip {cls}">{e(lab)}</span>
      <span class="lb-chip" title="אורך משוער">{sec:g} שניות</span>
      <span class="lb-chip">{VOICE[r['voice']]}</span>
      {aud_html}{pg_html}
      {car_html}
    </div>
  </header>
  {ed("h3", ek(k, "hook"), e(r['hook'].replace(chr(10), ' ')), "hook-big", f' title="{e(r["hook"].replace(chr(10), " "))}"')}
  <dl class="rows">{body}</dl>
</article>"""


TOOLBAR = """
<div class="lb-editbar" id="tb" role="toolbar" aria-label="עיצוב טקסט">
  <div class="lb-editbar-in">
    <button type="button" data-cmd="undo" title="ביטול (⌘Z)">↶</button>
    <button type="button" data-cmd="redo" title="ביצוע מחדש (⇧⌘Z)">↷</button>
    <span class="sep"></span>
    <select id="tb-block" title="סגנון">
      <option value="">סגנון</option><option value="p">פסקה</option><option value="h2">כותרת גדולה</option>
      <option value="h3">כותרת</option><option value="h4">כותרת קטנה</option><option value="blockquote">ציטוט</option>
    </select>
    <select id="tb-font" title="גופן">
      <option value="">גופן</option><option value="Heebo">ראשי</option><option value="Assistant">משני</option>
      <option value="Arial">אריאל</option><option value="ui-monospace">מונו</option>
    </select>
    <select id="tb-size" title="גודל">
      <option value="">גודל</option><option value="1">קטן מאוד</option><option value="2">קטן</option><option value="3">רגיל</option>
      <option value="4">בינוני</option><option value="5">גדול</option><option value="6">גדול מאוד</option><option value="7">ענק</option>
    </select>
    <span class="sep"></span>
    <button type="button" data-cmd="bold" title="מודגש (⌘B)"><b>B</b></button>
    <button type="button" data-cmd="italic" title="נטוי (⌘I)"><i>I</i></button>
    <button type="button" data-cmd="underline" title="קו תחתון (⌘U)"><u>U</u></button>
    <button type="button" data-cmd="strikeThrough" title="קו חוצה"><s>S</s></button>
    <label class="clr" title="צבע טקסט"><span class="a">A</span><input type="color" id="tb-color" value="#5b2bd6"></label>
    <label class="clr hl" title="הדגשת רקע"><span class="a">▇</span><input type="color" id="tb-hilite" value="#fbebc9"></label>
    <span class="sep"></span>
    <button type="button" data-cmd="justifyRight" title="יישור לימין">⇥</button>
    <button type="button" data-cmd="justifyCenter" title="מרכוז">≡</button>
    <button type="button" data-cmd="justifyLeft" title="יישור לשמאל">⇤</button>
    <button type="button" data-cmd="justifyFull" title="יישור לשני הצדדים">☰</button>
    <span class="sep"></span>
    <button type="button" data-cmd="insertUnorderedList" title="רשימת תבליטים">•</button>
    <button type="button" data-cmd="insertOrderedList" title="רשימה ממוספרת">1.</button>
    <button type="button" data-cmd="outdent" title="הקטנת הזחה">⇠</button>
    <button type="button" data-cmd="indent" title="הגדלת הזחה">⇢</button>
    <span class="sep"></span>
    <button type="button" data-cmd="link" title="קישור (⌘K)">🔗</button>
    <button type="button" data-cmd="unlink" title="הסרת קישור">⛓</button>
    <button type="button" data-cmd="superscript" title="כתב עילי">x²</button>
    <button type="button" data-cmd="subscript" title="כתב תחתי">x₂</button>
    <button type="button" data-cmd="dir" title="כיוון כתיבה ימין או שמאל">⇄</button>
    <button type="button" data-cmd="removeFormat" title="ניקוי עיצוב">⌫</button>
    <input id="tb-link" type="url" dir="ltr" hidden aria-label="כתובת הקישור, אנטר לאישור">
    <span class="hint">לוחצים על טקסט כדי לערוך</span>
  </div>
</div>"""

SCRIPT = r"""
<script>
(function () {
  "use strict";
  var KEY_F = "lb-reels-nov-filter", KEY_L = "lb-reels-nov-edits";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* filter */
  var btns = $$(".filters [data-f]");
  function applyFilter(f) {
    btns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.f === f)); });
    $$(".lb-day[data-series]").forEach(function (el) {
      var hit = f === "all" || (f === "grandma" ? el.dataset.aud === "grandma" : el.dataset.series === f);
      el.classList.toggle("is-dim", !hit);
    });
    try { localStorage.setItem(KEY_F, f); } catch (x) {}
  }
  btns.forEach(function (b) { b.addEventListener("click", function () { applyFilter(b.dataset.f); }); });
  var savedF = "all";
  try { savedF = localStorage.getItem(KEY_F) || "all"; } catch (x) {}
  if ($('.filters [data-f="' + savedF + '"]')) applyFilter(savedF);

  /* copy */
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var el = document.getElementById(b.dataset.copy);
      var done = function () { b.textContent = "הועתק"; setTimeout(function () { b.textContent = "העתקה"; }, 1600); };
      var select = function () { var r = document.createRange(); r.selectNodeContents(el); var s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = "מסומן, להעתיק"; };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(el.innerText).then(done, select); else select();
    });
  });

  /* sanitizer: keep formatting, drop scripts, handlers and unknown tags */
  var OK = { B:1, STRONG:1, I:1, EM:1, U:1, S:1, STRIKE:1, SPAN:1, FONT:1, A:1, UL:1, OL:1, LI:1, BR:1, DIV:1, P:1, H2:1, H3:1, H4:1, BLOCKQUOTE:1, SUB:1, SUP:1, MARK:1 };
  var ATTR = { style:1, href:1, color:1, size:1, face:1, dir:1 };
  function clean(html) {
    var t = document.createElement("template"); t.innerHTML = html;
    (function walk(node) {
      $$("*", node).reverse().forEach(function (el) {
        if (!OK[el.tagName]) {
          if (/^(SCRIPT|STYLE|IFRAME|OBJECT|EMBED|TEMPLATE|META|LINK)$/.test(el.tagName)) { el.remove(); return; }
          while (el.firstChild) el.parentNode.insertBefore(el.firstChild, el);
          el.remove(); return;
        }
        Array.prototype.slice.call(el.attributes).forEach(function (a) {
          var n = a.name.toLowerCase();
          if (!ATTR[n]) el.removeAttribute(a.name);
          else if (n === "href" && !/^(https?:|mailto:)/i.test(a.value.trim())) el.removeAttribute(a.name);
          else if (n === "style" && /url\(|expression|javascript:/i.test(a.value)) el.removeAttribute(a.name);
        });
        if (el.tagName === "A") { el.setAttribute("target", "_blank"); el.setAttribute("rel", "noopener"); }
      });
    })(t.content);
    return t.innerHTML;
  }

  /* editable fields */
  var fields = {};   // key -> {el, base, baseHtml}
  $$("[data-ek]").forEach(function (el) {
    fields[el.dataset.ek] = { el: el, base: el.innerText.trim(), baseHtml: el.innerHTML };
    el.setAttribute("contenteditable", "true");
    el.setAttribute("spellcheck", "true");
  });
  function syncHook(key) {
    var f = fields[key]; if (!f) return;
    $$('[data-hook-of="' + key + '"]').forEach(function (s) { s.textContent = f.el.innerText.replace(/\s*\n\s*/g, " ").trim(); });
  }

  /* status pill */
  var pill = $("#save-state");
  function state(t, kind) { pill.textContent = t; pill.className = "lb-chip " + (kind || ""); }

  /* store: artifact db when the viewer serves it, else this browser */
  var store = null, local = {}, readOnly = false;
  try { local = JSON.parse(localStorage.getItem(KEY_L) || "{}"); } catch (x) { local = {}; }
  function applyDoc(key, doc) {
    var f = fields[key]; if (!f || !doc || typeof doc.html !== "string") return;
    if (document.activeElement === f.el) return;
    var text = typeof doc.text === "string" ? doc.text.trim() : "";
    if (doc.base !== f.base && text !== f.base) { f.el.classList.add("is-stale"); f.el.title = "הטקסט השתנה במקור אחרי העריכה, מוצג הטקסט החדש"; return; }
    f.el.innerHTML = clean(doc.html);
    f.el.classList.add("is-edited");
    syncHook(key);
  }
  Object.keys(local).forEach(function (k) { applyDoc(k, local[k]); });

  var timers = {}, pending = 0;
  function save(key) {
    var f = fields[key]; if (!f || readOnly) return;
    var doc = { key: key, html: clean(f.el.innerHTML), text: f.el.innerText.trim(), base: f.base, at: new Date().toISOString() };
    pending++; state("שומר...", "info");
    var done = function () { pending--; if (!pending) state(store ? "נשמר" : "נשמר בדפדפן הזה", "success"); f.el.classList.add("is-edited"); };
    var fail = function (err) {
      pending--;
      if (err && err.code === "invalid_argument") { readOnly = true; lockAll(); state("קריאה בלבד", ""); return; }
      state("לא נשמר, אנסה שוב", "danger"); setTimeout(function () { save(key); }, 5000);
    };
    if (store) store.doc(key).set(doc).then(done, fail);
    else { try { local[key] = doc; localStorage.setItem(KEY_L, JSON.stringify(local)); done(); } catch (x) { fail(x); } }
  }
  function lockAll() { Object.keys(fields).forEach(function (k) { fields[k].el.setAttribute("contenteditable", "false"); }); $("#tb").hidden = true; }
  document.addEventListener("input", function (ev) {
    var el = ev.target.closest && ev.target.closest("[data-ek]"); if (!el) return;
    var key = el.dataset.ek; syncHook(key); state("לא נשמר עדיין", "warning");
    clearTimeout(timers[key]); timers[key] = setTimeout(function () { save(key); }, 700);
  });
  document.addEventListener("focusout", function (ev) {
    var el = ev.target.closest && ev.target.closest("[data-ek]"); if (!el || !timers[el.dataset.ek]) return;
    clearTimeout(timers[el.dataset.ek]); timers[el.dataset.ek] = null; save(el.dataset.ek);
  });
  /* paste keeps formatting, cleaned */
  document.addEventListener("paste", function (ev) {
    var el = ev.target.closest && ev.target.closest("[data-ek]"); if (!el) return;
    var h = ev.clipboardData && ev.clipboardData.getData("text/html");
    if (!h) return;
    ev.preventDefault(); document.execCommand("insertHTML", false, clean(h));
  });
  /* links inside edited text still open with ⌘ or Ctrl click */
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("[data-ek] a[href]");
    if (a && (ev.metaKey || ev.ctrlKey)) window.open(a.href, "_blank", "noopener");
  });

  /* Where edits live (6 Nov 2026): on claude.ai the artifact's db (collections edits, made, requests); on the project server
     its own file, research/.../series-2026-11/local-edits.json, through /api/reels-hub/* (reels.py merge local reads it);
     anywhere else (Vercel, a file) only this browser. The server twin below has the few db calls this page makes. */
  var onServer = null;   // promise: true when this page is served by the project server
  function projectServer() {
    if (!onServer) onServer = fetch("/api/board/env").then(function (r) { return r.ok ? r.json() : null; }, function () { return null; })
      .then(function (j) { return !!(j && j.server === "lumebook"); });
    return onServer;
  }
  function serverDb() {
    var HEAD = { "Content-Type": "application/json", "X-LumeBook-Board": "1" };
    return fetch("/api/reels-hub/state").then(function (r) { if (!r.ok) throw new Error("state"); return r.json(); }).then(function (st) {
      var docs = { edits: (st && st.edits) || {}, made: (st && st.made) || {}, requests: (st && st.requests) || {} };
      function put(name, id, doc) {
        return fetch("/api/reels-hub/doc?path=" + encodeURIComponent(name + "/" + id), { method: "PUT", headers: HEAD, body: JSON.stringify(doc) })
          .then(function (r) { if (!r.ok) { var e = new Error("put"); e.code = "unavailable"; throw e; } docs[name][id] = doc; });
      }
      /* what this browser kept before the server did: send edits and ticks the server lacks (or has older), then forget them here */
      var moved = [];
      Object.keys(local).forEach(function (k) {
        var l = local[k], s = docs.edits[k];
        if (l && typeof l.html === "string" && (!s || String(l.at) > String(s.at))) {
          docs.edits[k] = l; moved.push(put("edits", k, l).then(function () { delete local[k]; }));
        } else delete local[k];
      });
      Promise.all(moved).then(function () { try { localStorage.setItem(KEY_L, JSON.stringify(local)); } catch (x) {} }, function () {});
      var ticks = [];
      Object.keys(made).forEach(function (k) {
        if (!docs.made[k]) { var d = { key: k, made: !!made[k], at: new Date().toISOString() }; docs.made[k] = d; ticks.push(put("made", k, d)); }
      });
      Promise.all(ticks).then(function () { try { localStorage.removeItem(KEY_M); } catch (x) {} }, function () {});
      function collection(name) {
        return {
          doc: function (id) { return { set: function (doc) { return put(name, id, doc); } }; },
          add: function (doc) { return put(name, Date.now().toString(36) + Math.random().toString(36).slice(2, 7), doc); },
          onSnapshot: function (cb) {
            var ch = Object.keys(docs[name]).map(function (id) { return { type: "added", doc: { id: id, data: function () { return docs[name][id]; } } }; });
            setTimeout(function () { cb({ docChanges: function () { return ch; } }); }, 0);
          }
        };
      }
      return { collection: collection };
    });
  }
  function useDb(db) {
    store = db.collection("edits");
    madeStore = db.collection("made");
    reqStore = db.collection("requests");
    madeStore.onSnapshot(function (snap) {
      snap.docChanges().forEach(function (c) { if (c.type === "removed") return; var v = c.doc.data(); made[c.doc.id] = !!(v && v.made); paintMade(c.doc.id); });
    }, function () {});
    var timer = setTimeout(function () { state("השמירה לא עונה", "warning"); }, 10000);
    store.onSnapshot(function (snap) {
      clearTimeout(timer);
      snap.docChanges().forEach(function (c) { if (c.type !== "removed") applyDoc(c.doc.id, c.doc.data()); });
      if (!pending) state("נשמר", "success");
    }, function () { clearTimeout(timer); state("השמירה לא זמינה", "danger"); });
  }
  if (window.claude && claude.use) {
    claude.use("db").then(function (db) {
      if (!db) { state("נשמר בדפדפן הזה", ""); return; }
      useDb(db);
      return claude.use("user").then(function (u) {
        if (!u) return;
        return u.can("data.write").then(function (w) { if (w === false) { readOnly = true; lockAll(); state("קריאה בלבד", ""); } });
      });
    }, function () { state("נשמר בדפדפן הזה", ""); });
  } else {
    projectServer().then(function (ok) { return ok ? serverDb().then(useDb) : null; })
      .then(function () { if (!store) state("נשמר בדפדפן הזה", ""); }, function () { state("נשמר בדפדפן הזה", ""); });
  }

  /* popup: a day opens its reel */
  var dlg = $("#dlg"), dbody = $("#dlg-body"), holder = $("#cards"), cur = null;
  function flush() { Object.keys(timers).forEach(function (k) { if (timers[k]) { clearTimeout(timers[k]); timers[k] = null; save(k); } }); }
  function openReel(id) {
    var a = document.getElementById(id); if (!a || !a.classList.contains("reel")) return;
    flush(); if (cur) holder.appendChild(cur);
    cur = a; dbody.appendChild(a);
    if (!dlg.open) dlg.showModal();
    dlg.scrollTop = 0; $("#dlg-x").focus();
    try { history.replaceState(null, "", "#" + id); } catch (x) {}
  }
  dlg.addEventListener("close", function () {
    if (dlg.open) return;  /* a late close event after the popup was opened again */
    flush(); if (!cur) return;
    var c = $('.lb-day[data-k="' + cur.id + '"]'); holder.appendChild(cur); cur = null;
    try { history.replaceState(null, "", location.pathname + location.search); } catch (x) {}
    if (c) c.focus();
  });
  $("#dlg-x").addEventListener("click", function () { dlg.close(); });
  dlg.addEventListener("click", function (ev) { if (ev.target === dlg) dlg.close(); });
  $$("a.lb-day[data-k]").forEach(function (c) { c.addEventListener("click", function (ev) { ev.preventDefault(); openReel(c.dataset.k); }); });
  if (location.hash.length > 1) openReel(decodeURIComponent(location.hash.slice(1)));

  /* "עשיתי": tick the reels you made */
  var KEY_M = "lb-reels-nov-made", made = {}, madeStore = null;
  try { made = JSON.parse(localStorage.getItem(KEY_M) || "{}"); } catch (x) { made = {}; }
  function isMade(k) { if (k in made) return !!made[k]; var b = $('[data-made="' + k + '"]'); return !!(b && b.dataset.def === "1"); }
  function paintMade(k) {
    var on = isMade(k);
    $$('[data-made="' + k + '"]').forEach(function (b) { b.setAttribute("aria-pressed", String(on)); });
    var c = $('.lb-day[data-k="' + k + '"]'); if (c) c.classList.toggle("is-done", on);
  }
  $$("[data-made]").forEach(function (b) {
    paintMade(b.dataset.made);
    b.addEventListener("click", function () {
      if (readOnly) return;
      var k = b.dataset.made; made[k] = !isMade(k); paintMade(k);
      if (madeStore) {
        pending++; state("שומר...", "info");
        madeStore.doc(k).set({ key: k, made: made[k], at: new Date().toISOString() }).then(
          function () { pending--; if (!pending) state("נשמר", "success"); },
          function () { pending--; state("לא נשמר", "danger"); });
      } else { try { localStorage.setItem(KEY_M, JSON.stringify(made)); state("נשמר בדפדפן הזה", "success"); } catch (x) {} }
    });
  });

  /* comment box: Claude rewrites the open reel from a comment */
  var CFG = {}; try { CFG = JSON.parse($("#ask-cfg").textContent); } catch (x) {}
  var ask = $("#ask"), askT = $("#ask-t"), askGo = $("#ask-go"), askMsg = $("#ask-msg"), sampleFn = null, askCtl = null, reqStore = null;
  function msg(t, err) { askMsg.textContent = t; askMsg.classList.toggle("is-error", !!err); }
  function label(key) {
    var m = key.split("__"), f = m[1], i = m[2] ? Number(m[2]) + 1 : 0;
    return { hook: "כותרת (על המסך ובראש הכרטיס)", vo: "קריינות, שורה " + i, cards: "כרטיסייה על המסך " + i, caption: "כיתוב לאינסטגרם",
             shot: "הוראות צילום (פנימי, לירין)", films: "מה ירין מצלם (פנימי, רשימה מופרדת בפסיקים)" }[f] || f;
  }
  function tidy(t) {
    return String(t).replace(/\s*[\u2014\u2013]\s*/g, ", ").replace(/\u05BE/g, " ").replace(/(\S)\s+-\s+(\S)/g, "$1, $2")
      .replace(/;/g, ",").replace(/לומיבוק/g, "לומבוק").replace(/,\s*,/g, ",").trim();
  }
  function prompt(reel, comment) {
    var flds = {};
    $$("[data-ek]", reel).forEach(function (el) { flds[el.dataset.ek] = { role: label(el.dataset.ek), text: el.innerText.trim() }; });
    return [
      "אתה עורך את התסריט של ריל אחד לאינסטגרם של לומבוק (ספרי ילדים מותאמים אישית, ישראל). ירין, מנהל הסושיאל, כתב הערה. שנה את הטקסטים לפי ההערה בלבד.",
      "",
      "חוקים לכל טקסט שהורים רואים או שומעים (כותרת, קריינות, כרטיסיות, כיתוב):",
      "- עברית ישראלית יומיומית, כמו שירין מדבר עם הורה אחר. משפטים קצרים, פעלים לפני שמות עצם, בלי שפה של מותג או של מטפל.",
      "- בלי מקף מכל סוג (גם לא מקף עברי), בלי קו מפריד ארוך, בלי נקודה ופסיק. פסיק, נקודה, סימן שאלה וקריאה ומרכאות מותרים.",
      "- השם לומבוק בלבד, אף פעם לא לומיבוק. אף פעם לא להזכיר בינה מלאכותית. אף פעם לא \"קוד הנחה\" או \"קוד אישי\".",
      "- בלי עובדות חדשות. אף פעם לא להזכיר מחיר, סכום כסף, הנחה או מבצע. זמנים ותכונות רק מהעובדות כאן: " + CFG.facts + ". המבצע: " + CFG.offer + ".",
      "- כותרת: עד 8 מילים. קריינות: כל השורות יחד בין " + CFG.vo_min + " ל " + CFG.vo_max + " מילים, שורה אחת לכל מחשבה, עד 12 מילים בשורה.",
      "- שורת הסיום של הקריינות קבועה ומתווספת לבד: \"" + CFG.cta_voice + "\". לא לכתוב אותה בשורות.",
      "- הכיתוב מסתיים תמיד בשורה הזאת, מילה במילה: " + CFG.cta_caption,
      "- אם בסוף הכיתוב יש הסתייגות רפואית, להשאיר אותה בדיוק כמו שהיא.",
      "- הוראות הצילום ורשימת הצילום הן הערות פנימיות לירין, בעברית פשוטה, בגוף שני.",
      "",
      "אפשר לשנות רק את המפתחות שכבר קיימים. אי אפשר להוסיף או למחוק שורות. כל ערך חייב להיות לא ריק. לשנות רק מה שההערה מבקשת, ומה שחייב להשתנות בעקבותיה כדי שהריל יישאר עקבי.",
      "",
      "הריל עכשיו (מפתח, תפקיד, טקסט):",
      JSON.stringify(flds, null, 1),
      "",
      "ההערה של ירין:",
      comment,
      "",
      "תחזיר רק JSON בצורה הזאת, בלי שום טקסט אחר:",
      "{\"changes\": {\"<מפתח>\": \"<הטקסט החדש>\"}, \"summary\": \"משפט קצר בעברית: מה שינית\"}",
      "אם אי אפשר לעשות את מה שההערה מבקשת בלי לשבור את החוקים, תחזיר changes ריק ותסביר ב summary."
    ].join("\n");
  }
  function ideaPrompt(reel) {
    var flds = {};
    $$("[data-ek]", reel).forEach(function (el) { flds[el.dataset.ek] = { role: label(el.dataset.ek), text: el.innerText.trim() }; });
    var chip = $(".reel-head .lb-chip.cat", reel), when = $(".when", reel);
    var others = $$("article.reel").filter(function (a) { return a !== reel; })
      .map(function (a) { var h = $(".hook-big", a); return h ? h.innerText.replace(/\s+/g, " ").trim() : ""; }).filter(Boolean);
    return [
      "אתה כותב ריל חדש לאינסטגרם של לומבוק (ספרי ילדים מותאמים אישית, ישראל). ירין, מנהל הסושיאל, לא אהב את הרעיון של הריל הזה ורוצה רעיון אחר לגמרי לאותו יום.",
      "",
      "הסדרה של הריל: " + (chip ? chip.innerText.trim() : "") + ". היום: " + (when ? when.innerText.replace(/\s+/g, " ").trim() : "") + ". הרעיון החדש נשאר בסדרה הזאת אבל עם זווית, פתיחה ומבנה אחרים. לא לנסח מחדש את הרעיון הישן.",
      "רעיונות של רילס אחרים בחודש, לא לחזור עליהם: " + others.join(" | "),
      "",
      "חוקים לכל טקסט שהורים רואים או שומעים (כותרת, קריינות, כרטיסיות, כיתוב):",
      "- עברית ישראלית יומיומית, כמו שירין מדבר עם הורה אחר. משפטים קצרים, פעלים לפני שמות עצם, בלי שפה של מותג או של מטפל.",
      "- בלי מקף מכל סוג (גם לא מקף עברי), בלי קו מפריד ארוך, בלי נקודה ופסיק. פסיק, נקודה, סימן שאלה וקריאה ומרכאות מותרים.",
      "- השם לומבוק בלבד, אף פעם לא לומיבוק. אף פעם לא להזכיר בינה מלאכותית. אף פעם לא \"קוד הנחה\" או \"קוד אישי\".",
      "- בלי עובדות חדשות. אף פעם לא להזכיר מחיר, סכום כסף, הנחה או מבצע. זמנים ותכונות רק מהעובדות כאן: " + CFG.facts + ". המבצע: " + CFG.offer + ".",
      "- לא לדבר על השפות של הספר ולא על העותק הדיגיטלי: הקהל ישראלי ודובר עברית.",
      "- כותרת: עד 8 מילים, שואלת או מסקרנת, ומתאימה לשנייה הראשונה. קריינות: כל השורות יחד בין " + CFG.vo_min + " ל " + CFG.vo_max + " מילים, שורה אחת לכל מחשבה, עד 12 מילים בשורה. הריל כולו בין 10 ל 30 שניות.",
      "- שורת הסיום של הקריינות קבועה ומתווספת לבד: \"" + CFG.cta_voice + "\". לא לכתוב אותה בשורות.",
      "- הכיתוב מסתיים תמיד בשורה הזאת, מילה במילה: " + CFG.cta_caption,
      "- אם בסוף הכיתוב יש הסתייגות רפואית, להשאיר אותה בדיוק כמו שהיא.",
      "- ירין חייב להופיע בריל: קטע פתיחה שלו למצלמה ו/או הקול שלו בקריינות. בלי שחקנים, בלי ילדים זרים, בלי טרנדים של אפליקציות.",
      "- מה שאפשר לצלם לבד ובזול: ירין מדבר למצלמה, הקלטת מסך של האתר וההזמנה, הספר המודפס, תצוגה מקדימה של ספר, צילום מלמעלה, הקלטה בטלפון.",
      "- הוראות הצילום ורשימת הצילום הן הערות פנימיות לירין, בעברית פשוטה, בגוף שני (\"אתה\"), ו\"אני\" זה Claude. ברשימת הצילום פריטים מופרדים בפסיקים, בלי פסיק בתוך פריט.",
      "",
      "צריך להחזיר ערך חדש לכל אחד מהמפתחות שכאן, ורק להם. אי אפשר להוסיף או למחוק מפתחות, וכל ערך חייב להיות לא ריק:",
      JSON.stringify(flds, null, 1),
      "",
      "תחזיר רק JSON בצורה הזאת, בלי שום טקסט אחר:",
      "{\"changes\": {\"<מפתח>\": \"<הטקסט החדש>\"}, \"summary\": \"משפט קצר בעברית: מה הרעיון החדש\"}"
    ].join("\n");
  }
  var askNew = $("#ask-new");
  function setBusy(on, which) {
    askGo.textContent = on && which !== "new" ? "עצירה" : "שליחה"; askGo.dataset.busy = on ? "1" : ""; askT.disabled = on;
    askNew.textContent = on && which === "new" ? "עצירה" : "רעיון חדש"; askNew.dataset.busy = on ? "1" : "";
    askGo.disabled = on && which === "new"; askNew.disabled = on && which !== "new";
  }
  function apply(reel, changes) {
    var before = {}, keys = [];
    Object.keys(changes || {}).forEach(function (key) {
      var f = fields[key]; if (!f || !reel.contains(f.el)) return;
      var t = tidy(changes[key]); if (!t || t === f.el.innerText.trim()) return;
      before[key] = f.el.innerHTML; f.el.innerText = t;
      if (f.el.classList.contains("hook-big")) f.el.title = t;
      f.el.classList.add("is-changed"); (function (el) { setTimeout(function () { el.classList.remove("is-changed"); }, 2400); })(f.el);
      syncHook(key); save(key); keys.push(key);
    });
    return { before: before, keys: keys };
  }
  function undo(before) {
    Object.keys(before).forEach(function (key) { var f = fields[key]; if (!f) return; f.el.innerHTML = before[key]; syncHook(key); save(key); });
    msg("ביטלתי את השינוי.");
  }
  function run(reel, text, which, comment) {
    askCtl = new AbortController(); setBusy(true, which); msg(which === "new" ? "חושב על רעיון חדש..." : "חושב...");
    sampleFn.json(text, { signal: askCtl.signal, cache: false }).then(function (res) {
      if (cur !== reel) { msg(""); return; }
      var r = apply(reel, res && res.changes), sum = res && res.summary ? String(res.summary) : "";
      if (!r.keys.length) { msg(sum || "לא היה מה לשנות.", !sum); return; }
      if (which !== "new") askT.value = "";
      askMsg.classList.remove("is-error"); askMsg.textContent = (sum ? sum.replace(/[.\s]+$/, "") : "שיניתי " + r.keys.length + " טקסטים") + ".";
      var u = document.createElement("button"); u.type = "button"; u.textContent = "ביטול";
      u.addEventListener("click", function () { undo(r.before); }); askMsg.appendChild(u);
      if (reqStore) reqStore.add({ reel: reel.id, comment: comment, kind: which, summary: sum, keys: r.keys, at: new Date().toISOString() }).catch(function () {});
    }, function (e) {
      var c = e && e.code;
      if (c === "cancelled") { msg(which === "new" ? "עצרתי. הריל נשאר כמו שהיה." : "עצרתי. ההערה נשארה בתיבה."); return; }
      if (c === "not_granted" || c === "sampling_disabled" || c === "not_declared" || c === "capability_disabled" || c === "capability_removed") {
        sampleFn = null; msg("אין אישור לשנות טקסט מכאן. אפשר לאשר בתפריט ההרשאות של העמוד.", true); return; }
      if (c === "rate_limited") { msg("יותר מדי בקשות כרגע. נסה שוב עוד קצת.", true); return; }
      if (c === "not_logged_in") { msg("Claude לא מחובר במחשב הזה. צריך להריץ פעם אחת במסוף: claude auth login", true); return; }
      if (c === "no_cli") { msg("אין פקודת claude במחשב הזה, אז העמוד המקומי לא יכול לשאול את Claude. אפשר לעבוד בגרסה ב claude.ai.", true); return; }
      if (c === "timeout") { msg("Claude לקח יותר מדי זמן. אפשר לשלוח שוב.", true); return; }
      if (c === "invalid_json" || c === "empty_completion") { msg(which === "new" ? "לא הבנתי את התשובה. אפשר ללחוץ שוב." : "לא הבנתי את התשובה. אפשר לנסח את ההערה אחרת ולשלוח שוב.", true); return; }
      if (c === "refused") { msg("את ההערה הזאת לא יכולתי לבצע. נסה לנסח אחרת.", true); return; }
      msg("משהו נכשל בדרך. אפשר לשלוח שוב.", true);
    }).then(function () { setBusy(false); askCtl = null; });
  }
  function canRun(what) {
    if (!sampleFn) {
      msg(what + " עובד רק כשהעמוד פתוח ב claude.ai. ", true);
      if (CFG.artifact && !window.claude) {   /* opened on the project server: link to the claude.ai copy, where the buttons work */
        var a = document.createElement("a"); a.href = CFG.artifact; a.target = "_blank"; a.rel = "noopener"; a.textContent = "לפתיחה שם";
        askMsg.appendChild(a);
      }
      return false;
    }
    if (readOnly) { msg("העמוד פתוח לקריאה בלבד.", true); return false; }
    return true;
  }
  ask.addEventListener("submit", function (ev) {
    ev.preventDefault();
    if (askGo.dataset.busy) { if (askCtl) askCtl.abort(); return; }
    var comment = askT.value.trim(), reel = cur;
    if (!comment || !reel || !canRun("השינוי לפי הערה")) return;
    run(reel, prompt(reel, comment), "comment", comment);
  });
  askNew.addEventListener("click", function () {
    if (askNew.dataset.busy) { if (askCtl) askCtl.abort(); return; }
    var reel = cur;
    if (!reel || !canRun("רעיון חדש")) return;
    run(reel, ideaPrompt(reel), "new", "רעיון חדש");
  });
  askT.addEventListener("keydown", function (ev) { if (ev.key === "Enter" && (ev.metaKey || ev.ctrlKey)) { ev.preventDefault(); ask.requestSubmit(); } });
  dlg.addEventListener("close", function () { if (askCtl) askCtl.abort(); msg(""); });
  /* On claude.ai the ask buttons use the artifact's sample capability. On the project server there is no claude.ai, so
     POST /api/sample (tools/lumebook.py, the claude command of this Mac) answers instead; this wrapper looks like the
     artifact's sample function: a call, call.json, and errors with a .code the handlers below already know. */
  function localSample() {
    function fail(code, text) { var e = new Error(text || code); e.code = code; return e; }
    function call(input, opts) {
      var text = typeof input === "string" ? input : (input || []).map(function (m) { return m.content; }).join("\n\n");
      return fetch("/api/sample", { method: "POST", headers: { "Content-Type": "application/json", "X-LumeBook-Board": "1" },
        body: JSON.stringify({ prompt: text }), signal: opts && opts.signal }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) {
          if (!r.ok) throw fail(j.code || "failed", j.error);
          return { text: j.text || "", truncated: false };
        });
      }, function (x) { throw x && x.name === "AbortError" ? fail("cancelled") : fail("failed", x && x.message); });
    }
    call.json = function (input, opts) {
      return call(input, opts).then(function (r) {
        var t = r.text.replace(/^\s*```(?:json)?\s*|\s*```\s*$/g, "").trim(), a = t.indexOf("{"), b = t.lastIndexOf("}");
        if (!t) throw fail("empty_completion");
        try { return JSON.parse(a >= 0 && b > a ? t.slice(a, b + 1) : t); } catch (x) { throw fail("invalid_json"); }
      });
    };
    return call;
  }
  if (window.claude && claude.use) claude.use("sample").then(function (fn) { sampleFn = fn || null; }, function () {});
  else projectServer().then(function (ok) { if (ok) sampleFn = localSample(); });

  /* toolbar */
  var tb = $("#tb"), lastRange = null, lastEl = null;
  document.addEventListener("selectionchange", function () {
    var s = getSelection(); if (!s.rangeCount) return;
    var n = s.anchorNode; var el = n && (n.nodeType === 1 ? n : n.parentElement); el = el && el.closest("[data-ek]");
    if (el) { lastRange = s.getRangeAt(0).cloneRange(); lastEl = el; tb.classList.add("is-on"); }
    else if (!tb.contains(document.activeElement)) tb.classList.remove("is-on");
  });
  function restore() {
    if (!lastRange || !lastEl) return false;
    lastEl.focus({ preventScroll: true }); var s = getSelection(); s.removeAllRanges(); s.addRange(lastRange); return true;
  }
  function touched() { if (lastEl) lastEl.dispatchEvent(new Event("input", { bubbles: true })); }
  try { document.execCommand("styleWithCSS", false, true); } catch (x) {}
  $$("button[data-cmd]", tb).forEach(function (b) {
    b.addEventListener("mousedown", function (ev) { ev.preventDefault(); });
    b.addEventListener("click", function () {
      if (!restore()) return;
      var c = b.dataset.cmd;
      if (c === "link") {
        var inp = $("#tb-link"); inp.hidden = false; inp.value = "https://"; inp.focus(); inp.select(); return;
      }
      if (c === "dir") { var cur = lastEl.getAttribute("dir"); lastEl.setAttribute("dir", cur === "ltr" ? "rtl" : "ltr"); touched(); return; }
      document.execCommand(c, false, null); touched();
    });
  });
  var linkIn = $("#tb-link");
  linkIn.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") { linkIn.hidden = true; restore(); return; }
    if (ev.key !== "Enter") return;
    ev.preventDefault(); var v = linkIn.value.trim(); linkIn.hidden = true;
    if (restore() && /^(https?:|mailto:)/i.test(v)) { document.execCommand("createLink", false, v); touched(); }
  });
  $("#tb-block").addEventListener("change", function (ev) {
    if (ev.target.value && restore()) { document.execCommand("formatBlock", false, "<" + ev.target.value + ">"); touched(); } ev.target.value = "";
  });
  $("#tb-font").addEventListener("change", function (ev) {
    if (ev.target.value && restore()) { document.execCommand("fontName", false, ev.target.value); touched(); } ev.target.value = "";
  });
  $("#tb-size").addEventListener("change", function (ev) {
    if (ev.target.value && restore()) { document.execCommand("fontSize", false, ev.target.value); touched(); } ev.target.value = "";
  });
  $("#tb-color").addEventListener("input", function (ev) { if (restore()) { document.execCommand("foreColor", false, ev.target.value); touched(); } });
  $("#tb-hilite").addEventListener("input", function (ev) { if (restore()) { document.execCommand("hiliteColor", false, ev.target.value); touched(); } });
  document.addEventListener("keydown", function (ev) {
    if ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === "k" && ev.target.closest && ev.target.closest("[data-ek]")) {
      ev.preventDefault(); $('button[data-cmd="link"]', tb).click();
    }
  });
})();
</script>"""


def brief(dated, d):
    """The month in one block: who the reels talk to and which best sellers they sell (shared/facts.json top_books, buyers)."""
    facts = json.loads((HERE.parents[4] / "shared/facts.json").read_text())
    books = facts["top_books"]["books"]
    g = sum(1 for r in dated if r.get("audience") == "grandma")
    cards = []
    for b in books:
        if not b["id"]:
            continue
        page = f"books/{b['id']}"
        n = sum(1 for r in dated if r.get("page") == page)
        cards.append(f'<a href="https://lumebook.com/IL/he/{page}" target="_blank" rel="noopener"><b>{e(b["title"].split(" - ")[0])}</b>'
                     f'<span>{b["orders"]} הזמנות בכל התקופה, {n} רילס בחודש</span></a>')
    return (f'<section class="brief" aria-label="למי ועל מה"><h3>למי ועל מה החודש</h3>'
            f'<p>נשים בנות 55 עד 64 הן קבוצת הקונות הגדולה ביותר בנתוני מטא של 05 / 11 / 2026, ונשים מגיל 45 ומעלה הן 58% מהרכישות של נשים. '
            f'לכן {g} מתוך {len(dated)} הרילס מדברים לסבתות, והשאר להורים. כל ריל מכוון לספר מהרב מכר או לעמוד המתנות באתר, והקישור ב DM פותח אותו.</p>'
            f'<div class="books">{"".join(cards)}</div></section>')


def page(d):
    rs = sorted(d["reels"], key=reels.when)
    s = d["defaults"]
    L = s["length"]
    cats = design.categories("reel-series")
    dated = [r for r in rs if r["date"]]
    filt = '<button class="lb-chip cat no-swatch lb-cat-0" type="button" aria-pressed="true" data-f="all">הכול</button>' + "".join(
        f'<button class="lb-chip cat {design.cat_class("reel-series", k)}" type="button" aria-pressed="false" data-f="{k}">{e(v["label"])}</button>'
        for k, v in cats.items() if any(str(r["series"]) == k for r in rs))
    filt += '<button class="lb-chip cat lb-cat-3" type="button" aria-pressed="false" data-f="grandma">מדברים לסבתות</button>'
    cards = "".join(card(r, d) for r in dated)
    summary = brief(dated, d)
    cta_words = len(s["cta_voice"].split())
    ask_cfg = json.dumps({
        "facts": s["facts"], "offer": s.get("offer", {}).get("text", ""),
        "cta_voice": s["cta_voice"], "cta_caption": s["cta_caption"], "disclaimer": s["caption_disclaimer"],
        "vo_min": max(1, int((L["min"] - L["lead_seconds"]) * L["words_per_second"]) + 1 - cta_words),
        "vo_max": int((L["max"] - L["lead_seconds"]) * L["words_per_second"]) - cta_words,
        # the claude.ai copy of the hub: the ask buttons need claude.ai's sample capability, so the project server links there
        "artifact": json.loads((ROOT / "lumebook.json").read_text())["components"]["reels-hub"]["publish"]["url"],
    }, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>רילס נובמבר</title>
<meta name="claude:viewport-fit-sides" content="cover">
{design.head()}
<style>
/* Layout: a sticky bar with the save state, a formatting toolbar under it while text is being edited, a summary,
   the month as a 7-day grid (Sunday first), then one card per reel in date order, then the spares. */
body {{ background: var(--bg); color: var(--text); font-family: var(--font); }}
body::before {{ content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 21; background: var(--bar); }}
.lb-topbar-in, .lb-page {{ padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
.lb-topbar-in .sp {{ flex: 1; }}
.lb-topbar-in .sub {{ font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }}
#save-state {{ min-width: 6.5rem; justify-content: center; }}
.intro {{ display: grid; gap: var(--sp-3); }}
.intro h2 {{ font-size: var(--fs-display); font-weight: 800; letter-spacing: -.02em; line-height: 1.15; text-wrap: balance; }}
.intro p {{ color: var(--text-2); max-width: 62ch; }}
.filters {{ display: flex; flex-wrap: wrap; gap: var(--sp-2); }}
.aud {{ font-family: var(--font-2); font-size: .6875rem; font-weight: 700; padding: 0 5px; border-radius: 999px; background: var(--accent-soft); color: var(--accent-ink); }}
.brief {{ display: grid; gap: var(--sp-3); padding: var(--sp-4) var(--sp-5); border-radius: var(--r-lg); background: var(--surface-2); }}
.brief h3 {{ font-size: var(--fs-headline); }}
.brief p {{ color: var(--text-2); max-width: 70ch; font-size: var(--fs-callout); }}
.books {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: var(--sp-2); }}
.books a {{ display: grid; gap: 2px; padding: .6rem .8rem; border-radius: var(--r-md); background: var(--surface); border: 1px solid var(--line); color: var(--text); text-decoration: none; }}
.books a:hover {{ border-color: var(--tint); }}
.books b {{ font-size: var(--fs-callout); }}
.books span {{ font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }}
.st {{ width: .55rem; height: .55rem; border-radius: 50%; flex: none; }}
.st.success {{ background: var(--success); }} .st.info {{ background: var(--info); }} .st.warning {{ background: var(--warning); }} .st.danger {{ background: var(--danger); }}
.car {{ font-family: var(--font-2); font-size: .6875rem; color: var(--text-3); white-space: nowrap; }}
.legend {{ display: flex; flex-wrap: wrap; gap: var(--sp-2) var(--sp-4); font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-2); }}
.legend span {{ display: inline-flex; align-items: center; gap: 6px; }}
.reel {{ scroll-margin-top: 6rem; }}  /* the card itself is lb-card lb-tinted lb-cat-N */
.reel:target {{ box-shadow: 0 0 0 2px var(--tc); }}
.reel-head {{ display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-3); }}
.when {{ display: flex; align-items: baseline; gap: 8px; font-family: var(--font-2); }}
.when .wd {{ font-weight: 700; }} .when .dd {{ font-variant-numeric: tabular-nums; color: var(--text-2); }} .when .tm {{ color: var(--text-3); font-variant-numeric: tabular-nums; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }}
.hook-big {{ font-size: var(--fs-title); font-weight: 800; line-height: 1.25; letter-spacing: -.01em;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.hook-big:focus {{ white-space: normal; overflow: visible; }}
.rows {{ display: grid; gap: var(--sp-3); margin: var(--sp-3) 0 0; }}
.rows .row {{ display: grid; grid-template-columns: 9rem minmax(0, 1fr); gap: var(--sp-3); }}
.rows dt {{ font-family: var(--font-2); font-weight: 600; font-size: var(--fs-footnote); color: var(--text-3); padding-top: 2px; }}
.rows dd {{ margin: 0; min-width: 0; }}
.shot summary {{ cursor: pointer; width: fit-content; font-family: var(--font-2); font-weight: 600; font-size: var(--fs-footnote); color: var(--tint); }}
.shot summary:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 2px; border-radius: 4px; }}
.shot[open] summary {{ margin-bottom: 4px; }}
.shot .sub {{ display: block; margin-top: var(--sp-2); font-family: var(--font-2); font-weight: 600; font-size: var(--fs-footnote); color: var(--text-3); }}
.rows p, .rows li {{ font-size: var(--fs-callout); }}
.vo {{ margin: 0; padding-inline-start: 1.4rem; display: grid; gap: 3px; }}
.vo li::marker {{ color: var(--text-3); font-family: var(--font-2); font-size: var(--fs-footnote); }}
.vo li.fixed {{ color: var(--text-3); }}
.cap {{ display: grid; gap: var(--sp-2); justify-items: start; }}
.capbox {{ white-space: pre-wrap; font-size: var(--fs-callout); background: var(--surface-sunk); border-radius: var(--r-sm); padding: var(--sp-3); width: 100%; line-height: 1.55; }}
code {{ font-family: var(--font-mono); font-size: var(--fs-footnote); overflow-wrap: anywhere; }}
@media (max-width: 640px) {{
  .hook-big {{ font-size: var(--fs-headline); }}
  .car {{ display: none; }}
  .rows .row {{ grid-template-columns: minmax(0, 1fr); gap: 2px; }}
  .reel {{ padding: var(--sp-3) var(--sp-4); }}
  .lb-topbar-in .sub {{ display: none; }}
}}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
</head>
<body>
<header class="lb-topbar"><div class="lb-topbar-in">
  <h1>רילס נובמבר</h1><span class="sub">ריל ביום, {e(s['post_time'])}, {L['min']} עד {L['max']} שניות</span><span class="sp"></span>
  <span id="save-state" class="lb-chip" role="status" aria-live="polite">טוען...</span>
</div></header>
<main class="lb-page">
  <section class="intro">
    <span class="lb-eyebrow">05 עד 30 / 11 / 2026</span>
    {ed("h2", "page__title", "מערכת תוכן")}
  </section>

  {summary}

  <section class="lb-section" aria-labelledby="h-month">
    <div class="lb-section-head"><h2 id="h-month" class="lb-card-title">החודש</h2>
      <div class="legend"><span><i class="st success"></i>מוכן או פורסם</span><span><i class="st info"></i>מחכה לעריכה שלי</span><span><i class="st warning"></i>מחכה לך</span><span><i class="st danger"></i>חסום</span></div>
    </div>
    <div class="filters" role="group" aria-label="סינון לפי סדרה">{filt}</div>
    {month_grid(dated, s['carousel_days'])}
  </section>

</main>
<div id="cards" hidden>{cards}</div>
<dialog id="dlg" class="lb-dialog" aria-label="ריל">
  <div class="lb-dialog-card">
    <div class="lb-dialog-head">{TOOLBAR}<button type="button" class="lb-dialog-x" id="dlg-x" aria-label="סגירה">✕</button></div>
    <div class="lb-dialog-body" id="dlg-body"></div>
  </div>
  <form class="lb-ask" id="ask" autocomplete="off">
    <div class="lb-ask-top"><label class="lb-ask-label" for="ask-t">הערה לשינוי הריל</label><button type="button" class="lb-btn secondary sm" id="ask-new" title="מחליף את כל הריל ברעיון אחר לאותו יום ולאותה סדרה">רעיון חדש</button></div>
    <div class="lb-ask-row">
      <textarea id="ask-t" rows="2" dir="auto" placeholder="מה לשנות? למשל: כותרת יותר קצרה, פתיחה אחרת"></textarea>
      <button type="submit" class="lb-btn" id="ask-go">שליחה</button>
    </div>
    <p class="lb-ask-msg" id="ask-msg" role="status" aria-live="polite"></p>
  </form>
</dialog>
<script type="application/json" id="ask-cfg">{ask_cfg}</script>
{SCRIPT}
</body>
</html>
"""


def build(d=None):
    d = d or json.loads((HERE / "reels.json").read_text())
    OUT.write_text(page(d))
    return OUT


if __name__ == "__main__":
    print(build())
