"""Any later pass (the weekly Saturday search since 24 Oct 2026): add the creators in data<N>.py to C_all.json, with the
stats read into pass<N>_raw.json.

Run from src/research:  python3 merge_pass.py <N> [--date YYYY-MM-DD] [--reviewed <review.json>]
Same rules as merge4.py, written for the Hebrew rows (role, ages "2 עד 8", risk) that data files hold since 20 Oct 2026.
It only appends. Existing creators are never changed, and running it twice adds nothing. A creator already in the map
under another handle (same Instagram pk), or one that fails the admission bar of 24 Oct 2026 (weekly/gate.py, from
shared/facts.json creators.admission: followers, median views, views per follower, likes and comments per 1,000 views,
read from its pass<N>_raw.json row), is skipped and listed.
Each new row keeps its Instagram pk and its date ("added_on"), so build2.py shows it as batch <N> of that day.
--reviewed: the review.json lists of that run (weekly/README.md); every handle in them goes into weekly/reviewed.json,
so the next weekly runs do not review the same accounts again for 90 days.
"""
import json, re, os, sys, csv, datetime
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'weekly'))
import gate  # noqa: E402
P = lambda f: os.path.join(HERE, f)
SRC = os.path.dirname(HERE)
args = sys.argv[1:]
if not args or not args[0].isdigit(): sys.exit(__doc__)
N = int(args[0])
opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
DAY = opt('--date', datetime.date.today().isoformat())
D = datetime.date.fromisoformat(DAY)
ns = {}; exec(open(P('data%d.py' % N), encoding='utf-8').read(), ns)
ROWS, KIDS = ns['N%d' % N], ns.get('KIDS%d' % N, {})
RAW = {x['h']: x for x in json.load(open(P('pass%d_raw.json' % N), encoding='utf-8'))}
C = json.load(open(os.path.join(SRC, 'C_all.json'), encoding='utf-8'))
have = {c['h'] for c in C} | set(json.load(open(P('removed-2026-10-12.json'), encoding='utf-8'))['handles'])   # removed on Yarin's request: never add back
pks = {c['pk'] for c in C if c.get('pk')}
if os.path.exists(os.path.join(SRC, 'refresh', 'latest.json')):
    pks |= {x['pk'] for x in json.load(open(os.path.join(SRC, 'refresh', 'latest.json'), encoding='utf-8'))['data'].values() if x.get('pk')}

AR = {'CD':'Child-dev professional','PG':'Parent guide / coach','GAN':'Gan / preschool','EL':'Elementary & remedial teacher','NC':'Home daycare / childcare','P':'Parent','PD':'Parent (dad)','PT':'Parent (twins)','PS':'Parent (single / co-parent / blended)','TR':'Family travel & outings','SE':'Special ed & neurodiversity','HS':'Homeschool / alternative ed','BK':'Books & reading','CM':'Community leader / podcaster','GP':'Grandparent','SF':'Screen-free / free play'}
# the UGC roles in Hebrew, as C_all.json holds them since 20 Oct 2026
R_AUTH, R_EDU, R_LEARN, R_REL, R_KID, R_TEST, R_ADS = 'סמכות מקצועית', 'הסבר חינוכי', 'מיצוב של למידה וחינוך', 'הזדהות', 'תגובת הילד / הקשר משפחתי', 'המלצה של הורה', 'פוטנציאל לחומרים למודעות ממומנות'
R_GIFT, R_SCREEN, R_COMM, R_CREATIVE, R_LIFE, R_DEMO, R_PROOF, R_ORG = 'מתנה', 'מיצוב בלי מסכים', 'הפצה בקהילה', 'הפקה יצירתית', 'לייפסטייל והשראה', 'הדגמת מוצר', 'הוכחה חברתית', 'פוטנציאל לשיתוף פעולה אורגני'
ROLES = {'CD':[R_AUTH,R_EDU,R_LEARN],'PG':[R_AUTH,R_REL,R_EDU],'GAN':[R_LEARN,R_KID,R_COMM],'EL':[R_LEARN,R_EDU],'NC':[R_COMM,R_PROOF],'P':[R_REL,R_KID,R_TEST,R_ADS],'PD':[R_REL,R_KID,R_ADS],'PT':[R_REL,R_KID,R_TEST],'PS':[R_REL,R_TEST,R_ORG],'TR':[R_SCREEN,R_LIFE,R_GIFT],'SE':[R_AUTH,R_EDU],'HS':[R_SCREEN,R_DEMO,R_LEARN],'BK':[R_LEARN,R_AUTH,R_DEMO],'CM':[R_COMM,R_PROOF],'UX':[R_GIFT,R_CREATIVE],'GP':[R_REL,R_KID,R_GIFT],'SF':[R_SCREEN,R_AUTH,R_COMM]}
clamp = lambda x: max(1, min(5, x))
W = [14,14,12,8,10,12,8,6,8,8]
HEM = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']

