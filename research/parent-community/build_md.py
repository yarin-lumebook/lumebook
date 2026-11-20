"""Builds research/parent-community-outreach.md from data.json (the same data as the HTML page)."""
import json, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "parent-community-outreach.md")
D = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
R, OTH, DR, OFFER = D["rows"], D["other"], D["drafts"], D["offer"]
PORD = {"A": 0, "B": 1, "C": 2, "Reject": 3}

def esc(s):
    s = str(s if s is not None else "").replace("\n", " ").replace("|", "\\|").strip()
    return s or "Unknown"

def km(r):
    if r.get("dist_km") is None: return "national"
    return "in Ashkelon" if r["dist_km"] == 0 else f"{r['dist_km']} km"

def sortkey(r):  # closest first, then priority, then activity, then size
    return (r.get("band", 6), r.get("dist_km") or 0, PORD[r["priority"]], -(r.get("posts_month") or 0), -(r.get("members_n") or 0))

COLS = ["Priority", "Platform", "Community name", "Direct URL or public invite link", "Language", "Geographic focus", "Parent or creator segment",
        "Estimated member count", "Activity evidence", "Latest visible activity", "Public or private", "Promotional-post policy",
        "Administrator approval required", "Public administrator or contact route", "Evidence that collaboration posts fit",
        "Recommended approach", "Suggested post angle", "Confidence level", "Evidence URL", "Date checked", "Notes"]

def row(r):
    notes = "; ".join(x for x in [r.get("offer_note"), r.get("notes")] if x)
    seg = ", ".join((r.get("segments") or [])[:2])
    return "| " + " | ".join(esc(x) for x in [r["priority"], r["platform"], r["name"], r["url"], r["language"], f"{r['geo']} ({km(r)})", seg,
        r["members"], r["activity"], r["latest"], r["privacy"], r["policy"], r["approval"], r["contact"], r["collab"], r["approach"],
        r["angle"], r["confidence"], r["evidence"], r["checked"], notes]) + " |"

