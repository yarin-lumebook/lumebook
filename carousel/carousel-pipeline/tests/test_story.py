"""The story copy format (story-format.md; Yarin, 29 Oct 2026: "i like the new content, change the entire carousel machine
and November batch to match it", after "why is it always 8 things? why always lists?")."""

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import carousel_lib as lib  # noqa: E402
import nightly  # noqa: E402
import story_lib  # noqa: E402
import validate_pack  # noqa: E402
import voice_lint  # noqa: E402

FIXTURES = HERE / "fixtures"


def story_pack():
    """Six story options on two topics (pacifier + accidents after potty training), one per structure, adapted from the
    Lotem-format reference copy (media/projects/2026-10-29-lotem-format-carousels/copy-structures.json)."""
    return lib.read_json(FIXTURES / "story_pack.json")


def errors(pack, **kw):
    return [i for i in validate_pack.pack_issues(pack, **kw) if i.level == "ERROR"]


def messages(pack, **kw):
    return " | ".join(f"{i.path}: {i.message}" for i in errors(pack, **kw))


def option(pack, oid):
    return next(v for d in pack["directions"] for v in d["versions"] if v["id"] == oid)


def slide(pack, oid, n):
    return next(s for s in option(pack, oid)["slides"] if s["number"] == n)


class StoryFixture(unittest.TestCase):
    def test_the_fixture_is_valid(self):
        pack = story_pack()
        self.assertEqual(messages(pack), "")
        self.assertEqual(lib.gender_balance_issues(pack), [])
        self.assertEqual(lib.example_target_issues(pack, FIXTURES), [])

    def test_every_structure_is_in_the_fixture(self):
        self.assertEqual(sorted(option(story_pack(), f"kid-{i}")["structure"] for i in range(1, 7)), sorted(story_lib.STRUCTURE_IDS))

    def test_older_packs_keep_their_rules(self):
        self.assertEqual(errors(lib.read_json(FIXTURES / "two_topic_pack.json")), [])
        old = lib.read_json(FIXTURES / "two_topic_pack.json")
        slide_ = old["directions"][0]["versions"][0]["slides"][2]
        slide_["label"] = "פעם"
        slide_["scene"] = {"action": "The girl hugs her rabbit.", "setting": "A bedroom."}
        msgs = messages(old)
        self.assertIn("slides[2]/label: is not a known field", msgs)
        self.assertIn("slides[2]/scene: is not a known field", msgs)
        old["directions"][0]["versions"][0]["structure"] = "letter"
        self.assertIn("versions[0]/structure: is not a known field", messages(old))

    def test_story_packs_are_not_numbered_lists(self):
        pack = story_pack()
        self.assertFalse(lib.numbered_examples_apply(pack))
        self.assertTrue(lib.numbered_examples_apply({k: v for k, v in pack.items() if k != "copy_style"}))
        self.assertEqual(lib.slide_count(pack), lib.TEN_SLIDE_COUNT)


class Distribution(unittest.TestCase):
    def test_two_short_lists_fail(self):
        pack = story_pack()
        option(pack, "kid-6")["structure"] = "short_list"
        self.assertIn("short_list is used 2 times (max 1)", messages(pack))

    def test_a_topic_needs_three_structures(self):
        pack = story_pack()
        option(pack, "kid-2")["structure"] = "letter"
        self.assertIn("topic a (kid-1, kid-2, kid-3) need three different structures", messages(pack))

    def test_at_least_four_structures_none_more_than_twice(self):
        got = story_lib.distribution_problems({"kid-1": "letter", "kid-2": "one_day", "kid-3": "one_minute",
                                               "kid-4": "letter", "kid-5": "one_day", "kid-6": "one_minute"}, lib.PAIR_LANES)
        self.assertTrue(any("3 structures" in x for x in got))
        got = story_lib.distribution_problems({"kid-1": "letter", "kid-2": "one_day", "kid-3": "one_minute",
                                               "kid-4": "letter", "kid-5": "before_after", "kid-6": "letter"}, lib.PAIR_LANES)
        self.assertTrue(any("letter is used 3 times" in x for x in got))

    def test_the_structure_is_required(self):
        pack = story_pack()
        del option(pack, "kid-3")["structure"]
        self.assertIn("versions[2]/structure: is required", messages(pack))


