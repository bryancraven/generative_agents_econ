"""
Author: Joon Sung Park (joonspk@stanford.edu)
Updated: Adapted for OpenRouter API with xiaomi/mimo-v2-flash:free model

File: gpt_structure.py
Description: Wrapper functions for calling LLM APIs via OpenRouter.
"""
import json
import os
import re
import time
from typing import Optional, Callable, Any
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Try to import LLM logging (only available when event bus is enabled)
try:
    from event_bus import emit_llm_request, emit_llm_response
    LLM_LOGGING_ENABLED = True
except ImportError:
    LLM_LOGGING_ENABLED = False
    def emit_llm_request(*args, **kwargs): pass
    def emit_llm_response(*args, **kwargs): pass

# Load environment variables from .env file
load_dotenv()

# Initialize OpenRouter client (OpenAI-compatible API)
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Use xiaomi/mimo-v2-flash:free - fast, free model via OpenRouter
DEFAULT_MODEL = "xiaomi/mimo-v2-flash:free"


# ============================================================================
# #####################[SECTION 0: JSON EXTRACTION HELPERS] ##################
# ============================================================================

def _schema_to_example(schema: dict) -> str:
    """
    Convert JSON schema to example JSON string for prompt engineering.
    Used when the model doesn't support native JSON schema output.
    """
    def build_example(s):
        if isinstance(s, dict):
            if s.get("type") == "object":
                props = s.get("properties", {})
                return {k: build_example(v) for k, v in props.items()}
            elif s.get("type") == "array":
                items = s.get("items", {"type": "string"})
                return [build_example(items)]
            elif s.get("type") == "string":
                return "example_string"
            elif s.get("type") == "integer":
                return 0
            elif s.get("type") == "number":
                return 0.0
            elif s.get("type") == "boolean":
                return True
        return "value"

    example = build_example(schema)
    return json.dumps(example, indent=2)


def _extract_json_from_response(text: str) -> str:
    """
    Extract JSON from response text, handling markdown code blocks.
    """
    if not text:
        return "{}"

    text = text.strip()

    # Remove markdown code blocks
    if "```json" in text:
        match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1)
    elif "```" in text:
        match = re.search(r"```\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1)

    # Find JSON object or array boundaries
    text = text.strip()

    # Try to find JSON object
    if "{" in text:
        start = text.find("{")
        # Find matching closing brace
        depth = 0
        for i, c in enumerate(text[start:], start):
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i+1]

    # Try to find JSON array
    if "[" in text:
        start = text.find("[")
        depth = 0
        for i, c in enumerate(text[start:], start):
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return text[start:i+1]

    return text


def temp_sleep(seconds=0.1):
    """Rate limiting helper"""
    time.sleep(seconds)


# ============================================================================
# #####################[SECTION 1: STRUCTURED OUTPUT MODELS] #################
# ============================================================================

class JsonOutput(BaseModel):
    """Generic structured output model for JSON responses"""
    output: str


class ChatResponse(BaseModel):
    """Structured model for chat responses"""
    content: str


# ============================================================================
# #####################[SECTION 2: MODERN API FUNCTIONS] #####################
# ============================================================================

def ChatGPT_single_request(prompt: str) -> str:
    """
    Simple single request using Chat Completions API via OpenRouter.

    Args:
        prompt: User prompt string

    Returns:
        Response content as string
    """
    temp_sleep()

    try:
        emit_llm_request("ChatGPT_single_request", prompt, DEFAULT_MODEL)

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        result = response.choices[0].message.content

        emit_llm_response("ChatGPT_single_request", result, DEFAULT_MODEL)
        return result
    except Exception as e:
        print(f"ChatGPT ERROR: {e}")
        return "ChatGPT ERROR"


