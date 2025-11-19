import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const db = new Database(join(__dirname, 'english-learning.db'));

// Enable foreign keys
db.pragma('foreign_keys = ON');

// ===== EXISTING TABLES =====

// User profile and settings
db.exec(`
  CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    current_level TEXT DEFAULT 'beginner',
    proficiency_score INTEGER DEFAULT 0,
    freeze_days_remaining INTEGER DEFAULT 2,
    last_freeze_reset DATE,
    learning_goal_minutes INTEGER DEFAULT 30,
    preferred_practice_time TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Learning progress tracking
db.exec(`
  CREATE TABLE IF NOT EXISTS learning_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skill_type TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    exercises_completed INTEGER DEFAULT 0,
    total_time_minutes INTEGER DEFAULT 0,
    best_score INTEGER DEFAULT 0,
    average_score INTEGER DEFAULT 0,
    last_practiced DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Vocabulary tracking
db.exec(`
  CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    definition TEXT,
    difficulty_level TEXT,
    context_examples TEXT,
    frequency_rank INTEGER,
    word_family TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// User vocabulary mastery
db.exec(`
  CREATE TABLE IF NOT EXISTS user_vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    vocabulary_id INTEGER NOT NULL,
    mastery_level INTEGER DEFAULT 0,
    times_seen INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    times_used INTEGER DEFAULT 0,
    personal_example TEXT,
    last_reviewed DATETIME DEFAULT CURRENT_TIMESTAMP,
    next_review DATETIME,
    last_used DATETIME,
    FOREIGN KEY (user_id) REFERENCES user_profile(id),
    FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
  );
`);

// Exercise history
db.exec(`
  CREATE TABLE IF NOT EXISTS exercise_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_type TEXT NOT NULL,
    exercise_data TEXT,
    user_response TEXT,
    ai_feedback TEXT,
    score INTEGER,
    duration_seconds INTEGER,
    energy_level TEXT,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Conversation scenarios
db.exec(`
  CREATE TABLE IF NOT EXISTS conversation_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty_level TEXT NOT NULL,
    scenario_context TEXT NOT NULL,
    learning_objectives TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Writing prompts
db.exec(`
  CREATE TABLE IF NOT EXISTS writing_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    difficulty_level TEXT NOT NULL,
    category TEXT,
    learning_focus TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Grammar rules and exercises
db.exec(`
  CREATE TABLE IF NOT EXISTS grammar_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    difficulty_level TEXT NOT NULL,
    rule_explanation TEXT,
    examples TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Weekly challenges
db.exec(`
  CREATE TABLE IF NOT EXISTS weekly_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_number INTEGER NOT NULL,
    year INTEGER NOT NULL,
    challenge_type TEXT NOT NULL,
    challenge_data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// User achievements
db.exec(`
  CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_type TEXT NOT NULL,
    achievement_name TEXT NOT NULL,
    achievement_description TEXT,
    icon_name TEXT,
    achieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Mistakes journal
db.exec(`
  CREATE TABLE IF NOT EXISTS mistakes_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mistake_type TEXT NOT NULL,
    mistake_category TEXT,
    original_text TEXT,
    corrected_text TEXT,
    explanation TEXT,
    severity TEXT DEFAULT 'moderate',
    times_repeated INTEGER DEFAULT 1,
    resolved BOOLEAN DEFAULT 0,
    occurred_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Daily streaks
db.exec(`
  CREATE TABLE IF NOT EXISTS daily_streaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    streak_count INTEGER DEFAULT 0,
    last_activity_date DATE,
    longest_streak INTEGER DEFAULT 0,
    freeze_days_used INTEGER DEFAULT 0,
    total_practice_days INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// ===== NEW ADVANCED FEATURES TABLES =====

// Personal contexts for vocabulary
db.exec(`
  CREATE TABLE IF NOT EXISTS personal_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    context_name TEXT NOT NULL,
    context_category TEXT,
    description TEXT,
    color_code TEXT,
    icon_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Vocabulary to context mapping
db.exec(`
  CREATE TABLE IF NOT EXISTS vocabulary_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vocabulary_id INTEGER NOT NULL,
    context_id INTEGER NOT NULL,
    relevance_score INTEGER DEFAULT 5,
    FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id),
    FOREIGN KEY (context_id) REFERENCES personal_contexts(id)
  );
`);

// Context cards
db.exec(`
  CREATE TABLE IF NOT EXISTS context_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    vocabulary_id INTEGER NOT NULL,
    personal_example TEXT NOT NULL,
    usage_contexts TEXT,
    common_mistakes TEXT,
    related_words TEXT,
    last_reviewed DATETIME,
    review_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id),
    FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
  );
`);

// Error patterns tracking
db.exec(`
  CREATE TABLE IF NOT EXISTS error_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    error_type TEXT NOT NULL,
    error_description TEXT,
    occurrence_count INTEGER DEFAULT 1,
    examples TEXT,
    correction_strategy TEXT,
    improvement_rate REAL DEFAULT 0,
    last_occurred DATETIME DEFAULT CURRENT_TIMESTAMP,
    first_occurred DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// AI recommendations history
db.exec(`
  CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommendation_type TEXT NOT NULL,
    recommendation_text TEXT NOT NULL,
    priority INTEGER DEFAULT 3,
    reason TEXT,
    action_taken BOOLEAN DEFAULT 0,
    dismissed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acted_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Daily wins tracker
db.exec(`
  CREATE TABLE IF NOT EXISTS daily_wins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    win_description TEXT NOT NULL,
    win_category TEXT,
    emotional_value INTEGER DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Milestones
db.exec(`
  CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    milestone_type TEXT NOT NULL,
    milestone_name TEXT NOT NULL,
    milestone_description TEXT,
    target_value INTEGER,
    current_value INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT 0,
    celebrated BOOLEAN DEFAULT 0,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Micro lessons
db.exec(`
  CREATE TABLE IF NOT EXISTS micro_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    lesson_type TEXT NOT NULL,
    content TEXT NOT NULL,
    difficulty_level TEXT,
    duration_minutes INTEGER DEFAULT 3,
    focus_skill TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Voice journals
db.exec(`
  CREATE TABLE IF NOT EXISTS voice_journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    audio_duration_seconds INTEGER,
    transcription TEXT,
    ai_analysis TEXT,
    speaking_score INTEGER,
    vocabulary_used TEXT,
    mistakes_found TEXT,
    improvements_noted TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Learning analytics snapshots
db.exec(`
  CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    vocabulary_mastered INTEGER DEFAULT 0,
    grammar_score INTEGER DEFAULT 0,
    fluency_score INTEGER DEFAULT 0,
    total_practice_time INTEGER DEFAULT 0,
    exercises_completed INTEGER DEFAULT 0,
    average_score INTEGER DEFAULT 0,
    learning_velocity REAL DEFAULT 0,
    retention_rate REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Session performance tracking
db.exec(`
  CREATE TABLE IF NOT EXISTS session_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    time_of_day TEXT,
    duration_minutes INTEGER,
    exercises_completed INTEGER DEFAULT 0,
    average_score INTEGER,
    energy_level TEXT,
    focus_quality INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Word avoidance tracking
db.exec(`
  CREATE TABLE IF NOT EXISTS word_avoidance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    alternative_used TEXT,
    opportunities_count INTEGER DEFAULT 1,
    last_avoided DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Overused phrases tracking
db.exec(`
  CREATE TABLE IF NOT EXISTS overused_phrases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    phrase TEXT NOT NULL,
    usage_count INTEGER DEFAULT 1,
    alternatives_suggested TEXT,
    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Create indexes for better query performance
db.exec(`
  CREATE INDEX IF NOT EXISTS idx_user_vocabulary_user ON user_vocabulary(user_id);
  CREATE INDEX IF NOT EXISTS idx_user_vocabulary_next_review ON user_vocabulary(next_review);
  CREATE INDEX IF NOT EXISTS idx_exercise_history_user ON exercise_history(user_id);
  CREATE INDEX IF NOT EXISTS idx_exercise_history_date ON exercise_history(completed_at);
  CREATE INDEX IF NOT EXISTS idx_learning_progress_user ON learning_progress(user_id);
  CREATE INDEX IF NOT EXISTS idx_mistakes_journal_user ON mistakes_journal(user_id);
  CREATE INDEX IF NOT EXISTS idx_mistakes_journal_type ON mistakes_journal(mistake_category);
  CREATE INDEX IF NOT EXISTS idx_error_patterns_user ON error_patterns(user_id);
  CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id);
  CREATE INDEX IF NOT EXISTS idx_recommendations_active ON recommendations(user_id, dismissed, action_taken);
  CREATE INDEX IF NOT EXISTS idx_context_cards_user ON context_cards(user_id);
  CREATE INDEX IF NOT EXISTS idx_analytics_snapshots_user_date ON analytics_snapshots(user_id, snapshot_date);
  CREATE INDEX IF NOT EXISTS idx_daily_wins_user_date ON daily_wins(user_id, created_at);
`);

// Insert default user if not exists
const userCount = db.prepare('SELECT COUNT(*) as count FROM user_profile').get();
if (userCount.count === 0) {
  db.prepare(`
    INSERT INTO user_profile (username, current_level, proficiency_score, freeze_days_remaining, learning_goal_minutes)
    VALUES ('default_user', 'beginner', 0, 2, 30)
  `).run();

  const userId = db.prepare('SELECT id FROM user_profile WHERE username = ?').get('default_user').id;

  // Initialize progress tracking for all skills
  const skills = ['vocabulary', 'grammar', 'fluency', 'context_usage', 'writing_quality'];
  const insertProgress = db.prepare(`
    INSERT INTO learning_progress (user_id, skill_type, score, best_score, average_score)
    VALUES (?, ?, 0, 0, 0)
  `);

  for (const skill of skills) {
    insertProgress.run(userId, skill);
  }

  // Initialize daily streak
  db.prepare(`
    INSERT INTO daily_streaks (user_id, streak_count, last_activity_date, longest_streak, total_practice_days)
    VALUES (?, 0, DATE('now'), 0, 0)
  `).run(userId);

  // Create default personal contexts
  const defaultContexts = [
    { name: 'Work & Professional', category: 'professional', color: '#3b82f6', icon: 'Briefcase' },
    { name: 'Daily Life & Routine', category: 'daily', color: '#10b981', icon: 'Home' },
    { name: 'Social & Friends', category: 'social', color: '#f59e0b', icon: 'Users' },
    { name: 'Family & Personal', category: 'personal', color: '#ec4899', icon: 'Heart' },
    { name: 'Hobbies & Interests', category: 'hobbies', color: '#8b5cf6', icon: 'Star' },
  ];

  const insertContext = db.prepare(`
    INSERT INTO personal_contexts (user_id, context_name, context_category, color_code, icon_name)
    VALUES (?, ?, ?, ?, ?)
  `);

  for (const context of defaultContexts) {
    insertContext.run(userId, context.name, context.category, context.color, context.icon);
  }

  // Create initial milestones
  const initialMilestones = [
    { type: 'vocabulary', name: 'First 100 Words', description: 'Master your first 100 vocabulary words', target: 100 },
    { type: 'streak', name: '7-Day Streak', description: 'Practice for 7 days in a row', target: 7 },
    { type: 'streak', name: '30-Day Streak', description: 'Practice for 30 days in a row', target: 30 },
    { type: 'exercises', name: '100 Exercises', description: 'Complete 100 practice exercises', target: 100 },
    { type: 'proficiency', name: 'Intermediate Level', description: 'Reach intermediate proficiency', target: 60 },
  ];

  const insertMilestone = db.prepare(`
    INSERT INTO milestones (user_id, milestone_type, milestone_name, milestone_description, target_value)
    VALUES (?, ?, ?, ?, ?)
  `);

  for (const milestone of initialMilestones) {
    insertMilestone.run(userId, milestone.type, milestone.name, milestone.description, milestone.target);
  }
}

console.log('✓ Database initialized successfully with advanced features!');
console.log('✓ Database location:', join(__dirname, 'english-learning.db'));
console.log('✓ Added tables for:');
console.log('  - Personal contexts and context cards');
console.log('  - Error pattern recognition');
console.log('  - AI recommendations');
console.log('  - Daily wins and milestones');
console.log('  - Micro lessons and voice journals');
console.log('  - Learning analytics and session tracking');
console.log('  - Word avoidance and overuse detection');

db.close();
