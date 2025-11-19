/**
 * Book Evaluation Component - Display "Should I Read This?" results
 */
import React, { useState } from 'react';
import axios from 'axios';

interface Evaluation {
  readiness_score: number;
  recommendation_type: string;
  factors_breakdown: {
    complexity_match: number;
    interest_alignment: number;
    completion_likelihood: number;
    enjoyment_potential: number;
    growth_opportunity: number;
  };
  gaps_identified: string[];
  strengths: string[];
  detailed_reasoning: string;
  preparation_needed: boolean;
  estimated_ready_in_days?: number;
  quick_wins: string[];
  alternative_suggestions: string[];
}

interface BookEvaluationProps {
  bookId: number;
  bookTitle: string;
  onAddToFutureReads?: () => void;
}

const BookEvaluation: React.FC<BookEvaluationProps> = ({
  bookId,
  bookTitle,
  onAddToFutureReads
}) => {
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runEvaluation = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/evaluate/${bookId}`
      );

      setEvaluation(response.data.evaluation);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to evaluate book');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToFutureReads = async () => {
    if (!evaluation) return;

    try {
      await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/future-reads/add`,
        {
          book_id: bookId,
          reminder_preference: 'when_ready'
        },
        {
          params: { evaluation_data: evaluation }
        }
      );

      alert('Added to Future Reads! You\'ll be notified when ready.');

      if (onAddToFutureReads) {
        onAddToFutureReads();
      }
    } catch (err) {
      alert('Failed to add to Future Reads');
    }
  };

  const handleGeneratePrep = async () => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/preparation-plan/${bookId}`,
        evaluation
      );

      const plan = response.data.plan;
      alert(`Preparation Plan Created!\n\n${plan.plan_name}\n\nRecommended books:\n${plan.recommended_books.map((b: any) => `${b.sequence_order}. ${b.title} - ${b.why_this_helps}`).join('\n\n')}`);
    } catch (err) {
      alert('Failed to generate preparation plan');
    }
  };

  const getRecommendationIcon = (type: string): string => {
    switch (type) {
      case 'read_now':
        return '✅';
      case 'maybe_later':
        return '⏰';
      case 'not_yet':
        return '📚';
      case 'different_direction':
        return '🔄';
      default:
        return '❓';
    }
  };

  const getRecommendationColor = (type: string): string => {
    switch (type) {
      case 'read_now':
        return 'green';
      case 'maybe_later':
        return 'yellow';
      case 'not_yet':
        return 'orange';
      case 'different_direction':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getRecommendationTitle = (type: string): string => {
    switch (type) {
      case 'read_now':
        return 'Read Now!';
      case 'maybe_later':
        return 'Maybe Later';
      case 'not_yet':
        return 'Not Yet Ready';
      case 'different_direction':
        return 'Try Different Books';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="book-evaluation">
      <h2>Should I Read This?</h2>
      <h3>{bookTitle}</h3>

      {!evaluation && (
        <div className="evaluation-intro">
          <p>Get a comprehensive readiness assessment for this book:</p>
          <ul>
            <li>Readiness score (0-100)</li>
            <li>Complexity match with your reading level</li>
            <li>Interest alignment with your preferences</li>
            <li>Likelihood of completion</li>
            <li>Personalized recommendation</li>
          </ul>
          <button
            className="btn btn-primary btn-lg"
            onClick={runEvaluation}
            disabled={isLoading}
          >
            {isLoading ? 'Evaluating...' : 'Evaluate This Book'}
          </button>
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      {evaluation && (
        <div className="evaluation-results">
          {/* Overall Score */}
          <div className={`evaluation-verdict ${getRecommendationColor(evaluation.recommendation_type)}`}>
            <div className="verdict-icon">
              {getRecommendationIcon(evaluation.recommendation_type)}
            </div>
            <div className="verdict-content">
              <h2>{getRecommendationTitle(evaluation.recommendation_type)}</h2>
              <div className="readiness-score-large">
                <span className="score">{evaluation.readiness_score}</span>
                <span className="max">/100</span>
              </div>
            </div>
          </div>

          {/* Detailed Reasoning */}
          <div className="evaluation-section reasoning">
            <h3>Assessment</h3>
            <p className="reasoning-text">{evaluation.detailed_reasoning}</p>
          </div>

          {/* Factor Breakdown */}
          <div className="evaluation-section factors">
            <h3>Readiness Factors</h3>
            <div className="factors-grid">
              {Object.entries(evaluation.factors_breakdown).map(([factor, score]) => (
                <div key={factor} className="factor-card">
                  <div className="factor-label">
                    {factor.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                  </div>
                  <div className="factor-meter">
                    <div
                      className="factor-fill"
                      style={{
                        width: `${score}%`,
                        backgroundColor: score >= 75 ? '#4caf50' : score >= 50 ? '#ffc107' : '#ff5722'
                      }}
                    />
                  </div>
                  <div className="factor-score">{score}/100</div>
                </div>
              ))}
            </div>
          </div>

          {/* Strengths */}
          {evaluation.strengths.length > 0 && (
            <div className="evaluation-section strengths">
              <h3>✨ Strengths</h3>
              <ul>
                {evaluation.strengths.map((strength, idx) => (
                  <li key={idx}>{strength}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Gaps */}
          {evaluation.gaps_identified.length > 0 && (
            <div className="evaluation-section gaps">
              <h3>📋 Areas for Growth</h3>
              <ul>
                {evaluation.gaps_identified.map((gap, idx) => (
                  <li key={idx}>{gap}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Quick Wins */}
          {evaluation.quick_wins.length > 0 && (
            <div className="evaluation-section quick-wins">
              <h3>🚀 Quick Wins to Bridge Gaps</h3>
              <p>Reading these books will help prepare you:</p>
              <ul>
                {evaluation.quick_wins.map((book, idx) => (
                  <li key={idx}>{book}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Alternative Suggestions */}
          {evaluation.alternative_suggestions.length > 0 && (
            <div className="evaluation-section alternatives">
              <h3>💡 Better Matches for You</h3>
              <p>Consider these books instead:</p>
              <ul>
                {evaluation.alternative_suggestions.map((book, idx) => (
                  <li key={idx}>{book}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Action Buttons */}
          <div className="evaluation-actions">
            {evaluation.recommendation_type === 'read_now' ? (
              <button className="btn btn-primary btn-lg">
                Add to Reading List
              </button>
            ) : (
              <>
                <button
                  className="btn btn-primary"
                  onClick={handleAddToFutureReads}
                >
                  Add to Future Reads
                </button>

                {evaluation.preparation_needed && (
                  <button
                    className="btn btn-secondary"
                    onClick={handleGeneratePrep}
                  >
                    Generate Preparation Plan
                  </button>
                )}
              </>
            )}

            <button className="btn btn-outline" onClick={runEvaluation}>
              Re-evaluate
            </button>
          </div>

          {/* Timeline */}
          {evaluation.estimated_ready_in_days && (
            <div className="evaluation-timeline">
              <p>
                <strong>Estimated time to readiness:</strong>{' '}
                {evaluation.estimated_ready_in_days} days
                ({Math.ceil(evaluation.estimated_ready_in_days / 30)} months)
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BookEvaluation;
