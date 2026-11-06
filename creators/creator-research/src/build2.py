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
# experts badge (06 Nov 2026): c['xp'] = the professional fields of a creator (src/experts.py patterns over the bio line, hand list in experts.json)
import experts
experts.tag(C)
KIDS=json.load(open(P('kids.json')))
# offer facts come from shared/facts.json, so the map's messages and checks use the same numbers as every other component
FACTS=json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))),"shared","facts.json"),encoding="utf-8"))
OF=FACTS["offer"]
OFFER={"pct":OF["allocation_pct"],"ex":[OF["split_example"]["creator_earnings_pct"],OF["split_example"]["audience_discount_pct"]]}
assert sum(OFFER["ex"])==OFFER["pct"], "the split example must add up to the allocation"
for c in C:
    if c['h'] in KIDS: c['kids']=KIDS[c['h']]
# weekly refresh (refresh/refresh.py): fresh followers, median views and last reel over the research numbers, plus its flags
RF=json.load(open(P('refresh/latest.json'))) if os.path.exists(P('refresh/latest.json')) else {'date':None,'data':{}}
for c in C: c['f0'],c['med0']=c.get('f'),c.get('med')   # the research numbers, so the card can show the change since
for c in C:
    x=RF['data'].get(c['h'])
    if not x: continue
    for k in ('f','med','last'):
        if x.get(k) is not None: c[k]=x[k]
    if x.get('rf'): c['rf']=x['rf']
    c['rfd']=RF['date']
# engagement and buying talk on each creator's 12 most recent posts, measured 14 Oct 2026 for 134 creators
# (research/creator-content-conversion/round2/creators_kpi.csv; buying signals = comments asking where to buy or the price, wanting it, or saying they bought it)
KPI=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))),'research','creator-content-conversion','round2','creators_kpi.csv')
if os.path.exists(KPI):
    byh={c['h']:c for c in C}
    fl=lambda v: round(float(v),2) if v not in ('',None) else None
    for r in csv.DictReader(open(KPI,encoding='utf-8')):
        c=byh.get(r['creator'])
        if c: c['kpi']={'cpk':fl(r['median_comments_per_1k_plays']),'lpk':fl(r['median_likes_per_1k_plays']),'bs':fl(r['purchase_signals_per_100']),'n':int(r['posts']),'cm':int(r['comments_sampled']),'d':'2026-10-14','bn':int(r['posts']),'bd':'2026-10-14'}
# the Saturday refresh (refresh/refresh.py) measures them again for every creator: a fresh number replaces the 14 Oct one.
# lpk and cpk come with n reels and date d; bs with cm audience comments on bn reels, date bd
for c in C:
    k=(RF['data'].get(c['h']) or {}).get('kpi')
    if not k: continue
    q=c.setdefault('kpi',{})
    if k.get('lpk') is not None or k.get('cpk') is not None:
        for f in ('lpk','cpk'):
            if k.get(f) is not None: q[f]=k[f]
        q['n'],q['d']=k['n'],k['d']
    if k.get('bs') is not None: q.update(bs=k['bs'],cm=k['cm'],bn=k['bn'],bd=k['bd'])
import re
for i,c in enumerate(C):
    m=re.match(r'pass(\d+)',str(c.get('extra',''))); n=int(m.group(1)) if m else 1
    c['ai']=i; c['batch']=n; c['added']={5:'2026-10-20',4:'2026-10-18',3:'2026-10-11'}.get(n,'2026-10-03')
