"""The Lotem-look render (Yarin, 29 Oct 2026: "design the text like her but in lumebooks design system, change the font to
the websites font" and "create a different image for each slide like her as well").

Her text treatment (research/lotem-lerner-carousels/README.md, Visual): light type on a dimmed picture, a big cover line
with one coloured pill under it, a small label above each part of a point slide. Here in LumeBook's site palette (ink
#0B0518, gold #E6B762, cream #F8F0E1, from https://lumebook.com/assets/index-*.css :root) and the site's font, Varela
Round (shared/brand/fonts/VarelaRound-*.woff2, the files lumebook.com serves). No logo, handle or arrow: carousels do
not name the brand.

Pictures: slide 1 is pictures/<id>.png, slides 2 to 12 pictures/<id>/NN.png (falls back to the cover picture).
Writes runs/<id>/final-v4/ (final-v2/ short copy, final-v3/ long lists, same evening) (01.png ... 12.png at 1080 x 1350, contact sheet, caption, sources, alt text, fit report).
Usage: python3 render.py [lotem-1 ...]"""
import html, json, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "carousel" / "carousel-pipeline" / "scripts"))
import compose_slides as cs  # noqa: E402  (Chrome screenshots, contact sheet, caption and sources files)

FONTS = ROOT / "shared" / "brand" / "fonts"
W, H = 1080, 1350

CSS = """
@font-face{font-family:"Varela Round";src:url("{he}") format("woff2");unicode-range:U+0307-0308,U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F}
@font-face{font-family:"Varela Round";src:url("{la}") format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
:root{--ink:#0B0518;--ink-2:#1D1039;--gold:#E6B762;--gold-soft:#F3D9A1;--cream:#F8F0E1}
*{box-sizing:border-box;margin:0;padding:0}
html,body{direction:rtl;background:#0B0518}
body.single .slide:not(.on){display:none}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:var(--ink);font-family:"Varela Round",sans-serif;color:var(--cream);text-align:center}
.art{position:absolute;inset:0;width:1080px;height:1350px;object-fit:cover}
/* her inner slides dim the whole picture; ours dim it with the site's ink, most where the words are */
.veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,5,24,.88) 0,rgba(11,5,24,.8) 45%,rgba(11,5,24,.55) 66%,rgba(11,5,24,.22) 84%,rgba(11,5,24,.38) 100%)}
.cover .veil{background:linear-gradient(180deg,rgba(11,5,24,.88) 0,rgba(11,5,24,.66) 30%,rgba(11,5,24,0) 52%)}
.cta .veil{background:linear-gradient(180deg,rgba(11,5,24,.9) 0,rgba(11,5,24,.78) 40%,rgba(11,5,24,.45) 70%,rgba(11,5,24,.55) 100%)}
.copy{position:absolute;top:70px;left:70px;right:70px;direction:rtl}
.h,.t{text-wrap:balance;-webkit-text-stroke:.022em currentColor;paint-order:stroke fill;text-shadow:0 2px 22px rgba(11,5,24,.7)}
.h{line-height:1.16;letter-spacing:-.005em}
.h .ln{display:block}
.t{font-size:.74em;line-height:1.3;margin-top:.15em;-webkit-text-stroke-width:.014em}
.part{margin-top:.5em}
.lab{display:block;color:var(--gold);font-size:.56em;letter-spacing:.01em;margin-bottom:.15em;-webkit-text-stroke:.012em currentColor;text-shadow:0 2px 16px rgba(11,5,24,.8)}
.q{color:var(--gold-soft)}
/* her numbered points: a small round badge above the child's line (gold, the site's accent) */
.num{display:inline-flex;align-items:center;justify-content:center;width:84px;height:84px;border-radius:50%;background:var(--gold);color:var(--ink);font-size:46px;margin-bottom:26px;box-shadow:0 8px 24px rgba(11,5,24,.45)}
/* her cover: big light line, one red pill under it; ours is gold with ink type */
.pill{display:inline-block;margin-top:34px;background:var(--gold);color:var(--ink);border-radius:999px;padding:.22em .9em .3em;font-size:.5em;line-height:1.2;box-shadow:0 10px 28px rgba(11,5,24,.45)}
.btn{display:inline-flex;white-space:nowrap;align-items:center;gap:.35em;background:var(--gold);color:var(--ink);border-radius:999px;padding:.16em .8em .24em;-webkit-text-stroke:.02em currentColor;text-shadow:none;box-shadow:0 12px 30px rgba(0,0,0,.45)}
.btn svg{width:.8em;height:.8em;fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
/* version 3 (29 Oct 2026, "too little text ... too repetitive"): her point slides read as a short inner monologue.
   A small numbered tag on top (her "1: ..." label), the child's line, then a body that mixes plain lines, gold labels
   (## in the copy), a cream card with a sentence to say (> ), gold emphasis (**) and paragraph gaps (blank line). */
.tag{display:inline-flex;align-items:center;gap:.3em;color:var(--gold);font-size:.46em;margin-bottom:.45em;-webkit-text-stroke:.012em currentColor;text-shadow:0 2px 16px rgba(11,5,24,.8)}
.tag .num{width:1.55em;height:1.55em;margin:0;font-size:1em;box-shadow:0 6px 18px rgba(11,5,24,.45);-webkit-text-stroke:0}
.body{font-size:.6em;margin-top:.55em}
.body .t{font-size:1em;margin-top:0}
.body .t .ln{display:block;white-space:nowrap}
.body .gap{height:.55em}
.body .lab{font-size:.8em;margin:.55em 0 .05em}
.body .lab:first-child{margin-top:0}
.em{color:var(--gold);-webkit-text-stroke:.03em currentColor}
.say{display:inline-block;margin-top:.15em;background:var(--cream);color:var(--ink);border-radius:.7em;padding:.28em .8em .36em;line-height:1.3;-webkit-text-stroke:.012em currentColor;text-shadow:none;box-shadow:0 10px 28px rgba(11,5,24,.5)}
.say .q{color:var(--ink)}
/* version 4 (29 Oct 2026, "why always lists?"): each option its own structure. A tag without a number is plain gold
   text (a time of day, "פעם", "אתם חושבים:"). The letter option sets its words on a cream sheet in ink. */
.tag.plain{font-size:.5em}
.letter .copy{background:var(--cream);color:var(--ink);border-radius:34px;padding:56px 58px 60px;transform:rotate(-1.2deg);box-shadow:0 24px 60px rgba(11,5,24,.55)}
.letter .h,.letter .t,.letter .lab{text-shadow:none}
.letter .h{font-size:.92em}
.letter .em,.letter .q{color:#8A5A14}
.letter .veil{background:linear-gradient(180deg,rgba(11,5,24,.55) 0,rgba(11,5,24,.3) 60%,rgba(11,5,24,.2) 100%)}
pre#fit{display:none}
"""

