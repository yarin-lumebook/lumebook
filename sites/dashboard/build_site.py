#!/usr/bin/env python3
"""Build the static (Vercel) copy of the Lumebook dashboard.

Embeds sites/dashboard/out/snapshot.json plus the artifact database exports
(sites/dashboard/out/db/history/*.json, sites/dashboard/out/db/tracker/state.json, written by
ArtifactData list with out_dir) into sites/dashboard/lumebook-dashboard.html, which then
runs read-only with no live connections.

Output: sites/dashboard/site/lumebook-dashboard/index.html (deploy that folder with
`npx vercel deploy --prod --yes`). Also copies the SMM plan to /plan/ and the research pages that
have a `web` address on this site in shared/facts.json to /research/<slug>/ (since 05 Nov 2026).
"""
import glob, json, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, "lumebook.json")) and ROOT != os.path.dirname(ROOT):
    ROOT = os.path.dirname(ROOT)
OUT = os.path.join(HERE, "out")
SITE = os.path.join(HERE, "site", "lumebook-dashboard")


def load(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def main():
    snap = load(os.path.join(OUT, "snapshot.json"))
    if not snap:
        raise SystemExit("no sites/dashboard/out/snapshot.json; run refresh.py first")
    history = [h for h in (load(p) for p in sorted(glob.glob(os.path.join(OUT, "db", "history", "*.json")))) if h]
    today = load(os.path.join(OUT, "history.json"))
    if today and not any(h.get("date") == today.get("date") for h in history):
        history.append(today)
    history.sort(key=lambda h: h.get("date", ""))
    tracker = load(os.path.join(OUT, "db", "tracker", "state.json"), {})
    # the research library and the tool cubes open these copies on Vercel: take the addresses from facts.json now,
    # so a page added there shows up without waiting for the next refresh.py
    webs = {a["key"]: a["web"] for a in research_copies()}
    for a in snap.get("artifacts", []):
        a["web"] = webs.get(a.get("key"))

    page = open(os.path.join(HERE, "lumebook-dashboard.html"), encoding="utf-8").read()
    head, body = page.split('<div class="lb-app', 1)   # the app shell (lb-app, with no-sidebar since 5 Nov 2026)
    data = json.dumps({"snap": snap, "history": history, "tracker": tracker}, ensure_ascii=False).replace("</", "<\\/")
    doc = (
        '<!doctype html><html lang="he"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
        '<meta name="robots" content="noindex, nofollow">'
        + head + f"<script>window.__DASH__={data};</script></head><body>"
        + '<div class="lb-app' + body + "</body></html>"
    )
    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    shutil.copytree(os.path.join(HERE, "img"), os.path.join(SITE, "img"), dirs_exist_ok=True)
    # tasks and lessons (the default view since 31 Oct 2026): engine, styles and the lesson data. course-data.js is
    # the course component's output (python3 course/build.py, run by ripple), so building here never changes a
    # tracked file. Only the lesson content ships; Yarin's tasks, quiz answers and numbers live in the artifact
    # database (course/*) or that browser's localStorage, and nothing here exports them
    os.makedirs(os.path.join(SITE, "course"), exist_ok=True)
    for name in ("course.js", "course.css", "course-data.js"):
        shutil.copy2(os.path.join(HERE, "course", name), os.path.join(SITE, "course", name))
    # HQ's saved tools layout (edit mode on the project server writes it, 5 Nov 2026); the copy reads it, never writes it
    if os.path.exists(os.path.join(HERE, "hq-layout.json")):
        shutil.copy2(os.path.join(HERE, "hq-layout.json"), os.path.join(SITE, "hq-layout.json"))
    # one design system for the whole site
    os.makedirs(os.path.join(SITE, "design"), exist_ok=True)
    shutil.copy2(os.path.join(ROOT, "shared", "design", "lumebook.css"), os.path.join(SITE, "design", "lumebook.css"))
    shutil.copy2(os.path.join(ROOT, "shared", "design", "categories.css"), os.path.join(SITE, "design", "categories.css"))
    shutil.copy2(os.path.join(ROOT, "shared", "design", "icons.js"), os.path.join(SITE, "design", "icons.js"))   # the icon set (5 Nov 2026)
    shutil.copy2(os.path.join(ROOT, "shared", "design", "nav.js"), os.path.join(SITE, "design", "nav.js"))   # the project nav (5 Nov 2026)
    # the full SMM plan lives inside this site at /plan/ (its own Vercel project was retired on 8 Oct 2026)
    plan_src, plan_dst = os.path.join(ROOT, "sites", "lumebook-smm-plan"), os.path.join(SITE, "plan")
    shutil.rmtree(plan_dst, ignore_errors=True)
    shutil.copytree(plan_src, plan_dst, ignore=shutil.ignore_patterns(".*", "*.md", "__pycache__"))
    plan_html = os.path.join(plan_dst, "index.html")
    with open(plan_html, encoding="utf-8") as f:
        ph = f.read()
    if 'name="robots"' not in ph:
        ph = ph.replace("<head>", '<head>\n<meta name="robots" content="noindex, nofollow">', 1)
    with open(plan_html, "w", encoding="utf-8") as f:
        f.write(ph)
    research = copy_research()
    with open(os.path.join(SITE, "vercel.json"), "w", encoding="utf-8") as f:
        json.dump({"headers": [{"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]}]}, f, indent=2)
    print(f"built site/lumebook-dashboard/index.html · {len(doc)//1024} KB · {len(history)} history days · tracker {'yes' if tracker else 'empty'}")
    for path, kb, n in research:
        print(f"  research copy /{path}/ · {kb} KB" + (f" · {n} linked files" if n else ""))


def research_copies():
    """The facts.json artifacts whose `web` address is on this site (Yarin, 05 Nov 2026: research pages on Vercel).

    Only pages without internal sales figures or personal data get a `web` entry. The reels research, the reels
    system, the creator-content report, CRO/CRM, the sales readout, the carousel audit and the creator map have none."""
    facts = load(os.path.join(ROOT, "shared", "facts.json"), {})
    base = next(s["url"] for s in facts.get("sites", []) if s.get("key") == "dash").rstrip("/") + "/"
    return [dict(a, rel=a["web"][len(base):].strip("/")) for a in facts.get("artifacts", [])
            if (a.get("web") or "").startswith(base + "research/")]


def copy_research():
    """Copy each research page (its built publish.file) to research/<slug>/index.html, with the files it links."""
    reg = load(os.path.join(ROOT, "lumebook.json"), {})
    comps = reg.get("components", reg)
    shutil.rmtree(os.path.join(SITE, "research"), ignore_errors=True)
    out = []
    for a in research_copies():
        rel = a["rel"]
        src =(comps.get(a.get("component") or "", {}).get("publish") or {}).get("file")
        if not src or not os.path.exists(os.path.join(ROOT, src)):
            raise SystemExit(f"{a['key']}: no built page for {a['web']} (lumebook.json {a.get('component')}.publish.file)")
        dst = os.path.join(SITE, rel)
        os.makedirs(dst, exist_ok=True)
        with open(os.path.join(ROOT, src), encoding="utf-8") as f:
            html = f.read()
        # static files the page links by a relative path (carousel research: img2/*.jpg); JS templates are skipped
        src_dir, n = os.path.dirname(os.path.join(ROOT, src)), 0
        for ref in sorted(set(re.findall(r'(?:src|href)="([^"#?:$\'+{}<>\s]+)"', html))):
            ref_path = os.path.normpath(ref)
            if ref_path.startswith("..") or not os.path.isfile(os.path.join(src_dir, ref_path)):
                continue
            os.makedirs(os.path.dirname(os.path.join(dst, ref_path)), exist_ok=True)
            shutil.copy2(os.path.join(src_dir, ref_path), os.path.join(dst, ref_path))
            n += 1
        # artifact pages are fragments: give them a doctype (no quirks mode) and keep them out of search engines
        if not html.lstrip().lower().startswith("<!doctype"):
            html = "<!doctype html>\n" + html
        if 'name="robots"' not in html:
            html = html.replace("<!doctype html>\n", '<!doctype html>\n<meta name="robots" content="noindex, nofollow">\n', 1)
        with open(os.path.join(dst, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        out.append((rel, len(html.encode()) // 1024, n))
    return out


if __name__ == "__main__":
    main()
