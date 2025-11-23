# Intelligent Personal Book Recommender System
## Complete User Guide & Documentation - Part 4 (Final)

---

# 9. API Documentation

## 9.1 API Overview

**Base URL**: `http://localhost:8000`

**Interactive Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Authentication**: None (local application)

**Response Format**: JSON

**Error Handling**: Standard HTTP status codes

## 9.2 Core API Endpoints

### 9.2.1 Books

**Search Books**
```http
GET /api/books/search?query={query}&limit={limit}&genre={genre}
```

Parameters:
- `query` (required): Search term (title or author)
- `limit` (optional): Number of results (default: 10)
- `genre` (optional): Filter by genre

Response:
```json
{
  "results": [
    {
      "title": "The Name of the Wind",
      "author": "Patrick Rothfuss",
      "isbn": "9780756404741",
      "genre": "Fantasy",
      "page_count": 662,
      "cover_url": "https://...",
      "description": "..."
    }
  ]
}
```

**Get Book Details**
```http
GET /api/books/{book_id}
```

Response:
```json
{
  "id": 123,
  "title": "The Name of the Wind",
  "author": "Patrick Rothfuss",
  "genre": "Fantasy",
  "page_count": 662,
  "snoisle_available": true,
  "formats_available": ["ebook", "paperback", "audiobook"],
  "ai_summary": "Epic fantasy following Kvothe...",
  "complexity_score": 6,
  "themes": ["coming-of-age", "magic", "adventure"]
}
```

**Add Book to Library**
```http
POST /api/books
Content-Type: application/json

{
  "title": "Book Title",
  "author": "Author Name",
  "isbn": "9780123456789",
  "genre": "Fiction"
}
```

### 9.2.2 Reading Log

**Get User's Reading Log**
```http
GET /api/reading-log?status={status}&limit={limit}
```

Parameters:
- `status` (optional): to_read, reading, completed, dnf
- `limit` (optional): Number of results (default: 50)

**Update Reading Status**
```http
PUT /api/reading-log/{book_id}
Content-Type: application/json

{
  "status": "completed",
  "rating": 5,
  "date_completed": "2025-01-15",
  "personal_notes": "Absolutely loved it!"
}
```

**Log Reading Session**
```http
POST /api/reading-session
Content-Type: application/json

{
  "book_id": 123,
  "pages_read": 50,
  "minutes_read": 60,
  "session_date": "2025-01-15"
}
```

### 9.2.3 Recommendations

**Get Genre Recommendations**
```http
POST /api/recommendations/genre/{genre}
Content-Type: application/json

{
  "count": 5
}
```

Response:
```json
{
  "recommendations": [
    {
      "book": {
        "id": 456,
        "title": "Recommended Book",
        "author": "Author Name"
      },
      "reason": "Based on your love of...",
      "match_score": 92,
      "complexity_match": "comfortable"
    }
  ]
}
```

**Mood-Based Recommendations**
```http
POST /api/enhanced/recommendations/mood-based
Content-Type: application/json

{
  "mood_selections": {
    "energy": "light",
    "pacing": "fast",
    "tone": "hopeful",
    "complexity": "escapist"
  },
  "count": 3
}
```

### 9.2.4 Analytics

**Get Dashboard Stats**
```http
GET /api/analytics/dashboard
```

Response:
```json
{
  "total_books_read": 52,
  "total_pages_read": 18456,
  "average_rating": 4.2,
  "current_streak_days": 15,
  "genre_distribution": {
    "Fantasy": 32,
    "Literary Fiction": 28,
    "Science Fiction": 18
  },
  "monthly_trends": [...]
}
```

**Get Reading DNA**
```http
GET /api/enhanced/recommendations/reading-dna
```

Response:
```json
{
  "character_vs_plot_score": 0.6,
  "pacing_preference": "medium",
  "complexity_comfort_level": 6.5,
  "favorite_themes": ["coming-of-age", "identity"],
  "writing_style_preferences": {
    "lyrical": 0.72,
    "straightforward": 0.68
  }
}
```

