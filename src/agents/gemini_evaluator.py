import os
from typing import Dict, Any
from google import genai
from google.genai import types

class GeminiEvaluator:
    """
    Evaluator Agent using Gemini 3.1 Pro (Deep Thinking).
    Updated for 2026 SDK and model versions.
    """
    def __init__(self, project_id: str = None, location: str = "global", model_id: str = "gemini-3.1-pro"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.model_id = model_id
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set or provided.")

        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location
        )

    def evaluate(self, content: str, contract: str, thinking_budget: int = 16000) -> Dict[str, Any]:
        """
        Evaluates the provided content against the contract using Gemini 3.1 Deep Thinking.
        """
        print(f"[GeminiEvaluator] Deep Thinking evaluation with budget: {thinking_budget}...")
        
        prompt = f"""
        You are a Senior Staff Engineer acting as a 'Skeptical Judge'.
        Evaluate the submitted 'Content' critically based on the 'Sprint Contract'.
        Your final output must be in JSON format including (Grade: A, B, C / Feedback / Pass/Fail).
        
        ### Sprint Contract:
        {contract}
        
        ### Submitted Content:
        {content}
        
        Analyze any logical flaws, security vulnerabilities, or deviations from the DoD.
        Provide constructive but strict feedback for improvement.
        """
        
        try:
            # Thinking mode configuration (Gemini 3.1+)
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(include_thoughts=True),
                    # 2026 SDK feature: Thinking budget as a direct parameter
                    # budget_tokens=thinking_budget, 
                    temperature=0.0
                )
            )
            
            return {
                "evaluation": response.text,
                "thoughts": getattr(response, 'thought', "Thinking traces not available.")
            }
        except Exception as e:
            print(f"[GeminiEvaluator] Error: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    try:
        evaluator = GeminiEvaluator()
        # print(evaluator.evaluate("Sample code", "DoD: Rust Hello World"))
    except Exception as e:
        print(f"Setup Error: {e}")
