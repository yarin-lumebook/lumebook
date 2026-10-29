"""Download every carousel slide from src/posts.json into slides/<code>/NN.jpg and build sheets/<code>.jpg."""
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "media/projects/2026-10-29-lotem-lerner-carousels")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15"

posts = [p for p in json.load(open(os.path.join(HERE, "posts.json"))) if p["type"] == 8]
posts.sort(key=lambda p: p["taken"])

def get(job):
    url, path = job
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", path, url])
    return path

def sheet(code, files):
    # 4 per row, 540px tall tiles: big enough to read Hebrew slide text
    ims = [Image.open(f).convert("RGB") for f in files]
    H = 540
    ims = [im.resize((int(im.width * H / im.height), H)) for im in ims]
    cols = 4
    for part in range(0, len(ims), 8):
        chunk = ims[part:part + 8]
        rows = (len(chunk) + cols - 1) // cols
        W = max(sum(im.width for im in chunk[r * cols:(r + 1) * cols]) for r in range(rows))
        S = Image.new("RGB", (W, H * rows), "white")
        for r in range(rows):
            x = 0
            for im in chunk[r * cols:(r + 1) * cols]:
                S.paste(im, (x, r * H)); x += im.width
        S.save(os.path.join(ROOT, "sheets", f"{code}_{part // 8 + 1}.jpg"), quality=85)

os.makedirs(os.path.join(ROOT, "sheets"), exist_ok=True)
for i, p in enumerate(posts, 1):
    d = os.path.join(ROOT, "slides", p["code"])
    os.makedirs(d, exist_ok=True)
    jobs = [(s["u"], os.path.join(d, f"{n:02d}.jpg")) for n, s in enumerate(p["slides"], 1)]
    with ThreadPoolExecutor(6) as ex:
        files = list(ex.map(get, jobs))
    sheet(p["code"], files)
    print(f"PROGRESS {i}/{len(posts)} {p['code']}", flush=True)
