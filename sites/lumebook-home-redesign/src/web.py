#!/usr/bin/env python3
"""Copies the built demo into web/ for Vercel (Yarin, 17 / 11 / 2026: "deploy it so i can view it on my phone").

Run after `python3 tools/lumebook.py build home-redesign` (so the edit-button changes are baked into the pages),
then `python3 tools/lumebook.py deploy home-redesign`. Files the pages borrow from elsewhere in the repo
(the Partners open-book picture, the identity favicons) are copied into web/img and the links rewritten.
"""
import pathlib
import shutil

SITE = pathlib.Path(__file__).resolve().parent.parent
ROOT = SITE.parent.parent
WEB = SITE / "web"
BORROWED = {
    "../lumebook-partners/img/book-open.webp": ("sites/lumebook-partners/img/book-open.webp", "img/book-open.webp"),
    "../../shared/brand/identity-v1/web/favicon.svg": ("shared/brand/identity-v1/web/favicon.svg", "img/favicon.svg"),
    "../../shared/brand/identity-v1/web/favicon-32.png": ("shared/brand/identity-v1/web/favicon-32.png", "img/favicon-32.png"),
    "../../shared/brand/identity-v1/web/favicon-180.png": ("shared/brand/identity-v1/web/favicon-180.png", "img/favicon-180.png"),
}


def main():
    WEB.mkdir(exist_ok=True)
    for d in ("assets", "img"):
        if (WEB / d).exists():
            shutil.rmtree(WEB / d)
        shutil.copytree(SITE / d, WEB / d)
    for src, dst in BORROWED.values():
        shutil.copy2(ROOT / src, WEB / dst)
    for page in ("index.html", "kids.html", "gift-books.html", "albums.html", "compare.html"):
        html = (SITE / page).read_text(encoding="utf-8")
        for old, (_, new) in BORROWED.items():
            html = html.replace(old, new)
        assert "../" not in html.replace("</", ""), f"{page} still links outside the site"
        (WEB / page).write_text(html, encoding="utf-8")
    (WEB / ".vercelignore").write_text(".env*\n", encoding="utf-8")
    (WEB / ".gitignore").write_text(".vercel\n.env*\n", encoding="utf-8")
    print("web/ ready:", sum(1 for _ in WEB.rglob("*") if _.is_file()), "files")


if __name__ == "__main__":
    main()
