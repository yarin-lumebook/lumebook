"""Builds lumebook-parent-communities.html from data.json + page_template.html (LumeBook design system inlined)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # project root (research/<this folder>)
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
import design  # LumeBook design system: tokens, components, theme toggle

data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
page = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
page = (page.replace("<!--LB:HEAD-->", design.head())
            .replace("/*__DATA__*/null", blob))
out = os.path.join(HERE, "lumebook-parent-communities.html")
open(out, "w", encoding="utf-8").write(page)
print("wrote", out, f"{len(page) // 1024} KB")

# the markdown write-up comes from the same data
import runpy
runpy.run_path(os.path.join(HERE, "build_md.py"), run_name="__main__")
