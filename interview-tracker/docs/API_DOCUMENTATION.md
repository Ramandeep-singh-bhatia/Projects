# API Documentation

Complete REST API reference for the Interview Preparation Tracker backend.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Topics API](#topics-api)
- [Practice Sessions API](#practice-sessions-api)
- [Flashcards API](#flashcards-api)
- [Pomodoro API](#pomodoro-api)
- [Mock Interviews API](#mock-interviews-api)
- [Voice Notes API](#voice-notes-api)
- [Analytics API](#analytics-api)
- [Enhanced Analytics API](#enhanced-analytics-api)
- [Dashboard API](#dashboard-api)
- [Settings API](#settings-api)
- [Confidence Decay API](#confidence-decay-api)
- [Files API](#files-api)
- [Backup & Data Management API](#backup--data-management-api)

## Base URL

```
Development: http://localhost:8080/api
Production: https://your-domain.com/api
```

All endpoints are prefixed with `/api`.

## Authentication

Currently, the application does not implement authentication. All endpoints are publicly accessible.

**For production deployment**, implement authentication using:
- JWT tokens
- Spring Security
- OAuth2 / OpenID Connect

## Response Formats

### Success Response

```json
{
  "id": 1,
  "name": "Binary Search Trees",
  "category": "Data Structures",
  ...
}
```

### Error Response

```json
{
  "status": 404,
  "message": "Topic not found with id: 123",
  "timestamp": "2024-01-15T10:30:00"
}
```

### List Response

```json
[
  { "id": 1, "name": "..." },
  { "id": 2, "name": "..." }
]
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server-side error |

### Common Errors

**Resource Not Found (404):**
```json
{
  "status": 404,
  "message": "Topic not found with id: 999",
  "timestamp": "2024-01-15T10:30:00"
}
```

**Validation Error (400):**
```json
{
  "status": 400,
  "message": "Confidence must be between 1 and 10",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Topics API

Manage interview topics and subjects.

### Get All Topics

```http
GET /api/topics
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Binary Search Trees",
    "category": "Data Structures",
    "difficulty": "MEDIUM",
    "confidence": 7,
    "status": "IN_PROGRESS",
    "estimatedTime": 120,
    "notes": "Focus on deletion operation",
    "thingsToRemember": "In-order traversal gives sorted output",
    "sourceUrl": "https://example.com/bst",
    "reminderDate": "2024-02-01",
    "lastStudied": "2024-01-10T14:30:00",
    "createdAt": "2024-01-01T10:00:00",
    "updatedAt": "2024-01-10T14:30:00"
  }
]
```

### Get Topic by ID

```http
GET /api/topics/{id}
```

**Parameters:**
- `id` (path, required) - Topic ID

**Response (200 OK):** Single topic object

**Response (404 Not Found):** Topic not found error

### Get Topics by Category

```http
GET /api/topics/category/{category}
```

**Parameters:**
- `category` (path, required) - Category name

**Response (200 OK):** Array of topics in that category

### Create Topic

```http
POST /api/topics
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Quicksort Algorithm",
  "category": "Algorithms",
  "difficulty": "MEDIUM",
  "confidence": 5,
  "status": "NOT_STARTED",
  "estimatedTime": 90,
  "notes": "Understand partitioning logic",
  "thingsToRemember": "Average O(n log n), worst O(n²)",
  "sourceUrl": "https://example.com/quicksort",
  "reminderDate": "2024-01-20"
}
```

**Required Fields:**
- `name` (string)
- `category` (string)
- `difficulty` (string: EASY, MEDIUM, HARD)
- `confidence` (integer: 1-10)

**Response (201 Created):** Created topic object with ID

### Update Topic

```http
PUT /api/topics/{id}
Content-Type: application/json
```

**Parameters:**
- `id` (path, required) - Topic ID

**Request Body:** Same as create (all fields optional except required ones)

**Response (200 OK):** Updated topic object

### Delete Topic

```http
DELETE /api/topics/{id}
```

**Parameters:**
- `id` (path, required) - Topic ID

**Response (204 No Content):** Topic deleted successfully

**Note:** Deletes all associated sessions, flashcards, and files (cascade delete)

### Get Topics by Confidence Range

```http
GET /api/topics/confidence?min={min}&max={max}
```

**Parameters:**
- `min` (query, optional) - Minimum confidence (default: 0)
- `max` (query, optional) - Maximum confidence (default: 10)

**Response (200 OK):** Array of topics within confidence range

### Get Stale Topics

```http
GET /api/topics/stale?days={days}
```

**Parameters:**
- `days` (query, required) - Days since last studied

**Response (200 OK):** Array of topics not studied in X days

---

## Practice Sessions API

Log and manage study sessions.

### Get All Sessions

```http
GET /api/sessions
```

**Response (200 OK):** Array of all practice sessions

### Get Session by ID

```http
GET /api/sessions/{id}
```

**Response (200 OK):** Single session object

### Get Sessions for Topic

```http
GET /api/sessions/topic/{topicId}
```

**Parameters:**
- `topicId` (path, required) - Topic ID

**Response (200 OK):** Array of sessions for that topic

### Get Recent Sessions

```http
GET /api/sessions/recent?limit={limit}
```

**Parameters:**
- `limit` (query, optional) - Number of sessions to return (default: 10)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "topicId": 5,
    "topicName": "Binary Search Trees",
    "duration": 45,
    "sessionType": "REVISION",
    "performanceRating": 8,
    "whatWentWell": "Understood deletion",
    "mistakesMade": "Forgot to handle single child case",
    "notes": "Need more practice with edge cases",
    "confidenceBefore": 6,
    "confidenceAfter": 7,
    "sessionDate": "2024-01-15T14:00:00"
  }
]
```

### Create Session

```http
POST /api/sessions/topic/{topicId}
Content-Type: application/json
```

**Parameters:**
- `topicId` (path, required) - Topic ID

**Request Body:**
```json
{
  "duration": 60,
  "sessionType": "FIRST_LEARNING",
  "performanceRating": 7,
  "whatWentWell": "Grasped basic concept",
  "mistakesMade": "Confused with AVL trees",
  "notes": "Review rotation logic",
  "confidenceAfter": 6
}
```

**Session Types:**
- FIRST_LEARNING
- REVISION
- MOCK_INTERVIEW
- QUICK_REVIEW

**Response (201 Created):** Created session object

### Update Session

```http
PUT /api/sessions/{id}
Content-Type: application/json
```

**Response (200 OK):** Updated session object

### Delete Session

```http
DELETE /api/sessions/{id}
```

**Response (204 No Content):** Session deleted

### Get Sessions by Date Range

```http
GET /api/sessions/range?start={start}&end={end}
```

**Parameters:**
- `start` (query, required) - Start date (ISO 8601)
- `end` (query, required) - End date (ISO 8601)

**Response (200 OK):** Array of sessions in date range

---

## Flashcards API

Spaced repetition flashcard system with SM-2 algorithm.

### Get All Flashcards

```http
GET /api/flashcards
```

**Response (200 OK):** Array of all flashcards

### Get Flashcard by ID

```http
GET /api/flashcards/{id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "topicId": 5,
  "topicName": "Binary Search Trees",
  "front": "What is the time complexity of searching in a BST?",
  "back": "Average: O(log n), Worst: O(n) for unbalanced tree",
  "difficulty": "MEDIUM",
  "interval": 6,
  "repetitions": 2,
  "easeFactor": 2500,
  "nextReviewDate": "2024-01-20",
  "lastReviewed": "2024-01-14T10:00:00",
  "successCount": 5,
  "failureCount": 1,
  "createdAt": "2024-01-01T10:00:00"
}
```

### Get Flashcards by Topic

```http
GET /api/flashcards/topic/{topicId}
```

**Parameters:**
- `topicId` (path, required) - Topic ID

**Response (200 OK):** Array of flashcards for topic

### Get Due Flashcards

```http
GET /api/flashcards/due
```

**Response (200 OK):** Array of flashcards due for review today

### Get Flashcards Due by Date

```http
GET /api/flashcards/due/{date}
```

**Parameters:**
- `date` (path, required) - Date in format YYYY-MM-DD

**Response (200 OK):** Array of flashcards due on that date

### Create Flashcard

```http
POST /api/flashcards
Content-Type: application/json
```

**Request Body:**
```json
{
  "topicId": 5,
  "front": "Explain the insertion operation in a BST",
  "back": "Compare with root, go left if smaller, right if larger, repeat until null position found, insert there",
  "difficulty": "EASY"
}
```

**Response (201 Created):** Created flashcard with initial SM-2 values

### Update Flashcard

```http
PUT /api/flashcards/{id}
Content-Type: application/json
```

**Request Body:** Same as create (only front, back, difficulty modifiable)

**Response (200 OK):** Updated flashcard (statistics preserved)

### Delete Flashcard

```http
DELETE /api/flashcards/{id}
```

**Response (204 No Content):** Flashcard deleted

### Submit Flashcard Review

```http
POST /api/flashcards/{id}/review
Content-Type: application/json
```

**Parameters:**
- `id` (path, required) - Flashcard ID

**Request Body:**
```json
{
  "quality": 4
}
```

**Quality Scale (0-5):**
- 0: Complete blackout
- 1: Incorrect but recognized
- 2: Incorrect but familiar
- 3: Correct with difficulty
- 4: Correct with hesitation
- 5: Perfect recall

**Response (200 OK):** Updated flashcard with new SM-2 values

**Algorithm Applied:**
- Updates interval, repetitions, ease factor
- Calculates next review date
- Increments success/failure count

### Reset Flashcard

```http
POST /api/flashcards/{id}/reset
```

**Response (200 OK):** Flashcard with reset SM-2 values (interval=0, repetitions=0, ease=2.5)

### Get Flashcard Statistics

```http
GET /api/flashcards/statistics
```

**Response (200 OK):**
```json
{
  "totalCards": 150,
  "dueToday": 12,
  "masteredCards": 45,
  "averageSuccessRate": 78.5,
  "totalReviews": 523,
  "averageInterval": 8.3
}
```

---

## Pomodoro API

Pomodoro technique timer for focused study sessions.

### Get All Pomodoros

```http
GET /api/pomodoro
```

**Response (200 OK):** Array of all Pomodoro sessions

### Get Pomodoro by ID

```http
GET /api/pomodoro/{id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "topicId": 5,
  "topicName": "Binary Search Trees",
  "phase": "FOCUS",
  "duration": 25,
  "pomodoroNumber": 1,
  "completed": true,
  "startedAt": "2024-01-15T10:00:00",
  "completedAt": "2024-01-15T10:25:00"
}
```

**Phases:**
- FOCUS (25 min default)
- SHORT_BREAK (5 min default)
- LONG_BREAK (15 min default)

### Get Pomodoros by Topic

```http
GET /api/pomodoro/topic/{topicId}
```

**Response (200 OK):** Array of Pomodoros for topic

### Get Today's Pomodoros

```http
GET /api/pomodoro/today
```

**Response (200 OK):** Array of Pomodoros started today

### Start Pomodoro

```http
POST /api/pomodoro/start
Content-Type: application/json
```

**Request Body:**
```json
{
  "topicId": 5,
  "phase": "FOCUS",
  "pomodoroNumber": 1
}
```

**Note:** `topicId` is optional (for break phases)

**Response (201 Created):** Created Pomodoro session (in progress)

### Complete Pomodoro

```http
POST /api/pomodoro/{id}/complete
```

**Parameters:**
- `id` (path, required) - Pomodoro ID

**Response (200 OK):** Updated Pomodoro with completed=true and completedAt timestamp

### Cancel Pomodoro

```http
DELETE /api/pomodoro/{id}
```

**Response (204 No Content):** Pomodoro deleted (use for interrupted sessions)

### Get Pomodoro Statistics

```http
GET /api/pomodoro/statistics
```

**Response (200 OK):**
```json
{
  "totalPomodoros": 127,
  "completedPomodoros": 115,
  "totalFocusTime": 2875,
  "averagePerDay": 5.2,
  "currentStreak": 7,
  "pomodorosByTopic": {
    "Binary Search Trees": 15,
    "Quicksort": 12,
    "System Design": 20
  }
}
```

---

## Mock Interviews API

Generate and track mock interview sessions.

### Get All Mock Interviews

```http
GET /api/mock-interviews
```

**Response (200 OK):** Array of all mock interviews

### Get Mock Interview by ID

```http
GET /api/mock-interviews/{id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "questionCount": 10,
  "generatedAt": "2024-01-15T09:00:00",
  "completedAt": "2024-01-15T10:30:00",
  "totalDuration": 90,
  "averageConfidence": 7.2,
  "topics": [
    {
      "questionNumber": 1,
      "topic": {
        "id": 5,
        "name": "Binary Search Trees",
        "category": "Data Structures",
        "difficulty": "MEDIUM"
      },
      "confidenceRating": 8,
      "answer": "Explained BST properties and operations",
      "notes": "Need to review deletion"
    }
  ]
}
```

### Generate Mock Interview

```http
POST /api/mock-interviews/generate
Content-Type: application/json
```

**Request Body:**
```json
{
  "questionCount": 10,
  "categories": ["Data Structures", "Algorithms"],
  "difficulty": "BALANCED",
  "focusWeakAreas": true
}
```

**Difficulty Options:**
- BALANCED: Mix of Easy/Medium/Hard
- BEGINNER: Mostly Easy/Medium
- ADVANCED: Mostly Medium/Hard

**Response (201 Created):** Generated mock interview with selected topics

**Algorithm:**
- Weighted selection favoring low-confidence topics
- Balanced category distribution
- Respects difficulty preference
- Limits questions per category (max 3)

### Complete Mock Interview

```http
POST /api/mock-interviews/{id}/complete
Content-Type: application/json
```

**Request Body:**
```json
{
  "totalDuration": 90,
  "topicResponses": [
    {
      "topicId": 5,
      "confidenceRating": 8,
      "answer": "Explained insertion, deletion, search operations",
      "notes": "Need to review edge cases"
    }
  ]
}
```

**Response (200 OK):** Updated mock interview with completion data

### Delete Mock Interview

```http
DELETE /api/mock-interviews/{id}
```

**Response (204 No Content):** Mock interview deleted

### Get Mock Interview Statistics

```http
GET /api/mock-interviews/statistics
```

**Response (200 OK):**
```json
{
  "totalInterviews": 15,
  "totalQuestions": 150,
  "averageConfidence": 7.4,
  "averageDuration": 85,
  "improvementTrend": 1.2,
  "weakCategories": ["System Design", "Databases"]
}
```

---

## Voice Notes API

Audio recording management for topics.

### Get All Voice Notes

```http
GET /api/voice-notes
```

**Response (200 OK):** Array of all voice notes

### Get Voice Note by ID

```http
GET /api/voice-notes/{id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "topicId": 5,
  "topicName": "Binary Search Trees",
  "title": "Insertion Explanation",
  "description": "Walkthrough of insertion operation with example",
  "filename": "audio_20240115_100000.webm",
  "fileSize": 1024000,
  "duration": 180,
  "recordedAt": "2024-01-15T10:00:00"
}
```

### Get Voice Notes by Topic

```http
GET /api/voice-notes/topic/{topicId}
```

**Response (200 OK):** Array of voice notes for topic

### Upload Voice Note

```http
POST /api/voice-notes/topic/{topicId}
Content-Type: multipart/form-data
```

**Parameters:**
- `topicId` (path, required) - Topic ID

**Form Data:**
- `file` (file, required) - Audio file (WebM, MP3, WAV)
- `title` (string, optional) - Voice note title
- `description` (string, optional) - Voice note description

**Response (201 Created):** Created voice note metadata

### Update Voice Note Metadata

```http
PUT /api/voice-notes/{id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response (200 OK):** Updated voice note metadata

### Delete Voice Note

```http
DELETE /api/voice-notes/{id}
```

**Response (204 No Content):** Voice note and audio file deleted

### Download Voice Note

```http
GET /api/voice-notes/{id}/download
```

**Response (200 OK):** Audio file binary stream

**Headers:**
- Content-Type: audio/webm (or appropriate audio type)
- Content-Disposition: attachment; filename="audio_*.webm"

---

## Analytics API

Basic analytics and statistics.

### Get Analytics Summary

```http
GET /api/analytics/summary
```

**Response (200 OK):**
```json
{
  "totalTopics": 45,
  "totalSessions": 123,
  "totalStudyTime": 5420,
  "currentStreak": 7,
  "longestStreak": 14,
  "topicsByCategory": {
    "Data Structures": 15,
    "Algorithms": 12,
    "System Design": 10,
    "Behavioral": 8
  },
  "topicsByConfidence": {
    "low": 8,
    "medium": 22,
    "high": 15
  },
  "topicsByDifficulty": {
    "EASY": 12,
    "MEDIUM": 20,
    "HARD": 13
  }
}
```

### Get Recent Activity

```http
GET /api/analytics/recent-activity?limit={limit}
```

**Parameters:**
- `limit` (query, optional) - Number of activities (default: 10)

**Response (200 OK):**
```json
[
  {
    "type": "PRACTICE_SESSION",
    "description": "Practiced Binary Search Trees for 45 minutes",
    "timestamp": "2024-01-15T14:30:00"
  },
  {
    "type": "FLASHCARD_REVIEW",
    "description": "Reviewed 15 flashcards",
    "timestamp": "2024-01-15T10:15:00"
  }
]
```

---

## Enhanced Analytics API

Advanced analytics with detailed insights.

### Get Study Time Trends

```http
GET /api/enhanced-analytics/study-time?period={period}
```

**Parameters:**
- `period` (query, required) - WEEK, MONTH, or YEAR

**Response (200 OK):**
```json
{
  "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  "data": [120, 90, 150, 105, 180, 75, 60],
  "total": 780,
  "average": 111.4
}
```

### Get Confidence Distribution

```http
GET /api/enhanced-analytics/confidence-distribution
```

**Response (200 OK):**
```json
{
  "distribution": [
    { "confidence": 1, "count": 2 },
    { "confidence": 2, "count": 3 },
    ...
    { "confidence": 10, "count": 5 }
  ],
  "averageConfidence": 6.8
}
```

### Get Category Performance

```http
GET /api/enhanced-analytics/category-performance
```

**Response (200 OK):**
```json
[
  {
    "category": "Data Structures",
    "topicCount": 15,
    "averageConfidence": 7.2,
    "totalStudyTime": 1250,
    "completionRate": 73.3
  }
]
```

### Get Streak Information

```http
GET /api/enhanced-analytics/streaks
```

**Response (200 OK):**
```json
{
  "currentStreak": 7,
  "longestStreak": 14,
  "studyDates": ["2024-01-10", "2024-01-11", "2024-01-12"],
  "streakHistory": [
    { "startDate": "2024-01-01", "endDate": "2024-01-14", "length": 14 }
  ]
}
```

---

## Dashboard API

Dashboard widgets and revision suggestions.

### Get Revision Suggestions

```http
GET /api/dashboard/suggestions?category={category}&limit={limit}
```

**Parameters:**
- `category` (query, optional) - Filter by category
- `limit` (query, optional) - Number of suggestions (default: 10)

**Response (200 OK):**
```json
[
  {
    "topic": {
      "id": 5,
      "name": "Binary Search Trees",
      "category": "Data Structures",
      "difficulty": "MEDIUM",
      "confidence": 5
    },
    "priorityScore": 8.5,
    "daysSinceLastStudy": 12,
    "recommendedAction": "REVIEW"
  }
]
```

**Priority Algorithm:**
```
Priority = (Difficulty Weight) × (Confidence Weight) × (Recency Weight)

Difficulty Weight:
  EASY = 1.0, MEDIUM = 1.5, HARD = 2.0

Confidence Weight:
  (11 - confidence) / 10

Recency Weight:
  0-1 days: 0.3
  2-3 days: 0.6
  4-7 days: 1.0
  8-14 days: 1.5
  15-30 days: 2.0
  31+ days: 2.5
```

### Get Weekly Progress

```http
GET /api/dashboard/weekly/progress
```

**Response (200 OK):**
```json
{
  "weekStart": "2024-01-15",
  "weekEnd": "2024-01-21",
  "categories": [
    {
      "category": "Data Structures",
      "goal": 300,
      "actual": 245,
      "percentage": 81.7,
      "status": "ON_TRACK"
    }
  ],
  "totalGoal": 1200,
  "totalActual": 890,
  "overallPercentage": 74.2
}
```

### Get Weekly History

```http
GET /api/dashboard/weekly/history?weeks={weeks}
```

**Parameters:**
- `weeks` (query, optional) - Number of weeks to retrieve (default: 8)

**Response (200 OK):** Array of weekly progress for past N weeks

---

## Settings API

Application configuration and user preferences.

### Get Settings

```http
GET /api/settings
```

**Response (200 OK):**
```json
{
  "id": 1,
  "dailyStudyGoal": 120,
  "weekStartDay": "MONDAY",
  "pomodoroFocusDuration": 25,
  "pomodoroShortBreak": 5,
  "pomodoroLongBreak": 15,
  "pomodoroLongBreakInterval": 4,
  "enableNotifications": true,
  "enableAutoBackup": true,
  "autoBackupFrequency": "WEEKLY",
  "theme": "LIGHT"
}
```

### Update Settings

```http
PUT /api/settings
Content-Type: application/json
```

**Request Body:** Same structure as GET response (partial updates supported)

**Response (200 OK):** Updated settings

### Get Weekly Goals

```http
GET /api/settings/weekly-goals
```

**Response (200 OK):**
```json
[
  { "category": "Data Structures", "weeklyGoal": 300 },
  { "category": "Algorithms", "weeklyGoal": 240 },
  { "category": "System Design", "weeklyGoal": 180 }
]
```

### Update Weekly Goal

```http
PUT /api/settings/weekly-goals/{category}
Content-Type: application/json
```

**Request Body:**
```json
{
  "weeklyGoal": 360
}
```

**Response (200 OK):** Updated weekly goal

---

## Confidence Decay API

Automatic confidence decay management.

### Get Active Decay Rule

```http
GET /api/confidence-decay/rule
```

**Response (200 OK):**
```json
{
  "id": 1,
  "enabled": true,
  "daysInactive": 7,
  "decayPercentage": 5,
  "applyToCategories": ["Data Structures", "Algorithms"],
  "excludedTopicIds": [5, 12],
  "createdAt": "2024-01-01T10:00:00"
}
```

### Update Decay Rule

```http
PUT /api/confidence-decay/rule
Content-Type: application/json
```

**Request Body:**
```json
{
  "enabled": true,
  "daysInactive": 10,
  "decayPercentage": 8,
  "applyToCategories": ["Data Structures"],
  "excludedTopicIds": [5]
}
```

**Response (200 OK):** Updated decay rule

### Apply Decay Manually

```http
POST /api/confidence-decay/apply
```

**Response (200 OK):**
```json
{
  "topicsDecayed": 12,
  "averageDecayAmount": 2.3,
  "executedAt": "2024-01-15T10:00:00"
}
```

**Note:** Normally runs automatically via scheduled task (daily at 2 AM)

### Get Decay History

```http
GET /api/confidence-decay/history?topicId={topicId}&limit={limit}
```

**Parameters:**
- `topicId` (query, optional) - Filter by topic
- `limit` (query, optional) - Number of records (default: 50)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "topicId": 5,
    "topicName": "Binary Search Trees",
    "oldConfidence": 8,
    "newConfidence": 7,
    "changeReason": "DECAY",
    "notes": "Automatic decay after 7 days inactive",
    "changedAt": "2024-01-15T02:00:00"
  }
]
```

### Get Topics Due for Decay

```http
GET /api/confidence-decay/due
```

**Response (200 OK):** Array of topics that will decay on next run

---

## Files API

File upload and management for topics.

### Upload File

```http
POST /api/files/upload/{topicId}
Content-Type: multipart/form-data
```

**Parameters:**
- `topicId` (path, required) - Topic ID

**Form Data:**
- `file` (file, required) - File to upload

**Supported Types:**
- Documents: PDF, DOC, DOCX, TXT, MD
- Images: JPG, JPEG, PNG, GIF
- Code: HTML, JSON, XML

**Max Size:** 10 MB (configurable)

**Response (201 Created):**
```json
{
  "id": 1,
  "topicId": 5,
  "filename": "bst_notes.pdf",
  "originalFilename": "my_notes.pdf",
  "fileType": "application/pdf",
  "fileSize": 524288,
  "uploadedAt": "2024-01-15T10:00:00"
}
```

### Get Files for Topic

```http
GET /api/files/topic/{topicId}
```

**Response (200 OK):** Array of file metadata for topic

### Download File

```http
GET /api/files/{id}
```

**Response (200 OK):** File binary stream

**Headers:**
- Content-Type: (appropriate MIME type)
- Content-Disposition: attachment; filename="..."

### Preview File

```http
GET /api/files/{id}/preview
```

**Note:** Only works for images and text files

**Response (200 OK):** File content for preview

### Delete File

```http
DELETE /api/files/{id}
```

**Response (204 No Content):** File and metadata deleted

---

## Backup & Data Management API

Data export, import, and backup operations.

### Export All Data

```http
GET /api/data/export
```

**Response (200 OK):** JSON file download

**Includes:**
- All topics
- All practice sessions
- All flashcards
- All Pomodoro sessions
- All mock interviews
- All voice notes metadata
- Settings
- Decay rules
- Confidence history

### Import Data

```http
POST /api/data/import
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (file, required) - JSON backup file
- `mode` (string, required) - REPLACE or MERGE

**Modes:**
- REPLACE: Delete all current data, import backup
- MERGE: Keep current data, add backup data (handle duplicates)

**Response (200 OK):**
```json
{
  "topicsImported": 45,
  "sessionsImported": 123,
  "flashcardsImported": 150,
  "conflicts": 3,
  "importedAt": "2024-01-15T10:00:00"
}
```

### Create Backup

```http
POST /api/data/backup
```

**Response (201 Created):**
```json
{
  "filename": "backup_20240115_100000.json",
  "fileSize": 2048576,
  "recordCount": 318,
  "createdAt": "2024-01-15T10:00:00"
}
```

**Note:** Backup file saved to `uploads/backups/` directory

### Get Storage Info

```http
GET /api/data/storage-info
```

**Response (200 OK):**
```json
{
  "databaseSize": 5242880,
  "uploadedFilesSize": 15728640,
  "audioFilesSize": 8388608,
  "backupsSize": 4194304,
  "totalSize": 33554432,
  "fileCount": {
    "documents": 12,
    "audio": 8,
    "images": 5,
    "backups": 3
  },
  "lastBackupDate": "2024-01-14T10:00:00"
}
```

### Reset All Data

```http
DELETE /api/data/reset
```

**Warning:** Permanently deletes ALL data

**Response (204 No Content):** All data deleted

**Note:** Requires confirmation (implement in frontend)

---

## Rate Limiting

Currently no rate limiting is implemented. For production:

- Implement Spring Security with rate limiting
- Use Redis or in-memory rate limiter
- Typical limits:
  - 100 requests/minute for GET endpoints
  - 20 requests/minute for POST/PUT/DELETE endpoints
  - 5 requests/minute for expensive operations (backup, export)

## Versioning

Current API version: **v1** (implicit in base URL)

Future versions:
- `/api/v2/topics` - For breaking changes
- Maintain v1 for backward compatibility

## Pagination

Large list endpoints should support pagination:

```http
GET /api/topics?page=0&size=20&sort=name,asc
```

**Parameters:**
- `page` (query) - Page number (0-indexed)
- `size` (query) - Items per page
- `sort` (query) - Sort field and direction

**Response:**
```json
{
  "content": [...],
  "page": 0,
  "size": 20,
  "totalElements": 150,
  "totalPages": 8,
  "last": false
}
```

## CORS

Allowed origins (configurable):
- `http://localhost:3000`
- `http://localhost:5173`
- Production domain(s)

## WebSocket Support

Not currently implemented. Future consideration for:
- Real-time Pomodoro timer sync
- Live analytics updates
- Collaborative features

---

## Testing the API

### Using cURL

```bash
# Get all topics
curl http://localhost:8080/api/topics

# Create a topic
curl -X POST http://localhost:8080/api/topics \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Topic",
    "category": "Testing",
    "difficulty": "EASY",
    "confidence": 5
  }'

# Update topic
curl -X PUT http://localhost:8080/api/topics/1 \
  -H "Content-Type: application/json" \
  -d '{"confidence": 7}'

# Delete topic
curl -X DELETE http://localhost:8080/api/topics/1
```

### Using Postman

1. Import OpenAPI spec (if available)
2. Set base URL: `http://localhost:8080/api`
3. Create collection with all endpoints
4. Use environment variables for IDs

### Using HTTPie

```bash
# Get all topics
http GET localhost:8080/api/topics

# Create topic
http POST localhost:8080/api/topics \
  name="Test Topic" \
  category="Testing" \
  difficulty="EASY" \
  confidence:=5
```

---

For implementation details, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

For usage examples, see [USER_GUIDE.md](USER_GUIDE.md)
