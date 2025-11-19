"""
API caller for querying LLMs.
統一的 LLM API 呼叫介面
"""
import os
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import anthropic
from openai import OpenAI


class LLMTester:
    """統一的 LLM API 呼叫介面，支持 Claude 和 OpenAI"""

    def __init__(
        self,
        provider: str = "claude",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize LLM tester.

        Args:
            provider: API provider ("claude" or "openai")
            model_name: Name of the model to use (if None, uses default for provider)
            api_key: API key (if None, will use environment variable)
        """
        self.provider = provider.lower()

        if self.provider not in ["claude", "openai"]:
            raise ValueError(f"Unsupported provider: {provider}. Choose 'claude' or 'openai'.")

        # Set model name based on provider
        if model_name:
            self.model_name = model_name
        else:
            if self.provider == "claude":
                self.model_name = "claude-sonnet-4-5-20250929"
            else:  # openai
                self.model_name = "gpt-4o"

        # Get API key
        if self.provider == "claude":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("API key not found. Set ANTHROPIC_API_KEY environment variable.")
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:  # openai
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("API key not found. Set OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=self.api_key)

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

                if self.provider == "claude":
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
                    answer_text = message.content[0].text

                else:  # openai
                    response = self.client.chat.completions.create(
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
                    answer_text = response.choices[0].message.content

                end_time = time.time()

                response_data = {
                    "question": question,
                    "answer": answer_text,
                    "model": self.model_name,
                    "provider": self.provider,
                    "temperature": temperature,
                    "response_time": end_time - start_time,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "error": None
                }

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

        print(f"開始批次查詢: {len(questions)} 個問題 × 3 個版本 × {repeat} 次重複 = {total_queries} 次查詢")

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
                        self._save_responses(all_responses, "responses_temp.json")
                        print(f"  → 已儲存中間結果 ({query_count} 個回應)")

                    # Rate limiting: sleep briefly between queries
                    time.sleep(0.5)

        return all_responses

    def _save_responses(self, responses: List[Dict[str, Any]], filename: str):
        """Save responses to JSON file"""
        filepath = f"../data/responses/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

    def save_all_responses(self, responses: List[Dict[str, Any]], filename: str = "claude_responses.json"):
        """Save all responses to final file"""
        self._save_responses(responses, filename)
        print(f"\n所有回應已儲存至: ../data/responses/{filename}")


def main():
    """Test the API caller with a simple question"""
    import sys

    # Determine which provider to test
    provider = "claude"
    if len(sys.argv) > 1:
        provider = sys.argv[1].lower()

    if provider not in ["claude", "openai"]:
        print("用法: python api_caller.py [claude|openai]")
        return

    print(f"測試 {provider.upper()} API 連接...")

    # Check if API key is available
    if provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        key_name = "ANTHROPIC_API_KEY"
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        key_name = "OPENAI_API_KEY"

    if not api_key:
        print(f"錯誤: 未設置 {key_name} 環境變數")
        print(f"請執行: export {key_name}='your-api-key'")
        return

    try:
        tester = LLMTester(provider=provider)

        # Test with a simple question
        test_question = "計算 234 + 567"
        print(f"\n測試問題: {test_question}")
        print(f"使用模型: {tester.model_name}")

        response = tester.query(test_question)

        if response["success"]:
            print(f"✓ 成功!")
            print(f"提供商: {response['provider']}")
            print(f"回應: {response['answer']}")
            print(f"回應時間: {response['response_time']:.2f} 秒")
        else:
            print(f"✗ 失敗: {response['error']}")

    except Exception as e:
        print(f"✗ 初始化失敗: {e}")


if __name__ == "__main__":
    main()
