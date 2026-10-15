const fs = require('fs');
const path = require('path');
const {pathToFileURL} = require('url');
const {chromium} = require('/Users/yarinbruner/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
const root=__dirname;
const data=JSON.parse(fs.readFileSync(path.join(root,'series.json'),'utf8'));
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files']});
try{
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await page.goto(pathToFileURL(path.join(root,'stories.html')).href);
await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(im=>im.decode()));});
const report=[];
for(const f of data.frames.filter(f=>!process.argv.includes('--new-only')||!f.edit)){
await page.evaluate(id=>{
document.querySelectorAll('.story').forEach(s=>s.style.display=s.id===id?'block':'none');
window.scrollTo(0,0);
const section=document.getElementById(id);
for(const name of ['question','answer']){
const parent=section.querySelector('.'+name);
let size=parseFloat(getComputedStyle(parent).fontSize);
while([...parent.querySelectorAll('.line')].some(l=>l.scrollWidth>parent.clientWidth)&&size>40){
size-=2;parent.style.fontSize=size+'px';
}
}
},f.id);
await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const check=await page.evaluate(id=>{
const s=document.getElementById(id);
return {id,width:s.clientWidth,height:s.clientHeight,logoFont:getComputedStyle(s.querySelector('.wordmark')).fontFamily,heeboLoaded:document.fonts.check('900 100px Heebo'),direction:getComputedStyle(s).direction,numbering:!!s.querySelector('.ordinal'),overflow:[...s.querySelectorAll('.line')].some(l=>l.scrollWidth>l.parentElement.clientWidth),copy:[...s.querySelectorAll('.question .line,.answer .line')].map(l=>l.textContent).join('\n')};
},f.id);
if(check.overflow||check.numbering||!check.heeboLoaded||check.direction!=='rtl')throw Error('Layout check failed: '+f.id);
if(check.copy!==f.title+'\n'+f.answer)throw Error('Text mismatch: '+f.id);
await page.locator('#'+f.id).screenshot({path:path.join(root,f.id+'.png')});
report.push(check);
}
const reportPath=path.join(root,'render-report.json');
const prior=process.argv.includes('--new-only')&&fs.existsSync(reportPath)?JSON.parse(fs.readFileSync(reportPath,'utf8')).filter(r=>!report.some(n=>n.id===r.id)):[];
fs.writeFileSync(reportPath,JSON.stringify([...prior,...report],null,2));
console.log('Rendered '+report.length+' stories; Heebo, RTL, text and overflow checks passed');
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
