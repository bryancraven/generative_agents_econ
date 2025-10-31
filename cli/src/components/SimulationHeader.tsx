/**
 * Simulation Header - Status bar showing time, step, and running state
 */

import React from 'react';
import { Box, Text } from 'ink';
import type { SimulationStatus } from '../types/simulation';

interface Props {
  status: SimulationStatus | null;
  connected: boolean;
}

export function SimulationHeader({ status, connected }: Props) {
  if (!connected) {
    return (
      <Box borderStyle="round" borderColor="yellow" paddingX={1}>
        <Text color="yellow">⚠ Connecting to simulation server...</Text>
      </Box>
    );
  }

  if (!status) {
    return (
      <Box borderStyle="round" borderColor="gray" paddingX={1}>
        <Text color="gray">⏳ Waiting for simulation to start...</Text>
      </Box>
    );
  }

  const modeIcon = {
    running: '▶',
    paused: '⏸',
    stopped: '⏹',
    stepping: '⏩',
  }[status.mode];

  const modeColor = {
    running: 'green',
    paused: 'yellow',
    stopped: 'red',
    stepping: 'cyan',
  }[status.mode];

  return (
    <Box borderStyle="round" borderColor="cyan" paddingX={1}>
      <Box flexDirection="row" gap={2}>
        <Text bold color="cyan">
          Reverie Simulation
        </Text>
        <Text dimColor>│</Text>
        <Text>🕐 {status.currTime}</Text>
        <Text dimColor>│</Text>
        <Text>Step {status.step}</Text>
        <Text dimColor>│</Text>
        <Text color={modeColor}>
          {modeIcon} {status.mode.toUpperCase()}
        </Text>
        <Text dimColor>│</Text>
        <Text>{status.personasCount} agents</Text>
      </Box>
    </Box>
  );
}