class Cover(unittest.TestCase):
    def test_a_list_of_8_on_a_cover_that_is_not_a_short_list(self):
        pack = story_pack()
        slide(pack, "kid-1", 1)["headline"] = "אמא, 8 דברים\nעל המוצץ שלי"
        self.assertIn("only a short_list may promise «N דברים»", messages(pack))

    def test_the_short_list_cover_number_matches_its_points(self):
        pack = story_pack()
        slide(pack, "kid-3", 1)["headline"] = "אמא, 5 דברים\nשאני צריך כדי\nלהיפרד מהמוצץ"
        self.assertIn("the cover promises 5 but the list has 4 points", messages(pack))

    def test_cover_pill_and_headline_size(self):
        pack = story_pack()
        slide(pack, "kid-2", 1)["body"] = "הלילה הראשון שלי בלי מוצץ, מבפנים ומבחוץ"
        slide(pack, "kid-4", 1)["headline"] = "אמא ואבא, אני יודע היטב\nמה אתם חושבים"
        msgs = messages(pack)
        self.assertIn("the cover pill has", msgs)
        self.assertIn("kid-4/slide-1/headline: line 1 has 23 characters (max 18)", msgs)


class Slides(unittest.TestCase):
    def test_a_body_line_over_38_characters(self):
        pack = story_pack()
        s = slide(pack, "kid-5", 4)
        s["body"] = s["body"].replace("הנדנדה, החול, החברות.\n", "הנדנדה, החול, החברות, והמגלשה הגדולה בחצר.\n")
        self.assertIn("kid-5/slide-4/body: line 1 has 42 characters (max 38)", messages(pack))

    def test_a_missing_scene(self):
        pack = story_pack()
        del slide(pack, "kid-2", 5)["scene"]
        self.assertIn("kid-2/slide-5/scene: every slide from 2 to the last has its own picture", messages(pack))

    def test_the_cta_slide_needs_a_scene_too(self):
        pack = story_pack()
        del option(pack, "kid-6")["slides"][-1]["scene"]
        self.assertIn("kid-6/slide-10/scene", messages(pack))

    def test_a_scene_asks_for_no_writing(self):
        pack = story_pack()
        slide(pack, "kid-5", 2)["scene"]["action"] = "A wall clock showing 07:30 above the girl."
        self.assertIn("a scene asks for no words, letters or numbers", messages(pack))

    def test_story_slide_words(self):
        pack = story_pack()
        slide(pack, "kid-6", 3)["body"] = "קמתי יבשה."
        s = slide(pack, "kid-6", 5)
        s["body"] = s["body"] + "\n" + "\n".join(["ועוד משהו קטן שאני רוצה לספר לך עכשיו."] * 4)
        msgs = messages(pack)
        self.assertIn("kid-6/slide-3: a story slide carries 15 to 50 words", msgs)
        self.assertIn("kid-6/slide-5: a story slide carries 15 to 50 words", msgs)

    def test_old_cap_of_25_words_is_gone(self):
        self.assertGreater(story_lib.word_count(slide(story_pack(), "kid-4", 2)["headline"], slide(story_pack(), "kid-4", 2)["body"]), lib.SLIDE_MAX_WORDS)

    def test_headline_two_lines_of_26(self):
        pack = story_pack()
        slide(pack, "kid-5", 5)["headline"] = "אני מסתירה את השקית מכולם בגן"
        self.assertIn("kid-5/slide-5/headline: line 1 has 29 characters (max 26)", messages(pack))

    def test_an_empty_headline_only_in_a_letter(self):
        pack = story_pack()
        slide(pack, "kid-2", 4)["headline"] = ""
        self.assertIn("kid-2/slide-4/headline: the headline may be empty only on the body slides of a letter", messages(pack))

    def test_roles(self):
        pack = story_pack()
        slide(pack, "kid-2", 4)["role"] = "turn"
        slide(pack, "kid-2", 5)["role"] = "example"
        msgs = messages(pack)
        self.assertIn("kid-2/slide-4/role: slide 4 must be beat", msgs)
        self.assertIn("slides[4]/role: must be one of hook, beat, turn, story_cta", msgs)

    def test_slide_count(self):
        pack = story_pack()
        v = option(pack, "kid-3")
        v["slides"] = v["slides"][:3] + v["slides"][-1:]
        for n, s in enumerate(v["slides"], 1):
            s["number"] = n
        self.assertIn("a story option has 9 to 12 slides", messages(pack))

    def test_label_length(self):
        pack = story_pack()
        slide(pack, "kid-6", 9)["label"] = "וזה מה שאני רוצה שתדעי עליי, אמא"
        self.assertIn("kid-6/slide-9/label: a label is one line of up to 28 characters", messages(pack))


