import logging
import subprocess
import re
import os

from hub_core.config import CLAUDE_CMD, UV_EXE, PROJECTS_DIR, MAX_HEAL_RETRIES
from hub_core.port_manager import find_free_port

log = logging.getLogger("vibehub.agent")

# ============================================================
# Prompts
# ============================================================
# ARCHITECTURE NOTE:
# --system-prompt is a CLI argument → must NEVER contain " (double-quote)
# characters because Windows cmd.exe mangles them when invoking .CMD wrappers.
# Detailed rules (with code examples that need double-quotes) go into
# _RULES_PREAMBLE, which is prepended to the user prompt and delivered
# via stdin piping (bypasses CMD argument parsing entirely).

# Short, quote-free role descriptions for --system-prompt
CODEGEN_SYSTEM_ROLE = (
    "You are a code generation engine. "
    "Output ONLY a single Python code block. No explanations."
)

TEST_GEN_SYSTEM_ROLE = (
    "You are a test engineer. "
    "Output ONLY a single Python code block. No explanations."
)

# Detailed rules prepended to user prompt (piped via stdin, so " is safe)
CODEGEN_RULES = """\
You must output a complete, standalone, single-file Python script.

Mandatory rules (violating ANY is an error):

1. PEP 723 inline metadata — the VERY FIRST lines must be:
# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn"]
# ///
Replace the dependencies list with ALL third-party packages your code imports.
All TOML values MUST be double-quoted strings.

2. Dynamic port: use int(os.environ.get("PORT", 8000)). NEVER hardcode.

3. Bind address: 127.0.0.1 only. NEVER 0.0.0.0.

4. Prefer FastAPI + Uvicorn. For frontend tools use HTMLResponse to inline HTML/CSS/JS.

5. Entry point — file must end with:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))

6. Everything in ONE .py file. No extra files.

7. CRITICAL — URL paths in HTML/JS: This app will be served behind a reverse proxy
at a sub-path like /tools/my_app/. All fetch/XHR/form URLs in your HTML and
JavaScript MUST be relative (NO leading slash). Use "api/upload" not "/api/upload".
Use "./api/upload" or "api/upload". This ensures requests route correctly through
the reverse proxy.

8. CRITICAL — Keep code CONCISE. The entire script must be under 300 lines.
   For HTML/CSS/JS content, use MINIMAL styling. Avoid verbose CSS frameworks
   or large inline HTML templates. Use compact, functional UI design.
   If the user requests complex features, implement the CORE functionality only
   and keep the UI simple and clean.

9. UI Design — All tools MUST follow VibeHub unified style:
   - Colors: Primary #cba186 (brown), Background #f0f2f5 (light gray), White cards
   - Card style: border-radius: 16px, box-shadow: 0 2px 12px rgba(0,0,0,.08)
   - Buttons: .btn-primary (#cba186), .btn-secondary (#eee), .btn-dl (#000), rounded 10px
   - Layout: Header (title + actions) + Upload card + Button row + Grid preview
   - Drag zone: Dashed #cba186 border, hover to black
   - Transparent preview: Checkerboard pattern (linear-gradient)
   - Responsive: Desktop 3 columns, Tablet 2 columns, Mobile 1 column
   - Chinese text for all UI elements
   - Compact inline CSS: Use minified style strings, avoid verbose class names

10. Output ONLY the Python code inside a ```python code block. Nothing else.
"""

TEST_GEN_RULES = """\
Generate a lightweight test script for the given web tool.

Requirements:
1. Use httpx as HTTP client.
2. Start target app with: subprocess.Popen(["uv", "run", "main.py"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
   CRITICAL: Use DEVNULL for stdout/stderr to avoid pipe blocking. Use "uv run" not python.
3. Wait 4 seconds for startup, then test: GET / returns 2xx.
4. Print detailed error messages. exit(0) on pass, exit(1) on fail.
5. PEP 723 header (TOML values MUST be double-quoted):
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
6. Kill target process in finally block.
7. Each Python statement MUST be on its own line.

Output ONLY the test code inside a ```python code block. Nothing else.
"""


