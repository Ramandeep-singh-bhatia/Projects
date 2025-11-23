/**
 * Main App component with routing.
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import MyBooksPage from './pages/MyBooksPage';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        {/* Navigation */}
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-brand">
              📚 Book Recommender
            </Link>

            <div className="nav-links">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/my-books" className="nav-link">My Books</Link>
              <Link to="/dashboard" className="nav-link">Dashboard</Link>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/my-books" element={<MyBooksPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="footer">
          <p>Built with ❤️ using React, FastAPI, and Claude AI</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;
