import json
import logging
from datetime import datetime
from pathlib import Path

from hub_core.config import REGISTRY_FILE, REGISTRY_STATE_FILE

log = logging.getLogger("vibehub.registry")

# 运行时字段，存入 registry_state.json（git 忽略）
_RUNTIME_FIELDS = {"click_count", "status"}


def _ensure_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("{}", encoding="utf-8")


def _load_json(path: Path) -> dict:
    _ensure_file(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: dict):
    _ensure_file(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_registry() -> dict:
    return _load_json(REGISTRY_FILE)


def _save_registry(data: dict):
    _save_json(REGISTRY_FILE, data)


def _load_state() -> dict:
    return _load_json(REGISTRY_STATE_FILE)


def _save_state(data: dict):
    _save_json(REGISTRY_STATE_FILE, data)


def load() -> dict:
    """合并结构数据和运行时状态，返回完整视图"""
    reg = _load_registry()
    state = _load_state()
    merged = {}
    for slug, info in reg.items():
        s = state.get(slug, {})
        merged[slug] = {
            **info,
            "status": s.get("status", "stopped"),
            "click_count": s.get("click_count", 0),
        }
    return merged


def save(data: dict):
    """兼容旧调用：将完整数据分流写入两个文件"""
    reg = {}
    state = {}
    for slug, info in data.items():
        r = {}
        s = {}
        for k, v in info.items():
            if k in _RUNTIME_FIELDS:
                s[k] = v
            else:
                r[k] = v
        reg[slug] = r
        state[slug] = s
    _save_registry(reg)
    _save_state(state)


def register_tool(slug: str, display_name: str, script_path: str):
    reg = _load_registry()
    state = _load_state()
    reg[slug] = {
        "display_name": display_name,
        "path": script_path,
        "route_slug": slug,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "auto_start": True,
    }
    state.setdefault(slug, {})
    state[slug].setdefault("click_count", 0)
    state[slug]["status"] = "active"
    _save_registry(reg)
    _save_state(state)
    log.info(f"[{slug}] Registered: {display_name}")


def unregister_tool(slug: str):
    reg = _load_registry()
    state = _load_state()
    reg.pop(slug, None)
    state.pop(slug, None)
    _save_registry(reg)
    _save_state(state)
    log.info(f"[{slug}] Unregistered")


def list_tools() -> list[dict]:
    data = load()
    return [{"slug": slug, **info} for slug, info in data.items()]


def get_tool(slug: str) -> dict | None:
    data = load()
    info = data.get(slug)
    if info:
        return {"slug": slug, **info}
    return None


def set_status(slug: str, status: str):
    """status: 'active' | 'stopped' | 'error'"""
    state = _load_state()
    if slug not in state:
        state[slug] = {}
    state[slug]["status"] = status
    _save_state(state)
    log.info(f"[{slug}] Status → {status}")


def rename_tool(slug: str, new_name: str) -> bool:
    reg = _load_registry()
    if slug in reg:
        reg[slug]["display_name"] = new_name
        _save_registry(reg)
        log.info(f"[{slug}] Renamed → {new_name}")
        return True
    return False


def increment_click(slug: str):
    """记录工具被打开的次数"""
    state = _load_state()
    if slug not in state:
        state[slug] = {}
    state[slug]["click_count"] = state[slug].get("click_count", 0) + 1
    _save_state(state)


def set_auto_start(slug: str, value: bool):
    """设置工具是否自动启动"""
    reg = _load_registry()
    if slug in reg:
        reg[slug]["auto_start"] = value
        _save_registry(reg)
        log.info(f"[{slug}] auto_start → {value}")
