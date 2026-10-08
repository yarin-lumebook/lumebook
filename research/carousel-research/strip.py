import sys,os,glob
from PIL import Image
H=420
for code in sys.argv[1:]:
    allf=sorted(glob.glob(f'slides/{code}/*.jpg')); fs=allf if len(allf)<=5 else allf[:4]+allf[-1:]
    ims=[]
    for f in fs:
        try:
            im=Image.open(f).convert('RGB'); ims.append(im.resize((int(im.width*H/im.height),H)))
        except Exception: pass
    if not ims: print(code,'none'); continue
    gap=6; W=sum(i.width for i in ims)+gap*(len(ims)-1)
    S=Image.new('RGB',(W,H),(255,255,255)); x=0
    for i in ims: S.paste(i,(x,0)); x+=i.width+gap
    os.makedirs('img2',exist_ok=True)
    p=f'img2/{code}.jpg'; S.save(p,quality=78,optimize=True); print(code,len(fs),S.size,os.path.getsize(p)//1024,'KB')
