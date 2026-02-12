import json
import logging
from datetime import datetime
from pathlib import Path

from hub_core.config import REGISTRY_FILE

log = logging.getLogger("vibehub.registry")


def _ensure_file():
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text("{}", encoding="utf-8")


def load() -> dict:
    _ensure_file()
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def save(data: dict):
    _ensure_file()
    REGISTRY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def register_tool(slug: str, display_name: str, script_path: str):
    data = load()
    data[slug] = {
        "display_name": display_name,
        "status": "active",
        "path": script_path,
        "route_slug": slug,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    save(data)
    log.info(f"[{slug}] Registered: {display_name}")


def unregister_tool(slug: str):
    data = load()
    data.pop(slug, None)
    save(data)
    log.info(f"[{slug}] Unregistered")


def list_tools() -> list[dict]:
    data = load()
    result = []
    for slug, info in data.items():
        result.append({"slug": slug, **info})
    return result


def get_tool(slug: str) -> dict | None:
    data = load()
    info = data.get(slug)
    if info:
        return {"slug": slug, **info}
    return None


def set_status(slug: str, status: str):
    """status: 'active' | 'stopped' | 'error'"""
    data = load()
    if slug in data:
        data[slug]["status"] = status
        save(data)
        log.info(f"[{slug}] Status → {status}")


def rename_tool(slug: str, new_name: str) -> bool:
    data = load()
    if slug in data:
        data[slug]["display_name"] = new_name
        save(data)
        log.info(f"[{slug}] Renamed → {new_name}")
        return True
    return False
