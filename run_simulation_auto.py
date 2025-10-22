#!/usr/bin/env python3
"""
Automated simulation runner - runs simulation for specified steps
"""
import sys
import os

# Change to backend directory first
os.chdir('/Users/bryanc/dev/econ_agents/reverie/backend_server')
sys.path.insert(0, '/Users/bryanc/dev/econ_agents/reverie/backend_server')

# Now import
import reverie
ReverieServer = reverie.ReverieServer

# Create simulation
print("=" * 70)
print("STARTING GENERATIVE AGENTS SIMULATION")
print("=" * 70)
print()
print("Forking from: base_the_ville_isabella_maria_klaus")
print("New simulation: auto-test-gpt5-nano")
print("Steps to run: 20 (= 200 seconds = 3.33 minutes game time)")
print()

# Initialize the simulation
sim = ReverieServer("base_the_ville_isabella_maria_klaus", "auto-test-gpt5-nano")

print("Simulation initialized!")
print(f"Start time: {sim.start_time}")
print(f"Current time: {sim.curr_time}")
print(f"Agents: {list(sim.personas.keys())}")
print()
print("=" * 70)
print("RUNNING SIMULATION - 20 STEPS")
print("=" * 70)
print()

# Run 20 steps
for step in range(20):
    print(f"\n--- Step {step + 1}/20 (Game time: {sim.curr_time}) ---")

    # Move one step
    sim.start_server(1)

    # Show what agents are doing
    for persona_name, persona in sim.personas.items():
        action = persona.scratch.act_description if hasattr(persona.scratch, 'act_description') else "unknown"
        location = persona.scratch.curr_tile if hasattr(persona.scratch, 'curr_tile') else "unknown"
        print(f"  {persona_name}: {action} at {location}")

print()
print("=" * 70)
print("SIMULATION COMPLETE!")
print("=" * 70)
print(f"Final game time: {sim.curr_time}")
print(f"Total steps: {sim.step}")
print()
print("Saving simulation...")
sim.save()
print("✓ Simulation saved as: auto-test-gpt5-nano")
print()
print("View replay at: http://localhost:8000/replay/auto-test-gpt5-nano/1/")
print("=" * 70)
