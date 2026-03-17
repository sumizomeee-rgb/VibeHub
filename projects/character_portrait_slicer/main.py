# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn", "python-multipart", "pillow"]
# ///

import os, io, base64, uuid, json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from PIL import Image, ImageDraw

app = FastAPI()
TOOL_NAME = os.environ.get("DISPLAY_NAME") or "角色立绘切图工具"
store: dict[str, bytes] = {}

SPECS = [
    {"key": "full", "label": "完整立绘", "w": 1140, "h": 1440},
    {"key": "wide", "label": "宽版头像", "w": 504, "h": 225},
    {"key": "stroke", "label": "描边特写", "w": 256, "h": 256, "inner": [146, 205], "border": 4},
    {"key": "mini", "label": "缩放特写", "w": 128, "h": 128, "sync": "stroke"},
]

def crop_region(img: Image.Image, x, y, w, h):
    iw, ih = img.size
    px, py, pw, ph = int(x*iw), int(y*ih), int(w*iw), int(h*ih)
    canvas = Image.new("RGBA", (pw, ph), (0,0,0,0))
    sx = max(0, px); sy = max(0, py)
    ex = min(iw, px+pw); ey = min(ih, py+ph)
    if ex > sx and ey > sy:
        region = img.crop((sx, sy, ex, ey))
        canvas.paste(region, (sx - px, sy - py))
    return canvas

def render_spec(img, spec, regions):
    k = spec["key"]
    rk = spec.get("sync", k)
    r = regions.get(rk, {"x":0.1,"y":0.05,"width":0.8,"height":0.9})
    cropped = crop_region(img, r["x"], r["y"], r["width"], r["height"])
    tw, th = spec["w"], spec["h"]
    if "inner" in spec:
        iw, ih = spec["inner"]
        bd = spec["border"]
        fitted = cropped.resize((iw, ih), Image.LANCZOS)
        canvas = Image.new("RGBA", (tw, th), (0,0,0,0))
        ox, oy = (tw - iw)//2, (th - ih)//2
        canvas.paste(fitted, (ox, oy))
        draw = ImageDraw.Draw(canvas)
        for i in range(bd):
            draw.rectangle([ox+i, oy+i, ox+iw-1-i, oy+ih-1-i], outline=(0,0,0,255))
        return canvas
    elif spec.get("sync"):
        stroke_spec = next(s for s in SPECS if s["key"] == spec["sync"])
        full = render_spec(img, stroke_spec, regions)
        return full.resize((tw, th), Image.LANCZOS)
    else:
        return cropped.resize((tw, th), Image.LANCZOS)

def img_to_b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    fid = str(uuid.uuid4())[:8]
    data = await file.read()
    store[fid] = data
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    w, h = img.size
    return {"id": fid, "name": file.filename, "width": w, "height": h}

@app.post("/api/preview")
async def preview(fid: str = Form(...), regions: str = Form(...)):
    if fid not in store: return JSONResponse({"error": "not found"}, 404)
    img = Image.open(io.BytesIO(store[fid])).convert("RGBA")
    rg = json.loads(regions)
    result = {}
    for spec in SPECS:
        out = render_spec(img, spec, rg)
        result[spec["key"]] = {"data": img_to_b64(out), "w": spec["w"], "h": spec["h"]}
    return result

@app.post("/api/export")
async def export_img(fid: str = Form(...), regions: str = Form(...), key: str = Form(...)):
    if fid not in store: return JSONResponse({"error": "not found"}, 404)
    img = Image.open(io.BytesIO(store[fid])).convert("RGBA")
    rg = json.loads(regions)
    spec = next(s for s in SPECS if s["key"] == key)
    out = render_spec(img, spec, rg)
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png",
                    headers={"Content-Disposition": f"attachment; filename={key}.png"})

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

