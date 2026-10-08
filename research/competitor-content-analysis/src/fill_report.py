# Builds ../lumebook-competitor-content.html from db.json, table_data.json and app_shell.html.
# Run from this folder:  python3 fill_report.py
# Look and chrome come from the LumeBook design system (shared/design): design.head() inlines the stylesheet,
# design.theme_toggle() the theme button, design.logo_data_uri() the logo.
import json, os, sys, statistics as st
from collections import Counter, defaultdict
import re as _re
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(PROJECT, 'shared', 'design'))
import design
os.chdir(HERE)
R = json.load(open('db.json'))
BY = {r['key']: r for r in R}
T = open('app_shell.html').read()
T = (T.replace('__LBHEAD__', design.head())
      .replace('__THEME__', design.theme_toggle(dark_label='Dark mode', light_label='Light mode'))
      .replace('__LOGO__', design.logo_data_uri()))
ANSWER='''<div class="lb-prose">
<p><b>Build</b> a creator-led system with trackable codes (MeBook's real engine), carrying the two things nobody in the category does systematically: <b>likeness proof</b> (the real photo next to the page) and <b>answers</b> to price, delivery, effort and "is it really my kid", in short Hebrew videos. Keep the developmental angle, but win it with an expert voice and specific situations; MeBook already sells potty, pacifier, new-sibling and gan books in 10 of its 25 live ads.</p>
<p><b>Why:</b> the reveal-and-testimonial format is everywhere and sits near 1× each account's median views, so it is the entry ticket, not an edge. Customers say likeness is what they judge (<span class="he">"החברה היחידה שהפנים באמת דומים לילד"</span>), and their questions sit unanswered under competitor posts. No piece of 147 uses an expert.</p>
</div>'''
VERDICT=''.join(f'<div class="lb-card is-quiet verdict-card"><span class="lb-eyebrow">{a}</span><b>{b}</b><p class="lb-muted">{c}</p></div>' for a,b,c in [
 ('COPY','Creator codes + DM keyword','Collab posts with personal codes and "תגיבו ספר"; boost the best creator reel as an ad later.'),
 ('OUT-DO','Milestone stories','Add an expert (gannenet or child psychologist) and situations not seen in MeBook\'s sample.'),
 ('OWN','Likeness proof + FAQ answers','Customers ask for both; almost no competitor supplies either.'),
 ('SKIP FOR NOW','Generic gift flip-throughs','Every brand runs them; nothing in the data shows them standing out.')])
T=T.replace('__ANSWER__',ANSWER).replace('__VERDICT__',VERDICT)

def L(key, label=None):
    r = BY[key]
    return f'<a href="{r["url"]}" target="_blank" rel="noopener">{label or key.split("_",2)[2]}</a>'
def he(s): return f'<span class="he">{s}</span>'

