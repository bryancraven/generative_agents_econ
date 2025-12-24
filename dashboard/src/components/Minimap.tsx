import { useSimulationStore } from '../stores/simulationStore';

// Map dimensions (from the_ville maze)
const MAP_WIDTH = 140;
const MAP_HEIGHT = 100;

interface MinimapProps {
  className?: string;
}

export const Minimap = ({ className = '' }: MinimapProps) => {
  const { agents, selectedAgent, setSelectedAgent } = useSimulationStore();

  const agentList = Object.values(agents);

  return (
    <div className={`bg-black/60 backdrop-blur-md rounded-xl border border-white/10 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-3 py-2 border-b border-white/10 flex items-center justify-between">
        <span className="text-white/60 text-xs font-medium">Minimap</span>
        <span className="text-white/40 text-[10px]">
          {agentList.length} agents
        </span>
      </div>

      {/* Map area */}
      <div className="relative w-full aspect-[140/100]">
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox={`0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Background grid */}
          <defs>
            <pattern
              id="minimap-grid"
              width="10"
              height="10"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 10 0 L 0 0 0 10"
                fill="none"
                stroke="rgba(255,255,255,0.05)"
                strokeWidth="0.3"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#minimap-grid)" />

          {/* Zones (simplified representation) */}
          <rect x="20" y="20" width="40" height="30" fill="rgba(100,200,100,0.1)" rx="2" />
          <rect x="70" y="40" width="50" height="40" fill="rgba(100,100,200,0.1)" rx="2" />
          <rect x="10" y="60" width="30" height="30" fill="rgba(200,100,100,0.1)" rx="2" />

          {/* Agent positions */}
          {agentList.map((agent) => {
            const x = agent.location?.[0] ?? 0;
            const y = agent.location?.[1] ?? 0;
            const isSelected = selectedAgent === agent.name;
            const initials = agent.name.split(' ').map((n) => n[0]).join('');

            return (
              <g
                key={agent.name}
                onClick={() => setSelectedAgent(isSelected ? null : agent.name)}
                style={{ cursor: 'pointer' }}
              >
                {/* Selection ring */}
                {isSelected && (
                  <circle
                    cx={x}
                    cy={y}
                    r={4}
                    fill="none"
                    stroke="#22d3ee"
                    strokeWidth="0.5"
                    className="animate-pulse"
                  />
                )}

                {/* Agent dot */}
                <circle
                  cx={x}
                  cy={y}
                  r={2}
                  fill={isSelected ? '#22d3ee' : '#a855f7'}
                  className={isSelected ? 'animate-pulse' : ''}
                />

                {/* Agent initials */}
                <text
                  x={x + 3}
                  y={y + 1}
                  fill="rgba(255,255,255,0.7)"
                  fontSize="3"
                  fontFamily="system-ui"
                >
                  {initials}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Legend */}
        <div className="absolute bottom-1 left-1 flex gap-2">
          {agentList.slice(0, 3).map((agent) => (
            <div
              key={agent.name}
              className="flex items-center gap-1 text-[8px] text-white/50"
            >
              <span>{agent.emoji || ''}</span>
              <span>{agent.name.split(' ')[0]}</span>
            </div>
          ))}
          {agentList.length > 3 && (
            <span className="text-[8px] text-white/30">
              +{agentList.length - 3} more
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