def GPT4_request(prompt: str) -> str:
    """
    Request using Chat Completions API via OpenRouter.
    Legacy function name maintained for compatibility.

    Args:
        prompt: User prompt string

    Returns:
        Response content as string
    """
    temp_sleep()

    try:
        emit_llm_request("GPT4_request", prompt, DEFAULT_MODEL)

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        result = response.choices[0].message.content

        emit_llm_response("GPT4_request", result, DEFAULT_MODEL)
        return result

    except Exception as e:
        print(f"ChatGPT ERROR: {e}")
        return "ChatGPT ERROR"


def ChatGPT_request(prompt: str) -> str:
    """
    Standard request using Chat Completions API via OpenRouter.

    Args:
        prompt: User prompt string

    Returns:
        Response content as string
    """
    try:
        emit_llm_request("ChatGPT_request", prompt, DEFAULT_MODEL)

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        result = response.choices[0].message.content

        emit_llm_response("ChatGPT_request", result, DEFAULT_MODEL)
        return result

    except Exception as e:
        print(f"ChatGPT ERROR: {e}")
        return "ChatGPT ERROR"


def ChatGPT_structured_request(prompt: str, response_format: dict = None) -> str:
    """
    Request with JSON output using prompt engineering via OpenRouter.
    Uses prompt-based JSON extraction since free models don't support JSON schema.

    Args:
        prompt: User prompt string
        response_format: JSON schema for structured output (used to generate example)

    Returns:
        Response content as string (JSON)
    """
    try:
        # Build prompt with JSON instruction
        json_prompt = prompt
        if response_format:
            example = _schema_to_example(response_format)
            json_prompt += f"\n\nYou MUST respond with valid JSON in exactly this format:\n{example}\n\nRespond with ONLY the JSON, no other text or explanation."

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": json_prompt}],
            temperature=0.3,  # Lower temp for more deterministic JSON
            max_tokens=2000
        )

        result = response.choices[0].message.content

        # Extract JSON from response (handle markdown code blocks)
        result = _extract_json_from_response(result)

        # Validate it's parseable JSON
        json.loads(result)
        return result

    except json.JSONDecodeError as e:
        print(f"ChatGPT Structured JSON Parse ERROR: {e}")
        return '{"output": "error"}'
    except Exception as e:
        print(f"ChatGPT Structured ERROR: {e}")
        return '{"output": "error"}'


def GPT4_safe_generate_response(
    prompt: str,
    example_output: str,
    special_instruction: str,
    repeat: int = 3,
    fail_safe_response: str = "error",
    func_validate: Optional[Callable] = None,
    func_clean_up: Optional[Callable] = None,
    verbose: bool = False
) -> Any:
    """
    Safe generation with validation and retry logic using structured outputs.

    Args:
        prompt: The main prompt
        example_output: Example of expected output
        special_instruction: Additional instructions
        repeat: Number of retry attempts
        fail_safe_response: Fallback response on failure
        func_validate: Validation function
        func_clean_up: Cleanup function
        verbose: Print debug info

    Returns:
        Validated and cleaned response or False on failure
    """
    # Construct structured prompt
    full_prompt = f'GPT Prompt:\n"""\n{prompt}\n"""\n'
    full_prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
    full_prompt += "Example output json:\n"
    full_prompt += '{"output": "' + str(example_output) + '"}'

    if verbose:
        print("CHAT GPT PROMPT")
        print(full_prompt)

    # Define JSON schema for structured output (Responses API format)
    response_format = {
        "type": "object",
        "properties": {
            "output": {"type": "string"}
        },
        "required": ["output"],
        "additionalProperties": False
    }

    for i in range(repeat):
        try:
            # Use structured output to ensure valid JSON
            curr_gpt_response = ChatGPT_structured_request(full_prompt, response_format).strip()

            # Parse JSON response
            parsed_response = json.loads(curr_gpt_response)["output"]

            # Validate if function provided
            if func_validate and func_validate(parsed_response, prompt=prompt):
                if func_clean_up:
                    return func_clean_up(parsed_response, prompt=prompt)
                return parsed_response

            if verbose:
                print(f"---- repeat count: {i}")
                print(parsed_response)
                print("~~~~")

        except Exception as e:
            if verbose:
                print(f"Error on attempt {i}: {e}")
            pass

    return False


