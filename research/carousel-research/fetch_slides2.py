import sys, re, json, os, subprocess, html
sys.path.insert(0,'.')
from fetch_slides import fetch, sheet, UA
def caption(code):
    h=subprocess.run(["curl","-s","-A",UA,f"https://www.instagram.com/p/{code}/embed/captioned/"],capture_output=True,text=True).stdout
    m=re.search(r'<div class="Caption">(.*?)<div class="CaptionComments">',h,re.S)
    if m:
        t=re.sub(r'<br\s*/?>','\n',m.group(1)); t=re.sub(r'<[^>]+>','',t); return html.unescape(t).strip()
    m=re.search(r'edge_media_to_caption\\":\{\\"edges\\":\[\{\\"node\\":\{\\"text\\":\\"(.*?)\\"\}',h)
    if m:
        try: return json.loads('"'+m.group(1).replace('\\\\','\\')+'"')
        except Exception: return m.group(1)
    return ''
if __name__=="__main__":
    out={}
    if os.path.exists('captions.json'): out=json.load(open('captions.json'))
    for code in sys.argv[1:]:
        fs=fetch(code); p=sheet(code,fs,maxs=20); c=caption(code)
        out[code]={'slides':len(fs),'caption':c}
        print(code,len(fs),p,len(c))
    json.dump(out,open('captions.json','w'),ensure_ascii=False,indent=1)
