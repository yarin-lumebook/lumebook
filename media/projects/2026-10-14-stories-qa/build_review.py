from pathlib import Path
import json, shutil, struct, html, zipfile
root=Path(__file__).resolve().parent
mapping=json.loads("[{\"id\":\"01-opener\",\"path\":\"/Users/yarinbruner/.codex/generated_images/01a13958-4d64-7a93-bc78-1f5ccd8b8234/exec-36542e0e-7027-408c-83b9-2d5c4105cec7.png\"},{\"id\":\"02-personalisation\",\"path\":\"/Users/yarinbruner/.codex/generated_images/01a13958-4d64-7a93-bc78-1f5ccd8b8234/exec-0b14ce0c-1310-4c15-819f-a4ee6b769133.png\"},{\"id\":\"03-getting-started\",\"path\":\"/Users/yarinbruner/.codex/generated_images/01a13958-4d64-7a93-bc78-1f5ccd8b8234/exec-bd2310a1-fddc-4cca-9ae5-6541005da8be.png\"},{\"id\":\"04-free-preview\",\"path\":\"/Users/yarinbruner/.codex/generated_images/01a13958-4d64-7a93-bc78-1f5ccd8b8234/exec-5f8b874b-ca67-4d51-ac7e-6bc3441c9663.png\"},{\"id\":\"05-photo\",\"path\":\"/Users/yarinbruner/.codex/generated_images/01a13958-4d64-7a93-bc78-1f5ccd8b8234/exec-d4d35cbf-129a-4f09-a675-4738e7ac22a1.png\"},{\"id\":\"06-book-format\",\"path\":\"/Users/yarinbruner/.codex/generated_images/01a13958-4d64-7a93-bc78-1f5ccd8b8234/exec-c3598828-2fb5-4b48-b560-3e9b469afd9f.png\"},{\"id\":\"07-your-question\",\"path\":\"/Users/yarinbruner/.codex/generated_images/01a13958-4d64-7a93-bc78-1f5ccd8b8234/exec-1849dc97-694d-45f4-8760-8fb90d49dd4d.png\"}]")
data=json.loads((root/"series.json").read_text())
report=[]
for item in mapping:
    dest=root/(item["id"]+".png")
    shutil.copy2(item["path"],dest)
    raw=dest.read_bytes()
    width,height=struct.unpack(">II",raw[16:24])
    report.append({"file":dest.name,"width":width,"height":height,"visual_qa":"Hebrew checked against copy; correct RTL; no missing copy"})
(root/"dimensions.json").write_text(json.dumps(report,indent=2))
copy="\n\n".join(str(i+1)+"/7\n"+s["title"]+"\n"+s["answer"] for i,s in enumerate(data["frames"]))
(root/"copy.txt").write_text(copy+"\n")
notes="""# LumeBook Q&A story series
Created 14 October 2026
Voice: documented fallback Hebrew voice, not yet calibrated to Yarin
Images: built-in image_gen using canonical mascot and logo references
Seven numbered portrait PNGs in posting order; original generated dimensions are in dimensions.json
Prompts: complete generation prompt for each frame is saved in series.json

## Posting
Upload 01 through 07 in order
Frame 7: add a native Instagram Questions sticker in the blank cream area below the answer and left of Lume
Suggested sticker label: מה תרצו לדעת?
Keep the sticker left of centre so it does not cover Lume
The sticker must be added in Instagram so viewers can submit an answer
These are editorial product questions, not claimed customer submissions
Illustrated books and children are conceptual generated visuals, not actual product photography or customer images
No publishing was performed

## Checked product facts
Read https://lumebook.com/IL/he on 14 October 2026
Frame 2: the name is in the story and the illustrated character is based on the uploaded photo, per homepage steps and FAQ on https://lumebook.com/IL/he
Frame 3: story selection, name/photo entry and preview are described in the how-it-works section and FAQ on https://lumebook.com/IL/he
Frame 4: the preview is free and precedes purchase, per FAQ on https://lumebook.com/IL/he
Frame 5: a clear well-lit face photo is recommended and another photo can be tried, per FAQ on https://lumebook.com/IL/he
Frame 6: soft cover, colour pages and a digital copy by email are described in the product-format and receipt FAQ on https://lumebook.com/IL/he
Frames 1 and 7: editorial introduction and invitation with no external factual claim
No pricing, delivery deadline, age range or child-development outcome claims are used
Loose copy passed the project Hebrew voice lint with zero issues
Rendered Hebrew was visually checked against copy.json on all seven frames
Generated line breaks vary slightly from the copy source while preserving every word
"""
(root/"README.md").write_text(notes)
cards=[]
for i,s in enumerate(data["frames"]):
    filename=s["id"]+".png"
    cards.append('<article class="lb-card"><div class="lb-row"><h2>'+str(i+1)+'/7</h2><a class="lb-btn" href="'+filename+'" download>הורדת התמונה</a></div><img loading="lazy" src="'+filename+'" alt="'+html.escape(s["title"].replace("\n"," "),quote=True)+'"><p>'+html.escape(s["title"]).replace("\n","<br>")+'</p><p>'+html.escape(s["answer"]).replace("\n","<br>")+'</p></article>')
page='''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LumeBook Q&amp;A stories</title><link rel="stylesheet" href="../../../shared/design/lumebook.css"><style>
@font-face{font-family:Heebo;src:url("../../../shared/brand/fonts/Heebo-Bold.ttf");font-weight:700}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font)}
main{max-width:1200px;margin:auto;padding:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:var(--sp-5)}
article{padding:var(--sp-4);border:1px solid var(--line);border-radius:var(--r-card,20px);background:var(--surface)}
article img{width:100%;height:auto;border-radius:12px;margin-top:16px}
.lb-row{display:flex;align-items:center;justify-content:space-between;gap:16px}
a{color:var(--tint)}h1{font-size:var(--fs-display)}h2{font-size:var(--fs-title)}p{line-height:1.6}
.notice{background:var(--surface-2);padding:var(--sp-4);border-radius:16px;margin:24px 0}
</style></head><body><main><h1>סדרת שאלות ותשובות</h1><p>שבעה סטוריז לפי סדר העלאה</p><p><a href="lumebook-qa-stories.zip" download>הורדת כל התמונות</a> · <a href="copy.txt">הטקסטים</a> · <a href="series.json">הפרומפטים</a></p><div class="notice"><strong>הערות להעלאה</strong><p>בסטורי האחרון הוסיפו מדבקת שאלות באינסטגרם<br>מקמו אותה בשטח הריק משמאל לדמות<br>ניסוח למדבקה: מה תרצו לדעת?</p><p>טיוטה לפי סגנון העברית המתועד<br>הסגנון עדיין לא מכויל לירין</p><p>התשובות נבדקו מול <a href="https://lumebook.com/IL/he">עמוד המוצר</a> בתאריך 14 באוקטובר 2026<br>הספרים והילדים בתמונות הם איורים להמחשה</p></div><div class="grid">'''+''.join(cards)+'''</div></main></body></html>'''
(root/"index.html").write_text(page)
with zipfile.ZipFile(root/"lumebook-qa-stories.zip","w",zipfile.ZIP_DEFLATED) as bundle:
    for item in mapping:
        name=item["id"]+".png"
        bundle.write(root/name,name)
    for name in ("copy.txt","README.md"):
        bundle.write(root/name,name)
print(json.dumps(report))
print("Packaged seven PNGs and copy")

