"""Two topics a day and the save and share CTA (Yarin, 24 Oct 2026, after the carousel audit): "Keep the child-voice
numbered lists, on 2 topics that have a best-selling book (6 versions for each day (3 options for each) so i can choose the
strongest one)" and "change the cta to save the post and share to a parent who would agree"."""

import copy
import datetime as dt
import json
import re
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
import compose_slides  # noqa: E402
import create_review  # noqa: E402
import grades  # noqa: E402
import validate_pack  # noqa: E402

FIXTURES = HERE / "fixtures"


def pair_pack():
    """A complete two-topic pack (pacifier + diapers), built from the 19 and 20 Oct packs."""
    return lib.read_json(FIXTURES / "two_topic_pack.json")


def errors(pack, **kw):
    return [i for i in validate_pack.pack_issues(pack, **kw) if i.level == "ERROR"]


def messages(pack, **kw):
    return " | ".join(i.message for i in errors(pack, **kw))


class TwoTopicPack(unittest.TestCase):
    def test_the_fixture_is_valid(self):
        self.assertEqual(errors(pair_pack()), [])

    def test_a_new_pack_must_have_two_topics(self):
        old = lib.read_json(FIXTURES / "valid_pack.json")
        old["generated_at"] = "2026-10-25T21:00:00+03:00"
        self.assertIn("packs from 24 Oct 2026 have two topics", messages(old))

    def test_older_packs_keep_their_rules(self):
        old = lib.read_json(FIXTURES / "valid_pack.json")
        self.assertNotIn("two topics", messages(old))
        self.assertNotIn("save the post", messages(old))

    def test_both_topics_need_a_best_selling_book(self):
        pack = pair_pack()
        pack["topics"][1]["id"] = "picky-eating"
        for v in pack["directions"][0]["versions"][3:]:
            v["topic_id"] = "picky-eating"
        self.assertIn("picky-eating has no best-selling book", messages(pack))

    def test_two_different_books(self):
        pack = pair_pack()
        pack["topics"][1].update({"id": "pacifier-first-nights", "book": {"id": 41, "title_he": "ביי ביי מוצץ"}})
        for v in pack["directions"][0]["versions"][3:]:
            v["topic_id"] = "pacifier-first-nights"
        self.assertIn("two different best-selling books", messages(pack))

    def test_the_book_must_match_the_topic(self):
        pack = pair_pack()
        pack["topics"][0]["book"]["id"] = 15
        self.assertIn("goes with book 41", messages(pack))

    def test_each_option_names_its_topic(self):
        pack = pair_pack()
        pack["directions"][0]["versions"][4]["topic_id"] = pack["topics"][0]["id"]
        self.assertIn("kid-5 is about topic 2", messages(pack))

    def test_one_kid_direction_only(self):
        pack = pair_pack()
        pack["directions"][0]["id"] = "expert"
        self.assertIn("one kid direction", messages(pack))

    def test_rotation_blocks_a_topic_of_the_last_three_packs(self):
        pack = pair_pack()
        history = {"packs": [{"date": "2026-10-24", "topic_id": "x", "topic_ids": ["birthday-at-gan", "toilet-setbacks"], "options": []}]}
        self.assertIn("toilet-setbacks was used in the previous 3 packs", messages(pack, history=history))


