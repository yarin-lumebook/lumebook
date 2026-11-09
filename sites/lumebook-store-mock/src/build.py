#!/usr/bin/env python3
"""Build the store mock: lumebook.com/IL/he rebuilt as a landing page in the LumeBook design system (09 Nov 2026).

Yarin, 09 / 11 / 2026, in order: "take the website https://lumebook.com/IL/he and create a mock version using the design
system of the dashboard"; "you can change and move elements as you wish for it to have the best possible landing page
structure driving people to start designing their own book and sell"; "Yes, deploy it" (the Vercel review copy);
"i dont need the side bar"; "this part doesnt look good" (the violet Hanukkah capsule); "make it dark mode and magical using
the purple of the original website"; "heavily animate"; "add icons and images as much as you can"; "show deals not the
delivery" and "usual price 149" (the price section).

So this page is the one exception to the project's white-only rule: the lb- components of shared/design/lumebook.css with
page tokens in the store's own night purple and gold (read from lumebook.com's :root on 09 / 11 / 2026: --ink #0B0518,
--ink-1 #130827, --ink-2 #1D1039, --ink-3 #291852, gold #F3D9A1 / #E6B762 / #C9954A, cream #F8F0E1). No project nav.

    python3 tools/lumebook.py build store-mock      # or: python3 sites/lumebook-store-mock/src/build.py

Source: content.json in this folder. Outputs: ../index.html (the project server; always animates, like the internal pages
ignore Reduce Transparency, because Yarin's Mac has Reduce Motion on) and ../web/index.html (the Vercel review copy: honours
Reduce Motion unless ?motion=full, noindex nofollow, canonical lumebook.com/IL/he, no local-links map, no design comments).
Pictures are not copied: covers, customer photos, the hero books, Lume, the banner and the logo load from lumebook.com.
The build fails on an em or en dash, the brand spelt with a yod, a category the store-shelves set in
shared/design/categories.json does not know, or a book id without an entry. Standard library only.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SITE))
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
import design  # noqa: E402

SRC = os.path.join(HERE, "content.json")
OUT = os.path.join(SITE, "index.html")                 # the project server
OUT_WEB = os.path.join(SITE, "web", "index.html")      # the Vercel review copy (deploy dir web/)
PAGE = "sites/lumebook-store-mock/index.html"
CAT_SET = "store-shelves"
SHOW = 12          # books on the shelf before "עוד N ספרים"
GENDER = {"g": "girl", "b": "boy"}
HONOR = '<script>document.documentElement.setAttribute("data-honor-transparency","")</script>'


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def check(c):
    bad = []

    def walk(o, path):
        if isinstance(o, str):
            if re.search("[–—]", o):
                bad.append(f"{path}: em or en dash")
            if "לומיבוק" in o:
                bad.append(f"{path}: the brand is לומבוק in our pages (or LumeBook)")
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(c, "content")
    known = design.categories(CAT_SET)
    for cat in c["categories"]:
        if cat["key"] not in known:
            bad.append(f"category {cat['key']}: not in {CAT_SET} (shared/design/categories.json)")
        for i in cat["ids"]:
            if str(i) not in c["books"]:
                bad.append(f"category {cat['key']}: book {i} has no entry in books")
    for row in c["marquee"]["rows"]:
        for i in row:
            if str(i) not in c["books"]:
                bad.append(f"marquee: book {i} has no entry in books")
    if bad:
        sys.exit("store mock: content.json has problems:\n  " + "\n  ".join(bad))


def head_for(public):
    """design.head without the project nav (Yarin: "i dont need the side bar"). The dark glass needs its own tokens, so the
    Reduce Transparency switch (data-honor-transparency, which would turn every card white) is left out on both copies.
    The public copy also drops what only we should read: the local-links map and the design system's comments."""
    h = design.head(nav=False).replace(HONOR, "")
    if public:
        h = h.replace(design.local_links_script(), "")
        s, e = h.index("<style>"), h.index("</style>")
        style = re.sub(r"\n\s*\n+", "\n", re.sub(r"/\*.*?\*/", "", h[s:e], flags=re.S))
        h = h[:s] + style + h[e:]
    return h


def boot(force):
    """Runs first: the night tokens, and the motion classes. st-anim turns the motion on; st-full also brings it back where
    the system asks for reduced motion (lumebook.css then cuts every animation to .01ms). force: the local copy."""
    return ("<script>(function(){var d=document.documentElement;var th='dark';try{var t=/[?&]theme=(light|dark)/.exec(location.search);if(t)localStorage.setItem('st-theme',t[1]);th=localStorage.getItem('st-theme')||'dark';}catch(e){}"
            "if(th!=='light')d.classList.add('st-night');var m=document.querySelector('meta[name=theme-color]');if(m)m.content=th==='light'?'#FFFFFF':'#0B0518';var full=" + ("true" if force else "false") + ";"
            "try{var q=/[?&]motion=(full|auto)/.exec(location.search);if(q){if(q[1]==='full')localStorage.setItem('lb-motion','full');else localStorage.removeItem('lb-motion');}"
            "full=full||localStorage.getItem('lb-motion')==='full';}catch(e){}"
            "var calm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;"
            "if(full||!calm)d.classList.add('st-anim');if(full&&calm)d.classList.add('st-full');})();</script>")


def build():
    with open(SRC, encoding="utf-8") as f:
        c = json.load(f)
    check(c)
    store = c["store"].rstrip("/")
    wizard = c["wizard"]
    books, cats, hero = c["books"], c["categories"], c["hero"]
    hues = design.categories(CAT_SET)
    bh = c["books_head"]

    def url(p):
        return store + p if p.startswith("/") else p

    def ext(href, cls="", inner="", extra=""):
        klass = ' class="' + cls + '"' if cls else ""
        return f'<a{klass} href="{esc(url(href))}" target="_blank" rel="noopener"{extra}>{inner}</a>'

    def ic(name, cls=""):
        return design.icon(name, cls)

    def cover(i, g=None):
        g = g or books[str(i)][1]
        if len(books[str(i)]) > 3:
            g = "b"
        return f"{store}/book_covers/{GENDER[g]}/B{i}_{GENDER[g]}.webp"

    def img(src, cls="", alt="", extra=""):
        return f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="{esc(url(src))}" alt="{esc(alt)}" loading="lazy" decoding="async"{extra}>'

    def cta(label, extra=""):
        return (f'<a class="lb-btn st-cta{extra}" href="{esc(wizard)}" target="_blank" rel="noopener" data-cta>'
                f'<span data-cta-label>{esc(label)}</span>{ic("arrow-left")}</a>')

    def rv(i):
        return f' style="--i:{i}"'

    # ---------- the shelf: one card per book, in the order of the first category it appears in ----------
    order = []
    for cat in cats:
        for i in cat["ids"]:
            if i not in order:
                order.append(i)
    first = cats[0]["ids"]
    cards = []
    for i in order:
        title, g, best = books[str(i)][:3]
        only = len(books[str(i)]) > 3
        in_cats = " ".join(cat["key"] for cat in cats if i in cat["ids"])
        pos = first.index(i) if i in first else None
        hidden = "" if pos is not None and pos < SHOW else " hidden"
        style = f' style="order:{pos}"' if pos is not None else ""
        best_chip = f'<span class="lb-chip st-best">{ic("sparkle")}{esc(bh["best"])}</span>' if best else ""
        cards.append(
            f'<a class="lb-card is-flush st-book" href="{store}/IL/he/books/{i}" target="_blank" rel="noopener" data-id="{i}" data-cats="{in_cats}"{style}{hidden}>'
            f'<span class="st-cover"><img src="{cover(i, g)}" alt="" loading="lazy" decoding="async" data-book="{i}"{" data-only" if only else ""}></span>'
            f'<span class="st-book-body"><b class="st-book-title">{esc(title)}</b>'
            f'<span class="st-book-foot">{best_chip}<span class="st-go">{esc(bh["card_cta"])}{ic("arrow-left")}</span></span></span></a>')
    chips = "".join(
        f'<button type="button" class="lb-chip cat no-swatch lb-cat-{hues[cat["key"]]["cat"]}" data-cat="{cat["key"]}" aria-pressed="{"true" if n == 0 else "false"}">'
        f'{ic(cat.get("icon", "book"))}{esc(cat["label"])}<span class="st-n">{len(cat["ids"])}</span></button>' for n, cat in enumerate(cats))
    gender_seg = ('<div class="lb-segmented st-g" role="group" aria-label="בן או בת">'
                  '<button type="button" data-g="b" aria-pressed="false">בן</button>'
                  '<button type="button" data-g="g" aria-pressed="false">בת</button></div>')

    # ---------- hero ----------
    toc = "".join(f'<a href="{h}">{esc(t)}</a>' for h, t in c["toc"])
    checks = "".join(f'<li>{ic("check")}<span>{esc(t)}</span></li>' for t in hero["checks"])
    minis = "".join(
        f'<img class="st-mini m{n + 1}" src="{esc(url(src))}" alt="" decoding="async" style="--r:{r}deg">'
        for n, (src, r) in enumerate(zip(hero["books"], (-11, 9, -7))))

    # ---------- numbers, marquee ----------
    stats = []
    for n, s in enumerate(c["stats"]):
        ltr = " lb-ltr" if not re.search("[֐-׿]", s["value"]) else ""
        stats.append(
            f'<div class="lb-metric st-rv"{rv(n)}><dt class="lb-metric-label"><span class="lb-tile is-soft st-gold-tile">{ic(s["icon"])}</span>{esc(s["label"])}</dt>'
            f'<dd class="lb-metric-value{ltr}"><span class="st-num" data-count="{s["count"]}" data-dec="{s.get("dec", 0)}" '
            f'data-prefix="{esc(s.get("prefix", ""))}" data-suffix="{esc(s.get("suffix", ""))}">{esc(s["value"])}</span></dd></div>')
    mq = c["marquee"]

    def mq_items(row, dup):
        hide = ' aria-hidden="true" tabindex="-1"' if dup else ""
        return "".join(ext(f"/IL/he/books/{i}", "st-mq-item", img(cover(i), alt="" if dup else books[str(i)][0]), hide) for i in row)
    mq_rows = "".join(
        f'<div class="st-mq-row{" is-rev" if n else ""}"><div class="st-mq-track">{mq_items(row, False)}{mq_items(row, True)}</div></div>'
        for n, row in enumerate(mq["rows"]))

    # ---------- how ----------
    how = c["how"]

    def visual(v):
        if "covers" in v:
            return '<span class="st-fan">' + "".join(img(cover(i), "", "", f' style="--k:{k - 1}"') for k, i in enumerate(v["covers"])) + "</span>"
        if "icon" in v:
            return f'<span class="st-upload"><i></i>{ic(v["icon"])}</span>'
        cls = "st-step-photo" if "/ugc/" in v["img"] else "st-step-book"
        return img(v["img"], cls)
    steps = "".join(
        f'<li class="lb-card st-step st-rv"{rv(n)}><div class="st-step-vis">{visual(v)}</div>'
        f'<div class="st-step-head"><span class="lb-disc lg st-disc">{n + 1}</span><span class="lb-tile is-soft st-gold-tile">{ic(icn)}</span></div>'
        f'<h3>{esc(t)}</h3><p class="lb-muted">{esc(d)}</p></li>'
        for n, ((t, d), v, icn) in enumerate(zip(how["steps"], how["visuals"], how["icons"])))

    # ---------- proof, why ----------
    proof = c["proof"]

    def ugc(dup):
        hide = ' aria-hidden="true"' if dup else ""
        return "".join(
            f'<figure class="lb-media st-ugc-item"{hide}><div class="lb-media-frame is-4x5">{img(src, alt="" if dup else t)}</div>'
            f'<figcaption class="lb-media-body"><span class="lb-media-title">{ic("heart")}{esc(t)}</span></figcaption></figure>' for src, t in proof["items"])
    stars = "".join(f'<i style="--i:{n}">★</i>' for n in range(5))
    why = c["why"]
    why_cards = "".join(
        f'<div class="lb-card st-why-card st-rv"{rv(n)}><span class="lb-tile lg is-soft st-gold-tile st-bob" style="--d:{n * 0.6:.1f}s">{ic(icn)}</span>'
        f'<h3>{esc(t)}</h3><p class="lb-muted">{esc(d)}</p></div>' for n, (icn, t, d) in enumerate(why["items"]))

    # ---------- price and deals ----------
    pr = c["price"]
    includes = "".join(f'<li>{ic("check")}<span>{esc(t)}</span></li>' for t in pr["includes"])

    def deal_vis(dl):
        if "covers" in dl:
            return '<span class="st-deal-covers">' + "".join(img(cover(i), "", "", f' style="--k:{k}"') for k, i in enumerate(dl["covers"])) + "</span>"
        return img(dl["img"], "st-deal-img")
    deals = "".join(
        ext(dl.get("href", wizard), "lb-card st-deal st-rv",
            f'<span class="st-deal-vis">{deal_vis(dl)}</span>'
            f'<span class="st-deal-body"><span class="st-deal-title"><span class="lb-tile is-soft st-gold-tile">{ic(dl["icon"])}</span><b>{esc(dl["title"])}</b></span>'
            f'<small>{esc(dl["text"])}</small></span><span class="st-deal-badge">{esc(dl["badge"])}</span>', rv(n) + (' data-extra' if n == 0 else ''))
        for n, dl in enumerate(pr["deals"]))

    # ---------- faq, final, more, footer ----------
    faq = c["faq"]
    help_links = '<span class="lb-row st-help">' + "".join(ext(h, "lb-btn secondary sm", ic("whatsapp" if "wa.me" in h else "mail") + f"<span>{esc(t)}</span>") for t, h in faq["help_links"]) + "</span>"
    faqs = "".join(
        f'<details class="lb-disclosure st-rv"{rv(n)}{" open" if n == 0 else ""}><summary><span class="lb-tile is-soft st-gold-tile">{ic(icn)}</span><span class="lb-sum">{esc(q)}</span></summary>'
        f'<div class="lb-disclosure-body"><p>{esc(a)}</p>{help_links if n == len(faq["items"]) - 1 else ""}</div></details>'
        for n, ((q, a), icn) in enumerate(zip(faq["items"], faq["icons"])))
    fin, more = c["final"], c["more"]
    fam, guides = more["family"], more["guides"]
    fam_links = "".join(
        ext(h, "lb-group-row", f'<span class="lb-tile is-soft st-gold-tile">{ic(icn)}</span><span class="st-grow">{esc(t)}</span>{ic("arrow-left")}')
        for (t, h), icn in zip(fam["links"], fam["icons"]))
    guide_links = "".join(
        ext(h, "lb-group-row", f'{img(cv, "st-guide-img")}<span class="st-guide"><span>{esc(t)}</span><small>{ic("clock")}{esc(m)}</small></span>{ic("arrow-left")}')
        for (t, h, m), cv in zip(guides["items"], guides["covers"]))
    ficons = c["footer_icons"]
    foot_cols = "".join(
        f'<nav class="st-foot-col" aria-label="{esc(h)}"><b>{esc(h)}</b>'
        + "".join(ext(href, "", (ic(ficons[t]) if t in ficons else "") + f"<span>{esc(t)}</span>") for t, href in links) + "</nav>"
        for h, links in c["footer"])

    y, m, d = c["read_on"].split("-")
    client = {"cats": {cat["key"]: {"ids": cat["ids"], "href": url(cat["href"])} for cat in cats}, "show": SHOW,
              "store": store, "more": bh["more"], "cta": hero["cta"], "cta_named": hero["cta_named"], "tag": hero["tag_default"],
              # the working demo
              "books": {k: v for k, v in books.items() if not k.startswith("_")},
              "catLabel": {cat["key"]: cat["label"] for cat in cats},
              "catCls": {cat["key"]: f"lb-cat-{hues[cat['key']]['cat']}" for cat in cats},
              "catByHref": {cat["href"].rstrip("/").split("/")[-1]: cat["key"] for cat in cats},
              "price": 119, "was": 149, "extra": 99, "best": bh["best"],
              "pages": {"b": "/hero/series3-transparent-768.avif", "g": "/hero/series5-transparent-768.avif", "lume": hero["lume"]},
              "demo": c["demo"], "theme": c["theme"]}
    dm = c["demo"]
    demo_html = DEMO_HTML.format(
        i_x=ic("close"), i_back=ic("arrow-right"), i_fwd=ic("arrow-left"), i_spark=ic("sparkle"), i_up=ic("upload"), i_book=ic("book"), i_gift=ic("gift"),
        i_check=ic("check"), i_info=ic("info"), i_out=ic("open-out"), i_clock=ic("clock"), i_heart=ic("heart"),
        steps="".join(f'<li><b>{n + 1}</b><span>{esc(s)}</span></li>' for n, s in enumerate(dm["steps"])),
        book_deals="".join(f'<li>{ic("check")}<span>{esc(t)}</span></li>' for t in dm["book_deals"]),
        **{k: esc(v) for k, v in dm.items() if isinstance(v, str)})

    def render(public):
        notice = esc(c["notice_public" if public else "notice"]).replace("{date}", f'<span class="lb-ltr">{d} / {m} / {y}</span>')
        chip = c["mock_chip_public" if public else "mock_chip"]
        if public:
            meta = ('<!-- REVIEW COPY for the store team: never indexed, the real page is the canonical -->\n'
                    '<meta name="robots" content="noindex, nofollow">\n'
                    f'<link rel="canonical" href="{store}/IL/he">\n<title>הצעה לדף הבית · LumeBook</title>')
        else:
            meta = '<meta name="robots" content="noindex">\n<title>החנות בעיצוב שלנו · לומבוק</title>'
        return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0B0518">
{meta}
{boot(not public)}
{head_for(public)}
<style>{CSS}</style>
</head>
<body>
<div class="st-sky" aria-hidden="true"><i class="st-aurora a1"></i><i class="st-aurora a2"></i><i class="st-aurora a3"></i><i class="st-stars s1"></i><i class="st-stars s2"></i><i class="st-shoot sh1"></i><i class="st-shoot sh2"></i><i class="st-shoot sh3"></i><div class="st-motes" id="st-motes"></div></div>
<div class="st-progress" aria-hidden="true"><i id="st-progress"></i></div>
<div class="st" translate="no">
  {ext(c["promo"]["href"], "st-promo", ic(c["promo"].get("icon", "gift"), "st-wiggle") + f'<span class="st-shine-text">{esc(c["promo"]["text"])}</span><span class="st-promo-link"><span class="st-promo-l">{esc(c["promo"]["link"])}</span>{ic("arrow-left")}</span>')}
  <div class="lb-topbar lb-edge has-toc st-bar"><div class="lb-topbar-in">
    {ext("/IL/he", "lb-brand st-logo", f'<picture><source media="(max-width: 640px)" srcset="{store}/logo_squre-96.webp"><img src="{store}/logo_wide_small.avif" alt="LumeBook" width="549" height="160"></picture>')}
    <a class="lb-chip st-mock" href="#st-notice">{ic("info")}{esc(chip)}</a>
    <nav class="lb-toc" aria-label="בדף">{toc}</nav>
    <button class="lb-btn secondary icon st-theme" type="button" id="st-theme" aria-label="{esc(c["theme"]["to_light"])}">{ic("sun", "i-sun")}{ic("moon", "i-moon")}</button>
    <button class="lb-btn secondary st-my-btn" type="button" data-my>{ic("book")}<span class="st-my-l">{esc(dm["my_books"])}</span><b class="st-my-n" id="st-my-n">0</b></button>
    <a class="lb-btn st-bar-cta" href="{esc(wizard)}" target="_blank" rel="noopener" data-cta>{ic("sparkle")}<span class="st-cta-long">{esc(hero["cta"])}</span><span class="st-cta-short">{esc(hero["cta_short"])}</span><span class="st-cta-tiny">{esc(hero["cta_tiny"])}</span></a>
  </div></div>
  <main class="lb-page">
    <header class="lb-hero has-media st-hero">
      <div class="lb-hero-text">
        <span class="lb-chip accent st-l" style="--i:0">{ic("sparkle")}{esc(hero["chip"])}</span>
        <h1><span class="st-l" style="--i:1">{esc(hero["h1"][0])}</span><span class="st-l" style="--i:2"><span class="st-gold">{esc(hero["h1"][1])}</span></span></h1>
        <p class="lb-lede st-l" style="--i:3">{esc(hero["lede"])}</p>
        <div class="st-l" style="--i:4"><div class="lb-card st-start">
          <label class="st-field" for="st-name">{ic("pencil")}{esc(hero["form_label"])}</label>
          <div class="st-start-row">
            <input class="lb-input" id="st-name" type="text" dir="rtl" maxlength="20" autocomplete="off" enterkeyhint="go" placeholder="{esc(hero["form_placeholder"])}">
            {gender_seg}
          </div>
          {cta(hero["cta"], " is-wide")}
          <ul class="st-checks">{checks}</ul>
        </div></div>
        <p class="st-price st-l" style="--i:5"><span class="st-price-row"><b>{esc(hero["price"])}</b><s>{esc(hero["was"])}</s></span><small>{ic("gift")}{esc(hero["price_note"])}</small></p>
      </div>
      <div class="st-stage" id="st-stage">
        <i class="st-halo"></i>
        {minis}
        <img class="st-main" src="{esc(url(hero["image"]))}" alt="{esc(hero["image_alt"])}" width="768" height="768" fetchpriority="high">
        <img class="st-lume" src="{esc(url(hero["lume"]))}" alt="" decoding="async">
        <i class="st-orbit"><b></b><b></b><b></b><b></b><b></b></i>
        <span class="lb-glass is-thick is-capsule st-tag" id="st-tag">{ic("sparkle")}<b data-name>{esc(hero["tag_default"])}</b> {esc(hero["tag_suffix"])}</span>
      </div>
    </header>
    <dl class="lb-metrics st-stats">{"".join(stats)}</dl>

    <section class="st-marquee st-rv" aria-label="ספרים בחנות">
      <p class="st-mq-cap">{ic("sparkle")}{esc(mq["caption"])}</p>
      {mq_rows}
    </section>

    <section class="lb-section st-books" id="books">
      <div class="lb-section-head st-rv"><h2>{ic("book", "st-h-ic")}{esc(bh["h2"])}</h2><span class="lb-meta">{esc(bh["meta"])}</span></div>
      <div class="st-filters st-rv">
        <div class="st-cats" role="group" aria-label="נושאים">{chips}</div>
        <div class="st-gwrap"><span class="st-gl">{esc(bh["covers"])}</span>{gender_seg}</div>
      </div>
      <div class="st-shelf" id="st-shelf">{"".join(cards)}</div>
      <div class="st-shelf-foot">
        <button class="lb-btn secondary" id="st-more" type="button">{esc(bh["more"].format(n=max(0, len(first) - SHOW)))}</button>
        <a class="lb-btn ghost" id="st-all" href="{esc(url(cats[0]["href"]))}" target="_blank" rel="noopener">{esc(bh["all"])}{ic("arrow-left")}</a>
      </div>
    </section>

    <section class="lb-section st-how" id="how">
      <div class="lb-section-head st-rv"><h2>{ic("compass", "st-h-ic")}{esc(how["h2"])}</h2></div>
      <ol class="lb-grid st-steps" style="--min: 13rem">{steps}</ol>
      <div class="st-center st-rv">{cta(how["cta"])}</div>
    </section>

    <section class="lb-section st-proof" id="proof">
      <div class="lb-section-head st-rv"><h2>{ic("heart", "st-h-ic")}{esc(proof["h2"])}</h2><span class="lb-meta">{esc(proof["meta"])}</span></div>
      <div class="st-proof-grid">
        <figure class="lb-card is-accent st-quote st-rv">
          <span class="st-stars-row" aria-label="{esc(proof["rating"])}">{stars}</span>
          <blockquote>{esc(proof["quote"])}</blockquote>
          <figcaption>{esc(proof["quote_by"])} · <span class="lb-dim">{esc(proof["rating"])}</span></figcaption>
          {cta(proof["cta"])}
        </figure>
        <div class="st-ugc-row st-rv"><div class="st-ugc-track">{ugc(False)}{ugc(True)}</div></div>
      </div>
    </section>

    <section class="lb-section st-why" id="why">
      <div class="lb-section-head st-rv"><h2>{ic("eye", "st-h-ic")}{esc(why["h2"])}</h2></div>
      <figure class="st-banner st-rv">{img(why["banner"], "", why["banner_alt"])}</figure>
      <div class="lb-grid" style="--min: 13rem">{why_cards}</div>
    </section>

    <section class="lb-section st-pricing" id="price">
      <div class="lb-section-head st-rv"><h2>{ic("gift", "st-h-ic")}{esc(pr["h2"])}</h2></div>
      <div class="st-price-grid">
        <div class="lb-card is-accent st-offer st-rv">
          <div class="st-offer-top">
            {img(cover(pr["cover"]), "st-offer-cover")}
            <div class="st-offer-head">
              <span class="st-offer-label">{ic("book")}{esc(pr["label"])}</span>
              <div class="st-amount"><b><span class="st-gold">{esc(pr["amount"])}</span></b><span class="st-was"><small>{esc(pr["was_label"])}</small><s>{esc(pr["was"])}</s></span></div>
              <div class="lb-row"><span class="lb-chip st-best">{ic("sparkle")}{esc(pr["save"])}</span><span class="lb-chip accent">{ic("clock")}{esc(pr["amount_note"])}</span></div>
            </div>
          </div>
          <ul class="st-checks">{includes}</ul>
          {cta(pr["cta"], " is-wide")}
          <small class="st-cta-note">{ic("check-circle")}{esc(pr["cta_note"])}</small>
        </div>
        <div class="lb-stack st-deals">
          <h3 class="st-rv">{ic("sparkle")}{esc(pr["deals_h3"])}</h3>
          {deals}
        </div>
      </div>
    </section>

    <section class="lb-section st-faq" id="faq">
      <div class="lb-section-head st-rv"><h2>{ic("chat", "st-h-ic")}{esc(faq["h2"])}</h2></div>
      <div class="lb-disclosures">{faqs}</div>
    </section>

    <section class="st-final st-rv">
      <i class="st-final-glow"></i>
      {img(fin["lume"], "st-final-lume")}
      <div class="lb-card is-glass st-final-card">
        <h2>{esc(fin["h2"])}</h2>
        <p class="lb-lede">{esc(fin["lede"])}</p>
        <div class="lb-row st-final-row">{cta(fin["cta"])}{ext(fin["secondary_href"], "lb-btn secondary st-cta-2", ic("book") + esc(fin["secondary"]))}</div>
      </div>
    </section>

    <section class="lb-section st-more">
      <div class="lb-section-head st-rv"><h2>{ic("layers", "st-h-ic")}{esc(more["h2"])}</h2></div>
      <div class="lb-grid cols-2">
        <div class="lb-card st-rv"><h3>{esc(fam["h3"])}</h3><p class="lb-muted">{esc(fam["text"])}</p><div class="lb-group">{fam_links}</div></div>
        <div class="lb-card st-rv" style="--i:1"><h3>{esc(guides["h3"])}</h3><div class="lb-group">{guide_links}</div>{ext(guides["all"][1], "st-groups", esc(guides["all"][0]) + ic("arrow-left"))}</div>
      </div>
    </section>

    <footer class="lb-footer st-foot">
      <div class="st-foot-cols">{foot_cols}</div>
      <div class="lb-callout info has-icon st-notice" id="st-notice">{ic("info")}<p>{notice} {ext("/IL/he", "", "לחנות כפי שהיא", " data-real")}</p></div>
      <p>{esc(c["copyright"])}</p>
    </footer>
  </main>
{demo_html}
</div>
<script>window.ST_DATA = {design._js(client)};</script>
{JS}
</body>
</html>
"""

    os.makedirs(os.path.dirname(OUT_WEB), exist_ok=True)
    for path, public in ((OUT, False), (OUT_WEB, True)):
        page = render(public)
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"wrote {os.path.relpath(path, ROOT)}: {len(order)} books in {len(cats)} categories, {len(page):,} bytes")


# Page CSS: the lb- components with this page's night tokens; st- is this page's prefix. Colours are the store's own
# (lumebook.com :root, 09 / 11 / 2026), never the carousel slide variables (--lb-ink and friends).
CSS = r"""
@property --st-ang { syntax: "<angle>"; initial-value: 0deg; inherits: false; }

