#!/usr/bin/env python3
"""
Detailed diagnostic script to troubleshoot OpenAI API connectivity issues.
"""
import os
from openai import OpenAI

def test_openai_api():
    """Test OpenAI API with detailed diagnostics."""
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        return False

    print(f"✓ API key found: {api_key[:20]}...{api_key[-4:]}")
    print(f"  API key length: {len(api_key)} characters")
    print(f"  API key prefix: {api_key.split('-')[0] if '-' in api_key else 'N/A'}")

    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized\n")

        # Test 1: List available models
        print("=" * 60)
        print("TEST 1: Listing available models...")
        print("=" * 60)
        try:
            models = client.models.list()
            print(f"✓ Successfully retrieved model list")
            print(f"  Total models available: {len(models.data)}")

            # Show some available models
            model_ids = [m.id for m in models.data]
            gpt_models = [m for m in model_ids if 'gpt' in m.lower()]
            print(f"\n  Available GPT models ({len(gpt_models)}):")
            for model in sorted(gpt_models)[:10]:
                print(f"    - {model}")
            if len(gpt_models) > 10:
                print(f"    ... and {len(gpt_models) - 10} more")

        except Exception as e:
            print(f"❌ Failed to list models: {type(e).__name__}: {str(e)}")

        # Test 2: Try different models
        models_to_test = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-4o-mini",
            "gpt-4o"
        ]

        print("\n" + "=" * 60)
        print("TEST 2: Testing different models...")
        print("=" * 60)

        for model_name in models_to_test:
            print(f"\nTrying model: {model_name}")
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "user", "content": "Reply with just: OK"}
                    ],
                    max_tokens=10,
                    temperature=0
                )

                message = response.choices[0].message.content
                print(f"  ✓ SUCCESS!")
                print(f"    Response: {message}")
                print(f"    Model used: {response.model}")
                print(f"    Tokens: {response.usage.total_tokens}")
                print(f"\n✅ Working model found: {model_name}")
                return True

            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ Failed: {type(e).__name__}")
                if "does not exist" in error_msg or "model_not_found" in error_msg.lower():
                    print(f"    Reason: Model not available")
                elif "permission" in error_msg.lower() or "denied" in error_msg.lower():
                    print(f"    Reason: Permission denied")
                elif "quota" in error_msg.lower():
                    print(f"    Reason: Quota exceeded")
                else:
                    print(f"    Reason: {error_msg[:100]}")

        print("\n" + "=" * 60)
        print("❌ All model tests failed")
        print("=" * 60)
        return False

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_api()
