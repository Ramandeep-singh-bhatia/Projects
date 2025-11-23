import React, { useState } from 'react';
import { RefreshCcw, Clock, Calendar } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import './Review.css';

const Review = () => {
  const { vocabularyMastery, exerciseHistory } = useAppStore();
  const [activeTab, setActiveTab] = useState('vocabulary');

  const vocabDueForReview = vocabularyMastery.filter(v => {
    if (!v.next_review) return true;
    return new Date(v.next_review) <= new Date();
  });

  const recentExercises = exerciseHistory.slice(0, 20);

  return (
    <div className="review-page">
      <div className="review-header">
        <div>
          <h1><RefreshCcw size={32} /> Review & Practice</h1>
          <p>Reinforce your learning with spaced repetition</p>
        </div>
      </div>

      <div className="review-tabs">
        <button
          className={`tab-button ${activeTab === 'vocabulary' ? 'active' : ''}`}
          onClick={() => setActiveTab('vocabulary')}
        >
          Vocabulary Review
          {vocabDueForReview.length > 0 && (
            <span className="badge badge-danger">{vocabDueForReview.length}</span>
          )}
        </button>
        <button
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          Exercise History
        </button>
      </div>

      <div className="review-content">
        {activeTab === 'vocabulary' && (
          <div className="vocabulary-review">
            {vocabDueForReview.length > 0 ? (
              <>
                <div className="review-info">
                  <h3>Words Due for Review</h3>
                  <p>You have {vocabDueForReview.length} words ready for review</p>
                </div>
                <div className="vocab-review-list">
                  {vocabDueForReview.map((vocab, index) => (
                    <div key={index} className="vocab-review-card">
                      <div className="vocab-word">{vocab.word || `Word ${index + 1}`}</div>
                      <div className="vocab-mastery">
                        <span>Mastery: {vocab.mastery_level}%</span>
                        <div className="mastery-bar">
                          <div
                            className="mastery-fill"
                            style={{ width: `${vocab.mastery_level}%` }}
                          />
                        </div>
                      </div>
                      <div className="vocab-stats">
                        <span>Seen: {vocab.times_seen || 0} times</span>
                        <span>Correct: {vocab.times_correct || 0}/{vocab.times_seen || 0}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <button className="btn btn-primary">
                  Start Review Session
                </button>
              </>
            ) : (
              <div className="empty-state">
                <Calendar size={64} />
                <h3>All Caught Up!</h3>
                <p>No vocabulary words are due for review right now.</p>
                <p className="next-review">
                  Check back tomorrow for more words to review.
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="exercise-history">
            {recentExercises.length > 0 ? (
              <div className="history-list">
                {recentExercises.map((exercise, index) => (
                  <div key={index} className="history-item">
                    <div className="history-icon">
                      <Clock size={20} />
                    </div>
                    <div className="history-details">
                      <div className="history-type">{exercise.exercise_type}</div>
                      <div className="history-date">
                        {new Date(exercise.completed_at).toLocaleString()}
                      </div>
                    </div>
                    <div className={`history-score score-${Math.floor(exercise.score / 20)}`}>
                      {exercise.score}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <Clock size={64} />
                <h3>No Exercise History</h3>
                <p>Complete some exercises to see your history here.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Review;
