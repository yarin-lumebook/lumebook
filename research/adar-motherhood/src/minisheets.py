"""Compact hook sheets: 4 frames (0.3, 1.5, 3, 5 s) per Reel, 4 Reels per image. Usage: minisheets.py OUTDIR CODE..."""
import sys, subprocess, os
from PIL import Image, ImageDraw
M='/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-11-11-adar-motherhood-reels'
out=sys.argv[1]; codes=sys.argv[2:]; os.makedirs(out,exist_ok=True)
H=380
def frames(c):
    ims=[]
    for t in (0.3,1.5,3,5):
        p=f'/private/tmp/claude-501/-Users-yarinbruner-Claude-Projects-Lumebook/6ef979a9-888f-449b-a882-aacd93f89ec4/scratchpad/{c}_{t}.jpg'
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',f'{M}/videos/{c}.mp4','-frames:v','1','-vf',f'scale=-2:{H}',p])
        ims.append(Image.open(p))
    return ims
for n in range(0,len(codes),4):
    grp=codes[n:n+4]; rows=[frames(c) for c in grp]
    W=max(sum(i.width for i in r)+6*3 for r in rows)
    sh=Image.new('RGB',(W,(H+22)*len(rows)),(20,20,20)); d=ImageDraw.Draw(sh)
    for k,(c,r) in enumerate(zip(grp,rows)):
        d.text((4,k*(H+22)+4),c,fill=(255,230,120)); x=0
        for im in r: sh.paste(im,(x,k*(H+22)+20)); x+=im.width+6
    sh.save(f'{out}/sheet{n//4+1}.jpg',quality=80); print('wrote',n//4+1,grp)
