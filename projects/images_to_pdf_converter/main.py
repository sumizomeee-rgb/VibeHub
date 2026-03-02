# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn", "pillow", "python-multipart"]
# ///

import os
import io
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from PIL import Image

app = FastAPI()

pdf_store: dict[str, bytes] = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

HTML = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>图片转 PDF</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#f0f2f5;min-height:100vh;padding:20px}
.header{display:flex;justify-content:space-between;align-items:center;max-width:1100px;margin:0 auto 20px;padding:16px 24px;background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.header h1{font-size:20px;color:#333}
.upload-card{max-width:1100px;margin:0 auto 20px;background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);padding:24px}
.upload-card h2{font-size:18px;margin-bottom:16px;color:#333}
.drop{border:2px dashed #cba186;border-radius:12px;padding:40px 20px;text-align:center;cursor:pointer;transition:.2s;color:#999;position:relative;overflow:hidden}
.drop:hover,.drop.over{border-color:#000;background:#faf6ec}
.drop input{display:none}
.preview-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:12px;margin-top:20px}
.preview-item{position:relative;aspect-ratio:1;border-radius:10px;overflow:hidden;border:1px solid #eee;background:#fafafa}
.preview-item img{width:100%;height:100%;object-fit:cover}
.preview-item .remove{position:absolute;top:4px;right:4px;background:rgba(0,0,0,.6);color:#fff;border:none;border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:14px;line-height:22px;text-align:center}
.preview-item .idx{position:absolute;bottom:0;left:0;right:0;background:rgba(203,161,134,.9);color:#fff;font-size:11px;text-align:center;padding:2px 0}
.actions-row{max-width:1100px;margin:0 auto 20px;display:flex;gap:12px;justify-content:center}
.btn{padding:12px 24px;border:none;border-radius:10px;font-size:15px;cursor:pointer;transition:.2s;font-weight:600}
.btn-primary{background:#cba186;color:#fff}.btn-primary:hover:not(:disabled){background:#b8906f}
.btn-success{background:#10b981;color:#fff}.btn-success:hover:not(:disabled){background:#059669}
.btn:disabled{opacity:.4;cursor:not-allowed}
.status{max-width:1100px;margin:0 auto;text-align:center;color:#666;font-size:14px;min-height:24px}
.progress-bar{height:4px;background:#e5e5e5;border-radius:2px;margin-top:10px;overflow:hidden;display:none}
.progress-bar .fill{height:100%;background:#cba186;width:0;transition:width .3s}
</style></head><body>
<div class="header">
<h1>图片转 PDF</h1>
</div>
<div class="upload-card">
<h2>上传图片</h2>
<div class="drop" id="dropZone" onclick="fi.click()">
<div id="ph">点击或拖拽图片到此处</div><input type="file" id="fi" accept="image/*" multiple>
</div>
<div class="preview-grid" id="previewGrid"></div>
</div>
<div class="actions-row">
<button class="btn btn-primary" id="convertBtn" disabled onclick="convert()">生成 PDF</button>
<button class="btn btn-success" id="downloadBtn" disabled style="display:none" onclick="download()">下载 PDF</button>
</div>
<div class="progress-bar" id="progressBar"><div class="fill" id="progressFill"></div></div>
<div class="status" id="status"></div>
<script>
const fi=$('#fi'),dropZone=$('#dropZone'),previewGrid=$('#previewGrid'),convertBtn=$('#convertBtn'),downloadBtn=$('#downloadBtn'),statusEl=$('#status'),progressBar=$('#progressBar'),progressFill=$('#progressFill');
function $(s){return document.querySelector(s)}
let files=[],pdfId=null;
dropZone.onclick=()=>fi.click();
dropZone.ondragover=e=>{e.preventDefault();dropZone.classList.add('over')};
dropZone.ondragleave=()=>dropZone.classList.remove('over');
dropZone.ondrop=e=>{e.preventDefault();dropZone.classList.remove('over');addFiles(e.dataTransfer.files)};
fi.onchange=()=>{addFiles(fi.files);fi.value=''};
function addFiles(newFiles){for(const f of newFiles){if(f.type.startsWith('image/'))files.push(f)}renderPreviews();pdfId=null;downloadBtn.style.display='none';statusEl.textContent=''}
function renderPreviews(){previewGrid.innerHTML='';files.forEach((f,i)=>{
const d=document.createElement('div');d.className='preview-item';
const img=document.createElement('img');img.src=URL.createObjectURL(f);
const rm=document.createElement('button');rm.className='remove';rm.textContent='×';
rm.onclick=()=>{files.splice(i,1);renderPreviews();pdfId=null;downloadBtn.style.display='none'};
const idx=document.createElement('div');idx.className='idx';idx.textContent=i+1;
d.append(img,rm,idx);previewGrid.append(d)});
convertBtn.disabled=files.length===0}
async function convert(){if(!files.length)return;convertBtn.disabled=true;statusEl.textContent='正在生成 PDF…';
progressBar.style.display='block';progressFill.style.width='30%';
const fd=new FormData();files.forEach(f=>fd.append('images',f));
try{const res=await fetch('api/convert',{method:'POST',body:fd});
progressFill.style.width='90%';if(!res.ok){const e=await res.json();throw new Error(e.detail||'转换失败')}
const data=await res.json();pdfId=data.id;progressFill.style.width='100%';
statusEl.textContent='✓ PDF 生成成功！';downloadBtn.style.display='inline-block';downloadBtn.disabled=false}
catch(e){statusEl.textContent='✗ '+e.message}
finally{convertBtn.disabled=false;setTimeout(()=>{progressBar.style.display='none';progressFill.style.width='0'},800)}}
function download(){if(!pdfId)return;const a=document.createElement('a');a.href='api/download/'+pdfId;a.download='images.pdf';document.body.append(a);a.click();a.remove()}
</script></body></html>"""


@app.post("/api/convert")
async def convert(images: list[UploadFile] = File(...)):
    pil_images: list[Image.Image] = []
    for img_file in images:
        data = await img_file.read()
        img = Image.open(io.BytesIO(data)).convert("RGB")
        pil_images.append(img)

    if not pil_images:
        raise HTTPException(400, detail="没有有效的图片")

    buf = io.BytesIO()
    if len(pil_images) == 1:
        pil_images[0].save(buf, format="PDF")
    else:
        pil_images[0].save(buf, format="PDF", save_all=True, append_images=pil_images[1:])
    buf.seek(0)

    file_id = uuid.uuid4().hex[:12]
    pdf_store[file_id] = buf.getvalue()
    return {"id": file_id}


@app.get("/api/download/{file_id}")
async def download(file_id: str):
    if file_id not in pdf_store:
        raise HTTPException(404, detail="文件不存在或已过期")
    return StreamingResponse(
        io.BytesIO(pdf_store[file_id]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=images.pdf"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))