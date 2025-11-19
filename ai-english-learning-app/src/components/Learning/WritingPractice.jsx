import React, { useState } from 'react';
import { FileText, Send, Lightbulb } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import aiService from '../../services/aiService';
import './LearningModules.css';

const WritingPractice = () => {
  const { learningProgress, setLearningProgress, addExerciseToHistory, addMistake } = useAppStore();
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [userWriting, setUserWriting] = useState('');
  const [loading, setLoading] = useState(false);
  const [evaluation, setEvaluation] = useState(null);

  const prompts = [
    {
      id: 'daily_reflection',
      title: 'Daily Reflection',
      prompt: 'Describe your day today. What did you do? How did you feel?',
      category: 'personal',
      difficulty: 'beginner'
    },
    {
      id: 'professional_email',
      title: 'Professional Email',
      prompt: 'Write an email to a colleague asking them to collaborate on a project.',
      category: 'professional',
      difficulty: 'intermediate'
    },
    {
      id: 'opinion_essay',
      title: 'Opinion Essay',
      prompt: 'Do you think social media has more positive or negative effects on society? Explain your view.',
      category: 'academic',
      difficulty: 'advanced'
    },
    {
      id: 'story_writing',
      title: 'Creative Writing',
      prompt: 'Write a short story that begins with: "The door slowly creaked open..."',
      category: 'creative',
      difficulty: 'intermediate'
    },
    {
      id: 'product_review',
      title: 'Product Review',
      prompt: 'Write a review of your favorite product or service.',
      category: 'practical',
      difficulty: 'beginner'
    },
  ];

  const submitWriting = async () => {
    if (!userWriting.trim() || loading) return;

    setLoading(true);
    try {
      const result = await aiService.evaluateWriting(
        selectedPrompt.prompt,
        userWriting,
        selectedPrompt.category
      );

      setEvaluation(result);

      // Update progress
      const avgScore = (
        result.scores.grammar +
        result.scores.vocabulary +
        result.scores.clarity +
        result.scores.organization +
        result.scores.style
      ) / 5;

      const newScore = Math.round((learningProgress.writing_quality * 0.7) + (avgScore * 0.3));
      setLearningProgress({
        writing_quality: Math.min(100, newScore),
        grammar: Math.min(100, (learningProgress.grammar * 0.8) + (result.scores.grammar * 0.2)),
        vocabulary: Math.min(100, (learningProgress.vocabulary * 0.8) + (result.scores.vocabulary * 0.2))
      });

      // Save to history
      addExerciseToHistory({
        exercise_type: 'writing',
        exercise_data: JSON.stringify(selectedPrompt),
        user_response: userWriting,
        ai_feedback: JSON.stringify(result),
        score: result.overall_score,
        completed_at: new Date().toISOString()
      });

      // Add mistakes
      if (result.improvements) {
        result.improvements.forEach(improvement => {
          addMistake({
            mistake_type: 'writing',
            original_text: improvement.example || userWriting.substring(0, 100),
            corrected_text: improvement.suggestion || '',
            explanation: improvement.issue,
            occurred_at: new Date().toISOString()
          });
        });
      }
    } catch (error) {
      console.error('Error evaluating writing:', error);
      alert('Error evaluating your writing. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetWriting = () => {
    setSelectedPrompt(null);
    setUserWriting('');
    setEvaluation(null);
  };

  if (!selectedPrompt) {
    return (
      <div className="learning-module">
        <div className="module-header">
          <FileText size={32} className="module-icon" />
          <div>
            <h1>Writing Practice</h1>
            <p>Improve your writing with AI-powered feedback</p>
          </div>
        </div>

        <div className="prompts-grid">
          {prompts.map((prompt) => (
            <div
              key={prompt.id}
              className="prompt-card"
              onClick={() => setSelectedPrompt(prompt)}
            >
              <div className="prompt-header">
                <h3>{prompt.title}</h3>
                <span className={`badge badge-${prompt.category}`}>
                  {prompt.category}
                </span>
              </div>
              <p>{prompt.prompt}</p>
              <span className={`difficulty-badge difficulty-${prompt.difficulty}`}>
                {prompt.difficulty}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="learning-module">
      <div className="module-header">
        <div className="header-left">
          <FileText size={32} className="module-icon" />
          <div>
            <h1>{selectedPrompt.title}</h1>
            <span className={`difficulty-badge difficulty-${selectedPrompt.difficulty}`}>
              {selectedPrompt.difficulty}
            </span>
          </div>
        </div>
        <button className="btn btn-outline" onClick={resetWriting}>
          Choose Different Prompt
        </button>
      </div>

      <div className="writing-container">
        <div className="prompt-display">
          <h3>Writing Prompt</h3>
          <p>{selectedPrompt.prompt}</p>
        </div>

        <div className="writing-area">
          <textarea
            value={userWriting}
            onChange={(e) => setUserWriting(e.target.value)}
            placeholder="Start writing here..."
            rows={15}
            disabled={loading || evaluation}
          />
          <div className="word-count">
            Word count: {userWriting.trim().split(/\s+/).filter(w => w).length}
          </div>
        </div>

        {!evaluation ? (
          <button
            className="btn btn-primary btn-lg"
            onClick={submitWriting}
            disabled={!userWriting.trim() || loading}
          >
            {loading ? 'Evaluating...' : <><Send size={18} /> Submit for Review</>}
          </button>
        ) : (
          <>
            <div className="evaluation-results">
              <div className="overall-score-display">
                <div className="score-circle">
                  <div className="score-value">{evaluation.overall_score}</div>
                  <div className="score-label">Overall</div>
                </div>
              </div>

              <div className="skill-scores">
                {Object.entries(evaluation.scores).map(([skill, score]) => (
                  <div key={skill} className="skill-score-item">
                    <span className="skill-label">{skill.replace('_', ' ')}</span>
                    <div className="score-bar">
                      <div className="score-fill" style={{ width: `${score}%` }} />
                    </div>
                    <span className="score-value">{score}</span>
                  </div>
                ))}
              </div>

              {evaluation.strengths && evaluation.strengths.length > 0 && (
                <div className="feedback-section success">
                  <h4><Lightbulb size={20} /> Strengths</h4>
                  {evaluation.strengths.map((strength, i) => (
                    <div key={i} className="feedback-item">
                      <strong>{strength.point}</strong>
                      {strength.example && <p className="example">Example: "{strength.example}"</p>}
                    </div>
                  ))}
                </div>
              )}

              {evaluation.improvements && evaluation.improvements.length > 0 && (
                <div className="feedback-section warning">
                  <h4>Areas for Improvement</h4>
                  {evaluation.improvements.map((improvement, i) => (
                    <div key={i} className="feedback-item">
                      <strong>{improvement.issue}</strong>
                      {improvement.example && <p className="example">In your text: "{improvement.example}"</p>}
                      {improvement.suggestion && <p className="suggestion">Suggestion: {improvement.suggestion}</p>}
                    </div>
                  ))}
                </div>
              )}

              {evaluation.corrected_version && (
                <div className="corrected-version">
                  <h4>Improved Version</h4>
                  <p>{evaluation.corrected_version}</p>
                </div>
              )}

              {evaluation.vocabulary_suggestions && evaluation.vocabulary_suggestions.length > 0 && (
                <div className="feedback-section info">
                  <h4>Vocabulary Suggestions</h4>
                  {evaluation.vocabulary_suggestions.map((vocab, i) => (
                    <div key={i} className="vocab-suggestion">
                      <strong>{vocab.word}</strong>: {vocab.definition}
                      {vocab.usage && <p className="usage-example">{vocab.usage}</p>}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button className="btn btn-primary" onClick={resetWriting}>
              Try Another Prompt
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default WritingPractice;
