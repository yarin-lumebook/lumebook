#!/usr/bin/env python3
"""Hebrew and English on every internal page (Yarin, 08 Nov 2026: "i want the entire project in hebrew and english with a
toggle that appears everywhere to switch between them").

How it works
- The switch (עב | EN) sits at the top of the project nav on every internal page (shared/design/i18n.src.js, which
  design.py bundles into nav.js). The choice is kept in the browser (localStorage "lb-lang"); until it is used, a page
  shows the language it was written in. Once it is set, every page shows that language: Hebrew pages turn English and
  left to right, English pages turn Hebrew and right to left, and the English bits of a Hebrew page turn Hebrew.
- Words are swapped in place from dictionaries, never in the page's source: shared/i18n/common.json (the nav, the
  controls, words many pages share) and shared/i18n/pages/<page path>.json (one per page, keyed like the edit button's
  edits). Each holds "en" (Hebrew -> English) and "he" (English -> Hebrew). A key is the text of one block of the page
  (a paragraph, a button, a cell), its pieces joined by U+001F where bold or a link splits it, numbers written {0} {1}.
- Never translated: fields, editable text, code, the edit button, and anything inside translate="no" or the classes in
  i18n.src.js SKIP (Hebrew copy written for parents, such as carousel slides, reel scripts and messages to creators,
  stays Hebrew in both languages). The edit button switches the page back to its own language while it is open, so an
  edit never saves a translation into the page.
- New words: on the project server (:8780) a page reports what its dictionaries lack (POST /api/i18n/missing); a
  background worker here translates them through `claude -p` (no tools, no files, the Claude login of this Mac, never
  an API key, like /api/sample) and the page picks them up (GET /api/i18n/dict) a few seconds later. Elsewhere (claude.ai
  artifacts, Vercel) a page shows what its own baked copy has.
- Bake: a page's file carries its dictionaries (the lumebook-i18n block before </body>) so the artifact and Vercel copies
  switch too. tools/lumebook.py writes it after every build and in ripple, the nightly job runs bake_all().

CLI
  python3 tools/i18n.py status                 dictionaries per page and what is waiting
  python3 tools/i18n.py translate [--page KEY] translate what is waiting, here (PROGRESS lines for the progress bar)
  python3 tools/i18n.py check                  lint the dictionaries (placeholders, dashes, לומיבוק)
  python3 tools/i18n.py bake [KEY ...]         write the dictionary block into page files

Test on a spare port: LUMEBOOK_I18N_DIR points at scratch dictionaries, LUMEBOOK_I18N_QUEUE at a scratch queue file,
LUMEBOOK_CLAUDE at a stand-in command.
"""
import argparse, json, os, re, shutil, signal, subprocess, sys, tempfile, threading, time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.environ.get("LUMEBOOK_I18N_DIR") or os.path.join(ROOT, "shared", "i18n")
COMMON = "common"
QUEUE = os.environ.get("LUMEBOOK_I18N_QUEUE") or os.path.join(ROOT, ".lumebook", "i18n-queue.json")
SEP = "\u001f"
LANGS = ("en", "he")
HE = re.compile(r"[֐-׿]")
LAT = re.compile(r"[A-Za-z]")
PH = re.compile(r"\{\d+\}")
BLOCK = re.compile(r"<!-- lumebook-i18n:start.*?<!-- lumebook-i18n:end -->\n?", re.S)
# one dictionary for a page that is shown under two names
ALIAS = {"hook-studio/app": "carousel/carousel-pipeline/hook-studio.html"}
MODEL = os.environ.get("LUMEBOOK_I18N_MODEL", "sonnet")
BATCH_ITEMS = 60          # blocks per claude call
BATCH_CHARS = 5000        # source characters per claude call
PARALLEL = 3              # claude calls at the same time
TIMEOUT = 420             # seconds before a claude call is stopped
MAX_TRIES = 3             # a block that fails this often is dropped from the queue (and reported again when seen)
KEY_MAX = 4000
_io = threading.RLock()   # every read-modify-write of a dictionary or the queue


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def canon(key):
    key = (key or "").lstrip("/")
    return ALIAS.get(key, key)


def dict_path(scope):
    if scope == COMMON:
        return os.path.join(DIR, "common.json")
    path = os.path.normpath(os.path.join(DIR, "pages", canon(scope) + ".json"))
    if not path.startswith(os.path.join(DIR, "pages") + os.sep):
        raise ValueError("bad page key")
    return path


