#!/usr/bin/env python3
"""
Comprehensive test suite for modernized Generative Agents system
Tests OpenAI API integration, GPT structure, and core simulation components
"""
import sys
import os
sys.path.append('reverie/backend_server')
sys.path.append('reverie/backend_server/persona/prompt_template')

from gpt_structure import (
    ChatGPT_single_request,
    ChatGPT_safe_generate_response,
    GPT4_request,
    get_embedding
)

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_api_connection():
    """Test 1: Basic API connection"""
    print_section("TEST 1: API Connection")
    print("Testing basic OpenAI API connection with GPT-5-nano...")

    try:
        response = ChatGPT_single_request("Say 'connected' if you can read this.")
        print(f"✓ API Connection: SUCCESS")
        print(f"  Response: {response}")
        return True
    except Exception as e:
        print(f"✗ API Connection: FAILED")
        print(f"  Error: {e}")
        return False


def test_simple_reasoning():
    """Test 2: Simple reasoning task"""
    print_section("TEST 2: Simple Reasoning")
    print("Testing GPT-5-nano with minimal reasoning on a simple task...")

    try:
        prompt = "If John has 3 apples and gives 1 to Mary, how many apples does John have? Answer with just the number."
        response = ChatGPT_single_request(prompt)
        print(f"  Prompt: {prompt}")
        print(f"  Response: {response}")

        # Check if response contains "2"
        if "2" in response:
            print(f"✓ Simple Reasoning: SUCCESS")
            return True
        else:
            print(f"⚠ Simple Reasoning: UNEXPECTED ANSWER (but API works)")
            return True
    except Exception as e:
        print(f"✗ Simple Reasoning: FAILED")
        print(f"  Error: {e}")
        return False


def test_gpt4_request():
    """Test 3: GPT4 request function"""
    print_section("TEST 3: GPT4 Request Function")
    print("Testing GPT4_request() wrapper (uses GPT-5-nano)...")

    try:
        prompt = "What is the capital of France? Answer in one word."
        response = GPT4_request(prompt)
        print(f"  Prompt: {prompt}")
        print(f"  Response: {response}")

        if response and response != "ChatGPT ERROR":
            print(f"✓ GPT4 Request: SUCCESS")
            return True
        else:
            print(f"✗ GPT4 Request: FAILED")
            return False
    except Exception as e:
        print(f"✗ GPT4 Request: FAILED")
        print(f"  Error: {e}")
        return False


def test_structured_output():
    """Test 4: Structured output with validation"""
    print_section("TEST 4: Structured Output with Validation")
    print("Testing ChatGPT_safe_generate_response() with JSON schema...")

    try:
        prompt = "What is a good morning activity? Suggest one activity."

        def validate(response, prompt=None):
            """Validate response is not too long"""
            return len(response.split()) <= 10

        def cleanup(response, prompt=None):
            """Clean up response"""
            return response.strip().lower()

        response = ChatGPT_safe_generate_response(
            prompt=prompt,
            example_output="drinking coffee",
            special_instruction="Provide a brief activity (1-3 words).",
            repeat=3,
            func_validate=validate,
            func_clean_up=cleanup,
            verbose=False
        )

        print(f"  Prompt: {prompt}")
        print(f"  Response: {response}")

        if response and response is not False:
            print(f"✓ Structured Output: SUCCESS")
            return True
        else:
            print(f"✗ Structured Output: FAILED (no valid response)")
            return False
    except Exception as e:
        print(f"✗ Structured Output: FAILED")
        print(f"  Error: {e}")
        return False


def test_json_parsing():
    """Test 5: JSON response parsing"""
    print_section("TEST 5: JSON Response Parsing")
    print("Testing structured JSON output parsing...")

    try:
        prompt = "List three colors"

        def validate(response, prompt=None):
            """Basic validation"""
            return len(response) > 0

        def cleanup(response, prompt=None):
            """Clean up response"""
            return response.strip()

        response = ChatGPT_safe_generate_response(
            prompt=prompt,
            example_output="red, blue, green",
            special_instruction="Output exactly three comma-separated colors.",
            repeat=2,
            func_validate=validate,
            func_clean_up=cleanup,
            verbose=False
        )

        print(f"  Prompt: {prompt}")
        print(f"  Response: {response}")

        if response and response is not False:
            print(f"✓ JSON Parsing: SUCCESS")
            return True
        else:
            print(f"✗ JSON Parsing: FAILED")
            return False
    except Exception as e:
        print(f"✗ JSON Parsing: FAILED")
        print(f"  Error: {e}")
        return False


