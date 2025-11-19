import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Loader } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import aiService from '../../services/aiService';
import './Assessment.css';

const Assessment = () => {
  const navigate = useNavigate();
  const { setUser, setLearningProgress } = useAppStore();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [answers, setAnswers] = useState({});

  const questions = [
    {
      id: 'intro',
      question: 'Introduce yourself in 2-3 sentences.',
      type: 'textarea',
      placeholder: 'Tell me about yourself...',
    },
    {
      id: 'daily_routine',
      question: 'Describe your daily routine.',
      type: 'textarea',
      placeholder: 'What does a typical day look like for you?',
    },
    {
      id: 'vocabulary',
      question: 'Choose the word that best completes the sentence: "The project was _____ successful."',
      type: 'multiple',
      options: [
        { value: 'very', label: 'very' },
        { value: 'remarkably', label: 'remarkably' },
        { value: 'much', label: 'much' },
        { value: 'too', label: 'too' },
      ],
    },
    {
      id: 'grammar1',
      question: 'Which sentence is correct?',
      type: 'multiple',
      options: [
        { value: 'a', label: 'She has been working here since five years.' },
        { value: 'b', label: 'She has been working here for five years.' },
        { value: 'c', label: 'She has working here for five years.' },
        { value: 'd', label: 'She is working here since five years.' },
      ],
    },
    {
      id: 'write_email',
      question: 'Write a short professional email requesting a meeting with your manager.',
      type: 'textarea',
      placeholder: 'Write your email here...',
    },
    {
      id: 'conversation',
      question: 'How would you respond to someone who says: "Nice weather we\'re having!"',
      type: 'textarea',
      placeholder: 'Your response...',
    },
    {
      id: 'grammar2',
      question: 'Identify the error: "If I would have known, I would have helped you."',
      type: 'multiple',
      options: [
        { value: 'a', label: 'No error - the sentence is correct' },
        { value: 'b', label: '"would have known" should be "had known"' },
        { value: 'c', label: '"would have helped" should be "helped"' },
        { value: 'd', label: 'Both parts are incorrect' },
      ],
    },
    {
      id: 'opinion',
      question: 'Do you think remote work is better than office work? Explain your opinion.',
      type: 'textarea',
      placeholder: 'Share your thoughts...',
    },
  ];

  const handleAnswerChange = (questionId, value) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }));
  };

  const handleNext = () => {
    if (step < questions.length - 1) {
      setStep(step + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (step > 0) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const assessment = await aiService.evaluateBaselineAssessment(answers);

      // Update user profile and learning progress
      setUser({
        currentLevel: assessment.level,
        proficiencyScore: assessment.proficiency_score,
        hasCompletedAssessment: true,
      });

      setLearningProgress(assessment.scores);

      // Navigate to dashboard
      navigate('/');
    } catch (error) {
      console.error('Assessment error:', error);
      alert('Error processing assessment. Using default values.');

      // Set default values
      setUser({
        currentLevel: 'intermediate',
        proficiencyScore: 50,
        hasCompletedAssessment: true,
      });

      setLearningProgress({
        vocabulary: 50,
        grammar: 50,
        fluency: 50,
        context_usage: 50,
        writing_quality: 50,
      });

      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = questions[step];
  const isAnswered = answers[currentQuestion.id];
  const progress = ((step + 1) / questions.length) * 100;

  if (loading) {
    return (
      <div className="assessment-loading">
        <Loader className="spin" size={48} />
        <h2>Evaluating your assessment...</h2>
        <p>This may take a moment. We're analyzing your responses to create a personalized learning path.</p>
      </div>
    );
  }

  return (
    <div className="assessment">
      <div className="assessment-container">
        <div className="assessment-header">
          <h1>Baseline Assessment</h1>
          <p>Help us understand your current English proficiency level</p>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <div className="progress-text">
            Question {step + 1} of {questions.length}
          </div>
        </div>

        <div className="question-card">
          <div className="question-number">Question {step + 1}</div>
          <h2 className="question-text">{currentQuestion.question}</h2>

          <div className="answer-area">
            {currentQuestion.type === 'textarea' && (
              <textarea
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                placeholder={currentQuestion.placeholder}
                rows={6}
              />
            )}

            {currentQuestion.type === 'multiple' && (
              <div className="options-list">
                {currentQuestion.options.map((option) => (
                  <label key={option.value} className="option-item">
                    <input
                      type="radio"
                      name={currentQuestion.id}
                      value={option.value}
                      checked={answers[currentQuestion.id] === option.value}
                      onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                    />
                    <span className="option-label">{option.label}</span>
                    {answers[currentQuestion.id] === option.value && (
                      <CheckCircle className="option-check" size={20} />
                    )}
                  </label>
                ))}
              </div>
            )}
          </div>

          <div className="question-actions">
            <button
              className="btn btn-secondary"
              onClick={handlePrevious}
              disabled={step === 0}
            >
              Previous
            </button>
            <button
              className="btn btn-primary"
              onClick={handleNext}
              disabled={!isAnswered}
            >
              {step === questions.length - 1 ? 'Submit Assessment' : 'Next Question'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Assessment;
