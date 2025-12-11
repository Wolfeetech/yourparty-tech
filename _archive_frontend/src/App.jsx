import React, { useEffect } from 'react';
import Dashboard from './components/Dashboard';
import GenreBrowser from './components/GenreBrowser';
import MongoIntegration from './components/MongoIntegration';
import { Music } from 'lucide-react';
import { useStore } from './store';

function App() {
  const restoreLibrary = useStore(state => state.restoreLibrary);
  const _hasHydrated = useStore(state => state._hasHydrated);

  // Restore library from localStorage on first mount
  useEffect(() => {
    if (!_hasHydrated) {
      const restored = restoreLibrary();
      if (restored) {
        console.log('✅ Library automatisch wiederhergestellt');
      }
    }
  }, []);

  return (
    <div className="container">
      <header className="flex-between" style={{ padding: '2rem 0', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, var(--primary), var(--accent))',
            padding: '0.75rem',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)'
          }}>
            <Music size={32} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.5rem', margin: 0 }}>Music Library Automation</h1>
            <div className="text-muted">Auto-tag & Organize + Rating Sync</div>
          </div>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        <div style={{ position: 'sticky', top: '2rem', height: 'fit-content' }}>
          <Dashboard />
          <div style={{ marginTop: '2rem' }}>
            <MongoIntegration />
          </div>
        </div>
        <div>
          <GenreBrowser />
        </div>
      </div>
    </div>
  );
}

export default App;
