#!/usr/bin/env python3
"""Edit a nightly pack from its review page and save it back.

    python3 carousel/carousel-pipeline/scripts/review_server.py              # newest pack
    python3 carousel/carousel-pipeline/scripts/review_server.py --date 2026-10-08 --port 8777
    python3 carousel/carousel-pipeline/scripts/review_server.py --no-cloud  # skip the GitHub check

On start it first brings down any cloud night that is not here yet (cloud_sync.py: the nightly/DATE branches the cloud
routine pushes), so the newest page may be one the cloud made overnight. The row of dates on every page is redrawn
on each load, so older pages list the new nights too.

Open the printed address. Every slide headline and body, the caption, the CTA and the option title
become editable in place. "שמירה" (or Cmd+S) sends the changes here, and this server:

1. copies the current pack.json, review.html and review.md to drafts/DATE/versions/vN/ (nothing is lost)
2. applies the edits to pack.json (the CTA also updates the last slide, the caption's last line and the code word)
   and logs every copy edit (before and after) to .claude/skills/lumebook-hebrew-voice/examples/edits.jsonl,
   so the voice skill learns from Yarin's own changes
3. validates with the same rules as the nightly run and saves even if something fails, so no typing is lost
4. rebuilds review.html and review.md, and updates history.json when the pack is valid
5. returns the errors, which the page shows next to the exact field

Story packs (copy_style "story", story-format.md, 29 Oct 2026) also take a slide's label and its scene (scene_action,
scene_setting), and a body keeps its markup and one empty line as a paragraph gap. Labels are logged for the voice
skill like headlines and bodies; scenes are picture briefs and are not. /assets/fonts/*.woff2 falls back to
shared/brand/fonts (Varela Round, the story look) when the pipeline has no copy.

/ is Carousel Machine itself (studio.py): every carousel of the week on one page, edited in place through /api/save and
/api/save-reco, graded through /api/grade (grades.json) and produced through /api/production/* (producer.py,
productions.json); /api/production/postiz sends a finished one to Postiz, scheduled or as a draft (postiz_export.py). /api/state is
what the page reloads.

Listens on 127.0.0.1 only. Writes under carousel/carousel-pipeline/drafts/ and approved/, and to grades.json and productions.json.
Standard library only.
"""

import argparse
import os
import json
import re
import shutil
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch  # noqa: E402
import carousel_lib as lib  # noqa: E402
import cloud_sync  # noqa: E402
import create_review  # noqa: E402
import grades  # noqa: E402
import producer  # noqa: E402
import studio  # noqa: E402
import validate_pack  # noqa: E402

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FIELDS = {"headline", "body", "highlight", "caption", "cta", "title"}
STORY_FIELDS = {"label", "scene_action", "scene_setting"}   # story packs only (story-format.md, 29 Oct 2026)
DAY_PAGE_RE = re.compile(r"^/drafts/\d{4}-\d{2}-\d{2}/[\w-]+\.html$")
DAYS_RE = re.compile(r'<span class="rv-days" aria-label="תאריכים">.*?</span>', re.S)


def clean(text):
    return "\n".join(line.strip() for line in str(text).replace(" ", " ").splitlines() if line.strip())


def clean_keep_gaps(text):
    """A story body: lines trimmed, one empty line kept as the paragraph gap (story-format.md 3), none at the ends."""
    out = []
    for line in str(text).replace("\u00a0", " ").splitlines():
        line = line.strip()
        if line or (out and out[-1]):
            out.append(line)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


def cta_slide_lines(cta):
    w = lib.collapse(cta).split()
    return "\n".join(part for part in (" ".join(w[:3]), " ".join(w[3:7]), " ".join(w[7:])) if part)


