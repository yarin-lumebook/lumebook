#!/usr/bin/env python3
"""Build the course data the dashboard's task platform reads.

Reads course/lessons.json (order, task types, checklists, projects: the single source of truth), the lesson texts in
course/lessons/Lnn.md and the book list for the link maker (research/carousel-audit/data/books.json), checks them, and
writes sites/dashboard/course/course-data.js (window.LB_COURSE).

Checks (the build fails on any of them):
  - every lesson file has the fixed headings, at most 3 terms, 3 questions, exactly one right answer per set question,
    an open third question with a model answer (Claude grades the open answer against it in the platform)
  - English only (since 31 Oct 2026): no Hebrew letters in lessons.json, and in lesson files only inside `code`,
    where a lesson quotes literal Hebrew Yarin sees or types (a comment word, a screen label, a book title)
  - no em or en dash in lesson files and in lessons.json
  - curriculum.md section 5 agrees with lessons.json on order, type, capabilities and minutes
A lesson in lessons.json without a file is planned: the platform lists it as coming soon and never opens it.

  python3 course/build.py           # check and write
  python3 course/build.py --check   # check only
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LESSONS_DIR = os.path.join(HERE, "lessons")
OUT = os.path.join(ROOT, "sites", "dashboard", "course", "course-data.js")

HEADINGS = [  # (key, heading text), in file order
    ("now", "Do this now"),
    ("teach", "The lesson"),
    ("example", "Example"),
    ("mistake", "Common mistake"),
    ("cannot", "What the numbers can't prove"),
    ("terms", "Terms"),
    ("quiz", "Quiz"),
]
CAPS = {1: "Make every sale countable", 2: "Choose well", 3: "Run the system", 4: "Explain and defend"}
BANNED = [("\u2014", "em dash"), ("\u2013", "en dash")]
HEBREW = re.compile(r"[\u0590-\u05FF]")


class BuildError(Exception):
    pass


# ---------- markdown, the small subset the lessons use ----------
def inline(text):
    """Escape, then **bold**, `code`, [label](https://...)."""
    t = html.escape(text, quote=False)
    t = re.sub(r"`([^`]+)`", lambda m: f'<code dir="ltr">{m.group(1)}</code>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def md(block):
    """Paragraphs, - and 1. lists, ### subheadings, > quotes. Returns HTML."""
    out, para, items, kind = [], [], [], None

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        nonlocal kind
        if items:
            tag = "ol" if kind == "ol" else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            items.clear()
        kind = None

    for raw in block.split("\n"):
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush_para(); flush_list(); continue
        m_ul, m_ol = re.match(r"^[-*]\s+(.*)", s), re.match(r"^\d+[.)]\s+(.*)", s)
        if s.startswith("### "):
            flush_para(); flush_list(); out.append("<h4>" + inline(s[4:]) + "</h4>")
        elif s.startswith("> "):
            flush_para(); flush_list(); out.append("<blockquote>" + inline(s[2:]) + "</blockquote>")
        elif m_ul or m_ol:
            flush_para()
            k = "ul" if m_ul else "ol"
            if kind and kind != k:
                flush_list()
            kind = k
            items.append((m_ul or m_ol).group(1))
        elif items and raw.startswith(("  ", "\t")):
            items[-1] += " " + s  # a wrapped list item
        else:
            flush_list(); para.append(s)
    flush_para(); flush_list()
    return "".join(out)


# ---------- lesson files ----------
def split_sections(text, lid):
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or not lines[0].startswith("# "):
        raise BuildError(f"{lid}: the first line must be '# <title>'")
    title = lines[0][2:].strip()
    sections, cur = {}, None
    for line in lines[1:]:
        if line.startswith("## "):
            cur = line[3:].strip()
            if cur in sections:
                raise BuildError(f"{lid}: heading '## {cur}' appears twice")
            sections[cur] = []
        elif cur is not None:
            sections[cur].append(line)
        elif line.strip():
            raise BuildError(f"{lid}: text before the first '##' heading: {line.strip()[:40]}")
    names = [h for _, h in HEADINGS]
    got = list(sections)
    if got != names:
        missing = [h for h in names if h not in sections]
        extra = [h for h in got if h not in names]
        raise BuildError(f"{lid}: headings must be exactly, in order: {' / '.join(names)}"
                         + (f"; missing: {', '.join(missing)}" if missing else "")
                         + (f"; unexpected: {', '.join(extra)}" if extra else "")
                         + ("" if missing or extra else "; wrong order"))
    return title, {k: "\n".join(sections[h]).strip() for k, h in HEADINGS}


def parse_terms(block, lid):
    terms = []
    for line in block.split("\n"):
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^-\s+\*\*(.+?)\*\*\s*[:：]\s*(.+)$", s)
        if not m:
            raise BuildError(f"{lid}: a term must be written '- **term**: definition', got: {s[:50]}")
        terms.append({"term": m.group(1).strip(), "def": m.group(2).strip(), "def_html": inline(m.group(2).strip())})
    if len(terms) > 3:
        raise BuildError(f"{lid}: {len(terms)} terms, at most 3")
    return terms


def parse_quiz(block, lid):
    parts = re.split(r"^###\s+", block, flags=re.M)
    if parts[0].strip():
        raise BuildError(f"{lid}: text in the quiz before '### Question 1'")
    qs = []
    for n, part in enumerate(parts[1:], 1):
        head, _, body = part.partition("\n")
        m = re.match(r"^Question\s+(\d)(?:\s*·\s*(.+))?$", head.strip())
        if not m or int(m.group(1)) != n:
            raise BuildError(f"{lid}: quiz heading {n} must be '### Question {n}' (got '### {head.strip()}')")
        tag = (m.group(2) or "").strip()
        recall = None
        mr = re.match(r"^recall (L\d\d)$", tag)
        if mr:
            recall = mr.group(1)
        elif tag and tag != "open":
            raise BuildError(f"{lid}: question {n}: unknown tag '{tag}' (use 'open' or 'recall Lnn')")
        q_lines, options, explain = [], [], []
        for line in body.split("\n"):
            s = line.strip()
            mo = re.match(r"^-\s+\[( |x|X)\]\s+(.+)$", s)
            if mo:
                options.append({"text": mo.group(2).strip(), "html": inline(mo.group(2).strip()), "correct": mo.group(1).lower() == "x"})
            elif s.startswith(">"):
                explain.append(s.lstrip(">").strip())
            elif s:
                if options:
                    raise BuildError(f"{lid}: question {n}: text after the options must be a '> ' line: {s[:40]}")
                q_lines.append(s)
        if not q_lines:
            raise BuildError(f"{lid}: question {n} has no question text")
        if not explain:
            raise BuildError(f"{lid}: question {n} needs a '> ' line (the explanation or the model answer)")
        is_open = tag == "open"
        if is_open and options:
            raise BuildError(f"{lid}: question {n} is open but has options")
        if not is_open:
            if not 3 <= len(options) <= 4:
                raise BuildError(f"{lid}: question {n} needs 3 or 4 options, has {len(options)}")
            if sum(o["correct"] for o in options) != 1:
                raise BuildError(f"{lid}: question {n} needs exactly one '- [x]' option")
        qs.append({"n": n, "kind": "open" if is_open else "choice", "recall": recall,
                   "q": " ".join(q_lines), "q_html": inline(" ".join(q_lines)),
                   "options": options, "explain_html": md("\n".join(explain))})
    if len(qs) != 3:
        raise BuildError(f"{lid}: the quiz needs 3 questions, has {len(qs)}")
    if qs[2]["kind"] != "open" or any(q["kind"] == "open" for q in qs[:2]):
        raise BuildError(f"{lid}: questions 1 and 2 have set answers, question 3 is '### Question 3 · open'")
    return qs


def check_banned(text, where, code_ok=True):
    """Dashes anywhere; Hebrew only inside `code` (code_ok) or nowhere."""
    for i, line in enumerate(text.split("\n"), 1):
        for ch, name in BANNED:
            if ch in line:
                raise BuildError(f"{where}:{i}: {name}")
        bare = re.sub(r"`[^`]*`", "", line) if code_ok else line
        if HEBREW.search(bare):
            raise BuildError(f"{where}:{i}: Hebrew outside `code` (the course is in English): {line.strip()[:60]}")


def load_lesson(meta, ids):
    lid = meta["id"]
    path = os.path.join(LESSONS_DIR, lid + ".md")
    if not os.path.exists(path):
        return {**meta, "ready": False}
    text = open(path, encoding="utf-8").read()
    check_banned(text, os.path.relpath(path, ROOT))
    title, sec = split_sections(text, lid)
    for key in ("now", "teach", "example", "mistake", "cannot"):
        if not sec[key]:
            raise BuildError(f"{lid}: '## {dict(HEADINGS)[key]}' is empty")
    quiz = parse_quiz(sec["quiz"], lid)
    for q in quiz:
        if q["recall"] and (q["recall"] not in ids or ids.index(q["recall"]) >= ids.index(lid)):
            raise BuildError(f"{lid}: question {q['n']} recalls {q['recall']}, which is not an earlier lesson")
    words = len(re.findall(r"\S+", sec["teach"]))
    return {**meta, "ready": True, "title": title, "words": words,
            "now_html": inline(" ".join(sec["now"].split("\n"))),
            "teach_html": md(sec["teach"]), "example_html": md(sec["example"]),
            "mistake_html": md(sec["mistake"]), "cannot_html": md(sec["cannot"]),
            "terms": parse_terms(sec["terms"], lid), "quiz": quiz}


# ---------- curriculum drift ----------
def check_curriculum(spec):
    path = os.path.join(HERE, "curriculum.md")
    text = open(path, encoding="utf-8").read()
    sec = text.split("## 5. The sequence", 1)
    if len(sec) < 2:
        raise BuildError("curriculum.md: no '## 5. The sequence' section")
    body = sec[1].split("\n## ", 1)[0]
    name = {t["id"]: t["name"] for t in spec["types"]}
    rows = re.findall(r"^\|\s*(L\d\d)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|", body, flags=re.M)
    cur = [(r[0], r[2].strip(), sorted(int(x) for x in re.findall(r"\d", r[4])), int(r[5].strip())) for r in rows]
    want = [(l["id"], name[l["type"]], sorted(l["cap"]), l["min"]) for l in spec["lessons"]]
    if cur != want:
        diffs = [f"{a} != {b}" for a, b in zip(cur, want) if a != b]
        if len(cur) != len(want):
            diffs.insert(0, f"{len(cur)} rows in curriculum.md, {len(want)} lessons in lessons.json")
        raise BuildError("curriculum.md section 5 and lessons.json disagree: " + "; ".join(diffs[:5]))


# ---------- books for the link maker ----------
def load_books():
    p = os.path.join(ROOT, "research", "carousel-audit", "data", "books.json")
    d = json.load(open(p, encoding="utf-8"))
    store = d.get("store_url", "https://lumebook.com/IL/he").rstrip("/")
    books = []
    for topic, b in d.get("topics", {}).items():
        if not isinstance(b, dict) or not b.get("book"):
            continue
        books.append({"topic": topic, "book": b["book"], "about": b.get("about", ""),
                      "basis": b.get("basis", ""), "url": f"{store}/books/{b['book']}"})
    return store, books


def build():
    spec = json.load(open(os.path.join(HERE, "lessons.json"), encoding="utf-8"))
    check_banned(open(os.path.join(HERE, "lessons.json"), encoding="utf-8").read(), "course/lessons.json", code_ok=False)
    ids = [l["id"] for l in spec["lessons"]]
    if len(set(ids)) != len(ids):
        raise BuildError("lessons.json: duplicate lesson ids")
    types = {t["id"] for t in spec["types"]}
    for l in spec["lessons"]:
        if l["type"] not in types:
            raise BuildError(f"lessons.json: {l['id']} has unknown type {l['type']}")
        for p in l["pre"]:
            if p not in ids or ids.index(p) >= ids.index(l["id"]):
                raise BuildError(f"lessons.json: {l['id']} needs {p}, which is not an earlier lesson")
    known = set(ids)
    stray = sorted(f[:-3] for f in os.listdir(LESSONS_DIR) if f.endswith(".md") and f[:-3] not in known) if os.path.isdir(LESSONS_DIR) else []
    if stray:
        raise BuildError(f"course/lessons/ has files for lessons not in lessons.json: {', '.join(stray)}")
    check_curriculum(spec)
    lessons = [load_lesson(l, ids) for l in spec["lessons"]]
    store, books = load_books()
    data = {
        "built_from": "course/lessons.json + course/lessons/*.md (course/build.py)",
        "weeks": spec["weeks"], "exam": spec["exam"], "fade": spec["fade"], "types": spec["types"],
        "caps": CAPS, "lessons": lessons, "projects": spec["projects"],
        "store_url": store, "books": books,
    }
    return data


def main():
    try:
        data = build()
    except BuildError as e:
        print(f"course build failed: {e}", file=sys.stderr)
        return 1
    ready = [l for l in data["lessons"] if l["ready"]]
    summary = f"{len(ready)} of {len(data['lessons'])} lessons written ({', '.join(l['id'] for l in ready) or 'none'}), {len(data['books'])} books"
    if "--check" in sys.argv:
        print("course check ok: " + summary)
        return 0
    js = ("// Generated by course/build.py from course/lessons.json and course/lessons/*.md. Do not edit.\n"
          "window.LB_COURSE = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else None
    if old != js:
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(js)
        print(f"wrote {os.path.relpath(OUT, ROOT)} · {len(js)//1024} KB · {summary}")
    else:
        print(f"unchanged {os.path.relpath(OUT, ROOT)} · {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
