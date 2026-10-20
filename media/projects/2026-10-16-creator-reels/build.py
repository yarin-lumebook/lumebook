"""Gallery of every creator-made video about the book, played straight from the Drive "שיווק" folder.

The files stay in Drive (1.6 GB, shared with Yarin's Google account), so the page must be opened
in a browser that is signed in to that account. Rebuild: python3 media/projects/2026-10-16-creator-reels/build.py
"""
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

UGC_FOLDER = "https://drive.google.com/drive/folders/1C-VjkLdTq7xM830Txm_ulbQrS2E14vml"
RECUT_FOLDER = "https://drive.google.com/drive/folders/1b231Cbc59yN2819H82fJEEeFt0ZMWr9N"
RAW_SHOAM = "https://drive.google.com/drive/folders/1SRSNfgWXQut3Us38XaL_U0QKXLcGxEVZ"

# Folder "תוכן לקוחות ויוצרים", listed 16 Oct 2026. (creator, file title, Drive id, uploaded, size MB)
CREATORS = [
    ("Moran Arges", [
        ("Moran_arges_v1.mov", "1e1_mFb1JIGpzt5RVJ3LNMm30lISeu1bI", "2025-09-28", 146),
        ("Moran_arges_v2.mov", "198rDU3Mz6xYQtm4tq49idDmuEHZRbxbn", "2025-10-07", 169),
        ("Moran_arges_v3.mp4", "10ODaUZwqbceYS3jxh3yXamOQu-dF3wD-", "2025-10-15", 144),
    ]),
    ("Mor Keisar", [
        ("Mor_Keisar_v1.mp4", "1fj6k4nyG51LtaPVS5cNJdjuCsWPRIXhO", "2025-09-28", 6),
        ("Mor_Keisar_v2.MP4", "1hzGZ50nyznY5mvcmstWsU4fOVf1BFA8k", "2025-10-10", 58),
        ("Mor_Keisar_v3.MOV", "1CvE4hId3WfQOW3ZBCp1P_jH5AuNyvvbH", "2025-10-19", 49),
    ]),
    ("Koral", [
        ("Koral_V1.mov", "1EqWhRQAA8SYdd0GmtZb1NghR_r414Xz_", "2025-10-10", 92),
        ("Koral_V2.mov", "1KtkTRhVocwiuei7dyyfOHB6rpyMngfPb", "2025-10-17", 99),
    ]),
    ("Nofit", [
        ("Nofit_Hazut.mov", "1R2u-rzgbZtKz9lKQ2CxiishHwKWO4VmR", "2025-12-03", 56),
        ("Nofit_v1.mov", "1moz1vV9u8lR7NwxdOmKS-RbLpTKOTl67", "2025-12-09", 73),
        ("Nofit_v2.MOV", "13GQ0o-wqfubAdGFLxTHww05HvU9_Jbzh", "2025-12-09", 82),
        ("Nofit_v2_ar1-1.MOV", "1sbKXRolayOQYc-7r0AnhwGQpQ6xPiDbJ", "2026-01-13", 72),
    ]),
    ("Natali Fridman", [
        ("Natali_Fridman_v1.mp4", "1r940nGcdPfZ_FM79Y4LMHVqVacz6zxze", "2025-12-08", 7),
        ("Natali_Fridman_v2.mp4", "1o_nVSqKk5Tax3jt56gOyeR2NCXQCRlrk", "2025-12-09", 81),
        ("Natali_Fridman_v2_ratio1-1.mp4", "19qgLvrhM5rieEfACuJqEknIsJ_eo3gg-", "2026-01-01", 81),
    ]),
    ("Shoam", [
        ("Shoam_v1.mp4", "1eG5hciFf04Ux52XYSFSdmUhPzW0oPVVe", "2026-01-01", 12),
        ("Shoam_v2.mp4", "1om9iZU5yfU_4JCIYmjfarMfDSXm34AT1", "2026-01-11", 87),
        ("Shoam_v2_ar16-9.mp4", "1R45P5FH2JNLW_aQvL1ZadvYFCfqBT_B3", "2026-01-13", 87),
        ("Shoam_v2_ar1-1.mp4", "1AMaIssMTIFs727XbHfCr73l8pjtmA-kX", "2026-01-13", 65),
    ]),
    ("Tal Ifrach", [
        ("Tal_Ifrach_16-9.MOV", "1Jo3w6NqptnpX6jx7NX_4xMUPlek7NWo1", "2026-03-05", 86),
        ("Tal_Ifrach_ar1-1.MOV", "1qWWzB15bENcK7T8JGB-KlQlEBjenNTXg", "2026-03-05", 86),
    ]),
    ("לא מסומן", [
        ("File (4).mp4", "12gohpbZbQY4w4KVOgF4k8Z3prIwyNQPe", "2026-10-13", 24),
    ]),
]

