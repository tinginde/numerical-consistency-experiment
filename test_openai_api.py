#!/usr/bin/env python3
"""
Simple test script to verify OpenAI API connectivity.
"""
import os
from openai import OpenAI

def test_openai_api():
    """Test OpenAI API with a simple request."""
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        return False

    print(f"✓ API key found: {api_key[:20]}...{api_key[-4:]}")

    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized")

        # Make a simple test request
        print("\nTesting API with a simple completion request...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello! API is working.' in exactly those words."}
            ],
            max_tokens=20,
            temperature=0
        )

        # Extract response
        message = response.choices[0].message.content
        print(f"\n✓ API Response: {message}")
        print(f"✓ Model used: {response.model}")
        print(f"✓ Tokens used: {response.usage.total_tokens}")

        print("\n✅ SUCCESS: OpenAI API is working correctly!")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_api()
