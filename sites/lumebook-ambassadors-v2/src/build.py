#!/usr/bin/env python3
"""Build the redesigned ambassador page (review prototype for https://lumebook.com/IL/he/ambassadors).

Run:  python3 sites/lumebook-ambassadors-v2/src/build.py
Then: python3 sites/lumebook-ambassadors-v2/lint_copy.py

Reads the copy from src/content/he.json and the program numbers from shared/facts.json `ambassador_program`
(the store's terms, read 15 Nov 2026). Writes index.html. Never edit index.html by hand.

Numbers in the copy are written as {tokens}. The build fills them with the facts and wraps each in
<span data-v="token">, so ambassadors.js can replace them with the live values from GET /api/ambassadors/program
(budget, prices, link window, hold days). Standard library only.
"""
import html
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(SITE, "..", ".."))

COPY = json.load(open(os.path.join(HERE, "content", "he.json"), encoding="utf-8"))
FACTS = json.load(open(os.path.join(ROOT, "shared", "facts.json"), encoding="utf-8"))
P = FACTS["ambassador_program"]

STORE = "https://lumebook.com"  # the review copy links to the live store; on integration these become relative routes
ROUTES = {k: STORE + v for k, v in P["routes"].items()}
WHATSAPP = "https://wa.me/" + P["whatsapp"]
INSTAGRAM = "https://www.instagram.com/" + P["instagram"] + "/"
COVERS = [  # the store's own covers, non-religious best sellers (same rule as the partners page)
    ("girl", "B41_girl"),
    ("boy", "B13_boy"),
    ("girl", "B10_girl"),
]
COVER_URL = STORE + "/book_covers/{g}/{id}.avif"
OPEN_BOOK = "../lumebook-partners/img/book-open.webp"  # Ben, the made up toddler of the character pack (partners README)
LOGO = "../../shared/brand/logo_icon.png"


def money(n):
    return "₪{:,}".format(int(n))


# The reward is presented as a percentage of the book price (Yarin, 15 Nov 2026: "זה 25% לא 30 שקלים"),
# computed exactly as the live store does (ambassadorPercent-*.js): share = floor(budget / price), and each
# discount step is shown as its part of that share, rounded half up to one decimal.
SHARE = math.floor(P["budget_ils"] * 100 / P["regular_price_ils"])


def split_pct(discount_ils):
    d = math.floor(SHARE * discount_ils / P["budget_ils"] * 10 + 0.5) / 10
    return d, math.floor((SHARE - d) * 10 + 0.5) / 10


def pct(v):
    return f"{v:g}%"


EX_DISC = P["example_discount_ils"]
EX_DISC_PCT, EX_REWARD_PCT = split_pct(EX_DISC)
# he.json example.intro says "חצי לכל צד": keep the example an even split, or change that line too.
assert EX_DISC_PCT == EX_REWARD_PCT, "example split is no longer half and half: update example.intro in he.json"
VALUES = {  # token: (value, kind) ; kind "m" = money, "p" = percent, "n" = number
    "share": (SHARE, "p"),
    "regular": (P["regular_price_ils"], "m"),
    "list": (P["list_price_ils"], "m"),
    "book": (P["book_value_ils"], "m"),
    "cashmin": (P["cash_minimum_ils"], "m"),
    "ex_disc_pct": (EX_DISC_PCT, "p"),
    "ex_reward_pct": (EX_REWARD_PCT, "p"),
    "ex_reward_ils": (P["budget_ils"] - EX_DISC, "m"),
    "ex_price": (P["regular_price_ils"] - EX_DISC, "m"),
    "months": (P["license_months"], "n"),
    "window": (P["link_window_days"], "n"),
    "hold": (P["hold_days"], "n"),
    "paydays": (P["payout_business_days"], "n"),
    "expiry": (P["expiry_days"], "n"),
    "notice": (P["notice_days"], "n"),
}
TOKEN = re.compile(r"\{(\w+)\}")


def show(v, kind):
    return money(v) if kind == "m" else pct(v) if kind == "p" else str(v)


def plain(s):
    """Fill tokens with plain text (meta tags, attributes)."""
    def rep(m):
        k = m.group(1)
        if k not in VALUES:
            return m.group(0)
        v, kind = VALUES[k]
        return show(v, kind)
    return TOKEN.sub(rep, s)


