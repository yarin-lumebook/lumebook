#!/usr/bin/env python3
"""Seasonal carousels and single-picture ads: Black Friday and Hanukkah 2026 (Yarin, 19 Nov 2026).

Yarin, 19 Nov 2026: "i need black friday and hannukah carousels, the black friday carousels end when black friday
finishes, the hannukah one when hannukah ends, schedule them to postiz on alternating days (i need the last black friday
carousel to land on the day itself), create one example for each to let me review, then well create the entire batch and
then we can use photos and generate images to use for them and then schedule".
After the first review, the same day: "make black friday graphics black and white / hanukkah to be warm and magical / i
want to pictures to be in the front in their own little boxes and themes pattern for the bg / also give me 14 writen ideas
for both / they dont have to be a carousel they can be one picture / push for 100% conversion friendly ad suggesting a
better option for both".

The copy follows the test batch (one mom or one grandmother, feminine singular, LumeBook may be named, a comment word for
the link, Facebook gets its own text) and is checked by test_batch.lint. The look is this file's own:

    bf        black and white: a dotted and striped pattern, slides alternate black and white, the photo in a white
              (or black) box, a BLACK FRIDAY / בלאק פריידיי tape across the cover, the CTA and the ad
    hanukkah  warm and magical: an ember to plum glow, gold sparkles and small flames as the pattern, the photo in a gold
              box with a glow (an arch on the cover)

A slide shows its picture (`bg`, or `pics` for 2 to 3 boxes, `covers` for book covers, `cover` on the CTA) in a box in
front of the pattern, the words above it (below it on a quote). A carousel with "format": "single" is a one-picture post
or ad: one `cta` slide with `headline`, `no` (the usual buy, crossed out), `yes` (the better option, over its photo) and
`body` (the reason to act and the CTA's last line).

    carousel/carousel-pipeline/seasonal/2026-bf-hanukkah/
        carousels/KEY.json     bf-YYYY-MM-DD / hn-YYYY-MM-DD (the day it goes out), bf-ad-N / hn-ad-N (single pictures)
        slides/KEY/            NN.png, contact-sheet.png, render-report.json, slides.html
        ideas.md               14 written ideas for each holiday
        README.md              the plan, the dates, what waits for Yarin

    python3 carousel/carousel-pipeline/scripts/seasonal_batch.py status
    python3 carousel/carousel-pipeline/scripts/seasonal_batch.py lint [KEY ...]
    python3 carousel/carousel-pipeline/scripts/seasonal_batch.py render [KEY ...]
Standard library only (Chrome draws the slides). Never calls a paid tool and never touches Postiz.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel_lib as lib  # noqa: E402
import test_batch as tb  # noqa: E402

HOME = lib.PIPELINE / "seasonal" / "2026-bf-hanukkah"
W, H = 1080, 1350
SINGLE_MAX_WORDS = 34   # a one-picture post carries the hook, both options, the reason and the CTA line

tb.HOME = HOME
tb.CARS = HOME / "carousels"
tb.SLIDES = HOME / "slides"
tb.RUNS = HOME / "runs"
tb.VERSIONS = HOME / "versions"
tb.KEY_RE = re.compile(r"^(bf|hn)-(\d{4}-\d{2}-\d{2}|ad-\d+)$")

tb.TYPES["bf"] = {
    "he": "בלאק פריידיי", "short_he": "בלאק פריידיי", "brand": True, "disclaimer": False,
    "about_he": "לסבתא או לאמא עם עגלה מלאה. הצעת בלאק פריידיי: 119 לספר הראשון ו 99 לשני (ירין, 19 / 11 / 2026, shared/facts.json black_friday_2026); המחיר על השקופיות רק אחרי אישור של ירין, עד אז בלי מספר.",
    "why_he": "בלאק פריידיי הוא מודעות למחיר הרגיל (ירין, 18 / 11 / 2026). האחרון בסדרה עולה ביום עצמו, 27 / 11.",
}
tb.TYPES["hanukkah"] = {
    "he": "חנוכה: המתנה בחינם", "short_he": "חנוכה", "brand": True, "disclaimer": False,
    "about_he": "המתנה האישית בחינם של חנוכה: כרטיס ברכה או חוברת צביעה עם הילד בפנים. כל קרוסלה מובילה לעמוד holiday-cards.",
    "why_he": "חנוכה הוא המתנה החינמית (ירין, 18 / 11 / 2026). האחרונה בסדרה עולה ביום האחרון של החג, 12 / 12.",
}
tb.THEMES["bf"] = {"accent": "#0B0B0B", "hi": "#FFFFFF"}
tb.THEMES["hanukkah"] = {"accent": "#C98A2B", "hi": "#FFD36E"}


# ---------------------------------------------------------------- the look

_SPARK = "M0-12 2.4-2.4 12 0 2.4 2.4 0 12-2.4 2.4-12 0-2.4-2.4Z"
_FLAME = "M0-14C5-7 7-2 7 3a7 7 0 0 1-14 0C-7-2-5-7 0-14Z"
HANUKKAH_TILE = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240' viewBox='0 0 240 240'><g fill='#FFD58A'>"
    f"<path opacity='.55' transform='translate(40 46) scale(1.1)' d='{_SPARK}'/>"
    f"<path opacity='.32' transform='translate(172 30) scale(.7)' d='{_SPARK}'/>"
    f"<path opacity='.45' transform='translate(198 152) scale(.9)' d='{_SPARK}'/>"
    f"<path opacity='.28' transform='translate(90 192) scale(.6)' d='{_SPARK}'/>"
    f"<path opacity='.38' transform='translate(120 150) scale(.9)' d='{_FLAME}'/>"
    f"<path opacity='.26' transform='translate(62 110) scale(.6)' d='{_FLAME}'/>"
    f"<path opacity='.22' transform='translate(214 222) scale(.55)' d='{_FLAME}'/>"
    "<circle cx='120' cy='96' r='2.2' opacity='.6'/><circle cx='18' cy='132' r='1.6' opacity='.5'/>"
    "<circle cx='224' cy='92' r='1.4' opacity='.45'/><circle cx='150' cy='216' r='1.8' opacity='.5'/>"
    "<circle cx='12' cy='14' r='1.3' opacity='.4'/></g></svg>")

X_ICON = tb.X_ICON
V_ICON = tb.V_ICON
ARROW = ('<div class="arrow"><svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="2.8" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M11 18l-6-6 6-6"/></svg></div>')
TAPE = ('<div class="tape"><div class="run">'
        + '<span>BLACK FRIDAY</span><i>✦</i><span dir="rtl">בלאק פריידיי</span><i>✦</i>' * 8 + '</div></div>')


def css(base):
    fonts = tb._src(lib.PIPELINE / "assets" / "fonts", base)
    tile = quote(HANUKKAH_TILE)
    return f"""