def needs(text, to):
    """Does this text need translating into `to`? Hebrew letters for English; Latin words and no Hebrew for Hebrew."""
    if to == "en":
        return bool(HE.search(text))
    return not HE.search(text) and bool(re.search(r"[A-Za-z]{2}", text))


def load(scope):
    """{"en": {...}, "he": {...}} for a scope (missing file: empty)."""
    try:
        with open(dict_path(scope), encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        d = {}
    return {l: d.get(l) if isinstance(d.get(l), dict) else {} for l in LANGS}


def rev(scope):
    try:
        return os.stat(dict_path(scope)).st_mtime_ns
    except (OSError, ValueError):
        return 0


def save(scope, d):
    """Write a dictionary: one entry per line, sorted, so a git diff shows which words came or went."""
    path = dict_path(scope)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    head = {"_about": "Translations for the language switch (tools/i18n.py, shared/i18n/README.md): 'en' is Hebrew to English, "
                      "'he' is English to Hebrew. Keys are the page's own text, pieces split by U+001F, numbers as {0}. "
                      "Filled by the project server and tools/i18n.py translate; fix a wrong one here, then run tools/i18n.py bake.",
            "page": scope, "updated": now()}
    out = ["{"] + [f" {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}," for k, v in head.items()]
    for i, l in enumerate(LANGS):
        items = sorted((d.get(l) or {}).items())
        body = ",\n".join(f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}" for k, v in items)
        out.append(f' "{l}": {{' + ("\n" + body + "\n }" if items else "}") + ("," if i < len(LANGS) - 1 else ""))
    out.append("}")
    raw = "\n".join(out) + "\n"
    json.loads(raw)   # never write a file the pages can't read back
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(raw)
    os.replace(tmp, path)


def merge(scope, to, entries):
    with _io:
        d = load(scope)
        d[to].update(entries)
        save(scope, d)


def scopes():
    """Every scope that has a dictionary file: common plus the page keys."""
    out = []
    if os.path.isfile(dict_path(COMMON)):
        out.append(COMMON)
    base = os.path.join(DIR, "pages")
    for dp, _, files in os.walk(base):
        for f in files:
            if f.endswith(".json"):
                out.append(os.path.relpath(os.path.join(dp, f), base)[:-5].replace(os.sep, "/"))
    return sorted(out)


# ---------- the queue of words to translate ----------

def _qload():
    try:
        with open(QUEUE, encoding="utf-8") as fh:
            q = json.load(fh)
        return q if isinstance(q, dict) and isinstance(q.get("items"), list) else {"items": []}
    except (OSError, ValueError):
        return {"items": []}


def _qsave(q):
    os.makedirs(os.path.dirname(QUEUE), exist_ok=True)
    tmp = QUEUE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(q, fh, ensure_ascii=False, indent=0)
    os.replace(tmp, QUEUE)


def valid_key(k, to):
    if not isinstance(k, str) or not k.strip() or len(k) > KEY_MAX or k.count(SEP) > 40:
        return False
    return needs(k, to)


def enqueue(scope, to, keys):
    """Add keys the dictionaries lack; returns how many were new."""
    scope = canon(scope)
    with _io:
        have = load(scope)[to]
        q = _qload()
        seen = {(i["scope"], i["to"], i["k"]) for i in q["items"]}
        n = 0
        for k in keys:
            if k in have or (scope, to, k) in seen or not valid_key(k, to):
                continue
            q["items"].append({"scope": scope, "to": to, "k": k, "tries": 0, "at": int(time.time())})
            seen.add((scope, to, k))
            n += 1
        if n:
            _qsave(q)
        return n


def pending(scope_list=None, to=None):
    with _io:
        items = _qload()["items"]
    wanted = {canon(s) for s in scope_list} if scope_list else None
    return sum(1 for i in items if (wanted is None or i["scope"] in wanted) and (to is None or i["to"] == to))


def take_batch(busy, prefer=None):
    """The next batch to translate: items of one scope and direction not already being translated."""
    with _io:
        items = [i for i in _qload()["items"] if (i["scope"], i["to"], i["k"]) not in busy]
    if not items:
        return None, None, []
    if prefer:
        pick = [i for i in items if i["scope"] in prefer] or items
    else:
        pick = items
    head = max(pick, key=lambda i: i.get("at", 0)) if prefer else pick[0]   # the page being looked at now goes first
    scope, to = head["scope"], head["to"]
    batch, chars = [], 0
    for i in items:
        if i["scope"] != scope or i["to"] != to:
            continue
        if batch and (len(batch) >= BATCH_ITEMS or chars + len(i["k"]) > BATCH_CHARS):
            break
        batch.append(i["k"])
        chars += len(i["k"])
    return scope, to, batch


def finish(scope, to, keys, done):
    """Store what came back; count a try for what didn't, drop what failed MAX_TRIES times. Returns (stored, dropped)."""
    with _io:
        if done:
            merge(scope, to, done)
        q = _qload()
        keep, dropped, ks = [], 0, set(keys)
        for i in q["items"]:
            if i["scope"] == scope and i["to"] == to and i["k"] in ks:
                if i["k"] in done:
                    continue
                i["tries"] = i.get("tries", 0) + 1
                if i["tries"] >= MAX_TRIES:
                    dropped += 1
                    continue
            keep.append(i)
        q["items"] = keep
        _qsave(q)
    return len(done), dropped


# ---------- translating through claude -p ----------

RULES = {
    "en": """Translate each item from Hebrew to English.
- Plain, short, everyday English. Keep the length close to the original; labels and buttons stay short.
- Hebrew used as a quoted example of copy for Israeli parents (a carousel slide line, a hook, a caption, a message) is
  translated too, as a faithful English rendering.
- לומבוק is LumeBook.""",
    "he": """Translate each item from English to Hebrew.
- Everyday Israeli Hebrew, terse and clear, the way a young Israeli marketer writes his own work notes. Not formal, not translated-sounding.
- Instructions and buttons in the infinitive or as nouns (לשמור, לפתוח, שמירה), never addressed to a man or a woman.
- Keep the loanwords Israelis use in English letters: UTM, UGC, CTA, KPI, SEO, HQ, Q4, AI, API, CSV, URL. Reel is ריל (רילס), carousel is קרוסלה, story is סטורי, post is פוסט, feed is פיד, hook is הוק, creator is יוצר or יוצרת.
- A prefix letter before a Latin word or a number takes a hyphen: ב-Instagram, ל-25%, מ-HQ. The definite article joins ל ב כ: לספר, not להספר.
- LumeBook stays LumeBook in English letters; in Hebrew words it is לומבוק, never לומיבוק.""",
}

PROMPT = """You translate the words of LumeBook's internal web pages. LumeBook sells personalised children's books in
Israel; these pages are the tools and research of its one-person social media team.

{rules}

Format rules, for every item:
- An item is a list of pieces that appear in this order on the page, split where bold text, a link or a line break starts.
  Return a list with exactly the same number of pieces, in the same order; joined with spaces they must read as one natural
  text. Move words between neighbouring pieces if the grammar needs it, but never leave a piece empty unless it was a lone
  symbol.
- {{0}}, {{1}} ... stand for numbers: keep every one, exactly once, unchanged.
- Keep brand and product names, people's names, Instagram handles, file names, URLs, code and model names as they are.
- A piece that is only a name, a number, a symbol or a word that stays the same is returned unchanged.
- Keep separators exactly as they are: the middle dot, the slash, the vertical bar, arrows.
- Never use an em dash or an en dash. Use a comma, a colon or a full stop; a range of numbers is written {{0}}-{{1}} with a plain hyphen.
- Reply with JSON only, no fences and no comments: an object with the same keys as the items, each a list of strings.

Items:
{items}"""


def claude_bin():
    for c in (os.environ.get("LUMEBOOK_CLAUDE"), shutil.which("claude"), os.path.expanduser("~/.local/bin/claude")):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def run_claude(prompt, timeout=TIMEOUT):
    """The same locked down `claude -p` as /api/sample (tools/lumebook.py run_sample): no tools, no settings, no session,
    an empty folder, the Mac's Claude login (the environment is cut down, so no API key is used). (status, text or code)."""
    cli = claude_bin()
    if not cli:
        return 503, "no_cli"
    work = os.path.join(tempfile.gettempdir(), "lumebook-i18n")
    os.makedirs(work, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k in ("HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TMPDIR", "SHELL")}
    env["PATH"] = os.pathsep.join([os.path.dirname(cli), "/usr/local/bin", "/opt/homebrew/bin", "/usr/bin", "/bin"])
    env["MAX_THINKING_TOKENS"] = "0"   # no thinking: 22 s a batch instead of 80, the same translations (measured 8 Nov 2026)
    cmd = [cli, "-p", "--output-format", "json", "--model", MODEL, "--tools", "", "--no-session-persistence",
           "--disable-slash-commands", "--setting-sources", "", "--settings", '{"alwaysThinkingEnabled": false}',
           "--system-prompt", "You translate interface and research text. You have no tools and no files. Reply with JSON only."]
    with tempfile.TemporaryFile() as fin, tempfile.TemporaryFile() as fout:
        fin.write(prompt.encode("utf-8"))
        fin.seek(0)
        proc = subprocess.Popen(cmd, stdin=fin, stdout=fout, stderr=subprocess.DEVNULL, cwd=work, env=env, start_new_session=True)
        try:
            proc.wait(timeout)
        except subprocess.TimeoutExpired:
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(proc.pid, sig)
                    proc.wait(10)
                    break
                except subprocess.TimeoutExpired:
                    continue
                except ProcessLookupError:
                    break
            return 504, "timeout"
        fout.seek(0)
        raw = fout.read().decode("utf-8", "replace")
    try:
        res = json.loads(raw)
    except ValueError:
        return 502, "failed"
    text = res.get("result") if isinstance(res, dict) else None
    if isinstance(res, dict) and res.get("is_error"):
        low = str(text or "").lower()
        if res.get("api_error_status") == 429 or "rate limit" in low or "usage limit" in low:
            return 429, "rate_limited"
        if "authenticate" in low or "log in" in low or "login" in low or "oauth" in low:
            return 401, "not_logged_in"
        return 502, "failed"
    if not isinstance(text, str) or not text.strip():
        return 502, "empty"
    return 200, text


DASHES = re.compile("\\s*[\u2014\u2013]\\s*")


RANGE = re.compile("\\{(\\d+)\\}([kK%]?)\\s*[\u2014\u2013-]\\s*\\{(\\d+)\\}")


def fix(text, to, src=""):
    t = re.sub("(\\}[kK%]?)\\s*[\u2014\u2013]\\s*(\\{)", "\\1-\\2", text)   # a range of numbers keeps a plain hyphen
    t = DASHES.sub(", ", t)   # no other em or en dashes, ever
    for a, unit, b in RANGE.findall(src):   # a range the dash rule already turned into "5k, 50k"
        t = re.sub("\\{%s\\}([kK%%]?), \\{%s\\}" % (a, b), lambda m: "{%s}%s-{%s}" % (a, m.group(1), b), t)
    t = t.replace("לומיבוק", "לומבוק")
    if "\u00b7" in src and "\u00b7" not in t:   # the model sometimes turns the middle dot into a full stop
        t = t.replace(" . ", " \u00b7 ")
    return t.strip()


def placeholders(s):
    return sorted(PH.findall(s))


def parse_reply(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j < i:
        return None
    try:
        data = json.loads(t[i:j + 1])
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def translate_batch(keys, to):
    """Translate keys into `to`. Returns (status, {key: value}); value is a string, or a list for a key of several pieces."""
    items = {str(n + 1): k.split(SEP) for n, k in enumerate(keys)}
    prompt = PROMPT.format(rules=RULES[to], items=json.dumps(items, ensure_ascii=False, indent=0))
    status, text = run_claude(prompt)
    if status != 200:
        return status, text
    data = parse_reply(text)
    if data is None:
        return 502, "unreadable"
    out = {}
    for n, k in enumerate(keys):
        v = data.get(str(n + 1))
        segs = k.split(SEP)
        if isinstance(v, str):
            v = [v]
        if not isinstance(v, list) or len(v) != len(segs) or not all(isinstance(x, str) for x in v):
            continue
        v = [fix(x, to, sg) for x, sg in zip(v, segs)]
        if placeholders(SEP.join(v)) != placeholders(k):
            continue
        if any(not x and re.search(r"[A-Za-z\u0590-\u05FF]", s) for x, s in zip(v, segs)):
            continue   # a piece with words came back empty
        out[k] = v[0] if len(v) == 1 else v
    return 200, out


class Worker:
    """The project server's background translator: reported words in, dictionaries filled, one batch per claude call."""

    def __init__(self, log=None):
        self.log = log or (lambda *a: None)
        self.cv = threading.Condition()
        self.busy = set()
        self.threads = []
        self.paused_until = 0
        self.state = {"status": "idle"}
        self.prefer = {}          # scope -> last time a page asked about it

    def wake(self, scope=None):
        with self.cv:
            if scope:
                self.prefer[canon(scope)] = time.time()
            if time.time() > self.paused_until or self.state.get("status") in ("not_logged_in", "no_cli"):
                self.paused_until = 0
            while len(self.threads) < PARALLEL:
                t = threading.Thread(target=self._loop, daemon=True, name=f"i18n-{len(self.threads)}")
                self.threads.append(t)
                t.start()
            self.cv.notify_all()

    def report(self, page, to, items):
        """items: [{"scope": "common" | "page", "k": key}]. Returns how many were new."""
        page = canon(page)
        new = enqueue(COMMON, to, [i["k"] for i in items if i.get("scope") == COMMON])
        new += enqueue(page, to, [i["k"] for i in items if i.get("scope") != COMMON])
        if pending():
            self.wake(page)
        return new

    def _loop(self):
        while True:
            with self.cv:
                while True:
                    wait = self.paused_until - time.time()
                    if wait <= 0:
                        recent = {s for s, t in self.prefer.items() if time.time() - t < 900}
                        scope, to, keys = take_batch(self.busy, recent)
                        if keys:
                            for k in keys:
                                self.busy.add((scope, to, k))
                            break
                        self.state = {"status": "idle"}
                    self.cv.wait(max(5, min(wait, 600)) if wait > 0 else 600)
            self.state = {"status": "translating", "scope": scope, "to": to, "n": len(keys), "at": now()}
            try:
                status, res = translate_batch(keys, to)
            except Exception as e:   # never let one bad batch stop the worker
                status, res = 500, f"{type(e).__name__}"
            with self.cv:
                for k in keys:
                    self.busy.discard((scope, to, k))
                if status == 200:
                    stored, dropped = finish(scope, to, keys, res)
                    self.log(f"i18n: {stored}/{len(keys)} to {to} for {scope}" + (f", {dropped} dropped" if dropped else ""))
                elif status in (429, 401, 503):
                    self.paused_until = time.time() + (900 if status == 429 else 3600)
                    self.state = {"status": res, "until": self.paused_until}
                    self.log(f"i18n: paused ({res})")
                else:
                    finish(scope, to, keys, {})
                    self.log(f"i18n: batch failed ({res}) for {scope}")
                self.cv.notify_all()


# ---------- the dictionary in a page ----------

def page_rev(page):
    """Changes whenever the common words or the page's words change (the page polls with it)."""
    return f"{rev(COMMON)}.{rev(canon(page))}"


def payload(page, live=False):
    """What a page gets: its key, the common words and its own, both directions. live: served by the project server,
    which takes reports of missing words (a baked copy in an artifact or on Vercel has no one to report to)."""
    page = canon(page)
    out = {"page": page, "rev": page_rev(page), "common": load(COMMON), "dict": load(page)}
    if live:
        out["live"] = True
    return out


def _json_tag(obj):
    # "<" never appears outside strings in JSON, so escaping it keeps </script> and <!-- out of the page safely
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def tag(page, live=False):
    return f'<script type="application/json" id="lumebook-i18n">{_json_tag(payload(page, live))}</script>\n'


def strip(text):
    return BLOCK.sub("", text)


def block(page):
    return ("<!-- lumebook-i18n:start · the language switch's words for this page (shared/i18n, tools/i18n.py); "
            "written again after every build, never edit it by hand -->\n" + tag(page) + "<!-- lumebook-i18n:end -->\n")


def _at_body_end(text, chunk):
    i = text.lower().rfind("</body")
    if i < 0:
        return text + ("" if text.endswith("\n") else "\n") + chunk
    return text[:i] + chunk + text[i:]


def has_switch(text):
    """Only pages with the project nav (which carries the switch) get a dictionary."""
    return "LB_NAV_DATA" in text or "design/nav.js" in text


def baked(text, page):
    """The page with its block: in front of the edit button's block when there is one, so the order never flips."""
    t = strip(text)
    if not has_switch(t):
        return t
    i = t.find("<!-- lumebook-edits:start")
    return t[:i] + block(page) + t[i:] if i >= 0 else _at_body_end(t, block(page))


def bake_file(path, page):
    """Write the block into a page file; True when the file changed."""
    try:
        with open(path, "rb") as fh:
            text = fh.read().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    new = baked(text, page)
    if new == text:
        return False
    mode = os.stat(path).st_mode & 0o777
    tmp = path + ".i18n-tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(new)
    os.chmod(tmp, mode)
    os.replace(tmp, path)
    return True


def page_files():
    """Every page that can have the switch: built outputs in lumebook.json, the local pages of HQ's tools
    (shared/design/hq-tools.json: the CRO page has no component) and HQ itself. bake_file skips pages without the nav."""
    reg = json.load(open(os.path.join(ROOT, "lumebook.json"), encoding="utf-8"))
    out = []
    for c in (reg.get("components") or {}).values():
        for o in (c.get("build") or {}).get("outputs", []):
            if o.lower().endswith((".html", ".htm")) and o not in out:
                out.append(o)
    try:
        tools = json.load(open(os.path.join(ROOT, "shared", "design", "hq-tools.json"), encoding="utf-8"))
        for tp in tools.get("topics", []):
            for t in tp.get("tools", []):
                o = t.get("local") or ""
                if o.lower().endswith((".html", ".htm")) and o not in out:
                    out.append(o)
    except (OSError, ValueError):
        pass
    out.append("sites/dashboard/lumebook-dashboard.html")
    return [o for o in out if os.path.isfile(os.path.join(ROOT, o)) and not o.startswith("sites/dashboard/site/")]


def bake_outputs(outputs):
    return [o for o in outputs if o in page_files() and bake_file(os.path.join(ROOT, o), o)]


def bake_all():
    return [o for o in page_files() if bake_file(os.path.join(ROOT, o), o)]


# ---------- CLI ----------

def cmd_status():
    q = _qload()["items"]
    print(f"{'scope':70} {'en':>6} {'he':>6} {'waiting':>8}")
    for s in scopes():
        d = load(s)
        w = sum(1 for i in q if i["scope"] == s)
        print(f"{s:70} {len(d['en']):6} {len(d['he']):6} {w:8}")
    extra = sorted({i["scope"] for i in q} - set(scopes()))
    for s in extra:
        print(f"{s:70} {0:6} {0:6} {sum(1 for i in q if i['scope'] == s):8}")
    print(f"-- {len(q)} blocks waiting in {QUEUE}")


def cmd_translate(page=None):
    total = sum(1 for i in _qload()["items"] if not page or i["scope"] == canon(page))
    done = 0
    print(f"PROGRESS 0/{total} starting", flush=True)
    while True:
        prefer = {canon(page)} if page else None
        scope, to, keys = take_batch(set(), prefer)
        if not keys or (page and scope != canon(page)):
            break
        status, res = translate_batch(keys, to)
        if status != 200:
            if status in (429, 401, 503):
                print(f"stopped: {res}", flush=True)
                return 1
            finish(scope, to, keys, {})
            print(f"batch failed ({res}) for {scope}", flush=True)
            continue
        stored, dropped = finish(scope, to, keys, res)
        done += len(keys)
        print(f"PROGRESS {min(done, total)}/{total} {scope} to {to}: {stored} stored" + (f", {dropped} dropped" if dropped else ""), flush=True)
    print(f"done: {done} blocks", flush=True)
    return 0


def cmd_check():
    bad = 0
    for s in scopes():
        d = load(s)
        for to in LANGS:
            for k, v in d[to].items():
                vals = v if isinstance(v, list) else [v]
                joined = SEP.join(vals)
                why = []
                if len(vals) != len(k.split(SEP)):
                    why.append("pieces")
                if placeholders(joined) != placeholders(k):
                    why.append("numbers")
                if DASHES.search(joined):
                    why.append("dash")
                if "לומיבוק" in joined:
                    why.append("לומיבוק")
                if why:
                    bad += 1
                    print(f"{s} [{to}] {', '.join(why)}: {k[:80]!r}")
    print("ok" if not bad else f"{bad} entries to fix")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    t = sub.add_parser("translate")
    t.add_argument("--page")
    sub.add_parser("check")
    b = sub.add_parser("bake")
    b.add_argument("pages", nargs="*")
    a = ap.parse_args()
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "translate":
        return cmd_translate(a.page)
    if a.cmd == "check":
        return cmd_check()
    if a.cmd == "bake":
        done = bake_outputs(a.pages) if a.pages else bake_all()
        print("baked " + (", ".join(done) if done else "nothing (every page already carries its words)"))
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
