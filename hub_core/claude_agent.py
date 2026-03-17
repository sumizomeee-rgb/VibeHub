"""
VibeHub Claude Agent — Agent 模式任务执行器

让 Claude CLI 以 Agent 模式自主完成 文件创建、测试执行、错误修复 的完整闭环。
不再使用 --output-format text（纯文本模式），不再用正则提取代码。
Python 层仅负责：投放任务 → 实时透传日志 → 验证最终产物。
"""

import asyncio
import logging
import subprocess
import re
import os

from hub_core.config import CLAUDE_CMD, UV_EXE, PROJECTS_DIR, AGENT_TIMEOUT

log = logging.getLogger("vibehub.agent")


# ============================================================
# Mission Prompt 构建
# ============================================================

def _build_mission_prompt(
    user_request: str,
    existing_code: str | None = None,
    slug: str = "",
) -> str:
    """构造 Agent Mission Prompt。

    不再要求 Claude "输出代码文本"，
    而是要求它 **使用自身的工具** 在当前工作目录创建/修改文件并自测。
    """
    uv_exe = str(UV_EXE).replace("\\", "/")

    mission = f"""\
你的任务是在当前工作目录下开发一个 Python Web 工具。

## 用户需求
{user_request}

## 强制规则（违反任何一条即为失败）

### 文件规范
1. 将最终可运行的代码写入当前目录的 `main.py`，必须是单文件 FastAPI 应用。
2. 文件开头必须包含 PEP 723 inline metadata：
   ```
   # /// script
   # requires-python = ">=3.10"
   # dependencies = ["fastapi", "uvicorn"]
   # ///
   ```
   将 dependencies 替换为你实际使用的所有第三方库。

### 运行规范
3. 动态端口：使用 `int(os.environ.get("PORT", 8000))`，禁止硬编码。
4. 绑定地址：仅 `127.0.0.1`，禁止 `0.0.0.0`。
5. 工具显示名称：HTML 页面的 `<title>` 和页面主标题必须使用环境变量 `os.environ.get("DISPLAY_NAME", "工具")`，禁止硬编码中文标题。
6. 入口点：文件末尾必须是：
   ```python
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
   ```

### URL 规范
7. 本应用将被反向代理挂载在子路径 `/tools/{slug}/` 下。
   HTML/JS 中所有 fetch/XHR/form URL 必须是相对路径（无前导 `/`）。
   使用 `api/upload` 而非 `/api/upload`。

### UI 设计规范 (VibeHub 统一风格)
8. 颜色：主色 #cba186，背景 #f0f2f5，白色卡片
9. 卡片：border-radius: 16px, box-shadow: 0 2px 12px rgba(0,0,0,.08)
10. 按钮：主按钮 #cba186，次按钮 #eee，下载按钮 #000，圆角 10px
11. 布局：Header + 上传卡片 + 按钮行 + Grid 预览
12. 响应式：桌面 3 列，平板 2 列，手机 1 列
13. 所有 UI 文本使用中文

### 自测流程
14. 写完 `main.py` 后，你**必须**自己验证代码可运行：
    - 使用 Bash 工具执行：`PORT=18999 {uv_exe} run main.py &`（后台启动）
    - 等待 4 秒
    - 用 curl 测试 `http://127.0.0.1:18999/` 是否返回 2xx
    - 如果失败，阅读报错，修改 `main.py`，重新测试
    - 测试完成后，务必 kill 掉后台进程
    - 最多重试 3 次

### 完成信号
15. 当你确认 `main.py` 已可正常运行且测试通过，直接结束即可。
    不需要输出任何额外解释。
"""

    if existing_code:
        mission += f"""
## 现有代码（在此基础上修改）

```python
{existing_code}
```

请在现有代码基础上，根据用户需求进行修改。保留已有的正确逻辑。
"""

    return mission


# ============================================================
# 工作目录准备
# ============================================================

_WORKSPACE_CLAUDE_MD_TEMPLATE = """\
# CLAUDE.md

## 工作环境
- 当前目录是 VibeHub 的一个工具项目目录
- 使用 `{uv_exe}` 代替 `python` 来运行脚本（它会自动解析 PEP 723 依赖）
- 测试时使用 PORT 环境变量指定端口

## 禁止事项
- 不要创建除 main.py 之外的其他 Python 文件
- 不要安装系统级依赖
- 不要修改当前目录以外的任何文件
"""


def _prepare_workspace(
    tool_dir: str,
    user_request: str,
    existing_code: str | None,
    slug: str,
):
    """准备工作目录：写入 CLAUDE.md 和 _mission.md"""
    uv_exe = str(UV_EXE).replace("\\", "/")

    # 写入 CLAUDE.md 引导 Agent 行为边界
    claude_md_path = os.path.join(tool_dir, "CLAUDE.md")
    with open(claude_md_path, "w", encoding="utf-8") as f:
        f.write(_WORKSPACE_CLAUDE_MD_TEMPLATE.format(uv_exe=uv_exe))

    # 写入 _mission.md（避免 Windows CMD 参数长度限制 ~8191 字符）
    mission = _build_mission_prompt(user_request, existing_code, slug)
    mission_file = os.path.join(tool_dir, "_mission.md")
    with open(mission_file, "w", encoding="utf-8") as f:
        f.write(mission)

    log.info(f"[{slug}] 工作目录已准备: {tool_dir}, mission_len={len(mission)}")