class SaveAndShareCTA(unittest.TestCase):
    def option(self, pack, oid="kid-1"):
        return next(v for v in pack["directions"][0]["versions"] if v["id"] == oid)

    def test_default_forms_pass(self):
        for who, form in lib.SAVE_SHARE_FORMS.items():
            self.assertEqual([i for i in lib.save_share_cta_issues("cta", form["text"], who) if i.level == "ERROR"], [], who)

    def test_the_comment_word_is_gone(self):
        pack = pair_pack()
        self.option(pack)["code_word"] = "לומי"
        self.assertIn("no comment word since 24 Oct 2026", messages(pack))

    def test_a_comment_cta_is_rejected(self):
        bad = 'כתבי "לומי" בתגובות וקבלי קישור ליצירת ספר שבו הילדה שלך היא הגיבורה'
        msgs = " | ".join(i.message for i in lib.save_share_cta_issues("cta", bad, "mom"))
        self.assertIn("save verb", msgs)
        self.assertIn("comment CTA", msgs)

    def test_the_addressee_form(self):
        msgs = " | ".join(i.message for i in lib.save_share_cta_issues("cta", lib.SAVE_SHARE_FORMS["parents"]["text"], "mom"))
        self.assertIn("talks to mom", msgs)

    def test_a_comment_request_in_the_caption_is_a_second_cta(self):
        pack = pair_pack()
        v = self.option(pack)
        lines = lib.lines_of(v["caption"])
        v["caption"] = "\n".join(lines[:-1] + ["ספרו לנו בתגובות מה עבד אצלכם", lines[-1]])
        self.assertIn("comment CTA", messages(pack))

    def test_the_story_line_is_fixed(self):
        pack = pair_pack()
        self.option(pack, "kid-2")["slides"][-1]["headline"] = "אפשר לעזור לו גם\nבסיפור אישי"
        self.assertIn("אפשר לעזור להם גם בסיפור אישי", messages(pack))

    def test_save_line_is_the_button(self):
        self.assertTrue(compose_slides.SAVE_LINE_RE.match("תשמרי את הפוסט"))
        self.assertTrue(compose_slides.SAVE_LINE_RE.match("תשמרו את הפוסט"))
        self.assertFalse(compose_slides.SAVE_LINE_RE.match("תשמורת"))

    def test_save_and_send_icons(self):
        # Yarin, 24 Oct 2026: "add default save and send icons"
        for who, form in lib.SAVE_SHARE_FORMS.items():
            save, send = lib.lines_of(form["text"])
            html = compose_slides.lines_html(form["text"], button=save)
            self.assertIn(compose_slides.SAVE_ICON, html, who)
            self.assertIn(compose_slides.SEND_ICON, html, who)
            self.assertLess(html.index(compose_slides.SAVE_ICON), html.index(compose_slides.SEND_ICON))
        old = compose_slides.lines_html('כתבו "לומי" בתגובות', button='כתבו "לומי" בתגובות')   # the comment button of older packs
        self.assertNotIn('class="ic"', old)


class SwitchedOlderPack(unittest.TestCase):
    """The week of 25 Oct was written before the change and switched to the new last slide (cta_style save_share)."""

    def switched(self):
        pack = lib.read_json(FIXTURES / "valid_pack.json")
        pack["cta_style"] = lib.SAVE_SHARE_STYLE
        for d in pack["directions"]:
            for v in d["versions"]:
                cta = lib.SAVE_SHARE_FORMS[v["addressee"]]["text"]
                v.pop("code_word", None)
                v["cta"] = cta
                v["slides"][-1].update({"headline": lib.STORY_LINE, "highlight": lib.STORY_LINE_HIGHLIGHT, "body": cta})
                v["caption"] = "\n".join(lib.lines_of(v["caption"])[:-1] + [lib.collapse(cta)])
        return pack

    def test_the_new_cta_is_accepted(self):
        msgs = messages(self.switched())
        for old_rule in ("code word", "כתבו or כתבי", "two topics", "save the post"):
            self.assertNotIn(old_rule, msgs)

    def test_the_comment_cta_is_not(self):
        pack = self.switched()
        pack["directions"][0]["versions"][0]["code_word"] = "לומי"
        self.assertIn("no comment word", messages(pack))


class ChildVoiceOnly(unittest.TestCase):
    def test_an_option_not_in_the_childs_voice_fails(self):
        pack = pair_pack()
        v = pack["directions"][0]["versions"][0]
        for s in v["slides"][:5]:
            s["headline"] = re.sub(lib.FIRST_PERSON_RE, "", s["headline"])
            s["body"] = re.sub(lib.FIRST_PERSON_RE, "", s["body"])
        self.assertIn("child's voice", messages(pack))


