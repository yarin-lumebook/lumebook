"""The static (Vercel) copy of HQ must never carry the store's ambassadors person by person (audit of 08 Nov 2026).

Run: python3 -m unittest discover -s sites/dashboard/tests
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_site  # noqa: E402


def section():
    return {"total": 2, "tests": 1, "active": 1, "books": 3, "new_week": 1, "rewards_final": 40.0,
            "rows": [{"name": "Dana Example", "handle": "dana.example", "slug": "dana-x1", "joined": "2026-11-01"}],
            "payouts_open": [{"who": "Dana Example", "amount": 40.0, "due": "10/11/2026", "state": "חדש"}]}


class PublicSnapshot(unittest.TestCase):
    def snap(self):
        return {"date": "2026-11-08", "signups": section(),
                "home": {"ambassadors": section(), "attention": [
                    {"sev": "crit", "tag": "שגרירים", "text": "בקשת מימוש פתוחה של Dana Example, לטפל עד 10/11/2026", "view": "signups"},
                    {"sev": "info", "tag": "שגרירים", "text": "1 שגרירים חדשים השבוע", "view": "signups"},
                    {"sev": "warn", "tag": "יוצרים", "text": "19 תזכורות ליוצרים הגיעו לזמנן"}]}}

    def test_no_person_reaches_the_static_copy(self):
        out = json.dumps(build_site.public_snapshot(self.snap()), ensure_ascii=False)
        for private in ("Dana Example", "dana.example", "dana-x1"):
            self.assertNotIn(private, out)

    def test_counts_and_totals_stay(self):
        pub = build_site.public_snapshot(self.snap())
        for sec in (pub["signups"], pub["home"]["ambassadors"]):
            self.assertEqual((sec["total"], sec["books"], sec["rewards_final"]), (2, 3, 40.0))
            self.assertEqual(sec["payouts_open_count"], 1)
            self.assertTrue(sec["redacted"])
            self.assertNotIn("rows", sec)
            self.assertNotIn("payouts_open", sec)

    def test_attention_keeps_the_item_without_the_name(self):
        att = build_site.public_snapshot(self.snap())["home"]["attention"]
        self.assertEqual(len(att), 3)
        self.assertEqual(att[0]["text"], "בקשת מימוש פתוחה של שגריר")
        self.assertEqual(att[1]["text"], "1 שגרירים חדשים השבוע")
        self.assertEqual(att[2]["text"], "19 תזכורות ליוצרים הגיעו לזמנן")

    def test_the_local_snapshot_is_not_changed(self):
        snap = self.snap()
        build_site.public_snapshot(snap)
        self.assertEqual(len(snap["signups"]["rows"]), 1)
        self.assertEqual(len(snap["home"]["ambassadors"]["payouts_open"]), 1)

    def test_missing_sections_are_fine(self):
        self.assertEqual(build_site.public_snapshot({"date": "x"}), {"date": "x"})
        self.assertIsNone(build_site.public_snapshot({"signups": None})["signups"])


if __name__ == "__main__":
    unittest.main()
