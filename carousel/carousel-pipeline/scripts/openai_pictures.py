#!/usr/bin/env python3
"""The OpenAI Images API for Carousel Machine: client, cost estimate and the 4:5 crop (03 Nov 2026).

Yarin, 03 Nov 2026: "disconnect carousel machine from any other image generation tool, i want it to use the gpt api from
now on". This is the only place a carousel picture is made; fal.ai and ChatGPT in Chrome are retired (_to-delete/).

    python3 openai_pictures.py config            # model, size, quality, rates and the assumptions behind the estimate

Nothing here spends anything unless OpenAIImages.generate or .edit is called, and only openai_generate.py calls them,
after a budget the person approved. OPENAI_API_KEY is read from the environment (macOS Keychain "openai-api-key", exported
by ~/.zshrc; run through `zsh -ic`) and never written to disk, a log or an error message.
"""

import base64
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lib as lib  # noqa: E402

CONFIG = lib.PIPELINE / "scripts" / "openai_models.json"
API = "https://api.openai.com/v1/images"
TIMEOUT = 600
MODES = ("generate", "edit")
INPUT_KEYS = {"prompt", "size", "quality", "n"}
_KEY_RE = re.compile(r"sk-[A-Za-z0-9_\-]{6,}")


def config():
    return lib.read_json(CONFIG)


def saved_size(cfg=None):
    s = (cfg or config())["saved_size"]
    return s["width"], s["height"]


# ---------------------------------------------------------------- jobs and estimates

def base_input(cfg=None):
    """The settings every job carries (jobs.json "input"), minus the prompt."""
    cfg = cfg or config()
    return {"size": cfg["size"], "quality": cfg["quality"], "n": 1}


def job_issues(name, job, cfg=None):
    """Problems with one job against the model snapshot (openai_models.json). Makes no network call."""
    cfg = cfg or config()
    problems = []
    if job.get("mode") not in MODES:
        return [f"{name}: mode {job.get('mode')!r} is not one of {MODES}"]
    if job.get("model") != cfg["model"]:
        problems.append(f"{name}: model {job.get('model')!r} is not {cfg['model']}")
    inp = job.get("input") or {}
    for key in inp:
        if key not in INPUT_KEYS:
            problems.append(f"{name}: {key} is not an accepted input")
    if inp.get("quality") not in cfg["allowed_qualities"]:
        problems.append(f"{name}: quality {inp.get('quality')} is not allowed, only {cfg['allowed_qualities']} was measured")
    if inp.get("size") != cfg["size"]:
        problems.append(f"{name}: size {inp.get('size')} is not {cfg['size']}")
    if inp.get("n", 1) != 1:
        problems.append(f"{name}: n must be 1")
    prompt = inp.get("prompt", "")
    if not prompt.strip() or len(prompt) > cfg["prompt_max_chars"]:
        problems.append(f"{name}: prompt length {len(prompt)}")
    refs = job.get("refs") or []
    if job["mode"] == "edit" and not refs:
        problems.append(f"{name}: an edit needs a reference picture")
    if job["mode"] == "generate" and refs:
        problems.append(f"{name}: a text-to-image job has no reference picture")
    if len(refs) > cfg["max_reference_images"]:
        problems.append(f"{name}: too many reference images")
    return problems


def estimate_job(job, cfg=None):
    """The estimated tokens and dollars of one job, before any call. Deliberately on the high side (see openai_models.json)."""
    cfg = cfg or config()
    est, rates = cfg["estimate"], cfg["rates_usd_per_million_tokens"]
    text_in = math.ceil(len((job.get("input") or {}).get("prompt", "")) / est["prompt_chars_per_token"])
    image_in = est["reference_image_tokens"] * len(job.get("refs") or [])
    out = est["output_tokens_per_image"][(job.get("input") or {}).get("quality") or cfg["quality"]]
    usd = (text_in * rates["text_in"] + image_in * rates["image_in"] + out * rates["image_out"]) / 1e6
    return {"input_text_tokens": text_in, "input_image_tokens": image_in, "output_tokens": out, "usd": round(usd, 4)}


def estimate_total(jobs, names=None, cfg=None):
    """Sum of estimate_job over some jobs of a jobs.json dict (all of them by default)."""
    cfg = cfg or config()
    names = list(names if names is not None else jobs["jobs"])
    parts = [estimate_job(jobs["jobs"][n], cfg) for n in names]
    return {"images": len(parts), "input_text_tokens": sum(p["input_text_tokens"] for p in parts),
            "input_image_tokens": sum(p["input_image_tokens"] for p in parts),
            "output_tokens": sum(p["output_tokens"] for p in parts),
            "total_tokens": sum(p["input_text_tokens"] + p["input_image_tokens"] + p["output_tokens"] for p in parts),
            "usd": round(sum(p["usd"] for p in parts), 4)}


