import json,glob,sys
sys.path.insert(0,'.')
from classify import classify_post
OLD=sys.argv[1]
CM=json.load(open('cm.json')); CM.update(json.load(open('cm_extra.json')))
caps={}
for f in glob.glob('raw/*.json'):
    d=json.load(open(f))
    for p in d['posts']: caps[p['code']]=(d['username'],p.get('cap'))
agent={}
for f in glob.glob(OLD+'/comments_coded/*.json')+glob.glob(OLD+'/comments_extra_coded/*.json'):
    for p in json.load(open(f))['posts']: agent[p['code']]=p['counts']
pairs=[]
tot_r={};tot_a={}
for code,v in CM.items():
    if code not in agent or code not in caps: continue
    u,cap=caps[code]
    lab=classify_post(u,cap,v['comments'][:30])
    r={k:lab.count(k) for k in ['keyword','purchase','intent','product_q','creator']}
    a=agent[code]
    A={'keyword':a.get('keyword_request',0),'purchase':a.get('purchase_report',0),'intent':a.get('explicit_buying_intent',0),'product_q':a.get('product_or_price_question',0),'creator':a.get('creator_reply',0)}
    pairs.append((code,r,A))
    for k in r: tot_r[k]=tot_r.get(k,0)+r[k]; tot_a[k]=tot_a.get(k,0)+A[k]
print('posts',len(pairs)); print('rules ',tot_r); print('agents',tot_a)
def spear(x,y):
    import statistics
    def rank(v):
        s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
        i=0
        while i<len(s):
            j=i
            while j+1<len(s) and v[s[j+1]]==v[s[i]]: j+=1
            for k in range(i,j+1): r[s[k]]=(i+j)/2
            i=j+1
        return r
    rx,ry=rank(x),rank(y); mx,my=statistics.mean(rx),statistics.mean(ry)
    num=sum((a-mx)*(b-my) for a,b in zip(rx,ry)); den=(sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))**.5
    return num/den if den else float('nan')
for k in ['keyword','product_q']:
    print(k,'spearman per post',round(spear([p[1][k] for p in pairs],[p[2][k] for p in pairs]),3))
sig=lambda d:d['purchase']+d['intent']+d['product_q']
print('intent signal spearman',round(spear([sig(p[1]) for p in pairs],[sig(p[2]) for p in pairs]),3))
# biggest disagreements
dis=sorted(pairs,key=lambda p:-abs(sig(p[1])-sig(p[2])))[:8]
for code,r,a in dis: print(code,'rules',r,'agent',a)
