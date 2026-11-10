"""Reel copy rules (Yarin, 05 Nov 2026): never the price, and no false alarms on ordinary words (audit of 08 Nov 2026).

Run: python3 -m unittest discover -s research/israeli-product-reels/src/scripts/series-2026-11/tests
Checks the patterns only; nothing is read from or written to reels.json or lint.json.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reels  # noqa: E402


class PriceRule(unittest.TestCase):
    def test_price_talk_fails(self):
        for text in ["הספר עולה 99", "רק 149 ₪", "במקום 199", "₪20 משלוח", "120 ש\"ח", "120 ש״ח", "יש מבצע היום",
                     "הנחה לחנוכה", "משלוח חינם עד הבית", "בלי דמי משלוח", "העלות של הספר", "בזול", "בחצי מחיר", "כמה זה עולה"]:
            self.assertIsNotNone(reels.price_hit(text), text)

    def test_ordinary_words_pass(self):
        for text in ["הספר יצא מעולה", "אין קריאה לפעולה רפואית", "רק צריך להעלות תמונה", "הילדים היו מעולים",
                     "תוצאות מעולות", "משלוח עד הבית"]:
            self.assertIsNone(reels.price_hit(text), text)


def _reel(**kw):
    r = {"id": "9.9", "status": "needs-voice", "series": 1, "date": None, "voice": "yarin", "hook": "שאלה קצרה",
         "caption": "#a", "vo": ["שאלה קצרה פה", "שורה שתיים", "שורה שלוש"],
         "sees": ["אתה למצלמה, ומהפריים הראשון כריכת יום הולדת עם השם לידך", "עמוד מהתצוגה המקדימה", "עמוד הסיום עם הפנים שלו"],
         "shot": "", "payoff": "עמוד הסיום עם הפנים שלו"}
    r.update(kw)
    return {"defaults": {"length": {"card_seconds": 2.2}}, "reels": [r]}


class StudyRules(unittest.TestCase):
    """The @matan.nistor study's warnings (09 Nov 2026): M1 first frame, M2 face mid-reel, M3 ending, M4 payoff."""

    def codes(self, **kw):
        return {w.split()[1] for w in reels.principle_checks(_reel(**kw))}

    def test_a_good_reel_has_none(self):
        self.assertFalse({"M1", "M2", "M3", "M4"} & self.codes())

    def test_each_rule_fires(self):
        self.assertIn("M4", self.codes(payoff=""))
        self.assertIn("M1", self.codes(shot="קטע פתיחה עם ספר מודפס ביד (כל ספר שיש לך)", sees=["אתה למצלמה עם ספר מודפס ביד", "עמוד", "עמוד הסיום"]))
        self.assertIn("M2", self.codes(sees=["כריכת יום הולדת", "אתה למצלמה", "עמוד הסיום"]))
        self.assertIn("M3", self.codes(sees=["כריכת יום הולדת", "עמוד", "אתה למצלמה, מחייך"]))

    def test_yarin_with_the_book_is_not_a_talking_head(self):
        self.assertNotIn("M3", self.codes(sees=["כריכת יום הולדת", "עמוד", "אתה מחזיק את הספר המודפס"]))


class TwoOptions(unittest.TestCase):
    """Two options a day (Yarin, 10 Nov 2026): one reel or options 1 and 2, one lane per day, picks name a reel of the day."""
    DAY = "2026-11-12"

    def d(self, *rs, picks=None):
        return {"reels": [dict(id=i, date=self.DAY, series=s, status="needs-voice", option=o) for i, s, o in rs], "picks": picks or {}}

    def test_a_pair_in_one_lane_passes(self):
        self.assertEqual(reels.option_errors(self.d(("3.1", 3, 1), ("3.2", 3, 2), picks={self.DAY: "3.2", "_about": "x"})), [])

    def test_mixed_lanes_fail(self):
        self.assertTrue(any("lanes" in e for e in reels.option_errors(self.d(("3.1", 3, 1), ("9.9", 9, 2)))))

    def test_three_or_unnumbered_fail(self):
        self.assertTrue(reels.option_errors(self.d(("3.1", 3, 1), ("3.2", 3, 2), ("3.3", 3, 2))))
        self.assertTrue(reels.option_errors(self.d(("3.1", 3, 1), ("3.2", 3, None))))

    def test_pick_of_another_day_fails(self):
        self.assertTrue(any("picks" in e for e in reels.option_errors(self.d(("3.1", 3, 1), ("3.2", 3, 2), picks={self.DAY: "7.1"}))))

    def test_the_day_reel(self):
        d = self.d(("3.1", 3, 1), ("3.2", 3, 2))
        rs = reels.options(d)[self.DAY]
        self.assertEqual(reels.day_reel(d, rs)["id"], "3.1")
        d["picks"][self.DAY] = "3.2"
        self.assertEqual(reels.day_reel(d, rs)["id"], "3.2")
        rs[0]["status"] = "posted"
        self.assertEqual(reels.day_reel(d, rs)["id"], "3.1")


if __name__ == "__main__":
    unittest.main()
