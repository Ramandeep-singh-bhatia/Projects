# FitTracker Pro - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architectural Principles](#architectural-principles)
3. [Microservices Architecture](#microservices-architecture)
4. [Service Details](#service-details)
5. [Communication Patterns](#communication-patterns)
6. [Data Architecture](#data-architecture)
7. [Event-Driven Design](#event-driven-design)
8. [Security Architecture](#security-architecture)
9. [Caching Strategy](#caching-strategy)
10. [Monitoring and Observability](#monitoring-and-observability)
11. [Scalability and Performance](#scalability-and-performance)
12. [Deployment Architecture](#deployment-architecture)

---

## System Overview

FitTracker Pro is built using a **microservices architecture** with the following characteristics:

- **8 independent services**: Each owning its own domain and data
- **Event-driven communication**: Asynchronous messaging via Apache Kafka
- **Service discovery**: Dynamic service registration with Eureka
- **API Gateway pattern**: Single entry point for all client requests
- **Distributed caching**: Redis for performance optimization
- **Comprehensive observability**: Metrics, logs, and distributed tracing

### High-Level Architecture Diagram

```
                                    ┌─────────────────┐
                                    │   Client Apps   │
                                    │ (Web/Mobile/API)│
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  API Gateway    │
                                    │   (Port 8080)   │
                                    │  JWT Validation │
                                    │  Load Balancing │
                                    └────────┬────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          │                  │                  │
                 ┌────────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
                 │  User Service   │ │  Nutrition  │ │  Workout        │
                 │  (Port 8081)    │ │  Service    │ │  Service        │
                 │                 │ │  (8082)     │ │  (8083)         │
                 │ - Auth/JWT      │ │ - Meals     │ │ - Exercises     │
                 │ - Profiles      │ │ - Food DB   │ │ - Workouts      │
                 └────────┬────────┘ └──────┬──────┘ └────────┬────────┘
                          │                  │                  │
                          │         ┌────────▼──────────────────▼─────┐
                          │         │    Apache Kafka (Port 9092)     │
                          │         │  - meal-events                  │
                          │         │  - workout-events               │
                          │         │  - user-events                  │
                          │         └────────┬────────────────────────┘
                          │                  │
                          │         ┌────────▼────────┐
                          │         │   Analytics     │
                          │         │   Service       │
                          │         │   (Port 8084)   │
                          │         │ - Daily Summary │
                          │         │ - Reports       │
                          │         └─────────────────┘
                          │
                 ┌────────▼────────────────────────────────────┐
                 │         Infrastructure Layer                │
                 │                                              │
                 │  ┌──────────┐  ┌────────┐  ┌─────────────┐ │
                 │  │PostgreSQL│  │ Redis  │  │   Eureka    │ │
                 │  │(4 DBs)   │  │ Cache  │  │  Discovery  │ │
                 │  │Port 5432 │  │ 6379   │  │  (8761)     │ │
                 │  └──────────┘  └────────┘  └─────────────┘ │
                 │                                              │
                 │  ┌──────────┐  ┌─────────┐  ┌───────────┐  │
                 │  │Prometheus│  │ Grafana │  │  Jaeger   │  │
                 │  │  (9090)  │  │ (3000)  │  │  (16686)  │  │
                 │  └──────────┘  └─────────┘  └───────────┘  │
                 └──────────────────────────────────────────────┘
```

---

## Architectural Principles

### 1. Domain-Driven Design (DDD)

Each microservice represents a **bounded context**:

- **User Service**: Identity and Access Management (IAM) domain
- **Nutrition Service**: Nutrition tracking and food database domain
- **Workout Service**: Exercise and workout planning domain
- **Analytics Service**: Data aggregation and reporting domain

### 2. Single Responsibility Principle

Each service has a **single, well-defined responsibility**:

- Services own their data (database per service pattern)
- No direct database access across services
- Communication through APIs and events only

### 3. Loose Coupling

Services are **loosely coupled** through:

- **Synchronous**: REST APIs for request/response
- **Asynchronous**: Kafka events for state changes
- **Service Discovery**: No hardcoded service URLs

### 4. High Cohesion

Related functionality is **grouped together**:

- All nutrition-related features in Nutrition Service
- All workout-related features in Workout Service
- Shared code in Common module (DTOs, utilities)

### 5. API Gateway Pattern

**Single entry point** for all client requests:

- Centralized authentication/authorization
- Request routing to appropriate services
- Load balancing across service instances
- Protocol translation (if needed)

### 6. Event-Driven Architecture

**Eventual consistency** through events:

- Services publish domain events (MealCreated, WorkoutCompleted)
- Interested services subscribe and react
- Decoupled, resilient communication
- Enables real-time analytics updates

### 7. Database per Service

Each service has its **own database**:

- **fittracker_users**: User Service data
- **fittracker_nutrition**: Nutrition Service data
- **fittracker_workouts**: Workout Service data
- **fittracker_analytics**: Analytics Service data

**Benefits:**
- Independent scaling
- Technology flexibility
- Failure isolation
- Team autonomy

---

## Microservices Architecture

### Service Inventory

| Service | Purpose | Port | Database | Tech Stack |
|---------|---------|------|----------|------------|
| Eureka Server | Service Discovery & Registration | 8761 | None | Spring Cloud Eureka |
| Config Server | Centralized Configuration | 8888 | None | Spring Cloud Config |
| API Gateway | Entry point, routing, auth | 8080 | None | Spring Cloud Gateway |
| User Service | Authentication, user profiles | 8081 | PostgreSQL | Spring Boot, JPA, JWT |
| Nutrition Service | Food DB, meal tracking | 8082 | PostgreSQL | Spring Boot, JPA, Kafka |
| Workout Service | Exercise library, workouts | 8083 | PostgreSQL | Spring Boot, JPA, Kafka |
| Analytics Service | Data aggregation, reports | 8084 | PostgreSQL | Spring Boot, JPA, Kafka |
| Common | Shared DTOs and utilities | N/A | None | Java Library |

### Service Dependencies

```
API Gateway
    ↓ depends on
Eureka Server (for service discovery)

User Service
    ↓ depends on
Eureka Server, PostgreSQL, Redis

Nutrition Service
    ↓ depends on
Eureka Server, PostgreSQL, Redis, Kafka

Workout Service
    ↓ depends on
Eureka Server, PostgreSQL, Redis, Kafka

Analytics Service
    ↓ depends on
Eureka Server, PostgreSQL, Redis, Kafka (consumer)
```

---

## Service Details

### 1. Eureka Server (Service Discovery)

**Responsibility:** Service registration and discovery

**How it works:**
1. Each microservice registers itself on startup
2. Sends heartbeats every 30 seconds
3. API Gateway queries Eureka to find service instances
4. Load balances requests across available instances

**Configuration:**
```yaml
eureka:
  instance:
    hostname: localhost
  client:
    register-with-eureka: false
    fetch-registry: false
```

**Key Features:**
- Self-preservation mode (protects against network partitions)
- Dashboard at http://localhost:8761
- Health monitoring of registered services

### 2. Config Server (Configuration Management)

**Responsibility:** Centralized configuration for all services

**How it works:**
1. Services fetch configuration on startup
2. Can refresh configuration without restart
3. Supports multiple profiles (dev, prod)

**Configuration Sources:**
- Local file system
- Git repository (production)
- Environment variables

**Key Features:**
- Profile-based configuration
- Encryption support for sensitive data
- Configuration refresh endpoints

### 3. API Gateway

**Responsibility:** Single entry point for all client requests

**How it works:**
1. Client sends request to http://localhost:8080
2. Gateway validates JWT token
3. Queries Eureka for service location
4. Routes request to appropriate service
5. Returns response to client

**Routing Configuration:**
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://USER-SERVICE
          predicates:
            - Path=/api/users/**
        - id: nutrition-service
          uri: lb://NUTRITION-SERVICE
          predicates:
            - Path=/api/nutrition/**
```

**Key Features:**
- JWT token validation
- Load balancing (lb://)
- Request/response filtering
- Rate limiting (can be added)
- CORS configuration

**Security Filter Chain:**
```java
@Bean
public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
    return http
        .csrf().disable()
        .authorizeExchange()
            .pathMatchers("/api/users/register", "/api/users/login").permitAll()
            .anyExchange().authenticated()
        .and()
        .oauth2ResourceServer()
            .jwt()
        .and().build();
}
```

### 4. User Service

**Responsibility:** User authentication, authorization, and profile management

**Domain Model:**
```
User
├── id: Long
├── email: String (unique)
├── passwordHash: String (bcrypt)
├── firstName: String
├── lastName: String
├── dateOfBirth: LocalDate
├── gender: Gender (MALE, FEMALE, OTHER)
├── heightCm: Double
├── weightKg: Double
└── profile: UserProfile

UserProfile
├── id: Long
├── userId: Long
├── activityLevel: ActivityLevel
├── fitnessGoal: FitnessGoal
├── targetWeightKg: Double
├── targetCaloriesPerDay: Integer
├── targetProteinGrams: Integer
├── targetCarbsGrams: Integer
└── targetFatGrams: Integer
```

**Key Features:**
- User registration with email validation
- JWT token generation and validation
- Password hashing with BCrypt
- User profile management
- Profile-based goal setting

**Authentication Flow:**
```
1. User POST /api/users/login with {email, password}
2. UserService validates credentials
3. If valid, generate JWT token
4. Return token + user info
5. Client stores token
6. Client includes token in Authorization header for future requests
```

**JWT Token Structure:**
```json
{
  "sub": "user@example.com",
  "userId": 1,
  "iat": 1640000000,
  "exp": 1640086400
}
```

**Endpoints:**
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Authenticate user
- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update user profile
- `PUT /api/users/password` - Change password

### 5. Nutrition Service

**Responsibility:** Food database, meal logging, nutrition tracking

**Domain Model:**
```
FoodCategory
├── id: Long
├── name: String
└── description: String

FoodItem
├── id: Long
├── name: String
├── brand: String
├── categoryId: Long
├── servingSize: Double
├── servingUnit: String
├── caloriesPerServing: Integer
├── proteinGrams: Double
├── carbsGrams: Double
├── fatGrams: Double
├── fiberGrams: Double
├── sugarGrams: Double
├── sodiumMg: Integer
├── isVerified: Boolean
└── barcode: String

Meal
├── id: Long
├── userId: Long
├── mealType: MealType (BREAKFAST, LUNCH, DINNER, SNACK)
├── mealDate: LocalDate
├── mealTime: LocalTime
├── notes: String
└── items: List<MealItem>

MealItem
├── id: Long
├── mealId: Long
├── foodItemId: Long
├── servings: BigDecimal
├── calories: BigDecimal
├── proteinGrams: BigDecimal
├── carbsGrams: BigDecimal
└── fatGrams: BigDecimal
```

**Key Features:**
- Comprehensive food database
- Barcode lookup
- Meal creation with automatic nutrition calculation
- Meal history tracking
- Daily/weekly nutrition summaries
- Event publishing for analytics

**Nutrition Calculation:**
```java
// When creating a meal, nutrition is calculated automatically
BigDecimal servings = mealItemRequest.getServings();
MealItem item = MealItem.builder()
    .calories(foodItem.getCaloriesPerServing().multiply(servings))
    .proteinGrams(foodItem.getProteinGrams().multiply(servings))
    .carbsGrams(foodItem.getCarbsGrams().multiply(servings))
    .fatGrams(foodItem.getFatGrams().multiply(servings))
    .build();
```

**Event Publishing:**
```java
// After meal is saved
MealCreatedEvent event = MealCreatedEvent.builder()
    .userId(meal.getUserId())
    .mealId(meal.getId())
    .mealDate(meal.getMealDate())
    .totalCalories(meal.getTotalCalories())
    .totalProtein(meal.getTotalProtein())
    .totalCarbs(meal.getTotalCarbs())
    .totalFat(meal.getTotalFat())
    .build();

kafkaTemplate.send("meal-events", event);
```

**Endpoints:**
- `GET /api/nutrition/food-items` - Browse food database
- `GET /api/nutrition/food-items/search` - Search foods
- `GET /api/nutrition/food-items/{id}` - Get food details
- `POST /api/nutrition/meals` - Create meal
- `GET /api/nutrition/meals/date/{date}` - Get meals by date
- `GET /api/nutrition/meals/summary` - Get nutrition summary
- `DELETE /api/nutrition/meals/{id}` - Delete meal

### 6. Workout Service

**Responsibility:** Exercise library, workout planning, progress tracking

**Domain Model:**
```
ExerciseCategory
├── id: Long
├── name: String
└── description: String

Exercise
├── id: Long
├── name: String
├── description: String
├── categoryId: Long
├── muscleGroup: MuscleGroup
├── difficultyLevel: DifficultyLevel
├── equipmentNeeded: String
├── isVerified: Boolean
├── instructions: String (TEXT)
└── caloriesPerMinute: Double

Workout
├── id: Long
├── userId: Long
├── workoutName: String
├── workoutDate: LocalDate
├── startTime: LocalTime
├── endTime: LocalTime
├── totalDurationMinutes: Integer
├── totalCaloriesBurned: Integer
├── status: WorkoutStatus (IN_PROGRESS, COMPLETED, CANCELLED)
├── notes: String
└── exercises: List<WorkoutExercise>

WorkoutExercise
├── id: Long
├── workoutId: Long
├── exerciseId: Long
├── exerciseOrder: Integer
├── plannedSets: Integer
├── plannedReps: Integer
├── plannedDurationSeconds: Integer
├── actualSets: Integer
├── actualReps: Integer
├── actualDurationSeconds: Integer
├── weightKg: Double
└── caloriesBurned: Integer
```

**Key Features:**
- Searchable exercise database
- Workout session management (start/complete)
- Calorie burn estimation
- Progress tracking
- Event publishing for analytics

**Calorie Calculation:**
```java
// Estimate calories burned based on exercise and duration
public Integer calculateCaloriesBurned(Exercise exercise, Integer durationMinutes) {
    return (int) Math.round(exercise.getCaloriesPerMinute() * durationMinutes);
}

// For strength training (sets x reps)
public Integer calculateCaloriesBurned(Exercise exercise, Integer sets, Integer reps) {
    // Estimate: 12 calories per minute for strength training
    // Each set takes ~1 minute
    return sets * 12;
}
```

**Workout Completion Flow:**
```
1. Create workout (IN_PROGRESS)
2. Add exercises with planned sets/reps
3. User performs workout
4. Complete workout with actual data
5. Calculate total duration and calories
6. Publish WorkoutCompletedEvent
7. Analytics Service updates daily summary
```

**Endpoints:**
- `GET /api/workouts/exercises` - Browse exercises
- `GET /api/workouts/exercises/search` - Search exercises
- `GET /api/workouts/exercises/muscle-group/{group}` - Filter by muscle
- `POST /api/workouts` - Create workout
- `POST /api/workouts/{id}/complete` - Complete workout
- `GET /api/workouts/history` - Get workout history
- `DELETE /api/workouts/{id}` - Delete workout

### 7. Analytics Service

**Responsibility:** Data aggregation, analytics, and reporting

**Domain Model:**
```
DailySummary
├── id: Long
├── userId: Long
├── date: LocalDate
├── totalCaloriesConsumed: Integer
├── totalCaloriesBurned: Integer
├── netCalories: Integer
├── totalProteinGrams: Integer
├── totalCarbsGrams: Integer
├── totalFatGrams: Integer
├── totalFiberGrams: Integer
├── workoutDurationMinutes: Integer
├── workoutCount: Integer
└── mealCount: Integer

WeeklySummary
├── id: Long
├── userId: Long
├── weekStartDate: LocalDate
├── averageCaloriesPerDay: Integer
├── totalWorkoutMinutes: Integer
├── averageWorkoutDuration: Integer
└── weeklyProgress: Double
```

**Key Features:**
- Real-time analytics updates via Kafka
- Daily/weekly/monthly summaries
- Goal progress tracking
- Trend analysis
- Historical data aggregation

**Event Consumption:**
```java
@KafkaListener(topics = "meal-events", groupId = "analytics-service")
public void handleMealCreatedEvent(MealCreatedEvent event) {
    // Find or create daily summary for user and date
    DailySummary summary = dailySummaryRepository
        .findByUserIdAndDate(event.getUserId(), event.getMealDate())
        .orElse(new DailySummary(event.getUserId(), event.getMealDate()));

    // Update nutrition totals
    summary.addMealNutrition(event);

    // Save updated summary
    dailySummaryRepository.save(summary);
}

@KafkaListener(topics = "workout-events", groupId = "analytics-service")
public void handleWorkoutCompletedEvent(WorkoutCompletedEvent event) {
    // Find or create daily summary
    DailySummary summary = ...;

    // Update workout totals
    summary.addWorkoutData(event);

    // Save
    dailySummaryRepository.save(summary);
}
```

**Endpoints:**
- `GET /api/analytics/daily/{date}` - Get daily summary
- `GET /api/analytics/weekly?startDate={date}` - Get weekly summary
- `GET /api/analytics/range?start={date}&end={date}` - Get date range
- `GET /api/analytics/goals/progress` - Get goal progress
- `GET /api/analytics/trends` - Get trend data

### 8. Common Module

**Responsibility:** Shared code across all services

**Contents:**
- **DTOs**: ApiResponse, ErrorResponse
- **Enums**: Gender, ActivityLevel, FitnessGoal, MealType, etc.
- **Utilities**: DateUtils, ValidationUtils
- **Constants**: KafkaTopics, CacheNames

**ApiResponse Wrapper:**
```java
@Data
@Builder
public class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;
    private LocalDateTime timestamp;

    public static <T> ApiResponse<T> success(String message, T data) {
        return ApiResponse.<T>builder()
            .success(true)
            .message(message)
            .data(data)
            .timestamp(LocalDateTime.now())
            .build();
    }

    public static <T> ApiResponse<T> error(String message) {
        return ApiResponse.<T>builder()
            .success(false)
            .message(message)
            .data(null)
            .timestamp(LocalDateTime.now())
            .build();
    }
}
```

---

## Communication Patterns

### 1. Synchronous Communication (REST APIs)

**When to use:**
- Request/response operations
- User-initiated actions requiring immediate response
- Data queries

**Example: Get User Profile**
```
Client → API Gateway → User Service → Database → Response
```

**Benefits:**
- Immediate response
- Simple to implement
- Easy to debug

**Drawbacks:**
- Tight coupling
- Synchronous blocking
- Cascading failures

### 2. Asynchronous Communication (Kafka Events)

**When to use:**
- State change notifications
- Background processing
- Data synchronization across services
- Analytics updates

**Example: Meal Created**
```
Nutrition Service → Publish MealCreatedEvent → Kafka → Analytics Service → Update Daily Summary
```

**Benefits:**
- Loose coupling
- Resilient (message persistence)
- Scalable (multiple consumers)
- Non-blocking

**Drawbacks:**
- Eventual consistency
- More complex debugging
- Message ordering challenges

### 3. Service Discovery (Eureka)

**How it works:**
1. Service starts up
2. Registers with Eureka Server
3. Sends heartbeats every 30 seconds
4. API Gateway queries Eureka for service locations
5. Routes requests to available instances

**Benefits:**
- Dynamic service locations
- Automatic load balancing
- Fault tolerance
- Scalability

---

## Data Architecture

### Database per Service Pattern

Each service has its own PostgreSQL database:

```
PostgreSQL Instance (Port 5432)
├── fittracker_users (User Service)
│   ├── users
│   └── user_profiles
├── fittracker_nutrition (Nutrition Service)
│   ├── food_categories
│   ├── food_items
│   ├── meals
│   └── meal_items
├── fittracker_workouts (Workout Service)
│   ├── exercise_categories
│   ├── exercises
│   ├── workouts
│   └── workout_exercises
└── fittracker_analytics (Analytics Service)
    ├── daily_summaries
    ├── weekly_summaries
    └── goal_progress
```

### Database Migrations (Flyway)

**Versioned Migrations:**

Each service has migration scripts in `src/main/resources/db/migration/`:

```
db/migration/
├── V1__create_users_table.sql
├── V2__create_profiles_table.sql
├── V3__add_profile_constraints.sql
└── V4__create_indexes.sql
```

**Naming Convention:**
- `V{version}__{description}.sql`
- Migrations run automatically on application startup
- Flyway tracks applied migrations in `flyway_schema_history` table

**Example Migration:**
```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20) NOT NULL,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Data Consistency

**Eventual Consistency through Events:**

1. **Meal Created:**
   ```
   Nutrition DB: Insert meal → Commit → Publish event → Analytics DB: Update summary
   ```

2. **Workout Completed:**
   ```
   Workout DB: Update workout → Commit → Publish event → Analytics DB: Update summary
   ```

**Handling Failures:**
- Kafka persists messages (configurable retention)
- Consumer can retry on failure
- Dead letter queue for failed messages
- Idempotent event handlers (handle duplicates)

---

## Event-Driven Design

### Kafka Topics

| Topic | Producer | Consumer | Event Type |
|-------|----------|----------|------------|
| meal-events | Nutrition Service | Analytics Service | MealCreatedEvent, MealUpdatedEvent, MealDeletedEvent |
| workout-events | Workout Service | Analytics Service | WorkoutCompletedEvent, WorkoutDeletedEvent |
| user-events | User Service | Analytics Service | UserRegisteredEvent, ProfileUpdatedEvent |

### Event Structure

**MealCreatedEvent:**
```json
{
  "eventId": "uuid",
  "eventType": "MEAL_CREATED",
  "timestamp": "2024-01-15T08:30:00Z",
  "userId": 1,
  "mealId": 123,
  "mealDate": "2024-01-15",
  "mealType": "BREAKFAST",
  "totalCalories": 450,
  "totalProtein": 25.5,
  "totalCarbs": 55.0,
  "totalFat": 12.0
}
```

**WorkoutCompletedEvent:**
```json
{
  "eventId": "uuid",
  "eventType": "WORKOUT_COMPLETED",
  "timestamp": "2024-01-15T19:30:00Z",
  "userId": 1,
  "workoutId": 456,
  "workoutDate": "2024-01-15",
  "durationMinutes": 75,
  "caloriesBurned": 450,
  "exerciseCount": 6
}
```

### Event Publishing

```java
@Service
@RequiredArgsConstructor
public class EventPublisher {
    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publishMealCreatedEvent(MealCreatedEvent event) {
        // Use userId as partition key for ordering
        kafkaTemplate.send(
            KafkaTopics.MEAL_EVENTS,
            event.getUserId().toString(),
            event
        );
        log.info("Published MealCreatedEvent: {}", event);
    }
}
```

### Event Consumption

```java
@Service
@Slf4j
public class AnalyticsEventConsumer {

    @KafkaListener(
        topics = KafkaTopics.MEAL_EVENTS,
        groupId = "analytics-service"
    )
    public void handleMealEvent(MealCreatedEvent event) {
        log.info("Received MealCreatedEvent: {}", event);

        // Update daily summary
        dailySummaryService.updateFromMealEvent(event);
    }
}
```

### Event Ordering

**Partition by User ID:**
- All events for a user go to same partition
- Events for same user are processed in order
- Different users can be processed in parallel

**Configuration:**
```yaml
spring:
  kafka:
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
    consumer:
      group-id: analytics-service
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: "*"
```

---

## Security Architecture

### Authentication Flow

```
1. User submits credentials to /api/users/login
2. API Gateway forwards to User Service
3. User Service validates credentials
4. If valid, generates JWT token
5. Returns token to client
6. Client includes token in subsequent requests
7. API Gateway validates token before routing
```

### JWT Token Structure

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "user@example.com",
  "userId": 1,
  "roles": ["USER"],
  "iat": 1640000000,
  "exp": 1640086400
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

### Token Validation (API Gateway)

```java
@Bean
public SecurityWebFilterChain securityWebFilterChain(ServerHttpSecurity http) {
    return http
        .csrf().disable()
        .authorizeExchange()
            .pathMatchers("/api/users/register", "/api/users/login").permitAll()
            .anyExchange().authenticated()
        .and()
        .oauth2ResourceServer()
            .jwt()
        .and()
        .build();
}
```

### Security Best Practices

✅ **Passwords:** BCrypt hashing with salt
✅ **Tokens:** Short expiration (24 hours default)
✅ **HTTPS:** Required in production
✅ **CORS:** Configured for allowed origins
✅ **SQL Injection:** Prevented by JPA/Hibernate
✅ **XSS:** Input validation and sanitization
✅ **Secrets:** Environment variables, not hardcoded
✅ **Database:** Credentials in .env files

---

## Caching Strategy

### Redis Caching

**What is cached:**
- Frequently accessed food items
- Verified exercises
- User profiles
- Daily summaries

**Cache Configuration:**
```java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory factory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofHours(1))
            .serializeValuesWith(SerializationPair.fromSerializer(
                new GenericJackson2JsonRedisSerializer()
            ));

        return RedisCacheManager.builder(factory)
            .cacheDefaults(config)
            .build();
    }
}
```

### Cache Warming

**On Application Startup:**
```java
@Service
@RequiredArgsConstructor
public class CacheWarmingService {

    @EventListener(ApplicationReadyEvent.class)
    public void warmUpCaches() {
        log.info("Starting cache warming...");

        // Warm food items cache
        List<FoodItem> verified = foodItemRepository
            .findTop100ByIsVerifiedTrueOrderByNameAsc();
        verified.forEach(item ->
            cacheManager.getCache("foodItems").put(item.getId(), item)
        );

        log.info("Cache warming completed");
    }
}
```

### Cache Eviction

**Manual Eviction:**
```java
@PostMapping("/cache/clear")
public ResponseEntity<?> clearCache() {
    cacheManager.getCacheNames().forEach(name ->
        cacheManager.getCache(name).clear()
    );
    return ResponseEntity.ok("Cache cleared");
}
```

**Automatic Eviction:**
- TTL-based (default: 1 hour)
- LRU policy when memory is full
- Event-driven eviction (on data update)

---

## Monitoring and Observability

### Three Pillars of Observability

1. **Metrics** (Prometheus)
2. **Logs** (Application logs)
3. **Traces** (Jaeger)

### Prometheus Metrics

**Metrics Exposed:**
```
# HTTP requests
http_server_requests_seconds_count{service="user-service", method="GET", status="200"}
http_server_requests_seconds_sum{service="user-service", method="GET", status="200"}

# JVM metrics
jvm_memory_used_bytes{area="heap"}
jvm_threads_live_threads

# Database connections
hikaricp_connections_active{pool="HikariPool-1"}
hikaricp_connections_idle{pool="HikariPool-1"}

# Cache metrics
cache_gets_total{cache="foodItems", result="hit"}
cache_gets_total{cache="foodItems", result="miss"}
```

**Querying Metrics:**
```promql
# Request rate
rate(http_server_requests_seconds_count[5m])

# Error rate
rate(http_server_requests_seconds_count{status=~"5.."}[5m])

# 95th percentile latency
histogram_quantile(0.95, http_server_requests_seconds_bucket)
```

### Grafana Dashboards

**Pre-configured dashboards for:**
- JVM metrics (heap, GC, threads)
- HTTP request rates and latencies
- Database connection pool stats
- Cache hit/miss rates
- Kafka consumer lag

### Jaeger Distributed Tracing

**Trace a request across services:**

```
GET /api/analytics/daily/2024-01-15
    ├─ API Gateway (2ms)
    │   └─ JWT Validation (1ms)
    ├─ Eureka Lookup (5ms)
    ├─ Analytics Service (45ms)
    │   ├─ Check Redis Cache (2ms) [MISS]
    │   ├─ Database Query (35ms)
    │   │   └─ SELECT daily_summary WHERE user_id=1 AND date='2024-01-15'
    │   └─ Update Cache (3ms)
    └─ Total: 52ms
```

**Benefits:**
- Identify bottlenecks
- Debug cross-service issues
- Optimize slow operations
- Understand dependencies

---

## Scalability and Performance

### Horizontal Scaling

**Scale services independently:**

```bash
# Scale nutrition service to 3 instances
docker-compose up -d --scale nutrition-service=3

# Eureka shows 3 instances
# API Gateway load balances across all 3
```

**Stateless Services:**
- No session state stored locally
- All state in database or cache
- Any instance can handle any request

### Load Balancing

**Client-side load balancing (Ribbon):**
```java
@FeignClient(name = "nutrition-service")
public interface NutritionClient {
    @GetMapping("/api/nutrition/food-items/{id}")
    FoodItem getFoodItem(@PathVariable Long id);
}

// Ribbon automatically load balances across instances
```

**Strategies:**
- Round Robin (default)
- Weighted Response Time
- Availability Filtering

### Performance Optimizations

**Database:**
- Connection pooling (HikariCP)
- Indexes on frequently queried columns
- Pagination for large result sets
- Query optimization (N+1 prevention)

**Caching:**
- Redis for frequently accessed data
- Cache warming on startup
- TTL-based eviction
- Cache-aside pattern

**JVM Tuning:**
```bash
JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

**Connection Pools:**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 20000
```

---

## Deployment Architecture

### Development Environment

```
Docker Compose (docker-compose.yml)
├── PostgreSQL, Redis, Kafka (infrastructure)
└── Locally running microservices (mvn spring-boot:run)
```

**Benefits:**
- Fast iteration
- Easy debugging
- Hot reload

### Production Environment

```
Docker Compose (docker-compose.prod.yml)
├── All infrastructure services
└── All microservices in containers
```

**Or Kubernetes:**
```
Kubernetes Cluster
├── Namespace: fittracker-infrastructure
│   ├── PostgreSQL StatefulSet
│   ├── Redis Deployment
│   └── Kafka Cluster
└── Namespace: fittracker-services
    ├── Eureka Deployment (2 replicas)
    ├── API Gateway Deployment (3 replicas)
    ├── User Service Deployment (3 replicas)
    ├── Nutrition Service Deployment (3 replicas)
    ├── Workout Service Deployment (3 replicas)
    └── Analytics Service Deployment (2 replicas)
```

### Health Checks

**Liveness Probe:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8081/actuator/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8081
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

## Summary

FitTracker Pro demonstrates **modern microservices architecture** with:

✅ **Domain-Driven Design**: Clear bounded contexts
✅ **Event-Driven Architecture**: Asynchronous, decoupled communication
✅ **Service Discovery**: Dynamic service registration
✅ **API Gateway**: Single entry point with security
✅ **Database per Service**: Independent data ownership
✅ **Distributed Caching**: Redis for performance
✅ **Comprehensive Observability**: Metrics, logs, traces
✅ **Security**: JWT authentication, BCrypt passwords
✅ **Scalability**: Horizontal scaling, load balancing
✅ **Resilience**: Health checks, retries, circuit breakers (can be added)

This architecture enables:
- **Independent deployment** of services
- **Technology flexibility** per service
- **Team autonomy** (Conway's Law)
- **Fault isolation** (failure doesn't cascade)
- **Scalability** (scale bottlenecks independently)

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).
For API details, see [API_REFERENCE.md](API_REFERENCE.md).
For operations, see [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md).
