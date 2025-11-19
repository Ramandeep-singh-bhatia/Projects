# Manual Entry & Book Evaluation Features

This document describes the Manual Book Entry and "Should I Read This?" Evaluation features added in Version 3.0.

## Table of Contents
1. [Overview](#overview)
2. [Manual Book Entry](#manual-book-entry)
3. [Book Evaluation System](#book-evaluation-system)
4. [Future Reads Management](#future-reads-management)
5. [API Reference](#api-reference)
6. [Frontend Components](#frontend-components)
7. [Database Schema](#database-schema)

---

## Overview

Version 3.0 introduces powerful features for managing books discovered outside the app's recommendation system and intelligently evaluating whether you're ready to read specific books.

### Key Capabilities

**Manual Entry Features:**
- Add books by search, ISBN/barcode, or manual entry
- Batch import from Goodreads CSV export
- AI analysis of manually added books
- Track external recommendations (friends, critics, online sources)
- Profile impact calculation

**Evaluation Features:**
- "Should I Read This?" readiness assessment (0-100 score)
- 4 recommendation types: Read Now, Maybe Later, Not Yet, Different Direction
- Multi-factor analysis (complexity, interest, completion likelihood, etc.)
- Future Reads management for books you're not quite ready for
- Automatic readiness monitoring
- Preparation plan generation

---

## Manual Book Entry

### 1. Quick Add Methods

#### A. Search by Title/Author
```
POST /api/manual/quick-add/search?query={query}&source=manual
```

Searches external APIs (Google Books, Open Library) and adds the first match.

**Parameters:**
- `query` (required): Book title or author
- `source`: friend, online, bookstore, manual, other
- `recommender_name`: Name of recommender (optional)
- `why_read`: Reason for wanting to read (optional)

**Response:**
```json
{
  "success": true,
  "book_id": 123,
  "book_data": {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Fiction"
  },
  "message": "Book added successfully!"
}
```

#### B. Add by ISBN/Barcode
```
POST /api/manual/quick-add/isbn/{isbn}
```

Perfect for scanning barcodes or entering ISBN numbers.

**Example:**
```bash
POST /api/manual/quick-add/isbn/9780743273565
```

#### C. Manual Entry
```
POST /api/manual/add-book
```

For books not found in external APIs or when you want full control.

**Request Body:**
```json
{
  "book_data": {
    "title": "My Book",
    "author": "Author Name",
    "genre": "Fiction",
    "isbn": "1234567890",
    "page_count": 300,
    "description": "Book description"
  },
  "source": "friend",
  "recommender_name": "Alice",
  "why_read": "She said it changed her life",
  "auto_analyze": true
}
```

### 2. Batch Import from Goodreads

Import your entire Goodreads library in seconds!

```
POST /api/manual/batch-import
Content-Type: multipart/form-data

file: goodreads_library_export.csv
```

**Process:**
1. Export your Goodreads library (Goodreads → My Books → Import/Export → Export)
2. Upload the CSV file
3. Books are automatically analyzed and added
4. Get import statistics

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_processed": 150,
    "imported": 145,
    "skipped": 5,
    "analyzed": 120,
    "errors": []
  }
}
```

### 3. AI Book Analysis

When books are added, they're automatically analyzed for:
- **Complexity Score (1-10)**: Reading difficulty
- **Themes**: Main thematic elements
- **Mood Tags**: Energy, pacing, tone, complexity
- **Writing Style**: Prose characteristics
- **Reader Level**: Beginner, intermediate, advanced
- **Character vs Plot Score**: Narrative focus
- **Content Warnings**: Sensitive content

**Trigger manual analysis:**
```
POST /api/manual/analyze-book/{book_id}
```

### 4. Profile Impact Calculation

Understand how adding a book affects your reading profile:

```
POST /api/manual/profile-impact/{book_id}
```

**Response:**
```json
{
  "success": true,
  "impact": {
    "is_new_territory": true,
    "complexity_match": "challenging",
    "complexity_difference": 2.3,
    "thematic_overlap": 1,
    "total_themes": 15,
    "recommendation": "This book is outside your comfort zone! Consider adding to Future Reads for preparation."
  }
}
```

### 5. External Recommendation Tracking

Track who recommended what to learn which sources give you good suggestions:

```
POST /api/manual/external-recommendation
```

**Request:**
```json
{
  "book_id": 123,
  "recommender_type": "friend",
  "recommender_name": "Alice",
  "context": "She loved it and thought I would too",
  "trust_score": 0.8
}
```

The system learns over time which recommenders match your taste!

---

## Book Evaluation System

### "Should I Read This?" Feature

Get a comprehensive, AI-powered readiness assessment for any book.

#### 1. Run Evaluation

```
POST /api/manual/evaluate/{book_id}
```

**Response:**
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
      "Limited experience with non-linear narratives",
      "Could benefit from reading more literary fiction"
    ],
    "strengths": [
      "Strong thematic alignment with your interests",
      "Author style matches your preferences"
    ],
    "detailed_reasoning": "While this book explores themes you love, its complex narrative structure might be challenging right now. Reading 2-3 more books with experimental structures would prepare you perfectly.",
    "preparation_needed": true,
    "estimated_ready_in_days": 60,
    "quick_wins": [
      "Cloud Atlas by David Mitchell - introduces multi-narrative structure",
      "Slaughterhouse-Five by Kurt Vonnegut - non-linear storytelling"
    ],
    "alternative_suggestions": []
  }
}
```

#### 2. Recommendation Types

**Read Now (Score 75-100)**
- ✅ Perfect match for your current reading level
- High likelihood of completion and enjoyment
- Action: Add to reading list immediately

**Maybe Later (Score 50-74)**
- ⏰ Close but missing one or two elements
- You could read it now, but it might be challenging
- Action: Consider adding to Future Reads or read a preparatory book first

**Not Yet (Score 25-49)**
- 📚 Significant gaps between book and your current profile
- Low completion likelihood if attempted now
- Action: Add to Future Reads with preparation plan

**Different Direction (Score 0-24)**
- 🔄 Poor match with your reading DNA
- Better alternatives available
- Action: Consider suggested alternatives instead

#### 3. Multi-Factor Analysis

Each book is scored on 5 dimensions:

1. **Complexity Match (0-100)**
   - Compares book complexity to your comfort level
   - Considers vocabulary, structure, theme depth

2. **Interest Alignment (0-100)**
   - Thematic overlap with your favorites
   - Genre preferences
   - Character vs plot preference match

3. **Completion Likelihood (0-100)**
   - Probability you'll finish the book
   - Based on similar books you've DNF'd or completed

4. **Enjoyment Potential (0-100)**
   - Expected enjoyment level
   - Writing style match
   - Mood alignment

5. **Growth Opportunity (0-100)**
   - How much this expands your reading horizons
   - Balanced against being too far outside comfort zone

---

## Future Reads Management

Books you want to read eventually but aren't quite ready for.

### 1. Add to Future Reads

```
POST /api/manual/future-reads/add
```

**Request:**
```json
{
  "book_id": 123,
  "user_notes": "Looks fascinating, want to read when ready",
  "reminder_preference": "when_ready"
}
```

**Reminder Options:**
- `when_ready`: Notify when readiness score ≥ 75
- `monthly`: Check monthly
- `quarterly`: Check quarterly
- `never`: Manual checks only

### 2. Get Future Reads List

```
GET /api/manual/future-reads?status=waiting&min_readiness=50
```

**Filters:**
- `status`: waiting, preparing, ready, moved_to_reading, abandoned
- `min_readiness`: Minimum readiness score (0-100)

**Response:**
```json
{
  "success": true,
  "count": 5,
  "books": [
    {
      "future_read_id": 1,
      "book_id": 123,
      "title": "Infinite Jest",
      "author": "David Foster Wallace",
      "genre": "Literary Fiction",
      "readiness_score": 45,
      "estimated_ready_date": "2025-03-15",
      "status": "preparing",
      "has_preparation_plan": true
    }
  ]
}
```

### 3. Readiness Monitoring

The system automatically monitors your reading progress and updates readiness scores.

**Manual Readiness Check:**
```
POST /api/manual/readiness-check/run
```

Runs immediately and returns updates:
```json
{
  "success": true,
  "updates_found": 3,
  "updates": [
    {
      "book_id": 123,
      "title": "The Name of the Rose",
      "old_score": 65,
      "new_score": 78,
      "status": "ready",
      "message": "🎉 You're ready! Readiness improved from 65 to 78."
    }
  ]
}
```

**Get Ready Books:**
```
GET /api/manual/readiness-check/notifications
```

Returns all books with readiness ≥ 75.

### 4. Preparation Plans

For books you're not ready for, generate a custom reading plan:

```
POST /api/manual/preparation-plan/{book_id}
```

**Response:**
```json
{
  "success": true,
  "plan": {
    "plan_id": 5,
    "plan_name": "Preparation for Infinite Jest",
    "duration_days": 90,
    "recommended_books": [
      {
        "title": "A Heartbreaking Work of Staggering Genius",
        "author": "Dave Eggers",
        "why_this_helps": "Introduces postmodern narrative techniques in an accessible way",
        "sequence_order": 1
      },
      {
        "title": "White Noise",
        "author": "Don DeLillo",
        "why_this_helps": "Complex themes with more linear structure",
        "sequence_order": 2
      },
      {
        "title": "The Pale King",
        "author": "David Foster Wallace",
        "why_this_helps": "Same author, slightly more accessible",
        "sequence_order": 3
      }
    ],
    "milestones": [
      "After book 1: Comfort with experimental narration",
      "After book 2: Theme complexity preparation",
      "After book 3: Author familiarity achieved"
    ]
  }
}
```

---

## API Reference

### Endpoints Summary

#### Manual Entry
- `POST /api/manual/add-book` - Add book with full details
- `POST /api/manual/quick-add/search` - Quick add by search
- `POST /api/manual/quick-add/isbn/{isbn}` - Quick add by ISBN
- `POST /api/manual/batch-import` - Batch import CSV
- `POST /api/manual/analyze-book/{book_id}` - Trigger AI analysis
- `POST /api/manual/profile-impact/{book_id}` - Calculate profile impact
- `GET /api/manual/entries` - Get all manual entries
- `POST /api/manual/external-recommendation` - Track external rec

#### Evaluation
- `POST /api/manual/evaluate/{book_id}` - Evaluate readiness
- `POST /api/manual/future-reads/add` - Add to future reads
- `GET /api/manual/future-reads` - Get future reads list
- `POST /api/manual/preparation-plan/{book_id}` - Generate prep plan
- `POST /api/manual/readiness-check/run` - Run readiness check
- `GET /api/manual/readiness-check/notifications` - Get ready books

---

## Frontend Components

### 1. AddBookModal.tsx

Unified modal for adding books with three modes:

**Props:**
```typescript
interface AddBookModalProps {
  isOpen: boolean;
  onClose: () => void;
  onBookAdded?: (bookId: number) => void;
}
```

**Features:**
- Search mode: Quick search and add
- ISBN mode: Barcode/ISBN entry
- Manual mode: Full manual entry
- Optional automatic evaluation
- Source and recommender tracking

**Usage:**
```tsx
<AddBookModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  onBookAdded={handleBookAdded}
/>
```

### 2. BookEvaluation.tsx

Display detailed "Should I Read This?" results.

**Props:**
```typescript
interface BookEvaluationProps {
  bookId: number;
  bookTitle: string;
  onAddToFutureReads?: () => void;
}
```

**Features:**
- Readiness score with visual indicator
- Multi-factor breakdown
- Strengths and gaps analysis
- Quick win suggestions
- Add to Future Reads button
- Generate preparation plan button

**Usage:**
```tsx
<BookEvaluation
  bookId={123}
  bookTitle="Infinite Jest"
  onAddToFutureReads={handleAdd}
/>
```

### 3. FutureReadsBoard.tsx

Dashboard for managing future reads.

**Features:**
- Grid view of all future reads
- Readiness score visualization
- Status filtering (waiting, preparing, ready)
- Manual readiness check trigger
- Preparation plan generation
- Ready books alerts

**Usage:**
```tsx
<FutureReadsBoard />
```

---

## Database Schema

### New Tables

#### manually_added_books
Tracks books added outside the recommendation system.

```sql
CREATE TABLE manually_added_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_of_recommendation TEXT,
    recommender_name TEXT,
    why_read TEXT,
    was_outside_comfort_zone BOOLEAN DEFAULT 0,
    ai_analysis_complete BOOLEAN DEFAULT 0,
    profile_impact_calculated BOOLEAN DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

#### book_analysis
AI-generated deep analysis of books.

```sql
CREATE TABLE book_analysis (
    book_id INTEGER PRIMARY KEY,
    complexity_score INTEGER CHECK(complexity_score BETWEEN 1 AND 10),
    themes TEXT, -- JSON array
    mood_tags TEXT, -- JSON object
    writing_style TEXT,
    similar_books TEXT, -- JSON array
    reader_level TEXT,
    content_warnings TEXT, -- JSON array
    character_vs_plot_score REAL,
    narrative_structure TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

#### external_recommendations
Track recommendations from external sources.

```sql
CREATE TABLE external_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    recommender_type TEXT,
    recommender_name TEXT,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommendation_context TEXT,
    trust_score REAL DEFAULT 0.5,
    match_accuracy REAL,
    was_good_match BOOLEAN,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

#### future_reads
Books the user wants to read eventually.

```sql
CREATE TABLE future_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommended_by TEXT,
    current_readiness_score INTEGER,
    target_readiness_score INTEGER DEFAULT 75,
    estimated_ready_date DATE,
    preparation_plan_id INTEGER,
    reason_deferred TEXT,
    user_notes TEXT,
    reminder_preference TEXT DEFAULT 'when_ready',
    status TEXT DEFAULT 'waiting',
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (preparation_plan_id) REFERENCES reading_plans(id)
);
```

#### readiness_checkpoints
Monitor progression toward future books.

```sql
CREATE TABLE readiness_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    future_read_id INTEGER NOT NULL,
    checkpoint_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    readiness_score INTEGER,
    factors_assessed TEXT, -- JSON object
    gaps_identified TEXT, -- JSON array
    progress_since_last REAL,
    books_that_helped TEXT, -- JSON array
    ai_insights TEXT,
    FOREIGN KEY (future_read_id) REFERENCES future_reads(id)
);
```

#### book_interactions
Unified tracking of all book interactions.

```sql
CREATE TABLE book_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    interaction_type TEXT,
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interaction_context TEXT, -- JSON
    session_id TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

#### reading_history_complete
Comprehensive reading history with enriched data.

```sql
CREATE TABLE reading_history_complete (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_started TIMESTAMP,
    date_completed TIMESTAMP,
    rating INTEGER,
    how_discovered TEXT,
    discovery_source_id INTEGER,
    was_in_comfort_zone BOOLEAN,
    exceeded_expectations BOOLEAN,
    complexity_match TEXT,
    mood_at_start TEXT, -- JSON
    mood_at_end TEXT, -- JSON
    profile_alignment_score REAL,
    contributed_to_growth BOOLEAN,
    notes TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

---

## Usage Examples

### Example 1: Friend Recommends a Book

```typescript
// 1. Friend tells you about "The Overstory"
// 2. Quick add by search
const response = await axios.post(
  '/api/manual/quick-add/search?query=The Overstory&source=friend&recommender_name=Sarah'
);

// 3. Evaluate if you're ready
const evaluation = await axios.post(
  `/api/manual/evaluate/${response.data.book_id}`
);

// 4. If not ready, add to Future Reads
if (evaluation.data.evaluation.readiness_score < 75) {
  await axios.post('/api/manual/future-reads/add', {
    book_id: response.data.book_id,
    user_notes: "Sarah loved it, wants to discuss when I read it"
  });
}
```

### Example 2: Goodreads Import Workflow

```typescript
// 1. Import Goodreads library
const formData = new FormData();
formData.append('file', goodreadsCSV);

const importResult = await axios.post(
  '/api/manual/batch-import',
  formData
);

// 2. Run readiness check on all new books
const readinessCheck = await axios.post(
  '/api/manual/readiness-check/run'
);

// 3. Get books you're ready for
const readyBooks = await axios.get(
  '/api/manual/readiness-check/notifications'
);

// Now you have your entire library organized by readiness!
```

### Example 3: Preparation Plan for Classic

```typescript
// Want to read "Ulysses" but it's intimidating?

// 1. Add the book
const book = await axios.post('/api/manual/quick-add/search?query=Ulysses Joyce');

// 2. Evaluate
const eval = await axios.post(`/api/manual/evaluate/${book.data.book_id}`);
// Readiness: 25/100 - "Not Yet"

// 3. Generate preparation plan
const plan = await axios.post(
  `/api/manual/preparation-plan/${book.data.book_id}`
);

// Get a custom 3-4 book roadmap that builds up to Ulysses!
// Follow the plan, and the system monitors your progress automatically
```

---

## Implementation Notes

### AI Prompts

The system uses carefully crafted prompts for:

1. **Book Analysis** - Comprehensive analysis of any book
2. **Readiness Evaluation** - Multi-factor assessment considering reader profile
3. **Preparation Plans** - Custom reading roadmaps

All prompts use Claude Sonnet 4.5 with temperature 0.6-0.7 for balanced creativity and accuracy.

### Performance Optimization

- Book analysis results are cached
- Batch operations minimize AI API calls
- Readiness checks are rate-limited (max once per week per book)
- Indexes on all foreign keys and frequently queried fields

### Privacy & Data

- All data stored locally in SQLite
- No external data sharing
- AI analysis happens on-demand
- User controls all book additions and evaluations

---

## Troubleshooting

### Common Issues

**Book Not Found by ISBN**
- Try search by title instead
- Check ISBN format (ISBN-10 vs ISBN-13)
- Use manual entry as fallback

**Evaluation Taking Long**
- First evaluation builds your reading DNA (may take 30-60 seconds)
- Subsequent evaluations are faster
- Ensure ANTHROPIC_API_KEY is set

**Readiness Check Not Finding Updates**
- Requires at least 7 days between checks
- Complete more books to improve profile
- Check that Future Reads exist

---

## Future Enhancements (Planned)

- Mobile app with barcode scanning
- Social features (share future reads, compare readiness)
- Book club integration
- Reading challenge based on readiness scores
- ML-based readiness prediction (supplement AI)
- Integration with library apps beyond Sno-Isle

---

## Version History

**Version 3.0.0** (Current)
- Manual book entry system
- "Should I Read This?" evaluation
- Future Reads management
- Readiness monitoring
- Preparation plan generation

For previous versions, see TIER1_TIER2_FEATURES.md and README.md.
