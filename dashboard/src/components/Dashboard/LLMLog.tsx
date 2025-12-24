import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSimulationStore } from '../../stores/simulationStore';
import { GlassCard } from '../ui/GlassCard';

export const LLMLog = () => {
  const { llmLogs } = useSimulationStore();
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const truncate = (text: string | undefined, length: number) => {
    if (!text) return '';
    return text.length > length ? text.slice(0, length) + '...' : text;
  };

  return (
    <GlassCard
      title="LLM Logs"
      className="h-full"
      headerRight={
        <span className="text-white/40 text-xs">
          {llmLogs.length} calls
        </span>
      }
    >
      <div className="h-full overflow-y-auto p-2 space-y-1">
        {llmLogs.length === 0 ? (
          <div className="h-full flex items-center justify-center text-white/30 text-sm">
            No LLM calls yet
          </div>
        ) : (
          <AnimatePresence mode="popLayout">
            {llmLogs.map((log, i) => {
              const isExpanded = expandedIndex === i;
              const isRequest = log.type === 'request';

              return (
                <motion.div
                  key={`${log.timestamp}-${i}`}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className={`
                    p-2 rounded border transition cursor-pointer
                    ${isRequest
                      ? 'bg-blue-500/10 border-blue-500/20 hover:bg-blue-500/20'
                      : 'bg-green-500/10 border-green-500/20 hover:bg-green-500/20'
                    }
                  `}
                  onClick={() => setExpandedIndex(isExpanded ? null : i)}
                >
                  {/* Header */}
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-medium ${isRequest ? 'text-blue-400' : 'text-green-400'}`}>
                        {isRequest ? 'REQ' : 'RES'}
                      </span>
                      <span className="text-white/60 text-xs font-mono">
                        {log.function}
                      </span>
                    </div>
                    <span className="text-white/30 text-[10px] shrink-0">
                      {formatTime(log.timestamp)}
                    </span>
                  </div>

                  {/* Preview or full content */}
                  <div className="mt-1">
                    {isExpanded ? (
                      <div className="space-y-2">
                        {log.prompt && (
                          <div>
                            <div className="text-blue-400/60 text-[10px] mb-1">PROMPT</div>
                            <pre className="text-white/70 text-xs bg-black/30 rounded p-2 overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto">
                              {log.prompt}
                            </pre>
                          </div>
                        )}
                        {log.response && (
                          <div>
                            <div className="text-green-400/60 text-[10px] mb-1">RESPONSE</div>
                            <pre className="text-white/70 text-xs bg-black/30 rounded p-2 overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto">
                              {log.response}
                            </pre>
                          </div>
                        )}
                        <div className="text-white/30 text-[10px]">
                          Model: {log.model}
                        </div>
                      </div>
                    ) : (
                      <div className="text-white/50 text-xs truncate">
                        {truncate(log.prompt || log.response, 80)}
                      </div>
                    )}
                  </div>

                  {/* Expand indicator */}
                  <div className="text-white/30 text-[10px] text-right mt-1">
                    {isExpanded ? 'Click to collapse' : 'Click to expand'}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}
      </div>
    </GlassCard>
  );
};
