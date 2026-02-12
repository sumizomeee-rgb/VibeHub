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
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>图片转 PDF</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f0f2f5;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.container{background:#fff;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.08);padding:40px;max-width:640px;width:100%}
h1{font-size:1.6rem;color:#1a1a2e;margin-bottom:8px;text-align:center}
.subtitle{color:#888;text-align:center;margin-bottom:28px;font-size:.9rem}
.drop-zone{border:2px dashed #c5c5d2;border-radius:12px;padding:40px 20px;text-align:center;cursor:pointer;transition:all .2s;background:#fafafe;margin-bottom:20px}
.drop-zone:hover,.drop-zone.dragover{border-color:#6c63ff;background:#f5f4ff}
.drop-zone p{color:#666;font-size:.95rem;pointer-events:none}
.drop-zone .icon{font-size:2.4rem;margin-bottom:8px;pointer-events:none}
input[type=file]{display:none}
.preview-area{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;min-height:0}
.preview-item{position:relative;width:90px;height:90px;border-radius:8px;overflow:hidden;border:1px solid #e0e0e0}
.preview-item img{width:100%;height:100%;object-fit:cover}
.preview-item .remove{position:absolute;top:2px;right:2px;background:rgba(0,0,0,.55);color:#fff;border:none;border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:14px;line-height:22px;text-align:center}
.preview-item .idx{position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,.45);color:#fff;font-size:11px;text-align:center;padding:1px 0}
.actions{display:flex;gap:12px;flex-wrap:wrap}
.btn{flex:1;padding:12px 20px;border:none;border-radius:10px;font-size:.95rem;cursor:pointer;font-weight:600;transition:all .15s;min-width:140px;text-align:center}
.btn-primary{background:#6c63ff;color:#fff}.btn-primary:hover{background:#5a52d5}
.btn-success{background:#10b981;color:#fff}.btn-success:hover{background:#059669}
.btn:disabled{opacity:.45;cursor:not-allowed}
.status{margin-top:16px;text-align:center;color:#555;font-size:.9rem;min-height:24px}
.progress-bar{height:4px;background:#e5e5e5;border-radius:2px;margin-top:10px;overflow:hidden;display:none}
.progress-bar .fill{height:100%;background:#6c63ff;width:0;transition:width .3s}
</style>
</head>
<body>
<div class="container">
  <h1>📄 图片转 PDF</h1>
  <p class="subtitle">上传多张图片，一键合并为 PDF 文件</p>
  <div class="drop-zone" id="dropZone">
    <div class="icon">🖼️</div>
    <p>点击或拖拽图片到此处上传<br><small>支持 JPG / PNG / BMP / WEBP</small></p>
  </div>
  <input type="file" id="fileInput" multiple accept="image/*">
  <div class="preview-area" id="previewArea"></div>
  <div class="actions">
    <button class="btn btn-primary" id="convertBtn" disabled>生成 PDF</button>
    <button class="btn btn-success" id="downloadBtn" disabled style="display:none">下载 PDF</button>
  </div>
  <div class="progress-bar" id="progressBar"><div class="fill" id="progressFill"></div></div>
  <div class="status" id="status"></div>
</div>
<script>
const dropZone=document.getElementById("dropZone"),fileInput=document.getElementById("fileInput"),previewArea=document.getElementById("previewArea"),convertBtn=document.getElementById("convertBtn"),downloadBtn=document.getElementById("downloadBtn"),statusEl=document.getElementById("status"),progressBar=document.getElementById("progressBar"),progressFill=document.getElementById("progressFill");
let files=[], pdfId=null;

dropZone.addEventListener("click",()=>fileInput.click());
dropZone.addEventListener("dragover",e=>{e.preventDefault();dropZone.classList.add("dragover")});
dropZone.addEventListener("dragleave",()=>dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop",e=>{e.preventDefault();dropZone.classList.remove("dragover");addFiles(e.dataTransfer.files)});
fileInput.addEventListener("change",e=>{addFiles(e.target.files);fileInput.value=""});

function addFiles(newFiles){
  for(const f of newFiles){if(f.type.startsWith("image/"))files.push(f)}
  renderPreviews();pdfId=null;downloadBtn.style.display="none";statusEl.textContent=""
}

function renderPreviews(){
  previewArea.innerHTML="";
  files.forEach((f,i)=>{
    const div=document.createElement("div");div.className="preview-item";
    const img=document.createElement("img");img.src=URL.createObjectURL(f);
    const rm=document.createElement("button");rm.className="remove";rm.textContent="\\u00d7";
    rm.onclick=()=>{files.splice(i,1);renderPreviews();pdfId=null;downloadBtn.style.display="none"};
    const idx=document.createElement("div");idx.className="idx";idx.textContent=i+1;
    div.append(img,rm,idx);previewArea.append(div)
  });
  convertBtn.disabled=files.length===0
}

convertBtn.addEventListener("click",async()=>{
  if(!files.length)return;
  convertBtn.disabled=true;statusEl.textContent="正在生成 PDF…";
  progressBar.style.display="block";progressFill.style.width="30%";
  const fd=new FormData();
  files.forEach(f=>fd.append("images",f));
  try{
    const res=await fetch("api/convert",{method:"POST",body:fd});
    progressFill.style.width="90%";
    if(!res.ok){const e=await res.json();throw new Error(e.detail||"转换失败")}
    const data=await res.json();pdfId=data.id;
    progressFill.style.width="100%";
    statusEl.textContent="\\u2705 PDF 生成成功！";
    downloadBtn.style.display="inline-block";downloadBtn.disabled=false
  }catch(e){statusEl.textContent="\\u274c "+e.message}
  finally{convertBtn.disabled=false;setTimeout(()=>{progressBar.style.display="none";progressFill.style.width="0"},800)}
});

downloadBtn.addEventListener("click",()=>{
  if(!pdfId)return;
  const a=document.createElement("a");a.href="api/download/"+pdfId;a.download="images.pdf";
  document.body.append(a);a.click();a.remove()
});
</script>
</body>
</html>"""


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