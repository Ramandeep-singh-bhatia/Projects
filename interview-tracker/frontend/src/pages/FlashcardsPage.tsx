import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { flashcardService } from '../services/api';
import { Flashcard, FlashcardStats } from '../types';

const FlashcardsPage = () => {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [stats, setStats] = useState<FlashcardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('');
  const [showArchived, setShowArchived] = useState(false);
  const [selectedCard, setSelectedCard] = useState<Flashcard | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCard, setNewCard] = useState<Partial<Flashcard>>({ front: '', back: '' });

  useEffect(() => {
    loadFlashcards();
    loadStats();
  }, [showArchived]);

  const loadFlashcards = async () => {
    try {
      const response = await flashcardService.getAll(!showArchived);
      setFlashcards(response.data);
    } catch (error) {
      console.error('Error loading flashcards:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await flashcardService.getAnalytics();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      loadFlashcards();
      return;
    }

    try {
      const response = await flashcardService.search(searchTerm);
      setFlashcards(response.data);
    } catch (error) {
      console.error('Error searching:', error);
    }
  };

  const handleCreateCard = async () => {
    if (!newCard.front || !newCard.back) {
      alert('Front and back are required');
      return;
    }

    try {
      await flashcardService.create(newCard);
      setShowCreateModal(false);
      setNewCard({ front: '', back: '' });
      loadFlashcards();
      loadStats();
    } catch (error) {
      console.error('Error creating flashcard:', error);
      alert('Failed to create flashcard');
    }
  };

  const handleDeleteCard = async (id: number) => {
    if (!confirm('Delete this flashcard?')) return;

    try {
      await flashcardService.delete(id);
      loadFlashcards();
      loadStats();
    } catch (error) {
      console.error('Error deleting flashcard:', error);
    }
  };

  const handleArchiveCard = async (id: number) => {
    try {
      await flashcardService.archive(id);
      loadFlashcards();
      loadStats();
    } catch (error) {
      console.error('Error archiving flashcard:', error);
    }
  };

  const filteredCards = flashcards.filter(card => {
    if (filterCategory && card.category !== filterCategory) return false;
    if (filterDifficulty && card.difficulty !== filterDifficulty) return false;
    return true;
  });

  const getSuccessRate = (card: Flashcard) => {
    if (!card.reviewCount || card.reviewCount === 0) return 0;
    return Math.round(((card.successCount || 0) / card.reviewCount) * 100);
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="max-w-7xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Flashcards</h1>
        <div className="flex gap-2">
          <Link to="/flashcards/review" className="btn btn-primary">
            Start Review ({stats?.flashcardsDueToday || 0} due)
          </Link>
          <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
            Create Flashcard
          </button>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Total</div>
            <div className="text-2xl font-bold">{stats.totalFlashcards}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Active</div>
            <div className="text-2xl font-bold">{stats.activeFlashcards}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Due Today</div>
            <div className="text-2xl font-bold text-orange-600">{stats.flashcardsDueToday}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Success Rate</div>
            <div className="text-2xl font-bold text-green-600">{stats.averageSuccessRate}%</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400">Mastered</div>
            <div className="text-2xl font-bold text-blue-600">{stats.masteredCards}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="label">Search</label>
            <div className="flex gap-2">
              <input
                type="text"
                className="input flex-1"
                placeholder="Search front or back..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button onClick={handleSearch} className="btn btn-primary">Search</button>
            </div>
          </div>
          <div>
            <label className="label">Category</label>
            <select
              className="input"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              <option value="">All Categories</option>
              <option value="DSA">DSA</option>
              <option value="HLD">HLD</option>
              <option value="LLD">LLD</option>
              <option value="Behavioral">Behavioral</option>
            </select>
          </div>
          <div>
            <label className="label">Difficulty</label>
            <select
              className="input"
              value={filterDifficulty}
              onChange={(e) => setFilterDifficulty(e.target.value)}
            >
              <option value="">All Levels</option>
              <option value="EASY">Easy</option>
              <option value="MEDIUM">Medium</option>
              <option value="HARD">Hard</option>
            </select>
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={showArchived}
                onChange={(e) => setShowArchived(e.target.checked)}
              />
              <span>Show Archived</span>
            </label>
          </div>
        </div>
      </div>

      {/* Flashcards List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCards.map(card => (
          <div key={card.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-2">
              <span className={`text-xs px-2 py-1 rounded ${
                card.difficulty === 'EASY' ? 'bg-green-100 text-green-800' :
                card.difficulty === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {card.difficulty || 'N/A'}
              </span>
              {card.archived && (
                <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-800">Archived</span>
              )}
            </div>

            <div className="mb-4">
              <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">Front:</div>
              <div className="text-sm line-clamp-2">{card.front}</div>
            </div>

            <div className="mb-4">
              <div className="text-sm font-semibold text-gray-600 dark:text-gray-400">Back:</div>
              <div className="text-sm line-clamp-2">{card.back}</div>
            </div>

            <div className="text-xs text-gray-500 space-y-1 mb-4">
              <div>Reviews: {card.reviewCount || 0}</div>
              <div>Success Rate: {getSuccessRate(card)}%</div>
              <div>Next Review: {card.nextReviewDate ? new Date(card.nextReviewDate).toLocaleDateString() : 'N/A'}</div>
              {card.category && <div>Category: {card.category}</div>}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setSelectedCard(card)}
                className="btn btn-primary flex-1 text-sm"
              >
                View
              </button>
              {!card.archived ? (
                <button
                  onClick={() => handleArchiveCard(card.id!)}
                  className="btn btn-secondary text-sm"
                >
                  Archive
                </button>
              ) : null}
              <button
                onClick={() => handleDeleteCard(card.id!)}
                className="btn btn-danger text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredCards.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No flashcards found. Create your first flashcard to get started!
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4">
            <h2 className="text-2xl font-bold mb-4">Create Flashcard</h2>

            <div className="space-y-4">
              <div>
                <label className="label">Front (Question/Concept)</label>
                <textarea
                  className="input h-24"
                  value={newCard.front}
                  onChange={(e) => setNewCard({ ...newCard, front: e.target.value })}
                  placeholder="What do you want to remember?"
                />
              </div>

              <div>
                <label className="label">Back (Answer/Explanation)</label>
                <textarea
                  className="input h-32"
                  value={newCard.back}
                  onChange={(e) => setNewCard({ ...newCard, back: e.target.value })}
                  placeholder="The answer or explanation"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Category</label>
                  <input
                    type="text"
                    className="input"
                    value={newCard.category || ''}
                    onChange={(e) => setNewCard({ ...newCard, category: e.target.value })}
                    placeholder="e.g., DSA, HLD"
                  />
                </div>
                <div>
                  <label className="label">Difficulty</label>
                  <select
                    className="input"
                    value={newCard.difficulty || ''}
                    onChange={(e) => setNewCard({ ...newCard, difficulty: e.target.value as any })}
                  >
                    <option value="">Select...</option>
                    <option value="EASY">Easy</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HARD">Hard</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewCard({ front: '', back: '' });
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button onClick={handleCreateCard} className="btn btn-primary">
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View Card Modal */}
      {selectedCard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold">Flashcard Details</h2>
              <button
                onClick={() => setSelectedCard(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">FRONT</div>
                <div>{selectedCard.front}</div>
              </div>

              <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                <div className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">BACK</div>
                <div>{selectedCard.back}</div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Category:</span> {selectedCard.category || 'N/A'}
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Difficulty:</span> {selectedCard.difficulty || 'N/A'}
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Total Reviews:</span> {selectedCard.reviewCount || 0}
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Success Rate:</span> {getSuccessRate(selectedCard)}%
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Repetitions:</span> {selectedCard.repetitions || 0}
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Interval:</span> {selectedCard.interval || 0} days
                </div>
                <div className="col-span-2">
                  <span className="text-gray-600 dark:text-gray-400">Next Review:</span>{' '}
                  {selectedCard.nextReviewDate ? new Date(selectedCard.nextReviewDate).toLocaleString() : 'N/A'}
                </div>
              </div>

              <button
                onClick={() => setSelectedCard(null)}
                className="btn btn-primary w-full"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlashcardsPage;