def apply_edits(pack, edits):
    """Apply edits from the page. Returns a list of changes (option, field, slide, before, after).
    Raises ValueError on a bad edit."""
    options = {v["id"]: v for d in pack["directions"] for v in d["versions"]}
    story = create_review.story_applies(pack)
    changes = []
    for e in edits:
        v = options.get(e.get("option"))
        field = e.get("field")
        if v is None or field not in FIELDS | (STORY_FIELDS if story else set()):
            raise ValueError(f"unknown option or field: {e.get('option')} {field}")
        value = clean_keep_gaps(e.get("value", "")) if story and field == "body" else clean(e.get("value", ""))
        change = {"option": v["id"], "field": field, "slide": None}
        if field in STORY_FIELDS:   # a story slide's label (audience copy) or its scene (the picture brief, English)
            n = e.get("slide")
            if not isinstance(n, int) or not 1 <= n <= len(v["slides"]):
                raise ValueError(f"bad slide number {n}")
            s = v["slides"][n - 1]
            if field == "label":
                if n in (1, len(v["slides"])) and value:
                    raise ValueError("the cover and the save slide have no label")
                before = s.get("label", "")
                if before != value:
                    if value:
                        s["label"] = value
                    else:
                        s.pop("label", None)
                    changes.append({**change, "slide": n, "role": s.get("role"), "before": before, "after": value})
            else:
                if n == 1:
                    raise ValueError("slide 1's picture is the option's image brief")
                key = field.split("_", 1)[1]
                scene = s.get("scene") if isinstance(s.get("scene"), dict) else {"action": str(s.get("scene") or ""), "setting": ""}
                before = scene.get(key, "")
                if before != value:
                    scene[key] = value
                    s["scene"] = scene
                    changes.append({**change, "slide": n, "role": s.get("role"), "before": before, "after": value})
        elif field in ("headline", "body", "highlight"):
            n = e.get("slide")
            if not isinstance(n, int) or not 1 <= n <= len(v["slides"]):
                raise ValueError(f"bad slide number {n}")
            if field == "body" and n == len(v["slides"]):
                raise ValueError("the last slide's body is the CTA; edit the CTA instead")
            if field == "headline" and n == len(v["slides"]) and (story or lib.save_later_applies(pack)):
                raise ValueError("the last slide is only the CTA; edit the CTA instead")
            before = v["slides"][n - 1].get(field, "")
            if before != value:
                v["slides"][n - 1][field] = value
                changes.append({**change, "slide": n, "role": v["slides"][n - 1].get("role"), "before": before, "after": value})
        elif field == "title":
            if v["title"] != value:
                changes.append({**change, "before": v["title"], "after": value})
                v["title"] = value
        elif field == "caption":
            cta = v["cta"]
            old_body = "\n".join(l for l in lib.lines_of(v["caption"]) if lib.collapse(l) != lib.collapse(cta))
            body = [l for l in value.splitlines() if lib.collapse(l) != lib.collapse(cta)]
            new = "\n".join(body + [cta])
            if v["caption"] != new:
                v["caption"] = new
                changes.append({**change, "before": old_body, "after": "\n".join(body)})
        elif field == "cta":
            new_cta = lib.quote_code_word(lib.collapse(value))
            if new_cta != lib.collapse(v["cta"]):
                old = v["cta"]
                v["cta"] = new_cta
                cap = [l for l in lib.lines_of(v["caption"]) if lib.collapse(l) not in (lib.collapse(old), new_cta)]
                v["caption"] = "\n".join(cap + [new_cta])
                if lib.save_later_applies(pack):   # slide 10 is only the CTA: the save line, then לפעם הבאה ש... (24 Oct 2026)
                    v["slides"][-1]["headline"], v["slides"][-1]["body"] = lib.save_later_slide(new_cta)
                    v["slides"][-1].pop("highlight", None)
                else:
                    v["slides"][-1]["body"] = cta_slide_lines(new_cta)
                m = re.search(lib.CTA_WRITE_RE + r"\s*[״\"׳']?([\u05D0-\u05EA]+)", new_cta)
                if m:
                    v["code_word"] = m.group(1)
                changes.append({**change, "before": old, "after": new_cta})
    return changes


