# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "pillow",
#     "numpy",
#     "python-multipart"
# ]
# ///

import os
import io
import asyncio
import base64
import zipfile
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
app = FastAPI()

def add_stroke(img: Image.Image, color: str, width: int) -> Image.Image:
    """Add stroke/outline to image"""
    if width <= 0:
        return img

    # Convert hex to RGB
    color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # Create alpha mask
    alpha = img.split()[-1] if img.mode == 'RGBA' else Image.new('L', img.size, 255)

    # Dilate mask to create stroke
    stroke_mask = alpha.filter(ImageFilter.MaxFilter(width * 2 + 1))

    # Create stroke layer
    stroke_layer = Image.new('RGBA', img.size, color_rgb + (255,))
    stroke_layer.putalpha(stroke_mask)

    # Composite
    result = Image.new('RGBA', img.size, (0, 0, 0, 0))
    result.paste(stroke_layer, (0, 0), stroke_layer)
    result.paste(img, (0, 0), img)

    return result

def adjust_temperature(img: Image.Image, temp: float) -> Image.Image:
    """Adjust color temperature (-1 to 1, negative=cool, positive=warm)"""
    if temp == 0:
        return img

    arr = np.array(img.convert('RGB'))
    if temp > 0:  # Warm
        arr[:, :, 0] = np.clip(arr[:, :, 0] + temp * 30, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] - temp * 30, 0, 255)
    else:  # Cool
        arr[:, :, 0] = np.clip(arr[:, :, 0] + temp * 30, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] - temp * 30, 0, 255)

    result = Image.fromarray(arr.astype('uint8'), 'RGB')
    if img.mode == 'RGBA':
        result.putalpha(img.split()[-1])
    return result

def add_noise(img: Image.Image, intensity: float) -> Image.Image:
    """Add grain/noise texture"""
    if intensity <= 0:
        return img

    arr = np.array(img)
    noise = np.random.normal(0, intensity * 25, arr.shape[:2])

    for i in range(min(3, arr.shape[2])):
        arr[:, :, i] = np.clip(arr[:, :, i] + noise, 0, 255)

    return Image.fromarray(arr.astype('uint8'), img.mode)

def process_image(
    img_data: bytes,
    remove_bg: bool,
    inner_color: str, inner_width: int,
    mid_color: str, mid_width: int,
    outer_color: str, outer_width: int,
    temp: float, contrast: float, noise: float,
    crop_x: float, crop_y: float, crop_w: float, crop_h: float,
    interp: str
) -> Image.Image:
    """Process single image with all effects"""
    img = Image.open(io.BytesIO(img_data)).convert('RGBA')

    # Crop
    if crop_w > 0 and crop_h > 0:
        w, h = img.size
        x1 = int(crop_x * w)
        y1 = int(crop_y * h)
        x2 = int((crop_x + crop_w) * w)
        y2 = int((crop_y + crop_h) * h)
        img = img.crop((x1, y1, x2, y2))

    # Remove background mock (just do nothing to original image)
    if remove_bg:
        pass

    # Strokes (inner -> mid -> outer, so outer ends up outermost)
    img = add_stroke(img, inner_color, inner_width)
    img = add_stroke(img, mid_color, mid_width)
    img = add_stroke(img, outer_color, outer_width)

    # Color adjustments
    img = adjust_temperature(img, temp)
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)

    # Noise
    img = add_noise(img, noise)

    return img

