/**
 * Popup Component
 * Main UI when clicking extension icon
 */

import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Storage } from '../shared/utils/storage';
import { backendClient } from '../shared/api/backend-client';
import { MessageType } from '../shared/types';
import type { UserProfile, FormField } from '../shared/types';

const Popup: React.FC = () => {
  const [backendConnected, setBackendConnected] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [detectedFields, setDetectedFields] = useState<FormField[]>([]);
  const [loading, setLoading] = useState(true);
  const [filling, setFilling] = useState(false);

  useEffect(() => {
    init();
  }, []);

  const init = async () => {
    // Check backend connection
    const settings = await Storage.getSettings();
    if (settings) {
      backendClient.setBaseURL(settings.backendUrl);
    }

    const connected = await backendClient.healthCheck();
    setBackendConnected(connected);

    // Load profile
    if (connected) {
      const profileResponse = await backendClient.getProfile();
      if (profileResponse.data) {
        setProfile(profileResponse.data);
      }
    }

    // Load detected fields from current page
    const stored = await chrome.storage.local.get(['detected_fields', 'detected_platform']);
    if (stored.detected_fields) {
      setDetectedFields(stored.detected_fields);
    }

    setLoading(false);
  };

  const handleFillForm = async () => {
    setFilling(true);

    try {
      // Get active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      if (!tab.id) {
        alert('No active tab found');
        return;
      }

      // Send fill message to content script
      await chrome.tabs.sendMessage(tab.id, {
        type: MessageType.FILL_FORM,
        payload: {},
      });

      // Show success
      setTimeout(() => {
        setFilling(false);
      }, 1000);
    } catch (error) {
      console.error('Fill form error:', error);
      alert('Failed to fill form. Make sure you\'re on a job application page.');
      setFilling(false);
    }
  };

  const openOptions = () => {
    chrome.runtime.openOptionsPage();
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.title}>JobFlow</h2>
        </div>
        <div style={styles.loading}>Loading...</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>🚀 JobFlow</h2>
        <div style={styles.status}>
          <span style={{
            ...styles.statusDot,
            backgroundColor: backendConnected ? '#10B981' : '#EF4444'
          }} />
          <span style={styles.statusText}>
            {backendConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div style={styles.content}>
        {!backendConnected && (
          <div style={styles.warning}>
            <p>⚠️ Backend not connected</p>
            <p style={styles.warningText}>
              Make sure the backend server is running at localhost:8000
            </p>
            <button onClick={openOptions} style={styles.linkButton}>
              Open Settings
            </button>
          </div>
        )}

        {!profile && backendConnected && (
          <div style={styles.warning}>
            <p>📋 No profile found</p>
            <p style={styles.warningText}>
              Please create your profile first
            </p>
            <button onClick={openOptions} style={styles.linkButton}>
              Setup Profile
            </button>
          </div>
        )}

        {profile && (
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Profile</h3>
            <p style={styles.profileName}>
              {profile.first_name} {profile.last_name}
            </p>
            <p style={styles.profileDetail}>{profile.email}</p>
          </div>
        )}

        {detectedFields.length > 0 && (
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>Detected Form</h3>
            <p style={styles.detail}>
              {detectedFields.length} fields detected
            </p>
            <button
              onClick={handleFillForm}
              disabled={filling || !profile}
              style={{
                ...styles.button,
                ...(!profile ? styles.buttonDisabled : {})
              }}
            >
              {filling ? 'Filling...' : 'Fill Form'}
            </button>
          </div>
        )}

        {detectedFields.length === 0 && profile && (
          <div style={styles.info}>
            <p>Navigate to a job application page to detect forms</p>
          </div>
        )}
      </div>

      <div style={styles.footer}>
        <button onClick={openOptions} style={styles.footerButton}>
          Settings
        </button>
        <button
          onClick={() => window.open('http://localhost:8000/docs')}
          style={styles.footerButton}
        >
          API Docs
        </button>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '350px',
    minHeight: '400px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    backgroundColor: '#FFFFFF',
  },
  header: {
    padding: '16px',
    borderBottom: '1px solid #E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  title: {
    margin: 0,
    fontSize: '20px',
    fontWeight: '600',
    color: '#111827',
  },
  status: {
    display: 'flex',
    alignItems: 'center',
    marginTop: '8px',
    fontSize: '12px',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    marginRight: '6px',
  },
  statusText: {
    color: '#6B7280',
  },
  content: {
    padding: '16px',
  },
  section: {
    marginBottom: '16px',
  },
  sectionTitle: {
    margin: '0 0 8px 0',
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
  },
  profileName: {
    margin: '4px 0',
    fontSize: '14px',
    fontWeight: '500',
    color: '#111827',
  },
  profileDetail: {
    margin: '2px 0',
    fontSize: '12px',
    color: '#6B7280',
  },
  detail: {
    margin: '4px 0',
    fontSize: '14px',
    color: '#6B7280',
  },
  button: {
    width: '100%',
    padding: '10px 16px',
    marginTop: '12px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#FFFFFF',
    backgroundColor: '#3B82F6',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  buttonDisabled: {
    backgroundColor: '#9CA3AF',
    cursor: 'not-allowed',
  },
  warning: {
    padding: '12px',
    marginBottom: '16px',
    backgroundColor: '#FEF3C7',
    borderRadius: '6px',
    fontSize: '13px',
  },
  warningText: {
    margin: '8px 0',
    fontSize: '12px',
    color: '#92400E',
  },
  info: {
    padding: '12px',
    backgroundColor: '#EFF6FF',
    borderRadius: '6px',
    fontSize: '13px',
    color: '#1E40AF',
    textAlign: 'center' as const,
  },
  linkButton: {
    padding: '6px 12px',
    marginTop: '8px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#3B82F6',
    backgroundColor: 'transparent',
    border: '1px solid #3B82F6',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  loading: {
    padding: '40px',
    textAlign: 'center' as const,
    color: '#6B7280',
  },
  footer: {
    display: 'flex',
    gap: '8px',
    padding: '12px 16px',
    borderTop: '1px solid #E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  footerButton: {
    flex: 1,
    padding: '8px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#6B7280',
    backgroundColor: 'transparent',
    border: '1px solid #D1D5DB',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};

// Render
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<Popup />);
}

export default Popup;
