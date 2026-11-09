"""LumeBook daily reel calendar (Yarin, 04 Nov 2026: "one a day like we already uploaded").

reels.json is the only source. This tool turns it into the pages and the working folders:

    python3 reels.py build          # writes reel-series-scripts.md (every script) and november-calendar.md
    python3 reels.py lint           # Hebrew voice lint on every hook, voiceover line, card and caption
    python3 reels.py status         # the month at a glance: what is done, what waits on whom
    python3 reels.py new 2.1        # opens media/projects/<today>-reel-2-1/ with README, reel.json for the
                                    # reel editor, and the Instagram caption (disclaimer added where needed)
    python3 reels.py make 2.1       # assembles the reel from edit.json the way 1.1 was made (reel_make.py) and
                                    # burns the text with the reel editor: final/reel-2-1-1.mp4 and its QC sheet
    python3 reels.py link 2.1       # the UTM link for the "לומי" DM replies of that reel
    python3 reels.py done 2.1       # marks a reel posted after it goes up
    python3 reels.py results        # takes each posted reel's numbers from the latest Meta export
                                    # (research/carousel-audit: audit.py import first) into reels.json
    python3 reels.py log 2.1 lumi=4 dms=3 skip=41 watch=6.2   # the numbers the export lacks, 24 h after posting
    python3 reels.py report         # what works: every posted reel, then by series and by approach
    python3 reels.py merge FILE     # copies the saved edits (the "edits" collection of the reels hub artifact 7LypeDPVPLDcL5n2xEQui7, exported with ArtifactData) into reels.json
    python3 reels.py merge local    # the same for edits made on the project server (localhost:8780), which the hub
                                    # page saves in local-edits.json next to this file

Paths are relative to the project root; run from anywhere.
"""
import json, re, subprocess, sys, tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
DATA = HERE / "reels.json"
LINT = ROOT / "carousel/carousel-pipeline/scripts/voice_lint.py"
DAYS = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]
SERIES = {
    1: "לפני שמזמינים",
    2: "הספר של הילד שלך",
    3: "מתנה לחנוכה",
    4: "ירין בודק",
    5: "רגע בבית (באותו יום כמו הקרוסלה)",
    6: "טרנדים מוכנים",
    7: "ימי מבצע",
    8: "מסבתא לנכד",
    9: "שומרי מסורת",
}
STORE = json.loads((ROOT / "shared/facts.json").read_text())
STORE = next(x["url"] for x in STORE["sites"] if x["key"] == "store")
POSTS = ROOT / "research/carousel-audit/data/posts.json"
EDITOR_PY = Path.home() / ".claude/skills/watch-video/.venv/bin/python"
# utm_campaign per series: lower case, hyphens, never changed once links went out (research/cro-crm/measurement.md section 4)
CAMPAIGN = {1: "reel-before-order", 2: "reel-your-childs-book", 3: "reel-hanukkah-gift", 4: "reel-yarin-checks",
            5: "reel-home-moment", 6: "reel-trends", 7: "reel-sale-days", 8: "reel-grandma-gift",
            9: "reel-traditions"}
# numbers Yarin reads in Insights 24 h after posting (playbook section 7); the Meta export does not have them
LOG_KEYS = {"lumi": "\"לומי\" comments", "dms": "DMs answered", "clicks": "link clicks", "books": "books started",
            "skip": "skip rate %", "watch": "average watch s", "nonfollow": "views from non-followers %"}
STATUS = {
    "posted": "פורסם",
    "ready": "מוכן לפרסום",
    "needs-edit": "מחכה לעריכה (Claude)",
    "needs-voice": "מחכה לקריינות ולצילום של ירין",
    "needs-footage": "מחכה לחומר",
    "blocked": "חסום",
    "spare": "ספייר, בלי תאריך",
}


def load():
    return json.loads(DATA.read_text())


def save(d):
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")


def ddmm(iso):
    y, m, dd = iso.split("-")
    return f"{dd} / {m} / {y}"


def weekday(iso):
    return DAYS[date.fromisoformat(iso).weekday()]


def one_line(t):
    return t.replace("\n", " ")


