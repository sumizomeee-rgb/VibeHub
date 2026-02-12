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

# In-memory storage for converted images
tasks: dict[str, dict] = {}

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF 转图片工具</title>
<style>*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    color: #e0e0e0;
  }
  .container {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px; padding: 48px; max-width: 720px; width: 90%;
    box-shadow: 0 25px 60px rgba(0,0,0,0.4);
  }
  h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; text-align: center; }
  .subtitle { text-align: center; color: #aaa; margin-bottom: 32px; font-size: 14px; }
  .drop-zone {
    border: 2px dashed rgba(255,255,255,0.25); border-radius: 16px;
    padding: 48px 24px; text-align: center; cursor: pointer;
    transition: all 0.3s; position: relative;
  }
  .drop-zone:hover, .drop-zone.dragover {
    border-color: #7c6aef; background: rgba(124,106,239,0.08);
  }
  .drop-zone input { display: none; }
  .drop-zone .icon { font-size: 48px; margin-bottom: 12px; }
  .drop-zone p { color: #bbb; font-size: 15px; }
  .drop-zone .filename { color: #7c6aef; font-weight: 600; margin-top: 8px; }
  .btn {
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    width: 100%; padding: 14px 24px; border: none; border-radius: 12px;
    font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s;
    margin-top: 20px;
  }
  .btn-primary {
    background: linear-gradient(135deg, #7c6aef, #5a45d6); color: #fff;
  }
  .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(124,106,239,0.4); }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }
  .btn-download {
    background: linear-gradient(135deg, #10b981, #059669); color: #fff;
  }
  .btn-download:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(16,185,129,0.4); }
  .progress-wrap {
    margin-top: 20px; display: none;
  }
  .progress-bar {
    height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;
  }
  .progress-bar .fill {
    height: 100%; width: 0%; background: linear-gradient(90deg, #7c6aef, #10b981);
    border-radius: 3px; transition: width 0.3s;
  }
  .progress-text { text-align: center; margin-top: 8px; font-size: 13px; color: #aaa; }
  .preview-section { margin-top: 28px; display: none; }
  .preview-section h2 { font-size: 18px; margin-bottom: 16px; }
  .preview-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px; max-height: 400px; overflow-y: auto; padding: 4px;
  }
  .preview-grid::-webkit-scrollbar { width: 6px; }
  .preview-grid::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
  .preview-item {
    position: relative; border-radius: 10px; overflow: hidden;
    border: 1px solid rgba(255,255,255,0.1); aspect-ratio: 3/4;
    background: rgba(0,0,0,0.2);
  }
  .preview-item img { width: 100%; height: 100%; object-fit: cover; }
  .preview-item .page-num {
    position: absolute; bottom: 6px; right: 6px;
    background: rgba(0,0,0,0.7); color: #fff; font-size: 11px;
    padding: 2px 8px; border-radius: 6px;
  }
  .error { color: #f87171; text-align: center; margin-top: 12px; font-size: 14px; display: none; }
</style>
</head>
<body>
<div class="container">
  <h1>&#x1F4C4; PDF 转图片</h1>
  <p class="subtitle">上传 PDF 文件，将每一页转换为高清 PNG 图片</p>

  <div class="drop-zone" id="dropZone">
    <div class="icon">&#x1F4C1;</div>
    <p>点击或拖拽 PDF 文件到此处</p>
    <div class="filename" id="fileName"></div>
    <input type="file" id="fileInput" accept=".pdf">
  </div>

  <button class="btn btn-primary" id="convertBtn" disabled>开始转换</button>

  <div class="progress-wrap" id="progressWrap">
    <div class="progress-bar"><div class="fill" id="progressFill"></div></div>
    <div class="progress-text" id="progressText">正在转换中...</div>
  </div>

  <div class="error" id="errorMsg"></div>

  <div class="preview-section" id="previewSection">
    <h2 id="previewTitle">预览</h2>
    <div class="preview-grid" id="previewGrid"></div>
    <button class="btn btn-download" id="downloadBtn">&#x2B07; 下载全部图片 (ZIP)</button>
  </div>
</div>

<script>
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const convertBtn = document.getElementById('convertBtn');
const progressWrap = document.getElementById('progressWrap');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const errorMsg = document.getElementById('errorMsg');
const previewSection = document.getElementById('previewSection');
const previewGrid = document.getElementById('previewGrid');
const previewTitle = document.getElementById('previewTitle');
const downloadBtn = document.getElementById('downloadBtn');

let selectedFile = null;
let currentTaskId = null;

/* Compute the base path so all fetches work behind a reverse proxy */
function getBasePath() {
  let p = window.location.pathname;
  if (!p.endsWith('/')) p += '/';
  return p;
}
const BASE = getBasePath();

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('dragover');
  const f = e.dataTransfer.files[0];
  if (f && f.type === 'application/pdf') selectFile(f);
});
fileInput.addEventListener('change', () => { if (fileInput.files[0]) selectFile(fileInput.files[0]); });

function selectFile(f) {
  selectedFile = f;
  fileName.textContent = f.name;
  convertBtn.disabled = false;
  errorMsg.style.display = 'none';
  previewSection.style.display = 'none';
}

convertBtn.addEventListener('click', async () => {
  if (!selectedFile) return;
  convertBtn.disabled = true;
  progressWrap.style.display = 'block';
  progressFill.style.width = '20%';
  progressText.textContent = '正在上传并转换...';
  errorMsg.style.display = 'none';
  previewSection.style.display = 'none';
  previewGrid.innerHTML = '';

  const form = new FormData();
  form.append('file', selectedFile);

  try {
    progressFill.style.width = '50%';
    const resp = await fetch(BASE + 'convert', { method: 'POST', body: form });
    if (!resp.ok) {
      let detail = '转换失败';
      try { const err = await resp.json(); detail = err.detail || detail; } catch(_) {}
      throw new Error(detail);
    }
    const data = await resp.json();
    currentTaskId = data.task_id;
    const pages = data.pages;

    progressFill.style.width = '80%';
    progressText.textContent = '正在加载预览...';

    previewTitle.textContent = '预览 (共 ' + pages + ' 页)';
    for (let i = 1; i <= pages; i++) {
      const item = document.createElement('div');
      item.className = 'preview-item';
      item.innerHTML = '<img src="' + BASE + 'preview/' + currentTaskId + '/' + i + '" loading="lazy"><span class="page-num">第 ' + i + ' 页</span>';
      previewGrid.appendChild(item);
    }

    progressFill.style.width = '100%';
    progressText.textContent = '转换完成!';
    previewSection.style.display = 'block';

    setTimeout(() => { progressWrap.style.display = 'none'; }, 1000);
  } catch (e) {
    errorMsg.textContent = e.message;
    errorMsg.style.display = 'block';
    progressWrap.style.display = 'none';
  }
  convertBtn.disabled = false;
});

downloadBtn.addEventListener('click', () => {
  if (currentTaskId) window.location.href = BASE + 'download/' + currentTaskId;
});
</script>
</body>
</html>
"""


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