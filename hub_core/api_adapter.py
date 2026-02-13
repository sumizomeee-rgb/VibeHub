"""
VibeHub API Adapter — REST + WebSocket 端点
为 React 前端提供所有后端功能的 HTTP 接口
"""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from hub_core import config, registry, process_manager, caddy_gateway
from hub_core.build_manager import create_build, get_task

log = logging.getLogger("vibehub.api")

router = APIRouter(prefix="/api")


# ---- Request Models ----

class RenameRequest(BaseModel):
    display_name: str

class BuildRequest(BaseModel):
    prompt: str
    edit_slug: str | None = None


# ---- Registry 相关 ----

@router.get("/tools")
async def list_tools():
    tools = registry.list_tools()
    for t in tools:
        t["alive"] = process_manager.is_tool_alive(t["slug"])
    return tools


@router.get("/tools/{slug}")
async def get_tool(slug: str):
    tool = registry.get_tool(slug)
    if not tool:
        raise HTTPException(404, "工具不存在")
    tool["alive"] = process_manager.is_tool_alive(slug)
    return tool


@router.delete("/tools/{slug}")
async def delete_tool(slug: str):
    process_manager.stop_tool(slug)
    await caddy_gateway.remove_route(slug)
    registry.unregister_tool(slug)
    return {"ok": True}


@router.patch("/tools/{slug}/rename")
async def rename_tool(slug: str, req: RenameRequest):
    ok = registry.rename_tool(slug, req.display_name)
    if not ok:
        raise HTTPException(404, "工具不存在")
    return {"ok": True}


@router.post("/tools/{slug}/click")
async def click_tool(slug: str):
    registry.increment_click(slug)
    return {"ok": True}


@router.get("/tools/{slug}/code")
async def get_tool_code(slug: str):
    script_path = config.PROJECTS_DIR / slug / "main.py"
    if not script_path.exists():
        raise HTTPException(404, "代码文件不存在")
    code = script_path.read_text(encoding="utf-8")
    return {"code": code}


@router.get("/tools/{slug}/logs")
async def get_tool_logs(slug: str, tail: int = 50):
    log_text = process_manager.get_tool_log(slug, tail=tail)
    return {"logs": log_text}


# ---- 进程控制 ----

@router.post("/tools/{slug}/start")
async def start_tool(slug: str):
    tool = registry.get_tool(slug)
    if not tool:
        raise HTTPException(404, "工具不存在")
    if process_manager.is_tool_alive(slug):
        return {"ok": True, "message": "已在运行"}
    try:
        pid, port = process_manager.start_tool(slug)
        ready = await process_manager.wait_for_tool_ready(slug, timeout=30.0)
        if ready:
            await caddy_gateway.add_route(slug, port)
            registry.set_status(slug, "active")
            return {"ok": True}
        else:
            registry.set_status(slug, "error")
            raise HTTPException(500, "启动后未就绪")
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.post("/tools/{slug}/stop")
async def stop_tool(slug: str):
    process_manager.stop_tool(slug)
    await caddy_gateway.remove_route(slug)
    registry.set_status(slug, "stopped")
    return {"ok": True}


@router.post("/tools/{slug}/restart")
async def restart_tool(slug: str):
    tool = registry.get_tool(slug)
    if not tool:
        raise HTTPException(404, "工具不存在")
    try:
        process_manager.stop_tool(slug)
        await caddy_gateway.remove_route(slug)
        pid, port = process_manager.start_tool(slug)
        ready = await process_manager.wait_for_tool_ready(slug, timeout=30.0)
        if ready:
            await caddy_gateway.add_route(slug, port)
            registry.set_status(slug, "active")
            return {"ok": True}
        else:
            registry.set_status(slug, "error")
            raise HTTPException(500, "重启后未就绪")
    except Exception as e:
        raise HTTPException(500, str(e))


# ---- 构建流程 ----

@router.post("/build")
async def start_build(req: BuildRequest):
    if not req.prompt.strip():
        raise HTTPException(400, "请输入需求描述")
    task = await create_build(req.prompt, req.edit_slug)
    return {"task_id": task.task_id}


# ---- WebSocket: 构建进度 ----

async def build_ws_endpoint(ws: WebSocket, task_id: str):
    """WebSocket /ws/build/{task_id} — 实时推送构建进度"""
    task = get_task(task_id)
    if not task:
        await ws.close(code=4004, reason="任务不存在")
        return

    await ws.accept()
    queue = task.subscribe()

    try:
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                await ws.send_json(msg)
                # 如果是终态消息，发完后关闭
                if msg["type"] in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                # 心跳保活
                await ws.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        pass
    finally:
        task.unsubscribe(queue)
