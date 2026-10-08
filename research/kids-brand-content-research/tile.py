# Portrait-friendly frame sheets: frames every N s at 640px tall, 6 per sheet, timestamp labels.
import sys, os, subprocess, json, glob
from PIL import Image, ImageDraw, ImageFont
vid=sys.argv[1]; vidid=os.path.basename(vid)[:-4]; d=f'analysis/{vidid}/frames'
if os.path.exists(f'{d}/index.json'): print(vidid,'exists'); sys.exit()
os.makedirs(d,exist_ok=True)
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',vid]).strip())
step=1.0 if dur<=20 else (1.5 if dur<=45 else (2.0 if dur<=90 else dur/45))
ts=[round(t*step,2) for t in range(int(dur/step)+1) if t*step<dur-0.05]
files=[]
for i,t in enumerate(ts):
    out=f'{d}/f_{i:03d}_{t:06.2f}s.jpg'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',vid,'-frames:v','1','-vf','scale=-2:640',out])
    if os.path.exists(out): files.append((t,out))
font=ImageFont.load_default(size=28) if hasattr(ImageFont,'load_default') else None
sheets=[]
for s in range(0,len(files),6):
    chunk=files[s:s+6]; ims=[Image.open(f) for _,f in chunk]
    w=sum(im.width for im in ims)+8*(len(ims)-1); h=640+40
    sh=Image.new('RGB',(w,h),(17,17,20)); x=0; dr=ImageDraw.Draw(sh)
    for (t,_),im in zip(chunk,ims):
        sh.paste(im,(x,40)); dr.text((x+6,4),f'{int(t//60):02d}:{t%60:05.2f}',fill=(255,230,120),font=font); x+=im.width+8
    p=f'{d}/sheet_{s//6+1:02d}.jpg'; sh.save(p,quality=85); sheets.append({'sheet':p,'from':chunk[0][0],'to':chunk[-1][0]})
json.dump({'duration':dur,'step_s':step,'frames':[{'t':t,'file':f} for t,f in files],'sheets':sheets},open(f'{d}/index.json','w'),indent=1)
print(vidid,len(files),'frames',len(sheets),'sheets')
