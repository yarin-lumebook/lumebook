#!/usr/bin/env python3
"""Pictures from ChatGPT instead of fal.ai (Yarin, 30 Oct 2026: "disconnect my fal account from the carousel machine, use my
chatgpt in chrome to create the images so everything will be free"): the backend switch, chatgpt_pictures.py next, ingest
and status, and the hand-over from the last picture to the slides and the ZIP. Standard library only, no network, never
the real approved runs or productions.json.

    python3 -m unittest carousel/carousel-pipeline/tests/test_chatgpt_pictures.py -v
"""

import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE))

import carousel_lib as lib  # noqa: E402
import chatgpt_pictures as cg  # noqa: E402
import fal_generate  # noqa: E402
import prepare_fal_jobs  # noqa: E402
import producer  # noqa: E402
import studio  # noqa: E402
from test_story_production import COVER, frozen_of, story_option  # noqa: E402

VOICE0 = {"status": "fallback", "approved_samples": 0, "required": 15, "from_profile": 0, "from_examples_folder": 0}
KEY = "2026-11-01/kid-1"


def png_size(path):
    data = Path(path).read_bytes()[:24]
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    return struct.unpack(">II", data[16:24])


class BackendSwitch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="backend-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def config(self, value):
        path = self.tmp / "production.json"
        if value is None:
            path.unlink(missing_ok=True)
        else:
            path.write_text(json.dumps({"picture_backend": value}), encoding="utf-8")
        return path

    def test_chatgpt_is_the_default_and_fal_must_be_named(self):
        self.assertEqual(lib.read_json(lib.PIPELINE / "production.json")["picture_backend"], "chatgpt")
        for value, expected in ((None, "chatgpt"), ("chatgpt", "chatgpt"), ("fal", "fal"), ("FAL", "chatgpt"), ("other", "chatgpt")):
            with mock.patch.object(lib, "PRODUCTION_CONFIG", self.config(value)):
                self.assertEqual(lib.picture_backend(), expected, value)

    def test_fal_generate_refuses_to_run_without_fal(self):
        env = dict(os.environ, CAROUSEL_PRODUCTION_CONFIG=str(self.config("chatgpt")))
        env.pop("FAL_KEY", None)
        res = subprocess.run([sys.executable, str(SCRIPTS / "fal_generate.py"), str(self.tmp), "status"], capture_output=True, text=True, env=env)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("disconnected from fal.ai", res.stdout + res.stderr)
        with mock.patch.object(lib, "picture_backend", return_value="chatgpt"):
            with self.assertRaises(SystemExit):
                fal_generate.Fal()   # never even opens a connection

    def test_the_producer_never_runs_fal_with_chatgpt(self):
        with mock.patch.object(lib, "picture_backend", return_value="chatgpt"), \
                mock.patch.object(producer, "_sh", side_effect=AssertionError("fal_generate.py must not run")), \
                mock.patch.object(producer, "PRODUCTIONS", self.tmp / "p.json"):
            with self.assertRaises(RuntimeError):
                producer._generate("k", self.tmp)
            with self.assertRaises(RuntimeError):
                producer._generate_slides("k", self.tmp)
            self.assertEqual(producer.cap_usd(self.tmp), 0)


