import asyncio
import logging
import sys

from nicegui import ui, app

from hub_core import config, registry, process_manager, caddy_gateway

# Log to both file and console
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


@app.on_startup
async def startup():
    log.info("VibeHub 启动中...")
    try:
        await caddy_gateway.init_server()
        log.info(f"Caddy 网关已初始化 → 0.0.0.0:{config.GATEWAY_PORT}")
    except Exception as e:
        log.error(f"Caddy 初始化失败: {e}")
        return

    await resurrect_all_tools()
    log.info("VibeHub 启动完成")


@app.on_shutdown
async def shutdown():
    log.info("VibeHub 关闭中...")
    process_manager.stop_all()
    await caddy_gateway.close()
    log.info("VibeHub 已关闭")


# ---- 页面路由 ----

@ui.page("/")
def dashboard_page():
    from hub_core.ui.dashboard import create_dashboard
    create_dashboard()


@ui.page("/builder")
def builder_page():
    from hub_core.ui.builder import create_builder
    create_builder()


@ui.page("/builder/{slug}")
def builder_edit_page(slug: str):
    from hub_core.ui.builder import create_builder
    create_builder(edit_slug=slug)


ui.run(
    host="127.0.0.1",
    port=config.HUB_INTERNAL_PORT,
    title="VibeHub",
    reload=False,
    show=False,
)
