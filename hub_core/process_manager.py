import asyncio
import logging
import os
import subprocess
from pathlib import Path

import psutil

from hub_core.config import UV_EXE, LOGS_DIR, PROJECTS_DIR
from hub_core.port_manager import find_free_port

log = logging.getLogger("vibehub.process")

# 运行时状态：slug → {pid, port, process}
_running_tools: dict[str, dict] = {}


def start_tool(slug: str) -> tuple[int, int]:
    """启动工具子进程，返回 (pid, port)"""
    script_path = PROJECTS_DIR / slug / "main.py"
    if not script_path.exists():
        raise FileNotFoundError(f"工具脚本不存在: {script_path}")

    port = find_free_port()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{slug}.log"

    env = {**os.environ, "PORT": str(port)}
    proc = subprocess.Popen(
        [str(UV_EXE), "run", str(script_path)],
        env=env,
        stdout=open(log_file, "w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        cwd=str(script_path.parent),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    _running_tools[slug] = {"pid": proc.pid, "port": port, "process": proc}
    log.info(f"[{slug}] Started pid={proc.pid} port={port}")
    return proc.pid, port


def stop_tool(slug: str):
    """停止工具子进程（含子进程树）"""
    info = _running_tools.pop(slug, None)
    if not info:
        return
    pid = info["pid"]
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
        log.info(f"[{slug}] Stopped pid={pid}")
    except psutil.NoSuchProcess:
        log.info(f"[{slug}] Already dead pid={pid}")


def restart_tool(slug: str) -> tuple[int, int]:
    stop_tool(slug)
    return start_tool(slug)


def is_tool_alive(slug: str) -> bool:
    info = _running_tools.get(slug)
    if not info:
        return False
    return psutil.pid_exists(info["pid"])


def get_tool_port(slug: str) -> int | None:
    info = _running_tools.get(slug)
    return info["port"] if info else None


def get_tool_log(slug: str, tail: int = 50) -> str:
    """读取工具日志尾部"""
    log_file = LOGS_DIR / f"{slug}.log"
    if not log_file.exists():
        return ""
    lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-tail:])


async def wait_for_tool_ready(slug: str, timeout: float = 5.0) -> bool:
    """等待工具进程就绪（进程存活 + 端口可连接）"""
    info = _running_tools.get(slug)
    if not info:
        return False

    port = info["port"]
    import socket
    deadline = asyncio.get_event_loop().time() + timeout

    while asyncio.get_event_loop().time() < deadline:
        if not psutil.pid_exists(info["pid"]):
            return False
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except (ConnectionRefusedError, OSError, TimeoutError):
            await asyncio.sleep(0.3)

    return False


def get_all_running() -> dict[str, dict]:
    """返回所有运行中工具的 {slug: {pid, port}} 快照"""
    return {slug: {"pid": v["pid"], "port": v["port"]} for slug, v in _running_tools.items()}


def stop_all():
    """停止所有工具子进程"""
    for slug in list(_running_tools.keys()):
        stop_tool(slug)
