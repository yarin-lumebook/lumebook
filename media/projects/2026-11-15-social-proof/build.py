"""Social proof page: every good review and comment we found (screenshots, tagged by theme) and every real
photo or video of a child with their LumeBook book (copies in Drive).

Data: data.json next to this file (reviews[], kids[], drive{}). Screenshots in reviews/, kid thumbnails in kids/thumbs/.
Rebuild: python3 media/projects/2026-11-15-social-proof/build.py
"""
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

CAT_SET = "proof-themes"
PLATFORMS = {
    "google": "Google",
    "facebook": "Facebook",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "youtube": "YouTube",
    "whatsapp": "וואטסאפ",
}
KINDS = {"review": "ביקורת", "recommendation": "המלצה", "comment": "תגובה", "caption": "פוסט שתייגו אותנו", "message": "הודעה"}
# How close the person is to buying, from what the comment says (my read of the text, not their word). Rank 0 sorts first.
INTENTS = {
    "want": ("רוצים לקנות", "accent", 0, "מבקשים קישור, אומרים שיזמינו או שהם בדיוק צריכים את זה"),
    "bought": ("קנו או הזמינו", "success", 1, "כבר הזמינו, כולל הזמנה חוזרת"),
    "share": ("מעבירים הלאה או ממליצים", "info", 2, "מתייגים, שולחים לאחות או ממליצים לאחרים"),
    "praise": ("מחמאה בלבד", "outline", 3, "בלי סימן לקנייה"),
}
# UGC creators (Instagram handles or the Drive folder names). Shoham: the Drive folder "Shoam" and @shoham_novik are treated as one
# person by name match, my assumption. natasha_fridman_ and Natali Fridman are NOT merged (different first names).
CREATORS = {
    "shoham": "Shoham Novik (שהם)", "hadarv": "hadarv", "sapir": "sapir_ivan_mugatz", "sharon": "sharonsolomon11",
    "coralhauon": "coralhauon", "shani": "shani_tubiz_traveling", "ellinore": "ellinore.speech", "natasha": "natasha_fridman_",
    "meriorehov": "meriorehov", "nofit": "Nofit", "natali": "Natali Fridman", "morkeisar": "Mor Keisar", "koral": "Koral", "moran": "Moran Arges",
}
MOMENT_SET = "kid-moments"


def moment(name):
    """What happens in a kid photo or video, read from its file name (my read, not checked frame by frame)."""
    import re
    n = name.lower()
    if "creator-reel" in n or "edited" in n:
        return "reel"
    if re.search(r"unwrapping|delivery-box|unboxing", n):
        return "unbox"
    if re.search(r"hugging|to-chest", n):
        return "hug"
    if re.search(r"holding|showing|grinning|smiling|laughs|excited|flower-crown|boy-red-shirt-balcony|by-window", n):
        return "show"
    if re.search(r"mom-|-mom|sibling|garden-chairs|two-girls|reading-to|aunt", n) and re.search(r"read|sofa|chairs|siblings|two-girls", n):
        return "together"
    return "browse"


KID_SOURCES = {
    "customer": "לקוחות",
    "creator": "יוצרות תוכן",
    "unknown": "חומרי גלם, מקור לא רשום",
}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def sort_date(w, captured="2026-11-15"):
    """ISO date for sorting. Google shows only 'לפני 3 שבועות' (read on the capture day), so those are approximate."""
    import datetime
    import re
    w = (w or "").strip()
    if re.match(r"\d{4}-\d{2}-\d{2}", w):
        return w[:10]
    m = re.search(r"(\d+)\s*(שבועות|חודשים)", w)
    days = 0
    if m:
        days = int(m.group(1)) * (7 if m.group(2) == "שבועות" else 30)
    elif "חודשיים" in w:
        days = 60
    elif "שבוע" in w:
        days = 7
    elif "חודש" in w:
        days = 30
    elif "שנה" in w:
        days = 365
    return (datetime.date.fromisoformat(captured) - datetime.timedelta(days=days)).isoformat()


def theme(key):
    return design.categories(CAT_SET)[key]


def theme_chip(key):
    it = theme(key)
    return f'<span class="lb-chip cat lb-cat-{it["cat"]}">{esc(it["label"])}</span>'


def stars(n):
    if not n:
        return ""
    return f'<span class="pr-stars" aria-label="{n} כוכבים">{"★" * n}<span class="pr-stars-off">{"★" * (5 - n)}</span></span>'


def drive_btn(fid, label="בדרייב"):
    if not fid:
        return ""
    return (f'<a class="lb-btn secondary sm" href="https://drive.google.com/file/d/{esc(fid)}/view" target="_blank" rel="noopener">'
            f'{design.icon("open-out")}<span>{label}</span></a>')


HE_MONTHS = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]
NO_CREATOR = "בלי יוצרת (הפוסטים שלנו, ביקורות ולקוחות)"
PAGE_FILE = "media/projects/2026-11-15-social-proof/social-proof.html"


def month_label(iso):
    return f"{HE_MONTHS[int(iso[5:7]) - 1]} {iso[:4]}"


def attrs(**kw):
    return " ".join(f'data-{k.replace("_", "-")}="{esc(v)}"' for k, v in kw.items())


RM_BTN = (f'<button type="button" class="pr-rm" data-rm aria-label="הסרת הכרטיס" title="הסרה: לא אשתמש בו בעתיד">{design.icon("close")}</button>'
          f'<button type="button" class="pr-restore lb-btn sm" data-restore>{design.icon("undo")}<span>שחזור</span></button>')


