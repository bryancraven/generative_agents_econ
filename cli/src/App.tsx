/**
 * Main App Component - Sophisticated CLI UX for Reverie Simulation
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Box, Text, useApp } from 'ink';
import { SimulationHeader } from './components/SimulationHeader.js';
import { AgentList } from './components/AgentList.js';
import { AgentDetail } from './components/AgentDetail.js';
import { ThoughtStream } from './components/ThoughtStream.js';
import { Controls } from './components/Controls.js';
import { useSimulation } from './hooks/useSimulation.js';
import { useKeyboard } from './hooks/useKeyboard.js';

export function App() {
  const { exit } = useApp();
  const {
    connected,
    status,
    agents,
    cognitiveStream,
    error,
    run,
    pause,
    resume,
    step,
    save,
    getStatus,
  } = useSimulation();

  const [selectedAgentIndex, setSelectedAgentIndex] = useState(0);
  const [showQuitConfirm, setShowQuitConfirm] = useState(false);

  // Get personas list from status
  const personas = status?.personas || [];
  const selectedAgent = personas[selectedAgentIndex] || null;
  const selectedAgentState = selectedAgent ? agents.get(selectedAgent) : null;

  // Fetch initial status
  useEffect(() => {
    if (connected && !status) {
      getStatus().then((response) => {
        if (response.success && response.data) {
          // Status will be updated via event handling
        }
      });
    }
  }, [connected, status, getStatus]);

  // Keyboard handlers
  const handlePause = useCallback(() => {
    if (status?.mode === 'running') {
      pause();
    } else if (status?.mode === 'paused') {
      resume();
    }
  }, [status?.mode, pause, resume]);

  const handleStep = useCallback(() => {
    step();
  }, [step]);

  const handleRun = useCallback(
    (steps: number) => {
      run(steps);
    },
    [run]
  );

  const handleSave = useCallback(() => {
    save();
  }, [save]);

  const handleQuit = useCallback(() => {
    if (!showQuitConfirm) {
      setShowQuitConfirm(true);
      setTimeout(() => setShowQuitConfirm(false), 3000);
    } else {
      exit();
    }
  }, [showQuitConfirm, exit]);

  const handleNextAgent = useCallback(() => {
    setSelectedAgentIndex((prev) => (prev + 1) % Math.max(personas.length, 1));
  }, [personas.length]);

  const handlePrevAgent = useCallback(() => {
    setSelectedAgentIndex(
      (prev) => (prev - 1 + personas.length) % Math.max(personas.length, 1)
    );
  }, [personas.length]);

  useKeyboard({
    onPause: handlePause,
    onStep: handleStep,
    onRun: handleRun,
    onSave: handleSave,
    onQuit: handleQuit,
    onNextAgent: handleNextAgent,
    onPrevAgent: handlePrevAgent,
  });

  if (error) {
    return (
      <Box flexDirection="column" padding={1}>
        <Text color="red" bold>
          ❌ Error: {error}
        </Text>
        <Text dimColor marginTop={1}>
          Make sure the simulation server is running with CLI mode enabled.
        </Text>
        <Text dimColor>Press Q to quit.</Text>
      </Box>
    );
  }

  if (showQuitConfirm) {
    return (
      <Box
        flexDirection="column"
        padding={1}
        borderStyle="double"
        borderColor="yellow"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="yellow" bold>
          Press Q again to quit, or wait to cancel.
        </Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" padding={1}>
      {/* Header */}
      <SimulationHeader status={status} connected={connected} />

      {/* Main content area */}
      <Box flexDirection="row" marginTop={1} gap={1}>
        {/* Left sidebar - Agent list */}
        <AgentList agents={agents} selectedAgent={selectedAgent} personas={personas} />

        {/* Right panel - Agent detail and thought stream */}
        <Box flexDirection="column" flexGrow={1} gap={1}>
          {/* Agent detail */}
          <AgentDetail agent={selectedAgentState} />

          {/* Cognitive stream */}
          <Box flexGrow={1}>
            <ThoughtStream
              events={cognitiveStream}
              selectedAgent={selectedAgent}
              maxEvents={15}
            />
          </Box>
        </Box>
      </Box>

      {/* Controls bar */}
      <Box marginTop={1}>
        <Controls mode={status?.mode || 'stopped'} />
      </Box>
    </Box>
  );
}
