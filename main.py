import asyncio
import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from hub_core import config, registry, process_manager, caddy_gateway
from hub_core.api_adapter import router as api_router, build_ws_endpoint

# ---- Logging ----
log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
file_handler = logging.FileHandler(str(config.DATA_DIR / "logs" / "hub.log"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter(log_format))
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format))

root_logger = logging.getLogger("vibehub")
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)
log = root_logger


async def resurrect_all_tools():
    """启动恢复：拉起所有 registry 中 active 或 error 的工具"""
    tools = registry.list_tools()
    recoverable = [t for t in tools if t.get("status") in ("active", "error")]

    if not recoverable:
        log.info("没有需要恢复的工具")
        return

    log.info(f"开始恢复 {len(recoverable)} 个工具...")

    for tool in recoverable:
        slug = tool["slug"]
        try:
            pid, port = process_manager.start_tool(slug)
            ready = await process_manager.wait_for_tool_ready(slug, timeout=30.0)

            if ready:
                await caddy_gateway.add_route(slug, port)
                log.info(f"[{slug}] 恢复成功 → localhost:{port}")
            else:
                registry.set_status(slug, "error")
                log.warning(f"[{slug}] 启动后未就绪，标记为 error")
        except Exception as e:
            registry.set_status(slug, "error")
            log.error(f"[{slug}] 恢复失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    log.info("VibeHub 启动中...")
    try:
        await caddy_gateway.init_server()
        log.info(f"Caddy 网关已初始化 → 0.0.0.0:{config.GATEWAY_PORT}")
    except Exception as e:
        log.error(f"Caddy 初始化失败: {e}")

    await resurrect_all_tools()
    log.info("VibeHub 启动完成")
    yield
    # Shutdown
    log.info("VibeHub 关闭中...")
    process_manager.stop_all()
    await caddy_gateway.close()
    log.info("VibeHub 已关闭")


app = FastAPI(lifespan=lifespan)

# 1. API Router（最先挂载）
app.include_router(api_router)

# 2. WebSocket 端点
app.add_api_websocket_route("/ws/build/{task_id}", build_ws_endpoint)

# 3. SPA 静态文件（最后挂载）
_DIST_DIR = Path(__file__).parent / "frontend" / "dist"

if _DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(_DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        """SPA fallback: 所有非 API/WS 路径返回 index.html"""
        file_path = _DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_DIST_DIR / "index.html"))
else:
    @app.get("/")
    async def no_frontend():
        return {"error": "前端未构建，请执行 cd frontend && npm run build"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=config.HUB_INTERNAL_PORT)