def seconds(r, d):
    """Estimated length of the finished reel in seconds (Yarin, 04 Nov 2026: only 10 to 30 s)."""
    L = d["defaults"]["length"]
    if r.get("clip_seconds"):
        return float(r["clip_seconds"])
    if r.get("vo"):
        words = sum(len(l.split()) for l in r["vo"])
        if r["status"] != "posted":
            words += len(d["defaults"]["cta_voice"].split())
        return round(L["lead_seconds"] + words / L["words_per_second"], 1)
    if r.get("cards"):
        return round(len(r["cards"]) * L["card_seconds"] + L["cta_hold_seconds"], 1)
    return 0.0


def when(r):
    return r["date"] or "9999"


def caption_of(r, d):
    c = r["caption"]
    if r.get("disclaimer"):
        c += "\n\n" + d["defaults"]["caption_disclaimer"]
    return c


def script_md(r, d):
    out = [f"## {r['id']} {one_line(r['hook'])}", ""]
    out.append(f"- סדרה {r['series']}: {SERIES[r['series']]}")
    out.append(f"- תאריך: {weekday(r['date'])} {ddmm(r['date'])}, {d['defaults']['post_time']}" if r["date"] else "- תאריך: ספייר, בלי תאריך")
    out.append(f"- אורך משוער: {seconds(r, d):g} שניות")
    out.append(f"- סטטוס: {STATUS[r['status']]}")
    out.append(f"- קהל: {'סבתות' if r.get('audience') == 'grandma' else 'הורים'}" + (f", עמוד בחנות: {r['page']}" if r.get("page") else ""))
    if r.get("structure"):
        out.append(f"- מבנה: {r['structure']}")
    if r.get("payoff"):
        out.append(f"- השיא על המסך: {r['payoff']}")
    if r.get("shot"):
        out.append(f"- צילום: {r['shot']}")
    if r.get("footage"):
        out.append("- חומר: " + " / ".join(r["footage"]))
    if r.get("yarin_films"):
        out.append("- ירין מצלם: " + ", ".join(r["yarin_films"]))
    if r.get("vo"):
        words = sum(len(l.split()) for l in r["vo"]) + len(d["defaults"]["cta_voice"].split())
        out.append(f"- קריינות (בערך {words} מילים):")
        sees = r.get("sees", [])
        out += [f"  - {l}" + (f" (רואים: {sees[i]})" if i < len(sees) and sees[i] else "") for i, l in enumerate(r["vo"])]
        out.append(f"  - {d['defaults']['cta_voice']}")
    if r.get("cards"):
        out.append("- כרטיסיות טקסט על המסך:")
        out += [f"  - {l}" for l in r["cards"]]
    out.append("- כיתוב לאינסטגרם:")
    out += [f"  > {l}" if l else "  >" for l in caption_of(r, d).split("\n")]
    for b in r.get("blockers", []):
        out.append(f"- לבדוק: {b}")
    if r.get("notes"):
        out.append(f"- הערה: {r['notes']}")
    return "\n".join(out) + "\n"


