"""The experts badge of the creator map (Yarin, 06 Nov 2026).

Marks every creator who is a professional in the child and parenting field, so the map can show a badge on the
card and the table row and offer one switch ("מומחים בלבד") and a filter by field. Eleven fields: the eight Yarin named
on 06 Nov 2026, and three he added the same day (art and emotional therapists, developmental physiotherapists, nurses and doctors):

  guide    הדרכת הורים וייעוץ משפחתי     (parent guides, parent coaches, family counsellors)
  sleep    ייעוץ שינה
  potty    ליווי גמילה מחיתולים
  slp      קלינאות תקשורת
  ot       ריפוי בעיסוק
  psy      פסיכולוגיית ילדים             (child psychologists and child psychotherapists)
  biblio   ביבליותרפיה
  classes  חוגים וסדנאות לגיל הרך
  arts     טיפול רגשי ובאמנות            (art therapists and emotional therapists of children)
  physio   פיזיותרפיה התפתחותית
  med      רפואה וסיעוד                   (doctors and nurses; not a doctor's spouse, not a nursing student)

Field names are professions, not people, so one label fits a woman and a man alike.

How a creator gets a field, in this order:
  1. the bio line (`role` in C_all.json, which the research took from the creator's own bio) is matched with the
     patterns below. This runs on every build, so the creators the Saturday run adds are tagged without any step;
  2. a creator the research filed as "Parent guide / coach" is a parent guide (GUIDE_ARCH);
  3. experts.json is Yarin's hand list and always wins: {"add": {handle: [fields]}, "drop": {handle: [fields] or "all"}}.
     A wrong badge is fixed there, never in the patterns.

`python3 src/experts.py` prints who got which field (and who was added or dropped by hand).
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# key, long label (filter, tooltip), short label (badge), pattern over the bio line
KINDS = [
    ("guide", "הדרכת הורים וייעוץ משפחתי", "הדרכת הורים",
     r"מדריכ\S*\s+(ה)?הור(ים|ות)|מדריך\s+(ה)?הור(ים|ות)|הדרכ\S*\s+(ה)?הור(ים|ות)|הדרכה בהורות|מנחת\s+הורים|מנחה\s+הורים"
     r"|יועצ\S*\s+משפחתי|ייעוץ\s+משפחתי|טיפול\s+משפחתי|יועצ\S*\s+הורים|ייעוץ\s+הורי|מאמנ\S*\s+הורים|אימון\s+הורים|בית ספר להורות"),
    ("sleep", "ייעוץ שינה", "ייעוץ שינה",
     r"(יועצ|ייעוץ|הדרכ|מדריכ|מומח)\S*\s+(ה)?שינה"),
    ("potty", "ליווי גמילה מחיתולים", "גמילה מחיתולים",
     r"(יועצ|ייעוץ|מומח|מלוו|ליווי|הדרכ|מדריכ|מרכז)\S*\s+(ל|ב|ה)?גמילה|גמילה מחיתולים"),
    ("slp", "קלינאות תקשורת", "קלינאות תקשורת",
     r"קלינא|\bSLP\b|speech"),
    ("ot", "ריפוי בעיסוק", "ריפוי בעיסוק",
     r"מרפא\S*\s+בעיסוק|ריפוי\s+בעיסוק|\bOT\b"),
    ("psy", "פסיכולוגיית ילדים", "פסיכולוגיה",
     r"פסיכולוגית|פסיכולוג\b|פסיכותרפ"),
    ("biblio", "ביבליותרפיה", "ביבליותרפיה",
     r"ביבליו"),
    ("classes", "חוגים וסדנאות לגיל הרך", "חוגים וסדנאות",
     r"חוג(י|ים)|גן עם אמא|סדנ\S*[^;]{0,30}(אמא ותינוק|לאמהות|לפעוטות|לתינוקות|לילדים|תינוקות)|(תינוקות|פעוטות|אמא ותינוק)[^;]{0,40}סדנ"),
    ("arts", "טיפול רגשי ובאמנות", "טיפול רגשי",
     r"מטפל\S*\s+(רגשי\S*\s+)?(ב|בעזרת\s+)?אמנות|טיפול\s+(רגשי\s+)?באמנות|טיפול\s+רגשי|מטפל\S*\s+רגשי"),
    ("physio", "פיזיותרפיה התפתחותית", "פיזיותרפיה",
     r"פיזיותרפ"),
    ("med", "רפואה וסיעוד", "רפואה וסיעוד",
     r"רפואת ילדים|\bMD\b|רופא(ה|ת)\s|רופא ילדים|סיעוד\s+ילדים|אחות\s+(מוסמכת|ילדים)"),
]
ORDER = [k[0] for k in KINDS]
# the research archetype that already means "parent guide" (the first field above)
GUIDE_ARCH = "Parent guide / coach"


def load_overrides():
    p = os.path.join(HERE, "experts.json")
    if not os.path.exists(p):
        return {"add": {}, "drop": {}}
    j = json.load(open(p, encoding="utf-8"))
    return {"add": j.get("add", {}), "drop": j.get("drop", {})}


def fields_of(c, ov=None):
    """The fields of one creator, in the order of KINDS."""
    ov = ov or load_overrides()
    role = c.get("role", "") or ""
    got = {k for k, _l, _s, pat in KINDS if re.search(pat, role)}
    if c.get("arch") == GUIDE_ARCH:
        got.add("guide")
    h = c["h"]
    got |= set(ov["add"].get(h, []))
    d = ov["drop"].get(h)
    if d == "all":
        got = set()
    elif d:
        got -= set(d)
    unknown = got - set(ORDER)
    assert not unknown, "experts: unknown field %s for %s" % (sorted(unknown), h)
    return [k for k in ORDER if k in got]


def tag(creators):
    """Set c['xp'] (a list of field keys, empty for a creator who is not a professional) on every creator."""
    ov = load_overrides()
    for h in list(ov["add"]) + list(ov["drop"]):
        assert any(c["h"] == h for c in creators), "experts.json names %s, who is not in the map" % h
    for c in creators:
        c["xp"] = fields_of(c, ov)
    return creators


def kinds_for_page():
    """What the page needs: [[key, long label, short label], ...]."""
    return [[k, long_, short] for k, long_, short, _p in KINDS]


if __name__ == "__main__":
    C = json.load(open(os.path.join(HERE, "C_all.json"), encoding="utf-8"))
    tag(C)
    n = {k: 0 for k in ORDER}
    for c in C:
        for k in c["xp"]:
            n[k] += 1
    print("%d of %d creators carry the badge" % (sum(1 for c in C if c["xp"]), len(C)))
    for k, l, _s, _p in KINDS:
        print("  %-8s %3d  %s" % (k, n[k], l))
    for c in C:
        if c["xp"]:
            print("%-32s %-22s %s" % (c["h"], ",".join(c["xp"]), (c.get("role") or "")[:60]))
