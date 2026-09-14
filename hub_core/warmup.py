"""Resolve every tool's dependencies before anyone asks for a tool.

A fresh install has no package cache. Without this, the first launch of each tool
downloads a managed Python interpreter and every wheel from inside the request, so
the user sees an install step that the web deployment never shows.

The desktop build ships no cache, so the same resolution the runner performs is
done here instead, in the background, against the identical directories. A later
tool launch then finds everything already local and starts immediately.
"""
import asyncio
import logging
from pathlib import Path
from typing import Callable

from hub_core.catalog import Catalog
from hub_core.child_process import ChildProcess
from hub_core.config import Settings, resolve_executable
from hub_core.process_manager import tool_environment

log = logging.getLogger("vibehub.warmup")


def prepare_command(settings: Settings, script: Path) -> list[str]:
    command = [str(resolve_executable("uv", settings.bundle_dir)), "sync", "--script", str(script)]
    if script.with_suffix(".py.lock").exists():
        command.append("--locked")
    return command


class Warmer:
    """Own one cancellable dependency-preparation task."""

    def __init__(self, settings: Settings, catalog: Catalog,
                 process_factory: Callable = ChildProcess):
        self.settings = settings
        self.catalog = catalog
        self.process_factory = process_factory
        self.task: asyncio.Task | None = None
        self.child: ChildProcess | None = None
        self.closing = False

    def start(self):
        if not self.settings.warmup or self.task is not None:
            return
        self.closing = False
        self.task = asyncio.create_task(self._run(), name="vibehub:warmup")

    async def _run(self):
        for tool in self.catalog.tools:
            if self.closing:
                return
            try:
                directory = self.catalog.prepare(tool, self.settings)
                script = directory / "main.py"
                if not script.is_file():
                    continue
                child = self.process_factory(
                    prepare_command(self.settings, script), cwd=directory,
                    env=tool_environment(self.settings, tool.id),
                    log_file=self.settings.data_dir / "logs/warmup.log")
                self.child = child
                try:
                    deadline = asyncio.get_running_loop().time() + self.settings.startup_timeout
                    while child.alive and asyncio.get_running_loop().time() < deadline:
                        await asyncio.sleep(0.1)
                    if child.alive:
                        log.warning("Timed out preparing %s", tool.id)
                    elif child.process.returncode:
                        log.warning("Dependency preparation failed for %s with exit code %s",
                                    tool.id, child.process.returncode)
                    else:
                        log.info("Prepared dependencies for %s", tool.id)
                finally:
                    child.stop()
                    self.child = None
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Failed to prepare %s", tool.id)

    async def close(self):
        self.closing = True
        task = self.task
        self.task = None
        if task and not task.done():
            task.cancel()
        if task:
            await asyncio.gather(task, return_exceptions=True)
