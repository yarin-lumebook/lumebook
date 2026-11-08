#!/usr/bin/env python3
"""Keep the LumeBook components in step with each other.

Reads lumebook.json (the component registry) and shared/facts.json.

  python3 tools/lumebook.py status            what changed since the last ripple, what it affects, what is waiting
  python3 tools/lumebook.py ripple            status + rebuild what is safe to rebuild (build.auto), sync brand copies,
                                              queue the rest as to-dos, then remember the new state
  python3 tools/lumebook.py check             consistency rules (registry, brand copies, offer wording, spelling,
                                              em dashes in site copy, old paths, SMM English mirror)
  python3 tools/lumebook.py sync              copy shared/brand files to every place that needs a physical copy
  python3 tools/lumebook.py ack ID [--published [YYYY-MM-DD]]
                                              clear ID's to-dos; --published records that its artifact was republished
  python3 tools/lumebook.py map               the component graph
  python3 tools/lumebook.py build ID          run a component's build now (auto or manual)
  python3 tools/lumebook.py deploy ID         deploy a component that has publish.type vercel (asks Vercel CLI)
  python3 tools/lumebook.py serve [--port N]  one local server for the whole project (default 8780); every page it shows
                                              gets the edit button (shared/site-editor/README.md)
  python3 tools/lumebook.py edits [bake]      pages edited with the edit button; bake writes their edits into their files

Every command writes .lumebook/status.json, which the dashboard reads. Standard library only.
"""
import argparse, fnmatch, glob, hashlib, json, os, re, shutil, subprocess, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_editor  # noqa: E402  the edit button on every page (tools/site_editor.py)
import i18n  # noqa: E402  the language switch's words (tools/i18n.py, 8 Nov 2026)

try:  # Israel time with its summer and winter offsets (audit of 08 Nov 2026: a fixed UTC+3 was an hour off half the year)
    from zoneinfo import ZoneInfo
    IL = ZoneInfo("Asia/Jerusalem")
except Exception:  # no time zone data on this Python
    IL = timezone(timedelta(hours=3))


def find_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.exists(os.path.join(d, "lumebook.json")):
            return d
        d = os.path.dirname(d)
    sys.exit("lumebook.json not found above tools/")


ROOT = find_root()
REG = json.load(open(os.path.join(ROOT, "lumebook.json"), encoding="utf-8"))
COMP = REG["components"]
STATE_PATH = os.path.join(ROOT, REG["state"])
STATUS_PATH = os.path.join(ROOT, REG["status"])
LOG_PATH = os.path.join(os.path.dirname(STATE_PATH), "log.jsonl")


def now():
    return datetime.now(IL).isoformat(timespec="seconds")


def p(rel):
    return os.path.join(ROOT, rel)


def mtime_iso(rel):
    try:
        return datetime.fromtimestamp(os.path.getmtime(p(rel)), IL).isoformat(timespec="seconds")
    except OSError:
        return None


def watched_files(cid):
    out = set()
    for g in COMP[cid].get("watch", []):
        for f in glob.glob(p(g), recursive=True):
            if os.path.isfile(f) and not os.path.basename(f).startswith("."):
                out.add(os.path.relpath(f, ROOT))
    return sorted(out)


def digest(cid):
    h = hashlib.md5()
    files = watched_files(cid)
    for f in files:
        h.update(f.encode())
        with open(p(f), "rb") as fh:
            h.update(hashlib.md5(fh.read()).digest())
    return h.hexdigest(), files


def changed_files(cid, old_files):
    """Files whose content hash differs from the last ripple (old_files: {path: md5})."""
    out = []
    for f in watched_files(cid):
        with open(p(f), "rb") as fh:
            m = hashlib.md5(fh.read()).hexdigest()
        if old_files.get(f) != m:
            out.append(f)
    out += [f for f in old_files if not os.path.exists(p(f))]
    return out


def md5_file(rel):
    with open(p(rel), "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def file_hashes(cid):
    res = {}
    for f in watched_files(cid):
        with open(p(f), "rb") as fh:
            res[f] = hashlib.md5(fh.read()).hexdigest()
    return res


def load_state():
    try:
        return json.load(open(STATE_PATH, encoding="utf-8"))
    except (OSError, ValueError):
        return {"components": {}, "pending": []}


def save_state(st):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    json.dump(st, open(STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def log(event):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(event, at=now()), ensure_ascii=False) + "\n")


def downstream(start):
    seen, todo = [], list(start)
    while todo:
        c = todo.pop(0)
        for d in COMP.get(c, {}).get("feeds", []):
            if d not in seen and d not in start:
                seen.append(d)
                todo.append(d)
    return seen


def topo(ids):
    order, visiting = [], set()
    def visit(c):
        if c in order or c in visiting:
            return
        visiting.add(c)
        for up, comp in COMP.items():
            if c in comp.get("feeds", []) and up in ids:
                visit(up)
        order.append(c)
    for c in ids:
        visit(c)
    return order


def git_state(rel):
    """Uncommitted and unpushed changes inside one folder of the monorepo."""
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        return None
    run = lambda *a: subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, timeout=15).stdout.strip()
    try:
        dirty = [l for l in run("status", "--porcelain", "--", rel).splitlines() if l.strip()]
        ahead = run("rev-list", "--count", "@{u}..HEAD", "--", rel)
        return {"uncommitted": len(dirty), "unpushed": int(ahead) if ahead.isdigit() else None,
                "last_commit": run("log", "-1", "--format=%cI|%s", "--", rel)}
    except Exception as e:
        return {"error": str(e)[:80]}


# ---------- pending to-dos ----------

def add_pending(st, comp, action, reason, clears_with=None):
    for it in st["pending"]:
        if it["component"] == comp and it["action"] == action:
            if reason not in it["reasons"]:
                it["reasons"].append(reason)
            return
    st["pending"].append({"component": comp, "action": action, "reasons": [reason], "since": now(),
                          "clears_with": clears_with})


BUILD_FIX = "fix build: "


def clear_build_fix(st, cid):
    """A build of cid just succeeded: its 'fix build' to-do is done (audit of 08 Nov 2026; it used to wait for an ack)."""
    st["pending"] = [it for it in st["pending"] if not (it["component"] == cid and it["action"].startswith(BUILD_FIX))]


def ack_pending(st, cid, keep_build_fixes):
    """Clear cid's to-dos. ack --published or --deployed records a publication and keeps a failed build's to-do, which only
    a good build clears, so a republish can no longer hide a broken build (audit of 08 Nov 2026). Returns (cleared, kept)."""
    keep = lambda it: it["component"] != cid or (keep_build_fixes and it["action"].startswith(BUILD_FIX))
    before = len(st["pending"])
    st["pending"] = [it for it in st["pending"] if keep(it)]
    kept = [it for it in st["pending"] if it["component"] == cid]
    return before - len(st["pending"]), kept


def later(a, b):
    """a is after b, for ISO times with any UTC offset (summer +03:00 and winter +02:00 strings do not compare as text)."""
    try:
        return datetime.fromisoformat(a) > datetime.fromisoformat(b)
    except (TypeError, ValueError):
        return (a or "") > (b or "")


def auto_clear(st):
    keep = []
    for it in st["pending"]:
        out = it.get("clears_with")
        if out and mtime_iso(out) and later(mtime_iso(out), it["since"]):
            log({"type": "cleared", "component": it["component"], "action": it["action"], "by": out})
            continue
        keep.append(it)
    st["pending"] = keep


# ---------- publish staleness ----------

def publish_state(cid, st):
    pub = COMP[cid].get("publish")
    if not pub:
        return None
    res = {"type": pub["type"], "url": pub.get("url")}
    if pub["type"] == "artifact":
        src = pub["file"]
        res["source_modified"] = mtime_iso(src)
        cs = st["components"].get(cid, {})
        res["published_at"] = cs.get("published_at")
        if cs.get("published_hash") and os.path.exists(p(src)):
            # exact: the file differs from what was published
            res["behind"] = md5_file(src) != cs["published_hash"]
        elif res["published_at"] and res["source_modified"]:
            # seeded from the artifact list (date only): edited on a later day
            res["behind"] = res["source_modified"][:len(res["published_at"])] > res["published_at"]
        else:
            res["behind"] = None  # unknown until the first ack --published
        if pub.get("local_only"):
            # kept as it is on purpose (08 Nov 2026): no republish to-do, the local page is the current one
            res["local_only"] = pub["local_only"]
            res["behind"] = None
        if pub.get("repo"):
            res["git"] = git_state(COMP[cid]["path"])
    elif pub["type"] == "vercel":
        cs = st["components"].get(cid, {})
        res["deployed_at"] = cs.get("deployed_at")
        res["behind"] = (digest(cid)[0] != cs["deployed_hash"]) if cs.get("deployed_hash") else None
        res["git"] = git_state(COMP[cid]["path"])
    elif pub["type"] == "git":
        res["git"] = git_state(COMP[cid]["path"])
        g = res["git"] or {}
        res["behind"] = bool(g.get("uncommitted") or g.get("unpushed"))
    return res


# ---------- check ----------

AUDIENCE_FILES = ["sites/lumebook-ambassadors/index.html", "sites/lumebook-ambassadors/creators/index.html",
                  "sites/lumebook-ambassadors/apps-script-form.gs"]   # the SMM plan and the signup Form source retired 8 Nov 2026
OLD_NAMES = ["lumebook-smm-plan", "lumebook-ambassadors", "creator-research", "competitor-content-analysis",
             "kids-brand-content-research", "carousel-research", "carousel-playbook-research", "carousel-pipeline",
             "fal-carousel-trial"]
OLD_REL = re.compile(r"(?<![\w/.\-~@:])(" + "|".join(map(re.escape, OLD_NAMES)) + r")/")
OLD_ABS = re.compile(re.escape(ROOT) + r"/(" + "|".join(map(re.escape, OLD_NAMES + ["dashboard"])) + r")(?![\w-])")
OLD_ROOT_DOCS = re.compile(r"(?<![\w/.\-~@:(])(lumebook-product-brief\.md|lumebook-instagram-carousel-playbook-he\.md|lumebook-social-strategy\.html)")
# creative folders folded into media/projects/ on 14 Oct 2026 (see media/README.md)
OLD_MEDIA = re.compile(r"(?<![\w\-.])(output/(?:lume|reel-character|boys-interviews|podcast|imagegen|stories|highlights|reels-2026)"
                       r"|video/(?:fan-transition|text-pull-ben)|carousel/(?:fal-carousel-trial|references))(?![\w\-])")
SCAN_SKIP = {".git", "node_modules", "videos", "analysis", "slides", "img", "img2", ".vercel", ".site-editor", "__pycache__",
             "out", "site", "generated-assets", "discovery", ".lumebook", "versions", "voice-eval-workspace", "drafts", "approved",
             "_to-delete",
             # 8 Nov 2026: other sessions' git worktrees (.claude/worktrees: copies of this repo on their own branches) and the
             # account handoff's frozen copies of the old account's artifacts and database (docs/account-handoff) are records,
             # not project files to fix
             "worktrees", "artifact-copies", "db-export"}
# Claude Code's own permission lists keep the exact commands once allowed (old paths included); they are not project text
SCAN_SKIP_FILES = {"settings.local.json", "settings.json"}
SCAN_EXT = {".py", ".sh", ".md", ".json", ".html", ".js", ".gs", ".css"}


def scan_text_files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SCAN_SKIP]
        for fn in fns:
            if os.path.splitext(fn)[1] in SCAN_EXT and not (fn in SCAN_SKIP_FILES and os.path.basename(dp) == ".claude"):
                f = os.path.join(dp, fn)
                if os.path.getsize(f) < 3_000_000:
                    yield f
    tasks = os.path.expanduser("~/.claude/scheduled-tasks")
    for f in glob.glob(os.path.join(tasks, "lumebook-*", "SKILL.md")):
        yield f