# ============================================================
# Agent Runner
# ============================================================

# Agent 入口指令（短文本，通过 -p 传递，避免 CMD 参数长度限制）
_AGENT_ENTRY_INSTRUCTION = (
    "请阅读当前目录下的 _mission.md 文件，严格按照其中的指示完成任务。"
    "完成后不需要额外解释。"
)


async def run_agent_task(
    slug: str,
    user_request: str,
    existing_code: str | None = None,
    on_output: callable = None,
    timeout: int | None = None,
) -> bool:
    """以 Agent 模式执行 Claude CLI 任务。

    Args:
        slug: 工具标识（决定工作目录 projects/{slug}/）
        user_request: 用户原始需求描述
        existing_code: 已有代码（编辑模式时传入）
        on_output: 日志回调，每行输出时调用 on_output(line: str)
        timeout: 超时秒数，默认 AGENT_TIMEOUT

    Returns:
        bool: 任务是否成功（main.py 存在且语法正确）
    """
    if timeout is None:
        timeout = AGENT_TIMEOUT

    tool_dir = str(PROJECTS_DIR / slug)
    os.makedirs(tool_dir, exist_ok=True)

    # 准备工作目录（写入 CLAUDE.md + _mission.md）
    _prepare_workspace(tool_dir, user_request, existing_code, slug)

    # Claude CLI 命令
    # 关键变化：不再使用 --output-format text，释放 Agent 工具调用能力
    cmd = [
        CLAUDE_CMD,
        "--dangerously-skip-permissions",
        "-p", _AGENT_ENTRY_INSTRUCTION,
    ]

    log.info(f"[{slug}] 启动 Agent 任务 (timeout={timeout}s)")

    loop = asyncio.get_event_loop()
    proc_ref = [None]  # 跨线程可变引用，用于超时时 kill

    def _run_agent_sync() -> tuple[int, str]:
        """在线程池中同步执行 Agent 进程，逐行读取输出并透传"""
        output_lines = []
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=tool_dir,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            proc_ref[0] = proc

            # 逐行读取 Agent 的实时输出（包括工具调用日志）
            for raw_line in iter(proc.stdout.readline, ""):
                line = _strip_ansi(raw_line.rstrip())
                if line:
                    output_lines.append(line)
                    log.debug(f"[{slug}] Agent: {line[:200]}")
                    if on_output:
                        try:
                            loop.call_soon_threadsafe(on_output, line)
                        except RuntimeError:
                            pass  # event loop 已关闭

            proc.stdout.close()
            rc = proc.wait(timeout=30)
            return rc, "\n".join(output_lines)

        except Exception as e:
            log.error(f"[{slug}] Agent 进程异常: {e}")
            return -1, f"Agent 进程异常: {e}"

    # 在线程池中执行（避免阻塞事件循环，同时允许 WebSocket 推送日志）
    try:
        returncode, full_output = await asyncio.wait_for(
            loop.run_in_executor(None, _run_agent_sync),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        proc = proc_ref[0]
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
        log.error(f"[{slug}] Agent 超时 ({timeout}s)")
        if on_output:
            on_output(f"❌ Agent 执行超时 ({timeout}s)")
        return False

    log.info(f"[{slug}] Agent 退出 rc={returncode}, output_len={len(full_output)}")

    # 验证结果：main.py 是否存在且语法正确
    main_py = PROJECTS_DIR / slug / "main.py"
    if not main_py.exists():
        log.error(f"[{slug}] Agent 完成但 main.py 不存在")
        if on_output:
            on_output("❌ Agent 完成但未创建 main.py")
        return False

    code = main_py.read_text(encoding="utf-8")
    syntax_err = _check_syntax(code)
    if syntax_err:
        log.error(f"[{slug}] main.py 语法错误: {syntax_err}")
        if on_output:
            on_output(f"❌ main.py 语法错误: {syntax_err}")
        return False

    log.info(f"[{slug}] Agent 任务成功, main.py = {len(code)} chars")
    return True


# ============================================================
# 辅助函数
# ============================================================

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def _strip_ansi(text: str) -> str:
    """去除 ANSI 转义码（Claude CLI 输出包含彩色文本标记）"""
    return _ANSI_RE.sub("", text)


def _check_syntax(code: str) -> str | None:
    """检查 Python 代码语法，返回 None 表示通过，否则返回错误信息。"""
    try:
        compile(code, "<test>", "exec")
        return None
    except SyntaxError as e:
        return f"Line {e.lineno}: {e.msg}"
