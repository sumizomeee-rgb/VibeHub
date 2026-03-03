# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "pillow"
# ]
# ///

import os
import io
import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from PIL import Image, ImageFilter, ImageDraw, ImageChops

app = FastAPI()

class ProcessRequest(BaseModel):
    image: str
    prompt: str

def add_outline(image: Image.Image, outline_width: int = 10) -> Image.Image:
    """Add white outline to image"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Create outline by dilating the image
    outline = Image.new('RGBA', image.size, (255, 255, 255, 0))
    alpha = image.split()[3]

    # Expand alpha channel to create outline
    expanded = alpha
    for _ in range(outline_width):
        expanded = expanded.filter(ImageFilter.MaxFilter(3))

    # Create white outline layer
    outline.putalpha(expanded)
    draw = ImageDraw.Draw(outline)

    # Composite outline behind original
    result = Image.alpha_composite(outline, image)
    return result

@app.post("/api/process")
async def process_image(req: ProcessRequest):
    try:
        # Decode base64 image
        image_data = base64.b64decode(req.image.split(',')[1] if ',' in req.image else req.image)
        input_image = Image.open(io.BytesIO(image_data))

        # Add white outline
        result_image = add_outline(input_image, outline_width=10)

        # Convert to base64
        buffer = io.BytesIO()
        result_image.save(buffer, format='PNG')
        result_base64 = base64.b64encode(buffer.getvalue()).decode()

        return JSONResponse({"image": f"data:image/png;base64,{result_base64}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI 图像描边/贴纸生成工具</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:#f0f2f5;color:#333;line-height:1.6}
.container{max-width:1200px;margin:0 auto;padding:20px}
.header{background:#fff;padding:20px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:20px}
.header h1{font-size:24px;color:#333}
.main{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px}
.card{background:#fff;padding:24px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.upload-zone{border:2px dashed #cba186;border-radius:12px;padding:60px 20px;text-align:center;cursor:pointer;transition:all .3s;position:relative;overflow:hidden}
.upload-zone:hover{border-color:#000}
.upload-zone.has-image{padding:0;border:none}
.upload-preview{width:100%;height:auto;display:block;border-radius:12px}
.upload-overlay{position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);color:#fff;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .3s}
.upload-zone.has-image:hover .upload-overlay{opacity:1}
.prompt-group{margin:20px 0}
.prompt-group label{display:block;margin-bottom:8px;font-weight:500}
.prompt-group textarea{width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:14px;resize:vertical;min-height:100px}
.error{background:#fee;border:1px solid #fcc;color:#c33;padding:12px;border-radius:8px;margin:12px 0}
.btn{padding:12px 32px;border:none;border-radius:10px;font-size:16px;cursor:pointer;transition:all .3s}
.btn:disabled{opacity:.5;cursor:not-allowed}
.btn-primary{background:#cba186;color:#fff}
.btn-primary:hover:not(:disabled){background:#b8906f}
.result-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.result-header h2{font-size:18px}
.btn-dl{background:#000;color:#fff;padding:8px 20px;font-size:14px}
.result-preview{min-height:300px;border:1px solid #eee;border-radius:12px;display:flex;align-items:center;justify-content:center;background:#fafafa}
.result-preview img{max-width:100%;height:auto;border-radius:12px}
.placeholder{text-align:center;color:#999}
.loading{display:flex;flex-direction:column;align-items:center;gap:12px}
.spinner{width:40px;height:40px;border:4px solid #eee;border-top-color:#cba186;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.footer{background:#fff;padding:16px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.08);text-align:center;color:#666;font-size:14px}
@media(max-width:768px){.main{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
<div class="header"><h1>AI 图像描边/贴纸生成工具</h1></div>
<div class="main">
<div class="card">
<div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
<div id="uploadPlaceholder">
<div style="font-size:48px;margin-bottom:12px">📁</div>
<div>点击上传或拖拽图片</div>
</div>
<img id="uploadPreview" class="upload-preview" style="display:none">
<div class="upload-overlay">更换图片</div>
</div>
<input type="file" id="fileInput" accept="image/*" style="display:none">
<div class="prompt-group">
<label>提示词</label>
<textarea id="promptInput">识别图片中的主体物体，为其添加白色描边效果，使其适合作为贴纸使用。背景应为透明或纯色。</textarea>
</div>
<div id="errorMsg" class="error" style="display:none"></div>
<button class="btn btn-primary" id="processBtn" disabled>开始处理</button>
</div>
<div class="card">
<div class="result-header">
<h2>处理结果</h2>
<button class="btn btn-dl" id="downloadBtn" style="display:none">下载图片</button>
</div>
<div class="result-preview" id="resultPreview">
<div class="placeholder">
<div style="font-size:48px;margin-bottom:12px">🖼️</div>
<div>处理后的图片将显示在这里</div>
</div>
</div>
</div>
</div>
<div class="footer">AI 图像生成具有随机性，如果效果不理想，可以修改提示词后重试。</div>
</div>
<script>
let originalImage=null,processedImage=null;
const uploadZone=document.getElementById('uploadZone'),fileInput=document.getElementById('fileInput'),uploadPreview=document.getElementById('uploadPreview'),uploadPlaceholder=document.getElementById('uploadPlaceholder'),processBtn=document.getElementById('processBtn'),resultPreview=document.getElementById('resultPreview'),downloadBtn=document.getElementById('downloadBtn'),errorMsg=document.getElementById('errorMsg'),promptInput=document.getElementById('promptInput');
fileInput.onchange=e=>{const file=e.target.files[0];if(file){const reader=new FileReader();reader.onload=ev=>{originalImage=ev.target.result;uploadPreview.src=originalImage;uploadPreview.style.display='block';uploadPlaceholder.style.display='none';uploadZone.classList.add('has-image');processBtn.disabled=false;processedImage=null;errorMsg.style.display='none';resultPreview.innerHTML='<div class="placeholder"><div style="font-size:48px;margin-bottom:12px">🖼️</div><div>处理后的图片将显示在这里</div></div>';downloadBtn.style.display='none'};reader.readAsDataURL(file)}};
uploadZone.ondragover=e=>{e.preventDefault();uploadZone.style.borderColor='#000'};
uploadZone.ondragleave=()=>{uploadZone.style.borderColor='#cba186'};
uploadZone.ondrop=e=>{e.preventDefault();uploadZone.style.borderColor='#cba186';const file=e.dataTransfer.files[0];if(file&&file.type.startsWith('image/')){fileInput.files=e.dataTransfer.files;fileInput.dispatchEvent(new Event('change'))}};
processBtn.onclick=async()=>{if(!originalImage)return;processBtn.disabled=true;processBtn.innerHTML='<div class="loading"><div class="spinner"></div>正在处理</div>';errorMsg.style.display='none';resultPreview.innerHTML='<div class="loading"><div class="spinner"></div><div>正在识别主体轮廓...</div></div>';try{const res=await fetch('api/process',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:originalImage,prompt:promptInput.value})});if(!res.ok)throw new Error(await res.text());const data=await res.json();if(!data.image)throw new Error('返回数据格式错误：未包含图片');processedImage=data.image;resultPreview.innerHTML=`<img src="${processedImage}" alt="处理结果">`;downloadBtn.style.display='block'}catch(err){errorMsg.textContent='处理失败：'+err.message;errorMsg.style.display='block';resultPreview.innerHTML='<div class="placeholder"><div style="font-size:48px;margin-bottom:12px">❌</div><div>处理失败</div></div>'}finally{processBtn.disabled=false;processBtn.textContent='开始处理'}};
downloadBtn.onclick=()=>{if(!processedImage)return;const a=document.createElement('a');a.href=processedImage;a.download='sticker.png';a.click()};
</script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