## 9.3 Enhanced Features API

### 9.3.1 Reading Coach

**Create Reading Plan**
```http
POST /api/enhanced/reading-coach/create-plan
Content-Type: application/json

{
  "goal": "Explore classic literature",
  "duration_days": 90,
  "difficulty": "progressive"
}
```

**Get Active Plans**
```http
GET /api/enhanced/reading-coach/plans?status=active
```

**Update Plan Progress**
```http
PUT /api/enhanced/reading-coach/plans/{plan_id}/book/{book_id}
Content-Type: application/json

{
  "status": "completed",
  "date_completed": "2025-01-15"
}
```

### 9.3.2 Vocabulary Builder

**Add Word**
```http
POST /api/enhanced/vocabulary/add
Content-Type: application/json

{
  "word": "perspicacious",
  "book_id": 123,
  "page_number": 142,
  "context_sentence": "Her perspicacious analysis..."
}
```

**Get Words Due for Review**
```http
GET /api/enhanced/vocabulary/review-due
```

**Record Review**
```http
POST /api/enhanced/vocabulary/review/{word_id}
Content-Type: application/json

{
  "knew_it": true
}
```

### 9.3.3 Series Tracker

**Get All Series**
```http
GET /api/enhanced/series
```

**Get Series Progress**
```http
GET /api/enhanced/series/{series_id}/progress
```

Response:
```json
{
  "series_name": "The Stormlight Archive",
  "total_books": 5,
  "books_completed": 2,
  "current_book": {
    "title": "Oathbringer",
    "book_number": 3
  },
  "progress_percentage": 40
}
```

### 9.3.4 Annual Reports

**Generate Annual Report**
```http
POST /api/enhanced/reports/annual/{year}
```

**Get Annual Report**
```http
GET /api/enhanced/reports/annual/{year}
```

Response:
```json
{
  "year": 2024,
  "total_books": 52,
  "total_pages": 18456,
  "favorite_genre": "Fantasy",
  "top_rated_books": [...],
  "ai_narrative": "2024 was a year of...",
  "growth_summary": "You increased complexity tolerance by..."
}
```

## 9.4 Manual Entry & Evaluation API

### 9.4.1 Manual Book Entry

**Quick Add by Search**
```http
POST /api/manual/quick-add/search?query={query}
```

**Quick Add by ISBN**
```http
POST /api/manual/quick-add/isbn/{isbn}
```

**Manual Add with Full Details**
```http
POST /api/manual/add-book
Content-Type: application/json

{
  "book_data": {
    "title": "Book Title",
    "author": "Author Name",
    "genre": "Fiction",
    "page_count": 300
  },
  "source": "friend",
  "recommender_name": "Alice",
  "why_read": "She loved it",
  "auto_analyze": true
}
```

**Batch Import**
```http
POST /api/manual/batch-import
Content-Type: multipart/form-data

file: goodreads_export.csv
```

Response:
```json
{
  "success": true,
  "stats": {
    "total_processed": 150,
    "imported": 145,
    "skipped": 5,
    "analyzed": 120
  }
}
```

### 9.4.2 Book Evaluation

**Evaluate Readiness**
```http
POST /api/manual/evaluate/{book_id}
```

Response:
```json
{
  "success": true,
  "evaluation": {
    "readiness_score": 68,
    "recommendation_type": "maybe_later",
    "factors_breakdown": {
      "complexity_match": 75,
      "interest_alignment": 85,
      "completion_likelihood": 60,
      "enjoyment_potential": 80,
      "growth_opportunity": 90
    },
    "gaps_identified": [
      "Limited experience with non-linear narratives"
    ],
    "strengths": [
      "Strong thematic alignment"
    ],
    "detailed_reasoning": "While this book...",
    "preparation_needed": true,
    "estimated_ready_in_days": 60,
    "quick_wins": [
      "Cloud Atlas by David Mitchell"
    ]
  }
}
```

