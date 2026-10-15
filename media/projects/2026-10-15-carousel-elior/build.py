"""Customer-story carousel about Elior, in the LumeBook design system (shared/design/lumebook.css tokens):
night-sky brand background with gold sparkles, gold-framed photos, cream type. Local only, no paid calls.
Run: python3 build.py  ->  final/01.png ... final/NN.png (1080x1350) + final/contact-sheet.png"""
import html, json, shutil, subprocess, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BG = (ROOT / "shared/brand/social-backgrounds/lumebook-carousel-bg-v1.png").as_uri()
HEEBO = (ROOT / "shared/brand/fonts/Heebo-Black.ttf").as_uri()
HEEBO_B = (ROOT / "shared/brand/fonts/Heebo-Bold.ttf").as_uri()
slides = json.load(open(HERE / "slides.json"))

# design-system tokens (shared/design/lumebook.css)
CSS = """
@import url("https://fonts.googleapis.com/css2?family=Varela+Round&display=block");
@font-face{font-family:"HeeboX";src:url("%(heebo)s") format("truetype");font-weight:900}
@font-face{font-family:"HeeboX";src:url("%(heebo_b)s") format("truetype");font-weight:700}
:root{--lb-ink:#1D1039;--lb-ink-deep:#0B0518;--lb-gold:#E6B762;--lb-gold-deep:#C9954A;--lb-violet:#5B2BD6;--lb-cream:#F8F0E1}
html,body{margin:0;direction:rtl}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden;background:var(--lb-ink-deep) url("%(bg)s") center/cover no-repeat;text-align:center}
.slide:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,5,24,.72) 0,rgba(11,5,24,.35) 34%%,rgba(11,5,24,0) 60%%)}
.band{position:absolute;top:60px;left:70px;right:70px;height:%(band)spx;display:flex;flex-direction:column;align-items:center;justify-content:center}
.h{font-family:"Varela Round","HeeboX",sans-serif;font-weight:400;color:var(--lb-cream);font-size:92px;line-height:1.1;text-shadow:0 0 28px rgba(230,183,98,.45),0 2px 0 rgba(11,5,24,.4)}
.b{font-family:"HeeboX",sans-serif;font-weight:700;color:var(--lb-gold);font-size:50px;line-height:1.25;margin-top:18px}
.ln{display:block;white-space:nowrap;text-align:center}
.note{font-family:"HeeboX",sans-serif;font-weight:700;color:var(--lb-cream);opacity:.55;font-size:24px;margin-top:14px}
.frame{position:absolute;left:50%%;width:860px;height:780px;top:%(ftop)spx;border-radius:40px;padding:8px;
  background:linear-gradient(135deg,#F6D98F,var(--lb-gold) 40%%,var(--lb-gold-deep));box-shadow:0 0 70px rgba(230,183,98,.45),0 24px 60px rgba(0,0,0,.5)}
.frame img{width:100%%;height:100%%;object-fit:cover;display:block;border-radius:32px}
.spark{position:absolute;fill:#F6D98F;filter:drop-shadow(0 0 10px rgba(246,217,143,.9))}
.arrow{position:absolute;left:50%%;transform:translateX(-50%%);bottom:34px;width:84px;height:84px;border-radius:50%%;background:var(--lb-gold);display:flex;align-items:center;justify-content:center;box-shadow:0 0 30px rgba(230,183,98,.6)}
.arrow svg{width:42px;height:42px}.arrow path{fill:none;stroke:var(--lb-ink);stroke-width:5.5;stroke-linecap:round;stroke-linejoin:round}
.cta .band{top:auto;bottom:110px;height:430px}
.cta .h{font-size:74px}
.cta:after{content:"";position:absolute;left:0;right:0;bottom:0;height:640px;background:linear-gradient(0deg,rgba(11,5,24,.9) 0,rgba(11,5,24,.75) 55%%,rgba(11,5,24,0) 100%%)}
.cta .band{z-index:2}
.cta .b{color:var(--lb-cream);font-size:48px;margin-top:30px}
.btn{display:inline-block;background:var(--lb-gold);color:var(--lb-ink);border-radius:.45em;padding:.08em .55em .14em;margin-bottom:.22em;box-shadow:0 0 36px rgba(230,183,98,.55)}
.cta .frame{top:90px;width:560px;height:640px}
"""
BAND, FTOP = 400, 480

