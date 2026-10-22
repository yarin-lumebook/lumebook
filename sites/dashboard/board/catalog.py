#!/usr/bin/env python3
"""Resource catalog and first board for the dashboard work board.

Reads lumebook.json (components, feeds), shared/facts.json (artifact and site URLs, links, Drive folders, local
tools, key dates), shared/design/categories.json (board areas, workstreams), media/README.md plus media/projects/
(creative jobs), carousel/carousel-pipeline/approved/ (finished carousels), shared/brand/ (brand files) and
content.json next to this file (Hebrew titles, frames, starter cards, prompts, templates).

    python3 sites/dashboard/board/catalog.py          # writes sites/dashboard/board/seed.js
    python3 sites/dashboard/board/catalog.py --json   # prints the catalog

refresh.py puts resources() into the snapshot, so the board sees new resources every morning; build_site.py runs
write_seed() before it copies the board files. Every resource has a stable id ("cmp:creator-map",
"media:2026-10-16-dj-ben-reel"); a board card points at one with `ref` and keeps its own title and notes, so a
refresh updates what the card shows from the source and never renames or moves the card. Standard library only.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, "lumebook.json")) and ROOT != os.path.dirname(ROOT):
    ROOT = os.path.dirname(ROOT)
IL = timezone(timedelta(hours=3))
SEED_JS = os.path.join(HERE, "seed.js")

IMG = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VID = {".mp4", ".mov", ".webm", ".m4v"}
AUD = {".mp3", ".m4a", ".wav", ".ogg", ".opus"}
DOC = {".html": "html", ".pdf": "pdf", ".md": "md"}
SKIP_DIRS = {"source", "sources", "candidates", "analysis", "_cards", "frames", "qc", "annotated", "web", "videos", "transcripts", "__pycache__"}
SKIP_NAME = re.compile(r"(^|[-_])(ref|reference|raw|test|mute|take\d)([-_.]|$)", re.I)

# card size by type (world px); board.js has the same defaults for new cards
# (all multiples of the board's 20px grid, so snapping never nudges a seeded card)
SIZE = {"note": (260, 180), "task": (260, 180), "project": (300, 200), "link": (260, 140), "doc": (260, 140),
        "media": (260, 240), "tool": (260, 160), "prompt": (260, 160), "workflow": (260, 240), "metric": (260, 160),
        "view": (260, 140)}
COL_W, GAP, PAD, HEAD = 260, 20, 40, 80
FRAME_GAP = 120


def rel(p):
    return os.path.join(ROOT, p)


def load(p):
    with open(rel(p), encoding="utf-8") as f:
        return json.load(f)


def mtime(p):
    try:
        return datetime.fromtimestamp(os.path.getmtime(rel(p)), IL).isoformat(timespec="minutes")
    except OSError:
        return None


def media_kind(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in IMG:
        return "image"
    if ext in VID:
        return "video"
    if ext in AUD:
        return "audio"
    return DOC.get(ext)


def dm(iso):
    y, m, d = iso[:10].split("-")
    return f"{int(d)}.{int(m)}"


# ---------- resources ----------

def resources():
    reg = load("lumebook.json")["components"]
    facts = load("shared/facts.json")
    content = load(os.path.relpath(os.path.join(HERE, "content.json"), ROOT))
    cats = load("shared/design/categories.json")["sets"]
    ws_of = {cid: key for key, w in cats["workstreams"]["items"].items() for cid in w.get("components", [])}
    labels = content.get("labels", {})
    art_by_comp = {a["component"]: a for a in facts["artifacts"] if a.get("component")}
    site_by_comp = {}
    for s in facts["sites"]:
        if s.get("component"):
            site_by_comp.setdefault(s["component"], []).append(s)
    out = []

    def add(r):
        lab = labels.get(r["id"], {})
        r.update({k: v for k, v in lab.items() if k in ("title", "summary") and v})
        if lab.get("tags"):
            r["tags"] = lab["tags"]
        r.setdefault("tags", [])
        if r.get("path") and not r.get("modified"):
            r["modified"] = mtime(r["path"])
        out.append({k: v for k, v in r.items() if v not in (None, "", [], {})})

    # components: one resource per registry entry (retired sites and the frozen fal trial stay out)
    # a local tool that names a component stands for it on the board (Carousel Machine is the carousel pipeline)
    tools = {t["component"]: t for t in facts.get("local_tools", {}).get("tools", []) if t.get("component")}
    for cid, c in reg.items():
        if c.get("retired") or cid in ("ambassadors", "fal-trial"):
            continue
        pub, dep = c.get("publish") or {}, c.get("deploy") or {}
        art = art_by_comp.get(cid)
        r = {"id": f"cmp:{cid}", "component": cid, "ws": ws_of.get(cid), "title": (art or {}).get("label") or c["name"],
             "summary": (art or {}).get("summary") or c.get("notes", "")[:180], "date": (art or {}).get("date"),
             "feeds": [f"cmp:{f}" for f in c.get("feeds", []) if f in reg]}
        links = []
        if pub.get("type") in ("artifact", "via", "manual") and pub.get("url"):
            links.append({"label": {"artifact": "ארטיפקט", "via": "באתר", "manual": "עריכה"}[pub["type"]], "url": pub["url"]})
        for s in site_by_comp.get(cid, []):
            if s["url"] not in [x["url"] for x in links]:
                links.append({"label": "אתר", "url": s["url"]})
        if dep.get("url") and dep["url"] not in [x["url"] for x in links]:
            links.append({"label": "Vercel", "url": dep["url"]})
        if links:
            r["url"] = links[0]["url"]
            r["links"] = links
        # the file a person opens: the published page, else the build output, else a single watched file, else the folder
        single = [w for w in c.get("watch", []) if "*" not in w and os.path.isfile(rel(w))]
        src = pub.get("file") or ((c.get("build") or {}).get("outputs") or [None])[0] or (single[0] if len(single) == 1 else None) or c.get("path")
        r["path"] = src
        r["modified"] = mtime(src) if src else None
        if cid in tools:
            t = tools[cid]
            r.update(kind="local-tool", type="tool", url=t["url"], links=[{"label": "בדפדפן", "url": t["url"]}] + links,
                     tool={k: t.get(k) for k in ("key", "url", "ping", "runs_as", "runs_as_he", "status_cmd", "start_cmd")})
        elif pub.get("type") == "artifact":
            r.update(kind="artifact", type="doc")
        elif pub.get("type") in ("via",) or c.get("kind") == "site":
            r.update(kind="site", type="link")
        elif cid == "signup-form":
            r.update(kind="form", type="link", url=facts["links"]["form"],
                     links=[{"label": "הטופס", "url": facts["links"]["form"]}, {"label": "עריכה", "url": facts["links"]["form_edit"]}])
        elif c.get("kind") in ("assets",) or os.path.isdir(rel(src or "")):
            r.update(kind="folder", type="link", local_only=True)
        else:
            r.update(kind="file", type="doc", local_only=not r.get("url"))
        if cid == "sales-readout":
            r["private"] = True
        add(r)

    # artifacts without a component (the 35 reels examples)
    for a in facts["artifacts"]:
        if not a.get("component"):
            add({"id": f"art:{a['key']}", "kind": "artifact", "type": "doc", "title": a["label"], "summary": a.get("summary"),
                 "url": a["url"], "date": a.get("date")})

    # links and Drive folders
    L = facts["links"]
    for key in ("form_edit", "sheet", "drive", "tracker", "monorepo"):
        if L.get(key):
            add({"id": f"link:{key}", "kind": "sheet" if "spreadsheets" in L[key] else "drive" if "drive.google" in L[key] else "link",
                 "type": "link", "title": key, "url": L[key]})
    store = next((s for s in facts["sites"] if s["key"] == "store"), None)
    if store:
        add({"id": "link:store", "kind": "site", "type": "link", "title": store["label"], "url": store["url"]})
    ig = facts["brand"].get("instagram_live") or facts["brand"].get("instagram")
    add({"id": "link:instagram", "kind": "site", "type": "link", "title": f"@{ig}", "url": f"https://www.instagram.com/{ig}/", "tags": ["אינסטגרם"]})
    add({"id": "link:mebook_instagram", "kind": "site", "type": "link", "title": "@" + facts["brand"]["competitor_instagram"],
         "url": f"https://www.instagram.com/{facts['brand']['competitor_instagram']}/", "tags": ["מתחרים"]})
    if facts.get("parent_shoot_offer", {}).get("form_url"):
        add({"id": "link:parent_shoot_form", "kind": "form", "type": "link", "title": "parent shoot form", "url": facts["parent_shoot_offer"]["form_url"]})
    dc = facts.get("drive_content") or {}
    if dc.get("url"):
        add({"id": "drive:content", "kind": "drive", "type": "link", "title": dc["name"], "url": dc["url"]})
    if dc.get("carousels", {}).get("url"):
        add({"id": "drive:carousels", "kind": "drive", "type": "link", "title": dc["carousels"]["name"], "url": dc["carousels"]["url"]})

    # local tools that are not a component (the project server)
    for t in facts.get("local_tools", {}).get("tools", []):
        if t.get("component"):
            continue
        add({"id": f"tool:{t['key']}", "kind": "local-tool", "type": "tool", "title": t["label"], "url": t["url"],
             "tool": {k: t.get(k) for k in ("key", "url", "ping", "runs_as", "runs_as_he", "status_cmd", "start_cmd")}})

    # commands: copied to the clipboard, never run from the browser
    for key, cmd in (("ripple", "python3 tools/lumebook.py ripple"), ("check", "python3 tools/lumebook.py check"),
                     ("status", "python3 tools/lumebook.py status"), ("build-dashboard", "python3 tools/lumebook.py build dashboard")):
        add({"id": f"cmd:{key}", "kind": "command", "type": "tool", "title": key, "command": cmd, "tags": ["פקודה"]})

    # local files and folders worth a card
    for key, path in (("product-brief", "docs/lumebook-product-brief.md"), ("carousel-playbook-he", "docs/lumebook-instagram-carousel-playbook-he.md"),
                      ("ugc-research", "docs/lumebook-ugc-ambassador-research.md"), ("hebrew-voice", "docs/hebrew-voice-tool.md"),
                      ("organic-notes", "research/organic-content-conversion-notes-2026-10-14.md"),
                      ("parent-outreach", "research/parent-community-outreach.md"), ("hebrew-rules", "creators/creator-research/src/hebrew-rules.md")):
        if os.path.exists(rel(path)):
            add({"id": f"file:{key}", "kind": "file", "type": "doc", "title": os.path.basename(path), "path": path, "local_only": True})
    for key, path in (("correspondence", "creators/correspondence"), ("media-inbox", "media/inbox")):
        if os.path.isdir(rel(path)):
            add({"id": f"folder:{key}", "kind": "folder", "type": "link", "title": path, "path": path, "local_only": True})

    # dashboard views and live numbers (the page fills them from the snapshot)
    for key, v in content.get("views", {}).items():
        add({"id": f"view:{key}", "kind": "view", "type": "view", "view": key, "title": v["title"], "summary": v.get("summary")})
    for key, v in content.get("metrics", {}).items():
        add({"id": f"metric:{key}", "kind": "metric", "type": "metric", "metric": key, "title": v["title"], "summary": v.get("summary")})
    for key, v in content.get("prompts", {}).items():
        add({"id": f"prompt:{key}", "kind": "prompt", "type": "prompt", "title": v["title"], "summary": v.get("summary"),
             "prompt": v["text"], "tags": v.get("tags", [])})

    out.extend(media_resources(labels))
    return out


def media_files(folder, limit=12):
    """Previewable files of one job, finals first, references and raw takes last or left out."""
    found = []
    base = rel(folder)
    for dp, dns, fns in os.walk(base):
        depth = os.path.relpath(dp, base).count(os.sep) + (0 if dp == base else 1)
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".") and depth < 2]
        for fn in fns:
            if fn.startswith(".") or not media_kind(fn) or media_kind(fn) == "md":
                continue
            p = os.path.relpath(os.path.join(dp, fn), ROOT)
            score = (0 if "/final/" in p or "final" in fn else 1, 1 if SKIP_NAME.search(fn) else 0,
                     -os.path.getmtime(os.path.join(dp, fn)))
            found.append((score, p))
    found.sort()
    return [p for _, p in found[:limit]]


def media_resources(labels):
    out = []
    readme = rel("media/README.md")
    index = {}
    if os.path.exists(readme):
        for line in open(readme, encoding="utf-8"):
            m = re.match(r"\| `([^`]+)` \| (.*) \| ([^|]*) \| ([^|]*) \|\s*$", line)
            if m:
                index[m.group(1)] = {"summary": m.group(2).strip(), "status": m.group(4).strip()}
    proj = rel("media/projects")
    for name in sorted(os.listdir(proj)) if os.path.isdir(proj) else []:
        path = f"media/projects/{name}"
        if not os.path.isdir(rel(path)) or name.startswith("."):
            continue
        files = media_files(path)
        meta = index.get(name, {})
        first = re.split(r"(?<=[.!?])\s", meta.get("summary", ""), maxsplit=1)[0][:200]
        r = {"id": f"media:{name}", "kind": "media", "type": "media", "title": name[11:].replace("-", " "), "date": name[:10],
             "summary": first or None, "path": path, "local_only": True, "status": meta.get("status") or "unlisted",
             "media": {"kind": media_kind(files[0]) if files else None, "src": files[0] if files else None, "files": files},
             "tags": ["מדיה"], "modified": mtime(path)}
        lab = labels.get(r["id"], {})
        r.update({k: v for k, v in lab.items() if k in ("title", "summary") and v})
        out.append({k: v for k, v in r.items() if v not in (None, "", [], {})})

    # finished carousels (Carousel Machine production runs), newest four
    appr = rel("carousel/carousel-pipeline/approved")
    runs = sorted((d for d in os.listdir(appr) if re.match(r"\d{4}-\d{2}-\d{2}-", d) and os.path.isdir(os.path.join(appr, d, "final"))), reverse=True) if os.path.isdir(appr) else []
    for run in runs[:4]:
        path = f"carousel/carousel-pipeline/approved/{run}"
        fin = os.path.join(appr, run, "final")
        slides = sorted(f"{path}/final/{f}" for f in os.listdir(fin) if re.match(r"\d\d\.(png|jpg)$", f))
        sheet = f"{path}/final/contact-sheet.png" if os.path.exists(os.path.join(fin, "contact-sheet.png")) else None
        cap = ""
        if os.path.exists(os.path.join(fin, "caption.txt")):
            cap = open(os.path.join(fin, "caption.txt"), encoding="utf-8").read().strip().splitlines()[0][:160]
        files = ([sheet] if sheet else []) + slides
        out.append({"id": f"carousel:{run}", "kind": "media", "type": "media", "title": f"קרוסלה {dm(run)} · {run[11:]}", "date": run[:10],
                    "summary": cap or None, "path": f"{path}/final", "local_only": True, "tags": ["קרוסלות", "מוכן"],
                    "media": {"kind": "image" if files else None, "src": files[0] if files else None, "files": files[:12]},
                    "modified": mtime(f"{path}/final")})

    # brand files (a published copy, such as the dashboard's img/logo.png, previews everywhere)
    copies = {c["from"]: c["to"] for c in load("lumebook.json")["components"]["brand"].get("copies", [])}
    bdir = rel("shared/brand")
    for dp, dns, fns in os.walk(bdir):
        dns[:] = [d for d in dns if d != "fonts" and not d.startswith(".")]
        for fn in sorted(fns):
            if media_kind(fn) != "image" or fn.startswith("."):
                continue
            p = os.path.relpath(os.path.join(dp, fn), ROOT)
            key = os.path.relpath(p, "shared/brand")
            r = {"id": f"brand:{key}", "kind": "media", "type": "media", "title": key, "path": p, "local_only": True,
                 "media": {"kind": "image", "src": p, "files": [p]}, "tags": ["מותג"], "modified": mtime(p)}
            if copies.get(p, "").startswith("sites/dashboard/img/"):
                r["media"]["published"] = copies[p][len("sites/dashboard/"):]
            lab = labels.get(r["id"], {})
            r.update({k: v for k, v in lab.items() if k in ("title", "summary") and v})
            out.append(r)
    return out


# ---------- the first board ----------

def seed(res):
    content = load(os.path.relpath(os.path.join(HERE, "content.json"), ROOT))
    facts = load("shared/facts.json")
    areas = load("shared/design/categories.json")["sets"]["board-areas"]["items"]
    by_id = {r["id"]: r for r in res}
    dates = " · ".join(f"{d['label']} {dm(d['date'])}{' (לא מאושר)' if d.get('unconfirmed') else ''}"
                       for d in facts.get("key_dates", []) if "חנוכה" in d["label"])
    frames, cards, placed = [], [], {}
    rows = {}
    for fr in content["frames"]:
        items = []
        for it in fr["items"]:
            if it == "carousel:*":
                items += [r["id"] for r in res if r["id"].startswith("carousel:")][:2]
            elif it.startswith("card:") or it in by_id:
                items.append(it)
            else:
                print(f"catalog: frame {fr['key']} lists {it}, which is not in the catalog (left out)", file=sys.stderr)
        rows.setdefault(fr["row"], []).append((fr, items))

    y = 0
    for row in sorted(rows):
        x_right = 0
        row_h = 0
        for fr, items in rows[row]:
            cols = fr["cols"]
            w = PAD * 2 + cols * COL_W + (cols - 1) * GAP
            # lay the cards out in reading order: right to left, then down
            grid, line, line_h, cy = [], [], 0, HEAD
            for i, it in enumerate(items):
                sc = content["starter_cards"].get(it[5:], {}) if it.startswith("card:") else {}
                ctype = sc.get("type") if sc else by_id[it]["type"]
                cw, ch = sc.get("w", SIZE[ctype][0]), sc.get("h", SIZE[ctype][1])
                line.append((it, ctype, cw, ch))
                line_h = max(line_h, ch)
                if len(line) == cols or i == len(items) - 1:
                    for c, (iid, t, cw2, ch2) in enumerate(line):
                        grid.append((iid, t, w - PAD - (c + 1) * COL_W - c * GAP, cy, cw2, ch2))
                    cy += line_h + GAP
                    line, line_h = [], 0
            h = cy - GAP + PAD
            fx = x_right - w
            frames.append({"id": f"f-{fr['key']}", "title": areas[fr["key"]]["label"], "area": fr["key"], "x": fx, "y": y, "w": w, "h": h})
            for iid, t, cx, cy2, cw, ch in grid:
                card = {"x": fx + cx, "y": y + cy2, "w": cw, "h": ch, "type": t}
                if iid.startswith("card:"):
                    sc = dict(content["starter_cards"][iid[5:]])
                    card["id"] = f"s-card-{iid[5:]}"
                    card.update({k: v for k, v in sc.items() if k != "type"})
                    if "desc" in card:
                        card["desc"] = card["desc"].replace("{dates}", dates + "." if dates else "")
                    if sc.get("steps"):
                        card["checklist"] = [{"id": f"st{n}", "text": s, "done": False} for n, s in enumerate(sc["steps"])]
                        card.pop("steps", None)
                else:
                    r = by_id[iid]
                    card["id"] = "s-" + re.sub(r"[^A-Za-z0-9_-]", "-", iid)
                    card["ref"] = iid
                    card["title"] = r["title"]
                    card["tags"] = list(r.get("tags", []))
                    if r.get("prompt"):
                        card["prompt"] = r["prompt"]
                cards.append(card)
                placed[iid] = card["id"]
            x_right = fx - FRAME_GAP
            row_h = max(row_h, h)
        y += row_h + FRAME_GAP

    # registry dependencies drawn on the first board: only between cards in the same area. A line across the whole
    # board (facts to the creator map, brand to the pipeline) reads as clutter, and the design system and the dashboard
    # feed or read nearly everything; the card panel lists every registry relation either way.
    frame_of = {}
    for fr in frames:
        for card in cards:
            cx, cy = card["x"] + card["w"] / 2, card["y"] + card["h"] / 2
            if fr["x"] <= cx <= fr["x"] + fr["w"] and fr["y"] <= cy <= fr["y"] + fr["h"]:
                frame_of[card["id"]] = fr["id"]
    edges = []
    for r in res:
        if r["id"] not in placed or r["id"] in ("cmp:design", "cmp:dashboard"):
            continue
        for f in r.get("feeds", []):
            if f in placed and f != "cmp:dashboard" and frame_of.get(placed[r["id"]]) == frame_of.get(placed[f]):
                edges.append({"id": f"e-dep-{placed[r['id']][2:]}-{placed[f][2:]}", "from": placed[r["id"]], "to": placed[f],
                              "kind": "dep", "label": "מזין"})
    daily = next(f for f in frames if f["area"] == "daily")
    return {"frames": frames, "cards": cards, "edges": edges,
            "home": {"x": daily["x"] - 40, "y": daily["y"] - 40, "w": daily["w"] + 80, "h": daily["h"] + 80},
            "dock": [d for d in content.get("dock", []) if d in by_id],
            "known": [r["id"] for r in res]}


def templates():
    content = load(os.path.relpath(os.path.join(HERE, "content.json"), ROOT))
    facts = load("shared/facts.json")
    dc = facts.get("drive_content") or {}
    subst = {"{drive_content}": dc.get("url", ""), "{drive_carousels}": dc.get("carousels", {}).get("url", "")}
    out = []
    for t in content.get("templates", []):
        t = json.loads(json.dumps(t, ensure_ascii=False))
        for c in t["cards"]:
            if c.get("url") in subst:
                c["url"] = subst[c["url"]]
        out.append(t)
    return out


def build():
    res = resources()
    areas = load("shared/design/categories.json")["sets"]["board-areas"]["items"]
    return {"generated_at": datetime.now(IL).isoformat(timespec="seconds"), "schema": 1,
            "areas": {k: {"label": v["label"], "cat": v["cat"]} for k, v in areas.items()},
            "resources": res, "seed": seed(res), "templates": templates()}


def write_seed():
    """Write seed.js when the catalog, layout or templates changed (not for a new timestamp or file mtimes), so the
    published artifact file and the dashboard's watch list only change when something real did."""
    data = build()
    for r in data["resources"]:
        r.pop("modified", None)
    if os.path.exists(SEED_JS):
        try:
            old = open(SEED_JS, encoding="utf-8").read()
            prev = json.loads(old[old.index("=") + 1:].rstrip().rstrip(";"))
            if {k: v for k, v in prev.items() if k != "generated_at"} == {k: v for k, v in data.items() if k != "generated_at"}:
                return prev
        except (ValueError, OSError):
            pass
    text = ("/* Generated by sites/dashboard/board/catalog.py from lumebook.json, shared/facts.json, media/, shared/brand/ and\n"
            "   board/content.json. Do not edit: change those and run python3 sites/dashboard/board/catalog.py. */\n"
            "window.LB_SEED = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n")
    with open(SEED_JS, "w", encoding="utf-8") as f:
        f.write(text)
    return data


if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps(build(), ensure_ascii=False, indent=1))
    else:
        d = write_seed()
        print(f"seed.js · {len(d['resources'])} resources · {len(d['seed']['cards'])} cards in {len(d['seed']['frames'])} frames · "
              f"{len(d['seed']['edges'])} dependency edges · {len(d['templates'])} templates · {os.path.getsize(SEED_JS) // 1024} KB")
