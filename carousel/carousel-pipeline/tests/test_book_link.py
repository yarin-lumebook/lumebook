"""The book link CTA over the booklet (Yarin, 30 Oct 2026): a personalised book for the problem, one comment word, the
link in the DM; the open booklet with the child's photo under it (story-format.md section 7)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import carousel_lib as lib  # noqa: E402

PARENTS = lib.book_link_cta("הגמילה מהמוצץ", "מוצץ", "parents")
MOM = lib.book_link_cta("הקנאה באח החדש", "אח", "mom")


def errors(cta, addressee, code_word):
    return [i.message for i in lib.book_link_cta_issues("cta", cta, addressee, code_word=code_word) if i.level == "ERROR"]


class BookLinkTests(unittest.TestCase):
    def test_wording(self):
        self.assertEqual(PARENTS, 'אפשר גם לעזור להם עם הגמילה מהמוצץ בעזרת ספר מותאם אישית.\nתכתבו "מוצץ" ואשלח לכם קישור להכנת הספר')
        self.assertIn('תכתבי "אח" ואשלח לך', MOM)

    def test_valid_forms(self):
        self.assertEqual(errors(PARENTS, "parents", "מוצץ"), [])
        self.assertEqual(errors(MOM, "mom", "אח"), [])

    def test_slide_keeps_the_exact_cta(self):
        head, body = lib.book_link_slide(PARENTS)
        self.assertEqual(head, "אפשר גם לעזור להם\nעם הגמילה מהמוצץ\nבעזרת ספר מותאם אישית.")
        self.assertEqual(body, 'תכתבו "מוצץ"\nואשלח לכם קישור להכנת הספר')
        self.assertEqual(lib.collapse(head + "\n" + body), lib.collapse(PARENTS))
        self.assertEqual(lib.book_link_keyword(PARENTS), "מוצץ")

    def test_wrong_addressee_word_or_shape(self):
        self.assertTrue(errors(PARENTS, "mom", "מוצץ"))
        self.assertTrue(errors(PARENTS, "parents", "חדר"))
        self.assertTrue(errors("תשמרי את הפוסט לפעם הבאה שהיא מפחדת", "mom", ""))
        self.assertTrue(errors(lib.book_link_cta("הפחד הגדול מרעמים בלילה", "פחד", "mom"), "mom", "פחד"))
        self.assertTrue(errors(lib.book_link_cta("הגמילה", "ספר", "mom"), "mom", "ספר"))

    def test_applies_per_option(self):
        self.assertTrue(lib.book_link_applies({"cta_style": "book_link"}))
        self.assertTrue(lib.book_link_applies({"cta_style": "save_for_later"}, {"cta_style": "book_link"}))
        self.assertFalse(lib.book_link_applies({"cta_style": "save_for_later"}, {}))
        self.assertFalse(lib.save_later_applies({"cta_style": "book_link", "generated_at": "2026-11-01T00:00"}))
        self.assertFalse(lib.save_share_applies({"cta_style": "book_link", "generated_at": "2026-11-01T00:00"}))

    def test_caption_tail_early_lines_and_emoji(self):
        self.assertEqual(lib.cta_tail_lines({"cta": PARENTS}), 2)
        self.assertEqual(lib.cta_tail_lines({"cta": "תשמרי את הפוסט לפעם הבאה שהיא בוכה"}), 1)
        self.assertTrue(lib.book_link_early_issues("s", 'תכתבו "מוצץ" ואשלח לכם קישור'))
        self.assertFalse(lib.book_link_early_issues("s", "אני מפחד מרעמים, תחזיקו אותי"))
        self.assertEqual(lib.post_cta_emoji({"cta": PARENTS}), "📖")
        self.assertEqual(lib.post_cta_emoji({"cta": "תשמרי את הפוסט לפעם הבאה שהיא בוכה"}), "🔖")

    def test_booklet(self):
        ok = {"page_text": ["רוני נפרדה מהמוצץ,", "והארנב נשאר איתה", "כל הלילה."], "crop": [134, 192, 950, 516], "face": [0.228, 0.455]}
        self.assertEqual([i for i in lib.booklet_issues("b", ok) if i.level == "ERROR"], [])
        self.assertTrue(lib.booklet_issues("b", {**ok, "face": [1.4, 0.4]}))
        self.assertTrue(lib.booklet_issues("b", {**ok, "page_text": ["שורה ארוכה מדי בשביל עמוד אחד בחוברת"]}))
        self.assertEqual([i for i in lib.booklet_issues("b", {**ok, "face": [0.2, 0.5, 0.5]}) if i.level == "ERROR"], [])


class AppEditTests(unittest.TestCase):
    """Carousel Machine edits of a book link option (review_server.apply_edits): the text inside the book, and the CTA."""

    def option(self):
        import json
        pack = json.loads((Path(__file__).resolve().parents[1] / "drafts" / "2026-12-06" / "pack.json").read_text(encoding="utf-8"))
        v = next(x for d in pack["directions"] for x in d["versions"] if x["id"] == "kid-1")
        return pack, v

    def test_booklet_page(self):
        import review_server
        pack, v = self.option()
        if not v.get("booklet"):
            self.skipTest("2026-12-06 kid-1 has no booklet in this checkout")
        ch = review_server.apply_edits(pack, [{"option": "kid-1", "field": "booklet_page", "value": "שורה אחת\n\nשורה שתיים "}])
        self.assertEqual(v["booklet"]["page_text"], ["שורה אחת", "שורה שתיים"])
        self.assertEqual(ch[0]["field"], "booklet_page")

    def test_cta_edit_rebuilds_slide_and_caption(self):
        import review_server
        pack, v = self.option()
        if not lib.book_link_applies(pack, v):
            self.skipTest("2026-12-06 kid-1 is not a book link option in this checkout")
        new = 'אפשר גם לעזור להם עם הפרידה מהמוצץ בעזרת ספר מותאם אישית. תכתבו "מוצץ" ואשלח לכם קישור להכנת הספר'
        review_server.apply_edits(pack, [{"option": "kid-1", "field": "cta", "value": new}])
        self.assertEqual(v["slides"][-1]["headline"], "אפשר גם לעזור להם\nעם הפרידה מהמוצץ\nבעזרת ספר מותאם אישית.")
        self.assertEqual(lib.lines_of(v["caption"])[-2:], lib.lines_of(v["cta"]))
        self.assertEqual(v["code_word"], "מוצץ")


if __name__ == "__main__":
    unittest.main()