def check():
    issues = []  # (level, area, message)
    add = lambda lvl, area, msg: issues.append({"level": lvl, "area": area, "msg": msg})
    facts = json.load(open(p(REG["facts"]), encoding="utf-8"))

    # registry
    for cid, c in COMP.items():
        if not os.path.exists(p(c["path"])):
            add("error", "registry", f"{cid}: path {c['path']} does not exist")
        if c.get("watch") and not watched_files(cid):
            add("warn", "registry", f"{cid}: watch patterns match no files")
        for d in c.get("feeds", []):
            if d not in COMP:
                add("error", "registry", f"{cid}: feeds unknown component {d}")
        for o in c.get("build", {}).get("outputs", []):
            if not os.path.exists(p(o)):
                add("warn", "registry", f"{cid}: build output {o} missing")
    for a in facts.get("artifacts", []):
        cid = a.get("component")
        if cid and COMP.get(cid, {}).get("publish", {}).get("url") != a["url"]:
            add("error", "facts", f"artifact {a['key']}: facts.json URL differs from lumebook.json {cid}.publish.url")

    # brand copies
    for cp in [c for k in ("brand", "design") for c in COMP.get(k, {}).get("copies", [])]:
        if not os.path.exists(p(cp["from"])):
            add("error", "brand", f"missing canonical {cp['from']}")
        elif not os.path.exists(p(cp["to"])):
            add("warn", "brand", f"copy missing: {cp['to']} (run sync)")
        elif open(p(cp["from"]), "rb").read() != open(p(cp["to"]), "rb").read():
            add("warn", "brand", f"{cp['to']} differs from {cp['from']} (run sync, or move the new file into shared/brand first)")

    # category colours (shared/design/categories.json): valid hues, one hue per category in a set, every
    # component in exactly one workstream, and the generated categories.css up to date
    cat_path = p("shared/design/categories.json")
    if os.path.exists(cat_path):
        try:
            sets = json.load(open(cat_path, encoding="utf-8"))["sets"]
        except (ValueError, KeyError) as e:
            sets = {}
            add("error", "design", f"shared/design/categories.json does not parse: {e}")
        classes = {}
        for sid, st in sets.items():
            nums = [it.get("cat") for it in st.get("items", {}).values()]
            if any(n not in range(0, 9) for n in nums):
                add("error", "design", f"categories.json {sid}: a cat number is outside 0-8")
            if not 3 <= len(nums) <= 8:
                add("warn", "design", f"categories.json {sid}: {len(nums)} categories (colour 3 to 8)")
            dup = sorted({n for n in nums if n and nums.count(n) > 1})
            if dup:
                add("warn", "design", f"categories.json {sid}: hue {', '.join(map(str, dup))} used twice")
            if st.get("class"):
                if st["class"] in classes:
                    add("error", "design", f"categories.json {sid}: class prefix '{st['class']}' also used by {classes[st['class']]}")
                classes[st["class"]] = sid
        ws = sets.get("workstreams", {}).get("items", {})
        if ws:
            owner = {}
            for key, it in ws.items():
                for cid in it.get("components", []):
                    if cid not in COMP:
                        add("warn", "design", f"categories.json workstreams.{key}: unknown component {cid}")
                    if cid in owner:
                        add("warn", "design", f"categories.json: {cid} is in workstreams {owner[cid]} and {key}")
                    owner[cid] = key
            for cid in COMP:
                if cid not in owner:
                    add("warn", "design", f"{cid} has no workstream in shared/design/categories.json (the dashboard shows it uncoloured)")
        try:
            sys.path.insert(0, p("shared/design"))
            import design as _design
            css_path = p("shared/design/categories.css")
            if not os.path.exists(css_path) or open(css_path, encoding="utf-8").read() != _design.categories_css() + "\n":
                add("warn", "design", "shared/design/categories.css is older than categories.json (run sync)")
            js_path = p("shared/design/icons.js")
            if not os.path.exists(js_path) or open(js_path, encoding="utf-8").read() != _design.icons_js():
                add("warn", "design", "shared/design/icons.js is older than icons.json (run sync)")
            nav_path = p("shared/design/nav.js")
            if not os.path.exists(nav_path) or open(nav_path, encoding="utf-8").read() != _design.nav_js():
                add("warn", "design", "shared/design/nav.js is older than hq-tools.json, nav.src.js or the icons (run sync)")
        except Exception as e:  # a broken design.py must not stop the other checks
            add("error", "design", f"shared/design/design.py: {type(e).__name__}: {e}")

    # audience copy: spelling, offer wording, em dashes
    banned = [(w, "brand spelling, use " + facts["brand"]["name_he"]) for w in facts["brand"]["banned_spellings"]]
    banned += [(w, "offer wording, use '" + facts["offer"]["wording_he"] + "'") for w in facts["offer"]["banned_wording_he"]]
    for rel in AUDIENCE_FILES:
        if not os.path.exists(p(rel)):
            continue
        for n, line in enumerate(open(p(rel), encoding="utf-8"), 1):
            for w, why in banned:
                if w in line:
                    add("warn", "copy", f"{rel}:{n} has '{w}' ({why})")
            if "—" in line:
                add("warn", "copy", f"{rel}:{n} has an em dash")

    # commission number must match facts.offer.commission_max_pct (sites, form, creator map messages)
    pct = facts["offer"].get("commission_max_pct")
    rx = re.compile(r"(\d{1,2}) ?%(?:\s*|\\n)(?:עמלה|מכל מכירה|מכל הזמנה)|(\d{1,2})% of each sale|(?:\\u05e2\\u05d3 )(\d{1,2})%")
    for rel in AUDIENCE_FILES + ["creators/creator-research/src/template.html"]:
        if pct and os.path.exists(p(rel)):
            for n, line in enumerate(open(p(rel), encoding="utf-8"), 1):
                for m in rx.finditer(line):
                    v = int(next(g for g in m.groups() if g))
                    if v != pct:
                        add("warn", "copy", f"{rel}:{n} says {v}%; facts.json says one {pct}% allocation per sale")

    # old paths from before the 8 Oct 2026 reorganisation
    for f in scan_text_files():
        rel = os.path.relpath(f, ROOT) if f.startswith(ROOT) else f.replace(os.path.expanduser("~"), "~")
        if rel.startswith(("prompts/", "tools/")):
            continue
        try:
            text = open(f, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for rx in (OLD_REL, OLD_ABS):
            for m in rx.finditer(text):
                n = text.count("\n", 0, m.start()) + 1
                add("warn", "paths", f"{rel}:{n} old path '{m.group(0)}'")
        for m in OLD_MEDIA.finditer(text if not (rel.startswith("media/") and rel.endswith("README.md")) else ""):  # READMEs there record where each job came from
            n = text.count("\n", 0, m.start()) + 1
            add("warn", "paths", f"{rel}:{n} '{m.group(0)}' moved into media/projects/ (14 Oct 2026, see media/README.md)")
        if not rel.startswith("docs/"):
            for m in OLD_ROOT_DOCS.finditer(text):
                before = text[max(0, m.start() - 5):m.start()]
                if not before.endswith("docs/"):
                    n = text.count("\n", 0, m.start()) + 1
                    add("info", "paths", f"{rel}:{n} '{m.group(0)}' is now in docs/")

    return issues


# ---------- sync ----------

def sync(quiet=False):
    done = []
    try:  # categories.css is generated from categories.json; refresh it before it is copied
        sys.path.insert(0, p("shared/design"))
        import design as _design
        if _design.write_categories_css():
            done.append("shared/design/categories.css (generated)")
        if _design.write_icons_js():   # the icon set for pages without a build (5 Nov 2026)
            done.append("shared/design/icons.js (generated)")
        if _design.write_nav_js():     # the project nav for pages without a build: HQ, the SMM plan (5 Nov 2026)
            done.append("shared/design/nav.js (generated)")
    except Exception as e:
        print(f"sync: could not write shared/design/categories.css, icons.js or nav.js: {type(e).__name__}: {e}")
    for cp in [c for k in ("brand", "design") for c in COMP.get(k, {}).get("copies", [])]:
        src, dst = p(cp["from"]), p(cp["to"])
        if os.path.exists(src) and (not os.path.exists(dst) or open(src, "rb").read() != open(dst, "rb").read()):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            done.append(cp["to"])
    if done:
        log({"type": "sync", "copied": done})
    if not quiet:
        print("synced " + (", ".join(done) if done else "nothing (all copies match)"))
    return done


# ---------- status / ripple ----------

def page_file(cid):
    """The page a component's build makes (its publish.file, else its first .html output), so design.head() can tell the
    project nav which page it is in, inside a claude.ai artifact too (LB_PAGE_FILE, 5 Nov 2026)."""
    c = COMP[cid]
    files = [(c.get("publish") or {}).get("file") or ""] + list((c.get("build") or {}).get("outputs", []))
    return next((f for f in files if f.lower().endswith((".html", ".htm"))), "")


def build(cid):
    b = COMP[cid]["build"]
    cmd = [os.path.expanduser(x) for x in b["cmd"]]
    env = dict(os.environ, LB_PAGE_FILE=page_file(cid))
    try:
        r = subprocess.run(cmd, cwd=p(b["cwd"]), capture_output=True, text=True, timeout=900, env=env)
        ok, out = r.returncode == 0, (r.stderr or r.stdout).strip()[-300:]
    except (OSError, subprocess.TimeoutExpired) as e:  # missing folder or interpreter, or a hung build
        ok, out = False, f"{type(e).__name__}: {e}"[:300]
    baked = site_editor.bake_outputs(b.get("outputs", [])) if ok else []   # edits made with the edit button go back in
    if ok:
        i18n.bake_outputs(b.get("outputs", []))   # and the language switch's words (8 Nov 2026)
    log({"type": "build", "component": cid, "ok": ok, "tail": out, **({"baked": baked} if baked else {})})
    return ok, out


def evaluate(st, do_ripple):
    report = {"generated_at": now(), "root": ROOT, "changed": {}, "affected": {}, "built": [], "build_failed": [],
              "components": [], "pending": [], "checks": []}
    changed = {}
    for cid in COMP:
        old = st["components"].get(cid, {}).get("files")
        if old is None:
            continue  # never seen: baseline on this run, nothing to report
        cf = changed_files(cid, old)
        if cf:
            changed[cid] = cf
    report["changed"] = changed
    affected = {}
    for cid in changed:
        for d in downstream([cid]):
            affected.setdefault(d, []).append(cid)
    report["affected"] = affected

    if do_ripple:
        report["baked"] = site_editor.bake_all()
        report["i18n_baked"] = len(i18n.bake_all())
        if "brand" in changed or "design" in changed:
            sync(quiet=True)
        targets = topo(list(dict.fromkeys(list(changed) + list(affected))))
        for cid in targets:
            c = COMP[cid]
            b = c.get("build")
            own = cid in changed
            ups = affected.get(cid, [])
            why = ("own sources changed: " + ", ".join(changed[cid][:3])) if own else ("upstream changed: " + ", ".join(ups))
            if cid == "dashboard":
                # the nightly commit (00:00) and the morning task lumebook-hq-daily refresh it; one to-do that clears itself
                add_pending(st, cid, "refresh the dashboard snapshot (the nightly commit and the morning task lumebook-hq-daily do this)", why, clears_with="sites/dashboard/out/snapshot.json")
                continue
            # a design-system or brand change restyles every page built on it: rebuild those too
            styled = any(u in ("design", "brand") for u in ups)
            if b and b.get("auto") and (own or styled):
                ok, err = build(cid)
                (report["built"] if ok else report["build_failed"]).append(cid)
                if ok:
                    clear_build_fix(st, cid)
                else:
                    add_pending(st, cid, BUILD_FIX + " ".join(b["cmd"]), err or why)
            elif b and (own or styled):
                add_pending(st, cid, "rebuild (manual): cd " + b["cwd"] + " && " + " ".join(b["cmd"]) + (" | " + b["note"] if b.get("note") else ""),
                            why, clears_with=b["outputs"][0])
            # brand and facts reach their consumers automatically (sync, refresh.py); other upstream changes need a look
            real_ups = [u for u in ups if u not in ("brand", "facts", "design")]
            if real_ups and c.get("on_upstream_change"):
                add_pending(st, cid, "review: " + c["on_upstream_change"], "upstream changed: " + ", ".join(real_ups))
        for cid in COMP:
            st["components"].setdefault(cid, {})["files"] = file_hashes(cid)
            if cid in changed or cid in report["built"]:
                st["components"][cid]["changed_at"] = now()
        if changed:
            log({"type": "ripple", "changed": {k: v[:5] for k, v in changed.items()}, "built": report["built"]})
    else:
        for cid in COMP:  # first ever run: record a baseline so later runs can diff
            if "files" not in st["components"].get(cid, {}):
                st["components"].setdefault(cid, {})["files"] = file_hashes(cid)

    auto_clear(st)
    for cid, c in COMP.items():
        pub = publish_state(cid, st)
        item = {"id": cid, "name": c["name"], "kind": c["kind"], "path": c["path"],
                "changed": cid in changed, "changed_at": st["components"].get(cid, {}).get("changed_at"),
                "publish": pub, "schedule": c.get("schedule")}
        report["components"].append(item)
        if pub and pub.get("behind"):
            if pub["type"] == "artifact":
                act = f"republish artifact {pub['url']} from {COMP[cid]['publish']['file']}, then: python3 tools/lumebook.py ack {cid} --published"
            elif pub["type"] == "vercel":
                act = f"deploy the changed site: python3 tools/lumebook.py deploy {cid}"
            else:
                g = pub.get("git") or {}
                act = f"commit and push {c['path']} ({g.get('uncommitted', 0)} uncommitted, {g.get('unpushed', 0)} unpushed)"
            report["pending"].append({"component": cid, "action": act, "reasons": ["source newer than the published copy"], "since": None, "live": True})
    report["pending"] += st["pending"]
    issues = check()
    report["checks"] = issues
    report["counts"] = {"errors": sum(i["level"] == "error" for i in issues), "warnings": sum(i["level"] == "warn" for i in issues),
                        "pending": len(report["pending"]), "changed": len(changed)}
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    json.dump(report, open(STATUS_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return report


def print_report(r, verbose=False):
    c = r["counts"]
    print(f"LumeBook · {r['generated_at'][:16]} · {c['changed']} changed · {c['pending']} to-dos · {c['errors']} errors · {c['warnings']} warnings")
    for cid, files in r["changed"].items():
        print(f"  changed  {cid}: {', '.join(files[:4])}{' …' if len(files) > 4 else ''}")
    for cid, ups in r["affected"].items():
        print(f"  affects  {cid} (from {', '.join(ups)})")
    for cid in r["built"]:
        print(f"  rebuilt  {cid}")
    for cid in r["build_failed"]:
        print(f"  FAILED   {cid}")
    if r["pending"]:
        print("To-do:")
        for it in r["pending"]:
            print(f"  - [{it['component']}] {it['action']}")
    shown = [i for i in r["checks"] if verbose or i["level"] != "info"]
    if shown:
        print("Checks:")
        for i in shown[: (500 if verbose else 25)]:
            print(f"  {i['level']:5} {i['area']:9} {i['msg']}")
        if not verbose and len(shown) > 25:
            print(f"  … {len(shown) - 25} more (python3 tools/lumebook.py check)")


UPLOAD_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".webm", ".m4v", ".mp3", ".m4a", ".wav", ".ogg", ".opus", ".pdf"}
UPLOAD_MAX = 300 * 1024 * 1024
SAMPLE_MAX = 200 * 1024   # largest prompt POST /api/sample takes
SAMPLE_TIMEOUT = 240      # seconds before the claude process is stopped


def claude_bin():
    """The claude CLI: $LUMEBOOK_CLAUDE, else on PATH, else the native install (a login item has a short PATH)."""
    for c in (os.environ.get("LUMEBOOK_CLAUDE"), shutil.which("claude"), os.path.expanduser("~/.local/bin/claude")):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def run_sample(prompt, gone):
    """One question to Claude, the way a claude.ai artifact's `sample` capability works: a prompt in, text out
    (the local twin of it for pages on this server, 6 Nov 2026: the reels hub's ask box).

    Runs `claude -p` with no tools, no saved session, no skills and none of the settings files (so no hooks or plugins),
    from an empty folder (so no project CLAUDE.md or memory), the prompt on stdin and only a short system prompt. It uses
    the Claude login of this Mac (`claude auth login`), never an API key: the environment handed to it is cut down to HOME,
    PATH and the like, so an ANTHROPIC_API_KEY in the server's environment is not used. gone() says the browser gave up;
    the process is then stopped so nothing keeps running for an answer nobody reads.
    Returns (http status, body): 200 {"text"}, or an error {"error", "code"}; the codes match what the page handles."""
    import signal, tempfile, time
    cli = claude_bin()
    if not cli:
        return 503, {"error": "the claude command was not found; install Claude Code or set LUMEBOOK_CLAUDE", "code": "no_cli"}
    work = os.path.join(tempfile.gettempdir(), "lumebook-sample")
    os.makedirs(work, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ("HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TMPDIR", "SHELL")}
    env["PATH"] = os.pathsep.join([os.path.dirname(cli), "/usr/local/bin", "/opt/homebrew/bin", "/usr/bin", "/bin"])
    cmd = [cli, "-p", "--output-format", "json", "--tools", "", "--no-session-persistence", "--disable-slash-commands",
           "--setting-sources", "", "--system-prompt", "Answer exactly what the message asks, as plain text. You have no tools and no files."]
    with tempfile.TemporaryFile() as fin, tempfile.TemporaryFile() as fout:
        fin.write(prompt.encode("utf-8"))
        fin.seek(0)
        proc = subprocess.Popen(cmd, stdin=fin, stdout=fout, stderr=subprocess.DEVNULL, cwd=work, env=env, start_new_session=True)
        t0 = time.time()
        while proc.poll() is None:
            dropped = gone()
            if dropped or time.time() - t0 > SAMPLE_TIMEOUT:
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(proc.pid, sig)
                        proc.wait(10)
                        break
                    except subprocess.TimeoutExpired:
                        continue
                    except ProcessLookupError:
                        break
                return (499, {"error": "cancelled", "code": "cancelled"}) if dropped else (504, {"error": "Claude took too long", "code": "timeout"})
            time.sleep(0.4)
        fout.seek(0)
        raw = fout.read().decode("utf-8", "replace")
    try:
        res = json.loads(raw)
    except ValueError:
        return 502, {"error": "claude gave no readable answer", "code": "failed"}
    return sample_outcome(res)


def sample_outcome(res):
    """The final `result` object of `claude -p` (json, or the last event of stream-json) as (http status, body)."""
    text = res.get("result") if isinstance(res, dict) else None
    if isinstance(res, dict) and res.get("is_error"):
        low = str(text or "").lower()
        if res.get("api_error_status") == 429 or "rate limit" in low or "usage limit" in low:
            return 429, {"error": "Claude is busy or the usage limit is reached", "code": "rate_limited"}
        if "authenticate" in low or "log in" in low or "login" in low or "oauth" in low:
            return 401, {"error": "the claude command is not signed in on this Mac: run claude auth login in a terminal", "code": "not_logged_in"}
        return 502, {"error": "claude failed", "code": "failed"}
    if not isinstance(text, str) or not text.strip():
        return 502, {"error": "empty answer", "code": "empty_completion"}
    return 200, {"text": text}


SAMPLE_PARALLEL = 3        # background answers running at the same time (more wait in line)
SAMPLE_JOBS_KEEP = 40      # finished jobs kept for the page to pick up


class SampleJobs:
    """Background questions to Claude for pages on this server (Yarin, 07 Nov 2026: "if i click רעיון חדש and exit the tab
    i want it to continue in the bg and show me the process and let me do it for a couple of reels simultaneously").

    The page posts a prompt and gets a job id back at once; a worker thread runs the same locked down `claude -p` as
    run_sample, with stream-json so the page can show how far the answer got (`out`, the text so far). The answer waits
    here until a page claims it (and applies it to the reel), so closing the tab loses nothing. At most SAMPLE_PARALLEL
    run together, one per reel. Jobs are kept in a small JSON file (never the prompt), so a restart keeps finished
    answers; a job that was running when the server stopped is marked failed."""

    def __init__(self, path):
        import threading
        self.path, self.lock = path, threading.Lock()
        self.slots = threading.Semaphore(SAMPLE_PARALLEL)
        self.make_slots = threading.Semaphore(REEL_MAKE_PARALLEL)   # reel jobs (kind "make") run one at a time
        self.jobs, self.cancel = {}, {}
        try:
            with open(path, encoding="utf-8") as fh:
                for j in json.load(fh).get("jobs", []):
                    if j.get("status") in ("queued", "running"):
                        j.update(status="failed", code="restarted", ended=now())
                        if j.get("pid"):
                            stop_orphan(j["pid"])   # a reel job's Claude outlives the server otherwise
                    j.pop("out", None)
                    self.jobs[j["id"]] = j
        except (FileNotFoundError, ValueError, KeyError, AttributeError):
            pass

    def _save(self):   # with self.lock held
        keep = sorted(self.jobs.values(), key=lambda j: j.get("started", ""))
        done = [j for j in keep if j["status"] not in ("queued", "running")]
        for j in done[:max(0, len(done) - SAMPLE_JOBS_KEEP)]:
            self.jobs.pop(j["id"], None)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"jobs": [{k: v for k, v in j.items() if k != "out"} for j in self.jobs.values()]}, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)

    def list(self):
        with self.lock:
            return sorted((dict(j) for j in self.jobs.values()), key=lambda j: j.get("started", ""))

    def start(self, prompt, meta, make=None):
        """make: the reel job's settings (_run_make: Claude plans, the fixed recipe builds), else a plain question.
        One job per reel of either kind: a reel being made never gets its text rewritten under it."""
        import threading, secrets
        reel = meta.get("reel") or ""
        with self.lock:
            if reel and any(j.get("reel") == reel and j["status"] in ("queued", "running") for j in self.jobs.values()):
                return 409, {"error": "this reel already has a question running", "code": "busy_reel"}
            jid = datetime.now(IL).strftime("%H%M%S") + secrets.token_hex(3)
            job = {"id": jid, "reel": reel, "kind": meta.get("kind") or "new", "label": meta.get("label") or "",
                   "comment": meta.get("comment") or "", "status": "queued", "started": now(), "out": "", "chars": 0}
            if make:
                job.update(kind="make", step="", steps=0)
            self.jobs[jid] = job
            self.cancel[jid] = threading.Event()
            self._save()
        if make:
            threading.Thread(target=self._run_make, args=(jid, prompt, make), daemon=True).start()
        else:
            threading.Thread(target=self._run, args=(jid, prompt), daemon=True).start()
        return 202, {"job": dict(job)}

    def _run_make(self, jid, prompt, make):
        """A reel job in two parts. 1) Claude plans: the same locked down `claude -p` as every ask (no tools, no files), asked for the
        reel's edit.json as JSON. 2) The server builds: the plan is checked (clean_edit: only the reel's own dropped files, known keys,
        numbers in range), written to edit.json, and the fixed recipe runs (`reels.py make <id>`: reel_make.py and the reel editor).
        Claude never runs a command; its answer is data. make: {"folder", "rid", "merge", "test"} from the endpoint."""
        import time
        t0 = time.time()
        with self.make_slots:
            stop = self.cancel[jid]
            if stop.is_set():
                self._set(jid, status="cancelled", code="cancelled", ended=now())
                self.cancel.pop(jid, None)
                return
            self._set(jid, status="running", stage="thinking", ran=now(), step="Claude מתכנן את העריכה", steps=1)

            def step(text):
                with self.lock:
                    j = self.jobs.get(jid)
                    if j:
                        j["step"] = text[:160]
                        j["steps"] = j.get("steps", 0) + 1

            def heard(kind, text):
                with self.lock:
                    j = self.jobs.get(jid)
                    if j and kind == "text" and j.get("stage") != "writing":
                        j.update(stage="writing", step="Claude כותב את תוכנית העריכה", steps=j.get("steps", 0) + 1)
            status, body = run_sample_stream(prompt, stop.is_set, heard)
            result = build_reel(make, body.get("text", ""), stop.is_set, step, lambda pid: self._set(jid, pid=pid)) if status == 200 else (status, body)
        status, body = result
        fin = os.path.join(make["folder"], "final")
        made = sorted(f for f in os.listdir(fin) if f.lower().endswith(".mp4") and os.path.getmtime(os.path.join(fin, f)) >= t0) if os.path.isdir(fin) else []
        if status == 200:
            self._set(jid, status="done", text=body["text"], checks=body.get("checks", []), made=made, ended=now(), pid=None)
        else:
            self._set(jid, status="cancelled" if body.get("code") == "cancelled" else "failed", code=body.get("code"),
                      error=body.get("error"), made=made, ended=now(), pid=None)
        with self.lock:
            steps = (self.jobs.get(jid) or {}).get("steps", 0)
        log({"type": "reel-make", "status": status, "code": body.get("code"), "steps": steps, "made": len(made),
             "prompt_chars": len(prompt), "seconds": round(time.time() - t0, 1)})
        self.cancel.pop(jid, None)

    def _set(self, jid, **kw):
        with self.lock:
            j = self.jobs.get(jid)
            if j:
                j.update(kw)
                if "status" in kw:
                    self._save()

    def _run(self, jid, prompt):
        import time
        t0 = time.time()
        with self.slots:
            stop = self.cancel[jid]
            if stop.is_set():
                self._set(jid, status="cancelled", code="cancelled", ended=now())
                return
            self._set(jid, status="running", stage="thinking", ran=now())

            def delta(kind, text):
                with self.lock:
                    j = self.jobs.get(jid)
                    if j:
                        if kind == "text":
                            j["out"] = (j.get("out") or "") + text
                            j["chars"] = len(j["out"])
                        j["stage"] = "writing" if kind == "text" else "thinking"
            status, body = run_sample_stream(prompt, stop.is_set, delta)
        if status == 200:
            self._set(jid, status="done", text=body["text"], ended=now(), out="")
        else:
            self._set(jid, status="cancelled" if body.get("code") == "cancelled" else "failed", code=body.get("code"),
                      error=body.get("error"), ended=now(), out="")
        log({"type": "sample-job", "status": status, "code": body.get("code"), "prompt_chars": len(prompt),
             "seconds": round(time.time() - t0, 1)})
        self.cancel.pop(jid, None)

    def act(self, jid, what):
        """cancel a running job, claim a finished answer (only once: two open tabs never both apply it), dismiss a row"""
        with self.lock:
            j = self.jobs.get(jid)
            if not j:
                return 404, {"error": "no such job", "code": "gone"}
            if what == "cancel":
                ev = self.cancel.get(jid)
                if ev:
                    ev.set()
                return 200, {"job": dict(j)}
            if what == "claim":
                if j["status"] != "done" or j.get("claimed"):
                    return 409, {"error": "not ready or already taken", "code": "taken"}
                j["claimed"] = now()
                self._save()
                return 200, {"job": dict(j)}
            if what == "dismiss":
                if j["status"] in ("queued", "running"):
                    return 409, {"error": "still running", "code": "running"}
                self.jobs.pop(jid)
                self._save()
                return 200, {"ok": True}
        return 400, {"error": "unknown action", "code": "failed"}