def _call_claude(user_prompt: str, system_prompt: str, timeout: int = 120, _max_retries: int = 2) -> str:
    """Call Claude CLI, always piping user_prompt via stdin.

    system_prompt goes to --system-prompt (must be short, no double-quotes).
    user_prompt (which may contain rules + code with double-quotes) is piped
    via stdin to bypass Windows CMD argument length and quoting limits.

    Windows 上 Node.js libuv 管道偶发丢失 stdout，rc=0 但输出为空时自动重试。
    """
    flat_system = " ".join(system_prompt.replace("\r", "").split())

    cmd = [
        CLAUDE_CMD,
        "--dangerously-skip-permissions",
        "-p", "Follow the instructions provided via stdin.",
        "--system-prompt", flat_system,
        "--output-format", "text",
    ]

    last_error = None
    for attempt in range(1, _max_retries + 1):
        log.info(f"Calling Claude CLI (timeout={timeout}s, prompt_len={len(user_prompt)}, attempt={attempt})")

        result = subprocess.run(
            cmd,
            input=user_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
        )

        # Guard against None — Windows .CMD subprocess edge case
        stdout = result.stdout or ""
        stderr = result.stderr or ""

        log.info(f"Claude CLI rc={result.returncode} stdout_len={len(stdout)} stderr_len={len(stderr)}")

        # Claude CLI 可能在 Node.js 清理阶段触发 libuv 断言失败，
        # 导致 rc 非零，但 stdout 中已包含完整的有效输出。
        # 优先检查 stdout 是否有内容，有则忽略退出码。
        if result.returncode != 0:
            if stdout.strip():
                log.warning(f"Claude CLI rc={result.returncode} 但 stdout 有内容 ({len(stdout)} chars)，忽略退出码。stderr: {stderr[:200]}")
            else:
                log.error(f"Claude CLI error: {stderr[:500]}")
                raise RuntimeError(f"Claude CLI error (code={result.returncode}): {stderr[:500]}")

        if stdout.strip():
            return stdout

        # rc=0 但 stdout 为空 — Windows libuv 管道丢失，可重试
        log.warning(f"Claude CLI returned empty output (attempt {attempt}/{_max_retries}), stdout_len={len(stdout)}")
        last_error = "Claude CLI returned empty output"

    log.error(f"Claude CLI returned empty output after {_max_retries} attempts")
    raise RuntimeError(last_error)


def _extract_python_code(text: str) -> str:
    """Extract Python code block from Claude output.

    Uses line-anchored closing ``` to avoid matching triple-quotes
    inside Python code (e.g. r\"""...\""").
    Also handles truncated output where closing ``` is missing.
    """
    # Match ```python ... ``` where closing ``` is at line start
    match = re.search(r"```python\s*\n(.+?)^```", text, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1).strip()

    # Fallback: any ``` ... ``` with line-anchored close
    match = re.search(r"```\s*\n(.+?)^```", text, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1).strip()

    # 处理截断情况：有开头的 ```python 但没有闭合 ```
    match = re.search(r"```python\s*\n(.+)", text, re.DOTALL)
    if match:
        log.warning("Code block truncated (no closing ```), extracting available code")
        return match.group(1).strip()

    # Final fallback: strip obvious non-code lines
    log.warning("No code block found in Claude output, using raw text as fallback")
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("Note", "Here", "This", "I ", "I'", "Let me", "Sure")):
            lines.append(line)
    return "\n".join(lines).strip()


def _dynamic_timeout(prompt_len: int, base: int = 120) -> int:
    """根据 prompt 长度动态计算超时，每 5000 字符额外加 30s，上限 360s。"""
    extra = max(0, (prompt_len - 5000)) // 5000 * 30
    return min(base + extra, 360)


_CONCISE_HINT = (
    "\n\nIMPORTANT: Your previous attempt was too long and got truncated. "
    "You MUST keep the code under 250 lines. Use minimal HTML/CSS. "
    "No decorative styling — only functional UI elements. "
    "Follow VibeHub UI style: Primary #cba186, bg #f0f2f5, white rounded cards."
)


def _is_truncation_error(syntax_err: str) -> bool:
    """判断语法错误是否由输出截断导致（未闭合的字符串/括号）"""
    truncation_hints = ("unterminated", "unexpected EOF", "expected an indented block")
    return any(h in syntax_err.lower() for h in truncation_hints)


def generate_tool_code(user_prompt: str, existing_code: str | None = None) -> str:
    """Generate/modify tool code via Claude CLI. Validates syntax and retries up to 2 times."""
    base_prompt = CODEGEN_RULES + "\n---\nUser request: " + user_prompt
    if existing_code:
        base_prompt += f"\n\n## Existing code (modify based on this):\n```python\n{existing_code}\n```"

    timeout = _dynamic_timeout(len(base_prompt))
    log.info(f"Generating tool code for: {user_prompt[:80]}...")

    syntax_err = None
    for attempt in range(3):
        # 截断重试时追加精简提示
        full_prompt = base_prompt
        if attempt > 0 and syntax_err and _is_truncation_error(syntax_err):
            full_prompt = base_prompt + _CONCISE_HINT
            log.info(f"Attempt {attempt + 1}: adding conciseness hint (truncation detected)")

        output = _call_claude(full_prompt, CODEGEN_SYSTEM_ROLE, timeout=timeout)
        code = _extract_python_code(output)

        syntax_err = _check_syntax(code)
        if syntax_err is None:
            log.info(f"Generated code: {len(code)} chars, syntax OK")
            return code

        log.warning(f"Generated tool code has syntax error (attempt {attempt + 1}): {syntax_err}")

    # 3次都失败，仍然返回（让后续测试阶段捕获）
    log.error(f"Tool code syntax error after 3 attempts: {syntax_err}")
    return code