/* ---------- the page's own colour slots: light defaults (the design system's white tokens underneath), night below ---------- */
html {
  --st-gold: linear-gradient(135deg, #F3D9A1 0%, #E6B762 50%, #C9954A 100%); --st-on-gold: #1A0D33;
  --st-gold-text: linear-gradient(135deg, #C9954A 0%, #A87425 55%, #8A5A14 100%);
  --st-gold-shine: linear-gradient(90deg, #8A5A14 0%, #C9954A 22%, #E6B762 34%, #A87425 50%, #C9954A 72%, #8A5A14 100%);
  --st-well: rgba(91, 43, 214, .06); --st-final-bg: linear-gradient(180deg, #F7F2FF, #FFFFFF); --st-chip-bg: rgba(255, 255, 255, .85);
  --st-inset: inset 0 1px 2px rgba(41, 30, 22, .08);
  --st-promo-bg: linear-gradient(90deg, #FBEBC9, #F6DFAE, #FBEBC9); --st-promo-ink: #8A5A14;
  --st-promo-shine: linear-gradient(90deg, #8A5A14 0%, #C9954A 25%, #8A5A14 50%, #C9954A 75%, #8A5A14 100%);
  --st-sky: radial-gradient(120% 80% at 50% -10%, #EEE6FF 0%, #FBF8FF 45%, #FFFFFF 75%); --st-aurora-op: .4;
}
html.st-night {
  --st-gold-text: var(--st-gold);
  --st-gold-shine: linear-gradient(90deg, #C9954A 0%, #F3D9A1 22%, #FFF6DF 34%, #E6B762 50%, #F3D9A1 72%, #C9954A 100%);
  --st-well: rgba(11, 5, 24, .38); --st-final-bg: rgba(19, 8, 39, .6); --st-chip-bg: rgba(11, 5, 24, .65);
  --st-inset: var(--st-inset);
  --st-promo-bg: linear-gradient(90deg, rgba(41, 24, 82, .85), rgba(58, 34, 114, .9), rgba(41, 24, 82, .85)); --st-promo-ink: #F3D9A1;
  --st-promo-shine: linear-gradient(90deg, #E6B762 0%, #FFF3D6 25%, #E6B762 50%, #FFF3D6 75%, #E6B762 100%);
  --st-sky: radial-gradient(120% 80% at 50% -10%, #291852 0%, #130827 45%, #0B0518 80%); --st-aurora-op: .75;
}
/* ---------- night tokens: the design system's names, the store's purple and gold ---------- */
html.st-night {
  color-scheme: dark;
  --bg: #0B0518; --surface: #130827; --surface-2: #1D1039; --surface-sunk: #0B0518; --sidebar: #130827; --sidenav: #0B0518;
  --text: #F8F0E1; --text-2: #D3CABA; --text-3: #A89F90; --text-on-tint: #1A0D33;
  --fill: rgba(248, 240, 225, .06); --fill-2: rgba(248, 240, 225, .1); --fill-3: rgba(248, 240, 225, .16);
  --line: rgba(230, 183, 98, .14); --line-strong: rgba(230, 183, 98, .3);
  --tint: #C2AAFF; --tint-hover: #DCCFFF; --tint-soft: rgba(194, 170, 255, .16); --focus: rgba(230, 183, 98, .65);
  --accent: #E6B762; --accent-soft: rgba(230, 183, 98, .16); --accent-ink: #F3D9A1;
  --success: #74E3A8; --success-soft: rgba(116, 227, 168, .14); --info: #A9BDFF; --info-soft: rgba(169, 189, 255, .13);
  --warning: #FFB86E; --warning-soft: rgba(255, 184, 110, .15); --danger: #FF8A93; --danger-soft: rgba(255, 138, 147, .14);
  --cat-1-ink: #FFB877; --cat-1-soft: rgba(234, 122, 13, .2);  --cat-2-ink: #FF98BD; --cat-2-soft: rgba(224, 69, 123, .2);
  --cat-3-ink: #7BE6A5; --cat-3-soft: rgba(46, 157, 87, .22); --cat-4-ink: #9CC2FF; --cat-4-soft: rgba(47, 116, 219, .22);
  --cat-5-ink: #DAAEFF; --cat-5-soft: rgba(155, 79, 214, .24); --cat-6-ink: #74E6E2; --cat-6-soft: rgba(18, 156, 154, .22);
  --cat-7-ink: #C6CDDA; --cat-7-soft: rgba(93, 102, 119, .3);  --cat-8-ink: #F5D07E; --cat-8-soft: rgba(197, 139, 34, .24);
  --shadow-1: 0 1px 2px rgba(0, 0, 0, .4); --shadow-2: 0 14px 36px -14px rgba(0, 0, 0, .75); --shadow-3: 0 30px 70px -24px rgba(0, 0, 0, .85);
  --bar: rgba(11, 5, 24, .7); --overlay: rgba(4, 2, 10, .6);
  --glass: rgba(29, 16, 57, .55); --glass-thick: rgba(19, 8, 39, .86); --glass-bar: rgba(11, 5, 24, .5); --glass-clear: rgba(255, 255, 255, .08);
  --glass-grey: rgba(41, 24, 82, .5); --glass-grey-deep: rgba(29, 16, 57, .7);
  --glass-sheen: radial-gradient(130% 160% at 14% -30%, rgba(255, 255, 255, .13), rgba(255, 255, 255, 0) 58%);
  --glass-rim: inset 0 1px 0 rgba(255, 255, 255, .14), inset 0 -1px 0 rgba(0, 0, 0, .35), inset 0 0 0 1px rgba(230, 183, 98, .13);
  --glass-lift: 0 16px 40px -16px rgba(0, 0, 0, .75), 0 1px 3px rgba(0, 0, 0, .4);
  --glass-edge: 0 1px 0 rgba(230, 183, 98, .14), 0 14px 28px -22px rgba(0, 0, 0, .85);
  --glass-tint: #B497FF;
  --glass-card: linear-gradient(160deg, rgba(58, 34, 114, .62) 0%, rgba(34, 19, 69, .52) 48%, rgba(19, 8, 39, .5) 100%);
  --glass-card-thick: linear-gradient(160deg, rgba(58, 34, 114, .92) 0%, rgba(32, 18, 64, .9) 50%, rgba(19, 8, 39, .92) 100%);
  --glass-card-rim: inset 0 1px 0 rgba(255, 255, 255, .15), inset 1px 0 0 rgba(255, 255, 255, .05), inset 0 -1px 0 rgba(0, 0, 0, .35),
                    inset 0 0 0 1px rgba(230, 183, 98, .13), inset 0 0 34px rgba(155, 79, 214, .1);
  --glass-card-rim-sm: inset 0 1px 0 rgba(255, 255, 255, .12), inset 0 0 0 1px rgba(230, 183, 98, .13);
  --glass-card-lift: 0 2px 4px rgba(0, 0, 0, .3), 0 26px 46px -26px rgba(0, 0, 0, .85);
  background: #0B0518;
}
html.st-night body { background: #0B0518; }
body { overflow-x: clip; }
html:not(.st-night) .st-stars, html:not(.st-night) .st-shoot { display: none; }
.st { position: relative; z-index: 1; overflow-x: clip; --tdur: .35s; }
.st ::selection { background: rgba(230, 183, 98, .3); }

/* ---------- the night sky: aurora, stars, shooting stars, rising motes ---------- */
.st-sky { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; background: var(--st-sky); }
.st-aurora { position: absolute; width: 70vmax; height: 70vmax; border-radius: 50%; opacity: var(--st-aurora-op); will-change: transform; }
.st-aurora.a1 { top: -30vmax; right: -20vmax; background: radial-gradient(circle, rgba(124, 77, 255, .42), rgba(124, 77, 255, 0) 62%); }
.st-aurora.a2 { top: 25vh; left: -30vmax; background: radial-gradient(circle, rgba(192, 75, 214, .3), rgba(192, 75, 214, 0) 62%); }
.st-aurora.a3 { bottom: -35vmax; right: 10vw; background: radial-gradient(circle, rgba(230, 183, 98, .16), rgba(230, 183, 98, 0) 60%); }
.st-stars { position: absolute; inset: -100% 0 0 0; background-repeat: repeat; will-change: transform, opacity; }
.st-stars.s1 { background-size: 260px 260px; background-image:
  radial-gradient(1.6px 1.6px at 22px 34px, #FFF 50%, transparent 51%), radial-gradient(1.2px 1.2px at 140px 80px, #F3D9A1 50%, transparent 51%),
  radial-gradient(1px 1px at 210px 170px, #FFF 50%, transparent 51%), radial-gradient(1.4px 1.4px at 70px 220px, #DCCFFF 50%, transparent 51%),
  radial-gradient(1px 1px at 180px 20px, #FFF 50%, transparent 51%), radial-gradient(1.2px 1.2px at 110px 140px, #FFF 50%, transparent 51%); }
.st-stars.s2 { background-size: 420px 420px; opacity: .7; background-image:
  radial-gradient(2px 2px at 60px 90px, #FFF 50%, transparent 51%), radial-gradient(1.6px 1.6px at 300px 40px, #F3D9A1 50%, transparent 51%),
  radial-gradient(1.4px 1.4px at 380px 300px, #FFF 50%, transparent 51%), radial-gradient(2.2px 2.2px at 200px 360px, #E6B762 50%, transparent 51%),
  radial-gradient(1.2px 1.2px at 120px 260px, #DCCFFF 50%, transparent 51%); }
.st-shoot { position: absolute; width: 170px; height: 2px; border-radius: 2px; opacity: 0;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 246, 220, .95)); filter: drop-shadow(0 0 6px rgba(243, 217, 161, .9)); }
.st-shoot.sh1 { top: 12%; right: 8%; } .st-shoot.sh2 { top: 30%; right: 40%; } .st-shoot.sh3 { top: 4%; right: 62%; }
.st-motes { position: absolute; inset: 0; }
.st-mote { position: absolute; bottom: -24px; width: var(--s, 6px); height: var(--s, 6px); border-radius: 50%;
  background: radial-gradient(circle, #FFF6DD 0%, rgba(243, 217, 161, .8) 35%, rgba(243, 217, 161, 0) 70%); opacity: 0; }
.st-progress { position: fixed; top: 0; inset-inline: 0; height: 3px; z-index: 60; pointer-events: none; }
.st-progress i { display: block; height: 100%; background: var(--st-gold); transform-origin: right; transform: scaleX(0); box-shadow: 0 0 12px rgba(230, 183, 98, .8); }

/* ---------- promo strip and top bar ---------- */
.st-promo { position: relative; display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: .3rem .6rem; padding: .55rem var(--sp-4);
  background: var(--st-promo-bg); color: var(--st-promo-ink); font-weight: 700; font-size: var(--fs-callout); text-align: center; }
.st-promo::after { content: ""; position: absolute; inset-inline: 0; bottom: 0; height: 1px; background: linear-gradient(90deg, transparent, #E6B762, transparent); opacity: .7; }
.st-promo > svg { width: 1.1rem; height: 1.1rem; flex: none; color: var(--st-promo-ink); }
.st-shine-text { background: var(--st-promo-shine); background-size: 200% auto;
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.st a.st-promo-link { display: inline-flex; align-items: center; gap: .25rem; color: var(--st-promo-ink); font-weight: 700; padding: .1rem .65rem; border-radius: var(--r-pill);
  background: var(--fill); box-shadow: inset 0 0 0 1px rgba(230, 183, 98, .35); text-decoration: none; }
.st a.st-promo-link:hover { color: #1A0D33; background: var(--st-gold); text-decoration: none; }
.st-promo-link svg { width: .9rem; height: .9rem; }
.st-bar .st-logo img { height: 2.1rem; width: auto; border-radius: 0; }
.st-mock { flex: none; text-decoration: none; }
.st a.st-mock { color: var(--text-2); }
.st-mock svg { width: .85rem; height: .85rem; }
.st .lb-toc a { color: var(--text-2); }
.st .lb-toc a:hover { background: var(--fill); color: var(--text); }
.st .lb-toc a[aria-current="true"] { background: var(--accent-soft); color: var(--accent-ink); }
.st-bar-cta { flex: none; margin-inline-start: auto; }

/* ---------- controls on the night ground ---------- */
.st a { color: var(--tint); }
.st a:hover { color: var(--tint-hover); }
.st .lb-btn, .st .lb-btn:hover { background: var(--st-gold); color: var(--st-on-gold); border: 0;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .6), inset 0 -1px 0 rgba(0, 0, 0, .18), 0 10px 28px -10px rgba(230, 183, 98, .6); }
.st .lb-btn:hover { filter: brightness(1.07) saturate(1.08); }
.st .lb-btn.secondary, .st .lb-btn.secondary:hover { background: var(--fill); color: var(--text); box-shadow: inset 0 0 0 1px var(--line-strong), inset 0 1px 0 rgba(255, 255, 255, .08); }
.st .lb-btn.secondary:hover { background: var(--fill-2); filter: none; }
.st .lb-btn.ghost, .st .lb-btn.ghost:hover { background: transparent; color: var(--accent-ink); box-shadow: none; }
.st .lb-btn.ghost:hover { background: var(--accent-soft); }
.st .lb-segmented { background: var(--fill); box-shadow: inset 0 0 0 1px var(--line); }
.st .lb-segmented button { color: var(--text-2); }
.st .lb-segmented button[aria-pressed="true"] { background: var(--st-gold); color: var(--st-on-gold); box-shadow: 0 4px 14px -6px rgba(230, 183, 98, .7); }
.st .lb-input { background: var(--fill); border-color: var(--line-strong); color: var(--text); box-shadow: var(--st-inset); }
.st .lb-input::placeholder { color: var(--text-3); }
.st .lb-input:focus { border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-soft), var(--st-inset); }
.st .lb-chip { background: var(--fill); color: var(--text-2); }
.st .lb-chip svg { width: .95em; height: .95em; flex: none; }
.st .lb-chip.accent { background: var(--accent-soft); color: var(--accent-ink); }
.st-best { background: var(--st-gold) !important; color: var(--st-on-gold) !important; box-shadow: 0 4px 14px -6px rgba(230, 183, 98, .8); }
.st .lb-tile.st-gold-tile { background: var(--accent-soft); color: var(--accent-ink); box-shadow: inset 0 0 0 1px rgba(230, 183, 98, .28), 0 6px 16px -8px rgba(230, 183, 98, .55); }
.st .lb-metric { --tc: var(--accent); --tc-ink: var(--text); }
.st details.lb-disclosure > summary:hover { background: var(--fill); }
.st .lb-callout svg { color: var(--info); }

/* ---------- type and layout ---------- */
.st .lb-page { gap: clamp(3.5rem, 8vw, 6rem); position: relative; }
.st h2 { display: flex; align-items: center; gap: .6rem; font-size: clamp(1.55rem, 3.2vw, 2.2rem); line-height: 1.15; letter-spacing: -.018em; }
.st-h-ic { width: 1.6rem; height: 1.6rem; flex: none; color: var(--accent); filter: drop-shadow(0 0 10px rgba(230, 183, 98, .6)); }
.st .lb-section { gap: var(--sp-5); }
.st-gold { background: var(--st-gold-shine); background-size: 220% auto;
  -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 4px 24px rgba(230, 183, 98, .28)); }
.st-cta { position: relative; overflow: hidden; isolation: isolate; min-height: 3.3rem; padding-inline: 1.7rem 1.4rem; font-size: 1.0625rem; font-weight: 800; }
.st-cta::after { content: ""; position: absolute; inset-block: 0; left: 0; width: 45%; z-index: -1; pointer-events: none;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, .7), rgba(255, 255, 255, 0)); transform: translateX(-130%) skewX(-20deg); }
.st-cta.is-wide { width: 100%; }
.st-cta svg { transition: transform var(--dur-2) var(--ease-spring); }
.st-cta:hover svg { transform: translateX(-4px); }
.st-center { display: flex; justify-content: center; }

/* ---------- hero ---------- */
.st-hero { padding-block-start: var(--sp-4); gap: clamp(1.5rem, 4vw, 3.5rem); }
.st-hero h1 { font-size: clamp(2.3rem, 5.4vw, 3.8rem); line-height: 1.06; }
.st-hero h1 > span { display: block; }
.st-hero .lb-lede { color: var(--text-2); }
.st-hero .lb-chip svg { color: var(--accent); }
.st-start { position: relative; gap: var(--sp-3); padding: var(--sp-4) var(--sp-4) var(--sp-3); max-width: 34rem; border-radius: var(--r-xl);
  background: var(--glass-sheen), var(--glass-card-thick); -webkit-backdrop-filter: var(--glass-filter); backdrop-filter: var(--glass-filter); }
.st-start::before { content: ""; position: absolute; inset: -1.5px; border-radius: inherit; padding: 1.5px; pointer-events: none;
  background: conic-gradient(from var(--st-ang), rgba(230, 183, 98, 0) 0deg, rgba(230, 183, 98, 0) 200deg, #F3D9A1 270deg, #C2AAFF 320deg, rgba(230, 183, 98, 0) 360deg);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask-composite: exclude; }
.st-field { display: flex; align-items: center; gap: .45rem; font-weight: 700; font-size: var(--fs-callout); }
.st-field svg { width: 1rem; height: 1rem; color: var(--accent); }
.st-start-row { display: flex; gap: var(--sp-2); align-items: center; }
.st-start-row .lb-input { flex: 1; min-width: 0; min-height: 2.85rem; font-size: 1.05rem; border-radius: var(--r-pill); padding-inline: 1.1rem; }
.st-start-row .lb-segmented { flex: none; }
.st .lb-segmented button { min-height: 2.1rem; padding-inline: 1.05rem; font-size: var(--fs-callout); }
.st-checks { list-style: none; margin: 0; padding: 0; display: grid; gap: .35rem; font-size: var(--fs-callout); color: var(--text-2); }
.st-checks li { display: flex; gap: .45rem; align-items: flex-start; }
.st-checks svg { width: 1.05rem; height: 1.05rem; flex: none; margin-top: .2rem; color: var(--success); }
.st-start .st-checks { grid-template-columns: repeat(auto-fit, minmax(min(100%, 9.5rem), 1fr)); font-size: var(--fs-footnote); gap: .3rem .75rem; }
.st-price { display: grid; gap: .2rem; }
.st-price-row { display: flex; flex-wrap: wrap; align-items: baseline; gap: .6rem; font-size: 1.15rem; }
.st-price-row s, .st-was s { color: var(--text-3); text-decoration-color: rgba(255, 138, 147, .9); text-decoration-thickness: 2px; }
.st-price small { display: inline-flex; align-items: center; gap: .35rem; font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--accent-ink); }
.st-price small svg { width: 1rem; height: 1rem; }
.st-stage { --px: 0; --py: 0; position: relative; aspect-ratio: 1; width: 100%; max-width: 36rem; justify-self: center; }
.st-halo { position: absolute; inset: 10%; border-radius: 50%; filter: blur(34px); opacity: .85;
  background: conic-gradient(from 0deg, rgba(230, 183, 98, .05), rgba(230, 183, 98, .6), rgba(124, 77, 255, .7), rgba(192, 75, 214, .45), rgba(230, 183, 98, .05)); }
.st-stage img { position: absolute; height: auto; filter: drop-shadow(0 24px 30px rgba(0, 0, 0, .55)); }
.st-main { width: 74%; left: 13%; top: 10%; z-index: 3; translate: calc(var(--px) * 14px) calc(var(--py) * 14px); }
.st-mini { width: 31%; z-index: 2; opacity: .96; }
.st-mini.m1 { top: -2%; inset-inline-start: -4%; translate: calc(var(--px) * -26px) calc(var(--py) * -26px); }
.st-mini.m2 { top: 6%; inset-inline-end: -6%; width: 28%; translate: calc(var(--px) * 30px) calc(var(--py) * 20px); }
.st-mini.m3 { bottom: 4%; inset-inline-end: -4%; translate: calc(var(--px) * 22px) calc(var(--py) * 30px); }
.st-lume { width: 30%; bottom: -3%; inset-inline-start: -5%; z-index: 4; translate: calc(var(--px) * -18px) calc(var(--py) * 12px); transform-origin: 50% 90%; }
.st-orbit { position: absolute; inset: 2%; z-index: 5; pointer-events: none; }
.st-orbit b { position: absolute; width: 10px; height: 10px; border-radius: 50%; background: radial-gradient(circle, #FFF8E6 0%, rgba(243, 217, 161, 0) 70%); box-shadow: 0 0 14px 4px rgba(243, 217, 161, .55); }
.st-orbit b:nth-child(1) { top: 0; left: 50%; } .st-orbit b:nth-child(2) { top: 48%; right: 0; } .st-orbit b:nth-child(3) { bottom: 2%; left: 34%; width: 7px; height: 7px; }
.st-orbit b:nth-child(4) { top: 30%; left: 0; width: 6px; height: 6px; } .st-orbit b:nth-child(5) { top: 12%; right: 16%; width: 5px; height: 5px; }
.st-tag { position: absolute; z-index: 6; left: 50%; bottom: 2%; transform: translateX(-50%); display: inline-flex; align-items: center; gap: .4rem; padding: .55rem 1.1rem;
  font-size: var(--fs-callout); max-width: 92%; overflow: hidden; white-space: nowrap; color: var(--text); }
.st-tag svg { width: 1rem; height: 1rem; color: var(--accent); flex: none; }
.st-tag b { color: var(--accent-ink); overflow: hidden; text-overflow: ellipsis; }
.st-stats .lb-metric-value { justify-content: flex-end; }
.st-num { background: var(--st-gold-text); -webkit-background-clip: text; background-clip: text; color: transparent; }
@media (max-width: 760px) { .st-stage { max-width: 23rem; } .st-hero { gap: var(--sp-5); } }

/* ---------- covers marquee ---------- */
.st-marquee { display: grid; gap: var(--sp-3); width: 100vw; margin-inline: calc(50% - 50vw); transform: rotate(-2.5deg); padding-block: var(--sp-3); }
.st-mq-cap { display: flex; justify-content: center; align-items: center; gap: .5rem; font-weight: 800; font-size: clamp(1.05rem, 2.2vw, 1.35rem); color: var(--accent-ink); }
.st-mq-cap svg { width: 1.2rem; height: 1.2rem; }
.st-mq-row { overflow: hidden; direction: ltr; -webkit-mask-image: linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent); mask-image: linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent); }
.st-mq-track { display: flex; gap: 1rem; width: max-content; padding-block: .6rem; }
.st-mq-item { display: block; width: 9.5rem; aspect-ratio: 1; border-radius: var(--r-md); overflow: hidden; flex: none;
  box-shadow: 0 0 0 1px rgba(230, 183, 98, .2), 0 14px 26px -14px rgba(0, 0, 0, .8); transition: transform var(--dur-2) var(--ease-spring), box-shadow var(--dur-2) var(--ease); }
.st-mq-item img { width: 100%; height: 100%; object-fit: cover; display: block; }
.st-mq-item:hover { transform: translateY(-6px) scale(1.06) rotate(1.5deg); box-shadow: 0 0 0 2px #E6B762, 0 18px 34px -12px rgba(230, 183, 98, .6); }
html:not(.st-anim) .st-mq-row { overflow-x: auto; }

/* ---------- shelf ---------- */
.st-filters { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--sp-3); min-width: 0; }
.st-cats { display: flex; gap: var(--sp-2); overflow-x: auto; scrollbar-width: none; min-width: 0; flex: 1 1 30rem; padding: 4px 2px; }
.st-cats .lb-chip { flex: none; font-size: var(--fs-callout); padding: .45rem .9rem; min-height: 2.35rem; }
.st .st-cats button.lb-chip.cat[aria-pressed="true"] { background: var(--tc-soft); color: var(--tc-ink); box-shadow: inset 0 0 0 1.5px var(--tc), 0 0 22px -6px var(--tc); }
.st-n { font-variant-numeric: tabular-nums; opacity: .7; font-weight: 600; }
.st-gwrap { display: flex; align-items: center; gap: var(--sp-2); flex: none; }
.st-gl { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 600; color: var(--text-3); }
.st-shelf { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 11rem), 1fr)); gap: var(--sp-4); perspective: 900px; }
.st-book { --rx: 0deg; --ry: 0deg; gap: 0; transform: rotateX(var(--rx)) rotateY(var(--ry)); transform-style: preserve-3d; transition: transform .25s var(--ease), box-shadow var(--dur-2) var(--ease); }
.st-book[hidden] { display: none !important; }
.st a.st-book, .st a.st-book:hover { color: var(--text); text-decoration: none; }
a.st-book:hover { box-shadow: var(--glass-card-rim), 0 0 0 1px rgba(230, 183, 98, .5), 0 26px 46px -22px rgba(124, 77, 255, .65); }
.st-cover { position: relative; display: block; aspect-ratio: 1; overflow: hidden; background: var(--surface-2); }
.st-cover img { display: block; width: 100%; height: 100%; object-fit: cover; transition: transform var(--dur-3) var(--ease); }
.st-cover::after { content: ""; position: absolute; inset: 0; pointer-events: none; transform: translateX(-120%);
  background: linear-gradient(110deg, rgba(255, 255, 255, 0) 35%, rgba(255, 255, 255, .45) 50%, rgba(255, 255, 255, 0) 65%); }
a.st-book:hover .st-cover img { transform: scale(1.06); }
.st-book-body { display: grid; gap: var(--sp-2); padding: var(--sp-3); align-content: space-between; min-height: 6rem; }
.st-book-title { font-size: var(--fs-callout); line-height: 1.3; }
.st-book-foot { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: .35rem; }
.st-go { display: inline-flex; align-items: center; gap: .2rem; margin-inline-start: auto; color: var(--accent-ink); font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 800; }
.st-go svg { width: .95rem; height: .95rem; }
.st-shelf-foot { display: flex; flex-wrap: wrap; justify-content: center; gap: var(--sp-2); }

/* ---------- steps ---------- */
.st-steps { list-style: none; margin: 0; padding: 0; position: relative; }
.st-step { gap: var(--sp-2); overflow: hidden; }
.st-step-vis { position: relative; height: 9.5rem; margin: calc(var(--sp-4) * -1) calc(var(--sp-5) * -1) var(--sp-1); display: grid; place-items: center; overflow: hidden;
  background: radial-gradient(70% 90% at 50% 100%, rgba(124, 77, 255, .35), rgba(124, 77, 255, 0) 70%), var(--st-well); }
.st-fan { position: relative; width: 9rem; height: 7rem; }
.st-fan img { position: absolute; left: 50%; top: 50%; width: 5.6rem; aspect-ratio: 1; object-fit: cover; border-radius: .6rem; box-shadow: 0 10px 20px -8px rgba(0, 0, 0, .7);
  transform: translate(-50%, -50%) translateX(calc(var(--k) * -2.6rem)) rotate(calc(var(--k) * 12deg)); transition: transform var(--dur-3) var(--ease-spring); }
.st-step:hover .st-fan img { transform: translate(-50%, -60%) translateX(calc(var(--k) * -3.2rem)) rotate(calc(var(--k) * 18deg)); }
.st-fan img[style*="--k:0"] { z-index: 2; }
.st-upload { position: relative; display: grid; place-items: center; width: 5.5rem; height: 5.5rem; border-radius: 50%; color: var(--accent-ink); background: rgba(230, 183, 98, .1); }
.st-upload i { position: absolute; inset: 0; border-radius: 50%; border: 2px dashed rgba(230, 183, 98, .7); }
.st-upload svg { width: 2.3rem; height: 2.3rem; filter: drop-shadow(0 0 10px rgba(230, 183, 98, .7)); }
.st-step-book { height: 8.6rem; width: auto; filter: drop-shadow(0 16px 20px rgba(0, 0, 0, .6)); }
.st-step-photo { width: 100%; height: 100%; object-fit: cover; opacity: .9; }
.st-step-head { display: flex; align-items: center; justify-content: space-between; }
.st .lb-disc.st-disc { background: var(--st-gold); color: var(--st-on-gold); box-shadow: 0 0 0 4px rgba(230, 183, 98, .15), 0 8px 18px -6px rgba(230, 183, 98, .7); }

/* ---------- proof ---------- */
.st-proof-grid { display: grid; grid-template-columns: minmax(0, 20rem) minmax(0, 1fr); gap: var(--sp-5); align-items: center; }
.st-quote { margin: 0; gap: var(--sp-3); padding: var(--sp-5); border-radius: var(--r-xl); position: relative; overflow: hidden; }
.st-quote::before { content: "”"; position: absolute; top: -1.4rem; inset-inline-end: .6rem; font-size: 9rem; line-height: 1; font-weight: 800; color: rgba(230, 183, 98, .14); pointer-events: none; }
.st-stars-row { display: flex; gap: .15rem; font-size: 1.45rem; color: var(--accent); }
.st-stars-row i { font-style: normal; display: inline-block; text-shadow: 0 0 12px rgba(230, 183, 98, .7); }
.st-quote blockquote { margin: 0; font-size: 1.22rem; font-weight: 600; line-height: 1.45; position: relative; }
.st-quote figcaption { font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; }
.st-ugc-row { overflow: hidden; direction: ltr; -webkit-mask-image: linear-gradient(90deg, transparent, #000 6%, #000 94%, transparent); mask-image: linear-gradient(90deg, transparent, #000 6%, #000 94%, transparent); }
.st-ugc-track { display: flex; gap: var(--sp-3); width: max-content; padding-block: .5rem; }
.st-ugc-item { margin: 0; width: 12.5rem; direction: rtl; transition: transform var(--dur-2) var(--ease-spring); }
.st-ugc-item:hover { transform: translateY(-6px) rotate(-1deg); }
.st-ugc-item .lb-media-title { display: inline-flex; align-items: center; gap: .3rem; }
.st-ugc-item .lb-media-title svg { width: .9rem; height: .9rem; color: #FF98BD; flex: none; }
.st .lb-media-frame { box-shadow: 0 0 0 1px rgba(230, 183, 98, .18), 0 16px 30px -16px rgba(0, 0, 0, .85); }
html:not(.st-anim) .st-ugc-row { overflow-x: auto; }
@media (max-width: 860px) { .st-proof-grid { grid-template-columns: minmax(0, 1fr); } .st-ugc-row { order: -1; } .st-ugc-item { width: 10rem; } }

/* ---------- why ---------- */
.st-banner { position: relative; margin: 0; border-radius: var(--r-xl); overflow: hidden; box-shadow: 0 0 0 1px rgba(230, 183, 98, .2), 0 30px 60px -30px rgba(124, 77, 255, .7); }
.st-banner img { display: block; width: 100%; aspect-ratio: 800 / 333; object-fit: cover; }
.st-banner::after { content: ""; position: absolute; inset: 0; pointer-events: none; transform: translateX(-120%);
  background: linear-gradient(105deg, rgba(255, 255, 255, 0) 40%, rgba(255, 246, 220, .22) 50%, rgba(255, 255, 255, 0) 60%); }
.st-why-card { gap: var(--sp-2); }

/* ---------- price and deals ---------- */
.st-price-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: var(--sp-5); align-items: start; }
.st-offer { gap: var(--sp-3); padding: var(--sp-5); border-radius: var(--r-xl); position: relative; overflow: hidden; }
.st-offer::before { content: ""; position: absolute; top: -40%; inset-inline-end: -30%; width: 80%; aspect-ratio: 1; border-radius: 50%; pointer-events: none;
  background: radial-gradient(circle, rgba(230, 183, 98, .22), rgba(230, 183, 98, 0) 65%); }
.st-offer-top { display: flex; gap: var(--sp-4); align-items: center; position: relative; }
.st-offer-cover { width: 7.5rem; aspect-ratio: 1; object-fit: cover; border-radius: var(--r-md); flex: none; box-shadow: 0 0 0 1px rgba(230, 183, 98, .3), 0 20px 34px -16px rgba(0, 0, 0, .8); transform: rotate(-4deg); }
.st-offer-head { display: grid; gap: .45rem; min-width: 0; }
.st-offer-label { display: inline-flex; align-items: center; gap: .35rem; font-family: var(--font-2); font-weight: 700; color: var(--accent-ink); }
.st-offer-label svg { width: 1rem; height: 1rem; }
.st-amount { display: flex; flex-wrap: wrap; align-items: flex-end; gap: var(--sp-3); }
.st-amount b { font-size: clamp(2.8rem, 6.5vw, 3.9rem); line-height: 1; font-weight: 800; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }
.st-was { display: grid; line-height: 1.15; padding-bottom: .3rem; }
.st-was small { font-family: var(--font-2); font-size: var(--fs-caption); color: var(--text-3); font-weight: 600; }
.st-was s { font-size: 1.35rem; font-weight: 700; }
.st-cta-note { display: inline-flex; justify-content: center; align-items: center; gap: .35rem; font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }
.st-cta-note svg { width: .95rem; height: .95rem; color: var(--success); }
.st-deals { gap: var(--sp-3); }
.st-deals h3 { display: flex; align-items: center; gap: .45rem; font-size: 1.2rem; }
.st-deals h3 svg { width: 1.2rem; height: 1.2rem; color: var(--accent); }
.st a.st-deal, .st a.st-deal:hover { color: var(--text); text-decoration: none; }
.st-deal { display: grid; grid-template-columns: 5.5rem minmax(0, 1fr) auto; align-items: center; gap: var(--sp-3); padding: var(--sp-3); border-radius: var(--r-lg);
  transition: transform var(--dur-2) var(--ease-spring), box-shadow var(--dur-2) var(--ease); }
a.st-deal:hover { transform: translateY(-3px); box-shadow: var(--glass-card-rim), 0 0 0 1px rgba(230, 183, 98, .5), 0 22px 40px -22px rgba(124, 77, 255, .7); }
.st-deal-vis { position: relative; width: 5.5rem; height: 5.5rem; }
.st-deal-img { width: 100%; height: 100%; object-fit: cover; border-radius: var(--r-md); box-shadow: 0 10px 20px -10px rgba(0, 0, 0, .8); }
.st-deal-covers img { position: absolute; width: 4.1rem; aspect-ratio: 1; object-fit: cover; border-radius: .55rem; box-shadow: 0 10px 18px -8px rgba(0, 0, 0, .8);
  top: calc(var(--k) * 1.2rem); inset-inline-start: calc(var(--k) * 1.3rem); transform: rotate(calc(-6deg + var(--k) * 12deg)); }
.st-deal-covers img:only-child { width: 5.2rem; top: .15rem; inset-inline-start: .15rem; transform: rotate(-4deg); }
.st-deal-body { display: grid; gap: .2rem; min-width: 0; }
.st-deal-title { display: flex; align-items: center; gap: .45rem; }
.st-deal-title .lb-tile { width: 1.75rem; height: 1.75rem; }
.st-deal-body small { color: var(--text-2); font-size: var(--fs-footnote); line-height: 1.45; }
.st-deal-badge { align-self: center; padding: .35rem .8rem; border-radius: var(--r-pill); background: var(--st-gold); color: var(--st-on-gold);
  font-weight: 800; font-size: var(--fs-callout); white-space: nowrap; box-shadow: 0 6px 18px -8px rgba(230, 183, 98, .8); }
@media (max-width: 860px) { .st-price-grid { grid-template-columns: minmax(0, 1fr); } }

/* ---------- faq ---------- */
.st-faq .lb-disclosures { max-width: 54rem; }
.st-faq .lb-disclosure > summary { font-size: var(--fs-body); padding-block: .8rem; }
.st-faq .lb-disclosure > summary .lb-tile { width: 1.9rem; height: 1.9rem; }

/* ---------- final call ---------- */
.st-final { position: relative; display: grid; place-items: center; padding: clamp(2.5rem, 7vw, 5rem) var(--sp-4); border-radius: var(--r-xl); overflow: hidden;
  background: radial-gradient(80% 90% at 50% 0%, rgba(124, 77, 255, .4), rgba(124, 77, 255, 0) 70%), radial-gradient(60% 70% at 85% 100%, rgba(230, 183, 98, .22), rgba(230, 183, 98, 0) 70%), var(--st-final-bg);
  box-shadow: inset 0 0 0 1px rgba(230, 183, 98, .18); }
.st-final-glow { position: absolute; width: 60%; aspect-ratio: 1; border-radius: 50%; filter: blur(50px); opacity: .55; pointer-events: none;
  background: conic-gradient(from 90deg, rgba(230, 183, 98, .5), rgba(124, 77, 255, .6), rgba(192, 75, 214, .4), rgba(230, 183, 98, .5)); }
.st-final-lume { position: absolute; z-index: 2; width: clamp(7rem, 17vw, 12rem); inset-inline-start: clamp(.5rem, 4vw, 3rem); bottom: clamp(.5rem, 3vw, 2rem);
  filter: drop-shadow(0 18px 24px rgba(0, 0, 0, .6)); transform-origin: 50% 90%; }
.st-final-card { position: relative; z-index: 1; max-width: 40rem; text-align: center; justify-items: center; gap: var(--sp-3); padding: var(--sp-6) var(--sp-5); border-radius: var(--r-xl); }
.st-final-card h2 { justify-content: center; }
.st-final-card .lb-lede { margin-inline: auto; color: var(--text-2); }
.st-final-row { justify-content: center; }
.st-cta-2 { min-height: 3.3rem; padding-inline: 1.4rem; font-size: 1.0625rem; }
@media (max-width: 760px) { .st-final-lume { position: relative; inset: auto; margin-bottom: -2.2rem; } .st-final { gap: 0; } }

/* ---------- more, footer ---------- */
.st-more .lb-group-row { justify-content: space-between; gap: var(--sp-3); }
.st a.lb-group-row, .st a.lb-group-row:hover { color: var(--text); text-decoration: none; }
.st-more .lb-group-row > svg { width: 1rem; height: 1rem; flex: none; color: var(--accent-ink); }
.st-more .lb-group-row .lb-tile { width: 1.9rem; height: 1.9rem; }
.st-grow { flex: 1; min-width: 0; }
.st-guide-img { width: 3.2rem; height: 3.2rem; object-fit: cover; border-radius: .6rem; flex: none; box-shadow: 0 8px 16px -8px rgba(0, 0, 0, .8); }
.st-guide { display: grid; gap: .15rem; flex: 1; min-width: 0; }
.st-guide small { display: inline-flex; align-items: center; gap: .25rem; font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); }
.st-guide small svg { width: .85rem; height: .85rem; }
.st-groups { display: inline-flex; align-items: center; gap: .3rem; font-size: var(--fs-callout); font-weight: 700; justify-self: start; }
.st-groups svg { width: 1rem; height: 1rem; }
.st-foot { gap: var(--sp-4); border-top-color: var(--line); }
.st-foot-cols { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--sp-4); }
.st-foot-col { display: grid; gap: .4rem; align-content: start; }
.st-foot-col b { color: var(--accent-ink); font-size: var(--fs-callout); }
.st .st-foot-col a { display: inline-flex; align-items: center; gap: .4rem; color: var(--text-2); }
.st .st-foot-col a:hover { color: var(--text); }
.st-foot-col a svg { width: 1rem; height: 1rem; color: var(--accent-ink); flex: none; }
.st-notice p { margin: 0; color: var(--text-2); }
@media (max-width: 760px) { .st-foot-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); } }

/* ---------- sparkles (the pointer trail and the bursts, drawn by the script) ---------- */
.st-spark { position: fixed; z-index: 70; width: var(--s, 10px); height: var(--s, 10px); pointer-events: none; left: 0; top: 0;
  background: var(--c, #F3D9A1); clip-path: polygon(50% 0, 61% 39%, 100% 50%, 61% 61%, 50% 100%, 39% 61%, 0 50%, 39% 39%);
  filter: drop-shadow(0 0 6px rgba(243, 217, 161, .9)); }

/* ---------- motion (only with html.st-anim) ---------- */
@keyframes st-in { from { opacity: 0; transform: translateY(28px) scale(.98); filter: blur(6px); } to { opacity: 1; transform: none; filter: none; } }
@keyframes st-fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes st-float { 0%, 100% { transform: translateY(0) rotate(var(--r, 0deg)); } 50% { transform: translateY(-16px) rotate(calc(var(--r, 0deg) + 2deg)); } }
@keyframes st-bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-7px); } }
@keyframes st-wave { 0%, 100% { transform: rotate(-7deg); } 50% { transform: rotate(7deg); } }
@keyframes st-wiggle { 0%, 70%, 100% { transform: rotate(0); } 76% { transform: rotate(-16deg) scale(1.15); } 84% { transform: rotate(14deg) scale(1.15); } 92% { transform: rotate(-8deg); } }
@keyframes st-shimmer { from { background-position: 0% 50%; } to { background-position: 220% 50%; } }
@keyframes st-sweep { 0%, 55% { transform: translateX(-130%) skewX(-20deg); } 100% { transform: translateX(330%) skewX(-20deg); } }
@keyframes st-shine { from { transform: translateX(-120%); } to { transform: translateX(120%); } }
@keyframes st-spin { to { transform: rotate(1turn); } }
@keyframes st-ang { to { --st-ang: 360deg; } }
@keyframes st-glow { 0%, 100% { box-shadow: inset 0 1px 0 rgba(255, 255, 255, .6), 0 10px 28px -10px rgba(230, 183, 98, .55); }
  50% { box-shadow: inset 0 1px 0 rgba(255, 255, 255, .6), 0 14px 44px -6px rgba(230, 183, 98, .9); } }
@keyframes st-twinkle { 0%, 100% { opacity: .35; } 50% { opacity: 1; } }
@keyframes st-up { from { transform: translateY(0); } to { transform: translateY(50%); } }
@keyframes st-drift { from { transform: translate3d(0, 0, 0) scale(1); } to { transform: translate3d(-9vw, 7vh, 0) scale(1.25); } }
@keyframes st-shoot { 0% { opacity: 0; transform: translate(0, 0) rotate(-32deg); } 3% { opacity: 1; } 14% { opacity: 0; transform: translate(-46vw, 29vw) rotate(-32deg); } 100% { opacity: 0; transform: translate(-46vw, 29vw) rotate(-32deg); } }
@keyframes st-rise { 0% { opacity: 0; transform: translate(0, 0) scale(.5); } 12% { opacity: .95; } 80% { opacity: .7; } 100% { opacity: 0; transform: translate(var(--sway, 30px), -105vh) scale(1.1); } }
@keyframes st-marquee { to { transform: translateX(-50%); } }
@keyframes st-pop { 0% { opacity: 0; transform: translateY(18px) scale(.85) rotateX(18deg); } 70% { opacity: 1; transform: translateY(-3px) scale(1.02); } 100% { opacity: 1; transform: none; } }
@keyframes st-flip { 0% { transform: rotateY(0); } 50% { transform: rotateY(90deg) scale(.96); } 100% { transform: rotateY(0); } }
@keyframes st-tagpop { 0% { transform: translateX(-50%) scale(1); } 40% { transform: translateX(-50%) scale(1.09); } 100% { transform: translateX(-50%) scale(1); } }
@keyframes st-spark { 0% { opacity: 1; transform: translate(var(--x), var(--y)) scale(0) rotate(0); } 30% { opacity: 1; transform: translate(calc(var(--x) + var(--dx) * .3), calc(var(--y) + var(--dy) * .3)) scale(1) rotate(60deg); }
  100% { opacity: 0; transform: translate(calc(var(--x) + var(--dx)), calc(var(--y) + var(--dy))) scale(.2) rotate(200deg); } }
@keyframes st-zoom { from { transform: scale(1); } to { transform: scale(1.1); } }
@keyframes st-ring { 0% { transform: scale(.85); opacity: .9; } 100% { transform: scale(1.5); opacity: 0; } }
@keyframes st-strike { from { text-decoration-color: transparent; } to { text-decoration-color: rgba(255, 138, 147, .9); } }

.st-anim .st-aurora.a1 { --dur: 26s; animation: st-drift var(--dur) ease-in-out infinite alternate; }
.st-anim .st-aurora.a2 { --dur: 32s; animation: st-drift var(--dur) ease-in-out infinite alternate-reverse; }
.st-anim .st-aurora.a3 { --dur: 22s; animation: st-drift var(--dur) ease-in-out infinite alternate; }
.st-anim .st-stars.s1 { --dur: 4.5s, 160s; animation: st-twinkle 4.5s ease-in-out infinite, st-up 160s linear infinite; }
.st-anim .st-stars.s2 { --dur: 6.5s, 240s; animation: st-twinkle 6.5s ease-in-out infinite reverse, st-up 240s linear infinite; }
.st-anim .st-shoot { --dur: 11s; animation: st-shoot var(--dur) ease-in infinite; }
.st-anim .st-shoot.sh2 { animation-delay: 4.2s; } .st-anim .st-shoot.sh3 { animation-delay: 7.6s; }
.st-anim .st-mote { animation: st-rise var(--dur, 18s) linear infinite; animation-delay: var(--delay, 0s); }
.st-anim .st-wiggle { --dur: 3.4s; animation: st-wiggle var(--dur) ease-in-out infinite; transform-origin: 50% 20%; }
.st-anim .st-shine-text { --dur: 4s; animation: st-shimmer var(--dur) linear infinite; }
.st-anim .st-gold { --dur: 7s; animation: st-shimmer var(--dur) linear infinite; }
.st-anim .st-num { --dur: 6s; }
.st-anim .st-cta { --dur: 3.2s; animation: st-glow var(--dur) ease-in-out infinite; }
.st-anim .st-cta::after { --dur: 3.6s; animation: st-sweep var(--dur) ease-in-out infinite; }
.st-anim .st-bar-cta::after { content: ""; position: absolute; inset-block: 0; left: 0; width: 45%; pointer-events: none;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, .65), rgba(255, 255, 255, 0)); --dur: 4.2s; animation: st-sweep var(--dur) ease-in-out infinite; }
.st-bar-cta { position: relative; overflow: hidden; }
.st-anim .st-start::before { --dur: 5s; animation: st-ang var(--dur) linear infinite; }
.st-anim .st-l { --dur: 1s; animation: st-in var(--dur) var(--ease) both; animation-delay: calc(var(--i, 0) * 130ms + 120ms); }
.st-anim .st-halo { --dur: 16s; animation: st-spin var(--dur) linear infinite; }
.st-anim .st-main { --dur: 1.2s, 7s; animation: st-fade 1.2s var(--ease) both, st-float 7s ease-in-out 1.2s infinite; }
.st-anim .st-mini { --dur: 1.2s, 8s; animation: st-fade 1.2s var(--ease) both, st-float 8s ease-in-out infinite; }
.st-anim .st-mini.m1 { animation-delay: .3s, -2s; } .st-anim .st-mini.m2 { animation-delay: .45s, -5s; animation-duration: 1.2s, 9s; --dur: 1.2s, 9s; } .st-anim .st-mini.m3 { animation-delay: .6s, -3.5s; }
.st-anim .st-lume { --dur: 1.2s, 3.2s; animation: st-fade 1.2s var(--ease) .8s both, st-wave 3.2s ease-in-out infinite; }
.st-anim .st-orbit { --dur: 20s; animation: st-spin var(--dur) linear infinite; }
.st-anim .st-orbit b { --dur: 2.4s; animation: st-twinkle var(--dur) ease-in-out infinite; }
.st-anim .st-orbit b:nth-child(2n) { animation-delay: -1.2s; }
.st-anim .st-tag.is-pop { --dur: .5s; animation: st-tagpop var(--dur) var(--ease-spring); }
.st-anim .st-rv:not(.is-in) { opacity: 0; }
.st-anim .st-rv.is-in { --dur: .9s; animation: st-in var(--dur) var(--ease) both; animation-delay: calc(var(--i, 0) * 90ms); }
.st-anim .st-marquee.st-rv.is-in { animation-name: st-fade; }
.st-anim .st-mq-track { --dur: 60s; animation: st-marquee var(--dur) linear infinite; }
.st-anim .st-mq-row.is-rev .st-mq-track { --dur: 70s; animation-duration: 70s; animation-direction: reverse; }
.st-anim .st-mq-row:hover .st-mq-track, .st-anim .st-ugc-row:hover .st-ugc-track { animation-play-state: paused; }
.st-anim .st-ugc-track { --dur: 55s; animation: st-marquee var(--dur) linear infinite reverse; }
.st-anim .st-book.is-pop { --dur: .65s; animation: st-pop var(--dur) var(--ease-spring) both; animation-delay: calc(var(--i, 0) * 45ms); }
.st-anim img.is-flip { --dur: .6s; animation: st-flip var(--dur) var(--ease); }
.st-anim a.st-book:hover .st-cover::after { --dur: .9s; animation: st-shine var(--dur) var(--ease); }
.st-anim .st-bob { --dur: 3.6s; animation: st-bob var(--dur) ease-in-out infinite; animation-delay: var(--d, 0s); }
.st-anim .st-upload i { --dur: 9s; animation: st-spin var(--dur) linear infinite; }
.st-anim .st-upload svg { --dur: 1.8s; animation: st-bob var(--dur) ease-in-out infinite; }
.st-anim .st-upload::after { content: ""; position: absolute; inset: 0; border-radius: 50%; box-shadow: 0 0 0 2px rgba(230, 183, 98, .6); --dur: 2.2s; animation: st-ring var(--dur) ease-out infinite; }
.st-anim .st-step-book { --dur: 6s; animation: st-float var(--dur) ease-in-out infinite; }
.st-anim .st-step-photo { --dur: 14s; animation: st-zoom var(--dur) ease-in-out infinite alternate; }
.st-anim .st-steps::before { content: ""; position: absolute; top: 4.75rem; inset-inline: 10%; height: 2px; z-index: 2; pointer-events: none; opacity: .55;
  background: repeating-linear-gradient(90deg, #E6B762 0 10px, transparent 10px 20px); background-size: 40px 2px; --dur: 1.6s; animation: st-shimmer var(--dur) linear infinite; }
.st-anim .st-stars-row i { --dur: 2.6s; animation: st-twinkle var(--dur) ease-in-out infinite; animation-delay: calc(var(--i) * .25s); }
.st-anim .st-banner img { --dur: 20s; animation: st-zoom var(--dur) ease-in-out infinite alternate; }
.st-anim .st-banner::after { --dur: 6s; animation: st-shine var(--dur) ease-in-out infinite; }
.st-anim .st-offer-cover { --r: -4deg; --dur: 6.5s; animation: st-float var(--dur) ease-in-out infinite; }
.st-anim .st-offer::before { --dur: 5s; animation: st-twinkle var(--dur) ease-in-out infinite; }
.st-anim .st-was s { --dur: 1.2s; animation: st-strike var(--dur) ease-out 1s both; }
.st-anim .st-deal-badge { --dur: 3s; animation: st-glow var(--dur) ease-in-out infinite; }
.st-anim .st-deal:nth-of-type(2n) .st-deal-badge { animation-delay: -1.5s; }
.st-anim .st-deal-covers img { --dur: .4s; transition: transform var(--dur-3) var(--ease-spring); }
.st-anim a.st-deal:hover .st-deal-covers img { transform: rotate(calc(-14deg + var(--k) * 28deg)) translateY(-4px); }
.st-anim .st-final-glow { --dur: 14s; animation: st-spin var(--dur) linear infinite; }
.st-anim .st-final-lume { --dur: 3.4s, 6s; animation: st-wave 3.4s ease-in-out infinite, st-bob 6s ease-in-out infinite; }
.st-anim .st-h-ic { --dur: 4s; animation: st-bob var(--dur) ease-in-out infinite; }
.st-anim .st-spark { --dur: var(--life, .9s); animation: st-spark var(--life, .9s) var(--ease) forwards; }
.st-anim details.lb-disclosure[open] .lb-disclosure-body { --dur: .45s; animation: st-in var(--dur) var(--ease); }
/* the system asks for reduced motion, but this copy runs the motion anyway (st-full): give every animation and transition its
   length back over lumebook.css's .01ms (same !important, higher specificity) */
@media (prefers-reduced-motion: reduce) {
  html.st-full .st *, html.st-full .st *::before, html.st-full .st *::after, html.st-full .st-sky *, html.st-full .st-spark {
    animation-duration: var(--dur, .01ms) !important; transition-duration: var(--tdur, .01ms) !important; }
}

/* ---------- phones ---------- */
@media (max-width: 640px) {
  .st-bar .lb-toc { display: none; }
  .st .st-bar .lb-topbar-in { flex-wrap: nowrap; padding-block: .45rem; }
  .st-promo { font-size: var(--fs-footnote); padding-inline: var(--sp-3); }
  .st-bar .st-logo img { height: 1.7rem; }
  .st-bar-cta { min-height: 2.25rem; padding-inline: .9rem; font-size: var(--fs-footnote); }
  .st-bar-cta svg { display: none; }
  .st-start { padding: var(--sp-3); }
  .st-start-row { flex-wrap: wrap; }
  .st-start-row .lb-input { flex-basis: 100%; }
  .st-start-row .lb-segmented { width: 100%; display: grid; grid-template-columns: 1fr 1fr; }
  .st-mq-item { width: 6.8rem; }
  .st-shelf { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--sp-3); }
  .st-book-body { padding: var(--sp-2) var(--sp-3) var(--sp-3); }
  .st-cats { flex-basis: 100%; margin-inline: calc(var(--sp-4) * -1); padding-inline: var(--sp-4); }
  .st-offer-top { flex-direction: column; align-items: flex-start; }
  .st-deal { grid-template-columns: 4.5rem minmax(0, 1fr); }
  .st-deal-vis { width: 4.5rem; height: 4.5rem; }
  .st-deal-covers img { width: 3.4rem; }
  .st-deal-covers img:only-child { width: 4.3rem; }
  .st-deal-badge { grid-column: 2; justify-self: start; }
  .st-final-row > * { width: 100%; }
}
@media (max-width: 400px) { .st-mock { display: none; } }

/* ---------- the dark and light switch ---------- */
.st-theme { flex: none; width: 2.5rem; min-height: 2.5rem; position: relative; overflow: hidden; }
.st-theme svg { width: 1.15rem; height: 1.15rem; transition: transform .5s var(--ease-spring), opacity .3s; }
.st-theme .i-sun { color: var(--accent); }
.st-theme .i-moon { color: #7C4DFF; position: absolute; }
html.st-night .st-theme .i-moon, html:not(.st-night) .st-theme .i-sun { opacity: 0; transform: rotate(-90deg) scale(.4); }
.st-anim .st-theme:hover svg { transform: rotate(25deg) scale(1.1); }
::view-transition-old(root), ::view-transition-new(root) { animation: none; mix-blend-mode: normal; }
"""

JS = r"""<script>
(function () {
  var root = document.documentElement;
  try {
  var D = window.ST_DATA, $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var ANIM = root.classList.contains('st-anim'), fine = window.matchMedia && matchMedia('(pointer: fine)').matches;
  var shelfEl = $('#st-shelf'), cards = {}; $$('#st-shelf .st-book').forEach(function (c) { cards[c.getAttribute('data-id')] = c; });
  var more = $('#st-more'), all = $('#st-all'), cur = Object.keys(D.cats)[0], open = false;
  if (window.matchMedia && matchMedia('(max-width: 640px)').matches) D.show = 8;

  // ---------- sparkles ----------
  var alive = 0, COLORS = ['#F3D9A1', '#E6B762', '#FFF6DF', '#C2AAFF', '#FF98BD'];
  function spark(x, y, n, spread, big) {
    if (!ANIM) return;
    for (var k = 0; k < n && alive < 90; k++) {
      var s = document.createElement('i'), a = Math.random() * Math.PI * 2, r = (spread || 40) * (.4 + Math.random() * .8);
      s.className = 'st-spark';
      s.style.setProperty('--x', x + 'px'); s.style.setProperty('--y', y + 'px');
      s.style.setProperty('--dx', Math.cos(a) * r + 'px'); s.style.setProperty('--dy', (Math.sin(a) * r - (big ? 10 : 18)) + 'px');
      s.style.setProperty('--s', ((big ? 9 : 6) + Math.random() * (big ? 10 : 6)) + 'px');
      s.style.setProperty('--c', COLORS[(Math.random() * COLORS.length) | 0]);
      s.style.setProperty('--life', (.7 + Math.random() * .6).toFixed(2) + 's');
      alive++; s.addEventListener('animationend', function () { alive--; this.remove(); });
      (document.querySelector('dialog.st-dlg[open]') || document.body).appendChild(s);
    }
  }
  function burstAt(el, n) { var r = el.getBoundingClientRect(); spark(r.left + r.width / 2, r.top + r.height / 2, n || 14, Math.max(50, r.width / 2), true); }
  if (ANIM && fine) {
    var last = 0;
    window.addEventListener('pointermove', function (e) { var t = performance.now(); if (t - last < 38) return; last = t; spark(e.clientX, e.clientY, 1, 22); }, { passive: true });
  }
  $$('[data-cta]').forEach(function (b) {
    b.addEventListener('click', function (e) { spark(e.clientX || 0, e.clientY || 0, 22, 90, true); });
    b.addEventListener('pointerenter', function () { burstAt(b, 6); });
  });

  // ---------- the shelf ----------
  function shelf(pop) {
    var ids = D.cats[cur].ids, shown = [];
    Object.keys(cards).forEach(function (k) { cards[k].hidden = true; cards[k].classList.remove('is-pop'); });
    ids.forEach(function (id, i) { var c = cards[String(id)]; if (!c) return; c.style.order = i; c.hidden = !open && i >= D.show; if (!c.hidden) shown.push(c); });
    if (pop && ANIM) { void shelfEl.offsetWidth; shown.forEach(function (c, i) { c.style.setProperty('--i', i); c.classList.add('is-pop'); }); }
    var left = ids.length - D.show;
    more.hidden = open || left <= 0;
    more.textContent = D.more.replace('{n}', left);
    all.href = D.cats[cur].href;
  }
  $$('.st-cats [data-cat]').forEach(function (b) {
    b.addEventListener('click', function () {
      cur = b.getAttribute('data-cat'); open = false;
      $$('.st-cats [data-cat]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      burstAt(b, 8); shelf(true);
    });
  });
  more.addEventListener('click', function () { open = true; shelf(true); });
  if (ANIM && fine) {
    shelfEl.addEventListener('pointermove', function (e) {
      var c = e.target.closest('.st-book'); if (!c) return;
      var r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      c.style.setProperty('--ry', (x * 14).toFixed(2) + 'deg'); c.style.setProperty('--rx', (-y * 14).toFixed(2) + 'deg');
    });
    shelfEl.addEventListener('pointerout', function (e) { var c = e.target.closest('.st-book'); if (c && !c.contains(e.relatedTarget)) { c.style.setProperty('--rx', '0deg'); c.style.setProperty('--ry', '0deg'); } });
  }

  // ---------- boy or girl: both pickers move together and every cover follows ----------
  var G = { b: 'boy', g: 'girl' };
  $$('.st-g [data-g]').forEach(function (b) {
    b.addEventListener('click', function () {
      var g = b.getAttribute('data-g');
      $$('.st-g [data-g]').forEach(function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-g') === g ? 'true' : 'false'); });
      $$('img[data-book]').forEach(function (im) {
        if (im.hasAttribute('data-only')) return;
        var id = im.getAttribute('data-book');
        im.src = D.store + '/book_covers/' + G[g] + '/B' + id + '_' + G[g] + '.webp';
        if (ANIM && !im.closest('[hidden]')) { im.classList.remove('is-flip'); void im.offsetWidth; im.classList.add('is-flip'); }
      });
      burstAt(b, 10);
    });
  });

  // ---------- the child's name: on the hero tag and every start button (text only, never markup) ----------
  var input = $('#st-name'), tag = $('#st-tag');
  input.addEventListener('input', function () {
    var name = input.value.replace(/\s+/g, ' ').trim().slice(0, 20);
    $$('[data-name]').forEach(function (el) { el.textContent = name || D.tag; });
    $$('[data-cta-label]').forEach(function (el) {
      if (!el.hasAttribute('data-base')) el.setAttribute('data-base', el.textContent);
      el.textContent = name && el.getAttribute('data-base') === D.cta ? D.cta_named.replace('{name}', name) : el.getAttribute('data-base');
    });
    if (ANIM && tag.offsetParent) { tag.classList.remove('is-pop'); void tag.offsetWidth; tag.classList.add('is-pop'); burstAt(tag, 7); }
  });
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); $('.st-start [data-cta]').click(); } });

  // ---------- reveals, counting numbers ----------
  function count(el) {
    var to = parseFloat(el.getAttribute('data-count')), dec = +el.getAttribute('data-dec') || 0, pre = el.getAttribute('data-prefix') || '', suf = el.getAttribute('data-suffix') || '';
    var t0 = performance.now(), len = 1700;
    function fmt(v) { return pre + (dec ? v.toFixed(dec) : Math.round(v).toLocaleString('en-US')) + suf; }
    (function step(t) { var p = Math.min(1, (t - t0) / len), e = 1 - Math.pow(1 - p, 3); el.textContent = fmt(to * e); if (p < 1) requestAnimationFrame(step); })(t0);
  }
  if (ANIM && 'IntersectionObserver' in window) {
    var seen = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in'); seen.unobserve(e.target);
        $$('[data-count]', e.target).forEach(count);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    $$('.st-rv').forEach(function (el) { seen.observe(el); });
  } else { $$('.st-rv').forEach(function (el) { el.classList.add('is-in'); }); }

  // ---------- the hero follows the pointer ----------
  var stage = $('#st-stage');
  if (ANIM && fine && stage) {
    var raf = 0, px = 0, py = 0;
    window.addEventListener('pointermove', function (e) {
      px = Math.max(-1, Math.min(1, (e.clientX / innerWidth - .5) * 2)); py = Math.max(-1, Math.min(1, (e.clientY / innerHeight - .5) * 2));
      if (!raf) raf = requestAnimationFrame(function () { raf = 0; stage.style.setProperty('--px', px.toFixed(3)); stage.style.setProperty('--py', py.toFixed(3)); });
    }, { passive: true });
  }

  // ---------- rising motes ----------
  if (ANIM) {
    var motes = $('#st-motes'), n = innerWidth < 640 ? 14 : 30;
    for (var i = 0; i < n; i++) {
      var m = document.createElement('i'); m.className = 'st-mote';
      m.style.left = (Math.random() * 100).toFixed(1) + '%';
      m.style.setProperty('--s', (3 + Math.random() * 7).toFixed(1) + 'px');
      m.style.setProperty('--dur', (14 + Math.random() * 16).toFixed(1) + 's');
      m.style.setProperty('--delay', (-Math.random() * 30).toFixed(1) + 's');
      m.style.setProperty('--sway', ((Math.random() - .5) * 140).toFixed(0) + 'px');
      motes.appendChild(m);
    }
  }

  // ---------- scroll: progress line and the section pills ----------
  var bar = $('#st-progress'), ticking = false;
  function onScroll() { ticking = false; var h = document.documentElement.scrollHeight - innerHeight; bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, scrollY / h) : 0) + ')'; }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
  var links = $$('.st-bar .lb-toc a'), secs = links.map(function (a) { return document.querySelector(a.getAttribute('href')); });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a, i) { if (secs[i] === e.target) { links.forEach(function (x) { x.removeAttribute('aria-current'); }); a.setAttribute('aria-current', 'true'); } });
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    secs.forEach(function (s) { if (s) io.observe(s); });
  }
  /*DEMO*/
  shelf(false);
  } catch (err) { root.classList.remove('st-anim', 'st-full'); if (window.console) console.error(err); }
})();
</script>"""


# ======================= the working demo (Yarin, 09 / 11 / 2026: "create a fully working demo, everything does something,
# and let me create a fake book") =======================
# Every link in the page stays in the page: a start button opens the book maker, a book opens its card, a category filters
# the shelf, anything else opens a small sheet that says what the link does in the real store (with a button to open it).
# The book maker: pick a book, the child's name, boy or girl, a photo (shrunk to 320px in the browser, never sent anywhere)
# and a dedication, a short "making" moment, a page-flip preview, a pretend order with the deals and delivery, confetti, and
# "הספרים שלי" (this browser's localStorage only). No payment fields: nothing is charged and nothing is sent.
DEMO_HTML = """
<dialog class="st-dlg" id="st-wiz" aria-label="{my_books}">
 <div class="st-dlg-card st-wiz-card">
  <header class="st-dlg-head">
   <ol class="st-wsteps">{steps}</ol>
   <button class="st-x" type="button" data-close aria-label="סגירה">{i_x}</button>
  </header>
  <div class="st-dlg-body">
   <section data-step="1">
    <h2 class="st-dh">{i_spark}{pick_h}</h2><p class="lb-muted">{pick_p}</p>
    <div class="st-pick-cats"></div>
    <div class="st-pick-grid"></div>
   </section>
   <section data-step="2" hidden>
    <div class="st-hero-step">
     <div class="st-live-wrap"><div class="st-comp" id="st-w-live"></div><p class="st-live-title" id="st-w-book-title"></p>
      <button class="lb-btn ghost sm" type="button" data-goto="1">{i_back}<span>להחליף ספר</span></button></div>
     <div class="st-form">
      <h2 class="st-dh">{i_spark}{hero_h}</h2>
      <label class="st-flabel" for="st-w-name">{name_label}</label>
      <input class="lb-input" id="st-w-name" type="text" dir="rtl" maxlength="20" autocomplete="off" enterkeyhint="next">
      <span class="st-flabel">{gender_label}</span>
      <div class="lb-segmented st-wg" role="group" aria-label="{gender_label}"><button type="button" data-wg="b" aria-pressed="false">בן</button><button type="button" data-wg="g" aria-pressed="false">בת</button></div>
      <span class="st-flabel">{photo_label}</span>
      <label class="st-photo-drop" for="st-w-file"><img id="st-w-photo" alt="{photo_alt}"><span class="st-drop-ic">{i_up}</span><span class="st-drop-t"><b id="st-w-photo-btn">{photo_btn}</b><small>{photo_drop}</small></span></label>
      <input id="st-w-file" type="file" accept="image/*" hidden>
      <small class="st-hint">{i_info}<span>{photo_hint}</span></small>
      <label class="st-flabel" for="st-w-ded">{ded_label}</label>
      <input class="lb-input" id="st-w-ded" type="text" dir="rtl" maxlength="120" placeholder="{ded_ph}" autocomplete="off">
      <small class="st-need" id="st-w-need" hidden>{need}</small>
      <div class="st-wnav"><button class="lb-btn secondary" type="button" data-goto="1">{i_back}<span>{back}</span></button><button class="lb-btn st-cta" type="button" id="st-w-make"><span>{make}</span>{i_spark}</button></div>
     </div>
    </div>
   </section>
   <section data-step="3" hidden>
    <div class="st-make"><div class="st-make-orb"><i></i><img id="st-w-make-img" alt=""></div><p class="st-make-msg" id="st-w-msg" aria-live="polite"></p><div class="st-make-bar"><i id="st-w-bar"></i></div></div>
   </section>
   <section data-step="4" hidden>
    <h2 class="st-dh st-center-h" id="st-w-ph"></h2>
    <div class="st-flip"><div class="st-pages" id="st-w-pages"></div>
     <div class="st-flip-nav"><button class="lb-btn secondary sm" type="button" id="st-w-prev" aria-label="{page_prev}">{i_back}</button><span class="st-dots" id="st-w-dots"></span><button class="lb-btn secondary sm" type="button" id="st-w-next" aria-label="{page_next}">{i_fwd}</button></div></div>
    <p class="st-note">{i_info}<span>{preview_note}</span></p>
    <div class="st-wnav"><button class="lb-btn secondary" type="button" data-goto="2">{i_back}<span>{edit}</span></button><button class="lb-btn st-cta" type="button" data-goto="5"><span>{order}</span>{i_fwd}</button></div>
   </section>
   <section data-step="5" hidden>
    <h2 class="st-dh">{i_gift}{order_h}</h2>
    <div class="st-order">
     <div class="st-order-side"><div class="st-comp" id="st-o-comp"></div><p class="st-live-title" id="st-o-title"></p></div>
     <div class="st-order-main">
      <div class="lb-group st-lines">
       <div class="lb-group-row"><span>{line_book}</span><span class="st-amt"><s>149 ₪</s><b>119 ₪</b></span></div>
       <div class="lb-group-row"><span>{line_digital}</span><span class="st-amt"><b class="st-free">{gift}</b></span></div>
       <div class="lb-group-row" id="st-o-extra-row" hidden><span>{extra_line}: <span id="st-o-extra-name"></span></span><span class="st-amt"><b>99 ₪</b></span></div>
       <div class="lb-group-row"><span id="st-o-del-name"></span><span class="st-amt"><b id="st-o-del-cost"></b></span></div>
      </div>
      <label class="st-extra"><input type="checkbox" id="st-o-extra"><span>{i_gift}{extra_label}</span></label>
      <label class="st-extra-for" id="st-o-extra-for" hidden><span>{extra_for}</span><select class="lb-select" id="st-o-extra-id"></select></label>
      <fieldset class="st-del"><legend>{delivery_h}</legend><div class="st-dels" id="st-o-dels"></div></fieldset>
      <div class="st-order-cta"><div class="st-total"><span>{total}</span><b id="st-o-total"></b></div>
      <button class="lb-btn st-cta is-wide" type="button" id="st-o-confirm"><span>{confirm}</span>{i_check}</button></div>
      <small class="st-note">{i_info}<span>{demo_note}</span></small>
      <button class="lb-btn ghost sm st-back-sm" type="button" data-goto="4">{i_back}<span>{back}</span></button>
     </div>
    </div>
   </section>
   <section data-step="6" hidden>
    <div class="st-done"><div class="st-comp st-done-comp" id="st-d-comp"></div><h2 id="st-d-h"></h2><p class="lb-muted">{done_p}</p>
     <div class="lb-row st-final-row"><button class="lb-btn st-cta" type="button" data-my><span>{done_my}</span>{i_book}</button><button class="lb-btn secondary" type="button" data-again>{i_spark}<span>{done_again}</span></button></div></div>
   </section>
  </div>
 </div>
</dialog>
<dialog class="st-dlg" id="st-bookdlg" aria-label="{book_create}">
 <div class="st-dlg-card st-book-card">
  <button class="st-x st-x-float" type="button" data-close aria-label="סגירה">{i_x}</button>
  <div class="st-bd">
   <div class="st-bd-vis"><img id="st-b-img" alt=""><div class="lb-segmented st-bg" role="group" aria-label="בן או בת"><button type="button" data-bg="b" aria-pressed="false">בן</button><button type="button" data-bg="g" aria-pressed="false">בת</button></div></div>
   <div class="st-bd-text">
    <span class="lb-chip st-best" id="st-b-best">{i_spark}רב מכר</span>
    <h2 id="st-b-title"></h2>
    <div class="st-bd-cats"><span class="lb-dim">{book_in}</span><span id="st-b-cats"></span></div>
    <p class="st-bd-price"><b class="st-gold">119 ₪</b><s>149 ₪</s></p>
    <ul class="st-checks">{book_deals}</ul>
    <button class="lb-btn st-cta is-wide" type="button" id="st-b-go"><span>{book_create}</span>{i_spark}</button>
   </div>
  </div>
 </div>
</dialog>
<dialog class="st-dlg" id="st-sheet" aria-label="{sheet_h}">
 <div class="st-dlg-card st-sheet-card">
  <button class="st-x st-x-float" type="button" data-close aria-label="סגירה">{i_x}</button>
  <img class="st-sheet-img" id="st-s-img" alt="" hidden>
  <div class="st-sheet-body" id="st-s-body">
   <span class="lb-chip accent">{i_info}{sheet_h}</span>
   <h2 id="st-s-h"></h2>
   <p class="lb-muted">{sheet_p}</p>
   <code class="st-s-url lb-ltr" id="st-s-url"></code>
   <a class="lb-btn secondary" id="st-s-open" href="#" target="_blank" rel="noopener" data-real>{i_out}<span>{sheet_open}</span></a>
  </div>
 </div>
</dialog>
<dialog class="st-dlg is-side" id="st-my" aria-label="{my_books}">
 <div class="st-dlg-card st-my-card">
  <header class="st-dlg-head"><h2>{i_book}{my_books}</h2><button class="st-x" type="button" data-close aria-label="סגירה">{i_x}</button></header>
  <div class="st-dlg-body"><div class="st-my-list" id="st-my-list"></div><p class="lb-muted st-my-empty" id="st-my-empty">{my_empty}</p>
   <button class="lb-btn st-cta is-wide" type="button" data-again>{i_spark}<span>{done_again}</span></button></div>
 </div>
</dialog>
"""

DEMO_CSS = r"""
/* ---------- the working demo: dialogs ---------- */
body.st-locked { overflow: hidden; }
.st-dlg { position: fixed; inset: 0; width: 100%; height: 100%; max-width: none; max-height: none; margin: 0; padding: clamp(.4rem, 3vw, 2rem); border: 0;
  background: transparent; color: var(--text); overflow: hidden; }
.st-dlg[open] { display: grid; place-items: center; }
.st-dlg::backdrop { background: rgba(40, 24, 80, .38); }
html.st-night .st-dlg::backdrop { background: rgba(6, 2, 14, .76); -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); }
.st-dlg-card { position: relative; width: min(100%, 54rem); max-height: calc(100dvh - 1.5rem); display: flex; flex-direction: column; border-radius: var(--r-xl); overflow: hidden;
  background: var(--glass-sheen), var(--glass-card-thick); box-shadow: var(--glass-card-rim), 0 0 0 1px rgba(230, 183, 98, .22), 0 40px 90px -30px rgba(0, 0, 0, .95), 0 0 90px -30px rgba(124, 77, 255, .65); }
.st-dlg-head { display: flex; align-items: center; gap: var(--sp-3); padding: var(--sp-3) var(--sp-4); border-bottom: 1px solid var(--line); flex: none; }
.st-dlg-head h2 { display: flex; align-items: center; gap: .5rem; font-size: 1.25rem; }
.st-dlg-head h2 svg, .st-dh svg { width: 1.2rem; height: 1.2rem; color: var(--accent); flex: none; }
.st-dlg-body { padding: var(--sp-4) var(--sp-5) var(--sp-5); overflow-y: auto; min-height: 0; display: grid; gap: var(--sp-4); }
.st-dlg-body > section { display: grid; gap: var(--sp-3); min-width: 0; }
.st .st-dlg-body h2 { font-size: clamp(1.3rem, 2.6vw, 1.7rem); }
.st-x { flex: none; margin-inline-start: auto; display: grid; place-items: center; width: 2.5rem; height: 2.5rem; border-radius: 50%; border: 0; cursor: pointer; background: var(--fill-2); color: var(--text); }
.st-x svg { width: 1.1rem; height: 1.1rem; }
.st-x:hover { background: var(--fill-3); }
.st-x-float { position: absolute; top: .75rem; inset-inline-end: .75rem; z-index: 3; background: var(--st-chip-bg); }
.st-wsteps { list-style: none; display: flex; gap: .35rem; margin: 0; padding: 0; overflow-x: auto; min-width: 0; }
.st-wsteps li { display: inline-flex; align-items: center; gap: .35rem; padding: .25rem .7rem .25rem .3rem; border-radius: var(--r-pill); background: var(--fill); color: var(--text-3);
  font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; white-space: nowrap; transition: background .3s, color .3s, box-shadow .3s; }
.st-wsteps b { display: grid; place-items: center; width: 1.45rem; height: 1.45rem; border-radius: 50%; background: var(--fill-2); color: var(--text-2); font-size: .75rem; }
.st-wsteps li.is-on { color: var(--accent-ink); background: var(--accent-soft); }
.st-wsteps li.is-on b { background: var(--st-gold); color: var(--st-on-gold); }
.st-wsteps li.is-now { box-shadow: inset 0 0 0 1.5px #E6B762, 0 0 18px -6px rgba(230, 183, 98, .9); }
.st-pick-cats { display: flex; gap: var(--sp-2); overflow-x: auto; padding: 3px 2px; }
.st-pick-cats .lb-chip { flex: none; }
.st .st-pick-cats button.lb-chip.cat[aria-pressed="true"] { background: var(--tc-soft); color: var(--tc-ink); box-shadow: inset 0 0 0 1.5px var(--tc); }
.st-pick-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 8.5rem), 1fr)); gap: var(--sp-3); }
.st-pick { position: relative; display: grid; gap: .4rem; align-content: start; padding: .45rem; border: 0; border-radius: var(--r-md); background: var(--fill); color: var(--text);
  font: inherit; text-align: start; cursor: pointer; box-shadow: inset 0 0 0 1px var(--line); transition: transform .25s var(--ease-spring), box-shadow .25s; }
.st-pick img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: calc(var(--r-md) - .3rem); }
.st-pick-t { font-size: var(--fs-footnote); font-weight: 600; line-height: 1.3; }
.st-pick-best { position: absolute; top: .8rem; inset-inline-start: .8rem; font-style: normal; padding: .1rem .5rem; border-radius: var(--r-pill); background: var(--st-gold); color: var(--st-on-gold);
  font-family: var(--font-2); font-size: var(--fs-caption); font-weight: 800; }
