"""
Evaluator for calculating accuracy and consistency metrics.
計算一致性和準確性指標
"""
import re
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class ConsistencyEvaluator:
    """計算一致性和準確性指標"""

    def __init__(self, tolerance: float = 0.01):
        """
        Initialize evaluator.

        Args:
            tolerance: Tolerance for numerical comparison (for floating point)
        """
        self.tolerance = tolerance

    def extract_number(self, text: str) -> Optional[float]:
        """
        從回應文字中提取數值

        Args:
            text: Response text

        Returns:
            Extracted number or None if not found
        """
        if not text:
            return None

        # Try to find numbers in the text
        # Pattern matches: integers, decimals, numbers with commas
        patterns = [
            r'(?:答案是|結果是|等於|是)\s*([+-]?\d+\.?\d*)',  # "答案是 123"
            r'([+-]?\d+\.?\d*)\s*(?:元|個|本|顆|公尺|公分|公斤)',  # "123 元"
            r'(?:^|\s)([+-]?\d+\.?\d*)(?:\s|$)',  # Standalone number
            r'([+-]?\d{1,3}(?:,\d{3})+\.?\d*)',  # Number with commas
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Take the first match
                num_str = matches[0].replace(',', '')
                try:
                    return float(num_str)
                except ValueError:
                    continue

        return None

    def is_correct(self, extracted: Optional[float], ground_truth: float) -> bool:
        """
        Check if extracted answer is correct.

        Args:
            extracted: Extracted numerical answer
            ground_truth: Correct answer

        Returns:
            True if correct (within tolerance)
        """
        if extracted is None:
            return False

        # Check if within tolerance
        return abs(extracted - ground_truth) <= self.tolerance

    def calculate_accuracy(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        計算準確率

        Args:
            responses: List of response dictionaries

        Returns:
            Dictionary with accuracy metrics
        """
        total = len(responses)
        correct = 0
        no_answer = 0
        errors = []

        for resp in responses:
            ground_truth = resp["ground_truth"]
            extracted = self.extract_number(resp["answer"])

            if extracted is None:
                no_answer += 1
                errors.append({
                    "question_id": resp["question_id"],
                    "version": resp["version_type"],
                    "ground_truth": ground_truth,
                    "extracted": None,
                    "response": resp["answer"],
                    "error_type": "no_answer_found"
                })
            elif self.is_correct(extracted, ground_truth):
                correct += 1
            else:
                errors.append({
                    "question_id": resp["question_id"],
                    "version": resp["version_type"],
                    "ground_truth": ground_truth,
                    "extracted": extracted,
                    "response": resp["answer"],
                    "error_type": "incorrect_answer"
                })

        accuracy = correct / total if total > 0 else 0.0

        return {
            "total_responses": total,
            "correct": correct,
            "incorrect": total - correct - no_answer,
            "no_answer": no_answer,
            "accuracy": accuracy,
            "errors": errors
        }

    def calculate_consistency(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        計算一致性分數

        Args:
            responses: List of response dictionaries

        Returns:
            Dictionary with consistency metrics
        """
        # Group responses by question_id
        by_question = defaultdict(lambda: defaultdict(list))

        for resp in responses:
            qid = resp["question_id"]
            version = resp["version_type"]
            extracted = self.extract_number(resp["answer"])
            by_question[qid][version].append(extracted)

        consistency_scores = []

        for qid, versions in by_question.items():
            # Calculate cross-paraphrase consistency
            # Get the most common answer for each version
            version_answers = {}
            for version_type in ["direct", "contextualized", "variation"]:
                answers = versions.get(version_type, [])
                if answers:
                    # Find most common answer (mode)
                    most_common = max(set(answers), key=answers.count) if answers else None
                    version_answers[version_type] = most_common

            # Count how many versions agree
            if len(version_answers) == 3:
                unique_answers = set(version_answers.values())
                if None in unique_answers:
                    unique_answers.remove(None)

                if len(unique_answers) == 1:
                    paraphrase_consistency = 1.0
                elif len(unique_answers) == 2:
                    paraphrase_consistency = 0.67
                else:
                    paraphrase_consistency = 0.33
            else:
                paraphrase_consistency = 0.0

            # Calculate test-retest consistency (for each version)
            retest_consistencies = []
            for version_type, answers in versions.items():
                if len(answers) > 1:
                    # Count most common answer frequency
                    most_common = max(set(answers), key=answers.count) if answers else None
                    consistency = answers.count(most_common) / len(answers)
                    retest_consistencies.append(consistency)

            avg_retest_consistency = sum(retest_consistencies) / len(retest_consistencies) if retest_consistencies else 0.0

            # Overall consistency score
            ocs = (paraphrase_consistency + avg_retest_consistency) / 2

            consistency_scores.append({
                "question_id": qid,
                "paraphrase_consistency": paraphrase_consistency,
                "retest_consistency": avg_retest_consistency,
                "overall_consistency_score": ocs,
                "version_answers": version_answers
            })

        # Calculate average consistency
        avg_paraphrase = sum(s["paraphrase_consistency"] for s in consistency_scores) / len(consistency_scores)
        avg_retest = sum(s["retest_consistency"] for s in consistency_scores) / len(consistency_scores)
        avg_ocs = sum(s["overall_consistency_score"] for s in consistency_scores) / len(consistency_scores)

        return {
            "per_question": consistency_scores,
            "average_paraphrase_consistency": avg_paraphrase,
            "average_retest_consistency": avg_retest,
            "average_overall_consistency_score": avg_ocs
        }

    def analyze_errors(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        錯誤分析

        Args:
            responses: List of response dictionaries

        Returns:
            Dictionary with error analysis
        """
        error_types = defaultdict(int)
        by_category = defaultdict(lambda: {"correct": 0, "incorrect": 0, "no_answer": 0})
        by_operation = defaultdict(lambda: {"correct": 0, "incorrect": 0, "no_answer": 0})

        for resp in responses:
            ground_truth = resp["ground_truth"]
            extracted = self.extract_number(resp["answer"])
            category = resp.get("category", "unknown")
            operation = resp.get("operation", "unknown")

            if extracted is None:
                error_types["no_answer"] += 1
                by_category[category]["no_answer"] += 1
                by_operation[operation]["no_answer"] += 1
            elif self.is_correct(extracted, ground_truth):
                by_category[category]["correct"] += 1
                by_operation[operation]["correct"] += 1
            else:
                error_types["incorrect_calculation"] += 1
                by_category[category]["incorrect"] += 1
                by_operation[operation]["incorrect"] += 1

        return {
            "error_types": dict(error_types),
            "by_category": dict(by_category),
            "by_operation": dict(by_operation)
        }

    def generate_report(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report.

        Args:
            responses: List of response dictionaries

        Returns:
            Complete evaluation report
        """
        accuracy_results = self.calculate_accuracy(responses)
        consistency_results = self.calculate_consistency(responses)
        error_analysis = self.analyze_errors(responses)

        return {
            "accuracy": accuracy_results,
            "consistency": consistency_results,
            "error_analysis": error_analysis,
            "total_responses": len(responses)
        }

    def save_results(self, report: Dict[str, Any], output_dir: str = "../results"):
        """Save evaluation results to files"""
        # Save accuracy results
        accuracy_df = pd.DataFrame([{
            "total": report["accuracy"]["total_responses"],
            "correct": report["accuracy"]["correct"],
            "incorrect": report["accuracy"]["incorrect"],
            "no_answer": report["accuracy"]["no_answer"],
            "accuracy": report["accuracy"]["accuracy"]
        }])
        accuracy_df.to_csv(f"{output_dir}/accuracy_results.csv", index=False)

        # Save consistency results
        consistency_df = pd.DataFrame(report["consistency"]["per_question"])
        consistency_df.to_csv(f"{output_dir}/consistency_results.csv", index=False)

        # Save error analysis
        error_df = pd.DataFrame(report["accuracy"]["errors"])
        if not error_df.empty:
            error_df.to_csv(f"{output_dir}/error_analysis.csv", index=False)

        print(f"結果已儲存至 {output_dir}/")


def main():
    """Test evaluator with sample data"""
    # Sample test data
    sample_responses = [
        {
            "question_id": "test_001",
            "version_type": "direct",
            "answer": "答案是 801",
            "ground_truth": 801,
            "category": "arithmetic",
            "operation": "addition"
        },
        {
            "question_id": "test_001",
            "version_type": "contextualized",
            "answer": "小明現在有 801 元",
            "ground_truth": 801,
            "category": "arithmetic",
            "operation": "addition"
        },
        {
            "question_id": "test_001",
            "version_type": "variation",
            "answer": "等於 801",
            "ground_truth": 801,
            "category": "arithmetic",
            "operation": "addition"
        }
    ]

    evaluator = ConsistencyEvaluator()

    # Test number extraction
    print("測試數值提取:")
    for resp in sample_responses:
        num = evaluator.extract_number(resp["answer"])
        print(f"  '{resp['answer']}' -> {num}")

    # Test accuracy calculation
    print("\n測試準確率計算:")
    acc_results = evaluator.calculate_accuracy(sample_responses)
    print(f"  準確率: {acc_results['accuracy']:.2%}")
    print(f"  正確: {acc_results['correct']}/{acc_results['total_responses']}")


if __name__ == "__main__":
    main()
