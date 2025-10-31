/**
 * Agent List - Sidebar showing all agents with selection
 */

import React from 'react';
import { Box, Text } from 'ink';
import type { AgentState } from '../types/simulation';

interface Props {
  agents: Map<string, AgentState>;
  selectedAgent: string | null;
  personas: string[];
}

export function AgentList({ agents, selectedAgent, personas }: Props) {
  return (
    <Box flexDirection="column" borderStyle="round" borderColor="blue" paddingX={1} width={20}>
      <Text bold color="blue">
        AGENTS
      </Text>
      <Box flexDirection="column" marginTop={1}>
        {personas.map((name) => {
          const isSelected = name === selectedAgent;
          const agent = agents.get(name);
          const symbol = isSelected ? '◉' : '○';
          const color = isSelected ? 'cyan' : 'white';

          return (
            <Box key={name} marginY={0}>
              <Text color={color}>
                {symbol} {name.split(' ')[0]}
                {agent?.emoji ? ` ${agent.emoji}` : ''}
              </Text>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}