.st-pick:hover, .st-pick.is-on { transform: translateY(-4px); box-shadow: inset 0 0 0 1.5px #E6B762, 0 18px 30px -18px rgba(230, 183, 98, .7); }
.st-hero-step { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr); gap: var(--sp-5); align-items: start; }
.st-live-wrap { position: sticky; top: 0; display: grid; gap: var(--sp-2); justify-items: center; }
.st-live-wrap .st-comp { width: 100%; max-width: 20rem; }
.st-live-title { font-weight: 700; text-align: center; color: var(--text-2); }
.st-form { display: grid; gap: .5rem; min-width: 0; }
.st-flabel { font-weight: 700; font-size: var(--fs-callout); margin-top: .35rem; }
.st-form .lb-input { min-height: 2.8rem; font-size: 1.02rem; border-radius: var(--r-md); }
.st-wg { justify-self: start; }
.st-photo-drop { display: flex; align-items: center; gap: var(--sp-3); padding: var(--sp-3); border-radius: var(--r-lg); cursor: pointer; border: 1.5px dashed rgba(230, 183, 98, .45);
  background: rgba(230, 183, 98, .06); transition: background .2s, border-color .2s; }
.st-photo-drop:hover, .st-photo-drop.is-over { background: rgba(230, 183, 98, .14); border-color: var(--accent); }
.st-photo-drop img { display: none; width: 3.6rem; height: 3.6rem; border-radius: 50%; object-fit: cover; box-shadow: 0 0 0 2px #E6B762; flex: none; }
.st-photo-drop.has-photo img { display: block; }
.st-photo-drop.has-photo .st-drop-ic { display: none; }
.st-drop-ic { display: grid; place-items: center; width: 3.6rem; height: 3.6rem; border-radius: 50%; background: var(--accent-soft); color: var(--accent-ink); flex: none; }
.st-drop-ic svg { width: 1.6rem; height: 1.6rem; }
.st-drop-t { display: grid; }
.st-drop-t small { color: var(--text-3); font-size: var(--fs-footnote); }
.st-hint, .st-note { display: flex; gap: .4rem; align-items: flex-start; color: var(--text-3); font-size: var(--fs-footnote); line-height: 1.45; }
.st-hint svg, .st-note svg { width: .95rem; height: .95rem; flex: none; margin-top: .15rem; color: var(--info); }
.st-wnav { display: flex; flex-wrap: wrap; gap: var(--sp-2); justify-content: space-between; margin-top: var(--sp-2); }
.st-need { color: var(--danger); font-weight: 700; }
.st-back-sm { justify-self: start; }
.st .lb-btn:disabled { opacity: .4; cursor: default; filter: none; }

/* the made book: the store's cover, the child's photo in the corner circle and the name on a ribbon */
.st-comp { position: relative; container-type: inline-size; aspect-ratio: 1; border-radius: var(--r-md); overflow: hidden; background: var(--surface-2); box-shadow: 0 0 0 1px rgba(230, 183, 98, .3), 0 24px 40px -18px rgba(0, 0, 0, .85); }
.st-comp-cover { display: block; width: 100%; height: 100%; object-fit: cover; }
.st-comp-photo { position: absolute; top: 5%; left: 5%; width: 25%; aspect-ratio: 1; border-radius: 50%; overflow: hidden; display: grid; place-items: center; background: var(--st-gold); color: var(--st-on-gold);
  font-weight: 800; font-size: 12cqw; box-shadow: 0 0 0 3px #F8F0E1, 0 0 0 5px #E6B762, 0 10px 20px -6px rgba(0, 0, 0, .7); }
.st-comp-photo img { width: 100%; height: 100%; object-fit: cover; }
.st-comp-name { position: absolute; inset-inline: 7%; bottom: 5%; text-align: center; padding: .25em .7em; border-radius: var(--r-pill); background: rgba(11, 5, 24, .74); color: #FFF3D6;
  font-weight: 800; font-size: clamp(.55rem, 6.4cqw, 1.25rem); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; box-shadow: inset 0 0 0 1px rgba(230, 183, 98, .4); }

/* making, preview */
.st-make { display: grid; justify-items: center; gap: var(--sp-4); padding: var(--sp-5) 0; text-align: center; }
.st-make-orb { position: relative; width: min(16rem, 66vw); aspect-ratio: 1; display: grid; place-items: center; }
.st-make-orb i { position: absolute; inset: -12%; border-radius: 50%; background: conic-gradient(from 0deg, rgba(230, 183, 98, 0), #E6B762, #C2AAFF, rgba(230, 183, 98, 0)); filter: blur(18px); }
.st-make-orb img { position: relative; width: 82%; aspect-ratio: 1; object-fit: cover; border-radius: var(--r-lg); box-shadow: 0 0 0 2px rgba(230, 183, 98, .6), 0 20px 40px -14px rgba(0, 0, 0, .8); }
.st-make-msg { font-size: 1.2rem; font-weight: 700; min-height: 1.6em; }
.st-make-bar { width: min(22rem, 80%); height: .5rem; border-radius: var(--r-pill); background: var(--fill-2); overflow: hidden; }
.st-make-bar i { display: block; height: 100%; background: var(--st-gold); transform-origin: right; transform: scaleX(0); box-shadow: 0 0 14px rgba(230, 183, 98, .9); }
.st-center-h { justify-content: center; text-align: center; }
.st-flip { display: grid; gap: var(--sp-3); justify-items: center; }
.st-pages { position: relative; width: min(100%, 24rem); aspect-ratio: 1; perspective: 1400px; cursor: pointer; touch-action: pan-y; }
.st-page { position: absolute; inset: 0; border-radius: var(--r-md); opacity: 0; pointer-events: none; transform-origin: right center; transform: rotateY(-75deg) scale(.94);
  transition: transform .75s var(--ease), opacity .5s var(--ease); }
.st-page.is-past { transform-origin: left center; transform: rotateY(75deg) scale(.94); }
.st-page.is-on { opacity: 1; transform: none; pointer-events: auto; }
.st-page-ded, .st-page-art, .st-page-end { display: grid; place-items: center; align-content: center; gap: var(--sp-3); padding: var(--sp-5); text-align: center; overflow: hidden;
  background: radial-gradient(90% 90% at 50% 0%, #F3D9A1, #F8F0E1 70%); color: #1D1039; box-shadow: 0 0 0 1px rgba(230, 183, 98, .5), 0 24px 40px -18px rgba(0, 0, 0, .85); }
.st-page-ded p { font-size: clamp(1.1rem, 3vw, 1.5rem); font-weight: 700; line-height: 1.5; }
.st-page-spark { font-size: 2.2rem; color: #C9954A; }
.st-page-art img { width: 68%; filter: drop-shadow(0 14px 20px rgba(29, 16, 57, .35)); }
.st-page-art p, .st-page-end p { font-size: clamp(1rem, 2.6vw, 1.2rem); font-weight: 700; }
.st-page-end img { width: 45%; }
.st-flip-nav { display: flex; align-items: center; gap: var(--sp-3); }
.st-dots { display: flex; gap: 6px; }
.st-dots i { width: 7px; height: 7px; border-radius: 4px; background: var(--fill-3); transition: width .25s, background .25s; }
.st-dots i.is-on { width: 20px; background: #E6B762; }

/* order */
.st-order { display: grid; grid-template-columns: minmax(0, 15rem) minmax(0, 1fr); gap: var(--sp-5); align-items: start; }
.st-order-side { display: grid; gap: var(--sp-2); }
.st-order-main { display: grid; gap: var(--sp-3); min-width: 0; }
.st-lines .lb-group-row { justify-content: space-between; }
.st-amt { display: inline-flex; gap: .5rem; align-items: baseline; font-variant-numeric: tabular-nums; white-space: nowrap; }
.st-amt s { color: var(--text-3); text-decoration-color: rgba(255, 138, 147, .9); }
.st-free { color: var(--success); }
.st-extra { display: flex; align-items: center; gap: .6rem; padding: .7rem var(--sp-3); border-radius: var(--r-md); background: var(--accent-soft); box-shadow: inset 0 0 0 1px rgba(230, 183, 98, .35); cursor: pointer; font-weight: 700; }
.st-extra span { display: inline-flex; align-items: center; gap: .4rem; }
.st-extra svg { width: 1.05rem; height: 1.05rem; color: var(--accent-ink); }
.st-extra input, .st-del-opt input { accent-color: var(--accent); width: 1.15rem; height: 1.15rem; flex: none; margin: 0; }
.st-extra-for { display: flex; align-items: center; gap: .6rem; font-size: var(--fs-callout); }
.st-extra-for .lb-select { flex: 1; min-width: 0; }
.st .lb-select { background-color: var(--fill); color: var(--text); border-color: var(--line-strong); }
.st .lb-select option { background: var(--surface); color: var(--text); }
.st-del { border: 0; margin: 0; padding: 0; min-width: 0; }
.st-del legend { font-weight: 700; margin-bottom: .45rem; padding: 0; }
.st-dels { display: grid; gap: .45rem; }
.st-del-opt { display: flex; align-items: center; gap: .7rem; padding: .6rem var(--sp-3); border-radius: var(--r-md); background: var(--fill); box-shadow: inset 0 0 0 1px var(--line); cursor: pointer; }
.st-del-opt:has(input:checked) { background: var(--accent-soft); box-shadow: inset 0 0 0 1.5px #E6B762; }
.st-del-tx { display: grid; flex: 1; min-width: 0; }
.st-del-tx small { color: var(--text-3); font-size: var(--fs-footnote); }
.st-del-cost { font-weight: 800; white-space: nowrap; }
.st-total { display: flex; justify-content: space-between; align-items: baseline; padding: .7rem var(--sp-3); border-radius: var(--r-md); background: var(--st-well);
  box-shadow: inset 0 0 0 1px rgba(230, 183, 98, .3); font-size: 1.1rem; font-weight: 700; }
.st-total b { display: inline-block; font-size: 1.7rem; background: var(--st-gold-text); -webkit-background-clip: text; background-clip: text; color: transparent; }

/* done, book card, sheet, my books */
.st-done { display: grid; justify-items: center; gap: var(--sp-3); text-align: center; padding-block: var(--sp-3); }
.st-done-comp { width: min(18rem, 66vw); }
.st-confetti { position: fixed; top: -14px; width: 9px; height: 14px; border-radius: 2px; z-index: 5; pointer-events: none; }
.st-book-card { width: min(100%, 50rem); }
.st-bd { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); overflow-y: auto; }
.st-bd-vis { position: relative; display: grid; place-items: center; align-content: center; gap: var(--sp-3); padding: var(--sp-5);
  background: radial-gradient(80% 80% at 50% 40%, rgba(124, 77, 255, .45), rgba(124, 77, 255, 0) 70%), var(--st-well); }
.st-bd-vis img { width: 100%; max-width: 20rem; aspect-ratio: 1; object-fit: cover; border-radius: var(--r-lg); box-shadow: 0 0 0 1px rgba(230, 183, 98, .35), 0 30px 50px -20px rgba(0, 0, 0, .9); }
.st-bd-text { display: grid; gap: var(--sp-3); align-content: center; padding: var(--sp-5); }
.st-bd-text .st-best { justify-self: start; }
.st-bd-cats { display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; font-size: var(--fs-footnote); }
.st-bd-cats > span:last-child { display: contents; }
.st-bd-price { display: flex; align-items: baseline; gap: .7rem; }
.st-bd-price b { font-size: 2.6rem; font-weight: 800; line-height: 1; }
.st-bd-price s { color: var(--text-3); font-size: 1.2rem; text-decoration-color: rgba(255, 138, 147, .9); }
.st-sheet-card { width: min(100%, 30rem); }
.st-sheet-body { display: grid; gap: var(--sp-3); padding: var(--sp-5); justify-items: start; }
.st-s-url { font-size: var(--fs-footnote); color: var(--accent-ink); background: var(--fill); padding: .3rem .6rem; border-radius: var(--r-sm); word-break: break-all; }
#st-sheet.is-light .st-sheet-card { width: min(100%, 42rem); background: #0B0518; }
.st-sheet-img { display: block; width: 100%; max-height: 82dvh; object-fit: contain; }
.st-dlg.is-side[open] { place-items: stretch start; padding: 0; }
.st-my-card { width: min(100%, 26rem); max-height: none; height: 100dvh; border-radius: 0; }
.st-my-list { display: grid; gap: var(--sp-3); }
.st-my-item { display: grid; grid-template-columns: 6.5rem minmax(0, 1fr); gap: var(--sp-3); align-items: center; padding: var(--sp-3); }
.st-my-tx { display: grid; gap: .3rem; min-width: 0; }
.st-my-tx small { color: var(--text-3); }
.st-my-btn { flex: none; }
.st-my-btn svg { width: 1rem; height: 1rem; }
.st-my-n { display: grid; place-items: center; min-width: 1.35rem; height: 1.35rem; padding-inline: .3rem; border-radius: var(--r-pill); background: var(--st-gold); color: var(--st-on-gold); font-size: .75rem; }

@keyframes st-dlg-in { from { opacity: 0; transform: translateY(26px) scale(.95); } to { opacity: 1; transform: none; } }
@keyframes st-drawer { from { transform: translateX(100%); } to { transform: none; } }
@keyframes st-fall { from { transform: translate(0, 0) rotate(0); opacity: 1; } to { transform: translate(var(--sx), 106vh) rotate(var(--rot)); opacity: .85; } }
@keyframes st-msg { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
@keyframes st-num { 0% { transform: scale(1); } 40% { transform: scale(1.16); } 100% { transform: scale(1); } }
.st-anim .st-dlg[open] .st-dlg-card { --dur: .5s; animation: st-dlg-in var(--dur) var(--ease-spring); }
.st-anim .st-dlg.is-side[open] .st-dlg-card { animation-name: st-drawer; }
.st-anim .st-confetti { animation: st-fall var(--dur, 3s) cubic-bezier(.25, .6, .4, 1) forwards; }
.st-anim .st-make-orb i { --dur: 2.2s; animation: st-spin var(--dur) linear infinite; }
.st-anim .st-make-orb img { --r: 0deg; --dur: 3s; animation: st-float var(--dur) ease-in-out infinite; }
.st-anim .st-make-msg.is-new { --dur: .45s; animation: st-msg var(--dur) var(--ease); }
.st-anim .st-total b.is-new { --dur: .45s; animation: st-num var(--dur) var(--ease-spring); }
.st-anim .st-pick { --dur: .5s; animation: st-pop var(--dur) var(--ease-spring) both; animation-delay: calc(var(--i, 0) * 30ms); }
.st-anim .st-bd-vis img, .st-anim .st-done-comp { --r: 0deg; --dur: 6s; animation: st-float var(--dur) ease-in-out infinite; }
.st-anim .st-live-wrap .st-comp { --r: -2deg; --dur: 6s; animation: st-float var(--dur) ease-in-out infinite; }
.st-anim .st-page-spark { --dur: 2s; animation: st-twinkle var(--dur) ease-in-out infinite; }
@media (prefers-reduced-motion: reduce) {
  html.st-full .st-confetti { animation-duration: var(--dur, 3s) !important; }
}
@media (max-width: 720px) {
  .st-hero-step, .st-order, .st-bd { grid-template-columns: minmax(0, 1fr); }
  .st-live-wrap { position: static; }
  .st-live-wrap .st-comp { max-width: 13rem; }
  .st-order-side .st-comp { max-width: 12rem; }
  .st-dlg-body { padding: var(--sp-3) var(--sp-4) var(--sp-4); }
  .st-my-l { display: none; }
  .st-bd-vis { padding: var(--sp-5) var(--sp-4) var(--sp-2); }
  .st-bd-vis img { max-width: 13rem; }
  .st-bd-text { padding: var(--sp-4); }
}
"""

DEMO_JS = r"""
  // ======================= the working demo =======================
  var X = D.demo, BK = D.books, LS = 'st-mybooks', memory = null, makeTimer = 0;
  var W = $('#st-wiz'), BD = $('#st-bookdlg'), SH = $('#st-sheet'), MY = $('#st-my');
  var S = { id: null, name: '', g: null, photo: '', ded: '', extra: false, extraId: null, del: 0, total: 0 }, pickCat = Object.keys(D.cats)[0], page = 0;
  function bookCover(id, g) { var b = BK[id]; if (!b) return ''; var gg = b[3] ? 'b' : (g || b[1]), w = gg === 'g' ? 'girl' : 'boy'; return D.store + '/book_covers/' + w + '/B' + id + '_' + w + '.webp'; }
  function mk(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function fill(s, o) { return String(s).replace(/\{(\w+)\}/g, function (m, k) { return o[k] != null ? o[k] : m; }); }
  function heroGender() { var p = $('.st-hero .st-g [aria-pressed="true"]') || $('.st-g [aria-pressed="true"]'); return p ? p.getAttribute('data-g') : null; }
  function openDlg(d) { if (!d.open) { try { d.showModal(); } catch (e) { d.setAttribute('open', ''); } } document.body.classList.add('st-locked'); }
  function closeDlg(d) { if (d.open) { try { d.close(); } catch (e) { d.removeAttribute('open'); } } if (!$$('dialog.st-dlg[open]').length) document.body.classList.remove('st-locked'); }
  $$('dialog.st-dlg').forEach(function (d) {
    d.addEventListener('click', function (e) { if (e.target === d || (e.target.closest && e.target.closest('[data-close]'))) closeDlg(d); });
    d.addEventListener('close', function () { if (d === W) clearInterval(makeTimer); if (!$$('dialog.st-dlg[open]').length) document.body.classList.remove('st-locked'); });
  });
  function composite(box, id, g, photo, name) {
    box.textContent = '';
    var im = mk('img', 'st-comp-cover'); im.src = bookCover(id, g); im.alt = ''; box.appendChild(im);
    var ph = mk('span', 'st-comp-photo');
    if (photo) { var p = mk('img'); p.src = photo; p.alt = ''; ph.appendChild(p); } else ph.textContent = (name || '?').charAt(0);
    box.appendChild(ph);
    if (name) box.appendChild(mk('span', 'st-comp-name', X.star + ' ' + name));
  }

  // ---------- my books: this browser only ----------
  function myLoad() { try { return JSON.parse(localStorage.getItem(LS) || '[]') || []; } catch (e) { return []; } }
  function mySave(l) { try { localStorage.setItem(LS, JSON.stringify(l.slice(0, 12))); memory = null; return true; } catch (e) { memory = l.slice(0, 12); return false; } }
  function myList() { return memory || myLoad(); }
  function myCount() { $('#st-my-n').textContent = myList().length; }
  function openMy() {
    var list = myList(), box = $('#st-my-list'); box.textContent = '';
    $('#st-my-empty').hidden = list.length > 0;
    list.forEach(function (b, i) {
      if (!BK[b.id]) return;
      var row = mk('div', 'lb-card st-my-item'), cv = mk('div', 'st-comp'); composite(cv, b.id, b.g, b.photo, b.name); row.appendChild(cv);
      var tx = mk('div', 'st-my-tx'); tx.appendChild(mk('b', '', BK[b.id][0])); tx.appendChild(mk('small', '', X.star + ' ' + b.name + ' · ' + b.total + ' ₪'));
      var acts = mk('div', 'lb-row'), o = mk('button', 'lb-btn sm', X.my_open), r = mk('button', 'lb-btn ghost sm', X.my_remove); o.type = r.type = 'button';
      o.onclick = function () { closeDlg(MY); S = { id: b.id, name: b.name, g: b.g, photo: b.photo || '', ded: b.ded || '', extra: !!b.extra, extraId: b.extraId || null, del: b.del || 0, total: b.total }; openDlg(W); go(4); };
      r.onclick = function () { var l = myList(); l.splice(i, 1); mySave(l); myCount(); openMy(); };
      acts.appendChild(o); acts.appendChild(r); tx.appendChild(acts); row.appendChild(tx); box.appendChild(row);
    });
    openDlg(MY);
  }

  // ---------- the book maker ----------
  function go(n) {
    $$('[data-step]', W).forEach(function (s) { s.hidden = +s.getAttribute('data-step') !== n; });
    var k = Math.min(n, 5); $$('.st-wsteps li', W).forEach(function (li, i) { li.classList.toggle('is-on', i < k); li.classList.toggle('is-now', i === k - 1); });
    $('.st-dlg-body', W).scrollTop = 0;
    if (n === 1) renderPick(); else if (n === 2) renderHero(); else if (n === 3) runMake(); else if (n === 4) renderPreview(); else if (n === 5) renderOrder(); else if (n === 6) renderDone();
  }
  function startWizard(o) {
    o = o || {};
    var hn = $('#st-name').value.replace(/\s+/g, ' ').trim().slice(0, 20); if (hn) S.name = hn;
    var hg = heroGender(); if (o.g) S.g = o.g; else if (hg) S.g = hg;
    if (o.extra) S.extra = true;
    if (o.id) S.id = String(o.id);
    closeDlg(SH); openDlg(W); go(o.id ? 2 : 1);
  }
  $$('[data-goto]', W).forEach(function (b) { b.addEventListener('click', function () { go(+b.getAttribute('data-goto')); }); });
  $$('[data-again]').forEach(function (b) { b.addEventListener('click', function () { closeDlg(MY); S.id = null; S.photo = ''; S.ded = ''; S.extra = false; openDlg(W); go(1); }); });
  $$('[data-my]').forEach(function (b) { b.addEventListener('click', function () { closeDlg(W); openMy(); }); });

  function renderPick() {
    var cb = $('.st-pick-cats', W), grid = $('.st-pick-grid', W); cb.textContent = ''; grid.textContent = '';
    Object.keys(D.cats).forEach(function (k) {
      var b = mk('button', 'lb-chip cat no-swatch ' + D.catCls[k], D.catLabel[k]); b.type = 'button'; b.setAttribute('aria-pressed', k === pickCat ? 'true' : 'false');
      b.onclick = function () { pickCat = k; renderPick(); }; cb.appendChild(b);
    });
    D.cats[pickCat].ids.forEach(function (id, i) {
      id = String(id); if (!BK[id]) return;
      var b = mk('button', 'st-pick' + (S.id === id ? ' is-on' : '')); b.type = 'button'; b.style.setProperty('--i', i);
      var im = mk('img'); im.src = bookCover(id, S.g); im.alt = ''; im.loading = 'lazy'; b.appendChild(im);
      b.appendChild(mk('span', 'st-pick-t', BK[id][0])); if (BK[id][2]) b.appendChild(mk('i', 'st-pick-best', D.best));
      b.onclick = function () { S.id = id; burstAt(b, 12); setTimeout(function () { go(2); }, 180); };
      grid.appendChild(b);
    });
  }
  var wName = $('#st-w-name'), wDed = $('#st-w-ded'), wFile = $('#st-w-file'), drop = $('.st-photo-drop', W), wMake = $('#st-w-make');
  function live() { composite($('#st-w-live'), S.id, S.g, S.photo, S.name); $('#st-w-book-title').textContent = BK[S.id] ? BK[S.id][0] : ''; }
  function photoUi() { drop.classList.toggle('has-photo', !!S.photo); if (S.photo) $('#st-w-photo').src = S.photo; else $('#st-w-photo').removeAttribute('src'); $('#st-w-photo-btn').textContent = S.photo ? X.photo_change : X.photo_btn; }
  function renderHero() {
    if (!S.id) { go(1); return; }
    wName.value = S.name; wDed.value = S.ded; $('#st-w-need').hidden = true;
    $$('[data-wg]', W).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-wg') === S.g ? 'true' : 'false'); });
    photoUi(); live();
    if (fine && !S.name) setTimeout(function () { wName.focus(); }, 80);
  }
  wName.addEventListener('input', function () { S.name = wName.value.replace(/\s+/g, ' ').trim().slice(0, 20); live(); });
  wName.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); wMake.click(); } });
  wDed.addEventListener('input', function () { S.ded = wDed.value.trim().slice(0, 120); });
  $$('[data-wg]', W).forEach(function (b) { b.addEventListener('click', function () { S.g = b.getAttribute('data-wg'); $$('[data-wg]', W).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); live(); burstAt(b, 6); }); });
  function takeFile(f) {
    if (!f || !/^image\//.test(f.type)) return;
    var r = new FileReader();
    r.onload = function () {
      var im = new Image();
      im.onload = function () { var s = 320, cv = document.createElement('canvas'), k = Math.min(im.width, im.height); cv.width = cv.height = s; cv.getContext('2d').drawImage(im, (im.width - k) / 2, (im.height - k) / 2, k, k, 0, 0, s, s); S.photo = cv.toDataURL('image/jpeg', .82); photoUi(); live(); burstAt(drop, 14); };
      im.src = r.result;
    };
    r.readAsDataURL(f);
  }
  wFile.addEventListener('change', function () { takeFile(wFile.files && wFile.files[0]); wFile.value = ''; });
  ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('is-over'); }); });
  ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('is-over'); }); });
  drop.addEventListener('drop', function (e) { takeFile(e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]); });
  wMake.addEventListener('click', function () { if (!S.name || !S.g) { $('#st-w-need').hidden = false; (S.name ? $('[data-wg]', W) : wName).focus(); return; } go(3); });

  function runMake() {
    var msgs = X.loading, bar = $('#st-w-bar'), msg = $('#st-w-msg'), t0 = performance.now(), len = ANIM ? 3800 : 1200, k0 = -1, orb = $('.st-make-orb', W);
    $('#st-w-make-img').src = bookCover(S.id, S.g); bar.style.transform = 'scaleX(0)'; clearInterval(makeTimer);
    makeTimer = setInterval(function () {
      var p = Math.min(1, (performance.now() - t0) / len), k = Math.min(msgs.length - 1, Math.floor(p * msgs.length));
      bar.style.transform = 'scaleX(' + p.toFixed(3) + ')';
      if (k !== k0) { k0 = k; msg.textContent = fill(msgs[k], { name: S.name }); msg.classList.remove('is-new'); void msg.offsetWidth; msg.classList.add('is-new'); }
      if (Math.random() < .45) burstAt(orb, 2);
      if (p >= 1) { clearInterval(makeTimer); go(4); }
    }, 110);
  }
  function renderPreview() {
    $('#st-w-ph').textContent = fill(X.preview_h, { name: S.name });
    var g = S.g === 'g' ? 'g' : 'b', T = X['pages_' + g], ded = S.ded || X['ded_default_' + g], box = $('#st-w-pages'); box.textContent = '';
    var p0 = mk('div', 'st-page st-comp'); composite(p0, S.id, S.g, S.photo, S.name); box.appendChild(p0);
    var p1 = mk('div', 'st-page st-page-ded'); p1.appendChild(mk('span', 'st-page-spark', '✦')); p1.appendChild(mk('p', '', fill(T[0], { name: S.name, ded: ded }))); box.appendChild(p1);
    var p2 = mk('div', 'st-page st-page-art'), a = mk('img'); a.src = D.store + D.pages[g]; a.alt = ''; p2.appendChild(a); p2.appendChild(mk('p', '', fill(T[1], { name: S.name }))); box.appendChild(p2);
    var p3 = mk('div', 'st-page st-page-end'), l = mk('img'); l.src = D.store + D.pages.lume; l.alt = ''; p3.appendChild(l); p3.appendChild(mk('p', '', T[2])); box.appendChild(p3);
    showPage(0);
  }
  function showPage(n) {
    var pages = $$('.st-page', W), dots = $('#st-w-dots'); page = Math.max(0, Math.min(pages.length - 1, n));
    pages.forEach(function (p, i) { p.classList.toggle('is-on', i === page); p.classList.toggle('is-past', i < page); });
    dots.textContent = ''; pages.forEach(function (p, i) { dots.appendChild(mk('i', i === page ? 'is-on' : '')); });
    $('#st-w-prev').disabled = page === 0; $('#st-w-next').disabled = page === pages.length - 1;
  }
  $('#st-w-prev').addEventListener('click', function () { showPage(page - 1); });
  $('#st-w-next').addEventListener('click', function () { showPage(page + 1); burstAt($('#st-w-pages'), 6); });
  (function () {
    var x0 = null, box = $('#st-w-pages');
    box.addEventListener('pointerdown', function (e) { x0 = e.clientX; });
    box.addEventListener('pointerup', function (e) { if (x0 == null) return; var dx = e.clientX - x0; x0 = null; if (Math.abs(dx) > 40) showPage(page + (dx > 0 ? 1 : -1)); else showPage(page + 1 > $$('.st-page', W).length - 1 ? 0 : page + 1); });
  })();
  function renderOrder() {
    composite($('#st-o-comp'), S.id, S.g, S.photo, S.name); $('#st-o-title').textContent = BK[S.id][0];
    var sel = $('#st-o-extra-id'); sel.textContent = '';
    D.cats[Object.keys(D.cats)[0]].ids.forEach(function (id) { id = String(id); var o = mk('option', '', BK[id][0]); o.value = id; sel.appendChild(o); });
    sel.value = S.extraId && BK[S.extraId] ? S.extraId : (sel.querySelector('option[value="' + S.id + '"]') ? S.id : sel.options[0].value);
    $('#st-o-extra').checked = S.extra;
    var box = $('#st-o-dels'); box.textContent = '';
    X.delivery.forEach(function (d, i) {
      var lab = mk('label', 'st-del-opt'), r = mk('input'); r.type = 'radio'; r.name = 'st-del'; r.value = i; r.checked = i === S.del;
      r.onchange = function () { S.del = i; total(); };
      lab.appendChild(r); var tx = mk('span', 'st-del-tx'); tx.appendChild(mk('b', '', d[0])); tx.appendChild(mk('small', '', d[2])); lab.appendChild(tx);
      lab.appendChild(mk('span', 'st-del-cost', d[1] ? d[1] + ' ₪' : X.free)); box.appendChild(lab);
    });
    total();
  }
  function total() {
    var d = X.delivery[S.del] || X.delivery[0], sum = D.price + (S.extra ? D.extra : 0) + d[1], sid = $('#st-o-extra-id').value;
    $('#st-o-extra-row').hidden = !S.extra; $('#st-o-extra-for').hidden = !S.extra;
    S.extraId = sid; $('#st-o-extra-name').textContent = BK[sid] ? BK[sid][0] : '';
    $('#st-o-del-name').textContent = d[0]; $('#st-o-del-cost').textContent = d[1] ? d[1] + ' ₪' : X.free;
    var t = $('#st-o-total'); t.textContent = sum + ' ₪'; t.classList.remove('is-new'); void t.offsetWidth; t.classList.add('is-new');
    S.total = sum;
  }
  $('#st-o-extra').addEventListener('change', function () { S.extra = this.checked; total(); if (S.extra) burstAt(this.parentNode, 10); });
  $('#st-o-extra-id').addEventListener('change', total);
  $('#st-o-confirm').addEventListener('click', function () {
    var l = myList(); l.unshift({ id: S.id, name: S.name, g: S.g, photo: S.photo, ded: S.ded, extra: S.extra, extraId: S.extraId, del: S.del, total: S.total, at: Date.now() });
    mySave(l); myCount(); go(6);
  });
  function renderDone() {
    composite($('#st-d-comp'), S.id, S.g, S.photo, S.name);
    $('#st-d-h').textContent = fill(X.done_h, { name: S.name });
    if (!ANIM) return;
    var cols = ['#F3D9A1', '#E6B762', '#C2AAFF', '#FF98BD', '#74E6E2', '#FFFFFF'];
    for (var i = 0; i < 90; i++) {
      var c = mk('i', 'st-confetti'); c.style.left = (Math.random() * 100).toFixed(1) + 'vw'; c.style.background = cols[i % cols.length];
      c.style.setProperty('--dur', (2.2 + Math.random() * 2).toFixed(2) + 's'); c.style.animationDelay = (Math.random() * .6).toFixed(2) + 's';
      c.style.setProperty('--rot', (Math.random() * 720 - 360).toFixed(0) + 'deg'); c.style.setProperty('--sx', (Math.random() * 160 - 80).toFixed(0) + 'px');
      c.addEventListener('animationend', function () { this.remove(); }); W.appendChild(c);
    }
    var r = $('.st-dlg-card', W).getBoundingClientRect();
    for (var k = 0; k < 5; k++) setTimeout(function () { spark(r.left + Math.random() * r.width, r.top + Math.random() * r.height * .6, 14, 80, true); }, k * 170);
  }

  // ---------- a book's card ----------
  var bdId = null, bdG = null;
  function bdCover() { $('#st-b-img').src = bookCover(bdId, bdG); $$('[data-bg]', BD).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-bg') === bdG ? 'true' : 'false'); }); }
  function openBook(id) {
    id = String(id); if (!BK[id]) return; bdId = id; bdG = heroGender() || BK[id][1];
    $('#st-b-title').textContent = BK[id][0]; $('#st-b-best').hidden = !BK[id][2];
    var cb = $('#st-b-cats'); cb.textContent = '';
    Object.keys(D.cats).forEach(function (k) {
      if (D.cats[k].ids.map(String).indexOf(id) < 0) return;
      var b = mk('button', 'lb-chip cat no-swatch ' + D.catCls[k], D.catLabel[k]); b.type = 'button'; b.onclick = function () { closeDlg(BD); setCat(k, true); }; cb.appendChild(b);
    });
    bdCover(); openDlg(BD);
  }
  $$('[data-bg]', BD).forEach(function (b) { b.addEventListener('click', function () { bdG = b.getAttribute('data-bg'); bdCover(); burstAt(b, 6); }); });
  $('#st-b-go').addEventListener('click', function () { closeDlg(BD); startWizard({ id: bdId, g: bdG }); });

  // ---------- a sheet: what a link does in the real store, or a picture up close ----------
  function sheet(title, href, src) {
    var im = $('#st-s-img'), body = $('#st-s-body');
    if (src) { im.src = src; im.alt = title || ''; im.hidden = false; body.hidden = true; SH.classList.add('is-light'); }
    else {
      im.hidden = true; body.hidden = false; SH.classList.remove('is-light');
      var full = /^(https?:|mailto:)/.test(href) ? href : D.store + href;
      $('#st-s-h').textContent = title || ''; $('#st-s-url').textContent = full.replace(/^https?:\/\//, '').replace(/^mailto:/, ''); $('#st-s-open').href = full;
    }
    openDlg(SH);
  }
  function setCat(k, scroll, all) {
    var b = $('.st-cats [data-cat="' + k + '"]'); if (!b) return;
    cur = k; open = !!all; $$('.st-cats [data-cat]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    shelf(true); if (scroll) $('#books').scrollIntoView({ behavior: ANIM ? 'smooth' : 'auto', block: 'start' });
  }

  // ---------- every link stays in the page ----------
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a'); if (!a || !a.closest('.st') || a.hasAttribute('data-real')) return;
    var href = a.getAttribute('href') || ''; if (href.charAt(0) === '#') return;
    e.preventDefault();
    var path = href.replace(/^https?:\/\/[^\/]+/, '').replace(/\/$/, '');
    if (a.hasAttribute('data-cta') || /\/wizard$/.test(path)) { startWizard({ extra: a.hasAttribute('data-extra') }); return; }
    if (a.classList.contains('st-logo')) { window.scrollTo({ top: 0, behavior: ANIM ? 'smooth' : 'auto' }); return; }
    var m = /\/books\/(\d+)$/.exec(path); if (m) { openBook(m[1]); return; }
    if (a.id === 'st-all') { open = true; shelf(true); return; }
    var cm = /\/category\/([\w-]+)$/.exec(path); if (cm && D.catByHref[cm[1]]) { setCat(D.catByHref[cm[1]], true); return; }
    if (/\/gifts\/hanukkah$/.test(path)) { setCat('holidays', true); return; }
    if (/\/IL\/he\/books$/.test(path)) { setCat(cur, true, true); return; }
    if (/\/my-books$/.test(path)) { openMy(); return; }
    sheet((a.textContent || '').trim(), href);
  });
  $$('.st-ugc-item').forEach(function (f) { f.style.cursor = 'zoom-in'; f.addEventListener('click', function () { var im = $('img', f); sheet(im.alt, '', im.src); }); });
  var ban = $('.st-banner'); if (ban) { ban.style.cursor = 'zoom-in'; ban.addEventListener('click', function () { var im = $('img', ban); sheet(im.alt, '', im.src); }); }
  myCount();

  // ---------- dark and light (this browser remembers the choice) ----------
  var tbtn = $('#st-theme');
  function themeUi() {
    var dark = root.classList.contains('st-night'), lab = dark ? D.theme.to_light : D.theme.to_dark;
    tbtn.setAttribute('aria-label', lab); tbtn.title = lab;
    var m = $('meta[name="theme-color"]'); if (m) m.content = dark ? '#0B0518' : '#FFFFFF';
  }
  function flipTheme() { root.classList.toggle('st-night'); try { localStorage.setItem('st-theme', root.classList.contains('st-night') ? 'dark' : 'light'); } catch (e) {} themeUi(); }
  tbtn.addEventListener('click', function (e) {
    var r0 = tbtn.getBoundingClientRect(), x = e.clientX || (r0.left + r0.width / 2), y = e.clientY || (r0.top + r0.height / 2);
    if (ANIM && document.startViewTransition) {
      var rad = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y)), vt = document.startViewTransition(flipTheme);
      vt.ready.then(function () { root.animate({ clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + rad + 'px at ' + x + 'px ' + y + 'px)'] }, { duration: 750, easing: 'cubic-bezier(.22, 1, .36, 1)', pseudoElement: '::view-transition-new(root)' }); });
      vt.finished.then(function () { spark(x, y, 16, 80, true); });
    } else { flipTheme(); spark(x, y, 14, 70, true); }
  });
  themeUi();
