#!/usr/bin/env python3
"""Tests for the daily games and books recommendation carousels (scripts/reco_lib.py, scripts/reco_render.py).

    python3 -m unittest carousel/carousel-pipeline/tests/test_reco.py -v

The fixtures in tests/fixtures/reco/ are copies of the first real example (drafts/2026-10-08). Tests copy them
into a temp folder and draw placeholder images at every referenced path, so no real image, network call or
history file is touched (history goes to a temp file).
"""

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import carousel_lib as lib  # noqa: E402
import reco_lib as rl  # noqa: E402
import reco_render  # noqa: E402

FIXTURES = HERE / "fixtures" / "reco"


def load(fmt):
    return json.loads((FIXTURES / rl.FILES[fmt]).read_text(encoding="utf-8"))


def errors(issues):
    return [i for i in issues if i.level == "ERROR"]


def messages(issues, level="ERROR"):
    return "\n".join(str(i) for i in issues if i.level == level)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="reco-test-"))
        self.folder = self.tmp / "drafts" / "2026-10-08"
        self.folder.mkdir(parents=True)
        self.history_path = self.tmp / "reco-history.json"
        for fmt in rl.FORMATS:
            car = load(fmt)
            (self.folder / rl.FILES[fmt]).write_text(json.dumps(car, ensure_ascii=False), encoding="utf-8")
            imgs = [p["image"] for p in car["products"]] + [car["lumebook"]["image"]]
            for k, img in enumerate(imgs):
                lib.write_placeholder_png(self.folder / img["file"], 600, 760 if k % 2 else 600, seed=k)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def car(self, fmt="games"):
        return json.loads((self.folder / rl.FILES[fmt]).read_text(encoding="utf-8"))

    def check(self, car, history=None):
        return rl.carousel_issues(car, self.folder, history=history)

    def slide(self, car, n):
        return car["slides"][n - 1]


class FixtureAndStructure(Base):
    def test_both_fixtures_are_valid(self):
        for fmt in rl.FORMATS:
            issues = self.check(self.car(fmt), history={"carousels": []})
            self.assertEqual(errors(issues), [], f"{fmt}:\n{messages(issues)}")

    def test_rights_unverified_is_valid_but_not_publish_ready(self):
        car = self.car()
        car["products"][0]["image"]["rights_status"] = "rights_unverified"
        issues = self.check(car)
        st = rl.status(issues, car)
        self.assertTrue(st["valid"])
        self.assertFalse(st["publish_ready"])
        self.assertIn("rights", st["flags"])

    def test_exactly_seven_slides(self):
        car = self.car()
        car["slides"].pop()
        self.assertIn("allows at most" if False else "slides", messages(self.check(car)))
        self.assertTrue(errors(self.check(car)))

    def test_roles_are_fixed(self):
        car = self.car()
        self.slide(car, 2)["role"] = "hook"
        self.assertIn("slide 2 must be frame", messages(self.check(car)))

    def test_each_product_once_on_slides_3_to_5(self):
        car = self.car()
        self.slide(car, 4)["product_id"] = self.slide(car, 3)["product_id"]
        self.assertIn("exactly once", messages(self.check(car)))

    def test_exact_product_name_on_the_slide(self):
        car = self.car()
        self.slide(car, 3)["headline"] = "משחק נהדר"
        self.assertIn("exact product name", messages(self.check(car)))

    def test_slides_need_why_and_how(self):
        car = self.car()
        self.slide(car, 4)["how"] = ""
        self.assertIn("how a parent and child can use it", messages(self.check(car)))

    def test_why_names_the_activity_not_vague_praise(self):
        car = self.car()
        self.slide(car, 3)["why"] = "מעולה להתפתחות"
        msg = messages(self.check(car))
        self.assertIn("vague", msg)
        self.assertIn("actual activity", msg)

    def test_near_identical_products_are_refused(self):
        car = self.car()
        car["products"][1]["type"] = car["products"][0]["type"]
        self.assertIn("share a type", messages(self.check(car)))


