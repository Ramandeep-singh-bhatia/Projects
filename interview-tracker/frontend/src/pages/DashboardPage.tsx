import { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import { DashboardSuggestion, WeeklyProgress } from '../types';

const DashboardPage = () => {
  const [suggestions, setSuggestions] = useState<DashboardSuggestion[]>([]);
  const [weeklyProgress, setWeeklyProgress] = useState<WeeklyProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('');

  useEffect(() => {
    loadDashboardData();
  }, [filter]);

  const loadDashboardData = async () => {
    try {
      const [suggestionsRes, progressRes] = await Promise.all([
        dashboardService.getSuggestions(filter, 15),
        dashboardService.getWeeklyProgress(),
      ]);
      setSuggestions(suggestionsRes.data);
      setWeeklyProgress(progressRes.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    if (status === 'GREEN') return 'bg-green-500';
    if (status === 'YELLOW') return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      {/* Weekly Progress */}
      {weeklyProgress && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Weekly Progress</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'DSA', goal: weeklyProgress.dsaGoal, actual: weeklyProgress.dsaActual, status: weeklyProgress.dsaStatus, percentage: weeklyProgress.dsaPercentage },
              { label: 'HLD', goal: weeklyProgress.hldGoal, actual: weeklyProgress.hldActual, status: weeklyProgress.hldStatus, percentage: weeklyProgress.hldPercentage },
              { label: 'LLD', goal: weeklyProgress.lldGoal, actual: weeklyProgress.lldActual, status: weeklyProgress.lldStatus, percentage: weeklyProgress.lldPercentage },
              { label: 'Behavioral', goal: weeklyProgress.behavioralGoal, actual: weeklyProgress.behavioralActual, status: weeklyProgress.behavioralStatus, percentage: weeklyProgress.behavioralPercentage },
            ].map((item) => (
              <div key={item.label} className="card">
                <h3 className="font-semibold mb-2">{item.label}</h3>
                <div className="text-2xl font-bold mb-2">
                  {item.actual} / {item.goal}
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
                  <div
                    className={`h-2 rounded-full ${getStatusColor(item.status)}`}
                    style={{ width: `${Math.min(item.percentage, 100)}%` }}
                  ></div>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {item.percentage.toFixed(0)}% Complete
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Revision Suggestions */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-semibold">Suggested Topics to Revise</h2>
          <select
            className="input w-48"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="DSA">DSA</option>
            <option value="HLD">HLD</option>
            <option value="LLD">LLD</option>
            <option value="BEHAVIORAL">Behavioral</option>
          </select>
        </div>

        {suggestions.length === 0 ? (
          <div className="card text-center py-8 text-gray-500">
            No suggestions available. Start adding topics!
          </div>
        ) : (
          <div className="grid gap-4">
            {suggestions.map((suggestion, index) => (
              <div key={suggestion.topicId} className="card hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                      <h3 className="text-xl font-semibold">{suggestion.topic}</h3>
                      {suggestion.subtopic && (
                        <span className="text-sm text-gray-500">({suggestion.subtopic})</span>
                      )}
                      <span className="px-2 py-1 rounded bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 text-xs">
                        {suggestion.category}
                      </span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span>Confidence: {suggestion.confidence}/10</span>
                      <span>Last studied: {suggestion.daysSinceLastStudied} days ago</span>
                      <span>Est. time: {suggestion.estimatedTime} mins</span>
                      {suggestion.difficulty && (
                        <span className={`px-2 py-1 rounded ${
                          suggestion.difficulty === 'EASY' ? 'bg-green-100 text-green-800' :
                          suggestion.difficulty === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {suggestion.difficulty}
                        </span>
                      )}
                      <span className="text-primary-600 font-medium">
                        Priority: {suggestion.priorityScore.toFixed(2)}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => window.location.href = `/${suggestion.category.toLowerCase()}`}
                    className="btn btn-primary"
                  >
                    Start Practice
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