# a creator added by hand on a later day than the rest of the pass keeps its own date in C_all.json ("added_on": "YYYY-MM-DD");
# the weekly passes (6 and later, research/merge_pass.py) always write it. The page shows it as dd / mm / yyyy (isoDL, dL),
# so there is no long Hebrew date field any more (the old "chk", 5 Nov 2026)
for c in C:
    if c.get('added_on'): c['added']=c['added_on']
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
EDGE=[("koral_shaul_slp","קורל שאול","קלינאית תקשורת ואמא; קליניקות בנס ציונה ובקריית אונו",60600,177000,"","הקלינאית עם החשיפה הגבוהה ביותר שמצאנו; חציון 177K"),
("li_noy_bar","לינוי בר","יוצרת תוכן הורות; ״ליהנות מהילדים בלי מסכים״",61200,None,"","זווית של בלי מסכים, קצת מעל הטווח"),
("noy6166","נוי יותם","בלוגרית אמהות, עושה UGC",90900,42800,"",""),
("maayanraichman","מעיין רייכמן","עיתונאית ויוצרת תוכן על הורות וטיולים",113000,150000,"",""),
("galtamari1","גל תמרי","אבא, מאמן הורים, סופר",94400,None,"","קול נדיר של אבא מומחה"),
("michalolivero","מיכל אוליברו","מדריכת מונטסורי AMI, מרצה",99100,None,"",""),
("einatnathan","עינת נתן","סופרת בתחום ההורות (רק מספר העוקבים; הפרופיל לא נבדק לעומק)",106000,None,"",""),
("adva_style","אדווה כלפון","מייסדת קהילת אמהות (רק מספר העוקבים)",92000,None,"","")]
EXCL=[("אין רילס 6 חודשים ומעלה","box.from.books, sharonturgeman1, carmit_dinbar, lihen_imahut, shilat_ben_hemo, meirav_shvarzman, tom.rom_ot, study_stav, hadas_afek_, tali_moncarz, tal_psychologist, liron_shiffman, sara.danny.ot, menucha_fux"),
("פחות מ-1,000 עוקבים","lieli.play, gal_handly, lironam, ganenet_daniela_sagi, gan_agada1, the_olimom, _hayohaya_, savtagrafia ועוד"),
("לא תוכן הורות","batzion_assulin, racheloron, shirifadlon, carmelalerner_, amit.socher, dvorivainer, aba.itanu_anaelpashaev, hadaserez_imalevia, naamakaminer.positive.psych, drsivan_psychology, noa_kalian"),
("מתמקדים בבני נוער או במבוגרים, מחוץ לטווח 2 עד 8","omershnollll, liraz__madmon, alonmeir10, marsel_revivo (גילי 8 עד 14), nurse_shiran (תינוקות שנולדו ב-2026)"),
("עסקים, מקומות או מותגים עם חשיפה נמוכה","vikicdesigns, etgar_haotzar, mahuti_eol, shlomitlevit, tolaat_sfarim, sifriyat.pijama, kesem.mada, firststepmethod_il"),
("הסבב הרביעי, 18 באוקטובר 2026: אין רילס מאז לפני יולי","lihen_imahut, hilaraanan_, dr_tal_babystepspsychology, montessori.il, hila_efratii, ellayohanan, ofer.medem.friedman, soul.soulandpaper, alhaveda, orin_zherebitsky, shirvahaba"),
("הסבב הרביעי: חשבון ששינה שם וכבר במפה","by_shanina הוא שם שהיה ל-shanina_advent.learn; מ-24 באוקטובר 2026 היא במפה בשם החדש art_by_shanina"),
("לא עושים שיתופי פעולה","maya_navon_parenthood (בביו: בלי שיתופי פעולה ובלי קופונים)"),
("רגיש","aviharush (הביו מקשר לדף הנצחה; לא מתאים להצעת מוצר)"),
("בערבית או ברוסית","הוסרו לבקשתך: tasharybak, slp.lanaab, raghad.speech, yasmeen_mawassi (וגם מקרי הקצה בערבית מעל 50K)"),
("פחות מ-5,000 עוקבים (הוסרו ב-12 באוקטובר 2026 ולא פנינו אליהם; הרשומות המלאות ב-src/research/removed-2026-10-12.json)","_hadargilad_, adar_dan1, alina.barshai, anat_gavra, anna.botner.mironov, aviv_goldblatt, bat_el_shahar, beit_hayasmin, carmit_baram, dana_barsheshet, danaassory_imadana, danagu_slp, dr.rakefet, gabriela_madar, galalemida_beclass, go.parents_, hadasa_adar, hila.al.hahorut, horim.holon, inbar_gavrieli, iris_maayan, issar_bramly, its.a.twin.twin, journo_family, kidspace_byruthy, liat_noam, linoy_gelander, liron_bar_hen, liron_galili5, maayan.ab, maayanalush, magshima, malytsarfati, mamot.club, masha.ozeri, meirav_havivian, mesibalady.birthdaygirl, michal_greenwald_, michal_sat_, michal_tadmor_azran_, moments.il_, moranpasternak, netali_gan, nitzan.leon, noa.reis, nofartovly, odelia_katmor, ornit_teacher, pitputimslp, roni_babayov_dar, sensorysavta, shanny_ch_abramovich, shilat_almo, shira_kindergarten, shirankoifman, shirankrasnov, shiri_vago_katz, sterna_tm, taldinelton_oti, tinakiladze_, yael_schwartz10"),
("אחר","rochma_mikmak (חשבון בדיחה), linoyabutbul1 IG (עמוד אישי), evaifraimov TikTok (חציון של כ-700 צפיות)")]
TRK=[("kuchale","חשבון פרטי (7,138 עכשיו; בטבלה היה 8,300)"),("happymeute","1,050 עוקבים עכשיו; בטבלה היה 15,700"),("doronmatalon_official, lian_kleyman, peaceloveandbeer","שם המשתמש לא נמצא"),("rivka_zerbib","מתווכת נדל״ן בדרום פלורידה, לא ישראלית"),("avivmaman__","מייסד עסק; הרילס האחרון ב-2024"),("efratzoe, _lidorbar, ifathindes, ifatsochlizky","חשבונות של דילים, מותגי אופנה, וולנס או יחסי ציבור; הורות היא לא העיקר"),("hibasiam1","צילום ואירועים; לא הורות"),("moranlevi22, lizamaman, menucha_fux","ביו באנגלית עם תוכן בעברית שלא אומת, חציון של כ-700 צפיות, או אין רילס מאז פברואר")]
ARCH=[
["p-strong","הכי חזקים","קלינאיות תקשורת, מרפאות בעיסוק ואנשי מקצוע בהתפתחות","28 במאגר, ולרבים מהם חציון צפיות גבוה ממספר העוקבים (@knafaim.ot_by_noy: 10.7K עוקבים / חציון 14.7K; @eden_spaiev: 3.4K / 9.2K; @hadar_baier_slp: 6.1K / 10K). הם מביאים סמכות בלי ש-LumeBook טוענת טענה רפואית."],
["p-strong","הכי חזקים","מומחי אבני דרך: גמילה, שינה, אח חדש","מדריכות גמילה (@ima.shir, @lena.gaon.parenting, @shovali, @malytsarfati) ומומחית להכנה לאח חדש (@nataliegaash, 33K) מתחברות ישר לסיפורי הגמילה והאח הגדול של LumeBook."],
["p-strong","הכי חזקים","גננות ומשפחתונים","14 חשבונות של גנים ועוד 7 משפחתונים או תוכניות של גן עם אמא. החשיפה לא אחידה אבל האמון גבוה, וכל אחד מהם הוא גם ליד ל-B2B."],
["p-sat","רווי","מדריכות הורים שמוכרות קורסים","הקבוצה הגדולה ביותר (47). מיצוב כמעט זהה של ״בלי צעקות / גבולות״, ורבות מוכרות לאותם הורים. בוחרים לפי צפיות והתאמה, לא לפי התואר."],
["p-sat","רווי","לייפסטייל אמהות כללי ודילים","הטבלה הישנה הייתה בעיקר זה. בבדיקה חוזרת כמה מהם היו עמודי דילים, מותגי אופנה או בכלל לא ישראלים."],
["p-under","לא מנוצל","אבות","רק 4 בטווח (@rotem__unger, @almaanddad, @aba.maor, @kesem_maor_livshiz), ועוד אנשי חינוך גברים (@hofeshligdoldrorcohen, @nakash_amir). קולות נדירים בולטים."],
["p-under","לא מנוצל","הורים יחידניים, הורות משותפת ומשפחות מעורבות","נמצאו 4 (@sharon__rosenbaum, @ayelet_divorcewithkids, @bat_el_shahar, @edenmarlel00). ״שני בתים, סיפור אחד״ היא זווית שאף אחד אחר לא משתמש בה."],
["p-under","לא מנוצל","טיולים ובילויים עם המשפחה","13 בטווח, כמה מהם עם חשיפה גבוהה מאוד ביחס לגודל (@our_little_travelers: חציון 153K על 17.8K; @topfamily.travel: 74K על 22K). בית טבעי לזווית של בלי מסכים בדרכים."],
["p-under","מבטיח באופן מפתיע","סבים וסבתות","עדיין רק 3 עומדים בתנאים. שני חשבונות של סבים מקבלים חציון של 80K עד 110K צפיות על 4K עד 17K עוקבים. שני חשבונות הסיפורים של סבים וסבתות שנמצאו בסבב השני היו מתחת ל-1K."],
["p-under","מבטיח באופן מפתיע","קלינאיות ואנשי חינוך שכותבים ספרי ילדים","@books_are_friends_slp, @reshef_michal, @michalburnham_, @bishvil.hasafa_irit.slp, @yaffa_michaela_zukerman, @daniel.gabbai. הם ממלאים את החור של ״אנשי ספרים״ שמבקרים וספרניות לא מילאו."],
["p-under","מבטיח באופן מפתיע","אמהות UGC ומפיקות ימי הולדת","כמה אמהות מוכרות UGC ישירות (@ganotmor, @bar.levi.adiel, @valerialauren, @shaniben_shushan11, @gabriela_madar). 7 מפיקות ימי הולדת יכולות להפוך את הספר לרגע של יום הולדת."],
["p-weak","חלש בחיפוש הזה","מבקרי ספרים, ספרניות, מטפלות, מורות לכיתות א׳ עד ד׳","עדיין אף אחד בטווח אחרי הסבב השני. חשבונות הספרים היו חנויות או לא פעילים, והמורות מפרסמות בעיקר למורות אחרות."]]
MIX=[[2,"Child-dev professionals","@knafaim.ot_by_noy · @eden_spaiev"],[2,"Kindergarten teachers","@yeladim_ktanim · @etti_haft"],[2,"Milestone specialists","@ima.shir (potty) · @nataliegaash (new sibling)"],[2,"Parents: a dad + twins","@rotem__unger · @daria_mansour1"],[1,"Screen-free / free play","@hadas.shvat"],[1,"Grandparent","@saba.chiche"],[1,"Book-writing SLPs","@books_are_friends_slp"],[1,"UGC producer (raw footage)","@bar.levi.adiel"]]
Q=["Similar-accounts graph from 76 verified creators (Instagram suggestions)","גננת","הגננת","אמא גננת","קלינאית תקשורת","מרפאה בעיסוק","מדריכת הורים","גמילה מחיתולים","יוצרת תוכן הורות","אמא לתאומים","אבא במשרה מלאה","אבא של","אבא לבנות","אבא ובת","סבתא","סבא","סבא וסבתא","משפחתון","גן פרטי","גן ילדים","חינוך ביתי","מונטסורי בבית","בלי מסכים","פעילויות לילדים","פעילויות לגן","רעיונות לגן","יצירה עם ילדים","ספרי ילדים","ספרי ילדים המלצות","סופרת ילדים","ספרנית","מעודדת קריאה","הקראת סיפורים","שעת סיפור","סיפור לפני השינה","סיפור חברתי","מורה לכיתה א","מחנכת כיתה א","מורה לאנגלית לילדים","חוג מוזיקה לפעוטות","מפעילה ימי הולדת","צלמת ילדים","אמא לשלושה","אמא לארבעה","אמא לחמישה","אמא צעירה","אמא במשרה מלאה","טיולים עם ילדים","site:instagram.com / site:tiktok.com (agents)","Hebrew listicles: mako, ynet, 9instyle, Walla (agents)"]
h=open(P('template.html')).read()
J=lambda x: json.dumps(x,ensure_ascii=False)
# icons come from the LumeBook icon set (shared/design/icons.json, 24 grid): __ICON:name__ in the static HTML becomes
# design.icon(name), and the script gets the whole set as LBI; every name the page maps to (ICN) must be in the set
LBI={**design.icons(),**design.ui_icons()}
icn=json.loads(re.search(r'const ICN=(\{.*?\});',h).group(1))
gone=sorted(set(icn.values())-set(LBI)); assert not gone, "not in shared/design/icons.json: "+", ".join(gone)
h=re.sub(r'__ICON:([\w-]+)__',lambda m: design.icon(m.group(1),"i"),h)
assert h.count("__LB_ICONS__")==1; h=h.replace("__LB_ICONS__",J(LBI))
# what happened to the creators Yarin added with the map's "הוספת יוצרים" button (weekly.py requests writes it on Saturdays)
RQ=P('research/weekly/requests.json'); ADDQ=json.load(open(RQ,encoding='utf-8')) if os.path.exists(RQ) else {}
for k,v in {"__XP__":experts.kinds_for_page(),"__DATA__":C,"__OUT__":O,"__EDGE__":EDGE,"__EXCL__":EXCL,"__TRK__":TRK,"__ARCH__":ARCH,"__MIX__":MIX,"__Q__":Q,"__OFFER__":OFFER,"__ADDQ__":ADDQ,"__ADM__":FACTS["creators"]["admission"],
          # the books tab's hues (shared/design/categories.json set books-metrics), used as lb-cat-N
          "__BKCAT__":{k:v["cat"] for k,v in design.categories("books-metrics").items()}}.items(): h=h.replace(k,J(v))
