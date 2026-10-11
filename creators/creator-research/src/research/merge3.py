"""Third pass (11 Oct 2026): add the creators in data3.py to C_all.json, with the stats read into pass3_raw.json.

Run from src/research:  python3 merge3.py
It only appends. Existing creators are never changed, and running it twice adds nothing.
Ratings use the same rules as the second pass (merge.py), with one difference: the brand-fit bonus looks at the
role (what the bio says), not at the content idea I wrote.
"""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(HERE, f)
SRC = os.path.dirname(HERE)
exec(open(P('data3.py'), encoding='utf-8').read())          # N3, KIDS3
RAW = {x['h']: x for x in json.load(open(P('pass3_raw.json'), encoding='utf-8'))}
C = json.load(open(os.path.join(SRC, 'C_all.json'), encoding='utf-8'))
have = {c['h'] for c in C}

AR = {'CD':'Child-dev professional','PG':'Parent guide / coach','GAN':'Gan / preschool','EL':'Elementary & remedial teacher','NC':'Home daycare / childcare','P':'Parent','PD':'Parent (dad)','PT':'Parent (twins)','PS':'Parent (single / co-parent / blended)','TR':'Family travel & outings','SE':'Special ed & neurodiversity','HS':'Homeschool / alternative ed','BK':'Books & reading','CM':'Community leader / podcaster','GP':'Grandparent','SF':'Screen-free / free play'}
ROLES = {'CD':["Professional authority","Educational explanation","Learning/education positioning"],'PG':["Professional authority","Relatability","Educational explanation"],'GAN':["Learning/education positioning","Child reaction / family context","Community distribution"],'EL':["Learning/education positioning","Educational explanation"],'NC':["Community distribution","Social proof"],'P':["Relatability","Child reaction / family context","Parent testimonial","Paid-ad creative potential"],'PD':["Relatability","Child reaction / family context","Paid-ad creative potential"],'PT':["Relatability","Child reaction / family context","Parent testimonial"],'PS':["Relatability","Parent testimonial","Organic collaboration potential"],'TR':["Screen-free positioning","Lifestyle/aspirational","Gifting"],'SE':["Professional authority","Educational explanation"],'HS':["Screen-free positioning","Product demonstration","Learning/education positioning"],'BK':["Learning/education positioning","Professional authority","Product demonstration"],'CM':["Community distribution","Social proof"],'UX':["Gifting","Creative production"],'GP':["Relatability","Child reaction / family context","Gifting"],'SF':["Screen-free positioning","Professional authority","Community distribution"]}
clamp = lambda x: max(1, min(5, x))
W = [14,14,12,8,10,12,8,6,8,8]

def phone_il(d):
    d = re.sub(r'\D', '', d)
    if d.startswith('972'): d = d[3:]
    d = d.lstrip('0')
    return '0' + d if len(d) in (8, 9) else None

