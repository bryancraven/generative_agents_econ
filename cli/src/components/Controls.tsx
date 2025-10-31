/**
 * Controls - Keyboard shortcuts bar
 */

import React from 'react';
import { Box, Text } from 'ink';
import type { ExecutionMode } from '../types/simulation';

interface Props {
  mode: ExecutionMode;
}

export function Controls({ mode }: Props) {
  const isPaused = mode === 'paused' || mode === 'stopped';

  return (
    <Box borderStyle="round" borderColor="gray" paddingX={1}>
      <Box flexDirection="row" gap={1}>
        {isPaused ? (
          <Text>
            <Text bold>[Space]</Text> Resume
          </Text>
        ) : (
          <Text>
            <Text bold>[Space]</Text> Pause
          </Text>
        )}
        <Text dimColor>│</Text>
        <Text>
          <Text bold>[→]</Text> Step
        </Text>
        <Text dimColor>│</Text>
        <Text>
          <Text bold>[R]</Text> Run 10
        </Text>
        <Text dimColor>│</Text>
        <Text>
          <Text bold>[S]</Text> Save
        </Text>
        <Text dimColor>│</Text>
        <Text>
          <Text bold>[Tab]</Text> Switch Agent
        </Text>
        <Text dimColor>│</Text>
        <Text>
          <Text bold>[Q]</Text> Quit
        </Text>
      </Box>
    </Box>
  );
}
