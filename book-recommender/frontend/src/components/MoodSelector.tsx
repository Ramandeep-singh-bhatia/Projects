/**
 * Mood Selector Component - For mood-based recommendations
 */
import React, { useState } from 'react';
import axios from 'axios';

interface MoodSelections {
  energy: string;
  pacing: string;
  tone: string;
  complexity: string;
}

interface MoodRecommendation {
  title: string;
  author: string;
  genre: string;
  mood_match_score: number;
  why_this_mood: string;
  estimated_pages: number;
}

const MoodSelector: React.FC = () => {
  const [moods, setMoods] = useState<MoodSelections>({
    energy: 'balanced',
    pacing: 'medium',
    tone: 'balanced',
    complexity: 'medium'
  });

  const [recommendations, setRecommendations] = useState<MoodRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMoodChange = (dimension: keyof MoodSelections, value: string) => {
    setMoods(prev => ({ ...prev, [dimension]: value }));
  };

  const getRecommendations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/enhanced/recommendations/mood-based`,
        { mood_selections: moods, count: 3 }
      );

      setRecommendations(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mood-selector">
      <h2>What are you in the mood for?</h2>
      <p className="subtitle">Select your preferences to get perfectly matched recommendations</p>

      <div className="mood-controls">
        {/* Energy Level */}
        <div className="mood-dimension">
          <label>Energy Level</label>
          <div className="mood-options">
            {['light', 'balanced', 'heavy'].map(option => (
              <button
                key={option}
                className={`mood-btn ${moods.energy === option ? 'active' : ''}`}
                onClick={() => handleMoodChange('energy', option)}
              >
                {option === 'light' ? '☀️ Light' : option === 'balanced' ? '⚖️ Balanced' : '🌙 Heavy'}
              </button>
            ))}
          </div>
        </div>

        {/* Pacing */}
        <div className="mood-dimension">
          <label>Pacing</label>
          <div className="mood-options">
            {['slow', 'medium', 'fast'].map(option => (
              <button
                key={option}
                className={`mood-btn ${moods.pacing === option ? 'active' : ''}`}
                onClick={() => handleMoodChange('pacing', option)}
              >
                {option === 'slow' ? '🐢 Slow-burn' : option === 'medium' ? '🚶 Medium' : '🏃 Fast-paced'}
              </button>
            ))}
          </div>
        </div>

        {/* Emotional Tone */}
        <div className="mood-dimension">
          <label>Emotional Tone</label>
          <div className="mood-options">
            {['dark', 'balanced', 'hopeful'].map(option => (
              <button
                key={option}
                className={`mood-btn ${moods.tone === option ? 'active' : ''}`}
                onClick={() => handleMoodChange('tone', option)}
              >
                {option === 'dark' ? '🌑 Dark' : option === 'balanced' ? '🌗 Balanced' : '🌞 Hopeful'}
              </button>
            ))}
          </div>
        </div>

        {/* Complexity */}
        <div className="mood-dimension">
          <label>Intellectual Demand</label>
          <div className="mood-options">
            {['escapist', 'medium', 'thought-provoking'].map(option => (
              <button
                key={option}
                className={`mood-btn ${moods.complexity === option ? 'active' : ''}`}
                onClick={() => handleMoodChange('complexity', option)}
              >
                {option === 'escapist' ? '🌈 Escapist' : option === 'medium' ? '📚 Medium' : '🧠 Deep'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <button
        className="btn btn-primary mood-submit"
        onClick={getRecommendations}
        disabled={isLoading}
      >
        {isLoading ? 'Finding perfect matches...' : 'Get Recommendations'}
      </button>

      {error && <div className="error">{error}</div>}

      {recommendations.length > 0 && (
        <div className="mood-recommendations">
          <h3>Perfect Matches for Your Mood</h3>
          <div className="recommendations-grid">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="mood-rec-card">
                <h4>{rec.title}</h4>
                <p className="author">by {rec.author}</p>
                <p className="genre">{rec.genre} • {rec.estimated_pages} pages</p>
                <div className="match-score">
                  Match: {(rec.mood_match_score * 100).toFixed(0)}%
                </div>
                <p className="why-mood">{rec.why_this_mood}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MoodSelector;
