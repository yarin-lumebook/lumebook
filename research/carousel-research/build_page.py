import html, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # project root (research/<this folder>)
sys.path.insert(0, os.path.join(ROOT, "shared", "design"))
import design  # LumeBook design system: tokens, components, theme toggle, logo
IL_FUN=[
("hodayaohayon","DUKhAwjjD-T",5,2425,14.6,7100,51,"2026-01-31","Less sugar at home, fridge recipe sheet","אני"),
("hadas.shvat","DbOS3GDCHNi",13,1538,8.1,2361,23,"2026-07-25","Dopamine and boredom, book recommendation","comment for a summer booklet"),
("saraigatt","DbFa3eJja3l",12,294,1.3,2114,7,"2026-07-22","Mindfulness games list","תרגול"),
("avital.bashan","DboKFT-DWcc",10,1751,21.1,1771,68,"2026-08-04","Instead of X say Y, illustrated","כלים"),
("hodayaohayon","DR6TuX8jCjY",7,1929,11.6,1659,44,"2025-12-06","Grandma's winter remedies sheet","תרופות סבתא"),
("avital.bashan","Dd67eRzjXYN",10,1458,17.6,1653,116,"2026-09-30","Talking with kids about hard topics","קשר"),
("tal_strul","DZphMo0CAUb",8,613,13.0,1389,27,"2026-06-16","5 books for starting municipal gan","ספר + coupon"),
("saraigatt","DcIYOqZjZoQ",10,315,1.4,1388,4,"2026-08-17","Sibling jealousy, a story","❤️"),
("saraigatt","DciF8FvjTS0",12,452,2.0,1386,5,"2026-08-27","Building a bond, list","קשר"),
("dvir_atzmon_shatil","DdwmmkEirdA",16,1923,41.8,1358,54,"2026-09-26","Positive language challenge","אתגר"),
("hodayaohayon","DRoM-T4CPSj",8,1430,8.6,1239,29,"2025-11-29","Stop saying 'well done'","אני"),
("saraigatt","DcWR6wFDfHA",10,237,1.0,1179,3,"2026-08-22","End-of-summer ideas file","קיץ"),
("larissaginatmethod","DcOFta8DL1W",12,301,1.7,1169,5,"2026-08-19","Potty training in 5 steps","חיתול"),
("hodayaohayon","DbfEOAoCE_V",4,69,0.4,1167,2,"2026-08-01","Potty training phrases sheet","אני"),
("larissaginatmethod","Dd0zNyHjiIb",9,229,1.3,1155,10,"2026-09-28","Potty training, second run","חיתול"),
("yaffa_michaela_zukerman","DdoeylHDeQQ",20,2033,8.5,1149,28,"2026-09-23","Digital child-safety book launch","מוגנות (purchase)"),
]
IL_REACH=[
("raising_creative_kids","DdzLT8mnJXg",11,14074,122.4,409,565,"2026-09-27","One life through the ages, on failure"),
("adar.motherhood","DdYgdi7DMuK",7,7015,113.1,116,164,"2026-09-17","Watching my partner be a dad"),
("danit_parenting_coaching","Das4fCQDTBf",15,23367,92.4,814,353,"2026-07-12","Holding a curfew boundary (sells a guide)"),
("adar_dan1","DSIhVdCjC6f",7,1381,92.1,124,59,"2025-12-11","Child refuses to say hello or hug"),
("dvir_atzmon_shatil","DbtSApoCrPJ",16,3831,83.3,175,130,"2026-08-06","Owning mistakes and saying sorry"),
("edenmomlife","DXCJLUSjDbS",9,2589,58.8,162,111,"2026-04-12","What he will remember from childhood"),
("edenmomlife","DUUo7XfjEXM",8,2249,51.1,138,74,"2026-02-04","Overwhelm and anger with a toddler"),
("valerialauren","DVk06eOjMFp",10,4385,42.2,148,84,"2026-03-07","Don't over-entertain a happy child"),
("avital.bashan","DbWKJfvDSN5",10,3381,40.7,326,114,"2026-07-28","Ranking childhood moments"),
("natashagolan_","Dd1JpBCDLQe",11,1948,30.4,217,62,"2026-09-28","Letter before a second birth"),
("galtamari1","DRFcW60lwfo",11,32840,20.7,897,964,"2025-11-15","Friendships as leaves, branches, roots"),
("mama.on.point","DTfo7UpiAMf",15,7492,16.4,130,134,"2026-01-14","What kids learn when we lose it"),
]
GL_FUN=[
("teransands","Dd_qyGlFhfC",11,25975,14.3,47769,262,"2026-10-02","Mental load at home, family challenge","RESET"),
("composerstudyclub","DW4k5VoDFSt",7,33903,24.6,26813,1056,"2026-04-08","Kindergarten readiness through music","MUSIC"),
("letimomlife_","Da3tFf5ErDB",20,17037,6.3,24158,221,"2026-07-16","Toddler gift picks, links","play"),
("toddlerdietitiantiff","DcOLCWODnF6",19,9888,13.5,22969,63,"2026-08-19","Snack prep recipes and product links","PREP"),
("therapyformums","DZXJmKnCZ0Q",16,6886,27.8,16571,77,"2026-06-09","Mental load, how I changed it","LOAD"),
("yummytoddlerfood","DcqsJPwEX-B",7,10059,1.7,15737,39,"2026-08-30","Easy fall breakfasts","LINKS"),
("biglittlefeelings","DdSEMiKEpAE",6,15104,4.1,14624,248,"2026-09-14","Mental load in 5 layers","SUB"),
("letimomlife_","DcHk2C5j_Rd",20,4063,1.5,13924,50,"2026-08-16","Toddler favorites, links","shop"),
("yummytoddlerfood","DdHBm-VkcFn",8,7248,1.2,13206,34,"2026-09-10","Iron-rich snacks","LINKS"),
("katy_g_blog","DU3xc7cDV4M",12,64243,210.6,12963,5666,"2026-02-17","Gen Alpha and overstimulation","START"),
("feedinglittles","DbQmeoom8_L",14,5868,2.2,12449,33,"2026-07-26","Lunch boxes, links and codes","LUNCH"),
("thekinected_ot","Dc36QaeEclb",8,2517,0.9,11476,46,"2026-09-04","Developmental movement routine","MOVE"),
]
GL_REACH=[
("therapyformums","DReSKEGCZEW",19,136101,548.8,9335,2370,"2025-11-25","Dear partner: the mental load"),
("mommyandmishti","DZDgG2ogewZ",17,45575,495.4,692,2330,"2026-06-01","Stop saying 'I love you', say this"),
("wearemorethanmoms","DX7tn0VEs63",8,214293,412.9,2043,8369,"2026-05-04","Asked dads what moms stopped doing"),
("parentfocus","DR8KFbnkY1C",13,19900,361.8,1117,493,"2025-12-06","Tantrums: you don't have to fix feelings"),
("sleepwiseconsulting","DTQt5GSAbcK",5,7396,336.2,6717,171,"2026-01-08","Milk out of bedtime by 12 months"),
("mommyandmishti","DX1pEiSEstN",17,29410,319.7,262,1034,"2026-05-01","Why 'shy' is a harmful label"),
("smallstepsparenting","DM8ppTPoAod",7,11551,235.7,236,194,"2025-08-04","How to say sorry to a child"),
("katy_g_blog","DU3xc7cDV4M",12,64243,210.6,12963,5666,"2026-02-17","Gen Alpha and overstimulation"),
("thriveafterbabywithalex","DcBqyIxG_1f",12,20750,175.8,302,1138,"2026-08-14","Postpartum is not just hormones"),
("chroniclekidsbooks","DZvB-A4lMfK",3,15400,167.4,169,329,"2026-06-18","Elmo picture book announcement"),
("thriveafterbabywithalex","Ddg5kxcGyjv",10,14345,121.6,567,1204,"2026-09-20","Missing your older child after a new baby"),
("mother.ly","DdCUJjHmPZ-",2,13892,50.0,45,637,"2026-09-08","New picture book promo"),
]
def n(x): return f"{x:,}"
def link(c): return f'<a href="https://www.instagram.com/p/{c}/">{c}</a>'
def ask(a):
    if any('֐'<=ch<='׿' for ch in a): return f'<span class="he" dir="rtl">{html.escape(a)}</span>'
    return html.escape(a)
