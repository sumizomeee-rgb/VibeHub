import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = ROOT / "bin"
DATA_DIR = ROOT / "data"
PROJECTS_DIR = ROOT / "projects"
LOGS_DIR = DATA_DIR / "logs" / "tools"
REGISTRY_FILE = DATA_DIR / "registry.json"

UV_EXE = BIN_DIR / "uv.exe"
CADDY_EXE = BIN_DIR / "caddy.exe"
CADDY_ADMIN_URL = "http://localhost:2019"

GATEWAY_PORT = 9529
HUB_INTERNAL_PORT = 8080

# Claude CLI on Windows requires git-bash — auto-detect from PATH
if "CLAUDE_CODE_GIT_BASH_PATH" not in os.environ:
    bash_path = shutil.which("bash")
    if bash_path:
        os.environ["CLAUDE_CODE_GIT_BASH_PATH"] = bash_path

# shutil.which resolves .cmd/.bat on Windows
CLAUDE_CMD = shutil.which("claude") or "claude"
MAX_HEAL_RETRIES = 3
RESTART_EXIT_CODE = 42
