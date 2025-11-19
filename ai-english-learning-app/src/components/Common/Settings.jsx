import React, { useState } from 'react';
import { X, Save, Download, Upload } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import aiService from '../../services/aiService';
import './Settings.css';

const Settings = ({ onClose }) => {
  const { aiConfig, settings, setAIConfig, updateSettings, resetProgress } = useAppStore();
  const [apiKey, setApiKey] = useState(aiConfig.apiKey || '');
  const [useLocal, setUseLocal] = useState(aiConfig.useLocalModel);
  const [showConfirmReset, setShowConfirmReset] = useState(false);

  const handleSave = () => {
    if (!useLocal && apiKey) {
      aiService.setApiKey(apiKey);
      setAIConfig({ apiKey, useLocalModel: false });
    } else if (useLocal) {
      setAIConfig({ useLocalModel: true });
      aiService.setUseLocalModel(true);
    }
    onClose();
  };

  const handleExport = () => {
    const data = JSON.stringify(localStorage, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `english-learning-backup-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          Object.keys(data).forEach((key) => {
            localStorage.setItem(key, data[key]);
          });
          alert('Data imported successfully! Please refresh the page.');
        } catch (error) {
          alert('Error importing data. Please check the file format.');
        }
      };
      reader.readAsText(file);
    }
  };

  const handleReset = () => {
    if (showConfirmReset) {
      resetProgress();
      setShowConfirmReset(false);
      alert('Progress has been reset!');
      window.location.reload();
    } else {
      setShowConfirmReset(true);
    }
  };

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="settings-content">
          <section className="settings-section">
            <h3>AI Configuration</h3>
            <div className="setting-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={useLocal}
                  onChange={(e) => setUseLocal(e.target.checked)}
                />
                <span>Use Local Model (Ollama)</span>
              </label>
              <p className="setting-description">
                Run AI models locally on your computer. Requires Ollama to be installed and running.
              </p>
            </div>

            {!useLocal && (
              <div className="setting-item">
                <label>Claude API Key</label>
                <input
                  type="password"
                  placeholder="sk-ant-..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
                <p className="setting-description">
                  Get your API key from{' '}
                  <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer">
                    console.anthropic.com
                  </a>
                </p>
              </div>
            )}
          </section>

          <section className="settings-section">
            <h3>Learning Preferences</h3>
            <div className="setting-item">
              <label>Daily Goal (minutes)</label>
              <input
                type="number"
                min="5"
                max="120"
                value={settings.dailyGoalMinutes}
                onChange={(e) =>
                  updateSettings({ dailyGoalMinutes: parseInt(e.target.value) })
                }
              />
            </div>

            <div className="setting-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={settings.notificationsEnabled}
                  onChange={(e) =>
                    updateSettings({ notificationsEnabled: e.target.checked })
                  }
                />
                <span>Enable Notifications</span>
              </label>
            </div>
          </section>

          <section className="settings-section">
            <h3>Data Management</h3>
            <div className="setting-actions">
              <button className="btn btn-outline" onClick={handleExport}>
                <Download size={18} />
                Export Progress
              </button>

              <label className="btn btn-outline">
                <Upload size={18} />
                Import Progress
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImport}
                  style={{ display: 'none' }}
                />
              </label>

              <button
                className={`btn ${showConfirmReset ? 'btn-danger' : 'btn-secondary'}`}
                onClick={handleReset}
              >
                {showConfirmReset ? 'Confirm Reset?' : 'Reset Progress'}
              </button>
            </div>
          </section>
        </div>

        <div className="settings-footer">
          <button className="btn btn-primary" onClick={handleSave}>
            <Save size={18} />
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
