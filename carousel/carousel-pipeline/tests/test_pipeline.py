#!/usr/bin/env python3
"""Tests for the LumeBook carousel pipeline. Standard library only.

    python3 -m unittest discover -s carousel/carousel-pipeline/tests -v

The final-renderer test needs Google Chrome and is skipped without it.
No test touches the network or the real drafts, approved runs or history.
"""

import copy
import hashlib
import io
import json
import re
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import carousel_lib as lib  # noqa: E402
import compose_slides  # noqa: E402
import create_review  # noqa: E402
import prepare_picture_jobs  # noqa: E402
import review_server  # noqa: E402
import validate_pack  # noqa: E402
import voice_lint  # noqa: E402

FIXTURE = HERE / "fixtures" / "valid_pack.json"
VOICE0 = {"status": "fallback", "approved_samples": 0, "required": 15, "from_profile": 0, "from_examples_folder": 0}


def load():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def errors(pack, history=None, voice=VOICE0):
    return [i for i in validate_pack.pack_issues(pack, history=history, voice=voice) if i.level == "ERROR"]


def version(pack, option_id):
    for d in pack["directions"]:
        for v in d["versions"]:
            if v["id"] == option_id:
                return v
    raise KeyError(option_id)


class NoNetwork:
    """Fail loudly if anything tries to open a connection."""

    def __enter__(self):
        def boom(*a, **k):
            raise AssertionError("network access attempted")
        self.patches = [mock.patch.object(urllib.request, "urlopen", boom), mock.patch.object(socket.socket, "connect", boom)]
        for p in self.patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self.patches:
            p.stop()


