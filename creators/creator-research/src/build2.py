import json, csv, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
P=lambda f: os.path.join(HERE,f)
# LumeBook design system (shared/design): stylesheet, fonts, theme script and logo are inlined, the page is a single-file artifact
sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))),"shared","design"))
import design
C=json.load(open(P('C_all.json')))
CT=json.load(open(P('contacts.json')))
for c in C:
    k=CT.get(c['h'],{}); c['email']=', '.join(k.get('email',[])); c['phone']=', '.join(k.get('phone',[])); c['csrc']='; '.join(k.get('src',[]))
exec(open(P('enrich.py')).read()); enrich(C)
KIDS=json.load(open(P('kids.json')))
# offer facts come from shared/facts.json, so the map's messages and checks use the same numbers as every other component
FACTS=json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))),"shared","facts.json"),encoding="utf-8"))
OF=FACTS["offer"]
OFFER={"pct":OF["allocation_pct"],"ex":[OF["split_example"]["creator_earnings_pct"],OF["split_example"]["audience_discount_pct"]]}
assert sum(OFFER["ex"])==OFFER["pct"], "the split example must add up to the allocation"
for c in C:
    if c['h'] in KIDS: c['kids']=KIDS[c['h']]
for i,c in enumerate(C):
    p3=str(c.get('extra',''))=='pass3'
    c['ai']=i; c['added']='2026-10-11' if p3 else '2026-10-03'; c['batch']=3 if p3 else 2 if str(c.get('extra','')).startswith('pass2') else 1; c['chk']='11 Oct 2026' if p3 else '3 Oct 2026'
for c in C:
    if c['h']=='edenmomlife': c['arch']='Homeschool / alternative ed'
