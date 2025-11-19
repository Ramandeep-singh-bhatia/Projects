import React, { useState, useEffect } from 'react';
import { Award, Trophy, Clock, Target } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import aiService from '../../services/aiService';
import './LearningModules.css';

const WeeklyChallenge = () => {
  const { user, addExerciseToHistory } = useAppStore();
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [evaluation, setEvaluation] = useState(null);

  useEffect(() => {
    loadChallenge();
  }, []);

  const loadChallenge = async () => {
    setLoading(true);
    try {
      const weeklyChallenge = await aiService.generateWeeklyChallenge(user.currentLevel);
      setChallenge(weeklyChallenge);
    } catch (error) {
      console.error('Error loading challenge:', error);
      setChallenge({
        title: 'Weekly Writing Challenge',
        type: 'creative_writing',
        description: 'Write a creative piece based on the prompt below.',
        instructions: [
          'Write at least 150 words',
          'Use varied vocabulary',
          'Check your grammar before submitting'
        ],
        success_criteria: [
          'Meets minimum word count',
          'Uses appropriate vocabulary',
          'Has clear structure',
          'Contains minimal grammar errors'
        ],
        difficulty: user.currentLevel,
        estimated_time: '20 minutes',
        learning_objectives: ['Creative writing', 'Vocabulary usage', 'Grammar accuracy']
      });
    } finally {
      setLoading(false);
    }
  };

  const submitChallenge = async () => {
    if (!response.trim() || loading) return;

    setLoading(true);
    try {
      const evalPrompt = `Evaluate this weekly challenge submission:
Challenge: ${challenge.title}
Success Criteria: ${challenge.success_criteria.join(', ')}

Student's response: "${response}"

Provide detailed feedback in JSON format: {
  "score": 0-100,
  "criteria_met": ["..."],
  "criteria_not_met": ["..."],
  "strengths": ["..."],
  "improvements": ["..."],
  "overall_feedback": "..."
}`;

      const evalResponse = await aiService.chat(evalPrompt, {
        exerciseType: 'weekly_challenge',
        userLevel: user.currentLevel
      });

      const jsonMatch = evalResponse.match(/\{[\s\S]*\}/);
      const evalData = jsonMatch ? JSON.parse(jsonMatch[0]) : {
        score: 75,
        criteria_met: ['Good effort!'],
        criteria_not_met: [],
        strengths: ['Completed the challenge'],
        improvements: ['Keep practicing'],
        overall_feedback: 'Well done on completing this week\'s challenge!'
      };

      setEvaluation(evalData);
      setSubmitted(true);

      // Save to history
      addExerciseToHistory({
        exercise_type: 'weekly_challenge',
        exercise_data: JSON.stringify(challenge),
        user_response: response,
        ai_feedback: evalResponse,
        score: evalData.score,
        completed_at: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error submitting challenge:', error);
      alert('Error submitting challenge. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !challenge) {
    return (
      <div className="learning-module loading-state">
        <div className="loading-spinner" />
        <p>Loading this week's challenge...</p>
      </div>
    );
  }

  return (
    <div className="learning-module">
      <div className="module-header">
        <div className="header-left">
          <Award size={32} className="module-icon" />
          <div>
            <h1>Weekly Challenge</h1>
            <p>Push your limits and earn achievements</p>
          </div>
        </div>
      </div>

      {challenge && (
        <div className="challenge-container">
          <div className="challenge-header-card">
            <div className="challenge-icon">
              <Trophy size={48} />
            </div>
            <h2>{challenge.title}</h2>
            <div className="challenge-meta">
              <span className={`badge badge-primary`}>{challenge.type.replace('_', ' ')}</span>
              <span className={`difficulty-badge difficulty-${challenge.difficulty}`}>
                {challenge.difficulty}
              </span>
            </div>
          </div>

          <div className="challenge-details">
            <div className="detail-item">
              <Clock size={20} />
              <span>Estimated time: {challenge.estimated_time}</span>
            </div>
            <div className="detail-item">
              <Target size={20} />
              <span>Objectives: {challenge.learning_objectives.join(', ')}</span>
            </div>
          </div>

          <div className="challenge-description">
            <h3>Challenge Description</h3>
            <p>{challenge.description}</p>
          </div>

          <div className="challenge-instructions">
            <h3>Instructions</h3>
            <ol>
              {challenge.instructions.map((instruction, index) => (
                <li key={index}>{instruction}</li>
              ))}
            </ol>
          </div>

          <div className="success-criteria">
            <h3>Success Criteria</h3>
            <ul>
              {challenge.success_criteria.map((criteria, index) => (
                <li key={index}>{criteria}</li>
              ))}
            </ul>
          </div>

          {!submitted ? (
            <>
              <div className="response-area">
                <h3>Your Response</h3>
                <textarea
                  value={response}
                  onChange={(e) => setResponse(e.target.value)}
                  placeholder="Type your response here..."
                  rows={12}
                />
                <div className="word-count">
                  Words: {response.trim().split(/\s+/).filter(w => w).length}
                </div>
              </div>

              <button
                className="btn btn-primary btn-lg"
                onClick={submitChallenge}
                disabled={!response.trim() || loading}
              >
                {loading ? 'Submitting...' : 'Submit Challenge'}
              </button>
            </>
          ) : (
            <div className="challenge-results">
              <div className="results-header">
                <Trophy size={48} className="trophy-icon" />
                <h2>Challenge Complete!</h2>
                <div className="score-display">
                  {evaluation.score}/100
                </div>
              </div>

              {evaluation.criteria_met && evaluation.criteria_met.length > 0 && (
                <div className="feedback-section success">
                  <h4>✓ Criteria Met</h4>
                  <ul>
                    {evaluation.criteria_met.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {evaluation.criteria_not_met && evaluation.criteria_not_met.length > 0 && (
                <div className="feedback-section warning">
                  <h4>Areas for Improvement</h4>
                  <ul>
                    {evaluation.criteria_not_met.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {evaluation.strengths && evaluation.strengths.length > 0 && (
                <div className="feedback-section info">
                  <h4>Your Strengths</h4>
                  <ul>
                    {evaluation.strengths.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="overall-feedback">
                <h4>Overall Feedback</h4>
                <p>{evaluation.overall_feedback}</p>
              </div>

              <button className="btn btn-primary" onClick={() => window.location.reload()}>
                View Next Week's Challenge
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WeeklyChallenge;
