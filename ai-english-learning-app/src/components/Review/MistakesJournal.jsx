import React from 'react';
import { AlertCircle, TrendingDown } from 'lucide-react';
import useAppStore from '../../stores/appStore';
import './Review.css';

const MistakesJournal = () => {
  const { mistakes } = useAppStore();

  const getMistakesByType = () => {
    const grouped = {};
    mistakes.forEach(mistake => {
      if (!grouped[mistake.mistake_type]) {
        grouped[mistake.mistake_type] = [];
      }
      grouped[mistake.mistake_type].push(mistake);
    });
    return grouped;
  };

  const groupedMistakes = getMistakesByType();

  return (
    <div className="mistakes-journal">
      <div className="journal-header">
        <div>
          <h1><AlertCircle size={32} /> Mistakes Journal</h1>
          <p>Learn from your mistakes to improve faster</p>
        </div>
      </div>

      {mistakes.length > 0 ? (
        <>
          <div className="mistakes-stats">
            <div className="stat-card">
              <div className="stat-value">{mistakes.length}</div>
              <div className="stat-label">Total Mistakes</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{Object.keys(groupedMistakes).length}</div>
              <div className="stat-label">Categories</div>
            </div>
            <div className="stat-card">
              <TrendingDown size={24} className="improvement-icon" />
              <div className="stat-label">Improving</div>
            </div>
          </div>

          <div className="mistakes-list">
            {Object.entries(groupedMistakes).map(([type, typeMistakes]) => (
              <div key={type} className="mistake-category">
                <h3 className="category-title">
                  {type.replace('_', ' ').toUpperCase()}
                  <span className="count-badge">{typeMistakes.length}</span>
                </h3>
                {typeMistakes.slice(0, 10).map((mistake, index) => (
                  <div key={index} className="mistake-card">
                    <div className="mistake-time">
                      {new Date(mistake.occurred_at).toLocaleDateString()}
                    </div>
                    {mistake.original_text && (
                      <div className="mistake-original">
                        <strong>Original:</strong> {mistake.original_text}
                      </div>
                    )}
                    {mistake.corrected_text && (
                      <div className="mistake-corrected">
                        <strong>Corrected:</strong> {mistake.corrected_text}
                      </div>
                    )}
                    {mistake.explanation && (
                      <div className="mistake-explanation">
                        <strong>Explanation:</strong> {mistake.explanation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="empty-state">
          <AlertCircle size={64} />
          <h3>No Mistakes Recorded Yet</h3>
          <p>Keep practicing! Your mistakes will be tracked here to help you improve.</p>
        </div>
      )}
    </div>
  );
};

export default MistakesJournal;