def ChatGPT_safe_generate_response(
    prompt: str,
    example_output: str,
    special_instruction: str,
    repeat: int = 3,
    fail_safe_response: str = "error",
    func_validate: Optional[Callable] = None,
    func_clean_up: Optional[Callable] = None,
    verbose: bool = False
) -> Any:
    """
    Safe generation with validation and retry logic using structured outputs.
    Modern version using GPT-4o-mini with structured output enforcement.

    Args:
        prompt: The main prompt
        example_output: Example of expected output
        special_instruction: Additional instructions
        repeat: Number of retry attempts
        fail_safe_response: Fallback response on failure
        func_validate: Validation function
        func_clean_up: Cleanup function
        verbose: Print debug info

    Returns:
        Validated and cleaned response or False on failure
    """
    # Construct structured prompt
    full_prompt = f'"""\n{prompt}\n"""\n'
    full_prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
    full_prompt += "Example output json:\n"
    full_prompt += '{"output": "' + str(example_output) + '"}'

    if verbose:
        print("CHAT GPT PROMPT")
        print(full_prompt)

    # Define JSON schema for structured output (Responses API format)
    response_format = {
        "type": "object",
        "properties": {
            "output": {"type": "string"}
        },
        "required": ["output"],
        "additionalProperties": False
    }

    for i in range(repeat):
        try:
            # Use structured output to ensure valid JSON
            curr_gpt_response = ChatGPT_structured_request(full_prompt, response_format).strip()

            # Parse JSON response
            parsed_response = json.loads(curr_gpt_response)["output"]

            # Validate if function provided
            if func_validate and func_validate(parsed_response, prompt=prompt):
                if func_clean_up:
                    return func_clean_up(parsed_response, prompt=prompt)
                return parsed_response

            if verbose:
                print(f"---- repeat count: {i}")
                print(parsed_response)
                print("~~~~")

        except Exception as e:
            if verbose:
                print(f"Error on attempt {i}: {e}")
            pass

    return False


def ChatGPT_safe_generate_response_OLD(
    prompt: str,
    repeat: int = 3,
    fail_safe_response: str = "error",
    func_validate: Optional[Callable] = None,
    func_clean_up: Optional[Callable] = None,
    verbose: bool = False
) -> Any:
    """
    Legacy safe generation without structured output (kept for compatibility).
    """
    if verbose:
        print("CHAT GPT PROMPT")
        print(prompt)

    for i in range(repeat):
        try:
            curr_gpt_response = ChatGPT_request(prompt).strip()
            if func_validate and func_validate(curr_gpt_response, prompt=prompt):
                if func_clean_up:
                    return func_clean_up(curr_gpt_response, prompt=prompt)
                return curr_gpt_response
            if verbose:
                print(f"---- repeat count: {i}")
                print(curr_gpt_response)
                print("~~~~")

        except Exception as e:
            if verbose:
                print(f"Error on attempt {i}: {e}")
            pass

    print("FAIL SAFE TRIGGERED")
    return fail_safe_response


# ============================================================================
# ###################[SECTION 3: LEGACY COMPATIBILITY] #######################
# ============================================================================

def GPT_request(prompt: str, gpt_parameter: dict) -> str:
    """
    Legacy completion request using Chat Completions API via OpenRouter.

    Args:
        prompt: The prompt string
        gpt_parameter: Dictionary of parameters (engine, temperature, etc.)

    Returns:
        Response text
    """
    temp_sleep()
    try:
        max_tokens = max(16, gpt_parameter.get("max_tokens", 150))
        temperature = gpt_parameter.get("temperature", 0.7)

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"TOKEN LIMIT EXCEEDED: {e}")
        return "TOKEN LIMIT EXCEEDED"