**Add to Future Reads**
```http
POST /api/manual/future-reads/add
Content-Type: application/json

{
  "book_id": 123,
  "user_notes": "Want to read when ready",
  "reminder_preference": "when_ready"
}
```

**Get Future Reads**
```http
GET /api/manual/future-reads?status={status}&min_readiness={score}
```

**Generate Preparation Plan**
```http
POST /api/manual/preparation-plan/{book_id}
```

Response:
```json
{
  "success": true,
  "plan": {
    "plan_id": 5,
    "plan_name": "Preparation for Infinite Jest",
    "duration_days": 90,
    "recommended_books": [
      {
        "title": "The Pale King",
        "author": "David Foster Wallace",
        "why_this_helps": "Same author, more accessible",
        "sequence_order": 1
      }
    ]
  }
}
```

**Run Readiness Check**
```http
POST /api/manual/readiness-check/run
```

Response:
```json
{
  "success": true,
  "updates_found": 3,
  "updates": [
    {
      "book_id": 123,
      "title": "Book Title",
      "old_score": 65,
      "new_score": 78,
      "status": "ready",
      "message": "You're ready!"
    }
  ]
}
```

## 9.5 Error Handling

**Standard Error Response:**
```json
{
  "detail": "Error message here"
}
```

**HTTP Status Codes:**
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

**Example Error:**
```http
POST /api/manual/evaluate/999
Status: 404

{
  "detail": "Book 999 not found"
}
```

## 9.6 Rate Limiting

**Default Limits:**
- API requests: 60 per minute
- AI operations: 5 concurrent max
- Batch operations: 1 per minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

---

# 10. Database Schema

## 10.1 Core Tables

### 10.1.1 books

Primary table for book metadata.

```sql
CREATE TABLE books (
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

-- Indexes
CREATE INDEX idx_books_genre ON books(genre);
CREATE INDEX idx_books_isbn ON books(isbn);
```

**Key Fields:**
- `id`: Unique identifier
- `isbn`: ISBN-10 or ISBN-13
- `genre`: Main genre classification
- `snoisle_available`: Library availability flag
- `format_available`: JSON array of formats

### 10.1.2 reading_log

Tracks user's reading activity.

```sql
CREATE TABLE reading_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('to_read', 'reading', 'completed', 'dnf')),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_started TIMESTAMP,
    date_completed TIMESTAMP,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    reading_duration_days INTEGER,
    format_used TEXT,
    personal_notes TEXT,
    ai_summary TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_reading_log_status ON reading_log(status);
CREATE INDEX idx_reading_log_book_id ON reading_log(book_id);
```

**Status Values:**
- `to_read`: In TBR list
- `reading`: Currently reading
- `completed`: Finished
- `dnf`: Did Not Finish

### 10.1.3 reading_stats

Daily reading statistics.

```sql
CREATE TABLE reading_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    pages_read INTEGER DEFAULT 0,
    minutes_read INTEGER DEFAULT 0,
    books_completed_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reading_stats_date ON reading_stats(date);
```

## 10.2 AI & Analysis Tables

### 10.2.1 book_analysis

AI-generated deep analysis of books.

```sql
CREATE TABLE book_analysis (
    book_id INTEGER PRIMARY KEY,
    complexity_score INTEGER CHECK(complexity_score BETWEEN 1 AND 10),
    themes TEXT, -- JSON array
    mood_tags TEXT, -- JSON object
    writing_style TEXT,
    similar_books TEXT, -- JSON array of book IDs
    reader_level TEXT, -- 'beginner', 'intermediate', 'advanced'
    content_warnings TEXT, -- JSON array
    character_vs_plot_score REAL, -- -1 to +1
    narrative_structure TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
```

**JSON Field Examples:**

```json
// themes
["coming-of-age", "identity", "family"]

// mood_tags
{
  "energy": "balanced",
  "pacing": "medium",
  "tone": "hopeful",
  "complexity": "medium"
}

// similar_books
[456, 789, 123]

// content_warnings
["violence", "sexual content"]
```

### 10.2.2 reading_dna_profile

