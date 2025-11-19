/**
 * Home page with book recommendations by genre.
 */
import React, { useState, useEffect } from 'react';
import { getDashboardStats, startReading, DashboardStats } from '../services/api';
import GenreSection from '../components/GenreSection';
import '../styles/HomePage.css';

const GENRES = [
  // Fiction
  'Literary Fiction',
  'Mystery/Thriller',
  'Science Fiction',
  'Fantasy',
  'Historical Fiction',
  'Romance',
  // Non-Fiction
  'Biography',
  'Science',
  'History',
  'Self-Help',
  'Business',
  'Philosophy'
];

const HomePage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await getDashboardStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartReading = async (bookId: number) => {
    try {
      await startReading(bookId);
      alert('Started reading! Check your "Currently Reading" section.');
      loadStats(); // Refresh stats
    } catch (error: any) {
      alert('Failed to start reading: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (isLoading) {
    return <div className="loading-page">Loading...</div>;
  }

  return (
    <div className="home-page">
      {/* Quick Stats Widget */}
      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-value">{stats?.current_streak_days || 0}</div>
          <div className="stat-label">Day Streak</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.books_this_month || 0}</div>
          <div className="stat-label">Books This Month</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.books_read_year || 0}</div>
          <div className="stat-label">Books This Year</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.books_read_all_time || 0}</div>
          <div className="stat-label">Total Books</div>
        </div>
      </div>

      {/* Currently Reading */}
      {stats?.currently_reading && stats.currently_reading.length > 0 && (
        <div className="currently-reading-section">
          <h2>Currently Reading</h2>
          <div className="currently-reading-list">
            {stats.currently_reading.map((book: any) => (
              <div key={book.id} className="currently-reading-card">
                <img
                  src={book.cover_url || '/placeholder-book.png'}
                  alt={book.title}
                  className="book-cover-small"
                />
                <div className="book-info">
                  <h3>{book.title}</h3>
                  <p className="author">{book.author}</p>
                  <p className="reading-since">
                    Started: {new Date(book.date_started).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Welcome Message */}
      <div className="welcome-section">
        <h1>Discover Your Next Great Read</h1>
        <p>
          Personalized book recommendations tailored to your reading journey.
          Expand and explore genres below to find books that match your preferences.
        </p>
      </div>

      {/* Browse by Genre */}
      <div className="genre-sections">
        <h2 className="section-title">Browse by Genre</h2>
        <p className="section-subtitle">
          Click on any genre to see personalized recommendations
        </p>

        {GENRES.map((genre) => (
          <GenreSection
            key={genre}
            genre={genre}
            onStartReading={handleStartReading}
          />
        ))}
      </div>
    </div>
  );
};

export default HomePage;
