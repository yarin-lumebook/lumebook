"""Build report.html: the creator-content research as a sidebar app on the LumeBook design system.

    python3 research/creator-content-conversion/src/build_page.py

Sources: the curated findings below (kept in step with report.md), posts.csv and creators.csv for every
table and chart, evidence.md and methodology.md for the reference views. Never edit report.html by hand.
Internal page (holds sales figures): local file, not published. Standard library only.
"""
import collections
import csv
import html
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(OUT, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
sys.path.insert(0, HERE)
import design  # noqa: E402
from build_html import inline, convert  # noqa: E402  (markdown helpers)

E = html.escape


def num(x):
    if x in (None, ""):
        return None
    try:
        v = float(x)
    except ValueError:
        return None
    return int(v) if v.is_integer() else v


def fmt(v, d=2):
    if v is None:
        return "n/a"
    if isinstance(v, int) or (isinstance(v, float) and v >= 100):
        return f"{v:,.0f}"
    return f"{v:,.{d}f}"


def he(t):
    return f'<bdi class="he" dir="rtl">{E(t)}</bdi>'


def ig(code, label=None):
    return f'<a href="https://www.instagram.com/p/{E(code)}/" target="_blank" rel="noopener">{E(label or code)}</a>'


def chip(text, kind=""):
    return f'<span class="lb-chip {kind}">{E(text)}</span>'


def table(head, rows, num_cols=()):
    h = "".join(f'<th class="{"num" if i in num_cols else ""}">{c}</th>' for i, c in enumerate(head))
    b = "".join("<tr>" + "".join(f'<td class="{"num" if i in num_cols else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="lb-table-wrap"><table class="lb-table"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def hbars(items, maxv=None, fmtv=lambda v: fmt(v), marker=None, cls=""):
    maxv = maxv or max(v for _, v, _ in items)
    rows = []
    for label, v, sub in items:
        w = max(2, min(100, v / maxv * 100))
        mk = f'<b class="rp-mark" style="inset-inline-start:{marker / maxv * 100:.1f}%"></b>' if marker else ""
        rows.append(f'<div class="lb-hbar {cls}"><span>{label}{f"<small>{sub}</small>" if sub else ""}</span>'
                    f'<span class="track">{mk}<i style="width:{w:.1f}%"></i></span><span class="v">{fmtv(v)}</span></div>')
    return '<div class="lb-hbars">' + "".join(rows) + "</div>"


def stat(label, value, foot="", kind=""):
    return (f'<div class="lb-card rp-stat {kind}"><div class="lb-stat"><span class="lb-stat-label">{label}</span>'
            f'<span class="lb-stat-value">{value}</span>{f"<span class=lb-stat-foot>{foot}</span>" if foot else ""}</div></div>')


def head(title, eyebrow, lede=""):
    return (f'<header class="rp-head"><span class="lb-eyebrow">{eyebrow}</span><h2>{title}</h2>'
            + (f'<p class="lb-lede">{lede}</p>' if lede else "") + "</header>")


# ---------------------------------------------------------------- data
posts = list(csv.DictReader(open(os.path.join(OUT, "posts.csv"), encoding="utf-8")))
creators = {c["creator"]: c for c in csv.DictReader(open(os.path.join(OUT, "creators.csv"), encoding="utf-8"))}
for p in posts:
    for k in ("plays", "likes", "comments", "reposts", "followers_14oct", "rel_plays", "rel_likes", "rel_comments",
              "likes_per_1k_plays", "comments_per_1k_plays", "reposts_per_1k_plays", "likes_per_1k_followers_proxy",
              "baseline_n_same_format", "baseline_median_plays", "comments_sampled"):
        p[k] = num(p[k])
    for k in [k for k in p if k.startswith("cmt_")]:
        p[k] = num(p[k])
S = [p for p in posts if p["set"] == "sample"]
reels = [p for p in S if p["format"] == "reel" and p["plays"]]
big = [p for p in reels if p["plays"] >= 2000]
nonreel = [p for p in S if p["format"] != "reel"]
CP = [p for p in posts if p["comments_sampled"] not in (None, 0)]


def topic(p, n=64):
    t = p.get("topic") or ""
    return E(t[:n] + ("…" if len(t) > n else ""))


def intent(p):
    return (p["cmt_explicit_buying_intent"] or 0) + (p["cmt_product_or_price_question"] or 0) + (p["cmt_purchase_report"] or 0)


def subst(p):
    return (p["cmt_identification"] or 0) + (p["cmt_personal_experience"] or 0) + (p["cmt_practical_help_request"] or 0)


TOTAL_CMT = int(sum(p["comments_sampled"] for p in CP))
CLASS_TOT = {k: int(sum(p[k] or 0 for p in CP)) for k in posts[0] if k.startswith("cmt_") and k not in ("cmt_purchase_intent_signals",)}
INTENT_TOT = CLASS_TOT["cmt_explicit_buying_intent"] + CLASS_TOT["cmt_product_or_price_question"] + CLASS_TOT["cmt_purchase_report"]

# ---------------------------------------------------------------- views
V = {}  # id -> html

# Overview -------------------------------------------------------------
FINDINGS = [
    ("No creator post is tied to a LumeBook sale yet",
     "Everything here is attention, engagement or an intent proxy. The store already has the plumbing: an ambassador link that credits printed books for 7 days, and UTM attribution sent with each book started when the visitor accepts analytics cookies. Nobody has read that data for creators.",
     "measure", "E12"),
    ("Milestone topics do not win reach",
     "Inside each creator's own feed, LumeBook's buying occasions run at the creator's normal level (median 0.93x). Humour, family moments, nostalgia and hands-on demos are what spread.",
     "content", "E1"),
    ("Buying questions follow a useful thing shown in use",
     "Across 134 creators only 595 of 22,281 audience comments (2.7%) ask where to buy, the price, or say they want or bought it, and 71 posts get three or more. Those posts show a product demonstrated (41% vs 8% of ordinary posts), a price (13% vs 1%) or a brand collaboration (49% vs 15%); humour almost never (4% vs 19%).",
     "signals", "Round 2"),
    ("Professionals already sell through \"comment a word, I'll DM you\"",
     "15% of recent posts use it. Book lists made this way by speech therapists and a parent guide drew 882 to 1,389 comments. That is the natural way in for a personalised book.",
     "content", "E3, E5"),
    ("Gift-givers barely show up",
     "5 self-identified grandparents and 2 gift mentions in 2,982 comments; birthday posts are tributes that collect greetings. \"Older buyers are grandmothers\" stays a hypothesis.",
     "icp", "E6, E7"),
]
cards = "".join(
    f'<a class="lb-card rp-finding" href="#{v}"><span class="rp-n">{i}</span><h3>{E(t)}</h3><p class="lb-muted">{E(b)}</p>'
    f'<span class="lb-row">{chip("Evidence " + ev, "outline")}<span class="lb-spacer"></span><span class="rp-go">Open →</span></span></a>'
    for i, (t, b, v, ev) in enumerate(FINDINGS, 1))
V["overview"] = f"""
{head("What makes LumeBook's potential buyers stop, ask and consider buying", "Creator research · 14 Oct 2026",
      "134 creators from the creator map (the top half by views plus the first round), their 1,456 most recent Instagram posts and 22,428 audience comments read in Hebrew. A 41-creator deep dive was coded post by post from frames, slides and captions.")}
<div class="lb-alerts">
  <div class="lb-alert warn"><span class="lb-chip warning">Blocker</span><span class="lb-alert-text"><b>instagram.com/lumebookai could not be loaded on 14 Oct.</b> Control accounts loaded fine. Check it before any creator tags LumeBook.</span><a href="#evidence-e14">E14</a></div>
</div>
<div class="lb-grid cols-4">
  {stat("Creators sampled", "134", "top half of the 243 by views, + 13")}
  {stat("Recent posts", "1,456", "722 coded from frames and slides")}
  {stat("Comments read", "22,428", "on 1,391 posts")}
  {stat("Sales tied to a creator post", "0", "no attributed data read yet", "is-zero")}
</div>
<a class="lb-card is-accent" href="#signals"><span class="lb-eyebrow">New · round 2 · 134 creators</span><h3>Which creators' own posts already make people ask how to buy</h3>
  <p class="lb-muted">The top half of the map, 1,456 posts and 22,428 comments read: buying questions come from a product shown working with a price or deal, not from humour or tips. Kids' gift lists and toy reviews by therapists already pull them.</p><span class="rp-go">Open →</span></a>
<section class="lb-section"><div class="lb-section-head"><h3>Strongest findings</h3><span class="lb-meta">Tap a card for the detail</span></div>
<div class="lb-grid cols-2 rp-findings">{cards}</div></section>
<div class="lb-grid cols-2">
  <a class="lb-card is-accent rp-cta" href="#tests"><span class="lb-eyebrow">First test to run</span>
    <h3>A speech therapist's pacifier or book-list post, with LumeBook's pacifier book as the one personalised pick</h3>
    <p class="lb-muted">Start with <b>topaz_meir_slp</b>: already "in process" in the map, 3.25 plays per follower, a comment word on 10 of 12 posts, and her own commenters asked when to wean. Her ambassador link goes in the DM.</p>
    <span class="lb-row">{chip("T1", "tint")}{chip("7-day window", "")}<span class="lb-spacer"></span><span class="rp-go">See the test →</span></span></a>
  <a class="lb-card is-quiet" href="#unknowns"><span class="lb-eyebrow">Still unknown</span>
    <h3>Whether any of this sells books</h3>
    <p class="lb-muted">No post, topic or creator has attributed sessions, books started or orders. Reach, saves, shares and link taps live in creators' Insights. The store does not record who the buyer is relative to the child.</p>
    <span class="rp-go">Full list →</span></a>
</div>
<p class="lb-note">Labels used throughout: <b>Observed</b> (seen in a post, comment, profile or file), <b>Interpretation</b> (my reading), <b>Hypothesis</b> (to test). Internal: uses sales figures from <code>docs/lumebook-sales-data-decisions-2026-10-12.md</code>.</p>
"""

# Decision answers -----------------------------------------------------
QA = [
    ("Which topics attract attention?", "Humour and relatable moments, family outings and surprises, nostalgia, and practical skill demos (toilet wiping, potty). Milestone topics hold the baseline; they do not lift it.", "E1", "content"),
    ("Which topics generate substantive discussion or practical interest?", "Pregnancy and family life (identification), behaviour and gan adjustment (help requests and objections), reading aloud (book recommendation requests), development (keyword requests for files).", "E2", "content"),
    ("Which content produces explicit purchase-intent signals?", f"Posts that show a useful object in use or recommend specific items: a gan toilet light, board games, picture books, bedtime books, an attraction. Signals are few ({INTENT_TOT} in {TOTAL_CMT:,}).", "E4", "voice"),
    ("Which content has verified activation or purchase results?", "None in this study. Self-reported only: one author's 530 families and 4,000+ homes (public posts); one creator's 100+ copies (private email).", "E12", "measure"),
    ("Which buyer segments are supported, uncertain or contradicted?", "Weaning and transition parents: supported for interest. Expecting parents: attention yes, purchase uncertain. Birthday buyers, grandparents, fathers: uncertain. \"Only young moms buy\": contradicted.", "E6, E7, E8", "icp"),
    ("Which popular topics are weakly connected to buying a LumeBook?", "Couple and husband humour, comedy characters, travel, recipes, cleaning, beauty, pranks. High plays; comments are laughter or praise.", "E11", "content"),
    ("Which creators and approaches deserve testing first?", "Professionals who already run comment-word funnels on LumeBook occasions (pacifier, potty, gan, first grade, reading), then parents living a new-sibling moment now.", "E3, E5, E8", "creators"),
]
V["questions"] = head("Answers to the decision questions", "Answer", "Seven questions from the brief, each answered in one paragraph with the evidence behind it.") + \
    '<div class="lb-stack">' + "".join(
        f'<a class="lb-card rp-qa" href="#{v}"><div class="rp-qa-q"><span class="rp-n">{i}</span><h3>{E(q)}</h3></div><p>{E(a)}</p>'
        f'<span class="lb-row">{chip("Evidence " + ev, "outline")}<span class="lb-spacer"></span><span class="rp-go">Detail →</span></span></a>'
        for i, (q, a, ev, v) in enumerate(QA, 1)) + "</div>"

# Evidence boundary + leaderboards ------------------------------------
BOUND = [
    ("Attention", "Plays (reels)", "300 recent reels with plays", "Observed", "success"),
    ("Attention", "Reach, impressions, watch time, retention", "None", "Unavailable", ""),
    ("Engagement", "Likes, comments, reposts", "All recent posts (likes hidden on 41, reposts missing on 105)", "Observed", "success"),
    ("Engagement", "Saves, DM shares", "None", "Unavailable", ""),
    ("Consideration", "Product questions, buying intent, keyword requests", f"{TOTAL_CMT:,} classified comments on 184 posts", "Proxy", "info"),
    ("Consideration", "Profile visits, follows, link clicks, DMs", "None", "Unavailable", ""),
    ("Activation", "Sessions, books started, previews", "Store-wide only: 6,130 people started a book, 21.7% paid within 7 days", "Private, store-wide", "warning"),
    ("Checkout", "Checkout starts, payment step", "Store-wide only: 202 orders reached payment, 85 bought (30 days, Mixpanel)", "Private, store-wide", "warning"),
    ("Purchase", "Attributed orders, revenue, cost per purchase", "None per creator", "Unavailable", ""),
    ("Self-reported", "Creator sales claims", "530 families, 4,000+ homes (public); 100+ copies (private email)", "Unverified", "danger"),
]
boundary = table(["Stage", "KPI", "What this study has", "Status"],
                 [[f"<b>{s}</b>", E(k), E(h), chip(st_, c)] for s, k, h, st_, c in BOUND])

base = ["Creator", "Post", "Published", "Topic"]


def row(p, *extra):
    return [E(p["creator"]), ig(p["post_code"]), p["published_utc"][:10], topic(p)] + list(extra)


A1 = table(base + ["Plays", "Followers"], [row(p, fmt(p["plays"]), fmt(p["followers_14oct"])) for p in sorted(reels, key=lambda p: -p["plays"])[:10]], (4, 5))
A2 = table(base + ["Plays", "Creator median", "Ratio"],
           [row(p, fmt(p["plays"]), fmt(p["baseline_median_plays"]), f"<b>{p['rel_plays']:.1f}x</b>")
            for p in sorted([p for p in reels if (p["baseline_n_same_format"] or 0) >= 3 and p["rel_plays"]], key=lambda p: -p["rel_plays"])[:10]], (4, 5, 6))
cl = [c for c in creators.values() if num(c["median_reel_plays_per_follower_proxy"])]
A3 = table(["Creator", "Followers", "Median reel plays", "Plays per follower"],
           [[E(c["creator"]), fmt(num(c["followers_14oct"])), fmt(num(c["median_reel_plays"])), f"{num(c['median_reel_plays_per_follower_proxy']):.2f}"]
            for c in sorted(cl, key=lambda c: -num(c["median_reel_plays_per_follower_proxy"]))[:10]], (1, 2, 3))
E1 = table(base + ["Likes", "Plays", "Likes / 1k plays"], [row(p, fmt(p["likes"]), fmt(p["plays"]), fmt(p["likes_per_1k_plays"])) for p in sorted([p for p in big if p["likes_per_1k_plays"]], key=lambda p: -p["likes_per_1k_plays"])[:8]], (4, 5, 6))
E2 = table(base + ["CTA", "Comments", "Plays", "Comments / 1k plays"], [row(p, chip(p["cta"].replace("_", " "), "tint" if p["cta"] == "comment_keyword" else ""), fmt(p["comments"]), fmt(p["plays"]), fmt(p["comments_per_1k_plays"])) for p in sorted([p for p in big if p["comments_per_1k_plays"]], key=lambda p: -p["comments_per_1k_plays"])[:8]], (5, 6, 7))
E2b = table(base + ["Comments", "Plays", "Comments / 1k plays"], [row(p, fmt(p["comments"]), fmt(p["plays"]), fmt(p["comments_per_1k_plays"])) for p in sorted([p for p in big if p["comments_per_1k_plays"] and p["cta"] not in ("comment_keyword", "join_group_or_course") and p["status"] != "giveaway"], key=lambda p: -p["comments_per_1k_plays"])[:8]], (4, 5, 6))
E3 = table(base + ["Reposts", "Plays", "Reposts / 1k plays"], [row(p, fmt(p["reposts"]), fmt(p["plays"]), fmt(p["reposts_per_1k_plays"])) for p in sorted([p for p in big if p["reposts_per_1k_plays"]], key=lambda p: -p["reposts_per_1k_plays"])[:8]], (4, 5, 6))
E4 = table(base + ["CTA", "Comments", "Likes", "vs creator median"], [row(p, chip(p["cta"].replace("_", " "), "tint" if p["cta"] == "comment_keyword" else ""), fmt(p["comments"]), fmt(p["likes"]), f"{p['rel_comments']:.1f}x" if p["rel_comments"] else "n/a") for p in sorted(nonreel, key=lambda p: -(p["comments"] or 0))[:8]], (5, 6, 7))
E5 = table(base + ["Likes", "Followers", "Likes / 1k followers"], [row(p, fmt(p["likes"]), fmt(p["followers_14oct"]), fmt(p["likes_per_1k_followers_proxy"])) for p in sorted([p for p in nonreel if p["likes_per_1k_followers_proxy"]], key=lambda p: -p["likes_per_1k_followers_proxy"])[:8]], (4, 5, 6))
cp5 = [p for p in CP if p["comments_sampled"] >= 5]
C1 = table(["Creator", "Post", "Topic", "Sampled", "Intent", "Per 100", "Keyword req."],
           [[E(p["creator"]), ig(p["post_code"]), topic(p, 54), fmt(p["comments_sampled"]), f"<b>{intent(p)}</b>", f"{intent(p) * 100 / p['comments_sampled']:.0f}", fmt(p["cmt_keyword_request"])]
            for p in sorted(cp5, key=lambda p: (-intent(p), -intent(p) / p["comments_sampled"]))[:10]], (3, 4, 5, 6))
C2 = table(["Creator", "Post", "Topic", "Sampled", "Keyword requests", "Post total comments"],
           [[E(p["creator"]), ig(p["post_code"]), topic(p, 54), fmt(p["comments_sampled"]), f"<b>{fmt(p['cmt_keyword_request'])}</b>", fmt(p["comments"])]
            for p in sorted(cp5, key=lambda p: -(p["cmt_keyword_request"] or 0) / p["comments_sampled"])[:10]], (3, 4, 5))
C3 = table(["Creator", "Post", "Topic", "Sampled", "Substantive", "Per 100", "Help requests"],
           [[E(p["creator"]), ig(p["post_code"]), topic(p, 54), fmt(p["comments_sampled"]), f"<b>{subst(p)}</b>", f"{subst(p) * 100 / p['comments_sampled']:.0f}", fmt(p["cmt_practical_help_request"])]
            for p in sorted([p for p in cp5 if p["comments_sampled"] >= 10], key=lambda p: -subst(p) / p["comments_sampled"])[:10]], (3, 4, 5, 6))


def board(title, note, body):
    return f'<div class="lb-card is-flush rp-board"><div class="rp-board-head"><h4>{title}</h4><p class="lb-note">{note}</p></div>{body}</div>'


TABS = [
    ("attention", "Attention", board("A1 · Highest raw plays", "Reels, recent sample. Plays are not unique reach.", A1)
     + board("A2 · Plays vs the creator's own median", "Only creators with at least 3 sample reels. The fairest comparison across account sizes.", A2)
     + board("A3 · Median reel plays per follower", "Proxy: followers are not exposure. Lowest in sample: daniel.gabbai, 0.04.", A3)
     + '<p class="lb-note">Watch time, retention and completion: unavailable for every post.</p>'),
    ("engagement", "Engagement", board("E1 · Likes per 1,000 plays", "Reels with at least 2,000 plays. Likes hidden on 41 sample posts.", E1)
     + board("E2 · Comments per 1,000 plays, all CTAs", "Comment-word CTAs dominate this list by design.", E2)
     + board("E2b · Comments per 1,000 plays, no comment-word CTA or giveaway", "Organic conversation only.", E2b)
     + board("E3 · Reposts per 1,000 plays", "Public repost count. DM shares are not public.", E3)
     + board("E4 · Carousels and images: most comments", "Comment ratio is against the creator's own median.", E4)
     + board("E5 · Carousels and images: likes per 1,000 followers", "Proxy.", E5)
     + '<p class="lb-note">Saves and DM shares: unavailable.</p>'),
    ("consideration", "Consideration", board("C1 · Purchase-intent comments", "Explicit intent + product or price questions + self-reported purchases. Posts with at least 5 sampled comments, Instagram's ranked order.", C1)
     + board("C2 · Requests for an offered link, file or list", "Keyword requests: a request for the creator's offer, not spontaneous intent.", C2)
     + board("C3 · Substantive discussion", "Identification + personal experience + help requests. Posts with at least 10 sampled comments.", C3)
     + '<p class="lb-note">Profile visits, follows, link clicks, CTR and qualified DMs: unavailable.</p>'),
    ("purchase", "Activation and purchase", '<div class="lb-empty"><b>No leaderboard is possible.</b><br>No post, creator or topic in this study has attributed sessions, books started, previews, checkouts or orders. The only purchase figures tied to a creator are self-reported (<a href="#evidence-e12">E12</a>). Do not call any post here "highest converting".</div>'),
]
tabbar = '<div class="lb-tabs" role="tablist">' + "".join(
    f'<button role="tab" data-tab="{k}" aria-selected="{"true" if i == 0 else "false"}">{E(t)}</button>' for i, (k, t, _) in enumerate(TABS)) + "</div>"
panes = "".join(f'<div class="rp-pane lb-stack" data-pane="{k}" {"" if i == 0 else "hidden"}>{b}</div>' for i, (k, _, b) in enumerate(TABS))
V["kpis"] = head("KPI leaderboards", "Findings", "One ranking per KPI, never a combined score. Recent sample only, Instagram only, reels kept apart from carousels and images.") + \
    f'<details class="lb-card rp-details"><summary><b>What each funnel stage can and cannot show</b><span class="lb-dim"> · evidence boundary</span></summary>{boundary}<p class="lb-note">Missing means unknown, not zero.</p></details>' + \
    f'<div class="rp-tabs">{tabbar}{panes}</div>'

# Content patterns -------------------------------------------------------
ATT = [("Before/after demos", 3.08, "7 reels · 6 creators"), ("Potty and toilet skills", 3.43, "5 reels · 5 creators"),
       ("Family outings", 1.91, "13 reels"), ("Collab (co-authored) reels", 1.61, "12 reels · 11 creators"),
       ("Day vlogs", 1.54, "12 reels · 10 creators"), ("Gan start", 1.36, "9 reels"), ("Humour and entertainment", 1.25, "49 reels · 18 creators"),
       ("Development and behaviour", 1.00, "50 reels · 26 creators"), ("Everyday parenting", 1.00, "40 reels · 26 creators"),
       ("All LumeBook buying occasions", 0.93, "82 reels · 33 creators"), ("Books and reading", 0.90, "11 reels · 10 creators"),
       ("Product reviews", 0.76, "19 reels · 10 creators"), ("First grade", 0.72, "9 reels · 4 creators"), ("Birthday", 0.70, "6 reels")]
DISC = [("Pregnancy", 36.9, 1.0, 0, "5"), ("Everyday parenting", 20.6, 1.4, 18, "14"), ("Humour", 18.5, 0.0, 0, "15"),
        ("Behaviour and emotions", 11.8, 1.6, 47, "15"), ("Gan start", 7.4, 2.5, 38, "23"), ("Potty and diapers", 7.3, 8.9, 33, "11"),
        ("Reading and books", 6.9, 9.8, 53, "6"), ("Development and learning", 6.5, 2.6, 70, "23"), ("First grade", 5.1, 2.0, 80, "9"), ("Birthday", 0.0, 1.0, 11, "5")]
PATTERNS = [
    ("Comment-word CTAs lift comments", "In 18 of the 20 creators who use them, and they turn most comments into requests for the offer.", "E3"),
    ("A useful object in use draws \"where do I buy\"", "On posts by 5 different creators, even with no call to action at all.", "E4"),
    ("Professional book lists draw hundreds of keyword requests", "tal_strul, hilla_gover_slp, topaz_meir_slp, hen.kalimian.kids.", "E3, E5"),
    ("Commercial posts trade likes for comments", "Sponsored and own-product reels get about half the likes per 1,000 plays of organic reels.", "E9"),
    ("Price and real proof are rarely shown", "Price visible on 7 of 469 posts; a child's reaction is the proof on 17.", "E10"),
    ("Big hits are not buying templates", "The strong post out-talked the ordinary one on buying intent in only 7 of 40 creators.", "E11"),
]
V["content"] = head("What the content does", "Findings", "Topic, format and call to action compared inside each creator's own feed, so audience size cancels out.") + f"""
<div class="lb-grid" style="--min:26rem">
  <div class="lb-card"><div class="lb-card-head"><h3>What travels</h3>{chip("median plays vs creator median", "outline")}</div>
    {hbars([(E(l), v, E(s)) for l, v, s in sorted(ATT, key=lambda a: -a[1])], maxv=3.6, fmtv=lambda v: f"{v:.2f}x", marker=1.0)}
    <p class="lb-note">The line marks 1.0x, the creator's normal. Cells under 10 reels are directions, not findings.</p></div>
  <div class="lb-card"><div class="lb-card-head"><h3>What gets talked about</h3>{chip("per 100 sampled comments", "outline")}</div>
    {table(["Topic", "Posts", "Relate + help", "Buying intent", "Keyword req."], [[E(t), n, f"{s:.1f}", f"<b>{i:.1f}</b>" if i >= 5 else f"{i:.1f}", f"{k}"] for t, s, i, k, n in DISC], (1, 2, 3, 4))}
    <p class="lb-note">Pregnancy and humour make people relate; potty and books make them ask about products.</p></div>
</div>
<section class="lb-section"><div class="lb-section-head"><h3>Patterns that repeat across creators</h3></div>
<div class="lb-grid cols-3">{"".join(f'<div class="lb-card"><h4>{E(t)}</h4><p class="lb-muted lb-small">{E(b)}</p><a class="lb-xs" href="#evidence-{ev.split(",")[0].lower()}">Evidence {ev}</a></div>' for t, b, ev in PATTERNS)}</div></section>
<div class="lb-grid cols-2">
  <div class="lb-card is-quiet"><h3>Isolated outliers</h3><p class="lb-note">Do not build on these alone.</p><ul class="lb-list">
    <li><span>Morning-mantra reel, 1,205,190 plays, 209x the creator's median (April, 180-day window)</span><span class="lb-meta">nataliegaash · {ig("DXvwsYVN0lN")}</span></li>
    <li><span>Crisis-call reel, 3.5M plays and 0 comments, possibly a re-share</span><span class="lb-meta">yaffa_michaela_zukerman · {ig("DbFft0dN8PE")}</span></li>
    <li><span>Sponsored pan reel, 277,026 plays and 125 likes: a like rate consistent with paid promotion (inference)</span><span class="lb-meta">baryona · {ig("DcjCHEkMWTR")}</span></li></ul></div>
  <div class="lb-card is-quiet"><h3>Older breakouts</h3><p class="lb-note">96 posts, analysed separately from the recent sample.</p>
    <p class="lb-small">Mostly humour (25) and reassurance (18); text on video (21) and hands-on demos (19). 10 of 96 are LumeBook-relevant: 4 are toilet or diaper skills (orli.parenthood's clothespin exercise, 171K plays, 52x) and 3 are gan or first-grade transitions with a keyword offer (hen.kalimian.kids 1,379 and 1,401 comments; tal_strul's gan book list 1,389).</p>
    <p class="lb-small"><b>Format note:</b> 14 of 24 transcribed deep-dive reels have no speech at all. A creator brief should not depend on a talking head.</p></div>
</div>"""

# Audience voice ---------------------------------------------------------
LABELS = [("cmt_generic_praise", "Generic praise"), ("cmt_keyword_request", "Keyword requests"), ("cmt_personal_experience", "Personal experience"),
          ("cmt_identification", "Identification"), ("cmt_practical_help_request", "Help requests"), ("cmt_product_or_price_question", "Product or price questions"),
          ("cmt_objection", "Objections"), ("cmt_tag_or_share", "Tag or share"), ("cmt_creator_reply", "Creator replies"),
          ("cmt_explicit_buying_intent", "Explicit buying intent"), ("cmt_purchase_report", "Self-reported purchase")]
mix = hbars([(E(l), CLASS_TOT[k] * 100 / TOTAL_CMT, f"{CLASS_TOT[k]:,}") for k, l in LABELS], maxv=50, fmtv=lambda v: f"{v:.1f}%")
QUOTES = [
    ("Close to buying", [("איפה קונים?", "Where do you buy?", "knafaim.ot_by_noy", "DdWglWIKur-"),
                         ("וואוו רעיון מעולה איפה קונים?", "Great idea, where do you buy?", "lital_magnezi", "Dd5sq3TI1I5"),
                         ("אשמח להמלצות למתוקי בן 3", "I'd love picks for my sweetie aged 3", "tal_strul", "DdwREvSCJg2"),
                         ("אני חייבת את קווין הקואלה ל[שם]", "I must get this book for [name]", "books_are_friends_slp", "DbtoJF_iDU1")]),
    ("Asking for help", [("מתי נכון לגמול? ואיך להשתמש נכון?", "When is the right time to wean?", "topaz_meir_slp", "Db6Bi-nMywx"),
                         ("יש לכם המלצות לאיזה ספרים כדאי להקריא בגיל הזה?", "Which books should we read at this age?", "hilla_gover_slp", "Dar4kTwCMJV"),
                         ("איפה אפשר לרכוש ואיזה ספרים מומלצים ?", "Where can you buy, which books?", "hilla_gover_slp", "Dar4kTwCMJV")]),
    ("Relating, not buying", [("גם הבת שלי ידעה", "My daughter knew too", "ima.shir", "DdtDs1WNRDp"),
                              ("מזדהה", "I relate", "natallyaharon", "DdtOB6FNczn"),
                              ("סבתא שרוצה להעשיר את מגירת הצעצועים", "A grandmother who wants to enrich the toy drawer", "knafaim.ot_by_noy", "DdWglWIKur-")]),
]
qcols = "".join(
    f'<div class="lb-card"><h3>{E(g)}</h3><div class="lb-stack">' + "".join(
        f'<figure class="rp-q"><blockquote>{he(h)}</blockquote><figcaption>{E(en)} · <span class="lb-dim">{E(c)}</span> {ig(code, "post")}</figcaption></figure>'
        for h, en, c, code in qs) + "</div></div>" for g, qs in QUOTES)
V["voice"] = head("Audience voice", "Findings", f"{TOTAL_CMT:,} comments on 184 posts, up to 30 per post in Instagram's ranked order, read and classified in Hebrew.") + f"""
<div class="lb-grid cols-4">
  {stat("Purchase-intent comments", f"{INTENT_TOT}", f"{INTENT_TOT * 100 / TOTAL_CMT:.1f}% of all sampled")}
  {stat("Explicit buying intent", str(CLASS_TOT["cmt_explicit_buying_intent"]), "plus " + str(CLASS_TOT["cmt_purchase_report"]) + " self-reported purchases")}
  {stat("Keyword requests", f"{CLASS_TOT['cmt_keyword_request']:,}", "requests for an offered link or file")}
  {stat("Gift mentions", "2", "and 5 self-identified grandparents")}
</div>
<div class="lb-grid" style="--min:26rem">
  <div class="lb-card"><div class="lb-card-head"><h3>What the comments are</h3>{chip("share of comments", "outline")}</div>{mix}
    <p class="lb-note">Instagram's ranking chose which comments were sampled; long tails of keyword comments may be under-represented and creator-friendly comments over-represented.</p></div>
  <div class="lb-card"><h3>Objections seen</h3><p class="lb-small">Objections are about the advice, not about products: toilet-training method (5 comments), teaching reading before first grade (1), screen-time rules (7). The only product objection: an item was cheaper elsewhere.</p>
    <div class="lb-callout"><b>Not seen yet</b><span class="lb-small">No comments about delivery, personalisation quality or trust in a personalised book, because no sampled post sells one. MeBook's creator posts did draw price, delivery-time and how-to-order questions (3 Oct teardown).</span></div></div>
</div>
<div class="lb-grid cols-3 rp-quotes">{qcols}</div>
<p class="lb-note">Quotes at most 12 words, children's names replaced by [שם], no usernames. Each was re-read in the raw comment data.</p>"""

# Buyer segments -----------------------------------------------------------
ICP = [
    ("Parents facing a weaning step", "Supported", "success", "Mother or both parents → child 1 to 3 · pacifier, diapers",
     "ביי ביי מוצץ 86 orders, נפרדים מהטיטולים 66", "Pacifier and potty posts draw timing questions and keyword requests; toilet-skill demos are among the biggest outliers.", "Interest supported; purchase unknown"),
    ("Parents before a transition", "Supported", "success", "Mother or both parents → child 3 to 6 · gan start, first grade",
     "שלום כיתה א' 57; gan books in the catalogue", "First-grade readiness offers drew 1,379 and 1,401 comments; book lists for the move draw hundreds of requests.", "Interest supported; purchase unknown"),
    ("Expecting parents with an older child", "Partly", "info", "Mother → older sibling 2 to 6 · new sibling",
     "אח חדש + אחות חדשה 132", "Pregnancy posts draw the most identification (36.9 per 100) but almost no product talk.", "Attention supported; purchase link uncertain"),
    ("Birthday gift buyers", "Uncertain", "warning", "Parent → child 1 to 8 · birthday",
     "Birthday book is the top seller (262)", "Birthday posts are tributes with greetings; no gift conversation.", "Strong in sales, absent in creator conversation"),
    ("Grandparents and relatives", "Uncertain", "warning", "Grandmother, aunt → grandchild · birthday, holidays",
     "Meta credits women 55 to 64 with 17 of 62 ad purchases (model attribution)", "5 self-identified grandparents in 2,982 comments, asking practical questions; grandparent comedy draws banter.", "Present in audiences; buying role unknown"),
    ("Fathers", "Uncertain", "warning", "Father → any child",
     "Men 25 to 34: 8 Meta purchases on ₪112 (too small)", "Dad creators get the highest likes per play (almaanddad 40 to 64 per 1,000) but comments are praise.", "No buying signal seen"),
    ("Gan teachers for a class", "B2B", "tint", "Educator → class of 3 to 6",
     "B2B tiers on the site; no B2B split seen", "Gan-teacher creators speak mostly to other teachers, who request files and ask where to buy classroom items.", "An audience for the kindergarten offer, not B2C"),
    ("\"Only young moms buy\"", "Contradicted", "danger", "As a sole assumption",
     "The age spread of Meta purchases (12 Oct note)", "Not testable here.", "Drop as a sole assumption"),
]


def he_inline(t):
    return inline(t)


V["icp"] = head("Buyer segments", "Findings", "The buyer and the child are different people. The store records the child (name, gender; age is mostly a default value), not the buyer's relation to the child.") + \
    '<div class="lb-grid cols-2">' + "".join(
        f'<div class="lb-card rp-icp"><div class="lb-card-head"><h3>{E(n)}</h3>{chip(s, c)}</div><p class="lb-dim lb-small">{E(who)}</p>'
        f'<dl class="lb-kv"><dt>Sales</dt><dd>{he_inline(sales)}</dd><dt>Content</dt><dd>{E(cont)}</dd><dt>Verdict</dt><dd><b>{E(v)}</b></dd></dl></div>'
        for n, s, c, who, sales, cont, v in ICP) + "</div>" + \
    '<p class="lb-note">Sales column: internal admin screenshots of 12 Oct (docs/lumebook-sales-data-decisions-2026-10-12.md). Meta segments are Meta\'s attribution, not verified buyers.</p>'

# Creators -----------------------------------------------------------------
STATUS_KIND = {"process": "success", "book": "success", "sent": "info", "due": "warning", "declined": "danger", "not contacted": "", "no status": ""}
GROUPS = [
    ("A", "Professionals with LumeBook occasions and a working comment-word funnel", "Best fit for a book-list or how-to post with a personal link.", [
        ("topaz_meir_slp", "3.25 plays per follower; comment word on 10 of 12 posts; pacifier posts with weaning-timing questions; book-picks reel with 112,928 plays"),
        ("hen.kalimian.kids", "First-grade readiness; keyword offers drew 1,379 and 1,401 comments; already promoted a children's book via \"ספר\""),
        ("hilla_gover_slp", "Books-by-age list, 882 comments; parents ask her which books to read and where to buy"),
        ("orli.parenthood", "8 of 12 recent posts on potty or gan start; help requests and objections show an engaged audience"),
        ("tal_strul", "Gan-transition book list, 1,389 comments; bedtime books with a publisher; asked for picks by age"),
        ("knafaim.ot_by_noy", "Product lists draw \"where do I buy\" and a grandmother's question; 1.9 plays per follower")]),
    ("B", "Parents living a LumeBook moment now", "New sibling: lived moments get the deepest identification.", [
        ("ima.shir", "Pregnant with a third child; 7 of 12 posts are a pregnancy diary; 46 of 85 sampled comments are identification or stories"),
        ("imkassandra__", "New baby, three older siblings; 7.87 plays per follower, the highest in the sample"),
        ("lotanelias", "Three kids born in three years; keyword offers reach thousands of comments; already uses a personal discount code")]),
    ("C", "Book voices", "Small but on-topic.", [
        ("books_are_friends_slp", "Barter batch; the only explicit want for a named children's book in the sample"),
        ("yaffa_michaela_zukerman", "Sells her own books to her audience (self-reported 530 families, 4,000+ homes); sensitive topic, check fit first")]),
    ("D", "Gan teachers, for the kindergarten (B2B) offer", "They mostly reach other teachers.", [
        ("lital_magnezi", "Her toilet-light post drew 16 of 30 \"where do I buy\""),
        ("racheli.h.m", "Gan adjustment and first-day posts; teacher and parent audience"),
        ("_shirley_unger_kids_activities", "Autumn books post: 9 of 13 comments were product questions"),
        ("etti_haft", "Teacher kits and file funnels; barter batch")]),
]


def ccard(h, why):
    c = creators[h]
    stx = c["outreach_status_14oct"]
    extra = chip("barter batch", "accent") if c["barter_batch"] == "True" else ""
    mp = num(c["median_reel_plays"])
    return (f'<div class="lb-card rp-creator"><div class="lb-card-head"><a class="rp-handle" href="https://www.instagram.com/{E(h)}/" target="_blank" rel="noopener">@{E(h)}</a>'
            f'<span class="lb-row">{chip(stx, STATUS_KIND.get(stx, ""))}{extra}</span></div>'
            f'<div class="rp-mini"><span><b>{fmt(num(c["followers_14oct"]))}</b> followers</span><span><b>{fmt(mp) if mp else "n/a"}</b> median reel plays</span>'
            f'<span><b>{c["posts_high_relevance"]}</b>/12 high-relevance</span></div><p class="lb-small lb-muted">{inline(why)}</p></div>')


ctabs = '<div class="lb-tabs" role="tablist">' + "".join(
    f'<button role="tab" data-tab="g{g}" aria-selected="{"true" if i == 0 else "false"}">{g} · {E(t.split(",")[0].split(" with")[0].split(" living")[0].split(" for")[0])}</button>'
    for i, (g, t, _, _) in enumerate(GROUPS)) + "</div>"
cpanes = "".join(
    f'<div class="rp-pane lb-stack" data-pane="g{g}" {"" if i == 0 else "hidden"}><div><h3>{E(t)}</h3><p class="lb-note">{E(sub)}</p></div>'
    f'<div class="lb-grid cols-2">{"".join(ccard(h, w) for h, w in lst)}</div></div>'
    for i, (g, t, sub, lst) in enumerate(GROUPS))
V["creators"] = head("Creators to test first", "Actions", "Grouped by the kind of evidence behind them, not by a combined score. Status is the creator map's outreach state on 14 Oct.") + \
    f'<div class="rp-tabs">{ctabs}{cpanes}</div>' + \
    '<div class="lb-callout info"><b>Not first for sales tests</b><span class="lb-small">High reach but no buying talk: rivki_shashar, hatravelers_, savta_ziona_official, adar_azulay, edenmarlel00, natallyaharon, almaanddad. They may suit reach-only posts later. mor_knoll is a competitor conflict and posted no book content in the recent sample.</span></div>'

# Concepts -----------------------------------------------------------------
CONCEPTS = [
    ("Professional book list for a transition, with one personalised pick", "5 ספרים לפני כיתה א\nואחד שהילד שלכם בתוכו", "Gan / first grade", "Medium for requests · low for purchase",
     [("Buyer", "Parents of 3 to 6 year olds before gan or first grade (hypothesis)"), ("Format", "Speech therapist or parent guide: 5 picture books plus 1 where the child is the hero; comment word for the list"),
      ("Product", "שלום כיתה א' or a gan book"), ("Proof", "The creator's credential; show real printed pages"), ("CTA", "Comment a word; the DM carries the creator's ambassador link"),
      ("KPI", "Books started via the link per 1,000 accounts reached")], ["DZphMo0CAUb", "Da0n_qzACqS", "Dc6VXOdMWOv", "DdegHrWjvH9"]),
    ("Pacifier timing Q&A", "מתי נפרדים מהמוצץ\nומה עוזר בלילה הראשון", "Pacifier", "Medium-low",
     [("Buyer", "Parents of 1 to 3 year olds planning to drop the pacifier"), ("Format", "SLP reel answering the questions her own comments asked"), ("Product", "ביי ביי מוצץ"),
      ("Proof", "A professional answer to \"when is it time\"; no promises about results"), ("CTA", "Comment word for a short guide plus the link"), ("KPI", "Books started for the pacifier title")], ["Db6Bi-nMywx"]),
    ("One toilet skill, shown", "תרגיל אחד קטן\nלפני שנפרדים מהטיטול", "Potty", "Medium for attention · low for purchase",
     [("Buyer", "Parents of 2 to 3 year olds starting diaper weaning"), ("Format", "Hands-on demo reel, the format with the biggest outliers; the book is the story read before"), ("Product", "נפרדים מהטיטולים"),
      ("Proof", "The demo itself; the professional answers \"my child isn't ready\""), ("CTA", "Save, plus link in story"), ("KPI", "Plays vs the creator's median, then link sessions")], ["DdUFGI3oO8T", "DX6Ij0HIzlj", "Db2tjBCoLP3"]),
    ("Telling the older child about the baby", "איך מספרים לגדולה\nשמגיע אח קטן", "New sibling", "Medium for engagement · low for purchase",
     [("Buyer", "Expecting mother with a 2 to 6 year old"), ("Format", "An episode of a pregnancy diary by a creator who is pregnant now"), ("Product", "אח חדש / אחות חדשה"),
      ("Proof", "The older child's reaction on camera, with consent"), ("CTA", "\"How did you tell yours?\" plus a personal link in story"), ("KPI", "Books started for the sibling titles")], ["DdtDs1WNRDp", "DdwlAMSNv5S"]),
    ("What went in the gan bag", "מה שמנו בתיק\nלשבוע הראשון בגן", "Gan start", "Medium",
     [("Buyer", "Parents in the first weeks of gan"), ("Format", "Object-by-object reel, the book among practical items"), ("Product", "A gan book"),
      ("Proof", "Objects shown in use; price answered on screen"), ("CTA", "Comment word for the list of links"), ("KPI", "Product questions per 100 comments, then link sessions")], ["Dd5sq3TI1I5", "DbVCNNJiFUw"]),
    ("Price and delivery, said out loud", "כמה זה עולה\nותוך כמה זמן זה מגיע", "Any", "Low (hypothesis)",
     [("Buyer", "Any parent already considering; the payment step loses about half (12 Oct note)"), ("Format", "Printed book in hand, the price with the follower discount, days to arrive, what the preview shows"),
      ("Product", "Any title"), ("Proof", "The real book; answers price, delivery and \"will it look like my child\""), ("CTA", "Personal link"), ("KPI", "Paid orders ÷ books started for the linked cohort")], []),
    ("Grandma asked what to buy", "סבתא שאלה מה לקנות לנכדה\nהנה מה שבחרנו", "Gift", "Low",
     [("Buyer", "Grandmothers and aunts, birthday or Hanukkah"), ("Format", "A parent creator films the grandmother giving the book (real family, consent)"), ("Product", "Birthday or holiday book"),
      ("Proof", "Shows how the parent helps with the photo"), ("CTA", "\"Send this to grandma\" plus a personal link"), ("KPI", "Orders through the gift-tagged link")], []),
    ("The present she opened first", "המתנה שהיא פתחה ראשונה\nביום הולדת 4", "Birthday", "Low (no proven pattern)",
     [("Buyer", "Parents planning a 3rd or 4th birthday"), ("Format", "Party reel ending with the child seeing herself in the book"), ("Product", "Birthday book, the top seller"),
      ("Proof", "The child's reaction; order-by date in the caption"), ("CTA", "Personal link"), ("KPI", "Product questions per 100 comments and books started")], ["Dc0QYruIchn", "Dd_6ZOfDjxd"]),
    ("Reading aloud, page by page", "3 שאלות לשאול\nעל כל עמוד בספר", "Reading", "Medium",
     [("Buyer", "Parents of 1 to 4 year olds who ask what to read"), ("Format", "SLP shows three questions to ask on any page, using the child's own book"), ("Product", "Any title"),
      ("Proof", "A real child answering; handles \"my child won't sit for a book\""), ("CTA", "Save, comment word for a list by age"), ("KPI", "Saves (Insights) and keyword requests")], ["Dar4kTwCMJV", "Dc6VXOdMWOv"]),
    ("The gan gate, from the parent's side", "אני עדיין בשער של הגן\nוהיא כבר בפנים", "Gan start", "Medium for reach · low for purchase",
     [("Buyer", "Parents in gan adjustment"), ("Format", "Relatable humour reel (the reach format); product only in the caption"), ("Product", "A gan book, soft"),
      ("Proof", "None needed"), ("CTA", "Tag a partner; link in story"), ("KPI", "Plays vs the creator's median, link sessions as a check")], ["DcrLtsFqzc0", "DW5ze--jd01"]),
]


def conf_kind(c):
    return "success" if c.startswith("Medium") and "low" not in c.lower() else ("warning" if "Medium" in c else "")


ccards = "".join(
    f'<article class="lb-card rp-concept" data-occ="{E(occ)}"><div class="lb-card-head"><span class="rp-n">{i}</span><span class="lb-row">{chip(occ, "accent")}{chip(conf, conf_kind(conf))}</span></div>'
    f'<h3>{E(t)}</h3><blockquote class="rp-hook" dir="rtl" lang="he">{"<br>".join(E(l) for l in hook.splitlines())}</blockquote>'
    f'<dl class="lb-kv">{"".join(f"<dt>{E(k)}</dt><dd>{inline(v)}</dd>" for k, v in kv)}</dl>'
    + (f'<p class="lb-xs lb-dim">Examples: {" · ".join(ig(c) for c in ex)}</p>' if ex else "") + "</article>"
    for i, (t, hook, occ, conf, kv, ex) in enumerate(CONCEPTS, 1))
occs = sorted({c[2] for c in CONCEPTS})
filt = '<div class="lb-segmented rp-filter" role="group" aria-label="Filter by occasion"><button aria-pressed="true" data-f="">All</button>' + "".join(
    f'<button aria-pressed="false" data-f="{E(o)}">{E(o)}</button>' for o in occs) + "</div>"
V["concepts"] = head("Ten content concepts", "Actions", "Each with a buyer hypothesis, a Hebrew hook, the product link, the proof or objection to handle, the CTA and the KPI to judge it by.") + \
    f'<div class="lb-callout"><span class="lb-small">Hebrew hooks are written in the fallback voice (lumebook-hebrew-voice: 12 of 15 samples), addressed to parents in the plural, and pass <code>voice_lint.py</code>. In creator posts the creator rewrites them in her own words; LumeBook\'s own carousels never name the brand or a title.</span></div>' + \
    f'<div class="lb-toolbar">{filt}</div><div class="lb-grid cols-2 rp-concepts">{ccards}</div>'

# Tests --------------------------------------------------------------------
TESTS = [
    ("T1", "Professional book list", True,
     "A professional's transition book list with one personalised pick (concept 1 or 2) yields more books started per 1,000 reached than a single-product post.",
     "topaz_meir_slp first, then hen.kalimian.kids or hilla_gover_slp", "T3 and T4 single-product posts, normalised per 1,000 accounts reached",
     "Books started via the link within 7 days", "Ambassador link + utm_content=<shortcode>; keyword count on day 7; Insights screenshot (reach, saves, shares, link taps)",
     "7 days (link memory); final after the 14-day hold", "Keep the format with a creator if a post produces at least 1 paid printed order and at least 10 books started per 10,000 reached; otherwise change format before changing creator."),
    ("T2", "Comment word vs link sticker", False,
     "A comment word with the link in a DM yields more books started per 1,000 plays than a story link sticker, not just more comments.",
     "topaz_meir_slp and orli.parenthood, 2 posts each", "Same creator, same concept, alternating arms",
     "Books started per 1,000 plays", "utm_content=dm-<shortcode> vs story-<date>", "7 days per post",
     "Adopt the arm with at least 1.5x the books started per 1,000 plays over 2 pairs; otherwise treat them as equal and use the creator's habit."),
    ("T3", "Lived moment vs expert", False,
     "A parent living the new-sibling moment yields more sibling-book starts than an expert talking about it.",
     "ima.shir, imkassandra__ vs nataliegaash", "Between creators, normalised per 1,000 reached",
     "Sibling-title books started", "utm_term=t3-lived / t3-expert", "7 days",
     "Prefer lived-moment creators for sibling titles if they produce at least 2x the starts per 1,000 reached."),
    ("T4", "Price shown vs not", False,
     "Showing price and delivery time raises paid orders per book started.",
     "Two creators posting the same concept, one with price and delivery on screen", "Arm A vs arm B, each vs the store-wide paid ÷ started rate",
     "Paid orders ÷ books started (attributed)", "utm_term=t4-price / t4-noprice", "14 days",
     "Show price in every product post if the price arm's paid ÷ started is at least the store-wide rate and higher than the other arm."),
    ("T5", "Gift-giver framing", False,
     "Grandparent framing reaches buyers that parent framing does not.",
     "One parent creator with a real grandparent on camera, plus LumeBook's weekly gift-giver post", "Gift-tagged link vs parent-tagged link",
     "Books started and paid via the gift link, plus \"who is it for\" answers in the post-purchase WhatsApp message", "utm_term=t5-gift / t5-parent; one WhatsApp question after purchase", "14 days",
     "Continue the weekly gift-giver post after 4 weeks only if the gift link's starts per 1,000 sessions are at least those of the parent link."),
]
tcards = "".join(
    f'<article class="lb-card rp-test {"is-accent" if first else ""}"><div class="lb-card-head"><span class="lb-row"><span class="rp-tid">{tid}</span><h3>{E(name)}</h3></span>'
    + (chip("Run first", "tint") if first else "") + f'</div><p class="rp-hyp">{E(hyp)}</p>'
    f'<dl class="lb-kv"><dt>Who</dt><dd>{E(who)}</dd><dt>Compared with</dt><dd>{E(comp)}</dd><dt>Primary outcome</dt><dd><b>{E(out)}</b></dd>'
    f'<dt>Tracking</dt><dd>{E(trk)}</dd><dt>Window</dt><dd>{E(win)}</dd></dl>'
    f'<div class="rp-rule"><span class="lb-chip warning">Proposed rule</span><span class="lb-small">{E(rule)}</span></div></article>'
    for tid, name, first, hyp, who, comp, out, trk, win, rule in TESTS)
V["tests"] = head("Five tests for the next four weeks", "Actions · 15 Oct to 11 Nov 2026", "All thresholds are proposed test criteria, not verified baselines.") + """
<div class="lb-card is-quiet"><h4>Before any test</h4><ol class="rp-steps">
<li>Confirm the ambassador link format with Yossi, and whether extra UTMs survive it.</li>
<li>Enrol each test creator in the store's ambassador program.</li>
<li>Get read access to the ambassador ledger and to <code>acquisitionAttribution</code> per order.</li>
<li>Fix or confirm <code>@lumebookai</code>. Creator books for Hanukkah are due 10 Nov.</li></ol>
<p class="lb-note">The only verified funnel numbers are store-wide: 21.7% of people who start a book pay within 7 days; 85 of 202 orders that reached payment were bought in the last 30 days (Mixpanel, undercounted).</p></div>
<div class="lb-grid cols-2 rp-tests">""" + tcards + "</div>"

# Measurement --------------------------------------------------------------
TRACK = [
    ("Acquisition attribution", "On landing the site stores UTM source, medium, campaign, content and term, fbclid, gclid and the landing path as first and last touch. When a book is created it sends that record as acquisitionAttribution with a visitorId.",
     "Whether the admin stores and reports it per order. The 12 Oct note says the link is not saved; the code sends it, so the gap may be in reporting."),
    ("Consent gate", "Attribution, Mixpanel, Meta pixel and GTM run only when the visitor accepts analytics cookies.", "The share of visitors who accept."),
    ("Funnel events", "Mixpanel: page viewed, contents viewed, items added, checkout started, order created. Meta pixel: PageView, ViewContent, AddToCart, InitiateCheckout, Purchase.", "Whether \"preview completed\" is its own event."),
    ("Ambassador and recommender programs", "Live /IL/he/ambassadors and /IL/he/recommend. ₪30 per printed book split between follower discount (₪0 to ₪30) and commission; link remembers the visitor 7 days; 14-day hold; dashboard of books, pending, final, cancelled sales and payouts.",
     "Whether any map creator is enrolled; the link format; whether digital orders count; how ₪30 relates to the 25% in facts.json (₪30 is 25.2% of ₪119)."),
]
FUNNEL = [("Exposure", "Reach, plays, average watch time", "Creator Insights, day 7", "Private to creator"),
          ("Engagement", "Likes, comments, saves, shares, reposts", "Public + Insights", "Partly public"),
          ("Consideration", "Link taps, profile visits, keyword comments, DMs", "Insights + keyword count", "Private / public"),
          ("Session", "Landing views with the UTMs", "Mixpanel page_viewed", "Exists, not read"),
          ("Book started", "Orders created with utm_campaign = handle", "Store order table", "Exists, reporting unknown"),
          ("Preview", "Preview viewed", "Mixpanel or store", "Unknown if tracked"),
          ("Checkout", "checkout_started, payment-step arrivals", "Mixpanel + store", "Exists"),
          ("Purchase", "Paid orders credited to the link (printed, 7 days) and paid orders with matching UTMs", "Ambassador ledger + orders", "Exists, not read"),
          ("Economics", "Revenue, AOV, revenue per session, cost per purchase, contribution", "Orders + print cost", "Print cost unknown")]
fun = "".join(
    f'<li class="rp-fstep"><span class="rp-fn">{i}</span><div><b>{E(s)}</b><span class="lb-small lb-muted">{E(m)}</span><span class="lb-xs lb-dim">{E(src)}</span></div>{chip(stx, "success" if stx.startswith("Exists") and "not" not in stx and "unknown" not in stx else ("info" if "Exists" in stx else ("warning" if "Partly" in stx or "public" in stx else "")))}</li>'
    for i, (s, m, src, stx) in enumerate(FUNNEL, 1))
V["measure"] = head("Measurement plan", "Actions", "The store already has creator attribution in its code. The plan is to switch it on for the test creators and read it every Monday.") + \
    '<div class="lb-grid cols-2">' + "".join(
        f'<div class="lb-card"><h3>{E(t)}</h3><p class="lb-small">{E(w)}</p><div class="lb-callout info"><b>Unknown</b><span class="lb-small">{E(u)}</span></div></div>' for t, w, u in TRACK) + "</div>" + f"""
<div class="lb-grid" style="--min:26rem">
  <div class="lb-card"><h3>Funnel, step by step</h3><ol class="rp-funnel">{fun}</ol></div>
  <div class="lb-stack">
    <div class="lb-card"><h3>Link format (proposed)</h3><pre class="lb-ltr">&lt;ambassador link&gt;?utm_source=instagram&amp;utm_medium=creator
&amp;utm_campaign=&lt;handle&gt;&amp;utm_content=&lt;shortcode&gt;
&amp;utm_term=&lt;test-arm&gt;</pre>
      <p class="lb-small">One link per placement: <code>bio</code>, <code>story-YYYYMMDD</code>, <code>dm-&lt;shortcode&gt;</code>. Never a code: personal link only.</p></div>
    <div class="lb-card"><h3>Weekly routine</h3><ol class="rp-steps">
      <li>Each creator post: log date, time, handle, shortcode, format, concept, link.</li>
      <li>Day 7: public counts, keyword-comment count, the creator's Insights screenshot.</li>
      <li>Monday: export orders with acquisitionAttribution and the ambassador ledger; join on campaign or ambassador; compare with daily store orders.</li></ol></div>
    <div class="lb-card is-quiet"><h3>Keep three counts apart</h3><p class="lb-small"><b>Store orders</b> (server), <b>ambassador-credited orders</b> (7-day printed rule) and <b>platform-reported purchases</b> (Meta). Never add them. Count people, sessions, books and orders separately; one buyer averages 1.40 books.</p></div>
  </div>
</div>
<div class="lb-card"><h3>Attribution limits</h3><div class="lb-grid cols-3 rp-limits">
  <div><b>Consent</b><p class="lb-small lb-muted">Visitors who decline analytics carry no UTMs; the server-side ambassador link may still credit them.</p></div>
  <div><b>7-day window</b><p class="lb-small lb-muted">A gift-giver who buys two weeks later is not credited.</p></div>
  <div><b>Cross-device</b><p class="lb-small lb-muted">Instagram's in-app browser; a purchase finished later on another device can lose the link.</p></div>
  <div><b>Printed only</b><p class="lb-small lb-muted">Digital-only orders may not be credited to ambassadors.</p></div>
  <div><b>Spill-over</b><p class="lb-small lb-muted">People who search Google later are invisible; the daily-orders comparison is the only weak check.</p></div>
  <div><b>Platform numbers</b><p class="lb-small lb-muted">Meta's purchases are modelled and overlap store orders; report them separately.</p></div>
</div></div>"""

# Unknowns -----------------------------------------------------------------
UNK = ["Whether any creator content sells LumeBook books, and how many per post. No attributed data has been read.",
       "Reach, watch time, saves, shares, profile visits and link taps for any post (creator Insights only).",
       "Whether keyword requests become link clicks, books started or orders.",
       "Who buys: the store does not record the buyer's relation to the child; Meta's age segments are model attributions.",
       "Whether the ambassador link keeps extra UTM parameters, credits digital orders, and how many creators are enrolled.",
       "Whether @lumebookai was renamed, deactivated or restricted, and since when.",
       "Whether the patterns hold on TikTok (no TikTok handles in the map) or outside these 41 creators.",
       "Whether undisclosed paid promotion inflated any of the outliers.",
       "How comments outside Instagram's top-ranked 30 differ from the sample."]
V["unknowns"] = head("What we still do not know", "Reference", "Prefer \"we do not yet know\" over unsupported certainty.") + \
    '<div class="lb-group">' + "".join(f'<div class="lb-group-row"><span class="rp-q-mark">?</span><span>{E(u)}</span></div>' for u in UNK) + "</div>"

# Evidence (from evidence.md) ----------------------------------------------
ev_md = open(os.path.join(OUT, "evidence.md"), encoding="utf-8").read()
ev_parts = re.split(r"\n(?=## E\d+\.)", ev_md)
intro_md, blocks = ev_parts[0], ev_parts[1:]
ev_cards = []
for b in blocks:
    title = b.splitlines()[0][3:].strip()
    eid = title.split(".")[0].lower()
    body_md = "\n".join(b.splitlines()[1:]).replace("\n---", "")
    body_html, _ = convert(body_md)
    ev_cards.append(f'<details class="lb-card rp-ev" id="evidence-{eid}"><summary><span class="rp-tid">{E(title.split(".")[0])}</span><span>{inline(title.split(". ", 1)[1])}</span></summary><div class="rp-md">{body_html}</div></details>')
intro_html, _ = convert(intro_md.replace("# Evidence behind each conclusion", ""))
V["evidence"] = head("Evidence", "Reference · E1 to E14", "Every conclusion with the observed numbers, verified examples and links. Open a card for the detail.") + \
    f'<div class="lb-card is-quiet rp-md">{intro_html}</div><div class="lb-stack">' + "".join(ev_cards) + \
    '</div><div class="lb-row"><button class="lb-btn secondary sm" type="button" data-ev="open">Open all</button><button class="lb-btn ghost sm" type="button" data-ev="close">Close all</button></div>'

# Method (from methodology.md) ---------------------------------------------
me_md = open(os.path.join(OUT, "methodology.md"), encoding="utf-8").read()
me_parts = re.split(r"\n(?=## )", me_md)
me_cards = []
for b in me_parts[1:]:
    title = b.splitlines()[0][3:].strip()
    body_html, _ = convert("\n".join(b.splitlines()[1:]))
    me_cards.append(f'<details class="lb-card rp-ev"><summary><span>{inline(title)}</span></summary><div class="rp-md">{body_html}</div></details>')
V["method"] = head("Method and limits", "Reference", "Sources, sample, formulas, coding, comment sampling, what could not be measured, biases.") + \
    f"""<div class="lb-grid cols-4">
  {stat("Posts fetched", "2,992", "41 profiles, 14 Oct 18:04 to 18:19")}
  {stat("Recent sample", "469", "7 to 90 days old; 180 for 4 creators")}
  {stat("Older breakouts", "96", "5x the creator median or more")}
  {stat("Reels transcribed", "24", "of 105 deep-dive reels")}
</div><div class="lb-stack">""" + "".join(me_cards) + "</div>" + \
    '<p class="lb-note">Files: <code>posts.csv</code> (565 posts × 86 fields), <code>creators.csv</code> (41 × 40), <code>src/</code> (collector, scripts, coding briefs).</p>'


# Round 2: buying signals across 134 creators --------------------------------
R2 = os.path.join(OUT, "round2")
r2p = list(csv.DictReader(open(os.path.join(R2, "posts_kpi.csv"), encoding="utf-8")))
r2c = list(csv.DictReader(open(os.path.join(R2, "creators_kpi.csv"), encoding="utf-8")))
r2t = json.load(open(os.path.join(R2, "traits.json"), encoding="utf-8"))
for x in r2p:
    for k in ("purchase_signals", "product_q", "intent", "purchase", "offer_requests", "sampled_audience", "comments", "plays", "followers"):
        x[k] = num(x[k])
for x in r2c:
    for k in ("purchase_signals", "purchase_signals_per_100", "followers", "offer_requests", "posts_with_purchase_signal", "posts_with_comments_sampled", "comments_sampled"):
        x[k] = num(x[k])
aud = sum(x["sampled_audience"] or 0 for x in r2p)
sig_tot = sum(x["purchase_signals"] or 0 for x in r2p)
pq = sum(x["product_q"] or 0 for x in r2p); it = sum(x["intent"] or 0 for x in r2p); pu = sum(x["purchase"] or 0 for x in r2p)
offer_tot = sum(x["offer_requests"] or 0 for x in r2p)
with_sig = sum(1 for x in r2p if (x["purchase_signals"] or 0) > 0); top3 = sum(1 for x in r2p if (x["purchase_signals"] or 0) >= 3)
sampled_posts = sum(1 for x in r2p if x["sampled_audience"])


def trait_rows(g, keep):
    d = {t["trait"]: t for t in r2t["traits"][g]}
    return [[E(k), f"<b>{d[k]['top']}%</b>", f"{d[k]['base']}%"] for k in keep if k in d]


TP = ["product shown (featured or demonstrated)", "product demonstrated in use", "format: product review", "price visible",
      "discount, code or deal offered", "sponsored or brand collaboration", "practical takeaway", "humour", "format: skit / POV"]
TO = ["comment-word CTA", "creator's own product or service", "proof: expert credential", "format: tips carousel", "no CTA", "humour"]
TR = ["format: talking head", "proof: expert credential", "reassurance", "format: skit / POV", "product shown (featured or demonstrated)", "comment-word CTA"]
WHY = {"michal_nunu": "Try-on reels of evening dresses with a price", "orelcabelli": "Cleaning products demonstrated, personal code",
       "sivan_grosman_zukerman": "Attraction picks (several \"purchases\" are bad reviews)", "lital_magnezi": "Classroom items shown in use",
       "tom_zakai_levinkopf": "Kids' shoes, sponsored", "morkeisar": "Sponsored posts (mixer, baby play mat)", "hen.kalimian.kids": "Reading-room makeover: \"where is the rug from\"",
       "shelly.yudaikin": "Enquiries about her own therapy service", "ima.shir": "A device seen in a reel", "orel_zamir_ovadia": "Recipes and appliance deals"}
top_c = sorted([c for c in r2c if (c["comments_sampled"] or 0) >= 60], key=lambda c: -(c["purchase_signals"] or 0))[:10]
ctab = table(["Creator", "Followers", "Buying signals", "Per 100 comments", "Posts with a signal", "What triggers it"],
             [[f'<a href="https://www.instagram.com/{E(c["creator"])}/" target="_blank" rel="noopener">{E(c["creator"])}</a>', fmt(c["followers"]), f"<b>{c['purchase_signals']}</b>",
               f"{c['purchase_signals_per_100']:.1f}", f"{c['posts_with_purchase_signal']} of {c['posts_with_comments_sampled']}", E(WHY.get(c["creator"], ""))] for c in top_c], (1, 2, 3))
kids = [("Gift ideas for a 3-year-old by development area", "mash_iz", "DZqIIV_DjFM"), ("5 board games for age 3 (Kodkod)", "hadar_baier_slp", "DdGWWI1CACd"),
        ("Board games recommended by an OT", "knafaim.ot_by_noy", "DdWglWIKur-"), ("Kinetic sand language play", "trainingwheelsclinic", "DcSrULbN9dU"),
        ("Giotto creative kits for toddlers", "maya_doskalovich_ot", "DbunKNUMg0X"), ("Reading-room makeover", "hen.kalimian.kids", "DdZFL7NoIXu"),
        ("A gan teacher's autumn book shelf", "_shirley_unger_kids_activities", "DeKFbzRAmIy"), ("Toilet push light in a gan bathroom", "lital_magnezi", "Dd5sq3TI1I5")]
fit = ["hadar_baier_slp", "knafaim.ot_by_noy", "mash_iz", "maya_doskalovich_ot", "trainingwheelsclinic", "yana.nachmani", "lital_magnezi", "hen.kalimian.kids", "_shirley_unger_kids_activities", "shelly.yudaikin"]
V["signals"] = head("Buying signals across 134 creators", "Findings · round 2",
                    "The top half of the creator map by views (121 of 122 accounts; one no longer exists) plus the first 13 below it. Which of their own posts already make people ask how to buy? Public proxies only: none of these creators works with LumeBook, so there is no sales data.") + f"""
<div class="lb-grid cols-4">
  {stat("Creators", "134", "top half of the map + round 1")}
  {stat("Recent posts", f"{len(r2p):,}", f"{sampled_posts:,} with audience comments")}
  {stat("Audience comments read", f"{aud:,}", "up to 30 per post, Hebrew")}
  {stat("Buying signals", f"{sig_tot}", f"{sig_tot * 100 / aud:.1f}% of comments")}
</div>
<div class="lb-grid" style="--min:24rem">
  <div class="lb-card"><div class="lb-card-head"><h3>What counts as a buying signal</h3>{chip("verified by reading", "outline")}</div>
    {hbars([("Where to buy, link, price, sizes, shipping", pq, ""), ("Wants to buy it", it, ""), ("Says they bought or own it", pu, "")], fmtv=lambda v: f"{int(v)}")}
    <p class="lb-note">{with_sig} of {sampled_posts:,} posts have at least one; only {top3} have three or more. Separately, {offer_tot:,} comments ask for something the creator offered (a list, file or guide behind a comment word).</p></div>
  <div class="lb-card is-quiet"><h3>How the comments were read</h3><p class="lb-small">A Hebrew rule set finds requests for the creator's offer; it matches the round-1 agents closely (rank correlation 0.94 per post). For buying signals, a broad net flagged every comment that might be one (4,481, catching 64 of 68 known examples) and agents read each in Hebrew and labelled it.</p>
    <p class="lb-note">Proxies, not sales: no clicks, carts or orders are visible. Instagram's top-ranked comments only.</p></div>
</div>
<section class="lb-section"><div class="lb-section-head"><h3>Three different engines</h3><span class="lb-meta">Coded top posts vs {r2t['groups']['baseline']} ordinary coded posts</span></div>
<div class="lb-grid" style="--min:19rem">
  <div class="lb-card is-accent"><span class="lb-eyebrow">Buying questions · {r2t['groups']['top_purchase']} posts with 3+ signals</span><h3>A product shown working, with a price or deal</h3>
    {table(["Trait", "Top", "Ordinary"], trait_rows("top_purchase", TP), (1, 2))}</div>
  <div class="lb-card"><span class="lb-eyebrow">Offer requests · top {r2t['groups']['top_offer']} by requests per follower</span><h3>A free resource behind a comment word</h3>
    {table(["Trait", "Top", "Ordinary"], trait_rows("top_offer", TO), (1, 2))}</div>
  <div class="lb-card"><span class="lb-eyebrow">Reposts · top {r2t['groups']['top_reposts']} by reposts per 1k plays</span><h3>Experts and relatable moments, no product</h3>
    {table(["Trait", "Top", "Ordinary"], trait_rows("top_reposts", TR), (1, 2))}</div>
</div><p class="lb-note">No post does all three. Observational comparison; it does not show cause.</p></section>
<div class="lb-card is-flush rp-board"><div class="rp-board-head"><h4>Creators whose own posts draw the most buying signals</h4><p class="lb-note">At least 60 audience comments read. Separate from offer requests and reach.</p></div>{ctab}</div>
<div class="lb-grid" style="--min:24rem">
  <div class="lb-card"><h3>Kids' products that already draw "where do I buy"</h3><ul class="lb-list">{"".join(f'<li><span>{E(t)}</span><span class="lb-meta">{E(c)} · {ig(code)}</span></li>' for t, c, code in kids)}</ul>
    <p class="lb-note">Only 1 of the {r2t['groups']['top_purchase']} top posts features a children's book. Toys, games and gear are where these audiences ask to buy today.</p></div>
  <div class="lb-card is-accent"><span class="lb-eyebrow">What it means for LumeBook</span><h3>Show the printed book working, with its price</h3>
    <ul class="rp-steps"><li>A child opening the book and seeing themselves, the pages, the price with the follower discount, how to order.</li>
    <li>A "gift for a 3-year-old" list with the book in it: the format that already pulls buying questions on kids' products.</li>
    <li>Use the comment word to deliver the personal link, but read its comments as requests, not demand.</li>
    <li>Keep humour and skits for reach.</li></ul>
    <p class="lb-small"><b>Best-fit creators for a buying test:</b> {", ".join(E(x) for x in fit)}.</p></div>
</div>
<p class="lb-note">Files: <code>round2/round2.md</code>, <code>round2/posts_kpi.csv</code> ({len(r2p):,} posts), <code>round2/creators_kpi.csv</code> (134 creators).</p>"""


# Round 2 drives the headline views ------------------------------------------
for x in r2p:
    for k in ("likes", "reposts", "likes_per_1k_plays", "comments_per_1k_plays", "reposts_per_1k_plays", "plays_per_follower", "likes_per_1k_followers",
              "comments_per_1k_followers", "offer_requests_est_per_1k_followers", "purchase_signals_per_100", "offer_share"):
        x[k] = num(x[k])
reels2 = [x for x in r2p if x["format"] == "reel" and x["plays"]]
byc = collections.defaultdict(list)
for x in reels2:
    byc[x["creator"]].append(x["plays"])
for x in reels2:
    ps = byc[x["creator"]]
    x["n_reels"] = len(ps); x["med_plays"] = st.median(ps); x["rel_plays"] = x["plays"] / x["med_plays"] if x["med_plays"] else None
big2 = [x for x in reels2 if x["plays"] >= 2000]
nonreel2 = [x for x in r2p if x["format"] != "reel"]


def t2(x, n=56):
    t = x.get("topic") or ""
    return E(t[:n] + ("…" if len(t) > n else "")) if t else '<span class="lb-dim">not coded</span>'


def row2(x, *extra):
    return [E(x["creator"]), ig(x["post_code"]), x["published_utc"][:10], t2(x)] + list(extra)


A1b = table(base + ["Plays", "Followers"], [row2(x, fmt(x["plays"]), fmt(x["followers"])) for x in sorted(reels2, key=lambda x: -x["plays"])[:10]], (4, 5))
A2b = table(base + ["Plays", "Creator median", "Ratio"], [row2(x, fmt(x["plays"]), fmt(x["med_plays"]), f"<b>{x['rel_plays']:.1f}x</b>")
            for x in sorted([x for x in reels2 if x["n_reels"] >= 3], key=lambda x: -x["rel_plays"])[:10]], (4, 5, 6))
r2c_ppf = [c for c in csv.DictReader(open(os.path.join(R2, "creators_kpi.csv"), encoding="utf-8")) if num(c["median_plays_per_follower"])]
A3b = table(["Creator", "Followers", "Median reel plays", "Plays per follower"],
            [[E(c["creator"]), fmt(num(c["followers"])), fmt(num(c["median_plays"])), f"{num(c['median_plays_per_follower']):.2f}"]
             for c in sorted(r2c_ppf, key=lambda c: -num(c["median_plays_per_follower"]))[:10]], (1, 2, 3))
E1b = table(base + ["Likes", "Plays", "Likes / 1k plays"], [row2(x, fmt(x["likes"]), fmt(x["plays"]), fmt(x["likes_per_1k_plays"])) for x in sorted([x for x in big2 if x["likes_per_1k_plays"]], key=lambda x: -x["likes_per_1k_plays"])[:8]], (4, 5, 6))
E2c = table(base + ["Comments", "Plays", "Comments / 1k plays", "Offer share"], [row2(x, fmt(x["comments"]), fmt(x["plays"]), fmt(x["comments_per_1k_plays"]), f"{x['offer_share'] * 100:.0f}%" if x["offer_share"] is not None else "n/a") for x in sorted([x for x in big2 if x["comments_per_1k_plays"]], key=lambda x: -x["comments_per_1k_plays"])[:10]], (4, 5, 6, 7))
E2d = table(base + ["Comments", "Plays", "Comments / 1k plays"], [row2(x, fmt(x["comments"]), fmt(x["plays"]), fmt(x["comments_per_1k_plays"])) for x in sorted([x for x in big2 if x["comments_per_1k_plays"] and (x["offer_share"] or 0) < 0.2], key=lambda x: -x["comments_per_1k_plays"])[:10]], (4, 5, 6))
E3b = table(base + ["Reposts", "Plays", "Reposts / 1k plays"], [row2(x, fmt(x["reposts"]), fmt(x["plays"]), fmt(x["reposts_per_1k_plays"])) for x in sorted([x for x in big2 if x["reposts_per_1k_plays"]], key=lambda x: -x["reposts_per_1k_plays"])[:10]], (4, 5, 6))
E4b = table(base + ["Comments", "Likes", "Likes / 1k followers"], [row2(x, fmt(x["comments"]), fmt(x["likes"]), fmt(x["likes_per_1k_followers"])) for x in sorted([x for x in nonreel2 if x["likes_per_1k_followers"]], key=lambda x: -x["likes_per_1k_followers"])[:10]], (4, 5, 6))
cp2 = [x for x in r2p if (x["sampled_audience"] or 0) >= 5]
C1b = table(["Creator", "Post", "Topic", "Read", "Buying signals", "Per 100", "Where/price · want · bought"],
            [[E(x["creator"]), ig(x["post_code"]), t2(x, 50), fmt(x["sampled_audience"]), f"<b>{x['purchase_signals']}</b>", f"{x['purchase_signals_per_100']:.0f}", f"{x['product_q']} · {x['intent']} · {x['purchase']}"]
             for x in sorted(cp2, key=lambda x: (-(x["purchase_signals"] or 0), -(x["purchase_signals_per_100"] or 0)))[:15]], (3, 4, 5))
C2b = table(["Creator", "Post", "Topic", "Read", "Offer requests", "Share", "Post comments"],
            [[E(x["creator"]), ig(x["post_code"]), t2(x, 50), fmt(x["sampled_audience"]), f"<b>{x['offer_requests']}</b>", f"{x['offer_share'] * 100:.0f}%", fmt(x["comments"])]
             for x in sorted([x for x in cp2 if x["offer_requests_est_per_1k_followers"]], key=lambda x: -x["offer_requests_est_per_1k_followers"])[:12]], (3, 4, 5, 6))
TABS2 = [
    ("attention", "Attention", board("A1 · Highest raw plays", f"Reels, recent sample, {len(reels2):,} reels from 134 creators. Plays are not unique reach.", A1b)
     + board("A2 · Plays vs the creator's own median", "Creators with at least 3 sample reels. The fairest comparison across account sizes.", A2b)
     + board("A3 · Median reel plays per follower", "Proxy: followers are not exposure.", A3b) + '<p class="lb-note">Watch time, retention and completion: unavailable.</p>'),
    ("engagement", "Engagement", board("E1 · Likes per 1,000 plays", "Reels with at least 2,000 plays.", E1b)
     + board("E2 · Comments per 1,000 plays, all posts", "Offer share = share of read comments asking for the creator's offer; high values mean a comment-word funnel.", E2c)
     + board("E2b · Comments per 1,000 plays, conversation only", "Posts where under 20% of comments ask for an offer.", E2d)
     + board("E3 · Reposts per 1,000 plays", "Public repost count. DM shares are not public.", E3b)
     + board("E4 · Carousels and images: likes per 1,000 followers", "Proxy.", E4b) + '<p class="lb-note">Saves and DM shares: unavailable.</p>'),
    ("consideration", "Buying signals", board("C1 · Most buying-signal comments", "Where to buy, link, price, sizes or shipping questions; wanting to buy; saying they bought. Verified by reading. Posts with at least 5 audience comments read.", C1b)
     + board("C2 · Most offer requests per follower", "Comments asking for what the creator offered (a list, file, guide behind a comment word). A request for the offer, not demand for a product.", C2b)
     + board("C3 · Substantive discussion (round 1 only)", "Identification, personal stories and help requests were classified only in the 41-creator deep dive.", C3)),
    ("purchase", "Activation and purchase", TABS[3][2]),
]
tabbar2 = '<div class="lb-tabs" role="tablist">' + "".join(f'<button role="tab" data-tab="{k}" aria-selected="{"true" if i == 0 else "false"}">{E(t)}</button>' for i, (k, t, _) in enumerate(TABS2)) + "</div>"
panes2 = "".join(f'<div class="rp-pane lb-stack" data-pane="{k}" {"" if i == 0 else "hidden"}>{b}</div>' for i, (k, _, b) in enumerate(TABS2))
V["kpis"] = head("KPI leaderboards", "Findings · 134 creators", f"One ranking per KPI, never a combined score. {len(r2p):,} recent posts from 134 creators, Instagram only, reels kept apart from carousels and images.") + \
    f'<details class="lb-card rp-details"><summary><b>What each funnel stage can and cannot show</b><span class="lb-dim"> · evidence boundary</span></summary>{boundary}<p class="lb-note">Missing means unknown, not zero.</p></details>' + \
    f'<div class="rp-tabs">{tabbar2}{panes2}</div>'

R1NOTE = '<div class="lb-callout info rp-r1"><span class="lb-small"><b>Round 1 deep dive · 41 creators.</b> This view rests on the first run, where every post was coded and comments were classified in full detail. The 134-creator results are in <a href="#signals">Buying signals</a> and <a href="#kpis">KPI leaderboards</a>.</span></div>'
for k in ("questions", "content", "voice", "icp", "creators", "concepts", "tests", "evidence", "method"):
    V[k] = V[k].replace("</header>", "</header>" + R1NOTE, 1)

# ---------------------------------------------------------------- shell
ICONS = {
    "overview": '<path d="M3 12l9-8 9 8"/><path d="M5 10v10h14V10"/>',
    "questions": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.8.4-1 1-1 1.7"/><path d="M12 17h.01"/>',
    "kpis": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "signals": '<path d="M6 6h15l-1.5 9h-12z"/><path d="M6 6 5 3H2"/><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/>',
    "content": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "voice": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    "icp": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14a5 5 0 0 1 4.5 5"/>',
    "creators": '<path d="M12 3l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.4 6.8 19.1l1-5.8L3.5 9.2l5.9-.8z"/>',
    "concepts": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "tests": '<path d="M9 3h6M10 3v6L4.5 18.5A2 2 0 0 0 6.2 21h11.6a2 2 0 0 0 1.7-2.5L14 9V3"/>',
    "measure": '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
    "evidence": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
    "method": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    "unknowns": '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>',
}
NAV = [("Answer", [("overview", "Overview"), ("questions", "Decision answers")]),
       ("Findings", [("signals", "Buying signals · 134"), ("kpis", "KPI leaderboards"), ("content", "Content patterns"), ("voice", "Audience voice"), ("icp", "Buyer segments")]),
       ("Actions", [("creators", "Creators to test"), ("concepts", "Content concepts"), ("tests", "Four-week tests"), ("measure", "Measurement")]),
       ("Reference", [("evidence", "Evidence E1 to E14"), ("method", "Method and limits"), ("unknowns", "Still unknown")])]
COUNTS = {"concepts": "10", "tests": "5", "evidence": "14"}
nav = ""
for label, items in NAV:
    nav += f'<div class="lb-nav-label">{label}</div>'
    for k, t in items:
        cnt = f'<span class="lb-count">{COUNTS[k]}</span>' if k in COUNTS else ""
        nav += (f'<a class="lb-nav-item" href="#{k}" data-view="{k}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
                f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[k]}</svg><span>{t}</span>{cnt}</a>')
TITLES = {k: t for _, items in NAV for k, t in items}
views = "".join(f'<section class="lb-page rp-view" data-view="{k}" hidden>{v}</section>' for k, v in V.items())

CSS = """
html { direction: ltr; }
body { text-align: start; }
.rp-head { display: grid; gap: var(--sp-2); }
.rp-head h2 { font-size: clamp(1.6rem, 3.2vw, 2.25rem); }
bdi.he, [lang="he"] { font-family: var(--font); }
.rp-stat.is-zero .lb-stat-value { color: var(--danger); }
.rp-n { display: inline-grid; place-items: center; width: 1.75rem; height: 1.75rem; border-radius: 50%; background: var(--tint-soft); color: var(--tint); font-weight: 700; font-size: var(--fs-footnote); flex: none; }
.rp-finding { gap: var(--sp-2); }
.rp-finding h3, .rp-cta h3 { font-size: var(--fs-headline); }
.rp-go { font-size: var(--fs-footnote); font-weight: 600; color: var(--tint); }
.rp-qa-q { display: flex; gap: var(--sp-3); align-items: center; }
.rp-qa p { padding-inline-start: 2.75rem; }
.rp-qa .lb-row { padding-inline-start: 2.75rem; }
.rp-details summary { cursor: pointer; list-style: none; display: flex; flex-wrap: wrap; gap: .25rem; align-items: baseline; }
.rp-details summary::-webkit-details-marker, .rp-ev summary::-webkit-details-marker { display: none; }
.rp-details summary::after, .rp-ev summary::after { content: "+"; margin-inline-start: auto; color: var(--text-3); font-weight: 600; }
.rp-details[open] summary::after, .rp-ev[open] summary::after { content: "−"; }
.rp-tabs { display: grid; gap: var(--sp-4); }
.rp-board-head { padding: var(--sp-4) var(--sp-4) var(--sp-3); display: grid; gap: 2px; }
.rp-board .lb-table-wrap { border: 0; border-top: 1px solid var(--line); border-radius: 0; }
.lb-table td { vertical-align: top; }
.rp-board td:nth-child(3) { white-space: nowrap; }
.lb-hbar { grid-template-columns: minmax(7rem, 40%) minmax(0, 1fr) 3.4rem; }
.lb-hbar > span:first-child { display: grid; line-height: 1.25; }
.lb-hbar small { font-size: var(--fs-caption); color: var(--text-3); }
.lb-hbar .track { position: relative; }
.rp-mark { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--text-3); border-radius: 1px; z-index: 1; }
.rp-q { margin: 0; display: grid; gap: 4px; }
.rp-q blockquote, .rp-hook { margin: 0; padding: .6rem .85rem; background: var(--surface-2); border-inline-end: 3px solid var(--lb-gold-deep); border-radius: var(--r-sm); font-size: 1.05rem; font-weight: 600; direction: rtl; text-align: right; line-height: 1.5; }
.rp-q figcaption { font-size: var(--fs-footnote); color: var(--text-2); }
.rp-hook { font-size: 1.2rem; }
.rp-concept, .rp-test { align-content: start; }
.rp-concept h3, .rp-test h3 { font-size: var(--fs-headline); }
.rp-concept .lb-kv, .rp-test .lb-kv, .rp-icp .lb-kv { font-size: var(--fs-footnote); }
.rp-tid { display: inline-grid; place-items: center; min-width: 2.2rem; height: 1.6rem; padding-inline: .45rem; border-radius: var(--r-sm); background: var(--lb-ink, #1D1039); color: #fff; font-weight: 700; font-size: var(--fs-footnote); flex: none; }
.rp-hyp { font-size: var(--fs-callout); color: var(--text-2); }
.rp-rule { display: grid; gap: var(--sp-1); padding: var(--sp-3); border-radius: var(--r-md); background: var(--warning-soft); }
.rp-rule .lb-chip { justify-self: start; }
.rp-steps { margin: 0; padding-inline-start: 1.25rem; display: grid; gap: var(--sp-1); font-size: var(--fs-callout); }
.rp-funnel { list-style: none; margin: 0; padding: 0; display: grid; gap: 0; }
.rp-fstep { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: var(--sp-3); align-items: center; padding: .6rem 0; border-top: 1px solid var(--line); }
.rp-fstep:first-child { border-top: 0; }
.rp-fstep > div { display: grid; }
.rp-fn { width: 1.6rem; height: 1.6rem; border-radius: 50%; display: grid; place-items: center; background: var(--fill-2); font-size: var(--fs-caption); font-weight: 700; }
.rp-limits > div { display: grid; gap: 2px; }
.rp-filter { flex-wrap: wrap; }
.rp-filter button { white-space: nowrap; }
.rp-creator .rp-handle { font-weight: 700; }
.rp-mini { display: flex; flex-wrap: wrap; gap: var(--sp-2) var(--sp-4); font-size: var(--fs-footnote); color: var(--text-2); }
.rp-mini b { color: var(--text); font-variant-numeric: tabular-nums; }
.rp-q-mark { width: 1.6rem; height: 1.6rem; border-radius: 50%; display: grid; place-items: center; background: var(--warning-soft); color: var(--warning); font-weight: 700; flex: none; }
.rp-ev summary { cursor: pointer; list-style: none; display: flex; gap: var(--sp-3); align-items: center; font-weight: 600; }
.rp-md { display: grid; gap: var(--sp-3); font-size: var(--fs-callout); }
.rp-md h3 { font-size: var(--fs-callout); margin-top: var(--sp-2); }
.rp-md ul, .rp-md ol { margin: 0; padding-inline-start: 1.25rem; display: grid; gap: var(--sp-1); }
.rp-md .lb-table-wrap { margin: 0; }
.rp-md .rp-quote { display: block; padding: .5rem .8rem; background: var(--surface-2); border-radius: var(--r-sm); direction: rtl; text-align: right; font-weight: 600; }
.lb-topbar .lb-dim { font-size: var(--fs-footnote); }
.rp-crumb { font-weight: 600; }
@media (max-width: 640px) { .lb-grid.cols-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .lb-topbar .lb-dim { display: none; } .rp-stat { padding: var(--sp-3); } .rp-qa p, .rp-qa .lb-row { padding-inline-start: 0; } .lb-hbar { grid-template-columns: minmax(6rem, 42%) minmax(0, 1fr) 3rem; } }
@media print { .lb-sidebar, .lb-topbar { display: none; } .lb-app { display: block; } .rp-view { display: grid !important; break-before: page; } details { display: block; } }
"""

JS = """<script>
(function () {
  var views = document.querySelectorAll('.rp-view'), items = document.querySelectorAll('.lb-nav-item');
  var crumb = document.getElementById('rp-crumb'), side = document.querySelector('.lb-sidebar'), scrim = document.querySelector('.lb-scrim');
  var titles = TITLES;
  function route() {
    var h = (location.hash || '#overview').slice(1), target = null;
    if (h.indexOf('evidence-') === 0) { target = document.getElementById(h); h = 'evidence'; }
    if (!titles[h]) h = 'overview';
    views.forEach(function (v) { v.hidden = v.dataset.view !== h; });
    items.forEach(function (a) { if (a.dataset.view === h) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    crumb.textContent = titles[h];
    document.title = titles[h] + ' · Creator content and purchase intent';
    closeNav();
    if (target) { target.open = true; setTimeout(function () { target.scrollIntoView({block: 'start'}); }, 30); } else { window.scrollTo(0, 0); }
  }
  function closeNav() { side.classList.remove('is-open'); scrim.hidden = true; }
  document.getElementById('rp-menu').addEventListener('click', function () { side.classList.add('is-open'); scrim.hidden = false; });
  scrim.addEventListener('click', closeNav);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeNav(); });
  window.addEventListener('hashchange', route);
  document.querySelectorAll('.rp-tabs').forEach(function (box) {
    box.querySelectorAll('[role="tab"]').forEach(function (b) {
      b.addEventListener('click', function () {
        box.querySelectorAll('[role="tab"]').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
        box.querySelectorAll('.rp-pane').forEach(function (p) { p.hidden = p.dataset.pane !== b.dataset.tab; });
      });
    });
  });
  document.querySelectorAll('.rp-filter button').forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.dataset.f;
      b.parentNode.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      document.querySelectorAll('.rp-concept').forEach(function (c) { c.hidden = !!f && c.dataset.occ !== f; });
    });
  });
  document.querySelectorAll('[data-ev]').forEach(function (b) {
    b.addEventListener('click', function () { var o = b.dataset.ev === 'open'; document.querySelectorAll('.rp-view[data-view="evidence"] details').forEach(function (d) { d.open = o; }); });
  });
  route();
})();
</script>"""

page = f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Creator content and purchase intent</title>
{design.head()}
<style>{CSS}</style>
</head>
<body>
<div class="lb-app">
  <aside class="lb-sidebar" aria-label="Sections">
    <a class="lb-brand" href="#overview"><img src="{design.logo_data_uri()}" alt=""><span><b>Creator research</b><small>LumeBook · 14 Oct 2026</small></span></a>
    <nav class="lb-nav">{nav}</nav>
    <div class="lb-sidebar-foot"><span class="lb-chip warning">Internal · sales figures</span><span>134 creators · 1,456 posts · 22,428 comments</span><span>Deep dive: 41 creators, 469 coded posts</span><span>Built from <code>report.md</code>, <code>evidence.md</code>, <code>methodology.md</code>, the CSVs</span></div>
  </aside>
  <div class="lb-scrim" hidden></div>
  <main class="lb-main">
    <div class="lb-topbar"><div class="lb-topbar-in">
      <button class="lb-btn secondary icon lb-menu-btn" id="rp-menu" type="button" aria-label="Open sections"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
      <span class="rp-crumb" id="rp-crumb">Overview</span><span class="lb-spacer"></span><span class="lb-dim">Creator content and purchase intent</span>{design.theme_toggle(dark_label="Dark mode")}
    </div></div>
    {views}
  </main>
</div>
{JS.replace("TITLES", json.dumps(TITLES))}
</body>
</html>
"""
with open(os.path.join(OUT, "report.html"), "w", encoding="utf-8") as f:
    f.write(page)
print("wrote report.html", f"{len(page):,} bytes,", len(V), "views")
