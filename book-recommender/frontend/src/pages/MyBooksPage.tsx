/**
 * My Books page for tracking reading progress.
 */
import React, { useState, useEffect } from 'react';
import { getReadingLogs, updateReadingLog, markCompleted, ReadingLog } from '../services/api';
import '../styles/MyBooksPage.css';

interface BookWithLog extends ReadingLog {
  title?: string;
  author?: string;
  cover_url?: string;
  page_count?: number;
}

const MyBooksPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('reading');
  const [books, setBooks] = useState<BookWithLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadBooks(activeTab);
  }, [activeTab]);

  const loadBooks = async (status: string) => {
    setIsLoading(true);
    try {
      const response = await getReadingLogs(status);
      setBooks(response.data);
    } catch (error) {
      console.error('Failed to load books:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkCompleted = async (logId: number) => {
    const rating = prompt('Rate this book (1-5):');
    if (!rating) return;

    const ratingNum = parseInt(rating);
    if (ratingNum < 1 || ratingNum > 5) {
      alert('Please enter a rating between 1 and 5');
      return;
    }

    const notes = prompt('Any notes about this book? (optional)');

    try {
      await markCompleted(logId, ratingNum, notes || undefined, true);
      alert('Book marked as completed! 🎉');
      loadBooks(activeTab);
    } catch (error: any) {
      alert('Failed to mark as completed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleMarkDNF = async (logId: number) => {
    if (!window.confirm('Mark this book as Did Not Finish?')) return;

    try {
      await updateReadingLog(logId, { status: 'dnf' });
      alert('Book marked as DNF');
      loadBooks(activeTab);
    } catch (error: any) {
      alert('Failed to update: ' + error.message);
    }
  };

  const tabs = [
    { id: 'reading', label: 'Currently Reading' },
    { id: 'to_read', label: 'To Read' },
    { id: 'completed', label: 'Completed' },
    { id: 'dnf', label: 'Did Not Finish' }
  ];

  return (
    <div className="my-books-page">
      <h1>My Books</h1>

      {/* Tabs */}
      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Books List */}
      <div className="books-content">
        {isLoading ? (
          <div className="loading">Loading books...</div>
        ) : books.length === 0 ? (
          <div className="empty-state">
            <p>No books in this category yet.</p>
            <p>Start by exploring recommendations on the home page!</p>
          </div>
        ) : (
          <div className="books-grid">
            {books.map((book) => (
              <div key={book.id} className="book-card-full">
                {book.cover_url && (
                  <img
                    src={book.cover_url}
                    alt={book.title}
                    className="book-cover"
                  />
                )}
                <div className="book-info-full">
                  <h3>{book.title || 'Unknown Title'}</h3>
                  <p className="author">{book.author || 'Unknown Author'}</p>

                  {book.date_started && (
                    <p className="date-info">
                      Started: {new Date(book.date_started).toLocaleDateString()}
                    </p>
                  )}

                  {book.date_completed && (
                    <p className="date-info">
                      Completed: {new Date(book.date_completed).toLocaleDateString()}
                    </p>
                  )}

                  {book.reading_duration_days && (
                    <p className="duration">
                      Reading time: {book.reading_duration_days} days
                    </p>
                  )}

                  {book.rating && (
                    <div className="rating">
                      Rating: {'★'.repeat(book.rating)}{'☆'.repeat(5 - book.rating)}
                    </div>
                  )}

                  {book.personal_notes && (
                    <div className="notes">
                      <strong>Notes:</strong>
                      <p>{book.personal_notes}</p>
                    </div>
                  )}

                  {book.ai_summary && (
                    <div className="ai-summary">
                      <strong>AI Summary:</strong>
                      <p>{book.ai_summary}</p>
                    </div>
                  )}

                  {/* Actions */}
                  {book.status === 'reading' && (
                    <div className="book-actions">
                      <button
                        onClick={() => handleMarkCompleted(book.id)}
                        className="btn btn-success"
                      >
                        Mark as Completed
                      </button>
                      <button
                        onClick={() => handleMarkDNF(book.id)}
                        className="btn btn-danger"
                      >
                        Did Not Finish
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyBooksPage;
