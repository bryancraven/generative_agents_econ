"""
Author: CLI UX Enhancement
File: cli_mode.py
Description: Execution control for CLI mode (pause/resume/step).
Provides fine-grained control over simulation execution.
"""

import threading
from enum import Enum
from typing import Optional


class ExecutionMode(str, Enum):
    """Simulation execution modes"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"  # Single-step mode


class ExecutionController:
    """
    Controls simulation execution for CLI mode.
    Supports pause, resume, and step-by-step execution.
    """

    def __init__(self):
        self._mode = ExecutionMode.STOPPED
        self._lock = threading.Lock()
        self._step_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Start unpaused
        self._step_count = 0
        self._total_steps_to_run = 0
        self._manual_step_requested = False

    @property
    def mode(self) -> ExecutionMode:
        """Get current execution mode"""
        with self._lock:
            return self._mode

    @property
    def is_running(self) -> bool:
        """Check if simulation is running"""
        return self.mode == ExecutionMode.RUNNING

    @property
    def is_paused(self) -> bool:
        """Check if simulation is paused"""
        return self.mode == ExecutionMode.PAUSED

    @property
    def is_stopped(self) -> bool:
        """Check if simulation is stopped"""
        return self.mode == ExecutionMode.STOPPED

    @property
    def is_stepping(self) -> bool:
        """Check if simulation is in step mode"""
        return self.mode == ExecutionMode.STEPPING

    def start_running(self, step_count: int):
        """
        Start running the simulation.

        Args:
            step_count: Number of steps to run
        """
        with self._lock:
            self._mode = ExecutionMode.RUNNING
            self._total_steps_to_run = step_count
            self._step_count = 0
            self._pause_event.set()  # Ensure not paused
            self._manual_step_requested = False

    def pause(self):
        """Pause the simulation"""
        with self._lock:
            if self._mode == ExecutionMode.RUNNING:
                self._mode = ExecutionMode.PAUSED
                self._pause_event.clear()
                return True
            return False

    def resume(self):
        """Resume the simulation"""
        with self._lock:
            if self._mode == ExecutionMode.PAUSED:
                self._mode = ExecutionMode.RUNNING
                self._pause_event.set()
                return True
            return False

    def step(self):
        """
        Execute a single step.
        If paused, will execute one step and return to paused state.
        """
        with self._lock:
            if self._mode in [ExecutionMode.PAUSED, ExecutionMode.STOPPED]:
                self._mode = ExecutionMode.STEPPING
                self._manual_step_requested = True
                self._step_event.set()
                return True
            return False

    def stop(self):
        """Stop the simulation"""
        with self._lock:
            self._mode = ExecutionMode.STOPPED
            self._pause_event.set()  # Unblock any waiting threads
            self._step_event.set()

    def wait_if_paused(self):
        """
        Block if simulation is paused.
        Call this at the start of each simulation step.
        """
        # Check if we should pause
        mode = self.mode

        if mode == ExecutionMode.PAUSED:
            # Wait until resumed or step requested
            self._pause_event.wait()

        elif mode == ExecutionMode.STEPPING:
            # If in stepping mode, complete the step and go back to paused
            with self._lock:
                if self._manual_step_requested:
                    self._manual_step_requested = False
                    # Allow this step to execute
                    self._mode = ExecutionMode.PAUSED
                    self._step_event.clear()
                else:
                    # Already executed the step, wait for next step command
                    self._mode = ExecutionMode.PAUSED
                    self._pause_event.clear()
                    return self.wait_if_paused()

    def should_continue(self) -> bool:
        """
        Check if simulation should continue running.

        Returns:
            True if should continue, False if should stop
        """
        with self._lock:
            if self._mode == ExecutionMode.STOPPED:
                return False

            # Check if we've reached the target step count
            if self._mode == ExecutionMode.RUNNING:
                if self._total_steps_to_run > 0 and self._step_count >= self._total_steps_to_run:
                    self._mode = ExecutionMode.PAUSED
                    return False

            return True

    def increment_step(self):
        """Increment the step counter"""
        with self._lock:
            self._step_count += 1

    def get_progress(self) -> tuple:
        """
        Get execution progress.

        Returns:
            Tuple of (current_step, total_steps)
        """
        with self._lock:
            return (self._step_count, self._total_steps_to_run)

    def reset(self):
        """Reset the controller"""
        with self._lock:
            self._mode = ExecutionMode.STOPPED
            self._step_count = 0
            self._total_steps_to_run = 0
            self._manual_step_requested = False
            self._pause_event.set()
            self._step_event.clear()


# Global execution controller instance
_global_controller: Optional[ExecutionController] = None


def get_execution_controller() -> ExecutionController:
    """Get or create the global execution controller"""
    global _global_controller
    if _global_controller is None:
        _global_controller = ExecutionController()
    return _global_controller


if __name__ == "__main__":
    """Test the execution controller"""
    import time

    controller = get_execution_controller()

    print("Testing execution controller...")

    # Test running
    print("\n1. Starting run of 5 steps")
    controller.start_running(5)
    for i in range(5):
        controller.wait_if_paused()
        print(f"  Step {i+1}")
        controller.increment_step()
        time.sleep(0.5)
        if not controller.should_continue():
            break
    print(f"  Progress: {controller.get_progress()}")

    # Test pause/resume
    print("\n2. Testing pause/resume")
    controller.start_running(10)

    def run_simulation():
        step = 0
        while controller.should_continue() and step < 10:
            controller.wait_if_paused()
            step += 1
            print(f"  Step {step}")
            controller.increment_step()
            time.sleep(0.3)

    # Run in thread
    sim_thread = threading.Thread(target=run_simulation)
    sim_thread.start()

    time.sleep(1)
    print("  Pausing...")
    controller.pause()
    time.sleep(1)
    print("  Resuming...")
    controller.resume()

    sim_thread.join()
    print(f"  Progress: {controller.get_progress()}")

    # Test single step
    print("\n3. Testing single step")
    controller.reset()

    def step_simulation():
        for _ in range(3):
            controller.wait_if_paused()
            step = controller.get_progress()[0] + 1
            print(f"  Executed step {step}")
            controller.increment_step()

    step_thread = threading.Thread(target=step_simulation)
    step_thread.start()

    time.sleep(0.5)
    print("  Requesting step 1...")
    controller.step()
    time.sleep(0.5)
    print("  Requesting step 2...")
    controller.step()
    time.sleep(0.5)
    print("  Requesting step 3...")
    controller.step()

    step_thread.join()
    print(f"  Progress: {controller.get_progress()}")

    print("\nAll tests completed!")
