import { create } from 'zustand';
import type { SimulationEvent, AgentState, LLMLogEntry } from '../types/events';

interface SimulationStore {
  // Connection state
  connected: boolean;

  // Simulation state
  step: number;
  currTime: string;
  simCode: string;
  mode: 'stopped' | 'running' | 'paused' | 'stepping';

  // Events
  events: SimulationEvent[];
  llmLogs: LLMLogEntry[];

  // Agents
  agents: Record<string, AgentState>;
  agentNames: string[];

  // UI state
  selectedAgent: string | null;
  eventFilter: string | null;

  // Actions
  setConnected: (connected: boolean) => void;
  addEvent: (event: SimulationEvent) => void;
  updateAgentState: (name: string, state: Partial<AgentState>) => void;
  setAgents: (agents: string[]) => void;
  setSelectedAgent: (name: string | null) => void;
  setEventFilter: (filter: string | null) => void;
  setSimulationStatus: (status: Partial<{
    step: number;
    currTime: string;
    simCode: string;
    mode: 'stopped' | 'running' | 'paused' | 'stepping';
  }>) => void;
  clearEvents: () => void;
}

export const useSimulationStore = create<SimulationStore>((set) => ({
  // Initial state
  connected: false,
  step: 0,
  currTime: '',
  simCode: '',
  mode: 'stopped',
  events: [],
  llmLogs: [],
  agents: {},
  agentNames: [],
  selectedAgent: null,
  eventFilter: null,

  // Actions
  setConnected: (connected) => set({ connected }),

  addEvent: (event) => set((state) => {
    // Add to events list (keep last 500)
    const newEvents = [event, ...state.events].slice(0, 500);

    // Extract LLM logs
    const isLLMLog = event.type === 'llm.request' || event.type === 'llm.response';
    const newLLMLogs = isLLMLog
      ? [{
          timestamp: event.timestamp,
          function: (event.data?.function as string) || 'unknown',
          prompt: event.data?.prompt as string | undefined,
          response: event.data?.response as string | undefined,
          model: (event.data?.model as string) || 'unknown',
          type: event.type === 'llm.request' ? 'request' as const : 'response' as const,
        }, ...state.llmLogs].slice(0, 100)
      : state.llmLogs;

    // Update simulation status from events
    const updates: Partial<SimulationStore> = {
      events: newEvents,
      llmLogs: newLLMLogs,
    };

    if (event.data?.step !== undefined) {
      updates.step = event.data.step as number;
    }
    if (event.data?.curr_time !== undefined) {
      updates.currTime = event.data.curr_time as string;
    }
    if (event.data?.sim_code !== undefined) {
      updates.simCode = event.data.sim_code as string;
    }

    return updates;
  }),

  updateAgentState: (name, agentState) => set((state) => ({
    agents: {
      ...state.agents,
      [name]: { ...state.agents[name], ...agentState, name } as AgentState,
    },
  })),

  setAgents: (agentNames) => set((state) => {
    const agents: Record<string, AgentState> = {};
    agentNames.forEach((name) => {
      agents[name] = state.agents[name] || {
        name,
        location: [0, 0],
        action: 'unknown',
        actionAddress: '',
        emoji: '',
        description: '',
      };
    });
    return { agentNames, agents };
  }),

  setSelectedAgent: (name) => set({ selectedAgent: name }),

  setEventFilter: (filter) => set({ eventFilter: filter }),

  setSimulationStatus: (status) => set((state) => ({
    ...state,
    ...status,
  })),

  clearEvents: () => set({ events: [], llmLogs: [] }),
}));
