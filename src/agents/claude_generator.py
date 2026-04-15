import os
from anthropic import AnthropicVertex

class ClaudeGenerator:
    """
    Generator Agent using Claude 4.6 Sonnet on Vertex AI.
    Handles code generation and implementation tasks.
    Updated for 2026 SDK (anthropic[vertex]>=0.94.0).
    """
    def __init__(self, project_id: str = None, region: str = "global", model_id: str = "claude-4-6-sonnet@20260217"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.region = region
        self.model_id = model_id
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set or provided.")
            
        # Initialize AnthropicVertex client
        self.client = AnthropicVertex(region=self.region, project_id=self.project_id)

    def generate(self, prompt: str, system_instruction: str = "You are a senior software engineer.") -> str:
        """
        Sends a request to Claude 4.6 Sonnet on Vertex AI using the official SDK.
        """
        print(f"[ClaudeGenerator] Generating with {self.model_id} via {self.region} endpoint...")
        
        try:
            message = self.client.messages.create(
                model=self.model_id,
                max_tokens=4096,
                system=system_instruction,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"[ClaudeGenerator] Error: {str(e)}")
            return f"Error during generation: {str(e)}"

if __name__ == "__main__":
    # Test (requires GOOGLE_CLOUD_PROJECT to be set)
    try:
        gen = ClaudeGenerator(region="global")
        # result = gen.generate("Write a 'Hello World' in Rust.")
        # print(result)
    except Exception as e:
        print(f"Setup Error: {e}")
