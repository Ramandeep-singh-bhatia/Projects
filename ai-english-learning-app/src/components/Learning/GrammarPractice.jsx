import React, { useState } from 'react';
import { BookText, RotateCcw } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import aiService from '../../services/aiService';
import './LearningModules.css';

const GrammarPractice = () => {
  const { learningProgress, setLearningProgress, addExerciseToHistory } = useAppStore();
  const [exercise, setExercise] = useState(null);
  const [loading, setLoading] = useState(false);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);

  const topics = [
    { id: 'present_perfect', title: 'Present Perfect Tense', difficulty: 'intermediate' },
    { id: 'conditionals', title: 'Conditional Sentences', difficulty: 'intermediate' },
    { id: 'passive_voice', title: 'Passive Voice', difficulty: 'advanced' },
    { id: 'articles', title: 'Articles (a, an, the)', difficulty: 'beginner' },
    { id: 'prepositions', title: 'Prepositions', difficulty: 'beginner' },
    { id: 'modal_verbs', title: 'Modal Verbs', difficulty: 'intermediate' },
  ];

  const loadTopic = async (topic) => {
    setLoading(true);
    setShowResults(false);
    setAnswers({});

    try {
      const grammarExercise = await aiService.generateGrammarExercise(topic.title, topic.difficulty);
      setExercise({ ...grammarExercise, topic });
    } catch (error) {
      console.error('Error loading grammar exercise:', error);
      // Fallback exercise
      setExercise({
        title: topic.title,
        rule_explanation: 'Practice grammar rules and usage.',
        examples: ['Example sentence 1', 'Example sentence 2'],
        practice_items: [
          { sentence: 'I have been to Paris.', is_correct: true, correction: '' },
          { sentence: 'She has went to the store.', is_correct: false, correction: 'She has gone to the store.' }
        ],
        usage_context: 'Use this grammar in various contexts.',
        difficulty: topic.difficulty,
        topic
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (index, value) => {
    setAnswers(prev => ({ ...prev, [index]: value }));
  };

  const submitAnswers = () => {
    let correctCount = 0;
    exercise.practice_items.forEach((item, index) => {
      const userAnswer = answers[index];
      const isCorrect = (userAnswer === 'correct' && item.is_correct) ||
                       (userAnswer === 'incorrect' && !item.is_correct);
      if (isCorrect) correctCount++;
    });

    const finalScore = Math.round((correctCount / exercise.practice_items.length) * 100);
    setScore(finalScore);
    setShowResults(true);

    // Update progress
    const newScore = Math.round((learningProgress.grammar * 0.7) + (finalScore * 0.3));
    setLearningProgress({ grammar: Math.min(100, newScore) });

    // Save to history
    addExerciseToHistory({
      exercise_type: 'grammar',
      exercise_data: JSON.stringify(exercise),
      user_response: JSON.stringify(answers),
      score: finalScore,
      completed_at: new Date().toISOString()
    });
  };

  const resetExercise = () => {
    setExercise(null);
    setAnswers({});
    setShowResults(false);
  };

  if (!exercise) {
    return (
      <div className="learning-module">
        <div className="module-header">
          <BookText size={32} className="module-icon" />
          <div>
            <h1>Grammar Practice</h1>
            <p>Master English grammar rules through practice</p>
          </div>
        </div>

        <div className="topics-grid">
          {topics.map((topic) => (
            <div
              key={topic.id}
              className="topic-card"
              onClick={() => loadTopic(topic)}
            >
              <h3>{topic.title}</h3>
              <span className={`difficulty-badge difficulty-${topic.difficulty}`}>
                {topic.difficulty}
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
          <BookText size={32} className="module-icon" />
          <div>
            <h1>{exercise.title}</h1>
            <span className={`difficulty-badge difficulty-${exercise.difficulty}`}>
              {exercise.difficulty}
            </span>
          </div>
        </div>
        <button className="btn btn-outline" onClick={resetExercise}>
          <RotateCcw size={18} />
          Change Topic
        </button>
      </div>

      <div className="exercise-content">
        <div className="grammar-rule">
          <h3>Grammar Rule</h3>
          <p>{exercise.rule_explanation}</p>
        </div>

        <div className="grammar-examples">
          <h3>Examples</h3>
          <ul>
            {exercise.examples.map((example, index) => (
              <li key={index}>{example}</li>
            ))}
          </ul>
        </div>

        <div className="grammar-practice">
          <h3>Practice Exercises</h3>
          <p>Identify if each sentence is correct or incorrect. If incorrect, the correction will be shown after submission.</p>

          {exercise.practice_items.map((item, index) => (
            <div key={index} className="practice-item">
              <div className="practice-sentence">{item.sentence}</div>
              <div className="practice-options">
                <label className={`option-label ${answers[index] === 'correct' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name={`question-${index}`}
                    value="correct"
                    checked={answers[index] === 'correct'}
                    onChange={(e) => handleAnswerChange(index, e.target.value)}
                    disabled={showResults}
                  />
                  <span>Correct</span>
                </label>
                <label className={`option-label ${answers[index] === 'incorrect' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name={`question-${index}`}
                    value="incorrect"
                    checked={answers[index] === 'incorrect'}
                    onChange={(e) => handleAnswerChange(index, e.target.value)}
                    disabled={showResults}
                  />
                  <span>Incorrect</span>
                </label>
              </div>

              {showResults && (
                <div className={`result ${
                  (answers[index] === 'correct' && item.is_correct) ||
                  (answers[index] === 'incorrect' && !item.is_correct)
                    ? 'correct-answer'
                    : 'incorrect-answer'
                }`}>
                  {item.is_correct ? (
                    <span>✓ This sentence is correct!</span>
                  ) : (
                    <span>✗ Correction: {item.correction}</span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="action-buttons">
          {!showResults ? (
            <button
              className="btn btn-primary"
              onClick={submitAnswers}
              disabled={Object.keys(answers).length !== exercise.practice_items.length}
            >
              Submit Answers
            </button>
          ) : (
            <>
              <div className="final-score">Your Score: {score}/100</div>
              <button className="btn btn-primary" onClick={resetExercise}>
                Try Another Topic
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default GrammarPractice;
