"""The weekly batch (16 Oct 2026): the plan, the second games and books carousel, the mixed order, event packs, the pool page."""

import copy
import datetime as dt
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
import reco_lib as rl  # noqa: E402
import validate_pack  # noqa: E402

FIXTURES = HERE / "fixtures"


class Sandbox(unittest.TestCase):
    """Drafts, histories and batch plans in a temporary folder."""

    reco_active = True

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="batch-test-"))
        drafts = self.tmp / "drafts"
        (drafts / "2026-10-17").mkdir(parents=True)
        packs = [{"date": d, "topic_id": t} for d, t in (("2026-10-13", "new-sibling"), ("2026-10-14", "sorry-on-command"), ("2026-10-17", "same-story"))]
        cars = [{"date": "2026-10-17", "format": "mixed", "skill": "problem_solving", "stage_id": "x", "age_min": 5, "age_max": 7,
                 "hook_structure": "count_ages_skill", "hook": "", "products": []}]
        self.patches = [
            mock.patch.object(lib, "DRAFTS", drafts),
            mock.patch.object(lib, "HISTORY", self.tmp / "history.json"),
            mock.patch.object(rl, "HISTORY", self.tmp / "reco-history.json"),
            mock.patch.object(batch, "BATCHES", drafts / "batches"),
            mock.patch.object(rl, "ACTIVE", self.reco_active),  # the carousel tests below still cover the switched-off code
        ]
        for p in self.patches:
            p.start()
        lib.write_json(lib.HISTORY, {"packs": packs})
        lib.write_json(rl.HISTORY, {"carousels": cars})

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def plan(self):
        return batch.make_plan(today=dt.date(2026, 10, 16), merge=False, log=lambda *_: None)


class PlanWithoutCarousels(Sandbox):
    reco_active = False  # Yarin, 18 Oct 2026: no more games and books carousels

    def test_no_carousels_in_the_plan(self):
        plan = self.plan()
        self.assertEqual(len(plan["slots"]), 7)
        self.assertTrue(all(s["reco"] == [] for s in plan["slots"]))
        self.assertIn("no games and books carousels", plan["rules"])

    def test_batch_start_context_has_no_recommendations(self):
        import nightly
        plan = self.plan()
        out = nightly.batch_start_context(plan, plan["slots"][1], plan["slots"][1]["date"], lib.DRAFTS / plan["slots"][1]["date"], [])
        self.assertIn("batch", out)
        self.assertNotIn("recommendations", out)
        self.assertNotIn("recommendations_2", out)


class Plan(Sandbox):
    def test_seven_slots_after_the_newest_night(self):
        plan = self.plan()
        self.assertEqual(plan["id"], "2026-10-18")
        self.assertEqual([s["date"] for s in plan["slots"]], [f"2026-10-{d}" for d in range(18, 25)])
        self.assertTrue((batch.BATCHES / "2026-10-18.json").exists())

    def test_slot_one_is_the_event_and_the_topics_never_repeat(self):
        plan = self.plan()
        first, rest = plan["slots"][0], plan["slots"][1:]
        self.assertEqual(first["kind"], "event")
        self.assertIsNone(first["topic_id"])
        topics = [s["topic_id"] for s in rest] + [first["fallback_topic_id"]]
        self.assertEqual(len(set(topics)), 7)
        for used in ("new-sibling", "sorry-on-command", "same-story"):
            self.assertNotIn(used, topics)
        self.assertTrue(all(r["event"] for r in first["reco"]))
        self.assertFalse(any(r["event"] for s in rest for r in s["reco"]))

    def test_fourteen_carousels_and_no_skill_within_four_packs(self):
        plan = self.plan()
        per_slot = [[r["skill"] for r in s["reco"]] for s in plan["slots"]]
        self.assertEqual(sum(len(x) for x in per_slot), 14)
        self.assertEqual([r["format"] for r in plan["slots"][0]["reco"]], ["mixed", "mixed2"])
        history = [["problem_solving"]] + per_slot  # the 17 Oct carousel came first
        for i in range(1, len(history)):
            window = {s for group in history[max(0, i - rl.SKILL_COOLDOWN_RUNS):i] for s in group}
            for skill in history[i]:
                self.assertNotIn(skill, window, f"slot {i}: {skill} within {rl.SKILL_COOLDOWN_RUNS} packs")
            self.assertEqual(len(set(history[i])), len(history[i]))

    def test_a_second_plan_starts_after_the_first(self):
        self.plan()
        second = batch.make_plan(today=dt.date(2026, 10, 22), merge=False, log=lambda *_: None)
        self.assertEqual(second["slots"][0]["date"], "2026-10-25")

    def test_plan_for_date(self):
        self.plan()
        plan, slot = batch.plan_for_date("2026-10-20")
        self.assertEqual((plan["id"], slot["n"]), ("2026-10-18", 3))
        self.assertEqual(batch.plan_for_date("2026-10-17"), (None, None))

    def test_the_one_page_lists_the_plan(self):
        import studio
        plan = self.plan()
        with mock.patch.object(studio, "grades_unsent", lambda: False):
            page = studio.app_page(plan["id"])
        self.assertIn('dir="rtl"', page)
        self.assertIn(f'value="{plan["id"]}" selected', page)
        self.assertNotIn("—", page)


