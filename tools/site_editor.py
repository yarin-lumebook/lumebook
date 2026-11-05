"""The edit button on every page the project server shows (shared/site-editor/README.md).

tools/lumebook.py serve uses this module to
  - add the edit button (loader.js), the edits runtime (overlay.js) and the page's saved edits to every HTML page it
    serves, and to the Carousel Machine pages it forwards;
  - answer the editor under /__site-editor/ (info, source, save, upload, and the three scripts);
  - bake: write a page's edits into its own file (the lumebook-edits block before </body>), so the artifact and Vercel
    copies show them too. build() bakes a component's outputs after every build and ripple bakes every edited page,
    so edits survive rebuilds.

Two modes per page (shared/site-editor/pages.json):
  source  hand-written pages: what the file holds is edited in the file itself (as the site-editor skill does);
  layer   every other page: nothing of the file is rewritten, every change is an operation in
          shared/site-editor/edits/<page>.json that overlay.js applies whenever the page shows.
Standard library only.
"""
import fnmatch, hashlib, html, json, os, re, tempfile, threading, urllib.parse
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "shared", "site-editor")
EDITS = os.path.join(DIR, "edits")
BACKUP = os.path.join(ROOT, ".site-editor", "backup")      # the version each source-mode save replaced (gitignored)
INBOX = os.path.join(ROOT, "media", "inbox")               # pictures added with the editor (media/README.md: unsorted files)
API = "/__site-editor/"
SCRIPTS = ("overlay.js", "loader.js", "editor.js")
PAGE_EXT = (".html", ".htm")
OP_TYPES = {"html", "style", "attr", "hide", "show", "move", "insert", "tag", "css"}
MAX_SAVE = 30 * 1024 * 1024
MAX_PICTURE = 25 * 1024 * 1024
PICTURES = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp", "image/avif": "avif", "image/svg+xml": "svg"}
BLOCK = re.compile(r"<!-- lumebook-edits:start.*?<!-- lumebook-edits:end -->\n?", re.S)
IL = timezone(timedelta(hours=2))
LOCK = threading.Lock()
_cache = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()[:16]


def _rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _cached_json(path, default):
    try:
        m = os.path.getmtime(path)
    except OSError:
        return default
    hit = _cache.get(path)
    if hit and hit[0] == m:
        return hit[1]
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        data = default
    _cache[path] = (m, data)
    return data


def config():
    return _cached_json(os.path.join(DIR, "pages.json"), {})


def built_pages():
    """Page -> the component whose build writes it (lumebook.json build.outputs)."""
    reg = _cached_json(os.path.join(ROOT, "lumebook.json"), {})
    out = {}
    for cid, c in (reg.get("components") or {}).items():
        for o in (c.get("build") or {}).get("outputs", []):
            if o.lower().endswith(PAGE_EXT):
                out[o] = cid
    return out


def _match(rel, patterns):
    for pat in patterns or []:
        if rel == pat or (pat.endswith("/") and rel.startswith(pat)) or fnmatch.fnmatchcase(rel, pat):
            return True
    return False


def _inside(base, path):
    path = os.path.normpath(path)
    return path == base or path.startswith(base + os.sep)


def resolve(rel):
    """What the edit button does on a page: {key, file, mode, note}; None where it is off.

    rel is the page's path in the project (sites/x/index.html), or hook-studio/... for a Carousel Machine page."""
    rel = (rel or "").lstrip("/")
    if not rel or ".." in rel.split("/"):
        return None
    c = config()
    if _match(rel, c.get("off")):
        return None
    key = rel
    for src, to in (c.get("alias") or {}).items():
        if rel == src or (src.endswith("/") and rel.startswith(src)):
            key = to + rel[len(src):] if src.endswith("/") else to
            break
    file = None
    if not key.startswith("hook-studio/") and _inside(ROOT, os.path.join(ROOT, key)) and os.path.isfile(os.path.join(ROOT, key)):
        file = key
    mode = "source" if file and _match(key, c.get("source")) else "layer"
    note = next((v for k, v in (c.get("notes") or {}).items() if _match(key, [k])), "")
    built = built_pages().get(key)
    if not note and built:
        note = f"This page is built by a script (component {built} in lumebook.json). Your edits are kept apart from it and applied again after every rebuild."
    return {"key": key, "file": file, "mode": mode, "note": note}