class Markup(unittest.TestCase):
    def test_parse(self):
        blocks = story_lib.parse_body("אני **אוהב** אותה.\n\n## מה יעזור לי:\n> ״נלטף אותה ביחד?״\n")
        self.assertEqual([b["kind"] for b in blocks], ["line", "gap", "label", "card"])
        self.assertEqual(blocks[0]["text"], "אני אוהב אותה.")
        self.assertEqual(blocks[0]["emphasis"], ["אוהב"])
        self.assertEqual(story_lib.words("## מה יעזור לי:\n> ״נלטף אותה ביחד?״"), ["מה", "יעזור", "לי:", "״נלטף", "אותה", "ביחד?״"])

    def test_limits(self):
        pack = story_pack()
        s = slide(pack, "kid-4", 4)
        s["body"] = s["body"].replace("**שקשה לי**", "**שקשה** **לי** **עכשיו**") + "\n> ״אנחנו פה.״\n> ״ואנחנו איתך.״"
        msgs = messages(pack)
        self.assertIn("3 emphasised phrases", msgs)
        self.assertIn("2 card lines", msgs)

    def test_label_markup_length(self):
        self.assertTrue(any("characters (max 26)" in x for x in story_lib.markup_problems("## מה יעזור לי בפעם הבאה כשזה קורה:")))
        self.assertTrue(any("not closed" in x for x in story_lib.markup_problems("אני **מתבייש")))

    def test_shapes(self):
        self.assertEqual(story_lib.shape({"headline": "x", "body": "> ״אני פה.״"}), "card")
        self.assertEqual(story_lib.shape({"headline": "x", "body": "## מה אתם רואים:\nא\n## מה קורה לי בפנים:\nב"}), "see_inside")
        self.assertEqual(story_lib.shape({"headline": "למה דווקא אצלכם?", "body": "כי איתכם בטוח לי."}), "question")
        self.assertEqual(story_lib.shape({"headline": "x", "body": "אתמול הוא היה פה.\nהיום הוא איננו.\nואני מחכה."}), "beats")

    def test_facebook_text_has_no_markup(self):
        fb = lib.fb_source(option(story_pack(), "kid-4"))
        self.assertNotIn("##", fb)
        self.assertNotIn("**", fb)
        self.assertIn("אני עונה:", fb)


class Structures(unittest.TestCase):
    def test_letter_signature(self):
        pack = story_pack()
        s = slide(pack, "kid-1", 10)
        s["body"] = s["body"].replace("**אוהבת, רז**", "**אוהב, רז**")
        self.assertIn("ends with the signature line «**אוהבת, רז**»", messages(pack))

    def test_letter_opening_and_body_slides(self):
        pack = story_pack()
        slide(pack, "kid-1", 2)["headline"] = "אמא ואבא שלי,"
        slide(pack, "kid-1", 5)["headline"] = "רק דבר אחד"
        msgs = messages(pack)
        self.assertIn("a letter opens with the headline «אמא שלי,»", msgs)
        self.assertIn("kid-1/slide-5/headline: the letter's following slides have no headline", msgs)

    def test_thoughts_labels(self):
        pack = story_pack()
        slide(pack, "kid-4", 5)["label"] = "את חושבת:"
        slide(pack, "kid-4", 6)["headline"] = "נחזיר לו טיטול וזהו"
        msgs = messages(pack)
        self.assertIn("kid-4/slide-5/label: this thought slide is labelled «אתם חושבים:»", msgs)
        self.assertIn("kid-4/slide-6/headline: the headline is the parent's thought", msgs)

    def test_before_after_order(self):
        pack = story_pack()
        slide(pack, "kid-6", 4)["label"] = "ומאז"
        self.assertIn("before_after reads", messages(pack))

    def test_one_day_clock_goes_forward(self):
        pack = story_pack()
        slide(pack, "kid-5", 6)["label"] = "09:00, בסלון"
        self.assertIn("the clock goes forward", messages(pack))

    def test_one_minute_needs_the_start(self):
        pack = story_pack()
        slide(pack, "kid-2", 3)["label"] = "בלילה"
        self.assertIn("a slide labelled «הדקה מתחילה»", messages(pack))

    def test_short_list_three_to_five_points_and_shapes(self):
        pack = story_pack()
        slide(pack, "kid-3", 6)["label"] = "5: מילה טובה בבוקר"
        self.assertIn("the points are numbered 1, 2, 3", messages(pack))
        pack = story_pack()
        s = slide(pack, "kid-3", 5)
        s["body"] = "אני רוצה לבחור דובי משלי, רך וקטן.\n> ״אביב, בחרת חבר חדש למיטה.״\nאחד שאחבק בלילה במקום המוצץ."
        self.assertIn("neighbouring point slides look alike (both card)", messages(pack))

    def test_point_labels_only_in_a_short_list(self):
        pack = story_pack()
        slide(pack, "kid-6", 9)["label"] = "1: זה לא דווקא"
        self.assertIn("a numbered point label («1: זה לא דווקא») belongs to a short_list", messages(pack))


