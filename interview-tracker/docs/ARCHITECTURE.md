# Architecture Documentation

System architecture, design patterns, and technical decisions for the Interview Preparation Tracker.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Design Patterns](#design-patterns)
- [Data Flow](#data-flow)
- [Key Design Decisions](#key-design-decisions)
- [Scalability Considerations](#scalability-considerations)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          React 18 + TypeScript Frontend                │ │
│  │  - Component-based UI                                  │ │
│  │  - State management (React hooks)                      │ │
│  │  - Client-side routing                                 │ │
│  │  - API service layer                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST (JSON)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Spring Boot 3.2.0 Backend                    │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Controller Layer (REST API)                     │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Service Layer (Business Logic)                  │ │ │
│  │  │  - Topic Management                              │ │ │
│  │  │  - Flashcard SM-2 Algorithm                      │ │ │
│  │  │  - Confidence Decay Engine                       │ │ │
│  │  │  - Mock Interview Generator                      │ │ │
│  │  │  - Analytics Calculator                          │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Repository Layer (Data Access)                  │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ JDBC/JPA
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Persistence Layer                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           H2 Database (File-based)                     │ │
│  │  - Topics, Sessions, Flashcards                        │ │
│  │  - Pomodoros, Mock Interviews                          │ │
│  │  - Settings, Analytics Data                            │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           File System Storage                          │ │
│  │  - Uploaded documents (PDFs, images)                   │ │
│  │  - Voice recordings (audio files)                      │ │
│  │  - Backup files (JSON exports)                         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack Summary

**Frontend:**
- React 18 (UI framework)
- TypeScript 5.2+ (type safety)
- Vite 5.0 (build tool)
- Tailwind CSS 3.4 (styling)
- Axios (HTTP client)
- React Router v6 (routing)
- Recharts 2.10 (data visualization)

**Backend:**
- Spring Boot 3.2.0 (application framework)
- Java 17 (programming language)
- Spring Data JPA (ORM)
- Hibernate (JPA implementation)
- Lombok (boilerplate reduction)
- Maven (build tool)

**Database & Storage:**
- H2 Database (embedded, file-based)
- File system (uploads directory)

## Architecture Diagram

### Component Interaction

```
Frontend (React)
├── Pages
│   ├── Dashboard
│   ├── Topics
│   ├── Flashcards
│   ├── Pomodoro
│   ├── Mock Interviews
│   └── Analytics
│
├── Components
│   ├── TopicCard
│   ├── FlashcardReview
│   ├── PomodoroTimer
│   └── AnalyticsChart
│
├── Services (API Layer)
│   ├── topicService.ts
│   ├── flashcardService.ts
│   ├── pomodoroService.ts
│   └── analyticsService.ts
│
└── State Management
    └── React Hooks (useState, useEffect, custom hooks)

                    ↓ HTTP REST API

Backend (Spring Boot)
├── Controllers (REST Endpoints)
│   ├── TopicController
│   ├── FlashcardController
│   ├── PomodoroController
│   └── AnalyticsController
│
├── Services (Business Logic)
│   ├── TopicService
│   ├── FlashcardService (SM-2 Algorithm)
│   ├── ConfidenceDecayService
│   ├── MockInterviewService
│   └── AnalyticsService
│
├── Repositories (Data Access)
│   ├── TopicRepository
│   ├── FlashcardRepository
│   ├── PomodoroRepository
│   └── SessionRepository
│
└── Models (JPA Entities)
    ├── Topic
    ├── Flashcard
    ├── PracticeSession
    ├── Pomodoro
    └── MockInterview

                    ↓ JPA/JDBC

Data Layer
├── H2 Database (Relational Data)
│   ├── topic
│   ├── flashcard
│   ├── practice_session
│   ├── pomodoro
│   └── mock_interview
│
└── File System (Binary Data)
    ├── uploads/documents/
    ├── uploads/audio/
    └── uploads/backups/
```

## Design Patterns

### 1. Layered Architecture (MVC)

**Purpose:** Separation of concerns, maintainability

**Layers:**
```
Presentation → Business Logic → Data Access → Database
(Controller)      (Service)      (Repository)   (Entities)
```

**Benefits:**
- Clear responsibility boundaries
- Easy to test each layer independently
- Loose coupling between layers
- Easy to swap implementations

**Example:**
```java
@RestController  // Presentation
public class TopicController {
    @Autowired
    private TopicService service;  // Business Logic

    @GetMapping("/api/topics")
    public List<Topic> getAllTopics() {
        return service.getAllTopics();
    }
}

@Service  // Business Logic
public class TopicService {
    @Autowired
    private TopicRepository repository;  // Data Access

    public List<Topic> getAllTopics() {
        return repository.findAll();
    }
}

public interface TopicRepository extends JpaRepository<Topic, Long> {
    // Data Access (Spring Data auto-implements)
}
```

### 2. Repository Pattern

**Purpose:** Abstract data access logic

**Implementation:** Spring Data JPA repositories

**Benefits:**
- Database-agnostic service layer
- Automatic CRUD implementation
- Easy to mock for testing
- Centralized query logic

**Example:**
```java
public interface FlashcardRepository extends JpaRepository<Flashcard, Long> {
    List<Flashcard> findByTopicId(Long topicId);
    List<Flashcard> findByNextReviewDateBefore(LocalDate date);

    @Query("SELECT f FROM Flashcard f WHERE f.nextReviewDate <= CURRENT_DATE")
    List<Flashcard> findDueCards();
}
```

### 3. Dependency Injection

**Purpose:** Loose coupling, testability

**Implementation:** Spring @Autowired, constructor injection

**Benefits:**
- Easy to swap implementations
- Facilitates unit testing
- Spring manages lifecycle

**Example:**
```java
@Service
public class MockInterviewService {
    private final TopicRepository topicRepository;
    private final MockInterviewRepository interviewRepository;

    @Autowired  // Constructor injection (preferred)
    public MockInterviewService(
            TopicRepository topicRepository,
            MockInterviewRepository interviewRepository) {
        this.topicRepository = topicRepository;
        this.interviewRepository = interviewRepository;
    }
}
```

### 4. DTO (Data Transfer Object) Pattern

**Purpose:** Decouple API contracts from domain models

**Benefits:**
- API stability (internal changes don't affect API)
- Security (hide sensitive fields)
- Flexibility (combine multiple entities)

**Example:**
```java
public class TopicSummaryDTO {
    private Long id;
    private String name;
    private String category;
    private int sessionCount;
    private int flashcardCount;
    // No internal IDs or sensitive data
}
```

### 5. Service Facade Pattern

**Purpose:** Simplify complex subsystem interactions

**Example:** AnalyticsService aggregates data from multiple repositories

```java
@Service
public class AnalyticsService {
    @Autowired private TopicRepository topicRepo;
    @Autowired private SessionRepository sessionRepo;
    @Autowired private FlashcardRepository flashcardRepo;
    @Autowired private PomodoroRepository pomodoroRepo;

    public AnalyticsSummary getCompleteAnalytics() {
        // Aggregates data from all repositories
        return AnalyticsSummary.builder()
            .totalTopics(topicRepo.count())
            .totalSessions(sessionRepo.count())
            .totalStudyTime(calculateTotalStudyTime())
            .streak(calculateStreak())
            .build();
    }
}
```

### 6. Strategy Pattern

**Purpose:** Encapsulate algorithms

**Example:** SM-2 Algorithm in FlashcardService

```java
public interface SpacedRepetitionAlgorithm {
    FlashcardReview calculateNext(Flashcard card, int quality);
}

@Service
public class SM2Algorithm implements SpacedRepetitionAlgorithm {
    @Override
    public FlashcardReview calculateNext(Flashcard card, int quality) {
        // SM-2 algorithm implementation
    }
}
```

### 7. Observer Pattern (Implicit)

**Purpose:** React to entity changes

**Implementation:** JPA lifecycle callbacks

**Example:**
```java
@Entity
public class Topic {
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

### 8. Builder Pattern

**Purpose:** Construct complex objects

**Implementation:** Lombok @Builder

**Benefits:**
- Readable object creation
- Immutability support
- Optional parameters

**Example:**
```java
Topic topic = Topic.builder()
    .name("Binary Search")
    .category("Algorithms")
    .difficulty("EASY")
    .confidence(5)
    .build();
```

## Data Flow

### Example: Creating a Flashcard and Reviewing It

**1. User creates flashcard:**

```
Frontend:
  User fills form → flashcardService.createFlashcard()
    ↓ POST /api/flashcards (JSON)

Backend:
  FlashcardController.createFlashcard()
    ↓ validation
  FlashcardService.createFlashcard()
    ↓ initialize SM-2 values (interval=0, ease=2.5)
  FlashcardRepository.save()
    ↓ JPA/Hibernate
  H2 Database: INSERT INTO flashcard
    ↓ return saved entity
  Response: 201 Created (JSON)
```

**2. User reviews flashcard:**

```
Frontend:
  User rates quality (0-5) → flashcardService.submitReview()
    ↓ POST /api/flashcards/{id}/review (quality: 4)

Backend:
  FlashcardController.submitReview()
    ↓
  FlashcardService.submitReview(id, quality=4)
    ↓ load flashcard from DB
    ↓ apply SM-2 algorithm:
    ↓   - calculate new interval
    ↓   - update ease factor
    ↓   - set next review date
    ↓   - increment success count
  FlashcardRepository.save()
    ↓ JPA/Hibernate
  H2 Database: UPDATE flashcard SET interval=6, next_review_date=...
    ↓ return updated entity
  Response: 200 OK (updated flashcard JSON)
```

### Example: Confidence Decay Scheduled Task

```
Scheduled Task (runs daily at 2 AM):
  @Scheduled(cron = "0 0 2 * * *")
  ConfidenceDecayService.applyConfidenceDecay()
    ↓ load decay rule from database
    ↓ find topics: lastStudied < (now - daysInactive)
    ↓ for each stale topic:
    ↓   - calculate decay: oldConfidence * decayPercentage
    ↓   - newConfidence = max(1, oldConfidence - decay)
    ↓   - update topic.confidence
    ↓   - save ConfidenceHistory record (audit trail)
    ↓ TopicRepository.saveAll()
    ↓ H2 Database: UPDATE topic SET confidence=X WHERE id IN (...)
    ↓           : INSERT INTO confidence_history (...)
```

## Key Design Decisions

### 1. H2 Database (File-based)

**Decision:** Use H2 embedded database with file persistence

**Rationale:**
- ✅ Zero configuration (no separate database server)
- ✅ Portable (single file, easy backup)
- ✅ Fast for single-user applications
- ✅ SQL compatible (easy to migrate to PostgreSQL/MySQL)
- ✅ H2 Console for debugging

**Trade-offs:**
- ❌ Not suitable for multi-user production
- ❌ Limited concurrent access
- ❌ Smaller feature set than PostgreSQL

**Migration Path:**
```java
// To switch to PostgreSQL, just change application.properties:
spring.datasource.url=jdbc:postgresql://localhost:5432/interview_tracker
spring.datasource.driverClassName=org.postgresql.Driver
// No code changes needed (JPA abstraction)
```

### 2. Lombok for Boilerplate Reduction

**Decision:** Use Lombok annotations for getters/setters/builders

**Rationale:**
- ✅ Reduces code by 60-70%
- ✅ Less maintenance (no manual getter/setter updates)
- ✅ Cleaner entity classes
- ✅ Builder pattern for free

**Trade-offs:**
- ❌ Requires IDE plugin
- ❌ Compile-time code generation (learning curve)
- ❌ Can hide complexity

**Example Impact:**
```java
// Without Lombok: ~80 lines
public class Topic {
    private Long id;
    private String name;
    // + 10 more fields

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    // + 20 more getters/setters
    // + equals(), hashCode(), toString()
}

// With Lombok: ~15 lines
@Entity
@Data
@Builder
public class Topic {
    private Long id;
    private String name;
    // + 10 more fields
}
```

### 3. SM-2 Algorithm for Flashcards

**Decision:** Implement SuperMemo SM-2 spaced repetition algorithm

**Rationale:**
- ✅ Proven algorithm (30+ years)
- ✅ Simple to implement
- ✅ Effective for learning retention
- ✅ Adaptable (ease factor adjusts per card)

**Alternatives Considered:**
- SM-5+ (too complex for this use case)
- Leitner system (less adaptive)
- Custom algorithm (reinventing the wheel)

**Implementation:**
- Ease factor stored as integer (2500 = 2.5) for precision
- Quality scale 0-5 matches SM-2 spec
- Minimum ease factor 1.3 prevents too-frequent reviews

### 4. REST API (not GraphQL)

**Decision:** Use REST for API design

**Rationale:**
- ✅ Simpler to implement
- ✅ Better tooling (Swagger, Postman)
- ✅ Easier to cache
- ✅ Standard HTTP methods

**Trade-offs:**
- ❌ Over-fetching (get entire entity when only need few fields)
- ❌ Multiple requests for related data

**Mitigation:**
- Use DTOs to control response shape
- Implement pagination for large lists
- Consider GraphQL for future if frontend complexity grows

### 5. Frontend State Management (React Hooks)

**Decision:** Use React hooks (useState, useEffect) instead of Redux

**Rationale:**
- ✅ Simpler for this application size
- ✅ Less boilerplate
- ✅ Built-in to React
- ✅ Custom hooks for reusability

**When to switch to Redux:**
- Application grows beyond 50+ components
- Complex state sharing across distant components
- Need time-travel debugging
- Multiple developers need clear state patterns

### 6. Monolithic Architecture (not Microservices)

**Decision:** Single Spring Boot application

**Rationale:**
- ✅ Simpler deployment
- ✅ Easier development and debugging
- ✅ No network latency between services
- ✅ Sufficient for single-user application

**Migration to Microservices (if needed):**
```
Potential service boundaries:
- Topic & Session Management Service
- Flashcard & Spaced Repetition Service
- Analytics & Reporting Service
- File Storage Service
```

### 7. File System Storage (not Cloud Storage)

**Decision:** Store uploaded files on local file system

**Rationale:**
- ✅ Simple implementation
- ✅ No external dependencies
- ✅ No API costs
- ✅ Fast access

**Cloud Migration Path:**
```java
// Implement StorageService interface
public interface StorageService {
    String store(MultipartFile file);
    byte[] retrieve(String path);
}

// Implementations:
class LocalFileStorageService implements StorageService { }
class S3StorageService implements StorageService { }
class AzureBlobStorageService implements StorageService { }

// Switch via configuration
@Value("${storage.type}")
private String storageType;  // local, s3, azure
```

## Scalability Considerations

### Current Limitations

**Single User:**
- No authentication/authorization
- No multi-tenancy
- H2 database (single file)
- Local file storage

**Suitable For:**
- Personal use
- Desktop application
- <= 10,000 topics
- <= 100,000 flashcards
- <= 1 GB uploaded files

### Scaling to Multiple Users

**Required Changes:**

1. **Authentication & Authorization:**
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        http.authorizeRequests()
            .antMatchers("/api/public/**").permitAll()
            .antMatchers("/api/**").authenticated()
            .and()
            .oauth2ResourceServer().jwt();
        return http.build();
    }
}
```

2. **Multi-tenancy:**
```java
@Entity
public class Topic {
    @ManyToOne
    private User owner;  // Add owner relationship

    // Or use tenant ID
    private String tenantId;
}
```

3. **Database Migration:**
```properties
# PostgreSQL
spring.datasource.url=jdbc:postgresql://localhost:5432/interview_tracker
spring.datasource.username=postgres
spring.datasource.password=secret
```

4. **Cloud File Storage:**
```java
@Service
public class S3StorageService {
    @Autowired
    private AmazonS3 s3Client;

    public String uploadFile(MultipartFile file) {
        String key = UUID.randomUUID().toString();
        s3Client.putObject(bucketName, key, file.getInputStream(), metadata);
        return key;
    }
}
```

5. **Caching:**
```java
@Service
public class TopicService {
    @Cacheable(value = "topics", key = "#id")
    public Topic getTopicById(Long id) {
        return repository.findById(id).orElseThrow();
    }
}
```

6. **Load Balancing:**
```
     Load Balancer
    /      |      \
  App1   App2   App3
    \      |      /
    Shared Database
```

### Performance Optimization

**Current Optimizations:**

1. **Database Indexes:**
```sql
CREATE INDEX idx_topic_category ON topic(category);
CREATE INDEX idx_flashcard_next_review ON flashcard(next_review_date);
CREATE INDEX idx_session_date ON practice_session(session_date);
```

2. **Lazy Loading:**
```java
@OneToMany(mappedBy = "topic", fetch = FetchType.LAZY)
private List<Flashcard> flashcards;  // Only loaded when accessed
```

3. **Pagination:**
```java
public Page<Topic> getTopics(Pageable pageable) {
    return topicRepository.findAll(pageable);
}
```

4. **DTO Projection:**
```java
@Query("SELECT new com.interviewtracker.dto.TopicSummaryDTO(t.id, t.name, t.category) " +
       "FROM Topic t")
List<TopicSummaryDTO> findAllSummaries();  // Only fetch needed fields
```

**Future Optimizations:**

1. **Redis Caching:**
```java
@Cacheable(value = "analytics", key = "#userId")
public AnalyticsSummary getAnalytics(Long userId) { }
```

2. **Connection Pooling:**
```properties
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
```

3. **Async Processing:**
```java
@Async
public CompletableFuture<AnalyticsSummary> calculateAnalyticsAsync() { }
```

4. **Database Sharding (if millions of users):**
```
User IDs 1-1M    → Database Shard 1
User IDs 1M-2M   → Database Shard 2
...
```

## Security Considerations

### Current Security State

**⚠️ Not Production-Ready - No Authentication**

**Risks:**
- Anyone can access all data
- No user isolation
- No rate limiting
- No input sanitization beyond validation

### Production Security Checklist

**1. Authentication & Authorization:**
```java
// Implement JWT or OAuth2
@Configuration
@EnableWebSecurity
public class SecurityConfig { }
```

**2. Input Validation:**
```java
@NotBlank(message = "Name is required")
@Size(min = 1, max = 255)
private String name;

@Min(1) @Max(10)
private Integer confidence;
```

**3. SQL Injection Prevention:**
- ✅ Using JPA/Hibernate (parameterized queries)
- ✅ Never concatenating SQL strings

**4. XSS Prevention:**
```java
// Sanitize user input
String safe = StringEscapeUtils.escapeHtml4(userInput);
```

**5. CORS Configuration:**
```java
@CrossOrigin(origins = {"https://trusted-domain.com"})  // Specific domains only
```

**6. File Upload Security:**
```java
// Validate file type
String contentType = file.getContentType();
if (!allowedTypes.contains(contentType)) {
    throw new InvalidFileTypeException();
}

// Validate file size
if (file.getSize() > maxFileSize) {
    throw new FileTooLargeException();
}

// Scan for malware (in production)
virusScanner.scan(file);
```

**7. Rate Limiting:**
```java
@RateLimiter(name = "api", fallbackMethod = "fallback")
public List<Topic> getTopics() { }
```

**8. HTTPS Only:**
```properties
server.ssl.enabled=true
server.ssl.key-store=classpath:keystore.p12
```

**9. Secrets Management:**
```properties
# Don't commit secrets to git
spring.datasource.password=${DB_PASSWORD}  # Environment variable

# Or use AWS Secrets Manager, HashiCorp Vault
```

**10. Logging & Monitoring:**
```java
@Slf4j
public class TopicService {
    public Topic createTopic(Topic topic) {
        log.info("Creating topic: userId={}, topic={}", userId, topic.getName());
    }
}
```

---

## Extension Points

### Adding a New Feature (Example: Tags for Topics)

**1. Database:**
```java
@Entity
public class Tag {
    @Id @GeneratedValue
    private Long id;
    private String name;
    private String color;
}

@Entity
public class Topic {
    @ManyToMany
    @JoinTable(name = "topic_tags",
        joinColumns = @JoinColumn(name = "topic_id"),
        inverseJoinColumns = @JoinColumn(name = "tag_id"))
    private Set<Tag> tags = new HashSet<>();
}
```

**2. Repository:**
```java
public interface TagRepository extends JpaRepository<Tag, Long> {
    Optional<Tag> findByName(String name);
}
```

**3. Service:**
```java
@Service
public class TagService {
    public Tag createTag(Tag tag) { }
    public void addTagToTopic(Long topicId, Long tagId) { }
}
```

**4. Controller:**
```java
@RestController
@RequestMapping("/api/tags")
public class TagController {
    @PostMapping
    public ResponseEntity<Tag> createTag(@RequestBody Tag tag) { }

    @PostMapping("/topic/{topicId}")
    public ResponseEntity<Void> addTag(@PathVariable Long topicId, @RequestBody Long tagId) { }
}
```

**5. Frontend:**
```typescript
// types/tag.ts
export interface Tag {
  id: number;
  name: string;
  color: string;
}

// services/tagService.ts
export const tagService = {
  createTag: async (tag: Tag) => { },
  addTagToTopic: async (topicId: number, tagId: number) => { }
};

// components/TagPicker.tsx
export const TagPicker: React.FC<TagPickerProps> = ({ topicId }) => { };
```

---

For API details, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

For development guide, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

For deployment, see [DEPLOYMENT.md](DEPLOYMENT.md)
