"""
Author: CLI UX Enhancement
File: event_bus.py
Description: Event emission system for broadcasting simulation events to CLI clients.
Provides a centralized event bus for real-time monitoring and control.
"""

import json
import asyncio
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Simulation event types"""
    # Simulation lifecycle
    SIM_STARTED = "sim.started"
    SIM_STEP = "sim.step"
    SIM_PAUSED = "sim.paused"
    SIM_RESUMED = "sim.resumed"
    SIM_SAVED = "sim.saved"
    SIM_STOPPED = "sim.stopped"

    # Agent cognitive events
    AGENT_PERCEIVED = "agent.perceived"
    AGENT_RETRIEVED = "agent.retrieved"
    AGENT_PLANNED = "agent.planned"
    AGENT_REFLECTED = "agent.reflected"
    AGENT_EXECUTED = "agent.executed"
    AGENT_MOVED = "agent.moved"

    # Agent social events
    AGENT_CHAT_STARTED = "agent.chat_started"
    AGENT_CHAT_MESSAGE = "agent.chat_message"
    AGENT_CHAT_ENDED = "agent.chat_ended"

    # Agent state
    AGENT_STATE_CHANGED = "agent.state_changed"


@dataclass
class SimulationEvent:
    """Base class for all simulation events"""
    type: EventType
    timestamp: str
    data: Dict[str, Any]

    def to_json(self) -> str:
        """Serialize event to JSON string"""
        return json.dumps({
            'type': self.type.value,
            'timestamp': self.timestamp,
            'data': self.data
        })

    @classmethod
    def create(cls, event_type: EventType, data: Dict[str, Any]) -> 'SimulationEvent':
        """Factory method to create events with current timestamp"""
        return cls(
            type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data
        )


class EventBus:
    """
    Central event bus for simulation events.
    Supports both synchronous and asynchronous event handlers.
    """

    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._async_listeners: Dict[EventType, List[Callable]] = {}
        self._wildcard_listeners: List[Callable] = []
        self._async_wildcard_listeners: List[Callable] = []
        self._enabled = True
        self._event_queue: List[SimulationEvent] = []

    def enable(self):
        """Enable event emission"""
        self._enabled = True

    def disable(self):
        """Disable event emission (for performance in legacy mode)"""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if event bus is enabled"""
        return self._enabled

    def on(self, event_type: Optional[EventType], handler: Callable):
        """
        Register a synchronous event handler.
        If event_type is None, handler receives all events.

        Args:
            event_type: Type of event to listen for, or None for all events
            handler: Callable that takes (event: SimulationEvent) as argument
        """
        if event_type is None:
            self._wildcard_listeners.append(handler)
        else:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(handler)

    def on_async(self, event_type: Optional[EventType], handler: Callable):
        """
        Register an asynchronous event handler.
        If event_type is None, handler receives all events.

        Args:
            event_type: Type of event to listen for, or None for all events
            handler: Async callable that takes (event: SimulationEvent) as argument
        """
        if event_type is None:
            self._async_wildcard_listeners.append(handler)
        else:
            if event_type not in self._async_listeners:
                self._async_listeners[event_type] = []
            self._async_listeners[event_type].append(handler)

    def off(self, event_type: Optional[EventType], handler: Callable):
        """
        Unregister an event handler.

        Args:
            event_type: Type of event to stop listening for
            handler: Handler to remove
        """
        if event_type is None:
            if handler in self._wildcard_listeners:
                self._wildcard_listeners.remove(handler)
            if handler in self._async_wildcard_listeners:
                self._async_wildcard_listeners.remove(handler)
        else:
            if event_type in self._listeners and handler in self._listeners[event_type]:
                self._listeners[event_type].remove(handler)
            if event_type in self._async_listeners and handler in self._async_listeners[event_type]:
                self._async_listeners[event_type].remove(handler)

    def emit(self, event_type: EventType, data: Dict[str, Any]):
        """
        Emit an event to all registered handlers.

        Args:
            event_type: Type of event to emit
            data: Event data dictionary
        """
        if not self._enabled:
            return

        event = SimulationEvent.create(event_type, data)
        self._event_queue.append(event)

        # Call synchronous handlers
        handlers = self._listeners.get(event_type, []) + self._wildcard_listeners
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")

        # Schedule async handlers if event loop exists
        async_handlers = self._async_listeners.get(event_type, []) + self._async_wildcard_listeners
        if async_handlers:
            try:
                loop = asyncio.get_event_loop()
                for handler in async_handlers:
                    asyncio.create_task(handler(event))
            except RuntimeError:
                # No event loop running, skip async handlers
                pass

    def get_recent_events(self, count: int = 100) -> List[SimulationEvent]:
        """
        Get the most recent events from the queue.

        Args:
            count: Maximum number of events to return

        Returns:
            List of recent events (newest first)
        """
        return list(reversed(self._event_queue[-count:]))

    def clear_events(self):
        """Clear the event queue"""
        self._event_queue.clear()

    def remove_all_listeners(self):
        """Remove all registered event handlers"""
        self._listeners.clear()
        self._async_listeners.clear()
        self._wildcard_listeners.clear()
        self._async_wildcard_listeners.clear()


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus instance"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def emit_event(event_type: EventType, data: Dict[str, Any]):
    """Convenience function to emit events to the global event bus"""
    get_event_bus().emit(event_type, data)


