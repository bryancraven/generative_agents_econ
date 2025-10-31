/**
 * Custom hook for keyboard shortcuts and input handling
 */

import { useInput } from 'ink';
import { useCallback } from 'react';

export interface KeyboardHandlers {
  onPause?: () => void;
  onResume?: () => void;
  onStep?: () => void;
  onRun?: (steps: number) => void;
  onSave?: () => void;
  onQuit?: () => void;
  onNextAgent?: () => void;
  onPrevAgent?: () => void;
  onToggleView?: () => void;
  onToggleMemoryType?: () => void;
  onFilter?: () => void;
}

export function useKeyboard(handlers: KeyboardHandlers) {
  useInput(
    useCallback(
      (input, key) => {
        // Space - Pause/Resume
        if (input === ' ') {
          handlers.onPause?.();
        }

        // Arrow Right - Step forward
        if (key.rightArrow) {
          handlers.onStep?.();
        }

        // R - Run 10 steps
        if (input === 'r' || input === 'R') {
          handlers.onRun?.(10);
        }

        // S - Save
        if (input === 's' || input === 'S') {
          handlers.onSave?.();
        }

        // Q - Quit
        if (input === 'q' || input === 'Q') {
          handlers.onQuit?.();
        }

        // Tab - Next agent
        if (key.tab && !key.shift) {
          handlers.onNextAgent?.();
        }

        // Shift+Tab - Previous agent
        if (key.tab && key.shift) {
          handlers.onPrevAgent?.();
        }

        // V - Toggle view mode
        if (input === 'v' || input === 'V') {
          handlers.onToggleView?.();
        }

        // M - Toggle memory type (Events/Thoughts/Chats)
        if (input === 'm' || input === 'M') {
          handlers.onToggleMemoryType?.();
        }

        // F - Filter
        if (input === 'f' || input === 'F') {
          handlers.onFilter?.();
        }

        // Ctrl+C - Quit
        if (key.ctrl && input === 'c') {
          handlers.onQuit?.();
        }
      },
      [handlers]
    )
  );
}
