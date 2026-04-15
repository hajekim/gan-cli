import json
from typing import Dict, Any, List
from src.agents.gemini_evaluator import GeminiEvaluator
from src.config import PROJECT_ID, LOCATION, GEMINI_MODEL_ID

class ContractManager:
    """
    Manages the 'Sprint Contract' lifecycle. 
    Uses Gemini 3.1 Pro to decompose tasks into a formal JSON-based 'Definition of Done'.
    """
    def __init__(self):
        self.evaluator = GeminiEvaluator(
            project_id=PROJECT_ID, 
            location=LOCATION, 
            model_id=GEMINI_MODEL_ID
        )

    def create_contract(self, task_description: str) -> Dict[str, Any]:
        """
        Generates a formal Sprint Contract from a raw task description.
        """
        print(f"[ContractManager] Analyzing task and generating Sprint Contract...")
        
        prompt = f"""
        You are a Senior Architect and Project Manager.
        Analyze the following 'Task Description' and create a formal 'Sprint Contract' in JSON format for the development agent (Claude).
        
        ### Task Description:
        {task_description}
        
        ### JSON Response Format:
        {{
            "task_id": "SPRINT-XXX",
            "title": "Short descriptive title",
            "objective": "High-level goal",
            "definition_of_done": [
                "Detailed, measurable criterion 1",
                "Detailed, measurable criterion 2",
                ...
            ],
            "constraints": [
                "Coding standard or technology constraint 1",
                ...
            ],
            "verification_steps": [
                "Specific shell command or test to run for verification"
            ]
        }}
        
        Your response must ONLY be the raw JSON code block.
        """
        
        # We reuse the evaluator's client for generation here
        response = self.evaluator.evaluate(
            content=task_description, 
            contract="Formal JSON Schema for Sprint Contract"
        )
        
        # Parsing the JSON from the evaluation result (assuming formatted response)
        try:
            raw_text = response.get("evaluation", "")
            # Basic cleanup if markdown backticks are present
            if "```json" in raw_text:
                json_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                json_text = raw_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = raw_text.strip()
                
            contract = json.loads(json_text)
            return contract
        except Exception as e:
            print(f"[ContractManager] Failed to parse contract: {e}")
            return {"error": "Invalid JSON from Evaluator", "raw_output": response.get("evaluation")}

if __name__ == "__main__":
    # Test case: Implement a basic Python web server
    manager = ContractManager()
    contract = manager.create_contract("FastAPI를 사용하여 간단한 Hello World API 서버를 만드세요.")
    print(json.dumps(contract, indent=2, ensure_ascii=False))
