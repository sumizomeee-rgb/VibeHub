# VibeHub 工具 UI 设计规范

> 本文档定义 VibeHub 项目中所有工具的统一 UI 风格和配色规范，确保视觉一致性。

## 配色系统

| 用途 | 色值 | 说明 |
|------|------|------|
| 主色调 | `#cba186` | 棕色系，用于主按钮、链接、高亮 |
| 主色悬停 | `#b8906f` | 主按钮悬停状态 |
| 背景色 | `#f0f2f5` | 页面背景，浅灰 |
| 卡片背景 | `#ffffff` | 白色，用于卡片、模态框 |
| 文字主色 | `#333333` | 标题、正文文字 |
| 文字次色 | `#666666` | 辅助文字、说明 |
| 文字弱色 | `#999999` | 占位符、标注 |
| 边框色 | `#eeeeee` | 输入框、卡片边框 |
| 成功色 | `#10b981` | 绿色，用于成功状态、下载按钮 |
| 成功悬停 | `#059669` |  |
| 错误色 | `#e74c3c` | 红色，用于错误提示 |

## 组件规范

### 页面结构

```
body (background: #f0f2f5, padding: 20px)
  ├─ .header (白色卡片，标题 + 操作按钮)
  ├─ .upload-card (白色卡片，上传区域)
  ├─ .actions-row (按钮行)
  ├─ .specGrid / .preview-grid (网格布局)
  └─ 模态框（如有）
```

### 顶部标题区 (`.header`)

```css
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1100px;
    margin: 0 auto 20px;
    padding: 16px 24px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,.08);
}
.header h1 {
    font-size: 20px;
    color: #333;
}
```

### 上传卡片 (`.upload-card`)

```css
.upload-card {
    max-width: 1100px;
    margin: 0 auto 20px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,.08);
    padding: 24px;
}
.upload-card h2 {
    font-size: 18px;
    margin-bottom: 16px;
    color: #333;
}
```

### 拖拽上传区 (`.drop`)

```css
.drop {
    border: 2px dashed #cba186;
    border-radius: 12px;
    padding: 40px 20px;
    text-align: center;
    cursor: pointer;
    transition: .2s;
    color: #999;
}
.drop:hover, .drop.over {
    border-color: #000;
    background: #faf6ec;
}
```

### 按钮样式

```css
.btn {
    padding: 10px 18px;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    cursor: pointer;
    transition: .2s;
    font-weight: 600;
}
.btn-primary {
    background: #cba186;
    color: #fff;
}
.btn-primary:hover:not(:disabled) {
    background: #b8906f;
}
.btn-secondary {
    background: #eee;
    color: #333;
}
.btn-secondary:hover:not(:disabled) {
    background: #ddd;
}
.btn-dl, .btn-download {
    background: #000;
    color: #fff;
}
.btn-dl:hover:not(:disabled), .btn-download:hover:not(:disabled) {
    background: #333;
}
.btn-success {
    background: #10b981;
    color: #fff;
}
.btn-success:hover:not(:disabled) {
    background: #059669;
}
.btn:disabled {
    opacity: .4;
    cursor: not-allowed;
}
```

### 网格布局 (`.specGrid` / `.preview-grid`)

```css
.spec-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    max-width: 1100px;
    margin: 0 auto;
}
.spec-card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,.08);
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
/* 响应式：平板 2 列，手机 1 列 */
@media(max-width: 900px) {
    .spec-grid { grid-template-columns: repeat(2, 1fr); }
}
@media(max-width: 600px) {
    .spec-grid { grid-template-columns: 1fr; }
}
```

### 棋盘格透明背景

用于图片预览区显示透明效果：

```css
.transparent-bg {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background-image:
        linear-gradient(45deg, #e0e0e0 25%, transparent 25%),
        linear-gradient(-45deg, #e0e0e0 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #e0e0e0 75%),
        linear-gradient(-45deg, transparent 75%, #e0e0e0 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0;
}
```

### 进度条

```css
.progress-bar {
    height: 4px;
    background: #e5e5e5;
    border-radius: 2px;
    margin-top: 10px;
    overflow: hidden;
}
.progress-bar .fill {
    height: 100%;
    background: #cba186;
    width: 0;
    transition: width .3s;
}
```

### 模态框

```css
.modal-bg {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.5);
    backdrop-filter: blur(4px);
    display: none;
    z-index: 100;
    align-items: center;
    justify-content: center;
}
.modal-bg.show { display: flex; }
.modal {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,.15);
    width: 92vw;
    max-width: 900px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
```

### 加载动画

```css
.loader {
    width: 24px;
    height: 24px;
    border: 3px solid #eee;
    border-top-color: #cba186;
    border-radius: 50%;
    animation: spin .6s linear infinite;
}
@keyframes spin {
    to { transform: rotate(360deg); }
}
```

### 输入框

```css
input[type="text"] {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    font-size: 13px;
    outline: none;
}
input[type="text"]:focus {
    border-color: #cba186;
}
```

## 通用 JavaScript 模式

### 基础结构

```javascript
const fi=$('#fi'),dropZone=$('#dropZone'),convertBtn=$('#convertBtn'),statusEl=$('#status');
function $(s){return document.querySelector(s)}  // 简短的选择器函数

// 文件上传
dropZone.onclick=()=>fi.click();
dropZone.ondragover=e=>{e.preventDefault();dropZone.classList.add('over')};
dropZone.ondragleave=()=>dropZone.classList.remove('over');
dropZone.ondrop=e=>{e.preventDefault();dropZone.classList.remove('over');handleFile(e.dataTransfer.files[0])};
fi.onchange=()=>{if(fi.files[0])handleFile(fi.files[0])};

async function handleFile(file){
    // 处理文件...
}
```

## 给 Claude 的提示词模板

当创建新工具时，请在提示词中加入以下内容：

```
请按照 VibeHub 统一 UI 风格设计：
- 配色：主色 #cba186，背景 #f0f2f5，白色圆角卡片（border-radius: 16px），微阴影
- 布局：顶部 header（标题 + 操作按钮）+ 上传卡片 + 按钮行 + 网格预览
- 按钮：圆角 10px，.btn-primary（主色）、.btn-secondary（次级）、.btn-dl（黑色下载）
- 拖拽区：虚线边框 #cba186，hover 变黑色
- 透明背景预览使用棋盘格背景
- 响应式：桌面 3 列，平板 2 列，手机 1 列
- 所有文字使用中文
```

## Python 模板结构

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn", "..."]
# ///

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="工具名称")

HTML = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>工具名称</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#f0f2f5;min-height:100vh;padding:20px}
/* 按 UI 规范添加样式... */
</style></head><body>
<!-- 按 UI 规范添加 HTML 结构 -->
<script>
/* JavaScript 逻辑 */
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
```