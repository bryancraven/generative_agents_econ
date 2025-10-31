/**
 * Custom hook for managing simulation WebSocket connection and state
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import WebSocket from 'ws';
import type {
  SimulationEvent,
  AgentState,
  CognitiveEvent,
  SimulationStatus,
  CommandResponse,
  ExecutionMode,
} from '../types/simulation';

const WS_URL = 'ws://localhost:8765';
const RECONNECT_DELAY = 2000;
const MAX_COGNITIVE_EVENTS = 100;

export function useSimulation() {
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState<SimulationStatus | null>(null);
  const [agents, setAgents] = useState<Map<string, AgentState>>(new Map());
  const [cognitiveStream, setCognitiveStream] = useState<CognitiveEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  // Send command to simulation server
  const sendCommand = useCallback(
    async (cmd: string, data: Record<string, any> = {}): Promise<CommandResponse> => {
      return new Promise((resolve, reject) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          reject(new Error('WebSocket not connected'));
          return;
        }

        const message = JSON.stringify({ cmd, data });

        // Set up one-time response handler
        const responseHandler = (event: WebSocket.MessageEvent) => {
          try {
            const response = JSON.parse(event.data.toString());
            if (response.type === 'command.response' && response.cmd === cmd) {
              wsRef.current?.removeEventListener('message', responseHandler);
              resolve({
                success: response.data.success ?? true,
                message: response.data.message,
                data: response.data,
              });
            } else if (response.type === 'error' && response.cmd === cmd) {
              wsRef.current?.removeEventListener('message', responseHandler);
              resolve({
                success: false,
                message: response.data.message,
              });
            }
          } catch (err) {
            wsRef.current?.removeEventListener('message', responseHandler);
            reject(err);
          }
        };

        wsRef.current.addEventListener('message', responseHandler);
        wsRef.current.send(message);

        // Timeout after 5 seconds
        setTimeout(() => {
          wsRef.current?.removeEventListener('message', responseHandler);
          reject(new Error('Command timeout'));
        }, 5000);
      });
    },
    []
  );

  // Handle incoming simulation events
  const handleEvent = useCallback((event: SimulationEvent) => {
    switch (event.type) {
      case 'sim.started':
        setStatus({
          simCode: event.data.sim_code,
          step: event.data.step,
          currTime: event.data.curr_time,
          mode: 'running' as ExecutionMode,
          personas: event.data.personas,
          personasCount: event.data.personas.length,
        });
        break;

      case 'sim.step':
        setStatus((prev) =>
          prev ? { ...prev, step: event.data.step, currTime: event.data.curr_time } : null
        );
        break;

      case 'sim.paused':
        setStatus((prev) => (prev ? { ...prev, mode: 'paused' } : null));
        break;

      case 'sim.resumed':
        setStatus((prev) => (prev ? { ...prev, mode: 'running' } : null));
        break;

      case 'agent.perceived':
        setCognitiveStream((prev) => [
          {
            timestamp: event.timestamp,
            type: 'perceive',
            agent: event.data.agent,
            data: event.data.perceived,
            icon: '👁️',
            description: `Perceived ${event.data.count} ${event.data.count === 1 ? 'event' : 'events'}`,
          },
          ...prev.slice(0, MAX_COGNITIVE_EVENTS - 1),
        ]);
        break;

      case 'agent.retrieved':
        setCognitiveStream((prev) => [
          {
            timestamp: event.timestamp,
            type: 'retrieve',
            agent: event.data.agent,
            data: event.data.focal_points,
            icon: '📖',
            description: `Retrieved ${event.data.retrieved_count} memories`,
          },
          ...prev.slice(0, MAX_COGNITIVE_EVENTS - 1),
        ]);
        break;

      case 'agent.planned':
        setCognitiveStream((prev) => [
          {
            timestamp: event.timestamp,
            type: 'plan',
            agent: event.data.agent,
            data: event.data,
            icon: '🎯',
            description: event.data.action_description || event.data.action_address,
          },
          ...prev.slice(0, MAX_COGNITIVE_EVENTS - 1),
        ]);
        break;

      case 'agent.reflected':
        setCognitiveStream((prev) => [
          {
            timestamp: event.timestamp,
            type: 'reflect',
            agent: event.data.agent,
            data: event.data,
            icon: '💭',
            description: event.data.thought,
          },
          ...prev.slice(0, MAX_COGNITIVE_EVENTS - 1),
        ]);
        break;

      case 'agent.moved':
        // Update agent state
        setAgents((prev) => {
          const updated = new Map(prev);
          const agent = updated.get(event.data.agent);
          updated.set(event.data.agent, {
            name: event.data.agent,
            location: event.data.to_tile,
            action: event.data.description,
            actionAddress: '',
            emoji: event.data.emoji,
            description: event.data.description,
            ...(agent || {}),
          });
          return updated;
        });

        // Add to cognitive stream
        setCognitiveStream((prev) => [
          {
            timestamp: event.timestamp,
            type: 'move',
            agent: event.data.agent,
            data: event.data,
            icon: event.data.emoji || '🚶',
            description: event.data.description,
          },
          ...prev.slice(0, MAX_COGNITIVE_EVENTS - 1),
        ]);
        break;

      case 'agent.chat_started':
        setCognitiveStream((prev) => [
          {
            timestamp: event.timestamp,
            type: 'chat',
            agent: event.data.agent1,
            data: event.data,
            icon: '💬',
            description: `Started conversation with ${event.data.agent2}`,
          },
          ...prev.slice(0, MAX_COGNITIVE_EVENTS - 1),
        ]);
        break;
    }
  }, []);

  // WebSocket connection management
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(WS_URL);

      ws.on('open', () => {
        setConnected(true);
        setError(null);
        console.log('[CLI] Connected to simulation server');
      });

      ws.on('message', (data: Buffer) => {
        try {
          const message = JSON.parse(data.toString());

          if (message.type === 'connection.established') {
            console.log('[CLI] Connection established');
          } else if (message.type === 'events.history') {
            // Process historical events
            message.data.events.forEach((event: SimulationEvent) => {
              handleEvent(event);
            });
          } else {
            // Regular event
            handleEvent(message as SimulationEvent);
          }
        } catch (err) {
          console.error('[CLI] Error parsing message:', err);
        }
      });

      ws.on('close', () => {
        setConnected(false);
        console.log('[CLI] Disconnected from server');

        // Attempt reconnect
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('[CLI] Attempting to reconnect...');
          connect();
        }, RECONNECT_DELAY);
      });

      ws.on('error', (err) => {
        setError(err.message);
        console.error('[CLI] WebSocket error:', err);
      });

      wsRef.current = ws;
    } catch (err: any) {
      setError(err.message);
      console.error('[CLI] Connection error:', err);
    }
  }, [handleEvent]);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  // Command shortcuts
  const run = useCallback((steps: number = 1) => sendCommand('run', { steps }), [sendCommand]);
  const pause = useCallback(() => sendCommand('pause'), [sendCommand]);
  const resume = useCallback(() => sendCommand('resume'), [sendCommand]);
  const step = useCallback(() => sendCommand('step'), [sendCommand]);
  const save = useCallback(() => sendCommand('save'), [sendCommand]);

  const getAgentState = useCallback(
    (agentName: string) => sendCommand('get_agent_state', { agent_name: agentName }),
    [sendCommand]
  );

  const getAgentMemory = useCallback(
    (agentName: string, memoryType: 'event' | 'thought' | 'chat') =>
      sendCommand('get_agent_memory', { agent_name: agentName, memory_type: memoryType }),
    [sendCommand]
  );

  const getStatus = useCallback(() => sendCommand('get_simulation_status'), [sendCommand]);

  return {
    // State
    connected,
    status,
    agents,
    cognitiveStream,
    error,
    // Commands
    run,
    pause,
    resume,
    step,
    save,
    getAgentState,
    getAgentMemory,
    getStatus,
    sendCommand,
  };
}