# ---------------- findings ----------------
F = [
 ("MeBook's real engine is creators with codes, then paid amplification",
  "high", ["Copy the mechanism", "₪0-compatible"],
  f"""11 of MeBook's latest 12 Instagram reels were posted by creators or parents as collab posts, not by MeBook. 6 of them carry a personal code or a comment-for-code funnel: TALLY10 ({L('mebook_ig_DbAfvCdowT3')}), Atias40 ({L('mebook_ig_DV6fjEojHSs')}), mayah ({L('mebook_ig_DV5ekKViujI')}), Adib ({L('mebook_ig_DWOgOcmjAtx')}), and {he('"תגיבו ספר"')} ({L('mebook_ig_DbydNecM1GW')}, {L('mebook_ig_DVlyDocjXU4')}). MeBook also runs 25 active video ads, 18 of them launched 18–30 Sep. Its #3 ad by impressions ({L('mebook_ad_975833858878326','ad 975833858878326')}) is Lovie Malespin's creator reel {L('mebook_ig_DdCPPrKKRXG')}, matched on 95% of transcript words.""",
  "Lumebook can't match the ad spend, but codes + collab posts + the DM keyword cost nothing beyond a free book, and they solve the attribution problem (no baseline analytics)."),
 ("The developmental angle Lumebook chose on 1 Oct is already in MeBook's paid mix",
  "high", ["Repositions the edge"],
  f"""10 of MeBook's 25 live ads sell a milestone: potty training / pacifier weaning (6), new sibling (2), starting daycare (2). Its #2 ad by impressions is a co-brand with Materna (baby formula), offering {he('"סיפור MEBOOK אישי ב-AI רק ב-99 ₪ במקום 139 ₪"')} to Materna club members for the new-sibling book ({L('mebook_ad_2137767587097061','Materna ad, 38 days live')}). Organic milestone testimonials run at 1.2× median, the best of MeBook's repeatable patterns.""",
  "The edge can't be 'books for milestones'. It has to be how well Lumebook does it: an expert voice (0 of 147 pieces use one), situations not seen in MeBook's sample (fears, moving, hospital, a parent away; check MeBook's catalogue before claiming), and a series format. Also note the price anchor: MeBook ₪139 / ₪99 via partner vs Lumebook ₪119."),
 ("Big reach comes from novelty and craft, not from testimonials",
  "med", ["One-offs ≠ patterns"],
  f"""The largest outliers in the sample: Hooray Heroes' dog-book launch with an illustrator drawing on screen, 1.2M views (136× its TikTok median, {L('hoorayheroes_tt_7464548168877886742')}); its print-house clip, 422K, 48× ({L('hoorayheroes_tt_7473465819977092374')}); Wonderbly's 2023 range flip-through, 527K, 406× ({L('wonderbly_tt_7315373892745432352')}); Liron Ofir's improvised bedtime story turned into a MeBook book, 86.6K, 22× ({L('mebook_ig_Db79B6COOSN')}). Reveals and testimonials cluster at about 1×.""",
  "Behind-the-scenes of how the book is made repeats across two brands (Wonderbly's 4 BTS pieces median 1.5×), so that part is a pattern. The single viral hits are not reproducible on demand. Plan one 'how a photo becomes a book' piece per week as the reach slot; don't plan for virality."),
 ("Abroad, 'not AI' is a selling point. In Israel nobody is punishing AI yet",
  "med", ["Risk to watch"],
  f"""Under Hooray Heroes' 1.2M video the top comments are "this is made by real artists yall" (931 likes), "It's sad this art style was stolen by ai…" (539), "HUGE props for not using AI" (462). Wonderbly buyers write "I was so glad to find something that wasn't AI". In MeBook's Hebrew comments the only AI remark is a joke that it made a creator look thinner. MeBook says "AI" in its own ads, and a parent calls it a plus: {he('"מוצר מדהים, משולב טכנולוגיית AI"')} ({L('mebook_fb_920176889526452')}).""",
  "Don't hide AI, but give it a human face: who writes the stories, the professional reviewer, the editing step. That's insurance if the US/UK mood reaches Israel, and it is the BTS reach slot from finding 3."),
 ("Customers judge on likeness, yet almost nobody proves it on screen",
  "high", ["Own it"],
  f"""Hebrew commenters use resemblance as the quality bar: {he('"אין על MeBook החברה היחידה שהפנים באמת דומים לילד"')}, {he('"זה יצא בול שי לי"')}. English buyers of avatar books complain about the opposite: "4 different options for fair skin children and 1 option each for brown and black children", no same-sex couples, missing dog breeds. Only 10 of 147 pieces show the real photo next to the illustration (6 MeBook, 4 Hooray Heroes pets).""",
  "A recurring 'same face' format, real photo → page, side by side, in the first 2 seconds, is Lumebook's cleanest proof and it is unclaimed. It also answers the unspoken AI-quality doubt."),
 ("Comment sections are an unanswered FAQ, and Yoto shows what to do with it",
  "high", ["Own it"],
  f"""Under MeBook's 14 organic IG/TikTok posts: price ×4 ({he('"מה מחיר?"')}, {he('"כמה עולה"')}), delivery time ×2, how to order / link ×4, coupon ×1, {he('"אבל אנחנו צריכים לכתוב בפנים את הסיפור?"')} (do we write it ourselves?), an upload failure on TikTok, and a 5-books-per-child group order. None has a visible brand answer in the sample. Yoto turns questions into a recurring "answering your questions" / Tip Tuesday series: 5 FAQ pieces at a median 1.2×, and its beginner tutorials hit 7× on TikTok ({L('yoto_tt_7678000505532075296')}).""",
  "A weekly Hebrew answer video (\"שאלתם: …\") converts objections into content, gives the DM-keyword funnel something to point to, and costs only a phone and 30 minutes."),
 ("Collab engagement measures the creator's friends, not demand",
  "high", ["Measurement"],
  f"""On MeBook's collab reels many comments come from the creator's circle ({he('"כפרה דודה שלה"')}, {he('"החברה הכי טובה שלייי"')}, {he('"אלופה שלייייייי"')}). The 86.6K Liron reel's comments are laughter and "אפשר פרק 2?" with almost no purchase intent. The comment-keyword posts inflate comments with one-word {he('"ספר"')} replies.""",
  "Judge barter creators by code uses, DM-keyword leads and preview starts (UTM), never by likes. Pick creators whose audience is parents of 2–6-year-olds, not the creator's friends."),
 ("Gifters are a paid-media persona the organic feeds mostly ignore",
  "med", ["Hanukkah"],
  f"""MeBook's #1 ad by impressions speaks to the aunt or grandmother: {he('"ספר הרפתקאות אישי שבו הנכד או האחיין שלך הוא הכוכב הראשי"')} ({L('mebook_ad_2333886484096183')}). 14 of Wonderbly's 36 pieces target grandparents or relatives, timed to Christmas ("Never too soon for Christmas 🎄"). Gifter comments recur: "I can not wait to buy my grandson some for Christmas!" Organic reels from all four rarely speak to gifters directly.""",
  "From 1 Nov, version every pillar for the gifter (P2): grandma's voiceover, 'what to bring instead of another toy', with the Hanukkah cutoff."),
 ("Nobody in the book category makes retention or expert content",
  "high", ["Gap"],
  f"""Retention-stage pieces: Yoto 5 (tutorials, Tip Tuesday), every book brand 0. Expert endorsement: 0 of 147. The closest thing is an unprompted comment by a literature teacher under a MeBook reel: {he('"בתור מורה לספרות אני אומרת לך יש לזה ערך מטורף וחיבור רגשי שהילד יוצר עם הספר"')} ({L('mebook_ig_DWOgOcmjAtx')}).""",
  "Two open lanes: (1) a gannenet / child-psychologist voice on the milestone pillar, which fits the professional reviewer already planned; (2) 'the book 3 months later' and second-book or sibling content for existing customers."),
 ("TikTok looks empty in this category",
  "low", ["Cheap test"],
  f"""Hooray Heroes hasn't posted on TikTok since Nov 2025, Wonderbly since Oct 2025 (60-video listings). MeBook has 2 TikToks and 56 followers, yet its family story video about a girl's new-class worries got 31.2K views ({L('mebook_tt_7545096813838093574')}). Lumebook has no TikTok account (Oct 2 research).""",
  "Cross-post every Reel to a new Lumebook TikTok for 6 weeks; zero extra production. Low confidence: we only checked these four brands, not the whole Hebrew TikTok market."),
]
fh = []
for t, conf, tags, ev, impl in F:
    cl = {'high':'success', 'med':'accent', 'low':'warning'}[conf]
    lbl = {'high':'high confidence','med':'medium','low':'hypothesis'}[conf]
    fh.append(f'<li class="lb-card"><h3>{t}</h3><div class="ev">{ev}</div><div class="so"><b>So:</b> {impl}<div class="lb-row tags"><span class="lb-chip {cl}">{lbl}</span>' + ''.join(f'<span class="lb-chip">{x}</span>' for x in tags) + '</div></div></li>')
