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


def auto_clear(st):
    keep = []
    for it in st["pending"]:
        out = it.get("clears_with")
        if out and mtime_iso(out) and mtime_iso(out) > it["since"]:
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
                  "sites/lumebook-smm-plan/index.html", "creators/lumebook-ugc-form.gs",
                  "sites/lumebook-ambassadors/apps-script-form.gs"]
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
             "_to-delete"}
SCAN_EXT = {".py", ".sh", ".md", ".json", ".html", ".js", ".gs", ".css"}


def scan_text_files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SCAN_SKIP]
        for fn in fns:
            if os.path.splitext(fn)[1] in SCAN_EXT:
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

    # SMM plan: Hebrew page edited after its English mirror
    he, en = mtime_iso("sites/lumebook-smm-plan/index.html"), mtime_iso("sites/lumebook-smm-plan/content.en.md")
    if he and en and he > en:
        add("info", "smm-plan", "index.html is newer than content.en.md; mirror the Hebrew change before committing")
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
                # the 08:14 scheduled task rebuilds it from everything upstream; one to-do that clears itself
                add_pending(st, cid, "refresh the dashboard snapshot (the 08:14 task does this)", why, clears_with="sites/dashboard/out/snapshot.json")
                continue
            # a design-system or brand change restyles every page built on it: rebuild those too
            styled = any(u in ("design", "brand") for u in ups)
            if b and b.get("auto") and (own or styled):
                ok, err = build(cid)
                (report["built"] if ok else report["build_failed"]).append(cid)
                if not ok:
                    add_pending(st, cid, "fix build: " + " ".join(b["cmd"]), err or why)
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
      GET  /api/hq/layout       HQ's tools layout as Yarin arranged it (sites/dashboard/hq-layout.json; {} when never saved)
      PUT  /api/hq/layout       saves it (same-origin only, one JSON object, at most 512 KB); edit mode of HQ, 5 Nov 2026
      GET  /                    redirects to the HQ dashboard
      /hook-studio/             Carousel Machine (the login item on 127.0.0.1:8777) through this server: its own paths
                                (HS_PREFIX) are forwarded as they are, POSTs same-origin only; nothing of it runs here
      /__site-editor/           the edit button: every HTML page (and every forwarded Carousel Machine page) is sent with
                                the button, the edits runtime and the page's saved edits; GET info/source, PUT save/upload
                                (same-origin, X-Site-Editor header). tools/site_editor.py, shared/site-editor/README.md
    There is no endpoint that runs a command."""
    import http.client, http.server, functools, urllib.parse, urllib.request, threading
    origins = {f"http://localhost:{port}", f"http://127.0.0.1:{port}"}
    state_dir = p("creators/creator-research/state")
    state_lock = threading.Lock()
    hq_layout = p("sites/dashboard/hq-layout.json")
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

        def hook_studio(self, method):
            """Forward a Carousel Machine request to its own server (the login item); True when this was one."""
            u = urllib.parse.urlparse(self.path)
            if u.path in ("/hook-studio", "/hook-studio/"):
                target = "/" + ("?" + u.query if u.query else "")
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
            if path == "/api/hq/layout":
                with state_lock:
                    try:
                        with open(hq_layout, encoding="utf-8") as fh:
                            return self._json(200, json.load(fh))
                    except (FileNotFoundError, ValueError):
                        return self._json(200, {})
            page = site_editor.page_for_url(self, path)
            if page and site_editor.serve_page(self, page):   # the page with the edit button and its saved edits
                return
            return super().do_GET()

        def do_PUT(self):
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
            if self.hook_studio("POST"):
                return
            u = urllib.parse.urlparse(self.path)
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
        before = len(st["pending"])
        st["pending"] = [it for it in st["pending"] if it["component"] != a.id]
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
        log({"type": "ack", "component": a.id, "cleared": before - len(st["pending"]), "published": a.published})
        save_state(st)
        print(f"{a.id}: cleared {before - len(st['pending'])} to-dos" + (f", published_at={st['components'][a.id]['published_at']}" if a.published else ""))
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
