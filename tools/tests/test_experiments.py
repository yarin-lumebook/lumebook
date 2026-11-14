"""The MeBook study's content experiment log: the store (tools/experiments.py) and the metric calculations
(research/mebook-customer-research/experiments-metrics.js, run with node).

Run: python3 -m unittest discover -s tools/tests
Everything is written to a temporary folder; the real experiments.json is never touched.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import experiments as ex  # noqa: E402

METRICS_JS = os.path.join(ROOT, "research/mebook-customer-research/experiments-metrics.js")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def doc(**kw):
    d = {"title": "רגע הזיהוי", "hypothesis": "אני מאמין שהורים יקנו אם נראה ילד מזהה את עצמו, כי הם רוצים את הרגע הזה."}
    d.update(kw)
    return d


class Clean(unittest.TestCase):
    def test_only_title_and_hypothesis_are_required(self):
        out = ex.clean(doc(), "abc123")
        self.assertEqual(out["status"], "idea")
        self.assertEqual(out["results"]["purchases"], None)
        with self.assertRaises(ValueError):
            ex.clean(doc(title=" "), "abc123")
        with self.assertRaises(ValueError):
            ex.clean(doc(hypothesis=""), "abc123")

    def test_not_measured_stays_null_and_zero_stays_zero(self):
        out = ex.clean(doc(results={"purchases": 0, "visits": "", "views": None, "revenue": "1,250"}), "abc123")
        self.assertEqual(out["results"]["purchases"], 0)
        self.assertIsNone(out["results"]["visits"])
        self.assertIsNone(out["results"]["views"])
        self.assertEqual(out["results"]["revenue"], 1250)

    def test_bad_numbers_are_refused(self):
        for bad in (-1, "abc", True, float("inf")):
            with self.assertRaises(ValueError):
                ex.clean(doc(results={"purchases": bad}), "abc123")

    def test_completed_needs_conclusion_and_explanation(self):
        with self.assertRaises(ValueError):
            ex.clean(doc(status="completed"), "abc123")
        with self.assertRaises(ValueError):
            ex.clean(doc(status="completed", conclusion="promising"), "abc123")
        out = ex.clean(doc(status="completed", conclusion="promising", explanation="רכישה אחת, צריך לחזור"), "abc123")
        self.assertEqual(out["status"], "completed")

    def test_spend_belongs_to_paid(self):
        with self.assertRaises(ValueError):
            ex.clean(doc(mode="organic", results={"spend": 50}), "abc123")
        self.assertEqual(ex.clean(doc(mode="paid", results={"spend": 50}), "abc123")["results"]["spend"], 50)

    def test_links_dates_and_values(self):
        out = ex.clean(doc(links=["intent:50", "finding:p-recognition", "hyp:H2", "intent:50"]), "abc123")
        self.assertEqual(out["links"], ["intent:50", "finding:p-recognition", "hyp:H2"])
        for bad in (dict(links=["evil:1"]), dict(status="done"), dict(conclusion="won"), dict(start="14/11/2026"),
                    dict(start="2026-11-14", end="2026-11-01"), dict(mode="both")):
            with self.assertRaises(ValueError, msg=str(bad)):
                ex.clean(doc(**bad), "abc123")


class Store(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "experiments.json")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_missing_file_is_an_empty_log(self):
        self.assertEqual(ex.load(self.path), {"experiments": {}})

    def test_save_reload_update_and_follow_up(self):
        code, body = ex.put("first01", doc(links=["intent:50"]), self.path)
        self.assertEqual(code, 200)
        created = body["doc"]["created"]
        code, _ = ex.put("first01", doc(status="completed", conclusion="inconclusive", explanation="מעט נתונים",
                                       results={"purchases": 0}), self.path)
        self.assertEqual(code, 200)
        code, body = ex.put("second2", doc(title="המשך", prev="first01"), self.path)
        self.assertEqual(code, 200)
        data = json.loads(read(self.path))["experiments"]
        self.assertEqual(set(data), {"first01", "second2"})
        self.assertEqual(data["first01"]["created"], created)          # an update keeps the creation time
        self.assertEqual(data["first01"]["results"]["purchases"], 0)   # zero is saved as zero
        self.assertIsNone(data["first01"]["results"]["visits"])        # not measured is saved as null
        self.assertEqual(data["second2"]["prev"], "first01")

    def test_refusals_leave_the_file_alone(self):
        ex.put("keep001", doc(), self.path)
        before = read(self.path)
        self.assertEqual(ex.put("bad id!", doc(), self.path)[0], 400)
        self.assertEqual(ex.put("other01", doc(prev="nosuch1"), self.path)[0], 400)
        self.assertEqual(ex.put("other01", doc(status="completed"), self.path)[0], 400)
        self.assertEqual(read(self.path), before)


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class Metrics(unittest.TestCase):
    def run_js(self, cases):
        script = ("const M=require(%s); const cases=%s; console.log(JSON.stringify(cases.map(c=>"
                  "c.fn==='prompts'?M.prompts(c.r):M.metrics(c.r,c.mode))));") % (json.dumps(METRICS_JS), json.dumps(cases))
        out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout
        return json.loads(out)

    def test_cpa_roas_and_conversion(self):
        r = self.run_js([{"r": {"spend": 100, "purchases": 4, "revenue": 500, "visits": 200}, "mode": "paid"}])[0]
        self.assertEqual(r["cpa"], {"value": 25, "reason": None})
        self.assertEqual(r["roas"], {"value": 5, "reason": None})
        self.assertAlmostEqual(r["conversion"]["value"], 0.02)

    def test_unavailable_is_never_zero(self):
        organic, zero_buy, not_measured, zero_spend, zero_visits = self.run_js([
            {"r": {"spend": None, "purchases": 3, "visits": None}, "mode": "organic"},
            {"r": {"spend": 100, "purchases": 0, "revenue": 0, "visits": 50}, "mode": "paid"},
            {"r": {"spend": 100, "purchases": "", "revenue": None, "visits": 50}, "mode": "paid"},
            {"r": {"spend": 0, "purchases": 2, "revenue": 200}, "mode": "paid"},
            {"r": {"visits": 0, "purchases": 0}, "mode": "organic"},
        ])
        self.assertEqual(organic["cpa"]["reason"], "not_paid")
        self.assertEqual(organic["roas"]["reason"], "not_paid")
        self.assertEqual(organic["conversion"]["reason"], "visits_not_measured")
        self.assertEqual(zero_buy["cpa"], {"value": None, "reason": "zero_purchases"})
        self.assertEqual(zero_buy["roas"], {"value": 0, "reason": None})          # measured zero revenue is a real 0
        self.assertEqual(zero_buy["conversion"], {"value": 0, "reason": None})    # measured zero purchases is a real 0%
        self.assertEqual(not_measured["cpa"]["reason"], "purchases_not_measured")
        self.assertEqual(not_measured["roas"]["reason"], "revenue_not_measured")
        self.assertEqual(not_measured["conversion"]["reason"], "purchases_not_measured")
        self.assertEqual(zero_spend["roas"]["reason"], "zero_spend")
        self.assertEqual(zero_spend["cpa"], {"value": 0, "reason": None})
        self.assertEqual(zero_visits["conversion"]["reason"], "zero_visits")

    def test_prompts_need_their_numbers(self):
        none, reach, all_three = self.run_js([
            {"fn": "prompts", "r": {}},
            {"fn": "prompts", "r": {"impressions": 5000, "visits": 20}},
            {"fn": "prompts", "r": {"views": 900, "visits": 30, "purchases": 1}},
        ])
        self.assertEqual(none, [])
        self.assertEqual(reach, ["reach_vs_visits"])
        self.assertEqual(all_three, ["reach_vs_visits", "visits_vs_purchases", "single_purchase"])


if __name__ == "__main__":
    unittest.main()