def review_card(r, tkeys, crank, i):
    plat = PLATFORMS.get(r["platform"], r["platform"])
    kind = KINDS.get(r.get("kind"), "")
    ik = r.get("intent", "praise")
    ilabel, icls, irank, _ = INTENTS[ik]
    cname = CREATORS.get(r.get("creator"), "")
    iso = sort_date(r.get("when"))
    st = r.get("stars") or 0
    primary = r["themes"][0]
    themes = "".join(theme_chip(t) for t in r["themes"])
    sub = " · ".join(x for x in [plat, kind, cname] if x)
    q = " ".join([r.get("author", ""), r.get("text", ""), r.get("note", "") or "", cname, plat, ilabel] +
                 [theme(t)["label"] for t in r["themes"]]).lower()
    a = attrs(key="review:" + r["id"], q=q, platform=r["platform"], intent=ik, themes=" ".join(r["themes"]), creator=r.get("creator") or "", i=i,
              k_intent=irank, g_intent=ilabel,
              k_date=iso, g_date=month_label(iso),
              k_platform=list(PLATFORMS).index(r["platform"]), g_platform=plat,
              k_creator=crank.get(r.get("creator"), 999), g_creator=cname or NO_CREATOR,
              k_theme=tkeys.index(primary), g_theme=theme(primary)["label"],
              k_stars=st, g_stars=(f"{st} כוכבים" if st else "בלי דירוג בכוכבים"),
              k_author=(r.get("author") or "").lower(), g_author="")
    return f"""
    <article class="lb-card pr-item pr-card" {a}>
      {RM_BTN}
      <header class="pr-card-head"><span class="lb-chip {icls}">{esc(ilabel)}</span>{stars(st) if st else ''}<span class="pr-when">{esc(r.get('when') or '')}</span></header>
      <button type="button" class="pr-shot" data-open="{i}" aria-label="פתיחת הצילום של {esc(r.get('author'))}"><img src="{esc(r['file'])}" alt="" loading="lazy"></button>
      <div class="pr-chips">{themes}</div>
      <footer class="pr-card-foot"><span class="pr-who"><b translate="no">{esc(r.get('author'))}</b><small translate="no">{esc(sub)}</small></span></footer>
    </article>"""


def review_detail(r, i):
    """The full record, kept in a template and moved into the dialog when a card opens."""
    plat = PLATFORMS.get(r["platform"], r["platform"])
    ik = r.get("intent", "praise")
    ilabel, icls, _, idesc = INTENTS[ik]
    cname = CREATORS.get(r.get("creator"), "")
    src = f'<a class="lb-btn secondary sm" href="{esc(r["url"])}" target="_blank" rel="noopener">{design.icon("open-out")}<span>לפוסט המקורי</span></a>' if r.get("url") else ""
    drv = drive_btn(r.get("drive"), "הקובץ בדרייב")
    full = f'<a class="lb-btn ghost sm" href="{esc(r["file"])}" target="_blank" rel="noopener">{design.icon("open-out")}<span>הצילום בגודל מלא</span></a>'
    rows = [("פלטפורמה", plat), ("סוג", KINDS.get(r.get("kind"), "")), ("מתי", r.get("when") or ""), ("יוצרת UGC", cname)]
    kv = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows if v)
    text = f'<p class="lb-textblock" dir="rtl" lang="he" translate="no">{esc(r["text"])}</p>' if r.get("text") else ""
    note = f'<p class="pr-note">{esc(r["note"])}</p>' if r.get("note") else ""
    return f"""<template id="pr-d-{i}"><div class="pr-detail">
      <div class="pr-detail-shot"><img src="{esc(r['file'])}" alt=""></div>
      <div class="pr-detail-info">
        <div class="pr-chips"><span class="lb-chip {icls}" title="{esc(idesc)}">{esc(ilabel)}</span>{stars(r.get('stars'))}{''.join(theme_chip(t) for t in r['themes'])}</div>
        <dl class="pr-kv">{kv}</dl>{text}{note}
        <div class="lb-row">{src}{drv}{full}</div>
      </div></div></template>"""


def kid_card(k, mkeys, crank):
    is_video = k["type"] == "video"
    play = f'<span class="lb-media-play">{design.icon("play")}</span>' if is_video else ""
    fid = k.get("drive") or k.get("drive_src")
    # Drive draws the thumbnail; it shows in a browser signed in to a Google account that can open the folder
    tsrc = k.get("thumb") or (f"https://drive.google.com/thumbnail?id={fid}&sz=w480" if fid else "")
    thumb = f'<img src="{esc(tsrc)}" alt="" loading="lazy" referrerpolicy="no-referrer">' if tsrc else ""
    link = f"https://drive.google.com/file/d/{esc(fid)}/view" if fid else esc(k.get("local", "#"))
    src = KID_SOURCES.get(k.get("source"), k.get("source") or "")
    mk = moment(k["name"])
    mit = design.categories(MOMENT_SET)[mk]
    cname = CREATORS.get(k.get("creator"), "")
    typ = "סרטון" if is_video else "תמונה"
    sub = " · ".join(x for x in [typ, cname or src] if x)
    q = " ".join([k["desc"], k["name"], cname, k.get("folder", ""), mit["label"], src, typ]).lower()
    a = attrs(key="kid:" + k["name"], q=q, type=k["type"], source=k.get("source") or "", moment=mk, creator=k.get("creator") or "",
              k_moment=mkeys.index(mk), g_moment=mit["label"],
              k_creator=crank.get(k.get("creator"), 999), g_creator=cname or NO_CREATOR,
              k_type=("0" if is_video else "1"), g_type=("סרטונים" if is_video else "תמונות"),
              k_source=list(KID_SOURCES).index(k.get("source") or "unknown"), g_source=src,
              k_name=k["name"].lower(), g_name="")
    title = esc(k["desc"] + (". " + k["note"] if k.get("note") else ""))
    return f"""
    <a class="lb-card pr-item pr-kid" href="{link}" target="_blank" rel="noopener" title="{title}" {a}>
      {RM_BTN}
      <div class="lb-media-frame is-4x5">{thumb}{play}</div>
      <span class="pr-kid-title">{esc(k['desc'])}</span>
      <div class="pr-chips"><span class="lb-chip cat lb-cat-{mit['cat']}">{esc(mit['label'])}</span></div>
      <span class="pr-kid-sub" translate="no">{esc(sub)}</span>
    </a>"""


