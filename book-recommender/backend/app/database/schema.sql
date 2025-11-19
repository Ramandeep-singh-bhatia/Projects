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

-- MANUAL ENTRY & EVALUATION FEATURES

-- Manually Added Books: Track books added outside app recommendations
CREATE TABLE IF NOT EXISTS manually_added_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_of_recommendation TEXT, -- 'friend', 'online', 'bookstore', 'other'
    recommender_name TEXT,
    why_read TEXT,
    was_outside_comfort_zone BOOLEAN DEFAULT 0,
    ai_analysis_complete BOOLEAN DEFAULT 0,
    profile_impact_calculated BOOLEAN DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Book Analysis: AI-generated deep analysis of books
CREATE TABLE IF NOT EXISTS book_analysis (
    book_id INTEGER PRIMARY KEY,
    complexity_score INTEGER CHECK(complexity_score BETWEEN 1 AND 10),
    themes TEXT, -- JSON array
    mood_tags TEXT, -- JSON object: {energy, pacing, tone, complexity}
    writing_style TEXT,
    similar_books TEXT, -- JSON array of book IDs
    reader_level TEXT, -- 'beginner', 'intermediate', 'advanced'
    content_warnings TEXT, -- JSON array
    character_vs_plot_score REAL, -- -1 (plot) to 1 (character)
    narrative_structure TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- External Recommendations: Track recommendations from outside the app
CREATE TABLE IF NOT EXISTS external_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    recommender_type TEXT CHECK(recommender_type IN ('friend', 'family', 'online', 'critic', 'bookclub', 'other')),
    recommender_name TEXT,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommendation_context TEXT,
    trust_score REAL DEFAULT 0.5 CHECK(trust_score BETWEEN 0 AND 1),
    match_accuracy REAL, -- Set after reading, comparing to reading DNA
    was_good_match BOOLEAN,
    notes TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Future Reads: Books user wants to read but isn't ready for yet
CREATE TABLE IF NOT EXISTS future_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommended_by TEXT,
    current_readiness_score INTEGER CHECK(current_readiness_score BETWEEN 0 AND 100),
    target_readiness_score INTEGER DEFAULT 75 CHECK(target_readiness_score BETWEEN 0 AND 100),
    estimated_ready_date DATE,
    preparation_plan_id INTEGER,
    reason_deferred TEXT,
    user_notes TEXT,
    reminder_preference TEXT CHECK(reminder_preference IN ('when_ready', 'monthly', 'quarterly', 'never')) DEFAULT 'when_ready',
    status TEXT CHECK(status IN ('waiting', 'preparing', 'ready', 'moved_to_reading', 'abandoned')) DEFAULT 'waiting',
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (preparation_plan_id) REFERENCES reading_plans(id) ON DELETE SET NULL
);

-- Readiness Checkpoints: Monitor progression toward future books
CREATE TABLE IF NOT EXISTS readiness_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    future_read_id INTEGER NOT NULL,
    checkpoint_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    readiness_score INTEGER CHECK(readiness_score BETWEEN 0 AND 100),
    factors_assessed TEXT, -- JSON object with breakdown
    gaps_identified TEXT, -- JSON array: ['needs more fantasy exposure', 'complexity too high']
    progress_since_last REAL,
    books_that_helped TEXT, -- JSON array of book IDs that improved readiness
    ai_insights TEXT,
    FOREIGN KEY (future_read_id) REFERENCES future_reads(id) ON DELETE CASCADE
);

-- Book Interactions: Unified tracking of all book interactions
CREATE TABLE IF NOT EXISTS book_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    interaction_type TEXT CHECK(interaction_type IN ('searched', 'viewed', 'added_to_read', 'evaluated', 'started', 'completed', 'dnf', 'rated', 'noted', 'recommended')),
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interaction_context TEXT, -- JSON with additional data
    session_id TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Reading History Complete: Comprehensive reading history with enriched data
CREATE TABLE IF NOT EXISTS reading_history_complete (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('to_read', 'reading', 'completed', 'dnf')),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_started TIMESTAMP,
    date_completed TIMESTAMP,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    how_discovered TEXT, -- 'app_recommendation', 'manual_add', 'friend', etc.
    discovery_source_id INTEGER, -- Links to recommendation or external_recommendation
    was_in_comfort_zone BOOLEAN,
    exceeded_expectations BOOLEAN,
    complexity_match TEXT, -- 'too_easy', 'just_right', 'too_hard'
    mood_at_start TEXT, -- JSON of mood selections
    mood_at_end TEXT, -- JSON of mood after reading
    profile_alignment_score REAL, -- 0-1, how well it matched reading DNA
    contributed_to_growth BOOLEAN,
    notes TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
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
CREATE INDEX IF NOT EXISTS idx_manually_added_books_book_id ON manually_added_books(book_id);
CREATE INDEX IF NOT EXISTS idx_manually_added_books_source ON manually_added_books(source_of_recommendation);
CREATE INDEX IF NOT EXISTS idx_external_recommendations_book_id ON external_recommendations(book_id);
CREATE INDEX IF NOT EXISTS idx_external_recommendations_type ON external_recommendations(recommender_type);
CREATE INDEX IF NOT EXISTS idx_future_reads_book_id ON future_reads(book_id);
CREATE INDEX IF NOT EXISTS idx_future_reads_status ON future_reads(status);
CREATE INDEX IF NOT EXISTS idx_future_reads_readiness ON future_reads(current_readiness_score);
CREATE INDEX IF NOT EXISTS idx_readiness_checkpoints_future_read ON readiness_checkpoints(future_read_id);
CREATE INDEX IF NOT EXISTS idx_book_interactions_book_id ON book_interactions(book_id);
CREATE INDEX IF NOT EXISTS idx_book_interactions_type ON book_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_book_interactions_date ON book_interactions(interaction_date);
CREATE INDEX IF NOT EXISTS idx_reading_history_complete_book_id ON reading_history_complete(book_id);
CREATE INDEX IF NOT EXISTS idx_reading_history_complete_status ON reading_history_complete(status);
