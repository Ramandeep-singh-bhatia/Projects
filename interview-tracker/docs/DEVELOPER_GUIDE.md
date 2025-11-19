# Developer Guide

Technical implementation guide for developers working on the Interview Preparation Tracker.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Database Schema](#database-schema)
- [API Design](#api-design)
- [Key Algorithms](#key-algorithms)
- [Testing](#testing)
- [Code Style & Standards](#code-style--standards)
- [Contributing](#contributing)
- [Extending the Application](#extending-the-application)

## Architecture Overview

### Technology Stack

**Backend:**
- Spring Boot 3.2.0 (Java 17)
- Spring Data JPA / Hibernate
- H2 Database (embedded, file-based)
- Lombok for boilerplate reduction
- Maven for dependency management

**Frontend:**
- React 18 with TypeScript 5.2+
- Vite for build tooling
- Tailwind CSS for styling
- Axios for HTTP clients
- React Router v6 for navigation

### Design Patterns

**Backend:**
- **Layered Architecture:** Controller → Service → Repository
- **Dependency Injection:** Spring autowiring
- **DTO Pattern:** Separate domain models from API contracts
- **Repository Pattern:** Spring Data JPA repositories
- **Builder Pattern:** Lombok @Builder for entity creation

**Frontend:**
- **Component Composition:** Reusable React components
- **Custom Hooks:** Shared logic extraction
- **Service Layer:** API abstraction in services/
- **Type Safety:** Comprehensive TypeScript types

### Project Structure

```
backend/src/main/java/com/interviewtracker/
├── config/             # Configuration classes
│   ├── CorsConfig.java
│   ├── FileStorageConfig.java
│   └── WebConfig.java
│
├── controller/         # REST API controllers
│   ├── TopicController.java
│   ├── PracticeSessionController.java
│   ├── FlashcardController.java
│   ├── PomodoroController.java
│   └── ... (14 more)
│
├── service/            # Business logic layer
│   ├── TopicService.java
│   ├── FlashcardService.java (SM-2 algorithm)
│   ├── ConfidenceDecayService.java
│   ├── AnalyticsService.java
│   └── ... (14 more)
│
├── repository/         # Data access layer
│   ├── TopicRepository.java
│   ├── FlashcardRepository.java
│   └── ... (10 more)
│
├── model/              # JPA entities
│   ├── Topic.java
│   ├── Flashcard.java
│   ├── Pomodoro.java
│   └── ... (9 more)
│
├── dto/                # Data Transfer Objects
│   ├── TopicDTO.java
│   └── ... (API request/response models)
│
├── exception/          # Custom exceptions
│   ├── ResourceNotFoundException.java
│   ├── FileStorageException.java
│   └── GlobalExceptionHandler.java
│
└── InterviewTrackerApplication.java  # Main entry point
```

```
frontend/src/
├── components/         # React components
│   ├── common/         # Shared components (Button, Card, etc.)
│   ├── topics/         # Topic management UI
│   ├── flashcards/     # Flashcard system UI
│   ├── pomodoro/       # Pomodoro timer UI
│   ├── analytics/      # Charts and analytics
│   └── voicenotes/     # Audio recording UI
│
├── services/           # API service layer
│   ├── api.ts          # Axios instance configuration
│   ├── topicService.ts
│   ├── flashcardService.ts
│   └── ... (service per feature)
│
├── types/              # TypeScript type definitions
│   ├── topic.ts
│   ├── flashcard.ts
│   └── ... (types per domain)
│
├── hooks/              # Custom React hooks
│   ├── useTopics.ts
│   ├── useFlashcards.ts
│   └── usePomodoroTimer.ts
│
├── utils/              # Utility functions
│   ├── dateFormatter.ts
│   ├── validators.ts
│   └── constants.ts
│
├── App.tsx             # Root component with routing
├── main.tsx            # Application entry point
└── index.css           # Global styles
```

## Backend Development

### Entity Design

#### Example: Topic Entity

```java
@Entity
@Table(name = "topic")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Topic {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String category;

    @Column(nullable = false)
    private String difficulty;  // EASY, MEDIUM, HARD

    @Column(nullable = false)
    private Integer confidence = 5;  // 1-10 scale

    private String status;  // NOT_STARTED, IN_PROGRESS, COMPLETED

    private Integer estimatedTime;  // minutes

    @Column(length = 2000)
    private String notes;

    @Column(length = 1000)
    private String thingsToRemember;

    private String sourceUrl;

    private LocalDate reminderDate;

    private LocalDateTime lastStudied;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    // Relationships
    @OneToMany(mappedBy = "topic", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<PracticeSession> sessions = new ArrayList<>();

    @OneToMany(mappedBy = "topic", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<Flashcard> flashcards = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

**Key Annotations:**
- `@Entity` - Marks as JPA entity
- `@Table` - Specifies table name
- `@Data` - Lombok generates getters/setters/toString/equals/hashCode
- `@Builder` - Lombok generates builder pattern
- `@OneToMany` - Defines relationships
- `@JsonIgnore` - Prevents circular serialization
- `@PrePersist/@PreUpdate` - Lifecycle callbacks

### Repository Layer

```java
public interface TopicRepository extends JpaRepository<Topic, Long> {

    // Derived query methods (Spring Data JPA auto-implements)
    List<Topic> findByCategory(String category);

    List<Topic> findByConfidenceLessThan(Integer confidence);

    List<Topic> findByLastStudiedBefore(LocalDateTime date);

    // Custom query using @Query
    @Query("SELECT t FROM Topic t WHERE t.confidence < :threshold " +
           "AND t.lastStudied < :cutoffDate")
    List<Topic> findStaleTopics(
        @Param("threshold") Integer threshold,
        @Param("cutoffDate") LocalDateTime cutoffDate
    );

    // Native SQL query
    @Query(value = "SELECT category, AVG(confidence) as avgConfidence " +
                   "FROM topic GROUP BY category",
           nativeQuery = true)
    List<Object[]> getCategoryAverages();
}
```

### Service Layer

```java
@Service
public class TopicService {

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private PracticeSessionRepository sessionRepository;

    // Business logic methods

    public List<Topic> getAllTopics() {
        return topicRepository.findAll();
    }

    public Topic getTopicById(Long id) {
        return topicRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Topic not found"));
    }

    public Topic createTopic(Topic topic) {
        validateTopic(topic);
        return topicRepository.save(topic);
    }

    @Transactional
    public Topic updateTopic(Long id, Topic updatedTopic) {
        Topic topic = getTopicById(id);

        // Update fields
        topic.setName(updatedTopic.getName());
        topic.setConfidence(updatedTopic.getConfidence());
        // ... other fields

        return topicRepository.save(topic);
    }

    @Transactional
    public void deleteTopic(Long id) {
        Topic topic = getTopicById(id);
        topicRepository.delete(topic);  // Cascades to related entities
    }

    private void validateTopic(Topic topic) {
        if (topic.getName() == null || topic.getName().trim().isEmpty()) {
            throw new IllegalArgumentException("Topic name is required");
        }
        if (topic.getConfidence() < 1 || topic.getConfidence() > 10) {
            throw new IllegalArgumentException("Confidence must be 1-10");
        }
    }
}
```

### Controller Layer

```java
@RestController
@RequestMapping("/api/topics")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
public class TopicController {

    @Autowired
    private TopicService topicService;

    @GetMapping
    public ResponseEntity<List<Topic>> getAllTopics() {
        return ResponseEntity.ok(topicService.getAllTopics());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Topic> getTopicById(@PathVariable Long id) {
        return ResponseEntity.ok(topicService.getTopicById(id));
    }

    @PostMapping
    public ResponseEntity<Topic> createTopic(@Valid @RequestBody Topic topic) {
        Topic created = topicService.createTopic(topic);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Topic> updateTopic(
            @PathVariable Long id,
            @Valid @RequestBody Topic topic) {
        Topic updated = topicService.updateTopic(id, topic);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTopic(@PathVariable Long id) {
        topicService.deleteTopic(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/category/{category}")
    public ResponseEntity<List<Topic>> getTopicsByCategory(
            @PathVariable String category) {
        return ResponseEntity.ok(topicService.getTopicsByCategory(category));
    }
}
```

**Key Annotations:**
- `@RestController` - Marks as REST controller (combines @Controller + @ResponseBody)
- `@RequestMapping` - Base URL path
- `@GetMapping/@PostMapping/@PutMapping/@DeleteMapping` - HTTP methods
- `@PathVariable` - Extract from URL path
- `@RequestBody` - Parse request body to Java object
- `@Valid` - Trigger validation
- `@CrossOrigin` - Enable CORS for specific origins

### Exception Handling

```java
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(
            ResourceNotFoundException ex) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            LocalDateTime.now()
        );
        return new ResponseEntity<>(error, HttpStatus.NOT_FOUND);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorResponse> handleIllegalArgument(
            IllegalArgumentException ex) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            ex.getMessage(),
            LocalDateTime.now()
        );
        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(
            Exception ex) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "An unexpected error occurred",
            LocalDateTime.now()
        );
        return new ResponseEntity<>(error, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

### Configuration

#### CORS Configuration

```java
@Configuration
public class CorsConfig {

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins("http://localhost:3000", "http://localhost:5173")
                    .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                    .allowedHeaders("*")
                    .allowCredentials(true)
                    .maxAge(3600);
            }
        };
    }
}
```

#### File Storage Configuration

```java
@Configuration
@ConfigurationProperties(prefix = "app.file-storage")
@Data
public class FileStorageConfig {
    private String uploadDir = "./uploads";
    private String backupDir = "./uploads/backups";

    @PostConstruct
    public void init() {
        try {
            Files.createDirectories(Paths.get(uploadDir));
            Files.createDirectories(Paths.get(backupDir));
        } catch (IOException e) {
            throw new RuntimeException("Could not create upload directories", e);
        }
    }
}
```

## Frontend Development

### TypeScript Types

```typescript
// types/topic.ts
export interface Topic {
  id: number;
  name: string;
  category: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  confidence: number;  // 1-10
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED';
  estimatedTime?: number;
  notes?: string;
  thingsToRemember?: string;
  sourceUrl?: string;
  reminderDate?: string;
  lastStudied?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateTopicRequest {
  name: string;
  category: string;
  difficulty: string;
  confidence: number;
  status?: string;
  estimatedTime?: number;
  notes?: string;
  thingsToRemember?: string;
  sourceUrl?: string;
  reminderDate?: string;
}
```

### API Service Layer

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',  // Vite proxy handles this
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for auth tokens, etc.)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (for error handling)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

```typescript
// services/topicService.ts
import api from './api';
import { Topic, CreateTopicRequest } from '../types/topic';

export const topicService = {

  getAllTopics: async (): Promise<Topic[]> => {
    const response = await api.get<Topic[]>('/topics');
    return response.data;
  },

  getTopicById: async (id: number): Promise<Topic> => {
    const response = await api.get<Topic>(`/topics/${id}`);
    return response.data;
  },

  createTopic: async (data: CreateTopicRequest): Promise<Topic> => {
    const response = await api.post<Topic>('/topics', data);
    return response.data;
  },

  updateTopic: async (id: number, data: Partial<Topic>): Promise<Topic> => {
    const response = await api.put<Topic>(`/topics/${id}`, data);
    return response.data;
  },

  deleteTopic: async (id: number): Promise<void> => {
    await api.delete(`/topics/${id}`);
  },

  getTopicsByCategory: async (category: string): Promise<Topic[]> => {
    const response = await api.get<Topic[]>(`/topics/category/${category}`);
    return response.data;
  },
};
```

### Custom Hooks

```typescript
// hooks/useTopics.ts
import { useState, useEffect } from 'react';
import { topicService } from '../services/topicService';
import { Topic } from '../types/topic';

export const useTopics = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTopics = async () => {
    try {
      setLoading(true);
      const data = await topicService.getAllTopics();
      setTopics(data);
      setError(null);
    } catch (err) {
      setError('Failed to load topics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const createTopic = async (topic: CreateTopicRequest) => {
    const newTopic = await topicService.createTopic(topic);
    setTopics([...topics, newTopic]);
    return newTopic;
  };

  const updateTopic = async (id: number, updates: Partial<Topic>) => {
    const updatedTopic = await topicService.updateTopic(id, updates);
    setTopics(topics.map(t => t.id === id ? updatedTopic : t));
    return updatedTopic;
  };

  const deleteTopic = async (id: number) => {
    await topicService.deleteTopic(id);
    setTopics(topics.filter(t => t.id !== id));
  };

  return {
    topics,
    loading,
    error,
    fetchTopics,
    createTopic,
    updateTopic,
    deleteTopic,
  };
};
```

### Component Structure

```typescript
// components/topics/TopicCard.tsx
import React from 'react';
import { Topic } from '../../types/topic';
import { Edit, Trash2, BookOpen } from 'lucide-react';

interface TopicCardProps {
  topic: Topic;
  onEdit: (topic: Topic) => void;
  onDelete: (id: number) => void;
  onPractice: (topic: Topic) => void;
}

export const TopicCard: React.FC<TopicCardProps> = ({
  topic,
  onEdit,
  onDelete,
  onPractice,
}) => {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'EASY': return 'bg-green-100 text-green-800';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800';
      case 'HARD': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 8) return 'text-green-600';
    if (confidence >= 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold">{topic.name}</h3>
        <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(topic.difficulty)}`}>
          {topic.difficulty}
        </span>
      </div>

      <div className="mb-4">
        <span className="text-sm text-gray-600">Category: </span>
        <span className="text-sm font-medium">{topic.category}</span>
      </div>

      <div className="mb-4">
        <span className="text-sm text-gray-600">Confidence: </span>
        <span className={`text-sm font-bold ${getConfidenceColor(topic.confidence)}`}>
          {topic.confidence}/10
        </span>
      </div>

      {topic.lastStudied && (
        <div className="text-sm text-gray-500 mb-4">
          Last studied: {new Date(topic.lastStudied).toLocaleDateString()}
        </div>
      )}

      <div className="flex gap-2 mt-4">
        <button
          onClick={() => onPractice(topic)}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 flex items-center justify-center gap-2"
        >
          <BookOpen size={16} />
          Practice
        </button>
        <button
          onClick={() => onEdit(topic)}
          className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded"
        >
          <Edit size={20} />
        </button>
        <button
          onClick={() => onDelete(topic.id)}
          className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded"
        >
          <Trash2 size={20} />
        </button>
      </div>
    </div>
  );
};
```

### Routing

```typescript
// App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { TopicsPage } from './pages/TopicsPage';
import { FlashcardsPage } from './pages/FlashcardsPage';
import { PomodoroPage } from './pages/PomodoroPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="topics" element={<TopicsPage />} />
          <Route path="flashcards" element={<FlashcardsPage />} />
          <Route path="pomodoro" element={<PomodoroPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

## Database Schema

### Entity Relationship Diagram (ERD)

```
Topic (1) ---> (N) PracticeSession
Topic (1) ---> (N) Flashcard
Topic (1) ---> (N) Pomodoro
Topic (1) ---> (N) FileMetadata
Topic (1) ---> (N) VoiceNote

Settings (1) ---> (N) WeeklyGoal
Settings (1) ---> (N) ConfidenceDecayRule

ConfidenceDecayRule (1) ---> (N) ConfidenceHistory
Topic (1) ---> (N) ConfidenceHistory

MockInterview (1) ---> (N) MockInterviewTopic
Topic (1) ---> (N) MockInterviewTopic
```

### Table Schemas

#### topic
| Column | Type | Constraints |
|--------|------|-------------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT |
| name | VARCHAR(255) | NOT NULL |
| category | VARCHAR(100) | NOT NULL |
| difficulty | VARCHAR(20) | NOT NULL |
| confidence | INT | NOT NULL, DEFAULT 5 |
| status | VARCHAR(50) | |
| estimated_time | INT | |
| notes | TEXT | |
| things_to_remember | VARCHAR(1000) | |
| source_url | VARCHAR(500) | |
| reminder_date | DATE | |
| last_studied | TIMESTAMP | |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### flashcard
| Column | Type | Constraints |
|--------|------|-------------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT |
| topic_id | BIGINT | FOREIGN KEY → topic(id) |
| front | TEXT | NOT NULL |
| back | TEXT | NOT NULL |
| difficulty | VARCHAR(20) | |
| interval | INT | DEFAULT 0 |
| repetitions | INT | DEFAULT 0 |
| ease_factor | INT | DEFAULT 2500 (stored as 2500 = 2.5) |
| next_review_date | DATE | |
| last_reviewed | TIMESTAMP | |
| success_count | INT | DEFAULT 0 |
| failure_count | INT | DEFAULT 0 |
| created_at | TIMESTAMP | NOT NULL |

#### pomodoro
| Column | Type | Constraints |
|--------|------|-------------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT |
| topic_id | BIGINT | FOREIGN KEY → topic(id), NULLABLE |
| phase | VARCHAR(20) | NOT NULL (FOCUS, SHORT_BREAK, LONG_BREAK) |
| duration | INT | NOT NULL (minutes) |
| pomodoro_number | INT | |
| completed | BOOLEAN | DEFAULT FALSE |
| started_at | TIMESTAMP | NOT NULL |
| completed_at | TIMESTAMP | |

#### confidence_history
| Column | Type | Constraints |
|--------|------|-------------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT |
| topic_id | BIGINT | FOREIGN KEY → topic(id), NULLABLE |
| old_confidence | INT | |
| new_confidence | INT | NOT NULL |
| change_reason | VARCHAR(50) | NOT NULL (PRACTICE, DECAY, MANUAL) |
| notes | TEXT | |
| changed_at | TIMESTAMP | NOT NULL |

### Database Indexes

```sql
-- Performance optimization indexes
CREATE INDEX idx_topic_category ON topic(category);
CREATE INDEX idx_topic_confidence ON topic(confidence);
CREATE INDEX idx_topic_last_studied ON topic(last_studied);

CREATE INDEX idx_flashcard_topic ON flashcard(topic_id);
CREATE INDEX idx_flashcard_next_review ON flashcard(next_review_date);

CREATE INDEX idx_session_topic ON practice_session(topic_id);
CREATE INDEX idx_session_date ON practice_session(session_date);

CREATE INDEX idx_pomodoro_topic ON pomodoro(topic_id);
CREATE INDEX idx_pomodoro_started ON pomodoro(started_at);
```

## API Design

### RESTful Principles

**HTTP Methods:**
- GET - Retrieve resources
- POST - Create new resources
- PUT - Update entire resource
- PATCH - Partial update (not used in this project)
- DELETE - Remove resource

**Status Codes:**
- 200 OK - Successful GET, PUT
- 201 Created - Successful POST
- 204 No Content - Successful DELETE
- 400 Bad Request - Invalid input
- 404 Not Found - Resource doesn't exist
- 500 Internal Server Error - Server error

**URL Structure:**
```
/api/topics                    # Collection
/api/topics/{id}               # Single resource
/api/topics/{id}/sessions      # Sub-resource collection
/api/topics/{id}/flashcards    # Sub-resource collection
```

### Request/Response Formats

**Create Topic Request:**
```json
POST /api/topics
Content-Type: application/json

{
  "name": "Binary Search Trees",
  "category": "Data Structures",
  "difficulty": "MEDIUM",
  "confidence": 5,
  "estimatedTime": 120,
  "notes": "Understand insertion, deletion, traversals"
}
```

**Response:**
```json
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 123,
  "name": "Binary Search Trees",
  "category": "Data Structures",
  "difficulty": "MEDIUM",
  "confidence": 5,
  "status": "NOT_STARTED",
  "estimatedTime": 120,
  "notes": "Understand insertion, deletion, traversals",
  "createdAt": "2024-01-15T10:30:00",
  "updatedAt": "2024-01-15T10:30:00"
}
```

**Error Response:**
```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "status": 400,
  "message": "Confidence must be between 1 and 10",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Key Algorithms

### SM-2 Spaced Repetition Algorithm

Located in: `backend/src/main/java/com/interviewtracker/service/FlashcardService.java:submitReview()`

```java
public Flashcard submitReview(Long flashcardId, int quality) {
    // quality: 0-5 (user's self-assessment)

    Flashcard card = getFlashcardById(flashcardId);

    int repetitions = card.getRepetitions();
    int easeFactor = card.getEaseFactor();  // stored as int (2500 = 2.5)
    int interval = card.getInterval();

    // Update interval based on quality
    if (quality >= 3) {
        // Correct response
        if (repetitions == 0) {
            interval = 1;  // First correct: review tomorrow
        } else if (repetitions == 1) {
            interval = 6;  // Second correct: review in 6 days
        } else {
            // Subsequent: multiply by ease factor
            interval = Math.round(interval * (easeFactor / 1000.0f));
        }
        repetitions++;
        card.setSuccessCount(card.getSuccessCount() + 1);
    } else {
        // Incorrect response - reset
        repetitions = 0;
        interval = 1;  // Review tomorrow
        card.setFailureCount(card.getFailureCount() + 1);
    }

    // Update ease factor based on quality
    // Formula: EF' = EF + (0.28 - (5-q) * 0.28)
    // Simplified using integer math: EF += 280 - (5-q) * 280
    easeFactor = easeFactor + (280 - (5 - quality) * 280);

    // Minimum ease factor is 1.3 (1300)
    if (easeFactor < 1300) {
        easeFactor = 1300;
    }

    // Calculate next review date
    LocalDate nextReviewDate = LocalDate.now().plusDays(interval);

    // Update card
    card.setRepetitions(repetitions);
    card.setEaseFactor(easeFactor);
    card.setInterval(interval);
    card.setNextReviewDate(nextReviewDate);
    card.setLastReviewed(LocalDateTime.now());

    return flashcardRepository.save(card);
}
```

**Algorithm Explanation:**
1. Quality ≥3 (correct): increase interval
2. Quality <3 (incorrect): reset interval to 1
3. First correct: 1 day interval
4. Second correct: 6 days interval
5. Subsequent: interval × ease factor
6. Ease factor adjusts based on difficulty (quality rating)
7. Minimum ease factor prevents too-frequent reviews

### Confidence Decay Algorithm

Located in: `backend/src/main/java/com/interviewtracker/service/ConfidenceDecayService.java:applyConfidenceDecay()`

```java
@Scheduled(cron = "0 0 2 * * *")  // Runs daily at 2 AM
public void applyConfidenceDecay() {
    ConfidenceDecayRule rule = getActiveDecayRule();

    if (!rule.isEnabled()) {
        return;
    }

    int daysInactive = rule.getDaysInactive();
    int decayPercentage = rule.getDecayPercentage();

    // Find topics not studied in X days
    LocalDateTime cutoff = LocalDateTime.now().minusDays(daysInactive);
    List<Topic> staleTopics = topicRepository.findByLastStudiedBefore(cutoff);

    for (Topic topic : staleTopics) {
        int oldConfidence = topic.getConfidence();

        // Calculate new confidence
        int decay = (int) Math.ceil(oldConfidence * (decayPercentage / 100.0));
        int newConfidence = Math.max(1, oldConfidence - decay);  // Minimum 1

        // Update topic
        topic.setConfidence(newConfidence);
        topicRepository.save(topic);

        // Record history
        ConfidenceHistory history = ConfidenceHistory.builder()
            .topic(topic)
            .oldConfidence(oldConfidence)
            .newConfidence(newConfidence)
            .changeReason(ChangeReason.DECAY)
            .notes("Automatic decay after " + daysInactive + " days inactive")
            .changedAt(LocalDateTime.now())
            .build();

        confidenceHistoryRepository.save(history);
    }
}
```

**Algorithm Explanation:**
1. Runs daily at 2 AM (configurable via @Scheduled)
2. Checks decay rule settings (enabled, days, percentage)
3. Finds topics not studied in X days
4. Calculates decay: old confidence × decay percentage
5. Applies decay (minimum confidence stays at 1)
6. Records change in audit history

### Mock Interview Generation Algorithm

Located in: `backend/src/main/java/com/interviewtracker/service/MockInterviewService.java:generateMockInterview()`

```java
public MockInterview generateMockInterview(int questionCount) {
    List<Topic> allTopics = topicRepository.findAll();

    // Filter: only topics with some confidence and content
    List<Topic> eligibleTopics = allTopics.stream()
        .filter(t -> t.getConfidence() != null && t.getConfidence() > 0)
        .collect(Collectors.toList());

    // Weighted random selection based on inverse confidence
    // Lower confidence = higher probability of selection
    List<Topic> selected = weightedRandomSelection(eligibleTopics, questionCount);

    // Balance across categories
    selected = balanceCategories(selected);

    // Create mock interview record
    MockInterview interview = MockInterview.builder()
        .questionCount(selected.size())
        .generatedAt(LocalDateTime.now())
        .build();

    mockInterviewRepository.save(interview);

    // Link topics to interview
    for (int i = 0; i < selected.size(); i++) {
        MockInterviewTopic mit = MockInterviewTopic.builder()
            .mockInterview(interview)
            .topic(selected.get(i))
            .questionNumber(i + 1)
            .build();

        mockInterviewTopicRepository.save(mit);
    }

    return interview;
}

private List<Topic> weightedRandomSelection(List<Topic> topics, int count) {
    List<Topic> selected = new ArrayList<>();
    Random random = new Random();

    // Calculate weights (inverse of confidence)
    Map<Topic, Double> weights = new HashMap<>();
    double totalWeight = 0;

    for (Topic topic : topics) {
        double weight = 11.0 - topic.getConfidence();  // Higher for low confidence
        weights.put(topic, weight);
        totalWeight += weight;
    }

    // Select topics using weighted random
    for (int i = 0; i < count && !topics.isEmpty(); i++) {
        double randomValue = random.nextDouble() * totalWeight;
        double cumulative = 0;

        for (Topic topic : topics) {
            cumulative += weights.get(topic);
            if (cumulative >= randomValue) {
                selected.add(topic);
                topics.remove(topic);
                totalWeight -= weights.get(topic);
                break;
            }
        }
    }

    return selected;
}

private List<Topic> balanceCategories(List<Topic> topics) {
    // Ensure no category dominates (max 3 questions per category)
    Map<String, Long> categoryCount = topics.stream()
        .collect(Collectors.groupingBy(Topic::getCategory, Collectors.counting()));

    List<Topic> balanced = new ArrayList<>();
    Map<String, Integer> counts = new HashMap<>();

    for (Topic topic : topics) {
        int currentCount = counts.getOrDefault(topic.getCategory(), 0);
        if (currentCount < 3) {  // Max 3 per category
            balanced.add(topic);
            counts.put(topic.getCategory(), currentCount + 1);
        }
    }

    return balanced;
}
```

**Algorithm Explanation:**
1. Filter topics (must have confidence > 0)
2. Weighted random selection (lower confidence = higher probability)
3. Weight calculation: 11 - confidence (so confidence 2 gets weight 9)
4. Select using cumulative probability distribution
5. Balance categories (max 3 questions per category)
6. Store interview with linked topics

## Testing

### Backend Unit Tests

```java
@SpringBootTest
@AutoConfigureMockMvc
public class TopicServiceTest {

    @Autowired
    private TopicService topicService;

    @MockBean
    private TopicRepository topicRepository;

    @Test
    public void testCreateTopic() {
        // Arrange
        Topic topic = Topic.builder()
            .name("Test Topic")
            .category("DSA")
            .difficulty("MEDIUM")
            .confidence(5)
            .build();

        when(topicRepository.save(any(Topic.class))).thenReturn(topic);

        // Act
        Topic created = topicService.createTopic(topic);

        // Assert
        assertNotNull(created);
        assertEquals("Test Topic", created.getName());
        verify(topicRepository, times(1)).save(topic);
    }

    @Test
    public void testGetTopicById_NotFound() {
        // Arrange
        when(topicRepository.findById(999L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(ResourceNotFoundException.class, () -> {
            topicService.getTopicById(999L);
        });
    }
}
```

### Frontend Unit Tests

```typescript
// __tests__/components/TopicCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TopicCard } from '../components/topics/TopicCard';
import { Topic } from '../types/topic';

describe('TopicCard', () => {
  const mockTopic: Topic = {
    id: 1,
    name: 'Binary Search',
    category: 'Algorithms',
    difficulty: 'EASY',
    confidence: 7,
    status: 'IN_PROGRESS',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  };

  const mockHandlers = {
    onEdit: jest.fn(),
    onDelete: jest.fn(),
    onPractice: jest.fn(),
  };

  it('renders topic information correctly', () => {
    render(<TopicCard topic={mockTopic} {...mockHandlers} />);

    expect(screen.getByText('Binary Search')).toBeInTheDocument();
    expect(screen.getByText('Algorithms')).toBeInTheDocument();
    expect(screen.getByText('7/10')).toBeInTheDocument();
  });

  it('calls onPractice when practice button clicked', () => {
    render(<TopicCard topic={mockTopic} {...mockHandlers} />);

    const practiceButton = screen.getByText('Practice');
    fireEvent.click(practiceButton);

    expect(mockHandlers.onPractice).toHaveBeenCalledWith(mockTopic);
  });
});
```

### Integration Tests

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
public class TopicControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    public void testCreateAndRetrieveTopic() throws Exception {
        // Create topic
        Topic topic = Topic.builder()
            .name("Integration Test Topic")
            .category("Testing")
            .difficulty("EASY")
            .confidence(5)
            .build();

        String topicJson = objectMapper.writeValueAsString(topic);

        MvcResult result = mockMvc.perform(post("/api/topics")
                .contentType(MediaType.APPLICATION_JSON)
                .content(topicJson))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.name").value("Integration Test Topic"))
            .andReturn();

        String responseJson = result.getResponse().getContentAsString();
        Topic createdTopic = objectMapper.readValue(responseJson, Topic.class);

        // Retrieve topic
        mockMvc.perform(get("/api/topics/" + createdTopic.getId()))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Integration Test Topic"));
    }
}
```

## Code Style & Standards

### Java Conventions

- **Naming:**
  - Classes: PascalCase (TopicService)
  - Methods: camelCase (getTopicById)
  - Constants: UPPER_SNAKE_CASE (MAX_CONFIDENCE)
  - Packages: lowercase (com.interviewtracker.service)

- **Formatting:**
  - Indentation: 4 spaces
  - Line length: 120 characters max
  - Braces: Always use, even for single statements

- **Documentation:**
  - JavaDoc for public methods
  - Inline comments for complex logic
  - README in each package

### TypeScript Conventions

- **Naming:**
  - Interfaces/Types: PascalCase (Topic, TopicCardProps)
  - Functions/Variables: camelCase (fetchTopics, topicsList)
  - Components: PascalCase (TopicCard, Dashboard)
  - Constants: UPPER_SNAKE_CASE (API_BASE_URL)

- **Formatting:**
  - Indentation: 2 spaces
  - Semicolons: Required
  - Quotes: Single quotes
  - Line length: 100 characters max

- **TypeScript:**
  - Strict mode enabled
  - Explicit return types for functions
  - Avoid `any` type
  - Use interfaces for object shapes

## Contributing

### Development Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/flashcard-tags
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "Add tagging system to flashcards"
   ```

3. **Run tests:**
   ```bash
   # Backend
   cd backend && mvn test

   # Frontend
   cd frontend && npm test
   ```

4. **Push and create PR:**
   ```bash
   git push origin feature/flashcard-tags
   ```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Build/tooling

**Example:**
```
feat(flashcards): add tagging system

- Add Tag entity and repository
- Implement tag CRUD operations
- Update flashcard UI to support tags
- Add tag filtering

Closes #42
```

## Extending the Application

### Adding a New Entity

1. **Create entity class**
2. **Create repository interface**
3. **Create service class**
4. **Create controller**
5. **Add frontend types**
6. **Create service layer**
7. **Build UI components**

**Example: Adding a "Study Group" feature**

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed extension guides.

---

For API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

For deployment guide, see [DEPLOYMENT.md](DEPLOYMENT.md)