def fnav(view, label, key, options, total):
    """One filter list in the page sidebar: options = [(value, label, count, hue or None, tooltip)]."""
    def item(v, lb, n, hue, tip, active=False):
        sw = f'<i class="pr-sw lb-cat-{hue}"></i>' if hue is not None else '<i class="pr-sw is-none"></i>'
        t = f' title="{esc(tip)}"' if tip else ""
        return (f'<button type="button" class="lb-nav-item{" is-active" if active else ""}" data-v="{esc(v)}" aria-pressed="{"true" if active else "false"}"{t}>'
                f'{sw}<span class="pr-nav-t">{esc(lb)}</span><span class="lb-count">{n}</span></button>')
    rows = item("", "הכול", total, None, "", True) + "".join(item(*o) for o in options)
    return f'<div class="pr-fnav" data-view="{view}" data-fkey="{key}"><div class="lb-nav-label">{esc(label)}</div><div class="lb-nav">{rows}</div></div>'


def sort_select(view, sorts, default):
    opts = "".join(f'<option value="{k}"{" selected" if k == default else ""}>{esc(lb)}</option>' for k, lb in sorts)
    return f'<label class="pr-sortf" data-view="{view}"><span>מיון</span><select class="lb-select" data-sort="{view}">{opts}</select></label>'


def metric(view, key, value, label, n, hue_cls, sub=""):
    foot = f'<p class="lb-metric-foot">{esc(sub)}</p>' if sub else ""
    return (f'<button type="button" class="lb-metric {hue_cls} pr-metric" data-view="{view}" data-fkey="{key}" data-v="{esc(value)}" aria-pressed="false">'
            f'<span class="lb-metric-label">{esc(label)}</span><span class="lb-metric-value">{n}</span>{foot}</button>')