T = T.replace('__FINDINGS__', '\n'.join(fh))

# ---------------- pillars ----------------
PIL = [
 ("1 · Milestone stories", "35%", "P1, P3",
  "A real family's specific situation (new sibling, gan, potty, night fears) told by the parent, with a 10-second expert line from a gannenet or child psychologist, ending on the child reading their book.",
  f"Funnel: awareness → consideration. Format: phone-shot parent voiceover + reveal; expert cut-in. Series: \"הספר שעזר לנו עם…\". Evidence: MeBook's milestone testimonials are its best repeatable organic pattern (1.2×) and 10 of its 25 ads; expert voice appears in 0 of 147 pieces (finding 9); the playbook already plans a professional reviewer."),
 ("2 · Same face (likeness proof)", "20%", "P1, P2",
  "Real photo → illustrated page, side by side, in the first 2 seconds; then the child's reaction to 'that's me'.",
  f"Funnel: consideration. Format: 6–9s split-screen, Stories + Reels. Series: \"זה באמת הוא?\". Evidence: likeness is the customers' quality bar (finding 5); only 10 of 147 pieces show a photo next to the page; MeBook's POV split-screen collab is the one example ({L('mebook_ig_DbAfvCdowT3')})."),
 ("3 · First look (barter creators)", "20%", "P1, P2",
  "A creator's child sees the book for the first time, posted as a collab with a personal code and the DM keyword.",
  "Funnel: awareness → conversion. Format: raw phone reveal. Evidence: universal pattern (≈1× median everywhere: entry ticket, not edge), but it carries codes and attribution (finding 1). Brief creators to open on the photo-vs-page moment (pillar 2) and name the milestone (pillar 1) so these posts aren't generic."),
 ("4 · How it's made (human + AI)", "15%", "All",
  "From photo upload to printed book: who writes the stories, the reviewer's check, the print, the parcel. Founder or team on camera.",
  "Funnel: awareness. Format: process montage + voiceover. Evidence: BTS is the one repeatable reach pattern across two brands (finding 3) and answers the AI doubt before it grows (finding 4); MeBook's founder interview ran at 1.8× on Facebook."),
 ("5 · You asked (FAQ answers)", "10%", "P1, P2, P3",
  "One real comment question per video, answered in 20 seconds: price, delivery days, 'do I write the story?', photo tips, group orders for gan.",
  f"Funnel: consideration → conversion, and retention (photo tips, re-ordering). Format: talking head + screen recording. Evidence: unanswered questions under competitor posts (finding 6); Yoto's FAQ/tutorial series ({L('yoto_tt_7692062518386199830')}, {L('yoto_tt_7685789348322757910')})."),
]
ph = []
for name, share, pers, what, why in PIL:
    ph.append(f'<div class="lb-card pillar"><div><h3>{name}</h3><span class="lb-chip accent">{share} of Reels · personas {pers}</span><p>{what}</p></div><div class="ev" style="min-width:0">{why}</div></div>')
T = T.replace('__PILLARS__', '\n'.join(ph))

