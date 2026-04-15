"""FastMCP server exposing Claude Vertex AI and artifact management tools to Gemini CLI."""
import json
import os
import time

from mcp.server.fastmcp import FastMCP

from src.tools.claude_tool import generate as _claude_generate

mcp = FastMCP("claude-generator")


@mcp.tool()
def claude_generate(task: str, contract: str, feedback: str = "") -> str:
    """Claude 4.6 Sonnet (Vertex AI)으로 코드를 생성하거나 개선한다.

    Args:
        task: 구현할 작업 설명
        contract: JSON 형식의 Sprint Contract (definition_of_done 포함)
        feedback: Evaluator의 피드백 (재시도 시 제공, 최초 호출 시 생략)
    """
    return _claude_generate(task=task, contract=contract, feedback=feedback)


@mcp.tool()
def save_artifact(content: str, filename: str) -> str:
    """결과물을 artifacts/ 디렉토리에 저장한다.

    Args:
        content: 저장할 내용 (코드, 텍스트 등)
        filename: 저장할 파일명 (예: 'final_solution.py')

    Returns:
        저장된 파일의 경로
    """
    os.makedirs("artifacts", exist_ok=True)
    path = os.path.join("artifacts", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


@mcp.tool()
def load_progress() -> str:
    """state/progress.json에서 현재 스프린트 진행 상태를 로드한다.

    Returns:
        JSON 문자열 (파일 없으면 빈 객체 '{}')
    """
    try:
        with open("state/progress.json", encoding="utf-8") as f:
            return json.dumps(json.load(f), ensure_ascii=False)
    except FileNotFoundError:
        return "{}"


@mcp.tool()
def save_progress(sprint_id: str, status: str, grade: str = "") -> str:
    """현재 스프린트 상태를 state/progress.json에 저장한다.

    Args:
        sprint_id: 스프린트 식별자 (예: 'SPRINT-001')
        status: 현재 상태 ('IN_PROGRESS', 'SUCCESS', 'PARTIAL_SUCCESS')
        grade: Evaluator 평가 등급 ('A', 'B', 'C')

    Returns:
        저장 결과 메시지
    """
    os.makedirs("state", exist_ok=True)
    state = {
        "sprint_id": sprint_id,
        "status": status,
        "grade": grade,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open("state/progress.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    return f"Progress saved: {sprint_id} → {status} (Grade: {grade or 'N/A'})"


if __name__ == "__main__":
    mcp.run()