def ages_of(a):           # "2 עד 8" or "2–8" -> (2, 8); "לא צוין" -> (None, None)
    m = re.match(r'\s*(\d+)\s*(?:עד|–|-)\s*(\d+)', a or '')
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)

def phone_il(d):
    d = re.sub(r'\D', '', d)
    if d.startswith('972'): d = d[3:]
    d = d.lstrip('0')
    return '0' + d if len(d) in (8, 9) else None

contacts = json.load(open(os.path.join(SRC, 'contacts.json'), encoding='utf-8'))
kids = json.load(open(os.path.join(SRC, 'kids.json'), encoding='utf-8'))
added, skipped, new_rows = 0, [], []
for (h, name, code, role, ages, concept, risk) in ROWS:
    if h in have: skipped.append((h, 'already in the map or removed on request')); continue
    if h not in RAW: skipped.append((h, 'not in pass%d_raw.json (did not pass weekly.py check)' % N)); continue
    st = RAW[h]; f, med, last = st['fc'], st['med'], st['last']
    if not 5000 <= f <= 50000: skipped.append((h, '%s followers, outside 5,000 to 50,000' % format(f, ','))); continue
    why, _ = gate.check(st)                       # the admission bar (Yarin, 24 Oct 2026): a creator that fails it never joins
    if why: skipped.append((h, 'does not pass the admission bar: ' + why)); continue
    if st.get('pk') and st['pk'] in pks: skipped.append((h, 'same Instagram account as a creator already in the map (pk %s)' % st['pk'])); continue
    key = code.split(':')[0]; arch = AR.get(key) or ('Unexpected: ' + code.split(':', 1)[1].lower())
    r = (med or 0) / f
    a0, a1 = ages_of(ages)
    aud = {'NC':3,'CM':3,'UX':3,'SF':3}.get(key, 4)
    if a0 == 0 and a1 is not None and a1 <= 5: aud -= 1
    if a0 in (5, 6): aud -= 1                                                  # mostly older than the book's ages
    fit = {'BK':4,'SE':4,'HS':4,'GAN':4,'PD':4,'PT':4,'CD':4,'GP':4,'SF':4}.get(key, 3)
    if re.search(r'גמילה|חיתול|אח חדש|אחות חדשה|אח קטן|אחות קטנה|כיתה א|גננת|ספרי ילדים|ספר ילדים|potty|napp|weaning|sibling|first-grade|kindergarten teacher|\bgan\b|children\'s book', role, re.I): fit += 1
    trust = {'CD':4,'SE':4,'BK':4,'GAN':4,'PG':4,'EL':4,'SF':4}.get(key, 3)
    qual = 4 if r >= 1 else 3 if r >= 0.3 else 2
    auth = 3 if key in ('UX','CM','NC','SF') else 4
    ugc = {'P':4,'PD':4,'PT':4,'PS':4,'GP':4}.get(key, 3)
    if r >= 1: ugc += 1
    if last < (D - datetime.timedelta(days=78)).isoformat(): ugc -= 1         # same cut as the fourth pass (1 Aug for 18 Oct)
    cred = {'CD':5,'SE':5,'PG':4,'EL':4,'BK':4,'GAN':4,'HS':3,'NC':3,'CM':3,'SF':4}.get(key, 2)
    cam = 4 if r >= 0.7 else 3
    comm = 4 if f >= 5000 else 3
    afford = 5 if f < 5000 else 4 if f < 12000 else 3 if f < 25000 else 2
    if r >= 2 and f >= 5000: afford -= 1
    links = [l for l in (st.get('links') or [st.get('ext')]) if l]
    site = next((re.sub(r'^https?://(www\.)?', '', l).split('?')[0].rstrip('/') for l in links if not re.search(r'wa\.me|wa\.link|whatsapp|instagram\.com|tiktok\.com|facebook\.com|youtu|spotify', l)), None)
    managed = re.search(r'סוכנ|ניהול|מיוצג|agent|management', risk, re.I)
    contact = 'הודעה באינסטגרם (דרך ניהול)' if managed else 'הודעה באינסטגרם' + (' · ' + site[:60] if site else '')
    # the estimate of how they work: same rule as the second pass
    if key in ('P','PD','PT','PS','HS','NC','UX','GP') and afford >= 5: prac = "Likely gifted-only (est.)"
    elif 'UGC' in role: prac = "Low-cost paid micro (est.) — offers UGC"
    elif managed or (r >= 2 and f >= 10000): prac = "Potentially expensive relative to size (est.)"
    elif f >= 25000: prac = "Standard paid micro (est.)"
    else: prac = "Gifted + affiliate (est.)"
    sells = re.search(r'(?:^|[\s;(])(?:מוכר|מוכרת|מוכרים|מכירת)\s|\bsells\b', risk, re.I)
    conflict = "Adjacent (own books/products)" if sells else "No apparent conflict"
    s = [clamp(aud), clamp(fit), clamp(trust), qual, clamp(auth), clamp(ugc), clamp(cred), cam, comm, clamp(afford)]
    C.append(dict(h=h, name=name, plat="Instagram", f=f, med=med, last=last, lang='he', loc=None, arch=arch, role=role, ages=ages, topics=role,
                  roles=ROLES[key], prac=prac, conflict=conflict, s=s, concept=concept, risk=risk, contact=contact, short=False, extra="pass%d" % N,
                  score=round(sum(w * x for w, x in zip(W, s)) / 5, 1), added_on=DAY, pk=st.get('pk') or None))
    have.add(h); added += 1
    if st.get('pk'): pks.add(st['pk'])
    # contacts the creator publishes: phones and emails written in the bio, and WhatsApp numbers in bio links
    bio = st.get('bio') or ''
    ph = [phone_il(x) for x in re.findall(r'(?<!\d)0(?:5\d|[2-489]|7\d)[- ]?\d{3}[- ]?\d{4}(?!\d)', bio)]
    em = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', bio)
    wa = [phone_il(m) for l in links for m in re.findall(r'wa\.me/(?:message/)?\+?(\d{9,13})', l)] + [phone_il(m) for l in links for m in re.findall(r'whatsapp\.com/send/?\?phone=\+?(\d{9,13})', l)]
    src = (["Instagram bio"] if ph or em else []) + (["Instagram bio link (WhatsApp)"] if any(wa) else [])
    phones = list(dict.fromkeys([x for x in ph + wa if x]))
    if phones or em: contacts[h] = {"email": em, "phone": phones, "src": src}
    if h in KIDS: kids[h] = dict(KIDS[h], src="bio, read %d %s %d" % (D.day, D.strftime('%b'), D.year))
    new_rows.append(C[-1])