"""

MOBILE_CSS = r"""
/* ---------- phones (Yarin, 09 / 11 / 2026: "review the mobile version, it needs to be perfect"). Last in the file so it wins. ---------- */
.st-cta-short, .st-cta-tiny { display: none; }
.st a.st-promo, .st a.st-promo:hover { color: var(--st-promo-ink); text-decoration: none; }
.st-promo .st-promo-link { display: inline-flex; align-items: center; gap: .25rem; flex: none; color: var(--st-promo-ink); font-weight: 700; padding: .1rem .65rem;
  border-radius: var(--r-pill); background: var(--fill); box-shadow: inset 0 0 0 1px rgba(230, 183, 98, .35); transition: background .2s, color .2s; }
.st a.st-promo:hover .st-promo-link { color: var(--st-on-gold); background: var(--st-gold); }
.st-help { margin-top: .6rem; gap: .5rem; }
/* floating sheets blur what is behind them (design system: floating cards blur); light ones are near solid so the page never reads through */
.st-dlg-card { -webkit-backdrop-filter: var(--glass-filter); backdrop-filter: var(--glass-filter); }
html:not(.st-night) .st-dlg-card { background: var(--glass-sheen), rgba(255, 255, 255, .95); }
html:not(.st-night) #st-sheet.is-light .st-sheet-card { background: #0B0518; }
.st p, .st-checks li span, .st-deal-body small, .st-step p, .st blockquote { text-wrap: pretty; }
.st-help .lb-btn svg { width: 1rem; height: 1rem; }
.st-order-cta { display: grid; gap: var(--sp-3); }
.st-notice .lb-ltr { white-space: nowrap; }
.st-faq .lb-disclosure-body { padding-inline-start: calc(var(--sp-4) + 1.9rem + var(--sp-3)); }
@keyframes st-sheet-up { from { transform: translateY(100%); } to { transform: none; } }
@media (max-width: 1000px) { .st-anim .st-steps::before { display: none; } }
/* phones: the hero picture comes first, above the headline (Yarin, 09 / 11 / 2026) */
@media (max-width: 760px) {
  .st-hero > .st-stage { order: -1; margin-top: -.25rem; }
  .st-hero { padding-block-start: var(--sp-2); }
  /* and without Lume, the name tag and the age chip (Yarin, 09 / 11 / 2026: "remove all of it") */
  .st-hero .st-lume, .st-hero .st-tag, .st-hero .lb-hero-text > .lb-chip { display: none; }
  /* no empty strip under the picture (Yarin's marked screenshot, 09 / 11 / 2026): the low small book moves up beside the main one
     and the text starts right under the main book */
  .st-hero .st-mini.m3 { bottom: auto; top: 46%; width: 24%; }
  .st .st-stage { margin-bottom: calc(min(21rem, 100%) * -.2); }
  .st-hero > .lb-hero-text { position: relative; z-index: 7; }
}

