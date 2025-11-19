-- Books table: Store book information
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE,
    genre TEXT NOT NULL,
    page_count INTEGER,
    cover_url TEXT,
    description TEXT,
    publication_year INTEGER,
    snoisle_available BOOLEAN DEFAULT 0,
    format_available TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reading log: Track user's reading activity
CREATE TABLE IF NOT EXISTS reading_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('to_read', 'reading', 'completed', 'dnf')),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_started TIMESTAMP,
    date_completed TIMESTAMP,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    reading_duration_days INTEGER,
    format_used TEXT,
    personal_notes TEXT,
    ai_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Recommendations: Store AI-generated recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    genre TEXT NOT NULL,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    score REAL,
    shown_to_user BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Reading stats: Daily reading statistics
CREATE TABLE IF NOT EXISTS reading_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    pages_read INTEGER DEFAULT 0,
    minutes_read INTEGER DEFAULT 0,
    books_completed_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User preferences: Store user reading preferences and profile
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reading goals: Track user's reading goals
CREATE TABLE IF NOT EXISTS reading_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_type TEXT NOT NULL CHECK(goal_type IN ('annual', 'monthly', 'genre_diversity', 'custom')),
    target_value INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    year INTEGER,
    month INTEGER,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_reading_log_status ON reading_log(status);
CREATE INDEX IF NOT EXISTS idx_reading_log_book_id ON reading_log(book_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_genre ON recommendations(genre);
CREATE INDEX IF NOT EXISTS idx_recommendations_active ON recommendations(is_active);
CREATE INDEX IF NOT EXISTS idx_reading_stats_date ON reading_stats(date);
