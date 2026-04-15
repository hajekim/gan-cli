import json
import time
from src.orchestration.gan_loop import GANOrchestrator

def run_benchmark(task: str, max_refinements: int = 3):
    """
    Runs a benchmark for the GAN loop and prints the performance metrics.
    """
    orchestrator = GANOrchestrator(max_refinements=max_refinements)
    
    start_time = time.time()
    result = orchestrator.run_sprint(task)
    end_time = time.time()
    
    print("\n" + "="*50)
    print("📊 GAN LOOP BENCHMARK REPORT")
    print("="*50)
    print(f"🔹 Task: {task}")
    print(f"🔹 Status: {result.get('status')}")
    print(f"🔹 Iterations: {result.get('iteration')}")
    print(f"🔹 Total Time: {end_time - start_time:.2f} seconds")
    
    if result.get("status") in ["SUCCESS", "PARTIAL_SUCCESS"]:
        eval_data = result.get("evaluation", {})
        print(f"🔹 Final Grade: {eval_data.get('grade')}")
        print(f"🔹 Pass/Fail: {eval_data.get('pass_fail')}")
        print(f"🔹 Feedback Summary: {eval_data.get('feedback', '')[:200]}...")
        
        # Save results to a file for analysis
        report_path = f"artifacts/benchmark_report_{int(time.time())}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Detailed report saved to: {report_path}")
    
    print("="*50)

if __name__ == "__main__":
    # Sample task for benchmark
    sample_task = "Python으로 사용자 입력을 받아 가계부를 관리하는 CLI 프로그램을 만드세요. 데이터는 JSON 파일로 저장되어야 하며, 지출 합계 계산 기능이 포함되어야 합니다."
    
    # In a real environment, you would run this:
    # run_benchmark(sample_task)
    print("🚀 Benchmark tool ready. Run with a specific task to see the GAN loop in action.")