@font-face{{font-family:"Heebo LB";src:url("{fonts}/Heebo-Black.ttf") format("truetype");font-weight:900}}
@font-face{{font-family:"Heebo LB";src:url("{fonts}/Heebo-Bold.ttf") format("truetype");font-weight:700}}
@font-face{{font-family:"Assistant LB";src:url("{fonts}/Assistant-VariableFont_wght.ttf") format("truetype");font-weight:200 800}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:#111}}
body{{width:{W}px;direction:rtl;-webkit-font-smoothing:antialiased}}
body.one .slide{{display:none}} body.one .slide.on{{display:flex}}
.slide{{--k:1;width:{W}px;height:{H}px;position:relative;overflow:hidden;display:flex;flex-direction:column;align-items:center;
  padding:72px 74px 150px;text-align:center;color:var(--fg);font-family:"Assistant LB",sans-serif}}
.pat,.glow{{position:absolute;inset:0;pointer-events:none;z-index:0}}
.txt{{flex:none;position:relative;z-index:2;display:flex;flex-direction:column;align-items:center;max-width:100%}}
.num{{width:calc(var(--k)*94px);height:calc(var(--k)*94px);border-radius:50%;display:flex;align-items:center;justify-content:center;
  font:900 calc(var(--k)*56px)/1 "Heebo LB";background:var(--disc-bg);color:var(--disc-fg);margin-bottom:calc(var(--k)*16px)}}
.label{{font:800 calc(var(--k)*36px)/1.2 "Assistant LB";letter-spacing:.01em;opacity:.88;margin-bottom:calc(var(--k)*10px)}}
.h{{margin:0;font:900 calc(var(--k)*86px)/1.1 "Heebo LB"}}
.l-cover .h{{font-size:calc(var(--k)*106px);line-height:1.06}}
.b{{margin:calc(var(--k)*22px) 0 0;font:600 calc(var(--k)*40px)/1.34 "Assistant LB"}}
.l-cover .b{{display:inline-block;padding:.2em .8em .24em;border-radius:999px;background:var(--pill-bg);color:var(--pill-fg);font-weight:800}}
.q{{margin:0;font:900 calc(var(--k)*62px)/1.2 "Heebo LB"}}
.qmark{{font:900 calc(var(--k)*120px)/.6 "Heebo LB";color:var(--em-c);margin:calc(var(--k)*34px) 0 calc(var(--k)*6px)}}
.by{{margin-top:calc(var(--k)*20px);font:700 calc(var(--k)*34px) "Assistant LB";opacity:.9}}
.word{{display:inline-block;padding:0 .4em .06em;border-radius:.3em;background:var(--chip-bg);color:var(--chip-fg);font-weight:900;margin:0 .1em}}
.nw{{white-space:nowrap}}
em{{font-style:normal}}
.pics{{flex:1 1 0;min-height:0;width:100%;position:relative;z-index:1;display:flex;align-items:center;justify-content:center;gap:34px;margin-top:calc(var(--k)*40px)}}
.l-quote .pics{{margin:0 0 calc(var(--k)*10px)}}
.frame{{position:relative;margin:0;flex:none;height:100%;aspect-ratio:4/5;max-width:880px;padding:var(--bw);background:var(--frame-bg);
  border-radius:var(--fr);box-shadow:var(--frame-shadow);transform:rotate(var(--rot,0deg))}}
.frame.sq{{aspect-ratio:1/1}}
.frame img{{display:block;width:100%;height:100%;object-fit:cover;border-radius:calc(var(--fr) - var(--bw) + 2px)}}
.pics.n2 .frame,.pics.n3 .frame{{height:auto}}
.pics.n2 .frame{{width:430px}} .pics.n3 .frame{{width:290px}}
.pics.n2 .frame:nth-child(1){{--rot:3deg}} .pics.n2 .frame:nth-child(2){{--rot:-3deg}}
.pics.n3 .frame:nth-child(1){{--rot:4deg}} .pics.n3 .frame:nth-child(2){{--rot:-2deg;margin-top:-60px}} .pics.n3 .frame:nth-child(3){{--rot:3deg}}
.frame.todo{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;border:5px dashed currentColor;background:transparent;
  font:800 40px "Heebo LB";opacity:.8}}
