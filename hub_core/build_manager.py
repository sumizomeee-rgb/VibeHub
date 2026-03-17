"""
VibeHub Build Task Manager
将 builder.py 的 do_deploy() 逻辑抽取为异步任务 + WebSocket 推送
"""

import asyncio
import logging
import uuid
import traceback
from datetime import datetime
from pathlib import Path

from hub_core import config, registry, process_manager, caddy_gateway
from hub_core.claude_agent import run_agent_task
from hub_core.guard_agent import guard_check

log = logging.getLogger("vibehub.build")

_SNAPSHOT_DIR = config.DATA_DIR / "logs" / "snapshots"

# 活跃构建任务: task_id -> BuildTask
_tasks: dict[str, "BuildTask"] = {}

# per-slug 锁，防止并发构建同一工具
_build_locks: dict[str, asyncio.Lock] = {}


def _save_snapshot(slug: str, label: str, content: str):
    _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    path = _SNAPSHOT_DIR / f"{slug}_{ts}_{label}.py"
    path.write_text(content, encoding="utf-8")


class BuildTask:
    """一次构建任务的状态容器"""

    def __init__(self, task_id: str, prompt: str, edit_slug: str | None = None):
        self.task_id = task_id
        self.prompt = prompt
        self.edit_slug = edit_slug
        self.step = -1
        self.status = "pending"  # pending | running | complete | error
        self.messages: list[dict] = []
        self.result_data: dict | None = None
        self._listeners: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        # 发送历史消息
        for msg in self.messages:
            q.put_nowait(msg)
        self._listeners.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._listeners:
            self._listeners.remove(q)

    def _emit(self, msg: dict):
        self.messages.append(msg)
        for q in self._listeners:
            q.put_nowait(msg)

    def emit_step(self, step: int, message: str):
        self.step = step
        self._emit({"type": "step_change", "step": step, "message": message})

    def emit_log(self, message: str):
        self._emit({"type": "log", "message": message})

    def emit_complete(self, data: dict):
        self.status = "complete"
        self.result_data = data
        self._emit({"type": "complete", "data": data})

    def emit_error(self, message: str):
        self.status = "error"
        self._emit({"type": "error", "message": message})


async def _get_lock(slug: str) -> asyncio.Lock:
    if slug not in _build_locks:
        _build_locks[slug] = asyncio.Lock()
    return _build_locks[slug]


async def create_build(prompt: str, edit_slug: str | None = None) -> BuildTask:
    """创建并启动一个构建任务，返回 BuildTask"""
    task_id = uuid.uuid4().hex[:12]
    task = BuildTask(task_id, prompt, edit_slug)
    _tasks[task_id] = task
    asyncio.create_task(_run_build(task))
    return task


def get_task(task_id: str) -> BuildTask | None:
    return _tasks.get(task_id)


async def _run_build(task: BuildTask):
    """构建主流程（从 builder.py do_deploy 抽取）"""
    loop = asyncio.get_event_loop()
    task.status = "running"
    prompt = task.prompt
    edit_slug = task.edit_slug

    existing_tool = registry.get_tool(edit_slug) if edit_slug else None
    existing_code = ""
    if existing_tool:
        script_path = config.PROJECTS_DIR / edit_slug / "main.py"
        if script_path.exists():
            existing_code = script_path.read_text(encoding="utf-8")

    try:
        # Step 0: Guard 审核
        task.emit_step(0, "审核需求")
        if edit_slug:
            slug = edit_slug
            display_name = existing_tool.get("display_name", edit_slug) if existing_tool else edit_slug
            task.emit_log(f"✏️  编辑模式 → {display_name} ({slug})")
        else:
            task.emit_log("🔍  正在审核需求...")
            is_valid, guard_msg = await loop.run_in_executor(None, guard_check, prompt)
            if not is_valid:
                task.emit_log(f"❌  需求被拒绝：{guard_msg}")
                task.emit_error(f"需求被拒绝：{guard_msg}")
                return
            slug, display_name = guard_msg.split("|", 1)
            task.emit_log(f"✅  需求审核通过 → {display_name} ({slug})")

        # 获取 per-slug 锁
        lock = await _get_lock(slug)
        if lock.locked():
            task.emit_error(f"工具 {slug} 正在构建中，请稍后再试")
            return

        async with lock:
            await _run_build_locked(task, slug, display_name, prompt, existing_code, edit_slug)

    except Exception as e:
        log.error(f"Build error: {e}\n{traceback.format_exc()}")
        task.emit_log(f"❌  部署异常: {e}")
        task.emit_error(str(e)[:200])


