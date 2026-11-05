"""Carousel Machine's pictures come from the OpenAI Images API only (03 Nov 2026), under Yarin's four rules for the key:
always ask for a budget, never exceed it, tell the estimated tokens and cost before generating, create nothing without his
explicit permission. No test touches the network or the real approved runs."""

import io
import json
import shutil
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import carousel_lib as lib  # noqa: E402
import openai_pictures as op  # noqa: E402
import prepare_picture_jobs as pjobs  # noqa: E402
import producer  # noqa: E402
import studio  # noqa: E402

CFG = op.config()
USAGE_MEASURED = {"input_tokens": 121, "input_tokens_details": {"text_tokens": 121, "image_tokens": 0}, "output_tokens": 158}


def job(mode="generate", prompt="a prompt " * 50, refs=None):
    return pjobs.make_job(CFG, mode, prompt, refs if refs is not None else ([] if mode == "generate" else ["slide-01"]), op.base_input(CFG))


class Estimates(unittest.TestCase):
    def test_the_measured_run_costs_what_it_cost(self):
        # 03 Nov 2026: gpt-image-2.5-flare, 1024x1536, low: 121 text tokens in, 158 image tokens out
        self.assertAlmostEqual(op.usage_cost(USAGE_MEASURED, CFG), (121 * 5 + 158 * 30) / 1e6, places=5)
        self.assertAlmostEqual(op.usage_cost(USAGE_MEASURED, CFG), 0.0053, places=4)

    def test_the_estimate_is_above_the_measured_cost_and_counts_the_reference_picture(self):
        gen, edit = op.estimate_job(job("generate"), CFG), op.estimate_job(job("edit"), CFG)
        self.assertGreater(gen["usd"], op.usage_cost(USAGE_MEASURED, CFG))
        self.assertEqual((gen["input_image_tokens"], edit["input_image_tokens"]), (0, CFG["estimate"]["reference_image_tokens"]))
        self.assertGreater(edit["usd"], gen["usd"])
        total = op.estimate_total({"jobs": {"a": job("generate"), "b": job("edit")}}, cfg=CFG)
        self.assertEqual((total["images"], total["usd"]), (2, round(gen["usd"] + edit["usd"], 4)))
        self.assertEqual(total["total_tokens"], total["input_text_tokens"] + total["input_image_tokens"] + total["output_tokens"])

    def test_only_the_measured_quality_is_allowed(self):
        self.assertEqual(CFG["allowed_qualities"], ["low"])
        high = job()
        high["input"]["quality"] = "high"
        self.assertTrue(any("quality" in p for p in op.job_issues("x", high, CFG)))
        self.assertEqual(op.job_issues("x", job(), CFG), [])


