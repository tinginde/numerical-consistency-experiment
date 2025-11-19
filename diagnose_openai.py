#!/usr/bin/env python3
"""
Diagnostic script for OpenAI API issues
"""
import os
from openai import OpenAI

def test_openai_api():
    print("=" * 60)
    print("OpenAI API 診斷工具")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 未設置 OPENAI_API_KEY")
        return

    print(f"API Key: {api_key[:20]}...{api_key[-4:]}")
    print(f"API Key 長度: {len(api_key)} 字元")

    try:
        client = OpenAI(api_key=api_key)

        print("\n嘗試發送測試請求...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, please respond with just the number 42."}
            ],
            max_tokens=10
        )

        print("✓ API 呼叫成功!")
        print(f"回應: {response.choices[0].message.content}")
        print(f"使用的 tokens: {response.usage.total_tokens}")

    except Exception as e:
        print(f"✗ API 呼叫失敗")
        print(f"錯誤類型: {type(e).__name__}")
        print(f"錯誤訊息: {str(e)}")

        # Try to get more details
        if hasattr(e, 'response'):
            print(f"HTTP 狀態碼: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
            if hasattr(e.response, 'text'):
                print(f"回應內容: {e.response.text}")

        print("\n可能的解決方案:")
        print("1. 確認 API key 是否正確複製（沒有多餘的空格）")
        print("2. 前往 https://platform.openai.com/api-keys 檢查 API key 狀態")
        print("3. 前往 https://platform.openai.com/account/billing 檢查帳戶信用額度")
        print("4. 確認 API key 有正確的權限設置")

if __name__ == "__main__":
    test_openai_api()
