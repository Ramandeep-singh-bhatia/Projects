import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import useAppStore from './stores/appStore';

// Layout components
import Navigation from './components/Common/Navigation';
import Settings from './components/Common/Settings';

// Main views
import Dashboard from './components/Dashboard/Dashboard';
import Assessment from './components/Assessment/Assessment';
import ConversationPractice from './components/Learning/ConversationPractice';
import VocabularyPractice from './components/Learning/VocabularyPractice';
import GrammarPractice from './components/Learning/GrammarPractice';
import WritingPractice from './components/Learning/WritingPractice';
import SmallTalkPractice from './components/Learning/SmallTalkPractice';
import WeeklyChallenge from './components/Learning/WeeklyChallenge';
import Review from './components/Review/Review';
import MistakesJournal from './components/Review/MistakesJournal';

import './App.css';

function App() {
  const { user, aiConfig } = useAppStore();
  const [showSettings, setShowSettings] = useState(false);
  const [needsApiKey, setNeedsApiKey] = useState(false);

  useEffect(() => {
    // Check if we need to prompt for API key
    if (!aiConfig.useLocalModel && !aiConfig.apiKey) {
      const storedKey = localStorage.getItem('anthropic_api_key');
      if (!storedKey) {
        setNeedsApiKey(true);
      }
    }
  }, [aiConfig]);

  return (
    <Router>
      <div className="app">
        <Navigation onSettingsClick={() => setShowSettings(true)} />

        <main className="main-content">
          <Routes>
            <Route
              path="/"
              element={
                user.hasCompletedAssessment ? (
                  <Dashboard />
                ) : (
                  <Navigate to="/assessment" replace />
                )
              }
            />
            <Route path="/assessment" element={<Assessment />} />
            <Route path="/conversation" element={<ConversationPractice />} />
            <Route path="/vocabulary" element={<VocabularyPractice />} />
            <Route path="/grammar" element={<GrammarPractice />} />
            <Route path="/writing" element={<WritingPractice />} />
            <Route path="/small-talk" element={<SmallTalkPractice />} />
            <Route path="/challenge" element={<WeeklyChallenge />} />
            <Route path="/review" element={<Review />} />
            <Route path="/mistakes" element={<MistakesJournal />} />
          </Routes>
        </main>

        {showSettings && <Settings onClose={() => setShowSettings(false)} />}

        {needsApiKey && !aiConfig.useLocalModel && (
          <div className="api-key-prompt-overlay">
            <div className="api-key-prompt">
              <h2>Welcome to AI English Learning!</h2>
              <p>
                To get started, you'll need to configure an AI service. You can either:
              </p>
              <ul>
                <li>Use Claude API (requires API key from Anthropic)</li>
                <li>Use a local model with Ollama (free, runs on your computer)</li>
              </ul>
              <button
                className="btn btn-primary"
                onClick={() => {
                  setNeedsApiKey(false);
                  setShowSettings(true);
                }}
              >
                Configure AI Service
              </button>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;
