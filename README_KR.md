# Claude-GAN: Gemini CLI용 확장 도구

**Gemini CLI (Evaluator)**와 **Claude 4.6 Sonnet (Generator)**을 GAN 기반의 품질 개선 루프로 연결한 개발 시스템입니다. **Anthropic Harness Engineering** 철학에 따라 설계되었습니다.

## 🎯 개요

Gemini CLI가 **Skeptical Judge(회의적인 심사위원) 및 Architect** 역할(Brain)을 네이티브로 수행하고, **Claude 4.6 Sonnet**이 Vertex AI를 통해 MCP 도구로 호출되어 코드 생성(Hands)을 담당합니다. 두 모델은 구현이 엄격한 **Sprint Contract (DoD)**를 충족할 때까지 **Generator-Evaluator (GAN)** 루프를 반복합니다.

## 🏗 시스템 아키텍처 (MCP 기반)

```
Gemini CLI (Evaluator / Brain)
  │  ┌────────────────────────────────────────────────┐
  │  │  1. Sprint Contract 직접 작성 (네이티브 추론)  │
  │  │  2. claude_generate MCP 도구 호출 ─────────────┼──▶ Claude API (Vertex AI)
  │  │  3. 결과물 직접 평가 (네이티브 추론) ◀─────────┼─── 생성된 코드
  │  │  4. Grade A까지 반복                           │
  │  └────────────────────────────────────────────────┘
```

- **The Brain (Gemini CLI):** Sprint Contract(JSON DoD) 작성, 비판적 평가, GAN 루프 오케스트레이션을 CLI 세션 내에서 네이티브로 수행.
- **The Hands (Claude 4.6 Sonnet):** `claude_generate` MCP 도구를 통해 코드 생성 (Vertex AI global endpoint).
- **The MCP Server (`src/mcp_server.py`):** `claude_generate`, `save_artifact`, `load_progress`, `save_progress` 도구를 stdio transport로 Gemini CLI에 노출.

## 📋 사전 준비 사항

1. **Google Cloud Project:** **Vertex AI API**가 활성화된 프로젝트.
2. **Anthropic on Vertex AI:** `global` 리전에서 **Claude 4.6 Sonnet** 접근 권한.
3. **Gemini CLI:** 설치 및 인증 완료 (`gemini auth login`).
4. **Python 3.10+** 및 `pip`.

## 🛠 설치 및 설정

### 1. 리포지토리 클론

```bash
git clone https://github.com/your-repo/claude-gan.git
cd claude-gan
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
cp .env.template .env
# .env 파일을 열어 GOOGLE_CLOUD_PROJECT를 본인의 GCP 프로젝트 ID로 설정
```

또는 직접 export:

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=global
```

### 4. 확장 등록

```bash
gemini extensions link .
```

## 🚀 사용 방법

등록 후에는 Gemini CLI 세션마다 GEMINI.md가 자동으로 컨텍스트로 로드됩니다. 별도의 슬래시 커맨드 없이 자연어로 작업을 요청하면 됩니다:

```
FastAPI 서버에 JWT 인증을 구현해줘. GAN 루프로 진행해.
```

```
Python으로 가위바위보 게임을 만들어줘. GAN 루프로 진행해.
```

Gemini CLI가 자동으로:
1. 자체 추론으로 Sprint Contract(DoD) 작성
2. `claude_generate` 도구로 Claude에게 구현 요청
3. 계약 기준으로 결과물 평가
4. Grade A 달성까지 구체적인 피드백으로 반복

### 결과물

- 최종 코드 → `artifacts/solution_SPRINT-XXX.py`
- 스프린트 상태 → `state/progress.json`

## 🧠 핵심 패턴

- **Sprint Contract:** 구현 전 Gemini가 JSON 기반 DoD를 직접 정의.
- **Skeptical Judge:** Gemini가 기능 완전성, 엣지 케이스, 보안, 코드 품질 기준으로 엄격하게 평가.
- **MCP 도구 통합:** Claude는 서브프로세스가 아닌 호출 가능한 도구 — GAN 루프 전체가 Gemini CLI 세션 내에서 실행.

## 📄 라이선스

MIT License