HTML = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TOOL_NAME}}</title><style>
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
.specGrid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;max-width:1100px;margin:0 auto}
.spec-card{background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);padding:20px;display:flex;flex-direction:column}
.spec-card-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.spec-card-head h3{font-size:15px;color:#333}
.spec-card-head small{font-size:12px;color:#999}
.spec-preview{aspect-ratio:1;background-image:linear-gradient(45deg,#e0e0e0 25%,transparent 25%),linear-gradient(-45deg,#e0e0e0 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e0e0e0 75%),linear-gradient(-45deg,transparent 75%,#e0e0e0 75%);background-size:16px 16px;background-position:0 0,0 8px,8px -8px,-8px 0;border-radius:12px;display:flex;align-items:center;justify-content:center}
.spec-preview img{max-width:100%;max-height:100%;border-radius:8px}
.spec-actions{display:flex;gap:10px;margin-top:12px}
.spec-actions .btn{flex:1;font-size:13px}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.5);backdrop-filter:blur(4px);display:none;z-index:100;align-items:center;justify-content:center}
.modal-bg.show{display:flex}
.modal{background:#fff;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,.15);width:92vw;max-width:900px;max-height:90vh;display:flex;flex-direction:column;overflow:hidden}
.modal-header{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid #eee}
.modal-header h3{font-size:16px;color:#333}
.modal-body{display:flex;flex:1;overflow:hidden;min-height:0}
.edit-left{flex:2;position:relative;overflow:hidden;cursor:crosshair;background:#fafafa}
.edit-left canvas{width:100%;height:100%;object-fit:contain}
.edit-right{flex:1;padding:20px;overflow-y:auto;border-left:1px solid #eee;display:flex;flex-direction:column;align-items:center;gap:12px;background:#fcfcfc}
.edit-right img{max-width:100%;border:1px solid #eee;border-radius:10px}
.edit-right p{font-size:13px;color:#666}
.modal-footer{display:flex;justify-content:flex-end;gap:10px;padding:16px 20px;border-top:1px solid #eee}
input[type=file]{display:none}
@media(max-width:640px){.specGrid{grid-template-columns:1fr}}
</style></head><body>
<div class="header">
<h1>{{TOOL_NAME}}</h1>
<div class="actions">
<button class="btn btn-secondary" id="reBtn" style="display:none" onclick="reset()">更换素材</button>
</div></div>
<div class="upload-card">
<h2>上传图片</h2>
<div class="drop" id="dropZone" onclick="fi.click()">
<div id="ph">点击或拖拽图片到此处</div>
<img id="thumb" style="display:none"><input type="file" id="fi" accept="image/*">
</div>
</div>
<div id="specGrid" class="specGrid" style="display:none"></div>
<div class="modal-bg" id="modal">
<div class="modal">
<div class="modal-header"><h3 id="mTitle">编辑</h3><button class="btn btn-secondary" onclick="closeModal()">✕</button></div>
<div class="modal-body">
<div class="edit-left"><canvas id="eCanvas"></canvas></div>
<div class="edit-right"><p id="mInfo"></p><img id="mPreview"><p id="mSize"></p></div>
</div>
<div class="modal-footer">
<button class="btn btn-secondary" onclick="closeModal()">取消</button>
<button class="btn btn-primary" onclick="applyEdit()">应用</button>
</div>
</div></div>
<script>
const SPECS=[{key:'full',label:'完整立绘',w:1140,h:1440},{key:'wide',label:'宽版头像',w:504,h:225},{key:'stroke',label:'描边特写',w:256,h:256},{key:'mini',label:'缩放特写',w:128,h:128,sync:'stroke'}];
let fid='',fname='',imgW=0,imgH=0,regions={},previews={};
const defaults={full:{x:.05,y:.02,width:.9,height:.96},wide:{x:.15,y:.05,width:.7,height:.31},stroke:{x:.25,y:.05,width:.5,height:.35}};
const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);
const fi=$('#fi'),dropZone=$('#dropZone'),thumb=$('#thumb'),ph=$('#ph'),specGrid=$('#specGrid'),reBtn=$('#reBtn');
dropZone.onclick=()=>fi.click();
dropZone.ondragover=e=>{e.preventDefault();dropZone.classList.add('over')};
dropZone.ondragleave=()=>dropZone.classList.remove('over');
dropZone.ondrop=e=>{e.preventDefault();dropZone.classList.remove('over');if(e.dataTransfer.files[0])upload(e.dataTransfer.files[0])};
fi.onchange=()=>{if(fi.files[0])upload(fi.files[0])};
async function upload(file){
const fd=new FormData();fd.append('file',file);
const r=await fetch('api/upload',{method:'POST',body:fd});
const d=await r.json();fid=d.id;fname=file.name.replace(/\.[^.]+$/,'');imgW=d.width;imgH=d.height;
const reader=new FileReader();reader.onload=e=>{thumb.src=e.target.result;thumb.style.display='block';ph.style.display='none'};reader.readAsDataURL(file);
regions={};for(let s of SPECS)if(!s.sync)regions[s.key]={...defaults[s.key]};
dropZone.style.display='none';specGrid.style.display='grid';reBtn.style.display='flex';
await refreshAll();
}
function reset(){fid='';dropZone.style.display='';specGrid.style.display='none';reBtn.style.display='none';specGrid.innerHTML='';fi.value='';thumb.style.display='none';ph.style.display='block';regions={};previews={};
}
async function refreshAll(){
const fd=new FormData();fd.append('fid',fid);fd.append('regions',JSON.stringify(regions));
const r=await fetch('api/preview',{method:'POST',body:fd});previews=await r.json();renderCards();
}
function renderCards(){
specGrid.innerHTML='';for(let s of SPECS){
const p=previews[s.key];if(!p)continue;
const canEdit=!s.sync;
specGrid.innerHTML+=`<div class="spec-card"><div class="spec-card-head"><h3>${s.label}</h3><small>${s.w}×${s.h}</small></div>
<div class="spec-preview"><img src="data:image/png;base64,${p.data}"></div>
<div class="spec-actions">${canEdit?`<button class="btn btn-secondary" onclick="openEdit('${s.key}')">编辑</button>`:``}
<button class="btn btn-dl" onclick="dl('${s.key}')">导出 PNG</button></div></div>`;
}
}
function dl(key){
const fd=new FormData();fd.append('fid',fid);fd.append('regions',JSON.stringify(regions));fd.append('key',key);
fetch('api/export',{method:'POST',body:fd}).then(r=>r.blob()).then(b=>{
const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=`${fname}_${key}.png`;a.click();});
}
let editKey='',sel={},dragging=null,dragOff={};
function openEdit(key){
editKey=key;sel={...(regions[key]||defaults[key])};
$('#mTitle').textContent=SPECS.find(s=>s.key===key).label+' - 编辑选区';
$('#modal').classList.add('show');drawEditor();genPreview();
}
function closeModal(){$('#modal').classList.remove('show');}
function applyEdit(){regions[editKey]={...sel};closeModal();refreshAll();}
const eCanvas=$('#eCanvas'),ctx=eCanvas.getContext('2d');
let eImg=new Image(),eScale=1,eOx=0,eOy=0;
function drawEditor(){
eImg=new Image();eImg.onload=()=>{
const cont=eCanvas.parentElement,cw=cont.clientWidth,ch=cont.clientHeight;
eCanvas.width=cw;eCanvas.height=ch;
eScale=Math.min(cw/imgW,ch/imgH)*.9;eOx=(cw-imgW*eScale)/2;eOy=(ch-imgH*eScale)/2;
paint();
};eImg.src=`data:image/png;base64,${previews.full?.data||Object.values(previews)[0]?.data}`;
const fd=new FormData();fd.append('fid',fid);fd.append('regions',JSON.stringify({full:{x:0,y:0,width:1,height:1}}));
fetch('api/preview',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{
eImg=new Image();eImg.onload=()=>paint();eImg.src='data:image/png;base64,'+d.full.data;
});
}
function paint(){
const cw=eCanvas.width,ch=eCanvas.height;ctx.clearRect(0,0,cw,ch);
ctx.drawImage(eImg,eOx,eOy,imgW*eScale,imgH*eScale);
ctx.fillStyle='rgba(0,0,0,0.55)';ctx.fillRect(0,0,cw,ch);
const sx=eOx+sel.x*imgW*eScale,sy=eOy+sel.y*imgH*eScale,sw=sel.width*imgW*eScale,sh=sel.height*imgH*eScale;
ctx.save();ctx.beginPath();ctx.rect(sx,sy,sw,sh);ctx.clip();
ctx.drawImage(eImg,eOx,eOy,imgW*eScale,imgH*eScale);ctx.restore();
ctx.strokeStyle='#cba186';ctx.lineWidth=2;ctx.setLineDash([6,3]);ctx.strokeRect(sx,sy,sw,sh);ctx.setLineDash([]);
ctx.strokeStyle='rgba(203,161,134,0.25)';ctx.lineWidth=1;
for(let i=1;i<3;i++){ctx.beginPath();ctx.moveTo(sx+sw*i/3,sy);ctx.lineTo(sx+sw*i/3,sy+sh);ctx.stroke();ctx.beginPath();ctx.moveTo(sx,sy+sh*i/3);ctx.lineTo(sx+sw,sy+sh*i/3);ctx.stroke();}
ctx.fillStyle='#cba186';ctx.fillRect(sx+sw-6,sy+sh-6,12,12);
$('#mInfo').textContent=`选区: x=${(sel.x*100).toFixed(1)}% y=${(sel.y*100).toFixed(1)}% w=${(sel.width*100).toFixed(1)}% h=${(sel.height*100).toFixed(1)}%`;
}
eCanvas.onmousedown=e=>{
const r=eCanvas.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
const sx=eOx+sel.x*imgW*eScale,sy=eOy+sel.y*imgH*eScale,sw=sel.width*imgW*eScale,sh=sel.height*imgH*eScale;
if(Math.abs(mx-(sx+sw))<12&&Math.abs(my-(sy+sh))<12){dragging='resize';dragOff={x:mx,y:my,w:sel.width,h:sel.height};}
else if(mx>=sx&&mx<=sx+sw&&my>=sy&&my<=sy+sh){dragging='move';dragOff={x:mx-sx,y:my-sy};}
};
eCanvas.onmousemove=e=>{
if(!dragging)return;const r=eCanvas.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
if(dragging==='move'){sel.x=(mx-dragOff.x-eOx)/(imgW*eScale);sel.y=(my-dragOff.y-eOy)/(imgH*eScale);}
else{const spec=SPECS.find(s=>s.key===editKey),ratio=spec.w/spec.h;
let nw=dragOff.w+(mx-dragOff.x)/(imgW*eScale);nw=Math.max(.05,nw);sel.width=nw;sel.height=nw*(imgW/imgH)/ratio;}
paint();
};
eCanvas.onmouseup=()=>{if(dragging){dragging=null;genPreview();}};
async function genPreview(){
const fd=new FormData();fd.append('fid',fid);fd.append('regions',JSON.stringify({...regions,[editKey]:sel}));
const r=await fetch('api/preview',{method:'POST',body:fd});const d=await r.json();
const p=d[editKey];$('#mPreview').src='data:image/png;base64,'+p.data;
$('#mSize').textContent=`${p.w}×${p.h}px`;
}
</script></body></html>""".replace("{{TOOL_NAME}}", TOOL_NAME)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))