json.dump(C, open(os.path.join(SRC, 'C_all.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(contacts, open(os.path.join(SRC, 'contacts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(kids, open(os.path.join(SRC, 'kids.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# the CSV the dashboard reads: one row per new creator, same columns as the third pass
CSV = os.path.join(os.path.dirname(SRC), 'creators-200-2026-10-03.csv')
rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig'))); cols = list(rows[0].keys()); inside = {r['handle'].lstrip('@') for r in rows}
for c in new_rows:
    if c['h'] in inside: continue
    k = contacts.get(c['h'], {}); ph = ', '.join(k.get('phone', [])); em = ', '.join(k.get('email', []))
    ch = 'WhatsApp' if ph else 'Email' if em else 'Instagram DM'
    s = c['s']
    rows.append({**{x: '' for x in cols}, 'score': c['score'], 'research_pass': str(N), 'handle': '@' + c['h'], 'platform': 'Instagram', 'url': 'https://www.instagram.com/%s/' % c['h'],
                 'name': c['name'], 'followers': c['f'], 'median_reel_views_last12': c['med'] or '', 'last_reel': c['last'], 'archetype': c['arch'], 'role': c['role'], 'child_ages': c['ages'],
                 'ugc_roles': '; '.join(c['roles']), 'practicality_estimate': c['prac'], 'brand_conflict': c['conflict'], 'aud_fit': s[0], 'brand_fit': s[1], 'parent_trust': s[2], 'content_quality_est': s[3],
                 'authenticity': s[4], 'ugc_potential': s[5], 'credibility': s[6], 'on_camera_est': s[7], 'commercial': s[8], 'affordability': s[9], 'content_concept': c['concept'], 'risks': c['risk'],
                 'contact': c['contact'], 'email': em, 'phone_whatsapp': ph, 'contact_found_on': '; '.join(k.get('src', [])), 'first_channel': ch, 'checked_on': DAY, 'wave': str(N), 'send_via': ch,
                 'personal_line_check': 'generic line by category; replace with something specific if you can'})
w = csv.DictWriter(open(CSV, 'w', encoding='utf-8-sig', newline=''), fieldnames=cols); w.writeheader(); w.writerows(rows)
# the weekly ledger: every account shown in this run's reviews, picked or not
if opt('--reviewed'):
    LEDGER = os.path.join(HERE, 'weekly', 'reviewed.json')
    led = json.load(open(LEDGER, encoding='utf-8')) if os.path.exists(LEDGER) else {}
    for p in opt('--reviewed').split(','):
        for h in json.load(open(p, encoding='utf-8')): led[h] = DAY
    json.dump(dict(sorted(led.items())), open(LEDGER, 'w', encoding='utf-8'), indent=0)
    print('reviewed ledger', len(led))
new = [c for c in C if c.get('extra') == 'pass%d' % N]
print('pass', N, '| added', added, '| total', len(C), '| csv rows', len(rows))
for h, why in skipped: print('  SKIPPED', h, '|', why)
print(Counter(c['arch'] for c in new).most_common())
print(Counter(c['prac'] for c in new).most_common())
print('contacts now', len(contacts), '| kids now', len(kids))
