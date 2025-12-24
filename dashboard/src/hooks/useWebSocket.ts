import { useEffect, useRef, useCallback } from 'react';
import { useSimulationStore } from '../stores/simulationStore';
import type { SimulationEvent, AgentState } from '../types/events';

const WS_URL = 'ws://localhost:8765';
const RECONNECT_DELAY = 3000;

export const useWebSocket = () => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const {
    setConnected,
    addEvent,
    updateAgentState,
    setAgents,
    setSimulationStatus,
  } = useSimulationStore();

  const connect = useCallback(() => {
    // Clear any existing reconnect timeout
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    // Create new WebSocket connection
    console.log('[WS] Connecting to', WS_URL);
    ws.current = new WebSocket(WS_URL);

    ws.current.onopen = () => {
      console.log('[WS] Connected');
      setConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleMessage(data);
      } catch (error) {
        console.error('[WS] Failed to parse message:', error);
      }
    };

    ws.current.onclose = () => {
      console.log('[WS] Disconnected');
      setConnected(false);

      // Schedule reconnect
      reconnectTimeout.current = setTimeout(() => {
        console.log('[WS] Reconnecting...');
        connect();
      }, RECONNECT_DELAY);
    };

    ws.current.onerror = (error) => {
      console.error('[WS] Error:', error);
    };
  }, [setConnected]);

  const handleMessage = useCallback((data: Record<string, unknown>) => {
    const type = data.type as string;

    switch (type) {
      case 'connection.established':
        console.log('[WS] Connection acknowledged');
        break;

      case 'events.history':
        // Process historical events
        const historyEvents = (data.data as { events: SimulationEvent[] })?.events || [];
        historyEvents.forEach((event) => addEvent(event));
        break;

      case 'sim.started':
        const startData = data.data as Record<string, unknown>;
        setSimulationStatus({
          simCode: startData.sim_code as string,
          step: startData.step as number,
          currTime: startData.curr_time as string,
          mode: 'running',
        });
        if (startData.personas) {
          setAgents(startData.personas as string[]);
        }
        addEvent(data as SimulationEvent);
        break;

      case 'sim.step':
        const stepData = data.data as Record<string, unknown>;
        setSimulationStatus({
          step: stepData.step as number,
          currTime: stepData.curr_time as string,
        });
        addEvent(data as SimulationEvent);
        break;

      case 'sim.paused':
        setSimulationStatus({ mode: 'paused' });
        addEvent(data as SimulationEvent);
        break;

      case 'sim.resumed':
        setSimulationStatus({ mode: 'running' });
        addEvent(data as SimulationEvent);
        break;

      case 'sim.stopped':
        setSimulationStatus({ mode: 'stopped' });
        addEvent(data as SimulationEvent);
        break;

      case 'agent.moved':
        const moveData = data.data as Record<string, unknown>;
        updateAgentState(moveData.agent as string, {
          location: moveData.to_tile as [number, number],
          emoji: moveData.emoji as string,
          description: moveData.description as string,
        });
        addEvent(data as SimulationEvent);
        break;

      case 'agent.planned':
        const planData = data.data as Record<string, unknown>;
        updateAgentState(planData.agent as string, {
          action: planData.action_desc as string,
          actionAddress: planData.action_address as string,
        });
        addEvent(data as SimulationEvent);
        break;

      case 'agent.perceived':
      case 'agent.retrieved':
      case 'agent.reflected':
      case 'agent.executed':
      case 'agent.chat_started':
      case 'agent.chat_message':
      case 'agent.chat_ended':
      case 'agent.state_changed':
      case 'llm.request':
      case 'llm.response':
        addEvent(data as SimulationEvent);
        break;

      default:
        console.log('[WS] Unknown message type:', type, data);
    }
  }, [addEvent, updateAgentState, setAgents, setSimulationStatus]);

  const sendCommand = useCallback((cmd: string, cmdData?: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ cmd, data: cmdData }));
    } else {
      console.warn('[WS] Cannot send command - not connected');
    }
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  return {
    sendCommand,
    run: (steps: number = 10) => sendCommand('run', { steps }),
    pause: () => sendCommand('pause'),
    resume: () => sendCommand('resume'),
    step: () => sendCommand('step'),
    save: () => sendCommand('save'),
    getAgentState: (agentName: string) => sendCommand('get_agent_state', { agent_name: agentName }),
    getAgentMemory: (agentName: string, memoryType: string) =>
      sendCommand('get_agent_memory', { agent_name: agentName, memory_type: memoryType }),
  };
};
