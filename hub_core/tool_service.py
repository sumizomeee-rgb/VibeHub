"""One launch coordinator for both clients. No generation, registry or admin API."""
import asyncio
import logging

from hub_core.catalog import Catalog
from hub_core.process_manager import ToolRunner

log = logging.getLogger("vibehub.tools")


class ToolService:
    def __init__(self, catalog: Catalog, runner: ToolRunner, gateway):
        self.catalog = catalog
        self.runner = runner
        self.gateway = gateway
        self.tasks: dict[str, asyncio.Task] = {}
        self.states: dict[str, dict] = {}
        self.closing = False

    def view(self, tool_id: str) -> dict:
        tool = self.catalog.get(tool_id)
        state = self.states.get(tool_id, {"status": "idle", "message": ""})
        running = self.runner.running.get(tool_id)
        if state["status"] == "ready" and (not running or not running.alive):
            state = {"status": "error", "message": "工具已意外退出，请重新打开。"}
            self.states[tool_id] = state
        return {**tool.public(), **state}

    def open(self, tool_id: str) -> dict:
        self.catalog.get(tool_id)  # No unregistered paths can reach the runtime.
        if self.closing:
            raise RuntimeError("VibeHub 正在退出")
        state = self.view(tool_id)
        if state["status"] == "ready":
            return state
        task = self.tasks.get(tool_id)
        if not task or task.done():
            self.states[tool_id] = {"status": "starting", "message": "正在打开工具…"}
            self.tasks[tool_id] = asyncio.create_task(self._launch(tool_id), name=f"tool:{tool_id}")
        return self.view(tool_id)

    async def _launch(self, tool_id: str):
        try:
            await self.runner.stop(tool_id)
            await self.gateway.remove_route(tool_id)
            running = self.runner.start(self.catalog.get(tool_id))
            await self.runner.wait_ready(running)
            await self.gateway.add_route(tool_id, running.port)
            self.states[tool_id] = {"status": "ready", "message": ""}
        except asyncio.CancelledError:
            await self.runner.stop(tool_id)
            raise
        except Exception:
            log.exception("Failed to launch %s", tool_id)
            await self.runner.stop(tool_id)
            self.states[tool_id] = {"status": "error", "message": "工具启动失败，请重试；详细原因已记录到本机日志。"}

    async def close(self):
        self.closing = True
        for task in self.tasks.values():
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)
        await self.runner.close()