def generate_prompt(curr_input, prompt_lib_file):
    """
    Takes in the current input and the path to a prompt file.
    Replaces !<INPUT>! placeholders with actual input.

    Args:
        curr_input: Input(s) to feed in (string or list)
        prompt_lib_file: Path to the prompt file

    Returns:
        Final prompt string
    """
    if isinstance(curr_input, str):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]

    with open(prompt_lib_file, "r") as f:
        prompt = f.read()

    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)

    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]

    return prompt.strip()


def safe_generate_response(
    prompt: str,
    gpt_parameter: dict,
    repeat: int = 5,
    fail_safe_response: str = "error",
    func_validate: Optional[Callable] = None,
    func_clean_up: Optional[Callable] = None,
    verbose: bool = False
) -> Any:
    """
    Legacy safe generation with retry logic.

    Args:
        prompt: The prompt string
        gpt_parameter: Dictionary of GPT parameters
        repeat: Number of retry attempts
        fail_safe_response: Fallback response
        func_validate: Validation function
        func_clean_up: Cleanup function
        verbose: Print debug info

    Returns:
        Validated response or fail_safe_response
    """
    if verbose:
        print(prompt)

    for i in range(repeat):
        curr_gpt_response = GPT_request(prompt, gpt_parameter)
        if func_validate and func_validate(curr_gpt_response, prompt=prompt):
            if func_clean_up:
                return func_clean_up(curr_gpt_response, prompt=prompt)
            return curr_gpt_response
        if verbose:
            print(f"---- repeat count: {i}")
            print(curr_gpt_response)
            print("~~~~")

    return fail_safe_response


def get_embedding(text: str, model: str = None) -> list:
    """
    Get text embedding using local sentence-transformers model.
    Uses all-MiniLM-L6-v2 for 384-dimensional embeddings.

    Args:
        text: Text to embed
        model: Ignored (kept for backward compatibility)

    Returns:
        Embedding vector as list of floats (384 dimensions)
    """
    try:
        from persona.prompt_template.embeddings import get_embedding as local_get_embedding
        return local_get_embedding(text)
    except ImportError:
        # Fallback: try relative import
        try:
            from embeddings import get_embedding as local_get_embedding
            return local_get_embedding(text)
        except ImportError:
            print("Embedding ERROR: sentence-transformers not installed")
            return []
    except Exception as e:
        print(f"Embedding ERROR: {e}")
        return []


# ============================================================================
# #####################[SECTION 4: SCHEMA-BASED HELPERS] ####################
# ============================================================================

def _add_additional_properties_false(schema: dict) -> dict:
    """
    Recursively add 'additionalProperties': false to all object types in schema.
    Required for OpenAI Responses API structured output compliance.

    Args:
        schema: JSON Schema dict

    Returns:
        Modified schema with additionalProperties: false
    """
    if isinstance(schema, dict):
        # If this is an object type, add additionalProperties: false
        if schema.get("type") == "object":
            schema["additionalProperties"] = False

        # Recursively process all nested schemas
        for key, value in schema.items():
            if isinstance(value, dict):
                schema[key] = _add_additional_properties_false(value)
            elif isinstance(value, list):
                schema[key] = [_add_additional_properties_false(item) if isinstance(item, dict) else item
                               for item in value]

    return schema


def ChatGPT_schema_request(
    prompt: str,
    schema_class,
    repeat: int = 3,
    verbose: bool = False
):
    """
    Request with Pydantic schema validation.

    Args:
        prompt: User prompt string
        schema_class: Pydantic BaseModel class for response validation
        repeat: Number of retry attempts if validation fails
        verbose: Print debug info

    Returns:
        Validated Pydantic model instance or False on failure
    """
    # Get schema and ensure additionalProperties: false at all levels
    json_schema = schema_class.model_json_schema()
    json_schema = _add_additional_properties_false(json_schema)

    for attempt in range(repeat):
        try:
            # Get structured response
            response_text = ChatGPT_structured_request(prompt, json_schema)

            # Validate with Pydantic
            validated = schema_class.model_validate_json(response_text)

            if verbose:
                print(f"✓ Validation successful on attempt {attempt + 1}")

            return validated

        except Exception as e:
            if verbose:
                print(f"✗ Attempt {attempt + 1} failed: {e}")
            if attempt == repeat - 1:
                return False

    return False