def run_sample_stream(prompt, stopped, on_delta):
    """run_sample for a background job: the same command and limits, with stream-json so on_delta(kind, text) hears the
    answer as it is written ("thinking" or "text"). stopped() asks for a stop. Returns (http status, body) like run_sample."""
    import signal, tempfile, threading, time
    cli = claude_bin()
    if not cli:
        return 503, {"error": "the claude command was not found; install Claude Code or set LUMEBOOK_CLAUDE", "code": "no_cli"}
    work = os.path.join(tempfile.gettempdir(), "lumebook-sample")
    os.makedirs(work, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ("HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TMPDIR", "SHELL")}
    env["PATH"] = os.pathsep.join([os.path.dirname(cli), "/usr/local/bin", "/opt/homebrew/bin", "/usr/bin", "/bin"])
    cmd = [cli, "-p", "--output-format", "stream-json", "--verbose", "--include-partial-messages", "--tools", "",
           "--no-session-persistence", "--disable-slash-commands", "--setting-sources", "",
           "--system-prompt", "Answer exactly what the message asks, as plain text. You have no tools and no files."]
    final = {}
    with tempfile.TemporaryFile() as fin:
        fin.write(prompt.encode("utf-8"))
        fin.seek(0)
        proc = subprocess.Popen(cmd, stdin=fin, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=work, env=env,
                                start_new_session=True)

        def read():
            for line in proc.stdout:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(ev, dict):
                    continue
                if ev.get("type") == "result":
                    final["res"] = ev
                elif ev.get("type") == "stream_event":
                    d = (ev.get("event") or {}).get("delta") or {}
                    if d.get("type") == "text_delta":
                        on_delta("text", d.get("text") or "")
                    elif d.get("type") == "thinking_delta":
                        on_delta("thinking", "")
        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        t0 = time.time()
        while proc.poll() is None:
            dropped = stopped()
            if dropped or time.time() - t0 > SAMPLE_TIMEOUT:
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(proc.pid, sig)
                        proc.wait(10)
                        break
                    except subprocess.TimeoutExpired:
                        continue
                    except ProcessLookupError:
                        break
                return (499, {"error": "cancelled", "code": "cancelled"}) if dropped else (504, {"error": "Claude took too long", "code": "timeout"})
            time.sleep(0.3)
        reader.join(5)
    if "res" not in final:
        return 502, {"error": "claude gave no readable answer", "code": "failed"}
    return sample_outcome(final["res"])


