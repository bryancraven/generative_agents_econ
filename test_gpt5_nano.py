#!/usr/bin/env python3
"""
Test script for modernized GPT-5-nano Responses API
"""
import sys
sys.path.append('reverie/backend_server/persona/prompt_template')

from gpt_structure import (
    ChatGPT_single_request,
    ChatGPT_safe_generate_response,
    GPT4_request
)

def test_simple_request():
    """Test simple API request"""
    print("=" * 60)
    print("TEST 1: Simple ChatGPT Request")
    print("=" * 60)

    prompt = "What is 2+2? Answer in one word."
    print(f"Prompt: {prompt}")
    print("\nCalling GPT-5-nano with minimal reasoning...")

    try:
        response = ChatGPT_single_request(prompt)
        print(f"\nResponse: {response}")
        print("✓ Test 1 PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Test 1 FAILED: {e}")
        return False


def test_gpt4_request():
    """Test GPT4 request (now using GPT-5-nano)"""
    print("\n" + "=" * 60)
    print("TEST 2: GPT4_request (using GPT-5-nano)")
    print("=" * 60)

    prompt = "Name one primary color. Answer in one word."
    print(f"Prompt: {prompt}")
    print("\nCalling GPT-5-nano via GPT4_request...")

    try:
        response = GPT4_request(prompt)
        print(f"\nResponse: {response}")
        print("✓ Test 2 PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Test 2 FAILED: {e}")
        return False


def test_structured_output():
    """Test structured output with validation"""
    print("\n" + "=" * 60)
    print("TEST 3: Structured Output with Validation")
    print("=" * 60)

    prompt = "What is a good activity for someone driving to a friend's house?"
    print(f"Prompt: {prompt}")
    print("Expected: Short answer (1-3 words)")
    print("\nCalling GPT-5-nano with structured output...")

    try:
        def validate_short(response, prompt=None):
            """Validate response is short"""
            return len(response.split()) <= 5

        def cleanup(response, prompt=None):
            """Clean up response"""
            return response.strip()

        response = ChatGPT_safe_generate_response(
            prompt,
            example_output="listening to music",
            special_instruction="Output a brief activity suggestion (1-3 words).",
            repeat=3,
            func_validate=validate_short,
            func_clean_up=cleanup,
            verbose=True
        )

        if response:
            print(f"\nFinal Response: {response}")
            print("✓ Test 3 PASSED")
            return True
        else:
            print("\n✗ Test 3 FAILED: No valid response after retries")
            return False

    except Exception as e:
        print(f"\n✗ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("TESTING GPT-5-NANO WITH RESPONSES API")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Simple Request", test_simple_request()))
    results.append(("GPT4 Request", test_gpt4_request()))
    results.append(("Structured Output", test_structured_output()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("=" * 60)

    return all(passed for _, passed in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
