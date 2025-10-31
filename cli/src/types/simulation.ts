/**
 * TypeScript type definitions for simulation data structures
 */

export type ExecutionMode = 'stopped' | 'running' | 'paused' | 'stepping';

export type EventType =
  // Simulation lifecycle
  | 'sim.started'
  | 'sim.step'
  | 'sim.paused'
  | 'sim.resumed'
  | 'sim.saved'
  | 'sim.stopped'
  // Agent cognitive events
  | 'agent.perceived'
  | 'agent.retrieved'
  | 'agent.planned'
  | 'agent.reflected'
  | 'agent.executed'
  | 'agent.moved'
  // Agent social events
  | 'agent.chat_started'
  | 'agent.chat_message'
  | 'agent.chat_ended'
  // Agent state
  | 'agent.state_changed'
  // Connection
  | 'connection.established'
  | 'events.history'
  // Errors
  | 'error';

export interface SimulationEvent {
  type: EventType;
  timestamp: string;
  data: Record<string, any>;
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

export interface CognitiveEvent {
  timestamp: string;
  type: 'perceive' | 'retrieve' | 'plan' | 'reflect' | 'execute' | 'move' | 'chat';
  agent: string;
  data: any;
  icon: string;
  description: string;
}

export interface MemoryNode {
  type: 'event' | 'thought' | 'chat';
  description: string;
  subject?: string;
  predicate?: string;
  object?: string;
  timestamp?: string;
  poignancy?: number;
}

export interface SimulationStatus {
  simCode: string;
  step: number;
  currTime: string;
  mode: ExecutionMode;
  personas: string[];
  personasCount: number;
}

export interface AgentMemory {
  events: string[];
  thoughts: string[];
  chats: string[];
}

export type ViewMode = 'overview' | 'focused';
export type MemoryType = 'event' | 'thought' | 'chat';

export interface AppState {
  connected: boolean;
  status: SimulationStatus | null;
  agents: Map<string, AgentState>;
  cognitiveStream: CognitiveEvent[];
  selectedAgent: string | null;
  viewMode: ViewMode;
  memoryType: MemoryType;
  filterText: string;
}

export interface CommandResponse {
  success: boolean;
  message?: string;
  data?: any;
}
