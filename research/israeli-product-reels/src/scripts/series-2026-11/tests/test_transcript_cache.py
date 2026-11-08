"""The reel's transcript is redone when its sound changes (audit of 08 Nov 2026). Temp files only."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reel_make as rm  # noqa: E402


class TranscriptCache(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = Path(self.dir.name)
        self.wav, self.raw = d / "voice-studio.wav", d / "words-raw.json"
        self.wav.write_bytes(b"take one")

    def tearDown(self):
        self.dir.cleanup()

    def test_no_transcript_yet(self):
        self.assertTrue(rm.transcript_is_stale(self.raw, self.wav))

    def test_same_sound_keeps_the_transcript(self):
        self.raw.write_text("[]")
        rm.mark_transcript(self.raw, self.wav)
        self.assertFalse(rm.transcript_is_stale(self.raw, self.wav))

    def test_new_sound_redoes_it(self):
        self.raw.write_text("[]")
        rm.mark_transcript(self.raw, self.wav)
        self.wav.write_bytes(b"take two")
        self.assertTrue(rm.transcript_is_stale(self.raw, self.wav))

    def test_an_old_transcript_without_a_mark_is_redone_once(self):
        self.raw.write_text("[]")
        self.assertTrue(rm.transcript_is_stale(self.raw, self.wav))


if __name__ == "__main__":
    unittest.main()
