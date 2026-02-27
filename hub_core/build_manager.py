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
from hub_core.claude_agent import generate_tool_code, fix_tool_code, generate_test_code, run_test, _check_syntax
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
    """持有 slug 锁后的构建流程"""
    loop = asyncio.get_event_loop()

    # Step 1: 生成代码
    task.emit_step(1, "生成代码")
    task.emit_log("🤖  正在调用 AI 生成代码...")
    code = await loop.run_in_executor(None, generate_tool_code, prompt, existing_code or None)
    task.emit_log(f"✅  代码生成完成 ({len(code)} 字符)")
    _save_snapshot(slug, "gen", code)

    # Step 2: 单元测试
    task.emit_step(2, "单元测试")
    task.emit_log("🧪  正在生成测试脚本...")
    test_code = await loop.run_in_executor(None, generate_test_code, code)
    _save_snapshot(slug, "test", test_code)
    task.emit_log("🧪  正在执行测试...")

    tool_dir = config.PROJECTS_DIR / slug
    tool_dir.mkdir(parents=True, exist_ok=True)
    script_path = tool_dir / "main.py"
    script_path.write_text(code, encoding="utf-8")

    passed, test_log = await loop.run_in_executor(None, run_test, slug, test_code)

    # 自愈循环
    retries = 0
    while not passed and retries < config.MAX_HEAL_RETRIES:
        retries += 1

        # 判断错误来源：测试脚本自身语法错误 vs 工具代码问题
        is_test_script_error = "_test_main.py" in test_log and "SyntaxError" in test_log

        if is_test_script_error:
            task.emit_log(f"⚠️  测试脚本语法错误，重新生成测试 (第{retries}次)")
            test_code = await loop.run_in_executor(None, generate_test_code, code)
        else:
            task.emit_log(f"⚠️  测试未通过 (第{retries}次修复中...)")
            task.emit_log(f"    错误: {test_log[:200]}")
            code = await loop.run_in_executor(None, fix_tool_code, code, test_log)
            _save_snapshot(slug, f"fix{retries}", code)
            script_path.write_text(code, encoding="utf-8")
            test_code = await loop.run_in_executor(None, generate_test_code, code)

        passed, test_log = await loop.run_in_executor(None, run_test, slug, test_code)

    if passed:
        task.emit_log("✅  测试通过!")
    else:
        task.emit_log(f"⚠️  测试仍未通过（已重试{config.MAX_HEAL_RETRIES}次），继续部署...")

    # Step 3: 启动服务
    task.emit_step(3, "启动服务")
    task.emit_log("🚀  正在启动工具...")

    if edit_slug:
        process_manager.stop_tool(edit_slug)
        await caddy_gateway.remove_route(edit_slug)

    pid, port = process_manager.start_tool(slug)
    ready = await process_manager.wait_for_tool_ready(slug, timeout=30.0)

    if not ready:
        err_log = process_manager.get_tool_log(slug, tail=20)
        task.emit_log(f"❌  工具启动失败:\n{err_log}")
        if edit_slug:
            registry.set_status(slug, "error")
        task.emit_error("工具启动失败，请检查日志")
        return

    # Step 4: 注册路由
    task.emit_step(4, "注册路由")
    task.emit_log("🔗  正在注册网关路由...")
    await caddy_gateway.add_route(slug, port)

    # Step 5: 完成
    task.emit_step(5, "完成")
    registry.register_tool(slug, display_name, str(config.PROJECTS_DIR / slug / "main.py"))
    task.emit_log("✅  部署完成!")

    task.emit_complete({
        "slug": slug,
        "display_name": display_name,
        "url": f"/tools/{slug}/",
    })
