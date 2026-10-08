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
import prepare_fal_jobs  # noqa: E402
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
        for line in ("זו חרדת פרידה", "בלי דמעות תוך שבוע", "כל הילדים מרגישים ככה", "בספר של לומיבוק"):
            pack = load()
            version(pack, "expert-1")["slides"][3]["body"] = line
            self.assertTrue(errors(pack), line)

    def test_carousel_never_names_the_brand(self):
        for text in ("בספר של לומבוק", "LumeBook", "lumebook", "ספר של לומיבוק"):
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
        version(pack, "expert-1")["slides"][0]["headline"] = "לא תאמינו מה קורה בשער"
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
            ("e6", "hook", "תפסיקי להגיד לו את זה", "banned hook wording"),
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
        tmp.write_text(json.dumps({"hook": "אני לא בוכה, בגלל הגן", "cta": "כתבו גן בתגובות וקבלו קישור ליצירת ספר שבו הילד שלכם הוא הגיבור"}, ensure_ascii=False), encoding="utf-8")
        res = subprocess.run([sys.executable, str(SCRIPTS / "voice_lint.py"), str(tmp), "--cta", "cta", "--code-word", "גן", "--hook", "hook"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("U+002C", res.stdout)
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
        self.assertIn('color-scheme:light', html)
        self.assertNotIn('prefers-color-scheme:dark', html)
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
    def prepare(self, option="expert-1", extra=()):
        out = Path(tempfile.mkdtemp())
        argv = ["prepare_fal_jobs.py", str(FIXTURE), option, "--out-root", str(out), "--no-history", *extra]
        buf = io.StringIO()
        with NoNetwork(), mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(buf):
            prepare_fal_jobs.main()
        return out, json.loads(buf.getvalue())

    def test_prepare_makes_valid_jobs_without_network(self):
        out, summary = self.prepare()
        run = Path(summary["run_dir"])
        jobs = json.loads((run / "jobs.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["network_calls"], 0)
        self.assertEqual(len(jobs["jobs"]), lib.SLIDE_COUNT + 1)
        self.assertEqual(jobs["jobs"]["character-reference"]["endpoint"], "openai/gpt-image-2.5/flare/text-to-image")
        self.assertTrue(all(jobs["jobs"][f"slide-{n:02d}"]["endpoint"] == "openai/gpt-image-2.5/flare/edit" for n in range(1, lib.SLIDE_COUNT + 1)))
        self.assertTrue(all(j["input"]["image_size"] == {"width": 1024, "height": 1280} for j in jobs["jobs"].values()))
        cfg = prepare_fal_jobs.endpoint_config()
        self.assertEqual([p for n, j in jobs["jobs"].items() for p in prepare_fal_jobs.job_issues(n, j, cfg)], [])
        self.assertTrue((run / "APPROVAL.md").exists())
        self.assertIn("Estimated maximum", (run / "APPROVAL.md").read_text(encoding="utf-8"))
        self.assertGreater(summary["estimated_max_usd"], summary["estimated_usd"])

    def test_job_schema_check_catches_bad_input(self):
        cfg = prepare_fal_jobs.endpoint_config()
        bad = {"endpoint": "openai/gpt-image-2.5/flare/edit", "refs": ["r"], "input": {"prompt": "x", "image_size": {"width": 1000, "height": 1250}, "quality": "ultra", "output_format": "png", "num_images": 1, "seed": 3}}
        problems = prepare_fal_jobs.job_issues("slide-01", bad, cfg)
        self.assertTrue(any("multiples of 16" in p for p in problems))
        self.assertTrue(any("quality" in p for p in problems))
        self.assertTrue(any("seed" in p for p in problems))

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

    def prepare_again(self, out, expect_exit, extra=()):
        argv = ["prepare_fal_jobs.py", str(FIXTURE), "expert-1", "--out-root", str(out), "--no-history", *extra]
        with NoNetwork(), mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(io.StringIO()):
            if expect_exit:
                with self.assertRaises(SystemExit):
                    prepare_fal_jobs.main()
            else:
                prepare_fal_jobs.main()

    def fal(self, run, *args, env=None):
        e = dict(os.environ)
        e.pop("FAL_KEY", None)
        return subprocess.run([sys.executable, str(SCRIPTS / "fal_generate.py"), str(run), *args], capture_output=True, text=True, env=e)

    def test_slides_run_in_parallel_and_budget_is_checked_first(self):
        import fal_generate
        out, summary = self.prepare()
        run_dir = Path(summary["run_dir"])
        lib.write_placeholder_png(run_dir / "generated-assets" / "character-reference.png", 1024, 1280, seed=1)
        st = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
        st["jobs"]["character-reference"].update(status="done", attempts=1, qa="pass")
        (run_dir / "state.json").write_text(json.dumps(st), encoding="utf-8")
        img = run_dir / "fake.png"
        lib.write_placeholder_png(img, 64, 80, seed=3)
        calls = []

        class FakeFal:
            def upload(self, path):
                return "https://example.invalid/ref.png"

            def generate(self, endpoint, arguments):
                calls.append(time.time())
                time.sleep(0.4)
                return f"req-{len(calls)}", img.as_uri()

        args = mock.Mock(jobs=[], dry_run=False, workers=7, max_usd=0.05)
        with mock.patch.object(fal_generate, "Fal", FakeFal), redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):   # 7 slides cost more than $0.05: stop before any call
                fal_generate.cmd_run(fal_generate.Run(run_dir), args)
            self.assertEqual(calls, [])
            args.max_usd = 5
            t0 = time.time()
            fal_generate.cmd_run(fal_generate.Run(run_dir), args)
        self.assertEqual(len(calls), lib.SLIDE_COUNT)
        self.assertLess(time.time() - t0, 0.4 * lib.SLIDE_COUNT / 2)   # far faster than one by one
        st = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
        self.assertTrue(all(st["jobs"][f"slide-{n:02d}"]["status"] == "done" for n in range(1, lib.SLIDE_COUNT + 1)))
        log = (run_dir / "generated-assets" / "generation-log.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(log), lib.SLIDE_COUNT)

    def test_runner_dry_run_status_qa_and_limits(self):
        out, summary = self.prepare()
        run = Path(summary["run_dir"])
        res = self.fal(run, "run", "character-reference", "--dry-run")
        self.assertEqual(res.returncode, 0, res.stderr)
        payload = json.loads(res.stdout)
        self.assertEqual(payload["endpoint"], "openai/gpt-image-2.5/flare/text-to-image")
        # slides need a QA-passed reference
        res = self.fal(run, "run", "slide-01", "--dry-run")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("QA-passed", res.stdout + res.stderr)
        # a real run without approval amount or key stops before any call
        res = self.fal(run, "run", "character-reference")
        self.assertNotEqual(res.returncode, 0)
        # replacement policy
        state_path = run / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["jobs"]["slide-03"].update({"status": "done", "qa": "pass"})
        state_path.write_text(json.dumps(state), encoding="utf-8")
        self.assertIn("only failed images are replaced", self.fal(run, "replace", "slide-03", "--max-usd", "2").stdout + self.fal(run, "replace", "slide-03", "--max-usd", "2").stderr)
        state["jobs"]["slide-03"].update({"qa": "fail", "replacements": 2})
        state_path.write_text(json.dumps(state), encoding="utf-8")
        res = self.fal(run, "replace", "slide-03", "--max-usd", "2")
        self.assertIn("Ask Yarin for direction", res.stdout + res.stderr)
        # budget stop
        log = run / "generated-assets" / "generation-log.jsonl"
        log.write_text(json.dumps({"job": "x", "estimated_cost_usd": 1.58}) + "\n", encoding="utf-8")
        state["jobs"]["character-reference"].update({"status": "pending"})
        state_path.write_text(json.dumps(state), encoding="utf-8")
        res = self.fal(run, "run", "character-reference", "--max-usd", "1.60")
        self.assertIn("would pass the approved", res.stdout + res.stderr)
        self.assertNotIn("FAL_KEY=", res.stdout + res.stderr)


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


@unittest.skipUnless(Path(lib.CHROME).exists(), "Google Chrome is needed for the renderer test")
class Renderer(unittest.TestCase):
    def test_compose_with_placeholders(self):
        out = Path(tempfile.mkdtemp())
        argv = ["prepare_fal_jobs.py", str(FIXTURE), "kid-1", "--out-root", str(out), "--no-history"]
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(buf):
            prepare_fal_jobs.main()
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
        # the trial layout: centred type on the picture, no boxes, the art pushed down under the text
        self.assertIn("text-align:center", html)
        self.assertEqual(html.count('<div class="mirror">'), lib.SLIDE_COUNT)
        self.assertNotIn('class="pill"', html)
        with zipfile.ZipFile(result["zip"]) as z:
            names = set(z.namelist())
        self.assertTrue({f"slides/{n:02d}.png" for n in range(1, lib.SLIDE_COUNT + 1)} <= names)
        self.assertTrue({"caption.txt", "sources.md", "generation-log.jsonl", "contact-sheet.png"} <= names)
        report = json.loads((final / "rtl-report.json").read_text(encoding="utf-8"))
        self.assertTrue(all(s["direction"] == "rtl" and s["fit"] == "ok" for s in report))
        self.assertTrue(all("push" in s for s in report))  # the layout script ran on every slide
        self.assertTrue(report[-1]["dark"])  # the last slide is the dark evening slide
        self.assertNotIn("AI", html)  # never say the carousel is AI made (Yarin, 8 Oct 2026)

    def test_edit_final_changes_words_without_new_images(self):
        tmp = Path(tempfile.mkdtemp())
        drafts = tmp / "drafts" / "2026-10-08"
        drafts.mkdir(parents=True)
        shutil.copy(FIXTURE, drafts / "pack.json")
        out = tmp / "approved"
        argv = ["prepare_fal_jobs.py", str(drafts / "pack.json"), "kid-1", "--out-root", str(out), "--no-history"]
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", argv), mock.patch.object(lib, "voice_status", return_value=VOICE0), redirect_stdout(buf):
            prepare_fal_jobs.main()
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
            self.assertEqual(html.count('<section class="slide dark"'), 1)


if __name__ == "__main__":
    unittest.main()
