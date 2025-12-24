# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modernized fork of the "Generative Agents: Interactive Simulacra of Human Behavior" simulation framework (originally called "Reverie"). It simulates believable human behavior using LLM-powered agents that have memory, planning, and social capabilities.

**Modernization Status**: Now supports multiple LLM backends:
- **OpenRouter API** - Use any model via OpenRouter (default: `xiaomi/mimo-v2-flash:free`)
- **Local Embeddings** - sentence-transformers for embeddings (no OpenAI dependency)
- **React Dashboard** - Real-time monitoring via WebSocket

## Architecture

### Three-Component Architecture

The system has three main components:

1. **Environment Server** (Django) - `environment/frontend_server/`
   - Browser-based visualization at `localhost:8000`
   - Serves the 2D map interface showing agent movements
   - Handles replay/demo functionality
   - Storage location: `environment/frontend_server/storage/`

2. **Simulation Server** (Python) - `reverie/backend_server/`
   - Entry point: `reverie.py`
   - Manages agent state and progression
   - Handles all LLM interactions
   - Includes WebSocket server for dashboard (port 8765)
   - **IMPORTANT**: Must run from `reverie/backend_server/` directory

3. **React Dashboard** (optional) - `dashboard/`
   - Real-time monitoring at `localhost:3000`
   - Shows agent activities, LLM logs, minimap
   - Connects via WebSocket to simulation server

### Core Components

**ReverieServer** (`reverie/backend_server/reverie.py`)
- Main simulation controller
- Manages time progression (steps = 10 seconds game time)
- Maintains all agent (persona) instances
- Handles simulation forking and saving
- Includes integrated WebSocket server for React dashboard

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
- `gpt_structure.py`: LLM wrapper supporting OpenRouter API
- `embeddings.py`: Local embeddings using sentence-transformers
- `run_gpt_prompt.py`: All prompt functions that interface with the LLM

## Environment Setup

### First-Time Setup

1. **Configure API Key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key:
   # OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

2. **Create Virtual Environment** (Python 3.11 recommended):
   ```bash
   # Python 3.11 is recommended - Python 3.13 has compatibility issues
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create utils.py** (required, gitignored):
   Create `reverie/backend_server/utils.py`:
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()

   openai_api_key = os.getenv("OPENROUTER_API_KEY", "")
   maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
   fs_storage = "../../environment/frontend_server/storage"
   collision_block_id = "32125"
   debug = True
   ```

4. **Install Dashboard** (optional):
   ```bash
   cd dashboard
   npm install
   ```

### Running Tests

```bash
# Test OpenRouter API integration
python test_openrouter.py
```

## Running Simulations

### Starting a New Simulation

**Terminal 1 - Environment Server**:
```bash
cd environment/frontend_server
python manage.py runserver
# Browser: http://localhost:8000/
```

**Terminal 2 - Simulation Server**:
```bash
cd reverie/backend_server  # IMPORTANT: Must run from this directory!
python reverie.py
# Enter fork simulation: base_the_ville_isabella_maria_klaus
# Enter new simulation name: my-test
```

**Terminal 3 - React Dashboard** (optional):
```bash
cd dashboard
npm run dev
# Browser: http://localhost:3000/
```

### Simulation Commands

Once both servers are running:

- `run <steps>`: Run simulation for N steps (e.g., `run 100`)
  - 1 step = 10 seconds game time
  - Monitor at: `http://localhost:8000/simulator_home`
- `exit`: Exit without saving
- `fin`: Save and exit

### Viewing Simulations

**Live View**:
```
http://localhost:8000/simulator_home
```

**Replay** (debugging, identical sprites):
```
http://localhost:8000/replay/<simulation-name>/<starting-step>/
```

**Demo** (proper sprites, requires compression):
```bash
cd reverie
python compress_sim_storage.py
# In the file, call: compress("simulation-name")
# Then: http://localhost:8000/demo/<simulation-name>/<starting-step>/<speed>
```

## LLM Configuration

### OpenRouter API

The system uses OpenRouter for LLM access, allowing use of various models.

**Configuration** (in `gpt_structure.py`):
```python
DEFAULT_MODEL = "xiaomi/mimo-v2-flash:free"  # Free tier model
# Or use paid models: "openai/gpt-4o-mini", "anthropic/claude-3-haiku", etc.
```

**API Details**:
- Base URL: `https://openrouter.ai/api/v1`
- Uses Chat Completions API format
- Free models may not support JSON schema - uses prompt-based extraction

### Local Embeddings

Uses sentence-transformers for embeddings instead of OpenAI:
- Model: `all-MiniLM-L6-v2`
- Dimension: 384 (vs 1536 for OpenAI ada-002)
- The system handles dimension mismatch automatically in `retrieve.py`

## React Dashboard

The dashboard provides real-time monitoring of the simulation.

### Features
- **Agent Panel**: Current activities and status
- **Event Log**: Simulation events in real-time
- **LLM Log**: All LLM requests and responses
- **Minimap**: Agent positions overlay

### WebSocket Connection
- Server: `ws://localhost:8765`
- Sends last 50 events on reconnect
- Event types: `sim.step`, `agent.moved`, `llm.request`, `llm.response`, etc.

### Event Bus Integration
Events are emitted via `event_bus.py` and broadcast to connected dashboards:
```python
from event_bus import emit_llm_request, emit_llm_response
emit_llm_request("function_name", prompt, model)
emit_llm_response("function_name", response, model)
```

## Key Terminology

| Paper Term | Code Term |
|------------|-----------|
| Generative Agent | Persona |
| Memory Stream | Associative Memory |
| Simulation Framework | Reverie |

## File Locations Reference

- **Simulation control**: `reverie/backend_server/reverie.py`
- **Agent logic**: `reverie/backend_server/persona/persona.py`
- **LLM wrappers**: `reverie/backend_server/persona/prompt_template/gpt_structure.py`
- **Embeddings**: `reverie/backend_server/persona/prompt_template/embeddings.py`
- **Prompt functions**: `reverie/backend_server/persona/prompt_template/run_gpt_prompt.py`
- **Event bus**: `reverie/backend_server/event_bus.py`
- **Django views**: `environment/frontend_server/translator/views.py`
- **React dashboard**: `dashboard/src/`

## Security Notes

- `.env` file contains API key - **gitignored, never commit**
- `reverie/backend_server/utils.py` - **gitignored, never commit**
- Never hardcode API keys in source files
- The `.env.example` file shows required variables without actual keys

## Common Issues

### Python Version
- **Use Python 3.11** - Python 3.13 has numpy/setuptools compatibility issues
- Create venv with: `python3.11 -m venv .venv`

### Directory Issues
- **Must run simulation from `reverie/backend_server/`** - relative paths in utils.py require this
- If you see "No such file or directory" errors, check your working directory

### Dependency Issues
If you encounter package conflicts:
```bash
pip install --upgrade pip
pip install numpy>=1.25.2,<2.0
pip install typing-extensions>=4.11.0
pip install Pillow>=9.1.0
```

### Tokenizer Warnings
Suppress parallelism warnings:
```bash
export TOKENIZERS_PARALLELISM=false
```

### WebSocket Port Conflicts
If port 8765 is in use:
```bash
lsof -ti :8765 | xargs kill -9
```

### Simulation Initialization
- First run takes time - generates daily schedules for all agents
- Step counter stays at 0 during initialization
- Once schedules are generated, steps begin incrementing

### Free Model Quirks
Free OpenRouter models may:
- Return verbose explanations instead of concise answers
- Include markdown formatting in responses
- The `gpt_structure.py` includes JSON extraction helpers to handle this