CSS = r"""
  .pr-brand b { display: block; }
  .pr-views { display: grid; gap: 2px; }
  .pr-fnav[hidden] { display: none; }
  .pr-fnav .lb-nav-item { padding-block: .4rem; font-size: var(--fs-footnote); }
  .pr-fnav .lb-nav-item[aria-pressed="true"] { background: var(--raised); color: var(--tint); box-shadow: var(--shadow-1); }
  .pr-nav-t { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .pr-sw { flex: none; width: .55rem; height: .55rem; border-radius: 2px; background: var(--tc, var(--text-3)); }
  .pr-sw.is-none { background: var(--fill-2); }
  .pr-top { gap: var(--sp-3); }
  .pr-viewbar .lb-search { flex: 1 1 14rem; max-width: 28rem; }
  /* the "/" shortcut hint sits inside the field, at its far end */
  .pr-viewbar .lb-search .lb-kbd { position: absolute; inset-inline-end: .55rem; inset-block-start: 50%; transform: translateY(-50%); pointer-events: none; }
  .pr-viewbar .lb-search .lb-input { padding-inline-end: 2.6rem; }
  .pr-sortf { display: flex; align-items: center; gap: var(--sp-2); font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; color: var(--text-3); }
  .pr-sortf[hidden] { display: none; }
  .pr-sortf .lb-select { min-width: 10.5rem; }
  .pr-count {font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; color: var(--text-2); white-space: nowrap; }
  .pr-hero { gap: var(--sp-2); padding-bottom: 0; }
  .pr-hero .lb-row { margin-top: var(--sp-1); }
  .pr-view[hidden] { display: none; }
  .pr-view { display: grid; gap: var(--sp-5); }
  .pr-metrics { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .pr-metric { font: inherit; text-align: start; cursor: pointer; border: 0; }
  .pr-metric[aria-pressed="true"] { box-shadow: inset 0 0 0 2px var(--tc), var(--glass-card-lift, var(--shadow-1)); }
  .pr-note-line { margin: 0; font-family: var(--font-2); font-size: var(--fs-footnote); color: var(--text-3); text-align: center; }

  /* one grid, every card the same size */
  /* the cards-per-row switch sets --cols; fewer columns means bigger cards (the screenshot well grows with them) */
  .pr-grid { --cols: 4; --shot: 12.5rem; display: grid; gap: var(--sp-4); grid-template-columns: repeat(var(--cols), minmax(0, 1fr)); align-items: start; }
  .pr-grid[data-cols="1"] { --cols: 1; --shot: 34rem; }
  .pr-grid[data-cols="2"] { --cols: 2; --shot: 23rem; }
  .pr-grid[data-cols="3"] { --cols: 3; --shot: 16.5rem; }
  .pr-grid[data-cols="4"] { --cols: 4; --shot: 12.5rem; }
  .pr-grid[data-cols="5"] { --cols: 5; --shot: 10rem; }
  .pr-viewbar { display: flex; align-items: center; flex-wrap: wrap; gap: var(--sp-3); }
  .pr-colsf { display: flex; align-items: center; gap: var(--sp-2); font-family: var(--font-2); font-size: var(--fs-footnote); font-weight: 700; color: var(--text-3); }
  .pr-showrm { margin-inline-start: auto; }
  .pr-showrm[hidden] { display: none; }
  .pr-cols { flex: none; }
  .pr-item { position: relative; }
  .pr-rm { position: absolute; z-index: 2; inset-block-start: var(--sp-2); inset-inline-end: var(--sp-2); width: 1.9rem; height: 1.9rem; display: grid; place-items: center; padding: 0; border: 0; border-radius: var(--r-pill);
    background: var(--glass-sheen), var(--glass); box-shadow: var(--glass-edge); color: var(--text-2); cursor: pointer; opacity: 0; transition: opacity var(--dur-1, .15s) var(--ease, ease); }
  .pr-rm svg { width: 1rem; height: 1rem; }
  .pr-item:hover .pr-rm, .pr-rm:focus-visible { opacity: 1; }
  .pr-rm:hover { color: var(--danger, #C0392B); }
  @media (hover: none) { .pr-rm { opacity: 1; } }
  .pr-restore { display: none; position: absolute; z-index: 2; inset-block-start: 50%; inset-inline-start: 50%; transform: translate(-50%, -50%); }
  [dir="rtl"] .pr-restore { transform: translate(50%, -50%); }
  .pr-item.is-removed { opacity: .5; filter: grayscale(1); }
  .pr-item.is-removed .pr-restore { display: inline-flex; filter: none; }
  .pr-item.is-removed .pr-rm { display: none; }
  .pr-cols button { min-width: 2rem; padding-inline: .6rem; font-family: var(--font-2); font-weight: 700; }
  .pr-item[hidden], .pr-group[hidden] { display: none; }
  .pr-group { grid-column: 1 / -1; grid-row: auto; display: flex; align-items: center; gap: var(--sp-2); padding: var(--sp-3) var(--sp-1) 0; font-family: var(--font-2); font-size: var(--fs-callout); font-weight: 800; color: var(--text); }
  .pr-group::after { content: ""; flex: 1; height: 1px; background: var(--line); }
  .pr-grid > .pr-group { align-self: end; }
  .pr-card, .pr-kid { display: grid; gap: var(--sp-3); padding: var(--sp-3); min-width: 0; height: 100%; box-sizing: border-box; color: inherit; text-decoration: none; }
  .pr-card { grid-template-rows: 1.6rem var(--shot) 1.6rem auto; }
  .pr-kid { grid-template-rows: auto 2.6em 1.6rem 1.2em; align-content: start; }
  a.pr-kid:hover { text-decoration: none; color: inherit; }
  .pr-card:hover, .pr-kid:hover { transform: translateY(-2px); }
  .pr-card, .pr-kid { transition: transform var(--dur-1, .15s) var(--ease, ease); }
  .pr-card-head { display: flex; align-items: center; gap: var(--sp-1); min-width: 0; overflow: hidden; white-space: nowrap; }
  .pr-chips { display: flex; align-items: center; gap: var(--sp-1); min-width: 0; overflow: hidden; white-space: nowrap;
    -webkit-mask-image: linear-gradient(to left, #000 85%, transparent); mask-image: linear-gradient(to left, #000 85%, transparent); }
  [dir="ltr"] .pr-chips { -webkit-mask-image: linear-gradient(to right, #000 85%, transparent); mask-image: linear-gradient(to right, #000 85%, transparent); }
  .pr-chips .lb-chip, .pr-card-head .lb-chip { flex: none; }
  .pr-when { flex: none; margin-inline-start: auto; font-family: var(--font-2); font-size: var(--fs-caption); color: var(--text-3); }
  .pr-stars { flex: none; color: var(--lb-gold, #C9954A); letter-spacing: .04em; font-size: var(--fs-caption); }
  .pr-stars-off { color: var(--line-strong); }
  /* the screenshot sits in a pressed-in well, scaled to fit, never cropped */
  .pr-shot { position: relative; display: block; width: 100%; height: 100%; padding: 0; border: 0; border-radius: var(--r-md); background: var(--surface-sunk);
    box-shadow: inset 0 1px 3px rgba(var(--shade), .08); cursor: zoom-in; overflow: hidden; }
  .pr-shot img { position: absolute; inset: var(--sp-2); width: calc(100% - 2 * var(--sp-2)); height: calc(100% - 2 * var(--sp-2)); object-fit: contain; object-position: center; }
  .pr-shot:hover img { transform: scale(1.02); }
  .pr-shot img { transition: transform var(--dur-1, .15s) var(--ease, ease); }
  .pr-shot:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .pr-card-foot { display: flex; align-items: center; min-width: 0; }
  .pr-who { display: grid; min-width: 0; line-height: 1.3; }
  .pr-who b, .pr-who small { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .pr-who b { font-size: var(--fs-footnote); font-weight: 700; }
  .pr-who small { font-family: var(--font-2); font-size: var(--fs-caption); color: var(--text-3); }
  .pr-kid .lb-media-frame { border-radius: var(--r-md); }
  .pr-kid-title { font-weight: 600; font-size: var(--fs-footnote); line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .pr-kid-sub { font-family: var(--font-2); font-size: var(--fs-caption); color: var(--text-3); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .pr-empty { grid-column: 1 / -1; }

  /* the dialog that shows one review at full size */
  .pr-detail { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: var(--sp-4); padding: var(--sp-4); }
  .pr-detail-shot { display: grid; place-items: start center; padding: var(--sp-3); border-radius: var(--r-md); background: var(--surface-sunk); max-height: 70vh; overflow: auto; }
  .pr-detail-shot img { max-width: 100%; height: auto; border-radius: var(--r-xs); box-shadow: var(--shadow-1); background: #fff; }
  .pr-detail-info { display: grid; gap: var(--sp-3); align-content: start; min-width: 0; }
  .pr-detail-info .pr-chips { flex-wrap: wrap; white-space: normal; -webkit-mask-image: none; mask-image: none; }
  .pr-kv { display: grid; grid-template-columns: auto 1fr; gap: var(--sp-1) var(--sp-3); margin: 0; font-size: var(--fs-footnote); }
  .pr-kv dt { font-family: var(--font-2); font-weight: 700; color: var(--text-3); }
  .pr-kv dd { margin: 0; }
  .pr-note { margin: 0; font-size: var(--fs-footnote); color: var(--text-2); }
  .pr-dtitle { flex: 1; min-width: 0; padding-inline: var(--sp-4); font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .pr-gaps { margin: var(--sp-2) 0 0; padding-inline-start: 1.2rem; display: grid; gap: var(--sp-1); color: var(--text-2); }

  @media (max-width: 1100px) { .pr-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 760px) {
    .pr-detail { grid-template-columns: minmax(0, 1fr); }
    .pr-viewbar { row-gap: var(--sp-2); }
    .pr-viewbar .lb-kbd, .pr-sortf > span { display: none; }
    .pr-viewbar .lb-search { flex: 1 1 100%; max-width: none; }
    .pr-sortf { flex: 1 1 auto; }
    .pr-sortf .lb-select { min-width: 0; width: 100%; }
    .pr-count { margin-inline-start: 0; }
    .pr-cols { display: none; }
    .pr-grid, .pr-grid[data-cols] { --cols: 1; --shot: 22rem; }
    .pr-grid.is-kids, .pr-grid.is-kids[data-cols] { --cols: 2; }
  }
  @media (prefers-reduced-motion: reduce) { .pr-card, .pr-kid { transition: none; } .pr-card:hover, .pr-kid:hover { transform: none; } }
"""