class ChatGPTRun(unittest.TestCase):
    """A story run as the producer freezes it under the chatgpt backend, in a temporary folder."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="chatgpt-run-")).resolve()
        self.run_dir = self.tmp / "approved" / "2026-11-01-kid-1"
        (self.run_dir / "generated-assets" / "rejected").mkdir(parents=True)
        v = story_option(count=5)
        jobs = prepare_fal_jobs.build_jobs({"copy_style": "story"}, v, prepare_fal_jobs.endpoint_config())
        jobs.update(backend="chatgpt", max_usd=0)
        self.order = jobs["order"]
        lib.write_json(self.run_dir / "approved.json", frozen_of(v))
        lib.write_json(self.run_dir / "jobs.json", jobs)
        lib.write_json(self.run_dir / "state.json", {"jobs": {n: {"status": "pending", "attempts": 0, "replacements": 0, "qa": None, "notes": []}
                                                              for n in self.order}})
        self.downloads = self.tmp / "Downloads"
        self.downloads.mkdir()
        self.prod = self.tmp / "productions.json"
        self.item = {"key": KEY, "kind": "kid", "date": "2026-11-01", "id": "kid-1"}
        self.patches = [
            mock.patch.object(lib, "picture_backend", return_value="chatgpt"),
            mock.patch.object(producer, "PRODUCTIONS", self.prod),
            mock.patch.object(cg, "PRODUCTIONS", self.prod),
            mock.patch.object(cg, "downloads_dir", return_value=self.downloads),
            mock.patch.object(producer, "_prepare", return_value=self.run_dir),
            mock.patch.object(producer, "blocking_errors", return_value=[]),
            mock.patch.object(producer, "_sh", side_effect=AssertionError("no script may run: fal is disconnected")),
            mock.patch.object(producer, "_pool"),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def download(self, job, w=400, h=600):
        """What the helper leaves in ~/Downloads: ChatGPT's 2:3 portrait under the job's name."""
        path = self.downloads / cg.download_name(self.run_dir, job)
        lib.write_placeholder_png(path, w, h, seed=len(job))
        return path

    def start(self):
        producer._work(KEY, self.item, "start")
        return producer.get(KEY)

    def cover_approved(self):
        self.start()
        self.download("slide-01")
        cg.ingest(self.run_dir, "slide-01")
        producer.advance_waiting(background=False)
        producer._work(KEY, self.item, "approve")
        return producer.get(KEY)

    def test_start_waits_for_chatgpt_and_spends_nothing(self):
        rec = self.start()
        self.assertEqual((rec["status"], rec["stage"], rec["backend"], rec["spent_usd"]), ("waiting", "cover", "chatgpt", 0))
        self.assertEqual(rec["status_he"], producer.STATUS_HE["waiting"])
        self.assertEqual((rec["pictures_made"], rec["pictures_total"]), (0, len(self.order)))
        self.assertEqual(self.start()["status"], "waiting")   # pressing produce again leaves it waiting

    def test_next_gives_the_cover_first_with_everything_to_make_it(self):
        self.start()
        out = cg.next_jobs()
        self.assertEqual([j["job"] for j in out["jobs"]], ["slide-01"])
        job = out["jobs"][0]
        self.assertEqual((job["key"], job["stage"], job["reference"]), (KEY, "cover", None))
        self.assertEqual(job["download_as"], "lumebook-2026-11-01-kid-1-slide-01.png")
        self.assertEqual(Path(job["run_dir"]), self.run_dir.resolve())
        self.assertTrue(job["prompt"].startswith(cg.LEAD))
        self.assertIn(COVER["action"], job["prompt"])
        self.assertEqual(out["helper"], str(SCRIPTS / "chatgpt_helper.js"))
        self.assertTrue((SCRIPTS / "chatgpt_helper.js").exists())
        self.assertEqual(cg.next_jobs([str(self.run_dir)])["jobs"][0]["job"], "slide-01")   # a run folder named directly

    def test_ingest_takes_the_download_and_the_app_shows_it_for_approval(self):
        self.start()
        with self.assertRaises(SystemExit):
            cg.ingest(self.run_dir, "slide-02")   # slides wait for the approved cover
        dl = self.download("slide-01")
        res = cg.ingest(self.run_dir, "slide-01")
        pic = self.run_dir / "generated-assets" / "slide-01.png"
        self.assertEqual(png_size(pic), cg.SIZE)                      # ChatGPT's 2:3 cropped to 4:5 at 1024 x 1280
        self.assertFalse(dl.exists())
        self.assertTrue(Path(res["original"]).exists())
        self.assertIn("chatgpt-originals", res["original"])
        st = lib.read_json(self.run_dir / "state.json")["jobs"]["slide-01"]
        self.assertEqual((st["status"], st["qa"], st["attempts"], st["source"]), ("done", None, 1, "chatgpt"))
        log = [json.loads(l) for l in (self.run_dir / "generated-assets" / "generation-log.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual((log[-1]["estimated_cost_usd"], log[-1]["billed"], log[-1]["backend"]), (0, False, "chatgpt"))
        self.assertEqual(producer.spent(self.run_dir), 0)
        self.assertEqual(cg.next_jobs()["jobs"], [])                  # nothing more until Yarin approves
        with self.assertRaises(SystemExit):
            cg.ingest(self.run_dir, "slide-01", str(self.download("slide-01")))   # already has a picture
        self.assertEqual(producer.advance_waiting(background=False), [KEY])
        rec = producer.get(KEY)
        self.assertEqual(rec["status"], "review")
        self.assertTrue(rec["picture"].split("?")[0].endswith("generated-assets/slide-01.png"))

    def test_after_approval_next_gives_every_slide_with_the_cover_as_reference(self):
        rec = self.cover_approved()
        self.assertEqual((rec["status"], rec["stage"]), ("waiting", "slides"))
        self.assertEqual(lib.read_json(self.run_dir / "state.json")["jobs"]["slide-01"]["qa"], "pass")
        jobs = cg.next_jobs()["jobs"]
        self.assertEqual([j["job"] for j in jobs], self.order[1:])
        cover = str(self.run_dir / "generated-assets" / "slide-01.png")
        for j in jobs:
            self.assertEqual((j["reference"], j["stage"]), (cover, "slides"))
            self.assertIn(cg.REFERENCE_LEAD, j["prompt"])
            if j["job"] != self.order[-1]:   # the CTA slide has its own calm scene
                self.assertIn(f"moment {int(j['job'][-2:])}", j["prompt"])

    def test_the_last_slide_hands_over_to_compose(self):
        self.cover_approved()
        composed = []

        def fake_compose(key, run_dir):
            composed.append(Path(run_dir))
            producer._update(key, status="done")

        with mock.patch.object(producer, "_compose", side_effect=fake_compose):
            for n in self.order[1:-1]:
                self.download(n)
                cg.ingest(self.run_dir, n, str(self.downloads / cg.download_name(self.run_dir, n)))
            self.assertEqual(producer.advance_waiting(background=False), [])   # one slide still missing
            self.assertEqual(producer.get(KEY)["pictures_made"], len(self.order) - 1)
            self.download(self.order[-1])
            res = cg.ingest(self.run_dir, self.order[-1])
            self.assertEqual(res["still_to_make"], [])
            self.assertEqual(producer.advance_waiting(background=False), [KEY])
        self.assertEqual(composed, [self.run_dir])
        self.assertEqual(producer.get(KEY)["status"], "done")
        st = lib.read_json(self.run_dir / "state.json")["jobs"]
        self.assertTrue(all(s["status"] == "done" and s["qa"] == "pass" for s in st.values()))
        self.assertEqual(cg.next_jobs()["jobs"], [])

    def test_another_take_puts_the_cover_back_in_next_with_the_note(self):
        self.start()
        self.download("slide-01")
        cg.ingest(self.run_dir, "slide-01")
        producer.advance_waiting(background=False)
        producer._work(KEY, self.item, "redo", "the face to the camera")
        rec = producer.get(KEY)
        self.assertEqual((rec["status"], rec["replacements"]), ("waiting", 1))
        self.assertTrue((self.run_dir / "generated-assets" / "rejected" / "slide-01-attempt1.png").exists())
        job = cg.next_jobs()["jobs"][0]
        self.assertEqual(job["job"], "slide-01")
        self.assertIn("Fix from visual QA: the face to the camera", job["prompt"])
        self.download("slide-01")
        cg.ingest(self.run_dir, "slide-01")
        producer.advance_waiting(background=False)
        rec = producer.get(KEY)
        self.assertEqual(rec["status"], "review")
        self.assertTrue(rec["picture"].endswith("?v=2"))

    def test_status_says_what_to_make(self):
        self.start()
        buf = io.StringIO()
        with redirect_stdout(buf), mock.patch.object(cg, "run_path", side_effect=lambda v: Path(v)):
            cg.cmd_status()
        self.assertIn(KEY, buf.getvalue())
        self.assertIn("make now: slide-01", buf.getvalue())
        self.assertIn("picture backend: chatgpt", buf.getvalue())


class ChatGPTFreeze(unittest.TestCase):
    def test_prepare_marks_the_run_free_and_writes_the_chatgpt_steps(self):
        out = Path(tempfile.mkdtemp(prefix="chatgpt-freeze-"))
        cfg = out / "production.json"
        cfg.write_text(json.dumps({"picture_backend": "chatgpt"}), encoding="utf-8")
        argv = ["prepare_fal_jobs.py", str(HERE / "fixtures" / "story_pack.json"), "kid-1", "--out-root", str(out), "--no-history"]
        buf = io.StringIO()
        try:
            with mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "PRODUCTION_CONFIG", cfg), \
                    mock.patch.object(lib, "voice_status", return_value={**VOICE0, "approved_samples": 12}), redirect_stdout(buf):
                prepare_fal_jobs.main()
            summary = json.loads(buf.getvalue())
            run = Path(summary["run_dir"])
            jobs = lib.read_json(run / "jobs.json")
            self.assertEqual((jobs["backend"], jobs["max_usd"], jobs["story"]), ("chatgpt", 0, True))
            self.assertEqual((summary["backend"], summary["estimated_usd"], summary["estimated_max_usd"]), ("chatgpt", 0, 0))
            self.assertIn("$0", (run / "APPROVAL.md").read_text(encoding="utf-8"))
            readme = (run / "README.md").read_text(encoding="utf-8")
            self.assertIn("chatgpt_pictures.py", readme)
            self.assertNotIn("fal_generate", readme)
            self.assertNotIn("FAL_KEY", readme)
        finally:
            shutil.rmtree(out, ignore_errors=True)


class AppTexts(unittest.TestCase):
    def test_the_app_says_chatgpt_and_free_and_keeps_polling_while_waiting(self):
        js = studio.APP_JS
        self.assertIn("'waiting'", js)
        self.assertIn("ChatGPT · בחינם", js)
        self.assertIn("ב-ChatGPT ובחינם", js)
        self.assertIn("עד $1.00", js)   # the fal texts stay for picture_backend fal
        self.assertNotIn("—", js)
        self.assertNotIn("—", Path(SCRIPTS / "chatgpt_pictures.py").read_text(encoding="utf-8"))
        self.assertNotIn("—", Path(SCRIPTS / "chatgpt_helper.js").read_text(encoding="utf-8"))
        self.assertEqual(producer.STATUS_HE["waiting"], "מחכה לתמונות מ-ChatGPT")


if __name__ == "__main__":
    unittest.main()