O={
"knafaim.ot_by_noy":(1,"Gift a book + affiliate code; one reel + story, organic first; ask for whitelisting if it performs","Gan-adjustment story read with a child","Consideration (trust)","Saves + shares per view; preview starts via her code/UTM"),
"eden_spaiev":(1,"Gift-only barter; ask for raw footage too","At-home play ideas built on the book","Consideration + ad creative","Collab-reel views vs her 9.2K median; usable raw clips"),
"yeladim_ktanim":(1,"Gift 4 books (one per child) + affiliate code","Four kids' reactions + one activity per book","Awareness → consideration","'Where from?' comments; code orders"),
"etti_haft":(1,"Gift-only barter + B2B intro to her gan","Letter hunt on the child's own name","Consideration; B2B gan lead","Saves; whether her gan orders a class set"),
"ima.shir":(1,"Gift + affiliate code (potty-training story)","Her toddler's real potty-training week with the book","Conversion (urgent milestone)","Preview starts + orders on her code"),
"nataliegaash":(1,"Gift + affiliate code (big-sibling story)","Week-one prep for a new sibling, with her 3 tips","Conversion (milestone)","Preview starts + orders on her code"),
"hadas.shvat":(1,"Gift + organic mention in a 'screen-free things we do' piece","Book as a door to pretend play","Awareness (screen-free positioning)","Shares; profile visits to @lumebookai"),
"rotem__unger":(1,"Gift-only barter","Full-time-dad bedtime in nature","Awareness (dad audience)","Reach vs his 2.5K median; comments from dads"),
"daria_mansour1":(1,"Gift-only barter (2 books, twins)","Which twin recognises themselves first","Awareness + ad creative","Views vs 4.3K median; raw reveal clip for ads"),
"saba.chiche":(1,"Gift; small fee only if he asks (Yossi's approval)","Grandpa reveal to grandkids — Hanukkah gifting","Awareness → gifting conversion","Views; 'gift for grandkids' comments; Hanukkah code orders"),
"books_are_friends_slp":(1,"Gift + feature in their monthly reading pick","'This month's pick' + SLP reading tips","Consideration (book credibility)","Saves; link clicks"),
"bar.levi.adiel":(1,"Low-cost UGC package: raw footage + one post","Unboxing → first read → activity","Paid-ad creative","Usable clips; ad hook rate once run"),
"hilla_gover_slp":(2,"Gift + affiliate; she may ask for a fee","Language game on the book's pages","Consideration (authority)","Saves; code orders"),
"lital_magnezi":(2,"Paid collaboration + whitelisting (Yossi's approval); B2B gan pitch","3 ways to use it in the gan","Awareness + B2B","Views; gan B2B enquiries"),
"ganotmor":(2,"Paid UGC package: 3 hooks + usage rights (Yossi's approval)","Comedy hook → reveal","Paid-ad creative","Ad hook rate / CTR / cost per preview start"),
"almaanddad":(2,"Gift + fee if requested (Yossi's approval)","Dad reads Alma her own story; she corrects it","Awareness (dad + daughter)","Views vs his 33.5K median; cost per preview start"),
}
EDGE=[("koral_shaul_slp","קורל שאול","SLP, mom; clinics in Ness Ziona & Kiryat Ono",60600,177000,"","Strongest SLP reach found; median 177K"),
("li_noy_bar","לינוי בר","Parenting creator; 'enjoy kids away from screens'",61200,None,"","Screen-free angle, just over range"),
("noy6166","נוי יותם","Mom blogger, does UGC",90900,42800,"",""),
("maayanraichman","מעיין רייכמן","Parenting & travel journalist/creator",113000,150000,"",""),
("galtamari1","גל תמרי","Dad, parenting coach, author",94400,None,"","Rare dad-expert voice"),
("michalolivero","מיכל אוליברו","AMI Montessori guide, lecturer",99100,None,"",""),
("einatnathan","עינת נתן","Parenting author (count only; profile not deep-checked)",106000,None,"",""),
("adva_style","אדווה כלפון","Moms community founder (count only)",92000,None,"","")]
EXCL=[("No reel in 6+ months","box.from.books, sharonturgeman1, carmit_dinbar, lihen_imahut, shilat_ben_hemo, meirav_shvarzman, tom.rom_ot, study_stav, hadas_afek_, tali_moncarz, tal_psychologist, liron_shiffman, sara.danny.ot, menucha_fux"),
("Under 1,000 followers","lieli.play, gal_handly, lironam, ganenet_daniela_sagi, gan_agada1, the_olimom, _hayohaya_, savtagrafia, and others"),
("Not parenting content","batzion_assulin, racheloron, shirifadlon, carmelalerner_, amit.socher, dvorivainer, aba.itanu_anaelpashaev, hadaserez_imalevia, naamakaminer.positive.psych, drsivan_psychology, noa_kalian"),
("Teen or adult focus / outside the 2–8 range","omershnollll, liraz__madmon, alonmeir10, marsel_revivo (ages 8–14), nurse_shiran (babies born 2026)"),
("Businesses, venues or brands with low reach","vikicdesigns, etgar_haotzar, mahuti_eol, shlomitlevit, tolaat_sfarim, sifriyat.pijama, kesem.mada, firststepmethod_il"),
("Says no to collaborations","maya_navon_parenthood (bio: no collabs, no coupon codes)"),
("Sensitive","aviharush (bio links a memorial page; not appropriate for a product pitch)"),
("Arabic- or Russian-language","Removed at your request: tasharybak, slp.lanaab, raghad.speech, yasmeen_mawassi (and the Arabic over-50K edge cases)"),
("Under 5,000 followers (removed 12 Oct 2026, never contacted; the full records are in src/research/removed-2026-10-12.json)","_hadargilad_, adar_dan1, alina.barshai, anat_gavra, anna.botner.mironov, aviv_goldblatt, bat_el_shahar, beit_hayasmin, carmit_baram, dana_barsheshet, danaassory_imadana, danagu_slp, dr.rakefet, gabriela_madar, galalemida_beclass, go.parents_, hadasa_adar, hila.al.hahorut, horim.holon, inbar_gavrieli, iris_maayan, issar_bramly, its.a.twin.twin, journo_family, kidspace_byruthy, liat_noam, linoy_gelander, liron_bar_hen, liron_galili5, maayan.ab, maayanalush, magshima, malytsarfati, mamot.club, masha.ozeri, meirav_havivian, mesibalady.birthdaygirl, michal_greenwald_, michal_sat_, michal_tadmor_azran_, moments.il_, moranpasternak, netali_gan, nitzan.leon, noa.reis, nofartovly, odelia_katmor, ornit_teacher, pitputimslp, roni_babayov_dar, sensorysavta, shanny_ch_abramovich, shilat_almo, shira_kindergarten, shirankoifman, shirankrasnov, shiri_vago_katz, sterna_tm, taldinelton_oti, tinakiladze_, yael_schwartz10"),
("Other","rochma_mikmak (joke account), linoyabutbul1 IG (personal page), evaifraimov TikTok (~700 median views)")]
TRK=[("kuchale","Private account (7,138 now; tracker said 8,300)"),("happymeute","1,050 followers now; tracker said 15,700"),("doronmatalon_official, lian_kleyman, peaceloveandbeer","Handle not found"),("rivka_zerbib","South Florida realtor, not Israeli"),("avivmaman__","Business founder; last reel 2024"),("efratzoe, _lidorbar, ifathindes, ifatsochlizky","Deals, fashion-brand, wellness or PR accounts; parenting isn't the focus"),("hibasiam1","Photographer/events; not parenting"),("moranlevi22, lizamaman, menucha_fux","English bio with Hebrew content unverified, ~700 median views, or no reel since February")]
ARCH=[
["p-strong","Strongest","Speech therapists, OTs & developmental pros","28 in the database, many with reel medians above their follower count (@knafaim.ot_by_noy 10.7K followers / 14.7K median; @eden_spaiev 3.4K / 9.2K; @hadar_baier_slp 6.1K / 10K). They bring authority without Lumebook making a medical claim."],
["p-strong","Strongest","Milestone specialists: potty, sleep, new sibling","Potty-training guides (@ima.shir, @lena.gaon.parenting, @shovali, @malytsarfati) and a sibling-prep expert (@nataliegaash, 33K) map directly onto Lumebook's weaning and big-sibling stories."],
["p-strong","Strongest","Kindergarten teachers & home daycares","14 gan accounts plus 7 home daycares / gan-with-mom programmes. Reach is uneven but trust is high, and each one is also a B2B lead."],
["p-sat","Oversaturated","Parent coaches selling courses","The largest group (47). Near-identical 'no yelling / boundaries' positioning, many selling to the same parents. Pick on views and fit, not on the title."],
["p-sat","Oversaturated","Generic mom lifestyle & deals","The old tracker was mostly this. On re-check several were deals pages, fashion brands, or not Israeli at all."],
["p-under","Underused","Dads","Only 4 in range (@rotem__unger, @almaanddad, @aba.maor, @kesem_maor_livshiz), plus male educators (@hofeshligdoldrorcohen, @nakash_amir). Rare voices stand out."],
["p-under","Underused","Single, co-parent & blended families","4 found (@sharon__rosenbaum, @ayelet_divorcewithkids, @bat_el_shahar, @edenmarlel00). 'Two homes, one story' is an angle nobody else is using."],
["p-under","Underused","Family travel & outings","13 in range, several with very high reach for their size (@our_little_travelers 153K median on 17.8K; @topfamily.travel 74K on 22K). A natural home for the screen-free-on-the-go angle."],
["p-under","Unexpectedly promising","Grandparents","Still only 3 qualify. Two grandpa accounts get 80K–110K median views on 4K–17K followers. Both grandparent storytelling accounts found in the second pass were under 1K."],
["p-under","Unexpectedly promising","SLPs & educators who write children's books","@books_are_friends_slp, @reshef_michal, @michalburnham_, @bishvil.hasafa_irit.slp, @yaffa_michaela_zukerman, @daniel.gabbai. They fill the 'book people' gap that reviewers and librarians couldn't."],
["p-under","Unexpectedly promising","UGC moms & party producers","Several moms sell UGC directly (@ganotmor, @bar.levi.adiel, @valerialauren, @shaniben_shushan11, @gabriela_madar). 7 party producers can make the book a birthday moment."],
["p-weak","Weak in this search","Book reviewers, librarians, nannies, grade 1–4 teachers","Still none in range after the second pass. Book accounts were shops or inactive, and teachers mostly post for other teachers."]]
MIX=[[2,"Child-dev professionals","@knafaim.ot_by_noy · @eden_spaiev"],[2,"Kindergarten teachers","@yeladim_ktanim · @etti_haft"],[2,"Milestone specialists","@ima.shir (potty) · @nataliegaash (new sibling)"],[2,"Parents: a dad + twins","@rotem__unger · @daria_mansour1"],[1,"Screen-free / free play","@hadas.shvat"],[1,"Grandparent","@saba.chiche"],[1,"Book-writing SLPs","@books_are_friends_slp"],[1,"UGC producer (raw footage)","@bar.levi.adiel"]]
Q=["Similar-accounts graph from 76 verified creators (Instagram suggestions)","גננת","הגננת","אמא גננת","קלינאית תקשורת","מרפאה בעיסוק","מדריכת הורים","גמילה מחיתולים","יוצרת תוכן הורות","אמא לתאומים","אבא במשרה מלאה","אבא של","אבא לבנות","אבא ובת","סבתא","סבא","סבא וסבתא","משפחתון","גן פרטי","גן ילדים","חינוך ביתי","מונטסורי בבית","בלי מסכים","פעילויות לילדים","פעילויות לגן","רעיונות לגן","יצירה עם ילדים","ספרי ילדים","ספרי ילדים המלצות","סופרת ילדים","ספרנית","מעודדת קריאה","הקראת סיפורים","שעת סיפור","סיפור לפני השינה","סיפור חברתי","מורה לכיתה א","מחנכת כיתה א","מורה לאנגלית לילדים","חוג מוזיקה לפעוטות","מפעילה ימי הולדת","צלמת ילדים","אמא לשלושה","אמא לארבעה","אמא לחמישה","אמא צעירה","אמא במשרה מלאה","טיולים עם ילדים","site:instagram.com / site:tiktok.com (agents)","Hebrew listicles: mako, ynet, 9instyle, Walla (agents)"]
h=open(P('template.html')).read()
R=[('I re-checked 58 of its handles', 'I re-checked 40 of its handles'), ('<li><b>Verification.</b>', "<li><b>Second pass (same day).</b> I crawled Instagram's similar-accounts data from 76 verified Hebrew creators (about 2,000 accounts), filtered them by name and bio line, then added more seeds and keyword searches for dads, grandparents, gan and book creators. About 190 more were checked one by one, and 134 passed.</li><li><b>Rule since 12 Oct 2026: 5,000 followers or more.</b> Creators under 5,000 who had not been contacted were removed from the map (61, including 28 of the third pass). Under-5K creators who were already messaged stay, with their conversations.</li><li><b>Third pass (11 Oct 2026).</b> I took Instagram's similar-accounts lists from 117 creators already in the map, then from 74 of the new finds, and ran 48 Hebrew keyword searches: about 3,800 accounts in all. I opened the 446 most relevant ones, read followers, bio and the latest reels, and kept 100. Most of the ones I dropped were baby-sleep, birth, nutrition or shop accounts, or outside 1K to 50K followers. About 80 of the 100 are a clear fit; about 20 are borderline and say so in their risk note.</li><li><b>Hebrew only.</b> At your request, Arabic- and Russian-language creators were removed.</li>\n      <li><b>Verification.</b>"), ('<li><b>Location.</b> Three Arabic-language creators are marked “Israel residence unverified”. Confirm before outreach.</li>', "<li><b>Scoring method differs by pass.</b> The 70 first-pass creators and 3 second-pass creators were rated by hand. The other 131 second-pass creators and all 100 third-pass creators get stricter rule-based ratings from archetype, views-to-followers ratio, reel recency and size. Use the per-creator notes rather than small score gaps.</li><li><b>Language</b> is inferred from Hebrew names and bios; I didn't listen to audio. A few creators write bios in English.</li>")]
for a,b in R:
    assert a in h, a[:60]; h=h.replace(a,b)
J=lambda x: json.dumps(x,ensure_ascii=False)
for k,v in {"__DATA__":C,"__OUT__":O,"__EDGE__":EDGE,"__EXCL__":EXCL,"__TRK__":TRK,"__ARCH__":ARCH,"__MIX__":MIX,"__Q__":Q,"__OFFER__":OFFER}.items(): h=h.replace(k,J(v))
for k,v in {"<!--LB:HEAD-->":design.head(),"<!--LB:THEME-TOGGLE-->":"","__LB_LOGO__":design.logo_data_uri()}.items():
    assert h.count(k)==1, k; h=h.replace(k,v)
# NO_EM: the user never wants em dashes
h=h.replace(' \u2014 ',', ').replace('"\u2014"','"n/a"').replace("'\u2014'","'n/a'").replace('\u2014','-').replace(' \u2013 ',', ').replace('\u2013','-')
OUT=os.path.dirname(HERE)
open(OUT+'/lumebook-creator-map.html','w').write(h)
# CSV is maintained separately (contacts + outreach messages); do not rewrite it here
print('ok',len(C),len(h))
