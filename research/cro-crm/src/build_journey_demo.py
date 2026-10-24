#!/usr/bin/env python3
"""Build the fixed-journey walkthrough demo.

    python3 research/cro-crm/src/build_journey_demo.py

Input:  research/cro-crm/src/journey-demo.template.html (the layout and the ten phone screens, as code)
        research/cro-crm/src/journey-demo.json (every word of the story: steps, notes and their evidence, glossary;
        edit it, then rebuild, never edit the built HTML)
        shared/design/categories.json, set journey-stages (the stage colours)
        media/projects/2026-10-24-cro-crm-actions/ (the iPhone frame and the covers from lumebook.com; not in git, so a
        missing picture is left out: no frame gives a bare screen, no cover an empty square)
Output: research/cro-crm/journey-demo.html, one self-contained page on the LumeBook design system (design.head()
        inlined, white and black modes, pictures as data: URIs) that opens straight from disk.
        Local only, not published: it shows internal sales figures and imitates the store's own screens.

Nothing in the demo is generated or uploaded: photos and customer pages are placeholders, the payment step has no
card fields. Standard library only.
"""
import base64
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIR = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

SRC = HERE / "journey-demo.template.html"
DATA = HERE / "journey-demo.json"
MEDIA = ROOT / "media" / "projects" / "2026-10-24-cro-crm-actions"
OUT = DIR / "journey-demo.html"


def img(match):
    path = MEDIA / match.group(1)
    if not path.exists():
        print(f"  missing picture, left out: {path.relative_to(ROOT)}")
        return ""
    return "data:image/webp;base64," + base64.b64encode(path.read_bytes()).decode()


def as_js(obj):
    # JSON is valid JavaScript; keep "</" from closing the script tag
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def build():
    page = SRC.read_text(encoding="utf-8")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    data.pop("_about", None)
    page = (page.replace("<!--LB:HEAD-->", design.head())
                .replace("<!--LB:THEME-TOGGLE-->", design.theme_toggle(dark_label="מצב כהה"))
                .replace("{{LOGO}}", design.logo_data_uri())
                .replace("{{MASCOT}}", design.logo_data_uri("mascot_3d_transparent_320.png"))
                .replace("{{DEMO_JSON}}", as_js(data))
                .replace("{{STAGES_JSON}}", as_js(design.categories("journey-stages"))))
    page = re.sub(r"\{\{IMG:([\w.-]+)\}\}", img, page)
    if "—" in page:
        raise SystemExit("em dash in the demo; fix the template or journey-demo.json")
    if "לומיבוק" in page:
        raise SystemExit("banned brand spelling in the demo; use לומבוק")
    left = re.findall(r"<!--LB:[A-Z-]+-->|\{\{(?:LOGO|MASCOT|DEMO_JSON|STAGES_JSON|IMG:[^}]*)\}\}", page)
    if left:
        raise SystemExit(f"unreplaced placeholders: {left}")
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page) // 1024} KB, {len(data['steps'])} steps, "
          f"{sum(len(s['notes']) for s in data['steps'])} notes)")


if __name__ == "__main__":
    build()
