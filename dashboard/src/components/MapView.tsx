import { useSimulationStore } from '../stores/simulationStore';

const DJANGO_URL = 'http://localhost:8000';

export const MapView = () => {
  const { simCode, connected } = useSimulationStore();

  // Build URL for the simulation view
  const simulationUrl = simCode
    ? `${DJANGO_URL}/home/${simCode}/`
    : `${DJANGO_URL}/`;

  return (
    <div className="h-full w-full relative bg-slate-950">
      {/* Phaser simulation iframe */}
      <iframe
        src={simulationUrl}
        className="w-full h-full border-0"
        title="Simulation View"
      />

      {/* Overlay when not connected */}
      {!connected && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <div className="text-white/80 text-lg mb-2">Connecting to Simulation...</div>
            <div className="text-white/40 text-sm">
              Make sure the simulation server is running on port 8765
            </div>
          </div>
        </div>
      )}

      {/* Gradient overlay at edges for better integration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-8 bg-gradient-to-b from-slate-900/50 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-slate-900/50 to-transparent" />
      </div>
    </div>
  );
};