.frame.todo small{{font:500 26px "Assistant LB";max-width:80%}}
.arrow{{position:absolute;left:50%;margin-left:-36px;bottom:40px;width:72px;height:72px;border-radius:50%;z-index:4;display:flex;align-items:center;
  justify-content:center;background:var(--arrow-bg);color:var(--arrow-fg);box-shadow:0 8px 18px rgba(0,0,0,.35)}}
/* the one-picture post: the usual buy crossed out, the better option over its photo */
.vs{{flex:1 1 0;min-height:0;width:100%;position:relative;z-index:1;display:flex;align-items:center;justify-content:center;gap:34px;margin-top:calc(var(--k)*34px)}}
.opt{{position:relative;display:flex;flex-direction:column;align-items:center}}
.opt.no{{width:320px}}
.nobox{{width:100%;height:400px;border-radius:30px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;padding:28px;
  border:4px dashed var(--no-line);background:var(--no-bg);color:var(--no-fg);transform:rotate(3deg)}}
.nobox p{{margin:0;font:800 calc(var(--k)*46px)/1.15 "Heebo LB";text-decoration:line-through;text-decoration-thickness:5px;text-decoration-color:var(--no-strike)}}
.opt.yes{{width:560px;height:100%}}
.opt.yes .frame{{width:100%;height:auto;flex:1 1 0;min-height:0;aspect-ratio:auto;--rot:-2deg}}
.opt.yes .cap{{position:relative;z-index:2;margin:calc(var(--k)*22px) 0 0;font:900 calc(var(--k)*46px)/1.15 "Heebo LB"}}
.ic{{width:92px;height:92px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex:none}}
.ic svg{{width:54px;height:54px}}
.nobox .ic{{background:var(--no-ic-bg);color:var(--no-ic-fg)}}
.opt.yes .ic{{position:absolute;top:-30px;right:-24px;z-index:3;background:var(--yes-ic-bg);color:var(--yes-ic-fg);box-shadow:0 8px 20px rgba(0,0,0,.35)}}
.foot{{flex:none;position:relative;z-index:2;margin-top:calc(var(--k)*30px)}}
.foot .b{{margin:0}}
#report{{display:none}}