class LumeBook(Base):
    def test_brand_once_on_slide_6_only(self):
        car = self.car()
        self.slide(car, 3)["why"] += "\nכמו בלומבוק"
        self.assertIn("LumeBook appears only on slide 6", messages(self.check(car)))

    def test_slide_6_must_name_it(self):
        car = self.car()
        s = self.slide(car, 6)
        s["headline"] = lib.BRAND_RE.sub("ספר", s["headline"])
        s["body"] = lib.BRAND_RE.sub("ספר", s["body"])
        self.assertIn("exactly once", messages(self.check(car)))

    def test_slide_6_twice_is_too_much(self):
        car = self.car()
        self.slide(car, 6)["body"] += "\nשוב לומבוק"
        self.assertIn("exactly once", messages(self.check(car)))

    def test_not_in_caption(self):
        car = self.car()
        car["caption"] += "\nלומבוק"
        self.assertIn("not in the caption", messages(self.check(car)))

    def test_no_sales_talk_on_slide_6(self):
        for word in ("הנחה", "עכשיו", "בחינם", "₪"):
            car = self.car()
            self.slide(car, 6)["body"] += f"\nיש {word}"
            self.assertIn("sales talk", messages(self.check(car)), word)

    def test_slide_6_needs_a_live_site_fact(self):
        car = self.car()
        car["claims"] = [c for c in car["claims"] if c["kind"] != "product_fact"]
        self.assertIn("live-site product fact", messages(self.check(car)))

    def test_stale_site_fact(self):
        car = self.car()
        car["product_facts"][0]["checked_at"] = "2026-09-20"
        self.assertIn("re-check the live site", messages(self.check(car)))

    def test_lumebook_image_must_be_an_approved_asset(self):
        car = self.car()
        car["lumebook"]["image"]["source_type"] = "israeli_retailer"
        self.assertIn("lumebook_repo", messages(self.check(car)))

    def test_close_stays_useful_not_sales(self):
        car = self.car()
        self.slide(car, 7)["body"] += "\nקישור בתגובה"
        self.assertIn("sales slide", messages(self.check(car)))

    def test_close_has_a_light_prompt(self):
        car = self.car()
        s = self.slide(car, 7)
        s["headline"], s["body"] = "שלושה משחקים", "תור ועוד תור\nזה כל הסוד"
        self.assertIn("save, share or comment prompt", messages(self.check(car)))


