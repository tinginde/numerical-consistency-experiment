"""
API caller for querying LLMs.
統一的 LLM API 呼叫介面 - 支援 Claude 和 OpenAI
"""
import os
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class LLMTester:
    """統一的 LLM API 呼叫介面 - 支援多個提供商"""

    def __init__(self, model_name: str = "claude-sonnet-4-5-20250929", api_key: Optional[str] = None, provider: Optional[str] = None):
        """
        Initialize LLM tester.

        Args:
            model_name: Name of the model to use
            api_key: API key (if None, will use environment variable)
            provider: 'anthropic' or 'openai' (if None, auto-detect from model_name)
        """
        self.model_name = model_name

        # Auto-detect provider if not specified
        if provider is None:
            if any(x in model_name.lower() for x in ['gpt', 'davinci', 'turbo']):
                self.provider = 'openai'
            elif any(x in model_name.lower() for x in ['claude', 'sonnet', 'opus', 'haiku']):
                self.provider = 'anthropic'
            else:
                raise ValueError(f"Cannot auto-detect provider from model name: {model_name}. Please specify provider explicitly.")
        else:
            self.provider = provider.lower()

        # Initialize appropriate client
        if self.provider == 'anthropic':
            import anthropic
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("API key not found. Set ANTHROPIC_API_KEY environment variable.")
            self.client = anthropic.Anthropic(api_key=self.api_key)

        elif self.provider == 'openai':
            import openai
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("API key not found. Set OPENAI_API_KEY environment variable.")
            self.client = openai.OpenAI(api_key=self.api_key)

        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Use 'anthropic' or 'openai'.")

        self.responses = []

    def query(self, question: str, temperature: float = 0.0, max_retries: int = 3) -> Dict[str, Any]:
        """
        發送問題並取得回應

        Args:
            question: Question to ask
            temperature: Sampling temperature (0.0 for deterministic)
            max_retries: Maximum number of retries on failure

        Returns:
            Dictionary containing response and metadata
        """
        for attempt in range(max_retries):
            try:
                start_time = time.time()

                if self.provider == 'anthropic':
                    response_data = self._query_anthropic(question, temperature)
                elif self.provider == 'openai':
                    response_data = self._query_openai(question, temperature)
                else:
                    raise ValueError(f"Unsupported provider: {self.provider}")

                end_time = time.time()
                response_data["response_time"] = end_time - start_time
                response_data["timestamp"] = datetime.now().isoformat()
                response_data["success"] = True
                response_data["error"] = None

                return response_data

            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    return {
                        "question": question,
                        "answer": None,
                        "model": self.model_name,
                        "provider": self.provider,
                        "temperature": temperature,
                        "response_time": None,
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "error": str(e)
                    }
                else:
                    # Wait before retrying
                    time.sleep(2 ** attempt)

    def _query_anthropic(self, question: str, temperature: float) -> Dict[str, Any]:
        """Query Anthropic Claude API"""
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": f"{question}\n\n請直接給出數值答案。"
                }
            ]
        )

        return {
            "question": question,
            "answer": message.content[0].text,
            "model": self.model_name,
            "provider": "anthropic",
            "temperature": temperature
        }

    def _query_openai(self, question: str, temperature: float) -> Dict[str, Any]:
        """Query OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "你是一個數學助手。請直接給出數值答案，不需要過多解釋。"
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=temperature,
            max_tokens=500
        )

        return {
            "question": question,
            "answer": response.choices[0].message.content,
            "model": self.model_name,
            "provider": "openai",
            "temperature": temperature
        }

    def batch_query(
        self,
        questions: List[Dict[str, Any]],
        repeat: int = 3,
        temperature: float = 0.0,
        save_interval: int = 10
    ) -> List[Dict[str, Any]]:
        """
        批次處理多個問題

        Args:
            questions: List of question dictionaries
            repeat: Number of times to repeat each question variant
            temperature: Sampling temperature
            save_interval: Save responses every N queries

        Returns:
            List of all responses
        """
        all_responses = []
        total_queries = len(questions) * 3 * repeat  # 3 paraphrases × repeat times

        print(f"開始批次查詢 ({self.provider.upper()} - {self.model_name}): {len(questions)} 個問題 × 3 個版本 × {repeat} 次重複 = {total_queries} 次查詢")

        query_count = 0

        for q_idx, question in enumerate(questions):
            question_id = question["id"]
            versions = question["versions"]

            for version_type in ["direct", "contextualized", "variation"]:
                version_text = versions[version_type]

                for rep in range(repeat):
                    query_count += 1
                    print(f"查詢 {query_count}/{total_queries}: {question_id} - {version_type} - 第{rep+1}次", end="... ")

                    response = self.query(version_text, temperature=temperature)

                    response["question_id"] = question_id
                    response["version_type"] = version_type
                    response["repetition"] = rep + 1
                    response["ground_truth"] = question["ground_truth"]
                    response["category"] = question["category"]
                    response["operation"] = question.get("operation", "")

                    all_responses.append(response)

                    if response["success"]:
                        print("✓")
                    else:
                        print(f"✗ ({response['error']})")

                    # Save intermediate results
                    if query_count % save_interval == 0:
                        self._save_responses(all_responses, f"responses_temp_{self.provider}.json")
                        print(f"  → 已儲存中間結果 ({query_count} 個回應)")

                    # Rate limiting: sleep briefly between queries
                    time.sleep(0.5)

        return all_responses

    def _save_responses(self, responses: List[Dict[str, Any]], filename: str):
        """Save responses to JSON file"""
        from pathlib import Path

        # Get the project root directory
        project_root = Path(__file__).parent.parent
        responses_dir = project_root / "data" / "responses"
        responses_dir.mkdir(parents=True, exist_ok=True)

        filepath = responses_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

    def save_all_responses(self, responses: List[Dict[str, Any]], filename: Optional[str] = None):
        """Save all responses to final file"""
        from pathlib import Path

        if filename is None:
            filename = f"{self.provider}_responses.json"

        self._save_responses(responses, filename)

        project_root = Path(__file__).parent.parent
        filepath = project_root / "data" / "responses" / filename
        print(f"\n所有回應已儲存至: {filepath}")


def main():
    """Test the API caller with both providers"""
    print("測試 LLM API 連接...")

    # Test Anthropic
    print("\n=== 測試 Anthropic (Claude) ===")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            tester = LLMTester(model_name="claude-sonnet-4-5-20250929")
            test_question = "計算 234 + 567"
            print(f"測試問題: {test_question}")
            response = tester.query(test_question)
            if response["success"]:
                print(f"✓ 成功!")
                print(f"回應: {response['answer']}")
                print(f"回應時間: {response['response_time']:.2f} 秒")
            else:
                print(f"✗ 失敗: {response['error']}")
        except Exception as e:
            print(f"✗ Anthropic 測試失敗: {e}")
    else:
        print("未設置 ANTHROPIC_API_KEY，跳過測試")

    # Test OpenAI
    print("\n=== 測試 OpenAI ===")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            # Test GPT-4o
            print("\n--- GPT-4o ---")
            tester = LLMTester(model_name="gpt-4o")
            test_question = "計算 234 + 567"
            print(f"測試問題: {test_question}")
            response = tester.query(test_question)
            if response["success"]:
                print(f"✓ 成功!")
                print(f"回應: {response['answer']}")
                print(f"回應時間: {response['response_time']:.2f} 秒")
            else:
                print(f"✗ 失敗: {response['error']}")

            # Test GPT-3.5-turbo
            print("\n--- GPT-3.5-Turbo ---")
            tester = LLMTester(model_name="gpt-3.5-turbo")
            response = tester.query(test_question)
            if response["success"]:
                print(f"✓ 成功!")
                print(f"回應: {response['answer']}")
                print(f"回應時間: {response['response_time']:.2f} 秒")
            else:
                print(f"✗ 失敗: {response['error']}")

        except Exception as e:
            print(f"✗ OpenAI 測試失敗: {e}")
    else:
        print("未設置 OPENAI_API_KEY，跳過測試")


if __name__ == "__main__":
    main()
