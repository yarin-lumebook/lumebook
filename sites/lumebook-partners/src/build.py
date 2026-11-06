#!/usr/bin/env python3
"""Builds the four language versions of the partners page from src/content/<lang>.json.

Run:  python3 sites/lumebook-partners/src/build.py

Outputs (never edit these by hand, edit the JSON and rebuild; the edit button keeps its changes apart in shared/site-editor/edits/):
  sites/lumebook-partners/index.html        Hebrew  (target route /IL/he/partners)
  sites/lumebook-partners/en/index.html     English (/IL/en/partners)
  sites/lumebook-partners/ar/index.html     Arabic  (/IL/ar/partners)
  sites/lumebook-partners/ru/index.html     Russian (/IL/ru/partners)

All four share partners.css and partners.js. The form strings reach the script through a JSON block (id="i18n") in each page.
Standard library only.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
LANGS = ["he", "en", "ar", "ru"]
STORE = "https://lumebook.com/IL/{lang}"

# the store's own contact route and the inquiry address (shared/facts.json partners.inquiries_email, Yarin 06 / 11 / 2026)
FACTS = json.load(open(os.path.join(SITE, "..", "..", "shared", "facts.json"), encoding="utf-8"))
EMAIL = FACTS["partners"]["inquiries_email"]
WHATSAPP = "972559800791"


def h(s):
    return html.escape(s, quote=False)


def a(s):
    return html.escape(s, quote=True)


def load(lang):
    return json.load(open(os.path.join(HERE, "content", lang + ".json"), encoding="utf-8"))


def out_path(lang):
    return os.path.join(SITE, "index.html") if lang == "he" else os.path.join(SITE, lang, "index.html")


def prefix(lang):
    return "" if lang == "he" else "../"


def rel(frm, to):
    if frm == to:
        return "./"
    if frm == "he":
        return to + "/"
    return "../" if to == "he" else "../" + to + "/"


def page(lang, all_content):
    c = all_content[lang]
    pre = prefix(lang)
    store = STORE.format(lang=lang)
    o = []
    w = o.append

    w("<!doctype html>")
    w(f'<html lang="{lang}" dir="{c["dir"]}">')
    w("<head>")
    w('<meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
    w(f"<title>{h(c['title'])}</title>")
    w(f'<meta name="description" content="{a(c["description"])}">')
    w('<meta name="google" content="notranslate">')
    w('<meta name="theme-color" content="#FAF6EF">')
    w("<!-- REVIEW COPY: remove this robots line when the page goes live on the store. The target route is the canonical below. -->")
    w('<meta name="robots" content="noindex, nofollow">')
    w(f'<link rel="canonical" href="https://lumebook.com/IL/{lang}/partners">')
    for lg in LANGS:
        w(f'<link rel="alternate" hreflang="{all_content[lg]["hreflang"]}" href="https://lumebook.com/IL/{lg}/partners">')
    w('<link rel="alternate" hreflang="x-default" href="https://lumebook.com/IL/he/partners">')
    w('<meta property="og:type" content="website">')
    w('<meta property="og:site_name" content="Lumebook">')
    w(f'<meta property="og:locale" content="{c["locale"]}">')
    w(f'<meta property="og:url" content="https://lumebook.com/IL/{lang}/partners">')
    w(f'<meta property="og:title" content="{a(c["title"])}">')
    w(f'<meta property="og:description" content="{a(c["description"])}">')
    w('<meta property="og:image" content="https://lumebook.com/og-image.png">')
    w(f'<link rel="stylesheet" href="{pre}partners.css">')
    w("</head>")
    w("<body>")
    w(f'<a class="skip" href="#main">{h(c["skip"])}</a>')
    w("")
    flag = h(c["review_flag"]).replace("{path}", '<span class="ltr">docs/partners</span>')
    w(f'<div class="review-flag" data-review-only>{flag}</div>')
    w("")

    # header
    w('<header class="bar">')
    w('  <div class="wrap">')
    w(f'    <a class="bar-logo" href="{store}" aria-label="{a(c["logo_aria"])}"><img src="{pre}img/logo.png" alt="LumeBook" width="320" height="93"></a>')
    w(f'    <nav aria-label="{a(c["nav_aria"])}">')
    w(f'      <a class="hide-sm" href="{store}">{h(c["nav_store"])}</a>')
    w(f'      <a class="hide-sm" href="{store}/ambassadors">{h(c["nav_amb"])}</a>')
    w(f'      <a class="btn" href="#inquiry" data-track="header">{h(c["nav_cta"])}</a>')
    w("    </nav>")
    w(f'    <nav class="langs hide-sm" aria-label="{a(c["lang_aria"])}">')
    for lg in LANGS:
        cur = ' aria-current="true"' if lg == lang else ""
        w(f'      <a lang="{lg}" hreflang="{lg}" href="{rel(lang, lg)}"{cur}>{h(all_content[lg]["native_name"])}</a>')
    w("    </nav>")
    w("  </div>")
    w("</header>")
    w("")
    w('<main id="main">')

    # hero
    hero = c["hero"]
    w('<section class="hero" aria-labelledby="hero-title">')
    w('  <div class="wrap">')
    w(f'    <p class="eyebrow">{h(hero["eyebrow"])}</p>')
    w(f'    <h1 id="hero-title">{h(hero["h1"])}</h1>')
    w(f'    <p class="lede">{h(hero["lede"])}</p>')
    w('    <div class="actions">')
    w(f'      <a class="btn" href="#inquiry" data-track="hero_primary">{h(hero["cta1"])}</a>')
    w(f'      <a class="link" href="#how" data-track="hero_secondary">{h(hero["cta2"])}</a>')
    w("    </div>")
    w('    <div class="covers" aria-hidden="true">')
    for img, size in (("B41_girl.avif", 640), ("B2_boy.avif", 1024), ("B10_girl.avif", 800)):
        w(f'      <figure class="cover"><img src="{pre}img/{img}" alt="" width="{size}" height="{size}" loading="eager"></figure>')
    w("    </div>")
    w('    <div class="can-apply">')
    w(f'      <p>{h(hero["can_apply"])}</p>')
    w('      <ul class="tags">')
    for t in hero["tags"]:
        w(f"        <li>{h(t)}</li>")
    w("      </ul>")
    w("    </div>")
    w("  </div>")
    w("</section>")
    w("")

    # who
    who = c["who"]
    w('<section class="section wrap" id="who" aria-labelledby="who-title">')
    w(f'  <div class="head"><h2 id="who-title">{h(who["title"])}</h2><p>{h(who["intro"])}</p></div>')
    w('  <ul class="cards">')
    starts = ["story", "expertise"]
    tracks = ["entry_story", "entry_expertise"]
    for i, card in enumerate(who["cards"]):
        w('    <li class="card is-entry">')
        w(f'      <h3>{h(card["title"])}</h3>')
        w(f'      <p>{h(card["text"])}</p>')
        if card.get("tags"):
            w(f'      <ul class="tags" aria-label="{a(card["tags_aria"])}">')
            for t in card["tags"]:
                w(f"        <li>{h(t)}</li>")
            w("      </ul>")
        if card.get("note"):
            w(f'      <p>{h(card["note"])}</p>')
        w(f'      <a class="btn" href="#inquiry" data-start="{starts[i]}" data-track="{tracks[i]}">{h(card["btn"])}</a>')
        w("    </li>")
    w("  </ul>")
    if who.get("fine"):
        w(f'  <p class="fine">{h(who["fine"])}</p>')
    w("</section>")
    w("")

    # topics
    tp = c["topics"]
    w('<section class="section wrap" id="topics" aria-labelledby="topics-title">')
    w(f'  <div class="head"><h2 id="topics-title">{h(tp["title"])}</h2><p>{h(tp["intro"])}</p></div>')
    w('  <ul class="cards three">')
    for t, d in tp["items"]:
        w(f'    <li class="card"><h3>{h(t)}</h3><p>{h(d)}</p></li>')
    w("  </ul>")
    w("</section>")
    w("")

    # include
    inc = c["include"]
    w('<section class="section wrap" id="include" aria-labelledby="include-title">')
    w(f'  <div class="head"><h2 id="include-title">{h(inc["title"])}</h2><p>{h(inc["intro"])}</p></div>')
    w('  <ul class="cards">')
    for t, d in inc["items"]:
        w(f'    <li class="card"><h3>{h(t)}</h3><p>{h(d)}</p></li>')
    w("  </ul>")
    w(f'  <p class="note-box"><strong>{h(inc["note"])}</strong></p>')
    w("</section>")
    w("")

    # how
    hw = c["how"]
    w('<section class="section wrap" id="how" aria-labelledby="how-title">')
    w(f'  <div class="head"><h2 id="how-title">{h(hw["title"])}</h2><p>{h(hw["intro"])}</p></div>')
    w('  <ol class="steps">')
    for t, d in hw["steps"]:
        w(f"    <li><div><b>{h(t)}</b><span>{h(d)}</span></div></li>")
    w("  </ol>")
    w(f'  <p class="fine">{h(hw["fine"])}</p>')
    w("</section>")
    w("")

    # agree
    ag = c["agree"]
    w('<section class="section wrap" id="agree" aria-labelledby="agree-title">')
    w(f'  <div class="head"><h2 id="agree-title">{h(ag["title"])}</h2><p>{h(ag["intro"])}</p></div>')
    w('  <ul class="agree">')
    for t, d in ag["items"]:
        w(f"    <li><div><b>{h(t)}</b><span>{h(d)}</span></div></li>")
    w("  </ul>")
    w(f'  <p class="note-box">{h(ag["note"])}</p>')
    w("</section>")
    w("")

    # faq
    fq = c["faq"]
    w('<section class="section wrap" id="faq" aria-labelledby="faq-title">')
    w(f'  <div class="head"><h2 id="faq-title">{h(fq["title"])}</h2></div>')
    w('  <div class="faq">')
    for q, ans in fq["items"]:
        w(f"    <details><summary>{h(q)}</summary><p>{h(ans)}</p></details>")
    w("  </div>")
    w("</section>")
    w("")

    # form
    f = c["form"]
    w('<section class="section apply wrap" id="inquiry" aria-labelledby="inquiry-title">')
    w('  <div class="panel">')
    w(f'    <div class="head"><h2 id="inquiry-title">{h(f["title"])}</h2><p>{h(f["intro"])}</p></div>')
    w("    <noscript>")
    w('      <div class="result is-failure">')
    w(f'        <h3>{h(f["noscript_title"])}</h3>')
    w(f'        <p>{h(f["noscript_text"])}</p>')
    w(f'        <div class="row"><a class="btn" href="https://wa.me/{WHATSAPP}">{h(f["whatsapp"])}</a> <a class="btn btn-ghost" href="mailto:{EMAIL}"><span class="ltr">{EMAIL}</span></a></div>')
    w("      </div>")
    w("    </noscript>")
    w("")
    w(f'    <form id="partner-form" novalidate data-endpoint="" data-whatsapp="{WHATSAPP}" data-email="{EMAIL}">')
    w('      <div id="form-errors" class="form-error-summary" role="alert" tabindex="-1" hidden></div>')
    w('      <div id="form-fields">')
    w(f'        <p class="form-lead">{h(f["lead"])}</p>')
    opt = f'<span class="opt">{h(f["optional"])}</span>'

    def field(key, fid, label, inner, err, optional=False, extra=""):
        lab = f'{h(label)} {opt}' if optional else h(label)
        w(f'        <div class="field{extra}" data-field="{key}">')
        w(f'          <label for="{fid}">{lab}</label>')
        w(f"          {inner}")
        w(f'          <span class="err" id="{err}"></span>')
        w("        </div>")
        w("")

    field("fullName", "f-name", f["name"],
          '<input class="input" id="f-name" name="fullName" type="text" autocomplete="name" maxlength="100" required aria-required="true" aria-describedby="e-name">', "e-name")
    opts = f'<option value="">{h(f["field_placeholder"])}</option>' + "".join(f'<option value="{a(v)}">{h(t)}</option>' for v, t in f["field_options"])
    field("field", "f-field", f["field"],
          f'<select class="input" id="f-field" name="field" required aria-required="true" aria-describedby="e-field">{opts}</select>', "e-field")
    w('        <div class="field cond" data-field="fieldOther" id="other-wrap" hidden>')
    w(f'          <label for="f-other">{h(f["other"])}</label>')
    w('          <input class="input" id="f-other" name="fieldOther" type="text" maxlength="120" aria-describedby="e-other">')
    w('          <span class="err" id="e-other"></span>')
    w("        </div>")
    w("")
    field("email", "f-email", f["email"],
          '<input class="input" id="f-email" name="email" type="email" dir="ltr" inputmode="email" autocomplete="email" maxlength="160" placeholder="name@example.com" required aria-required="true" aria-describedby="e-email">', "e-email")
    field("whatsapp", "f-wa", f["wa"],
          '<input class="input" id="f-wa" name="whatsapp" type="tel" dir="ltr" inputmode="tel" autocomplete="tel" maxlength="24" placeholder="050 123 4567" aria-describedby="e-wa">', "e-wa", optional=True)
    field("profile", "f-profile", f["profile"],
          '<input class="input" id="f-profile" name="profile" type="text" dir="ltr" inputmode="url" autocomplete="url" maxlength="200" placeholder="example.com" aria-describedby="e-profile">', "e-profile", optional=True)

    w('        <fieldset class="field" data-field="start" aria-describedby="e-start">')
    w(f'          <legend>{h(f["start"])}</legend>')
    w('          <div class="choices">')
    for v, t, hint in f["start_options"]:
        w(f'            <label class="choice"><input type="radio" name="start" value="{v}"><span>{h(t)}<small>{h(hint)}</small></span></label>')
    w("          </div>")
    w('          <span class="err" id="e-start"></span>')
    w("        </fieldset>")
    w("")
    w('        <fieldset class="field cond" data-field="rights" id="rights-wrap" aria-describedby="h-rights e-rights" hidden>')
    w(f'          <legend>{h(f["rights"])}</legend>')
    w(f'          <span class="hint" id="h-rights">{h(f["rights_hint"])}</span>')
    w('          <div class="choices">')
    for v, t in f["rights_options"]:
        w(f'            <label class="choice"><input type="radio" name="rights" value="{v}"><span>{h(t)}</span></label>')
    w("          </div>")
    w('          <span class="err" id="e-rights"></span>')
    w("        </fieldset>")
    w("")
    w('        <div class="field" data-field="description">')
    w(f'          <label for="f-desc">{h(f["desc"])}</label>')
    w(f'          <span class="hint" id="h-desc">{h(f["desc_hint"])}</span>')
    w('          <textarea class="input" id="f-desc" name="description" rows="5" maxlength="1200" required aria-required="true" aria-describedby="h-desc e-desc c-desc"></textarea>')
    w('          <span class="counter" id="c-desc" aria-hidden="true"></span>')
    w('          <span class="err" id="e-desc"></span>')
    w("        </div>")
    w("")
    field("bookTitle", "f-title", f["book_title"],
          '<input class="input" id="f-title" name="bookTitle" type="text" maxlength="120" aria-describedby="e-title">', "e-title", optional=True)
    w('        <div class="hp" aria-hidden="true">')
    w(f'          <label for="f-company">{h(f["honeypot"])}</label>')
    w('          <input id="f-company" name="company" type="text" tabindex="-1" autocomplete="off">')
    w("        </div>")
    w("")
    w(f'        <button class="btn submit" type="submit" id="submit-btn">{h(f["submit"])}</button>')
    privacy = f'<a href="{store}/privacy-policy">{h(f["note1_link"])}</a>'
    w(f'        <p class="form-note">{h(f["note1"]).replace("{link}", privacy)}</p>')
    w(f'        <p class="form-note">{h(f["note2"])}</p>')
    w("      </div>")
    w("")
    w('      <div id="form-result" class="result" tabindex="-1" hidden></div>')
    w("    </form>")
    w('    <p class="visually-hidden" id="live" role="status" aria-live="polite"></p>')
    w("  </div>")
    w("</section>")
    w("")

    # closing
    cl = c["closing"]
    w('<section class="closing wrap" aria-labelledby="closing-title">')
    w(f'  <h2 id="closing-title">{h(cl["title"])}</h2>')
    w(f'  <p>{h(cl["text"])}</p>')
    w('  <div class="actions">')
    w(f'    <a class="btn" href="#inquiry" data-track="closing">{h(cl["cta"])}</a>')
    w(f'    <a class="link" href="https://wa.me/{WHATSAPP}" data-track="closing_whatsapp">{h(cl["wa"])}</a>')
    w("  </div>")
    w("</section>")
    w("")
    w("</main>")
    w("")

    # footer
    ft = c["footer"]
    w('<footer class="foot">')
    w('  <div class="wrap">')
    w(f'    <p>{h(ft["disclaimer"])}</p>')
    w(f'    <nav aria-label="{a(ft["nav_aria"])}">')
    w(f'      <a href="{store}">{h(ft["store"])}</a>')
    w(f'      <a href="{store}/ambassadors">{h(ft["amb"])}</a>')
    w(f'      <a href="{store}/privacy-policy">{h(ft["privacy"])}</a>')
    w(f'      <a href="mailto:{EMAIL}"><span class="ltr">{EMAIL}</span></a>')
    w("    </nav>")
    w('    <nav class="langs" aria-label="' + a(c["lang_aria"]) + '">')
    for lg in LANGS:
        cur = ' aria-current="true"' if lg == lang else ""
        w(f'      <a lang="{lg}" hreflang="{lg}" href="{rel(lang, lg)}"{cur}>{h(all_content[lg]["native_name"])}</a>')
    w("    </nav>")
    w("  </div>")
    w("</footer>")
    w("")

    # strings for partners.js
    js = dict(c["js"])
    js["lang"] = lang
    js["labels"] = {
        "field": {v: t for v, t in f["field_options"]},
        "start": {v: t for v, t, _ in f["start_options"]},
        "rights": {v: t for v, t in f["rights_options"]},
    }
    js["counter"] = f["counter"]
    blob = json.dumps(js, ensure_ascii=False).replace("</", "<\\/")
    w(f'<script type="application/json" id="i18n">{blob}</script>')
    w(f'<script src="{pre}partners.js"></script>')
    w("</body>")
    w("</html>")
    return "\n".join(o) + "\n"


def main():
    all_content = {lg: load(lg) for lg in LANGS}
    for lg in LANGS:
        p = out_path(lg)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        text = page(lg, all_content)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {os.path.relpath(p, os.path.join(SITE, '..', '..'))} ({len(text):,} bytes)")


if __name__ == "__main__":
    main()