def GPT_schema_safe_generate(
    prompt: str,
    schema_class,
    repeat: int = 3,
    fail_safe_response=None,
    verbose: bool = False
):
    """
    Safe generation with Pydantic schema validation and fail-safe.

    Args:
        prompt: User prompt string
        schema_class: Pydantic BaseModel class for response validation
        repeat: Number of retry attempts
        fail_safe_response: Response to return on failure (default: False)
        verbose: Print debug info

    Returns:
        Validated Pydantic model instance or fail_safe_response on failure
    """
    result = ChatGPT_schema_request(prompt, schema_class, repeat, verbose)

    if result is False:
        if verbose:
            print("FAIL SAFE TRIGGERED")
        return fail_safe_response if fail_safe_response is not None else False

    return result


def schema_to_legacy_format(schema_response, function_name: str):
    """
    Convert schema-based response to legacy format for backward compatibility.

    Args:
        schema_response: Pydantic model instance
        function_name: Name of the function (to determine conversion logic)

    Returns:
        Legacy format (varies by function)
    """
    # Task decomposition: [[task, duration], ...]
    if function_name == "task_decomp":
        return [[s.description, s.duration_minutes] for s in schema_response.subtasks]

    # Daily plan: [activity_description, ...]
    elif function_name == "daily_plan":
        return [f"{a.activity} at {a.time}" for a in schema_response.activities]

    # Hourly schedule: [[activity, duration], ...]
    elif function_name == "hourly_schedule":
        return [[a.activity, a.duration_minutes] for a in schema_response.activities]

    # Wake up hour: integer
    elif function_name == "wake_up_hour":
        return schema_response.wake_up_hour

    # Keywords: list of strings
    elif function_name == "extract_keywords":
        return schema_response.keywords

    # Poignancy: integer rating
    elif function_name == "poignancy":
        return schema_response.rating

    # Event triple: [subject, predicate, object]
    elif function_name == "event_triple":
        return [schema_response.subject, schema_response.predicate, schema_response.object]

    # Conversation: [[speaker, utterance], ...]
    elif function_name == "create_conversation":
        return [[u.speaker, u.utterance] for u in schema_response.conversation]

    # Default: return the model dict
    else:
        return schema_response.model_dump()


# ============================================================================
# #####################[SECTION 5: EXAMPLE USAGE] ############################
# ============================================================================

if __name__ == '__main__':
    # Example usage with modern API
    gpt_parameter = {
        "engine": DEFAULT_MODEL,
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ['"']
    }

    curr_input = ["driving to a friend's house"]
    prompt_lib_file = "prompt_template/test_prompt_July5.txt"

    # Test simple request
    test_prompt = "What is a good activity for: driving to a friend's house?"

    def __func_validate(gpt_response, prompt=None):
        if len(gpt_response.strip()) <= 1:
            return False
        if len(gpt_response.strip().split(" ")) > 1:
            return False
        return True

    def __func_clean_up(gpt_response, prompt=None):
        cleaned_response = gpt_response.strip()
        return cleaned_response

    # Test with new API
    print("Testing modern ChatGPT request:")
    output = ChatGPT_single_request(test_prompt)
    print(output)

    print("\nTesting structured output:")
    structured_output = ChatGPT_safe_generate_response(
        test_prompt,
        "listening to music",
        "Output a single word activity.",
        repeat=3,
        func_validate=lambda x, prompt=None: len(x.split()) <= 3,
        func_clean_up=lambda x, prompt=None: x.strip(),
        verbose=True
    )
    print(structured_output)