class ValidatorHardRules(unittest.TestCase):
    def test_fixture_is_valid(self):
        self.assertEqual(errors(load()), [])

    def test_fixture_shape(self):
        pack = load()
        self.assertEqual([d["id"] for d in pack["directions"]], ["kid", "expert"])
        self.assertEqual(sum(len(v["slides"]) for d in pack["directions"] for v in d["versions"]), 6 * lib.SLIDE_COUNT)

    def test_em_dash_reports_field_line_column_and_char(self):
        pack = load()
        v = version(pack, "kid-2")
        v["slides"][2]["body"] = "התרגלתי להיות איתך בבית — ושכחתי"
        errs = errors(pack)
        hit = [e for e in errs if e.char == "—"]
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0].path, "kid/kid-2/slide-3/body")
        self.assertEqual((hit[0].line, hit[0].col), (1, 25))
        self.assertIn("U+2014", str(hit[0]))

    def test_period_in_caption(self):
        pack = load()
        v = version(pack, "expert-1")
        v["caption"] = v["caption"].replace("נראה כמו הדבר החם לעשות", "נראה כמו הדבר החם לעשות.")
        hit = [e for e in errors(pack) if e.char == "."]
        self.assertTrue(hit)
        self.assertEqual(hit[0].path, "expert/expert-1/caption")

    def test_comma_in_headline(self):
        pack = load()
        version(pack, "kid-1")["slides"][0]["headline"] = "אני לא בוכה, בגלל הגן"
        hit = [e for e in errors(pack) if e.char == ","]
        self.assertEqual(hit[0].path, "kid/kid-1/slide-1/headline")

    def test_comma_in_cta(self):
        pack = load()
        v = version(pack, "kid-3")
        bad = v["cta"].replace("בתגובות", "בתגובות,")
        v["cta"] = bad
        self.assertTrue(any(e.char == "," and e.path.endswith("/cta") for e in errors(pack)))

    def test_lookalike_dashes_and_commas(self):
        for ch in ("–", "…", "，", "―"):
            pack = load()
            version(pack, "expert-2")["slides"][3]["headline"] = f"״בארבע״ עוד לא{ch} אומר לו הרבה"
            self.assertTrue(any(e.char == ch for e in errors(pack)), ch)

    def test_validator_never_edits_the_file(self):
        tmp = Path(tempfile.mkdtemp())
        pack = load()
        version(pack, "kid-1")["slides"][0]["headline"] = "אני לא בוכה, בגלל הגן."
        path = tmp / "pack.json"
        path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        res = subprocess.run([sys.executable, str(SCRIPTS / "validate_pack.py"), str(path), "--no-history"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("U+002C", res.stdout)
        self.assertIn("U+002E", res.stdout)
        self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_missing_hebrew(self):
        pack = load()
        version(pack, "expert-3")["slides"][1]["headline"] = "Her fear is real"
        self.assertTrue(any("must contain Hebrew" in e.message and e.path == "expert/expert-3/slide-2/headline" for e in errors(pack)))

    def test_missing_slide(self):
        pack = load()
        del version(pack, "kid-2")["slides"][4]
        msgs = [str(e) for e in errors(pack)]
        self.assertTrue(any(f"needs at least {lib.SLIDE_COUNT} items" in m for m in msgs), msgs)

    def test_wrong_slide_order(self):
        pack = load()
        v = version(pack, "kid-2")
        v["slides"][0]["number"], v["slides"][1]["number"] = 2, 1
        self.assertTrue(any(f"numbered 1 to {lib.SLIDE_COUNT}" in e.message for e in errors(pack)))

    def test_repeated_option_ids(self):
        pack = load()
        version(pack, "kid-2")["id"] = "kid-1"
        self.assertTrue(any("duplicate option id kid-1" in e.message for e in errors(pack)))

    def test_three_versions_per_direction(self):
        pack = load()
        pack["directions"][1]["versions"].pop()
        self.assertTrue(any("allows at most" in e.message or "needs at least 3" in e.message for e in errors(pack)))

    def test_missing_expert_sources(self):
        pack = load()
        v = version(pack, "expert-1")
        v["sources"] = []
        msgs = [str(e) for e in errors(pack)]
        self.assertTrue(any("needs at least 1 items" in m for m in msgs))
        self.assertTrue(any("unknown source id" in m for m in msgs))

    def test_expert_needs_a_sourced_fact(self):
        pack = load()
        v = version(pack, "expert-2")
        v["claims"] = [c for c in v["claims"] if c["kind"] != "sourced_fact"]
        self.assertTrue(any("at least one sourced fact" in e.message for e in errors(pack)))

    def test_product_fact_must_exist(self):
        pack = load()
        version(pack, "kid-1")["claims"][-1]["source_ids"] = ["site-made-up"]
        self.assertTrue(any("unknown product fact id" in e.message for e in errors(pack)))

    def test_stale_product_facts(self):
        pack = load()
        pack["product_facts"][0]["checked_at"] = "2026-09-01"
        self.assertTrue(any("re-check the live site" in e.message for e in errors(pack)))

    def test_hook_word_limits(self):
        pack = load()
        version(pack, "kid-1")["slides"][0]["headline"] = "אני לא בוכה בגלל הגן ולא בגלל הגננת שלי"
        self.assertTrue(any("hook main line" in e.message for e in errors(pack)))

    def test_headline_line_too_wide_for_the_slide(self):
        pack = load()
        version(pack, "expert-3")["slides"][2]["headline"] = "השבוע אחרי החגים היא שוב בוכה בבוקר"
        self.assertTrue(any("will not fit the slide" in e.message for e in errors(pack)))

    def test_regular_slide_word_limit(self):
        pack = load()
        version(pack, "kid-1")["slides"][3]["body"] = "\n".join(["אני בעצם שואל מתי את חוזרת היום"] * 4)
        self.assertTrue(any("max 25" in e.message for e in errors(pack)))

    def test_cta_must_match_caption_last_line_and_slide_8(self):
        pack = load()
        v = version(pack, "kid-1")
        v["caption"] = v["caption"] + "\nתודה שקראתם"
        self.assertTrue(any("final line must be exactly the CTA" in e.message for e in errors(pack)))
        pack = load()
        version(pack, "kid-1")["slides"][lib.CTA_SLIDE - 1]["body"] = "כתבו לב בתגובות"
        self.assertTrue(any(f"slide {lib.CTA_SLIDE} must contain the exact CTA" in e.message for e in errors(pack)))

    def test_second_cta_is_rejected(self):
        pack = load()
        v = version(pack, "expert-1")
        lines = v["caption"].split("\n")
        lines.insert(-1, "ושמרו את הפוסט לבוקר")
        v["caption"] = "\n".join(lines)
        self.assertTrue(any("second CTA" in e.message for e in errors(pack)))

    def test_cta_keeps_the_brief_idea(self):
        pack = load()
        v = version(pack, "kid-1")
        new = "כתבו לב בתגובות ונשלח לכם משהו נחמד"
        v["cta"] = new
        msgs = [e.message for e in errors(pack)]
        self.assertTrue(any("קישור" in m for m in msgs))

    def test_diagnosis_guarantee_and_universal_words(self):
        for line in ("זו חרדת פרידה", "בלי דמעות תוך שבוע", "כל הילדים מרגישים ככה", "בספר של לומבוק"):
            pack = load()
            version(pack, "expert-1")["slides"][3]["body"] = line
            self.assertTrue(errors(pack), line)

    def test_carousel_never_names_the_brand(self):
        for text in ("בספר של לומיבוק", "LumeBook", "lumebook", "ספר של לומבוק"):
            pack = load()
            version(pack, "kid-1")["slides"][6]["body"] = text
            self.assertTrue(any("never name the brand" in e.message for e in errors(pack)), text)
        pack = load()
        v = version(pack, "expert-1")
        lines = v["caption"].split("\n")
        lines.insert(-1, "ובלומבוק יש ספר כזה")
        v["caption"] = "\n".join(lines)
        self.assertTrue(any("never name the brand" in e.message and e.path.endswith("caption") for e in errors(pack)))

    def test_carousel_never_names_a_catalogue_book(self):
        pack = load()
        version(pack, "kid-2")["slides"][6]["body"] = "בספר ״לב האומץ״\nאני הגיבורה"
        self.assertTrue(any("never name a catalogue book" in e.message for e in errors(pack)))
        pack = load()
        version(pack, "kid-2")["slides"][2]["body"] = "כשיש אח חדש בבית"  # the generic phrase is fine
        self.assertEqual(errors(pack), [])

    def test_last_slide_suggests_a_personalised_story(self):
        pack = load()
        version(pack, "expert-1")["slides"][lib.CTA_SLIDE - 1]["headline"] = "ועוד דרך לעזור לה"
        self.assertTrue(any("personalised story" in e.message for e in errors(pack)))

    def test_nothing_before_the_last_slide_prepares_a_sale(self):
        for text in ("ספר שבו הוא הגיבור", "סיפור אישי עליו", "הקישור בתגובות"):
            pack = load()
            version(pack, "kid-1")["slides"][lib.RESOLUTION_SLIDE - 1]["body"] = text
            self.assertTrue(any("prepares a sale" in e.message for e in errors(pack)), text)

    def test_every_slide_before_the_cta_pulls_to_the_next(self):
        pack = load()
        version(pack, "kid-1")["slides"][3].pop("pull")
        self.assertTrue(any("needs a pull" in e.message for e in errors(pack)))
        pack = load()
        version(pack, "kid-1")["slides"][2]["pull"] = {"type": "question", "note": "asks something"}
        self.assertTrue(any("no question" in e.message for e in errors(pack)))

    def test_arc_roles(self):
        pack = load()
        version(pack, "kid-2")["slides"][lib.SOLUTION_SLIDES[0] - 1]["role"] = "reframe"
        self.assertTrue(any(f"slide {lib.SOLUTION_SLIDES[0]} must be solution" in e.message for e in errors(pack)))
        pack = load()
        version(pack, "kid-2")["slides"][lib.RESOLUTION_SLIDE - 1]["role"] = "solution"
        self.assertTrue(any(f"slide {lib.RESOLUTION_SLIDE} must be resolution" in e.message for e in errors(pack)))

    def test_solution_must_carry_sourced_value(self):
        pack = load()
        v = version(pack, "expert-2")
        v["claims"] = [c for c in v["claims"] if c["slide"] != lib.SOLUTION_SLIDES[-1]]
        self.assertTrue(any("every solution slide" in e.message for e in errors(pack)))

    def test_hook_must_come_from_the_bank_and_fit(self):
        pack = load()
        version(pack, "kid-1")["hook"]["formula"] = "made-up-formula"
        self.assertTrue(any("not in hook-bank.md" in e.message for e in errors(pack)))
        pack = load()
        version(pack, "kid-1")["hook"]["formula"] = "reversal"  # an expert formula
        msgs = [e.message for e in errors(pack)]
        self.assertTrue(any("is a expert formula" in m for m in msgs))
        self.assertTrue(any("belongs to family" in m for m in msgs))

    def test_hook_score_must_pass(self):
        pack = load()
        version(pack, "expert-2")["hook"]["score"].update({"specific": 0, "feeling": 1})
        self.assertTrue(any("rewrite it" in e.message for e in errors(pack)))

    def test_hook_payoff_and_gap(self):
        pack = load()
        version(pack, "kid-3")["hook"]["payoff_slide"] = 10
        self.assertTrue(any("which slide" in e.message for e in errors(pack)))

    def test_banned_hook_openers(self):
        pack = load()
        version(pack, "expert-1")["slides"][0]["headline"] = "חובה לראות מה קורה בשער"
        self.assertTrue(any("banned hook opener" in e.message for e in errors(pack)))

    def test_each_option_uses_its_own_formula(self):
        pack = load()
        version(pack, "expert-3")["hook"]["formula"] = "reversal"
        version(pack, "expert-3")["hook_family"] = "reframe"
        self.assertTrue(any("used 2 times" in e.message for e in errors(pack)))

    def test_hook_bank_rows(self):
        bank = lib.load_hook_bank()
        self.assertGreaterEqual(len(bank), 12)
        for f in bank.values():
            self.assertIn(f["family"], lib.HOOK_FAMILIES)
            self.assertIn(f["direction"], ("kid", "expert", "both"))

    def test_never_dad(self):
        for text in ("ואז אבא הולך", "אתה הולך באמת", "בוא נמציא ביי"):
            pack = load()
            version(pack, "kid-1")["slides"][1]["body"] = text
            self.assertTrue(any("never talk to dad" in e.message for e in errors(pack)), text)

    def test_cta_matches_the_addressee(self):
        pack = load()
        v = version(pack, "kid-1")  # talks to mom
        plural = "כתבו לב בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור"
        v["caption"] = v["caption"].replace(v["cta"], plural)
        v["slides"][lib.CTA_SLIDE - 1]["body"] = plural
        v["cta"] = plural
        self.assertTrue(any("must talk to mom" in e.message for e in errors(pack)))

    def test_child_name_rules(self):
        pack = load()
        version(pack, "kid-1")["child_name"] = "גיורגי"
        self.assertTrue(any("not a boy name in names.md" in e.message for e in errors(pack)))
        pack = load()
        version(pack, "kid-2")["child_name"] = "נועה"  # a valid girl name that never appears on the slides
        self.assertTrue(any("use the name at least once" in e.message for e in errors(pack)))
        pack = load()
        version(pack, "expert-2")["child_name"] = version(pack, "kid-1")["child_name"]
        self.assertTrue(any("is used 2 times" in e.message for e in errors(pack)))
        self.assertTrue(set(lib.load_names()["boy"]) and set(lib.load_names()["girl"]))

    def test_image_anchor_follows_the_addressee(self):
        pack = load()
        version(pack, "kid-1")["character_anchor"]["parent"] = "His father, early thirties, short dark hair."
        self.assertTrue(any("mother only" in e.message for e in errors(pack)))

    def test_competitor_code_word_is_blocked(self):
        pack = load()
        v = version(pack, "kid-3")
        v["code_word"] = "ספר"
        self.assertTrue(any("MeBook" in e.message for e in errors(pack)))

    def test_invented_authority(self):
        pack = load()
        version(pack, "expert-1")["slides"][3]["body"] = "ד״ר כהן אומרת\nשהבכי עובר"
        self.assertTrue(any("authority theater" in e.message for e in errors(pack)))

    def test_voice_cannot_claim_calibrated_without_samples(self):
        pack = load()
        pack["voice"]["status"] = "calibrated"
        self.assertTrue(any("claims calibrated" in e.message for e in errors(pack)))

    def test_hook_family_max_twice_per_pack(self):
        pack = load()
        for vid in ("kid-1", "kid-2", "kid-3"):
            version(pack, vid)["hook_family"] = "moment"
        self.assertTrue(any("used 3 times" in e.message for e in errors(pack)))


class Rotation(unittest.TestCase):
    def history(self, **entry):
        base = {"date": "2026-10-01", "topic_id": "fear-of-dark", "code_words": [], "hooks": [], "options": [], "selected": []}
        base.update(entry)
        return {"packs": [base]}

    def test_topic_used_in_previous_14_packs(self):
        pack = load()
        h = self.history(topic_id="gan-separation")
        self.assertTrue(any("previous 14 packs" in e.message for e in errors(pack, history=h)))

    def test_same_date_rerun_is_not_a_repeat(self):
        pack = load()
        h = self.history(date=pack["date"], topic_id=pack["topic"]["id"], code_words=["לב"], hooks=["אני לא בוכה בגלל הגן"])
        self.assertEqual(errors(pack, history=h), [])

    def test_code_word_cooldown(self):
        pack = load()
        h = self.history(code_words=["לב"])
        self.assertTrue(any("was used in the last 14 days" in e.message for e in errors(pack, history=h)))

    def test_hook_family_blocked_after_two_selections(self):
        pack = load()
        opts = [{"id": "kid-1", "hook_family": "moment", "code_word": "x", "title": "t"}]
        h = {"packs": [
            {"date": "2026-10-03", "topic_id": "fear-of-dark", "code_words": [], "hooks": [], "options": opts, "selected": ["kid-1"]},
            {"date": "2026-10-05", "topic_id": "new-sibling", "code_words": [], "hooks": [], "options": opts, "selected": ["kid-1"]},
        ]}
        self.assertTrue(any("published twice" in e.message for e in errors(pack, history=h)))

    def test_record_history_is_idempotent(self):
        tmp = Path(tempfile.mkdtemp()) / "history.json"
        pack = load()
        lib.record_history(pack, tmp)
        lib.record_history(pack, tmp)
        data = json.loads(tmp.read_text(encoding="utf-8"))
        self.assertEqual(len(data["packs"]), 1)
        self.assertEqual(len(data["packs"][0]["options"]), 6)
        self.assertTrue(lib.mark_selected(pack["date"], "kid-2", tmp))
        lib.record_history(pack, tmp)  # rerun keeps the selection
        self.assertEqual(json.loads(tmp.read_text(encoding="utf-8"))["packs"][0]["selected"], ["kid-2"])

    def test_review_date(self):
        import datetime as dt
        tz = dt.timezone(dt.timedelta(hours=3))
        self.assertEqual(str(lib.review_date_for(dt.datetime(2026, 10, 7, 22, 0, tzinfo=tz))), "2026-10-08")
        self.assertEqual(str(lib.review_date_for(dt.datetime(2026, 10, 8, 1, 30, tzinfo=tz))), "2026-10-08")

    def test_backup_before_overwrite(self):
        folder = Path(tempfile.mkdtemp())
        (folder / "pack.json").write_text("{}", encoding="utf-8")
        (folder / "review.html").write_text("x", encoding="utf-8")
        first = lib.backup_existing(folder)
        (folder / "pack.json").write_text("{}", encoding="utf-8")
        second = lib.backup_existing(folder)
        self.assertEqual((first.name, second.name), ("v1", "v2"))
        self.assertTrue((first / "review.html").exists())
        self.assertFalse((folder / "pack.json").exists())


SAMPLE_SLATE = HERE / "fixtures" / "sample_slate_gan_separation.json"


def load_v3():
    """The valid fixture as a schema_version 3 pack: the same six options plus the sample hook slate."""
    pack = load()
    sample = json.loads(SAMPLE_SLATE.read_text(encoding="utf-8"))
    pack["schema_version"] = 3
    pack["hook_slate"] = sample["hook_slate"]
    for d in pack["directions"]:
        for v in d["versions"]:
            v["hook"].update(sample["used"][v["id"]])
    return pack


def candidate(pack, cid):
    for direction in ("kid", "expert"):
        for c in pack["hook_slate"][direction]:
            if c["id"] == cid:
                return c
    raise KeyError(cid)


def messages(pack, **kw):
    return [e.message for e in errors(pack, **kw)]


COVER_OK = {"action": "The girl faces the viewer and looks straight into the camera with huge wide eyes and raised eyebrows, "
                       "both hands gripping her backpack straps; her mother is small and soft in the background at the gate.",
            "camera": "Child eye level, close head-and-shoulders shot, the face large in the frame."}


def cover_pack():
    """A schema 3 pack written after the slide 1 thumbnail rule (and before the bold look's shorter lines),
    with a cover brief on every option."""
    pack = load_v3()
    pack["generated_at"] = "2026-10-10T17:30:00+03:00"
    for f in pack["product_facts"]:
        f["checked_at"] = "2026-10-11"
    for d in pack["directions"]:
        for v in d["versions"]:
            v["slides"][0]["image"].update(COVER_OK)
            for key in lib.COVER_HOOK_MUST_BE_2:
                candidate(pack, v["hook"]["slate_id"])["score"][key] = 2
    return pack


class CoverSlide(unittest.TestCase):
    """Yarin, 10 Oct 2026: slide 1 is clickbaity and always shows the child's face to the viewer, exaggerated."""

    def test_prompt_adds_the_cover_line_only_on_slide_1(self):
        v = version(load(), "kid-1")
        first = lib.compose_image_prompt(v["character_anchor"], v["slides"][0]["image"], 1, pillar="kid")
        third = lib.compose_image_prompt(v["character_anchor"], v["slides"][2]["image"], 3, pillar="kid")
        self.assertIn(lib.COVER_FACE, first)
        self.assertIn("FACES THE VIEWER", first)
        self.assertIn("exaggerated", first)
        self.assertNotIn("exaggerated sadness or tears", first)   # the usual avoid line would fight the expression
        self.assertNotIn(lib.PILLARS["kid"]["photo"], first)       # the cover has its own framing
        self.assertNotIn(lib.COVER_FACE, third)
        self.assertIn(lib.PILLARS["kid"]["photo"], third)
        edit = lib.compose_image_prompt(v["character_anchor"], v["slides"][0]["image"], 1, for_edit=True, pillar="expert")
        self.assertIn(lib.COVER_FACE, edit)

    def test_new_packs_need_a_face_to_camera_cover(self):
        self.assertEqual(errors(cover_pack()), [])
        pack = cover_pack()
        img = version(pack, "kid-2")["slides"][0]["image"]
        img["action"] = "Seen from inside the kindergarten, the parents walk away while the girl watches them go."
        img["camera"] = "From behind the girl at her height."
        msgs = messages(pack)
        self.assertTrue(any("faces the viewer" in m for m in msgs))
        self.assertTrue(any("from behind" in m.lower() for m in msgs))
        pack = cover_pack()
        version(pack, "expert-1")["slides"][0]["image"]["action"] = "The girl faces the viewer and looks into the camera, calm, by the gate."
        self.assertTrue(any("exaggerated expression" in m for m in messages(pack)))

    def test_packs_written_before_the_rule_still_validate(self):
        self.assertEqual(errors(load_v3()), [])   # generated 7 Oct, slide 1 briefs from before the rule
        self.assertFalse(lib.cover_rule_applies(load()))

    def test_only_the_strongest_hook_candidates_reach_slide_1(self):
        pack = cover_pack()
        cid = version(pack, "kid-1")["hook"]["slate_id"]
        candidate(pack, cid)["score"]["stopping_power"] = 1
        self.assertTrue(any("slide 1 is the thumbnail" in m and "stopping_power" in m for m in messages(pack)))


class HookStrategy(unittest.TestCase):
    """Hook bank evidence, the nightly hook slate and the diversity rules (hook strategy research, 8 Oct 2026)."""

    def bank_file(self, extra_formula="", extra_meta=""):
        text = lib.HOOK_BANK.read_text(encoding="utf-8")
        text = text.replace("\n## Evidence and rotation", extra_formula + "\n## Evidence and rotation", 1)
        text = text.replace("\n## Formula cards", extra_meta + "\n## Formula cards", 1)
        path = Path(tempfile.mkdtemp()) / "hook-bank.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_every_formula_has_valid_evidence_and_rotation_data(self):
        bank = lib.load_hook_bank()
        self.assertGreaterEqual(len(bank), 22)
        self.assertEqual([str(i) for i in lib.bank_issues(bank, results={"posts": []})], [])
        for f in bank.values():
            self.assertIn("lumebook_hypothesis", f["evidence"], f["id"])  # nothing is validated yet
            self.assertNotIn("lumebook_validated", f["evidence"], f["id"])

    def test_bank_tables_and_code_agree(self):
        text = lib.HOOK_BANK.read_text(encoding="utf-8")
        for move in lib.SLIDE2_MOVES:
            self.assertIn(f"| `{move}` |", text)
        for key in lib.SLATE_SCORE_KEYS + lib.SLATE_FAIL_CHECKS:
            self.assertIn(f"`{key}`", text)
        schema = lib.read_json(lib.SCHEMA)
        self.assertEqual(set(schema["$defs"]["version"]["properties"]["hook_family"]["enum"]), set(lib.HOOK_FAMILIES))
        self.assertEqual(schema["properties"]["schema_version"]["enum"], [2, 3])

    def test_formula_without_evidence_row_fails(self):
        path = self.bank_file(extra_formula="| `new-thing` | moment | both | x | y | z |\n")
        issues = lib.bank_issues(lib.load_hook_bank(path), results={"posts": []}, orphans=lib.bank_orphans(path))
        self.assertTrue(any("needs a row in the Evidence and rotation table" in i.message for i in issues))

    def test_validated_label_needs_lumebook_results(self):
        row = "| `new-thing` | lumebook_validated | recognition | quote | zoom_in | 3 | 2026-10-08 | 2027-04-08 |\n"
        path = self.bank_file(extra_formula="| `new-thing` | moment | both | x | y | z |\n", extra_meta=row)
        bank = lib.load_hook_bank(path)
        self.assertTrue(any("lumebook_validated needs" in i.message for i in lib.bank_issues(bank, results={"posts": []}, orphans=[])))
        posts = [{"hook_formula": "new-thing", "topic_id": f"t{i % 3}", "reach": 500, "promotion_note": "6 posts, 3 topics, beat the rolling median on code-word comments per 1,000 reach"} for i in range(6)]
        self.assertFalse(any("lumebook_validated" in i.message for i in lib.bank_issues(bank, results={"posts": posts}, orphans=[])))
        few = posts[:4]
        self.assertTrue(any("lumebook_validated needs" in i.message for i in lib.bank_issues(bank, results={"posts": few}, orphans=[])))

    def test_trend_must_be_rechecked_within_120_days(self):
        row = "| `new-thing` | current_trend + lumebook_hypothesis | recognition | quote | zoom_in | 3 | 2026-10-08 | 2027-06-01 |\n"
        path = self.bank_file(extra_formula="| `new-thing` | moment | both | x | y | z |\n", extra_meta=row)
        issues = lib.bank_issues(lib.load_hook_bank(path), results={"posts": []}, orphans=[])
        self.assertTrue(any("must be re-checked within" in i.message for i in issues))

    def test_formula_status(self):
        import datetime as dt
        trend = {"evidence": ["current_trend"], "review_by": "2027-01-08"}
        other = {"evidence": ["lumebook_hypothesis"], "review_by": "2027-01-08"}
        self.assertEqual(lib.formula_status(trend, dt.date(2027, 1, 8)), "current")
        self.assertEqual(lib.formula_status(trend, dt.date(2027, 1, 9)), "expired")
        self.assertEqual(lib.formula_status(other, dt.date(2027, 1, 9)), "review_due")

    def test_expired_trend_blocks_a_v3_pack_and_warns_on_v2(self):
        bank = lib.load_hook_bank()
        bank["child-not-because"] = dict(bank["child-not-because"], evidence=["current_trend", "lumebook_hypothesis"], researched="2026-06-01", review_by="2026-09-01")
        with mock.patch.object(lib, "load_hook_bank", return_value=bank):
            self.assertTrue(any("revalidate it" in m for m in messages(load_v3())))
            warns = [i for i in validate_pack.pack_issues(load(), voice=VOICE0) if i.level == "WARN" and "revalidate it" in i.message]
            self.assertEqual(len(warns), 1)
            self.assertFalse(any("revalidate it" in m for m in messages(load())))

    def test_sample_slate_pack_is_valid(self):
        pack = load_v3()
        self.assertEqual(errors(pack), [])
        slate = pack["hook_slate"]
        self.assertEqual((len(slate["kid"]), len(slate["expert"])), (6, 6))
        for direction in ("kid", "expert"):
            formulas = [c["formula"] for c in slate[direction]]
            self.assertEqual(len(set(formulas)), 6)  # structurally different
            self.assertGreaterEqual(len({c["mechanism"] for c in slate[direction]}), 3)
            for c in slate[direction]:
                self.assertIsNone(lib.SALE_PREP_RE.search(c["hook"] + c["slide2"]))
                self.assertTrue(3 <= c["payoff_slide"] <= 6 and len(c["answer"]) >= 8)
                self.assertIsNone(lib.SLIDE2_LEANS_ON_SLIDE1_RE.search(c["slide2"]))
        # every used candidate that states a fact has a sourced claim on slide 1 or 2
        for d in pack["directions"]:
            for v in d["versions"]:
                c = candidate(pack, v["hook"]["slate_id"])
                if c["factual_claim"]:
                    self.assertTrue(any(cl["kind"] == "sourced_fact" and cl["slide"] in (1, 2) for cl in v["claims"]), v["id"])

    def test_v2_pack_does_not_need_a_slate(self):
        self.assertEqual(errors(load()), [])

    def test_v3_pack_needs_slate_and_hook_links(self):
        pack = load_v3()
        pack.pop("hook_slate")
        self.assertTrue(any("is not in hook_slate" in m for m in messages(pack)))
        pack = load_v3()
        version(pack, "kid-1")["hook"].pop("slate_id")
        self.assertTrue(any("required from schema_version 3" in m for m in messages(pack)))
        pack = load_v3()
        version(pack, "expert-1")["hook"]["mechanism"] = "practical_utility"
        self.assertTrue(any("works through" in m for m in messages(pack)))

    def test_failing_candidate_cannot_become_an_option(self):
        pack = load_v3()
        candidate(pack, "k6")["used_by"] = "kid-2"
        candidate(pack, "k2")["used_by"] = ""
        self.assertTrue(any("this candidate fails" in m for m in messages(pack)))
        pack = load_v3()
        candidate(pack, "k1")["score"]["honest_curiosity"] = 0
        self.assertTrue(any("0 on honest_curiosity" in m for m in messages(pack)))
        pack = load_v3()
        candidate(pack, "e1")["fail_checks"]["blames_parent"] = True
        self.assertTrue(any("blames_parent" in m for m in messages(pack)))

    def test_slate_shape_rules(self):
        pack = load_v3()
        pack["hook_slate"]["kid"].pop()
        self.assertTrue(any("at least 6 items" in m for m in messages(pack)))
        pack = load_v3()
        candidate(pack, "k5")["formula"] = "child-body-moment"
        self.assertTrue(any("appears twice" in m for m in messages(pack)))
        pack = load_v3()
        candidate(pack, "k5").update(formula="child-hidden-half", family="child_pov", mechanism="perspective_shift")
        self.assertTrue(any("family child_pov has 3 candidates" in m for m in messages(pack)))
        pack = load_v3()
        candidate(pack, "e2")["used_by"] = ""
        self.assertTrue(any("exactly one candidate per option" in m for m in messages(pack)))

    def test_slate_text_follows_audience_rules(self):
        cases = [
            ("e4", "slide2", "רק שתדעי, זה מוכר", "forbidden comma"),
            ("e5", "hook", "ספר שבו הילד שלך הוא הגיבור", "hooks never sell"),
            ("e4", "hook", "רק שתדעי\nלפני שיהיה מאוחר", "banned hook wording"),
            ("e6", "hook", "את עושה את זה לא נכון", "banned hook wording"),
            ("k5", "slide2", "אבל בשער אני מחזיק חזק", "leans on slide 1"),
            ("k4", "hook", "אמא\nאבא שוכח אותי בגן", "never talk to dad"),
            ("e5", "hook", "דמייני שמחר בבוקר בעבודה חדשה לגמרי אין לך אף מושג", "hook main line"),
        ]
        for cid, field, text, expected in cases:
            pack = load_v3()
            candidate(pack, cid)[field] = text
            self.assertTrue(any(expected in m for m in messages(pack)), (cid, text))

    def test_factual_hook_needs_a_source_on_slide_1_or_2(self):
        pack = load_v3()
        for c in version(pack, "kid-3")["claims"]:
            if c["slide"] == 2:
                c.update(kind="lumebook_wording", source_ids=[])
        self.assertTrue(any("map a sourced_fact claim to slide 1 or 2" in m for m in messages(pack)))

    def test_six_options_must_differ(self):
        pack = load_v3()
        for d in pack["directions"]:
            for v in d["versions"]:
                v["awareness_stage"] = "problem_aware"
        self.assertTrue(any("one awareness stage" in m for m in messages(pack)))
        pack = load_v3()
        for d in pack["directions"]:
            for v in d["versions"]:
                v["hook"]["slide2_move"] = "zoom_in"
                candidate(pack, v["hook"]["slate_id"])["slide2_move"] = "zoom_in"
        self.assertTrue(any("slide 2 hooks use 1 moves" in m for m in messages(pack)))
        pack = load_v3()
        version(pack, "expert-3")["slides"][0].update(headline="אני לא בוכה בגלל הגן", body="אני בוכה כי את הולכת")
        self.assertTrue(any("near rewrites" in m for m in messages(pack)))
        pack = load_v3()
        for vid in ("kid-2", "kid-3"):
            version(pack, vid)["hook"]["mechanism"] = "perspective_shift"
        self.assertTrue(any("at least 2 different mechanisms" in m or "differs from slate" in m for m in messages(pack)))

    def test_slide2_must_stand_alone_in_options(self):
        pack = load_v3()
        version(pack, "kid-2")["slides"][1]["headline"] = "אבל כל בוקר הפרידה אחרת"
        self.assertTrue(any("leans on slide 1" in m for m in messages(pack)))
        pack = load()
        version(pack, "kid-2")["slides"][1]["headline"] = "אבל כל בוקר הפרידה אחרת"
        self.assertEqual(errors(pack), [])  # version 2 packs only get a warning

    def test_history_and_rotation_carry_the_new_fields(self):
        pack = load_v3()
        entry = lib.history_entry(pack)
        o = next(o for o in entry["options"] if o["id"] == "kid-1")
        self.assertEqual((o["mechanism"], o["slide2_move"], o["shape"], o["awareness_stage"]), ("perspective_shift", "name_trigger", "negation", "problem_aware"))
        self.assertEqual(len(entry["slide2_hooks"]), 6)
        old = lib.history_entry(load())  # version 2: mechanism falls back to the formula's first mechanism
        self.assertEqual(next(o for o in old["options"] if o["id"] == "kid-1")["mechanism"], "perspective_shift")
        h = {"packs": [dict(entry, date="2026-10-07", selected=["kid-1"])]}
        ctx = lib.rotation_context(h, "2026-10-09")
        self.assertEqual(ctx["recent_mechanisms"]["recognition"], 2)
        self.assertIn("child-not-because", ctx["selected_formulas_last_14_days"])
        self.assertIn(entry["slide2_hooks"][0], ctx["recent_slide2_hooks"])

    def test_near_duplicate_against_history_warns(self):
        pack = load()
        h = {"packs": [{"date": "2026-10-01", "topic_id": "fear-of-dark", "code_words": [], "hooks": ["אני לא בוכה בגלל הגן היום"], "options": [], "selected": []}]}
        warns = [i for i in validate_pack.pack_issues(pack, history=h, voice=VOICE0) if i.level == "WARN"]
        self.assertTrue(any("reuses most of the wording" in w.message for w in warns))

    def test_finish_requires_the_slate_for_new_packs(self):
        import nightly
        self.assertTrue(nightly.finish_schema_issues(load()))
        self.assertEqual(nightly.finish_schema_issues(load_v3()), [])

    def test_nightly_start_context_lists_bank_status_and_slate_rules(self):
        import nightly
        ctx = nightly.hook_context(lib.rotation_context({"packs": []}, "2026-10-09"), "2026-10-09")
        self.assertEqual(ctx["schema_version"], 3)
        self.assertEqual(ctx["hook_slate_rules"]["per_direction"], 6)
        row = next(r for r in ctx["hook_bank"] if r["id"] == "just-so-you-know")
        self.assertEqual((row["status"], row["evidence"]), ("current", ["current_trend", "lumebook_hypothesis"]))
        late = nightly.hook_context(lib.rotation_context({"packs": []}, "2027-02-01"), "2027-02-01")
        self.assertIn("just-so-you-know", late["blocked_expired_formulas"])


class Voice(unittest.TestCase):
    def test_status_counts_samples_and_needs_15(self):
        tmp = Path(tempfile.mkdtemp())
        profile = tmp / "voice-profile.md"
        profile.write_text("## Writing samples\n\n```text\nPaste the exact message here\n```\n```text\nהיי מה קורה\n```\n", encoding="utf-8")
        approved = tmp / "approved"
        approved.mkdir()
        (approved / "README.md").write_text("שלום", encoding="utf-8")
        for i in range(13):
            (approved / f"{i:03d}.md").write_text("טקסט אמיתי", encoding="utf-8")
        no_edits = tmp / "edits.jsonl"  # never the real log, which grows with every edit Yarin saves
        s = lib.voice_status(profile, approved, edits_path=no_edits)
        self.assertEqual((s["status"], s["approved_samples"]), ("fallback", 14))
        (approved / "999.md").write_text("עוד אחד", encoding="utf-8")
        self.assertEqual(lib.voice_status(profile, approved, edits_path=no_edits)["status"], "calibrated")

    def test_lint_cli(self):
        tmp = Path(tempfile.mkdtemp()) / "copy.json"
        tmp.write_text(json.dumps({"hook": "אני לא בוכה - בגלל הגן", "cta": "כתבו גן בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור"}, ensure_ascii=False), encoding="utf-8")
        res = subprocess.run([sys.executable, str(SCRIPTS / "voice_lint.py"), str(tmp), "--cta", "cta", "--code-word", "גן", "--hook", "hook"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("U+002D", res.stdout)   # a hyphen; commas are fine again since 24 Oct 2026
        self.assertEqual(len(voice_lint.lint({"cta": 'כתבו "גן" בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור'}, cta="cta", code_word="גן")), 0)


class Review(unittest.TestCase):
    def test_review_html_and_md_are_rtl_and_complete(self):
        tmp = Path(tempfile.mkdtemp())
        shutil.copy(FIXTURE, tmp / "pack.json")
        html_path, md_path = create_review.write_review(tmp / "pack.json")
        html = html_path.read_text(encoding="utf-8")
        self.assertEqual(create_review.rtl_issues(html), [])
        self.assertEqual(html.count('<article class="option p-'), 6)
        # the two pillars are colour coded: three options each, one banner each, a legend in the header
        self.assertEqual(html.count('<article class="option p-kid"'), 3)
        self.assertEqual(html.count('<article class="option p-expert"'), 3)
        for pil in lib.PILLARS.values():
            self.assertIn(pil["name_he"], html)
            self.assertIn(pil["color"], html)
        self.assertIn('class="legend"', html)
        self.assertIn("Rubik-VariableFont_wght.ttf", html)
        self.assertEqual(html.count('<div class="card'), 6 * lib.SLIDE_COUNT)
        # dark mode (16 Nov 2026): the page follows the system appearance; the slide deck keeps its own light look (audience content)
        self.assertIn('@media (prefers-color-scheme: dark)', html)
        self.assertIn('<meta name="color-scheme" content="light dark">', html)
        self.assertRegex(html, r'\.deck\{[^}]*color-scheme:light')
        self.assertNotIn('score-row', html)  # no scorecard
        self.assertEqual(html.count('<summary>טענות ומקורות'), 6)  # claims live in a dropdown
        self.assertIn('dir="ltr"', html)  # English prompts isolated
        self.assertNotIn("winner", html.lower())
        md = md_path.read_text(encoding="utf-8")
        self.assertIn('<div dir="rtl"', md)
        self.assertEqual(md.count("#### שקופית"), 6 * lib.SLIDE_COUNT)

    def test_review_shows_the_exact_model_prompt(self):
        pack = load()
        v = version(pack, "kid-1")
        prompt = lib.compose_image_prompt(v["character_anchor"], v["slides"][lib.CTA_SLIDE - 1]["image"], lib.CTA_SLIDE)
        self.assertIn("Nothing in the scene identifies a brand", prompt)
        self.assertNotIn("LumeBook", prompt)
        self.assertIn("No generated words, letters, numbers, logos", prompt)
        self.assertIn(v["character_anchor"]["child"], prompt)

    def test_code_word_is_always_in_quotes(self):
        pack = load()
        for d in pack["directions"]:
            for v in d["versions"]:
                self.assertIn(f'"{v["code_word"]}"', v["cta"])
                self.assertIn(f'"{v["code_word"]}"', v["slides"][-1]["body"])
                self.assertIn(f'"{v["code_word"]}"', v["caption"].splitlines()[-1])
        bare = lib.cta_issues("cta", "כתבו גן בתגובות וקבלו קישור ליצירת ספר שבו הילדה שלכם היא הגיבורה", "גן")
        self.assertTrue(any(i.level == "ERROR" and "quotation" in i.message for i in bare))
        ok = lib.cta_issues("cta", 'כתבו "גן" בתגובות וקבלו קישור ליצירת ספר שבו הילדה שלכם היא הגיבורה', "גן")
        self.assertFalse([i for i in ok if i.level == "ERROR"])

    def test_image_prompts_carry_the_pillar_look(self):
        pack = load()
        image = version(pack, "kid-1")["slides"][2]["image"]
        anchor = version(pack, "kid-1")["character_anchor"]
        kid = lib.compose_image_prompt(anchor, image, 3, pillar="kid")
        expert = lib.compose_image_prompt(anchor, image, 3, pillar="expert")
        self.assertIn(lib.PILLARS["kid"]["photo"], kid)
        self.assertIn(lib.PILLARS["expert"]["photo"], expert)
        self.assertNotIn(lib.PILLARS["expert"]["photo"], kid)


class Production(unittest.TestCase):
    """Freezing an option and running its picture jobs through the OpenAI Images API (03 Nov 2026). No test calls the network."""

    def prepare(self, option="expert-1", extra=()):
        out = Path(tempfile.mkdtemp())
        argv = ["prepare_picture_jobs.py", str(FIXTURE), option, "--out-root", str(out), "--no-history", *extra]
        buf = io.StringIO()
        with NoNetwork(), mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(buf):
            prepare_picture_jobs.main()
        return out, json.loads(buf.getvalue())

    def test_prepare_makes_valid_jobs_without_network(self):
        out, summary = self.prepare()
        run = Path(summary["run_dir"])
        jobs = json.loads((run / "jobs.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["network_calls"], 0)
        self.assertEqual(len(jobs["jobs"]), lib.SLIDE_COUNT + 1)
        cfg = prepare_picture_jobs.endpoint_config()
        self.assertEqual((jobs["jobs"]["character-reference"]["mode"], jobs["jobs"]["character-reference"]["model"]), ("generate", cfg["model"]))
        self.assertTrue(all(jobs["jobs"][f"slide-{n:02d}"]["mode"] == "edit" for n in range(1, lib.SLIDE_COUNT + 1)))
        self.assertTrue(all((j["input"]["size"], j["input"]["quality"]) == (cfg["size"], "low") for j in jobs["jobs"].values()))
        self.assertEqual([p for n, j in jobs["jobs"].items() for p in prepare_picture_jobs.job_issues(n, j, cfg)], [])
        self.assertTrue((run / "APPROVAL.md").exists())
        sheet = (run / "APPROVAL.md").read_text(encoding="utf-8")
        self.assertIn("Estimated maximum", sheet)
        self.assertIn("Estimated tokens", sheet)
        self.assertGreater(summary["estimated_max_usd"], summary["estimated_usd"])

    def test_job_schema_check_catches_bad_input(self):
        cfg = prepare_picture_jobs.endpoint_config()
        bad = {"mode": "edit", "model": "some-other-model", "refs": ["r"], "input": {"prompt": "x", "size": "1000x1250", "quality": "high", "n": 1, "seed": 3}}
        problems = prepare_picture_jobs.job_issues("slide-01", bad, cfg)
        self.assertTrue(any("model" in p for p in problems))
        self.assertTrue(any("size" in p for p in problems))
        self.assertTrue(any("quality" in p for p in problems))   # only the measured quality is allowed
        self.assertTrue(any("seed" in p for p in problems))
        self.assertTrue(any("needs a reference" in p for p in prepare_picture_jobs.job_issues("s", {**bad, "refs": []}, cfg)))

    def test_prepare_is_idempotent_and_refuses_silent_overwrite(self):
        out, summary = self.prepare()
        self.prepare_again(out, expect_exit=False)
        # change the frozen copy and expect a refusal without --refreeze
        approved = Path(summary["run_dir"]) / "approved.json"
        data = json.loads(approved.read_text(encoding="utf-8"))
        data["option"]["title"] = "שונה"
        approved.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.prepare_again(out, expect_exit=True)
        # a paid image and the spend log exist before the copy change
        run = Path(summary["run_dir"])
        lib.write_placeholder_png(run / "generated-assets" / "slide-02.png", 1024, 1280, seed=2)
        (run / "generated-assets" / "generation-log.jsonl").write_text('{"job": "slide-02", "est_cost_usd": 0.06}\n', encoding="utf-8")
        st = json.loads((run / "state.json").read_text(encoding="utf-8"))
        st["jobs"]["slide-02"].update(status="done", attempts=1, qa="pass")
        (run / "state.json").write_text(json.dumps(st), encoding="utf-8")
        self.prepare_again(out, expect_exit=False, extra=("--refreeze",))
        self.assertTrue((run / "versions" / "v1" / "approved.json").exists())
        # a copy-only change keeps the image, its QA result and the spend log
        self.assertTrue((run / "generated-assets" / "slide-02.png").exists())
        self.assertTrue((run / "generated-assets" / "generation-log.jsonl").exists())
        st = json.loads((run / "state.json").read_text(encoding="utf-8"))
        self.assertEqual((st["jobs"]["slide-02"]["status"], st["jobs"]["slide-02"]["qa"]), ("done", "pass"))
        self.assertEqual(st["jobs"]["slide-03"]["status"], "pending")

    def test_another_options_errors_do_not_block_the_freeze(self):
        pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
        others = [v for d in pack["directions"] for v in d["versions"] if v["id"] != "expert-1"]
        others[0]["slides"][-2]["headline"] = ""          # another option mid-edit
        path = Path(tempfile.mkdtemp()) / "pack.json"
        path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
        self.assertTrue(validate_pack.pack_issues(pack) and any(i.level == "ERROR" for i in validate_pack.pack_issues(pack)))
        self.assertEqual(validate_pack.option_errors(pack, "expert-1"), [])
        self.assertNotEqual(validate_pack.option_errors(pack, others[0]["id"]), [])
        out = Path(tempfile.mkdtemp())
        argv = ["prepare_picture_jobs.py", str(path), "expert-1", "--out-root", str(out), "--no-history"]
        with NoNetwork(), mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(io.StringIO()):
            prepare_picture_jobs.main()
        argv[2] = others[0]["id"]
        with NoNetwork(), mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):
                prepare_picture_jobs.main()

    def prepare_again(self, out, expect_exit, extra=()):
        argv = ["prepare_picture_jobs.py", str(FIXTURE), "expert-1", "--out-root", str(out), "--no-history", *extra]
        with NoNetwork(), mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(io.StringIO()):
            if expect_exit:
                with self.assertRaises(SystemExit):
                    prepare_picture_jobs.main()
            else:
                prepare_picture_jobs.main()

    def gen(self, run, *args):
        e = dict(os.environ)
        e.pop("OPENAI_API_KEY", None)
        return subprocess.run([sys.executable, str(SCRIPTS / "openai_generate.py"), str(run), *args], capture_output=True, text=True, env=e)

    def test_slides_run_in_parallel_and_budget_is_checked_first(self):
        import openai_generate
        import openai_pictures as op
        out, summary = self.prepare()
        run_dir = Path(summary["run_dir"])
        lib.write_placeholder_png(run_dir / "generated-assets" / "character-reference.png", 1024, 1280, seed=1)
        st = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
        st["jobs"]["character-reference"].update(status="done", attempts=1, qa="pass")
        (run_dir / "state.json").write_text(json.dumps(st), encoding="utf-8")
        img = run_dir / "fake.png"
        lib.write_placeholder_png(img, 1024, 1536, seed=3)
        calls = []
        usage = {"input_tokens": 1000, "input_tokens_details": {"text_tokens": 400, "image_tokens": 600}, "output_tokens": 200}

        class FakeImages:
            def edit(self, job, ref_paths, cfg=None):
                calls.append((time.time(), job["mode"], [Path(r).name for r in ref_paths]))
                time.sleep(0.4)
                return f"req-{len(calls)}", img.read_bytes(), usage

        args = mock.Mock(jobs=[], dry_run=False, workers=7, max_usd=0.05)
        with mock.patch.object(op, "OpenAIImages", FakeImages), redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):   # the 7 slides are estimated at more than $0.05: stop before any call
                openai_generate.cmd_run(openai_generate.Run(run_dir), args)
            self.assertEqual(calls, [])
            args.max_usd = 5
            t0 = time.time()
            openai_generate.cmd_run(openai_generate.Run(run_dir), args)
        self.assertEqual(len(calls), lib.SLIDE_COUNT)
        self.assertTrue(all(c[1:] == ("edit", ["character-reference.png"]) for c in calls))
        self.assertLess(time.time() - t0, 0.4 * lib.SLIDE_COUNT / 2)   # far faster than one by one
        st = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
        self.assertTrue(all(st["jobs"][f"slide-{n:02d}"]["status"] == "done" for n in range(1, lib.SLIDE_COUNT + 1)))
        self.assertEqual(lib.png_size(run_dir / "generated-assets" / "slide-01.png"), (1024, 1280))   # the centred 4:5 crop
        log = [json.loads(l) for l in (run_dir / "generated-assets" / "generation-log.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(log), lib.SLIDE_COUNT)
        self.assertTrue(all(r["cost_basis"] == "usage" and r["usage"] == usage for r in log))
        self.assertAlmostEqual(log[0]["estimated_cost_usd"], (400 * 5 + 600 * 8 + 200 * 30) / 1e6, places=5)   # the real cost, from usage

    def test_runner_dry_run_status_qa_and_limits(self):
        out, summary = self.prepare()
        run = Path(summary["run_dir"])
        res = self.gen(run, "run", "character-reference", "--dry-run")
        self.assertEqual(res.returncode, 0, res.stderr)
        payload, _ = json.JSONDecoder().raw_decode(res.stdout)
        self.assertEqual((payload["mode"], payload["estimate"]["usd"] > 0), ("generate", True))
        # slides need a QA-passed reference
        res = self.gen(run, "run", "slide-01", "--dry-run")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("QA-passed", res.stdout + res.stderr)
        # a real run without an approved budget stops before any call
        res = self.gen(run, "run", "character-reference")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("--max-usd is required", res.stdout + res.stderr)
        # replacement policy
        state_path = run / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["jobs"]["slide-03"].update({"status": "done", "qa": "pass"})
        state_path.write_text(json.dumps(state), encoding="utf-8")
        both = self.gen(run, "replace", "slide-03", "--max-usd", "2")
        self.assertIn("only failed images are replaced", both.stdout + both.stderr)
        state["jobs"]["slide-03"].update({"qa": "fail", "replacements": 2})
        state_path.write_text(json.dumps(state), encoding="utf-8")
        res = self.gen(run, "replace", "slide-03", "--max-usd", "2")
        self.assertIn("Ask Yarin for direction", res.stdout + res.stderr)
        # budget stop: what is logged plus this call's estimate would pass the approved amount
        log = run / "generated-assets" / "generation-log.jsonl"
        log.write_text(json.dumps({"job": "x", "estimated_cost_usd": 1.58}) + "\n", encoding="utf-8")
        state["jobs"]["character-reference"].update({"status": "pending"})
        state_path.write_text(json.dumps(state), encoding="utf-8")
        res = self.gen(run, "run", "character-reference", "--max-usd", "1.58")
        self.assertIn("would pass the approved", res.stdout + res.stderr)
        self.assertNotIn("OPENAI_API_KEY=", res.stdout + res.stderr)


class Editor(unittest.TestCase):
    def setUp(self):
        import review_server
        self.rs = review_server
        self.tmp = Path(tempfile.mkdtemp())
        self.drafts = self.tmp / "drafts"
        folder = self.drafts / load()["date"]
        folder.mkdir(parents=True)
        shutil.copy(FIXTURE, folder / "pack.json")
        self.folder = folder
        self.hist = self.tmp / "history.json"

    def save(self, edits):
        self.log = self.tmp / "edits.jsonl"
        return self.rs.save(load()["date"], edits, drafts=self.drafts, history_path=self.hist, edits_log=self.log)

    def test_edit_headline_with_comma_is_saved_and_reported(self):
        res = self.save([{"option": "kid-1", "field": "headline", "slide": 1, "value": "אני לא בוכה, בגלל הגן"}])
        self.assertEqual(res["changed"], 1)
        self.assertFalse(res["valid"])
        self.assertTrue(any(e["path"] == "kid/kid-1/slide-1/headline" and e.get("char") == "," for e in res["errors"]))
        saved = json.loads((self.folder / "pack.json").read_text(encoding="utf-8"))
        self.assertEqual(version(saved, "kid-1")["slides"][0]["headline"], "אני לא בוכה, בגלל הגן")
        self.assertTrue((self.folder / "versions" / "v1" / "pack.json").exists())  # backup copy
        self.assertTrue((self.folder / "review.html").exists())
        self.assertFalse(self.hist.exists())  # invalid packs do not touch history

    def test_valid_edit_updates_review_and_history(self):
        res = self.save([{"option": "kid-1", "field": "headline", "slide": 1, "value": "אני לא בוכה\nבגלל הגן"}])
        self.assertTrue(res["valid"], res["errors"])
        self.assertTrue(self.hist.exists())
        self.assertIn("בגלל הגן", (self.folder / "review.html").read_text(encoding="utf-8"))

    def test_cta_edit_updates_last_slide_caption_and_code_word(self):
        typed = "כתבי יד בתגובות וקבלי קישור ליצירת ספר שבו הילד שלך הוא הגיבור"  # typed without quotes
        new = 'כתבי "יד" בתגובות וקבלי קישור ליצירת ספר שבו הילד שלך הוא הגיבור'   # the editor adds them
        res = self.save([{"option": "kid-1", "field": "cta", "slide": None, "value": typed}])
        self.assertTrue(res["valid"], res["errors"])
        v = version(json.loads((self.folder / "pack.json").read_text(encoding="utf-8")), "kid-1")
        self.assertEqual((v["cta"], v["code_word"]), (new, "יד"))
        self.assertEqual(v["caption"].split("\n")[-1], new)
        self.assertEqual(lib.collapse(v["slides"][lib.CTA_SLIDE - 1]["body"]), new)

    def test_caption_edit_keeps_the_cta_as_last_line(self):
        v0 = version(load(), "kid-1")
        body = "\n".join(v0["caption"].split("\n")[:-1]).replace("לפעמים", "הרבה פעמים")
        res = self.save([{"option": "kid-1", "field": "caption", "slide": None, "value": body}])
        v = version(json.loads((self.folder / "pack.json").read_text(encoding="utf-8")), "kid-1")
        self.assertEqual(v["caption"].split("\n")[-1], v0["cta"])
        self.assertIn("הרבה פעמים", v["caption"])
        self.assertEqual(res["changed"], 1)

    def test_bad_edits_are_refused(self):
        self.assertIn("error", self.save([{"option": "kid-9", "field": "headline", "slide": 1, "value": "x"}]))
        self.assertIn("error", self.save([{"option": "kid-1", "field": "body", "slide": lib.CTA_SLIDE, "value": "x"}]))
        self.assertIn("error", self.rs.save("../../etc", [], drafts=self.drafts, history_path=self.hist, edits_log=self.tmp / "e.jsonl"))
        self.assertEqual(self.save([])["changed"], 0)

    def test_edits_are_logged_for_the_voice_skill(self):
        self.save([{"option": "kid-1", "field": "headline", "slide": 3, "value": "רק תגידי לי כמה זמן זה לוקח"},
                   {"option": "kid-1", "field": "body", "slide": 3, "value": "כשאני נתלה עלייך\nבשער\nאני בעצם שואל מתי את חוזרת"},
                   {"option": "kid-1", "field": "title", "slide": None, "value": "שם חדש"}])
        log = lib.load_voice_edits(self.log)
        self.assertEqual([e["kind"] for e in log], ["rewrite", "line_breaks"])  # titles are not voice samples
        self.assertEqual(log[0]["before"], version(load(), "kid-1")["slides"][2]["headline"])
        self.assertEqual((log[0]["addressee"], log[0]["role"]), ("mom", "reframe"))
        status = lib.voice_status(profile_path=self.tmp / "none.md", approved_dir=self.tmp / "none", edits_path=self.log)
        self.assertEqual((status["approved_samples"], status["from_review_edits"]), (1, 1))

    def test_edit_kinds(self):
        self.assertEqual(lib.edit_kind("אני לא בוכה בגלל הגן", "אני לא בוכה\nבגלל הגן"), "line_breaks")
        self.assertEqual(lib.edit_kind("תגידי לי מתי את חוזרת", "תגידי לי מתי את באה"), "tweak")
        self.assertEqual(lib.edit_kind("תגידי לי מתי את חוזרת", "רק תגידי לי כמה זמן זה לוקח"), "rewrite")

    def test_http_endpoints(self):
        import threading
        import urllib.error
        server = self.rs.ThreadingHTTPServer(("127.0.0.1", 0), self.rs.Handler)
        server.default_date = load()["date"]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            base = f"http://127.0.0.1:{server.server_address[1]}"
            with urllib.request.urlopen(base + "/api/ping") as r:
                self.assertEqual(json.loads(r.read())["ok"], True)
            req = urllib.request.Request(base + "/api/save", data=json.dumps({"date": "bad", "edits": []}).encode(), headers={"Content-Type": "application/json"}, method="POST")
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(req)
            self.assertEqual(cm.exception.code, 400)
            with self.assertRaises(urllib.error.HTTPError):
                urllib.request.urlopen(base + "/scripts/carousel_lib.py")  # only drafts are served
        finally:
            server.shutdown()
            server.server_close()


@unittest.skipUnless(lib.CHROME, "Google Chrome is needed for the renderer test")
class BoldLook(unittest.TestCase):
    """The bold look (10 Oct 2026): short lines for very large type and one highlighted phrase per slide."""

    def test_rule_starts_after_the_cover_rule(self):
        self.assertFalse(lib.bold_rule_applies(cover_pack()))
        self.assertTrue(lib.bold_rule_applies({"generated_at": "2026-10-10T22:05:00+03:00"}))

    def test_highlight_is_whole_words_from_one_headline_line(self):
        slide = {"number": 3, "headline": "קשה לי בעיקר\nברגע שאתם הולכים", "highlight": "ברגע שאתם הולכים"}
        self.assertEqual(lib.highlight_issues("p", slide), [])
        for bad, why in (("", "name the 1 to 3 words"), ("רגע שאתם", "cuts a word"), ("בעיקר ברגע", "not in the headline"),
                         ("קשה לי בעיקר", None)):
            msgs = [i.message for i in lib.highlight_issues("p", {**slide, "highlight": bad})]
            if why:
                self.assertTrue(any(why in m for m in msgs), (bad, msgs))
            else:
                self.assertEqual(msgs, [])
        long = {"number": 2, "headline": "אחת שתיים שלוש ארבע", "highlight": "אחת שתיים שלוש ארבע"}
        self.assertTrue(any("max 3" in i.message for i in lib.highlight_issues("p", long)))
        self.assertEqual(lib.highlight_issues("p", {"number": lib.CTA_SLIDE, "headline": "סיפור אישי"}), [])

    def test_new_packs_get_the_short_line_limits(self):
        pack = cover_pack()
        pack["generated_at"] = "2026-10-10T22:05:00+03:00"
        msgs = messages(pack)
        self.assertTrue(any("highlight" in m for m in msgs))
        v = version(pack, "kid-1")
        v["slides"][0]["headline"] = "כותרת ארוכה מדי לשער של קרוסלה"
        self.assertTrue(any(f"max {lib.COVER_HEADLINE_LINE_MAX_CHARS}" in m for m in messages(pack)))

    def test_renderer_marks_the_phrase_the_bubble_and_the_button(self):
        html = compose_slides.lines_html("2 דברים שיעזרו לי", highlight="2 דברים")
        self.assertIn('<span class="hl">2 דברים</span>', html)
        self.assertIn('<span class="q">', compose_slides.lines_html("ואז ״נועה ביי נתראה בצהריים״", bubbles=True))
        self.assertNotIn('class="q"', compose_slides.lines_html('כתבו "גן" בתגובות', bubbles=True))
        self.assertIn('class="btn"', compose_slides.lines_html('כתבו "גן" בתגובות\nוקבלו קישור', button='כתבו "גן" בתגובות'))
        self.assertEqual(compose_slides.slide_highlight({"number": 1, "headline": "אמא ואבא\n2 דברים"}), "2 דברים")
        self.assertEqual(compose_slides.slide_highlight({"number": 4, "headline": "דבר ראשון"}), "")

    def test_loud_openers_are_allowed_and_shame_is_not(self):
        text = "תפסיקי לשאול ״איך היה?״ מה שלא מספרים לך הסוד של הבוקר לא תאמיני חייבת לדעת"
        self.assertFalse(any(re.search(p, text) for p, _ in lib.HOOK_BANNED))
        for bad in ("את עושה את זה לא נכון", "הורים טובים לא צועקים", "לפני שיהיה מאוחר", "הטעות שכל ההורים עושים"):
            self.assertTrue(any(re.search(p, bad) for p, _ in lib.HOOK_BANNED), bad)


class FixedCodeWord(unittest.TestCase):
    """Yarin, 10 Oct 2026: the CTA word is always לומי, with no rotation."""

    def pack(self, word):
        pack = cover_pack()
        pack["generated_at"] = "2026-10-10T22:30:00+03:00"
        for d in pack["directions"]:
            for v in d["versions"]:
                old = v["code_word"]
                v["code_word"] = word
                v["cta"] = v["cta"].replace(f'"{old}"', f'"{word}"')
                v["slides"][-1]["body"] = review_server.cta_slide_lines(v["cta"])
                lines = v["caption"].splitlines()
                lines[-1] = v["cta"]
                v["caption"] = "\n".join(lines)
        return pack

    def test_constant_and_cutoff(self):
        self.assertEqual(lib.CTA_CODE_WORD, "לומי")
        self.assertFalse(lib.fixed_code_word_applies({"generated_at": "2026-10-10T21:59:00+03:00"}))
        self.assertTrue(lib.fixed_code_word_applies({"generated_at": "2026-10-10T22:00:00+03:00"}))

    def test_new_packs_accept_only_the_fixed_word(self):
        self.assertFalse(any("the CTA word is always" in m for m in messages(self.pack("לומי"))))
        self.assertTrue(any("the CTA word is always" in m for m in messages(self.pack("גן"))))

    def test_the_word_is_not_rotated_out(self):
        pack = self.pack("לומי")
        history = {"packs": [{"date": "2026-10-09", "topic_id": "x", "code_words": ["לומי"], "options": []}]}
        issues = validate_pack.pack_issues(pack, history=history)
        self.assertFalse(any("was used in the last" in str(i) and "code_word" in str(i) for i in issues))

    def test_old_packs_keep_their_words(self):
        self.assertFalse(any("the CTA word is always" in m for m in messages(load_v3())))

    def test_brand_check_does_not_treat_it_as_the_brand(self):
        self.assertFalse(lib.BRAND_RE.search('כתבי "לומי" בתגובות'))
        self.assertEqual(lib.code_word_issues("code_word", "לומי"), [])


class HeadlineStory(unittest.TestCase):
    """Yarin, 10 Oct 2026: every headline tells its part of the story on its own."""

    def test_order_words_and_fragments_are_refused(self):
        for head in ("דבר ראשון", "דבר שני", "ועוד דבר קטן", "ואז", "קודם"):
            self.assertTrue(lib.headline_story_issues("p", {"headline": head}), head)
        self.assertTrue(lib.headline_story_issues("p", {"headline": "מים ליד"}))

    def test_full_thoughts_pass(self):
        for head in ("דבר ראשון\nשיניים ספר מיטה", "קודם מים ליד המיטה", "ובלי מסך\nחצי שעה עד שעה", "ואם היא רעבה\nקערת דגנים וחלב"):
            self.assertEqual(lib.headline_story_issues("p", {"headline": head}), [], head)

    def test_rule_applies_to_new_packs_only(self):
        pack = cover_pack()
        version(pack, "kid-1")["slides"][3]["headline"] = "דבר ראשון"
        self.assertFalse(any("only an order word" in m for m in messages(pack)))
        pack["generated_at"] = "2026-10-10T22:30:00+03:00"
        self.assertTrue(any("only an order word" in m for m in messages(pack)))

    def test_review_page_shows_the_headlines_alone(self):
        import create_review
        pack = cover_pack()
        html = create_review.build_html(pack)
        self.assertIn("הכותרות בלבד", html)
        self.assertIn(" ← ", html)


class ExamplesRule(unittest.TestCase):
    """Yarin, 10 Oct 2026: wherever a slide lists examples there are 3 to 7 of them."""

    SLIDE = {"headline": "במקום משחק\nסיפור או מוזיקה שקטה", "body": "או אמבטיה לרועי\nשקט לפני השינה"}

    def issues(self, items, version=None):
        return [str(i) for i in lib.example_issues("p", dict(self.SLIDE, examples=items), version, {})]

    def test_three_to_seven_items_pass(self):
        self.assertEqual(self.issues(["סיפור", "מוזיקה שקטה", "אמבטיה"]), [])
        self.assertTrue(any("3 to 7" in m for m in self.issues(["סיפור", "אמבטיה"])))
        slide = dict(self.SLIDE, body=self.SLIDE["body"] + " " + " ".join(f"פריט{k}" for k in range(1, 6)))
        many = ["סיפור", "מוזיקה שקטה", "אמבטיה"] + [f"פריט{k}" for k in range(1, 6)]
        self.assertTrue(any("3 to 7" in str(i) for i in lib.example_issues("p", dict(slide, examples=many), None, {})))

    def test_items_must_be_on_the_slide_and_different(self):
        self.assertTrue(any("does not appear on the slide" in m for m in self.issues(["סיפור", "אמבטיה", "שיר"])))
        self.assertTrue(any("different from each other" in m for m in self.issues(["סיפור", "סיפור", "אמבטיה"])))

    def test_no_list_no_check(self):
        self.assertEqual(lib.example_issues("p", self.SLIDE, None, {}), [])

    def test_the_options_draw_is_enforced(self):
        self.assertTrue(any("draw for this option is 4" in m for m in self.issues(["סיפור", "מוזיקה שקטה", "אמבטיה"], {"examples_target": 4})))
        self.assertEqual(self.issues(["סיפור", "מוזיקה שקטה", "אמבטיה"], {"examples_target": 3}), [])

    def test_the_draw_is_saved_and_in_range(self):
        folder = Path(tempfile.mkdtemp())
        slots = lib.draw_example_slots(folder)
        self.assertEqual(set(slots), set(lib.OPTION_IDS) | set(lib.PAIR_OPTION_IDS))  # kid-4 to kid-6 since 24 Oct 2026
        self.assertTrue(all(lib.NUMBERED_EXAMPLES_MIN <= n <= lib.NUMBERED_EXAMPLES_MAX for n in slots.values()))
        self.assertEqual(lib.draw_example_slots(folder), slots)

    def test_new_packs_need_the_target_and_it_must_match_the_draw(self):
        pack = cover_pack()
        pack["generated_at"] = "2026-10-11T00:30:00+03:00"
        self.assertTrue(any("examples_target" in m for m in messages(pack)))
        folder = Path(tempfile.mkdtemp())
        slots = lib.draw_example_slots(folder)
        for d in pack["directions"]:
            for v in d["versions"]:
                v["examples_target"] = slots[v["id"]]
        self.assertEqual(lib.example_target_issues(pack, folder), [])
        version(pack, "kid-1")["examples_target"] = slots["kid-1"] % 5 + 3 if slots["kid-1"] % 5 + 3 != slots["kid-1"] else 3 if slots["kid-1"] != 3 else 4
        self.assertTrue(lib.example_target_issues(pack, folder))

    def test_old_packs_need_nothing(self):
        self.assertFalse(any("examples_target" in m for m in messages(cover_pack())))


class TenSlides(unittest.TestCase):
    """Yarin, 14 Oct 2026: 10 slides (1 hook, 2 explains, 3 to 8 show 1 or 2 numbered examples each, 9 recaps,
    10 story and CTA) and one picture for the whole carousel."""

    def fixture(self):
        f = json.loads((HERE / "fixtures" / "ten_slide_option.json").read_text(encoding="utf-8"))
        return {"generated_at": f["generated_at"]}, f["version"], set(f["product_ids"])

    def errs(self, v=None):
        pack, v0, ids = self.fixture()
        return [str(i) for i in validate_pack.version_issues("kid", v or v0, pack, ids) if i.level == "ERROR"]

    def test_the_fixture_option_passes(self):
        self.assertEqual(self.errs(), [])

    def test_seven_slides_are_rejected_in_new_packs(self):
        _, v, _ = self.fixture()
        v["slides"] = v["slides"][:7]
        self.assertTrue(any("numbered 1 to 10" in m for m in self.errs(v)))

    def test_one_picture_on_the_option_not_on_slides(self):
        _, v, _ = self.fixture()
        image = v.pop("image")
        self.assertTrue(any("one picture for the whole carousel" in m for m in self.errs(v)))
        v["image"] = image
        v["slides"][4]["image"] = image
        self.assertTrue(any("not on a slide" in m for m in self.errs(v)))

    def test_roles(self):
        _, v, _ = self.fixture()
        v["slides"][1]["role"] = "example"
        self.assertTrue(any("slide 2 must be explain" in m for m in self.errs(v)))
        _, v, _ = self.fixture()
        v["slides"][8]["role"] = "resolution"
        self.assertTrue(any("slide 9 must be recap" in m for m in self.errs(v)))

    def test_one_or_two_examples_per_slide(self):
        _, v, _ = self.fixture()
        v["slides"][3]["examples"] = []
        self.assertTrue(any("1 or 2 numbered examples" in m for m in self.errs(v)))

    def test_numbers_run_across_the_carousel(self):
        _, v, _ = self.fixture()
        v["slides"][3]["headline"] = v["slides"][3]["headline"].replace("2 ", "1 ", 1)
        self.assertTrue(any("example 2" in m for m in self.errs(v)))

    def test_explain_and_recap_list_no_examples(self):
        _, v, _ = self.fixture()
        v["slides"][8]["examples"] = ["לחכות"]
        self.assertTrue(any("slide 9 recaps" in m for m in self.errs(v)))

    def test_total_matches_the_draw_and_the_cover(self):
        _, v, _ = self.fixture()
        v["examples_target"] = 7
        self.assertTrue(any("draw for this option is 7" in m for m in self.errs(v)))
        _, v, _ = self.fixture()
        v["slides"][0]["headline"] = v["slides"][0]["headline"].replace("6", "5")
        self.assertTrue(any("cover promises 5" in str(i) for i in lib.numbered_example_issues("p", v)))

    def test_a_whole_ten_slide_pack_passes_schema_and_rules(self):
        """The nightly run validates the schema as well as the rules: claims on slides 8 to 10 must be accepted."""
        pack = load_v3()
        fx = json.loads((HERE / "fixtures" / "ten_slide_option.json").read_text(encoding="utf-8"))
        pack["generated_at"] = fx["generated_at"]
        for d in pack["directions"]:
            for i, v in enumerate(d["versions"]):
                nv = copy.deepcopy(fx["version"])
                nv["id"] = v["id"]
                if d["id"] == "expert":
                    nv["expert_frame"] = {"type": "evidence_based_take"}
                d["versions"][i] = nv
        schema_errors = [m for m in messages(pack) if "must be at most" in m or "is not one of" in m or "is a required" in m or "Additional properties" in m]
        self.assertEqual(schema_errors, [])

    def test_layout_switches_at_the_cutoff(self):
        self.assertEqual(lib.slide_roles({"generated_at": "2026-10-13T22:07:20+03:00"}), lib.SLIDE_ROLES)
        self.assertEqual(lib.slide_count({"generated_at": "2026-10-14T22:00:00+03:00"}), 10)
        self.assertEqual(lib.slide_roles({"generated_at": "2026-10-14T22:00:00+03:00"})[9], ("recap",))


class ValueFirst(unittest.TestCase):
    """Yarin, 11 Oct 2026: the cover says what value the viewer gets."""

    def test_value_rule_applies_from_the_cutoff(self):
        self.assertFalse(lib.value_hook_applies({"generated_at": "2026-10-10T23:59:00+03:00"}))
        self.assertTrue(lib.value_hook_applies({"generated_at": "2026-10-11T00:01:00+03:00"}))

    def test_a_cover_candidate_must_score_2_on_usefulness(self):
        pack = cover_pack()
        pack["generated_at"] = "2026-10-11T01:00:00+03:00"
        for d in pack["directions"]:
            for v in d["versions"]:
                candidate(pack, v["hook"]["slate_id"])["score"]["usefulness"] = 2
        self.assertFalse(any("must say what the viewer gets" in m for m in messages(pack)))
        candidate(pack, version(pack, "kid-1")["hook"]["slate_id"])["score"]["usefulness"] = 1
        self.assertTrue(any("must say what the viewer gets" in m for m in messages(pack)))

    def test_an_older_pack_is_not_held_to_it(self):
        pack = cover_pack()
        cand = candidate(pack, version(pack, "kid-1")["hook"]["slate_id"])
        cand["score"]["usefulness"] = 1
        self.assertFalse(any("must say what the viewer gets" in m for m in messages(pack)))

    def test_value_markers(self):
        for yes in ("אמא\n2 דברים שיעזרו לי", "משפט אחד סוגר את הערב", "איך מתחילים שגרת שינה", "במקום ״אין ממה לפחד״"):
            self.assertTrue(lib.VALUE_MARKER_RE.search(yes), yes)
        for no in ("בכיתה מלאך בבית הר געש", "יש לי סוד"):
            self.assertFalse(lib.VALUE_MARKER_RE.search(no), no)


class Renderer(unittest.TestCase):
    def test_compose_with_placeholders(self):
        out = Path(tempfile.mkdtemp())
        argv = ["prepare_picture_jobs.py", str(FIXTURE), "kid-1", "--out-root", str(out), "--no-history"]
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(buf):
            prepare_picture_jobs.main()
        run = Path(json.loads(buf.getvalue())["run_dir"])
        res = subprocess.run([sys.executable, str(SCRIPTS / "compose_slides.py"), str(run), "--placeholders"], capture_output=True, text=True, timeout=600)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        result = json.loads(res.stdout)
        self.assertEqual(result["rtl_problems"], [])
        for p in result["slides"]:
            self.assertEqual(lib.png_size(p), (1080, 1350))
        final = Path(result["out_dir"])
        for name in ("contact-sheet.png", "rtl-check.png", "caption.txt", "sources.md", "alt-text.txt", "slides.html", "rtl-report.json"):
            self.assertTrue((final / name).exists(), name)
        html = (final / "slides.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="he" dir="rtl">', html)
        self.assertNotIn("logo_square", html)  # no brand mark unless --brand-mark
        # the trial layout: centred type on the picture, no boxes; the picture is never moved or stretched (24 Oct 2026)
        self.assertIn("text-align:center", html)
        self.assertNotIn('class="mirror"', html)
        self.assertNotIn('class="pill"', html)
        with zipfile.ZipFile(result["zip"]) as z:
            names = set(z.namelist())
        self.assertTrue({f"slides/{n:02d}.png" for n in range(1, lib.SLIDE_COUNT + 1)} <= names)
        self.assertTrue({"caption.txt", "sources.md", "generation-log.jsonl", "contact-sheet.png"} <= names)
        report = json.loads((final / "rtl-report.json").read_text(encoding="utf-8"))
        self.assertTrue(all(s["direction"] == "rtl" and s["fit"] == "ok" for s in report))
        self.assertTrue(all(s["push"] == 0 for s in report))  # the layout script ran on every slide and moved no picture
        self.assertTrue(report[-1]["dark"])  # the last slide is the dark evening slide
        self.assertNotIn("AI", html)  # never say the carousel is AI made (Yarin, 8 Oct 2026)

    def test_edit_final_changes_words_without_new_images(self):
        tmp = Path(tempfile.mkdtemp())
        drafts = tmp / "drafts" / "2026-10-08"
        drafts.mkdir(parents=True)
        shutil.copy(FIXTURE, drafts / "pack.json")
        out = tmp / "approved"
        argv = ["prepare_picture_jobs.py", str(drafts / "pack.json"), "kid-1", "--out-root", str(out), "--no-history"]
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(buf):
            prepare_picture_jobs.main()
        run = Path(json.loads(buf.getvalue())["run_dir"])
        st = json.loads((run / "state.json").read_text(encoding="utf-8"))
        for name in st["jobs"]:
            lib.write_placeholder_png(run / "generated-assets" / f"{name}.png", 1024, 1280, seed=len(name))
            st["jobs"][name].update(status="done", attempts=1, qa="pass")
        (run / "state.json").write_text(json.dumps(st), encoding="utf-8")
        first = subprocess.run([sys.executable, str(SCRIPTS / "compose_slides.py"), str(run)], capture_output=True, text=True, timeout=600)
        self.assertEqual(first.returncode, 0, first.stderr)
        res = subprocess.run([sys.executable, str(SCRIPTS / "edit_final.py"), str(run), "--slide", "2", "--headline", "אני מחזיק חזק\\nכי אני לא רוצה שתלכי",
                              "--drafts", str(tmp / "drafts"), "--history", str(tmp / "history.json"), "--edits-log", str(tmp / "edits.jsonl")],
                             capture_output=True, text=True, timeout=600)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        out_json = json.loads(res.stdout)
        self.assertEqual(out_json["re_exported_slides"], [2])
        frozen = json.loads((run / "approved.json").read_text(encoding="utf-8"))
        self.assertEqual(frozen["option"]["slides"][1]["headline"], "אני מחזיק חזק\nכי אני לא רוצה שתלכי")
        with zipfile.ZipFile(out_json["zip"]) as z:
            self.assertEqual(sum(n.startswith("slides/") for n in z.namelist()), lib.SLIDE_COUNT)
        self.assertTrue((tmp / "edits.jsonl").exists())   # the edit teaches the voice, in the test's own log

    def test_quotes_and_latin_render_as_text(self):
        html = compose_slides.lines_html('בלי "עוד חמש דקות" & AI')
        self.assertIn("&quot;עוד חמש דקות&quot;", html)
        self.assertNotIn("<bdi dir=\"ltr\">quot</bdi>", html)
        self.assertIn('<bdi dir="ltr">AI</bdi>', html)

    def test_both_pillars_share_the_trial_layout(self):
        for oid, direction in (("kid-1", "kid"), ("expert-1", "expert")):
            frozen = {"date": "2026-10-08", "direction": direction, "option": version(load(), oid)}
            out = Path(tempfile.mkdtemp())
            images = {s["number"]: out / "x.png" for s in frozen["option"]["slides"]}
            html = compose_slides.build_html(frozen, images, out, None)
            self.assertNotIn('class="who"', html)
            self.assertNotIn('class="count"', html)
            self.assertEqual(html.count('<section class="slide dark cta"'), 1)

    def test_clean_look_paints_only_the_last_slide(self):
        """Yarin, 14 Oct 2026: plain type on every slide but the CTA slide, which stays as it was."""
        f = json.loads((HERE / "fixtures" / "ten_slide_option.json").read_text(encoding="utf-8"))
        frozen = {"date": "2026-10-15", "direction": "kid", "option": f["version"]}
        out = Path(tempfile.mkdtemp())
        images = {s["number"]: out / "x.png" for s in frozen["option"]["slides"]}
        html = compose_slides.build_html(frozen, images, out, None, look="clean")
        self.assertIn("look-bold look-clean", html)
        sections = html.split("<section")[1:]
        self.assertEqual(len(sections), 10)
        self.assertTrue(all('class="hl"' not in sec and 'class="q"' not in sec for sec in sections[:-1]))
        self.assertIn('class="hl"', sections[-1])
        self.assertIn('class="btn"', sections[-1])


class ChromeLookup(unittest.TestCase):
    """find_chrome: CHROME_PATH, then the Mac app, then Chromium on PATH (Claude Code on the web)."""

    def setUp(self):
        self.bin = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.bin, True)
        self.fake = self.bin / "chromium"
        self.fake.write_text("#!/bin/sh\n")
        self.fake.chmod(0o755)

    def find(self, env, mac):
        with mock.patch.dict(os.environ, env), mock.patch.object(lib, "CHROME_MAC", mac):
            if "CHROME_PATH" not in env:
                os.environ.pop("CHROME_PATH", None)
            return lib.find_chrome()

    def test_linux_finds_chromium_on_path(self):
        self.assertEqual(self.find({"PATH": str(self.bin)}, "/nowhere/Chrome"), str(self.fake))

    def test_mac_app_comes_before_path(self):
        mac = self.bin / "Google Chrome"
        mac.write_text("")
        self.assertEqual(self.find({"PATH": str(self.bin)}, str(mac)), str(mac))

    def test_chrome_path_wins_and_is_not_second_guessed(self):
        self.assertEqual(self.find({"CHROME_PATH": str(self.fake), "PATH": ""}, "/nowhere/Chrome"), str(self.fake))
        self.assertEqual(self.find({"CHROME_PATH": "chromium", "PATH": str(self.bin)}, "/nowhere/Chrome"), str(self.fake))
        self.assertIsNone(self.find({"CHROME_PATH": "/nowhere/chrome", "PATH": str(self.bin)}, "/nowhere/Chrome"))

    def test_none_when_nothing_is_installed(self):
        self.assertIsNone(self.find({"PATH": str(self.bin / "empty")}, "/nowhere/Chrome"))
        with mock.patch.object(lib, "CHROME", None), self.assertRaises(SystemExit) as err:
            compose_slides.chrome([])
        self.assertIn("CHROME_PATH", str(err.exception))


if __name__ == "__main__":
    unittest.main()


class SyncNumberedExamples(unittest.TestCase):
    """Yarin, 18 Oct 2026: edits in Carousel Machine reworded and removed examples, the hidden lists stayed old and the
    production stopped. carousel_lib.sync_numbered_examples makes the lists and the count follow the slides."""

    def option(self):
        return json.loads((HERE / "fixtures" / "ten_slide_option.json").read_text(encoding="utf-8"))["version"]

    def example_errors(self, v):
        return [i for i in lib.numbered_example_issues("kid/kid-1", v) if i.level == "ERROR"]

    def test_a_valid_option_is_left_alone(self):
        v = self.option()
        before = json.dumps(v, ensure_ascii=False)
        r = lib.sync_numbered_examples(v)
        self.assertEqual(json.dumps(v, ensure_ascii=False), before)
        self.assertEqual(r, {"examples": None, "renumbered": False, "changed": []})

    def test_a_reworded_example_updates_its_list(self):
        v = self.option()
        v["slides"][3]["headline"] = "2 לשאול איך הוא מרגיש"
        self.assertTrue(self.example_errors(v))
        lib.sync_numbered_examples(v)
        self.assertEqual(v["slides"][3]["examples"], ["לשאול איך הוא מרגיש"])
        self.assertEqual(self.example_errors(v), [])

    def test_an_added_example_renumbers_and_updates_the_count_and_cover(self):
        v = self.option()
        v["slides"][3]["headline"] = "2 להגיד מה הוא מרגיש\n3 לשאול מה קורה"
        r = lib.sync_numbered_examples(v)
        self.assertEqual(r["examples"], (6, 7))
        self.assertTrue(r["renumbered"])
        self.assertEqual(v["examples_target"], 7)
        self.assertIn("7 דברים", v["slides"][0]["headline"])
        self.assertEqual(v["slides"][7]["headline"], "7 לחבק אותי אחרי")
        self.assertEqual(self.example_errors(v), [])
