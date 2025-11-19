import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const db = new Database(join(__dirname, 'english-learning.db'));

// Enable foreign keys
db.pragma('foreign_keys = ON');

// User profile and settings
db.exec(`
  CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    current_level TEXT DEFAULT 'beginner',
    proficiency_score INTEGER DEFAULT 0,
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
    last_reviewed DATETIME DEFAULT CURRENT_TIMESTAMP,
    next_review DATETIME,
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
    original_text TEXT,
    corrected_text TEXT,
    explanation TEXT,
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
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
  );
`);

// Create indexes for better query performance
db.exec(`
  CREATE INDEX IF NOT EXISTS idx_user_vocabulary_user ON user_vocabulary(user_id);
  CREATE INDEX IF NOT EXISTS idx_exercise_history_user ON exercise_history(user_id);
  CREATE INDEX IF NOT EXISTS idx_learning_progress_user ON learning_progress(user_id);
  CREATE INDEX IF NOT EXISTS idx_mistakes_journal_user ON mistakes_journal(user_id);
`);

// Insert default user if not exists
const userCount = db.prepare('SELECT COUNT(*) as count FROM user_profile').get();
if (userCount.count === 0) {
  db.prepare(`
    INSERT INTO user_profile (username, current_level, proficiency_score)
    VALUES ('default_user', 'beginner', 0)
  `).run();

  const userId = db.prepare('SELECT id FROM user_profile WHERE username = ?').get('default_user').id;

  // Initialize progress tracking for all skills
  const skills = ['vocabulary', 'grammar', 'fluency', 'context_usage', 'writing_quality'];
  const insertProgress = db.prepare(`
    INSERT INTO learning_progress (user_id, skill_type, score)
    VALUES (?, ?, 0)
  `);

  for (const skill of skills) {
    insertProgress.run(userId, skill);
  }

  // Initialize daily streak
  db.prepare(`
    INSERT INTO daily_streaks (user_id, streak_count, last_activity_date, longest_streak)
    VALUES (?, 0, DATE('now'), 0)
  `).run(userId);
}

console.log('Database initialized successfully!');
console.log('Database location:', join(__dirname, 'english-learning.db'));

db.close();
