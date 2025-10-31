# Reverie CLI - Sophisticated UX for Generative Agents

A modern, interactive CLI interface for the Reverie generative agents simulation, built with TypeScript, React (Ink), and Bun.

## Features

✨ **Real-time monitoring** - Watch agent thoughts, actions, and movements as they happen
🎯 **Interactive controls** - Pause, resume, step through simulation with keyboard shortcuts
👥 **Agent focus** - Cycle through agents and view detailed cognitive streams
⚡ **High performance** - Built with Bun for speed, Ink for responsive UI
🎨 **Rich visualization** - Color-coded events, emojis, status indicators

## Prerequisites

- **Bun** (JavaScript runtime) - [Install Bun](https://bun.sh)
  ```bash
  curl -fsSL https://bun.sh/install | bash
  ```

- **Python 3.8+** with the simulation backend running

## Installation

1. **Install dependencies**:
   ```bash
   cd cli
   bun install
   ```

2. **Verify installation**:
   ```bash
   bun run src/index.tsx
   ```

## Usage

### Starting the CLI

**Option 1: Direct run** (recommended for development):
```bash
cd cli
bun run src/index.tsx
```

**Option 2: Using launcher script**:
```bash
cd cli
./bin/reverie-cli.js
```

**Option 3: Install globally** (optional):
```bash
cd cli
bun link
# Then from anywhere:
reverie-cli
```

### Starting the Simulation with CLI Mode

The CLI requires the Python simulation server to be running with CLI mode enabled:

**Terminal 1 - Environment Server** (Django):
```bash
cd environment/frontend_server
python manage.py runserver
```

**Terminal 2 - Simulation Server** (with CLI mode):
```python
cd reverie/backend_server
python
>>> from reverie import ReverieServer
>>> rs = ReverieServer("base_the_ville_isabella_maria_klaus", "test-simulation")
>>> rs.enable_cli_mode()  # ← Enable CLI mode!
>>> rs.start_server(1000)  # Or use open_server() for interactive
```

**Terminal 3 - CLI Interface**:
```bash
cd cli
bun run src/index.tsx
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Space** | Pause/Resume simulation |
| **→** (Right Arrow) | Step forward (when paused) |
| **R** | Run 10 steps |
| **S** | Save simulation |
| **Tab** | Cycle to next agent |
| **Shift+Tab** | Cycle to previous agent |
| **Q** | Quit (press twice to confirm) |
| **Ctrl+C** | Force quit |

## UI Layout

```
┌─ Reverie Simulation ──────────────────────────────────────────┐
│ 🕐 June 25, 2022 14:30:00 │ Step 145 │ ▶ RUNNING │ 3 agents  │
├────────────┬──────────────────────────────────────────────────┤
│ AGENTS     │ ISABELLA RODRIGUEZ                               │
│            │ 📍 (58, 39)                                       │
│ ◉ Isabella │ 🎨 painting @ painting easel                     │
│ ○ Maria    │                                                   │
│ ○ Klaus    │ ┌─ Cognitive Stream ──────────────────────────┐ │
│            │ │ 2s ago 💭 REFLECT: "sunset colors..."       │ │
│            │ │ 5s ago 🎯 PLAN: Continue painting           │ │
│            │ │ 10s ago 📖 RETRIEVE: 3 memories             │ │
│            │ │ 15s ago 👁️ PERCEIVE: Maria walking by       │ │
│            │ └─────────────────────────────────────────────┘ │
├────────────┴──────────────────────────────────────────────────┤
│ [Space] Pause [→] Step [R] Run 10 [S] Save [Tab] Switch [Q] │
└───────────────────────────────────────────────────────────────┘
```

## Event Types & Icons

| Icon | Type | Description |
|------|------|-------------|
| 👁️ | **PERCEIVE** | Agent observes nearby events |
| 📖 | **RETRIEVE** | Agent recalls relevant memories |
| 🎯 | **PLAN** | Agent decides on action |
| 💭 | **REFLECT** | Agent generates insights |
| 🚶 | **MOVE** | Agent moves to new location |
| 💬 | **CHAT** | Agent converses with another agent |

## Architecture

### Component Structure

```
cli/
├── src/
│   ├── index.tsx              # Entry point
│   ├── App.tsx                # Main app component
│   ├── components/
│   │   ├── SimulationHeader.tsx   # Status bar
│   │   ├── AgentList.tsx          # Agent sidebar
│   │   ├── AgentDetail.tsx        # Selected agent info
│   │   ├── ThoughtStream.tsx      # Cognitive events
│   │   └── Controls.tsx           # Keyboard shortcuts bar
│   ├── hooks/
│   │   ├── useSimulation.ts       # WebSocket connection
│   │   └── useKeyboard.ts         # Keyboard input handling
│   └── types/
│       └── simulation.ts          # TypeScript types
└── bin/
    └── reverie-cli.js         # Executable launcher
```

### Communication Flow

```
Python Backend (port 8765)
    ↕ WebSocket (JSON events)
TypeScript CLI (Ink/React)
```

**Events sent from Python → CLI**:
- `sim.started`, `sim.step`, `sim.paused`, `sim.resumed`
- `agent.perceived`, `agent.retrieved`, `agent.planned`, `agent.reflected`, `agent.moved`
- `agent.chat_started`, `agent.chat_message`

**Commands sent from CLI → Python**:
- `run(steps)`, `pause`, `resume`, `step`, `save`
- `get_agent_state(name)`, `get_agent_memory(name, type)`

## Development

### Watch mode (auto-reload on changes):
```bash
bun --watch src/index.tsx
```

### Type checking:
```bash
bun run type-check
```

### Building:
```bash
bun run build
```

## Troubleshooting

### "Error: WebSocket not connected"
- Ensure Python simulation is running with `rs.enable_cli_mode()`
- Check that port 8765 is not in use
- Verify websockets package is installed: `pip install websockets==12.0`

### "Bun runtime not found"
- Install Bun: `curl -fsSL https://bun.sh/install | bash`
- Add to PATH: `export PATH="$HOME/.bun/bin:$PATH"`

### UI not updating
- Check Python console for event bus errors
- Verify WebSocket connection in CLI (should show "Connected")
- Try restarting both Python server and CLI

### Agent names truncated
- Adjust terminal width (recommended: 120+ columns)
- Or use shorter simulation names

## macOS-Specific Notes

- **Terminal.app**: Works well, supports colors
- **iTerm2**: Recommended, best Unicode support
- **Warp**: Also supported
- **Font recommendation**: SF Mono, Menlo, or FiraCode

Ensure terminal is at least 100 columns wide for best experience.

## Comparison with Legacy CLI

| Feature | Legacy CLI | New CLI |
|---------|-----------|---------|
| Interface | Text prompts | Rich TUI |
| Monitoring | Manual commands | Real-time |
| Control | Type commands | Keyboard shortcuts |
| Agent view | Print commands | Live panels |
| Cognitive events | Hidden | Visible stream |
| Performance | Blocking | Non-blocking |

## Advanced Usage

### Custom event handling

Modify `useSimulation.ts` `handleEvent()` to customize event processing.

### Adding new commands

1. Add command to `sendCommand()` in `useSimulation.ts`
2. Handle in Python's `_handle_cli_command()` in `reverie.py`
3. Wire up keyboard shortcut in `useKeyboard.ts`

### Styling

Components use Ink's `<Box>` and `<Text>` with:
- Border styles: `round`, `single`, `double`
- Colors: Chalk color names (cyan, green, yellow, etc.)
- Layout: Flexbox (same as CSS)

## License

Same as parent Reverie project.

## Credits

Built with:
- [Ink](https://github.com/vadimdemedes/ink) - React for CLIs
- [Bun](https://bun.sh) - Fast JavaScript runtime
- [ws](https://github.com/websockets/ws) - WebSocket client
- [date-fns](https://date-fns.org) - Date formatting