@media (max-width: 640px) {
  /* every tap target 44px */
  .st a.st-promo { min-height: 2.75rem; padding-block: .35rem; flex-wrap: nowrap; }
  .st-promo .st-promo-l { display: none; }
  .st-promo .st-promo-link { padding: .3rem .4rem; }
  .st-bar .st-logo { min-height: 2.75rem; display: inline-flex; align-items: center; }
  .st-bar .st-logo { flex: none; }
  .st-bar .st-mock { display: none; }
  .st-bar .st-logo img { height: 2.6rem; width: 2.6rem; object-fit: contain; }
  .st .st-bar .lb-btn { min-height: 2.75rem; }
  .st-theme { width: 2.75rem; }
  .st .lb-segmented button { min-height: 2.75rem; }
  .st .st-cats .lb-chip { min-height: 2.75rem; }
  .st .lb-btn.sm { min-height: 2.75rem; }
  .st-x { width: 2.75rem; height: 2.75rem; }
  .st .st-bd-cats .lb-chip, .st .st-pick-cats .lb-chip { min-height: 2.75rem; padding-inline: .95rem; font-size: var(--fs-callout); }
  .st-groups { min-height: 2.75rem; }
  .st .st-foot-col a { min-height: 2.75rem; }
  .st-foot-col { gap: 0; }
  .st-foot-cols { row-gap: var(--sp-5); }
  .st h2 { align-items: flex-start; }
  .st-h-ic { width: 1.35rem; height: 1.35rem; margin-top: .3rem; }

  /* hero: the start card's checks in one column, the floating books inside the screen, the name tag under the picture */
  .st-start .st-checks { grid-template-columns: minmax(0, 1fr); }
  .st-stage { max-width: 21rem; margin-bottom: 2.6rem; }
  .st-main { width: 70%; left: 15%; top: 12%; }
  .st-mini { width: 27%; }
  .st-mini.m1 { top: 0; inset-inline-start: 0; }
  .st-mini.m2 { top: 4%; inset-inline-end: 0; width: 25%; }
  .st-mini.m3 { bottom: 6%; inset-inline-end: 0; }
  .st-lume { width: 25%; bottom: 0; inset-inline-start: 0; }
  .st-tag { top: calc(100% + .35rem); bottom: auto; font-size: var(--fs-footnote); }

  /* the three numbers on one row */
  .st .lb-metrics.st-stats { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .5rem; }
  .st-stats .lb-metric { padding: .75rem .35rem .7rem; justify-items: center; text-align: center; gap: .3rem; }
  .st-stats .lb-metric-label { flex-direction: column; gap: .3rem; font-size: var(--fs-footnote); }
  .st-stats .lb-metric-label > .lb-tile { width: 1.9rem; height: 1.9rem; }
  .st-stats .lb-metric-value { justify-content: center; font-size: 1.45rem; }
  .st-mq-cap { font-size: 1rem; text-align: center; padding-inline: 1.5rem; }
  .st-mq-cap svg { display: none; }

  /* steps and reasons as compact rows */
  .st-step { grid-template-columns: 6.25rem minmax(0, 1fr); column-gap: .9rem; row-gap: .15rem; align-items: center; padding: .7rem; position: relative; }
  .st-step-vis { grid-row: 1 / span 2; margin: 0; width: 6.25rem; height: 6.25rem; border-radius: var(--r-md); }
  .st-step-head { position: absolute; top: .35rem; inset-inline-start: .35rem; z-index: 2; }
  .st-step-head .lb-tile { display: none; }
  .st .lb-disc.st-disc { width: 1.85rem; height: 1.85rem; font-size: var(--fs-footnote); }
  .st-step h3 { align-self: end; }
  .st-step p { align-self: start; font-size: var(--fs-callout); line-height: 1.45; }
  .st-fan { transform: scale(.6); }
  .st-upload { width: 4rem; height: 4rem; }
  .st-upload svg { width: 1.7rem; height: 1.7rem; }
  .st-step-book { height: 5.4rem; }
  .st-why-card { grid-template-columns: auto minmax(0, 1fr); column-gap: .85rem; row-gap: .15rem; align-items: start; padding: var(--sp-3) var(--sp-4); }
  .st-why-card > .lb-tile { grid-row: 1 / span 2; }

  /* price and deals */
  .st-offer { padding: var(--sp-4); }
  .st-offer-top { flex-direction: row; align-items: center; gap: var(--sp-3); }
  .st-offer-cover { width: 5.5rem; }
  .st-amount b { font-size: 2.6rem; }
  .st-was s { font-size: 1.1rem; }
  .st-deal { position: relative; grid-template-columns: 4.5rem minmax(0, 1fr); align-items: start; }
  .st-deal-badge { position: absolute; top: .7rem; inset-inline-end: .7rem; grid-column: auto; padding: .2rem .6rem; font-size: var(--fs-footnote); }
  .st-deal-title { padding-inline-end: 4.4rem; }

  /* faq, final, footer */
  .st-faq .lb-disclosure-body { padding-inline-start: var(--sp-4); }
  .st-final { padding: 1rem .6rem .6rem; }
  .st-final-card { padding: var(--sp-5) var(--sp-4); }

  /* dialogs are bottom sheets */
  .st-dlg { padding: 0; }
  .st-dlg[open], .st-dlg.is-side[open] { place-items: end stretch; }
  .st-dlg-card, .st-book-card, .st-sheet-card, .st-my-card { width: 100%; height: auto; max-height: calc(100dvh - .75rem); border-radius: var(--r-xl) var(--r-xl) 0 0; }
  .st-dlg-card::before { content: ""; position: absolute; top: .4rem; left: 50%; width: 2.4rem; height: .3rem; margin-left: -1.2rem; border-radius: 3px; background: var(--fill-3); z-index: 4; }
  .st-anim .st-dlg[open] .st-dlg-card, .st-anim .st-dlg.is-side[open] .st-dlg-card { animation-name: st-sheet-up; }
  #st-sheet.is-light[open] { place-items: center; padding: .5rem; }
  #st-sheet.is-light .st-sheet-card { border-radius: var(--r-lg); }
  .st-dlg-head { padding: 1rem var(--sp-3) .6rem; }
  .st-x-float { top: 1rem; }
  .st-wsteps li:not(.is-now) span { display: none; }
  .st-wsteps li:not(.is-now) { padding: .25rem; }
  .st-dlg-body { padding: var(--sp-3) var(--sp-4) 0; }
  .st-dlg-body > section { padding-bottom: var(--sp-4); }
  .st-my-card .st-dlg-body { padding-bottom: calc(var(--sp-4) + env(safe-area-inset-bottom)); }
  .st-live-wrap { position: static; grid-template-columns: 5.5rem minmax(0, 1fr); justify-items: start; align-items: center; column-gap: var(--sp-3); }
  .st-live-wrap .st-comp { grid-row: 1 / span 2; width: 5.5rem; max-width: none; }
  .st-live-title { text-align: start; }
  .st-hero-step { gap: var(--sp-3); }
  .st-wg, .st-bg { justify-self: stretch; display: grid; grid-template-columns: 1fr 1fr; }
  .st-wnav, .st-order-cta { position: sticky; bottom: 0; z-index: 5; margin: var(--sp-2) calc(var(--sp-4) * -1) 0; padding: .7rem var(--sp-4) calc(.7rem + env(safe-area-inset-bottom));
    background: var(--glass-sheen), var(--glass-thick); -webkit-backdrop-filter: var(--glass-filter); backdrop-filter: var(--glass-filter); border-top: 1px solid var(--line); }
  .st-wnav { flex-direction: column-reverse; flex-wrap: nowrap; gap: .5rem; margin-bottom: calc(var(--sp-4) * -1); }
  .st-wnav .lb-btn { width: 100%; }
  .st-order-cta { gap: .55rem; }
  .st-order-cta .st-total { padding: .45rem .75rem; }
  .st-order { gap: var(--sp-3); }
  .st-order-side { grid-template-columns: 5rem minmax(0, 1fr); align-items: center; gap: var(--sp-3); }
  .st-order-side .st-comp { width: 5rem; max-width: none; }
  .st-order-side .st-live-title { text-align: start; }
  .st-pages { width: min(100%, 19rem); }
  .st-bd-vis { padding-top: 1.6rem; }
  .st-bd-text { padding-bottom: calc(var(--sp-4) + env(safe-area-inset-bottom)); }
}
@media (max-height: 520px) and (orientation: landscape) {
  .st-bar .lb-toc, .st-bar .st-mock { display: none; }
  .st .st-bar .lb-topbar-in { flex-wrap: nowrap; padding-block: .35rem; }
  .st-dlg-card { max-height: calc(100dvh - .5rem); }
}
@media (max-width: 350px) {
  .st .st-bar .lb-topbar-in { gap: .4rem; padding-inline: .75rem; }
  .st-bar-cta .st-cta-short { display: none !important; }
  .st-bar-cta .st-cta-tiny { display: inline; }
  .st .st-bar .lb-btn { padding-inline: .7rem; }
}
@media (max-width: 400px) {
  .st-bar-cta .st-cta-long { display: none; }
  .st-bar-cta .st-cta-short { display: inline; }
  .st-hero h1 { font-size: 2.05rem; }
}
"""

CSS += DEMO_CSS + MOBILE_CSS
JS = JS.replace("/*DEMO*/", DEMO_JS)


if __name__ == "__main__":
    build()
