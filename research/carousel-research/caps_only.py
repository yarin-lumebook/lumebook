import sys,json,os
sys.path.insert(0,'.')
from fetch_slides2 import caption
out=json.load(open('captions.json')) if os.path.exists('captions.json') else {}
for c in sys.argv[1:]:
    if c in out and out[c].get('caption'): continue
    out[c]={'slides':out.get(c,{}).get('slides'),'caption':caption(c)}
json.dump(out,open('captions.json','w'),ensure_ascii=False,indent=1)
for c in sys.argv[1:]:
    t=(out[c]['caption'] or '').replace('\n',' / ')
    print('##',c,'|',t[:160],'…',t[-200:] if len(t)>360 else '')
