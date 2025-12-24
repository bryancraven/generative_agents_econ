// Simulation event types
export type EventType =
  | 'sim.started'
  | 'sim.step'
  | 'sim.paused'
  | 'sim.resumed'
  | 'sim.saved'
  | 'sim.stopped'
  | 'agent.perceived'
  | 'agent.retrieved'
  | 'agent.planned'
  | 'agent.reflected'
  | 'agent.executed'
  | 'agent.moved'
  | 'agent.chat_started'
  | 'agent.chat_message'
  | 'agent.chat_ended'
  | 'agent.state_changed'
  | 'llm.request'
  | 'llm.response'
  | 'connection.established'
  | 'events.history';

export interface SimulationEvent {
  type: EventType;
  timestamp: string;
  data: Record<string, unknown>;
}

export interface AgentState {
  name: string;
  location: [number, number];
  action: string;
  actionAddress: string;
  emoji: string;
  description: string;
  chattingWith?: string;
  currTime?: string;
}

export interface SimulationStatus {
  simCode: string;
  step: number;
  currTime: string;
  mode: 'stopped' | 'running' | 'paused' | 'stepping';
  personas: string[];
  personasCount: number;
}

export interface LLMLogEntry {
  timestamp: string;
  function: string;
  prompt?: string;
  response?: string;
  model: string;
  type: 'request' | 'response';
}

// WebSocket message types
export interface WSMessage {
  type: string;
  data?: Record<string, unknown>;
  cmd?: string;
}
