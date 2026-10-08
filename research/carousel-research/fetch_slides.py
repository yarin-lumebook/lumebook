import sys, re, json, os, subprocess, html
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15"
def fetch(code):
    out=f"slides/{code}"
    os.makedirs(out,exist_ok=True)
    h=subprocess.run(["curl","-s","-A",UA,f"https://www.instagram.com/p/{code}/embed/captioned/"],capture_output=True,text=True).stdout
    i=h.find('edge_sidecar_to_children')
    urls=[]
    if i>=0:
        seg=h[i:i+200000]
        for m in re.finditer(r'\\"is_video\\":(true|false),\\"display_url\\":\\"(.*?)\\"',seg):
            u=m.group(2).replace('\\\\\\/','/').replace('\\\\u00253D','%3D').replace('\\\\u0026','&').replace('\\u0026','&')
            u=u.replace('\\/','/')
            urls.append((m.group(1)=='true',html.unescape(u)))
    # dedupe preserve order
    seen=set();res=[]
    for v,u in urls:
        k=u.split('?')[0]
        if k in seen: continue
        seen.add(k);res.append((v,u))
    files=[]
    for n,(v,u) in enumerate(res):
        f=f"{out}/{n+1:02d}.jpg"
        if not os.path.exists(f):
            subprocess.run(["curl","-s","-L","-A",UA,"-o",f,u])
        files.append((f,v))
    return files
def sheet(code,files,maxs=10):
    from PIL import Image
    ims=[]
    for f,v in files[:maxs]:
        try: ims.append(Image.open(f).convert('RGB'))
        except Exception as e: pass
    if not ims: return None
    H=480
    ims=[im.resize((int(im.width*H/im.height),H)) for im in ims]
    cols=min(5,len(ims)); rows=(len(ims)+cols-1)//cols
    W=max(sum(im.width for im in ims[r*cols:(r+1)*cols]) for r in range(rows))
    S=Image.new('RGB',(W,H*rows),'white')
    for r in range(rows):
        x=0
        for im in ims[r*cols:(r+1)*cols]:
            S.paste(im,(x,r*H)); x+=im.width
    p=f"slides/{code}_sheet.jpg"; S.save(p,quality=82); return p
if __name__=="__main__":
    for code in sys.argv[1:]:
        fs=fetch(code); p=sheet(code,fs)
        print(code,len(fs),p)
