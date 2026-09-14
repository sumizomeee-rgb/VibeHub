"""Public launcher API only. There are intentionally no administration endpoints."""
from contextlib import asynccontextmanager
import json
from pathlib import Path
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from hub_core.catalog import Catalog
from hub_core.caddy_gateway import CaddyGateway
from hub_core.config import Settings
from hub_core.process_manager import ToolRunner
from hub_core.tool_service import ToolService


def desktop_release(directory: Path) -> tuple[dict, Path]:
    base = (directory / "windows").resolve()
    try:
        metadata = json.loads((base / "latest.json").read_text(encoding="utf-8"))
        name = metadata["filename"]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+\.exe", name):
            raise ValueError("Invalid release filename")
        artifact = base / name
        if artifact.is_symlink() or not artifact.resolve().is_relative_to(base):
            raise ValueError("Unsafe artifact path")
        if metadata["platform"] != "windows-x64" or not isinstance(metadata["version"], str):
            raise ValueError("Invalid release platform/version")
        if not re.fullmatch(r"[0-9a-f]{64}", metadata["sha256"]):
            raise ValueError("Invalid SHA256")
        if type(metadata["bytes"]) is not int or metadata["bytes"] <= 0 or artifact.stat().st_size != metadata["bytes"]:
            raise ValueError("Invalid release size")
        return {key: metadata[key] for key in ("version", "platform", "filename", "bytes", "sha256")}, artifact
    except (OSError, KeyError, ValueError, TypeError) as error:
        raise HTTPException(404, "暂未发布 Windows 客户端") from error


def create_app(settings: Settings | None = None, *, service=None, gateway=None) -> FastAPI:
    settings = settings or Settings.from_env()
    catalog = service.catalog if service else Catalog(settings.bundle_dir)
    gateway = gateway or CaddyGateway(settings)
    service = service or ToolService(catalog, ToolRunner(settings, catalog), gateway)

    @asynccontextmanager
    async def lifespan(app):
        catalog.validate()
        try:
            await gateway.start()
            yield
        finally:
            try:
                await service.close()
            finally:
                await gateway.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.tools = service
    app.state.gateway = gateway

    @app.middleware("http")
    async def same_origin_mutations(request: Request, call_next):
        if request.url.path.startswith("/api/") and request.method not in {"GET", "HEAD", "OPTIONS"}:
            # A custom header cannot be sent by cross-origin forms. No CORS is enabled.
            if request.headers.get("X-VibeHub-Request") != "1":
                return JSONResponse({"detail": "Invalid launcher request"}, status_code=403)
            origin = request.headers.get("origin")
            own_origin = f"{request.url.scheme}://{request.url.netloc}"
            if origin and origin.rstrip("/") != own_origin:
                return JSONResponse({"detail": "Cross-origin request rejected"}, status_code=403)
            if request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse({"detail": "Cross-site request rejected"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "version": settings.version}

    @app.get("/api/app")
    async def application_info():
        return {"name": "VibeHub", "version": settings.version, "desktop": settings.desktop}

    @app.get("/api/tools")
    async def list_tools():
        return [tool.public() for tool in catalog.tools]

    @app.get("/api/tools/{tool_id}")
    async def tool_status(tool_id: str):
        try:
            return service.view(tool_id)
        except KeyError:
            raise HTTPException(404, "工具不存在") from None

    @app.post("/api/tools/{tool_id}/open")
    async def open_tool(tool_id: str):
        try:
            result = service.open(tool_id)
            return JSONResponse(result, status_code=200 if result["status"] == "ready" else 202)
        except KeyError:
            raise HTTPException(404, "工具不存在") from None
        except RuntimeError as error:
            raise HTTPException(503, str(error)) from error

    @app.get("/api/desktop/latest")
    async def latest():
        metadata, _ = desktop_release(settings.release_dir)
        return {**metadata, "download_url": "/api/desktop/download"}

    @app.api_route("/api/desktop/download", methods=["GET", "HEAD"])
    async def download():
        metadata, artifact = desktop_release(settings.release_dir)
        return FileResponse(artifact, filename=metadata["filename"], media_type="application/vnd.microsoft.portable-executable")

    # Cold bookmarks are taken through the host, which performs automatic startup.
    # Once ready, Caddy serves /tools/{id}/* directly from the tool process.
    @app.get("/tools/{tool_id}")
    @app.get("/tools/{tool_id}/{path:path}")
    async def cold_tool(tool_id: str, path: str = ""):
        try:
            catalog.get(tool_id)
        except KeyError:
            raise HTTPException(404, "工具不存在") from None
        return RedirectResponse(f"/tool/{tool_id}", status_code=307)

    dist = settings.bundle_dir / "frontend/dist"

    @app.api_route("/{path:path}", methods=["GET", "HEAD"])
    async def frontend(path: str):
        # Do not disguise removed API/WS routes or missing assets as HTTP 200 HTML.
        if path == "api" or path.startswith(("api/", "ws/")):
            raise HTTPException(404, "Not found")
        candidate = (dist / path).resolve()
        if not candidate.is_relative_to(dist.resolve()):
            raise HTTPException(404, "Not found")
        if candidate.is_file():
            return FileResponse(candidate)
        if path and not path.startswith("tool/"):
            raise HTTPException(404, "Not found")
        index = dist / "index.html"
        if not index.exists():
            raise HTTPException(503, "前端尚未构建，请运行 build.bat 或 python build.py --target web")
        return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return app