@app.post("/api/process")
async def process_images(
    files: List[UploadFile] = File(...),
    remove_bg: bool = Form(False),
    inner_color: str = Form("#ffffff"),
    inner_width: int = Form(0),
    mid_color: str = Form("#000000"),
    mid_width: int = Form(2),
    outer_color: str = Form("#ffffff"),
    outer_width: int = Form(4),
    temp: float = Form(0),
    contrast: float = Form(1.0),
    noise: float = Form(0),
    crop_x: float = Form(0),
    crop_y: float = Form(0),
    crop_w: float = Form(1),
    crop_h: float = Form(1),
    interp: str = Form("LANCZOS")
):
    """Process images and return base64 previews"""
    results = []


    for file in files:
        img_data = await file.read()
        img = process_image(
            img_data, remove_bg,
            inner_color, inner_width,
            mid_color, mid_width,
            outer_color, outer_width,
            temp, contrast, noise,
            crop_x, crop_y, crop_w, crop_h,
            interp
        )

        # Generate preview (256px)
        img_256 = img.copy()
        img_256.thumbnail((256, 256), getattr(Image.Resampling, interp))

        buf = io.BytesIO()
        img_256.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()

        results.append({
            "filename": file.filename,
            "preview": f"data:image/png;base64,{b64}"
        })

    return {"results": results}

@app.post("/api/download")
async def download_zip(
    files: List[UploadFile] = File(...),
    remove_bg: bool = Form(False),
    inner_color: str = Form("#ffffff"),
    inner_width: int = Form(0),
    mid_color: str = Form("#000000"),
    mid_width: int = Form(2),
    outer_color: str = Form("#ffffff"),
    outer_width: int = Form(4),
    temp: float = Form(0),
    contrast: float = Form(1.0),
    noise: float = Form(0),
    crop_x: float = Form(0),
    crop_y: float = Form(0),
    crop_w: float = Form(1),
    crop_h: float = Form(1),
    interp: str = Form("LANCZOS")
):
    """Generate ZIP with 256px and 128px versions"""
    zip_buffer = io.BytesIO()
    await asyncio.sleep(1.0) # Mock long processing time


    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            img_data = await file.read()
            img = process_image(
                img_data, remove_bg,
                inner_color, inner_width,
                mid_color, mid_width,
                outer_color, outer_width,
                temp, contrast, noise,
                crop_x, crop_y, crop_w, crop_h,
                interp
            )

            base_name = os.path.splitext(file.filename)[0]

            # 256px version
            img_256 = img.copy()
            img_256.thumbnail((256, 256), getattr(Image.Resampling, interp))
            buf_256 = io.BytesIO()
            img_256.save(buf_256, format='PNG')
            zf.writestr(f"{base_name}_256.png", buf_256.getvalue())

            # 128px version
            img_128 = img.copy()
            img_128.thumbnail((128, 128), getattr(Image.Resampling, interp))
            buf_128 = io.BytesIO()
            img_128.save(buf_128, format='PNG')
            zf.writestr(f"{base_name}_128.png", buf_128.getvalue())

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=stickers.zip"}
    )

@app.get("/", response_class=HTMLResponse)
async def index():
    return r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>贴纸风格生成器 Pro</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f0f2f5; }
