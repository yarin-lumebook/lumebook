"""Rule-based Hebrew comment classifier for purchase signals, used to scale the comment analysis
beyond what agents can read by hand. Validated against the agent-classified comments of the first run.

Classes (one per comment, first match wins):
  creator      written by the post's own account
  keyword      a request for the offer the post advertised (the post's comment word, or a short
               link/file request on a post that offers something by DM, or the same short comment
               repeated by 5+ people on the post)
  purchase     says they already bought / ordered / have it
  intent       says they want to buy / order / must have it
  product_q    asks where to buy, for a link, the price, sizes, shipping, how to order
  other        everything else
"""
import re
import unicodedata

EMOJI = re.compile(r"[\U0001F000-\U0001FAFF☀-➿️‍❤⭐✨]+")
NONWORD = re.compile(r"[^\w֐-׿ ]+")


def norm(t):
    t = EMOJI.sub(" ", t or "")
    t = NONWORD.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip().lower()


KW_CAPTION = re.compile(
    r"(?:כתב[וי]|תכתב[וי]|הגיב[וי]|תגיב[וי]|מגיבים|מגיבות|להגיב|תרשמ[וי]|רשמ[וי]|comment)[^\n]{0,40}?(?:את המילה|במילה|המילה)?\s*[\"'״“”‘’«]\s*([^\"'״“”‘’»\n]{1,20}?)\s*[\"'״“”‘’»]")
KW_CAPTION2 = re.compile(r"(?:את המילה|המילה)\s+([֐-׿A-Za-z]{2,15})")
DM_OFFER = re.compile(r"ואשלח|אשלח ל|אשלח את|שלחו לי|בפרטי|בדיי?אם|בהודעה פרטית|\bDM\b|ישלח אליכ|ישלח לכ|נשלח לכ|תקבל[וי] (?:את|קישור|לינק)|לקבלת|לקבל את (?:הקישור|הלינק|הקובץ|המדריך|הרשימה)", re.I)
LINKREQ = re.compile(r"^(?:אשמח|אני אשמח|גם אשמח|אשמח מאוד|לינק|קישור|רוצה|מעוניינת|מעוניין|אשמח לקבל|אשמח ללינק|אשמח לקישור|כאן|פה|אני|גם אני|שלחי|תשלחי|בבקשה)(?:\s|$)")

PURCHASE = re.compile(r"יש לי אות|יש לנו אות|גם לנו יש|גם אצלנו יש|הזמנתי|הזמנו|קניתי|קנינו|רכשתי|רכשנו|יש לנו את|יש לי את|כבר יש לנו|הגיע לנו|קיבלנו את|אצלנו בבית יש")
INTENT = re.compile(r"חייבת (?:כזה|כזאת|את|לקנות|להזמין|להשיג)|חייב (?:כזה|את|לקנות)|רוצה (?:כזה|כזאת|לקנות|להזמין|אחד)|אזמין|הולכת (?:להזמין|לקנות)|הולך (?:להזמין|לקנות)|מזמינה|בטוח (?:קונה|מזמינה)|על הרשימה שלי|חייבת לנסות|חייבת להשיג")
PRODUCT_Q = re.compile(r"מאיפה [\u0590-\u05FF]|איפה (?:קונים|קנית|אפשר לקנות|אפשר לרכוש|ניתן לרכוש|רוכשים|משיגים|השגת|מוכרים|זה)|מאיפה (?:זה|ה|קנית)|כמה (?:עולה|זה עולה|עלה|זה עלה|עולים)|מה המחיר|מחיר\b|מחירים|יש קישור|אפשר (?:קישור|לינק|את הקישור|את הלינק|לקבל קישור)|אשמח (?:לקישור|ללינק)|לינק\?|קישור\?|איך (?:מזמינים|קונים|מזמינה|אפשר להזמין|להזמין)|משלוח|קופון|קוד הנחה|יש הנחה|לאיזה גיל|מאיזה גיל|מתאים לגיל|באיזה (?:חנות|אתר)|שם (?:של ה|ה)?(?:מוצר|ספר|משחק)|מה השם של")