# ---------------- tests ----------------
TESTS = [
 ("T1 · Milestone reveals by barter creators with codes", "Start week of 6 Oct",
  dict(Hypothesis="Creator reveals framed around a named milestone drive more free-preview starts per 1K views than generic 'special gift' reveals.",
       Insight="MeBook's milestone testimonials are its strongest repeatable organic pattern (1.2×) and it backs them with 10 ads; generic gift reveals sit at ~1×.",
       Pillar="1 + 3", Persona="P1 parent of a 2–6yo facing a change", Angle="child_development + emotion", Format="Raw phone reveal, collab post",
       Hook="\"שבועיים לפני שהאח הקטן נולד, הכנתי לה ספר שבו היא האחות הגדולה\" (situation first, then the photo-vs-page moment)",
       Creator="6 micro-creators (5–30K, parents of 2–6yo), free book barter", CTA="Personal code + \"תגיבו ספר\" DM keyword + UTM",
       Pieces="6 milestone vs 4 generic-gift reveals (same creators' pool)", Period="6 Oct – 9 Nov",
       Primary="Free-preview starts per 1K views (UTM + code)", Secondary="Code uses, DM-keyword comments, saves, shares, 3s hold if creators share insights",
       Support="Milestone pieces ≥1.5× the generic pieces on preview starts per 1K views", Reject="No difference, or generic wins on preview starts",
       Next="If supported: test which milestone wins (sibling vs gan vs fears); then whitelist the top piece when budget exists")),
 ("T2 · 'Same face' side-by-side series", "Start week of 13 Oct",
  dict(Hypothesis="Showing the real photo next to the illustrated page in the first 2 seconds raises hold rate and preview starts vs a standard reveal.",
       Insight="Customers judge on likeness; only 10 of 147 competitor pieces prove it on screen.",
       Pillar="2", Persona="P1, P2", Angle="proof + transformation", Format="6–9s split-screen Reel + Story",
       Hook="Photo on the left, page on the right: \"זה באמת הוא?\"", Creator="In-house edit from customer photos (with consent) + barter creators",
       CTA="Free preview link", Pieces="8 side-by-side vs 4 standard reveals", Period="13 Oct – 16 Nov",
       Primary="3-second hold rate (IG insights) and preview starts", Secondary="Saves, shares, 'is it really him' comments",
       Support="Hold rate ≥20% higher than standard reveals; preview starts not lower", Reject="No hold-rate lift",
       Next="Use the winning side-by-side as the opening shot in every creator brief")),
 ("T3 · Weekly Hebrew FAQ answer", "Start week of 6 Oct",
  dict(Hypothesis="Answering one real objection per week (price, delivery, effort) lifts link clicks and DM leads more than a parenting-tip post in the same slot.",
       Insight="Price, delivery, 'how to order' and 'do we write it?' sit unanswered under MeBook posts; Yoto's FAQ/tutorial series runs at 1.2× (FAQs) to 7× (tutorials).",
       Pillar="5", Persona="P1, P2, P3", Angle="objection_handling + convenience", Format="Talking head + screen recording, 20s",
       Hook="Screenshot of the question as the first frame: \"שאלתם: צריך לכתוב את הסיפור לבד?\"", Creator="In-house (you or Yossi)",
       CTA="Free preview link; pin a comment with the answer", Pieces="6 FAQ videos replacing 6 parenting-tip posts", Period="6 Oct – 16 Nov",
       Primary="Profile link clicks per post", Secondary="Saves, DMs, preview starts",
       Support="FAQ posts ≥2× the link clicks of the tip posts they replace", Reject="Equal or lower",
       Next="Turn the top 3 answers into a highlight and a landing-page FAQ block")),
 ("T4 · How it's made (human + AI)", "Start week of 20 Oct",
  dict(Hypothesis="A process video (photo → story writer → reviewer → print) reaches further than product demos and pre-empts AI-quality doubts.",
       Insight="BTS is the one reach pattern repeated by two brands (HH 1.2M / 422K; Wonderbly BTS median 1.5×); 'not AI' sentiment abroad.",
       Pillar="4", Persona="All", Angle="novelty + proof", Format="Process montage + founder voiceover",
       Hook="\"ככה תמונה אחת הופכת לספר של 24 עמודים\"", Creator="Founder / team", CTA="Free preview", Pieces="3", Period="20 Oct – 16 Nov",
       Primary="Reach to non-followers (IG insights)", Secondary="Shares, saves, AI-related comments (sentiment)",
       Support="Non-follower reach ≥2× Lumebook's Oct median", Reject="Below median",
       Next="If supported: monthly BTS slot; test the reviewer on camera")),
 ("T5 · Gifter version before Hanukkah", "Start 1 Nov",
  dict(Hypothesis="The same reveal re-cut for grandparents/aunts ('instead of another toy') drives more preview starts from Facebook than the parent cut.",
       Insight="MeBook's #1 ad by impressions targets the aunt/grandmother; Wonderbly targets grandparents in 14 pieces.",
       Pillar="1–3 re-cut", Persona="P2 gifter", Angle="emotion + gift", Format="Grandma voiceover over a reveal",
       Hook="\"במקום עוד צעצוע שישכח בארון\"", Creator="Barter creator's parent/grandparent", CTA="Free preview + Hanukkah cutoff",
       Pieces="4 gifter cuts vs 4 parent cuts, cross-posted to FB", Period="1 – 22 Nov",
       Primary="Preview starts by UTM (FB vs IG)", Secondary="Shares, tags",
       Support="Gifter cuts ≥1.3× parent cuts on FB preview starts", Reject="No difference",
       Next="Brief a Hanukkah gifter creator wave")),
 ("T6 · TikTok cross-post", "Start week of 6 Oct",
  dict(Hypothesis="Cross-posting Reels to a new TikTok account yields reach at near-zero cost because the category is inactive there.",
       Insight="HH and Wonderbly stopped posting; MeBook has 2 TikToks, one at 31.2K views.",
       Pillar="All", Persona="P1", Angle="n/a", Format="Same Reels, native captions",
       Hook="Same as IG", Creator="n/a", CTA="Link in bio", Pieces="All Reels for 6 weeks", Period="6 Oct – 16 Nov",
       Primary="Median views per post vs IG median", Secondary="Profile → site clicks",
       Support="TikTok median views ≥ IG median", Reject="Below half the IG median after 6 weeks",
       Next="If supported: test one TikTok-native format (storytime)")),
 ("T7 · Parent storyteller series (entertainment)", "Opportunistic",
  dict(Hypothesis="An improvised parent bedtime story turned into a Lumebook book, posted as a series, earns reach and follow-through ('episode 2?').",
       Insight="Liron Ofir's story → MeBook book, 86.6K (22×); comments ask for a sequel and a kids' show.",
       Pillar="Reach slot", Persona="P1", Angle="entertainment + connection", Format="Creator storytelling + book reveal",
       Hook="The creator's own story opener", Creator="1 dad/mom storyteller creator (barter)", CTA="Free preview",
       Pieces="2 episodes", Period="Nov", Primary="Reach + follower growth", Secondary="Code uses (expect low)",
       Support="Episode 1 > 5× Lumebook median and episode 2 holds ≥50% of it", Reject="Episode 1 < 2×",
       Next="Only continue if codes show any sales; otherwise treat as brand reach")),
]
th = []
for name, when, d in TESTS:
    rows = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in d.items())
    th.append(f'<details class="lb-card"{" open" if name.startswith("T1") else ""}><summary>{name} <span class="lb-chip tint">{when}</span></summary><dl class="lb-kv">{rows}</dl></details>')
