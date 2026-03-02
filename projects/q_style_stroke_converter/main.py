# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn"]
# ///

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="头像切图工具")

HTML = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>头像切图工具</title>
<!-- JSZip CDN for batch zip export -->
<script src="https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#f0f2f5;min-height:100vh;padding:20px}
.header{display:flex;justify-content:space-between;align-items:center;max-width:1100px;margin:0 auto 20px;padding:16px 24px;background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.header h1{font-size:20px;color:#333}
.header .actions{display:flex;gap:10px}
.btn{padding:10px 18px;border:none;border-radius:10px;font-size:14px;cursor:pointer;transition:.2s;font-weight:600}
.btn-primary{background:#cba186;color:#fff}.btn-primary:hover:not(:disabled){background:#b8906f}
.btn-secondary{background:#eee;color:#333}.btn-secondary:hover:not(:disabled){background:#ddd}
.btn-dl{background:#000;color:#fff}.btn-dl:hover:not(:disabled){background:#333}
.btn:disabled{opacity:.4;cursor:not-allowed}
.upload-card{max-width:1100px;margin:0 auto 20px;background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);padding:24px}
.upload-card h2{font-size:18px;margin-bottom:16px;color:#333}
.drop{border:2px dashed #cba186;border-radius:12px;padding:40px 20px;text-align:center;cursor:pointer;transition:.2s;color:#999;position:relative;overflow:hidden}
.drop:hover,.drop.over{border-color:#000;background:#faf6ec}
.drop img{max-width:100%;max-height:180px;border-radius:8px;margin-top:8px}
.drop input{display:none}
.gen-row{max-width:1100px;margin:0 auto 20px;text-align:center}
#specGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;max-width:1100px;margin:0 auto}
.spec-card{background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);padding:20px;display:flex;flex-direction:column;align-items:center}
.spec-card h3{font-size:15px;color:#333;margin-bottom:12px;text-align:center}
.spec-preview{width:100%;aspect-ratio:1;border-radius:12px;display:flex;align-items:center;justify-content:center;position:relative;
background-image:linear-gradient(45deg,#e0e0e0 25%,transparent 25%),linear-gradient(-45deg,#e0e0e0 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e0e0e0 75%),linear-gradient(-45deg,transparent 75%,#e0e0e0 75%);
background-size:16px 16px;background-position:0 0,0 8px,8px -8px,-8px 0}
.spec-preview canvas{max-width:100%;max-height:100%;border-radius:8px}
.size-label{font-size:12px;color:#999;margin-top:8px}
.spec-card input[type=text]{width:100%;padding:8px 12px;border:1px solid #e0e0e0;border-radius:8px;font-size:13px;margin-top:10px;outline:none}
.spec-card input[type=text]:focus{border-color:#cba186}
.spec-card .exportBtn{width:100%;margin-top:10px}
.loader-sm{display:none;width:24px;height:24px;border:3px solid #eee;border-top-color:#cba186;border-radius:50%;animation:spin .6s linear infinite;position:absolute}
@keyframes spin{to{transform:rotate(360deg)}}
.err{color:#e74c3c;font-size:13px;margin-top:8px;display:none}
@media(max-width:900px){#specGrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){#specGrid{grid-template-columns:1fr}}
</style></head><body>
"""


HTML_BODY = """
<div class="header">
<h1>头像切图工具</h1>
<div class="actions">
<button class="btn btn-primary" id="batchExportBtn" disabled onclick="batchExport()">一键打包导出</button>
<button class="btn btn-secondary" id="changeImageBtn" onclick="fi.click()">更换图片</button>
</div></div>
<div class="upload-card">
<h2>上传图片</h2>
<div class="drop" id="drop" onclick="fi.click()">
<div id="ph">点击或拖拽图片到此处</div>
<img id="thumb" style="display:none"><input type="file" id="fi" accept="image/*">
</div>
<div class="err" id="err"></div>
</div>
<div class="gen-row">
<button class="btn btn-primary" id="generateBtn" disabled onclick="generateAll()">生成所有规格预览</button>
</div>
<div id="specGrid"></div>
"""

HTML_SCRIPT = r"""<script>
const SPECS=[
{id:'s140',title:'140\u00d7140 \u900f\u660e\u5e95\u5934\u50cf',w:140,h:140,circle:false,def:'avatar_140x140'},
{id:'s800',title:'800\u00d7800 \u900f\u660e\u5e95\u5934\u50cf',w:800,h:800,circle:false,def:'avatar_800x800'},
{id:'s256c',title:'ICONTOOLS 256\u00d7256 \u900f\u660e\u5e95',w:256,h:256,circle:true,def:'icon_256x256_circle'},
{id:'s128',title:'ICONTOOLS IP 128\u00d7128',w:128,h:128,circle:true,from256:true,def:'icon_128x128'},
{id:'s140c',title:'140\u00d7140 \u5706\u5f62\u900f\u660e\u5e95',w:140,h:140,circle:true,def:'avatar_140x140_circle'},
{id:'s256a',title:'256\u00d7256 \u900f\u660e\u5e95\uff08\u81ea\u9002\u5e94\uff09',w:256,h:256,circle:false,def:'avatar_256x256'}
];
let srcImg=null;const results={};
const grid=document.getElementById('specGrid');
SPECS.forEach(sp=>{const d=document.createElement('div');d.className='spec-card';
d.innerHTML='<h3>'+sp.title+'</h3><div class="spec-preview"><div class="loader-sm" id="loader_'+sp.id+'"></div><canvas id="cv_'+sp.id+'" style="display:none"></canvas></div><div class="size-label">'+sp.w+'\u00d7'+sp.h+'px</div><input type="text" id="name_'+sp.id+'" placeholder="\u8f93\u5165\u6587\u4ef6\u540d..."><button class="btn btn-dl exportBtn" data-id="'+sp.id+'" disabled onclick="exportOne(\''+sp.id+'\')">导出 PNG</button>';
grid.appendChild(d)});
const fi=document.getElementById('fi'),drop=document.getElementById('drop'),thumb=document.getElementById('thumb'),
ph=document.getElementById('ph'),genBtn=document.getElementById('generateBtn'),errEl=document.getElementById('err'),
batchBtn=document.getElementById('batchExportBtn');
function showErr(m){errEl.textContent=m;errEl.style.display='block';setTimeout(()=>errEl.style.display='none',3000)}
function loadFile(f){if(!f||!f.type.startsWith('image/')){showErr('\u8bf7\u9009\u62e9\u6709\u6548\u7684\u56fe\u7247\u6587\u4ef6');return}
const r=new FileReader();r.onload=e=>{const img=new Image();img.onload=()=>{srcImg=img;thumb.src=e.target.result;thumb.style.display='block';ph.style.display='none';genBtn.disabled=false;generateAll()};
img.onerror=()=>showErr('\u56fe\u7247\u52a0\u8f7d\u5931\u8d25');img.src=e.target.result};r.readAsDataURL(f)}
fi.onchange=()=>{if(fi.files[0])loadFile(fi.files[0])};
drop.ondragover=e=>{e.preventDefault();drop.classList.add('over')};
drop.ondragleave=()=>drop.classList.remove('over');
drop.ondrop=e=>{e.preventDefault();drop.classList.remove('over');if(e.dataTransfer.files[0])loadFile(e.dataTransfer.files[0])};

function applyTripleStroke({srcImage,outSize,isCircle}){
const S=outSize,c=document.createElement('canvas');c.width=S;c.height=S;
const ctx=c.getContext('2d'),sc=0.65,tw=S*sc,th=S*sc;
const iw=srcImage.width,ih=srcImage.height,ra=Math.min(tw/iw,th/ih);
const dw=iw*ra,dh=ih*ra,dx=(S-dw)/2,dy=(S-dh)/2;
const tc=document.createElement('canvas');tc.width=S;tc.height=S;
const tctx=tc.getContext('2d');tctx.drawImage(srcImage,dx,dy,dw,dh);
const id=tctx.getImageData(0,0,S,S),d=id.data;
for(let i=0;i<d.length;i+=4){if(d[i]>240&&d[i+1]>240&&d[i+2]>240)d[i+3]=0}
tctx.putImageData(id,0,0);
const alpha=new Uint8Array(S*S);
for(let i=0;i<alpha.length;i++)alpha[i]=d[i*4+3]>20?1:0;
function boxBlur(src,rad){
const tmp=new Float32Array(S*S),dst=new Float32Array(S*S),w=rad*2+1;
for(let y=0;y<S;y++){let s=0;for(let x=0;x<w&&x<S;x++)s+=src[y*S+x];
for(let x=0;x<S;x++){tmp[y*S+x]=s;const l=x-rad,r2=x+rad+1;if(r2<S)s+=src[y*S+r2];if(l>=0)s-=src[y*S+l]}}
for(let x=0;x<S;x++){let s=0;for(let y=0;y<w&&y<S;y++)s+=tmp[y*S+x];
for(let y=0;y<S;y++){dst[y*S+x]=s;const t=y-rad,b=y+rad+1;if(b<S)s+=tmp[b*S+x];if(t>=0)s-=tmp[t*S+x]}}
const out=new Uint8Array(S*S);for(let i=0;i<out.length;i++)out[i]=dst[i]>0?1:0;return out}
const sf=S/256;
const m1=boxBlur(alpha,Math.max(1,Math.round(10*sf)));
const m2=boxBlur(alpha,Math.max(1,Math.round(8*sf)));
const m3=boxBlur(alpha,Math.max(1,Math.round(2*sf)));
const od=ctx.createImageData(S,S),op=od.data;
for(let i=0;i<S*S;i++){let r=0,g=0,b=0,a=0;
if(m1[i]){r=203;g=161;b=134;a=255}
if(m2[i]){r=250;g=246;b=236;a=255}
if(m3[i]){r=0;g=0;b=0;a=255}
const sa=d[i*4+3];if(sa>20){const f=sa/255;r=d[i*4]*f+r*(1-f);g=d[i*4+1]*f+g*(1-f);b=d[i*4+2]*f+b*(1-f);a=255}
op[i*4]=r;op[i*4+1]=g;op[i*4+2]=b;op[i*4+3]=a}
ctx.putImageData(od,0,0);
if(isCircle){const tc2=document.createElement('canvas');tc2.width=S;tc2.height=S;
const t2=tc2.getContext('2d');t2.beginPath();t2.arc(S/2,S/2,S/2,0,Math.PI*2);t2.clip();t2.drawImage(c,0,0);
ctx.clearRect(0,0,S,S);ctx.drawImage(tc2,0,0)}
return c}

function generateAll(){if(!srcImg)return;genBtn.disabled=true;batchBtn.disabled=true;
SPECS.forEach(sp=>{document.getElementById('loader_'+sp.id).style.display='block';
document.getElementById('cv_'+sp.id).style.display='none';
document.querySelector('[data-id="'+sp.id+'"]').disabled=true});
setTimeout(()=>{let c256c=null;
SPECS.forEach(sp=>{try{let c;
if(sp.from256){if(!c256c)c256c=applyTripleStroke({srcImage:srcImg,outSize:256,isCircle:true});
c=document.createElement('canvas');c.width=128;c.height=128;
const x=c.getContext('2d');x.imageSmoothingEnabled=true;x.imageSmoothingQuality='high';x.drawImage(c256c,0,0,128,128)}
else{c=applyTripleStroke({srcImage:srcImg,outSize:sp.w,isCircle:sp.circle});if(sp.id==='s256c')c256c=c}
const cv=document.getElementById('cv_'+sp.id);cv.width=sp.w;cv.height=sp.h;
cv.getContext('2d').drawImage(c,0,0);cv.style.display='block';results[sp.id]=c;
document.querySelector('[data-id="'+sp.id+'"]').disabled=false}
catch(e){console.error(sp.id,e);showErr(sp.title+' \u5904\u7406\u5931\u8d25: '+e.message)}
document.getElementById('loader_'+sp.id).style.display='none'});
genBtn.disabled=false;batchBtn.disabled=false},50)}

function exportOne(id){const sp=SPECS.find(s=>s.id===id),c=results[id];if(!c)return;
const n=document.getElementById('name_'+id).value.trim()||sp.def;
const a=document.createElement('a');a.download=n+'.png';a.href=c.toDataURL('image/png');a.click()}

async function batchExport(){if(typeof JSZip==='undefined'){alert('JSZip \u672a\u52a0\u8f7d');return}
const zip=new JSZip();let has=false;
SPECS.forEach(sp=>{const c=results[sp.id];if(!c)return;
const n=(document.getElementById('name_'+sp.id).value.trim()||sp.def)+'.png';
zip.file(n,c.toDataURL('image/png').split(',')[1],{base64:true});has=true});
if(!has){alert('\u8bf7\u5148\u751f\u6210\u9884\u89c8');return}
batchBtn.disabled=true;batchBtn.textContent='\u6253\u5305\u4e2d...';
try{const b=await zip.generateAsync({type:'blob'});
const a=document.createElement('a');a.download='avatars.zip';a.href=URL.createObjectURL(b);a.click();URL.revokeObjectURL(a.href)}
catch(e){alert('\u6253\u5305\u5931\u8d25: '+e.message);console.error(e)}
batchBtn.disabled=false;batchBtn.textContent='\u4e00\u952e\u6253\u5305\u5bfc\u51fa'}
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML + HTML_BODY + HTML_SCRIPT


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