RESOURCE = re.compile(r"(?:אשמח|אפשר|אפשרי|תשלחי|שלחי|רוצה)[^\n]{0,20}(?:קובץ|לקובץ|הקובץ|עותק|pdf|PDF|דף|דפים|דפי|קבוצה|לקבוצה|מדריך|למדריך|רשימה|לרשימה|תבנית|הדרכה|להדרכה|הקלטה|סדנה|וובינר|מתכון|המתכון)")


def caption_keywords(cap):
    cap = cap or ""
    kws = set()
    for m in KW_CAPTION.finditer(cap):
        kws.add(norm(m.group(1)))
    for m in KW_CAPTION2.finditer(cap):
        kws.add(norm(m.group(1)))
    return {k for k in kws if k and len(k) <= 20}


def classify_post(owner, caption, comments):
    """comments: list of dicts with u, t. Returns list of class labels, same order."""
    kws = caption_keywords(caption)
    offer = bool(kws) or bool(DM_OFFER.search(caption or ""))
    counts = {}
    for c in comments:
        n = norm(c.get("t"))
        if n and len(n.split()) <= 3:
            counts[n] = counts.get(n, 0) + 1
    repeated = {k for k, v in counts.items() if v >= 5}
    linkish = sum(1 for c in comments if LINKREQ.match(norm(c.get("t"))) or re.search(r"אשמח (?:לקישור|ללינק)|^(?:לינק|קישור)$", norm(c.get("t"))))
    if linkish >= 5:
        offer = True
    out = []
    for c in comments:
        t = c.get("t") or ""
        n = norm(t)
        if c.get("u") == owner:
            out.append("creator")
            continue
        words = n.split()
        first = words[0] if words else ""
        if n and (n in kws or first in kws or any(n.startswith(k) for k in kws)
                  or n in repeated
                  or (offer and len(words) <= 4 and (LINKREQ.match(n) or not words))):
            out.append("keyword")
            continue
        if RESOURCE.search(t):
            out.append("keyword")
            continue
        if not n and offer:
            out.append("keyword")
            continue
        if PURCHASE.search(t):
            out.append("purchase")
        elif INTENT.search(t):
            out.append("intent")
        elif PRODUCT_Q.search(t):
            out.append("product_q")
        else:
            out.append("other")
    return out


# Broad net for possible purchase signals; agents read every candidate and decide.
CANDIDATE = re.compile(
    r"איפה|מאיפה|כמה|מחיר|עול[הים]|קישור|לינק|link|קנ[יוה]|קונ[הים]|לקנות|הזמ[נ]|להזמין|מזמינ|רכש|לרכוש|רוצה|חייב|משלוח|"
    r"קופון|קוד|הנחה|אתר|חנות|גיל|שם של|מה השם|יש לי|יש לנו|לנו יש|אצלנו יש|גם אני|מתנה|לנכד|לאחיינ|למתנה|ספר|משחק|מוצר|"
    r"מומלץ|ממליצ|המלצה|בא לי|מחכה|יש את|services|שווה|הגיע|קיבלתי|קיבלנו|עובד|באמת עוזר|מעוניינ|פרטים|זמין|במלאי|price|buy|order", re.I)


QUESTION = re.compile(r"\?|^\s*(?:איזה|איזו|איך|מה |מתי|יש לך|יש לכם|יש לכן|את עושה|אתם עושים|אפשר|בא לי|מחכה|מיקום|איפה)")


def candidates(owner, caption, comments):
    labels = classify_post(owner, caption, comments)
    return [i for i, (c, l) in enumerate(zip(comments, labels)) if l not in ("keyword", "creator") and (
        CANDIDATE.search(c.get("t") or "") or QUESTION.search(c.get("t") or ""))], labels
