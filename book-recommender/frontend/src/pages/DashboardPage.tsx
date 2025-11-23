/**
 * Dashboard page with reading statistics and analytics.
 */
import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { getDashboardStats, getGenreStats, getReadingPatterns, DashboardStats } from '../services/api';
import '../styles/DashboardPage.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const MONTH_NAMES = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [genreStats, setGenreStats] = useState<any[]>([]);
  const [readingPatterns, setReadingPatterns] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, genreRes, patternsRes] = await Promise.all([
        getDashboardStats(),
        getGenreStats(),
        getReadingPatterns()
      ]);

      setStats(statsRes.data);
      setGenreStats(genreRes.data);
      setReadingPatterns(patternsRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="loading-page">Loading dashboard...</div>;
  }

  // Prepare data for charts
  const genreDistribution = stats?.genre_distribution
    ? Object.entries(stats.genre_distribution).map(([name, value]) => ({
        name,
        value
      }))
    : [];

  const monthlyTrends = stats?.monthly_trends
    ? stats.monthly_trends.map((trend: any) => ({
        month: MONTH_NAMES[trend.month - 1],
        books: trend.books_completed,
        pages: trend.pages_read,
        rating: trend.avg_rating
      }))
    : [];

  return (
    <div className="dashboard-page">
      <h1>Reading Dashboard</h1>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-box">
          <h3>Books Read (Year)</h3>
          <div className="stat-number">{stats?.books_read_year || 0}</div>
        </div>
        <div className="stat-box">
          <h3>Books Read (All Time)</h3>
          <div className="stat-number">{stats?.books_read_all_time || 0}</div>
        </div>
        <div className="stat-box">
          <h3>Total Pages</h3>
          <div className="stat-number">{stats?.pages_read_total.toLocaleString() || 0}</div>
        </div>
        <div className="stat-box">
          <h3>Avg Speed</h3>
          <div className="stat-number">{stats?.average_reading_speed || 0} <span className="unit">pages/day</span></div>
        </div>
        <div className="stat-box">
          <h3>Completion Rate</h3>
          <div className="stat-number">{stats?.completion_rate || 0}%</div>
        </div>
        <div className="stat-box">
          <h3>Current Streak</h3>
          <div className="stat-number">{stats?.current_streak_days || 0} <span className="unit">days</span></div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        {/* Monthly Trends */}
        {monthlyTrends.length > 0 && (
          <div className="chart-container">
            <h2>Monthly Reading Trends</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="books" stroke="#8884d8" name="Books Completed" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Genre Distribution */}
        {genreDistribution.length > 0 && (
          <div className="chart-container">
            <h2>Genre Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={genreDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {genreDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Genre Stats Table */}
        {genreStats.length > 0 && (
          <div className="chart-container">
            <h2>Genre Statistics</h2>
            <table className="genre-stats-table">
              <thead>
                <tr>
                  <th>Genre</th>
                  <th>Books Read</th>
                  <th>Avg Rating</th>
                  <th>Total Pages</th>
                  <th>Completion Rate</th>
                </tr>
              </thead>
              <tbody>
                {genreStats.map((genre: any, idx: number) => (
                  <tr key={idx}>
                    <td>{genre.genre}</td>
                    <td>{genre.books_read}</td>
                    <td>{genre.average_rating.toFixed(1)} ★</td>
                    <td>{genre.total_pages.toLocaleString()}</td>
                    <td>{genre.completion_rate.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Reading Patterns */}
      {readingPatterns && (
        <div className="patterns-section">
          <h2>Reading Patterns</h2>
          <div className="patterns-grid">
            <div className="pattern-card">
              <h3>Favorite Genres</h3>
              <ul>
                {readingPatterns.favorite_genres.map((genre: string, idx: number) => (
                  <li key={idx}>{genre}</li>
                ))}
              </ul>
            </div>
            <div className="pattern-card">
              <h3>Average Book Length</h3>
              <p className="big-number">{readingPatterns.average_book_length} pages</p>
            </div>
            <div className="pattern-card">
              <h3>Genre Diversity</h3>
              <p className="big-number">{readingPatterns.genre_diversity_score.toFixed(1)}%</p>
            </div>
            <div className="pattern-card">
              <h3>Reading Velocity</h3>
              <p className="big-number capitalize">{readingPatterns.reading_velocity_trend}</p>
            </div>
          </div>
        </div>
      )}

      {/* Top Rated Books */}
      {stats?.top_rated_books && stats.top_rated_books.length > 0 && (
        <div className="top-rated-section">
          <h2>Top Rated Books</h2>
          <div className="books-list">
            {stats.top_rated_books.map((book: any) => (
              <div key={book.id} className="book-item">
                <img
                  src={book.cover_url || '/placeholder-book.png'}
                  alt={book.title}
                  className="book-cover-tiny"
                />
                <div className="book-details">
                  <h4>{book.title}</h4>
                  <p>{book.author}</p>
                  <div className="rating">
                    {'★'.repeat(book.rating)}{'☆'.repeat(5 - book.rating)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