for k,v in {"<!--LB:HEAD-->":design.head(),"__LB_LOGO__":design.logo_data_uri()}.items():
    assert h.count(k)==1, k; h=h.replace(k,v)
# NO_EM: the user never wants em dashes
h=h.replace(' \u2014 ',', ').replace('"\u2014"','"n/a"').replace("'\u2014'","'n/a'").replace('\u2014','-').replace(' \u2013 ',', ').replace('\u2013','-')
# dates as dd / mm / yyyy everywhere (Yarin, 30 Oct 2026), also the long Hebrew dates inside the data (refresh flags, research notes);
# kept left to right inside Hebrew with LRI/PDI. A date without a year is 2026, the year all the research ran.
HEM=['\u05d9\u05e0\u05d5\u05d0\u05e8','\u05e4\u05d1\u05e8\u05d5\u05d0\u05e8','\u05de\u05e8\u05e5','\u05d0\u05e4\u05e8\u05d9\u05dc','\u05de\u05d0\u05d9','\u05d9\u05d5\u05e0\u05d9','\u05d9\u05d5\u05dc\u05d9','\u05d0\u05d5\u05d2\u05d5\u05e1\u05d8','\u05e1\u05e4\u05d8\u05de\u05d1\u05e8','\u05d0\u05d5\u05e7\u05d8\u05d5\u05d1\u05e8','\u05e0\u05d5\u05d1\u05de\u05d1\u05e8','\u05d3\u05e6\u05de\u05d1\u05e8']
h=re.sub(r'(\d{1,2}) \u05d1('+'|'.join(HEM)+r')(?: (\d{4}))?',lambda m:'\u2066%02d / %02d / %s\u2069'%(int(m.group(1)),HEM.index(m.group(2))+1,m.group(3) or '2026'),h)
OUT=os.path.dirname(HERE)
open(OUT+'/lumebook-creator-map.html','w').write(h)
# CSV is maintained separately (contacts + outreach messages); do not rewrite it here
print('ok',len(C),len(h))
# the kids are named once per message, in Hebrew letters (src/test_kids_names.mjs); skipped when node is not installed
import shutil, subprocess
if shutil.which('node'):
    r=subprocess.run(['node',P('test_kids_names.mjs')],capture_output=True,text=True)
    print((r.stdout.strip().splitlines() or ['no output'])[-1])
    if r.returncode: print(r.stdout+r.stderr); sys.exit(1)
