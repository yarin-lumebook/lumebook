"""Stack review.jpg strips of several Reels into one image with code labels, for my verification pass.
python stack_strips.py OUT.jpg CODE...  (watch-video venv)"""
import sys
from PIL import Image, ImageDraw, ImageFont
M='/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-10-15-israeli-product-reels/analysis'
out, codes = sys.argv[1], sys.argv[2:]
ims=[Image.open(f'{M}/{c}/review.jpg') for c in codes]
w=max(i.width for i in ims); h=sum(i.height+34 for i in ims)
sh=Image.new('RGB',(w,h),(255,255,255)); d=ImageDraw.Draw(sh); f=ImageFont.load_default(size=28); y=0
for c,i in zip(codes,ims):
    d.text((6,y+2),c,fill=(200,0,80),font=f); sh.paste(i,(0,y+34)); y+=i.height+34
sh=sh.resize((int(w*0.75),int(h*0.75))); sh.save(out,quality=80); print(out,sh.size)