def usage_cost(usage, cfg=None):
    """The real dollars of one finished call, from the usage block OpenAI returned."""
    cfg = cfg or config()
    rates = cfg["rates_usd_per_million_tokens"]
    usage = usage or {}
    details = usage.get("input_tokens_details") or {}
    image_in = int(details.get("image_tokens") or 0)
    text_in = int(details.get("text_tokens") if details.get("text_tokens") is not None else (usage.get("input_tokens") or 0) - image_in)
    out = int(usage.get("output_tokens") or 0)
    return round((text_in * rates["text_in"] + image_in * rates["image_in"] + out * rates["image_out"]) / 1e6, 5)


# ---------------------------------------------------------------- the API

class ApiError(RuntimeError):
    """A failed call. billed is False when OpenAI answered with an error status (nothing was generated), True when the
    outcome is unknown (a timeout or a dropped connection), so the runner counts it as spent to stay under the budget."""

    def __init__(self, message, status=None, billed=False, code=None):
        super().__init__(message)
        self.status, self.billed, self.code = status, billed, code


def scrub(text):
    return _KEY_RE.sub("[key]", str(text))


def _multipart(fields, files):
    boundary = uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for field, name, data in files:
        out.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{name}"\r\n'
                   "Content-Type: image/png\r\n\r\n".encode() + data + b"\r\n")
    out.append(f"--{boundary}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={boundary}"


class OpenAIImages:
    def __init__(self, key=None):
        self.key = key or os.environ.get("OPENAI_API_KEY", "")
        if not self.key:
            raise SystemExit("OPENAI_API_KEY is not set in this shell. Run through zsh -ic so ~/.zshrc loads it from the Keychain.")

    def _call(self, url, body, content_type):
        req = urllib.request.Request(url, body, {"Authorization": "Bearer " + self.key, "Content-Type": content_type}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.headers.get("x-request-id", ""), json.load(resp)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            try:
                err = json.loads(raw).get("error") or {}
            except ValueError:
                err = {}
            raise ApiError(scrub(f"OpenAI HTTP {exc.code}: {err.get('code') or ''} {err.get('message') or raw[:300]}".strip()),
                           status=exc.code, billed=False, code=err.get("code")) from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ApiError(scrub(f"OpenAI call did not finish ({exc}); counted as spent because the outcome is unknown"), billed=True) from None

    def _result(self, rid, data):
        items = data.get("data") or []
        if not items or not items[0].get("b64_json"):
            raise ApiError("OpenAI answered without an image", billed=True)
        return rid, base64.b64decode(items[0]["b64_json"]), data.get("usage") or {}

    def generate(self, job, cfg=None):
        """Text to image. Returns (request id, PNG bytes, usage)."""
        cfg = cfg or config()
        inp = job["input"]
        body = json.dumps({"model": job["model"], "prompt": inp["prompt"], "size": inp["size"], "quality": inp["quality"], "n": 1}).encode()
        return self._result(*self._call(API + "/generations", body, "application/json"))

    def edit(self, job, ref_paths, cfg=None):
        """The reference picture(s) plus a prompt, to a new picture. Returns (request id, PNG bytes, usage)."""
        cfg = cfg or config()
        inp = job["input"]
        fields = {"model": job["model"], "prompt": inp["prompt"], "size": inp["size"], "quality": inp["quality"], "n": "1"}
        files = [("image[]", Path(p).name, Path(p).read_bytes()) for p in ref_paths]
        body, ctype = _multipart(fields, files)
        return self._result(*self._call(API + "/edits", body, ctype))


# ---------------------------------------------------------------- the 4:5 crop

def _size_sips(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)], capture_output=True, text=True, timeout=60).stdout
    vals = {k.strip(): v.strip() for k, _, v in (l.partition(":") for l in out.splitlines()) if k.strip() in ("pixelWidth", "pixelHeight")}
    return int(vals["pixelWidth"]), int(vals["pixelHeight"])


def crop_box(w, h, ratio=0.8):
    """The centred 4:5 area of a w x h picture, as (width, height)."""
    if w / h > ratio:
        return round(h * ratio), h
    return w, round(w / ratio)


def normalize(src, dst, size=None):
    """src picture -> dst PNG: the centred 4:5 crop at 1024 x 1280. Pillow when present, else macOS sips."""
    src, dst = Path(src), Path(dst)
    size = size or saved_size()
    ratio = size[0] / size[1]
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if Image is not None:
        with Image.open(src) as im:
            im = im.convert("RGB")
            cw, ch = crop_box(*im.size, ratio)
            left, top = (im.width - cw) // 2, (im.height - ch) // 2
            im.crop((left, top, left + cw, top + ch)).resize(size, Image.LANCZOS).save(dst, "PNG")
        return
    if not shutil.which("sips"):
        raise SystemExit("cannot convert the picture: neither Pillow nor macOS sips is available")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work.png"
        run = lambda *a: subprocess.run(["sips", *a], capture_output=True, text=True, timeout=120, check=True)  # noqa: E731
        run("-s", "format", "png", str(src), "--out", str(work))
        cw, ch = crop_box(*_size_sips(work), ratio)
        run("-c", str(ch), str(cw), str(work))          # sips crops around the centre
        run("-z", str(size[1]), str(size[0]), str(work))
        shutil.move(str(work), str(dst))


def main():
    cfg = config()
    print(json.dumps({k: v for k, v in cfg.items() if not k.startswith("_")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