User's reading personality.

```sql
CREATE TABLE reading_dna_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    character_vs_plot_score REAL, -- -1 (plot) to 1 (character)
    pacing_preference TEXT,
    narrative_style_preference TEXT,
    complexity_comfort_level INTEGER,
    favorite_themes TEXT, -- JSON array
    writing_style_preferences TEXT, -- JSON object
    profile_summary TEXT,
    ai_generated_narrative TEXT
);
```

### 10.2.3 recommendations

Tracks AI-generated recommendations.

```sql
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    genre TEXT NOT NULL,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    score REAL,
    shown_to_user BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
```

## 10.3 Enhanced Features Tables

### 10.3.1 reading_plans

Personalized reading roadmaps.

```sql
CREATE TABLE reading_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name TEXT NOT NULL,
    goal TEXT,
    duration_days INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    target_end_date DATE,
    status TEXT CHECK(status IN ('active', 'completed', 'abandoned')),
    difficulty_progression TEXT,
    ai_reasoning TEXT
);

CREATE TABLE plan_books (
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
```

### 10.3.2 vocabulary

Vocabulary builder system.

```sql
CREATE TABLE vocabulary (
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
    mastery_level TEXT CHECK(mastery_level IN ('learning', 'familiar', 'mastered')),
    next_review_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL
);

CREATE TABLE vocabulary_review_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    knew_it BOOLEAN,
    review_interval_days INTEGER,
    FOREIGN KEY (word_id) REFERENCES vocabulary(id) ON DELETE CASCADE
);
```

**Spaced Repetition Intervals:**
1. New: Review in 1 day
2. If correct: 3 days
3. If correct: 7 days
4. If correct: 14 days
5. If correct: 30 days
6. If correct: 60 days
7. Mastered!

### 10.3.3 book_series

Series tracking.

```sql
CREATE TABLE book_series (
    series_id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT NOT NULL UNIQUE,
    total_books INTEGER,
    primary_author TEXT,
    genre TEXT,
    description TEXT
);

CREATE TABLE series_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    book_number INTEGER,
    reading_order INTEGER,
    is_standalone BOOLEAN DEFAULT 0,
    FOREIGN KEY (series_id) REFERENCES book_series(series_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE user_series_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER NOT NULL,
    books_completed INTEGER DEFAULT 0,
    current_book_id INTEGER,
    started_date TIMESTAMP,
    last_read_date TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES book_series(series_id) ON DELETE CASCADE,
    FOREIGN KEY (current_book_id) REFERENCES books(id) ON DELETE SET NULL
);
```

## 10.4 Manual Entry & Evaluation Tables

### 10.4.1 manually_added_books

Tracks books added outside recommendations.

```sql
CREATE TABLE manually_added_books (
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

CREATE INDEX idx_manually_added_books_book_id ON manually_added_books(book_id);
CREATE INDEX idx_manually_added_books_source ON manually_added_books(source_of_recommendation);
```

### 10.4.2 future_reads

Books queued for later reading.

```sql
CREATE TABLE future_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommended_by TEXT,
    current_readiness_score INTEGER CHECK(current_readiness_score BETWEEN 0 AND 100),
    target_readiness_score INTEGER DEFAULT 75,
    estimated_ready_date DATE,
    preparation_plan_id INTEGER,
    reason_deferred TEXT,
    user_notes TEXT,
    reminder_preference TEXT CHECK(reminder_preference IN ('when_ready', 'monthly', 'quarterly', 'never')),
    status TEXT CHECK(status IN ('waiting', 'preparing', 'ready', 'moved_to_reading', 'abandoned')),
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (preparation_plan_id) REFERENCES reading_plans(id) ON DELETE SET NULL
);

CREATE INDEX idx_future_reads_status ON future_reads(status);
CREATE INDEX idx_future_reads_readiness ON future_reads(current_readiness_score);
```

### 10.4.3 readiness_checkpoints

Monitors readiness progression.