def t(s):
    """Escape, then fill tokens with spans the page script can update."""
    s = html.escape(s, quote=False)

    def rep(m):
        k = m.group(1)
        if k not in VALUES:
            raise SystemExit(f"unknown token {{{k}}} in copy")
        v, kind = VALUES[k]
        shown = show(v, kind)
        return f'<span class="v" data-v="{k}">{shown}</span>'
    return TOKEN.sub(rep, s)


def a(s):
    return html.escape(plain(s), quote=True)


ICON = {
    "check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "do": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10.2 8.6l5 3.4-5 3.4z" fill="currentColor"/></svg>',
    "info": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 10.8v5.6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="7.6" r="1.3" fill="currentColor"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.2a8.7 8.7 0 0 0-7.5 13.1L3.3 20.8l4.6-1.2A8.7 8.7 0 1 0 12 3.2z" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"/><path d="M9 8.3c.3-.6.9-.6 1.1 0l.6 1.5c.1.3 0 .6-.2.8l-.5.5c.6 1.2 1.6 2.2 2.8 2.8l.5-.5c.2-.2.5-.3.8-.2l1.5.6c.6.2.6.8 0 1.1-.6.4-1.4.6-2.1.4-2.4-.7-4.4-2.7-5.1-5.1-.2-.7 0-1.5.4-2z" fill="currentColor"/></svg>',
}

ACTOR_CLASS = {"אתם": "you", "LumeBook": "lb", "לומבוק": "lb", "הקונים": "buyer"}


