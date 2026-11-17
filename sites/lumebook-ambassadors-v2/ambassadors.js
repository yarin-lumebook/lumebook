/* Redesigned ambassador page: live numbers, the split choice, the form and its states.
 *
 * Talks to the same API as the live store page (read from lumebook.com's code on 15 Nov 2026):
 *   GET  /api/ambassadors/program  -> {open, budgetMinor, stepMinor, discountOptions, regularPriceMinor, listPriceMinor, linkWindowDays, holdDays}
 *   POST /api/ambassadors/signup   body {fullName, email, discountMinor, termsAccepted:true, termsVersion, phone, program:"creators", socialHandle, followersBand}
 *        401 -> phone not verified yet (the store opens PhoneVerificationDialog, then sends the same body again)
 *        404 {error:"PROGRAM_CLOSED"} -> closed
 *        400 {fields:[...]} -> invalid fields
 *        200 {status:"disabled"} -> link paused
 *        200 {status:"active", link, existing, ...} -> the personal link
 *
 * Safety: the API is used only when the page runs on lumebook.com AND the form says data-api="live".
 * Everywhere else (local preview, review copies) a mock answers, so testing never creates an ambassador
 * or sends a WhatsApp code. ?demo=active|existing|verify-fail|invalid|error|disabled|closed picks the mock outcome.
 */
