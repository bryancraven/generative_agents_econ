"""
Author: CLI UX Enhancement
File: ipc_server.py
Description: WebSocket server for IPC between Python simulation and TypeScript CLI.
Handles bi-directional communication for real-time monitoring and control.
"""

import asyncio
import json
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Set, Optional, Dict, Any
from threading import Thread
import traceback

from event_bus import get_event_bus, SimulationEvent, EventType


class IPCServer:
    """
    WebSocket server for communicating with CLI clients.
    Broadcasts simulation events and receives control commands.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.server = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[Thread] = None
        self.command_handler = None
        self._running = False

    def set_command_handler(self, handler):
        """
        Set the handler for incoming commands from CLI.

        Args:
            handler: Callable that takes (command: str, data: dict) and returns response dict
        """
        self.command_handler = handler

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new WebSocket client connection"""
        self.clients.add(websocket)
        client_id = id(websocket)
        print(f"[IPC] Client connected: {client_id}")

        try:
            # Send initial connection acknowledgment
            await websocket.send(json.dumps({
                'type': 'connection.established',
                'data': {
                    'client_id': client_id,
                    'message': 'Connected to simulation server'
                }
            }))

            # Send recent events to new client (catch-up)
            event_bus = get_event_bus()
            recent_events = event_bus.get_recent_events(count=50)
            if recent_events:
                await websocket.send(json.dumps({
                    'type': 'events.history',
                    'data': {
                        'events': [
                            {
                                'type': event.type.value,
                                'timestamp': event.timestamp,
                                'data': event.data
                            }
                            for event in recent_events
                        ]
                    }
                }))

            # Listen for commands from client
            async for message in websocket:
                try:
                    command_data = json.loads(message)
                    response = await self._handle_command(command_data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError as e:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'data': {'message': f'Invalid JSON: {str(e)}'}
                    }))
                except Exception as e:
                    print(f"[IPC] Error handling command: {e}")
                    traceback.print_exc()
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'data': {'message': f'Command error: {str(e)}'}
                    }))

        except websockets.exceptions.ConnectionClosed:
            print(f"[IPC] Client disconnected: {client_id}")
        finally:
            self.clients.remove(websocket)

    async def _handle_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a command from the CLI client.

        Args:
            command_data: Dictionary with 'cmd' and optional 'data' keys

        Returns:
            Response dictionary
        """
        cmd = command_data.get('cmd')
        data = command_data.get('data', {})

        if not cmd:
            return {
                'type': 'error',
                'data': {'message': 'Missing "cmd" field'}
            }

        print(f"[IPC] Received command: {cmd}")

        # Call the command handler if set
        if self.command_handler:
            try:
                result = self.command_handler(cmd, data)
                return {
                    'type': 'command.response',
                    'cmd': cmd,
                    'data': result
                }
            except Exception as e:
                return {
                    'type': 'error',
                    'cmd': cmd,
                    'data': {'message': str(e)}
                }
        else:
            return {
                'type': 'error',
                'data': {'message': 'No command handler registered'}
            }

    async def _broadcast_event(self, event: SimulationEvent):
        """
        Broadcast an event to all connected clients.

        Args:
            event: SimulationEvent to broadcast
        """
        if not self.clients:
            return

        message = json.dumps({
            'type': event.type.value,
            'timestamp': event.timestamp,
            'data': event.data
        })

        # Send to all connected clients
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                print(f"[IPC] Error broadcasting to client: {e}")
                disconnected_clients.add(client)

        # Remove disconnected clients
        self.clients -= disconnected_clients

    def _event_handler(self, event: SimulationEvent):
        """
        Handle events from the event bus (synchronous callback).
        Schedules async broadcast on the event loop.
        """
        if self.loop and self._running:
            asyncio.run_coroutine_threadsafe(
                self._broadcast_event(event),
                self.loop
            )

    async def _start_server(self):
        """Start the WebSocket server (async)"""
        self.loop = asyncio.get_event_loop()

        # Register event handler
        event_bus = get_event_bus()
        event_bus.on(None, self._event_handler)  # Listen to all events

        # Start WebSocket server
        self.server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port
        )

        self._running = True
        print(f"[IPC] WebSocket server started on ws://{self.host}:{self.port}")

        # Keep server running
        await asyncio.Future()  # Run forever

    def _run_server_thread(self):
        """Run the WebSocket server in a separate thread"""
        asyncio.run(self._start_server())

    def start(self):
        """
        Start the IPC server in a background thread.
        Non-blocking - returns immediately.
        """
        if self._running:
            print("[IPC] Server already running")
            return

        self.thread = Thread(target=self._run_server_thread, daemon=True)
        self.thread.start()

        # Wait a moment for server to start
        import time
        time.sleep(0.5)

    def stop(self):
        """Stop the IPC server"""
        if not self._running:
            return

        print("[IPC] Stopping server...")
        self._running = False

        # Unregister event handler
        event_bus = get_event_bus()
        event_bus.off(None, self._event_handler)

        # Close all client connections
        if self.loop:
            for client in self.clients:
                asyncio.run_coroutine_threadsafe(client.close(), self.loop)

        # Stop the server
        if self.server:
            self.server.close()

        print("[IPC] Server stopped")

    def is_running(self) -> bool:
        """Check if the server is running"""
        return self._running

    def broadcast_message(self, message_type: str, data: Dict[str, Any]):
        """
        Manually broadcast a custom message to all clients.

        Args:
            message_type: Type of message
            data: Message data
        """
        if not self.loop or not self._running:
            return

        message = json.dumps({
            'type': message_type,
            'data': data
        })

        async def _send():
            disconnected_clients = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except Exception:
                    disconnected_clients.add(client)
            self.clients -= disconnected_clients

        asyncio.run_coroutine_threadsafe(_send(), self.loop)


# Global IPC server instance
_global_ipc_server: Optional[IPCServer] = None


def get_ipc_server(host: str = "localhost", port: int = 8765) -> IPCServer:
    """Get or create the global IPC server instance"""
    global _global_ipc_server
    if _global_ipc_server is None:
        _global_ipc_server = IPCServer(host, port)
    return _global_ipc_server


def start_ipc_server(command_handler=None, host: str = "localhost", port: int = 8765):
    """
    Convenience function to start the IPC server.

    Args:
        command_handler: Handler for CLI commands
        host: Server host
        port: Server port
    """
    server = get_ipc_server(host, port)
    if command_handler:
        server.set_command_handler(command_handler)
    server.start()
    return server


# Example command handler
def example_command_handler(cmd: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example command handler implementation.
    Replace this with actual simulation control logic.
    """
    if cmd == "run":
        steps = data.get('steps', 1)
        return {'success': True, 'message': f'Running {steps} steps'}

    elif cmd == "pause":
        return {'success': True, 'message': 'Simulation paused'}

    elif cmd == "resume":
        return {'success': True, 'message': 'Simulation resumed'}

    elif cmd == "step":
        return {'success': True, 'message': 'Stepped forward 1 step'}

    elif cmd == "save":
        return {'success': True, 'message': 'Simulation saved'}

    elif cmd == "get_agent_state":
        agent_name = data.get('agent_name')
        return {
            'success': True,
            'agent': agent_name,
            'state': {
                'location': [58, 39],
                'action': 'painting',
                'emotion': 'focused'
            }
        }

    elif cmd == "get_agent_memory":
        agent_name = data.get('agent_name')
        memory_type = data.get('memory_type', 'event')
        return {
            'success': True,
            'agent': agent_name,
            'memory_type': memory_type,
            'memories': [
                {'description': 'Example memory 1', 'timestamp': '14:00:00'},
                {'description': 'Example memory 2', 'timestamp': '14:15:00'}
            ]
        }

    else:
        return {'success': False, 'message': f'Unknown command: {cmd}'}


if __name__ == "__main__":
    """Test the IPC server"""
    print("Starting test IPC server...")

    # Enable event bus
    event_bus = get_event_bus()
    event_bus.enable()

    # Start server with example handler
    server = start_ipc_server(command_handler=example_command_handler)

    print("Server running. Press Ctrl+C to stop.")
    print("Connect with: wscat -c ws://localhost:8765")

    try:
        # Simulate some events
        import time
        from event_bus import emit_sim_started, emit_sim_step, emit_agent_moved

        time.sleep(1)
        emit_sim_started("test-sim", 0, "June 25, 2022, 00:00:00", ["Isabella Rodriguez"])

        for i in range(10):
            time.sleep(2)
            emit_sim_step(i, f"June 25, 2022, {i}:00:00")
            emit_agent_moved("Isabella Rodriguez", (58, 39), (58, 40), "🚶", "walking")

    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()