class Client(unittest.TestCase):
    def fake_response(self, body):
        resp = mock.MagicMock()
        resp.__enter__.return_value = resp
        resp.read.return_value = json.dumps(body).encode()
        resp.headers = {"x-request-id": "req_1"}
        return resp

    def png_b64(self):
        import base64
        tmp = Path(tempfile.mkdtemp())
        try:
            lib.write_placeholder_png(tmp / "a.png", 64, 96, seed=1)
            return base64.b64encode((tmp / "a.png").read_bytes()).decode()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_no_key_no_call(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                op.OpenAIImages()

    def test_generate_sends_the_job_and_returns_the_usage(self):
        seen = {}

        def urlopen(req, timeout=None):
            seen["url"], seen["body"], seen["auth"] = req.full_url, json.loads(req.data), req.get_header("Authorization")
            return self.fake_response({"data": [{"b64_json": self.png_b64()}], "usage": USAGE_MEASURED})

        with mock.patch.object(op.urllib.request, "urlopen", urlopen):
            rid, png, usage = op.OpenAIImages("sk-test-key-123456").generate(job(), CFG)
        self.assertEqual((rid, usage), ("req_1", USAGE_MEASURED))
        self.assertTrue(png.startswith(b"\x89PNG"))
        self.assertTrue(seen["url"].endswith("/v1/images/generations"))
        self.assertEqual((seen["body"]["model"], seen["body"]["size"], seen["body"]["quality"], seen["body"]["n"]),
                         (CFG["model"], CFG["size"], "low", 1))

    def test_edit_is_multipart_with_the_reference_picture(self):
        seen = {}
        tmp = Path(tempfile.mkdtemp())
        lib.write_placeholder_png(tmp / "slide-01.png", 64, 80, seed=2)

        def urlopen(req, timeout=None):
            seen["url"], seen["body"], seen["type"] = req.full_url, req.data, req.get_header("Content-type")
            return self.fake_response({"data": [{"b64_json": self.png_b64()}], "usage": USAGE_MEASURED})

        try:
            with mock.patch.object(op.urllib.request, "urlopen", urlopen):
                op.OpenAIImages("sk-test-key-123456").edit(job("edit"), [tmp / "slide-01.png"], CFG)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertTrue(seen["url"].endswith("/v1/images/edits"))
        self.assertTrue(seen["type"].startswith("multipart/form-data; boundary="))
        self.assertIn(b'name="image[]"; filename="slide-01.png"', seen["body"])
        self.assertIn(b'name="model"', seen["body"])

    def test_an_error_answer_is_not_billed_and_never_shows_the_key(self):
        err = urllib.error.HTTPError("u", 401, "x", {}, io.BytesIO(json.dumps({"error": {"code": "invalid_api_key", "message": "Incorrect API key provided: sk-test-key-123456."}}).encode()))
        with mock.patch.object(op.urllib.request, "urlopen", side_effect=err):
            with self.assertRaises(op.ApiError) as ctx:
                op.OpenAIImages("sk-test-key-123456").generate(job(), CFG)
        self.assertFalse(ctx.exception.billed)
        self.assertEqual(ctx.exception.status, 401)
        self.assertNotIn("sk-test-key-123456", str(ctx.exception))

    def test_a_dropped_connection_counts_as_spent(self):
        with mock.patch.object(op.urllib.request, "urlopen", side_effect=urllib.error.URLError("timed out")):
            with self.assertRaises(op.ApiError) as ctx:
                op.OpenAIImages("sk-x").generate(job(), CFG)
        self.assertTrue(ctx.exception.billed)   # the outcome is unknown, so the budget counts it

    def test_the_picture_is_cropped_to_a_centred_4_by_5(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            lib.write_placeholder_png(tmp / "in.png", 1024, 1536, seed=4)
            op.normalize(tmp / "in.png", tmp / "out.png")
            self.assertEqual(lib.png_size(tmp / "out.png"), (1024, 1280))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Approval(unittest.TestCase):
    """The producer never spends before Yarin approves a stage (rules 1 to 4)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="approval-"))
        self.run_dir = self.tmp / "2026-11-03-kid-1"
        (self.run_dir / "generated-assets").mkdir(parents=True)
        jobs = {"order": ["picture"], "backend": "openai", "max_replacements_per_job": 2, "jobs": {"picture": job()}}
        lib.write_json(self.run_dir / "jobs.json", jobs)
        lib.write_json(self.run_dir / "state.json", {"jobs": {"picture": {"status": "pending", "attempts": 0, "replacements": 0, "qa": None, "notes": []}}})
        self.store = self.tmp / "p.json"
        self.patches = [mock.patch.object(producer, "PRODUCTIONS", self.store)]
        for p in self.patches:
            p.start()
        self.key = "2026-11-03/kid-1"
        self.item = {"key": self.key, "date": "2026-11-03", "id": "kid-1", "kind": "kid"}

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def work_start(self):
        calls = []
        with mock.patch.object(producer, "_sh", side_effect=lambda *a, **k: calls.append(a) or (0, "")), \
                mock.patch.object(producer, "blocking_errors", return_value=[]), \
                mock.patch.object(producer, "_prepare", return_value=self.run_dir):
            producer._update(self.key, status="queued", run_dir=str(self.run_dir), kind="kid")
            producer._work(self.key, self.item, "start")
        return calls

    def test_a_started_carousel_stops_for_approval_and_makes_nothing(self):
        calls = self.work_start()
        self.assertEqual(calls, [])   # no picture call of any kind
        rec = producer.get(self.key)
        self.assertEqual(rec["status"], producer.APPROVAL)
        info = rec["approval"]
        self.assertEqual((info["stage"], info["images"], info["model"], info["quality"]), ("cover", 1, CFG["model"], "low"))
        self.assertGreater(info["usd"], 0)
        self.assertGreater(info["tokens"], 0)
        self.assertEqual(rec["pending"], {"action": "start", "note": None})
        self.assertFalse((self.run_dir / "generated-assets" / "picture.png").exists())

    def test_authorize_needs_a_clear_yes_and_a_budget_that_covers_the_estimate(self):
        self.work_start()
        need = producer.get(self.key)["approval"]["need_usd"]
        for bad_confirmed in (None, False, "yes", 1):
            with self.assertRaises(ValueError):
                producer.authorize(self.key, self.item, 5, bad_confirmed)
        for bad_budget in (None, "", "abc", 0, -1):
            with self.assertRaises(ValueError):
                producer.authorize(self.key, self.item, bad_budget, True)
        with self.assertRaises(ValueError) as ctx:
            producer.authorize(self.key, self.item, need / 2, True)   # below the estimate
        self.assertIn("התקציב נמוך", str(ctx.exception))
        self.assertEqual(producer.get(self.key)["status"], producer.APPROVAL)   # nothing changed, nothing queued

    def test_authorize_grants_exactly_one_stage_and_resumes_it(self):
        self.work_start()
        need = producer.get(self.key)["approval"]["need_usd"]
        with mock.patch.object(producer._pool, "submit") as submit:
            rec = producer.authorize(self.key, self.item, need + 0.05, True)
        self.assertEqual((rec["budget_usd"], rec["grant"]["stage"], rec["status"]), (round(need + 0.05, 4), "cover", "queued"))
        submit.assert_called_once()
        self.assertEqual(submit.call_args.args[1:], (self.key, self.item, "start", None))
        # the work then spends the permission: the budget goes to the runner and the grant is gone
        calls = []

        def fake_sh(args, timeout, env_shell=False):
            calls.append([str(a) for a in args])
            lib.write_json(self.run_dir / "state.json", {"jobs": {"picture": {"status": "done", "attempts": 1, "replacements": 0, "qa": None, "notes": []}}})
            return 0, ""

        with mock.patch.object(producer, "_sh", side_effect=fake_sh), mock.patch.object(producer, "blocking_errors", return_value=[]), \
                mock.patch.object(producer, "_prepare", return_value=self.run_dir):
            producer._work(self.key, self.item, "start")
        run_call = next(c for c in calls if "run" in c)
        self.assertEqual(run_call[-2:], ["--max-usd", str(round(need + 0.05, 4))])
        self.assertIsNone(producer.get(self.key)["grant"])
        self.assertEqual(producer.get(self.key)["status"], "review")

    def test_another_take_asks_again_even_with_budget_left(self):
        lib.write_json(self.run_dir / "state.json", {"jobs": {"picture": {"status": "done", "attempts": 1, "replacements": 0, "qa": "fail", "notes": []}}})
        producer._update(self.key, status="review", run_dir=str(self.run_dir), kind="kid", picture="/x.png", budget_usd=50.0, grant=None)
        with mock.patch.object(producer, "_sh", side_effect=AssertionError("no call without approval")):
            producer._work(self.key, self.item, "redo", "fix the hands")
        rec = producer.get(self.key)
        self.assertEqual((rec["status"], rec["approval"]["stage"], rec["pending"]["note"]), (producer.APPROVAL, "redo", "fix the hands"))
        # a budget that is already used up asks for more
        self.assertEqual(rec["approval"]["budget_usd"], 50.0)

    def test_declining_makes_nothing(self):
        self.work_start()
        self.assertEqual(producer.cancel(self.key)["status"], "cancelled")   # a first stage leaves the queue
        self.assertIsNone(producer.get(self.key))
        lib.write_json(self.run_dir / "state.json", {"jobs": {"picture": {"status": "done", "attempts": 1, "replacements": 0, "qa": None, "notes": []}}})
        producer._update(self.key, status="review", run_dir=str(self.run_dir), kind="kid", picture="/x.png")
        with mock.patch.object(producer, "_sh", side_effect=AssertionError("no call without approval")):
            producer._work(self.key, self.item, "redo", "again")
        self.assertEqual(producer.cancel(self.key)["status"], "review")   # another take: back to the picture he was looking at

    def test_an_approval_survives_a_restart_and_a_stale_permission_does_not(self):
        self.work_start()
        producer.recover()
        self.assertEqual(producer.get(self.key)["status"], producer.APPROVAL)
        producer._update(self.key, status="generating", grant={"stage": "cover"})
        producer.recover()
        rec = producer.get(self.key)
        self.assertEqual((rec["status"], rec["grant"]), ("failed", None))


class Page(unittest.TestCase):
    def test_the_page_asks_for_the_budget_and_names_no_other_tool(self):
        js = studio.APP_JS
        for part in ("approvalBox", "'authorize'", "confirmed: true", "תקציב", "הערכת טוקנים", "הערכת עלות"):
            self.assertIn(part, js)
        self.assertNotIn("ChatGPT", js)
        self.assertNotIn("fal", js.lower().replace("falsy", "").replace("false", "").replace("fallback", "").replace("falls", ""))

    def test_nothing_in_the_pipeline_scripts_reaches_another_image_tool(self):
        # addresses and key names only: the docstrings still say what was retired
        banned = ("mcp.fal.ai", "FAL_KEY", "fal-ai/", "chatgpt.com", "api.genspark", "api.higgsfield", "chatgpt_pictures", "fal_generate")
        for path in sorted(SCRIPTS.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            for word in banned:
                self.assertNotIn(word, text, f"{path.name}: {word}")
        self.assertFalse((SCRIPTS / "fal_generate.py").exists() or (SCRIPTS / "chatgpt_pictures.py").exists())


if __name__ == "__main__":
    unittest.main()