(function () {
  "use strict";

  var D = JSON.parse(document.getElementById("amb-data").textContent);
  var form = document.getElementById("amb-form");
  if (!form) return;

  var params = new URLSearchParams(location.search);
  var DEMO = params.get("demo") || "active";
  var onStore = /(^|\.)lumebook\.com$/.test(location.hostname);
  var LIVE = onStore && form.getAttribute("data-api") === "live";
  if (!LIVE) document.documentElement.setAttribute("data-mock", "");
  if (LIVE || params.has("clean")) {
    // ?clean=1 hides the review banner for screenshots; the form stays in mock mode
    document.querySelectorAll(".review[data-review-only]").forEach(function (el) { el.remove(); });
  }
  if (params.has("clean")) {
    document.querySelectorAll('img[loading="lazy"]').forEach(function (img) { img.loading = "eager"; }); // full-page screenshots
  }

  var program = D.program;

  /* ------------------------------------------------------------ helpers */
  function money(minor) {
    var n = minor / 100;
    return "₪" + new Intl.NumberFormat("he-IL", { minimumFractionDigits: n % 1 ? 2 : 0, maximumFractionDigits: 2 }).format(n);
  }
  // The reward is shown as a percentage of the book price, exactly as the live store computes it:
  // share = floor(budget / price), each discount step shown as its part of the share (Yarin, 15 Nov 2026: 25%, not ₪30).
  var PCT = new Intl.NumberFormat("he-IL", { style: "percent", maximumFractionDigits: 1 });
  function sharePct(p) {
    return p.regularPriceMinor > 0 ? Math.floor(p.budgetMinor / (p.regularPriceMinor / 100)) : D.shareFallback;
  }
  function splitPct(p, discountMinor) {
    var share = sharePct(p);
    if (p.budgetMinor <= 0) return { discount: 0, reward: 0 };
    var d = Math.round(share * discountMinor / p.budgetMinor * 10) / 10;
    return { discount: d, reward: Math.round((share - d) * 10) / 10 };
  }
  function pct(v) { return PCT.format(v / 100); }
  function fill(s, vars) {
    return s.replace(/\{(\w+)\}/g, function (m, k) { return k in vars ? vars[k] : m; });
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  }
  function track(event, props) {
    // New hooks only (the live page sends no ambassador events of its own). No personal data in props.
    try { document.dispatchEvent(new CustomEvent("lumebook:track", { detail: { event: event, props: props || {} } })); } catch (e) { /* old browser */ }
  }
  function normPhone(v) {
    var s = v.replace(/[\s().\-]/g, "");
    if (/^05\d{8}$/.test(s)) return s;
    if (/^\+9725\d{8}$/.test(s)) return "0" + s.slice(4);
    return null;
  }
  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var HANDLE = /^@?[A-Za-z0-9._]{1,30}$/;

  /* ------------------------------------------------------------ live numbers on the page */
  function applyProgram(p) {
    program = p;
    var ex = D.exampleDiscountMinor;
    if (p.discountOptions.indexOf(ex) === -1) ex = p.discountOptions[Math.floor(p.discountOptions.length / 3)] || 0;
    var exSplit = splitPct(p, ex);
    var vals = {
      share: pct(sharePct(p)), regular: money(p.regularPriceMinor), list: money(p.listPriceMinor),
      window: String(p.linkWindowDays), hold: String(p.holdDays),
      ex_disc_pct: pct(exSplit.discount), ex_reward_pct: pct(exSplit.reward),
      ex_reward_ils: money(p.budgetMinor - ex), ex_price: money(p.regularPriceMinor - ex)
    };
    document.querySelectorAll("[data-v]").forEach(function (el) {
      var k = el.getAttribute("data-v");
      if (k in vals && el.textContent !== vals[k]) el.textContent = vals[k];
    });
    var bar = document.querySelector(".ex-bar");
    if (bar) { bar.style.setProperty("--disc", exSplit.discount); bar.style.setProperty("--total", sharePct(p)); }
    renderSplitOptions();
    if (!p.open) showState("closed", true);
  }

  /* ------------------------------------------------------------ split choice */
  var splitBox = document.getElementById("split");
  var splitOut = document.getElementById("split-out");
  var barDisc = document.querySelector(".sb-disc");
  var barReward = document.querySelector(".sb-reward");

  function renderSplitOptions() {
    var have = Array.prototype.map.call(splitBox.querySelectorAll("input"), function (i) { return +i.value; });
    var want = program.discountOptions;
    if (have.join() !== want.join()) {
      var current = selectedDiscount();
      var pick = want.indexOf(current) !== -1 ? current : want[Math.floor(want.length / 2)];
      splitBox.style.setProperty("--n", want.length);
      splitBox.innerHTML = want.map(function (o) {
        return '<label class="seg"><input type="radio" name="discountMinor" value="' + o + '"' + (o === pick ? " checked" : "") +
          "><span>" + pct(splitPct(program, o).discount) + '<span class="sr-only"> הנחה</span></span></label>';
      }).join("");
    }
    updateSplit();
  }
  function selectedDiscount() {
    var c = splitBox.querySelector("input:checked");
    return c ? +c.value : null;
  }
  function updateSplit() {
    var d = selectedDiscount();
    if (d === null) { splitOut.textContent = ""; return; }
    var sp = splitPct(program, d);
    var vars = { price: "<b>" + money(program.regularPriceMinor - d) + "</b>", regular: money(program.regularPriceMinor), reward: "<b>" + pct(sp.reward) + "</b>", share: "<b>" + pct(sharePct(program)) + "</b>" };
    var key = d === 0 ? "split_out_none" : sp.reward <= 0 ? "split_out_all" : "split_out_both";
    splitOut.innerHTML = fill(esc(D.form[key]), vars);
    barDisc.style.flexGrow = sp.discount;
    barReward.style.flexGrow = Math.max(sp.reward, 0);
  }
  splitBox.addEventListener("change", function () { updateSplit(); if (submitted) validate(false); });

  /* ------------------------------------------------------------ validation */
  var E = D.form.errors;
  var FIELDS = [
    { name: "socialHandle", el: "f-handle", err: "e-handle", check: function () {
      var v = form.socialHandle.value.trim();
      if (!v) return E.handle_missing;
      if (!HANDLE.test(v)) return E.handle_invalid;
    } },
    { name: "followersBand", group: "bands", err: "e-followers", check: function () {
      if (!form.querySelector('input[name="followersBand"]:checked')) return E.followers;
    } },
    { name: "fullName", el: "f-name", err: "e-name", check: function () {
      if (form.fullName.value.trim().length < 2) return E.name;
    } },
    { name: "phone", el: "f-phone", err: "e-phone", check: function () {
      if (!normPhone(form.phone.value)) return E.phone;
    } },
    { name: "email", el: "f-email", err: "e-email", check: function () {
      if (!EMAIL.test(form.email.value.trim())) return E.email;
    } },
    { name: "discountMinor", group: "split", err: "e-split", check: function () {
      if (selectedDiscount() === null) return E.split;
    } },
    { name: "termsAccepted", el: "f-terms", err: "e-terms", check: function () {
      if (!form.termsAccepted.checked) return E.terms;
    } }
  ];
  var submitted = false;
  var serverBad = {};

  function setError(f, msg) {
    var target = document.getElementById(f.el || f.group);
    var err = document.getElementById(f.err);
    if (msg) {
      err.textContent = msg; err.hidden = false;
      target.setAttribute("aria-invalid", "true");
    } else {
      err.textContent = ""; err.hidden = true;
      target.removeAttribute("aria-invalid");
    }
  }
  function validate(focusFirst) {
    var bad = [];
    FIELDS.forEach(function (f) {
      var msg = f.check() || serverBad[f.name];
      setError(f, msg);
      if (msg) bad.push({ f: f, msg: msg });
    });
    var sum = document.getElementById("err-sum");
    if (bad.length && focusFirst) {
      sum.innerHTML = "<p style=\"margin:0\">" + esc(E.summary) + "</p><ul>" + bad.map(function (b) {
        return '<li><a href="#' + (b.f.el || b.f.group) + '">' + esc(b.msg) + "</a></li>";
      }).join("") + "</ul>";
      sum.hidden = false;
      var first = document.getElementById(bad[0].f.el) || document.querySelector("#" + bad[0].f.group + " input");
      if (first) first.focus();
    } else if (!bad.length) {
      sum.hidden = true; sum.innerHTML = "";
    }
    return bad.length === 0;
  }
  document.getElementById("err-sum").addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a) return;
    e.preventDefault();
    var id = a.getAttribute("href").slice(1);
    var el = document.getElementById(id);
    var input = el && (el.matches("input") ? el : el.querySelector("input"));
    if (input) input.focus();
  });

  var started = false;
  form.addEventListener("input", function (e) {
    if (!started) { started = true; track("Ambassador_Form_Started"); }
    if (e.target.name === "socialHandle" && /^\s*@/.test(e.target.value)) {
      e.target.value = e.target.value.replace(/^\s*@+/, ""); // the field already shows the @
    }
    var name = e.target.name;
    if (serverBad[name]) delete serverBad[name];
    if (submitted) validate(false);
  });
  form.addEventListener("change", function (e) {
    if (serverBad[e.target.name]) delete serverBad[e.target.name];
    if (submitted) validate(false);
  });

  /* ------------------------------------------------------------ API: live or mock */
  var mockVerified = false;
  var mockFailedOnce = false;
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  var api = LIVE ? {
    program: function () {
      return fetch("/api/ambassadors/program", { credentials: "include", cache: "no-store", headers: { Accept: "application/json" } })
        .then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
    },
    signup: function (body) {
      return fetch("/api/ambassadors/signup", { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
        .then(function (r) {
          return r.json().catch(function () { return null; }).then(function (j) { return mapSignup(r.status, r.ok, j); });
        }).catch(function () { return { kind: "error" }; });
    },
    verify: function (phone) {
      // On the store this is the existing PhoneVerificationDialog (verificationOnly, lockedCountryCode IL, hideEmail,
      // hideMarketingConsent). A static copy cannot run it: the store must provide window.LumeBookVerifyPhone(phone) -> Promise<boolean>.
      if (typeof window.LumeBookVerifyPhone === "function") return window.LumeBookVerifyPhone(phone);
      return Promise.resolve(false);
    }
  } : {
    program: function () {
      var p = JSON.parse(JSON.stringify(D.program));
      if (DEMO === "closed") p.open = false;
      return wait(250).then(function () { return p; });
    },
    signup: function (body) {
      return wait(700).then(function () {
        if (DEMO === "error") return { kind: "error" };
        if (DEMO === "invalid") return { kind: "invalid", fields: ["socialHandle", "email"] };
        if (!mockVerified) return { kind: "verify" };
        if (DEMO === "disabled") return { kind: "disabled" };
        if (DEMO === "existing") return { kind: "active", existing: true, link: "https://lumebook.com/demo-link", discountMinor: 1000 };
        return { kind: "active", existing: false, link: "https://lumebook.com/demo-link", discountMinor: body.discountMinor };
      });
    },
    verify: null // the mock uses the dialog below
  };

  function mapSignup(status, ok, r) {
    if (status === 401) return { kind: "verify" };
    if (status === 404 && r && r.error === "PROGRAM_CLOSED") return { kind: "closed" };
    if (status === 400) return { kind: "invalid", fields: r && Array.isArray(r.fields) ? r.fields.filter(function (f) { return typeof f === "string"; }) : [] };
    if (!ok || !r) return { kind: "error" };
    if (r.status === "disabled") return { kind: "disabled" };
    if (r.status === "active" && typeof r.link === "string") {
      return { kind: "active", existing: r.existing === true, link: r.link, discountMinor: typeof r.discountMinor === "number" ? r.discountMinor : null };
    }
    return { kind: "error" };
  }

  /* ------------------------------------------------------------ verify dialog (mock stand-in) */
  var dlg = document.getElementById("verify");
  var V = D.verify;
  function askCode(phone) {
    if (LIVE) return api.verify(phone);
    return new Promise(function (resolve) {
      var input = document.getElementById("f-code");
      var err = document.getElementById("verify-err");
      var ok = document.getElementById("verify-ok");
      document.getElementById("verify-text").textContent = fill(V.text, { phone: phone });
      input.value = ""; err.hidden = true; input.removeAttribute("aria-invalid");
      ok.disabled = false; ok.textContent = V.submit;
      function done(result) {
        dlg.removeEventListener("cancel", onCancel);
        document.getElementById("verify-cancel").onclick = null;
        document.getElementById("verify-form").onsubmit = null;
        if (dlg.open) dlg.close();
        if (!result) btn.focus(); // back to where the person was
        resolve(result);
      }
      function onCancel() { done(false); }
      dlg.addEventListener("cancel", onCancel);
      document.getElementById("verify-cancel").onclick = function () { done(false); };
      document.getElementById("verify-form").onsubmit = function (e) {
        e.preventDefault();
        var code = input.value.replace(/\D/g, "");
        var wrong = !/^\d{6}$/.test(code) || (DEMO === "verify-fail" && !mockFailedOnce);
        if (wrong) {
          if (/^\d{6}$/.test(code)) mockFailedOnce = true;
          err.textContent = V.error; err.hidden = false; input.setAttribute("aria-invalid", "true"); input.focus();
          return;
        }
        ok.disabled = true; ok.textContent = V.processing;
        wait(500).then(function () { mockVerified = true; done(true); });
      };
      dlg.showModal();
      input.focus();
    });
  }

  /* ------------------------------------------------------------ submit */
  var btn = document.getElementById("submit");
  var formErr = document.getElementById("form-err");
  var busy = false;

  function setBusy(on) {
    busy = on;
    btn.disabled = on;
    btn.setAttribute("aria-busy", on ? "true" : "false");
    btn.textContent = on ? D.form.sending : D.form.submit;
  }

  function payload() {
    return {
      fullName: form.fullName.value.trim(),
      email: form.email.value.trim(),
      discountMinor: selectedDiscount(),
      termsAccepted: true,
      termsVersion: D.termsVersion,
      phone: normPhone(form.phone.value) || form.phone.value.trim(),
      program: "creators",
      socialHandle: "@" + form.socialHandle.value.trim().replace(/^@+/, ""), // the live form's placeholder is "@username"
      followersBand: (form.querySelector('input[name="followersBand"]:checked') || {}).value
    };
  }

  function send(body, afterVerify) {
    setBusy(true);
    formErr.hidden = true;
    return api.signup(body).then(function (res) {
      setBusy(false);
      track("Ambassador_Signup_Result", { kind: res.kind, existing: !!res.existing });
      if (res.kind === "verify") {
        if (afterVerify) { showFormError(E.generic); return; }
        return askCode(body.phone).then(function (ok) { if (ok) return send(body, true); });
      }
      if (res.kind === "invalid") {
        serverBad = {};
        res.fields.forEach(function (f) { serverBad[f] = E.server_fields; });
        if (!res.fields.length) showFormError(E.generic);
        validate(true);
        return;
      }
      if (res.kind === "closed") return showState("closed");
      if (res.kind === "disabled") return showState("disabled");
      if (res.kind === "active") return showSuccess(res, body);
      showFormError(E.generic);
    });
  }

  function showFormError(msg) {
    formErr.innerHTML = esc(msg) + ' <a href="' + esc(D.whatsapp) + '" target="_blank" rel="noopener">' + esc(D.states.whatsapp) + "</a>";
    formErr.hidden = false;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (busy) return;
    submitted = true;
    serverBad = {};
    if (!validate(true)) return;
    track("Ambassador_Signup_Submitted", { discountMinor: selectedDiscount() });
    send(payload(), false);
  });

  /* ------------------------------------------------------------ success and other states */
  var S = D.success;
  function view(name, quiet) {
    document.querySelectorAll("#join [data-view]").forEach(function (el) { el.hidden = el.getAttribute("data-view") !== name; });
    if (quiet) return; // e.g. the program is closed when the page loads: no jump, no focus move
    var target = document.querySelector('#join [data-view="' + name + '"]');
    var h = target.querySelector("h2");
    if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
    document.getElementById("join").scrollIntoView({ block: "start" });
  }

  function showSuccess(res, body) {
    var d = typeof res.discountMinor === "number" ? res.discountMinor : body.discountMinor;
    var sp = splitPct(program, d);
    var first = body.fullName.split(/\s+/)[0];
    var title = res.existing ? S.title_existing : first ? fill(S.title, { name: first }) : S.title_noname;
    var share = pct(sharePct(program));
    var sub = res.existing ? S.sub_existing : fill(d > 0 ? S.sub : S.sub_none, { window: program.linkWindowDays, share: share });
    var price = money(program.regularPriceMinor - d);
    // Three share texts: part discount, no discount, and the whole share as discount (no reward, still a commercial collaboration).
    var shareKey = d === 0 ? "share_text_none" : sp.reward <= 0 ? "share_text_all" : "share_text";
    var shareText = fill(S[shareKey], { price: price, regular: money(program.regularPriceMinor), share: share });
    var wa = D.whatsapp + "?text=" + encodeURIComponent(fill(S.wa_message, { link: res.link }));
    var hrefs = [D.routes.books, wa, D.routes.dashboard];
    var canShare = typeof navigator.share === "function";
    var box = document.querySelector('#join [data-view="success"]');
    box.innerHTML =
      '<p class="ok-badge">✓ <span>' + esc(res.existing ? S.badge_existing : S.badge_new) + "</span></p>" +
      '<h2 class="sec-h">' + esc(title) + "</h2>" +
      '<p class="sec-intro">' + esc(sub) + "</p>" +
      '<div class="linkbox"><p class="linkbox-label">' + esc(S.link_label) + "</p>" +
      "<code>" + esc(res.link.replace(/^https?:\/\//, "")) + "</code>" +
      '<div class="linkbox-btns"><button class="btn btn-gold" type="button" data-copy>' + esc(S.copy) + "</button>" +
      (canShare ? '<button class="btn btn-ghost" type="button" data-share>' + esc(S.share) + "</button>" : "") +
      '</div><p class="sr-only" aria-live="polite" data-copied></p></div>' +
      '<p class="split-line">' + esc(fill(S.split_line, { discount: pct(sp.discount), reward: pct(Math.max(sp.reward, 0)) })) + "</p>" +
      '<h3 class="card-h" style="margin-top:1.5rem">' + esc(S.next_title) + "</h3>" +
      '<ol class="next-list">' + S.next.map(function (n, i) {
        var ext = i === 1 ? ' target="_blank" rel="noopener"' : "";
        return "<li><p>" + esc(n.t) + '</p><a class="btn btn-ghost" href="' + esc(hrefs[i]) + '"' + ext + ">" + esc(n.b) + "</a></li>";
      }).join("") + "</ol>";
    box.querySelector("[data-copy]").addEventListener("click", function (e) {
      var b = e.currentTarget;
      var live = box.querySelector("[data-copied]");
      var done = function () { b.textContent = S.copied; live.textContent = S.copied; setTimeout(function () { b.textContent = S.copy; live.textContent = ""; }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(res.link).then(done, function () {});
    });
    var sh = box.querySelector("[data-share]");
    if (sh) sh.addEventListener("click", function () { navigator.share({ title: "LumeBook", text: shareText, url: res.link }).catch(function () {}); });
    view("success");
  }

  function showState(kind, quiet) {
    var St = D.states;
    var box = document.querySelector('#join [data-view="state"]');
    box.innerHTML = '<h2 class="sec-h">' + esc(St[kind + "_title"]) + "</h2>" +
      '<p class="sec-intro">' + esc(St[kind + "_text"]) + "</p>" +
      '<p style="margin-top:1.25rem"><a class="btn btn-gold" href="' + esc(D.whatsapp) + '" target="_blank" rel="noopener">' + esc(St.whatsapp) + "</a></p>";
    view("state", quiet);
  }

  /* ------------------------------------------------------------ start */
  /* ------------------------------------------------------------ sticky join button (phones and tablets) */
  // Shown only while neither the hero button nor the join section is on screen. CSS keeps it off from 900px up.
  var sticky = document.querySelector("[data-sticky-cta]");
  var heroBtn = document.querySelector(".hero .btn-lg");
  var joinSec = document.getElementById("join");
  if (sticky && heroBtn && joinSec && "IntersectionObserver" in window) {
    var inView = { hero: false, join: false };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { inView[e.target === heroBtn ? "hero" : "join"] = e.isIntersecting; });
      sticky.classList.toggle("is-on", !inView.hero && !inView.join);
    });
    io.observe(heroBtn);
    io.observe(joinSec);
  }

  document.querySelectorAll("[data-track]").forEach(function (el) {
    el.addEventListener("click", function () { track(el.getAttribute("data-track")); });
  });
  updateSplit();
  api.program().then(function (p) {
    if (p && Array.isArray(p.discountOptions) && p.discountOptions.length && typeof p.budgetMinor === "number") applyProgram(p);
  });
})();
