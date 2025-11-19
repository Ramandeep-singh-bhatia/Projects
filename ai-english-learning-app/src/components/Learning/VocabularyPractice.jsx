import React, { useState, useEffect } from 'react';
import { BookOpen, RefreshCw, Check, X } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import aiService from '../../services/aiService';
import './LearningModules.css';

const VocabularyPractice = () => {
  const { user, learningProgress, setLearningProgress, addExerciseToHistory } = useAppStore();
  const [exercise, setExercise] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userAnswer, setUserAnswer] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const difficulties = ['beginner', 'intermediate', 'advanced'];

  const loadExercise = async (difficulty) => {
    setLoading(true);
    setShowFeedback(false);
    setUserAnswer('');

    try {
      const vocabExercise = await aiService.generateVocabularyExercise(difficulty);
      setExercise(vocabExercise);
    } catch (error) {
      console.error('Error loading vocabulary exercise:', error);
      setExercise({
        title: 'Vocabulary Practice',
        scenario: 'Practice using new vocabulary words in context.',
        vocabulary: [
          { word: 'eloquent', definition: 'Fluent and persuasive in speaking or writing', example: 'She gave an eloquent speech.' },
          { word: 'meticulous', definition: 'Showing great attention to detail', example: 'He is meticulous in his work.' }
        ],
        task: 'Write a short paragraph using these vocabulary words in a natural way.',
        difficulty: difficulty
      });
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!userAnswer.trim()) return;

    setLoading(true);
    try {
      // Evaluate the answer
      const evaluation = await aiService.chat(
        `Evaluate this vocabulary usage:\n\nTask: ${exercise.task}\nVocabulary: ${exercise.vocabulary.map(v => v.word).join(', ')}\n\nStudent's response: "${userAnswer}"\n\nProvide feedback in JSON format: {"score": 0-100, "correct_usage": ["..."], "mistakes": ["..."], "suggestions": ["..."]}`,
        { exerciseType: 'vocabulary' }
      );

      const jsonMatch = evaluation.match(/\{[\s\S]*\}/);
      const feedbackData = jsonMatch ? JSON.parse(jsonMatch[0]) : {
        score: 70,
        correct_usage: ['Good effort!'],
        mistakes: [],
        suggestions: ['Keep practicing!']
      };

      setFeedback(feedbackData);
      setShowFeedback(true);

      // Update progress
      const newScore = Math.round((learningProgress.vocabulary * 0.7) + (feedbackData.score * 0.3));
      setLearningProgress({ vocabulary: Math.min(100, newScore) });

      // Save to history
      addExerciseToHistory({
        exercise_type: 'vocabulary',
        exercise_data: JSON.stringify(exercise),
        user_response: userAnswer,
        ai_feedback: evaluation,
        score: feedbackData.score,
        completed_at: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error submitting answer:', error);
      setFeedback({
        score: 70,
        correct_usage: ['Good attempt at using new vocabulary!'],
        mistakes: [],
        suggestions: ['Continue practicing to improve your vocabulary usage.']
      });
      setShowFeedback(true);
    } finally {
      setLoading(false);
    }
  };

  const resetExercise = () => {
    setShowFeedback(false);
    setUserAnswer('');
    setFeedback(null);
  };

  if (!exercise) {
    return (
      <div className="learning-module">
        <div className="module-header">
          <BookOpen size={32} className="module-icon" />
          <div>
            <h1>Vocabulary Practice</h1>
            <p>Learn new words through contextual usage</p>
          </div>
        </div>

        <div className="difficulty-selection">
          <h2>Choose Your Difficulty Level</h2>
          <div className="difficulty-buttons">
            {difficulties.map((diff) => (
              <button
                key={diff}
                className={`btn btn-outline difficulty-${diff}`}
                onClick={() => loadExercise(diff)}
                disabled={loading}
              >
                {diff}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="learning-module">
      <div className="module-header">
        <div className="header-left">
          <BookOpen size={32} className="module-icon" />
          <div>
            <h1>{exercise.title}</h1>
            <span className={`difficulty-badge difficulty-${exercise.difficulty}`}>
              {exercise.difficulty}
            </span>
          </div>
        </div>
        <button className="btn btn-outline" onClick={() => setExercise(null)}>
          <RefreshCw size={18} />
          Change Level
        </button>
      </div>

      <div className="exercise-content">
        <div className="scenario-box">
          <h3>Scenario</h3>
          <p>{exercise.scenario}</p>
        </div>

        <div className="vocabulary-list">
          <h3>Vocabulary Words</h3>
          {exercise.vocabulary.map((vocab, index) => (
            <div key={index} className="vocab-item">
              <div className="vocab-word">{vocab.word}</div>
              <div className="vocab-definition">{vocab.definition}</div>
              <div className="vocab-example">
                <em>Example: {vocab.example}</em>
              </div>
            </div>
          ))}
        </div>

        <div className="task-box">
          <h3>Your Task</h3>
          <p>{exercise.task}</p>
        </div>

        <div className="answer-section">
          <textarea
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            placeholder="Write your answer here..."
            rows={8}
            disabled={showFeedback}
          />

          <div className="action-buttons">
            {!showFeedback ? (
              <button
                className="btn btn-primary"
                onClick={submitAnswer}
                disabled={!userAnswer.trim() || loading}
              >
                {loading ? 'Evaluating...' : 'Submit Answer'}
              </button>
            ) : (
              <button className="btn btn-primary" onClick={resetExercise}>
                <RefreshCw size={18} />
                Try Another Exercise
              </button>
            )}
          </div>
        </div>

        {showFeedback && feedback && (
          <div className="feedback-box">
            <div className="feedback-score-large">
              Score: {feedback.score}/100
              {feedback.score >= 80 ? <Check className="score-icon success" /> : <X className="score-icon warning" />}
            </div>

            {feedback.correct_usage && feedback.correct_usage.length > 0 && (
              <div className="feedback-section success">
                <h4>Correct Usage</h4>
                <ul>
                  {feedback.correct_usage.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {feedback.mistakes && feedback.mistakes.length > 0 && (
              <div className="feedback-section warning">
                <h4>Areas to Improve</h4>
                <ul>
                  {feedback.mistakes.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {feedback.suggestions && feedback.suggestions.length > 0 && (
              <div className="feedback-section info">
                <h4>Suggestions</h4>
                <ul>
                  {feedback.suggestions.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VocabularyPractice;