.header { background: #fff; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.05); }
.header h1 { color: #333; font-size: 24px; }
.container { display: flex; gap: 20px; padding: 20px; max-width: 1600px; margin: 0 auto; align-items: flex-start; }
.sidebar { width: 320px; flex-shrink: 0; max-height: calc(100vh - 100px); overflow-y: auto; }
.main { flex: 1; min-width: 0; position: sticky; top: 20px; }
.card { background: #fff; border-radius: 16px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,.08); margin-bottom: 20px; }
.card h3 { margin-bottom: 15px; color: #333; font-size: 16px; }
.upload-zone { border: 2px dashed #cba186; border-radius: 12px; padding: 40px 20px; text-align: center; cursor: pointer; transition: all .3s; }
.upload-zone:hover { border-color: #000; background: #fafafa; }
.upload-zone input { display: none; }
.btn-primary { background: #cba186; color: #fff; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; font-size: 14px; transition: opacity .3s; }
.btn-primary:hover { opacity: .8; }
.btn-secondary { background: #eee; color: #333; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; font-size: 14px; }
.btn-dl { background: #000; color: #fff; border: none; padding: 8px 16px; border-radius: 10px; cursor: pointer; font-size: 13px; }
.control-group { margin-bottom: 20px; }
.control-group label { display: block; margin-bottom: 8px; color: #666; font-size: 14px; }
.control-row { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
input[type="color"] { width: 50px; height: 36px; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; }
input[type="text"] { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }
input[type="range"] { flex: 1; }
select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
.toggle { position: relative; display: inline-block; width: 50px; height: 26px; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle-slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #ccc; border-radius: 26px; transition: .3s; }
.toggle-slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 3px; bottom: 3px; background: #fff; border-radius: 50%; transition: .3s; }
.toggle input:checked + .toggle-slider { background: #cba186; }
.toggle input:checked + .toggle-slider:before { transform: translateX(24px); }
.empty-state { text-align: center; padding: 80px 20px; color: #999; }
.toolbar { display: flex; gap: 10px; margin-bottom: 20px; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.img-card { background: #fff; border-radius: 16px; padding: 15px; box-shadow: 0 2px 12px rgba(0,0,0,.08); position: relative; }
.img-card img { width: 100%; border-radius: 8px; display: block; }
.img-card .filename { margin: 10px 0; font-size: 13px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.img-card .edit-btn { position: absolute; top: 20px; right: 20px; background: rgba(0,0,0,.7); color: #fff; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }
.modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,.8); z-index: 1000; align-items: center; justify-content: center; }
.modal.active { display: flex; }
.modal-content { background: #fff; border-radius: 16px; padding: 30px; max-width: 90vw; max-height: 90vh; position: relative; }
.crop-container { position: relative; display: inline-block; }
.crop-box { position: absolute; border: 2px solid #cba186; cursor: move; }
.crop-handle { position: absolute; right: -6px; bottom: -6px; width: 12px; height: 12px; background: #cba186; border-radius: 50%; cursor: nwse-resize; }
.modal-actions { margin-top: 20px; display: flex; gap: 10px; justify-content: center; }
@media (max-width: 1024px) { .container { flex-direction: column; } .sidebar { width: 100%; } .grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="header"><h1>贴纸风格生成器 Pro</h1></div>
<div class="container">
<div class="sidebar">
<div class="card">
<h3>上传图片</h3>
<div class="upload-zone" onclick="document.getElementById('fileInput').click()">
<input type="file" id="fileInput" multiple accept="image/*">
<p>📁 点击或拖拽上传图片</p>
</div>
</div>
<div class="card">
<h3>全局控制</h3>
<button class="btn-secondary" onclick="resetDefaults()" style="width:100%;margin-bottom:10px">恢复默认值</button>
<div class="control-group">
<label style="display:flex;align-items:center;gap:10px">
<span>自动去除背景</span>
<label class="toggle"><input type="checkbox" id="removeBg"><span class="toggle-slider"></span></label>
</label>
</div>
<div class="control-group">
<label>图像插值算法</label>
<select id="interp">
<option value="NEAREST">最近邻（快速）</option>
<option value="BILINEAR">双线性（平衡）</option>
<option value="LANCZOS" selected>Lanczos（高质量）</option>
</select>
</div>
</div>
<div class="card">
<h3>描边设置</h3>
<div class="control-group">
<label>内层描边</label>
<div class="control-row">
<input type="color" id="innerColor" value="#ffffff">
<input type="text" id="innerColorHex" value="#ffffff">
</div>
<input type="range" id="innerWidth" min="0" max="20" value="0">
</div>
<div class="control-group">
<label>中层描边</label>
<div class="control-row">
<input type="color" id="midColor" value="#000000">
<input type="text" id="midColorHex" value="#000000">
</div>
<input type="range" id="midWidth" min="0" max="20" value="2">
</div>
<div class="control-group">
<label>外层描边</label>
<div class="control-row">
<input type="color" id="outerColor" value="#ffffff">
<input type="text" id="outerColorHex" value="#ffffff">
</div>
<input type="range" id="outerWidth" min="0" max="20" value="4">
</div>
</div>
<div class="card">
<h3>图像调色</h3>
<div class="control-group">
<label>色温（冷 ← → 暖）</label>
<input type="range" id="temp" min="-1" max="1" step="0.1" value="0">
</div>
<div class="control-group">
<label>对比度</label>
<input type="range" id="contrast" min="0.5" max="2" step="0.1" value="1">
</div>
</div>
<div class="card">
<h3>质感调节</h3>
<div class="control-group">
<label>杂质/噪点强度</label>
<input type="range" id="noise" min="0" max="1" step="0.05" value="0">
</div>
</div>
<button class="btn-primary" id="refreshBtn" onclick="refreshPreview()" style="width:100%;display:none">🔄 手动刷新预览</button>
</div>
<div class="main">
<div id="emptyState" class="empty-state">
<p style="font-size:48px">📸</p>
<p>请上传图片开始处理</p>
</div>
<div id="resultArea" style="display:none">
<div class="toolbar">
<button class="btn-secondary" onclick="clearAll()">清空列表</button>
<button class="btn-dl" onclick="downloadAll()">批量下载 ZIP</button>
</div>
<div class="grid" id="grid"></div>
</div>
</div>
</div>
<div class="modal" id="cropModal">
<div class="modal-content">
<div class="crop-container" id="cropContainer"></div>
<div class="modal-actions">
<button class="btn-secondary" onclick="closeCrop()">取消</button>
<button class="btn-primary" onclick="applyCrop()">应用裁剪</button>
</div>
</div>
</div>
<script>
let uploadedFiles = [];
let cropData = {x:0, y:0, w:1, h:1};
// Real-time refresh with abort controller
let refreshTimeout;
let currentAbortController = null;

function requestRefresh() {
  if (!uploadedFiles.length) return;
  clearTimeout(refreshTimeout);
  refreshTimeout = setTimeout(refreshPreview, 400); // Debounce for smooth performance
}

// Color sync
['inner','mid','outer'].forEach(layer => {
  document.getElementById(layer+'Color').addEventListener('input', e => {
    document.getElementById(layer+'ColorHex').value = e.target.value;
    requestRefresh();
  });
  document.getElementById(layer+'ColorHex').addEventListener('input', e => {
    document.getElementById(layer+'Color').value = e.target.value;
    requestRefresh();
  });
});

// Auto-refresh on other inputs
['removeBg', 'innerWidth', 'midWidth', 'outerWidth', 'temp', 'contrast', 'noise', 'interp'].forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener('input', requestRefresh);
    el.addEventListener('change', requestRefresh);
  }
});

// File upload
document.getElementById('fileInput').addEventListener('change', e => {
  uploadedFiles = Array.from(e.target.files);
  if(uploadedFiles.length) {
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('resultArea').style.display = 'block';
    document.getElementById('refreshBtn').style.display = 'block';
    refreshPreview();
  }
});

// Drag & drop
const zone = document.querySelector('.upload-zone');
zone.addEventListener('dragover', e => { e.preventDefault(); zone.style.borderColor = '#000'; });
zone.addEventListener('dragleave', () => { zone.style.borderColor = '#cba186'; });
zone.addEventListener('drop', e => {
  e.preventDefault();
  zone.style.borderColor = '#cba186';
  const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
  if(files.length) {
    uploadedFiles = files;
    document.getElementById('fileInput').files = e.dataTransfer.files;
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('resultArea').style.display = 'block';
    document.getElementById('refreshBtn').style.display = 'block';
    refreshPreview();
  }
});

async function refreshPreview() {
  if (currentAbortController) {
    currentAbortController.abort();
  }
  currentAbortController = new AbortController();

  const formData = new FormData();
  uploadedFiles.forEach(f => formData.append('files', f));
  formData.append('remove_bg', document.getElementById('removeBg').checked);
  formData.append('inner_color', document.getElementById('innerColor').value);
  formData.append('inner_width', document.getElementById('innerWidth').value);
  formData.append('mid_color', document.getElementById('midColor').value);
  formData.append('mid_width', document.getElementById('midWidth').value);
  formData.append('outer_color', document.getElementById('outerColor').value);
  formData.append('outer_width', document.getElementById('outerWidth').value);
  formData.append('temp', document.getElementById('temp').value);
  formData.append('contrast', document.getElementById('contrast').value);
  formData.append('noise', document.getElementById('noise').value);
  formData.append('crop_x', cropData.x);
  formData.append('crop_y', cropData.y);
  formData.append('crop_w', cropData.w);
  formData.append('crop_h', cropData.h);
  formData.append('interp', document.getElementById('interp').value);

  try {
    const res = await fetch('api/process', { method: 'POST', body: formData });
    const data = await res.json();

    const grid = document.getElementById('grid');
  grid.innerHTML = '';
  data.results.forEach((r, i) => {
    const card = document.createElement('div');
    card.className = 'img-card';
    card.innerHTML = `
      <button class="edit-btn" onclick="openCrop(${i})">✂️ 裁剪</button>
      <img src="${r.preview}" alt="${r.filename}">
      <div class="filename">${r.filename}</div>
      <button class="btn-dl" onclick="downloadSingle(${i})" style="width:100%">下载 ZIP</button>
    `;
    grid.appendChild(card);
  });
  } catch (err) {
    console.error(err);
  } finally {
    isRendering = false;
    if (needsRender) {
      refreshPreview();
    }
  }
}

function openCrop(index) {
  currentCropIndex = index;
  const file = uploadedFiles[index];
  const reader = new FileReader();
  reader.onload = e => {
    const img = new Image();
    img.onload = () => {
      const container = document.getElementById('cropContainer');
      container.innerHTML = '';
      img.style.maxWidth = '80vw';
      img.style.maxHeight = '70vh';
      img.style.display = 'block';
      container.appendChild(img);

      const box = document.createElement('div');
      box.className = 'crop-box';
      box.style.left = (cropData.x * img.width) + 'px';
      box.style.top = (cropData.y * img.height) + 'px';
      box.style.width = (cropData.w * img.width) + 'px';
      box.style.height = (cropData.h * img.height) + 'px';

      const handle = document.createElement('div');
      handle.className = 'crop-handle';
      box.appendChild(handle);
      container.appendChild(box);

      let isDragging = false, isResizing = false, startX, startY, startLeft, startTop, startWidth, startHeight;

      box.addEventListener('mousedown', e => {
        if(e.target === handle) {
          isResizing = true;
          startWidth = box.offsetWidth;
          startHeight = box.offsetHeight;
        } else {
          isDragging = true;
          startLeft = box.offsetLeft;
          startTop = box.offsetTop;
        }
        startX = e.clientX;
        startY = e.clientY;
        e.preventDefault();
      });

      document.addEventListener('mousemove', e => {
        if(isDragging) {
          let newLeft = startLeft + e.clientX - startX;
          let newTop = startTop + e.clientY - startY;
          newLeft = Math.max(0, Math.min(newLeft, img.width - box.offsetWidth));
          newTop = Math.max(0, Math.min(newTop, img.height - box.offsetHeight));
          box.style.left = newLeft + 'px';
          box.style.top = newTop + 'px';
        } else if(isResizing) {
          let newWidth = startWidth + e.clientX - startX;
          let newHeight = startHeight + e.clientY - startY;
          newWidth = Math.max(50, Math.min(newWidth, img.width - box.offsetLeft));
          newHeight = Math.max(50, Math.min(newHeight, img.height - box.offsetTop));
          box.style.width = newWidth + 'px';
          box.style.height = newHeight + 'px';
        }
      });

      document.addEventListener('mouseup', () => {
        isDragging = false;
        isResizing = false;
      });

      document.getElementById('cropModal').classList.add('active');
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function closeCrop() {
  document.getElementById('cropModal').classList.remove('active');
}

function applyCrop() {
  const container = document.getElementById('cropContainer');
  const img = container.querySelector('img');
  const box = container.querySelector('.crop-box');
  cropData = {
    x: box.offsetLeft / img.width,
    y: box.offsetTop / img.height,
    w: box.offsetWidth / img.width,
    h: box.offsetHeight / img.height
  };
  closeCrop();
  refreshPreview();
}

async function downloadSingle(index) {
  const formData = new FormData();
  formData.append('files', uploadedFiles[index]);
  formData.append('remove_bg', document.getElementById('removeBg').checked);
  formData.append('inner_color', document.getElementById('innerColor').value);
  formData.append('inner_width', document.getElementById('innerWidth').value);
  formData.append('mid_color', document.getElementById('midColor').value);
  formData.append('mid_width', document.getElementById('midWidth').value);
  formData.append('outer_color', document.getElementById('outerColor').value);
  formData.append('outer_width', document.getElementById('outerWidth').value);
  formData.append('temp', document.getElementById('temp').value);
  formData.append('contrast', document.getElementById('contrast').value);
  formData.append('noise', document.getElementById('noise').value);
  formData.append('crop_x', cropData.x);
  formData.append('crop_y', cropData.y);
  formData.append('crop_w', cropData.w);
  formData.append('crop_h', cropData.h);
  formData.append('interp', document.getElementById('interp').value);

  const res = await fetch('api/download', { method: 'POST', body: formData });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = uploadedFiles[index].name.replace(/\.[^.]+$/, '') + '.zip';
  a.click();
  URL.revokeObjectURL(url);
}

async function downloadAll() {
  const formData = new FormData();
  uploadedFiles.forEach(f => formData.append('files', f));
  formData.append('remove_bg', document.getElementById('removeBg').checked);
  formData.append('inner_color', document.getElementById('innerColor').value);
  formData.append('inner_width', document.getElementById('innerWidth').value);
  formData.append('mid_color', document.getElementById('midColor').value);
  formData.append('mid_width', document.getElementById('midWidth').value);
  formData.append('outer_color', document.getElementById('outerColor').value);
  formData.append('outer_width', document.getElementById('outerWidth').value);
  formData.append('temp', document.getElementById('temp').value);
  formData.append('contrast', document.getElementById('contrast').value);
  formData.append('noise', document.getElementById('noise').value);
  formData.append('crop_x', cropData.x);
  formData.append('crop_y', cropData.y);
  formData.append('crop_w', cropData.w);
  formData.append('crop_h', cropData.h);
  formData.append('interp', document.getElementById('interp').value);

  const res = await fetch('api/download', { method: 'POST', body: formData });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'stickers.zip';
  a.click();
  URL.revokeObjectURL(url);
}

function clearAll() {
  uploadedFiles = [];
  cropData = {x:0, y:0, w:1, h:1};
  document.getElementById('fileInput').value = '';
  document.getElementById('emptyState').style.display = 'block';
  document.getElementById('resultArea').style.display = 'none';
  document.getElementById('refreshBtn').style.display = 'none';
}

function resetDefaults() {
  document.getElementById('removeBg').checked = false;
  document.getElementById('innerColor').value = '#ffffff';
  document.getElementById('innerColorHex').value = '#ffffff';
  document.getElementById('innerWidth').value = 0;
  document.getElementById('midColor').value = '#000000';
  document.getElementById('midColorHex').value = '#000000';
  document.getElementById('midWidth').value = 2;
  document.getElementById('outerColor').value = '#ffffff';
  document.getElementById('outerColorHex').value = '#ffffff';
  document.getElementById('outerWidth').value = 4;
  document.getElementById('temp').value = 0;
  document.getElementById('contrast').value = 1;
  document.getElementById('noise').value = 0;
  document.getElementById('interp').value = 'LANCZOS';
  cropData = {x:0, y:0, w:1, h:1};
  if(uploadedFiles.length) refreshPreview();
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
