import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { flashcardService } from '../services/api';
import { Flashcard } from '../types';

const FlashcardReviewPage = () => {
  const navigate = useNavigate();
  const [dueCards, setDueCards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [reviewedCount, setReviewedCount] = useState(0);
  const [sessionComplete, setSessionComplete] = useState(false);

  useEffect(() => {
    loadDueCards();
  }, []);

  const loadDueCards = async () => {
    try {
      const response = await flashcardService.getDue();
      const cards = response.data;

      if (cards.length === 0) {
        setSessionComplete(true);
      }

      setDueCards(cards);
    } catch (error) {
      console.error('Error loading due cards:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRating = async (quality: number) => {
    const currentCard = dueCards[currentIndex];
    if (!currentCard.id) return;

    try {
      await flashcardService.submitReview(currentCard.id, quality);
      setReviewedCount(prev => prev + 1);

      // Move to next card
      if (currentIndex + 1 < dueCards.length) {
        setCurrentIndex(currentIndex + 1);
        setShowAnswer(false);
      } else {
        // Session complete
        setSessionComplete(true);
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Failed to submit review');
    }
  };

  const getRatingLabel = (quality: number) => {
    switch (quality) {
      case 0: return 'Complete blackout';
      case 1: return 'Incorrect but recalled';
      case 2: return 'Recalled with serious difficulty';
      case 3: return 'Recalled with some difficulty';
      case 4: return 'Recalled easily';
      case 5: return 'Perfect recall';
      default: return '';
    }
  };

  const getRatingEmoji = (quality: number) => {
    switch (quality) {
      case 0: return '❌';
      case 1: return '😵';
      case 2: return '😟';
      case 3: return '😐';
      case 4: return '😊';
      case 5: return '🎯';
      default: return '';
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  if (sessionComplete || dueCards.length === 0) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="card">
          <h1 className="text-3xl font-bold mb-4">🎉 Review Session Complete!</h1>

          {reviewedCount > 0 ? (
            <>
              <div className="mb-6">
                <p className="text-xl mb-2">Great job! You reviewed:</p>
                <div className="text-4xl font-bold text-green-600 mb-4">{reviewedCount} cards</div>
              </div>

              <div className="space-y-2 text-gray-600 dark:text-gray-400 mb-6">
                <p>Your progress has been saved.</p>
                <p>Come back tomorrow for more reviews!</p>
              </div>
            </>
          ) : (
            <div className="mb-6">
              <p className="text-xl mb-4">No cards are due for review right now.</p>
              <p className="text-gray-600 dark:text-gray-400">Check back later or create more flashcards!</p>
            </div>
          )}

          <div className="flex gap-4 justify-center">
            <button onClick={() => navigate('/flashcards')} className="btn btn-primary">
              Back to Library
            </button>
            <button onClick={() => navigate('/')} className="btn btn-secondary">
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentCard = dueCards[currentIndex];
  const progress = ((currentIndex + 1) / dueCards.length) * 100;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-2xl font-bold">Flashcard Review</h1>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Card {currentIndex + 1} of {dueCards.length}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Flashcard */}
      <div className="card mb-6 min-h-[400px]">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm px-3 py-1 rounded bg-gray-100 dark:bg-gray-700">
            {currentCard.category || 'General'}
          </span>
          <span className={`text-sm px-3 py-1 rounded ${
            currentCard.difficulty === 'EASY' ? 'bg-green-100 text-green-800 dark:bg-green-900' :
            currentCard.difficulty === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900' :
            'bg-red-100 text-red-800 dark:bg-red-900'
          }`}>
            {currentCard.difficulty || 'N/A'}
          </span>
        </div>

        {!showAnswer ? (
          /* Question Side */
          <div className="flex flex-col items-center justify-center py-16">
            <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">QUESTION</div>
            <div className="text-2xl text-center mb-8 px-4">{currentCard.front}</div>
            <button
              onClick={() => setShowAnswer(true)}
              className="btn btn-primary text-lg px-8 py-3"
            >
              Show Answer
            </button>
            <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
              or press Space
            </div>
          </div>
        ) : (
          /* Answer Side */
          <div>
            <div className="mb-8">
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">QUESTION</div>
              <div className="text-lg mb-6">{currentCard.front}</div>

              <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">ANSWER</div>
              <div className="text-xl p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                {currentCard.back}
              </div>
            </div>

            <div className="border-t dark:border-gray-700 pt-6">
              <div className="text-center mb-4">
                <div className="text-lg font-semibold mb-2">How well did you know this?</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Rate your recall (this affects next review date)
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[0, 1, 2, 3, 4, 5].map(quality => (
                  <button
                    key={quality}
                    onClick={() => handleRating(quality)}
                    className={`p-4 rounded-lg border-2 transition-all hover:scale-105 ${
                      quality === 0 || quality === 1 || quality === 2
                        ? 'border-red-300 hover:border-red-500 hover:bg-red-50 dark:hover:bg-red-900'
                        : 'border-green-300 hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900'
                    }`}
                  >
                    <div className="text-3xl mb-2">{getRatingEmoji(quality)}</div>
                    <div className="font-semibold mb-1">{quality}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {getRatingLabel(quality)}
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
                Keyboard shortcuts: 0-5 to rate
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Card Stats */}
      <div className="card">
        <div className="text-sm font-semibold mb-2">Current Card Statistics</div>
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-600 dark:text-gray-400">Reviews</div>
            <div className="font-semibold">{currentCard.reviewCount || 0}</div>
          </div>
          <div>
            <div className="text-gray-600 dark:text-gray-400">Repetitions</div>
            <div className="font-semibold">{currentCard.repetitions || 0}</div>
          </div>
          <div>
            <div className="text-gray-600 dark:text-gray-400">Interval</div>
            <div className="font-semibold">{currentCard.interval || 0} days</div>
          </div>
          <div>
            <div className="text-gray-600 dark:text-gray-400">Success Rate</div>
            <div className="font-semibold">
              {currentCard.reviewCount && currentCard.reviewCount > 0
                ? Math.round(((currentCard.successCount || 0) / currentCard.reviewCount) * 100)
                : 0}%
            </div>
          </div>
        </div>
      </div>

      {/* Keyboard Shortcuts Handler */}
      <div
        className="fixed inset-0 pointer-events-none"
        onKeyDown={(e) => {
          if (!showAnswer && e.key === ' ') {
            e.preventDefault();
            setShowAnswer(true);
          } else if (showAnswer && e.key >= '0' && e.key <= '5') {
            e.preventDefault();
            handleRating(parseInt(e.key));
          }
        }}
        tabIndex={-1}
      />
    </div>
  );
};

export default FlashcardReviewPage;
