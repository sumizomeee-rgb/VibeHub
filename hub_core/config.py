"""One configuration model for the web server and the desktop window.

Bundled files are read-only. All caches, logs and tool data live under data_dir.
Nothing in this module starts processes or creates directories at import time.
"""
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import sys
import tomllib

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)).resolve()


def executable_dir() -> Path:
    """The folder holding VibeHub.exe, or the repository when running from source."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return ROOT


def desktop_root() -> Path:
    """Kept beside the executable so results are easy to find, not buried in AppData."""
    return executable_dir() / "VibeHub"


def resolve_executable(name: str, root: Path = ROOT) -> Path:
    override = os.environ.get(f"VIBEHUB_{name.upper()}")
    if override:
        return Path(override).expanduser().resolve()
    filename = name + (".exe" if os.name == "nt" else "")
    target = "windows-x64" if os.name == "nt" else "linux-x64"
    bundled = root / "bin" / target / filename
    if not bundled.is_file():
        bundled = root / "bin" / filename
    return bundled if bundled.is_file() else Path(shutil.which(name) or bundled)


@dataclass(frozen=True)
class Settings:
    bundle_dir: Path = ROOT
    data_dir: Path = ROOT / ".runtime"
    output_dir: Path = ROOT / "output"
    host: str = "127.0.0.1"
    port: int = 9529
    hub_port: int = 8080
    desktop: bool = False
    startup_timeout: float = 180.0
    tool_python: str = "3.12"
    warmup: bool = True

    @property
    def version(self) -> str:
        with (self.bundle_dir / "pyproject.toml").open("rb") as f:
            return tomllib.load(f)["project"]["version"]

    @property
    def release_dir(self) -> Path:
        return Path(os.environ.get("VIBEHUB_RELEASE_DIR", str(self.bundle_dir / "release"))).resolve()

    @classmethod
    def from_env(cls, *, desktop: bool = False) -> "Settings":
        default_data = ROOT / ".runtime"
        if desktop or getattr(sys, "frozen", False):
            if os.name == "nt":
                local_app_data = os.environ.get("LOCALAPPDATA")
                default_data = Path(local_app_data) / "VibeHub" if local_app_data else Path.home() / "AppData/Local/VibeHub"
            else:
                xdg_data_home = os.environ.get("XDG_DATA_HOME")
                default_data = Path(xdg_data_home) / "VibeHub" if xdg_data_home else Path.home() / ".local/share/VibeHub"
        data_dir = Path(os.environ.get("VIBEHUB_DATA_DIR", default_data)).expanduser().resolve()
        # Desktop results stay visible beside the executable. A web deployment
        # keeps writable output with its other persistent state, outside the bundle.
        default_output = desktop_root() / "output" if desktop or getattr(sys, "frozen", False) else data_dir / "output"
        return cls(
            data_dir=data_dir,
            output_dir=Path(os.environ.get("VIBEHUB_OUTPUT_DIR", default_output)).expanduser().resolve(),
            host="127.0.0.1" if desktop else os.environ.get("VIBEHUB_HOST", "127.0.0.1"),
            port=0 if desktop else int(os.environ.get("VIBEHUB_PORT", "9529")),
            desktop=desktop,
            startup_timeout=float(os.environ.get("VIBEHUB_STARTUP_TIMEOUT", "180")),
            tool_python=os.environ.get("VIBEHUB_TOOL_PYTHON", "3.12"),
            warmup=os.environ.get("VIBEHUB_WARMUP", "1").lower() not in {"0", "false", "no"},
        )
