import { useSimulationStore } from '../../stores/simulationStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import { GlassCard } from '../ui/GlassCard';

export const SimulationControls = () => {
  const { connected, step, currTime, simCode, mode } = useSimulationStore();
  const { run, pause, resume, step: stepOnce, save } = useWebSocket();

  const modeColors = {
    stopped: 'text-gray-400',
    running: 'text-green-400',
    paused: 'text-yellow-400',
    stepping: 'text-blue-400',
  };

  const modeIcons = {
    stopped: '',
    running: '',
    paused: '',
    stepping: '',
  };

  return (
    <GlassCard className="shrink-0">
      <div className="p-4">
        {/* Status bar */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            {/* Connection indicator */}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
              <span className="text-white/60 text-xs">{connected ? 'Connected' : 'Disconnected'}</span>
            </div>

            {/* Mode */}
            <div className={`text-sm font-medium ${modeColors[mode]}`}>
              {modeIcons[mode]} {mode.toUpperCase()}
            </div>
          </div>

          {/* Sim code */}
          {simCode && (
            <div className="text-white/40 text-xs font-mono">
              {simCode}
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-white/5 rounded-lg p-3">
            <div className="text-white/40 text-xs mb-1">Step</div>
            <div className="text-white text-xl font-bold">{step}</div>
          </div>
          <div className="bg-white/5 rounded-lg p-3">
            <div className="text-white/40 text-xs mb-1">Game Time</div>
            <div className="text-white text-sm font-medium truncate">
              {currTime || '--'}
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex gap-2">
          {mode === 'running' ? (
            <button
              onClick={pause}
              disabled={!connected}
              className="flex-1 px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 rounded-lg text-sm font-medium transition disabled:opacity-50"
            >
              Pause
            </button>
          ) : (
            <button
              onClick={resume}
              disabled={!connected}
              className="flex-1 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-sm font-medium transition disabled:opacity-50"
            >
              Resume
            </button>
          )}

          <button
            onClick={stepOnce}
            disabled={!connected || mode === 'running'}
            className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg text-sm font-medium transition disabled:opacity-50"
          >
            Step
          </button>

          <button
            onClick={() => run(10)}
            disabled={!connected}
            className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 rounded-lg text-sm font-medium transition disabled:opacity-50"
          >
            +10
          </button>

          <button
            onClick={save}
            disabled={!connected}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white/70 rounded-lg text-sm font-medium transition disabled:opacity-50"
          >
            Save
          </button>
        </div>
      </div>
    </GlassCard>
  );
};
