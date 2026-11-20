#!/usr/bin/env python3
"""Fix an option's validator errors on its own when Yarin presses Produce (Yarin, 22 Oct 2026: "i dont want any more
errors, let me hit the produce button and youll figure it out youself").

    python3 carousel/carousel-pipeline/scripts/autofix.py 2026-10-22 expert-2      # fix one option now, print what changed

producer.py runs this before freezing an option that still has ERRORs (producer.blocking_errors):
1. a line that is too long is split at the space that keeps both halves inside the limit (no model call)
2. anything left goes to Claude (`claude -p`, no tools, outside the project so no hooks or CLAUDE.md) with the option's
   copy, the exact errors, the Hebrew rules and the voice skill; it answers with field edits, smallest change that clears them
3. edits are saved like a page save (versions/vN snapshot, example lists synced, review.html rebuilt) but are NOT logged
   to the voice skill's edits.jsonl (they are not Yarin's own words); every fix goes to drafts/DATE/autofix.jsonl instead
4. validate again; up to ROUNDS rounds, then whatever is left stops the production with the list
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel_lib as lib  # noqa: E402

ROUNDS = 3
CLAUDE_TIMEOUT = 420
MODEL = "opus"   # Hebrew quality matters more than speed here
LONG_LINE_RE = re.compile(r"line (\d+) has \d+ characters .*\(max (\d+)\)")
SLIDE_FIELD_RE = re.compile(r"/slide-(\d+)/(headline|body)$")
RULES = (lib.ROOT / "creators/creator-research/src/hebrew-rules.md", lib.ROOT / ".claude/skills/lumebook-hebrew-voice/SKILL.md")


class NotFixed(RuntimeError):
    def __init__(self, errors):
        lines = "\n".join(("שקופית %s: " % e["slide"] if e.get("slide") else "") + e["message"] for e in errors)
        super().__init__(f"התיקון האוטומטי לא הצליח לסגור {len(errors)} דברים:\n{lines}")
        self.errors = errors


def _option(pack, option_id):
    return next(v for d in pack["directions"] for v in d["versions"] if v["id"] == option_id)


def split_line(line, limit):
    """The split at a space whose longer half is shortest, both halves within limit; None when there is none."""
    best = None
    for m in re.finditer(r" ", line):
        a, b = line[:m.start()].rstrip(), line[m.end():].lstrip()
        if a and b and len(a) <= limit and len(b) <= limit and (best is None or max(len(a), len(b)) < max(map(len, best))):
            best = (a, b)
    return best


def mechanical(v, errors):
    """Edits for too-long lines (not the last slide's body, which is the CTA and is rebuilt from it)."""
    last = len(v["slides"])
    texts = {}
    for e in errors:
        m, f = LONG_LINE_RE.search(e["message"]), SLIDE_FIELD_RE.search(e["path"])
        if not (m and f):
            continue
        n, field = int(f.group(1)), f.group(2)
        if field == "body" and n == last:
            continue
        lines = texts.setdefault((n, field), lib.lines_of(v["slides"][n - 1].get(field, "")))
        i, limit = int(m.group(1)) - 1, int(m.group(2))
        if i < len(lines) and len(lines[i]) > limit:
            parts = split_line(lines[i], limit)
            if parts:
                lines[i:i + 1] = list(parts)
    return [{"option": v["id"], "field": field, "slide": n, "value": "\n".join(lines)}
            for (n, field), lines in texts.items() if "\n".join(lines) != v["slides"][n - 1].get(field, "")]


def _prompt(pack, v, errors):
    copy = {k: v.get(k) for k in ("title", "child_name", "child_gender", "addressee", "code_word", "caption", "cta")}
    copy["slides"] = [{"slide": i, "headline": s.get("headline", ""), "body": s.get("body", "")} for i, s in enumerate(v["slides"], 1)]
    rules = "\n\n".join(p.read_text(encoding="utf-8") for p in RULES if p.exists())
    return f"""You fix validator errors in one Hebrew Instagram carousel for LumeBook (personalised kids' books, Israel).
Yarin wrote or edited this copy. Make the SMALLEST change that clears every error below, keep his wording and meaning
everywhere else, and keep each line inside the character limit the error names. Natural everyday Israeli Hebrew, correct grammar.

Hard rules: never address the dad or use masculine-singular "you" (אתה, בוא נ...) anywhere, even inside a quote the parent says
to the child: rephrase the verb instead (e.g. «אם אתה ממשיך» -> «אם תמשיך»). Address mom (feminine singular) or both parents (plural)
as the option's addressee says. No em dashes. Brand is לומיבוק. Never mention AI. Line breaks are "\\n"; a headline has at most 3 lines.
The last slide is built from the CTA (its body; since 24 Oct 2026 its headline too): to change it, edit the "cta" field, never that slide.

Errors to clear:
{json.dumps(errors, ensure_ascii=False, indent=1)}

The option:
{json.dumps(copy, ensure_ascii=False, indent=1)}

Reference rules (follow them):
{rules}

Answer with ONLY one JSON object, no other text:
{{"edits": [{{"field": "headline" | "body" | "title" | "caption" | "cta", "slide": <number for headline/body, else null>, "value": "<the whole new text of that field>"}}]}}"""


def _claude_bin():
    return shutil.which("claude") or str(Path.home() / ".local/bin/claude")


def ask_claude(pack, v, errors):
    """Field edits from `claude -p`, run from an empty temp folder so no project hooks or instructions load."""
    with tempfile.TemporaryDirectory(prefix="lb-autofix-") as tmp:
        p = subprocess.run([_claude_bin(), "-p", "--model", MODEL, "--tools", "", "--output-format", "text",
                            "--no-session-persistence", "--setting-sources", ""],
                           input=_prompt(pack, v, errors), capture_output=True, text=True, timeout=CLAUDE_TIMEOUT, cwd=tmp,
                           env={**os.environ, "PATH": os.environ.get("PATH", "") + ":" + str(Path.home() / ".local/bin")})
    out = p.stdout or ""
    m = re.search(r"\{.*\}", out, re.S)
    if "authenticate" in out + (p.stderr or ""):
        raise RuntimeError("הכלי claude במחשב לא מחובר (ההתחברות פגה), אז את התיקון הזה הוא לא יכול לעשות. "
                           "מריצים claude בטרמינל, מתחברים, ולוחצים להמשיך מאותה נקודה.")
    if p.returncode or not m:
        raise RuntimeError("Claude לא ענה לתיקון: " + (out or p.stderr or "")[-400:])
    edits = json.loads(m.group(0)).get("edits") or []
    return [{"option": v["id"], "field": e["field"], "slide": e.get("slide"), "value": str(e.get("value", ""))}
            for e in edits if isinstance(e, dict) and e.get("field")]


def save(date, edits, how):
    """Save like the page does, without logging to the voice skill. Returns the changes."""
    import create_review
    import review_server  # lazy: review_server imports producer, which imports this
    folder = lib.DRAFTS / date
    pack_path = folder / "pack.json"
    pack = lib.read_json(pack_path)
    for e in edits:
        e["value"] = review_server.clean(e["value"])
    changes = review_server.apply_edits(pack, edits)
    if not changes:
        return []
    review_server.sync_examples(pack, changes, folder)
    review_server.snapshot(folder)
    lib.write_json(pack_path, pack)
    create_review.write_review(pack_path)
    with open(folder / "autofix.jsonl", "a", encoding="utf-8") as f:
        for c in changes:
            f.write(json.dumps({"at": lib.now_local().isoformat(timespec="seconds"), "how": how, **c}, ensure_ascii=False) + "\n")
    return changes


def run(item):
    """Clear the option's blocking errors. Returns the list of changes; raises NotFixed with what is left."""
    import producer
    done = []
    for _ in range(ROUNDS):
        errors = producer.blocking_errors(item)
        if not errors:
            return done
        pack = lib.read_json(lib.DRAFTS / item["date"] / "pack.json")
        v = _option(pack, item["id"])
        edits, how = mechanical(v, errors), "split"
        if not edits:
            edits, how = ask_claude(pack, v, errors), "claude"
        try:
            changes = save(item["date"], edits, how)
        except ValueError:
            changes = []
        if not changes:
            break
        done.extend(changes)
    errors = producer.blocking_errors(item)
    if errors:
        raise NotFixed(errors)
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("date")
    ap.add_argument("option")
    args = ap.parse_args()
    for c in run({"date": args.date, "id": args.option, "kind": args.option.split("-")[0]}):
        print(json.dumps(c, ensure_ascii=False))


if __name__ == "__main__":
    main()
