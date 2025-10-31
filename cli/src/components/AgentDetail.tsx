/**
 * Agent Detail - Focused view of a single agent
 */

import React from 'react';
import { Box, Text } from 'ink';
import type { AgentState } from '../types/simulation';

interface Props {
  agent: AgentState | null;
}

export function AgentDetail({ agent }: Props) {
  if (!agent) {
    return (
      <Box flexDirection="column" borderStyle="round" borderColor="gray" paddingX={1}>
        <Text dimColor>Select an agent to view details (use Tab)</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="green" paddingX={1}>
      <Text bold color="green">
        {agent.name.toUpperCase()}
      </Text>
      <Box marginTop={1} flexDirection="column">
        <Box>
          <Text bold>Location: </Text>
          <Text>
            ({agent.location[0]}, {agent.location[1]})
          </Text>
        </Box>
        <Box marginTop={1}>
          <Text bold>Action: </Text>
          <Text>
            {agent.emoji} {agent.description}
          </Text>
        </Box>
        {agent.chattingWith && (
          <Box marginTop={1}>
            <Text bold>Chatting with: </Text>
            <Text color="magenta">{agent.chattingWith}</Text>
          </Box>
        )}
        {agent.currTime && (
          <Box marginTop={1}>
            <Text dimColor>Last updated: {agent.currTime}</Text>
          </Box>
        )}
      </Box>
    </Box>
  );
}