```sql
CREATE TABLE readiness_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    future_read_id INTEGER NOT NULL,
    checkpoint_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    readiness_score INTEGER CHECK(readiness_score BETWEEN 0 AND 100),
    factors_assessed TEXT, -- JSON object
    gaps_identified TEXT, -- JSON array
    progress_since_last REAL,
    books_that_helped TEXT, -- JSON array of book IDs
    ai_insights TEXT,
    FOREIGN KEY (future_read_id) REFERENCES future_reads(id) ON DELETE CASCADE
);
```

**Checkpoint JSON Examples:**

```json
// factors_assessed
{
  "complexity_match": 75,
  "interest_alignment": 85,
  "completion_likelihood": 60,
  "enjoyment_potential": 80,
  "growth_opportunity": 90
}

// gaps_identified
["complexity_gap", "length_tolerance", "style_unfamiliarity"]

// books_that_helped
[456, 789] // book IDs
```

## 10.5 Database Maintenance

### 10.5.1 Common Queries

**Get all books by genre:**
```sql
SELECT * FROM books WHERE genre = 'Fantasy' ORDER BY title;
```

**Get reading statistics for a date range:**
```sql
SELECT
    SUM(pages_read) as total_pages,
    SUM(minutes_read) as total_minutes,
    SUM(books_completed_count) as books_finished
FROM reading_stats
WHERE date BETWEEN '2025-01-01' AND '2025-01-31';
```

**Get user's favorite themes:**
```sql
SELECT
    bt.theme,
    COUNT(*) as count,
    AVG(rl.rating) as avg_rating
FROM book_themes bt
JOIN reading_log rl ON bt.book_id = rl.book_id
WHERE rl.status = 'completed'
GROUP BY bt.theme
ORDER BY avg_rating DESC, count DESC
LIMIT 10;
```

**Get Future Reads ready to read:**
```sql
SELECT
    b.id,
    b.title,
    b.author,
    fr.current_readiness_score
FROM future_reads fr
JOIN books b ON fr.book_id = b.id
WHERE fr.current_readiness_score >= 75
    AND fr.status = 'ready'
ORDER BY fr.current_readiness_score DESC;
```

### 10.5.2 Database Backup

**Manual Backup:**
```bash
# Simple copy
cp ./data/books.db ./data/books.backup.db

# With timestamp
cp ./data/books.db "./data/books_$(date +%Y%m%d).db"

# Compressed backup
sqlite3 ./data/books.db ".backup ./data/books.backup.db"
gzip ./data/books.backup.db
```

**Automated Backup Script:**
```bash
#!/bin/bash
# /path/to/backup-db.sh

DB_PATH="./data/books.db"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Create backup
sqlite3 "$DB_PATH" ".backup $BACKUP_DIR/books_$DATE.db"

# Compress
gzip "$BACKUP_DIR/books_$DATE.db"

# Keep only last 30 days
find "$BACKUP_DIR" -name "books_*.db.gz" -mtime +30 -delete

echo "Backup created: books_$DATE.db.gz"
```

### 10.5.3 Database Optimization

**Vacuum (reclaim space):**
```sql
VACUUM;
```

**Analyze (update statistics):**
```sql
ANALYZE;
```

**Reindex:**
```sql
REINDEX;
```

**Check integrity:**
```sql
PRAGMA integrity_check;
```

### 10.5.4 Migration Strategy

**For Schema Changes:**

1. **Backup First!**
2. **Create migration script**
3. **Test on copy**
4. **Apply to production**

**Example Migration (Add column):**
```sql
-- migration_001.sql
-- Add "series_id" to books table

-- 1. Create new table with desired schema
CREATE TABLE books_new (
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
    series_id INTEGER, -- NEW COLUMN
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES book_series(series_id)
);

-- 2. Copy data
INSERT INTO books_new SELECT *, NULL FROM books;

-- 3. Drop old table
DROP TABLE books;

-- 4. Rename new table
ALTER TABLE books_new RENAME TO books;

-- 5. Recreate indexes
CREATE INDEX idx_books_genre ON books(genre);
CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_books_series ON books(series_id);
```

