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

-- TIER 1 & 2 ENHANCEMENTS

-- Reading Plans: Personalized reading roadmaps
CREATE TABLE IF NOT EXISTS reading_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name TEXT NOT NULL,
    goal TEXT,
    duration_days INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    target_end_date DATE,
    status TEXT CHECK(status IN ('active', 'completed', 'abandoned')) DEFAULT 'active',
    difficulty_progression TEXT,
    ai_reasoning TEXT
);

CREATE TABLE IF NOT EXISTS plan_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    sequence_order INTEGER,
    why_this_book TEXT,
    recommended_start_date DATE,
    actual_start_date DATE,
    completed_date DATE,
    FOREIGN KEY (plan_id) REFERENCES reading_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Mood System: Mood-based book recommendations
CREATE TABLE IF NOT EXISTS book_moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    mood_dimension TEXT NOT NULL, -- light_heavy, paced, tone, etc.
    mood_value INTEGER CHECK(mood_value BETWEEN 1 AND 5),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mood_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    selected_moods TEXT, -- JSON of mood selections
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommendations_generated TEXT -- JSON of book IDs recommended
);

-- Book Complexity: Track reading difficulty progression
CREATE TABLE IF NOT EXISTS book_complexity (
    book_id INTEGER PRIMARY KEY,
    complexity_score INTEGER CHECK(complexity_score BETWEEN 1 AND 10),
    vocabulary_level INTEGER CHECK(vocabulary_level BETWEEN 1 AND 10),
    structure_complexity INTEGER CHECK(structure_complexity BETWEEN 1 AND 10),
    theme_depth INTEGER CHECK(theme_depth BETWEEN 1 AND 10),
    calculated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_generated BOOLEAN DEFAULT 1,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Theme Tracking: Deep thematic analysis
CREATE TABLE IF NOT EXISTS book_themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    theme TEXT NOT NULL,
    confidence_score REAL DEFAULT 1.0,
    ai_generated BOOLEAN DEFAULT 1,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_theme_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme TEXT NOT NULL UNIQUE,
    preference_score REAL DEFAULT 0.0,
    books_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Series Management: Track book series
CREATE TABLE IF NOT EXISTS book_series (
    series_id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT NOT NULL UNIQUE,
    total_books INTEGER,
    primary_author TEXT,
    genre TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS series_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    book_number INTEGER,
    reading_order INTEGER,
    is_standalone BOOLEAN DEFAULT 0,
    FOREIGN KEY (series_id) REFERENCES book_series(series_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_series_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    books_completed INTEGER DEFAULT 0,
    current_book_id INTEGER,
    started_date TIMESTAMP,
    last_read_date TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES book_series(series_id) ON DELETE CASCADE,
    FOREIGN KEY (current_book_id) REFERENCES books(id) ON DELETE SET NULL
);

-- Vocabulary Builder: Track and learn new words
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    definition TEXT,
    pronunciation TEXT,
    part_of_speech TEXT,
    context_sentence TEXT,
    book_id INTEGER,
    page_number INTEGER,
    date_encountered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_reviewed INTEGER DEFAULT 0,
    mastery_level TEXT CHECK(mastery_level IN ('learning', 'familiar', 'mastered')) DEFAULT 'learning',
    next_review_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS vocabulary_review_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    knew_it BOOLEAN,
    review_interval_days INTEGER,
    FOREIGN KEY (word_id) REFERENCES vocabulary(id) ON DELETE CASCADE
);

-- Reading Journal: Enhanced note-taking
CREATE TABLE IF NOT EXISTS reading_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    note_type TEXT CHECK(note_type IN ('thought', 'quote', 'question', 'reaction', 'analysis')) DEFAULT 'thought',
    content TEXT NOT NULL,
    page_number INTEGER,
    chapter TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT, -- JSON array
    is_favorite BOOLEAN DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Reading Sessions: Detailed session tracking
CREATE TABLE IF NOT EXISTS reading_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    duration_minutes INTEGER,
    pages_read INTEGER,
    session_rating INTEGER CHECK(session_rating BETWEEN 1 AND 5),
    location TEXT,
    notes TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Predictions & Intelligence
CREATE TABLE IF NOT EXISTS completion_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_probability REAL CHECK(predicted_probability BETWEEN 0 AND 1),
    reasoning TEXT,
    confidence_level TEXT CHECK(confidence_level IN ('low', 'medium', 'high')),
    actual_completed BOOLEAN,
    prediction_accuracy REAL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reading_slumps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slump_start_date DATE,
    slump_end_date DATE,
    days_duration INTEGER,
    books_during_slump INTEGER DEFAULT 0,
    recovery_method TEXT,
    notes TEXT
);

-- Book Pairings: Complementary book suggestions
CREATE TABLE IF NOT EXISTS book_pairings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book1_id INTEGER NOT NULL,
    book2_id INTEGER NOT NULL,
    pairing_type TEXT CHECK(pairing_type IN ('learning_followup', 'perspective_flip', 'fiction_nonfiction', 'contrasting')),
    relationship_description TEXT,
    ai_generated BOOLEAN DEFAULT 1,
    user_created BOOLEAN DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book1_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (book2_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Reading DNA: User's reading personality profile
CREATE TABLE IF NOT EXISTS reading_dna_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    character_vs_plot_score REAL, -- -1 (plot) to 1 (character)
    pacing_preference TEXT,
    narrative_style_preference TEXT,
    complexity_comfort_level INTEGER,
    favorite_themes TEXT, -- JSON array
    writing_style_preferences TEXT, -- JSON
    profile_summary TEXT,
    ai_generated_narrative TEXT
);

-- Annual Reports: Year-end summaries
CREATE TABLE IF NOT EXISTS annual_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL UNIQUE,
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_books INTEGER,
    total_pages INTEGER,
    favorite_genre TEXT,
    top_rated_books TEXT, -- JSON array
    reading_highlights TEXT, -- JSON with various stats
    ai_narrative TEXT,
    growth_summary TEXT
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_reading_log_status ON reading_log(status);
CREATE INDEX IF NOT EXISTS idx_reading_log_book_id ON reading_log(book_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_genre ON recommendations(genre);
CREATE INDEX IF NOT EXISTS idx_recommendations_active ON recommendations(is_active);
CREATE INDEX IF NOT EXISTS idx_reading_stats_date ON reading_stats(date);
CREATE INDEX IF NOT EXISTS idx_plan_books_plan_id ON plan_books(plan_id);
CREATE INDEX IF NOT EXISTS idx_book_moods_book_id ON book_moods(book_id);
CREATE INDEX IF NOT EXISTS idx_book_themes_book_id ON book_themes(book_id);
CREATE INDEX IF NOT EXISTS idx_book_themes_theme ON book_themes(theme);
CREATE INDEX IF NOT EXISTS idx_series_books_series_id ON series_books(series_id);
CREATE INDEX IF NOT EXISTS idx_vocabulary_mastery ON vocabulary(mastery_level);
CREATE INDEX IF NOT EXISTS idx_vocabulary_next_review ON vocabulary(next_review_date);
CREATE INDEX IF NOT EXISTS idx_reading_notes_book_id ON reading_notes(book_id);
CREATE INDEX IF NOT EXISTS idx_reading_sessions_book_id ON reading_sessions(book_id);
CREATE INDEX IF NOT EXISTS idx_reading_sessions_date ON reading_sessions(session_date);