# ---- making a reel from its card in the reels hub (Yarin, 07 Nov 2026: "a full file dropping and a prompt text box to the reel
# cards so i could let you create the reel through there"). Dropped files go into the reel's media folder. A reel job asks Claude
# (no tools, like every ask) for the reel's edit.json, checks it, and runs the fixed recipe (reels.py make: reel_make.py + the reel
# editor). A Claude with a shell, started by the page on its own, was refused by the safety check on 07 Nov 2026 and is not built.
REELS_SRC = "research/israeli-product-reels/src/scripts/series-2026-11"
REEL_UPLOAD_EXT = UPLOAD_EXT | {".heic", ".aac", ".mkv"}
REEL_UPLOAD_MAX = 4 * 1024 ** 3        # one dropped file (iPhone 4K takes are large)
REEL_BUILD_TIMEOUT = 30 * 60           # seconds the recipe may run (whisper and the encodes are slow)
REEL_MAKE_PARALLEL = 1                 # reel jobs at the same time (video work is heavy); the rest wait in line


def reel_kind(name):
    ext = os.path.splitext(name)[1].lower()
    if ext in (".mp4", ".mov", ".m4v", ".webm", ".mkv"):
        return "video"
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic"):
        return "image"
    if ext in (".mp3", ".m4a", ".wav", ".ogg", ".opus", ".aac"):
        return "audio"
    return "file"


def reel_env():
    """The environment of the recipe: the server's, with a PATH that finds ffmpeg, ffprobe and avconvert from a login item."""
    extra = [os.path.expanduser("~/.local/bin"), "/usr/local/bin", "/opt/homebrew/bin", "/usr/bin", "/bin", "/usr/sbin", "/sbin"]
    return dict(os.environ, PATH=os.pathsep.join([x for x in os.environ.get("PATH", "").split(os.pathsep) if x] + extra))


def stop_orphan(pid):
    """Stop the process group of a reel job whose server went away, only if it is still the recipe or a claude command (a pid can
    be reused after the Mac restarts)."""
    import signal
    try:
        cmdline = subprocess.run(["ps", "-o", "command=", "-p", str(int(pid))], capture_output=True, text=True, timeout=5).stdout
        if any(w in cmdline for w in ("reels.py", "reel_make.py", "reel_editor.py", "claude")):
            os.killpg(int(pid), signal.SIGTERM)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass


def media_info(path):
    """Length, size and sound of one dropped file (ffprobe), for Claude's plan; {} when ffprobe cannot read it."""
    probe = shutil.which("ffprobe", path=reel_env()["PATH"])
    if not probe or reel_kind(path) not in ("video", "audio", "image"):
        return {}
    try:
        out = subprocess.run([probe, "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height", "-of", "json", path],
                             capture_output=True, text=True, timeout=20).stdout
        j = json.loads(out or "{}")
    except (OSError, ValueError, subprocess.SubprocessError):
        return {}
    st = j.get("streams") or []
    v = next((s for s in st if s.get("codec_type") == "video"), {})
    info = {"audio": any(s.get("codec_type") == "audio" for s in st)}
    try:
        info["seconds"] = round(float((j.get("format") or {}).get("duration")), 2)
    except (TypeError, ValueError):
        pass
    if v.get("width"):
        info["size"] = f"{v['width']}x{v['height']}"
    return info


def reel_plan_prompt(r, folder, files, script, ask):
    """What Claude is asked for a reel job: the reel's edit.json as JSON. Written here, not in the page: the page sends only the reel,
    Yarin's words and the script as it shows it."""
    try:
        with open(p(REELS_SRC + "/reels.json"), encoding="utf-8") as fh:
            d = json.load(fh).get("defaults", {})
        with open(p(REELS_SRC + "/reel_make.py"), encoding="utf-8") as fh:
            doc = fh.read().split('"""')[1].strip()
    except (OSError, ValueError, IndexError):
        d, doc = {}, ""
    try:
        with open(os.path.join(folder, "edit.json"), encoding="utf-8") as fh:
            edit_now = fh.read()[:6000]
    except OSError:
        edit_now = ""

    def one(v, n=1500):
        return " ".join(str(v or "").split())[:n]

    def many(v):
        return [one(x, 400) for x in (v if isinstance(v, list) else []) if one(x)][:40]
    vo = many(script.get("vo")) or many(r.get("vo"))
    rows = []
    for f in files:
        i = media_info(os.path.join(folder, f["path"]))
        bits = [f["kind"]] + ([f"{i['seconds']:g} s"] if "seconds" in i else []) + ([i["size"]] if "size" in i else []) + \
               (["with sound" if i.get("audio") else "no sound"] if f["kind"] == "video" else [])
        rows.append(f"- {f['path']}: {', '.join(bits)}")
    L = [f"You plan the edit of LumeBook's Instagram reel {r['id']} (personalised children's books, Israel). Yarin dropped his files on the "
         "reel's card and wrote what he wants. Your answer becomes the reel's edit.json, and the fixed recipe reel_make.py then builds the "
         "video from it: it cuts the pauses, takes the caption spelling from the script, and burns the hook, the word by word captions and "
         "the closing card. You see no pictures: decide from the file names, their lengths, the shooting notes and Yarin's words.",
         "", "How edit.json works (from reel_make.py):", doc, "",
         "The reel",
         f"- voice: {r.get('voice')} (yarin = his own voiceover), talks to {'grandmothers' if r.get('audience') == 'grandma' else 'parents'}",
         f"- hook (top text of the first seconds): {one(script.get('hook')) or one(r.get('hook'))}",
         "- voiceover lines, numbered from 0 as \"at\" counts them (the recipe adds the closing line \"" + one(d.get("cta_voice")) + "\", cued as \"cta\"):"]
    L += [f"  {i}. {x}" for i, x in enumerate(vo)] or ["  (none)"]
    sees = many(script.get("sees")) or many(r.get("sees"))
    if sees:
        L += ["- what is seen while each line plays (Yarin's notes, same numbers):"] + [f"  {i}. {x}" for i, x in enumerate(sees)]
    for key, lab, base in (("shot", "shooting notes", r.get("shot")), ("films", "what Yarin films", ", ".join(r.get("yarin_films") or []))):
        v = one(script.get(key)) or one(base)
        if v:
            L.append(f"- {lab}: {v}")
    L += ["", "The files Yarin dropped (use these paths exactly, nothing else):"] + (rows or ["- none"])
    if edit_now:
        L += ["", "The edit.json there now (a template from when the folder was made, \"_footage\" says what each segment was meant to show):", edit_now]
    L += ["", "What Yarin asked for (his words):", one(ask, 6000) or "(nothing written: plan it from the files and the script)", "",
          "Rules: use only the paths listed above and never invent one; the first segment starts at 0 and the segments follow the script "
          "in order; a cue word must be a word of the script; leave out keys you do not need (no TODO paths, no _about or _footage keys). "
          "If these files cannot make the reel (for example no voice take and no talking take), return \"edit\": null and say what is missing.",
          "",
          "Return only JSON, no other text:",
          "{\"edit\": {the edit.json object} or null, \"summary\": \"one or two short Hebrew sentences for Yarin, without dashes: which file "
          "goes where\", \"missing\": \"Hebrew: what he still needs to film or drop, empty when nothing is missing\"}"]
    return "\n".join(L)


