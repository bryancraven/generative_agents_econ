import { MapView } from './MapView';
import { Minimap } from './Minimap';
import { SimulationControls } from './Dashboard/SimulationControls';
import { AgentPanel } from './Dashboard/AgentPanel';
import { EventLog } from './Dashboard/EventLog';
import { LLMLog } from './Dashboard/LLMLog';

export const Layout = () => {
  return (
    <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 flex overflow-hidden">
      {/* Left side - Map View (60%) */}
      <div className="w-[60%] h-full relative">
        <MapView />

        {/* Minimap overlay */}
        <Minimap className="absolute bottom-4 right-4 w-72 h-52 shadow-2xl" />
      </div>

      {/* Right side - Dashboard (40%) */}
      <div className="w-[40%] h-full flex flex-col p-4 gap-4 overflow-hidden">
        {/* Controls - fixed height */}
        <SimulationControls />

        {/* Scrollable panels */}
        <div className="flex-1 flex flex-col gap-4 overflow-hidden min-h-0">
          {/* Agent Panel */}
          <div className="h-[30%] min-h-[200px]">
            <AgentPanel />
          </div>

          {/* Event Log */}
          <div className="h-[35%] min-h-[200px]">
            <EventLog />
          </div>

          {/* LLM Log */}
          <div className="h-[35%] min-h-[200px]">
            <LLMLog />
          </div>
        </div>
      </div>
    </div>
  );
};