class Evidence(Base):
    def test_popular_needs_strong_or_two_independent_signals(self):
        car = self.car()
        p = car["products"][0]
        p["popularity_label"] = "popular_in_israel"
        p["popularity_signals"] = [{"id": "pop-x", "type": "multi_retailer", "description": "two shops", "url": "https://shop.co.il/x",
                                    "quote": "במלאי", "accessed": "2026-10-08", "group": "shops"}]
        car["claims"] = [c for c in car["claims"] if c["kind"] != "popularity"]
        self.assertIn("popular_in_israel needs one strong", messages(self.check(car)))
        p["popularity_signals"].append({"id": "pop-y", "type": "hebrew_edition_established_publisher", "description": "publisher",
                                        "url": "https://pub.co.il/y", "quote": "מהדורה", "accessed": "2026-10-08", "group": "publisher"})
        self.assertNotIn("popular_in_israel needs one strong", messages(self.check(car)))
        p["popularity_signals"] = [{"id": "pop-z", "type": "bestseller_list", "description": "list", "url": "https://store.co.il/top",
                                    "quote": "רבי מכר", "accessed": "2026-10-08", "group": "store"}]
        self.assertNotIn("popular_in_israel needs one strong", messages(self.check(car)))

    def test_international_popularity_never_counts(self):
        car = self.car()
        p = car["products"][0]
        p["popularity_label"] = "popular_in_israel"
        p["popularity_signals"] = [{"id": "pop-a", "type": "bestseller_list", "description": "Amazon US", "url": "https://www.amazon.com/best",
                                    "quote": "#1 Best Seller", "accessed": "2026-10-08", "group": "amazon"}]
        car["claims"] = [c for c in car["claims"] if c["kind"] != "popularity"]
        msg = messages(self.check(car))
        self.assertIn("not Israel-specific", msg)
        self.assertIn("popular_in_israel needs one strong", msg)

    def test_available_only_is_flagged(self):
        car = self.car()
        p = car["products"][0]
        p["popularity_label"] = "available_in_israel"
        car["claims"] = [c for c in car["claims"] if not (c["kind"] == "popularity" and any(sid.startswith("pop-") and sid in {s["id"] for s in p["popularity_signals"]} for sid in c["source_ids"]))]
        issues = self.check(car)
        self.assertIn("only available_in_israel", messages(issues, "WARN"))
        self.assertFalse(rl.status(issues, car)["publish_ready"])

    def test_popularity_wording_needs_popular_label(self):
        car = self.car()
        n = next(s["number"] for s in car["slides"] if s.get("product_id") == car["products"][0]["id"])
        car["products"][0]["popularity_label"] = "available_in_israel"
        car["claims"] = [c for c in car["claims"] if c["kind"] != "popularity"]
        self.slide(car, n)["why"] = "רב מכר בגנים\nמחכים לתור"
        self.assertIn("only supports available_in_israel", messages(self.check(car)))

    def test_israeli_availability_required_and_fresh(self):
        car = self.car()
        car["products"][0]["availability"] = [{"retailer": "Amazon", "url": "https://www.amazon.com/x", "status": "in_stock", "accessed": "2026-10-08", "quote": "In stock"}]
        self.assertIn("Israel-specific availability", messages(self.check(car)))
        car = self.car()
        car["products"][0]["availability"][0]["accessed"] = "2026-09-01"
        self.assertIn("still sold", messages(self.check(car)))
        car = self.car()
        for a in car["products"][0]["availability"]:
            a["status"] = "out_of_stock"
        self.assertIn("available now", messages(self.check(car)))

    def test_age_conflict(self):
        car = self.car()
        car["products"][0]["official_age"]["min"] = 8
        car["products"][0]["official_age"]["text"] = "8+"
        self.assertIn("age recommendation conflicts", messages(self.check(car)))

    def test_slide_age_follows_the_official_age(self):
        car = self.car()
        self.slide(car, 3)["age"] = "מגיל 9"
        self.assertIn("official age", messages(self.check(car)))

    def test_developmental_claims_need_sources(self):
        car = self.car()
        car["claims"] = [c for c in car["claims"] if not (c["slide"] == 4 and c["kind"] == "developmental")]
        self.assertIn("slide 4 says why", messages(self.check(car)))
        car = self.car()
        dev = next(c for c in car["claims"] if c["kind"] == "developmental")
        dev["source_ids"] = []
        self.assertIn("credible source", messages(self.check(car)))

    def test_dev_source_must_be_credible(self):
        car = self.car()
        car["dev_sources"][0]["url"] = "https://some-blog.example.com/games"
        car["dev_sources"][0]["kind"] = "reputable_explainer"
        self.assertIn("credible source list", messages(self.check(car)))


class Images(Base):
    def test_missing_image(self):
        car = self.car()
        car["products"][0]["image"]["file"] = "reco-assets/nope.jpg"
        self.assertIn("image file not found", messages(self.check(car)))

    def test_no_search_engine_or_generator_images(self):
        for url in ("https://encrypted-tbn0.gstatic.com/images?q=x", "https://v3.fal.media/files/x.png", "https://i.pinimg.com/x.jpg"):
            car = self.car()
            car["products"][0]["image"]["image_url"] = url
            self.assertIn("search engine, pin board or image generator", messages(self.check(car)), url)

    def test_rights_status_is_required(self):
        car = self.car()
        del car["products"][0]["image"]["rights_status"]
        self.assertTrue(errors(self.check(car)))


