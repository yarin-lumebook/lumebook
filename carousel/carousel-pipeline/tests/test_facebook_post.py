"""The Facebook post, the disclaimers and the 3D booklet (Yarin, 31 Oct 2026): Facebook gets its own converting text that
ends with the site link over slide 1 with its text; every slide from slide 2 carries the medical disclaimer and every
written caption ends with the short one; the booklet under the book link CTA is drawn in 3D."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import carousel_lib as lib  # noqa: E402
import compose_slides  # noqa: E402
import postiz_export  # noqa: E402

LINK = lib.fb_link()
GOOD = ("״אמא, עוד כמה ימים?״ בפעם העשירית היום 🎂\n\n"
        "השבוע שלפני יום ההולדת עובר להם לאט לאט.\n"
        "הם לא מנסים לשגע, פשוט קשה להם לראות את הזמן.\n\n"
        "כמה דברים שעוזרים לראות אותו:\n"
        "• לוח על המקרר, ואיקס אחד כל בוקר\n"
        "• שרשרת נייר, וכל יום מורידים טבעת\n"
        "• לספר מה בדיוק יהיה ביום עצמו\n\n"
        "ואפשר גם לעזור להם עם ההמתנה ליום ההולדת\n"
        "בעזרת ספר מותאם אישית, שבו הם הגיבורים.\n"
        "עם השם שלהם, ודמות שנראית כמוהם.\n"
        "התצוגה המקדימה בחינם, ומשלמים רק אם אהבת.\n\n"
        "להכנת הספר 👇\n" + LINK)


def errors(text):
    return [i.message for i in lib.fb_post_issues("fb", text) if i.level == "ERROR"]


class FacebookPostRules(unittest.TestCase):
    def test_link_is_the_utm_site_link(self):
        self.assertEqual(LINK, "https://lumebook.com/IL/he?utm_source=facebook&utm_medium=social")

    def test_good_post_passes_with_or_without_the_disclaimer(self):
        self.assertEqual(errors(GOOD), [])
        self.assertEqual(errors(lib.with_disclaimer(GOOD)), [])

    def test_link_must_close_the_post_alone(self):
        self.assertTrue(any("last line is the link" in e for e in errors(GOOD.rsplit("\n", 1)[0])))
        moved = GOOD.replace("להכנת הספר 👇", "להכנת הספר 👇 " + LINK)
        self.assertTrue(any("once, alone" in e for e in errors(moved)))

    def test_no_comment_word_cta(self):
        text = GOOD.replace("להכנת הספר 👇", 'תכתבי "עוגה" ואשלח לך קישור 👇')
        self.assertTrue(any("comment word" in e for e in errors(text)))

    def test_two_emojis_hook_and_cta(self):
        self.assertTrue(any("two emojis" in e for e in errors(GOOD.replace("לוח על המקרר", "לוח 🗓 על המקרר"))))
        self.assertTrue(any("hook" in e for e in errors(GOOD.replace(" 🎂", ""))))

    def test_audience_rules_apply(self):
        self.assertTrue(any("forbidden" in e for e in errors(GOOD.replace("לאט לאט.", "לאט; לאט."))))
        self.assertTrue(any("AI" in e for e in errors(GOOD.replace("ודמות שנראית כמוהם.", "ודמות AI שנראית כמוהם."))))

    def test_length(self):
        short = "״אמא, עוד כמה ימים?״ 🎂\nספר שבו הם הגיבורים.\nלהכנת הספר 👇\n" + LINK
        self.assertTrue(any("words" in e for e in errors(short)))


class Disclaimers(unittest.TestCase):
    def test_caption_disclaimer_once(self):
        once = lib.with_disclaimer("שורה")
        self.assertEqual(once, "שורה\n\n" + lib.CAPTION_DISCLAIMER)
        self.assertEqual(lib.with_disclaimer(once), once)
        self.assertEqual(lib.strip_disclaimer(once), "שורה")

    def test_disclaimers_keep_the_punctuation_rule(self):
        for text in (lib.SLIDE_DISCLAIMER, lib.CAPTION_DISCLAIMER):
            self.assertEqual(lib.forbidden_char_issues("d", text), [])

    def test_slide_disclaimer_from_the_second_slide(self):
        v = {"structure": "one_day", "slides": []}
        for n in (1, 2, 5, 9):
            html = compose_slides.story_slide_html(v, {"number": n, "headline": "שורה", "body": "גוף"}, "pic.png", 9)
            self.assertEqual(compose_slides.esc(lib.SLIDE_DISCLAIMER) in html, n > 1, n)


class PostizTexts(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fb-post-"))
        self.run = self.tmp / "2026-11-30-kid-1"
        (self.run / "final").mkdir(parents=True)
        option = {"id": "kid-1", "cta": "תשמרי את הפוסט", "caption": "אמא, שורה ראשונה.\nתשמרי את הפוסט",
                  "slides": [{"number": 1, "headline": "שער", "body": ""}, {"number": 2, "headline": "שקופית", "body": "גוף"}]}
        lib.write_json(self.run / "approved.json", {"date": "2026-11-30", "option": option})
        (self.run / "final" / "caption.txt").write_text(lib.with_disclaimer(option["caption"]) + "\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_both_texts_end_with_the_disclaimer_once(self):
        out = postiz_export.texts(self.run)
        for key in ("caption", "fb_text"):
            self.assertTrue(out[key].endswith(lib.CAPTION_DISCLAIMER), key)
            self.assertEqual(out[key].count(lib.CAPTION_DISCLAIMER), 1, key)

    def test_own_facebook_text_over_slide_1(self):
        txt = lib.fb_post_path(self.run)
        txt.parent.mkdir()
        txt.write_text(GOOD + "\n", encoding="utf-8")
        self.assertEqual(postiz_export.texts(self.run)["fb_text"], lib.with_disclaimer(GOOD))
        body = postiz_export.payload(self.run, ["s1.png", "s2.png"])
        fb = next(p for p in body["posts"] if p["integration"]["id"] == postiz_export.config()["facebook"])
        self.assertEqual(fb["value"][0]["image"], [{"id": "s01", "path": "s1.png"}])   # slide 1 with its text
        self.assertTrue(fb["value"][0]["content"].startswith("״אמא, עוד כמה ימים?״"))

    def test_changed_slides_get_a_new_stamp(self):
        a, b = self.tmp / "a.png", self.tmp / "b.png"
        a.write_bytes(b"one")
        b.write_bytes(b"two")
        first = postiz_export.stamp([a, b])
        b.write_bytes(b"three")
        self.assertNotEqual(first, postiz_export.stamp([a, b]))


class Booklet3D(unittest.TestCase):
    BOOKLET = {"page_text": ["שורה אחת,", "ועוד שורה."], "crop": [134, 192, 950, 516], "face": [0.228, 0.455]}

    def test_homography_maps_the_corners(self):
        src = [(0, 0), (100, 0), (100, 50), (0, 50)]
        dst = [(10, 20), (120, 25), (115, 90), (5, 80)]
        hm = compose_slides.homography(src, dst)
        for s, d in zip(src, dst):
            x, y = compose_slides.hpoint(hm, *s)
            self.assertAlmostEqual(x, d[0], places=6)
            self.assertAlmostEqual(y, d[1], places=6)
        self.assertTrue(compose_slides.matrix3d(hm, 3, 4).startswith("matrix3d("))

    def test_pages_bend_into_the_fold_and_the_far_edge_is_narrower(self):
        geo = compose_slides.booklet_geometry(self.BOOKLET)
        far, near = geo["outline"]["far"], geo["outline"]["near"]
        self.assertGreater(far[len(far) // 2][1], far[0][1])         # the fold sits lower than the outer corner
        self.assertGreater(far[0][0], near[-1][0])                    # the far left corner is further in than the near one
        self.assertEqual(len(geo["pages"][-1]), len(compose_slides.BOOK_STRIPS) - 1)

    def test_arrow_tip_sits_under_the_face_on_the_picture_page(self):
        tip, tail = compose_slides.booklet_face_tip(self.BOOKLET)
        self.assertTrue(65 < tip[0] < 540 and 620 < tip[1] < 1200, tip)
        self.assertGreater(tail[1], tip[1])

    def test_html_has_the_page_text_and_unique_ids(self):
        tmp = Path(tempfile.mkdtemp(prefix="bk3-"))
        try:
            png = tmp / "booklet.png"
            png.write_bytes(bytes.fromhex("89504e470d0a1a0a0000000d49484452") + (1376).to_bytes(4, "big") + (768).to_bytes(4, "big") + b"\x08\x06\x00\x00\x00")
            html = compose_slides.booklet_html(self.BOOKLET, {"booklet": "b.png", "kid": "k.png", "booklet_path": png}, uid="__UID__")
            self.assertIn("<span>שורה אחת,</span>", html)
            self.assertIn('id="ah__UID__"', html)
            self.assertEqual(html.count('class="bk3-strip"'), 2 * (len(compose_slides.BOOK_STRIPS) - 1))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