# Convenience functions for common events
def emit_sim_started(sim_code: str, step: int, curr_time: str, personas: List[str]):
    """Emit simulation started event"""
    emit_event(EventType.SIM_STARTED, {
        'sim_code': sim_code,
        'step': step,
        'curr_time': curr_time,
        'personas': personas
    })


def emit_sim_step(step: int, curr_time: str):
    """Emit simulation step event"""
    emit_event(EventType.SIM_STEP, {
        'step': step,
        'curr_time': curr_time
    })


def emit_sim_paused(step: int):
    """Emit simulation paused event"""
    emit_event(EventType.SIM_PAUSED, {'step': step})


def emit_sim_resumed(step: int):
    """Emit simulation resumed event"""
    emit_event(EventType.SIM_RESUMED, {'step': step})


def emit_agent_perceived(agent_name: str, perceived_nodes: List[Any]):
    """Emit agent perception event"""
    # Convert ConceptNode objects to dicts
    perceived_data = []
    for node in perceived_nodes:
        perceived_data.append({
            'type': node.type if hasattr(node, 'type') else 'unknown',
            'description': node.description if hasattr(node, 'description') else str(node),
            'subject': node.subject if hasattr(node, 'subject') else '',
            'predicate': node.predicate if hasattr(node, 'predicate') else '',
            'object': node.object if hasattr(node, 'object') else ''
        })

    emit_event(EventType.AGENT_PERCEIVED, {
        'agent': agent_name,
        'perceived': perceived_data,
        'count': len(perceived_nodes)
    })


def emit_agent_retrieved(agent_name: str, retrieved_count: int, focal_points: List[str]):
    """Emit agent memory retrieval event"""
    emit_event(EventType.AGENT_RETRIEVED, {
        'agent': agent_name,
        'retrieved_count': retrieved_count,
        'focal_points': focal_points[:5]  # First 5 focal points
    })


def emit_agent_planned(agent_name: str, action_address: str, action_desc: str, duration: int):
    """Emit agent planning event"""
    emit_event(EventType.AGENT_PLANNED, {
        'agent': agent_name,
        'action_address': action_address,
        'action_description': action_desc,
        'duration_minutes': duration
    })


def emit_agent_reflected(agent_name: str, thought: str, keywords: List[str]):
    """Emit agent reflection event"""
    emit_event(EventType.AGENT_REFLECTED, {
        'agent': agent_name,
        'thought': thought,
        'keywords': keywords
    })


def emit_agent_moved(agent_name: str, from_tile: tuple, to_tile: tuple,
                     pronunciatio: str, description: str):
    """Emit agent movement event"""
    emit_event(EventType.AGENT_MOVED, {
        'agent': agent_name,
        'from_tile': list(from_tile) if from_tile else None,
        'to_tile': list(to_tile),
        'emoji': pronunciatio,
        'description': description
    })


def emit_agent_chat_started(agent1: str, agent2: str, location: str):
    """Emit agent chat started event"""
    emit_event(EventType.AGENT_CHAT_STARTED, {
        'agent1': agent1,
        'agent2': agent2,
        'location': location
    })


def emit_agent_chat_message(agent: str, message: str, other_agent: str):
    """Emit agent chat message event"""
    emit_event(EventType.AGENT_CHAT_MESSAGE, {
        'agent': agent,
        'message': message,
        'other_agent': other_agent
    })


def emit_agent_chat_ended(agent1: str, agent2: str):
    """Emit agent chat ended event"""
    emit_event(EventType.AGENT_CHAT_ENDED, {
        'agent1': agent1,
        'agent2': agent2
    })