JS = r"""<script>
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const side = $('.lb-sidebar'), scrim = $('.lb-scrim');
  const closeNav = () => { side.classList.remove('is-open'); scrim.hidden = true; };
  $('#pr-menu').addEventListener('click', () => { side.classList.add('is-open'); scrim.hidden = false; });
  scrim.addEventListener('click', closeNav);

  // sort direction per key: dates and stars run high to low, the rest low to high
  const DIR = { date: -1, stars: -1 };
  const cap = s => s[0].toUpperCase() + s.slice(1);
  const num = v => v !== '' && !isNaN(v);
  const cmp = (a, b) => num(a) && num(b) ? a - b : String(a).localeCompare(String(b), 'he');
  const search = $('#pr-q'), count = $('#pr-count');
  const V = {};
  let cur = 'reviews';
  const RM = { show: false, keys: new Set(Object.keys(__REMOVED__)) };

  $$('.pr-view').forEach(root => {
    const view = root.dataset.view, grid = $('[data-grid]', root), items = $$('.pr-item', grid);
    const sel = $(`[data-sort="${view}"]`);
    const st = { q: '', f: {} }, heads = new Map();
    const empty = Object.assign(document.createElement('p'), { className: 'lb-empty pr-empty', textContent: 'אין תוצאות. אפשר לנקות את החיפוש או את אחד הסינונים.' });
    empty.hidden = true; grid.append(empty);
    items.forEach((c, i) => c._i = i);
    const match = c => {
      if (c.classList.contains('is-removed') && !RM.show) return false;
      if (st.q && !st.q.split(/\s+/).every(w => c.dataset.q.includes(w))) return false;
      return Object.entries(st.f).every(([k, v]) => !v || (k === 'themes' ? c.dataset.themes.split(' ').includes(v)
        : v === '_none' ? c.dataset[k] === '' : c.dataset[k] === v));
    };
    const render = () => {
      const mode = sel.value, K = 'k' + cap(mode), G = 'g' + cap(mode), dir = DIR[mode] || 1;
      const sorted = [...items].sort((a, b) => dir * cmp(a.dataset[K], b.dataset[K]) || a._i - b._i);
      const tot = {}; let shown = 0;
      sorted.forEach(c => { c.hidden = !match(c); if (!c.hidden) { shown++; tot[c.dataset[G]] = (tot[c.dataset[G]] || 0) + 1; } });
      let o = 0, last = null; const used = new Set();
      sorted.forEach(c => {
        if (c.hidden) return;
        const g = c.dataset[G];
        if (g && g !== last) {
          let h = heads.get(g);
          if (!h) { h = document.createElement('div'); h.className = 'pr-group'; heads.set(g, h); grid.append(h); }
          h.replaceChildren(Object.assign(document.createElement('span'), { textContent: g }), Object.assign(document.createElement('span'), { className: 'lb-count', textContent: tot[g] }));
          h.hidden = false; h.style.order = o++; used.add(g); last = g;
        }
        c.style.order = o++;
      });
      heads.forEach((h, g) => { if (!used.has(g)) h.hidden = true; });
      empty.hidden = shown > 0; empty.style.order = o;
      if (view === cur) count.textContent = 'מוצגים ' + shown + ' מתוך ' + items.filter(c => !c.classList.contains('is-removed')).length;
    };
    const setFilter = (key, v) => {
      st.f[key] = v;
      $$(`.pr-fnav[data-view="${view}"][data-fkey="${key}"] .lb-nav-item`).forEach(b => b.setAttribute('aria-pressed', b.dataset.v === v));
      $$(`.pr-metric[data-view="${view}"]`).forEach(m => m.setAttribute('aria-pressed', !!v && m.dataset.fkey === key && m.dataset.v === v));
      render();
    };
    $$(`.pr-fnav[data-view="${view}"]`).forEach(g => g.addEventListener('click', e => {
      const b = e.target.closest('.lb-nav-item'); if (!b) return; setFilter(g.dataset.fkey, b.dataset.v); if (innerWidth < 860) closeNav();
    }));
    $$(`.pr-metric[data-view="${view}"]`).forEach(m => m.addEventListener('click', () =>
      setFilter(m.dataset.fkey, st.f[m.dataset.fkey] === m.dataset.v ? '' : m.dataset.v)));
    sel.addEventListener('change', render);
    V[view] = { st, render, reset: () => { Object.keys(st.f).forEach(k => setFilter(k, '')); st.q = ''; render(); } };
    render();
  });

  // views: the sidebar's two pages; each has its own search text, sort and filters
  const views = $$('.pr-view'), links = $$('.pr-views .lb-nav-item');
  const show = v => {
    if (!V[v]) v = 'reviews';
    cur = v;
    views.forEach(s => s.hidden = s.dataset.view !== v);
    $$('[data-view]').forEach(el => { if (!el.classList.contains('pr-view') && !el.classList.contains('pr-metric')) el.hidden = el.dataset.view !== v; });
    links.forEach(a => a.getAttribute('href') === '#' + v ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current'));
    search.value = V[v].st.q; V[v].render();
  };
  links.forEach(a => a.addEventListener('click', e => { e.preventDefault(); history.replaceState(null, '', a.getAttribute('href')); show(a.getAttribute('href').slice(1)); closeNav(); window.scrollTo(0, 0); }));
  // removing a card: it is recorded on the project server (removed.json) so nobody picks it for a reel, carousel or post
  const rmBtn = $('#pr-showrm'), rmN = $('#pr-rmn');
  const applyRemoved = () => {
    $$('.pr-item').forEach(c => c.classList.toggle('is-removed', RM.keys.has(c.dataset.key)));
    rmN.textContent = RM.keys.size; rmBtn.hidden = RM.keys.size === 0;
    if (!RM.keys.size) RM.show = false;
    rmBtn.setAttribute('aria-pressed', String(RM.show));
    Object.values(V).forEach(v => v.render());
  };
  const save = (key, removed, label) => fetch('/api/social-proof/removed', { method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-LumeBook-Board': '1' }, body: JSON.stringify({ key, removed, label }) })
    .then(r => r.ok ? r.json() : Promise.reject(r.status));
  const toast = (msg, undo) => {
    $$('.lb-toast.pr-toast').forEach(t => t.remove());
    const t = document.createElement('div'); t.className = 'lb-toast pr-toast'; t.setAttribute('role', 'status');
    t.append(document.createTextNode(msg + ' '));
    if (undo) { const b = Object.assign(document.createElement('button'), { type: 'button', textContent: 'ביטול' }); b.style.cssText = 'all:unset;cursor:pointer;font-weight:700;text-decoration:underline'; b.onclick = () => { undo(); t.remove(); }; t.append(b); }
    document.body.append(t); setTimeout(() => t.remove(), 6000);
  };
  const setRemoved = (card, removed) => {
    const key = card.dataset.key, label = ($('.pr-who b', card) || $('.pr-kid-title', card) || {}).textContent || '';
    const before = new Set(RM.keys);
    removed ? RM.keys.add(key) : RM.keys.delete(key); applyRemoved();
    save(key, removed, label.trim()).then(() => {
      if (removed) toast('הכרטיס הוסר ולא ישמש בעתיד.', () => setRemoved(card, false));
    }).catch(() => { RM.keys = before; applyRemoved(); toast('לא נשמר. ההסרה עובדת רק בשרת הפרויקט (localhost:8780).'); });
  };
  document.addEventListener('click', e => {
    const x = e.target.closest('[data-rm],[data-restore]'); if (!x) return;
    e.preventDefault(); e.stopPropagation();
    setRemoved(x.closest('.pr-item'), x.hasAttribute('data-rm'));
  }, true);
  rmBtn.addEventListener('click', () => { RM.show = !RM.show; applyRemoved(); });
  fetch('/api/social-proof/removed').then(r => r.ok ? r.json() : null).then(d => { if (d && d.removed) { RM.keys = new Set(Object.keys(d.removed)); applyRemoved(); } }).catch(() => {});
  applyRemoved();

  // cards per row, 1 to 5: fewer means bigger cards; kept in this browser
  const colBtns = $$('#pr-cols button');
  const setCols = n => {
    $$('[data-grid]').forEach(g => g.dataset.cols = n);
    colBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.n === String(n))));
    try { localStorage.setItem('pr-cols', n); } catch (e) {}
  };
  colBtns.forEach(b => b.addEventListener('click', () => setCols(b.dataset.n)));
  let c0 = '4'; try { c0 = localStorage.getItem('pr-cols') || '4'; } catch (e) {}
  setCols(/^[1-5]$/.test(c0) ? c0 : '4');
  search.addEventListener('input', () => { V[cur].st.q = search.value.trim().toLowerCase(); V[cur].render(); });
  $('#pr-reset').addEventListener('click', () => { search.value = ''; V[cur].reset(); });
  document.addEventListener('keydown', e => { if (e.key === '/' && document.activeElement === document.body) { e.preventDefault(); search.focus(); } });
  show(location.hash.slice(1) || 'reviews');

  // one review at full size in the design-system dialog
  const dlg = $('#pr-dialog'), body = $('#pr-dialog-body'), dtitle = $('#pr-dialog-title');
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-open]'); if (!b) return;
    const card = b.closest('.pr-card'), t = $('#pr-d-' + b.dataset.open);
    body.replaceChildren(t.content.cloneNode(true));
    dtitle.textContent = $('.pr-who b', card).textContent;
    dlg.showModal();
  });
  $('#pr-dialog-x').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
})();
</script>"""


