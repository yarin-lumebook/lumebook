#!/usr/bin/env python3
"""Edit a nightly pack from its review page and save it back.

    python3 carousel/carousel-pipeline/scripts/review_server.py              # newest pack
    python3 carousel/carousel-pipeline/scripts/review_server.py --date 2026-10-08 --port 8777

Open the printed address. Every slide headline and body, the caption, the CTA and the option title
become editable in place. "שמירה" (or Cmd+S) sends the changes here, and this server:

1. copies the current pack.json, review.html and review.md to drafts/DATE/versions/vN/ (nothing is lost)
2. applies the edits to pack.json (the CTA also updates the last slide, the caption's last line and the code word)
   and logs every copy edit (before and after) to .claude/skills/lumebook-hebrew-voice/examples/edits.jsonl,
   so the voice skill learns from Yarin's own changes
3. validates with the same rules as the nightly run and saves even if something fails, so no typing is lost
4. rebuilds review.html and review.md, and updates history.json when the pack is valid
5. returns the errors, which the page shows next to the exact field

Listens on 127.0.0.1 only. Writes only under carousel/carousel-pipeline/drafts/. Standard library only.
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
import carousel_lib as lib  # noqa: E402
import create_review  # noqa: E402
import validate_pack  # noqa: E402

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FIELDS = {"headline", "body", "highlight", "caption", "cta", "title"}


def clean(text):
    return "\n".join(line.strip() for line in str(text).replace(" ", " ").splitlines() if line.strip())


def cta_slide_lines(cta):
    w = lib.collapse(cta).split()
    return "\n".join(part for part in (" ".join(w[:3]), " ".join(w[3:7]), " ".join(w[7:])) if part)


def apply_edits(pack, edits):
    """Apply edits from the page. Returns a list of changes (option, field, slide, before, after).
    Raises ValueError on a bad edit."""
    options = {v["id"]: v for d in pack["directions"] for v in d["versions"]}
    changes = []
    for e in edits:
        v = options.get(e.get("option"))
        field = e.get("field")
        if v is None or field not in FIELDS:
            raise ValueError(f"unknown option or field: {e.get('option')} {field}")
        value = clean(e.get("value", ""))
        change = {"option": v["id"], "field": field, "slide": None}
        if field in ("headline", "body", "highlight"):
            n = e.get("slide")
            if not isinstance(n, int) or not 1 <= n <= len(v["slides"]):
                raise ValueError(f"bad slide number {n}")
            if field == "body" and n == len(v["slides"]):
                raise ValueError("the last slide's body is the CTA; edit the CTA instead")
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
                v["slides"][-1]["body"] = cta_slide_lines(new_cta)
                m = re.search(lib.CTA_WRITE_RE + r"\s*[״\"׳']?([\u05D0-\u05EA]+)", new_cta)
                if m:
                    v["code_word"] = m.group(1)
                changes.append({**change, "before": old, "after": new_cta})
    return changes


def voice_records(pack, changes, date):
    """Edits to audience copy, with context, for the voice skill to learn from (examples/edits.jsonl)."""
    by_id = {v["id"]: (d["id"], v) for d in pack["directions"] for v in d["versions"]}
    out = []
    for c in changes:
        if c["field"] not in ("headline", "body", "caption"):
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
    return {"changed": len(changes), "valid": not errors, "errors": errors, "warnings": warnings,
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
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", f"/drafts/{self.server.default_date}/review.html")
            self.end_headers()
            return
        # drafts for the review pages, assets/fonts for the pillar typefaces; nothing else in the pipeline folder is served
        if not self.path.startswith(("/drafts/", "/assets/fonts/")) or ".." in self.path:
            return self.send_error(404)
        return super().do_GET()

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

    def do_POST(self):
        if self.path == "/api/save-reco":
            return self.save_reco()
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


def newest_date():
    dates = sorted(p.name for p in lib.DRAFTS.iterdir() if p.is_dir() and DATE_RE.match(p.name) and (p / "review.html").exists()) if lib.DRAFTS.exists() else []
    return dates[-1] if dates else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", help="pack date YYYY-MM-DD (default: newest)")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8777)))
    args = ap.parse_args()
    date = args.date or newest_date()
    if not date:
        raise SystemExit("no packs in carousel/carousel-pipeline/drafts yet")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.default_date = date
    print(f"Review editor: http://localhost:{args.port}/drafts/{date}/review.html  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