JS = """
const q = new URLSearchParams(location.search), one = q.get('s');
if (one) { document.body.classList.add('single'); document.querySelector('.slide[data-n="' + one + '"]').classList.add('on'); }
function fit(s) {
  // the whole copy block shrinks in steps until it ends above data-maxh and no word runs past the sides
  const c = s.querySelector('.copy'), maxH = Number(c.dataset.maxh), min = Number(c.dataset.min);
  let k = Number(c.dataset.max);
  const over = () => c.scrollHeight > maxH || [...c.querySelectorAll('.h,.t,.pill,.say')].some(e => e.scrollWidth > e.clientWidth + 1);
  c.style.fontSize = k + 'px';
  while (over() && k > min) { k -= 2; c.style.fontSize = k + 'px'; }
  return { n: Number(s.dataset.n), size: k, height: c.scrollHeight, maxH, ok: !over() };
}
(async () => {
  try { await document.fonts.ready; } catch (e) {}
  await Promise.all([...document.images].map(i => i.complete ? null : new Promise(r => { i.onload = r; i.onerror = r; })));
  const rep = [...document.querySelectorAll('.slide')].map(fit);
  rep.forEach(r => r.font = document.fonts.check('40px "Varela Round"', 'אב'));
  document.getElementById('fit').textContent = JSON.stringify(rep);
  document.body.dataset.ready = '1';
})();
"""

SAVE_ICON = '<svg viewBox="0 0 24 24"><path d="M6.5 3h11a1.5 1.5 0 0 1 1.5 1.5V21l-7-6.2L5 21V4.5A1.5 1.5 0 0 1 6.5 3z"/></svg>'
QUOTE = re.compile(r"(״[^״]+״)")
LABELS = ("מה יעזור לי:", "בעצם")


def esc(t):
    return html.escape(t, quote=False)


def text(t):
    # spoken lines in quotation marks in the soft gold
    return "".join(f'<span class="q">{esc(p)}</span>' if i % 2 else esc(p) for i, p in enumerate(QUOTE.split(t)))


def rich(t):
    # **x** in the copy is gold emphasis, the stand-in for her heavy-bold words (Varela Round has one weight)
    return "".join(f'<span class="em">{text(p)}</span>' if i % 2 else text(p) for i, p in enumerate(t.split("**")))


