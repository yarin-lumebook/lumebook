"""A second send to Postiz keeps the first post's record (audit of 08 Nov 2026). Fakes only: no upload, no Postiz call."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import postiz_export as pe  # noqa: E402


class PostizHistory(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="postiz-history-"))
        self.run_dir = self.tmp / "2026-11-12-kid-1"
        (self.run_dir / "final").mkdir(parents=True)
        (self.run_dir / "final" / "caption.txt").write_text("כיתוב", encoding="utf-8")
        self.ids = iter(["post-1", "post-2", "post-3"])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def send(self):
        fake_cli = lambda *a, **k: [{"postId": next(self.ids), "integration": "x"}]
        with mock.patch.object(pe, "slides_of", return_value=[self.run_dir / "01.png"]), \
                mock.patch.object(pe, "stamp", return_value="s1"), \
                mock.patch.object(pe, "_upload", return_value={"id": "m1", "path": "https://example.invalid/m1.png"}), \
                mock.patch.object(pe, "payload", return_value={"type": "draft", "date": "2026-11-12T06:00:00+02:00", "posts": []}), \
                mock.patch.object(pe, "_cli", side_effect=fake_cli):
            return pe.send(self.run_dir, draft=True)

    def test_the_first_send_has_no_history(self):
        self.assertNotIn("previous", self.send())

    def test_every_earlier_post_id_is_kept(self):
        self.send()
        self.send()
        rec = self.send()
        self.assertEqual(rec["result"][0]["postId"], "post-3")
        self.assertEqual([p["result"][0]["postId"] for p in rec["previous"]], ["post-1", "post-2"])
        self.assertEqual(json.loads((self.run_dir / "postiz.json").read_text())["previous"][1]["result"][0]["postId"], "post-2")


if __name__ == "__main__":
    unittest.main()
