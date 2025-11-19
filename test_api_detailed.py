#!/usr/bin/env python3
"""详细的 API 错误诊断"""
import os
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")
print(f"API Key: {api_key[:30]}...{api_key[-10:]}")
print(f"Length: {len(api_key)}")

client = OpenAI(api_key=api_key)

print("\n尝试调用 API...")
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=5
    )
    print(f"✓ 成功: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ 错误类型: {type(e).__name__}")
    print(f"❌ 错误信息: {e}")

    # 打印更多详细信息
    if hasattr(e, 'response'):
        print(f"❌ Response: {e.response}")
    if hasattr(e, 'status_code'):
        print(f"❌ Status code: {e.status_code}")
    if hasattr(e, 'body'):
        print(f"❌ Body: {e.body}")
