# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn", "python-multipart", "pymupdf"]
# ///

import os
import io
import zipfile
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI()
TOOL_NAME = os.environ.get("DISPLAY_NAME") or "PDF 转图片"

tasks: dict[str, dict] = {}

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

HTML = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TOOL_NAME}}</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#f0f2f5;min-height:100vh;padding:20px}
.header{display:flex;justify-content:space-between;align-items:center;max-width:1100px;margin:0 auto 20px;padding:16px 24px;background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.header h1{font-size:20px;color:#333}
.upload-card{max-width:1100px;margin:0 auto 20px;background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);padding:24px}
.upload-card h2{font-size:18px;margin-bottom:16px;color:#333}
.drop{border:2px dashed #cba186;border-radius:12px;padding:40px 20px;text-align:center;cursor:pointer;transition:.2s;color:#999;position:relative;overflow:hidden}
.drop:hover,.drop.over{border-color:#000;background:#faf6ec}
.drop input{display:none}
.filename{margin-top:8px;color:#cba186;font-weight:600;font-size:14px}
.actions-row{max-width:1100px;margin:0 auto 20px;display:flex;justify-content:center}
.btn{padding:12px 24px;border:none;border-radius:10px;font-size:15px;cursor:pointer;transition:.2s;font-weight:600}
.btn-primary{background:#cba186;color:#fff}.btn-primary:hover:not(:disabled){background:#b8906f}
.btn-success{background:#10b981;color:#fff}.btn-success:hover:not(:disabled){background:#059669}
.btn:disabled{opacity:.4;cursor:not-allowed}
.progress-wrap{max-width:1100px;margin:0 auto 20px;display:none}
.progress-bar{height:4px;background:#e5e5e5;border-radius:2px;overflow:hidden}
.progress-bar .fill{height:100%;background:#cba186;width:0;transition:width .3s}
.progress-text{text-align:center;margin-top:8px;font-size:13px;color:#666}
.preview-section{max-width:1100px;margin:0 auto;background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);padding:20px;display:none}
.preview-section h3{font-size:16px;margin-bottom:16px;color:#333}
.preview-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;max-height:400px;overflow-y:auto;padding:4px}
.preview-grid::-webkit-scrollbar{width:6px}
.preview-grid::-webkit-scrollbar-thumb{background:#ddd;border-radius:3px}
.preview-item{position:relative;border-radius:10px;overflow:hidden;border:1px solid #eee;aspect-ratio:3/4;background:#fafafa}
.preview-item img{width:100%;height:100%;object-fit:cover}
.preview-item .page-num{position:absolute;bottom:6px;right:6px;background:rgba(0,0,0,.7);color:#fff;font-size:11px;padding:2px 8px;border-radius:6px}
.err{max-width:1100px;margin:0 auto;text-align:center;color:#e74c3c;font-size:14px;display:none}
</style></head><body>
<div class="header">
<h1>{{TOOL_NAME}}</h1>
</div>
<div class="upload-card">
<h2>上传 PDF 文件</h2>
<div class="drop" id="dropZone" onclick="fi.click()">
<div id="ph">点击或拖拽 PDF 文件到此处</div>
<div class="filename" id="fileName"></div><input type="file" id="fi" accept=".pdf">
</div>
</div>
<div class="actions-row">
<button class="btn btn-primary" id="convertBtn" disabled onclick="convert()">开始转换</button>
</div>
<div class="progress-wrap" id="progressWrap">
<div class="progress-bar"><div class="fill" id="progressFill"></div></div>
<div class="progress-text" id="progressText">正在转换中...</div>
</div>
<div class="err" id="errorMsg"></div>
<div class="preview-section" id="previewSection">
<h3 id="previewTitle">预览</h3>
<div class="preview-grid" id="previewGrid"></div>
<div class="actions-row" style="margin:20px 0 0 0">
<button class="btn btn-success" id="downloadBtn" onclick="download()">下载全部图片 (ZIP)</button>
</div>
</div>
<script>
const dropZone=$('#dropZone'),fi=$('#fi'),fileName=$('#fileName'),convertBtn=$('#convertBtn'),progressWrap=$('#progressWrap'),progressFill=$('#progressFill'),progressText=$('#progressText'),errorMsg=$('#errorMsg'),previewSection=$('#previewSection'),previewGrid=$('#previewGrid'),previewTitle=$('#previewTitle'),downloadBtn=$('#downloadBtn');
function $(s){return document.querySelector(s)}
let selectedFile=null,currentTaskId=null;
function getBasePath(){let p=window.location.pathname;if(!p.endsWith('/'))p+='/';return p}
const BASE=getBasePath();
dropZone.onclick=()=>fi.click();
dropZone.ondragover=e=>{e.preventDefault();dropZone.classList.add('over')};
dropZone.ondragleave=()=>dropZone.classList.remove('over');
dropZone.ondrop=e=>{e.preventDefault();dropZone.classList.remove('over');const f=e.dataTransfer.files[0];if(f&&f.type==='application/pdf')selectFile(f)};
fi.onchange=()=>{if(fi.files[0])selectFile(fi.files[0])};
function selectFile(f){selectedFile=f;fileName.textContent=f.name;convertBtn.disabled=false;errorMsg.style.display='none';previewSection.style.display='none'}
async function convert(){if(!selectedFile)return;convertBtn.disabled=true;progressWrap.style.display='block';progressFill.style.width='20%';progressText.textContent='正在上传并转换...';errorMsg.style.display='none';previewSection.style.display='none';previewGrid.innerHTML='';
const form=new FormData();form.append('file',selectedFile);
try{progressFill.style.width='50%';const resp=await fetch(BASE+'convert',{method:'POST',body:form});
if(!resp.ok){let detail='转换失败';try{const err=await resp.json();detail=err.detail||detail}catch(_){}throw new Error(detail)}
const data=await resp.json();currentTaskId=data.task_id;const pages=data.pages;progressFill.style.width='80%';progressText.textContent='正在加载预览...';
previewTitle.textContent='预览 (共 '+pages+' 页)';
for(let i=1;i<=pages;i++){const item=document.createElement('div');item.className='preview-item';item.innerHTML='<img src="'+BASE+'preview/'+currentTaskId+'/'+i+'" loading="lazy"><span class="page-num">第 '+i+' 页</span>';previewGrid.appendChild(item)}
progressFill.style.width='100%';progressText.textContent='转换完成!';previewSection.style.display='block';setTimeout(()=>{progressWrap.style.display='none'},1000)}
catch(e){errorMsg.textContent=e.message;errorMsg.style.display='block';progressWrap.style.display='none'}
convertBtn.disabled=false}
function download(){if(currentTaskId)window.location.href=BASE+'download/'+currentTaskId}
</script></body></html>""".replace("{{TOOL_NAME}}", TOOL_NAME)


@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="请上传 PDF 文件")

    import fitz

    task_id = str(uuid.uuid4())
    pdf_bytes = await file.read()

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception:
        raise HTTPException(status_code=400, detail="无法解析该 PDF 文件")

    page_count = len(doc)
    if page_count > 200:
        doc.close()
        raise HTTPException(status_code=400, detail="PDF 页数过多（最多 200 页）")

    images = {}
    for i in range(page_count):
        page = doc.load_page(i)
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        images[i + 1] = pix.tobytes("png")

    doc.close()

    tasks[task_id] = {"images": images, "filename": Path(file.filename).stem}

    if len(tasks) > 20:
        oldest = list(tasks.keys())[0]
        del tasks[oldest]

    return {"task_id": task_id, "pages": len(images)}


@app.get("/preview/{task_id}/{page}")
async def preview_page(task_id: str, page: int):
    if task_id not in tasks or page not in tasks[task_id]["images"]:
        raise HTTPException(status_code=404, detail="未找到")
    return StreamingResponse(
        io.BytesIO(tasks[task_id]["images"][page]),
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@app.get("/download/{task_id}")
async def download_zip(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="未找到")

    task = tasks[task_id]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for page_num, png_data in task["images"].items():
            zf.writestr(f"{task['filename']}_page_{page_num}.png", png_data)
    buf.seek(0)

    safe_filename = task["filename"].replace('"', "_")
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}_images.zip"'
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))