def fun_table(title,rows):
    h=f'<h3>{title}</h3><div class="lb-table-wrap"><table class="lb-table mid top"><thead><tr><th class="num">#</th><th>Account</th><th>Post</th><th>Topic</th><th>Comment word</th><th class="num">Comments</th><th class="num">Likes</th><th class="num">Likes vs median</th><th class="num">Slides</th><th class="num">Date</th></tr></thead><tbody>'
    for i,r in enumerate(rows,1):
        u,c,s,l,x,cm,rp,d,t,a=r
        h+=f'<tr><td class="num">{i}</td><td>{u}</td><td>{link(c)}</td><td class="cap">{html.escape(t)}</td><td>{ask(a)}</td><td class="num"><b>{n(cm)}</b></td><td class="num">{n(l)}</td><td class="num">{x}x</td><td class="num">{s}</td><td class="num">{d}</td></tr>'
    return h+'</tbody></table></div>'
def reach_table(title,rows):
    h=f'<h3>{title}</h3><div class="lb-table-wrap"><table class="lb-table mid top"><thead><tr><th class="num">#</th><th>Account</th><th>Post</th><th>Topic</th><th class="num">Likes</th><th class="num">Likes vs median</th><th class="num">Reposts</th><th class="num">Comments</th><th class="num">Slides</th><th class="num">Date</th></tr></thead><tbody>'
    for i,r in enumerate(rows,1):
        u,c,s,l,x,cm,rp,d,t=r
        h+=f'<tr><td class="num">{i}</td><td>{u}</td><td>{link(c)}</td><td class="cap">{html.escape(t)}</td><td class="num">{n(l)}</td><td class="num"><b>{x}x</b></td><td class="num">{n(rp)}</td><td class="num">{n(cm)}</td><td class="num">{s}</td><td class="num">{d}</td></tr>'
    return h+'</tbody></table></div>'
