"""Hook Studio, the app (16 Oct 2026): grades, the summary the next batch reads, the producer's free export and recovery, the pages."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import batch  # noqa: E402
import carousel_lib as lib  # noqa: E402
import grade_page  # noqa: E402
import grades  # noqa: E402
import producer  # noqa: E402
import studio  # noqa: E402

FIXTURES = HERE / "fixtures"
DATE = "2026-10-19"
PLAN = {"id": DATE, "kind": "weekly", "made_on": "2026-10-16",
        "slots": [{"n": 1, "date": DATE, "kind": "regular", "topic_id": "pacifier-weaning", "topic_he": "פרידה מהמוצץ",
                   "reco": [{"format": "mixed", "skill": "early_literacy", "skill_he": "אוריינות ראשונית", "event": False},
                            {"format": "mixed2", "skill": "turn_taking", "skill_he": "לחכות לתור", "event": False}]}]}


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="studio-test-"))
        drafts = self.tmp / "drafts"
        folder = drafts / DATE
        folder.mkdir(parents=True)
        pack = lib.read_json(FIXTURES / "valid_pack.json")
        pack["date"] = DATE
        lib.write_json(folder / "pack.json", pack)
        (folder / "review.html").write_text("<html><body></body></html>", encoding="utf-8")
        car = lib.read_json(FIXTURES / "reco" / "reco-carousel.json")
        lib.write_json(folder / "reco-carousel.json", car)
        (folder / "reco").mkdir()
        for i in range(1, len(car["slides"]) + 1):
            (folder / "reco" / f"{i:02d}.png").write_bytes(b"\x89PNG fake")
        lib.write_json(drafts / "batches" / f"{DATE}.json", PLAN)
        self.patches = [
            mock.patch.object(lib, "DRAFTS", drafts),
            mock.patch.object(lib, "APPROVED", self.tmp / "approved"),
            mock.patch.object(batch, "BATCHES", drafts / "batches"),
            mock.patch.object(grades, "GRADES", self.tmp / "grades.json"),
            mock.patch.object(producer, "PRODUCTIONS", self.tmp / "productions.json"),
            mock.patch.object(studio, "grades_unsent", lambda: False),
        ]
        for p in self.patches:
            p.start()
        self.items = grades.items(PLAN)

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def item(self, key):
        return next(i for i in self.items if i["key"] == key)


class Grades(Sandbox):
    def test_items_are_the_six_options_then_the_carousel(self):
        self.assertEqual([i["key"] for i in self.items][:6], [f"{DATE}/{x}" for x in ("kid-1", "kid-2", "kid-3", "expert-1", "expert-2", "expert-3")])
        reco = self.items[6]
        self.assertEqual((reco["key"], reco["kind"], reco["skill_he"]), (f"{DATE}/reco", "reco", "אוריינות ראשונית"))
        self.assertEqual(len(reco["images"]), len(reco["slides"]))
        self.assertEqual(len(self.items), 7)   # the second carousel is not in the folder

    def test_upsert_keeps_a_snapshot_and_fields_left_out(self):
        it = self.item(f"{DATE}/kid-2")
        grades.upsert(it, score=5, why="  פתיח חזק  ")
        entry = grades.upsert(it, produce=True)
        self.assertEqual((entry["score"], entry["why"], entry["produce"]), (5, "פתיח חזק", True))
        self.assertEqual(entry["cover"], it["cover"])
        self.assertEqual(entry["hook_formula"], it["hook_formula"])
        with self.assertRaises(ValueError):
            grades.upsert(it, score=6)

    def test_pick_unsent_sends_each_pick_once(self):
        grades.upsert(self.item(f"{DATE}/kid-1"), produce=True)
        grades.upsert(self.item(f"{DATE}/reco"), produce=True)
        grades.upsert(self.item(f"{DATE}/kid-3"), score=2)
        self.assertEqual(grades.pick_unsent(DATE), [f"{DATE}/kid-1", f"{DATE}/reco"])
        self.assertEqual(grades.pick_unsent(DATE), [])

    def test_brief_lists_reasons_best_first_and_says_it_is_taste(self):
        self.assertIn("No grades yet", grades.brief())
        grades.upsert(self.item(f"{DATE}/kid-1"), score=2, why="ארוך מדי")
        grades.upsert(self.item(f"{DATE}/expert-1"), score=5, why="הצעדים ברורים")
        text = grades.brief()
        self.assertIn("not performance data", text)
        self.assertLess(text.index("הצעדים ברורים"), text.index("ארוך מדי"))
        self.assertIn("Liked (4 to 5)", text)
        self.assertIn("Disliked (1 to 2)", text)
        self.assertNotIn("—", text)


class Producer(Sandbox):
    def test_reco_export_writes_slides_texts_and_zip(self):
        run = producer.export_reco(DATE, "reco")
        final = run / "final"
        names = {p.name for p in final.iterdir()}
        self.assertTrue({"caption.txt", "alt-text.txt", "sources.md", f"{DATE}-reco.zip", "01.png"} <= names)
        import zipfile
        listed = zipfile.ZipFile(final / f"{DATE}-reco.zip").namelist()
        self.assertIn("slides/01.png", listed)
        self.assertIn("caption.txt", listed)

    def test_reco_start_finishes_without_cost(self):
        with mock.patch.object(producer, "_pool") as pool:
            pool.submit.side_effect = lambda fn, *a: fn(*a)
            rec = producer.start(self.item(f"{DATE}/reco"))
        self.assertEqual(rec["status"], "queued")
        done = producer.get(f"{DATE}/reco")
        self.assertEqual((done["status"], done["spent_usd"]), ("done", 0))
        self.assertTrue(done["zip"].endswith(".zip"))

    def test_recover_marks_interrupted_work(self):
        lib.write_json(producer.PRODUCTIONS, {"runs": {"a": {"key": "a", "kind": "reco", "status": "exporting"},
                                                       "b": {"key": "b", "kind": "kid", "status": "done"}}})
        producer.recover()
        runs = producer.load()["runs"]
        self.assertEqual(runs["a"]["status"], "failed")
        self.assertEqual(runs["b"]["status"], "done")

    def test_approve_needs_a_picture_waiting(self):
        with self.assertRaises(ValueError):
            producer.approve(f"{DATE}/kid-1", self.item(f"{DATE}/kid-1"))

    def test_spend_counts_only_billed_calls(self):
        gen = self.tmp / "run" / "generated-assets"
        gen.mkdir(parents=True)
        (gen / "generation-log.jsonl").write_text(
            json.dumps({"estimated_cost_usd": 0.055}) + "\n" + json.dumps({"estimated_cost_usd": 0.055, "billed": False}) + "\n", encoding="utf-8")
        self.assertEqual(producer.spent(self.tmp / "run"), 0.055)


class Pages(Sandbox):
    def test_every_page_is_hebrew_rtl_without_em_dashes(self):
        pages = {"home": studio.home_page(), "packs": studio.packs_page(), "productions": studio.productions_page(),
                 "grade": grade_page.page(PLAN), "pool": batch.pool_page(DATE)}
        for name, html in pages.items():
            self.assertIn('dir="rtl"', html, name)
            self.assertIn("Hook Studio", html, name)
            self.assertNotIn("—", html, name)
            self.assertIn('aria-current="page"', html, name)

    def test_grade_page_carries_the_batch_data(self):
        html = grade_page.page(PLAN)
        blob = html.split('<script type="application/json" id="gv-data">')[1].split("</script>")[0]
        data = json.loads(blob)
        self.assertEqual(data["batch"], DATE)
        self.assertEqual(len(data["items"]), 7)

    def test_next_cloud_run_is_a_thursday_evening_utc(self):
        import datetime as dt
        at = studio.next_cloud_run(dt.datetime(2026, 10, 16, 8, 0, tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)
        self.assertEqual((at.weekday(), at.hour, at.day), (3, 19, 22))


if __name__ == "__main__":
    unittest.main()