def sync_examples(pack, changes, folder):
    """After headline edits, the hidden example lists and counts follow the slides (carousel_lib.sync_numbered_examples).
    A new count also goes into example-slots.json, which the validator checks against. Not logged as a voice edit."""
    if not lib.numbered_examples_apply(pack):
        return {}
    edited = {c["option"] for c in changes if c["field"] == "headline"}
    out = {}
    for d in pack["directions"]:
        for v in d["versions"]:
            if v["id"] not in edited:
                continue
            r = lib.sync_numbered_examples(v)
            if r["changed"] or r["examples"]:
                out[v["id"]] = r
            if r["examples"]:
                slots_path = Path(folder) / lib.EXAMPLE_SLOTS_FILE
                if slots_path.exists():
                    slots = lib.read_json(slots_path)
                    slots.setdefault("slots", {})[v["id"]] = r["examples"][1]
                    slots.setdefault("edited", {})[v["id"]] = f'{r["examples"][0]} to {r["examples"][1]} by an edit, {lib.now_local().date()}'
                    lib.write_json(slots_path, slots)
    return out


def voice_records(pack, changes, date):
    """Edits to audience copy, with context, for the voice skill to learn from (examples/edits.jsonl)."""
    by_id = {v["id"]: (d["id"], v) for d in pack["directions"] for v in d["versions"]}
    out = []
    for c in changes:
        if c["field"] not in ("headline", "body", "caption", "label"):   # scenes are picture briefs, not audience copy
            continue
        direction, v = by_id[c["option"]]
        out.append({"at": lib.now_local().isoformat(timespec="seconds"), "pack_date": date, "direction": direction,
                    "option": c["option"], "field": c["field"], "slide": c.get("slide"), "role": c.get("role"),
                    "child_gender": v.get("child_gender"), "addressee": v.get("addressee"),
                    "kind": lib.edit_kind(c["before"], c["after"]), "before": c["before"], "after": c["after"]})
    return out


def snapshot(folder):
    """Copy (not move) the current pack and review files to versions/vN before saving."""
    folder = Path(folder)
    present = [folder / n for n in ("pack.json", "review.html", "review.md") if (folder / n).exists()]
    if not present:
        return None
    versions = folder / "versions"
    versions.mkdir(exist_ok=True)
    n = 1
    while (versions / f"v{n}").exists():
        n += 1
    target = versions / f"v{n}"
    target.mkdir()
    for p in present:
        shutil.copy2(p, target / p.name)
    return target


