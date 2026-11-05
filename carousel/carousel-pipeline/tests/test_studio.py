"""Carousel Machine (16 and 17 Oct 2026): grades, the summary the next batch reads, the producer's free export and recovery, the one page."""

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
            mock.patch.object(grades.rl, "ACTIVE", True),  # the batch fixture has its carousels; the switch-off test is below
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


class CarouselsOff(Sandbox):
    def test_games_and_books_are_hidden_when_switched_off(self):
        with mock.patch.object(grades.rl, "ACTIVE", False):
            its = grades.items(batch.load(DATE))
        self.assertTrue(its)
        self.assertFalse([i for i in its if i["kind"] == "reco"])


class Producer(Sandbox):
    def break_kid_1(self):
        path = lib.DRAFTS / DATE / "pack.json"
        pack = lib.read_json(path)
        v = next(v for d in pack["directions"] for v in d["versions"] if v["id"] == "kid-1")
        v["slides"][1]["headline"] = " ".join(["מילה"] * 40)
        lib.write_json(path, pack)

    def test_an_option_with_errors_is_fixed_before_it_is_produced(self):
        """Yarin, 22 Oct 2026: Produce never refuses; it runs autofix.py first (it used to raise Blocked, 18 Oct)."""
        other_before = producer.blocking_errors(self.item(f"{DATE}/kid-2"))
        self.break_kid_1()
        key = f"{DATE}/kid-1"
        with mock.patch.object(producer, "_pool") as pool:
            producer.start(self.item(key))
            pool.submit.assert_called_once()
        self.assertEqual(producer.get(key)["status"], "queued")
        import autofix
        seen = []
        with mock.patch.object(autofix, "run", side_effect=lambda it: seen.append(producer.get(key)["status"]) or []), \
                mock.patch.object(producer, "_prepare", side_effect=RuntimeError("stop here")):
            producer._work(key, self.item(key), "start")
        self.assertEqual(seen, ["fixing"])
        self.assertEqual(producer.get(key)["error"], "stop here")
        self.assertEqual(producer.blocking_errors(self.item(f"{DATE}/kid-2")), other_before)  # kid-1's errors never touch kid-2

    def test_autofix_splits_a_long_line_without_a_model(self):
        import autofix
        self.assertEqual(autofix.split_line("נותנים לו להירגע ומשתדלים לא לזרז אותו", 34), ("נותנים לו להירגע", "ומשתדלים לא לזרז אותו"))
        self.assertIsNone(autofix.split_line("מילהארוכהמאודבליבכלל רווחים", 10))
        v = {"id": "kid-1", "slides": [{"body": "x"}, {"body": "נותנים לו להירגע ומשתדלים לא לזרז אותו"}, {"body": "cta"}]}
        err = {"path": "kid/kid-1/slide-2/body", "message": "line 1 has 38 characters and will not fit the slide at a readable size (max 34); break it into two lines"}
        self.assertEqual(autofix.mechanical(v, [err]), [{"option": "kid-1", "field": "body", "slide": 2, "value": "נותנים לו להירגע\nומשתדלים לא לזרז אותו"}])

    def test_the_page_state_carries_each_options_errors(self):
        self.break_kid_1()
        its = {i["key"]: i for i in studio.state(DATE)["items"]}
        self.assertTrue(its[f"{DATE}/kid-1"]["errors"])
        self.assertEqual(its[f"{DATE}/reco"]["errors"], [])

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

    def test_a_declined_picture_says_so_plainly(self):
        key = f"{DATE}/kid-1"
        producer._update(key, status="generating")
        out = '{"error": "The model\'s safety system declined this request (content_policy_violation)."}'
        with mock.patch.object(producer, "_sh", return_value=(1, out)), mock.patch.object(producer, "_picture_state", return_value={}), \
                mock.patch.object(producer, "_gate", return_value=1.0):   # Yarin's budget and yes are tested in test_openai_pictures.py
            with self.assertRaises(RuntimeError) as ctx:
                producer._generate(key, self.tmp)
        self.assertEqual(str(ctx.exception), producer.DECLINED_HE)
        self.assertTrue(producer.get(key)["declined"])

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
    def test_one_page_hebrew_rtl_without_em_dashes(self):
        html = studio.app_page(DATE)
        self.assertIn('dir="rtl"', html)
        self.assertIn("Carousel Machine", html)
        self.assertNotIn("—", html)
        for part in ('id="hs-groups"', 'id="hs-stage"', 'id="hs-insp"', 'id="hs-send"'):
            self.assertIn(part, html)

    def test_state_carries_items_grades_and_runs(self):
        grades.upsert(self.item(f"{DATE}/kid-2"), score=4)
        html = studio.app_page(DATE)
        data = json.loads(html.split('<script type="application/json" id="hs-state">')[1].split("</script>")[0])
        self.assertEqual(data["batch"], DATE)
        self.assertEqual(len(data["items"]), 7)
        self.assertEqual(data["grades"][f"{DATE}/kid-2"]["score"], 4)
        kid = data["items"][0]
        self.assertTrue(kid["cta"])
        self.assertNotIn(kid["cta"], kid["caption_body"])   # the CTA is edited on its own
        reco = data["items"][6]
        self.assertTrue(all("role" in s for s in reco["slides"]))
        self.assertTrue(reco["images"][0].split("?v=")[1].isdigit())   # cache-busted after a re-render

    def test_next_cloud_run_is_a_thursday_evening_utc(self):
        import datetime as dt
        at = studio.next_cloud_run(dt.datetime(2026, 10, 16, 8, 0, tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)
        self.assertEqual((at.weekday(), at.hour, at.day), (3, 19, 22))


if __name__ == "__main__":
    unittest.main()


class DriveExport(unittest.TestCase):
    """Finished carousels are copied to Yarin's Drive folder, or wait in a queue (18 Oct 2026)."""

    def setUp(self):
        import drive_export
        self.de = drive_export
        self.tmp = Path(tempfile.mkdtemp())
        self.approved = self.tmp / "approved"
        self.run = self.approved / "2026-10-18-kid-2"
        (self.run / "final").mkdir(parents=True)
        for n in ("01.png", "02.png", "caption.txt", "alt-text.txt", "contact-sheet.png", "slides.html"):
            (self.run / "final" / n).write_text(n, encoding="utf-8")
        lib.write_json(self.run / "approved.json", {"topic": {"title_he": "מעבר לשעון חורף"}})
        self.cloud = self.tmp / "CloudStorage"
        cfg = {"name": "LumeBook תוכן", "account": "a@b.c", "carousels": {"name": "קרוסלות"}}
        self.patches = [mock.patch.object(lib, "APPROVED", self.approved),                         mock.patch.object(drive_export, "CLOUD", self.cloud),
                        mock.patch.object(drive_export, "config", return_value=cfg)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_runs_outside_approved_never_reach_drive(self):
        other = self.tmp / "elsewhere"
        other.mkdir()
        self.assertIsNone(self.de.export(other, quiet=True))
        self.assertFalse(self.de.pending_path().exists())

    def test_queues_without_drive_then_copies_on_flush(self):
        self.assertIsNone(self.de.export(self.run, quiet=True))
        self.assertEqual(lib.read_json(self.de.pending_path())["runs"], ["2026-10-18-kid-2"])
        target = self.cloud / "GoogleDrive-a@b.c" / "My Drive" / "LumeBook תוכן"
        target.mkdir(parents=True)
        root, done, left = self.de.flush()
        self.assertEqual((root, left), (target, []))
        dest = target / "קרוסלות" / "2026-10-18-kid-2 מעבר לשעון חורף"
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["01.png", "02.png", "alt-text.txt", "caption.txt", "contact-sheet.png"])
        self.assertFalse(self.de.pending_path().exists())