def build():
    # cards Yarin removed on the page (tools/social_proof.py): the page starts with them hidden, the server list refreshes it
    try:
        removed_json = json.dumps(json.loads((HERE / "removed.json").read_text(encoding="utf-8")).get("removed") or {}, ensure_ascii=False).replace("</", "<\\/")
    except (OSError, ValueError):
        removed_json = "{}"
    d = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
    reviews, kids, drive = d["reviews"], d.get("kids", []), d["drive"]
    tset, mset = design.categories(CAT_SET), design.categories(MOMENT_SET)
    tkeys, mkeys = list(tset), list(mset)

    def n_of(rows, fn, v):
        return sum(1 for r in rows if fn(r) == v)

    rcreators = sorted({r.get("creator") for r in reviews if r.get("creator")}, key=lambda c: -n_of(reviews, lambda r: r.get("creator"), c))
    kcreators = sorted({k.get("creator") for k in kids if k.get("creator")}, key=lambda c: -n_of(kids, lambda k: k.get("creator"), c))
    plats = [p for p in PLATFORMS if any(r["platform"] == p for r in reviews)]
    srcs = [s for s in KID_SOURCES if any((k.get("source") or "unknown") == s for k in kids)]
    ihue = {"want": 2, "bought": 3, "share": 4, "praise": None}

    side_filters = "".join([
        fnav("reviews", "כוונת קנייה", "intent", [(k, v[0], n_of(reviews, lambda r: r.get("intent", "praise"), k), ihue[k], v[3]) for k, v in INTENTS.items()], len(reviews)),
        fnav("reviews", "נושא", "themes", [(k, it["label"], sum(1 for r in reviews if k in r["themes"]), it["cat"], "") for k, it in tset.items()], len(reviews)),
        fnav("reviews", "פלטפורמה", "platform", [(p, PLATFORMS[p], n_of(reviews, lambda r: r["platform"], p), None, "") for p in plats], len(reviews)),
        fnav("reviews", "יוצרת UGC (הפוסט שלה)", "creator", [(c, CREATORS.get(c, c), n_of(reviews, lambda r: r.get("creator"), c), None, "") for c in rcreators] +
             [("_none", "בלי יוצרת", sum(1 for r in reviews if not r.get("creator")), None, "הפוסטים שלנו, ביקורות ולקוחות")], len(reviews)),
        fnav("kids", "מה קורה בצילום", "moment", [(m, it["label"], n_of(kids, lambda k: moment(k["name"]), m), it["cat"], "") for m, it in mset.items()], len(kids)),
        fnav("kids", "יוצרת UGC", "creator", [(c, CREATORS.get(c, c), n_of(kids, lambda k: k.get("creator"), c), None, "") for c in kcreators] +
             [("_none", "בלי יוצרת", sum(1 for k in kids if not k.get("creator")), None, "לקוחות וחומרי גלם")], len(kids)),
        fnav("kids", "סוג", "type", [("photo", "תמונות", n_of(kids, lambda k: k["type"], "photo"), None, ""), ("video", "סרטונים", n_of(kids, lambda k: k["type"], "video"), None, "")], len(kids)),
        fnav("kids", "מקור", "source", [(s, KID_SOURCES[s], n_of(kids, lambda k: k.get("source") or "unknown", s), None, "") for s in srcs], len(kids)),
    ])

    rmetrics = "".join(metric("reviews", "intent", k, v[0], n_of(reviews, lambda r: r.get("intent", "praise"), k),
                              {"want": "lb-cat-2", "bought": "is-ok", "share": "lb-cat-4", "praise": ""}[k], v[3]) for k, v in INTENTS.items())
    n_creator_kids = sum(1 for k in kids if k.get("creator"))
    kmetrics = (metric("kids", "type", "photo", "תמונות", n_of(kids, lambda k: k["type"], "photo"), "lb-cat-4", "של ילדים עם הספר שלהם")
                + metric("kids", "type", "video", "סרטונים", n_of(kids, lambda k: k["type"], "video"), "lb-cat-5", "גלם ורילס ערוכים")
                + metric("kids", "source", "creator", "מיוצרות תוכן", n_of(kids, lambda k: k.get("source"), "creator"), "lb-cat-2", f"{len(kcreators)} יוצרות")
                + metric("kids", "source", "customer", "מלקוחות", n_of(kids, lambda k: k.get("source"), "customer"), "is-ok", "שלחו לנו בוואטסאפ"))

    rsorts = [("intent", "כוונת קנייה"), ("date", "תאריך, מהחדש"), ("platform", "פלטפורמה"), ("creator", "יוצרת UGC"),
              ("theme", "נושא ראשי"), ("stars", "דירוג בכוכבים"), ("author", "שם, א עד ת")]
    ksorts = [("moment", "מה קורה בצילום"), ("creator", "יוצרת UGC"), ("type", "תמונות וסרטונים"), ("source", "מקור"), ("name", "שם הקובץ")]
    rc = {c: i for i, c in enumerate(rcreators)}
    kc = {c: i for i, c in enumerate(kcreators)}
    rcards = "".join(review_card(r, tkeys, rc, i) for i, r in enumerate(reviews))
    rtemplates = "".join(review_detail(r, i) for i, r in enumerate(reviews))
    kcards = "".join(kid_card(k, mkeys, kc) for k in kids)

    folder = lambda fid: f"https://drive.google.com/drive/folders/{fid}"
    gaps = "".join(f"<li>{esc(g)}</li>" for g in d.get("gaps", []))
    gaps_html = f'<details class="lb-disclosure"><summary>מה לא נמצא או לא נבדק</summary><ul class="pr-gaps">{gaps}</ul></details>' if gaps else ""
    ic = design.icon

    page = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>הוכחה חברתית · לומבוק</title>
{design.head(page=PAGE_FILE)}
<style>{CSS}</style>
</head>
<body>
<div class="lb-app">
  <aside class="lb-sidebar" aria-label="תצוגות וסינון">
    <a class="lb-brand pr-brand" href="#reviews"><span><b>הוכחה חברתית</b><small>נאסף ב־{esc(d['captured_label'])}</small></span></a>
    <nav class="lb-nav pr-views">
      <a class="lb-nav-item" href="#reviews">{ic("chat")}<span>ביקורות ותגובות</span><span class="lb-count">{len(reviews)}</span></a>
      <a class="lb-nav-item" href="#kids">{ic("people")}<span>ילדים עם הספר</span><span class="lb-count">{len(kids)}</span></a>
    </nav>
    {side_filters}
    <div class="lb-sidebar-foot"><span>הכול גם בדרייב, בתיקיות שבראש העמוד.</span></div>
  </aside>
  <div class="lb-scrim" hidden></div>
  <main class="lb-main">
    <div class="lb-page">
      <header class="lb-hero pr-hero">
        <h1>הוכחה חברתית</h1>
        <p class="lb-lede">כל הביקורות והתגובות הטובות שמצאנו בכל הפלטפורמות, וכל תמונה או סרטון אמיתי של ילד עם הספר שלו.</p>
        <div class="lb-row">
          <a class="lb-btn secondary sm" href="{folder(drive['reviews'])}" target="_blank" rel="noopener">{ic("folder")}<span>תגובות וביקורות בדרייב</span></a>
          <a class="lb-btn secondary sm" href="{folder(drive['intent_folder'])}" target="_blank" rel="noopener">{ic("folder")}<span>לפי כוונת קנייה</span></a>
          <a class="lb-btn secondary sm" href="{folder(drive['kids'])}" target="_blank" rel="noopener">{ic("folder")}<span>ילדים עם הספר בדרייב</span></a>
        </div>
      </header>

      <div class="pr-viewbar">
        <button class="lb-btn secondary icon lb-menu-btn" id="pr-menu" type="button" aria-label="פתיחת התצוגות והסינון">{ic("menu")}</button>
        <label class="lb-search">{ic("search")}<span class="lb-sr">חיפוש</span><input class="lb-input" id="pr-q" type="search" dir="rtl" placeholder="חיפוש בטקסט, בשם או ביוצרת" autocomplete="off"><span class="lb-kbd" aria-hidden="true">/</span></label>
        {sort_select("reviews", rsorts, "intent")}{sort_select("kids", ksorts, "moment")}
        <label class="pr-colsf"><span>כרטיסים בשורה</span><div class="lb-segmented pr-cols" id="pr-cols" role="group" aria-label="כרטיסים בשורה">{"".join(f'<button type="button" data-n="{i}" aria-pressed="false">{i}</button>' for i in range(1, 6))}</div></label>
        <button type="button" class="lb-btn ghost sm" id="pr-reset">ניקוי</button>
        <span class="pr-count" id="pr-count" aria-live="polite"></span>
        <button type="button" class="lb-btn secondary sm pr-showrm" id="pr-showrm" aria-pressed="false" hidden>{ic("eye")}<span>הצגת כרטיסים שהוסרו (<b id="pr-rmn">0</b>)</span></button>
      </div>

      <section class="pr-view" data-view="reviews" id="reviews">
        <div class="lb-metrics pr-metrics">{rmetrics}</div>
        <p class="pr-note-line">כוונת הקנייה היא הקריאה שלנו לפי מה שכתוב. ביקורות גוגל והודעות הלקוחות הן של אנשים שכבר קנו. לחיצה על צילום פותחת אותו בגודל מלא.</p>
        <div class="pr-grid" data-grid>{rcards}</div>
        {gaps_html}
      </section>

      <section class="pr-view" data-view="kids" id="kids" hidden>
        <div class="lb-metrics pr-metrics">{kmetrics}</div>
        <p class="pr-note-line">״מה קורה בצילום״ נקבע לפי שם הקובץ. Shoam בדרייב ו־shoham_novik נחשבות אותה יוצרת לפי השם, זו הנחה. לחיצה פותחת את הקובץ בדרייב.</p>
        <div class="pr-grid is-kids" data-grid>{kcards}</div>
      </section>
    </div>
  </main>
</div>
<dialog class="lb-dialog" id="pr-dialog" aria-labelledby="pr-dialog-title">
  <div class="lb-dialog-card">
    <div class="lb-dialog-head"><span class="pr-dtitle" id="pr-dialog-title" translate="no"></span><button type="button" class="lb-dialog-x" id="pr-dialog-x" aria-label="סגירה">✕</button></div>
    <div class="lb-dialog-body" id="pr-dialog-body"></div>
  </div>
</dialog>
{rtemplates}
{JS.replace("__REMOVED__", removed_json)}
</body>
</html>
"""
    out = HERE / "social-proof.html"
    out.write_text(page, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    build()
