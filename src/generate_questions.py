"""
Question generator for numerical consistency experiment.
生成數值推理測試問題
"""
import random
import json
from typing import Dict, List, Any


class QuestionGenerator:
    """生成數值推理測試問題"""

    def __init__(self, seed: int = 42):
        """
        Initialize question generator.

        Args:
            seed: Random seed for reproducibility
        """
        random.seed(seed)

    def generate_arithmetic_questions(self, n: int = 25) -> List[Dict[str, Any]]:
        """
        生成基本算術問題

        Args:
            n: Number of questions to generate (分配到各種運算)

        Returns:
            List of question dictionaries
        """
        questions = []
        operations_per_type = n // 4

        # 加法問題
        questions.extend(self._generate_addition_questions(operations_per_type))

        # 減法問題
        questions.extend(self._generate_subtraction_questions(operations_per_type))

        # 乘法問題
        questions.extend(self._generate_multiplication_questions(operations_per_type))

        # 除法問題
        questions.extend(self._generate_division_questions(n - 3 * operations_per_type))

        return questions

    def _generate_addition_questions(self, n: int) -> List[Dict[str, Any]]:
        """生成加法問題"""
        questions = []

        for i in range(n):
            # 變化數字大小：兩位數、三位數、小數
            if i % 3 == 0:
                a, b = random.randint(10, 99), random.randint(10, 99)
            elif i % 3 == 1:
                a, b = random.randint(100, 999), random.randint(100, 999)
            else:
                a = round(random.uniform(10, 100), 1)
                b = round(random.uniform(10, 100), 1)

            ground_truth = a + b
            if isinstance(a, float) or isinstance(b, float):
                ground_truth = round(ground_truth, 1)

            question = {
                "id": f"arith_add_{i+1:03d}",
                "category": "arithmetic",
                "operation": "addition",
                "operands": [a, b],
                "ground_truth": ground_truth,
                "versions": self._create_addition_paraphrases(a, b)
            }
            questions.append(question)

        return questions

    def _generate_subtraction_questions(self, n: int) -> List[Dict[str, Any]]:
        """生成減法問題"""
        questions = []

        for i in range(n):
            if i % 3 == 0:
                a, b = random.randint(50, 99), random.randint(10, 49)
            elif i % 3 == 1:
                a, b = random.randint(500, 999), random.randint(100, 499)
            else:
                a = round(random.uniform(50, 200), 1)
                b = round(random.uniform(10, 50), 1)

            ground_truth = a - b
            if isinstance(a, float) or isinstance(b, float):
                ground_truth = round(ground_truth, 1)

            question = {
                "id": f"arith_sub_{i+1:03d}",
                "category": "arithmetic",
                "operation": "subtraction",
                "operands": [a, b],
                "ground_truth": ground_truth,
                "versions": self._create_subtraction_paraphrases(a, b)
            }
            questions.append(question)

        return questions

    def _generate_multiplication_questions(self, n: int) -> List[Dict[str, Any]]:
        """生成乘法問題"""
        questions = []

        for i in range(n):
            if i % 3 == 0:
                # 兩位數 × 兩位數
                a, b = random.randint(11, 99), random.randint(11, 99)
            elif i % 3 == 1:
                # 三位數 × 一位數
                a, b = random.randint(100, 999), random.randint(2, 9)
            else:
                # 小數乘法
                a = round(random.uniform(5, 50), 1)
                b = random.randint(2, 20)

            ground_truth = a * b
            if isinstance(a, float) or isinstance(b, float):
                ground_truth = round(ground_truth, 1)

            question = {
                "id": f"arith_mul_{i+1:03d}",
                "category": "arithmetic",
                "operation": "multiplication",
                "operands": [a, b],
                "ground_truth": ground_truth,
                "versions": self._create_multiplication_paraphrases(a, b)
            }
            questions.append(question)

        return questions

    def _generate_division_questions(self, n: int) -> List[Dict[str, Any]]:
        """生成除法問題"""
        questions = []

        for i in range(n):
            if i % 3 == 0:
                # 整除
                b = random.randint(5, 20)
                quotient = random.randint(10, 50)
                a = b * quotient
                ground_truth = quotient
            elif i % 3 == 1:
                # 有餘數
                b = random.randint(5, 20)
                quotient = random.randint(10, 50)
                remainder = random.randint(1, b-1)
                a = b * quotient + remainder
                ground_truth = quotient  # 商數
            else:
                # 小數結果
                a = random.randint(100, 500)
                b = random.randint(3, 15)
                ground_truth = round(a / b, 2)

            question = {
                "id": f"arith_div_{i+1:03d}",
                "category": "arithmetic",
                "operation": "division",
                "operands": [a, b],
                "ground_truth": ground_truth,
                "versions": self._create_division_paraphrases(a, b)
            }
            questions.append(question)

        return questions

    def _create_addition_paraphrases(self, a, b) -> Dict[str, str]:
        """為加法問題生成三種措辭版本"""
        return {
            "direct": f"計算 {a} + {b}",
            "contextualized": f"小明有 {a} 元，媽媽又給他 {b} 元，他現在有多少錢？",
            "variation": f"{a} 加上 {b} 等於多少？"
        }

    def _create_subtraction_paraphrases(self, a, b) -> Dict[str, str]:
        """為減法問題生成三種措辭版本"""
        return {
            "direct": f"計算 {a} - {b}",
            "contextualized": f"書店有 {a} 本書，賣出了 {b} 本，還剩下幾本？",
            "variation": f"{a} 減去 {b} 是多少？"
        }

    def _create_multiplication_paraphrases(self, a, b) -> Dict[str, str]:
        """為乘法問題生成三種措辭版本"""
        return {
            "direct": f"計算 {a} × {b}",
            "contextualized": f"一盒蛋糕有 {b} 個，買了 {a} 盒，總共有幾個蛋糕？",
            "variation": f"{a} 和 {b} 相乘的結果是什麼？"
        }

    def _create_division_paraphrases(self, a, b) -> Dict[str, str]:
        """為除法問題生成三種措辭版本"""
        return {
            "direct": f"計算 {a} ÷ {b}",
            "contextualized": f"有 {a} 顆糖果要平分給 {b} 個小朋友，每個人可以分到幾顆？",
            "variation": f"{a} 除以 {b} 等於多少？"
        }

    def generate_percentage_questions(self, n: int = 25) -> List[Dict[str, Any]]:
        """生成百分比問題（基礎版本）"""
        questions = []

        for i in range(n):
            base = random.randint(100, 1000)
            percentage = random.choice([10, 15, 20, 25, 30, 50])
            ground_truth = round(base * percentage / 100, 2)

            question = {
                "id": f"percent_{i+1:03d}",
                "category": "percentage",
                "operation": "percentage_calculation",
                "operands": [base, percentage],
                "ground_truth": ground_truth,
                "versions": {
                    "direct": f"{base} 的 {percentage}% 是多少？",
                    "contextualized": f"一件原價 {base} 元的衣服打 {100-percentage} 折，折扣金額是多少？",
                    "variation": f"如果要從 {base} 中計算 {percentage}%，結果是多少？"
                }
            }
            questions.append(question)

        return questions

    def save_questions(self, questions: List[Dict[str, Any]], filepath: str):
        """Save questions to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    def load_questions(self, filepath: str) -> List[Dict[str, Any]]:
        """Load questions from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)


def main():
    """Generate and save test questions"""
    generator = QuestionGenerator()

    # Generate 10 questions for initial testing (arithmetic only)
    print("生成測試問題...")
    questions = generator.generate_arithmetic_questions(n=10)

    print(f"生成了 {len(questions)} 個問題")

    # Display first question as example
    print("\n範例問題:")
    print(json.dumps(questions[0], ensure_ascii=False, indent=2))

    # Save questions
    output_file = "../data/questions.json"
    generator.save_questions(questions, output_file)
    print(f"\n問題已儲存至: {output_file}")

    # Also save ground truth separately
    ground_truth = {q["id"]: q["ground_truth"] for q in questions}
    with open("../data/ground_truth.json", 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, ensure_ascii=False, indent=2)
    print(f"正確答案已儲存至: ../data/ground_truth.json")


if __name__ == "__main__":
    main()