def build():
    c = COPY
    out = []
    w = out.append
    hero, steps, deal, ex, costs, faq, form = c["hero"], c["steps"], c["deal"], c["example"], c["costs"], c["faq"], c["form"]

    # ---------------------------------------------------------------- head
    w("<!doctype html>")
    w('<html lang="he" dir="rtl">')
    w("<head>")
    w('<meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    w(f"<title>{a(c['meta']['title'])}</title>")
    w(f'<meta name="description" content="{a(c["meta"]["description"])}">')
    w("<!-- REVIEW COPY: remove the robots line when the page moves into the store -->")
    w('<meta name="robots" content="noindex, nofollow">')
    w(f'<link rel="canonical" href="{ROUTES["page"]}">')
    w(f'<meta property="og:title" content="{a(c["meta"]["title"])}">')
    w(f'<meta property="og:description" content="{a(c["meta"]["description"])}">')
    w('<meta property="og:locale" content="he_IL">')
    w('<meta name="theme-color" content="#0b0518">')
    w('<link rel="preconnect" href="https://fonts.googleapis.com">')
    w('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    w('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800&display=swap">')
    w('<link rel="stylesheet" href="ambassadors.css">')
    w("</head>")
    w('<body class="amb2">')

    # ---------------------------------------------------------------- review banner + store chrome stand-in
    w('<div class="review" data-review-only role="note">')
    w(f'  <p>{t(c["review"]["banner"])}</p>')
    w(f'  <p class="review-states"><span>{t(c["review"]["states"])}</span> '
      + " ".join(f'<a href="?demo={k}#join">{k}</a>' for k in ["active", "existing", "verify-fail", "invalid", "error", "disabled", "closed"])
      + "</p>")
    w("</div>")
    w('<header class="store-bar" data-store-chrome>')
    w(f'  <a class="store-logo" href="{STORE}/IL/he"><img src="{LOGO}" alt="" width="28" height="28"><span>LumeBook</span></a>')
    w(f'  <a class="store-link" href="{ROUTES["dashboard"]}">{t(c["footer"]["dashboard"])}</a>')
    w("</header>")

    w('<main id="top">')

    # ---------------------------------------------------------------- hero
    w('<section class="hero" aria-labelledby="hero-title">')
    w('  <div class="wrap hero-grid">')
    w('    <div class="hero-text">')
    w(f'      <p class="eyebrow">{t(hero["eyebrow"])}</p>')
    # Each sentence of the headline starts its own line, so a phone never breaks between "לילדים." and "אתם".
    h1 = " ".join(f'<span class="h1-line">{t(part)}</span>' for part in re.split(r"(?<=\.) ", hero["h1"]))
    w(f'      <h1 id="hero-title">{h1}</h1>')
    w(f'      <p class="lead">{t(hero["lead"])}</p>')
    w(f'      <p class="fit">{ICON["check"]}<span>{t(hero["fit"])}</span></p>')
    w('      <div class="deal-sum">')
    for key, icon, cls in (("get", "check", "is-get"), ("do", "do", "is-do")):
        w(f'        <div class="deal-col {cls}">')
        w(f'          <h2 class="deal-h">{t(hero[key + "_title"])}</h2>')
        w("          <ul>")
        for item in hero[key]:
            w(f'            <li>{ICON[icon]}<span>{t(item)}</span></li>')
        w("          </ul>")
        w("        </div>")
    w("      </div>")
    w('      <div class="cost">')
    w(f'        <p class="cost-h"><span class="cost-q">{t(hero["cost_title"])}</span> <strong class="cost-v">{t(hero["cost_value"])}</strong></p>')
    w(f'        <p class="cost-t">{t(hero["cost_text"])}</p>')
    w(f'        <p class="cost-c">{ICON["info"]}<span>{t(hero["cost_condition"])} <a href="#costs">{t(hero["cost_link"])}</a></span></p>')
    w("      </div>")
    w('      <div class="cta-row">')
    w(f'        <a class="btn btn-gold btn-lg" href="#join" data-track="Ambassador_Hero_CTA_Clicked">{t(hero["cta"])}</a>')
    w(f'        <a class="text-link" href="#how">{t(hero["how_link"])} {ICON["arrow"]}</a>')
    w("      </div>")
    w(f'      <p class="cta-note">{t(hero["cta_note"])}</p>')
    w("    </div>")
    w(f'    <div class="covers" role="img" aria-label="{a(hero["covers_alt"])}">')
    for k, (g, cid) in enumerate(COVERS):
        w(f'      <img class="cv cv{k + 1}" src="{COVER_URL.format(g=g, id=cid)}" alt="" width="640" height="640" decoding="async"{" fetchpriority=\"high\"" if k == 1 else ""}>')
    w("    </div>")
    w("  </div>")
    w("</section>")

    # ---------------------------------------------------------------- steps
    w('<section id="how" class="sec" aria-labelledby="how-title">')
    w('  <div class="wrap narrow">')
    w(f'    <h2 id="how-title" class="sec-h">{t(steps["h2"])}</h2>')
    w(f'    <p class="sec-intro">{t(steps["intro"])}</p>')
    w('    <ol class="steps">')
    for n, s in enumerate(steps["items"], 1):
        w('      <li class="step">')
        w(f'        <span class="step-n" aria-hidden="true">{n}</span>')
        w('        <div class="step-body">')
        w(f'          <p class="step-who"><span class="who who-{ACTOR_CLASS[s["actor"]]}">{t(s["actor"])}</span></p>')
        w(f'          <h3 class="step-t"><span class="sr-only">צעד {n}: </span>{t(s["title"])}</h3>')
        w(f'          <p class="step-x">{t(s["text"])}</p>')
        w('          <p class="step-next">'
          f'<span class="then">{t(steps["then"])}</span>'
          f'<span class="who who-{ACTOR_CLASS[s["next_actor"]]}">{t(s["next_actor"])}</span>'
          f'<span class="step-next-x">{t(s["next"])}</span></p>')
        w("        </div>")
        w("      </li>")
    w("    </ol>")
    w("  </div>")
    w("</section>")

    # ---------------------------------------------------------------- what you get / what you give
    w('<section id="deal" class="sec" aria-labelledby="deal-title">')
    w('  <div class="wrap">')
    w(f'    <h2 id="deal-title" class="sec-h">{t(deal["h2"])}</h2>')
    w('    <figure class="book-fig">')
    w(f'      <img src="{OPEN_BOOK}" alt="{a(deal["image_alt"])}" width="900" height="684" decoding="async">')
    w(f'      <figcaption>{t(deal["image_note"])}</figcaption>')
    w("    </figure>")
    w('    <div class="deal-grid">')
    for key, icon, cls in (("get", "check", "is-get"), ("give", "do", "is-do")):
        w(f'      <div class="card deal-card {cls}">')
        w(f'        <h3 class="card-h">{t(deal[key + "_title"])}</h3>')
        w('        <ul class="deal-list">')
        for item in deal[key]:
            w(f'          <li>{ICON[icon]}<div><strong>{t(item["t"])}</strong><span class="dd">{t(item["d"])}</span></div></li>')
        w("        </ul>")
        w("      </div>")
    w("    </div>")
    w("  </div>")
    w("</section>")

    # ---------------------------------------------------------------- example
    w('<section id="example" class="sec" aria-labelledby="ex-title">')
    w('  <div class="wrap narrow">')
    w(f'    <h2 id="ex-title" class="sec-h">{t(ex["h2"])}</h2>')
    w('    <div class="card ex-card">')
    w(f'      <p class="ex-intro">{t(ex["intro"])}</p>')
    w(f'      <div class="ex-bar" aria-hidden="true" style="--disc:{EX_DISC_PCT};--total:{SHARE}">')
    w(f'        <span class="ex-disc"><b>{t("{ex_disc_pct}")}</b> {t(ex["bar_disc"])}</span>')
    w(f'        <span class="ex-reward"><b>{t("{ex_reward_pct}")}</b> {t(ex["bar_reward"])}</span>')
    w("      </div>")
    w('      <ol class="ex-steps">')
    for line in ex["steps"]:
        w(f"        <li>{t(line)}</li>")
    w("      </ol>")
    w(f'      <p class="ex-range">{t(ex["range"])}</p>')
    w(f'      <p class="fine">{t(ex["note"])}</p>')
    w("    </div>")
    # Payout conditions next to the split explanation, not only in the FAQ (Yarin's revised copy, 17 Nov 2026).
    w('    <div class="ex-payout">')
    w(f'      <h3 class="ex-payout-h">{t(ex["payout_title"])}</h3>')
    w(f'      <p>{t(ex["payout"])}</p>')
    w("    </div>")
    w("  </div>")
    w("</section>")

    # ---------------------------------------------------------------- costs
    w('<section id="costs" class="sec" aria-labelledby="costs-title">')
    w('  <div class="wrap narrow">')
    w(f'    <h2 id="costs-title" class="sec-h">{t(costs["h2"])}</h2>')
    w('    <dl class="costs card">')
    for r in costs["rows"]:
        flag = " is-flag" if r.get("flag") else ""
        w(f'      <div class="cost-row{flag}">')
        w(f'        <dt>{t(r["k"])}</dt>')
        w(f'        <dd class="cost-row-v">{t(r["v"])}</dd>')
        w(f'        <dd class="cost-row-d">{t(r["d"])}</dd>')
        w("      </div>")
    w("    </dl>")
    w(f'    <p class="fine">{t(costs["months_note"])}</p>')
    w("  </div>")
    w("</section>")

    # ---------------------------------------------------------------- faq
    w('<section id="faq" class="sec" aria-labelledby="faq-title">')
    w('  <div class="wrap narrow">')
    w(f'    <h2 id="faq-title" class="sec-h">{t(faq["h2"])}</h2>')
    w('    <div class="faq">')
    for item in faq["items"]:
        w("      <details>")
        w(f'        <summary><span>{t(item["q"])}</span></summary>')
        w(f'        <p>{t(item["a"])}</p>')
        w("      </details>")
    w("    </div>")
    w(f'    <p class="faq-more"><a href="{ROUTES["terms"]}">{t(faq["more"])}</a></p>')
    w("  </div>")
    w("</section>")

    # ---------------------------------------------------------------- form
    budget_minor = P["budget_ils"] * 100
    step_minor = P["step_ils"] * 100
    options = list(range(0, budget_minor + 1, step_minor))
    default = options[len(options) // 2]
    w('<section id="join" class="sec sec-join" aria-labelledby="join-title" tabindex="-1">')
    w('  <div class="wrap form-wrap">')
    w('    <div class="card join-card" data-view="form">')
    w(f'      <h2 id="join-title" class="sec-h">{t(form["h2"])}</h2>')
    w(f'      <p class="sec-intro">{t(form["sub"])}</p>')
    w(f'      <p class="have"><a href="{ROUTES["dashboard"]}">{t(form["have_link"])}</a></p>')
    w('      <form id="amb-form" novalidate data-api="mock">')
    w(f'        <div class="err-sum" id="err-sum" role="alert" hidden tabindex="-1"></div>')
    # social
    w('        <fieldset class="grp">')
    w(f'          <legend>{t(form["g_social"])}</legend>')
    w('          <div class="field" data-field="socialHandle">')
    w(f'            <label for="f-handle">{t(form["handle"])}</label>')
    w(f'            <p class="hint" id="h-handle">{t(form["handle_hint"])}</p>')
    w(f'            <div class="in-wrap in-at"><span class="at" aria-hidden="true">@</span><input id="f-handle" name="socialHandle" dir="ltr" type="text" inputmode="text" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="{a(form["handle_ph"])}" aria-describedby="h-handle e-handle" required></div>')
    w('            <p class="err" id="e-handle" hidden></p>')
    w("          </div>")
    w('          <fieldset class="field sub" data-field="followersBand" aria-describedby="h-followers e-followers">')
    w(f'            <legend>{t(form["followers"])}</legend>')
    w(f'            <p class="hint" id="h-followers">{t(form["followers_hint"])}</p>')
    w('            <div class="chips" id="bands">')
    for band in P.get("follower_bands", ["under_5000", "5000_15000", "15000_30000", "30000_plus"]):
        w(f'              <label class="chip"><input type="radio" name="followersBand" value="{band}" required><span>{t(form["bands"][band])}</span></label>')
    w("            </div>")
    w('            <p class="err" id="e-followers" hidden></p>')
    w("          </fieldset>")
    w("        </fieldset>")
    # details
    w('        <fieldset class="grp">')
    w(f'          <legend>{t(form["g_details"])}</legend>')
    for fid, name, typ, extra, key, ph in (
        ("f-name", "fullName", "text", 'autocomplete="name" dir="rtl"', "name", "name_ph"),
        ("f-phone", "phone", "tel", 'autocomplete="tel" inputmode="tel" dir="ltr"', "phone", "phone_ph"),
        ("f-email", "email", "email", 'autocomplete="email" inputmode="email" dir="ltr" autocapitalize="off" spellcheck="false"', "email", "email_ph"),
    ):
        short = fid[2:]
        w(f'          <div class="field" data-field="{name}">')
        w(f'            <label for="{fid}">{t(form[key])}</label>')
        w(f'            <p class="hint" id="h-{short}">{t(form[key + "_hint"])}</p>')
        w(f'            <input id="{fid}" name="{name}" type="{typ}" {extra} placeholder="{a(form[ph])}" aria-describedby="h-{short} e-{short}" required>')
        w(f'            <p class="err" id="e-{short}" hidden></p>')
        w("          </div>")
    w("        </fieldset>")
    # split
    w('        <fieldset class="grp" data-field="discountMinor" aria-describedby="h-split e-split">')
    w(f'          <legend>{t(form["g_split"])}</legend>')
    w(f'          <p class="hint" id="h-split">{t(form["split_hint"])}</p>')
    w('          <div class="split" id="split">')
    for o in options:
        checked = " checked" if o == default else ""
        w(f'            <label class="seg"><input type="radio" name="discountMinor" value="{o}"{checked}><span>{pct(split_pct(o // 100)[0])}<span class="sr-only"> הנחה</span></span></label>')
    w("          </div>")
    w('          <output class="split-out" id="split-out" for="split" aria-live="polite"></output>')
    w('          <div class="split-bar" id="split-bar" aria-hidden="true"><span class="sb-disc"></span><span class="sb-reward"></span></div>')
    w(f'          <p class="split-fixed">{ICON["info"]}<span>{t(form["split_fixed"])}</span></p>')
    w(f'          <p class="fine">{t(form["list_price"])}</p>')
    w('          <p class="err" id="e-split" hidden></p>')
    w("        </fieldset>")
    # consent
    w('        <fieldset class="grp" data-field="termsAccepted">')
    w(f'          <legend>{t(form["g_consent"])}</legend>')
    w("          <details class=\"terms-sum\">")
    w(f'            <summary>{t(form["consent_summary"])}</summary>')
    w("            <ul>")
    for item in form["consent_items"]:
        w(f"              <li>{t(item)}</li>")
    w("            </ul>")
    w(f'            <p><a href="{ROUTES["terms"]}" target="_blank" rel="noopener">{t(form["consent_terms"])}</a></p>')
    w("          </details>")
    w('          <label class="check"><input id="f-terms" name="termsAccepted" type="checkbox" aria-describedby="e-terms" required>'
      f'<span>{t(form["consent"])} (<a href="{ROUTES["terms"]}" target="_blank" rel="noopener">{t(form["consent_terms"])}</a>)</span></label>')
    w('          <p class="err" id="e-terms" hidden></p>')
    w("        </fieldset>")
    w('        <p class="form-err" id="form-err" role="alert" hidden></p>')
    w(f'        <button class="btn btn-gold btn-lg btn-block" type="submit" id="submit">{t(form["submit"])}</button>')
    w(f'        <p class="submit-note">{t(form["submit_note"])}</p>')
    w("      </form>")
    w("    </div>")
    w('    <div class="card join-card" data-view="success" hidden></div>')
    w('    <div class="card join-card" data-view="state" hidden></div>')
    w("  </div>")
    w("</section>")
    w("</main>")

    # ---------------------------------------------------------------- sticky join button (Yarin, 17 Nov 2026)
    # Phones and tablets only: on a 390px phone the hero button sits almost two screens down. The script shows the bar
    # only while neither the hero button nor the form is on screen, so there is never a second button next to the first.
    w('<div class="sticky-cta" data-sticky-cta>')
    w(f'  <a class="btn btn-gold btn-lg" href="#join" data-track="Ambassador_Sticky_CTA_Clicked">{t(hero["cta"])}</a>')
    w("</div>")

    # ---------------------------------------------------------------- footer
    f = c["footer"]
    w('<footer class="foot">')
    w('  <div class="wrap foot-in">')
    w(f'    <a class="foot-wa" href="{WHATSAPP}" target="_blank" rel="noopener">{ICON["wa"]}<span>{t(f["questions"])}</span></a>')
    w('    <nav class="foot-links" aria-label="קישורים">')
    w(f'      <a href="{ROUTES["terms"]}">{t(f["terms"])}</a>')
    w(f'      <a href="{ROUTES["dashboard"]}">{t(f["dashboard"])}</a>')
    w(f'      <a href="{ROUTES["privacy"]}">{t(f["privacy"])}</a>')
    w(f'      <a href="{INSTAGRAM}" dir="ltr" target="_blank" rel="noopener">{t(f["instagram"])}</a>')
    w("    </nav>")
    w("  </div>")
    w("</footer>")

    # ---------------------------------------------------------------- verify dialog (stand-in for the store's PhoneVerificationDialog)
    v = c["verify"]
    w('<dialog class="verify" id="verify" aria-labelledby="verify-title">')
    w('  <form method="dialog" id="verify-form" novalidate>')
    w(f'    <h2 id="verify-title">{t(v["title"])}</h2>')
    w('    <p id="verify-text"></p>')
    w(f'    <label for="f-code">{t(v["label"])}</label>')
    w('    <input id="f-code" name="code" dir="ltr" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" aria-describedby="verify-err verify-demo">')
    w('    <p class="err" id="verify-err" hidden></p>')
    w(f'    <p class="fine" id="verify-demo" data-review-only>{t(v["demo"])}</p>')
    w('    <div class="verify-btns">')
    w(f'      <button class="btn btn-gold" type="submit" id="verify-ok">{t(v["submit"])}</button>')
    w(f'      <button class="btn btn-ghost" type="button" id="verify-cancel">{t(v["cancel"])}</button>')
    w("    </div>")
    w("  </form>")
    w("</dialog>")

    # ---------------------------------------------------------------- runtime data for the script
    runtime = {
        "form": {k: form[k] for k in ("split_out_both", "split_out_none", "split_out_all", "sending", "submit", "errors")},
        "verify": v,
        "success": c["success"],
        "states": c["states"],
        "routes": ROUTES,
        "whatsapp": WHATSAPP,
        "termsVersion": P["terms_version"],
        "program": {  # static fallback; the live GET /api/ambassadors/program replaces it
            "open": True,
            "budgetMinor": budget_minor,
            "stepMinor": step_minor,
            "discountOptions": options,
            "regularPriceMinor": P["regular_price_ils"] * 100,
            "listPriceMinor": P["list_price_ils"] * 100,
            "linkWindowDays": P["link_window_days"],
            "holdDays": P["hold_days"],
        },
        "exampleDiscountMinor": EX_DISC * 100,
        "shareFallback": SHARE,
    }
    data = json.dumps(runtime, ensure_ascii=False).replace("</", "<\\/")
    w(f'<script type="application/json" id="amb-data">{data}</script>')
    w('<script src="ambassadors.js" defer></script>')
    w("</body>")
    w("</html>")

    path = os.path.join(SITE, "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"wrote {os.path.relpath(path, ROOT)}")


# Words the page script fills in at run time, shown as placeholders in the copy file.
RUNTIME = {
    "price": "[המחיר לקונה אחרי ההנחה]",
    "reward": "[האחוז שלכם]",
    "discount": "[אחוז ההנחה]",
    "name": "[שם פרטי]",
    "link": "[הקישור האישי]",
    "phone": "[מספר הוואטסאפ]",
}


def write_copy_doc():
    """copy-he.md: every visitor string in page order, numbers filled in. Generated, never edited by hand."""
    c = COPY

    def x(s):
        s = plain(s)
        s = TOKEN.sub(lambda m: RUNTIME.get(m.group(1), m.group(0)), s)
        return s.replace("|", "\\|").replace("\n", "<br>")

    out = []
    w = out.append

    def table(rows):
        w("| Element | Text |")
        w("|---|---|")
        for k, v in rows:
            w(f"| {k} | {x(v)} |")
        w("")

    def bullets(items):
        for i in items:
            w(f"- {x(i)}")
        w("")

    hero, steps, deal, ex, costs, faq, form = c["hero"], c["steps"], c["deal"], c["example"], c["costs"], c["faq"], c["form"]
    w("# Ambassador page: the full copy (Hebrew)")
    w("")
    w(f"Every visitor-facing string of the redesigned page (`sites/lumebook-ambassadors-v2`), in page order. Generated by `src/build.py` from `src/content/he.json` on every build: edit the JSON, not this file.")
    w("")
    w(f"Numbers are filled in from `shared/facts.json` `ambassador_program` (the store's terms, version `{P['terms_version']}`). On the page, the share ({pct(SHARE)}), the prices, the 7 day link window and the 14 day hold are replaced live from the store's `GET /api/ambassadors/program`. Words in [brackets] are filled in by the page while someone uses it.")
    w("")

    w("## Browser tab and sharing")
    table([("Page title", c["meta"]["title"]), ("Description", c["meta"]["description"])])

    w("## 1. First screen")
    table([("Eyebrow", hero["eyebrow"]), ("Headline (H1)", hero["h1"]), ("Lead", hero["lead"]), ("Who it is for", hero["fit"])])
    w(f"**{x(hero['get_title'])}**")
    w("")
    bullets(hero["get"])
    w(f"**{x(hero['do_title'])}**")
    w("")
    bullets(hero["do"])
    table([
        ("Cost box: question", hero["cost_title"]), ("Cost box: amount", hero["cost_value"]), ("Cost box: text", hero["cost_text"]),
        ("Cost box: condition", hero["cost_condition"]), ("Cost box: link", hero["cost_link"]),
        ("Main button", hero["cta"]), ("Sticky button on phones (same text)", hero["cta"]),
        ("Text link", hero["how_link"]), ("Under the button", hero["cta_note"]),
        ("Book covers, alt text", hero["covers_alt"]),
    ])

    w("## 2. How it works")
    table([("Heading", steps["h2"]), ("Intro", steps["intro"])])
    for n, s in enumerate(steps["items"], 1):
        w(f"**{n}. {x(s['title'])}** ({x(s['actor'])})")
        w("")
        w(x(s["text"]))
        w("")
        w(f"{x(steps['then'])} ({x(s['next_actor'])}): {x(s['next'])}")
        w("")

    w("## 3. What you get, what you give")
    table([("Heading", deal["h2"]), ("Picture caption", deal["image_note"]), ("Picture alt text", deal["image_alt"])])
    for key in ("get", "give"):
        w(f"**{x(deal[key + '_title'])}**")
        w("")
        for item in deal[key]:
            w(f"- **{x(item['t'])}**: {x(item['d'])}")
        w("")

    w("## 4. Example")
    table([("Heading", ex["h2"]), ("Intro", ex["intro"]), ("Bar, discount part", ex["bar_disc"]), ("Bar, reward part", ex["bar_reward"])])
    for n, line in enumerate(ex["steps"], 1):
        w(f"{n}. {x(line)}")
    w("")
    table([("Under the steps", ex["range"]), ("Small print", ex["note"])])
    w(f"**{x(ex['payout_title'])}** {x(ex['payout'])}")
    w("")

    w("## 5. Costs")
    w(f"**{x(costs['h2'])}**")
    w("")
    w("| Item | Amount | Detail |")
    w("|---|---|---|")
    for r in costs["rows"]:
        w(f"| {x(r['k'])} | {x(r['v'])} | {x(r['d'])} |")
    w("")
    w(x(costs["months_note"]))
    w("")

    w("## 6. Questions")
    w(f"**{x(faq['h2'])}**")
    w("")
    for item in faq["items"]:
        w(f"**{x(item['q'])}**")
        w("")
        w(x(item["a"]))
        w("")
    w(f"Link under the questions: {x(faq['more'])}")
    w("")

    w("## 7. Sign-up form")
    table([("Heading", form["h2"]), ("Intro", form["sub"]), ("Link", form["have_link"])])
    w("**Instagram**")
    w("")
    table([
        ("Group title", form["g_social"]), ("Field", form["handle"]), ("Hint", form["handle_hint"]), ("Placeholder", "@" + form["handle_ph"]),
        ("Question", form["followers"]), ("Hint", form["followers_hint"]),
    ] + [("Option", v) for v in form["bands"].values()])
    w("**Contact details**")
    w("")
    table([("Group title", form["g_details"])] + [
        row for key in ("name", "phone", "email")
        for row in ((f"Field", form[key]), ("Hint", form[key + "_hint"]), ("Placeholder", form[key + "_ph"]))
    ])
    w("**The split**")
    w("")
    opts = ", ".join(pct(split_pct(o)[0]) for o in range(0, P["budget_ils"] + 1, P["step_ils"]))
    table([
        ("Group title", form["g_split"]), ("Hint", form["split_hint"]),
        ("Buttons (discount for the buyer)", opts),
        ("Readout, part discount", form["split_out_both"]), ("Readout, no discount", form["split_out_none"]),
        ("Readout, all discount", form["split_out_all"]), ("Note", form["split_fixed"]), ("Small print", form["list_price"]),
    ])
    w("**Consent**")
    w("")
    table([("Group title", form["g_consent"]), ("Summary toggle", form["consent_summary"])])
    for n, item in enumerate(form["consent_items"], 1):
        w(f"{n}. {x(item)}")
    w("")
    table([
        ("Checkbox", form["consent"] + " (" + form["consent_terms"] + ")"), ("Button", form["submit"]),
        ("Button while sending", form["sending"]), ("Under the button", form["submit_note"]),
    ])
    w("**Error messages**")
    w("")
    err_labels = {"summary": "Summary above the form", "server_fields": "Field the server refused", "generic": "Could not save",
                  "handle_missing": "Instagram name missing", "handle_invalid": "Instagram name not valid", "followers": "Followers not chosen",
                  "name": "Name missing", "phone": "Phone not valid", "email": "Email not valid", "split": "Split not chosen", "terms": "Terms not accepted"}
    table([(err_labels.get(k, k), v) for k, v in form["errors"].items()])

    v = c["verify"]
    w("## 8. WhatsApp code window")
    w("")
    w("On the store this is the store's own verification window; these are the strings the prototype's stand-in uses.")
    w("")
    table([("Title", v["title"]), ("Text", v["text"]), ("Field", v["label"]), ("Button", v["submit"]), ("Cancel", v["cancel"]),
           ("While checking", v["processing"]), ("Wrong code", v["error"]), ("Review copy only", v["demo"])])

    s = c["success"]
    w("## 9. After sign-up")
    table([
        ("Badge, new", s["badge_new"]), ("Badge, already signed up", s["badge_existing"]),
        ("Title", s["title"]), ("Title without a name", s["title_noname"]), ("Title, already signed up", s["title_existing"]),
        ("Text", s["sub"]), ("Text, no discount chosen", s["sub_none"]), ("Text, already signed up", s["sub_existing"]),
        ("Link label", s["link_label"]), ("Buttons", s["copy"] + " / " + s["copied"] + " / " + s["share"]),
        ("Split line", s["split_line"]),
        ("Share text", s["share_text"]), ("Share text, no discount", s["share_text_none"]),
        ("Share text, all discount", s["share_text_all"]),
        ("Next steps title", s["next_title"]),
    ] + [(f"Step {n} + button", f"{it['t']} [{it['b']}]") for n, it in enumerate(s["next"], 1)] + [
        ("WhatsApp message (prefilled)", s["wa_message"]),
    ])

    st = c["states"]
    w("## 10. Other states")
    table([("Sign-up closed: title", st["closed_title"]), ("Sign-up closed: text", st["closed_text"]),
           ("Link paused: title", st["disabled_title"]), ("Link paused: text", st["disabled_text"]), ("Button", st["whatsapp"])])

    f = c["footer"]
    w("## 11. Footer")
    table([("WhatsApp", f["questions"]), ("Links", " · ".join([f["terms"], f["dashboard"], f["privacy"], f["instagram"]]))])

    w("## Review copy only (removed on the store)")
    table([("Banner", c["review"]["banner"])])

    lines = []
    for i, line in enumerate(out):  # a blank line after every heading, so every Markdown viewer draws the table
        lines.append(line)
        if line.startswith("#") and (i + 1 == len(out) or out[i + 1] != ""):
            lines.append("")
    path = os.path.join(SITE, "copy-he.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    print(f"wrote {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    build()
    write_copy_doc()
