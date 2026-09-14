import asyncio
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import ValidationError

from hub_core.api_adapter import create_app, desktop_release
from hub_core.catalog import Catalog, ToolSpec, script_metadata, project_files
from hub_core.child_process import InstanceLock
from hub_core.config import ROOT, Settings, resolve_executable
from hub_core.tool_service import ToolService


class FakeGateway:
    def __init__(self):
        self.routes = {}
        self.started = False
    async def start(self): self.started = True
    async def add_route(self, slug, port): self.routes[slug] = port
    async def remove_route(self, slug): self.routes.pop(slug, None)
    async def close(self): self.started = False


class FakeRunner:
    def __init__(self):
        self.running = {}
        self.starts = 0
        self.fail = False
        self.gate = None
    def start(self, spec):
        self.starts += 1
        child = SimpleNamespace(alive=True, port=19999)
        self.running[spec.id] = child
        return child
    async def wait_ready(self, child):
        if self.gate: await self.gate.wait()
        if self.fail: raise TimeoutError("fixture startup failure")
    async def stop(self, slug): self.running.pop(slug, None)
    async def close(self): self.running.clear()


class CatalogTests(unittest.TestCase):
    def test_all_existing_tools_conform(self):
        catalog = Catalog(ROOT)
        catalog.validate()
        self.assertEqual(len(catalog.tools), 5)

    def test_rejects_untrusted_or_windows_reserved_ids(self):
        for value in ("../escape", "with space", "con", "com1", "evil/path", "C:\\evil", "foo.bar", "ABC"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                ToolSpec(id=value, name="example")

    def test_assets_are_part_of_project(self):
        directory = ROOT / "projects/avatar_crop_tool"
        names = [p.relative_to(directory).as_posix() for p in project_files(directory)]
        self.assertIn("assets/crop_reference_01.png", names)
        self.assertIn("assets/achievement_overlay.png", names)

    def test_discovery_does_not_execute_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "main.py"
            path.write_text('# /// script\n# dependencies = []\n# ///\nraise RuntimeError("not executed")\n')
            self.assertEqual(script_metadata(path)["dependencies"], [])

    def test_bad_pep723_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "main.py"
            for source in ('print("no metadata")', '# /// script\n# dependencies = "fastapi"\n# ///\n', '# /// script\n# dependencies = []\n# ///\nnot python code!!'):
                path.write_text(source)
                with self.assertRaises((ValueError, SyntaxError)):
                    script_metadata(path)

    def test_packaged_code_and_assets_are_copied_to_persistent_storage(self):
        catalog = Catalog(ROOT)
        with tempfile.TemporaryDirectory() as tmp, patch("sys.frozen", True, create=True):
            settings = Settings(data_dir=Path(tmp))
            tool = catalog.get("avatar_crop_tool")
            first = catalog.prepare(tool, settings)
            self.assertTrue(first.is_relative_to(Path(tmp)))
            self.assertTrue((first / "assets/crop_reference_01.png").exists())
            (first / "user-output.txt").write_text("preserve")
            self.assertEqual(catalog.prepare(tool, settings), first)
            self.assertEqual((first / "user-output.txt").read_text(), "preserve")

    def test_duplicate_catalog_id_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tools.json").write_text(json.dumps({"schema_version": 1, "tools": [{"id":"demo","name":"Demo"}]*2}))
            with self.assertRaises(ValueError): Catalog(root)

    def test_executable_override(self):
        with patch.dict(os.environ, {"VIBEHUB_UV": str(ROOT / "custom-uv")}):
            self.assertEqual(resolve_executable("uv"), ROOT / "custom-uv")

    def test_instance_lock_released(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = InstanceLock(Path(tmp) / "lock"), InstanceLock(Path(tmp) / "lock")
            first.acquire()
            try:
                with self.assertRaises(RuntimeError): second.acquire()
            finally:
                first.release()
            second.acquire(); second.release()


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.runner = FakeRunner()
        self.gateway = FakeGateway()
        self.service = ToolService(Catalog(ROOT), self.runner, self.gateway)
        self.slug = "avatar_crop_tool"
    async def asyncTearDown(self): await self.service.close()

    async def test_rapid_clicks_launch_only_once(self):
        for _ in range(20):
            self.assertEqual(self.service.open(self.slug)["status"], "starting")
        await self.service.tasks[self.slug]
        self.assertEqual(self.runner.starts, 1)
        self.assertEqual(self.service.open(self.slug)["status"], "ready")
        self.assertEqual(self.runner.starts, 1)

    async def test_failure_is_cleaned_up_and_retry_works(self):
        self.runner.fail = True
        self.service.open(self.slug)
        await self.service.tasks[self.slug]
        self.assertEqual(self.service.view(self.slug)["status"], "error")
        self.assertFalse(self.runner.running)
        self.assertFalse(self.gateway.routes)
        self.runner.fail = False
        self.service.open(self.slug)
        await self.service.tasks[self.slug]
        self.assertEqual(self.service.view(self.slug)["status"], "ready")

    async def test_route_failure_is_not_reported_as_ready(self):
        async def fail(*_): raise RuntimeError("gateway error")
        self.gateway.add_route = fail
        self.service.open(self.slug)
        await self.service.tasks[self.slug]
        self.assertEqual(self.service.view(self.slug)["status"], "error")
        self.assertFalse(self.runner.running)

    async def test_shutdown_cancels_pending_launches(self):
        self.runner.gate = asyncio.Event()
        self.service.open(self.slug)
        await asyncio.sleep(0)
        await self.service.close()
        self.assertFalse(self.runner.running)
        self.assertTrue(all(t.done() for t in self.service.tasks.values()))

    async def test_crash_becomes_retryable(self):
        self.service.open(self.slug)
        await self.service.tasks[self.slug]
        self.runner.running[self.slug].alive = False
        self.assertEqual(self.service.view(self.slug)["status"], "error")
        self.service.open(self.slug)
        await self.service.tasks[self.slug]
        self.assertEqual(self.runner.starts, 2)

    async def test_unknown_tool_never_starts(self):
        with self.assertRaises(KeyError): self.service.open("not_in_catalog")
        self.assertEqual(self.runner.starts, 0)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(data_dir=Path(self.temp.name))
        self.gateway = FakeGateway()
        self.runner = FakeRunner()
        self.service = ToolService(Catalog(ROOT), self.runner, self.gateway)
        self.client = TestClient(create_app(self.settings, service=self.service, gateway=self.gateway))
        self.client.__enter__()
    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def test_home_api_and_cold_tool_links(self):
        self.assertEqual(len(self.client.get("/api/tools").json()), 5)
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        response = self.client.get("/tools/avatar_crop_tool/", follow_redirects=False)
        self.assertEqual(response.headers["location"], "/tool/avatar_crop_tool")

    def test_old_admin_surface_is_gone(self):
        for path in ("/api/build", "/api/admin/restart", "/api/admin/rebuild-frontend", "/api/tools/avatar_crop_tool/start", "/api/tools/avatar_crop_tool/stop", "/api/tools/avatar_crop_tool/restart"):
            self.assertIn(self.client.post(path, headers={"X-VibeHub-Request":"1"}).status_code, {404,405})
        for path in ("/api/tools/avatar_crop_tool/code", "/api/tools/avatar_crop_tool/logs", "/ws/build/anything", "/builder"):
            self.assertEqual(self.client.get(path).status_code, 404, path)
        self.assertIn(self.client.delete("/api/tools/avatar_crop_tool", headers={"X-VibeHub-Request":"1"}).status_code, {404,405})

    def test_open_requires_same_origin_request(self):
        path = "/api/tools/avatar_crop_tool/open"
        self.assertEqual(self.client.post(path).status_code, 403)
        self.assertEqual(self.client.post(path, headers={"X-VibeHub-Request":"1", "Origin":"https://evil.example"}).status_code, 403)
        self.assertIn(self.client.post(path, headers={"X-VibeHub-Request":"1", "Origin":"http://testserver"}).status_code, {200,202})

    def test_unknown_tool_and_missing_asset_fail_honestly(self):
        self.assertEqual(self.client.post("/api/tools/missing/open", headers={"X-VibeHub-Request":"1"}).status_code, 404)
        self.assertEqual(self.client.get("/assets/missing.js").status_code, 404)
        self.assertEqual(self.client.get("/tools/missing/").status_code, 404)

    def test_release_manifest_and_download(self):
        base = Path(self.temp.name) / "release/windows"
        base.mkdir(parents=True)
        payload = b"MZ-test-artifact"
        (base / "VibeHub.exe").write_bytes(payload)
        metadata = {"version":"3.0.0", "platform":"windows-x64", "filename":"VibeHub.exe", "bytes":len(payload), "sha256":hashlib.sha256(payload).hexdigest()}
        (base / "latest.json").write_text(json.dumps(metadata))
        with patch.dict(os.environ, {"VIBEHUB_RELEASE_DIR":str(base.parent)}):
            self.assertEqual(self.client.get("/api/desktop/latest").json()["bytes"], len(payload))
            self.assertEqual(self.client.get("/api/desktop/download").content, payload)
            self.assertEqual(self.client.get("/api/desktop/download", headers={"Range":"bytes=0-1"}).content, b"MZ")
            metadata["filename"] = "../../outside.exe"
            (base / "latest.json").write_text(json.dumps(metadata))
            self.assertEqual(self.client.get("/api/desktop/latest").status_code, 404)


if __name__ == "__main__": unittest.main()
