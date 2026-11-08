"""To-dos in .lumebook/state.json: a republish must not hide a broken build (audit of 08 Nov 2026).

Run: python3 -m unittest discover -s tools/tests
Pure functions on an in-memory state: nothing is read from or written to .lumebook/.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lumebook as lb  # noqa: E402


def state():
    return {"components": {}, "pending": [
        {"component": "strategy", "action": lb.BUILD_FIX + "python3 src/build_strategy_page.py", "reasons": ["boom"], "since": "x"},
        {"component": "strategy", "action": "review: hooks", "reasons": ["upstream"], "since": "x"},
        {"component": "dashboard", "action": lb.BUILD_FIX + "python3 build_site.py", "reasons": ["boom"], "since": "x"}]}


class Pending(unittest.TestCase):
    def test_ack_published_keeps_a_failed_build(self):
        st = state()
        cleared, kept = lb.ack_pending(st, "strategy", keep_build_fixes=True)
        self.assertEqual(cleared, 1)
        self.assertEqual([it["action"] for it in kept], [lb.BUILD_FIX + "python3 src/build_strategy_page.py"])
        self.assertEqual(len(st["pending"]), 2)

    def test_plain_ack_still_clears_everything_of_that_component(self):
        st = state()
        cleared, kept = lb.ack_pending(st, "strategy", keep_build_fixes=False)
        self.assertEqual((cleared, kept), (2, []))
        self.assertEqual([it["component"] for it in st["pending"]], ["dashboard"])

    def test_a_good_build_clears_only_its_own_build_fix(self):
        st = state()
        lb.clear_build_fix(st, "strategy")
        self.assertEqual([(it["component"], it["action"][:10]) for it in st["pending"]],
                         [("strategy", "review: ho"), ("dashboard", lb.BUILD_FIX[:10])])


class Times(unittest.TestCase):
    def test_summer_and_winter_offsets_compare_as_times(self):
        # 23:30 winter time is 21:30 UTC, after 23:45 summer time (20:45 UTC); as text it looked earlier
        self.assertTrue(lb.later("2026-11-08T23:30:00+02:00", "2026-11-08T23:45:00+03:00"))
        self.assertFalse(lb.later("2026-11-08T22:30:00+02:00", "2026-11-08T23:45:00+03:00"))

    def test_israel_offset_follows_the_season(self):
        from datetime import datetime
        self.assertEqual(datetime(2026, 7, 1, 12, tzinfo=lb.IL).utcoffset().total_seconds(), 3 * 3600)
        self.assertEqual(datetime(2026, 11, 8, 12, tzinfo=lb.IL).utcoffset().total_seconds(), 2 * 3600)


if __name__ == "__main__":
    unittest.main()
