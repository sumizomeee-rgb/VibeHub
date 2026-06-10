import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from hub_core import api_adapter, config, registry


class ExecutableResolutionTests(unittest.TestCase):
    def test_env_var_overrides_local_and_path_lookup(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"VIBEHUB_UV": "/opt/vibehub/bin/uv"}
        ):
            bin_dir = Path(tmp)
            (bin_dir / "uv").write_text("", encoding="utf-8")

            resolved = config._resolve_executable(
                "VIBEHUB_UV",
                "uv",
                bin_dir=bin_dir,
                is_windows=False,
                which=lambda _name: "/usr/local/bin/uv",
            )

        self.assertEqual(resolved, Path("/opt/vibehub/bin/uv"))

    def test_linux_prefers_extensionless_bin_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            (bin_dir / "uv").write_text("", encoding="utf-8")
            (bin_dir / "uv.exe").write_text("", encoding="utf-8")

            resolved = config._resolve_executable(
                "VIBEHUB_UV",
                "uv",
                bin_dir=bin_dir,
                is_windows=False,
                which=lambda _name: None,
            )

        self.assertEqual(resolved, bin_dir / "uv")

    def test_windows_prefers_exe_bin_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            (bin_dir / "caddy").write_text("", encoding="utf-8")
            (bin_dir / "caddy.exe").write_text("", encoding="utf-8")

            resolved = config._resolve_executable(
                "VIBEHUB_CADDY",
                "caddy",
                bin_dir=bin_dir,
                is_windows=True,
                which=lambda _name: None,
            )

        self.assertEqual(resolved, bin_dir / "caddy.exe")

    def test_path_lookup_is_last_resort(self):
        with tempfile.TemporaryDirectory() as tmp:
            resolved = config._resolve_executable(
                "VIBEHUB_UV",
                "uv",
                bin_dir=Path(tmp),
                is_windows=False,
                which=lambda name: f"/usr/bin/{name}",
            )

        self.assertEqual(resolved, Path("/usr/bin/uv"))


class RegistryPathTests(unittest.TestCase):
    def test_project_script_paths_are_stored_relative_to_repo_root(self):
        script_path = config.PROJECTS_DIR / "demo_tool" / "main.py"

        stored = registry._portable_script_path(script_path)

        self.assertEqual(stored, "projects/demo_tool/main.py")


class AdminCommandTests(unittest.TestCase):
    def test_rebuild_frontend_does_not_use_shell(self):
        completed = SimpleNamespace(returncode=0, stderr="")
        with patch.object(api_adapter.subprocess, "run", return_value=completed) as run:
            result = asyncio.run(api_adapter.rebuild_frontend())

        self.assertEqual(result, {"ok": True, "message": "前端重建完成"})
        self.assertEqual(run.call_args.kwargs.get("shell"), False)


class StartScriptTests(unittest.TestCase):
    def test_linux_start_script_uses_extensionless_local_binaries(self):
        script = (config.ROOT / "start.sh").read_text(encoding="utf-8")

        self.assertIn("bin/uv", script)
        self.assertIn("bin/caddy", script)
        self.assertNotIn("uv.exe", script)
        self.assertNotIn("caddy.exe", script)

    def test_linux_start_script_warns_for_missing_claude_without_blocking(self):
        script = (config.ROOT / "start.sh").read_text(encoding="utf-8")

        self.assertIn("warn_cmd \"Claude CLI\"", script)
        self.assertNotIn("check_cmd \"Claude CLI\"", script)

    def test_windows_start_script_warns_for_missing_claude_without_blocking(self):
        script = (config.ROOT / "start.bat").read_text(encoding="utf-8")

        self.assertIn("[WARN] Claude CLI not found", script)
        self.assertNotIn("set \"ENV_OK=0\"", script.split("where claude", 1)[1].split("where bash", 1)[0])


if __name__ == "__main__":
    unittest.main()