/* black friday: black and white */
.t-bf .slide{{--fg:#FFFFFF;--em-bg:#FFFFFF;--em-fg:#0B0B0B;--em-c:#FFFFFF;--pill-bg:#FFFFFF;--pill-fg:#0B0B0B;--chip-bg:#FFFFFF;--chip-fg:#0B0B0B;
  --disc-bg:#FFFFFF;--disc-fg:#0B0B0B;--frame-bg:#FFFFFF;--bw:14px;--fr:10px;--frame-shadow:0 34px 70px rgba(0,0,0,.65);--arrow-bg:#FFFFFF;--arrow-fg:#0B0B0B;
  --no-bg:#1C1C1C;--no-fg:#9A9A9A;--no-line:#5A5A5A;--no-strike:#FFFFFF;--no-ic-bg:#3A3A3A;--no-ic-fg:#FFFFFF;--yes-ic-bg:#FFFFFF;--yes-ic-fg:#0B0B0B;background:#0B0B0B}}
.t-bf .slide.inv{{--fg:#0B0B0B;--em-bg:#0B0B0B;--em-fg:#FFFFFF;--em-c:#0B0B0B;--pill-bg:#0B0B0B;--pill-fg:#FFFFFF;--chip-bg:#0B0B0B;--chip-fg:#FFFFFF;
  --disc-bg:#0B0B0B;--disc-fg:#FFFFFF;--frame-bg:#0B0B0B;--frame-shadow:0 30px 60px rgba(0,0,0,.35);--arrow-bg:#0B0B0B;--arrow-fg:#FFFFFF;background:#F2F2F0}}
.t-bf .pat{{background:radial-gradient(rgba(255,255,255,.16) 1.7px,transparent 2px) 0 0/26px 26px,
  repeating-linear-gradient(135deg,rgba(255,255,255,.06) 0 3px,transparent 3px 34px)}}
.t-bf .inv .pat{{background:radial-gradient(rgba(0,0,0,.14) 1.7px,transparent 2px) 0 0/26px 26px,
  repeating-linear-gradient(135deg,rgba(0,0,0,.05) 0 3px,transparent 3px 34px)}}
.t-bf .glow{{background:radial-gradient(70% 45% at 50% 64%,rgba(255,255,255,.10),rgba(255,255,255,0) 70%)}}
.t-bf .inv .glow{{background:none}}
.t-bf .h{{line-height:1.2}}
.t-bf em{{display:inline-block;line-height:1;background:var(--em-bg);color:var(--em-fg);padding:.04em .16em .12em;border-radius:.06em}}
.t-bf .frame:not(.todo){{--rot:-1.6deg}} .t-bf .inv .frame:not(.todo){{--rot:1.6deg}}
.tape{{position:absolute;left:-90px;right:-90px;bottom:132px;height:78px;z-index:3;display:flex;align-items:center;overflow:hidden;
  background:#FFFFFF;color:#0B0B0B;border-top:5px solid #0B0B0B;border-bottom:5px solid #0B0B0B;transform:rotate(-3.5deg);box-shadow:0 12px 30px rgba(0,0,0,.5)}}
.tape .run{{display:flex;align-items:center;gap:28px;white-space:nowrap;direction:ltr;font:900 40px/1 "Heebo LB";letter-spacing:.06em;padding-left:24px}}
.tape i{{font-style:normal;font-size:30px}}
.ad .tape{{top:30px;bottom:auto;transform:rotate(-2.5deg)}}
.slide.ad{{padding-top:150px}}

/* hanukkah: warm and magical */
.t-hanukkah .slide{{--fg:#FFF3D6;--em-c:#FFD36E;--pill-bg:linear-gradient(135deg,#FFE7A6,#E0A23E);--pill-fg:#3A1206;--chip-bg:linear-gradient(135deg,#FFE7A6,#E0A23E);
  --chip-fg:#3A1206;--disc-bg:radial-gradient(circle at 35% 30%,#FFF0B8,#E2A33B 60%,#A8661A);--disc-fg:#3A1206;
  --frame-bg:linear-gradient(145deg,#FFE6A3,#C98A2B 38%,#FFE29A 62%,#B9771F);--bw:11px;--fr:34px;
  --frame-shadow:0 0 0 2px rgba(255,230,160,.45),0 0 80px rgba(255,176,64,.55),0 34px 64px rgba(0,0,0,.55);
  --arrow-bg:linear-gradient(135deg,#FFE7A6,#E0A23E);--arrow-fg:#3A1206;
  --no-bg:rgba(30,10,30,.55);--no-fg:rgba(255,243,214,.6);--no-line:rgba(255,213,138,.45);--no-strike:#FFD36E;--no-ic-bg:rgba(255,243,214,.18);--no-ic-fg:#FFF3D6;
  --yes-ic-bg:linear-gradient(135deg,#FFE7A6,#E0A23E);--yes-ic-fg:#3A1206;
  background:radial-gradient(130% 80% at 50% 72%,#8A3A14 0%,#46171A 46%,#1B0A20 100%)}}
.t-hanukkah .pat{{background:url("data:image/svg+xml,{tile}") 0 0/240px 240px;opacity:.9}}
.t-hanukkah .glow{{background:
  radial-gradient(60% 40% at 50% 66%,rgba(255,196,96,.42),rgba(255,160,60,0) 70%),
  radial-gradient(circle 110px at 12% 18%,rgba(255,205,130,.22),rgba(255,205,130,0)),
  radial-gradient(circle 80px at 88% 12%,rgba(255,215,150,.20),rgba(255,215,150,0)),
  radial-gradient(circle 140px at 92% 78%,rgba(255,180,90,.18),rgba(255,180,90,0)),
  radial-gradient(circle 90px at 8% 86%,rgba(255,200,120,.20),rgba(255,200,120,0))}}
.t-hanukkah .h,.t-hanukkah .q{{text-shadow:0 4px 22px rgba(0,0,0,.45)}}
.t-hanukkah em{{color:var(--em-c);text-shadow:0 0 .35em rgba(255,186,73,.8),0 4px 22px rgba(0,0,0,.4)}}
.t-hanukkah .l-cover .frame,.t-hanukkah .l-cover .frame img{{border-radius:999px 999px 34px 34px}}
.t-hanukkah .frame:not(.todo){{--rot:0deg}}
"""


FIT_JS = """
(function(){
  const q = new URLSearchParams(location.search), one = q.get('s');
  const slides = [...document.querySelectorAll('.slide')];
  if (one) { document.body.classList.add('one'); slides.forEach(s => s.classList.toggle('on', s.dataset.n === one)); }
  const room = s => { const p = s.querySelector('.pics, .vs'); return p ? p.getBoundingClientRect().height : 9999; };
  const over = s => { const t = s.querySelector('.foot') || s.querySelector('.txt'); if (!t) return false;
    const sr = s.getBoundingClientRect(), r = t.getBoundingClientRect();
    return room(s) < Number(s.dataset.min || 380) || r.bottom > sr.bottom - 118 || r.top - sr.top < 30; };
  const report = [];
  const fit = () => slides.forEach(s => { if (one && s.dataset.n !== one) return; let k = 1; s.style.setProperty('--k', k);
    while (over(s) && k > 0.56) { k = Math.round((k - 0.03) * 100) / 100; s.style.setProperty('--k', k); }
    report.push({n: Number(s.dataset.n), k, fits: !over(s), dir: getComputedStyle(s).direction, pics: Math.round(room(s))}); });
  const done = () => { fit(); if (q.get('check')) document.getElementById('report').textContent = JSON.stringify(report); };
  let ran = false; const once = () => { if (!ran) { ran = true; done(); } };
  const imgs = [...document.images].map(i => i.complete ? Promise.resolve() : new Promise(r => { i.onload = i.onerror = r; }));
  Promise.all([document.fonts ? document.fonts.ready : Promise.resolve(), ...imgs]).then(once); setTimeout(once, 3000);
})();
"""


def pics_of(s):
    if s.get("layout") == "covers":
        return list(s.get("covers") or [])[:3]
    if s.get("pics"):
        return list(s["pics"])[:3]
    if s.get("layout") == "cta" and s.get("cover"):
        return [s["cover"]]
    return [s["bg"]] if s.get("bg") else []


def frame(car, key, s, k, base, cls=""):
    """One picture in its own box: a real one from the test batch's assets.json, or a picture the carousel makes."""
    made_list = car.get("pictures") or {}
    pos = s.get("pos") if k == s.get("bg") else None
    if k in made_list:
        made = tb.made_picture(key, k)
        if not made:
            return (f'<figure class="frame todo {cls}"><span>תמונה שתיווצר בהפקה</span>'
                    f'<small>{html.escape(made_list[k].get("purpose", ""))}</small></figure>')
        src, p = tb._src(made, base), pos or "50% 40%"
    else:
        a = tb.assets().get(k)
        if not a:
            return f'<figure class="frame todo {cls}"><span>חסרה תמונה</span><small>{html.escape(str(k))}</small></figure>'
        src, p = tb._src(lib.ROOT / a["file"], base), pos or a.get("position", "50% 40%")
    shape = " sq" if str(k).startswith("cover-") else ""
    return f'<figure class="frame{shape} {cls}"><img src="{src}" alt="" style="object-position:{p}"></figure>'


def body_html(car, s):
    body = tb.rich(s.get("body", ""))
    word = car.get("comment_word", "")
    if word:
        body = body.replace(f'&quot;{html.escape(word)}&quot;', f'<b class="word">״{html.escape(word)}״</b>')
    return body


def slide_html(car, s, n, total, base, key):
    t = car["type"]
    lay = s.get("layout", "point")
    single = car.get("format") == "single"
    inv = t == "bf" and not single and lay not in ("cover", "cta") and n % 2 == 0
    cls = f"slide l-{lay}" + (" ad" if single else "") + (" inv" if inv else "")
    parts = [f'<section class="{cls}" data-n="{n}"><div class="pat"></div><div class="glow"></div>']
    if t == "bf" and (single or lay in ("cover", "cta")):
        parts.append(TAPE)
    txt = []
    if s.get(tb.NUM_FIELD):
        txt.append(f'<div class="num">{int(s[tb.NUM_FIELD])}</div>')
    if s.get("label"):
        txt.append(f'<div class="label">{tb.rich(s["label"])}</div>')
    if lay == "quote":
        txt.append('<div class="qmark">״</div>')
        txt.append(f'<blockquote class="q">{tb.rich(s.get("quote", ""))}</blockquote>')
        if s.get("by"):
            txt.append(f'<div class="by">{tb.rich(s["by"])}</div>')
    elif s.get("headline"):
        tag = "h1" if lay == "cover" or single else "h2"
        txt.append(f'<{tag} class="h">{tb.rich(s["headline"])}</{tag}>')
    if s.get("body") and not single:
        txt.append(f'<p class="b">{body_html(car, s)}</p>')
    text = '<div class="txt">' + "".join(txt) + '</div>'
    if single:
        yes_pic = frame(car, key, s, s["bg"], base) if s.get("bg") else ""
        vs = ('<div class="vs">'
              f'<div class="opt no"><div class="nobox"><i class="ic">{X_ICON}</i><p>{tb.rich(s.get("no", ""))}</p></div></div>'
              f'<div class="opt yes"><i class="ic">{V_ICON}</i>{yes_pic}<p class="cap">{tb.rich(s.get("yes", ""))}</p></div>'
              '</div>')
        parts += [text, vs, f'<div class="foot"><p class="b">{body_html(car, s)}</p></div>']
        parts[0] = parts[0].replace('data-n=', 'data-min="440" data-n=')
    else:
        ps = pics_of(s)
        boxes = f'<div class="pics n{len(ps)}">' + "".join(frame(car, key, s, k, base) for k in ps) + '</div>' if ps else ""
        parts += [boxes, text] if lay == "quote" else [text, boxes]
    if n < total:
        parts.append(ARROW)
    parts.append('</section>')
    return "".join(parts)


def slides_html(car, key, out_dir):
    total = len(car["slides"])
    body = "".join(slide_html(car, s, n, total, out_dir, key) for n, s in enumerate(car["slides"], start=1))
    return ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{html.escape(key)}</title><style>{css(out_dir)}</style></head>'
            f'<body dir="rtl" class="t-{car["type"]}">{body}<pre id="report"></pre><script>{FIT_JS}</script></body></html>')


def render(key):
    """Draw the slides as 1080 x 1350 PNGs in slides/KEY, with the contact sheet and the fit report. Returns problems."""
    import compose_slides as cs
    car = tb.load(key)
    out_dir = tb.SLIDES / key
    out_dir.mkdir(parents=True, exist_ok=True)
    page = out_dir / "slides.html"
    page.write_text(slides_html(car, key, out_dir), encoding="utf-8")
    for old in out_dir.glob("[0-9][0-9].png"):
        if int(old.stem) > len(car["slides"]):
            old.unlink()
    dom = cs.dump_dom(page.as_uri() + "?check=1", W, H)
    m = re.search(r'<pre id="report">(.*?)</pre>', dom, re.S)
    report = json.loads(html.unescape(m.group(1))) if m and m.group(1).strip() else []
    problems = [f"slide {r['n']}: the words leave too little room for the picture even at the smallest size; shorten them" for r in report if not r.get("fits")]
    problems += [f"slide {r['n']}: direction {r['dir']}" for r in report if r.get("dir") != "rtl"]
    if not report:
        problems.append("the slide check could not read the page")
    for n in range(1, len(car["slides"]) + 1):
        cs.screenshot(page.as_uri() + f"?s={n}", out_dir / f"{n:02d}.png", W, H)
    cs.contact_sheet(out_dir, len(car["slides"]))
    lib.write_json(out_dir / "render-report.json", {"problems": problems, "slides": report})
    return problems


# ---------------------------------------------------------------- checks

def lint(key):
    """test_batch.lint, with the one-picture post's own shape: one slide, more words, both cover and CTA rules met by it."""
    car = tb.load(key)
    issues = tb.lint(car, key)
    known = tb.assets()
    for i, s in enumerate(car.get("slides") or [], start=1):
        for k in s.get("pics") or []:
            if k not in known and k not in (car.get("pictures") or {}):
                issues.append(tb._issue("ERROR", f"{key}/slide-{i}", f"picture {k!r} is not in assets.json"))
    if car.get("format") != "single":
        return issues
    out = []
    for i in issues:
        m = i.message
        if "slides; 6 to 10" in m or m == "slide 1 is the cover":
            continue
        w = re.match(r"(\d+) words on the slide \(max \d+\)", m)
        if w:
            if int(w.group(1)) > SINGLE_MAX_WORDS:
                out.append(tb._issue("ERROR", i.path, f"{w.group(1)} words on the picture (max {SINGLE_MAX_WORDS})"))
            continue
        out.append(i)
    s = (car.get("slides") or [{}])[0]
    if len(car.get("slides") or []) != 1 or s.get("layout") != "cta" or not (s.get("no") and s.get("yes") and s.get("bg")):
        out.append(tb._issue("ERROR", key, "a one-picture post is one cta slide with no, yes, bg, headline and body"))
    return out


def run_lint(ks):
    bad = 0
    for k in ks:
        issues = lint(k)
        errs = [i for i in issues if i.level == "ERROR"]
        warns = [i for i in issues if i.level == "WARN"]
        bad += len(errs)
        print(f"{k}: {len(errs)} errors, {len(warns)} warnings")
        for i in errs + warns:
            print(f"  {i.level} {i.path}: {i.message}" + (f"  [{i.excerpt}]" if getattr(i, "excerpt", "") else ""))
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["status", "lint", "render"])
    ap.add_argument("keys", nargs="*")
    a = ap.parse_args()
    ks = a.keys or tb.keys()
    if a.cmd == "status":
        for k in tb.keys():
            car = tb.load(k)
            b = tb.budget(car)
            kind = "one picture" if car.get("format") == "single" else f"{len(car['slides'])} slides"
            print(f"{k}  {car['date']}  {car['type']:9}  {kind}  pictures to make: {b['images']}  ${b['usd']}  {car.get('title', '')}")
    elif a.cmd == "lint":
        sys.exit(1 if run_lint(ks) else 0)
    else:
        for k in ks:
            problems = render(k)
            print(f"{k}: rendered to {tb.SLIDES / k}" + (f"  PROBLEMS: {problems}" if problems else ""))


if __name__ == "__main__":
    main()
