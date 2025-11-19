/**
 * Genre section component for displaying recommendations by genre.
 */
import React, { useState, useEffect } from 'react';
import { getRecommendations, Recommendation } from '../services/api';
import BookCard from './BookCard';

interface GenreSectionProps {
  genre: string;
  onStartReading: (bookId: number) => void;
}

const GenreSection: React.FC<GenreSectionProps> = ({ genre, onStartReading }) => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRecommendations = async (refresh: boolean = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getRecommendations(genre, 3, refresh);
      setRecommendations(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isExpanded && recommendations.length === 0) {
      loadRecommendations();
    }
  }, [isExpanded]);

  return (
    <div className="genre-section">
      <div className="genre-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h2>{genre}</h2>
        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
      </div>

      {isExpanded && (
        <div className="genre-content">
          {isLoading && <div className="loading">Loading recommendations...</div>}

          {error && (
            <div className="error">
              {error}
              {error.includes('not initialized') && (
                <p className="error-hint">
                  Please ensure ANTHROPIC_API_KEY is set in your environment.
                </p>
              )}
            </div>
          )}

          {!isLoading && !error && (
            <>
              <div className="recommendations-grid">
                {recommendations.map((book, idx) => (
                  <BookCard
                    key={idx}
                    book={book}
                    onStartReading={onStartReading}
                  />
                ))}
              </div>

              <button
                onClick={() => loadRecommendations(true)}
                className="btn btn-refresh"
                disabled={isLoading}
              >
                🔄 Refresh Recommendations
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default GenreSection;
