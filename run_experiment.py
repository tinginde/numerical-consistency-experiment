#!/usr/bin/env python3
"""
Main script to run the numerical consistency experiment.
主執行腳本
"""
import sys
import os
import json
import argparse
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generate_questions import QuestionGenerator
from api_caller import LLMTester
from evaluator import ConsistencyEvaluator
import config


def generate_questions(num_questions: int = 10):
    """Generate test questions"""
    print("=" * 60)
    print("步驟 1: 生成測試問題")
    print("=" * 60)

    generator = QuestionGenerator()
    questions = generator.generate_arithmetic_questions(n=num_questions)

    print(f"✓ 生成了 {len(questions)} 個算術問題")

    # Save questions
    generator.save_questions(questions, str(config.QUESTIONS_FILE))
    print(f"✓ 問題已儲存至: {config.QUESTIONS_FILE}")

    # Save ground truth
    ground_truth = {q["id"]: q["ground_truth"] for q in questions}
    with open(config.GROUND_TRUTH_FILE, 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, ensure_ascii=False, indent=2)
    print(f"✓ 正確答案已儲存至: {config.GROUND_TRUTH_FILE}")

    # Display sample question
    print("\n範例問題:")
    sample = questions[0]
    print(f"  ID: {sample['id']}")
    print(f"  類別: {sample['category']} - {sample['operation']}")
    print(f"  正確答案: {sample['ground_truth']}")
    print(f"  版本:")
    for version_type, text in sample['versions'].items():
        print(f"    - {version_type}: {text}")

    return questions


def run_queries(questions, model_name: str, num_repetitions: int = 3):
    """Query LLM API with all question variants"""
    print("\n" + "=" * 60)
    print("步驟 2: 查詢 LLM API")
    print("=" * 60)

    # Detect provider
    if any(x in model_name.lower() for x in ['gpt', 'davinci', 'turbo']):
        provider = 'openai'
        api_key_env = 'OPENAI_API_KEY'
        api_key = os.getenv('OPENAI_API_KEY')
    else:
        provider = 'anthropic'
        api_key_env = 'ANTHROPIC_API_KEY'
        api_key = os.getenv('ANTHROPIC_API_KEY')

    # Check API key
    if not api_key:
        print(f"❌ 錯誤: 未設置 {api_key_env} 環境變數")
        print(f"請執行: export {api_key_env}='your-api-key'")
        sys.exit(1)

    tester = LLMTester(model_name=model_name, api_key=api_key)

    # Batch query
    responses = tester.batch_query(
        questions=questions,
        repeat=num_repetitions,
        temperature=config.TEMPERATURE,
        save_interval=5
    )

    # Save final responses
    tester.save_all_responses(responses)

    print(f"\n✓ 完成 {len(responses)} 次查詢")

    return responses


def evaluate_responses(responses):
    """Evaluate responses for accuracy and consistency"""
    print("\n" + "=" * 60)
    print("步驟 3: 評估結果")
    print("=" * 60)

    evaluator = ConsistencyEvaluator(tolerance=0.01)

    # Generate comprehensive report
    report = evaluator.generate_report(responses)

    # Display summary
    print("\n準確性結果:")
    print(f"  總查詢數: {report['accuracy']['total_responses']}")
    print(f"  正確: {report['accuracy']['correct']}")
    print(f"  錯誤: {report['accuracy']['incorrect']}")
    print(f"  無法提取答案: {report['accuracy']['no_answer']}")
    print(f"  準確率: {report['accuracy']['accuracy']:.2%}")

    print("\n一致性結果:")
    print(f"  平均跨措辭一致性: {report['consistency']['average_paraphrase_consistency']:.2%}")
    print(f"  平均重複測試一致性: {report['consistency']['average_retest_consistency']:.2%}")
    print(f"  平均整體一致性分數 (OCS): {report['consistency']['average_overall_consistency_score']:.2%}")

    print("\n錯誤分析:")
    for category, stats in report['error_analysis']['by_category'].items():
        total = stats['correct'] + stats['incorrect'] + stats['no_answer']
        accuracy = stats['correct'] / total if total > 0 else 0
        print(f"  {category}: {accuracy:.2%} 準確率 ({stats['correct']}/{total})")

    # Save results
    evaluator.save_results(report, output_dir=str(config.RESULTS_DIR))
    print(f"\n✓ 詳細結果已儲存至: {config.RESULTS_DIR}/")

    return report


