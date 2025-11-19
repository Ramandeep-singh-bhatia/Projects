/**
 * Series Tracker Component - Track book series progress
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Series {
  series_id: number;
  series_name: string;
  primary_author: string;
  total_books: number;
  books_completed: number;
  books_in_database: number;
}

const SeriesTracker: React.FC = () => {
  const [series, setSeries] = useState<Series[]>([]);
  const [inProgress, setInProgress] = useState<Series[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSeries();
  }, []);

  const loadSeries = async () => {
    try {
      const [allSeriesRes, inProgressRes] = await Promise.all([
        axios.get(`${process.env.REACT_APP_API_URL}/enhanced/series`),
        axios.get(`${process.env.REACT_APP_API_URL}/enhanced/series/in-progress`)
      ]);

      setSeries(allSeriesRes.data);
      setInProgress(inProgressRes.data);
    } catch (error) {
      console.error('Failed to load series:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateProgress = (s: Series) => {
    if (!s.total_books) return 0;
    return (s.books_completed / s.total_books) * 100;
  };

  if (isLoading) {
    return <div className="loading">Loading series...</div>;
  }

  return (
    <div className="series-tracker">
      <h1>Series Tracker</h1>

      {/* In Progress Series */}
      {inProgress.length > 0 && (
        <div className="series-section">
          <h2>Currently Reading</h2>
          <div className="series-grid">
            {inProgress.map(s => (
              <div key={s.series_id} className="series-card in-progress">
                <h3>{s.series_name}</h3>
                <p className="author">by {s.primary_author}</p>

                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${calculateProgress(s)}%` }}
                  />
                </div>

                <div className="series-stats">
                  <span>{s.books_completed} / {s.total_books || '?'} books</span>
                  <span className="progress-percent">
                    {calculateProgress(s).toFixed(0)}%
                  </span>
                </div>

                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => window.location.href = `/series/${s.series_id}`}
                >
                  Continue Series
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Series */}
      <div className="series-section">
        <h2>All Series</h2>
        {series.length === 0 ? (
          <p className="empty-state">No series tracked yet. Start a series to see it here!</p>
        ) : (
          <div className="series-list">
            {series.map(s => (
              <div key={s.series_id} className="series-list-item">
                <div className="series-info">
                  <h4>{s.series_name}</h4>
                  <p>{s.primary_author}</p>
                </div>

                <div className="series-progress-mini">
                  {s.books_completed} / {s.total_books || s.books_in_database} books
                </div>

                <div className="series-status">
                  {s.books_completed === 0 && <span className="badge not-started">Not Started</span>}
                  {s.books_completed > 0 && s.books_completed < (s.total_books || Infinity) && (
                    <span className="badge in-progress">In Progress</span>
                  )}
                  {s.total_books && s.books_completed >= s.total_books && (
                    <span className="badge completed">Completed</span>
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

export default SeriesTracker;