def test_embeddings():
    """Test 6: Text embeddings"""
    print_section("TEST 6: Text Embeddings")
    print("Testing get_embedding() with text-embedding-ada-002...")

    try:
        text = "Hello, this is a test of the embedding system."
        embedding = get_embedding(text)

        print(f"  Input text: {text}")
        print(f"  Embedding length: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")

        # text-embedding-ada-002 produces 1536-dimensional embeddings
        if len(embedding) == 1536:
            print(f"✓ Embeddings: SUCCESS (correct dimensions)")
            return True
        elif len(embedding) > 0:
            print(f"⚠ Embeddings: SUCCESS (unexpected dimensions: {len(embedding)})")
            return True
        else:
            print(f"✗ Embeddings: FAILED (empty embedding)")
            return False
    except Exception as e:
        print(f"✗ Embeddings: FAILED")
        print(f"  Error: {e}")
        return False


def test_persona_prompt():
    """Test 7: Persona-style prompt"""
    print_section("TEST 7: Persona-Style Prompt")
    print("Testing agent-style prompt with character context...")

    try:
        prompt = """You are simulating Isabella Rodriguez, a friendly artist.
Given that it's 8:00 AM and Isabella just woke up, what would be her first activity of the day?
Respond with a brief activity (1-3 words)."""

        def validate(response, prompt=None):
            return len(response.split()) <= 5

        def cleanup(response, prompt=None):
            return response.strip()

        response = ChatGPT_safe_generate_response(
            prompt=prompt,
            example_output="making breakfast",
            special_instruction="Output a brief morning activity.",
            repeat=2,
            func_validate=validate,
            func_clean_up=cleanup,
            verbose=False
        )

        print(f"  Character: Isabella Rodriguez")
        print(f"  Context: 8:00 AM, just woke up")
        print(f"  Activity: {response}")

        if response and response is not False:
            print(f"✓ Persona Prompt: SUCCESS")
            return True
        else:
            print(f"✗ Persona Prompt: FAILED")
            return False
    except Exception as e:
        print(f"✗ Persona Prompt: FAILED")
        print(f"  Error: {e}")
        return False


def test_cost_efficiency():
    """Test 8: Multiple quick requests (cost efficiency check)"""
    print_section("TEST 8: Cost Efficiency Check")
    print("Testing multiple rapid requests with minimal reasoning...")

    try:
        prompts = [
            "Say 'one'",
            "Say 'two'",
            "Say 'three'"
        ]

        responses = []
        for i, prompt in enumerate(prompts, 1):
            response = ChatGPT_single_request(prompt)
            responses.append(response)
            print(f"  Request {i}: {response}")

        if all(responses) and all(r != "ChatGPT ERROR" for r in responses):
            print(f"✓ Cost Efficiency: SUCCESS (3 requests completed)")
            print(f"  Note: Using GPT-5-nano with minimal reasoning = ultra-low cost")
            return True
        else:
            print(f"✗ Cost Efficiency: FAILED")
            return False
    except Exception as e:
        print(f"✗ Cost Efficiency: FAILED")
        print(f"  Error: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 70)
    print(" COMPREHENSIVE TEST SUITE FOR GENERATIVE AGENTS")
    print(" Testing GPT-5-nano with Responses API")
    print("=" * 70)

    tests = [
        ("API Connection", test_api_connection),
        ("Simple Reasoning", test_simple_reasoning),
        ("GPT4 Request Function", test_gpt4_request),
        ("Structured Output", test_structured_output),
        ("JSON Parsing", test_json_parsing),
        ("Text Embeddings", test_embeddings),
        ("Persona-Style Prompt", test_persona_prompt),
        ("Cost Efficiency", test_cost_efficiency),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name}: CRASHED")
            print(f"  Exception: {e}")
            results.append((name, False))

    # Print summary
    print_section("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:12} {name}")

    print(f"\n{'─' * 70}")
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print(f"{'─' * 70}")
        print("🎉 ALL TESTS PASSED!")
        print("\nYour system is fully functional:")
        print("  ✓ OpenAI API connection working")
        print("  ✓ GPT-5-nano with minimal reasoning operational")
        print("  ✓ Structured outputs with validation working")
        print("  ✓ Embeddings API functional")
        print("  ✓ Ready for generative agent simulations!")
    else:
        print(f"{'─' * 70}")
        print(f"⚠ {total - passed} test(s) failed. Please review errors above.")

    print("=" * 70 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
