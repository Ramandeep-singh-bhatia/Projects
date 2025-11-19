import React, { useState } from 'react';
import { Coffee, MessageCircle, RotateCcw } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import aiService from '../../services/aiService';
import './LearningModules.css';

const SmallTalkPractice = () => {
  const { setLearningProgress, learningProgress } = useAppStore();
  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadScenario = async (difficulty) => {
    setLoading(true);
    try {
      const smallTalkScenario = await aiService.generateSmallTalkScenario(difficulty);
      setScenario(smallTalkScenario);
    } catch (error) {
      console.error('Error loading small talk scenario:', error);
      setScenario({
        situation: 'You are in an elevator with a colleague you don\'t know well.',
        starters: ['Nice weather today!', 'How\'s your day going?', 'Working on anything interesting?'],
        responses: ['Yes, it\'s beautiful!', 'Pretty good, thanks! How about you?', 'Just the usual. How about you?'],
        phrases: ['How about you?', 'That\'s interesting!', 'I know what you mean.'],
        tips: ['Be friendly and natural', 'Ask follow-up questions', 'Show genuine interest'],
        difficulty
      });
    } finally {
      setLoading(false);
    }
  };

  const resetScenario = () => {
    setScenario(null);
  };

  if (!scenario) {
    return (
      <div className="learning-module">
        <div className="module-header">
          <Coffee size={32} className="module-icon" />
          <div>
            <h1>Small Talk Mastery</h1>
            <p>Master the art of casual conversation</p>
          </div>
        </div>

        <div className="difficulty-selection">
          <h2>Choose Your Level</h2>
          <div className="difficulty-buttons">
            <button
              className="btn btn-outline difficulty-beginner"
              onClick={() => loadScenario('beginner')}
              disabled={loading}
            >
              Beginner
            </button>
            <button
              className="btn btn-outline difficulty-intermediate"
              onClick={() => loadScenario('intermediate')}
              disabled={loading}
            >
              Intermediate
            </button>
            <button
              className="btn btn-outline difficulty-advanced"
              onClick={() => loadScenario('advanced')}
              disabled={loading}
            >
              Advanced
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="learning-module">
      <div className="module-header">
        <div className="header-left">
          <Coffee size={32} className="module-icon" />
          <div>
            <h1>Small Talk Practice</h1>
            <span className={`difficulty-badge difficulty-${scenario.difficulty}`}>
              {scenario.difficulty}
            </span>
          </div>
        </div>
        <button className="btn btn-outline" onClick={resetScenario}>
          <RotateCcw size={18} />
          New Scenario
        </button>
      </div>

      <div className="small-talk-content">
        <div className="situation-box">
          <h3><MessageCircle size={20} /> Situation</h3>
          <p>{scenario.situation}</p>
        </div>

        <div className="tips-section">
          <h3>Tips for This Situation</h3>
          <ul className="tips-list">
            {scenario.tips.map((tip, index) => (
              <li key={index}>{tip}</li>
            ))}
          </ul>
        </div>

        <div className="starters-section">
          <h3>Conversation Starters</h3>
          <div className="phrase-cards">
            {scenario.starters.map((starter, index) => (
              <div key={index} className="phrase-card">
                <MessageCircle size={16} />
                <span>{starter}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="responses-section">
          <h3>Appropriate Responses</h3>
          <div className="phrase-cards">
            {scenario.responses.map((response, index) => (
              <div key={index} className="phrase-card response">
                <span>{response}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="phrases-section">
          <h3>Useful Phrases</h3>
          <div className="phrase-grid">
            {scenario.phrases.map((phrase, index) => (
              <div key={index} className="phrase-tag">
                {phrase}
              </div>
            ))}
          </div>
        </div>

        <div className="practice-prompt">
          <h3>Practice Exercise</h3>
          <p>
            Try role-playing this scenario! Use the conversation starters, responses, and phrases
            above. Practice with a friend or record yourself having this conversation.
          </p>
          <button
            className="btn btn-primary"
            onClick={resetScenario}
          >
            Try Another Scenario
          </button>
        </div>
      </div>
    </div>
  );
};

export default SmallTalkPractice;