def build():
    d = load()
    reels = d["reels"]
    by_id = sorted(reels, key=lambda r: [int(x) for x in r["id"].split(".")])

    s = ["# סקריפטים לריל, נובמבר 2026", "",
         "נבנה מ reels.json על ידי reels.py build. לא לערוך כאן, לערוך את reels.json.", "",
         f"מילת תגובה: לומי. עובדות: {d['defaults']['facts']}.", "",
         "סדרות 1 ו 2 נכתבו ב 03 / 11 / 2026 (סשן 'Reel series ideas'). ב 04 / 11 / 2026 נוסף שלב הטלפון לפני התצוגה המקדימה ב 1.2, 1.5 ו 2.1, ונוספו 2.7, 2.8, סדרות 3 עד 6. מאוחר יותר באותו ערב: רק רילס של 10 עד 30 שניות, ונוספה סדרה 7 (11.11, בלאק פריידיי, סייבר מאנדיי).", ""]
    cur = None
    for r in by_id:
        if r["series"] != cur:
            cur = r["series"]
            s += [f"# סדרה {cur}: {SERIES[cur]}", ""]
        s.append(script_md(r, d))
    (HERE / "reel-series-scripts.md").write_text("\n".join(s))

    c = ["# Reel calendar, November 2026", "",
         "Built from reels.json by `reels.py build`. Edit reels.json, not this file.", "",
         f"One reel a day at {d['defaults']['post_time']} Israel time, {d['defaults']['channel']}.", "",
         f"Every reel is {d['defaults']['length']['min']} to {d['defaults']['length']['max']} seconds (estimate in the Sec column).", "",
         "| Date | Day | Reel | Hook | Sec | For | Store page | Status | Waits on |", "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(reels, key=when):
        if not r["date"]:
            continue
        waits = " / ".join(r.get("blockers", [])) or ("Yarin: " + ", ".join(r["yarin_films"]) if r.get("yarin_films") else "")
        c.append(f"| {ddmm(r['date'])} | {weekday(r['date'])} | {r['id']} | {one_line(r['hook'])} | {seconds(r, d):g} | {r.get('audience', 'parents')} | {r.get('page', 'home')} | {STATUS[r['status']]} | {waits} |")
    spares = [r for r in reels if not r["date"]]
    if spares:
        c += ["", "## Spares (no date)", ""] + [f"- {r['id']} {one_line(r['hook'])}: {r.get('notes', '')}" for r in spares]
    c += ["", "## Filming days", "",
          "Each shoot records the 2 s hook clips to camera and the voiceovers for the reels listed, so the edit can run while the week posts.", ""]
    for sh in d["shoots"]:
        c.append(f"- **{weekday(sh['date'])} {ddmm(sh['date'])}**: reels {', '.join(sh['for'])}. {sh['note']}")
    c += ["", "## One reel, start to finish", "",
          "1. Yarin sends the hook clip and the voiceover and any extra shots.",
          "2. `python3 research/israeli-product-reels/src/scripts/series-2026-11/reels.py new <id>` opens the media project with the script, the caption, edit.json and link.txt (the UTM link for the לומי DM replies).",
          f"3. Claude fills edit.json (which clip goes on which voiceover line) and runs `reels.py make <id>`: the 1.1 recipe in one command ({d['defaults']['edit_recipe']}) The captions take the script's spelling; the command lists any word the take does not match.",
          "4. Yarin watches the draft and asks for changes.",
          "5. On Yarin's OK, the reel goes to Postiz as a trial reel at the calendar time (never without the OK).",
          "6. `reels.py done <id>` after it is up. Every DM reply to לומי uses the reel's link.txt link, so sales count as Yarin's.",
          "7. After the next Meta export (`research/carousel-audit/src/audit.py import <csv>`): `reels.py results`, then `reels.py log <id> lumi=.. dms=.. skip=.. watch=..` from Insights, then `reels.py report` (results.md).", ""]
    c += ["## Series", ""]
    for k, v in SERIES.items():
        ids = [r["id"] for r in by_id if r["series"] == k]
        c.append(f"- **{k}. {v}**: {', '.join(ids)}")
    (HERE / "november-calendar.md").write_text("\n".join(c) + "\n")
    sys.path.insert(0, str(HERE))
    import build_page
    build_page.build(d)
    print("wrote reel-series-scripts.md, november-calendar.md and november-calendar.html")


def lint():
    d = load()
    fields = {}
    L = d["defaults"]["length"]
    bad = []
    for r in d["reels"]:
        if r["status"] == "posted":
            continue
        sec = seconds(r, d)
        if r["date"] and not (L["min"] <= sec <= L["max"]):
            bad.append(f"- ERROR {r['id']}: about {sec:g} s, outside {L['min']} to {L['max']} s")
        # Yarin, 05 Nov 2026: never mention the price (an amount, a discount, a sale, the delivery cost)
        copy = " ".join([r["hook"], r["caption"]] + r.get("vo", []) + r.get("cards", []))
        hit = price_hit(copy)
        if hit:
            bad.append(f"- ERROR {r['id']}: mentions the price ({hit!r}); reels never do (Yarin, 05 Nov 2026)")
        hit = NO_TALK.search(copy)
        if hit:
            bad.append(f"- ERROR {r['id']}: talks about {hit.group(0)!r}; reels never mention the language options or the digital copy (Yarin, 05 Nov 2026)")
        # Yarin, 07 Nov 2026: none of the kids are his; he speaks as LumeBook's marketing guy, never as a parent
        if r["voice"] == "yarin":
            hit = NOT_A_PARENT.search(" ".join([copy, r.get("shot", "")]))
            if hit:
                bad.append(f"- ERROR {r['id']}: Yarin speaks as a parent ({hit.group(0)!r}); he has no children, he is LumeBook's marketing guy (Yarin, 07 Nov 2026)")
        if r["voice"] != "trend" or "\n" in r["hook"]:
            fields[f"{r['id']}_hook"] = r["hook"]
        for i, l in enumerate(r.get("vo", [])):
            fields[f"{r['id']}_vo{i}"] = l
        for i, l in enumerate(r.get("cards", [])):
            fields[f"{r['id']}_card{i}"] = l
        for i, l in enumerate(r["caption"].split("\n")):
            fields[f"{r['id']}_cap{i}"] = l
    for k in ("cta_screen", "cta_voice", "cta_caption"):
        fields[k] = d["defaults"][k]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(fields, f, ensure_ascii=False)
    (HERE / "lint.json").write_text(json.dumps(fields, ensure_ascii=False, indent=1) + "\n")
    res = subprocess.run([sys.executable, str(LINT), f.name], capture_output=True, text=True)
    print(res.stdout + res.stderr)
    print("\n".join(bad) or f"length: every dated reel is {L['min']} to {L['max']} s")
    warn = principle_checks(d)
    print("\n".join(warn) if warn else "principles: no warnings")
    return res.returncode or (1 if bad else 0)


PRICE = re.compile(r"שקל|₪|ש\"ח|ש״ח|מחיר|מבצע|הנחה|במקום \d|\b(?:79|99|119|149)\b|עולה|עלות|זול|בחצי|משלוח חינם|דמי משלוח")
# whole words that hold a PRICE stem without being about money (audit of 08 Nov 2026: מעולה, לפעולה in the caption
# disclaimer and להעלות failed the lint); a word not listed here still fails
PRICE_NOT = {"מעולה", "מעולים", "מעולות", "פעולה", "לפעולה", "בפעולה", "הפעולה", "פעולות", "להעלות", "תעלות", "מעלות"}


def price_hit(text):
    """The first price word in text (the whole word around a PRICE match), or None."""
    for m in PRICE.finditer(text):
        word = re.search(r"\w*$", text[:m.start()]).group(0) + m.group(0) + re.match(r"\w*", text[m.end():]).group(0)
        if word not in PRICE_NOT:
            return word
    return None



NO_TALK = re.compile(r"דיגיטל|אנגלית|ערבית|רוסית|שפות|בשפה|שפה")   # Yarin, 05 Nov 2026: the content is in Hebrew for an Israeli audience; nobody cares about the digital copy
NOT_A_PARENT = re.compile(r"(?:ה|ל|ש|מ|ב)?(?:ילד|ילדה|ילדים|בן|בת|נכד|נכדה|נכדים) שלי|אצלנו בבית|אני (?:אמא|אבא)|כאבא|הבית שלי|פרצוף עייף")
HOOK_CHARS = 34   # 2 s of reading at 17 characters a second (principle T5)
SETUP = re.compile(r"(?:היי|שלום|היום אני|הרבה הורים|בואו נדבר|רציתי לספר)")
PRODUCT = re.compile(r"ספר|כריכ|קופס|עמוד|רגע תגובה|תמונה שלך")
EXTRA_ASKS = ("עקבו", "תעקבו", "שתפו", "תשתפו", "תייגו", "בביו", "לינק בביו", "קישור בביו")
# @matan.nistor study rules (Yarin, 09 Nov 2026: "implement to all reels in the reel calendar and the editing rules";
# research/matan-nistor-reels/report.md, rules in the Hebrew voice skill's references/reel-scripts.md)
ANY_BOOK = "כל ספר שיש לך"                  # the shooting note for a hook clip with whatever printed book Yarin has
TALKING = re.compile(r"^\s*(?:אתה|ירין)\b")   # a shot of Yarin himself


def principle_checks(d):
    """Warnings from the 63 principles that a script can be checked against before filming
    (research/israeli-product-reels/smm-research/principles.md). Warnings, not errors: Yarin decides."""
    L = d["defaults"]["length"]
    out, no_search = [], []
    for r in d["reels"]:
        if r["status"] == "posted":
            continue
        rid = r["id"]
        hook = one_line(r["hook"])
        said = " ".join(r.get("vo", []) + r.get("cards", []))
        text = said + " " + r["caption"]
        # Hook rules (Yarin, 07 Nov 2026: "implement them in all the reels"), from principles H1 to H7 and T3, T5:
        # T5: Hebrew on screen at most 17 characters a second; the hook sits over a 2 s talking clip, so 34 characters
        if len(hook) > HOOK_CHARS:
            out.append(f"- T5 {rid}: hook is {len(hook)} characters, {len(hook) / 17:.1f} s to read; keep it to {HOOK_CHARS} (2 s)")
        if len(hook.split()) > 8:
            out.append(f"- H1 {rid}: hook is {len(hook.split())} words, keep it to 8")
        vo = r.get("vo") or []
        if vo:
            # H6: the hook is said and shown, so the first spoken line carries the hook's words
            words = lambda t: set(re.findall(r"[֐-׿0-9.]+", t))
            hw = words(hook)
            if hw and len(hw & words(vo[0])) / len(hw) < 0.6:
                out.append(f"- H6 {rid}: the first spoken line does not say the hook ({vo[0]})")
            # H1: no greeting or setup before the hook
            if SETUP.match(vo[0]):
                out.append(f"- H1 {rid}: the reel opens with a setup line, not the hook ({vo[0]})")
        # H3 and H7: the product is in the first frame (the book in hand, the cover or the box)
        first = (r.get("sees") or [""])[0]
        if first and not PRODUCT.search(first):
            out.append(f"- H3 {rid}: no book in the first frame ({first})")
        for i, c in enumerate(r.get("cards", [])):
            if len(one_line(c)) / 17 > L["card_seconds"]:
                out.append(f"- T5 {rid}: card {i + 1} is {len(one_line(c))} characters, needs {len(one_line(c)) / 17:.1f} s, cards get {L['card_seconds']} s")
        # T6: an on-screen line does not start with a Latin word or punctuation (the reel editor keeps numbers
        # in reading order, so a leading "119" is fine; a leading "LumeBook" or "?" lands on the wrong side)
        for line in r["hook"].split("\n") + [x for c in r.get("cards", []) for x in c.split("\n")]:
            first = line.strip()[:1]
            if first and (first.isascii() and first.isalpha() or first in "?!.,:"):
                out.append(f"- T6 {rid}: on-screen line starts with {first!r}: {line.strip()}")
        # M1 to M4: the @matan.nistor study (09 Nov 2026). Warnings like the rest; Yarin decides.
        sees_l = r.get("sees") or []
        if r["voice"] == "yarin" and r.get("vo") and not r.get("payoff"):
            out.append(f"- M4 {rid}: no payoff: name what the viewer sees when the reel pays off (reels.json \"payoff\")")
        if sees_l and ANY_BOOK in r.get("shot", "") and "כריכ" not in sees_l[0]:
            out.append(f"- M1 {rid}: the first frame is any printed book; show this reel's cover with a name from the first frame")
        n_vo = len(r.get("vo") or [])
        for i, sh in enumerate(sees_l[1:max(n_vo - 1, 1)], 1):
            if TALKING.match(sh) and not PRODUCT.search(sh):
                out.append(f"- M2 {rid}: line {i + 1} cuts back to Yarin's face ({sh}); give it its own picture of what is said")
        if n_vo > 1 and len(sees_l) >= n_vo and TALKING.match(sees_l[n_vo - 1]) and not PRODUCT.search(sees_l[n_vo - 1]):
            out.append(f"- M3 {rid}: the last line ends on Yarin ({sees_l[n_vo - 1]}); end on the payoff picture")
        # Shabbat: the traditions series talks to families who keep it, so it never goes up on a Friday or Saturday
        if r["series"] == 9 and r["date"] and date.fromisoformat(r["date"]).weekday() in (4, 5):
            out.append(f"- S9 {rid}: traditions reel on {weekday(r['date'])}; move it to Sunday to Thursday")
        # C1: one CTA per reel, the "לומי" comment
        asks = [a for a in EXTRA_ASKS if a in text]
        if asks:
            out.append(f"- C1 {rid}: a second ask besides \"לומי\": {', '.join(asks)}")
        # T7: the caption is a searchable Hebrew description, up to 5 specific hashtags
        tags = r["caption"].count("#")
        if tags > 5:
            out.append(f"- T7 {rid}: {tags} hashtags, keep it to 5")
        if tags == 0:
            no_search.append(rid)
    if no_search:
        out.append(f"- T7: {len(no_search)} captions have no hashtags or search line ({', '.join(no_search[:6])}"
                   f"{' ...' if len(no_search) > 6 else ''}). Instagram search reads the caption: one plain line of words "
                   "parents search for and up to 5 specific hashtags.")
    return out


def status():
    d = load()
    today = date.today().isoformat()
    for r in sorted(d["reels"], key=when):
        mark = ">" if r["date"] == today else " "
        proj = r.get("project", "")
        has = ""
        if proj and (ROOT / proj / "final").exists():
            has = f" final: {len(list((ROOT / proj / 'final').glob('*.mp4')))} mp4"
        print(f"{mark} {r['date'] or 'spare':<10} {r['id']:>4} {r['status']:<13} {one_line(r['hook'])[:40]}{has}")
        for b in r.get("blockers", []):
            print(f"{'':22}! {b}")


def new(rid):
    d = load()
    r = next((x for x in d["reels"] if x["id"] == rid), None)
    if not r:
        sys.exit(f"no reel {rid}")
    if r.get("project"):
        sys.exit(f"{rid} already has {r['project']}")
    if not r["date"]:
        sys.exit(f"{rid} is a spare: give it a date in reels.json first")
    folder = f"media/projects/{date.today().isoformat()}-reel-{rid.replace('.', '-')}"
    p = ROOT / folder
    for sub in ("source", "work", "final"):
        (p / sub).mkdir(parents=True, exist_ok=True)
    (p / "README.md").write_text(
        f"# Reel {rid}: {one_line(r['hook'])}\n\nPosting {ddmm(r['date'])} {d['defaults']['post_time']}. "
        f"Script and caption come from research/israeli-product-reels/src/scripts/series-2026-11/reels.json.\n\n"
        + script_md(r, d) +
        "\n## Checklist\n\n- [ ] footage in `source/`\n- [ ] edit (1.1 recipe), QC frames, transcript check\n"
        "- [ ] no AI wording on screen (the wizard's AI step is cut)\n- [ ] blockers above cleared\n"
        "- [ ] Yarin's OK on the final\n- [ ] Postiz trial reel scheduled with Yarin's OK\n")
    (p / "caption.txt").write_text(caption_of(r, d) + "\n")
    (p / "reel.json").write_text(json.dumps({
        "source": "work/video.mp4", "name": f"reel-{rid.replace('.', '-')}",
        "hooks": [r["hook"]], "hook_seconds": max(1.6, round(len(one_line(r["hook"])) / 17, 1)), "captions": "words.json",
        "cta": {"text": d["defaults"]["cta_screen"], "seconds": 3.0, "highlight": True},
        "versions": 1, "flip": False, "audio": "work/sound.wav"}, ensure_ascii=False, indent=1) + "\n")
    if r.get("vo"):
        # the plan reels.py make reads (reel_make.py has every key)
        foot = r.get("footage", [])
        plan = {"_about": "reels.py make reads this (reel_make.py has every key). Put Yarin's files in source/yarin/, fill each "
                          "segment's src and ss, and cue it on a voiceover line number or a word of the script.",
                "speed_after_hook": 1.1}
        if any("one talking take" in f.lower() for f in foot):
            plan.update(take="source/yarin/take.mov", voice_start=0.0)       # 1.7: the whole reel is one take, jump cuts
        else:
            screen = ("screen", "recording", "preview pages", "site recording")
            segs = [{"at": i, "src": "source/TODO.mov", "ss": 0, "window": any(w in f.lower() for w in screen), "_footage": f}
                    for i, f in enumerate(x for x in foot if not x.lower().startswith("yarin: hook"))]
            if segs:
                segs[-1]["at"] = "cta" if len(segs) > 1 else 0
            plan.update(hook_clip="source/yarin/hook.mov", hook_end=None, voice="source/yarin/voice.m4a", voice_start=0.0, segments=segs)
        # a number card on top for each counted point ("אחד:", "שתיים,"), as 1.7's shot asks
        nums = {"אחד": "1", "שתיים": "2", "שלוש": "3", "ארבע": "4", "חמש": "5"}
        cards = [{"at": i, "text": nums[l.split()[0].strip(",:.")]} for i, l in enumerate(r["vo"]) if l.split()[0].strip(",:.") in nums]
        if cards:
            plan["top_cards"] = cards
        (p / "edit.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n")
    (p / "link.txt").write_text(link(rid, quiet=True) + "\n")
    r["project"] = folder
    save(d)
    print(folder)


def link(rid, quiet=False):
    """The store link for the "לומי" DM replies of one reel. utm_medium=social is what counts as Yarin's
    (lumebook-yarin-pay-utm-25pct); the series is the campaign, the posting day the content, the reel the term."""
    d = load()
    r = next((x for x in d["reels"] if x["id"] == rid), None)
    if not r:
        sys.exit(f"no reel {rid}")
    from urllib.parse import urlencode
    q = {"utm_source": "instagram", "utm_medium": "social", "utm_campaign": CAMPAIGN[r["series"]],
         "utm_content": "dm-" + (r["date"] or date.today().isoformat()).replace("-", ""), "utm_term": "r" + rid.replace(".", "-")}
    # the reel's own book or gift page (reels.json "page"), else the store home (Yarin, 05 Nov 2026: best sellers)
    u = STORE + ("/" + r["page"] if r.get("page") else "") + "?" + urlencode(q)
    if not quiet:
        print(u)
    return u


def make(rid, *flags):
    """Assemble with reel_make.py under the reel editor's Python (it has Pillow), then build with the reel editor."""
    sys.exit(subprocess.run([str(EDITOR_PY), str(HERE / "reel_make.py"), rid, *flags]).returncode)


def results():
    """Copy each posted reel's latest numbers from the carousel audit's import of the Meta export
    (research/carousel-audit/src/audit.py import <export.csv> first). Matched by posting day and an evening time."""
    d = load()
    posts = json.loads(POSTS.read_text())["posts"].values()
    reels = [p for p in posts if p["type"] == "reel" and p.get("username") == "lumebook.il"]
    n = 0
    for r in d["reels"]:
        if r["status"] != "posted" or not r["date"]:
            continue
        hit = [p for p in reels if p["posted_local"][:10] == r["date"] and p["posted_local"][11:13] >= "18"]
        if len(hit) != 1:
            print(f"{r['id']}: {len(hit)} reels posted that evening in the export ({POSTS.name}), not matched")
            continue
        p = hit[0]
        r["ig"] = {"shortcode": p["shortcode"], "permalink": p["permalink"], "posted": p["posted_local"]}
        r.setdefault("results", {}).update({k: p["latest"].get(k) for k in ("views", "reach", "likes", "comments", "shares", "saves", "follows")})
        r["results"]["as_of"] = p["latest"]["as_of"]
        n += 1
    save(d)
    print(f"{n} reels updated from the export. Next: reels.py log <id> lumi=.. dms=.. skip=.. watch=.., then reels.py report")


def log(rid, *pairs):
    d = load()
    r = next((x for x in d["reels"] if x["id"] == rid), None)
    if not r:
        sys.exit(f"no reel {rid}")
    res = r.setdefault("results", {})
    for kv in pairs:
        k, _, v = kv.partition("=")
        if k not in LOG_KEYS:
            sys.exit(f"unknown {k}: use {', '.join(LOG_KEYS)}")
        res[k] = float(v) if "." in v else int(v)
    res["logged"] = date.today().isoformat()
    save(d)
    print(rid, {k: res[k] for k in res if k in LOG_KEYS})


def report():
    """Playbook section 7: compare concepts by "לומי" comments, DMs and books, not by plays, and run each
    concept at least twice before judging it. Shares per reach stand in for sends (principles R5, C4)."""
    d = load()
    done_ = [r for r in d["reels"] if r.get("results")]
    if not done_:
        print("no results yet: after posting, import the Meta export (research/carousel-audit/src/audit.py import <csv>), "
              "then reels.py results and reels.py log")
        return
    def row(rs):
        g = lambda k: [r["results"][k] for r in rs if r["results"].get(k) is not None]
        avg = lambda k: (sum(g(k)) / len(g(k))) if g(k) else None
        reach = sum(g("reach")) or None
        shares = sum(g("shares")) if g("shares") else None
        f = lambda v, p=0: "" if v is None else f"{v:.{p}f}"
        return [str(len(rs)), f(avg("views")), f(shares / reach * 100 if shares is not None and reach else None, 1),
                f(avg("saves"), 1), f(avg("lumi"), 1), f(avg("dms"), 1), f(avg("books"), 1), f(avg("skip")), f(avg("watch"), 1)]
    head = "| {} | Reels | Views | Shares per 100 reach | Saves | לומי | DMs | Books | Skip % | Watch s |"
    sep = "|---" * 10 + "|"
    lines = ["# Reel results", "", head.format("Reel"), sep]
    for r in sorted(done_, key=when):
        lines.append(f"| {r['id']} {ddmm(r['date'])} | " + " | ".join(row([r])) + " |")
    for title, key, names in (("Series", "series", SERIES), ("Approach", "approach", None)):
        lines += ["", head.format(title), sep]
        for k in sorted({r.get(key) for r in done_}, key=str):
            rs = [r for r in done_ if r.get(key) == k]
            mark = "" if len(rs) >= 2 else " (1 reel, too early to judge)"
            lines.append(f"| {k} {names[k] if names else ''}{mark} | " + " | ".join(row(rs)) + " |")
    (HERE / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def merge(path, only=None):
    """Copy the page's saved edits into reels.json. path = JSON of the artifact db collection "edits"
    (a list of documents, or {"docs": [...]}, each with key and text). Formatting stays on the page only;
    reels.json gets the plain text. Prints what changed; build afterwards.
    only = one reel id (merge local 5.5): copy that reel's edits and nothing else (the hub's reel job does this
    before it builds the video, 07 Nov 2026)."""
    d = load()
    if path == "local":   # edits made on the project server: {"edits": {key: doc}, "made": ..., "requests": ...}
        lf = HERE / "local-edits.json"
        raw = json.loads(lf.read_text()) if lf.exists() else {}
        docs = list((raw.get("edits") or {}).values())
        print(f"{len(docs)} edits in {lf.name}")
    else:
        raw = json.loads(Path(path).read_text())
        docs = raw.get("docs", raw.get("documents", [])) if isinstance(raw, dict) else raw
    by = {"r" + r["id"].replace(".", "-"): r for r in d["reels"]}
    lists = {"vo": "vo", "sees": "sees", "cards": "cards", "footage": "footage", "blocker": "blockers"}
    shoots = {s["date"]: s for s in d["shoots"]}
    n = 0
    for doc in docs:
        doc = doc.get("data", doc)
        key, text = doc.get("key") or doc.get("id"), (doc.get("text") or "").strip()
        html = doc.get("html") or ""
        if html and (not text or "<br" in html):   # some saves keep the text only in html (no text, or line breaks lost)
            text = re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>|</div>|</p>", "\n", html)).replace("&nbsp;", " ")
            text = "\n".join(l.strip() for l in text.split("\n")).strip()
        if not key or text == "":
            continue
        parts = key.split("__")
        if only and parts[0] != "r" + only.replace(".", "-"):
            continue
        if parts[0] == "shoot":
            sh = shoots.get(parts[1])
            if sh and sh["note"] != text:
                sh["note"] = text; n += 1; print(key)
            continue
        r = by.get(parts[0])
        if not r:
            print(f"skipped {key} (page text, not in reels.json)")
            continue
        field = parts[1]
        if field == "caption":
            text = text.split("\n\n" + d["defaults"]["caption_disclaimer"])[0].rstrip()
            old = r["caption"]
        elif field == "films":
            text_l = [x.strip() for x in text.split(",") if x.strip()]
            if text_l != r.get("yarin_films"):
                r["yarin_films"] = text_l; n += 1; print(key)
            continue
        elif field in lists:
            arr = r.setdefault(lists[field], [])
            i = int(parts[2])
            if field == "sees" and i < len(r.get("vo", [])):
                arr.extend([""] * (i + 1 - len(arr)))  # "what they see" follows the voiceover lines
            if i < len(arr) and arr[i] != text:
                arr[i] = text; n += 1; print(key)
            continue
        else:
            old = r.get(field, "")
        if field == "hook" and " ".join(text.split()) == " ".join(old.split()):
            continue  # the page shows the hook on one line; same words keep the on-screen line break
        if old != text:
            r[field] = text; n += 1; print(key)
    save(d)
    print(f"{n} fields changed. Next: reels.py lint, then reels.py build")


def done(rid):
    d = load()
    r = next((x for x in d["reels"] if x["id"] == rid), None)
    if not r:
        sys.exit(f"no reel {rid}")
    r["status"] = "posted"
    save(d)
    build()


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["status"]
    {"build": build, "lint": lint, "status": status, "new": new, "done": done, "merge": merge, "make": make,
     "link": link, "results": results, "log": log, "report": report}[cmd](*args)
