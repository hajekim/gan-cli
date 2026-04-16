"""FastMCP server exposing Claude Vertex AI and artifact management tools to Gemini CLI."""
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from filelock import FileLock
from mcp.server.fastmcp import FastMCP

from src.tools.claude_tool import generate as _claude_generate

# Anchor all relative paths to the project root regardless of cwd when invoked globally.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ARTIFACTS_DIR = _PROJECT_ROOT / "artifacts"
_STATE_FILE = _PROJECT_ROOT / "state" / "progress.json"
_LOCK_FILE = _STATE_FILE.with_suffix(".lock")

load_dotenv(_PROJECT_ROOT / ".env")

mcp = FastMCP("claude-gan")


@mcp.tool()
def claude_generate(task: str, contract: str, feedback: str = "") -> str:
    """Generate or refine code using Claude 4.6 Sonnet on Vertex AI.

    Args:
        task: Description of the implementation task.
        contract: Sprint Contract as a JSON string (must include definition_of_done).
        feedback: Evaluator feedback from a previous iteration. Omit on first call.

    Returns:
        Generated code string. Includes USAGE metadata at the end for token tracking.
        If truncated, includes a WARNING comment before USAGE.
    """
    result = _claude_generate(task=task, contract=contract, feedback=feedback)
    text = result["text"]

    if result["truncated"]:
        text += "\n\n# WARNING: Response was truncated due to max_tokens limit."

    text += (
        f"\n\n# USAGE: input_tokens={result['input_tokens']},"
        f" output_tokens={result['output_tokens']}"
    )
    return text


@mcp.tool()
def save_artifact(content: str, filename: str) -> str:
    """Save generated output to the artifacts/ directory.

    Args:
        content: The content to save (code, text, etc.).
        filename: File name only — no path separators allowed (e.g. 'solution.py').

    Returns:
        Absolute path of the saved file.
    """
    safe_name = Path(filename).name
    if "\x00" in filename or safe_name != filename or not safe_name:
        raise ValueError(
            f"Invalid filename '{filename}': must be a plain file name with no path separators."
        )

    try:
        _ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        path = _ARTIFACTS_DIR / safe_name
        path.write_text(content, encoding="utf-8")
    except OSError as e:
        raise RuntimeError(f"Failed to save artifact '{safe_name}': {e}") from e

    return str(path)


@mcp.tool()
def load_progress() -> str:
    """Load the current sprint state from state/progress.json.

    Returns:
        JSON string of the current state, or '{}' if no state file exists yet.
    """
    with FileLock(_LOCK_FILE):
        try:
            return json.dumps(
                json.loads(_STATE_FILE.read_text(encoding="utf-8")),
                ensure_ascii=False,
            )
        except (FileNotFoundError, json.JSONDecodeError):
            return "{}"


@mcp.tool()
def save_progress(
    sprint_id: str,
    status: str,
    grade: str = "",
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> str:
    """Persist the current sprint status to state/progress.json.

    Args:
        sprint_id: Sprint identifier (e.g. 'SPRINT-001').
        status: One of 'IN_PROGRESS', 'SUCCESS', or 'PARTIAL_SUCCESS'.
        grade: Evaluator grade ('A', 'B', or 'C').
        input_tokens: Input token count from the last claude_generate call.
        output_tokens: Output token count from the last claude_generate call.

    Returns:
        Confirmation message.
    """
    state = {
        "sprint_id": sprint_id,
        "status": status,
        "grade": grade,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tokens": {"input": input_tokens, "output": output_tokens},
    }

    with FileLock(_LOCK_FILE):
        try:
            _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            _STATE_FILE.write_text(
                json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as e:
            raise RuntimeError(f"Failed to save progress: {e}") from e

    return f"Progress saved: {sprint_id} → {status} (Grade: {grade or 'N/A'})"


if __name__ == "__main__":
    mcp.run()
