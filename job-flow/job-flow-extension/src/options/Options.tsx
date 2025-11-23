/**
 * Options Page Component
 * Extension settings and configuration
 */

import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Storage } from '../shared/utils/storage';
import { backendClient } from '../shared/api/backend-client';
import type { Settings } from '../shared/types';

const Options: React.FC = () => {
  const [settings, setSettings] = useState<Settings>(Storage.getDefaultSettings());
  const [backendConnected, setBackendConnected] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    const loaded = await Storage.getSettings();
    if (loaded) {
      setSettings(loaded);
      backendClient.setBaseURL(loaded.backendUrl);
      await testConnection(loaded.backendUrl);
    }
  };

  const testConnection = async (url?: string) => {
    setTestingConnection(true);
    const testUrl = url || settings.backendUrl;
    backendClient.setBaseURL(testUrl);

    const connected = await backendClient.healthCheck();
    setBackendConnected(connected);
    setTestingConnection(false);
  };

  const handleSave = async () => {
    await Storage.setSettings(settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleBackendUrlChange = (url: string) => {
    setSettings({ ...settings, backendUrl: url });
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>JobFlow Settings</h1>
        <p style={styles.subtitle}>Configure your job application automation</p>
      </header>

      <main style={styles.main}>
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Backend Connection</h2>

          <div style={styles.formGroup}>
            <label style={styles.label}>Backend API URL</label>
            <input
              type="text"
              value={settings.backendUrl}
              onChange={(e) => handleBackendUrlChange(e.target.value)}
              placeholder="http://localhost:8000"
              style={styles.input}
            />
            <p style={styles.hint}>
              URL of the JobFlow backend server (default: http://localhost:8000)
            </p>
          </div>

          <div style={styles.statusContainer}>
            <button
              onClick={() => testConnection()}
              disabled={testingConnection}
              style={styles.button}
            >
              {testingConnection ? 'Testing...' : 'Test Connection'}
            </button>

            {!testingConnection && (
              <div style={{
                ...styles.status,
                color: backendConnected ? '#10B981' : '#EF4444'
              }}>
                {backendConnected ? '✓ Connected' : '✗ Not Connected'}
              </div>
            )}
          </div>

          {!backendConnected && (
            <div style={styles.errorBox}>
              <p><strong>Backend not connected.</strong></p>
              <p>Make sure the backend server is running:</p>
              <pre style={styles.code}>
                cd job-flow-backend{'\n'}
                uvicorn app.main:app --reload
              </pre>
            </div>
          )}
        </section>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Auto-Fill Settings</h2>

          <div style={styles.formGroup}>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={settings.autoFillEnabled}
                onChange={(e) => setSettings({
                  ...settings,
                  autoFillEnabled: e.target.checked
                })}
                style={styles.checkbox}
              />
              <span>Enable automatic form filling</span>
            </label>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={settings.showReviewInterface}
                onChange={(e) => setSettings({
                  ...settings,
                  showReviewInterface: e.target.checked
                })}
                style={styles.checkbox}
              />
              <span>Show review interface before submitting</span>
            </label>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={settings.keyboardShortcutsEnabled}
                onChange={(e) => setSettings({
                  ...settings,
                  keyboardShortcutsEnabled: e.target.checked
                })}
                style={styles.checkbox}
              />
              <span>Enable keyboard shortcuts (Ctrl+Shift+F to fill)</span>
            </label>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={settings.notificationsEnabled}
                onChange={(e) => setSettings({
                  ...settings,
                  notificationsEnabled: e.target.checked
                })}
                style={styles.checkbox}
              />
              <span>Show notifications</span>
            </label>
          </div>
        </section>

        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Quick Links</h2>

          <div style={styles.linkGrid}>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              style={styles.link}
            >
              📚 API Documentation
            </a>
            <a
              href="https://github.com/yourusername/job-flow"
              target="_blank"
              rel="noopener noreferrer"
              style={styles.link}
            >
              💻 GitHub Repository
            </a>
            <a
              href={`${settings.backendUrl}/api/profile/`}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.link}
            >
              👤 View Profile
            </a>
            <a
              href={`${settings.backendUrl}/api/analytics/overview`}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.link}
            >
              📊 Analytics
            </a>
          </div>
        </section>

        <div style={styles.saveContainer}>
          <button
            onClick={handleSave}
            style={styles.saveButton}
          >
            {saved ? '✓ Saved!' : 'Save Settings'}
          </button>
        </div>
      </main>

      <footer style={styles.footer}>
        <p>JobFlow v1.0.0 • Job Application Automation Tool</p>
      </footer>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#F9FAFB',
  },
  header: {
    padding: '32px',
    backgroundColor: '#FFFFFF',
    borderBottom: '1px solid #E5E7EB',
  },
  title: {
    margin: 0,
    fontSize: '32px',
    fontWeight: '600',
    color: '#111827',
  },
  subtitle: {
    margin: '8px 0 0 0',
    fontSize: '16px',
    color: '#6B7280',
  },
  main: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '32px',
  },
  section: {
    marginBottom: '32px',
    padding: '24px',
    backgroundColor: '#FFFFFF',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  sectionTitle: {
    margin: '0 0 20px 0',
    fontSize: '20px',
    fontWeight: '600',
    color: '#111827',
  },
  formGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
  },
  input: {
    width: '100%',
    padding: '10px 12px',
    fontSize: '14px',
    border: '1px solid #D1D5DB',
    borderRadius: '6px',
    boxSizing: 'border-box' as const,
  },
  hint: {
    margin: '6px 0 0 0',
    fontSize: '12px',
    color: '#6B7280',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '14px',
    color: '#374151',
    cursor: 'pointer',
  },
  checkbox: {
    marginRight: '10px',
    width: '16px',
    height: '16px',
    cursor: 'pointer',
  },
  statusContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  button: {
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#FFFFFF',
    backgroundColor: '#3B82F6',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  status: {
    fontSize: '14px',
    fontWeight: '500',
  },
  errorBox: {
    marginTop: '16px',
    padding: '16px',
    backgroundColor: '#FEF2F2',
    border: '1px solid #FCA5A5',
    borderRadius: '6px',
    fontSize: '14px',
    color: '#991B1B',
  },
  code: {
    marginTop: '12px',
    padding: '12px',
    backgroundColor: '#1F2937',
    color: '#F9FAFB',
    borderRadius: '4px',
    fontSize: '12px',
    fontFamily: 'monospace',
    overflow: 'auto',
  },
  linkGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '12px',
  },
  link: {
    padding: '16px',
    backgroundColor: '#F3F4F6',
    border: '1px solid #E5E7EB',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#3B82F6',
    textDecoration: 'none',
    textAlign: 'center' as const,
  },
  saveContainer: {
    marginTop: '32px',
    textAlign: 'center' as const,
  },
  saveButton: {
    padding: '12px 32px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#FFFFFF',
    backgroundColor: '#10B981',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
  },
  footer: {
    padding: '24px',
    textAlign: 'center' as const,
    fontSize: '14px',
    color: '#6B7280',
  },
};

// Render
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<Options />);
}

export default Options;
