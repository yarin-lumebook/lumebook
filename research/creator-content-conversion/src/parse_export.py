import json,sys
f=sys.argv[1]
a=json.load(open(f))
t=a[0]['text']
dec=json.JSONDecoder()
obj,end=dec.raw_decode(t)
if isinstance(obj,str):
    if obj.startswith('{') and '\n[' in obj:
        head,body=obj.split('\n',1); print('head',head); obj=json.loads(body)
    else:
        obj=json.loads(obj)
items = obj if isinstance(obj,list) else [obj]
for d in items:
    if isinstance(d,str): d=json.loads(d)
    json.dump(d,open('raw/%s.json'%d['username'],'w'),ensure_ascii=False)
    print('saved',d['username'],len(d['posts']),d['prof'] and d['prof'].get('fc'))