def table(rows):
    return "\n".join(["| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)] + [row(r) for r in rows])

live = sorted([r for r in R if r["priority"] != "Reject"], key=sortkey)
rej = sorted([r for r in R if r["priority"] == "Reject"], key=sortkey)
cnt = Counter(r["priority"] for r in R)
ap = Counter(r["approach"] for r in live)
fb = sum(1 for r in R if r["platform"].startswith("Facebook"))
wa = sum(1 for r in R if r["platform"].startswith("WhatsApp"))
wa_states = Counter(r.get("wa_status") for r in R if r["platform"].startswith("WhatsApp"))
bands = Counter(r.get("band_label") for r in live)
moved = [r for r in R if r.get("offer_note")]
byid = {r["id"]: r for r in R}

SEGS = ["General parents", "Local city or neighbourhood parents", "Mothers", "Fathers", "Babies and toddlers", "Preschool and primary-school parents",
        "Children's books and reading", "Special education or child development", "Content creators and UGC", "Product testing, deals and recommendations"]

L = []
w = L.append
w("# Parent community outreach map")
w("")
w(f"LumeBook recruitment of Israeli families for a social-media shooting day at home in exchange for a free personalised book. Communities were researched and checked on 2026-10-09 and re-ranked for this offer on {OFFER['checked']}. Every count, rule and activity figure was read on the community's own page on 2026-10-09 unless a row says otherwise.")
w("")
w("## The offer")
w("")
w(f"**{OFFER['he']}**")
w("")
for t in OFFER["terms"]:
    w(f"- {t}")
w("")
w(f"Distance: {OFFER['distance_method']}")
w("")
w("## Executive summary")
w("")
w(f"- **Total unique communities found: {len(R)}**, plus {len(OTH)} pages, sites and organisations listed separately as other routes (not counted).")
w(f"- **Facebook: {fb}** groups, each opened on its About page in a logged-in browser (read-only: nothing joined, liked, posted or messaged).")
w(f"- **WhatsApp: {wa}** groups, communities and channels. Invite status: " + ", ".join(f"{k} {v}" for k, v in wa_states.items() if k) + ". ERROR means WhatsApp rate-limited the check, so the invite is unverified.")
w(f"- **Other platforms: {len(R) - fb - wa}** (Telegram groups and public forums).")
w(f"- **Priority:** A {cnt['A']}, B {cnt['B']}, C {cnt['C']}, Reject {cnt['Reject']}. For the shooting-day offer, {len(moved)} rows moved down: local groups more than 80 km from Ashkelon, and creator groups (parents no longer need to post).")
w(f"- **Recommended for direct posting: {ap['Post directly']}**; administrator outreach first: {ap['Ask admin first']}; paid post or formal partnership: {ap['Paid post or formal partnership']}; monitor only: {ap['Monitor']}.")
w(f"- **Rejected: {cnt['Reject']}**; questionable (priority C): {cnt['C']}.")
w("- **Usable groups by distance from Ashkelon:** " + ", ".join(f"{b} {bands.get(b, 0)}" for b in ["Ashkelon", "Under 30 km", "30 to 55 km", "55 to 80 km", "Over 80 km", "National (members anywhere)"]) + ".")
w("- **Most promising segment:** the Ashkelon mothers groups, several of which allow free posting, then Sderot, Ashdod and Netivot. National groups come after the local ones, with the family's city asked in the form.")
w("- **Major gaps:** no Ashkelon parent WhatsApp group was found; no Israeli Arabic-language parent group was verified; the parent sign-up form does not exist yet. Details in Search gaps.")
w("")
w("### How to read this")
w("")
w("- **Geographic focus** shows the city and the straight-line distance from Ashkelon. National groups have members anywhere.")
w("- **Activity evidence** for Facebook is the Activity box on each group's About page, copied as shown. Use it to compare groups, not as an absolute.")
w("- **Promotional-post policy** quotes or paraphrases the group's About text and rules from the admins.")
w("- **Confidence:** High = written rules were read; Medium = only About text or a valid invite page; Low = name and numbers only, or an invite that could not be checked.")
w("- Verified facts are members, activity, privacy, rules and invite status. **Assumptions** are the priority, the approach and the post angle, which are judgement from those facts.")
w("")
w("## Master list")
w("")
w(f"{len(live)} communities, sorted closest to Ashkelon first, then by priority, activity and size. Rejected entries are in the appendix.")
w("")
w(table(live))
w("")
w("## Top 20 opportunities")
w("")
w("Closest to Ashkelon first, then the strongest groups, for families who will host a short shoot with their child and the book.")
w("")
for i, t in enumerate(D["top"], 1):
    r = byid[t["id"]]
    w(f"{i}. **{r['name']}** ({r['members']} members, {km(r)}, priority {r['priority']}, {r['approach']}). [{r['url']}]({r['url']}). {t['why']}")
w("")
w("## Coverage by audience")
w("")
w('A community can count in more than one row. "All" includes rejected entries; "Usable" is A, B and C.')
w("")
w("| Audience | Usable | All |")
w("|---|---|---|")
for s in SEGS:
    w(f"| {s} | {sum(1 for r in live if s in (r.get('segments') or []))} | {sum(1 for r in R if s in (r.get('segments') or []))} |")
for lang, label in [("Hebrew", "Hebrew-speaking families"), ("English", "English-speaking families in Israel"), ("Russian", "Russian-speaking families in Israel"), ("Arabic", "Arabic-speaking families in Israel")]:
    w(f"| {label} | {sum(1 for r in live if r['language'] == lang)} | {sum(1 for r in R if r['language'] == lang)} |")
w("")
w("## Search gaps")
w("")
w("- **Ashkelon on WhatsApp.** The WhatsApp search found no WhatsApp links on the Ashkelon municipality site, so no Ashkelon parent WhatsApp group is listed. Route: Ashkelon community centres and the city's early-childhood department.")
w("- **Arabic-speaking families in Israel.** Facebook search returned city buy-sell groups and pan-Arab pregnancy groups, none verifiably Israeli. Route: early-childhood departments of Arab local authorities.")
w("- **Russian and English speakers.** A few groups each, with ad-day or admin-approval rules. МамыАшкелона is in Ashkelon itself. Check that the shoot and the book can be in Hebrew for these families before posting.")
w("- **WhatsApp generally.** Public invites live mostly on municipal and community-centre pages and are mostly one-way. 21 invites could not be checked because WhatsApp rate-limited the checks.")
w("- **Fathers.** The אבא פגום network (136K group, 30.7K marketplace) is national; ask for the family's city in the form.")
w("- **Not searched.** Haredi, Druze and Bedouin family communities. Kiryat Gat, Kiryat Malachi and Gedera were searched on 2026-10-14 and 8 groups were added; the Ashkelon coast moshavim were not searched by name.")
w("")
w("## Other routes (pages, sites, organisations)")
w("")
w("Not communities you can post in, so not counted above. Facebook answers crawlers even for missing pages, so a working link there only means the page responded.")
w("")
w("| Priority | Type | Name | URL | Reach seen | Why | HTTP |")
w("|---|---|---|---|---|---|---|")
for o in sorted(OTH, key=lambda o: PORD.get(o.get("suggested_priority"), 2)):
    w("| " + " | ".join(esc(x) for x in [o.get("suggested_priority"), o.get("platform"), o.get("name"), o.get("url"), o.get("members"), o.get("why"), o.get("http")]) + " |")
w("")
w("## Outreach guidance")
w("")
w("- Ask the admin first whenever the rules mention approval, a business day or a thread, and post only where and when the rules allow.")
w("- Never collect children's details in comments. Every draft points to a private form. The ambassadors form is built for creators with a follower band, so families need a short sign-up form: parent name and phone, city or neighbourhood, the child's first name and age for the book, days that suit a visit, guardian confirmation, and consent that the child's face and the parent will appear on LumeBook's socials. That form does not exist yet.")
w("- Before each visit, get written consent from the parent that names where the videos will appear. Book visits by city so one trip covers several families (a suggestion, not tested).")
w("- The Hebrew drafts use the fallback voice (2 of 15 approved samples), pass the project's Hebrew lint except the slide-only word limit, write לומיבוק, mention no AI and use no em dashes.")
w("")
for title, k in [("1. Post for a local parents group", "post_general"), ("2. Short post for business-day threads and local boards", "post_short"), ("3. Private message asking an administrator for permission", "dm_admin"), ("4. Filming consent, signed before each visit (draft for a lawyer to read)", "consent")]:
    w(f"### {title}")
    w("")
    w('<div dir="rtl">')
    w("")
    for line in DR[k].split("\n"):
        w(line + "  " if line else "")
    w("")
    w("</div>")
    w("")
w("## Appendix: rejected")
w("")
w(f"{len(rej)} entries, with the reason in Notes and Promotional-post policy: expired invites, groups whose rules forbid this activity, non-Israeli groups, off-topic groups and sensitive support groups.")
w("")
w(table(rej))
w("")
w("### Named in articles, not located")
w("")
w("Listed in ynet and Kipa parenting articles, not found by name in Facebook search on 2026-10-09, not counted: מטיילים עם קטנטנים, מטיילים עם תינוקות מסביב לעולם, מניקות מעניקות, רפואה ובריאות לילדותים, מותר לך; להיות יותר מאימא, אבות מבשלים יחד.")
w("")
w("## Method and final quality check")
w("")
w("- **Discovery, best first:** Facebook group search in a logged-in browser (read-only), 50+ queries in Hebrew, English, Russian and Arabic by city and topic, about 620 raw hits and about 320 relevant; then each group's About page (287 opened); municipal and community-centre sites crawled for WhatsApp invites; creator hubs, WhatsApp directories, Linktrees and the ynet and Kipa group lists. Best queries: \"אמהות <city>\" and \"הורים <city>\". Open-web Hebrew search mostly returned news.")
w(f"- **Re-rank on {OFFER['checked']}:** distance from Ashkelon added to every row; local groups more than 80 km away and creator groups moved to C; each record keeps its 2026-10-09 grade in the data file.")
w("- **URLs:** every Facebook group URL rendered on 2026-10-09. WhatsApp invites were checked one by one until WhatsApp returned HTTP 429; rows marked unverified need a re-check. Other-route links show their HTTP status.")
w("- **Duplicates:** merged by URL and invite code; same-name groups that are separate are kept and flagged in Notes.")
w("- **Privacy:** no member lists opened, no private phone numbers or personal emails recorded, no child data collected. Nothing was joined, posted or messaged.")
w("- **Honest outreach:** every draft states the deal, the visible-face requirement, guardian-only participation, where the videos will appear, and that not everyone is accepted.")
w(f"- **Priority A:** all {cnt['A']} A rows have an activity figure and a quoted rule or About line that allows posting.")
w("")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("wrote", OUT, f"{len(L)} lines")
