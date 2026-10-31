#!/usr/bin/env python3
"""Build the static (Vercel) copy of the Lumebook dashboard.

Embeds sites/dashboard/out/snapshot.json plus the artifact database exports
(sites/dashboard/out/db/history/*.json, sites/dashboard/out/db/tracker/state.json, written by
ArtifactData list with out_dir) into sites/dashboard/lumebook-dashboard.html, which then
runs read-only with no live connections.

Output: sites/dashboard/site/lumebook-dashboard/index.html (deploy that folder with
`npx vercel deploy --prod --yes`).
"""
import glob, json, os, shutil

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

    page = open(os.path.join(HERE, "lumebook-dashboard.html"), encoding="utf-8").read()
    head, body = page.split('<div class="lb-app"', 1)
    data = json.dumps({"snap": snap, "history": history, "tracker": tracker}, ensure_ascii=False).replace("</", "<\\/")
    doc = (
        '<!doctype html><html lang="he"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
        '<meta name="robots" content="noindex, nofollow">'
        + head + f"<script>window.__DASH__={data};</script></head><body>"
        + '<div class="lb-app"' + body + "</body></html>"
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
    # one design system for the whole site
    os.makedirs(os.path.join(SITE, "design"), exist_ok=True)
    shutil.copy2(os.path.join(ROOT, "shared", "design", "lumebook.css"), os.path.join(SITE, "design", "lumebook.css"))
    shutil.copy2(os.path.join(ROOT, "shared", "design", "categories.css"), os.path.join(SITE, "design", "categories.css"))
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
    with open(os.path.join(SITE, "vercel.json"), "w", encoding="utf-8") as f:
        json.dump({"headers": [{"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]}]}, f, indent=2)
    print(f"built site/lumebook-dashboard/index.html · {len(doc)//1024} KB · {len(history)} history days · tracker {'yes' if tracker else 'empty'}")


if __name__ == "__main__":
    main()