STAR = '<svg class="spark" style="{s}" viewBox="0 0 40 40"><path d="M20 0 C22 14 26 18 40 20 C26 22 22 26 20 40 C18 26 14 22 0 20 C14 18 18 14 20 0Z"/></svg>'
SPARKS = [("left:70px;top:{t1}px;width:54px", ), ("right:84px;top:{t2}px;width:34px",), ("left:120px;bottom:120px;width:30px",),
          ("right:60px;bottom:170px;width:58px",), ("left:520px;top:{t3}px;width:22px",)]

def sparks(ftop):
    pos = [f"left:62px;top:{ftop - 34}px;width:56px", f"right:70px;top:{ftop + 120}px;width:34px",
           f"left:96px;top:{ftop + 560}px;width:28px", f"right:46px;top:{ftop + 700}px;width:60px", f"right:150px;top:{ftop + 812}px;width:20px"]
    return "".join(STAR.format(s=p) for p in pos)

ARROW = '<div class="arrow"><svg viewBox="0 0 44 44"><path d="M27 10 L15 22 L27 34"/></svg></div>'

def lines(text, button_line=None):
    out = []
    for i, l in enumerate(text.split("\n")):
        t = html.escape(l)
        out.append(f'<span class="ln">{f"<span class=btn>{t}</span>" if i == button_line else t}</span>')
    return "".join(out)

def slide_html(i, s):
    tilt = -1.6 if i % 2 else 1.6
    if s.get("cta"):
        img = (HERE / "source/photo-cover.jpg").as_uri()
        return (f'<div class="slide cta"><div class="frame" style="transform:translateX(-50%) rotate(-2.4deg)"><img src="{img}" style="object-position:50% 12%"></div>'
                f'{sparks(90)}<div class="band"><div class="h">{lines(s["h"])}</div><div class="b">{lines(s["b"], button_line=0)}</div></div></div>')
    bsize = f' style="font-size:{s["bsize"]}px"' if s.get("bsize") else ""
    hsize = f' style="font-size:{s["hsize"]}px"' if s.get("hsize") else ""
    note = f'<div class="note">{html.escape(s["note"])}</div>' if s.get("note") else ""
    img = (HERE / s["img"]).as_uri()
    return (f'<div class="slide"><div class="frame" style="transform:translateX(-50%) rotate({tilt}deg)"><img src="{img}" style="object-position:{s["pos"]}"></div>'
            f'{sparks(FTOP)}<div class="band"><div class="h"{hsize}>{lines(s["h"])}</div><div class="b"{bsize}>{lines(s["b"])}</div>{note}</div>{ARROW}</div>')

def shoot(page, out):
    profile = tempfile.mkdtemp(prefix="lumebook-chrome-")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={profile}",
           "--force-device-scale-factor=1", "--allow-file-access-from-files", "--virtual-time-budget=9000",
           "--window-size=1080,1350", f"--screenshot={out}", page.as_uri()]
    out.unlink(missing_ok=True)
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(200):  # Chrome sometimes writes the PNG and never exits
        time.sleep(0.25)
        if proc.poll() is not None or (out.exists() and out.stat().st_size > 0):
            time.sleep(0.4); break
    if proc.poll() is None: proc.kill()
    shutil.rmtree(profile, ignore_errors=True)

css = CSS % {"heebo": HEEBO, "heebo_b": HEEBO_B, "bg": BG, "band": BAND, "ftop": FTOP}
final = HERE / "final"; final.mkdir(exist_ok=True)
work = HERE / "_html"; work.mkdir(exist_ok=True)
for i, s in enumerate(slides, 1):
    page = work / f"{i:02d}.html"
    page.write_text(f'<!doctype html><meta charset="utf-8"><style>{css}</style><body dir="rtl">{slide_html(i, s)}</body>')
    shoot(page, final / f"{i:02d}.png")
    print(final / f"{i:02d}.png", (final / f"{i:02d}.png").exists())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", str(final / "0*.png"),
                "-vf", f"scale=300:-1,tile={len(slides)}x1", "-frames:v", "1", str(final / "contact-sheet.png")], check=True)
