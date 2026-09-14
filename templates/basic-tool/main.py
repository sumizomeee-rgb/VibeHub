# /// script
# requires-python = ">=3.12"
# dependencies = ["fastapi", "uvicorn"]
# ///
"""Copy this directory to projects/<id>, then add one ToolSpec to tools.json."""
import html
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
NAME = os.environ.get("DISPLAY_NAME") or "新工具"


@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__NAME__</title>
<style>body{font-family:system-ui;background:#f0f2f5;color:#222;padding:24px}
main{max-width:900px;margin:auto;background:white;padding:28px;border-radius:16px}</style>
</head><body><main><h1>__NAME__</h1><p>在这里实现工具功能。返回首页由外层 ToolHost 统一提供。</p>
<button id="run">运行示例</button><pre id="result"></pre></main>
<script>document.getElementById('run').onclick=async()=>{
const result=await fetch('api/example');
document.getElementById('result').textContent=JSON.stringify(await result.json(),null,2);
};</script></body></html>""".replace("__NAME__", html.escape(NAME))


@app.get("/api/example")
async def example():
    return {"message": "工具已就绪"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "8000")))
