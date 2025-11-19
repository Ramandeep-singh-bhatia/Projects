/**
 * Vocabulary Flashcard Component - For spaced repetition learning
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface VocabularyWord {
  id: number;
  word: string;
  definition: string;
  pronunciation: string;
  context_sentence: string;
  book_title: string;
  mastery_level: string;
}

const VocabularyFlashcard: React.FC = () => {
  const [words, setWords] = useState<VocabularyWord[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadWordsForReview();
    loadStats();
  }, []);

  const loadWordsForReview = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/enhanced/vocabulary/review?limit=10`
      );
      setWords(response.data);
    } catch (error) {
      console.error('Failed to load vocabulary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/enhanced/vocabulary/stats`
      );
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleReview = async (knew_it: boolean) => {
    if (words.length === 0) return;

    const currentWord = words[currentIndex];

    try {
      await axios.post(
        `${process.env.REACT_APP_API_URL}/enhanced/vocabulary/review/${currentWord.id}`,
        null,
        { params: { knew_it } }
      );

      // Move to next word
      if (currentIndex < words.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setShowAnswer(false);
      } else {
        // All words reviewed
        alert('Great job! All words reviewed.');
        loadWordsForReview();
        loadStats();
        setCurrentIndex(0);
      }
    } catch (error) {
      console.error('Failed to record review:', error);
    }
  };

  if (isLoading) {
    return <div className="loading">Loading vocabulary...</div>;
  }

  if (words.length === 0) {
    return (
      <div className="vocabulary-empty">
        <h2>No Words Due for Review!</h2>
        <p>Come back tomorrow or add new words from your reading.</p>
        {stats && (
          <div className="vocab-stats-summary">
            <p>Total Words: {stats.total_words}</p>
            <p>Mastered: {stats.mastery?.mastered || 0}</p>
          </div>
        )}
      </div>
    );
  }

  const currentWord = words[currentIndex];

  return (
    <div className="vocabulary-flashcard-container">
      {/* Stats Header */}
      {stats && (
        <div className="vocab-stats-header">
          <div className="stat">
            <span className="stat-label">Total</span>
            <span className="stat-value">{stats.total_words}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Learning</span>
            <span className="stat-value">{stats.mastery?.learning || 0}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Mastered</span>
            <span className="stat-value">{stats.mastery?.mastered || 0}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Streak</span>
            <span className="stat-value">{stats.review_streak_days} days</span>
          </div>
        </div>
      )}

      {/* Flashcard */}
      <div className="flashcard-wrapper">
        <div className="progress-indicator">
          {currentIndex + 1} / {words.length}
        </div>

        <div className={`flashcard ${showAnswer ? 'flipped' : ''}`}>
          <div className="flashcard-front">
            <h2 className="word">{currentWord.word}</h2>
            {currentWord.pronunciation && (
              <p className="pronunciation">{currentWord.pronunciation}</p>
            )}
            <div className="context">
              <p className="context-label">Context:</p>
              <p className="context-sentence">"{currentWord.context_sentence}"</p>
            </div>
            {currentWord.book_title && (
              <p className="source">From: {currentWord.book_title}</p>
            )}
            <button className="btn btn-secondary" onClick={() => setShowAnswer(true)}>
              Show Definition
            </button>
          </div>

          {showAnswer && (
            <div className="flashcard-back">
              <h3>Definition</h3>
              <p className="definition">{currentWord.definition}</p>
              <div className="review-actions">
                <button
                  className="btn btn-danger"
                  onClick={() => handleReview(false)}
                >
                  Still Learning
                </button>
                <button
                  className="btn btn-success"
                  onClick={() => handleReview(true)}
                >
                  I Knew It!
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VocabularyFlashcard;
