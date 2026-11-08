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


if __name__ == "__main__":
    unittest.main()