def clean_edit(e, paths, images):
    """Claude's plan cut down to what reel_make.py reads, with every file one of the reel's own dropped files and every number in
    range. Returns (edit, "") or (None, why)."""
    if not isinstance(e, dict):
        return None, "the plan has no edit"

    def num(v, lo, hi):
        return isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= hi

    def cue(v):
        return (isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 200) or (isinstance(v, str) and 0 < len(v) <= 40 and "\n" not in v)
    out = {}
    for k in ("take", "hook_clip", "voice"):
        if e.get(k) is not None:
            if e[k] not in paths:
                return None, f"{k} {e[k]!r} is not one of the dropped files"
            out[k] = e[k]
    for k, lo, hi in (("voice_start", 0, 600), ("speed_after_hook", 0.8, 1.6)):
        if e.get(k) is not None:
            if not num(e[k], lo, hi):
                return None, f"{k} {e[k]!r} is out of range"
            out[k] = e[k]
    if "hook_end" in e:
        if e["hook_end"] is not None and not num(e["hook_end"], 0, 60):
            return None, f"hook_end {e['hook_end']!r} is out of range"
        out["hook_end"] = e["hook_end"]
    bg = e.get("background")
    if bg is not None:
        if not isinstance(bg, dict) or bg.get("src") not in paths or not num(bg.get("ss", 0), 0, 7200):
            return None, "background is not one of the dropped files"
        out["background"] = {"src": bg["src"], "ss": bg.get("ss", 0)}
    ov = e.get("hook_overlay")
    if ov is not None:
        if not isinstance(ov, dict) or ov.get("img") not in images or not num(ov.get("y", 1230), 0, 1920):
            return None, "hook_overlay is not one of the dropped pictures"
        out["hook_overlay"] = {"img": ov["img"], "y": ov.get("y", 1230)}
    segs = e.get("segments")
    if segs is not None:
        if not isinstance(segs, list) or len(segs) > 40:
            return None, "segments is not a list"
        out["segments"] = []
        for s in segs:
            if not isinstance(s, dict) or not cue(s.get("at")) or s.get("src") not in paths:
                return None, f"segment {s!r} has a wrong cue or a file that was not dropped"
            c = {"at": s["at"], "src": s["src"], "ss": s.get("ss", 0)}
            if not num(c["ss"], 0, 7200):
                return None, f"segment start {c['ss']!r} is out of range"
            if s.get("window") is not None:
                c["window"] = bool(s["window"])
            if s.get("speed") is not None:
                if not num(s["speed"], 0.25, 4):
                    return None, f"segment speed {s['speed']!r} is out of range"
                c["speed"] = s["speed"]
            if s.get("crop") is not None:
                if not isinstance(s["crop"], str) or not re.fullmatch(r"\d{1,5}:\d{1,5}:\d{1,5}:\d{1,5}", s["crop"]):
                    return None, f"segment crop {s['crop']!r} is not w:h:x:y"
                c["crop"] = s["crop"]
            out["segments"].append(c)
    cards = e.get("top_cards")
    if cards is not None:
        if not isinstance(cards, list) or len(cards) > 20:
            return None, "top_cards is not a list"
        out["top_cards"] = []
        for c in cards:
            if not isinstance(c, dict) or not cue(c.get("at")) or not isinstance(c.get("text"), str) or not 0 < len(c["text"]) <= 24:
                return None, f"top card {c!r} is not a cue and a short text"
            t = {"at": c["at"], "text": c["text"]}
            if c.get("size") is not None:
                if not num(c["size"], 20, 300):
                    return None, f"top card size {c['size']!r} is out of range"
                t["size"] = c["size"]
            out["top_cards"].append(t)
    if not out.get("take") and not (out.get("hook_clip") and out.get("voice")):
        return None, "the plan needs one talking take, or a hook clip and a voice take"
    return out, ""


def build_reel(make, answer, stopped, step, on_pid):
    """Part 2 of a reel job: Claude's plan (answer, JSON text) in, the video out. Checks the plan, writes edit.json (an earlier one
    moves to work/edit-<time>.json), copies this reel's page edits into reels.json when the page showed other text (reels.py merge
    local <id>), keeps an earlier final/reel-<id>-1.mp4 under a dated name, and runs the fixed recipe with its output as steps.
    LUMEBOOK_REEL_MAKE_CMD replaces the recipe on a test server. Returns (http status, body) like run_sample."""
    import shlex, signal, threading, time
    t = str(answer or "").strip()
    t = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", t)
    a, b = t.find("{"), t.rfind("}")
    try:
        plan = json.loads(t[a:b + 1] if a >= 0 and b > a else t)
    except ValueError:
        return 502, {"error": "the plan was not JSON", "code": "invalid_json"}
    if not isinstance(plan, dict):
        return 502, {"error": "the plan was not a JSON object", "code": "invalid_json"}

    def said(v):
        return re.sub(r"\s*[\u2014\u2013]\s*", ", ", " ".join(str(v or "").split()))[:600]
    summary, missing = said(plan.get("summary")), said(plan.get("missing"))
    if plan.get("edit") is None:
        return 200, {"text": " ".join(x for x in (summary, missing) if x) or "חסרים חומרים כדי ליצור את הריל.", "checks": []}
    edit, why = clean_edit(plan["edit"], make["paths"], make["images"])
    if not edit:
        return 422, {"error": why, "code": "bad_plan"}
    folder, rid = make["folder"], make["rid"]
    work, fin = os.path.join(folder, "work"), os.path.join(folder, "final")
    os.makedirs(work, exist_ok=True)
    logf = open(os.path.join(work, "reel-job.log"), "a", encoding="utf-8")

    def note(line):
        logf.write(f"{datetime.now(IL).strftime('%Y-%m-%d %H:%M:%S')} {line}\n")
        logf.flush()
    try:
        step("שומר את תוכנית העריכה")
        note("plan: " + json.dumps(edit, ensure_ascii=False))
        ej = os.path.join(folder, "edit.json")
        if os.path.exists(ej):
            shutil.move(ej, os.path.join(work, "edit-" + datetime.now(IL).strftime("%Y%m%d-%H%M%S") + ".json"))
        with open(ej, "w", encoding="utf-8") as fh:
            json.dump({"_about": f"Written {now()} by a reel job of the reels hub from Claude's plan (tools/lumebook.py build_reel); "
                                 "reels.py make reads it.", **edit}, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        env = reel_env()
        if make.get("merge"):
            step("מעתיק לתסריט את העריכות מהעמוד")
            m = subprocess.run([sys.executable, p(REELS_SRC + "/reels.py"), "merge", "local", rid], cwd=ROOT, env=env,
                               capture_output=True, text=True, timeout=120)
            note("merge local: " + " ".join((m.stdout + m.stderr).split())[-400:])
        name = "reel-" + rid.replace(".", "-")
        stamp = datetime.now(IL).strftime("%Y%m%d-%H%M%S")
        kept = []   # (where it was, where it is now): an earlier finished reel keeps a dated name, never overwritten

        def put_back():   # the build failed or was stopped and wrote nothing new: the earlier reel takes its name again
            if not os.path.exists(os.path.join(fin, name + "-1.mp4")):
                for was, now_at in kept:
                    if os.path.exists(now_at) and not os.path.exists(was):
                        shutil.move(now_at, was)
        for suffix in ("-1.mp4", "-qc.jpg"):
            old = os.path.join(fin, name + suffix)
            if os.path.exists(old):
                base, ext = os.path.splitext(old)
                dest, n = f"{base}-{stamp}{ext}", 2
                while os.path.exists(dest):
                    dest, n = f"{base}-{stamp}-{n}{ext}", n + 1
                shutil.move(old, dest)
                kept.append((old, dest))
        cmd = (shlex.split(os.environ["LUMEBOOK_REEL_MAKE_CMD"]) if os.environ.get("LUMEBOOK_REEL_MAKE_CMD")
               else [sys.executable, p(REELS_SRC + "/reels.py"), "make"]) + [rid] + (["--folder", folder] if make.get("test") else [])
        step("בונה את הריל: מכין את הקול")
        proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                                start_new_session=True)
        on_pid(proc.pid)
        lines, checks = [], []

        def read():
            for raw in proc.stdout:
                line = raw.rstrip()
                if not line:
                    continue
                lines.append(line)
                note("make: " + line)
                s = line.strip()
                if s.startswith("check:"):
                    c = s[6:].strip()   # reel_make.py align(): what whisper heard against the script, said in Hebrew for the card
                    for pat, he in ((r"heard (.+), script says (.+) \(script kept\)", r"נשמע \1, בתסריט \2 (נשאר התסריט)"),
                                    (r"heard (.+), script says (.+) \(times spread\)", r"נשמע \1, בתסריט \2 (הזמנים נפרסו)"),
                                    (r"not heard: (.+?) \(.*\)$", r"לא נשמע: \1"),
                                    (r"heard but not in the script: (.+?) \(.*\)$", r"נשמע ולא בתסריט: \1")):
                        c = re.sub(pat, he, c)
                    checks.append(c[:200])
                    step("בדיקה: " + c[:120])
                elif s.startswith("sound:"):
                    step("הקול מוכן, מתמלל ומתאים לתסריט")
                elif re.match(r"s\d+\s|take\s", s):
                    step("מרכיב את הקטעים")
                elif s.startswith("length"):
                    step("שורף כותרת, כתוביות וכרטיס סיום")
        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        t0 = time.time()
        while proc.poll() is None:
            dropped = stopped()
            if dropped or time.time() - t0 > REEL_BUILD_TIMEOUT:
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(proc.pid, sig)
                        proc.wait(10)
                        break
                    except subprocess.TimeoutExpired:
                        continue
                    except ProcessLookupError:
                        break
                note("stopped" if dropped else "timed out")
                put_back()
                return (499, {"error": "cancelled", "code": "cancelled"}) if dropped else (504, {"error": "the recipe took too long", "code": "timeout"})
            time.sleep(0.5)
        reader.join(5)
        note(f"recipe exit {proc.returncode}")
        if proc.returncode != 0 or not os.path.exists(os.path.join(fin, name + "-1.mp4")):
            put_back()
            last = next((x.strip() for x in reversed(lines) if x.strip()), "no output")
            return 500, {"error": last[:300], "code": "build_failed"}
        return 200, {"text": summary or "הריל מוכן.", "checks": checks[:10]}
    finally:
        logf.close()