class History(unittest.TestCase):
    def test_both_topics_are_recorded_and_rotated(self):
        entry = lib.history_entry(pair_pack())
        self.assertEqual(entry["topic_ids"], ["pacifier-weaning", "toilet-setbacks"])
        self.assertEqual(entry["code_words"], [])
        ctx = lib.rotation_context({"packs": [entry]}, "2026-10-26")
        self.assertIn("toilet-setbacks", ctx["recent_pair_topic_ids"])
        last = {t["id"]: t["last_used"] for t in ctx["topics"]}
        self.assertEqual(last["toilet-setbacks"], "2026-10-25")


class PairPlan(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pair-test-"))
        drafts = self.tmp / "drafts"
        drafts.mkdir()
        self.patches = [mock.patch.object(lib, "DRAFTS", drafts), mock.patch.object(lib, "HISTORY", self.tmp / "history.json"),
                        mock.patch.object(batch, "BATCHES", drafts / "batches")]
        for p in self.patches:
            p.start()
        lib.write_json(lib.HISTORY, {"packs": [{"date": "2026-10-24", "topic_id": "pacifier-weaning", "options": []}]})

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_week_of_two_best_seller_topics_a_day(self):
        plan = batch.make_plan(today=dt.date(2026, 10, 29), merge=False, log=lambda *_: None)
        self.assertEqual(plan["format"], lib.PAIR_FORMAT)
        self.assertEqual(len(plan["slots"]), 7)
        bank = {t["id"]: t for t in lib.load_topic_bank()}
        seen, per_book = set(), {}
        for s in plan["slots"]:
            self.assertEqual(s["kind"], "pair")
            ids = [t["topic_id"] for t in s["topics"]]
            books = [bank[t]["bestseller"]["book"] for t in ids]
            self.assertEqual(len(set(books)), 2, s)
            self.assertEqual([t["options"] for t in s["topics"]], [list(ids) for _, ids in lib.PAIR_LANES])
            for t, b in zip(ids, books):
                self.assertNotIn(t, seen)
                seen.add(t)
                per_book[b] = per_book.get(b, 0) + 1
        self.assertEqual(len(seen), 14)
        self.assertLessEqual(max(per_book.values()), lib.PAIR_BOOK_MAX_IN_BATCH)
        self.assertNotIn("pacifier-weaning", {t["topic_id"] for t in plan["slots"][0]["topics"]})  # used the day before

    def test_older_plans_stay_one_topic(self):
        plan = batch.make_plan(today=dt.date(2026, 10, 16), merge=False, log=lambda *_: None)
        self.assertNotEqual(plan.get("format"), lib.PAIR_FORMAT)

    def test_items_carry_each_options_topic(self):
        plan = batch.make_plan(today=dt.date(2026, 10, 29), merge=False, log=lambda *_: None)
        slot = plan["slots"][0]
        pack = pair_pack()
        pack["date"] = slot["date"]
        folder = lib.DRAFTS / slot["date"]
        folder.mkdir(parents=True)
        lib.write_json(folder / "pack.json", pack)
        its = [i for i in grades.items(plan) if i["date"] == slot["date"]]
        self.assertEqual(len(its), 6)
        self.assertEqual({i["topic_id"] for i in its[:3]}, {"pacifier-weaning"})
        self.assertEqual({i["topic_id"] for i in its[3:]}, {"toilet-setbacks"})
        self.assertEqual([i["lane"] for i in its], ["a"] * 3 + ["b"] * 3)
        self.assertEqual(len(its[0]["day_topics"]), 2)


class ReviewPage(unittest.TestCase):
    def test_the_review_page_builds(self):
        tmp = Path(tempfile.mkdtemp(prefix="pair-review-"))
        try:
            path = tmp / "pack.json"
            lib.write_json(path, pair_pack())
            html_path, md_path = create_review.write_review(path)
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("kid-6", html)
            self.assertIn("פספוסים אחרי גמילה", html)
            self.assertEqual(create_review.rtl_issues(html), [])
            self.assertIn("שמירה ושליחה", md_path.read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class PicturePrompt(unittest.TestCase):
    def test_the_text_zone_is_light(self):
        self.assertIn("never dark, blue", lib.text_zone_sentence({"edge": "top", "percent": 45}))


class GenderBalance(unittest.TestCase):
    """Yarin, 24 Oct 2026: "make sure the carousel machine do 50/50 boys and girls"."""

    def new_pack(self, genders):
        pack = pair_pack()
        pack["generated_at"] = "2026-10-29T22:00:00+03:00"
        for v in pack["directions"][0]["versions"]:
            v["child_gender"] = genders[v["id"]]
        return pack

    def test_the_slots_are_half_and_half_and_flip_daily(self):
        a, b = lib.gender_slots("2026-10-31"), lib.gender_slots("2026-11-01")
        for slots in (a, b):
            self.assertEqual(sorted(slots.values()).count("girl"), 3)
            for _, ids in lib.PAIR_LANES:
                self.assertEqual({slots[i] for i in ids}, {"girl", "boy"})
        self.assertNotEqual(a["kid-1"], b["kid-1"])

    def test_a_pack_written_from_the_slots_passes(self):
        self.assertEqual(lib.gender_balance_issues(self.new_pack(lib.gender_slots("2026-10-29"))), [])

    def test_four_girls_is_an_error(self):
        genders = dict(lib.gender_slots("2026-10-29"), **{"kid-2": "girl", "kid-4": "girl", "kid-6": "girl"})
        self.assertIn("half girls and half boys", " ".join(i.message for i in lib.gender_balance_issues(self.new_pack(genders))))

    def test_each_topic_needs_both(self):
        genders = {"kid-1": "girl", "kid-2": "girl", "kid-3": "girl", "kid-4": "boy", "kid-5": "boy", "kid-6": "boy"}
        self.assertIn("topic a", " ".join(i.message for i in lib.gender_balance_issues(self.new_pack(genders))))

    def test_older_packs_keep_their_rules(self):
        self.assertEqual(lib.gender_balance_issues(pair_pack()), [])


if __name__ == "__main__":
    unittest.main()


def later_pack():
    """The fixture as a pack written after the evening of 24 Oct 2026: slide 10 is only the save for later CTA, and the
    new punctuation rule holds (its few ו-N hyphens dropped the way the week of 25 Oct was moved)."""
    pack = pair_pack()
    pack["generated_at"] = "2026-10-24T22:00:00+03:00"

    def unhyphen(text):
        return re.sub(r"(?<![A-Za-z])(?:ו|ב)?[-־](?=\d)", "", text)
    for cands in pack["hook_slate"].values():
        for c in cands:
            for field in ("hook", "slide2"):
                c[field] = unhyphen(c.get(field, ""))
    for v in pack["directions"][0]["versions"]:
        for s in v["slides"]:
            s["headline"], s["body"] = unhyphen(s["headline"]), unhyphen(s.get("body", ""))
        kid = "שהוא מתעורר בלילה" if v["child_gender"] == "boy" else "שהיא מתעוררת בלילה"
        cta = lib.SAVE_LATER_FORMS[v["addressee"]]["save"] + "\nלפעם הבאה " + kid
        last = v["slides"][-1]
        last["headline"], last["body"] = lib.save_later_slide(cta)
        last.pop("highlight", None)
        lines = [ln for ln in lib.lines_of(v["caption"]) if lib.collapse(ln) != lib.collapse(v["cta"])]
        v["caption"], v["cta"] = "\n".join(lines + [lib.collapse(cta)]), cta
    return pack


class SaveForLaterCTA(unittest.TestCase):
    """Yarin, 24 Oct 2026 (evening): "remove אפשר לעזור להם גם בסיפור אישי from the cta" and "i want the cta to change,
    'תשמרו את הפוסט לפעם הבאה שX'"."""

    def option(self, pack, oid="kid-1"):
        return next(v for v in pack["directions"][0]["versions"] if v["id"] == oid)

    def test_a_new_pack_passes(self):
        self.assertEqual(errors(later_pack()), [])

    def test_the_story_line_is_gone(self):
        pack = later_pack()
        v = self.option(pack)
        v["slides"][-1]["headline"] = lib.STORY_LINE
        v["slides"][-1]["body"] = lib.collapse(v["cta"])
        self.assertIn("slide 10 is only the CTA", messages(pack))

    def test_the_moment_is_required(self):
        pack = later_pack()
        v = self.option(pack)
        v["cta"] = "תשמרי את הפוסט"
        self.assertIn("לפעם הבאה ש", messages(pack))

    def test_the_addressee_form(self):
        msgs = " | ".join(i.message for i in lib.save_later_cta_issues("cta", "תשמרו את הפוסט\nלפעם הבאה שזה קורה", "mom"))
        self.assertIn("talks to mom", msgs)

    def test_a_send_request_is_a_second_cta(self):
        msgs = " | ".join(i.message for i in lib.save_later_cta_issues("cta", "תשמרו את הפוסט לפעם הבאה שזה קורה ותשלחו לאמא", "parents"))
        self.assertIn("second CTA", msgs)

    def test_the_moment_is_about_the_kid(self):
        # Yarin, 24 Oct 2026: "always refer to the kid"
        msgs = " | ".join(i.message for i in lib.save_later_cta_issues("cta", "תשמרי את הפוסט לפעם הבאה שיש סופה", "mom", gender="girl"))
        self.assertIn("always about the child", msgs)
        for ok in ("תשמרי את הפוסט לפעם הבאה שהיא מפחדת מרעמים", "תשמרי את הפוסט לפעם הבאה שיש לה יום הולדת",
                   "תשמרי את הפוסט לפעם הבאה שלא משתפים אותה", "תשמרי את הפוסט לפעם הבאה שנועה מפחדת"):
            self.assertEqual([i for i in lib.save_later_cta_issues("cta", ok, "mom", gender="girl", child_name="נועה") if i.level == "ERROR"], [], ok)
        msgs = " | ".join(i.message for i in lib.save_later_cta_issues("cta", "תשמרי את הפוסט לפעם הבאה שהיא מפחדת", "mom", gender="boy"))
        self.assertIn("הוא, לו, אותו", msgs)

    def test_the_moment_is_short_not_a_scene(self):
        # Yarin, 24 Oct 2026: the per-option scenes were "too specific" and did not "sound natural"
        msgs = " | ".join(i.message for i in lib.save_later_cta_issues("cta", "תשמרי את הפוסט לפעם הבאה שהיא מתפרקת באמצע חגיגה גדולה בגן", "mom", gender="girl"))
        self.assertIn("not a scene", msgs)

    def test_one_line_per_topic(self):
        pack = later_pack()
        v, other = self.option(pack, "kid-2"), self.option(pack, "kid-3")
        self.assertEqual((v["child_gender"], other["child_gender"], v["topic_id"]), ("boy", "boy", other["topic_id"]))
        self.assertNotIn("ends the CTA the same way", messages(pack))
        cta = lib.SAVE_LATER_FORMS[v["addressee"]]["save"] + "\nלפעם הבאה שהוא בוכה בגן"
        v["slides"][-1]["headline"], v["slides"][-1]["body"] = lib.save_later_slide(cta)
        v["caption"] = "\n".join(lib.lines_of(v["caption"])[:-1] + [lib.collapse(cta)])
        v["cta"] = cta
        self.assertIn("ends the CTA the same way", messages(pack))

    def test_a_quoted_moment(self):
        self.assertEqual([i for i in lib.save_later_cta_issues("cta", "תשמרו את הפוסט\nלפעם הבאה ש״זה רק חלום״ לא מספיק", "parents") if i.level == "ERROR"], [])

    def test_the_slide_keeps_the_moment_whole(self):
        self.assertEqual(lib.save_later_slide("תשמרי את הפוסט לפעם הבאה שהוא לא ניגש לילדים חדשים"),
                         ("תשמרי את הפוסט", "לפעם הבאה\nשהוא לא ניגש לילדים חדשים"))
        self.assertEqual(lib.save_later_slide("תשמרי את הפוסט לפעם הבאה שיש סופה"), ("תשמרי את הפוסט", "לפעם הבאה שיש סופה"))

    def test_the_save_line_is_the_button(self):
        html = compose_slides.lines_html("תשמרי את הפוסט", button="תשמרי את הפוסט")
        self.assertIn('class="btn"', html)
        self.assertIn(compose_slides.SAVE_ICON, html)

    def test_editing_the_cta_rebuilds_slide_10(self):
        import review_server
        pack = later_pack()
        review_server.apply_edits(pack, [{"option": "kid-1", "field": "cta", "value": "תשמרי את הפוסט לפעם הבאה שהיא מתעוררת בבכי"}])
        last = self.option(pack)["slides"][-1]
        self.assertEqual((last["headline"], last["body"]), ("תשמרי את הפוסט", "לפעם הבאה שהיא מתעוררת בבכי"))
        self.assertEqual(lib.lines_of(self.option(pack)["caption"])[-1], "תשמרי את הפוסט לפעם הבאה שהיא מתעוררת בבכי")
        with self.assertRaises(ValueError):
            review_server.apply_edits(pack, [{"option": "kid-1", "field": "headline", "slide": 10, "value": "משהו אחר לגמרי"}])


class Punctuation(unittest.TestCase):
    """Yarin, 24 Oct 2026: "lets bring back punctuation marks except em dashes, semicolon and hyphens"."""

    def chars(self, text, **kw):
        return {i.message for i in lib.forbidden_char_issues("t", text, **kw)}

    def test_punctuation_is_back(self):
        self.assertEqual(self.chars("זה מוכר, וזה עובר. באמת? כן! ככה: ״לאט״…"), set())

    def test_dashes_semicolons_and_hyphens_stay_out(self):
        for ch in ("—", "–", "-", "־", ";", "；"):
            self.assertTrue(self.chars(f"זה מוכר{ch} וזה עובר"), ch)

    def test_older_packs_keep_their_rule(self):
        self.assertTrue(self.chars("זה מוכר, וזה עובר.", legacy=True))
        self.assertEqual(self.chars("בגיל 3-6", legacy=True), set())

    def test_the_gate(self):
        self.assertFalse(lib.punctuation_rule_applies(pair_pack()))
        self.assertTrue(lib.punctuation_rule_applies(later_pack()))
        old = pair_pack()
        old["cta_style"] = lib.SAVE_LATER_STYLE
        self.assertTrue(lib.punctuation_rule_applies(old))

    def test_a_new_pack_with_a_comma_passes(self):
        pack = later_pack()
        v = pack["directions"][0]["versions"][0]
        v["slides"][1]["body"] = v["slides"][1]["body"].split("\n")[0] + ", באמת"
        self.assertNotIn("comma", messages(pack))


class SlideLook(unittest.TestCase):
    def test_a_one_picture_carousel_is_clean_without_highlights(self):
        v = copy.deepcopy(later_pack()["directions"][0]["versions"][0])
        for s in v["slides"]:
            s.pop("highlight", None)
        self.assertEqual(compose_slides.choose_look(None, None, v), "clean")
        self.assertEqual(compose_slides.choose_look(None, "classic", v), "clean")   # the 24 Oct mistake does not stick
        self.assertEqual(compose_slides.choose_look(None, "bold", v), "bold")
        self.assertEqual(compose_slides.choose_look("classic", None, v), "classic")