# ---------- the edits of one page ----------

def ops_path(key):
    path = os.path.normpath(os.path.join(EDITS, key + ".json"))
    if not _inside(EDITS, path):
        raise ValueError("bad page key")
    return path


def read_ops(key):
    """(operations, version) of a page; version 'none' when it has never been edited."""
    try:
        with open(ops_path(key), "rb") as fh:
            raw = fh.read()
    except (FileNotFoundError, ValueError):
        return [], "none"
    try:
        ops = json.loads(raw.decode("utf-8")).get("ops") or []
    except ValueError:
        ops = []
    return ops, sha(raw)


def _write(path, data, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".site-editor-")
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)
    os.chmod(tmp, mode if mode is not None else 0o644)
    os.replace(tmp, path)


def write_ops(key, ops):
    head = {
        "_about": "Edits made with the edit button on this page (shared/site-editor/README.md). overlay.js applies them; "
                  "tools/lumebook.py writes them into the page's file. Change them only through the editor.",
        "page": key,
        "updated": datetime.now(IL).isoformat(timespec="seconds"),
    }
    # one edit per line, so a git diff shows which edits came or went
    lines = [f" {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}," for k, v in head.items()]
    body = ",\n".join("  " + json.dumps(o, ensure_ascii=False, separators=(",", ":")) for o in ops)
    raw = ("{\n" + "\n".join(lines) + '\n "ops": [' + ("\n" + body + "\n ]" if ops else "]") + "\n}\n").encode("utf-8")
    json.loads(raw.decode("utf-8"))   # never write a file the editor can't read back
    _write(ops_path(key), raw)
    return sha(raw)


# ---------- the lumebook-edits block inside a page's file ----------

def strip(text):
    return BLOCK.sub("", text)


def _at_body_end(text, chunk):
    i = text.lower().rfind("</body")
    if i < 0:
        return text + ("" if text.endswith("\n") else "\n") + chunk
    return text[:i] + chunk + text[i:]