---

# 11. Development Guide

## 11.1 Project Structure

```
book-recommender/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── api/
│   │   │   ├── routes.py           # Core API routes
│   │   │   ├── enhanced_routes.py  # Enhanced features
│   │   │   └── manual_routes.py    # Manual entry & evaluation
│   │   ├── database/
│   │   │   ├── database.py         # DB initialization
│   │   │   └── schema.sql          # Database schema
│   │   └── services/
│   │       ├── book_api.py         # External APIs integration
│   │       ├── recommendation_engine.py
│   │       ├── reading_coach.py
│   │       ├── enhanced_recommendations.py
│   │       ├── vocabulary_service.py
│   │       ├── series_tracker.py
│   │       ├── reading_journal.py
│   │       ├── annual_reports.py
│   │       ├── manual_entry_service.py
│   │       ├── evaluation_service.py
│   │       └── library_checker.py
│   ├── data/
│   │   └── books.db                # SQLite database
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                        # Your config (gitignored)
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BookCard.tsx
│   │   │   ├── GenreSection.tsx
│   │   │   ├── MoodSelector.tsx
│   │   │   ├── VocabularyFlashcard.tsx
│   │   │   ├── SeriesTracker.tsx
│   │   │   ├── ReadingDNA.tsx
│   │   │   ├── AddBookModal.tsx
│   │   │   ├── BookEvaluation.tsx
│   │   │   └── FutureReadsBoard.tsx
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   └── MyBooksPage.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.tsx
│   ├── package.json
│   └── .env                        # Your config (gitignored)
│
├── README.md
├── TIER1_TIER2_FEATURES.md
├── MANUAL_ENTRY_EVALUATION_FEATURES.md
├── COMPLETE_USER_GUIDE.md (Parts 1-4)
└── .gitignore
```

## 11.2 Adding New Features

### 11.2.1 Backend Feature

**Example: Add "Reading Challenge" Feature**

**Step 1: Database Schema**

Edit `backend/app/database/schema.sql`:
```sql
-- Reading Challenges
CREATE TABLE reading_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_name TEXT NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    target_books INTEGER,
    books_completed INTEGER DEFAULT 0,
    status TEXT CHECK(status IN ('active', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_challenges_status ON reading_challenges(status);
```

**Step 2: Service Layer**

Create `backend/app/services/reading_challenge.py`:
```python
"""
Reading Challenge Service
"""
import sqlite3
from typing import Dict, List, Any
from datetime import datetime, date


class ReadingChallengeService:
    """Manage reading challenges"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_challenge(
        self,
        name: str,
        target_books: int,
        start_date: date,
        end_date: date,
        description: str = ""
    ) -> int:
        """Create a new reading challenge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO reading_challenges
                (challenge_name, description, start_date, end_date, target_books, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            """, (name, description, start_date, end_date, target_books))

            challenge_id = cursor.lastrowid
            conn.commit()

            return challenge_id

        finally:
            conn.close()

    def get_active_challenges(self) -> List[Dict[str, Any]]:
        """Get all active challenges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, challenge_name, target_books, books_completed,
                       start_date, end_date
                FROM reading_challenges
                WHERE status = 'active'
                ORDER BY end_date ASC
            """)

            challenges = []
            for row in cursor.fetchall():
                challenges.append({
                    'id': row[0],
                    'name': row[1],
                    'target': row[2],
                    'completed': row[3],
                    'progress': (row[3] / row[2]) * 100,
                    'start_date': row[4],
                    'end_date': row[5]
                })

            return challenges

        finally:
            conn.close()

    def update_progress(self, challenge_id: int, books_completed: int):
        """Update challenge progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Update books completed
            cursor.execute("""
                UPDATE reading_challenges
                SET books_completed = ?
                WHERE id = ?
            """, (books_completed, challenge_id))

            # Check if completed
            cursor.execute("""
                SELECT target_books, end_date
                FROM reading_challenges
                WHERE id = ?
            """, (challenge_id,))

            row = cursor.fetchone()
            target_books = row[0]
            end_date = datetime.strptime(row[1], '%Y-%m-%d').date()

            if books_completed >= target_books:
                status = 'completed'
            elif datetime.now().date() > end_date:
                status = 'failed'
            else:
                status = 'active'

            cursor.execute("""
                UPDATE reading_challenges
                SET status = ?
                WHERE id = ?
            """, (status, challenge_id))

            conn.commit()

        finally:
            conn.close()


# Global instance
_challenge_service = None


def init_challenge_service(db_path: str):
    global _challenge_service
    _challenge_service = ReadingChallengeService(db_path)


def get_challenge_service() -> ReadingChallengeService:
    if _challenge_service is None:
        raise RuntimeError("Challenge service not initialized")
    return _challenge_service
```

