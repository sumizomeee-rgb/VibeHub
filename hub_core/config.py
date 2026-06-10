import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = ROOT / "bin"
DATA_DIR = ROOT / "data"
PROJECTS_DIR = ROOT / "projects"
LOGS_DIR = DATA_DIR / "logs" / "tools"
REGISTRY_FILE = DATA_DIR / "registry.json"
REGISTRY_STATE_FILE = DATA_DIR / "registry_state.json"

def _resolve_executable(
    env_var: str,
    binary_name: str,
    *,
    bin_dir: Path = BIN_DIR,
    is_windows: bool = os.name == "nt",
    which=shutil.which,
) -> Path:
    """Resolve bundled or system executable with env override first."""
    configured = os.environ.get(env_var)
    if configured:
        return Path(configured)

    local_name = f"{binary_name}.exe" if is_windows else binary_name
    local_path = bin_dir / local_name
    if local_path.exists():
        return local_path

    path_match = which(binary_name)
    if path_match:
        return Path(path_match)

    return local_path


UV_EXE = _resolve_executable("VIBEHUB_UV", "uv")
CADDY_EXE = _resolve_executable("VIBEHUB_CADDY", "caddy")
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
AGENT_TIMEOUT = 300  # Agent 模式超时（秒），需完成 创建+测试+修复 的完整循环
RESTART_EXIT_CODE = 42
