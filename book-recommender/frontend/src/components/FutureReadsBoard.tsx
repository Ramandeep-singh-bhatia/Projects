/**
 * Future Reads Board - Manage books you want to read eventually
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface FutureRead {
  future_read_id: number;
  book_id: number;
  title: string;
  author: string;
  genre: string;
  cover_url?: string;
  readiness_score: number;
  estimated_ready_date?: string;
  status: string;
  notes?: string;
  recommended_by?: string;
  has_preparation_plan: boolean;
}

const FutureReadsBoard: React.FC = () => {
  const [futureReads, setFutureReads] = useState<FutureRead[]>([]);
  const [readyBooks, setReadyBooks] = useState<FutureRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  useEffect(() => {
    loadFutureReads();
    loadReadyBooks();
  }, [selectedStatus]);

  const loadFutureReads = async () => {
    try {
      const params: any = {};
      if (selectedStatus !== 'all') {
        params.status = selectedStatus;
      }

      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/manual/future-reads`,
        { params }
      );

      setFutureReads(response.data.books);
    } catch (error) {
      console.error('Failed to load future reads:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadReadyBooks = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/manual/readiness-check/notifications`
      );

      setReadyBooks(response.data.ready_books);
    } catch (error) {
      console.error('Failed to load ready books:', error);
    }
  };

  const runReadinessCheck = async () => {
    setIsLoading(true);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/readiness-check/run`
      );

      if (response.data.updates_found > 0) {
        alert(`Found ${response.data.updates_found} readiness updates!`);
        loadFutureReads();
        loadReadyBooks();
      } else {
        alert('No readiness updates at this time. Keep reading to build your profile!');
      }
    } catch (error) {
      console.error('Readiness check failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generatePreparationPlan = async (bookId: number) => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/manual/preparation-plan/${bookId}`
      );

      const plan = response.data.plan;
      alert(`Preparation Plan: ${plan.plan_name}\n\nRecommended books:\n${plan.recommended_books.map((b: any) => `- ${b.title} by ${b.author}`).join('\n')}`);

      loadFutureReads(); // Refresh to show plan link
    } catch (error) {
      console.error('Failed to generate plan:', error);
    }
  };

  const getReadinessColor = (score: number): string => {
    if (score >= 75) return 'green';
    if (score >= 50) return 'yellow';
    if (score >= 25) return 'orange';
    return 'red';
  };

  const getReadinessLabel = (score: number): string => {
    if (score >= 75) return 'Ready Now!';
    if (score >= 50) return 'Almost Ready';
    if (score >= 25) return 'Getting There';
    return 'Needs Prep';
  };

  if (isLoading) {
    return <div className="loading-page">Loading your future reads...</div>;
  }

  return (
    <div className="future-reads-board">
      <div className="page-header">
        <h1>Future Reads</h1>
        <p className="subtitle">Books you want to read - we'll let you know when you're ready!</p>
      </div>

      {/* Ready Now Alert */}
      {readyBooks.length > 0 && (
        <div className="ready-alert">
          <h2>🎉 Books Ready to Read!</h2>
          <p>You're now ready for {readyBooks.length} book(s) in your Future Reads!</p>
          <div className="ready-books-list">
            {readyBooks.map(book => (
              <div key={book.future_read_id} className="ready-book-card">
                <strong>{book.title}</strong> by {book.author}
                <span className="readiness-score ready">{book.readiness_score}/100</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="board-controls">
        <div className="filter-group">
          <label>Filter by status:</label>
          <select
            value={selectedStatus}
            onChange={e => setSelectedStatus(e.target.value)}
            className="form-control"
          >
            <option value="all">All</option>
            <option value="waiting">Waiting</option>
            <option value="preparing">Preparing</option>
            <option value="ready">Ready</option>
          </select>
        </div>

        <button
          className="btn btn-primary"
          onClick={runReadinessCheck}
          disabled={isLoading}
        >
          Run Readiness Check
        </button>
      </div>

      {/* Future Reads Grid */}
      {futureReads.length === 0 ? (
        <div className="empty-state">
          <h3>No future reads yet!</h3>
          <p>When you evaluate a book and it's not quite ready, add it here.</p>
          <p>We'll monitor your reading progress and let you know when you're ready!</p>
        </div>
      ) : (
        <div className="future-reads-grid">
          {futureReads.map(book => (
            <div key={book.future_read_id} className="future-read-card">
              {book.cover_url && (
                <img src={book.cover_url} alt={book.title} className="book-cover" />
              )}

              <div className="book-info">
                <h3>{book.title}</h3>
                <p className="author">by {book.author}</p>
                <p className="genre">{book.genre}</p>

                {book.recommended_by && (
                  <p className="recommended-by">
                    Recommended by: {book.recommended_by}
                  </p>
                )}

                {book.notes && (
                  <p className="notes">"{book.notes}"</p>
                )}
              </div>

              {/* Readiness Indicator */}
              <div className="readiness-section">
                <div className="readiness-meter">
                  <div className="meter-label">
                    <span>Readiness</span>
                    <span className={`score ${getReadinessColor(book.readiness_score)}`}>
                      {book.readiness_score}/100
                    </span>
                  </div>
                  <div className="meter-bar">
                    <div
                      className={`meter-fill ${getReadinessColor(book.readiness_score)}`}
                      style={{ width: `${book.readiness_score}%` }}
                    />
                  </div>
                  <div className="meter-status">
                    {getReadinessLabel(book.readiness_score)}
                  </div>
                </div>

                {book.estimated_ready_date && (
                  <p className="estimated-date">
                    Est. ready: {new Date(book.estimated_ready_date).toLocaleDateString()}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="card-actions">
                {book.status !== 'ready' && !book.has_preparation_plan && (
                  <button
                    className="btn btn-sm btn-secondary"
                    onClick={() => generatePreparationPlan(book.book_id)}
                  >
                    Create Prep Plan
                  </button>
                )}

                {book.has_preparation_plan && (
                  <span className="badge has-plan">Has Prep Plan</span>
                )}

                {book.status === 'ready' && (
                  <button className="btn btn-sm btn-primary">
                    Add to Reading List
                  </button>
                )}
              </div>

              <div className="status-badge">
                <span className={`badge status-${book.status}`}>
                  {book.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Help Section */}
      <div className="help-section">
        <h3>How Future Reads Works</h3>
        <ul>
          <li><strong>Automatic Monitoring:</strong> We track your reading progress and recalculate readiness scores</li>
          <li><strong>Smart Notifications:</strong> Get notified when you're ready for a book (score ≥ 75)</li>
          <li><strong>Preparation Plans:</strong> Need help getting ready? Generate a custom reading plan</li>
          <li><strong>Run Manual Checks:</strong> Click "Run Readiness Check" to check all books now</li>
        </ul>
      </div>
    </div>
  );
};

export default FutureReadsBoard;
