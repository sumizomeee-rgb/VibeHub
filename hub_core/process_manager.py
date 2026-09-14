"""Start PEP 723 tools; dependencies and HTTP servers remain isolated subprocesses."""
import asyncio
from dataclasses import dataclass
from pathlib import Path

import httpx

from hub_core.catalog import Catalog, ToolSpec
from hub_core.child_process import ChildProcess, clean_environment
from hub_core.config import Settings, resolve_executable
from hub_core.caddy_gateway import free_port


@dataclass
class RunningTool:
    child: ChildProcess
    port: int

    @property
    def alive(self) -> bool:
        return self.child.alive


class ToolRunner:
    def __init__(self, settings: Settings, catalog: Catalog):
        self.settings = settings
        self.catalog = catalog
        self.running: dict[str, RunningTool] = {}

    def start(self, tool: ToolSpec) -> RunningTool:
        directory = self.catalog.prepare(tool, self.settings)
        script = directory / "main.py"
        if not script.is_file():
            raise FileNotFoundError(script)
        port = free_port()
        env = clean_environment()
        data = self.settings.data_dir
        tool_data = data / "tools" / tool.id
        tool_data.mkdir(parents=True, exist_ok=True)
        env.update({"PORT": str(port), "DISPLAY_NAME": tool.name,
                    "PYTHONUNBUFFERED": "1", "UV_NO_PROGRESS": "1",
                    "UV_CACHE_DIR": str(data / "runtime/uv"),
                    "UV_PYTHON_INSTALL_DIR": str(data / "runtime/python"),
                    "UV_PYTHON": self.settings.tool_python,
                    "VIBEHUB_TOOL_DATA_DIR": str(tool_data)})
        command = [str(resolve_executable("uv", self.settings.bundle_dir)), "run", "--no-project"]
        if script.with_suffix(".py.lock").exists():
            command.append("--locked")
        command += ["--script", str(script)]
        child = ChildProcess(command, cwd=directory, env=env,
                             log_file=data / "logs/tools" / f"{tool.id}.log")
        result = RunningTool(child, port)
        self.running[tool.id] = result
        return result

    async def wait_ready(self, tool: RunningTool):
        deadline = asyncio.get_running_loop().time() + self.settings.startup_timeout
        async with httpx.AsyncClient(timeout=1, trust_env=False, follow_redirects=False) as client:
            while asyncio.get_running_loop().time() < deadline:
                if not tool.alive:
                    raise RuntimeError("工具进程提前退出")
                try:
                    response = await client.get(f"http://127.0.0.1:{tool.port}/")
                    if 200 <= response.status_code < 400:
                        return
                except httpx.HTTPError:
                    pass
                await asyncio.sleep(0.25)
        raise TimeoutError("准备运行环境或启动工具超时")

    async def stop(self, tool_id: str):
        running = self.running.pop(tool_id, None)
        if running:
            await asyncio.to_thread(running.child.stop)

    async def close(self):
        await asyncio.gather(*(self.stop(tool_id) for tool_id in list(self.running)))

    def emergency_stop(self):
        for running in list(self.running.values()):
            running.child.stop()
        self.running.clear()
