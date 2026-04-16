import json
import os

import anthropic
from anthropic import AnthropicVertex
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

MODEL_ID: str = os.getenv("CLAUDE_MODEL_ID", "claude-sonnet-4-6")
MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "8192"))

_SYSTEM_PROMPT = (
    "You are a senior software engineer. "
    "Implement the task strictly according to the Sprint Contract (DoD). "
    "Respond with clean, production-ready code only."
)


def create_client() -> AnthropicVertex:
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    region = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    return AnthropicVertex(region=region, project_id=project_id)


@retry(
    retry=retry_if_exception_type(
        (anthropic.APIStatusError, anthropic.APIConnectionError)
    ),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def _call_api(client: AnthropicVertex, **kwargs):
    """Vertex AI API 호출. rate limit·네트워크 오류 시 최대 3회 지수 백오프 재시도."""
    return client.messages.create(**kwargs)


def generate(task: str, contract: str, feedback: str = "") -> dict:
    """Claude Vertex AI를 호출하여 코드를 생성하거나 개선한다.

    Args:
        task: 사용자 작업 설명
        contract: JSON 형식의 Sprint Contract (DoD 포함)
        feedback: Evaluator의 이전 피드백 (최초 호출 시 빈 문자열)

    Returns:
        dict: {
            "text": 생성된 코드 문자열,
            "input_tokens": 입력 토큰 수,
            "output_tokens": 출력 토큰 수,
            "truncated": max_tokens 도달 여부,
        }

    Raises:
        ValueError: contract가 유효한 JSON이 아닐 때
        anthropic.APIStatusError: 재시도 후에도 API 오류가 지속될 때
        anthropic.APIConnectionError: 재시도 후에도 네트워크 오류가 지속될 때
    """
    try:
        json.loads(contract)
    except json.JSONDecodeError as e:
        raise ValueError(f"contract must be valid JSON: {e}") from e

    client = create_client()
    prompt = _build_prompt(task, contract, feedback)

    message = _call_api(
        client,
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "text": _extract_text(message.content),
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "truncated": message.stop_reason == "max_tokens",
    }


def _extract_text(content: list) -> str:
    """content block 목록에서 텍스트를 안전하게 추출한다.

    TextBlock만 수집하며, 복수의 블록은 이어붙여 반환한다.

    Raises:
        ValueError: 텍스트 블록이 하나도 없을 때
    """
    parts = [block.text for block in content if hasattr(block, "text")]
    if not parts:
        raise ValueError("No text content in Claude response.")
    return "".join(parts)


def _build_prompt(task: str, contract: str, feedback: str) -> str:
    base = f"### Task:\n{task}\n\n### Sprint Contract (DoD):\n{contract}"
    if feedback:
        return (
            base
            + f"\n\n### Previous Feedback:\n{feedback}"
            + "\n\nRefine your implementation to address all feedback points."
        )
    return base + "\n\nImplement strictly according to the Contract above."