def _data(key, ops):
    # "<" never appears outside strings in JSON, so escaping it keeps </script> and <!-- out of the page safely
    return json.dumps({"page": key, "ops": ops}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def block(key, ops):
    with open(os.path.join(DIR, "overlay.js"), encoding="utf-8") as fh:
        runtime = fh.read().replace("</script", "<\\/script")
    return (f"<!-- lumebook-edits:start · edits made with the edit button, kept in shared/site-editor/edits/{key}.json; "
            f"tools/lumebook.py writes this block again after every build, never edit it by hand -->\n"
            f'<script type="application/json" id="lumebook-edits">{_data(key, ops)}</script>\n'
            f'<script id="lumebook-edits-runtime">\n{runtime}</script>\n'
            "<!-- lumebook-edits:end -->\n")


def baked(text, key, ops):
    t = strip(text)
    return _at_body_end(t, block(key, ops)) if ops else t


def bake(key):
    """Write a page's edits into its file (or take the block out when it has none). True when the file changed."""
    info = resolve(key)
    if not info or not info["file"]:
        return False
    path = os.path.join(ROOT, info["file"])
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    ops, _ = read_ops(info["key"])
    if not ops and "lumebook-edits:start" not in text:
        return False
    new = baked(text, info["key"], ops)
    if new == text:
        return False
    _write(path, new.encode("utf-8"), os.stat(path).st_mode & 0o777)
    return True


def edited_pages():
    out = []
    for dirpath, _, files in os.walk(EDITS):
        for f in files:
            if f.endswith(".json") and not f.startswith("."):
                out.append(_rel(os.path.join(dirpath, f))[len("shared/site-editor/edits/"):-len(".json")])
    return sorted(out)


def bake_all():
    """Bake every edited page: the step that puts edits back after a page was rebuilt outside tools/lumebook.py."""
    return [k for k in edited_pages() if bake(k)]


def bake_outputs(outputs):
    """After a build: the outputs that have edits get them written back in."""
    keys = set(edited_pages())
    return [o for o in outputs if o in keys and bake(o)]


# ---------- serving ----------

def inject(text, info):
    """The page as the project server shows it: its file without the baked block, plus the current edits, the runtime and the button."""
    key = info["key"]
    ops, _ = read_ops(key)
    a = lambda v: html.escape(v or "", quote=True)
    tags = (f'<script type="application/json" id="lumebook-edits">{_data(key, ops)}</script>\n'
            f'<script src="{API}overlay.js"></script>\n'
            f'<script src="{API}loader.js" data-page="{a(key)}" data-mode="{a(info["mode"])}" data-file="{a(info["file"] or key)}" data-note="{a(info["note"])}"></script>\n')
    return _at_body_end(strip(text), tags)


def page_for_url(handler, url_path):
    """The project file an URL shows (folders give their index.html), as a path relative to the project, or None."""
    path = os.path.realpath(handler.translate_path(url_path))
    if not _inside(ROOT, path):
        return None
    if os.path.isdir(path):
        if not url_path.endswith("/"):
            return None   # the base class redirects /dir to /dir/
        for name in ("index.html", "index.htm"):
            if os.path.isfile(os.path.join(path, name)):
                return _rel(os.path.join(path, name))
        return None
    if os.path.isfile(path) and path.lower().endswith(PAGE_EXT):
        return _rel(path)
    return None


def serve_page(handler, rel):
    """Send a project page with the edit button; False when the page isn't one for the button (the caller serves the plain file)."""
    info = resolve(rel)
    if not info:
        return False
    try:
        with open(os.path.join(ROOT, rel), "rb") as fh:
            text = fh.read().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    _send(handler, 200, inject(text, info).encode("utf-8"), "text/html; charset=utf-8")
    return True


def proxied_key(url_path):
    """The edits key of a Carousel Machine page shown through /hook-studio/."""
    path = url_path.split("?")[0]
    if path in ("/hook-studio", "/hook-studio/"):
        return "hook-studio/app"
    return "hook-studio" + path.rstrip("/")


def _send(handler, code, body, ctype, extra=None):
    handler.send_response(code)
    handler.send_header("Content-Type", ctype)
    handler.send_header("Content-Length", str(len(body)))
    for k, v in (extra or {}).items():
        handler.send_header(k, v)
    handler.end_headers()
    handler.wfile.write(body)


def _json(handler, code, obj):
    _send(handler, code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")


def _from_editor(handler, port):
    hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    if handler.headers.get("Host", "") not in hosts:
        return False   # DNS rebinding
    origin = handler.headers.get("Origin")
    if origin and origin not in {f"http://{h}" for h in hosts}:
        return False
    return handler.headers.get("X-Site-Editor") == "1"   # a custom header forces a CORS preflight, which is never approved


def _looks_like(data, ext):
    if ext == "jpg":
        return data[:3] == b"\xff\xd8\xff"
    if ext == "png":
        return data[:8] == b"\x89PNG\r\n\x1a\n"
    if ext == "gif":
        return data[:6] in (b"GIF87a", b"GIF89a")
    if ext == "webp":
        return data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    if ext == "avif":
        return data[4:12] in (b"ftypavif", b"ftypavis")
    return ext == "svg" and "<svg" in data[:4096].decode("utf-8", "ignore").lower()


def handle(handler, method, port, log=None):
    """Answer /__site-editor/ requests. True when the request was one of them."""
    u = urllib.parse.urlsplit(handler.path)
    path = urllib.parse.unquote(u.path)
    if not path.startswith(API):
        return False
    name = path[len(API):]
    if method == "GET" and name in SCRIPTS:
        with open(os.path.join(DIR, name), "rb") as fh:
            _send(handler, 200, fh.read(), "text/javascript; charset=utf-8")
        return True
    if not _from_editor(handler, port):
        _json(handler, 403, {"ok": False, "error": "forbidden"})
        return True
    info = resolve((urllib.parse.parse_qs(u.query).get("page") or [""])[0])
    if not info:
        _json(handler, 404, {"ok": False, "error": "no such page"})
        return True
    key, file = info["key"], info["file"]
    fpath = os.path.join(ROOT, file) if file else None

    if method == "GET" and name == "info":
        ops, ov = read_ops(key)
        version = None
        if fpath:
            with open(fpath, "rb") as fh:
                version = sha(fh.read())
        _json(handler, 200, {"ok": True, "key": key, "file": file, "mode": info["mode"], "note": info["note"], "version": version, "ops": ops, "opsVersion": ov})
        return True

    if method == "GET" and name == "source":
        if info["mode"] != "source":
            _json(handler, 400, {"ok": False, "error": "this page is edited as a layer"})
            return True
        with open(fpath, "rb") as fh:
            raw = fh.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            _json(handler, 400, {"ok": False, "error": "encoding"})
            return True
        _send(handler, 200, strip(text).encode("utf-8"), "text/plain; charset=utf-8", {"X-Version": sha(raw)})
        return True

    if method == "PUT" and name == "save":
        size = int(handler.headers.get("Content-Length") or 0)
        if size <= 0 or size > MAX_SAVE:
            _json(handler, 413, {"ok": False, "error": "size"})
            return True
        try:
            doc = json.loads(handler.rfile.read(size).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            _json(handler, 400, {"ok": False, "error": "not JSON"})
            return True
        ops = doc.get("ops")
        if not isinstance(ops, list) or not all(isinstance(o, dict) and o.get("t") in OP_TYPES for o in ops):
            _json(handler, 400, {"ok": False, "error": "ops must be a list of edit operations"})
            return True
        page_html = doc.get("html")
        with LOCK:
            _, ov = read_ops(key)
            if handler.headers.get("X-Ops-Version", "") != ov:
                _json(handler, 409, {"ok": False, "error": "edits changed", "opsVersion": ov})
                return True
            if page_html is not None:
                if info["mode"] != "source" or not isinstance(page_html, str):
                    _json(handler, 400, {"ok": False, "error": "this page is edited as a layer"})
                    return True
                low = page_html.lower()
                if "<html" not in low and "<body" not in low:
                    _json(handler, 400, {"ok": False, "error": "not a full HTML page"})
                    return True
                with open(fpath, "rb") as fh:
                    current = fh.read()
                if handler.headers.get("X-Base-Version", "") != sha(current):
                    _json(handler, 409, {"ok": False, "error": "changed on disk", "version": sha(current)})
                    return True
                if strip(current.decode("utf-8")) != page_html:
                    _write(os.path.join(BACKUP, file), current)
                    _write(fpath, baked(page_html, key, ops).encode("utf-8"), os.stat(fpath).st_mode & 0o777)
                    if log:
                        log({"type": "site-editor", "page": key, "saved": "file"})
            old_ops, _ = read_ops(key)
            if ops != old_ops:
                ov = write_ops(key, ops)
                if log:
                    log({"type": "site-editor", "page": key, "saved": "edits", "ops": len(ops)})
            if fpath:
                bake(key)
                with open(fpath, "rb") as fh:
                    version = sha(fh.read())
            else:
                version = None
        _json(handler, 200, {"ok": True, "version": version, "opsVersion": ov})
        return True

    if method == "PUT" and name == "upload":
        ctype = (handler.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        ext = PICTURES.get(ctype)
        size = int(handler.headers.get("Content-Length") or 0)
        if not ext:
            _json(handler, 415, {"ok": False, "error": "unsupported picture type"})
            return True
        if size <= 0 or size > MAX_PICTURE:
            _json(handler, 413, {"ok": False, "error": "size"})
            return True
        data = handler.rfile.read(size)
        if not _looks_like(data, ext):
            _json(handler, 400, {"ok": False, "error": "file content doesn't match its type"})
            return True
        base = os.path.splitext(os.path.basename((urllib.parse.parse_qs(u.query).get("name") or ["picture"])[0]))[0]
        slug = re.sub(r"[^\w\-֐-׿]+", "-", base).strip("-.").lower()[:40] or "picture"
        day = datetime.now(IL).date().isoformat()
        dest = os.path.join(INBOX, f"{day}-{slug}-{hashlib.sha256(data).hexdigest()[:8]}.{ext}")
        if not os.path.exists(dest):
            _write(dest, data)
            if log:
                log({"type": "media-inbox", "path": _rel(dest), "bytes": size, "from": "site-editor", "page": key})
        src = os.path.relpath(dest, os.path.dirname(fpath)).replace(os.sep, "/") if fpath else "/" + _rel(dest)
        _json(handler, 200, {"ok": True, "path": src})
        return True

    _json(handler, 404, {"ok": False, "error": "not found"})
    return True
