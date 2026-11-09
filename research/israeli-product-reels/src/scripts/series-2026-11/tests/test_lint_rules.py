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


if __name__ == "__main__":
    unittest.main()