class Hebrew(Base):
    def test_punctuation_and_voice(self):
        for field, value, expect in (("why", "מחכים לתור, ומטילים קובייה", "comma"), ("how", "משחקים יחד.", "period"),
                                     ("why", "זה ישפר את הריכוז", "promises a developmental result"),
                                     ("how", "תגיד לו לחכות לתור", "talks to a father"), ("how", "תן לו להטיל את הקובייה", "talks to a father"), ("why", "נוצר בעזרת AI", "AI")):
            car = self.car()
            self.slide(car, 3)[field] = value
            msg = messages(self.check(car))
            self.assertTrue(errors(self.check(car)), value)
            if expect:
                self.assertIn(expect, msg, value)

    def test_never_dad(self):
        car = self.car()
        self.slide(car, 2)["body"] += "\nאבא יכול לשחק"
        self.assertIn("never talk to dad", messages(self.check(car)))

    def test_product_title_may_keep_its_own_punctuation(self):
        car = self.car()
        p = car["products"][0]
        n = next(s["number"] for s in car["slides"] if s.get("product_id") == p["id"])
        p["title_he"] = "אחת, שתיים"
        self.slide(car, n)["headline"] = "אחת, שתיים"
        self.assertNotIn("comma", messages(self.check(car)))

    def test_ages_are_approximate(self):
        car = self.car()
        for n in (1, 2):
            s = self.slide(car, n)
            s["headline"] = rl.AGE_HEDGE_RE.sub("", s["headline"])
            s["body"] = rl.AGE_HEDGE_RE.sub("", s.get("body", ""))
        car["caption"] = rl.AGE_HEDGE_RE.sub("", car["caption"])
        self.assertIn("ages are approximate", messages(self.check(car)))


class Process(Base):
    def test_no_paid_calls_no_generation_no_posting(self):
        for key, value, expect in (("paid_api_calls", 1, "paid API"), ("images_generated", 2, "generate images"), ("posted", True, "posted")):
            car = self.car()
            car["checks"][key] = value
            self.assertIn(expect, messages(self.check(car)))


class Rotation(Base):
    def history_with(self, car, date="2026-09-30", **changes):
        entry = rl.history_entry(car)
        entry.update(date=date, **changes)
        return {"carousels": [entry]}

    def test_product_within_30_days(self):
        car = self.car()
        h = self.history_with(car, stage_id="other-stage", skill="memory", hook_structure="observation")
        self.assertIn("no product twice within 30 days", messages(self.check(car, h)))
        car["products"][0]["seasonal_reason"] = "חנוכה"
        self.assertIn("seasonal reason given", messages(self.check(car, h), "WARN"))

    def test_older_than_30_days_is_fine(self):
        car = self.car()
        h = self.history_with(car, date="2026-08-01", stage_id="other-stage", skill="memory", hook_structure="observation")
        self.assertNotIn("no product twice", messages(self.check(car, h)))

    def test_skill_stage_and_hook_structure_rotate(self):
        car = self.car()
        h = self.history_with(car, products=[])
        msg = messages(self.check(car, h))
        self.assertIn("rotate the skill", msg)
        self.assertIn("ran in the last 14 days", msg)
        self.assertIn("opened the previous", msg)

    def test_other_format_does_not_block_skill(self):
        car = self.car()
        h = self.history_with(car, products=[], format="books" if car["format"] == "games" else "games")
        self.assertNotIn("rotate the skill", messages(self.check(car, h)))

    def test_record_history_is_idempotent(self):
        car = self.car()
        rl.record_history(car, self.history_path)
        rl.record_history(car, self.history_path)
        rl.record_history(self.car("books"), self.history_path)
        h = rl.load_history(self.history_path)
        self.assertEqual(len(h["carousels"]), 2)
        ctx = rl.rotation_context(h, "2026-10-09")
        self.assertIn(car["stage"]["skill"], ctx["games"]["blocked_skills"])
        self.assertTrue(ctx["blocked_products"])

    def test_backup_before_a_rerun(self):
        target = rl.backup_existing(self.folder)
        self.assertTrue((target / rl.FILES["games"]).exists())
        self.assertFalse((self.folder / rl.FILES["games"]).exists())


