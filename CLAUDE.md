# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modernized fork of the "Generative Agents: Interactive Simulacra of Human Behavior" simulation framework (originally called "Reverie"). It simulates believable human behavior using LLM-powered agents that have memory, planning, and social capabilities.

**Modernization Status**: Upgraded from GPT-3.5-turbo (OpenAI SDK 0.27.0) to GPT-5-nano with the Responses API (OpenAI SDK 2.5.0+), using structured outputs and minimal reasoning for cost efficiency.

## Architecture

### Two-Server Architecture

The system requires two concurrent servers:

1. **Environment Server** (Django) - `environment/frontend_server/`
   - Browser-based visualization at `localhost:8000`
   - Serves the 2D map interface showing agent movements
   - Handles replay/demo functionality
   - Storage location: `environment/frontend_server/storage/`

2. **Simulation Server** (Python) - `reverie/backend_server/`
   - Entry point: `reverie.py`
   - Manages agent state and progression
   - Handles all LLM interactions
   - CLI-based control interface

### Core Components

**ReverieServer** (`reverie/backend_server/reverie.py`)
- Main simulation controller
- Manages time progression (steps = 10 seconds game time)
- Maintains all agent (persona) instances
- Handles simulation forking and saving

**Persona** (`reverie/backend_server/persona/persona.py`)
- The generative agent class (internally called "Persona" from 2022 terminology)
- Three memory systems:
  - `s_mem`: Spatial memory (locations as tree structure)
  - `a_mem`: Associative memory (the "Memory Stream" from the paper)
  - `scratch`: Short-term/working memory

**Cognitive Modules** (`reverie/backend_server/persona/cognitive_modules/`)
- `perceive.py`: Filters nearby events based on attention bandwidth and retention
- `retrieve.py`: Retrieves relevant memories using recency, importance, and relevance
- `plan.py`: Generates daily schedules and decomposes actions
- `reflect.py`: Creates higher-level insights from memories
- `execute.py`: Executes planned actions in the environment
- `converse.py`: Handles agent-to-agent conversations

**LLM Integration** (`reverie/backend_server/persona/prompt_template/`)
- `gpt_structure.py`: Wrapper for OpenAI API (modernized to use Responses API)
- `run_gpt_prompt.py`: All prompt functions that interface with the LLM
- Uses GPT-5-nano-2025-08-07 with minimal reasoning effort

## Environment Setup

### First-Time Setup

1. **Configure API Key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Legacy Setup** (if needed):
   Create `reverie/backend_server/utils.py` with legacy configuration (see README.md)

### Running Tests

```bash
# Test OpenAI API integration
python test_gpt5_nano.py
```

## Running Simulations

### Starting a New Simulation

**Terminal 1 - Environment Server**:
```bash
cd environment/frontend_server
python manage.py runserver
# Browser: http://localhost:8000/ (should show "server is running")
```

**Terminal 2 - Simulation Server**:
```bash
cd reverie/backend_server
python reverie.py
# Enter fork simulation: base_the_ville_isabella_maria_klaus
# Enter new simulation name: test-simulation
```

### Simulation Commands

Once both servers are running:

- `run <steps>`: Run simulation for N steps (e.g., `run 100`)
  - 1 step = 10 seconds game time
  - Monitor at: `http://localhost:8000/simulator_home`
- `exit`: Exit without saving
- `fin`: Save and exit

### Replay & Demo

**Replay** (debugging, identical sprites):
```
http://localhost:8000/replay/<simulation-name>/<starting-step>/
```

**Demo** (proper sprites, requires compression):
```bash
# First, compress the simulation
cd reverie
python compress_sim_storage.py
# In the file, call: compress("simulation-name")

# Then view at:
# http://localhost:8000/demo/<simulation-name>/<starting-step>/<speed>
# Speed: 1 (slowest) to 5 (fastest)
```

## Key Terminology Differences

The codebase uses older internal terminology from 2022:

| Paper Term | Code Term |
|------------|-----------|
| Generative Agent | Persona |
| Memory Stream | Associative Memory |
| Simulation Framework | Reverie |

## OpenAI API Integration

### Model Configuration

- **Current Model**: `gpt-5-nano-2025-08-07`
- **API Pattern**: Responses API with minimal reasoning
- **Cost**: $0.05 per 1M input tokens, $0.40 per 1M output tokens

### Adding New LLM Prompts

When adding new prompt functions in `run_gpt_prompt.py`:

1. Create a `create_prompt_input()` inner function
2. Define validation function: `def __func_validate(gpt_response, prompt="")`
3. Define cleanup function: `def __func_clean_up(gpt_response, prompt="")`
4. Call structured or safe generation functions:
   - `ChatGPT_safe_generate_response()` - for JSON outputs with validation
   - `ChatGPT_single_request()` - for simple text responses

### Structured Outputs

Use structured outputs for reliable JSON parsing:

```python
from gpt_structure import ChatGPT_safe_generate_response

response = ChatGPT_safe_generate_response(
    prompt=my_prompt,
    example_output="example response",
    special_instruction="Output format instructions",
    repeat=3,  # retry attempts
    func_validate=my_validator,
    func_clean_up=my_cleanup,
    verbose=False
)
```

## Simulation Storage Structure

```
environment/frontend_server/storage/<sim-name>/
├── reverie/
│   └── meta.json           # Simulation metadata
├── personas/
│   └── <persona-name>/
│       └── bootstrap_memory/
│           ├── associative_memory/  # Memory stream (nodes.json, embeddings.json)
│           ├── spatial_memory.json  # Location tree
│           └── scratch.json         # Working memory
└── movement/
    └── <step>.json         # Agent positions per step
```

## Memory System Details

### Associative Memory (Memory Stream)

Stores events as `ConceptNode` objects with:
- **Type**: event, thought, or chat
- **SPO**: Subject-Predicate-Object triples
- **Metadata**: created time, expiration, poignancy, keywords
- **Embeddings**: Vector embeddings for semantic retrieval (using text-embedding-ada-002)

### Retrieval Algorithm

Combines three scores for memory relevance:
1. **Recency**: Exponential decay based on time
2. **Importance**: Poignancy score (1-10)
3. **Relevance**: Cosine similarity of embeddings

## File Locations Reference

- **Simulation control**: `reverie/backend_server/reverie.py`
- **Agent logic**: `reverie/backend_server/persona/persona.py`
- **LLM wrappers**: `reverie/backend_server/persona/prompt_template/gpt_structure.py`
- **Prompt functions**: `reverie/backend_server/persona/prompt_template/run_gpt_prompt.py`
- **Django views**: `environment/frontend_server/translator/views.py`
- **Compression utility**: `reverie/compress_sim_storage.py`

## Security Notes

- `.env` file contains API key and is gitignored
- `reverie/backend_server/utils.py` contains legacy API key and is gitignored
- Never commit these files or expose API keys in code

## Common Issues

1. **OpenAI API rate limiting**: Save simulation frequently with `fin` command. Rate limit delays may require restart.
2. **Simulation forking**: All simulations must fork from a base simulation (hand-crafted initial state).
3. **Time steps**: Remember 1 step = 10 seconds. Plan accordingly for simulation duration.
4. **Browser compatibility**: Use Chrome or Safari. Firefox may have frontend glitches.
