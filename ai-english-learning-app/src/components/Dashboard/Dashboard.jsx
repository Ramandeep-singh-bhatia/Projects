import React from 'react';
import { Link } from 'react-router-dom';
import {
  MessageSquare,
  BookOpen,
  FileText,
  Award,
  TrendingUp,
  Target,
  Clock,
  Star,
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import useAppStore from '../../stores/appStore';
import './Dashboard.css';

const Dashboard = () => {
  const { user, learningProgress, streak, exerciseHistory } = useAppStore();

  const skills = [
    { name: 'Vocabulary', score: learningProgress.vocabulary, color: '#6366f1' },
    { name: 'Grammar', score: learningProgress.grammar, color: '#10b981' },
    { name: 'Fluency', score: learningProgress.fluency, color: '#f59e0b' },
    { name: 'Context Usage', score: learningProgress.context_usage, color: '#8b5cf6' },
    { name: 'Writing', score: learningProgress.writing_quality, color: '#ec4899' },
  ];

  const modules = [
    {
      title: 'Conversation Practice',
      description: 'Role-play scenarios and contextual conversations',
      icon: MessageSquare,
      path: '/conversation',
      color: '#6366f1',
    },
    {
      title: 'Vocabulary Builder',
      description: 'Learn words in context and reinforce retention',
      icon: BookOpen,
      path: '/vocabulary',
      color: '#10b981',
    },
    {
      title: 'Writing Tasks',
      description: 'Improve your writing with AI feedback',
      icon: FileText,
      path: '/writing',
      color: '#f59e0b',
    },
    {
      title: 'Weekly Challenge',
      description: 'Test your skills with fun challenges',
      icon: Award,
      path: '/challenge',
      color: '#ec4899',
    },
  ];

  const recentActivity = exerciseHistory.slice(0, 5);

  // Generate mock progress data for the chart
  const getProgressChartData = () => {
    const data = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        score: user.proficiencyScore - (i * 2) + Math.random() * 5,
      });
    }
    return data;
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Welcome back, {user.username}! 👋</h1>
          <p className="dashboard-subtitle">
            You're on a {streak.current}-day streak! Keep up the great work!
          </p>
        </div>
        <div className="proficiency-badge">
          <div className="proficiency-score">{user.proficiencyScore}</div>
          <div className="proficiency-label">Proficiency Score</div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card progress-card">
          <div className="card-header">
            <h3>Your Progress</h3>
            <TrendingUp className="header-icon" />
          </div>
          <div className="progress-chart">
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={getProgressChartData()}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#6366f1"
                  strokeWidth={2}
                  dot={{ fill: '#6366f1' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="dashboard-card stats-card">
          <div className="card-header">
            <h3>Skills Overview</h3>
            <Target className="header-icon" />
          </div>
          <div className="skills-list">
            {skills.map((skill) => (
              <div key={skill.name} className="skill-item">
                <div className="skill-info">
                  <span className="skill-name">{skill.name}</span>
                  <span className="skill-score">{skill.score}</span>
                </div>
                <div className="skill-bar">
                  <div
                    className="skill-fill"
                    style={{
                      width: `${skill.score}%`,
                      backgroundColor: skill.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card activity-card">
          <div className="card-header">
            <h3>Recent Activity</h3>
            <Clock className="header-icon" />
          </div>
          <div className="activity-list">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity, index) => (
                <div key={index} className="activity-item">
                  <div className="activity-icon">
                    {activity.exercise_type === 'conversation' && <MessageSquare size={16} />}
                    {activity.exercise_type === 'vocabulary' && <BookOpen size={16} />}
                    {activity.exercise_type === 'writing' && <FileText size={16} />}
                    {activity.exercise_type === 'grammar' && <Star size={16} />}
                  </div>
                  <div className="activity-details">
                    <div className="activity-title">{activity.exercise_type}</div>
                    <div className="activity-time">
                      {new Date(activity.completed_at).toLocaleString()}
                    </div>
                  </div>
                  <div className={`activity-score score-${Math.floor(activity.score / 20)}`}>
                    {activity.score}
                  </div>
                </div>
              ))
            ) : (
              <p className="no-activity">No recent activity. Start practicing to see your progress!</p>
            )}
          </div>
        </div>
      </div>

      <div className="learning-modules">
        <h2>Learning Modules</h2>
        <div className="modules-grid">
          {modules.map((module) => (
            <Link
              key={module.path}
              to={module.path}
              className="module-card"
              style={{ '--module-color': module.color }}
            >
              <div className="module-icon">
                <module.icon size={32} />
              </div>
              <h3>{module.title}</h3>
              <p>{module.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