class SecondCarousel(unittest.TestCase):
    def car(self, fmt):
        car = json.loads((FIXTURES / "reco" / rl.FILES[rl.MIXED]).read_text(encoding="utf-8"))
        car["format"] = fmt
        return car

    def test_mixed2_shares_the_rules_and_files(self):
        self.assertEqual(rl.FILES[rl.MIXED2], "reco-carousel-2.json")
        self.assertEqual(rl.SIZES[rl.MIXED2], rl.SIZES[rl.MIXED])
        self.assertIn(rl.MIXED2, rl.FORMATS)

    def test_the_two_carousels_of_one_pack_never_share_a_product(self):
        first = self.car(rl.MIXED)
        history = {"carousels": [rl.history_entry(first)]}
        issues = rl.rotation_issues(self.car(rl.MIXED2), history)
        self.assertTrue(any("recommended on" in str(i) and i.level == "ERROR" for i in issues))

    def test_a_normal_night_is_not_its_own_sibling(self):
        car = self.car(rl.MIXED)
        issues = rl.rotation_issues(car, {"carousels": [rl.history_entry(car)]})
        self.assertFalse(any("recommended on" in str(i) for i in issues))


class MixedOrder(unittest.TestCase):
    def car(self, generated_at):
        car = json.loads((FIXTURES / "reco" / rl.FILES[rl.MIXED]).read_text(encoding="utf-8"))
        car["generated_at"] = generated_at
        return car

    def order_errors(self, car):
        folder = Path(tempfile.mkdtemp(prefix="order-"))
        try:
            return [str(i) for i in rl.carousel_issues(car, folder) if "mix the games" in str(i) or "every game first" in str(i)]
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_older_carousels_keep_games_first(self):
        self.assertEqual(self.order_errors(self.car("2026-10-14T22:10:00+03:00")), [])

    def test_new_carousels_must_mix(self):
        errs = self.order_errors(self.car("2026-10-16T22:10:00+03:00"))
        self.assertTrue(any("mix the games" in e for e in errs), errs)

    def test_alternating_order_passes(self):
        car = self.car("2026-10-16T22:10:00+03:00")
        kinds = {p["id"]: p["kind"] for p in car["products"]}
        rec = [s for s in car["slides"] if s["role"] == "recommendation"]
        games = [s for s in rec if kinds[s["product_id"]] == "game"]
        books = [s for s in rec if kinds[s["product_id"]] == "book"]
        mixed = [x for pair in zip(games, books) for x in pair] + games[len(books):] + books[len(games):]
        numbers = [s["number"] for s in rec]
        for s, n in zip(mixed, numbers):
            s["number"] = n
        others = [s for s in car["slides"] if s["role"] != "recommendation"]
        car["slides"] = sorted(others + mixed, key=lambda s: s["number"])
        self.assertEqual(self.order_errors(car), [])


class EventPack(unittest.TestCase):
    def pack(self, **event):
        pack = {"date": "2026-10-20", "generated_at": "2026-10-16T22:10:00+03:00",
                "topic": {"id": "event-test", "title_he": "חג", "reason": "a test event pack"}}
        if event is not None:
            pack["topic"]["event"] = {"name_he": "חג", "date": "2026-10-25", "kind": "holiday", "tone": "exciting",
                                      "source": {"url": "https://example.org", "publisher": "x", "quote": "the date", "accessed": "2026-10-16"}, **event}
        return pack

    def test_event_topic_needs_an_event(self):
        pack = self.pack()
        del pack["topic"]["event"]
        self.assertTrue(validate_pack.event_issues(pack, None))

    def test_valid_event(self):
        self.assertEqual(validate_pack.event_issues(self.pack(), self.pack()["topic"]["event"]), [])

    def test_hard_moment_needs_talk_guidance(self):
        pack = self.pack(tone="hard")
        self.assertTrue(any("talk_source" in str(i) for i in validate_pack.event_issues(pack, pack["topic"]["event"])))

    def test_event_too_far_ahead(self):
        pack = self.pack(date="2026-12-30")
        self.assertTrue(any("days from the pack date" in str(i) for i in validate_pack.event_issues(pack, pack["topic"]["event"])))

    def test_only_event_topics_are_outside_the_bank(self):
        self.assertTrue(lib.is_event_topic("event-hanukkah-2026"))
        self.assertFalse(lib.is_event_topic("same-story"))


if __name__ == "__main__":
    unittest.main()
