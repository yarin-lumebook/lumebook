#!/usr/bin/env python3
"""The story format's render and production (story-format.md sections 4 and 6, 29 Oct 2026). Standard library only.

    python3 -m unittest carousel/carousel-pipeline/tests/test_story_production.py -v

No test touches the network, fal.ai, Postiz or the real approved runs. The render test needs Google Chrome.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import carousel_lib as lib  # noqa: E402
import compose_slides  # noqa: E402
import drive_export  # noqa: E402
import openai_generate  # noqa: E402
import openai_pictures as op  # noqa: E402
import postiz_export  # noqa: E402
import prepare_picture_jobs  # noqa: E402
import producer  # noqa: E402

ANCHOR = {"child": "A 4-year-old Israeli girl with dark curls.", "parent": "Her mother, early thirties.",
          "wardrobe": "Girl: yellow T-shirt. Mother: grey cardigan."}
COVER = {"beat": "she wants to say something", "action": "The girl faces the viewer and looks straight into the camera with huge wide eyes.",
         "setting": "A small Israeli living room.", "camera": "Child eye level.", "lighting": "Soft daylight.",
         "wardrobe_objects": "A plush rabbit.", "text_zone": {"edge": "top", "percent": 40, "surface": "plain cream wall"}}


def story_option(structure="one_day", count=9):
    """A story option in the pack shape: cover, beats with every kind of markup, the save CTA."""
    beats = [
        {"label": "07:30, בבוקר", "headline": "אני מתעוררת לאט", "body": "העיניים שלי עוד סגורות.\nאני רוצה **עוד רגע** איתך.\n\n## מה יעזור לי:\nשיר קטן לפני שקמים."},
        {"label": "1: פתאום אני קטנה", "headline": "", "body": "אני מבקשת שתרימי אותי.\nכמו פעם.\n> ״אני פה, מתוקה.״"},
        {"label": "אתם חושבים:", "headline": "״היא סתם עושה דווקא״", "body": "## אני עונה:\nאני פשוט עייפה מהיום."},
    ]
    slides = [{"number": 1, "role": "hook", "headline": "אמא, יש לי\nמשהו להגיד לך", "body": "יום אחד שלי"}]
    for n in range(2, count):
        b = beats[(n - 2) % len(beats)]
        slides.append({"number": n, "role": "beat", **b,
                       "scene": {"action": f"The girl in moment {n} of her day.", "setting": "The same living room."}})
    slides.append({"number": count, "role": "story_cta", "headline": "תשמרי את הפוסט", "body": "לפעם הבאה שהיא עייפה",
                   "scene": {"action": "The girl sleeps calmly hugging her mother.", "setting": "Her bed at night."}})
    return {"id": "kid-1", "structure": structure, "character_anchor": ANCHOR, "image": COVER, "slides": slides,
            "caption": "אמא, יש לי משהו להגיד לך\nתשמרי את הפוסט לפעם הבאה שהיא עייפה", "cta": "",
            "sources": [{"id": "s1", "title": "t", "url": "https://example.org", "publisher": "p", "accessed": "2026-10-29",
                         "supports": "x", "quote": "q"}], "claims": []}


def frozen_of(option, copy_style="story"):
    out = {"date": "2026-11-01", "topic": {"id": "t", "title_he": "נושא"}, "direction": "kid", "option_id": option["id"],
           "voice": {}, "product_facts": [], "option": option}
    if copy_style:
        out["copy_style"] = copy_style
    return out


class StoryLookChoice(unittest.TestCase):
    def test_story_runs_get_the_story_look_and_others_never_do(self):
        self.assertTrue(compose_slides.is_story(frozen_of(story_option())))
        self.assertTrue(compose_slides.is_story(frozen_of({**story_option(), "structure": "letter"}, copy_style=None)))
        self.assertFalse(compose_slides.is_story(frozen_of({"id": "kid-1", "slides": []}, copy_style=None)))
        self.assertEqual(compose_slides.choose_look(None, None, story_option(), story=True), "story")
        self.assertEqual(compose_slides.choose_look(None, "story", story_option(), story=True), "story")   # edit_final re-export
        self.assertEqual(compose_slides.choose_look("clean", None, story_option(), story=True), "clean")  # --look wins
        one_pic = {"image": COVER, "slides": [{"number": 1}]}
        self.assertEqual(compose_slides.choose_look(None, "story", one_pic), "clean")   # never carried to older copy

    def test_markup_becomes_labels_cards_and_gold_words(self):
        html = compose_slides.story_body_html("שורה אחת\n**מילה** שנייה\n\n## מה יעזור לי:\n> ״אני פה״")
        self.assertIn('<span class="em">מילה</span>', html)
        self.assertIn('<div class="gap"></div>', html)
        self.assertIn('<div class="lab">מה יעזור לי:</div>', html)
        self.assertIn('<span class="say"><span class="q">״אני פה״</span></span>', html)
        v = story_option()
        tag = compose_slides.story_slide_html(v, v["slides"][2], "x.png", 9)
        self.assertIn('<span class="num">1</span>פתאום אני קטנה', tag)
        plain = compose_slides.story_slide_html(v, v["slides"][1], "x.png", 9)
        self.assertIn('class="tag plain">07:30, בבוקר', plain)
        cta = compose_slides.story_slide_html(v, v["slides"][-1], "x.png", 9)
        self.assertIn('class="btn"><svg', cta)
        letter = compose_slides.story_slide_html({**v, "structure": "letter"}, v["slides"][2], "x.png", 9)
        self.assertIn('class="slide letter"', letter)
        self.assertEqual(compose_slides.plain_text("## מה:\n> ״אני״\n**כן** לא"), "מה:\n״אני״\nכן לא")


class StoryJobs(unittest.TestCase):
    def test_cover_by_text_to_image_then_an_edit_per_slide(self):
        cfg = prepare_picture_jobs.endpoint_config()
        v = story_option(count=12)
        jobs = prepare_picture_jobs.build_jobs({"copy_style": "story"}, v, cfg)
        self.assertEqual(jobs["order"], [f"slide-{n:02d}" for n in range(1, 13)])
        self.assertEqual((jobs["story"], jobs["reference_job"], jobs["backend"]), (True, "slide-01", "openai"))
        self.assertNotIn("max_usd", jobs)   # no built-in cap: the budget is whatever Yarin approves (03 Nov 2026)
        cover, slide = jobs["jobs"]["slide-01"], jobs["jobs"]["slide-05"]
        self.assertEqual((cover["mode"], cover["model"], cover["refs"]), ("generate", cfg["model"], []))
        self.assertIn(COVER["action"], cover["input"]["prompt"])
        self.assertEqual((slide["mode"], slide["model"], slide["refs"]), ("edit", cfg["model"], ["slide-01"]))
        self.assertEqual(cover["input"]["quality"], "low")
        for part in (ANCHOR["child"], "moment 5", lib.STYLE, "upper third", "No words, letters or numbers"):
            self.assertIn(part, slide["input"]["prompt"])
        self.assertEqual([p for n, j in jobs["jobs"].items() for p in prepare_picture_jobs.job_issues(n, j, cfg)], [])
        base, maximum = prepare_picture_jobs.cost_summary(jobs)
        self.assertGreater(base, 0)
        self.assertAlmostEqual(maximum, base * (1 + prepare_picture_jobs.MAX_REPLACEMENTS), places=3)
        self.assertEqual(base, round(sum(op.estimate_job(j, cfg)["usd"] for j in jobs["jobs"].values()), 4))

    def test_older_options_keep_their_one_picture(self):
        pack = json.loads((HERE / "fixtures" / "two_topic_pack.json").read_text(encoding="utf-8"))
        v = pack["directions"][0]["versions"][0]
        jobs = prepare_picture_jobs.build_jobs(pack, v, prepare_picture_jobs.endpoint_config())
        self.assertEqual(jobs["order"], ["picture"])
        self.assertNotIn("story", jobs)

    def test_a_slide_with_no_scene_stops_the_freeze(self):
        v = story_option()
        del v["slides"][3]["scene"]
        with self.assertRaises(SystemExit):
            prepare_picture_jobs.build_jobs({"copy_style": "story"}, v, prepare_picture_jobs.endpoint_config())


class StoryRun(unittest.TestCase):
    """A run folder with jobs.json and state.json as prepare_picture_jobs writes them, in a temporary folder."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="story-run-"))
        self.run_dir = self.tmp / "2026-11-01-kid-1"
        (self.run_dir / "generated-assets" / "rejected").mkdir(parents=True)
        v = story_option()
        self.jobs = prepare_picture_jobs.build_jobs({"copy_style": "story"}, v, prepare_picture_jobs.endpoint_config())
        lib.write_json(self.run_dir / "approved.json", frozen_of(v))
        lib.write_json(self.run_dir / "jobs.json", self.jobs)
        self.state({n: "pending" for n in self.jobs["order"]})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def state(self, statuses, qa=None):
        lib.write_json(self.run_dir / "state.json", {"jobs": {n: {"status": s, "attempts": int(s == "done"), "replacements": 0,
                                                                 "qa": (qa or {}).get(n), "notes": []} for n, s in statuses.items()}})

    def test_the_cover_runs_alone_first_and_the_budget_holds(self):
        run = openai_generate.Run(self.run_dir)
        self.assertEqual(openai_generate.reference_job(run), "slide-01")
        with mock.patch.object(openai_generate, "execute") as ex, \
                mock.patch.object(op, "OpenAIImages", side_effect=AssertionError("no network in tests")):
            openai_generate.cmd_run(run, mock.Mock(jobs=[], dry_run=False, max_usd=1.0, workers=4))
        self.assertEqual([c.args[1] for c in ex.call_args_list], ["slide-01"])   # never the slides before the cover passes
        run.log({"job": "x", "estimated_cost_usd": 0.5})
        with self.assertRaises(SystemExit):
            openai_generate.check_budget(run, 0.6, 1.0)   # 0.5 logged + 0.6 would pass the approved 1.0
        openai_generate.check_budget(run, 0.4, 1.0)
        with self.assertRaises(SystemExit):
            openai_generate.check_budget(run, 0.01, None)   # no budget, no call

    def test_producer_knows_the_cover_and_asks_before_spending(self):
        self.assertTrue(producer.is_story(self.run_dir))
        self.assertEqual((producer.cover_job(self.run_dir), producer.cover_job(self.tmp)), ("slide-01", "picture"))
        store = self.tmp / "p.json"
        with mock.patch.object(producer, "PRODUCTIONS", store):
            with self.assertRaises(producer.NeedsApproval) as ctx:   # no budget, no permission
                producer._gate("k", self.run_dir, "cover", ["slide-01"])
            self.assertEqual((ctx.exception.info["stage"], ctx.exception.info["images"]), ("cover", 1))
            self.assertGreater(ctx.exception.info["usd"], 0)
            producer._update("k", budget_usd=5.0, grant={"stage": "slides"})
            with self.assertRaises(producer.NeedsApproval):   # a permission for another stage is not this one
                producer._gate("k", self.run_dir, "cover", ["slide-01"])
            producer._update("k", grant={"stage": "cover"}, budget_usd=0.0001)
            with self.assertRaises(producer.NeedsApproval):   # the estimate does not fit the budget
                producer._gate("k", self.run_dir, "cover", ["slide-01"])
            producer._update("k", grant={"stage": "cover"}, budget_usd=5.0)
            self.assertEqual(producer._gate("k", self.run_dir, "cover", ["slide-01"]), 5.0)
            self.assertIsNone(producer.get("k").get("grant"))   # used up: the next stage asks again

    def test_after_the_cover_the_other_slides_run_together_and_pass_with_it(self):
        order = self.jobs["order"]
        self.state({n: "done" if n == "slide-01" else "pending" for n in order}, qa={"slide-01": "pass"})
        calls = []

        def fake_sh(args, timeout, env_shell=False):
            args = [str(a) for a in args]
            calls.append(args)
            if "run" in args:   # openai_generate run: every asked slide is made, except slide-04 the first time
                st = lib.read_json(self.run_dir / "state.json")
                for n in args[args.index("run") + 1:args.index("--max-usd")]:
                    if n != "slide-04" or len([c for c in calls if "run" in c]) > 1:
                        st["jobs"][n]["status"] = "done"
                lib.write_json(self.run_dir / "state.json", st)
            elif "qa" in args:
                st = lib.read_json(self.run_dir / "state.json")
                st["jobs"][args[args.index("qa") + 1]]["qa"] = args[args.index("qa") + 2]
                lib.write_json(self.run_dir / "state.json", st)
            return 0, ""

        with mock.patch.object(producer, "_sh", side_effect=fake_sh), mock.patch.object(producer, "PRODUCTIONS", self.tmp / "p.json"):
            producer._update("k", budget_usd=5.0, grant={"stage": "slides"})
            with self.assertRaises(RuntimeError) as ctx:
                producer._generate_slides("k", self.run_dir)
            self.assertIn("slide-04", str(ctx.exception))
            first = next(c for c in calls if "run" in c)
            self.assertEqual(first[first.index("run") + 1:first.index("--max-usd")], order[1:])
            self.assertEqual(first[-1], "5.0")
            with self.assertRaises(producer.NeedsApproval):   # pressing produce again asks again: the permission was used up
                producer._generate_slides("k", self.run_dir)
            producer._update("k", grant={"stage": "slides"})
            producer._generate_slides("k", self.run_dir)   # then it makes only the missing one
            again = [c for c in calls if "run" in c][-1]
            self.assertEqual(again[again.index("run") + 1:again.index("--max-usd")], ["slide-04"])
        st = lib.read_json(self.run_dir / "state.json")["jobs"]
        self.assertTrue(all(s["status"] == "done" and s["qa"] == "pass" for s in st.values()))

    def test_only_this_carousels_slides_are_sent_on(self):
        final = self.run_dir / "final"
        final.mkdir()
        for n in range(1, 13):   # 12 PNGs left from a longer version; the option has 9 slides
            (final / f"{n:02d}.png").write_bytes(b"x")
        self.assertEqual([p.name for p in drive_export.final_slides(self.run_dir)], [f"{n:02d}.png" for n in range(1, 10)])
        self.assertEqual(len(postiz_export.slides_of(self.run_dir)), 9)

    def test_facebook_text_has_no_markup(self):
        fb = postiz_export.fb_text(self.run_dir)
        self.assertNotIn("**", fb)
        self.assertNotIn("##", fb)
        self.assertIn("עוד רגע", fb)


