#!/usr/bin/env python3
"""Produce a carousel from Carousel Machine itself, with no chat in between (Yarin, 16 Oct 2026: "i want the entire
carousel engine, editor and producer to be viewed in one place i can easily access no need of talking to you each time").

    python3 carousel/carousel-pipeline/scripts/producer.py status          # every production and where it stands
    python3 carousel/carousel-pipeline/scripts/producer.py export-reco 2026-10-19 reco-2   # games and books ZIP, no cost

Pictures come from the OpenAI Images API only (03 Nov 2026, Yarin: "disconnect carousel machine from any other image
generation tool, i want it to use the gpt api from now on"; openai_pictures.py, openai_generate.py). fal.ai and ChatGPT in
Chrome are retired. Yarin's rules for the key (memory feedback-openai-api-key-rules) are enforced here, not left to the page:
always ask for a budget, never exceed it, tell the estimated tokens and cost before generating, create nothing without
his explicit permission. So no picture is made until Yarin has approved the stage: every stage that would spend (the cover or
the one picture, the other slides of a story, another take) first stops in status "approval" with its estimated tokens and
dollars; Yarin gives the carousel's budget and confirms (authorize(), the page's dialog); only then does that one stage run,
through openai_generate.py --max-usd BUDGET, which refuses any call that would pass the budget. The permission is used once.

Kid and expert option (one picture behind all ten slides, packs from 14 Oct 2026):
1. prepare_picture_jobs.py freezes the option into approved/DATE-ID/ (refreezes when the copy was edited since; images
   whose prompt did not change carry over). Free.
2. Approval of the picture stage, then openai_generate.py run picture --max-usd BUDGET.
3. Yarin looks at the picture in Carousel Machine and approves it (qa pass) or asks for another with a note (qa fail +
   replace, at most 2 replacements; each another take needs its own approval and room in the budget)
4. compose_slides.py exports the 1080 x 1350 slides, contact sheet, RTL check, caption, sources and the ZIP

Story carousel (story-format.md, 29 Oct 2026: a picture per slide, 9 to 12 slides):
1. prepare_picture_jobs.py freezes it with jobs slide-01 (the cover, text-to-image) and slide-02..NN (edits of the cover)
2. Approval of the cover, then openai_generate.py run slide-01; Carousel Machine shows the cover for approval or another take
3. after the cover is approved: Approval of the slides (the estimate and the budget left), then openai_generate.py run makes
   every other slide in parallel; they are marked QA-passed with the cover's approval and compose_slides.py exports in the
   story look. A slide that failed is made again by pressing produce again (and approving again): finished pictures are
   never bought twice

Games and books carousel: its slide PNGs are already final, so production is an export: approved/DATE-reco[-2]/final/
with the slides, caption, alt text, sources, contact sheet and the ZIP. No paid call.

State is productions.json (one entry per carousel, keyed "<date>/<id>"), written only here. Work runs in background
threads inside review_server.py; a restart in the middle marks the entry so the page offers to continue
(prepare and openai_generate are both resumable, a finished picture is never bought twice). An entry waiting in
"approval" survives a restart and a pending permission is never carried over to another stage.
"""

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel_lib as lib  # noqa: E402
import openai_pictures as op  # noqa: E402
import prepare_picture_jobs as pjobs  # noqa: E402
import reco_lib as rl  # noqa: E402

PRODUCTIONS = lib.PIPELINE / "productions.json"
GENERATE = HERE / "openai_generate.py"
PICTURE = "picture"
SLIDES_HE = "מייצר את התמונות של השקופיות"
BUSY = ("queued", "fixing", "preparing", "generating", "composing", "exporting")
APPROVAL = "approval"   # waiting for Yarin's budget and explicit yes; not BUSY, so a restart keeps it
STATUS_HE = {"queued": "בתור", "fixing": "מתקן את הטקסט", "preparing": "מקפיא את הטקסט", "generating": "מייצר תמונה", "review": "מחכה לאישור שלך",
             APPROVAL: "מחכה לתקציב ולאישור שלך", "composing": "מרכיב שקופיות", "exporting": "מייצא", "done": "מוכן לפרסום", "failed": "נעצר"}
