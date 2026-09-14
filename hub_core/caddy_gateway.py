"""A private, owned Caddy instance shared by web and desktop entrypoints."""
import asyncio
import json
from pathlib import Path
import socket

import httpx

from hub_core.child_process import ChildProcess, clean_environment
from hub_core.config import Settings, resolve_executable


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class CaddyGateway:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.admin_url = f"http://127.0.0.1:{free_port()}"
        self.child = None
        self.client = None
        self.routes: dict[str, int] = {}
        self.lock = asyncio.Lock()

    def _hub_route(self) -> dict:
        return {"handle": [{"handler": "reverse_proxy", "upstreams": [{"dial": f"127.0.0.1:{self.settings.hub_port}"}]}], "terminal": True}

    def _routes(self, routes: dict[str, int]) -> list:
        result = []
        for slug, port in sorted(routes.items()):
            result.extend([
                {"match": [{"path": [f"/tools/{slug}"]}], "handle": [{"handler": "static_response", "status_code": 308, "headers": {"Location": [f"/tools/{slug}/"]}}], "terminal": True},
                {"match": [{"path": [f"/tools/{slug}/*"]}], "handle": [
                    {"handler": "rewrite", "strip_path_prefix": f"/tools/{slug}"},
                    {"handler": "reverse_proxy", "upstreams": [{"dial": f"127.0.0.1:{port}"}]},
                ], "terminal": True},
            ])
        return [*result, self._hub_route()]

    async def start(self):
        settings = self.settings
        config = {
            "admin": {"listen": self.admin_url.removeprefix("http://")},
            "apps": {"http": {"servers": {"vibehub": {
                "listen": [f"{settings.host}:{settings.port}"],
                "automatic_https": {"disable": True},
                "routes": self._routes({}),
            }}}},
        }
        path = settings.data_dir / "caddy.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config), encoding="utf-8")
        environment = clean_environment()
        environment.update({"XDG_DATA_HOME": str(settings.data_dir / "caddy-data"), "XDG_CONFIG_HOME": str(settings.data_dir / "caddy-config")})
        self.child = ChildProcess([str(resolve_executable("caddy", settings.bundle_dir)), "run", "--config", str(path)],
                                  cwd=settings.data_dir, env=environment, log_file=settings.data_dir / "logs/caddy.log")
        self.client = httpx.AsyncClient(base_url=self.admin_url, timeout=5, trust_env=False)
        deadline = asyncio.get_running_loop().time() + 15
        while asyncio.get_running_loop().time() < deadline:
            if not self.child.alive:
                raise RuntimeError("Caddy 启动失败，请检查端口占用和 logs/caddy.log")
            try:
                response = await self.client.get("/config/")
                response.raise_for_status()
                return
            except httpx.HTTPError:
                await asyncio.sleep(0.1)
        raise RuntimeError("Caddy 网关启动超时")

    async def _publish(self, routes: dict[str, int]):
        # PATCH replaces the routes array; POST would append a nested array.
        response = await self.client.patch("/config/apps/http/servers/vibehub/routes", json=self._routes(routes))
        response.raise_for_status()
        self.routes = routes

    async def add_route(self, slug: str, port: int):
        async with self.lock:
            await self._publish({**self.routes, slug: port})

    async def remove_route(self, slug: str):
        async with self.lock:
            if slug in self.routes:
                await self._publish({s: p for s, p in self.routes.items() if s != slug})

    async def close(self):
        try:
            if self.client:
                await self.client.aclose()
        finally:
            if self.child:
                await asyncio.to_thread(self.child.stop)