tables=('<p>Comment tables list the most-commented carousels whose caption or last slide asks for a comment word; giveaways are left out. Reach tables need at least 1,000 likes (Israel) or 3,000 (global) and are sorted by likes against the account\'s median.</p>'
 +fun_table('Israel: most comments on a comment-word carousel',IL_FUN)
 +reach_table('Israel: biggest reach against the account median',IL_REACH)
 +fun_table('Global: most comments on a comment-word carousel',GL_FUN)
 +reach_table('Global: biggest reach against the account median',GL_REACH))
GL_EXTRA='''
  <article class="card lb-card is-flush lb-media">
    <div class="lb-scroller"><img src="img2/Da3tFf5ErDB.jpg" alt="Toddler gift picks: a birthday photo cover, a toy garage, a balance bike, outdoor activities"></div>
    <div class="lb-media-body">
      <div class="head"><h3>6. letimomlife_: toddler gift picks</h3><div class="pills lb-row"><span class="lb-chip">20 slides</span><span class="lb-chip">17,037 likes · 6.3x</span><span class="lb-chip accent">24,158 comments</span><span class="lb-chip success">product links</span></div></div>
      <p><strong>Structure:</strong> "Toddler gifts I'd choose all over again", then one product per slide in real use at home, each with a one-line reason.</p>
      <p><strong>How it sells:</strong> follow and comment "play" for the links by DM. She repeats the format every few weeks with the word "shop" (13,924 comments on one run).</p>
      <span class="src lb-note"><a href="https://www.instagram.com/p/Da3tFf5ErDB/">instagram.com/p/Da3tFf5ErDB</a> · 16 Jul 2026</span>
    </div>
  </article>

  <article class="card lb-card is-flush lb-media">
    <div class="lb-scroller"><img src="img2/Ddg5kxcGyjv.jpg" alt="A photo of an older child with a new baby, with English text about missing the older child"></div>
    <div class="lb-media-body">
      <div class="head"><h3>7. thriveafterbabywithalex: missing your older child</h3><div class="pills lb-row"><span class="lb-chip">10 slides</span><span class="lb-chip accent">14,345 likes · 122x</span><span class="lb-chip">567 comments</span><span class="lb-chip accent">1,204 reposts</span></div></div>
      <p><strong>Structure:</strong> one photo of the older child with the baby, and the text "No one warned me I might miss my older child after having another baby", then the small moments and the guilt, then a question to the reader.</p>
      <p><strong>Why it matters:</strong> the new-sibling milestone again, this time as the top global sibling carousel. Same emotional angle as natashagolan_ in Israel, with twice the share rate.</p>
      <span class="src lb-note"><a href="https://www.instagram.com/p/Ddg5kxcGyjv/">instagram.com/p/Ddg5kxcGyjv</a> · 20 Sep 2026</span>
    </div>
  </article>

  <article class="card lb-card is-flush lb-media">
    <div class="lb-scroller"><img src="img2/DZvB-A4lMfK.jpg" alt="Three red slides: Elmo asked, thousands responded, now there is a book"></div>
    <div class="lb-media-body">
      <div class="head"><h3>8. Chronicle Books kids: a three-slide book launch</h3><div class="pills lb-row"><span class="lb-chip">3 slides</span><span class="lb-chip accent">15,400 likes · 167x</span><span class="lb-chip">169 comments</span><span class="lb-chip">329 reposts</span></div></div>
      <p><strong>Structure:</strong> "Elmo asked" (a screenshot of the original post), "Thousands of you responded, and Elmo listened", "Now there is a book. Out October 27th".</p>
      <p><strong>Why it matters:</strong> the best publisher book carousel in the pool, and it is three slides of story about where the book came from. The caption sends readers to pre-order.</p>
      <span class="src lb-note"><a href="https://www.instagram.com/p/DZvB-A4lMfK/">instagram.com/p/DZvB-A4lMfK</a> · 18 Jun 2026</span>
    </div>
  </article>'''
