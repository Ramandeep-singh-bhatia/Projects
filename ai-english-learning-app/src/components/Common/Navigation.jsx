import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  BookOpen,
  MessageSquare,
  FileText,
  Award,
  Settings as SettingsIcon,
  Menu,
  X,
} from 'lucide-react';
import useAppStore from '../../stores/appStore';
import './Navigation.css';

const Navigation = ({ onSettingsClick }) => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, streak } = useAppStore();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/conversation', icon: MessageSquare, label: 'Conversation' },
    { path: '/vocabulary', icon: BookOpen, label: 'Vocabulary' },
    { path: '/writing', icon: FileText, label: 'Writing' },
    { path: '/challenge', icon: Award, label: 'Challenge' },
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <BookOpen className="brand-icon" />
          <span className="brand-name">AI English Learning</span>
        </div>

        <button
          className="mobile-menu-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        <div className={`nav-links ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </Link>
          ))}
        </div>

        <div className="nav-actions">
          <div className="streak-display">
            <span className="streak-icon">🔥</span>
            <span className="streak-count">{streak.current || 0}</span>
          </div>

          <div className="user-level">
            <span className="level-badge">{user.currentLevel}</span>
          </div>

          <button className="settings-btn" onClick={onSettingsClick}>
            <SettingsIcon size={20} />
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