T = T.replace('__TESTS__', '\n'.join(th))

# ---------------- competitor systems ----------------
def bars(comp, field, n=5):
    rs = [r for r in R if r['competitor'] == comp]
    c = Counter((r['coded'].get(field) or '?') for r in rs).most_common(n)
    mx = c[0][1]
    return '<div class="lb-hbars">' + ''.join(f'<div class="lb-hbar"><span class="lb-truncate" title="{k}">{k}</span><span class="track"><i style="width:{v/mx*100:.0f}%"></i></span><span class="v">{v}</span></div>' for k, v in c) + '</div>'
SYS = {
 'mebook': ("MeBook (IL, direct)", "43 pieces · IG 15K, FB 5K, TikTok 56 followers", {
   "Machine": "Creator collabs on IG with personal codes → best creator reels and parent testimonials run as Meta ads (25 live, 18 launched 18–30 Sep) → partner distribution (Materna club, ₪99).",
   "Personas": "Parents of 0–8 (most), parents facing a change (13 pieces), aunts/grandparents (12, incl. the #1 ad).",
   "Pains / aspirations": "New sibling, potty, pacifier, daycare, first grade, confidence / keepsake, 'a gift they won't forget'.",
   "Hooks": "Outcome-first (11), problem-first (7), reaction (6). Hebrew speech in 31 of 43.",
   "Proof": "Customer testimonial (20), child reaction (18), close-up (17); photo-vs-page only 6.",
   "CTA": "Codes and DM keyword (organic); ads mostly consideration (17/25), 6 conversion with codes / abandoned-cart offers.",
   "Cadence": "IG reels ~2/month on its grid (Mar–Sep 2026), mostly via collabs; ad bursts before holidays.",
   "Strengths": "Attribution via codes; partner channel; milestone ads; raw parent voices.",
   "Weaknesses": "Organic reach is borrowed (creator-circle engagement); TikTok unused; FAQs unanswered; little likeness proof."}),
 'hoorayheroes': ("Hooray Heroes (US, direct)", "31 pieces · IG 253K, TikTok 66.5K", {
   "Machine": "Organic-only in this sample (no active video ads found by keyword; unverified under other page names). Batches of creator/customer pet-book videos posted the same day, plus occasional launches and BTS.",
   "Personas": "Gift buyers, pet owners (12 pet pieces), couples; children are on screen in only 7 of 31.",
   "Pains / aspirations": "Pet loss / keepsake, 'looks exactly like him', love stories / memory, connection.",
   "Hooks": "Story (8), demonstration (6), reaction (5).",
   "Proof": "Product close-up (21), testimonials (12); real-dog-vs-illustration (4).",
   "CTA": "Mostly none; link in bio.",
   "Cadence": "TikTok 1.3/week over its last 60, silent since 10 Nov 2025; IG reels slowed (last in sample 12 Jun 2026).",
   "Strengths": "Hand-drawn craft as proof (1.2M BTS); emotional pet niche.",
   "Weaknesses": "Inconsistent; many low-view near-duplicate UGC posts; avatar limits drive complaints (breeds, same-sex couples)."}),
 'wonderbly': ("Wonderbly (UK, direct)", "36 pieces · IG 599K, TikTok 12.9K", {
   "Machine": "~130 active video ads in a GB Ad Library search for “wonderbly”, mostly launched 21 Sep for Christmas: review-quote cards, gift moments, creator partnership ads run from creators' pages. Ambassador codes posted by fans in comments.",
   "Personas": "Parents 3–8 (24 pieces), gifters / grandparents (14 pieces).",
   "Pains / aspirations": "Keepsake, Christmas tradition, reluctant readers, sibling jealousy, 'they grow up fast'.",
   "Hooks": "Demonstration (7), social proof (5), story (4).",
   "Proof": "Close-up (18), child reaction (12), testimonials (11), creator endorsement (5).",
   "CTA": "Shop / learn more; ambassador codes (15BTESS, AMB2026JAYDE15) in comments.",
   "Cadence": "IG ~3 reels/month; TikTok inactive since Oct 2025.",
   "Strengths": "Seasonal paid machine; craft BTS; licensed books (Guinness World Records).",
   "Weaknesses": "Diversity / appearance complaints; delivery and order-error complaints in public comments."}),
 'yoto': ("Yoto (UK, adjacent best-in-class)", "37 pieces · IG 258K, TikTok 60.3K", {
   "Machine": "High-cadence brand-made content (30 of 37 in-house): launches, FAQ answers, Tip Tuesday tutorials, comparisons; creator partnership ads with codes (Harley10).",
   "Personas": "Parents 3–8 and 0–3; gift buyers around launches.",
   "Pains / aspirations": "Screen time, bedtime, travel, independent play / calm, confidence in buying the right device.",
   "Hooks": "Demonstration (15), question (5), story (5).",
   "Proof": "Product close-up (23); child reaction (8).",
   "CTA": "Comment keywords, pre-order, codes in creator ads.",
   "Cadence": "TikTok 4.6/week; IG ~4 reels/week.",
   "Strengths": "Covers retention (5 pieces) and objections (5); series formats people can expect.",
   "Weaknesses": "Launch backlash plays out in comments ('looks so juvenile', regional availability)."}),
}
sh = []
for comp, (name, sub, kv) in SYS.items():
    dl = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in kv.items())
    sh.append(f'<article class="lb-card sys-card"><h3>{name}</h3><div class="lb-dim lb-xs">{sub}</div><p class="lb-stat-label">Pillars</p>{bars(comp,"pillar")}<p class="lb-stat-label">Funnel</p>{bars(comp,"funnel_stage",4)}<p class="lb-stat-label">Creator</p>{bars(comp,"creator_type",4)}<dl class="lb-kv">{dl}</dl></article>')
