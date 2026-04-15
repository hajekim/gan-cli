import json
import time
from typing import Dict, Any, List
from src.agents.claude_generator import ClaudeGenerator
from src.contract.manager import ContractManager
from src.contract.validator import ContractValidator
from src.config import PROJECT_ID, LOCATION, CLAUDE_MODEL_ID

class GANOrchestrator:
    """
    Orchestrates the GAN-inspired loop between Claude (Generator) and Gemini (Evaluator).
    Follows Anthropic's Harness-driven design.
    """
    def __init__(self, max_refinements: int = 3):
        self.contract_manager = ContractManager()
        self.generator = ClaudeGenerator(project_id=PROJECT_ID, region=LOCATION, model_id=CLAUDE_MODEL_ID)
        self.validator = ContractValidator()
        self.max_refinements = max_refinements

    def run_sprint(self, task_description: str) -> Dict[str, Any]:
        """
        Executes a complete sprint: 
        1. Create Contract -> 2. Generate -> 3. Validate -> 4. Refine (Loop)
        """
        print(f"\n🚀 Starting New Sprint: {task_description[:50]}...")
        
        # 1. Create Sprint Contract (The Brain plans)
        contract = self.contract_manager.create_contract(task_description)
        if "error" in contract:
            return {"status": "FAILED", "error": "Contract generation failed."}
        
        print(f"📄 Sprint Contract Created: {contract.get('title')}")
        print(f"🎯 Objective: {contract.get('objective')}")

        # 2 & 3. Iterative GAN Loop
        current_submission = ""
        current_feedback = ""
        iteration = 0
        
        while iteration < self.max_refinements:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}/{self.max_refinements}...")

            # 2. Generator (The Hands) implements
            prompt = self._build_generator_prompt(task_description, contract, current_submission, current_feedback)
            current_submission = self.generator.generate(prompt)
            
            # 3. Evaluator (The Brain) judges
            result = self.validator.validate(current_submission, contract)
            
            grade = result.get("grade", "C")
            feedback = result.get("feedback", "No feedback provided.")
            pass_fail = result.get("pass_fail", "Fail")
            
            print(f"📊 Evaluation Result: Grade {grade} ({pass_fail})")
            
            if grade == "A" or pass_fail.lower() == "pass":
                print("✅ Sprint Objective Achieved!")
                return {
                    "status": "SUCCESS",
                    "iteration": iteration,
                    "final_submission": current_submission,
                    "contract": contract,
                    "evaluation": result
                }
            
            # Prepare for next iteration
            current_feedback = feedback
            print(f"💡 Feedback for refinement: {feedback[:100]}...")

        print("⚠️ Max refinements reached without Grade A.")
        return {
            "status": "PARTIAL_SUCCESS",
            "iteration": iteration,
            "final_submission": current_submission,
            "contract": contract,
            "evaluation": result
        }

    def _build_generator_prompt(self, task: str, contract: Dict[str, Any], last_submission: str, feedback: str) -> str:
        """
        Constructs the prompt for Claude (Generator) based on current state.
        """
        contract_str = json.dumps(contract, indent=2, ensure_ascii=False)
        
        if not last_submission:
            return f"""
            ### Task:
            {task}
            
            ### Sprint Contract (DoD):
            {contract_str}
            
            Implement the requirements strictly according to the Contract (DoD) above.
            """
        else:
            return f"""
            ### Task:
            {task}
            
            ### Previous Submission:
            {last_submission}
            
            ### Feedback from Evaluator (Skeptical Judge):
            {feedback}
            
            ### Sprint Contract (DoD):
            {contract_str}
            
            Refine your implementation based on the feedback to satisfy ALL points in the Contract.
            """

if __name__ == "__main__":
    # Example execution
    orchestrator = GANOrchestrator(max_refinements=2)
    # result = orchestrator.run_sprint("Python으로 가위바위보 게임을 만드세요. 점수 기록 기능이 포함되어야 합니다.")
    # print(result.get("status"))
