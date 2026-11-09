"""The static (Vercel) copy of HQ must never carry the store's ambassadors person by person (audit of 08 Nov 2026),
nor the creator outreach work: who is tracked, follow-up and reminder lists, stages, outreach counts (09 Nov 2026).

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


def creators():
    return {"total": 437, "shortlist": 15, "by_pass": {"1": 61}, "archetypes": [["אמא לתאומים", 40]], "bands": [["5-10K", 50]],
            "checked_on": "2026-11-08", "modified": "2026-11-08T21:00", "with_direct_contact_hint": 2,
            "competitor_conflicts": ["@noa.conflict"],
            "tracked": [{"handle": "noa.creator", "name": "Noa Creator", "url": "https://www.instagram.com/noa.creator/",
                         "contact": "IG DM · linktr.ee/noa.creator", "group": "barter", "live_error": False}]}


def home_creators():
    return {"total": 437, "contacted": 437, "sent": 180, "declined": 148, "process": 11, "reply_rate": 3, "books_out": 8,
            "followups_due": 140, "reminders_due": 2, "post_views": 7337, "posts": 3,
            "followups_who": ["Noa Creator"], "reminders_who": ["Tal Reminder"]}


class PublicSnapshot(unittest.TestCase):
    def snap(self):
        return {"date": "2026-11-08", "signups": section(), "creators": creators(),
                "home": {"ambassadors": section(), "creators": home_creators(), "attention": [
                    {"sev": "crit", "tag": "שגרירים", "text": "בקשת מימוש פתוחה של Dana Example, לטפל עד 10/11/2026", "view": "signups"},
                    {"sev": "info", "tag": "שגרירים", "text": "1 שגרירים חדשים השבוע", "view": "signups"},
                    {"sev": "warn", "tag": "יוצרים", "text": "19 תזכורות ליוצרים הגיעו לזמנן"}]}}

    def test_no_person_reaches_the_static_copy(self):
        out = json.dumps(build_site.public_snapshot(self.snap()), ensure_ascii=False)
        for private in ("Dana Example", "dana.example", "dana-x1", "noa.creator", "Noa Creator", "noa.conflict", "Tal Reminder", "linktr.ee"):
            self.assertNotIn(private, out)

    def test_no_creator_outreach_count_reaches_the_static_copy(self):
        pub = build_site.public_snapshot(self.snap())
        self.assertEqual(pub["home"]["creators"], {"total": 437, "redacted": True})
        self.assertEqual((pub["creators"]["tracked"], pub["creators"]["competitor_conflicts"]), ([], []))
        self.assertNotIn("with_direct_contact_hint", pub["creators"])
        self.assertFalse(any(a["tag"] == "יוצרים" for a in pub["home"]["attention"]))

    def test_the_creator_map_research_totals_stay(self):
        c = build_site.public_snapshot(self.snap())["creators"]
        self.assertEqual((c["total"], c["shortlist"], c["bands"], c["archetypes"]), (437, 15, [["5-10K", 50]], [["אמא לתאומים", 40]]))
        self.assertTrue(c["redacted"])

    def test_the_tracker_loses_its_creator_stages_and_outreach_count(self):
        pub = build_site.public_tracker({"tasks": {"t1": True}, "creators": {"noa.creator": 3}, "counts": {"outreach": 5, "other": 1}})
        self.assertEqual(pub, {"tasks": {"t1": True}, "creators": {}, "counts": {"other": 1}})
        self.assertEqual(build_site.public_tracker({}), {"creators": {}, "counts": {}})

    def test_counts_and_totals_stay(self):
        pub = build_site.public_snapshot(self.snap())
        for sec in (pub["signups"], pub["home"]["ambassadors"]):
            self.assertEqual((sec["total"], sec["books"], sec["rewards_final"]), (2, 3, 40.0))
            self.assertEqual(sec["payouts_open_count"], 1)
            self.assertTrue(sec["redacted"])
            self.assertNotIn("rows", sec)
            self.assertNotIn("payouts_open", sec)

    def test_attention_keeps_the_ambassador_item_without_the_name(self):
        att = build_site.public_snapshot(self.snap())["home"]["attention"]
        self.assertEqual([a["text"] for a in att], ["בקשת מימוש פתוחה של שגריר", "1 שגרירים חדשים השבוע"])

    def test_the_local_snapshot_is_not_changed(self):
        snap = self.snap()
        build_site.public_snapshot(snap)
        self.assertEqual(len(snap["signups"]["rows"]), 1)
        self.assertEqual(len(snap["home"]["ambassadors"]["payouts_open"]), 1)
        self.assertEqual(len(snap["creators"]["tracked"]), 1)
        self.assertEqual(snap["home"]["creators"]["followups_due"], 140)
        self.assertEqual(len(snap["home"]["attention"]), 3)

    def test_missing_sections_are_fine(self):
        self.assertEqual(build_site.public_snapshot({"date": "x"}), {"date": "x"})
        self.assertIsNone(build_site.public_snapshot({"signups": None})["signups"])
        self.assertIsNone(build_site.public_snapshot({"creators": None, "home": {"creators": None}})["creators"])


class PublicWords(unittest.TestCase):
    """The words block baked into the page never names anyone in the static copy, whatever the dictionary holds."""

    def page(self, en):
        payload = {"page": "sites/dashboard/lumebook-dashboard.html", "rev": "1", "common": {"en": {"שמירה": "Save"}, "he": {}},
                   "dict": {"en": en, "he": {"IG DM · linktr.ee/noa.creator": "IG DM · linktr.ee/noa.creator"}}}
        return ('<html><body><div class="lb-app">x</div><script type="application/json" id="lumebook-i18n">'
                + json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c") + "</script></body></html>")

    def snap(self):
        return {"creators": creators(), "signups": section(), "home": {"creators": home_creators(), "ambassadors": section()}}

    def test_who_is_private(self):
        private = build_site.private_strings(self.snap())
        for s in ("noa.creator", "noa creator", "noa.conflict", "tal reminder", "dana example", "dana.example", "dana-x{0}", "linktr.ee/noa.creator"):
            self.assertIn(s, private)

    def test_entries_naming_someone_are_dropped_and_the_rest_stay(self):
        en = {"@noa.creator\u001fNoa Creator": "@noa.creator\u001fNoa Creator", "בקשת מימוש פתוחה של Dana Example": "Open payout request from Dana Example",
              "מפת היוצרים": "Creator map", "קישור dana-x{0}": "Link dana-x{0}"}
        out = build_site.public_words(self.page(en), build_site.private_strings(self.snap()))
        data = json.loads(out.split('id="lumebook-i18n">', 1)[1].split("</script>", 1)[0])
        self.assertEqual(data["dict"]["en"], {"מפת היוצרים": "Creator map"})
        self.assertEqual(data["dict"]["he"], {})
        self.assertEqual(data["common"]["en"], {"שמירה": "Save"})
        self.assertTrue(out.startswith('<html><body><div class="lb-app">x</div>'))

    def test_a_page_without_words_is_unchanged(self):
        self.assertEqual(build_site.public_words("<html></html>", {"noa"}), "<html></html>")
        self.assertEqual(build_site.public_words(self.page({}), set()), self.page({}))


if __name__ == "__main__":
    unittest.main()
