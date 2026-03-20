# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn"]
# ///

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
TOOL_NAME = os.environ.get("DISPLAY_NAME") or "意识切图工具"


@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TOOL_NAME}}</title>
<style>
:root{--primary:#cba186;--primary-hover:#b8906f;--bg:#f0f2f5;--card-bg:#fff;--border:#e8e8e8;--text-main:#333;--text-sub:#666;--text-light:#999}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);padding:20px;color:var(--text-main)}
.container{max-width:1400px;margin:0 auto}
.header{background:var(--card-bg);padding:20px 24px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.04);margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}
h1{font-size:22px;color:var(--text-main);display:flex;align-items:center;gap:8px}
.btn-primary{background:var(--primary);color:#fff;border:none;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;transition:all .2s;display:flex;align-items:center;gap:6px}
.btn-primary:hover{background:var(--primary-hover)}
.btn-secondary{background:#2c2c2c;color:#fff;border:none;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;transition:all .2s;display:flex;align-items:center;gap:6px}
.btn-secondary:hover{background:#000}
.btn-outline{background:transparent;color:var(--text-sub);border:1px solid var(--border);padding:6px 12px;border-radius:6px;cursor:pointer;font-size:13px;transition:all .2s;display:flex;align-items:center;gap:4px}
.btn-outline:hover{color:var(--primary);border-color:var(--primary);background:#fff3eb}

.workspace{background:var(--card-bg);padding:24px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.04);min-height:70vh}
.slot-section{margin-bottom:28px}
.slot-section:last-child{margin-bottom:0}
.slot-header{display:flex;justify-content:space-between;align-items:center;background:#fafbfc;padding:14px 20px;border-radius:12px;margin-bottom:16px;border:1px solid var(--border);flex-wrap:wrap;gap:10px}
.slot-info{display:flex;align-items:center;gap:12px}
.slot-label{font-size:16px;font-weight:700;color:var(--text-main)}
.slot-dot{width:8px;height:8px;border-radius:50%;background:#ccc;flex-shrink:0}
.slot-dot.active{background:#52c41a;box-shadow:0 0 0 3px rgba(82,196,26,.2)}
.slot-thumb{width:36px;height:36px;border-radius:6px;object-fit:cover;border:1px solid var(--border);background:#eee}
.slot-status{font-size:13px;color:var(--text-light)}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}
.card{background:#fff;padding:20px;border-radius:16px;border:1px solid var(--border);display:flex;flex-direction:column;position:relative;transition:all .3s}
.card:hover{box-shadow:0 4px 20px rgba(0,0,0,.06);transform:translateY(-2px)}
.card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.card h3{font-size:16px;color:var(--text-main);font-weight:600;margin-bottom:4px}
.card p.sub{font-size:12px;color:var(--text-light);margin-bottom:16px}
.badge{background:#fff3eb;color:var(--primary);padding:4px 8px;border-radius:6px;font-size:12px;font-weight:600}
.preview-wrap{position:relative;margin-bottom:16px}
.preview{width:100%;aspect-ratio:1;background:repeating-conic-gradient(#f4f4f4 0 25%,#fff 0 50%) 0 0/16px 16px;border-radius:8px;display:flex;align-items:center;justify-content:center;overflow:hidden;border:1px solid #eee}
.preview canvas{max-width:100%;max-height:100%;display:block;box-shadow:0 2px 8px rgba(0,0,0,.05)}
.card-actions{position:absolute;top:8px;right:8px;display:flex;gap:6px;z-index:10}
.action-btn{background:rgba(255,255,255,.9);color:#333;border:1px solid #ddd;width:28px;height:28px;border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);transition:all .2s}
.action-btn:hover{background:var(--primary);color:#fff;border-color:var(--primary)}
.info-row{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#555;background:#f8f9fa;padding:8px 12px;border-radius:6px;margin-bottom:6px}
.info-row span.label{color:var(--text-light);flex-shrink:0}
.info-row span.val{font-family:monospace;font-size:13px;word-break:break-all;text-align:right}
.name-input{border:1px dashed var(--border);background:#fafbfc;font-family:monospace;font-size:13px;text-align:right;width:100%;color:var(--text-main);transition:all .2s;padding:2px 20px 2px 4px;border-radius:4px;outline:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2'%3E%3Cpath d='M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7'/%3E%3Cpath d='M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 4px center}
.name-input:hover,.name-input:focus{border-color:var(--primary);border-style:solid;background-color:#fff;box-shadow:0 0 0 2px rgba(203,161,134,.15)}

.empty-state{grid-column:1/-1;text-align:center;padding:40px 20px;color:var(--text-light);background:#fafbfc;border-radius:12px;border:2px dashed var(--border)}
.empty-state svg{margin-bottom:12px;opacity:.5}

.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:1000;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.modal.active{display:flex}
.modal-content{background:var(--card-bg);border-radius:16px;padding:24px;width:95vw;max-width:1200px;height:90vh;display:flex;flex-direction:column;box-shadow:0 10px 40px rgba(0,0,0,.2)}
.modal-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;flex-shrink:0;flex-wrap:wrap;gap:12px}
.modal-title{font-size:18px;font-weight:600;display:flex;align-items:center;gap:8px}
.modal-tips{font-size:13px;color:var(--primary);background:#fff3eb;padding:6px 12px;border-radius:6px;margin-top:8px;display:inline-block}
.modal-canvas-wrap{flex:1;min-height:0;position:relative;user-select:none;overflow:hidden;border-radius:8px;background:repeating-conic-gradient(#f4f4f4 0 25%,#fff 0 50%) 0 0/16px 16px;border:1px solid var(--border);display:flex;align-items:center;justify-content:center;padding:20px}
.modal-img-container{position:relative;display:inline-block;box-shadow:0 0 20px rgba(0,0,0,.1)}
.modal-img-container img{display:block;width:100%;height:100%;opacity:.8}
.modal-crop-box{position:absolute;outline:2px solid var(--primary);cursor:move;box-shadow:0 0 0 9999px rgba(0,0,0,.5)}
.modal-grid{position:absolute;inset:0;pointer-events:none;border:1px solid rgba(255,255,255,.3);z-index:10}
.modal-grid::before{content:'';position:absolute;top:33.3%;bottom:33.3%;left:0;right:0;border-top:1px dashed rgba(255,255,255,.5);border-bottom:1px dashed rgba(255,255,255,.5)}
.modal-grid::after{content:'';position:absolute;left:33.3%;right:33.3%;top:0;bottom:0;border-left:1px dashed rgba(255,255,255,.5);border-right:1px dashed rgba(255,255,255,.5)}
.modal-resize{position:absolute;right:-7px;bottom:-7px;width:14px;height:14px;background:var(--primary);border:2px solid #fff;border-radius:50%;cursor:nwse-resize;box-shadow:0 2px 4px rgba(0,0,0,.2);z-index:11}
.modal-btns{display:flex;gap:12px;justify-content:flex-end;margin-top:20px;flex-shrink:0}

@media(max-width:768px){.grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:480px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="container">
<div class="header">
    <h1>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
        {{TOOL_NAME}}
    </h1>
    <button class="btn-secondary" id="btnExportAll">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
        打包全部资源
    </button>
</div>

<div class="workspace">
    <div class="slot-section" id="slot0"></div>
    <div class="slot-section" id="slot1"></div>
    <div class="slot-section" id="slot2"></div>
</div>
</div>

<input type="file" id="fileInput" accept="image/*" style="display:none">

<div class="modal" id="modal">
<div class="modal-content">
    <div class="modal-header">
        <div>
            <div class="modal-title" id="modalTitle">编辑区域</div>
            <div class="modal-tips">提示：选框可以拖拽到图片外部，超出部分将自动补齐为透明底</div>
        </div>
    </div>
    <div class="modal-canvas-wrap" id="modalWrap">
        <div class="modal-img-container" id="modalImgContainer">
            <img id="modalImg" src="">
            <div class="modal-crop-box" id="modalCropBox">
                <div class="modal-grid"></div>
                <div class="modal-resize" id="modalResize"></div>
            </div>
        </div>
    </div>
    <div class="modal-btns">
        <button class="btn-outline" id="modalCancel">取消编辑</button>
        <button class="btn-primary" id="modalConfirm">保存裁剪选区</button>
    </div>
</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script>
const ITEMS = [
    { id: 'fullBody',   label: '完整立绘', w: 1140, h: 1440, folder: 'RoleWaferLihui', cropKey: 'fullBody',   ratio: 1140/1440 },
    { id: 'wideBanner', label: '宽版头像', w: 504,  h: 225,  folder: 'RoleWaferBag',   cropKey: 'wideBanner', ratio: 504/225 },
    { id: 'closeup256', label: '描边特写', w: 256,  h: 256,  folder: 'IconTools',      cropKey: 'closeup',    ratio: 146/205, hasStroke: true },
    { id: 'closeup128', label: '缩放特写', w: 128,  h: 128,  folder: 'IconToolsSp',    cropKey: 'closeup',    ratio: 146/205, isDownsample: true }
];

const SLOT_COUNT = 3;
const slots = [];
for (let i = 0; i < SLOT_COUNT; i++) {
    slots.push({
        img: null, baseName: '',
        cropData: {
            fullBody:   { x: 0, y: 0, w: 100, h: 100 },
            wideBanner: { x: 0, y: 0, w: 100, h: 100 },
            closeup:    { x: 0, y: 0, w: 100, h: 100 }
        },
        names: { fullBody: '', wideBanner: '', closeup256: '', closeup128: '' }
    });
}

const fileInput = document.getElementById('fileInput'),
modal = document.getElementById('modal'), modalImg = document.getElementById('modalImg'),
modalCropBox = document.getElementById('modalCropBox'), modalResize = document.getElementById('modalResize'),
modalConfirm = document.getElementById('modalConfirm'), modalCancel = document.getElementById('modalCancel'),
modalTitle = document.getElementById('modalTitle'), modalImgContainer = document.getElementById('modalImgContainer');

let uploadingSlotIdx = -1;

window.onload = () => { for (let i = 0; i < SLOT_COUNT; i++) renderSlot(i); };

// ---- 上传 ----
function triggerUpload(idx) { uploadingSlotIdx = idx; fileInput.click(); }

fileInput.onchange = e => {
    if (!e.target.files[0] || uploadingSlotIdx < 0) return;
    const idx = uploadingSlotIdx;
    const file = e.target.files[0];
    const base = file.name.replace(/\\.[^.]+$/, '');
    slots[idx].baseName = base;
    setSlotNames(idx, base);
    const reader = new FileReader();
    reader.onload = ev => {
        const img = new Image();
        img.onload = () => { slots[idx].img = img; initCrops(idx); renderSlot(idx); };
        img.src = ev.target.result;
    };
    reader.readAsDataURL(file);
    fileInput.value = '';
};

function setSlotNames(idx, base) {
    const n = slots[idx].names;
    n.fullBody = base;
    n.wideBanner = base + 'Bag';
    n.closeup256 = base;
    n.closeup128 = base + 'Sp';
}

function initCrops(idx) {
    const img = slots[idx].img, cd = slots[idx].cropData;
    let fbR = 1140/1440, fbH = img.height * 0.9, fbW = fbH * fbR;
    if (fbW > img.width * 0.9) { fbW = img.width * 0.9; fbH = fbW / fbR; }
    cd.fullBody = { x: (img.width - fbW) / 2, y: (img.height - fbH) / 2, w: fbW, h: fbH };

    let wbR = 504/225, wbW = img.width * 0.8, wbH = wbW / wbR;
    if (wbH > img.height * 0.4) { wbH = img.height * 0.4; wbW = wbH * wbR; }
    cd.wideBanner = { x: (img.width - wbW) / 2, y: img.height * 0.05, w: wbW, h: wbH };

    let cuR = 146/205, cuH = img.height * 0.35, cuW = cuH * cuR;
    if (cuW > img.width * 0.6) { cuW = img.width * 0.6; cuH = cuW / cuR; }
    cd.closeup = { x: (img.width - cuW) / 2, y: img.height * 0.02, w: cuW, h: cuH };
}

// ---- 槽位渲染 ----
function renderSlot(idx) {
    const slot = slots[idx];
    const section = document.getElementById('slot' + idx);
    section.innerHTML = '';

    // 槽位标题栏
    const hdr = document.createElement('div');
    hdr.className = 'slot-header';
    let infoHtml = '<div class="slot-info"><div class="slot-dot' + (slot.img ? ' active' : '') + '"></div>' +
        '<span class="slot-label">立绘 ' + (idx + 1) + '</span>';
    if (slot.img) {
        infoHtml += '<img class="slot-thumb" src="' + slot.img.src + '">' +
            '<span class="slot-status">' + slot.img.width + 'x' + slot.img.height + ' - ' + slot.baseName + '</span>';
    } else {
        infoHtml += '<span class="slot-status">未上传</span>';
    }
    infoHtml += '</div>';
    hdr.innerHTML = infoHtml;
    const btn = document.createElement('button');
    btn.className = 'btn-primary';
    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> 上传/更换';
    btn.onclick = () => triggerUpload(idx);
    hdr.appendChild(btn);
    section.appendChild(hdr);

    // 网格
    const gridEl = document.createElement('div');
    gridEl.className = 'grid';
    if (!slot.img) {
        gridEl.innerHTML = '<div class="empty-state">' +
            '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>' +
            '<p>点击上方按钮上传立绘原图</p></div>';
    } else {
        ITEMS.forEach(item => gridEl.appendChild(buildCard(idx, item)));
    }
    section.appendChild(gridEl);
}

function buildCard(slotIdx, item) {
    const slot = slots[slotIdx];
    const card = document.createElement('div');
    card.className = 'card';
    const syncBadge = (item.cropKey === 'closeup') ? '<div class="badge">Sync</div>' : '';
    const strokeLabel = item.hasStroke ? ' | 4px描边' : '';

    card.innerHTML =
        '<div class="card-header">' +
            '<div><h3>' + item.label + '</h3><p class="sub">' + item.w + 'x' + item.h + strokeLabel + '</p></div>' +
            syncBadge +
        '</div>' +
        '<div class="preview-wrap">' +
            '<div class="card-actions">' +
                '<button class="action-btn edit-btn" title="编辑区域"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>' +
                '<button class="action-btn dl-btn" title="单独下载"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg></button>' +
            '</div>' +
            '<div class="preview"><canvas></canvas></div>' +
        '</div>' +
        '<div class="info-row"><span class="label">文件夹</span> <span class="val">' + item.folder + '</span></div>' +
        '<div class="info-row"><span class="label">文件名</span> ' +
            '<input type="text" class="name-input" value="' + (slot.names[item.id] || '') + '" title="点击修改打包输出的文件名">' +
        '</div>';

    card.querySelector('.name-input').onchange = e => {
        const v = e.target.value.trim();
        if (v) slot.names[item.id] = v; else e.target.value = slot.names[item.id];
    };

    const cv = card.querySelector('canvas');
    const maxD = 260;
    let dW, dH;
    if (item.w > item.h) { dW = maxD; dH = maxD * (item.h / item.w); }
    else { dH = maxD; dW = maxD * (item.w / item.h); }
    cv.width = item.w; cv.height = item.h;
    cv.style.width = dW + 'px'; cv.style.height = dH + 'px';
    drawCanvas(cv, item, slot.img, slot.cropData);

    card.querySelector('.edit-btn').onclick = () => openModal(slotIdx, item);
    card.querySelector('.dl-btn').onclick = () => exportSingle(slotIdx, item);
    return card;
}

// ---- 渲染核心 ----
function extractCropRegion(src, crop) {
    const cw = Math.ceil(crop.w), ch = Math.ceil(crop.h);
    const MAX = 268435456;
    let sw = cw, sh = ch;
    if (sw * sh > MAX) { const s = Math.sqrt(MAX / (sw * sh)); sw = Math.floor(sw * s); sh = Math.floor(sh * s); }
    const off = document.createElement('canvas');
    off.width = sw; off.height = sh;
    const c = off.getContext('2d');
    c.imageSmoothingEnabled = true; c.imageSmoothingQuality = 'high';
    const sx = Math.max(0, crop.x), sy = Math.max(0, crop.y);
    const sx2 = Math.min(src.naturalWidth || src.width, crop.x + crop.w);
    const sy2 = Math.min(src.naturalHeight || src.height, crop.y + crop.h);
    if (sx2 > sx && sy2 > sy) {
        const scX = sw / crop.w, scY = sh / crop.h;
        c.drawImage(src, sx, sy, sx2 - sx, sy2 - sy, (sx - crop.x) * scX, (sy - crop.y) * scY, (sx2 - sx) * scX, (sy2 - sy) * scY);
    }
    return { canvas: off, w: sw, h: sh };
}

function stepDown(srcCv, curW, curH, tW, tH) {
    while (curW > tW * 2 || curH > tH * 2) {
        let nW = Math.max(Math.ceil(curW * 0.5), tW), nH = Math.max(Math.ceil(curH * 0.5), tH);
        let t = document.createElement('canvas'); t.width = nW; t.height = nH;
        let tc = t.getContext('2d'); tc.imageSmoothingEnabled = true; tc.imageSmoothingQuality = 'high';
        tc.drawImage(srcCv, 0, 0, curW, curH, 0, 0, nW, nH);
        srcCv = t; curW = nW; curH = nH;
    }
    return { canvas: srcCv, w: curW, h: curH };
}

function drawCanvas(canvas, item, src, cd) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, item.w, item.h);
    if (!src) return;
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    const crop = cd[item.cropKey];

    if (item.isDownsample) {
        const tmp = document.createElement('canvas'); tmp.width = 256; tmp.height = 256;
        const ref = ITEMS.find(i => i.id === 'closeup256');
        drawCanvas(tmp, ref, src, cd);
        ctx.drawImage(tmp, 0, 0, 256, 256, 0, 0, 128, 128);
        return;
    }

    if (item.hasStroke) {
        const cW = 146, cH = 205, cX = 55, cY = 25.5, sw = 4;
        let { canvas: sc, w: cw, h: ch } = extractCropRegion(src, crop);
        ({ canvas: sc, w: cw, h: ch } = stepDown(sc, cw, ch, cW, cH));
        ctx.drawImage(sc, 0, 0, cw, ch, cX, cY, cW, cH);
        ctx.fillStyle = '#000';
        ctx.fillRect(cX, cY, cW, sw);
        ctx.fillRect(cX, cY + cH - sw, cW, sw);
        ctx.fillRect(cX, cY, sw, cH);
        ctx.fillRect(cX + cW - sw, cY, sw, cH);
        return;
    }

    let { canvas: sc, w: cw, h: ch } = extractCropRegion(src, crop);
    ({ canvas: sc, w: cw, h: ch } = stepDown(sc, cw, ch, item.w, item.h));
    ctx.drawImage(sc, 0, 0, cw, ch, 0, 0, item.w, item.h);
}

// ---- 模态框 ----
let activeSlotIdx = -1, activeItem = null;
let isDragging = false, isResizing = false;
let startMouseX, startMouseY, startCrop;
let tempCrop = { x: 0, y: 0, w: 0, h: 0 };
let visualRatio = 1;

function updateVisualRatio() {
    if (!modal.classList.contains('active') || !modalImg.naturalWidth) return;
    visualRatio = modalImg.clientWidth / modalImg.naturalWidth;
    updateCropBoxDOM();
}

window.addEventListener('resize', () => { if (modal.classList.contains('active')) fitModalImage(); });

function fitModalImage() {
    const wrap = document.getElementById('modalWrap');
    const r = wrap.getBoundingClientRect();
    const aW = r.width - 40, aH = r.height - 40;
    const nW = modalImg.naturalWidth, nH = modalImg.naturalHeight;
    if (!nW || !nH || aW <= 0 || aH <= 0) return;
    const ratio = Math.min(aW / nW, aH / nH, 1);
    modalImgContainer.style.width = Math.floor(nW * ratio) + 'px';
    modalImgContainer.style.height = Math.floor(nH * ratio) + 'px';
    updateVisualRatio();
}

function openModal(slotIdx, item) {
    activeSlotIdx = slotIdx; activeItem = item;
    const slot = slots[slotIdx];
    modalTitle.innerHTML = '立绘 ' + (slotIdx + 1) + ' - ' + item.label + ' (' + item.w + 'x' + item.h + ')';
    modalConfirm.innerText = item.cropKey === 'closeup' ? '保存选区 (同步描边/缩放特写)' : '保存选区';
    tempCrop = { ...slot.cropData[item.cropKey] };
    modal.classList.add('active');
    requestAnimationFrame(() => {
        if (modalImg.src === slot.img.src && modalImg.naturalWidth) fitModalImage();
        else { modalImg.onload = () => fitModalImage(); modalImg.src = slot.img.src; }
    });
}

function updateCropBoxDOM() {
    modalCropBox.style.left = (tempCrop.x * visualRatio) + 'px';
    modalCropBox.style.top = (tempCrop.y * visualRatio) + 'px';
    modalCropBox.style.width = (tempCrop.w * visualRatio) + 'px';
    modalCropBox.style.height = (tempCrop.h * visualRatio) + 'px';
}

modalCropBox.onmousedown = e => {
    if (e.target === modalResize) isResizing = true; else isDragging = true;
    startMouseX = e.clientX; startMouseY = e.clientY;
    startCrop = { ...tempCrop };
    e.stopPropagation(); e.preventDefault();
};

window.onmousemove = e => {
    if (!isDragging && !isResizing) return;
    const dx = (e.clientX - startMouseX) / visualRatio;
    const dy = (e.clientY - startMouseY) / visualRatio;
    if (isDragging) { tempCrop.x = startCrop.x + dx; tempCrop.y = startCrop.y + dy; }
    else if (isResizing) {
        let nw = startCrop.w + dx, nh = nw / activeItem.ratio;
        if (nw > 20 && nh > 20) { tempCrop.w = nw; tempCrop.h = nh; }
    }
    updateCropBoxDOM();
};

window.onmouseup = () => { isDragging = false; isResizing = false; };

modalConfirm.onclick = () => {
    slots[activeSlotIdx].cropData[activeItem.cropKey] = { ...tempCrop };
    modal.classList.remove('active');
    renderSlot(activeSlotIdx);
};
modalCancel.onclick = () => modal.classList.remove('active');

// ---- 导出 ----
async function exportSingle(slotIdx, item) {
    const slot = slots[slotIdx];
    const cv = document.createElement('canvas'); cv.width = item.w; cv.height = item.h;
    drawCanvas(cv, item, slot.img, slot.cropData);
    const blob = await new Promise(r => cv.toBlob(r));
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = (slot.names[item.id] || item.label) + '.png';
    a.click();
}

async function exportAll() {
    const hasAny = slots.some(s => s.img);
    if (!hasAny) return alert('请先上传至少一张立绘！');
    const zip = new JSZip();
    document.body.style.cursor = 'wait';
    for (let i = 0; i < SLOT_COUNT; i++) {
        const slot = slots[i];
        if (!slot.img) continue;
        for (const item of ITEMS) {
            const cv = document.createElement('canvas'); cv.width = item.w; cv.height = item.h;
            drawCanvas(cv, item, slot.img, slot.cropData);
            const blob = await new Promise(r => cv.toBlob(r));
            zip.folder(item.folder).file((slot.names[item.id] || item.label) + '.png', blob);
        }
    }
    const content = await zip.generateAsync({ type: 'blob' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(content);
    a.download = '意识_全量资源_' + Date.now() + '.zip';
    a.click();
    document.body.style.cursor = 'default';
}

document.getElementById('btnExportAll').onclick = exportAll;
</script>
</body>
</html>""".replace("{{TOOL_NAME}}", TOOL_NAME)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