T = T.replace('__SYSTEMS__', '\n'.join(sh))

# ---------------- outliers table ----------------
OUT = [
 ('hoorayheroes_tt_7464548168877886742', 'Launch of dog books: illustrator drawing on a tablet + voiceover (Jan 2025)', 'One-off launch; the visible artist sparked the "real artists, not AI" thread'),
 ('hoorayheroes_tt_7473465819977092374', 'Print-house binding process, 15s (Feb 2025)', 'BTS craft, repeated by Wonderbly'),
 ('wonderbly_tt_7315373892745432352', 'Woman flips through the range: "one for every grandchild" (Dec 2023)', 'Old, Christmas, gifter angle; not repeated since'),
 ('hoorayheroes_ig_DW1lbRsDKoM', 'Dog-mom creator, "I\'ll never forget who made me a mom first", #gifted', 'Identity hook + niche creator audience'),
 ('mebook_ig_Db79B6COOSN', "Liron Ofir's improvised bedtime story turned into a MeBook book", "Borrowed audience; comments ask for episode 2, not prices"),
 ('wonderbly_tt_7315377164940086561', 'Creator: "3 steps to creating a personalized kids book" screen walk-through', 'How-it-works is repeatable'),
 ('yoto_ig_DdGi63cAprh', '4th-gen player launch (985 comments, heavy backlash)', 'Launches pull reach; comments ≠ approval'),
 ('yoto_tt_7678000505532075296', '2-minute beginner guide', 'Tutorials outperform on Yoto TikTok'),
]
oh = []
for k, what, read in OUT:
    r = BY[k]
    oh.append(f'<tr><td>{L(k, r["competitor"].replace("hoorayheroes","Hooray Heroes").replace("mebook","MeBook").replace("wonderbly","Wonderbly").replace("yoto","Yoto")+" · "+r["platform"].replace("Instagram","IG"))}</td><td class="num">{r["views"]:,}</td><td class="num">{r["outlier_index"]:.0f}×</td><td>{what}</td><td>{read}</td></tr>')
T = T.replace('__OUTLIERS__', '\n'.join(oh))

# ---------------- pattern table ----------------
pc = defaultdict(Counter); po = defaultdict(list)
for r in R:
    p = (r['coded'].get('repeatable_pattern') or '').replace('other:', '')
    if p.startswith(('ugc_repost', 'review_quote', 'abandoned', 'regret', 'seasonal', 'animated', 'creator_story', 'print', 'parent_testimonial', 'tip_tuesday', 'beginners', 'card_rec', 'new_card', 'event', 'lifestyle', 'travel', 'grandma', 'draw', 'shelf', 'creator_pet', 'creator_recipe', 'cause')):
        p = {'review_quote_card':'review_quote_card','review_quote_over_unboxing':'review_quote_card','review_quote_trending_audio':'review_quote_card','tip_tuesday_tutorial':'faq_answer / tutorial','beginners_guide_tutorial':'faq_answer / tutorial','print_house_bts':'artist_bts / craft','parent_testimonial_voiceover':'milestone_testimonial','parent_testimonial_vo':'milestone_testimonial','regret_testimonial_voiceover':'milestone_testimonial','seasonal_nostalgia_testimonial':'gift_moment','abandoned_cart_code':'static_offer'}.get(p, 'other')
    p = {'artist_bts':'artist_bts / craft','founder_bts':'artist_bts / craft','faq_answer':'faq_answer / tutorial'}.get(p, p)
    pc[p][r['competitor']] += 1
    if r['source'] == 'organic' and r.get('outlier_index'): po[p].append(r['outlier_index'])
rows = []
for p, c in sorted(pc.items(), key=lambda x: -sum(x[1].values())):
    if p in ('other', ''): continue
    med = f'{st.median(po[p]):.1f}×' if po[p] else 'n/a'
    rows.append(f'<tr><td><code>{p}</code></td>' + ''.join(f'<td class="num">{c.get(k) or ""}</td>' for k in ['mebook','hoorayheroes','wonderbly','yoto']) + f'<td class="num">{med} <span class="lb-dim">(n={len(po[p])})</span></td></tr>')
T = T.replace('__PATTERNTABLE__', '\n'.join(rows))

