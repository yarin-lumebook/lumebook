#!/usr/bin/env python3
"""Tests for the daily recommendation carousels (scripts/reco_lib.py, scripts/reco_render.py): the combined games and
books carousel (format mixed, from 14 Oct 2026) and the older separate games and books carousels.

    python3 -m unittest carousel/carousel-pipeline/tests/test_reco.py -v

games-carousel.json and books-carousel.json are copies of the first real example (drafts/2026-10-08);
reco-carousel.json (9 suggestions, 12 slides) is assembled from the 13 and 14 Oct drafts. Tests copy them
into a temp folder and draw placeholder images at every referenced path, so no real image, network call or
history file is touched (history goes to a temp file).
"""

import copy
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
            if fmt == rl.MIXED2:  # only a weekly batch pack has the second one (test_batch.py)
                continue
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

    def lay(self, car):
        """The slide layout of this carousel: its size comes from how many products it has."""
        return rl.layout(len(car["products"]) + 1)

    def make_car(self, fmt, n_options):
        """A valid carousel with n_options suggestions (the LumeBook book counted as one), built from the fixture:
        extra products are copies with their own ids and titles, fewer products drop the last ones."""
        car = copy.deepcopy(self.car(fmt))
        rec = [s for s in car["slides"] if s["role"] == "recommendation"]
        dev = next(c for c in car["claims"] if c["kind"] == "developmental" and c["slide"] > 2)
        products = car["products"]
        while len(products) < n_options - 1:
            k = len(products) + 1
            src = copy.deepcopy(products[k % len(rec) if k >= len(rec) else 0])
            src["id"] = f"{src['kind']}-extra{k}"
            src["title_he"] = f"{src['title_he']} {k}"
            src["type"] = f"{src['type']}_{k}"
            src["author"] = f"{src.get('author', '')}{k}" if src.get("author") else ""
            for sig in src["popularity_signals"]:
                sig["id"] = f"{sig['id']}-x{k}"
            products.append(src)
        del products[n_options - 1:]
        hook, frame, lumebook, close = car["slides"][0], car["slides"][1], next(s for s in car["slides"] if s["role"] == "lumebook"), car["slides"][-1]
        hook["body"] = ""
        if fmt == "books":
            hook["headline"] = f"{n_options} ספרי ילדים\nשעוזרים לילדים\nלספר סיפור"
        else:
            hook["headline"] = f"{n_options} משחקי קופסא\nשעוזרים לילדים\nלחכות לתור"
        lay = rl.layout(n_options)
        slides = [hook, frame]
        prod_iter = iter(products)
        claims = [c for c in car["claims"] if c["slide"] <= 2]
        for n in range(3, lay["close_slide"]):
            if n == lay["lumebook_slide"]:
                slides.append(dict(copy.deepcopy(lumebook), number=n))
                claims += [dict(copy.deepcopy(c), slide=n) for c in car["claims"] if c["slide"] == next(x["number"] for x in car["slides"] if x["role"] == "lumebook")]
                continue
            prod = next(prod_iter)
            tmpl = copy.deepcopy(rec[0])
            tmpl.update(number=n, product_id=prod["id"], headline=prod["title_he"], age=f"גיל {prod['official_age']['min']} עד 5")
            slides.append(tmpl)
            claims.append(dict(copy.deepcopy(dev), slide=n))
        slides.append(dict(close, number=lay["close_slide"]))
        car["slides"], car["claims"] = slides, claims
        return car


    def make_mixed(self, n_options, games=None):
        """A valid mixed carousel with n_options suggestions built from the 9-suggestion fixture: the first `games`
        games (default about half, at least 3) and enough books, games first, the LumeBook book second to last."""
        car = copy.deepcopy(self.car(rl.MIXED))
        all_games = [p for p in car["products"] if p["kind"] == "game"]
        all_books = [p for p in car["products"] if p["kind"] == "book"]
        g = games if games is not None else min(len(all_games), max(3, (n_options - 1) // 2))
        products = all_games[:g] + all_books[:n_options - 1 - g]
        return self.rebuild(car, products)

    def rebuild(self, car, products):
        """Lay out car's slides again for this product list (in this order), keeping each product's slide and claims."""
        old_rec = {s["product_id"]: s for s in car["slides"] if s["role"] == "recommendation"}
        old_lb = next(s for s in car["slides"] if s["role"] == "lumebook")
        n_options = len(products) + 1
        lay = rl.layout(n_options)
        hook, frame, close = copy.deepcopy(car["slides"][0]), copy.deepcopy(car["slides"][1]), copy.deepcopy(car["slides"][-1])
        hook["headline"] = re.sub(r"^\d+", str(n_options), hook["headline"])
        slides, claims = [hook, frame], [c for c in car["claims"] if c["slide"] <= 2]
        it = iter(products)
        for n in range(3, lay["close_slide"]):
            src = old_lb if n == lay["lumebook_slide"] else old_rec[next(it)["id"]]
            claims += [dict(copy.deepcopy(c), slide=n) for c in car["claims"] if c["slide"] == src["number"]]
            slides.append(dict(copy.deepcopy(src), number=n))
        slides.append(dict(close, number=lay["close_slide"]))
        car["products"], car["slides"], car["claims"] = products, slides, claims
        return car


class FixtureAndStructure(Base):
    def test_both_fixtures_are_valid(self):
        for fmt in rl.FORMATS:
            issues = self.check(load(fmt) if fmt == rl.MIXED2 else self.car(fmt), history={"carousels": []})
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
        r = self.lay(car)["rec_slides"]
        self.slide(car, r[1])["product_id"] = self.slide(car, r[0])["product_id"]
        self.assertIn("exactly once", messages(self.check(car)))

    def test_exact_product_name_on_the_slide(self):
        car = self.car()
        self.slide(car, 3)["headline"] = "משחק נהדר"
        self.assertIn("exact product name", messages(self.check(car)))

    def test_slides_need_why_and_how(self):
        car = self.car()
        self.slide(car, self.lay(car)["rec_slides"][1])["how"] = ""
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
    def test_lumebook_is_the_second_to_last_suggestion(self):
        car = self.car()
        lay = self.lay(car)
        self.assertEqual(lay["roles"][lay["lumebook_slide"]], "lumebook")
        self.assertEqual(lay["lumebook_slide"], lay["close_slide"] - 2)  # second to last suggestion
        s = self.slide(car, lay["lumebook_slide"])
        self.assertIn("LumeBook", s["headline"])  # ספר של LumeBook
        s["body"] = "ספר נחמד\nשבו הוא יוצא להרפתקה"
        self.assertIn("Yarin's format", messages(self.check(car)))

    def test_brand_once_on_its_slide_only(self):
        car = self.car()
        self.slide(car, 3)["why"] += "\nכמו בלומבוק"
        self.assertIn(f"LumeBook appears only on slide {self.lay(car)['lumebook_slide']}", messages(self.check(car)))

    def test_lumebook_slide_must_name_it(self):
        car = self.car()
        s = self.slide(car, self.lay(car)["lumebook_slide"])
        for f in ("headline", "body"):
            s[f] = lib.BRAND_RE.sub("ספר", s[f])
        self.assertIn("exactly once", messages(self.check(car)))

    def test_lumebook_twice_is_too_much(self):
        car = self.car()
        self.slide(car, self.lay(car)["lumebook_slide"])["body"] += "\nשוב לומבוק"
        self.assertIn("exactly once", messages(self.check(car)))

    def test_not_in_caption(self):
        car = self.car()
        car["caption"] += "\nלומבוק"
        self.assertIn("not in the caption", messages(self.check(car)))

    def test_no_sales_talk_on_the_lumebook_slide(self):
        for word in ("הנחה", "עכשיו", "בחינם", "₪"):
            car = self.car()
            self.slide(car, self.lay(car)["lumebook_slide"])["body"] += f"\nיש {word}"
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

    def test_slides_have_no_badges_and_show_the_site_3d_book(self):
        out_dir, _ = reco_render.render(self.folder / rl.FILES["games"], png=False)
        html = (out_dir / "slides.html").read_text(encoding="utf-8")
        self.assertNotIn('class="tag"', html)
        self.assertNotIn("מתוך 3", html)
        self.assertIn('class="main hero3d"', html)  # the homepage 3D book with the child photo circle
        self.assertIn("left:50%;transform:translateX(-50%)", html)  # the arrow sits in the middle

    def test_close_stays_useful_not_sales(self):
        car = self.car()
        self.slide(car, len(car["slides"]))["body"] += "\nקישור בתגובה"
        self.assertIn("sales slide", messages(self.check(car)))

    def test_close_has_a_light_prompt(self):
        car = self.car()
        s = self.slide(car, len(car["slides"]))
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
        car["claims"] = [c for c in car["claims"] if not (c["slide"] == self.lay(car)["rec_slides"][1] and c["kind"] == "developmental")]
        self.assertIn(f"slide {self.lay(car)['rec_slides'][1]} says why", messages(self.check(car)))
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
        self.assertNotIn("opened the previous", msg)  # the hook is one fixed template now, so it is not rotated

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
        self.assertIn('class="rp-slides rp-copy"', page)  # each slide's text sits under its preview
        for summary in ("המוצרים", "מקורות", "בדיקות"):
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

    def test_saved_edits_reach_the_next_nightly_run(self):
        log = self.tmp / "edits.jsonl"
        reco_render.save("2026-10-08", "games", [{"slide": 3, "field": "how", "value": "שחקו יחד אחרי ארוחת ערב"}],
                         drafts=self.tmp / "drafts", history_path=self.history_path, edits_log=log, render_png=False)
        with log.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"direction": "kid", "kind": "rewrite", "before": "a", "after": "b"}) + "\n")
        got = rl.recent_edits(path=log)
        self.assertEqual(len(got), 1)  # kid and expert edits stay with the pack
        self.assertEqual((got[0]["direction"], got[0]["slide"], got[0]["role"], got[0]["field"]), ("games", 3, "recommendation", "how"))
        self.assertEqual(got[0]["after"], "שחקו יחד אחרי ארוחת ערב")
        with mock.patch.object(rl, "recent_edits", return_value=got):
            ctx = rl.start_context("2026-10-08", self.folder, history={"carousels": []})
        self.assertEqual(ctx["recent_edits_learn_from_these"], got)

    def test_bad_edits_are_refused(self):
        res = reco_render.save("2026-10-08", "games", [{"slide": 1, "field": "why", "value": "x"}], drafts=self.tmp / "drafts",
                               history_path=self.history_path, edits_log=self.tmp / "e.jsonl", render_png=False)
        self.assertIn("error", res)

    def test_finish_reco_cli_without_chrome(self):
        import nightly
        args = mock.Mock(folder=str(self.folder), no_png=True)
        with mock.patch.object(rl, "load_history", return_value={"carousels": []}), mock.patch.object(rl, "record_history") as rec:
            nightly.cmd_finish_reco(args)
        self.assertEqual(rec.call_count, 1)  # from 14 Oct 2026 the night has one carousel: games and books together
        self.assertEqual(rec.call_args[0][0]["format"], rl.MIXED)

    def test_finish_reco_still_finishes_an_older_night(self):
        import nightly
        (self.folder / rl.FILES[rl.MIXED]).unlink()
        args = mock.Mock(folder=str(self.folder), no_png=True)
        with mock.patch.object(rl, "load_history", return_value={"carousels": []}), mock.patch.object(rl, "record_history") as rec:
            nightly.cmd_finish_reco(args)
        self.assertEqual(sorted(c[0][0]["format"] for c in rec.call_args_list), ["books", "games"])