STAGE_HE = {"cover": "התמונה (או השער)", "slides": "שאר התמונות של השקופיות", "redo": "תמונה אחרת"}
# The image model sometimes declines a harmless family scene (18 Oct 2026: expert-1 of 20 Oct twice; the same
# cover wording passed for kid-1, so the trigger is unknown). Rewording the scene and trying again got it through.
SAFETY_MARKERS = ("content_policy_violation", "moderation_blocked", "safety system declined", "safety_violations")
DECLINED_HE = ("מסנן הבטיחות של מודל התמונות דחה את תיאור התמונה. זה קורה לפעמים גם בסצנה תמימה, ולא ידוע מה בדיוק הפעיל אותו. "
               "בקשה שנדחתה לא מייצרת תמונה. אפשר לנסח מחדש את תיאור הסצנה למטה ולנסות שוב.")
QA_CHECKS_HE = ("הפנים של הילד אל המצלמה, עם הבעה גדולה", "הרעיון של הקרוסלה נקרא מהתמונה", "יש אזור נקי לטקסט",
                "ידיים ופנים טבעיים, בלי אותיות או לוגו", "תלת ממד מונפש, לא צילום")
ABOUT = ("Carousel Machine productions (producer.py). One entry per carousel keyed <date>/<id>; status: " + ", ".join(STATUS_HE)
         + ". Kid and expert: approved/DATE-ID, one picture; story format (29 Oct 2026): a picture per slide, the cover approved first."
         " Games and books: export only. Since 03 Nov 2026 every picture comes from the OpenAI Images API and every stage that"
         " spends waits in approval for Yarin's budget and yes (budget_usd, grant, approval on each entry).")

_lock = threading.RLock()
_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="produce")


def now_iso():
    return lib.now_local().isoformat(timespec="seconds")


def load(path=None):
    path = Path(path or PRODUCTIONS)
    data = lib.read_json(path) if path.exists() else {}
    data.setdefault("_about", ABOUT)
    data.setdefault("runs", {})
    return data


def get(key, path=None):
    return load(path)["runs"].get(key)


def _update(key, path=None, **fields):
    with _lock:
        data = load(path)
        rec = data["runs"].setdefault(key, {"key": key})
        rec.update(fields)
        rec["updated_at"] = now_iso()
        if fields.get("status"):
            rec["status_he"] = STATUS_HE.get(fields["status"], fields["status"])
        lib.write_json(path or PRODUCTIONS, data)
        return dict(rec)


def rel(path):
    """A path under the pipeline folder as the URL Carousel Machine serves it from."""
    path = Path(path).resolve()
    if lib.PIPELINE.resolve() not in path.parents:   # tests write to a temporary folder
        return str(path)
    return "/" + str(path.relative_to(lib.PIPELINE.resolve())).replace("\\", "/")


def run_dir_for(item):
    return lib.APPROVED / f'{item["date"]}-{item["id"]}'


# ---------------------------------------------------------------- spend and files

def spent(run_dir):
    log = Path(run_dir) / "generated-assets" / "generation-log.jsonl"
    total = 0.0
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except (ValueError, json.JSONDecodeError):
                continue
            if rec.get("billed", True):   # the same rule as openai_generate.Run.spent
                total += float(rec.get("estimated_cost_usd") or 0)
    return round(total, 5)


def outputs(run_dir):
    import drive_export   # final_slides: only this carousel's slide count, never a stale NN.png from a longer version
    final = Path(run_dir) / "final"
    out = {}
    zips = sorted(final.glob("*.zip")) if final.exists() else []
    if zips:
        out["zip"] = rel(zips[-1])
    for name, key in (("contact-sheet.png", "contact_sheet"), ("rtl-check.png", "rtl_check"), ("caption.txt", "caption_file")):
        if (final / name).exists():
            out[key] = rel(final / name)
    slides = drive_export.final_slides(run_dir) if final.exists() else []
    out["slides"] = [rel(p) for p in slides]
    return out


def compose_problems(text):
    """The RTL and fit problems compose_slides.py prints in its closing JSON."""
    at = text.find('{\n  "out_dir"')
    if at < 0:
        return []
    try:
        return json.loads(text[at:text.rindex("}") + 1]).get("rtl_problems", [])
    except (ValueError, json.JSONDecodeError):
        return []


