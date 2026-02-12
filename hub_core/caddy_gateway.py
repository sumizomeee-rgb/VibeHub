import logging

import httpx

from hub_core.config import CADDY_ADMIN_URL, GATEWAY_PORT, HUB_INTERNAL_PORT

log = logging.getLogger("vibehub.caddy")

_client: httpx.AsyncClient | None = None


async def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=10.0)
    return _client


async def init_server():
    """初始化 Caddy HTTP server，监听 0.0.0.0:GATEWAY_PORT"""
    client = await _get_client()

    # 主控面板 fallback 路由（放在最后）
    hub_route = {
        "@id": "hub_main",
        "match": [{"path": ["/*"]}],
        "handle": [
            {
                "handler": "reverse_proxy",
                "upstreams": [{"dial": f"localhost:{HUB_INTERNAL_PORT}"}],
            },
        ],
    }

    server_cfg = {
        "listen": [f":{GATEWAY_PORT}"],
        "routes": [hub_route],
    }

    # 创建 server（若已存在会覆盖）
    resp = await client.put(
        f"{CADDY_ADMIN_URL}/config/apps/http/servers/srv0",
        json=server_cfg,
    )
    resp.raise_for_status()


async def add_route(slug: str, port: int):
    """注册工具路由: /tools/{slug}/* → localhost:{port}，插入到数组头部"""
    client = await _get_client()

    route = {
        "@id": f"tool_{slug}",
        "match": [{"path": [f"/tools/{slug}", f"/tools/{slug}/*"]}],
        "handle": [
            {"handler": "rewrite", "strip_path_prefix": f"/tools/{slug}"},
            {
                "handler": "reverse_proxy",
                "upstreams": [{"dial": f"localhost:{port}"}],
            },
        ],
    }

    # PUT 到 routes/0 插入头部，确保优先于 hub 的 /* 通配路由
    resp = await client.put(
        f"{CADDY_ADMIN_URL}/config/apps/http/servers/srv0/routes/0",
        json=route,
    )
    resp.raise_for_status()
    log.info(f"[{slug}] Route added → localhost:{port}")


async def remove_route(slug: str):
    """删除工具路由"""
    client = await _get_client()
    try:
        resp = await client.delete(f"{CADDY_ADMIN_URL}/id/tool_{slug}")
        resp.raise_for_status()
        log.info(f"[{slug}] Route removed")
    except httpx.HTTPStatusError:
        log.info(f"[{slug}] Route not found, skip")


async def close():
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None
