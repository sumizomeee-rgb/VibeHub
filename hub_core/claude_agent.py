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

8. Output ONLY the Python code inside a ```python code block. Nothing else.
"""

TEST_GEN_RULES = """\
Generate a lightweight test script for the given web tool.

Requirements:
1. Use httpx as HTTP client.
2. Use subprocess to start the target app (main.py) with PORT env var.
3. Cover: app starts on port, GET / returns 2xx, bad params don't crash.
4. exit(0) on pass, exit(1) on fail with reason.
5. PEP 723 header (TOML values MUST be double-quoted):
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
6. Timeout 15s max. Kill target process when done.

Output ONLY the test code inside a ```python code block. Nothing else.
"""


def _call_claude(user_prompt: str, system_prompt: str, timeout: int = 120) -> str:
    """Call Claude CLI, always piping user_prompt via stdin.

    system_prompt goes to --system-prompt (must be short, no double-quotes).
    user_prompt (which may contain rules + code with double-quotes) is piped
    via stdin to bypass Windows CMD argument length and quoting limits.
    """
    flat_system = " ".join(system_prompt.replace("\r", "").split())

    cmd = [
        CLAUDE_CMD,
        "--dangerously-skip-permissions",
        "-p", "Follow the instructions provided via stdin.",
        "--system-prompt", flat_system,
        "--output-format", "text",
    ]

    log.info(f"Calling Claude CLI (timeout={timeout}s, prompt_len={len(user_prompt)})")

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

    if result.returncode != 0:
        log.error(f"Claude CLI error: {stderr[:500]}")
        raise RuntimeError(f"Claude CLI error (code={result.returncode}): {stderr[:500]}")

    if not stdout.strip():
        log.error("Claude CLI returned empty output")
        raise RuntimeError("Claude CLI returned empty output")

    return stdout


def _extract_python_code(text: str) -> str:
    """Extract Python code block from Claude output."""
    # Match ```python ... ```
    match = re.search(r"```python\s*\n(.+?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: any ``` ... ```
    match = re.search(r"```\s*\n(.+?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Final fallback: treat entire output as code
    log.warning("No code block found in Claude output, using raw text as fallback")
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("Note", "Here", "This", "I ")):
            lines.append(line)
    return "\n".join(lines).strip()


def generate_tool_code(user_prompt: str, existing_code: str | None = None) -> str:
    """Generate/modify tool code via Claude CLI."""
    full_prompt = CODEGEN_RULES + "\n---\nUser request: " + user_prompt
    if existing_code:
        full_prompt += f"\n\n## Existing code (modify based on this):\n```python\n{existing_code}\n```"

    log.info(f"Generating tool code for: {user_prompt[:80]}...")
    output = _call_claude(full_prompt, CODEGEN_SYSTEM_ROLE)
    code = _extract_python_code(output)
    log.info(f"Generated code: {len(code)} chars")
    return code


def fix_tool_code(code: str, error_log: str) -> str:
    """Send error log + code to Claude for fixing."""
    full_prompt = CODEGEN_RULES + "\n---\n"
    full_prompt += f"""The following Python script has errors. Fix it and output the complete corrected code.

### Original code:
```python
{code}
```

### Error log:
```
{error_log}
```

Output the fixed complete code following all mandatory rules."""

    log.info(f"Fixing tool code, error: {error_log[:100]}...")
    output = _call_claude(full_prompt, CODEGEN_SYSTEM_ROLE)
    fixed = _extract_python_code(output)
    log.info(f"Fixed code: {len(fixed)} chars")
    return fixed


def generate_test_code(tool_code: str) -> str:
    """Generate test script for tool code."""
    full_prompt = TEST_GEN_RULES + "\n---\n"
    full_prompt += f"Generate a test script for this web tool:\n```python\n{tool_code}\n```"
    log.info("Generating test code...")
    output = _call_claude(full_prompt, TEST_GEN_SYSTEM_ROLE, timeout=60)
    code = _extract_python_code(output)
    log.info(f"Generated test code: {len(code)} chars")
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
        output = (result.stdout + "\n" + result.stderr).strip()
        log.info(f"Test [{slug}] {'PASSED' if passed else 'FAILED'}: {output[:200]}")
        return passed, output
    except subprocess.TimeoutExpired:
        log.error(f"Test [{slug}] timed out (60s)")
        return False, "Test timed out (60s)"
    finally:
        test_file.unlink(missing_ok=True)
