"""Every OpenAI call that may have been paid lands in the spend log (audit of 08 Nov 2026).

An answer cut off or unreadable after a 200, or a crop that fails after a paid picture, used to leave the job "running"
with nothing logged, so the budget check undercounted. Temporary folders and fake clients only: no network, no key.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import carousel_lib as lib  # noqa: E402
import openai_generate as og  # noqa: E402
import openai_pictures as op  # noqa: E402
import prepare_picture_jobs as pjobs  # noqa: E402

CFG = op.config()
USAGE = {"input_tokens": 121, "input_tokens_details": {"text_tokens": 121, "image_tokens": 0}, "output_tokens": 158}


class Broken:
    """A client whose answer cannot be read (as json.load or base64 would fail on a cut-off body)."""

    def generate(self, job, cfg=None):
        raise ValueError("Expecting value: line 1 column 1 (char 0)")


class Paid:
    def generate(self, job, cfg=None):
        return "req_1", b"\x89PNG not really", USAGE


class SpendLog(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="spend-log-"))
        run_dir = self.tmp / "2026-11-09-kid-1"
        (run_dir / "generated-assets").mkdir(parents=True)
        job = pjobs.make_job(CFG, "generate", "a prompt " * 50, [], op.base_input(CFG))
        lib.write_json(run_dir / "jobs.json", {"order": ["picture"], "backend": "openai", "max_replacements_per_job": 2,
                                               "jobs": {"picture": job}})
        lib.write_json(run_dir / "state.json", {"jobs": {"picture": {"status": "pending", "attempts": 0, "replacements": 0,
                                                                      "qa": None, "notes": []}}})
        self.run = og.Run(run_dir)
        self.estimate = op.estimate_job(job, CFG)["usd"]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_an_unreadable_answer_counts_as_spent_at_the_estimate(self):
        with self.assertRaises(RuntimeError):
            og.execute(self.run, "picture", 1.0, False, client=Broken(), cfg=CFG)
        self.assertEqual(json.loads((self.run.dir / "state.json").read_text())["jobs"]["picture"]["status"], "failed")
        self.assertAlmostEqual(self.run.spent(), self.estimate)
        self.assertEqual(og.Run.reserved, 0.0)

    def test_a_failed_crop_after_a_paid_picture_is_logged_at_its_cost(self):
        real = op.normalize
        op.normalize = lambda raw, out: (_ for _ in ()).throw(RuntimeError("cannot convert the picture"))
        try:
            with self.assertRaises(RuntimeError):
                og.execute(self.run, "picture", 1.0, False, client=Paid(), cfg=CFG)
        finally:
            op.normalize = real
        self.assertAlmostEqual(self.run.spent(), op.usage_cost(USAGE, CFG))
        self.assertTrue((self.run.gen / "openai-originals" / "picture-attempt1.png").exists())   # the paid original is kept


if __name__ == "__main__":
    unittest.main()