def serve(port):
    """Static server for the whole project folder, no caching, so every page and research report is one URL away.

    Three small endpoints for the dashboard work board, all on 127.0.0.1 only:
      GET  /api/board/env       tells the board it runs on the project server (local media previews, uploads)
      GET  /api/local-tools     pings the services in facts.local_tools (Carousel Machine...) from here; starts nothing
      POST /api/media-inbox     saves one uploaded file into media/inbox/ (the unsorted folder of media/README.md),
                                same-origin only (Origin header + X-LumeBook-Board), allowed media types, never overwrites
      GET  /api/creator-map/state   the creator map's saved data (statuses, notes, settings, voice) from creators/creator-research/state/
      PUT  /api/creator-map/doc?path=outreach/<handle>   writes one document of it (same-origin only; paths limited to
                                outreach, settings, voice, log); this replaced the artifact database on 20 Oct 2026
      GET  /api/home            HQ's home numbers, live (sites/dashboard/home_stats.py collect(): Carousel Machine, creator map,
                                reel calendar, ambassadors, Instagram and Facebook, most used pages, what needs attention);
                                cached 20 seconds; 8 Nov 2026. Every page open (a document request for a project page or
                                /hook-studio/) adds one to today's count in .lumebook/page-views.json for "most used"
      GET  /api/hq/layout       HQ's tools layout as Yarin arranged it (sites/dashboard/hq-layout.json; {} when never saved)
      PUT  /api/hq/layout       saves it (same-origin only, one JSON object, at most 512 KB); edit mode of HQ, 5 Nov 2026
      GET  /                    redirects to the HQ dashboard
      /hook-studio/             Carousel Machine (the login item on 127.0.0.1:8777) through this server: its own paths
                                (HS_PREFIX) are forwarded as they are, POSTs same-origin only; nothing of it runs here
      /__site-editor/           the edit button: every HTML page (and every forwarded Carousel Machine page) is sent with
                                the button, the edits runtime and the page's saved edits; GET info/source, PUT save/upload
                                (same-origin, X-Site-Editor header). tools/site_editor.py, shared/site-editor/README.md
      POST /api/sample          {"prompt": "..."} -> {"text": "..."}: one question to Claude through `claude -p` (no tools, no
                                settings, empty working folder; run_sample above), for pages that need what a claude.ai
                                artifact's sample capability gives (the reels hub's ask box, 6 Nov 2026). Same-origin only
                                (Origin + X-LumeBook-Board), one at a time, 200 KB at most; the prompt is never logged.
                                Needs `claude auth login` on this Mac once; the answer comes from that login's plan.
      POST /api/i18n/missing    {"page", "to": "en"|"he", "items": [{"k", "scope"}]}: blocks a page's language dictionaries lack
                                (the language switch, 8 Nov 2026); a background worker (tools/i18n.py Worker) translates them
                                through the same locked down `claude -p` (Sonnet, thinking off) into shared/i18n. Same-origin only.
      GET  /api/i18n/dict       ?page=&lang=&rev=: the page's words in one language when they changed since rev, and how many
                                blocks are still waiting. Every page this server shows carries its words (site_editor.inject).
      GET  /api/reels-hub/state the reels hub's own edits ({edits, made, requests}, each a map of documents) from
                                research/israeli-product-reels/src/scripts/series-2026-11/local-edits.json ({} when none)
      POST /api/sample/jobs     {"prompt", "reel", "kind", "label", "comment"} -> 202 {"job"}: the same question as a background
                                job (SampleJobs above): it keeps running when the tab closes, up to 3 at once, one per reel
      GET  /api/sample/jobs     {"jobs": [...]}: every job with its status, the text written so far while it runs
                                ("out", "chars") and the answer when done ("text"); never the prompt
      POST /api/sample/jobs/<id>/cancel|claim|dismiss   stop it, take the answer (once), or drop the row; same-origin only
      PUT  /api/reels-hub/doc?path=edits/<key>   writes one document (also made/<key>, requests/<id>); same-origin only,
                                at most 256 KB each; the hub page on this server saves here instead of the artifact
                                database, and `reels.py merge local` copies the edits into reels.json (6 Nov 2026)
      GET  /api/reel-files?reel=r5-5   the reel's media folder: {project, files (source/), finals (final/*.mp4, newest first)}
      GET  /api/reel-files/raw?reel=r5-5&f=source/x.mov   one of those files (Range requests, so the page's players can seek)
      POST /api/reel-files?reel=r5-5&name=x.mov   one dropped file (the body) into the reel's source/, never overwriting; the first
                                one opens the folder with `reels.py new <id>`; same-origin only, media types, 4 GB at most (7 Nov 2026)
      POST /api/reel-files/remove?reel=r5-5&f=source/x.mov   moves a dropped file to _to-delete/ with a README line; same-origin only
      POST /api/reel-make/jobs  {"reel", "prompt", "script", "label"} -> 202 {"job"}: a reel job (kind "make") in the same list as the
                                asks: Claude plans the edit (no tools), the plan is checked and written to edit.json, and the fixed
                                recipe `reels.py make <id>` builds the video; one at a time, cancel/dismiss as above (build_reel)
    The commands are fixed: only the prompt (on stdin) and checked data (a reel id, edit.json values) come from the page."""
    import http.client, http.server, functools, urllib.parse, urllib.request, threading, select, socket
    sample_lock = threading.Lock()
    origins = {f"http://localhost:{port}", f"http://127.0.0.1:{port}"}
    local_hosts = {f"localhost:{port}", f"127.0.0.1:{port}", f"[::1]:{port}"}   # Host headers of this server's own pages
    state_dir = p("creators/creator-research/state")
    state_lock = threading.Lock()
    hq_layout = p("sites/dashboard/hq-layout.json")
    views_file = p(".lumebook/page-views.json")
    views_lock = threading.Lock()
    home_cache = {"at": 0.0, "data": None, "mtime": None, "mod": None}

    def count_view(page):
        """One more open of a project page today (HQ home's "most used", 8 Nov 2026); 45 days kept."""
        with views_lock:
            try:
                with open(views_file, encoding="utf-8") as fh:
                    v = json.load(fh)
            except (OSError, ValueError):
                v = {}
            days = v.setdefault("days", {})
            day = datetime.now().date().isoformat()
            days.setdefault(day, {})[page] = days.get(day, {}).get(page, 0) + 1
            for old_day in sorted(days)[:-45]:
                del days[old_day]
            os.makedirs(os.path.dirname(views_file), exist_ok=True)
            tmp = views_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(v, fh, ensure_ascii=False, indent=0)
            os.replace(tmp, views_file)

    def home_stats():
        """sites/dashboard/home_stats.py, reloaded when the file changes, so an edit there needs no server restart."""
        import importlib.util, time
        path = p("sites/dashboard/home_stats.py")
        mt = os.path.getmtime(path)
        if home_cache["mod"] is None or home_cache["mtime"] != mt:
            spec = importlib.util.spec_from_file_location("lumebook_home_stats", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            home_cache.update(mod=mod, mtime=mt, at=0.0)
        if time.time() - home_cache["at"] > 20 or home_cache["data"] is None:
            home_cache["data"] = home_cache["mod"].collect()
            home_cache["at"] = time.time()
        return home_cache["data"]
    # LUMEBOOK_REELS_HUB_FILE: a test server on a spare port writes somewhere else, never into Yarin's real edits
    reels_hub_file = os.environ.get("LUMEBOOK_REELS_HUB_FILE") or p("research/israeli-product-reels/src/scripts/series-2026-11/local-edits.json")
    sample_jobs = SampleJobs(os.environ.get("LUMEBOOK_SAMPLE_JOBS_FILE") or p(".lumebook/sample-jobs.json"))
    # the language switch (8 Nov 2026): pages report words their dictionaries lack, this translates them in the background
    i18n_worker = i18n.Worker(log=lambda m: print(m, file=sys.stderr, flush=True))
    if i18n.pending():
        i18n_worker.wake()   # words left waiting when the server last stopped
    sample_job_act = re.compile(r"^/api/sample/jobs/([0-9a-f]{6,20})/(cancel|claim|dismiss)$")
    reels_hub_doc = re.compile(r"^(edits|made|requests)/([\w.\-]{1,120})$")
    # LUMEBOOK_REEL_MEDIA: a test server keeps each reel's files in <that folder>/<key> and never runs reels.py new or merge
    reel_media_test = os.environ.get("LUMEBOOK_REEL_MEDIA")
    reel_lock = threading.Lock()
    reel_key = re.compile(r"^r(\d{1,2})-(\d{1,2})$")

    def reel_dir(key, create=False):
        """(the reel in reels.json, its media folder or None) for a hub key such as r5-5; (None, None) when there is no such reel.
        create opens the folder the way `reels.py new` does (which also writes the reel's "project" into reels.json)."""
        m = reel_key.match(key or "")
        if not m:
            return None, None
        rid = f"{m.group(1)}.{m.group(2)}"

        def find():
            try:
                with open(p(REELS_SRC + "/reels.json"), encoding="utf-8") as fh:
                    return next((x for x in json.load(fh)["reels"] if x.get("id") == rid), None)
            except (OSError, ValueError, KeyError):
                return None
        r = find()
        if not r:
            return None, None
        if reel_media_test:
            folder = os.path.join(reel_media_test, key)
            if create:
                os.makedirs(os.path.join(folder, "source"), exist_ok=True)
            return r, (folder if os.path.isdir(folder) else None)
        if create and not r.get("project") and r.get("date"):
            with reel_lock:
                r = find() or r
                if not r.get("project"):
                    out = subprocess.run([sys.executable, p(REELS_SRC + "/reels.py"), "new", rid], cwd=ROOT, capture_output=True, text=True, timeout=120)
                    log({"type": "reel-folder", "reel": rid, "ok": out.returncode == 0, "tail": (out.stdout + out.stderr).strip()[-200:]})
                    r = find() or r
        folder = p(r["project"]) if r.get("project") else None
        if folder and create:
            os.makedirs(os.path.join(folder, "source"), exist_ok=True)
        return r, (folder if folder and os.path.isdir(folder) else None)

    def reel_path(folder, rel):
        """The file rel (source/... or final/...) inside a reel's folder, or None when it points anywhere else."""
        if not folder or not isinstance(rel, str) or not rel.startswith(("source/", "final/")) or "\x00" in rel:
            return None
        full, base = os.path.realpath(os.path.join(folder, rel)), os.path.realpath(folder)
        return full if full.startswith(base + os.sep) else None

    def reel_entry(key, folder, rel):
        st = os.stat(os.path.join(folder, rel))
        return {"name": rel.split("/", 1)[1], "path": rel, "size": st.st_size, "mtime": int(st.st_mtime), "kind": reel_kind(rel),
                "url": "/api/reel-files/raw?reel=" + key + "&f=" + urllib.parse.quote(rel)}

    def reel_listing(key, folder):
        out = {"reel": key, "project": None, "files": [], "finals": []}
        if not folder:
            return out
        out["project"] = os.path.basename(folder) if reel_media_test else os.path.relpath(folder, ROOT)
        src = os.path.join(folder, "source")
        for dp, dns, fns in os.walk(src):
            dns[:] = sorted(x for x in dns if not x.startswith("."))
            for f in fns:
                if not f.startswith(".") and os.path.splitext(f)[1].lower() in REEL_UPLOAD_EXT:
                    out["files"].append(reel_entry(key, folder, os.path.relpath(os.path.join(dp, f), folder)))
        out["files"].sort(key=lambda e: (e["mtime"], e["path"]))
        fin = os.path.join(folder, "final")
        if os.path.isdir(fin):
            out["finals"] = sorted((reel_entry(key, folder, "final/" + f) for f in os.listdir(fin)
                                    if f.lower().endswith(".mp4") and not f.startswith(".")), key=lambda e: -e["mtime"])
        return out
    doc_path = re.compile(r"^(?:(outreach|settings|voice)/([\w.\-]{1,120})|log/([\w.\-]{1,120})/events/([\w.\-]{1,60}))$")

    def state_read(name):
        try:
            with open(os.path.join(state_dir, name + ".json"), encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            return {}

    def state_write(name, obj):
        os.makedirs(state_dir, exist_ok=True)
        dest = os.path.join(state_dir, name + ".json")
        tmp = dest + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, dest)

    hs_port = 8777
    hs_prefix = ("/api/ping", "/api/state", "/api/productions", "/api/production/", "/api/save", "/api/grade",
                 "/api/produce-send", "/api/push-grades", "/api/sync", "/drafts/", "/approved/", "/assets/fonts/",
                 "/pool/", "/grade/", "/productions", "/packs")

    class H(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, *args):
            pass

        def guess_type(self, path):
            # pages written as artifacts (docs/lumebook-social-strategy.html) carry no <meta charset>; without a charset here
            # the browser reads their Hebrew as windows-1252
            t = super().guess_type(path)
            return t + "; charset=utf-8" if t.startswith("text/") or t in ("application/javascript", "application/json") else t

        def _json(self, code, obj):
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _foreign_host(self):
            """DNS rebinding (audit of 08 Nov 2026): a web site whose name points at 127.0.0.1 could read this whole folder
            (.git, creators/correspondence, /api/home) through a page of its own. Its requests carry its own Host header,
            so anything but this server's own name is refused, for every method."""
            if (self.headers.get("Host") or "").strip().lower() in local_hosts:
                return False
            self._json(403, {"error": "local requests only"})
            return True

        def do_HEAD(self):
            if self._foreign_host():
                return
            super().do_HEAD()

        def reel_post(self, u):
            """The reels hub's make sheet: a dropped file in, a dropped file out (to _to-delete), or a reel job (see serve's list)."""
            q = urllib.parse.parse_qs(u.query)
            size = int(self.headers.get("Content-Length") or 0)
            if u.path == "/api/reel-files":
                key, name = (q.get("reel") or [""])[0], (q.get("name") or [""])[0]
                base, ext = os.path.splitext(os.path.basename(name))
                if ext.lower() not in REEL_UPLOAD_EXT:
                    return self._json(415, {"error": "allowed: video, audio, images, pdf", "code": "bad_type"})
                if size <= 0 or size > REEL_UPLOAD_MAX:
                    return self._json(413, {"error": f"a file is 1 byte to {REEL_UPLOAD_MAX // 1024 ** 3} GB", "code": "too_big"})
                r, folder = reel_dir(key, create=True)
                if not r:
                    return self._json(404, {"error": "no such reel", "code": "gone"})
                if not folder:
                    return self._json(500, {"error": "the reel has no media folder", "code": "no_folder"})
                safe = re.sub(r"[^\w.\-]+", "-", base).strip("-.")[:80] or "file"
                src = os.path.join(folder, "source")
                os.makedirs(src, exist_ok=True)
                n = 1
                while True:   # never overwrite: name, name-2, name-3 ... (x mode also covers two drops of one name at once)
                    dest = os.path.join(src, f"{safe}{'' if n == 1 else '-' + str(n)}{ext.lower()}")
                    try:
                        fh = open(dest, "xb")
                        break
                    except FileExistsError:
                        n += 1
                left = size
                with fh:
                    while left:
                        chunk = self.rfile.read(min(left, 1 << 20))
                        if not chunk:
                            break
                        fh.write(chunk)
                        left -= len(chunk)
                if left:
                    os.remove(dest)   # our own half-written copy, not a project file
                    return self._json(400, {"error": "upload interrupted", "code": "failed"})
                rel = os.path.relpath(dest, folder)
                log({"type": "reel-file", "reel": key, "path": rel, "bytes": size})
                return self._json(201, {"file": reel_entry(key, folder, rel),
                                        "project": os.path.basename(folder) if reel_media_test else os.path.relpath(folder, ROOT)})
            if u.path == "/api/reel-files/remove":
                key, rel = (q.get("reel") or [""])[0], (q.get("f") or [""])[0]
                r, folder = reel_dir(key)
                full = reel_path(folder, rel) if r else None
                if not full or not rel.startswith("source/") or not os.path.isfile(full):
                    return self._json(404, {"error": "not found", "code": "gone"})
                top = reel_media_test or ROOT
                where = os.path.relpath(full, top)
                dest = os.path.join(top, "_to-delete", where)
                stem, ext = os.path.splitext(dest)
                n = 2
                while os.path.exists(dest):
                    dest, n = f"{stem}-{n}{ext}", n + 1
                with reel_lock:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.move(full, dest)
                    readme = os.path.join(top, "_to-delete", "README.md")
                    if os.path.exists(readme) or reel_media_test:
                        with open(readme, "a", encoding="utf-8") as fh:
                            fh.write(f"- `{where}`: {datetime.now(IL).strftime('%d %b %Y')}, removed with the ✕ on its tile in reel "
                                     f"{r['id']}'s make sheet in the reels hub (dropped by mistake or replaced). Not in git.\n")
                log({"type": "reel-file-removed", "reel": key, "path": where})
                return self._json(200, {"ok": True, "moved": os.path.relpath(dest, top)})
            # a reel job
            if size <= 0 or size > SAMPLE_MAX:
                return self._json(400, {"error": "bad size", "code": "failed"})
            try:
                doc = json.loads(self.rfile.read(size).decode("utf-8"))
            except ValueError:
                return self._json(400, {"error": "not JSON", "code": "failed"})
            if not isinstance(doc, dict):
                return self._json(400, {"error": "a reel job is a JSON object", "code": "failed"})
            key, ask = str(doc.get("reel") or ""), str(doc.get("prompt") or "")[:8000]
            script = doc.get("script") if isinstance(doc.get("script"), dict) else {}
            r, folder = reel_dir(key)
            if not r:
                return self._json(404, {"error": "no such reel", "code": "gone"})
            files = reel_listing(key, folder)["files"]
            if not files:
                return self._json(400, {"error": "drop the reel's files first", "code": "no_files"})

            def same(a, b):
                return " ".join(str(a or "").split()) == " ".join(str(b or "").split())
            page_vo = [x for x in (script.get("vo") or []) if isinstance(x, str)]
            differs = (script.get("hook") is not None and not same(script.get("hook"), r.get("hook"))) or \
                      (bool(page_vo) and [" ".join(x.split()) for x in page_vo] != [" ".join(str(x).split()) for x in r.get("vo", [])])
            make = {"folder": folder, "rid": r["id"], "merge": bool(differs and not reel_media_test), "test": bool(reel_media_test),
                    "paths": {f["path"] for f in files}, "images": {f["path"] for f in files if f["kind"] == "image"}}
            prompt = reel_plan_prompt(r, folder, files, script, ask)
            meta = {"reel": key, "kind": "make", "label": str(doc.get("label") or "")[:400], "comment": ask[:400]}
            return self._json(*sample_jobs.start(prompt, meta, make=make))

        def send_range(self, full):
            """One file with Range support (a video element asks for pieces to seek); .mov goes out as video/mp4 so Chrome plays it."""
            size = os.path.getsize(full)
            ctype = "video/mp4" if full.lower().endswith((".mov", ".m4v")) else (self.guess_type(full) or "application/octet-stream")
            start, end, code = 0, size - 1, 200
            m = re.fullmatch(r"bytes=(\d*)-(\d*)", (self.headers.get("Range") or "").strip())
            if m and size and (m.group(1) or m.group(2)):
                if m.group(1):
                    start, end = int(m.group(1)), int(m.group(2)) if m.group(2) else size - 1
                else:
                    start = max(0, size - int(m.group(2)))
                end = min(end, size - 1)
                if start > end:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                code = 206
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(max(0, end - start + 1)))
            if code == 206:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.end_headers()
            with open(full, "rb") as fh:
                fh.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = fh.read(min(left, 1 << 20))
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        return
                    left -= len(chunk)

        def hook_studio(self, method):
            """Forward a Carousel Machine request to its own server (the login item); True when this was one."""
            u = urllib.parse.urlparse(self.path)
            if u.path in ("/hook-studio", "/hook-studio/"):
                target = "/" + ("?" + u.query if u.query else "")
                if method == "GET" and self.headers.get("Sec-Fetch-Dest") == "document":
                    try:
                        count_view("hook-studio/")
                    except Exception:
                        pass
            elif u.path.startswith(hs_prefix):
                target = self.path
            else:
                return False
            if method == "POST" and self.headers.get("Origin") not in origins:
                self._json(403, {"error": "same-origin requests only"})
                return True
            body = None
            if method == "POST":
                size = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(size) if 0 < size <= 8 * 1024 * 1024 else b""
            try:
                conn = http.client.HTTPConnection("127.0.0.1", hs_port, timeout=300)
                conn.request(method, target, body=body, headers={"Content-Type": self.headers.get("Content-Type", "application/json")} if body is not None else {})
                r = conn.getresponse()
                data = r.read()
                status, headers = r.status, r.getheaders()
                conn.close()
            except OSError:
                self._json(502, {"error": "Carousel Machine is not running", "start": "python3 carousel/carousel-pipeline/scripts/hook_studio_login.py restart"})
                return True
            ctype = r.getheader("Content-Type", "")
            if ctype.startswith("text/html"):
                data = data.replace(b'href="/" ', b'href="/hook-studio/" ')   # the "Carousel Machine" back link on the review pages
                info = site_editor.resolve(site_editor.proxied_key(u.path)) if status == 200 else None
                if info:
                    try:
                        data = site_editor.inject(data.decode("utf-8"), info).encode("utf-8")
                    except UnicodeDecodeError:
                        pass
            self.send_response(status)
            for k, v in headers:
                if k.lower() in ("content-type", "location", "content-disposition", "last-modified"):
                    if k.lower() == "location" and (v == "/" or v.startswith("/?")):
                        v = "/hook-studio/" + v[1:]
                    self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return True

        def do_GET(self):
            if self._foreign_host():
                return
            if self.hook_studio("GET"):
                return
            if site_editor.handle(self, "GET", port, log):
                return
            path = urllib.parse.urlparse(self.path).path
            if path == "/":   # the front door is the HQ dashboard, not a folder listing (Yarin, 20 Oct 2026)
                self.send_response(302)
                self.send_header("Location", "/sites/dashboard/site/lumebook-dashboard/")
                self.end_headers()
                return
            if path in ("/favicon.ico", "/favicon.png"):   # one tab icon for every page on this server
                data = open(p("shared/brand/logo_square_96.png"), "rb").read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if path == "/api/board/env":
                return self._json(200, {"server": "lumebook", "port": port, "inbox": "media/inbox", "upload_max_mb": UPLOAD_MAX // (1024 * 1024)})
            if path == "/api/local-tools":
                facts = json.load(open(p("shared/facts.json"), encoding="utf-8"))
                out = []
                for t in facts.get("local_tools", {}).get("tools", []):
                    ok = None
                    if t.get("ping"):
                        if urllib.parse.urlparse(t["ping"]).port == port:
                            ok = True  # this server
                        else:
                            try:
                                with urllib.request.urlopen(t["ping"], timeout=2) as r:
                                    ok = r.status == 200
                            except Exception:
                                ok = False
                    out.append({"key": t["key"], "ok": ok, "url": t.get("url")})
                return self._json(200, {"tools": out, "checked_at": now()})
            if path == "/api/creator-map/state":
                with state_lock:
                    return self._json(200, {k: state_read(k) for k in ("outreach", "settings", "voice", "log")})
            if path == "/api/home":
                try:
                    return self._json(200, home_stats())
                except Exception as e:
                    return self._json(500, {"error": f"{type(e).__name__}: {e}"[:300]})
            if path == "/api/hq/layout":
                with state_lock:
                    try:
                        with open(hq_layout, encoding="utf-8") as fh:
                            return self._json(200, json.load(fh))
                    except (FileNotFoundError, ValueError):
                        return self._json(200, {})
            if path == "/api/sample/jobs":
                return self._json(200, {"jobs": sample_jobs.list()})
            if path == "/api/i18n/dict":
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                page, lang = i18n.canon((q.get("page") or [""])[0]), (q.get("lang") or [""])[0]
                if lang not in i18n.LANGS or not page or not site_editor.resolve(page):
                    return self._json(400, {"error": "page and lang (en or he) please"})
                r = i18n.page_rev(page)
                out = {"rev": r, "pending": i18n.pending([i18n.COMMON, page], lang), "worker": i18n_worker.state.get("status")}
                if (q.get("rev") or [""])[0] != r:
                    out["common"], out["page"] = i18n.load(i18n.COMMON)[lang], i18n.load(page)[lang]
                return self._json(200, out)
            if path in ("/api/reel-files", "/api/reel-files/raw"):
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                key = (q.get("reel") or [""])[0]
                r, folder = reel_dir(key)
                if not r:
                    return self._json(404, {"error": "no such reel", "code": "gone"})
                if path == "/api/reel-files":
                    return self._json(200, reel_listing(key, folder))
                full = reel_path(folder, (q.get("f") or [""])[0])
                if not full or not os.path.isfile(full):
                    return self._json(404, {"error": "not found"})
                return self.send_range(full)
            if path == "/api/reels-hub/state":
                with state_lock:
                    try:
                        with open(reels_hub_file, encoding="utf-8") as fh:
                            return self._json(200, json.load(fh))
                    except (FileNotFoundError, ValueError):
                        return self._json(200, {})
            page = site_editor.page_for_url(self, path)
            if page and self.headers.get("Sec-Fetch-Dest") == "document":
                try:
                    count_view(page)
                except Exception:
                    pass
            if page and site_editor.serve_page(self, page):   # the page with the edit button and its saved edits
                return
            return super().do_GET()

        def do_PUT(self):
            if self._foreign_host():
                return
            if site_editor.handle(self, "PUT", port, log):
                return
            u = urllib.parse.urlparse(self.path)
            if u.path == "/api/hq/layout":
                if self.headers.get("Origin") not in origins or self.headers.get("X-LumeBook-Board") != "1":
                    return self._json(403, {"error": "same-origin requests only"})
                size = int(self.headers.get("Content-Length") or 0)
                if size <= 0 or size > 512 * 1024:
                    return self._json(400, {"error": "bad size"})
                try:
                    doc = json.loads(self.rfile.read(size).decode("utf-8"))
                except ValueError:
                    return self._json(400, {"error": "not JSON"})
                if not isinstance(doc, dict) or not isinstance(doc.get("topics"), list):
                    return self._json(400, {"error": "a layout is a JSON object with a topics list"})
                with state_lock:
                    tmp = hq_layout + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as fh:
                        json.dump(doc, fh, ensure_ascii=False, indent=1)
                    os.replace(tmp, hq_layout)
                return self._json(200, {"ok": True})
            if u.path == "/api/reels-hub/doc":
                if self.headers.get("Origin") not in origins or self.headers.get("X-LumeBook-Board") != "1":
                    return self._json(403, {"error": "same-origin requests only"})
                m = reels_hub_doc.match((urllib.parse.parse_qs(u.query).get("path") or [""])[0])
                size = int(self.headers.get("Content-Length") or 0)
                if not m or size <= 0 or size > 256 * 1024:
                    return self._json(400, {"error": "bad path or size"})
                try:
                    doc = json.loads(self.rfile.read(size).decode("utf-8"))
                except ValueError:
                    return self._json(400, {"error": "not JSON"})
                if not isinstance(doc, dict):
                    return self._json(400, {"error": "a document is a JSON object"})
                with state_lock:
                    try:
                        with open(reels_hub_file, encoding="utf-8") as fh:
                            allv = json.load(fh)
                    except (FileNotFoundError, ValueError):
                        allv = {}
                    if not isinstance(allv, dict):
                        allv = {}
                    for k in ("edits", "made", "requests"):
                        if not isinstance(allv.get(k), dict):
                            allv[k] = {}
                    allv[m.group(1)][m.group(2)] = doc
                    out = json.dumps(allv, ensure_ascii=False, indent=1)
                    if len(out.encode("utf-8")) > 8 * 1024 * 1024:
                        return self._json(413, {"error": "the reels hub file is over 8 MB"})
                    tmp = reels_hub_file + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as fh:
                        fh.write(out)
                    os.replace(tmp, reels_hub_file)
                return self._json(200, {"ok": True})
            if u.path != "/api/creator-map/doc":
                return self._json(404, {"error": "not found"})
            if self.headers.get("Origin") not in origins or self.headers.get("X-LumeBook-Board") != "1":
                return self._json(403, {"error": "same-origin requests only"})
            m = doc_path.match((urllib.parse.parse_qs(u.query).get("path") or [""])[0])
            size = int(self.headers.get("Content-Length") or 0)
            if not m or size <= 0 or size > 2 * 1024 * 1024:
                return self._json(400, {"error": "bad path or size"})
            try:
                doc = json.loads(self.rfile.read(size).decode("utf-8"))
            except ValueError:
                return self._json(400, {"error": "not JSON"})
            if not isinstance(doc, dict):
                return self._json(400, {"error": "a document is a JSON object"})
            with state_lock:
                if m.group(1):
                    coll = state_read(m.group(1))
                    coll[m.group(2)] = doc
                    state_write(m.group(1), coll)
                else:
                    lg = state_read("log")
                    lg.setdefault(m.group(3), {})[m.group(4)] = doc
                    state_write("log", lg)
            return self._json(200, {"ok": True})

        def do_POST(self):
            if self._foreign_host():
                return
            if self.hook_studio("POST"):
                return
            u = urllib.parse.urlparse(self.path)
            if u.path == "/api/i18n/missing":   # words a page's dictionaries lack (the language switch, 8 Nov 2026)
                if self.headers.get("Origin") not in origins or self.headers.get("X-LumeBook-Board") != "1":
                    return self._json(403, {"error": "same-origin requests only"})
                size = int(self.headers.get("Content-Length") or 0)
                if size <= 0 or size > 2 * 1024 * 1024:
                    return self._json(400, {"error": "bad size"})
                try:
                    doc = json.loads(self.rfile.read(size).decode("utf-8"))
                except ValueError:
                    return self._json(400, {"error": "not JSON"})
                page = i18n.canon(str(doc.get("page") or "")) if isinstance(doc, dict) else ""
                to, items = (doc.get("to"), doc.get("items")) if isinstance(doc, dict) else (None, None)
                if to not in i18n.LANGS or not page or not site_editor.resolve(page) or not isinstance(items, list) or len(items) > 1000:
                    return self._json(400, {"error": "page, to (en or he) and a list of items please"})
                items = [i for i in items if isinstance(i, dict) and isinstance(i.get("k"), str)]
                new = i18n_worker.report(page, to, items)
                return self._json(200, {"new": new, "pending": i18n.pending([i18n.COMMON, page], to)})
            if u.path == "/api/sample/jobs" or sample_job_act.match(u.path):
                if self.headers.get("Origin") not in origins or self.headers.get("X-LumeBook-Board") != "1":
                    return self._json(403, {"error": "same-origin requests only", "code": "not_granted"})
                m = sample_job_act.match(u.path)
                if m:
                    return self._json(*sample_jobs.act(m.group(1), m.group(2)))
                size = int(self.headers.get("Content-Length") or 0)
                if size <= 0 or size > SAMPLE_MAX:
                    return self._json(400, {"error": "bad size", "code": "failed"})
                try:
                    doc = json.loads(self.rfile.read(size).decode("utf-8"))
                except ValueError:
                    return self._json(400, {"error": "not JSON", "code": "failed"})
                prompt = doc.get("prompt") if isinstance(doc, dict) else None
                if not isinstance(prompt, str) or not prompt.strip():
                    return self._json(400, {"error": "a prompt is a non-empty string", "code": "failed"})
                meta = {k: str(doc.get(k) or "")[:400] for k in ("reel", "kind", "label", "comment")}
                if meta["reel"] and not re.match(r"^[\w.\-]{1,40}$", meta["reel"]):
                    return self._json(400, {"error": "bad reel id", "code": "failed"})
                return self._json(*sample_jobs.start(prompt, meta))
            if u.path in ("/api/reel-files", "/api/reel-files/remove", "/api/reel-make/jobs"):
                if self.headers.get("Origin") not in origins or self.headers.get("X-LumeBook-Board") != "1":
                    return self._json(403, {"error": "same-origin requests only", "code": "not_granted"})
                return self.reel_post(u)
            if u.path == "/api/sample":
                if self.headers.get("Origin") not in origins or self.headers.get("X-LumeBook-Board") != "1":
                    return self._json(403, {"error": "same-origin requests only", "code": "not_granted"})
                size = int(self.headers.get("Content-Length") or 0)
                if size <= 0 or size > SAMPLE_MAX:
                    return self._json(400, {"error": "bad size", "code": "failed"})
                try:
                    doc = json.loads(self.rfile.read(size).decode("utf-8"))
                except ValueError:
                    return self._json(400, {"error": "not JSON", "code": "failed"})
                prompt = doc.get("prompt") if isinstance(doc, dict) else None
                if not isinstance(prompt, str) or not prompt.strip():
                    return self._json(400, {"error": "a prompt is a non-empty string", "code": "failed"})
                if not sample_lock.acquire(blocking=False):
                    return self._json(429, {"error": "one request at a time", "code": "rate_limited"})

                def gone():   # the browser closed the connection (the page's stop button, or the tab)
                    try:
                        ready, _, _ = select.select([self.connection], [], [], 0)
                        return bool(ready) and self.connection.recv(1, socket.MSG_PEEK) == b""
                    except OSError:
                        return True
                try:
                    t0 = datetime.now(IL)
                    status, body = run_sample(prompt, gone)
                finally:
                    sample_lock.release()
                log({"type": "sample", "status": status, "code": body.get("code"), "prompt_chars": len(prompt),
                     "seconds": round((datetime.now(IL) - t0).total_seconds(), 1)})
                try:
                    return self._json(status, body)
                except OSError:   # nobody is listening any more
                    return
            if u.path != "/api/media-inbox":
                return self._json(404, {"error": "not found"})
            if self.headers.get("Origin") not in origins or self.headers.get("X-LumeBook-Board") != "1":
                return self._json(403, {"error": "same-origin board requests only"})
            name = (urllib.parse.parse_qs(u.query).get("name") or [""])[0]
            base, ext = os.path.splitext(os.path.basename(name))
            if ext.lower() not in UPLOAD_EXT:
                return self._json(415, {"error": "allowed: images, video, audio, pdf"})
            size = int(self.headers.get("Content-Length") or 0)
            if size <= 0 or size > UPLOAD_MAX:
                return self._json(413, {"error": f"file must be 1 byte to {UPLOAD_MAX // (1024 * 1024)} MB"})
            safe = re.sub(r"[^\w.\-\u0590-\u05FF]+", "-", base).strip("-.")[:80] or "file"
            day = datetime.now(IL).date().isoformat()
            inbox = p("media/inbox")
            os.makedirs(inbox, exist_ok=True)
            dest, n = os.path.join(inbox, f"{day}-{safe}{ext.lower()}"), 2
            while os.path.exists(dest):
                dest, n = os.path.join(inbox, f"{day}-{safe}-{n}{ext.lower()}"), n + 1
            left = size
            with open(dest, "xb") as f:
                while left:
                    chunk = self.rfile.read(min(left, 1 << 20))
                    if not chunk:
                        break
                    f.write(chunk)
                    left -= len(chunk)
            if left:
                os.remove(dest)
                return self._json(400, {"error": "upload interrupted"})
            log({"type": "media-inbox", "path": os.path.relpath(dest, ROOT), "bytes": size})
            return self._json(201, {"path": os.path.relpath(dest, ROOT)})

    print(f"LumeBook project on http://localhost:{port}/  (HQ: /sites/dashboard/site/lumebook-dashboard/)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=ROOT)).serve_forever()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", default="status", choices=["status", "ripple", "check", "sync", "ack", "map", "build", "deploy", "serve", "edits"])
    ap.add_argument("id", nargs="?")
    ap.add_argument("--published", nargs="?", const="now", help="with ack: artifact republished (now or YYYY-MM-DD)")
    ap.add_argument("--deployed", action="store_true", help="with ack: the live site matches the files on disk now")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--port", type=int, default=8780)
    a = ap.parse_args()
    st = load_state()

    if a.cmd == "serve":
        serve(a.port)
        return
    if a.cmd == "edits":
        if a.id == "bake":
            done = site_editor.bake_all()
            print("baked " + (", ".join(done) if done else "nothing (every edited page already carries its edits)"))
            return
        pages = site_editor.edited_pages()
        for key in pages:
            ops, _ = site_editor.read_ops(key)
            info = site_editor.resolve(key) or {}
            where = info.get("file") or "(no file: applied when the page is shown)"
            print(f"{len(ops):4} edits  {key}  [{info.get('mode', 'off')}]  {where}")
        print(f"-- {len(pages)} edited pages. python3 tools/lumebook.py edits bake writes the edits into their files.")
        return
    if a.cmd == "build":
        if a.id not in COMP or not COMP[a.id].get("build"):
            sys.exit(f"{a.id}: no build in lumebook.json; see: python3 tools/lumebook.py map")
        ok, out = build(a.id)
        print(("built " if ok else "BUILD FAILED ") + a.id + ("" if ok else ": " + out))
        sys.exit(0 if ok else 1)
    if a.cmd == "deploy":
        c = COMP.get(a.id, {})
        dep = c.get("deploy") if c.get("deploy", {}).get("type") == "vercel" else c.get("publish", {})
        if dep.get("type") != "vercel":
            sys.exit(f"{a.id}: nothing to deploy to Vercel (see lumebook.json)")
        if c.get("build"):
            ok, out = build(a.id)
            if not ok:
                sys.exit("build failed: " + out)
        r = subprocess.run(["npx", "--yes", "vercel", "deploy", "--prod", "--yes"], cwd=p(dep["dir"]), text=True)
        log({"type": "deploy", "component": a.id, "ok": r.returncode == 0})
        if r.returncode == 0:
            cs = st["components"].setdefault(a.id, {})
            cs["deployed_hash"], cs["deployed_at"] = digest(a.id)[0], now()
            save_state(st)
        sys.exit(r.returncode)
    if a.cmd == "map":
        for cid, c in COMP.items():
            pub = c.get("publish", {})
            b = c.get("build", {})
            print(f"{cid:20} {c['kind']:9} {c['path']}")
            print(f"{'':20} build: {'auto' if b.get('auto') else 'manual' if b else '-'} · publish: {pub.get('type', '-')} · feeds: {', '.join(c.get('feeds', [])) or '-'}")
        return
    if a.cmd == "sync":
        sync()
        return
    if a.cmd == "check":
        issues = check()
        if a.json:
            print(json.dumps(issues, ensure_ascii=False, indent=1))
        else:
            for i in issues:
                print(f"{i['level']:5} {i['area']:9} {i['msg']}")
            print(f"-- {sum(i['level'] == 'error' for i in issues)} errors, {sum(i['level'] == 'warn' for i in issues)} warnings, {sum(i['level'] == 'info' for i in issues)} info")
        sys.exit(1 if any(i["level"] == "error" for i in issues) else 0)
    if a.cmd == "ack":
        if a.id not in COMP:
            sys.exit(f"unknown component {a.id}; see: python3 tools/lumebook.py map")
        cleared, kept = ack_pending(st, a.id, keep_build_fixes=bool(a.published or a.deployed))
        if a.published:
            cs = st["components"].setdefault(a.id, {})
            cs["published_at"] = now() if a.published == "now" else a.published
            pub = COMP[a.id].get("publish", {})
            if a.published == "now" and pub.get("file") and os.path.exists(p(pub["file"])):
                cs["published_hash"] = md5_file(pub["file"])
            else:
                cs.pop("published_hash", None)
        if a.deployed:
            cs = st["components"].setdefault(a.id, {})
            cs["deployed_hash"], cs["deployed_at"] = digest(a.id)[0], now()
        log({"type": "ack", "component": a.id, "cleared": cleared, "published": a.published})
        save_state(st)
        print(f"{a.id}: cleared {cleared} to-dos" + (f", published_at={st['components'][a.id]['published_at']}" if a.published else ""))
        for it in kept:
            print(f"  still open: {it['action']} (a good build clears it; or: python3 tools/lumebook.py ack {a.id})")
        evaluate(load_state(), False)
        return
    r = evaluate(st, a.cmd == "ripple")
    save_state(st)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print_report(r)


if __name__ == "__main__":
    main()