def fix_tool_code(code: str, error_log: str) -> str:
    """Send error log + code to Claude for fixing.

    如果原始代码是因为截断导致的语法错误，直接用精简提示重新生成，
    而不是把一大段坏代码发回去"修复"。
    """
    syntax_err = _check_syntax(code)

    # 截断导致的错误 → 重新生成比"修复"更有效
    if syntax_err and _is_truncation_error(syntax_err):
        log.info("Code appears truncated, regenerating with concise hint instead of fixing")
        # 从错误日志中提取原始需求信息比较困难，
        # 所以仍然发送代码但只取前 150 行作为参考
        code_lines = code.splitlines()
        truncated_ref = "\n".join(code_lines[:150])
        full_prompt = CODEGEN_RULES + _CONCISE_HINT + "\n---\n"
        full_prompt += f"""Rewrite this script. The previous version was too long and got truncated.
Keep ALL the same functionality but use much more concise code (under 250 lines).

### Reference (first 150 lines of previous attempt):
```python
{truncated_ref}
```

### Error:
```
{error_log[:300]}
```"""
    else:
        # 正常修复流程，但限制代码长度避免 prompt 膨胀
        code_to_send = code
        if len(code) > 12000:
            log.warning(f"Code too large ({len(code)} chars), truncating to 12000 for fix prompt")
            code_to_send = code[:12000] + "\n# ... (truncated)"

        full_prompt = CODEGEN_RULES + "\n---\n"
        full_prompt += f"""The following Python script has errors. Fix it and output the complete corrected code.

### Original code:
```python
{code_to_send}
```

### Error log:
```
{error_log[:500]}
```

Output the fixed complete code following all mandatory rules."""

    timeout = _dynamic_timeout(len(full_prompt))
    log.info(f"Fixing tool code (prompt_len={len(full_prompt)}), error: {error_log[:100]}...")
    output = _call_claude(full_prompt, CODEGEN_SYSTEM_ROLE, timeout=timeout)
    fixed = _extract_python_code(output)
    log.info(f"Fixed code: {len(fixed)} chars")
    return fixed


def _check_syntax(code: str) -> str | None:
    """检查 Python 代码语法，返回 None 表示通过，否则返回错误信息。"""
    try:
        compile(code, "<test>", "exec")
        return None
    except SyntaxError as e:
        return f"Line {e.lineno}: {e.msg}"


def generate_test_code(tool_code: str) -> str:
    """Generate test script for tool code. Validates syntax and retries up to 2 times."""
    full_prompt = TEST_GEN_RULES + "\n---\n"
    full_prompt += f"Generate a test script for this web tool:\n```python\n{tool_code}\n```"

    for attempt in range(3):
        log.info(f"Generating test code (attempt {attempt + 1})...")
        output = _call_claude(full_prompt, TEST_GEN_SYSTEM_ROLE, timeout=60)
        code = _extract_python_code(output)

        syntax_err = _check_syntax(code)
        if syntax_err is None:
            log.info(f"Generated test code: {len(code)} chars, syntax OK")
            return code

        log.warning(f"Generated test code has syntax error: {syntax_err}, retrying...")

    # 3次都有语法错误，返回最后一次的结果（让调用方处理）
    log.error(f"Test code syntax error after 3 attempts: {syntax_err}")
    return code


def run_test(slug: str, test_code: str) -> tuple[bool, str]:
    """Execute test script, return (passed, log)."""
    test_dir = PROJECTS_DIR / slug
    test_file = test_dir / "_test_main.py"

    try:
        test_file.write_text(test_code, encoding="utf-8")
        port = find_free_port()
        log.info(f"Running test for [{slug}] on port {port}")

        result = subprocess.run(
            [str(UV_EXE), "run", str(test_file)],
            env={**os.environ, "PORT": str(port)},
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            cwd=str(test_dir),
        )

        passed = result.returncode == 0
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        output = (stdout + "\n" + stderr).strip()
        log.info(f"Test [{slug}] {'PASSED' if passed else 'FAILED'}: {output[:200]}")
        return passed, output
    except subprocess.TimeoutExpired:
        log.error(f"Test [{slug}] timed out (60s)")
        return False, "Test timed out (60s)"
    finally:
        test_file.unlink(missing_ok=True)
