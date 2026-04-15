import json
from typing import Dict, Any, List
from src.agents.gemini_evaluator import GeminiEvaluator
from src.config import PROJECT_ID, LOCATION, GEMINI_MODEL_ID

class CleanSlateManager:
    """
    Implements the 'Clean Slate Protocol'.
    Summarizes current context into artifacts and prepares for session resets.
    """
    def __init__(self):
        self.evaluator = GeminiEvaluator(
            project_id=PROJECT_ID, 
            location=LOCATION, 
            model_id=GEMINI_MODEL_ID
        )

    def summarize_and_reset(self, session_history: str, current_artifacts: List[str]) -> str:
        """
        Takes long session history and summarizes it into a new 'project_context_vN.md'.
        Returns the path to the new artifact.
        """
        print(f"[CleanSlateManager] Summarizing long session history for reset...")
        
        prompt = f"""
        당신은 프로젝트의 'Context Manager'입니다.
        현재까지의 세션 기록(Session History)을 분석하여, 다음 세션에서 반드시 알아야 할 핵심 상태와 아티팩트 정보를 요약하십시오.
        불필요한 대화나 중간 과정은 생략하고, 최종 결론과 현재의 '진실의 원천(Source of Truth)'만 남기십시오.
        
        ### Current Artifacts:
        {", ".join(current_artifacts)}
        
        ### Session History:
        {session_history}
        
        응답은 Markdown 형식으로 작성하십시오.
        """
        
        response = self.evaluator.evaluate(
            content=session_history,
            contract="Summarize everything into a clean 'project_context.md' format."
        )
        
        summary = response.get("evaluation", "")
        
        # Save to artifacts directory
        import time
        version = int(time.time())
        artifact_path = f"artifacts/project_context_v{version}.md"
        
        with open(artifact_path, "w") as f:
            f.write(summary)
            
        print(f"✅ Clean Slate Artifact Created: {artifact_path}")
        return artifact_path

    def should_reset(self, turn_count: int, context_usage: float) -> bool:
        """
        Logic to determine if a reset is needed (e.g., based on turn count or estimated context).
        Anthropic suggests proactive resets before performance degrades.
        """
        if turn_count >= 10:
            return True
        if context_usage >= 0.8: # 80% of context window used
            return True
        return False

if __name__ == "__main__":
    # Test scaffolding
    # manager = CleanSlateManager()
    # manager.summarize_and_reset("Long history string...", ["PLAN.md", "DEFINE.md"])
    pass