def _sh(args, timeout, env_shell=False):
    """Run a pipeline script. env_shell: through `zsh -ic` so OPENAI_API_KEY comes from the Keychain via ~/.zshrc (never echoed)."""
    if env_shell:
        cmd = ["zsh", "-ic", " ".join(shlex.quote(str(a)) for a in args)]
    else:
        cmd = [str(a) for a in args]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(lib.PIPELINE.parents[1]))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _tail(text, n=6):
    lines = [l for l in text.strip().splitlines() if l.strip() and "OPENAI_API_KEY" not in l and "sk-" not in l]
    return "\n".join(lines[-n:])


def _jobs(run_dir):
    path = Path(run_dir) / "jobs.json"
    return lib.read_json(path) if path.exists() else {}


def is_story(run_dir):
    """A story run: a picture per slide, the cover (slide-01) approved first (jobs.json "story", 29 Oct 2026)."""
    return bool(_jobs(run_dir).get("story"))


def cover_job(run_dir):
    """The picture Yarin approves in Carousel Machine: the one picture, or the cover of a story run."""
    jobs = _jobs(run_dir)
    return (jobs.get("reference_job") or "slide-01") if jobs.get("story") else PICTURE


def run_dir_of(rec):
    """The run folder behind a productions.json entry ("/approved/DATE-ID", or an absolute path in tests)."""
    raw = str(rec["run_dir"])
    p = Path(raw)
    return p if p.is_absolute() and (p / "jobs.json").exists() else lib.PIPELINE / raw.lstrip("/")


class NeedsApproval(Exception):
    """A stage that would spend has no permission yet (Yarin's rules, 03 Nov 2026): carries what the page shows him."""

    def __init__(self, stage, names, est, spent_now, budget):
        super().__init__(f"stage {stage} needs Yarin's budget and approval")
        self.info = {"stage": stage, "stage_he": STAGE_HE.get(stage, stage), "images": est["images"], "jobs": list(names),
                     "usd": est["usd"], "tokens": est["total_tokens"], "input_text_tokens": est["input_text_tokens"],
                     "input_image_tokens": est["input_image_tokens"], "output_tokens": est["output_tokens"],
                     "spent_usd": round(spent_now, 4), "budget_usd": budget or None,
                     "need_usd": round(spent_now + est["usd"], 4), "model": op.config()["model"], "quality": op.config()["quality"]}


def _gate(key, run_dir, stage, names):
    """Permission to spend for this one stage, or NeedsApproval. Returns the budget to pass to openai_generate.py --max-usd.
    The permission (rec["grant"], set by authorize()) is for exactly this stage and is used up here, so the next stage, another
    take or a retry asks again. It also needs the estimate to fit in the budget left."""
    rec = get(key) or {}
    est = op.estimate_total(_jobs(run_dir), names)
    budget = float(rec.get("budget_usd") or 0)
    spent_now = spent(run_dir)
    grant = rec.get("grant") or {}
    if not (grant.get("stage") == stage and budget > 0 and spent_now + est["usd"] <= budget + 1e-9):
        raise NeedsApproval(stage, names, est, spent_now, budget)
    _update(key, grant=None)
    return budget



def _picture_state(run_dir):
    state = Path(run_dir) / "state.json"
    if not state.exists():
        return {}
    return lib.read_json(state).get("jobs", {}).get(cover_job(run_dir), {})


# ---------------------------------------------------------------- games and books export (no cost)

