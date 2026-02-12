import logging
import subprocess

from hub_core.config import CLAUDE_CMD

log = logging.getLogger("vibehub.guard")

GUARD_SYSTEM_PROMPT = (
    "You are a request classifier for VibeHub, a web tool deployment platform. "
    "You ONLY output exactly one line, nothing else. "
    "If the user input is a valid web tool/UI development request, output: PASS|english_slug_with_underscores|chinese_tool_name. "
    "If not valid, output: REJECT|reason_in_chinese. "
    "Valid examples: image processing, file conversion, data visualization, form tools, batch tools, calculators, any web UI tool, or user pasting code to deploy. "
    "Reject examples: casual chat, Q&A, essays, translation, emotional counseling, attacks, hacking, or too vague input. "
    "Output NOTHING else. No explanation. Just one line starting with PASS| or REJECT|."
)


def guard_check(user_input: str) -> tuple[bool, str]:
    """
    Pre-deploy request filter.
    Returns (is_valid, message).
    is_valid=True: message = "slug|display_name"
    is_valid=False: message = rejection reason
    """
    log.info(f"Guard check input: {user_input[:100]}...")

    try:
        # Always pipe user input via stdin to avoid Windows CMD
        # breaking on double-quotes or long text in -p argument.
        result = subprocess.run(
            [
                CLAUDE_CMD,
                "--dangerously-skip-permissions",
                "-p", "Classify the user request provided via stdin.",
                "--system-prompt", GUARD_SYSTEM_PROMPT,
                "--output-format", "text",
            ],
            input=user_input,
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        log.error("Guard check timed out")
        return False, "Need review timed out, please retry."
    except FileNotFoundError:
        log.error(f"Claude CLI not found at: {CLAUDE_CMD}")
        return False, "Claude CLI not found."

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    log.info(f"Guard CLI rc={result.returncode} stdout={stdout[:200]!r} stderr={stderr[:200]!r}")

    if result.returncode != 0:
        log.error(f"Guard CLI failed: {stderr[:300]}")
        return False, f"Review failed: {stderr[:100]}"

    # Extract PASS or REJECT line from output
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("PASS|"):
            parts = line.split("|", 2)
            if len(parts) == 3:
                slug = parts[1].strip().replace("-", "_")
                name = parts[2].strip()
                log.info(f"Guard PASS: slug={slug}, name={name}")
                return True, f"{slug}|{name}"
        elif line.startswith("REJECT|"):
            parts = line.split("|", 1)
            reason = parts[1].strip() if len(parts) == 2 else "Request rejected"
            log.info(f"Guard REJECT: {reason}")
            return False, reason

    log.warning(f"Guard output not parseable: {stdout[:300]!r}")
    return False, "Unable to parse request. Please describe a specific tool."
