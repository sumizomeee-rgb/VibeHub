# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn"]
# ///

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>头像切图工具</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui,-apple-system,sans-serif;background:#f0f2f5;padding:20px}
.container{max-width:1400px;margin:0 auto}.header{background:#fff;padding:24px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:20px;display:flex;justify-content:space-between;align-items:center}
h1{font-size:24px;color:#333}.btn-primary{background:#cba186;color:#fff;border:none;padding:12px 24px;border-radius:10px;cursor:pointer;font-size:14px}
.btn-primary:hover{background:#b8906f}.upload-card{background:#fff;padding:32px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:20px}
.drop-zone{border:2px dashed #cba186;border-radius:12px;padding:60px 20px;text-align:center;cursor:pointer;transition:all .3s}
.drop-zone:hover{border-color:#000;background:#fafafa}.drop-zone.active{border-color:#000;background:#f5f5f5}
.drop-zone input{display:none}.icon{margin-bottom:12px;display:flex;justify-content:center}.text{color:#666;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:20px}
.card{background:#fff;padding:20px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);position:relative}
.card h3{font-size:16px;margin-bottom:12px;color:#333}.preview{width:100%;aspect-ratio:1;background:repeating-conic-gradient(#e0e0e0 0 25%,#fff 0 50%) 0 0/20px 20px;border-radius:8px;margin-bottom:12px;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative}
.preview canvas{max-width:100%;max-height:100%;display:block;border:2px solid #cba186;border-radius:4px}.name-input{width:100%;padding:8px 32px 8px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;margin-bottom:12px}
.name-wrap{position:relative}.clear-btn{position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:none;color:#999;cursor:pointer;font-size:16px}
.btn-dl{background:#000;color:#fff;border:none;padding:8px 16px;border-radius:8px;cursor:pointer;font-size:13px;width:100%}
.btn-dl:hover{background:#333}.edit-btn{position:absolute;top:8px;right:8px;background:#cba186;color:#fff;border:none;padding:6px 12px;border-radius:6px;cursor:pointer;font-size:12px;z-index:10}
.edit-btn:hover{background:#b8906f}.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:1000;align-items:center;justify-content:center}
.modal.active{display:flex}.modal-content{background:#fff;border-radius:16px;padding:24px;max-width:90vw;max-height:90vh;display:flex;flex-direction:column;align-items:center}
.modal-canvas-wrap{position:relative;margin-bottom:16px}.modal-canvas-wrap canvas{display:block;max-width:80vw;max-height:60vh}
.modal-crop-box{position:absolute;outline:2px solid #cba186;cursor:move;box-shadow:0 0 0 9999px rgba(0,0,0,.3)}
.modal-resize{position:absolute;right:-6px;bottom:-6px;width:12px;height:12px;background:#cba186;border:2px solid #fff;border-radius:50%;cursor:nwse-resize}
.modal-btns{display:flex;gap:12px}.modal-btn{padding:10px 24px;border:none;border-radius:8px;cursor:pointer;font-size:14px}
.modal-confirm{background:#cba186;color:#fff}.modal-cancel{background:#666;color:#fff}
@media(max-width:768px){.grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:480px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>头像切图工具</h1>
<button class="btn-primary" id="exportAll" style="display:none">一键打包导出</button>
</div>
<div class="upload-card">
<div class="drop-zone" id="dropZone">
<div class="icon">
<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cba186" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
<polyline points="17 8 12 3 7 8"></polyline>
<line x1="12" y1="3" x2="12" y2="15"></line>
</svg>
</div>
<div class="text">点击或拖拽图片到此处上传</div>
<input type="file" id="fileInput" accept="image/*">
</div>
<div class="grid" id="grid" style="display:none"></div>
</div>
</div>
<div class="modal" id="modal">
<div class="modal-content">
<div class="modal-canvas-wrap">
<canvas id="modalCanvas"></canvas>
<div class="modal-crop-box" id="modalCropBox"><div class="modal-resize" id="modalResize"></div></div>
</div>
<div class="modal-btns">
<button class="modal-btn modal-confirm" id="modalConfirm">确认</button>
<button class="modal-btn modal-cancel" id="modalCancel">取消</button>
</div>
</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script>
const presets=[
{name:'透明底140px',size:140,type:'square',defaultName:'头像-140px'},
{name:'透明底256px',size:256,type:'square',defaultName:'头像-256px'},
{name:'透明底800px',size:800,type:'square',defaultName:'头像-800px'},
{name:'圆形头像128px',size:128,type:'circle',defaultName:'圆形头像-128px'},
{name:'圆形头像256px',size:256,type:'circle',defaultName:'圆形头像-256px'},
{name:'IconTools黑芯1024px',size:1024,type:'icon-black',defaultName:'IconTools-黑芯-1024px'},
{name:'IconTools白芯1024px',size:1024,type:'icon-white',defaultName:'IconTools-白芯-1024px'}
];
let img,cropData={x:0,y:0,size:100},scale=1,canvasData={w:0,h:0},modalScale=1;
let modalCtx,modalDrag=false,modalRes=false,modalStart={x:0,y:0},tempCrop={},initialCrop={};
const dropZone=document.getElementById('dropZone'),fileInput=document.getElementById('fileInput'),
grid=document.getElementById('grid'),exportAll=document.getElementById('exportAll'),
modal=document.getElementById('modal'),modalCanvas=document.getElementById('modalCanvas'),
modalCropBox=document.getElementById('modalCropBox'),modalResize=document.getElementById('modalResize'),
modalConfirm=document.getElementById('modalConfirm'),modalCancel=document.getElementById('modalCancel');

dropZone.onclick=()=>fileInput.click();
dropZone.ondragover=e=>{e.preventDefault();dropZone.classList.add('active')};
dropZone.ondragleave=()=>dropZone.classList.remove('active');
dropZone.ondrop=e=>{e.preventDefault();dropZone.classList.remove('active');if(e.dataTransfer.files[0])loadImage(e.dataTransfer.files[0])};
fileInput.onchange=e=>{if(e.target.files[0])loadImage(e.target.files[0])};

function loadImage(file){
    const reader=new FileReader();
    reader.onload=e=>{
        img=new Image();
        img.onload=()=>{
            const maxW=800,maxH=600;
            let w=img.width,h=img.height;
            if(w>maxW||h>maxH){const r=Math.min(maxW/w,maxH/h);w*=r;h*=r}
            w=Math.round(w);
            h=Math.round(h);
            canvasData={w,h};
            scale=w/img.width;
            const minSize=Math.min(w,h)*0.6;
            cropData={x:(w-minSize)/2,y:(h-minSize)/2,size:minSize};
            grid.style.display='grid';
            exportAll.style.display='block';
            renderPreviews();
        };
        img.src=e.target.result;
    };
    reader.readAsDataURL(file);
}

function renderPreviews(){
    grid.innerHTML='';
    presets.forEach(p=>{
        const card=document.createElement('div');
        card.className='card';
        card.innerHTML=`<h3>${p.name}</h3><div class="preview">
        <button class="edit-btn">编辑区域</button>
        <canvas></canvas>
        </div><div class="name-wrap"><input class="name-input" placeholder="${p.defaultName}" data-default="${p.defaultName}">
        <button class="clear-btn">✕</button></div><button class="btn-dl">下载</button>`;
        const cv=card.querySelector('canvas'),c=cv.getContext('2d');
        cv.width=p.size;cv.height=p.size;
        drawPreview(c,p);
        card.querySelector('.edit-btn').onclick=()=>openModal();
        card.querySelector('.clear-btn').onclick=()=>card.querySelector('.name-input').value='';
        card.querySelector('.btn-dl').onclick=()=>{
            const name=card.querySelector('.name-input').value.trim()||card.querySelector('.name-input').dataset.default;
            cv.toBlob(b=>{const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=name+'.png';a.click()});
        };
        grid.appendChild(card);
    });
}

function drawPreview(ctx,preset){
    ctx.clearRect(0,0,preset.size,preset.size);
    const sx=cropData.x/scale,sy=cropData.y/scale,ss=cropData.size/scale;
    if(preset.type==='circle'||preset.type.startsWith('icon')){
        if(preset.type.startsWith('icon')){
            ctx.fillStyle=preset.type==='icon-black'?'#000':'#fff';
            ctx.beginPath();
            ctx.arc(preset.size/2,preset.size/2,preset.size/2,0,Math.PI*2);
            ctx.fill();
        }
        ctx.save();
        ctx.beginPath();
        ctx.arc(preset.size/2,preset.size/2,preset.size/2,0,Math.PI*2);
        ctx.clip();
        ctx.drawImage(img,sx,sy,ss,ss,0,0,preset.size,preset.size);
        ctx.restore();
    }else{
        ctx.drawImage(img,sx,sy,ss,ss,0,0,preset.size,preset.size);
    }
}

function openModal(){
    modalCanvas.width=canvasData.w;
    modalCanvas.height=canvasData.h;
    modalCtx=modalCanvas.getContext('2d');
    modalCtx.drawImage(img,0,0,img.width,img.height,0,0,canvasData.w,canvasData.h);
    modal.classList.add('active');
    setTimeout(()=>{
        modalScale=modalCanvas.clientWidth/modalCanvas.width;
        tempCrop={x:cropData.x,y:cropData.y,size:cropData.size};
        modalCropBox.style.left=(tempCrop.x*modalScale)+'px';
        modalCropBox.style.top=(tempCrop.y*modalScale)+'px';
        modalCropBox.style.width=(tempCrop.size*modalScale)+'px';
        modalCropBox.style.height=(tempCrop.size*modalScale)+'px';
    },0);
}

modalCropBox.onmousedown=e=>{
    if(e.target===modalResize){modalRes=true}else{modalDrag=true}
    modalStart={x:e.clientX,y:e.clientY};
    initialCrop={x:tempCrop.x, y:tempCrop.y, size:tempCrop.size};
    e.stopPropagation();e.preventDefault();
};

modal.onmousemove=e=>{
    if(!modalDrag&&!modalRes)return;
    const dx=(e.clientX-modalStart.x)/modalScale, dy=(e.clientY-modalStart.y)/modalScale;
    
    if(modalDrag){
        tempCrop.x=Math.max(0,Math.min(canvasData.w-initialCrop.size,initialCrop.x+dx));
        tempCrop.y=Math.max(0,Math.min(canvasData.h-initialCrop.size,initialCrop.y+dy));
    }else if(modalRes){
        const delta=Math.max(dx,dy);
        tempCrop.size=Math.max(30,Math.min(canvasData.w-initialCrop.x,canvasData.h-initialCrop.y,initialCrop.size+delta));
    }
    
    modalCropBox.style.left=(tempCrop.x*modalScale)+'px';
    modalCropBox.style.top=(tempCrop.y*modalScale)+'px';
    modalCropBox.style.width=(tempCrop.size*modalScale)+'px';
    modalCropBox.style.height=(tempCrop.size*modalScale)+'px';
};

modal.onmouseup=()=>{modalDrag=false;modalRes=false};

modalConfirm.onclick=()=>{
    cropData={x:tempCrop.x,y:tempCrop.y,size:tempCrop.size};
    modal.classList.remove('active');
    renderPreviews();
};
modalCancel.onclick=()=>modal.classList.remove('active');

exportAll.onclick=async()=>{
    const zip=new JSZip();
    const cards=grid.querySelectorAll('.card');
    for(let i=0;i<cards.length;i++){
        const card=cards[i];
        const cv=card.querySelector('canvas');
        const name=card.querySelector('.name-input').value.trim()||card.querySelector('.name-input').dataset.default;
        const blob=await new Promise(r=>cv.toBlob(r));
        zip.file(name+'.png',blob);
    }
    const content=await zip.generateAsync({type:'blob'});
    const a=document.createElement('a');
    a.href=URL.createObjectURL(content);
    a.download='头像切图-'+Date.now()+'.zip';
    a.click();
};
</script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))