# ---------------- voice ----------------
V = f"""
<div class="lb-table-wrap"><table class="lb-table mid top">
<thead><tr><th>Theme</th><th>Verbatim (sample)</th><th>Use it in</th></tr></thead><tbody>
<tr><td><b>Likeness = quality</b><br><span class="lb-dim lb-xs">MeBook, IL</span></td><td><span class="he">"אין על MeBook החברה היחידה שהפנים באמת דומים לילד" · "זה יצא בול שי לי" · "הוא ממש בתוך הסיפר"</span></td><td>Hooks (pillar 2), landing-page hero, ad headline: "בול הוא"</td></tr>
<tr><td><b>Price / delivery / how</b><br><span class="lb-dim lb-xs">MeBook, IL</span></td><td><span class="he">"מה מחיר?" · "כמה עולה" · "תוך כמה זמן מגיע ההזמנה?" · "איך מזמינים??" · "שלחי קישור" · "יש קופון?"</span></td><td>FAQ series (pillar 5), pinned comments, site FAQ</td></tr>
<tr><td><b>Effort confusion</b></td><td><span class="he">"אבל אנחנו צריכים לכתוב בפנים את הסיפור?"</span></td><td>Hook: "לא צריך לכתוב כלום. דקה, תמונה, וזהו."</td></tr>
<tr><td><b>Upload friction</b></td><td><span class="he">"מנסה ליצור לא מצליח להעלות תמונה אשמח לעזרה"</span> (TikTok, no visible reply)</td><td>Photo-tips video; check Lumebook's upload flow on mobile</td></tr>
<tr><td><b>Group / gan orders</b></td><td><span class="he">"כמה זמן צריכה להזמין מראש צריכה 5 ספרים לכל ילד כמה ע העלות"</span></td><td>B2B kindergarten offer in FAQ; gannenet creators</td></tr>
<tr><td><b>Keepsake</b></td><td><span class="he">"מזכרת לעוד שנים רבות" · "נפלא לילדים ממש מזכרת לשנים"</span> · "you'll miss this" (Wonderbly ad)</td><td>Gifter cuts, captions</td></tr>
<tr><td><b>Expert value (unprompted)</b></td><td><span class="he">"בתור מורה לספרות אני אומרת לך יש לזה ערך מטורף וחיבור רגשי שהילד יוצר עם הספר"</span></td><td>Recruit educators as voices (pillar 1)</td></tr>
<tr><td><b>Ownership proof</b></td><td><span class="he">"גם לנו יש" · "גם אני הזמנתי לבן שלי לגיל שנה" · "הזמנתי 🤞🏼"</span></td><td>Social proof captions; UGC repost asks</td></tr>
<tr><td><b>Series appetite</b></td><td><span class="he">"אפשר פרק 2?" · "למה באלי המשך" · "תוכנית ילדים, כל פרק סיפור!"</span></td><td>T7 storyteller series</td></tr>
<tr><td><b>"Not AI" (EN)</b><br><span class="lb-dim lb-xs">HH, Wonderbly</span></td><td>"this is made by real artists yall" (931♥) · "HUGE props for not using AI" (462♥) · "I was so glad to find something that wasn't AI"</td><td>Pillar 4: show the humans in the loop</td></tr>
<tr><td><b>Avatar limits (EN)</b></td><td>"4 different options for fair skin children and 1 option each for brown and black children" · "you can't make these for same-sex couples" · "Please add Saint Bernard!"</td><td>Pillar 2: "every face, from your own photo"</td></tr>
<tr><td><b>Ops complaints in public (EN)</b></td><td>"I order 1 month ago I didn't receive the order" · wrong book received · "40 dollars for a book??"</td><td>Lesson: answer service issues fast in comments</td></tr>
</tbody></table></div>
<div class="lb-prose"><p class="lb-note">Counts and quotes come from deduplicated comment files. MeBook: 266 unique comments; Hooray Heroes 230; Wonderbly 491; Yoto 287. Most comments are praise or tags; the buying signals above are the minority that matter.</p></div>
"""
T = T.replace('__VOICE__', V)

# ---------------- gaps ----------------
G = [
 ("1 · Everyone does it, appears to work", False, ["Real family first-look reveal (all 3 book brands)", "Parent testimonial with phone footage", "Creator partnerships with codes (MeBook, Wonderbly, Yoto)"], "Do it, but as the vehicle for pillars 1–2, not as the message."),
 ("2 · Everyone does it, saturated", False, ["'The most special gift' flip-through to music (MeBook 5 ads, Wonderbly, HH)", "Static offer / review-quote cards", "Generic keepsake captions"], "Skip at ₪0; nothing in the data shows these standing out organically."),
 ("3 · Competitors rarely do it", True, ["Likeness proof, photo next to page (10 of 147)", "FAQ / objection answers (Yoto only, 5)", "Behind-the-scenes of making the book (8 across all)", "Retention content (Yoto only, 5)", "Founder on camera (MeBook 1)"], "Pillars 2, 4, 5 live here."),
 ("4 · Nobody does it, customers ask for it", True, ["Expert voice (0 of 147) vs the teacher comment", "Public answers to price / delivery / 'do I write it?'", "Series storytelling ('אפשר פרק 2?')", "Group / gan ordering explained on social", "Upload help"], "Strongest differentiation: expert milestone series + FAQ answers."),
]
gh = []
for t, hot, items, so in G:
    gh.append(f'<article class="lb-card bucket{" is-accent" if hot else ""}"><h3>{t}</h3><ul>' + ''.join(f'<li>{i}</li>' for i in items) + f'</ul><p class="ev"><b>So:</b> {so}</p></article>')
T = T.replace('__GAPS__', '\n'.join(gh))