def export_reco(date, out_dir_name, drafts=None, approved=None):
    """Copy a games and books carousel's final slides into approved/DATE-<reco|reco-2>/final with its texts and a ZIP."""
    drafts = Path(drafts or lib.DRAFTS)
    folder = drafts / date
    fmt = {v: k for k, v in rl.OUT_DIRS.items()}[out_dir_name]
    car = lib.read_json(rl.carousel_path(folder, fmt))
    src = folder / out_dir_name
    slides = car.get("slides", [])
    pngs = [src / f"{i:02d}.png" for i in range(1, len(slides) + 1)]
    missing = [p.name for p in pngs if not p.exists()]
    if missing:
        raise RuntimeError("חסרות שקופיות: " + ", ".join(missing))
    final = Path(approved or lib.APPROVED) / f"{date}-{out_dir_name}" / "final"
    final.mkdir(parents=True, exist_ok=True)
    for p in pngs:
        shutil.copy2(p, final / p.name)
    if (src / "contact-sheet.png").exists():
        shutil.copy2(src / "contact-sheet.png", final / "contact-sheet.png")
    (final / "caption.txt").write_text(car.get("caption", "").strip() + "\n", encoding="utf-8")
    alt = [f'{i}: {lib.collapse(" ".join([s.get("headline", ""), s.get("body", "")]))}' for i, s in enumerate(slides, 1)]
    (final / "alt-text.txt").write_text("\n".join(alt) + "\n", encoding="utf-8")
    stage = car.get("stage") or {}
    md = [f"# Sources · games and books · {date}", "", f'Stage: {stage.get("age_label_he", "")} · {stage.get("skill", "")}', "", "## Development sources", ""]
    for s in car.get("dev_sources", []):
        md.append(f'- [{s.get("title", "")}]({s.get("url", "")}) · {s.get("publisher", "")} · read {s.get("accessed", "")}')
    md += ["", "## Products (slide order)", ""]
    for p in car.get("products", []):
        md.append(f'- {rl.KIND_HE.get(p.get("kind"), p.get("kind", ""))} · {p.get("title_he", "")} · {p.get("popularity_label", "")}')
        for a in p.get("availability", []):
            md.append(f'  - available: {a.get("retailer", "")} · {a.get("status", "")} · {a.get("url", "")} · {a.get("accessed", "")}')
    (final / "sources.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    zip_path = final / f"{date}-{out_dir_name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in pngs:
            z.write(final / p.name, f"slides/{p.name}")
        for name in ("caption.txt", "alt-text.txt", "sources.md", "contact-sheet.png"):
            if (final / name).exists():
                z.write(final / name, name)
    import drive_export  # Yarin's Drive content folder (18 Oct 2026); only real approved/ runs reach it
    drive_export.export(final.parent, quiet=True)
    return final.parent


# ---------------------------------------------------------------- the steps

def _prepare(item):
    pack = lib.DRAFTS / item["date"] / "pack.json"
    script = HERE / "prepare_picture_jobs.py"
    code, out = _sh([sys.executable, script, pack, item["id"]], 120)
    if code and "--refreeze" in out:   # Yarin edited the copy after an earlier freeze: archive it, keep matching images
        code, out = _sh([sys.executable, script, pack, item["id"], "--refreeze"], 120)
    if code:
        raise RuntimeError("ההקפאה נכשלה:\n" + _tail(out))
    run_dir = run_dir_for(item)
    jobs = lib.read_json(run_dir / "jobs.json")
    if jobs.get("order") != [PICTURE] and not jobs.get("story"):
        raise RuntimeError("זו קרוסלה בפורמט הישן (תמונה לכל שקופית). אותה מפיקים דרך קלוד.")
    return run_dir


def _generate(key, run_dir, replace_note=None):
    """The cover (or the one picture), or another take of it. Needs Yarin's permission for this stage first (_gate)."""
    job = cover_job(run_dir)
    budget = _gate(key, run_dir, "redo" if replace_note is not None else "cover", [job])
    _update(key, status="generating", error=None)
    if replace_note is not None:
        code, out = _sh([sys.executable, GENERATE, run_dir, "qa", job, "fail", "--note", replace_note], 60)
        if code:
            raise RuntimeError(_tail(out))
        args = [sys.executable, GENERATE, run_dir, "replace", job, "--note", replace_note, "--max-usd", budget]
    else:
        args = [sys.executable, GENERATE, run_dir, "run", job, "--max-usd", budget]
    code, out = _sh(args, 900, env_shell=True)
    st = _picture_state(run_dir)
    if st.get("status") != "done":
        if any(m in out for m in SAFETY_MARKERS):
            _update(key, declined=True)
            raise RuntimeError(DECLINED_HE)
        raise RuntimeError("התמונה לא נוצרה:\n" + _tail(out))
    pic = Path(run_dir) / "generated-assets" / f"{job}.png"
    _update(key, status="review", picture=rel(pic) + f"?v={st.get('attempts', 1)}", spent_usd=spent(run_dir),
            replacements=st.get("replacements", 0), attempts=st.get("attempts", 1),
            error=_tail(out) if code else None)


def _generate_slides(key, run_dir):
    """Story run, after the cover is approved: every other slide in parallel as an edit of the cover, inside the budget.
    Needs Yarin's permission for this stage first (_gate). The cover's approval covers the look of the others (Carousel Machine
    has no per-slide approval): each new picture is marked QA-passed. Raises when a slide is still missing, so pressing produce
    again (and approving again) makes only the missing ones."""
    jobs = _jobs(run_dir)
    cover = cover_job(run_dir)
    state = lambda: lib.read_json(Path(run_dir) / "state.json").get("jobs", {})  # noqa: E731
    todo = [n for n in jobs.get("order", []) if n != cover and state().get(n, {}).get("status") != "done"]
    out = ""
    if todo:
        budget = _gate(key, run_dir, "slides", todo)
        _update(key, status="generating", error=None)
        _update(key, status_he=SLIDES_HE, slides_total=len(jobs.get("order", [])))
        code, out = _sh([sys.executable, GENERATE, run_dir, "run", *todo, "--max-usd", budget], 1800, env_shell=True)
    st = state()
    for n in jobs.get("order", []):
        if n != cover and st.get(n, {}).get("status") == "done" and st[n].get("qa") is None:
            _sh([sys.executable, GENERATE, run_dir, "qa", n, "pass", "--note", "approved with the cover in Carousel Machine"], 60)
    st = state()
    missing = [n for n in jobs.get("order", []) if st.get(n, {}).get("status") != "done"]
    _update(key, spent_usd=spent(run_dir), slides_made=len(jobs.get("order", [])) - len(missing))
    if missing:
        if any(m in out for m in SAFETY_MARKERS):
            _update(key, declined=True)
        raise RuntimeError(f"{len(missing)} תמונות של שקופיות לא נוצרו ({', '.join(missing)}). "
                           "אפשר ללחוץ שוב על הפקה ולאשר: רק החסרות ייווצרו, בלי לשלם שוב על מה שכבר קיים.\n" + _tail(out))


def _compose(key, run_dir):
    _update(key, status="composing", error=None)
    code, out = _sh([sys.executable, HERE / "compose_slides.py", run_dir], 600)
    files = outputs(run_dir)
    if not files.get("zip"):
        raise RuntimeError("הייצוא נכשל:\n" + _tail(out))
    problems = compose_problems(out)
    warn = ("לבדוק לפני פרסום: " + "; ".join(problems[:4])) if problems else (_tail(out) if code else None)
    _update(key, status="done", done_at=now_iso(), spent_usd=spent(run_dir), warning=warn, rtl_problems=len(problems), **files)


def _work(key, item, action, note=None):
    try:
        if item["kind"] == "reco":
            _update(key, status="exporting", error=None)
            run_dir = export_reco(item["date"], item["id"])
            _update(key, status="done", done_at=now_iso(), run_dir=rel(run_dir), spent_usd=0, **outputs(run_dir))
            return
        if action == "approve":
            run_dir = run_dir_of(get(key))
            code, out = _sh([sys.executable, GENERATE, run_dir, "qa", cover_job(run_dir), "pass"], 60)
            if code:
                raise RuntimeError(_tail(out))
            if is_story(run_dir):
                _generate_slides(key, run_dir)
            return _compose(key, run_dir)
        if action == "redo":
            return _generate(key, run_dir_of(get(key)), replace_note=note or "another take")
        if blocking_errors(item):   # Yarin, 22 Oct 2026: Produce fixes the copy itself instead of stopping
            import autofix
            _update(key, status="fixing", error=None)
            fixed = autofix.run(item)
            _update(key, fixed=[{k: c.get(k) for k in ("field", "slide", "before", "after")} for c in fixed])
        _update(key, status="preparing", error=None)
        run_dir = _prepare(item)
        _update(key, run_dir=rel(run_dir), spent_usd=spent(run_dir), backend=lib.picture_backend())
        st = _picture_state(run_dir)
        if st.get("status") == "done" and st.get("qa") == "pass":
            if is_story(run_dir):
                _generate_slides(key, run_dir)     # only the slides still missing; none when all were made
            return _compose(key, run_dir)          # a picture approved earlier: only re-export
        if st.get("status") == "done":
            pic = Path(run_dir) / "generated-assets" / f"{cover_job(run_dir)}.png"
            _update(key, status="review", picture=rel(pic) + f"?v={st.get('attempts', 1)}", spent_usd=spent(run_dir))
            return
        _generate(key, run_dir)
    except NeedsApproval as na:   # nothing has been spent: the page asks for the budget and the yes, authorize() continues
        _update(key, status=APPROVAL, error=None, approval=na.info, pending={"action": action, "note": note})
    except Exception as exc:  # noqa: BLE001 - the page shows the reason and offers to try again
        rec = get(key) or {}
        back = "review" if action == "redo" and rec.get("picture") else "failed"
        _update(key, status=back, error=str(exc)[:1500])


# ---------------------------------------------------------------- the check before a production

class Blocked(ValueError):
    """Was raised by start() while the option had validator errors (Yarin, 18 Oct 2026). Since 22 Oct 2026 ("i dont want any
    more errors, let me hit the produce button and youll figure it out youself") start() queues anyway and _work runs
    autofix.py first; callers still catch it."""

    def __init__(self, errors):
        super().__init__(f"לפני הפקה צריך לתקן {len(errors)} דברים")
        self.errors = errors


_checked = {}  # pack path -> (mtime_ns, pack, issues): one validation per pack change, the page asks every few seconds


def blocking_errors(item):
    """The ERRORs that stop producing one kid or expert option (validate_pack.option_errors), as {slide, path, message}.
    Games and books carousels are an export of finished slides and are never blocked."""
    if item.get("kind") == "reco":
        return []
    import validate_pack
    path = lib.DRAFTS / item["date"] / "pack.json"
    if not path.exists():
        return [{"slide": None, "path": str(path.name), "message": "pack.json is missing"}]
    mtime = path.stat().st_mtime_ns
    hit = _checked.get(str(path))
    if not hit or hit[0] != mtime:
        pack = lib.read_json(path)
        hit = _checked[str(path)] = (mtime, pack, validate_pack.pack_issues(pack, history=None))
    _, pack, issues = hit
    out = []
    for i in issues:
        if i.level != "ERROR" or validate_pack.other_option_issue(i, pack, item["id"]):
            continue
        m = re.search(r"/slide-(\d+)", str(i.path))
        out.append({"slide": int(m.group(1)) if m else None, "path": str(i.path), "message": i.message})
    return out


def _item_fields(item):
    return {k: item[k] for k in ("date", "kind", "id", "format", "topic_he", "cover", "batch", "child_name", "skill_he") if item.get(k)}


def start(item):
    """Queue one carousel. A carousel already in progress, waiting for approval or done is left alone (done: use start again
    after edits). Starting spends nothing: the free steps run (fix the copy, freeze it), then the first stage that would spend
    stops in "approval" until Yarin gives a budget and a yes (authorize)."""
    key = item["key"]
    with _lock:
        rec = get(key)
        if rec and rec.get("status") in BUSY + ("review", APPROVAL):
            return rec
        rec = _update(key, status="queued", requested_at=now_iso(), error=None, warning=None, declined=None, fixed=None,
                      approval=None, pending=None, grant=None, **_item_fields(item))
    _pool.submit(_work, key, item, "start")
    return rec


def approve(key, item):
    """Approve the shown picture. A story cover then needs its own approval before the other slides are made."""
    with _lock:
        rec = get(key)
        if not rec or rec.get("status") != "review":
            raise ValueError("אין תמונה שמחכה לאישור")
        rec = _update(key, status="composing")
    _pool.submit(_work, key, item, "approve")
    return rec


def redo(key, item, note):
    """Ask for another take. It is a new picture, so it stops in "approval" again before anything is made."""
    with _lock:
        rec = get(key)
        if not rec or rec.get("status") != "review":
            raise ValueError("אין תמונה שמחכה לאישור")
        if rec.get("replacements", 0) >= 2:
            raise ValueError("כבר נוצרו 3 תמונות לקרוסלה הזו. כדי לנסות שוב צריך את קלוד.")
        rec = _update(key, status="generating", note=str(note)[:500])
    _pool.submit(_work, key, item, "redo", str(note)[:500])
    return rec


def authorize(key, item, budget_usd, confirmed):
    """Yarin's budget and explicit yes for the stage waiting in "approval" (rules of 03 Nov 2026). The budget is the most the
    whole carousel may cost, what was already spent included, and it must cover this stage's estimate. The permission is for this
    one stage and is used up when it runs."""
    if confirmed is not True:
        raise ValueError("צריך לאשר במפורש לפני שנוצרת תמונה")
    try:
        budget = round(float(budget_usd), 4)
    except (TypeError, ValueError):
        raise ValueError("כתבו תקציב במספרים, למשל 0.30") from None
    if not budget > 0:
        raise ValueError("כתבו תקציב גדול מאפס")
    with _lock:
        rec = get(key)
        if not rec or rec.get("status") != APPROVAL or not rec.get("approval") or not rec.get("pending"):
            raise ValueError("אין שלב שמחכה לתקציב")
        info, pending = rec["approval"], rec["pending"]
        spent_now = spent(run_dir_of(rec)) if rec.get("run_dir") else 0.0
        need = round(spent_now + float(info["usd"]), 4)
        if budget + 1e-9 < need:
            raise ValueError(f"התקציב נמוך מההערכה: צריך לפחות ${need:.2f} (כבר נוצל ${spent_now:.2f}, ההערכה לשלב הזה ${float(info['usd']):.2f})")
        rec = _update(key, budget_usd=budget, grant={"stage": info["stage"], "at": now_iso()}, status="queued", approval=None, pending=None)
    _pool.submit(_work, key, item, pending["action"], pending.get("note"))
    return rec


def cancel(key):
    """Yarin does not approve the waiting stage: nothing is made. Another take or the slides go back to the picture he is
    looking at; a first stage leaves the queue."""
    with _lock:
        rec = get(key)
        if not rec or rec.get("status") != APPROVAL:
            raise ValueError("אין שלב שמחכה לאישור")
        action = (rec.get("pending") or {}).get("action")
        if action in ("approve", "redo") and rec.get("picture"):
            return _update(key, status="review", approval=None, pending=None, grant=None, error=None)
        data = load()
        data["runs"].pop(key, None)
        lib.write_json(PRODUCTIONS, data)
        return {"key": key, "status": "cancelled"}


def recover(path=None):
    """On server start: anything that was running when the server stopped."""
    with _lock:
        data = load(path)
        changed = False
        for key, rec in data["runs"].items():
            if rec.get("status") not in BUSY:
                continue
            run_dir = run_dir_of(rec) if rec.get("run_dir") else None
            st = _picture_state(run_dir) if run_dir else {}
            if rec.get("kind") != "reco" and st.get("status") == "done" and st.get("qa") != "pass":
                rec.update(status="review", status_he=STATUS_HE["review"],
                           picture=rel(run_dir / "generated-assets" / f"{cover_job(run_dir)}.png") + f"?v={st.get('attempts', 1)}")
            else:
                rec.update(status="failed", status_he=STATUS_HE["failed"], grant=None,
                           error="Carousel Machine נסגר באמצע. אפשר להמשיך מאותה נקודה, בלי לשלם שוב על מה שכבר נוצר. כל שלב שמוציא כסף יבקש אישור מחדש.")
            changed = True
        if changed:
            lib.write_json(path or PRODUCTIONS, data)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    e = sub.add_parser("export-reco")
    e.add_argument("date")
    e.add_argument("which", choices=sorted(rl.OUT_DIRS[f] for f in rl.MIXED_FORMATS))
    args = ap.parse_args()
    if args.cmd == "status":
        for key, rec in sorted(load()["runs"].items()):
            print(f'{key:24} {rec.get("status", ""):10} ${rec.get("spent_usd", 0):.2f} {rec.get("zip", "")} {rec.get("error") or ""}'.rstrip())
    else:
        print(export_reco(args.date, args.which))


if __name__ == "__main__":
    main()
