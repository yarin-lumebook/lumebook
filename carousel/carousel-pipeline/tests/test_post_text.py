"""Post texts (Yarin, 26 Oct 2026): punctuated caption and Facebook text, one emoji on the hook and 🔖 on the CTA."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import carousel_lib as lib  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ten_slide_option.json"


def option():
    v = json.loads(FIXTURE.read_text(encoding="utf-8"))["version"]
    v["caption"] = "מה עוזר לה בבוקר\nחיבוק קצר ומילה טובה\nתשמרי את הפוסט לפעם הבאה"
    return v


def punctuated(v, hook_line=0):
    cap = "מה עוזר לה בבוקר? ☀️\nחיבוק קצר, ומילה טובה.\nתשמרי את הפוסט לפעם הבאה 🔖"
    fb = lib.fb_source(v).split("\n")
    fb[hook_line] += " ☀️"
    fb[-1] += " 🔖"
    return {"caption": cap, "fb_text": "\n".join(fb)}


class PostTextTest(unittest.TestCase):
    def test_valid_and_rebuilt_unchanged(self):
        v = option()
        v["post_text"] = punctuated(v)
        self.assertEqual([i.message for i in lib.post_text_issues("p", v) if i.level == "ERROR"], [])
        self.assertEqual(lib.post_texts(v)["caption"], v["post_text"]["caption"])

    def test_hook_emoji_may_end_line_two(self):
        v = option()
        v["post_text"] = punctuated(v, hook_line=1)
        self.assertEqual([i.message for i in lib.post_text_issues("p", v) if i.level == "ERROR"], [])
        self.assertEqual(lib.post_texts(v)["fb_text"], v["post_text"]["fb_text"])

    def test_edit_keeps_punctuation_of_unchanged_words(self):
        v = option()
        v["post_text"] = punctuated(v)
        v["caption"] = v["caption"].replace("חיבוק קצר", "חיבוק ארוך")
        self.assertEqual(lib.post_texts(v)["caption"].split("\n")[1], "חיבוק ארוך, ומילה טובה.")

    def test_rejects_changed_words_extra_emoji_and_dash(self):
        v = option()
        pt = punctuated(v)
        v["post_text"] = {**pt, "caption": pt["caption"].replace("חיבוק קצר,", "חיבוק קצר 🤗 - ")}
        msgs = " ".join(i.message for i in lib.post_text_issues("p", v))
        self.assertIn("two emojis", msgs)
        self.assertIn("hyphen", msgs)
        v["post_text"] = {**pt, "fb_text": pt["fb_text"].replace(lib.post_words(pt["fb_text"])[0], "אחר", 1)}
        self.assertIn("words must be exactly", " ".join(i.message for i in lib.post_text_issues("p", v)))

    def test_missing_post_text(self):
        self.assertIn("post_text is missing", lib.post_text_issues("p", option())[0].message)


if __name__ == "__main__":
    unittest.main()
