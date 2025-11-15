import { useState, useEffect } from 'react';
import { analyticsService } from '../services/api';
import { AnalyticsSummary, PracticeSession } from '../types';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AnalyticsPage = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [recentActivity, setRecentActivity] = useState<PracticeSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const [summaryRes, activityRes] = await Promise.all([
        analyticsService.getSummary(),
        analyticsService.getRecentActivity(10),
      ]);
      setSummary(summaryRes.data);
      setRecentActivity(activityRes.data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  if (!summary) {
    return <div className="text-center py-8">No data available</div>;
  }

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

  const categoryData = Object.entries(summary.topicsByCategory || {}).map(([name, value]) => ({
    name,
    value,
  }));

  const timeData = Object.entries(summary.timeByCategory || {}).map(([name, value]) => ({
    name,
    value,
  }));

  const confidenceData = Object.entries(summary.topicsByConfidenceLevel || {}).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Analytics</h1>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Topics</h3>
          <div className="text-3xl font-bold">{summary.totalTopics}</div>
        </div>
        <div className="card">
          <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Sessions</h3>
          <div className="text-3xl font-bold">{summary.totalSessions}</div>
        </div>
        <div className="card">
          <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Time</h3>
          <div className="text-3xl font-bold">{Math.floor(summary.totalTimeSpent / 60)}h {summary.totalTimeSpent % 60}m</div>
        </div>
        <div className="card">
          <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Confidence</h3>
          <div className="text-3xl font-bold">{summary.averageConfidence.toFixed(1)}/10</div>
        </div>
      </div>

      {/* Study Streak */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="card">
          <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Current Streak</h3>
          <div className="text-3xl font-bold text-primary-600">{summary.currentStreak} days</div>
        </div>
        <div className="card">
          <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Longest Streak</h3>
          <div className="text-3xl font-bold text-green-600">{summary.longestStreak} days</div>
        </div>
        <div className="card">
          <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Days This Month</h3>
          <div className="text-3xl font-bold text-yellow-600">{summary.daysStudiedThisMonth} days</div>
        </div>
      </div>

      {/* Time Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Topics by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Time by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={timeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Topics by Confidence */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Topics by Confidence Level</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={confidenceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        {recentActivity.length === 0 ? (
          <div className="text-center py-4 text-gray-500">No recent activity</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b dark:border-gray-700">
                  <th className="text-left py-2">Date</th>
                  <th className="text-left py-2">Duration</th>
                  <th className="text-left py-2">Performance</th>
                  <th className="text-left py-2">Type</th>
                </tr>
              </thead>
              <tbody>
                {recentActivity.map((session) => (
                  <tr key={session.id} className="border-b dark:border-gray-700">
                    <td className="py-2">{new Date(session.sessionDate!).toLocaleDateString()}</td>
                    <td className="py-2">{session.duration} mins</td>
                    <td className="py-2">{session.performanceRating}/10</td>
                    <td className="py-2">{session.sessionType.replace('_', ' ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsPage;