**Step 3: API Routes**

Create `backend/app/api/challenge_routes.py`:
```python
"""
Reading Challenge API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import List
from app.services.reading_challenge import get_challenge_service

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


class CreateChallengeRequest(BaseModel):
    name: str
    target_books: int
    start_date: date
    end_date: date
    description: str = ""


@router.post("/create")
def create_challenge(request: CreateChallengeRequest):
    """Create a new reading challenge"""
    service = get_challenge_service()

    challenge_id = service.create_challenge(
        name=request.name,
        target_books=request.target_books,
        start_date=request.start_date,
        end_date=request.end_date,
        description=request.description
    )

    return {
        "success": True,
        "challenge_id": challenge_id,
        "message": "Challenge created!"
    }


@router.get("/active")
def get_active_challenges():
    """Get all active challenges"""
    service = get_challenge_service()
    challenges = service.get_active_challenges()

    return {
        "success": True,
        "challenges": challenges
    }


@router.put("/{challenge_id}/progress")
def update_progress(challenge_id: int, books_completed: int):
    """Update challenge progress"""
    service = get_challenge_service()
    service.update_progress(challenge_id, books_completed)

    return {
        "success": True,
        "message": "Progress updated!"
    }
```

**Step 4: Register Routes**

Edit `backend/app/main.py`:
```python
from .api.challenge_routes import router as challenge_router

# In the app setup:
app.include_router(challenge_router, tags=["Reading Challenges"])

# In lifespan():
from .services.reading_challenge import init_challenge_service
init_challenge_service(db_path)
```

**Step 5: Test the API**

```bash
# Create challenge
curl -X POST http://localhost:8000/api/challenges/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "52 Books in 2025",
    "target_books": 52,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'

# Get active challenges
curl http://localhost:8000/api/challenges/active
```

### 11.2.2 Frontend Feature

**Example: Add Reading Challenge Component**

**Step 1: Create Component**