def visualize_results(report):
    """Create visualizations of results"""
    print("\n" + "=" * 60)
    print("步驟 4: 生成視覺化")
    print("=" * 60)

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd

        sns.set_style("whitegrid")

        # 1. Accuracy by category
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Accuracy bar chart
        by_cat = report['error_analysis']['by_category']
        categories = list(by_cat.keys())
        accuracies = []
        for cat in categories:
            stats = by_cat[cat]
            total = stats['correct'] + stats['incorrect'] + stats['no_answer']
            acc = stats['correct'] / total if total > 0 else 0
            accuracies.append(acc * 100)

        axes[0].bar(categories, accuracies, color='steelblue')
        axes[0].set_ylabel('準確率 (%)', fontsize=12)
        axes[0].set_title('各類別準確率', fontsize=14, fontweight='bold')
        axes[0].set_ylim(0, 100)
        axes[0].grid(axis='y', alpha=0.3)

        # Consistency metrics
        consistency_data = {
            '跨措辭一致性': report['consistency']['average_paraphrase_consistency'] * 100,
            '重複測試一致性': report['consistency']['average_retest_consistency'] * 100,
            '整體一致性分數': report['consistency']['average_overall_consistency_score'] * 100
        }

        axes[1].bar(consistency_data.keys(), consistency_data.values(), color='coral')
        axes[1].set_ylabel('一致性分數 (%)', fontsize=12)
        axes[1].set_title('一致性指標', fontsize=14, fontweight='bold')
        axes[1].set_ylim(0, 100)
        axes[1].tick_params(axis='x', rotation=15)
        axes[1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_path = config.VIZ_DIR / "experiment_results.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 視覺化已儲存至: {output_path}")

        plt.close()

    except ImportError as e:
        print(f"⚠ 無法生成視覺化: {e}")
        print("  請安裝: pip install matplotlib seaborn")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Run numerical consistency experiment')
    parser.add_argument('--num-questions', type=int, default=10,
                        help='Number of questions to generate (default: 10)')
    parser.add_argument('--num-repetitions', type=int, default=3,
                        help='Number of repetitions per question variant (default: 3)')
    parser.add_argument('--model', type=str, default=config.MODEL_NAME,
                        help='Model to use (default: claude-sonnet-4-5-20250929). Examples: gpt-4o, gpt-3.5-turbo')
    parser.add_argument('--skip-generation', action='store_true',
                        help='Skip question generation (use existing questions)')
    parser.add_argument('--skip-queries', action='store_true',
                        help='Skip API queries (use existing responses)')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print(" 數值推理一致性實驗")
    print(" Numerical Reasoning Consistency Experiment")
    print("=" * 60)
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模型: {args.model}")
    print(f"問題數: {args.num_questions}")
    print(f"重複次數: {args.num_repetitions}")
    print(f"總查詢次數: {args.num_questions} × 3 版本 × {args.num_repetitions} = {args.num_questions * 3 * args.num_repetitions}")
    print("=" * 60)

    # Step 1: Generate questions
    if not args.skip_generation:
        questions = generate_questions(num_questions=args.num_questions)
    else:
        print("使用現有問題...")
        generator = QuestionGenerator()
        questions = generator.load_questions(str(config.QUESTIONS_FILE))

    # Step 2: Query API
    if not args.skip_queries:
        responses = run_queries(questions, model_name=args.model, num_repetitions=args.num_repetitions)
    else:
        print("使用現有回應...")
        # Try to load from model-specific file first
        provider = 'openai' if any(x in args.model.lower() for x in ['gpt', 'turbo']) else 'anthropic'
        response_file = config.RESPONSES_DIR / f"{provider}_responses.json"
        if response_file.exists():
            with open(response_file, 'r', encoding='utf-8') as f:
                responses = json.load(f)
        else:
            with open(config.CLAUDE_RESPONSES_FILE, 'r', encoding='utf-8') as f:
                responses = json.load(f)

    # Step 3: Evaluate
    report = evaluate_responses(responses)

    # Step 4: Visualize
    visualize_results(report)

    print("\n" + "=" * 60)
    print("✓ 實驗完成!")
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Save final report
    report_path = config.RESULTS_DIR / "experiment_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n完整報告: {report_path}")


if __name__ == "__main__":
    main()
