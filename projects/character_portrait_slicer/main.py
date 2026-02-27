# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn", "python-multipart", "pillow"]
# ///

import os, io, base64, uuid, json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from PIL import Image, ImageDraw

app = FastAPI()
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

HTML = r"""<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>角色立绘切图工具 v3.7</title><style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f172a;--card:#1e293b;--border:#334155;--text:#e2e8f0;--dim:#94a3b8;--blue:#2563eb;--blue-h:#3b82f6;--radius:1.2rem}
body{background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;min-height:100vh}
header{display:flex;justify-content:space-between;align-items:center;padding:1rem 1.5rem;border-bottom:1px solid var(--border)}
.logo{font-size:1.4rem;font-weight:800;font-style:italic;background:linear-gradient(135deg,var(--blue),#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo span{font-size:.75rem;font-weight:400;color:var(--dim);-webkit-text-fill-color:var(--dim);margin-left:.5rem}
.btn{padding:.45rem 1rem;border-radius:.6rem;border:1px solid var(--border);background:var(--card);color:var(--text);cursor:pointer;font-size:.8rem;transition:.2s}
.btn:hover{border-color:var(--blue);color:var(--blue-h)}
.btn-p{background:var(--blue);border-color:var(--blue);color:#fff}.btn-p:hover{background:var(--blue-h)}
.drop{display:flex;flex-direction:column;align-items:center;justify-content:center;border:2px dashed var(--border);border-radius:var(--radius);padding:3rem;margin:1.5rem;cursor:pointer;transition:.2s;min-height:50vh}
.drop:hover,.drop.over{border-color:var(--blue);background:rgba(37,99,235,.06)}
.drop h2{font-size:1.1rem;margin-bottom:.5rem}.drop p{color:var(--dim);font-size:.85rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;padding:1.5rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}
.card-head{display:flex;justify-content:space-between;align-items:center;padding:.75rem 1rem;border-bottom:1px solid var(--border)}
.card-head h3{font-size:.85rem}.card-head small{color:var(--dim);font-size:.7rem}
.card-preview{flex:1;display:flex;align-items:center;justify-content:center;padding:1rem;min-height:160px;
  background-image:linear-gradient(45deg,#1a2332 25%,transparent 25%),linear-gradient(-45deg,#1a2332 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#1a2332 75%),linear-gradient(-45deg,transparent 75%,#1a2332 75%);
  background-size:16px 16px;background-position:0 0,0 8px,8px -8px,-8px 0}
.card-preview img{max-width:100%;max-height:200px;object-fit:contain}
.card-actions{display:flex;gap:.5rem;padding:.75rem 1rem;border-top:1px solid var(--border)}
.card-actions .btn{flex:1;text-align:center;font-size:.75rem}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(8px);display:none;z-index:100;align-items:center;justify-content:center}
.modal-bg.show{display:flex}
.modal{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);width:92vw;max-width:900px;max-height:90vh;display:flex;flex-direction:column;overflow:hidden}
.modal-header{display:flex;justify-content:space-between;align-items:center;padding:.8rem 1.2rem;border-bottom:1px solid var(--border)}
.modal-body{display:flex;flex:1;overflow:hidden;min-height:0}
.edit-left{flex:2;position:relative;overflow:hidden;cursor:crosshair;background:#0a0f1a}
.edit-left canvas{width:100%;height:100%;object-fit:contain}
.edit-right{flex:1;padding:1rem;overflow-y:auto;border-left:1px solid var(--border);display:flex;flex-direction:column;align-items:center;gap:.5rem}
.edit-right img{max-width:100%;border:1px solid var(--border);border-radius:.5rem}
.edit-right p{font-size:.75rem;color:var(--dim)}
.modal-footer{display:flex;justify-content:flex-end;gap:.5rem;padding:.8rem 1.2rem;border-top:1px solid var(--border)}
input[type=file]{display:none}
</style></head><body>
<header><div class="logo">CutPro<span>v3.7</span></div><button class="btn" id="reBtn" style="display:none" onclick="reset()">更换素材</button></header>
<div id="dropZone" class="drop"><h2>拖拽或点击上传角色立绘</h2><p>支持 PNG / JPG / WebP</p></div>
<input type="file" id="fileIn" accept="image/*">
<div id="cards" class="grid" style="display:none"></div>
<div class="modal-bg" id="modal"><div class="modal"><div class="modal-header"><h3 id="mTitle">编辑</h3><button class="btn" onclick="closeModal()">✕</button></div>
<div class="modal-body"><div class="edit-left"><canvas id="eCanvas"></canvas></div>
<div class="edit-right"><p id="mInfo"></p><img id="mPreview"><p id="mSize"></p></div></div>
<div class="modal-footer"><button class="btn" onclick="closeModal()">取消</button><button class="btn btn-p" onclick="applyEdit()">应用</button></div></div></div>
<script>
const SPECS=[{key:"full",label:"完整立绘",w:1140,h:1440},{key:"wide",label:"宽版头像",w:504,h:225},
{key:"stroke",label:"描边特写",w:256,h:256},{key:"mini",label:"缩放特写",w:128,h:128,sync:"stroke"}];
let fid="",fname="",imgW=0,imgH=0,regions={},previews={};
const defaults={full:{x:.05,y:.02,width:.9,height:.96},wide:{x:.15,y:.05,width:.7,height:.31},stroke:{x:.25,y:.05,width:.5,height:.35}};
const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);
const dropZone=$('#dropZone'),fileIn=$('#fileIn'),cardsEl=$('#cards');
dropZone.onclick=()=>fileIn.click();
dropZone.ondragover=e=>{e.preventDefault();dropZone.classList.add('over')};
dropZone.ondragleave=()=>dropZone.classList.remove('over');
dropZone.ondrop=e=>{e.preventDefault();dropZone.classList.remove('over');if(e.dataTransfer.files[0])upload(e.dataTransfer.files[0])};
fileIn.onchange=()=>{if(fileIn.files[0])upload(fileIn.files[0])};
async function upload(file){
  const fd=new FormData();fd.append('file',file);
  const r=await fetch('api/upload',{method:'POST',body:fd});
  const d=await r.json();fid=d.id;fname=file.name.replace(/\.[^.]+$/,'');imgW=d.width;imgH=d.height;
  regions={};for(let s of SPECS)if(!s.sync)regions[s.key]={...defaults[s.key]};
  dropZone.style.display='none';cardsEl.style.display='grid';$('#reBtn').style.display='';
  await refreshAll();
}
function reset(){fid="";dropZone.style.display='';cardsEl.style.display='none';$('#reBtn').style.display='none';cardsEl.innerHTML='';fileIn.value='';}
async function refreshAll(){
  const fd=new FormData();fd.append('fid',fid);fd.append('regions',JSON.stringify(regions));
  const r=await fetch('api/preview',{method:'POST',body:fd});previews=await r.json();renderCards();
}
function renderCards(){
  cardsEl.innerHTML='';for(let s of SPECS){
    const p=previews[s.key];if(!p)continue;
    const canEdit=!s.sync;
    cardsEl.innerHTML+=`<div class="card"><div class="card-head"><h3>${s.label}</h3><small>${s.w}×${s.h}</small></div>
    <div class="card-preview"><img src="data:image/png;base64,${p.data}"></div>
    <div class="card-actions">${canEdit?`<button class="btn" onclick="openEdit('${s.key}')">编辑</button>`:``}
    <button class="btn btn-p" onclick="dl('${s.key}')">导出 PNG</button></div></div>`;
  }
}
function dl(key){
  const fd=new FormData();fd.append('fid',fid);fd.append('regions',JSON.stringify(regions));fd.append('key',key);
  fetch('api/export',{method:'POST',body:fd}).then(r=>r.blob()).then(b=>{
    const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=`${fname}_${key}.png`;a.click();});
}
let editKey="",sel={},dragging=null,dragOff={};
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
  // reload original via preview hack - just use upload data
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
  ctx.strokeStyle='#3b82f6';ctx.lineWidth=2;ctx.setLineDash([6,3]);ctx.strokeRect(sx,sy,sw,sh);ctx.setLineDash([]);// grid lines
  ctx.strokeStyle='rgba(148,163,184,0.25)';ctx.lineWidth=1;
  for(let i=1;i<3;i++){ctx.beginPath();ctx.moveTo(sx+sw*i/3,sy);ctx.lineTo(sx+sw*i/3,sy+sh);ctx.stroke();ctx.beginPath();ctx.moveTo(sx,sy+sh*i/3);ctx.lineTo(sx+sw,sy+sh*i/3);ctx.stroke();}
  // handle
  ctx.fillStyle='#3b82f6';ctx.fillRect(sx+sw-6,sy+sh-6,12,12);
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
</script></body></html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))