class Facts(unittest.TestCase):
    def test_a_help_slide_needs_its_claim(self):
        pack = story_pack()
        v = option(pack, "kid-4")
        v["claims"] = [c for c in v["claims"] if c["slide"] != 5]
        self.assertIn("slide 5 tells the parents what helps", messages(pack))

    def test_at_least_three_sourced_help_actions(self):
        pack = story_pack()
        v = option(pack, "kid-1")
        v["claims"] = [c for c in v["claims"] if c["slide"] in (3, 4, 11)]
        self.assertIn("at least 3 help actions backed by sources", messages(pack))


class VoiceStaysTheSame(unittest.TestCase):
    def test_dash_semicolon_and_brand_still_fail(self):
        pack = story_pack()
        s = slide(pack, "kid-5", 7)
        s["body"] = s["body"].replace("ואת לא כועסת. את מחבקת.", "ואת לא כועסת; את מחבקת - כמו לומבוק.")
        msgs = messages(pack)
        self.assertIn("semicolon", msgs)
        self.assertIn("hyphen", msgs)
        self.assertIn("never name the brand", msgs)

    def test_dad_and_all_children_still_fail(self):
        pack = story_pack()
        s = slide(pack, "kid-6", 3)
        s["body"] = s["body"].replace("סיפרת לסבתא בטלפון,", "אבא סיפר שכל הילדים ככה,")
        msgs = messages(pack)
        self.assertIn("never talk to dad", msgs)
        self.assertIn("every child feels the same", msgs)

    def test_the_bridge_line(self):
        pack = story_pack()
        v = option(pack, "kid-2")
        v["caption"] = v["caption"].replace("ובערב אפשר להמשיך עם סיפור שבו אני הגיבור", "ובערב נקרא סיפור ביחד")
        self.assertIn("the bridge line «ובערב אפשר להמשיך עם סיפור שבו אני הגיבור»", messages(pack))

    def test_the_cta_is_unchanged(self):
        pack = story_pack()
        v = option(pack, "kid-3")
        v["cta"] = "תשמרו את הפוסט\nלפעם הבאה שהוא מחפש את המוצץ"
        self.assertIn("the CTA talks to mom", messages(pack))


class NightlyStart(unittest.TestCase):
    def test_structures_keep_the_rules_and_rotate(self):
        recent = {"letter": 2, "one_day": 2, "thoughts_answers": 1}
        for date in ("2026-11-02", "2026-11-03", "2026-11-04"):
            a = story_lib.assign_structures(lib.PAIR_LANES, recent, seed=date)
            self.assertEqual(sorted(a), sorted(lib.PAIR_OPTION_IDS))
            self.assertEqual(story_lib.distribution_problems(a, lib.PAIR_LANES), [])
            self.assertNotIn("letter", a.values())
            self.assertNotIn("one_day", a.values())
        self.assertEqual(story_lib.assign_structures(lib.PAIR_LANES, {}, seed="2026-11-02"), story_lib.assign_structures(lib.PAIR_LANES, {}, seed="2026-11-02"))

    def test_start_context(self):
        history = {"packs": [{"date": "2026-11-01", "topic_id": "x", "options": [{"id": "kid-1", "hook_family": "story", "structure": "letter"}]}]}
        ctx = lib.rotation_context(history, "2026-11-02")
        self.assertEqual(ctx["recent_structures"], {"letter": 1})
        out = nightly.story_start_context(ctx, "2026-11-02", {"format": lib.PAIR_FORMAT})
        self.assertEqual(out["copy_style"], "story")
        self.assertNotIn("letter", out["structure_per_option"].values())
        self.assertNotIn("examples_per_option", out)
        self.assertEqual(out["rules"]["slides"], [9, 12])

    def test_history_records_the_structure(self):
        entry = lib.history_entry(story_pack())
        self.assertEqual({o["id"]: o["structure"] for o in entry["options"]}["kid-1"], "letter")


class VoiceLint(unittest.TestCase):
    def test_story_fields(self):
        body = slide(story_pack(), "kid-4", 2)["body"]
        self.assertTrue(any("max 25" in i.message for i in voice_lint.lint({"s2": body})))
        self.assertEqual([i.message for i in voice_lint.lint({"s2": body}, story=True) if i.level == "ERROR"], [])
        long_line = {"s3": body + "\nוזאת שורה ארוכה מאוד שלא תיכנס לשקופית בשום אופן"}
        self.assertTrue(any("max 38" in i.message for i in voice_lint.lint(long_line, story=True)))


if __name__ == "__main__":
    unittest.main()