@unittest.skipUnless(lib.CHROME, "Google Chrome is needed for the renderer test")
class StoryRender(unittest.TestCase):
    def test_placeholders_render_every_slide_in_the_story_look(self):
        tmp = Path(tempfile.mkdtemp(prefix="story-render-"))
        try:
            run_dir = tmp / "2026-11-01-kid-1"
            run_dir.mkdir()
            lib.write_json(run_dir / "approved.json", frozen_of(story_option(structure="letter", count=10)))
            res = subprocess.run([sys.executable, str(SCRIPTS / "compose_slides.py"), str(run_dir), "--placeholders"],
                                 capture_output=True, text=True, timeout=600)
            self.assertEqual(res.returncode, 0, res.stdout[-1500:] + res.stderr[-1500:])
            out = json.loads(res.stdout)
            self.assertEqual((out["look"], out["rtl_problems"], len(out["slides"])), ("story", [], 10))
            final = run_dir / "final-placeholders"
            for n in range(1, 11):
                self.assertEqual(lib.png_size(final / f"{n:02d}.png"), (1080, 1350))
            report = json.loads((final / "rtl-report.json").read_text(encoding="utf-8"))
            self.assertTrue(all(r["font"] and r["fit"] == "ok" for r in report))
            self.assertIn("look-story", (final / "slides.html").read_text(encoding="utf-8"))
            self.assertNotIn("**", (final / "alt-text.txt").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
