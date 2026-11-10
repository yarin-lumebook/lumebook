"""The five trial versions of a make (Yarin, 10 Nov 2026): which hooks they get, and that their lengths go both ways.

Run: python3 -m unittest discover -s research/israeli-product-reels/src/scripts/series-2026-11/tests
(the length test needs Pillow, so it is skipped under a Python without it; the reel editor's own venv has it)
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import reel_make  # noqa: E402
import reels  # noqa: E402


class TrialHooks(unittest.TestCase):
    def test_reel_hooks_first_then_mine(self):
        with tempfile.TemporaryDirectory() as t:
            hooks, note = reel_make.trial_hooks_for("1.4", "א\nב", Path(t), ["ג", "ד", "ה", "ו"])
        self.assertEqual(hooks, ["א\nב", "ג", "ד", "ה", "ו"])
        self.assertEqual(note, "")

    def test_plan_hooks_when_the_reel_has_none(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "edit.json").write_text(json.dumps({"trial_hooks": ["ג", "", "ד"]}))
            hooks, note = reel_make.trial_hooks_for("1.4", "א", Path(t), ["", " "])
        self.assertEqual(hooks, ["א", "ג", "ד"])
        self.assertIn("only 3", note)

    def test_repeats_are_dropped(self):
        with tempfile.TemporaryDirectory() as t:
            hooks, _ = reel_make.trial_hooks_for("1.4", "א ב", Path(t), ["א  ב", "ג"])
        self.assertEqual(hooks, ["א ב", "ג"])


class OwnCta(unittest.TestCase):
    def test_his_own_closing_line_replaces_the_fixed_one(self):
        self.assertTrue(reels.own_cta({"vo": ["שורה", "תכתבו לי לומי בתגובות,", "ואני אשלח לכם קישור"]}))
        self.assertFalse(reels.own_cta({"vo": ["שורה", "עוד שורה"]}))


class TrialLengths(unittest.TestCase):
    def test_some_shorter_some_longer_all_different(self):
        try:
            sys.path.insert(0, str(HERE.parents[4] / ".claude/skills/reel-editor/scripts"))
            import reel_editor
        except ImportError:
            self.skipTest("Pillow is not installed for this Python")
        for seed in ("reel-1-4-a", "reel-1-4-b", "x"):
            ps = reel_editor.trial_params(5, seed, False, 21.0)
            delta = [p["hold_end"] - p["trim_start"] - p["trim_end"] for p in ps]
            self.assertTrue(any(x < 0 for x in delta) and any(x > 0 for x in delta), delta)
            self.assertEqual(len({round(x, 2) for x in delta}), 5)
            self.assertTrue(all(0.15 - 0.02 <= abs(x) <= 0.8 for x in delta), delta)
            self.assertTrue(all(not p["flip"] for p in ps))
            self.assertEqual(len({p["zoom"] for p in ps}), 5)


if __name__ == "__main__":
    unittest.main()
