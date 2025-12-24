import { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSimulationStore } from '../../stores/simulationStore';
import { GlassCard } from '../ui/GlassCard';

const EVENT_CONFIG: Record<string, { color: string; icon: string }> = {
  'sim.started': { color: 'text-green-400', icon: '' },
  'sim.step': { color: 'text-blue-400', icon: '' },
  'sim.paused': { color: 'text-yellow-400', icon: '' },
  'sim.resumed': { color: 'text-green-400', icon: '' },
  'sim.saved': { color: 'text-purple-400', icon: '' },
  'agent.perceived': { color: 'text-purple-400', icon: '' },
  'agent.retrieved': { color: 'text-cyan-400', icon: '' },
  'agent.planned': { color: 'text-yellow-400', icon: '' },
  'agent.reflected': { color: 'text-pink-400', icon: '' },
  'agent.executed': { color: 'text-orange-400', icon: '' },
  'agent.moved': { color: 'text-green-400', icon: '' },
  'agent.chat_started': { color: 'text-cyan-400', icon: '' },
  'agent.chat_message': { color: 'text-cyan-300', icon: '' },
  'agent.chat_ended': { color: 'text-cyan-500', icon: '' },
};

export const EventLog = () => {
  const { events, selectedAgent, eventFilter, setEventFilter } = useSimulationStore();

  // Get unique event types for filter buttons
  const eventTypes = useMemo(() => {
    return [...new Set(events.map((e) => e.type))].slice(0, 8);
  }, [events]);

  // Filter events
  const filteredEvents = useMemo(() => {
    return events.filter((e) => {
      // Filter by selected agent
      if (selectedAgent) {
        const eventAgent = e.data?.agent as string | undefined;
        if (eventAgent && eventAgent !== selectedAgent) return false;
      }
      // Filter by event type
      if (eventFilter && e.type !== eventFilter) return false;
      return true;
    });
  }, [events, selectedAgent, eventFilter]);

  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const getEventDescription = (event: typeof events[0]) => {
    const data = event.data || {};

    switch (event.type) {
      case 'agent.moved':
        return `${data.agent} moved to (${(data.to_tile as number[])?.[0]}, ${(data.to_tile as number[])?.[1]})`;
      case 'agent.planned':
        return `${data.agent}: ${(data.action_desc as string)?.slice(0, 50)}...`;
      case 'agent.perceived':
        return `${data.agent} perceived ${data.count || 0} events`;
      case 'agent.retrieved':
        return `${data.agent} retrieved ${data.retrieved_count || 0} memories`;
      case 'agent.reflected':
        return `${data.agent}: "${(data.thought as string)?.slice(0, 50)}..."`;
      case 'agent.chat_started':
        return `${data.agent1} started chatting with ${data.agent2}`;
      case 'agent.chat_message':
        return `${data.speaker}: "${(data.message as string)?.slice(0, 40)}..."`;
      case 'sim.step':
        return `Step ${data.step}`;
      default:
        return event.type;
    }
  };

  return (
    <GlassCard
      title="Event Log"
      className="h-full"
      headerRight={
        <span className="text-white/40 text-xs">
          {filteredEvents.length} events
        </span>
      }
    >
      <div className="flex flex-col h-full">
        {/* Filter bar */}
        <div className="flex gap-1 p-2 border-b border-white/10 flex-wrap shrink-0">
          <button
            onClick={() => setEventFilter(null)}
            className={`
              px-2 py-1 rounded text-xs transition
              ${!eventFilter ? 'bg-white/20 text-white' : 'bg-white/5 text-white/60 hover:bg-white/10'}
            `}
          >
            All
          </button>
          {eventTypes.map((type) => {
            const config = EVENT_CONFIG[type] || { color: 'text-white/60', icon: '' };
            const shortName = type.split('.')[1] || type;
            return (
              <button
                key={type}
                onClick={() => setEventFilter(eventFilter === type ? null : type)}
                className={`
                  px-2 py-1 rounded text-xs transition
                  ${eventFilter === type
                    ? 'bg-white/20'
                    : 'bg-white/5 hover:bg-white/10'
                  }
                  ${config.color}
                `}
              >
                {shortName}
              </button>
            );
          })}
        </div>

        {/* Event list */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          <AnimatePresence mode="popLayout">
            {filteredEvents.slice(0, 100).map((event, i) => {
              const config = EVENT_CONFIG[event.type] || { color: 'text-white/60', icon: '' };

              return (
                <motion.div
                  key={`${event.timestamp}-${i}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 10 }}
                  transition={{ duration: 0.15 }}
                  className="p-2 rounded bg-white/5 border border-white/5 hover:bg-white/10 transition"
                >
                  <div className="flex justify-between items-start gap-2">
                    <span className={`text-xs font-medium ${config.color}`}>
                      {config.icon} {event.type}
                    </span>
                    <span className="text-white/30 text-[10px] shrink-0">
                      {formatTime(event.timestamp)}
                    </span>
                  </div>
                  <div className="text-white/60 text-xs mt-1 truncate">
                    {getEventDescription(event)}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {filteredEvents.length === 0 && (
            <div className="h-full flex items-center justify-center text-white/30 text-sm">
              No events
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );
};
