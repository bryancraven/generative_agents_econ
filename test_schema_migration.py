#!/usr/bin/env python3
"""
Test Harness for Schema-Based Migration

Compares old string-parsing functions vs new schema-based functions.
Tests critical functions that were failing with GPT-5-nano.
"""

import sys
import os

# Add backend paths
sys.path.insert(0, '/Users/bryanc/dev/econ_agents/reverie/backend_server')
os.chdir('/Users/bryanc/dev/econ_agents/reverie/backend_server')

from persona.prompt_template.gpt_structure import ChatGPT_schema_request
from persona.prompt_template.prompt_schemas import (
    TaskDecomposition,
    WakeUpHourResponse,
    DailyPlanResponse,
    Subtask
)
import json


def test_task_decomposition_schema():
    """Test task decomposition with structured output"""
    print("=" * 70)
    print("TEST 1: Task Decomposition with Schema Validation")
    print("=" * 70)

    # Simulate a realistic task decomposition prompt
    prompt = """
Name: Isabella Rodriguez
Age: 34
Backstory: Isabella Rodriguez is a painter who wants to explore the world while working on her art.
Personality: creative, outgoing, passionate
Location: Isabella is at an artist's studio

Today is July 1, 2023. From 08:00am ~09:00am, Isabella is planning on having breakfast,
from 09:00am ~ 12:00pm, Isabella is planning on painting in her studio.

In 5 min increments, list the subtasks Isabella does when Isabella is painting in her studio
from 09:00am ~ 12:00pm (total duration in minutes: 180):

Return a JSON object with this EXACT structure:
{
  "subtasks": [
    {"description": "task description", "duration_minutes": 5},
    {"description": "task description", "duration_minutes": 10}
  ]
}

- Break the task into realistic 5-minute increments
- Each subtask must have "description" (string) and "duration_minutes" (integer)
- The sum of all duration_minutes should approximately equal 180
- Return ONLY the JSON object, no other text
"""

    print("\nPrompt (abbreviated):")
    print("Context: Isabella painting in studio for 180 minutes")
    print("Expected format: JSON with subtasks array\n")

    try:
        print("Calling GPT-5-nano with schema validation...")
        response = ChatGPT_schema_request(
            prompt,
            TaskDecomposition,
            repeat=3,
            verbose=True
        )

        if response:
            print("\n✓ SUCCESS! GPT-5-nano returned valid structured output")
            print(f"\nNumber of subtasks: {len(response.subtasks)}")
            print("\nSubtasks breakdown:")
            total_min = 0
            for i, subtask in enumerate(response.subtasks, 1):
                print(f"  {i}. {subtask.description}: {subtask.duration_minutes} min")
                total_min += subtask.duration_minutes
            print(f"\nTotal duration: {total_min} minutes (expected: 180)")

            # Convert to legacy format
            legacy_format = [[s.description, s.duration_minutes] for s in response.subtasks]
            print(f"\nLegacy format (first 3):")
            for task, duration in legacy_format[:3]:
                print(f"  ['{task}', {duration}]")

            return True
        else:
            print("\n✗ FAILED: Could not get valid response after retries")
            return False

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wake_up_hour_schema():
    """Test wake up hour with structured output"""
    print("\n" + "=" * 70)
    print("TEST 2: Wake Up Hour with Schema Validation")
    print("=" * 70)

    prompt = """
Name: Isabella Rodriguez
Age: 34
Personality: creative, outgoing, passionate
Lifestyle: Isabella is a professional painter who keeps a regular schedule

In general, Isabella wakes up early to catch the morning light for painting.
Isabella's wake up hour:

Return a JSON object with the wake up hour.
The hour must be between 0-23 (e.g., 6 for 6am, 14 for 2pm).
Example: {"wake_up_hour": 8}
"""

    print("\nPrompt (abbreviated):")
    print("Context: Isabella, morning person painter")
    print("Expected format: JSON with wake_up_hour (0-23)\n")

    try:
        print("Calling GPT-5-nano with schema validation...")
        response = ChatGPT_schema_request(
            prompt,
            WakeUpHourResponse,
            repeat=3,
            verbose=True
        )

        if response:
            print(f"\n✓ SUCCESS! Wake up hour: {response.wake_up_hour}:00")
            print(f"Validation: Hour is between 0-23: {0 <= response.wake_up_hour <= 23}")
            return True
        else:
            print("\n✗ FAILED: Could not get valid response")
            return False

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_daily_plan_schema():
    """Test daily plan with structured output"""
    print("\n" + "=" * 70)
    print("TEST 3: Daily Plan with Schema Validation")
    print("=" * 70)

    prompt = """
Name: Isabella Rodriguez
Age: 34
Personality: creative, outgoing, passionate
Lifestyle: Isabella is a professional painter with a balanced routine

In general, Isabella maintains a healthy work-life balance while pursuing her art.
Today is July 1, 2023. Here is Isabella's plan today in broad-strokes
(with the time of the day. e.g., have a lunch at 12:00 pm, watch TV from 7 to 8 pm):
1) wake up and complete the morning routine at 6:00 am, 2)

Return a JSON object with the daily activities:
{
  "activities": [
    {"activity": "eat breakfast", "time": "7:00 am"},
    {"activity": "work on project", "time": "9:00 am"}
  ]
}

- Include activities with their times throughout the day
- Use natural language for activities
- Times should be in format like "8:00 am" or "2:00 pm"
"""

    print("\nPrompt (abbreviated):")
    print("Context: Isabella's daily plan")
    print("Expected format: JSON with activities array\n")

    try:
        print("Calling GPT-5-nano with schema validation...")
        response = ChatGPT_schema_request(
            prompt,
            DailyPlanResponse,
            repeat=3,
            verbose=True
        )

        if response:
            print(f"\n✓ SUCCESS! {len(response.activities)} activities planned")
            print("\nDaily schedule:")
            for activity in response.activities:
                print(f"  {activity.time}: {activity.activity}")

            # Convert to legacy format
            legacy_format = [f"{a.activity} at {a.time}" for a in response.activities]
            print(f"\nLegacy format (first 3):")
            for act in legacy_format[:3]:
                print(f"  '{act}'")

            return True
        else:
            print("\n✗ FAILED: Could not get valid response")
            return False

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pydantic_validation():
    """Test Pydantic validation edge cases"""
    print("\n" + "=" * 70)
    print("TEST 4: Pydantic Validation Edge Cases")
    print("=" * 70)

    print("\nTest 4a: Valid task decomposition")
    try:
        valid_data = {
            "subtasks": [
                {"description": "setup easel", "duration_minutes": 5},
                {"description": "mix paints", "duration_minutes": 10}
            ]
        }
        decomp = TaskDecomposition(**valid_data)
        print("✓ Valid data accepted")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

    print("\nTest 4b: Invalid duration (negative)")
    try:
        invalid_data = {
            "subtasks": [
                {"description": "paint", "duration_minutes": -5}
            ]
        }
        decomp = TaskDecomposition(**invalid_data)
        print("✗ Should have rejected negative duration!")
        return False
    except Exception as e:
        print(f"✓ Correctly rejected: {type(e).__name__}")

    print("\nTest 4c: Invalid duration (too large)")
    try:
        invalid_data = {
            "subtasks": [
                {"description": "paint", "duration_minutes": 500}
            ]
        }
        decomp = TaskDecomposition(**invalid_data)
        print("✗ Should have rejected duration > 180!")
        return False
    except Exception as e:
        print(f"✓ Correctly rejected: {type(e).__name__}")

    print("\nTest 4d: Empty subtasks list")
    try:
        invalid_data = {"subtasks": []}
        decomp = TaskDecomposition(**invalid_data)
        print("✗ Should have rejected empty list!")
        return False
    except Exception as e:
        print(f"✓ Correctly rejected: {type(e).__name__}")

    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("SCHEMA-BASED MIGRATION TEST HARNESS")
    print("Testing GPT-5-nano with Structured Outputs")
    print("=" * 70)

    results = []

    # Run API-based tests (require OpenAI API key)
    print("\n📡 API-BASED TESTS (require OpenAI API key)")
    results.append(("Task Decomposition Schema", test_task_decomposition_schema()))
    results.append(("Wake Up Hour Schema", test_wake_up_hour_schema()))
    results.append(("Daily Plan Schema", test_daily_plan_schema()))

    # Run validation tests (no API required)
    print("\n🔍 VALIDATION TESTS (local only)")
    results.append(("Pydantic Validation", test_pydantic_validation()))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Schema migration is working correctly.")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed.")

    print("=" * 70)

    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