# Folder "9x16", 10 Aug 2026: vertical re-cuts made from the creator footage.
RECUTS = [
    ("06-moran-idea-to-book.mp4", "1lSaaRdF1IcMRufaJEVB2bOaS70-0_k9J", "2026-08-10", 48),
    ("07-natali-open-conversation.mp4", "1uuNGaQMhLFUgNkjREkStIUcY4EtJkTrl", "2026-08-10", 16),
    ("08-nofit-heartfelt-gift.mp4", "13w8xG30fcaOS2aX9Tj4ekGVDUIm8n1sY", "2026-08-10", 31),
    ("09-koral-first-birthday.mp4", "1N6e3JFAJrLj4uMozZDcdc1W5Vo718DGq", "2026-08-10", 22),
    ("10-reader-keeps-turning-pages.mp4", "1R_f6JpohfGlc2vjWd7cDW6In8nYjHzv1", "2026-08-10", 41),
]


def card(title, fid, date, mb):
    t = html.escape(title)
    view = f"https://drive.google.com/file/d/{fid}/view"
    return f"""
    <article class="lb-card is-flush reel">
      <iframe src="https://drive.google.com/file/d/{fid}/preview" loading="lazy" allow="autoplay; fullscreen" allowfullscreen title="{t}"></iframe>
      <div class="meta">
        <a href="{view}" target="_blank" rel="noopener" dir="ltr">{t}</a>
        <span>{date} · {mb} MB</span>
      </div>
    </article>"""


def section(name, files, note=""):
    cards = "".join(card(*f) for f in files)
    note_html = f'<p class="note">{note}</p>' if note else ""
    return f"""
  <section class="group">
    <div class="group-head"><h2 dir="auto">{html.escape(name)}</h2><span class="lb-chip tint">{len(files)}</span></div>
    {note_html}
    <div class="reels">{cards}</div>
  </section>"""


def build():
    total = sum(len(f) for _, f in CREATORS)
    body = "".join(section(n, f) for n, f in CREATORS)
    body += section("גרסאות 9:16 שנערכו מהחומר", RECUTS,
                    f'עריכות מ־10 באוגוסט 2026, תיקייה <a href="{RECUT_FOLDER}" target="_blank" rel="noopener">9x16</a>.')
    page = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>רילס של יוצרים</title>
{design.head()}
<style>
  .intro p {{ color: var(--text-2); margin: 0; }}
  .group {{ display: grid; gap: var(--sp-3); }}
  .group-head {{ display: flex; align-items: center; gap: var(--sp-2); }}
  .group-head h2 {{ margin: 0; }}
  .note {{ margin: 0; color: var(--text-2); }}
  .reels {{ display: grid; gap: var(--sp-4); grid-template-columns: repeat(auto-fill, minmax(min(100%, 15rem), 1fr)); }}
  .reel iframe {{ width: 100%; aspect-ratio: 9 / 16; border: 0; display: block; background: var(--surface-2); }}
  .reel .meta {{ display: grid; gap: 2px; padding: var(--sp-3) var(--sp-4); font-size: var(--fs-callout); }}
  .reel .meta a {{ font-weight: 600; overflow-wrap: anywhere; text-align: start; }}
  .reel .meta span {{ color: var(--text-2); }}
</style>
</head>
<body>
<main class="lb-page">
  <header class="intro">
    <h1>רילס של יוצרים על הספר</h1>
    <p>{total} סרטונים מ־7 יוצרים בתיקייה <a href="{UGC_FOLDER}" target="_blank" rel="noopener">תוכן לקוחות ויוצרים</a>, ועוד {len(RECUTS)} עריכות 9:16. הסרטונים מתנגנים ישר מהדרייב, אז צריך להיות מחובר לחשבון הגוגל שיש לו גישה לתיקייה. חומר גלם של שהם (22 קבצים, כ־2 GB) נשאר <a href="{RAW_SHOAM}" target="_blank" rel="noopener">בתיקייה שלו</a>.</p>
  </header>
{body}
</main>
</body>
</html>
"""
    out = Path(__file__).with_name("creator-reels.html")
    out.write_text(page, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    build()