Create `frontend/src/components/ReadingChallenge.tsx`:
```typescript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Challenge {
  id: number;
  name: string;
  target: number;
  completed: number;
  progress: number;
  start_date: string;
  end_date: string;
}

const ReadingChallenge: React.FC = () => {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChallenges();
  }, []);

  const loadChallenges = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/challenges/active`
      );
      setChallenges(response.data.challenges);
    } catch (error) {
      console.error('Failed to load challenges:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading challenges...</div>;

  return (
    <div className="reading-challenges">
      <h2>Active Reading Challenges</h2>

      {challenges.length === 0 ? (
        <div className="empty-state">
          <p>No active challenges. Create one to start!</p>
          <button className="btn btn-primary">Create Challenge</button>
        </div>
      ) : (
        <div className="challenges-grid">
          {challenges.map(challenge => (
            <div key={challenge.id} className="challenge-card">
              <h3>{challenge.name}</h3>

              <div className="progress-section">
                <div className="progress-numbers">
                  <span className="completed">{challenge.completed}</span>
                  <span className="separator">/</span>
                  <span className="target">{challenge.target}</span>
                  <span className="label">books</span>
                </div>

                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${challenge.progress}%` }}
                  />
                </div>

                <div className="progress-percentage">
                  {Math.round(challenge.progress)}% complete
                </div>
              </div>

              <div className="challenge-dates">
                <span>Ends: {new Date(challenge.end_date).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReadingChallenge;
```

**Step 2: Add Styles**

In `frontend/src/App.css`:
```css
.reading-challenges {
  padding: 20px;
}

.challenges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.challenge-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.challenge-card h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.progress-numbers {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 10px;
}

.progress-numbers .completed {
  font-size: 48px;
  font-weight: bold;
  color: #4caf50;
}

.progress-numbers .separator {
  font-size: 32px;
  margin: 0 5px;
  color: #999;
}

.progress-numbers .target {
  font-size: 32px;
  color: #666;
}

.progress-numbers .label {
  font-size: 18px;
  margin-left: 10px;
  color: #999;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
  margin: 15px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  transition: width 0.3s ease;
}

.progress-percentage {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

.challenge-dates {
  text-align: center;
  font-size: 14px;
  color: #999;
  padding-top: 15px;
  border-top: 1px solid #eee;
}
```

**Step 3: Add to App**

Edit `frontend/src/App.tsx`:
```typescript
import ReadingChallenge from './components/ReadingChallenge';

// In your routing:
<Route path="/challenges" element={<ReadingChallenge />} />
```

**Step 4: Test Component**

```bash
npm start
# Navigate to http://localhost:3000/challenges
```

## 11.3 Testing

### 11.3.1 Backend Testing

**Install pytest:**
```bash
pip install pytest pytest-asyncio httpx
```

**Create test file** `backend/tests/test_challenges.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_challenge():
    """Test creating a reading challenge"""
    response = client.post("/api/challenges/create", json={
        "name": "Test Challenge",
        "target_books": 10,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "challenge_id" in data


def test_get_active_challenges():
    """Test fetching active challenges"""
    response = client.get("/api/challenges/active")

    assert response.status_code == 200
    data = response.json()
    assert "challenges" in data
    assert isinstance(data["challenges"], list)


def test_update_progress():
    """Test updating challenge progress"""
    # First create a challenge
    create_response = client.post("/api/challenges/create", json={
        "name": "Test",
        "target_books": 10,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    })
    challenge_id = create_response.json()["challenge_id"]

    # Update progress
    response = client.put(
        f"/api/challenges/{challenge_id}/progress?books_completed=5"
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
```

**Run tests:**
```bash
cd backend
pytest
```

### 11.3.2 Frontend Testing

**Install testing library:**
```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

**Create test** `frontend/src/components/ReadingChallenge.test.tsx`:
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import ReadingChallenge from './ReadingChallenge';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

test('renders challenges', async () => {
  mockedAxios.get.mockResolvedValue({
    data: {
      challenges: [
        {
          id: 1,
          name: '52 Books in 2025',
          target: 52,
          completed: 10,
          progress: 19.2,
          start_date: '2025-01-01',
          end_date: '2025-12-31'
        }
      ]
    }
  });

  render(<ReadingChallenge />);

  await waitFor(() => {
    expect(screen.getByText('52 Books in 2025')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });
});
```

**Run tests:**
```bash
npm test
```

## 11.4 Code Quality

### 11.4.1 Linting

**Backend (flake8):**
```bash
pip install flake8
flake8 app/ --max-line-length=100
```

**Frontend (ESLint):**
```bash
npm run lint
```

### 11.4.2 Formatting

**Backend (black):**
```bash
pip install black
black app/
```

**Frontend (Prettier):**
```bash
npm install --save-dev prettier
npx prettier --write src/
```

### 11.4.3 Type Checking

**Backend (mypy):**
```bash
pip install mypy
mypy app/
```

**Frontend (TypeScript):**
```bash
npm run type-check
```

---

*This completes the comprehensive documentation. The guide covers Installation, Configuration, Running, Usage, Features, API, Database, Development, and all aspects needed to understand and use the Intelligent Personal Book Recommender System.*