def save(date, edits, drafts=lib.DRAFTS, history_path=lib.HISTORY, edits_log=lib.VOICE_EDITS):
    if not DATE_RE.match(str(date)):
        return {"error": "bad date"}
    folder = Path(drafts) / date
    pack_path = folder / "pack.json"
    if not pack_path.exists():
        return {"error": f"no pack for {date}"}
    pack = lib.read_json(pack_path)
    try:
        changes = apply_edits(pack, edits)
    except ValueError as exc:
        return {"error": str(exc)}
    if not changes:
        return {"changed": 0, "errors": [], "warnings": [], "note": "nothing changed"}
    synced = sync_examples(pack, changes, folder)
    for d in pack["directions"]:   # the written post texts follow the edited caption and slides, punctuation kept
        for v in d["versions"]:
            if isinstance(v.get("post_text"), dict) and any(c["option"] == v["id"] for c in changes):
                v["post_text"] = lib.post_texts(v)
    backup = snapshot(folder)
    lib.write_json(pack_path, pack)
    logged = lib.log_voice_edits(voice_records(pack, changes, date), edits_log)
    voice = lib.voice_status(edits_path=edits_log)
    issues = validate_pack.pack_issues(pack, history=lib.load_history(history_path), voice=voice)
    errors = [i.as_dict() for i in issues if i.level == "ERROR"]
    warnings = [i.as_dict() for i in issues if i.level == "WARN"]
    create_review.write_review(pack_path)
    if not errors:
        lib.record_history(pack, history_path)
    return {"changed": len(changes), "valid": not errors, "errors": errors, "warnings": warnings, "synced": synced,
            "backup": str(backup.relative_to(Path(drafts).parent)) if backup else None,
            "voice_logged": logged, "voice_samples": voice["approved_samples"], "voice_required": voice["required"]}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(lib.PIPELINE), **kwargs)

    def log_message(self, fmt, *args):  # keep the terminal quiet except for saves
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/ping"):
            return self.send_json({"ok": True})
        brand = self.brand_font()
        if brand:   # the story look's Varela Round, until the pipeline keeps its own copy in assets/fonts
            return brand
        route = self.path.split("?")[0]
        if route in ("/", ""):
            if self.server.pinned_date:
                self.send_response(302)
                self.send_header("Location", f"/drafts/{self.server.default_date}/review.html")
                self.end_headers()
                return
            query = dict(part.split("=", 1) for part in self.path.partition("?")[2].split("&") if "=" in part)
            wanted = query.get("batch", "")
            return self.send_html(studio.app_page(wanted if DATE_RE.match(wanted) and batch.load(wanted) else None))
        if route == "/api/state":
            query = dict(part.split("=", 1) for part in self.path.partition("?")[2].split("&") if "=" in part)
            wanted = query.get("batch", "")
            return self.send_json(studio.state(wanted if DATE_RE.match(wanted) and batch.load(wanted) else None))
        if route == "/api/postiz-preview":
            import postiz_export
            from urllib.parse import parse_qs
            rec = producer.get(parse_qs(self.path.partition("?")[2]).get("key", [""])[0]) or {}
            if rec.get("status") != "done" or not rec.get("run_dir"):
                return self.send_json({"error": "הקרוסלה עוד לא מוכנה"}, 400)
            return self.send_json(postiz_export.preview(lib.PIPELINE / rec["run_dir"].lstrip("/")))
        if route == "/api/productions":
            return self.send_json({"runs": producer.load()["runs"]})
        # the older addresses (16 Oct 2026) all open the one page (Yarin, 17 Oct: "one page for everything without any subpages")
        m = re.match(r"^/(pool|grade)/(\d{4}-\d{2}-\d{2})/?$", route)
        if m or route in ("/productions", "/packs"):
            self.send_response(302)
            self.send_header("Location", f"/?batch={m.group(2)}" if m else "/")
            self.end_headers()
            return
        # production outputs: the picture to approve, the exported slides, contact sheet and ZIP (read only)
        if route.startswith("/approved/") and ".." not in route and route.rsplit(".", 1)[-1].lower() in ("png", "jpg", "zip", "txt", "md", "json", "html"):
            return super().do_GET()
        # drafts for the review pages, assets/fonts for the pillar typefaces; nothing else in the pipeline folder is served
        if not self.path.startswith(("/drafts/", "/assets/fonts/", "/assets/brand/")) or ".." in self.path:
            return self.send_error(404)
        if DAY_PAGE_RE.match(self.path.split("?")[0]):
            return self.send_page()
        return super().do_GET()

    def brand_font(self):
        """/assets/fonts/NAME that the pipeline has no copy of but shared/brand/fonts does (the woff2 files lumebook.com
        serves); None when this is not one, so the normal file serving answers."""
        route = self.path.split("?")[0]
        name = route[len("/assets/fonts/"):] if route.startswith("/assets/fonts/") else ""
        if not re.fullmatch(r"[\w.-]+\.woff2", name) or (lib.PIPELINE / "assets" / "fonts" / name).exists():
            return None
        src = lib.PIPELINE.parents[1] / "shared" / "brand" / "fonts" / name
        if not src.is_file():
            return None
        body = src.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "font/woff2")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=86400")
        self.end_headers()
        self.wfile.write(body)
        return True

    def send_page(self):
        """A review or carousel page with today's row of dates, so nights added since it was built show too."""
        import reco_render
        path = Path(self.translate_path(self.path))
        if not path.is_file():
            return self.send_error(404)
        html = DAYS_RE.sub(lambda _: reco_render.days_html(path.parent), path.read_text(encoding="utf-8"), count=1)
        if not self.server.pinned_date:   # the editors keep their own layout; this gets back to Carousel Machine
            html = html.replace("</body>", studio.BACK_LINK + "</body>", 1)
        return self.send_html(html)

    def send_html(self, html):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        if self.path.endswith((".html", ".md")):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def guess_type(self, path):
        if str(path).endswith(".md"):
            return "text/markdown; charset=utf-8"
        if str(path).endswith(".html"):
            return "text/html; charset=utf-8"
        return super().guess_type(path)

    def read_payload(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(min(length, 2_000_000)).decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            return None

    def do_POST(self):
        if self.path == "/api/save-reco":
            return self.save_reco()
        if self.path in ("/api/grade", "/api/produce-send"):
            return self.grade_api()
        if self.path.startswith("/api/production/"):
            return self.production_api()
        if self.path == "/api/push-grades":
            result = studio.push_grades()
            print(f"grades pushed: {result}", flush=True)
            return self.send_json(result, 200 if result.get("ok") else 400)
        if self.path == "/api/sync":
            lines = []
            new = cloud_sync.sync(log=lines.append) or []
            return self.send_json({"new": len(new) if isinstance(new, (list, tuple, set)) else 0, "log": lines[-20:]})
        if self.path != "/api/save":
            return self.send_error(404)
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(min(length, 2_000_000)).decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            return self.send_json({"error": "bad request"}, 400)
        result = save(payload.get("date"), payload.get("edits", []))
        n = len(result.get("errors", []))
        print(f"saved {payload.get('date')}: {result.get('changed', 0)} fields, {'valid' if result.get('valid') else str(n) + ' errors'}" if "error" not in result else f"save refused: {result['error']}", flush=True)
        self.send_json(result, 200 if "error" not in result else 400)


def _save_reco(self):
    """Edits to the games and books carousel, or an older games or books one (reco_render.save): back up, apply, validate, re-render, rebuild the page."""
    import reco_render
    try:
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(min(length, 2_000_000)).decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return self.send_json({"error": "bad request"}, 400)
    result = reco_render.save(payload.get("date"), payload.get("format"), payload.get("edits", []))
    print(f"saved {payload.get('date')} {payload.get('format')}: {result.get('changed', 0)} fields" if "error" not in result else f"save refused: {result['error']}", flush=True)
    self.send_json(result, 200 if "error" not in result else 400)


Handler.save_reco = _save_reco


def _grade_api(self):
    """The grading page (grade_page.py): save one carousel's grade, or send the picked ones to produce-queue.json."""
    payload = self.read_payload()
    plan = batch.load(payload.get("batch", "")) if isinstance(payload, dict) and DATE_RE.match(str(payload.get("batch", ""))) else None
    if not plan:
        return self.send_json({"error": "unknown batch"}, 400)
    if self.path == "/api/produce-send":
        its = {i["key"]: i for i in grades.items(plan)}
        started, blocked = [], []
        for k in grades.pick_unsent(plan["id"]):
            if k not in its or producer.get(k):   # one with a production already (re-export is its own button)
                continue
            try:
                started.append(producer.start(its[k]))
            except producer.Blocked as exc:
                blocked.append({"key": k, "errors": exc.errors})
        grades.unsend([b["key"] for b in blocked])
        for r in started:
            print(f"production started: {r['key']}", flush=True)
        for b in blocked:
            print(f"production blocked: {b['key']} ({len(b['errors'])} errors)", flush=True)
        stored = {k: v for k, v in grades.load()["grades"].items() if k in its}
        return self.send_json({"started": started, "blocked": blocked, "grades": stored})
    item = next((i for i in grades.items(plan) if i["key"] == payload.get("key")), None)
    if not item:
        return self.send_json({"error": "unknown carousel"}, 400)
    score = payload.get("score")
    if score is not None and score not in grades.SCORES:
        return self.send_json({"error": "score must be 1 to 5"}, 400)
    produce = payload.get("produce")
    entry = grades.upsert(item, score=score, why=payload.get("why"), produce=None if produce is None else bool(produce))
    return self.send_json({"entry": entry})


Handler.grade_api = _grade_api


def set_image_action(item, text):
    """A new scene for the option's one picture, after the image model declined the old one (backup first, review rebuilt;
    a picture brief is not audience copy, so it is not logged as a voice edit)."""
    folder = lib.DRAFTS / item["date"]
    pack_path = folder / "pack.json"
    pack = lib.read_json(pack_path)
    v = next(v for d in pack["directions"] for v in d["versions"] if v["id"] == item["id"])
    if not isinstance(v.get("image"), dict):
        raise ValueError("לאפשרות הזאת אין תמונה אחת")
    if v["image"].get("action") == text:
        return
    snapshot(folder)
    v["image"]["action"] = text
    lib.write_json(pack_path, pack)
    create_review.write_review(pack_path)


def _item_for_key(key):
    """The batch item (grades.items) behind a production key such as 2026-10-19/kid-2."""
    date = str(key).split("/")[0]
    plan = batch.plan_for_date(date)[0] if DATE_RE.match(date) else None
    return next((i for i in grades.items(plan) if i["key"] == key), None) if plan else None


def _production_api(self):
    """Carousel Machine's producer (producer.py): start or continue, approve the picture, ask for another, show in Finder."""
    payload = self.read_payload()
    if not isinstance(payload, dict):
        return self.send_json({"error": "bad request"}, 400)
    key = str(payload.get("key", ""))
    item = _item_for_key(key)
    if not item:
        return self.send_json({"error": "הקרוסלה לא נמצאה בבאץ'"}, 400)
    action = self.path.rsplit("/", 1)[-1]
    try:
        if action == "start":
            rec = producer.start(item)
        elif action == "approve":
            rec = producer.approve(key, item)
        elif action == "redo":
            note = str(payload.get("note", "")).strip()
            if not note:
                return self.send_json({"error": "כתבו מה לשנות בתמונה"}, 400)
            rec = producer.redo(key, item, note)
        elif action == "brief":
            text = clean(payload.get("action", ""))
            if len(text) < 20:
                return self.send_json({"error": "תארו את הסצנה במשפט או שניים"}, 400)
            set_image_action(item, text)
            rec = producer.start(item)
        elif action == "reveal":
            rec = producer.get(key) or {}
            target = rec.get("zip") or rec.get("run_dir")
            if not target:
                return self.send_json({"error": "אין עדיין קבצים"}, 400)
            path = (lib.PIPELINE / target.lstrip("/")).resolve()
            if lib.PIPELINE not in path.parents:
                return self.send_json({"error": "bad path"}, 400)
            import subprocess
            subprocess.run(["open", "-R", str(path)], check=False, timeout=10)
        elif action == "postiz":
            # to Postiz, scheduled for the picked time or a draft: Instagram gets every slide, Facebook slide 1 with the rest written out (postiz_export.py)
            import postiz_export
            rec = producer.get(key) or {}
            if rec.get("status") != "done" or not rec.get("run_dir"):
                return self.send_json({"error": "הקרוסלה עוד לא מוכנה"}, 400)
            try:
                sent = postiz_export.send(lib.PIPELINE / rec["run_dir"].lstrip("/"), when=payload.get("when") or None,
                                          draft=bool(payload.get("draft")))
            except RuntimeError as exc:
                return self.send_json({"error": str(exc)}, 502)
            producer._update(key, postiz={"sent_at": sent["sent_at"], "date": sent["date"], "status": sent["status"]})
        else:
            return self.send_error(404)
    except producer.Blocked as exc:
        print(f"production blocked: {key} ({len(exc.errors)} errors)", flush=True)
        return self.send_json({"error": str(exc), "errors": exc.errors}, 400)
    except ValueError as exc:
        return self.send_json({"error": str(exc)}, 400)
    print(f"production {action}: {key}", flush=True)
    return self.send_json({"run": producer.get(key)})


Handler.production_api = _production_api


def newest_date():
    dates = sorted(p.name for p in lib.DRAFTS.iterdir() if p.is_dir() and DATE_RE.match(p.name) and (p / "review.html").exists()) if lib.DRAFTS.exists() else []
    return dates[-1] if dates else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", help="pack date YYYY-MM-DD (default: newest)")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8777)))
    ap.add_argument("--no-cloud", action="store_true", help="do not check GitHub for cloud nights")
    args = ap.parse_args()
    if not args.no_cloud:
        cloud_sync.sync(log=lambda m: print(m, flush=True))
    producer.recover()
    date = args.date or newest_date()
    if not date:
        raise SystemExit("no packs in carousel/carousel-pipeline/drafts yet")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.default_date = date
    server.pinned_date = bool(args.date)
    plan = None if args.date else batch.newest_batch_with_content()
    where = "" if plan else f"drafts/{date}/review.html"
    print(f"Carousel Machine: http://localhost:{args.port}/{where}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
