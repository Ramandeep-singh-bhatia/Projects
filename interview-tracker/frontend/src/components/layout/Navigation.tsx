import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';

const Navigation = () => {
  const location = useLocation();
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.classList.toggle('dark');
  };

  const navLinks = [
    { path: '/', label: 'Dashboard' },
    { path: '/dsa', label: 'DSA' },
    { path: '/hld', label: 'HLD' },
    { path: '/lld', label: 'LLD' },
    { path: '/behavioral', label: 'Behavioral' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/settings', label: 'Settings' },
  ];

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              Interview Tracker
            </h1>
            <div className="hidden md:flex space-x-4">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === link.path
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