async def _run_build_locked(task, slug, display_name, prompt, existing_code, edit_slug):
    """持有 slug 锁后的构建流程 (Agent 模式)

    Claude CLI 以 Agent 模式自主完成：代码生成 → 自测 → 修复 的完整闭环。
    Python 层仅负责：投放任务 → 透传日志 → 验证产物 → 部署服务。
    """

    # Step 1: Agent 自主构建（带重试机制）
    task.emit_step(1, "AI 构建中")

    def on_agent_output(line: str):
        """实时透传 Agent 日志到前端 WebSocket"""
        if len(line) > 500:
            line = line[:500] + "..."
        task.emit_log(f"  🔧 {line}")

    success = False
    for attempt in range(1, config.MAX_HEAL_RETRIES + 1):
        if attempt == 1:
            task.emit_log("🤖  Agent 正在自主构建工具...")
        else:
            task.emit_log(f"🔄  重试构建 (第 {attempt}/{config.MAX_HEAL_RETRIES} 次)...")

        success = await run_agent_task(
            slug=slug,
            user_request=prompt,
            existing_code=existing_code or None,
            on_output=on_agent_output,
        )

        if success:
            task.emit_log("✅  Agent 构建完成!")
            break

        if attempt < config.MAX_HEAL_RETRIES:
            task.emit_log(f"⚠️  构建失败，准备重试...")
            await asyncio.sleep(2)
        else:
            task.emit_log("❌  Agent 构建失败，已达最大重试次数")
            task.emit_error("Agent 构建失败，main.py 不存在或语法错误")
            return

    # Step 2: 启动服务
    task.emit_step(2, "启动服务")
    task.emit_log("🚀  正在启动工具...")

    # 编辑模式：备份旧代码
    backup_path = None
    if edit_slug:
        script_path = config.PROJECTS_DIR / slug / "main.py"
        backup_path = config.PROJECTS_DIR / slug / "main.py.backup"
        try:
            import shutil
            shutil.copy(script_path, backup_path)
            task.emit_log("💾  已备份当前版本")
        except Exception as e:
            log.warning(f"[{slug}] 备份失败: {e}")

        process_manager.stop_tool(edit_slug)
        await caddy_gateway.remove_route(edit_slug)

    pid, port = process_manager.start_tool(slug, display_name)
    ready = await process_manager.wait_for_tool_ready(slug, timeout=30.0)

    if not ready:
        err_log = process_manager.get_tool_log(slug, tail=20)
        task.emit_log(f"❌  工具启动失败:\n{err_log}")

        # 编辑模式：尝试回滚
        if edit_slug and backup_path and backup_path.exists():
            task.emit_log("🔄  正在回滚到旧版本...")
            try:
                import shutil
                shutil.copy(backup_path, script_path)
                process_manager.stop_tool(slug)
                pid, port = process_manager.start_tool(slug, display_name)
                ready = await process_manager.wait_for_tool_ready(slug, timeout=30.0)
                if ready:
                    await caddy_gateway.add_route(slug, port)
                    registry.set_status(slug, "active")
                    task.emit_error("新版本启动失败，已回滚到旧版本")
                else:
                    registry.set_status(slug, "error")
                    task.emit_error("回滚失败，工具无法启动")
            except Exception as e:
                log.error(f"[{slug}] 回滚失败: {e}")
                registry.set_status(slug, "error")
                task.emit_error(f"回滚失败: {str(e)[:100]}")
        else:
            if edit_slug:
                registry.set_status(slug, "error")
            task.emit_error("工具启动失败，请检查日志")
        return

    # Step 3: 注册路由
    task.emit_step(3, "注册路由")
    task.emit_log("🔗  正在注册网关路由...")
    await caddy_gateway.add_route(slug, port)

    # Step 4: 完成
    task.emit_step(4, "完成")
    registry.register_tool(slug, display_name, str(config.PROJECTS_DIR / slug / "main.py"))
    task.emit_log("✅  部署完成!")

    task.emit_complete({
        "slug": slug,
        "display_name": display_name,
        "url": f"/tools/{slug}/",
    })
