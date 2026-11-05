#!/usr/bin/env python3
"""Reels Explorer: one page to browse everything LumeBook has for Reels (the November calendar, the filming research,
the 63 principles, the other video research, the tools, the finished reel jobs).

Reads the sources, never copies their text by hand where a file has it:
  src/scripts/series-2026-11/reels.json   the calendar (edit there, rebuild here)
  playbook.md                             findings, seven approaches, five concepts, weak choices, what to log
  smm-research/principles.md              the 63 principles
The tool list, the other research cards and the reel-job list are written below (CATALOG), from the READMEs and memory
notes of 5 Nov 2026; update them when a tool or a job is added.

Build:  python3 research/israeli-product-reels/src/build_reels_explorer.py
Output: research/israeli-product-reels/reels-explorer.html (inlines the design system, like every internal page)
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent
ROOT = RES.parents[1]
sys.path.insert(0, str(ROOT / "shared" / "design"))
import design  # noqa: E402

OUT = RES / "reels-explorer.html"

LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def clean(s):
    """Markdown to plain text: links keep their label, bold and code lose their marks."""
    s = LINK.sub(r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- calendar
SERIES = {
    1: ("לפני שמזמינים", "Before you order", 4),
    2: ("הספר של הילד שלך", "Your child's book", 2),
    3: ("מתנה לחנוכה", "Hanukkah gift", 8),
    4: ("ירין בודק", "Yarin tests it", 5),
    5: ("רגע בבית", "A moment at home", 6),
    6: ("טרנדים מוכנים", "Ready trends (dropped)", 7),
    7: ("ימי מבצע", "Sale days", 1),
    8: ("מסבתא לנכד", "From grandma", 3),
}

EN_HOOK = {
    "1.1": "What if it won't look like my kid?",
    "1.7": "3 things to know before you order",
    "1.6": "Which book suits my child?",
    "2.6": "The photo next to the cover. You decide",
    "1.2": "How long does ordering take? Let's time it",
    "2.1": "This is how a child's book is born",
    "1.4": "Grandma, what do you get in the book?",
    "7.1": "11.11, a day for one",
    "3.1": "A Hanukkah gift that doesn't end after the eighth candle (החנוכה שלי)",
    "2.7": "The moment he finds out he's inside the book",
    "5.3": "The same bedtime story every night?",
    "1.3": "Birthday on Thursday. Will it arrive in time?",
    "4.1": "I made a book from my photo at age 4",
    "3.2": "Grandparents, what do you buy your grandchild for Hanukkah?",
    "1.5": "Grandma, what if I didn't like it?",
    "3.3": "Order by when for Hanukkah?",
    "2.3": "A new sibling? There's a book for that",
    "5.1": "The last night with the pacifier",
    "3.4": "Aunts and uncles, this is your Hanukkah gift this year",
    "2.4": "Forgot a birthday gift?",
    "2.5": "Siblings? Each one gets their own book",
    "4.2": "You asked in the comments, I answer",
    "2.8": "Grandma, what do you write in the dedication?",
    "5.5": "A superhero, without a cape (הלב של יובל)",
    "8.2": "A first birthday for your grandchild? A first book for them (חברים צבעוניים)",
    "8.1": "Grandma, is your grandchild's birthday coming up? (יום הולדת)",
    "5.4": "Saying goodbye to diapers? (עדן והחיות החופשיות)",
    "7.2": "Grandma, Black Friday. A book for every grandchild",
    "5.2": "\"Again?\" for the hundredth time",
    "2.2": "[Name]'s book has arrived",
    "7.3": "Cyber Monday. Order from the couch",
}

STATUS = {
    "posted": "Posted",
    "needs-voice": "Needs Yarin's voice and clip",
    "needs-footage": "Needs real footage",
}


def load_reels():
    r = json.loads((HERE / "scripts" / "series-2026-11" / "reels.json").read_text(encoding="utf-8"))
    reels = []
    for x in r["reels"]:
        reels.append({
            "id": x["id"], "date": x["date"], "series": x["series"], "status": x["status"],
            "hook": x["hook"], "en": EN_HOOK.get(x["id"], ""), "approach": x["approach"],
            "shot": x.get("shot") or "", "vo": x.get("vo") or [], "caption": x.get("caption") or "",
            "footage": x.get("footage") or [], "films": x.get("yarin_films") or [], "notes": x.get("notes") or "",
            "audience": x.get("audience", "parents"), "page": x.get("page") or "",
        })
    dropped = [{"id": x["id"], "date": x["date"], "hook": x["hook"], "why": x.get("dropped") or (x.get("notes") or "").split(". ")[0]} for x in r["dropped"]]
    d = r["defaults"]
    return {
        "reels": reels, "dropped": dropped, "shoots": r["shoots"],
        "defaults": {"post_time": d.get("post_time"), "channel": d.get("channel"), "cta_screen": d.get("cta_screen"),
                     "cta_voice": d.get("cta_voice"), "cta_caption": d.get("cta_caption")},
        "series": {str(k): {"he": v[0], "en": v[1], "cat": v[2]} for k, v in SERIES.items()},
    }


# ---------------------------------------------------------------- playbook
def playbook():
    t = (RES / "playbook.md").read_text(encoding="utf-8").split("\n")
    text = "\n".join(t)

    def section(start, end):
        a = text.index(start)
        b = text.index(end, a + 1)
        return text[a:b]

    # 1. findings: numbered, "**Title.** rest"
    s1 = section("## 1. What the 173 Reels show", "## 2. Seven approaches")
    findings = []
    for m in re.finditer(r"^\d+\. \*\*(.+?)\*\* (.*)$", s1, re.M):
        findings.append({"title": clean(m.group(1)).rstrip("."), "body": clean(m.group(2))})

    # 2. approaches: table rows "| A | Name | What | examples | who |"
    s2 = section("## 2. Seven approaches", "### A. Story with a turn")
    approaches = []
    for line in s2.split("\n"):
        m = re.match(r"^\| ([A-G]) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|$", line)
        if m:
            codes = re.findall(r"instagram\.com/reel/([^/)]+)/", m.group(4))
            approaches.append({"k": m.group(1), "name": clean(m.group(2)), "what": clean(m.group(3)),
                               "codes": codes, "who": clean(m.group(5))})

    # 3. weak choices table
    s3 = section("## 3. Weaker choices in the sample, and what to do instead", "## 4. Five LumeBook Reel concepts")
    weak = []
    for line in s3.split("\n"):
        m = re.match(r"^\| (.+?) \| (.+?) \| (.+?) \|$", line)
        if m and not m.group(1).startswith(("What I saw", "---")):
            weak.append({"saw": clean(m.group(1)), "where": clean(m.group(2)), "fix": clean(m.group(3))})

    # 4. concepts
    s4 = section("## 4. Five LumeBook Reel concepts", "## 5. Your first shoot")
    concepts = []
    for m in re.finditer(r"^### Concept (\d): \"(.+?)\" \((.+?)\)\n(.*?)(?=^### Concept |\Z)", s4, re.M | re.S):
        body = m.group(4)

        def field(name):
            f = re.search(r"^- \*\*" + name + r":\*\* (.*)$", body, re.M)
            return clean(f.group(1)) if f else ""
        concepts.append({"n": int(m.group(1)), "he": m.group(2), "en": clean(m.group(3)), "idea": field("Idea"),
                         "response": field("Intended response"), "length": field("Length"),
                         "honesty": field("Honesty rule")})

    # 7. what to log
    s7 = section("## 7. After posting: what to log", "## 8.")
    log = [clean(x[2:]) for x in s7.split("\n") if x.startswith("- ")]
    log_intro = clean(s7.split("\n")[2]) if len(s7.split("\n")) > 2 else ""

    return {"findings": findings, "approaches": approaches, "weak": weak, "concepts": concepts, "log": log,
            "log_intro": log_intro}


# ---------------------------------------------------------------- principles
GROUPS = [
    ("H", "The hook", "First 3 seconds", 1), ("R", "Keep them watching", "Retention and interaction", 2),
    ("C", "Call to action", "What you ask for", 3), ("S", "What to show", "Product, proof, people", 4),
    ("E", "Editing", "Cuts, speed, sound", 5), ("K", "Topic", "What the Reel is about", 6),
    ("F", "Filming", "How it is shot", 7), ("T", "Text and caption", "On screen and in the post", 8),
]


def principles():
    t = (RES / "smm-research" / "principles.md").read_text(encoding="utf-8")
    items = []
    for m in re.finditer(r"^### ([A-Z])(\d+)\. (.+?)\n(.*?)(?=^### |^## |\Z)", t, re.M | re.S):
        body = m.group(4)

        def field(name):
            f = re.search(r"^- \*\*" + name + r":\*\* (.*)$", body, re.M)
            return clean(f.group(1)) if f else ""
        strength = field("Strength")
        word = re.match(r"[A-Za-z]+", strength)
        items.append({"id": m.group(1) + m.group(2), "g": m.group(1), "title": clean(m.group(3)),
                      "rule": field("Rule"), "strength": word.group(0).lower() if word else "",
                      "why": strength, "lb": ("Overridden 05 / 11 / 2026: Yarin decided reels never mention the price, so LumeBook shows no price at all. " if m.group(1) + m.group(2) == "S3" else "") + field("For LumeBook"), "overlaps": field("Overlaps with"),
                      "evidence": field("Full evidence")})
    return {"groups": [{"k": g[0], "name": g[1], "sub": g[2], "cat": g[3]} for g in GROUPS], "items": items}


# ---------------------------------------------------------------- catalog (written by hand)
CATALOG = {
    "asof": "05 / 11 / 2026",
    "rules": [
        {"t": "Every reel includes Yarin", "d": "No stand-alone trend clips. Yarin talks to camera for a 2 second hook and records the voiceover.",
         "src": "reels.json, dropped note of 05 / 11 / 2026"},
        {"t": "A real voice, not a preset", "d": "ElevenLabs preset voices were rejected as not warm, Israeli or like a mom. Use a real recording.",
         "src": "memory: feedback-reel-voice-and-captions (24 Oct 2026)"},
        {"t": "Bold white hook, word-by-word captions", "d": "Hook at the top, captions on the lowest safe line, CTA on screen for the last seconds. Nothing in the top 14%, bottom 35% or outer 6% of the frame.",
         "src": "memory above; playbook rules F2 and T4"},
        {"t": "Never mention the price", "d": "No amount, no discount, no sale, no second-book price and no delivery cost in a hook, voiceover, card or caption. reels.py lint fails it.",
         "src": "Yarin, 05 / 11 / 2026; overrides principle S3"},
        {"t": "No language options, no digital copy", "d": "The content is in Hebrew for a Hebrew speaking Israeli audience, so a reel never talks about the languages the book comes in, and nobody cares about the digital copy, so it is never mentioned. reels.py lint fails both.",
         "src": "Yarin, 05 / 11 / 2026, in the calendar's comment box"},
        {"t": "Search line and up to 5 hashtags", "d": "Every caption has one plain line of words parents search for and up to 5 specific hashtags, just above the לומי line.",
         "src": "principle T7"},
        {"t": "One CTA: the word לומי", "d": "Comment the word, get a personal link by DM. The same action in voice, on screen and in the caption.",
         "src": "reels.json defaults; playbook C1 and C3"},
        {"t": "Trial reel at 21:30", "d": "One reel a day on Instagram lumebook.il as a trial reel, one time all month so results compare.",
         "src": "reels.json defaults"},
        {"t": "No child's face in LumeBook's own reels", "d": "A creator's child appears only with the parent's written OK, and a child's name on a cover stays hidden.",
         "src": "playbook S5; memory: feedback-reel-voice-and-captions"},
        {"t": "Nothing goes up without Yarin's OK", "d": "The draft goes to Yarin first; Postiz schedules only after the OK.",
         "src": "november-calendar.md, step 5"},
    ],
    "library": [
        {"id": "lib-israeli", "t": "Israeli product Reels", "when": "15 and 18 Oct 2026", "n": "173 Reels, 108 creators",
         "d": "197 Reels watched, 173 verified, 24 excluded. Each verified Reel is answered on eight questions (hook, every few seconds, CTA, what is shown, editing, topic, filming, text), each answer citing a principle.",
         "find": ["35 of 41 first-round Reels show the product within 2 seconds; across all 173 it is 150.",
                  "Personalised-book Reels nearly all use a child on camera (29 of 36) and almost none shows the price (1 of 36).",
                  "Hands-only, no-face Reels were the weakest group: median 0.45 plays per follower against 0.76.",
                  "Comment words collect requests, not proof of buying."],
         "path": "research/israeli-product-reels/", "url": "https://claude.ai/artifact/3JRcb77z4HcE8PRcVjcpEp", "urlLabel": "Open the research page"},
        {"id": "lib-creator-brief", "t": "Creator Reel brief", "when": "15 Oct 2026", "n": "Hebrew, not sent yet",
         "d": "The brief for barter creators: shot skeleton, one worry with checked facts, CTA, caption with the disclosure line, do-not list, checklist.",
         "find": ["Built on approach A (story with a turn).", "Hebrew linted by src/lint_creator_brief.py.", "Public at lumebook-creator-brief.vercel.app."],
         "path": "research/israeli-product-reels/creator-brief.md", "url": "https://claude.ai/artifact/8aHom1FHtP9jiSgBkbgGc7", "urlLabel": "Open the brief"},
        {"id": "lib-kids", "t": "Kids content lab", "when": "6 Oct 2026", "n": "64 short videos",
         "d": "Kids brands, experts and AI or faceless videos, each broken down for solo creation: no kids on camera, not an expert.",
         "find": ["12 formats and 10 lessons.", "Off-product parent tips beat brand reach by a wide margin.", "Result-first hands demos and mistake-then-fix scripts work.", "The photo-to-cartoon wipe trend is LumeBook's own product."],
         "path": "research/kids-brand-content-research/", "url": "https://claude.ai/artifact/4Uaprv274bf69dH5KkQyPY", "urlLabel": "Open the lab"},
        {"id": "lib-competitor", "t": "Competitor content teardown", "when": "3 Oct 2026", "n": "147 pieces",
         "d": "MeBook, Hooray Heroes, Wonderbly and Yoto: posts, ads and Reels, coded and compared.",
         "find": ["MeBook's engine is creator collabs with personal codes; 11 of its 12 latest Reels were posted by creators.", "Expert endorsement appears in 0 of 147 pieces.", "Likeness proof (photo beside the page) appears in only 10."],
         "path": "research/competitor-content-analysis/", "url": "https://claude.ai/artifact/XRuKAwrXNwf6iPfkLG8o7f", "urlLabel": "Open the report"},
        {"id": "lib-conversion", "t": "Creator content vs purchase intent", "when": "14 Oct 2026", "n": "41 creators, 469 posts, 2,982 comments",
         "d": "Which creator content makes people talk about buying, and which only earns attention.",
         "find": ["Attention is not buying talk.", "The store already has ambassador links and UTM attribution."],
         "path": "research/creator-content-conversion/report.md", "url": "", "urlLabel": ""},
        {"id": "lib-yossi", "t": "Reels showcase for Yossi", "when": "2 Oct 2026", "n": "35 videos",
         "d": "Proven TikToks and Reels, each with what happens, why it worked and how LumeBook could copy it. Also the first social benchmarks.",
         "find": ["LumeBook's last 12 Reels on 2 Oct: 28 to 151 views, median 48.", "MeBook's Reels: mostly 1.3K to 5.6K, median about 4K; one creator collab reached 86.5K."],
         "path": "memory: lumebook-reels-examples-2026-10", "url": "https://claude.ai/artifact/VXmpAd4VLAKKJ4KMwvWuZn", "urlLabel": "Open the showcase"},
        {"id": "lib-notes", "t": "Four research passes", "when": "18 Oct 2026", "n": "63 principles",
         "d": "Platform documentation, studies and industry data on hooks and retention, CTA and text, what is shown and filmed, and editing and topic. Every source was opened; for most paywalled papers only the abstract was read.",
         "find": ["notes/hooks-retention.md", "notes/cta-text.md", "notes/shown-filmed.md", "notes/edit-topic.md", "sample-check.md compares each principle with the 173 Reels' public counts."],
         "path": "research/israeli-product-reels/smm-research/", "url": "", "urlLabel": ""},
        {"id": "lib-method", "t": "Social video research method", "when": "Oct 2026", "n": "How the research was done",
         "d": "yt-dlp and Instagram browser tricks, the 200 result cap on web search, and checking any machine reading of Hebrew myself.",
         "find": ["Used for every study above."], "path": "memory: social-video-research-method", "url": "", "urlLabel": ""},
    ],
    "tools": [
        {"id": "t-reel-editor", "t": "reel-editor skill", "kind": "Skill",
         "d": "Burns a bold white hook at the top and optional word-by-word captions into a reel, inside Instagram's safe zone. Makes trial versions: a seeded flip, a small zoom and a slight trim per version, so no two uploads are the same file. Adds the Higgsfield reference's sound to silent results.",
         "how": "Say \"reel editor\", \"caption this reel\" or \"make 5 versions for trial reels\"", "path": ".claude/skills/reel-editor/",
         "extra": "scripts/reel_editor.py (Pillow draws, ffmpeg burns), transcribe.py, emoji_png.swift"},
        {"id": "t-reels-py", "t": "reels.py (November series tool)", "kind": "Script",
         "d": "Single source for the month: reels.json builds every script and the calendar, lints the Hebrew and fails any mention of the price (Yarin, 05 Nov 2026) and checks scripts against the principles (T5, T6, C1, T7), opens a media project per reel with edit.json and the reel's UTM link, assembles and burns the reel (make), and after posting pulls the Meta export numbers into a results table by series and approach.",
         "how": "python3 research/israeli-product-reels/src/scripts/series-2026-11/reels.py build | lint | status | new <id> | make <id> | link <id> | done <id> | results | log <id> lumi=.. dms=.. | report | merge FILE",
         "path": "research/israeli-product-reels/src/scripts/series-2026-11/", "extra": "Outputs november-calendar.md, november-calendar.html and reel-series-scripts.md. Edit reels.json, not those files."},
        {"id": "t-calendar-page", "t": "November reel calendar page", "kind": "Page",
         "d": "The month as a page, one reel a day from 05 to 30 / 11 / 2026, with scripts, filming days and captions. Edits made on the page are merged back with reels.py merge.",
         "how": "Open the artifact", "path": "research/israeli-product-reels/src/scripts/series-2026-11/november-calendar.html",
         "url": "https://claude.ai/artifact/DGXzTyAGSYLXmAeYjRPt1E", "urlLabel": "Open the calendar page"},
        {"id": "t-recipe-11", "t": "The reel 1.1 edit recipe", "kind": "Recipe",
         "d": "The template for the month: Yarin's talking hook clip at 1x, voiceover with pauses cut to 0.1 s and the studio chain, everything after the intro at 1.1x, screen recordings in a centred 720x1440 window over a blurred book clip, top hook only during the intro, word-by-word captions, the purple לומי CTA for the last 3 seconds, Instagram music at 30%.",
         "how": "reels.py make <id> runs it from the reel's edit.json (reel_make.py, 05 Nov 2026); build_v9.py stays as the original", "path": "research/israeli-product-reels/src/scripts/series-2026-11/reel_make.py",
         "extra": "Two modes: hook clip + voiceover over segments (1.1), or one talking take with jump cuts (1.7). Captions take the script's spelling, cuts land on script words, number cards on top. Rebuilt 1.1 from its raw takes in one command: 16.7 s against the posted 16.5 s."},
        {"id": "t-watch", "t": "watch-video skill", "kind": "Skill",
         "d": "Watches a local or downloadable video through platform captions and timestamped frames. It produced the frame strips and breakdowns for the research.",
         "how": "Ask to watch or break down a video", "path": "~/.claude/skills/watch-video/", "extra": "Its Python venv also has Pillow, which the reel editor uses."},
        {"id": "t-higgsfield", "t": "Higgsfield CLI and skills", "kind": "Service",
         "d": "Video and image generation. Genjutsu motion transfer for trend recreations, Wan 2.7 for talking shots that lip-sync to an existing voice, Seedance 2.5, reframe to 9:16, Bytedance upscale, custom voices.",
         "how": "higgsfield generate create <job type> ... then generate wait <id>",
         "path": "skills: higgsfield-generate, higgsfield-soul-id and others",
         "extra": "Costs and limits on 15 and 16 Oct: Genjutsu 15 s is 45 credits at 480p and 105 at 720p. The free Genjutsu Lite (10 a month on the Plus plan) works only on the website, forced to object swap. Check with generate cost, which is free."},
        {"id": "t-fal", "t": "fal.ai connector", "kind": "Service",
         "d": "Stills with nano-banana-2 and chained edits for consistent characters, Hebrew speech with ElevenLabs v4, word timings with Scribe v2, and sync-lipsync v3 to put a new voice on a good picture. Retired for carousel pictures only.",
         "how": "MCP tools mcp__fal-ai__*", "path": "memory: lumebook-genjutsu-fan-transition-2026-10; reel-build-toolchain"},
        {"id": "t-whisper", "t": "Hebrew transcription (ivrit-ai Whisper)", "kind": "Script",
         "d": "Word timestamps for Hebrew, used to cut at word boundaries and to check takes nobody can hear. Faster-whisper with the ivrit-ai large-v3 model is cached locally.",
         "how": "KMP_DUPLICATE_LIB_OK=TRUE /usr/bin/python3 ...", "path": ".claude/skills/reel-editor/scripts/transcribe.py"},
        {"id": "t-chain", "t": "ffmpeg, avconvert and Pillow chain", "kind": "Recipe",
         "d": "iPhone clips are HLG HDR, so convert them first with macOS avconvert (the local ffmpeg has no zscale and washes colours out). Text cards are drawn with Pillow in Heebo, with the line reversed and digit runs re-reversed for RTL. Join shots with the concat filter, not stream copy.",
         "how": "avconvert --preset Preset1920x1080", "path": "memory: reel-build-toolchain", "extra": "The Drive connector downloads stop at 10 MB."},
        {"id": "t-postiz", "t": "Postiz", "kind": "Service",
         "d": "Schedules Instagram and Facebook posts for lumebook.il. Always ask before posting. An Instagram carousel holds at most 10 images.",
         "how": "postiz CLI and the postiz skill", "path": "memory: reference-postiz"},
        {"id": "t-lint", "t": "Hebrew voice lint", "kind": "Script",
         "d": "Checks every hook, voiceover line, card and caption against Yarin's Hebrew rules (punctuation, RTL, wording). reels.py lint runs it on the whole month.",
         "how": "python3 .../reels.py lint", "path": "carousel/carousel-pipeline/scripts/voice_lint.py", "extra": "The lumebook-hebrew-voice skill holds the voice."},
        {"id": "t-research-build", "t": "Research build and check scripts", "kind": "Script",
         "d": "build_research_page.py renders the research page; build_principles.py builds the 63 principles from the four notes; evidence_check.py compares each principle with the 173 Reels; check_table.py validates the 8-question table; build_creator_brief.py and lint_creator_brief.py handle the brief.",
         "how": "python3 research/israeli-product-reels/src/<script>.py", "path": "research/israeli-product-reels/src/"},
        {"id": "t-research-page", "t": "Product Reels Playbook page", "kind": "Page",
         "d": "The full research as one app: the eight tools, a page per principle, concept, deep dive and Reel, the proof board and a pre-post checklist.",
         "how": "Open the artifact", "path": "research/israeli-product-reels/reels-research.html", "url": "https://claude.ai/artifact/3JRcb77z4HcE8PRcVjcpEp", "urlLabel": "Open the playbook page"},
        {"id": "t-insights", "t": "Instagram Insights log", "kind": "Process",
         "d": "24 hours after posting, log the skip rate, average watch time, sends per reach and the share of views from non-followers. Compare concepts by books started and DMs, not plays.",
         "how": "A trial reel tests two hooks on the same footage", "path": "playbook.md, section 7"},
    ],
    "jobs": [
        {"slug": "2026-11-03-reel-1-1-preview-screen", "kind": "Own reel", "status": "posted", "size": "653 MB", "t": "Reel 1.1, the template for the month",
         "d": "Posted 04 / 11 / 2026 at 21:31 as a trial reel. Versions build_v3 to build_v9; the final recipe is build_v9.py.", "tools": "reel-editor, ffmpeg, Pillow"},
        {"slug": "2026-10-24-grandma-baking-book-reel", "kind": "Own reel", "status": "active", "size": "912 MB", "t": "Grandma baking book",
         "d": "A gift-for-a-grandchild reel (playbook concept 5) from Drive close-ups. Also an 8 s cut and mom-voice versions in each creator's own narration. Ready for review; the family's OK for the child's name and photo is still needed.", "tools": "ElevenLabs v4, Pillow, ffmpeg"},
        {"slug": "2026-10-13-reels-superhero-book", "kind": "Own reel", "status": "active", "size": "123 MB", "t": "Superhero book reels 1 to 4",
         "d": "Cut from a WhatsApp reading session.", "tools": ""},
        {"slug": "2026-10-14-reel-captions-1014", "kind": "Captions", "status": "", "size": "149 MB", "t": "Caption versions of a 14 Oct reel",
         "d": "Three captioned versions, one flipped. Has build.py and captions.json; not in the media index.", "tools": "reel-editor"},
        {"slug": "2026-10-29-reel-1029", "kind": "Captions", "status": "", "size": "90 MB", "t": "Reel rebuilt from Yarin's CapCut cut",
         "d": "No speed-up, 30 fps, word-by-word captions, hook and purple CTA. Not in the media index.", "tools": "reel-editor"},
        {"slug": "2026-10-29-car-yap-ugc", "kind": "UGC", "status": "", "size": "120 MB", "t": "Car yap UGC",
         "d": "Seedance 2.5 picture with a real recorded Hebrew voice; sentence boxes instead of word captions and the child's name hidden on the cover. Not in the media index.", "tools": "Higgsfield Seedance 2.5, fal lipsync"},
        {"slug": "2026-10-20-bedtime-story-reel", "kind": "Creator footage", "status": "active", "size": "38 MB", "t": "Bedtime story reel",
         "d": "In the style of a MeBook bedtime-story reel, built from Sapir's clips of Ariel's book. A free draft exists; waiting for Yarin's approval and the 4 raw clips over 10 MB.", "tools": ""},
        {"slug": "2026-10-16-creator-reels", "kind": "Creator footage", "status": "active", "size": "20 KB", "t": "Creator reels gallery",
         "d": "A gallery page of 22 creator videos about the book (7 creators) from the Drive folder, plus 5 re-cuts in 9x16. Videos stay in Drive.", "tools": "build.py"},
        {"slug": "2026-10-25-genjutsu-lite-trends", "kind": "Trend", "status": "done", "size": "", "t": "Six free Genjutsu Lite trends",
         "d": "Six trend recreations from Higgsfield's community feed: the book turning in 3D, Ben reading in a night window, mom eating cake from the fridge, Lume dancing among books, Ben and Lume dancing, mom after bedtime. All free, website only, 1080p, with sound added. Five caption versions of the window one exist for trial reels.", "tools": "Higgsfield Genjutsu Lite"},
        {"slug": "2026-10-21-genjutsu-ben-truck-jump", "kind": "Trend", "status": "active", "size": "", "t": "Ben and the jumping toy truck",
         "d": "A giant toy truck jumps over Ben in a chair. Five caption versions for trial reels with random flip and slight trim.", "tools": "Genjutsu 480p, reel-editor"},
        {"slug": "2026-10-19-genjutsu-ben-dance-lume", "kind": "Trend", "status": "active", "size": "40 MB", "t": "Ben dances, Lume films",
         "d": "Genjutsu 480p, 45 credits. Upscale pending.", "tools": "Genjutsu"},
        {"slug": "2026-10-16-dj-ben-reel", "kind": "Trend", "status": "active", "size": "66 MB", "t": "DJ Ben and dancing Lume",
         "d": "Reframed from landscape to 9:16 in two halves, aligned, then Genjutsu 480p. Upscale pending.", "tools": "Higgsfield reframe, Genjutsu"},
        {"slug": "2026-10-16-genjutsu-truck-box", "kind": "Trend", "status": "done", "size": "51 MB", "t": "Truck box, the birthday book comes out",
         "d": "The book comes out of the box instead of a hoodie. v2 final has a clean cover and a Hebrew voice. Product-swap trends work, but Genjutsu regenerates the whole scene.", "tools": "Genjutsu, Bytedance upscale, ElevenLabs v4"},
        {"slug": "2026-10-15-genjutsu-lume-rapper", "kind": "Trend", "status": "done", "size": "34 MB", "t": "Lume as the rapper",
         "d": "Motion transfer into the red-venue crowd trend, plus a cheaper Kling test that drifted off the face.", "tools": "Genjutsu, fal Kling 2.6"},
        {"slug": "2026-10-11-fan-transition-reel", "kind": "Trend", "status": "done", "size": "23 MB", "t": "Fan-transition outfit reel",
         "d": "Kid, kid and mom, family, with the book only in the last look. Stills on fal, video on Higgsfield 720p.", "tools": "fal nano-banana-2, Genjutsu"},
        {"slug": "2026-10-13-text-pull-ben-reel", "kind": "Trend", "status": "done", "size": "22 MB", "t": "Text-pull reel with Ben",
         "d": "", "tools": ""},
        {"slug": "2026-10-10-genjutsu-hotel-lobby", "kind": "Trend", "status": "done", "size": "7.5 MB", "t": "Hotel lobby Genjutsu inputs",
         "d": "Reference clip, mascot, toddler and prompt.", "tools": "Genjutsu"},
        {"slug": "2026-10-12-podcast-strawberries", "kind": "Podcast", "status": "done", "size": "550 MB", "t": "Strawberry-truck episode",
         "d": "25.5 s, Lume and a kid co-host in the purple studio, clean and Hebrew-subtitled, plus reels B, C, v1 and v2.", "tools": "Higgsfield Wan 2.7, ElevenLabs v4"},
        {"slug": "2026-10-12-podcast-lume-pilot", "kind": "Podcast", "status": "done", "size": "91 MB", "t": "Podcast talking-shot pilot",
         "d": "Wan 2.7 lip-syncs to an existing take; 10 credits per 4 s.", "tools": "Wan 2.7"},
        {"slug": "2026-10-12-podcast-studio-set", "kind": "Podcast", "status": "done", "size": "23 MB", "t": "Purple podcast studio angles", "d": "", "tools": ""},
        {"slug": "2026-10-12-boys-interviews", "kind": "Podcast", "status": "done", "size": "9.6 MB", "t": "Boys interview audio", "d": "Per boy and combined.", "tools": ""},
        {"slug": "2026-10-11-lume-character-pack", "kind": "Characters", "status": "done", "size": "197 MB", "t": "Lume mascot pack", "d": "13 angles in final/.", "tools": ""},
        {"slug": "2026-10-11-toddler-character-pack", "kind": "Characters", "status": "done", "size": "198 MB", "t": "Toddler Ben pack", "d": "13 angles in final/.", "tools": ""},
        {"slug": "2026-10-15-israeli-product-reels", "kind": "Research footage", "status": "done", "size": "712 MB", "t": "47 Israeli creator Reels",
         "d": "Videos, frames, contact sheets, transcripts and annotated strips for the research. Other creators' work, internal study only.", "tools": "watch-video"},
    ],
}


HE_DIR = HERE / "he"          # Hebrew translations of the English research text, one JSON per source (written 05 Nov 2026)
JOB_STATUS = {"posted": "פורסם", "active": "פעיל", "done": "הושלם"}
S3_NOTE = "בוטל ב 05 / 11 / 2026: ירין החליט שרילס לעולם לא מזכירים מחיר, ולכן לומבוק לא מציגה מחיר בכלל. "


def hebrew(data):
    """Overlay the Hebrew translations (src/he/*.json). A missing file or key keeps the English text, so the page still builds."""
    def load(name):
        f = HE_DIR / name
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    he = load("principles.json")
    if he:
        for g in data["principles"]["groups"]:
            o = he["groups"].get(g["k"])
            if o:
                g.update(name=o["name"], sub=o["sub"])
        for it in data["principles"]["items"]:
            o = he["items"].get(it["id"])
            if o:
                it.update(title=o["title"], rule=o["rule"], lb=o["lb"])
            if it["id"] == "S3" and not it["lb"].startswith("בוטל"):
                it["lb"] = S3_NOTE + it["lb"].replace("Overridden 05 / 11 / 2026: Yarin decided reels never mention the price, so LumeBook shows no price at all. ", "")
    pb = load("playbook.json")
    if pb:
        for k in ("findings", "approaches", "weak", "concepts", "log"):
            if len(pb[k]) == len(data["playbook"][k]):
                data["playbook"][k] = pb[k]
        data["playbook"]["log_intro"] = pb["log_intro"]
    cat = load("catalog.json")
    if cat:
        for k in ("rules", "library", "tools", "jobs"):
            if len(cat[k]) == len(data["catalog"][k]):
                data["catalog"][k] = cat[k]
    return data


def main():
    sys.path.insert(0, str(HERE))
    import hub_calendar
    reels_json = json.loads((HERE / "scripts" / "series-2026-11" / "reels.json").read_text(encoding="utf-8"))
    cal = hub_calendar.parts(reels_json)
    data = {"calendar": load_reels(), "playbook": playbook(), "principles": principles(), "catalog": CATALOG,
            "jobStatus": JOB_STATUS,
            "cal": {k: cal[k] for k in ("brief", "legend", "filters", "grid")}}
    data = hebrew(data)
    pj = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    tpl = (HERE / "reels_explorer_template.html").read_text(encoding="utf-8")
    cards = cal["cards"] + cal["dialog"].replace('<dialog id="dlg"', '<dialog dir="rtl" lang="he" id="dlg"') + cal["ask_cfg"]
    html = (tpl.replace("__DESIGN_HEAD__", design.head()).replace("__LOGO__", design.logo_data_uri())
            .replace("__THEME_TOGGLE__", design.theme_toggle()).replace("__CAL_CSS__", cal["css"])
            .replace("__CAL_CARDS__", cards).replace("__CAL_JS__", cal["js"]).replace("__DATA__", pj))
    OUT.write_text(html, encoding="utf-8")
    n = data["principles"]["items"]
    print(f"wrote {OUT.relative_to(ROOT)}  {len(html)//1024} KB  reels {len(data['calendar']['reels'])}  "
          f"principles {len(n)}  findings {len(data['playbook']['findings'])}  approaches {len(data['playbook']['approaches'])}  "
          f"concepts {len(data['playbook']['concepts'])}  weak {len(data['playbook']['weak'])}  hebrew {'yes' if (HE_DIR / 'principles.json').exists() else 'not yet'}")


if __name__ == "__main__":
    main()
