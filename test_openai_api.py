#!/usr/bin/env python3
"""
Quick test script for OpenAI API
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api_caller import LLMTester

def main():
    # Test with OpenAI API
    print("=" * 60)
    print("測試 OpenAI API")
    print("=" * 60)

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ 錯誤: 未設置 OPENAI_API_KEY 環境變數")
        print("請執行: export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)

    print(f"API Key: {openai_key[:20]}...{openai_key[-4:]}")

    # Test GPT-4o
    print("\n--- 測試 GPT-4o ---")
    try:
        tester = LLMTester(model_name="gpt-4o")
        test_question = "計算 234 + 567"
        print(f"問題: {test_question}")

        response = tester.query(test_question)

        if response["success"]:
            print(f"✓ 成功!")
            print(f"回應: {response['answer']}")
            print(f"回應時間: {response['response_time']:.2f} 秒")
        else:
            print(f"✗ 失敗: {response['error']}")
    except Exception as e:
        print(f"✗ 例外: {e}")

    # Test GPT-3.5-turbo
    print("\n--- 測試 GPT-3.5-Turbo ---")
    try:
        tester = LLMTester(model_name="gpt-3.5-turbo")

        response = tester.query(test_question)

        if response["success"]:
            print(f"✓ 成功!")
            print(f"回應: {response['answer']}")
            print(f"回應時間: {response['response_time']:.2f} 秒")
        else:
            print(f"✗ 失敗: {response['error']}")
    except Exception as e:
        print(f"✗ 例外: {e}")

if __name__ == "__main__":
    main()