class Review(Base):
    def test_review_gets_tabs_and_each_carousel_its_own_minimal_page(self):
        html = '<!doctype html>\n<html lang="he" dir="rtl"><body><div class="lb-page"><nav class="jump"></nav></div><script>x</script></body></html>'
        out = reco_render.inject_review(html, self.folder, history={"carousels": []})
        self.assertIn('class="lb-tabs rv-tabs"', out)
        self.assertIn('href="games.html"', out)
        self.assertIn('href="books.html"', out)
        self.assertNotIn("data-reco", out)  # the carousels live on their own pages, not inside review.html
        page = (self.folder / "games.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="he" dir="rtl">', page)
        self.assertIn('aria-selected="true">משחקים', page)
        for summary in ("טקסט", "המוצרים", "מקורות", "בדיקות"):
            self.assertIn(f"<summary>{summary}", page)
        self.assertIn('data-reco="games"', page)
        self.assertIn("זכויות תמונה לא מאומתות", page)
        for p in self.car()["products"]:
            self.assertIn(p["title_he"], page)

    def test_standalone_page_is_rtl(self):
        import create_review
        page = reco_render.write_review(self.folder)
        self.assertEqual(create_review.rtl_issues(page.read_text(encoding="utf-8")), [])

    def test_save_edits_backs_up_logs_and_revalidates(self):
        log = self.tmp / "edits.jsonl"
        res = reco_render.save("2026-10-08", "games", [{"slide": 3, "field": "why", "value": "מחכים, לתור"}],
                               drafts=self.tmp / "drafts", history_path=self.history_path, edits_log=log, render_png=False)
        self.assertEqual(res["changed"], 1)
        self.assertFalse(res["valid"])
        self.assertTrue(any(e["char"] == "," for e in res["errors"] if "char" in e))
        self.assertTrue((self.folder / "versions" / "v1" / rl.FILES["games"]).exists())
        self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 1)
        self.assertFalse(self.history_path.exists())  # invalid carousels never enter history
        self.assertIn("games.html", (self.folder / "review.html").read_text(encoding="utf-8"))
        self.assertIn("מחכים, לתור", (self.folder / "games.html").read_text(encoding="utf-8"))

    def test_bad_edits_are_refused(self):
        res = reco_render.save("2026-10-08", "games", [{"slide": 1, "field": "why", "value": "x"}], drafts=self.tmp / "drafts",
                               history_path=self.history_path, edits_log=self.tmp / "e.jsonl", render_png=False)
        self.assertIn("error", res)

    def test_finish_reco_cli_without_chrome(self):
        import nightly
        args = mock.Mock(folder=str(self.folder), no_png=True)
        with mock.patch.object(rl, "load_history", return_value={"carousels": []}), mock.patch.object(rl, "record_history") as rec:
            nightly.cmd_finish_reco(args)
        self.assertEqual(rec.call_count, 2)


class Render(Base):
    def test_slides_html_has_seven_rtl_slides_with_centred_images(self):
        out_dir, problems = reco_render.render(self.folder / rl.FILES["games"], png=False)
        html = (out_dir / "slides.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('<section class="slide'), 7)
        self.assertIn('<html lang="he" dir="rtl">', html)
        self.assertIn("object-fit:contain", html)
        self.assertEqual(html.count('class="main"'), 3 + 3 + 1)  # fan on slide 1, slides 3 to 5, LumeBook on 6

    @unittest.skipUnless(Path(lib.CHROME).exists(), "needs Google Chrome")
    def test_chrome_export_passes_the_layout_checks(self):
        out_dir, problems = reco_render.render(self.folder / rl.FILES["books"])
        self.assertEqual(problems, [])
        for n in range(1, 8):
            self.assertEqual(lib.png_size(out_dir / f"{n:02d}.png"), (1080, 1350))
        self.assertTrue((out_dir / "contact-sheet.png").exists())

    def test_render_problems_catch_distortion_and_off_centre(self):
        rep = [{"n": 3, "role": "recommendation", "lang": "he", "htmlDir": "rtl", "direction": "rtl", "blocks": [],
                "texts": [{"fit": "ok", "top": 140, "bottom": 300, "where": "title"}, {"fit": "ok", "top": 1012, "bottom": 1200, "where": "reason"}],
                "imgs": [{"src": "x", "loaded": True, "natural": [100, 100], "shown": [300, 200], "aspect_error": 0.5, "center_dx": 40, "share": 0.2, "top": 380, "bottom": 960}]}]
        probs = " ".join(reco_render.render_problems(rep))
        for word in ("distorted", "off centre", "too small"):
            self.assertIn(word, probs)


if __name__ == "__main__":
    unittest.main()
