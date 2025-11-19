#!/usr/bin/env python3
"""
Demo script to test the experiment pipeline with mock data.
使用模擬數據測試實驗流程
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generate_questions import QuestionGenerator
from evaluator import ConsistencyEvaluator
import config


def create_mock_responses(questions, num_repetitions=3):
    """
    Create mock responses for testing (simulating perfect/near-perfect LLM)
    創建模擬回應用於測試
    """
    print("生成模擬回應（模擬 LLM 行為）...")

    responses = []
    import random

    for question in questions:
        qid = question["id"]
        ground_truth = question["ground_truth"]

        for version_type in ["direct", "contextualized", "variation"]:
            for rep in range(num_repetitions):
                # Simulate high accuracy with occasional errors
                is_correct = random.random() > 0.1  # 90% accuracy

                if is_correct:
                    answer_num = ground_truth
                else:
                    # Generate a wrong answer
                    answer_num = ground_truth + random.randint(-10, 10)

                # Format answer in different ways
                answer_formats = [
                    f"答案是 {answer_num}",
                    f"{answer_num}",
                    f"計算結果為 {answer_num}",
                    f"等於 {answer_num}"
                ]

                response = {
                    "question_id": qid,
                    "version_type": version_type,
                    "repetition": rep + 1,
                    "question": question["versions"][version_type],
                    "answer": random.choice(answer_formats),
                    "ground_truth": ground_truth,
                    "category": question["category"],
                    "operation": question.get("operation", ""),
                    "model": "mock-claude",
                    "temperature": 0.0,
                    "response_time": random.uniform(0.5, 2.0),
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "error": None
                }

                responses.append(response)

    print(f"✓ 生成了 {len(responses)} 個模擬回應")
    return responses


def main():
    """Main execution with mock data"""
    print("\n" + "=" * 60)
    print(" 數值推理一致性實驗 - 演示版本")
    print(" Numerical Reasoning Consistency Experiment - Demo")
    print("=" * 60)
    print("使用模擬數據進行測試")
    print("=" * 60)

    # Step 1: Load existing questions
    print("\n步驟 1: 載入測試問題")
    generator = QuestionGenerator()
    questions = generator.load_questions(str(config.QUESTIONS_FILE))
    print(f"✓ 載入了 {len(questions)} 個問題")

    # Step 2: Create mock responses
    print("\n步驟 2: 生成模擬回應")
    responses = create_mock_responses(questions, num_repetitions=3)

    # Save mock responses
    with open(config.CLAUDE_RESPONSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
    print(f"✓ 模擬回應已儲存至: {config.CLAUDE_RESPONSES_FILE}")

    # Step 3: Evaluate
    print("\n步驟 3: 評估結果")
    evaluator = ConsistencyEvaluator(tolerance=0.01)
    report = evaluator.generate_report(responses)

    # Display results
    print("\n" + "=" * 60)
    print(" 評估結果")
    print("=" * 60)

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

    print("\n各類別準確率:")
    for category, stats in report['error_analysis']['by_category'].items():
        total = stats['correct'] + stats['incorrect'] + stats['no_answer']
        accuracy = stats['correct'] / total if total > 0 else 0
        print(f"  {category}: {accuracy:.2%} ({stats['correct']}/{total})")

    print("\n各運算類型準確率:")
    for operation, stats in report['error_analysis']['by_operation'].items():
        total = stats['correct'] + stats['incorrect'] + stats['no_answer']
        accuracy = stats['correct'] / total if total > 0 else 0
        print(f"  {operation}: {accuracy:.2%} ({stats['correct']}/{total})")

    # Save results
    evaluator.save_results(report, output_dir=str(config.RESULTS_DIR))
    print(f"\n✓ 詳細結果已儲存至: {config.RESULTS_DIR}/")

    # Step 4: Visualize
    print("\n步驟 4: 生成視覺化")
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import seaborn as sns

        sns.set_style("whitegrid")
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Accuracy by category
        by_cat = report['error_analysis']['by_category']
        categories = list(by_cat.keys())
        accuracies = []
        for cat in categories:
            stats = by_cat[cat]
            total = stats['correct'] + stats['incorrect'] + stats['no_answer']
            acc = stats['correct'] / total if total > 0 else 0
            accuracies.append(acc * 100)

        axes[0, 0].bar(categories, accuracies, color='steelblue')
        axes[0, 0].set_ylabel('Accuracy (%)', fontsize=12)
        axes[0, 0].set_title('Accuracy by Category', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylim(0, 100)
        axes[0, 0].grid(axis='y', alpha=0.3)

        # 2. Accuracy by operation
        by_op = report['error_analysis']['by_operation']
        operations = list(by_op.keys())
        op_accuracies = []
        for op in operations:
            stats = by_op[op]
            total = stats['correct'] + stats['incorrect'] + stats['no_answer']
            acc = stats['correct'] / total if total > 0 else 0
            op_accuracies.append(acc * 100)

        axes[0, 1].bar(operations, op_accuracies, color='coral')
        axes[0, 1].set_ylabel('Accuracy (%)', fontsize=12)
        axes[0, 1].set_title('Accuracy by Operation', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylim(0, 100)
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(axis='y', alpha=0.3)

        # 3. Consistency metrics
        consistency_data = {
            'Cross-paraphrase': report['consistency']['average_paraphrase_consistency'] * 100,
            'Test-retest': report['consistency']['average_retest_consistency'] * 100,
            'Overall (OCS)': report['consistency']['average_overall_consistency_score'] * 100
        }

        axes[1, 0].bar(consistency_data.keys(), consistency_data.values(),
                       color=['#2ecc71', '#3498db', '#9b59b6'])
        axes[1, 0].set_ylabel('Consistency Score (%)', fontsize=12)
        axes[1, 0].set_title('Consistency Metrics', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylim(0, 100)
        axes[1, 0].tick_params(axis='x', rotation=15)
        axes[1, 0].grid(axis='y', alpha=0.3)

        # 4. Error distribution pie chart
        error_data = {
            'Correct': report['accuracy']['correct'],
            'Incorrect': report['accuracy']['incorrect'],
            'No Answer': report['accuracy']['no_answer']
        }

        colors = ['#2ecc71', '#e74c3c', '#95a5a6']
        axes[1, 1].pie(error_data.values(), labels=error_data.keys(),
                       autopct='%1.1f%%', colors=colors, startangle=90)
        axes[1, 1].set_title('Response Distribution', fontsize=14, fontweight='bold')

        plt.tight_layout()
        output_path = config.VIZ_DIR / "demo_results.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 視覺化已儲存至: {output_path}")

        plt.close()

    except Exception as e:
        print(f"⚠ 視覺化生成失敗: {e}")

    # Save final report
    report_path = config.RESULTS_DIR / "demo_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("✓ 演示完成!")
    print("=" * 60)
    print(f"\n完整報告: {report_path}")
    print("\n注意: 這是使用模擬數據的演示版本")
    print("若要執行真實實驗，請設置 ANTHROPIC_API_KEY 並運行 run_experiment.py")


if __name__ == "__main__":
    main()
