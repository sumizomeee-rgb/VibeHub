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
<title>神威·头像切图工业化工具 V3</title>
<style>
:root{--primary:#cba186;--primary-hover:#b8906f;--bg:#f0f2f5;--card-bg:#fff;--border:#e8e8e8;--text-main:#333;--text-sub:#666;--text-light:#999}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);padding:20px;color:var(--text-main)}
.container{max-width:1400px;margin:0 auto}
.header{background:var(--card-bg);padding:20px 24px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.04);margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}
h1{font-size:22px;color:var(--text-main);display:flex;align-items:center;gap:8px}
.header-btns{display:flex;gap:12px}
.btn-primary{background:var(--primary);color:#fff;border:none;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;transition:all .2s;display:flex;align-items:center;gap:6px}
.btn-primary:hover{background:var(--primary-hover)}
.btn-secondary{background:#2c2c2c;color:#fff;border:none;padding:9px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600;transition:all .2s;display:flex;align-items:center;gap:6px}
.btn-secondary:hover{background:#000}
.btn-outline{background:transparent;color:var(--text-sub);border:1px solid var(--border);padding:6px 12px;border-radius:6px;cursor:pointer;font-size:13px;transition:all .2s;display:flex;align-items:center;gap:4px}
.btn-outline:hover{color:var(--primary);border-color:var(--primary);background:#fff3eb}

.workspace{background:var(--card-bg);padding:24px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.04);min-height:70vh}
.tabs{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:16px}
.tab-btn{padding:8px 20px;border-radius:20px;border:1px solid var(--border);background:#fff;color:var(--text-sub);cursor:pointer;font-size:14px;transition:all .2s;font-weight:500}
.tab-btn:hover{color:var(--primary);border-color:var(--primary)}
.tab-btn.active{background:var(--primary);color:#fff;border-color:var(--primary)}

.tab-toolbar{display:flex;justify-content:space-between;align-items:center;background:#fafbfc;padding:16px 20px;border-radius:12px;margin-bottom:24px;border:1px solid var(--border)}
.tab-status{display:flex;align-items:center;gap:12px;font-size:14px;color:var(--text-sub)}
.status-dot{width:10px;height:10px;border-radius:50%;background:#ccc}
.status-dot.active{background:#52c41a;box-shadow:0 0 0 3px rgba(82,196,26,.2)}
.img-preview-thumb{width:40px;height:40px;border-radius:6px;object-fit:cover;border:1px solid var(--border);background:#eee}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
.card{background:#fff;padding:20px;border-radius:16px;border:1px solid var(--border);display:flex;flex-direction:column;position:relative;transition:all .3s}
.card:hover{box-shadow:0 4px 20px rgba(0,0,0,.06);transform:translateY(-2px)}
.card.independent{border:1px solid var(--primary);box-shadow:0 4px 16px rgba(203,161,134,.1)}
.card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.card h3{font-size:16px;color:var(--text-main);font-weight:600;margin-bottom:4px}
.card p.sub{font-size:12px;color:var(--text-light);margin-bottom:16px}
.badge{background:#fff3eb;color:var(--primary);padding:4px 8px;border-radius:6px;font-size:12px;font-weight:600;display:flex;align-items:center;gap:4px}
.preview-wrap{position:relative;margin-bottom:16px}
.preview{width:100%;aspect-ratio:1;background:repeating-conic-gradient(#f4f4f4 0 25%,#fff 0 50%) 0 0/16px 16px;border-radius:8px;display:flex;align-items:center;justify-content:center;overflow:hidden;border:1px solid #eee}
.preview canvas{max-width:100%;max-height:100%;display:block;box-shadow:0 2px 8px rgba(0,0,0,.05)}
.card-actions{position:absolute;top:8px;right:8px;display:flex;gap:6px;z-index:10}
.action-btn{background:rgba(255,255,255,.9);color:#333;border:1px solid #ddd;width:28px;height:28px;border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);transition:all .2s}
.action-btn:hover{background:var(--primary);color:#fff;border-color:var(--primary)}
.info-row{display:flex;justify-content:space-between;font-size:12px;color:#555;background:#f8f9fa;padding:8px 12px;border-radius:6px;margin-bottom:6px}
.info-row span.label{color:var(--text-light)}
.info-row span.val{font-family:monospace;font-size:13px}

.empty-state{grid-column:1/-1;text-align:center;padding:60px 20px;color:var(--text-light);background:#fafbfc;border-radius:12px;border:2px dashed var(--border)}
.empty-state svg{margin-bottom:16px;opacity:0.5}

.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:1000;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.modal.active{display:flex}
.modal-content{background:var(--card-bg);border-radius:16px;padding:24px;width:95vw;max-width:1200px;height:90vh;display:flex;flex-direction:column;box-shadow:0 10px 40px rgba(0,0,0,.2)}
.modal-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-shrink:0}
.modal-title{font-size:18px;font-weight:600;display:flex;align-items:center;gap:8px}
.modal-tips{font-size:13px;color:var(--primary);background:#fff3eb;padding:6px 12px;border-radius:6px}
.modal-canvas-wrap{flex:1;position:relative;user-select:none;overflow:auto;border-radius:8px;background:repeating-conic-gradient(#f4f4f4 0 25%,#fff 0 50%) 0 0/16px 16px;border:1px solid var(--border);display:flex;align-items:center;justify-content:center;padding:100px}
.modal-img-container{position:relative;box-shadow:0 0 20px rgba(0,0,0,.1)}
.modal-img-container img{display:block;max-width:none;opacity:0.8}
.modal-crop-box{position:absolute;outline:2px solid var(--primary);cursor:move;box-shadow:0 0 0 9999px rgba(0,0,0,.5)}
.modal-grid{position:absolute;inset:0;pointer-events:none;border:1px solid rgba(255,255,255,.3)}
.modal-grid::before{content:'';position:absolute;top:33.3%;bottom:33.3%;left:0;right:0;border-top:1px dashed rgba(255,255,255,.5);border-bottom:1px dashed rgba(255,255,255,.5)}
.modal-grid::after{content:'';position:absolute;left:33.3%;right:33.3%;top:0;bottom:0;border-left:1px dashed rgba(255,255,255,.5);border-right:1px dashed rgba(255,255,255,.5)}
.modal-resize{position:absolute;right:-7px;bottom:-7px;width:14px;height:14px;background:var(--primary);border:2px solid #fff;border-radius:50%;cursor:nwse-resize;box-shadow:0 2px 4px rgba(0,0,0,.2)}
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
        头像切图工业化工具 V3
    </h1>
    <div class="header-btns" id="exportBtns">
        <button class="btn-primary" id="btnExportCategory">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            打包当前页签
        </button>
        <button class="btn-secondary" id="btnExportAll">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
            一键打包所有
        </button>
    </div>
</div>

<div class="workspace">
    <div class="tabs" id="tabsContainer"></div>
    
    <div class="tab-toolbar">
        <div class="tab-status" id="tabStatus">
            <div class="status-dot" id="statusDot"></div>
            <img class="img-preview-thumb" id="statusThumb" src="" style="display:none">
            <span id="statusText">当前页签未上传底图</span>
        </div>
        <div>
            <button class="btn-primary" onclick="document.getElementById('tabFileInput').click()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                上传/更换底图
            </button>
            <input type="file" id="tabFileInput" accept="image/*" style="display:none">
        </div>
    </div>

    <div class="grid" id="grid"></div>
</div>
</div>

<div class="modal" id="modal">
<div class="modal-content">
    <div class="modal-header">
        <div class="modal-title" id="modalTitle">编辑区域</div>
        <div class="modal-tips">✨ 提示：选框可以拖拽到图片外部，超出部分将自动补齐为透明底</div>
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
const rawData = [
    { category: '成就', resource: '成就配图', folder: 'IconTask', name: 'TaskIconR4Shenwei', sizeStr: '598*87' },
    { category: '基础头像', resource: '头像方-小', folder: 'Role', name: 'RoleHeadR4Shenwei1', sizeStr: '140*140' },
    { category: '基础头像', resource: '头像圆-小', folder: 'Role', name: 'RoleHeadR4Shenwei2', sizeStr: '140*140' },
    { category: '基础头像', resource: '头像方-大', folder: 'RoleCharacter', name: 'RoleHeadR4Shenwei1', sizeStr: '800*800' },
    { category: '基础头像', resource: '战队头像方-大', folder: 'RolePlayer', name: 'RoleHeadR4Shenwei1', sizeStr: '800*800' },
    { category: '终解头像', resource: '头像方-小', folder: 'Role', name: 'RoleHeadR4Shenwei3', sizeStr: '140*140' },
    { category: '终解头像', resource: '头像圆-小', folder: 'Role', name: 'RoleHeadR4Shenwei4', sizeStr: '140*140' },
    { category: '终解头像', resource: '头像方-大', folder: 'RoleCharacter', name: 'RoleHeadR4Shenwei3', sizeStr: '800*800' },
    { category: '终解头像', resource: '战队头像方-大', folder: 'RolePlayer', name: 'RoleHeadR4Shenwei3', sizeStr: '800*800' },
    { category: '终解头像', resource: '战队头像圆', folder: 'RolePlayerSp', name: 'RoleHeadR4Shenwei4', sizeStr: '256*256' },
    { category: 'Q版头像', resource: '头像方', folder: 'Role', name: 'RoleHeadR4Shenwei1Q', sizeStr: '140*140' },
    { category: 'Q版头像', resource: '头像圆', folder: 'Role', name: 'RoleHeadR4Shenwei2Q', sizeStr: '140*140' },
    { category: '道具图标', resource: '头像道具-大', folder: 'IconTools', name: 'RoleHeadR4Shenwei2', sizeStr: '256*256' },
    { category: '道具图标', resource: '头像道具-小', folder: 'IconToolsSp', name: 'RoleHeadR4Shenwei2Sp', sizeStr: '128*128' },
    { category: '道具图标', resource: '头像碎片-大', folder: 'IconTools', name: 'IconTools1061004', sizeStr: '256*256' },
    { category: '道具图标', resource: '头像碎片-小', folder: 'IconToolsSp', name: 'IconTools1061004Sp', sizeStr: '128*128' },
    { category: '半身', resource: '角色半身', folder: 'RoleCharacterBig', name: 'RoleCharacterBigR4ShenweiNormal01', sizeStr: '1000*1080' },
    { category: '初始基础涂装', resource: '基础涂装-大', folder: 'IconTools', name: 'Clo10610040101', sizeStr: '256*256' },
    { category: '初始基础涂装', resource: '基础涂装-小', folder: 'IconToolsSp', name: 'Clo10610040101Sp', sizeStr: '128*128' },
    { category: '初阶解放涂装', resource: '基础涂装-大', folder: 'IconTools', name: 'Clo10610040102', sizeStr: '256*256' },
    { category: '初阶解放涂装', resource: '基础涂装-小', folder: 'IconToolsSp', name: 'Clo10610040102Sp', sizeStr: '128*128' },
    { category: '高阶解放涂装', resource: '基础涂装-大', folder: 'IconTools', name: 'Clo10610040103', sizeStr: '256*256' },
    { category: '高阶解放涂装', resource: '基础涂装-小', folder: 'IconToolsSp', name: 'Clo10610040103Sp', sizeStr: '128*128' },
    { category: '伴生特效涂装', resource: '伴生涂装-大', folder: 'IconTools', name: 'Clo10610049011', sizeStr: '256*256' },
    { category: '伴生特效涂装', resource: '伴生涂装-小', folder: 'IconToolsSp', name: 'Clo10610049011', sizeStr: '128*128' },
    { category: '伴生特效涂装', resource: '伴生特效皮头像方-大', folder: 'RoleCharacter', name: 'RoleHeadR4Shenwei5', sizeStr: '800*800' },
    { category: '伴生特效涂装', resource: '伴生特效皮头像方-小', folder: 'Role', name: 'RoleHeadR4Shenwei5', sizeStr: '140*140' },
    { category: '伴生特效涂装', resource: '伴生特效皮战队头像-圆', folder: 'RolePlayerSp', name: 'RoleHeadR4Shenwei5', sizeStr: '256*256' }
];

let items = [];
let categories = [];
let currentCategory = '';

// V3 核心存储：按 Tab 分离图片和共享裁剪数据
let categoryData = {}; 

rawData.forEach(d => {
    let [w, h] = d.sizeStr.split('*').map(Number);
    let isSquare = (w === h);
    if (!categories.includes(d.category)) {
        categories.push(d.category);
        categoryData[d.category] = { img: null, sharedCrop: {x:0, y:0, w:100, h:100} };
    }
    items.push({
        ...d, w, h, isCircle: d.resource.includes('圆'), isSquare,
        localCropData: isSquare ? null : {x:0, y:0, w:100, h:100} // 非1:1独享
    });
});

const tabsContainer = document.getElementById('tabsContainer'), grid = document.getElementById('grid'),
statusDot = document.getElementById('statusDot'), statusText = document.getElementById('statusText'),
statusThumb = document.getElementById('statusThumb'), tabFileInput = document.getElementById('tabFileInput'),
modal = document.getElementById('modal'), modalImg = document.getElementById('modalImg'),
modalCropBox = document.getElementById('modalCropBox'), modalResize = document.getElementById('modalResize'),
modalConfirm = document.getElementById('modalConfirm'), modalCancel = document.getElementById('modalCancel'),
modalTitle = document.getElementById('modalTitle'), modalImgContainer = document.getElementById('modalImgContainer');

// 初始化页面
window.onload = () => {
    renderTabs();
    switchTab(categories[0]);
};

// 单页签传图逻辑
tabFileInput.onchange = e => {
    if(e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = ev => {
            const newImg = new Image();
            newImg.onload = () => {
                categoryData[currentCategory].img = newImg;
                initCropForCategory(currentCategory);
                updateToolbar();
                renderGrid();
            };
            newImg.src = ev.target.result;
        };
        reader.readAsDataURL(e.target.files[0]);
    }
};

function initCropForCategory(cat) {
    const img = categoryData[cat].img;
    // 初始化同Tab下的 1:1 共享选区
    let minSize = Math.min(img.width, img.height) * 0.7;
    categoryData[cat].sharedCrop = {
        x: (img.width - minSize) / 2, y: (img.height - minSize) / 2, w: minSize, h: minSize
    };
    // 初始化同Tab下非 1:1 的独立选区
    items.filter(i => i.category === cat && !i.isSquare).forEach(item => {
        let targetRatio = item.w / item.h;
        let imgRatio = img.width / img.height;
        let cw, ch;
        if (imgRatio > targetRatio) { ch = img.height * 0.8; cw = ch * targetRatio; }
        else { cw = img.width * 0.8; ch = cw / targetRatio; }
        item.localCropData = { x: (img.width - cw) / 2, y: (img.height - ch) / 2, w: cw, h: ch };
    });
}

function renderTabs() {
    tabsContainer.innerHTML = '';
    categories.forEach(cat => {
        let btn = document.createElement('button');
        btn.className = 'tab-btn';
        btn.innerText = cat;
        btn.onclick = () => switchTab(cat);
        tabsContainer.appendChild(btn);
    });
}

function switchTab(cat) {
    currentCategory = cat;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.innerText === cat));
    updateToolbar();
    renderGrid();
}

function updateToolbar() {
    const img = categoryData[currentCategory].img;
    if (img) {
        statusDot.classList.add('active');
        statusText.innerText = `已就绪 (${img.width}x${img.height})`;
        statusThumb.src = img.src;
        statusThumb.style.display = 'block';
    } else {
        statusDot.classList.remove('active');
        statusText.innerText = '当前页签未上传底图';
        statusThumb.style.display = 'none';
    }
}

function renderGrid() {
    grid.innerHTML = '';
    const currentItems = items.filter(i => i.category === currentCategory);
    const hasImg = !!categoryData[currentCategory].img;

    if (!hasImg) {
        grid.innerHTML = `
            <div class="empty-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                <h3>当前分类暂无图源</h3>
                <p style="margin-top:8px;font-size:14px">请点击上方按钮上传立绘底图</p>
            </div>
        `;
        return;
    }

    currentItems.forEach(item => {
        const card = document.createElement('div');
        card.className = `card ${!item.isSquare ? 'independent' : ''}`;
        
        const badgeHtml = !item.isSquare ? `<div class="badge">✨ 独立比例</div>` : '';

        // 包含编辑和单图下载按钮
        card.innerHTML = `
            <div class="card-header">
                <div><h3>${item.resource}</h3><p class="sub">${item.sizeStr} | ${item.isCircle?'圆形遮罩':'方形切图'}</p></div>
                ${badgeHtml}
            </div>
            <div class="preview-wrap">
                <div class="card-actions">
                    <button class="action-btn edit-btn" title="编辑区域"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>
                    <button class="action-btn dl-btn" title="单独下载"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg></button>
                </div>
                <div class="preview"><canvas></canvas></div>
            </div>
            <div class="info-row"><span class="label">文件夹</span> <span class="val">${item.folder}</span></div>
            <div class="info-row"><span class="label">文件名</span> <span class="val">${item.name}</span></div>
        `;
        const cv = card.querySelector('canvas');
        const maxDisplaySize = 240;
        let displayW, displayH;
        if(item.w > item.h) { displayW = maxDisplaySize; displayH = maxDisplaySize * (item.h/item.w); }
        else { displayH = maxDisplaySize; displayW = maxDisplaySize * (item.w/item.h); }
        cv.width = item.w; cv.height = item.h;
        cv.style.width = displayW + 'px'; cv.style.height = displayH + 'px';
        
        drawCanvas(cv, item, categoryData[currentCategory].img);
        
        card.querySelector('.edit-btn').onclick = () => openModal(item);
        card.querySelector('.dl-btn').onclick = () => exportSingle(item);
        grid.appendChild(card);
    });
}

// 核心渲染逻辑 (引入 Translate 矩阵，完美支持负坐标和透明溢出)
function drawCanvas(canvas, item, sourceImg) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, item.w, item.h);
    if (!sourceImg) return;

    const crop = item.isSquare ? categoryData[item.category].sharedCrop : item.localCropData;
    
    ctx.save();
    if (item.isCircle) {
        ctx.beginPath();
        ctx.arc(item.w/2, item.h/2, Math.min(item.w, item.h)/2, 0, Math.PI*2);
        ctx.clip();
    }
    
    // 矩阵映射算法：将源图缩放并平移，使选框区域(crop.x, crop.y)精准落在 Canvas 的 (0, 0)
    ctx.scale(item.w / crop.w, item.h / crop.h);
    ctx.translate(-crop.x, -crop.y);
    ctx.drawImage(sourceImg, 0, 0);
    ctx.restore();
}

// ---- 模态框交互逻辑 (无边界限制) ----
let activeItem = null;
let isDragging = false, isResizing = false;
let startMouseX, startMouseY, startCrop;
let tempCrop = {x:0, y:0, w:0, h:0};
// V3不再缩放原图，原尺寸渲染在模态框内，依靠CSS Overflow提供外围拖拽空间
let modalScale = 1; 

function openModal(item) {
    activeItem = item;
    const isGlobal = item.isSquare;
    modalTitle.innerHTML = isGlobal ? `编辑：${item.category} 共享选区 (1:1)` : `编辑：${item.resource} 独立选区 (${item.sizeStr})`;
    modalConfirm.innerText = isGlobal ? "保存共享选区 (应用至当前分类)" : "保存独立选区";
    
    const sourceCrop = isGlobal ? categoryData[item.category].sharedCrop : item.localCropData;
    tempCrop = { ...sourceCrop };
    
    modalImg.src = categoryData[item.category].img.src;
    modal.classList.add('active');
    
    // 强制按实际像素比例交互
    modalScale = 1;
    updateCropBoxDOM();
}

function updateCropBoxDOM() {
    modalCropBox.style.left = tempCrop.x + 'px';
    modalCropBox.style.top = tempCrop.y + 'px';
    modalCropBox.style.width = tempCrop.w + 'px';
    modalCropBox.style.height = tempCrop.h + 'px';
}

modalCropBox.onmousedown = e => {
    if(e.target === modalResize) isResizing = true;
    else isDragging = true;
    startMouseX = e.clientX;
    startMouseY = e.clientY;
    startCrop = { ...tempCrop };
    e.stopPropagation(); e.preventDefault();
};

window.onmousemove = e => {
    if(!isDragging && !isResizing) return;
    const dx = e.clientX - startMouseX;
    const dy = e.clientY - startMouseY;
    
    if (isDragging) {
        // V3：移除边界限制，允许选框超出图片
        tempCrop.x = startCrop.x + dx;
        tempCrop.y = startCrop.y + dy;
    } else if (isResizing) {
        const targetRatio = activeItem.isSquare ? 1 : (activeItem.w / activeItem.h);
        let nw = startCrop.w + dx;
        let nh = nw / targetRatio;
        if (nw > 20 && nh > 20) {
            tempCrop.w = nw; tempCrop.h = nh;
        }
    }
    updateCropBoxDOM();
};

window.onmouseup = () => { isDragging = false; isResizing = false; };

modalConfirm.onclick = () => {
    if (activeItem.isSquare) categoryData[activeItem.category].sharedCrop = { ...tempCrop };
    else activeItem.localCropData = { ...tempCrop };
    modal.classList.remove('active');
    renderGrid();
};
modalCancel.onclick = () => modal.classList.remove('active');

// ---- 单图及 ZIP 导出 ----
async function exportSingle(item) {
    const cv = document.createElement('canvas');
    cv.width = item.w; cv.height = item.h;
    drawCanvas(cv, item, categoryData[item.category].img);
    const blob = await new Promise(r => cv.toBlob(r));
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${item.name}.png`;
    a.click();
}

async function exportZip(itemsToExport, zipName) {
    // 过滤掉当前分类下没有上传底图的数据
    itemsToExport = itemsToExport.filter(i => !!categoryData[i.category].img);
    if(itemsToExport.length === 0) return alert("选中的分类没有底图数据，无法打包！");

    const zip = new JSZip();
    document.body.style.cursor = 'wait';

    for (let i = 0; i < itemsToExport.length; i++) {
        const item = itemsToExport[i];
        const cv = document.createElement('canvas');
        cv.width = item.w; cv.height = item.h;
        drawCanvas(cv, item, categoryData[item.category].img);
        const blob = await new Promise(r => cv.toBlob(r));
        zip.folder(item.folder).file(item.name + '.png', blob);
    }
    const content = await zip.generateAsync({type:'blob'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(content);
    a.download = zipName + '.zip';
    a.click();
    document.body.style.cursor = 'default';
}

document.getElementById('btnExportCategory').onclick = () => exportZip(items.filter(i => i.category === currentCategory), `神威_${currentCategory}_${Date.now()}`);
document.getElementById('btnExportAll').onclick = () => exportZip(items, `神威_全量资源_${Date.now()}`);
</script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))