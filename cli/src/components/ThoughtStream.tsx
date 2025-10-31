/**
 * Thought Stream - Live cognitive events display
 */

import React from 'react';
import { Box, Text } from 'ink';
import { formatDistanceToNow } from 'date-fns';
import type { CognitiveEvent } from '../types/simulation';

interface Props {
  events: CognitiveEvent[];
  selectedAgent: string | null;
  maxEvents?: number;
}

export function ThoughtStream({ events, selectedAgent, maxEvents = 10 }: Props) {
  // Filter events for selected agent if any
  const filteredEvents = selectedAgent
    ? events.filter((e) => e.agent === selectedAgent)
    : events;

  const displayEvents = filteredEvents.slice(0, maxEvents);

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="magenta" paddingX={1}>
      <Text bold color="magenta">
        Cognitive Stream {selectedAgent ? `- ${selectedAgent}` : '(All Agents)'}
      </Text>
      <Box flexDirection="column" marginTop={1}>
        {displayEvents.length === 0 ? (
          <Text dimColor>No events yet...</Text>
        ) : (
          displayEvents.map((event, idx) => {
            const timeAgo = formatDistanceToNow(new Date(event.timestamp), {
              addSuffix: false,
              includeSeconds: true,
            });

            const typeColors = {
              perceive: 'blue',
              retrieve: 'cyan',
              plan: 'green',
              reflect: 'yellow',
              execute: 'magenta',
              move: 'white',
              chat: 'magenta',
            };

            const typeLabels = {
              perceive: 'PERCEIVE',
              retrieve: 'RETRIEVE',
              plan: 'PLAN',
              reflect: 'REFLECT',
              execute: 'EXECUTE',
              move: 'MOVE',
              chat: 'CHAT',
            };

            return (
              <Box key={idx} flexDirection="column" marginY={0}>
                <Box>
                  <Text dimColor>{timeAgo} ago </Text>
                  <Text>{event.icon} </Text>
                  <Text color={typeColors[event.type]} bold>
                    {typeLabels[event.type]}:
                  </Text>
                  {!selectedAgent && (
                    <Text color="gray"> [{event.agent.split(' ')[0]}]</Text>
                  )}
                </Box>
                <Box marginLeft={2}>
                  <Text>{event.description}</Text>
                </Box>
              </Box>
            );
          })
        )}
      </Box>
    </Box>
  );
}
