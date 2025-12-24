import { useSimulationStore } from '../../stores/simulationStore';
import { GlassCard } from '../ui/GlassCard';

export const AgentPanel = () => {
  const { agents, agentNames, selectedAgent, setSelectedAgent } = useSimulationStore();

  const selected = selectedAgent ? agents[selectedAgent] : null;

  return (
    <GlassCard title="Agents" className="h-full">
      <div className="flex h-full">
        {/* Agent list */}
        <div className="w-40 border-r border-white/10 overflow-y-auto">
          {agentNames.map((name) => {
            const agent = agents[name];
            const isSelected = selectedAgent === name;

            return (
              <button
                key={name}
                onClick={() => setSelectedAgent(isSelected ? null : name)}
                className={`
                  w-full px-3 py-2 text-left text-sm transition
                  ${isSelected
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'text-white/70 hover:bg-white/5'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{agent?.emoji || ''}</span>
                  <span className="truncate">{name.split(' ')[0]}</span>
                </div>
              </button>
            );
          })}

          {agentNames.length === 0 && (
            <div className="p-3 text-white/40 text-sm">
              No agents loaded
            </div>
          )}
        </div>

        {/* Agent detail */}
        <div className="flex-1 p-4 overflow-y-auto">
          {selected ? (
            <div className="space-y-4">
              {/* Name and emoji */}
              <div className="flex items-center gap-3">
                <span className="text-3xl">{selected.emoji || ''}</span>
                <h4 className="text-white text-lg font-medium">{selected.name}</h4>
              </div>

              {/* Location */}
              <div>
                <div className="text-white/40 text-xs mb-1">Location</div>
                <div className="text-white/80 text-sm font-mono">
                  ({selected.location?.[0] || 0}, {selected.location?.[1] || 0})
                </div>
              </div>

              {/* Current action */}
              <div>
                <div className="text-white/40 text-xs mb-1">Current Action</div>
                <div className="text-white/80 text-sm">
                  {selected.action || 'Unknown'}
                </div>
              </div>

              {/* Action address */}
              {selected.actionAddress && (
                <div>
                  <div className="text-white/40 text-xs mb-1">Location</div>
                  <div className="text-white/60 text-xs font-mono">
                    {selected.actionAddress}
                  </div>
                </div>
              )}

              {/* Description */}
              {selected.description && (
                <div>
                  <div className="text-white/40 text-xs mb-1">Description</div>
                  <div className="text-white/60 text-sm">
                    {selected.description}
                  </div>
                </div>
              )}

              {/* Chatting with */}
              {selected.chattingWith && (
                <div className="flex items-center gap-2 text-pink-400 text-sm">
                  <span>Chatting with</span>
                  <span className="font-medium">{selected.chattingWith}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-white/40 text-sm">
              Select an agent to view details
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );
};
