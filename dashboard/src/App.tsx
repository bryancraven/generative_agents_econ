import { useEffect } from 'react';
import { Layout } from './components/Layout';
import { useWebSocket } from './hooks/useWebSocket';

function App() {
  // Initialize WebSocket connection
  useWebSocket();

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Prevent shortcuts when typing in inputs
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case ' ':
          e.preventDefault();
          // Toggle pause/resume (handled by controls)
          break;
        case 'Escape':
          // Clear selection
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return <Layout />;
}

export default App;