# ---------------- method ----------------
M = """
<div class="lb-prose">
<h3>Workflow</h3>
<ol class="tight">
<li><b>Competitor selection.</b> Searched Israeli and international AI / personalised-book brands; probed TikTok listings and IG follower counts. Kept 3 direct + 1 adjacent for depth.</li>
<li><b>Collection.</b> IG: latest 12 reels per brand with grid view counts (Instagram caps the grid; deeper history was blocked by rate limits, so I stopped to protect your account). TikTok: full 60-video listing per brand (views, likes, shares, saves), sampled the latest 12–14 + top 3–5. Meta Ad Library: active video ads sorted by Meta's impressions ranking (MeBook all 25; Wonderbly top 12 + creator partnership ads; Yoto top 10). MeBook FB page: 4 visible reels.</li>
<li><b>Listening.</b> Every video downloaded with yt-dlp and transcribed locally with Whisper (Hebrew: large-v3-turbo, first 60s; English: small.en, first 60s). 7 ads were served without audio and coded from visuals + ad text. Child speech transcribes imperfectly.</li>
<li><b>Watching.</b> Timestamped contact sheets per video (watch-video skill). Haiku agents coded each piece from the sheets + a dossier (caption, account, metrics, transcript, top comments). Sonnet reviewed every coding against the dossier and taxonomy. I checked key items myself against frames (✓ in the table), including the Materna ₪99 ad, the Hooray Heroes artist video, the dog-mom outlier and the Tali Admon POV reel, and fixed 3 codings.</li>
<li><b>Comments.</b> TikTok: public comment endpoint (up to 150 per video). IG: top ~60 per reel through your logged-in session, read-only, paced. Hebrew read by me; English via a Haiku pass plus my keyword review.</li>
</ol>
<h3>Database schema</h3>
<p>One row per piece. Identity: brand, platform, source (organic/paid), URL, date, posting account or ad page. Metrics: followers, views, likes, comments, shares, saves (TikTok), ad rank by impressions, days active, multiple versions. Normalised: view efficiency, engagement rate by views, share/save rate, outlier index. Coded: pillar, funnel stage, format, creator type, hook type + verbatim hook text, angle (≤2), proof (list), persona (≤2), pain, aspiration, core angle sentence, product feature / use case, CTA type + text, production style, sound, child on screen, paid signals, repeatable pattern, comment sentiment, friend tags, buying-intent quotes, objections, customer language, why it may have worked (hypothesis), Lumebook test idea, evidence split into observed / spoken / inferred, confidence, review note. Full list in <code>competitor_content_db.csv</code>; allowed values in <code>taxonomy.md</code>.</p>
<h3>Taxonomy (summary)</h3>
<ul class="tight">
<li><b>Pillar (what it's for):</b> product_demo, reveal_reaction, customer_story, social_proof, problem_awareness, parenting_education, gift_occasion, product_range, offer_promo, behind_scenes, entertainment, community_ugc_repost, comparison_objection, brand_mission.</li>
<li><b>Format (how it's made):</b> ugc_testimonial, creator_demo, talking_head, founder_led, screen_recording, product_demo_broll, reaction_video, voiceover_montage, text_on_screen_montage, carousel, static, meme_trend, skit, street_interview, before_after, animation_ai.</li>
<li><b>Hook:</b> problem_first, curiosity, contrarian, outcome_first, identity, social_proof, question, mistake, comparison, demonstration, shock_surprise, story, reaction, gift_prompt, offer.</li>
<li><b>Angle:</b> pain, aspiration, convenience, identity, status, speed, savings, fear_loss, skepticism, comparison, transformation, novelty, proof, objection_handling, emotion_nostalgia, child_development, connection.</li>
<li><b>Funnel rule for ambiguous posts:</b> judge by what the last 30% and the caption ask for. Buy with an incentive or deadline → conversion; buy without incentive but shows mechanics → consideration; no ask → awareness; speaks to existing owners → retention. Paid ≠ automatically conversion.</li>
</ul>
<h3>Normalised metrics</h3>
<ul class="tight">
<li><b>Outlier index</b> = views ÷ account median on that platform (IG: 12-reel grid; TikTok: last 60 videos). The main comparison measure; it controls for audience size.</li>
<li><b>View efficiency</b> = views ÷ followers. Distorted by collab posts (the creator's audience) and by ads.</li>
<li><b>Engagement by views</b> = (likes + comments) ÷ views. Distorted by comment-keyword CTAs and giveaway mechanics.</li>
<li><b>Better business signals</b> (for Lumebook's own tracking): preview starts by UTM, code uses, DM-keyword leads, profile→link clicks, saves, shares, price/delivery questions, friend tags, branded search.</li>
</ul>
<h3>Limits: read before quoting</h3>
<ul class="tight">
<li>No sales data. Ad Library rank is Meta's ordering of active ads, not spend or results; ads have no public views. Days active ≠ success when most ads launched 2 weeks ago.</li>
<li>IG views come from the grid and include collab audiences; FB views from the page grid; Hooray Heroes showed no active video ads by keyword search (it may run them under another page name).</li>
<li>Sample sizes per pattern are small (n in the pattern table). Treat medians as directional.</li>
<li>Coding was done by models from frames and transcripts; spot-checked, not fully audited. Hebrew on-screen text was verified only on the ✓ items.</li>
<li>Some links (ad library, IG) may need a login to view.</li>
</ul>
</div>
"""
T = T.replace('__METHOD__', M)
T = T.replace('__DATA__', open('table_data.json').read())
T=_re.sub(r'(?<=\d)–(?=\d)','-',T)
T=T.replace(' – ',' to ').replace('–','-').replace(' — ',', ').replace('—',', ')
open('../lumebook-competitor-content.html', 'w').write(T)  # run from src/
print('dashes left:',T.count('—'),T.count('–'))
print('ok', len(T)//1024, 'KB', '__' in T.replace('__rows', '').replace('__proto', ''))
