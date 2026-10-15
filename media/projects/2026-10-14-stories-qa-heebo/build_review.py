from pathlib import Path
import json, html, zipfile
root=Path(__file__).resolve().parent
data=json.loads((root/"series.json").read_text())
fonts=(root.parents[2]/"shared/brand/fonts")
black=(fonts/"Heebo-Black.ttf").as_uri()
bold=(fonts/"Heebo-Bold.ttf").as_uri()
css=f"""
@font-face{{font-family:Heebo;src:url('{black}');font-weight:900;font-display:block}}
@font-face{{font-family:Heebo;src:url('{bold}');font-weight:700;font-display:block}}
*{{box-sizing:border-box}}html,body{{margin:0;padding:0;background:#FBF7F0}}
.story{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#FBF7F0;direction:rtl;text-align:center;font-family:Heebo}}
.art{{position:absolute;inset:0;width:100%;height:100%;object-fit:fill}}
.story.new .art{{inset:auto;top:570px;left:194px;width:691px;height:1229px;mask-image:linear-gradient(to right,transparent,black 5%,black 95%,transparent)}}
.logo{{position:absolute;top:160px;left:100px;right:100px;color:#57B9C3;line-height:1.04}}
.wordmark{{font:900 100px/1.12 Heebo;direction:ltr;letter-spacing:-2px}}
.tagline{{font:700 43px/1.35 Heebo;direction:rtl}}
.label{{position:absolute;top:362px;left:0;right:0;font:700 42px/1.3 Heebo;color:white}}
.label span{{display:inline-block;padding:12px 36px;background:#5B2BD6;border-radius:45px}}
.question{{position:absolute;top:485px;left:90px;right:90px;height:242px;display:flex;align-items:center;justify-content:center;flex-direction:column;font:900 96px/1.17 Heebo;color:#5B2BD6}}
.answer{{position:absolute;top:772px;left:90px;right:90px;height:252px;display:flex;align-items:flex-start;justify-content:flex-start;flex-direction:column;align-items:center;font:700 52px/1.52 Heebo;color:#1D1039}}
.line{{display:block;white-space:nowrap}}
"""
sections=[]
for f in data["frames"]:
    question="".join('<span class="line">'+html.escape(line)+'</span>' for line in f["title"].splitlines())
    answer="".join('<span class="line">'+html.escape(line)+'</span>' for line in f["answer"].splitlines())
    sections.append('<section class="story'+(' new' if not f.get('edit') else '')+'" id="'+f["id"]+'"><img class="art" src="art/'+f["id"]+'.png" alt=""><div class="logo"><div class="wordmark">LumeBook</div><div class="tagline">הסיפור של הילד/ה שלך</div></div><div class="label"><span>שאלות ותשובות</span></div><div class="question">'+question+'</div><div class="answer">'+answer+'</div></section>')
(root/"stories.html").write_text('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>LumeBook Heebo Q&amp;A</title><style>'+css+'</style></head><body>'+"".join(sections)+'</body></html>')
(root/"copy.txt").write_text("\n\n".join(f["title"]+"\n"+f["answer"] for f in data["frames"])+"\n")
notes="""# LumeBook Q&A stories, Heebo revision
Created 14 October 2026
Ten actual question-and-answer stories, no cover counted as a question
No visible numbering on images, preview cards, filenames or copy
Logo wordmark and tagline rendered from actual local Heebo font files
All final stories are 1080 by 1920 PNGs
Built-in image_gen edits five earlier illustrations and creates five new illustrations
Editable native type layout: stories.html
All generation prompts and claim sources: series.json
Voice: documented fallback Hebrew, not yet calibrated to Yarin
Books and child faces are conceptual illustrations, not customer images or actual product-cover photography
No publishing was performed

## Product sources
Answers are checked against https://lumebook.com/IL/he, read on 14 October 2026
Each frame records its source section in series.json
No pricing, shipping time, age-range or developmental-effect claims appear
"""
(root/"README.md").write_text(notes)
cards=[]
for f in data["frames"]:
    cards.append('<article class="lb-card"><a href="'+f["id"]+'.png" download><img loading="lazy" src="'+f["id"]+'.png" alt="'+html.escape(f["title"].replace("\n"," "),quote=True)+'"></a><p>'+html.escape(f["title"]).replace("\n","<br>")+'</p><a href="'+f["id"]+'.png" download>הורדת התמונה</a></article>')
page='''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LumeBook Q&amp;A Heebo</title><link rel="stylesheet" href="../../../shared/design/lumebook.css"><style>
@font-face{font-family:Heebo;src:url("../../../shared/brand/fonts/Heebo-Bold.ttf");font-weight:700}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font)}
main{max-width:1200px;margin:auto;padding:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:var(--sp-5)}
article{padding:var(--sp-4);border:1px solid var(--line);border-radius:20px;background:var(--surface)}
article img{width:100%;height:auto;border-radius:12px}
a{color:var(--tint)}h1{font-size:var(--fs-display)}p{line-height:1.6}
.notice{padding:var(--sp-4);border-radius:16px;background:var(--surface-2);margin:24px 0}
</style></head><body><main><h1>שאלות ותשובות על הספר</h1><p>לוגו בפונט Heebo<br>שאלה ותשובה בכל סטורי</p><p><a href="lumebook-qa-heebo.zip" download>הורדת כל התמונות</a> · <a href="copy.txt">הטקסטים</a> · <a href="series.json">הפרומפטים</a></p><div class="notice"><p>טיוטה לפי סגנון העברית המתועד<br>הסגנון עדיין לא מכויל לירין</p><p>התשובות נבדקו מול <a href="https://lumebook.com/IL/he">עמוד המוצר</a> בתאריך 14 באוקטובר 2026<br>הספרים והילדים בתמונות הם איורים להמחשה</p></div><div class="grid">'''+''.join(cards)+'''</div></main></body></html>'''
(root/"index.html").write_text(page)
print("Editable Heebo story layouts and preview saved")
