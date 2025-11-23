# FitTracker Pro - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Component Architecture](#component-architecture)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Design](#database-design)
7. [API Design](#api-design)
8. [Security Architecture](#security-architecture)
9. [Communication Patterns](#communication-patterns)
10. [Deployment Architecture](#deployment-architecture)

## System Overview

FitTracker Pro is a full-stack fitness tracking application built using modern microservices architecture with a React-based single-page application frontend.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼───────┐         ┌──────▼──────┐
│   Frontend    │         │  API Gateway │
│  (React SPA)  │◄────────┤  (Port 8080) │
└───────────────┘         └──────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
            ┌───────▼──┐  ┌─────▼───┐  ┌────▼────┐
            │  User    │  │Nutrition│  │ Workout │
            │ Service  │  │ Service │  │ Service │
            └────┬─────┘  └────┬────┘  └────┬────┘
                 │             │            │
            ┌────▼─────────────▼────────────▼─────┐
            │       PostgreSQL Databases           │
            └──────────────────────────────────────┘
```

### Key Characteristics

- **Microservices Architecture:** Independent, scalable services
- **Event-Driven:** Asynchronous communication via Kafka
- **API-First Design:** RESTful APIs with OpenAPI documentation
- **Containerized:** Docker support for all components
- **Cloud-Ready:** Deployable on any cloud platform

## Architecture Patterns

### 1. Microservices Pattern

**Why Microservices?**
- **Scalability:** Scale services independently based on demand
- **Maintainability:** Easier to understand and modify smaller codebases
- **Technology Flexibility:** Use different technologies per service
- **Resilience:** Failure in one service doesn't crash the entire system
- **Team Autonomy:** Different teams can work on different services

**Services:**
1. **User Service:** Authentication, authorization, user management
2. **Nutrition Service:** Meal tracking, food database, nutrition calculations
3. **Workout Service:** Exercise tracking, workout programs
4. **Analytics Service:** Reports, statistics, goal tracking
5. **API Gateway:** Single entry point, routing, load balancing
6. **Eureka Server:** Service discovery and registration

### 2. Database Per Service Pattern

Each microservice has its own database to ensure:
- **Data Isolation:** No direct database access between services
- **Independent Scaling:** Scale databases independently
- **Technology Choice:** Different databases for different needs
- **Loose Coupling:** Services communicate via APIs, not shared databases

```
User Service     → fittracker_user_db
Nutrition Service → fittracker_nutrition_db
Workout Service  → fittracker_workout_db
Analytics Service → fittracker_analytics_db
```

### 3. API Gateway Pattern

The API Gateway acts as a reverse proxy to:
- **Route Requests:** Direct requests to appropriate microservices
- **Authentication:** Validate JWT tokens
- **Load Balancing:** Distribute load across service instances
- **Rate Limiting:** Prevent API abuse
- **CORS Handling:** Manage cross-origin requests

### 4. Event-Driven Architecture

Services communicate asynchronously via events:
- **Event Publishing:** Services publish domain events (e.g., MealCreated, WorkoutCompleted)
- **Event Consumption:** Services subscribe to relevant events
- **Decoupling:** Services don't need to know about each other
- **Reliability:** Message queues ensure delivery

**Event Flow Example:**
```
User Creates Meal
      │
      ├─► Nutrition Service saves meal
      │
      ├─► Publishes MealCreatedEvent
      │
      └─► Analytics Service consumes event
          └─► Updates daily statistics
```

## Component Architecture

### Service Registry (Eureka Server)

**Purpose:** Service discovery and health monitoring

**Features:**
- Service registration on startup
- Health checks every 30 seconds
- Load balancing across instances
- Automatic de-registration on failure

**Configuration:**
```yaml
eureka:
  server:
    enable-self-preservation: false
  client:
    register-with-eureka: false
    fetch-registry: false
```

### API Gateway (Spring Cloud Gateway)

**Purpose:** Single entry point for all client requests

**Responsibilities:**
- Request routing
- JWT authentication
- Rate limiting
- CORS handling
- Request/response logging

**Routing Example:**
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://USER-SERVICE
          predicates:
            - Path=/api/auth/**,/api/users/**
          filters:
            - AuthenticationFilter
            - RateLimitingFilter
```

### Config Server (Optional)

**Purpose:** Centralized configuration management

**Benefits:**
- Single source of truth for configurations
- Environment-specific configurations
- Hot reload of configurations
- Encrypted sensitive data

## Backend Architecture

### Layered Architecture

Each microservice follows a layered architecture:

```
┌──────────────────────────────────┐
│      Controller Layer            │  ← REST API endpoints
├──────────────────────────────────┤
│      Service Layer               │  ← Business logic
├──────────────────────────────────┤
│      Repository Layer            │  ← Data access
├──────────────────────────────────┤
│      Entity Layer                │  ← Domain models
└──────────────────────────────────┘
```

### User Service Architecture

```
UserController
    ├── POST /api/auth/register
    ├── POST /api/auth/login
    ├── GET  /api/auth/profile
    └── PUT  /api/auth/profile
         │
         ▼
    UserService
         ├── registerUser()
         ├── loginUser()
         ├── getUserProfile()
         └── updateUserProfile()
              │
              ▼
    UserRepository (JPA)
         │
         ▼
    PostgreSQL (fittracker_user_db)
```

**Key Components:**
- **JWT Authentication:** Token-based authentication
- **BCrypt Password Hashing:** Secure password storage
- **Spring Security:** Authorization and authentication
- **Custom UserDetails:** Integration with Spring Security

### Nutrition Service Architecture

```
NutritionController
    ├── GET  /api/meals/date/{date}
    ├── POST /api/meals
    ├── PUT  /api/meals/{id}
    └── DELETE /api/meals/{id}
         │
         ▼
    MealService
         ├── createMeal()
         ├── getMealsByDate()
         ├── updateMeal()
         └── deleteMeal()
              │
              ▼
    MealRepository
         │
         ▼
    PostgreSQL (fittracker_nutrition_db)
```

**Key Components:**
- **Food Database:** 500+ pre-loaded food items
- **Nutrition Calculator:** Automatic macro calculation
- **Daily Summaries:** Aggregated nutrition data
- **Caching:** Redis for frequently accessed data

### Workout Service Architecture

```
WorkoutController
    ├── GET  /api/workouts/date/{date}
    ├── POST /api/workouts
    ├── PUT  /api/workouts/{id}/complete
    └── DELETE /api/workouts/{id}
         │
         ▼
    WorkoutService
         ├── createWorkout()
         ├── completeWorkout()
         ├── getWorkoutsByDate()
         └── deleteWorkout()
              │
              ▼
    WorkoutRepository
         │
         ▼
    PostgreSQL (fittracker_workout_db)
```

**Key Components:**
- **Exercise Library:** 100+ pre-loaded exercises
- **Workout Templates:** Reusable workout plans
- **Progress Tracking:** Set, rep, and weight history
- **Calorie Estimation:** Automatic calorie burn calculation

### Analytics Service Architecture

```
AnalyticsController
    ├── GET /api/analytics/nutrition/{userId}
    ├── GET /api/analytics/workout/{userId}
    ├── GET /api/goals
    └── POST /api/goals
         │
         ▼
    AnalyticsService
         ├── getNutritionAnalytics()
         ├── getWorkoutAnalytics()
         ├── generateReports()
         └── trackGoals()
              │
              ▼
    AnalyticsRepository
         │
         ▼
    PostgreSQL (fittracker_analytics_db)
```

**Key Components:**
- **Report Generation:** Weekly and monthly reports
- **Goal Tracking:** Progress towards fitness goals
- **Achievement System:** Badges and milestones
- **Data Aggregation:** Statistical analysis

## Frontend Architecture

### Component Hierarchy

```
App
├── Router
│   ├── PublicRoutes
│   │   ├── LoginPage
│   │   └── RegisterPage
│   └── PrivateRoutes (Auth Required)
│       ├── DashboardPage
│       ├── NutritionPage
│       ├── WorkoutsPage
│       ├── AnalyticsPage
│       ├── ProfilePage
│       └── SettingsPage
```

### State Management (Redux Toolkit)

```
Redux Store
├── auth
│   ├── state: { user, token, loading, error }
│   └── actions: { login, register, logout, updateProfile }
├── nutrition
│   ├── state: { meals, dailySummary, loading, error }
│   └── actions: { fetchMeals, createMeal, updateMeal, deleteMeal }
├── workout
│   ├── state: { workouts, loading, error }
│   └── actions: { fetchWorkouts, createWorkout, completeWorkout }
└── analytics
    ├── state: { data, reports, loading, error }
    └── actions: { fetchAnalytics, fetchReports }
```

### Service Layer

**API Services** handle all HTTP communication:

```typescript
// auth.service.ts
class AuthService {
  async login(credentials: LoginRequest): Promise<AuthResponse>
  async register(userData: RegisterRequest): Promise<User>
  async getProfile(): Promise<UserProfile>
  async updateProfile(data: UpdateProfileRequest): Promise<UserProfile>
}

// nutrition.service.ts
class NutritionService {
  async getMealsByDate(date: string): Promise<Meal[]>
  async createMeal(data: CreateMealRequest): Promise<Meal>
  async getDailySummary(date: string): Promise<NutritionSummary>
}
```

### Axios Interceptors

**Request Interceptor:** Adds JWT token to all requests
```typescript
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Response Interceptor:** Handles token refresh and errors
```typescript
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh
      const newToken = await refreshToken();
      // Retry original request
    }
    return Promise.reject(error);
  }
);
```

### Component Architecture

**Container Components** (Smart):
- Connect to Redux store
- Handle business logic
- Manage side effects

**Presentational Components** (Dumb):
- Receive data via props
- Display UI
- Emit events to parents

**Example:**
```
NutritionPage (Container)
    │
    ├─► NutritionSummaryCard (Presentational)
    │       └─► Displays daily nutrition stats
    │
    ├─► MealCard (Presentational)
    │       └─► Displays individual meal
    │
    └─► AddMealDialog (Container)
            └─► Handles meal creation logic
```

## Database Design

### Schema Overview

#### User Database (fittracker_user_db)

```sql
-- Users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User profiles table
CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES users(id),
    height_cm DECIMAL(5,2),
    current_weight_kg DECIMAL(5,2),
    target_weight_kg DECIMAL(5,2),
    activity_level VARCHAR(50),
    fitness_goal VARCHAR(50),
    target_daily_calories INT,
    target_protein_g INT,
    target_carbs_g INT,
    target_fat_g INT
);

