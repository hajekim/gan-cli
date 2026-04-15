import json
from typing import Dict, Any
from src.agents.gemini_evaluator import GeminiEvaluator
from src.config import PROJECT_ID, LOCATION, GEMINI_MODEL_ID

class ContractValidator:
    """
    Validates the 'Submitted Content' from Generator (Claude) against the 'Sprint Contract'.
    Acts as the 'Skeptical Judge'.
    """
    def __init__(self):
        self.evaluator = GeminiEvaluator(
            project_id=PROJECT_ID, 
            location=LOCATION, 
            model_id=GEMINI_MODEL_ID
        )

    def validate(self, content: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates content against the JSON contract and returns a structured Grade and Feedback.
        """
        print(f"[ContractValidator] Validating submission against contract {contract.get('task_id', 'Unknown')}...")
        
        contract_str = json.dumps(contract, indent=2, ensure_ascii=False)
        
        response = self.evaluator.evaluate(
            content=content,
            contract=contract_str
        )
        
        # Parsing the evaluation result
        try:
            raw_text = response.get("evaluation", "")
            # Basic cleanup for JSON extraction
            if "```json" in raw_text:
                json_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                json_text = raw_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = raw_text.strip()
                
            result = json.loads(json_text)
            # Merge with raw thoughts if available
            result["thoughts"] = response.get("thoughts")
            return result
        except Exception as e:
            print(f"[ContractValidator] Failed to parse evaluation: {e}")
            return {
                "grade": "C", 
                "feedback": f"Failed to parse evaluation: {e}. Raw Output: {response.get('evaluation')[:200]}...",
                "pass_fail": "Fail"
            }

if __name__ == "__main__":
    # Test case: Implement a basic Python web server
    validator = ContractValidator()
    # Mock data
    # contract = {...}
    # content = "Mock FastAPI implementation code..."
    # result = validator.validate(content, contract)
    # print(json.dumps(result, indent=2, ensure_ascii=False))