contacts = json.load(open(os.path.join(SRC, 'contacts.json'), encoding='utf-8'))
kids = json.load(open(os.path.join(SRC, 'kids.json'), encoding='utf-8'))
added = 0
for (h, name, code, role, ages, concept, risk) in N3:
    if h in have: continue
    st = RAW[h]; f, med, last = st['fc'], st['med'], st['last']
    key = code.split(':')[0]; arch = AR.get(key) or ('Unexpected: ' + code.split(':', 1)[1].lower())
    r = (med or 0) / f
    aud = {'NC':3,'CM':3,'UX':3,'SF':3}.get(key, 4)
    if ages.startswith('0') and ages.split('–')[-1].strip() in ('2','3','4','5'): aud -= 1
    if ages.split('–')[0].strip() in ('5','6'): aud -= 1                      # mostly older than the book's ages
    fit = {'BK':4,'SE':4,'HS':4,'GAN':4,'PD':4,'PT':4,'CD':4,'GP':4,'SF':4}.get(key, 3)
    if re.search(r'potty|napp|weaning|sibling|first-grade|kindergarten teacher|gan\b|children\'s book', role, re.I): fit += 1
    trust = {'CD':4,'SE':4,'BK':4,'GAN':4,'PG':4,'EL':4,'SF':4}.get(key, 3)
    qual = 4 if r >= 1 else 3 if r >= 0.3 else 2
    auth = 3 if key in ('UX','CM','NC','SF') else 4
    ugc = {'P':4,'PD':4,'PT':4,'PS':4,'GP':4}.get(key, 3)
    if r >= 1: ugc += 1
    if last < '2026-08-01': ugc -= 1
    cred = {'CD':5,'SE':5,'PG':4,'EL':4,'BK':4,'GAN':4,'HS':3,'NC':3,'CM':3,'SF':4}.get(key, 2)
    cam = 4 if r >= 0.7 else 3
    comm = 4 if f >= 5000 else 3
    afford = 5 if f < 5000 else 4 if f < 12000 else 3 if f < 25000 else 2
    if r >= 2 and f >= 5000: afford -= 1
    links = [l for l in (st.get('links') or [st.get('ext')]) if l]
    site = next((re.sub(r'^https?://(www\.)?', '', l).split('?')[0].rstrip('/') for l in links if not re.search(r'wa\.me|wa\.link|whatsapp|instagram\.com|tiktok\.com|facebook\.com|youtu|spotify', l)), None)
    contact = 'IG DM' + (' · ' + site[:60] if site else '')
    if 'agent' in risk.lower(): contact = 'IG DM (management)'
    # the estimate of how they work: same rule as the second pass
    if key in ('P','PD','PT','PS','HS','NC','UX','GP') and afford >= 5: prac = "Likely gifted-only (est.)"
    elif 'UGC' in role: prac = "Low-cost paid micro (est.) — offers UGC"
    elif 'management' in contact or (r >= 2 and f >= 10000): prac = "Potentially expensive relative to size (est.)"
    elif f >= 25000: prac = "Standard paid micro (est.)"
    elif f < 5000: prac = "Likely gifted-only (est.)"
    else: prac = "Gifted + affiliate (est.)"
    conflict = "Adjacent (own books/products)" if re.search(r'Sells|sells', risk) else "No apparent conflict"
    s = [clamp(aud), clamp(fit), clamp(trust), qual, clamp(auth), clamp(ugc), clamp(cred), cam, comm, clamp(afford)]
    C.append(dict(h=h, name=name, plat="Instagram", f=f, med=med, last=last, lang='he', loc=None, arch=arch, role=role, ages=ages, topics=role,
                  roles=ROLES[key], prac=prac, conflict=conflict, s=s, concept=concept, risk=risk, contact=contact, short=False, extra="pass3",
                  score=round(sum(w * x for w, x in zip(W, s)) / 5, 1)))
    added += 1
    # contacts the creator publishes: phones and emails written in the bio, and WhatsApp numbers in bio links
    bio = st.get('bio') or ''
    ph = [phone_il(x) for x in re.findall(r'(?<!\d)0(?:5\d|[2-489]|7\d)[- ]?\d{3}[- ]?\d{4}(?!\d)', bio)]
    em = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', bio)
    wa = [phone_il(m) for l in links for m in re.findall(r'wa\.me/(?:message/)?\+?(\d{9,13})', l)] + [phone_il(m) for l in links for m in re.findall(r'whatsapp\.com/send/?\?phone=\+?(\d{9,13})', l)]
    src = (["Instagram bio"] if ph or em else []) + (["Instagram bio link (WhatsApp)"] if any(wa) else [])
    phones = list(dict.fromkeys([x for x in ph + wa if x]))
    if phones or em: contacts[h] = {"email": em, "phone": phones, "src": src}
    if h in KIDS3: kids[h] = dict(KIDS3[h], src="bio, read 11 Oct 2026")

json.dump(C, open(os.path.join(SRC, 'C_all.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(contacts, open(os.path.join(SRC, 'contacts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(kids, open(os.path.join(SRC, 'kids.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
new = [c for c in C if c.get('extra') == 'pass3']
print('added', added, '| total', len(C), '| pass3', len(new))
print(Counter(c['arch'] for c in new).most_common())
print(Counter(c['prac'] for c in new).most_common())
print('contacts now', len(contacts), '| kids now', len(kids))