-- Weight history table
CREATE TABLE weight_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    weight_kg DECIMAL(5,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
```

#### Nutrition Database (fittracker_nutrition_db)

```sql
-- Food items table
CREATE TABLE food_items (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    serving_size VARCHAR(100),
    serving_unit VARCHAR(50),
    calories INT NOT NULL,
    protein_g DECIMAL(5,2),
    carbs_g DECIMAL(5,2),
    fat_g DECIMAL(5,2),
    fiber_g DECIMAL(5,2),
    sugar_g DECIMAL(5,2),
    is_verified BOOLEAN DEFAULT false,
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meals table
CREATE TABLE meals (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    meal_date DATE NOT NULL,
    meal_time TIME,
    notes TEXT,
    total_calories INT,
    total_protein DECIMAL(5,2),
    total_carbs DECIMAL(5,2),
    total_fat DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meal items table
CREATE TABLE meal_items (
    id BIGSERIAL PRIMARY KEY,
    meal_id BIGINT REFERENCES meals(id) ON DELETE CASCADE,
    food_item_id BIGINT REFERENCES food_items(id),
    servings DECIMAL(5,2) NOT NULL,
    calories INT,
    protein_g DECIMAL(5,2),
    carbs_g DECIMAL(5,2),
    fat_g DECIMAL(5,2)
);
```

#### Workout Database (fittracker_workout_db)

```sql
-- Exercise categories table
CREATE TABLE exercise_categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

-- Exercises table
CREATE TABLE exercises (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id BIGINT REFERENCES exercise_categories(id),
    muscle_group VARCHAR(100),
    difficulty_level VARCHAR(50),
    equipment_needed VARCHAR(255),
    calories_per_minute DECIMAL(5,2),
    is_verified BOOLEAN DEFAULT false
);

-- Workouts table
CREATE TABLE workouts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    workout_name VARCHAR(255),
    workout_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_duration_minutes INT,
    total_calories_burned INT,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workout exercises table
CREATE TABLE workout_exercises (
    id BIGSERIAL PRIMARY KEY,
    workout_id BIGINT REFERENCES workouts(id) ON DELETE CASCADE,
    exercise_id BIGINT REFERENCES exercises(id),
    exercise_order INT,
    planned_sets INT,
    planned_reps INT,
    planned_duration_seconds INT,
    actual_sets INT,
    actual_reps INT,
    actual_duration_seconds INT,
    weight_kg DECIMAL(5,2),
    calories_burned INT
);
```

### Database Relationships

```
users (1) ─────── (1) user_profiles
  │
  ├─ (1) ─────── (N) weight_history
  │
  ├─ (1) ─────── (N) meals
  │                    │
  │                    └─ (1) ─────── (N) meal_items
  │                                       │
  │                                       └─ (N) ─────── (1) food_items
  │
  └─ (1) ─────── (N) workouts
                       │
                       └─ (1) ─────── (N) workout_exercises
                                           │
                                           └─ (N) ─────── (1) exercises
                                                             │
                                                             └─ (N) ─────── (1) exercise_categories
```

### Indexing Strategy

**Performance Optimization:**
```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);

-- Meal queries by user and date
CREATE INDEX idx_meals_user_date ON meals(user_id, meal_date);

-- Workout queries by user and date
CREATE INDEX idx_workouts_user_date ON workouts(user_id, workout_date);

-- Food item searches
CREATE INDEX idx_food_items_name ON food_items(name);
CREATE INDEX idx_food_items_brand ON food_items(brand);

-- Exercise searches
CREATE INDEX idx_exercises_name ON exercises(name);
CREATE INDEX idx_exercises_muscle_group ON exercises(muscle_group);
```

## API Design

### RESTful Principles

All APIs follow REST conventions:

**Resource Naming:**
- Use nouns for resources: `/api/meals`, `/api/workouts`
- Use plural names: `/api/users` not `/api/user`
- Use hierarchical structure: `/api/meals/{id}/items`

**HTTP Methods:**
- **GET:** Retrieve resources (idempotent)
- **POST:** Create resources
- **PUT:** Update resources (replace)
- **PATCH:** Partial update
- **DELETE:** Remove resources

**Status Codes:**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server error

### API Versioning

**URL Versioning:**
```
/api/v1/meals
/api/v2/meals
```

**Header Versioning:**
```
Accept: application/vnd.fittracker.v1+json
```

### Response Format

**Success Response:**
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "id": 1,
    "name": "Breakfast"
  },
  "timestamp": "2024-11-19T10:30:00Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "timestamp": "2024-11-19T10:30:00Z",
  "errors": [
    {
      "field": "email",
      "message": "Email is required"
    }
  ]
}
```

### Pagination

**Request:**
```
GET /api/meals?page=0&size=20&sort=mealDate,desc
```

**Response:**
```json
{
  "content": [...],
  "page": 0,
  "size": 20,
  "totalElements": 100,
  "totalPages": 5,
  "isFirst": true,
  "isLast": false,
  "hasNext": true,
  "hasPrevious": false
}
```

## Security Architecture

### Authentication Flow

```
1. User submits credentials
        │
        ▼
2. Server validates credentials
        │
        ▼
3. Server generates JWT token
        │
        ▼
4. Client stores token (localStorage)
        │
        ▼
5. Client includes token in all requests
        │
        ▼
6. Server validates token on each request
```

### JWT Structure

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
  "iat": 1700000000,
  "exp": 1700086400
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)
```

### Security Best Practices

1. **Password Security:**
   - BCrypt hashing with salt
   - Minimum 8 characters
   - Requires uppercase, lowercase, number, special char

2. **JWT Token Security:**
   - Short expiration time (24 hours)
   - Stored in localStorage (or httpOnly cookie)
   - Validated on every request
   - Refresh token mechanism

3. **API Security:**
   - Rate limiting (100 requests/minute)
   - CORS configuration
   - Input validation
   - SQL injection prevention (JPA)
   - XSS protection

4. **Data Security:**
   - Encrypted database connections
   - Sensitive data encryption
   - HTTPS in production
   - Audit logging

## Communication Patterns

### Synchronous Communication (REST)

**Used for:**
- Client ↔ API Gateway
- API Gateway ↔ Microservices
- Direct user requests

**Example:**
```
Frontend ──(HTTP)──> API Gateway ──(HTTP)──> User Service
                                      │
                                      └──(DB Query)──> PostgreSQL
```

### Asynchronous Communication (Event-Driven)

**Used for:**
- Cross-service updates
- Analytics aggregation
- Notification triggers

**Example:**
```
Nutrition Service
    │
    ├─ User logs meal
    │
    └─ Publishes MealCreatedEvent to Kafka
            │
            └─> Analytics Service consumes
                    │
                    └─> Updates daily statistics
```

### Event Types

1. **UserRegisteredEvent**
   - Published by: User Service
   - Consumed by: Analytics Service
   - Triggers: Welcome email, initial setup

2. **MealCreatedEvent**
   - Published by: Nutrition Service
   - Consumed by: Analytics Service
   - Triggers: Daily summary update

3. **WorkoutCompletedEvent**
   - Published by: Workout Service
   - Consumed by: Analytics Service
   - Triggers: Progress tracking, achievements

4. **UserWeightUpdatedEvent**
   - Published by: User Service
   - Consumed by: Analytics Service
   - Triggers: Weight history chart update

## Deployment Architecture

### Development Environment

```
Developer Machine
    │
    ├─ PostgreSQL (localhost:5432)
    ├─ Eureka Server (localhost:8761)
    ├─ User Service (localhost:8081)
    ├─ Nutrition Service (localhost:8082)
    ├─ Workout Service (localhost:8083)
    ├─ Analytics Service (localhost:8084)
    ├─ API Gateway (localhost:8080)
    └─ Frontend (localhost:5173)
```

### Docker Deployment

```
Docker Network (fittracker-network)
    │
    ├─ postgres (Container)
    ├─ backend (Container - All services)
    └─ frontend (Container - Nginx)
```

### Production Deployment (Kubernetes)

```
Load Balancer
    │
    ├─> Frontend Pods (3 replicas)
    │       └─> Nginx serving React build
    │
    └─> API Gateway Pods (3 replicas)
            │
            ├─> User Service Pods (2 replicas)
            ├─> Nutrition Service Pods (3 replicas)
            ├─> Workout Service Pods (2 replicas)
            └─> Analytics Service Pods (2 replicas)
```

### Scalability Strategy

**Horizontal Scaling:**
- Add more instances of services
- Load balance across instances
- Stateless service design

**Vertical Scaling:**
- Increase resources (CPU, RAM)
- Optimize queries and caching
- Database connection pooling

**Caching Strategy:**
- Redis for frequently accessed data
- Food items database caching
- Exercise library caching
- User session caching

---

**Last Updated:** November 2024
**Version:** 1.0.0
