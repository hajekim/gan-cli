import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or "YOUR_PROJECT_ID"
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

# Model IDs for 2026-04
CLAUDE_MODEL_ID = "claude-4-6-sonnet@20260217"
GEMINI_MODEL_ID = "gemini-3.1-pro"

# Common settings
THINKING_BUDGET = 16000
MAX_TOKENS = 4096
