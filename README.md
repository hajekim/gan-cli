# Claude-GAN Extension for Gemini CLI

A development system that connects **Gemini CLI (Evaluator)** and **Claude 4.6 Sonnet (Generator)** via a GAN-inspired refinement loop, built on **Anthropic's Harness Engineering** philosophy.

## 🎯 Overview

Gemini CLI acts natively as the **Skeptical Judge and Architect** (Brain), while **Claude 4.6 Sonnet** on Vertex AI handles code generation (Hands) via an MCP tool. The two models iterate through a **Generator-Evaluator (GAN)** loop until the implementation meets a rigorous **Sprint Contract (DoD)**.

## 🏗 System Architecture (MCP-Based)

```
Gemini CLI (Evaluator / Brain)
  │  ┌────────────────────────────────────────────────┐
  │  │  1. Write Sprint Contract (native reasoning)   │
  │  │  2. Call claude_generate MCP tool  ────────────┼──▶ Claude API (Vertex AI)
  │  │  3. Evaluate result (native reasoning) ◀───────┼─── generated code
  │  │  4. Repeat until Grade A                       │
  │  └────────────────────────────────────────────────┘
```

- **The Brain (Gemini CLI):** Writes the Sprint Contract (JSON DoD), performs skeptical evaluation, and orchestrates the loop — all natively within the CLI session.
- **The Hands (Claude 4.6 Sonnet):** Executes implementation via the `claude_generate` MCP tool (Vertex AI global endpoint).
- **The MCP Server (`src/mcp_server.py`):** Exposes `claude_generate`, `save_artifact`, `load_progress`, and `save_progress` tools to Gemini CLI over stdio transport.

## 📋 Prerequisites

1. **Google Cloud Project:** A project with the **Vertex AI API** enabled.
2. **Anthropic on Vertex AI:** Access to **Claude 4.6 Sonnet** in the `global` region.
3. **Gemini CLI:** Installed and authenticated (`gemini auth login`).
4. **Python 3.10+** with `pip`.

## 🛠 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/claude-gan.git
cd claude-gan
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
cp .env.template .env
# Edit .env: set GOOGLE_CLOUD_PROJECT to your GCP project ID
```

Or export directly:

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=global
```

### 4. Register the Extension

```bash
gemini extensions link .
```

## 🚀 Usage

Once registered, GEMINI.md is automatically loaded as context for every Gemini CLI session. No slash command needed — just describe your task naturally:

```
Implement a FastAPI server with JWT authentication. Run the GAN loop.
```

```
Python으로 가위바위보 게임을 만들어줘. GAN 루프로 진행해.
```

Gemini CLI will:
1. Write a Sprint Contract (DoD) using its own reasoning
2. Call `claude_generate` to get an implementation from Claude
3. Evaluate the result against the contract
4. Iterate with specific feedback until Grade A is achieved

### Output

- Final code → `artifacts/solution_SPRINT-XXX.py`
- Sprint state → `state/progress.json`

## 🧠 Core Patterns

- **Sprint Contract:** Gemini defines a JSON-based DoD before any implementation begins.
- **Skeptical Judge:** Gemini evaluates against concrete criteria (functionality, edge cases, security, code quality).
- **MCP Tool Integration:** Claude is a callable tool, not a subprocess — the GAN loop runs entirely within the Gemini CLI session.

## 📄 License

MIT License
