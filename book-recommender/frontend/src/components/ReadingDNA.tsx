/**
 * Reading DNA Component - Display reading personality profile
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface ReadingDNA {
  character_vs_plot_score: number;
  narrative_preferences: any;
  complexity_profile: any;
  thematic_dna: Array<{theme: string; frequency: number; importance: string}>;
  writing_style_preferences: any;
  character_patterns: any;
  reading_personality_summary: string;
  recommendations_guidance: string;
  unique_traits: string[];
}

const ReadingDNA: React.FC = () => {
  const [dna, setDna] = useState<ReadingDNA | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadReadingDNA();
  }, []);

  const loadReadingDNA = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/enhanced/recommendations/reading-dna`
      );

      setDna(response.data);
    } catch (err: any) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to load Reading DNA');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="loading-page">Analyzing your Reading DNA...</div>;
  }

  if (error) {
    return (
      <div className="error-page">
        <h2>{error}</h2>
        <p>Read and rate at least 5 books to unlock your Reading DNA profile!</p>
      </div>
    );
  }

  if (!dna) {
    return null;
  }

  // Calculate character vs plot percentage
  const charPlotScore = ((dna.character_vs_plot_score + 1) / 2) * 100;

  return (
    <div className="reading-dna-page">
      <h1>Your Reading DNA</h1>
      <p className="subtitle">A deep analysis of your unique reading personality</p>

      {/* Personality Summary */}
      <div className="dna-section personality-summary">
        <h2>Your Reading Personality</h2>
        <p className="dna-narrative">{dna.reading_personality_summary}</p>
      </div>

      {/* Character vs Plot */}
      <div className="dna-section">
        <h2>Narrative Style Preference</h2>
        <div className="character-plot-meter">
          <div className="meter-labels">
            <span>Plot-Driven</span>
            <span>Character-Driven</span>
          </div>
          <div className="meter-bar">
            <div
              className="meter-fill"
              style={{ width: `${charPlotScore}%` }}
            />
            <div
              className="meter-indicator"
              style={{ left: `${charPlotScore}%` }}
            />
          </div>
          <p className="meter-description">
            {dna.narrative_preferences?.structure || 'Balanced preference'}
          </p>
        </div>
      </div>

      {/* Thematic Interests */}
      {dna.thematic_dna && dna.thematic_dna.length > 0 && (
        <div className="dna-section">
          <h2>Top Themes You Love</h2>
          <div className="themes-grid">
            {dna.thematic_dna.slice(0, 5).map((theme, idx) => (
              <div key={idx} className={`theme-card importance-${theme.importance}`}>
                <h3>{theme.theme}</h3>
                <p className="frequency">{theme.frequency} books</p>
                <span className={`importance-badge ${theme.importance}`}>
                  {theme.importance}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Complexity Profile */}
      {dna.complexity_profile && (
        <div className="dna-section">
          <h2>Complexity Comfort Zone</h2>
          <div className="complexity-stats">
            <div className="complexity-card">
              <h4>Comfort Level</h4>
              <div className="big-number">{dna.complexity_profile.comfort_level}/10</div>
            </div>
            <div className="complexity-card">
              <h4>Vocabulary Challenge</h4>
              <p>{dna.complexity_profile.vocabulary_challenge}</p>
            </div>
            <div className="complexity-card">
              <h4>Theme Depth</h4>
              <p>{dna.complexity_profile.theme_depth}</p>
            </div>
          </div>
        </div>
      )}

      {/* Writing Style */}
      {dna.writing_style_preferences && (
        <div className="dna-section">
          <h2>Writing Style Preferences</h2>
          <div className="style-grid">
            <div className="style-item">
              <strong>Prose:</strong>
              <p>{dna.writing_style_preferences.prose}</p>
            </div>
            <div className="style-item">
              <strong>Dialogue:</strong>
              <p>{dna.writing_style_preferences.dialogue_importance}</p>
            </div>
            <div className="style-item">
              <strong>Atmosphere:</strong>
              <p>{dna.writing_style_preferences.atmosphere}</p>
            </div>
          </div>
        </div>
      )}

      {/* Unique Traits */}
      {dna.unique_traits && dna.unique_traits.length > 0 && (
        <div className="dna-section">
          <h2>Your Unique Reading Traits</h2>
          <ul className="traits-list">
            {dna.unique_traits.map((trait, idx) => (
              <li key={idx}>{trait}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations Guidance */}
      <div className="dna-section recommendations-guidance">
        <h2>How to Use Your DNA</h2>
        <p>{dna.recommendations_guidance}</p>
      </div>

      <button className="btn btn-primary" onClick={loadReadingDNA}>
        Regenerate DNA Profile
      </button>
    </div>
  );
};

export default ReadingDNA;
