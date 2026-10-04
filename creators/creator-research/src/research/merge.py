import json
exec(open('data.py').read())          # C (70 Hebrew, first pass)
exec(open('data2.py').read())         # N
stats={}
for l in open('deep2.txt'):
    l=l.rstrip('\n')
    if not l: continue
    h,f,rest=l.split('|',2); bio,med,mx,last=rest.rsplit('|',3)
    stats[h]=dict(f=int(f),med=int(med) if med not in('','-') else None,last=last)
AR={'CD':'Child-dev professional','PG':'Parent guide / coach','GAN':'Gan / preschool','EL':'Elementary & remedial teacher','NC':'Home daycare / childcare','P':'Parent','PD':'Parent (dad)','PT':'Parent (twins)','PS':'Parent (single / co-parent / blended)','TR':'Family travel & outings','SE':'Special ed & neurodiversity','HS':'Homeschool / alternative ed','BK':'Books & reading','CM':'Community leader / podcaster'}
ROLES={'CD':["Professional authority","Educational explanation","Learning/education positioning"],'PG':["Professional authority","Relatability","Educational explanation"],'GAN':["Learning/education positioning","Child reaction / family context","Community distribution"],'EL':["Learning/education positioning","Educational explanation"],'NC':["Community distribution","Social proof"],'P':["Relatability","Child reaction / family context","Parent testimonial","Paid-ad creative potential"],'PD':["Relatability","Child reaction / family context","Paid-ad creative potential"],'PT':["Relatability","Child reaction / family context","Parent testimonial"],'PS':["Relatability","Parent testimonial","Organic collaboration potential"],'TR':["Screen-free positioning","Lifestyle/aspirational","Gifting"],'SE':["Professional authority","Educational explanation"],'HS':["Screen-free positioning","Product demonstration","Learning/education positioning"],'BK':["Learning/education positioning","Professional authority","Product demonstration"],'CM':["Community distribution","Social proof"],'UX':["Gifting","Creative production"]}
BASE={'CD':(4,5,5,5,4,4),'PG':(4,4,4,4,4,4),'GAN':(5,5,5,4,5,4),'EL':(4,4,4,4,4,3),'NC':(3,4,4,3,4,3),'P':(4,4,4,2,5,5),'PD':(5,5,4,2,5,5),'PT':(4,5,4,2,5,5),'PS':(4,4,4,3,5,4),'TR':(4,4,4,2,4,4),'SE':(4,5,5,5,5,3),'HS':(4,5,4,3,5,4),'BK':(4,5,5,4,4,4),'CM':(3,4,4,3,4,2),'UX':(3,4,3,2,4,4)}
def clamp(x): return max(1,min(5,x))
for (h,name,code,role,ages,concept,risk,contact) in N:
    st=stats[h]; f,med,last=st['f'],st['med'],st['last']
    key=code.split(':')[0]; arch=AR.get(key) or ('Unexpected: '+code.split(':',1)[1].lower())
    import re
    r=(med or 0)/f
    aud={'NC':3,'CM':3,'UX':3}.get(key,4)
    if ages.startswith('0') and ages.split('–')[-1].strip() in ('2','3','4'): aud-=1
    fit={'BK':4,'SE':4,'HS':4,'GAN':4,'PD':4,'PT':4,'CD':4}.get(key,3)
    if re.search(r'potty|diaper|weaning|sibling|book|author|kindergarten teacher|gan', role+' '+concept, re.I): fit+=1
    trust={'CD':4,'SE':4,'BK':4,'GAN':4,'PG':4,'EL':4}.get(key,3)
    qual=4 if r>=1 else 3 if r>=0.3 else 2
    auth=3 if key in('UX','CM','NC') else 4
    ugc={'P':4,'PD':4,'PT':4,'PS':4}.get(key,3)
    if r>=1: ugc+=1
    if last<'2026-07-01': ugc-=1
    cred={'CD':5,'SE':5,'PG':4,'EL':4,'BK':4,'GAN':4,'HS':3,'NC':3,'CM':3}.get(key,2)
    cam=4 if r>=0.7 else 3
    comm=4 if f>=5000 else 3
    afford=5 if f<5000 else 4 if f<12000 else 3 if f<25000 else 2
    if r>=2 and f>=5000: afford-=1
    if key in('P','PD','PT','PS','HS','NC','UX') and afford>=5: prac="Likely gifted-only (est.)"
    elif 'UGC' in role or 'UGC' in concept: prac="Low-cost paid micro (est.) — offers UGC"
    elif 'managed' in risk.lower() or 'management' in contact or (r>=2 and f>=10000): prac="Potentially expensive relative to size (est.)"
    elif f>=25000: prac="Standard paid micro (est.)"
    elif f<5000: prac="Likely gifted-only (est.)"
    else: prac="Gifted + affiliate (est.)"
    conflict="Adjacent (own books/products)" if (key=='BK' or 'Sells' in risk or 'sells' in risk or 'own parenting brand' in risk) else "No apparent conflict"
    C.append(dict(h=h,name=name,plat="Instagram",f=f,med=med,last=last,lang='he',loc=None,arch=arch,role=role,ages=ages,topics=role,roles=ROLES[key],prac=prac,conflict=conflict,s=[clamp(aud),clamp(fit),clamp(trust),qual,clamp(auth),clamp(ugc),clamp(cred),cam,comm,clamp(afford)],concept=concept,risk=risk,contact=contact,short=False,extra="pass2"))
REMAP={'ima.shir','orli.parenthood','yael__lazar','parentips_by_shir','avital.bashan','marialguide','chenkadoshnice','ifatmatznerherooti','michalrahamim7','henhaim8','mor_knoll'}
for c in C:
    if c['h'] in REMAP: c['arch']='Parent guide / coach'
    c['arch']={'Family travel':'Family travel & outings','Nanny / childcare':'Home daycare / childcare','Elementary teacher':'Elementary & remedial teacher'}.get(c['arch'],c['arch'])
SHORT={'knafaim.ot_by_noy','lital_magnezi','eden_spaiev','yeladim_ktanim','ima.shir','hadas.shvat','etti_haft','hilla_gover_slp','nataliegaash','saba.chiche','ganotmor','rotem__unger','almaanddad','daria_mansour1','books_are_friends_slp'}
for c in C: c['short']=c['h'] in SHORT
HAND={'nataliegaash':[5,5,5,3,4,4,5,4,4,3],'almaanddad':[5,5,4,4,5,5,2,5,4,2],'books_are_friends_slp':[5,5,5,3,5,4,5,3,3,5]}
for c in C:
    if c['h'] in HAND: c['s']=HAND[c['h']]; c['extra']='pass2-hand'
W=[14,14,12,8,10,12,8,6,8,8]
for c in C: c['score']=round(sum(w*s for w,s in zip(W,c['s']))/5,1)
json.dump(C,open('C_all.json','w'),ensure_ascii=False)
from collections import Counter
print(len(C), sum(c['short'] for c in C)); print(Counter(c['arch'] for c in C).most_common())
missing=SHORT-set(c['h'] for c in C); print('missing',missing)