s=open(os.path.join(HERE,'page_template.html'),encoding='utf-8').read()
s=s.replace('__IL_ACC__','460').replace('__GL_ACC__','292').replace('__IL_CAR__','3,980').replace('__GL_CAR__','3,643').replace('__IL_WIN__','149 of 259')
old='<div class="finding lb-card"><b>The selling mechanism is the comment-word DM</b><p>__IL_FUN__ Israeli carousels end with "comment X and I\'ll send it". Those posts pull comments at many times the account\'s normal rate: up to 295x on a small account. Globally the same move reaches 16,571 comments on one post.</p></div>'
new='<div class="finding lb-card"><b>The selling mechanism is the comment-word DM</b><p>At least 255 of the Israeli carousels (6%) end with "comment X and I\'ll send it", against at least 584 of the global ones (16%). Those posts pull comments at many times the account\'s normal rate, up to 295x on a small Israeli account and 47,769 comments on one global post.</p></div>'
assert old in s; s=s.replace(old,new)
s=s.replace('__GL_EXTRA__',GL_EXTRA).replace('__TABLES__',tables)
s=(s.replace('<!--LB:HEAD-->',design.head())
   .replace('LB_LOGO_URI',design.logo_data_uri()))
assert '<!--LB:' not in s and 'LB_LOGO_URI' not in s
assert '__' not in s.replace('__dj',''), [x for x in s.split() if '__' in x][:5]
open(os.path.join(HERE,'lumebook-carousel-research.html'),'w',encoding='utf-8').write(s); print(len(s))
