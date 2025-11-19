import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, RotateCcw, Mic, MicOff, Lightbulb } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import aiService from '../../services/aiService';
import './LearningModules.css';

const ConversationPractice = () => {
  const { user, setLearningProgress, learningProgress, addExerciseToHistory, addMistake } = useAppStore();
  const [scenario, setScenario] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);

  const scenarios = [
    { id: 'restaurant', title: 'Ordering at a Restaurant', difficulty: 'beginner' },
    { id: 'job_interview', title: 'Job Interview', difficulty: 'intermediate' },
    { id: 'small_talk', title: 'Small Talk at Coffee Shop', difficulty: 'beginner' },
    { id: 'business_meeting', title: 'Business Meeting', difficulty: 'advanced' },
    { id: 'shopping', title: 'Shopping for Clothes', difficulty: 'beginner' },
    { id: 'doctor', title: 'At the Doctor\'s Office', difficulty: 'intermediate' },
  ];

  useEffect(() => {
    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };

      recognitionInstance.onerror = () => {
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }
  }, []);

  const startScenario = async (selectedScenario) => {
    setScenario(selectedScenario);
    setMessages([]);
    setFeedback(null);
    setLoading(true);

    try {
      const scenarioDescription = `${selectedScenario.title} - A ${selectedScenario.difficulty} level conversation scenario.`;
      const aiResponse = await aiService.chat(
        `Start a conversation scenario: ${scenarioDescription}. Provide the initial situation and your first message as the other person in the conversation.`,
        { exerciseType: 'conversation', scenario: scenarioDescription }
      );

      setMessages([{ role: 'ai', message: aiResponse }]);
    } catch (error) {
      console.error('Error starting scenario:', error);
      setMessages([{
        role: 'ai',
        message: `Welcome to ${selectedScenario.title}! I'll be playing the other person in this conversation. Let's start - how can I help you today?`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setMessages((prev) => [...prev, { role: 'user', message: userMessage }]);
    setLoading(true);

    try {
      const evaluation = await aiService.evaluateConversationResponse(
        scenario.title,
        userMessage,
        messages
      );

      setMessages((prev) => [...prev, { role: 'ai', message: evaluation.next_message }]);
      setFeedback(evaluation);

      // Update progress
      const newScore = Math.round((learningProgress.fluency * 0.7) + (evaluation.score * 0.3));
      setLearningProgress({ fluency: Math.min(100, newScore) });

      // Save exercise history
      addExerciseToHistory({
        exercise_type: 'conversation',
        user_response: userMessage,
        ai_feedback: JSON.stringify(evaluation),
        score: evaluation.score,
        completed_at: new Date().toISOString()
      });

      // Add mistakes if any
      if (evaluation.improvements && evaluation.improvements.length > 0) {
        evaluation.improvements.forEach(improvement => {
          addMistake({
            mistake_type: 'conversation',
            original_text: userMessage,
            explanation: improvement,
            occurred_at: new Date().toISOString()
          });
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [...prev, {
        role: 'ai',
        message: 'That\'s interesting! Can you tell me more about that?'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const toggleListening = () => {
    if (!recognition) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  const resetScenario = () => {
    setScenario(null);
    setMessages([]);
    setFeedback(null);
  };

  if (!scenario) {
    return (
      <div className="learning-module">
        <div className="module-header">
          <MessageSquare size={32} className="module-icon" />
          <div>
            <h1>Conversation Practice</h1>
            <p>Practice real-world conversations with AI-powered scenarios</p>
          </div>
        </div>

        <div className="scenarios-grid">
          {scenarios.map((s) => (
            <div
              key={s.id}
              className="scenario-card"
              onClick={() => startScenario(s)}
            >
              <h3>{s.title}</h3>
              <span className={`difficulty-badge difficulty-${s.difficulty}`}>
                {s.difficulty}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="learning-module conversation-module">
      <div className="module-header">
        <div className="header-left">
          <MessageSquare size={32} className="module-icon" />
          <div>
            <h1>{scenario.title}</h1>
            <span className={`difficulty-badge difficulty-${scenario.difficulty}`}>
              {scenario.difficulty}
            </span>
          </div>
        </div>
        <button className="btn btn-outline" onClick={resetScenario}>
          <RotateCcw size={18} />
          Change Scenario
        </button>
      </div>

      <div className="conversation-container">
        <div className="messages-area">
          {messages.map((msg, index) => (
            <div key={index} className={`message message-${msg.role}`}>
              <div className="message-content">{msg.message}</div>
            </div>
          ))}
          {loading && (
            <div className="message message-ai">
              <div className="message-content typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>

        {feedback && (
          <div className="feedback-panel">
            <div className="feedback-header">
              <Lightbulb size={20} />
              <span>AI Feedback</span>
            </div>
            <div className="feedback-score">Score: {feedback.score}/100</div>
            {feedback.good_points && feedback.good_points.length > 0 && (
              <div className="feedback-section">
                <strong>What you did well:</strong>
                <ul>
                  {feedback.good_points.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
            {feedback.improvements && feedback.improvements.length > 0 && (
              <div className="feedback-section">
                <strong>Room for improvement:</strong>
                <ul>
                  {feedback.improvements.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
            {feedback.alternatives && feedback.alternatives.length > 0 && (
              <div className="feedback-section">
                <strong>Alternative ways to say it:</strong>
                <ul>
                  {feedback.alternatives.map((alt, i) => (
                    <li key={i}>{alt}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="input-area">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Type your response..."
            rows={3}
            disabled={loading}
          />
          <div className="input-actions">
            {recognition && (
              <button
                className={`btn btn-outline ${isListening ? 'listening' : ''}`}
                onClick={toggleListening}
              >
                {isListening ? <MicOff size={18} /> : <Mic size={18} />}
              </button>
            )}
            <button
              className="btn btn-primary"
              onClick={sendMessage}
              disabled={!inputMessage.trim() || loading}
            >
              <Send size={18} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationPractice;