def body_html(body):
    """Version 3 body: '## ' gold label, '> ' cream card, blank line a gap, other lines grouped into paragraphs."""
    out, para = [], []
    def flush():
        if para:
            out.append('<div class="t">' + "".join(f'<span class="ln">{rich(l)}</span>' for l in para) + "</div>")
            para.clear()
    for line in body.split("\n"):
        line = line.strip()
        if not line:
            flush(); out.append('<div class="gap"></div>')
        elif line.startswith("## "):
            flush(); out.append(f'<div class="lab">{rich(line[3:])}</div>')
        elif line.startswith("> "):
            flush(); out.append(f'<div><span class="say">{rich(line[2:])}</span></div>')
        else:
            para.append(line)
    flush()
    return '<div class="body">' + "".join(out) + "</div>"


def part(line):
    """A body line; one that opens with בעצם or מה יעזור לי: gets that opening as her small label above it."""
    for lab in LABELS:
        if line.startswith(lab + " ") or line.startswith(lab):
            rest = line[len(lab):].strip()
            return f'<div class="part"><span class="lab">{esc(lab)}</span><div class="t">{text(rest)}</div></div>'
    return f'<div class="part"><div class="t">{text(line)}</div></div>'


def slide_html(o, n, s, img, last):
    head, body = s["headline"], s.get("body", "").strip()
    cls, inner = "", []
    if n == 1:
        cls = "cover"
        inner.append('<div class="h">' + "".join(f'<span class="ln">{text(l)}</span>' for l in head.split("\n")) + "</div>")
        if body:
            inner.append(f'<div class="pill">{esc(body)}</div>')
        size = (104, 72, 560)
    elif n == last:
        cls = "cta"
        inner.append(f'<div class="h"><span class="btn">{SAVE_ICON}{esc(head)}</span></div>')
        inner.append('<div class="part"><div class="t" style="font-size:.9em">' + rich(body) + "</div></div>")
        size = (84, 60, 520)
    else:
        label = s.get("label", "")
        m = re.match(r"(\d+):\s+(.*)", label)
        if m:
            inner.append(f'<div><span class="tag"><span class="num">{m.group(1)}</span>{esc(m.group(2))}</span></div>')
        elif label:
            inner.append(f'<div><span class="tag plain">{esc(label)}</span></div>')
        if head:
            inner.append(f'<div class="h">{rich(head)}</div>')
        if o.get("structure") == "letter":
            cls = "letter"
        inner.append(body_html(body))
        size = (84, 62, 900)
    mx, mn, max_h = size
    return (f'<section class="slide {cls}" data-n="{n}"><img class="art" src="{img}" alt=""><div class="veil"></div>'
            f'<div class="copy" data-max="{mx}" data-min="{mn}" data-maxh="{max_h}" style="font-size:{mx}px">'
            + "".join(inner) + "</div></section>")


def render(oid):
    o = next(x for x in json.load(open(HERE / "options.json")) if x["id"] == oid)
    run = HERE / "runs" / oid
    out = run / "final-v4"
    out.mkdir(parents=True, exist_ok=True)
    rel = lambda p: Path(os.path.relpath(p, out)).as_posix()
    last = len(o["slides"])
    pics = {}
    for n, s in enumerate(o["slides"], 1):
        p = HERE / "pictures" / (s.get("picture") or f"{oid}/{n:02d}.png")
        pics[n] = p if n > 1 and p.exists() else HERE / "pictures" / f"{oid}.png"
    css = CSS.replace("{he}", rel(FONTS / "VarelaRound-hebrew.woff2")).replace("{la}", rel(FONTS / "VarelaRound-latin.woff2"))
    page = ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{oid}</title><style>{css}</style></head><body dir="rtl">'
            + "".join(slide_html(o, n, s, rel(pics[n]), last) for n, s in enumerate(o["slides"], 1))
            + f'<pre id="fit"></pre><script>{JS}</script></body></html>')
    page_path = out / "slides.html"
    page_path.write_text(page, encoding="utf-8")
    dom = cs.dump_dom(page_path.as_uri(), W, H)
    m = re.search(r'<pre id="fit">(.*?)</pre>', dom, re.S)
    report = json.loads(html.unescape(m.group(1))) if m and m.group(1).strip() else []
    (out / "fit-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    for n in range(1, last + 1):
        cs.screenshot(page_path.as_uri() + f"?s={n}", out / f"{n:02d}.png", W, H)
    cs.contact_sheet(out, last)
    frozen = json.load(open(run / "approved.json"))
    frozen["option"].update(caption=o["caption"], slides=[dict(s, number=n) for n, s in enumerate(o["slides"], 1)])
    cs.write_texts(frozen, out)
    bad = [r for r in report if not r["ok"] or not r.get("font")]
    missing = [n for n in range(2, last + 1) if pics[n] == HERE / "pictures" / f"{oid}.png"]
    print(oid, "OK" if report and not bad else f"CHECK {bad or 'no report'}", f"cover picture reused on {missing}" if missing else "")


if __name__ == "__main__":
    for oid in sys.argv[1:] or [f"lotem-{i}" for i in range(1, 6)]:
        render(oid)
