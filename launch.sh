#!/bin/bash
# =============================================================================
# GENERATIVE AGENTS SIMULATION LAUNCHER
# =============================================================================
# Unified script to run the simulation with OpenRouter API and local embeddings
# Usage: ./launch.sh [steps]
#        ./launch.sh          # Run 100 steps (default)
#        ./launch.sh 50       # Run 50 steps
# =============================================================================

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
STEPS=${1:-100}
SIM_NAME="openrouter-run-$(date +%Y%m%d-%H%M%S)"
DJANGO_PORT=8000
DASHBOARD_PORT=3000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}=============================================="
echo -e "  GENERATIVE AGENTS SIMULATION LAUNCHER"
echo -e "==============================================${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"

    # Kill Django server if running
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null || true
        echo -e "${GREEN}  Django server stopped${NC}"
    fi

    # Kill dashboard if running
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null || true
        echo -e "${GREEN}  Dashboard stopped${NC}"
    fi

    echo -e "${GREEN}Done.${NC}"
}
trap cleanup EXIT

# Step 1: Create virtual environment
echo -e "${BLUE}[1/5] Setting up Python virtual environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    echo "      Creating new virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo -e "      ${GREEN}Created: $VENV_DIR${NC}"
else
    echo -e "      ${GREEN}Using existing: $VENV_DIR${NC}"
fi

# Step 2: Activate virtual environment
echo -e "${BLUE}[2/5] Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
echo -e "      ${GREEN}Python: $(which python)${NC}"

# Step 3: Install dependencies
echo -e "${BLUE}[3/5] Installing dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r "$PROJECT_ROOT/requirements.txt"
echo -e "      ${GREEN}Dependencies installed${NC}"

# Step 4: Start Django frontend server
echo -e "${BLUE}[4/5] Starting Django frontend server...${NC}"
cd "$PROJECT_ROOT/environment/frontend_server"

# Run migrations silently
python manage.py migrate --run-syncdb 2>/dev/null || true

# Start Django server in background
python manage.py runserver $DJANGO_PORT 2>&1 | sed 's/^/      [Django] /' &
DJANGO_PID=$!

echo -e "      ${GREEN}Django server started (PID: $DJANGO_PID)${NC}"
echo -e "      ${GREEN}Frontend: http://localhost:$DJANGO_PORT${NC}"

# Wait for Django to start
sleep 3

# Step 5: Run simulation
echo -e "${BLUE}[5/5] Starting simulation...${NC}"
echo ""
echo -e "${CYAN}=============================================="
echo -e "  SIMULATION CONFIGURATION"
echo -e "==============================================${NC}"
echo -e "  Fork from:    ${GREEN}base_the_ville_isabella_maria_klaus${NC}"
echo -e "  New sim:      ${GREEN}$SIM_NAME${NC}"
echo -e "  Steps:        ${GREEN}$STEPS${NC}"
echo -e "  Game time:    ${GREEN}$((STEPS * 10)) seconds = $((STEPS * 10 / 60)) minutes${NC}"
echo -e "  Model:        ${GREEN}xiaomi/mimo-v2-flash:free (OpenRouter)${NC}"
echo -e "  Embeddings:   ${GREEN}all-MiniLM-L6-v2 (Local)${NC}"
echo ""
echo -e "${CYAN}=============================================="
echo -e "  RUNNING SIMULATION"
echo -e "==============================================${NC}"
echo ""

cd "$PROJECT_ROOT"

python3 << EOF
import sys
import os
import time

# Setup paths
os.chdir('$PROJECT_ROOT/reverie/backend_server')
sys.path.insert(0, '$PROJECT_ROOT/reverie/backend_server')

from reverie import ReverieServer

# Initialize
print("Initializing simulation...")
sim = ReverieServer("base_the_ville_isabella_maria_klaus", "$SIM_NAME")

# Try to enable CLI mode if available
try:
    sim.enable_cli_mode()
    print("CLI mode enabled (WebSocket on port 8765)")
except Exception as e:
    print(f"CLI mode not available: {e}")

print()
print(f"Agents: {list(sim.personas.keys())}")
print(f"Start time: {sim.curr_time}")
print()

# Run simulation
start_time = time.time()
for step in range($STEPS):
    print(f"--- Step {step + 1}/$STEPS (Game time: {sim.curr_time}) ---")

    sim.start_server(1)

    # Show what agents are doing
    for persona_name, persona in sim.personas.items():
        action = getattr(persona.scratch, 'act_description', 'unknown')
        emoji = getattr(persona.scratch, 'act_pronunciatio', '')
        print(f"  {emoji} {persona_name}: {action[:60]}...")
    print()

elapsed = time.time() - start_time
print()
print("=" * 60)
print(f"SIMULATION COMPLETE!")
print("=" * 60)
print(f"Final game time: {sim.curr_time}")
print(f"Total steps: {sim.step}")
print(f"Real time elapsed: {elapsed:.1f} seconds")
print()
print("Saving simulation...")
sim.save()
print(f"Saved as: $SIM_NAME")
print()
print(f"View replay at: http://localhost:$DJANGO_PORT/replay/$SIM_NAME/1/")
print("=" * 60)
EOF

echo ""
echo -e "${GREEN}Simulation complete!${NC}"
echo ""
echo -e "Frontend running at: ${CYAN}http://localhost:$DJANGO_PORT${NC}"
echo -e "Replay at: ${CYAN}http://localhost:$DJANGO_PORT/replay/$SIM_NAME/1/${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services.${NC}"

# Keep script running to maintain Django server
wait $DJANGO_PID
