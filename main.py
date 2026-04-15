import sys
import argparse
from src.orchestration.gan_loop import GANOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Gemini-Claude GAN Agent Orchestrator")
    parser.add_argument("task", type=str, help="The task for the agents to implement.")
    parser.add_argument("--refinements", type=int, default=3, help="Max number of refinement iterations.")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🤖 Gemini-Claude GAN Agent System (Modern Harness Edition)")
    print("="*80)
    print(f"🔹 Task: {args.task}")
    print(f"🔹 Max Refinements: {args.refinements}")
    print("="*80)
    
    try:
        orchestrator = GANOrchestrator(max_refinements=args.refinements)
        result = orchestrator.run_sprint(args.task)
        
        print("\n" + "="*80)
        print("🎉 Final Result Status:", result.get("status"))
        print("="*80)
        
        if result.get("status") == "SUCCESS":
            print("\n✅ Implementation complete! Grade A received.")
            print("\n### Final Submission Snippet:")
            print(result.get("final_submission", "")[:500] + "...")
        else:
            print("\n⚠️ Partial success or failure. Check logs for details.")
            
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