class RandomSize(Base):
    def test_layout_for_every_size(self):
        for n in range(rl.OPTIONS_MIN, rl.OPTIONS_MAX + 1):
            lay = rl.layout(n)
            self.assertEqual(lay["total"], n + 3)
            self.assertEqual(list(lay["roles"].values()).count("lumebook"), 1)
            self.assertEqual(len(lay["rec_slides"]), n - 1)  # the LumeBook book counts as one of the n
            self.assertEqual(lay["roles"][lay["lumebook_slide"]], "lumebook")
            self.assertEqual(lay["lumebook_slide"], lay["close_slide"] - 2)  # second to last suggestion
            self.assertEqual(lay["roles"][1], "hook")
            self.assertEqual(lay["roles"][lay["close_slide"]], "close")

    def test_every_size_from_3_to_7_validates(self):
        for fmt in rl.LEGACY_FORMATS:
            for n in range(rl.OPTIONS_MIN, rl.OPTIONS_MAX + 1):
                car = self.make_car(fmt, n)
                issues = self.check(car)
                self.assertEqual(errors(issues), [], f"{fmt} with {n} suggestions:\n{messages(issues)}")
                self.assertEqual(len(car["slides"]), n + 3)

    def test_out_of_range_sizes_are_refused(self):
        car = self.make_car("books", 3)
        car["products"] = car["products"][:1]
        self.assertIn("3 to 7", messages(self.check(car)))
        car = self.make_car("books", 7)
        car["products"].append(copy.deepcopy(car["products"][0]))
        car["products"][-1]["id"] = "book-extra99"
        self.assertIn("3 to 7", messages(self.check(car)))

    def test_slide_count_must_match_the_suggestions(self):
        car = self.make_car("games", 4)
        car["slides"].pop(2)
        for i, s in enumerate(car["slides"], 1):
            s["number"] = i
        self.assertIn("need exactly 7 slides", messages(self.check(car)))

    def test_the_hook_is_always_the_template(self):
        car = self.make_car("books", 5)
        hook = self.slide(car, 1)
        self.assertEqual(errors(self.check(car)), [])
        for headline, expect in (("שוב אותו ספר?", "the hook is always"),
                                 ("4 ספרי ילדים\nשעוזרים לילדים\nלספר סיפור", "the hook says 4"),
                                 ("5 ספרי ילדים לגילאי 4-5\nשעוזרים לילדים\nלספר סיפור", "no ages in the hook"),
                                 ("5 ספרים\nשעוזרים לילדים\nלספר סיפור", "the hook is always")):
            hook["headline"] = headline
            self.assertIn(expect, messages(self.check(car)), headline)
        hook["headline"] = "5 ספרי ילדים\nשעוזרים לילדים\nלספר סיפור"
        hook["body"] = "ועוד שורה"
        self.assertIn("no body", messages(self.check(car)))

    def test_games_hook_template(self):
        car = self.make_car("games", 3)
        self.assertEqual(errors(self.check(car)), [])
        self.slide(car, 1)["headline"] = "3 רעיונות לגיל 4 עד 5\nשמתרגלים תור"
        self.assertIn("משחקי קופסא ש", messages(self.check(car)))

    def test_tonights_draw_is_enforced_when_it_exists(self):
        lib.write_json(self.folder / rl.SLOTS_FILE, {"games": 5, "books": 5})
        car = self.make_car("games", 3)
        self.assertIn("tonight's random draw for games is 5", messages(self.check(car)))
        self.assertEqual(errors(self.check(self.make_car("games", 5))), [])

    def test_draw_is_random_in_range_and_stable_on_rerun(self):
        """The nightly draw is the combined carousel's size: 7 to 9 suggestions, so 10 to 12 slides."""
        import random
        seen = set()
        for seed in range(300):
            folder = self.tmp / f"d{seed}"
            folder.mkdir()
            first = rl.draw_slots(folder, rng=random.Random(seed))
            self.assertEqual(list(first), [rl.MIXED])  # only the combined carousel is drawn
            self.assertEqual(rl.draw_slots(folder, rng=random.Random(seed + 1000)), first)  # a rerun keeps the night's draw
            for v in first.values():
                self.assertTrue(7 <= v <= 9)
                self.assertTrue(10 <= rl.layout(v)["total"] <= 12)
                seen.add(v)
        self.assertEqual(seen, set(range(7, 10)))

    def test_an_older_draw_file_is_topped_up_with_the_mixed_size(self):
        lib.write_json(self.folder / rl.SLOTS_FILE, {"games": 4, "books": 5})
        got = rl.draw_slots(self.folder)
        self.assertTrue(7 <= got[rl.MIXED] <= 9)
        saved = json.loads((self.folder / rl.SLOTS_FILE).read_text(encoding="utf-8"))
        self.assertEqual((saved["games"], saved["books"]), (4, 5))  # an older night's draw stays as it was

    def test_start_context_gives_the_sizes_and_slides(self):
        (self.tmp / "start").mkdir()
        ctx = rl.start_context("2026-10-15", self.tmp / "start", history={"carousels": []})
        n = ctx["suggestions"]["tonight"]
        self.assertTrue(7 <= n <= 9)
        self.assertEqual(ctx["suggestions"]["products_tonight"], n - 1)
        self.assertEqual(len(ctx["suggestions"]["slides_tonight"]), n + 3)
        self.assertEqual(ctx["suggestions"]["slides_tonight"][str(n + 1)], "lumebook")
        self.assertTrue(ctx["write_to"].endswith("reco-carousel.json"))
        self.assertNotIn("write_games_to", ctx)
        self.assertTrue(ctx["example"].endswith("reco-carousel.json"))
        self.assertIn("משחקים וספרים", ctx["hook_template"])

    def test_render_shows_up_to_three_covers_in_the_hook_and_drops_old_slides(self):
        car = self.make_car("books", 7)
        lib.write_json(self.folder / rl.FILES["books"], car)
        stale = self.folder / "books" / "12.png"
        stale.parent.mkdir(exist_ok=True)
        stale.write_bytes(b"x")
        out_dir, _ = reco_render.render(self.folder / rl.FILES["books"], png=False)
        html = (out_dir / "slides.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('<section class="slide'), 10)
        self.assertEqual(html.count('class="card" style="left:'), 3)
        self.assertEqual(html.count('class="main'), 3 + 6 + 1)
        self.assertFalse(stale.exists())


class BigNumberHook(Base):
    def test_hook_number_is_drawn_big_and_ages_are_gone(self):
        out_dir, _ = reco_render.render(self.folder / rl.FILES["games"], png=False)
        html = (out_dir / "slides.html").read_text(encoding="utf-8")
        n = len(self.car()["products"]) + 1
        self.assertIn(f'<div class="bignum" data-f="headline" data-join="space">{n}</div>', html)
        self.assertNotIn("לגילאי", self.car()["slides"][0]["headline"])


class PluralAndClose(Base):
    def test_always_both_parents_in_the_plural(self):
        car = self.car("books")
        car["addressee"] = "mom"
        self.assertIn("always talk to both parents", messages(self.check(car)))
        for field, value, expect in (("how", "שאלי מה יקרה", "feminine singular command"),
                                     ("how", "תנו לילד לספר מהציורים", "talks about one child"),
                                     ("how", "שאלו מה עובד לך", "talks to one parent")):
            car = self.car("books")
            n = self.lay(car)["rec_slides"][0]
            self.slide(car, n)[field] = value
            self.assertIn(expect, messages(self.check(car)), value)

    def test_quotes_and_titles_may_stay_singular(self):
        car = self.car("books")
        n = self.lay(car)["rec_slides"][0]
        self.slide(car, n)["how"] = "שאלו ״מה הוא פגש?״\nובקשו מהילדים לספר"
        self.assertNotIn("talks about one child", messages(self.check(car)))
        self.assertNotIn("singular pronoun", messages(self.check(car), "WARN"))

    def test_close_is_only_the_save_and_comment_lines(self):
        car = self.car()
        last = self.slide(car, len(car["slides"]))
        self.assertEqual(last["body"], "")
        last["body"] = "תור קצר וחוק אחד ברור"
        self.assertIn("only the save and comment lines", messages(self.check(car)))

    def test_close_background_is_every_suggestion_under_purple(self):
        out_dir, _ = reco_render.render(self.folder / rl.FILES["books"], png=False)
        html = (out_dir / "slides.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('class="t"><img class="bg"'), 12)
        self.assertIn('<div class="purple"></div>', html)
        car = self.car("books")
        for f in [p["image"]["file"] for p in car["products"]] + [car["lumebook"]["image"]["file"]]:
            self.assertIn(Path(f).name, html.split('class="collage"')[1])


class Render(Base):
    def test_slides_html_has_one_rtl_slide_per_slide_with_centred_images(self):
        out_dir, problems = reco_render.render(self.folder / rl.FILES["games"], png=False)
        html = (out_dir / "slides.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('<section class="slide'), len(self.car()["slides"]))
        self.assertIn('<html lang="he" dir="rtl">', html)
        self.assertIn("object-fit:contain", html)
        n_products = len(self.car()["products"])
        self.assertEqual(html.count('class="main'), min(3, n_products) + n_products + 1)  # the hook fan, the products, the LumeBook book

    @unittest.skipUnless(lib.CHROME, "needs Google Chrome")
    def test_chrome_export_passes_the_layout_checks(self):
        out_dir, problems = reco_render.render(self.folder / rl.FILES["books"])
        self.assertEqual(problems, [])
        for n in range(1, len(self.car("books")["slides"]) + 1):
            self.assertEqual(lib.png_size(out_dir / f"{n:02d}.png"), (1080, 1350))
        self.assertTrue((out_dir / "contact-sheet.png").exists())

    def test_render_problems_catch_distortion_and_off_centre(self):
        rep = [{"n": 3, "role": "recommendation", "lang": "he", "htmlDir": "rtl", "direction": "rtl", "blocks": [],
                "texts": [{"fit": "ok", "top": 140, "bottom": 300, "where": "title"}, {"fit": "ok", "top": 1012, "bottom": 1200, "where": "reason"}],
                "imgs": [{"src": "x", "loaded": True, "natural": [100, 100], "shown": [300, 200], "aspect_error": 0.5, "center_dx": 40, "share": 0.2, "top": 380, "bottom": 960}]}]
        probs = " ".join(reco_render.render_problems(rep))
        for word in ("distorted", "off centre", "too small"):
            self.assertIn(word, probs)


class BoldLook(Base):
    """Hook Studio (10 Oct 2026): games and books get the highlight, the bold renderer and the hook wordings."""

    def bold_car(self, fmt="games"):
        car = self.car(fmt)
        car["generated_at"] = "2026-10-10T20:30:00+03:00"
        return car

    def test_old_carousels_need_no_highlight(self):
        self.assertEqual(errors(self.check(self.car("games"))), [])
        self.assertFalse(reco_render.is_bold(self.car("games")))

    def test_new_carousels_need_a_highlight_on_the_hook_and_the_frame(self):
        car = self.bold_car()
        msgs = messages(self.check(car))
        self.assertIn("slide-1/highlight", msgs)
        self.assertIn("slide-2/highlight", msgs)

    def test_highlight_is_whole_words_from_the_headline(self):
        car = self.bold_car()
        hook = self.slide(car, 1)
        tail = lambda text: " ".join(lib.lines_of(text)[-1].split()[-2:])
        last = tail(hook["headline"])
        hook["highlight"] = last
        self.slide(car, 2)["highlight"] = tail(self.slide(car, 2)["headline"])
        self.assertEqual(messages(self.check(car)).count("highlight"), 0, messages(self.check(car)))
        hook["highlight"] = last[1:]
        self.assertIn("cuts a word", messages(self.check(car)))
        hook["highlight"] = "מילה שלא בכותרת"
        self.assertIn("not in the headline", messages(self.check(car)))

    def test_a_product_title_is_never_highlighted(self):
        car = self.bold_car()
        rec = next(s for s in car["slides"] if s["role"] == "recommendation")
        rec["highlight"] = rec["headline"].split()[0]
        self.assertIn("only the hook, the frame and the close slide", messages(self.check(car)))

    def test_the_hook_sentence_stays_the_same(self):
        car = self.bold_car()
        self.slide(car, 1)["headline"] = "משחקים שכדאי להכיר\nבשביל הילדים"
        self.assertIn("the hook is always", messages(self.check(car)))

    def test_alternatives_are_audience_text(self):
        car = self.bold_car()
        car["hook_alternatives"] = ["4 משחקי קופסא, שמלמדים", "4 משחקי קופסא שבהם הילדים מתכננים"]
        self.assertIn("hook_alternatives[0]", messages(self.check(car)))
        car["hook_alternatives"] = []
        self.assertIn("hook_alternatives", messages(self.check(car), "WARN"))

    def test_renderer_marks_the_phrase_once(self):
        html = reco_render.lines_html("4 משחקי קופסא\nשבהם הילדים\nמתכננים כמה צעדים קדימה", "כמה צעדים קדימה")
        self.assertEqual(html.count('class="hl"'), 1)
        self.assertIn('<span class="hl">כמה צעדים קדימה</span>', html)
        self.assertNotIn('class="hl"', reco_render.lines_html("שורה אחת"))

    def test_look_follows_the_highlights(self):
        car = self.bold_car()
        self.slide(car, 1)["highlight"] = lib.lines_of(self.slide(car, 1)["headline"])[-1]
        html = reco_render.build_slides_html(car, self.folder / "games", self.folder)
        self.assertIn('class="look-bold"', html)
        self.assertIn('class="look-classic"', reco_render.build_slides_html(self.car("games"), self.folder / "games", self.folder))


class ValueHook(Base):
    """Yarin, 11 Oct 2026: the games and books hook says what value they give."""

    def test_a_hook_with_no_value_verb_is_flagged(self):
        car = self.car()
        car["generated_at"] = "2026-10-11T01:00:00+03:00"
        self.slide(car, 1)["headline"] = "4 משחקי קופסא\nשבהם הילדים\nמתכננים כמה צעדים קדימה"
        self.assertIn("what the value is", messages(self.check(car), "WARN"))
        self.slide(car, 1)["headline"] = "4 משחקי קופסא\nשיעזרו להם\nלתכנן כמה צעדים קדימה"
        self.assertNotIn("what the value is", messages(self.check(car), "WARN"))

    def test_old_carousels_are_not_flagged(self):
        self.assertNotIn("what the value is", messages(self.check(self.car()), "WARN"))


class LumebookCover(Base):
    """Yarin, 10 Oct 2026: the LumeBook picture shows the idea of the slide's line (the catalogue book's own cover)."""

    COVER = "https://lumebook.com/book_covers/girl/B54_girl.avif"

    def cover_car(self, fmt="games"):
        car = self.car(fmt)
        car["generated_at"] = "2026-10-11T00:10:00+03:00"
        car["lumebook"]["image"].update(image_url=self.COVER, page_url="https://lumebook.com/IL/he/books/54",
                                         depicts="A girl holds a glowing compass whose light rays point in many directions: the idea of seeing where each choice leads")
        car["lumebook"]["catalogue_book_id"] = 54
        car["lumebook"]["catalogue_book"] = "המצפן של הבחירות (גילאי 4-8)"
        return car

    def lumebook_msgs(self, car):
        return "\n".join(str(i) for i in errors(self.check(car)) if "lumebook/" in str(i))

    def test_new_carousels_must_not_use_the_homepage_render(self):
        car = self.car()
        car["generated_at"] = "2026-10-11T00:10:00+03:00"
        self.assertIn("catalogue book whose idea", self.lumebook_msgs(car))
        self.assertEqual(self.lumebook_msgs(self.car()), "")  # an old carousel keeps its hero render

    def test_a_cover_with_its_book_and_description_passes(self):
        self.assertEqual(self.lumebook_msgs(self.cover_car()), "")

    def test_the_cover_must_match_the_book_id_and_the_folder(self):
        car = self.cover_car()
        car["lumebook"]["catalogue_book_id"] = 50
        self.assertIn("the cover is book 54", self.lumebook_msgs(car))
        car = self.cover_car()
        car["lumebook"]["image"]["image_url"] = "https://lumebook.com/book_covers/boy/B54_girl.avif"
        self.assertIn("must agree", self.lumebook_msgs(car))

    def test_the_picture_must_be_described(self):
        car = self.cover_car()
        car["lumebook"]["image"]["depicts"] = "ok"
        self.assertIn("depicts", self.lumebook_msgs(car))
        car = self.cover_car()
        car["lumebook"]["catalogue_book"] = ""
        self.assertIn("name the catalogue book", self.lumebook_msgs(car))

    def test_the_cover_is_drawn_as_a_cover(self):
        car = self.cover_car()
        html = reco_render.build_slides_html(car, self.folder / "games", self.folder)
        self.assertNotIn('class="main hero3d"', html)
        # flat in a white card like the other books, not a 3D object (Yarin, 14 Oct 2026)
        self.assertNotIn("book3d", html)
        slide = next(part for part in html.split('<section') if 'data-role="lumebook"' in part)
        self.assertIn('<div class="card"><img class="main"', slide)


class Mixed(Base):
    """Yarin, 14 Oct 2026: "combine the book and games to one carousel. 10-20 slides"."""

    def test_the_fixture_is_valid_with_twelve_slides(self):
        car = self.car(rl.MIXED)
        self.assertEqual(car["format"], rl.MIXED)
        self.assertEqual(len(car["slides"]), 12)
        issues = self.check(car, history={"carousels": []})
        self.assertEqual(errors(issues), [], messages(issues))

    def test_every_size_from_10_to_12_slides_validates(self):
        for n in range(7, 10):
            car = self.make_mixed(n)
            issues = self.check(car)
            self.assertEqual(errors(issues), [], f"mixed with {n} suggestions:\n{messages(issues)}")
            self.assertEqual(len(car["slides"]), n + 3)
            self.assertTrue(10 <= len(car["slides"]) <= 12)

    def test_fewer_than_10_or_more_than_12_slides_are_refused(self):
        car = self.make_mixed(7)
        car = self.rebuild(car, car["products"][:-1])  # 6 suggestions, 9 slides
        self.assertIn("7 to 9", messages(self.check(car)))
        car = self.make_mixed(9)
        extra = copy.deepcopy(car["products"][-1])
        extra.update(id="book-extra99", title_he="ספר נוסף", type="extra_type")
        for sig in extra["popularity_signals"]:
            sig["id"] += "-x99"
        car["products"].append(extra)
        self.assertIn("7 to 9", messages(self.check(car)))  # 10 suggestions, 13 slides

    def test_at_least_three_games_and_three_books(self):
        car = self.make_mixed(9, games=2)  # 2 games, 6 books
        self.assertIn("at least 3 games", messages(self.check(car)))
        car = self.make_mixed(9, games=6)  # 6 games, 2 books
        self.assertIn("at least 3 books", messages(self.check(car)))
        self.assertEqual(errors(self.check(self.make_mixed(7, games=3))), [])

    def test_each_kind_keeps_its_maker_rule(self):
        car = self.make_mixed(9)
        book = next(p for p in car["products"] if p["kind"] == "book")
        book["author"] = ""
        self.assertIn("books need the author", messages(self.check(car)))
        car = self.make_mixed(9)
        next(p for p in car["products"] if p["kind"] == "game")["manufacturer"] = ""
        self.assertIn("games need the manufacturer", messages(self.check(car)))

    def test_games_first_then_books_and_lumebook_second_to_last(self):
        car = self.make_mixed(9)
        lay = self.lay(car)
        self.assertEqual(lay["lumebook_slide"], len(car["slides"]) - 2)
        kinds = [next(p["kind"] for p in car["products"] if p["id"] == s["product_id"]) for s in car["slides"] if s["role"] == "recommendation"]
        self.assertEqual(kinds, sorted(kinds, key=lambda k: k != "game"))
        self.assertEqual(self.slide(car, lay["lumebook_slide"] + 1)["role"], "recommendation")  # a book follows LumeBook
        # a book before a game is refused
        games = [p for p in car["products"] if p["kind"] == "game"]
        books = [p for p in car["products"] if p["kind"] == "book"]
        mixed_up = self.rebuild(copy.deepcopy(car), [books[0]] + games + books[1:])
        self.assertIn("every game first", messages(self.check(mixed_up)))
        # LumeBook anywhere else is refused
        car = self.make_mixed(9)
        a, b = self.slide(car, lay["lumebook_slide"]), self.slide(car, 5)
        a_num, b_num = a["number"], b["number"]
        car["slides"][a_num - 1], car["slides"][b_num - 1] = dict(b, number=a_num), dict(a, number=b_num)
        self.assertIn(f"slide {b_num} must be recommendation", messages(self.check(car)))

    def test_hook_template_counts_every_suggestion(self):
        car = self.make_mixed(8)
        hook = self.slide(car, 1)
        self.assertTrue(hook["headline"].startswith("8 משחקים וספרים"))
        self.assertEqual(errors(self.check(car)), [])
        for headline, expect in (("8 משחקי קופסא\nלגילאי 5-6 שיעזרו להם\nלהכיר אותיות ומספרים", "X משחקים וספרים לגילאי A-B ש..."),
                                 ("8 ספרי ילדים\nלגילאי 5-6 שיעזרו להם\nלהכיר אותיות ומספרים", "X משחקים וספרים לגילאי A-B ש..."),
                                 ("7 משחקים וספרים\nלגילאי 5-6 שיעזרו להם\nלהכיר אותיות ומספרים", "the hook says 7"),
                                 ("8 משחקים וספרים\nשיעזרו להם\nלהכיר אותיות ומספרים", "X משחקים וספרים לגילאי A-B ש..."),  # ages missing
                                 ("8 משחקים וספרים\nלגילאי 4-6 שיעזרו להם\nלהכיר אותיות ומספרים", "write «לגילאי 5-6»"),
                                 ("8 משחקים וספרים\nלגילאי 5-6 שיעזרו להם להכיר\nאותיות ומספרים ולספור\nעד עשר ולחרוז ביחד", "max 12")):
            hook["headline"] = headline
            self.assertIn(expect, messages(self.check(car)), headline)
        self.assertTrue(rl.HOOK_TEMPLATE_RE[rl.MIXED].match("9 משחקים וספרים לגילאי 5-6 שיעזרו להם להכיר אותיות"))
        self.assertTrue(rl.HOOK_TEMPLATE_RE[rl.MIXED].match("9 משחקים וספרים לגיל 4 שעוזרים לילדים לחכות"))
        self.assertFalse(rl.HOOK_TEMPLATE_RE[rl.MIXED].match("9 משחקים שיעזרו להם"))
        self.assertTrue(rl.HOOK_TEMPLATE_RE["games"].match("4 משחקי קופסא שעוזרים לילדים לחכות"))  # older nights unchanged
        self.assertIn("no ages in the hook", messages(self.check(dict(self.car("games"), slides=[dict(self.car("games")["slides"][0], headline="4 משחקי קופסא לגילאי 5-6 שעוזרים לילדים לחכות")] + self.car("games")["slides"][1:]))))

    def test_old_formats_still_validate_and_render(self):
        for fmt in rl.LEGACY_FORMATS:
            self.assertEqual(errors(self.check(self.car(fmt), history={"carousels": []})), [], fmt)
            out_dir, _ = reco_render.render(self.folder / rl.FILES[fmt], png=False)
            self.assertEqual(out_dir.name, fmt)
            html = (out_dir / "slides.html").read_text(encoding="utf-8")
            self.assertNotIn('class="kind"', html)  # the kind tag is for the combined carousel only
        car = self.car("games")
        car["products"].append(copy.deepcopy(self.car("books")["products"][0]))
        self.assertIn("recommends only games", messages(self.check(car)))

    def test_the_draw_is_enforced(self):
        lib.write_json(self.folder / rl.SLOTS_FILE, {rl.MIXED: 9})
        self.assertIn("tonight's random draw for mixed is 9", messages(self.check(self.make_mixed(8))))
        self.assertEqual(errors(self.check(self.make_mixed(9))), [])

    def test_cream_background_except_the_close_slide(self):
        """Yarin, 14 Oct 2026: "go back to cream"; the close slide stays as it was."""
        html = reco_render.build_slides_html(self.car(rl.MIXED), self.folder / "reco", self.folder)
        before, close = html.split('data-role="close" data-format')
        self.assertIn("--bg:250,246,239", before)
        self.assertNotIn("--bg:241,236,255", before)
        self.assertIn("--bg:241,236,255", close.split("</section>")[0] + html.split('data-role="close"')[0][-400:])

    def test_plain_text_look_except_the_close_slide(self):
        """Yarin, 14 Oct 2026: plain dark headlines with the number inside the sentence, no colour block, close slide as it was."""
        car = self.car(rl.MIXED)
        html = reco_render.build_slides_html(car, self.folder / "reco", self.folder)
        self.assertIn('class="look-bold look-plain"', html)
        self.assertNotIn('class="bignum"', html)
        self.assertIn("9 משחקים וספרים", html)  # the number stays in the hook sentence
        self.assertNotIn('class="hl"', html.split('data-role="close" data-format')[0])  # no colour block before the close slide
        self.assertIn("Heebo-Bold.ttf", html)
        car["slides"][-1]["highlight"] = "שוב ושוב"
        html = reco_render.build_slides_html(car, self.folder / "reco", self.folder)
        self.assertIn('<span class="hl">שוב ושוב</span>', html.split('data-role="close" data-format')[1])  # the close slide keeps its look
        self.assertEqual(errors(self.check(car)), [])  # highlights stay valid data
        games = reco_render.build_slides_html(self.car("games"), self.folder / "games", self.folder)
        self.assertNotIn('look-plain">', games)  # older carousels keep their look

    def test_twelve_slides_render_with_kind_tags_and_a_full_collage(self):
        out_dir, problems = reco_render.render(self.folder / rl.FILES[rl.MIXED], png=False)
        self.assertEqual(out_dir.name, "reco")
        html = (out_dir / "slides.html").read_text(encoding="utf-8")
        car = self.car(rl.MIXED)
        self.assertEqual(html.count('<section class="slide'), 12)
        self.assertEqual(html.count('class="kind" data-kind="game"'), 4)
        self.assertEqual(html.count('class="kind" data-kind="book"'), 4)
        self.assertEqual(html.count('class="t"><img class="bg"'), 12)  # 9 suggestions fill the 3 x 4 collage
        collage = html.split('class="collage"')[1]
        for f in [p["image"]["file"] for p in car["products"]] + [car["lumebook"]["image"]["file"]]:
            self.assertIn(Path(f).name, collage)
        fan = [p["kind"] for p in reco_render.fan_products(car)]
        self.assertEqual(fan, ["game", "book", "game"])  # the hook shows both kinds
        self.assertEqual(html.count(ARROW_MARK), 11)  # every slide but the last has the arrow

    @unittest.skipUnless(lib.CHROME, "needs Google Chrome")
    def test_chrome_export_of_twelve_slides(self):
        out_dir, problems = reco_render.render(self.folder / rl.FILES[rl.MIXED])
        self.assertEqual(problems, [])
        for n in range(1, 13):
            self.assertEqual(lib.png_size(out_dir / f"{n:02d}.png"), (1080, 1350))
        self.assertTrue((out_dir / "contact-sheet.png").exists())

    def test_review_page_scrolls_sideways_on_a_phone(self):
        reco_render.render(self.folder / rl.FILES[rl.MIXED], png=False)
        page = reco_render.write_review(self.folder)
        reco = (self.folder / "reco.html").read_text(encoding="utf-8")
        self.assertIn('data-format="mixed" data-dir="reco"', reco)
        self.assertIn('aria-selected="true">משחקים וספרים', reco)
        self.assertIn("12 שקופיות · 4 משחקים · 4 ספרים", reco)
        self.assertIn("grid-auto-flow:column", reco)
        self.assertIn("overflow-x:auto", reco)
        self.assertIn('href="reco.html"', page.read_text(encoding="utf-8"))
        self.assertEqual(reco.count('class="rp-slide" data-n='), 12)

    def test_a_night_without_a_carousel_links_the_newest_combined_one(self):
        other = self.tmp / "drafts" / "2026-10-15"
        other.mkdir()
        tabs = reco_render.tabs_html(other, "pack")
        self.assertIn('href="../2026-10-08/reco.html"', tabs)
        self.assertNotIn("games.html", tabs)  # the older separate tabs show only on their own nights

    def test_edits_on_the_combined_page_are_saved_and_learnt(self):
        log = self.tmp / "edits.jsonl"
        res = reco_render.save("2026-10-08", rl.MIXED, [{"slide": 3, "field": "how", "value": "תנו להם להיות הקופה\nולספור בקול כל שטר"}],
                               drafts=self.tmp / "drafts", history_path=self.history_path, edits_log=log, render_png=False)
        self.assertEqual(res["changed"], 1, res)
        self.assertTrue(res["valid"], res)
        self.assertTrue((self.folder / "versions" / "v1" / rl.FILES[rl.MIXED]).exists())
        self.assertEqual(rl.recent_edits(path=log)[0]["direction"], rl.MIXED)
        self.assertEqual(rl.load_history(self.history_path)["carousels"][0]["format"], rl.MIXED)

    def test_rotation_looks_at_games_books_and_mixed(self):
        car = self.car(rl.MIXED)
        books_entry = rl.history_entry(self.car("books"))
        books_entry.update(date="2026-10-12", skill=car["stage"]["skill"], stage_id="other")
        games_entry = rl.history_entry(self.car("games"))
        games_entry.update(date="2026-10-12", products=[{"id": "game-x", "kind": "game", "title_he": car["products"][0]["title_he"]}])
        h = {"carousels": [books_entry, games_entry]}
        msg = messages(self.check(car, h))
        self.assertIn("rotate the skill", msg)  # a skill an older books carousel used blocks the combined one
        self.assertIn(f"products/{car['products'][0]['id']}: recommended on 2026-10-12", msg)  # same title from a games entry
        ctx = rl.rotation_context(h, "2026-10-14", rl.NIGHTLY_FORMATS)
        self.assertIn(car["stage"]["skill"], ctx[rl.MIXED]["blocked_skills"])
        self.assertIn(car["products"][0]["title_he"], ctx[rl.MIXED]["recent_titles"])
        self.assertTrue(any(t in ctx[rl.MIXED]["recent_titles"] for t in [p["title_he"] for p in self.car("books")["products"]]))
        # an older games carousel still rotates only against games
        self.assertNotIn("rotate the skill", messages(self.check(self.car("games"), {"carousels": [books_entry]})))

    def test_history_records_the_kind_of_each_product(self):
        rl.record_history(self.car(rl.MIXED), self.history_path)
        entry = rl.load_history(self.history_path)["carousels"][0]
        self.assertEqual(entry["format"], rl.MIXED)
        self.assertEqual(sorted({p["kind"] for p in entry["products"]}), ["book", "game"])

    def test_backup_moves_the_combined_files(self):
        out_dir, _ = reco_render.render(self.folder / rl.FILES[rl.MIXED], png=False)
        target = rl.backup_existing(self.folder)
        self.assertTrue((target / rl.FILES[rl.MIXED]).exists())
        self.assertTrue((target / "reco" / "slides.html").exists())


ARROW_MARK = '<div class="arrow">'


if __name__ == "__main__":
    unittest.main()
